# Land Research Invest

AI agent, ktorý vyhľadáva dostupné stavebné pozemky (do 82 km od Bratislavy)
a automaticky ich preveruje podľa vašich kritérií.

Vy nastavíte rozpočet a požiadavky. Agent urobí prieskum.
Dostanete zoradený zoznam kandidátov — a checklist pre tých, ktorých sa oplatí navštíviť.

---

## 1. Rýchly štart

**Dvojklik na `spustit.bat`** — server sa spustí, prehliadač sa otvorí automaticky.

Ak chcete skratku na ploche (Windows):
1. Pravý klik na ploche → Nový → Skratka
2. Umiestnenie: `C:\__TESTAUTOMATION\SCRIPTS\PYTHON\myapps_github_cline\land_research_invest\spustit.bat`
3. Názov: `Land Research Invest`
4. Voliteľne ikonka: Vlastnosti → Zmeniť ikonu → `C:\Windows\System32\shell32.dll` → č. 22

Po spustení:
- Príkazový riadok zobrazuje Flask log
- Prehliadač sa otvorí na `http://localhost:5001`
- Zastavenie: zatvoriť okno príkazového riadku (Ctrl+C)

---

## 2. Čo agent overí za vás

| Kritérium | Čo sa overuje |
|---|---|
| Cena | Férová vs. okolité pozemky? Podozrivo nízke EUR/m² = varuje |
| Vzdialenosť | Ako ďaleko od Bratislavy? (odhad z názvu obce) |
| Záplavy | Je v záplavovej zóne? (100-ročné dáta SHMU) |
| Terén | Sklon, zosuvy, radónové riziko |
| Bonita pôdy | Výška štátnych odvodov za vyňatie z PPF |
| Prístupová cesta | Riadna cesta, min. šírka pre hasičov (6 m) |
| Siete | Vzdialenosť elektriny, vody, kanalizácie |
| Prostredie | Diaľnica, priemysel, skládka v okolí? |
| Chránené územia | Natura 2000, CHKO, národný park? |
| Tvar parcely | Šírka a pravidelnosť (pre stavebnú čiaru) |
| Priama dostupnosť | Siete tesne vedľa (< 50 m) = nízke náklady na prípojky |
| Poloha v obci | Okraj / Stred / Mimo — okraj = rozvojový potenciál |
| Druh pozemku | Orná pôda / záhrada / zastav. plocha (z katastra KN) |
| Skvost flag | Okraj + priame siete + poľnohosp. pôda = investičná prémia |

---

## 3. Skóre a farby

### GIS skóre (0–100)

| Rozsah | Verdikt | Farba |
|---|---|---|
| 85–100 | SILNÁ KÚPA | zelená |
| 70–84 | PREVERIŤ | modrá |
| 50–69 | ZVÁŽIŤ | oranžová |
| 0–49 | PRESKOČIŤ | červená |

**Dve fázy:**
- **Predbežné skóre** — ihneď po prieskume, 0 sieťových požiadaviek. Váhy: cena 30% | výmera 25% | EUR/m² 20% | vzdialenosť 10% | typ zdroja 10%. Chýbajúci údaj: váha 0, skóre sa nezníži.
- **Plné GIS skóre** — spustíte ručne pre vybrané pozemky (~20 s/pozemok). Váhy v `config/criteria.yaml → scoring → weights`.

### Investičný index (0–100)

| Zložka | Max b. |
|---|---|
| Potenciál preklasifikácie | 35 |
| Mispricingové signály | 35 |
| Kvalita dát (istota) | 15 |
| Rizikové penalizácie | −25 max |


### Investičné signály

| Signál | Typ | Kedy |
|---|---|---|
| 🟢 BLIZKO_BA | príležitosť | < 25 km od BA |
| 🟢 DRAZBA_PODHODNOTENA | príležitosť | dražba s cenou v rozsahu |
| 🟢 HORICE | príležitosť | dlho v ponuke + klesajúca cena + 180+ dní |
| 🟢 DRAZBA_POD_ZNALECKOU | príležitosť | vyvolávacia ≥ 20 % pod znaleckou |
| 🟢 DRAZBA_OPAKOVANA | príležitosť | kolo ≥ 2 (predchádzajúce bez záujemcov) |
| 🟢 LACNEJSI_AKO_OKOLIE | príležitosť | ppsm < 60 % mediánu obce (min. 4 pozemky) |
| 🟡 DLHO_V_PONUKE | info | inzerát > 120 dní |
| 🟡 CENA_KLESA | info | pokles ceny ≥ 5 % od prvého záznamu |
| 🔴 CENA_PODOZRIVA | riziko | podozrivo nízke €/m² z inzerátu |
| 🔴 PRILIS_DALEKO | riziko | > 82 km od BA |
| 🔴 PODIEL_ALEBO_CHYBNE_DATA | riziko | výmera < 100 m² alebo cena < 500 € |

Signály sa zobrazujú ako farebné chipy v tabuľke vedľa skóre.
Historické signály (HORICE, DLHO_V_PONUKE, CENA_KLESA) sa budujú po 2+ behoch.

---

## 4. Nastavenia (config/criteria.yaml)

Všetko meníte v **jedinom súbore** `config/criteria.yaml`. Po zmene reštartovať appku.
> Formát YAML: odsadenie = medzery (NIE tabulátory).

### Rýchly prehľad

| Čo zmeniť | Kde v YAML |
|---|---|
| Maximálna cena | `criteria → price → max_eur` |
| Bližšie k BA | `criteria → location → max_distance_km` |
| Väčšie pozemky | `criteria → parcel → min_area_sqm` |
| Váhy GIS | `scoring → weights` (súčet = 1.0) |
| Filter prahov | `scoring → thresholds → strong_buy` |
| Signál HORICE | `signals → horice_dlho_days` (dni, default 180) |
| Index váhy | `opportunity → mispricing_weights` |
| Index penalizácie | `opportunity → risk_penalties` |
| Vypnúť zdroj | `sources → NAZOV → enabled: false` |
| Vypnúť kontrolu | `features → use_XXX: false` |

### Váhy GIS skóre (`scoring → weights`) — súčet MUSÍ byť 1.0

```yaml
price:           0.18
distance:        0.12
infrastructure:  0.20
legal_proxy:     0.18
flood_risk:      0.10
soil_quality:    0.08
terrain:         0.07
protected_zones: 0.07
```

### Investičný index (`opportunity`)

```yaml
opportunity:
  mispricing_weights:
    LACNEJSI_AKO_OKOLIE: 0.75   # 0.4 = menej váhy peer comparison
  risk_penalties:
    PRILIS_DALEKO: 0            # 0 = vypnúť penalizáciu za vzdialenosť
```

### Časté chyby

```bash
# Zlý súčet váh → scoring.weights musí dávať 1.0
# Overiť YAML:
python -c "import yaml; yaml.safe_load(open('config/criteria.yaml'))"
# Overiť config testy:
python -m pytest tests/test_config_validator.py -v
```

---

## 5. Zdroje prieskumu

| Zdroj | Poznámka |
|---|---|
| nehnutelnosti.sk | inzeráty |
| topreality.sk | inzeráty |
| reality.sk | inzeráty |
| SPF (pozfond.sk) | štátny pozemkový fond `!` |
| Notárske dražby | často pod trhovou cenou `!` |
| SKE dražobné vyhlášky | exekučné predaje `!` |
| Obchodný vestník | konkurzy a súdne dražby `!` |

`!` = najlepšie zdroje pre podhodnotené pozemky.
Vypnuté: Bazoš (blokovaný), bankové dražby, Facebook Marketplace (ToS — nikdy).

---

## 6. Záloha histórie

Po každom úspešnom prieskume sa DB automaticky zálohuje:

```
data/backups/parcels_latest.sql.gz   — najnovšia záloha (odporúčame commitnúť)
data/backups/history/                — rotovaný archív, posledných 20 (lokálne)
```

**Prenos na nový PC:**
1. `git add data/backups/parcels_latest.sql.gz` → commit → push
2. Nový PC: `git pull` → spustiť appku
3. UI → Nastavenia → Záloha histórie → **Obnoviť zo súboru** → `parcels_latest.sql.gz`

Manuálny export/import: UI → Nastavenia → Záloha histórie.

---

## 7. Riešenie problémov

| Problém | Riešenie |
|---|---|
| Python nie je nainštalovaný | python.org (zaškrtnúť Add to PATH) |
| Prieskum nenašiel výsledky | Portály dočasne nedostupné, skúste o 15 min |
| GIS služba timeout | Skúste neskôr; analýza prebehne aj bez nej (skóre 50) |
| Port 5001 obsadený | Zmeniť `PORT` v `.env` |
| Chcete AI (Gemini) | Vytvoriť `.env` s `GOOGLE_API_KEY=...` |
| Chybný YAML po zmene | `python -c "import yaml; yaml.safe_load(open('config/criteria.yaml'))"` |
| Signály chýbajú | Budujú sa postupne — spustite prieskum aspoň 2× |

---

## 8. REST API (pre pokročilých)

```
GET  /api/health
GET  /api/config/
POST /api/scrape/start
GET  /api/scrape/progress
GET  /api/scrape/results
POST /api/scrape/score-selected
GET  /api/scrape/score-progress
GET  /api/scrape/results.csv
GET  /api/scrape/diff            (nové/zlacneli/zmizli)
GET  /api/scrape/runs            (história behov)
GET  /api/scrape/up-links        (?location=<obec>)
GET  /api/scrape/up-coverage
GET  /api/backup/status
GET  /api/backup/export
POST /api/backup/import
GET  /api/backup/history
POST /api/analyze
POST /api/parcels/analyze-batch
```

---

## 9. Testy

```bash
python -m pytest tests/ -q        # 1546 testov, ~55 sekúnd
python -m pytest tests/ -v        # detailný výstup
```

---

Autor: Robert Fodor | 2026

