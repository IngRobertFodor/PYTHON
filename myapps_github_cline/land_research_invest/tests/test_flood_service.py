"""
Testy - Sluzba zaplavovych uzemi
============================
Testuje kontrolu Q100 zaplavoveho uzemia.
HTTP requesty na SHMU WMS su mockované - 100% offline.
"""

import pytest
from unittest.mock import patch, MagicMock
from services.flood_service import check, _parse_flood_response
from models.result import ServiceResult


def _mock_wms_response(in_flood: bool, use_json: bool = True):
    m = MagicMock()
    m.status_code = 200
    m.raise_for_status = MagicMock()
    if use_json:
        m.headers = {"content-type": "application/json"}
        if in_flood:
            m.json.return_value = {
                "features": [{"type": "Feature", "properties": {"zona": "Q100"}}]
            }
        else:
            m.json.return_value = {"features": []}
    else:
        m.headers = {"content-type": "text/xml"}
        m.text = "q100 zaplavov feature data" if in_flood else "<empty/>"
        m.json.side_effect = Exception("not json")
    return m


class TestCheckFunction:
    """Testy hlavnej check() funkcie."""

    @patch("services.flood_service.requests.get")
    def test_returns_service_result(self, mock_get):
        mock_get.return_value = _mock_wms_response(False)
        result = check(48.2195, 17.3976)
        assert isinstance(result, ServiceResult)

    @patch("services.flood_service.requests.get")
    def test_not_in_flood_zone_score_100(self, mock_get):
        """Pozemok mimo zaplavy = score 100."""
        mock_get.return_value = _mock_wms_response(False)
        result = check(48.2195, 17.3976)
        assert result.ok is True
        assert result.score == 100.0
        assert result.data["in_flood_zone_q100"] is False

    @patch("services.flood_service.requests.get")
    def test_in_flood_zone_score_0(self, mock_get):
        """Pozemok v zaplavovej zone = score 0 (kriticky bloker)."""
        mock_get.return_value = _mock_wms_response(True)
        result = check(48.2195, 17.3976)
        assert result.ok is True
        assert result.score == 0.0
        assert result.data["in_flood_zone_q100"] is True

    @patch("services.flood_service.requests.get")
    def test_in_flood_risk_level_high(self, mock_get):
        mock_get.return_value = _mock_wms_response(True)
        result = check(48.2195, 17.3976)
        assert result.data["risk_level"] == "HIGH"

    @patch("services.flood_service.requests.get")
    def test_not_in_flood_risk_level_none(self, mock_get):
        mock_get.return_value = _mock_wms_response(False)
        result = check(48.2195, 17.3976)
        assert result.data["risk_level"] == "NONE"

    @patch("services.flood_service.requests.get")
    def test_data_contains_lat_lon(self, mock_get):
        mock_get.return_value = _mock_wms_response(False)
        result = check(48.2195, 17.3976)
        assert result.data["lat"] == 48.2195
        assert result.data["lon"] == 17.3976

    @patch("services.flood_service.requests.get")
    def test_source_is_set(self, mock_get):
        mock_get.return_value = _mock_wms_response(False)
        result = check(48.2195, 17.3976)
        assert result.source == "flood_service"

    @patch("services.flood_service.requests.get")
    def test_wms_error_returns_neutral_50(self, mock_get):
        """Pri chybe WMS nepotrestame pozemok - neutralne 50."""
        import requests as req
        mock_get.side_effect = req.RequestException("WMS down")
        result = check(48.2195, 17.3976)
        assert result.ok is False
        assert result.score == 50.0
        assert result.error is not None

    def test_feature_disabled_returns_skip(self):
        with patch("services.flood_service.is_feature_enabled", return_value=False):
            result = check(48.2195, 17.3976)
        assert result.data.get("skipped") is True


class TestParseFloodResponse:
    """Testy parsera WMS odpovede."""

    def test_json_with_features_is_flood(self):
        m = _mock_wms_response(True, use_json=True)
        assert _parse_flood_response(m) is True

    def test_json_without_features_is_not_flood(self):
        m = _mock_wms_response(False, use_json=True)
        assert _parse_flood_response(m) is False

    def test_text_with_flood_keyword_is_flood(self):
        m = _mock_wms_response(True, use_json=False)
        assert _parse_flood_response(m) is True

    def test_empty_xml_is_not_flood(self):
        m = MagicMock()
        m.headers = {"content-type": "text/xml"}
        m.text = "<empty/>"
        m.json.side_effect = Exception("not json")
        assert _parse_flood_response(m) is False
