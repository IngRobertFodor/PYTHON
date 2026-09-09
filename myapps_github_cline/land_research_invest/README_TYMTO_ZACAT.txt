Land Research Invest
====================

AI agent, ktory vyhladava dostupne stavebne pozemky
(do 70 km od Bratislavy) a automaticky ich preveruje
podla kriterii, ktore su pre vas dolezite.

Vy nastavite rozpocet a poziadavky. Agent urobi prieskum.
Dostandte zoriadeny zoznam kandidatov -- a checklist pre tych,
ktorych sa oplati navstivit.


==============================================================
CO AGENT OVERI ZA VAS
==============================================================

Pri kazdom najdenom pozemku agent automaticky skontroluje:

  Cena              Je cena ferova vs. okolite pozemky?
  Vzdialenost       Ako daleko od Bratislavy? Cas jazdy?
  Zaplavy           Je v zaplavovej zone? (100-rocne data SHMU)
  Teren             Sklon, zosuvy, radonove riziko
  Bonita pody       Vyska statnych odvodov za vynatie z PPF
  Pristupova cesta  Riadna cesta, min. sirka pre hasicov (6 m)
  Siete             Vzdialenost elektriny, vody, kanalizacie
  Prostredie        Dialnica, priemysel, skladka v okoli?
  Chranene uzemia   Natura 2000, CHKO, narodny park?
  Tvar parcely      Sirka a pravidelnost (pre stavebnú ciaru)

Kazdy pozemok dostane skore od 0 do 100:

  85-100   STRONG BUY  -- vynikajuci, konajte rychlo
  70-84    INVESTIGATE -- dobry kandidat, overte a navstivte
  50-69    CONSIDER    -- mozne, ma urcite kompromisy
   0-49    SKIP        -- nesplnĽa vase kriteria


==============================================================
CO MUSIITE UROBIT RUCNE
==============================================================

Agent vsetko pripravi -- vy dokoncite posledny krok:

  List vlastnictva (kataster)
    Portal blokuje automatizaciu (CAPTCHA).
    Agent vygeneruje checklist -> vy overite na:
    https://kataster.skgeodesy.sk

  Uzemnoplanovacie informacia (UPI od obce)
    Pisomne potvrdenie od obce (IBV zona).
    Agent pripravi ziadost.

  Kapacita trafostanice
    Blízkost vedenia sa overi automaticky.
    Kapacitu si potvrdte u distributora (ZSDIS).


==============================================================
KDE HLADA
==============================================================

  Realitne portaly    Nehnutelnosti.sk, TopReality.sk, Reality.sk
  Statne pozemky      SPF -- Slovensky pozemkovy fond
  Notarske drazby     Casto pod trhovou cenou
  Exekucne predaje    Mozu byt vyrazne podhodnotene
  Obchodny vestnik    Konkurzy a sudne drazby -- zlata bana
  Obecne predaje      Samospravy predavajuce prebytocne pozemky


==============================================================
STAV PROJEKTU
==============================================================

  Backend sluzby:  17 z 17 naimplementovanych
  Testy:           723 testov, 0 zlyhani
  Pokrytie toku:   pipeline_service orchestruje cely tok

  Zostatok:
    llm_agent_service, realestate_scraper_service,
    monitor_service


==============================================================
AKO ZACAT
==============================================================

  Ako nainstalovat a spustit:
    -> AKO_SPUSTIT_POUZIVATEL.txt

  Ako nastavit cenu, vzdialenost, velkost a dalsie poziadavky:
    -> NASTAVENIA_POUZIVATEL.txt

  Technicka dokumentacia (architektura, sluzby, endpointy):
    -> ARCHITEKTURA_DEVELOPER.txt


Autor: Robert Fodor | 2026
