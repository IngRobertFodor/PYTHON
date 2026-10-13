"""
rezoning_service.py — Kvantifikácia zisku z preklasifikácie pôdy
=================================================================
Odhaduje potenciálny zisk: kúpiť poľnohosp. pôdu → preklasifikovať → predať.

POZOR: Orientačné ±30-50 %. Nie právny ani finančný poradca.
0 HTTP, 100 % offline, testovateľné.
"""

from models.parcel import Parcel
from config_loader import get_criteria

_ZASIETOVANIE_EUR_PER_M = {
    "elektrina": 100.0,
    "cesta":     120.0,
}

# Fallback regionálne ceny stavebných pozemkov (EUR/m2, BA kraj 2024-2026)
_DEFAULT_STAVEBNE_CENY = [
    (15,  180.0),
    (30,  120.0),
    (50,   75.0),
    (85,   45.0),
    (999,  30.0),
]


def estimate_rezoning_profit(parcel: Parcel) -> Parcel:
    """
    Odhaduje zisk z preklasifikácie.
    Nastaví: rezoning_profit_eur, rezoning_cost_eur,
             rezoning_value_eur, rezoning_breakdown.
    """
    area       = parcel.area_sqm
    kupna_cena = parcel.price_eur

    bpej_d     = _get_data(parcel, "bpej_service")
    overpass_d = _get_data(parcel, "overpass_service")
    dist_d     = _get_data(parcel, "distance_service")

    # Vzdialenosť od BA
    dist_km = float(dist_d.get("distance_km", 0)) if dist_d else 0.0
    if dist_km <= 0:
        try:
            from services.scoring_service import _estimate_distance_km
            dist_km = _estimate_distance_km(parcel.location_text) or 50.0
        except Exception:
            dist_km = 50.0

    # Náklady na vyňatie
    odvody_per_m2  = float(bpej_d.get("estimated_odvody_eur_per_m2", 0.5)
                           if bpej_d else 0.5)
    naklad_vynatie = odvody_per_m2 * area if area > 0 else 0.0

    # Náklady na zasieťovanie (len ak > 10 m)
    elec_dist_m = float((overpass_d.get("electricity") or {}).get("distance_m", 100)
                        if overpass_d else 100)
    road_dist_m = float((overpass_d.get("road") or {}).get("distance_m", 50)
                        if overpass_d else 50)
    naklad_elec  = max(0.0, elec_dist_m - 10) * _ZASIETOVANIE_EUR_PER_M["elektrina"]
    naklad_cesta = max(0.0, road_dist_m - 10) * _ZASIETOVANIE_EUR_PER_M["cesta"]
    naklad_zasietovanie = naklad_elec + naklad_cesta
    naklad_celkom = naklad_vynatie + naklad_zasietovanie

    # Hodnota ako stavebný pozemok
    stavebna_cena_m2 = _get_stavebna_cena(dist_km)
    hodnota_stavebna = stavebna_cena_m2 * area if area > 0 else 0.0

    # Čistý hrubý zisk
    cisty_zisk = hodnota_stavebna - kupna_cena - naklad_celkom

    # Confidence (podiel vstupov z reálnych GIS dát)
    cf = 0.0
    if bpej_d:         cf += 0.3
    if overpass_d:     cf += 0.2
    if dist_d:         cf += 0.2
    if kupna_cena > 0: cf += 0.3
    confidence = round(cf, 2)

    breakdown = {
        "area_sqm":               area,
        "kupna_cena_eur":         kupna_cena,
        "dist_km":                round(dist_km, 1),
        "bpej_odvody_per_m2":     round(odvody_per_m2, 3),
        "naklad_vynatie_eur":     round(naklad_vynatie, 0),
        "elec_dist_m":            round(elec_dist_m, 0),
        "road_dist_m":            round(road_dist_m, 0),
        "naklad_zasietovanie_eur": round(naklad_zasietovanie, 0),
        "naklad_celkom_eur":      round(naklad_celkom, 0),
        "stavebna_cena_per_m2":   stavebna_cena_m2,
        "hodnota_stavebna_eur":   round(hodnota_stavebna, 0),
        "cisty_zisk_est_eur":     round(cisty_zisk, 0),
        "confidence":             confidence,
        "poznamka": "ORIENTACNE +-30-50%. Nie pravny ani financny poradca.",
    }

    parcel.rezoning_profit_eur = round(cisty_zisk, 0)
    parcel.rezoning_cost_eur   = round(naklad_celkom, 0)
    parcel.rezoning_value_eur  = round(hodnota_stavebna, 0)
    parcel.rezoning_breakdown  = breakdown
    return parcel


def get_stavebna_cena_m2(dist_km: float) -> float:
    """Orientačná cena stavebného pozemku EUR/m2 podľa km od BA."""
    return _get_stavebna_cena(dist_km)


def _get_data(parcel: Parcel, service: str):
    r = parcel.get_result(service)
    return r.data if r and r.ok else None


def _get_stavebna_cena(dist_km: float) -> float:
    try:
        cfg = get_criteria().get("rezoning", {}).get("stavebne_ceny_podla_km", [])
        if cfg:
            for entry in cfg:
                if dist_km <= entry.get("max_km", 999):
                    return float(entry.get("eur_per_m2", 30.0))
    except Exception:
        pass
    for max_km, cena in _DEFAULT_STAVEBNE_CENY:
        if dist_km <= max_km:
            return cena
    return _DEFAULT_STAVEBNE_CENY[-1][1]
