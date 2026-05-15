"""
Unit Tests - Weather Service
=============================
Tests weather forecasting, grid generation, and helper functions.
Uses mocked HTTP responses.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from services.weather_service import (
    get_weather_for_point,
    get_weather_grid,
    _generate_grid,
    _area_summary,
    _parse_date,
    _is_outdoor_friendly,
    _outdoor_recommendation,
    WEATHER_CODES,
)


class TestGetWeatherForPoint:
    """Tests for get_weather_for_point function."""

    @patch('services.weather_service.requests.get')
    def test_returns_weather_data(self, mock_get, sample_weather_response):
        """Should return complete weather data for a point."""
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
        """Should include SK and EN descriptions and icon."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_weather_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        today = datetime.now().strftime('%Y-%m-%d')
        result = get_weather_for_point(48.15, 17.11, today)

        assert result['weather_description_sk'] == 'Prevažne jasno'
        assert result['weather_description_en'] == 'Mainly clear'
        assert result['weather_icon'] == '🌤️'

    @patch('services.weather_service.requests.get')
    def test_outdoor_friendly_clear_weather(self, mock_get, sample_weather_response):
        """Clear weather with low precipitation should be outdoor friendly."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_weather_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        today = datetime.now().strftime('%Y-%m-%d')
        result = get_weather_for_point(48.15, 17.11, today)

        assert result['is_outdoor_friendly'] is True

    @patch('services.weather_service.requests.get')
    def test_not_outdoor_friendly_rain(self, mock_get):
        """Rainy weather should not be outdoor friendly."""
        rain_response = {
            'daily': {
                'time': ['2026-05-16'],
                'temperature_2m_max': [18.0],
                'temperature_2m_min': [10.0],
                'precipitation_sum': [15.0],
                'weathercode': [63],  # Moderate rain
                'windspeed_10m_max': [25.0],
                'uv_index_max': [2.0],
            }
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = rain_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        today = datetime.now().strftime('%Y-%m-%d')
        result = get_weather_for_point(48.15, 17.11, today)

        assert result['is_outdoor_friendly'] is False
        assert result['weather_code'] == 63

    @patch('services.weather_service.requests.get')
    def test_handles_network_error(self, mock_get):
        """Should return error on network failure."""
        import requests
        mock_get.side_effect = requests.RequestException("API down")

        result = get_weather_for_point(48.15, 17.11, '')

        assert 'error' in result
        assert 'Weather fetch failed' in result['error']

    @patch('services.weather_service.requests.get')
    def test_no_data_available(self, mock_get):
        """Should handle empty daily data."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'daily': {'time': []}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = get_weather_for_point(48.15, 17.11, '2026-05-16')

        assert 'error' in result


class TestGenerateGrid:
    """Tests for _generate_grid function."""

    def test_generates_9_points_for_3x3(self):
        """3x3 grid should produce 9 points."""
        points = _generate_grid(48.15, 17.11, 25, 3)
        assert len(points) == 9

    def test_grid_has_correct_positions(self):
        """Grid points should have correct position labels."""
        points = _generate_grid(48.15, 17.11, 25, 3)
        positions = [p['position'] for p in points]
        expected = ['NW', 'N', 'NE', 'W', 'C', 'E', 'SW', 'S', 'SE']
        assert positions == expected

    def test_center_point_is_at_center(self):
        """Center point (C) should be at the given coordinates."""
        points = _generate_grid(48.15, 17.11, 25, 3)
        center = next(p for p in points if p['position'] == 'C')
        assert abs(center['lat'] - 48.15) < 0.01
        assert abs(center['lon'] - 17.11) < 0.01

    def test_grid_spread_increases_with_radius(self):
        """Larger radius should produce more spread out points."""
        small_grid = _generate_grid(48.15, 17.11, 10, 3)
        large_grid = _generate_grid(48.15, 17.11, 50, 3)

        # NW point should be further north/west in large grid
        small_nw = next(p for p in small_grid if p['position'] == 'NW')
        large_nw = next(p for p in large_grid if p['position'] == 'NW')

        assert large_nw['lat'] > small_nw['lat']  # Further north


class TestAreaSummary:
    """Tests for _area_summary function."""

    def test_empty_results(self):
        """Should handle empty grid results."""
        result = _area_summary([])
        assert result['message_sk'] == 'Údaje nedostupné'
        assert result['message_en'] == 'Data unavailable'

    def test_calculates_averages(self):
        """Should calculate correct temperature averages."""
        grid_results = [
            {'temperature_max': 20, 'temperature_min': 10, 'precipitation_mm': 0,
             'is_outdoor_friendly': True, 'grid_position': 'N', 'weather_icon': '☀️'},
            {'temperature_max': 22, 'temperature_min': 12, 'precipitation_mm': 2,
             'is_outdoor_friendly': True, 'grid_position': 'S', 'weather_icon': '🌤️'},
            {'temperature_max': 18, 'temperature_min': 8, 'precipitation_mm': 5,
             'is_outdoor_friendly': False, 'grid_position': 'E', 'weather_icon': '🌧️'},
        ]

        result = _area_summary(grid_results)

        assert result['avg_temp_max'] == 20.0  # (20+22+18)/3
        assert result['avg_temp_min'] == 10.0  # (10+12+8)/3
        assert result['max_precipitation_mm'] == 5.0
        assert result['outdoor_friendly_ratio'] == '2/3'

    def test_best_worst_areas(self):
        """Should identify areas with best/worst weather."""
        grid_results = [
            {'temperature_max': 20, 'temperature_min': 10, 'precipitation_mm': 0,
             'is_outdoor_friendly': True, 'grid_position': 'NW', 'weather_icon': '☀️'},
            {'temperature_max': 15, 'temperature_min': 8, 'precipitation_mm': 10,
             'is_outdoor_friendly': False, 'grid_position': 'SE', 'weather_icon': '🌧️'},
        ]

        result = _area_summary(grid_results)

        assert result['best_weather_area'] == 'NW'  # Least precipitation
        assert result['worst_weather_area'] == 'SE'  # Most precipitation


class TestParseDate:
    """Tests for _parse_date function."""

    def test_valid_date(self):
        """Should parse valid date string."""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        result = _parse_date(tomorrow)
        assert result.strftime('%Y-%m-%d') == tomorrow

    def test_empty_string_returns_today(self):
        """Empty string should return today."""
        result = _parse_date('')
        assert result.date() == datetime.now().date()

    def test_none_returns_today(self):
        """None should return today."""
        result = _parse_date(None)
        assert result.date() == datetime.now().date()

    def test_future_date_capped(self):
        """Date more than 16 days ahead should be capped."""
        far_future = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        result = _parse_date(far_future)
        max_date = datetime.now() + timedelta(days=16)
        assert result.date() <= max_date.date()

    def test_past_date_returns_today(self):
        """Past date should return today."""
        past = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        result = _parse_date(past)
        assert result.date() == datetime.now().date()

    def test_invalid_format_returns_today(self):
        """Invalid date format should return today."""
        result = _parse_date('not-a-date')
        assert result.date() == datetime.now().date()


class TestIsOutdoorFriendly:
    """Tests for _is_outdoor_friendly function."""

    def test_clear_sky_low_wind(self):
        """Clear sky with low wind/precip should be outdoor friendly."""
        daily = {'precipitation_sum': [0.5], 'windspeed_10m_max': [10]}
        assert _is_outdoor_friendly(0, daily) is True

    def test_clear_but_high_wind(self):
        """Clear sky but high wind should NOT be outdoor friendly."""
        daily = {'precipitation_sum': [0], 'windspeed_10m_max': [50]}
        assert _is_outdoor_friendly(0, daily) is False

    def test_clear_but_high_precipitation(self):
        """Clear code but high precipitation should NOT be outdoor friendly."""
        daily = {'precipitation_sum': [5], 'windspeed_10m_max': [10]}
        assert _is_outdoor_friendly(1, daily) is False

    def test_rain_code(self):
        """Rain weather code should NOT be outdoor friendly."""
        daily = {'precipitation_sum': [10], 'windspeed_10m_max': [20]}
        assert _is_outdoor_friendly(63, daily) is False

    def test_thunderstorm(self):
        """Thunderstorm should NOT be outdoor friendly."""
        daily = {'precipitation_sum': [20], 'windspeed_10m_max': [60]}
        assert _is_outdoor_friendly(95, daily) is False


class TestOutdoorRecommendation:
    """Tests for _outdoor_recommendation function."""

    def test_clear_sky_english(self):
        """Clear sky recommendation in English."""
        result = _outdoor_recommendation(0, 'en')
        assert 'Ideal for outdoor' in result

    def test_clear_sky_slovak(self):
        """Clear sky recommendation in Slovak."""
        result = _outdoor_recommendation(0, 'sk')
        assert 'Ideálne na outdoor' in result

    def test_rain_english(self):
        """Rain recommendation in English."""
        result = _outdoor_recommendation(63, 'en')
        assert 'rain' in result.lower() or 'indoor' in result.lower()

    def test_storm_english(self):
        """Storm recommendation in English."""
        result = _outdoor_recommendation(95, 'en')
        assert 'Storm' in result or 'indoors' in result.lower()

    def test_snow_english(self):
        """Snow recommendation in English."""
        result = _outdoor_recommendation(73, 'en')
        assert 'Snow' in result or 'winter' in result.lower()

    def test_fog_english(self):
        """Fog recommendation in English."""
        result = _outdoor_recommendation(45, 'en')
        assert 'Fog' in result or 'visibility' in result.lower()


class TestWeatherCodes:
    """Tests for WEATHER_CODES dictionary."""

    def test_all_codes_have_sk_en_icon(self):
        """All weather codes should have sk, en, and icon keys."""
        for code, data in WEATHER_CODES.items():
            assert 'sk' in data, f"Code {code} missing 'sk'"
            assert 'en' in data, f"Code {code} missing 'en'"
            assert 'icon' in data, f"Code {code} missing 'icon'"

    def test_code_0_is_clear(self):
        """Code 0 should be clear sky."""
        assert WEATHER_CODES[0]['en'] == 'Clear sky'
        assert WEATHER_CODES[0]['icon'] == '☀️'

    def test_code_95_is_thunderstorm(self):
        """Code 95 should be thunderstorm."""
        assert 'Thunderstorm' in WEATHER_CODES[95]['en']
        assert 'Búrka' in WEATHER_CODES[95]['sk']