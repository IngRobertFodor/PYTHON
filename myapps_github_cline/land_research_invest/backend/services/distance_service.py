"""
Distance Service
================
Vypocet vzdialenosti pozemku od Bratislavy a konverzia suradnic.
Pouziva Haversine formulu (bez externe API - 100% offline).
Koordinaty: WGS-84 (GPS) a S-JTSK (slovensky kataster EPSG:5514).
"""

import math
from models.result import ServiceResult
from config_loader import get_criteria, is_feature_enabled

# --- Konstanty ---
BRATISLAVA_LAT = 48.1486
BRATISLAVA_LON = 17.1077
EARTH_RADIUS_KM = 6371.0

# Priblizna priemerná rychlost jazdy mimo BA (km/h)
# Zahrnuje obce, krajske cesty - nie dialnica
AVG_SPEED_KMH = 55.0

SERVICE_NAME = "distance_service"


# ----------------------------------------------------------------
# Verejne funkcie (pouziva agent ako tools)
# ----------------------------------------------------------------

def check(lat: float, lon: float) -> ServiceResult:
    """
    Hlavna funkcia sluzby - overi vzdialenost od Bratislavy.
    Vrati ServiceResult s jednotnym kontraktom.

    Args:
        lat: zemepisna sirka parcely (WGS-84)
        lon: zemepisna dlzka parcely (WGS-84)

    Returns:
        ServiceResult so score 0-100 a detailmi
    """
    if not is_feature_enabled("use_distance"):
        return ServiceResult.skip_result(SERVICE_NAME, "use_distance=false v config")

    try:
        cfg = get_criteria().get("location", {})
        max_km = cfg.get("max_distance_km", 70)

        distance_km = calculate_distance(
            BRATISLAVA_LAT, BRATISLAVA_LON, lat, lon
        )
        drive_min = estimate_drive_time(distance_km)
        within = distance_km <= max_km
        score = _score_distance(distance_km, max_km)

        return ServiceResult(
            ok=True,
            score=score,
            data={
                "distance_km": round(distance_km, 2),
                "drive_time_min": drive_min,
                "max_distance_km": max_km,
                "within_criteria": within,
            },
            source=SERVICE_NAME,
        )

    except Exception as e:
        return ServiceResult.error_result(SERVICE_NAME, str(e))


def calculate_distance(lat1: float, lon1: float,
                       lat2: float, lon2: float) -> float:
    """
    Haversine vzdialenost medzi dvoma GPS bodmi v kilometroch.

    Args:
        lat1, lon1: prvy bod (WGS-84 stupne)
        lat2, lon2: druhy bod (WGS-84 stupne)

    Returns:
        Vzdialenost v km (float)
    """
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (math.sin(d_lat / 2) ** 2
         + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_KM * c


def distance_from_bratislava(lat: float, lon: float) -> float:
    """
    Skratka: vzdialenost bodu od centra Bratislavy v km.

    Args:
        lat, lon: suradnice bodu (WGS-84)

    Returns:
        Vzdialenost v km
    """
    return calculate_distance(BRATISLAVA_LAT, BRATISLAVA_LON, lat, lon)


def estimate_drive_time(distance_km: float) -> int:
    """
    Odhad casu jazdy autom v minutach.
    Pouziva priemernu rychlost AVG_SPEED_KMH (55 km/h).

    Args:
        distance_km: vzdialenost v km

    Returns:
        Odhadovany cas jazdy v minutach (int)
    """
    if distance_km < 0:
        return 0
    return round((distance_km / AVG_SPEED_KMH) * 60)


def wgs84_to_jtsk(lat: float, lon: float) -> tuple[float, float]:
    """
    Konverzia WGS-84 (GPS) na S-JTSK (EPSG:5514) pre kataster SR.
    Pouziva pyproj kniznicu.

    Args:
        lat: zemepisna sirka (WGS-84)
        lon: zemepisna dlzka (WGS-84)

    Returns:
        (x, y) v S-JTSK suradniciach (metre)
    """
    from pyproj import Transformer
    transformer = Transformer.from_crs(
        "EPSG:4326", "EPSG:5514", always_xy=True
    )
    x, y = transformer.transform(lon, lat)
    return x, y


def jtsk_to_wgs84(x: float, y: float) -> tuple[float, float]:
    """
    Konverzia S-JTSK (EPSG:5514) na WGS-84 (GPS).

    Args:
        x, y: S-JTSK suradnice (metre)

    Returns:
        (lat, lon) vo WGS-84 stupnoch
    """
    from pyproj import Transformer
    transformer = Transformer.from_crs(
        "EPSG:5514", "EPSG:4326", always_xy=True
    )
    lon, lat = transformer.transform(x, y)
    return lat, lon


# ----------------------------------------------------------------
# Interni pomocne funkcie
# ----------------------------------------------------------------

def _score_distance(distance_km: float, max_km: float) -> float:
    """
    Vypocita score 0-100 podla vzdialenosti.
    Linearny pokles: 0 km = 100, max_km = 0.
    Nad max_km = 0 (nesplna kriterium).

    Args:
        distance_km: skutocna vzdialenost
        max_km: maximalna povolena vzdialenost z configu

    Returns:
        Score 0.0 - 100.0
    """
    if distance_km <= 0:
        return 100.0
    if distance_km >= max_km:
        return 0.0
    return round(100.0 * (1.0 - distance_km / max_km), 2)
