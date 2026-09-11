"""BaseScraper - abstraktna trieda pre vsetky scrapery
=====================================================
Kazdy novy portal = novy subor ktory zdedi BaseScraper
a implementuje: fetch_html(), parse_listings().

Konvencia nazvania:
  source_name (config key) -> <source_name>_scraper.py
  napr. nehnutelnosti_sk   -> nehnutelnosti_scraper.py
        topreality_sk      -> topreality_scraper.py
"""

import time
import requests
from models.parcel import Parcel
from config_loader import get_sources

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
AI_BOT_USER_AGENT = "LandResearchInvest/1.0 (land-parcel-research)"

TIMEOUT = 20


class BaseScraper:
    """Abstraktna trieda pre scraper jedneho zdroja."""

    # Podtriedy MUSIA definovat:
    SOURCE_NAME = ""          # napr. "nehnutelnosti_sk"
    BASE_URL    = ""          # napr. "https://www.nehnutelnosti.sk"

    def __init__(self):
        cfg = get_sources().get(self.SOURCE_NAME, {})
        self.rate_limit  = cfg.get("rate_limit_per_min", 10)
        self.neutral_ua  = cfg.get("use_neutral_useragent", False)
        self._last_call  = 0.0

    @property
    def user_agent(self):
        """Zvoli user-agent podla nastavenia zdroja."""
        return DEFAULT_USER_AGENT if self.neutral_ua else AI_BOT_USER_AGENT

    def fetch_html(self, url):
        """
        HTTP GET s rate-limitom a spravnym user-agentom.
        Implementuj v podtriede ak potrebujes specialny handling.
        """
        self._wait_rate_limit()
        resp = requests.get(
            url,
            headers={"User-Agent": self.user_agent},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        return resp.text

    def parse_listings(self, html):
        """
        Parsuje HTML/JSON a vrati zoznam Parcel objektov.
        MUSI byt implementovana v podtriede.
        """
        raise NotImplementedError(f"{self.__class__.__name__}.parse_listings() nie je implementovana")

    def get_listing_urls(self, criteria=None):
        """
        Vrati zoznam URL na scrapovanie.
        Predvolene vracia [BASE_URL] - podtrieda moze prepisat.
        """
        return [self.BASE_URL] if self.BASE_URL else []

    def scrape(self, criteria=None):
        """
        Orchestracia: fetch + parse pre vsetky listing URLs.
        Vracia zoznam Parcel objektov.
        """
        results = []
        for url in self.get_listing_urls(criteria):
            try:
                html = self.fetch_html(url)
                parcels = self.parse_listings(html)
                results.extend(parcels)
            except Exception as exc:
                print(f"[{self.SOURCE_NAME}] chyba pri {url}: {exc}")
        return results

    def scrape_all_pages(self, base_url, page_param="page", max_safety=50):
        """
        Stránkovanie: ide stranu po strane kym su NOVE vysledky.
        Auto-stop: strana vrati 0 novych pozemkov (koniec / duplicity).
        Strop: max_safety stran (poistka proti nekonecnu, default 50).
        Pouziva ten isty rate-limit ako fetch_html().
        """
        seen    = set()
        results = []
        for page in range(1, max_safety + 1):
            url = self._page_url(base_url, page, page_param)
            try:
                html    = self.fetch_html(url)
                parcels = self.parse_listings(html)
            except Exception as exc:
                print(f"[{self.SOURCE_NAME}] strana {page} chyba: {exc}")
                break
            new = [p for p in parcels if p.url and p.url not in seen]
            if not new:
                break                    # koniec zoznamu alebo duplicity
            seen.update(p.url for p in new)
            results.extend(new)
        return results

    @staticmethod
    def _page_url(base_url, page, param="page"):
        """
        Prida strankovaci parameter do URL.
        Strana 1 vracia povodne base_url bez parametra.
        Strana N prida ?param=N alebo &param=N podla existencie query stringu.
        """
        if page == 1:
            return base_url
        sep = "&" if "?" in base_url else "?"
        return f"{base_url}{sep}{param}={page}"

    # ----------------------------------------------------------------
    # Interne pomocne metody
    # ----------------------------------------------------------------

    def _wait_rate_limit(self):
        """Pocka ak je potrebne pre dodrzanie rate-limitu."""
        if self.rate_limit <= 0:
            return
        min_interval = 60.0 / self.rate_limit
        elapsed = time.monotonic() - self._last_call
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self._last_call = time.monotonic()

    @staticmethod
    def _make_parcel(title="", url="", price_eur=0.0, area_sqm=0.0,
                     location_text="", source_portal="",
                     parcel_number="", description=""):
        """Helper - vytvori Parcel zo scraped dat."""
        return Parcel(
            title=title,
            url=url,
            price_eur=float(price_eur or 0),
            area_sqm=float(area_sqm or 0),
            location_text=location_text,
            source_portal=source_portal,
            parcel_number=parcel_number,
            description=description,
        )
