"""
Weather Service
===============
Uses Open-Meteo API for weather forecasts.
Completely free, no API key required.
Supports up to 16-day forecast and multi-point grid for area visualization.
"""

import requests
import math
from datetime import datetime, timedelta

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Weather code descriptions
WEATHER_CODES = {
    0: {'sk': 'Jasno', 'en': 'Clear sky', 'icon': '☀️'},
    1: {'sk': 'Prevažne jasno', 'en': 'Mainly clear', 'icon': '🌤️'},
    2: {'sk': 'Čiastočne zamračené', 'en': 'Partly cloudy', 'icon': '⛅'},
    3: {'sk': 'Zamračené', 'en': 'Overcast', 'icon': '☁️'},
    45: {'sk': 'Hmla', 'en': 'Fog', 'icon': '🌫️'},
    48: {'sk': 'Námraza', 'en': 'Rime fog', 'icon': '🌫️'},
    51: {'sk': 'Mrholenie slabé', 'en': 'Light drizzle', 'icon': '🌦️'},
    53: {'sk': 'Mrholenie', 'en': 'Moderate drizzle', 'icon': '🌦️'},
    55: {'sk': 'Mrholenie silné', 'en': 'Dense drizzle', 'icon': '🌧️'},
    61: {'sk': 'Dážď slabý', 'en': 'Slight rain', 'icon': '🌦️'},
    63: {'sk': 'Dážď', 'en': 'Moderate rain', 'icon': '🌧️'},
    65: {'sk': 'Dážď silný', 'en': 'Heavy rain', 'icon': '🌧️'},
    66: {'sk': 'Mrznúci dážď slabý', 'en': 'Light freezing rain', 'icon': '🌨️'},
    67: {'sk': 'Mrznúci dážď silný', 'en': 'Heavy freezing rain', 'icon': '🌨️'},
    71: {'sk': 'Sneženie slabé', 'en': 'Slight snow', 'icon': '🌨️'},
    73: {'sk': 'Sneženie', 'en': 'Moderate snow', 'icon': '❄️'},
    75: {'sk': 'Sneženie silné', 'en': 'Heavy snow', 'icon': '❄️'},
    77: {'sk': 'Snehové zrná', 'en': 'Snow grains', 'icon': '❄️'},
    80: {'sk': 'Prehánky slabé', 'en': 'Slight rain showers', 'icon': '🌦️'},
    81: {'sk': 'Prehánky', 'en': 'Moderate rain showers', 'icon': '🌧️'},
    82: {'sk': 'Prehánky silné', 'en': 'Violent rain showers', 'icon': '⛈️'},
    85: {'sk': 'Snehové prehánky slabé', 'en': 'Slight snow showers', 'icon': '🌨️'},
    86: {'sk': 'Snehové prehánky silné', 'en': 'Heavy snow showers', 'icon': '❄️'},
    95: {'sk': 'Búrka', 'en': 'Thunderstorm', 'icon': '⛈️'},
    96: {'sk': 'Búrka s krupobitím', 'en': 'Thunderstorm with hail', 'icon': '⛈️'},
    99: {'sk': 'Búrka so silným krupobitím', 'en': 'Thunderstorm with heavy hail', 'icon': '⛈️'},
}


def get_weather_for_point(lat, lon, date=''):
    """
    Get weather forecast for a single point.
    If date is provided, returns forecast for that specific date.
    Otherwise returns today's forecast.
    """
    target_date = _parse_date(date)

    params = {
        'latitude': lat,
        'longitude': lon,
        'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,windspeed_10m_max,uv_index_max',
        'timezone': 'auto',
        'start_date': target_date.strftime('%Y-%m-%d'),
        'end_date': target_date.strftime('%Y-%m-%d')
    }

    try:
        response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        daily = data.get('daily', {})
        if not daily.get('time'):
            return {'error': 'No weather data available for this date'}

        weather_code = daily.get('weathercode', [0])[0]
        weather_info = WEATHER_CODES.get(weather_code, WEATHER_CODES[0])

        return {
            'date': target_date.strftime('%Y-%m-%d'),
            'lat': lat,
            'lon': lon,
            'temperature_max': daily.get('temperature_2m_max', [0])[0],
            'temperature_min': daily.get('temperature_2m_min', [0])[0],
            'precipitation_mm': daily.get('precipitation_sum', [0])[0],
            'wind_speed_max': daily.get('windspeed_10m_max', [0])[0],
            'uv_index': daily.get('uv_index_max', [0])[0],
            'weather_code': weather_code,
            'weather_description_sk': weather_info.get('sk', ''),
            'weather_description_en': weather_info.get('en', ''),
            'weather_icon': weather_info.get('icon', '🌤️'),
            'is_outdoor_friendly': _is_outdoor_friendly(weather_code, daily),
            'outdoor_recommendation_sk': _outdoor_recommendation(weather_code, 'sk'),
            'outdoor_recommendation_en': _outdoor_recommendation(weather_code, 'en'),
        }

    except requests.RequestException as e:
        return {'error': f'Weather fetch failed: {str(e)}'}


def get_weather_grid(lat, lon, radius_km, date=''):
    """
    Get weather for a 3x3 grid of points covering the search area.
    This provides weather visualization for the entire travel region.
    """
    target_date = _parse_date(date)

    # Generate 9 points (3x3 grid) within the radius
    grid_points = _generate_grid(lat, lon, radius_km, 3)

    # Fetch weather for all grid points in one efficient request
    results = []
    for point in grid_points:
        weather = get_weather_for_point(point['lat'], point['lon'], target_date.strftime('%Y-%m-%d'))
        if not weather.get('error'):
            weather['grid_position'] = point.get('position', '')
            results.append(weather)

    # Determine overall area weather summary
    summary = _area_summary(results)

    return {
        'date': target_date.strftime('%Y-%m-%d'),
        'center': {'lat': lat, 'lon': lon},
        'radius_km': radius_km,
        'grid_points': results,
        'summary': summary
    }


def _generate_grid(center_lat, center_lon, radius_km, grid_size=3):
    """
    Generate a grid of points covering the area.
    Returns list of {lat, lon, position} dicts.
    """
    points = []
    # Convert km to degrees (approximate)
    lat_offset = radius_km / 111.0
    lon_offset = radius_km / (111.0 * math.cos(math.radians(center_lat)))

    positions = ['NW', 'N', 'NE', 'W', 'C', 'E', 'SW', 'S', 'SE']
    idx = 0

    for i in range(grid_size):
        for j in range(grid_size):
            lat = center_lat + lat_offset * (1 - i)  # Top to bottom
            lon = center_lon + lon_offset * (j - 1)  # Left to right
            points.append({
                'lat': round(lat, 4),
                'lon': round(lon, 4),
                'position': positions[idx] if idx < len(positions) else f'{i},{j}'
            })
            idx += 1

    return points


def _area_summary(grid_results):
    """Generate a summary of weather across the area."""
    if not grid_results:
        return {'message_sk': 'Údaje nedostupné', 'message_en': 'Data unavailable'}

    temps_max = [r['temperature_max'] for r in grid_results if r.get('temperature_max') is not None]
    temps_min = [r['temperature_min'] for r in grid_results if r.get('temperature_min') is not None]
    precipitation = [r['precipitation_mm'] for r in grid_results if r.get('precipitation_mm') is not None]
    outdoor_count = sum(1 for r in grid_results if r.get('is_outdoor_friendly'))

    avg_temp_max = sum(temps_max) / len(temps_max) if temps_max else 0
    avg_temp_min = sum(temps_min) / len(temps_min) if temps_min else 0
    max_precip = max(precipitation) if precipitation else 0
    total_points = len(grid_results)

    # Find best/worst areas
    best_area = min(grid_results, key=lambda x: x.get('precipitation_mm', 999))
    worst_area = max(grid_results, key=lambda x: x.get('precipitation_mm', 0))

    return {
        'avg_temp_max': round(avg_temp_max, 1),
        'avg_temp_min': round(avg_temp_min, 1),
        'max_precipitation_mm': round(max_precip, 1),
        'outdoor_friendly_ratio': f'{outdoor_count}/{total_points}',
        'best_weather_area': best_area.get('grid_position', ''),
        'worst_weather_area': worst_area.get('grid_position', ''),
        'best_weather_icon': best_area.get('weather_icon', ''),
        'worst_weather_icon': worst_area.get('weather_icon', ''),
    }


def _parse_date(date_str):
    """Parse date string or return today."""
    if date_str:
        try:
            parsed = datetime.strptime(date_str, '%Y-%m-%d')
            # Limit to 16 days from now
            max_date = datetime.now() + timedelta(days=16)
            if parsed > max_date:
                return max_date
            if parsed < datetime.now():
                return datetime.now()
            return parsed
        except ValueError:
            pass
    return datetime.now()


def _is_outdoor_friendly(weather_code, daily_data):
    """Determine if weather is suitable for outdoor activities."""
    # Good outdoor weather: clear, partly cloudy, light clouds
    good_codes = [0, 1, 2, 3]
    if weather_code in good_codes:
        # Also check precipitation
        precip = daily_data.get('precipitation_sum', [0])[0] or 0
        wind = daily_data.get('windspeed_10m_max', [0])[0] or 0
        return precip < 2 and wind < 40
    return False


def _outdoor_recommendation(weather_code, lang='en'):
    """Generate outdoor activity recommendation based on weather."""
    if weather_code in [0, 1]:
        return 'Ideálne na outdoor aktivity' if lang == 'sk' else 'Ideal for outdoor activities'
    elif weather_code in [2, 3]:
        return 'Vhodné na outdoor, oblačno' if lang == 'sk' else 'Good for outdoor, cloudy'
    elif weather_code in [45, 48]:
        return 'Hmla – obmedená viditeľnosť' if lang == 'sk' else 'Fog – limited visibility'
    elif weather_code in [51, 53, 61, 80]:
        return 'Dážď – odporúčame indoor aktivity' if lang == 'sk' else 'Rain – indoor activities recommended'
    elif weather_code in [55, 63, 65, 81, 82]:
        return 'Silný dážď – len indoor' if lang == 'sk' else 'Heavy rain – indoor only'
    elif weather_code in [71, 73, 75, 77, 85, 86]:
        return 'Sneženie – zimné aktivity' if lang == 'sk' else 'Snow – winter activities'
    elif weather_code in [95, 96, 99]:
        return '⚠️ Búrka – zostaňte vnútri' if lang == 'sk' else '⚠️ Storm – stay indoors'
    return 'Skontrolujte počasie' if lang == 'sk' else 'Check weather conditions'