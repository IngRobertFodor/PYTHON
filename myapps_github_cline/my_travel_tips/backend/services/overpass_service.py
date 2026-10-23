"""Overpass API Service v2.0 - POI discovery with improved scoring,
parallel queries, auto-expand radius, and better deduplication.
FIX v2.1: display_name with non-Latin transliteration (Greek, Cyrillic, etc.)
"""
import requests
import math
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from unidecode import unidecode as _unidecode
    _UNIDECODE_AVAILABLE = True
except ImportError:
    _UNIDECODE_AVAILABLE = False


def _is_latin(text):
    """Return True if all significant characters are Latin/ASCII.
    Latin-extended characters (diacritics like ý, š, č, ä, ő, etc.) are
    still considered Latin since they are readable by Latin-script users.
    Only truly non-Latin scripts (Greek, Cyrillic, Arabic, CJK, etc.) return False.
    """
    for ch in text:
        if ch.isalpha():
            cp = ord(ch)
            # Latin Basic (0-127), Latin-1 Supplement (128-255),
            # Latin Extended-A (256-383), Latin Extended-B (384-591)
            # covers virtually all European Latin scripts including Slovak diacritics
            if cp > 591:
                return False
    return True


def _best_display_name(tags, lang='en'):
    """
    Pick the best human-readable name for a POI based on language priority.
    Priority: name:<lang> -> name:en -> int_name -> name:la -> name
    If the chosen name is non-Latin (e.g. Greek, Cyrillic, Arabic),
    a Latin transliteration is appended in parentheses.
    Example: 'Akropolis Athinon (Ακρόπολη Αθηνών)' -> readable for SK/EN users.
    Falls back gracefully when unidecode is unavailable.
    """
    candidates = [
        tags.get(f'name:{lang}', ''),
        tags.get('name:en', ''),
        tags.get('int_name', ''),
        tags.get('name:la', ''),
        tags.get('name', ''),
    ]
    chosen = next((c for c in candidates if c), tags.get('name', ''))

    if not chosen:
        return ''

    if _is_latin(chosen):
        return chosen

    # Non-Latin script detected – append transliteration for readability
    if _UNIDECODE_AVAILABLE:
        latin = _unidecode(chosen).strip()
        if latin and latin != chosen:
            return f'{latin} ({chosen})'
    return chosen


OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.osm.rambler.ru/cgi/interpreter",
]
USER_AGENT = "MyTravelTips/2.0 (travel-poi-discovery)"

MAINSTREAM_TAGS = [
    'tourism=attraction', 'tourism=museum', 'tourism=gallery',
    'tourism=theme_park', 'tourism=zoo', 'tourism=aquarium', 'tourism=resort',
    'historic=castle', 'historic=palace', 'historic=monument',
    'historic=memorial', 'historic=city_gate', 'historic=city_wall', 'historic=manor',
    'leisure=park', 'leisure=water_park', 'leisure=nature_reserve',
    'amenity=theatre', 'amenity=arts_centre', 'amenity=marketplace',
    'boundary=national_park', 'boundary=protected_area',
]

ALTERNATIVE_TAGS = [
    'tourism=artwork', 'tourism=viewpoint',
    'natural=cave_entrance', 'waterway=waterfall', 'waterway=rapids',
    'geological=*', 'natural=peak', 'natural=spring', 'natural=hot_spring',
    'natural=arch', 'natural=geyser', 'natural=volcano', 'natural=glacier',
    'natural=beach', 'natural=rock',
    'historic=ruins', 'historic=archaeological_site', 'historic=aqueduct',
    'historic=wreck', 'historic=wayside_shrine', 'historic=boundary_stone',
    'historic=mine', 'man_made=lighthouse', 'man_made=windmill', 'man_made=tower',
    'amenity=monastery', 'building=church', 'leisure=garden', 'tourism=wilderness_hut',
]

FALLBACK_MAINSTREAM_TAGS = [
    'tourism=viewpoint', 'leisure=garden', 'historic=memorial',
    'amenity=place_of_worship', 'tourism=information',
]
FALLBACK_ALTERNATIVE_TAGS = [
    'tourism=artwork', 'natural=spring', 'man_made=tower',
    'building=church', 'historic=wayside_shrine',
]

POI_TYPE_WEIGHTS = {
    'tourism=attraction': 25, 'tourism=museum': 20, 'tourism=zoo': 20,
    'tourism=theme_park': 25, 'historic=castle': 25, 'historic=palace': 25,
    'boundary=national_park': 30, 'waterway=waterfall': 20,
    'natural=cave_entrance': 18, 'natural=volcano': 25, 'natural=glacier': 22,
    'natural=hot_spring': 20, 'man_made=lighthouse': 15, 'natural=geyser': 22,
    'tourism=viewpoint': 10, 'leisure=park': 8, 'historic=monument': 10,
    'building=church': 5, 'historic=wayside_shrine': 3,
}


def get_pois(lat, lon, radius_km, custom_tags=None, lang='en'):
    """Get POIs from Overpass API. Auto-expands radius if not enough results."""
    radius_m = int(radius_km * 1000)
    config = _get_query_config(radius_km)
    if custom_tags:
        return _get_pois_custom(lat, lon, radius_m, radius_km, config, custom_tags, lang)
    return _get_pois_default(lat, lon, radius_m, radius_km, config, lang)


def _get_pois_custom(lat, lon, radius_m, radius_km, config, custom_tags, lang='en'):
    route_tags = [t for t in custom_tags if t.startswith('route=')]
    poi_tags = [t for t in custom_tags if not t.startswith('route=')]
    all_pois = []
    with ThreadPoolExecutor(max_workers=2) as ex:
        futures = []
        if poi_tags:
            futures.append(ex.submit(_query_overpass, lat, lon, radius_m, poi_tags, config))
        if route_tags:
            futures.append(ex.submit(_query_overpass_routes, lat, lon, radius_m, route_tags, config))
        for f in as_completed(futures):
            try:
                all_pois.extend(_process_pois(f.result(), lat, lon, 'mainstream', radius_km, lang))
            except Exception as e:
                print(f"Query error: {e}")
    all_pois.sort(key=lambda x: x.get('score', 0), reverse=True)
    mainstream = all_pois[:10]
    for p in mainstream:
        p['category'] = 'mainstream'
    alternative = all_pois[10:20]
    for p in alternative:
        p['category'] = 'alternative'
    return {'mainstream': mainstream, 'alternative': alternative}


def _get_pois_default(lat, lon, radius_m, radius_km, config, lang='en'):
    m_raw, a_raw = [], []
    with ThreadPoolExecutor(max_workers=2) as ex:
        fm = ex.submit(_query_overpass, lat, lon, radius_m, MAINSTREAM_TAGS, config)
        fa = ex.submit(_query_overpass, lat, lon, radius_m, ALTERNATIVE_TAGS, config)
        try:
            m_raw = fm.result()
        except Exception:
            pass
        try:
            a_raw = fa.result()
        except Exception:
            pass
    mainstream = _process_pois(m_raw, lat, lon, 'mainstream', radius_km, lang)
    alternative = _process_pois(a_raw, lat, lon, 'alternative', radius_km, lang)
    m_keys = {_dedup_key(p) for p in mainstream}
    alternative = [p for p in alternative if _dedup_key(p) not in m_keys]
    mainstream.sort(key=lambda x: x.get('score', 0), reverse=True)
    alternative.sort(key=lambda x: x.get('score', 0), reverse=True)
    mainstream = _fill(mainstream, lat, lon, radius_km, radius_m, config, 'mainstream', FALLBACK_MAINSTREAM_TAGS, lang)
    alternative = _fill(alternative, lat, lon, radius_km, radius_m, config, 'alternative', FALLBACK_ALTERNATIVE_TAGS, lang)
    if len(mainstream) < 5 and radius_km < 150:
        mainstream = _auto_expand(mainstream, lat, lon, radius_km, 'mainstream', MAINSTREAM_TAGS, lang)
    if len(alternative) < 5 and radius_km < 150:
        alternative = _auto_expand(alternative, lat, lon, radius_km, 'alternative', ALTERNATIVE_TAGS, lang)
    return {'mainstream': mainstream[:10], 'alternative': alternative[:10]}


def _auto_expand(lst, lat, lon, radius_km, cat, tags, lang='en'):
    ekm = min(radius_km * 1.5, 150)
    em = int(ekm * 1000)
    ec = _get_query_config(ekm)
    print(f"Auto-expand {cat}: {radius_km}km -> {ekm}km")
    raw = _query_overpass(lat, lon, em, tags, ec)
    extra = _process_pois(raw, lat, lon, cat, ekm, lang)
    keys = {_dedup_key(p) for p in lst}
    new = [p for p in extra if _dedup_key(p) not in keys]
    new.sort(key=lambda x: x.get('score', 0), reverse=True)
    lst.extend(new[:10 - len(lst)])
    return lst


def _dedup_key(poi):
    name = poi.get('name', '').lower().strip()
    return name + '|' + str(round(poi.get('lat', 0), 2)) + '|' + str(round(poi.get('lon', 0), 2))


def _fill(lst, lat, lon, rkm, rm, config, cat, ftags, lang='en'):
    if len(lst) >= 10:
        return lst
    keys = {_dedup_key(p) for p in lst}
    raw = _query_overpass(lat, lon, rm, ftags, config)
    pois = _process_pois(raw, lat, lon, cat, rkm, lang)
    new = [p for p in pois if _dedup_key(p) not in keys]
    new.sort(key=lambda x: x.get('score', 0), reverse=True)
    return lst + new[:10 - len(lst)]


def _get_query_config(radius_km):
    if radius_km <= 25:
        return {'timeout': 30, 'maxsize': 10485760}
    elif radius_km <= 50:
        return {'timeout': 45, 'maxsize': 26214400}
    elif radius_km <= 100:
        return {'timeout': 60, 'maxsize': 52428800}
    return {'timeout': 90, 'maxsize': 104857600}


def _query_overpass(lat, lon, radius_m, tags, config):
    """Send Overpass query using POST (more reliable than GET for long queries).
    Tries each server in OVERPASS_SERVERS with exponential backoff on rate-limit.
    IMPORTANT: Do NOT send 'Accept: application/json' – overpass-api.de returns 406.
    """
    if not tags:
        return []
    query = _build_query(lat, lon, radius_m, tags, config)
    # No Accept header – Overpass API does not want 'application/json' Accept value
    headers = {'User-Agent': USER_AGENT}
    timeout = config.get('timeout', 30) + 10

    for attempt, url in enumerate(OVERPASS_SERVERS):
        try:
            # Use POST – more reliable than GET for long queries
            r = requests.post(url, data={'data': query}, headers=headers, timeout=timeout)
            if r.status_code == 200:
                try:
                    elems = r.json().get('elements', [])
                    print(f"Overpass OK: {len(elems)} elems from {url.split('/')[2]}")
                    return elems
                except Exception as json_err:
                    print(f"Overpass JSON parse error from {url.split('/')[2]}: {json_err}")
                    continue
            elif r.status_code == 429:
                wait = 2 ** attempt  # exponential backoff: 1s, 2s, 4s
                print(f"Overpass 429 rate-limit from {url.split('/')[2]}, waiting {wait}s...")
                time.sleep(wait)
                continue
            elif r.status_code in (504, 502, 503):
                print(f"Overpass server error {r.status_code} from {url.split('/')[2]}, trying next...")
                continue
            else:
                print(f"Overpass unexpected status {r.status_code} from {url.split('/')[2]}")
                continue
        except requests.exceptions.Timeout:
            print(f"Overpass timeout from {url.split('/')[2]}")
            continue
        except Exception as e:
            print(f"Overpass error from {url.split('/')[2]}: {e}")
            continue

    print("Overpass: all servers failed, returning empty list")
    return []


def _query_overpass_routes(lat, lon, radius_m, route_tags, config):
    if not route_tags:
        return []
    parts = []
    for tag in route_tags:
        if '=' in tag:
            k, v = tag.split('=', 1)
            parts.append(f'  relation["{k}"="{v}"](around:{radius_m},{lat},{lon});')
    if not parts:
        return []
    nl = chr(10)
    maxsize = config.get('maxsize', 10485760)
    query = f"[out:json][timeout:{config['timeout']}][maxsize:{maxsize}];({nl}{nl.join(parts)}{nl});out tags center;"
    headers = {'User-Agent': USER_AGENT}
    timeout = config.get('timeout', 30) + 10

    for attempt, url in enumerate(OVERPASS_SERVERS):
        try:
            r = requests.post(url, data={'data': query}, headers=headers, timeout=timeout)
            if r.status_code == 200:
                try:
                    return r.json().get('elements', [])
                except Exception:
                    continue
            elif r.status_code == 429:
                time.sleep(2 ** attempt)
                continue
        except Exception:
            continue
    return []


def _build_query(lat, lon, radius_m, tags, config):
    """Build an Overpass QL query for the given tags and location.
    Uses 'out tags center;' so that ways/relations return their tags AND center point.
    Adds [maxsize:...] to prevent server-side memory overflow on large queries.
    """
    key_groups = {}
    wildcards = []
    for tag in tags:
        if '=' in tag:
            k, v = tag.split('=', 1)
            if v == '*':
                wildcards.append(k)
            else:
                key_groups.setdefault(k, []).append(v)
    parts = []
    for k, vals in key_groups.items():
        if len(vals) == 1:
            f = f'["{k}"="{vals[0]}"]'
        else:
            f = '["{k}"~"^({v})$"]'.format(k=k, v='|'.join(vals))
        parts.append(f'  nwr{f}(around:{radius_m},{lat},{lon});')
    for k in wildcards:
        parts.append(f'  nwr["{k}"](around:{radius_m},{lat},{lon});')
    nl = chr(10)
    maxsize = config.get('maxsize', 10485760)
    timeout = config.get('timeout', 30)
    # 'out tags center' returns tags AND center coords for ways/relations (critical!)
    return f"[out:json][timeout:{timeout}][maxsize:{maxsize}];({nl}{nl.join(parts)}{nl});out tags center;"


def _process_pois(elements, center_lat, center_lon, category, max_radius_km=None, lang='en'):
    pois = []
    seen = set()
    for el in elements:
        tags = el.get('tags', {})
        name = tags.get('name', '')
        if not name:
            continue
        nlow = name.lower()
        if nlow in seen:
            continue
        seen.add(nlow)
        if el.get('type') == 'node':
            plat, plon = el.get('lat', 0), el.get('lon', 0)
        else:
            c = el.get('center', {})
            plat = c.get('lat', el.get('lat', 0))
            plon = c.get('lon', el.get('lon', 0))
        if not plat or not plon:
            continue
        dist = _haversine(center_lat, center_lon, plat, plon)
        if max_radius_km and dist > max_radius_km * 1.1:
            continue
        poi_type = _determine_type(tags)
        score = _calculate_score(tags, dist, category)
        pois.append({
            'name': name, 'name_en': tags.get('name:en', name),
            'name_sk': tags.get('name:sk', ''),
            'display_name': _best_display_name(tags, lang),
            'lat': plat, 'lon': plon, 'distance_km': round(dist, 1),
            'type': poi_type, 'category': category, 'score': score,
            'wikipedia': tags.get('wikipedia', ''), 'wikidata': tags.get('wikidata', ''),
            'website': tags.get('website', tags.get('url', '')),
            'description': tags.get('description', ''),
            'opening_hours': tags.get('opening_hours', ''),
            'tags': {k: tags.get(k, '') for k in ['tourism', 'historic', 'natural', 'leisure',
                     'amenity', 'man_made', 'geological', 'waterway', 'route', 'boundary']},
            'is_outdoor': _is_outdoor(tags),
        })
    return pois


def _determine_type(tags):
    if tags.get('route') in ['hiking', 'foot']:
        return 'hiking'
    if tags.get('route') == 'bicycle':
        return 'cycling'
    if tags.get('natural') == 'peak':
        return 'peak'
    if tags.get('tourism') == 'viewpoint':
        return 'viewpoint'
    if tags.get('natural') in ['cave_entrance', 'spring', 'hot_spring', 'arch']:
        return 'nature'
    if tags.get('waterway') == 'waterfall':
        return 'waterfall'
    if tags.get('natural') in ['geyser', 'volcano', 'glacier']:
        return 'volcano'
    if tags.get('natural') == 'beach':
        return 'beach'
    if tags.get('natural') == 'rock' or tags.get('geological'):
        return 'geology'
    if tags.get('leisure') in ['park', 'garden', 'nature_reserve']:
        return 'nature'
    if tags.get('boundary') in ['national_park', 'protected_area']:
        return 'national_park'
    if tags.get('historic') in ['castle', 'palace', 'manor', 'city_gate', 'city_wall']:
        return 'historic'
    if tags.get('historic') in ['ruins', 'archaeological_site', 'aqueduct', 'wreck']:
        return 'archaeology'
    if tags.get('historic') in ['monument', 'memorial', 'mine']:
        return 'historic'
    if tags.get('amenity') in ['monastery', 'place_of_worship'] or tags.get('building') == 'church':
        return 'religious'
    if tags.get('tourism') in ['museum', 'gallery', 'attraction', 'theme_park', 'zoo', 'aquarium']:
        return 'cultural'
    if tags.get('amenity') in ['theatre', 'arts_centre', 'marketplace']:
        return 'cultural'
    if tags.get('man_made') in ['lighthouse', 'windmill', 'tower']:
        return 'historic'
    if tags.get('tourism') == 'wilderness_hut':
        return 'hut'
    return 'cultural'


def _calculate_score(tags, distance_km, category):
    score = 0
    if tags.get('wikipedia'):
        score += 30
    if tags.get('wikidata'):
        score += 20
    score += min(len(tags) * 2, 20)
    if tags.get('website') or tags.get('url'):
        score += 10
    if tags.get('opening_hours'):
        score += 5
    if tags.get('name:en'):
        score += 5
    if distance_km < 5:
        score += 15
    elif distance_km < 15:
        score += 10
    elif distance_km < 30:
        score += 5
    elif distance_km < 60:
        score += 2
    for tk in ['tourism', 'historic', 'natural', 'waterway', 'boundary', 'man_made', 'leisure', 'building']:
        val = tags.get(tk)
        if val:
            score += POI_TYPE_WEIGHTS.get(tk + '=' + val, 0)
    if category == 'mainstream':
        if tags.get('tourism') in ['attraction', 'museum', 'zoo', 'theme_park']:
            score += 10
        if tags.get('boundary') in ['national_park', 'protected_area']:
            score += 15
    if category == 'alternative':
        if tags.get('natural') in ['cave_entrance', 'hot_spring', 'geyser', 'volcano']:
            score += 15
        if tags.get('waterway') in ['waterfall', 'rapids']:
            score += 12
        if tags.get('historic') in ['wayside_shrine', 'boundary_stone']:
            score -= 10
    return score


def _is_outdoor(tags):
    return any([
        tags.get('natural'), tags.get('waterway'), tags.get('geological'),
        tags.get('tourism') == 'viewpoint',
        tags.get('leisure') in ['park', 'garden', 'nature_reserve'],
        tags.get('man_made') in ['lighthouse', 'windmill'],
        tags.get('historic') == 'ruins',
        tags.get('route') in ['hiking', 'foot', 'bicycle'],
        tags.get('boundary') in ['national_park', 'protected_area'],
        tags.get('tourism') == 'wilderness_hut',
    ])


def _haversine(lat1, lon1, lat2, lon2):
    import math
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))
