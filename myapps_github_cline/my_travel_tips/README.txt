✈️ My Travel Tips
=================

Aplikácia na objavovanie bodov záujmu v oblasti kam cestujete.

Zadáte destináciu (alebo kliknete na mapu), nastavíte okruh hľadania a aplikácia vám nájde 10 mainstream a 10 alternatívnych/zaujímavých miest s popismi, počasím a relevantnými linkami.


🌟 Funkcie
----------

- 🗺️ Interaktívna mapa - klikni alebo hľadaj textom
- 📏 Okruh hľadania - v km alebo čase cestovania (1h 30min, autom/bicyklom/pešo)
- 🌤️ Počasie - predpoveď na vybraný dátum, vizuálna mapa počasia v celej oblasti (3x3 grid)
- 🏆 10 Mainstream POI - najznámejšie a najpopulárnejšie miesta
- 💎 10 Alternatívnych POI - skryté poklady, menej preskúmané miesta
- 🔗 5 cielených linkov pre každé miesto - podľa typu POI (AllTrails, Wikiloc, Komoot, TripAdvisor, Atlas Obscura...)
- 🥾 Turistické trasy a cyklotrasy - vyhľadávanie OSM route relations
- 🎨 Dynamické farby - téma sa prispôsobí oblasti (hory=zelená, more=modrá, mesto=indigo, vidiek=hnedá)
- 🌐 SK + EN - prepínateľný jazyk


🚀 Ako spustiť lokálne
-----------------------

1. Klonovať repozitár

    git clone <repo-url>
    cd my_travel_tips

2. Vytvoriť virtuálne prostredie

    cd backend
    python -m venv venv
    venv\Scripts\activate       # Windows
    source venv/bin/activate    # Linux/Mac

3. Nainštalovať závislosti

    pip install -r requirements.txt

4. Spustiť

    python app.py

5. Otvoriť v prehliadači

    http://localhost:5000


🛠️ Technológie
---------------

Komponent          | Technológia
-------------------|---------------------------
Backend            | Python Flask
Frontend           | HTML5 + CSS3 + Vanilla JS
Mapa               | Leaflet.js + OpenStreetMap
POI dáta           | Overpass API (OpenStreetMap)
Popisy             | Wikipedia REST API
Oficiálne weby     | Wikidata API
Počasie            | Open-Meteo API
Geocoding          | Nominatim (OpenStreetMap)
Routing/čas        | OSRM
Hosting            | Render.com

✅ Žiadne API kľúče! Všetky služby sú 100% zadarmo a open-source.


📁 Štruktúra projektu
---------------------

my_travel_tips/
├── backend/
│   ├── app.py                    # Flask hlavný súbor
│   ├── requirements.txt          # Python závislosti
│   ├── routes/
│   │   ├── geocoding.py          # Geocoding endpointy
│   │   ├── poi.py                # POI hľadanie
│   │   └── weather.py            # Počasie endpointy
│   └── services/
│       ├── geocoding_service.py  # Nominatim + OSRM
│       ├── overpass_service.py   # OpenStreetMap POI (51 tagov)
│       ├── wikipedia_service.py  # Wikipedia + Wikidata
│       ├── links_service.py      # Cielené linky (15 typov POI)
│       ├── weather_service.py    # Open-Meteo počasie
│       └── region_theme_service.py # Dynamické témy
├── frontend/
│   ├── index.html                # Hlavná stránka
│   ├── css/
│   │   ├── style.css             # Hlavné štýly
│   │   └── themes.css            # Farebné témy
│   └── js/
│       ├── app.js                # Hlavná logika
│       ├── i18n.js               # SK/EN preklady
│       ├── map.js                # Leaflet mapa
│       ├── poi.js                # POI karty
│       ├── theme.js              # Správa tém
│       └── weather.js            # Počasie widget
├── tests/                        # Pytest test suite (226 testov)
├── render.yaml                   # Render.com config
├── test_results.txt              # Výsledky testov
└── README.txt


🗂️ Kategórie POI (frontend checkboxes)
----------------------------------------

🏛️ Historické a kultúrne:
  - 🏰 Hrady a zámky
  - 🏛️ Pamätníky a monumenty
  - ⛏️ Archeológia a ruiny
  - 🏭 Industriálne dedičstvo (bane, majáky, veterné mlyny)
  - ⛪ Kostoly a kaplnky
  - 🕌 Kláštory
  - 🧱 Mestské brány a hradby
  - 🏡 Kaštiele a šľachtické sídla
  - 🏛️ Akvadukty
  - ⚓ Vraky lodí
  - 🏛️ Historické trhoviská

🎭 Kultúra a vzdelávanie:
  - 🏛️ Múzeá a galérie
  - 🎭 Divadlá a kultúrne centrá
  - 🎨 Sochy a umelecké diela

🌿 Príroda a outdoor:
  - 🌊 Vodopády
  - 🦇 Jaskyne
  - ⛰️ Horské vrcholy
  - 👁️ Vyhliadky
  - 🌺 Parky a záhrady
  - 💧 Pramene a termálne pramene
  - 🪨 Geologické útvary
  - 🌋 Sopky a gejzíry
  - 🧊 Ľadovce
  - 🏖️ Pláže
  - 🪨 Ikonické skaly
  - 🌊 Pereje
  - 🌲 Národné parky a chránené oblasti
  - 🦋 Prírodné rezervácie

🥾 Turistika a pohyb:
  - 🥾 Turistické trasy (OSM hiking routes)
  - 🚴 Cyklotrasy (OSM bicycle routes)
  - 🏕️ Turistické útulne a horské chaty
  - 🏃 Turistické okruhy

🎡 Zábava a aktivity:
  - 🎢 Zábavné parky
  - 🦁 ZOO a akváriá
  - 💦 Vodné parky
  - ⭐ Turistické atrakcie
  - 🏖️ Turistické rezorty


🔗 Cielené linky pre každé POI (5 kusov)
-----------------------------------------

Každý typ POI dostáva presne cielené linky na relevantné zdroje:

Typ POI              | Link 1         | Link 2      | Link 3      | Link 4       | Link 5
---------------------|----------------|-------------|-------------|--------------|-------------
🥾 Turistická trasa  | Wikiloc        | AllTrails   | Komoot      | Wikipedia    | Google Maps
🚴 Cyklotrasa        | Komoot         | AllTrails   | Strava      | Wikipedia    | Google Maps
🏰 Hrad/Zámok        | Ofic. web      | Wikipedia   | Google Maps | TripAdvisor  | Wikivoyage
🌊 Vodopád           | AllTrails      | Wikipedia   | Google Maps | iNaturalist  | Wikiloc
🌲 Národný park      | Ofic. web      | Wikipedia   | Google Maps | AllTrails    | Komoot
⛰️ Vrchol            | AllTrails      | Wikiloc     | Google Maps | Wikipedia    | Komoot
👁️ Vyhliadka         | AllTrails      | Wikiloc     | Google Maps | Wikipedia    | Komoot
🌋 Sopka/Gejzír      | Wikipedia      | Google Maps | AllTrails   | iNaturalist  | Atlas Obscura
🪨 Geológia           | iNaturalist    | Wikipedia   | Google Maps | Atlas Obscura| AllTrails
⛏️ Archeológia        | Wikipedia      | Google Maps | Wikivoyage  | Atlas Obscura| TripAdvisor
⛪ Kostol/Kláštor     | Ofic. web      | Wikipedia   | Google Maps | Wikivoyage   | TripAdvisor
🏖️ Pláž              | Wikipedia      | Google Maps | AllTrails   | TripAdvisor  | iNaturalist
🏕️ Horská chata      | Komoot         | AllTrails   | Wikiloc     | Wikipedia    | Google Maps
💎 Atlas Obscura POI  | Atlas Obscura  | Wikipedia   | Google Maps | Reddit       | iNaturalist


🧪 Testovanie
--------------

    python -m pytest tests/ -v --rootdir=.

226 testov pokrýva: overpass/POI, links, geocoding, weather, themes, routes, frontend.


☁️ Deploy na Render.com (zadarmo)
----------------------------------

1. Push na GitHub
2. Ísť na render.com (https://render.com) -> New -> Web Service
3. Pripojiť GitHub repozitár
4. Nastavenia:
   - Build Command: pip install -r backend/requirements.txt
   - Start Command: cd backend && gunicorn app:app --bind 0.0.0.0:$PORT

Alternatívne: Render automaticky rozpozná render.yaml súbor.

⚠️ Cold Start
Na free plán server "zaspí" po 15 min nečinnosti. Prvé otvorenie po pauze trvá ~30s.


📝 Autor
---------

Robert Fodor | 2026