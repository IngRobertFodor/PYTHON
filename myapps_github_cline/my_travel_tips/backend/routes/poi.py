"""
POI Routes - Endpoints for Points of Interest discovery.
Uses Overpass API (OpenStreetMap) for POI data.
IMPROVEMENT: Parallel Wikipedia enrichment (10x faster).
DIAG v2.2: Returns _meta diagnostics in response body.
v2.4: In-memory TTL cache + /cache/clear endpoint.
"""
import time
from flask import Blueprint, jsonify, request
from concurrent.futures import ThreadPoolExecutor
from services.overpass_service import get_pois
from services.wikipedia_service import enrich_poi_with_wikipedia
from services.links_service import generate_links
from services.cache_service import poi_cache, make_poi_cache_key

poi_bp = Blueprint('poi', __name__)


@poi_bp.route('/search', methods=['GET'])
def search_pois():
    """
    Search for POIs within a radius of given coordinates.
    Query params: lat, lon, radius_km, lang, tags
    Returns: mainstream (10) + alternative (10) POIs with links + _meta diagnostics
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

    print(f"[ROUTE] /api/poi/search | lat={lat} lon={lon} radius={radius_km}km lang={lang} tags={tags_str[:80]}")

    # Parse tags filter from frontend checkboxes
    custom_tags = None
    if tags_str:
        custom_tags = [t.strip() for t in tags_str.split(',') if t.strip()]

    # ── Cache lookup ──────────────────────────────────────────────────────────
    cache_key = make_poi_cache_key(lat, lon, radius_km, custom_tags, lang)
    cached = poi_cache.get(cache_key)
    if cached is not None:
        print(f"[CACHE] ✓ HIT | key=({round(lat,2)},{round(lon,2)},{int(radius_km)}) | "
              f"cache size={poi_cache.stats()['valid']}")
        response = dict(cached)
        response['_meta'] = dict(response.get('_meta', {}))
        response['_meta']['from_cache'] = True
        return jsonify(response)
    print(f"[CACHE] ✗ MISS | fetching from Overpass...")
    # ─────────────────────────────────────────────────────────────────────────

    # Get POIs from Overpass API
    t0 = time.time()
    pois = get_pois(lat, lon, radius_km, custom_tags, lang)
    overpass_time_ms = int((time.time() - t0) * 1000)

    mainstream = pois.get('mainstream', [])[:10]
    alternative = pois.get('alternative', [])[:10]
    meta = pois.get('_meta', {})
    meta['overpass_time_ms'] = overpass_time_ms
    meta['lat'] = lat
    meta['lon'] = lon
    meta['tags_received'] = len(custom_tags) if custom_tags else 0
    meta['from_cache'] = False

    print(f"[ROUTE] Overpass done in {overpass_time_ms}ms | mainstream={len(mainstream)} alternative={len(alternative)}")

    # Build warning message when no results
    warning = None
    if not mainstream and not alternative:
        raw = meta.get('raw_elements', 0)
        if raw == 0:
            warning = ("Overpass API nevrátilo žiadne dáta (server bol pravdepodobne preťažený). "
                       "Skúste znova o chvíľu, alebo zväčšite okruh hľadania."
                       if lang == 'sk' else
                       "Overpass API returned no data (server may be overloaded). "
                       "Please try again in a moment, or increase the search radius.")
        else:
            warning = (f"Overpass vrátil {raw} elementov, ale žiadne nevyhovelo filtrám. "
                       "Skúste iné kategórie alebo väčší okruh."
                       if lang == 'sk' else
                       f"Overpass returned {raw} elements, but none passed the filters. "
                       "Try different categories or a larger radius.")
        print(f"[ROUTE] WARNING: {warning}")
    meta['warning'] = warning

    # Enrich ALL POIs in parallel (Wikipedia + links) - much faster than sequential
    all_pois = mainstream + alternative
    enriched = _enrich_parallel(all_pois, lang)

    # Split back into mainstream and alternative
    mainstream_enriched = enriched[:len(mainstream)]
    alternative_enriched = enriched[len(mainstream):]

    response_data = {
        'mainstream': mainstream_enriched,
        'alternative': alternative_enriched,
        'center': {'lat': lat, 'lon': lon},
        'radius_km': radius_km,
        '_meta': meta
    }

    # Store in cache only when we got actual results
    if mainstream_enriched or alternative_enriched:
        poi_cache.set(cache_key, response_data)
        print(f"[CACHE] Stored | cache size now={poi_cache.stats()['valid']}")

    return jsonify(response_data)


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


@poi_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear the in-memory POI cache. Useful during development/testing."""
    stats_before = poi_cache.stats()
    poi_cache.clear()
    print(f"[CACHE] Cleared (had {stats_before['valid']} valid entries)")
    return jsonify({'status': 'cleared', 'entries_removed': stats_before['valid']})


@poi_bp.route('/cache/stats', methods=['GET'])
def cache_stats():
    """Return current cache statistics."""
    return jsonify(poi_cache.stats())
