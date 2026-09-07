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

LEGENDA:
  AUTO   = agent vyriesí plne sam, bezi paralelne bez brzdenia
  SEMI   = agent pripravi 90%, ty spravís 1 krok (napr. CAPTCHA)
  MANUAL = agent vygeneruje checklist/ziadost, ty kontrolujes rucne


1. LOKACIA A CENA
  Max vzdialenost od BA (70 km)          | distance_service    | AUTO
  Cena (10k-50k EUR, max EUR/m2)         | z inzeratu          | AUTO
  Vymera (600-1500 m2), sirka min 15 m   | zbgis_service       | AUTO


2. UZEMNO-PRAVNE (UPI, IZP, UPZ, odstupy)
  IBV zona v uzemnom plane               | zoning_pdf_service  | SEMI (OCR+LLM ~80%)
  Index zastavanosti (IZP >= 0.20)       | zoning_pdf_service  | SEMI (z UP dokumentu)
  Absencia poziadavky na UPZ             | zoning_pdf_service  | SEMI (z UP dokumentu)
  Stavebna cara, odstup od cesty (5m)    | zbgis_service       | AUTO
  Odstupy od susedov (min 2m)            | zbgis_service       | AUTO


3. LIST VLASTNICTVA A KATASTER
  Ziadna aktivna plomba (V, Z)           | cadastral_service   | SEMI (Playwright+CAPTCHA)
  Cast C: bez zal. a predkupneho prava   | cadastral_service   | SEMI
  Bez prava dozitia / neznameho bremena  | cadastral_service   | SEMI
  Max 2 spoluvlastnici, bez reg. E       | cadastral_service   | SEMI
  Zlomok podielu max 1/8                 | cadastral_service   | SEMI
  Bez vlastnictva SPF                    | cadastral_service   | SEMI
  Ziadni nezisti vlastnici               | cadastral_service   | SEMI
  Pristupova cesta: vec. bremeno / obec  | cadastral_service   | SEMI

  -> Poloautomat: Playwright predvyplni kataster, ty kliknes CAPTCHA,
     agent precita a vyhodnoti sekcie B/C/D automaticky.


4. PRISTUPOVA CESTA A INFRASTRUKTURA
  Sirka cesty min 6 m (hasici)           | overpass_service    | AUTO
  Povrch cesty (asfalt, dlazba...)       | overpass_service    | AUTO
  Elektrina - blízkost vedenia           | overpass_service    | AUTO
  Elektrina - kapacita trafostanice      | -                   | MANUAL (ZSDIS)
  Vodovod - blízkost                     | overpass_service    | AUTO
  Kanalizacia / zumpa povolena           | overpass_service    | AUTO
  Plyn (volitelny)                       | overpass_service    | AUTO


5. TEREN, GEOLOGIA A HYDRO
  Mimo zaplavoveho uzemia Q100           | flood_service       | AUTO (SHMU WMS)
  Sklon max 15% (idealne do 5%)          | terrain_service     | AUTO (DMR 5.0)
  Orientacia svahu (juh/juhovychod)      | terrain_service     | AUTO (DMR 5.0)
  Nadmorska vyska max 400 m              | terrain_service     | AUTO (DMR 5.0)
  Mimo zosuvneho uzemia                  | terrain_service     | AUTO (SGUDSH)
  Radonove riziko max trieda 2           | terrain_service     | AUTO (SGUDSH)
  Spodna voda - varovanie                | terrain_service     | SEMI (BPEJ proxy)


6. OCHRANE PASMA A ENVIRONMENT
  Mimo ochranneho pasma VVN (25 m)       | overpass_service    | AUTO
  Mimo ochranneho pasma VTL plynu (50 m) | overpass_service    | AUTO
  Mimo 50 m od lesa                      | overpass_service    | AUTO
  Mimo Natura 2000 / CHKO / NPR          | protected_service   | AUTO (SOP SR WMS)
  Mimo archeologickej zony               | -                   | MANUAL (KPU)
  Bez skaldky v okolí 500 m              | overpass_service    | AUTO
  Bez priemyslu v 300 m                  | overpass_service    | AUTO
  Environmentalna zataz (SAZP)           | env_service         | SEMI


7. BONITA PODY (BPEJ)
  Ochrana trieda max 6 (1-4 = drahe)     | bpej_service        | AUTO (BPEJ WMS)
  Odhad odvodov za vynatie z PPF         | bpej_service        | AUTO


8. TRHOVA ANALYZA
  EUR/m2 vs. lokalny priemer             | price_service       | AUTO
  Dlzka inzercie (motivacia predajcu)    | price_service       | AUTO
  Historia zmien ceny                    | price_service       | AUTO


9. OKOLIE A DOSTUPNOST
  Skola do 5 km                          | overpass_service    | AUTO
  Obchod do 3 km                         | overpass_service    | AUTO
  Autobusova zastavka do 2 km            | overpass_service    | AUTO
  Dialnicny privazan do 20 km            | overpass_service    | AUTO
  Hluk: min 50 m od dialnice/zeleznice   | overpass_service    | AUTO


PREHLAD:
  AUTO  (bez brzdenia) : 28 kriterii - GIS, OSM, teren, cena, okolie
  SEMI  (1 krok od teba):  9 kriterii - kataster CAPTCHA, UP-OCR, spodna voda
  MANUAL (checklist)   :  3 kriteria - kapacita trafo, archeologia, env. zataz


==============================================================
5. RESEARCH STRATEGY - ZDROJE A LEGALNOST
==============================================================

LEGENDA ZON:
  GREEN  = bezpecne automatizovat (overene robots.txt)
  YELLOW = opatrne (nutny neutralny User-Agent, obmedzenia)
  RED    = nevyuzivat (ToS zakazuje automatizovany pristup)


GREEN ZONA - bezi naplno, bez brzdenia:

  Nehnutelnosti.sk   | AUTO | sitemap-listings; /api/ blokovane
  TopReality.sk      | AUTO | limit 10 req/min podla robots.txt
  Notarske drazby    | AUTO | notar.sk/drazby - verejny register zo zakona
  SPF                | AUTO | pozemkovyfond.sk - verejne obchodne sutaze
  Obchodny vestnik   | AUTO | justice.gov.sk - konkurzy, drazby, likvidacie (!)
  Exekutorske drazby | AUTO | sexe.sk - zabavene pozemky pod trhovym cenou (!)
  Drazby.net         | AUTO | agregator drazob - jeden zdroj, vela ponuk
  EKS statny majetok | AUTO | eks.sk - statny a samospravny majetok
  BSK kraj           | AUTO | regionbratislava.sk - prebytocny majetok
  Obce uradne tabule | SEMI | roztrocene weby obci, parser per-obec

  (!) = obzvlast zaujimave pre lacne investicne pozemky

YELLOW ZONA - opatrne:

  Reality.sk         | AUTO | robots.txt zakazuje AI-bot UA -> neutralny UA
  Byty.sk            | AUTO | overit robots.txt pred spustenim
  Bazos.sk           | SEMI | /search.php blokovany - len priame URL linky
  Bankove drazby     | SEMI | ToS per-banka - overit individualne

RED ZONA - nevyuzivat:

  Facebook Marketplace | --- | ToS explicitne zakazuje automatizovany pristup


GIS ZDROJE (otvorene data SR - plne legalne):

  ZBGIS WFS/WMS (UGKK)  | Geometria parciel, ortofoto
  DMR 5.0 WCS (UGKK)    | LiDAR vyskopis - sklon, orientacia, vyska
  SRTM/Copernicus DEM   | Globalny vyskopis 30m - fallback
  SHMU WMS              | Zaplavove uzemia Q100
  SGUDSH WMS            | Zosuvne uzemia, radonove riziko
  BPEJ WMS (geodata)    | Bonita pody, ochranné triedy, odvody
  SOP SR WMS            | Natura 2000, CHKO, NPR
  SAZP WMS              | Environmentalna zataz (ak dostupne)
  Overpass (OSM)        | Cesty, elektrina, voda, les, hluk, vybavenost
  Nominatim (OSM)       | Geocoding adres


ZASADY BEZPECNEHO SCRAPINGU:

  1. Kontrolovat robots.txt pred kazdym scrapom
  2. Dodriat rate-limity (TopReality: 10/min, ostatne: 5-30/min)
  3. Pouzivat neutralny User-Agent pre YELLOW zonu
  4. Preferovat sitemap / oficialne API pred crawlovanim
  5. Cachovat - netahat tie iste data opakovane v kratkom case
  6. Exponential backoff pri rate-limit / chybovej odpovedi

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





