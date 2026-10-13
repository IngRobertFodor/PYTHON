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

WEIGHT_TO_SOURCE = {
    "price":           "price_analysis_service",
    "distance":        "distance_service",
    "infrastructure":  "overpass_service",
    "legal_proxy":     "cadastral_service",
    "flood_risk":      "flood_service",
    "soil_quality":    "bpej_service",
    "terrain":         "terrain_service",
    "protected_zones": "protected_service",
}


def score_parcel(parcel: Parcel) -> Parcel:
    cfg = get_scoring()
    weights = cfg.get("weights", {})
    thresholds = cfg.get("thresholds", {})
    total_score, _ = _calculate_weighted_score(parcel.results, weights)
    parcel.final_score = round(total_score, 2)
    parcel.recommendation = _get_recommendation(total_score, thresholds)
    # GIS signály + merge s prelim
    try:
        from services.signals import gis_signals as _gs, merge_signals as _ms
        parcel.signals = _ms(parcel.signals or [], _gs(parcel))
    except Exception:
        pass
    # Kvantifikácia zisku z preklasifikácie (ak je poľnohosp. pôda)
    try:
        zbgis_d = (parcel.get_result("zbgis_service") or type("R", (), {"data": {}})()).data
        if zbgis_d.get("is_agricultural", False):
            from services.rezoning_service import estimate_rezoning_profit as _erp
            _erp(parcel)
            # Doplniť zisk do dovodu signálu PREKLASIFIKACIA
            if parcel.rezoning_profit_eur != 0:
                for sig in parcel.signals:
                    if sig.get("kod") == "PREKLASIFIKACIA":
                        profit = parcel.rezoning_profit_eur
                        cost   = parcel.rezoning_cost_eur
                        value  = parcel.rezoning_value_eur
                        sig["dovod"] += (
                            f" | Est. zisk: {profit:+,.0f} € "
                            f"(hodnota {value:,.0f} € − náklady {cost:,.0f} €)"
                        )
    except Exception:
        pass
    return parcel


def calculate_weighted_score(results: dict, weights: dict) -> float:
    score, _ = _calculate_weighted_score(results, weights)
    return score


def get_recommendation(score: float) -> str:
    cfg = get_scoring()
    return _get_recommendation(score, cfg.get("thresholds", {}))


def needs_cadastral_checklist(score: float) -> bool:
    cfg = get_scoring()
    return score >= cfg.get("checklist_min_score", 70)


def _calculate_weighted_score(results: dict, weights: dict) -> tuple:
    weighted_sum = 0.0
    used_weight  = 0.0
    for wk, wv in weights.items():
        src = WEIGHT_TO_SOURCE.get(wk)
        if src is None: continue
        r = results.get(src)
        if r is None: continue
        weighted_sum += r.score * wv
        used_weight  += wv
    if used_weight == 0.0: return 0.0, 0.0
    return round(weighted_sum / used_weight, 4), used_weight


def _get_recommendation(score: float, thresholds: dict) -> str:
    if score >= thresholds.get("strong_buy",  85): return "STRONG BUY"
    if score >= thresholds.get("investigate", 70): return "INVESTIGATE"
    if score >= thresholds.get("consider",    50): return "CONSIDER"
    return "SKIP"



# ----------------------------------------------------------------
# Konstanty pre prelim scoring
# ----------------------------------------------------------------

_DRAZOBNE_SOURCES = {"ske_drazobne_vyhlasky", "notarske_drazby", "obchodny_vestnik"}
_BA_LAT = 48.1486
_BA_LON = 17.1077
_INZERAT_SOURCES  = {"nehnutelnosti_sk", "topreality_sk", "reality_sk"}
_SUSPICIOUS_PPSM_THRESHOLD = 1.5


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    import math
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a  = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _normalize_loc(text: str) -> str:
    import unicodedata
    nfkd = unicodedata.normalize("NFKD", text.lower().strip())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


_SK_TOWN_COORDS: dict = {
    "bratislava": (48.1486, 17.1077), "senec": (48.2189, 17.3672),
    "pezinok": (48.2896, 17.2673),    "modra": (48.3334, 17.3059),
    "malacky": (48.4338, 17.0189),    "trnava": (48.3774, 17.5855),
    "dunajska streda": (47.9950, 17.6167), "galanta": (48.1858, 17.7296),
    "sala": (48.1505, 17.8793),       "hlohovec": (48.4308, 17.7972),
    "piestany": (48.5881, 17.8333),   "nitra": (48.3061, 18.0865),
    "trencin": (48.8940, 18.0445),    "banska bystrica": (48.7395, 19.1531),
    "zvolen": (48.5724, 19.1203),     "zilina": (49.2235, 18.7394),
    "presov": (49.0022, 21.2394),     "kosice": (48.7167, 21.2500),
    "poprad": (49.0584, 20.2977),     "ruzomberok": (49.0748, 19.3042),
    "liptovsky mikulas": (49.0828, 19.6094), "martin": (49.0647, 18.9233),
    "nove zamky": (47.9848, 18.1618), "komarno": (47.7638, 18.1268),
    "levice": (48.2148, 18.6021),     "senica": (48.6810, 17.3659),
    "bernolakovo": (48.2000, 17.2833),"ivanka pri dunaji": (48.1833, 17.2667),
    "svaty jur": (48.2537, 17.2201),  "rovinka": (48.1169, 17.2494),
    "raca": (48.2073, 17.1373),       "devinska nova ves": (48.1992, 16.9961),
    "stupava": (48.2720, 17.0310),    "zohor": (48.3373, 17.0040),
    "malinovo": (48.1413, 17.3210),   "velky biel": (48.1617, 17.3548),
    "lehnice": (47.9668, 17.4208),    "samorin": (48.0289, 17.3131),
    "blatne": (48.1946, 17.4271),     "vinosady": (48.3227, 17.3188),
    "leopoldov": (48.4463, 17.7669),  "devin": (48.1802, 16.9772),
    "jarovce": (48.0700, 17.1050),    "rusovce": (48.0787, 17.1219),
    "cunovo": (47.9997, 17.1528),     "nova bana": (48.4167, 18.6500),
    "nove mesto nad vahom": (48.7568, 17.8318), "skalica": (48.8408, 17.2258),
    "spiske bystre": (48.9500, 20.5167), "opina": (48.6667, 21.3333),
}


def _estimate_distance_km(location_text: str) -> float | None:
    """Odhadne vzdialenost od BA z location_text (bez GPS)."""
    if not location_text:
        return None
    try:
        from services.sk_places import dist_to_ba as _dtba
        km = _dtba(location_text)
        if km is not None:
            return km
    except Exception:
        pass
    loc     = location_text.lower().strip()
    loc_asc = _normalize_loc(location_text)
    for key in (loc, loc_asc):
        if key in _SK_TOWN_COORDS:
            lat, lon = _SK_TOWN_COORDS[key]
            return _haversine_km(_BA_LAT, _BA_LON, lat, lon)
    for town in sorted(_SK_TOWN_COORDS, key=len, reverse=True):
        if len(town) < 4:
            continue
        town_asc = _normalize_loc(town)

def preliminary_score(parcel: Parcel) -> Parcel:
    """
    Lacny pre-scoring BEZ HTTP.
    Skore = vazeny priemer LEN z dostupnych komponentov (normalizacia vah).
    Chybajuci udaj: komponent vynechany (nie penalizacia).
    Nastavi: preliminary_score, prelim_recommendation,
             prelim_confidence, prelim_missing, prelim_breakdown, signals.
    """
    from config_loader import get_criteria, get_scoring
    cfg        = get_criteria()
    price_cfg  = cfg.get("price",  {})
    parcel_cfg = cfg.get("parcel", {})
    thresholds = get_scoring().get("thresholds", {})

    min_eur  = float(price_cfg.get("min_eur",  0))
    max_eur  = float(price_cfg.get("max_eur",  200000))
    max_ppsm = float(price_cfg.get("max_price_per_sqm_eur", 300))
    min_area = float(parcel_cfg.get("min_area_sqm", 300))
    max_area = float(parcel_cfg.get("max_area_sqm", 800))
    max_km   = float(cfg.get("location", {}).get("max_distance_km", 82))

    if parcel.price_per_sqm == 0.0 and parcel.price_eur > 0 and parcel.area_sqm > 0:
        parcel.price_per_sqm = round(parcel.price_eur / parcel.area_sqm, 2)

    price  = parcel.price_eur
    area   = parcel.area_sqm
    ppsm   = parcel.price_per_sqm
    source = parcel.source_portal

    missing: list    = []
    breakdown: dict  = {}
    W_PRICE  = 0.30; W_AREA = 0.25; W_PPSM = 0.20
    W_DIST   = 0.10; W_SOURCE = 0.10
    components: list = []

    # price_score
    if price <= 0:
        missing.append("cena"); breakdown["price"] = None
    elif min_eur <= price <= max_eur:
        breakdown["price"] = 100.0; components.append((W_PRICE, 100.0))
    elif price < min_eur:
        breakdown["price"] = 80.0; components.append((W_PRICE, 80.0))
    else:
        s = max(0.0, 100.0 - (price - max_eur) / (2 * max_eur + 1) * 100.0)
        breakdown["price"] = s; components.append((W_PRICE, s))

    # area_score
    if area <= 0:
        missing.append("vymera"); breakdown["area"] = None
    elif min_area <= area <= max_area:
        breakdown["area"] = 100.0; components.append((W_AREA, 100.0))
    elif area < min_area:
        s = max(30.0, 100.0 - (min_area - area) / (min_area + 1) * 60.0)
        breakdown["area"] = s; components.append((W_AREA, s))
    else:
        s = max(30.0, 100.0 - (area - max_area) / (max_area + 1) * 60.0)
        breakdown["area"] = s; components.append((W_AREA, s))

    # ppsm_score
    is_susp = (source in _INZERAT_SOURCES and 0 < ppsm < _SUSPICIOUS_PPSM_THRESHOLD)
    if is_susp:
        missing.append("cena_podozriva"); breakdown["ppsm"] = None
    elif ppsm <= 0:
        missing.append("eur_m2"); breakdown["ppsm"] = None
    elif ppsm <= max_ppsm:
        breakdown["ppsm"] = 100.0; components.append((W_PPSM, 100.0))
    else:
        s = max(20.0, 100.0 - (ppsm - max_ppsm) / (max_ppsm + 1) * 80.0)
        breakdown["ppsm"] = s; components.append((W_PPSM, s))

    # dist_score
    est_km = _estimate_distance_km(parcel.location_text)
    if est_km is None:
        missing.append("poloha"); breakdown["dist"] = None
    elif est_km <= max_km * 0.5:
        breakdown["dist"] = 100.0; components.append((W_DIST, 100.0))
    elif est_km <= max_km:
        s = max(60.0, 100.0 - (est_km - max_km * 0.5) / (max_km * 0.5) * 40.0)
        breakdown["dist"] = s; components.append((W_DIST, s))
    else:
        s = max(0.0, 60.0 - (est_km - max_km) / (max_km + 1) * 60.0)
        breakdown["dist"] = s; components.append((W_DIST, s))

    # source_bonus (vzdy dostupny)
    src_s = 80.0 if source in _DRAZOBNE_SOURCES else 50.0
    breakdown["source"] = src_s; components.append((W_SOURCE, src_s))

    # Normalizovany vazeny priemer
    total_w = sum(w for w, _ in components)
    if total_w == 0.0:
        total = 0.0; confidence = 0.0
    else:
        total      = sum(w * s for w, s in components) / total_w
        max_w      = W_PRICE + W_AREA + W_PPSM + W_DIST + W_SOURCE
        confidence = round(total_w / max_w, 3)

    rec = ("NEDOSTATOK_DAT" if confidence < 0.5
           else _get_recommendation(total, thresholds))

    try:
        from services.signals import preliminary_signals as _psig
        parcel.signals = _psig(parcel)
    except Exception:
        parcel.signals = []

    parcel.preliminary_score     = round(total, 2)
    parcel.prelim_recommendation = rec
    parcel.prelim_confidence     = confidence
    parcel.prelim_missing        = missing
    parcel.prelim_breakdown      = breakdown
    return parcel

