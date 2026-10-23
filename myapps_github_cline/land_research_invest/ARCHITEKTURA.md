# Architektúra — technická dokumentácia

Pre vývojárov a AI agentov.

---

## 1. Technologický stack

| Komponent | Technológia |
|---|---|
| Backend | Python Flask |
| Frontend | HTML5 + CSS3 + Vanilla JS |
| Mapa | Leaflet.js + OpenStreetMap |
| Scraping | requests + BeautifulSoup + pypdf |
| Kataster / geometria | ZBGIS WFS (UGKK) |
| Záplavy Q100 | SHMU WMS |
| Terén / výškopis | DMR 5.0 (UGKK) + SRTM (Copernicus) |
| Bonita pôdy | geodata.gov.sk WMS |
| Infraštruktúra | Overpass API (OpenStreetMap) |
| Geokódovanie | Nominatim (OpenStreetMap) |
| GIS spracovanie | geopandas, shapely, pyproj, owslib |
| Databáza | SQLite (via storage_service) |
| Plánovanie | APScheduler |
| Notifikácie | python-telegram-bot / SMTP |
| AI agent (voliteľné) | LangChain + Google Gemini |

---

## 2. Vrstvy systému

```
+----------------------------------------------------------+
|  AI ORCHESTRATOR  (llm_agent_service) [PLÁNOVANÉ]        |
+------------------+---------------------------------------+
                   | volá nástroje (@tool)
     +-------------+----------+---------------+
     v             v          v               v
  [Scrapery]  [GIS validátory] [Pipeline]  [Scoring/Report]
  7 zdrojov:  zbgis/flood/     pipeline_   scoring_service
  nehnut.sk   terrain/bpej/    service     preliminary_score
  topreality  overpass/protect (orchestr.) report_service
  reality_sk  geocoding                    cadastral_service
  spf/ske/notar/OV
```

---

## 3. Tok dát — dvojfázový scoring

### Fáza 1: Scraping + predbežné skóre (0 HTTP, okamžite)

1. `scraper_service.scrape_all()` — 7 zdrojov paralelne (ThreadPoolExecutor)
2. Dedup podľa `(url + parcel_number)`
3. `scoring_service.preliminary_score()` — price(30%) + area(25%) + ppsm(20%) + dist(10%) + source(10%)
   - Chýbajúci údaj = komponent vynechaný, nie penalizácia
4. `signals.preliminary_signals()` — investičné signály bez HTTP
5. `storage_service.save_run()` → SQLite
6. `signals.history_signals()` + `peer_analysis_service.apply_peer_signals()` + `opportunity_service.apply_opportunity()`

### Fáza 2: GIS scoring (na požiadanie, ~20 s/pozemok)

1. `pipeline_service.analyze_parcel()` — orchestrátor
2. 8 GIS služieb paralelne: flood, terrain, bpej, overpass, protected, zbgis, geocoding, price_analysis
3. `scoring_service.score_parcel()` — vážené GIS skóre (0–100)
4. `signals.gis_signals()` — PREKLASIFIKACIA, LACNE_VYNATIE, DRAHE_VYNATIE
5. `rezoning_service.estimate_rezoning_profit()` — ak `is_agricultural == True`
6. `storage_service.patch_parcel()` → aktualizácia DB

### `_enrich_from_db`

Pri každom načítaní DB záznamu sa vždy prepočíta `investment_index`
a spustí `apply_peer_signals()` + `apply_opportunity()` — fixuje stale index=0.

---

## 4. Zoznam služieb

| Súbor | Čo robí |
|---|---|
| `pipeline_service.py` | orchestrátor GIS analýzy |
| `scoring_service.py` | GIS skóre (0–100) + `preliminary_score()` |
| `signals.py` | všetky investičné signály (pozri sekciu 6) |
| `opportunity_service.py` | `investment_index()` (0–100) + `explain()` |
| `peer_analysis_service.py` | LACNEJSI_AKO_OKOLIE peer comparison v rámci obce |
| `rezoning_service.py` | odhad zisku z preklasifikácie |
| `report_service.py` | investičný report |
| `cadastral_service.py` | LV checklist + `evaluate_lv_data()` |
| `distance_service.py` | Haversine + WGS84/JTSK konverzia |
| `flood_service.py` | SHMU WMS Q100 |
| `terrain_service.py` | sklon, zosuvy, radón |
| `bpej_service.py` | bonita pôdy, odvody |
| `overpass_service.py` | OSM cesta/elektrina/voda, classify_access/position |
| `protected_service.py` | VVN/VTL, Natura 2000, CHKO |
| `zbgis_service.py` | ZBGIS WFS geometria, druh pozemku z KN |
| `geocoding_service.py` | Nominatim adresa → GPS |
| `price_analysis_service.py` | EUR/m² vs. regionálny priemer |
| `storage_service.py` | SQLite (save_run/patch_parcel/load/list_runs) |
| `diff_service.py` | nové/zlacneli/zmizli/still_here |
| `uzemny_plan_service.py` | UP asistent (gisplan.sk + fallback + checklist) |
| `backup_service.py` | gzipped SQL dump + merge import + rotácia (max 20) |
| `sk_places.py` | GeoNames SK (~8300 obcí) — vzdialenosť offline |
| `scraper_service.py` | orchestrátor scraperov (paralelne, dedup, progress) |
| `notifier_service.py` | Telegram / email notifikácie |
| `monitor_service.py` | APScheduler periodický scan |
| `scrapers/nehnutelnosti_scraper.py` | JSON-LD parser (slug ≥ 4 znaky) |
| `scrapers/topreality_scraper.py` | JSON-LD detail parser |
| `scrapers/reality_sk_scraper.py` | div.offer CSS parser |
| `scrapers/spf_scraper.py` | PDF parser + filter 70 km |
| `scrapers/ske_scraper.py` | SKE exekútorské dražby |
| `scrapers/notarske_drazby_scraper.py` | notar.sk PDF dražby |

---

## 5. Databáza — SQLite schéma (kľúčové stĺpce)

```
parcels
  url, parcel_number, title, price_eur, area_sqm, location_text, source
  first_seen              -- B1: dátum prvého výskytu
  price_history           -- B1: JSON [{date, price}, ...]
  vyvolavacia_cena_eur    -- B2: dražobná vyvolávacia cena
  znalecka_hodnota_eur    -- B2: znalecká hodnota
  drazba_kolo             -- B2: kolo dražby (≥2 = opakovaná)
  peer_median_ppsm        -- B3: mediánové EUR/m² v obci
  peer_count              -- B3: počet porovnaných pozemkov v obci
  signals_json            -- JSON všetkých signálov
  investment_index        -- B4: 0–100
  invest_summary          -- B4: textové zdôvodnenie (2–4 vety)
  preliminary_score, prelim_confidence, prelim_recommendation
  prelim_breakdown        -- JSON rozpad predbežného skóre
  final_score, recommendation
  run_id, scraped_at
```

---

## 6. Investičné signály

### Predbežné (`preliminary_signals`, 0 HTTP)

| Signál | Podmienka |
|---|---|
| BLIZKO_BA | odhad km < 25 |
| PRILIS_DALEKO | odhad km > 82 |
| CENA_PODOZRIVA | inzerát + ppsm < 1.5 EUR/m² |
| DRAZBA_PODHODNOTENA | dražobný zdroj + cena v rozsahu |
| PODIEL_ALEBO_CHYBNE_DATA | area_sqm < 100 alebo (price < 500 + area < 50) → cap indexu na 30 |

### Historické (z DB, po `save_run`)

| Signál | Podmienka |
|---|---|
| DLHO_V_PONUKE | inzerát > 120 dní |
| CENA_KLESA | pokles ceny ≥ 5 % od prvej hodnoty |
| HORICE | DLHO_V_PONUKE + CENA_KLESA + vek ≥ 180 dní |

### Dražobné (B2)

| Signál | Podmienka |
|---|---|
| DRAZBA_POD_ZNALECKOU | vyvolávacia ≥ 20 % pod znaleckou |
| DRAZBA_OPAKOVANA | kolo ≥ 2 |

### Peer comparison (B3)

| Signál | Podmienka |
|---|---|
| LACNEJSI_AKO_OKOLIE | ppsm < 60 % mediánu obce (min. 4 pozemky) |

### GIS signály

| Signál | Podmienka |
|---|---|
| PREKLASIFIKACIA | is_agricultural + OKRAJ + {PRIAMA\|CIASTOCNA} + bpej ≥ 5 |
| LACNE_VYNATIE | is_agricultural + bpej ≥ 7 (odvody ≤ 0.10 EUR/m²) |
| DRAHE_VYNATIE | is_agricultural + bpej ≤ 4 (odvody ≥ 3 EUR/m²) |

---

## 7. Investičný index — vzorec

```
investment_index = rezoning_pts(0–35)
                 + misprint_pts(0–35)
                 + confidence_pts(0–15)
                 - risk_penalty(max 25)

Cap: ak PODIEL_ALEBO_CHYBNE_DATA → max 30

rezoning_pts:   log rast so ziskom (10k€→10b, 50k€→24b, 300k€→35b)
misprint_pts:   HORICE(1.0) > DRAZBA_POD_ZNALECKOU(0.9) > LACNEJSI_AKO_OKOLIE(0.75) > ...
confidence_pts: prelim_confidence × 15
risk_penalty:   ZAPLAVA(-20), CHRANENE(-15), DRAHE_VYNATIE(-12), PODIEL(-25)

Váhy konfigurovateľné: criteria.yaml → sekcia opportunity
```

---

## 8. REST endpointy

| Metóda | Cesta | Popis |
|---|---|---|
| GET | /api/health | health check |
| GET | /api/config/ | aktuálna konfigurácia |
| POST | /api/scrape/start | spustí scraping + predbežné skóre |
| GET | /api/scrape/progress | priebeh scraping |
| GET | /api/scrape/results | výsledky posledného behu |
| POST | /api/scrape/score-selected | GIS scoring pre vybrané pozemky |
| GET | /api/scrape/score-progress | priebeh GIS scoringu |
| GET | /api/scrape/results.csv | export CSV |
| GET | /api/scrape/diff | nové/zlacneli/zmizli vs. predchádzajúci beh |
| GET | /api/scrape/runs | história behov |
| GET | /api/scrape/up-links | UP asistent (?location=\<obec\>) |
| GET | /api/scrape/up-coverage | pokrytie gisplan.sk z cache |
| GET | /api/backup/status | stav zálohy |
| GET | /api/backup/export | stiahnuť zálohu |
| POST | /api/backup/import | obnoviť zo zálohy |
| GET | /api/backup/history | rotované zálohy |
| POST | /api/analyze | GIS analýza jednej parcely |
| POST | /api/parcels/analyze-batch | GIS analýza dávky |

---

## 9. Premenné prostredia (.env)

| Premenná | Default | Popis |
|---|---|---|
| `FLASK_DEBUG` | `false` | Nikdy `true` v produkcii |
| `HOST` | `127.0.0.1` | `0.0.0.0` pre sieťový prístup |
| `PORT` | `5001` | Port Flask servera |
| `CORS_ORIGINS` | `http://localhost:5001,...` | Povolené CORS origins |
| `GOOGLE_API_KEY` | — | Gemini AI (voliteľné) |

---

## 10. Fixovanie bežných problémov

| Problém | Ako opraviť |
|---|---|
| Testy padajú | `python -m pytest tests/ -v --tb=long` |
| Scraper vracia 0 výsledkov | Skontrolovať `per_source_status` v `/api/scrape/results` |
| SSRF chyba | `url_fetch_service.py` → rozšíriť allowlist v `_detect_portal` |
| Index=0 pri starých záznamoch | `_enrich_from_db` prepočíta pri ďalšom `/api/scrape/results` |
| OV parser nerozpozná PDF | Log — 3 extraktory: `_try_vertical_form`, `_try_flow_text`, `_try_specifikacia` |
| Záloha neuložila | Skontrolovať práva na `data/backups/` |
| Chybný YAML | `python -c "import yaml; yaml.safe_load(open('config/criteria.yaml'))"` |

---

## 11. Testovanie

```bash
python -m pytest tests/ -q              # 1546 testov, ~55 s
python -m pytest tests/ -v --tb=short
python -m pytest tests/test_signals.py tests/test_opportunity_service.py -v
python -m pytest tests/test_backup_service.py -v
python -m pytest tests/test_obchodny_vestnik_scraper.py -v
```

Fixtures: `tests/fixtures/` — PDF vzorky OV, `ov_expected.json`.

---

Autor: Robert Fodor | 2026

