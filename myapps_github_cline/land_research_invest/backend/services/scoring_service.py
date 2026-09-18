"""
Scoring sluzba
==============
Vypocita vazene celkove skore pozemku (0-100) zo vsetkych
ServiceResult-ov nazbieranych validatormi.
Cista logika - bez externe API, 100% offline a testovatelna.
Vahy a prahy sa citaju z config/criteria.yaml.
"""

from models.result import ServiceResult
from models.parcel import Parcel
from config_loader import get_scoring

SERVICE_NAME = "scoring_service"

# Mapovanie: nazov vahy v YAML -> nazov source v results dict
WEIGHT_TO_SOURCE = {
    "price":            "price_analysis_service",
    "distance":         "distance_service",
    "infrastructure":   "overpass_service",
    "legal_proxy":      "cadastral_service",
    "flood_risk":       "flood_service",
    "soil_quality":     "bpej_service",
    "terrain":          "terrain_service",
    "protected_zones":  "protected_service",
}


def score_parcel(parcel: Parcel) -> Parcel:
    """
    Vypocita celkove skore pozemku a nastavi recommendation.
    Modifikuje parcel in-place a vrati ho spat.

    Args:
        parcel: Parcel s vyplnenymi results zo vsetkych sluzieb

    Returns:
        Ten isty Parcel s nastavenym final_score a recommendation
    """
    cfg = get_scoring()
    weights = cfg.get("weights", {})
    thresholds = cfg.get("thresholds", {})

    total_score, total_weight = _calculate_weighted_score(parcel.results, weights)

    parcel.final_score = round(total_score, 2)
    parcel.recommendation = _get_recommendation(total_score, thresholds)
    return parcel


def calculate_weighted_score(results: dict, weights: dict) -> float:
    """
    Verejne dostupna verzia pre priame pouzitie (napr. v testoch).

    Args:
        results: dict {source_name: ServiceResult}
        weights: dict {weight_key: float} zo YAML scoring.weights

    Returns:
        Vazene skore 0.0 - 100.0
    """
    score, _ = _calculate_weighted_score(results, weights)
    return score


def get_recommendation(score: float) -> str:
    """
    Vrati textove odporucanie na zaklade skore a pragov z configu.

    Args:
        score: celkove skore 0-100

    Returns:
        "STRONG BUY" | "INVESTIGATE" | "CONSIDER" | "SKIP"
    """
    cfg = get_scoring()
    thresholds = cfg.get("thresholds", {})
    return _get_recommendation(score, thresholds)


def needs_cadastral_checklist(score: float) -> bool:
    """
    Vrati True ak skore presahuje prah pre generovanie
    katastrálneho checklistu.

    Args:
        score: celkove skore 0-100

    Returns:
        True ak treba vygenerovat checklist
    """
    cfg = get_scoring()
    min_score = cfg.get("checklist_min_score", 70)
    return score >= min_score


# ----------------------------------------------------------------
# Interne pomocne funkcie
# ----------------------------------------------------------------

def _calculate_weighted_score(results: dict, weights: dict) -> tuple[float, float]:
    """
    Vypocita vazeny priemerny score.

    Pravidla:
    - Ak result pre danu vahu chyba -> preskoci (nulova vaha)
    - Ak result.data['skipped'] == True -> pouzije neutralnych 50
    - Ak result.ok == False a nie je skipped -> score 0 (chyba sluzby)
    - Vahy sa normalizuju podla skutocne dostupnych sluzieb

    Args:
        results: {source_name: ServiceResult}
        weights: {weight_key: float}

    Returns:
        (vazene_skore, sucet_pouzitych_vah)
    """
    weighted_sum = 0.0
    used_weight = 0.0

    for weight_key, weight_value in weights.items():
        source = WEIGHT_TO_SOURCE.get(weight_key)
        if source is None:
            continue

        result = results.get(source)
        if result is None:
            # Sluzba este nebezala - preskocit
            continue

        score = result.score
        weighted_sum += score * weight_value
        used_weight += weight_value

    if used_weight == 0.0:
        return 0.0, 0.0

    # Normalizacia: prepocitame na 100% aj ked niektoré sluzby chybaju
    normalized = (weighted_sum / used_weight)
    return round(normalized, 4), used_weight


def _get_recommendation(score: float, thresholds: dict) -> str:
    """
    Vrati textove odporucanie na zaklade pragov z configu.

    Args:
        score: celkove skore 0-100
        thresholds: dict z YAML (strong_buy, investigate, consider)

    Returns:
        "STRONG BUY" | "INVESTIGATE" | "CONSIDER" | "SKIP"
    """
    strong_buy  = thresholds.get("strong_buy",  85)
    investigate = thresholds.get("investigate", 70)
    consider    = thresholds.get("consider",    50)

    if score >= strong_buy:
        return "STRONG BUY"
    if score >= investigate:
        return "INVESTIGATE"
    if score >= consider:
        return "CONSIDER"
    return "SKIP"


_DRAZOBNE_SOURCES = {"ske_drazobne_vyhlasky", "notarske_drazby", "obchodny_vestnik"}


def preliminary_score(parcel: Parcel) -> Parcel:
    """
    Lacny pre-scoring pozemku BEZ HTTP volaní.
    Pouziva iba data dostupne priamo po scrape_all():
      price_eur, area_sqm, price_per_sqm, source_portal.

    Nastavi parcel.preliminary_score (0-100) a parcel.prelim_recommendation.
    Modifikuje parcel in-place a vrati ho spat.

    Komponenty (vazeny priemer):
      price_score    (35%) — cena v konfigurovanom rozsahu
      area_score     (30%) — vymera v konfigurovanom rozsahu
      ppsm_score     (20%) — EUR/m2 pod limitom
      source_bonus   (10%) — drazbove zdroje = bonus (podhodnotene)
      data_quality   ( 5%) — penalizacia za chybajuce polia
    """
    from config_loader import get_criteria, get_scoring

    cfg        = get_criteria()
    price_cfg  = cfg.get("price",  {})
    parcel_cfg = cfg.get("parcel", {})
    thresholds = get_scoring().get("thresholds", {})

    min_eur   = float(price_cfg.get("min_eur",  0))
    max_eur   = float(price_cfg.get("max_eur",  10000))
    max_ppsm  = float(price_cfg.get("max_price_per_sqm_eur", 100))
    min_area  = float(parcel_cfg.get("min_area_sqm", 350))
    max_area  = float(parcel_cfg.get("max_area_sqm", 1000))

    # --- Vypocitaj price_per_sqm ak chyba ---
    if parcel.price_per_sqm == 0.0 and parcel.price_eur > 0 and parcel.area_sqm > 0:
        parcel.price_per_sqm = round(parcel.price_eur / parcel.area_sqm, 2)

    price = parcel.price_eur
    area  = parcel.area_sqm
    ppsm  = parcel.price_per_sqm

    # --- price_score ---
    if price <= 0:
        price_score = 50.0          # neznama cena = neutral
    elif min_eur <= price <= max_eur:
        price_score = 100.0
    elif price < min_eur:
        # pod min je tiez zaujimave (lacnejsie nez ocakavame)
        price_score = 80.0
    else:
        # nad max: linearny pokles, pri 3x max -> 0
        ratio = (price - max_eur) / (2 * max_eur + 1)
        price_score = max(0.0, 100.0 - ratio * 100.0)

    # --- area_score ---
    if area <= 0:
        area_score = 50.0
    elif min_area <= area <= max_area:
        area_score = 100.0
    elif area < min_area:
        ratio = (min_area - area) / (min_area + 1)
        area_score = max(0.0, 100.0 - ratio * 60.0)
    else:
        ratio = (area - max_area) / (max_area + 1)
        area_score = max(0.0, 100.0 - ratio * 60.0)

    # --- ppsm_score ---
    if ppsm <= 0:
        ppsm_score = 50.0
    elif ppsm <= max_ppsm:
        ppsm_score = 100.0
    else:
        ratio = (ppsm - max_ppsm) / (max_ppsm + 1)
        ppsm_score = max(0.0, 100.0 - ratio * 80.0)

    # --- source_bonus ---
    source_bonus = 80.0 if parcel.source_portal in _DRAZOBNE_SOURCES else 50.0

    # --- data_quality ---
    has_price = price > 0
    has_area  = area  > 0
    if has_price and has_area:
        data_quality = 100.0
    elif has_price or has_area:
        data_quality = 50.0
    else:
        data_quality = 0.0

    # --- Vazeny priemer ---
    total = (
        price_score  * 0.35 +
        area_score   * 0.30 +
        ppsm_score   * 0.20 +
        source_bonus * 0.10 +
        data_quality * 0.05
    )

    parcel.preliminary_score      = round(total, 2)
    parcel.prelim_recommendation  = _get_recommendation(total, thresholds)
    return parcel


    # Normalizacia: prepocitame na 100% aj ked niektoré sluzby chybaju
    normalized = (weighted_sum / used_weight)
    return round(normalized, 4), used_weight


def _get_recommendation(score: float, thresholds: dict) -> str:
    """
    Vrati textove odporucanie na zaklade pragov z configu.

    Args:
        score: celkove skore 0-100
        thresholds: dict z YAML (strong_buy, investigate, consider)

    Returns:
        "STRONG BUY" | "INVESTIGATE" | "CONSIDER" | "SKIP"
    """
    strong_buy = thresholds.get("strong_buy", 85)
    investigate = thresholds.get("investigate", 70)
    consider = thresholds.get("consider", 50)

    if score >= strong_buy:
        return "STRONG BUY"
    if score >= investigate:
        return "INVESTIGATE"
    if score >= consider:
        return "CONSIDER"
    return "SKIP"
