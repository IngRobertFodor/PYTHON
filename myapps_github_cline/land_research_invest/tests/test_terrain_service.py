"""
Testy - Sluzba terenu
==============================
Testuje analyzu terenu: sklon, orientacia, vyska, zosuvy, radon.
HTTP requesty su mockované - 100% offline.
"""

import pytest
from unittest.mock import patch, MagicMock
from services.terrain_service import (
    check, get_elevation, get_slope_and_aspect,
    is_landslide_zone, get_radon_risk,
    _calculate_score, _parse_elevation_response,
    _parse_feature_response, _parse_radon_response,
    _deg_to_aspect,
)
from models.result import ServiceResult


BASE_LAT, BASE_LON = 48.2195, 17.3976

# --- Pomocne funkcie ---

def mock_elevation_response(value: float):
    m = MagicMock()
    m.status_code = 200
    m.raise_for_status = MagicMock()
    m.headers = {"content-type": "application/json"}
    m.json.return_value = {
        "features": [{"properties": {"value": value}}]
    }
    return m


def mock_feature_response(has_feature: bool):
    m = MagicMock()
    m.status_code = 200
    m.raise_for_status = MagicMock()
    m.headers = {"content-type": "application/json"}
    m.json.return_value = {
        "features": [{"type": "Feature"}] if has_feature else []
    }
    return m


def mock_radon_response(risk_class: int):
    labels = {1: "nizke", 2: "stredne", 3: "vysoke"}
    m = MagicMock()
    m.status_code = 200
    m.raise_for_status = MagicMock()
    m.headers = {"content-type": "application/json"}
    m.json.return_value = {
        "features": [{"properties": {"class": risk_class}}]
    }
    return m


DEFAULT_CFG = {
    "max_slope_percent": 15,
    "preferred_slope_percent": 5,
    "preferred_aspects": ["S", "SE", "SW"],
    "max_elevation_m": 400,
    "max_radon_risk_class": 2,
}

class TestDegToAspect:
    """Testy konverzie stupnov na orientaciu svahu."""

    def test_north_0(self):     assert _deg_to_aspect(0.0)   == "N"
    def test_north_360(self):   assert _deg_to_aspect(359.0) == "N"
    def test_south_180(self):   assert _deg_to_aspect(180.0) == "S"
    def test_east_90(self):     assert _deg_to_aspect(90.0)  == "E"
    def test_west_270(self):    assert _deg_to_aspect(270.0) == "W"
    def test_se_135(self):      assert _deg_to_aspect(135.0) == "SE"
    def test_sw_225(self):      assert _deg_to_aspect(225.0) == "SW"
    def test_ne_45(self):       assert _deg_to_aspect(45.0)  == "NE"
    def test_nw_315(self):      assert _deg_to_aspect(315.0) == "NW"


class TestParseElevationResponse:
    """Testy parsera WMS odpovede pre nadmorsku vysku."""

    def test_json_features_value(self):
        m = mock_elevation_response(250.5)
        assert _parse_elevation_response(m) == pytest.approx(250.5)

    def test_json_gray_index_key(self):
        m = MagicMock()
        m.headers = {"content-type": "application/json"}
        m.json.return_value = {"features": [{"properties": {"GRAY_INDEX": 310.0}}]}
        assert _parse_elevation_response(m) == pytest.approx(310.0)

    def test_text_fallback(self):
        m = MagicMock()
        m.headers = {"content-type": "text/plain"}
        m.json.side_effect = Exception("not json")
        m.text = "elevation = 185.3"
        assert _parse_elevation_response(m) == pytest.approx(185.3)

    def test_raises_when_unparseable(self):
        m = MagicMock()
        m.headers = {"content-type": "text/plain"}
        m.json.side_effect = Exception("not json")
        m.text = "<empty/>"
        with pytest.raises(RuntimeError):
            _parse_elevation_response(m)


class TestParseFeatureResponse:
    """Testy parsera WMS feature (zosuvy)."""

    def test_json_with_features_is_true(self):
        assert _parse_feature_response(mock_feature_response(True)) is True

    def test_json_without_features_is_false(self):
        assert _parse_feature_response(mock_feature_response(False)) is False

    def test_text_with_landslide_keyword_is_true(self):
        m = MagicMock()
        m.headers = {"content-type": "text/xml"}
        m.json.side_effect = Exception()
        m.text = "zosuv feature detected"
        assert _parse_feature_response(m) is True

    def test_empty_text_is_false(self):
        m = MagicMock()
        m.headers = {"content-type": "text/xml"}
        m.json.side_effect = Exception()
        m.text = "<empty/>"
        assert _parse_feature_response(m) is False


class TestParseRadonResponse:
    """Testy parsera radonovej triedy."""

    def test_class_1_from_json(self):
        assert _parse_radon_response(mock_radon_response(1)) == 1

    def test_class_2_from_json(self):
        assert _parse_radon_response(mock_radon_response(2)) == 2

    def test_class_3_from_json(self):
        assert _parse_radon_response(mock_radon_response(3)) == 3

    def test_text_vysoke_returns_3(self):
        m = MagicMock()
        m.headers = {"content-type": "text/plain"}
        m.json.side_effect = Exception()
        m.text = "radon risk: vysoke"
        assert _parse_radon_response(m) == 3

    def test_unknown_defaults_to_1(self):
        m = MagicMock()
        m.headers = {"content-type": "text/plain"}
        m.json.side_effect = Exception()
        m.text = "<empty/>"
        assert _parse_radon_response(m) == 1



class TestCalculateScore:
    """Testy scoring algoritmu terenu."""

    def test_landslide_is_critical_blocker(self):
        assert _calculate_score(200.0, 3.0, "S", True, 1, DEFAULT_CFG) == 0.0

    def test_ideal_terrain_gives_100(self):
        assert _calculate_score(150.0, 2.0, "S", False, 1, DEFAULT_CFG) == 100.0

    def test_steep_slope_reduces_by_40(self):
        """Svah >15% = -40 bodov."""
        steep = _calculate_score(150.0, 20.0, "S", False, 1, DEFAULT_CFG)
        assert steep == pytest.approx(60.0)

    def test_moderate_slope_partial_penalty(self):
        moderate = _calculate_score(150.0, 10.0, "S", False, 1, DEFAULT_CFG)
        assert 60.0 < moderate < 100.0

    def test_north_aspect_minus_20(self):
        s = _calculate_score(150.0, 2.0, "S", False, 1, DEFAULT_CFG)
        n = _calculate_score(150.0, 2.0, "N", False, 1, DEFAULT_CFG)
        assert n == pytest.approx(s - 20.0)

    def test_east_aspect_minus_10(self):
        s = _calculate_score(150.0, 2.0, "S", False, 1, DEFAULT_CFG)
        e = _calculate_score(150.0, 2.0, "E", False, 1, DEFAULT_CFG)
        assert e == pytest.approx(s - 10.0)

    def test_high_elevation_reduces_score(self):
        ok = _calculate_score(300.0, 2.0, "S", False, 1, DEFAULT_CFG)
        hi = _calculate_score(500.0, 2.0, "S", False, 1, DEFAULT_CFG)
        assert hi < ok

    def test_high_radon_minus_20(self):
        r1 = _calculate_score(150.0, 2.0, "S", False, 1, DEFAULT_CFG)
        r3 = _calculate_score(150.0, 2.0, "S", False, 3, DEFAULT_CFG)
        assert r3 == pytest.approx(r1 - 20.0)

    def test_medium_radon_minus_5(self):
        r1 = _calculate_score(150.0, 2.0, "S", False, 1, DEFAULT_CFG)
        r2 = _calculate_score(150.0, 2.0, "S", False, 2, DEFAULT_CFG)
        assert r2 == pytest.approx(r1 - 5.0)

    def test_score_never_below_0(self):
        assert _calculate_score(700.0, 30.0, "N", False, 3, DEFAULT_CFG) >= 0.0

    def test_score_never_above_100(self):
        assert _calculate_score(50.0, 0.0, "S", False, 1, DEFAULT_CFG) <= 100.0

    def test_none_values_no_crash(self):
        score = _calculate_score(None, None, None, None, None, DEFAULT_CFG)
        assert 0.0 <= score <= 100.0



class TestCheckFunction:
    """Testy hlavnej check() funkcie - jednotny kontrakt."""

    def _side_effect(self, elevation=200.0, landslide=False, radon=1):
        """Mock side_effect pre requests.get - rozlisuje podla LAYERS param."""
        def _effect(url, **kwargs):
            layer = kwargs.get("params", {}).get("LAYERS", "")
            if "radon" in layer:
                return mock_radon_response(radon)
            if "zosuv" in layer:
                return mock_feature_response(landslide)
            return mock_elevation_response(elevation)
        return _effect

    @patch("services.terrain_service.requests.get")
    def test_returns_service_result(self, mock_get):
        mock_get.side_effect = self._side_effect()
        assert isinstance(check(BASE_LAT, BASE_LON), ServiceResult)

    @patch("services.terrain_service.requests.get")
    def test_ideal_high_score(self, mock_get):
        mock_get.side_effect = self._side_effect(200.0, False, 1)
        r = check(BASE_LAT, BASE_LON)
        assert r.ok is True and r.score >= 90.0

    @patch("services.terrain_service.requests.get")
    def test_landslide_gives_score_0(self, mock_get):
        mock_get.side_effect = self._side_effect(200.0, True, 1)
        r = check(BASE_LAT, BASE_LON)
        assert r.ok is True and r.score == 0.0

    @patch("services.terrain_service.requests.get")
    def test_data_contains_elevation(self, mock_get):
        mock_get.side_effect = self._side_effect(180.0)
        assert "elevation_m" in check(BASE_LAT, BASE_LON).data

    @patch("services.terrain_service.requests.get")
    def test_data_contains_slope_and_aspect(self, mock_get):
        mock_get.side_effect = self._side_effect()
        r = check(BASE_LAT, BASE_LON)
        assert "slope_percent" in r.data and "aspect" in r.data

    @patch("services.terrain_service.requests.get")
    def test_data_contains_landslide_flag(self, mock_get):
        mock_get.side_effect = self._side_effect()
        assert "in_landslide_zone" in check(BASE_LAT, BASE_LON).data

    @patch("services.terrain_service.requests.get")
    def test_data_contains_radon_class(self, mock_get):
        mock_get.side_effect = self._side_effect()
        assert "radon_risk_class" in check(BASE_LAT, BASE_LON).data

    @patch("services.terrain_service.requests.get")
    def test_source_is_set(self, mock_get):
        mock_get.side_effect = self._side_effect()
        assert check(BASE_LAT, BASE_LON).source == "terrain_service"

    @patch("services.terrain_service.requests.get")
    def test_wms_error_returns_neutral_50(self, mock_get):
        import requests as req
        mock_get.side_effect = req.RequestException("WMS down")
        r = check(BASE_LAT, BASE_LON)
        assert r.ok is False and r.score == 50.0

    def test_feature_disabled_returns_skip(self):
        with patch("services.terrain_service.is_feature_enabled", return_value=False):
            r = check(BASE_LAT, BASE_LON)
        assert r.data.get("skipped") is True and r.score == 50.0

