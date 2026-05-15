"""
Region Theme Service
====================
Determines dynamic color theme based on the type of region/area.
Colors adapt to the travel destination type.
"""

import requests
import math

USER_AGENT = "FodorTravelTIPs/1.0"

# Theme definitions with color palettes
THEMES = {
    'mountain': {
        'name': 'Mountain',
        'primary': '#2d5a27',       # Deep forest green
        'secondary': '#5d8a54',     # Lighter green
        'accent': '#8fbc8f',        # Dark sea green
        'background': '#f0f7f0',    # Very light green
        'text': '#1a3a15',          # Dark green text
        'card': '#ffffff',
        'gradient_start': '#2d5a27',
        'gradient_end': '#5d8a54',
    },
    'coastal': {
        'name': 'Coastal',
        'primary': '#006994',       # Deep ocean blue
        'secondary': '#40a8c4',     # Turquoise
        'accent': '#d4a574',        # Sandy
        'background': '#f0f8ff',    # Alice blue
        'text': '#003d5c',          # Dark blue text
        'card': '#ffffff',
        'gradient_start': '#006994',
        'gradient_end': '#40a8c4',
    },
    'urban': {
        'name': 'Urban',
        'primary': '#1a237e',       # Dark indigo
        'secondary': '#3949ab',     # Indigo
        'accent': '#c9a227',        # Gold
        'background': '#f5f5f8',    # Light grey-blue
        'text': '#1a1a2e',          # Near black
        'card': '#ffffff',
        'gradient_start': '#1a237e',
        'gradient_end': '#3949ab',
    },
    'rural': {
        'name': 'Rural',
        'primary': '#5d4037',       # Brown
        'secondary': '#8d6e63',     # Light brown
        'accent': '#7cb342',        # Grass green
        'background': '#faf8f5',    # Warm white
        'text': '#3e2723',          # Dark brown text
        'card': '#ffffff',
        'gradient_start': '#5d4037',
        'gradient_end': '#7cb342',
    },
    'default': {
        'name': 'Travel',
        'primary': '#1b5e83',       # Steel blue
        'secondary': '#2e86ab',     # Sky blue
        'accent': '#f6a623',        # Amber/gold
        'background': '#f8fafe',    # Very light blue
        'text': '#1a2a3a',          # Dark navy text
        'card': '#ffffff',
        'gradient_start': '#1b5e83',
        'gradient_end': '#2e86ab',
    }
}


def get_theme_for_location(lat, lon, region_type=None):
    """
    Determine the appropriate color theme for a location.
    Uses elevation data and geographic features to decide.
    """
    if region_type and region_type in THEMES:
        return THEMES[region_type]

    # Try to detect region type from elevation and geography
    detected_type = _detect_region_type_advanced(lat, lon)
    return THEMES.get(detected_type, THEMES['default'])


def get_all_themes():
    """Return all available themes (for testing/preview)."""
    return THEMES


def _detect_region_type_advanced(lat, lon):
    """
    Advanced region type detection using Open-Meteo elevation API.
    """
    try:
        # Use Open-Meteo to get elevation
        url = f"https://api.open-meteo.com/v1/elevation?latitude={lat}&longitude={lon}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            elevation = data.get('elevation', [0])[0]

            # Mountain: elevation > 800m
            if elevation > 800:
                return 'mountain'

            # Coastal: elevation < 20m and near known coastal areas
            if elevation < 20:
                if _is_near_coast(lat, lon):
                    return 'coastal'

            # Default based on elevation
            if elevation > 400:
                return 'rural'  # Higher rural areas

    except Exception:
        pass

    return 'default'


def _is_near_coast(lat, lon):
    """
    Simple check if coordinates are likely near a coast.
    Uses Overpass API to check for coastline nearby.
    """
    try:
        # Check for coastline within 10km
        query = f"""
        [out:json][timeout:5];
        way["natural"="coastline"](around:10000,{lat},{lon});
        out count;
        """
        response = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={'data': query},
            timeout=8
        )
        if response.status_code == 200:
            data = response.json()
            count = data.get('elements', [])
            # If there's a remark about count
            if len(count) > 0:
                return True
    except Exception:
        pass

    # Fallback: known coastal latitude/longitude ranges (very rough)
    # Mediterranean, Atlantic coast, etc.
    coastal_indicators = [
        (35, 45, -10, 35),   # Mediterranean
        (50, 60, -5, 10),    # North Sea/Atlantic
        (54, 66, 10, 30),    # Baltic
    ]

    for lat_min, lat_max, lon_min, lon_max in coastal_indicators:
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            # Could be coastal, but not certain
            return False  # Be conservative

    return False