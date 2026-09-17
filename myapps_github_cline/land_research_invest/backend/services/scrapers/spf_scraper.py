"""SPF scraper - Slovensky pozemkovy fond (dvojurovnovy: HTML index + PDF parcely).
====================================================================================
Urovne:
  1. HTML index (parse_index):
       Parsuje HTML stranku SPF s PDF odkazmi (uzemneplany plugin).
       URL vzor: https://pozfond.sk/wp-content/uploads/uzemneplany/<Okres>_<Obec>_<KU>.pdf
       Poznamka: stara domena www.pozemkovyfond.sk ma SSL chybu a vracia 503.
       Nova domena: https://pozfond.sk (platny SSL cert *.pozfond.sk).
       Ked nie su aktivne pozemky (mimo vyhlasovacieho obdobia), pouzije sa
       posledna archivna stranka (ARCHIVE_URL).
  2. PDF pozemkov (parse_pdf_pozemky):
       pypdf cita tabu v pamati (nie na disk)
       Kazda strana: header + riadky parciel
       Format riadku (vsetko ako newline-oddelene tokeny):
         Okres(2 slova) Obec(2 slova) KU(2 slova) Parcela Vymera Druh LV UmPoz ...

Investicny vyznam:
  SPF ponuka neprenajanate pozemky na prenajom (polnohospodarska poda, extravilán).
  Cena nájmu nie je v PDF -> price_eur = 0 (skórovanie spracuje ako neutral).
  Kľúčové polia: parcela, výmera, druh pozemku, LV, umiestnenie (1=extravilán, 0=intravilán).
  Druh pozemku kódy (kataster): 2=orná pôda, 5=záhrada, 7=trvalý trávny porast,
    10=lesný pozemok, 13=ostatná plocha, 11=zastavaná plocha...

Pouzitie:
  scraper = SpfScraper()
  # a) z HTML indexu ziskaj URL -> spusti scrape_pdf pre kazdu URL
  # b) priamo: scraper.scrape_pdf(pdf_path_alebo_bytes)
"""

import re
import io
import unicodedata
import pypdf
from bs4 import BeautifulSoup

from services.scrapers.base_scraper import BaseScraper
from config_loader import get_sources

SOURCE_NAME = "spf"
BASE_URL    = "https://pozfond.sk"
# Aktivna listing stranka (ked su pozemky vyhlasene)
LISTING_URL = "https://pozfond.sk/zoznam-pozemkov-na-prenajom/"
# Archivna stranka - pouziva sa ked nie su aktivne pozemky
PDF_BASE    = "https://pozfond.sk/wp-content/uploads/uzemneplany/"

# ----------------------------------------------------------------
# Filter okresov - relevantné pre investíciu (do ~70km od BA)
# Normalizovany format: male pismena, medzery -> pomlcky
# ----------------------------------------------------------------
OKRESY_BA_70KM = {
    # Blízke (~50km od BA)
    "bratislava",
    "bratislava-i", "bratislava-ii", "bratislava-iii",
    "bratislava-iv", "bratislava-v",
    "malacky",
    "pezinok",
    "senec",
    "trnava",
    "dunajska-streda",
    "galanta",
    # Stredné (~70km od BA, súlad s criteria.yaml max_distance_km: 70)
    "hlohovec",
    "senica",
    "skalica",
    "sala",
    "nove-zamky",
    "piestany",
}

# Kody druhu pozemku podla katastra nehnutelnosti
DRUH_KODY = {
    "2":  "Orna poda",
    "5":  "Zahrada",
    "6":  "Ovocny sad",
    "7":  "Trvaly travny porast",
    "10": "Lesny pozemok",
    "11": "Zastavana plocha a nadvorie",
    "13": "Ostatna plocha",
    "14": "Vodna plocha",
}
# Umiestnenie: 1=extravilán (mimo zastavaného územia), 0=intravilán
UMIESTNENIE = {"1": "extravilán", "0": "intravilán"}

# Regex pre PDF odkaz v HTML
_PDF_LINK_RE = re.compile(
    r'href=["\']([^"\']*uzemneplany/[^"\']+\.pdf)["\']',
    re.IGNORECASE,
)
# Hlavicka stranky PDF (opakovana na kazdej strane) - token sekvencia
_PDF_HEADER_TOKENS = {
    "Údaje podľa katastra nehnuteľností",
    "Výmera v správe a nakladaní SPF (m",
    "Výmera neprenajatá v m",
    "Okres", "Obec", "Katastrálne územie", "Parcela", "Výmera",
    "Druh poz.", "LV", "Um. poz.", "SR-SPF", "NV-SPF", "Spolu",
    chr(178),   # superscript 2 (m²)
    chr(178) + ")",   # ²)
}


class SpfScraper(BaseScraper):
    """Scraper Slovenskeho pozemkoveho fondu (HTML index + PDF parcely).

    Logika listing URL:
      1. Nacita LISTING_URL (https://pozfond.sk/zoznam-pozemkov-na-prenajom/)
      2. Ak obsahuje PDF uzemneplany linky -> pouzije ich (aktivne vyhlasovanie)
      3. Ak nie -> hlada prvy archivny link (href obsahujuci 'archiv') a nacita ho
      Tym pokryva obe stavy: aktivne aj neaktivne vyhlasovanie.
    """

    SOURCE_NAME = "spf"
    BASE_URL    = BASE_URL

    def get_listing_urls(self, criteria=None):
        """Vracia [LISTING_URL] - scrape() vola parse_listings() ktory resi fallback."""
        return [LISTING_URL]

    def fetch_pdf_bytes(self, url):
        """
        Stiahne PDF ako binarne bytes (nie text).
        BaseScraper.fetch_html() vracia resp.text (string) - pre PDF treba resp.content (bytes).
        """
        import requests as _req
        self._wait_rate_limit()
        _RETRYABLE = (
            _req.exceptions.ConnectionError,
            _req.exceptions.Timeout,
            _req.exceptions.ReadTimeout,
            _req.exceptions.ConnectTimeout,
            TimeoutError, OSError,
        )
        from services.scrapers.base_scraper import RETRY_DELAY, RETRY_DELAY2, MAX_RETRIES
        delays = [RETRY_DELAY, RETRY_DELAY2]
        for attempt in range(MAX_RETRIES + 1):
            self._wait_rate_limit()
            try:
                resp = _req.get(
                    url,
                    headers={"User-Agent": self.user_agent},
                    timeout=self.timeout,
                )
                resp.raise_for_status()
                return resp.content  # bytes, nie text!
            except _RETRYABLE as exc:
                if attempt < MAX_RETRIES:
                    delay = delays[attempt]
                    print(f"[{self.SOURCE_NAME}] sietovy vypadok pri {url}: {exc} — retry za {delay}s")
                    import time as _time
                    _time.sleep(delay)
                else:
                    raise

    def parse_listings(self, html):
        """
        Parsuje HTML stranku SPF.
        Ak neobsahuje PDF linky, automaticky nasleduje prvy archivny link.
        Vracia zoznam Parcel zo vsetkych PDF na stranke.
        """
        # Skus priamu stranku
        index = parse_index(html)

        # Fallback: hladaj archivny link (SPF mimo vyhlasovacie obdobie)
        # Filter: 'archiv' + pozemkovy kontext (pozemk/prenaj/neprenaj)
        #         NESMIE byt faktury-archiv ani objednavky-archiv
        if not index:
            soup = BeautifulSoup(html, "html.parser")
            archiv_link = None
            for a in soup.find_all("a", href=True):
                href = a["href"]
                low  = href.lower()
                is_pozemkovy = (
                    "archiv" in low
                    and ("pozemk" in low or "prenaj" in low or "neprenaj" in low)
                    and "faktur" not in low
                    and "objednavk" not in low
                )
                if is_pozemkovy and "pozfond.sk" in href:
                    archiv_link = href
                    break
                elif is_pozemkovy and href.startswith("/"):
                    archiv_link = BASE_URL + href
                    break
            if archiv_link:
                print(f"[{self.SOURCE_NAME}] Aktivne pozemky nenajdene, pouzivam archiv: {archiv_link}")
                try:
                    archiv_html = self.fetch_html(archiv_link)
                    index = parse_index(archiv_html)
                except Exception as exc:
                    print(f"[{self.SOURCE_NAME}] Archiv chyba: {exc}")

        if not index:
            print(f"[{self.SOURCE_NAME}] Ziadne PDF linky nenajdene na SPF stranke")
            return []

        # Filter okresov: len relevantne pre investiciu (do ~70km od BA)
        # Konfigurovatelne cez criteria.yaml: spf.filter_okresy_70km: true/false
        cfg = get_sources().get(self.SOURCE_NAME, {})
        if cfg.get("filter_okresy_70km", True):
            before = len(index)
            index = [e for e in index if _normalize_okres(e.get("okres", "")) in OKRESY_BA_70KM]
            print(f"[{self.SOURCE_NAME}] Filter 70km od BA: {len(index)}/{before} PDF (okresy: {sorted({_normalize_okres(e['okres']) for e in index})})")

        if not index:
            print(f"[{self.SOURCE_NAME}] Ziadne PDF v relevantnych okresoch (filter_okresy_70km)")
            return []

        # Limit max_pdf: ochrana pred tisíckami PDF (napr. 557 po filtri = 55min)
        # Konfigurovatelne cez criteria.yaml: spf.max_pdf: 30 (false = bez limitu)
        max_pdf = cfg.get("max_pdf", 30)
        if max_pdf and len(index) > max_pdf:
            print(f"[{self.SOURCE_NAME}] max_pdf limit: {max_pdf}/{len(index)} PDF (zmen v criteria.yaml pre viac)")
            index = index[:max_pdf]

        parcels = []
        for entry in index:
            try:
                pdf_bytes = self.fetch_pdf_bytes(entry["pdf_url"])
                new = parse_pdf_pozemky(pdf_bytes, entry["okres"], entry["obec"], entry["pdf_url"])
                parcels.extend(new)
            except Exception as exc:
                print(f"[{self.SOURCE_NAME}] PDF chyba {entry.get('pdf_url','')}: {exc}")
        return parcels

    def scrape_pdf(self, pdf_source, okres="", obec=""):
        """
        Parsuje jedno PDF so zoznamom parciel.
        pdf_source: cesta (str/Path) alebo bytes.
        Vracia zoznam Parcel.
        """
        try:
            return parse_pdf_pozemky(pdf_source, okres, obec)
        except Exception as exc:
            print(f"[{self.SOURCE_NAME}] scrape_pdf error: {exc}")
            return []


# ----------------------------------------------------------------
# Samostatne funkcie (testovatelne bez instancie)
# ----------------------------------------------------------------


def _normalize_okres(okres):
    """
    Normalizuje nazov okresu pre porovnanie s OKRESY_BA_70KM.
    Prevod: 'Dunajska Streda' -> 'dunajska-streda'
            'Bratislava I'    -> 'bratislava-i'
            'Rimavska-Sobota' -> 'rimavska-sobota'
            'Malacky Mesto'   -> 'malacky'  (odstrani trailing 'Mesto'/'Obec')
    """
    import unicodedata
    # Odstran diakritiku
    nfkd = unicodedata.normalize("NFKD", okres.strip())
    ascii_str = "".join(c for c in nfkd if not unicodedata.combining(c))
    # Male pismena, medzery -> pomlcky
    result = ascii_str.lower().replace(" ", "-").strip("-")
    # Odstran trailing "-mesto" alebo "-obec" (artifact z HTML parsingu)
    for suffix in ("-mesto", "-obec", "-/-obec"):
        if result.endswith(suffix):
            result = result[: -len(suffix)]
    return result



def parse_index(html):
    """
    Parsuje HTML stranku SPF a vracia zoznam PDF zaznamov.

    Podporuje dve HTML struktury:
      1. Stara (wpDataTable): <tr> s 12+ <td>, td[7]=Okres, td[8]=Obec, td[11]=PDF link
      2. Nova (uzemneplany plugin): href linky obsahujuce 'uzemneplany/*.pdf'
         s prilozenym textom 'Okres: X Mesto / Obec: Y'

    Vracia zoznam dict: [{okres, obec, pdf_url}, ...].
    """
    soup = BeautifulSoup(html, "html.parser")
    results = []
    seen_urls = set()

    # --- METODA 1: wpDataTable (<tr> s 12+ <td>) ---
    for row in soup.find_all("tr"):
        tds = row.find_all("td")
        if len(tds) < 12:
            continue
        okres = tds[7].get_text(strip=True)
        obec  = tds[8].get_text(strip=True)
        link  = tds[11].find("a")
        if not link or not okres:
            continue
        pdf_url = link.get("href", "").strip()
        if pdf_url and "uzemneplany" in pdf_url and pdf_url not in seen_urls:
            results.append({"okres": okres, "obec": obec, "pdf_url": pdf_url})
            seen_urls.add(pdf_url)

    if results:
        return results

    # --- METODA 2: uzemneplany plugin (href linky v HTML) ---
    # Vzor: href="https://pozfond.sk/wp-content/uploads/uzemneplany/Okres_Obec_KU.pdf"
    # Pridruzeny text moze byt: "Okres: Rimavska-Sobota Mesto / Obec: Martinova"
    _OKRES_RE = re.compile(r"Okres[:\s]+([A-Za-z\u00c0-\u024f\-]+(?:\s+[A-Za-z\u00c0-\u024f\-]+)?)", re.IGNORECASE)
    _OBEC_RE  = re.compile(r"(?:Mesto\s*/\s*Obec|Obec)[:\s]+([A-Za-z\u00c0-\u024f\-]+(?:\s+[A-Za-z\u00c0-\u024f\-]+)?)", re.IGNORECASE)

    for a in soup.find_all("a", href=True):
        pdf_url = a.get("href", "").strip()
        if "uzemneplany" not in pdf_url or not pdf_url.endswith(".pdf"):
            continue
        if pdf_url in seen_urls:
            continue

        # Hladaj Okres/Obec v okolnom texte (rodic element + siblings)
        context = ""
        parent = a.parent
        if parent:
            context = parent.get_text(" ", strip=True)

        okres = ""
        obec  = ""
        m_ok = _OKRES_RE.search(context)
        m_ob = _OBEC_RE.search(context)
        if m_ok:
            okres = m_ok.group(1).strip()
        if m_ob:
            obec = m_ob.group(1).strip()

        # Fallback: extrahuj z URL nazvu suboru
        if not okres or not obec:
            url_okres, url_obec = extract_okres_obec_from_pdf_url(pdf_url)
            if not okres:
                okres = url_okres
            if not obec:
                obec = url_obec

        results.append({"okres": okres, "obec": obec, "pdf_url": pdf_url})
        seen_urls.add(pdf_url)

    return results


def extract_pdf_text_spf(pdf_source):
    """
    Nacita SPF PDF a vracia text kazdej stranky ako zoznam stringov.
    pdf_source: cesta (str/Path) alebo bytes/bytearray.
    """
    if isinstance(pdf_source, (bytes, bytearray)):
        reader = pypdf.PdfReader(io.BytesIO(pdf_source))
    else:
        reader = pypdf.PdfReader(str(pdf_source))
    return [page.extract_text() or "" for page in reader.pages]


def _tokenize_page(page_text):
    """
    Rozdeli text stranky na tokeny (oddelene novymi riadkami/medzerami).
    Filtruje prazdne tokeny a hlavickove tokeny.
    """
    tokens = [t.strip() for t in re.split(r"\n+", page_text) if t.strip()]
    # Odfiltruj hlavickove tokeny (opakuju sa na kazdej strane)
    return [t for t in tokens if t not in _PDF_HEADER_TOKENS]


def parse_pdf_pozemky(pdf_source, okres="", obec="", pdf_url=""):
    """
    Parsuje PDF so zoznamom parciel SPF.
    Token schema na parcelu (9 tokenov):
      [0-1] Okres (2 tokeny, napr. 'Banska' + 'Stiavnica')
      [2-3] Obec / KU (2 tokeny, napr. 'Dekys' + 'Dekys')
      [4]   Parcela (napr. '35' alebo '156/1')
      [5]   Vymera v m2 (napr. '347')
      [6]   Druh pozemku kod (napr. '5')
      [7]   LV (napr. '0' alebo '715')
      [8]   Umiestnenie (napr. '1'=extravilan, '0'=intravilan)
      [9+]  Numericke hodnoty vymier SR-SPF/NV-SPF (preskocime)
    Vracia zoznam Parcel.
    """
    pages = extract_pdf_text_spf(pdf_source)
    all_tokens = []
    for page in pages:
        all_tokens.extend(_tokenize_page(page))

    parcels = []
    i = 0
    while i + 8 < len(all_tokens):
        try:
            t_parcela = all_tokens[i + 4]
            t_vymera  = all_tokens[i + 5]
            t_druh    = all_tokens[i + 6]
            t_lv      = all_tokens[i + 7]
            t_um      = all_tokens[i + 8]

            # Validacia: parcela je cislo (moze mat /), vymera a druh su cele cisla
            if not re.match(r"^\d+(/\d+)?$", t_parcela):
                i += 1
                continue
            if not re.match(r"^\d+$", t_vymera):
                i += 1
                continue
            if not re.match(r"^\d{1,2}$", t_druh):
                i += 1
                continue
            if t_um not in ("0", "1"):
                i += 1
                continue

            # Zrekonstruuj nazvy z tokenov
            r_okres = (all_tokens[i] + " " + all_tokens[i + 1]).strip()
            r_ku    = (all_tokens[i + 2] + " " + all_tokens[i + 3]).strip()

            loc_okres = okres if okres else r_okres
            loc_obec  = obec  if obec  else r_ku.split()[0] if r_ku else ""

            vymera_m2 = float(t_vymera)
            druh_text = DRUH_KODY.get(t_druh, f"Druh {t_druh}")
            um_text   = UMIESTNENIE.get(t_um, t_um)

            desc_parts = [
                "SPF PRENAJOM",
                f"Okres: {loc_okres}",
                f"Obec: {loc_obec}",
                f"K.u.: {r_ku}",
                f"Parc.c.: {t_parcela}",
                f"Druh: {druh_text}",
                f"LV: {t_lv}",
                f"Umiestnenie: {um_text}",
                f"Vymera: {t_vymera} m2",
            ]
            title = (
                f"SPF - {loc_obec} parc.{t_parcela} ({druh_text})"
            )

            parcels.append(BaseScraper._make_parcel(
                title         = title,
                url           = pdf_url or PDF_BASE,
                price_eur     = 0.0,
                area_sqm      = vymera_m2,
                location_text = loc_obec if loc_obec else r_ku,
                source_portal = SOURCE_NAME,
                parcel_number = t_parcela,
                description   = " | ".join(desc_parts)[:500],
            ))
            i += 9   # posun o 9 tokenov (1 parcela bez numerickych hodnot)
            # Preskoc numericke hodnoty vymier (SR-SPF/NV-SPF) - max 5
            skip = 0
            while i < len(all_tokens) and skip < 6:
                if re.match(r"^\d+\.\d+$", all_tokens[i]):
                    i += 1
                    skip += 1
                else:
                    break

        except (IndexError, ValueError):
            i += 1

    return parcels


def extract_okres_obec_from_pdf_url(pdf_url):
    """
    Extrahuje okres a obec z URL nazvu PDF suboru.
    Vzor: .../uzemneplany/Malacky_Pernek_Pernek.pdf -> ('Malacky', 'Pernek')
    """
    m = re.search(r"uzemneplany/([^/]+)\.pdf", pdf_url, re.IGNORECASE)
    if not m:
        return "", ""
    parts = m.group(1).split("_")
    okres = parts[0].replace("-", " ") if len(parts) > 0 else ""
    obec  = parts[1].replace("-", " ") if len(parts) > 1 else ""
    return okres, obec

