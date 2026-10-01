"""
Storage Service - SQLite perzistencia vysledkov
================================================
Bez novych zavislosti -- len sqlite3 (stdlib) + json.
save_run / patch_parcel / load_last_run / load_run / list_runs / get_run_meta
"""
import sqlite3, json, threading
from datetime import datetime, timezone
from pathlib import Path

SERVICE_NAME = "storage_service"
_DB_PATH = Path(__file__).parent.parent.parent / "data" / "parcels.db"
_lock    = threading.Lock()


def _get_conn() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    _create_schema(conn)
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
            created_at            TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_parcels_run ON parcels(run_id);
        CREATE INDEX IF NOT EXISTS idx_parcels_url ON parcels(url);
    """)

def save_run(parcels: list) -> int:
    """Ulozi novy beh + vsetky parcely. Vracia run_id."""
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
                conn.execute("""
                    INSERT INTO parcels
                    (run_id, url, source_portal, title, price_eur, area_sqm,
                     location_text, parcel_number, lat, lon, price_per_sqm,
                     preliminary_score, prelim_recommendation,
                     final_score, recommendation, results_json, created_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    run_id,
                    p.get("url", ""),
                    p.get("source_portal", ""),
                    p.get("title", ""),
                    float(p.get("price_eur",  0) or 0),
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
    result = []
    for r in rows:
        d = dict(r)
        try:
            d["results"] = json.loads(d.pop("results_json") or "{}")
        except Exception:
            d["results"] = {}
        d.pop("id",         None)
        d.pop("run_id",     None)
        d.pop("created_at", None)
        result.append(d)
    return result
