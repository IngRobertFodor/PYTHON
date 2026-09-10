"""
Sluzba terenu
=============
Analyza terenu pozemku: sklon, orientacia svahu, nadmorska vyska,
zosuvne uzemia a radonove riziko.

Zdroje dat:
  - DMR 5.0 WMS (UGKK) - vyskopis SR (LiDAR)
  - SGUDSH WMS          - zosuvne uzemia, radonova mapa

Automatizacia: AUTO (bezi bez brzdenia)
"""

import math
import requests
from models.result import ServiceResult
from config_loader import is_feature_enabled, get_criteria_section, get_endpoints

SERVICE_NAME = "terrain_service"
TIMEOUT = 8   # kratky timeout - pri blokujucich serveroch rychly fallback
GRADIENT_OFFSET_DEG = 0.0009   # ~90m offset pre gradient

ASPECT_SECTORS = [
    (0,    22.5,  "N"),
    (22.5,  67.5, "NE"),
    (67.5, 112.5, "E"),
    (112.5,157.5, "SE"),
    (157.5,202.5, "S"),
    (202.5,247.5, "SW"),
    (247.5,292.5, "W"),
    (292.5,337.5, "NW"),
    (337.5,360.0, "N"),
]


def check(lat: float, lon: float) -> ServiceResult:
    """
    Hlavna funkcia - komplexna analyza terenu pozemku.

    Args:
        lat, lon: WGS-84 suradnice

    Returns:
        ServiceResult so score 0-100 a detailmi
    """
    if not is_feature_enabled("use_terrain"):
        return ServiceResult.skip_result(SERVICE_NAME, "use_terrain=false")

    cfg = get_criteria_section("terrain")
    data = {}
    errors = []

    elevation = _safe_call(get_elevation, errors, "elevation", lat, lon)
    if elevation is not None:
        data["elevation_m"] = elevation

    slope, aspect = None, None
    try:
        slope, aspect = get_slope_and_aspect(lat, lon)
        data["slope_percent"] = slope
        data["aspect"] = aspect
    except Exception as e:
        errors.append(f"slope/aspect: {e}")

    landslide = _safe_call(is_landslide_zone, errors, "landslide", lat, lon)
    if landslide is not None:
        data["in_landslide_zone"] = landslide

    radon = _safe_call(get_radon_risk, errors, "radon", lat, lon)
    if radon is not None:
        data["radon_risk_class"] = radon

    if errors:
        data["errors"] = errors

    # Ak vsetky zlyhali -> neutralne 50
    all_none = all(v is None for v in [elevation, slope, landslide, radon])
    if all_none:
        return ServiceResult(
            ok=False, score=50.0, data=data,
            error="; ".join(errors), source=SERVICE_NAME,
        )

    score = _calculate_score(elevation, slope, aspect, landslide, radon, cfg)
    return ServiceResult(ok=True, score=score, data=data, source=SERVICE_NAME)


def _safe_call(fn, errors: list, label: str, *args):
    """Zavola funkciu a pri chybe zaznaci error, vrati None."""
    try:
        return fn(*args)
    except Exception as e:
        errors.append(f"{label}: {e}")
        return None


# ----------------------------------------------------------------
# Verejne funkcie (pouzitelne aj samostatne)
# ----------------------------------------------------------------

def get_elevation(lat: float, lon: float) -> float:
    """Ziska nadmorsku vysku bodu z DMR WMS GetFeatureInfo."""
    endpoints = get_endpoints()
    wms_url = endpoints.get("zbgis_wms", "https://zbgis.skgeodesy.sk/wms")
    delta = 0.0001
    bbox = f"{lon-delta},{lat-delta},{lon+delta},{lat+delta}"
    resp = requests.get(wms_url, params={
        "SERVICE": "WMS", "VERSION": "1.3.0", "REQUEST": "GetFeatureInfo",
        "LAYERS": "DMR5", "QUERY_LAYERS": "DMR5",
        "INFO_FORMAT": "application/json",
        "BBOX": bbox, "CRS": "EPSG:4326",
        "WIDTH": "11", "HEIGHT": "11", "I": "5", "J": "5",
    }, timeout=TIMEOUT)
    resp.raise_for_status()
    return _parse_elevation_response(resp)


def get_slope_and_aspect(lat: float, lon: float) -> tuple[float, str]:
    """
    Vypocita sklon (%) a orientaciu svahu z DMR 5-bodovej mrizky.
    Returns: (slope_percent, aspect_code)
    """
    o = GRADIENT_OFFSET_DEG
    north = get_elevation(lat + o, lon)
    south = get_elevation(lat - o, lon)
    east  = get_elevation(lat,     lon + o)
    west  = get_elevation(lat,     lon - o)
    dist_m = o * 111_000
    dz_dy = (north - south) / (2 * dist_m)
    dz_dx = (east  - west)  / (2 * dist_m)
    slope = round(math.tan(math.atan(math.sqrt(dz_dx**2 + dz_dy**2))) * 100, 2)
    aspect_deg = math.degrees(math.atan2(-dz_dx, -dz_dy)) % 360
    return slope, _deg_to_aspect(aspect_deg)


def is_landslide_zone(lat: float, lon: float) -> bool:
    """Overi ci sa bod nachadza v zosuvnom uzemi (SGUDSH WMS)."""
    endpoints = get_endpoints()
    wms_url = endpoints.get("sgudsh_wms", "https://gis.geology.sk/arcgis/services")
    delta = 0.001
    bbox = f"{lat-delta},{lon-delta},{lat+delta},{lon+delta}"
    resp = requests.get(wms_url, params={
        "SERVICE": "WMS", "VERSION": "1.3.0", "REQUEST": "GetFeatureInfo",
        "LAYERS": "zosuvy", "QUERY_LAYERS": "zosuvy",
        "INFO_FORMAT": "application/json",
        "BBOX": bbox, "CRS": "EPSG:4326",
        "WIDTH": "11", "HEIGHT": "11", "I": "5", "J": "5",
    }, timeout=TIMEOUT)
    resp.raise_for_status()
    return _parse_feature_response(resp)


def get_radon_risk(lat: float, lon: float) -> int:
    """Ziska triedu radonoveho rizika 1/2/3 (SGUDSH WMS)."""
    endpoints = get_endpoints()
    wms_url = endpoints.get("sgudsh_wms", "https://gis.geology.sk/arcgis/services")
    delta = 0.001
    bbox = f"{lat-delta},{lon-delta},{lat+delta},{lon+delta}"
    resp = requests.get(wms_url, params={
        "SERVICE": "WMS", "VERSION": "1.3.0", "REQUEST": "GetFeatureInfo",
        "LAYERS": "radon", "QUERY_LAYERS": "radon",
        "INFO_FORMAT": "application/json",
        "BBOX": bbox, "CRS": "EPSG:4326",
        "WIDTH": "11", "HEIGHT": "11", "I": "5", "J": "5",
    }, timeout=TIMEOUT)
    resp.raise_for_status()
    return _parse_radon_response(resp)



# ----------------------------------------------------------------
# Scoring
# ----------------------------------------------------------------

def _calculate_score(
    elevation: float | None,
    slope: float | None,
    aspect: str | None,
    landslide: bool | None,
    radon: int | None,
    cfg: dict,
) -> float:
    """
    Vazeny score 0-100.
    Zosuvne uzemia = KRITICKY BLOKER (score 0).
    """
    if landslide is True:
        return 0.0

    score = 100.0
    max_slope        = cfg.get("max_slope_percent", 15)
    pref_slope       = cfg.get("preferred_slope_percent", 5)
    max_elev         = cfg.get("max_elevation_m", 400)
    max_radon        = cfg.get("max_radon_risk_class", 2)
    preferred_aspects = cfg.get("preferred_aspects", ["S", "SE", "SW"])

    # Sklon (az -40 bodov)
    if slope is not None:
        if slope > max_slope:
            score -= 40.0
        elif slope > pref_slope:
            ratio = (slope - pref_slope) / max(max_slope - pref_slope, 1)
            score -= ratio * 25.0

    # Orientacia (az -20 bodov)
    if aspect is not None:
        if aspect not in preferred_aspects:
            score -= 20.0 if aspect in ("N", "NW", "NE") else 10.0

    # Nadmorska vyska (az -20 bodov)
    if elevation is not None and elevation > max_elev:
        score -= min(20.0, ((elevation - max_elev) / 50.0) * 5.0)

    # Radon (az -20 bodov)
    if radon is not None:
        if radon > max_radon:
            score -= 20.0
        elif radon == max_radon:
            score -= 5.0

    return round(max(0.0, min(100.0, score)), 2)


# ----------------------------------------------------------------
# Parsery WMS odpovedi
# ----------------------------------------------------------------

def _parse_elevation_response(response: requests.Response) -> float:
    """Extrahuje nadmorsku vysku z WMS odpovede (JSON alebo text)."""
    ct = response.headers.get("content-type", "")
    if "json" in ct:
        try:
            features = response.json().get("features", [])
            if features:
                props = features[0].get("properties", {})
                for key in ("value", "GRAY_INDEX", "elevation", "vyska", "h"):
                    if key in props:
                        return float(props[key])
        except Exception:
            pass
    for line in response.text.splitlines():
        if "=" in line:
            try:
                val = float(line.split("=")[-1].strip())
                if -100 < val < 3000:
                    return val
            except ValueError:
                continue
    raise RuntimeError(f"Nepodarilo sa parsovat vysku: {response.text[:100]}")


def _parse_feature_response(response: requests.Response) -> bool:
    """True ak WMS odpoved obsahuje features (bod je v zosuvnej zone)."""
    ct = response.headers.get("content-type", "")
    if "json" in ct:
        try:
            return len(response.json().get("features", [])) > 0
        except Exception:
            pass
    text = response.text.lower()
    return any(kw in text for kw in ["feature", "zosuv", "landslide", "geometry"])


def _parse_radon_response(response: requests.Response) -> int:
    """Extrahuje triedu radonoveho rizika 1/2/3. Default 1 ak nerozpozna."""
    ct = response.headers.get("content-type", "")
    if "json" in ct:
        try:
            features = response.json().get("features", [])
            if features:
                props = features[0].get("properties", {})
                for key in ("class", "trieda", "radon_class", "value", "riziko"):
                    if key in props:
                        val = int(props[key])
                        if val in (1, 2, 3):
                            return val
        except Exception:
            pass
    text = response.text.lower()
    if "vysoke" in text or "high" in text:
        return 3
    if "stredne" in text or "medium" in text:
        return 2
    return 1


def _deg_to_aspect(degrees: float) -> str:
    """Prevedie azimut v stupnoch na textovy kod orientacie svahu."""
    for lo, hi, code in ASPECT_SECTORS:
        if lo <= degrees < hi:
            return code
    return "N"

