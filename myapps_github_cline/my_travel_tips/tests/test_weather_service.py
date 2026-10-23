"""
Unit Tests - Weather Service
=============================
Tests weather forecasting, grid generation, and helper functions.
Uses mocked HTTP responses.
NOTE: weather_service uses minified aliases: WC (codes), _grid, _summary, _isof, _rec
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from services.weather_service import (
    get_weather_for_point,
    get_weather_grid,
    _grid as _generate_grid,
    _summary as _area_summary,
    _parse_date,
    _isof as _is_outdoor_friendly,
    _rec as _outdoor_recommendation,
    WC as WEATHER_CODES,
)


class TestGetWeatherForPoint:
    """Tests for get_weather_for_point function."""

    @patch('services.weather_service.requests.get')
    def test_returns_weather_data(self, mock_get, sample_weather_response):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_weather_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        today = datetime.now().strftime('%Y-%m-%d')
        result = get_weather_for_point(48.15, 17.11, today)
        assert result['temperature_max'] == 22.5
        assert result['temperature_min'] == 12.3
        assert result['precipitation_mm'] == 0.0
        assert result['wind_speed_max'] == 15.0
        assert result['uv_index'] == 6.0
        assert result['weather_code'] == 1
        assert result['lat'] == 48.15
        assert result['lon'] == 17.11

    @patch('services.weather_service.requests.get')
    def test_returns_weather_descriptions(self, mock_get, sample_weather_response):
        """WC code 1 -> e='Clear', i='sunny'"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_weather_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        result = get_weather_for_point(48.15, 17.11, datetime.now().strftime('%Y-%m-%d'))
        assert 'weather_description_sk' in result
        assert 'weather_description_en' in result
        assert 'weather_icon' in result
        assert result['weather_description_en'] == 'Clear'
        assert result['weather_icon'] == 'sunny'

    @patch('services.weather_service.requests.get')
    def test_outdoor_friendly_clear_weather(self, mock_get, sample_weather_response):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_weather_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        result = get_weather_for_point(48.15, 17.11, datetime.now().strftime('%Y-%m-%d'))
        assert result['is_outdoor_friendly'] is True

    @patch('services.weather_service.requests.get')
    def test_not_outdoor_friendly_rain(self, mock_get):
        rain_response = {'daily': {'time': ['2026-05-16'],
            'temperature_2m_max': [18.0], 'temperature_2m_min': [10.0],
            'precipitation_sum': [15.0], 'weathercode': [63],
            'windspeed_10m_max': [25.0], 'uv_index_max': [2.0]}}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = rain_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        result = get_weather_for_point(48.15, 17.11, datetime.now().strftime('%Y-%m-%d'))
        assert result['is_outdoor_friendly'] is False
        assert result['weather_code'] == 63

    @patch('services.weather_service.requests.get')
    def test_handles_network_error(self, mock_get):
        import requests as req_lib
        mock_get.side_effect = req_lib.RequestException("Connection failed")
        result = get_weather_for_point(48.15, 17.11)
        assert 'error' in result

    @patch('services.weather_service.requests.get')
    def test_handles_no_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'daily': {}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        result = get_weather_for_point(48.15, 17.11)
        assert 'error' in result


class TestGenerateGrid:
    """Tests for _generate_grid (aliased to _grid) function."""

    def test_generates_9_points_for_3x3(self):
        points = _generate_grid(48.15, 17.11, 25)
        assert len(points) == 9

    def test_grid_has_correct_positions(self):
        points = _generate_grid(48.15, 17.11, 25)
        for p in points:
            assert len(p) == 2
            assert isinstance(p[0], float)
            assert isinstance(p[1], float)

    def test_center_point_is_at_center(self):
        center_lat, center_lon = 48.15, 17.11
        points = _generate_grid(center_lat, center_lon, 25)
        center_point = points[4]
        assert abs(center_point[0] - center_lat) < 0.01
        assert abs(center_point[1] - center_lon) < 0.01

    def test_grid_spread_increases_with_radius(self):
        small_grid = _generate_grid(48.15, 17.11, 10)
        large_grid = _generate_grid(48.15, 17.11, 50)
        small_spread = abs(small_grid[0][0] - small_grid[8][0])
        large_spread = abs(large_grid[0][0] - large_grid[8][0])
        assert large_spread > small_spread


class TestAreaSummary:
    """Tests for _area_summary (aliased to _summary) function."""

    def test_empty_results(self):
        result = _area_summary([])
        assert 'message' in result

    def test_calculates_averages(self):
        grid_results = [
            {'temperature_max': 20.0, 'precipitation_mm': 0.0, 'is_outdoor_friendly': True},
            {'temperature_max': 22.0, 'precipitation_mm': 1.0, 'is_outdoor_friendly': True},
            {'temperature_max': 18.0, 'precipitation_mm': 0.5, 'is_outdoor_friendly': False},
        ]
        result = _area_summary(grid_results)
        assert 'avg_temp_max' in result
        assert result['avg_temp_max'] == 20.0

    def test_outdoor_friendly_ratio_present(self):
        grid_results = [
            {'temperature_max': 15.0, 'precipitation_mm': 5.0, 'is_outdoor_friendly': False},
            {'temperature_max': 20.0, 'precipitation_mm': 0.0, 'is_outdoor_friendly': True},
        ]
        result = _area_summary(grid_results)
        assert 'outdoor_friendly_ratio' in result


class TestParseDate:
    """Tests for _parse_date function."""

    def test_valid_date_format(self):
        """Valid future YYYY-MM-DD (within 16 days) should parse correctly."""
        from datetime import datetime, timedelta
        future_date = datetime.now() + timedelta(days=5)
        date_str = future_date.strftime('%Y-%m-%d')
        result = _parse_date(date_str)
        assert result.month == future_date.month
        assert result.day == future_date.day
        assert result.year == future_date.year

    def test_empty_string_returns_today(self):
        result = _parse_date('')
        assert result.date() == datetime.now().date()

    def test_none_returns_today(self):
        result = _parse_date(None)
        assert result.date() == datetime.now().date()

    def test_future_date_capped_at_16_days(self):
        far_future = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        result = _parse_date(far_future)
        max_allowed = datetime.now() + timedelta(days=16)
        assert result.date() <= max_allowed.date()

    def test_past_date_returns_today(self):
        result = _parse_date('2020-01-01')
        assert result.date() == datetime.now().date()

    def test_invalid_date_returns_today(self):
        result = _parse_date('not-a-date')
        assert result.date() == datetime.now().date()


class TestIsOutdoorFriendly:
    """Tests for _is_outdoor_friendly (_isof) function."""

    def test_clear_sky_low_wind(self):
        daily = {'precipitation_sum': [0.5], 'windspeed_10m_max': [10]}
        assert _is_outdoor_friendly(0, daily) is True

    def test_clear_but_high_wind(self):
        daily = {'precipitation_sum': [0], 'windspeed_10m_max': [50]}
        assert _is_outdoor_friendly(0, daily) is False

    def test_clear_but_high_precipitation(self):
        daily = {'precipitation_sum': [5], 'windspeed_10m_max': [10]}
        assert _is_outdoor_friendly(1, daily) is False

    def test_rain_code(self):
        daily = {'precipitation_sum': [10], 'windspeed_10m_max': [20]}
        assert _is_outdoor_friendly(63, daily) is False

    def test_thunderstorm(self):
        daily = {'precipitation_sum': [20], 'windspeed_10m_max': [60]}
        assert _is_outdoor_friendly(95, daily) is False


class TestOutdoorRecommendation:
    """Tests for _outdoor_recommendation (_rec) function."""

    def test_clear_sky_english(self):
        result = _outdoor_recommendation(0, 'en')
        assert 'Ideal for outdoor' in result

    def test_clear_sky_slovak(self):
        """Minified code uses 'Idealne' (without diacritics)."""
        result = _outdoor_recommendation(0, 'sk')
        assert 'Idealne na outdoor' in result

    def test_rain_english(self):
        result = _outdoor_recommendation(63, 'en')
        assert 'rain' in result.lower() or 'indoor' in result.lower()

    def test_storm_english(self):
        result = _outdoor_recommendation(95, 'en')
        assert 'Storm' in result or 'indoors' in result.lower()

    def test_snow_english(self):
        result = _outdoor_recommendation(73, 'en')
        assert 'Snow' in result or 'winter' in result.lower()

    def test_fog_english(self):
        result = _outdoor_recommendation(45, 'en')
        assert 'Fog' in result or 'visibility' in result.lower()


class TestWeatherCodes:
    """Tests for WC (WEATHER_CODES) dict – uses minified keys s/e/i."""

    def test_all_codes_have_s_e_i_keys(self):
        for code, data in WEATHER_CODES.items():
            assert 's' in data, f"Code {code} missing 's'"
            assert 'e' in data, f"Code {code} missing 'e'"
            assert 'i' in data, f"Code {code} missing 'i'"

    def test_code_0_is_clear(self):
        assert WEATHER_CODES[0]['e'] == 'Clear'
        assert WEATHER_CODES[0]['i'] == 'sunny'

    def test_code_95_is_storm(self):
        assert 'Burka' in WEATHER_CODES[95]['s'] or 'Storm' in WEATHER_CODES[95]['e']
