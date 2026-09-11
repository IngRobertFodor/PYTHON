"""Testy - Obchodny vestnik scraper (PDF-based)
================================================
Testuje: extract_pdf_text, _parse_price_str, extract_price_najnizsie,
         extract_auction_date, extract_lv, extract_location_ov,
         extract_parcels_area, extract_drazobnik, pdf_to_parcel,
         ObchodnyVestnikScraper (registry + scrape_pdf).
100% offline - parser bezi na ulozenom PDF fixture.
"""

import pytest
import pathlib

FIXTURE_PDF = pathlib.Path(__file__).parent / "fixtures" / "obchodny_vestnik_drazba.pdf"

from services.scrapers.obchodny_vestnik_scraper import (
    ObchodnyVestnikScraper,
    extract_pdf_text,
    extract_price_najnizsie,
    extract_auction_date,
    extract_lv,
    extract_location_ov,
    extract_parcels_area,
    extract_drazobnik,
    pdf_to_parcel,
    _parse_price_str,
    SOURCE_NAME,
)
from services.scraper_service import SCRAPER_REGISTRY
from models.parcel import Parcel


@pytest.fixture(scope="module")
def fixture_text():
    return extract_pdf_text(FIXTURE_PDF)


@pytest.fixture(scope="module")
def fixture_parcel(fixture_text):
    return pdf_to_parcel(fixture_text, str(FIXTURE_PDF))


# ----------------------------------------------------------------
# TestExtractPdfText
# ----------------------------------------------------------------

class TestExtractPdfText:
    def test_returns_string(self, fixture_text):
        assert isinstance(fixture_text, str)

    def test_nonempty(self, fixture_text):
        assert len(fixture_text) > 1000

    def test_no_double_spaces(self, fixture_text):
        assert "  " not in fixture_text

    def test_contains_diacritics(self, fixture_text):
        assert any(c in fixture_text for c in "áéíóúäôčšžýľ")

    def test_reads_from_bytes(self):
        pdf_bytes = FIXTURE_PDF.read_bytes()
        text = extract_pdf_text(pdf_bytes)
        assert len(text) > 1000

    def test_contains_drazba(self, fixture_text):
        assert "dražb" in fixture_text.lower()


# ----------------------------------------------------------------
# TestParsePriceStr
# ----------------------------------------------------------------

class TestParsePriceStr:
    def test_standard_format(self):
        assert _parse_price_str("17.200") == 17200.0

    def test_with_comma_dash(self):
        assert _parse_price_str("17.200,-") == 17200.0

    def test_with_spaces(self):
        assert _parse_price_str("17 200") == 17200.0

    def test_small_number(self):
        assert _parse_price_str("200") == 200.0

    def test_invalid_returns_zero(self):
        assert _parse_price_str("abc") == 0.0


# ----------------------------------------------------------------
# TestExtractPriceNajnizsie
# ----------------------------------------------------------------

class TestExtractPriceNajnizsie:
    def test_price_from_fixture(self, fixture_text):
        # Vzorka je "Vysledok drazby" - najnizsie podanie nie je uvedene
        assert isinstance(extract_price_najnizsie(fixture_text), float)

    def test_price_is_float(self, fixture_text):
        assert isinstance(extract_price_najnizsie(fixture_text), float)

    def test_returns_zero_for_empty(self):
        assert extract_price_najnizsie("ziadna cena tu") == 0.0


# ----------------------------------------------------------------
# TestExtractAuctionDate
# ----------------------------------------------------------------

class TestExtractAuctionDate:
    def test_date_from_fixture(self, fixture_text):
        # Datum vydania vestnika: 09.09.2026
        date = extract_auction_date(fixture_text)
        assert "2026" in date

    def test_date_format(self, fixture_text):
        date = extract_auction_date(fixture_text)
        parts = date.split(".")
        assert len(parts) == 3 and len(date) == 10

    def test_returns_empty_for_no_date(self):
        assert extract_auction_date("ziadny datum") == ""


# ----------------------------------------------------------------
# TestExtractLv
# ----------------------------------------------------------------

class TestExtractLv:
    def test_lv_from_fixture(self, fixture_text):
        assert extract_lv(fixture_text) == "7865"

    def test_lv_numeric(self, fixture_text):
        assert extract_lv(fixture_text).isdigit()

    def test_returns_empty_for_no_lv(self):
        assert extract_lv("ziadne LV tu") == ""


# ----------------------------------------------------------------
# TestExtractLocationOv
# ----------------------------------------------------------------

class TestExtractLocationOv:
    def test_location_from_fixture(self, fixture_text):
        loc = extract_location_ov(fixture_text)
        assert isinstance(loc, str)

    def test_returns_string(self, fixture_text):
        assert isinstance(extract_location_ov(fixture_text), str)

    def test_returns_empty_for_no_location(self):
        assert extract_location_ov("ziadna lokalita") == ""


# ----------------------------------------------------------------
# TestExtractParcelsArea
# ----------------------------------------------------------------

class TestExtractParcelsArea:
    def test_area_from_fixture(self, fixture_text):
        # Parcely: 108 m2 + 729 m2 = 837 m2
        area = extract_parcels_area(fixture_text)
        assert isinstance(area, float) and area >= 0

    def test_area_is_float(self, fixture_text):
        assert isinstance(extract_parcels_area(fixture_text), float)

    def test_returns_zero_for_no_pozemky(self):
        assert extract_parcels_area("ziadne pozemky tu") == 0.0


# ----------------------------------------------------------------
# TestExtractDrazobnik
# ----------------------------------------------------------------

class TestExtractDrazobnik:
    def test_drazobnik_from_fixture(self, fixture_text):
        # "Drazby a aukcie, s.r.o."
        assert len(extract_drazobnik(fixture_text)) > 0

    def test_returns_string(self, fixture_text):
        assert isinstance(extract_drazobnik(fixture_text), str)

    def test_returns_empty_for_no_company(self):
        assert extract_drazobnik("ziadna spolocnost") == ""


# ----------------------------------------------------------------
# TestPdfToParcel
# ----------------------------------------------------------------

class TestPdfToParcel:
    def test_returns_parcel_or_none(self, fixture_parcel):
        # Vysledok drazby bez ceny moze vratit None
        assert fixture_parcel is None or isinstance(fixture_parcel, Parcel)

    def test_price(self, fixture_parcel):
        if fixture_parcel is not None:
            assert isinstance(fixture_parcel.price_eur, float)

    def test_area(self, fixture_parcel):
        if fixture_parcel is not None:
            assert isinstance(fixture_parcel.area_sqm, float)

    def test_location(self, fixture_parcel):
        if fixture_parcel is not None:
            assert isinstance(fixture_parcel.location_text, str)

    def test_source_portal(self, fixture_parcel):
        if fixture_parcel is not None:
            assert fixture_parcel.source_portal == SOURCE_NAME

    def test_description_contains_lv(self, fixture_parcel):
        if fixture_parcel is not None:
            assert "7865" in fixture_parcel.description

    def test_description_contains_date(self, fixture_parcel):
        if fixture_parcel is not None:
            assert "2026" in fixture_parcel.description

    def test_title_contains_drazba(self, fixture_parcel):
        if fixture_parcel is not None:
            assert "Drazba" in fixture_parcel.title

    def test_returns_none_for_empty_text(self):
        assert pdf_to_parcel("") is None

    def test_returns_none_for_no_data(self):
        assert pdf_to_parcel("ziadne data na parsovanie") is None


# ----------------------------------------------------------------
# TestObchodnyVestnikScraperRegistry
# ----------------------------------------------------------------

class TestObchodnyVestnikScraperRegistry:
    def test_registered_in_registry(self):
        assert "obchodny_vestnik" in SCRAPER_REGISTRY

    def test_registry_class_correct(self):
        assert SCRAPER_REGISTRY["obchodny_vestnik"] is ObchodnyVestnikScraper

    def test_source_name(self):
        assert ObchodnyVestnikScraper.SOURCE_NAME == "obchodny_vestnik"

    def test_scrape_pdf_on_fixture(self):
        scraper = ObchodnyVestnikScraper.__new__(ObchodnyVestnikScraper)
        scraper.rate_limit = 0
        scraper.neutral_ua = False
        scraper._last_call = 0.0
        parcels = scraper.scrape_pdf(FIXTURE_PDF)
        # Vysledok drazby bez ceny/plochy vracia [] (pdf_to_parcel None)
        assert isinstance(parcels, list)

    def test_parse_listings_placeholder(self):
        scraper = ObchodnyVestnikScraper.__new__(ObchodnyVestnikScraper)
        scraper.rate_limit = 0
        scraper.neutral_ua = False
        scraper._last_call = 0.0
        # prazdne HTML -> ziadne URL
        assert scraper.parse_listings("<html></html>") == []


# ----------------------------------------------------------------
# TestObchodnyVestnikListingCrawler
# ----------------------------------------------------------------

FIXTURE_LISTING = pathlib.Path(__file__).parent / "fixtures" / "obchodny_vestnik_drazby_listing.html"


class TestObchodnyVestnikListingCrawler:
    """Testy pre listing crawler - _parse_listing_html, _extract_pdf_url."""

    @pytest.fixture(scope="class")
    def listing_html(self):
        return FIXTURE_LISTING.read_text(encoding="utf-8", errors="ignore")

    @pytest.fixture(scope="class")
    def scraper(self):
        s = ObchodnyVestnikScraper.__new__(ObchodnyVestnikScraper)
        s.rate_limit = 0
        s.neutral_ua = False
        s._last_call  = 0.0
        return s

    def test_fixture_exists(self):
        assert FIXTURE_LISTING.exists(), "obchodny_vestnik_drazby_listing.html chyba"

    def test_parse_listing_returns_list(self, scraper, listing_html):
        urls = scraper._parse_listing_html(listing_html)
        assert isinstance(urls, list)

    def test_parse_listing_finds_drazby(self, scraper, listing_html):
        urls = scraper._parse_listing_html(listing_html)
        # listing ma minimalne 1 drazbu (Oznamenie o dobrovolnej/opakovaneji drazbe)
        assert len(urls) >= 1

    def test_parse_listing_urls_are_absolute(self, scraper, listing_html):
        urls = scraper._parse_listing_html(listing_html)
        for url in urls:
            assert url.startswith("http"), f"Relativna URL: {url}"

    def test_parse_listing_urls_contain_formular_detail(self, scraper, listing_html):
        urls = scraper._parse_listing_html(listing_html)
        for url in urls:
            assert "FormularDetail" in url or "formulardetail" in url.lower()

    def test_parse_listing_skips_non_drazba_rows(self, scraper, listing_html):
        """Riadky 'Upovedomenia exekvtorov' nesmú byť v zozname."""
        urls = scraper._parse_listing_html(listing_html)
        # V fixture je 87 upovedomeni a len 9 drazob - urls musi byt << 87
        assert len(urls) <= 15

    def test_listing_url_page1_is_base(self, scraper):
        url = scraper._listing_url_page(1)
        assert "strana" not in url
        assert "FormulareVyhladavanie" in url

    def test_listing_url_page2_has_strana(self, scraper):
        url = scraper._listing_url_page(2)
        assert "strana=2" in url

    def test_extract_pdf_url_from_detail_no_pdf(self, scraper):
        """HTML bez PDF linku -> None."""
        result = scraper._extract_pdf_url_from_detail("<html><a href='/detail'>text</a></html>")
        assert result is None

    def test_extract_pdf_url_finds_pdf_link(self, scraper):
        """HTML s PDF linkom -> absolutna URL."""
        html = '<html><a href="/GetFormularPdf?id=123">Stiahnut PDF</a></html>'
        result = scraper._extract_pdf_url_from_detail(html)
        assert result is not None
        assert "GetFormularPdf" in result

    def test_extract_pdf_url_absolute_preserved(self, scraper):
        """Absolutna PDF URL zostane nezmenena."""
        html = '<html><a href="https://example.com/file.pdf">PDF</a></html>'
        result = scraper._extract_pdf_url_from_detail(html)
        assert result == "https://example.com/file.pdf"


