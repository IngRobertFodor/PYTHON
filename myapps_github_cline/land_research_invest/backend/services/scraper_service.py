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
"""

from config_loader import get_green_sources
from services.scrapers.nehnutelnosti_scraper import NehnutelnostiScraper
from services.scrapers.topreality_scraper import TopRealityScraper
from services.scrapers.obchodny_vestnik_scraper import ObchodnyVestnikScraper
from services.scrapers.spf_scraper import SpfScraper
from services.scrapers.notarske_drazby_scraper import NotarskeDrazbyaScraper
from services.scrapers.reality_sk_scraper import RealitySkScraper

SERVICE_NAME = "scraper_service"

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
    # "exekutorske_drazby": ExekutorskeDrazbyScr,   # TODO faza C4
    # "drazby_net":        DrazbyNetScraper,         # TODO faza C4
    # "eks_statny_majetok": EksScraper,              # TODO faza C5
    # "bsk_kraj":          BskKrajScraper,           # TODO faza C6
    # "obce_uradne_tabule": ObceUradneTabuleScraper, # TODO faza C6
}


def get_registered_scrapers():
    """Vrati zoznam registrovanych scraperov (source_name)."""
    return list(SCRAPER_REGISTRY.keys())


def scrape_all(criteria=None):
    """
    Spusti vsetky registrovane scrapery pre GREEN+enabled zdroje.

    Pre kazdy zdroj:
      - Ak je v SCRAPER_REGISTRY -> spusti scraper
      - Ak nie je                -> preskoci + vypise info

    Args:
        criteria: volitelny dict s kriterimi (napr. max_price, max_distance)

    Returns:
        list[Parcel] - deduplikovane, zoradene podla URL
    """
    green = get_green_sources()
    all_parcels = []

    for source_name in green:
        if source_name not in SCRAPER_REGISTRY:
            print(f"[scraper_service] {source_name}: parser TODO - preskacujem")
            continue
        try:
            scraper = SCRAPER_REGISTRY[source_name]()
            print(f"[scraper_service] Scrapujem: {source_name}")
            parcels = scraper.scrape(criteria)
            print(f"[scraper_service] {source_name}: {len(parcels)} pozemkov")
            all_parcels.extend(parcels)
        except Exception as exc:
            print(f"[scraper_service] {source_name} CHYBA: {exc}")

    return _deduplicate(all_parcels)


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