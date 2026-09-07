"""
Sluzba chranených uzemi
========================
Kontrola ochrannych pasiem a chranenych uzemi okolo pozemku.

Kontroluje:
  - Natura 2000 (SKUEV, SKCHVU) - europska siet chranenych uzemi
  - CHKO - chranena krajinna oblast
  - NPR / PR - narodna/prirodna rezervacia
  - NP - narodny park

Zdroj: SOP SR WMS (Statna ochrana prirody SR) - otvorene data
Automatizacia: AUTO (bezi bez brzdenia)

Poznamka: VVN, VTL a les su pokryte v overpass_service cez OSM.
Archeologicke zony (KPU) su MANUAL - ziadne verejne API.
"""

import requests
from models.result import ServiceResult
from config_loader import is_feature_enabled, get_criteria_section, get_endpoints

SERVICE_NAME = "protected_service"
TIMEOUT = 20

# SOP SR WMS vrstvy (overit GetCapabilities pred pouzitim)
# Zdroj: https://maps.sopsr.sk/geoserver/wms
WMS_LAYERS = {
    "natura2000_hab": "SKUEV",    # Natura 2000 - Stanovistne oblasti
    "natura2000_birds": "SKCHVU", # Natura 2000 - Chranene vtacie uzemia
    "chko": "CHKO",               # Chranena krajinna oblast
    "npr": "NPR",                 # Narodna prirodna rezervacia
    "pr": "PR",                   # Prirodna rezervacia
    "np": "NP",                   # Narodny park
}


def check(lat: float, lon: float) -> ServiceResult:
    """
    Hlavna funkcia - kontrola ochrannych pasiem.

    Args:
        lat, lon: WGS-84 suradnice

    Returns:
        ServiceResult so score 0-100 a zoznamom najdenych oblasti
    """
    if not is_feature_enabled("use_natura_chko"):
        return ServiceResult.skip_result(SERVICE_NAME, "use_natura_chko=false")

    try:
        findings = _query_all_layers(lat, lon)
        score = _calculate_score(findings)

        return ServiceResult(
            ok=True,
            score=score,
            data={
                "in_natura2000":   findings.get("natura2000_hab", False) or
                                   findings.get("natura2000_birds", False),
                "in_chko":         findings.get("chko", False),
                "in_npr_pr":       findings.get("npr", False) or
                                   findings.get("pr", False),
                "in_np":           findings.get("np", False),
                "findings":        findings,
                "any_protected":   any(findings.values()),
            },
            source=SERVICE_NAME,
        )
    except Exception as e:
        return ServiceResult(
            ok=False, score=50.0, data={},
            error=f"SOP SR WMS nedostupny: {e}", source=SERVICE_NAME,
        )


def _query_all_layers(lat: float, lon: float) -> dict[str, bool]:
    """
    Dotaze sa na vsetky WMS vrstvy paralelne (sekvenčne, s fallback).

    Returns:
        {layer_key: bool} - True ak sa bod nachadza v danej oblasti
    """
    findings = {}
    errors = []

    for layer_key in WMS_LAYERS:
        try:
            findings[layer_key] = _query_wms_layer(lat, lon, layer_key)
        except Exception as e:
            findings[layer_key] = False
            errors.append(f"{layer_key}: {e}")

    return findings


def _query_wms_layer(lat: float, lon: float, layer_key: str) -> bool:
    """
    Dotaze sa na jednu WMS vrstvu.

    Returns:
        True ak sa bod nachadza v danej chranej oblasti
    Raises:
        RuntimeError ak WMS neodpovie
    """
    endpoints = get_endpoints()
    wms_url = endpoints.get("sop_sr_wms", "https://maps.sopsr.sk/geoserver/wms")
    layer_name = WMS_LAYERS[layer_key]

    delta = 0.001
    bbox = f"{lat-delta},{lon-delta},{lat+delta},{lon+delta}"

    resp = requests.get(wms_url, params={
        "SERVICE": "WMS",
        "VERSION": "1.3.0",
        "REQUEST": "GetFeatureInfo",
        "LAYERS": layer_name,
        "QUERY_LAYERS": layer_name,
        "INFO_FORMAT": "application/json",
        "BBOX": bbox,
        "CRS": "EPSG:4326",
        "WIDTH": "11",
        "HEIGHT": "11",
        "I": "5",
        "J": "5",
    }, timeout=TIMEOUT)
    resp.raise_for_status()
    return _parse_protected_response(resp)


def _parse_protected_response(response: requests.Response) -> bool:
    """
    True ak WMS odpoved obsahuje features (bod je v chranej oblasti).
    """
    ct = response.headers.get("content-type", "")
    if "json" in ct:
        try:
            return len(response.json().get("features", [])) > 0
        except Exception:
            pass
    text = response.text.lower()
    return any(kw in text for kw in ["feature", "natura", "chko", "rezerv", "geometry"])


def _calculate_score(findings: dict[str, bool]) -> float:
    """
    Score 0-100 podla najdenych ochrannych pasiem.

    Logika:
    - Ziadne pasmo     -> 100 (idealne)
    - NP alebo NPR/PR  -> 0   (stavba prakticky nemozna)
    - CHKO             -> 20  (stavba silne obmedzena)
    - Natura 2000      -> 40  (EIA povinnost, oneskorenie)
    """
    if not any(findings.values()):
        return 100.0

    # Najvaznejsie obmedzenia (kriticky bloker)
    if findings.get("np") or findings.get("npr") or findings.get("pr"):
        return 0.0

    score = 100.0

    if findings.get("chko"):
        score -= 80.0   # -> 20

    if findings.get("natura2000_hab") or findings.get("natura2000_birds"):
        score -= min(60.0, score - 10.0)  # min score 10 ak uz nie je 20 z CHKO

    return round(max(0.0, min(100.0, score)), 2)
