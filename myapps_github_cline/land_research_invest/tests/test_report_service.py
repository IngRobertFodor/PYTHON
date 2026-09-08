"""Testy - Report sluzba
=======================
Testuje vsetky funkcie report_service: summary, breakdown, red_flags,
investment_view, text_report a generate_report.
Cista logika - 100% offline, ziadne HTTP requesty.
"""

import pytest
from models.parcel import Parcel
from models.result import ServiceResult
from services.report_service import (
    generate_report,
    build_summary,
    build_score_breakdown,
    build_red_flags,
    build_investment_view,
    format_text_report,
    _verdict_icon,
)


# ----------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------

def make_parcel(**kw):
    """Vrati Parcel s rozumnymi defaults + overrides."""
    defaults = dict(
        title="Test parcela Senec",
        url="https://example.com/1234",
        location_text="Senec",
        parcel_number="1234/5",
        price_eur=35000.0,
        area_sqm=800.0,
        final_score=75.0,
        recommendation="INVESTIGATE",
    )
    defaults.update(kw)
    return Parcel(**defaults)


def sr(source, score=80.0, ok=True, data=None, error=None):
    """Skrateny konstruktor ServiceResult."""
    return ServiceResult(
        ok=ok, score=score,
        data=data or {},
        error=error,
        source=source,
    )


def parcel_with_distance(dist_km=45.0, **kw):
    p = make_parcel(**kw)
    p.add_result(sr("distance_service", 80.0, data={"distance_km": dist_km}))
    return p


# ----------------------------------------------------------------
# TestVerdictIcon
# ----------------------------------------------------------------

class TestVerdictIcon:
    def test_strong_buy(self):
        assert _verdict_icon("STRONG BUY") == "[**]"

    def test_investigate(self):
        assert _verdict_icon("INVESTIGATE") == "[??]"

    def test_consider(self):
        assert _verdict_icon("CONSIDER") == "[..]"

    def test_skip(self):
        assert _verdict_icon("SKIP") == "[XX]"

    def test_unknown_returns_default(self):
        assert _verdict_icon("WHATEVER") == "[--]"


# ----------------------------------------------------------------
# TestBuildSummary
# ----------------------------------------------------------------

class TestBuildSummary:
    def test_contains_title(self):
        p = make_parcel(title="Pozemok Senec")
        assert build_summary(p)["title"] == "Pozemok Senec"

    def test_price_per_sqm_calculated(self):
        p = make_parcel(price_eur=40000.0, area_sqm=800.0)
        assert build_summary(p)["price_per_sqm"] == pytest.approx(50.0)

    def test_price_per_sqm_zero_area(self):
        p = make_parcel(price_eur=40000.0, area_sqm=0.0)
        assert build_summary(p)["price_per_sqm"] == 0.0

    def test_distance_from_result(self):
        p = parcel_with_distance(dist_km=30.0)
        assert build_summary(p)["distance_km"] == 30.0

    def test_distance_none_without_service(self):
        p = make_parcel()
        assert build_summary(p)["distance_km"] is None

    def test_final_score_present(self):
        p = make_parcel(final_score=88.5)
        assert build_summary(p)["final_score"] == 88.5

    def test_recommendation_present(self):
        p = make_parcel(recommendation="STRONG BUY")
        assert build_summary(p)["recommendation"] == "STRONG BUY"


# ----------------------------------------------------------------
# TestBuildScoreBreakdown
# ----------------------------------------------------------------

class TestBuildScoreBreakdown:
    def test_returns_items_list(self):
        p = make_parcel()
        bd = build_score_breakdown(p)
        assert isinstance(bd["items"], list)

    def test_items_count_equals_weight_keys(self):
        # 8 vah v YAML -> 8 poloziek
        p = make_parcel()
        bd = build_score_breakdown(p)
        assert len(bd["items"]) == 8

    def test_missing_service_has_none_score(self):
        p = make_parcel()  # bez akychkolvek results
        bd = build_score_breakdown(p)
        assert all(item["score"] is None for item in bd["items"])

    def test_missing_service_status_is_missing(self):
        p = make_parcel()
        bd = build_score_breakdown(p)
        assert all(item["status"] == "missing" for item in bd["items"])

    def test_present_service_has_score(self):
        p = make_parcel()
        p.add_result(sr("price_analysis_service", score=90.0))
        bd = build_score_breakdown(p)
        price_item = next(i for i in bd["items"] if i["weight_key"] == "price")
        assert price_item["score"] == 90.0

    def test_present_service_status_ok(self):
        p = make_parcel()
        p.add_result(sr("price_analysis_service", score=90.0))
        bd = build_score_breakdown(p)
        price_item = next(i for i in bd["items"] if i["weight_key"] == "price")
        assert price_item["status"] == "ok"

    def test_skipped_service_status(self):
        p = make_parcel()
        p.add_result(sr("flood_service", score=50.0, data={"skipped": True}))
        bd = build_score_breakdown(p)
        flood_item = next(i for i in bd["items"] if i["weight_key"] == "flood_risk")
        assert flood_item["status"] == "skipped"

    def test_error_service_status(self):
        p = make_parcel()
        p.add_result(sr("flood_service", score=0.0, ok=False, error="timeout"))
        bd = build_score_breakdown(p)
        flood_item = next(i for i in bd["items"] if i["weight_key"] == "flood_risk")
        assert flood_item["status"] == "error"

    def test_contrib_is_score_times_weight(self):
        p = make_parcel()
        p.add_result(sr("price_analysis_service", score=100.0))
        bd = build_score_breakdown(p)
        price_item = next(i for i in bd["items"] if i["weight_key"] == "price")
        expected = round(100.0 * price_item["weight"], 4)
        assert price_item["contrib"] == pytest.approx(expected)

    def test_final_score_matches_parcel(self):
        p = make_parcel(final_score=72.5)
        assert build_score_breakdown(p)["final_score"] == 72.5


# ----------------------------------------------------------------
# TestBuildRedFlags
# ----------------------------------------------------------------

class TestBuildRedFlags:
    def test_clean_parcel_no_flags(self):
        p = make_parcel()
        rf = build_red_flags(p)
        assert rf["blocker_count"] == 0
        assert rf["warning_count"] == 0
        assert rf["has_blockers"] is False

    def test_rejected_service_is_blocker(self):
        p = make_parcel()
        p.add_result(sr("flood_service", score=0.0, ok=False, error="API timeout"))
        rf = build_red_flags(p)
        assert rf["has_blockers"] is True
        assert any("flood_service" in b for b in rf["blockers"])

    def test_skipped_service_not_a_blocker(self):
        p = make_parcel()
        p.add_result(sr("flood_service", score=50.0, data={"skipped": True}))
        rf = build_red_flags(p)
        assert rf["has_blockers"] is False

    def test_flood_zone_is_blocker(self):
        p = make_parcel()
        p.add_result(sr("flood_service", score=0.0, data={"in_flood_zone": True}))
        rf = build_red_flags(p)
        assert any("Q100" in b or "zaplavovej" in b for b in rf["blockers"])

    def test_cadastral_issue_is_blocker(self):
        p = make_parcel()
        p.add_result(sr("cadastral_service", score=70.0,
            data={"mode": "evaluated", "issues": ["Zalozne pravo"], "warnings": []}))
        rf = build_red_flags(p)
        assert any("Zalozne pravo" in b for b in rf["blockers"])

    def test_cadastral_warning_is_warning(self):
        p = make_parcel()
        p.add_result(sr("cadastral_service", score=90.0,
            data={"mode": "evaluated", "issues": [], "warnings": ["Nezname vecne bremeno"]}))
        rf = build_red_flags(p)
        assert rf["blocker_count"] == 0
        assert any("Nezname vecne bremeno" in w for w in rf["warnings"])

    def test_cadastral_checklist_mode_ignored(self):
        # mode=checklist nema issues/warnings -> nema byt bloker
        p = make_parcel()
        p.add_result(sr("cadastral_service", score=50.0,
            data={"mode": "checklist"}))
        rf = build_red_flags(p)
        assert rf["blocker_count"] == 0

    def test_bpej_class_4_is_warning(self):
        p = make_parcel()
        p.add_result(sr("bpej_service", score=60.0,
            data={"protection_class": 4}))
        rf = build_red_flags(p)
        assert any("BPEJ" in w for w in rf["warnings"])

    def test_bpej_class_5_not_warning(self):
        p = make_parcel()
        p.add_result(sr("bpej_service", score=80.0,
            data={"protection_class": 5}))
        rf = build_red_flags(p)
        assert not any("BPEJ" in w for w in rf["warnings"])

    def test_protected_violation_is_blocker(self):
        p = make_parcel()
        p.add_result(sr("protected_service", score=0.0,
            data={"violations": ["VVN linka v ochrannom pasme"], "warnings": []}))
        rf = build_red_flags(p)
        assert any("VVN" in b for b in rf["blockers"])


# ----------------------------------------------------------------
# TestBuildInvestmentView
# ----------------------------------------------------------------

class TestBuildInvestmentView:
    def test_pass_verdict_for_good_parcel(self):
        p = make_parcel(price_eur=35000.0, area_sqm=800.0)
        assert build_investment_view(p)["verdict"] == "PASS"

    def test_over_budget_verdict(self):
        p = make_parcel(price_eur=60000.0, area_sqm=800.0)
        inv = build_investment_view(p)
        assert inv["over_budget"] is True
        assert inv["verdict"] == "OVER_BUDGET"

    def test_over_sqm_verdict(self):
        # 40000 / 200 = 200 EUR/m2 > 100 limit
        p = make_parcel(price_eur=40000.0, area_sqm=200.0)
        inv = build_investment_view(p)
        assert inv["over_sqm_limit"] is True
        assert inv["verdict"] == "OVER_SQM"

    def test_fail_verdict_both_over(self):
        # 60000 EUR budget + 60000/200 = 300 EUR/m2
        p = make_parcel(price_eur=60000.0, area_sqm=200.0)
        assert build_investment_view(p)["verdict"] == "FAIL"

    def test_area_mismatch_too_small(self):
        # 400 m2 < min 600
        p = make_parcel(price_eur=20000.0, area_sqm=400.0)
        inv = build_investment_view(p)
        assert inv["area_ok"] is False
        assert inv["verdict"] == "AREA_MISMATCH"

    def test_area_mismatch_too_large(self):
        # 2000 m2 > max 1500
        p = make_parcel(price_eur=20000.0, area_sqm=2000.0)
        inv = build_investment_view(p)
        assert inv["area_ok"] is False
        assert inv["verdict"] == "AREA_MISMATCH"

    def test_area_ok_in_range(self):
        p = make_parcel(price_eur=35000.0, area_sqm=800.0)
        assert build_investment_view(p)["area_ok"] is True

    def test_price_per_sqm_calculated(self):
        p = make_parcel(price_eur=40000.0, area_sqm=1000.0)
        assert build_investment_view(p)["price_per_sqm"] == pytest.approx(40.0)

    def test_zero_area_safe(self):
        p = make_parcel(price_eur=35000.0, area_sqm=0.0)
        inv = build_investment_view(p)
        assert inv["price_per_sqm"] == 0.0
        assert inv["area_ok"] is False

    def test_limits_read_from_config(self):
        p = make_parcel()
        inv = build_investment_view(p)
        assert inv["max_eur"] == 50000
        assert inv["max_price_per_sqm"] == 100


# ----------------------------------------------------------------
# TestFormatTextReport
# ----------------------------------------------------------------

class TestFormatTextReport:
    def test_returns_string(self):
        assert isinstance(format_text_report(make_parcel()), str)

    def test_contains_score(self):
        p = make_parcel(final_score=75.0)
        assert "75.0" in format_text_report(p)

    def test_contains_recommendation(self):
        p = make_parcel(recommendation="STRONG BUY")
        assert "STRONG BUY" in format_text_report(p)

    def test_contains_price(self):
        p = make_parcel(price_eur=35000.0)
        text = format_text_report(p)
        assert "35" in text

    def test_contains_location(self):
        p = make_parcel(location_text="Senec")
        assert "Senec" in format_text_report(p)

    def test_contains_rozpad_skore(self):
        assert "ROZPAD SKORE" in format_text_report(make_parcel())

    def test_contains_celkove_skore(self):
        assert "CELKOVE SKORE" in format_text_report(make_parcel())

    def test_contains_zakladne_udaje(self):
        assert "ZAKLADNE UDAJE" in format_text_report(make_parcel())

    def test_contains_verdict_line(self):
        assert "VERDICT" in format_text_report(make_parcel())

    def test_red_flags_section_shown_when_blockers(self):
        p = make_parcel()
        p.add_result(sr("flood_service", score=0.0, ok=False, error="API error"))
        assert "RED FLAGS" in format_text_report(p)

    def test_red_flags_section_hidden_when_clean(self):
        p = make_parcel()
        assert "RED FLAGS" not in format_text_report(p)

    def test_contains_icon_for_strong_buy(self):
        p = make_parcel(recommendation="STRONG BUY")
        assert "[**]" in format_text_report(p)

    def test_contains_icon_for_skip(self):
        p = make_parcel(recommendation="SKIP")
        assert "[XX]" in format_text_report(p)


# ----------------------------------------------------------------
# TestGenerateReport
# ----------------------------------------------------------------

class TestGenerateReport:
    def test_returns_service_result(self):
        assert isinstance(generate_report(make_parcel()), ServiceResult)

    def test_score_equals_final_score(self):
        p = make_parcel(final_score=82.0)
        assert generate_report(p).score == pytest.approx(82.0)

    def test_source_is_report_service(self):
        assert generate_report(make_parcel()).source == "report_service"

    def test_ok_is_true(self):
        assert generate_report(make_parcel()).ok is True

    def test_data_has_summary(self):
        assert "summary" in generate_report(make_parcel()).data

    def test_data_has_score_breakdown(self):
        assert "score_breakdown" in generate_report(make_parcel()).data

    def test_data_has_red_flags(self):
        assert "red_flags" in generate_report(make_parcel()).data

    def test_data_has_investment(self):
        assert "investment" in generate_report(make_parcel()).data

    def test_data_has_recommendation(self):
        assert "recommendation" in generate_report(make_parcel()).data

    def test_data_has_text_report(self):
        assert "text_report" in generate_report(make_parcel()).data

    def test_text_report_is_string(self):
        r = generate_report(make_parcel())
        assert isinstance(r.data["text_report"], str)

    def test_strong_buy_parcel(self):
        p = make_parcel(final_score=90.0, recommendation="STRONG BUY")
        r = generate_report(p)
        assert r.score == pytest.approx(90.0)
        assert r.data["recommendation"] == "STRONG BUY"

    def test_skip_parcel(self):
        p = make_parcel(final_score=30.0, recommendation="SKIP")
        r = generate_report(p)
        assert r.data["recommendation"] == "SKIP"
        assert "[XX]" in r.data["text_report"]
