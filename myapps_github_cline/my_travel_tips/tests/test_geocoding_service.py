"""
Unit Tests - Geocoding Service
===============================
Tests geocoding, reverse geocoding, and travel radius calculation.
Uses mocked HTTP responses for fast, reliable tests.
"""

import pytest
from unittest.mock import patch, MagicMock
from services.geocoding_service import (
    geocode_place,
    reverse_geocode,
    calculate_travel_radius,
    _extract_region,
    _detect_region_type,
)


class TestGeocodePlace:
    """Tests for geocode_place function."""

    @patch('services.geocoding_service.requests.get')
    def test_geocode_returns_results(self, mock_get, sample_nominatim_response):
        """Should return list of geocoded results."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_nominatim_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = geocode_place('Bratislava', 'sk')

        assert 'results' in result
        assert len(result['results']) == 1
        assert result['results'][0]['name'] == 'Bratislava, Slovakia'
        assert result['results'][0]['lat'] == 48.1486
        assert result['results'][0]['lon'] == 17.1077
        assert result['results'][0]['country_code'] == 'sk'
        assert result['results'][0]['region'] == 'Bratislavský kraj'

    @patch('services.geocoding_service.requests.get')
    def test_geocode_empty_query(self, mock_get):
        """Should handle empty results gracefully."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = geocode_place('nonexistentplace12345', 'en')

        assert 'results' in result
        assert len(result['results']) == 0

    @patch('services.geocoding_service.requests.get')
    def test_geocode_handles_network_error(self, mock_get):
        """Should return error dict on network failure."""
        import requests
        mock_get.side_effect = requests.RequestException("Connection failed")

        result = geocode_place('Bratislava', 'en')

        assert 'error' in result
        assert 'Geocoding failed' in result['error']
        assert result['results'] == []

    @patch('services.geocoding_service.requests.get')
    def test_geocode_sends_correct_params(self, mock_get):
        """Should send correct parameters to Nominatim."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        geocode_place('Vienna', 'en')

        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args
        params = call_kwargs[1]['params'] if 'params' in call_kwargs[1] else call_kwargs.kwargs['params']
        assert params['q'] == 'Vienna'
        assert params['format'] == 'jsonv2'
        assert params['accept-language'] == 'en'
        assert params['limit'] == 5

    @patch('services.geocoding_service.requests.get')
    def test_geocode_multiple_results(self, mock_get):
        """Should return multiple matching places."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'display_name': 'Paris, France', 'lat': '48.8566', 'lon': '2.3522',
             'type': 'city', 'category': 'place', 'importance': 0.9,
             'address': {'city': 'Paris', 'country': 'France', 'country_code': 'fr', 'state': 'Île-de-France'}},
            {'display_name': 'Paris, Texas, USA', 'lat': '33.6609', 'lon': '-95.5555',
             'type': 'city', 'category': 'place', 'importance': 0.4,
             'address': {'city': 'Paris', 'country': 'United States', 'country_code': 'us', 'state': 'Texas'}},
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = geocode_place('Paris', 'en')

        assert len(result['results']) == 2
        assert result['results'][0]['country'] == 'France'
        assert result['results'][1]['country'] == 'United States'


class TestReverseGeocode:
    """Tests for reverse_geocode function."""

    @patch('services.geocoding_service.requests.get')
    def test_reverse_geocode_success(self, mock_get):
        """Should return place name from coordinates."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'display_name': 'Bratislava, Slovakia',
            'address': {
                'city': 'Bratislava',
                'country': 'Slovakia',
                'country_code': 'sk',
                'state': 'Bratislavský kraj',
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = reverse_geocode(48.15, 17.11, 'sk')

        assert result['name'] == 'Bratislava, Slovakia'
        assert result['city'] == 'Bratislava'
        assert result['country'] == 'Slovakia'
        assert result['country_code'] == 'sk'
        assert result['lat'] == 48.15
        assert result['lon'] == 17.11

    @patch('services.geocoding_service.requests.get')
    def test_reverse_geocode_network_error(self, mock_get):
        """Should return error on network failure."""
        import requests
        mock_get.side_effect = requests.RequestException("Timeout")

        result = reverse_geocode(48.15, 17.11, 'en')

        assert 'error' in result
        assert 'Reverse geocoding failed' in result['error']

    @patch('services.geocoding_service.requests.get')
    def test_reverse_geocode_village(self, mock_get):
        """Should detect village region type."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'display_name': 'Limbach, Slovakia',
            'address': {
                'village': 'Limbach',
                'country': 'Slovakia',
                'country_code': 'sk',
                'state': 'Bratislavský kraj',
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = reverse_geocode(48.28, 17.22, 'sk')

        assert result['region_type'] == 'rural'


class TestCalculateTravelRadius:
    """Tests for calculate_travel_radius function."""

    @patch('services.geocoding_service._validate_with_osrm')
    def test_car_60min(self, mock_osrm):
        """Car 60min should give radius ~42km (60*0.7)."""
        mock_osrm.return_value = None  # Skip OSRM validation

        result = calculate_travel_radius(48.15, 17.11, 60, 'car')

        assert result['mode'] == 'car'
        assert result['time_minutes'] == 60
        assert result['speed_kmh'] == 60
        assert result['radius_km'] == 42.0  # 60km/h * 60min/60 * 0.7

    @patch('services.geocoding_service._validate_with_osrm')
    def test_bike_60min(self, mock_osrm):
        """Bike 60min should give radius ~10.5km."""
        mock_osrm.return_value = None

        result = calculate_travel_radius(48.15, 17.11, 60, 'bike')

        assert result['mode'] == 'bike'
        assert result['speed_kmh'] == 15
        assert result['radius_km'] == 10.5  # 15km/h * 1h * 0.7

    @patch('services.geocoding_service._validate_with_osrm')
    def test_walk_60min(self, mock_osrm):
        """Walk 60min should give radius ~3.5km."""
        mock_osrm.return_value = None

        result = calculate_travel_radius(48.15, 17.11, 60, 'walk')

        assert result['mode'] == 'walk'
        assert result['speed_kmh'] == 5
        assert result['radius_km'] == 3.5  # 5km/h * 1h * 0.7

    @patch('services.geocoding_service._validate_with_osrm')
    def test_radius_cap_maximum(self, mock_osrm):
        """Radius should be capped at 200km."""
        mock_osrm.return_value = None

        result = calculate_travel_radius(48.15, 17.11, 600, 'car')  # 10 hours

        assert result['radius_km'] == 200.0

    @patch('services.geocoding_service._validate_with_osrm')
    def test_radius_cap_minimum(self, mock_osrm):
        """Radius should be at least 1km."""
        mock_osrm.return_value = None

        result = calculate_travel_radius(48.15, 17.11, 1, 'walk')  # 1 min walk

        assert result['radius_km'] == 1.0

    @patch('services.geocoding_service._validate_with_osrm')
    def test_unknown_mode_defaults_to_car(self, mock_osrm):
        """Unknown transport mode should use car speed (60km/h)."""
        mock_osrm.return_value = None

        result = calculate_travel_radius(48.15, 17.11, 60, 'helicopter')

        assert result['speed_kmh'] == 60  # defaults to car


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_extract_region_state(self):
        """Should extract state from address."""
        address = {'state': 'Bratislavský kraj', 'country': 'Slovakia'}
        assert _extract_region(address) == 'Bratislavský kraj'

    def test_extract_region_county(self):
        """Should fallback to county if no state."""
        address = {'county': 'Some County', 'country': 'Ireland'}
        assert _extract_region(address) == 'Some County'

    def test_extract_region_empty(self):
        """Should return empty string if no region info."""
        address = {'country': 'Slovakia'}
        assert _extract_region(address) == ''

    def test_detect_region_type_urban(self):
        """City without village should be urban."""
        address = {'city': 'Bratislava', 'country': 'Slovakia'}
        assert _detect_region_type(address, 48.15, 17.11) == 'urban'

    def test_detect_region_type_rural(self):
        """Village without city should be rural."""
        address = {'village': 'Limbach', 'country': 'Slovakia'}
        assert _detect_region_type(address, 48.28, 17.22) == 'rural'

    def test_detect_region_type_town(self):
        """Town should be urban."""
        address = {'town': 'Modra', 'country': 'Slovakia'}
        assert _detect_region_type(address, 48.33, 17.30) == 'urban'

    def test_detect_region_type_default(self):
        """No city/village/town should return default."""
        address = {'country': 'Slovakia'}
        assert _detect_region_type(address, 48.15, 17.11) == 'default'