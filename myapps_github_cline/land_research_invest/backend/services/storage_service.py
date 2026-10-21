"""
Storage Service - SQLite perzistencia vysledkov
================================================
Bez novych zavislosti -- len sqlite3 (stdlib) + json.
save_run / patch_parcel / load_last_run / load_run / list_runs / get_run_meta

B1 — História cien a čas na trhu:
  first_seen       TEXT  — ISO dátum prvého výskytu URL
  price_history    TEXT  — JSON [{\"date\": ISO, \"price_eur\": float}, ...]
  listing_age_days INT   — vypočítaný z first_seen pri načítaní

B2–B4 — Signály, index, peer, dražobné polia (H2 fix: perzistencia):
  signals_json     TEXT  — JSON zoznam všetkých signálov
  investment_index INT   — 0–100 (B4)
  invest_summary   TEXT  — textové zdôvodnenie (B4)
  peer_median_ppsm REAL  — mediánová €/m² v obci (B3)
  peer_count       INT   — počet peerov (B3)
  peer_ratio       REAL  — ratio pozemku vs. mediánu (B3)
  vyvolavacia_eur  REAL  — vyvolávacia cena dražby (B2)
  znalecka_eur     REAL  — znalecká/odhad hodnota (B2)
  drazba_kolo      INT   — 1=prvé, 2+=opakovaná (B2)
"""
import sqlite3, json, threading
from datetime import datetime, timezone
from pathlib import Path

SERVICE_NAME = "storage_service"
_DB_PATH = Path(__file__).parent.parent.parent / "data" / "parcels.db"
_lock    = threading.Lock()

# Nové stĺpce pridané po B1 (migrácia ich pridá do existujúcej DB)
_NEW_COLUMNS = [
    ("first_seen",        "ALTER TABLE parcels ADD COLUMN first_seen TEXT"),
    ("price_history",     "ALTER TABLE parcels ADD COLUMN price_history TEXT DEFAULT '[]'"),
    ("signals_json",      "ALTER TABLE parcels ADD COLUMN signals_json TEXT DEFAULT '[]'"),
    ("investment_index",  "ALTER TABLE parcels ADD COLUMN investment_index INTEGER DEFAULT 0"),
    ("invest_summary",    "ALTER TABLE parcels ADD COLUMN invest_summary TEXT DEFAULT ''"),
    ("peer_median_ppsm",  "ALTER TABLE parcels ADD COLUMN peer_median_ppsm REAL DEFAULT 0"),
    ("peer_count",        "ALTER TABLE parcels ADD COLUMN peer_count INTEGER DEFAULT 0"),
    ("peer_ratio",        "ALTER TABLE parcels ADD COLUMN peer_ratio REAL DEFAULT 0"),
    ("vyvolavacia_eur",   "ALTER TABLE parcels ADD COLUMN vyvolavacia_eur REAL DEFAULT 0"),
    ("znalecka_eur",      "ALTER TABLE parcels ADD COLUMN znalecka_eur REAL DEFAULT 0"),
    ("drazba_kolo",       "ALTER TABLE parcels ADD COLUMN drazba_kolo INTEGER DEFAULT 0"),
]


def _get_conn() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    _create_schema(conn)
    _migrate_schema(conn)
    return conn


def _create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS runs (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at   TEXT NOT NULL,
            finished_at  TEXT,
            parcel_count INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS parcels (
            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id                INTEGER NOT NULL REFERENCES runs(id),
            url                   TEXT,
            source_portal         TEXT,
            title                 TEXT,
            price_eur             REAL DEFAULT 0,
            area_sqm              REAL DEFAULT 0,
            location_text         TEXT,
            parcel_number         TEXT,
            lat                   REAL DEFAULT 0,
            lon                   REAL DEFAULT 0,
            price_per_sqm         REAL DEFAULT 0,
            preliminary_score     REAL DEFAULT 0,
            prelim_recommendation TEXT,
            final_score           REAL DEFAULT 0,
            recommendation        TEXT,
            results_json          TEXT DEFAULT '{}',
            created_at            TEXT NOT NULL,
            first_seen            TEXT,
            price_history         TEXT DEFAULT '[]',
            signals_json          TEXT DEFAULT '[]',
            investment_index      INTEGER DEFAULT 0,
            invest_summary        TEXT DEFAULT '',
            peer_median_ppsm      REAL DEFAULT 0,
            peer_count            INTEGER DEFAULT 0,
            peer_ratio            REAL DEFAULT 0,
            vyvolavacia_eur       REAL DEFAULT 0,
            znalecka_eur          REAL DEFAULT 0,
            drazba_kolo           INTEGER DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS idx_parcels_run ON parcels(run_id);
        CREATE INDEX IF NOT EXISTS idx_parcels_url ON parcels(url);
        CREATE INDEX IF NOT EXISTS idx_parcels_url_id ON parcels(url, id);
    """)


def _migrate_schema(conn: sqlite3.Connection) -> None:
    """Pridá nové stĺpce do existujúcej DB (idempotentné — ignoruje 'already exists').
    Používa centrálny zoznam _NEW_COLUMNS definovaný na úrovni modulu."""
    existing = {
        row[1]
        for row in conn.execute("PRAGMA table_info(parcels)").fetchall()
    }
    for col, sql in _NEW_COLUMNS:
        if col not in existing:
            try:
                conn.execute(sql)
                conn.commit()
            except Exception:
                pass  # stĺpec uz existuje alebo ina nekriticka chyba
    # Pridaj nové indexy ak neexistujú
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_parcels_url_id ON parcels(url, id)"
    )
    conn.commit()

def _find_prev_parcel(conn: sqlite3.Connection, url: str) -> dict | None:
    """Nájde posledný zaznamenaný výskyt URL (akýkoľvek predošlý beh).
    Vráti dict s first_seen, price_history, price_eur — alebo None."""
    row = conn.execute(
        "SELECT first_seen, price_history, price_eur FROM parcels "
        "WHERE url=? ORDER BY id DESC LIMIT 1",
        (url,)
    ).fetchone()
    if row is None:
        return None
    return {
        "first_seen":    row["first_seen"],
        "price_history": row["price_history"] or "[]",
        "price_eur":     row["price_eur"] or 0.0,
    }


def save_run(parcels: list) -> int:
    """Ulozi novy beh + vsetky parcely. Vracia run_id.

    B1: Pre každú parcelu:
      - Ak URL už existuje v DB → zachová first_seen + aktualizuje price_history
      - Ak nová URL → first_seen = teraz, začne novú price_history
    """
    now = datetime.now(timezone.utc).isoformat()
    with _lock:
        conn = _get_conn()
        try:
            cur = conn.execute(
                "INSERT INTO runs (started_at, finished_at, parcel_count) VALUES (?,?,?)",
                (now, now, len(parcels))
            )
            run_id = cur.lastrowid
            for p in parcels:
                url       = p.get("url", "")
                price_eur = float(p.get("price_eur", 0) or 0)

                # --- História cien (B1) ---
                prev = _find_prev_parcel(conn, url) if url else None
                if prev:
                    first_seen = prev["first_seen"] or now
                    history    = json.loads(prev["price_history"] or "[]")
                    # pridaj nový záznam len ak sa cena zmenila alebo je história prázdna
                    if not history or abs(history[-1]["price_eur"] - price_eur) > 0.01:
                        history.append({"date": now, "price_eur": price_eur})
                else:
                    first_seen = now
                    history    = [{"date": now, "price_eur": price_eur}]

                conn.execute("""
                    INSERT INTO parcels
                    (run_id, url, source_portal, title, price_eur, area_sqm,
                     location_text, parcel_number, lat, lon, price_per_sqm,
                     preliminary_score, prelim_recommendation,
                     final_score, recommendation, results_json, created_at,
                     first_seen, price_history,
                     signals_json, investment_index, invest_summary,
                     peer_median_ppsm, peer_count, peer_ratio,
                     vyvolavacia_eur, znalecka_eur, drazba_kolo)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    run_id,
                    url,
                    p.get("source_portal", ""),
                    p.get("title", ""),
                    price_eur,
                    float(p.get("area_sqm",   0) or 0),
                    p.get("location_text", ""),
                    p.get("parcel_number", ""),
                    float(p.get("lat", 0) or 0),
                    float(p.get("lon", 0) or 0),
                    float(p.get("price_per_sqm", 0) or 0),
                    float(p.get("preliminary_score", 0) or 0),
                    p.get("prelim_recommendation", ""),
                    float(p.get("final_score", 0) or 0),
                    p.get("recommendation", ""),
                    json.dumps(p.get("results", {}), ensure_ascii=False),
                    now,
                    first_seen,
                    json.dumps(history, ensure_ascii=False),
                    # B2–B4 perzistencia
                    json.dumps(p.get("signals", []),  ensure_ascii=False),
                    int(p.get("investment_index",  0) or 0),
                    p.get("investment_summary", "") or "",
                    float(p.get("peer_median_ppsm", 0) or 0),
                    int(p.get("peer_count",          0) or 0),
                    float(p.get("peer_ratio",        0) or 0),
                    float(p.get("vyvolavacia_cena_eur", 0) or 0),
                    float(p.get("znalecka_hodnota_eur", 0) or 0),
                    int(p.get("drazba_kolo",            0) or 0),
                ))
            conn.commit()
            return run_id
        finally:
            conn.close()


def patch_parcel(url: str, updated: dict) -> bool:
    """Aktualizuje parcelu po GIS scorovani."""
    with _lock:
        conn = _get_conn()
        try:
            conn.execute("""
                UPDATE parcels SET
                    final_score=?, recommendation=?, results_json=?,
                    lat=?, lon=?, price_per_sqm=?
                WHERE url=?
                  AND run_id=(SELECT MAX(run_id) FROM parcels WHERE url=?)
            """, (
                float(updated.get("final_score", 0) or 0),
                updated.get("recommendation", ""),
                json.dumps(updated.get("results", {}), ensure_ascii=False),
                float(updated.get("lat", 0) or 0),
                float(updated.get("lon", 0) or 0),
                float(updated.get("price_per_sqm", 0) or 0),
                url, url,
            ))
            conn.commit()
            return conn.execute("SELECT changes()").fetchone()[0] > 0
        finally:
            conn.close()


def load_last_run() -> list:
    """Vrati parcely z posledneho behu (prazdny list ak ziadny)."""
    with _lock:
        conn = _get_conn()
        try:
            row = conn.execute("SELECT id FROM runs ORDER BY id DESC LIMIT 1").fetchone()
            if row is None:
                return []
            return _load_run_rows(conn, row["id"])
        finally:
            conn.close()


def load_run(run_id: int) -> list:
    with _lock:
        conn = _get_conn()
        try:
            return _load_run_rows(conn, run_id)
        finally:
            conn.close()


def list_runs(limit: int = 10) -> list:
    with _lock:
        conn = _get_conn()
        try:
            rows = conn.execute(
                "SELECT id, started_at, finished_at, parcel_count "
                "FROM runs ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()


def get_run_meta(run_id: int):
    with _lock:
        conn = _get_conn()
        try:
            row = conn.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()


def _load_run_rows(conn: sqlite3.Connection, run_id: int) -> list:
    rows = conn.execute(
        "SELECT * FROM parcels WHERE run_id=? ORDER BY preliminary_score DESC",
        (run_id,)
    ).fetchall()
    now = datetime.now(timezone.utc)
    result = []
    for r in rows:
        d = dict(r)
        try:
            d["results"] = json.loads(d.pop("results_json") or "{}")
        except Exception:
            d["results"] = {}
        # Deserializácia price_history
        try:
            d["price_history"] = json.loads(d.get("price_history") or "[]")
        except Exception:
            d["price_history"] = []
        # Deserializácia signals_json (B2–B4 perzistencia)
        try:
            d["signals"] = json.loads(d.pop("signals_json") or "[]")
        except Exception:
            d.pop("signals_json", None)
            d["signals"] = []
        # Premenuj stĺpce DB → parcel kľúče (B2–B4)
        d["investment_summary"]   = d.pop("invest_summary",    "")
        d["vyvolavacia_cena_eur"] = d.pop("vyvolavacia_eur",   0.0)
        d["znalecka_hodnota_eur"] = d.pop("znalecka_eur",      0.0)
        # Vypočítaj listing_age_days z first_seen
        first_seen_str = d.get("first_seen")
        if first_seen_str:
            try:
                fs = datetime.fromisoformat(first_seen_str)
                if fs.tzinfo is None:
                    from datetime import timezone as _tz
                    fs = fs.replace(tzinfo=_tz.utc)
                d["listing_age_days"] = max(0, (now - fs).days)
            except Exception:
                d["listing_age_days"] = 0
        else:
            d["listing_age_days"] = 0
        # Vypočítaj price_drop_pct z price_history
        history = d["price_history"]
        if len(history) >= 2:
            p_first = history[0]["price_eur"]
            p_last  = history[-1]["price_eur"]
            if p_first > 0:
                d["price_drop_pct"] = round((p_first - p_last) / p_first * 100, 1)
            else:
                d["price_drop_pct"] = 0.0
        else:
            d["price_drop_pct"] = 0.0
        d.pop("id",         None)
        d.pop("run_id",     None)
        d.pop("created_at", None)
        result.append(d)
    return result
