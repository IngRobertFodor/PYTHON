"""
Unit Tests - Overpass Service (POI)
====================================
Tests POI discovery, scoring, categorization, and Overpass query building.
Uses mocked HTTP responses.
"""

import pytest
from unittest.mock import patch, MagicMock
from services.overpass_service import (
    get_pois,
    _get_query_config,
    _build_query,
    _process_pois,
    _determine_poi_type,
    _calculate_score,
    _is_outdoor,
    _haversine,
    MAINSTREAM_TAGS,
    ALTERNATIVE_TAGS,
)


class TestGetPois:
    """Tests for get_pois function."""

    @patch('services.overpass_service._query_overpass')
    def test_returns_mainstream_and_alternative(self, mock_query, sample_overpass_response):
        """Should return both mainstream and alternative POI lists."""
        mock_query.return_value = sample_overpass_response['elements']

        result = get_pois(48.15, 17.11, 25)

        assert 'mainstream' in result
        assert 'alternative' in result
        assert isinstance(result['mainstream'], list)
        assert isinstance(result['alternative'], list)

    @patch('services.overpass_service._query_overpass')
    def test_limits_to_10_per_category(self, mock_query):
        """Should return max 10 POIs per category."""
        elements = []
        for i in range(20):
            elements.append({
                'type': 'node', 'id': i, 'lat': 48.15 + i * 0.01, 'lon': 17.11,
                'tags': {'name': f'Castle {i}', 'historic': 'castle', 'wikipedia': f'en:Castle_{i}'}
            })
        mock_query.return_value = elements

        result = get_pois(48.15, 17.11, 25)

        assert len(result['mainstream']) <= 10
        assert len(result['alternative']) <= 10

    @patch('services.overpass_service._query_overpass')
    def test_custom_tags_mode(self, mock_query, sample_overpass_response):
        """Custom tags should use single query and split by score."""
        mock_query.return_value = sample_overpass_response['elements']

        result = get_pois(48.15, 17.11, 25, custom_tags=['historic=castle'])

        mock_query.assert_called_once()
        assert 'mainstream' in result
        assert 'alternative' in result

    @patch('services.overpass_service._query_overpass')
    def test_empty_results(self, mock_query):
        """Should handle empty API response."""
        mock_query.return_value = []

        result = get_pois(48.15, 17.11, 25)

        assert result['mainstream'] == []
        assert result['alternative'] == []

    @patch('services.overpass_service._query_overpass')
    def test_removes_duplicates_between_categories(self, mock_query):
        """Same POI shouldn't appear in both mainstream and alternative."""
        castle = {
            'type': 'node', 'id': 1, 'lat': 48.14, 'lon': 17.10,
            'tags': {'name': 'Test Castle', 'historic': 'castle', 'wikipedia': 'en:Test Castle'}
        }
        mock_query.return_value = [castle]

        result = get_pois(48.15, 17.11, 25)

        all_names = ([p['name'] for p in result['mainstream']] +
                     [p['name'] for p in result['alternative']])
        assert len(all_names) == len(set(n.lower() for n in all_names))


class TestGetQueryConfig:
    """Tests for _get_query_config function."""

    def test_small_radius(self):
        config = _get_query_config(10)
        assert config['timeout'] == 30
        assert config['limit'] == 200

    def test_medium_radius(self):
        config = _get_query_config(40)
        assert config['timeout'] == 45
        assert config['limit'] == 300

    def test_large_radius(self):
        config = _get_query_config(75)
        assert config['timeout'] == 60
        assert config['limit'] == 400

    def test_very_large_radius(self):
        config = _get_query_config(150)
        assert config['timeout'] == 90
        assert config['limit'] == 500


class TestBuildQuery:
    """Tests for _build_query function."""

    def test_single_tag(self):
        config = {'timeout': 30, 'maxsize': 10485760, 'limit': 200}
        query = _build_query(48.15, 17.11, 25000, ['historic=castle'], config)

        assert '[out:json]' in query
        assert '[timeout:30]' in query
        assert '"historic"="castle"' in query
        assert 'around:25000,48.15,17.11' in query
        assert 'out center' in query

    def test_multiple_tags_same_key_uses_regex(self):
        config = {'timeout': 30, 'maxsize': 10485760, 'limit': 200}
        tags = ['historic=castle', 'historic=palace', 'historic=monument']
        query = _build_query(48.15, 17.11, 25000, tags, config)

        assert '"historic"~"^(castle|palace|monument)$"' in query

    def test_wildcard_tag(self):
        config = {'timeout': 30, 'maxsize': 10485760, 'limit': 200}
        query = _build_query(48.15, 17.11, 25000, ['geological=*'], config)

        assert '"geological"' in query
        assert '="*"' not in query

    def test_mixed_keys(self):
        config = {'timeout': 30, 'maxsize': 10485760, 'limit': 200}
        tags = ['historic=castle', 'tourism=museum']
        query = _build_query(48.15, 17.11, 25000, tags, config)

        assert '"historic"="castle"' in query
        assert '"tourism"="museum"' in query


class TestProcessPois:
    """Tests for _process_pois function."""

    def test_processes_node_elements(self, sample_overpass_response):
        elements = sample_overpass_response['elements']
        result = _process_pois(elements, 48.15, 17.11, 'mainstream')

        assert len(result) == 3
        assert result[0]['name'] == 'Bratislava Castle'
        assert result[0]['lat'] == 48.1422
        assert result[0]['lon'] == 17.1000

    def test_processes_way_elements(self, sample_overpass_response):
        elements = sample_overpass_response['elements']
        result = _process_pois(elements, 48.15, 17.11, 'mainstream')

        museum = next(p for p in result if 'Museum' in p['name'])
        assert museum['lat'] == 48.1600
        assert museum['lon'] == 17.0800

    def test_skips_unnamed_pois(self):
        elements = [
            {'type': 'node', 'id': 1, 'lat': 48.15, 'lon': 17.11,
             'tags': {'historic': 'castle'}},
        ]
        result = _process_pois(elements, 48.15, 17.11, 'mainstream')
        assert len(result) == 0

    def test_skips_duplicate_names(self):
        elements = [
            {'type': 'node', 'id': 1, 'lat': 48.15, 'lon': 17.11,
             'tags': {'name': 'Test Castle', 'historic': 'castle'}},
            {'type': 'node', 'id': 2, 'lat': 48.16, 'lon': 17.12,
             'tags': {'name': 'Test Castle', 'historic': 'castle'}},
        ]
        result = _process_pois(elements, 48.15, 17.11, 'mainstream')
        assert len(result) == 1

    def test_calculates_distance(self, sample_overpass_response):
        elements = sample_overpass_response['elements']
        result = _process_pois(elements, 48.15, 17.11, 'mainstream')

        for poi in result:
            assert 'distance_km' in poi
            assert poi['distance_km'] >= 0

    def test_includes_required_fields(self, sample_overpass_response):
        elements = sample_overpass_response['elements']
        result = _process_pois(elements, 48.15, 17.11, 'mainstream')

        required = ['name', 'lat', 'lon', 'distance_km', 'type', 'category',
                    'score', 'wikipedia', 'wikidata', 'website', 'tags', 'is_outdoor']
        for poi in result:
            for field in required:
                assert field in poi, f"Missing '{field}' in '{poi['name']}'"


class TestDeterminePoiType:
    """Tests for _determine_poi_type function."""

    def test_nature_peak(self):
        assert _determine_poi_type({'natural': 'peak'}) == 'nature'

    def test_nature_cave(self):
        assert _determine_poi_type({'natural': 'cave_entrance'}) == 'nature'

    def test_nature_waterfall(self):
        assert _determine_poi_type({'waterway': 'waterfall'}) == 'nature'

    def test_nature_viewpoint(self):
        assert _determine_poi_type({'tourism': 'viewpoint'}) == 'nature'

    def test_nature_park(self):
        assert _determine_poi_type({'leisure': 'park'}) == 'nature'

    def test_historic_castle(self):
        assert _determine_poi_type({'historic': 'castle'}) == 'historic'

    def test_historic_ruins(self):
        assert _determine_poi_type({'historic': 'ruins'}) == 'historic'

    def test_religious_monastery(self):
        assert _determine_poi_type({'amenity': 'monastery'}) == 'religious'

    def test_religious_church(self):
        assert _determine_poi_type({'building': 'church'}) == 'religious'

    def test_cultural_museum(self):
        assert _determine_poi_type({'tourism': 'museum'}) == 'cultural'

    def test_cultural_zoo(self):
        assert _determine_poi_type({'tourism': 'zoo'}) == 'cultural'

    def test_default_type(self):
        assert _determine_poi_type({'amenity': 'restaurant'}) == 'cultural'


class TestCalculateScore:
    """Tests for _calculate_score function."""

    def test_wikipedia_adds_score(self):
        tags_with = {'wikipedia': 'en:Test', 'name': 'Test'}
        tags_without = {'name': 'Test'}
        score_with = _calculate_score(tags_with, 10, 'mainstream')
        score_without = _calculate_score(tags_without, 10, 'mainstream')
        assert score_with - score_without >= 30

    def test_wikidata_adds_score(self):
        tags_with = {'wikidata': 'Q12345', 'name': 'Test'}
        tags_without = {'name': 'Test'}
        score_with = _calculate_score(tags_with, 10, 'mainstream')
        score_without = _calculate_score(tags_without, 10, 'mainstream')
        assert score_with - score_without >= 20

    def test_closer_distance_higher_score(self):
        tags = {'name': 'Test', 'wikipedia': 'en:Test'}
        score_close = _calculate_score(tags, 3, 'mainstream')
        score_far = _calculate_score(tags, 50, 'mainstream')
        assert score_close > score_far

    def test_website_adds_score(self):
        """Website presence should add at least 10 points (plus tag count bonus)."""
        tags_with = {'name': 'Test', 'website': 'http://test.com'}
        tags_without = {'name': 'Test'}
        score_with = _calculate_score(tags_with, 10, 'mainstream')
        score_without = _calculate_score(tags_without, 10, 'mainstream')
        assert score_with - score_without >= 10

    def test_alternative_bonus_for_unusual(self):
        tags = {'name': 'Test Cave', 'natural': 'cave_entrance'}
        score_alt = _calculate_score(tags, 10, 'alternative')
        score_main = _calculate_score(tags, 10, 'mainstream')
        assert score_alt > score_main


class TestIsOutdoor:
    """Tests for _is_outdoor function."""

    def test_natural_feature(self):
        assert _is_outdoor({'natural': 'peak'}) is True

    def test_waterfall(self):
        assert _is_outdoor({'waterway': 'waterfall'}) is True

    def test_viewpoint(self):
        assert _is_outdoor({'tourism': 'viewpoint'}) is True

    def test_park(self):
        assert _is_outdoor({'leisure': 'park'}) is True

    def test_ruins(self):
        assert _is_outdoor({'historic': 'ruins'}) is True

    def test_museum_not_outdoor(self):
        assert _is_outdoor({'tourism': 'museum'}) is False

    def test_theatre_not_outdoor(self):
        assert _is_outdoor({'amenity': 'theatre'}) is False


class TestHaversine:
    """Tests for _haversine distance calculation."""

    def test_same_point_zero_distance(self):
        assert _haversine(48.15, 17.11, 48.15, 17.11) == 0

    def test_bratislava_to_vienna(self):
        distance = _haversine(48.15, 17.11, 48.21, 16.37)
        assert 50 < distance < 70

    def test_short_distance(self):
        distance = _haversine(48.150, 17.110, 48.151, 17.111)
        assert distance < 1

    def test_symmetry(self):
        d1 = _haversine(48.15, 17.11, 48.21, 16.37)
        d2 = _haversine(48.21, 16.37, 48.15, 17.11)
        assert abs(d1 - d2) < 0.001


class TestTagLists:
    """Tests for tag list definitions."""

    def test_mainstream_tags_format(self):
        for tag in MAINSTREAM_TAGS:
            assert '=' in tag, f"Invalid format: {tag}"

    def test_alternative_tags_format(self):
        for tag in ALTERNATIVE_TAGS:
            assert '=' in tag, f"Invalid format: {tag}"

    def test_no_overlap_between_tag_lists(self):
        overlap = set(MAINSTREAM_TAGS) & set(ALTERNATIVE_TAGS)
        assert len(overlap) == 0, f"Overlapping: {overlap}"