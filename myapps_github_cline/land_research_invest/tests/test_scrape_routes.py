"""Testy - scrape_routes (GET /api/scrape/progress, POST /api/scrape/start)
============================================================================
100% offline - mocked scrape_all + progress stav.
"""

import pytest
from unittest.mock import patch, MagicMock

from app import create_app
from services.scraper_service import _progress, _progress_lock, _reset_progress, _finish_progress


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
        data = client.get("/api/scrape/progress").get_json()
        assert isinstance(data, dict)

    def test_get_progress_has_keys(self, client):
        data = client.get("/api/scrape/progress").get_json()
        for key in ["running", "total", "done", "percent",
                    "finished", "total_parcels"]:
            assert key in data, f"Chybajuci kluc: {key}"

    def test_get_progress_not_running_initially(self, client):
        _set_progress(running=False, finished=False)
        data = client.get("/api/scrape/progress").get_json()
        assert data["running"] is False

    def test_get_progress_reflects_state(self, client):
        _set_progress(running=True, done=3, total=7, percent=43)
        data = client.get("/api/scrape/progress").get_json()
        assert data["running"] is True
        assert data["done"] == 3
        assert data["total"] == 7
        assert data["percent"] == 43

    def test_get_progress_finished(self, client):
        _set_progress(running=False, finished=True, percent=100, total_parcels=2483)
        data = client.get("/api/scrape/progress").get_json()
        assert data["finished"] is True
        assert data["total_parcels"] == 2483


# ----------------------------------------------------------------
# TestScrapeStartEndpoint
# ----------------------------------------------------------------

class TestScrapeStartEndpoint:
    def setup_method(self):
        _set_progress(running=False, finished=False, total=0, done=0,
                      percent=0, sources=[], per_source={},
                      elapsed_s=0.0, total_parcels=0)

    def test_post_start_202(self, client):
        with patch("routes.scrape_routes.scrape_all", return_value=[]):
            resp = client.post("/api/scrape/start")
        assert resp.status_code == 202

    def test_post_start_returns_message(self, client):
        with patch("routes.scrape_routes.scrape_all", return_value=[]):
            data = client.post("/api/scrape/start").get_json()
        assert "message" in data or "error" in data

    def test_post_start_409_if_running(self, client):
        _set_progress(running=True)
        resp = client.post("/api/scrape/start")
        assert resp.status_code == 409

    def test_post_start_409_has_error_key(self, client):
        _set_progress(running=True)
        data = client.post("/api/scrape/start").get_json()
        assert "error" in data

    def test_post_start_not_running_initially(self, client):
        _set_progress(running=False)
        with patch("routes.scrape_routes.scrape_all", return_value=[]):
            resp = client.post("/api/scrape/start")
        assert resp.status_code in (202, 409)  # 202 ak OK, 409 ak lock uz drzany

    def test_progress_endpoint_accessible_during_run(self, client):
        """GET /progress musi fungovat aj ked /start prave bezi."""
        _set_progress(running=True, done=2, total=7, percent=28)
        resp = client.get("/api/scrape/progress")
        assert resp.status_code == 200
        assert resp.get_json()["running"] is True
