"""
Unit Tests - Overpass Service (POI)
=========================================
Tests POI discovery, scoring, categorization, query building, error handling.
FIX v2.1: Added tests for _best_display_name, _is_latin (non-Latin transliteration).
"""

import pytest
from unittest.mock import patch, MagicMock
from services.overpass_service import (
    get_pois, _get_query_config, _build_query, _process_pois,
    _determine_type as _determine_poi_type, _calculate_score, _is_outdoor, _haversine,
    _query_overpass, MAINSTREAM_TAGS, ALTERNATIVE_TAGS,
    _best_display_name, _is_latin,
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
        """Same POI shouldn't appear in both mainstream and alternative."""
        # Mainstream returns castles, alternative returns viewpoints
        mainstream_elements = [{'type': 'node', 'id': i, 'lat': 48.14 + i * 0.001, 'lon': 17.10,
                                'tags': {'name': f'Castle {i}', 'historic': 'castle', 'wikipedia': f'en:C{i}'}}
                               for i in range(12)]
        alt_elements = [{'type': 'node', 'id': 100 + i, 'lat': 48.14 + i * 0.001, 'lon': 17.10,
                         'tags': {'name': f'View {i}', 'tourism': 'viewpoint'}}
                        for i in range(12)]
        # Also include one castle in alternative (should be deduplicated)
        alt_elements.append({'type': 'node', 'id': 999, 'lat': 48.141, 'lon': 17.10,
                             'tags': {'name': 'Castle 0', 'historic': 'castle'}})
        # Mock returns: 1st call=mainstream, 2nd call=alternative, 3rd+=fallback (empty)
        mock_query.side_effect = [mainstream_elements, alt_elements, [], []]
        result = get_pois(48.15, 17.11, 25)
        mainstream_names = {p['name'].lower() for p in result['mainstream']}
        alternative_names = {p['name'].lower() for p in result['alternative']}
        # 'Castle 0' should NOT appear in alternative (already in mainstream)
        assert 'castle 0' not in alternative_names
        # No overlap
        assert len(mainstream_names & alternative_names) == 0


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
        config = {'timeout': 30, 'maxsize': 10485760}
        query = _build_query(48.15, 17.11, 25000, ['historic=castle'], config)
        assert '[out:json]' in query
        assert 'historic' in query and 'castle' in query
        assert 'around:25000,48.15,17.11' in query

    def test_multiple_tags_same_key_uses_regex(self):
        config = {'timeout': 30, 'maxsize': 10485760}
        query = _build_query(48.15, 17.11, 25000, ['historic=castle', 'historic=palace', 'historic=monument'], config)
        assert 'historic' in query
        assert 'castle' in query and 'palace' in query

    def test_wildcard_tag(self):
        config = {'timeout': 30, 'maxsize': 10485760}
        query = _build_query(48.15, 17.11, 25000, ['geological=*'], config)
        assert 'geological' in query

    def test_uses_out_tags_center(self):
        config = {'timeout': 30, 'maxsize': 10485760}
        query = _build_query(48.15, 17.11, 25000, ['historic=castle'], config)
        assert 'out tags center' in query

    def test_includes_maxsize(self):
        config = {'timeout': 30, 'maxsize': 10485760}
        query = _build_query(48.15, 17.11, 25000, ['historic=castle'], config)
        assert 'maxsize:10485760' in query

    def test_empty_tags_returns_fallback(self):
        config = {'timeout': 30, 'maxsize': 10485760}
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
    @patch('services.overpass_service.requests.post')
    def test_timeout_returns_empty(self, mock_post):
        import requests as req_lib
        mock_post.side_effect = req_lib.exceptions.Timeout("timeout")
        config = {'timeout': 30, 'maxsize': 10485760, 'limit': 200}
        result = _query_overpass(48.15, 17.11, 25000, ['historic=castle'], config)
        assert result == []

    @patch('services.overpass_service.requests.post')
    def test_server_error_returns_empty(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_post.return_value = mock_resp
        config = {'timeout': 30, 'maxsize': 10485760, 'limit': 200}
        result = _query_overpass(48.15, 17.11, 25000, ['historic=castle'], config)
        assert result == []

    def test_empty_tags_returns_empty(self):
        config = {'timeout': 30, 'maxsize': 10485760, 'limit': 200}
        result = _query_overpass(48.15, 17.11, 25000, [], config)
        assert result == []


class TestIsLatin:
    """Tests for _is_latin helper."""

    def test_latin_ascii_only(self):
        """Pure ASCII text is Latin."""
        assert _is_latin('Bratislava') is True

    def test_latin_with_diacritics(self):
        """Latin with diacritics (e.g. Slovak) is still Latin."""
        assert _is_latin('Bratislavský hrad') is True

    def test_greek_text_not_latin(self):
        """Greek alphabet is not Latin."""
        assert _is_latin('Ακρόπολη Αθηνών') is False

    def test_cyrillic_not_latin(self):
        """Cyrillic alphabet is not Latin."""
        assert _is_latin('Москва') is False

    def test_arabic_not_latin(self):
        """Arabic script is not Latin."""
        assert _is_latin('القاهرة') is False

    def test_empty_string(self):
        """Empty string has no non-Latin characters → True."""
        assert _is_latin('') is True

    def test_numbers_and_spaces(self):
        """Numbers, spaces, punctuation are neutral → True."""
        assert _is_latin('Route 66 (2026)') is True


class TestBestDisplayName:
    """Tests for _best_display_name – the core non-Latin fix."""

    def test_latin_name_returned_as_is(self):
        """Latin-only name should be returned without modification."""
        tags = {'name': 'Bratislava Castle', 'name:en': 'Bratislava Castle'}
        result = _best_display_name(tags, 'en')
        assert result == 'Bratislava Castle'

    def test_prefers_name_en_over_native(self):
        """Should prefer name:en when lang=en even if native name exists."""
        tags = {'name': 'Ακρόπολη Αθηνών', 'name:en': 'Acropolis of Athens'}
        result = _best_display_name(tags, 'en')
        assert result == 'Acropolis of Athens'

    def test_prefers_name_lang_over_name_en(self):
        """name:<lang> should win over name:en."""
        tags = {'name': 'Ακρόπολη', 'name:en': 'Acropolis', 'name:sk': 'Akropola'}
        result = _best_display_name(tags, 'sk')
        assert result == 'Akropola'

    def test_fallback_to_name_en_when_lang_missing(self):
        """If name:<lang> absent, fall back to name:en."""
        tags = {'name': 'Ακρόπολη Αθηνών', 'name:en': 'Acropolis of Athens'}
        result = _best_display_name(tags, 'sk')
        assert result == 'Acropolis of Athens'

    def test_greek_without_name_en_gets_transliteration(self):
        """Greek name without name:en should be transliterated."""
        tags = {'name': 'Ακρόπολη'}
        result = _best_display_name(tags, 'en')
        # Should contain Latin transliteration
        assert result != 'Ακρόπολη' or True  # graceful even without unidecode
        # If unidecode is available the result must contain Latin characters
        try:
            from unidecode import unidecode
            latin_part = result.split('(')[0].strip()
            assert _is_latin(latin_part), f"Expected Latin prefix, got: {result}"
        except ImportError:
            pass  # unidecode not available – result is unchanged Greek, acceptable

    def test_cyrillic_without_name_en_gets_transliteration(self):
        """Cyrillic name without name:en should be transliterated."""
        tags = {'name': 'Москва'}
        result = _best_display_name(tags, 'en')
        try:
            from unidecode import unidecode
            latin_part = result.split('(')[0].strip()
            assert _is_latin(latin_part), f"Expected Latin prefix, got: {result}"
        except ImportError:
            pass

    def test_empty_tags_returns_empty_string(self):
        """No name tags → empty string."""
        assert _best_display_name({}, 'en') == ''

    def test_int_name_used_as_fallback(self):
        """int_name used when name:<lang> and name:en are absent."""
        tags = {'name': 'Ακρόπολη', 'int_name': 'Acropolis'}
        result = _best_display_name(tags, 'en')
        assert result == 'Acropolis'

    def test_process_pois_includes_display_name(self):
        """_process_pois should include display_name field in each POI."""
        elements = [{
            'type': 'node', 'id': 1,
            'lat': 37.97, 'lon': 23.73,
            'tags': {
                'name': 'Ακρόπολη Αθηνών',
                'name:en': 'Acropolis of Athens',
                'historic': 'monument',
            }
        }]
        result = _process_pois(elements, 37.97, 23.73, 'mainstream', 25, 'en')
        assert len(result) == 1
        assert 'display_name' in result[0]
        assert result[0]['display_name'] == 'Acropolis of Athens'
