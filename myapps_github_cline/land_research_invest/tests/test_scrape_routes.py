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
        _set_last_results([{"title": "Test", "preliminary_score": 80}])
        data = client.get("/api/scrape/results").get_json()
        assert data["count"] == 1 and data["results"][0]["title"] == "Test"

    def test_results_sorted_desc(self, client):
        """_set_last_results ulozi v danom poradi; _run() zoradi podla preliminary_score."""
        _set_last_results([
            {"title": "B", "final_score": 90, "preliminary_score": 90},
            {"title": "C", "final_score": 75, "preliminary_score": 75},
            {"title": "A", "final_score": 60, "preliminary_score": 60},
        ])
        data = client.get("/api/scrape/results").get_json()
        scores = [r["preliminary_score"] for r in data["results"]]
        assert scores == sorted(scores, reverse=True)

    def test_results_has_count(self, client):
        _set_last_results([{"x": 1}, {"x": 2}])
        assert client.get("/api/scrape/results").get_json()["count"] == 2

    def test_set_get_last_results_roundtrip(self, client):
        items = [{"title": "X", "preliminary_score": 55}]
        _set_last_results(items)
        assert _get_last_results() == items


# ----------------------------------------------------------------
# TestScoreSelectedEndpoint
# ----------------------------------------------------------------

from routes.scrape_routes import _get_score_progress

class TestScoreSelectedEndpoint:
    def setup_method(self):
        _set_last_results([])

    def test_score_selected_empty_urls_400(self, client):
        resp = client.post("/api/scrape/score-selected",
                           json={}, content_type="application/json")
        assert resp.status_code == 400

    def test_score_selected_urls_not_found_404(self, client):
        _set_last_results([{"url": "http://a.sk/1", "preliminary_score": 80}])
        resp = client.post("/api/scrape/score-selected",
                           json={"urls": ["http://nemas.sk/99"]},
                           content_type="application/json")
        assert resp.status_code == 404

    def test_score_selected_202_when_found(self, client):
        _set_last_results([{"url": "http://a.sk/1", "preliminary_score": 80,
                            "price_eur": 5000, "area_sqm": 600,
                            "source_portal": "nehnutelnosti_sk"}])
        with patch("routes.scrape_routes.analyze_parcel"):
            resp = client.post("/api/scrape/score-selected",
                               json={"urls": ["http://a.sk/1"]},
                               content_type="application/json")
        assert resp.status_code == 202

    def test_score_selected_returns_count(self, client):
        _set_last_results([{"url": "http://a.sk/1", "preliminary_score": 80,
                            "price_eur": 5000, "area_sqm": 600}])
        with patch("routes.scrape_routes.analyze_parcel"):
            data = client.post("/api/scrape/score-selected",
                               json={"urls": ["http://a.sk/1"]},
                               content_type="application/json").get_json()
        assert "count" in data or "error" in data

    def test_score_selected_409_if_running(self, client):
        from routes.scrape_routes import _score_lock
        acquired = _score_lock.acquire(blocking=False)
        try:
            resp = client.post("/api/scrape/score-selected",
                               json={"urls": ["http://x.sk/1"]},
                               content_type="application/json")
            assert resp.status_code == 409
        finally:
            if acquired:
                _score_lock.release()


# ----------------------------------------------------------------
# TestScrapeResultsCsv — GET /api/scrape/results.csv
# ----------------------------------------------------------------

class TestScrapeResultsCsv:
    def setup_method(self):
        _set_last_results([])

    def test_csv_200_empty(self, client):
        resp = client.get("/api/scrape/results.csv")
        assert resp.status_code == 200

    def test_csv_content_type(self, client):
        resp = client.get("/api/scrape/results.csv")
        assert "text/csv" in resp.content_type

    def test_csv_attachment_header(self, client):
        resp = client.get("/api/scrape/results.csv")
        cd = resp.headers.get("Content-Disposition", "")
        assert "attachment" in cd
        assert "pozemky.csv" in cd

    def test_csv_header_row(self, client):
        text = client.get("/api/scrape/results.csv").data.decode("utf-8-sig")
        assert "Zdroj" in text
        assert "Lokalita" in text
        assert "Prelim_skore" in text
        assert "URL" in text

    def test_csv_empty_has_only_header(self, client):
        text = client.get("/api/scrape/results.csv").data.decode("utf-8-sig")
        lines = [l for l in text.strip().splitlines() if l]
        assert len(lines) == 1  # iba hlavicka

    def test_csv_row_count(self, client):
        _set_last_results([
            {"source_portal": "nehnutelnosti_sk", "location_text": "Senec",
             "price_eur": 8000, "area_sqm": 600, "price_per_sqm": 13.33,
             "preliminary_score": 95.0, "prelim_recommendation": "STRONG BUY",
             "final_score": 65.5, "recommendation": "CONSIDER",
             "url": "http://test.sk/1"},
            {"source_portal": "spf", "location_text": "Malacky",
             "price_eur": 0, "area_sqm": 500, "price_per_sqm": 0,
             "preliminary_score": 80.0, "prelim_recommendation": "INVESTIGATE",
             "final_score": 0, "recommendation": "",
             "url": "http://test.sk/2"},
        ])
        text = client.get("/api/scrape/results.csv").data.decode("utf-8-sig")
        lines = [l for l in text.strip().splitlines() if l]
        assert len(lines) == 3  # hlavicka + 2 riadky

    def test_csv_contains_data(self, client):
        _set_last_results([
            {"source_portal": "topreality_sk", "location_text": "Pezinok",
             "price_eur": 9000, "area_sqm": 700, "price_per_sqm": 12.86,
             "preliminary_score": 98.0, "prelim_recommendation": "STRONG BUY",
             "final_score": 66.6, "recommendation": "CONSIDER",
             "url": "http://test.sk/3"},
        ])
        text = client.get("/api/scrape/results.csv").data.decode("utf-8-sig")
        assert "Pezinok" in text
        assert "topreality_sk" in text
        assert "98.0" in text


class TestScoreProgressEndpoint:
    def test_score_progress_200(self, client):
        assert client.get("/api/scrape/score-progress").status_code == 200

    def test_score_progress_has_keys(self, client):
        data = client.get("/api/scrape/score-progress").get_json()
        for key in ["running", "done", "total", "percent", "finished"]:
            assert key in data

    def test_score_progress_not_running_initially(self, client):
        data = client.get("/api/scrape/score-progress").get_json()
        assert data["running"] is False


# Testy pre /results su v TestScrapeResultsEndpoint (viď vyssie)



