"""Config routes
===============
GET  /api/config/        -> aktualne kriteria, vahy, prahy (read-only)
GET  /api/config/validate -> overenie criteria.yaml, vrati zoznam chyb
POST /api/config/limits  -> ulozi 4 bezpecne polia (max_eur, min/max_area_sqm,
                            max_distance_km); ostatne polia configu su nedotknutelne
"""

import copy
from flask import Blueprint, jsonify, request
from config_loader    import get_config, get_scoring, get_criteria, get_features, \
                             get_notifications, save_config
from config_validator import validate_config

config_bp = Blueprint("config", __name__)

# Whitelist editovatelnych poli — nic ine sa neuklada
_EDITABLE = {
    "criteria.price.max_eur":           (float, int),
    "criteria.parcel.min_area_sqm":     (float, int),
    "criteria.parcel.max_area_sqm":     (float, int),
    "criteria.location.max_distance_km":(float, int),
}


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


@config_bp.route("/limits", methods=["POST"])
def update_limits():
    """
    Uloži 4 bezpečné polia do criteria.yaml.

    Accepted JSON body (všetky voliteľné, aspoň 1 musí byť prítomný):
        {
          "max_eur":           50000,
          "min_area_sqm":      350,
          "max_area_sqm":      1000,
          "max_distance_km":   85
        }

    Returns:
        200 { ok: true, saved: {...}, criteria: {...} }
        400 { ok: false, errors: [...] }   validačná chyba — NEULOŽÍ
        400 { ok: false, errors: [...] }   neznáme/chýbajúce polia
        500 { ok: false, errors: [...] }   chyba zápisu
    """
    body = request.get_json(silent=True) or {}

    # Mapovanie vstupného kľúča na cestu v confige
    _MAP = {
        "max_eur":          ("criteria", "price",    "max_eur"),
        "min_area_sqm":     ("criteria", "parcel",   "min_area_sqm"),
        "max_area_sqm":     ("criteria", "parcel",   "max_area_sqm"),
        "max_distance_km":  ("criteria", "location", "max_distance_km"),
    }

    # Aspoň jedno pole musí prísť
    known = {k: v for k, v in body.items() if k in _MAP}
    if not known:
        return jsonify({
            "ok": False,
            "errors": [
                "Žiadne platné pole. Povolené: "
                + ", ".join(_MAP.keys()) + "."
            ],
        }), 400

    # Overiť typy — musia byť čísla
    type_errors = []
    for k, v in known.items():
        if not isinstance(v, (int, float)):
            type_errors.append(f"'{k}' musí byť číslo (dostané: {type(v).__name__}).")
    if type_errors:
        return jsonify({"ok": False, "errors": type_errors}), 400

    # Deep-copy aktuálneho configu a aplikuj zmeny (whitelist)
    new_cfg = copy.deepcopy(get_config())
    saved = {}
    for k, v in known.items():
        sec1, sec2, key = _MAP[k]
        new_cfg.setdefault(sec1, {}).setdefault(sec2, {})[key] = v
        saved[k] = v

    # Validácia pred zápisom — ak chyba, NEULOŽÍ
    errors = validate_config(new_cfg)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 400

    # Zápis + reload cache
    try:
        save_config(new_cfg)
    except OSError as e:
        return jsonify({"ok": False, "errors": [f"Chyba zápisu: {e}"]}), 500

    return jsonify({
        "ok":       True,
        "saved":    saved,
        "criteria": get_criteria(),
    }), 200

