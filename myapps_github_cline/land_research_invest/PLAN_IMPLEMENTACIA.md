# Implementacny plan - Land Research Invest

> **Living dokument** - aktualizuje sa po kazdom krokovani (checkboxy).
> Posledna aktualizacia: pozri git commit alebo datum zmeny suboru.

---

## Stav projektu

| Oblast | Stav |
|--------|------|
| Backend sluzby (GIS, scoring, report, pipeline, notifier, API) | HOTOVO |
| Frontend (mapa, karty, modal, demo) | HOTOVO |
| Scraper kostra (BaseScraper, registry, scrape_all) | HOTOVO |
| nehnutelnosti_sk parser | HOTOVO |
| Testy | **679, 0 zlyh** |

---

## FAZA A - Periodicky scan (monitor_service)

**Ciel:** APScheduler automaticky spusta scrape_all -> analyze_parcel -> notify_parcel

- [x] A1: Config sekcia `monitoring` (interval_minutes, max_parcels_per_scan)
- [x] A2: `config_loader.get_monitoring()`
- [x] A3: `backend/services/monitor_service.py`
  - `ScanResult` dataclass (scanned, notified, errors, duration_s, timestamp)
  - `start(provider=None)` - spusti APScheduler BackgroundScheduler
  - `stop()` - zastavi scheduler
  - `run_scan()` - jeden scan: scrape_all -> analyze -> notify
  - `get_status()` - running, next_run, last_scan_time, last_scan_count
- [x] A4: Flask endpointy
  - `GET  /api/monitor/status`
  - `POST /api/monitor/scan` (manualny trigger)
- [x] A5: `tests/test_monitor_service.py` (~25 testov)
- [x] A6:
- [x] B1: topreality_sk scraper (JSON-LD + data-price + BreadcrumbList) Aktualizacia dokumentacie (PLAN + 4 docs)

**Vysledok B1:** `pytest` = 679, 0 zlyh -- SPLNENE

---

## FAZA B - Scrapery (9 zdrojov, postupne)

> Kazda faza: 1 scraper + fixture HTML (od teba) + testy
> `SCRAPER_REGISTRY` = 1 riadok zmena, `scrape_all()` sa NEMENI

### B1 - topreality_sk

**Typ:** realitny portal (podobna struktura ako nehnutelnosti.sk)
**URL:** https://www.topreality.sk
**Rate:** 10/min | **Zone:** GREEN

- [ ] B1.1: HTML vzorka od pouzivatela -> `tests/fixtures/topreality_listing.html`
- [ ] B1.2: `backend/services/scrapers/topreality_scraper.py`
- [ ] B1.3: Pridat do `SCRAPER_REGISTRY`
- [ ] B1.4: `tests/test_topreality_scraper.py` (~15 testov)
- [ ] B1.5: Aktualizacia dokumentacie

### B2 - obchodny_vestnik (**ZLATO** - konkurzy/drazby)

**Typ:** oficialny register konkurzov, drazob, likvidacii
**URL:** https://www.justice.gov.sk/PortalApp/ObchodnyVestnik
**Rate:** 10/min | **Zone:** GREEN
**Poznamka:** Najlepsie podhodnotene pozemky!

- [ ] B2.1: HTML vzorka od pouzivatela -> `tests/fixtures/obchodny_vestnik_listing.html`
- [ ] B2.2: `backend/services/scrapers/obchodny_vestnik_scraper.py`
- [ ] B2.3: Pridat do `SCRAPER_REGISTRY`
- [ ] B2.4: `tests/test_obchodny_vestnik_scraper.py` (~15 testov)
- [ ] B2.5: Aktualizacia dokumentacie

### B3 - spf (Slovensky pozemkovy fond)

**Typ:** verejne obchodne sutaze - statne pozemky
**URL:** https://www.pozemkovyfond.sk
**Rate:** 10/min | **Zone:** GREEN

- [ ] B3.1: HTML vzorka -> `tests/fixtures/spf_listing.html`
- [ ] B3.2: `backend/services/scrapers/spf_scraper.py`
- [ ] B3.3: Pridat do `SCRAPER_REGISTRY`
- [ ] B3.4: `tests/test_spf_scraper.py` (~15 testov)
- [ ] B3.5: Aktualizacia dokumentacie

### B4 - exekutorske_drazby + drazby_net

**Typ:** drazby zabavenych pozemkov (pod trhovym cenam)
**URL:** sexe.sk / drazby.net
**Rate:** 10/min | **Zone:** GREEN
**Poznamka:** Drazby_net je agregator - moze pokryvat aj exekutorske

- [ ] B4.1: HTML vzorky -> `tests/fixtures/exekutorske_listing.html`, `drazby_net_listing.html`
- [ ] B4.2: `backend/services/scrapers/exekutorske_drazby_scraper.py`
- [ ] B4.3: `backend/services/scrapers/drazby_net_scraper.py`
- [ ] B4.4: Pridat do `SCRAPER_REGISTRY` (2 zaznamy)
- [ ] B4.5: Testy (~20 testov)
- [ ] B4.6: Aktualizacia dokumentacie

### B5 - notarske_drazby + eks_statny_majetok

**Typ:** notarske drazby + elektronicke aukcie statu
**URL:** notar.sk/drazby / eks.sk
**Rate:** 10/min | **Zone:** GREEN
**Poznamka:** EKS = aukcie statnych organizacii a samosprav

- [ ] B5.1: HTML vzorky -> `tests/fixtures/notarske_listing.html`, `eks_listing.html`
- [ ] B5.2: `backend/services/scrapers/notarske_drazby_scraper.py`
- [ ] B5.3: `backend/services/scrapers/eks_scraper.py`
- [ ] B5.4: Pridat do `SCRAPER_REGISTRY` (2 zaznamy)
- [ ] B5.5: Testy (~20 testov)
- [ ] B5.6: Aktualizacia dokumentacie

### B6 - bsk_kraj + obce_uradne_tabule (najkomplexnejsie)

**Typ:** urade tabule - prebytocny majetok BSK + obecne predaje
**URL:** regionbratislava.sk / (per-obec - viac URL)
**Rate:** 5/min | **Zone:** GREEN
**Poznamka:** obce_uradne_tabule = parser per-obec, potrebuje zoznam URL obci

- [ ] B6.1: HTML vzorky -> `tests/fixtures/bsk_listing.html`, `obec_tabula_listing.html`
- [ ] B6.2: `backend/services/scrapers/bsk_kraj_scraper.py`
- [ ] B6.3: `backend/services/scrapers/obce_uradne_tabule_scraper.py`
  - Subkonfig: zoznam URL obci (v criteria.yaml alebo osobitny subor)
- [ ] B6.4: Pridat do `SCRAPER_REGISTRY` (2 zaznamy)
- [ ] B6.5: Testy (~20 testov)
- [ ] B6.6: Aktualizacia dokumentacie

---

## FAZA C - LLM agent (volitelne)

**Ciel:** LangChain + Google Gemini orchestruje existujuce nastroje (@tool)
**Pozaduje:** GOOGLE_API_KEY v .env
**Poznamka:** Pipeline funguje aj bez LLM. LLM prida inteligentne rozhodovanie.

- [ ] C1: `backend/services/llm_agent_service.py`
  - Gemini ako primarny LLM, Claude ako zaloha
  - @tool obaly: analyze_parcel_tool, scrape_source_tool, get_status_tool
  - LangChain AgentExecutor s max 50 iteraciami
- [ ] C2: `tests/test_llm_agent_service.py` (~15 testov - mock LLM)
- [ ] C3: Aktualizacia dokumentacie

---

## FAZA D - Frontend rozsirenia (volitelne)

- [ ] D1: Tlacidlo "Spustit realny sken" -> `POST /api/monitor/scan`
- [ ] D2: Status monitora na stranke (posledny scan, dalsi scan)
- [ ] D3: Real-time aktualizacia vysledkov (polling /api/monitor/status)
- [ ] D4: Filter kariet podla skore / lokality
- [ ] D5: Export vysledkov do CSV / JSON

---

## Postup dodavania HTML vzoriek (pre FAZU B)

Pre kazdy zdroj v FAZE B:
1. Otvor portal v prehliadaci
2. Vyhladaj "pozemky predaj" alebo "drazba pozemok"
3. `Ctrl+S` -> Uloz ako "Webova stranka, iba HTML"
4. Uloz do `tests/fixtures/<zdroj>_listing.html`
5. Notifikuj AI: "Dal som HTML pre <zdroj>"

Potom AI: precita fixture, extrahuje strukturu, napise presny parser.

---

## Prehladna tabulka pokroku

| Faza | Popis | Status | Testy |
|------|-------|--------|-------|
| HOTOVO | GIS, scoring, cadastral, report, pipeline, notifier, API, frontend | ✅ | 608 |
| HOTOVO | scraper kostra + nehnutelnosti_sk | ✅ | +36 |
| **A** | monitor_service + periodicky scan | ✅ HOTOVO | +26 |
| B1 | topreality_sk | ✅ HOTOVO | +45 |
| B2 | obchodny_vestnik (ZLATO) | ⏳ NEXT | ~+15 |
| B3 | spf | ❌ caka na HTML | ~+15 |
| B4 | exekutorske + drazby_net | ❌ caka na HTML | ~+20 |
| B5 | notarske + eks | ❌ caka na HTML | ~+20 |
| B6 | bsk_kraj + obce (najkomplexnejsie) | ❌ caka na HTML | ~+20 |
| C | llm_agent_service (volitelne) | ❌ | ~+15 |
| D | frontend rozsirenia (volitelne) | ❌ | manual |
| **TOTAL** | | | **~870** |
