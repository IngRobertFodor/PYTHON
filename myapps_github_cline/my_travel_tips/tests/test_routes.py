"""
Unit Tests - Flask Routes (API Endpoints)
==========================================
Tests all API endpoints with mocked services.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestHealthEndpoint:
    """Tests for /api/health endpoint."""

    def test_health_returns_200(self, client):
        response = client.get('/api/health')
        assert response.status_code == 200

    def test_health_returns_correct_json(self, client):
        response = client.get('/api/health')
        data = response.get_json()
        assert data['status'] == 'ok'
        assert data['app'] == 'My Travel Tips'


class TestGeocodingRoutes:
    """Tests for /api/geocoding/* endpoints."""

    def test_search_missing_query_returns_400(self, client):
        response = client.get('/api/geocoding/search?q=')
        assert response.status_code == 400

    def test_search_no_query_param_returns_400(self, client):
        response = client.get('/api/geocoding/search')
        assert response.status_code == 400

    @patch('routes.geocoding.geocode_place')
    def test_search_valid_query(self, mock_geocode, client):
        mock_geocode.return_value = {'results': [{'name': 'Test', 'lat': 48.0, 'lon': 17.0}]}
        response = client.get('/api/geocoding/search?q=Bratislava&lang=sk')
        assert response.status_code == 200
        data = response.get_json()
        assert 'results' in data

    def test_reverse_missing_lat_lon_returns_400(self, client):
        response = client.get('/api/geocoding/reverse')
        assert response.status_code == 400

    def test_reverse_missing_lon_returns_400(self, client):
        response = client.get('/api/geocoding/reverse?lat=48.15')
        assert response.status_code == 400

    @patch('routes.geocoding.reverse_geocode')
    def test_reverse_valid_coords(self, mock_reverse, client):
        mock_reverse.return_value = {'name': 'Bratislava', 'city': 'Bratislava'}
        response = client.get('/api/geocoding/reverse?lat=48.15&lon=17.11&lang=sk')
        assert response.status_code == 200
        data = response.get_json()
        assert 'name' in data

    def test_travel_radius_missing_params_returns_400(self, client):
        response = client.get('/api/geocoding/travel-radius')
        assert response.status_code == 400

    def test_travel_radius_missing_time_returns_400(self, client):
        response = client.get('/api/geocoding/travel-radius?lat=48.15&lon=17.11')
        assert response.status_code == 400

    @patch('routes.geocoding.calculate_travel_radius')
    def test_travel_radius_valid(self, mock_radius, client):
        mock_radius.return_value = {'radius_km': 42.0, 'mode': 'car', 'time_minutes': 60, 'speed_kmh': 60}
        response = client.get('/api/geocoding/travel-radius?lat=48.15&lon=17.11&time_minutes=60&mode=car')
        assert response.status_code == 200
        data = response.get_json()
        assert data['radius_km'] == 42.0


class TestWeatherRoutes:
    """Tests for /api/weather/* endpoints."""

    def test_point_missing_coords_returns_400(self, client):
        response = client.get('/api/weather/point')
        assert response.status_code == 400

    def test_point_missing_lon_returns_400(self, client):
        response = client.get('/api/weather/point?lat=48.15')
        assert response.status_code == 400

    @patch('routes.weather.get_weather_for_point')
    def test_point_valid_request(self, mock_weather, client):
        mock_weather.return_value = {
            'temperature_max': 22.5,
            'temperature_min': 12.0,
            'weather_icon': '☀️',
        }
        response = client.get('/api/weather/point?lat=48.15&lon=17.11')
        assert response.status_code == 200
        data = response.get_json()
        assert data['temperature_max'] == 22.5

    def test_grid_missing_coords_returns_400(self, client):
        response = client.get('/api/weather/grid')
        assert response.status_code == 400

    @patch('routes.weather.get_weather_grid')
    def test_grid_valid_request(self, mock_grid, client):
        mock_grid.return_value = {
            'grid_points': [{'lat': 48.15, 'lon': 17.11}],
            'summary': {'avg_temp_max': 20}
        }
        response = client.get('/api/weather/grid?lat=48.15&lon=17.11&radius_km=25')
        assert response.status_code == 200
        data = response.get_json()
        assert 'grid_points' in data
        assert 'summary' in data


class TestPOIRoutes:
    """Tests for /api/poi/* endpoints."""

    def test_search_missing_coords_returns_400(self, client):
        response = client.get('/api/poi/search')
        assert response.status_code == 400

    def test_search_missing_lon_returns_400(self, client):
        response = client.get('/api/poi/search?lat=48.15')
        assert response.status_code == 400

    def test_search_radius_too_large_returns_400(self, client):
        response = client.get('/api/poi/search?lat=48.15&lon=17.11&radius_km=500')
        assert response.status_code == 400

    def test_search_radius_zero_returns_400(self, client):
        response = client.get('/api/poi/search?lat=48.15&lon=17.11&radius_km=0')
        assert response.status_code == 400

    def test_search_negative_radius_returns_400(self, client):
        response = client.get('/api/poi/search?lat=48.15&lon=17.11&radius_km=-5')
        assert response.status_code == 400

    @patch('routes.poi.get_pois')
    @patch('routes.poi.enrich_poi_with_wikipedia')
    @patch('routes.poi.generate_links')
    def test_search_valid_request(self, mock_links, mock_wiki, mock_pois, client):
        mock_pois.return_value = {
            'mainstream': [{'name': 'Castle', 'lat': 48.14, 'lon': 17.10}],
            'alternative': []
        }
        mock_wiki.side_effect = lambda poi, lang: poi
        mock_links.return_value = [{'type': 'google_maps', 'url': 'http://test', 'icon': '🗺️', 'label': 'Maps'}]

        response = client.get('/api/poi/search?lat=48.15&lon=17.11&radius_km=25&lang=en')
        assert response.status_code == 200
        data = response.get_json()
        assert 'mainstream' in data
        assert 'alternative' in data
        assert 'center' in data
        assert data['center']['lat'] == 48.15

    @patch('routes.poi.get_pois')
    @patch('routes.poi.enrich_poi_with_wikipedia')
    @patch('routes.poi.generate_links')
    def test_search_with_tags_filter(self, mock_links, mock_wiki, mock_pois, client):
        mock_pois.return_value = {'mainstream': [], 'alternative': []}
        mock_wiki.side_effect = lambda poi, lang: poi
        mock_links.return_value = []

        response = client.get('/api/poi/search?lat=48.15&lon=17.11&radius_km=25&tags=historic%3Dcastle')
        assert response.status_code == 200

    @patch('routes.poi.get_pois')
    @patch('routes.poi.enrich_poi_with_wikipedia')
    @patch('routes.poi.generate_links')
    def test_search_default_radius(self, mock_links, mock_wiki, mock_pois, client):
        """Without radius_km param, should use default 25."""
        mock_pois.return_value = {'mainstream': [], 'alternative': []}
        mock_wiki.side_effect = lambda poi, lang: poi
        mock_links.return_value = []

        response = client.get('/api/poi/search?lat=48.15&lon=17.11')
        assert response.status_code == 200
        data = response.get_json()
        assert data['radius_km'] == 25


class TestPOICache:
    """Tests for the in-memory POI cache integration."""

    def test_cache_clear_endpoint(self, client):
        """POST /api/poi/cache/clear should return 200 with cleared status."""
        response = client.post('/api/poi/cache/clear')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'cleared'
        assert 'entries_removed' in data

    def test_cache_stats_endpoint(self, client):
        """GET /api/poi/cache/stats should return size and valid count."""
        response = client.get('/api/poi/cache/stats')
        assert response.status_code == 200
        data = response.get_json()
        assert 'size' in data
        assert 'valid' in data

    @patch('routes.poi.get_pois')
    @patch('routes.poi.enrich_poi_with_wikipedia')
    @patch('routes.poi.generate_links')
    def test_second_request_returns_from_cache(self, mock_links, mock_wiki, mock_pois, client):
        """Second identical request should be served from cache (get_pois not called twice)."""
        from services.cache_service import poi_cache
        poi_cache.clear()  # ensure clean state

        sample_poi = {
            'name': 'Acropolis', 'display_name': 'Acropolis of Athens',
            'name_en': 'Acropolis of Athens', 'name_sk': '', 'lat': 37.97,
            'lon': 23.73, 'distance_km': 0.5, 'type': 'historic',
            'score': 80, 'category': 'mainstream', 'wikipedia': '',
            'wikidata': '', 'website': '', 'description': '', 'opening_hours': '',
            'tags': {}, 'is_outdoor': False, 'links': []
        }
        mock_pois.return_value = {'mainstream': [sample_poi], 'alternative': []}
        mock_wiki.side_effect = lambda poi, lang: poi
        mock_links.return_value = []

        url = '/api/poi/search?lat=37.97&lon=23.73&radius_km=25&lang=sk&tags=historic%3Dcastle'

        # First request – should call get_pois
        r1 = client.get(url)
        assert r1.status_code == 200
        assert mock_pois.call_count == 1

        # Second identical request – should return from cache, NOT call get_pois again
        r2 = client.get(url)
        assert r2.status_code == 200
        assert mock_pois.call_count == 1  # still 1, not 2!

        data2 = r2.get_json()
        assert data2['_meta']['from_cache'] is True

        poi_cache.clear()  # cleanup



class TestStaticFiles:
    """Tests for static file serving."""

    def test_root_serves_html(self, client):
        response = client.get('/')
        # May return 200 or 404 depending on if frontend exists
        # Just verify it doesn't crash
        assert response.status_code in [200, 404]