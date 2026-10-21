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
    # B1 — história cien
    "ponuka_dlho_days":              120,  # inzerát starší → DLHO_V_PONUKE
    "pokles_min_pct":                5.0,  # min. pokles ceny → CENA_KLESA
    "horice_dlho_days":              180,  # kombinovaný prah → HORICE
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
# B1 — Signály histórie cien (motivovaný predajca)
# ----------------------------------------------------------------

def history_signals(parcel: "Parcel") -> list[dict]:
    """Signály z histórie cien a času na trhu.

    Vstupy z parcel (plní scrape_routes po save_run / z DB load):
      parcel.listing_age_days  — počet dní od first_seen
      parcel.price_drop_pct    — % pokles od prvej ceny (pozitívne = zlacnelo)
      parcel.price_history     — [{date, price_eur}, ...]

    Signály:
      DLHO_V_PONUKE  — inzerát visí dlhšie ako ponuka_dlho_days
      CENA_KLESA     — cena klesla o pokles_min_pct alebo viac
      HORICE         — kombinácia: DLHO + CENA_KLESA + výrazný pokles
                       → silný signál motivovaného predajcu
    """
    cfg      = _cfg()
    result   = []
    age_days = int(parcel.listing_age_days or 0)
    drop_pct = float(parcel.price_drop_pct or 0.0)
    history  = parcel.price_history or []

    dlho_prah  = int(cfg.get("ponuka_dlho_days", 120))
    pokles_pct = float(cfg.get("pokles_min_pct",   5.0))
    horice_dni = int(cfg.get("horice_dlho_days",  180))

    # Pomocné texty
    def _age_txt(days: int) -> str:
        if days >= 30:
            months = days // 30
            return f"{months} mes." if months < 12 else f"{months // 12} r. {months % 12} mes."
        return f"{days} dní"

    def _drop_txt(pct: float, hist: list) -> str:
        if len(hist) >= 2:
            p0  = hist[0]["price_eur"]
            p1  = hist[-1]["price_eur"]
            eur = p0 - p1
            return f"−{pct:.1f} % (z {p0:,.0f} → {p1:,.0f} €, ušetrenie {eur:,.0f} €)"
        return f"−{pct:.1f} %"

    is_dlho  = age_days >= dlho_prah
    is_klesa = drop_pct >= pokles_pct

    # --- HORICE (kombinovaný super-signál, má prednosť pred DLHO aj CENA_KLESA) ---
    if is_dlho and is_klesa and age_days >= horice_dni:
        dovod = (
            f"V ponuke {_age_txt(age_days)}, cena klesla {_drop_txt(drop_pct, history)}. "
            f"Silne motivovaný predajca — výrazný priestor na vyjednávanie."
        )
        result.append(_s("HORICE", "PRILEZITOST",
            "🔥 Horúce — motivovaný predajca",
            dovod, min(0.95, 0.7 + age_days / 1000)))
        return result

    # --- DLHO_V_PONUKE ---
    if is_dlho:
        dovera = min(0.9, 0.6 + age_days / 1000)
        dovod  = (
            f"V ponuke {_age_txt(age_days)} (limit {dlho_prah} dní). "
            f"Motivovaný predajca — priestor na vyjednávanie."
        )
        result.append(_s("DLHO_V_PONUKE", "PRILEZITOST",
            f"⏳ Dlho v ponuke ({_age_txt(age_days)})",
            dovod, round(dovera, 2)))

    # --- CENA_KLESA ---
    if is_klesa:
        n_poklesov = sum(
            1 for i in range(1, len(history))
            if history[i]["price_eur"] < history[i - 1]["price_eur"]
        )
        pokles_str = _drop_txt(drop_pct, history)
        krat_str   = f"{n_poklesov}× znížená" if n_poklesov > 1 else "znížená"
        dovod      = (
            f"Cena {krat_str}: {pokles_str}. "
            f"Predajca prichádza k realite trhu."
        )
        dovera = min(0.9, 0.65 + drop_pct / 100)
        result.append(_s("CENA_KLESA", "PRILEZITOST",
            f"🏷️ Cena klesla −{drop_pct:.1f} %",
            dovod, round(dovera, 2)))

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
