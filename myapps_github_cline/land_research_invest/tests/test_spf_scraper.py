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
# TestParseIndexMetoda2 — nova HTML struktura (uzemneplany plugin href)
# ----------------------------------------------------------------

_PLUGIN_HTML = """<html><body>
<div class="entry-content">
  <p>Okres: Malacky Mesto / Obec: Pernek
  <a href="https://pozfond.sk/wp-content/uploads/uzemneplany/Malacky_Pernek_Pernek.pdf">Stiahnut PDF</a></p>
  <p>Okres: Rimavska-Sobota Mesto / Obec: Martinova
  <a href="https://pozfond.sk/wp-content/uploads/uzemneplany/Rimavska-Sobota_Martinova_Martinova.pdf">Stiahnut PDF</a></p>
  <p>Okres: Banska-Stiavnica Mesto / Obec: Dekys
  <a href="https://pozfond.sk/wp-content/uploads/uzemneplany/Banska-Stiavnica_Dekys_Dekys.pdf">Stiahnut PDF</a></p>
</div>
</body></html>"""

_LISTING_NO_PDF_HTML = """<html><body>
<p>Aktualne fond nezverejnuje nove zoznamy.</p>
<a href="https://pozfond.sk/zoznam-pozemkov-na-prenajom-archiv-2-4-2026/">Archiv pre zoznam neprenajatych pozemkov</a>
</body></html>"""


class TestParseIndexMetoda2:
    def test_plugin_html_returns_list(self):
        result = parse_index(_PLUGIN_HTML)
        assert isinstance(result, list)

    def test_plugin_html_3_entries(self):
        result = parse_index(_PLUGIN_HTML)
        assert len(result) == 3

    def test_plugin_html_has_keys(self):
        result = parse_index(_PLUGIN_HTML)
        for e in result:
            assert "okres" in e and "obec" in e and "pdf_url" in e

    def test_plugin_html_first_okres(self):
        result = parse_index(_PLUGIN_HTML)
        assert "Malacky" in result[0]["okres"]

    def test_plugin_html_first_obec(self):
        result = parse_index(_PLUGIN_HTML)
        assert "Pernek" in result[0]["obec"]

    def test_plugin_html_pdf_url_correct(self):
        result = parse_index(_PLUGIN_HTML)
        assert result[0]["pdf_url"].endswith("Malacky_Pernek_Pernek.pdf")

    def test_plugin_html_no_duplicates(self):
        result = parse_index(_PLUGIN_HTML)
        urls = [e["pdf_url"] for e in result]
        assert len(urls) == len(set(urls))

    def test_plugin_html_url_contains_uzemneplany(self):
        result = parse_index(_PLUGIN_HTML)
        assert all("uzemneplany" in e["pdf_url"] for e in result)

    def test_no_pdf_returns_empty(self):
        """HTML bez PDF uzemneplany odkazov vraci prazdny zoznam."""
        assert parse_index(_LISTING_NO_PDF_HTML) == []


# ----------------------------------------------------------------
# TestSpfScraperListingUrl — nova get_listing_urls + BASE_URL
# ----------------------------------------------------------------

class TestSpfScraperListingUrl:
    def test_base_url_is_pozfond(self):
        from services.scrapers.spf_scraper import BASE_URL, LISTING_URL
        assert "pozfond.sk" in BASE_URL
        assert "www.pozemkovyfond.sk" not in BASE_URL

    def test_listing_url_is_zoznam(self):
        from services.scrapers.spf_scraper import LISTING_URL
        assert "zoznam-pozemkov-na-prenajom" in LISTING_URL


# ----------------------------------------------------------------
# TestSpfFallbackFilter — fallback preferuje pozemkovy archiv
# ----------------------------------------------------------------

# HTML simulujuci SPF listing stranku BEZ aktivnych pozemkov
# Obsahuje faktury-archiv a objednavky-archiv PRED pozemkovym archivom
_LISTING_WITH_WRONG_ARCHIV = """<html><body>
<p>Aktualne fond nezverejnuje nove zoznamy.</p>
<a href="https://pozfond.sk/verejny-pristup-k-informaciam/faktury-archiv/">Faktury archiv</a>
<a href="https://pozfond.sk/verejny-pristup-k-informaciam/objednavky-archiv/">Objednavky archiv</a>
<a href="https://pozfond.sk/zoznam-pozemkov-na-prenajom-archiv-2-4-2026/">Archiv neprenajatych pozemkov</a>
</body></html>"""

# HTML kde je pozemkovy archiv ako relativna URL
_LISTING_RELATIVE_ARCHIV = """<html><body>
<a href="/verejny-pristup-k-informaciam/faktury-archiv/">Faktury archiv</a>
<a href="/zoznam-pozemkov-na-prenajom-archiv-1-1-2026/">Pozemkovy archiv</a>
</body></html>"""


class TestSpfFallbackFilter:
    """Overuje, ze SPF fallback trafuje pozemkovy archiv, nie faktury/objednavky."""

    def _scraper(self):
        s = SpfScraper.__new__(SpfScraper)
        s.rate_limit = 0
        s.neutral_ua = False
        s.timeout    = 20
        s._last_call = 0.0
        return s

    def test_skips_faktury_archiv(self):
        """faktury-archiv NESMIE byt pouzity ako fallback."""
        from unittest.mock import patch, MagicMock
        s = self._scraper()
        captured = []

        def mock_fetch(url):
            captured.append(url)
            return "<html><body></body></html>"

        with patch.object(s, "fetch_html", side_effect=mock_fetch):
            s.parse_listings(_LISTING_WITH_WRONG_ARCHIV)

        for url in captured:
            assert "faktury-archiv" not in url, f"Trafil faktury-archiv: {url}"

    def test_skips_objednavky_archiv(self):
        """objednavky-archiv NESMIE byt pouzity ako fallback."""
        from unittest.mock import patch
        s = self._scraper()
        captured = []

        def mock_fetch(url):
            captured.append(url)
            return "<html><body></body></html>"

        with patch.object(s, "fetch_html", side_effect=mock_fetch):
            s.parse_listings(_LISTING_WITH_WRONG_ARCHIV)

        for url in captured:
            assert "objednavky-archiv" not in url, f"Trafil objednavky-archiv: {url}"

    def test_uses_pozemkovy_archiv(self):
        """Pozemkovy archiv MUSI byt pouzity (obsahuje 'prenajom' + 'archiv')."""
        from unittest.mock import patch
        s = self._scraper()
        captured = []

        def mock_fetch(url):
            captured.append(url)
            return "<html><body></body></html>"

        with patch.object(s, "fetch_html", side_effect=mock_fetch):
            s.parse_listings(_LISTING_WITH_WRONG_ARCHIV)

        assert any("pozemkov" in url or "prenajom" in url for url in captured), \
            f"Pozemkovy archiv nebol pouzity. Volania: {captured}"



# ----------------------------------------------------------------
# TestNormalizeOkres
# ----------------------------------------------------------------

from services.scrapers.spf_scraper import _normalize_okres, OKRESY_BA_70KM


class TestNormalizeOkres:
    def test_malacky(self):
        assert _normalize_okres("Malacky") == "malacky"

    def test_dunajska_streda_medzery(self):
        assert _normalize_okres("Dunajska Streda") == "dunajska-streda"

    def test_bratislava_i(self):
        assert _normalize_okres("Bratislava I") == "bratislava-i"

    def test_rimavska_sobota_pomlcka(self):
        assert _normalize_okres("Rimavska-Sobota") == "rimavska-sobota"

    def test_strips_whitespace(self):
        assert _normalize_okres("  Trnava  ") == "trnava"

    def test_empty_string(self):
        assert _normalize_okres("") == ""


class TestOkresyBa70km:
    def test_blizke_v_sete(self):
        """Blízke okresy (BA, Malacky, Pezinok, Senec) musia byť v sete."""
        for ok in ["malacky", "pezinok", "senec", "trnava", "galanta"]:
            assert ok in OKRESY_BA_70KM, f"{ok} chyba v OKRESY_BA_70KM"

    def test_stredne_v_sete(self):
        """Stredné okresy (~70km) musia byť v sete."""
        for ok in ["hlohovec", "senica", "skalica", "sala", "nove-zamky", "piestany"]:
            assert ok in OKRESY_BA_70KM, f"{ok} chyba v OKRESY_BA_70KM"

    def test_vzdialene_nie_v_sete(self):
        """Vzdialené okresy (Košice, Prešov, Rimavská Sobota) nesmú byť v sete."""
        for ok in ["kosice", "presov", "rimavska-sobota", "banska-bystrica", "zilina"]:
            assert ok not in OKRESY_BA_70KM, f"{ok} nesmie byť v OKRESY_BA_70KM"

    def test_aspon_14_okresov(self):
        """Sada musí mať aspoň 14 relevantných okresov."""
        assert len(OKRESY_BA_70KM) >= 14


class TestSpfFilterOkresy:
    """Testuje filter 70km v parse_listings() cez mock."""

    _HTML_WITH_MIXED_OKRESY = """<html><body>
<div>
  Okres: Malacky Mesto / Obec: Rohoznica
  <a href="https://pozfond.sk/wp-content/uploads/uzemneplany/Malacky_Rohoznica_Rohoznica.pdf">PDF</a>
</div>
<div>
  Okres: Rimavska-Sobota Mesto / Obec: Martinova
  <a href="https://pozfond.sk/wp-content/uploads/uzemneplany/Rimavska-Sobota_Martinova_Martinova.pdf">PDF</a>
</div>
<div>
  Okres: Pezinok Mesto / Obec: Pernek
  <a href="https://pozfond.sk/wp-content/uploads/uzemneplany/Pezinok_Pernek_Pernek.pdf">PDF</a>
</div>
<div>
  Okres: Kosice Mesto / Obec: Lukovistia
  <a href="https://pozfond.sk/wp-content/uploads/uzemneplany/Kosice_Lukovistia_Lukovistia.pdf">PDF</a>
</div>
</body></html>"""

    def _scraper(self, filter_on=True):
        from unittest.mock import patch, MagicMock
        s = SpfScraper.__new__(SpfScraper)
        s.rate_limit = 0
        s.neutral_ua = False
        s.timeout    = 20
        s._last_call = 0.0
        return s

    def test_filter_zachova_blizke(self):
        """Malacky a Pezinok (blízke) musia prejsť filtrom."""
        from unittest.mock import patch
        s = self._scraper()
        captured = []
        def mock_pdf(url):
            captured.append(url)
            return b"%PDF fake"
        with patch.object(s, "fetch_html", return_value="<html></html>"):
            with patch.object(s, "fetch_pdf_bytes", side_effect=mock_pdf):
                with patch("services.scrapers.spf_scraper.get_sources",
                           return_value={"spf": {"filter_okresy_70km": True}}):
                    s.parse_listings(self._HTML_WITH_MIXED_OKRESY)
        fetched_names = " ".join(u for u in captured if "uzemneplany" in u)
        assert "Malacky" in fetched_names or "Pezinok" in fetched_names

    def test_filter_odstrani_vzdialene(self):
        """Rimavska-Sobota a Kosice (vzdialené) nesmú byť stiahnuté."""
        from unittest.mock import patch
        s = self._scraper()
        captured = []
        def mock_pdf(url):
            captured.append(url)
            return b"%PDF fake"
        with patch.object(s, "fetch_html", return_value="<html></html>"):
            with patch.object(s, "fetch_pdf_bytes", side_effect=mock_pdf):
                with patch("services.scrapers.spf_scraper.get_sources",
                           return_value={"spf": {"filter_okresy_70km": True}}):
                    s.parse_listings(self._HTML_WITH_MIXED_OKRESY)
        fetched_pdfs = " ".join(u for u in captured if "uzemneplany" in u)
        assert "Rimavska-Sobota" not in fetched_pdfs
        assert "Kosice" not in fetched_pdfs

    def test_filter_vypnuty_zachova_vsetky(self):
        """filter_okresy_70km=False → stiahnu sa všetky PDF vrátane vzdialených."""
        from unittest.mock import patch
        s = self._scraper()
        captured = []
        def mock_pdf(url):
            captured.append(url)
            return b"%PDF fake"
        with patch.object(s, "fetch_html", return_value="<html></html>"):
            with patch.object(s, "fetch_pdf_bytes", side_effect=mock_pdf):
                with patch("services.scrapers.spf_scraper.get_sources",
                           return_value={"spf": {"filter_okresy_70km": False}}):
                    s.parse_listings(self._HTML_WITH_MIXED_OKRESY)
        fetched_pdfs = [u for u in captured if "uzemneplany" in u]
        assert len(fetched_pdfs) == 4


# ----------------------------------------------------------------
# TestSpfMaxPdf — limit max_pdf
# ----------------------------------------------------------------

class TestSpfMaxPdf:
    """Testuje max_pdf limit v parse_listings()."""

    # HTML s 5 PDF zo SENEC (relevantny okres)
    _HTML_5_PDF = "\n".join([
        '<html><body>' + "".join([
            f'<div>Okres: Senec Mesto / Obec: Obec{i}'
            f' <a href="https://pozfond.sk/wp-content/uploads/uzemneplany/Senec_Obec{i}_Obec{i}.pdf">PDF</a></div>'
            for i in range(1, 6)
        ]) + '</body></html>'
    ])

    def _scraper(self):
        s = SpfScraper.__new__(SpfScraper)
        s.rate_limit = 0
        s.neutral_ua = False
        s.timeout    = 20
        s._last_call = 0.0
        return s

    def test_max_pdf_limits_count(self):
        """max_pdf=2 zo 5 PDF → len 2 PDF stiahnuté."""
        from unittest.mock import patch
        s = self._scraper()
        captured = []
        def mock_fetch(url):
            captured.append(url)
            return b"%PDF fake"
        with patch.object(s, "fetch_html", return_value="<html></html>"):
            with patch.object(s, "fetch_pdf_bytes", side_effect=mock_fetch):
                with patch("services.scrapers.spf_scraper.get_sources",
                           return_value={"spf": {"filter_okresy_70km": True, "max_pdf": 2}}):
                    s.parse_listings(self._HTML_5_PDF)
        fetched = [u for u in captured if "uzemneplany" in u]
        assert len(fetched) == 2

    def test_max_pdf_false_no_limit(self):
        """max_pdf=False → všetkých 5 PDF stiahnutých."""
        from unittest.mock import patch
        s = self._scraper()
        captured = []
        def mock_fetch(url):
            captured.append(url)
            return b"%PDF fake"
        with patch.object(s, "fetch_html", return_value="<html></html>"):
            with patch.object(s, "fetch_pdf_bytes", side_effect=mock_fetch):
                with patch("services.scrapers.spf_scraper.get_sources",
                           return_value={"spf": {"filter_okresy_70km": True, "max_pdf": False}}):
                    s.parse_listings(self._HTML_5_PDF)
        fetched = [u for u in captured if "uzemneplany" in u]
        assert len(fetched) == 5

    def test_max_pdf_default_is_30(self):
        """max_pdf default = 30: 5 PDF < 30 → všetkých 5 stiahnutých (limit sa neaplikuje)."""
        from unittest.mock import patch
        s = self._scraper()
        captured = []
        def mock_fetch(url):
            captured.append(url)
            return b"%PDF fake"
        with patch.object(s, "fetch_html", return_value="<html></html>"):
            with patch.object(s, "fetch_pdf_bytes", side_effect=mock_fetch):
                with patch("services.scrapers.spf_scraper.get_sources",
                           return_value={"spf": {"filter_okresy_70km": True}}):
                    s.parse_listings(self._HTML_5_PDF)
        fetched = [u for u in captured if "uzemneplany" in u]
        # 5 PDF, default limit 30 → všetky 5 prejdú (5 < 30)
        assert len(fetched) == 5

    def test_relative_archiv_url_prefixed(self):
        """Relativna URL pozemkoveho archivu sa preda s BASE_URL."""
        from unittest.mock import patch
        from services.scrapers.spf_scraper import BASE_URL
        s = self._scraper()
        captured = []

        def mock_fetch(url):
            captured.append(url)
            return "<html><body></body></html>"

        with patch.object(s, "fetch_html", side_effect=mock_fetch):
            s.parse_listings(_LISTING_RELATIVE_ARCHIV)

        pozemkove = [u for u in captured if "pozemkov" in u or "prenajom" in u]
        assert pozemkove, f"Pozemkovy archiv nebol pouzity. Volania: {captured}"
        assert all(u.startswith("http") for u in pozemkove), \
            f"URL nezacina http: {pozemkove}"

    def test_no_archiv_link_at_all(self):
        """Ak nie je ziadny archivny link, vrati prazdny zoznam."""
        s = self._scraper()
        result = s.parse_listings("<html><body><p>Nic tu nie je.</p></body></html>")
        assert result == []


    def test_get_listing_urls_returns_listing_url(self):
        from services.scrapers.spf_scraper import LISTING_URL
        scraper = SpfScraper.__new__(SpfScraper)
        scraper.rate_limit = 0
        scraper.neutral_ua = False
        scraper.timeout    = 20
        scraper._last_call = 0.0
        urls = scraper.get_listing_urls()
        assert urls == [LISTING_URL]

    def test_timeout_loaded_from_config(self):
        """timeout atribut existuje (nastaveny z DEFAULT_TIMEOUT ak nie je v config)."""
        scraper = SpfScraper.__new__(SpfScraper)
        scraper.rate_limit = 0
        scraper.neutral_ua = False
        scraper.timeout    = 20
        scraper._last_call = 0.0
        assert hasattr(scraper, "timeout")
        assert scraper.timeout >= 10


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

