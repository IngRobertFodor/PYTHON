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

    def test_blueprints_registered(self, client):
        from app import create_app
        app = create_app({"TESTING": True})
        assert {"health", "config", "parcels", "monitor", "scrape", "backup"} \
               <= set(app.blueprints.keys())


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
        """CORS je povolený pre localhost:5001 (nie pre arbitrary origins)."""
        # Povolený origin (localhost:5001)
        r = client.get("/api/health",
                        headers={"Origin": "http://localhost:5001"})
        assert "Access-Control-Allow-Origin" in r.headers

    def test_cors_blocked_for_external_origin(self, client):
        """CORS blokuje arbitrary externé origins (ochrana pred S2)."""
        r = client.get("/api/health",
                        headers={"Origin": "http://evil.com"})
        # Flask-CORS buď vráti header s hodnotou 'http://evil.com' (old behavior)
        # alebo ho vynechá — v každom prípade NE-smie byť '*'
        acao = r.headers.get("Access-Control-Allow-Origin", "")
        assert acao != "*", "CORS nesmie povolovat * origins"


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

    def test_root_subtitle_has_km_number(self, client):
        r = client.get("/")
        # Server-side render: {{MAX_KM}} musi byt nahradeny cislom, nie ponechany ako placeholder
        assert b"{{MAX_KM}}" not in r.data
        # Subtitle musi obsahovat "km od Bratislavy"
        assert b"km od Bratislavy" in r.data

    def test_root_limits_server_rendered(self, client):
        r = client.get("/")
        html = r.data
        # Ziadny placeholder nesmie ostat nenahradeny
        assert b"{{MAX_KM}}"    not in html
        assert b"{{MAX_PRICE}}" not in html
        assert b"{{MIN_AREA}}"  not in html
        assert b"{{MAX_AREA}}"  not in html
        # Vsetky inputy musia mat konkretne ciselne hodnoty
        assert b'value="' in html  # aspon jeden input s hodnotou

    def test_root_content_type_html(self, client):
        r = client.get("/")
        assert "text/html" in r.content_type

    def test_root_has_ai_agent_root(self, client):
        """index.html musí obsahovať placeholder pre AI widget."""
        r = client.get("/")
        assert b'id="ai-agent-root"' in r.data

    def test_root_has_ai_agent_css(self, client):
        """index.html musí načítavať ai_agent.css."""
        r = client.get("/")
        assert b"ai_agent.css" in r.data

    def test_root_has_ai_agent_js(self, client):
        """index.html musí načítavať ai_agent.js."""
        r = client.get("/")
        assert b"ai_agent.js" in r.data


# ----------------------------------------------------------------
# TestConfigRoutes  —  GET /api/config/  GET /api/config/validate
#                      POST /api/config/limits
# ----------------------------------------------------------------

class TestConfigRoutes:
    def setup_method(self):
        """Uloží raw bytes criteria.yaml pred každým testom."""
        import pathlib
        p = pathlib.Path(__file__).parent.parent / "config" / "criteria.yaml"
        self._yaml_backup = p.read_bytes()
        self._yaml_path = p

    def teardown_method(self, method):
        """Obnoví criteria.yaml vrátane komentárov po každom teste."""
        from config_loader import reload_config
        self._yaml_path.write_bytes(self._yaml_backup)
        reload_config()  # invaliduje cache

    def test_get_config_200(self, client):
        r = client.get("/api/config/")
        assert r.status_code == 200

    def test_get_config_has_sections(self, client):
        data = client.get("/api/config/").get_json()
        for key in ("scoring", "criteria", "features", "notifications"):
            assert key in data, f"Chýba sekcia: {key}"

    def test_get_config_scoring_has_weights(self, client):
        data = client.get("/api/config/").get_json()
        assert "weights" in data["scoring"]

    def test_get_config_criteria_has_location(self, client):
        data = client.get("/api/config/").get_json()
        assert "location" in data["criteria"]

    def test_validate_config_200(self, client):
        r = client.get("/api/config/validate")
        assert r.status_code == 200

    def test_validate_config_valid_field(self, client):
        data = client.get("/api/config/validate").get_json()
        assert "valid" in data
        assert isinstance(data["valid"], bool)

    def test_validate_config_errors_list(self, client):
        data = client.get("/api/config/validate").get_json()
        assert isinstance(data["errors"], list)

    def test_validate_config_is_valid(self, client):
        """Realna criteria.yaml musi byt platna."""
        data = client.get("/api/config/validate").get_json()
        assert data["valid"] is True, f"criteria.yaml invalid: {data['errors']}"

    def test_update_limits_200(self, client):
        """POST /api/config/limits aktualizuje max_eur a vrati ok=True."""
        r = client.post("/api/config/limits", json={"max_eur": 9000})
        assert r.status_code == 200
        data = r.get_json()
        assert data["ok"] is True
        assert data["saved"]["max_eur"] == 9000

    def test_update_limits_unknown_field_400(self, client):
        r = client.post("/api/config/limits", json={"unknown_field": 999})
        assert r.status_code == 400

    def test_update_limits_non_number_400(self, client):
        r = client.post("/api/config/limits", json={"max_eur": "nie_cislo"})
        assert r.status_code == 400

    def test_update_limits_empty_body_400(self, client):
        r = client.post("/api/config/limits", json={})
        assert r.status_code == 400

    def test_update_limits_invalid_value_400(self, client):
        """Záporná max_eur musí byť odmietnutá validátorom."""
        r = client.post("/api/config/limits", json={"max_eur": -1})
        assert r.status_code == 400

    def test_update_limits_criteria_returned(self, client):
        """Odpoveď obsahuje aktualizované criteria."""
        r = client.post("/api/config/limits", json={"max_eur": 8500})
        data = r.get_json()
        assert "criteria" in data

    def test_update_all_limits(self, client):
        """Všetky 4 polia naraz — ok a vrátia sa v saved."""
        payload = {
            "max_eur": 7500,
            "min_area_sqm": 300,
            "max_area_sqm": 900,
            "max_distance_km": 70,
        }
        r = client.post("/api/config/limits", json=payload)
        assert r.status_code == 200
        data = r.get_json()
        assert data["ok"] is True
        for k, v in payload.items():
            assert data["saved"][k] == v


# ----------------------------------------------------------------
# TestBackupRoutes  —  GET /api/backup/status   GET /api/backup/history
#                      GET /api/backup/export   POST /api/backup/import
# ----------------------------------------------------------------

class TestBackupRoutes:
    def setup_method(self):
        """Reset rate-limit timestampu pred každým testom."""
        from routes.backup_routes import _IMPORT_RATE_LOCK_TS
        _IMPORT_RATE_LOCK_TS[0] = 0.0

    def test_status_200(self, client):
        r = client.get("/api/backup/status")
        assert r.status_code == 200

    def test_status_has_expected_keys(self, client):
        data = client.get("/api/backup/status").get_json()
        for key in ("latest_backup", "history_count", "db_size_kb", "db_runs", "db_parcels"):
            assert key in data, f"Chýba kľúč: {key}"

    def test_status_db_parcels_is_int(self, client):
        data = client.get("/api/backup/status").get_json()
        assert isinstance(data["db_parcels"], int)

    def test_status_db_runs_is_int(self, client):
        data = client.get("/api/backup/status").get_json()
        assert isinstance(data["db_runs"], int)

    def test_history_200(self, client):
        r = client.get("/api/backup/history")
        assert r.status_code == 200

    def test_history_returns_list(self, client):
        data = client.get("/api/backup/history").get_json()
        assert isinstance(data, list)

    def test_export_200(self, client):
        r = client.get("/api/backup/export")
        assert r.status_code == 200

    def test_export_content_type_gzip(self, client):
        r = client.get("/api/backup/export")
        ct = r.content_type
        assert "gzip" in ct or "octet-stream" in ct

    def test_export_content_disposition(self, client):
        r = client.get("/api/backup/export")
        assert "parcels_latest.sql.gz" in r.headers.get("Content-Disposition", "")

    def test_export_is_valid_gzip(self, client):
        import gzip
        r = client.get("/api/backup/export")
        assert r.status_code == 200
        assert r.data[:2] == b"\x1f\x8b"
        decompressed = gzip.decompress(r.data).decode("utf-8")
        assert "CREATE TABLE" in decompressed or "BEGIN TRANSACTION" in decompressed

    def test_import_missing_file_400(self, client):
        r = client.post("/api/backup/import", data={})
        assert r.status_code == 400

    def test_import_invalid_content_400(self, client):
        """Nie-gzip obsah musí byť odmietnutý."""
        from io import BytesIO
        data = {"file": (BytesIO(b"not a gzip file"), "bad.sql.gz")}
        r = client.post("/api/backup/import", data=data,
                        content_type="multipart/form-data")
        assert r.status_code == 400

    def test_import_valid_roundtrip(self, client):
        """Export → import roundtrip: import vráti ok=True."""
        from io import BytesIO
        export_r = client.get("/api/backup/export")
        assert export_r.status_code == 200
        gz_bytes = export_r.data
        data = {"file": (BytesIO(gz_bytes), "parcels_latest.sql.gz")}
        import_r = client.post("/api/backup/import", data=data,
                                content_type="multipart/form-data")
        assert import_r.status_code == 200
        result = import_r.get_json()
        assert result["ok"] is True
        assert "added_runs" in result
        assert "new_parcels" in result

    def test_import_rate_limit_429(self, client):
        """Druhý okamžitý import musí vrátiť 429 (rate-limit 10 s).
        Použijeme minimálny mock gzip SQL dump aby test bol rýchly
        a timestamp nastavíme tesne pred druhým requestom."""
        import gzip
        import time
        from io import BytesIO
        from routes.backup_routes import _IMPORT_RATE_LOCK_TS
        from services.backup_service import _validate_gz_sql

        # Minimálny valídny gzip SQL dump
        sql = b"BEGIN TRANSACTION;\nCREATE TABLE IF NOT EXISTS runs (id INTEGER);\nCOMMIT;\n"
        gz_bytes = gzip.compress(sql)

        # Prvý import — prejde (timestamp bol 0 z setup_method)
        r1 = client.post("/api/backup/import",
                         data={"file": (BytesIO(gz_bytes), "test.sql.gz")},
                         content_type="multipart/form-data")
        # Nastavíme timestamp na "práve teraz" aby rate-limit platil pre druhý request
        _IMPORT_RATE_LOCK_TS[0] = time.monotonic()
        # Druhý okamžite — musí byť 429
        r2 = client.post("/api/backup/import",
                         data={"file": (BytesIO(gz_bytes), "test.sql.gz")},
                         content_type="multipart/form-data")
        assert r2.status_code == 429


# ----------------------------------------------------------------
# TestFetchUrlEndpoint  —  POST /api/parcels/fetch-url
# ----------------------------------------------------------------

class TestFetchUrlEndpoint:
    MODULE_FETCH = "services.url_fetch_service.fetch_parcel_from_url"

    def test_missing_url_400(self, client):
        r = client.post("/api/parcels/fetch-url", json={})
        assert r.status_code == 400

    def test_empty_url_400(self, client):
        r = client.post("/api/parcels/fetch-url", json={"url": ""})
        assert r.status_code == 400
        assert r.get_json()["ok"] is False

    def test_unsupported_portal_400(self, client):
        """URL z nepodporovaného portálu vráti 400."""
        with patch(self.MODULE_FETCH,
                   side_effect=ValueError("Nepodporovany portal")):
            r = client.post("/api/parcels/fetch-url",
                            json={"url": "https://bazos.sk/1234"})
        assert r.status_code == 400
        assert r.get_json()["ok"] is False

    def test_network_error_502(self, client):
        """Sieťová chyba vráti 502."""
        import requests as _req
        with patch(self.MODULE_FETCH,
                   side_effect=_req.ConnectionError("timeout")):
            r = client.post("/api/parcels/fetch-url",
                            json={"url": "https://www.nehnutelnosti.sk/1"})
        assert r.status_code == 502
        assert r.get_json()["ok"] is False

    def test_success_returns_parcel(self, client):
        """Úspešný parse vráti ok=True a parcel dict."""
        mock_parcel = {
            "title": "Pozemok Senec",
            "price_eur": 45000.0,
            "area_sqm": 850.0,
            "location_text": "Senec",
            "source_portal": "nehnutelnosti_sk",
            "url": "https://www.nehnutelnosti.sk/test/",
            "price_per_sqm": 52.94,
            "parse_quality": "full",
        }
        with patch(self.MODULE_FETCH, return_value=mock_parcel):
            r = client.post("/api/parcels/fetch-url",
                            json={"url": "https://www.nehnutelnosti.sk/test/"})
        assert r.status_code == 200
        data = r.get_json()
        assert data["ok"] is True
        assert data["parcel"]["title"] == "Pozemok Senec"
        assert data["parcel"]["price_eur"] == 45000.0

    def test_success_parcel_has_expected_keys(self, client):
        mock_parcel = {
            "title": "Test", "price_eur": 10000.0, "area_sqm": 500.0,
            "location_text": "Pezinok", "source_portal": "topreality_sk",
            "url": "https://www.topreality.sk/test/",
            "price_per_sqm": 20.0, "parse_quality": "partial",
        }
        with patch(self.MODULE_FETCH, return_value=mock_parcel):
            r = client.post("/api/parcels/fetch-url",
                            json={"url": "https://www.topreality.sk/test/"})
        data = r.get_json()
        assert data["ok"] is True
        for key in ("title", "price_eur", "area_sqm", "location_text",
                    "source_portal", "url"):
            assert key in data["parcel"], f"Chýba kľúč v parcel: {key}"

    def test_parser_exception_500(self, client):
        """Neočakávaná chyba parsera vráti 500."""
        with patch(self.MODULE_FETCH,
                   side_effect=RuntimeError("unexpected parse error")):
            r = client.post("/api/parcels/fetch-url",
                            json={"url": "https://www.nehnutelnosti.sk/x/"})
        assert r.status_code == 500
        assert r.get_json()["ok"] is False
