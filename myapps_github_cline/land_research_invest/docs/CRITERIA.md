# 📋 Kritériá vyhľadávania — Land Research Invest Agent

Mapovanie 5 skupín požiadaviek na konkrétne služby a stav automatizácie.

---

## 🔑 Legenda

| Symbol | Význam |
|--------|--------|
| ✅ Auto | Agent zvládne plne automaticky |
| ⚠️ Čiastočne | Agent poskytne indíciu / blízkosť, finálne potvrdenie manuálne |
| ❌ Manuál | Agent vygeneruje checklist, kontrola výhradne ručná (CAPTCHA / úrad) |

---

## 1. Územno-právne riziká (ÚPI z Obce)

| Kritérium | Služba | Auto? |
|-----------|--------|-------|
| Vydaná ÚPI — zóna IBV | `cadastral_service` | ❌ Manuál (obec) |
| Absencia požiadavky na ÚPZ / zón. štúdiu | — | ❌ Manuál (z ÚPI) |
| Index zastavanosti (IZP ≥ 0.25) | `scoring_service` | ⚠️ Manuál (z ÚPI) |
| Stavebná čara a odstupy OK | `zbgis_service` | ✅ Geometria WFS |
| Šírka parcely min 15–16 m | `zbgis_service` | ✅ Geometria WFS |

---

## 2. List vlastníctva a Kataster (ZBGIS)

| Kritérium | Služba | Auto? |
|-----------|--------|-------|
| Žiadna aktívna plomba (V, Z) | `cadastral_service` | ❌ Manuál (CAPTCHA) |
| Časť C: bez kritických tiarch | `cadastral_service` | ❌ Manuál (CAPTCHA) |
| Max 2 spoluvlastníci, register E OK | `cadastral_service` | ❌ Manuál (CAPTCHA) |
| Bez záložného práva / dožitia | `cadastral_service` | ❌ Manuál (CAPTCHA) |
| Bez predkupného práva štátu/obce | `cadastral_service` | ❌ Manuál (CAPTCHA) |

> **Poznámka:** `katasterportal.sk` blokuje automatizáciu CAPTCHA.
> Agent pre každý top pozemok vygeneruje štruktúrovaný checklist so sekciami B/C/D,
> ktorý vyplníte ručne na `kataster.skgeodesy.sk`.

---

## 3. Prístupová cesta a infraštruktúra

| Kritérium | Služba | Auto? |
|-----------|--------|-------|
| Právny prístup (obec / vecné bremeno) | `cadastral_service` | ⚠️ LV cesty manuál |
| Šírka cesty min 6 m (hasiči) | `overpass_service` | ✅ OSM `width` tag |
| Prístupová cesta nie je v správe SPF | `cadastral_service` | ❌ Manuál |

---

## 4. Inžinierske siete (kapacita a vzdialenosť)

| Kritérium | Služba | Auto? |
|-----------|--------|-------|
| Elektrina — blízkosť vedenia | `overpass_service` | ✅ OSM `power=line` |
| Elektrina — kapacita trafostanice | — | ⚠️ Potvrdiť ZSDIS |
| Vzdialenosť napojenia sietí (metre) | `overpass_service` | ✅ OSM |
| Kanalizácia v obci | `overpass_service` | ✅ OSM `sewer` |
| Žumpa / ČOV povolená (ak bez kan.) | `scoring_service` | ⚠️ Poznámka v reporte |

---

## 5. Geológia, terén a ochranné pásma

| Kritérium | Služba | Auto? |
|-----------|--------|-------|
| Mimo záplavového územia Q100 | `flood_service` | ✅ SHMÚ WMS |
| Bezpečné podložie / spodná voda | `bpej_service` | ⚠️ Zosuvné mapy ŠGÚDŠ |
| Environmentálna záťaž (skládka) | `overpass_service` | ⚠️ OSM `landuse=landfill` |
| Ochranné pásmo VVN (vysoké napätie) | `overpass_service` | ✅ OSM `power=line` |
| Ochranné pásmo VTL (vysokotl. plyn) | `overpass_service` | ✅ OSM `pipeline` |
| 50 m pásmo lesa | `overpass_service` | ✅ OSM `forest` + buffer |
| Archeologická zóna | `cadastral_service` | ❌ Manuál (KPÚ) |
| Bonita pôdy BPEJ (skupina 1–4) | `bpej_service` | ✅ WMS + odhad odvodov |

---

## 📊 Súhrn realizovateľnosti

### ✅ Plne automatizovateľné — jadro scoring engine
- Geometria parcely (šírka, tvar, výmera)
- Vzdialenosť od Bratislavy
- Záplavy Q100
- Bonita pôdy BPEJ + odhad odvodov za vyňatie z PPF
- Ochranné pásma VVN / VTL / les
- Šírka prístupovej cesty
- Blízkosť elektriny, kanalizácie

### ⚠️ Čiastočne automatizovateľné
- Kapacita trafostanice (blízkosť auto, kapacitu potvrdiť ZSDIS)
- Zosuvné územia (ak dostupné WMS vrstvy ŠGÚDŠ)
- Právny prístup cesty (blízkosť auto, LV cesty manuál)

### ❌ Nutne manuálne — agent generuje checklisty
- List vlastníctva sekcie B/C/D (CAPTCHA)
- Vydanie ÚPI/ÚPZ (obec)
- Kapacita trafostanice (ZSDIS)
- Archeologická zóna (KPÚ)

---

## ⚙️ Predvolené hodnoty kritérií (`config/criteria.yaml`)

| Parameter | Predvolená hodnota |
|-----------|--------------------|
| Max cena | 50 000 EUR |
| Min cena | 10 000 EUR |
| Max vzdialenosť od BA | 70 km |
| Min výmera | 600 m² |
| Max výmera | 1 500 m² |
| Min šírka parcely | 15 m |
| Požadovaná zóna | IBV, rodinné domy |
| Min šírka cesty | 6 m |
| Max BPEJ ochranná skupina | 6 |
| Score prah pre checklist | 70 / 100 |

---

## 📝 Autor

Robert Fodor | 2026
