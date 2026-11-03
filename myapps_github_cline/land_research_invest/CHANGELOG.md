# Changelog

Míľniky projektu. Pre podrobný wave-by-wave log pozri `git log`.

---

## 2026-11 — Audit + logging refaktoring

- **Audit P1:** Nahradené všetky `print()` v produkčných Python súboroch za `logging` (štandardná knižnica)
  - Dotknuté súbory: `base_scraper`, `scraper_service`, `scoring_service`, `scrape_routes`, `nehnutelnosti_scraper`, `topreality_scraper`, `notarske_drazby_scraper`, `ske_scraper`, `spf_scraper`, `obchodny_vestnik_scraper`, `url_fetch_service`, `signals`
  - `logger = logging.getLogger(__name__)` v každom module — správna hierarchia logov
  - Úroveň: `WARNING` pre recoverable chyby, `INFO` pre diagnostiku, `DEBUG` pre parsing detaily
  - Výsledok: `print()` ostali len v `data/analyza_scoring.py` a `data/build_obce_sk.py` (diagnostické skripty, nie serverový kód)
- **Audit P1:** `except Exception: pass` (bez logu) v `signals.py` → doplnený `logger.debug`
- **Všetky 1546 testov prechádza** po zmenách

## 2026-11 — P2: Route testy + bugfix backup validácie

- **P2 route testy** — pridané do `tests/test_app.py` (žiadne nové súbory):
  - `TestConfigRoutes` (15 testov): `GET /api/config/`, `GET /api/config/validate`, `POST /api/config/limits` — všetky kombinácie OK/4xx, whitelist, type-check, round-trip so zálohou configu
  - `TestBackupRoutes` (14 testov): `GET /api/backup/status`, `GET /api/backup/history`, `GET /api/backup/export`, `POST /api/backup/import` — vrátane gzip validácie, roundtrip export→import, rate-limit 429
  - `TestFetchUrlEndpoint` (7 testov): `POST /api/parcels/fetch-url` — missing URL 400, nepodporovaný portál 400, sieťová chyba 502, parser exception 500, úspešný parse 200
- **Bugfix P0 — `backup_service._validate_gz_sql`**: `gzip.decompress(gz_bytes[:512])` → `gzip.decompress(gz_bytes)[:512]` — truncated gzip stream spôsoboval `ValueError` pri každom importe reálnej zálohy (funkcia nikdy nepracovala správne pre súbory > ~512 B komprimovaného obsahu)
- **Celkový počet testov: 1572** (+26), všetky zelené

## 2026-11 — Vlna C1: AI Orchestrator (backend)

- **`backend/services/llm_agent_service.py`** — AI agent cez Google Gemini (google-genai SDK)
  - 9 toolov: `get_parcels`, `get_run_summary`, `analyze_parcel_gis`, `get_peer_statistics`,
    `get_up_coverage`, `explain_investment`, `get_diff`, `get_backup_status`, `export_csv_filtered`
  - Model management: primárny `gemini-3.5-flash` + záložný `gemini-3.1-flash-lite`; override cez `.env LLM_MODEL`
  - Automatický fallback pri deprecated/quota/network chybách
  - Hybrid model discovery: Google API `models.list()` (3s timeout) → hardcoded fallback zoznam
  - Health check s 24h cache; exports cleanup (súbory staršie ako 24h)
- **`backend/routes/agent_routes.py`** — REST endpoints:
  - `POST /api/agent/ask` — hlavný chat (max 500 znakov)
  - `GET  /api/agent/status` — dostupnosť + aktuálny model
  - `GET  /api/agent/health` — detailný stav modelov (primary / fallback / active)
  - `GET  /api/agent/available-models` — hybrid zoznam
  - `POST /api/agent/select-model` — override modelu (uloží do Flask session)
  - `POST /api/agent/clear-model` — vymaže override
  - `GET  /api/agent/exports/<file>` — stiahne CSV export (path traversal guard)
- **`backend/app.py`** — registrácia `agent_bp` + `SECRET_KEY` pre Flask session
- **`tests/test_llm_agent_service.py`** — 49 testov, 100% mocked LLM (žiadne reálne volania)
- **Reálny test**: `gemini-3.5-flash` úspešne odpovedá v SK + tool-calling funguje (`get_run_summary`)
- **Celkový počet testov: 1621** (+49), všetky zelené

## 2026-11 — Vlna C2: AI Orchestrator UI (chat panel)

- **`frontend/js/ai_agent.js`** — vanilla JS trieda `AIAgent` (floating chat panel)
  - Toggle tlačidlo `💬 AI asistent` vpravo dole (fixed, zbalený pri štarte)
  - Resizable panel: drag za ľavý-horný roh (min 300×400, max 800×90vh)
  - Prompt chips (5 predvolených otázok) — klik = automatické odoslanie
  - Chat bubliny (user / AI / error) s jednoduchým markdown-light renderingom (bold, code, lists)
  - Tool call chips pod AI odpoveďou — zobrazí aký tool bol volaný
  - Loading animácia (3 bodky) počas čakania na odpoveď
  - Warning banner keď primárny model nefunguje + ⚙️ model picker modal
  - Model picker: `GET /api/agent/available-models` → rádio buttons → `POST /api/agent/select-model`
  - Chat história v `localStorage` (posledných 30 správ, per session)
  - Model override v `localStorage` (perzistuje medzi F5)
  - Plne responzívny: pod 640px = fullscreen panel
  - `Esc` zavrie panel; `Enter` odošle (Shift+Enter = nový riadok)
- **`frontend/css/ai_agent.css`** — izolovaný CSS (nezasahuje do existujúcich štýlov)
- **`frontend/index.html`** — pridaný `<div id="ai-agent-root">` + CSS + JS linky
- **`tests/test_app.py`** — +3 testy: HTML obsahuje AI placeholder, CSS link, JS link
- **Celkový počet testov: 1624** (+3), všetky zelené


- **Q1:** Signál `PODIEL_ALEBO_CHYBNE_DATA` + cap Investment indexu na max 30 pri area < 100 m²
- **Q2:** `preliminary_signals()` volané v `_run()`; `_enrich_from_db` vždy prepočíta index + peer/opportunity
- **Q3:** UI — separátne `<td>` pre Index a Skóre + `inv-zero` badge
- **Q4:** Location fix — nehnutelnosti slug min. 4 znaky, topreality zátvorkový guard, backfill
- **Q5:** OV parser prepísaný — 3 extraktory (`_try_vertical_form`, `_try_flow_text`, `_try_specifikacia`), validovaný na 4 reálnych PDF; whitespace normalizácia (pypdf vkladá `\n` do názvov obcí)

## 2026-10 — P1/P2: IDE + Záloha

- **P1:** `.vscode/settings.json` + `pyrightconfig.json` — oprava IDE import warnings
- **P2:** `backup_service.py` + `backup_routes.py` + UI — gzipped SQL dump, merge import, rotovaná história (max 20), auto-backup po scrape

## 2026-10 — UX F1–F5

- Oprava preklepov v UI
- `per_source_status` diagnostika (ok/error/timeout/empty) + warn banner
- Humanizované error hlášky (SK)
- Tooltipy
- Dokumentácia aktualizovaná

## 2026-10 — Hardening H1–H5

- `debug=False`, `host=127.0.0.1`, CORS allowlist
- SQLite migrácia — nové stĺpce: `signals_json`, `investment_index`, `invest_summary`, `peer_*`, `first_seen`, `price_history`, auction fields
- SSRF guard v `url_fetch_service._detect_portal` (urlparse + allowlist)
- Nahradené `except: pass` za logging
- Opportunity váhy presunuté do `criteria.yaml`

## 2026-10 — Vlna B1–B4: Investičná awareness

- **B1:** História cien — `first_seen`, `price_history`; signály DLHO_V_PONUKE, CENA_KLESA, HORICE
- **B2:** Dražobné polia — `vyvolavacia_cena_eur`, `znalecka_hodnota_eur`, `drazba_kolo`; signály DRAZBA_POD_ZNALECKOU, DRAZBA_OPAKOVANA
- **B3:** Peer comparison — `peer_analysis_service`; signál LACNEJSI_AKO_OKOLIE (ppsm < 60 % mediánu obce)
- **B4:** Investment Index 0–100 — `opportunity_service`; `explain()` + `apply_opportunity()`

## 2026-09 — Scraping a live testy

- 7 zdrojov aktívnych: nehnutelnosti.sk, topreality.sk, reality.sk, SPF, SKE, notárske dražby, Obchodný vestník
- Live prieskum 2026-10-01: **4 594 parciel**
- Strankovanie všetkých zdrojov (auto-stop + strop 50 strán)
- Paralelizácia (ThreadPoolExecutor), retry, per-zdroj timeout

## 2026-09 — Dvojfázový scoring + SQLite + Diff

- `preliminary_score()` — 0 HTTP, 5 komponentov
- `storage_service` — SQLite perzistencia behov
- `diff_service` — nové/zlacneli/zmizli/still_here
- UP asistent — `uzemny_plan_service` (gisplan.sk + fallback + checklist)

## 2026-08 — GIS scoring + Frontend

- 8 GIS komponentov: flood, terrain, bpej, overpass, protected, zbgis, geocoding, price_analysis
- Weighted scoring (0–100) + report
- Frontend: tabuľka + filter + mapa (Leaflet) + modal s rozpadom skóre
- Monitor service (APScheduler)

---

Autor: Robert Fodor | 2026
