"""
Overpass API Service
====================
Queries OpenStreetMap data via Overpass API for Points of Interest.
Separates results into mainstream (well-known) and alternative (hidden gems).
Free, no API key required.

Supports radius up to 150km with intelligent query scaling.
"""

import requests
import math
import time

# Primary and fallback Overpass API servers
OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

USER_AGENT = "FodorTravelTIPs/1.0 (travel-poi-discovery)"

# Tags that indicate MAINSTREAM / popular POIs
MAINSTREAM_TAGS = [
    'tourism=attraction',
    'tourism=museum',
    'historic=castle',
    'historic=monument',
    'historic=memorial',
    'leisure=park',
    'tourism=theme_park',
    'tourism=zoo',
    'amenity=theatre',
    'tourism=aquarium',
    'leisure=water_park',
    'historic=palace',
    'tourism=gallery',
    'amenity=arts_centre',
]

# Tags that indicate ALTERNATIVE / unique / hidden gem POIs
ALTERNATIVE_TAGS = [
    'tourism=artwork',
    'tourism=viewpoint',
    'historic=ruins',
    'historic=archaeological_site',
    'natural=cave_entrance',
    'waterway=waterfall',
    'geological=*',
    'natural=peak',
    'natural=spring',
    'natural=arch',
    'man_made=lighthouse',
    'man_made=windmill',
    'historic=wayside_shrine',
    'historic=boundary_stone',
    'amenity=monastery',
    'building=church',
    'natural=hot_spring',
    'leisure=garden',
    'historic=mine',
    'historic=farm',
    'tourism=wilderness_hut',
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
        # Custom tags from frontend checkboxes
        # Single query with all selected tags, then split by score
        all_raw = _query_overpass(lat, lon, radius_m, custom_tags, config)
        
        # Process all results
        all_pois = _process_pois(all_raw, lat, lon, 'mainstream')
        
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

    print("All Overpass servers failed!")
    return []


def _build_query(lat, lon, radius_m, tags, config):
    """
    Build an optimized Overpass QL query.
    Groups tags by key for efficiency.
    """
    timeout = config['timeout']
    maxsize = config['maxsize']
    limit = config['limit']

    # Group tags by key for regex optimization
    # e.g. tourism=attraction, tourism=museum → ["tourism"~"attraction|museum"]
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
            },
            'is_outdoor': _is_outdoor(tags)
        }

        pois.append(poi)

    return pois


def _determine_poi_type(tags):
    """Determine the type category for link generation."""
    if tags.get('natural') in ['peak', 'cave_entrance', 'spring', 'arch', 'hot_spring']:
        return 'nature'
    if tags.get('waterway') == 'waterfall':
        return 'nature'
    if tags.get('geological'):
        return 'nature'
    if tags.get('tourism') == 'viewpoint':
        return 'nature'
    if tags.get('leisure') in ['park', 'garden', 'nature_reserve']:
        return 'nature'
    if tags.get('historic') in ['castle', 'palace', 'ruins', 'archaeological_site',
                                 'monument', 'memorial', 'mine']:
        return 'historic'
    if tags.get('amenity') in ['monastery', 'place_of_worship']:
        return 'religious'
    if tags.get('building') == 'church':
        return 'religious'
    if tags.get('tourism') in ['museum', 'gallery', 'attraction', 'theme_park',
                                'zoo', 'aquarium']:
        return 'cultural'
    if tags.get('man_made') in ['lighthouse', 'windmill']:
        return 'historic'
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

    # For alternative: bonus for unique/unusual types
    if category == 'alternative':
        unusual_values = {
            'natural': ['cave_entrance', 'hot_spring', 'arch'],
            'man_made': ['lighthouse'],
            'waterway': ['waterfall'],
            'geological': None,  # Any value
        }
        for key, values in unusual_values.items():
            tag_val = tags.get(key)
            if tag_val:
                if values is None or tag_val in values:
                    score += 15

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