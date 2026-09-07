"""
Unit Tests - Overpass Service
================================
Testuje analyzu infrastrukturnych prvkov cez OSM Overpass API.
HTTP requesty su mockované - 100% offline.
"""

import pytest
from unittest.mock import patch, MagicMock
from services.overpass_service import (
    check, _analyze_elements, _calculate_score, _haversine_m, _min_dist,
)
from models.result import ServiceResult


def make_node(lat, lon, tags): return {"type": "node", "lat": lat, "lon": lon, "tags": tags}
def make_way(lat, lon, tags): return {"type": "way", "center": {"lat": lat, "lon": lon}, "tags": tags}

BASE_LAT, BASE_LON = 48.2195, 17.3976


def good_elements():
    return [
        make_node(BASE_LAT + 0.0005, BASE_LON, {"highway": "residential", "width": "7"}),
        make_node(BASE_LAT + 0.001,  BASE_LON, {"power": "pole"}),
        make_node(BASE_LAT, BASE_LON + 0.001,  {"waterway": "stream"}),
        make_way(BASE_LAT + 0.01,    BASE_LON,  {"landuse": "forest"}),
        make_way(BASE_LAT + 0.05,    BASE_LON,  {"highway": "motorway"}),
        make_way(BASE_LAT + 0.02,    BASE_LON,  {"railway": "rail"}),
        make_way(BASE_LAT + 0.06,    BASE_LON,  {"landuse": "landfill"}),
        make_way(BASE_LAT + 0.04,    BASE_LON,  {"landuse": "industrial"}),
    ]



class TestHaversineM:
    def test_same_point_is_zero(self):
        assert _haversine_m(BASE_LAT, BASE_LON, BASE_LAT, BASE_LON) == pytest.approx(0, abs=1)

    def test_100m_north(self):
        d = _haversine_m(BASE_LAT, BASE_LON, BASE_LAT + 0.0009, BASE_LON)
        assert 80 < d < 120

    def test_symmetry(self):
        d1 = _haversine_m(BASE_LAT, BASE_LON, BASE_LAT + 0.01, BASE_LON)
        d2 = _haversine_m(BASE_LAT + 0.01, BASE_LON, BASE_LAT, BASE_LON)
        assert d1 == pytest.approx(d2, rel=0.001)


class TestMinDist:
    def test_finds_nearest_highway(self):
        elements = [
            make_node(BASE_LAT + 0.01,  BASE_LON, {"highway": "residential"}),
            make_node(BASE_LAT + 0.001, BASE_LON, {"highway": "track"}),
        ]
        assert _min_dist(elements, BASE_LAT, BASE_LON, "highway", None) < 200

    def test_filters_by_value(self):
        elements = [
            make_node(BASE_LAT + 0.001, BASE_LON, {"power": "substation"}),
            make_node(BASE_LAT + 0.005, BASE_LON, {"power": "pole"}),
        ]
        d_pole = _min_dist(elements, BASE_LAT, BASE_LON, "power", ["pole"])
        d_all  = _min_dist(elements, BASE_LAT, BASE_LON, "power", None)
        assert d_pole > d_all

    def test_no_matching_returns_9999(self):
        elements = [make_node(BASE_LAT, BASE_LON, {"landuse": "forest"})]
        assert _min_dist(elements, BASE_LAT, BASE_LON, "highway", None) == 9999.0


class TestAnalyzeElements:
    def test_returns_all_sections(self):
        r = _analyze_elements(good_elements(), BASE_LAT, BASE_LON)
        for k in ["road", "electricity", "water", "forest_buffer", "noise", "environment"]:
            assert k in r

    def test_road_accessible_when_nearby(self):
        assert _analyze_elements(good_elements(), BASE_LAT, BASE_LON)["road"]["accessible"] is True

    def test_road_not_accessible_when_empty(self):
        assert _analyze_elements([], BASE_LAT, BASE_LON)["road"]["accessible"] is False

    def test_electricity_available_when_nearby(self):
        assert _analyze_elements(good_elements(), BASE_LAT, BASE_LON)["electricity"]["available"] is True

    def test_forest_safe_when_far(self):
        assert _analyze_elements(good_elements(), BASE_LAT, BASE_LON)["forest_buffer"]["safe"] is True


class TestCalculateScore:
    def test_good_elements_give_high_score(self):
        assert _calculate_score(_analyze_elements(good_elements(), BASE_LAT, BASE_LON)) > 50.0

    def test_empty_elements_give_low_score(self):
        assert _calculate_score(_analyze_elements([], BASE_LAT, BASE_LON)) < 30.0

    def test_score_in_range_0_100(self):
        for els in [good_elements(), []]:
            s = _calculate_score(_analyze_elements(els, BASE_LAT, BASE_LON))
            assert 0.0 <= s <= 100.0

    def test_returns_float(self):
        assert isinstance(
            _calculate_score(_analyze_elements(good_elements(), BASE_LAT, BASE_LON)), float
        )


class TestCheckFunction:
    def _mock_post(self, elements):
        m = MagicMock()
        m.status_code = 200
        m.json.return_value = {"elements": elements}
        m.raise_for_status = MagicMock()
        return m

    @patch("services.overpass_service.requests.post")
    def test_returns_service_result(self, mock_post):
        mock_post.return_value = self._mock_post(good_elements())
        assert isinstance(check(BASE_LAT, BASE_LON), ServiceResult)

    @patch("services.overpass_service.requests.post")
    def test_good_area_positive_score(self, mock_post):
        mock_post.return_value = self._mock_post(good_elements())
        r = check(BASE_LAT, BASE_LON)
        assert r.ok is True and r.score > 50.0

    @patch("services.overpass_service.requests.post")
    def test_source_is_set(self, mock_post):
        mock_post.return_value = self._mock_post([])
        assert check(BASE_LAT, BASE_LON).source == "overpass_service"

    @patch("services.overpass_service.requests.post")
    def test_all_servers_fail_neutral_50(self, mock_post):
        import requests as req
        mock_post.side_effect = req.RequestException("down")
        r = check(BASE_LAT, BASE_LON)
        assert r.ok is False and r.score == 50.0

    def test_feature_disabled_returns_skip(self):
        with patch("services.overpass_service.is_feature_enabled", return_value=False):
            r = check(BASE_LAT, BASE_LON)
        assert r.data.get("skipped") is True and r.score == 50.0
