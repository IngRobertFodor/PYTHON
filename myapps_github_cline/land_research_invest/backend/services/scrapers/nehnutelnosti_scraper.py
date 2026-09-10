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
import unicodedata
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
    Extrahuje a parsuje JSON-LD z RSC payloadu (self.__next_f.push).
    Vracia dict (schema.org @context/@graph).
    Vyvolava ValueError ak nie je najdeny.

    Poznamka: Next.js RSC format pouziva self.__next_f.push([1,"..."]) kde
    JSON-LD je dvojnasobne escapovany string. Hladame blok obsahujuci
    '@context' + 'priceSpecification' bez pevneho markera (meni sa s deployom).
    """
    # Najdi vsetky RSC push bloky s JSON obsahom
    # Format: self.__next_f.push([1,"<escaped-json>"])
    # aj varianty: self.__next_f.push([1,"<chunk-id>:<escaped-json>"])
    candidates = re.finditer(
        r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)',
        html, re.DOTALL
    )

    for m in candidates:
        raw = m.group(1)
        # Hladame blok ktory obsahuje schema.org JSON-LD s priceSpecification
        if '"@context"' not in raw and '@context' not in raw:
            continue
        if 'priceSpecification' not in raw and 'itemListElement' not in raw:
            continue

        # Unescape dvojnasobne escapovany string
        try:
            unescaped = _unescape_rsc(raw)
            # Ak je to chunk "ID:JSON", odroznime ID prefix
            if unescaped.startswith('{'):
                return json.loads(unescaped)
            # Format "ChunkID:json" - najdi prvy {
            brace = unescaped.find('{')
            if brace >= 0:
                return json.loads(unescaped[brace:])
        except (json.JSONDecodeError, Exception):
            continue

    raise ValueError(
        "JSON-LD blok s priceSpecification nenajdeny v RSC payloade. "
        "Portál mohol zmenit strukturu HTML."
    )


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


# Znamy zoznam obci a mestskych casti v okruhu 70 km od Bratislavy.
# Pouziva sa pri extrakcii lokality z nazvu/URL inzeratu.
# Porovnanie je diakritika-necitlive (Lamac = Lamač).
ZNAME_OBCE = [
    # Bratislava - mestske casti
    "Vajnory", "Lamac", "Lamač", "Devín", "Devin", "Rača", "Raca",
    "Vinohrady", "Koliba", "Karlova Ves", "Ružinov", "Ruzinov",
    "Petržalka", "Petrzalka", "Nové Mesto", "Nove Mesto",
    "Staré Mesto", "Stare Mesto", "Dúbravka", "Dubravka",
    "Podunajské Biskupice", "Podunajske Biskupice",
    "Vrakuňa", "Vrakuna", "Záhorská Bystrica", "Zahorska Bystrica",
    "Devínska Nová Ves", "Devinska Nova Ves",
    "Rusovce", "Čunovo", "Cunovo", "Jarovce",
    # Okres Senec
    "Senec", "Ivanka pri Dunaji", "Ivanka",
    "Bernolákovo", "Bernolakovo",
    "Chorvátsky Grob", "Chorvatsky Grob",
    "Malinovo", "Most pri Bratislave",
    "Rovinka", "Dunajská Lužná", "Dunajska Luzna",
    "Miloslavov", "Tomášov", "Tomasov",
    "Nová Dedinka", "Nova Dedinka",
    "Hamuliakovo", "Šamorín", "Samorin",
    # Okres Pezinok
    "Pezinok", "Modra", "Svätý Jur", "Svaty Jur",
    "Slovenský Grob", "Slovensky Grob", "Limbach",
    "Viničné", "Vinicne", "Šenkvice", "Senkvice",
    "Budmerice", "Dubová", "Dubova",
    # Okres Malacky
    "Malacky", "Stupava", "Marianka", "Lozorno",
    "Zohor", "Záhorská Ves", "Zahorska Ves",
    "Plavecký Štvrtok", "Plavecky Stvrtok",
    "Borinka", "Gajary", "Kuchyňa", "Kuchyna",
    "Sološnica", "Solosnica", "Rohožník", "Rohoznik",
    # Okolie (do 70 km)
    "Svätý Jur", "Perneck", "Blatné", "Blatne",
]

# Normalizacna mapa: ASCII verzia -> originalny nazov
_OBEC_NORM: dict[str, str] = {}
for _o in ZNAME_OBCE:
    _key = unicodedata.normalize("NFD", _o.lower())
    _key = "".join(c for c in _key if unicodedata.category(c) != "Mn")
    if _key not in _OBEC_NORM:
        _OBEC_NORM[_key] = _o


def _normalize(s: str) -> str:
    """Odstrani diakritiku a vrati male pismena."""
    n = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in n if unicodedata.category(c) != "Mn")


def _extract_location(title: str, url: str) -> str:
    """
    Vytiahne lokalitu z inzeratu v 3 urovniach (od najpresnejsej):

    1. Zoznam znamych obci BA regionu - hlada v nazve aj URL slugu
       (diakritika-necitlive): 'Vajnory', 'Lamac', 'Senec'...
    2. Zatvorka v nazve: '... (Chorvatsky Grob)' -> 'Chorvatsky Grob'
    3. Fallback: posledne slovo URL slugu (ocistene)
    """
    title_n = _normalize(title)
    # Z URL vytiahneme slug (posledna cast cesty)
    slug = url.rstrip("/").split("/")[-1] if "/" in url else ""
    slug_n = _normalize(slug.replace("-", " "))

    # --- Uroven 1: zoznam znamych obci ---
    # Hladame od najdlhsich nazov (Chorvátsky Grob pred Grob)
    for obec_norm, obec_orig in sorted(
        _OBEC_NORM.items(), key=lambda x: -len(x[0])
    ):
        if obec_norm in title_n or obec_norm in slug_n:
            return obec_orig

    # --- Uroven 2: zatvorka v nazve ---
    m = re.search(r'\(([^)]{3,40})\)\s*$', title)
    if m:
        return m.group(1).strip()

    # --- Uroven 3: posledne slovo slugu ---
    if slug:
        parts = [p for p in slug.split("-") if len(p) > 2 and p.isalpha()]
        if parts:
            return parts[-1].title()

    return ""


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
