"""
Weather Routes
==============
Endpoints for weather data.
Uses Open-Meteo API (free, no API key required).
"""

from flask import Blueprint, jsonify, request
from services.weather_service import (
    get_weather_for_point,
    get_weather_grid
)

weather_bp = Blueprint('weather', __name__)


@weather_bp.route('/point', methods=['GET'])
def weather_point():
    """
    Get weather forecast for a single point.
    Query params: lat, lon, date (YYYY-MM-DD)
    """
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    date = request.args.get('date', '')

    if lat is None or lon is None:
        return jsonify({'error': 'Parameters "lat" and "lon" are required'}), 400

    result = get_weather_for_point(lat, lon, date)
    return jsonify(result)


@weather_bp.route('/grid', methods=['GET'])
def weather_grid():
    """
    Get weather for multiple points in an area (grid).
    Used for weather visualization across the travel area.
    Query params: lat, lon, radius_km, date (YYYY-MM-DD)
    """
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    radius_km = request.args.get('radius_km', 25, type=float)
    date = request.args.get('date', '')

    if lat is None or lon is None:
        return jsonify({'error': 'Parameters "lat" and "lon" are required'}), 400

    result = get_weather_grid(lat, lon, radius_km, date)
    return jsonify(result)