"""Topreality.sk scraper - parsuje HTML detail stranky."""
import re, json
from services.scrapers.base_scraper import BaseScraper
SOURCE_NAME = "topreality_sk"
BASE_DOMAIN  = "https://www.topreality.sk"
SEARCH_URLS = [
    "https://www.topreality.sk/pozemky/bratislavsky-kraj/predaj/",
    "https://www.topreality.sk/pozemky/trnavsky-kraj/predaj/",
]
_AREA_M2_RE     = re.compile('(\\d[\\d ]{0,5}?)\\s*m(?:²|2)(?=[^/\\d]|$)', re.IGNORECASE)
_AREA_ARE_RE    = re.compile('(\\d+)\\s*-?\\s*(?:arov|arovy|arovych|are)(?=[^a-z]|$)', re.IGNORECASE)
_DATA_PRICE_RE  = re.compile(r"""data-price=["'"](\d+)["'"]""")
_PRICE_CLASS_RE = re.compile(r"""class=["'"]price["'"][^>]*>\s*([\d\s\xa0]+)\s*\u20ac""")
_JSONLD_PAT     = re.compile(r"""<script[^>]+type=["'"]application/ld\+json["'"][^>]*>(.*?)</script>""", re.DOTALL | re.IGNORECASE)

class TopRealityScraper(BaseScraper):
    SOURCE_NAME = "topreality_sk"
    BASE_URL    = SEARCH_URLS[0]
    def get_listing_urls(self, criteria=None): return SEARCH_URLS
    def parse_listings(self, html):
        """Parsuje HTML detailovej stranky topreality.sk."""
        try: blocks = extract_jsonld_blocks(html)
        except Exception as exc: print(f"[{self.SOURCE_NAME}] extract err: {exc}"); return []
        try: parcel = listing_to_parcel(blocks, html)
        except Exception as exc: print(f"[{self.SOURCE_NAME}] parse err: {exc}"); return []
        return [] if parcel is None else [parcel]

def _fix_json_nl(s):
    """Escapuje literal newlines uvnutri JSON string hodnot."""
    result, in_str, i = [], False, 0
    while i < len(s):
        c = s[i]
        if c == chr(34) and (i == 0 or s[i-1] != chr(92)): in_str = not in_str; result.append(c)
        elif in_str and c == chr(10): result.append(chr(92) + "n")
        elif in_str and c == chr(13): result.append(chr(92) + "r")
        else: result.append(c)
        i += 1
    return "".join(result)

def extract_jsonld_blocks(html):
    """Najde vsetky ld+json bloky. Automaticky fixuje literal newlines."""
    blocks = []
    for m in _JSONLD_PAT.finditer(html):
        raw = m.group(1).strip()
        if not raw: continue
        try: blocks.append(json.loads(raw))
        except json.JSONDecodeError:
            try: blocks.append(json.loads(_fix_json_nl(raw)))
            except json.JSONDecodeError: pass
    return blocks

def find_listing_block(blocks):
    """Vrati blok @type RealEstateListing alebo None."""
    for b in blocks:
        t = b.get("@type", "")
        if isinstance(t, str) and "RealEstateListing" in t: return b
        if isinstance(t, list) and any("RealEstateListing" in x for x in t): return b
    return None

def find_breadcrumb_block(blocks):
    """Vrati BreadcrumbList blok alebo None."""
    for b in blocks:
        t = b.get("@type", "")
        if isinstance(t, str) and "BreadcrumbList" in t: return b
    return None

def extract_price_from_html(html):
    """Cena z data-price atributu (priorita) alebo class=price. 0.0 ak nenajde."""
    m = _DATA_PRICE_RE.search(html)
    if m: return float(m.group(1))
    m2 = _PRICE_CLASS_RE.search(html)
    if m2:
        raw = m2.group(1).replace(" ", "").replace(chr(0xA0), "")
        if raw.isdigit(): return float(raw)
    return 0.0

def extract_area_from_text(text):
    """Vymera z textu: m2/m² alebo are. 0.0 ak nenajde."""
    m = _AREA_M2_RE.search(text)
    if m:
        try: return float(m.group(1).replace(" ", ""))
        except ValueError: pass
    m2 = _AREA_ARE_RE.search(text)
    if m2:
        try: return float(m2.group(1)) * 100.0
        except ValueError: pass
    return 0.0

_SKIP_SEG = {
    "pozemky", "predam", "prenajom", "domy", "byty",
    "apartman", "rodinne", "stavebne", "ibv", "chaty",
}

def extract_location_from_breadcrumb(bc):
    """
    Z BreadcrumbList extrahuje lokalitu (obec/mesto).
    Ignoruje 'Reality' a kategorie (pozemky, predam, rodinne...).
    Vracia najkonkretnejsiu lokalitu alebo "".
    """
    if bc is None: return ""
    items = bc.get("itemListElement", [])
    candidates = []
    for it in sorted(items, key=lambda x: x.get("position", 0)):
        url  = it.get("item", {}).get("@id", "")
        name = it.get("item", {}).get("name", "").strip()
        if not name or name == "Reality": continue
        parts = [p for p in url.rstrip("/").split("/") if p]
        last  = parts[-1].replace("-", "").lower() if len(parts) > 1 else ""
        if not any(s in last for s in _SKIP_SEG):
            candidates.append(name)
    return candidates[-1] if candidates else ""

def listing_to_parcel(blocks, html):
    """Zo JSON-LD blokov + HTML vytazuje Parcel. None ak chyba listing blok."""
    listing = find_listing_block(blocks)
    if listing is None: return None
    title = listing.get("name", "").strip()
    url   = listing.get("url", "").strip()
    desc  = listing.get("description", "").strip()
    if url and not url.startswith("http"): url = BASE_DOMAIN + url
    bc = find_breadcrumb_block(blocks)
    return BaseScraper._make_parcel(
        title         = title,
        url           = url,
        price_eur     = extract_price_from_html(html),
        area_sqm      = extract_area_from_text(title + " " + desc),
        location_text = extract_location_from_breadcrumb(bc),
        source_portal = SOURCE_NAME,
        description   = desc[:500],
    )
