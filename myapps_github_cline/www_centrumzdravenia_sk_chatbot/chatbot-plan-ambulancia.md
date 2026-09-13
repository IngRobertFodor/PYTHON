# Plán: FAQ chatbot pre www.centrumuzdravenia.sk

**Cieľ:** Jednoduchý chatbot na stránke (Google Sites), ktorý odpovie návštevníkom na bežné otázky (ordinačné hodiny, adresa, cenník, ako sa objednať) porovnávaním kľúčových slov s vopred pripravenou databázou otázok a odpovedí. Bez AI, bez servera, bez dodatočných nákladov. Neskôr rozšíriteľné o AI a/alebo pomoc s objednávaním termínu.

**Náklady:** 0 € navyše (beží priamo v prehliadači návštevníka, žiadny backend).

---

## FÁZA 1 – Obsah (otázky a odpovede) ✅ (hotovo)

- [x] 1.1 Spísať zoznam najčastejších otázok návštevníkov (min. 10-15 na začiatok) — 18 otázok hotovo
- [x] 1.2 Ku každej otázke pripraviť stručnú, jasnú odpoveď (2-4 vety)
- [x] 1.3 Ku každej otázke priradiť kľúčové slová, podľa ktorých ju bot rozpozná (napr. "hodiny", "otvorené", "kedy" → odpoveď o ordinačných hodinách)
- [x] 1.4 Pripraviť aj "fallback" odpoveď pre prípad, že bot otázke nerozumie (napr. odkaz na telefón/e-mail ambulancie)
- [x] 1.5 Rozhodnúť o úvodnej uvítacej správe chatbota

Celý obsah je hotový a uložený v `chatbot-faq-obsah.md` (finálna verzia).

## FÁZA 2 – Postavenie widgetu

- [ ] 2.1 Vytvoriť HTML/CSS/JS chat widget (bublina v rohu, po kliknutí sa otvorí okno s chatom)
- [ ] 2.2 Naprogramovať logiku vyhľadávania odpovede podľa kľúčových slov z Fázy 1
- [ ] 2.3 Vizuál prispôsobiť farbám/štýlu stránky ambulancie
- [ ] 2.4 Otestovať lokálne (v prehliadači, mimo Google Sites)

## FÁZA 3 – Vloženie do Google Sites

- [ ] 3.1 V Google Sites: **Insert → Embed → Embed code**
- [ ] 3.2 Vložiť HTML/CSS/JS kód widgetu z Fázy 2
- [ ] 3.3 Nastaviť veľkosť embed boxu (widget sa zobrazí len v rámci tohto boxu, nie ako bublina cez celú stránku – obmedzenie Google Sites)
- [ ] 3.4 Umiestniť box na vhodné miesto (napr. spodná časť hlavnej stránky, alebo samostatná podstránka "Otázky")
- [ ] 3.5 Publikovať zmeny

## FÁZA 4 – Testovanie

- [ ] 4.1 Otestovať priamo na publikovanej stránke (aj na mobile, aj na počítači)
- [ ] 4.2 Skúsiť rôzne formulácie tej istej otázky, doladiť kľúčové slová podľa výsledkov
- [ ] 4.3 Dať otestovať niekomu netechnickému (napr. manželke), či mu odpovede dávajú zmysel

## FÁZA 5 – Neskoršie rozšírenia (voliteľné, nie teraz)

- [ ] 5.1 Napojenie na AI (cez existujúce n8n na Hetzneri) – bot by rozumel aj voľne formulovaným otázkam, nielen presným kľúčovým slovám. Vyžaduje účet u AI poskytovateľa a DPA (podobne ako pri Hetzneri) a mesačné náklady rádovo jednotky eur.
- [ ] 5.2 Pomoc s objednávaním termínu – prepojenie na Google Kalendár (rovnaký kalendár, aký sa už používa pri e-mailovej automatizácii)
- [ ] 5.3 Ak by bot niekedy ukladal konverzácie (napr. kvôli AI), treba znova riešiť GDPR – zatiaľ sa to netýka, lebo jednoduchý FAQ bot nič neukladá ani neposiela mimo prehliadača

---

## Poznámky / rozhodnutia

- Zámerne bez AI na začiatok – rýchlejšie na postavenie, nič nestojí, žiadne GDPR riziko (žiadne dáta neopúšťajú prehliadač návštevníka)
- Chatbot má odpovedať len na všeobecné informácie o ambulancii (hodiny, adresa, cenník, objednávanie) – **nemal by vyzývať návštevníkov na opis zdravotných ťažkostí**
- Google Sites obmedzenie: vlastný kód sa vkladá cez Insert → Embed → Embed code a vykresľuje sa v rámci pevného boxu, nie ako bublina cez celú stránku
- Widget beží na rovnakom princípe nezávisle od Hetzner/n8n infraštruktúry – v prípade rozšírenia o AI (Fáza 5) sa napojí na existujúci n8n server
