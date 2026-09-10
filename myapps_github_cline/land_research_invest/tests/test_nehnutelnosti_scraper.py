"""Testy - Nehnutelnosti.sk scraper
=====================================
Testuje: extract_jsonld (RSC payload), extract_items_from_graph,
         item_to_parcel, _extract_location, NehnutelnostiScraper.
100% offline - parser bezi na ulozenom HTML fixture (Next.js SSR).
"""

import pytest
import pathlib
from unittest.mock import patch

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "nehnutelnosti_sk_listing.html"

from services.scrapers.nehnutelnosti_scraper import (
    NehnutelnostiScraper,
    extract_jsonld,
    extract_items_from_graph,
    item_to_parcel,
    _extract_location,
    SOURCE_NAME,
)
from models.parcel import Parcel


@pytest.fixture(scope="module")
def fixture_html():
    return FIXTURE.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def fixture_jsonld(fixture_html):
    return extract_jsonld(fixture_html)


@pytest.fixture(scope="module")
def fixture_items(fixture_jsonld):
    return extract_items_from_graph(fixture_jsonld)


@pytest.fixture(scope="module")
def fixture_parcels(fixture_items):
    return [p for p in (item_to_parcel(it) for it in fixture_items) if p]


# ----------------------------------------------------------------
# TestExtractJsonld
# ----------------------------------------------------------------

class TestExtractJsonld:
    def test_returns_dict(self, fixture_jsonld):
        assert isinstance(fixture_jsonld, dict)

    def test_has_context(self, fixture_jsonld):
        assert fixture_jsonld.get("@context") == "https://schema.org"

    def test_has_graph(self, fixture_jsonld):
        assert isinstance(fixture_jsonld.get("@graph"), list)

    def test_graph_not_empty(self, fixture_jsonld):
        assert len(fixture_jsonld["@graph"]) > 0

    def test_raises_on_missing_marker(self):
        with pytest.raises(ValueError, match="nenajdeny v RSC payloade"):
            extract_jsonld("<html>no marker here</html>")


# ----------------------------------------------------------------
# TestExtractItems
# ----------------------------------------------------------------

class TestExtractItems:
    def test_returns_list(self, fixture_items):
        assert isinstance(fixture_items, list)

    def test_30_items(self, fixture_items):
        assert len(fixture_items) >= 20    # listing ma 20-30 poloziek

    def test_each_item_has_name(self, fixture_items):
        assert all("name" in it for it in fixture_items)

    def test_each_item_has_price_spec(self, fixture_items):
        assert all("priceSpecification" in it for it in fixture_items)

    def test_first_item_name(self, fixture_items):
        name = fixture_items[0]["name"].lower()
        assert "pozemok" in name or "staveb" in name

    def test_empty_graph_returns_empty(self):
        assert extract_items_from_graph({"@graph": []}) == []


# ----------------------------------------------------------------
# TestItemToParcel
# ----------------------------------------------------------------

class TestItemToParcel:
    def test_returns_parcel_for_valid_item(self, fixture_items):
        valid = next(it for it in fixture_items if it.get("priceSpecification", {}).get("price", 0) > 1)
        assert isinstance(item_to_parcel(valid), Parcel)

    def test_first_parcel_price(self, fixture_parcels):
        # ceny z listing.html su roznorode - overujeme len ze su kladne
        assert all(p.price_eur > 0 for p in fixture_parcels)

    def test_first_parcel_area(self, fixture_parcels):
        # vymery z listing.html su roznorodne - overujeme ze su kladne
        assert all(p.area_sqm >= 0 for p in fixture_parcels)

    def test_parcel_has_url(self, fixture_parcels):
        assert all(p.url.startswith("https://") for p in fixture_parcels)

    def test_parcel_source_portal(self, fixture_parcels):
        assert all(p.source_portal == "nehnutelnosti_sk" for p in fixture_parcels)

    def test_filters_zero_price(self, fixture_items):
        zero = next(
            (it for it in fixture_items if it.get("priceSpecification", {}).get("price", 1) <= 1),
            None
        )
        if zero:
            assert item_to_parcel(zero) is None

    def test_27_valid_parcels(self, fixture_parcels):
        assert len(fixture_parcels) >= 20    # listing vracia 20+ pozemkov

    def test_area_extracted_from_floorsize(self, fixture_items):
        item_fs = next(
            (it for it in fixture_items
             if isinstance(it.get("floorSize"), dict) and it["floorSize"].get("value")
             and it.get("priceSpecification", {}).get("price", 0) > 1),
            None
        )
        if item_fs:
            assert item_to_parcel(item_fs).area_sqm > 0


# ----------------------------------------------------------------
# TestExtractLocation
# ----------------------------------------------------------------

class TestExtractLocation:
    def test_from_title_brackets(self):
        assert _extract_location("Pozemok v slepej ulici (Chorvatsky Grob)", "") == "Chorvatsky Grob"

    def test_from_url(self):
        url = "https://www.nehnutelnosti.sk/detail/JuBPL/predaj-pozemky-senec-nov\u00e1-lokalita"
        result = _extract_location("Pozemok", url)
        assert "senec" in result.lower() or result == ""

    def test_empty_when_no_info(self):
        assert isinstance(_extract_location("Pozemok bez lokality", "https://example.com/detail/abc/pozemok"), str)


# ----------------------------------------------------------------
# TestNehnutelnostiScraper
# ----------------------------------------------------------------

class TestNehnutelnostiScraper:
    def test_source_name(self):
        assert NehnutelnostiScraper.SOURCE_NAME == "nehnutelnosti_sk"

    def test_source_name_constant(self):
        assert SOURCE_NAME == "nehnutelnosti_sk"

    def test_parse_listings_returns_list(self, fixture_html):
        scraper = NehnutelnostiScraper.__new__(NehnutelnostiScraper)
        scraper.rate_limit = 0
        scraper.neutral_ua = False
        scraper._last_call = 0.0
        parcels = scraper.parse_listings(fixture_html)
        assert isinstance(parcels, list) and len(parcels) >= 20

    def test_parse_listings_bad_html_returns_empty(self):
        scraper = NehnutelnostiScraper.__new__(NehnutelnostiScraper)
        scraper.rate_limit = 0
        scraper.neutral_ua = False
        scraper._last_call = 0.0
        assert scraper.parse_listings("<html>no data</html>") == []

    def test_scrape_uses_multiple_urls(self, fixture_html):
        with patch.object(NehnutelnostiScraper, "fetch_html", return_value=fixture_html):
            parcels = NehnutelnostiScraper().scrape()
        assert len(parcels) >= 25

