"""
Unit Tests - Links Service
===========================
Tests link generation for POIs.
"""

import pytest
from services.links_service import (
    generate_links,
    _get_contextual_links,
    _build_alltrails_link,
    _build_reddit_link,
    _build_wikivoyage_link,
    _build_inaturalist_link,
    _t,
)


class TestGenerateLinks:
    """Tests for generate_links function."""

    def test_returns_5_links_max(self, sample_poi):
        """Should return exactly 5 links."""
        links = generate_links(sample_poi, 'en')
        assert len(links) == 5

    def test_always_has_google_maps(self, sample_poi):
        """Should always include Google Maps link."""
        links = generate_links(sample_poi, 'en')
        types = [l['type'] for l in links]
        assert 'google_maps' in types

    def test_always_has_wikipedia(self, sample_poi):
        """Should always include Wikipedia link."""
        links = generate_links(sample_poi, 'en')
        types = [l['type'] for l in links]
        assert 'wikipedia' in types

    def test_google_maps_url_format(self, sample_poi):
        """Google Maps link should contain coordinates."""
        links = generate_links(sample_poi, 'en')
        gmaps = next(l for l in links if l['type'] == 'google_maps')
        assert '48.1422' in gmaps['url']
        assert '17.1' in gmaps['url']
        assert 'google.com/maps' in gmaps['url']

    def test_all_links_have_url(self, sample_poi):
        """All links should have a valid URL starting with http."""
        links = generate_links(sample_poi, 'en')
        for link in links:
            assert link['url'].startswith('http'), f"Bad URL: {link['url']}"

    def test_all_links_have_icon(self, sample_poi):
        """All links should have an icon."""
        links = generate_links(sample_poi, 'en')
        for link in links:
            assert link['icon'], f"Missing icon for {link['type']}"

    def test_all_links_have_label(self, sample_poi):
        """All links should have a label."""
        links = generate_links(sample_poi, 'en')
        for link in links:
            assert link['label'], f"Missing label for {link['type']}"

    def test_all_links_have_type(self, sample_poi):
        """All links should have a type field."""
        links = generate_links(sample_poi, 'en')
        for link in links:
            assert link['type'], f"Missing type"

    def test_official_website_included_when_available(self, sample_poi):
        """Should include official website if POI has one."""
        sample_poi['official_website'] = 'https://www.test-castle.sk'
        links = generate_links(sample_poi, 'en')
        types = [l['type'] for l in links]
        assert 'official' in types

    def test_wikipedia_search_fallback(self):
        """Without wiki_url, should generate Wikipedia search link."""
        poi = {
            'name': 'Unknown Place',
            'name_en': 'Unknown Place',
            'lat': 48.15,
            'lon': 17.11,
            'type': 'cultural',
            'wiki_url': '',
            'official_website': '',
        }
        links = generate_links(poi, 'en')
        wiki = next(l for l in links if l['type'] == 'wikipedia')
        assert 'Special:Search' in wiki['url']
        assert 'Unknown' in wiki['url']

    def test_slovak_wikipedia_for_sk_lang(self):
        """Slovak language should use sk.wikipedia."""
        poi = {
            'name': 'Hrad',
            'name_en': 'Castle',
            'lat': 48.15,
            'lon': 17.11,
            'type': 'historic',
            'wiki_url': '',
            'official_website': '',
        }
        links = generate_links(poi, 'sk')
        wiki = next(l for l in links if l['type'] == 'wikipedia')
        assert 'sk.wikipedia.org' in wiki['url']


class TestContextualLinks:
    """Tests for _get_contextual_links function."""

    def test_nature_gets_alltrails(self):
        """Nature POI should get AllTrails link."""
        links = _get_contextual_links('nature', 'Peak', 'Peak', 48.15, 17.11, 'en')
        types = [l['type'] for l in links]
        assert 'alltrails' in types

    def test_nature_gets_reddit_hiking(self):
        """Nature POI should get Reddit r/hiking link."""
        links = _get_contextual_links('nature', 'Peak', 'Peak', 48.15, 17.11, 'en')
        reddit = next(l for l in links if l['type'] == 'reddit')
        assert 'hiking' in reddit['url']

    def test_historic_gets_wikivoyage(self):
        """Historic POI should get Wikivoyage link."""
        links = _get_contextual_links('historic', 'Castle', 'Castle', 48.15, 17.11, 'en')
        types = [l['type'] for l in links]
        assert 'wikivoyage' in types

    def test_historic_gets_reddit_travel(self):
        """Historic POI should get Reddit r/travel link."""
        links = _get_contextual_links('historic', 'Castle', 'Castle', 48.15, 17.11, 'en')
        reddit = next(l for l in links if l['type'] == 'reddit')
        assert 'travel' in reddit['url']

    def test_geology_gets_inaturalist(self):
        """Geology POI should get iNaturalist link."""
        links = _get_contextual_links('geology', 'Cave', 'Cave', 48.15, 17.11, 'en')
        types = [l['type'] for l in links]
        assert 'inaturalist' in types

    def test_returns_2_links(self):
        """Should always return exactly 2 contextual links."""
        for poi_type in ['nature', 'historic', 'religious', 'geology', 'cultural']:
            links = _get_contextual_links(poi_type, 'Test', 'Test', 48.15, 17.11, 'en')
            assert len(links) == 2, f"Type '{poi_type}' returned {len(links)} links"


class TestLinkBuilders:
    """Tests for individual link builder functions."""

    def test_alltrails_link(self):
        url = _build_alltrails_link('High Tatras', 49.0, 20.0)
        assert 'alltrails.com' in url
        assert 'High' in url

    def test_reddit_link(self):
        url = _build_reddit_link('Bratislava Castle', 'travel')
        assert 'reddit.com/r/travel' in url
        assert 'Bratislava' in url

    def test_reddit_link_hiking(self):
        url = _build_reddit_link('Mountain Peak', 'hiking')
        assert 'reddit.com/r/hiking' in url

    def test_wikivoyage_link_english(self):
        url = _build_wikivoyage_link('Prague', 'en')
        assert 'en.wikivoyage.org' in url
        assert 'Prague' in url

    def test_wikivoyage_link_slovak(self):
        url = _build_wikivoyage_link('Praha', 'sk')
        assert 'sk.wikivoyage.org' in url

    def test_inaturalist_link(self):
        url = _build_inaturalist_link(48.15, 17.11)
        assert 'inaturalist.org' in url
        assert '48.15' in url
        assert '17.11' in url


class TestTranslationHelper:
    """Tests for _t translation helper."""

    def test_returns_slovak_for_sk(self):
        assert _t('Slovensky', 'English', 'sk') == 'Slovensky'

    def test_returns_english_for_en(self):
        assert _t('Slovensky', 'English', 'en') == 'English'

    def test_returns_english_for_other(self):
        assert _t('Slovensky', 'English', 'de') == 'English'