"""
Fodor Travel TIPs - Main Flask Application
============================================
A travel points-of-interest discovery app with weather integration.
"""

import sys
import os

# Add backend directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

from routes.poi import poi_bp
from routes.weather import weather_bp
from routes.geocoding import geocoding_bp

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Register blueprints
app.register_blueprint(poi_bp, url_prefix='/api/poi')
app.register_blueprint(weather_bp, url_prefix='/api/weather')
app.register_blueprint(geocoding_bp, url_prefix='/api/geocoding')


@app.route('/')
def serve_frontend():
    """Serve the main frontend page."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory(app.static_folder, path)


@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'app': 'Fodor Travel TIPs'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)