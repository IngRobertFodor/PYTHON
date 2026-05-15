"""
Integration Tests - Frontend Static Files
===========================================
Verifies that frontend files exist and contain expected content.
These tests check actual file content (no mocking needed).
"""

import pytest


class TestHTMLStructure:
    """Tests for index.html content."""

    def test_html_serves_successfully(self, client):
        response = client.get('/')
        assert response.status_code == 200

    def test_html_has_title(self, client):
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'My Travel Tips' in html

    def test_html_has_search_input(self, client):
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'location-input' in html

    def test_html_has_map_container(self, client):
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'id="map"' in html

    def test_html_has_categories_grid(self, client):
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'categories-grid' in html

    def test_html_has_explore_button(self, client):
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'explore-btn' in html

    def test_html_has_weather_section(self, client):
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'weather-section' in html

    def test_html_has_results_section(self, client):
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'results-section' in html

    def test_html_has_leaflet(self, client):
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'leaflet' in html.lower()

    def test_html_has_app_js(self, client):
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'app.js' in html

    def test_html_has_language_switch(self, client):
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'lang-btn' in html

    def test_html_has_category_groups(self, client):
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'data-group="historic"' in html
        assert 'data-group="nature"' in html
        assert 'data-group="culture"' in html


class TestCSSFiles:
    """Tests for CSS file content."""

    def test_style_css_exists(self, client):
        response = client.get('/css/style.css')
        assert response.status_code == 200

    def test_style_css_has_hero(self, client):
        response = client.get('/css/style.css')
        css = response.data.decode('utf-8')
        assert 'hero-background' in css

    def test_style_css_has_categories(self, client):
        response = client.get('/css/style.css')
        css = response.data.decode('utf-8')
        assert 'categories-section' in css

    def test_style_css_has_poi_cards(self, client):
        response = client.get('/css/style.css')
        css = response.data.decode('utf-8')
        assert 'poi-card' in css

    def test_style_css_has_responsive(self, client):
        response = client.get('/css/style.css')
        css = response.data.decode('utf-8')
        assert '@media' in css

    def test_style_css_has_variables(self, client):
        response = client.get('/css/style.css')
        css = response.data.decode('utf-8')
        assert '--primary' in css

    def test_themes_css_exists(self, client):
        response = client.get('/css/themes.css')
        assert response.status_code == 200

    def test_themes_css_has_all_themes(self, client):
        response = client.get('/css/themes.css')
        css = response.data.decode('utf-8')
        assert 'theme-mountain' in css
        assert 'theme-coastal' in css
        assert 'theme-urban' in css
        assert 'theme-rural' in css


class TestJSFiles:
    """Tests for JavaScript file content."""

    def test_app_js_exists(self, client):
        response = client.get('/js/app.js')
        assert response.status_code == 200

    def test_app_js_has_key_functions(self, client):
        response = client.get('/js/app.js')
        js = response.data.decode('utf-8')
        assert 'explore' in js
        assert 'getSelectedTags' in js

    def test_map_js_exists(self, client):
        response = client.get('/js/map.js')
        assert response.status_code == 200

    def test_map_js_has_key_functions(self, client):
        response = client.get('/js/map.js')
        js = response.data.decode('utf-8')
        assert 'MapManager' in js

    def test_weather_js_exists(self, client):
        response = client.get('/js/weather.js')
        assert response.status_code == 200

    def test_weather_js_has_key_functions(self, client):
        response = client.get('/js/weather.js')
        js = response.data.decode('utf-8')
        assert 'WeatherModule' in js

    def test_poi_js_exists(self, client):
        response = client.get('/js/poi.js')
        assert response.status_code == 200

    def test_poi_js_has_key_functions(self, client):
        response = client.get('/js/poi.js')
        js = response.data.decode('utf-8')
        assert 'POIModule' in js

    def test_i18n_js_exists(self, client):
        response = client.get('/js/i18n.js')
        assert response.status_code == 200

    def test_i18n_js_has_key_functions(self, client):
        response = client.get('/js/i18n.js')
        js = response.data.decode('utf-8')
        assert 'I18N' in js

    def test_theme_js_exists(self, client):
        response = client.get('/js/theme.js')
        assert response.status_code == 200

    def test_theme_js_has_key_functions(self, client):
        response = client.get('/js/theme.js')
        js = response.data.decode('utf-8')
        assert 'ThemeManager' in js


class TestTimeParsing:
    """Tests for time string parsing logic (used in frontend)."""

    import re

    @staticmethod
    def _parse_time(s):
        """Parse time string in various formats to minutes."""
        import re
        total = 0
        s = s.lower().strip()
        hm = re.search(r'(\d+\.?\d*)\s*(h|hod)', s)
        if hm:
            total += float(hm.group(1)) * 60
        mm = re.search(r'(\d+)\s*(m|min)', s)
        if mm:
            total += int(mm.group(1))
        if not hm and not mm:
            try:
                total = float(s)
            except ValueError:
                pass
        return round(total)

    def test_parse_plain_minutes(self):
        assert self._parse_time('60') == 60

    def test_parse_h_format(self):
        assert self._parse_time('1h') == 60

    def test_parse_h_min_format(self):
        assert self._parse_time('1h 30min') == 90

    def test_parse_hod_min_format(self):
        assert self._parse_time('2 hod 15 min') == 135

    def test_parse_min_only(self):
        assert self._parse_time('45min') == 45

    def test_parse_decimal_hours(self):
        assert self._parse_time('1.5h') == 90

    def test_parse_m_short(self):
        assert self._parse_time('30m') == 30

    def test_parse_2h(self):
        assert self._parse_time('2h') == 120