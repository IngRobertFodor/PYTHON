"""
Geocoding Service
=================
Uses Nominatim (OpenStreetMap) for geocoding and OSRM for travel time calculations.
Both are free and require no API keys.
"""

import requests
import math

NOMINATIM_BASE = "https://nominatim.openstreetmap.org"
OSRM_BASE = "http://router.project-osrm.org"
USER_AGENT = "FodorTravelTIPs/1.0"


def geocode_place(query, lang='en'):
    """
    Convert place name to coordinates using Nominatim.
    Returns list of matching places.
    """
    headers = {'User-Agent': USER_AGENT}
    params = {
        'q': query,
        'format': 'jsonv2',
        'addressdetails': 1,
        'limit': 5,
        'accept-language': lang
    }

    try:
        response = requests.get(
            f"{NOMINATIM_BASE}/search",
            params=params,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data:
            results.append({
                'name': item.get('display_name', ''),
                'lat': float(item.get('lat', 0)),
                'lon': float(item.get('lon', 0)),
                'type': item.get('type', ''),
                'category': item.get('category', ''),
                'country': item.get('address', {}).get('country', ''),
                'country_code': item.get('address', {}).get('country_code', ''),
                'region': _extract_region(item.get('address', {})),
                'importance': item.get('importance', 0)
            })

        return {'results': results}

    except requests.RequestException as e:
        return {'error': f'Geocoding failed: {str(e)}', 'results': []}


def reverse_geocode(lat, lon, lang='en'):
    """
    Convert coordinates to place name using Nominatim.
    """
    headers = {'User-Agent': USER_AGENT}
    params = {
        'lat': lat,
        'lon': lon,
        'format': 'jsonv2',
        'addressdetails': 1,
        'accept-language': lang
    }

    try:
        response = requests.get(
            f"{NOMINATIM_BASE}/reverse",
            params=params,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        address = data.get('address', {})
        return {
            'name': data.get('display_name', ''),
            'lat': lat,
            'lon': lon,
            'city': address.get('city', address.get('town', address.get('village', ''))),
            'country': address.get('country', ''),
            'country_code': address.get('country_code', ''),
            'region': _extract_region(address),
            'region_type': _detect_region_type(address, lat, lon)
        }

    except requests.RequestException as e:
        return {'error': f'Reverse geocoding failed: {str(e)}'}


def calculate_travel_radius(lat, lon, time_minutes, mode='car'):
    """
    Estimate travel radius based on time and mode of transport.
    Uses average speed estimates and OSRM for validation.
    
    Average speeds:
    - car: ~60 km/h (considering roads, not highway)
    - bike: ~15 km/h
    - walk: ~5 km/h
    """
    speed_map = {
        'car': 60,
        'bike': 15,
        'walk': 5
    }

    speed_kmh = speed_map.get(mode, 60)
    # Calculate estimated radius (straight line, ~70% of actual travel distance)
    estimated_radius_km = (speed_kmh * time_minutes / 60) * 0.7

    # Cap at reasonable limits
    estimated_radius_km = min(estimated_radius_km, 200)
    estimated_radius_km = max(estimated_radius_km, 1)

    # Try to validate with OSRM for car mode
    if mode == 'car':
        osrm_radius = _validate_with_osrm(lat, lon, estimated_radius_km, time_minutes)
        if osrm_radius:
            estimated_radius_km = osrm_radius

    return {
        'radius_km': round(estimated_radius_km, 1),
        'time_minutes': time_minutes,
        'mode': mode,
        'speed_kmh': speed_kmh
    }


def _validate_with_osrm(lat, lon, estimated_radius, time_minutes):
    """
    Use OSRM to validate travel radius by checking a few points.
    Returns adjusted radius if OSRM is available.
    """
    try:
        # Test 4 cardinal directions at estimated radius
        test_distance = estimated_radius / 111.0  # degrees approx
        test_points = [
            (lat + test_distance, lon),  # North
            (lat - test_distance, lon),  # South
            (lat, lon + test_distance / math.cos(math.radians(lat))),  # East
            (lat, lon - test_distance / math.cos(math.radians(lat))),  # West
        ]

        durations = []
        for point in test_points:
            url = f"{OSRM_BASE}/route/v1/driving/{lon},{lat};{point[1]},{point[0]}"
            params = {'overview': 'false'}
            resp = requests.get(url, params=params, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('routes'):
                    duration_min = data['routes'][0]['duration'] / 60
                    durations.append(duration_min)

        if durations:
            avg_duration = sum(durations) / len(durations)
            # Adjust radius based on actual vs estimated time
            if avg_duration > 0:
                ratio = time_minutes / avg_duration
                adjusted = estimated_radius * ratio
                return min(max(adjusted, 1), 200)

    except Exception:
        pass

    return None


def _extract_region(address):
    """Extract region/state from address data."""
    return (address.get('state', '') or
            address.get('region', '') or
            address.get('county', ''))


def _detect_region_type(address, lat, lon):
    """
    Detect the type of region for theme coloring.
    Returns: mountain, coastal, urban, rural, default
    """
    # Simple heuristic based on available data
    place_type = address.get('type', '')
    city = address.get('city', '')
    town = address.get('town', '')
    village = address.get('village', '')

    # Urban detection
    if city and not village:
        return 'urban'

    # Coastal detection (very rough - based on known coastal countries/regions)
    country_code = address.get('country_code', '')
    # Add more sophisticated detection if needed

    # Rural/village detection
    if village and not city:
        return 'rural'

    # Default
    if town:
        return 'urban'

    return 'default'