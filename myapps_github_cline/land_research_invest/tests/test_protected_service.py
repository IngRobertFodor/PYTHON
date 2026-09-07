"""
Unit Tests - Protected Service
================================
Testuje kontrolu ochrannych pasiem (Natura 2000, CHKO, NPR, NP).
HTTP requesty su mockované - 100% offline.
"""

import pytest
from unittest.mock import patch, MagicMock
from services.protected_service import (
    check, _query_all_layers, _calculate_score,
    _parse_protected_response, WMS_LAYERS,
)
from models.result import ServiceResult

BASE_LAT, BASE_LON = 48.2195, 17.3976


def mock_wms(has_feature: bool):
    m = MagicMock()
    m.status_code = 200
    m.raise_for_status = MagicMock()
    m.headers = {"content-type": "application/json"}
    m.json.return_value = {"features": [{"type": "Feature"}] if has_feature else []}
    return m


def no_protection():
    return {k: False for k in WMS_LAYERS}


class TestWmsLayers:
    def test_six_layers_defined(self):      assert len(WMS_LAYERS) == 6
    def test_natura2000_hab_present(self):  assert "natura2000_hab" in WMS_LAYERS
    def test_natura2000_birds_present(self):assert "natura2000_birds" in WMS_LAYERS
    def test_chko_present(self):            assert "chko" in WMS_LAYERS
    def test_npr_present(self):             assert "npr" in WMS_LAYERS
    def test_np_present(self):              assert "np" in WMS_LAYERS


class TestParseProtectedResponse:
    def test_json_with_features_true(self):
        assert _parse_protected_response(mock_wms(True)) is True

    def test_json_without_features_false(self):
        assert _parse_protected_response(mock_wms(False)) is False

    def test_text_natura_keyword_true(self):
        m = MagicMock()
        m.headers = {"content-type": "text/xml"}
        m.json.side_effect = Exception()
        m.text = "natura zona found"
        assert _parse_protected_response(m) is True

    def test_empty_text_false(self):
        m = MagicMock()
        m.headers = {"content-type": "text/xml"}
        m.json.side_effect = Exception()
        m.text = "<empty/>"
        assert _parse_protected_response(m) is False


class TestCalculateScore:
    def test_no_protection_gives_100(self):
        assert _calculate_score(no_protection()) == 100.0

    def test_np_gives_0(self):
        f = no_protection(); f["np"] = True
        assert _calculate_score(f) == 0.0

    def test_npr_gives_0(self):
        f = no_protection(); f["npr"] = True
        assert _calculate_score(f) == 0.0

    def test_pr_gives_0(self):
        f = no_protection(); f["pr"] = True
        assert _calculate_score(f) == 0.0

    def test_chko_gives_20(self):
        f = no_protection(); f["chko"] = True
        assert _calculate_score(f) == pytest.approx(20.0)

    def test_natura2000_reduces_score(self):
        f = no_protection(); f["natura2000_hab"] = True
        assert _calculate_score(f) < 100.0

    def test_chko_plus_natura_below_20(self):
        f = no_protection(); f["chko"] = True; f["natura2000_hab"] = True
        assert _calculate_score(f) < 20.0

    def test_np_overrides_chko(self):
        f = no_protection(); f["np"] = True; f["chko"] = True
        assert _calculate_score(f) == 0.0

    def test_score_in_range_0_100(self):
        for key in WMS_LAYERS:
            f = no_protection(); f[key] = True
            assert 0.0 <= _calculate_score(f) <= 100.0


class TestQueryAllLayers:
    @patch("services.protected_service.requests.get")
    def test_returns_all_keys(self, mock_get):
        mock_get.return_value = mock_wms(False)
        findings = _query_all_layers(BASE_LAT, BASE_LON)
        assert set(findings.keys()) == set(WMS_LAYERS.keys())

    @patch("services.protected_service.requests.get")
    def test_all_false_when_no_features(self, mock_get):
        mock_get.return_value = mock_wms(False)
        assert not any(_query_all_layers(BASE_LAT, BASE_LON).values())

    @patch("services.protected_service.requests.get")
    def test_layer_error_gives_false_not_crash(self, mock_get):
        """Chyba jednej vrstvy neplati cely dotaz."""
        import requests as req
        mock_get.side_effect = req.RequestException("timeout")
        findings = _query_all_layers(BASE_LAT, BASE_LON)
        assert set(findings.keys()) == set(WMS_LAYERS.keys())
        assert not any(findings.values())


class TestCheckFunction:
    @patch("services.protected_service.requests.get")
    def test_returns_service_result(self, mock_get):
        mock_get.return_value = mock_wms(False)
        assert isinstance(check(BASE_LAT, BASE_LON), ServiceResult)

    @patch("services.protected_service.requests.get")
    def test_no_protection_score_100(self, mock_get):
        mock_get.return_value = mock_wms(False)
        r = check(BASE_LAT, BASE_LON)
        assert r.ok is True and r.score == 100.0

    @patch("services.protected_service.requests.get")
    def test_any_protected_false_when_clear(self, mock_get):
        mock_get.return_value = mock_wms(False)
        assert check(BASE_LAT, BASE_LON).data["any_protected"] is False

    @patch("services.protected_service.requests.get")
    def test_in_natura_when_detected(self, mock_get):
        """Prva vrstva (natura2000_hab) vracia True, ostatne False."""
        call_count = [0]
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            return mock_wms(call_count[0] == 1)
        mock_get.side_effect = side_effect
        r = check(BASE_LAT, BASE_LON)
        assert r.data["in_natura2000"] is True
        assert r.data["any_protected"] is True

    @patch("services.protected_service.requests.get")
    def test_data_has_all_keys(self, mock_get):
        mock_get.return_value = mock_wms(False)
        r = check(BASE_LAT, BASE_LON)
        for key in ["in_natura2000","in_chko","in_npr_pr","in_np","findings","any_protected"]:
            assert key in r.data

    @patch("services.protected_service.requests.get")
    def test_source_is_set(self, mock_get):
        mock_get.return_value = mock_wms(False)
        assert check(BASE_LAT, BASE_LON).source == "protected_service"

    @patch("services.protected_service.requests.get")
    def test_wms_error_all_layers_returns_ok_100(self, mock_get):
        """
        Ked vsetky WMS vrstvy zlyhaju, _query_all_layers vracia False pre kazdu.
        check() to vyhodnosti ako 'ziadna ochrana' = score 100.
        Toto je spravne spravanie: pri nedostupnosti WMS nepotrestame pozemok.
        """
        import requests as req
        mock_get.side_effect = req.RequestException("SOP SR down")
        r = check(BASE_LAT, BASE_LON)
        assert r.ok is True
        assert r.score == 100.0
        assert r.data["any_protected"] is False

    def test_feature_disabled_returns_skip(self):
        with patch("services.protected_service.is_feature_enabled", return_value=False):
            r = check(BASE_LAT, BASE_LON)
        assert r.data.get("skipped") is True and r.score == 50.0

