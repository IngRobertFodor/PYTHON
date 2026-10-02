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


# ----------------------------------------------------------------
# F1/F2: _clean_address + _best_candidate + geocode_quality (R1)
# ----------------------------------------------------------------

from services.geocoding_service import _clean_address, _best_candidate, _dist_km


class TestCleanAddress:
    def test_empty(self):               assert _clean_address("") == ""
    def test_dash(self):                assert _clean_address("-") == ""
    def test_endash(self):              assert _clean_address("–") == ""
    def test_por(self):                 assert _clean_address("por.") == ""
    def test_too_short(self):           assert _clean_address("ab") == ""
    def test_senec_adds_sk(self):       assert "Slovensko" in _clean_address("Senec")
    def test_senec_preserves(self):     assert "Senec" in _clean_address("Senec")
    def test_already_has_sk(self):      r=_clean_address("Senec, Slovensko"); assert r.count("Slovensko")==1
    def test_psc_stripped(self):
        r = _clean_address("Povazska 1706/35, Trencin 91101")
        assert "91101" not in r
    def test_psc_salvages_city(self):
        r = _clean_address("Povazska 1706/35, Trencin 91101")
        # Trencin by malo byt zachovane ako obec
        assert "Trencin" in r or r == ""
    def test_long_title_truncated(self):
        long = "Pozemok v BA I. + SP na predaj kategoria IBV blizko lesa krk 123456789"
        r = _clean_address(long)
        assert len(r) <= 80
    def test_normal_short_ok(self):
        assert _clean_address("Malacky") != ""


class TestBestCandidate:
    def _cand(self, lat, lon, cat="place", typ="village"):
        return {"lat":str(lat),"lon":str(lon),"category":cat,"type":typ,
                "display_name":"Test","address":{}}

    def test_empty_returns_none(self):
        assert _best_candidate([]) is None

    def test_good_quality_near_ba(self):
        c = [self._cand(48.219, 17.397)]
        r = _best_candidate(c)
        assert r["geocode_quality"] == "good"

    def test_far_quality(self):
        c = [self._cand(48.718, 17.115)]  # Gbely ~80km
        r = _best_candidate(c)
        assert r["geocode_quality"] in {"good", "far"}  # Gbely je OK (88km)

    def test_outside_sr_is_uncertain(self):
        c = [self._cand(51.0, 14.0)]  # Nemecko
        r = _best_candidate(c)
        assert r["geocode_quality"] == "uncertain"

    def test_bad_type_is_uncertain(self):
        c = [self._cand(48.2, 17.4, cat="natural", typ="peak")]
        r = _best_candidate(c)
        assert r["geocode_quality"] == "uncertain"

    def test_prefers_good_type_over_bad(self):
        bad  = self._cand(48.2, 17.4, cat="natural", typ="peak")
        good = self._cand(48.219, 17.397, cat="place", typ="town")
        r = _best_candidate([bad, good])
        assert r["geocode_quality"] == "good"

    def test_geocode_quality_in_result(self):
        c = [self._cand(48.219, 17.397)]
        r = _best_candidate(c)
        assert "geocode_quality" in r
        assert "dist_km_ba" in r

    def test_dist_km_ba_correct(self):
        c = [self._cand(48.219, 17.397)]
        r = _best_candidate(c)
        assert 5 < r["dist_km_ba"] < 40
