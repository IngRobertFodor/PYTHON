"""Testy - SPF scraper (Slovensky pozemkovy fond)
==================================================
Testuje: parse_index (HTML), extract_pdf_text_spf, parse_pdf_pozemky,
         extract_okres_obec_from_pdf_url, SpfScraper (registry).
100% offline - bezi na fixtures spf_listing.html + spf_detail.pdf.
"""

import pytest
import pathlib

FIX_HTML = pathlib.Path(__file__).parent / "fixtures" / "spf_listing.html"
FIX_PDF  = pathlib.Path(__file__).parent / "fixtures" / "spf_detail.pdf"

from services.scrapers.spf_scraper import (
    SpfScraper,
    parse_index,
    parse_pdf_pozemky,
    extract_pdf_text_spf,
    extract_okres_obec_from_pdf_url,
    SOURCE_NAME,
    DRUH_KODY,
)
from services.scraper_service import SCRAPER_REGISTRY
from models.parcel import Parcel


@pytest.fixture(scope="module")
def fixture_html():
    return FIX_HTML.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def fixture_index(fixture_html):
    return parse_index(fixture_html)


@pytest.fixture(scope="module")
def fixture_parcels():
    return parse_pdf_pozemky(FIX_PDF, "Banska Stiavnica", "Dekys")


# ----------------------------------------------------------------
# TestParseIndex
# ----------------------------------------------------------------

class TestParseIndex:
    def test_returns_list(self, fixture_index):
        assert isinstance(fixture_index, list)

    def test_30_entries(self, fixture_index):
        assert len(fixture_index) == 30

    def test_entry_has_keys(self, fixture_index):
        for e in fixture_index:
            assert "okres" in e and "obec" in e and "pdf_url" in e

    def test_first_entry_okres(self, fixture_index):
        assert fixture_index[0]["okres"] == "Malacky"

    def test_first_entry_obec(self, fixture_index):
        assert fixture_index[0]["obec"] == "Pernek"

    def test_pdf_url_contains_uzemneplany(self, fixture_index):
        assert all("uzemneplany" in e["pdf_url"] for e in fixture_index)

    def test_pdf_url_ends_with_pdf(self, fixture_index):
        assert all(e["pdf_url"].endswith(".pdf") for e in fixture_index)

    def test_empty_html_returns_empty(self):
        assert parse_index("<html><body></body></html>") == []


# ----------------------------------------------------------------
# TestExtractPdfTextSpf
# ----------------------------------------------------------------

class TestExtractPdfTextSpf:
    def test_returns_list(self):
        assert isinstance(extract_pdf_text_spf(FIX_PDF), list)

    def test_15_pages(self):
        assert len(extract_pdf_text_spf(FIX_PDF)) == 15

    def test_pages_nonempty(self):
        assert all(len(p) > 10 for p in extract_pdf_text_spf(FIX_PDF))

    def test_reads_bytes(self):
        assert len(extract_pdf_text_spf(FIX_PDF.read_bytes())) == 15

    def test_contains_diacritics(self):
        full = " ".join(extract_pdf_text_spf(FIX_PDF))
        assert any(c in full for c in "\u00e1\u00e9\u00ed\u00f3\u00fa\u00e4\u00f4\u010d\u0161\u017e\u00fd\u013e")


# ----------------------------------------------------------------
# TestParsePdfPozemky
# ----------------------------------------------------------------

class TestParsePdfPozemky:
    def test_returns_list(self, fixture_parcels):
        assert isinstance(fixture_parcels, list)

    def test_parses_many_parcels(self, fixture_parcels):
        assert len(fixture_parcels) > 50

    def test_first_parcel_is_parcel(self, fixture_parcels):
        assert isinstance(fixture_parcels[0], Parcel)

    def test_first_parcel_number(self, fixture_parcels):
        assert "35" in fixture_parcels[0].title

    def test_first_parcel_area(self, fixture_parcels):
        assert fixture_parcels[0].area_sqm == 347.0

    def test_source_portal(self, fixture_parcels):
        assert all(p.source_portal == SOURCE_NAME for p in fixture_parcels)

    def test_price_is_zero(self, fixture_parcels):
        assert all(p.price_eur == 0.0 for p in fixture_parcels)

    def test_area_positive(self, fixture_parcels):
        assert all(p.area_sqm > 0 for p in fixture_parcels)

    def test_location_nonempty(self, fixture_parcels):
        assert all(len(p.location_text) > 0 for p in fixture_parcels)

    def test_description_contains_spf(self, fixture_parcels):
        assert all("SPF" in p.description for p in fixture_parcels)

    def test_description_contains_parc(self, fixture_parcels):
        assert "Parc.c.:" in fixture_parcels[0].description

    def test_druh_in_description(self, fixture_parcels):
        druh_vals = list(DRUH_KODY.values())
        assert any(any(d in p.description for d in druh_vals) for p in fixture_parcels[:10])


# ----------------------------------------------------------------
# TestExtractOkresObecFromPdfUrl
# ----------------------------------------------------------------

class TestExtractOkresObecFromPdfUrl:
    def test_malacky_pernek(self):
        url = "https://pozfond.sk/wp-content/uploads/uzemneplany/Malacky_Pernek_Pernek.pdf"
        okres, obec = extract_okres_obec_from_pdf_url(url)
        assert okres == "Malacky" and obec == "Pernek"

    def test_banska_stiavnica(self):
        url = "https://pozfond.sk/wp-content/uploads/uzemneplany/Banska-Stiavnica_Dekys_Dekys.pdf"
        okres, obec = extract_okres_obec_from_pdf_url(url)
        assert "Banska" in okres and "Dekys" in obec

    def test_invalid_url_returns_empty(self):
        o, b = extract_okres_obec_from_pdf_url("https://example.com/no.pdf")
        assert o == "" and b == ""


# ----------------------------------------------------------------
# TestSpfScraperRegistry
# ----------------------------------------------------------------

class TestSpfScraperRegistry:
    def test_registered_in_registry(self):
        assert "spf" in SCRAPER_REGISTRY

    def test_registry_class_correct(self):
        assert SCRAPER_REGISTRY["spf"] is SpfScraper

    def test_source_name(self):
        assert SpfScraper.SOURCE_NAME == "spf"

    def test_scrape_pdf_on_fixture(self):
        scraper = SpfScraper.__new__(SpfScraper)
        scraper.rate_limit = 0
        scraper.neutral_ua = False
        scraper._last_call = 0.0
        parcels = scraper.scrape_pdf(FIX_PDF, "Banska Stiavnica", "Dekys")
        assert len(parcels) > 50
        assert all(isinstance(p, Parcel) for p in parcels)

    def test_scrape_pdf_correct_first_parcel(self):
        scraper = SpfScraper.__new__(SpfScraper)
        scraper.rate_limit = 0
        scraper.neutral_ua = False
        scraper._last_call = 0.0
        parcels = scraper.scrape_pdf(FIX_PDF, "Banska Stiavnica", "Dekys")
        assert parcels[0].area_sqm == 347.0
        assert parcels[0].price_eur == 0.0

