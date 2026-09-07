"""
Unit Tests - BPEJ Service
===========================
Testuje bonitu pody, ochranné triedy, odvody a scoring.
HTTP requesty su mockované - 100% offline.
"""

import pytest
from unittest.mock import patch, MagicMock
from services.bpej_service import (
    check, estimate_odvody,
    _calculate_score, _parse_bpej_response,
    _clamp_class, _estimate_class_from_code,
    ODVODY_PER_CLASS,
)
from models.result import ServiceResult

BASE_LAT, BASE_LON = 48.2195, 17.3976
DEFAULT_CFG = {"max_protection_class": 6, "high_cost_classes": [1, 2, 3, 4]}


def mock_bpej_response(bpej_code: str, protection_class: int):
    m = MagicMock()
    m.status_code = 200
    m.raise_for_status = MagicMock()
    m.headers = {"content-type": "application/json"}
    m.json.return_value = {"features": [{"properties": {"BPEJ": bpej_code, "OT": protection_class}}]}
    return m


def mock_empty_response():
    m = MagicMock()
    m.status_code = 200
    m.raise_for_status = MagicMock()
    m.headers = {"content-type": "application/json"}
    m.json.return_value = {"features": []}
    m.text = "<empty/>"
    return m


class TestOdvodyPerClass:
    def test_class_1_highest(self):
        assert ODVODY_PER_CLASS[1] > ODVODY_PER_CLASS[4]

    def test_class_9_zero(self):
        assert ODVODY_PER_CLASS[9] == 0.0

    def test_rates_decrease(self):
        for c in range(1, 9):
            assert ODVODY_PER_CLASS[c] >= ODVODY_PER_CLASS[c + 1]

    def test_all_classes_defined(self):
        assert set(ODVODY_PER_CLASS.keys()) == {1, 2, 3, 4, 5, 6, 7, 8, 9}


class TestEstimateOdvody:
    def test_class_1_per_m2(self):
        assert estimate_odvody(1) == pytest.approx(15.0)

    def test_class_9_is_zero(self):
        assert estimate_odvody(9) == 0.0

    def test_area_multiplies_rate(self):
        assert estimate_odvody(5, 1000.0) == pytest.approx(estimate_odvody(5) * 1000.0)

    def test_returns_float(self):
        assert isinstance(estimate_odvody(3), float)


class TestClampClass:
    def test_valid_unchanged(self):
        for c in range(1, 10): assert _clamp_class(c) == c

    def test_below_1_clamps(self):
        assert _clamp_class(0) == 1

    def test_above_9_clamps(self):
        assert _clamp_class(10) == 9


class TestEstimateClassFromCode:
    def test_low_hpj_low_class(self):
        assert _estimate_class_from_code("01020") <= 3

    def test_high_hpj_high_class(self):
        assert _estimate_class_from_code("07520") >= 7

    def test_invalid_defaults_5(self):
        assert _estimate_class_from_code("X") == 5


class TestCalculateScore:
    def test_class_1_low(self):
        assert _calculate_score(1, DEFAULT_CFG) < 30.0

    def test_class_9_is_100(self):
        assert _calculate_score(9, DEFAULT_CFG) == pytest.approx(100.0)

    def test_class_5_above_50(self):
        assert _calculate_score(5, DEFAULT_CFG) >= 50.0

    def test_score_increases_with_class(self):
        scores = [_calculate_score(c, DEFAULT_CFG) for c in range(1, 10)]
        for i in range(len(scores) - 1):
            assert scores[i] <= scores[i + 1]

    def test_score_in_range_0_100(self):
        for c in range(1, 10):
            assert 0.0 <= _calculate_score(c, DEFAULT_CFG) <= 100.0


class TestParseBpejResponse:
    def test_extracts_bpej_code(self):
        code, _ = _parse_bpej_response(mock_bpej_response("07020", 5))
        assert code == "07020"

    def test_extracts_protection_class(self):
        _, pclass = _parse_bpej_response(mock_bpej_response("07020", 5))
        assert pclass == 5

    def test_empty_raises(self):
        with pytest.raises(RuntimeError):
            _parse_bpej_response(mock_empty_response())

    def test_clamps_invalid_class(self):
        _, pclass = _parse_bpej_response(mock_bpej_response("07020", 15))
        assert 1 <= pclass <= 9

    def test_fallback_code_estimation(self):
        """Ak OT chyba, odhadne triedu z kodu."""
        m = MagicMock()
        m.status_code = 200
        m.raise_for_status = MagicMock()
        m.headers = {"content-type": "application/json"}
        m.json.return_value = {"features": [{"properties": {"BPEJ": "07020"}}]}
        code, pclass = _parse_bpej_response(m)
        assert code == "07020" and 1 <= pclass <= 9


class TestCheckFunction:
    """Testy hlavnej check() funkcie."""

    @patch("services.bpej_service.requests.get")
    def test_returns_service_result(self, mock_get):
        mock_get.return_value = mock_bpej_response("07020", 5)
        assert isinstance(check(BASE_LAT, BASE_LON), ServiceResult)

    @patch("services.bpej_service.requests.get")
    def test_good_soil_high_score(self, mock_get):
        mock_get.return_value = mock_bpej_response("07520", 7)
        r = check(BASE_LAT, BASE_LON)
        assert r.ok is True and r.score >= 70.0

    @patch("services.bpej_service.requests.get")
    def test_class_1_low_score(self, mock_get):
        mock_get.return_value = mock_bpej_response("01010", 1)
        r = check(BASE_LAT, BASE_LON)
        assert r.ok is True and r.score < 30.0

    @patch("services.bpej_service.requests.get")
    def test_data_contains_bpej_code(self, mock_get):
        mock_get.return_value = mock_bpej_response("07020", 5)
        assert "bpej_code" in check(BASE_LAT, BASE_LON).data

    @patch("services.bpej_service.requests.get")
    def test_data_contains_protection_class(self, mock_get):
        mock_get.return_value = mock_bpej_response("07020", 5)
        assert "protection_class" in check(BASE_LAT, BASE_LON).data

    @patch("services.bpej_service.requests.get")
    def test_data_contains_odvody(self, mock_get):
        mock_get.return_value = mock_bpej_response("07020", 5)
        assert "estimated_odvody_eur_per_m2" in check(BASE_LAT, BASE_LON).data

    @patch("services.bpej_service.requests.get")
    def test_high_cost_warning_class_1(self, mock_get):
        mock_get.return_value = mock_bpej_response("01010", 1)
        assert check(BASE_LAT, BASE_LON).data["high_cost_warning"] is True

    @patch("services.bpej_service.requests.get")
    def test_no_high_cost_warning_class_7(self, mock_get):
        mock_get.return_value = mock_bpej_response("07520", 7)
        assert check(BASE_LAT, BASE_LON).data["high_cost_warning"] is False

    @patch("services.bpej_service.requests.get")
    def test_class_7_suitable_for_construction(self, mock_get):
        mock_get.return_value = mock_bpej_response("07520", 7)
        assert check(BASE_LAT, BASE_LON).data["suitable_for_construction"] is True

    @patch("services.bpej_service.requests.get")
    def test_class_3_not_suitable(self, mock_get):
        mock_get.return_value = mock_bpej_response("01030", 3)
        assert check(BASE_LAT, BASE_LON).data["suitable_for_construction"] is False

    @patch("services.bpej_service.requests.get")
    def test_source_is_set(self, mock_get):
        mock_get.return_value = mock_bpej_response("07020", 5)
        assert check(BASE_LAT, BASE_LON).source == "bpej_service"

    @patch("services.bpej_service.requests.get")
    def test_wms_error_returns_neutral_50(self, mock_get):
        import requests as req
        mock_get.side_effect = req.RequestException("WMS down")
        r = check(BASE_LAT, BASE_LON)
        assert r.ok is False and r.score == 50.0

    def test_feature_disabled_returns_skip(self):
        with patch("services.bpej_service.is_feature_enabled", return_value=False):
            r = check(BASE_LAT, BASE_LON)
        assert r.data.get("skipped") is True and r.score == 50.0

