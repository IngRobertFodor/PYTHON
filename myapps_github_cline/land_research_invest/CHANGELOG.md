# Changelog

Míľniky projektu. Pre podrobný wave-by-wave log pozri `git log`.

---

## 2026-10 — Q-fixes a OV parser

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
