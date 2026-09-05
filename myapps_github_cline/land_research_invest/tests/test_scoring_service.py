"""
Unit Tests - Scoring Service
=============================
Testuje vazeny scoring algoritmus, odporucania a prahove hodnoty.
Cista logika - 100% offline, ziadne HTTP requesty ani mockovanie.
"""

import pytest
from models.result import ServiceResult
from models.parcel import Parcel
from services.scoring_service import (
    score_parcel, calculate_weighted_score,
    get_recommendation, needs_cadastral_checklist,
    WEIGHT_TO_SOURCE,
)


def make_result(source: str, score: float, ok: bool = True) -> ServiceResult:
    return ServiceResult(ok=ok, score=score, data={}, source=source)


def make_full_results(
    price=80.0, distance=70.0, infra=90.0,
    legal=60.0, flood=100.0, soil=75.0
) -> dict:
    return {
        "price_analysis_service": make_result("price_analysis_service", price),
        "distance_service":       make_result("distance_service",       distance),
        "overpass_service":       make_result("overpass_service",       infra),
        "cadastral_service":      make_result("cadastral_service",      legal),
        "flood_service":          make_result("flood_service",          flood),
        "bpej_service":           make_result("bpej_service",           soil),
    }


WEIGHTS = {
    "price": 0.20, "distance": 0.15, "infrastructure": 0.25,
    "legal_proxy": 0.20, "flood_risk": 0.10, "soil_quality": 0.10,
}



class TestWeightToSourceMapping:
    """Overuje ze mapovanie vah -> service names je spravne."""

    def test_exactly_six_mappings(self):
        assert len(WEIGHT_TO_SOURCE) == 6

    def test_price_maps_correctly(self):
        assert WEIGHT_TO_SOURCE["price"] == "price_analysis_service"

    def test_distance_maps_correctly(self):
        assert WEIGHT_TO_SOURCE["distance"] == "distance_service"

    def test_infrastructure_maps_correctly(self):
        assert WEIGHT_TO_SOURCE["infrastructure"] == "overpass_service"

    def test_legal_proxy_maps_correctly(self):
        assert WEIGHT_TO_SOURCE["legal_proxy"] == "cadastral_service"

    def test_flood_risk_maps_correctly(self):
        assert WEIGHT_TO_SOURCE["flood_risk"] == "flood_service"

    def test_soil_quality_maps_correctly(self):
        assert WEIGHT_TO_SOURCE["soil_quality"] == "bpej_service"


class TestCalculateWeightedScore:
    """Testy vazeneho scoring algoritmu."""

    def test_all_100_returns_100(self):
        score = calculate_weighted_score(
            make_full_results(100, 100, 100, 100, 100, 100), WEIGHTS)
        assert score == pytest.approx(100.0, abs=0.1)

    def test_all_zero_returns_0(self):
        assert calculate_weighted_score(
            make_full_results(0, 0, 0, 0, 0, 0), WEIGHTS) == pytest.approx(0.0)

    def test_all_50_returns_50(self):
        assert calculate_weighted_score(
            make_full_results(50, 50, 50, 50, 50, 50), WEIGHTS) == pytest.approx(50.0)

    def test_score_in_range_0_to_100(self):
        score = calculate_weighted_score(make_full_results(), WEIGHTS)
        assert 0.0 <= score <= 100.0

    def test_returns_float(self):
        assert isinstance(calculate_weighted_score(make_full_results(), WEIGHTS), float)

    def test_empty_results_returns_0(self):
        assert calculate_weighted_score({}, WEIGHTS) == 0.0

    def test_higher_infrastructure_raises_total(self):
        low  = calculate_weighted_score(make_full_results(infra=20),  WEIGHTS)
        high = calculate_weighted_score(make_full_results(infra=100), WEIGHTS)
        assert high > low

    def test_infrastructure_bigger_impact_than_price(self):
        """Infrastruktura (0.25) musi mat vacsi dopad ako cena (0.20)."""
        base = make_full_results(50, 50, 50, 50, 50, 50)
        base_score = calculate_weighted_score(base, WEIGHTS)
        delta_infra = calculate_weighted_score(
            {**base, "overpass_service": make_result("overpass_service", 100)},
            WEIGHTS) - base_score
        delta_price = calculate_weighted_score(
            {**base, "price_analysis_service": make_result("price_analysis_service", 100)},
            WEIGHTS) - base_score
        assert delta_infra > delta_price

    def test_missing_service_normalizes_remaining(self):
        partial = {k: v for k, v in make_full_results().items()
                   if k != "flood_service"}
        assert 0.0 <= calculate_weighted_score(partial, WEIGHTS) <= 100.0

    def test_skip_result_uses_50_not_0(self):
        """skip_result -> score=50, nie 0."""
        results_zero = make_full_results(flood=0)
        results_skip = {**make_full_results(flood=0),
                        "flood_service": ServiceResult.skip_result("flood_service", "off")}
        assert calculate_weighted_score(results_skip, WEIGHTS) > \
               calculate_weighted_score(results_zero, WEIGHTS)


class TestGetRecommendation:
    """Testy textoveho odporucania podla score."""

    def test_85_is_strong_buy(self):
        assert get_recommendation(85.0) == "STRONG BUY"

    def test_100_is_strong_buy(self):
        assert get_recommendation(100.0) == "STRONG BUY"

    def test_84_is_investigate(self):
        assert get_recommendation(84.9) == "INVESTIGATE"

    def test_70_is_investigate(self):
        assert get_recommendation(70.0) == "INVESTIGATE"

    def test_69_is_consider(self):
        assert get_recommendation(69.9) == "CONSIDER"

    def test_50_is_consider(self):
        assert get_recommendation(50.0) == "CONSIDER"

    def test_49_is_skip(self):
        assert get_recommendation(49.9) == "SKIP"

    def test_0_is_skip(self):
        assert get_recommendation(0.0) == "SKIP"

    def test_returns_string(self):
        assert isinstance(get_recommendation(75.0), str)


class TestNeedsCadastralChecklist:
    """Testy prahu pre generovanie katastralneho checklistu."""

    def test_70_needs_checklist(self):
        assert needs_cadastral_checklist(70.0) is True

    def test_100_needs_checklist(self):
        assert needs_cadastral_checklist(100.0) is True

    def test_69_does_not_need_checklist(self):
        assert needs_cadastral_checklist(69.9) is False

    def test_0_does_not_need_checklist(self):
        assert needs_cadastral_checklist(0.0) is False

    def test_returns_bool(self):
        assert isinstance(needs_cadastral_checklist(75.0), bool)


class TestScoreParcel:
    """Testy hlavnej score_parcel() funkcie na Parcel objekte."""

    def _make_parcel(self, **kwargs) -> Parcel:
        p = Parcel(url="http://test.sk/1", price_eur=30000, area_sqm=800)
        for source, result in make_full_results(**kwargs).items():
            p.add_result(result)
        return p

    def test_returns_parcel(self):
        assert isinstance(score_parcel(self._make_parcel()), Parcel)

    def test_modifies_inplace(self):
        p = self._make_parcel()
        assert score_parcel(p) is p

    def test_final_score_is_set(self):
        assert score_parcel(self._make_parcel()).final_score > 0.0

    def test_recommendation_is_set(self):
        rec = score_parcel(self._make_parcel()).recommendation
        assert rec in ("STRONG BUY", "INVESTIGATE", "CONSIDER", "SKIP")

    def test_all_perfect_gives_strong_buy(self):
        p = self._make_parcel(
            price=100, distance=100, infra=100, legal=100, flood=100, soil=100)
        score_parcel(p)
        assert p.recommendation == "STRONG BUY"
        assert p.final_score >= 85.0

    def test_all_zero_gives_skip(self):
        p = self._make_parcel(
            price=0, distance=0, infra=0, legal=0, flood=0, soil=0)
        score_parcel(p)
        assert p.recommendation == "SKIP"
        assert p.final_score < 50.0

    def test_empty_parcel_score_is_0(self):
        p = Parcel(url="http://test.sk/2", price_eur=20000, area_sqm=700)
        score_parcel(p)
        assert p.final_score == 0.0

    def test_checklist_needed_above_70(self):
        p = self._make_parcel(
            price=100, distance=100, infra=100, legal=100, flood=100, soil=100)
        score_parcel(p)
        assert needs_cadastral_checklist(p.final_score) is True

    def test_checklist_not_needed_below_70(self):
        p = self._make_parcel(
            price=0, distance=0, infra=0, legal=0, flood=0, soil=0)
        score_parcel(p)
        assert needs_cadastral_checklist(p.final_score) is False

