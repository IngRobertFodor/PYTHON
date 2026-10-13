"""
signals.py — Investičné signály (príležitosti + riziká)
========================================================
Generuje pomenované investičné tézy z GIS výsledkov a prelim dát.

Dve fázy:
  - preliminary_signals(parcel)  — 0 HTTP, z inzerátových dát
  - gis_signals(parcel)          — po plnom GIS scoringu

Každý signál:
  { "kod": str, "typ": "PRILEZITOST"|"RIZIKO",
    "nazov": str, "dovod": str, "dovera": float 0.0-1.0 }

Prahy sa čítajú z config/criteria.yaml sekcia signals (s fallback defaults).
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.parcel import Parcel

_DRAZOBNE_SOURCES = {"ske_drazobne_vyhlasky", "notarske_drazby", "obchodny_vestnik"}
_INZERAT_SOURCES  = {"nehnutelnosti_sk", "topreality_sk", "reality_sk"}

_DEFAULTS = {
    "blizko_ba_km":                   25,
    "prilis_daleko_km":               82,
    "cena_podozriva_ppsm":           1.5,
    "drazba_max_eur":             200000,
    "preklasifikacia_min_bpej_class":  5,
    "lacne_vynatie_min_bpej_class":    7,
    "podhodnotene_max_ratio":       0.30,
}


def _cfg() -> dict:
    try:
        from config_loader import get_criteria
        return {**_DEFAULTS, **get_criteria().get("signals", {})}
    except Exception:
        return dict(_DEFAULTS)


def _s(kod: str, typ: str, nazov: str, dovod: str, dovera: float) -> dict:
    return {"kod": kod, "typ": typ, "nazov": nazov,
            "dovod": dovod, "dovera": round(float(dovera), 2)}


# ----------------------------------------------------------------
# Prelim signály (0 HTTP)
# ----------------------------------------------------------------

def preliminary_signals(parcel: "Parcel") -> list[dict]:
    """Signály dostupné ihneď po scrape — len z inzerátových dát."""
    cfg    = _cfg()
    result = []
    price  = parcel.price_eur
    area   = parcel.area_sqm
    ppsm   = parcel.price_per_sqm or (price / area if price > 0 and area > 0 else 0.0)
    source = parcel.source_portal

    # BLIZKO_BA / PRILIS_DALEKO
    try:
        from services.scoring_service import _estimate_distance_km
        km     = _estimate_distance_km(parcel.location_text)
        blizko = float(cfg["blizko_ba_km"])
        daleko = float(cfg["prilis_daleko_km"])
        if km is not None:
            if km <= blizko:
                result.append(_s("BLIZKO_BA", "PRILEZITOST",
                    "Blízko Bratislavy",
                    f"{km:.0f} km od BA (limit {blizko:.0f} km)",
                    0.9 if km <= blizko * 0.6 else 0.7))
            elif km > daleko:
                result.append(_s("PRILIS_DALEKO", "RIZIKO",
                    "Príliš ďaleko od BA",
                    f"{km:.0f} km od BA (max {daleko:.0f} km)", 0.7))
    except Exception:
        pass

    # CENA_PODOZRIVA
    podozriva = float(cfg["cena_podozriva_ppsm"])
    if source in _INZERAT_SOURCES and 0 < ppsm < podozriva:
        result.append(_s("CENA_PODOZRIVA", "RIZIKO",
            "Podozrivo nízka cena",
            f"{ppsm:.2f} €/m² — možná parsovacia chyba (< {podozriva} €/m²)", 0.8))

    # DRAZBA_PODHODNOTENA
    if source in _DRAZOBNE_SOURCES and 0 < price <= float(cfg["drazba_max_eur"]):
        result.append(_s("DRAZBA_PODHODNOTENA", "PRILEZITOST",
            "Dražba — potenciálne podhodnotené",
            f"{source} za {price:,.0f} € — dražby bývajú pod trhom", 0.6))

    return result


# ----------------------------------------------------------------
# GIS signály (po plnom scoringu)
# ----------------------------------------------------------------

def gis_signals(parcel: "Parcel") -> list[dict]:
    """
    Signály po plnom GIS scoringu — čerpá z parcel.results.

    Presné kľúče podľa reálnych ServiceResult.data z každej služby:
      bpej_service:      protection_class, estimated_odvody_eur_per_m2
      zbgis_service:     is_agricultural, is_buildable, druh_pozemku
      overpass_service:  village_position.position, direct_access.level
                         electricity.distance_m, road.distance_m
      flood_service:     in_flood_zone_q100
      protected_service: in_natura2000, in_chko, in_npr_pr, in_np
      price_analysis:    price_ratio, local_avg_per_sqm, price_per_sqm
    """
    cfg    = _cfg()
    result = []

    def _d(name: str) -> dict:
        r = parcel.get_result(name)
        return r.data if r and r.ok else {}

    bpej_d      = _d("bpej_service")
    overpass_d  = _d("overpass_service")
    zbgis_d     = _d("zbgis_service")
    flood_d     = _d("flood_service")
    protected_d = _d("protected_service")
    price_d     = _d("price_analysis_service")

    # Správne kľúče po kontrole zdrojového kódu každej služby
    bpej_class = int(bpej_d.get("protection_class", 0))
    is_agri    = bool(zbgis_d.get("is_agricultural", False))
    # overpass: vnorené dicts (village_position, direct_access)
    position   = (overpass_d.get("village_position") or {}).get("position", "")
    access     = (overpass_d.get("direct_access")    or {}).get("level",    "")
    odvody     = float(bpej_d.get("estimated_odvody_eur_per_m2", -1))
    # vzdialenosti pre zasietovanie (pre Blok 2)
    elec_dist_m = float((overpass_d.get("electricity") or {}).get("distance_m", 9999))
    road_dist_m = float((overpass_d.get("road")        or {}).get("distance_m", 9999))

    # --- PREKLASIFIKACIA ---
    # Orná pôda na OKRAJI dediny s PRIAMOU/CIASTOCNOU dostupnosťou + nízka bonita
    if (is_agri and position == "OKRAJ"
            and access in ("PRIAMA", "CIASTOCNA")
            and bpej_class >= int(cfg["preklasifikacia_min_bpej_class"])):
        dovod = (
            f"Poľnohospodárska pôda, poloha OKRAJ dediny, "
            f"prístup {access}, BPEJ trieda {bpej_class} "
            f"(odvody ≈ {odvody:.2f} €/m²)"
        )
        result.append(_s("PREKLASIFIKACIA", "PRILEZITOST",
            "Kandidát na preklasifikáciu (pole → stavebný)",
            dovod, 0.8 if access == "PRIAMA" else 0.6))

    # --- LACNE_VYNATIE ---
    # Poľnohosp. pôda s BPEJ trieda ≥ 7 (odvody ≤ 0.10 €/m²) = lacné vyňatie
    if is_agri and bpej_class >= int(cfg["lacne_vynatie_min_bpej_class"]) and odvody >= 0:
        result.append(_s("LACNE_VYNATIE", "PRILEZITOST",
            "Lacné vyňatie z PPF",
            f"BPEJ trieda {bpej_class}, odvody ≈ {odvody:.2f} €/m²", 0.9))

    # --- DRAHE_VYNATIE ---
    # BPEJ trieda 1-4 = vysoko chránená pôda = drahé vyňatie (tisíce €/m²)
    if is_agri and 0 < bpej_class <= 4:
        odvody_s = f"{odvody:.2f} €/m²" if odvody >= 0 else "neznáme"
        result.append(_s("DRAHE_VYNATIE", "RIZIKO",
            "Drahé vyňatie z PPF",
            f"BPEJ trieda {bpej_class} (vysoko chránená pôda), odvody ≈ {odvody_s}",
            0.9))

    # --- PODHODNOTENE ---
    # price_analysis vracia price_ratio (parcel/local_avg) a local_avg_per_sqm
    price_ratio     = float(price_d.get("price_ratio", 1.0))
    local_avg_ppsm  = float(price_d.get("local_avg_per_sqm", 0))
    par_ppsm        = float(price_d.get("price_per_sqm", 0)) or parcel.price_per_sqm
    max_ratio       = float(cfg["podhodnotene_max_ratio"])   # default 0.30
    if local_avg_ppsm > 0 and par_ppsm > 0 and price_ratio <= max_ratio:
        result.append(_s("PODHODNOTENE", "PRILEZITOST",
            "Výrazne pod trhom",
            f"{par_ppsm:.0f} €/m² vs. local avg {local_avg_ppsm:.0f} €/m² "
            f"(ratio {price_ratio:.2f}, limit {max_ratio})",
            0.7))

    # --- ZAPLAVA ---
    # flood_service vracia in_flood_zone_q100 (nie flood_zone_q100!)
    if flood_d.get("in_flood_zone_q100", False):
        result.append(_s("ZAPLAVA", "RIZIKO",
            "Záplavová zóna Q100",
            "SHMU WMS: pozemok leží v záplavovej zóne 100-ročnej vody", 0.9))

    # --- CHRANENE_UZEMIE ---
    # protected_service vracia in_natura2000, in_chko, in_npr_pr, in_np
    # VVN/VTL: overpass nerozlišuje typ napätia → nie je spoľahlivé, vynechané
    hits = []
    if protected_d.get("in_natura2000"): hits.append("Natura 2000")
    if protected_d.get("in_chko"):       hits.append("CHKO")
    if protected_d.get("in_npr_pr"):     hits.append("NPR/PR rezervácia")
    if protected_d.get("in_np"):         hits.append("Národný park")
    if hits:
        result.append(_s("CHRANENE_UZEMIE", "RIZIKO",
            "Chránené / obmedzené územie", ", ".join(hits), 0.9))

    return result

    return result


# ----------------------------------------------------------------
# Merge (prelim + GIS, GIS má prednosť)
# ----------------------------------------------------------------

def merge_signals(prelim: list[dict], gis: list[dict]) -> list[dict]:
    """Zlúči prelim + GIS signály — GIS prepíše prelim s rovnakým kódom."""
    by_kod = {s["kod"]: s for s in prelim}
    for s in gis:
        by_kod[s["kod"]] = s
    return list(by_kod.values())
