"""
Sluzba infrastruktury (Overpass)  J1: building -> classify_access/position/is_gem_candidate
"""
import requests
import math
from models.result import ServiceResult
from config_loader import is_feature_enabled, get_criteria_section, get_endpoints

SERVICE_NAME = "overpass_service"
TIMEOUT = 8
OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]


def check(lat: float, lon: float) -> ServiceResult:
    if not is_feature_enabled("use_overpass"):
        return ServiceResult.skip_result(SERVICE_NAME, "use_overpass=false")
    try:
        elements = _query_overpass(lat, lon, radius=500)
        analysis = _analyze_elements(elements, lat, lon)
        score = _calculate_score(analysis)
        return ServiceResult(ok=True, score=score, data=analysis, source=SERVICE_NAME)
    except Exception as e:
        return ServiceResult(ok=False, score=50.0, data={},
                             error=f"Overpass nedostupny: {e}", source=SERVICE_NAME)


def _query_overpass(lat: float, lon: float, radius: int) -> list:
    query = _build_query(lat, lon, radius)
    for server in OVERPASS_SERVERS:
        try:
            resp = requests.post(server, data={"data": query}, timeout=TIMEOUT,
                                 headers={"User-Agent": "LandResearchInvest/1.0"})
            resp.raise_for_status()
            return resp.json().get("elements", [])
        except Exception:
            continue
    raise RuntimeError("Vsetky Overpass servery nedostupne")


def _build_query(lat: float, lon: float, radius: int) -> str:
    r_big = max(radius, 350)
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
      way["building"](around:{r_big},{lat},{lon});
      node["building"](around:{r_big},{lat},{lon});
    );
    out center;
    """


def _analyze_elements(elements: list, lat: float, lon: float) -> dict:
    road_dist     = _min_dist(elements, lat, lon, "highway", None)
    road_type     = _nearest_val(elements, lat, lon, "highway")
    road_width    = _nearest_num(elements, lat, lon, "highway", "width")
    elec_dist     = _min_dist(elements, lat, lon, "power", ["line", "pole", "tower"])
    water_dist    = _min_dist(elements, lat, lon, "waterway", None)
    pipeline_dist = _min_dist(elements, lat, lon, "man_made", ["pipeline"])
    forest_dist   = min(_min_dist(elements, lat, lon, "landuse", ["forest"]),
                        _min_dist(elements, lat, lon, "natural",  ["wood"]))
    motorway_dist   = _min_dist(elements, lat, lon, "highway", ["motorway", "trunk"])
    railway_dist    = _min_dist(elements, lat, lon, "railway", None)
    landfill_dist   = _min_dist(elements, lat, lon, "landuse", ["landfill"])
    industrial_dist = _min_dist(elements, lat, lon, "landuse", ["industrial"])
    building_dist    = _min_dist(elements, lat, lon, "building", None)
    building_cnt_100 = _count_within(elements, lat, lon, "building", 100)
    building_cnt_300 = _count_within(elements, lat, lon, "building", 300)

    cfg_i = get_criteria_section("infrastructure")
    cfg_p = get_criteria_section("protected_zones")
    cfg_e = get_criteria_section("environment")
    cfg_n = get_criteria_section("noise")

    road_min_w    = cfg_i.get("road",        {}).get("min_width_m",        6)
    elec_max      = cfg_i.get("electricity", {}).get("max_distance_m",   200)
    water_max     = cfg_i.get("water",       {}).get("max_distance_m",   200)
    forest_buf    = cfg_p.get("forest_buffer_m", 50)
    landfill_b    = cfg_e.get("landfill_buffer_m",   500)
    industrial_b  = cfg_e.get("industrial_buffer_m", 300)
    noise_hw_min  = cfg_n.get("min_highway_distance_m",  50)
    noise_rail_max = cfg_n.get("max_railway_distance_m", 150)

    analysis = {
        "road": {"distance_m": road_dist, "type": road_type, "width_m": road_width,
                 "accessible": road_dist < 100, "wide_enough": (road_width or 0) >= road_min_w},
        "electricity": {"distance_m": elec_dist, "available": elec_dist <= elec_max},
        "water":       {"distance_m": water_dist, "available": water_dist <= water_max},
        "pipeline_gas": {"distance_m": pipeline_dist, "nearby": pipeline_dist < 100},
        "forest_buffer": {"distance_m": forest_dist, "safe": forest_dist >= forest_buf},
        "noise": {"motorway_distance_m": motorway_dist, "railway_distance_m": railway_dist,
                  "motorway_safe": motorway_dist >= noise_hw_min,
                  "railway_safe":  railway_dist  >= noise_rail_max},
        "environment": {"landfill_distance_m": landfill_dist,
                        "industrial_distance_m": industrial_dist,
                        "landfill_safe":   landfill_dist   >= landfill_b,
                        "industrial_safe": industrial_dist >= industrial_b},
        "buildings": {
            "nearest_m":  round(building_dist) if building_dist < 9999 else None,
            "count_100m": building_cnt_100,
            "count_300m": building_cnt_300,
        },
    }
    cfg_ac = get_criteria_section("access_classification")
    access = classify_access(analysis, cfg_ac)
    pos    = classify_position(analysis, cfg_ac)
    analysis["direct_access"]    = access
    analysis["village_position"] = pos
    analysis["is_gem_candidate"] = is_gem_candidate(access, pos)
    return analysis


# ----------------------------------------------------------------
# Klasifikacne funkcie (J1)
# ----------------------------------------------------------------

def classify_access(analysis: dict, cfg: dict) -> dict:
    """
    Priama dostupnost infrastruktury.
    Proxy: blizke domy = elektrina/voda/cesta su tam (dom bez elektriny neexistuje).
    Urovne: PRIAMA / CIASTOCNA / ZIADNA
    """
    ac = cfg.get("direct_access", {})
    full_m    = ac.get("full_m",    50)
    partial_m = ac.get("partial_m", 150)
    b = analysis.get("buildings", {})
    r = analysis.get("road", {})
    nearest_bld = b.get("nearest_m")
    road_dist   = r.get("distance_m", 9999)
    road_r = round(road_dist) if road_dist < 9999 else None
    bld_ok  = nearest_bld is not None and nearest_bld <= full_m
    road_ok = road_dist <= full_m
    bld_par  = nearest_bld is not None and nearest_bld <= partial_m
    road_par = road_dist <= partial_m
    if bld_ok and road_ok:
        return {"level": "PRIAMA",
                "reason": f"dom {nearest_bld} m, cesta {road_r} m",
                "building_m": nearest_bld, "road_m": road_r}
    if bld_par and road_par:
        return {"level": "CIASTOCNA",
                "reason": f"dom {nearest_bld} m, cesta {road_r} m",
                "building_m": nearest_bld, "road_m": road_r}
    parts = []
    if nearest_bld is None:       parts.append("ziadne domy do 350 m")
    elif nearest_bld > partial_m: parts.append(f"najblizsi dom {nearest_bld} m")
    if road_dist > partial_m:     parts.append(f"cesta {road_r} m")
    return {"level": "ZIADNA",
            "reason": "; ".join(parts) or "daleko od infrastruktury",
            "building_m": nearest_bld, "road_m": road_r}


def classify_position(analysis: dict, cfg: dict) -> dict:
    """
    Poloha parcely v ramci obce.
    Proxy: hustota domov v 2 okruhoch (100 m / 300 m).
    Urovne: STRED / OKRAJ / MIMO
    """
    vp = cfg.get("village_position", {})
    core_100 = vp.get("core_count_100m",    30)
    edge_300 = vp.get("edge_min_count_300m",  3)
    b = analysis.get("buildings", {})
    cnt100 = b.get("count_100m", 0)
    cnt300 = b.get("count_300m", 0)
    if cnt100 >= core_100:
        return {"position": "STRED", "reason": f"{cnt100} domov do 100 m",
                "count_100m": cnt100, "count_300m": cnt300}
    if cnt300 >= edge_300:
        return {"position": "OKRAJ",
                "reason": f"{cnt100} domov do 100 m, {cnt300} do 300 m",
                "count_100m": cnt100, "count_300m": cnt300}
    return {"position": "MIMO", "reason": f"len {cnt300} domov do 300 m",
            "count_100m": cnt100, "count_300m": cnt300}


def is_gem_candidate(access: dict, position: dict) -> bool:
    """
    Kandidat na 'skvost': okraj dediny s priamou/ciastocnou dostupnostou.
    position==OKRAJ AND access in {PRIAMA, CIASTOCNA}
    """
    return (position.get("position") == "OKRAJ"
            and access.get("level") in {"PRIAMA", "CIASTOCNA"})


def _calculate_score(analysis: dict) -> float:
    """Vypocita score 0-100. Logika nezmenena -- len pridane 'buildings' kluc nemeni score."""
    score = 0.0
    road = analysis.get("road", {})
    if road.get("accessible"):
        score += 20
        if road.get("wide_enough"):
            score += 15
    if analysis.get("electricity", {}).get("available"):  score += 25
    if analysis.get("water",       {}).get("available"):  score += 15
    if analysis.get("forest_buffer", {}).get("safe"):     score += 10
    noise = analysis.get("noise", {})
    if noise.get("motorway_safe") and noise.get("railway_safe"): score += 10
    env = analysis.get("environment", {})
    if env.get("landfill_safe") and env.get("industrial_safe"):  score += 5
    return min(round(score, 2), 100.0)


def _haversine_m(lat1, lon1, lat2, lon2) -> float:
    R = 6371000.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _coords(el: dict):
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


def _count_within(elements, lat, lon, key, radius_m: float) -> int:
    """Pocet OSM prvkov so zadanym tagom v danom okruhu."""
    cnt = 0
    for el in elements:
        if el.get("tags", {}).get(key) is None: continue
        c = _coords(el)
        if c and _haversine_m(lat, lon, c[0], c[1]) <= radius_m:
            cnt += 1
    return cnt


def _nearest_val(elements, lat, lon, key):
    best_d, result = 9999.0, None
    for el in elements:
        v = el.get("tags", {}).get(key)
        if v is None: continue
        c = _coords(el)
        if c:
            d = _haversine_m(lat, lon, c[0], c[1])
            if d < best_d: best_d, result = d, v
    return result


def _nearest_num(elements, lat, lon, filter_key, value_key):
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
