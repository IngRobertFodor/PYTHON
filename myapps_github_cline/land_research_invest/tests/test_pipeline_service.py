"""Testy - Pipeline sluzba (orchestrator)
=========================================
Testuje kompletny tok analyzy pozemku: geocoding, GIS sluzby,
scoring, cadastral checklist a report.
100% offline - vsetky HTTP sluzby su mocknutelne.
"""

import pytest
from unittest.mock import patch, MagicMock
from models.parcel  import Parcel
from models.result  import ServiceResult
from services.pipeline_service import (
    analyze_parcel,
    ensure_coordinates,
    run_gis_services,
    run_price_service,
    build_final_report,
    _service_map,
)


# ----------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------

def make_parcel(**kw):
    """Parcel s GPS suradnicami (Senec) + rozumnymi defaults."""
    defaults = dict(
        title="Test pozemok Senec",
        url="https://example.com/test",
        location_text="Senec, Slovakia",
        parcel_number="1234/5",
        price_eur=35000.0,
        area_sqm=800.0,
        lat=48.219,
        lon=17.397,
    )
    defaults.update(kw)
    return Parcel(**defaults)


def ok_result(source, score=80.0, data=None):
    return ServiceResult(ok=True, score=score,
                         data=data or {}, source=source)


def err_result(source, msg="API chyba"):
    return ServiceResult.error_result(source, msg)


def skip_result(source):
    return ServiceResult.skip_result(source, "flag=false")


MODULE = "services.pipeline_service"


# ----------------------------------------------------------------
# TestServiceMap
# ----------------------------------------------------------------

class TestServiceMap:
    def test_returns_list(self):
        assert isinstance(_service_map(), list)

    def test_has_7_entries(self):
        assert len(_service_map()) == 7

    def test_each_entry_is_tuple_of_4(self):
        for entry in _service_map():
            assert len(entry) == 4

    def test_all_sources_are_strings(self):
        for _, source, _, _ in _service_map():
            assert isinstance(source, str) and source

    def test_all_callables_are_callable(self):
        for _, _, fn, _ in _service_map():
            assert callable(fn)

    def test_distance_service_present(self):
        sources = [s for _, s, _, _ in _service_map()]
        assert "distance_service" in sources

    def test_flood_service_present(self):
        sources = [s for _, s, _, _ in _service_map()]
        assert "flood_service" in sources

    def test_zbgis_service_present(self):
        sources = [s for _, s, _, _ in _service_map()]
        assert "zbgis_service" in sources


# ----------------------------------------------------------------
# TestEnsureCoordinates
# ----------------------------------------------------------------

class TestEnsureCoordinates:
    def test_skips_geocoding_when_coords_present(self):
        p = make_parcel(lat=48.2, lon=17.1)
        with patch(MODULE + "._geo.check") as mock_geo:
            result = ensure_coordinates(p)
            mock_geo.assert_not_called()
            assert result is True

    def test_calls_geocoding_when_lat_zero(self):
        p = make_parcel(lat=0.0, lon=0.0)
        geo_r = ok_result("geocoding_service", 100.0,
                           data={"lat": 48.2, "lon": 17.3})
        with patch(MODULE + "._geo.check", return_value=geo_r):
            result = ensure_coordinates(p)
            assert result is True
            assert p.lat == pytest.approx(48.2)
            assert p.lon == pytest.approx(17.3)

    def test_geocoding_result_added_to_parcel(self):
        p = make_parcel(lat=0.0, lon=0.0)
        geo_r = ok_result("geocoding_service", 100.0,
                           data={"lat": 48.2, "lon": 17.3})
        with patch(MODULE + "._geo.check", return_value=geo_r):
            ensure_coordinates(p)
            assert "geocoding_service" in p.results

    def test_failed_geocoding_returns_false(self):
        p = make_parcel(lat=0.0, lon=0.0)
        with patch(MODULE + "._geo.check",
                   return_value=err_result("geocoding_service")):
            result = ensure_coordinates(p)
            assert result is False

    def test_geocoding_exception_returns_false(self):
        p = make_parcel(lat=0.0, lon=0.0)
        with patch(MODULE + "._geo.check", side_effect=RuntimeError("timeout")):
            result = ensure_coordinates(p)
            assert result is False

    def test_empty_address_returns_false(self):
        p = make_parcel(lat=0.0, lon=0.0, location_text="", title="")
        result = ensure_coordinates(p)
        assert result is False
        assert "geocoding_service" in p.results


# ----------------------------------------------------------------
# TestRunGisServices
# ----------------------------------------------------------------

class TestRunGisServices:
    def _all_ok_patch(self):
        """Context manager: vsetky 7 GIS sluzieb vracia ok_result."""
        patches = {}
        for _, source, _, _ in _service_map():
            mod_attr = source.replace("_service", "")
            # mapovanie source -> modul alias v pipeline_service
            svc_map = {
                "distance_service":  "_dist",
                "flood_service":     "_flood",
                "terrain_service":   "_terrain",
                "bpej_service":      "_bpej",
                "overpass_service":  "_overpass",
                "protected_service": "_protected",
                "zbgis_service":     "_zbgis",
            }
            alias = svc_map.get(source, source)
            patches[source] = patch(
                f"{MODULE}.{alias}.check",
                return_value=ok_result(source)
            )
        return patches

    def test_all_services_added_to_results(self):
        p = make_parcel()
        patches = self._all_ok_patch()
        with patch(MODULE + "._dist.check",      return_value=ok_result("distance_service")), \
             patch(MODULE + "._flood.check",     return_value=ok_result("flood_service")), \
             patch(MODULE + "._terrain.check",   return_value=ok_result("terrain_service")), \
             patch(MODULE + "._bpej.check",      return_value=ok_result("bpej_service")), \
             patch(MODULE + "._overpass.check",  return_value=ok_result("overpass_service")), \
             patch(MODULE + "._protected.check", return_value=ok_result("protected_service")), \
             patch(MODULE + "._zbgis.check",     return_value=ok_result("zbgis_service")):
            run_gis_services(p)
        sources = set(p.results.keys())
        for _, source, _, _ in _service_map():
            assert source in sources, f"{source} chyba v results"

    def test_exception_adds_error_result(self):
        p = make_parcel()
        with patch(MODULE + "._dist.check",      side_effect=RuntimeError("siet")), \
             patch(MODULE + "._flood.check",     return_value=ok_result("flood_service")), \
             patch(MODULE + "._terrain.check",   return_value=ok_result("terrain_service")), \
             patch(MODULE + "._bpej.check",      return_value=ok_result("bpej_service")), \
             patch(MODULE + "._overpass.check",  return_value=ok_result("overpass_service")), \
             patch(MODULE + "._protected.check", return_value=ok_result("protected_service")), \
             patch(MODULE + "._zbgis.check",     return_value=ok_result("zbgis_service")):
            run_gis_services(p)
        dist_r = p.results.get("distance_service")
        assert dist_r is not None
        assert dist_r.ok is False

    def test_exception_does_not_stop_pipeline(self):
        p = make_parcel()
        with patch(MODULE + "._dist.check",      side_effect=RuntimeError("siet")), \
             patch(MODULE + "._flood.check",     return_value=ok_result("flood_service")), \
             patch(MODULE + "._terrain.check",   return_value=ok_result("terrain_service")), \
             patch(MODULE + "._bpej.check",      return_value=ok_result("bpej_service")), \
             patch(MODULE + "._overpass.check",  return_value=ok_result("overpass_service")), \
             patch(MODULE + "._protected.check", return_value=ok_result("protected_service")), \
             patch(MODULE + "._zbgis.check",     return_value=ok_result("zbgis_service")):
            run_gis_services(p)
        # ostatne sluzby stale v results aj napriek vynimke v dist
        assert "flood_service" in p.results
        assert "bpej_service"  in p.results


# ----------------------------------------------------------------
# TestRunPriceService
# ----------------------------------------------------------------

class TestRunPriceService:
    def test_price_result_added(self):
        p = make_parcel()
        p.add_result(ok_result("distance_service", 80.0,
                                data={"distance_km": 28.0}))
        with patch(MODULE + "._price.check",
                   return_value=ok_result("price_analysis_service")):
            run_price_service(p)
        assert "price_analysis_service" in p.results

    def test_uses_distance_from_results(self):
        p = make_parcel()
        p.add_result(ok_result("distance_service", 80.0,
                                data={"distance_km": 42.0}))
        with patch(MODULE + "._price.check",
                   return_value=ok_result("price_analysis_service")) as mock_p:
            run_price_service(p)
            call_kwargs = mock_p.call_args[1]
            assert call_kwargs["distance_km"] == pytest.approx(42.0)

    def test_fallback_distance_when_no_dist_service(self):
        p = make_parcel()  # ziadny distance_service result
        with patch(MODULE + "._price.check",
                   return_value=ok_result("price_analysis_service")) as mock_p:
            run_price_service(p)
            call_kwargs = mock_p.call_args[1]
            assert call_kwargs["distance_km"] == pytest.approx(35.0)

    def test_exception_adds_error_result(self):
        p = make_parcel()
        with patch(MODULE + "._price.check", side_effect=ValueError("bad")):
            run_price_service(p)
        r = p.results.get("price_analysis_service")
        assert r is not None and r.ok is False


# ----------------------------------------------------------------
# TestBuildFinalReport
# ----------------------------------------------------------------

class TestBuildFinalReport:
    def test_report_added_to_results(self):
        p = make_parcel()
        p.final_score = 75.0
        p.recommendation = "INVESTIGATE"
        with patch(MODULE + "._report.generate_report",
                   return_value=ok_result("report_service", 75.0)):
            build_final_report(p)
        assert "report_service" in p.results

    def test_returns_service_result(self):
        p = make_parcel()
        p.final_score = 75.0
        p.recommendation = "INVESTIGATE"
        with patch(MODULE + "._report.generate_report",
                   return_value=ok_result("report_service", 75.0)) as mock_r:
            result = build_final_report(p)
        assert isinstance(result, ServiceResult)

    def test_exception_adds_error_result(self):
        p = make_parcel()
        with patch(MODULE + "._report.generate_report",
                   side_effect=RuntimeError("chyba")):
            result = build_final_report(p)
        assert result.ok is False
        assert "report_service" in p.results


# ----------------------------------------------------------------
# TestAnalyzeParcel - end-to-end flow
# ----------------------------------------------------------------

def _patch_all(score=82.0, recommendation="INVESTIGATE"):
    """
    Context manazery pre kompletny mock vsetkych online zavislosti.
    Vracia dict {nazov: patch} - pouzit ako nested with.
    """
    gis_results = {
        "distance_service":  ok_result("distance_service",  85.0, {"distance_km": 28.0}),
        "flood_service":     ok_result("flood_service",     100.0),
        "terrain_service":   ok_result("terrain_service",   80.0),
        "bpej_service":      ok_result("bpej_service",      75.0),
        "overpass_service":  ok_result("overpass_service",  80.0),
        "protected_service": ok_result("protected_service", 90.0),
        "zbgis_service":     ok_result("zbgis_service",     85.0),
    }
    price_r  = ok_result("price_analysis_service", 88.0)
    cad_r    = ok_result("cadastral_service",       50.0,
                          {"mode": "checklist", "awaiting_manual_verification": True})
    report_r = ok_result("report_service",          score,
                          {"text_report": "OK", "recommendation": recommendation})

    return {
        "_dist":      patch(MODULE + "._dist.check",      return_value=gis_results["distance_service"]),
        "_flood":     patch(MODULE + "._flood.check",     return_value=gis_results["flood_service"]),
        "_terrain":   patch(MODULE + "._terrain.check",   return_value=gis_results["terrain_service"]),
        "_bpej":      patch(MODULE + "._bpej.check",      return_value=gis_results["bpej_service"]),
        "_overpass":  patch(MODULE + "._overpass.check",  return_value=gis_results["overpass_service"]),
        "_protected": patch(MODULE + "._protected.check", return_value=gis_results["protected_service"]),
        "_zbgis":     patch(MODULE + "._zbgis.check",     return_value=gis_results["zbgis_service"]),
        "_price":     patch(MODULE + "._price.check",     return_value=price_r),
        "_cadastral": patch(MODULE + "._cadastral.check", return_value=cad_r),
        "_report":    patch(MODULE + "._report.generate_report", return_value=report_r),
    }


class TestAnalyzeParcel:
    def _run(self, score=82.0, recommendation="INVESTIGATE", **parcel_kw):
        p = make_parcel(**parcel_kw)
        patches = _patch_all(score, recommendation)
        with patches["_dist"], patches["_flood"], patches["_terrain"], \
             patches["_bpej"], patches["_overpass"], patches["_protected"], \
             patches["_zbgis"], patches["_price"], patches["_cadastral"], \
             patches["_report"]:
            analyze_parcel(p)
        return p

    def test_returns_parcel(self):
        p = self._run()
        assert isinstance(p, Parcel)

    def test_results_contains_distance(self):
        p = self._run()
        assert "distance_service" in p.results

    def test_results_contains_flood(self):
        p = self._run()
        assert "flood_service" in p.results

    def test_results_contains_price(self):
        p = self._run()
        assert "price_analysis_service" in p.results

    def test_final_score_is_set(self):
        p = self._run(score=82.0)
        assert p.final_score > 0.0

    def test_recommendation_is_set(self):
        p = self._run(recommendation="INVESTIGATE")
        assert p.recommendation != ""

    def test_report_in_results(self):
        p = self._run()
        assert "report_service" in p.results

    def test_high_score_triggers_cadastral(self):
        # score 82 >= 70 -> cadastral checklist
        p = self._run(score=82.0)
        assert "cadastral_service" in p.results

    def test_low_score_skips_cadastral(self):
        # score pod pragom 70 -> cadastral sa nevola
        patches = _patch_all(score=40.0)
        p = make_parcel()
        with patches["_dist"], patches["_flood"], patches["_terrain"], \
             patches["_bpej"], patches["_overpass"], patches["_protected"], \
             patches["_zbgis"], patches["_price"], patches["_cadastral"] as mock_cad, \
             patches["_report"]:
            # scoring_service nastavime manualne aby sme mali niske skore
            with patch(MODULE + "._scoring.score_parcel",
                       side_effect=lambda p: setattr(p, "final_score", 40.0) or p), \
                 patch(MODULE + "._scoring.needs_cadastral_checklist",
                       return_value=False):
                analyze_parcel(p)
            mock_cad.assert_not_called()

    def test_geocoding_not_called_when_coords_present(self):
        p = make_parcel(lat=48.2, lon=17.1)
        patches = _patch_all()
        with patches["_dist"], patches["_flood"], patches["_terrain"], \
             patches["_bpej"], patches["_overpass"], patches["_protected"], \
             patches["_zbgis"], patches["_price"], patches["_cadastral"], \
             patches["_report"]:
            with patch(MODULE + "._geo.check") as mock_geo:
                analyze_parcel(p)
                mock_geo.assert_not_called()
