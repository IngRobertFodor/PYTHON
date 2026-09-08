"""Parcel routes
===============
POST /api/analyze             -> analyza 1 pozemku
POST /api/parcels/analyze-batch -> analyza N pozemkov, zoradene podla skore
"""

from flask import Blueprint, jsonify, request
from models.parcel  import Parcel
from services.pipeline_service  import analyze_parcel
from services.notifier_service  import notify_parcel

parcel_bp = Blueprint("parcels", __name__)

# Povinne polia v JSON tele poziadavky
REQUIRED_FIELDS = ["title", "price_eur", "area_sqm", "location_text"]


def _parcel_from_json(data):
    """
    Vytvori Parcel z JSON dict.
    Akceptuje vsetky polia Parcel dataclassy, ostatne ignoruje.
    """
    return Parcel(
        title          = data.get("title", ""),
        url            = data.get("url", ""),
        source_portal  = data.get("source_portal", ""),
        price_eur      = float(data.get("price_eur", 0)),
        area_sqm       = float(data.get("area_sqm", 0)),
        location_text  = data.get("location_text", ""),
        parcel_number  = data.get("parcel_number", ""),
        description    = data.get("description", ""),
        lat            = float(data.get("lat", 0.0)),
        lon            = float(data.get("lon", 0.0)),
    )


def _validate_required(data):
    """
    Vrati zoznam chybajucich povinnych poli.
    """
    missing = [f for f in REQUIRED_FIELDS if not data.get(f)]
    return missing


@parcel_bp.route("/analyze", methods=["POST"])
def analyze_one():
    """
    Analyza jedneho pozemku.

    Request JSON:
        { title, price_eur, area_sqm, location_text,
          url?, source_portal?, parcel_number?,
          lat?, lon?, description? }

    Returns:
        200 { parcel: {...}, report: {...} }       ok
        400 { error, missing_fields: [...] }       chybajuce polia
        500 { error }                             chyba pipeline
    """
    data = request.get_json(silent=True) or {}
    missing = _validate_required(data)
    if missing:
        return jsonify({"error": "Chybaju povinne polia",
                        "missing_fields": missing}), 400

    try:
        parcel = _parcel_from_json(data)
        analyze_parcel(parcel)
        notify_parcel(parcel)
        report_r = parcel.results.get("report_service")
        return jsonify({
            "parcel": parcel.to_dict(),
            "report": report_r.data if report_r else {},
        }), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@parcel_bp.route("/parcels/analyze-batch", methods=["POST"])
def analyze_batch():
    """
    Analyza zoznamu pozemkov.

    Request JSON:
        { parcels: [ {title, price_eur, area_sqm, location_text, ...}, ... ] }

    Returns:
        200 { results: [...], count: N }   zoradene podla final_score DESC
        400 { error }                      chybajuci zoznam
        500 { error }                      chyba
    """
    data = request.get_json(silent=True) or {}
    items = data.get("parcels")
    if not isinstance(items, list):
        return jsonify({"error": "Ocakava sa: { parcels: [...] }"}), 400

    results = []
    errors  = []

    for i, item in enumerate(items):
        missing = _validate_required(item)
        if missing:
            errors.append({"index": i, "missing": missing})
            continue
        try:
            parcel = _parcel_from_json(item)
            analyze_parcel(parcel)
            notify_parcel(parcel)
            results.append(parcel.to_dict())
        except Exception as exc:
            errors.append({"index": i, "error": str(exc)})

    results.sort(key=lambda p: p["final_score"], reverse=True)

    return jsonify({
        "results": results,
        "count":   len(results),
        "errors":  errors,
    }), 200
