"""Testy - SKE Drazobne vyhlasky scraper
=========================================
Testuje: _parse_listing_html, extract_detail_*, _detail_to_parcel.
100% offline - parsuje ulozene HTML fixture.
"""

import pytest
import pathlib

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "ske_drazobne_vyhlasky_listing.html"

from services.scrapers.ske_scraper import (
    SkeScraper,
    extract_detail_title,
    extract_detail_location,
    extract_detail_area,
    SOURCE_NAME,
)
from services.scraper_service import SCRAPER_REGISTRY
from models.parcel import Parcel
from bs4 import BeautifulSoup


@pytest.fixture(scope="module")
def listing_html():
    return FIXTURE.read_text(encoding="utf-8", errors="ignore")


@pytest.fixture(scope="module")
def scraper():
    s = SkeScraper.__new__(SkeScraper)
    s.rate_limit = 0
    s.neutral_ua = False
    s._last_call  = 0.0
    return s


class TestParseListingHtml:
    def test_fixture_exists(self):
        assert FIXTURE.exists()

    def test_returns_list(self, scraper, listing_html):
        assert isinstance(scraper._parse_listing_html(listing_html), list)

    def test_finds_19_nehnutelnosti(self, scraper, listing_html):
        assert len(scraper._parse_listing_html(listing_html)) == 19

    def test_entry_keys(self, scraper, listing_html):
        for e in scraper._parse_listing_html(listing_html):
            for k in ("ov_id", "cislo_ov", "cislo_ex", "datum", "exekutor"):
                assert k in e

    def test_ov_id_is_numeric(self, scraper, listing_html):
        for e in scraper._parse_listing_html(listing_html):
            assert e["ov_id"].isdigit()

    def test_first_entry_ov_id(self, scraper, listing_html):
        assert scraper._parse_listing_html(listing_html)[0]["ov_id"] == "4747440"

    def test_first_entry_datum(self, scraper, listing_html):
        assert scraper._parse_listing_html(listing_html)[0]["datum"] == "11.09.2026"

    def test_skips_hnutelny_majetok(self, scraper):
        html = ("<table><tr><th>h</th></tr>"
                "<tr><td>OV1</td><td>EX1</td><td>1.1.2026</td>"
                "<td>Hnuteln\u00fd majetok</td><td>podanie</td>"
                "<td>JUDr. X</td><td>1.1.2026</td></tr></table>")
        assert scraper._parse_listing_html(html) == []

    def test_empty_html_returns_empty(self, scraper):
        assert scraper._parse_listing_html("<html></html>") == []

    def test_page_url_format(self, scraper):
        url = scraper._page_url("https://ske.sk/drazobne-vyhlasky/", 2, "dv_page")
        assert "dv_page=2" in url


class TestExtractDetailFunctions:
    def test_area_m2(self):
        assert extract_detail_area("Vymera: 750 m2") == 750.0

    def test_area_m_squared(self):
        assert extract_detail_area("plocha 500 m\u00b2") == 500.0

    def test_area_not_found(self):
        assert extract_detail_area("bez rozmerov") == 0.0

    def test_location_kataster(self):
        assert "Senec" in extract_detail_location("Katastralne uzemie: Senec")

    def test_location_obec(self):
        assert "Pezinok" in extract_detail_location("Obec: Pezinok")

    def test_location_empty(self):
        assert extract_detail_location("ziadna") == ""

    def test_title_h1(self):
        soup = BeautifulSoup("<html><body><h1>Pozemok</h1></body></html>", "html.parser")
        assert "Pozemok" in extract_detail_title(soup)

    def test_title_empty(self):
        assert extract_detail_title(BeautifulSoup("<html></html>", "html.parser")) == ""


class TestDetailToParcel:
    def test_returns_parcel(self, scraper):
        html = ("<html><body><h1>Pozemok</h1>"
                "<p>Katastralne uzemie: Senec</p>"
                "<p>Vymera: 800 m2</p></body></html>")
        entry = {"ov_id": "123", "cislo_ov": "OV1", "cislo_ex": "EX1",
                 "datum": "1.1.2026", "exekutor": "JUDr. X", "druh": "podanie"}
        p = scraper._detail_to_parcel(html, "https://ske.sk/detail/?ov_podanie_id=123", entry)
        assert p is not None and isinstance(p, Parcel)
        assert p.area_sqm == 800.0
        assert "Senec" in p.location_text
        assert p.price_eur == 0.0

    def test_returns_none_for_empty(self, scraper):
        entry = {"ov_id": "x", "cislo_ov": "", "cislo_ex": "",
                 "datum": "", "exekutor": "", "druh": ""}
        assert scraper._detail_to_parcel("<html></html>", "https://ske.sk/x", entry) is None

    def test_price_always_zero(self, scraper):
        html = "<html><body><h1>Pozemok</h1><p>Obec: Trnava</p></body></html>"
        entry = {"ov_id": "y", "cislo_ov": "OV2", "cislo_ex": "EX2",
                 "datum": "2.2.2026", "exekutor": "JUDr. Y", "druh": "podanie"}
        p = scraper._detail_to_parcel(html, "https://ske.sk/y", entry)
        if p:
            assert p.price_eur == 0.0

    def test_description_contains_ex(self, scraper):
        html = "<html><body><h1>Pozemok</h1><p>Obec: Malacky</p></body></html>"
        entry = {"ov_id": "z", "cislo_ov": "OV3", "cislo_ex": "123EX456",
                 "datum": "3.3.2026", "exekutor": "JUDr. Z", "druh": "podanie"}
        p = scraper._detail_to_parcel(html, "https://ske.sk/z", entry)
        if p:
            assert "123EX456" in p.description


class TestSkeScraperRegistry:
    def test_registered(self):
        assert "ske_drazobne_vyhlasky" in SCRAPER_REGISTRY

    def test_class_correct(self):
        assert SCRAPER_REGISTRY["ske_drazobne_vyhlasky"] is SkeScraper

    def test_source_name(self):
        assert SkeScraper.SOURCE_NAME == "ske_drazobne_vyhlasky"

    def test_parse_listings_on_fixture(self, scraper, listing_html):
        entries = scraper.parse_listings(listing_html)
        assert isinstance(entries, list) and len(entries) == 19

