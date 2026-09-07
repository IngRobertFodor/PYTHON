"""
Testy - Geokodovacia sluzba
================================
Testuje prevod adresy na GPS suradnice.
HTTP requesty su mockované - 100% offline.
"""

import pytest
from unittest.mock import patch, MagicMock
from services.geocoding_service import geocode, geocode_parcel_number, check
from models.result import ServiceResult

SAMPLE_NOMINATIM = [{
    "lat": "48.2195",
    "lon": "17.3976",
    "display_name": "Senec, Senec District, Slovakia",
    "type": "city",
    "address": {
        "city": "Senec",
        "country": "Slovakia",
        "country_code": "sk",
    }
}]


def _mock_response(data, status=200):
    m = MagicMock()
    m.status_code = status
    m.json.return_value = data
    m.raise_for_status = MagicMock()
    return m


class TestGeocode:
    """Testy funkcie geocode() - adresa na GPS."""

    @patch("services.geocoding_service.requests.get")
    def test_returns_lat_lon(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_NOMINATIM)
        result = geocode("Senec")
        assert result is not None
        assert result["lat"] == pytest.approx(48.2195, abs=0.001)
        assert result["lon"] == pytest.approx(17.3976, abs=0.001)

    @patch("services.geocoding_service.requests.get")
    def test_returns_display_name(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_NOMINATIM)
        result = geocode("Senec")
        assert "display_name" in result

    @patch("services.geocoding_service.requests.get")
    def test_empty_response_returns_none(self, mock_get):
        mock_get.return_value = _mock_response([])
        result = geocode("nonexistentplace99999")
        assert result is None

    @patch("services.geocoding_service.requests.get")
    def test_network_error_raises(self, mock_get):
        import requests as req
        mock_get.side_effect = req.RequestException("timeout")
        with pytest.raises(req.RequestException):
            geocode("Senec")

    @patch("services.geocoding_service.requests.get")
    def test_lat_lon_are_floats(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_NOMINATIM)
        result = geocode("Senec")
        assert isinstance(result["lat"], float)
        assert isinstance(result["lon"], float)

    @patch("services.geocoding_service.requests.get")
    def test_uses_correct_user_agent(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_NOMINATIM)
        geocode("Senec")
        call_kwargs = mock_get.call_args
        headers = call_kwargs[1].get("headers", {}) or call_kwargs.kwargs.get("headers", {})
        assert "User-Agent" in headers
        assert "LandResearchInvest" in headers["User-Agent"]


class TestGeocodeParcelNumber:
    """Testy fallback geocodingu podla cisla parcely + obec."""

    @patch("services.geocoding_service.requests.get")
    def test_falls_back_to_municipality(self, mock_get):
        """Ak parcelne cislo nenajde, skusi len obec."""
        mock_get.side_effect = [
            _mock_response([]),                  # prvy pokus - parcela nenajdena
            _mock_response(SAMPLE_NOMINATIM),    # druhy pokus - len obec
        ]
        result = geocode_parcel_number("9999/99", "Senec")
        assert result is not None
        assert result["lat"] == pytest.approx(48.2195, abs=0.001)

    @patch("services.geocoding_service.requests.get")
    def test_returns_none_if_both_fail(self, mock_get):
        mock_get.return_value = _mock_response([])
        result = geocode_parcel_number("9999/99", "nonexistent")
        assert result is None


class TestCheckFunction:
    """Testy hlavnej check() funkcie - jednotny kontrakt."""

    @patch("services.geocoding_service.requests.get")
    def test_returns_service_result(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_NOMINATIM)
        result = check("Senec")
        assert isinstance(result, ServiceResult)

    @patch("services.geocoding_service.requests.get")
    def test_ok_true_on_found(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_NOMINATIM)
        result = check("Senec")
        assert result.ok is True
        assert result.score == 100.0

    @patch("services.geocoding_service.requests.get")
    def test_ok_false_on_not_found(self, mock_get):
        mock_get.return_value = _mock_response([])
        result = check("nonexistentplace99999")
        assert result.ok is False
        assert result.score == 0.0

    @patch("services.geocoding_service.requests.get")
    def test_data_contains_lat_lon(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_NOMINATIM)
        result = check("Senec")
        assert "lat" in result.data
        assert "lon" in result.data

    @patch("services.geocoding_service.requests.get")
    def test_source_is_set(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_NOMINATIM)
        result = check("Senec")
        assert result.source == "geocoding_service"

    def test_feature_disabled_returns_skip(self):
        with patch("services.geocoding_service.is_feature_enabled", return_value=False):
            result = check("Senec")
        assert result.data.get("skipped") is True

    @patch("services.geocoding_service.requests.get")
    def test_network_error_returns_error_result(self, mock_get):
        import requests as req
        mock_get.side_effect = req.RequestException("timeout")
        result = check("Senec")
        assert result.ok is False
        assert result.error is not None
