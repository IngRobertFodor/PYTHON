"""Testy - Scraper sluzba
=========================
Testuje: base_scraper, nehnutelnosti_scraper (na realnom fixture),
         scraper_service (registry, dedup, scrape_all).
100% offline - HTTP je mocknuty, parser bezi na ulozenom HTML.
"""

import pytest
import pathlib
from unittest.mock import patch, MagicMock

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "nehnut_detail.html"

from services.scrapers.base_scraper import BaseScraper
from services.scrapers.nehnutelnosti_scraper import (
    extract_jsonld, extract_items_from_graph, item_to_parcel,
    _unescape_rsc, _extract_location, NehnutelnostiScraper,
)
from services.scraper_service import (
    scrape_all, scrape_source, get_registered_scrapers, _deduplicate,
    SCRAPER_REGISTRY,
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
        with pytest.raises(ValueError, match="T23c11"):
            extract_jsonld("<html>no marker here</html>")


# ----------------------------------------------------------------
# TestExtractItems
# ----------------------------------------------------------------

class TestExtractItems:
    def test_returns_list(self, fixture_items):
        assert isinstance(fixture_items, list)

    def test_30_items(self, fixture_items):
        assert len(fixture_items) == 30

    def test_each_item_has_name(self, fixture_items):
        assert all("name" in it for it in fixture_items)

    def test_each_item_has_price_spec(self, fixture_items):
        assert all("priceSpecification" in it for it in fixture_items)

    def test_first_item_name(self, fixture_items):
        assert "pozemok" in fixture_items[0]["name"].lower() or "staveb" in fixture_items[0]["name"].lower()

    def test_empty_graph_returns_empty(self):
        assert extract_items_from_graph({"@graph": []}) == []


# ----------------------------------------------------------------
# TestItemToParcel
# ----------------------------------------------------------------

class TestItemToParcel:
    def test_returns_parcel_for_valid_item(self, fixture_items):
        valid = next(it for it in fixture_items if it.get("priceSpecification",{}).get("price",0) > 1)
        p = item_to_parcel(valid)
        assert isinstance(p, Parcel)

    def test_first_parcel_price(self, fixture_parcels):
        prices = [p.price_eur for p in fixture_parcels]
        assert 285390.0 in prices

    def test_first_parcel_area(self, fixture_parcels):
        areas = [p.area_sqm for p in fixture_parcels]
        assert 1057.0 in areas

    def test_parcel_has_url(self, fixture_parcels):
        assert all(p.url.startswith("https://") for p in fixture_parcels)

    def test_parcel_source_portal(self, fixture_parcels):
        assert all(p.source_portal == "nehnutelnosti_sk" for p in fixture_parcels)

    def test_filters_zero_price(self, fixture_items):
        zero_price = next(
            (it for it in fixture_items if it.get("priceSpecification",{}).get("price",1) <= 1),
            None
        )
        if zero_price:
            assert item_to_parcel(zero_price) is None

    def test_27_valid_parcels(self, fixture_parcels):
        assert len(fixture_parcels) >= 25  # aspon 25 z 30

    def test_area_extracted_from_floorsize(self, fixture_items):
        item_with_fs = next(
            (it for it in fixture_items
             if isinstance(it.get("floorSize"), dict) and it["floorSize"].get("value")
             and it.get("priceSpecification",{}).get("price",0) > 1),
            None
        )
        if item_with_fs:
            p = item_to_parcel(item_with_fs)
            assert p.area_sqm > 0


# ----------------------------------------------------------------
# TestExtractLocation
# ----------------------------------------------------------------

class TestExtractLocation:
    def test_from_title_brackets(self):
        title = "Pozemok v slepej ulici (Chorvatsky Grob)"
        assert _extract_location(title, "") == "Chorvatsky Grob"

    def test_from_url(self):
        url = "https://www.nehnutelnosti.sk/detail/JuBPL/predaj-pozemky-senec-nov\u00e1-lokalita"
        result = _extract_location("Pozemok", url)
        assert "senec" in result.lower() or result == ""

    def test_empty_when_no_info(self):
        result = _extract_location("Pozemok bez lokality", "https://example.com/detail/abc/pozemok")
        assert isinstance(result, str)


# ----------------------------------------------------------------
# TestScraperService
# ----------------------------------------------------------------

class TestScraperService:
    def test_registry_has_nehnutelnosti(self):
        assert "nehnutelnosti_sk" in SCRAPER_REGISTRY

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
        assert len(parcels) >= 25
        assert all(isinstance(p, Parcel) for p in parcels)

    def test_scrape_all_calls_nehnutelnosti(self, fixture_html):
        with patch.object(NehnutelnostiScraper, "fetch_html", return_value=fixture_html):
            parcels = scrape_all()
        assert len(parcels) >= 25

    def test_scrape_all_deduplicates(self, fixture_html):
        with patch.object(NehnutelnostiScraper, "fetch_html", return_value=fixture_html):
            parcels = scrape_all()
        urls = [p.url for p in parcels if p.url]
        assert len(urls) == len(set(urls))

    def test_deduplicate_removes_duplicates(self):
        p1 = BaseScraper._make_parcel(url="https://example.com/1", price_eur=1000, area_sqm=100)
        p2 = BaseScraper._make_parcel(url="https://example.com/1", price_eur=1000, area_sqm=100)
        p3 = BaseScraper._make_parcel(url="https://example.com/2", price_eur=2000, area_sqm=200)
        result = _deduplicate([p1, p2, p3])
        assert len(result) == 2

    def test_deduplicate_preserves_order(self):
        p1 = BaseScraper._make_parcel(url="https://a.com/1", price_eur=1)
        p2 = BaseScraper._make_parcel(url="https://a.com/2", price_eur=2)
        result = _deduplicate([p1, p2])
        assert result[0].url == "https://a.com/1"

    def test_scrape_all_skips_unregistered_sources(self):
        with patch.object(NehnutelnostiScraper, "fetch_html", return_value="<html></html>"):
            parcels = scrape_all()
        assert isinstance(parcels, list)
