"""
Geocoding Routes
================
Endpoints for geocoding (place name → coordinates) and reverse geocoding.
Uses Nominatim (OpenStreetMap) API.
"""

from flask import Blueprint, jsonify, request
from services.geocoding_service import (
    geocode_place,
    reverse_geocode,
    calculate_travel_radius
)

geocoding_bp = Blueprint('geocoding', __name__)


@geocoding_bp.route('/search', methods=['GET'])
def search_place():
    """
    Search for a place by name and return coordinates.
    Query params: q (place name), lang (sk/en)
    """
    query = request.args.get('q', '').strip()
    lang = request.args.get('lang', 'en')

    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400

    results = geocode_place(query, lang)
    return jsonify(results)


@geocoding_bp.route('/reverse', methods=['GET'])
def reverse():
    """
    Reverse geocode coordinates to place name.
    Query params: lat, lon, lang (sk/en)
    """
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    lang = request.args.get('lang', 'en')

    if lat is None or lon is None:
        return jsonify({'error': 'Parameters "lat" and "lon" are required'}), 400

    result = reverse_geocode(lat, lon, lang)
    return jsonify(result)


@geocoding_bp.route('/travel-radius', methods=['GET'])
def travel_radius():
    """
    Calculate radius in km from travel time.
    Query params: lat, lon, time_minutes, mode (car/walk/bike)
    """
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    time_minutes = request.args.get('time_minutes', type=int)
    mode = request.args.get('mode', 'car')

    if lat is None or lon is None or time_minutes is None:
        return jsonify({'error': 'Parameters "lat", "lon", and "time_minutes" are required'}), 400

    result = calculate_travel_radius(lat, lon, time_minutes, mode)
    return jsonify(result)