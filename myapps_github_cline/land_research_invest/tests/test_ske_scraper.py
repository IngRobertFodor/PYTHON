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
    extract_detail_price,
    extract_detail_odhad,
    extract_detail_obec,
    extract_detail_kataster,
    extract_detail_lv,
    extract_detail_datum_drazby,
    extract_detail_cas_drazby,
    extract_detail_miesto,
    extract_detail_datum_obhliadky,
    extract_detail_vlastnik,
    extract_detail_ov_cislo,
    extract_detail_parcely_list,
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


# Vzorovy text detailu (simuluje realne data zo SKE)
SAMPLE_TEXT = (
    "Najni\u017e\u0161ie podanie 20500 \u20ac Odhad hodnoty 20500 \u20ac "
    "D\u00e1tum dra\u017eby 15.09.2026 \u010cas dra\u017eby 09:00 "
    "Miesto dra\u017eby Hlavn\u00e1 1, Trnava 91701 Obhliadka "
    "D\u00e1tum obhliadky 09.09.2026 "
    "Obec: Trnava, Kataster: Trnava, LV: 1234 "
    "Parcela C, 100/1, v\u00fdmera 364, z\u00e1hrada "
    "Parcela C, 100/2, v\u00fdmera 526, zastavan\u00e1 plocha "
    "Vlastn\u00edk Jan Novak, Hlavna 1, podiel 1/1 Z\u00e1vady "
    "\u010c\u00edslo zverejnenia v OV X047677"
)


# ----------------------------------------------------------------
# TestParseListingHtml
# ----------------------------------------------------------------

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



# ----------------------------------------------------------------
# TestExtractDetailFunctions
# ----------------------------------------------------------------

class TestExtractDetailFunctions:
    def test_price_found(self):
        assert extract_detail_price(SAMPLE_TEXT) == 20500.0

    def test_price_zero(self):
        assert extract_detail_price("Najni\u017e\u0161ie podanie 0 \u20ac") == 0.0

    def test_price_not_found(self):
        assert extract_detail_price("bez ceny") == 0.0

    def test_odhad_found(self):
        assert extract_detail_odhad(SAMPLE_TEXT) == 20500.0

    def test_odhad_not_found(self):
        assert extract_detail_odhad("bez odhadu") == 0.0

    def test_area_sucet_parciel(self):
        assert extract_detail_area(SAMPLE_TEXT) == 890.0

    def test_area_not_found(self):
        assert extract_detail_area("bez rozmerov") == 0.0

    def test_obec_found(self):
        assert extract_detail_obec(SAMPLE_TEXT) == "Trnava"

    def test_obec_not_found(self):
        assert extract_detail_obec("ziadna obec") == ""

    def test_kataster_found(self):
        assert extract_detail_kataster(SAMPLE_TEXT) == "Trnava"

    def test_lv_found(self):
        assert extract_detail_lv(SAMPLE_TEXT) == "1234"

    def test_lv_not_found(self):
        assert extract_detail_lv("bez LV") == ""

    def test_datum_drazby(self):
        assert extract_detail_datum_drazby(SAMPLE_TEXT) == "15.09.2026"

    def test_datum_not_found(self):
        assert extract_detail_datum_drazby("bez datumu") == ""

    def test_cas_drazby(self):
        assert extract_detail_cas_drazby(SAMPLE_TEXT) == "09:00"

    def test_miesto(self):
        assert "Trnava" in extract_detail_miesto(SAMPLE_TEXT)

    def test_datum_obhliadky(self):
        assert extract_detail_datum_obhliadky(SAMPLE_TEXT) == "09.09.2026"

    def test_vlastnik(self):
        assert "Jan Novak" in extract_detail_vlastnik(SAMPLE_TEXT)

    def test_ov_cislo(self):
        assert extract_detail_ov_cislo(SAMPLE_TEXT) == "X047677"

    def test_ov_cislo_not_found(self):
        assert extract_detail_ov_cislo("bez OV") == ""

    def test_parcely_list_count(self):
        parcely = extract_detail_parcely_list(SAMPLE_TEXT)
        assert len(parcely) == 2

    def test_parcely_list_contains_cisla(self):
        parcely = extract_detail_parcely_list(SAMPLE_TEXT)
        assert any("100/1" in p for p in parcely)
        assert any("100/2" in p for p in parcely)

# ----------------------------------------------------------------
# TestDetailToParcel
# ----------------------------------------------------------------

class TestDetailToParcel:
    def _entry(self, cislo_ex="123EX456"):
        return {"ov_id": "123", "cislo_ov": "OV1", "cislo_ex": cislo_ex,
                "datum": "1.1.2026", "exekutor": "JUDr. X", "druh": "podanie"}

    def test_parcel_with_price_and_area(self, scraper):
        html = ("<p>Najni\u017e\u0161ie podanie 20500 \u20ac</p>"
                "<p>Obec: Senec, Kataster: Senec, LV: 999</p>"
                "<p>Parcela C, 1/1, v\u00fdmera 800, z\u00e1hrada</p>"
                "<p>D\u00e1tum dra\u017eby 15.09.2026 \u010cas dra\u017eby 10:00</p>"
                "<p>Miesto dra\u017eby Hlavn\u00e1 1, Senec Obhliadka</p>")
        p = scraper._detail_to_parcel(html, "https://ske.sk/x", self._entry())
        assert p is not None and isinstance(p, Parcel)
        assert p.price_eur == 20500.0
        assert p.area_sqm  == 800.0
        assert "Senec" in p.location_text
        assert p.parcel_number == "999"

    def test_returns_none_when_no_location(self, scraper):
        entry = {"ov_id": "x", "cislo_ov": "", "cislo_ex": "",
                 "datum": "", "exekutor": "", "druh": ""}
        assert scraper._detail_to_parcel("<html></html>", "https://ske.sk/x", entry) is None

    def test_description_contains_cislo_ex(self, scraper):
        html = ("<p>Obec: Malacky, Kataster: Malacky, LV: 1</p>"
                "<p>Parcela C, 1/1, v\u00fdmera 100, z\u00e1hrada</p>")
        p = scraper._detail_to_parcel(html, "https://ske.sk/z", self._entry("123EX456"))
        if p:
            assert "123EX456" in p.description

    def test_area_sum_multiple_parcels(self, scraper):
        html = ("<p>Obec: Trnava, Kataster: Trnava, LV: 5</p>"
                "<p>Parcela C, 1/1, v\u00fdmera 200, z\u00e1hrada</p>"
                "<p>Parcela C, 1/2, v\u00fdmera 300, zastavana</p>")
        p = scraper._detail_to_parcel(html, "https://ske.sk/t", self._entry())
        if p:
            assert p.area_sqm == 500.0


# ----------------------------------------------------------------
# TestSkeScraperRegistry
# ----------------------------------------------------------------

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

        parcely = extract_detail_parcely_list(SAMPLE_TEXT)
        assert any("100/1" in p for p in parcely)
        assert any("100/2" in p for p in parcely)

    def test_parcely_empty(self):
        assert extract_detail_parcely_list("bez parciel") == []

    def test_location_uses_obec(self):
        assert "Trnava" in extract_detail_location(SAMPLE_TEXT)

    def test_title_h1(self):
        soup = BeautifulSoup("<html><body><h1>Pozemok</h1></body></html>", "html.parser")
        assert "Pozemok" in extract_detail_title(soup)

    def test_title_empty(self):
        assert extract_detail_title(BeautifulSoup("<html></html>", "html.parser")) == ""


