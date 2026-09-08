"""
Testy - Sluzba katastra
=======================
Testuje generovanie checklistu, vyhodnotenie LV dat a scoring.
Cista logika - 100% offline, ziadne HTTP requesty.
"""

import pytest
from unittest.mock import patch
from services.cadastral_service import (
    check, evaluate_lv_data, generate_checklist, _calculate_score,
)
from models.result import ServiceResult


# ----------------------------------------------------------------
# Helper - cisty LV (ziadne problemy)
# ----------------------------------------------------------------

def clean_lv(overrides=None):
    base = {
        "plombs": [],
        "liens": False,
        "preemption": False,
        "usufruct": False,
        "unknown_easement": False,
        "co_owners": 1,
        "has_register_e": False,
        "min_fraction_denominator": 1,
        "spf_owner": False,
        "unknown_owners": False,
        "road_has_easement": True,
    }
    if overrides:
        base.update(overrides)
    return base


# ----------------------------------------------------------------
# TestGenerateChecklist
# ----------------------------------------------------------------

class TestGenerateChecklist:
    def test_returns_string(self):
        assert isinstance(generate_checklist(), str)

    def test_contains_section_b(self):
        assert "SEKCIA B" in generate_checklist()

    def test_contains_section_c(self):
        assert "SEKCIA C" in generate_checklist()

    def test_contains_section_d(self):
        assert "SEKCIA D" in generate_checklist()

    def test_contains_road_section(self):
        assert "PRISTUPOVA CESTA" in generate_checklist()

    def test_contains_parcel_number(self):
        result = generate_checklist(parcel_number="1234/5")
        assert "1234/5" in result

    def test_contains_location(self):
        result = generate_checklist(location="Senec")
        assert "Senec" in result

    def test_contains_kataster_url(self):
        assert "kataster.skgeodesy.sk" in generate_checklist()

    def test_empty_parcel_shows_placeholder(self):
        result = generate_checklist()
        assert "(doplnit)" in result


# ----------------------------------------------------------------
# TestCalculateScore
# ----------------------------------------------------------------

class TestCalculateScore:
    def test_no_issues_is_100(self):
        assert _calculate_score([], []) == 100.0

    def test_one_issue_minus_30(self):
        assert _calculate_score(["problem"], []) == 70.0

    def test_two_issues_minus_60(self):
        assert _calculate_score(["a", "b"], []) == 40.0

    def test_three_issues_gives_10(self):
        assert _calculate_score(["a", "b", "c"], []) == 10.0

    def test_four_issues_gives_0(self):
        assert _calculate_score(["a", "b", "c", "d"], []) == 0.0

    def test_warning_minus_10(self):
        assert _calculate_score([], ["w"]) == 90.0

    def test_issue_and_warning(self):
        assert _calculate_score(["i"], ["w"]) == 60.0

    def test_score_never_below_0(self):
        assert _calculate_score(["a"]*10, ["w"]*10) == 0.0

    def test_score_never_above_100(self):
        assert _calculate_score([], []) <= 100.0

    def test_returns_float(self):
        assert isinstance(_calculate_score([], []), float)


# ----------------------------------------------------------------
# TestEvaluateLvData
# ----------------------------------------------------------------

class TestEvaluateLvData:
    def test_clean_lv_gives_100(self):
        r = evaluate_lv_data(clean_lv())
        assert r.score == 100.0

    def test_clean_lv_is_clean(self):
        assert evaluate_lv_data(clean_lv()).data["clean"] is True

    def test_plomba_v_is_issue(self):
        r = evaluate_lv_data(clean_lv({"plombs": ["V"]}))
        assert r.score < 100.0
        assert any("plomba" in i.lower() or "plomb" in i.lower() for i in r.data["issues"])

    def test_lien_is_issue(self):
        r = evaluate_lv_data(clean_lv({"liens": True}))
        assert any("zalozne" in i.lower() for i in r.data["issues"])

    def test_preemption_is_issue(self):
        r = evaluate_lv_data(clean_lv({"preemption": True}))
        assert any("predkupne" in i.lower() for i in r.data["issues"])

    def test_usufruct_is_issue(self):
        r = evaluate_lv_data(clean_lv({"usufruct": True}))
        assert any("dozitia" in i.lower() for i in r.data["issues"])

    def test_unknown_easement_is_warning(self):
        r = evaluate_lv_data(clean_lv({"unknown_easement": True}))
        assert len(r.data["warnings"]) > 0
        assert len(r.data["issues"]) == 0

    def test_too_many_co_owners_is_issue(self):
        r = evaluate_lv_data(clean_lv({"co_owners": 5}))
        assert any("spoluvlastnikov" in i.lower() for i in r.data["issues"])

    def test_register_e_fraction_too_small_is_issue(self):
        r = evaluate_lv_data(clean_lv({"has_register_e": True, "min_fraction_denominator": 32}))
        assert any("register e" in i.lower() for i in r.data["issues"])

    def test_register_e_acceptable_fraction_ok(self):
        r = evaluate_lv_data(clean_lv({"has_register_e": True, "min_fraction_denominator": 4}))
        assert all("register e" not in i.lower() for i in r.data["issues"])

    def test_spf_owner_is_issue(self):
        r = evaluate_lv_data(clean_lv({"spf_owner": True}))
        assert any("spf" in i.lower() for i in r.data["issues"])

    def test_unknown_owners_is_issue(self):
        r = evaluate_lv_data(clean_lv({"unknown_owners": True}))
        assert any("vlastnici" in i.lower() for i in r.data["issues"])

    def test_no_road_easement_is_warning(self):
        r = evaluate_lv_data(clean_lv({"road_has_easement": False}))
        assert len(r.data["warnings"]) > 0

    def test_parcel_number_in_data(self):
        r = evaluate_lv_data(clean_lv(), parcel_number="1234/5")
        assert r.data["parcel_number"] == "1234/5"

    def test_source_is_set(self):
        assert evaluate_lv_data(clean_lv()).source == "cadastral_service"

    def test_multiple_issues_cumulative_penalty(self):
        lv = clean_lv({"liens": True, "preemption": True})
        r = evaluate_lv_data(lv)
        assert r.score == pytest.approx(40.0)

    def test_returns_service_result(self):
        assert isinstance(evaluate_lv_data(clean_lv()), ServiceResult)


# ----------------------------------------------------------------
# TestCheckFunction
# ----------------------------------------------------------------

class TestCheckFunction:
    def test_no_data_returns_checklist_mode(self):
        r = check()
        assert r.data["mode"] == "checklist"

    def test_no_data_score_is_50(self):
        r = check()
        assert r.score == 50.0

    def test_no_data_ok_is_true(self):
        r = check()
        assert r.ok is True

    def test_no_data_awaiting_verification(self):
        r = check()
        assert r.data["awaiting_manual_verification"] is True

    def test_no_data_checklist_is_string(self):
        r = check()
        assert isinstance(r.data["checklist"], str)

    def test_with_clean_lv_returns_evaluated_mode(self):
        r = check(lv_data=clean_lv())
        assert r.data["mode"] == "evaluated"

    def test_with_clean_lv_score_100(self):
        r = check(lv_data=clean_lv())
        assert r.score == 100.0

    def test_with_issue_lv_score_below_100(self):
        r = check(lv_data=clean_lv({"liens": True}))
        assert r.score < 100.0

    def test_parcel_number_passed_to_checklist(self):
        r = check(parcel_number="9999/1")
        assert "9999/1" in r.data["checklist"]

    def test_source_is_cadastral_service(self):
        assert check().source == "cadastral_service"

    def test_returns_service_result(self):
        assert isinstance(check(), ServiceResult)
