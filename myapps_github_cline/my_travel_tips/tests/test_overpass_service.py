"""
Unit Tests - Overpass Service (POI)
=========================================
Tests POI discovery, scoring, categorization, query building, error handling.
"""

import pytest
from unittest.mock import patch, MagicMock
from services.overpass_service import (
    get_pois, _get_query_config, _build_query, _process_pois,
    _determine_poi_type, _calculate_score, _is_outdoor, _haversine,
    _query_overpass, MAINSTREAM_TAGS, ALTERNATIVE_TAGS,
)


class TestGetPois:
    @patch('services.overpass_service._query_overpass')
    def test_returns_mainstream_and_alternative(self, mock_query, sample_overpass_response):
        mock_query.return_value = sample_overpass_response['elements']
        result = get_pois(48.15, 17.11, 25)
        assert 'mainstream' in result
        assert 'alternative' in result

    @patch('services.overpass_service._query_overpass')
    def test_limits_to_10_per_category(self, mock_query):
        elements = [{'type': 'node', 'id': i, 'lat': 48.15 + i * 0.01, 'lon': 17.11,
                     'tags': {'name': f'Castle {i}', 'historic': 'castle', 'wikipedia': f'en:C{i}'}}
                    for i in range(20)]
        mock_query.return_value = elements
        result = get_pois(48.15, 17.11, 25)
        assert len(result['mainstream']) <= 10
        assert len(result['alternative']) <= 10

    @patch('services.overpass_service._query_overpass')
    def test_custom_tags_mode(self, mock_query, sample_overpass_response):
        mock_query.return_value = sample_overpass_response['elements']
        result = get_pois(48.15, 17.11, 25, custom_tags=['historic=castle'])
        mock_query.assert_called_once()
        assert 'mainstream' in result

    @patch('services.overpass_service._query_overpass')
    def test_empty_results(self, mock_query):
        mock_query.return_value = []
        result = get_pois(48.15, 17.11, 25)
        assert result['mainstream'] == []
        assert result['alternative'] == []

    @patch('services.overpass_service._query_overpass')
    def test_removes_duplicates_between_categories(self, mock_query):
        mock_query.return_value = [{'type': 'node', 'id': 1, 'lat': 48.14, 'lon': 17.10,
                                    'tags': {'name': 'Test Castle', 'historic': 'castle'}}]
        result = get_pois(48.15, 17.11, 25)
        all_names = [p['name'] for p in result['mainstream']] + [p['name'] for p in result['alternative']]
        assert len(all_names) == len(set(n.lower() for n in all_names))


class TestGetQueryConfig:
    def test_small_radius(self):
        assert _get_query_config(10)['timeout'] == 30

    def test_medium_radius(self):
        assert _get_query_config(40)['timeout'] == 45

    def test_large_radius(self):
        assert _get_query_config(75)['timeout'] == 60

    def test_very_large_radius(self):
        assert _get_query_config(150)['timeout'] == 90


class TestBuildQuery:
    def test_single_tag(self):
        config = {'timeout': 30, 'maxsize': 10485760, 'limit': 200}
        query = _build_query(48.15, 17.11, 25000, ['historic=castle'], config)
        assert '[out:json]' in query
        assert '"historic"="castle"' in query
        assert 'around:25000,48.15,17.11' in query

    def test_multiple_tags_same_key_uses_regex(self):
        config = {'timeout': 30, 'maxsize': 10485760, 'limit': 200}
        query = _build_query(48.15, 17.11, 25000, ['historic=castle', 'historic=palace', 'historic=monument'], config)
        assert '"historic"~"^(castle|palace|monument)$"' in query

    def test_wildcard_tag(self):
        config = {'timeout': 30, 'maxsize': 10485760, 'limit': 200}
        query = _build_query(48.15, 17.11, 25000, ['geological=*'], config)
        assert '"geological"' in query
        assert '="*"' not in query

    def test_empty_tags_returns_fallback(self):
        config = {'timeout': 30, 'maxsize': 10485760, 'limit': 200}
        query = _build_query(48.15, 17.11, 25000, [], config)
        assert '[out:json]' in query


class TestProcessPois:
    def test_processes_node_elements(self, sample_overpass_response):
        result = _process_pois(sample_overpass_response['elements'], 48.15, 17.11, 'mainstream')
        assert len(result) == 3
        assert result[0]['name'] == 'Bratislava Castle'

    def test_skips_unnamed_pois(self):
        elements = [{'type': 'node', 'id': 1, 'lat': 48.15, 'lon': 17.11, 'tags': {'historic': 'castle'}}]
        assert len(_process_pois(elements, 48.15, 17.11, 'mainstream')) == 0

    def test_skips_duplicate_names(self):
        elements = [
            {'type': 'node', 'id': 1, 'lat': 48.15, 'lon': 17.11, 'tags': {'name': 'X', 'historic': 'castle'}},
            {'type': 'node', 'id': 2, 'lat': 48.16, 'lon': 17.12, 'tags': {'name': 'X', 'historic': 'castle'}},
        ]
        assert len(_process_pois(elements, 48.15, 17.11, 'mainstream')) == 1

    def test_includes_required_fields(self, sample_overpass_response):
        result = _process_pois(sample_overpass_response['elements'], 48.15, 17.11, 'mainstream')
        required = ['name', 'lat', 'lon', 'distance_km', 'type', 'category', 'score', 'tags', 'is_outdoor']
        for poi in result:
            for field in required:
                assert field in poi

    def test_skips_zero_coordinates(self):
        elements = [{'type': 'node', 'id': 1, 'lat': 0, 'lon': 0, 'tags': {'name': 'NoCoords', 'historic': 'castle'}}]
        assert len(_process_pois(elements, 48.15, 17.11, 'mainstream')) == 0


class TestDeterminePoiType:
    def test_hiking_route(self):
        assert _determine_poi_type({'route': 'hiking'}) == 'hiking'

    def test_cycling_route(self):
        assert _determine_poi_type({'route': 'bicycle'}) == 'cycling'

    def test_peak(self):
        assert _determine_poi_type({'natural': 'peak'}) == 'peak'

    def test_viewpoint(self):
        assert _determine_poi_type({'tourism': 'viewpoint'}) == 'viewpoint'

    def test_waterfall(self):
        assert _determine_poi_type({'waterway': 'waterfall'}) == 'waterfall'

    def test_volcano(self):
        assert _determine_poi_type({'natural': 'volcano'}) == 'volcano'

    def test_beach(self):
        assert _determine_poi_type({'natural': 'beach'}) == 'beach'

    def test_geology(self):
        assert _determine_poi_type({'geological': 'moraine'}) == 'geology'

    def test_national_park(self):
        assert _determine_poi_type({'boundary': 'national_park'}) == 'national_park'

    def test_historic_castle(self):
        assert _determine_poi_type({'historic': 'castle'}) == 'historic'

    def test_archaeology(self):
        assert _determine_poi_type({'historic': 'ruins'}) == 'archaeology'

    def test_religious(self):
        assert _determine_poi_type({'amenity': 'monastery'}) == 'religious'

    def test_cultural_museum(self):
        assert _determine_poi_type({'tourism': 'museum'}) == 'cultural'

    def test_hut(self):
        assert _determine_poi_type({'tourism': 'wilderness_hut'}) == 'hut'

    def test_default(self):
        assert _determine_poi_type({'amenity': 'restaurant'}) == 'cultural'


class TestCalculateScore:
    def test_wikipedia_adds_score(self):
        assert _calculate_score({'wikipedia': 'en:X', 'name': 'X'}, 10, 'mainstream') > _calculate_score({'name': 'X'}, 10, 'mainstream')

    def test_closer_distance_higher_score(self):
        tags = {'name': 'X', 'wikipedia': 'en:X'}
        assert _calculate_score(tags, 3, 'mainstream') > _calculate_score(tags, 50, 'mainstream')

    def test_mainstream_bonus(self):
        tags = {'name': 'X', 'tourism': 'attraction'}
        assert _calculate_score(tags, 10, 'mainstream') > _calculate_score(tags, 10, 'alternative')

    def test_alternative_bonus_for_unusual(self):
        tags = {'name': 'X', 'natural': 'cave_entrance'}
        assert _calculate_score(tags, 10, 'alternative') > _calculate_score(tags, 10, 'mainstream')

    def test_penalty_for_generic(self):
        tags = {'name': 'X', 'historic': 'boundary_stone'}
        score = _calculate_score(tags, 10, 'alternative')
        tags2 = {'name': 'X', 'historic': 'ruins'}
        score2 = _calculate_score(tags2, 10, 'alternative')
        assert score2 > score


class TestIsOutdoor:
    def test_natural(self):
        assert _is_outdoor({'natural': 'peak'}) is True

    def test_waterfall(self):
        assert _is_outdoor({'waterway': 'waterfall'}) is True

    def test_hiking_route(self):
        assert _is_outdoor({'route': 'hiking'}) is True

    def test_national_park(self):
        assert _is_outdoor({'boundary': 'national_park'}) is True

    def test_museum_not_outdoor(self):
        assert _is_outdoor({'tourism': 'museum'}) is False


class TestHaversine:
    def test_same_point(self):
        assert _haversine(48.15, 17.11, 48.15, 17.11) == 0

    def test_bratislava_to_vienna(self):
        assert 50 < _haversine(48.15, 17.11, 48.21, 16.37) < 70

    def test_symmetry(self):
        d1 = _haversine(48.15, 17.11, 48.21, 16.37)
        d2 = _haversine(48.21, 16.37, 48.15, 17.11)
        assert abs(d1 - d2) < 0.001


class TestTagLists:
    def test_mainstream_tags_format(self):
        for tag in MAINSTREAM_TAGS:
            assert '=' in tag

    def test_alternative_tags_format(self):
        for tag in ALTERNATIVE_TAGS:
            assert '=' in tag

    def test_no_overlap(self):
        assert len(set(MAINSTREAM_TAGS) & set(ALTERNATIVE_TAGS)) == 0

    def test_mainstream_has_national_parks(self):
        assert 'boundary=national_park' in MAINSTREAM_TAGS

    def test_alternative_has_volcanoes(self):
        assert 'natural=volcano' in ALTERNATIVE_TAGS


class TestErrorHandling:
    @patch('services.overpass_service.requests.get')
    def test_timeout_returns_empty(self, mock_get):
        import requests as req_lib
        mock_get.side_effect = req_lib.exceptions.Timeout("timeout")
        config = {'timeout': 30, 'maxsize': 10485760, 'limit': 200}
        result = _query_overpass(48.15, 17.11, 25000, ['historic=castle'], config)
        assert result == []

    @patch('services.overpass_service.requests.get')
    def test_server_error_returns_empty(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_get.return_value = mock_resp
        config = {'timeout': 30, 'maxsize': 10485760, 'limit': 200}
        result = _query_overpass(48.15, 17.11, 25000, ['historic=castle'], config)
        assert result == []

    def test_empty_tags_returns_empty(self):
        config = {'timeout': 30, 'maxsize': 10485760, 'limit': 200}
        result = _query_overpass(48.15, 17.11, 25000, [], config)
        assert result == []
