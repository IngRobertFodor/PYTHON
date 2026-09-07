"""
BPEJ Service
============
Kontrola bonity pody (BPEJ) a odhad odvodov za vynatie z PPF.

Ochranné triedy pody 1-9:
  1-4 = vysoko chranena poda, drahe vynatie (tisice EUR/m2) -> nízky score
  5-6 = stredne chranena -> stredny score
  7-9 = nizka ochrana, lacne alebo bez odvodov -> vysoky score

Zdroj: BPEJ WMS (geodata.gov.sk / VUPOP)
Automatizacia: AUTO (bezi bez brzdenia)
"""

import requests
from models.result import ServiceResult
from config_loader import is_feature_enabled, get_criteria_section, get_endpoints

SERVICE_NAME = "bpej_service"
TIMEOUT = 20

# Orientacne odvody za vynatie z PPF (EUR/m2) podla ochrannej triedy
ODVODY_PER_CLASS = {
    1: 15.00, 2: 10.00, 3: 6.00, 4: 3.00,
    5: 1.50,  6: 0.50,  7: 0.10, 8: 0.05, 9: 0.00,
}


def check(lat: float, lon: float) -> ServiceResult:
    """
    Hlavna funkcia - kontrola bonity pody pozemku.

    Returns:
        ServiceResult so score 0-100, BPEJ kodom, triedou a odvodmi
    """
    if not is_feature_enabled("use_bpej"):
        return ServiceResult.skip_result(SERVICE_NAME, "use_bpej=false")

    cfg = get_criteria_section("soil")

    try:
        bpej_code, protection_class = get_bpej(lat, lon)
        odvody = estimate_odvody(protection_class)
        score = _calculate_score(protection_class, cfg)

        return ServiceResult(
            ok=True, score=score,
            data={
                "bpej_code": bpej_code,
                "protection_class": protection_class,
                "estimated_odvody_eur_per_m2": odvody,
                "high_cost_warning": protection_class in cfg.get("high_cost_classes", [1,2,3,4]),
                "suitable_for_construction": protection_class > 4,
            },
            source=SERVICE_NAME,
        )
    except Exception as e:
        return ServiceResult(
            ok=False, score=50.0, data={},
            error=f"BPEJ WMS nedostupny: {e}", source=SERVICE_NAME,
        )


def get_bpej(lat: float, lon: float) -> tuple[str, int]:
    """
    Ziska BPEJ kod a ochrannu triedu z WMS GetFeatureInfo.

    Returns:
        (bpej_code, protection_class) napr. ("07020", 5)
    Raises:
        RuntimeError ak WMS neodpovie
    """
    endpoints = get_endpoints()
    wms_url = endpoints.get("bpej_wms", "https://geodata.gov.sk/geoserver/wms")
    delta = 0.0001
    bbox = f"{lon-delta},{lat-delta},{lon+delta},{lat+delta}"

    resp = requests.get(wms_url, params={
        "SERVICE": "WMS", "VERSION": "1.3.0", "REQUEST": "GetFeatureInfo",
        "LAYERS": "bpej", "QUERY_LAYERS": "bpej",
        "INFO_FORMAT": "application/json",
        "BBOX": bbox, "CRS": "EPSG:4326",
        "WIDTH": "11", "HEIGHT": "11", "I": "5", "J": "5",
    }, timeout=TIMEOUT)
    resp.raise_for_status()
    return _parse_bpej_response(resp)


def estimate_odvody(protection_class: int, area_sqm: float = 1.0) -> float:
    """
    Odhadne odvody za vynatie pody z PPF.

    Args:
        protection_class: ochranná trieda 1-9
        area_sqm: plocha (default 1.0 = vrati EUR/m2)

    Returns:
        Odhad odvodov v EUR
    """
    rate = ODVODY_PER_CLASS.get(_clamp_class(protection_class), 0.0)
    return round(rate * area_sqm, 2)


# ----------------------------------------------------------------
# Scoring
# ----------------------------------------------------------------

def _calculate_score(protection_class: int, cfg: dict) -> float:
    """
    Score 0-100 na zaklade ochrannej triedy pody.

    Triedy 1-4 (high_cost): 0-30 (drahe vynatie z PPF)
    Triedy 5-6:              50-70 (stredne)
    Triedy 7-9:              80-100 (lacne alebo bez odvodov)
    """
    high_cost = cfg.get("high_cost_classes", [1, 2, 3, 4])
    sorted_hc = sorted(high_cost)

    if protection_class in sorted_hc:
        idx = sorted_hc.index(protection_class)
        return round(idx * (30.0 / max(len(sorted_hc) - 1, 1)), 2)

    # Nad high_cost triedami: linearny 50 -> 100
    above = protection_class - max(sorted_hc)   # napr. trieda 5: 5-4=1
    max_above = 9 - max(sorted_hc)              # napr. 9-4=5
    score = 50.0 + (above / max(max_above, 1)) * 50.0
    return round(min(100.0, max(0.0, score)), 2)


# ----------------------------------------------------------------
# Parser WMS odpovede
# ----------------------------------------------------------------

def _parse_bpej_response(response: requests.Response) -> tuple[str, int]:
    """
    Extrahuje BPEJ kod a ochrannu triedu z WMS GetFeatureInfo.

    Returns:
        (bpej_code, protection_class)
    Raises:
        RuntimeError ak sa nepodarilo parsovat
    """
    ct = response.headers.get("content-type", "")

    if "json" in ct:
        try:
            features = response.json().get("features", [])
            if features:
                props = features[0].get("properties", {})
                bpej_code = (
                    props.get("BPEJ") or props.get("bpej") or
                    props.get("kod") or props.get("code") or ""
                )
                pclass = (
                    props.get("OT") or props.get("ot") or
                    props.get("ochrana") or props.get("protection_class") or
                    props.get("trieda")
                )
                if pclass is not None:
                    return str(bpej_code or "unknown"), _clamp_class(int(pclass))
                if bpej_code and len(str(bpej_code)) >= 2:
                    return str(bpej_code), _estimate_class_from_code(str(bpej_code))
        except Exception:
            pass

    raise RuntimeError(f"Nepodarilo sa parsovat BPEJ: {response.text[:200]}")


def _clamp_class(value: int) -> int:
    """Obmedzí ochrannu triedu na platny rozsah 1-9."""
    return max(1, min(9, int(value)))


def _estimate_class_from_code(bpej_code: str) -> int:
    """
    Priblizny odhad ochrannej triedy z BPEJ kodu (fallback).
    HPJ (2-3. cifra): nizsia = kvalitnejsia poda = vyssia ochrana.
    """
    try:
        hpj = int(bpej_code[1:3])
        if hpj <= 20: return 2
        if hpj <= 40: return 4
        if hpj <= 60: return 6
        return 8
    except (ValueError, IndexError):
        return 5

