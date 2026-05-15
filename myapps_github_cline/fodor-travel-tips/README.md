# ✈️ Fodor Travel TIPs

**Aplikácia na objavovanie bodov záujmu v oblasti kam cestujete.**

Zadáte destináciu (alebo kliknete na mapu), nastavíte okruh hľadania a aplikácia vám nájde **10 mainstream** a **10 alternatívnych/zaujímavých** miest s popismi, počasím a relevantnými linkami.

---

## 🌟 Funkcie

- 🗺️ **Interaktívna mapa** - klikni alebo hľadaj textom
- 📏 **Okruh hľadania** - v km alebo čase cestovania (1h 30min, autom/bicyklom/pešo)
- 🌤️ **Počasie** - predpoveď na vybraný dátum, vizuálna mapa počasia v celej oblasti (3x3 grid)
- 🏆 **10 Mainstream POI** - najznámejšie a najpopulárnejšie miesta
- 💎 **10 Alternatívnych POI** - skryté poklady, menej preskúmané miesta
- 🔗 **5 linkov pre každé miesto** - Wikipedia, Oficiálny web, Google Maps + Reddit/AllTrails/Wikivoyage/iNaturalist
- 🎨 **Dynamické farby** - téma sa prispôsobí oblasti (hory=zelená, more=modrá, mesto=indigo, vidiek=hnedá)
- 🌐 **SK + EN** - prepínateľný jazyk

---

## 🚀 Ako spustiť lokálne

### 1. Klonovať repozitár
```bash
git clone <repo-url>
cd fodor-travel-tips
```

### 2. Vytvoriť virtuálne prostredie
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Nainštalovať závislosti
```bash
pip install -r requirements.txt
```

### 4. Spustiť
```bash
python app.py
```

### 5. Otvoriť v prehliadači
```
http://localhost:5000
```

---

## ☁️ Deploy na Render.com (zadarmo)

### 1. Push na GitHub
```bash
git init
git add .
git commit -m "Initial commit - Fodor Travel TIPs"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Render.com setup
1. Ísť na [render.com](https://render.com) a zaregistrovať sa zadarmo
2. Kliknúť **"New" → "Web Service"**
3. Pripojiť GitHub repozitár
4. Nastavenia:
   - **Name:** fodor-travel-tips
   - **Runtime:** Python
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && gunicorn app:app --bind 0.0.0.0:$PORT`
5. Kliknúť **"Create Web Service"**

Alternatívne: Render automaticky rozpozná `render.yaml` súbor.

### ⚠️ Cold Start
Na free plán server "zaspí" po 15 min nečinnosti. Prvé otvorenie po pauze trvá ~30s.

---

## 🛠️ Technológie

| Komponent | Technológia |
|-----------|------------|
| Backend | Python Flask |
| Frontend | HTML5 + CSS3 + Vanilla JS |
| Mapa | Leaflet.js + OpenStreetMap |
| POI dáta | Overpass API (OpenStreetMap) |
| Popisy | Wikipedia REST API |
| Oficiálne weby | Wikidata API |
| Počasie | Open-Meteo API |
| Geocoding | Nominatim (OpenStreetMap) |
| Routing/čas | OSRM |
| Hosting | Render.com |

**✅ Žiadne API kľúče! Všetky služby sú 100% zadarmo a open-source.**

---

## 📁 Štruktúra projektu

```
fodor-travel-tips/
├── backend/
│   ├── app.py                    # Flask hlavný súbor
│   ├── requirements.txt          # Python závislosti
│   ├── routes/
│   │   ├── geocoding.py          # Geocoding endpointy
│   │   ├── poi.py                # POI hľadanie
│   │   └── weather.py            # Počasie endpointy
│   └── services/
│       ├── geocoding_service.py  # Nominatim + OSRM
│       ├── overpass_service.py   # OpenStreetMap POI
│       ├── wikipedia_service.py  # Wikipedia + Wikidata
│       ├── links_service.py      # Generovanie 5 linkov
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
├── render.yaml                   # Render.com config
├── .env.example                  # Príklad env premenných
├── .gitignore
└── README.md
```

---

## 🔗 Linky pre každé POI (5 kusov)

### Povinné (vždy 3):
1. 🌐 **Oficiálny web** (z Wikidata)
2. 📖 **Wikipedia** (SK preferencia, EN fallback)
3. 🗺️ **Google Maps** (z koordinát)

### Kontextové (2 podľa typu POI):
| Typ POI | Link 4 | Link 5 |
|---------|--------|--------|
| Príroda/Outdoor | 🥾 AllTrails | 💬 Reddit r/hiking |
| Historické/Kultúrne | 📚 Wikivoyage | 💬 Reddit r/travel |
| Mestá/Námestia | 📚 Wikivoyage | 💬 Reddit r/travel |
| Prírodné javy | 🌿 iNaturalist | 🥾 AllTrails |
| Jaskyne/Geológia | 🌿 iNaturalist | 💬 Reddit r/travel |
| Náboženské | 📚 Wikivoyage | 💬 Reddit r/travel |

---

## 📝 Autor

**Robert Fodor** | 2026