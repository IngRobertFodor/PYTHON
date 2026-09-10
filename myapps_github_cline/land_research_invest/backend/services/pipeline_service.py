"""Pipeline sluzba - Orchestrator analyzy pozemku
=================================================
Spoji vsetky GIS sluzby do jedneho toku.
Zoberie Parcel, prebehne ho cez kazdu sluzbu podla feature flagov
a vrati ho s vyplnenym results{}, final_score a recommendation.

Tok (podla ARCHITEKTURA_DEVELOPER.txt sekcia 3):
  1. ensure_coordinates  -- geocoding ak chybaju lat/lon
  2. run_gis_services    -- 8 GIS sluzieb paralelne (feature flagy)
  3. score_parcel        -- vazene skore 0-100
  4. cadastral check     -- ak skore >= checklist_min_score (70)
  5. build_final_report  -- generuj report

Principy:
  - Vypnuta sluzba  -> ServiceResult.skip_result (neutralne 50)
  - Vynimka sluzby  -> ServiceResult.error_result (pipeline pokracuje)
  - Offline-testov. -> vsetky sluzby su mocknutelne cez unittest.mock
"""

import services.distance_service      as _dist
import services.flood_service         as _flood
import services.terrain_service       as _terrain
import services.bpej_service          as _bpej
import services.overpass_service      as _overpass
import services.protected_service     as _protected
import services.zbgis_service         as _zbgis
import services.price_analysis_service as _price
import services.geocoding_service     as _geo
import services.scoring_service       as _scoring
import services.cadastral_service     as _cadastral
import services.report_service        as _report

from concurrent.futures import ThreadPoolExecutor, as_completed
from models.result  import ServiceResult
from models.parcel  import Parcel
from config_loader  import is_feature_enabled

SERVICE_NAME = "pipeline_service"


# ----------------------------------------------------------------
# Mapovanie: feature_flag -> (modul, zdroj, funkcia na volanie)
# Poradie zodpoveda toku v ARCHITEKTURA sekcia 3.
# ----------------------------------------------------------------

def _service_map():
    """
    Vrati zoznam konfiguracia GIS sluzieb.
    Kazda polozka je tuple:
      (feature_flag, source_name, callable, extra_kwargs_fn)
    extra_kwargs_fn(parcel) -> dict  -- volitelne extra argumenty
    """
    return [
        (
            "use_distance",
            "distance_service",
            _dist.check,
            lambda p: {"lat": p.lat, "lon": p.lon},
        ),
        (
            "use_flood",
            "flood_service",
            _flood.check,
            lambda p: {"lat": p.lat, "lon": p.lon},
        ),
        (
            "use_terrain",
            "terrain_service",
            _terrain.check,
            lambda p: {"lat": p.lat, "lon": p.lon},
        ),
        (
            "use_bpej",
            "bpej_service",
            _bpej.check,
            lambda p: {"lat": p.lat, "lon": p.lon},
        ),
        (
            "use_overpass",
            "overpass_service",
            _overpass.check,
            lambda p: {"lat": p.lat, "lon": p.lon},
        ),
        (
            "use_vvn_vtl",
            "protected_service",
            _protected.check,
            lambda p: {"lat": p.lat, "lon": p.lon},
        ),
        (
            "use_distance",   # ZBGIS bezi ak mame suradnice
            "zbgis_service",
            _zbgis.check,
            lambda p: {"lat": p.lat, "lon": p.lon,
                       "parcel_number": p.parcel_number or None},
        ),
    ]


def ensure_coordinates(parcel):
    """
    Ak parcel.lat == 0 alebo parcel.lon == 0, zavolaj geocoding_service.
    Vysledok ulozi do parcel.lat / parcel.lon a prida result.

    Args:
        parcel: Parcel (modifikuje in-place)
    Returns:
        True ak su suradnice dostupne, False ak geocoding zlyhal
    """
    if parcel.lat != 0.0 and parcel.lon != 0.0:
        return True   # uz mame suradnice

    address = parcel.location_text or parcel.title or ""
    if not address:
        parcel.add_result(
            ServiceResult.error_result(
                "geocoding_service",
                "Chyba adresa: location_text aj title su prazdne"
            )
        )
        return False

    try:
        result = _geo.check(address)
    except Exception as exc:
        parcel.add_result(
            ServiceResult.error_result("geocoding_service", str(exc))
        )
        return False

    parcel.add_result(result)
    if result.ok:
        parcel.lat = result.data.get("lat", 0.0)
        parcel.lon = result.data.get("lon", 0.0)
        return parcel.lat != 0.0 and parcel.lon != 0.0
    return False


def run_gis_services(parcel):
    """
    Prebehne vsetkych 7 GIS sluzieb (okrem price) podla feature flagov.
    Sluzby sa spustaju PARALELNE (ThreadPoolExecutor) -- celkovy cas
    je MAX(jednotlivych casov), nie SUM. GIS servery casto blokuju
    HTTP (timeout 15-30s) -- bez paralelizmu by analyza trvala 120+ s.

    Kazda sluzba:
      - Ak feature flag = False -> skip_result (neutralne 50)
      - Ak vyhodi vynimku       -> error_result (pipeline pokracuje)
      - Inak                    -> vysledok sa prida do parcel.results

    Args:
        parcel: Parcel s vyplnenym lat/lon
    """
    service_map = _service_map()

    # Rozdelit na skip (bez HTTP) a aktivne (s HTTP)
    skip_results = []
    active_items = []
    for flag, source, fn, kwargs_fn in service_map:
        if not is_feature_enabled(flag):
            skip_results.append(
                ServiceResult.skip_result(source, f"{flag}=false")
            )
        else:
            active_items.append((source, fn, kwargs_fn))

    for sr in skip_results:
        parcel.add_result(sr)

    if not active_items:
        return

    # Paralelne HTTP volania
    def _call(source, fn, kwargs_fn):
        try:
            kwargs = kwargs_fn(parcel)
            result = fn(**kwargs)
            result.source = source
            return result
        except Exception as exc:
            return ServiceResult.error_result(source, str(exc))

    with ThreadPoolExecutor(max_workers=len(active_items)) as executor:
        futures = {
            executor.submit(_call, source, fn, kwargs_fn): source
            for source, fn, kwargs_fn in active_items
        }
        for future in as_completed(futures):
            parcel.add_result(future.result())


def run_price_service(parcel):
    """
    Spusti price_analysis_service s datami z parcely.
    Vyzaduje: price_eur, area_sqm a distance_km z distance_service.
    """
    if not is_feature_enabled("use_price_analysis"):
        parcel.add_result(
            ServiceResult.skip_result("price_analysis_service", "use_price_analysis=false")
        )
        return

    dist_r = parcel.results.get("distance_service")
    dist_km = dist_r.data.get("distance_km", 35.0) if (dist_r and dist_r.ok) else 35.0

    try:
        result = _price.check(
            price_eur=parcel.price_eur,
            area_sqm=parcel.area_sqm,
            distance_km=dist_km,
        )
        result.source = "price_analysis_service"
        parcel.add_result(result)
    except Exception as exc:
        parcel.add_result(
            ServiceResult.error_result("price_analysis_service", str(exc))
        )


def build_final_report(parcel):
    """
    Vygeneruje investicny report a ulozi ho do parcel.results.

    Args:
        parcel: Parcel s vyplnenym final_score a results
    Returns:
        ServiceResult z report_service
    """
    try:
        result = _report.generate_report(parcel)
        parcel.add_result(result)
        return result
    except Exception as exc:
        err = ServiceResult.error_result("report_service", str(exc))
        parcel.add_result(err)
        return err


def analyze_parcel(parcel):
    """
    Hlavna funkcia - kompletna analyza pozemku.

    Tok:
      1. Zabezpec GPS suradnice (geocoding ak chybaju)
      2. Spusti vsetkych 7 GIS sluzieb (feature flagy)
      3. Spusti price_analysis_service
      4. Vypocitaj vazene skore (scoring_service)
      5. Ak skore >= checklist_min_score: generuj LV checklist
      6. Generuj investicny report

    Args:
        parcel: Parcel so zakladnymi udajmi z inzeratu
                (title, url, price_eur, area_sqm, location_text)

    Returns:
        Ten isty Parcel s vyplnenymi results, final_score,
        recommendation a reportom.
    """
    # 1. GPS
    ensure_coordinates(parcel)

    # 2. GIS sluzby
    run_gis_services(parcel)

    # 3. Cenova analyza
    run_price_service(parcel)

    # 3b. Vypocitaj price_per_sqm na objekte (pouziva frontend na kartach)
    if parcel.area_sqm and parcel.area_sqm > 0:
        parcel.price_per_sqm = round(parcel.price_eur / parcel.area_sqm, 2)

    # 4. Scoring
    _scoring.score_parcel(parcel)

    # 5. Kataster checklist pre kandidatov nad prahom
    if _scoring.needs_cadastral_checklist(parcel.final_score):
        try:
            cad = _cadastral.check(
                lv_data=None,
                parcel_number=parcel.parcel_number,
                location=parcel.location_text,
            )
            parcel.add_result(cad)
        except Exception as exc:
            parcel.add_result(
                ServiceResult.error_result("cadastral_service", str(exc))
            )

    # 6. Report
    build_final_report(parcel)

    return parcel
