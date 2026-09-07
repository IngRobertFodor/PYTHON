"""
Testy - Validator konfiguracie
================================
Testuje ze validate_config() zachyti kazdu chybu po slovensky
a ze platny config preide bez chyb.
100% offline - pracuje s dict, nie so suborom.
"""

import pytest
import copy
from config_validator import validate_config

VALID_CFG = {
    "criteria": {
        "location": {
            "center_lat": 48.1486, "center_lon": 17.1077,
            "max_distance_km": 70,
        },
        "price": {
            "min_eur": 10000, "max_eur": 50000,
            "max_price_per_sqm_eur": 100,
        },
        "parcel": {
            "min_area_sqm": 600, "max_area_sqm": 1500, "min_width_m": 15,
        },
        "terrain": {
            "max_slope_percent": 15, "preferred_slope_percent": 5,
            "max_elevation_m": 400, "max_radon_risk_class": 2,
        },
    },
    "scoring": {
        "weights": {
            "price": 0.18, "distance": 0.12, "infrastructure": 0.20,
            "legal_proxy": 0.18, "flood_risk": 0.10, "soil_quality": 0.08,
            "terrain": 0.07, "protected_zones": 0.07,
        },
        "thresholds": {"strong_buy": 85, "investigate": 70, "consider": 50},
        "checklist_min_score": 70,
    },
    "sources": {
        "nehnutelnosti_sk": {"enabled": True, "zone": "GREEN"},
        "reality_sk":       {"enabled": True, "zone": "YELLOW"},
    },
    "features": {"use_distance": True, "use_flood": True},
}


def mod(**kv):
    """Hlboka kopia VALID_CFG s prepisom cez dotted key."""
    c = copy.deepcopy(VALID_CFG)
    for key, val in kv.items():
        parts = key.split(".")
        obj = c
        for p in parts[:-1]: obj = obj[p]
        obj[parts[-1]] = val
    return c


class TestValidConfig:
    def test_valid_no_errors(self):      assert validate_config(VALID_CFG) == []
    def test_returns_list(self):         assert isinstance(validate_config(VALID_CFG), list)


class TestRequiredSections:
    def test_missing_criteria(self):
        c = copy.deepcopy(VALID_CFG); del c["criteria"]
        assert any("criteria" in e for e in validate_config(c))

    def test_missing_scoring(self):
        c = copy.deepcopy(VALID_CFG); del c["scoring"]
        assert any("scoring" in e for e in validate_config(c))

    def test_missing_sources(self):
        c = copy.deepcopy(VALID_CFG); del c["sources"]
        assert any("sources" in e for e in validate_config(c))

    def test_missing_features(self):
        c = copy.deepcopy(VALID_CFG); del c["features"]
        assert any("features" in e for e in validate_config(c))


class TestWeights:
    def test_sum_over_1(self):
        errors = validate_config(mod(**{"scoring.weights.price": 0.50}))
        assert any("1.0" in e or "sucet" in e.lower() for e in errors)

    def test_sum_under_1(self):
        errors = validate_config(mod(**{"scoring.weights.price": 0.01}))
        assert any("1.0" in e or "sucet" in e.lower() for e in errors)

    def test_exact_1_passes(self):
        assert validate_config(VALID_CFG) == []

    def test_negative_weight(self):
        errors = validate_config(mod(**{"scoring.weights.price": -0.10}))
        assert any("zaporna" in e or "price" in e for e in errors)

    def test_non_numeric_weight(self):
        errors = validate_config(mod(**{"scoring.weights.price": "abc"}))
        assert any("price" in e for e in errors)


class TestThresholds:
    def test_strong_buy_lt_investigate(self):
        c = mod(**{"scoring.thresholds.strong_buy": 60,
                   "scoring.thresholds.investigate": 70})
        assert any("strong_buy" in e for e in validate_config(c))

    def test_investigate_lt_consider(self):
        c = mod(**{"scoring.thresholds.investigate": 40,
                   "scoring.thresholds.consider": 50})
        assert any("investigate" in e for e in validate_config(c))

    def test_above_100(self):
        errors = validate_config(mod(**{"scoring.thresholds.strong_buy": 105}))
        assert any("100" in e for e in errors)

    def test_below_0(self):
        errors = validate_config(mod(**{"scoring.thresholds.consider": -5}))
        assert len(errors) > 0

    def test_valid_passes(self):
        assert validate_config(VALID_CFG) == []


class TestPrice:
    def test_min_greater_than_max(self):
        c = mod(**{"criteria.price.min_eur": 60000,
                   "criteria.price.max_eur": 50000})
        assert any("min_eur" in e for e in validate_config(c))

    def test_min_equals_max(self):
        c = mod(**{"criteria.price.min_eur": 50000,
                   "criteria.price.max_eur": 50000})
        assert len(validate_config(c)) > 0

    def test_negative_max_eur(self):
        assert len(validate_config(mod(**{"criteria.price.max_eur": -1}))) > 0

    def test_valid_passes(self):
        assert validate_config(VALID_CFG) == []


class TestParcel:
    def test_min_area_gt_max(self):
        c = mod(**{"criteria.parcel.min_area_sqm": 2000,
                   "criteria.parcel.max_area_sqm": 1500})
        assert any("min_area_sqm" in e for e in validate_config(c))

    def test_zero_width(self):
        errors = validate_config(mod(**{"criteria.parcel.min_width_m": 0}))
        assert any("min_width_m" in e for e in errors)


class TestLocation:
    def test_zero_distance(self):
        errors = validate_config(mod(**{"criteria.location.max_distance_km": 0}))
        assert any("max_distance_km" in e for e in errors)

    def test_string_lat(self):
        errors = validate_config(mod(**{"criteria.location.center_lat": "BA"}))
        assert any("center_lat" in e for e in errors)


class TestSources:
    def test_invalid_enabled_string(self):
        c = copy.deepcopy(VALID_CFG)
        c["sources"]["nehnutelnosti_sk"]["enabled"] = "yes"
        assert any("enabled" in e for e in validate_config(c))

    def test_invalid_zone(self):
        c = copy.deepcopy(VALID_CFG)
        c["sources"]["nehnutelnosti_sk"]["zone"] = "ORANGE"
        assert any("zone" in e for e in validate_config(c))

    def test_valid_zones_pass(self):
        assert validate_config(VALID_CFG) == []


class TestTerrain:
    def test_preferred_slope_gte_max(self):
        c = mod(**{"criteria.terrain.preferred_slope_percent": 15,
                   "criteria.terrain.max_slope_percent": 15})
        assert any("preferred_slope" in e for e in validate_config(c))

    def test_invalid_radon_class_5(self):
        errors = validate_config(mod(**{"criteria.terrain.max_radon_risk_class": 5}))
        assert any("radon" in e for e in errors)

    def test_radon_class_1_passes(self):
        assert validate_config(mod(**{"criteria.terrain.max_radon_risk_class": 1})) == []

    def test_radon_class_3_passes(self):
        assert validate_config(mod(**{"criteria.terrain.max_radon_risk_class": 3})) == []

    def test_negative_elevation(self):
        assert len(validate_config(mod(**{"criteria.terrain.max_elevation_m": -100}))) > 0

