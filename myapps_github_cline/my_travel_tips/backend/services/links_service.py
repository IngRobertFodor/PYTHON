"""
Links Service
=============
Generates 5 relevant links for each POI based on its type.
Each link is precisely targeted to the POI category for maximum usefulness.

Supports 15 POI type-specific link configurations.
Sources: Wikiloc, Komoot, Strava, TripAdvisor, Atlas Obscura, AllTrails, iNaturalist, Wikivoyage, Reddit.
"""

import urllib.parse


def generate_links(poi, lang='en'):
    """
    Generate 5 links for a POI based on its type.
    Links are precisely targeted to the POI category.

    Returns list of 5 link dicts with: type, icon, label, url
    """
    links = []
    name = poi.get('name', '') or ''
    name_en = poi.get('name_en', name) or name
    lat = poi.get('lat', 0)
    lon = poi.get('lon', 0)
    poi_type = poi.get('type', 'cultural')
    source = poi.get('source', '')

    # Get type-specific link configuration
    link_config = _get_link_config(poi_type, source)

    for link_def in link_config:
        link = _build_link(link_def, poi, name, name_en, lat, lon, lang)
        if link:
            links.append(link)

    # Ensure we always have exactly 5 links
    while len(links) < 5:
        # Fill with Google Maps if missing
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
    """
    Get link configuration for a specific POI type.
    Returns ordered list of 5 link definitions.
    """
    # Atlas Obscura sourced POI - direct link priority
    if source == 'atlas_obscura':
        return ['atlas_obscura_direct', 'wikipedia', 'google_maps', 'reddit_travel', 'inaturalist']

    configs = {
        'hiking': ['wikiloc', 'alltrails', 'komoot', 'wikipedia', 'google_maps'],
        'cycling': ['komoot', 'alltrails', 'strava', 'wikipedia', 'google_maps'],
        'historic': ['official', 'wikipedia', 'google_maps', 'tripadvisor', 'wikivoyage'],
        'cultural': ['official', 'wikipedia', 'google_maps', 'tripadvisor', 'wikivoyage'],
        'waterfall': ['alltrails', 'wikipedia', 'google_maps', 'inaturalist', 'wikiloc'],
        'nature': ['alltrails', 'wikipedia', 'google_maps', 'inaturalist', 'komoot'],
        'national_park': ['official', 'wikipedia', 'google_maps', 'alltrails', 'komoot'],
        'peak': ['alltrails', 'wikiloc', 'google_maps', 'wikipedia', 'komoot'],
        'viewpoint': ['alltrails', 'wikiloc', 'google_maps', 'wikipedia', 'komoot'],
        'volcano': ['wikipedia', 'google_maps', 'alltrails', 'inaturalist', 'atlas_obscura'],
        'geology': ['inaturalist', 'wikipedia', 'google_maps', 'atlas_obscura', 'alltrails'],
        'beach': ['wikipedia', 'google_maps', 'alltrails', 'tripadvisor', 'inaturalist'],
        'archaeology': ['wikipedia', 'google_maps', 'wikivoyage', 'atlas_obscura', 'tripadvisor'],
        'religious': ['official', 'wikipedia', 'google_maps', 'wikivoyage', 'tripadvisor'],
        'hut': ['komoot', 'alltrails', 'wikiloc', 'wikipedia', 'google_maps'],
    }

    return configs.get(poi_type, configs['cultural'])


def _build_link(link_type, poi, name, name_en, lat, lon, lang):
    """Build a single link based on its type definition."""
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
    }

    builder = builders.get(link_type)
    if builder:
        return builder()
    return None


# === LINK BUILDERS ===

def _make_official_link(poi, lang):
    """Official website link (from Wikidata or OSM)."""
    url = poi.get('official_website', '') or poi.get('website', '')
    if url:
        return {
            'type': 'official',
            'icon': '🌐',
            'label': _t('Oficiálny web', 'Official Website', lang),
            'url': url
        }
    # Fallback to TripAdvisor search if no official website
    name_en = poi.get('name_en', poi.get('name', ''))
    return _make_tripadvisor_link(name_en)


def _make_wikipedia_link(name, name_en, poi, lang):
    """Wikipedia link - direct or search."""
    wiki_url = poi.get('wiki_url', '')
    if wiki_url:
        return {
            'type': 'wikipedia',
            'icon': '📖',
            'label': 'Wikipedia',
            'url': wiki_url
        }
    # Generate Wikipedia search link
    wiki_lang = 'sk' if lang == 'sk' else 'en'
    search_name = name if lang == 'sk' and name else name_en
    wiki_search = urllib.parse.quote(search_name) if search_name else ''
    return {
        'type': 'wikipedia',
        'icon': '📖',
        'label': 'Wikipedia',
        'url': f'https://{wiki_lang}.wikipedia.org/wiki/Special:Search/{wiki_search}'
    }


def _make_google_maps_link(lat, lon):
    """Google Maps link from coordinates."""
    return {
        'type': 'google_maps',
        'icon': '🗺️',
        'label': 'Google Maps',
        'url': f'https://www.google.com/maps/search/?api=1&query={lat},{lon}'
    }


def _make_alltrails_link(name):
    """AllTrails search link."""
    encoded = urllib.parse.quote(name) if name else ''
    return {
        'type': 'alltrails',
        'icon': '🥾',
        'label': 'AllTrails',
        'url': f'https://www.alltrails.com/search?q={encoded}'
    }


def _make_wikiloc_link(name, lat, lon):
    """Wikiloc trail search link."""
    encoded = urllib.parse.quote(name) if name else ''
    return {
        'type': 'wikiloc',
        'icon': '🗺️',
        'label': 'Wikiloc',
        'url': f'https://www.wikiloc.com/trails/search?q={encoded}&lat={lat}&lng={lon}'
    }


def _make_komoot_link(name, lat, lon):
    """Komoot search link."""
    encoded = urllib.parse.quote(name) if name else ''
    return {
        'type': 'komoot',
        'icon': '🚴',
        'label': 'Komoot',
        'url': f'https://www.komoot.com/discover?lat={lat}&lng={lon}&query={encoded}'
    }


def _make_strava_link(name, lat, lon):
    """Strava routes search link."""
    encoded = urllib.parse.quote(name) if name else ''
    return {
        'type': 'strava',
        'icon': '🏃',
        'label': 'Strava Routes',
        'url': f'https://www.strava.com/local?lat={lat}&lng={lon}&query={encoded}'
    }


def _make_tripadvisor_link(name):
    """TripAdvisor search link."""
    encoded = urllib.parse.quote(name) if name else ''
    return {
        'type': 'tripadvisor',
        'icon': '⭐',
        'label': 'TripAdvisor',
        'url': f'https://www.tripadvisor.com/Search?q={encoded}'
    }


def _make_wikivoyage_link(name, lang='en'):
    """Wikivoyage search link."""
    wiki_lang = 'sk' if lang == 'sk' else 'en'
    encoded = urllib.parse.quote(name) if name else ''
    return {
        'type': 'wikivoyage',
        'icon': '📚',
        'label': 'Wikivoyage',
        'url': f'https://{wiki_lang}.wikivoyage.org/wiki/Special:Search/{encoded}'
    }


def _make_inaturalist_link(lat, lon):
    """iNaturalist observations link for location."""
    return {
        'type': 'inaturalist',
        'icon': '🌿',
        'label': 'iNaturalist',
        'url': f'https://www.inaturalist.org/observations?lat={lat}&lng={lon}&radius=10'
    }


def _make_atlas_obscura_search_link(name):
    """Atlas Obscura search link."""
    encoded = urllib.parse.quote(name) if name else ''
    return {
        'type': 'atlas_obscura',
        'icon': '💎',
        'label': 'Atlas Obscura',
        'url': f'https://www.atlasobscura.com/search?q={encoded}'
    }


def _make_atlas_obscura_direct_link(poi):
    """Atlas Obscura direct link (for POIs sourced from Atlas Obscura)."""
    ao_url = poi.get('atlas_obscura_url', '')
    if ao_url:
        return {
            'type': 'atlas_obscura',
            'icon': '💎',
            'label': 'Atlas Obscura',
            'url': ao_url
        }
    # Fallback to search
    name = poi.get('name_en', poi.get('name', ''))
    return _make_atlas_obscura_search_link(name)


def _make_reddit_link(name, subreddit='travel'):
    """Reddit search link within a subreddit."""
    encoded = urllib.parse.quote(name) if name else ''
    return {
        'type': 'reddit',
        'icon': '💬',
        'label': f'Reddit r/{subreddit}',
        'url': f'https://www.reddit.com/r/{subreddit}/search/?q={encoded}&restrict_sr=1'
    }


def _t(sk_text, en_text, lang):
    """Simple translation helper."""
    return sk_text if lang == 'sk' else en_text
