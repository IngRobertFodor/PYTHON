🏡 Land Research Invest
=======================

AI agent na vyhľadávanie lacných stavebných pozemkov (orná pôda / IBV) do 70 km od Bratislavy.

Zadáte kritériá (cena, rozloha, vzdialenosť) a agent prehľadá realitné portály,
overí pozemky voči verejným datasetom (kataster, záplavy, bonita pôdy, infraštruktúra),
oskóruje ich a pripraví report + manuálny checklist pre kataster.


🌟 Funkcie
----------

- 🤖 AI agent (Google Gemini) - autonómne vyhľadávanie a rozhodovanie
- 🏘️ Scraping realitných portálov - Nehnutelnosti.sk, Reality.sk (Playwright)
- 🗺️ ZBGIS kataster - geometria parcely (šírka, tvar, výmera) cez WFS
- 🌊 Záplavové územia Q100 - kontrola cez SHMÚ WMS
- 🌱 Bonita pôdy (BPEJ) - ochranná skupina + odhad odvodov za vyňatie z PPF
- 🚗 Infraštruktúra - prístupová cesta (šírka), elektrina, voda cez Overpass API
- 📏 Vzdialenosť od Bratislavy - Haversine + odhad času jazdy
- 📊 Skórovací systém - vážené hodnotenie 0-100 podľa kritérií
- 📋 Kataster checklist - manuálny sprievodca kontrolou LV (sekcie B/C/D)
- 🗺️ Interaktívna mapa - Leaflet.js s farebne odlíšenými kandidátmi


🚀 Ako spustiť lokálne
-----------------------

1. Prejsť do priečinka

    cd myapps_github_cline/land_research_invest/backend

2. Vytvoriť virtuálne prostredie

    python -m venv venv
    venv\Scripts\activate       # Windows
    source venv/bin/activate    # Linux/Mac

3. Nainštalovať závislosti

    pip install -r requirements.txt
    playwright install chromium

4. Nastaviť API kľúč

    Skopírovať .env.example na .env a doplniť:
    GOOGLE_API_KEY=váš_kľúč_sem

5. Spustiť

    python app.py

6. Otvoriť v prehliadači

    http://localhost:5001


🛠️ Technológie
---------------

Komponent             | Technológia
----------------------|---------------------------
Backend               | Python Flask
AI agent              | LangChain + Google Gemini (langchain-google-genai)
AI fallback           | Anthropic Claude (langchain-anthropic)
Frontend              | HTML5 + CSS3 + Vanilla JS
Mapa                  | Leaflet.js + OpenStreetMap
Realitné dáta         | Playwright (scraping Nehnutelnosti.sk, Reality.sk)
Kataster / geometria  | ZBGIS WFS (ÚGKK)
Záplavy Q100          | SHMÚ WMS
Bonita pôdy BPEJ      | MPSR / geodata.gov.sk WMS
Infraštruktúra        | Overpass API (OpenStreetMap)
Geocoding             | Nominatim (OpenStreetMap)
GIS spracovanie       | geopandas, shapely, pyproj, owslib

⚠️  LLM vyžaduje GOOGLE_API_KEY (Gemini má veľký free tier).
✅  Všetky GIS/geo služby sú 100% zadarmo a open-source.


📁 Štruktúra projektu
---------------------

land_research_invest/
├── backend/
│   ├── app.py                            # Flask hlavný súbor
│   ├── requirements.txt                  # Python závislosti
│   ├── routes/
│   │   ├── search_routes.py              # /api/scan, /api/search
│   │   └── parcel_routes.py              # /api/parcel/<id>
│   ├── services/
│   │   ├── llm_agent_service.py          # 🧠 AI orchestrátor (Gemini)
│   │   ├── realestate_scraper_service.py # Playwright scraping
│   │   ├── zbgis_service.py              # Kataster geometria (WFS)
│   │   ├── flood_service.py              # SHMÚ Q100 (WMS)
│   │   ├── bpej_service.py               # Bonita pôdy
│   │   ├── overpass_service.py           # Infraštruktúra (OSM)
│   │   ├── geocoding_service.py          # Nominatim
│   │   ├── distance_service.py           # Vzdialenosť od BA
│   │   ├── scoring_service.py            # Skórovací algoritmus
│   │   └── cadastral_service.py          # Kataster checklist
│   └── models/
│       ├── parcel.py                     # Dátový model pozemku
│       └── criteria.py                   # Kritériá
├── frontend/
│   ├── index.html                        # Dashboard
│   ├── css/style.css
│   └── js/
│       ├── app.js                        # Hlavná logika
│       └── map.js                        # Leaflet mapa
├── config/
│   └── criteria.yaml                     # Používateľské kritériá
├── tests/                                # Pytest test suite
├── docs/                                 # Markdown dokumentácia (pre skills)
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── CRITERIA.md
│   └── HOW_TO_RUN_THIS_APP.md
├── .env.example
├── .gitignore
├── pytest.ini
├── pyrightconfig.json
├── start_app.bat
├── HOW_TO_RUN_THIS_APP.txt
├── ARCHITECTURE.txt
├── CRITERIA.txt
└── README.txt                            ← tento súbor


🧪 Testovanie
--------------

    python -m pytest tests/ -v --rootdir=.


📝 Autor
---------

Robert Fodor | 2026
