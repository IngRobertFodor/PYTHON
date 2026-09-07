"""
Overpass Service
================
Analyza infrastrukturnych prvkov okolo pozemku cez OpenStreetMap Overpass API.
Kontroluje: cesta, elektrina, voda, kanalizacia, plyn,
ochrane pasma (VVN, VTL, les), hluk, prostredie.
Free, bez API kluca.
"""

import requests
import math
from models.result import ServiceResult
from config_loader import is_feature_enabled, get_criteria_section, get_endpoints

SERVICE_NAME = "overpass_service"
TIMEOUT = 30

OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]


def check(lat: float, lon: float) -> ServiceResult:
    """
    Komplexna kontrola infrastrukturnych prvkov v okoli pozemku.

    Args:
        lat, lon: WGS-84 suradnice pozemku

    Returns:
        ServiceResult so score 0-100 a detailmi
    """
    if not is_feature_enabled("use_overpass"):
        return ServiceResult.skip_result(SERVICE_NAME, "use_overpass=false")

    try:
        elements = _query_overpass(lat, lon, radius=500)
        analysis = _analyze_elements(elements, lat, lon)
        score = _calculate_score(analysis)
        return ServiceResult(ok=True, score=score, data=analysis, source=SERVICE_NAME)
    except Exception as e:
        return ServiceResult(
            ok=False, score=50.0, data={},
            error=f"Overpass nedostupny: {e}", source=SERVICE_NAME
        )


def _query_overpass(lat: float, lon: float, radius: int) -> list:
    """Posle Overpass QL dotaz, skusi viacero serverov (fallback)."""
    query = _build_query(lat, lon, radius)
    for server in OVERPASS_SERVERS:
        try:
            resp = requests.post(
                server, data={"data": query}, timeout=TIMEOUT,
                headers={"User-Agent": "LandResearchInvest/1.0"},
            )
            resp.raise_for_status()
            return resp.json().get("elements", [])
        except Exception:
            continue
    raise RuntimeError("Vsetky Overpass servery nedostupne")


def _build_query(lat: float, lon: float, radius: int) -> str:
    """Zostaví Overpass QL dotaz pre danu poziciu a polomer."""
    return f"""
    [out:json][timeout:25];
    (
      way["highway"](around:{radius},{lat},{lon});
      node["power"~"line|pole|tower"](around:{radius},{lat},{lon});
      way["power"="line"](around:{radius},{lat},{lon});
      way["waterway"](around:{radius},{lat},{lon});
      way["man_made"="pipeline"](around:{radius},{lat},{lon});
      way["landuse"~"forest"](around:{radius},{lat},{lon});
      way["natural"="wood"](around:{radius},{lat},{lon});
      way["highway"~"motorway|trunk"](around:{radius},{lat},{lon});
      way["railway"](around:{radius},{lat},{lon});
      way["landuse"~"industrial|landfill"](around:{radius},{lat},{lon});
    );
    out center;
    """


def _analyze_elements(elements: list, lat: float, lon: float) -> dict:
    """Analyzuje OSM prvky a vypocita vzdialenosti / pritomnost."""
    road_dist = _min_dist(elements, lat, lon, "highway", None)
    road_type = _nearest_val(elements, lat, lon, "highway")
    road_width = _nearest_num(elements, lat, lon, "highway", "width")
    elec_dist = _min_dist(elements, lat, lon, "power", ["line", "pole", "tower"])
    water_dist = _min_dist(elements, lat, lon, "waterway", None)
    pipeline_dist = _min_dist(elements, lat, lon, "man_made", ["pipeline"])
    forest_dist = min(
        _min_dist(elements, lat, lon, "landuse", ["forest"]),
        _min_dist(elements, lat, lon, "natural", ["wood"])
    )
    motorway_dist = _min_dist(elements, lat, lon, "highway", ["motorway", "trunk"])
    railway_dist = _min_dist(elements, lat, lon, "railway", None)
    landfill_dist = _min_dist(elements, lat, lon, "landuse", ["landfill"])
    industrial_dist = _min_dist(elements, lat, lon, "landuse", ["industrial"])

    cfg_i = get_criteria_section("infrastructure")
    cfg_p = get_criteria_section("protected_zones")
    cfg_e = get_criteria_section("environment")
    cfg_n = get_criteria_section("noise")

    road_min_w = cfg_i.get("road", {}).get("min_width_m", 6)
    elec_max   = cfg_i.get("electricity", {}).get("max_distance_m", 200)
    water_max  = cfg_i.get("water", {}).get("max_distance_m", 200)
    forest_buf = cfg_p.get("forest_buffer_m", 50)
    landfill_b = cfg_e.get("landfill_buffer_m", 500)
    industrial_b = cfg_e.get("industrial_buffer_m", 300)
    noise_hw_min = cfg_n.get("min_highway_distance_m", 50)
    noise_rail_max = cfg_n.get("max_railway_distance_m", 150)

    return {
        "road": {
            "distance_m": road_dist,
            "type": road_type,
            "width_m": road_width,
            "accessible": road_dist < 100,
            "wide_enough": (road_width or 0) >= road_min_w,
        },
        "electricity": {
            "distance_m": elec_dist,
            "available": elec_dist <= elec_max,
        },
        "water": {
            "distance_m": water_dist,
            "available": water_dist <= water_max,
        },
        "pipeline_gas": {
            "distance_m": pipeline_dist,
            "nearby": pipeline_dist < 100,
        },
        "forest_buffer": {
            "distance_m": forest_dist,
            "safe": forest_dist >= forest_buf,
        },
        "noise": {
            "motorway_distance_m": motorway_dist,
            "railway_distance_m": railway_dist,
            "motorway_safe": motorway_dist >= noise_hw_min,
            "railway_safe": railway_dist >= noise_rail_max,
        },
        "environment": {
            "landfill_distance_m": landfill_dist,
            "industrial_distance_m": industrial_dist,
            "landfill_safe": landfill_dist >= landfill_b,
            "industrial_safe": industrial_dist >= industrial_b,
        },
    }


def _calculate_score(analysis: dict) -> float:
    """Vypocita score 0-100 na zaklade analyzy infrastruktury."""
    score = 0.0
    road = analysis.get("road", {})
    if road.get("accessible"):
        score += 20
        if road.get("wide_enough"):
            score += 15
    if analysis.get("electricity", {}).get("available"):
        score += 25
    if analysis.get("water", {}).get("available"):
        score += 15
    if analysis.get("forest_buffer", {}).get("safe"):
        score += 10
    noise = analysis.get("noise", {})
    if noise.get("motorway_safe") and noise.get("railway_safe"):
        score += 10
    env = analysis.get("environment", {})
    if env.get("landfill_safe") and env.get("industrial_safe"):
        score += 5
    return min(round(score, 2), 100.0)


def _haversine_m(lat1, lon1, lat2, lon2) -> float:
    """Vzdialenost v metroch (Haversine)."""
    R = 6371000.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _coords(el: dict) -> tuple[float, float] | None:
    lat = el.get("lat") or el.get("center", {}).get("lat")
    lon = el.get("lon") or el.get("center", {}).get("lon")
    return (lat, lon) if lat and lon else None


def _min_dist(elements, lat, lon, key, values) -> float:
    best = 9999.0
    for el in elements:
        v = el.get("tags", {}).get(key)
        if v is None: continue
        if values and v not in values: continue
        c = _coords(el)
        if c:
            d = _haversine_m(lat, lon, c[0], c[1])
            if d < best: best = d
    return best


def _nearest_val(elements, lat, lon, key) -> str | None:
    best_d, result = 9999.0, None
    for el in elements:
        v = el.get("tags", {}).get(key)
        if v is None: continue
        c = _coords(el)
        if c:
            d = _haversine_m(lat, lon, c[0], c[1])
            if d < best_d: best_d, result = d, v
    return result


def _nearest_num(elements, lat, lon, filter_key, value_key) -> float | None:
    best_d, result = 9999.0, None
    for el in elements:
        if el.get("tags", {}).get(filter_key) is None: continue
        raw = el.get("tags", {}).get(value_key)
        if raw is None: continue
        try: val = float(str(raw).replace(",", "."))
        except ValueError: continue
        c = _coords(el)
        if c:
            d = _haversine_m(lat, lon, c[0], c[1])
            if d < best_d: best_d, result = d, val
    return result

