"""
Backup routes
=============
GET  /api/backup/status   -> stav zálohy + DB info
GET  /api/backup/export   -> stiahni parcels_latest.sql.gz
POST /api/backup/import   -> upload .sql.gz, merge do DB
GET  /api/backup/history  -> zoznam archívnych záloh
"""

from flask import Blueprint, jsonify, request, Response, send_file
from services.backup_service import (
    backup_status, list_history,
    export_db, import_db,
    _LATEST_FILE,
)

backup_bp = Blueprint("backup", __name__)

_IMPORT_RATE_LOCK_TS = [0.0]   # [last_call_time]


@backup_bp.route("/status", methods=["GET"])
def get_backup_status():
    """Vráti info o zálohe a DB (veľkosť, počty, dátum poslednej zálohy)."""
    try:
        return jsonify(backup_status()), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@backup_bp.route("/export", methods=["GET"])
def get_backup_export():
    """Stiahne parcels_latest.sql.gz. Ak neexistuje, vytvorí ho."""
    try:
        path = export_db()
        return send_file(
            str(path),
            mimetype="application/gzip",
            as_attachment=True,
            download_name="parcels_latest.sql.gz",
        )
    except Exception as exc:
        return jsonify({"error": f"Export zlyhal: {exc}"}), 500


@backup_bp.route("/import", methods=["POST"])
def post_backup_import():
    """
    Prijme .sql.gz súbor a zlúči ho do lokálnej DB.
    Multipart form-data: pole 'file'.
    """
    import time
    now = time.monotonic()
    if now - _IMPORT_RATE_LOCK_TS[0] < 10:
        return jsonify({"error": "Príliš veľa pokusov — počkaj 10 sekúnd."}), 429
    _IMPORT_RATE_LOCK_TS[0] = now

    if "file" not in request.files:
        return jsonify({"error": "Chýba súbor — pošli multipart pole 'file'."}), 400

    gz_file = request.files["file"]
    gz_bytes = gz_file.read()

    try:
        stats = import_db(gz_bytes)
        return jsonify({
            "ok": True,
            "added_runs":     stats["added_runs"],
            "new_parcels":    stats["new_parcels"],
            "merged_parcels": stats["merged_parcels"],
            "message": (
                f"✅ Hotovo! Pridané: {stats['added_runs']} behov, "
                f"{stats['new_parcels']} nových pozemkov, "
                f"{stats['merged_parcels']} pozemkov zlúčených."
            ),
        }), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Import zlyhal: {exc}"}), 500


@backup_bp.route("/history", methods=["GET"])
def get_backup_history():
    """Vráti zoznam archívnych záloh v history/."""
    try:
        return jsonify(list_history()), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
