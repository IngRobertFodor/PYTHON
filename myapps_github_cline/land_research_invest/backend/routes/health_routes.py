"""Health routes
===============
GET /api/health  -> stav aplikacie, pocet sluzieb, verzia
"""

from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

SERVICES = [
    "pipeline_service", "scoring_service",   "report_service",
    "cadastral_service", "distance_service",  "flood_service",
    "terrain_service",  "bpej_service",       "overpass_service",
    "protected_service","zbgis_service",       "geocoding_service",
    "price_analysis_service", "notifier_service",
]


@health_bp.route("/health", methods=["GET"])
def health():
    """
    Stav aplikacie.

    Returns:
        200 { status, services_count, services, version }
    """
    return jsonify({
        "status":         "ok",
        "services_count": len(SERVICES),
        "services":       SERVICES,
        "version":        "1.0.0",
    }), 200
