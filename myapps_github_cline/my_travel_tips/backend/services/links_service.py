"""Links Service - Generates 5 relevant links for each POI based on its type."""
import urllib.parse


def generate_links(poi, lang='en'):
    """Generate 5 links for a POI based on its type."""
    links = []
    name = poi.get('name', '') or ''
    name_en = poi.get('name_en', name) or name
    lat = poi.get('lat', 0)
    lon = poi.get('lon', 0)
    poi_type = poi.get('type', 'cultural')
    source = poi.get('source', '')
    link_config = _get_link_config(poi_type, source)
    for link_def in link_config:
        link = _build_link(link_def, poi, name, name_en, lat, lon, lang)
        if link:
            links.append(link)
    while len(links) < 5:
        if not any(l['type'] == 'google_maps' for l in links):
            links.append(_make_google_maps_link(lat, lon))
        elif not any(l['type'] == 'wikipedia' for l in links):
            links.append(_make_wikipedia_link(name, name_en, poi, lang))
        else:
            links.append(_make_tripadvisor_link(name_en))
        if len(links) >= 5:
            break
    return links[:5]


def _get_link_config(poi_type, source=''):
    """Get link config for POI type."""
    if source == 'atlas_obscura':
        return ['atlas_obscura_direct', 'wikipedia', 'google_maps', 'reddit_travel', 'inaturalist']
    configs = {
        'hiking': ['wikiloc', 'alltrails', 'komoot', 'wikipedia', 'google_maps'],
        'cycling': ['komoot', 'alltrails', 'strava', 'wikipedia', 'google_maps'],
        'historic': ['official', 'wikipedia', 'google_maps', 'tripadvisor', 'atlas_obscura'],
        'cultural': ['official', 'wikipedia', 'google_arts_culture', 'tripadvisor', 'google_maps'],
        'waterfall': ['alltrails', 'wikipedia', 'google_maps', 'inaturalist', 'wikiloc'],
        'nature': ['alltrails', 'wikipedia', 'google_maps', 'inaturalist', 'komoot'],
        'national_park': ['official', 'wikipedia', 'google_maps', 'alltrails', 'komoot'],
        'peak': ['alltrails', 'wikiloc', 'google_maps', 'wikipedia', 'peakvisor'],
        'viewpoint': ['alltrails', 'wikiloc', 'google_maps', 'wikipedia', 'peakvisor'],
        'volcano': ['wikipedia', 'google_maps', 'alltrails', 'inaturalist', 'atlas_obscura'],
        'geology': ['inaturalist', 'wikipedia', 'google_maps', 'atlas_obscura', 'alltrails'],
        'beach': ['wikipedia', 'google_maps', 'windy', 'tripadvisor', 'inaturalist'],
        'archaeology': ['wikipedia', 'google_maps', 'wikivoyage', 'atlas_obscura', 'tripadvisor'],
        'religious': ['official', 'wikipedia', 'google_maps', 'atlas_obscura', 'tripadvisor'],
        'hut': ['komoot', 'alltrails', 'wikiloc', 'wikipedia', 'google_maps'],
    }
    return configs.get(poi_type, configs['cultural'])


def _build_link(link_type, poi, name, name_en, lat, lon, lang):
    """Build a single link."""
    builders = {
        'official': lambda: _make_official_link(poi, lang),
        'wikipedia': lambda: _make_wikipedia_link(name, name_en, poi, lang),
        'google_maps': lambda: _make_google_maps_link(lat, lon),
        'alltrails': lambda: _make_alltrails_link(name_en),
        'wikiloc': lambda: _make_wikiloc_link(name_en, lat, lon),
        'komoot': lambda: _make_komoot_link(name_en, lat, lon),
        'strava': lambda: _make_strava_link(name_en, lat, lon),
        'tripadvisor': lambda: _make_tripadvisor_link(name_en),
        'wikivoyage': lambda: _make_wikivoyage_link(name_en, lang),
        'inaturalist': lambda: _make_inaturalist_link(lat, lon),
        'atlas_obscura': lambda: _make_atlas_obscura_search_link(name_en),
        'atlas_obscura_direct': lambda: _make_atlas_obscura_direct_link(poi),
        'reddit_travel': lambda: _make_reddit_link(name_en, 'travel'),
        'reddit_hiking': lambda: _make_reddit_link(name_en, 'hiking'),
        'google_arts_culture': lambda: _make_google_arts_culture_link(name_en),
        'peakvisor': lambda: _make_peakvisor_link(name_en, lat, lon),
        'windy': lambda: _make_windy_link(lat, lon),
    }
    builder = builders.get(link_type)
    return builder() if builder else None


def _make_official_link(poi, lang):
    url = poi.get('official_website', '') or poi.get('website', '')
    if url:
        return {'type': 'official', 'icon': '\U0001f310',
                'label': 'Oficialny web' if lang == 'sk' else 'Official Website', 'url': url}
    return _make_tripadvisor_link(poi.get('name_en', poi.get('name', '')))


def _make_wikipedia_link(name, name_en, poi, lang):
    wiki_url = poi.get('wiki_url', '')
    if wiki_url:
        return {'type': 'wikipedia', 'icon': '\U0001f4d6', 'label': 'Wikipedia', 'url': wiki_url}
    wl = 'sk' if lang == 'sk' else 'en'
    sn = name if lang == 'sk' and name else name_en
    ws = urllib.parse.quote(sn) if sn else ''
    return {'type': 'wikipedia', 'icon': '\U0001f4d6', 'label': 'Wikipedia',
            'url': 'https://' + wl + '.wikipedia.org/wiki/Special:Search/' + ws}


def _make_google_maps_link(lat, lon):
    return {'type': 'google_maps', 'icon': '\U0001f5fa\ufe0f', 'label': 'Google Maps',
            'url': 'https://www.google.com/maps/search/?api=1&query=' + str(lat) + ',' + str(lon)}


def _make_alltrails_link(name):
    e = urllib.parse.quote(name) if name else ''
    return {'type': 'alltrails', 'icon': '\U0001f97e', 'label': 'AllTrails',
            'url': 'https://www.alltrails.com/search?q=' + e}


def _make_wikiloc_link(name, lat, lon):
    e = urllib.parse.quote(name) if name else ''
    return {'type': 'wikiloc', 'icon': '\U0001f5fa\ufe0f', 'label': 'Wikiloc',
            'url': 'https://www.wikiloc.com/trails/search?q=' + e + '&lat=' + str(lat) + '&lng=' + str(lon)}


def _make_komoot_link(name, lat, lon):
    e = urllib.parse.quote(name) if name else ''
    return {'type': 'komoot', 'icon': '\U0001f6b4', 'label': 'Komoot',
            'url': 'https://www.komoot.com/discover?lat=' + str(lat) + '&lng=' + str(lon) + '&query=' + e}


def _make_strava_link(name, lat, lon):
    e = urllib.parse.quote(name) if name else ''
    return {'type': 'strava', 'icon': '\U0001f3c3', 'label': 'Strava Routes',
            'url': 'https://www.strava.com/local?lat=' + str(lat) + '&lng=' + str(lon) + '&query=' + e}


def _make_tripadvisor_link(name):
    e = urllib.parse.quote(name) if name else ''
    return {'type': 'tripadvisor', 'icon': '\u2b50', 'label': 'TripAdvisor',
            'url': 'https://www.tripadvisor.com/Search?q=' + e}


def _make_wikivoyage_link(name, lang='en'):
    wl = 'sk' if lang == 'sk' else 'en'
    e = urllib.parse.quote(name) if name else ''
    return {'type': 'wikivoyage', 'icon': '\U0001f4da', 'label': 'Wikivoyage',
            'url': 'https://' + wl + '.wikivoyage.org/wiki/Special:Search/' + e}


def _make_inaturalist_link(lat, lon):
    return {'type': 'inaturalist', 'icon': '\U0001f33f', 'label': 'iNaturalist',
            'url': 'https://www.inaturalist.org/observations?lat=' + str(lat) + '&lng=' + str(lon) + '&radius=10'}


def _make_atlas_obscura_search_link(name):
    e = urllib.parse.quote(name) if name else ''
    return {'type': 'atlas_obscura', 'icon': '\U0001f48e', 'label': 'Atlas Obscura',
            'url': 'https://www.atlasobscura.com/search?q=' + e}


def _make_atlas_obscura_direct_link(poi):
    ao_url = poi.get('atlas_obscura_url', '')
    if ao_url:
        return {'type': 'atlas_obscura', 'icon': '\U0001f48e', 'label': 'Atlas Obscura', 'url': ao_url}
    return _make_atlas_obscura_search_link(poi.get('name_en', poi.get('name', '')))


def _make_reddit_link(name, subreddit='travel'):
    e = urllib.parse.quote(name) if name else ''
    return {'type': 'reddit', 'icon': '\U0001f4ac', 'label': 'Reddit r/' + subreddit,
            'url': 'https://www.reddit.com/r/' + subreddit + '/search/?q=' + e + '&restrict_sr=1'}


def _make_google_arts_culture_link(name):
    e = urllib.parse.quote(name) if name else ''
    return {'type': 'google_arts_culture', 'icon': '\U0001f3a8', 'label': 'Google Arts & Culture',
            'url': 'https://artsandculture.google.com/search?q=' + e}


def _make_peakvisor_link(name, lat, lon):
    e = urllib.parse.quote(name) if name else ''
    return {'type': 'peakvisor', 'icon': '\U0001f3d4\ufe0f', 'label': 'PeakVisor',
            'url': 'https://peakvisor.com/?lat=' + str(lat) + '&lng=' + str(lon) + '&name=' + e}


def _make_windy_link(lat, lon):
    return {'type': 'windy', 'icon': '\U0001f30a', 'label': 'Windy.com',
            'url': 'https://www.windy.com/?' + str(lat) + ',' + str(lon) + ',12'}


def _t(sk_text, en_text, lang):
    """Simple translation helper."""
    return sk_text if lang == 'sk' else en_text