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
"""

import time
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

# Per-zdroj timeout: ak jeden zdroj trvá dlhšie, nepocká sa naňho donekonecna.
# 2700s = 45 min (dostatok aj pre zdroje s 50 stranami + rate-limitom 10/min)
SCRAPER_TIMEOUT_SEC = 2700

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
        print(f"[scraper_service] {src}: parser TODO - preskacujem")

    all_parcels = []
    t_start = time.monotonic()

    print(f"[scraper_service] Paralelne spustam {len(active)} zdrojov: {active}")

    with ThreadPoolExecutor(max_workers=len(active) or 1) as executor:
        future_to_src = {
            executor.submit(_scrape_one, src, criteria): src
            for src in active
        }
        for future in as_completed(future_to_src, timeout=SCRAPER_TIMEOUT_SEC + 30):
            src = future_to_src[future]
            try:
                parcels = future.result(timeout=SCRAPER_TIMEOUT_SEC)
                print(f"[scraper_service] {src}: {len(parcels)} pozemkov")
                all_parcels.extend(parcels)
            except FuturesTimeoutError:
                print(f"[scraper_service] {src}: TIMEOUT po {SCRAPER_TIMEOUT_SEC}s — preskakujem")
            except Exception as exc:
                print(f"[scraper_service] {src} CHYBA: {exc}")

    elapsed = time.monotonic() - t_start
    result = _deduplicate(all_parcels)
    print(f"[scraper_service] Hotovo: {len(result)} unikatnych pozemkov za {elapsed:.0f}s")
    return result


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
    print(f"[scraper_service] Scrapujem: {source_name}")
    scraper = SCRAPER_REGISTRY[source_name]()
    return scraper.scrape(criteria)


def _deduplicate(parcels):
    """
    Odstrani duplicitne pozemky podla URL.
    Zachova prvy vyskyt.
    """
    seen = set()
    result = []
    for p in parcels:
        key = p.url.strip().lower() if p.url else id(p)
        if key not in seen:
            seen.add(key)
            result.append(p)
    return result
