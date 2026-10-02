"""
Geokodovacia sluzba
===================
Prevod textovej adresy na GPS suradnice (WGS-84) cez Nominatim.
Free, bez API kluca.

F1/F2 (oprava lokality):
  - _clean_address(): vyčistenie pred geokodovanim (odstrani adresu dlznika, utrzky)
  - limit:5 + _best_candidate(): vyber najlepsieho kandidata (place/boundary, najblizsi k BA)
  - geocode_quality: "good" | "far" | "uncertain"
  - fallback: vycistena adresa -> len obec -> None
"""

import re
import math
import requests
from models.result import ServiceResult
from config_loader import is_feature_enabled

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT    = "LandResearchInvest/1.0 (land-parcel-research)"
SERVICE_NAME  = "geocoding_service"
TIMEOUT       = 10

SR_LAT_MIN, SR_LAT_MAX = 47.7, 49.6
SR_LON_MIN, SR_LON_MAX = 16.8, 22.6
BA_LAT, BA_LON         = 48.1486, 17.1077
FAR_KM                 = 120.0

GOOD_CATEGORIES = {"place", "boundary"}
GOOD_TYPES = {
    "city", "town", "village", "hamlet", "suburb",
    "municipality", "district", "administrative",
}


def check(address: str) -> ServiceResult:
    if not is_feature_enabled("use_distance"):
        return ServiceResult.skip_result(SERVICE_NAME, "use_distance=false")
    try:
        result = geocode(address)
        if not result:
            return ServiceResult.error_result(
                SERVICE_NAME, f"Adresa nenajdena: {address}"
            )
        return ServiceResult(ok=True, score=100.0, data=result, source=SERVICE_NAME)
    except Exception as e:
        return ServiceResult.error_result(SERVICE_NAME, str(e))


def geocode(address: str, country_code: str = "sk") -> dict | None:
    """
    F1: limit:5 + vyber najlepsieho kandidata.
    F2: vycisti adresu, fallback len na obec.
    """
    clean = _clean_address(address)
    if not clean:
        return None

    result = _nominatim_best(clean, country_code)
    if result and result["geocode_quality"] != "uncertain":
        return result

    obec = clean.split(",")[0].strip()
    if obec and obec != clean:
        result2 = _nominatim_best(obec, country_code)
        if result2 and result2["geocode_quality"] != "uncertain":
            return result2

    return result or None


def _nominatim_best(query: str, country_code: str) -> dict | None:
    params = {
        "q": query, "format": "jsonv2", "addressdetails": 1,
        "limit": 5, "countrycodes": country_code, "accept-language": "sk",
    }
    r = requests.get(NOMINATIM_URL, params=params,
                     headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    return _best_candidate(data) if data else None


def _best_candidate(candidates: list) -> dict | None:
    if not candidates:
        return None
    in_sr = [c for c in candidates
             if SR_LAT_MIN <= float(c["lat"]) <= SR_LAT_MAX
             and SR_LON_MIN <= float(c["lon"]) <= SR_LON_MAX]
    pool  = in_sr if in_sr else candidates
    good  = [c for c in pool
             if c.get("category") in GOOD_CATEGORIES
             or c.get("type") in GOOD_TYPES]
    chosen = min(good or pool,
                 key=lambda c: _dist_km(float(c["lat"]), float(c["lon"]),
                                        BA_LAT, BA_LON))
    lat, lon = float(chosen["lat"]), float(chosen["lon"])
    dist = _dist_km(lat, lon, BA_LAT, BA_LON)
    in_sr_box = SR_LAT_MIN <= lat <= SR_LAT_MAX and SR_LON_MIN <= lon <= SR_LON_MAX
    is_good   = (chosen.get("category") in GOOD_CATEGORIES
                 or chosen.get("type") in GOOD_TYPES)
    quality   = "good" if (in_sr_box and is_good and dist <= FAR_KM) else \
                "far"  if (in_sr_box and is_good) else "uncertain"
    return {
        "lat": lat, "lon": lon,
        "display_name":    chosen.get("display_name", ""),
        "type":            chosen.get("type", ""),
        "category":        chosen.get("category", ""),
        "address":         chosen.get("address", {}),
        "geocode_quality": quality,
        "dist_km_ba":      round(dist, 1),
    }


def _clean_address(address: str) -> str:
    """
    F2: Vycisti location_text pred geokodovanim.
    Resi: adresy dlznikov (PSC), utrzky nazvu, nezmysly.
    """
    if not address:
        return ""
    s = address.strip()
    if s in ("-", "\u2013", "por.", "...", "n/a", "N/A") or len(s) < 3:
        return ""
    # Adresa dlznika: PSC alebo ulica+cislo domu
    if re.search(r"\b\d{5}\b", s):
        parts = [p.strip() for p in s.split(",")]
        for part in reversed(parts):
            if part and not re.search(r"\d", part) and len(part) >= 3:
                s = part
                break
        else:
            return ""
    # Prilis dlhe utrzky z nazvov inzeratov
    if len(s) > 60:
        s = s.split(",")[0].strip()
    if len(s) > 60:
        return ""
    # Pridaj ", Slovensko" pre lepsiu presnost
    if "slovensko" not in s.lower() and "slovakia" not in s.lower():
        s = s + ", Slovensko"
    return s


def _dist_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def geocode_parcel_number(parcel_number: str, municipality: str) -> dict | None:
    result = geocode(f"{parcel_number}, {municipality}")
    return result or geocode(municipality)

