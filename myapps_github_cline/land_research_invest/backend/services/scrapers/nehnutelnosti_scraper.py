"""Nehnutelnosti.sk scraper
============================
Parsuje JSON-LD (schema.org) payload z Next.js SSR HTML.

Technicke detaily:
  - Stranka pouziva Next.js RSC payload: __next_f.push([1, "..."])
  - JSON-LD je v bloku oznacenom T23c11 (RSC text chunk ID)
  - Payload je dvojnasob escapovany -> treba unescape pred json.loads
  - Hlavne data su v @graph[].mainEntity.itemListElement[].item

Kluce v item:
  name              -> title
  priceSpecification.price -> price_eur
  floorSize.value   -> area_sqm  (fallback: regex z description)
  url               -> url (absolutna)
  category          -> filter pozemkov
  description       -> popis
"""

import re
import json
from services.scrapers.base_scraper import BaseScraper

SOURCE_NAME = "nehnutelnosti_sk"
BASE_DOMAIN = "https://www.nehnutelnosti.sk"

# URL pre vyhladavanie pozemkov na predaj (IBV/rodinne domy)
SEARCH_URLS = [
    "https://www.nehnutelnosti.sk/vysledky/pozemky/bratislavsky-kraj/predaj/",
    "https://www.nehnutelnosti.sk/vysledky/pozemky/trnavsky-kraj/predaj/",
]

# Kategorie ktore su relevantne pre IBV/stavebne pozemky
LAND_CATEGORIES = {
    "Pozemok pre rodinné domy",
    "Stavebny pozemok",
    "Pozemok pre IBV",
    "Pozemok",
}

# Regex pre vyjadrenie vymery v description (fallback)
AREA_RE = re.compile(r'(\d[\d ]{0,6}?)\s*m2', re.IGNORECASE)


class NehnutelnostiScraper(BaseScraper):
    SOURCE_NAME = "nehnutelnosti_sk"
    BASE_URL    = SEARCH_URLS[0]

    def get_listing_urls(self, criteria=None):
        return SEARCH_URLS

    def parse_listings(self, html):
        """
        Parsuje HTML stranky nehnutelnosti.sk.
        Extrahuje JSON-LD z RSC payloadu (T23c11 blok).
        """
        try:
            jsonld = extract_jsonld(html)
        except Exception as exc:
            print(f"[{self.SOURCE_NAME}] JSON-LD extract failed: {exc}")
            return []

        items = extract_items_from_graph(jsonld)
        parcels = []
        for it in items:
            try:
                p = item_to_parcel(it)
                if p is not None:
                    parcels.append(p)
            except Exception as exc:
                print(f"[{self.SOURCE_NAME}] item parse error: {exc}")
        return parcels


# ----------------------------------------------------------------
# Samostatne funkcie (testovatelne bez instancie)
# ----------------------------------------------------------------

def extract_jsonld(html):
    """
    Extrahuje a parsuje JSON-LD z RSC payloadu.
    Vracia dict (schema.org @context/@graph).
    Vyvolava ValueError ak nie je najdeny.
    """
    marker = "T23c11"
    idx = html.find(marker)
    if idx == -1:
        raise ValueError(f"Marker '{marker}' nenajdeny v HTML")

    json_start = html.find('{', idx)
    if json_start == -1:
        raise ValueError("JSON objekt za markerom nenajdeny")

    # Najdi koniec JSON objektu (pocitaj zavorky)
    depth = 0
    json_end = json_start
    for i in range(json_start, min(json_start + 600_000, len(html))):
        ch = html[i]
        if ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                json_end = i + 1
                break

    raw = html[json_start:json_end]
    unescaped = _unescape_rsc(raw)
    return json.loads(unescaped)


def extract_items_from_graph(jsonld):
    """
    Z @graph najde mainEntity.itemListElement a vrati zoznam item dictov.
    """
    for node in jsonld.get('@graph', []):
        if 'mainEntity' not in node:
            continue
        me = node['mainEntity']
        elements = me.get('itemListElement', [])
        return [e['item'] for e in elements if 'item' in e]
    return []


def item_to_parcel(item):
    """
    Konvertuje schema.org item dict na Parcel.
    Vracia None ak nie je pozemok alebo chyba cena.
    """
    # Filter: len pozemky
    category = item.get('category', '')
    acc_cat  = item.get('accommodationCategory', '')
    is_land  = (
        acc_cat == 'LAND'
        or any(c in category for c in ('Pozemok', 'pozemok', 'IBV'))
    )
    if not is_land:
        return None

    # Cena
    ps    = item.get('priceSpecification', {})
    price = float(ps.get('price', 0) or 0)
    if price <= 1:
        return None   # cena 0 alebo 1 = neplatna

    # Vymera - prednostne floorSize, fallback regex
    area  = 0.0
    fs    = item.get('floorSize')
    if isinstance(fs, dict) and fs.get('value'):
        area = float(fs['value'])
    if area <= 0:
        desc  = item.get('description', '')
        m     = AREA_RE.search(desc)
        if m:
            area = float(m.group(1).replace(' ', ''))

    # URL
    url = item.get('url', '')
    if url and not url.startswith('http'):
        url = BASE_DOMAIN + url

    # Lokalita - z nazvu (v zatvorke) alebo z URL
    title = item.get('name', '')
    location = _extract_location(title, url)

    from services.scrapers.base_scraper import BaseScraper
    return BaseScraper._make_parcel(
        title        = title,
        url          = url,
        price_eur    = price,
        area_sqm     = area,
        location_text= location,
        source_portal= SOURCE_NAME,
        description  = item.get('description', '')[:500],
    )


def _extract_location(title, url):
    """
    Vytiahne lokalitu z nazvu inzeratu (v zatvorke) alebo z URL.
    Priklady:
      '... (Chorvatsky Grob)' -> 'Chorvatsky Grob'
      '.../predaj-pozemky-senec-...' -> 'senec'
    """
    # Z nazvu: hladaj poslednu zatvorku
    m = re.search(r'\(([^)]{3,40})\)\s*$', title)
    if m:
        return m.group(1).strip()
    # Z URL: cast medzi 'pozemky-' a nasledujucim '-'
    m2 = re.search(r'/pozemky[^/]*?-([a-z][a-z-]{2,30})(?:-[a-z]|-\d|/|$)', url)
    if m2:
        return m2.group(1).replace('-', ' ').title()
    return ''


def _unescape_rsc(raw):
    #RSC double-escaped string unescape
    BSLN = chr(92) + chr(110)
    BSLQ = chr(92) + chr(34)
    DBLN = chr(92)*2 + chr(110)
    DBLQ = chr(92)*2 + chr(34)
    return (
        raw
        .replace(DBLN, chr(32))
        .replace(DBLQ, chr(1))
        .replace(BSLN, chr(10))
        .replace(BSLQ, chr(34))
        .replace(chr(92)*2, chr(92))
        .replace(chr(1), chr(34))
    )
