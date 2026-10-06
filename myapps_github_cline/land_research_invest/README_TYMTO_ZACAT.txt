Land Research Invest — ZAČNITE TÝMTO
======================================

AI agent, ktorý vyhľadáva dostupné stavebné pozemky
(do 85 km od Bratislavy) a automaticky ich preveruje
podľa vašich kritérií.

Vy nastavíte rozpočet a požiadavky. Agent urobí prieskum.
Dostanete zoradený zoznam kandidátov — a checklist pre tých,
ktorých sa oplatí navštíviť.


==============================================================
1. CO AGENT OVERI ZA VAS
==============================================================

Pri každom nájdenom pozemku agent automaticky skontroluje:

  Cena              Je cena férová vs. okolité pozemky?
                    Podozrivo nízke EUR/m2 z inzerátov = varuje
  Vzdialenosť       Ako ďaleko od Bratislavy? (odhad z názvu obce)
  Záplavy           Je v záplavovej zóne? (100-ročné dáta SHMU)
  Terén             Sklon, zosuvy, radónové riziko
  Bonita pôdy       Výška štátnych odvodov za vyňatie z PPF
  Prístupová cesta  Riadna cesta, min. šírka pre hasičov (6 m)
  Siete             Vzdialenosť elektriny, vody, kanalizácie
  Prostredie        Diaľnica, priemysel, skládka v okolí?
  Chránené územia   Natura 2000, CHKO, národný park?
  Tvar parcely      Šírka a pravidelnosť (pre stavebnú čiaru)
  Priama dostupnosť Siete tesne vedľa (< 50 m) = nízke náklady na prípojky
  Poloha v obci     Okraj / Stred / Mimo — okraj = rozvojový potenciál
  Druh pozemku      Orná pôda / záhrada / zastav. plocha (z katastra KN)
  Skvost flag       Okraj dediny + priame siete + poľnohosp. pôda = investičná prémia


==============================================================
2. SKORE A FARBY — AKO CITAT VYSLEDKY
==============================================================

Každý pozemok dostane skóre od 0 do 100:

  85-100   SILNA KUPA    (zelena)   — vynikajuci, konajte rychlo
  70-84    PREVERIT      (modra)    — dobry kandidat, overte a navstivte
  50-69    ZVAZIT        (oranzova) — mozne, ma urcite kompromisy
   0-49    PRESKOCIT     (cervena)  — nespĺňa vase kriteria

Dve fázy skórovania
-------------------
  Rýchle predbežné skóre  (ihneď po prieskume, 0 HTTP požiadaviek)
    Zohľadňuje: cena / výmera / EUR/m2 / vzdialenosť (odhad) / zdroj
    Váhy: cena 30% | výmera 25% | EUR/m2 20% | vzdialenosť 10%
          typ zdroja 10% | kvalita dát 5%
    Zobrazuje sa v tabuľke prieskumu (farebný odznak Skóre).
    Pozor: vzdialené pozemky (>85 km) a inzeráty s nevierohodnou
    cenou (<1.5 EUR/m2) dostanú automaticky nižšie predbežné skóre.

  Plné GIS skóre  (spustíte ručne pre vybrané pozemky, ~20s/pozemok)
    Zohľadňuje: 8 GIS komponentov (záplavy, terén, pôda, siete...)
    Váhy sa nastavujú v criteria.yaml (scoring -> weights, súčet = 1.00).
    Zobrazuje sa v modali a na mape ako plné markery.

Stavy GIS komponentov v rozpade skóre
--------------------------------------
  [ok]       Služba prebehla úspešne — skóre je spoľahlivé.
  [error]    Štátny GIS server neodpovedal (SHMU, ZBGIS, geodata.gov.sk).
             Použité neutrálne skóre 50. Pozemok nebol penalizovaný.
             Toto je BEŽNÁ situácia — slovenské štátne servery sú nestabilné.
  [missing]  Nepodarilo sa zistiť GPS súradnice — komponent nezapočítaný.
  [skip]     Komponent je vypnutý v nastaveniach (criteria.yaml).
  Aj keď niektoré komponenty skončia [error], analýza vždy dobehne.

Red flags v modali
------------------
  [!]  BLOKER — kritická chyba (napr. záplava Q100, chránené územie)
  [?]  VAROVANIE — upozornenie, nie bloker (napr. vyššia cena)

Prečo GIS servery zlyhávajú
-----------------------------
  Projekt používa verejné slovenské štátne databázy (SHMU, ZBGIS,
  geodata.gov.sk, Nominatim/OSM, Overpass API). Sú bezplatné, bez
  API kľúča — ale občas pomalé, dočasne nedostupné alebo blokujú
  automatické dopyty (403 Forbidden). Je to normálne.


==============================================================
3. INSTALACIA (iba raz)
==============================================================

Krok 1 — Python
  Stiahnite z https://www.python.org/downloads/
  Pri inštalácii zaškrtnite "Add Python to PATH".
  Po inštalácii reštartujte počítač.

Krok 2 — Google Gemini API kluč (voliteľné)
  Aplikácia funguje PLNE BEZ tohto kľúča.
  Pre voliteľné AI funkcie: https://aistudio.google.com/app/apikey
  Skopírujte ".env.example" na ".env" a vložte kľúč:
      GOOGLE_API_KEY=vas_kluc_tu

Krok 3 — Závislosti
  Dvakrát kliknite na "spustit.bat"
  Automaticky sa nainštalujú Flask, GIS knižnice, BeautifulSoup...
  Prvé spustenie môže trvať niekoľko minút.


==============================================================
4. SPUSTENIE
==============================================================

  Spustiť:  dvakrát kliknite na "spustit.bat"
            prehliadač sa otvorí na http://localhost:5001

  Zastaviť: zavrite čierne CMD okno
            alebo dvakrát kliknite na "STOP.bat"
            alebo Ctrl+C v CMD okne


==============================================================
5. AKO POUZIVAT
==============================================================

Krok 1 — Spustite prieskum
  Kliknite "Spustiť prieskum"
  Agent prehľadá ~11 zdrojov paralelne (trvá ~15 min).
  Po dokončení sa zobrazí tabuľka s rýchlym skóre.

Krok 2 — Filtrujte tabuľku
  Zdroj:          rozbaľovací zoznam (konkrétny portál)
  Typ zdroja:     tlačidlá  [Drazby] [Inzeraty] [SPF]
  Cena max:       maximálna cena v EUR
  Výmera min:     minimálna výmera v m2
  Min. skóre:     len pozemky nad zadaným skóre
  Posl. beh:      zaškrtnuté = zobrazí iba najnovší prieskum
                  (predvolene ZAP — odfiltruje duplicity zo starších behov)
  Len skvosty:    okraj dediny + priame siete + poľnohosp. pôda
  Sledované:      len pozemky s hviezdičkou (watchlist)

  Triedenie:      kliknite na hlavičku stĺpca Skore | Cena EUR
                  | m2 | EUR/m2 — opakovaný klik otočí smer

Krok 3 — Skórujte vybrané (plný GIS)
  Zaškrtnite max 30 pozemkov → kliknite "Skórovať vybrané"
  Trvá ~20s/pozemok. Po dokončení:
    - Modal: 8 GIS komponentov + odhad nákladov na prípojky
    - Mapa: plné GIS markery + sekcia Územný plán

Krok 4 — Analyzujte v modali
  Pre každý pozemok: kliknite na riadok v tabuľke.
  Sekcia "Územný plán":
    - Pre niektoré obce: priamy odkaz na UP mapu (gisplan.sk)
    - Pre ostatné: stránka obce + 3 cielené Google dotazy
    - Checklist 7 otázok (zóna bývania, zmena UP, záväzná časť...)

Krok 5 — Export
  CSV        všetky výsledky vrátane Priama_dostupnost, Skvost (SK Excel)
  JSON       plný export s GIS detailmi
  JSON slim  bez GIS detailov (ľahší súbor)


==============================================================
6. CO UROBIT RUCNE (agent to neprepaci)
==============================================================

  List vlastníctva (kataster)
    Portál blokuje automatizáciu (CAPTCHA).
    Agent vygeneruje checklist → vy overíte na:
    https://kataster.skgeodesy.sk
    (sekcie B/C/D — vlastník, vecné bremená, záložné práva)

  Územnoplánovacia informácia (UPI od obce)
    Písomné potvrdenie IBV zóny od obce.
    Agent pripraví žiadosť a odkazy.

  Kapacita trafostanice
    Blízkosť vedenia = overená automaticky.
    Kapacitu si potvrďte u distribútora (ZSD/ZSDIS).


==============================================================
7. ZDROJE (co agent prehladava)
==============================================================

  Zapnuté (~11 zdrojov):
    Nehnutelnosti.sk      hlavný portál
    TopReality.sk         limit 10 req/min
    Reality.sk
    Byty.sk
    SPF                   štátne pozemky (pozfond.sk)
    Notárske dražby       casto pod trhovou cenou  (!)
    SKE dražobné vyhlášky exekučné predaje          (!)
    Obchodný vestník      konkurzy a súdne dražby  (!)
    EKS štátny majetok    elektronické aukcie štátu
    BSK kraj              prebytočný majetok BSK
    Obecné úradné tabule  obecné predaje

  Vypnuté (dôvod v criteria.yaml):
    Bazos.sk              vyhľadávanie blokované
    Bankové dražby        overiť podmienky banky
    Facebook Marketplace  ToS zakazuje automatizáciu — NIKDY

  (!) = najlepšie zdroje pre podhodnotené pozemky


==============================================================
8. RIESENIE PROBLEMOV
==============================================================

  Python nie je nainštalovaný  -> python.org (zaškrtnite Add to PATH)
  Prieskum nenašiel výsledky   -> portály dočasne nedostupné,
                                  skúste o 15 min
  GIS služba timeout           -> skúste neskôr; analýza prebehne
                                  aj bez danej služby (skóre 50)
  Port 5001 obsadený           -> zmeňte PORT v .env
  Chcete AI (Gemini)           -> vytvorte .env s GOOGLE_API_KEY=...
  Chybný YAML po zmene         -> python -c "import yaml;
                                  yaml.safe_load(open('config/criteria.yaml'))"


==============================================================
9. KAM DALEJ
==============================================================

  Zmena ceny, vzdialenosti, váh scoring, zdrojov:
    -> NASTAVENIA_POUZIVATEL.txt

  Technická dokumentácia (architektúra, API, GIS služby):
    -> ARCHITEKTURA_DEVELOPER.txt

  Plán implementácie a TODO:
    -> PLAN_IMPLEMENTACIA.md


==============================================================
10. REST API (pre pokrocilych)
==============================================================

  GET  http://localhost:5001/api/health
  GET  http://localhost:5001/api/config/
  POST http://localhost:5001/api/analyze
  POST http://localhost:5001/api/parcels/analyze-batch
  POST http://localhost:5001/api/scrape/start
  GET  http://localhost:5001/api/scrape/progress
  GET  http://localhost:5001/api/scrape/results
  POST http://localhost:5001/api/scrape/score-selected
  GET  http://localhost:5001/api/scrape/score-progress
  GET  http://localhost:5001/api/scrape/results.csv
  GET  http://localhost:5001/api/scrape/diff          (nove/zlacneli/zmizli)
  GET  http://localhost:5001/api/scrape/runs          (historia behov)
  GET  http://localhost:5001/api/scrape/up-links      (?location=<obec>)
  GET  http://localhost:5001/api/scrape/up-coverage   (pokrytie gisplan.sk)


==============================================================
11. SPUSTENIE TESTOV
==============================================================

  python -m pytest tests/ -q       (1216 testov, ~35 sekund)
  python -m pytest tests/ -v       (detailny vystup)


Autor: Robert Fodor | 2026
