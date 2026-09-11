"""Reality.sk scraper
=====================
Parsuje reality.sk - druhy najvacsi realitny portal SR.

Technicke detaily:
  - Karta inzeratu: div.offer (24 na stranku)
  - Cena: p.offer-price (text: '1,678,170 EUR', ciarky = tisice)
  - Vymera: v texte karty 'N,NNN m2' (ciarky ako tisice)
  - Lokalita: z odkazu /bratislava-lamac/ alebo textu
  - URL: /pozemky/<slug>/<id>/
  - Strankovanie: ?page=N (auto-stop na prazdnej strane)
  - YELLOW zona: pouziva neutralny user-agent (use_neutral_useragent: true)
"""

import re
from services.scrapers.base_scraper import BaseScraper

SOURCE_NAME  = "reality_sk"
BASE_DOMAIN  = "https://www.reality.sk"
# Hlavne URL pre vyhladavanie pozemkov na predaj
SEARCH_URLS  = [
    "https://www.reality.sk/pozemky/bratislava/predaj/",
    "https://www.reality.sk/pozemky/senec/predaj/",
    "https://www.reality.sk/pozemky/pezinok/predaj/",
    "https://www.reality.sk/pozemky/malacky/predaj/",
]

_COMMA_NUM_RE = re.compile(r"([\d,]+)\s*m[\u00b2\u00b2²\s]*2?", re.IGNORECASE)
_AREA_RE      = re.compile(r"([\d,]+)\s*m[\u00b2²2]", re.IGNORECASE)
_LOC_HREF_RE  = re.compile(r"^/([\w-]+)/?$")



class RealitySkScraper(BaseScraper):
    """Scraper reality.sk - CSS selektory na div.offer kartach."""

    SOURCE_NAME = "reality_sk"
    BASE_URL    = SEARCH_URLS[0]

    def scrape(self, criteria=None):
        """Strankovanie: pre kazdu SEARCH_URL vsetky strany (auto-stop)."""
        seen, results = set(), []
        for base_url in SEARCH_URLS:
            for p in self.scrape_all_pages(base_url, page_param="page", max_safety=50):
                if p.url and p.url not in seen:
                    seen.add(p.url)
                    results.append(p)
        return results

    def parse_listings(self, html):
        """Parsuje listing stranku reality.sk. Vracia zoznam Parcel."""
        return parse_listing_page(html)


# ----------------------------------------------------------------
# Samostatne funkcie (testovatelne bez instancie)
# ----------------------------------------------------------------

def parse_listing_page(html):
    """Zo HTML listing stranky extrahuje zoznam Parcel (div.offer karty)."""
    from bs4 import BeautifulSoup
    soup    = BeautifulSoup(html, "html.parser")
    parcels = []
    seen    = set()
    for div in soup.find_all("div", class_="offer"):
        try:
            p = _offer_to_parcel(div, seen)
            if p is not None:
                parcels.append(p)
        except Exception:
            continue
    return parcels


def _offer_to_parcel(div, seen_urls):
    """Z jednej div.offer karty vytvori Parcel. None ak chyba URL alebo duplikat."""
    # URL
    a_url = div.find("a", href=re.compile(r"/pozemky/", re.I))
    if not a_url:
        return None
    href = a_url["href"]
    if not href.startswith("http"):
        href = BASE_DOMAIN + href
    if href in seen_urls:
        return None
    seen_urls.add(href)

    # Nazov
    title = a_url.get_text(strip=True)[:120] or "Pozemok"

    # Cena
    price = extract_price(div)

    # Vymera
    body_text = div.get_text(separator=" ", strip=True)
    area      = extract_area(body_text)

    # Lokalita
    location = extract_location(div)

    return BaseScraper._make_parcel(
        title         = title,
        url           = href,
        price_eur     = price,
        area_sqm      = area,
        location_text = location,
        source_portal = SOURCE_NAME,
    )


def extract_price(div):
    """Extrahuje cenu z p.offer-price. Format: '1,678,170 EUR'. 0.0 ak nenajde alebo len EUR/m2."""
    price_tag = div.find(class_="offer-price")
    if not price_tag:
        return 0.0
    # Zisti prvy textovy uzol (nie small = EUR/m2)
    text = ""
    for node in price_tag.children:
        import bs4
        if isinstance(node, bs4.NavigableString):
            text = str(node).strip()
            if text:
                break
    if not text:
        text = price_tag.get_text(strip=True)
    # Ak prvy uzol je EUR/m2 (nie absolutna cena) -> vrat 0.0
    if "/m" in text.lower() or "\u20ac/m" in text:
        return 0.0
    # Odstrán ciarky a jednotku
    text = text.split("\u20ac")[0].split("EUR")[0].strip()
    text = text.replace(",", "").replace("\xa0", "").replace(" ", "")
    try:
        val = float(text)
        # Sanity check: realitna cena nemoze byt < 100 EUR (to je EUR/m2 chyba)
        return val if val >= 100 else 0.0
    except (ValueError, TypeError):
        return 0.0


def extract_area(text):
    """Extrahuje vymeru z textu karty. Format: '4,303 m2'. 0.0 ak nenajde."""
    m = _AREA_RE.search(text)
    if m:
        raw = m.group(1).replace(",", "")
        try:
            return float(raw)
        except ValueError:
            pass
    return 0.0


def extract_location(div):
    """Extrahuje lokalitu z odkazu v karte (/bratislava-lamac/ -> Bratislava Lamac)."""
    for a in div.find_all("a", href=_LOC_HREF_RE):
        slug = a["href"].strip("/")
        if slug and slug not in ("pozemky", "predaj", "prenajom"):
            # Slug -> citatelna forma (bratislava-lamac -> Bratislava Lamac)
            parts = slug.replace("-", " ").title()
            return parts
    # Fallback: text s lokalitou
    loc_el = div.find(class_=re.compile(r"loc|localit|mesto|obec", re.I))
    if loc_el:
        return loc_el.get_text(strip=True)[:60]
    return ""
