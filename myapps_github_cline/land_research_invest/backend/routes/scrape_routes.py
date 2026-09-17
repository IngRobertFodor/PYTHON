"""Scrape routes
================
GET  /api/scrape/progress  -> aktualny stav scrapingu (X/N zdrojov, %, per-source)
POST /api/scrape/start     -> spusti scrape_all() v pozadi (thread), vrati 202

Pouzitie vo frontende:
  1. POST /api/scrape/start          -> spusti scraping
  2. GET  /api/scrape/progress       -> polling kazde 2s -> zobraz progress bar
  3. Ked progress.finished == true   -> zobraz vysledky
"""

import threading
from flask import Blueprint, jsonify

from services.scraper_service import scrape_all, get_scrape_progress

scrape_bp = Blueprint("scrape", __name__)

# Globalny lock: zabrani sucasnemu spusteniu dvoch scrapingov
_scrape_lock = threading.Lock()


@scrape_bp.route("/progress", methods=["GET"])
def scrape_progress():
    """
    Vrati aktualny stav scrapingu.

    Returns:
        200 {
            running:    bool,   -- True pocas scrapingu
            total:      int,    -- celkovy pocet zdrojov (napr. 7)
            done:       int,    -- pocet dokoncených zdrojov
            percent:    int,    -- 0-100
            sources:    list,   -- ['nehnutelnosti_sk', ...]
            per_source: dict,   -- {'spf': 0, 'topreality_sk': 128, ...} alebo None=este bezi
            elapsed_s:  float,  -- cas behu v sekundach
            finished:   bool,   -- True po dokonceni scrape_all()
            total_parcels: int  -- celkovy pocet pozemkov (priebezne rastie)
        }
    """
    return jsonify(get_scrape_progress()), 200


@scrape_bp.route("/start", methods=["POST"])
def scrape_start():
    """
    Spusti scrape_all() v pozadi (daemon thread).
    Ak uz bezi, vrati 409 Conflict.

    Returns:
        202 { message, sources }    -- scraping spusteny
        409 { error }               -- uz bezi
    """
    prog = get_scrape_progress()
    if prog.get("running"):
        return jsonify({"error": "Scraping uz bezi"}), 409

    if not _scrape_lock.acquire(blocking=False):
        return jsonify({"error": "Scraping uz bezi (lock)"}), 409

    def _run():
        try:
            scrape_all()
        finally:
            _scrape_lock.release()

    t = threading.Thread(target=_run, daemon=True, name="scrape_all_bg")
    t.start()

    prog_after = get_scrape_progress()
    return jsonify({
        "message": "Scraping spusteny",
        "sources": prog_after.get("sources", []),
    }), 202
