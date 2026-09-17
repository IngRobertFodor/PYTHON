"""Testy - scrape_routes (GET /api/scrape/progress, POST /api/scrape/start, GET /api/scrape/results)
====================================================================================================
100% offline - mocked scrape_all + progress stav.
"""

import pytest
from unittest.mock import patch, MagicMock

from app import create_app
from services.scraper_service import _progress, _progress_lock, _reset_progress, _finish_progress
from routes.scrape_routes import _set_last_results, _get_last_results


@pytest.fixture
def client():
    app = create_app({"TESTING": True})
    with app.test_client() as c:
        yield c


def _set_progress(**kwargs):
    with _progress_lock:
        _progress.update(kwargs)


# ----------------------------------------------------------------
# TestScrapeProgressEndpoint
# ----------------------------------------------------------------

class TestScrapeProgressEndpoint:
    def test_get_progress_200(self, client):
        resp = client.get("/api/scrape/progress")
        assert resp.status_code == 200

    def test_get_progress_json(self, client):
        assert isinstance(client.get("/api/scrape/progress").get_json(), dict)

    def test_get_progress_has_keys(self, client):
        data = client.get("/api/scrape/progress").get_json()
        for key in ["running", "total", "done", "percent", "finished", "total_parcels"]:
            assert key in data

    def test_get_progress_not_running_initially(self, client):
        _set_progress(running=False, finished=False)
        assert client.get("/api/scrape/progress").get_json()["running"] is False

    def test_get_progress_reflects_state(self, client):
        _set_progress(running=True, done=3, total=7, percent=43)
        data = client.get("/api/scrape/progress").get_json()
        assert data["done"] == 3 and data["total"] == 7 and data["percent"] == 43

    def test_get_progress_finished(self, client):
        _set_progress(running=False, finished=True, percent=100, total_parcels=2483)
        data = client.get("/api/scrape/progress").get_json()
        assert data["finished"] is True and data["total_parcels"] == 2483


# ----------------------------------------------------------------
# TestScrapeStartEndpoint
# ----------------------------------------------------------------

class TestScrapeStartEndpoint:
    def setup_method(self):
        _set_progress(running=False, finished=False, total=0, done=0,
                      percent=0, sources=[], per_source={}, elapsed_s=0.0, total_parcels=0)

    def test_post_start_202(self, client):
        with patch("routes.scrape_routes.scrape_all", return_value=[]):
            with patch("routes.scrape_routes.analyze_parcel"):
                resp = client.post("/api/scrape/start")
        assert resp.status_code == 202

    def test_post_start_returns_message(self, client):
        with patch("routes.scrape_routes.scrape_all", return_value=[]):
            with patch("routes.scrape_routes.analyze_parcel"):
                data = client.post("/api/scrape/start").get_json()
        assert "message" in data or "error" in data

    def test_post_start_409_if_running(self, client):
        _set_progress(running=True)
        assert client.post("/api/scrape/start").status_code == 409

    def test_post_start_409_has_error_key(self, client):
        _set_progress(running=True)
        assert "error" in client.post("/api/scrape/start").get_json()

    def test_progress_accessible_during_run(self, client):
        _set_progress(running=True, done=2, total=7, percent=28)
        resp = client.get("/api/scrape/progress")
        assert resp.status_code == 200 and resp.get_json()["running"] is True


# ----------------------------------------------------------------
# TestScrapeResultsEndpoint
# ----------------------------------------------------------------

class TestScrapeResultsEndpoint:
    def setup_method(self):
        _set_last_results([])

    def test_results_200_empty(self, client):
        resp = client.get("/api/scrape/results")
        assert resp.status_code == 200

    def test_results_empty_list(self, client):
        data = client.get("/api/scrape/results").get_json()
        assert data["count"] == 0 and data["results"] == []

    def test_results_returns_stored(self, client):
        _set_last_results([{"title": "Test", "final_score": 80}])
        data = client.get("/api/scrape/results").get_json()
        assert data["count"] == 1 and data["results"][0]["title"] == "Test"

    def test_results_sorted_desc(self, client):
        """_set_last_results ulozi v danom poradi; _run() zoradi pred ulozenim."""
        # Simulujeme co by _run() ulozil (uz zoradene)
        _set_last_results([
            {"title": "B", "final_score": 90},
            {"title": "C", "final_score": 75},
            {"title": "A", "final_score": 60},
        ])
        data = client.get("/api/scrape/results").get_json()
        scores = [r["final_score"] for r in data["results"]]
        assert scores == sorted(scores, reverse=True)

    def test_results_has_count(self, client):
        _set_last_results([{"x": 1}, {"x": 2}])
        data = client.get("/api/scrape/results").get_json()
        assert data["count"] == 2

    def test_set_get_last_results_roundtrip(self, client):
        items = [{"title": "X", "final_score": 55}]
        _set_last_results(items)
        assert _get_last_results() == items

