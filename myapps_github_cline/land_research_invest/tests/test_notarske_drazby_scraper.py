"""Testy - Notarske drazby scraper
====================================
Testuje: _parse_listing_html, extract_detail_*, _detail_to_parcel.
100% offline - parsuje ulozene HTML fixture.
"""

import re
import pytest
import pathlib

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "notarske_drazby_listing.html"

from services.scrapers.notarske_drazby_scraper import (
    NotarskeDrazbyaScraper,
    extract_detail_title,
    extract_detail_location,
    extract_detail_price,
    extract_detail_area,
    SOURCE_NAME,
    BASE_DOMAIN,
)
from services.scraper_service import SCRAPER_REGISTRY
from models.parcel import Parcel


@pytest.fixture(scope="module")
def listing_html():
    return FIXTURE.read_text(encoding="utf-8", errors="ignore")


@pytest.fixture(scope="module")
def scraper():
    s = NotarskeDrazbyaScraper.__new__(NotarskeDrazbyaScraper)
    s.rate_limit = 0
    s.neutral_ua = False
    s._last_call  = 0.0
    return s



# ----------------------------------------------------------------
# TestParseListingHtml
# ----------------------------------------------------------------

class TestParseListingHtml:
    def test_fixture_exists(self):
        assert FIXTURE.exists()

    def test_returns_list(self, scraper, listing_html):
        assert isinstance(scraper._parse_listing_html(listing_html), list)

    def test_finds_drazby(self, scraper, listing_html):
        entries = scraper._parse_listing_html(listing_html)
        assert len(entries) >= 5

    def test_entry_has_required_keys(self, scraper, listing_html):
        for e in scraper._parse_listing_html(listing_html):
            for k in ("act_id", "ncr", "drazobnik", "typ"):
                assert k in e

    def test_act_id_is_hex(self, scraper, listing_html):
        for e in scraper._parse_listing_html(listing_html):
            assert re.match(r"^[a-f0-9]+$", e["act_id"], re.I)

    def test_empty_html_returns_empty(self, scraper):
        assert scraper._parse_listing_html("<html></html>") == []

    def test_skips_upustenie(self, scraper):
        html = ("<table><tr><th>h</th></tr>"
                "<tr><td>1</td><td>X</td><td>N</td>"
                "<td>Upustenie od drazby</td><td></td><td>1.1.2026</td>"
                "<td><a href=\"drazba?actId=abc123\">link</a></td></tr></table>")
        assert scraper._parse_listing_html(html) == []

    def test_includes_oznamenie(self, scraper):
        html = ("<table><tr><th>h</th></tr>"
                "<tr><td>999/2026</td><td>LICITOR a.s.</td><td>Banka</td>"
                "<td>Oznamenie o drazbe</td><td></td><td>15.10.2026</td>"
                "<td><a href=\"drazba?actId=abc123def456\">link</a></td></tr></table>")
        entries = scraper._parse_listing_html(html)
        assert len(entries) == 1
        assert entries[0]["act_id"] == "abc123def456"
        assert entries[0]["ncr"] == "999/2026"


# ----------------------------------------------------------------
# TestExtractDetailFunctions
# ----------------------------------------------------------------

class TestExtractDetailFunctions:
    def test_price_eur_symbol(self):
        assert extract_detail_price("Najnizsie podanie: 15.000,- \u20ac") == 15000.0

    def test_price_eur_word(self):
        assert extract_detail_price("Cena: 25 000 EUR") == 25000.0

    def test_price_not_found(self):
        assert extract_detail_price("Ziadna cena") == 0.0

    def test_area_m2(self):
        assert extract_detail_area("Vymera pozemku: 750 m2") == 750.0

    def test_area_m_space_2(self):
        assert extract_detail_area("Vymera: 1200 m 2") == 1200.0

    def test_area_not_found(self):
        assert extract_detail_area("bez rozmerov") == 0.0

    def test_location_obec(self):
        assert "Senec" in extract_detail_location("Obec: Senec, okres Senec")

    def test_location_mesto(self):
        assert "Malacky" in extract_detail_location("Mesto: Malacky")

    def test_location_empty(self):
        assert extract_detail_location("ziadna lokalita") == ""


# ----------------------------------------------------------------
# TestDetailToParcel
# ----------------------------------------------------------------

class TestDetailToParcel:
    def test_returns_parcel(self, scraper):
        html = ("<html><body><h1>Predmet drazby: pozemok</h1>"
                "<p>Obec: Senec</p><p>Vymera: 800 m2</p>"
                "<p>Najnizsie podanie: 20.000,- \u20ac</p></body></html>")
        entry = {"act_id": "abc", "ncr": "100/2026", "drazobnik": "LICITOR",
                 "typ": "Oznamenie o drazbe", "datum": "15.10.2026"}
        p = scraper._detail_to_parcel(html, "https://notar.sk/drazba?actId=abc", entry)
        assert p is not None and isinstance(p, Parcel)
        assert p.price_eur == 20000.0
        assert p.area_sqm  == 800.0
        assert "Senec" in p.location_text

    def test_returns_none_for_empty(self, scraper):
        entry = {"act_id": "x", "ncr": "", "drazobnik": "", "typ": "", "datum": ""}
        assert scraper._detail_to_parcel("<html></html>", "https://notar.sk/x", entry) is None

    def test_source_portal(self, scraper):
        html = "<html><body><h1>Predmet</h1><p>Obec: Trnava</p></body></html>"
        entry = {"act_id": "y", "ncr": "200/2026", "drazobnik": "X",
                 "typ": "Oznamenie", "datum": "1.1.2026"}
        p = scraper._detail_to_parcel(html, "https://notar.sk/y", entry)
        if p:
            assert p.source_portal == "notarske_drazby"

    def test_description_contains_ncr(self, scraper):
        html = "<html><body><h1>Pozemok</h1><p>Obec: Pezinok</p></body></html>"
        entry = {"act_id": "z", "ncr": "999/2026", "drazobnik": "Y",
                 "typ": "Oznamenie", "datum": "5.5.2026"}
        p = scraper._detail_to_parcel(html, "https://notar.sk/z", entry)
        if p:
            assert "999/2026" in p.description


# ----------------------------------------------------------------
# TestNotarskeDrazbyScraperRegistry
# ----------------------------------------------------------------

class TestNotarskeDrazbyScraperRegistry:
    def test_registered_in_registry(self):
        assert "notarske_drazby" in SCRAPER_REGISTRY

    def test_registry_class_correct(self):
        assert SCRAPER_REGISTRY["notarske_drazby"] is NotarskeDrazbyaScraper

    def test_source_name(self):
        assert NotarskeDrazbyaScraper.SOURCE_NAME == "notarske_drazby"

    def test_parse_listings_on_fixture(self, scraper, listing_html):
        entries = scraper.parse_listings(listing_html)
        assert isinstance(entries, list) and len(entries) >= 5

    def test_base_domain(self):
        assert BASE_DOMAIN == "https://www.notar.sk"
