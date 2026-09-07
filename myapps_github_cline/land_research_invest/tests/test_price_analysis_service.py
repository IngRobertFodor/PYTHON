"""
Testy - Sluzba cenovej analyzy
=====================================
Testuje cenovu analyzu, porovnanie s priemerom, scoring.
100% offline - ziadne externe API ani HTTP.
"""

import pytest
from unittest.mock import patch
from services.price_analysis_service import (
    check, get_fallback_avg, calculate_local_avg,
    _calculate_price_drop, _is_seller_motivated,
    _calculate_score, REGIONAL_AVG_EUR_PER_SQM,
)
from models.result import ServiceResult

DEFAULT_CFG = {
    "max_listing_age_days": 180,
    "price_vs_local_avg_max_ratio": 1.2,
    "underpriced_threshold_ratio": 0.8,
}


class TestGetFallbackAvg:
    """Testy regionalnych fallback priemerov EUR/m2."""

    def test_close_to_ba_high_avg(self):
        """Do 20 km od BA = vyssi priemer."""
        assert get_fallback_avg(10.0) > get_fallback_avg(60.0)

    def test_far_from_ba_low_avg(self):
        """70 km od BA = najnizsi priemer zo zoznamu."""
        assert get_fallback_avg(70.0) <= get_fallback_avg(30.0)

    def test_all_distance_bands_defined(self):
        """Kazde pasmo vzdialenosti vracia rozumnu hodnotu."""
        for km in [5, 15, 25, 40, 55, 70]:
            avg = get_fallback_avg(km)
            assert avg > 0

    def test_beyond_70km_returns_minimum(self):
        """Nad 70 km vracia minimálny fallback."""
        assert get_fallback_avg(100.0) == REGIONAL_AVG_EUR_PER_SQM[-1][1]

    def test_returns_float(self):
        assert isinstance(get_fallback_avg(30.0), float)


class TestCalculateLocalAvg:
    """Testy trimmovaneho priemeru z DB."""

    def test_basic_average(self):
        assert calculate_local_avg([10.0, 20.0, 30.0]) == pytest.approx(20.0)

    def test_too_few_returns_none(self):
        assert calculate_local_avg([10.0, 20.0]) is None
        assert calculate_local_avg([]) is None

    def test_trims_extremes(self):
        """10 hodnot: trimuje 1 z kazdeho konca."""
        prices = [1.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 100.0]
        avg = calculate_local_avg(prices)
        assert avg == pytest.approx(10.0)

    def test_returns_float(self):
        result = calculate_local_avg([20.0, 30.0, 40.0])
        assert isinstance(result, float)


class TestCalculatePriceDrop:
    """Testy poklesu ceny z historie inzeratu."""

    def test_no_history_returns_0(self):
        assert _calculate_price_drop([]) == 0.0

    def test_single_entry_returns_0(self):
        assert _calculate_price_drop([{"date": "2024-01", "price_eur": 30000}]) == 0.0

    def test_price_drop_calculated(self):
        history = [
            {"date": "2024-01", "price_eur": 40000},
            {"date": "2024-06", "price_eur": 32000},
        ]
        drop = _calculate_price_drop(history)
        assert drop == pytest.approx(20.0)  # 20% pokles

    def test_price_increase_is_negative(self):
        """Ak cena stupla, drop je zaporny."""
        history = [
            {"date": "2024-01", "price_eur": 30000},
            {"date": "2024-06", "price_eur": 35000},
        ]
        assert _calculate_price_drop(history) < 0.0

    def test_no_change_returns_0(self):
        history = [
            {"date": "2024-01", "price_eur": 30000},
            {"date": "2024-06", "price_eur": 30000},
        ]
        assert _calculate_price_drop(history) == 0.0


class TestIsSellerMotivated:
    def test_old_listing_is_motivated(self):
        assert _is_seller_motivated(200, 180) is True

    def test_fresh_listing_not_motivated(self):
        assert _is_seller_motivated(30, 180) is False

    def test_exactly_at_threshold_not_motivated(self):
        assert _is_seller_motivated(180, 180) is False


class TestCalculateScore:
    """Testy scoring algoritmu cenovej analyzy."""

    def test_underpriced_gives_high_score(self):
        """Ratio 0.5 (50% pod priemerom) = blizko 100."""
        score = _calculate_score(0.5, 0, 0.0, DEFAULT_CFG)
        assert score >= 90.0

    def test_at_avg_gives_mid_score(self):
        """Ratio 1.0 (rovny priemer) = stredny score."""
        score = _calculate_score(1.0, 0, 0.0, DEFAULT_CFG)
        assert 60.0 <= score <= 80.0

    def test_overpriced_gives_low_score(self):
        """Ratio 1.5 (50% nad priemerom) = nízky score."""
        score = _calculate_score(1.5, 0, 0.0, DEFAULT_CFG)
        assert score < 40.0

    def test_old_listing_bonus(self):
        """Stary inzerat (>180 dni) = bonus +5."""
        fresh = _calculate_score(1.0, 30, 0.0, DEFAULT_CFG)
        old   = _calculate_score(1.0, 200, 0.0, DEFAULT_CFG)
        assert old == pytest.approx(fresh + 5.0, abs=0.1)

    def test_price_drop_bonus(self):
        """Pokles ceny >= 5% = bonus +5."""
        no_drop = _calculate_score(1.0, 0, 0.0, DEFAULT_CFG)
        dropped = _calculate_score(1.0, 0, 10.0, DEFAULT_CFG)
        assert dropped == pytest.approx(no_drop + 5.0, abs=0.1)

    def test_score_in_range_0_100(self):
        for ratio in [0.3, 0.8, 1.0, 1.2, 1.5, 2.5]:
            s = _calculate_score(ratio, 0, 0.0, DEFAULT_CFG)
            assert 0.0 <= s <= 100.0

    def test_score_decreases_with_ratio(self):
        """Vyssi price_ratio = nizsi score."""
        scores = [_calculate_score(r, 0, 0.0, DEFAULT_CFG)
                  for r in [0.5, 0.8, 1.0, 1.2, 1.5]]
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1]

    def test_double_bonus_max_100(self):
        """Oba bonusy (stara inzercia + pokles) nemozu dat viac ako 100."""
        score = _calculate_score(0.5, 200, 10.0, DEFAULT_CFG)
        assert score <= 100.0


class TestCheckFunction:
    """Testy hlavnej check() funkcie."""

    def test_returns_service_result(self):
        r = check(30000, 800, 30.0)
        assert isinstance(r, ServiceResult)

    def test_underpriced_parcel_high_score(self):
        """800m2 za 10000 EUR = ~12.5 EUR/m2 (daleko pod priemerom ~35 EUR/m2)."""
        r = check(10000, 800, 40.0)
        assert r.ok is True and r.score >= 85.0

    def test_overpriced_parcel_low_score(self):
        """800m2 za 120000 EUR = 150 EUR/m2 (vysoko nad priemerom ~35 EUR/m2)."""
        r = check(120000, 800, 40.0)
        assert r.ok is True and r.score < 40.0

    def test_data_contains_price_per_sqm(self):
        r = check(30000, 800, 30.0)
        assert "price_per_sqm" in r.data
        assert r.data["price_per_sqm"] == pytest.approx(37.5)

    def test_data_contains_ratio(self):
        r = check(30000, 800, 30.0)
        assert "price_ratio" in r.data

    def test_data_is_underpriced_flag(self):
        r = check(5000, 800, 40.0)   # velmi lacny
        assert r.data["is_underpriced"] is True

    def test_data_is_overpriced_flag(self):
        r = check(200000, 800, 30.0)  # predrazeny
        assert r.data["is_overpriced"] is True

    def test_uses_local_avg_when_provided(self):
        """Ak je lokalny priemer zadany, nepoužije fallback."""
        r = check(30000, 800, 30.0, local_avg_eur_per_sqm=50.0)
        assert r.data["used_fallback_avg"] is False
        assert r.data["local_avg_per_sqm"] == pytest.approx(50.0)

    def test_uses_fallback_when_no_local_avg(self):
        r = check(30000, 800, 30.0)
        assert r.data["used_fallback_avg"] is True

    def test_price_history_calculated(self):
        history = [
            {"date": "2024-01", "price_eur": 40000},
            {"date": "2024-06", "price_eur": 32000},
        ]
        r = check(32000, 800, 40.0, price_history=history)
        assert r.data["price_drop_pct"] == pytest.approx(20.0)

    def test_seller_motivated_flag(self):
        r = check(30000, 800, 40.0, listing_age_days=200)
        assert r.data["seller_motivated"] is True

    def test_invalid_area_returns_error(self):
        r = check(30000, 0, 30.0)
        assert r.ok is False

    def test_invalid_price_returns_error(self):
        r = check(0, 800, 30.0)
        assert r.ok is False

    def test_source_is_set(self):
        assert check(30000, 800, 30.0).source == "price_analysis_service"

    def test_feature_disabled_returns_skip(self):
        with patch("services.price_analysis_service.is_feature_enabled",
                   return_value=False):
            r = check(30000, 800, 30.0)
        assert r.data.get("skipped") is True

