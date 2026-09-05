"""
Unit Tests - Distance Service
==============================
Testuje Haversine vzdialenost, scoring, odhad casu jazdy,
konverziu suradnic a integraciu s config_loader.
Vsetky testy su 100% offline - ziadne HTTP requesty.
"""

import pytest
from unittest.mock import patch
from services.distance_service import (
    calculate_distance,
    distance_from_bratislava,
    estimate_drive_time,
    wgs84_to_jtsk,
    jtsk_to_wgs84,
    check,
    _score_distance,
    BRATISLAVA_LAT,
    BRATISLAVA_LON,
)
from models.result import ServiceResult


# ----------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------

@pytest.fixture
def bratislava_coords():
    return {"lat": 48.1486, "lon": 17.1077}

@pytest.fixture
def trnava_coords():
    # Trnava ~47 km od BA
    return {"lat": 48.3774, "lon": 17.5853}

@pytest.fixture
def nitra_coords():
    # Nitra ~74.5 km od BA (nad 70 km kriterium)
    return {"lat": 48.3080, "lon": 18.0849}

@pytest.fixture
def senec_coords():
    # Senec ~25 km od BA
    return {"lat": 48.2195, "lon": 17.3976}


# ----------------------------------------------------------------
# TestCalculateDistance
# ----------------------------------------------------------------

class TestCalculateDistance:
    """Testy Haversine vzdialenosti medzi GPS bodmi."""

    def test_same_point_returns_zero(self, bratislava_coords):
        """Vzdialenost bodu od seba sameho musi byt 0."""
        result = calculate_distance(
            bratislava_coords["lat"], bratislava_coords["lon"],
            bratislava_coords["lat"], bratislava_coords["lon"]
        )
        assert result == pytest.approx(0.0, abs=0.01)

    def test_bratislava_to_trnava_approx_47km(self, trnava_coords):
        """BA -> Trnava by mala byt priblizne 40-55 km."""
        result = calculate_distance(
            BRATISLAVA_LAT, BRATISLAVA_LON,
            trnava_coords["lat"], trnava_coords["lon"]
        )
        assert 40.0 <= result <= 55.0

    def test_bratislava_to_nitra_approx_74km(self, nitra_coords):
        """BA -> Nitra (centrum) je priblizne 70-80 km (Haversine)."""
        result = calculate_distance(
            BRATISLAVA_LAT, BRATISLAVA_LON,
            nitra_coords["lat"], nitra_coords["lon"]
        )
        assert 70.0 <= result <= 80.0

    def test_bratislava_to_senec_approx_25km(self, senec_coords):
        """BA -> Senec by mala byt priblizne 20-32 km."""
        result = calculate_distance(
            BRATISLAVA_LAT, BRATISLAVA_LON,
            senec_coords["lat"], senec_coords["lon"]
        )
        assert 20.0 <= result <= 32.0

    def test_result_is_positive(self, trnava_coords):
        """Vzdialenost musi byt vzdy kladna."""
        result = calculate_distance(
            BRATISLAVA_LAT, BRATISLAVA_LON,
            trnava_coords["lat"], trnava_coords["lon"]
        )
        assert result > 0

    def test_symmetry(self, trnava_coords):
        """Vzdialenost A->B == B->A."""
        d1 = calculate_distance(
            BRATISLAVA_LAT, BRATISLAVA_LON,
            trnava_coords["lat"], trnava_coords["lon"]
        )
        d2 = calculate_distance(
            trnava_coords["lat"], trnava_coords["lon"],
            BRATISLAVA_LAT, BRATISLAVA_LON
        )
        assert d1 == pytest.approx(d2, rel=0.001)

    def test_returns_float(self, trnava_coords):
        """Funkcia musi vracat float."""
        result = calculate_distance(
            BRATISLAVA_LAT, BRATISLAVA_LON,
            trnava_coords["lat"], trnava_coords["lon"]
        )
        assert isinstance(result, float)



# ----------------------------------------------------------------
# TestDistanceFromBratislava
# ----------------------------------------------------------------

class TestDistanceFromBratislava:
    """Testy skratkovej funkcie distance_from_bratislava."""

    def test_senec_within_70km(self, senec_coords):
        result = distance_from_bratislava(senec_coords["lat"], senec_coords["lon"])
        assert result < 70.0

    def test_nitra_over_70km(self, nitra_coords):
        result = distance_from_bratislava(nitra_coords["lat"], nitra_coords["lon"])
        assert result > 70.0

    def test_trnava_within_70km(self, trnava_coords):
        result = distance_from_bratislava(trnava_coords["lat"], trnava_coords["lon"])
        assert result < 70.0

    def test_bratislava_center_is_zero(self):
        result = distance_from_bratislava(BRATISLAVA_LAT, BRATISLAVA_LON)
        assert result == pytest.approx(0.0, abs=0.01)


# ----------------------------------------------------------------
# TestEstimateDriveTime
# ----------------------------------------------------------------

class TestEstimateDriveTime:
    """Testy odhadu casu jazdy."""

    def test_zero_distance_returns_zero(self):
        assert estimate_drive_time(0) == 0

    def test_55km_approx_60min(self):
        """55 km pri 55 km/h = ~60 minut."""
        result = estimate_drive_time(55)
        assert result == pytest.approx(60, abs=2)

    def test_returns_int(self):
        assert isinstance(estimate_drive_time(40), int)

    def test_longer_distance_more_time(self):
        assert estimate_drive_time(30) < estimate_drive_time(60)

    def test_negative_distance_returns_zero(self):
        assert estimate_drive_time(-10) == 0

# ----------------------------------------------------------------
# TestCheckFunction
# ----------------------------------------------------------------

class TestCheckFunction:
    """Testy hlavnej check() funkcie - jednotny kontrakt."""

    def test_returns_service_result(self, senec_coords):
        result = check(senec_coords["lat"], senec_coords["lon"])
        assert isinstance(result, ServiceResult)

    def test_senec_within_criteria(self, senec_coords):
        """Senec (25 km) splna kriterium do 70 km."""
        result = check(senec_coords["lat"], senec_coords["lon"])
        assert result.ok is True
        assert result.data["within_criteria"] is True

    def test_nitra_not_within_criteria(self, nitra_coords):
        """Nitra (74.5 km) nesplna kriterium 70 km."""
        result = check(nitra_coords["lat"], nitra_coords["lon"])
        assert result.ok is True
        assert result.data["within_criteria"] is False

    def test_nitra_score_is_zero(self, nitra_coords):
        result = check(nitra_coords["lat"], nitra_coords["lon"])
        assert result.score == 0.0

    def test_senec_score_positive(self, senec_coords):
        result = check(senec_coords["lat"], senec_coords["lon"])
        assert result.score > 0.0

    def test_source_is_distance_service(self, senec_coords):
        result = check(senec_coords["lat"], senec_coords["lon"])
        assert result.source == "distance_service"

    def test_data_contains_distance_km(self, senec_coords):
        result = check(senec_coords["lat"], senec_coords["lon"])
        assert "distance_km" in result.data
        assert isinstance(result.data["distance_km"], float)

    def test_data_contains_drive_time(self, senec_coords):
        result = check(senec_coords["lat"], senec_coords["lon"])
        assert "drive_time_min" in result.data

    def test_feature_disabled_returns_skip(self, senec_coords):
        """Ak use_distance=false, check() vracia skip_result."""
        with patch("services.distance_service.is_feature_enabled", return_value=False):
            result = check(senec_coords["lat"], senec_coords["lon"])
        assert result.data.get("skipped") is True
        assert result.score == 50.0

    def test_to_dict_has_required_keys(self, senec_coords):
        result = check(senec_coords["lat"], senec_coords["lon"])
        d = result.to_dict()
        assert all(k in d for k in ["ok", "score", "data", "error", "source"])


# ----------------------------------------------------------------
# TestCoordinateConversion (vyzaduje pyproj)
# ----------------------------------------------------------------

_pyproj_missing = pytest.mark.skipif(
    not __import__("importlib").util.find_spec("pyproj"),
    reason="pyproj nie je nainstalovany - pip install pyproj"
)


@_pyproj_missing
class TestCoordinateConversion:
    """Testy konverzie suradnic WGS-84 <-> S-JTSK (vyzaduje pyproj)."""

    def test_wgs84_to_jtsk_returns_tuple(self):
        result = wgs84_to_jtsk(BRATISLAVA_LAT, BRATISLAVA_LON)
        assert isinstance(result, tuple) and len(result) == 2

    def test_jtsk_to_wgs84_returns_tuple(self):
        x, y = wgs84_to_jtsk(BRATISLAVA_LAT, BRATISLAVA_LON)
        result = jtsk_to_wgs84(x, y)
        assert isinstance(result, tuple) and len(result) == 2

    def test_roundtrip_accuracy(self):
        """WGS84 -> JTSK -> WGS84 musi dat povodne suradnice (tolerance 0.001 stupna)."""
        original_lat, original_lon = 48.3774, 17.5853
        x, y = wgs84_to_jtsk(original_lat, original_lon)
        back_lat, back_lon = jtsk_to_wgs84(x, y)
        assert back_lat == pytest.approx(original_lat, abs=0.001)
        assert back_lon == pytest.approx(original_lon, abs=0.001)

    def test_jtsk_x_negative_for_slovakia(self):
        """S-JTSK X pre SR musi byt zaporna (specificka vlastnost JTSK)."""
        x, y = wgs84_to_jtsk(BRATISLAVA_LAT, BRATISLAVA_LON)
        assert x < 0


# ----------------------------------------------------------------
# TestScoreDistance
# ----------------------------------------------------------------

class TestScoreDistance:
    """Testy interneho scoring algoritmu."""

    def test_zero_distance_is_100(self):
        assert _score_distance(0, 70) == 100.0

    def test_max_distance_is_zero(self):
        assert _score_distance(70, 70) == 0.0

    def test_over_max_is_zero(self):
        assert _score_distance(90, 70) == 0.0

    def test_half_distance_approx_50(self):
        assert _score_distance(35, 70) == pytest.approx(50.0, abs=0.1)

    def test_score_decreases_with_distance(self):
        assert _score_distance(10, 70) > _score_distance(40, 70)

    def test_score_always_in_range_0_100(self):
        for d in [0, 10, 35, 69, 70, 100]:
            score = _score_distance(d, 70)
            assert 0.0 <= score <= 100.0

