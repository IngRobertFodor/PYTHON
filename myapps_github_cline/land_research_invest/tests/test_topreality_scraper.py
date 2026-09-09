"""Testy - Topreality.sk scraper
==================================
Testuje: extract_jsonld_blocks, find_listing_block, find_breadcrumb_block,
         extract_price_from_html, extract_area_from_text,
         extract_location_from_breadcrumb, listing_to_parcel, TopRealityScraper.
100% offline - parser bezi na ulozenom HTML fixture.
"""

import pytest
import pathlib
from unittest.mock import patch

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "topreality_sk_detail.html"

from services.scrapers.topreality_scraper import (
    TopRealityScraper,
    extract_jsonld_blocks,
    find_listing_block,
    find_breadcrumb_block,
    extract_price_from_html,
    extract_area_from_text,
    extract_location_from_breadcrumb,
    listing_to_parcel,
    SOURCE_NAME,
)
from services.scraper_service import SCRAPER_REGISTRY
from models.parcel import Parcel


@pytest.fixture(scope="module")
def fixture_html():
    return FIXTURE.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def fixture_blocks(fixture_html):
    return extract_jsonld_blocks(fixture_html)


@pytest.fixture(scope="module")
def fixture_parcel(fixture_blocks, fixture_html):
    return listing_to_parcel(fixture_blocks, fixture_html)


# ----------------------------------------------------------------
# TestExtractJsonldBlocks
# ----------------------------------------------------------------

class TestExtractJsonldBlocks:
    def test_returns_list(self, fixture_blocks):
        assert isinstance(fixture_blocks, list)

    def test_four_blocks_found(self, fixture_blocks):
        assert len(fixture_blocks) == 4

    def test_blocks_are_dicts(self, fixture_blocks):
        assert all(isinstance(b, dict) for b in fixture_blocks)

    def test_has_organization_block(self, fixture_blocks):
        types = [b.get("@type", "") for b in fixture_blocks]
        assert "Organization" in types

    def test_has_real_estate_listing(self, fixture_blocks):
        types = [b.get("@type", "") for b in fixture_blocks]
        assert "RealEstateListing" in types

    def test_has_breadcrumb_list(self, fixture_blocks):
        types = [b.get("@type", "") for b in fixture_blocks]
        assert "BreadcrumbList" in types

    def test_empty_html_returns_empty_list(self):
        assert extract_jsonld_blocks("<html><body></body></html>") == []

    def test_invalid_json_is_skipped(self):
        html = '<script type="application/ld+json">{invalid json}</script>'
        assert extract_jsonld_blocks(html) == []


# ----------------------------------------------------------------
# TestFindListingBlock
# ----------------------------------------------------------------

class TestFindListingBlock:
    def test_finds_real_estate_listing(self, fixture_blocks):
        b = find_listing_block(fixture_blocks)
        assert b is not None
        assert b.get("@type") == "RealEstateListing"

    def test_returns_none_for_empty(self):
        assert find_listing_block([]) is None

    def test_returns_none_when_no_match(self):
        blocks = [{"@type": "Organization"}, {"@type": "Website"}]
        assert find_listing_block(blocks) is None

    def test_listing_has_name(self, fixture_blocks):
        b = find_listing_block(fixture_blocks)
        assert isinstance(b.get("name"), str) and len(b["name"]) > 5

    def test_listing_has_url(self, fixture_blocks):
        b = find_listing_block(fixture_blocks)
        assert "topreality.sk" in b.get("url", "")

    def test_listing_has_description(self, fixture_blocks):
        b = find_listing_block(fixture_blocks)
        assert len(b.get("description", "")) > 50


# ----------------------------------------------------------------
# TestFindBreadcrumbBlock
# ----------------------------------------------------------------

class TestFindBreadcrumbBlock:
    def test_finds_breadcrumb(self, fixture_blocks):
        b = find_breadcrumb_block(fixture_blocks)
        assert b is not None and b.get("@type") == "BreadcrumbList"

    def test_returns_none_for_empty(self):
        assert find_breadcrumb_block([]) is None

    def test_breadcrumb_has_items(self, fixture_blocks):
        b = find_breadcrumb_block(fixture_blocks)
        assert len(b.get("itemListElement", [])) >= 2


# ----------------------------------------------------------------
# TestExtractPriceFromHtml
# ----------------------------------------------------------------

class TestExtractPriceFromHtml:
    def test_price_from_fixture(self, fixture_html):
        assert extract_price_from_html(fixture_html) == 89900.0

    def test_price_from_data_price_attr(self):
        assert extract_price_from_html('<a data-price="75000">x</a>') == 75000.0

    def test_price_fallback_class_price(self):
        html = '<strong class="price"> 55000 \u20ac</strong>'
        assert extract_price_from_html(html) == 55000.0

    def test_price_zero_when_missing(self):
        assert extract_price_from_html("<html>no price here</html>") == 0.0

    def test_data_price_has_priority_over_class(self):
        html = '<a data-price="100000"></a><strong class="price">99999 \u20ac</strong>'
        assert extract_price_from_html(html) == 100000.0


# ----------------------------------------------------------------
# TestExtractAreaFromText
# ----------------------------------------------------------------

class TestExtractAreaFromText:
    def test_area_from_fixture_description(self, fixture_blocks):
        listing = find_listing_block(fixture_blocks)
        text = listing.get("name", "") + " " + listing.get("description", "")
        assert extract_area_from_text(text) == 401.0

    def test_area_m2_no_space(self):
        assert extract_area_from_text("pozemok 800m2 na predaj") == 800.0

    def test_area_m2_with_space(self):
        assert extract_area_from_text("vymera 650 m2") == 650.0

    def test_area_m_squared_unicode(self):
        assert extract_area_from_text("pozemok 401 m\u00b2 stavebny") == 401.0

    def test_area_from_are_conversion(self):
        assert extract_area_from_text("4-arovy pozemok") == 400.0

    def test_area_zero_when_missing(self):
        assert extract_area_from_text("pekny pozemok v obci") == 0.0


# ----------------------------------------------------------------
# TestExtractLocationFromBreadcrumb
# ----------------------------------------------------------------

class TestExtractLocationFromBreadcrumb:
    def test_location_from_fixture(self, fixture_blocks):
        bc = find_breadcrumb_block(fixture_blocks)
        loc = extract_location_from_breadcrumb(bc)
        assert len(loc) > 0

    def test_returns_empty_for_none(self):
        assert extract_location_from_breadcrumb(None) == ""

    def test_returns_empty_for_no_items(self):
        assert extract_location_from_breadcrumb({"itemListElement": []}) == ""

    def test_returns_last_position(self):
        bc = {
            "itemListElement": [
                {"position": 1, "item": {"name": "Reality"}},
                {"position": 2, "item": {"name": "Senec"}},
                {"position": 3, "item": {"name": "Hruba Borsa"}},
            ]
        }
        assert extract_location_from_breadcrumb(bc) == "Hruba Borsa"


# ----------------------------------------------------------------
# TestListingToParcel
# ----------------------------------------------------------------

class TestListingToParcel:
    def test_returns_parcel(self, fixture_parcel):
        assert isinstance(fixture_parcel, Parcel)

    def test_parcel_price(self, fixture_parcel):
        assert fixture_parcel.price_eur == 89900.0

    def test_parcel_area(self, fixture_parcel):
        assert fixture_parcel.area_sqm == 401.0

    def test_parcel_source_portal(self, fixture_parcel):
        assert fixture_parcel.source_portal == SOURCE_NAME

    def test_parcel_url_absolute(self, fixture_parcel):
        assert fixture_parcel.url.startswith("https://")

    def test_parcel_title_nonempty(self, fixture_parcel):
        assert len(fixture_parcel.title) > 5

    def test_parcel_location_nonempty(self, fixture_parcel):
        assert len(fixture_parcel.location_text) > 0

    def test_returns_none_for_no_listing_block(self, fixture_html):
        assert listing_to_parcel([], fixture_html) is None


# ----------------------------------------------------------------
# TestTopRealityScraperRegistry
# ----------------------------------------------------------------

class TestTopRealityScraperRegistry:
    def test_registered_in_scraper_registry(self):
        assert "topreality_sk" in SCRAPER_REGISTRY

    def test_registry_class_is_correct(self):
        assert SCRAPER_REGISTRY["topreality_sk"] is TopRealityScraper

    def test_parse_listings_on_fixture(self, fixture_html):
        scraper = TopRealityScraper.__new__(TopRealityScraper)
        scraper.rate_limit = 0
        scraper.neutral_ua = False
        scraper._last_call = 0.0
        parcels = scraper.parse_listings(fixture_html)
        assert len(parcels) == 1
        assert isinstance(parcels[0], Parcel)

    def test_scrape_calls_fetch_html(self, fixture_html):
        with patch.object(TopRealityScraper, "fetch_html", return_value=fixture_html):
            scraper = TopRealityScraper()
            parcels = scraper.scrape()
        # 2 SEARCH_URLS, kazda vrati 1 pozemok = 2 celkovo
        assert len(parcels) == 2

    def test_source_name(self):
        assert TopRealityScraper.SOURCE_NAME == "topreality_sk"



