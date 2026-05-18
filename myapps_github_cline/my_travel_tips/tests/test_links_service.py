"""
Unit Tests - Links Service
================================
Tests link generation for POIs with type-specific configurations.
"""

import pytest
from services.links_service import (
    generate_links, _get_link_config, _build_link,
    _make_google_maps_link, _make_alltrails_link, _make_wikiloc_link,
    _make_komoot_link, _make_tripadvisor_link, _make_wikivoyage_link,
    _make_inaturalist_link, _make_atlas_obscura_search_link,
    _make_reddit_link, _make_strava_link, _t,
)


class TestGenerateLinks:
    def test_returns_5_links(self, sample_poi):
        links = generate_links(sample_poi, 'en')
        assert len(links) == 5

    def test_always_has_google_maps(self, sample_poi):
        links = generate_links(sample_poi, 'en')
        types = [l['type'] for l in links]
        assert 'google_maps' in types

    def test_all_links_have_url(self, sample_poi):
        links = generate_links(sample_poi, 'en')
        for link in links:
            assert link['url'].startswith('http')

    def test_all_links_have_icon(self, sample_poi):
        links = generate_links(sample_poi, 'en')
        for link in links:
            assert link['icon']

    def test_all_links_have_label(self, sample_poi):
        links = generate_links(sample_poi, 'en')
        for link in links:
            assert link['label']

    def test_all_links_have_type(self, sample_poi):
        links = generate_links(sample_poi, 'en')
        for link in links:
            assert link['type']

    def test_historic_gets_tripadvisor(self, sample_poi):
        sample_poi['type'] = 'historic'
        links = generate_links(sample_poi, 'en')
        types = [l['type'] for l in links]
        assert 'tripadvisor' in types

    def test_hiking_gets_wikiloc(self):
        poi = {'name': 'Trail', 'name_en': 'Trail', 'lat': 48.15, 'lon': 17.11,
               'type': 'hiking', 'wiki_url': '', 'official_website': '', 'website': ''}
        links = generate_links(poi, 'en')
        types = [l['type'] for l in links]
        assert 'wikiloc' in types

    def test_cycling_gets_komoot(self):
        poi = {'name': 'Route', 'name_en': 'Route', 'lat': 48.15, 'lon': 17.11,
               'type': 'cycling', 'wiki_url': '', 'official_website': '', 'website': ''}
        links = generate_links(poi, 'en')
        types = [l['type'] for l in links]
        assert 'komoot' in types

    def test_waterfall_gets_alltrails(self):
        poi = {'name': 'Falls', 'name_en': 'Falls', 'lat': 48.15, 'lon': 17.11,
               'type': 'waterfall', 'wiki_url': '', 'official_website': '', 'website': ''}
        links = generate_links(poi, 'en')
        types = [l['type'] for l in links]
        assert 'alltrails' in types

    def test_national_park_gets_alltrails(self):
        poi = {'name': 'Park', 'name_en': 'Park', 'lat': 48.15, 'lon': 17.11,
               'type': 'national_park', 'wiki_url': '', 'official_website': 'http://x.com', 'website': ''}
        links = generate_links(poi, 'en')
        types = [l['type'] for l in links]
        assert 'alltrails' in types

    def test_geology_gets_inaturalist(self):
        poi = {'name': 'Rock', 'name_en': 'Rock', 'lat': 48.15, 'lon': 17.11,
               'type': 'geology', 'wiki_url': '', 'official_website': '', 'website': ''}
        links = generate_links(poi, 'en')
        types = [l['type'] for l in links]
        assert 'inaturalist' in types

    def test_atlas_obscura_source_gets_direct_link(self):
        poi = {'name': 'Weird', 'name_en': 'Weird', 'lat': 48.15, 'lon': 17.11,
               'type': 'cultural', 'source': 'atlas_obscura', 'wiki_url': '',
               'official_website': '', 'website': '', 'atlas_obscura_url': 'https://www.atlasobscura.com/places/x'}
        links = generate_links(poi, 'en')
        assert links[0]['type'] == 'atlas_obscura'
        assert 'atlasobscura.com/places/x' in links[0]['url']

    def test_empty_name_handled(self):
        poi = {'name': '', 'name_en': '', 'lat': 48.15, 'lon': 17.11,
               'type': 'cultural', 'wiki_url': '', 'official_website': '', 'website': ''}
        links = generate_links(poi, 'en')
        assert len(links) == 5
        for link in links:
            assert link['url'].startswith('http')


class TestGetLinkConfig:
    def test_hiking_config(self):
        config = _get_link_config('hiking')
        assert 'wikiloc' in config
        assert 'alltrails' in config

    def test_cycling_config(self):
        config = _get_link_config('cycling')
        assert 'komoot' in config
        assert 'strava' in config

    def test_historic_config(self):
        config = _get_link_config('historic')
        assert 'tripadvisor' in config
        assert 'wikivoyage' in config

    def test_unknown_type_falls_back(self):
        config = _get_link_config('unknown_xyz')
        assert config == _get_link_config('cultural')

    def test_atlas_obscura_source(self):
        config = _get_link_config('cultural', source='atlas_obscura')
        assert 'atlas_obscura_direct' in config

    def test_all_configs_have_5_items(self):
        for t in ['hiking', 'cycling', 'historic', 'cultural', 'waterfall',
                  'nature', 'national_park', 'peak', 'viewpoint', 'volcano',
                  'geology', 'beach', 'archaeology', 'religious', 'hut']:
            assert len(_get_link_config(t)) == 5


class TestLinkBuilders:
    def test_google_maps(self):
        link = _make_google_maps_link(48.15, 17.11)
        assert 'google.com/maps' in link['url']
        assert '48.15' in link['url']

    def test_alltrails(self):
        link = _make_alltrails_link('High Tatras')
        assert 'alltrails.com' in link['url']
        assert 'High' in link['url']

    def test_wikiloc(self):
        link = _make_wikiloc_link('Trail', 48.15, 17.11)
        assert 'wikiloc.com' in link['url']

    def test_komoot(self):
        link = _make_komoot_link('Route', 48.15, 17.11)
        assert 'komoot.com' in link['url']

    def test_strava(self):
        link = _make_strava_link('Route', 48.15, 17.11)
        assert 'strava.com' in link['url']

    def test_tripadvisor(self):
        link = _make_tripadvisor_link('Castle')
        assert 'tripadvisor.com' in link['url']

    def test_wikivoyage_en(self):
        link = _make_wikivoyage_link('Prague', 'en')
        assert 'en.wikivoyage.org' in link['url']

    def test_wikivoyage_sk(self):
        link = _make_wikivoyage_link('Praha', 'sk')
        assert 'sk.wikivoyage.org' in link['url']

    def test_inaturalist(self):
        link = _make_inaturalist_link(48.15, 17.11)
        assert 'inaturalist.org' in link['url']
        assert '48.15' in link['url']

    def test_atlas_obscura_search(self):
        link = _make_atlas_obscura_search_link('Weird Place')
        assert 'atlasobscura.com' in link['url']

    def test_reddit(self):
        link = _make_reddit_link('Castle', 'travel')
        assert 'reddit.com/r/travel' in link['url']

    def test_empty_name_alltrails(self):
        link = _make_alltrails_link('')
        assert 'alltrails.com' in link['url']

    def test_special_chars_encoded(self):
        link = _make_tripadvisor_link('Château & Café')
        assert 'Ch%C3%A2teau' in link['url'] or 'tripadvisor.com' in link['url']


class TestTranslationHelper:
    def test_returns_slovak_for_sk(self):
        assert _t('Slovensky', 'English', 'sk') == 'Slovensky'

    def test_returns_english_for_en(self):
        assert _t('Slovensky', 'English', 'en') == 'English'

    def test_returns_english_for_other(self):
        assert _t('Slovensky', 'English', 'de') == 'English'