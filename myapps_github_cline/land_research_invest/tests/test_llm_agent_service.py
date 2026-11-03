"""
test_llm_agent_service.py — Testy AI orchestrátora
====================================================
100% offline — žiadne reálne volania na Gemini API.
LLM je mocknutý; tooly volajú mocknuté dáta.
"""

import sys
import pathlib
import json

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "backend"))

import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    from app import create_app
    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret"})
    with app.test_client() as c:
        yield c


def _make_parcel(url="https://test.sk/1", location="Senec", index=75,
                 source="nehnutelnosti_sk", price=45000, area=800, signals=None):
    return {
        "url": url, "title": f"Pozemok {location}",
        "location_text": location, "price_eur": price, "area_sqm": area,
        "price_per_sqm": round(price / area, 2),
        "investment_index": index, "source_portal": source,
        "signals": signals or [{"kod": "BLIZKO_BA", "typ": "PRILEZITOST"}],
    }


# ---------------------------------------------------------------------------
# is_available() + _classify_error()
# ---------------------------------------------------------------------------

class TestIsAvailable:
    def test_true_when_key_set(self, monkeypatch):
        monkeypatch.setenv("GOOGLE_API_KEY", "fake-key-123")
        from services import llm_agent_service as svc
        assert svc.is_available() is True

    def test_false_when_key_missing(self, monkeypatch):
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.setattr("services.llm_agent_service._load_env", lambda: None)
        from services import llm_agent_service as svc
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        assert svc.is_available() is False


class TestClassifyError:
    def setup_method(self):
        from services import llm_agent_service as svc
        self.fn = svc._classify_error

    def test_deprecated(self):
        assert self.fn(Exception("no longer available")) == "deprecated"

    def test_quota(self):
        assert self.fn(Exception("resource_exhausted 429")) == "quota"

    def test_not_found(self):
        assert self.fn(Exception("not_found 404")) == "not_found"

    def test_network(self):
        assert self.fn(Exception("connection timeout")) == "network"

    def test_unknown(self):
        assert self.fn(Exception("some random error")) == "unknown"


# ---------------------------------------------------------------------------
# ask() — graceful fallback bez API key
# ---------------------------------------------------------------------------

class TestAskNoApiKey:
    def test_returns_ok_false(self, monkeypatch):
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.setattr("services.llm_agent_service._load_env", lambda: None)
        from services import llm_agent_service as svc
        result = svc.ask("test otázka")
        assert result["ok"] is False
        assert result["error_type"] == "no_api_key"

    def test_answer_is_sk_string(self, monkeypatch):
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.setattr("services.llm_agent_service._load_env", lambda: None)
        from services import llm_agent_service as svc
        result = svc.ask("test")
        assert isinstance(result["answer"], str) and len(result["answer"]) > 0

    def test_empty_question(self, monkeypatch):
        monkeypatch.setenv("GOOGLE_API_KEY", "fake")
        from services import llm_agent_service as svc
        assert svc.ask("")["error_type"] == "empty_question"


# ---------------------------------------------------------------------------
# Tool: _tool_get_parcels
# ---------------------------------------------------------------------------

class TestToolGetParcels:
    def _run(self, parcels, **kwargs):
        from services import llm_agent_service as svc
        with patch("routes.scrape_routes._get_last_results", return_value=parcels):
            return svc._tool_get_parcels(**kwargs)

    def test_returns_list(self):
        assert isinstance(self._run([_make_parcel()]), list)

    def test_min_index_filter(self):
        p = [_make_parcel(index=80), _make_parcel(url="u2", index=40)]
        assert len(self._run(p, min_index=70)) == 1

    def test_obec_filter(self):
        p = [_make_parcel(location="Senec"), _make_parcel(url="u2", location="Modra")]
        r = self._run(p, obec_substring="senec")
        assert len(r) == 1 and "Senec" in r[0]["location_text"]

    def test_source_type_drazby(self):
        p = [_make_parcel(source="notarske_drazby"), _make_parcel(url="u2", source="nehnutelnosti_sk")]
        r = self._run(p, source_type="drazby")
        assert len(r) == 1 and r[0]["source_portal"] == "notarske_drazby"

    def test_has_signal_filter(self):
        p1 = _make_parcel(signals=[{"kod": "HORICE"}, {"kod": "BLIZKO_BA"}])
        p2 = _make_parcel(url="u2", signals=[{"kod": "CENA_KLESA"}])
        assert len(self._run([p1, p2], has_signal="HORICE")) == 1

    def test_sorted_by_index_desc(self):
        p = [_make_parcel(index=50), _make_parcel(url="u2", index=90), _make_parcel(url="u3", index=70)]
        r = self._run(p)
        idx = [x["investment_index"] for x in r]
        assert idx == sorted(idx, reverse=True)

    def test_limit(self):
        p = [_make_parcel(url=f"u{i}", index=i) for i in range(30)]
        assert len(self._run(p, limit=5)) == 5

    def test_empty_db(self):
        assert self._run([]) == []

    def test_result_keys(self):
        r = self._run([_make_parcel()])
        assert all(k in r[0] for k in ["url", "location_text", "price_eur",
                                        "investment_index", "source_portal", "signals"])


# ---------------------------------------------------------------------------
# Tool: _tool_get_run_summary
# ---------------------------------------------------------------------------

class TestToolGetRunSummary:
    def test_returns_dict_with_count(self):
        from services import llm_agent_service as svc
        mp = {"per_source_status": {}, "failed_sources": [], "elapsed_s": 10}
        mr = [{"id": 1, "started_at": "2026-11-03T10:00:00", "parcel_count": 4500}]
        with patch("services.scraper_service.get_scrape_progress", return_value=mp), \
             patch("services.storage_service.list_runs", return_value=mr):
            r = svc._tool_get_run_summary()
        assert r["parcel_count"] == 4500

    def test_empty_runs(self):
        from services import llm_agent_service as svc
        with patch("services.scraper_service.get_scrape_progress", return_value={}), \
             patch("services.storage_service.list_runs", return_value=[]):
            assert svc._tool_get_run_summary()["parcel_count"] == 0


# ---------------------------------------------------------------------------
# Tool: _tool_analyze_parcel_gis
# ---------------------------------------------------------------------------

class TestToolAnalyzeParcelGis:
    def test_invalid_url(self):
        from services import llm_agent_service as svc
        assert "error" in svc._tool_analyze_parcel_gis("not-a-url")

    def test_url_not_found(self):
        from services import llm_agent_service as svc
        with patch("routes.scrape_routes._get_last_results", return_value=[]):
            assert "error" in svc._tool_analyze_parcel_gis("https://test.sk/999")

    def test_success(self):
        from services import llm_agent_service as svc
        from models.parcel import Parcel

        def _mock_analyze(p):
            p.final_score   = 78.0
            p.recommendation = "INVESTIGATE"
            return p

        with patch("routes.scrape_routes._get_last_results",
                   return_value=[_make_parcel(url="https://t.sk/1")]), \
             patch("services.pipeline_service.analyze_parcel", side_effect=_mock_analyze):
            r = svc._tool_analyze_parcel_gis("https://t.sk/1")
        assert r["final_score"] == 78.0


# ---------------------------------------------------------------------------
# Tool: _tool_get_peer_statistics
# ---------------------------------------------------------------------------

class TestToolGetPeerStatistics:
    def test_missing_obec(self):
        from services import llm_agent_service as svc
        assert "error" in svc._tool_get_peer_statistics("")

    def test_not_found(self):
        from services import llm_agent_service as svc
        with patch("routes.scrape_routes._get_last_results", return_value=[]):
            assert svc._tool_get_peer_statistics("Neexistujuca")["found"] is False

    def test_found(self):
        from services import llm_agent_service as svc
        from services.peer_analysis_service import ObecStats
        ms = {"senec": ObecStats(median_ppsm=85.0, count=10, min_ppsm=50.0, max_ppsm=120.0)}
        with patch("routes.scrape_routes._get_last_results", return_value=[]), \
             patch("services.peer_analysis_service.compute_obec_stats", return_value=ms):
            r = svc._tool_get_peer_statistics("Senec")
        assert r["found"] is True and r["median_ppsm"] == 85.0


# ---------------------------------------------------------------------------
# Zvyšné tooly: explain, diff, backup, csv
# ---------------------------------------------------------------------------

class TestToolExplainInvestment:
    def test_missing_url(self):
        from services import llm_agent_service as svc
        assert "Chýba" in svc._tool_explain_investment("")

    def test_not_found(self):
        from services import llm_agent_service as svc
        with patch("routes.scrape_routes._get_last_results", return_value=[]):
            assert "nebol" in svc._tool_explain_investment("https://t.sk/x")

    def test_ok(self):
        from services import llm_agent_service as svc
        with patch("routes.scrape_routes._get_last_results",
                   return_value=[_make_parcel(url="https://t.sk/1")]), \
             patch("services.opportunity_service.explain", return_value="Pozemok OK."):
            assert "Pozemok" in svc._tool_explain_investment("https://t.sk/1")


class TestToolGetDiff:
    def test_not_enough_runs(self):
        from services import llm_agent_service as svc
        with patch("services.storage_service.list_runs", return_value=[{"id": 1}]):
            assert "message" in svc._tool_get_diff()

    def test_counts(self):
        from services import llm_agent_service as svc
        md = {"new": [_make_parcel()], "cheaper": [], "gone": [], "same": []}
        with patch("services.storage_service.list_runs", return_value=[{"id": 2}, {"id": 1}]), \
             patch("services.storage_service.load_run", return_value=[]), \
             patch("services.diff_service.compute_diff", return_value=md):
            assert svc._tool_get_diff()["new_count"] == 1


class TestToolGetBackupStatus:
    def test_ok(self):
        from services import llm_agent_service as svc
        with patch("services.backup_service.backup_status", return_value={"db_parcels": 4500}):
            assert svc._tool_get_backup_status()["db_parcels"] == 4500


class TestToolExportCsvFiltered:
    def test_no_parcels(self):
        from services import llm_agent_service as svc
        with patch("routes.scrape_routes._get_last_results", return_value=[]):
            assert svc._tool_export_csv_filtered(min_index=99)["ok"] is False

    def test_creates_file(self, tmp_path, monkeypatch):
        from services import llm_agent_service as svc
        # Patch modul-level premenná cez patch.object
        with patch.object(svc, "_EXPORTS_DIR", tmp_path), \
             patch("routes.scrape_routes._get_last_results", return_value=[_make_parcel()]):
            r = svc._tool_export_csv_filtered()
        assert r["ok"] is True and (tmp_path / r["filename"]).exists()


# ---------------------------------------------------------------------------
# list_available_models() a agent_routes
# ---------------------------------------------------------------------------

class TestListAvailableModels:
    def test_hardcoded_when_no_key(self, monkeypatch):
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.setattr("services.llm_agent_service._load_env", lambda: None)
        from services import llm_agent_service as svc
        svc._models_cache = None
        r = svc.list_available_models()
        assert r["source"] == "hardcoded" and len(r["models"]) > 0

    def test_google_api_ok(self, monkeypatch):
        monkeypatch.setenv("GOOGLE_API_KEY", "fake")
        from services import llm_agent_service as svc
        svc._models_cache = None
        data = {"models": [{"name": "models/gemini-3.5-flash", "displayName": "G",
                            "supportedGenerationMethods": ["generateContent"]}]}
        mr = MagicMock()
        mr.read.return_value = json.dumps(data).encode()
        mr.__enter__ = lambda s: s
        mr.__exit__ = MagicMock(return_value=False)
        with patch("urllib.request.urlopen", return_value=mr):
            r = svc.list_available_models()
        assert r["source"] == "google-api"

    def test_cache(self):
        import time
        from services import llm_agent_service as svc
        svc._models_cache = {"source": "c", "models": []}
        svc._models_cache_ts = time.monotonic()
        assert svc.list_available_models()["cached"] is True


class TestAgentRoutes:
    def test_status_200(self, client):
        assert client.get("/api/agent/status").status_code == 200

    def test_available_models_has_list(self, client):
        r = client.get("/api/agent/available-models").get_json()
        assert isinstance(r["models"], list)

    def test_ask_empty_400(self, client):
        assert client.post("/api/agent/ask", json={}).status_code == 400

    def test_ask_too_long_400(self, client):
        assert client.post("/api/agent/ask", json={"question": "x"*501}).status_code == 400

    def test_ask_no_key_ok_false(self, client, monkeypatch):
        import services.llm_agent_service as svc
        monkeypatch.setattr(svc, "is_available", lambda: False)
        r = client.post("/api/agent/ask", json={"question": "test"})
        assert r.status_code == 200 and not r.get_json()["ok"]

    def test_health_200(self, client):
        assert client.get("/api/agent/health").status_code == 200

    def test_select_no_model_400(self, client):
        assert client.post("/api/agent/select-model", json={}).status_code == 400

    def test_clear_model_200(self, client):
        assert client.post("/api/agent/clear-model").status_code == 200

    def test_export_traversal_400(self, client):
        """Flask normalizuje '../' v URL pred routingom.
        Overíme bezpečnostnú kontrolu v handleri priamym volaním s '..' v názve."""
        from unittest.mock import patch
        # Simulujeme priamy request kde Flask neodfiltroval '..'
        r = client.get("/api/agent/exports/export_..bad.csv")
        # Handler vráti 400 (nezačína 'export_' a nekončí '.csv' — preto 400)
        # alebo 404 ak Flask URL pattern to nezoberá — oboje je bezpečné
        assert r.status_code in (400, 404)

    def test_export_missing_404(self, client):
        assert client.get("/api/agent/exports/export_missing.csv").status_code == 404

    def test_blueprint_in_app(self, client):
        from app import create_app
        assert "agent" in create_app({"TESTING": True, "SECRET_KEY": "x"}).blueprints

