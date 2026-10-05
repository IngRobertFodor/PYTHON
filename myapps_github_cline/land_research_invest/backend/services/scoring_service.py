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

# Bratislava centroid (Hlavné námestie)
_BA_LAT = 48.1486
_BA_LON = 17.1077

# Portály kde ceny môžu byť neúplné / zrkadlové (placeholder 1 EUR/m²)
_INZERAT_SOURCES = {"nehnutelnosti_sk", "topreality_sk", "reality_sk"}

# Podozrivo nízky EUR/m² prah pre inzerátové portály
_SUSPICIOUS_PPSM_THRESHOLD = 1.5


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Vzdialenosť medzi dvoma bodmi v km (Haversine)."""
    import math
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# Základné súradnice SK obcí pre odhad vzdialenosti na prelim fáze
# (keď GPS nie je k dispozícii z geocodingu)
_SK_TOWN_COORDS: dict = {
    # BA okolie
    "bratislava": (48.1486, 17.1077),
    "senec": (48.2196, 17.3969),
    "pezinok": (48.2896, 17.2698),
    "malacky": (48.4358, 17.0235),
    "stupava": (48.2720, 17.0250),
    "modra": (48.3344, 17.3132),
    "svätý jur": (48.2500, 17.2167),
    "bernolákovo": (48.1947, 17.3014),
    "dunajská streda": (47.9956, 17.6150),
    "šamorín": (47.9972, 17.3119),
    "vistuk": (48.2997, 17.3631),
    "marianka": (48.2167, 17.0833),
    "jahodná": (48.2583, 17.4583),
    "miloslavov": (48.0933, 17.2969),
    "most pri bratislave": (48.1000, 17.2167),
    "rusovce": (47.9753, 17.1047),
    "čunovo": (47.9411, 17.1756),
    "vajnory": (48.1900, 17.2150),
    "rača": (48.2061, 17.1464),
    "záhorská bystrica": (48.2311, 17.0122),
    "devín": (48.1736, 17.0358),
    "devínska nová ves": (48.1983, 17.0628),
    "dúbravka": (48.1725, 17.0567),
    "petržalka": (48.0908, 17.0956),
    "ružinov": (48.1483, 17.1578),
    "vrakuňa": (48.1400, 17.1994),
    "podunajské biskupice": (48.1136, 17.2042),
    "nové mesto": (48.1719, 17.1331),
    "lamač": (48.1878, 17.0467),
    "karlova ves": (48.1583, 17.0600),
    "staré mesto": (48.1436, 17.1028),
    # Ostatné SK mestá (ďalej od BA)
    "trnava": (48.3781, 17.5882),
    "piešťany": (48.5883, 17.8306),
    "nitra": (48.3069, 18.0836),
    "trenčín": (48.8942, 18.0442),
    "žilina": (49.2234, 18.7403),
    "martin": (49.0619, 18.9220),
    "zvolen": (48.5753, 19.1239),
    "banská bystrica": (48.7361, 19.1533),
    "košice": (48.7167, 21.2500),
    "prešov": (49.0022, 21.2394),
    "poprad": (49.0556, 20.2958),
    "ružomberok": (49.0794, 19.3083),
    "liptovský mikuláš": (49.0847, 19.6136),
    "lučenec": (48.3339, 19.6661),
    "rimavská sobota": (48.3811, 20.0175),
    "skalica": (48.8492, 17.2264),
    "senica": (48.6814, 17.3661),
    "hlohovec": (48.4267, 17.8017),
    "topoľčany": (48.5600, 18.1694),
    "zlaté moravce": (48.3811, 18.3972),
    "levice": (48.2172, 18.6083),
    "nové zámky": (47.9856, 18.1619),
    "komárno": (47.7625, 18.1264),
    "dunajská lužná": (48.1142, 17.2808),
    "veľké pole": (48.4267, 18.9575),
    "sikenica": (48.1333, 18.5833),
    "ihráč": (48.3750, 18.7500),
    "halič": (48.4003, 19.7181),
    "varhaňovce": (49.0833, 21.3167),
    "stará ľubovňa": (49.3000, 20.6833),
    "stankovany": (49.0667, 19.2500),
    "bílkove humence": (48.5167, 17.8000),
    "diakovce": (47.9833, 17.9333),
    "bzince pod javorinou": (48.7167, 17.7500),
    "toporec": (49.1500, 20.6833),
    "veľká lomnica": (49.1500, 20.3833),
    "stebník": (49.4000, 21.5833),
    "vyhne": (48.4833, 18.8667),
    "bruty": (48.1833, 18.2500),
    "víťazovce": (48.3833, 19.7167),
    "hanigovce": (49.0833, 21.1833),
    "podhorany": (48.4667, 18.2500),
    "skalité": (49.4667, 18.9833),
    "ladomirová": (49.3833, 21.8000),
    "vernár": (48.8500, 20.3167),
    "šuňava": (49.0167, 20.1667),
    "hurbanovo": (47.8706, 18.1908),
    "gbeľany": (49.1833, 18.7500),
    "vištuk": (48.2997, 17.3631),
    "soboš": (49.2167, 21.5167),
    "kamenný most": (47.9667, 18.5500),
    "blatné": (48.2500, 17.2833),
    "sasinkovo": (48.2833, 17.7500),
    "zlatná na ostrove": (47.8833, 18.1500),
    "modra": (48.3344, 17.3132),
    "bara": (48.0167, 18.5333),
    "melek": (48.3500, 17.9500),
    "báb": (48.2667, 18.1000),
    "spišské bystré": (48.9500, 20.5167),
    "opiná": (48.6667, 21.3333),
    # ASCII verzie (bez diakritiky) -- automaticky normalizovane v _estimate_distance_km
    "kosice": (48.7167, 21.2500),
    "presov": (49.0022, 21.2394),
    "zilina": (49.2234, 18.7403),
    "trencin": (48.8942, 18.0442),
    "banska bystrica": (48.7361, 19.1533),
    "piestany": (48.5883, 17.8306),
    "stara lubovna": (49.3000, 20.6833),
    "raca": (48.2061, 17.1464),
    "devin": (48.1736, 17.0358),
    "devinska nova ves": (48.1983, 17.0628),
    "dubravka": (48.1725, 17.0567),
    "petrzalka": (48.0908, 17.0956),
    "ruzinov": (48.1483, 17.1578),
    "vrakuna": (48.1400, 17.1994),
    "lamac": (48.1878, 17.0467),
    "kamenny most": (47.9667, 18.5500),
    "blatne": (48.2500, 17.2833),
    "halic": (48.4003, 19.7181),
    "varhanovce": (49.0833, 21.3167),
    "skalite": (49.4667, 18.9833),
    "ladomirova": (49.3833, 21.8000),
    "vernar": (48.8500, 20.3167),
    "sunava": (49.0167, 20.1667),
    "hanigovce": (49.0833, 21.1833),
    "vitazovce": (48.3833, 19.7167),
    "ihrac": (48.3750, 18.7500),
    "velke pole": (48.4267, 18.9575),
    "velka lomnica": (49.1500, 20.3833),
    "stebnik": (49.4000, 21.5833),
    "bzince pod javorinou": (48.7167, 17.7500),
    "gbelany": (49.1833, 18.7500),
    "sobos": (49.2167, 21.5167),
    "diakovce": (47.9833, 17.9333),
    "bilkove humence": (48.5167, 17.8000),
    "hurbanovo": (47.8706, 18.1908),
    "vistuk": (48.2997, 17.3631),
    "podhorany": (48.4667, 18.2500),
    "bruty": (48.1833, 18.2500),
    "kamenný most": (47.9667, 18.5500),
}



def _normalize_loc(text: str) -> str:
    """Normalizuje text: lowercase, bez diakritiky, strip."""
    import unicodedata
    nfkd = unicodedata.normalize("NFKD", text.lower().strip())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _estimate_distance_km(location_text: str) -> float | None:
    """
    Odhadne vzdialenosť od BA na základe location_text (bez GPS).
    Prehľadá slovník SK miest (s diakritikou aj bez). Vracia km alebo None.
    """
    if not location_text:
        return None
    loc     = location_text.lower().strip()
    loc_asc = _normalize_loc(location_text)

    # 1. Presná zhoda (s diakritikou aj bez)
    for key in (loc, loc_asc):
        if key in _SK_TOWN_COORDS:
            lat, lon = _SK_TOWN_COORDS[key]
            return _haversine_km(_BA_LAT, _BA_LON, lat, lon)

    # 2. Čiastočná zhoda — town IN loc alebo loc IN town (obe varianty)
    for town, coords in _SK_TOWN_COORDS.items():
        town_asc = _normalize_loc(town)
        if (town in loc or loc_asc in town_asc
                or town_asc in loc_asc or loc in town):
            return _haversine_km(_BA_LAT, _BA_LON, coords[0], coords[1])
    return None


def preliminary_score(parcel: Parcel) -> Parcel:
    """
    Lacny pre-scoring pozemku BEZ HTTP volani.
    Pouziva iba data dostupne priamo po scrape_all():
      price_eur, area_sqm, price_per_sqm, source_portal, location_text.

    Nastavi parcel.preliminary_score (0-100) a parcel.prelim_recommendation.
    Modifikuje parcel in-place a vrati ho spat.

    Komponenty (vazeny priemer):
      price_score    (30%) -- cena v konfigurovanom rozsahu
      area_score     (25%) -- vymera v konfigurovanom rozsahu
      ppsm_score     (20%) -- EUR/m2 pod limitom (P1: 0 ak suspicious)
      dist_score     (10%) -- odhad vzdialenosti od BA z location_text (P2)
      source_bonus   (10%) -- drazbove zdroje = bonus (podhodnotene)
      data_quality   ( 5%) -- penalizacia za chybajuce polia

    P1: ppsm < 1.5 EUR/m2 z inzeratovych portalov -> ppsm_score=0
        (pravdepodobna parsovacia chyba, nie realna cena)
    P2: vzdialenost od BA odhadnuta z location_text pre drazbove zdroje
        -> penalizacia za priilis vzdialene lokality
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
    max_km    = float(cfg.get("location", {}).get("max_distance_km", 85))

    # --- Vypocitaj price_per_sqm ak chyba ---
    if parcel.price_per_sqm == 0.0 and parcel.price_eur > 0 and parcel.area_sqm > 0:
        parcel.price_per_sqm = round(parcel.price_eur / parcel.area_sqm, 2)

    price = parcel.price_eur
    area  = parcel.area_sqm
    ppsm  = parcel.price_per_sqm

    # --- P1: Suspicious price flag (inzeratovy portal + ppsm < 1.5) ---
    is_suspicious_price = (
        parcel.source_portal in _INZERAT_SOURCES
        and ppsm > 0
        and ppsm < _SUSPICIOUS_PPSM_THRESHOLD
    )

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

    # --- ppsm_score (P1: nuluj pre suspicious ceny z inzeratov) ---
    if is_suspicious_price:
        ppsm_score = 0.0    # P1: nevierohodna cena z inzeratu -> penalizuj
    elif ppsm <= 0:
        ppsm_score = 50.0
    elif ppsm <= max_ppsm:
        ppsm_score = 100.0
    else:
        ratio = (ppsm - max_ppsm) / (max_ppsm + 1)
        ppsm_score = max(0.0, 100.0 - ratio * 80.0)

    # --- P2: dist_score -- odhad vzdialenosti od BA z location_text ---
    est_km = _estimate_distance_km(parcel.location_text)
    if est_km is None:
        dist_score = 40.0   # neznama poloha -> mierna penalizacia
    elif est_km <= max_km * 0.5:
        dist_score = 100.0  # blizko BA (<42.5km) -> plny bonus
    elif est_km <= max_km:
        ratio = (est_km - max_km * 0.5) / (max_km * 0.5)
        dist_score = max(60.0, 100.0 - ratio * 40.0)
    else:
        # za limitom -> vyznamna penalizacia
        ratio = (est_km - max_km) / (max_km + 1)
        dist_score = max(0.0, 60.0 - ratio * 60.0)

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

    # --- Vazeny priemer (sucet vah = 1.00) ---
    total = (
        price_score  * 0.30 +
        area_score   * 0.25 +
        ppsm_score   * 0.20 +
        dist_score   * 0.10 +
        source_bonus * 0.10 +
        data_quality * 0.05
    )

    parcel.preliminary_score      = round(total, 2)
    parcel.prelim_recommendation  = _get_recommendation(total, thresholds)
    return parcel


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
