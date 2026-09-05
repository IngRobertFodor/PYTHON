"""
Scoring Service
===============
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
    "price":          "price_analysis_service",
    "distance":       "distance_service",
    "infrastructure": "overpass_service",
    "legal_proxy":    "cadastral_service",
    "flood_risk":     "flood_service",
    "soil_quality":   "bpej_service",
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
