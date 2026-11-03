# Audit Report — 2026-11-03

> Pracovný dokument. Po review a commite zmazať.

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
