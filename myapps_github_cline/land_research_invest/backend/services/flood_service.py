"""
Flood Service
=============
Kontrola ci sa pozemok nachadza v 100-rocnom zaplavovom uzemi (Q100).
Pouziva SHMU WMS GetFeatureInfo - free, bez API kluca.
Kriticky bloker: pozemok v Q100 ziskava score 0.
"""

import requests
from models.result import ServiceResult
from config_loader import is_feature_enabled, get_endpoints

SERVICE_NAME = "flood_service"
TIMEOUT = 15

# WMS parametre pre SHMU Q100 vrstvu
# Nazov vrstvy overit cez GetCapabilities pred pouzitim
WMS_LAYER = "zaplavove_uzemia_q100"
WMS_VERSION = "1.3.0"
WMS_SRS = "EPSG:4326"


def check(lat: float, lon: float) -> ServiceResult:
    """
    Overi ci sa bod nachadza v Q100 zaplavovom uzemi.

    Args:
        lat: zemepisna sirka (WGS-84)
        lon: zemepisna dlzka (WGS-84)

    Returns:
        ServiceResult: score=0 ak v zaplave, score=100 ak mimo
    """
    if not is_feature_enabled("use_flood"):
        return ServiceResult.skip_result(SERVICE_NAME, "use_flood=false")

    try:
        in_flood = _query_shmu_wms(lat, lon)
        score = 0.0 if in_flood else 100.0

        return ServiceResult(
            ok=True,
            score=score,
            data={
                "in_flood_zone_q100": in_flood,
                "risk_level": "HIGH" if in_flood else "NONE",
                "lat": lat,
                "lon": lon,
            },
            source=SERVICE_NAME,
        )
    except Exception as e:
        # Pri chybe WMS vrstvy nepotrestame pozemok - neutralne 50
        return ServiceResult(
            ok=False,
            score=50.0,
            data={"lat": lat, "lon": lon},
            error=f"SHMU WMS nedostupny: {e}",
            source=SERVICE_NAME,
        )


def _query_shmu_wms(lat: float, lon: float) -> bool:
    """
    Posle WMS GetFeatureInfo request na SHMU a vyhodnoti odpoved.

    Args:
        lat, lon: WGS-84 suradnice

    Returns:
        True ak je bod v Q100 zaplavovom uzemi
    """
    endpoints = get_endpoints()
    base_url = endpoints.get("shmu_wms", "https://geo.shmu.sk/wms")

    # Buffer okolo bodu pre BoundingBox (v stupnoch, ~100m)
    delta = 0.001
    bbox = f"{lat - delta},{lon - delta},{lat + delta},{lon + delta}"

    params = {
        "SERVICE": "WMS",
        "VERSION": WMS_VERSION,
        "REQUEST": "GetFeatureInfo",
        "LAYERS": WMS_LAYER,
        "QUERY_LAYERS": WMS_LAYER,
        "INFO_FORMAT": "application/json",
        "BBOX": bbox,
        "CRS": WMS_SRS,
        "WIDTH": "11",
        "HEIGHT": "11",
        "I": "5",
        "J": "5",
    }

    response = requests.get(base_url, params=params, timeout=TIMEOUT)
    response.raise_for_status()

    return _parse_flood_response(response)


def _parse_flood_response(response: requests.Response) -> bool:
    """
    Vyhodnoti odpoved WMS GetFeatureInfo.
    Vrati True ak odpoved obsahuje features (bod je v zaplavovom uzemi).

    Args:
        response: HTTP response z WMS

    Returns:
        True ak v zaplavovom uzemi
    """
    content_type = response.headers.get("content-type", "")

    if "json" in content_type:
        try:
            data = response.json()
            features = data.get("features", [])
            return len(features) > 0
        except Exception:
            pass

    # Fallback: textova odpoved - ak obsahuje suradnice alebo feature data
    text = response.text.lower()
    flood_indicators = ["q100", "zaplavov", "floodzones", "feature"]
    return any(indicator in text for indicator in flood_indicators)
