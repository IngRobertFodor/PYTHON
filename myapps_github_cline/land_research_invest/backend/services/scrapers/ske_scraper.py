"""SKE (Slovenska komora exekutorov) - Drazobne vyhlasky scraper
================================================================
Parsuje verejnu HTML tabulku drazobnych vyhlasok na ske.sk.
Zdroj: https://ske.sk/drazobne-vyhlasky/

Listing: HTML tabulka (21 riadkov/stranu, 7 stran)
  Stlpce: Cislo OV | Cislo EX | Datum | Typ majetku |
          Druh zverejnenia | Exekutor | Uverejnene dna
  Strankovanie: ?dv_page=N
  Filter: len Typ majetku = Nehnutelnost

Detail: https://ske.sk/drazobna-vyhlaska-detail/?ov_podanie_id=NNNNN
  Obsahuje VSETKY relevantne udaje priamo v HTML:
    - Najnizsie podanie (EUR) + Odhad hodnoty
    - Datum + cas + miesto drazby
    - Obec + katastralne uzemie + LV
    - Vsetky parcely s vymerami (sucet = celkova vymera)
    - Vlastnik + Cislo zverejnenia v OV
"""

import re
from services.scrapers.base_scraper import BaseScraper

SOURCE_NAME  = "ske_drazobne_vyhlasky"
BASE_DOMAIN  = "https://www.ske.sk"
LISTING_URL  = "https://www.ske.sk/drazobne-vyhlasky/"

# Regex vzory pre extrakciu z detailu
_PRICE_RE    = re.compile(
    r"Najni\u017e\u0161ie podanie\s+([\d\s]+(?:[.,]\d{1,2})?)\s*\u20ac", re.I)
_ODHAD_RE    = re.compile(
    r"Odhad hodnoty\s+([\d\s]+(?:[.,]\d{1,2})?)\s*\u20ac", re.I)
_DATUM_DR_RE = re.compile(
    r"D\u00e1tum dra\u017eby\s+(\d{1,2}\.\d{1,2}\.\d{4})")
_CAS_DR_RE   = re.compile(
    r"\u010cas dra\u017eby\s+(\d{1,2}[:.]\d{2})")
_MIESTO_RE   = re.compile(
    r"Miesto dra\u017eby\s+([^\n]{5,80}?)(?:\s+Obhliadka|\s+D\u00e1tum obhl)")
_DATUM_OBH_RE= re.compile(
    r"D\u00e1tum obhliadky\s+(\d{1,2}\.\d{1,2}\.\d{4})")
_OBEC_RE     = re.compile(
    r"Obec:\s*([A-Z\u00c0-\u017e][^\n,;]{1,40}?)(?:,|\s+Kataster)")
_KAT_RE      = re.compile(
    r"Kataster:\s*([A-Z\u00c0-\u017e][^\n,;]{1,40}?)(?:,|\s+LV)")
_LV_RE       = re.compile(r"LV:\s*(\d+)")
_VYMERA_RE   = re.compile(r"v\u00fdmera\s+(\d+)", re.I)
_VLASTNIK_RE = re.compile(
    r"Vlastn\u00edk\s+([^\n]{5,80}?)(?:,\s*podiel|\s+Z\u00e1vady)")
_OV_CISLO_RE = re.compile(
    r"\u010c\u00edslo zverejnenia v OV\s+(X\d+)")
_NEHNUT_KEYS = ["nehnutelnost", "nehnut"]
_SKIP_DRUH   = ["zrusenie", "oprava", "zmena"]


class SkeScraper(BaseScraper):
    """Scraper drazobnych vyhlasok SKE (ske.sk).

    Vytiahne zo SKE detailu vsetky dostupne udaje:
    cenu (Najnizsie podanie), vymeru (sucet vsetkych parciel),
    obec/kataster/LV, datum+miesto drazby+obhliadky, vlastnika, OV cislo.
    """

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
                    detail_url = (f"{BASE_DOMAIN}/drazobna-vyhlaska-detail/"
                                  f"?ov_podanie_id={entry['ov_id']}")
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
            typ  = cells[3].get_text(strip=True).lower()
            if not any(k in typ for k in _NEHNUT_KEYS):
                continue
            druh = cells[4].get_text(strip=True).lower()
            if any(k in druh for k in _SKIP_DRUH):
                continue
            a = row.find("a", href=re.compile(r"ov_podanie_id", re.I))
            if not a:
                continue
            m = re.search(r"ov_podanie_id=(\d+)", a["href"])
            if not m:
                continue
            entries.append({
                "ov_id":    m.group(1),
                "cislo_ov": cells[0].get_text(strip=True),
                "cislo_ex": cells[1].get_text(strip=True),
                "datum":    cells[2].get_text(strip=True),
                "exekutor": cells[5].get_text(strip=True)[:60] if len(cells) > 5 else "",
                "druh":     cells[4].get_text(strip=True),
            })
        return entries

    def _detail_to_parcel(self, html, url, entry):
        """Z HTML detailu drazby extrahuje plny Parcel so vsetkymi datami."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ", strip=True)

        price      = extract_detail_price(text)
        odhad      = extract_detail_odhad(text)
        area       = extract_detail_area(text)
        obec       = extract_detail_obec(text)
        kataster   = extract_detail_kataster(text)
        lv         = extract_detail_lv(text)
        datum_dr   = extract_detail_datum_drazby(text)
        cas_dr     = extract_detail_cas_drazby(text)
        miesto_dr  = extract_detail_miesto(text)
        datum_obhl = extract_detail_datum_obhliadky(text)
        vlastnik   = extract_detail_vlastnik(text)
        ov_cislo   = extract_detail_ov_cislo(text)
        parcely    = extract_detail_parcely_list(text)
        title      = extract_detail_title(soup)

        location = obec or kataster or miesto_dr
        if not location:
            return None
        if not title:
            title = f"Exek\u00fatork\u00e1 dra\u017eba {entry.get('cislo_ov', '')}"

        # Zostavenie boheho popisu
        desc = []
        desc.append(f"EXEK. DRA\u017dBA | {entry.get('cislo_ov', '')} | EX: {entry.get('cislo_ex', '')}")
        desc.append(f"Exek\u00fator: {entry.get('exekutor', '')}")
        if datum_dr:
            desc.append(f"Dr\u00e1\u017eba: {datum_dr}{' ' + cas_dr if cas_dr else ''}")
        if miesto_dr:
            desc.append(f"Miesto: {miesto_dr}")
        if datum_obhl:
            desc.append(f"Obhliadka: {datum_obhl}")
        if obec:
            ku = f" / Kat: {kataster}" if kataster and kataster != obec else ""
            desc.append(f"Obec: {obec}{ku}")
        if lv:
            desc.append(f"LV: {lv}")
        if parcely:
            desc.append(f"Parcely ({len(parcely)}): {'; '.join(parcely[:3])}")
        if vlastnik:
            desc.append(f"Vlastn\u00edk: {vlastnik}")
        if odhad > 0 and price == 0:
            desc.append(f"Odhad: {odhad:,.0f} \u20ac")
        if ov_cislo:
            desc.append(f"OV: {ov_cislo}")

        return self._make_parcel(
            title         = title,
            url           = url,
            price_eur     = price,
            area_sqm      = area,
            location_text = location,
            source_portal = SOURCE_NAME,
            parcel_number = lv,
            description   = " | ".join(desc)[:500],
        )


# ----------------------------------------------------------------
# Standalone funkcie (testovatelne bez instancie)
# ----------------------------------------------------------------

def extract_detail_price(text):
    """Extrahuje Najnizsie podanie (EUR). 0.0 ak nenajde alebo je 0."""
    m = _PRICE_RE.search(text)
    if m:
        raw = m.group(1).replace(" ", "").replace(",", ".").replace("\u00a0", "")
        try:
            v = float(raw)
            return v if v > 0 else 0.0
        except ValueError:
            pass
    return 0.0


def extract_detail_odhad(text):
    """Extrahuje Odhad hodnoty (EUR). 0.0 ak nenajde."""
    m = _ODHAD_RE.search(text)
    if m:
        raw = m.group(1).replace(" ", "").replace(",", ".").replace("\u00a0", "")
        try:
            return float(raw)
        except ValueError:
            pass
    return 0.0


def extract_detail_area(text):
    """Extrahuje celkovu vymeru = SUCET vsetkych parciel (m2)."""
    total = sum(int(m.group(1)) for m in _VYMERA_RE.finditer(text))
    return float(total) if total > 0 else 0.0


def extract_detail_parcely_list(text):
    """Vracia zoznam strucnych popisov parciel ['C 3377 (1118m2)', ...]."""
    parcely = []
    pat = re.compile(
        r"Parcela\s+(?:parcela registra\s+)?[\"']?([ABCDE])[\"']?,?\s*([\d/]+),\s*v\u00fdmera\s+(\d+)",
        re.I)
    for m in pat.finditer(text):
        parcely.append(f"{m.group(1)} {m.group(2)} ({m.group(3)}m\u00b2)")
    return parcely


def extract_detail_obec(text):
    """Extrahuje Obec z textu detailu."""
    m = _OBEC_RE.search(text)
    return m.group(1).strip()[:50] if m else ""


def extract_detail_kataster(text):
    """Extrahuje Katastralne uzemie z textu detailu."""
    m = _KAT_RE.search(text)
    return m.group(1).strip()[:50] if m else ""


def extract_detail_lv(text):
    """Extrahuje cislo LV z textu detailu."""
    m = _LV_RE.search(text)
    return m.group(1) if m else ""


def extract_detail_datum_drazby(text):
    """Extrahuje datum drazby (DD.MM.YYYY)."""
    m = _DATUM_DR_RE.search(text)
    return m.group(1) if m else ""


def extract_detail_cas_drazby(text):
    """Extrahuje cas drazby (HH:MM alebo HH.MM)."""
    m = _CAS_DR_RE.search(text)
    return m.group(1) if m else ""


def extract_detail_miesto(text):
    """Extrahuje miesto konania drazby."""
    m = _MIESTO_RE.search(text)
    return m.group(1).strip()[:80] if m else ""


def extract_detail_datum_obhliadky(text):
    """Extrahuje datum obhliadky."""
    m = _DATUM_OBH_RE.search(text)
    return m.group(1) if m else ""


def extract_detail_vlastnik(text):
    """Extrahuje meno vlastnika nehnutelnosti."""
    m = _VLASTNIK_RE.search(text)
    return m.group(1).strip()[:60] if m else ""


def extract_detail_ov_cislo(text):
    """Extrahuje cislo zverejnenia v OV (napr. X047677)."""
    m = _OV_CISLO_RE.search(text)
    return m.group(1) if m else ""


def extract_detail_title(soup):
    """Extrahuje nadpis predmetu drazby z HTML."""
    for tag in soup.find_all(["h1", "h2", "h3", "strong", "b"]):
        t = tag.get_text(strip=True)
        if any(k in t.lower() for k in ["predmet", "pozemok", "nehnutel", "parcela"]):
            return t[:120]
    h1 = soup.find("h1")
    return h1.get_text(strip=True)[:120] if h1 else ""


def extract_detail_location(text):
    """Extrahuje obec/kataster ako location_text (spatna kompatibilita)."""
    return extract_detail_obec(text) or extract_detail_kataster(text)

