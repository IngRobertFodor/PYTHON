"""
test_backup_service.py — testy pre backup_service (P2)
======================================================
Round-trip: export → import, merge logika, rotácia, validácia.
"""
import sys, pathlib, tempfile, gzip, json, sqlite3
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "backend"))

import pytest
from unittest.mock import patch
from services.backup_service import (
    export_db, import_db,
    backup_status, list_history,
    _rotate_history, _merge_price_history, _earliest,
    _validate_gz_sql, _parse_json_list,
)


def _make_temp_db(tmp_path, n_runs=1, n_parcels=2):
    db = pathlib.Path(tmp_path) / "parcels.db"
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT NOT NULL,
            parcel_count INTEGER DEFAULT 0,
            sources_json TEXT DEFAULT '{}'
        );
        CREATE TABLE IF NOT EXISTS parcels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER, url TEXT,
            price_eur REAL DEFAULT 0, area_sqm REAL DEFAULT 0,
            location_text TEXT DEFAULT '', source_portal TEXT DEFAULT '',
            first_seen TEXT, price_history TEXT DEFAULT '[]'
        );
    """)
    for i in range(n_runs):
        conn.execute("INSERT INTO runs (started_at, parcel_count) VALUES (?, ?)",
                     (f"2026-10-{10+i:02d}T10:00:00", n_parcels))
    for i in range(n_parcels):
        conn.execute(
            "INSERT INTO parcels (run_id,url,price_eur,area_sqm,first_seen,price_history) "
            "VALUES (?,?,?,?,?,?)",
            (1, f"https://test.sk/{i}", 50000.0+i*1000, 800.0+i*50,
             "2026-09-01", json.dumps([{"date":"2026-09-01","price_eur":50000}])),
        )
    conn.commit(); conn.close()
    return db


class TestExportImportRoundtrip:

    def test_export_creates_gz(self, tmp_path):
        db = _make_temp_db(tmp_path / "db")
        dst = tmp_path / "backups" / "latest.sql.gz"
        with patch("services.backup_service._DB_PATH", db):
            result = export_db(dst)
        assert result.exists() and result.stat().st_size > 0

    def test_exported_is_valid_gzip(self, tmp_path):
        db = _make_temp_db(tmp_path / "db")
        dst = tmp_path / "bak.sql.gz"
        with patch("services.backup_service._DB_PATH", db):
            export_db(dst)
        with gzip.open(str(dst), "rt", encoding="utf-8") as fh:
            sql = fh.read()
        assert "CREATE TABLE" in sql and "parcels" in sql

    def test_round_trip_new_parcels(self, tmp_path):
        src_db = _make_temp_db(tmp_path / "src", n_runs=1, n_parcels=3)
        dst_db = tmp_path / "dst" / "parcels.db"
        dst_db.parent.mkdir()
        conn = sqlite3.connect(str(dst_db))
        conn.executescript("""
            CREATE TABLE runs (id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT, parcel_count INTEGER DEFAULT 0,
                sources_json TEXT DEFAULT '{}');
            CREATE TABLE parcels (id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER, url TEXT, price_eur REAL DEFAULT 0,
                area_sqm REAL DEFAULT 0, location_text TEXT DEFAULT '',
                source_portal TEXT DEFAULT '', first_seen TEXT,
                price_history TEXT DEFAULT '[]');
        """); conn.close()
        gz_path = tmp_path / "bak.sql.gz"
        with patch("services.backup_service._DB_PATH", src_db):
            export_db(gz_path)
        gz_bytes = gz_path.read_bytes()
        with patch("services.backup_service._DB_PATH", dst_db):
            stats = import_db(gz_bytes)
        assert stats["new_parcels"] == 3
        assert stats["added_runs"] == 1
        assert stats["merged_parcels"] == 0

    def test_no_duplicates_on_second_import(self, tmp_path):
        db = _make_temp_db(tmp_path / "db", n_parcels=2)
        gz = tmp_path / "bak.sql.gz"
        with patch("services.backup_service._DB_PATH", db):
            export_db(gz)
        gz_bytes = gz.read_bytes()
        with patch("services.backup_service._DB_PATH", db):
            import_db(gz_bytes)
            s2 = import_db(gz_bytes)
        assert s2["new_parcels"] == 0 and s2["added_runs"] == 0


class TestMergeLogic:

    def test_merge_history_combines_unique(self):
        local = [{"date": "2026-09-01", "price_eur": 50000}]
        src   = [{"date": "2026-10-01", "price_eur": 48000}]
        m = _merge_price_history(local, src)
        assert len(m) == 2 and m[0]["date"] < m[1]["date"]

    def test_merge_history_no_dup(self):
        e = {"date": "2026-09-01", "price_eur": 50000}
        assert len(_merge_price_history([e], [e])) == 1

    def test_earliest_prefers_older(self):
        assert _earliest("2026-01-01", "2026-06-01") == "2026-01-01"

    def test_earliest_none_a(self):
        assert _earliest(None, "2026-06-01") == "2026-06-01"

    def test_earliest_both_none(self):
        assert _earliest(None, None) is None


class TestValidation:

    def test_valid_passes(self, tmp_path):
        db = _make_temp_db(tmp_path / "db")
        gz = tmp_path / "t.sql.gz"
        with patch("services.backup_service._DB_PATH", db):
            export_db(gz)
        _validate_gz_sql(gz.read_bytes())  # nesmie vyhodiť

    def test_rejects_non_gzip(self):
        with pytest.raises(ValueError, match="gzip"):
            _validate_gz_sql(b"not a gzip file")

    def test_rejects_gzip_non_sql(self):
        gz = gzip.compress(b"this is not sql content")
        with pytest.raises(ValueError, match="SQL dump"):
            _validate_gz_sql(gz)

    def test_rejects_too_large(self):
        data = b"\x1f\x8b" + b"x" * (51 * 1024 * 1024)
        with pytest.raises(ValueError, match="príliš veľký"):
            _validate_gz_sql(data)


class TestRotation:

    def test_rotate_keeps_newest(self, tmp_path):
        hist = tmp_path / "history"; hist.mkdir()
        import time
        for i in range(25):
            (hist / f"parcels_202{i:02d}01_000000.sql.gz").write_bytes(b"")
            time.sleep(0.01)
        with patch("services.backup_service._HISTORY_DIR", hist):
            _rotate_history(keep=20)
        assert len(list(hist.glob("*.sql.gz"))) == 20

    def test_rotate_noop_when_few(self, tmp_path):
        hist = tmp_path / "history"; hist.mkdir()
        for i in range(5):
            (hist / f"parcels_{i}.sql.gz").write_bytes(b"")
        with patch("services.backup_service._HISTORY_DIR", hist):
            _rotate_history(keep=20)
        assert len(list(hist.glob("*.sql.gz"))) == 5


class TestBackupStatus:

    def test_status_no_db(self, tmp_path):
        with patch("services.backup_service._DB_PATH", tmp_path / "nope.db"), \
             patch("services.backup_service._LATEST_FILE", tmp_path / "nope.sql.gz"), \
             patch("services.backup_service._HISTORY_DIR", tmp_path / "h"):
            s = backup_status()
        assert s["latest_backup"] is None and s["db_runs"] == 0

    def test_status_with_db(self, tmp_path):
        db = _make_temp_db(tmp_path / "db", n_runs=2, n_parcels=3)
        with patch("services.backup_service._DB_PATH", db), \
             patch("services.backup_service._LATEST_FILE", tmp_path / "nope.sql.gz"), \
             patch("services.backup_service._HISTORY_DIR", tmp_path / "h"):
            s = backup_status()
        assert s["db_runs"] == 2 and s["db_parcels"] == 3

    def test_status_with_latest(self, tmp_path):
        db  = _make_temp_db(tmp_path / "db")
        dst = tmp_path / "backups" / "latest.sql.gz"
        with patch("services.backup_service._DB_PATH", db):
            export_db(dst)
        with patch("services.backup_service._DB_PATH", db), \
             patch("services.backup_service._LATEST_FILE", dst), \
             patch("services.backup_service._HISTORY_DIR", tmp_path / "h"):
            s = backup_status()
        assert s["latest_backup"] is not None and s["latest_size_kb"] > 0


class TestParseJsonList:

    def test_valid_string(self):
        assert _parse_json_list('[{"date":"2026-01-01","price_eur":50000}]') == \
               [{"date": "2026-01-01", "price_eur": 50000}]

    def test_list_passthrough(self):
        lst = [{"a": 1}]
        assert _parse_json_list(lst) is lst

    def test_empty_string(self):
        assert _parse_json_list("") == []

    def test_none(self):
        assert _parse_json_list(None) == []

    def test_invalid_json(self):
        assert _parse_json_list("not json {}{{") == []

