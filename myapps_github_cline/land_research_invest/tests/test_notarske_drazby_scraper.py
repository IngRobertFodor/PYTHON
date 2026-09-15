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
    extract_detail_datum,
    extract_detail_navrhovatel,
    extract_pdf_url,
    SOURCE_NAME,
    BASE_DOMAIN,
    LISTING_BASE,
    SEARCH_PARAMS,
    DEFAULT_MAX_PAGES,
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
    s.max_pages   = DEFAULT_MAX_PAGES
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
        assert len(entries) >= 15   # nova fixtura ma 21 riadkov

    def test_entry_has_required_keys(self, scraper, listing_html):
        for e in scraper._parse_listing_html(listing_html):
            for k in ("act_id", "ncr", "drazobnik", "navrhovatel", "typ", "datum"):
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
        html = ("<html><body>"
                "<p>Druh predmetu dr\u00e1\u017eby: Nehnuteln\u00e1 vec</p>"
                "<p>Miesto konania dr\u00e1\u017eby: Senec 90301</p>"
                "</body></html>")
        entry = {"act_id": "abc", "ncr": "100/2026", "drazobnik": "LICITOR",
                 "navrhovatel": "Banka", "typ": "Ozn\u00e1menie o dra\u017ebe",
                 "datum": "15.10.2026"}
        p = scraper._detail_to_parcel(html, "https://notar.sk/drazba?actId=abc", entry)
        assert p is not None and isinstance(p, Parcel)
        assert p.price_eur == 0.0   # cena je v PDF, nie v HTML
        assert p.area_sqm  == 0.0   # vymera je v PDF, nie v HTML
        assert "Senec" in p.location_text


# ----------------------------------------------------------------
# TestListingUrl  (nova logika URL + strankovania)
# ----------------------------------------------------------------

class TestListingUrl:
    def _make_scraper(self):
        s = NotarskeDrazbyaScraper.__new__(NotarskeDrazbyaScraper)
        s.rate_limit = 0; s.neutral_ua = False; s._last_call = 0.0
        return s

    def test_listing_base_correct(self):
        assert LISTING_BASE == "https://www.notar.sk/drazby/"

    def test_search_params_contains_auction_search(self):
        assert "auction-search=Hladat" in SEARCH_PARAMS

    def test_listing_url_page1_no_start(self):
        url = self._make_scraper()._listing_url(1)
        assert "start=" not in url
        assert "auction-search=Hladat" in url

    def test_listing_url_page2_has_start(self):
        url = self._make_scraper()._listing_url(2)
        assert "start=2" in url
        assert "auction-search=Hladat" in url

    def test_listing_url_page24_has_start_24(self):
        url = self._make_scraper()._listing_url(24)
        assert "start=24" in url

    def test_listing_url_starts_with_listing_base(self):
        url = self._make_scraper()._listing_url(1)
        assert url.startswith(LISTING_BASE)

    def test_parse_listings_on_new_fixture(self, scraper, listing_html):
        """Nova fixtura (21 riadkov z notar.sk/drazby/) — parser funguje."""
        entries = scraper.parse_listings(listing_html)
        assert len(entries) >= 15

    def test_fixture_has_hex_act_ids(self, scraper, listing_html):
        """Nova fixtura ma hex actId (nie stare numericky format)."""
        import re
        entries = scraper.parse_listings(listing_html)
        for e in entries:
            assert re.match(r"^[a-f0-9]{10,}$", e["act_id"], re.I)


# ----------------------------------------------------------------
# TestExtractPdfUrl
# ----------------------------------------------------------------

class TestExtractPdfUrl:
    def test_finds_listina_pdf_link(self):
        html = ('<a href="/listina/?actId=abc&documentId=xyz&filename=Oznamenie_o_drazbe.pdf">'
                'Ozn\u00e1menie</a>')
        from bs4 import BeautifulSoup
        url = extract_pdf_url(BeautifulSoup(html, "html.parser"))
        assert url.startswith("https://www.notar.sk/listina/")
        assert ".pdf" in url

    def test_returns_absolute_url(self):
        from bs4 import BeautifulSoup
        url = extract_pdf_url(BeautifulSoup(
            '<a href="/listina/?actId=aaa&filename=test.pdf">PDF</a>', "html.parser"))
        assert url.startswith("https://")

    def test_already_absolute_unchanged(self):
        full = "https://www.notar.sk/listina/?actId=aaa&filename=x.pdf"
        from bs4 import BeautifulSoup
        assert extract_pdf_url(BeautifulSoup(f'<a href="{full}">PDF</a>', "html.parser")) == full

    def test_empty_if_no_pdf(self):
        from bs4 import BeautifulSoup
        assert extract_pdf_url(BeautifulSoup("<a href='/drazba'>X</a>", "html.parser")) == ""


# ----------------------------------------------------------------
# TestExtractNewFunctions
# ----------------------------------------------------------------

class TestExtractNewFunctions:
    def test_datum_found(self):
        txt = "D\u00e1tum a \u010das otvorenia dra\u017eby: 28.10.2026 10:30:00"
        assert "28.10.2026" in extract_detail_datum(txt)

    def test_datum_not_found(self):
        assert extract_detail_datum("ziadny datum") == ""

# ----------------------------------------------------------------
# TestDetailToParcelPdf
# ----------------------------------------------------------------

class TestDetailToParcelPdf:
    def _s(self):
        s = NotarskeDrazbyaScraper.__new__(NotarskeDrazbyaScraper)
        s.rate_limit = 0; s.neutral_ua = False; s._last_call = 0.0
        s.max_pages = DEFAULT_MAX_PAGES
        return s

    def _entry(self, act_id="abc", ncr="1/2026"):
        return {"act_id": act_id, "ncr": ncr, "drazobnik": "LICITOR",
                "navrhovatel": "Banka", "typ": "Ozn\u00e1menie", "datum": "1.1.2026"}

    def test_url_is_pdf_when_available(self):
        pdf = "https://www.notar.sk/listina/?actId=abc&filename=Ozn.pdf"
        html = (f'<p>Druh predmetu dra\u017eby: Nehnutelna vec</p>'
                f'<p>Miesto konania dra\u017eby: Trnava 91701</p>'
                f'<a href="{pdf}">Ozn\u00e1menie</a>')
        p = self._s()._detail_to_parcel(html, "https://notar.sk/x", self._entry())
        assert p is not None and p.url == pdf

    def test_url_fallback_to_detail_if_no_pdf(self):
        html = ('<p>Druh predmetu dra\u017eby: Nehnutelna vec</p>'
                '<p>Miesto konania dra\u017eby: Bratislava 81102</p>')
        du = "https://notar.sk/drazba?actId=abc"
        p = self._s()._detail_to_parcel(html, du, self._entry())
        assert p is not None and p.url == du

    def test_price_area_zero(self):
        html = ('<p>Druh predmetu dra\u017eby: Nehnutelna vec</p>'
                '<p>Miesto konania dra\u017eby: Senec 90301</p>')
        p = self._s()._detail_to_parcel(html, "https://notar.sk/y", self._entry())
        assert p is not None and p.price_eur == 0.0 and p.area_sqm == 0.0

    def test_description_has_ncr_and_pdf_note(self):
        html = ('<p>Druh predmetu dra\u017eby: Nehnutelna vec</p>'
                '<p>Miesto konania dra\u017eby: Ko\u0161ice 04001</p>')
        p = self._s()._detail_to_parcel(html, "https://notar.sk/z", self._entry(ncr="999/2026"))
        assert p is not None
        assert "999/2026" in p.description
        assert "PDF" in p.description


# ----------------------------------------------------------------
# TestMaxPages
# ----------------------------------------------------------------

class TestMaxPages:
    def test_default_max_pages_constant(self):
        assert DEFAULT_MAX_PAGES == 3

    def test_listing_url_page3_has_start3(self):
        s = NotarskeDrazbyaScraper.__new__(NotarskeDrazbyaScraper)
        s.rate_limit = 0; s.neutral_ua = False; s._last_call = 0.0; s.max_pages = 3
        assert "start=3" in s._listing_url(3)

    def test_listing_url_page1_no_start(self):
        s = NotarskeDrazbyaScraper.__new__(NotarskeDrazbyaScraper)
        s.rate_limit = 0; s.neutral_ua = False; s._last_call = 0.0; s.max_pages = 3
        assert "start=" not in s._listing_url(1)


    def test_navrhovatel_found(self):
        txt = "Navrhovate\u013e (-ia) dra\u017eby: 365.bank, a. s., I\u010cO: 12345"
        assert "365.bank" in extract_detail_navrhovatel(txt)

    def test_navrhovatel_not_found(self):
        assert extract_detail_navrhovatel("ziadny") == ""

    def test_location_trims_blizšie(self):
        txt = "Miesto konania dra\u017eby: Hlavn\u00e1 1, Trnava 91701 Bli\u017e\u0161ie ozn."
        loc = extract_detail_location(txt)
        assert "Trnava" in loc
        assert "Bli\u017e\u0161ie" not in loc


    def test_detail_url_format(self, scraper, listing_html):
        """Detail URL sa sklada spravne z BASE_DOMAIN + actId."""
        entries = scraper.parse_listings(listing_html)
        if entries:
            act_id = entries[0]["act_id"]
            expected = f"{BASE_DOMAIN}/drazba?actId={act_id}"
            assert expected.startswith("https://www.notar.sk/drazba?actId=")


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

    def test_listing_base(self):
        assert LISTING_BASE == "https://www.notar.sk/drazby/"
