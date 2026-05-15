"""
Links Service
=============
Generates 5 relevant links for each POI:
- 3 mandatory: Official Website, Wikipedia, Google Maps
- 2 contextual based on POI type: AllTrails/Reddit/Wikivoyage/iNaturalist
"""

import urllib.parse


def generate_links(poi, lang='en'):
    """
    Generate 5 links for a POI based on its type.
    
    Mandatory (always 3):
        1. Official Website (from Wikidata P856, or skip if not available)
        2. Wikipedia (SK preference, EN fallback)
        3. Google Maps (generated from coordinates)
    
    Contextual (2 based on POI type):
        nature/outdoor → AllTrails + Reddit
        historic/cultural → Wikivoyage + Reddit
        urban/city → Wikivoyage + Reddit
        nature/fauna/flora → iNaturalist + AllTrails
        caves/geology → iNaturalist + Reddit
        religious → Wikivoyage + Reddit
    """
    links = []
    name = poi.get('name', '')
    name_en = poi.get('name_en', name)
    lat = poi.get('lat', 0)
    lon = poi.get('lon', 0)
    poi_type = poi.get('type', 'cultural')

    # === MANDATORY LINKS ===

    # 1. Official Website
    official_url = poi.get('official_website', '')
    if official_url:
        links.append({
            'type': 'official',
            'icon': '🌐',
            'label': _t('Oficiálny web', 'Official Website', lang),
            'url': official_url
        })

    # 2. Wikipedia
    wiki_url = poi.get('wiki_url', '')
    if wiki_url:
        links.append({
            'type': 'wikipedia',
            'icon': '📖',
            'label': 'Wikipedia',
            'url': wiki_url
        })
    else:
        # Generate Wikipedia search link
        wiki_lang = 'sk' if lang == 'sk' else 'en'
        wiki_search = urllib.parse.quote(name)
        links.append({
            'type': 'wikipedia',
            'icon': '📖',
            'label': 'Wikipedia',
            'url': f'https://{wiki_lang}.wikipedia.org/wiki/Special:Search/{wiki_search}'
        })

    # 3. Google Maps
    gmaps_url = f'https://www.google.com/maps/search/?api=1&query={lat},{lon}'
    links.append({
        'type': 'google_maps',
        'icon': '🗺️',
        'label': 'Google Maps',
        'url': gmaps_url
    })

    # === CONTEXTUAL LINKS (2 based on type) ===
    contextual = _get_contextual_links(poi_type, name, name_en, lat, lon, lang)
    links.extend(contextual)

    # Ensure we always have exactly 5 links (fill with Reddit if needed)
    while len(links) < 5:
        reddit_url = _build_reddit_link(name_en, 'travel')
        links.append({
            'type': 'reddit',
            'icon': '💬',
            'label': 'Reddit',
            'url': reddit_url
        })
        break  # Avoid infinite loop

    return links[:5]


def _get_contextual_links(poi_type, name, name_en, lat, lon, lang):
    """Get 2 contextual links based on POI type."""
    links = []

    if poi_type == 'nature':
        # Outdoor / Nature / Hiking → AllTrails + Reddit r/hiking
        links.append({
            'type': 'alltrails',
            'icon': '🥾',
            'label': 'AllTrails',
            'url': _build_alltrails_link(name_en, lat, lon)
        })
        links.append({
            'type': 'reddit',
            'icon': '💬',
            'label': 'Reddit r/hiking',
            'url': _build_reddit_link(name_en, 'hiking')
        })

    elif poi_type == 'historic':
        # Historic / Cultural / Monuments → Wikivoyage + Reddit r/travel
        links.append({
            'type': 'wikivoyage',
            'icon': '📚',
            'label': 'Wikivoyage',
            'url': _build_wikivoyage_link(name_en, lang)
        })
        links.append({
            'type': 'reddit',
            'icon': '💬',
            'label': 'Reddit r/travel',
            'url': _build_reddit_link(name_en, 'travel')
        })

    elif poi_type == 'religious':
        # Religious / Spiritual → Wikivoyage + Reddit r/travel
        links.append({
            'type': 'wikivoyage',
            'icon': '📚',
            'label': 'Wikivoyage',
            'url': _build_wikivoyage_link(name_en, lang)
        })
        links.append({
            'type': 'reddit',
            'icon': '💬',
            'label': 'Reddit r/travel',
            'url': _build_reddit_link(name_en, 'travel')
        })

    elif poi_type == 'geology':
        # Caves / Geology / Unique formations → iNaturalist + Reddit
        links.append({
            'type': 'inaturalist',
            'icon': '🌿',
            'label': 'iNaturalist',
            'url': _build_inaturalist_link(lat, lon)
        })
        links.append({
            'type': 'reddit',
            'icon': '💬',
            'label': 'Reddit r/travel',
            'url': _build_reddit_link(name_en, 'travel')
        })

    else:
        # Cultural / Default → Wikivoyage + Reddit r/travel
        links.append({
            'type': 'wikivoyage',
            'icon': '📚',
            'label': 'Wikivoyage',
            'url': _build_wikivoyage_link(name_en, lang)
        })
        links.append({
            'type': 'reddit',
            'icon': '💬',
            'label': 'Reddit r/travel',
            'url': _build_reddit_link(name_en, 'travel')
        })

    return links


def _build_alltrails_link(name, lat, lon):
    """Build AllTrails search/explore link."""
    encoded = urllib.parse.quote(name)
    return f'https://www.alltrails.com/search?q={encoded}'


def _build_reddit_link(name, subreddit='travel'):
    """Build Reddit search link within a subreddit."""
    encoded = urllib.parse.quote(name)
    return f'https://www.reddit.com/r/{subreddit}/search/?q={encoded}&restrict_sr=1'


def _build_wikivoyage_link(name, lang='en'):
    """Build Wikivoyage search link."""
    wiki_lang = 'sk' if lang == 'sk' else 'en'
    encoded = urllib.parse.quote(name)
    return f'https://{wiki_lang}.wikivoyage.org/wiki/Special:Search/{encoded}'


def _build_inaturalist_link(lat, lon):
    """Build iNaturalist observations link for location."""
    return f'https://www.inaturalist.org/observations?lat={lat}&lng={lon}&radius=10'


def _t(sk_text, en_text, lang):
    """Simple translation helper."""
    return sk_text if lang == 'sk' else en_text