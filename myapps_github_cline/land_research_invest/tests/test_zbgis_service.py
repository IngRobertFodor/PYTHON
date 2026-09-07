"""
Testy - Sluzba geometrie parciel (ZBGIS)
============================
Testuje geometricku analyzu parcely z ZBGIS WFS.
HTTP requesty su mockované - 100% offline.
"""

import pytest
from unittest.mock import patch, MagicMock
from services.zbgis_service import (
    check, _calculate_score, _parse_wfs_response,
    _bbox_to_dimensions, _calculate_regularity, _extract_all_coords,
)
from models.result import ServiceResult

BASE_LAT, BASE_LON = 48.2195, 17.3976
DEFAULT_CFG = {
    "min_area_sqm": 600, "max_area_sqm": 1500,
    "min_width_m": 15, "min_shape_regularity": 0.5,
}

GOOD_FEATURE = {"features": [{"properties": {"VYMERA": 800.0}, "geometry": {
    "type": "Polygon",
    "coordinates": [[[0.0,0.0],[20.0,0.0],[20.0,40.0],[0.0,40.0],[0.0,0.0]]]
}}]}

NARROW_FEATURE = {"features": [{"properties": {"VYMERA": 800.0}, "geometry": {
    "type": "Polygon",
    "coordinates": [[[0.0,0.0],[8.0,0.0],[8.0,100.0],[0.0,100.0],[0.0,0.0]]]
}}]}

EMPTY_RESPONSE = {"features": []}


def mock_wfs(data):
    m = MagicMock()
    m.status_code = 200
    m.raise_for_status = MagicMock()
    m.headers = {"content-type": "application/json"}
    m.json.return_value = data
    m.text = str(data)
    return m


class TestBboxToDimensions:
    def test_square(self):
        w, l = _bbox_to_dimensions([0, 0, 20, 20])
        assert w == pytest.approx(20.0) and l == pytest.approx(20.0)

    def test_rectangle_width_smaller(self):
        w, l = _bbox_to_dimensions([0, 0, 20, 40])
        assert w == pytest.approx(20.0) and l == pytest.approx(40.0)

    def test_width_lte_length(self):
        w, l = _bbox_to_dimensions([0, 0, 100, 15])
        assert w <= l


class TestCalculateRegularity:
    def test_perfect_rectangle(self):
        assert _calculate_regularity(800.0, 20.0, 40.0) == pytest.approx(1.0)

    def test_l_shape_less_than_1(self):
        assert _calculate_regularity(600.0, 20.0, 40.0) < 1.0

    def test_zero_dimensions_returns_0(self):
        assert _calculate_regularity(800.0, 0.0, 40.0) == 0.0

    def test_in_range_0_1(self):
        for a in [100, 400, 800, 1200]:
            assert 0.0 <= _calculate_regularity(a, 20.0, 40.0) <= 1.0


class TestExtractAllCoords:
    def test_polygon_returns_coords(self):
        geom = {"type":"Polygon","coordinates":[[[0,0],[10,0],[10,10],[0,10],[0,0]]]}
        assert len(_extract_all_coords(geom)) == 5

    def test_empty_geometry(self):
        assert _extract_all_coords({}) == []

    def test_multipolygon(self):
        geom = {"type":"MultiPolygon","coordinates":[[[[0,0],[10,0],[10,10],[0,10],[0,0]]]]}
        assert len(_extract_all_coords(geom)) > 0


class TestCalculateScore:
    def test_good_parcel_high_score(self):
        geo = {"area_sqm":800,"width_m":20,"length_m":40,"shape_regularity":1.0}
        assert _calculate_score(geo, DEFAULT_CFG) > 80.0

    def test_small_parcel_low_score(self):
        """Parcela 200m2 (pod min 600m2) dostane nízky príspevok za plochu."""
        geo_small = {"area_sqm":200,"width_m":20,"length_m":10,"shape_regularity":1.0}
        geo_good  = {"area_sqm":800,"width_m":20,"length_m":40,"shape_regularity":1.0}
        # Mala parcela musi mat mensi score ako dobra parcela
        assert _calculate_score(geo_small, DEFAULT_CFG) < _calculate_score(geo_good, DEFAULT_CFG)

    def test_narrow_penalized(self):
        narrow = {"area_sqm":800,"width_m":8, "length_m":100,"shape_regularity":1.0}
        wide   = {"area_sqm":800,"width_m":20,"length_m":40, "shape_regularity":1.0}
        assert _calculate_score(narrow, DEFAULT_CFG) < _calculate_score(wide, DEFAULT_CFG)

    def test_irregular_penalized(self):
        reg   = {"area_sqm":800,"width_m":20,"length_m":40,"shape_regularity":1.0}
        irreg = {"area_sqm":800,"width_m":20,"length_m":40,"shape_regularity":0.2}
        assert _calculate_score(irreg, DEFAULT_CFG) < _calculate_score(reg, DEFAULT_CFG)

    def test_in_range_0_100(self):
        for a in [100,600,800,1500,3000]:
            geo = {"area_sqm":a,"width_m":20,"length_m":40,"shape_regularity":0.8}
            assert 0.0 <= _calculate_score(geo, DEFAULT_CFG) <= 100.0


class TestParseWfsResponse:
    def test_extracts_area(self):
        geo = _parse_wfs_response(mock_wfs(GOOD_FEATURE), BASE_LAT, BASE_LON)
        assert geo["area_sqm"] == pytest.approx(800.0)

    def test_extracts_width(self):
        geo = _parse_wfs_response(mock_wfs(GOOD_FEATURE), BASE_LAT, BASE_LON)
        assert geo["width_m"] == pytest.approx(20.0, abs=1.0)

    def test_extracts_length(self):
        geo = _parse_wfs_response(mock_wfs(GOOD_FEATURE), BASE_LAT, BASE_LON)
        assert geo["length_m"] == pytest.approx(40.0, abs=1.0)

    def test_regularity_in_range(self):
        geo = _parse_wfs_response(mock_wfs(GOOD_FEATURE), BASE_LAT, BASE_LON)
        assert 0.0 <= geo["shape_regularity"] <= 1.0

    def test_empty_raises(self):
        with pytest.raises(RuntimeError):
            _parse_wfs_response(mock_wfs(EMPTY_RESPONSE), BASE_LAT, BASE_LON)


class TestCheckFunction:
    @patch("services.zbgis_service.requests.get")
    def test_returns_service_result(self, mock_get):
        mock_get.return_value = mock_wfs(GOOD_FEATURE)
        assert isinstance(check(BASE_LAT, BASE_LON), ServiceResult)

    @patch("services.zbgis_service.requests.get")
    def test_good_parcel_high_score(self, mock_get):
        mock_get.return_value = mock_wfs(GOOD_FEATURE)
        r = check(BASE_LAT, BASE_LON)
        assert r.ok is True and r.score > 80.0

    @patch("services.zbgis_service.requests.get")
    def test_narrow_parcel_lower_score(self, mock_get):
        mock_get.return_value = mock_wfs(NARROW_FEATURE)
        r = check(BASE_LAT, BASE_LON)
        assert r.ok is True and r.score < 80.0

    @patch("services.zbgis_service.requests.get")
    def test_data_contains_area(self, mock_get):
        mock_get.return_value = mock_wfs(GOOD_FEATURE)
        assert "area_sqm" in check(BASE_LAT, BASE_LON).data

    @patch("services.zbgis_service.requests.get")
    def test_data_contains_width(self, mock_get):
        mock_get.return_value = mock_wfs(GOOD_FEATURE)
        assert "width_m" in check(BASE_LAT, BASE_LON).data

    @patch("services.zbgis_service.requests.get")
    def test_meets_min_area_true(self, mock_get):
        mock_get.return_value = mock_wfs(GOOD_FEATURE)
        assert check(BASE_LAT, BASE_LON).data["meets_min_area"] is True

    @patch("services.zbgis_service.requests.get")
    def test_meets_min_width_true(self, mock_get):
        mock_get.return_value = mock_wfs(GOOD_FEATURE)
        assert check(BASE_LAT, BASE_LON).data["meets_min_width"] is True

    @patch("services.zbgis_service.requests.get")
    def test_narrow_does_not_meet_min_width(self, mock_get):
        mock_get.return_value = mock_wfs(NARROW_FEATURE)
        assert check(BASE_LAT, BASE_LON).data["meets_min_width"] is False

    @patch("services.zbgis_service.requests.get")
    def test_parcel_number_in_data(self, mock_get):
        mock_get.return_value = mock_wfs(GOOD_FEATURE)
        r = check(BASE_LAT, BASE_LON, parcel_number="1234/5")
        assert r.data["parcel_number"] == "1234/5"

    @patch("services.zbgis_service.requests.get")
    def test_source_is_set(self, mock_get):
        mock_get.return_value = mock_wfs(GOOD_FEATURE)
        assert check(BASE_LAT, BASE_LON).source == "zbgis_service"

    @patch("services.zbgis_service.requests.get")
    def test_wfs_error_returns_neutral_50(self, mock_get):
        import requests as req
        mock_get.side_effect = req.RequestException("WFS down")
        r = check(BASE_LAT, BASE_LON)
        assert r.ok is False and r.score == 50.0

    def test_feature_disabled_returns_skip(self):
        with patch("services.zbgis_service.is_feature_enabled", return_value=False):
            r = check(BASE_LAT, BASE_LON)
        assert r.data.get("skipped") is True

