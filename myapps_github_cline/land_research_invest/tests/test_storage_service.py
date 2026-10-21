import sys, pathlib, tempfile, json, time
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "backend"))
import pytest
from unittest.mock import patch

TMP_DB = pathlib.Path(tempfile.mkdtemp()) / "test_parcels.db"

@pytest.fixture(autouse=True)
def patch_db_path():
    import services.storage_service as ss
    orig = ss._DB_PATH
    ss._DB_PATH = TMP_DB
    yield
    ss._DB_PATH = orig
    if TMP_DB.exists(): TMP_DB.unlink()
    ss._lock.__class__  # reset by reimport not needed

from services.storage_service import (
    save_run, patch_parcel, load_last_run, load_run, list_runs, get_run_meta,
)

SAMPLE = [
    {"url": "http://a.sk/1", "source_portal": "nehnutelnosti_sk",
     "title": "Pozemok A", "price_eur": 5000, "area_sqm": 500,
     "location_text": "Senec", "parcel_number": "1/1",
     "lat": 48.2, "lon": 17.4, "price_per_sqm": 10,
     "preliminary_score": 85.0, "prelim_recommendation": "STRONG BUY",
     "final_score": 0, "recommendation": "", "results": {}},
    {"url": "http://a.sk/2", "source_portal": "spf",
     "title": "Pozemok B", "price_eur": 3000, "area_sqm": 400,
     "location_text": "Pezinok", "parcel_number": "",
     "lat": 48.3, "lon": 17.3, "price_per_sqm": 7.5,
     "preliminary_score": 72.0, "prelim_recommendation": "INVESTIGATE",
     "final_score": 0, "recommendation": "", "results": {}},
]


class TestSaveAndLoad:
    def test_save_returns_run_id(self):
        rid = save_run(SAMPLE)
        assert isinstance(rid, int) and rid > 0

    def test_load_last_run_empty_initially(self):
        assert load_last_run() == []

    def test_load_last_run_after_save(self):
        save_run(SAMPLE)
        rows = load_last_run()
        assert len(rows) == 2

    def test_load_last_run_sorted_by_score(self):
        save_run(SAMPLE)
        rows = load_last_run()
        assert rows[0]["preliminary_score"] >= rows[1]["preliminary_score"]

    def test_load_run_by_id(self):
        rid = save_run(SAMPLE)
        rows = load_run(rid)
        assert len(rows) == 2

    def test_list_runs(self):
        save_run(SAMPLE)
        save_run(SAMPLE)
        runs = list_runs()
        assert len(runs) == 2

    def test_list_runs_limit(self):
        for _ in range(5):
            save_run(SAMPLE)
        assert len(list_runs(limit=3)) == 3

    def test_get_run_meta(self):
        rid = save_run(SAMPLE)
        meta = get_run_meta(rid)
        assert meta is not None
        assert meta["parcel_count"] == 2

    def test_get_run_meta_none_for_missing(self):
        assert get_run_meta(9999) is None

    def test_results_json_roundtrip(self):
        p = dict(SAMPLE[0])
        p["results"] = {"distance_service": {"ok": True, "score": 80.0}}
        save_run([p])
        rows = load_last_run()
        assert rows[0]["results"]["distance_service"]["score"] == 80.0

    def test_multiple_runs_last_is_newest(self):
        save_run([SAMPLE[0]])
        save_run([SAMPLE[1]])
        rows = load_last_run()
        assert len(rows) == 1
        assert rows[0]["url"] == "http://a.sk/2"


class TestPatchParcel:
    def test_patch_updates_final_score(self):
        save_run(SAMPLE)
        updated = dict(SAMPLE[0])
        updated["final_score"] = 91.5
        updated["recommendation"] = "STRONG BUY"


# ================================================================
# B1 — Testy histórie cien a first_seen
# ================================================================

class TestB1Schema:
    """Testy nových stĺpcov first_seen a price_history."""

    def test_first_run_sets_first_seen(self):
        save_run([SAMPLE[0]])
        rows = load_last_run()
        assert rows[0]["first_seen"] is not None
        assert len(rows[0]["first_seen"]) > 0

    def test_first_run_price_history_single_entry(self):
        save_run([SAMPLE[0]])
        rows = load_last_run()
        h = rows[0]["price_history"]
        assert isinstance(h, list)
        assert len(h) == 1
        assert h[0]["price_eur"] == pytest.approx(5000.0)

    def test_second_run_same_price_no_new_entry(self):
        """Druhý beh rovnaká cena → price_history zostane 1 záznam."""
        save_run([SAMPLE[0]])
        save_run([SAMPLE[0]])
        rows = load_last_run()
        h = rows[0]["price_history"]
        assert len(h) == 1

    def test_second_run_changed_price_adds_entry(self):
        """Druhý beh iná cena → price_history má 2 záznamy."""
        save_run([SAMPLE[0]])
        p2 = dict(SAMPLE[0])
        p2["price_eur"] = 4500.0
        save_run([p2])
        rows = load_last_run()
        h = rows[0]["price_history"]
        assert len(h) == 2
        assert h[0]["price_eur"] == pytest.approx(5000.0)
        assert h[1]["price_eur"] == pytest.approx(4500.0)

    def test_first_seen_preserved_across_runs(self):
        """first_seen z prvého behu sa zachová v druhom behu."""
        save_run([SAMPLE[0]])
        first_seen_1 = load_last_run()[0]["first_seen"]
        save_run([SAMPLE[0]])
        assert load_last_run()[0]["first_seen"] == first_seen_1

    def test_listing_age_days_is_zero_for_fresh(self):
        save_run([SAMPLE[0]])
        rows = load_last_run()
        assert rows[0]["listing_age_days"] == 0

    def test_listing_age_days_from_old_first_seen(self):
        """Starší first_seen → listing_age_days >= 149."""
        import services.storage_service as ss
        import sqlite3
        from datetime import datetime, timezone, timedelta
        old_date = (datetime.now(timezone.utc) - timedelta(days=150)).isoformat()
        save_run([SAMPLE[0]])
        conn = sqlite3.connect(str(ss._DB_PATH))
        conn.execute("UPDATE parcels SET first_seen=? WHERE url=?",
                     (old_date, "http://a.sk/1"))
        conn.commit()
        conn.close()
        rows = load_last_run()
        p = next(r for r in rows if r["url"] == "http://a.sk/1")
        assert p["listing_age_days"] >= 149

    def test_price_drop_pct_computed(self):
        """price_drop_pct = (5000-4000)/5000*100 = 20 %."""
        save_run([SAMPLE[0]])
        p2 = dict(SAMPLE[0]); p2["price_eur"] = 4000.0
        save_run([p2])
        rows = load_last_run()
        assert rows[0]["price_drop_pct"] == pytest.approx(20.0, abs=0.2)

    def test_price_drop_pct_zero_single_entry(self):
        save_run([SAMPLE[0]])
        rows = load_last_run()
        assert rows[0]["price_drop_pct"] == pytest.approx(0.0)

    def test_migration_old_db_without_columns(self):
        """_migrate_schema() zvládne existujúcu DB bez nových stĺpcov."""
        import services.storage_service as ss
        import sqlite3
        conn = sqlite3.connect(str(ss._DB_PATH))
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT NOT NULL, finished_at TEXT,
                parcel_count INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS parcels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL, url TEXT, source_portal TEXT, title TEXT,
                price_eur REAL DEFAULT 0, area_sqm REAL DEFAULT 0,
                location_text TEXT, parcel_number TEXT,
                lat REAL DEFAULT 0, lon REAL DEFAULT 0, price_per_sqm REAL DEFAULT 0,
                preliminary_score REAL DEFAULT 0, prelim_recommendation TEXT,
                final_score REAL DEFAULT 0, recommendation TEXT,
                results_json TEXT DEFAULT '{}', created_at TEXT NOT NULL
            );
        """)
        conn.commit()
        conn.close()  # Zatvoriť pred save_run aby sa predišlo PermissionError na Windows
        result = save_run([SAMPLE[0]])
        assert result > 0
        rows = load_last_run()
        assert rows[0].get("first_seen") is not None
        assert isinstance(rows[0].get("price_history"), list)


# ================================================================
# H2 — Testy perzistencie B2–B4 polí (signály, investment_index...)
# ================================================================

class TestH2Perzistencia:
    """Overuje, že signály a B2–B4 polia sa uložia do DB a načítajú späť."""

    def _sample_enriched(self):
        p = dict(SAMPLE[0])
        p["signals"] = [
            {"kod": "HORICE", "typ": "PRILEZITOST", "nazov": "test",
             "dovod": "test dovod", "dovera": 0.9},
            {"kod": "ZAPLAVA", "typ": "RIZIKO",     "nazov": "zaplava",
             "dovod": "test", "dovera": 0.8},
        ]
        p["investment_index"]     = 67
        p["investment_summary"]   = "Testové zdôvodnenie."
        p["peer_median_ppsm"]     = 45.0
        p["peer_count"]           = 6
        p["peer_ratio"]           = 0.44
        p["vyvolavacia_cena_eur"] = 35000.0
        p["znalecka_hodnota_eur"] = 50000.0
        p["drazba_kolo"]          = 2
        return p

    def test_signals_sa_ulozi_a_nacita(self):
        p = self._sample_enriched()
        save_run([p])
        rows = load_last_run()
        sigs = rows[0].get("signals", [])
        kody = [s["kod"] for s in sigs]
        assert "HORICE" in kody
        assert "ZAPLAVA" in kody

    def test_investment_index_sa_ulozi(self):
        save_run([self._sample_enriched()])
        rows = load_last_run()
        assert rows[0].get("investment_index") == 67

    def test_investment_summary_sa_ulozi(self):
        save_run([self._sample_enriched()])
        rows = load_last_run()
        assert rows[0].get("investment_summary") == "Testové zdôvodnenie."

    def test_peer_polia_sa_ulozia(self):
        save_run([self._sample_enriched()])
        rows = load_last_run()
        r = rows[0]
        assert r.get("peer_median_ppsm") == pytest.approx(45.0)
        assert r.get("peer_count") == 6
        assert r.get("peer_ratio") == pytest.approx(0.44)

    def test_drazobne_polia_sa_ulozia(self):
        save_run([self._sample_enriched()])
        rows = load_last_run()
        r = rows[0]
        assert r.get("vyvolavacia_cena_eur") == pytest.approx(35000.0)
        assert r.get("znalecka_hodnota_eur") == pytest.approx(50000.0)
        assert r.get("drazba_kolo") == 2

    def test_signals_prazdny_zoznam_nehavaruje(self):
        p = dict(SAMPLE[0])
        p["signals"] = []
        save_run([p])
        rows = load_last_run()
        assert rows[0].get("signals") == []

    def test_stara_db_bez_stlpcov_migruje(self):
        """Existujúca DB bez B2–B4 stĺpcov sa migruje bez chyby."""
        import services.storage_service as ss
        import sqlite3
        conn = sqlite3.connect(str(ss._DB_PATH))
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT NOT NULL, finished_at TEXT,
                parcel_count INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS parcels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL, url TEXT, source_portal TEXT, title TEXT,
                price_eur REAL DEFAULT 0, area_sqm REAL DEFAULT 0,
                location_text TEXT, parcel_number TEXT,
                lat REAL DEFAULT 0, lon REAL DEFAULT 0, price_per_sqm REAL DEFAULT 0,
                preliminary_score REAL DEFAULT 0, prelim_recommendation TEXT,
                final_score REAL DEFAULT 0, recommendation TEXT,
                results_json TEXT DEFAULT '{}', created_at TEXT NOT NULL
            );
        """)
        conn.commit()
        conn.close()
        # Po migrácii musí save_run + load_last_run fungovať
        result = save_run([SAMPLE[0]])
        assert result > 0
        rows = load_last_run()
        assert rows[0].get("signals") is not None
        assert isinstance(rows[0].get("investment_index"), int)

        conn.close()
        result = save_run([SAMPLE[0]])
        assert result > 0
        rows = load_last_run()
        assert rows[0].get("first_seen") is not None
        assert isinstance(rows[0].get("price_history"), list)

    def test_three_price_changes_history(self):
        """Tri rôzne ceny → price_history má 3 záznamy."""
        save_run([SAMPLE[0]])
        p2 = dict(SAMPLE[0]); p2["price_eur"] = 4500.0
        save_run([p2])
        p3 = dict(SAMPLE[0]); p3["price_eur"] = 4000.0
        save_run([p3])
        rows = load_last_run()
        h = rows[0]["price_history"]
        assert len(h) == 3
        assert h[0]["price_eur"] == pytest.approx(5000.0)
        assert h[2]["price_eur"] == pytest.approx(4000.0)

    def test_new_url_gets_fresh_history(self):
        save_run([SAMPLE[1]])
        rows = load_last_run()
        assert rows[0]["first_seen"] is not None
        assert len(rows[0]["price_history"]) == 1

    def test_patch_results_json(self):
        save_run(SAMPLE)
        updated = dict(SAMPLE[0])
        updated["results"] = {"overpass_service": {"ok": True, "score": 60.0}}
        patch_parcel("http://a.sk/1", updated)
        rows = load_last_run()
        p = next(r for r in rows if r["url"] == "http://a.sk/1")
        assert p["results"]["overpass_service"]["score"] == 60.0
