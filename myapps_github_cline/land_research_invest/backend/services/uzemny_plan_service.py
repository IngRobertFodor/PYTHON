"""
Uzemno-planovaci asistent
=========================
Generuje priame odkazy na uzemny plan obce a checklist na rucne overenie.
Podporuje gisplan.sk (T-MAPY T-WIST) ako primarny zdroj + fallbacky.

Poznatky z reverse-engineeringu (2026-10-01):
  - Vzor URL: https://<obec-slug>.gisplan.sk/mapa/uzemny-plan/
  - Overene obce: malacky, modra, bernolakovo (maju UP mapu)
  - Bez gisplan: senec, pezinok, ivanka-pri-dunaji, chorvatsky-grob
  - Detekcia: "HTTP Server Test Page powered by: Rocky" = nema gisplan
  - SSL: verify=False nutne (rovnako ako SPF scraper)

0 HTTP pri generovani odkazov. Volitelny HEAD check pri is_gisplan_available().
Cache v pamati aby sme nespamovali gisplan.sk.
"""

import re
import unicodedata
import threading
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SERVICE_NAME = "uzemny_plan_service"

_gisplan_cache: dict = {}
_cache_lock = threading.Lock()

_NO_GISPLAN_MARKERS = [
    "http server test page",
    "powered by: rocky",
    "powered by rocky",
    "apache http server",
    "nginx welcome",
    "default web page",
]

_HAS_GISPLAN_MARKERS = [
    "gisplan",
    "t-wist",
    "tmapy",
    "spinbox",
    "uzemny-plan",
    "katastralna-mapa",
]



def normalize_obec(location_text: str) -> str:
    """
    Normalizuje textovu adresu na slug pre gisplan.sk subdomenу.
      "Senec, Bratislavsky kraj"      -> "senec"
      "Bernolákovo"                   -> "bernolakovo"
      "Ivanka pri Dunaji, okr. Senec" -> "ivanka-pri-dunaji"
      "Kamenný Most"                  -> "kamenny-most"
      "Velky-Meder"                   -> "velky-meder"   (pomlcka zachovana)
      "Nova-Vieska"                   -> "nova-vieska"
    """
    if not location_text:
        return ""
    text = location_text.split(",")[0].strip()
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(c for c in nfkd if not unicodedata.combining(c))
    # Pomlcka a medzera su oba oddelovace slov -> unifikuj na medzeru
    unified = re.sub(r"[-_]", " ", ascii_text.lower())
    # Ponechaj len pismena, cislice a medzery
    cleaned = re.sub(r"[^a-z0-9 ]", "", unified)
    # Medzery na pomlcky, viac pomlciek na jednu
    slug = re.sub(r"\s+", "-", cleaned.strip())
    slug = re.sub(r"-{2,}", "-", slug)
    return slug


def build_up_links(location_text: str, check_gisplan: bool = False) -> dict:
    """
    Generuje priame odkazy na uzemny plan obce a checklist.

    Args:
        location_text: textova adresa z inzeratu
        check_gisplan: ak True, vykona HTTP check ci ma gisplan.sk (5s timeout)

    Returns:
        {obec, obec_slug, has_gisplan, gisplan_up_url, gisplan_base_url,
         fallback_links, checklist}
    """
    obec_raw = location_text.split(",")[0].strip() if location_text else ""
    slug = normalize_obec(location_text)
    gisplan_base = f"https://{slug}.gisplan.sk" if slug else ""
    gisplan_up   = f"{gisplan_base}/mapa/uzemny-plan/" if slug else ""

    has_gisplan = None
    if check_gisplan and slug:
        has_gisplan = is_gisplan_available(slug)
    elif slug:
        with _cache_lock:
            has_gisplan = _gisplan_cache.get(slug)

    return {
        "obec":             obec_raw,
        "obec_slug":        slug,
        "has_gisplan":      has_gisplan,
        "gisplan_up_url":   gisplan_up,
        "gisplan_base_url": gisplan_base,
        "fallback_links":   _build_fallback_links(obec_raw, slug),
        "checklist":        get_checklist(),
    }


def _build_fallback_links(obec: str, slug: str) -> list:
    """
    Fallback odkazy pre overenie UP bez gisplan.sk.
    Pokryva: stranku obce, ZBGIS, geoportal, cielenych Google dotazy.
    """
    q_up       = (obec + " územný plán").replace(" ", "+")
    q_pdf      = ('"' + obec + '" UPN mapa OR pdf').replace(" ", "+")
    q_zmena    = (obec + " zmena územný plán").replace(" ", "+")
    q_samospr  = (obec + " územné plánovanie samospráva").replace(" ", "+")

    links = []

    # 1. Priamy odkaz na stranku obce (format <slug>.sk je bezny pre SK obce)
    if slug:
        # Pouzij prvu cast slugu (bez okresu/kraja) pre domenove meno
        obec_domain = slug.split("-")[0] if "-" in slug else slug
        links.append({
            "label": f"🏛️ Stránka obce {obec}",
            "url":   f"https://www.{slug}.sk/",
            "hint":  "Hladaj sekciu 'Územné plánovanie' alebo 'Samospráva > ÚP'",
        })

    # 2. gisplan.sk katalog obci
    if slug:
        links.append({
            "label": "🗺️ GISPLAN katalóg",
            "url":   f"https://{slug}.gisplan.sk/",
            "hint":  "Skontroluj ci ma obec mapovy portal (nie vsetky obce ho maju)",
        })

    # 3. ZBGIS mapovy klient
    links.append({
        "label": "📐 ZBGIS mapový klient",
        "url":   "https://zbgis.skgeodesy.sk/mkzbgis/sk/zakladna-mapa",
        "hint":  "Vyhladaj parcelu v katastrálnej mape SR",
    })

    # 4. Geoportal SR
    links.append({
        "label": "🌐 Geoportál SR",
        "url":   "https://www.geoportal.gov.sk/sk/zbgis/",
        "hint":  "Mapy a GIS sluzby SR",
    })

    # 5. Google: UP mapa/pdf (cielenejsi ako len 'uzemny plan')
    links.append({
        "label": f"🔍 ÚP mapa/PDF: '{obec}'",
        "url":   f"https://www.google.sk/search?q={q_pdf}",
        "hint":  "Najdi PDF alebo mapovy subor uzemneho planu obce",
    })

    # 6. Google: uzemne planovanie na stranke obce
    links.append({
        "label": f"🔍 ÚP samospráva: '{obec}'",
        "url":   f"https://www.google.sk/search?q={q_samospr}",
        "hint":  "Najdi sekciu uzemneho planovania na stranke samospravy",
    })

    # 7. Google: zmena UP (najdolezitejsi pre investicne rozhodnutie)
    links.append({
        "label": f"🔍 Zmena ÚP: '{obec}'",
        "url":   f"https://www.google.sk/search?q={q_zmena}",
        "hint":  "Zisti ci bola schvalena zmena uzemneho planu",
    })

    return links


def get_checklist() -> list:
    """Vrati checklist kontrolnych otazok pre rucne overenie UP."""
    return [
        {
            "id":       "zona_byvania",
            "otazka":   "Je parcela v ÚP v zóne bývania / IBV / zmiešaného územia?",
            "hint":     "Hladaj farebnu legendu — typicky zlta/oranzova = byvanie",
            "kriticka": True,
        },
        {
            "id":       "zmena_up",
            "otazka":   "Existuje schválená Zmena a doplnok ÚP meniaca funkčné využitie?",
            "hint":     "Pozri datumove vydania zmien UP — nova zmena = vyssia hodnota",
            "kriticka": True,
        },
        {
            "id":       "zavazna_cast",
            "otazka":   "Je to záväzná časť ÚP alebo len územná rezerva (výhľad)?",
            "hint":     "Rezerva = planovany rozvoj v buducnosti (5-20 rokov), nie hned",
            "kriticka": True,
        },
        {
            "id":       "izp",
            "otazka":   "Aký je Index zastavanosti plôch (IZP) pre danú zónu?",
            "hint":     "Min IZP 0.20-0.25 = moznost stavby RD, nizsie = problem",
            "kriticka": False,
        },
        {
            "id":       "regulativy",
            "otazka":   "Sú regulatívy obmedzujúce stavbu RD (výška, odstupy, min. plocha)?",
            "hint":     "Strictne regulativy mozu zdraziit alebo skomplikovat vystavbu",
            "kriticka": False,
        },
        {
            "id":       "vedenia",
            "otazka":   "Prechádzajú parcelou alebo okolím ochranné pásma / vedenia?",
            "hint":     "VVN, VTL, vodovod — ZBGIS Inzinierske siete",
            "kriticka": False,
        },
        {
            "id":       "pristup",
            "otazka":   "Je prístup k parcele zakreslený v ÚP ako verejná komunikácia?",
            "hint":     "Pristupova cesta bez pravneho titulu blokuje stavebne povolenie",
            "kriticka": True,
        },
    ]


def is_gisplan_available(slug: str) -> bool:
    """
    Overi (GET) ci <slug>.gisplan.sk ma funkcnu UP mapu.
    Cachuje vysledok v pamati. verify=False (SSL problemy).
    """
    with _cache_lock:
        if slug in _gisplan_cache:
            return _gisplan_cache[slug]

    result = _check_gisplan_http(slug)

    with _cache_lock:
        _gisplan_cache[slug] = result

    return result


def _check_gisplan_http(slug: str) -> bool:
    """HTTP check na gisplan subdomenu. Bez SSL overenia."""
    try:
        r = requests.get(
            f"https://{slug}.gisplan.sk/",
            verify=False, timeout=5,
            headers={"User-Agent": "LandResearchInvest/1.0"},
            allow_redirects=True,
        )
        if r.status_code != 200:
            return False
        body_lower = r.text.lower()
        if any(m in body_lower for m in _NO_GISPLAN_MARKERS):
            return False
        if any(m in body_lower for m in _HAS_GISPLAN_MARKERS):
            return True
        return False
    except Exception:
        return False


def warm_cache(slugs: list) -> dict:
    """Prekontroluje zoznam slugov (napr. po scrape_all). Vracia {slug: bool}."""
    return {s: is_gisplan_available(s) for s in slugs if s}


