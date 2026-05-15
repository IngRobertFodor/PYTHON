"""
POI Routes
==========
Endpoints for Points of Interest discovery.
Uses Overpass API (OpenStreetMap) for POI data.
Accepts category tags filter from frontend checkboxes.
"""

from flask import Blueprint, jsonify, request
from services.overpass_service import get_pois
from services.wikipedia_service import enrich_poi_with_wikipedia
from services.links_service import generate_links

poi_bp = Blueprint('poi', __name__)


@poi_bp.route('/search', methods=['GET'])
def search_pois():
    """
    Search for POIs within a radius of given coordinates.
    Query params:
        lat: latitude of center
        lon: longitude of center
        radius_km: radius in kilometers (1-200)
        lang: language (sk/en)
        tags: comma-separated OSM tags to filter (e.g. "tourism=museum,historic=castle")
    Returns:
        mainstream: list of 10 mainstream POIs
        alternative: list of 10 alternative/unique POIs
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

    # Parse tags filter (from frontend checkboxes)
    custom_tags = None
    if tags_str:
        custom_tags = [t.strip() for t in tags_str.split(',') if t.strip()]

    # Get POIs from Overpass API
    pois = get_pois(lat, lon, radius_km, custom_tags)

    # Separate into mainstream and alternative
    mainstream = pois.get('mainstream', [])[:10]
    alternative = pois.get('alternative', [])[:10]

    # Enrich with Wikipedia data and generate links
    mainstream = [enrich_and_link(poi, lang) for poi in mainstream]
    alternative = [enrich_and_link(poi, lang) for poi in alternative]

    return jsonify({
        'mainstream': mainstream,
        'alternative': alternative,
        'center': {'lat': lat, 'lon': lon},
        'radius_km': radius_km
    })


def enrich_and_link(poi, lang):
    """Enrich a POI with Wikipedia description and generate all links."""
    poi = enrich_poi_with_wikipedia(poi, lang)
    poi['links'] = generate_links(poi, lang)
    return poi