"""Monitor routes
=================
GET  /api/monitor/status  -> stav monitora (running, next_run, last_result)
POST /api/monitor/scan    -> manualny trigger jedneho skenu
"""

from flask import Blueprint, jsonify
from services.monitor_service import run_scan, get_status
from config_loader import is_feature_enabled

monitor_bp = Blueprint("monitor", __name__)


@monitor_bp.route("/status", methods=["GET"])
def monitor_status():
    """
    Vrati stav monitora.

    Returns:
        200 { running, interval_minutes, next_run_iso, last_result }
    """
    return jsonify(get_status()), 200


@monitor_bp.route("/scan", methods=["POST"])
def trigger_scan():
    """
    Manualny trigger jedneho skenu (bez ohlabu na use_monitoring flag).
    Uzitocne pre testovanie a manualne spustenie.

    Returns:
        200 { scanned, notified, errors, duration_s, timestamp }
        503 ak APScheduler nie je dostupny a scraper tiez zlyha
    """
    try:
        result = run_scan()
        return jsonify(result.to_dict()), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
