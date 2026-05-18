"""
Overpass API Service
====================
Queries OpenStreetMap data via Overpass API for Points of Interest.
Separates results into mainstream (well-known) and alternative (hidden gems).
Free, no API key required.

Supports radius up to 150km with intelligent query scaling.

v1.1 - Extended tags for hiking, cycling, nature, historic sites worldwide.
"""

import requests
import math
import time

# Primary and fallback Overpass API servers
OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

USER_AGENT = "MyTravelTips/1.1 (travel-poi-discovery)"

# Tags that indicate MAINSTREAM / popular POIs
MAINSTREAM_TAGS = [
    # Tourism & Attractions
    'tourism=attraction',
    'tourism=museum',
    'tourism=gallery',
    'tourism=theme_park',
    'tourism=zoo',
    'tourism=aquarium',
    'tourism=resort',
    # Historic
    'historic=castle',
    'historic=palace',
    'historic=monument',
    'historic=memorial',
    'historic=city_gate',
    'historic=city_wall',
    'historic=manor',
    # Leisure & Parks
    'leisure=park',
    'leisure=water_park',
    'leisure=nature_reserve',
    # Culture
    'amenity=theatre',
    'amenity=arts_centre',
    'amenity=marketplace',
    # Protected areas
    'boundary=national_park',
    'boundary=protected_area',
]

# Tags that indicate ALTERNATIVE / unique / hidden gem POIs
ALTERNATIVE_TAGS = [
    # Unique nature
    'tourism=artwork',
    'tourism=viewpoint',
    'natural=cave_entrance',
    'waterway=waterfall',
    'waterway=rapids',
    'geological=*',
    'natural=peak',
    'natural=spring',
    'natural=hot_spring',
    'natural=arch',
    'natural=geyser',
    'natural=volcano',
    'natural=glacier',
    'natural=beach',
    'natural=rock',
    # Unique historic
    'historic=ruins',
    'historic=archaeological_site',
    'historic=aqueduct',
    'historic=wreck',
    'historic=wayside_shrine',
    'historic=boundary_stone',
    'historic=mine',
    # Unique man-made
    'man_made=lighthouse',
    'man_made=windmill',
    'man_made=tower',
    # Other unique
    'amenity=monastery',
    'building=church',
    'leisure=garden',
    'tourism=wilderness_hut',
]

# Tags for hiking & cycling routes (special handling)
HIKING_TAGS = [
    'route=hiking',
    'route=foot',
]

CYCLING_TAGS = [
    'route=bicycle',
]


def get_pois(lat, lon, radius_km, custom_tags=None):
    """
    Get POIs from Overpass API within given radius.
    Supports radius up to 150km.

    Args:
        lat, lon: center coordinates
        radius_km: search radius in km
        custom_tags: optional list of OSM tags from frontend checkboxes
                     If provided, uses these instead of default MAINSTREAM/ALTERNATIVE split

    Returns dict with 'mainstream' and 'alternative' lists.
    """
    radius_m = int(radius_km * 1000)

    # Determine query parameters based on radius
    config = _get_query_config(radius_km)

    if custom_tags:
        # Separate route tags from POI tags (routes need different query)
        route_tags = [t for t in custom_tags if t.startswith('route=')]
        poi_tags = [t for t in custom_tags if not t.startswith('route=')]

        all_pois = []

        # Query POI tags
        if poi_tags:
            poi_raw = _query_overpass(lat, lon, radius_m, poi_tags, config)
            all_pois.extend(_process_pois(poi_raw, lat, lon, 'mainstream'))

        # Query route tags (different query structure for relations)
        if route_tags:
            route_raw = _query_overpass_routes(lat, lon, radius_m, route_tags, config)
            all_pois.extend(_process_pois(route_raw, lat, lon, 'mainstream'))

        # Sort by score
        all_pois.sort(key=lambda x: x.get('score', 0), reverse=True)

        # Top 10 = mainstream (most notable/popular)
        mainstream = all_pois[:10]
        for poi in mainstream:
            poi['category'] = 'mainstream'

        # Next 10 = alternative (less known but interesting)
        alternative = all_pois[10:20]
        for poi in alternative:
            poi['category'] = 'alternative'

    else:
        # Default behavior: use predefined tag lists
        mainstream_raw = _query_overpass(lat, lon, radius_m, MAINSTREAM_TAGS, config)
        time.sleep(0.5)
        alternative_raw = _query_overpass(lat, lon, radius_m, ALTERNATIVE_TAGS, config)

        # Process and score
        mainstream = _process_pois(mainstream_raw, lat, lon, 'mainstream')
        alternative = _process_pois(alternative_raw, lat, lon, 'alternative')

        # Remove duplicates between lists (prefer mainstream)
        mainstream_names = {poi['name'].lower() for poi in mainstream if poi.get('name')}
        alternative = [poi for poi in alternative
                       if poi.get('name', '').lower() not in mainstream_names]

        # Sort by score
        mainstream.sort(key=lambda x: x.get('score', 0), reverse=True)
        alternative.sort(key=lambda x: x.get('score', 0), reverse=True)

    return {
        'mainstream': mainstream[:10],
        'alternative': alternative[:10]
    }


def _get_query_config(radius_km):
    """
    Get query configuration based on radius size.
    Larger radius = longer timeout, more results needed.
    """
    if radius_km <= 25:
        return {'timeout': 30, 'maxsize': 10485760, 'limit': 200}
    elif radius_km <= 50:
        return {'timeout': 45, 'maxsize': 26214400, 'limit': 300}
    elif radius_km <= 100:
        return {'timeout': 60, 'maxsize': 52428800, 'limit': 400}
    else:  # 100-150km
        return {'timeout': 90, 'maxsize': 104857600, 'limit': 500}


def _query_overpass(lat, lon, radius_m, tags, config):
    """
    Build and execute Overpass query for given tags.
    Uses GET method with proper headers.
    Tries fallback servers on failure.
    """
    if not tags:
        return []

    # Build compact query using regex for multiple values of same key
    query = _build_query(lat, lon, radius_m, tags, config)

    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'application/json',
    }

    # Try each server
    for server_url in OVERPASS_SERVERS:
        try:
            response = requests.get(
                server_url,
                params={'data': query},
                headers=headers,
                timeout=config['timeout'] + 10
            )

            if response.status_code == 200:
                data = response.json()
                elements = data.get('elements', [])
                print(f"Overpass: got {len(elements)} elements from {server_url.split('/')[2]}")
                return elements
            elif response.status_code == 429:
                # Rate limited - wait and try next server
                print(f"Overpass rate limited on {server_url.split('/')[2]}, trying next...")
                time.sleep(2)
                continue
            elif response.status_code == 504:
                # Timeout - try next server
                print(f"Overpass timeout on {server_url.split('/')[2]}, trying next...")
                continue
            else:
                print(f"Overpass error {response.status_code} on {server_url.split('/')[2]}")
                continue

        except requests.exceptions.Timeout:
            print(f"Overpass timeout (requests) on {server_url.split('/')[2]}")
            continue
        except requests.RequestException as e:
            print(f"Overpass request error: {e}")
            continue
        except (ValueError, KeyError) as e:
            print(f"Overpass JSON parse error: {e}")
            continue

    print("All Overpass servers failed!")
    return []


def _query_overpass_routes(lat, lon, radius_m, route_tags, config):
    """
    Query Overpass for route relations (hiking, cycling).
    Routes are stored as relations in OSM, need different query structure.
    """
    if not route_tags:
        return []

    timeout = config['timeout']

    # Build route-specific query
    route_queries = []
    for tag in route_tags:
        if '=' in tag:
            key, value = tag.split('=', 1)
            route_queries.append(
                f'relation["{key}"="{value}"](around:{radius_m},{lat},{lon});'
            )

    if not route_queries:
        return []

    query = f"""[out:json][timeout:{timeout}];
(
{chr(10).join('  ' + rq for rq in route_queries)}
);
out center;"""

    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'application/json',
    }

    for server_url in OVERPASS_SERVERS:
        try:
            response = requests.get(
                server_url,
                params={'data': query},
                headers=headers,
                timeout=config['timeout'] + 10
            )

            if response.status_code == 200:
                data = response.json()
                elements = data.get('elements', [])
                print(f"Overpass routes: got {len(elements)} elements")
                return elements
            else:
                continue

        except (requests.RequestException, ValueError):
            continue

    return []


def _build_query(lat, lon, radius_m, tags, config):
    """
    Build an optimized Overpass QL query.
    Groups tags by key for efficiency.
    """
    timeout = config['timeout']
    maxsize = config['maxsize']

    # Group tags by key for regex optimization
    # e.g. tourism=attraction, tourism=museum -> ["tourism"~"attraction|museum"]
    key_groups = {}
    wildcard_keys = []

    for tag in tags:
        if '=' in tag:
            key, value = tag.split('=', 1)
            if value == '*':
                wildcard_keys.append(key)
            else:
                if key not in key_groups:
                    key_groups[key] = []
                key_groups[key].append(value)

    # Build filter parts
    tag_queries = []

    # Grouped by key using regex (much more efficient)
    for key, values in key_groups.items():
        if len(values) == 1:
            filter_str = f'["{key}"="{values[0]}"]'
        else:
            regex = '|'.join(values)
            filter_str = f'["{key}"~"^({regex})$"]'

        tag_queries.append(f'nwr{filter_str}(around:{radius_m},{lat},{lon});')

    # Wildcard keys
    for key in wildcard_keys:
        tag_queries.append(f'nwr["{key}"](around:{radius_m},{lat},{lon});')

    if not tag_queries:
        return f'[out:json][timeout:{timeout}];out;'

    query = f"""[out:json][timeout:{timeout}];
(
{chr(10).join('  ' + tq for tq in tag_queries)}
);
out center;"""

    return query


def _process_pois(elements, center_lat, center_lon, category):
    """
    Process raw Overpass elements into structured POI objects.
    Calculate a relevance/popularity score for sorting.
    """
    pois = []
    seen_names = set()

    for element in elements:
        tags = element.get('tags', {})
        name = tags.get('name', '')

        # Skip unnamed POIs
        if not name:
            continue

        # Skip duplicates
        name_lower = name.lower()
        if name_lower in seen_names:
            continue
        seen_names.add(name_lower)

        # Get coordinates
        if element.get('type') == 'node':
            poi_lat = element.get('lat', 0)
            poi_lon = element.get('lon', 0)
        else:
            center = element.get('center', {})
            poi_lat = center.get('lat', element.get('lat', 0))
            poi_lon = center.get('lon', element.get('lon', 0))

        if not poi_lat or not poi_lon:
            continue

        # Calculate distance from center
        distance_km = _haversine(center_lat, center_lon, poi_lat, poi_lon)

        # Determine POI type/category
        poi_type = _determine_poi_type(tags)

        # Calculate score
        score = _calculate_score(tags, distance_km, category)

        # Get Wikipedia/Wikidata info if available
        wikipedia = tags.get('wikipedia', '')
        wikidata = tags.get('wikidata', '')

        poi = {
            'name': name,
            'name_en': tags.get('name:en', name),
            'name_sk': tags.get('name:sk', ''),
            'lat': poi_lat,
            'lon': poi_lon,
            'distance_km': round(distance_km, 1),
            'type': poi_type,
            'category': category,
            'score': score,
            'wikipedia': wikipedia,
            'wikidata': wikidata,
            'website': tags.get('website', tags.get('url', '')),
            'description': tags.get('description', ''),
            'opening_hours': tags.get('opening_hours', ''),
            'tags': {
                'tourism': tags.get('tourism', ''),
                'historic': tags.get('historic', ''),
                'natural': tags.get('natural', ''),
                'leisure': tags.get('leisure', ''),
                'amenity': tags.get('amenity', ''),
                'man_made': tags.get('man_made', ''),
                'geological': tags.get('geological', ''),
                'waterway': tags.get('waterway', ''),
                'route': tags.get('route', ''),
                'boundary': tags.get('boundary', ''),
            },
            'is_outdoor': _is_outdoor(tags)
        }

        pois.append(poi)

    return pois


def _determine_poi_type(tags):
    """Determine the type category for link generation."""
    # Hiking/Cycling routes
    if tags.get('route') in ['hiking', 'foot']:
        return 'hiking'
    if tags.get('route') == 'bicycle':
        return 'cycling'

    # Nature types
    if tags.get('natural') == 'peak':
        return 'peak'
    if tags.get('tourism') == 'viewpoint':
        return 'viewpoint'
    if tags.get('natural') in ['cave_entrance', 'spring', 'hot_spring', 'arch']:
        return 'nature'
    if tags.get('waterway') == 'waterfall':
        return 'waterfall'
    if tags.get('waterway') == 'rapids':
        return 'nature'
    if tags.get('natural') in ['geyser', 'volcano', 'glacier']:
        return 'volcano'
    if tags.get('natural') in ['beach']:
        return 'beach'
    if tags.get('natural') == 'rock':
        return 'geology'
    if tags.get('geological'):
        return 'geology'
    if tags.get('leisure') in ['park', 'garden', 'nature_reserve']:
        return 'nature'
    if tags.get('boundary') in ['national_park', 'protected_area']:
        return 'national_park'

    # Historic types
    if tags.get('historic') in ['castle', 'palace', 'manor', 'city_gate', 'city_wall']:
        return 'historic'
    if tags.get('historic') in ['ruins', 'archaeological_site', 'aqueduct', 'wreck']:
        return 'archaeology'
    if tags.get('historic') in ['monument', 'memorial', 'mine']:
        return 'historic'

    # Religious
    if tags.get('amenity') in ['monastery', 'place_of_worship']:
        return 'religious'
    if tags.get('building') == 'church':
        return 'religious'

    # Cultural
    if tags.get('tourism') in ['museum', 'gallery', 'attraction', 'theme_park',
                                'zoo', 'aquarium', 'resort']:
        return 'cultural'
    if tags.get('amenity') in ['theatre', 'arts_centre', 'marketplace']:
        return 'cultural'

    # Man-made unique
    if tags.get('man_made') in ['lighthouse', 'windmill', 'tower']:
        return 'historic'

    # Wilderness hut
    if tags.get('tourism') == 'wilderness_hut':
        return 'hut'

    return 'cultural'


def _calculate_score(tags, distance_km, category):
    """
    Calculate a relevance/popularity score.
    Higher score = more relevant/interesting.
    """
    score = 0

    # Wikipedia/Wikidata presence (indicates notability)
    if tags.get('wikipedia'):
        score += 30
    if tags.get('wikidata'):
        score += 20

    # Number of tags (more tags = better documented = more popular)
    tag_count = len(tags)
    score += min(tag_count * 2, 20)

    # Website presence
    if tags.get('website') or tags.get('url'):
        score += 10

    # Distance penalty (closer = better, but not too much)
    if distance_km < 5:
        score += 15
    elif distance_km < 15:
        score += 10
    elif distance_km < 30:
        score += 5
    elif distance_km < 60:
        score += 2

    # Opening hours presence (means it's a managed attraction)
    if tags.get('opening_hours'):
        score += 5

    # Name in English available (more international = more notable)
    if tags.get('name:en'):
        score += 5

    # Mainstream bonus: managed tourist attractions
    if category == 'mainstream':
        if tags.get('tourism') in ['attraction', 'museum', 'zoo', 'aquarium', 'theme_park']:
            score += 15
        if tags.get('boundary') in ['national_park', 'protected_area']:
            score += 20
        if tags.get('historic') in ['castle', 'palace']:
            score += 10

    # Alternative bonus: unique/unusual types
    if category == 'alternative':
        unusual_values = {
            'natural': ['cave_entrance', 'hot_spring', 'arch', 'geyser', 'volcano',
                        'glacier', 'rock'],
            'man_made': ['lighthouse', 'tower'],
            'waterway': ['waterfall', 'rapids'],
            'geological': None,  # Any value
            'historic': ['aqueduct', 'wreck', 'ruins', 'archaeological_site'],
        }
        for key, values in unusual_values.items():
            tag_val = tags.get(key)
            if tag_val:
                if values is None or tag_val in values:
                    score += 15

        # Penalty for too generic items
        if tags.get('historic') in ['boundary_stone', 'wayside_shrine']:
            score -= 10

    return score


def _is_outdoor(tags):
    """Determine if POI is primarily an outdoor activity."""
    outdoor_indicators = [
        tags.get('natural'),
        tags.get('waterway'),
        tags.get('geological'),
        tags.get('tourism') == 'viewpoint',
        tags.get('leisure') in ['park', 'garden', 'nature_reserve'],
        tags.get('man_made') in ['lighthouse', 'windmill'],
        tags.get('historic') == 'ruins',
        tags.get('route') in ['hiking', 'foot', 'bicycle'],
        tags.get('boundary') in ['national_park', 'protected_area'],
        tags.get('tourism') == 'wilderness_hut',
    ]
    return any(outdoor_indicators)


def _haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in km using Haversine formula."""
    R = 6371  # Earth's radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c
