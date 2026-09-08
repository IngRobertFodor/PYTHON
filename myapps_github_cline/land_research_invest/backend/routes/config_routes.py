"""Config routes
===============
GET /api/config           -> aktualne kriteria, vahy, prahy (read-only)
GET /api/config/validate  -> overenie criteria.yaml, vrati zoznam chyb
"""

from flask import Blueprint, jsonify
from config_loader    import get_scoring, get_criteria, get_features, get_notifications
from config_validator import validate_config

config_bp = Blueprint("config", __name__)


@config_bp.route("/", methods=["GET"])
def get_config_endpoint():
    """
    Aktualne nastavenia (read-only pre UI / frontend).

    Returns:
        200 { scoring: {weights, thresholds}, criteria: {...}, features: {...}, notifications: {...} }
    """
    return jsonify({
        "scoring":       get_scoring(),
        "criteria":      get_criteria(),
        "features":      get_features(),
        "notifications": get_notifications(),
    }), 200


@config_bp.route("/validate", methods=["GET"])
def validate_config_endpoint():
    """
    Overi criteria.yaml a vrati zoznam chyb.

    Returns:
        200 { valid: true,  errors: [] }      ak je config OK
        200 { valid: false, errors: [...] }   ak su chyby
    """
    errors = validate_config()
    return jsonify({
        "valid":  len(errors) == 0,
        "errors": errors,
    }), 200
