"""
Sluzba geometrie parciel (ZBGIS)
=================================
Geometricka analyza parcely z katastra SR cez ZBGIS WFS.

Zistuje:
  - Vymera (m2)
  - Sirka a dlzka parcely (m)
  - Pravidelnost tvaru (0-1, kde 1=dokonaly obdlznik)
  - Ci splna minimalne rozmery pre stavbu RD

Zdroj: ZBGIS WFS (UGKK) - otvorene data, bez API kluca
Automatizacia: AUTO (bezi bez brzdenia)

Poznamka k endpointom:
  WFS GetFeature s CQL filtrom podla cisla parcely (napr. "1234/5")
  alebo podla BBox okolo GPS suradnic.
  Geometria je v S-JTSK (EPSG:5514), konverzia cez pyproj.
"""

import math
import requests
from models.result import ServiceResult
from config_loader import is_feature_enabled, get_criteria_section, get_endpoints

SERVICE_NAME = "zbgis_service"
TIMEOUT = 8   # kratky timeout - pri blokujucich serveroch rychly fallback

WFS_TYPENAME = "KN_PARCELY"    # overit GetCapabilities pred pouzitim
WFS_VERSION  = "2.0.0"


def check(lat: float, lon: float,
          parcel_number: str | None = None) -> ServiceResult:
    """
    Hlavna funkcia - geometricka analyza parcely.

    Args:
        lat, lon: WGS-84 suradnice (pouziju sa ak parcel_number nie je znamy)
        parcel_number: cislo parcely napr. "1234/5" (volitelne, zlepsuje presnost)

    Returns:
        ServiceResult so score 0-100 a geometrickymi detailmi
    """
    if not is_feature_enabled("use_distance"):
        return ServiceResult.skip_result(SERVICE_NAME, "feature disabled")

    cfg = get_criteria_section("parcel")

    try:
        geometry = get_parcel_geometry(lat, lon, parcel_number)
        score = _calculate_score(geometry, cfg)

        return ServiceResult(
            ok=True,
            score=score,
            data={
                "area_sqm": geometry["area_sqm"],
                "width_m": geometry["width_m"],
                "length_m": geometry["length_m"],
                "shape_regularity": geometry["shape_regularity"],
                "meets_min_area": geometry["area_sqm"] >= cfg.get("min_area_sqm", 600),
                "meets_min_width": geometry["width_m"] >= cfg.get("min_width_m", 15),
                "parcel_number": parcel_number or "",
            },
            source=SERVICE_NAME,
        )
    except Exception as e:
        return ServiceResult(
            ok=False, score=50.0, data={},
            error=f"ZBGIS WFS nedostupny: {e}", source=SERVICE_NAME,
        )


def get_parcel_geometry(lat: float, lon: float,
                        parcel_number: str | None = None) -> dict:
    """
    Ziska geometriu parcely z ZBGIS WFS.

    Strategia:
    1. Ak je parcel_number -> WFS filter podla cisla parcely
    2. Inak -> WFS BBox filter okolo GPS suradnic (vrati blizku parcelu)

    Args:
        lat, lon: WGS-84 suradnice
        parcel_number: cislo parcely (volitelne)

    Returns:
        {area_sqm, width_m, length_m, shape_regularity, bbox}

    Raises:
        RuntimeError ak WFS neodpovie alebo data chybaju
    """
    endpoints = get_endpoints()
    wfs_url = endpoints.get("zbgis_wfs", "https://zbgis.skgeodesy.sk/wfs/default")

    if parcel_number:
        params = _build_parcel_number_params(parcel_number)
    else:
        params = _build_bbox_params(lat, lon)

    resp = requests.get(wfs_url, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    return _parse_wfs_response(resp, lat, lon)


def _build_parcel_number_params(parcel_number: str) -> dict:
    """WFS GetFeature filter podla cisla parcely."""
    cql = f"CISLO_PARCELY='{parcel_number}'"
    return {
        "SERVICE": "WFS",
        "VERSION": WFS_VERSION,
        "REQUEST": "GetFeature",
        "TYPENAMES": WFS_TYPENAME,
        "OUTPUTFORMAT": "application/json",
        "CQL_FILTER": cql,
        "COUNT": "1",
    }


def _build_bbox_params(lat: float, lon: float, delta: float = 0.0003) -> dict:
    """WFS GetFeature BBox filter okolo GPS suradnic (~30m x 30m)."""
    # ZBGIS pouziva S-JTSK (EPSG:5514) pre BBox
    try:
        from pyproj import Transformer
        tr = Transformer.from_crs("EPSG:4326", "EPSG:5514", always_xy=True)
        x, y = tr.transform(lon, lat)
        # Buffer ~50m v S-JTSK
        buf = 50
        bbox = f"{x-buf},{y-buf},{x+buf},{y+buf},EPSG:5514"
    except ImportError:
        # Fallback: WGS-84 BBox
        bbox = f"{lon-delta},{lat-delta},{lon+delta},{lat+delta},EPSG:4326"

    return {
        "SERVICE": "WFS",
        "VERSION": WFS_VERSION,
        "REQUEST": "GetFeature",
        "TYPENAMES": WFS_TYPENAME,
        "OUTPUTFORMAT": "application/json",
        "BBOX": bbox,
        "COUNT": "1",
    }


# ----------------------------------------------------------------
# Parsing a geometricke vypocty
# ----------------------------------------------------------------

def _parse_wfs_response(response: requests.Response,
                        lat: float, lon: float) -> dict:
    """
    Parsuje WFS GeoJSON odpoved a vypocita geometricke vlastnosti parcely.

    Returns:
        {area_sqm, width_m, length_m, shape_regularity, bbox}
    Raises:
        RuntimeError ak data chybaju
    """
    ct = response.headers.get("content-type", "")

    if "json" in ct:
        try:
            data = response.json()
            features = data.get("features", [])
            if features:
                feature = features[0]
                props = feature.get("properties", {})
                geometry = feature.get("geometry", {})

                # Skus ziskat vymeru priamo z properties
                area = _extract_area(props)

                # Ziskaj BBox z geometrie alebo properties
                bbox = _extract_bbox(geometry, props)

                if bbox and area:
                    width, length = _bbox_to_dimensions(bbox)
                    regularity = _calculate_regularity(area, width, length)
                    return {
                        "area_sqm": area,
                        "width_m": width,
                        "length_m": length,
                        "shape_regularity": regularity,
                        "bbox": bbox,
                    }
        except Exception:
            pass

    raise RuntimeError(f"Nepodarilo sa parsovat WFS: {response.text[:200]}")


def _extract_area(props: dict) -> float | None:
    """Extrahuje vymeru z WFS properties (skusa rozne nazvy poli)."""
    for key in ("VYMERA", "vymera", "area", "AREA", "SHAPE_AREA", "shape_area"):
        if key in props:
            try:
                return float(props[key])
            except (ValueError, TypeError):
                continue
    return None


def _extract_bbox(geometry: dict, props: dict) -> list | None:
    """
    Extrahuje BBox [minX, minY, maxX, maxY] z GeoJSON geometrie alebo properties.
    Suradnice su v S-JTSK (EPSG:5514) - metre.
    """
    # Skus bbox z properties
    for key in ("bbox", "BBOX", "envelope"):
        if key in props:
            try:
                bbox = props[key]
                if isinstance(bbox, (list, tuple)) and len(bbox) == 4:
                    return [float(v) for v in bbox]
            except Exception:
                pass

    # Vypocitaj z coordinates geometrie
    coords = _extract_all_coords(geometry)
    if not coords:
        return None

    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    return [min(xs), min(ys), max(xs), max(ys)]


def _extract_all_coords(geometry: dict) -> list:
    """Rekurzivne extrahuje vsetky suradnice z GeoJSON geometrie."""
    if not geometry:
        return []
    coords = geometry.get("coordinates", [])
    geom_type = geometry.get("type", "")

    if geom_type == "Point":
        return [coords] if coords else []
    elif geom_type in ("LineString", "MultiPoint"):
        return coords
    elif geom_type in ("Polygon", "MultiLineString"):
        result = []
        for ring in coords:
            result.extend(ring if isinstance(ring[0], (list, tuple)) else [ring])
        return result
    elif geom_type == "MultiPolygon":
        result = []
        for polygon in coords:
            for ring in polygon:
                result.extend(ring)
        return result
    return []


def _bbox_to_dimensions(bbox: list) -> tuple[float, float]:
    """
    Vypocita sirku a dlzku z BBox [minX, minY, maxX, maxY].
    Vrati (sirka, dlzka) kde sirka <= dlzka.
    """
    dx = abs(bbox[2] - bbox[0])
    dy = abs(bbox[3] - bbox[1])
    width = min(dx, dy)
    length = max(dx, dy)
    return round(width, 2), round(length, 2)


def _calculate_regularity(area: float, width: float, length: float) -> float:
    """
    Pravidelnost tvaru parcely (0-1).
    1.0 = dokonaly obdlznik (plocha = sirka * dlzka)
    Nizsia hodnota = nepravidelny tvar (L-tvar, trojuholnik...)
    """
    if width <= 0 or length <= 0:
        return 0.0
    envelope_area = width * length
    if envelope_area <= 0:
        return 0.0
    return round(min(1.0, area / envelope_area), 3)


# ----------------------------------------------------------------
# Scoring
# ----------------------------------------------------------------

def _calculate_score(geometry: dict, cfg: dict) -> float:
    """
    Score 0-100 na zaklade geometrickych vlastnosti parcely.

    Kriteria:
    - Vymera (min/max z configu)
    - Sirka (min z configu, pre stavebnu caru)
    - Tvar (pravidelnost)
    """
    area   = geometry.get("area_sqm", 0)
    width  = geometry.get("width_m", 0)
    length = geometry.get("length_m", 0)
    reg    = geometry.get("shape_regularity", 0)

    min_area = cfg.get("min_area_sqm", 600)
    max_area = cfg.get("max_area_sqm", 1500)
    min_width = cfg.get("min_width_m", 15)
    min_reg  = cfg.get("min_shape_regularity", 0.5)

    score = 0.0

    # Vymera (40 bodov)
    if area >= min_area:
        if area <= max_area:
            score += 40.0
        else:
            # Nad max - stale OK ale mensi bonus
            score += 30.0
    else:
        # Pod min - proporcionalne
        score += max(0.0, (area / min_area) * 20.0)

    # Sirka (35 bodov) - kriticky pre stavebnu caru
    if width >= min_width:
        score += 35.0
    elif width > 0:
        score += max(0.0, (width / min_width) * 20.0)

    # Tvar (25 bodov)
    if reg >= min_reg:
        score += 25.0 * min(1.0, reg)
    elif reg > 0:
        score += (reg / min_reg) * 12.0

    return round(min(100.0, score), 2)

