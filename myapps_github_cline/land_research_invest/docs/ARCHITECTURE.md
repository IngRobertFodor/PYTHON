# 🏗️ Architektúra — Land Research Invest Agent

## Prehľad

AI-driven agent, ktorý kombinuje LLM reasoning (Google Gemini) s deterministickými
GIS validátormi a scoring engine. Agent má sadu **tools** (nástrojov), ktoré volá
autonómne podľa workflowu. Sekundárny LLM (Anthropic Claude) slúži ako fallback.

---

## 🧱 Vrstvy systému

```
┌──────────────────────────────────────────────────────────────┐
│          AI ORCHESTRATOR  (llm_agent_service.py)             │
│          Google Gemini (primárny)                            │
│          Anthropic Claude (fallback)                         │
│          LangChain agent + tools                             │
└──────────────────┬───────────────────────────────────────────┘
                   │  volá tools (LangChain @tool)
      ┌────────────┼────────────────┬──────────────────┐
      ▼            ▼                ▼                  ▼
[Scraper]     [GIS validators]  [Scoring]        [Checklist]
realestate_   zbgis_service     scoring_         cadastral_
scraper_      flood_service     service.py       service.py
service.py    bpej_service
              overpass_service
              distance_service
              geocoding_service
```

---

## 🔄 Tok dát (workflow)

1. Používateľ zadá kritériá (`config/criteria.yaml` alebo cez webové UI)
2. Agent zavolá tool: `search_real_estate_portals` → zoznam URL kandidátov
3. Pre **každý** nájdený pozemok agent postupne volá:
   - `geocoding_service` → GPS súradnice z adresy inzerátu
   - `zbgis_service` → geometria parcely (šírka, tvar, výmera)
   - `distance_service` → vzdialenosť a čas jazdy od Bratislavy
   - `flood_service` → kontrola Q100 záplavového pásma
   - `overpass_service` → prístupová cesta, elektrina, voda (OSM)
   - `bpej_service` → bonita pôdy, ochranná skupina, odvody
4. `scoring_service` → vážené skóre 0–100 + odporúčanie
5. Ak skóre > prah (default 70): `cadastral_service` → manuálny LV checklist
6. Výsledok: **TOP N pozemkov** s reportom + checklistami

---

## 📊 Skórovací algoritmus

| Kritérium | Váha |
|-----------|------|
| Cena | 20 % |
| Vzdialenosť od BA | 15 % |
| Infraštruktúra | 25 % |
| Právna čistota (proxy) | 20 % |
| Záplavové riziko | 10 % |
| Bonita pôdy (BPEJ) | 10 % |

| Skóre | Odporúčanie |
|-------|-------------|
| ≥ 85 | ✅ STRONG BUY |
| ≥ 70 | 🔍 INVESTIGATE |
| ≥ 50 | 🤔 CONSIDER |
| < 50 | ❌ SKIP |

---

## 🌐 Súradnicové systémy

| Systém | EPSG | Použitie |
|--------|------|----------|
| WGS-84 | 4326 | GPS, Nominatim, Leaflet.js |
| S-JTSK | 5514 | Slovenský kataster (ZBGIS) |
| Konverzia | pyproj | `wgs84_to_jtsk()`, `jtsk_to_wgs84()` |

---

## 🤖 LLM konfigurácia

| Parameter | Hodnota |
|-----------|---------|
| Primárny LLM | Google Gemini (`gemini-1.5-flash` alebo novší) |
| Knižnica | `langchain-google-genai >= 4.4.0` |
| API kľúč | `GOOGLE_API_KEY` (v `.env`) |
| Fallback LLM | Anthropic Claude (`claude-3-5-sonnet`) |
| Fallback knižnica | `langchain-anthropic >= 1.0.0` |
| Fallback kľúč | `ANTHROPIC_API_KEY` (voliteľné, v `.env`) |
| Temperature | `0.2` (nízka = konzistentné výsledky) |
| Max iterations | `50` (ochrana pred nekonečnou slučkou) |
| Free tier | Gemini: ✅ áno (veľký); Claude: ❌ nie |

---

## 🔌 Externé endpointy

> ⚠️ WMS/WFS endpointy slovenských štátnych služieb sa môžu meniť. Vždy overiť aktuálnosť pred implementáciou.

| Služba | Endpoint (orientačný) |
|--------|----------------------|
| ZBGIS WFS | `https://zbgis.skgeodesy.sk/wfs/default` |
| SHMÚ WMS | `https://geo.shmu.sk/wms` |
| BPEJ WMS | `https://geodata.gov.sk/geoserver/wms` |
| Overpass API | `https://overpass-api.de/api/interpreter` |
| Overpass mirror | `https://overpass.kumi.systems/api/interpreter` |
| Nominatim | `https://nominatim.openstreetmap.org/search` |
| Gemini API | `https://generativelanguage.googleapis.com` |

---

## 🗂️ Kľúčové súbory a zodpovednosť

| Súbor | Zodpovednosť |
|-------|-------------|
| `llm_agent_service.py` | LangChain agent, tool definície, system prompt |
| `realestate_scraper_service.py` | Playwright scraping (stealth mode) |
| `zbgis_service.py` | WFS queries, geometria, šírka parcely |
| `flood_service.py` | SHMÚ WMS, Q100 pixel analýza |
| `bpej_service.py` | BPEJ WMS, ochranná skupina, odvody |
| `overpass_service.py` | Overpass QL, cesty / elektrina / voda |
| `geocoding_service.py` | Nominatim → GPS súradnice |
| `distance_service.py` | Haversine vzdialenosť, čas jazdy |
| `scoring_service.py` | Vážené skóre 0–100, odporúčanie |
| `cadastral_service.py` | Manuálny LV checklist (B/C/D sekcie) |
| `models/parcel.py` | Pydantic model pozemku |
| `models/criteria.py` | Pydantic model kritérií |
| `config/criteria.yaml` | Používateľské nastavenia (cena, km, m²) |

---

## 📝 Autor

Robert Fodor | 2026
