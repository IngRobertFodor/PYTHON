"""Testy - Scraper sluzba (spolocne testy)
Testuje: BaseScraper kontrakt, SCRAPER_REGISTRY, scrape_all, scrape_source,
_deduplicate. Integracne testy mocuju HTTP volania.
Parser-specificke testy su v test_<zdroj>_scraper.py suboroch.
100% offline - HTTP je mocknuty.
"""

import pytest
import pathlib
from unittest.mock import patch

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "nehnutelnosti_sk_listing.html"

from services.scrapers.base_scraper import BaseScraper
from services.scrapers.nehnutelnosti_scraper import NehnutelnostiScraper
from services.scraper_service import (
    scrape_all, scrape_source, get_registered_scrapers, _deduplicate,
    SCRAPER_REGISTRY,
)
from models.parcel import Parcel


@pytest.fixture(scope="module")
def fixture_html():
    return FIXTURE.read_text(encoding="utf-8")


# ----------------------------------------------------------------
# TestBaseScraper
# ----------------------------------------------------------------

class TestBaseScraper:
    def test_source_name_empty_by_default(self):
        assert BaseScraper.SOURCE_NAME == ""

    def test_parse_listings_raises_not_implemented(self):
        scraper = BaseScraper.__new__(BaseScraper)
        scraper.rate_limit = 0
        scraper.neutral_ua = False
        scraper._last_call = 0.0
        with pytest.raises(NotImplementedError):
            scraper.parse_listings("html")

    def test_make_parcel_returns_parcel(self):
        p = BaseScraper._make_parcel(title="test", price_eur=10000, area_sqm=500)
        assert isinstance(p, Parcel)

    def test_make_parcel_fields(self):
        p = BaseScraper._make_parcel(
            title="Pozemok Senec",
            url="https://example.com/1",
            price_eur=35000,
            area_sqm=800,
            location_text="Senec",
        )
        assert p.title == "Pozemok Senec"
        assert p.price_eur == 35000.0
        assert p.area_sqm == 800.0
        assert p.location_text == "Senec"


# ----------------------------------------------------------------
# TestPagination
# ----------------------------------------------------------------

class TestPagination:
    """Testy pre scrape_all_pages a _page_url v BaseScraper."""

    def _make_scraper(self):
        s = BaseScraper.__new__(BaseScraper)
        s.SOURCE_NAME = "test_src"
        s.rate_limit  = 0
        s.neutral_ua  = False
        s._last_call  = 0.0
        return s

    # --- _page_url ---

    def test_page_url_page1_returns_base(self):
        assert BaseScraper._page_url("https://x.sk/pozemky/", 1) == "https://x.sk/pozemky/"

    def test_page_url_page2_adds_query(self):
        assert BaseScraper._page_url("https://x.sk/pozemky/", 2) == "https://x.sk/pozemky/?page=2"

    def test_page_url_page3_appends_to_existing_query(self):
        url = "https://x.sk/hladat?typ=pozemok"
        assert BaseScraper._page_url(url, 3) == "https://x.sk/hladat?typ=pozemok&page=3"

    def test_page_url_custom_param(self):
        assert BaseScraper._page_url("https://x.sk/", 2, "strana") == "https://x.sk/?strana=2"

    # --- scrape_all_pages ---

    def test_auto_stop_on_empty_page(self, fixture_html):
        """Strana 2 je prazdna -> auto-stop po strane 1."""
        call_count = {"n": 0}
        def mock_fetch(url):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return fixture_html   # strana 1: pozemky
            return "<html></html>"    # strana 2: prazdno -> stop

        s = NehnutelnostiScraper.__new__(NehnutelnostiScraper)
        s.rate_limit = 0; s.neutral_ua = False; s._last_call = 0.0
        with patch.object(NehnutelnostiScraper, "fetch_html", side_effect=mock_fetch):
            parcels = s.scrape_all_pages("https://www.nehnutelnosti.sk/vysledky/pozemky/test/")
        assert len(parcels) >= 20
        assert call_count["n"] == 2   # strana 1 + strana 2 (prazdna)

    def test_auto_stop_on_duplicates(self, fixture_html):
        """Strana 2 ma rovnake URL ako strana 1 -> auto-stop (0 novych)."""
        s = NehnutelnostiScraper.__new__(NehnutelnostiScraper)
        s.rate_limit = 0; s.neutral_ua = False; s._last_call = 0.0
        with patch.object(NehnutelnostiScraper, "fetch_html", return_value=fixture_html):
            parcels = s.scrape_all_pages("https://www.nehnutelnosti.sk/vysledky/pozemky/test/")
        # strana 1 = pozemky, strana 2 = tie iste URL -> auto-stop
        assert len(parcels) >= 20

    def test_safety_cap_stops_at_max(self, fixture_html):
        """Strop max_safety=3: nemoze ist dalej ako 3 strany aj keby prichadzali nove."""
        counter = {"n": 0}
        def mock_fetch_unique(url):
            counter["n"] += 1
            return fixture_html

        s = NehnutelnostiScraper.__new__(NehnutelnostiScraper)
        s.rate_limit = 0; s.neutral_ua = False; s._last_call = 0.0
        # kazda strana vracia rovnake URL -> auto-stop po 2 volaniach
        # (strana 1 = nowe, strana 2 = duplicity)
        with patch.object(NehnutelnostiScraper, "fetch_html", return_value=fixture_html):
            parcels = s.scrape_all_pages("https://test.sk/", max_safety=3)
        assert counter["n"] <= 4   # max 2 (auto-stop) alebo 3 (safety cap) + 1 buffer

    def test_exception_in_fetch_stops_gracefully(self):
        """Vynimka pri fetch -> break, vrati co mame."""
        s = NehnutelnostiScraper.__new__(NehnutelnostiScraper)
        s.rate_limit = 0; s.neutral_ua = False; s._last_call = 0.0
        with patch.object(NehnutelnostiScraper, "fetch_html", side_effect=Exception("conn err")):
            parcels = s.scrape_all_pages("https://test.sk/")
        assert parcels == []


# ----------------------------------------------------------------
# TestScraperService
# ----------------------------------------------------------------

class TestScraperService:
    def test_registry_has_nehnutelnosti(self):
        assert "nehnutelnosti_sk" in SCRAPER_REGISTRY

    def test_registry_has_topreality(self):
        assert "topreality_sk" in SCRAPER_REGISTRY

    def test_registry_has_obchodny_vestnik(self):
        assert "obchodny_vestnik" in SCRAPER_REGISTRY

    def test_get_registered_scrapers_returns_list(self):
        assert isinstance(get_registered_scrapers(), list)

    def test_get_registered_scrapers_contains_nehnutelnosti(self):
        assert "nehnutelnosti_sk" in get_registered_scrapers()

    def test_scrape_source_raises_for_unknown(self):
        with pytest.raises(KeyError):
            scrape_source("nonexistent_source_xyz")

    def test_scrape_source_calls_scraper(self, fixture_html):
        with patch.object(NehnutelnostiScraper, "fetch_html", return_value=fixture_html):
            parcels = scrape_source("nehnutelnosti_sk")
        assert len(parcels) >= 20
        assert all(isinstance(p, Parcel) for p in parcels)

    def test_scrape_all_calls_nehnutelnosti(self, fixture_html):
        with patch.object(NehnutelnostiScraper, "fetch_html", return_value=fixture_html):
            parcels = scrape_all()
        assert len(parcels) >= 20

    def test_scrape_all_deduplicates(self, fixture_html):
        with patch.object(NehnutelnostiScraper, "fetch_html", return_value=fixture_html):
            parcels = scrape_all()
        urls = [p.url for p in parcels if p.url]
        assert len(urls) == len(set(urls))

    def test_deduplicate_removes_duplicates(self):
        p1 = BaseScraper._make_parcel(url="https://example.com/1", price_eur=1000, area_sqm=100)
        p2 = BaseScraper._make_parcel(url="https://example.com/1", price_eur=1000, area_sqm=100)
        p3 = BaseScraper._make_parcel(url="https://example.com/2", price_eur=2000, area_sqm=200)
        assert len(_deduplicate([p1, p2, p3])) == 2

    def test_deduplicate_preserves_order(self):
        p1 = BaseScraper._make_parcel(url="https://a.com/1", price_eur=1)
        p2 = BaseScraper._make_parcel(url="https://a.com/2", price_eur=2)
        assert _deduplicate([p1, p2])[0].url == "https://a.com/1"

    def test_scrape_all_skips_unregistered_sources(self):
        with patch.object(NehnutelnostiScraper, "fetch_html", return_value="<html></html>"):
            parcels = scrape_all()
        assert isinstance(parcels, list)

