"""
Geocoding Service
=================
Prevod textovej adresy na GPS suradnice (WGS-84) cez Nominatim.
Rovnaky pristup ako v my_travel_tips - free, bez API kluca.
"""

import requests
from models.result import ServiceResult
from config_loader import is_feature_enabled

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "LandResearchInvest/1.0 (land-parcel-research)"
SERVICE_NAME = "geocoding_service"
TIMEOUT = 10


def check(address: str) -> ServiceResult:
    """
    Hlavna funkcia sluzby - prevedie adresu na GPS suradnice.

    Args:
        address: textova adresa, napr. "Senec, Slovakia"

    Returns:
        ServiceResult s lat/lon v data dict
    """
    if not is_feature_enabled("use_distance"):
        return ServiceResult.skip_result(SERVICE_NAME, "use_distance=false")

    try:
        result = geocode(address)
        if not result:
            return ServiceResult.error_result(
                SERVICE_NAME, f"Adresa nenajdena: {address}"
            )
        return ServiceResult(
            ok=True,
            score=100.0,
            data=result,
            source=SERVICE_NAME,
        )
    except Exception as e:
        return ServiceResult.error_result(SERVICE_NAME, str(e))


def geocode(address: str, country_code: str = "sk") -> dict | None:
    """
    Prevedie textovu adresu na GPS suradnice cez Nominatim.

    Args:
        address: napr. "Senec" alebo "Hlavna 1, Trnava"
        country_code: ISO kod krajiny, default "sk"

    Returns:
        {lat, lon, display_name, type} alebo None ak nenajdene
    """
    params = {
        "q": address,
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": 1,
        "countrycodes": country_code,
        "accept-language": "sk",
    }
    headers = {"User-Agent": USER_AGENT}

    response = requests.get(
        NOMINATIM_URL, params=params, headers=headers, timeout=TIMEOUT
    )
    response.raise_for_status()
    data = response.json()

    if not data:
        return None

    item = data[0]
    return {
        "lat": float(item["lat"]),
        "lon": float(item["lon"]),
        "display_name": item.get("display_name", ""),
        "type": item.get("type", ""),
        "address": item.get("address", {}),
    }


def geocode_parcel_number(parcel_number: str, municipality: str) -> dict | None:
    """
    Pokusi sa geokodovat parcelu podla cisla a nazvu obce.
    Fallback: geokoduje len obec.

    Args:
        parcel_number: napr. "1234/5"
        municipality: napr. "Senec"

    Returns:
        {lat, lon, ...} alebo None
    """
    # Skus najprv kombinaciu
    result = geocode(f"{parcel_number}, {municipality}")
    if result:
        return result
    # Fallback: len obec
    return geocode(municipality)
