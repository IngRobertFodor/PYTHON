"""
Wikipedia & Wikidata Service
=============================
Fetches descriptions, images, and official website URLs for POIs.
Uses Wikipedia REST API and Wikidata API.
Both are free, no API key required.
"""

import requests
import urllib.parse

WIKIPEDIA_API = "https://{lang}.wikipedia.org/api/rest_v1"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "FodorTravelTIPs/1.0"


def enrich_poi_with_wikipedia(poi, lang='en'):
    """
    Enrich POI with Wikipedia description and thumbnail.
    Tries the specified language first, falls back to English.
    """
    wikipedia_tag = poi.get('wikipedia', '')
    wikidata_id = poi.get('wikidata', '')
    name = poi.get('name', '')

    # Try to get Wikipedia info
    description = ''
    thumbnail = ''
    wiki_url = ''

    if wikipedia_tag:
        # Format: "en:Article Name" or "sk:Názov článku"
        wiki_lang, wiki_title = _parse_wikipedia_tag(wikipedia_tag)
        desc_data = _get_wikipedia_summary(wiki_title, wiki_lang)
        if desc_data:
            description = desc_data.get('description', '')
            thumbnail = desc_data.get('thumbnail', '')
            wiki_url = desc_data.get('url', '')

    # If no Wikipedia tag, try searching by name
    if not description and name:
        # Try requested language first
        desc_data = _search_wikipedia(name, lang)
        if desc_data:
            description = desc_data.get('description', '')
            thumbnail = desc_data.get('thumbnail', '')
            wiki_url = desc_data.get('url', '')

        # Fallback to English if requested language failed
        if not description and lang != 'en':
            desc_data = _search_wikipedia(name, 'en')
            if desc_data:
                description = desc_data.get('description', '')
                thumbnail = desc_data.get('thumbnail', '')
                wiki_url = desc_data.get('url', '')

    # Get official website from Wikidata
    official_website = ''
    if wikidata_id:
        official_website = _get_official_website(wikidata_id)

    # Update POI
    poi['description'] = description or poi.get('description', '')
    poi['thumbnail'] = thumbnail
    poi['wiki_url'] = wiki_url
    poi['official_website'] = official_website or poi.get('website', '')

    return poi


def _parse_wikipedia_tag(wikipedia_tag):
    """Parse OSM wikipedia tag format 'lang:Title'."""
    if ':' in wikipedia_tag:
        parts = wikipedia_tag.split(':', 1)
        return parts[0], parts[1]
    return 'en', wikipedia_tag


def _get_wikipedia_summary(title, lang='en'):
    """
    Get Wikipedia article summary using REST API.
    Returns description, thumbnail URL, and article URL.
    """
    try:
        encoded_title = urllib.parse.quote(title.replace(' ', '_'))
        url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
        headers = {'User-Agent': USER_AGENT}

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                'description': data.get('extract', '')[:300],
                'thumbnail': data.get('thumbnail', {}).get('source', ''),
                'url': data.get('content_urls', {}).get('desktop', {}).get('page', '')
            }
    except requests.RequestException:
        pass
    return None


def _search_wikipedia(query, lang='en'):
    """
    Search Wikipedia for an article by name.
    Returns summary of first matching article.
    """
    try:
        url = f"https://{lang}.wikipedia.org/w/api.php"
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': query,
            'format': 'json',
            'srlimit': 1,
            'utf8': 1
        }
        headers = {'User-Agent': USER_AGENT}

        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = data.get('query', {}).get('search', [])
            if results:
                title = results[0].get('title', '')
                return _get_wikipedia_summary(title, lang)
    except requests.RequestException:
        pass
    return None


def _get_official_website(wikidata_id):
    """
    Get official website URL from Wikidata (property P856).
    """
    try:
        params = {
            'action': 'wbgetclaims',
            'entity': wikidata_id,
            'property': 'P856',
            'format': 'json'
        }
        headers = {'User-Agent': USER_AGENT}

        response = requests.get(WIKIDATA_API, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            claims = data.get('claims', {}).get('P856', [])
            if claims:
                return claims[0].get('mainsnak', {}).get('datavalue', {}).get('value', '')
    except requests.RequestException:
        pass
    return ''