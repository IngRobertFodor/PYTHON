"""Obchodny vestnik scraper - PDF-based parser drazobnych oznameni.
===================================================================
Stiahne PDF formular drazobneho oznamenia z justice.gov.sk a extrahuje
investicne relevantne udaje: vyvolavaciu cenu, vymeru pozemkov, LV,
katastralne uzemie, datum drazby, drazobnika.

Technicke detaily:
  - Portal: https://www.justice.gov.sk/PortalApp/ObchodnyVestnik
  - Format: PDF formulare podla zakona c. 527/2002 Z.z. o dobrovolnych drazbch
  - Pouziva: pypdf (uz nainstalovany) - cita PDF do pamate (nie na disk!)
  - Text PDF ma formulacne polia oznacene pismenami (C. miesto, D. datum,
    G. predmet, L. najnizsie podanie...) - parser vyuziva tieto markery
  - Vymera = sucet vsetkych pozemkovych parciel (bez stavieb)
  - Cena = Najnizsie podanie (L.) - vyvolavacia cena drazby

Kluce extrakcie:
  extract_pdf_text()            -> plny normalizovany text
  extract_price_najnizsie()     -> float EUR (najnizsie podanie)
  extract_auction_date()        -> retazec datumu konania
  extract_location_ov()         -> obec/katastralne uzemie
  extract_lv()                  -> cislo listu vlastnictva
  extract_parcels_area()        -> sucet vymery pozemkov v m2
  extract_drazobnik()           -> nazov drazobnickej spolocnosti
  pdf_to_parcel()               -> Parcel objekt
"""

import re
import io
import pypdf

from services.scrapers.base_scraper import BaseScraper

SOURCE_NAME = "obchodny_vestnik"
BASE_URL    = "https://www.justice.gov.sk/PortalApp/ObchodnyVestnik"

# --- Regex vzory ---
# Cena: "17.200,- €" alebo "17 200 EUR" alebo "17200,00 €"
_PRICE_RE = re.compile(
    r"([\d\s]{1,10}[\d])[,.][-\s]?\s*" + chr(0x20AC),
    re.IGNORECASE,
)
# Datum: "8. 10. 2026" alebo "08.10.2026"
_DATE_RE = re.compile(
    r"\b(\d{1,2})[.\s]+(\d{1,2})[.\s]+(20\d{2})\b"
)
# LV cislo: "LV : 1672" alebo "LV c. 1672" alebo "LV 1672"
_LV_RE = re.compile(
    r"LV\s*(?:c\.?|" + chr(269) + r"\.?)?\s*:?\s*(\d+)",
    re.IGNORECASE,
)
# Vymera: "379" pred "Zastavan" alebo pred typom pozemku
# Format v PDF: "529 Zastavan\u00e1 plocha a n\u00e1dvorie 379"
_PARCEL_ROW_RE = re.compile(
    r"\d+\s+"
    r"(?:Zastavana plocha|Zahrada|Orna poda|Trval"
    + chr(253)
    + r" travny porast|Lesny pozemok|Vodna plocha|Ostatna plocha)"
    r"[^0-9]*(\d+)",
    re.IGNORECASE | re.UNICODE,
)
# Katastralne uzemie a obec z "Zakladna specifikacia"
_KU_RE   = re.compile(
    r"Katastr[a\u00e1]lne\s+[u\u00fa]zemie\s*:?\s*([A-Z\u00c0-\u017e][^\n,;:]{2,40}?)(?:\s+Okres|\s+LV|\s*$)",
    re.IGNORECASE,
)
_OBEC_RE = re.compile(
    r"Obec\s*:?\s*([A-Z\u00c0-\u017e][a-z\u00c0-\u017e][^\n,;:]{1,35}?)(?:\s+Katastr|\s+LV|\s+Okres|\s*$)",
    re.IGNORECASE,
)
# Drazobnik - "Obchodne meno" sekcia pred adresou
_DRAZOBNIK_RE = re.compile(
    r"Obchodn[e\u00e9]\s+meno[^:]*:\s*([A-Z\u00c0-\u017e][^\n]{3,60}?)(?:\s+I\.|$)",
    re.IGNORECASE,
)


class ObchodnyVestnikScraper(BaseScraper):
    """Scraper drazobnych oznameni z Obchodneho vestnika (PDF-based).

    Workflow:
      1. scrape() -> _scrape_listing_pages() -> FormularDetail URL zo zoznamu
      2. Pre kazdu URL: fetch_html() -> _extract_pdf_url_from_detail() -> PDF URL
      3. fetch_pdf_bytes(pdf_url) -> scrape_pdf() -> Parcel
    """

    SOURCE_NAME   = "obchodny_vestnik"
    BASE_URL      = BASE_URL
    BASE_DOMAIN   = "https://obchodnyvestnik.justice.gov.sk"
    _LISTING_URL  = (
        "https://obchodnyvestnik.justice.gov.sk"
        "/ObchodnyVestnik/Formular/FormulareVyhladavanie.aspx"
    )
    _DRAZBA_KEYS  = ["dra\u017eb", "drazb", "dobrovoln", "opakovan",
                     "dra\u017eobn", "drazobn"]

    def scrape(self, criteria=None):
        """Kompletny workflow: listing -> detail -> PDF -> Parcel."""
        parcels, seen = [], set()
        for page_parcels in self._scrape_listing_pages():
            for p in page_parcels:
                if p.url and p.url not in seen:
                    seen.add(p.url)
                    parcels.append(p)
        return parcels

    def _scrape_listing_pages(self):
        """Generator: pre kazdu stranu listingu yieldi zoznam Parcel."""
        seen_ids = set()
        for page in range(1, 51):
            url = self._page_url(self._listing_url_page(page), 1)
            try:
                html = self.fetch_html(url)
            except Exception as exc:
                print(f"[{self.SOURCE_NAME}] listing strana {page} chyba: {exc}")
                break
            form_urls = self._parse_listing_html(html)
            new_urls  = [u for u in form_urls if u not in seen_ids]
            if not new_urls:
                break
            seen_ids.update(new_urls)
            page_parcels = []
            for fu in new_urls:
                try:
                    page_parcels.extend(self._process_formular(fu))
                except Exception as exc:
                    print(f"[{self.SOURCE_NAME}] formular {fu} chyba: {exc}")
            yield page_parcels

    def _listing_url_page(self, page):
        """URL pre konkretnu stranu listingu OV."""
        base = self._LISTING_URL
        sep  = "&" if "?" in base else "?"
        return base if page == 1 else f"{base}{sep}strana={page}"

    def _parse_listing_html(self, html):
        """Zo HTML listingu extrahuje zoznam FormularDetail URL pre drazby."""
        from bs4 import BeautifulSoup
        soup  = BeautifulSoup(html, "html.parser")
        urls  = []
        table = soup.find("table")
        if not table:
            return urls
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            if len(cells) < 2:
                continue
            typ = cells[1].get_text(strip=True).lower()
            if not any(k in typ for k in self._DRAZBA_KEYS):
                continue
            a = row.find("a", href=re.compile(r"FormularDetail", re.I))
            if a:
                href = a["href"]
                if not href.startswith("http"):
                    href = self.BASE_DOMAIN + href
                urls.append(href)
        return urls

    def _process_formular(self, formular_url):
        """Z FormularDetail stranky najde PDF link a parsuje ho."""
        html    = self.fetch_html(formular_url)
        pdf_url = self._extract_pdf_url_from_detail(html)
        if not pdf_url:
            return []
        pdf_bytes = self.fetch_pdf_bytes(pdf_url)
        return self.scrape_pdf(pdf_bytes)

    def _extract_pdf_url_from_detail(self, html):
        """Zo stranky FormularDetail extrahuje URL na PDF."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if re.search(r"\.pdf|GetFormularPdf|formular.*pdf", href, re.I):
                if not href.startswith("http"):
                    href = self.BASE_DOMAIN + href
                return href
        return None

    def parse_listings(self, html):
        """BaseScraper kontrakt - vrati FormularDetail URL zo stranky listingu."""
        return self._parse_listing_html(html)

    def fetch_pdf_bytes(self, url):
        """Stiahne PDF ako bytes (nepise na disk)."""
        import requests
        self._wait_rate_limit()
        resp = requests.get(
            url,
            headers={"User-Agent": self.user_agent},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.content

    def scrape_pdf(self, pdf_source):
        """Parsuje PDF drazobneho oznamenia. pdf_source: cesta alebo bytes."""
        try:
            text   = extract_pdf_text(pdf_source)
            parcel = pdf_to_parcel(text, str(pdf_source))
            return [] if parcel is None else [parcel]
        except Exception as exc:
            print(f"[{self.SOURCE_NAME}] scrape_pdf error: {exc}")
            return []


# ----------------------------------------------------------------
# Samostatne funkcie (testovatelne bez instancie)
# ----------------------------------------------------------------

def extract_pdf_text(pdf_source):
    """
    Precita PDF a vrati normalizovany plaintext.
    pdf_source: cesta k suboru (str/Path) alebo bytes.
    """
    if isinstance(pdf_source, (bytes, bytearray)):
        reader = pypdf.PdfReader(io.BytesIO(pdf_source))
    else:
        reader = pypdf.PdfReader(str(pdf_source))
    pages = [page.extract_text() or "" for page in reader.pages]
    raw = " ".join(pages)
    return re.sub(r"\s+", " ", raw).strip()


def _parse_price_str(price_str):
    """Konvertuje '17.200,-' alebo '17 200' na float."""
    c = price_str.strip().replace(" ", "").replace("\xa0", "")
    c = re.sub(r"[.](?=\d{3}(?:[,.]|$))", "", c)  # tisice bodka
    c = re.sub(r"[,](?=\d{3}(?:[,.]|$))", "", c)  # tisice ciarka
    c = c.rstrip(",-.").replace(",", ".").replace(" ", "")
    try:
        return float(c)
    except ValueError:
        return 0.0


def extract_price_najnizsie(text):
    """
    Extrahuje Najnizsie podanie (vyvolavacia cena).
    PDF ma obratene poradie: hodnota pred labelom.
    Vracia float alebo 0.0.
    """
    EUR = chr(0x20AC)
    # Hodnota pred "Najnizsie podanie" (obratene poradie)
    pat = re.compile(
        r"([\d][\d\s.]{0,10}[\d])[,.][-\s]?\s*" + EUR
        + r"[^" + EUR + r"]{0,60}?Najni" + chr(382) + r"(?:ie|"
        + chr(353) + r"ie)",
        re.IGNORECASE | re.DOTALL,
    )
    m = pat.search(text)
    if m:
        return _parse_price_str(m.group(1))
    # Fallback: "Najnizsie" a hodnota za nim
    pat2 = re.compile(
        r"Najni" + chr(382) + r"(?:ie|" + chr(353) + r"ie)"
        + r".{0,80}?([\d][\d\s.]{0,10}[\d])[,.][-\s]?\s*" + EUR,
        re.IGNORECASE | re.DOTALL,
    )
    m2 = pat2.search(text)
    if m2:
        return _parse_price_str(m2.group(1))
    # Fallback2: max zo vsetkych cien
    vals = [_parse_price_str(p) for p in _PRICE_RE.findall(text)]
    vals = [v for v in vals if v > 0]
    return max(vals) if vals else 0.0


def extract_auction_date(text):
    """
    Extrahuje datum konania drazby ('D. datum').
    Vracia 'DD.MM.YYYY' alebo ''.
    """
    pat = re.compile(
        r"(\d{1,2})[.\s]+(\d{1,2})[.\s]+(20\d{2})"
        + r"(?:[^.]{0,80}?D[a\u00e1]tum\s+konania)",
        re.IGNORECASE,
    )
    m = pat.search(text)
    if m:
        return f"{int(m.group(1)):02d}.{int(m.group(2)):02d}.{m.group(3)}"
    m2 = _DATE_RE.search(text)
    if m2:
        return f"{int(m2.group(1)):02d}.{int(m2.group(2)):02d}.{m2.group(3)}"
    return ""


def extract_lv(text):
    """Extrahuje cislo LV. Vracia retazec alebo ''."""
    m = _LV_RE.search(text)
    return m.group(1) if m else ""


def extract_location_ov(text):
    """
    Extrahuje lokalitu (katastralne uzemie) zo sekcie Zakladna specifikacia.
    Format: '... 1672 Okres Obec KatastralneUzemie KatastralneUzemie Pozemky ...'
    Vracia retazec alebo ''.
    """
    i = text.find("pecifik")
    block = text[i:i+500] if i >= 0 else text[:600]
    # Format: LV Okres Obec KU KU (4 slova za cislom LV)
    m = re.search(r"(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+Pozemky", block)
    if m:
        # skupina 4 alebo 5 = katastralne uzemie (posledne pred Pozemky)
        return m.group(5).strip()
    # Fallback: obec (skupina 3)
    m2 = re.search(r"(\d+)\s+(\S+)\s+(\S+)\s+(\S+)", block)
    if m2:
        return m2.group(3).strip()
    # Povodny regex fallback
    mk = _KU_RE.search(block)
    if mk:
        return mk.group(1).strip()
    mo = _OBEC_RE.search(block)
    if mo:
        return mo.group(1).strip()
    return ""


def extract_parcels_area(text):
    """
    Extrahuje celkovu vymeru pozemkov (sucet parciel).
    Format: '529 Zastavana plocha a nadvorie 379 531 Zahrada 304'
    Vracia float (m2) alebo 0.0.
    """
    i = text.lower().find("pozemky")
    if i < 0:
        return 0.0
    # Ohranicime blok - konci pri "Stavby" alebo po 600 znakoch
    block_raw = text[i:i+600]
    j = block_raw.lower().find("stavby")
    block = block_raw[:j] if j > 0 else block_raw

    # Pattern: cislo_parcely DRUH_POZEMKU vymera
    # Druh pozemku obsahuje diakritiku - hladame viacslovna hodnotu pred cislom vymery
    # Format: "529 Zastavaná plocha a nádvorie 379 531 Záhrada 304"
    # Hladame vzory: (druh pozemku v texte) nasledovany cislom (vymera)
    pozemok_re = re.compile(
        r"\d+\s+"                          # cislo parcely
        r"[A-Z\u00c0-\u017e][^\d]{3,50}?"  # druh pozemku (text s diakritikou)
        r"\s+(\d{2,6})"                    # vymera v m2
        r"(?:\s+\d|\s*$)",                 # za tym bud dalsia parcela alebo koniec
        re.IGNORECASE,
    )
    total = 0.0
    for m in pozemok_re.finditer(block):
        try:
            val = float(m.group(1))
            if 10 <= val <= 999999:
                total += val
        except ValueError:
            pass
    return total


def extract_drazobnik(text):
    """
    Extrahuje nazov drazobnickej spolocnosti.
    Vracia retazec alebo ''.
    """
    # Hladaj priamo nazov spolocnosti (a.s., s.r.o.) v prvej casti textu
    m = re.search(
        r"([A-Z\u00c0-\u017e][a-zA-Z\u00c0-\u017e\s,]{2,50}?"
        r"(?:a\.s\.|s\.r\.o\.|spol\.|k\.s\.|n\.o\.))",
        text[:800],
    )
    if m:
        return m.group(1).strip()
    # Fallback: prvy riadok v bloku "Oznacenie drazobnika" -> meno firmy
    i = text.find("Ozna")
    if i >= 0:
        block = text[i:i+300]
        m2 = re.search(
            r"(?:I\.\s+|meno[^:]*:\s*)"
            r"([A-Z\u00c0-\u017e][^\n.]{3,60}?)"
            r"(?:\s+X\d|\s+\d{2}\s|\s*$)",
            block,
        )
        if m2:
            return m2.group(1).strip()
    return ""


def pdf_to_parcel(text, source_url=""):
    """
    Z normalizovaneho textu PDF vytvori Parcel.
    Vracia Parcel alebo None ak chybaju minimalne data.
    """
    price    = extract_price_najnizsie(text)
    area     = extract_parcels_area(text)
    location = extract_location_ov(text)
    lv       = extract_lv(text)
    datum    = extract_auction_date(text)
    drazob   = extract_drazobnik(text)

    # Minimalna validacia
    if price <= 0 and not lv:
        return None

    parts = []
    if drazob:
        parts.append("DRAZBA: " + drazob)
    if datum:
        parts.append("Datum: " + datum)
    if lv:
        parts.append("LV: " + lv)
    if location:
        parts.append("K.u.: " + location)
    if price > 0:
        parts.append("Najnizsie podanie: " + str(int(price)) + " EUR")

    title = "Drazba"
    if drazob:
        title += " - " + drazob[:40]
    if location:
        title += " (" + location + ")"

    return BaseScraper._make_parcel(
        title         = title,
        url           = source_url,
        price_eur     = price,
        area_sqm      = area,
        location_text = location,
        source_portal = SOURCE_NAME,
        description   = " | ".join(parts)[:500],
    )

