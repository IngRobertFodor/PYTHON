"""Scrape routes
================
GET  /api/scrape/progress  -> aktualny stav scrapingu (X/N zdrojov, %, per-source)
POST /api/scrape/start     -> spusti scrape_all() + analyze v pozadi, vrati 202
GET  /api/scrape/results   -> vysledky posledneho scrapingu (analyzovane, zoradene)

Pouzitie vo frontende:
  1. POST /api/scrape/start          -> spusti scraping
  2. GET  /api/scrape/progress       -> polling kazde 2s -> zobraz progress bar
  3. Ked progress.finished == true   -> GET /api/scrape/results -> zobraz vysledky
"""

import threading
from flask import Blueprint, jsonify

from services.scraper_service import scrape_all, get_scrape_progress
from services.pipeline_service import analyze_parcel

scrape_bp = Blueprint("scrape", __name__)

_scrape_lock  = threading.Lock()
_results_lock = threading.Lock()
_last_results = []


def _get_last_results():
    with _results_lock:
        return list(_last_results)


def _set_last_results(items):
    with _results_lock:
        _last_results.clear()
        _last_results.extend(items)


@scrape_bp.route("/progress", methods=["GET"])
def scrape_progress():
    """Vrati aktualny stav scrapingu (running, done, percent, per_source, ...)"""
    return jsonify(get_scrape_progress()), 200


@scrape_bp.route("/start", methods=["POST"])
def scrape_start():
    """
    Spusti scrape_all() + analyze_parcel() v pozadi (daemon thread).
    Ak uz bezi, vrati 409 Conflict.
    Returns 202 { message, sources } alebo 409.
    """
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
                    analyze_parcel(p)
                except Exception:
                    pass
                analyzed.append(p.to_dict())
            analyzed.sort(key=lambda d: d.get("final_score", 0), reverse=True)
            _set_last_results(analyzed)
        finally:
            _scrape_lock.release()

    threading.Thread(target=_run, daemon=True, name="scrape_all_bg").start()
    prog = get_scrape_progress()
    return jsonify({"message": "Scraping spusteny", "sources": prog.get("sources", [])}), 202


@scrape_bp.route("/results", methods=["GET"])
def scrape_results():
    """Vrati vysledky posledneho scrapingu, zoradene podla final_score DESC."""
    items = _get_last_results()
    return jsonify({"results": items, "count": len(items)}), 200
