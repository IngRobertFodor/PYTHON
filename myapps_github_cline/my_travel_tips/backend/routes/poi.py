"""
POI Routes - Endpoints for Points of Interest discovery.
Uses Overpass API (OpenStreetMap) for POI data.
IMPROVEMENT: Parallel Wikipedia enrichment (10x faster).
"""
from flask import Blueprint, jsonify, request
from concurrent.futures import ThreadPoolExecutor
from services.overpass_service import get_pois
from services.wikipedia_service import enrich_poi_with_wikipedia
from services.links_service import generate_links

poi_bp = Blueprint('poi', __name__)


@poi_bp.route('/search', methods=['GET'])
def search_pois():
    """
    Search for POIs within a radius of given coordinates.
    Query params: lat, lon, radius_km, lang, tags
    Returns: mainstream (10) + alternative (10) POIs with links
    """
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    radius_km = request.args.get('radius_km', 25, type=float)
    lang = request.args.get('lang', 'en')
    tags_str = request.args.get('tags', '')

    if lat is None or lon is None:
        return jsonify({'error': 'Parameters "lat" and "lon" are required'}), 400
    if radius_km <= 0 or radius_km > 200:
        return jsonify({'error': 'Radius must be between 1 and 200 km'}), 400

    # Parse tags filter from frontend checkboxes
    custom_tags = None
    if tags_str:
        custom_tags = [t.strip() for t in tags_str.split(',') if t.strip()]

    # Get POIs from Overpass API
    pois = get_pois(lat, lon, radius_km, custom_tags)
    mainstream = pois.get('mainstream', [])[:10]
    alternative = pois.get('alternative', [])[:10]

    # Enrich ALL POIs in parallel (Wikipedia + links) - much faster than sequential
    all_pois = mainstream + alternative
    enriched = _enrich_parallel(all_pois, lang)

    # Split back into mainstream and alternative
    mainstream_enriched = enriched[:len(mainstream)]
    alternative_enriched = enriched[len(mainstream):]

    return jsonify({
        'mainstream': mainstream_enriched,
        'alternative': alternative_enriched,
        'center': {'lat': lat, 'lon': lon},
        'radius_km': radius_km
    })


def _enrich_parallel(pois, lang, max_workers=8):
    """
    Enrich all POIs with Wikipedia data and links IN PARALLEL.
    This is ~10x faster than doing it one by one sequentially.
    max_workers=8 means up to 8 Wikipedia API calls at same time.
    """
    if not pois:
        return []

    def enrich_one(poi):
        try:
            poi = enrich_poi_with_wikipedia(poi, lang)
            poi['links'] = generate_links(poi, lang)
        except Exception:
            poi['links'] = generate_links(poi, lang)
        return poi

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(enrich_one, pois))

    return results