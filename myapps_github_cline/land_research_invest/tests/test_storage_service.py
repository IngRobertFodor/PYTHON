import sys, pathlib, tempfile
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
        # pred prvym behom
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
        ok = patch_parcel("http://a.sk/1", updated)
        assert ok is True
        rows = load_last_run()
        p = next(r for r in rows if r["url"] == "http://a.sk/1")
        assert p["final_score"] == pytest.approx(91.5)
        assert p["recommendation"] == "STRONG BUY"

    def test_patch_unknown_url_returns_false(self):
        save_run(SAMPLE)
        ok = patch_parcel("http://no.such.url/999", {"final_score": 50})
        assert ok is False

    def test_patch_results_json(self):
        save_run(SAMPLE)
        updated = dict(SAMPLE[0])
        updated["results"] = {"overpass_service": {"ok": True, "score": 60.0}}
        patch_parcel("http://a.sk/1", updated)
        rows = load_last_run()
        p = next(r for r in rows if r["url"] == "http://a.sk/1")
        assert p["results"]["overpass_service"]["score"] == 60.0
