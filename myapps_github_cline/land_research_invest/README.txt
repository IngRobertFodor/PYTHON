Land Research Invest
====================

AI agent na vyhladavanie lacnych stavebnych pozemkov (orna poda / IBV) do 70 km od Bratislavy.

Zadate kriteria (cena, rozloha, vzdialenost) a agent prehlada realtne portaly aj dalsie
zdroje (drazby, SPF, obce), overi pozemky voci verejnym datasetom (kataster, zaplavy,
teren, bonita pody, infrastruktura, ortofoto, uzemny plan), oskuruje ich a pripravi
report + manualny checklist pre kataster.

Dokumentacia: README.txt (tento subor) + HOW_TO_RUN_THIS_APP.txt


==============================================================
1. PREHLAD A FUNKCIE
==============================================================

- AI agent (Google Gemini) - autonomne vyhladavanie a rozhodovanie
- Scraping realitnych portalov - Nehnutelnosti.sk, Reality.sk, TopReality (Playwright)
- Drazby a statne predaje - notarske drazby, SPF, obecne pozemky
- ZBGIS kataster - geometria parcely (sirka, tvar, vymera) cez WFS
- Zaplavove uzemia Q100 - kontrola cez SHMU WMS
- Teren - sklon, orientacia, zosuvne uzemia, radonove riziko (DMR / SGUDSH)
- Ortofoto - letecke snimky parcely (UGKK) + volitelna LLM vision analyza
- Uzemny plan - OCR + LLM extrakcia IBV zony z obecnych PDF dokumentov
- Bonita pody (BPEJ) - ochrannu skupina + odhad odvodov za vynatie z PPF
- Infrastruktura - pristupova cesta (sirka), elektrina, voda (Overpass API)
- Okolie - skola, obchod, MHD, dialnica (OpenStreetMap)
- Vzdialenost od Bratislavy - Haversine + odhad casu jazdy
- Cenovy kontext - EUR/m2 vs. priemer okolia, historia inzeratu
- Skorovaci system - vazene hodnotenie 0-100 podla kriterii
- Kataster checklist - manualny spruvodca kontrolou LV (sekcie B/C/D)
- Monitoring + notifikacie - periodicky sken, email / Telegram
- Interaktivna mapa - Leaflet.js s farebne odlisenymi kandidatmi


==============================================================
2. TECHNOLOGIE
==============================================================

  Komponent             | Technologia
  ----------------------|-------------------------------------
  Backend               | Python Flask
  AI agent              | LangChain + Google Gemini (primarny)
  AI fallback           | Anthropic Claude
  Frontend              | HTML5 + CSS3 + Vanilla JS
  Mapa                  | Leaflet.js + OpenStreetMap
  Realtne data          | Playwright scraping
  Kataster / geometria  | ZBGIS WFS (UGKK)
  Zaplavy Q100          | SHMU WMS
  Teren / vyskopis      | DMR 5.0 (UGKK) + SRTM (Copernicus)
  Zosuvne uzemia        | SGUDSH WMS
  Ortofoto              | Ortofotomozaika SR (UGKK WMS)
  Bonita pody BPEJ      | geodata.gov.sk WMS
  Infrastruktura        | Overpass API (OpenStreetMap)
  Geocoding             | Nominatim (OpenStreetMap)
  GIS spracovanie       | geopandas, shapely, pyproj, owslib
  OCR                   | pytesseract (UP dokumenty)
  Monitoring            | APScheduler
  Notifikacie           | python-telegram-bot / SMTP



==============================================================
3. ARCHITEKTURA
==============================================================

Vrstvy systemu
--------------

  +------------------------------------------------------------+
  |       AI ORCHESTRATOR  (llm_agent_service.py)              |
  |       Google Gemini (primarny) / Claude (fallback)         |
  |       LangChain agent + tools                              |
  +-------------------+----------------------------------------+
                      | vola tools (@tool)
       +--------------+-----------+-----------------+
       v              v           v                 v
  [Scrapery]    [GIS validatory]  [Scoring]   [Checklist]
  realestate    zbgis / flood /   scoring_    cadastral_
  auction       terrain / bpej /  service     service
  scraper       overpass / ortofoto / zoning_pdf


Tok dat (workflow)
------------------

  1. Pouzivatel zada kriteria (config/criteria.yaml alebo cez UI)
  2. Agent vola: search_real_estate_portals + search_auctions
     -> zoznam kandidatov zo vsetkych zdrojov
  3. Pre KAZDY pozemok agent vola:
       geocoding_service       -> GPS suradnice z adresy
       zbgis_service           -> geometria (sirka, tvar, vymera)
       distance_service        -> vzdialenost a cas jazdy od BA
       flood_service           -> Q100 zaplavove pasmo
       terrain_service         -> sklon, zosuvy, radon
       ortofoto_service        -> letecka snimka + LLM vision
       zoning_pdf_service      -> UP: IBV zona, index zastavnosti
       overpass_service        -> cesta, elektrina, voda, okolie
       bpej_service            -> bonita pody, ochrana, odvody
       price_analysis_service  -> EUR/m2 vs. priemer, historia
  4. scoring_service           -> vazene skore 0-100
  5. Ak skore >= 70:
       cadastral_service       -> manualny LV checklist (B/C/D)
  6. notifier_service          -> email / Telegram notifikacia
  7. monitor_service           -> ulozi do DB, dalsi sken o X hodin


Skorovaci algoritmus
--------------------

  Kriterium              | Vaha
  -----------------------|------
  Cena (EUR/m2)          | 20 %
  Vzdialenost od BA      | 15 %
  Infrastruktura         | 25 %
  Pravna cistota (proxy) | 20 %
  Zaplavove riziko       | 10 %
  Bonita pody (BPEJ)     | 10 %

  >= 85  ->  STRONG BUY  (vynikajuci kandidat)
  >= 70  ->  INVESTIGATE (dobry, overit detaily)
  >= 50  ->  CONSIDER    (prijatelny s kompromismi)
  <  50  ->  SKIP        (nespla kriteria)


Suradnicove systemy a LLM
--------------------------

  WGS-84 (EPSG:4326)  GPS, Nominatim, Leaflet.js
  S-JTSK (EPSG:5514)  Slovensky kataster (ZBGIS)
  Konverzia: pyproj   wgs84_to_jtsk(), jtsk_to_wgs84()

  Primarny  | Google Gemini (gemini-1.5-flash)  | langchain-google-genai >= 4.4.0
  Fallback  | Anthropic Claude (sonnet)         | langchain-anthropic >= 1.0.0
  Temperature 0.2  |  Max iterations 50
  Kluce: GOOGLE_API_KEY (povinny)  |  ANTHROPIC_API_KEY (volitelny, v .env)


Externe endpointy (overit pri implementacii)
--------------------------------------------

  ZBGIS WFS    | zbgis.skgeodesy.sk/wfs/default
  SHMU WMS     | geo.shmu.sk/wms
  BPEJ WMS     | geodata.gov.sk/geoserver/wms
  SGUDSH WMS   | gis.geology.sk/arcgis/services
  DMR 5.0 WCS  | zbgis.skgeodesy.sk/wcs
  Ortofoto WMS | zbgis.skgeodesy.sk/wms
  Overpass     | overpass-api.de/api/interpreter
  Nominatim    | nominatim.openstreetmap.org/search

  POZNAMKA: WMS/WFS endpointy SK statnych sluzieb sa mozu menit.
  Vzdy overit GetCapabilities pred implementaciou danej sluzby.


==============================================================
4. KRITERIA - AUTOMATIZACIA
==============================================================

Legenda:
  AUTO       = agent zvladne plne automaticky
  CIASTOCNE  = agent poskytne indiciu, finalne potvrdenie manualny
  MANUAL     = agent vygeneruje checklist, kontrola rucna (CAPTCHA/urad)


1. Uzemno-pravne rizika
  Vydana UPI - zona IBV               | cadastral_service   | MANUAL (obec)
  Index zastavnosti (IZP >= 0.25)     | scoring_service     | CIASTOCNE (z UPI)
  Sirka parcely min 15-16 m           | zbgis_service       | AUTO (WFS)
  Stavebna cara a odstupy OK          | zbgis_service       | AUTO (WFS)

2. List vlastnictva a Kataster
  Ziadna aktivna plomba (V, Z)        | cadastral_service   | MANUAL (CAPTCHA)
  Cast C: bez kritickych tiarch       | cadastral_service   | MANUAL (CAPTCHA)
  Max 2 spoluvlastnici, bez reg. E    | cadastral_service   | MANUAL (CAPTCHA)
  Bez zalozneho / predkupneho prava   | cadastral_service   | MANUAL (CAPTCHA)

  Poloautomat: Playwright otvori kataster, predvyplni parcelu;
  vy kliknete CAPTCHA; agent precita a vyhodnoti LV automaticky.

3. Pristupova cesta a infrastruktura
  Sirka cesty min 6 m (hasici)        | overpass_service    | AUTO (OSM width)
  Pravny pristup (vec. bremeno)       | cadastral_service   | CIASTOCNE
  Pristupova cesta nie je SPF         | cadastral_service   | MANUAL

4. Inzinierske siete
  Elektrina - blízkost vedenia        | overpass_service    | AUTO (OSM)
  Elektrina - kapacita trafostanice   |                     | CIASTOCNE (ZSDIS)
  Vzdialenost napojenia sieti         | overpass_service    | AUTO (metre)
  Kanalizacia / zumpa OK              | overpass_service    | AUTO (OSM sewer)

5. Geologia, teren a ochrane pasma
  Mimo zaplavoveho uzemia Q100        | flood_service       | AUTO (SHMU WMS)

==============================================================
5. RESEARCH STRATEGY - ZDROJE A LEGALNOST
==============================================================

Inzertne zdroje (overene robots.txt)
-------------------------------------

  ZELENA ZONA - bezpecne automatizovat:

  Nehnutelnosti.sk  | Detaily + Sitemap OK, /api/ blokovane
                    | -> pouzivat sitemap-listings pre URL zoznam
  TopReality.sk     | Takmer vsetko OK, limit 10 req/min
                    | -> dodriat Request-rate: 10/1m
  Notarske drazby   | Verejny register (OVS, notar.sk)
                    | -> zo zakona verejne, plne automatizovat
  SPF               | Verejne obchodne sutaze (pozemkovyfond.sk)
  Obce              | Uradne tabule (predaj obecnych pozemkov)
                    | -> verejne, ale roztrocene po weboch obci

  ZLTA ZONA - opatrne, s pravidlami:

  Reality.sk        | Detaily OK, ale zakazuje AI-botov
                    | -> neutralny User-Agent (nie AI-bot hlavicka)
  Bazos.sk          | /search.php a filtre blokovane
                    | -> len priame detail linky, nie vyhladavanie
  Bankove drazby    | Rozne ToS podla banky
                    | -> individualne overit pred zapojenim

  CERVENA ZONA - nevyuzivat:

  Facebook Marketplace  | ToS explicitne zakazuje scraping


Hlbkove GIS zdroje (vsetky legalne - otvorene data SR)
-------------------------------------------------------

  Teren a rizika:
  DMR 5.0 (UGKK)       | Vyskopis SR (LiDAR) -> sklon, orientacia
  SRTM/Copernicus DEM  | Globalny vyskopis 30m -> fallback
  Zosuvne uzemia       | Register svahových deformacii (SGUDSH WMS)
  Radonova mapa        | Radonove riziko (SGUDSH WMS)

  Vizualna analyza:
  Ortofotomozaika SR   | Letecke snimky (UGKK WMS) -> vyrez parcely
  LLM vision          | Analyza ortofota: pristup, zelen, stav parcely

  Uzemny plan (UP):
  Weby obci            | PDF dokumenty UP -> HTTP download (info zakon)
  OCR pipeline         | pytesseract -> text z PDF/skenu
  LLM extrakcia        | IBV zona? IZP? (~70-85% presnost, vzdy overit)
  Auto-draft ziadosti  | Agent vygeneruje email ziadost o UPI pre obec

  Cenovy kontext:
  Vlastna DB           | EUR/m2 z nazbieranych dat -> lokalny priemer
  Historia inzeratu    | Ako dlho visi, zmeny ceny -> motivacia predajcu

  Okolie:
  Overpass (OSM)       | Skola, obchod, MHD, dialnica, priemysel v okoli
  LLM web search       | Novinky, planovany rozvoj lokality (volitelne)


Zasady bezpecneho scrapingu (zabudovane do agenta)
--------------------------------------------------

  1. Kontrolovat robots.txt pred kazdym scrapom
  2. Dodriat rate-limity portalov (napr. TopReality 10/min)
  3. Pouzivat neutralny User-Agent (nie AI-bot hlavicka)
  4. Preferovat sitemap / oficialne data pred agresivnym crawlom
  5. Cachovat - netahat tie iste data opakovane v kratkom case
  6. Exponential backoff - pri chybe cakat a opakovat


==============================================================
6. STRUKTURA PROJEKTU
==============================================================

  land_research_invest/
  ├── backend/
  │   ├── app.py
  │   ├── requirements.txt
  │   ├── routes/
  │   │   ├── search_routes.py
  │   │   └── parcel_routes.py
  │   ├── services/
  │   │   ├── llm_agent_service.py
  │   │   ├── realestate_scraper_service.py
  │   │   ├── auction_scraper_service.py
  │   │   ├── zbgis_service.py
  │   │   ├── flood_service.py
  │   │   ├── terrain_service.py
  │   │   ├── ortofoto_service.py
  │   │   ├── zoning_pdf_service.py
  │   │   ├── bpej_service.py
  │   │   ├── overpass_service.py
  │   │   ├── geocoding_service.py
  │   │   ├── distance_service.py
  │   │   ├── price_analysis_service.py
  │   │   ├── scoring_service.py
  │   │   ├── cadastral_service.py
  │   │   ├── cadastral_semiauto_service.py
  │   │   ├── locality_context_service.py
  │   │   ├── monitor_service.py
  │   │   └── notifier_service.py
  │   └── models/
  │       ├── parcel.py
  │       └── criteria.py
  ├── frontend/
  │   ├── index.html
  │   ├── css/style.css
  │   └── js/
  │       ├── app.js
  │       └── map.js
  ├── config/
  │   └── criteria.yaml
  ├── tests/
  ├── .env.example
  ├── .gitignore
  ├── pytest.ini
  ├── pyrightconfig.json
  ├── start_app.bat
  ├── HOW_TO_RUN_THIS_APP.txt
  └── README.txt


Testovanie
----------

  python -m pytest tests/ -v --rootdir=.


Autor
-----

Robert Fodor | 2026

  Sklon, orientacia svahu             | terrain_service     | AUTO (DMR 5.0)
  Zosuvne uzemia                      | terrain_service     | AUTO (SGUDSH WMS)
  Radonove riziko                     | terrain_service     | AUTO (SGUDSH WMS)
  Ochrane pasmo VVN / VTL / les       | overpass_service    | AUTO (OSM)
  Bonita pody BPEJ (skupina 1-4)      | bpej_service        | AUTO + odhad odvodov
  Archeologicka zona                  | cadastral_service   | MANUAL (KPU)


Predvolene hodnoty kriterii (config/criteria.yaml)
--------------------------------------------------

  Max cena                   | 50 000 EUR
  Min cena                   | 10 000 EUR
  Max vzdialenost od BA      | 70 km
  Min vymera                 | 600 m2
  Max vymera                 | 1 500 m2
  Min sirka parcely          | 15 m
  Pozadovana zona            | IBV, rodinne domy
  Min sirka cesty            | 6 m
  Max BPEJ ochrana skupina   | 6
  Score prah pre checklist   | 70 / 100





