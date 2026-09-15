"""Notarske drazby scraper
================================
Parsuje Notarsky centralny register drazob (notar.sk).

Listing: HTML tabulka zo stranky /drazby/ (vyhladavaci formular, GET)
  - URL: https://www.notar.sk/drazby/?...&auction-search=Hladat&start=N
  - 6 stlpcov: NCRdr | Drazobnik | Navrhovatel | Typ | Oznamenie | Datum
  - Odkaz na detail: drazba?actId=<hex_id>
  - Strankovanie: &start=N (cislo strany, 1-based)

Detail: HTML stranka jednotlivej drazby
  - Obsahuje: NCRdr, drazobnik, navrhovatel, miesto konania, datum, druh predmetu
  - Odkaz na PDF "Oznamenie o drazbe" (sken s cenou/vymerou/adresou predmetu)

PDF (Oznamenie o drazbe):
  - URL: https://www.notar.sk/listina/?actId=...&documentId=...&filename=...pdf
  - Priamy verejny odkaz (bez session) -> parcel.url = klikaci PDF odkaz
  - Pouzivatel jednym klikom ziska cenu, vymeru a presnu adresu predmetu

Obmedzenie stranok: max_pages (z configu, default 3) -> ~40 najnovsich drazieb
"""

import re
from services.scrapers.base_scraper import BaseScraper

SOURCE_NAME  = "notarske_drazby"
BASE_DOMAIN  = "https://www.notar.sk"
LISTING_BASE = "https://www.notar.sk/drazby/"
SEARCH_PARAMS = (
    "actNumber1=&actNumber2=&auctioneerName=&auctioneerCode="
    "&subjectCity=&AuctionActType=&auctionDateFrom=&auctionDateTo="
    "&auction-search=Hladat"
)

DEFAULT_MAX_PAGES = 3

_SKIP_TYPES  = ["upustenie", "zrusenie", "zanik"]
_PRICE_RE    = re.compile(
    r"(\d[\d\s\.]{1,10}\d)[,\.]?[-\s]?\s*(?:eur|EUR|\u20ac)", re.IGNORECASE)
_AREA_RE     = re.compile(r"(\d[\d\s]{0,5}?)\s*m\s*(?:2|\xb2|\u00b2)", re.IGNORECASE)
_PDF_URL_RE  = re.compile(r"(?:https?://[^/]+)?/listina/[^\"'>\s]+\.pdf", re.IGNORECASE)
_LOCATION_RE = re.compile(
    r"Miesto konania dr[a\u00e1]\u017eby:\s*([^\n]{3,80})", re.IGNORECASE)


class NotarskeDrazbyaScraper(BaseScraper):
    """Scraper Notarskeho centralneho registra drazob (notar.sk).

    parcel.url = priamy PDF odkaz (Oznamenie o drazbe) — klikaci link na sken
    s cenou, vymerou a adresou predmetu drazby.
    """

    SOURCE_NAME = "notarske_drazby"
    BASE_URL    = LISTING_BASE

    def __init__(self):
        super().__init__()
        from config_loader import get_sources
        cfg = get_sources().get(self.SOURCE_NAME, {})
        self.max_pages = int(cfg.get("max_pages", DEFAULT_MAX_PAGES))

    def scrape(self, criteria=None):
        """Prechadza listing (max_pages stran) a zbiera data z detailov."""
        parcels, seen = [], set()
        for page_parcels in self._scrape_listing_pages():
            for p in page_parcels:
                key = p.url.strip().lower() if p.url else id(p)
                if key not in seen:
                    seen.add(key)
                    parcels.append(p)
        return parcels

    def _listing_url(self, page):
        """Vrati URL listingu pre danu stranu (1-based)."""
        url = f"{LISTING_BASE}?{SEARCH_PARAMS}"
        if page > 1:
            url += f"&start={page}"
        return url

    def _scrape_listing_pages(self):
        """Generator: pre kazdu stranu (do max_pages) yieldi zoznam Parcel."""
        seen_ids = set()
        for page in range(1, self.max_pages + 1):
            url = self._listing_url(page)
            try:
                html = self.fetch_html(url)
            except Exception as exc:
                print(f"[{self.SOURCE_NAME}] listing strana {page} chyba: {exc}")
                break
            entries = self._parse_listing_html(html)
            new = [e for e in entries if e["act_id"] not in seen_ids]
            if not new:
                break
            seen_ids.update(e["act_id"] for e in new)
            page_parcels = []
            for entry in new:
                try:
                    detail_url  = f"{BASE_DOMAIN}/drazba?actId={entry['act_id']}"
                    detail_html = self.fetch_html(detail_url)
                    p = self._detail_to_parcel(detail_html, detail_url, entry)
                    if p:
                        page_parcels.append(p)
                except Exception as exc:
                    print(f"[{self.SOURCE_NAME}] detail {entry['act_id'][:8]} chyba: {exc}")
            yield page_parcels

    def parse_listings(self, html):
        """BaseScraper kontrakt — vracia zoznam entry dict zo stranky listingu."""
        return self._parse_listing_html(html)

    def _parse_listing_html(self, html):
        """Zo HTML listingu extrahuje zoznam entry dictov pre drazby."""
        from bs4 import BeautifulSoup
        soup    = BeautifulSoup(html, "html.parser")
        entries = []
        table   = soup.find("table")
        if not table:
            return entries
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            if len(cells) < 4:
                continue
            typ = cells[3].get_text(strip=True).lower()
            if any(s in typ for s in _SKIP_TYPES):
                continue
            a = row.find("a", href=re.compile(r"actId", re.I))
            if not a:
                continue
            act_id = re.search(r"actId=([a-f0-9]+)", a["href"], re.I)
            if not act_id:
                continue
            entries.append({
                "act_id":      act_id.group(1),
                "ncr":         cells[0].get_text(strip=True),
                "drazobnik":   cells[1].get_text(strip=True)[:80],
                "navrhovatel": cells[2].get_text(strip=True)[:80],
                "typ":         cells[3].get_text(strip=True),
                "datum":       cells[5].get_text(strip=True) if len(cells) > 5 else "",
            })
        return entries

    def _detail_to_parcel(self, html, detail_url, entry):
        """Z HTML detailu drazby extrahuje Parcel alebo None.

        parcel.url = PDF odkaz (Oznamenie o drazbe) ak dostupny, inak detail_url.
        Cena a vymera nie su v HTML (len v skenovanom PDF) -> price=0, area=0.
        """
        from bs4 import BeautifulSoup
        soup    = BeautifulSoup(html, "html.parser")
        text    = soup.get_text(separator=" ", strip=True)

        title        = extract_detail_title(soup, text)
        location     = extract_detail_location(text)
        datum_drazby = extract_detail_datum(text)
        navrhovatel  = extract_detail_navrhovatel(text)
        pdf_url      = extract_pdf_url(soup)

        # Ziadne uzitocne data -> preskoc
        if not title and not location:
            return None

        # parcel.url = priamy klikaci PDF odkaz (Oznamenie o drazbe)
        # Pouzivatel jednym klikom vidi cenu, vymeru a adresu predmetu v skene
        final_url = pdf_url if pdf_url else detail_url

        desc_parts = [
            f"NOTARSKA DRAZBA | NCRdr: {entry.get('ncr', '')}",
            f"Drazobnik: {entry.get('drazobnik', '')[:50]}",
            f"Navrhovatel: {navrhovatel or entry.get('navrhovatel', '')[:50]}",
            f"Termin: {datum_drazby or entry.get('datum', '')}",
            f"Miesto konania: {location}",
            f"Predmet: {title}",
            ">> Cena a vymera su v PDF (klik na odkaz Oznamenie o drazbe).",
        ]
        description = " | ".join(p for p in desc_parts if p.split(": ", 1)[-1].strip())

        return self._make_parcel(
            title        = title or f"Notarska drazba NCRdr {entry.get('ncr', '')}",
            url          = final_url,
            price_eur    = 0.0,
            area_sqm     = 0.0,
            location_text= location,
            source_portal= SOURCE_NAME,
            description  = description,
        )



    def parse_listings(self, html):
        """BaseScraper kontrakt - vracia zoznam entry dict zo stranky listingu."""
        return self._parse_listing_html(html)


# ----------------------------------------------------------------
# Samostatne funkcie (testovatelne bez instancie)
# ----------------------------------------------------------------

def extract_pdf_url(soup):
    """Najde priamy PDF odkaz (Oznamenie o drazbe) v HTML detaile.

    Vracia absolutnu https://www.notar.sk/listina/... URL
    alebo prazdny retazec ak nie je dostupna.
    """
    # Primarne: <a href="/listina/...pdf">
    a = soup.find("a", href=_PDF_URL_RE)
    if not a:
        # Fallback: <a> obsahujuci .pdf v href (akykolvek odkaz)
        for tag in soup.find_all("a", href=True):
            if ".pdf" in tag["href"].lower() and "listina" in tag["href"].lower():
                a = tag
                break
    if not a:
        return ""
    href = a["href"]
    if href.startswith("http"):
        return href
    return BASE_DOMAIN + href


def extract_detail_title(soup, text):
    """Extrahuje typ/nazov predmetu drazby z HTML detailu.

    Priorita: 'Druh predmetu drazby: X' -> napr. 'Nehnutelna vec'.
    """
    # 1. Druh predmetu drazby: X
    m = re.search(r"Druh predmetu[^:]*:\s*([^\n|]{3,80}?)(?:\s+S\xfavisiace|\s*$)", text)
    if m:
        return m.group(1).strip()[:120]
    # 2. H-tagy s kluczovymi slovami
    for tag in soup.find_all(["h1", "h2", "h3"]):
        t = tag.get_text(strip=True)
        if any(k in t.lower() for k in ["predmet", "dra\u017eb", "nehnutel", "pozemok"]):
            return t[:120]
    h1 = soup.find("h1")
    return h1.get_text(strip=True)[:120] if h1 else ""


def extract_detail_location(text):
    """Extrahuje miesto konania drazby (adresa mesta) z textu detailu.

    Poznamka: NCRdr HTML neobsahuje adresu predmetu drazby (len v PDF).
    Pouzijeme 'Miesto konania drazby' ako orientacnu lokalitu pre GIS.
    Format: 'Hlavna 1, Trnava 91701' alebo 'Bratislava 81102'.
    """
    m = _LOCATION_RE.search(text)
    if m:
        raw = m.group(1).strip()
        # Orez za "Blizšie oznacenie" alebo "Datum"
        raw = re.split(r"\s+Bli\u017e\u0161ie|\s+D\u00e1tum", raw)[0].strip()
        return raw[:60]
    # Fallback: Obec / Mesto
    for pat in [
        r"[Oo]bec\s*[:\-]?\s*([A-Z\u00c0-\u017e][a-z\u00c0-\u017e][^\n,;]{1,40})",
        r"[Mm]esto\s*[:\-]?\s*([A-Z\u00c0-\u017e][a-z\u00c0-\u017e][^\n,;]{1,40})",
    ]:
        fm = re.search(pat, text)
        if fm:
            return fm.group(1).strip()[:60]
    return ""


def extract_detail_datum(text):
    """Extrahuje datum a cas otvorenia drazby z textu detailu."""
    m = re.search(
        r"D\u00e1tum a \u010das otvorenia dra\u017eby:\s*([\d\.\s:]{10,25})", text)
    return m.group(1).strip() if m else ""


def extract_detail_navrhovatel(text):
    """Extrahuje meno navrhovatela (banky / veritela) z textu detailu."""
    m = re.search(
        r"Navrhovate\u013e[^:]*:\s*([^,\n]{3,60}),", text)
    return m.group(1).strip()[:60] if m else ""


def extract_detail_price(text):
    """Extrahuje vyvolavaci cenu z textu. 0.0 ak nenajde (cena je v PDF)."""
    m = _PRICE_RE.search(text)
    if m:
        raw = m.group(1).replace(" ", "").replace(".", "").replace(",", "")
        try:
            return float(raw)
        except ValueError:
            pass
    return 0.0


def extract_detail_area(text):
    """Extrahuje vymeru v m2 z textu. 0.0 ak nenajde (vymera je v PDF)."""
    m = _AREA_RE.search(text)
    if m:
        raw = m.group(1).replace(" ", "")
        try:
            return float(raw)
        except ValueError:
            pass
    return 0.0


