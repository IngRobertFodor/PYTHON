# Audit Report — 2026-11-03

> Pracovný dokument. Po review a commite zmazať.
> **Stav 2026-11-03:** P0/P1 opravené, P2 testy hotové, C1 AI backend hotový.
> **Stav 2026-11 (hotfix):** opravená rozbitá štruktúra `_renderDiffBanner` v `app.js`
> + krížik v legende prerobený na minimalizačné tlačidlo. Detaily nižšie.

---

## ✅ OPRAVENÉ 2026-11 (hotfix frontend)

### `#diff-banner` stráca CSS triedu `diff-banner` (prienik 3 nezávislých prieskumov)

**Symptóm:** CSS pravidlá pre `.diff-banner` (modré pozadie, border,
padding, flex layout) sa neaplikovali na wrapper nad diff chipmi
„✨ N nových / 📉 N zlacneli / 🗑️ N zmizlo / N nezmenených".
Chipy samy mali vlastné pozadie, ale wrapper box okolo nich chýbal.

**Metóda nálezu:** Po predošlých jednoduchších opravách som urobil
**3 nezávislé prieskumy** s rôznym zameraním a opravujem len to, čo
sa objavilo v ich **priesniku** (z ~15 individuálnych nálezov prešiel
do prieniku len tento jeden).

**Príčina:** HTML `<div id="diff-banner" class="hidden"></div>` nemalo
základnú CSS triedu `diff-banner`. Zároveň v CSS chýbal selektor
`.diff-banner.hidden` (ostatné `.hidden` boli vždy definované
per-selektor).

**Oprava:**
1. HTML (`index.html` r.95): `class="diff-banner hidden"`
2. CSS (`style.css` r.507): `.diff-banner.hidden { display: none; }`

Cache-bust `?v=46` → `?v=47`.

### Rozbitá CSS štruktúra v `style.css` okolo `.up-checklist li` + `.backup-*`

**Symptóm:** Sekcia *„Záloha histórie prieskumov"* v sidebar panely vyzerala
neštýlovaná — holý text namiesto krajného boxu s pozadím, borderom a
flex-labelmi.

**Príčina:** Blok `.up-checklist li { ... }` nebol uzavretý pred komentárom
`/* BACKUP PANEL */` a všetky `.backup-status-info`, `.backup-row`,
`.backup-info-loading` pravidlá sa parsovali ako **nested selektory**
vo vnútri `.up-checklist li`. Štandardný CSS (bez CSS Nesting) ich
ignoruje. Zátvorky boli matematicky v balance (222 `{` = 222 `}`),
takže tichá chyba.

Zároveň `.up-checklist li` strácal `font-size: .74rem` (sirota deklarácia).

**Oprava:** Pre-usporiadanie pravidiel — `.up-checklist li` správne
uzavreté, `.backup-*` presunuté na top-level za `.up-cl-hint`.
Cache-bust `?v=45` → `?v=46`.

### Mobile media query ignorovala `.sidebar-splitter`

Na obrazovkách `≤ 768px` ostával drag-splitter viditeľný ako artefakt
cez celú výšku. Pridané `.sidebar-splitter { display: none }` a
`.sidebar, .map-panel { grid-row: auto }` v media query.

### Duplicitné 🔴 bodky pri rizikových vlajočkách

**Symptóm:** V tabuľke pri niektorých pozemkoch dve červené bodky 🔴🔴 vedľa seba
(napr. riadok 3878 — `PODIEL?` vlajka + `Lacný −57 % (háčik?)` vlajka + dve bodky).

**Príčina:** V `app.js` r.1094 chýbal filter `!FLAG_KODY.has(s.kod)` v rozklade
`riskSigs` — rovnaký filter bol pri `oppSigs` (r.1093) na príležitostné signály,
ale pri rizikových sa nedoplnil. Výsledok: každé riziko s vlastnou vlajkou (chip)
sa zobrazilo aj ako samostatná 🔴 bodka.

**Oprava:** Doplnený filter → `riskSigs = sigs.filter(s => s.typ === "RIZIKO"
&& !FLAG_KODY.has(s.kod))`. Cache-bust `?v=44` → `?v=45`.

### Rozbitá štruktúra `_renderDiffBanner()` v `app.js`

**Symptóm:** Krížik v legende v mape (vpravo hore) sa nedal kliknúť — nič sa nedialo.
Rovnako nefungovalo tlačidlo „📤 Stiahnuť zálohu", „📥 Obnoviť zo súboru"
a status zálohy sa nenačítal pri otvorení sekcie.

**Príčina:** Chýbajúca `}` za telom `_renderDiffBanner()` okolo r.1505. Všetky
nasledujúce top-level funkcie (`_loadBackupStatus`, `onBackupExport`,
`onBackupImport`, DOMContentLoaded-handler, `toggleLegend`) sa tým stali
**nested function declarations** v scope `_renderDiffBanner` → neviditeľné
pre `onclick="…"` inline handlery v HTML → `ReferenceError` pri behu.

**Nebezpečné na odhalenie:** `node --check` ani static analyzer nepísali
syntaktickú chybu (JS je formálne platný). Prejavilo sa to iba v runtime,
a pretože toggleLegend je „nice-to-have" a backup používatelia nevyužívajú
denne, chyba pretrvávala aj v produkčnom stave.

**Oprava v jednom commite:**
1. Pridaná uzatváracia `}` + blok `banner.querySelectorAll(".diff-chip[data-filter]")`
   presunutý **dovnútra** `_renderDiffBanner` (pred jej koniec).
2. Odstránený osirotený duplicitný blok + prebytočný `}` za `toggleLegend`.
3. Cache-bust `?v=43` → `?v=44` (inak prehliadač ostane na starej JS kópii).

### UX: krížik v legende → minimalizačné tlačidlo (▴/▾)
- Sémanticky správne — nie je to „close for ever", je to „minimize/expand".
- Pridané `aria-label`, `aria-expanded`, `type="button"` pre screen readery
  a prístupnosť.
- CSS `.legend-toggle` — pill vzhľad: sivé pozadie + border + hover + focus-visible.
- Logika v `toggleLegend()`: ▴ (rozbalená) kliknutím zbalí → šípka sa zmení
  na ▾; rovnako aktualizuje `aria-expanded` z `"true"` → `"false"`.

---

## ✅ OPRAVENÉ (P0/P1 — inline fixné)

### P1 — `print()` v produkčnom kóde → `logging`

Všetky `print(f"[modul] ...")` v serverovom kóde nahradené za `logging.getLogger(__name__)`.

Dotknuté súbory (12):
- `services/scrapers/base_scraper.py`
- `services/scraper_service.py`
- `services/scoring_service.py`
- `routes/scrape_routes.py`
- `services/scrapers/nehnutelnosti_scraper.py`
- `services/scrapers/topreality_scraper.py`
- `services/scrapers/notarske_drazby_scraper.py`
- `services/scrapers/ske_scraper.py`
- `services/scrapers/spf_scraper.py`
- `services/scrapers/obchodny_vestnik_scraper.py`
- `services/url_fetch_service.py`
- `services/signals.py`

Úrovne: `WARNING` (recoverable errors), `INFO` (diagnostika), `DEBUG` (parsing detaily).
`print()` zostali úmyselne iba v `data/analyza_scoring.py` a `data/build_obce_sk.py`
(standalone CLI skripty, nie serverový kód — tam sú `print()` správne).

### P1 — `except Exception: pass` bez logu → `logger.debug()`

- `services/signals.py:98` — BLIZKO_BA výpočet: doplnený `logger.debug`

Zostatok `except Exception: pass` (terrain_service, zbgis_service):
- `terrain_service.py:239,258,277` — JSON/text parsing fallbacky → ponechaný `pass` je tu úmyselný
  (WMS API vracia rôzne formáty, parser skúša viac formátov; `pass` = "skús ďalší formát")
- `zbgis_service.py:200,262` — WFS response parsing → rovnaký prípad

Tieto `pass` sú **správne** — nie sú silent failures, ale multi-format fallback logikou.

---

## 📋 NÁVRHY (P2/P3 — na odsúhlasenie)

### P2 — Chýbajúce testy pre routes

Chýbajú dedikované test súbory pre:
- `routes/backup_routes.py` — nie je `test_backup_routes.py` (backup_service má testy, routes nie)
- `routes/config_routes.py` — nie je `test_config_routes.py` (config_validator má testy)
- `routes/health_routes.py` — triviálne, nízka priorita
- `routes/monitor_routes.py` — triviálne, nízka priorita
- `routes/parcel_routes.py` — nie je `test_parcel_routes.py` (pipeline_service má testy)

**Reálny dopad:** `test_scrape_routes.py` a `test_app.py` pokrývajú hlavné routes cez Flask test client. Chýbajúce sú len okrajové cases (error handling, edge cases pre backup a parcel routes).

**Odporúčanie:** Pridať do existujúcich `test_app.py` alebo `test_scrape_routes.py` — nie nové súbory.

### P2 — `pipeline_service.py` komentár nesedí s kódom

```python
# Tok (podla ARCHITEKTURA_DEVELOPER.txt sekcia 3)
```
`ARCHITEKTURA_DEVELOPER.txt` bol zmazaný (nahradený `ARCHITEKTURA.md` v commite `3c8e95f`).
→ Opraviť komentár na `ARCHITEKTURA.md sekcia 3`.

### P2 — `config_loader.py` — globálna cache bez thread-safe invalidácie

`_config_cache` je globálna premenná. `save_config()` volá `reload_config()` čo nastaví `_config_cache = None`.
V multi-threaded prostredi (Flask + ThreadPoolExecutor) môže race condition spôsobiť, že 2 vlákna
simultánne načítajú YAML. Funkčné, ale nie thread-safe.

→ Nízka priorita (single-user lokálny nástroj, config sa mení zriedka).

### P2 — `nehnutelnosti_scraper.py` — bare `except Exception: pass` na riadku ~404

`_extract_location()` má `except Exception: pass` pred fallbackom na zátvorkový guard.
Bez logu — pri neočakávanej chybe tichá degradácia.
→ Nahradiť za `except Exception: logger.debug(...)`.

### P3 — `pipeline_service.py` — ZBGIS berie feature flag `use_distance`

```python
("use_distance",   # ZBGIS berie ak mame suradnice
 "zbgis_service",
```
ZBGIS sa spúšťa len ak `use_distance=True` (predpokladá GPS súradnice). To je správne, ale komentár
navodzuje dojem, že by mal mať vlastný flag `use_zbgis`. Aktuálne funguje dobre.

### P3 — `backup_service.py` — `_merge()` má bare `except Exception: src_runs = []`

```python
try:
    src_runs = src.execute("SELECT * FROM runs").fetchall()
except Exception:
    src_runs = []
```
Bez logu — pri korumpovanom backupe tichá degradácia. Nízka priorita (validácia pred volaním).

### P3 — `data/analyza_scoring.py` — top-level kód pri importe

Súbor spúšťa SQL dotazy na globálnej úrovni (mimo `if __name__ == "__main__"`).
Pri importe kdekoľvek by sa spustil. Nie je importovaný nikde v projekte, len CLI nástroj.
→ Zabaliť do `if __name__ == "__main__":`.

### P3 — `ARCHITEKTURA.md` — endpoint `/api/scrape/results.csv` chýba v REST tabuľke

V `README.md` je `GET /api/scrape/results.csv` uvedený.
V `ARCHITEKTURA.md` sekcia 8 táto cesta chýba.
→ Doplniť.

---

## 📊 Coverage mapa (testy vs. služby)

Pokryté testami (40 súborov):
- Všetky core services: scoring, signals, opportunity, peer, pipeline, storage, backup...
- Všetky scrapery (7/7)
- Routes: scrape_routes, app

**Bez priameho testu** (netestované samostatne, pokryté nepriamo cez test_app / test_scrape_routes):
- `routes/backup_routes.py` — `test_backup_service.py` testuje service, nie HTTP vrstvu
- `routes/config_routes.py` — `test_config_validator.py` testuje validáciu, nie HTTP
- `routes/parcel_routes.py` — `test_pipeline_service.py` testuje pipeline, nie HTTP
- `routes/health_routes.py` — triviálne 1 riadok
- `routes/monitor_routes.py` — triviálne

---

## Zhrnutie

| Kategória | Počet | Stav |
|---|---|---|
| P0 — kritické | 0 | ✅ žiadne |
| P1 — opravené inline | 2 | ✅ hotovo |
| P2 — návrhy na odsúhlasenie | 5 | 📋 viď vyššie |
| P3 — nice-to-have | 5 | 📋 viď vyššie |
| Testy | 1546 / 1546 ✅ | zelené |
| Bezpečnosť | OK | SSRF guard, CORS, debug=False |

---

> Po review: zmazať tento súbor. Zistenia sú v CHANGELOG.md + priamo v kóde.
