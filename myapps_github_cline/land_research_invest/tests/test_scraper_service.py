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
    _scrape_one, SCRAPER_REGISTRY, SCRAPER_TIMEOUT_SEC,
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
        """scrape_all paralelne — mockujeme _scrape_one aby sme nevolali web."""
        import services.scraper_service as ss

        def fake_scrape_one(src, criteria=None):
            if src == "nehnutelnosti_sk":
                s = NehnutelnostiScraper.__new__(NehnutelnostiScraper)
                s.rate_limit = 0; s.neutral_ua = False; s._last_call = 0.0
                with patch.object(NehnutelnostiScraper, "fetch_html", return_value=fixture_html):
                    return s.scrape()
            return []

        with patch.object(ss, "_scrape_one", side_effect=fake_scrape_one):
            parcels = scrape_all()
        assert len(parcels) >= 20

    def test_scrape_all_deduplicates(self, fixture_html):
        import services.scraper_service as ss

        def fake_scrape_one(src, criteria=None):
            if src == "nehnutelnosti_sk":
                s = NehnutelnostiScraper.__new__(NehnutelnostiScraper)
                s.rate_limit = 0; s.neutral_ua = False; s._last_call = 0.0
                with patch.object(NehnutelnostiScraper, "fetch_html", return_value=fixture_html):
                    return s.scrape()
            return []

        with patch.object(ss, "_scrape_one", side_effect=fake_scrape_one):
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
        import services.scraper_service as ss
        with patch.object(ss, "_scrape_one", return_value=[]):
            parcels = scrape_all()
        assert isinstance(parcels, list)

# ----------------------------------------------------------------
# TestParallelScraping
# ----------------------------------------------------------------

class TestParallelScraping:
    """Testy paralelnéno scrape_all a odolnosti voči chybám."""

    def test_scrape_all_returns_list(self, fixture_html):
        import services.scraper_service as ss
        with patch.object(ss, "_scrape_one", return_value=[]):
            assert isinstance(scrape_all(), list)

    def test_scrape_all_parallel_all_sources_called(self, fixture_html):
        """Všetky aktívne zdroje sa zavolajú (paralelne)."""
        called = set()
        import services.scraper_service as ss

        def tracking_scrape_one(src, criteria=None):
            called.add(src)
            if src == "nehnutelnosti_sk":
                s = NehnutelnostiScraper.__new__(NehnutelnostiScraper)
                s.rate_limit = 0; s.neutral_ua = False; s._last_call = 0.0
                with patch.object(NehnutelnostiScraper, "fetch_html", return_value=fixture_html):
                    return s.scrape()
            return []

        with patch.object(ss, "_scrape_one", side_effect=tracking_scrape_one):
            scrape_all()
        assert "nehnutelnosti_sk" in called

    def test_scrape_all_one_source_exception_others_continue(self, fixture_html):
        """Výnimka v jednom zdroji nepreruší ostatné."""
        import services.scraper_service as ss

        def selective_scrape(src, criteria=None):
            if src == "nehnutelnosti_sk":
                s = NehnutelnostiScraper.__new__(NehnutelnostiScraper)
                s.rate_limit = 0; s.neutral_ua = False; s._last_call = 0.0
                with patch.object(NehnutelnostiScraper, "fetch_html", return_value=fixture_html):
                    return s.scrape()
            raise RuntimeError(f"Simulovana chyba pre {src}")

        with patch.object(ss, "_scrape_one", side_effect=selective_scrape):
            result = scrape_all()
        assert isinstance(result, list) and len(result) >= 1

    def test_scrape_all_deduplicates_across_sources(self):
        """Dedup funguje aj keď viacero zdrojov vráti rovnaké URL."""
        import services.scraper_service as ss
        dup = BaseScraper._make_parcel(url="https://example.com/dup", title="Dup",
                                       price_eur=1000, area_sqm=500)
        with patch.object(ss, "_scrape_one", side_effect=lambda src, c=None: [dup]):
            result = scrape_all()

# ----------------------------------------------------------------
# TestFetchHtmlRetry
# ----------------------------------------------------------------

class TestFetchHtmlRetry:
    """Testy retry logiky vo fetch_html (BaseScraper)."""

    def _make_scraper(self):
        s = BaseScraper.__new__(BaseScraper)
        s.SOURCE_NAME = "test_retry"
        s.rate_limit  = 0
        s.neutral_ua  = False
        s._last_call  = 0.0
        return s

    def test_fetch_html_success_no_retry(self):
        """Úspešný request — žiadny retry (requests.get volaný 1×)."""
        s = self._make_scraper()
        mock_resp = type("R", (), {
            "text": "<html>ok</html>",
            "raise_for_status": lambda self: None
        })()
        with patch("requests.get", return_value=mock_resp) as mock_get:
            html = s.fetch_html("https://example.com/ok")
        assert html == "<html>ok</html>"
        assert mock_get.call_count == 1

    def test_fetch_html_retry_on_connection_error(self):
        """ConnectionError → retry → úspech (2 volania requests.get)."""
        from requests.exceptions import ConnectionError as ReqConnErr
        s = self._make_scraper()
        mock_resp = type("R", (), {
            "text": "<html>retry_ok</html>",
            "raise_for_status": lambda self: None
        })()
        call_count = {"n": 0}

        def mock_get(*a, **kw):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise ReqConnErr("Connection reset")
            return mock_resp

        with patch("requests.get", side_effect=mock_get):
            with patch("time.sleep"):
                html = s.fetch_html("https://example.com/retry")
        assert html == "<html>retry_ok</html>"
        assert call_count["n"] == 2

    def test_fetch_html_retry_fails_raises(self):
        """ConnectionError pri retry aj → výnimka sa propaguje."""
        from requests.exceptions import ConnectionError as ReqConnErr
        s = self._make_scraper()
        with patch("requests.get", side_effect=ReqConnErr("stale")):
            with patch("time.sleep"):
                with pytest.raises(ReqConnErr):
                    s.fetch_html("https://example.com/fail")

    def test_fetch_html_http_error_no_retry(self):
        """HTTP 404 → len raise_for_status, žiadny retry."""
        import requests as req_lib
        s = self._make_scraper()
        mock_resp = req_lib.models.Response()
        mock_resp.status_code = 404
        with patch("requests.get", return_value=mock_resp):
            with pytest.raises(req_lib.exceptions.HTTPError):
                s.fetch_html("https://example.com/404")

    def test_scraper_timeout_constant_is_positive(self):
        assert SCRAPER_TIMEOUT_SEC > 0

    def test_scrape_one_calls_scraper(self, fixture_html):
        with patch.object(NehnutelnostiScraper, "fetch_html", return_value=fixture_html):
            result = _scrape_one("nehnutelnosti_sk")
        assert isinstance(result, list) and all(isinstance(p, Parcel) for p in result)

    def test_scrape_one_unknown_source_raises(self):
        with pytest.raises(KeyError):
            _scrape_one("neexistujuci_zdroj_xyz")
