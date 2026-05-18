"""
Pytest configuration and shared fixtures for My Travel Tips tests.
"""

import sys
import os
import pytest

# Add backend directory to path
BACKEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, BACKEND_DIR)

from app import app as flask_app  # noqa: E402


@pytest.fixture
def app():
    """Create application for testing."""
    flask_app.config['TESTING'] = True
    return flask_app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_poi():
    """Sample POI data for testing."""
    return {
        'name': 'Bratislava Castle',
        'name_en': 'Bratislava Castle',
        'name_sk': 'Bratislavský hrad',
        'lat': 48.1422,
        'lon': 17.1000,
        'distance_km': 2.5,
        'type': 'historic',
        'category': 'mainstream',
        'score': 75,
        'wikipedia': 'en:Bratislava Castle',
        'wikidata': 'Q168713',
        'website': 'https://www.bratislava-hrad.sk',
        'official_website': 'https://www.bratislava-hrad.sk',
        'wiki_url': 'https://en.wikipedia.org/wiki/Bratislava_Castle',
        'description': 'A castle in Bratislava',
        'opening_hours': 'Mo-Su 09:00-17:00',
        'tags': {
            'tourism': '',
            'historic': 'castle',
            'natural': '',
            'leisure': '',
            'amenity': '',
            'man_made': '',
            'geological': '',
            'waterway': '',
            'route': '',
            'boundary': '',
        },
        'is_outdoor': False
    }


@pytest.fixture
def sample_weather_response():
    """Sample Open-Meteo API response."""
    return {
        'daily': {
            'time': ['2026-05-16'],
            'temperature_2m_max': [22.5],
            'temperature_2m_min': [12.3],
            'precipitation_sum': [0.0],
            'weathercode': [1],
            'windspeed_10m_max': [15.0],
            'uv_index_max': [6.0],
        }
    }


@pytest.fixture
def sample_nominatim_response():
    """Sample Nominatim geocoding response."""
    return [
        {
            'display_name': 'Bratislava, Slovakia',
            'lat': '48.1486',
            'lon': '17.1077',
            'type': 'city',
            'category': 'place',
            'importance': 0.78,
            'address': {
                'city': 'Bratislava',
                'country': 'Slovakia',
                'country_code': 'sk',
                'state': 'Bratislavský kraj',
            }
        }
    ]


@pytest.fixture
def sample_overpass_response():
    """Sample Overpass API response with POI elements."""
    return {
        'elements': [
            {
                'type': 'node',
                'id': 123456,
                'lat': 48.1422,
                'lon': 17.1000,
                'tags': {
                    'name': 'Bratislava Castle',
                    'name:en': 'Bratislava Castle',
                    'name:sk': 'Bratislavský hrad',
                    'historic': 'castle',
                    'wikipedia': 'en:Bratislava Castle',
                    'wikidata': 'Q168713',
                    'website': 'https://www.bratislava-hrad.sk',
                    'opening_hours': 'Mo-Su 09:00-17:00',
                }
            },
            {
                'type': 'node',
                'id': 789012,
                'lat': 48.1500,
                'lon': 17.1200,
                'tags': {
                    'name': 'Devín Castle',
                    'name:en': 'Devín Castle',
                    'historic': 'castle',
                    'wikipedia': 'en:Devín Castle',
                    'wikidata': 'Q1167838',
                }
            },
            {
                'type': 'way',
                'id': 345678,
                'center': {'lat': 48.1600, 'lon': 17.0800},
                'tags': {
                    'name': 'SNM - Historical Museum',
                    'tourism': 'museum',
                    'website': 'https://www.snm.sk',
                }
            },
        ]
    }