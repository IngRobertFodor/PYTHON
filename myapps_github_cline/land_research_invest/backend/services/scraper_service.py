"""Scraper sluzba - orchestrator vsetkych zdrojov
=================================================
Zbiera inzeraty zo vsetkych zapnutych GREEN zdrojov
definovanych v config/criteria.yaml (sources sekcia).

Aktivacia:
  Kazdy zdroj sa skrapuje len ak:
    1. sources -> <zdroj> -> enabled: true
    2. sources -> <zdroj> -> zone: GREEN
    3. Je registrovany parser v SCRAPER_REGISTRY

Pridanie noveho zdroja:
  1. Vytvor backend/services/scrapers/<zdroj>_scraper.py
     (zdedi BaseScraper, implementuj parse_listings)
  2. Pridaj do SCRAPER_REGISTRY nizsie
  Tato funkcia (scrape_all) sa NEzmeni.

Paralelizacia:
  scrape_all() spusta vsetky zdroje SUCASNE (ThreadPoolExecutor).
  Kazdy zdroj je na inej domene => nulove riziko banu.
  Rate-limit v ramci jednej domeny ostava zachovany v BaseScraper.

Progress:
  scrape_all() aktualizuje globalny thread-safe stav _progress.
  get_scrape_progress() vracia aktualny stav pre API / frontend.
"""

import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError

from config_loader import get_green_sources
from services.scrapers.nehnutelnosti_scraper import NehnutelnostiScraper
from services.scrapers.topreality_scraper import TopRealityScraper
from services.scrapers.obchodny_vestnik_scraper import ObchodnyVestnikScraper
from services.scrapers.spf_scraper import SpfScraper
from services.scrapers.notarske_drazby_scraper import NotarskeDrazbyaScraper
from services.scrapers.reality_sk_scraper import RealitySkScraper
from services.scrapers.ske_scraper import SkeScraper

SERVICE_NAME = "scraper_service"
logger = logging.getLogger(__name__)

# Per-zdroj timeout: ak jeden zdroj trvá dlhšie, nepocká sa naňho donekonecna.
# 2700s = 45 min (dostatok aj pre zdroje s 50 stranami + rate-limitom 10/min)
SCRAPER_TIMEOUT_SEC = 2700

# ----------------------------------------------------------------
# Progress stav (thread-safe singleton)
# ----------------------------------------------------------------

_progress_lock = threading.Lock()
_progress = {
    "running":   False,   # True pocas scrape_all()
    "total":     0,       # celkovy pocet zdrojov
    "done":      0,       # pocet dokoncených zdrojov
    "percent":   0,       # done/total * 100 (0-100)
    "sources":   [],      # zoznam vsetkych zdrojov
    "per_source": {},     # {zdroj: pocet_pozemkov alebo None ak este bezi}
    # F2: rozšírená diagnostika stavu zdroja (spätne kompatibilné — per_source ostáva)
    "per_source_status": {},  # {zdroj: {"status": ok|error|timeout|empty, "count": N, "error": str}}
    "elapsed_s": 0.0,
    "finished":  False,
    "total_parcels": 0,
    "failed_sources": [],    # F2: zoznam zdrojov ktoré zlyhali (pre súhrnnú lištu v UI)
}


def get_scrape_progress():
    """
    Vrati aktualny progress stav scrapingu (thread-safe kopia).
    Pouziva sa pre API endpoint GET /api/scrape/progress.

    Returns:
        dict: running, total, done, percent, sources, per_source,
              elapsed_s, finished, total_parcels
    """
    with _progress_lock:
        return dict(_progress)


def _reset_progress(sources):
    """Resetuje progress pred novym behom scrape_all()."""
    with _progress_lock:
        _progress["running"]           = True
        _progress["total"]             = len(sources)
        _progress["done"]              = 0
        _progress["percent"]           = 0
        _progress["sources"]           = list(sources)
        _progress["per_source"]        = {s: None for s in sources}  # None = este bezi
        _progress["per_source_status"] = {s: {"status": "running", "count": None, "error": ""} for s in sources}
        _progress["elapsed_s"]         = 0.0
        _progress["finished"]          = False
        _progress["total_parcels"]     = 0
        _progress["failed_sources"]    = []


def _update_progress(src, count, elapsed_s, status="ok", error_msg=""):
    """Aktualizuje progress po dokonceni jedneho zdroja.

    Args:
        src:       nazov zdroja
        count:     pocet najdenych pozemkov
        elapsed_s: cas od zaciatku behu
        status:    "ok" | "error" | "timeout" | "empty"
        error_msg: strucny popis chyby (len pri status=error/timeout)
    """
    with _progress_lock:
        _progress["per_source"][src] = count
        _progress["done"]     += 1
        total = _progress["total"]
        _progress["percent"]   = round(100 * _progress["done"] / total) if total else 0
        _progress["elapsed_s"] = elapsed_s
        _progress["total_parcels"] += count
        # F2: rozšírená diagnostika
        effective_status = status
        if effective_status == "ok" and count == 0:
            effective_status = "empty"
        _progress["per_source_status"][src] = {
            "status": effective_status,
            "count":  count,
            "error":  error_msg,
        }
        if effective_status in ("error", "timeout"):
            _progress["failed_sources"].append(src)


def _finish_progress(elapsed_s):
    """Oznaci progress ako dokonceny."""
    with _progress_lock:
        _progress["running"]   = False
        _progress["finished"]  = True
        _progress["elapsed_s"] = elapsed_s
        if _progress["total"]:
            _progress["percent"] = 100

# ----------------------------------------------------------------
# Registry: config source_name -> ScraperClass
# Pridaj sem kazdý novy zdroj po implementacii.
# ----------------------------------------------------------------

SCRAPER_REGISTRY = {
    "nehnutelnosti_sk":  NehnutelnostiScraper,
    "topreality_sk":     TopRealityScraper,
    "obchodny_vestnik":  ObchodnyVestnikScraper,
    "spf":               SpfScraper,
    "notarske_drazby":   NotarskeDrazbyaScraper,
    "reality_sk":        RealitySkScraper,
    "ske_drazobne_vyhlasky": SkeScraper,
    # "eks_statny_majetok": EksScraper,              # TODO faza C5
    # "bsk_kraj":          BskKrajScraper,           # TODO faza C6
    # "obce_uradne_tabule": ObceUradneTabuleScraper, # TODO faza C6
}


def get_registered_scrapers():
    """Vrati zoznam registrovanych scraperov (source_name)."""
    return list(SCRAPER_REGISTRY.keys())


def scrape_all(criteria=None):
    """
    Spusti vsetky registrovane scrapery pre GREEN+enabled zdroje PARALELNE.

    Paralelizacia: kazdy zdroj bezi v samostatnom thread (ThreadPoolExecutor).
    Kazdy zdroj je na inej domene => ziadny server nedostane viac requestov
    nez dovoli jeho rate-limit. Nulove riziko banu.

    Per-zdroj timeout: zaseknuty zdroj neblokuje ostatne — po SCRAPER_TIMEOUT_SEC
    sa preskoci a ostatne vysledky sa vrátia.

    Args:
        criteria: volitelny dict s kriterimi (napr. max_price, max_distance)

    Returns:
        list[Parcel] - deduplikovane, zoradene podla URL
    """
    green = get_green_sources()
    active = [src for src in green if src in SCRAPER_REGISTRY]
    skipped = [src for src in green if src not in SCRAPER_REGISTRY]

    for src in skipped:
        logger.info("[scraper_service] %s: parser nie je registrovaný — preskakujem", src)

    all_parcels = []
    t_start = time.monotonic()

    _reset_progress(active)
    logger.info("[scraper_service] Paralelne spúšťam %d zdrojov: %s", len(active), active)

    with ThreadPoolExecutor(max_workers=len(active) or 1) as executor:
        future_to_src = {
            executor.submit(_scrape_one, src, criteria): src
            for src in active
        }
        try:
            for future in as_completed(future_to_src, timeout=SCRAPER_TIMEOUT_SEC + 30):
                src = future_to_src[future]
                elapsed_now = time.monotonic() - t_start
                try:
                    parcels = future.result(timeout=SCRAPER_TIMEOUT_SEC)
                    logger.info("[scraper_service] %s: %s pozemkov", src, len(parcels))
                    all_parcels.extend(parcels)
                    _update_progress(src, len(parcels), elapsed_now, status="ok")
                except FuturesTimeoutError:
                    logger.warning("[scraper_service] %s: TIMEOUT po %ss — preskakujem", src, SCRAPER_TIMEOUT_SEC)
                    _update_progress(src, 0, elapsed_now,
                                     status="timeout",
                                     error_msg=f"Timeout po {SCRAPER_TIMEOUT_SEC}s")
                except Exception as exc:
                    err_short = str(exc)[:120]
                    logger.error("[scraper_service] %s CHYBA: %s", src, err_short)
                    _update_progress(src, 0, elapsed_now,
                                     status="error",
                                     error_msg=err_short)
        except TimeoutError:
            pending = [s for f,s in future_to_src.items() if not f.done()]
            for src in pending:
                logger.warning("[scraper_service] %s: GLOBALNY TIMEOUT — preskakujem", src)
                _update_progress(src, 0, time.monotonic() - t_start,
                                 status="timeout",
                                 error_msg="Globálny timeout — zdroj nedobehol")

    elapsed = time.monotonic() - t_start
    result = _deduplicate(all_parcels)
    _enrich_coords_offline(result)   # F5-A: doplní GPS z sk_places (obec-level, 0 HTTP)
    _finish_progress(elapsed)
    logger.info("[scraper_service] Hotovo: %s unikatnych pozemkov za %ss", len(result), round(elapsed))
    return result


def _enrich_coords_offline(parcels):
    """
    F5-A: Doplní GPS súradnice z sk_places (offline, obec-level ~2-5 km presnosť).

    Pozemky z inzerátov / SPF majú lat=0/lon=0 po scrape. Mapa by bola prázdna
    dokým používateľ nespustí plný GIS scoring. Toto doplní obec-level GPS
    pre všetkých, mapa sa naplní ihneď. Presnejšie GPS (ulica) sa doplní
    neskôr v pipeline cez Nominatim (geocoding_service).

    Mutuje parcely in-place. 0 HTTP volaní, čas ~0.5s pre 5000 pozemkov.
    """
    try:
        from services import sk_places
    except Exception as exc:
        logger.warning("[scraper_service] sk_places import zlyhal, mapa ostane prázdna: %s", exc)
        return

    enriched = 0
    for p in parcels:
        if (p.lat and p.lon) or not p.location_text:
            continue
        place = sk_places.find_place(p.location_text)
        if place:
            _, lat, lon = place
            p.lat = lat
            p.lon = lon
            enriched += 1
    logger.info("[scraper_service] Offline GPS doplnené pre %d/%d pozemkov", enriched, len(parcels))


def scrape_source(source_name, criteria=None):
    """
    Spusti jeden konkretny scraper.

    Args:
        source_name: napr. "nehnutelnosti_sk"
        criteria: volitelny dict

    Returns:
        list[Parcel]

    Raises:
        KeyError: ak source_name nie je v registri
    """
    if source_name not in SCRAPER_REGISTRY:
        raise KeyError(f"Scraper '{source_name}' nie je registrovany. Dostupne: {get_registered_scrapers()}")
    scraper = SCRAPER_REGISTRY[source_name]()
    return scraper.scrape(criteria)


# ----------------------------------------------------------------
# Interne pomocne funkcie
# ----------------------------------------------------------------

def _scrape_one(source_name, criteria=None):
    """Spusti jeden scraper — volane z ThreadPoolExecutor."""
    logger.info("[scraper_service] Scrapujem: %s", source_name)
    scraper = SCRAPER_REGISTRY[source_name]()
    return scraper.scrape(criteria)


def _deduplicate(parcels):
    """
    Odstrani duplicitne pozemky.
    Klic: url (lower) + parcel_number + location_text — zachova vsetky parcely
    z toho isteho PDF/drazby aj ked zdielaju URL.
    Zachova prvy vyskyt.
    """
    seen = set()
    result = []
    for p in parcels:
        base     = p.url.strip().lower() if p.url else str(id(p))
        suffix   = p.parcel_number.strip() if p.parcel_number else ""
        loc      = p.location_text.strip().lower() if p.location_text else ""
        # Pouzij kombinaciu url + parcel_number + lokacia pre SKE/OV kde
        # jeden drazobny spis (url) moze mat viacero parciel v roznych obciach
        key = f"{base}#{suffix}#{loc}" if (suffix or loc) else base
        if key not in seen:
            seen.add(key)
            result.append(p)
    return result
