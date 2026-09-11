"""SKE (Slovenska komora exekutorov) - Drazobne vyhlasky scraper
================================================================
Parsuje verejnu HTML tabulku drazobnych vyhlasok na ske.sk.
Zdroj: https://ske.sk/drazobne-vyhlasky/
Data su preberane z Obchodneho vestnika MS SR.

Listing: HTML tabulka (21 riadkov/stranu, 7 stran)
  Stlpce: Cislo OV | Cislo EX | Datum drazby | Typ majetku |
          Druh zverejnenia | Exekutor | Uverejnene dna
  Strankovanie: ?dv_page=N
  Filter: len Typ majetku = Nehnutelnost

Detail: https://ske.sk/drazobna-vyhlaska-detail/?ov_podanie_id=NNNNN
  Obsahuje popis predmetu drazby, katastralnu obec, parcelu, LV.
  Neobsahuje cenu (cena az v PDF OV) -> price_eur = 0.0

Poznamka: cena drazby nie je v HTML detaile - je len v OV PDF.
  price_eur = 0.0 je spravne (investor si overuje OV rucne).
"""

import re
from services.scrapers.base_scraper import BaseScraper

SOURCE_NAME  = "ske_drazobne_vyhlasky"
BASE_DOMAIN  = "https://www.ske.sk"
LISTING_URL  = "https://www.ske.sk/drazobne-vyhlasky/"


class SkeScraper(BaseScraper):
    """Scraper drazobnych vyhlasok SKE (ske.sk)."""

    SOURCE_NAME = "ske_drazobne_vyhlasky"
    BASE_URL    = LISTING_URL

    def scrape(self, criteria=None):
        """Prechadza vsetky strany listingu, filtruje nehnutelnosti."""
        seen, results = set(), []
        for page in range(1, 51):
            url = self._page_url(LISTING_URL, page, "dv_page")
            try:
                html = self.fetch_html(url)
            except Exception as exc:
                print(f"[{self.SOURCE_NAME}] strana {page} chyba: {exc}")
                break
            entries = self._parse_listing_html(html)
            new = [e for e in entries if e["ov_id"] not in seen]
            if not new:
                break
            seen.update(e["ov_id"] for e in new)
            for entry in new:
                try:
                    detail_url  = f"{BASE_DOMAIN}/drazobna-vyhlaska-detail/?ov_podanie_id={entry['ov_id']}"
                    detail_html = self.fetch_html(detail_url)
                    p = self._detail_to_parcel(detail_html, detail_url, entry)
                    if p:
                        results.append(p)
                except Exception as exc:
                    print(f"[{self.SOURCE_NAME}] detail {entry['ov_id']} chyba: {exc}")
        return results

    def parse_listings(self, html):
        """BaseScraper kontrakt - vracia zoznam entry dict."""
        return self._parse_listing_html(html)

    def _parse_listing_html(self, html):
        """Extrahuje zoznam entry dictov z HTML tabulky SKE."""
        from bs4 import BeautifulSoup
        soup    = BeautifulSoup(html, "html.parser")
        entries = []
        tbl     = soup.find("table")
        if not tbl:
            return entries
        for row in tbl.find_all("tr")[1:]:
            cells = row.find_all("td")
            if len(cells) < 5:
                continue
            # Filter: len nehnutelnosti
            typ   = cells[3].get_text(strip=True).lower()
            if not any(k in typ for k in _NEHNUT_KEYS):
                continue
            # Filter: preskoc zrusenia/opravy
            druh  = cells[4].get_text(strip=True).lower()
            if any(k in druh for k in _SKIP_DRUH):
                continue
            # Ziskaj ov_podanie_id z odkazu
            a     = row.find("a", href=re.compile(r"ov_podanie_id", re.I))
            if not a:
                continue
            m     = re.search(r"ov_podanie_id=(\d+)", a["href"])
            if not m:
                continue
            entries.append({
                "ov_id":     m.group(1),
                "cislo_ov":  cells[0].get_text(strip=True),
                "cislo_ex":  cells[1].get_text(strip=True),
                "datum":     cells[2].get_text(strip=True),
                "exekutor":  cells[5].get_text(strip=True)[:60] if len(cells) > 5 else "",
                "druh":      cells[4].get_text(strip=True),
            })
        return entries

    def _detail_to_parcel(self, html, url, entry):
        """Z HTML detailu drazby extrahuje Parcel."""
        from bs4 import BeautifulSoup
        soup  = BeautifulSoup(html, "html.parser")
        text  = soup.get_text(separator=" ", strip=True)
        title    = extract_detail_title(soup)
        location = extract_detail_location(text)
        area     = extract_detail_area(text)
        if not title and not location:
            return None
        desc = (
            f"EXEKUTORSKA DRAZBA | {entry.get('cislo_ov','')} | "
            f"EX: {entry.get('cislo_ex','')} | "
            f"datum: {entry.get('datum','')} | "
            f"{entry.get('exekutor','')}"
        )
        return self._make_parcel(
            title         = title or f"Drazba {entry.get('cislo_ov','')}",
            url           = url,
            price_eur     = 0.0,
            area_sqm      = area,
            location_text = location,
            source_portal = SOURCE_NAME,
            description   = desc,
        )


# ----------------------------------------------------------------
# Samostatne funkcie (testovatelne bez instancie)
# ----------------------------------------------------------------

def extract_detail_title(soup):
    """Extrahuje popis predmetu drazby z HTML detailu."""
    for tag in soup.find_all(["h1", "h2", "h3", "strong", "b"]):
        t = tag.get_text(strip=True)
        if any(k in t.lower() for k in ["predmet", "pozemok", "nehnutel", "parcela"]):
            return t[:120]
    h1 = soup.find("h1")
    return h1.get_text(strip=True)[:120] if h1 else ""


def extract_detail_location(text):
    """Extrahuje katastralnu obec z textu detailu."""
    for pat in [
        r"[Kk]atastr\w*\s+\w*\s*[:\-]?\s*([A-Z\u00c0-\u017e][a-z\u00c0-\u017e][^\n,;]{1,40})",
        r"[Oo]bec\s*[:\-]?\s*([A-Z\u00c0-\u017e][a-z\u00c0-\u017e][^\n,;]{1,40})",
        r"[Mm]esto\s*[:\-]?\s*([A-Z\u00c0-\u017e][a-z\u00c0-\u017e][^\n,;]{1,40})",
    ]:
        m = re.search(pat, text)
        if m:
            return m.group(1).strip()[:60]
    return ""


def extract_detail_area(text):
    """Extrahuje vymeru pozemku v m2 z textu detailu."""
    m = re.search(r"([\d\s]{1,8})\s*m\s*(?:2|\xb2|²)", text, re.IGNORECASE)
    if m:
        raw = m.group(1).replace(" ", "")
        try:
            return float(raw)
        except ValueError:
            pass
    return 0.0


_NEHNUT_KEYS = ["nehnutelnost", "nehnut"]
_SKIP_DRUH   = ["zrusenie", "oprava", "zmena"]
