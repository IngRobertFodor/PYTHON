"""Scrape routes
================
GET  /api/scrape/progress        -> aktualny stav scrapingu
POST /api/scrape/start           -> spusti scrape_all() + pre-scoring, vrati 202
GET  /api/scrape/results         -> vysledky (preliminary_score zoradene)
POST /api/scrape/score-selected  -> plny GIS scoring vybranych parciel
GET  /api/scrape/score-progress  -> stav plneho scoringu
"""

import threading
from flask import Blueprint, jsonify, request

from services.scraper_service  import scrape_all, get_scrape_progress
from services.scoring_service  import preliminary_score
from services.pipeline_service import analyze_parcel
from models.parcel import Parcel

scrape_bp = Blueprint("scrape", __name__)

# --- Scraping ---
_scrape_lock  = threading.Lock()
_results_lock = threading.Lock()
_last_results: list = []

# --- Plny scoring ---
_score_lock      = threading.Lock()
_score_progress  = {"running": False, "done": 0, "total": 0,
                    "percent": 0, "finished": False}
_score_prog_lock = threading.Lock()


def _get_last_results():
    with _results_lock:
        return list(_last_results)


def _set_last_results(items):
    with _results_lock:
        _last_results.clear()
        _last_results.extend(items)


def _patch_last_results(scored: dict):
    """Aktualizuje zaznam v _last_results podla url (in-place patch)."""
    with _results_lock:
        for i, item in enumerate(_last_results):
            if item.get("url") == scored.get("url"):
                _last_results[i] = scored
                break


def _get_score_progress():
    with _score_prog_lock:
        return dict(_score_progress)


def _update_score_progress(done, total, finished=False):
    with _score_prog_lock:
        _score_progress["done"]     = done
        _score_progress["total"]    = total
        _score_progress["percent"]  = int(done / total * 100) if total else 0
        _score_progress["running"]  = not finished
        _score_progress["finished"] = finished


@scrape_bp.route("/progress", methods=["GET"])
def scrape_progress():
    """Vrati aktualny stav scrapingu."""
    return jsonify(get_scrape_progress()), 200


@scrape_bp.route("/start", methods=["POST"])
def scrape_start():
    """Spusti scrape_all() + lacny preliminary_score() v pozadi. 202/409."""
    if get_scrape_progress().get("running"):
        return jsonify({"error": "Scraping uz bezi"}), 409
    if not _scrape_lock.acquire(blocking=False):
        return jsonify({"error": "Scraping uz bezi (lock)"}), 409

    def _run():
        try:
            parcels = scrape_all()
            analyzed = []
            for p in parcels:
                try:
                    preliminary_score(p)
                except Exception:
                    pass
                analyzed.append(p.to_dict())
            analyzed.sort(key=lambda d: d.get("preliminary_score", 0), reverse=True)
            _set_last_results(analyzed)
        finally:
            _scrape_lock.release()

    threading.Thread(target=_run, daemon=True, name="scrape_all_bg").start()
    prog = get_scrape_progress()
    return jsonify({"message": "Scraping spusteny", "sources": prog.get("sources", [])}), 202


@scrape_bp.route("/results", methods=["GET"])
def scrape_results():
    """Vrati vysledky zoradene podla preliminary_score DESC."""
    items = _get_last_results()
    return jsonify({"results": items, "count": len(items)}), 200


@scrape_bp.route("/score-selected", methods=["POST"])
def score_selected():
    """
    Spusti plny analyze_parcel() pre vybrane parcely.
    Body: { "urls": [...] }  max 30.
    Returns 202/400/404/409.
    """
    if not _score_lock.acquire(blocking=False):
        return jsonify({"error": "Scoring uz bezi"}), 409

    data = request.get_json(silent=True) or {}
    urls = data.get("urls", [])
    if not urls:
        _score_lock.release()
        return jsonify({"error": "Ziadne URL na scoring"}), 400

    urls     = urls[:30]
    to_score = [item for item in _get_last_results() if item.get("url") in set(urls)]

    if not to_score:
        _score_lock.release()
        return jsonify({"error": "Ziadne parcely pre zadane URL"}), 404

    _update_score_progress(0, len(to_score), finished=False)

    def _run_scoring():
        try:
            for i, item in enumerate(to_score):
                try:
                    p = Parcel(
                        url                  = item.get("url", ""),
                        source_portal        = item.get("source_portal", ""),
                        title                = item.get("title", ""),
                        price_eur            = float(item.get("price_eur", 0)),
                        area_sqm             = float(item.get("area_sqm", 0)),
                        location_text        = item.get("location_text", ""),
                        parcel_number        = item.get("parcel_number", ""),
                        description          = item.get("description", ""),
                        lat                  = float(item.get("lat", 0)),
                        lon                  = float(item.get("lon", 0)),
                        price_per_sqm        = float(item.get("price_per_sqm", 0)),
                        preliminary_score    = float(item.get("preliminary_score", 0)),
                        prelim_recommendation= item.get("prelim_recommendation", ""),
                    )
                    analyze_parcel(p)
                    _patch_last_results(p.to_dict())
                except Exception as exc:
                    print(f"[score_selected] {item.get('url','')}: {exc}")
                _update_score_progress(i + 1, len(to_score))
        finally:
            _update_score_progress(len(to_score), len(to_score), finished=True)
            _score_lock.release()

    threading.Thread(target=_run_scoring, daemon=True, name="score_selected_bg").start()
    return jsonify({"message": "Scoring spusteny", "count": len(to_score)}), 202


@scrape_bp.route("/score-progress", methods=["GET"])
def score_progress():
    """Vrati stav plneho GIS scoringu."""
    return jsonify(_get_score_progress()), 200


@scrape_bp.route("/results.csv", methods=["GET"])
def scrape_results_csv():
    """
    Exportuje vsetky vysledky posledneho scrapingu ako CSV.
    Delimiter: ; (SK Excel standard), encoding: utf-8-sig (BOM -> diakritika OK).
    Vracia vsetky _last_results bez ohladom na klientsky filter.
    """
    import csv
    import io
    from flask import Response

    items = _get_last_results()
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)

    writer.writerow([
        "Zdroj", "Lokalita", "Cena_EUR", "Vymera_m2", "EUR_m2",
        "Prelim_skore", "Prelim_odporucanie",
        "Final_skore", "Odporucanie", "URL",
    ])

    for p in items:
        area = p.get("area_sqm") or 0
        price = p.get("price_eur") or 0
        ppsm = p.get("price_per_sqm") or (
            round(price / area, 2) if area > 0 else 0
        )
        writer.writerow([
            p.get("source_portal", ""),
            p.get("location_text", ""),
            price,
            area,
            ppsm,
            p.get("preliminary_score", 0),
            p.get("prelim_recommendation", ""),
            p.get("final_score", 0),
            p.get("recommendation", ""),
            p.get("url", ""),
        ])

    csv_bytes = output.getvalue().encode("utf-8-sig")   # BOM pre SK Excel
    return Response(
        csv_bytes,
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=pozemky.csv",
            "Content-Length": str(len(csv_bytes)),
        },
    )

