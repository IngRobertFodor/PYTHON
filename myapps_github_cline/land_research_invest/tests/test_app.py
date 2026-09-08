"""Testy - Flask app (app.py + routes)
======================================
Testuje vsetky endpointy cez Flask test_client.
100% offline - pipeline_service je mocknuty.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from models.parcel import Parcel
from models.result import ServiceResult
from app import create_app

MODULE_PIPELINE  = "routes.parcel_routes.analyze_parcel"
MODULE_NOTIFIER  = "routes.parcel_routes.notify_parcel"


@pytest.fixture
def client():
    app = create_app({"TESTING": True})
    with app.test_client() as c:
        yield c


def make_parcel_json(**kw):
    base = {
        "title":         "Test Senec",
        "price_eur":     35000,
        "area_sqm":      800,
        "location_text": "Senec, Slovakia",
        "url":           "https://example.com/1",
    }
    base.update(kw)
    return base


def mock_analyze(parcel):
    """Nastavenie vysledkov bez HTTP callou."""
    parcel.final_score   = 78.0
    parcel.recommendation = "INVESTIGATE"
    parcel.add_result(ServiceResult(
        ok=True, score=78.0,
        data={"text_report": "OK report", "recommendation": "INVESTIGATE"},
        source="report_service",
    ))
    return parcel


def mock_notify(parcel):
    return ServiceResult.skip_result("notifier_service", "testing")


# ----------------------------------------------------------------
# TestCreateApp
# ----------------------------------------------------------------

class TestCreateApp:
    def test_returns_flask_app(self, client):
        from flask import Flask
        from app import create_app
        app = create_app({"TESTING": True})
        assert isinstance(app, Flask)

    def test_testing_mode(self, client):
        from app import create_app
        app = create_app({"TESTING": True})
        assert app.config["TESTING"] is True

    def test_three_blueprints_registered(self, client):
        from app import create_app
        app = create_app({"TESTING": True})
        assert set(app.blueprints.keys()) == {"health", "config", "parcels"}


# ----------------------------------------------------------------
# TestHealthRoute
# ----------------------------------------------------------------

class TestHealthRoute:
    def test_returns_200(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200

    def test_status_ok(self, client):
        r = client.get("/api/health")
        assert r.get_json()["status"] == "ok"

    def test_services_count(self, client):
        r = client.get("/api/health")
        data = r.get_json()
        assert isinstance(data["services_count"], int)
        assert data["services_count"] > 0

    def test_services_list_present(self, client):
        r = client.get("/api/health")
        assert isinstance(r.get_json()["services"], list)

    def test_version_present(self, client):
        r = client.get("/api/health")
        assert "version" in r.get_json()

    def test_cors_header(self, client):
        r = client.get("/api/health",
                        headers={"Origin": "http://localhost:3000"})
        assert "Access-Control-Allow-Origin" in r.headers


# ----------------------------------------------------------------
# TestConfigRoutes
# ----------------------------------------------------------------

class TestConfigRoutes:
    def test_get_config_returns_200(self, client):
        assert client.get("/api/config/").status_code == 200

    def test_get_config_has_scoring(self, client):
        data = client.get("/api/config/").get_json()
        assert "scoring" in data

    def test_get_config_has_weights(self, client):
        data = client.get("/api/config/").get_json()
        assert "weights" in data["scoring"]

    def test_get_config_has_thresholds(self, client):
        data = client.get("/api/config/").get_json()
        assert "thresholds" in data["scoring"]

    def test_get_config_has_features(self, client):
        assert "features" in client.get("/api/config/").get_json()

    def test_get_config_has_notifications(self, client):
        assert "notifications" in client.get("/api/config/").get_json()

    def test_validate_returns_200(self, client):
        assert client.get("/api/config/validate").status_code == 200

    def test_validate_valid_flag(self, client):
        data = client.get("/api/config/validate").get_json()
        assert "valid" in data

    def test_validate_errors_list(self, client):
        data = client.get("/api/config/validate").get_json()
        assert isinstance(data["errors"], list)

    def test_validate_config_is_valid(self, client):
        data = client.get("/api/config/validate").get_json()
        assert data["valid"] is True
        assert data["errors"] == []


# ----------------------------------------------------------------
# TestAnalyzeRoute - POST /api/analyze
# ----------------------------------------------------------------

class TestAnalyzeRoute:
    def test_valid_request_returns_200(self, client):
        with patch(MODULE_PIPELINE, side_effect=mock_analyze), \
             patch(MODULE_NOTIFIER, side_effect=mock_notify):
            r = client.post("/api/analyze",
                            json=make_parcel_json())
        assert r.status_code == 200

    def test_response_has_parcel(self, client):
        with patch(MODULE_PIPELINE, side_effect=mock_analyze), \
             patch(MODULE_NOTIFIER, side_effect=mock_notify):
            data = client.post("/api/analyze", json=make_parcel_json()).get_json()
        assert "parcel" in data

    def test_response_has_report(self, client):
        with patch(MODULE_PIPELINE, side_effect=mock_analyze), \
             patch(MODULE_NOTIFIER, side_effect=mock_notify):
            data = client.post("/api/analyze", json=make_parcel_json()).get_json()
        assert "report" in data

    def test_parcel_has_final_score(self, client):
        with patch(MODULE_PIPELINE, side_effect=mock_analyze), \
             patch(MODULE_NOTIFIER, side_effect=mock_notify):
            data = client.post("/api/analyze", json=make_parcel_json()).get_json()
        assert "final_score" in data["parcel"]

    def test_parcel_has_recommendation(self, client):
        with patch(MODULE_PIPELINE, side_effect=mock_analyze), \
             patch(MODULE_NOTIFIER, side_effect=mock_notify):
            data = client.post("/api/analyze", json=make_parcel_json()).get_json()
        assert data["parcel"]["recommendation"] == "INVESTIGATE"

    def test_missing_title_returns_400(self, client):
        body = make_parcel_json()
        del body["title"]
        r = client.post("/api/analyze", json=body)
        assert r.status_code == 400

    def test_missing_price_returns_400(self, client):
        body = make_parcel_json()
        del body["price_eur"]
        r = client.post("/api/analyze", json=body)
        assert r.status_code == 400

    def test_missing_location_returns_400(self, client):
        body = make_parcel_json()
        del body["location_text"]
        r = client.post("/api/analyze", json=body)
        assert r.status_code == 400

    def test_400_contains_missing_fields(self, client):
        body = make_parcel_json()
        del body["title"]
        data = client.post("/api/analyze", json=body).get_json()
        assert "missing_fields" in data
        assert "title" in data["missing_fields"]

    def test_empty_body_returns_400(self, client):
        r = client.post("/api/analyze", json={})
        assert r.status_code == 400

    def test_pipeline_exception_returns_500(self, client):
        with patch(MODULE_PIPELINE, side_effect=RuntimeError("GIS timeout")):
            r = client.post("/api/analyze", json=make_parcel_json())
        assert r.status_code == 500

    def test_500_contains_error_key(self, client):
        with patch(MODULE_PIPELINE, side_effect=RuntimeError("err")):
            data = client.post("/api/analyze", json=make_parcel_json()).get_json()
        assert "error" in data


# ----------------------------------------------------------------
# TestAnalyzeBatchRoute - POST /api/parcels/analyze-batch
# ----------------------------------------------------------------

class TestAnalyzeBatchRoute:
    def test_valid_batch_returns_200(self, client):
        with patch(MODULE_PIPELINE, side_effect=mock_analyze), \
             patch(MODULE_NOTIFIER, side_effect=mock_notify):
            r = client.post("/api/parcels/analyze-batch",
                            json={"parcels": [make_parcel_json(), make_parcel_json()]})
        assert r.status_code == 200

    def test_result_contains_results_list(self, client):
        with patch(MODULE_PIPELINE, side_effect=mock_analyze), \
             patch(MODULE_NOTIFIER, side_effect=mock_notify):
            data = client.post("/api/parcels/analyze-batch",
                               json={"parcels": [make_parcel_json()]}).get_json()
        assert "results" in data
        assert isinstance(data["results"], list)

    def test_result_count_matches(self, client):
        with patch(MODULE_PIPELINE, side_effect=mock_analyze), \
             patch(MODULE_NOTIFIER, side_effect=mock_notify):
            data = client.post("/api/parcels/analyze-batch",
                               json={"parcels": [make_parcel_json(), make_parcel_json()]}).get_json()
        assert data["count"] == 2

    def test_results_sorted_by_score_desc(self, client):
        scores = [60.0, 90.0, 75.0]
        idx = [0]
        def mock_analyze_varying(parcel):
            parcel.final_score = scores[idx[0] % len(scores)]
            parcel.recommendation = "CONSIDER"
            parcel.add_result(ServiceResult(
                ok=True, score=parcel.final_score,
                data={"text_report": "ok"},
                source="report_service"))
            idx[0] += 1
            return parcel
        with patch(MODULE_PIPELINE, side_effect=mock_analyze_varying), \
             patch(MODULE_NOTIFIER, side_effect=mock_notify):
            data = client.post("/api/parcels/analyze-batch",
                               json={"parcels": [make_parcel_json()]*3}).get_json()
        sc = [r["final_score"] for r in data["results"]]
        assert sc == sorted(sc, reverse=True)

    def test_missing_parcels_key_returns_400(self, client):
        r = client.post("/api/parcels/analyze-batch", json={"other": []})
        assert r.status_code == 400

    def test_empty_parcels_list_returns_200(self, client):
        r = client.post("/api/parcels/analyze-batch", json={"parcels": []})
        assert r.status_code == 200
        assert r.get_json()["count"] == 0

    def test_invalid_parcel_in_batch_recorded_as_error(self, client):
        invalid = {"title": "", "price_eur": 0, "area_sqm": 0, "location_text": ""}
        valid   = make_parcel_json()
        with patch(MODULE_PIPELINE, side_effect=mock_analyze), \
             patch(MODULE_NOTIFIER, side_effect=mock_notify):
            data = client.post("/api/parcels/analyze-batch",
                               json={"parcels": [invalid, valid]}).get_json()
        assert len(data["errors"]) >= 1
        assert data["count"] == 1


# ----------------------------------------------------------------
# TestFrontendServing
# ----------------------------------------------------------------

class TestFrontendServing:
    def test_root_returns_200(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_root_returns_html(self, client):
        r = client.get("/")
        assert b"<!DOCTYPE html>" in r.data or b"<!doctype html>" in r.data.lower()

    def test_root_contains_app_title(self, client):
        r = client.get("/")
        assert b"Land Research Invest" in r.data

    def test_root_content_type_html(self, client):
        r = client.get("/")
        assert "text/html" in r.content_type
