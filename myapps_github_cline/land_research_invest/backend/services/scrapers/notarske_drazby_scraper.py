"""Notarske drazby scraper
================================
Parsuje Notarsky centralny register drazob (notar.sk).

Listing: HTML tabulka so zoznamom drazieb
  - 6 stlpcov: NCRdr cislo | Drazobnik | Navrhovatel | Typ | prazdne | Datum
  - Odkaz na detail: drazba?actId=<hex_id>

Detail: HTML stranka jednotlivej drazby
  - Predmet drazby, Lokalita, Vymera, Najnizsie podanie (vyvolavacia cena)

Poznamka: PDF v detaile je skenovany (OCR faza) - priorita je HTML text.
"""

import re
from services.scrapers.base_scraper import BaseScraper

SOURCE_NAME = "notarske_drazby"
BASE_DOMAIN = "https://www.notar.sk"
LISTING_URL = "https://www.notar.sk/notarsky-centralny-register-drazob/"

_SKIP_TYPES = ["upustenie", "zrusenie", "zanik"]
_PRICE_RE   = re.compile(
    r"(\d[\d\s\.]{1,10}\d)[,\.]?[-\s]?\s*(?:eur|EUR|\u20ac)", re.IGNORECASE)
_AREA_RE    = re.compile(r"(\d[\d\s]{0,5}?)\s*m\s*(?:2|\xb2|\u00b2)", re.IGNORECASE)


class NotarskeDrazbyaScraper(BaseScraper):
    """Scraper Notarskeho centralneho registra drazob (notar.sk)."""

    SOURCE_NAME = "notarske_drazby"
    BASE_URL    = LISTING_URL

    def scrape(self, criteria=None):
        """Prechadza listing (vsetky strany) a zbiera data z detailov."""
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
            url = self._page_url(LISTING_URL, page, "page")
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
                    print(f"[{self.SOURCE_NAME}] detail chyba: {exc}")
            yield page_parcels

    def parse_listings(self, html):
        """BaseScraper kontrakt - vracia zoznam entry dict zo stranky listingu."""
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
            href   = a["href"]
            act_id = re.search(r"actId=([a-f0-9]+)", href, re.I)
            if not act_id:
                continue
            entries.append({
                "act_id":    act_id.group(1),
                "ncr":       cells[0].get_text(strip=True),
                "drazobnik": cells[1].get_text(strip=True)[:60],
                "typ":       cells[3].get_text(strip=True),
                "datum":     cells[5].get_text(strip=True) if len(cells) > 5 else "",
            })
        return entries

    def _detail_to_parcel(self, html, url, entry):
        """Z HTML detailu drazby extrahuje Parcel alebo None."""
        from bs4 import BeautifulSoup
        soup  = BeautifulSoup(html, "html.parser")
        text  = soup.get_text(separator=" ", strip=True)
        title    = extract_detail_title(soup, text)
        location = extract_detail_location(text)
        price    = extract_detail_price(text)
        area     = extract_detail_area(text)
        if not title and not location and price == 0.0:
            return None
        desc = (
            f"NOTARSKA DRAZBA | {entry.get('ncr','')} | "
            f"{entry.get('drazobnik','')} | datum: {entry.get('datum','')} | "
            f"typ: {entry.get('typ','')}"
        )
        return self._make_parcel(
            title=title or f"Drazba {entry.get('ncr','')}",
            url=url,
            price_eur=price,
            area_sqm=area,
            location_text=location,
            source_portal=SOURCE_NAME,
            description=desc,
        )


# ----------------------------------------------------------------
# Samostatne funkcie (testovatelne bez instancie)
# ----------------------------------------------------------------

def extract_detail_title(soup, text):
    """Extrahuje nadpis predmetu drazby z HTML detailu."""
    for tag in soup.find_all(["h1", "h2", "h3"]):
        t = tag.get_text(strip=True)
        if any(k in t.lower() for k in ["predmet", "dra\u017eb", "nehnutel", "pozemok"]):
            return t[:120]
    h1 = soup.find("h1")
    return h1.get_text(strip=True)[:120] if h1 else ""


def extract_detail_location(text):
    """Extrahuje obec/mesto predmetu drazby z textu detailu."""
    for pat in [
        r"[Oo]bec\s*[:\-]?\s*([A-Z\u00c0-\u017e][a-z\u00c0-\u017e][^\n,;]{1,40})",
        r"[Mm]esto\s*[:\-]?\s*([A-Z\u00c0-\u017e][a-z\u00c0-\u017e][^\n,;]{1,40})",
        r"[Kk]atastr\w*\s+\w*\s*[:\-]?\s*([A-Z\u00c0-\u017e][a-z\u00c0-\u017e][^\n,;]{1,40})",
    ]:
        m = re.search(pat, text)
        if m:
            return m.group(1).strip()[:60]
    return ""


def extract_detail_price(text):
    """Extrahuje vyvolavaci cenu z textu detailu. 0.0 ak nenajde."""
    m = _PRICE_RE.search(text)
    if m:
        raw = m.group(1).replace(" ", "").replace(".", "").replace(",", "")
        try:
            return float(raw)
        except ValueError:
            pass
    return 0.0


def extract_detail_area(text):
    """Extrahuje vymeru pozemku v m2 z textu detailu. 0.0 ak nenajde."""
    m = _AREA_RE.search(text)
    if m:
        raw = m.group(1).replace(" ", "")
        try:
            return float(raw)
        except ValueError:
            pass
    return 0.0

