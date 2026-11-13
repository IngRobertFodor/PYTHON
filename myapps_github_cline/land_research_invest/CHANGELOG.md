# Changelog

Míľniky projektu. Pre podrobný wave-by-wave log pozri `git log`.

---

## 2026-11 — Hotfix: duplicitné 🔴 bodky pri rizikových vlajočkách

### 🐛 Problém

Pri niektorých pozemkoch sa v tabuľke zobrazovali **dve červené bodky
🔴🔴** namiesto jednej. Príklad: pozemok v riadku 3878 mal:
- `PODIEL_ALEBO_CHYBNE_DATA` (riziko) → vlajka `⚠️ PODIEL?` + 🔴 bodka (duplikát)
- `LACNEJSI_AKO_OKOLIE` (riziko, „háčik?") → vlajka `📊 Lacný −57 % (háčik?)` + 🔴 bodka (duplikát)

### 🎯 Príčina

V `app.js` r.1093–1094 bol filter `FLAG_KODY` aplikovaný **len na
príležitostné signály** (🟢), nie na rizikové (🔴):

```js
const oppSigs  = sigs.filter(s => s.typ === "PRILEZITOST" && !FLAG_KODY.has(s.kod));
const riskSigs = sigs.filter(s => s.typ === "RIZIKO");  // ❌ chýba filter
```

Dôsledok: každý rizikový signál s vlastnou vlajkou (`PODIEL_ALEBO_CHYBNE_DATA`,
`LACNEJSI_AKO_OKOLIE` typu RIZIKO) sa zobrazil **dvakrát** — raz ako chip,
raz ako samostatná 🔴 bodka.

### ✅ Oprava

Doplnený rovnaký filter aj na rizikové signály:

```js
const riskSigs = sigs.filter(s => s.typ === "RIZIKO" && !FLAG_KODY.has(s.kod));
```

Teraz každý signál s vlastnou vlajkou (chip) je **vylúčený z bodkovej
reprezentácie** — nezávisle od typu. Všeobecné riziká bez vlajky (napr.
`CENA_PODOZRIVA`, `PRILIS_DALEKO`) sa stále zobrazia ako 🔴.

### Verzie: v=44 → v=45

Testy: **1642 zelených** (bez zmien v počte — frontend-only zmena).

---

## 2026-11 — Hotfix: rozbité toggle-funkcie vo frontende + minimalizácia legendy

### 🐛 Kritická oprava: `_renderDiffBanner` nemala uzatváraciu zátvorku

**Problém:** V `frontend/js/app.js` chýbala uzatváracia `}` za telom funkcie
`_renderDiffBanner()` (okolo pôvodného r.1505). Následné top-level funkcie
`_loadBackupStatus`, `onBackupExport`, `onBackupImport`, DOMContentLoaded-handler
a `toggleLegend` sa tým stali **vnorenými function declarations** vo vnútri
`_renderDiffBanner` → neviditeľné z globálneho scope. Každé
`onclick="toggleLegend()"`, `onclick="onBackupExport()"`,
`onchange="onBackupImport(this)"` v HTML vyhadzovalo `ReferenceError`.

`node --check` chybu neodhalil (JS syntakticky validný), prejavila sa
až pri behu v prehliadači.

**Reálne rozbité pred opravou:**
- Zbaliť/rozbaliť legendu v mape (tlačidlo vpravo hore)
- „📤 Stiahnuť zálohu" tlačidlo
- „📥 Obnoviť zo súboru" (import zálohy)
- Auto-refresh statusu zálohy pri otvorení sekcie Záloha

**Oprava:**
- Pridaná chýbajúca `}` na koniec `_renderDiffBanner` (nový r.1523)
- Blok wire-up diff-chip click-handlerov presunutý **dovnútra**
  `_renderDiffBanner` — logicky správne miesto, lebo tam sa chips práve
  vyrenderovali do DOM
- Osirotený duplicitný blok za `toggleLegend` (pôvodné r.1610–1626) odstránený

### 🎨 Krížik v legende → minimalizačné tlačidlo

Predtým používateľ videl `×` (vyzerá ako „zatvoriť navždy"). Teraz je to
jednoznačné **minimalizačné tlačidlo** so šípkou `▴` (zbaliť) / `▾` (rozbaliť):

- `index.html` — `<button class="legend-toggle" type="button"
  aria-label="Minimalizovať legendu" aria-expanded="true">&#9652;</button>`
- `toggleLegend()` — prehodená sémantika šípok (▴ keď rozbalená → klik zbalí,
  ▾ keď zbalená → klik rozbalí) + dynamicky aktualizuje `aria-expanded`
  a `aria-label` pre screen readery
- CSS `.legend-toggle` — pill vzhľad (sivé pozadie `#f1f5f9`, border,
  hover `#e2e8f0` + `focus-visible`) — vyzerá jasne ako tlačidlo,
  nie ako close ikona

### Verzie: v=43 → v=44

Testy: **1642 zelených** (bez zmien v počte — frontend-only zmena).

---

## 2026-11 — Fáza 5 UI polish: tretia dávka — dynamické farby Skóre

### 🎯 Hlavná zmena: tabuľka Skóre teraz rozlišuje Prelim vs Full-GIS

**Problém:** Tabuľka v Skóre stĺpci používala jednu sadu farieb (sýte emerald/amber/
orange/red = **plné GIS skóre** podľa legendy), ale pozemok s `preliminary_score=93.8`
dostal rovnakú **tmavo-zelenú „SILNÁ KÚPA"** farbu, aj keď ešte neprešiel GIS
analýzou. Užívateľ nemal spôsob rozlíšiť „overené" vs „odhad".

**Riešenie:** Dynamické farby podľa `final_score`:
- **`final_score > 0`** → **plné GIS farby** (`full_color()` — sýte Tailwind-500)
  + plný border + box-shadow (`.badge-final`)
- **`final_score == 0`** → **prelim pastel** (`prelim_color()` — Tailwind-300)
  + prerušovaný border, tmavý text pre kontrast (`.badge-prelim`)

**Dopad:**
- Tabuľka ihneď informuje: pastel + dashed border = odhad, sýte + solid border = overené
- Legenda doplnená vysvetleniami: *„GIS skóre — sýte farby + plný okraj"* vs
  *„Prelim skóre — pastel farby + prerušovaný okraj"*
- Tooltip na badge: *„Plné GIS skóre (overené)"* / *„Prelim skóre (odhad — bez GIS)"*

### 📊 Technické detaily
- `prelim_color()` vrátený na pastel Tailwind-300 (`#6ee7b7, #fcd34d, #fdba74, #94a3b8`)
- Nová `full_color()` so sýtymi Tailwind-500 (`#10b981, #f59e0b, #f97316, #ef4444`)
- V `renderResultsTable()`: `hasFinal = (p.final_score || 0) > 0`,
  podľa toho sa vyberá farba, kontrast textu aj CSS trieda
- Mapa (`_prelimMapColor`) už to robila správne — teraz je tabuľka konzistentná

### Verzie: v=41 → v=42
Testy: **1642 zelených** (bez zmien v počte).

---

## 2026-11 — Fáza 5 UI polish: druhá dávka (8 opráv)

Po ďalšom screenshot audite a reálnom teste prieskumu:

### 🎨 Konzistencia s legendou
- **`.inv-badge` farby** zjednotené s legendou (70+ emerald, 50-69 amber,
  30-49 orange, 1-29 red, 0 slate). Predtým: 70+ dark-green, 40-69 navy-blue,
  1-39 grey — nesúladné s legendou v mape a `_scoreColor()`.
- **Thresholdy v JS** zladené v tabuľke aj v modali: 70 / 50 / 30 (predtým 70 / 40)
- **Amber badge** (70-84 Skóre a 50-69 Index) má teraz tmavý text (`#78350f`)
  namiesto bieleho — WCAG kontrast z ~2.3 na ~7+

### 🧹 Legacy čistenie
- **Odstránená prázdna `.results-section` s nadpisom „VYSLEDKY"** ktorá sa
  zobrazovala pod všetkými sekciami ako artefakt pred tabuľkou. `#results-panel`
  presunutý do „Analyzovať 1 pozemok" sekcie (legacy funkcia `renderResults()`
  má kde renderovať jednorazový výsledok).

### 📊 Tabuľka
- **Stĺpec Zdroj** má teraz `max-width: 90px + ellipsis + title=full_text` —
  rieši horizontálny scrollbar
- **Tie-breaker v sorte**: pri rovnakom Index DESC sa druhotne radí podľa
  `preliminary_score DESC`. Skupinky 12 pozemkov s rovnakým Index 40 už
  nevyzerajú náhodne usporiadané.
- **Mini-legenda signálov** (`.sig-hint`) nad tabuľkou vysvetľuje 🟢/🔴/🔥/🔨/📊
  ikony v stĺpci Skóre — predtým užívateľ nevedel čo znamenajú

### 🛠️ Opravy UX
- **Záloha „Načítavam..." fix**: `_loadBackupStatus()` sa teraz volá aj pri
  `DOMContentLoaded` ak je sekcia otvorená (prehliadač remembers stav). Predtým
  visel „Načítavam..." kým používateľ neklikol toggle.
- **„Skórovať vybrané" farba** aktívna zmena z zelenej (`#10b981` kolízia
  s `btn-demo`) na navy (`#1a3a5c`), disabled zo svetlo-zelenej (`#9dbfa0`,
  vyzeralo ako aktívne) na čisté sivé (`#cbd5e1 + #64748b text`)

### 📎 Drobnosti
- **Diff badge „N nezmenených"** — tmavší kontrast (`#e2e8f0 bg + #334155 text`)
- **Verzie**: `v=40 → v=41` pre style.css + všetky JS

Testy: **1642 zelených** (bez zmien v počte).

---

## 2026-11 — Fáza 5 UI polish: vizuálna audit cez live screenshot

Po reálnom teste prieskumu (4916 pozemkov) kompletný prechod cez UI zľava:

### Opravy konzistencie farieb
- **`prelim_color()` v `app.js`** zjednotený s `_scoreColor()` a legendou:
  - 85+ emerald-500 (`#10b981`), 70-84 amber-500 (`#f59e0b`),
    50-69 orange-500 (`#f97316`), <50 red-500 (`#ef4444`)
  - Predtým: stará paleta (`#2e7d32, #1565c0, #e65100, #757575`) — pozemok 75.8
    zelený, 68.6 oranžový → nesedelo s legendou (70+ amber)
- **Prelim marker <50** zmenený z `slate-300` (`#cbd5e1` — takmer neviditeľné
  na svetlosivej mape) na `slate-400` (`#94a3b8`) + zladený v legende

### Vizuálne vylepšenia
- **Legenda** má teraz **toggle (×)** — dá sa zbaliť ak prekrýva mapu
- **3 sekcie legendy** (Index / GIS / Prelim) oddelené horizontálnym dashed
  separátorom (`.legend-group + .legend-group`)
- **Ikona „Analyzovať 1 pozemok"** zmenená z 🔍 (duplicitná s "Spustiť prieskum")
  na 🔬 (mikroskop — jasnejšia metafora pre analýzu)

### Defenzívne CSS opravy
- **Prázdny `.scrape-warn-banner:empty`** — `display: none` + reset padding/border,
  aby neostal visieť ako žltý pruh po skončení prieskumu bez chybných zdrojov
- **Prázdny `.progress-sources:empty`** — rovnako
- JS `showProgressSection(false)` vyčistí `#progress-sources.innerHTML`

### Verzie
- `v=39 → v=40` pre `style.css` a všetky `*.js` (browser cache bust)

Testy: **1642 zelených** (bez zmien v počte).

---

## 2026-11 — Fáza 5 reálny test: F5-A oprava mapy

- **Problém:** Po scrape 4734 pozemkov mala mapa **0 bodov**. Nominatim geokódovanie
  beží až počas plného GIS scoringu (ručne, max 10-20 pozemkov), preto 99% ostávalo bez GPS.
- **Oprava:** Nová funkcia `_enrich_coords_offline()` v `scraper_service.py` — po scrape
  dopĺňa GPS z offline databázy `sk_places` (GeoNames ~8300 slovenských obcí, 0 HTTP).
  Pokrytie: **94.8%** (4488/4734 pozemkov dostane obec-level GPS ~2-5 km presnosť).
- **Retro-aplikácia:** `scrape_routes._enrich_from_db()` dopĺňa GPS aj pre staršie DB
  záznamy — mapa funguje okamžite aj bez nového scrape behu.
- Presnejšie GPS (ulica) zostáva v Nominatim cez `geocoding_service` pri GIS scoringu.
- +5 testov v `TestEnrichCoordsOffline` (mix s/bez GPS, neznáma obec, batch)
- **Celkový počet testov: 1642** (+5)

## 2026-11 — Pyright cleanup: 0 unused importov

- VS Code Problems panel bol znečistený **41 warningami** typu `reportUnusedImport`.
- Vyčistené v **18 súboroch**: 2 backend (`pipeline_service.py`, `scoring_service.py`)
  a 16 test-ov. Odstránené importy ktoré sa nikde nepoužívali
  (`json`, `MagicMock`, `tempfile`, `_dist_km`, `SEARCH_URLS`, ...).
- Zachované: `SOURCE_NAME` v `test_topreality_scraper.py` (používa sa na riadku 253),
  `pytest` v `test_terrain_service.py` (používa sa pre `pytest.approx` na riadku 171).
- Testy: 1642 zelených (bez zmien v počte).
- VS Code Problems: **0 warningov** v Pyright basic mode.

## 2026-11 — Modernizácia farebnej palety

- **Prechod zo starých tlmených farieb na moderný Tailwind-inspired palette** (`emerald/amber/orange/red`-500):
  - SILNÁ KÚPA: `#2d7a2d` → `#10b981` (emerald, svieža zelená)
  - PREVERIŤ: `#c8a000` → `#f59e0b` (amber, jantárová)
  - ZVÁŽIŤ: `#c85a00` → `#f97316` (orange, živá)
  - PRESKOČIŤ: `#a02020` → `#ef4444` (red, čistá)
- **Prelim stlmené verzie** zjemnené na pastely (emerald-300 / amber-300 / orange-300 / slate-300)
  s tmavým textom pre dobrý kontrast
- **Status badges + flags + buttons** v `style.css` tiež modernizované (emerald + red paleta)
- **Geolokácia warning** v `map.js` zjednotený na amber-600
- README sekcia 3 — tabuľka farieb aktualizovaná
- Verzie static súborov `v=38→39` (vynútenie cache invalidation)

## 2026-11 — UX polish po reálnom teste (Fáza 5)

- **Legenda v mape rozšírená**: nová sekcia **🏆 Investičný index (0–100)** nad GIS skóre + horný hint box
  vysvetľujúci rozdiel *Index = investičný potenciál* vs *Skóre = fyzická kvalita pozemku*
- **Tooltipy v hlavičke tabuľky prepísané** (`<th>` title) — kratšie, s rozlíšením čo meria Index a čo Skóre;
  pri Skóre pridaný návod ako sa z Prelim stane Plné GIS
- **Zjednotené farby pre 70–84 (PREVERIŤ)**: `#1565c0` modrá → `#c8a000` žltá všade
  (`_scoreColor`, `_recStyle`, `_prelimMapColor`) — teraz legenda, mapa, tabuľkové body a modal badge
  ukazujú tú istú farbu
- **README sekcia 3 "Skóre a farby"**: pridané vysvetlenie rozdielu Index vs Skóre tabuľkou na vrchu,
  PREVERIŤ farba opravená z *modrá* na *žltá* (realita)
- **Verzie static súborov zvýšené** (`v=37→38`, `v=1→2`) — prehliadač sa vyhne cache

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
  - Toggle tlačidlo `💬 AI asistent` **vpravo hore** pod headerom (`top: 62px; right: 20px`)
  - Resizable panel: drag za **pravý-dolný roh** (min 300×400, max 800×90vh)
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

## 2026-11 — UI opravy po reálnom teste

- **AI toggle pozícia**: presunutý z pravého dolného rohu (`bottom: 20px`) do pravého horného rohu
  (`top: 62px`) — eliminuje prekrývanie s legendou mapy
- **AI toggle zarovnanie**: toggle presunutý priamo do `<header>` ako flex item — zarovnaný
  vertikálne s názvom appky, biele priesvitné pozadie (rgba) na modrom header pozadí, žiadne
  magic `top:` čísla

## 2026-11 — Vlna C: Security + Token efficiency + opravy

### Security
- **S1 — Model whitelist** (`select-model`): model musí byť v zozname z `available-models` —
  zabraňuje volaniu nepovolených/drahých modelov
- **S2 — Export realpath guard**: dvojitá ochrana voči path traversal aj cez symlinky
  (`Path.resolve()` check že súbor je v `data/exports/`)
- **S4 — Rate limit 10 req/min** pre `POST /api/agent/ask` per IP (sliding window, in-memory)
- **S5 — Session cookie hardening**: `HttpOnly=True`, `SameSite=Lax`

### Token efficiency
- **T1 — System prompt 400→150 tokenov**: skrátený na esenciu, zachováva všetky pravidlá
- **T2 — Tool outputy**: `get_parcels` vracia len 8 kľúčov (`url/loc/price/area/ppsm/index/src/sigs`)
  namiesto 9 plných polí; default `limit: 20→10`
- **T3 — 5-min TTL cache** pre identické otázky: `hashlib.md5(model+question)` →
  instant odpoveď bez Gemini volania
- **T4 — `max_output_tokens: 2048→800`**: stačí pre chat odpovede
- **T5 — `tokens_used`** v response: `{in, out, total}` z `usage_metadata` (debug/UX)

### Bug opravy (Vlna C)
- **#1 — `_classify_error` 503→quota**: `503 UNAVAILABLE` od Google = rate limit/overload,
  správne klasifikované ako `quota` (nie `network`) — používateľ dostane *"Skús o 1 minútu"*
  namiesto *"problém so sieťou"*
- **#2 — Retry s backoff**: pri `quota` čaká 5s a skúsi znova pred prechodom na fallback model
- **#5 — JS timeout 60s**: `AbortController` + SK chybová správa *"AI neodpovedá (timeout 60s)"*
- **#6 — Tool chip tooltip**: čitateľný formát `obec=Senec, limit=10` namiesto `JSON.stringify`
- **#7 — Dead import**: `from google import genai as _genai` v `_run_agent` odstránený

### Testy
- `TestClassifyError`: +3 testy (503/unavailable→quota, dns→network)
- `TestSecurity`: +5 testov (rate limit ok/block/429, whitelist reject/allow)
- `TestTokenEfficiency`: +3 testy (default limit, cache hit/miss)
- **Celkový počet testov: 1635** (+11), všetky zelené

## 2026-11 — Vlna C.1: Pyright cleanup + polish + regression fix

### Pyright "Problems" — unused imports vyčistené (VS Code žlté warningy)
- `app.py` — `send_from_directory`
- `models/result.py` — `Any`
- `routes/backup_routes.py` — `Response`, `_LATEST_FILE`
- `routes/monitor_routes.py` — `is_feature_enabled`
- `routes/scrape_routes.py` — `merge_signals`
- `services/monitor_service.py` — `field`
- `services/overpass_service.py` — `get_endpoints`
- `services/protected_service.py` — `get_criteria_section`
- `services/zbgis_service.py` — `math`
- `services/scraper_service.py` — `print` → `logger` (posledné 2 ostávajúce print-y)

### P0: Kritické opravy
- **P0-1 — Persistent SECRET_KEY**: generuje sa raz do `data/.secret_key` (gitignored) —
  každý reštart appky prestane invalidovať Flask session (model override sa zachová)
- **P0-2 — `except: pass` → `logger.warning`** v `scrape_routes._run()` —
  tichá degradácia pri preliminary_score sa teraz loguje

### P1: Regression fix
- **P1-4 — CSV export broken fieldnames**: `_tool_export_csv_filtered` používal staré
  dlhé kľúče (`location_text`, `investment_index`, ...) namiesto T2 krátkych (`loc`, `index`, ...) —
  CSV bol prázdny (len header). Opravené + test overujúci obsah stĺpcov

### P2: Polish
- **P2-3 — `MAX_AGENT_ROUNDS = 5`**: magic number v `_run_agent` nahradený konštantou
- **`_NO_DISTANCE_LIMIT = 999`**: sentinel pre "bez limitu vzdialenosti"

### Testy
- +2 testy: CSV správne stĺpce, MAX_AGENT_ROUNDS existuje
- **Celkový počet testov: 1637** (+2), všetky zelené


- **AI modal picker scroll**: `#ai-model-modal-box` dostal `max-height: 85vh` + `display: flex; flex-direction: column`;
  zoznam modelov (`.ai-model-modal-body`) má `overflow-y: auto; flex: 1` — header a footer sú vždy
  viditeľné, dlhý zoznam modelov od Google API scrolluje vnútri


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
