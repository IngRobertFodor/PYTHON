Land Research Invest
====================

AI agent, ktorý vyhľadáva dostupné stavebné pozemky
(do 70 km od Bratislavy) a automaticky ich preveruje
podľa kritérií, ktoré sú pre vás dôležité.

Vy nastavíte rozpočet a požiadavky. Agent urobí prieskum.
Dostanete zoradený zoznam kandidátov — a checklist pre tých,
ktorých sa oplatí navštíviť.


==============================================================
ČO AGENT OVERÍ ZA VÁS
==============================================================

Pri každom nájdenom pozemku agent automaticky skontroluje:

  Cena              Je cena férová vs. okolité pozemky?
  Vzdialenosť       Ako ďaleko od Bratislavy? Čas jazdy?
  Záplavy           Je v záplavovej zóne? (100-ročné dáta SHMÚ)
  Terén             Sklon, zosuvy, radónové riziko
  Bonita pôdy       Výška štátnych odvodov za vyňatie z PPF
  Prístupová cesta  Riadna cesta, min. šírka pre hasičov (6 m)
  Siete             Vzdialenosť elektriny, vody, kanalizácie
  Prostredie        Diaľnica, priemysel, skládka v okolí?
  Chránené územia   Natura 2000, CHKO, národný park?
  Tvar parcely      Šírka a pravidelnosť (pre stavebnú čiaru)

Každý pozemok dostane skóre od 0 do 100:

  85–100   SILNÁ KÚPA    — vynikajúci, konajte rýchlo
  70–84    PREVERIT      — dobrý kandidát, overte a navštívte
  50–69    ZVÁŽIŤ        — možné, má určité kompromisy
   0–49    PRESKOČIŤ     — nespĺňa vaše kritériá


==============================================================
ČO MUSÍTE UROBIŤ RUČNE
==============================================================

Agent všetko pripraví — vy dokončíte posledný krok:

  List vlastníctva (kataster)
    Portál blokuje automatizáciu (CAPTCHA).
    Agent vygeneruje checklist → vy overíte na:
    https://kataster.skgeodesy.sk

  Územnoplánovacia informácia (ÚPI od obce)
    Písomné potvrdenie od obce (IBV zóna).
    Agent pripraví žiadosť.

  Kapacita trafostanice
    Blízkosť vedenia sa overí automaticky.
    Kapacitu si potvrďte u distribútora (ZSDIS).


==============================================================
KDE HĽADÁ
==============================================================

  Realitné portály    Nehnutelnosti.sk, TopReality.sk, Reality.sk
  Štátne pozemky      SPF — Slovenský pozemkový fond
  Notárske dražby     Často pod trhovou cenou
  Exekučné predaje    Môžu byť výrazne podhodnotené
  Obchodný vestník    Konkurzy a súdne dražby — zlatá baňa
  Obecné predaje      Samosprávy predávajúce prebytočné pozemky


==============================================================
AKO ZAČAŤ
==============================================================

  Ako nainštalovať a spustiť:
    → AKO_SPUSTIT_POUZIVATEL.txt

  Ako nastaviť cenu, vzdialenosť, veľkosť a ďalšie požiadavky:
    → NASTAVENIA_POUZIVATEL.txt

  Technická dokumentácia (architektúra, služby, endpointy):
    → ARCHITEKTURA_DEVELOPER.txt


Autor: Robert Fodor | 2026
