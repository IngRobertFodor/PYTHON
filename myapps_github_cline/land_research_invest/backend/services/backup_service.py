"""
Backup Service — zálohovanie a obnova SQLite DB
================================================
Exportuje celú DB ako gzip-nutý SQL dump (sqlite3.iterdump).
Importuje backup späť do DB s merge logikou (bez mazania lokálnych dát).

Variant Y:
  data/backups/parcels_latest.sql.gz   — vždy posledná záloha (prepíše sa)
  data/backups/history/parcels_<ts>.sql.gz — rotovaný archív (max keep=20)

Bezpečnosť:
  - WAL checkpoint pred exportom
  - Validácia formátu pri importe (gzip magic + SQL header)
  - Limit 50 MB na upload
  - Merge: zachová lokálne dáta, pridá chýbajúce z backupu
"""

import gzip
import json
import logging
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_DB_PATH      = Path(__file__).parent.parent.parent / "data" / "parcels.db"
_BACKUP_DIR   = _DB_PATH.parent / "backups"
_HISTORY_DIR  = _BACKUP_DIR / "history"
_LATEST_FILE  = _BACKUP_DIR / "parcels_latest.sql.gz"
_MAX_HISTORY  = 20
_MAX_IMPORT_BYTES = 50 * 1024 * 1024  # 50 MB

_backup_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Import / merge
# ---------------------------------------------------------------------------

def import_db(gz_bytes: bytes) -> dict:
    """
    Importuje backup (bytes gzip SQL) do existujúcej DB — merge režim.
    Vráti: {"added_runs": N, "merged_parcels": M, "new_parcels": K}
    """
    _validate_gz_sql(gz_bytes)
    sql_text = gzip.decompress(gz_bytes).decode("utf-8")

    mem_conn = sqlite3.connect(":memory:")
    mem_conn.row_factory = sqlite3.Row
    try:
        mem_conn.executescript(sql_text)
    except Exception as exc:
        mem_conn.close()
        raise ValueError(f"Neplatný SQL dump: {exc}") from exc

    with _backup_lock:
        _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        local_conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
        local_conn.row_factory = sqlite3.Row
        try:
            stats = _merge(mem_conn, local_conn)
        finally:
            local_conn.close()
    mem_conn.close()
    logger.info("[backup] import OK: %s", stats)
    return stats


def _merge(src: sqlite3.Connection, dst: sqlite3.Connection) -> dict:
    added_runs = merged_parcels = new_parcels = 0

    # runs
    try:
        src_runs = src.execute("SELECT * FROM runs").fetchall()
    except Exception:
        src_runs = []
    for run in src_runs:
        ex = dst.execute("SELECT id FROM runs WHERE started_at=?", (run["started_at"],)).fetchone()
        if not ex:
            cols = run.keys()
            vals = tuple(run[c] for c in cols)
            ph   = ",".join("?" * len(cols))
            dst.execute(f"INSERT OR IGNORE INTO runs ({','.join(cols)}) VALUES ({ph})", vals)
            added_runs += 1
    dst.commit()

    # parcels
    try:
        src_parcels = src.execute("SELECT * FROM parcels").fetchall()
    except Exception:
        src_parcels = []
    for sp in src_parcels:
        url = sp["url"]
        lp  = dst.execute("SELECT * FROM parcels WHERE url=?", (url,)).fetchone()
        if lp is None:
            cols = sp.keys()
            vals = tuple(sp[c] for c in cols)
            ph   = ",".join("?" * len(cols))
            try:
                dst.execute(f"INSERT OR IGNORE INTO parcels ({','.join(cols)}) VALUES ({ph})", vals)
                new_parcels += 1
            except Exception as exc:
                logger.warning("[backup] INSERT parcela %s: %s", url, exc)
        else:
            _merge_parcel(dst, lp, sp)
            merged_parcels += 1
    dst.commit()
    return {"added_runs": added_runs, "merged_parcels": merged_parcels,
            "new_parcels": new_parcels}


def export_db(dst: Optional[Path] = None) -> Path:
    """Exportuje DB do gzip SQL dumpu. Vráti cestu k súboru."""
    dst = dst or _LATEST_FILE
    dst.parent.mkdir(parents=True, exist_ok=True)

    with _backup_lock:
        conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
        try:
            conn.execute("PRAGMA wal_checkpoint(FULL)")
            sql_lines = list(conn.iterdump())
        finally:
            conn.close()

    sql_text = "\n".join(sql_lines)
    tmp = Path(str(dst) + ".tmp")
    with gzip.open(str(tmp), "wt", encoding="utf-8", compresslevel=6) as fh:
        fh.write(sql_text)
    tmp.replace(dst)
    logger.info("[backup] export → %s (%.1f kB)", dst.name, dst.stat().st_size / 1024)
    return dst


def auto_backup() -> None:
    """Automatická záloha po scrape: prepíše latest + pridá do history (rotácia)."""
    if not _DB_PATH.exists():
        return
    try:
        path = export_db(_LATEST_FILE)
        _copy_to_history(path)
        _rotate_history(_MAX_HISTORY)
    except Exception as exc:
        logger.warning("[backup] auto_backup zlyhala: %s", exc)


def _copy_to_history(src: Path) -> Path:
    _HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    ts  = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dst = _HISTORY_DIR / f"parcels_{ts}.sql.gz"
    dst.write_bytes(src.read_bytes())
    return dst


def _rotate_history(keep: int = _MAX_HISTORY) -> None:
    if not _HISTORY_DIR.exists():
        return
    files = sorted(_HISTORY_DIR.glob("parcels_*.sql.gz"), key=lambda p: p.stat().st_mtime)
    for old in files[:-keep]:
        try:
            old.unlink()
        except Exception:
            pass


def _merge_parcel(dst, lp, sp) -> None:
    """Zlúči price_history + zachová najstarší first_seen pre existujúcu parcelu."""
    sp_keys = list(sp.keys())
    lp_keys = list(lp.keys())
    src_hist = _parse_json_list(sp["price_history"] if "price_history" in sp_keys else "[]")
    loc_hist = _parse_json_list(lp["price_history"] if "price_history" in lp_keys else "[]")
    new_hist = _merge_price_history(loc_hist, src_hist)
    src_fs   = sp["first_seen"] if "first_seen" in sp_keys else None
    loc_fs   = lp["first_seen"] if "first_seen" in lp_keys else None
    best_fs  = _earliest(loc_fs, src_fs)
    dst.execute(
        "UPDATE parcels SET price_history=?, first_seen=? WHERE url=?",
        (json.dumps(new_hist, ensure_ascii=False), best_fs, sp["url"]),
    )


def _parse_json_list(raw) -> list:
    if not raw:
        return []
    if isinstance(raw, list):
        return raw
    try:
        return json.loads(raw) or []
    except Exception:
        return []


def _merge_price_history(local: list, src: list) -> list:
    seen = {(e.get("date"), e.get("price_eur")): e for e in local}
    for e in src:
        k = (e.get("date"), e.get("price_eur"))
        if k not in seen:
            seen[k] = e
    return sorted(seen.values(), key=lambda x: x.get("date", ""))


def _earliest(a, b):
    if a and b:
        return a if a <= b else b
    return a or b


def _validate_gz_sql(gz_bytes: bytes) -> None:
    if len(gz_bytes) > _MAX_IMPORT_BYTES:
        raise ValueError(f"Súbor je príliš veľký ({len(gz_bytes)//1024} kB). Limit je 50 MB.")
    if len(gz_bytes) < 2 or gz_bytes[:2] != b"\x1f\x8b":
        raise ValueError("Neplatný formát — očakáva sa gzip súbor (.sql.gz).")
    try:
        start = gzip.decompress(gz_bytes[:512]).decode("utf-8", errors="ignore")
    except Exception as exc:
        raise ValueError(f"Súbor nie je platný gzip: {exc}") from exc
    if "BEGIN TRANSACTION" not in start and "CREATE TABLE" not in start:
        raise ValueError("Obsah súboru nie je platný SQL dump.")


# ---------------------------------------------------------------------------
# Stav / info
# ---------------------------------------------------------------------------

def backup_status() -> dict:
    result: dict = {
        "latest_backup": None, "latest_size_kb": 0,
        "history_count": 0,   "db_size_kb": 0,
        "db_runs": 0,          "db_parcels": 0,
    }
    if _LATEST_FILE.exists():
        stat = _LATEST_FILE.stat()
        result["latest_backup"]  = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
        result["latest_size_kb"] = round(stat.st_size / 1024, 1)
    if _HISTORY_DIR.exists():
        result["history_count"] = len(list(_HISTORY_DIR.glob("parcels_*.sql.gz")))
    if _DB_PATH.exists():
        result["db_size_kb"] = round(_DB_PATH.stat().st_size / 1024, 1)
        try:
            conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
            result["db_runs"]    = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
            result["db_parcels"] = conn.execute("SELECT COUNT(*) FROM parcels").fetchone()[0]
            conn.close()
        except Exception:
            pass
    return result


def list_history() -> list:
    if not _HISTORY_DIR.exists():
        return []
    files = sorted(
        _HISTORY_DIR.glob("parcels_*.sql.gz"),
        key=lambda p: p.stat().st_mtime, reverse=True,
    )
    return [
        {
            "name":     f.name,
            "size_kb":  round(f.stat().st_size / 1024, 1),
            "modified": datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).isoformat(),
        }
        for f in files
    ]

