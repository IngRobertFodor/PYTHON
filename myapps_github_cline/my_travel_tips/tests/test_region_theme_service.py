"""
Unit Tests - Region Theme Service
===================================
Tests theme detection and color palette definitions.
"""

import pytest
from unittest.mock import patch, MagicMock
from services.region_theme_service import (
    get_theme_for_location,
    get_all_themes,
    _detect_region_type_advanced,
    THEMES,
)


class TestGetThemeForLocation:
    """Tests for get_theme_for_location function."""

    def test_returns_theme_for_known_type(self):
        """Should return correct theme when region_type is provided."""
        theme = get_theme_for_location(48.15, 17.11, 'mountain')
        assert theme['name'] == 'Mountain'
        assert theme['primary'] == '#2d5a27'

    def test_returns_coastal_theme(self):
        theme = get_theme_for_location(43.0, 16.0, 'coastal')
        assert theme['name'] == 'Coastal'
        assert theme['primary'] == '#006994'

    def test_returns_urban_theme(self):
        theme = get_theme_for_location(48.15, 17.11, 'urban')
        assert theme['name'] == 'Urban'

    def test_returns_rural_theme(self):
        theme = get_theme_for_location(48.28, 17.22, 'rural')
        assert theme['name'] == 'Rural'

    def test_returns_default_theme_for_unknown_type(self):
        theme = get_theme_for_location(48.15, 17.11, 'unknown_type')
        # Should fall through to detection
        assert 'primary' in theme

    @patch('services.region_theme_service._detect_region_type_advanced')
    def test_detects_type_when_not_provided(self, mock_detect):
        """Should detect region type from coordinates when not provided."""
        mock_detect.return_value = 'mountain'
        theme = get_theme_for_location(49.0, 20.0)
        assert theme['name'] == 'Mountain'


class TestGetAllThemes:
    """Tests for get_all_themes function."""

    def test_returns_all_themes(self):
        themes = get_all_themes()
        assert 'mountain' in themes
        assert 'coastal' in themes
        assert 'urban' in themes
        assert 'rural' in themes
        assert 'default' in themes

    def test_themes_have_required_colors(self):
        """Each theme should have all required color fields."""
        required_fields = ['name', 'primary', 'secondary', 'accent',
                          'background', 'text', 'card', 'gradient_start', 'gradient_end']
        themes = get_all_themes()
        for key, theme in themes.items():
            for field in required_fields:
                assert field in theme, f"Theme '{key}' missing '{field}'"

    def test_colors_are_valid_hex(self):
        """All color values should be valid hex colors."""
        import re
        hex_pattern = re.compile(r'^#[0-9a-fA-F]{6}$')
        themes = get_all_themes()
        color_fields = ['primary', 'secondary', 'accent', 'background', 'text', 'card',
                       'gradient_start', 'gradient_end']
        for key, theme in themes.items():
            for field in color_fields:
                value = theme[field]
                assert hex_pattern.match(value), f"Theme '{key}' field '{field}' invalid: {value}"


class TestDetectRegionTypeAdvanced:
    """Tests for _detect_region_type_advanced function."""

    @patch('services.region_theme_service.requests.get')
    def test_high_elevation_returns_mountain(self, mock_get):
        """Elevation > 800m should return mountain."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'elevation': [1200]}
        mock_get.return_value = mock_response

        result = _detect_region_type_advanced(49.0, 20.0)
        assert result == 'mountain'

    @patch('services.region_theme_service.requests.get')
    def test_medium_elevation_returns_rural(self, mock_get):
        """Elevation 400-800m should return rural."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'elevation': [500]}
        mock_get.return_value = mock_response

        result = _detect_region_type_advanced(48.5, 17.5)
        assert result == 'rural'

    @patch('services.region_theme_service.requests.get')
    def test_api_failure_returns_default(self, mock_get):
        """API failure should return default theme."""
        mock_get.side_effect = Exception("Network error")

        result = _detect_region_type_advanced(48.15, 17.11)
        assert result == 'default'


class TestThemeDefinitions:
    """Tests for THEMES dictionary structure."""

    def test_mountain_theme_is_green(self):
        """Mountain theme should use green tones."""
        assert '2d5a27' in THEMES['mountain']['primary']  # Green

    def test_coastal_theme_is_blue(self):
        """Coastal theme should use blue tones."""
        assert '006994' in THEMES['coastal']['primary']  # Ocean blue

    def test_urban_theme_is_dark(self):
        """Urban theme should use dark indigo."""
        assert '1a237e' in THEMES['urban']['primary']  # Indigo

    def test_rural_theme_is_brown(self):
        """Rural theme should use brown/earth tones."""
        assert '5d4037' in THEMES['rural']['primary']  # Brown

    def test_default_theme_is_steel_blue(self):
        """Default theme should use steel blue."""
        assert '1b5e83' in THEMES['default']['primary']