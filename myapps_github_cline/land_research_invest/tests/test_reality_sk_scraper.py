"""Testy - Reality.sk scraper
================================
Testuje: parse_listing_page, extract_price, extract_area, extract_location.
100% offline - parser bezi na ulozenom HTML fixture.
"""

import pytest
import pathlib
from unittest.mock import patch

FIXTURE_L = pathlib.Path(__file__).parent / "fixtures" / "reality_sk_listing.html"
FIXTURE_D = pathlib.Path(__file__).parent / "fixtures" / "reality_sk_detail.html"

from services.scrapers.reality_sk_scraper import (
    RealitySkScraper,
    parse_listing_page,
    extract_price,
    extract_area,
    extract_location,
    SOURCE_NAME,
    SEARCH_URLS,
)
from services.scraper_service import SCRAPER_REGISTRY
from models.parcel import Parcel
from bs4 import BeautifulSoup


@pytest.fixture(scope="module")
def listing_html():
    return FIXTURE_L.read_text(encoding="utf-8", errors="ignore")


@pytest.fixture(scope="module")
def scraper():
    s = RealitySkScraper.__new__(RealitySkScraper)
    s.rate_limit = 0
    s.neutral_ua = True   # YELLOW zona
    s._last_call  = 0.0
    return s


# ----------------------------------------------------------------
# TestExtractPrice
# ----------------------------------------------------------------

class TestExtractPrice:
    def _div(self, html):
        return BeautifulSoup(html, "html.parser")

    def test_absolute_price(self):
        html = '<div class="offer"><p class="col-6 p-0 offer-price">1,678,170 \u20ac<small>390 \u20ac/m\u00b2 </small></p></div>'
        div = self._div(html).find("div", class_="offer")
        assert extract_price(div) == 1678170.0

    def test_price_dohodou_returns_zero(self):
        html = '<div class="offer"><p class="col-6 p-0 offer-price">100 \u20ac/m2100 \u20ac/m2</p></div>'
        div = self._div(html).find("div", class_="offer")
        assert extract_price(div) == 0.0

    def test_no_price_tag_returns_zero(self):
        html = '<div class="offer"><p>bez ceny</p></div>'
        div = self._div(html).find("div", class_="offer")
        assert extract_price(div) == 0.0

    def test_price_with_spaces(self):
        html = '<div class="offer"><p class="offer-price">299\xa0900 \u20ac</p></div>'
        div = self._div(html).find("div", class_="offer")
        assert extract_price(div) == 299900.0


# ----------------------------------------------------------------
# TestExtractArea
# ----------------------------------------------------------------

class TestExtractArea:
    def test_area_with_comma(self):
        assert extract_area("4,303 m\u00b2") == 4303.0

    def test_area_without_comma(self):
        assert extract_area("622 m\u00b2") == 622.0

    def test_area_m2(self):
        assert extract_area("750 m2") == 750.0

    def test_area_not_found(self):
        assert extract_area("bez rozmerov") == 0.0


# ----------------------------------------------------------------
# TestParseListingPage
# ----------------------------------------------------------------

class TestParseListingPage:
    def test_fixture_exists(self):
        assert FIXTURE_L.exists()

    def test_returns_24_parcels(self, listing_html):
        parcels = parse_listing_page(listing_html)
        assert len(parcels) == 24

    def test_all_have_url(self, listing_html):
        parcels = parse_listing_page(listing_html)
        for p in parcels:
            assert p.url and "reality.sk" in p.url

    def test_all_have_area(self, listing_html):
        parcels = parse_listing_page(listing_html)
        assert all(p.area_sqm > 0 for p in parcels)

    def test_all_have_location(self, listing_html):
        parcels = parse_listing_page(listing_html)
        assert all(p.location_text for p in parcels)

    def test_first_parcel_price(self, listing_html):
        parcels = parse_listing_page(listing_html)
        assert parcels[0].price_eur == 1678170.0

    def test_first_parcel_area(self, listing_html):
        parcels = parse_listing_page(listing_html)
        assert parcels[0].area_sqm == 4303.0

    def test_first_parcel_location(self, listing_html):
        parcels = parse_listing_page(listing_html)
        assert "Bratislava" in parcels[0].location_text

    def test_source_portal(self, listing_html):
        parcels = parse_listing_page(listing_html)
        assert all(p.source_portal == "reality_sk" for p in parcels)

    def test_no_duplicates(self, listing_html):
        parcels = parse_listing_page(listing_html)
        urls = [p.url for p in parcels]
        assert len(urls) == len(set(urls))

    def test_price_dohodou_is_zero(self, listing_html):
        parcels = parse_listing_page(listing_html)
        prices = [p.price_eur for p in parcels]
        # Niektoré sú 0 (cena dohodou) - overí že nie je falošná cena
        assert all(p == 0.0 or p >= 100 for p in prices)


# ----------------------------------------------------------------
# TestRealitySkScraperRegistry
# ----------------------------------------------------------------

class TestRealitySkScraperRegistry:
    def test_registered(self):
        assert "reality_sk" in SCRAPER_REGISTRY

    def test_class_correct(self):
        assert SCRAPER_REGISTRY["reality_sk"] is RealitySkScraper

    def test_source_name(self):
        assert RealitySkScraper.SOURCE_NAME == "reality_sk"

    def test_search_urls_not_empty(self):
        assert len(SEARCH_URLS) >= 4

    def test_parse_listings_on_fixture(self, scraper, listing_html):
        parcels = scraper.parse_listings(listing_html)
        assert isinstance(parcels, list)
        assert len(parcels) == 24

    def test_scrape_uses_all_pages(self, scraper, listing_html):
        with patch.object(RealitySkScraper, "fetch_html", return_value=listing_html):
            parcels = scraper.scrape()
        assert len(parcels) >= 1
        assert all(isinstance(p, Parcel) for p in parcels)
