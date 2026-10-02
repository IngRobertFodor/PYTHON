// demo.js - vzorove pozemky pre ukazku UI
// Aktualizovane: realne lokality BA okolia, demonstruju nove funkcie
// (skvost detektor, J1 infra, UP asistent, rozpad skore)
const DEMO_PARCELS = [
  {
    // SKVOST KANDIDAT: orná pôda na okraji Malaciek, priama dostupnosť
    title: "Orná pôda - okraj Malaciek, siete nablízku",
    url: "https://nehnutelnosti.sk/demo/1",
    source_portal: "nehnutelnosti_sk",
    price_eur: 7500,
    area_sqm: 650,
    location_text: "Malacky, Bratislavský kraj",
    parcel_number: "1842/3",
    description: "Orná pôda na okraji zastavaného územia. Elektrina a cesta 30 m.",
    lat: 48.435, lon: 17.023,
  },
  {
    // DRAŽBA: exekútorská dražba, nízka cena = podhodnotené
    title: "Exekútorská dražba - záhrada Senec",
    url: "https://www.ske.sk/drazobna-vyhlaska-detail/?ov_podanie_id=demo2",
    source_portal: "ske_drazobne_vyhlasky",
    price_eur: 4200,
    area_sqm: 480,
    location_text: "Senec, Bratislavský kraj",
    parcel_number: "LV 512",
    description: "Záhrada na okraji obce. Dátum dražby: 15.11.2026. Exekútor: JUDr. Novák.",
    lat: 48.218, lon: 17.396,
  },
  {
    // STRED DEDINY: stavebný pozemok v centre — drahší ale priama dostupnosť
    title: "Stavebný pozemok - centrum Pezinok",
    url: "https://topreality.sk/demo/3",
    source_portal: "topreality_sk",
    price_eur: 9800,
    area_sqm: 420,
    location_text: "Pezinok, Bratislavský kraj",
    parcel_number: "876/1",
    description: "Stavebný pozemok priamo v obci, všetky siete.",
    lat: 48.290, lon: 17.267,
  },
  {
    // MIMO OBCE: lacné pole bez sietí - zdanlivo atraktívne
    title: "Orná pôda - mimo obce (pozor na siete)",
    url: "https://reality.sk/demo/4",
    source_portal: "reality_sk",
    price_eur: 3500,
    area_sqm: 800,
    location_text: "Veľký Biel, Senec okres",
    parcel_number: "2341/7",
    description: "Orná pôda pri poli. Najbližšia obec 400 m, siete ďaleko.",
    lat: 48.206, lon: 17.345,
  },
  {
    // SPF pozemok: štátny pozemkový fond - zvyčajne lacný
    title: "SPF pozemok - záhrada Modra",
    url: "https://pozfond.sk/demo/5",
    source_portal: "spf",
    price_eur: 5800,
    area_sqm: 550,
    location_text: "Modra, Pezinok okres",
    parcel_number: "LV 234 / k.ú. Modra",
    description: "Pozemok Štátneho pozemkového fondu. Záhrada blízko viníc.",
    lat: 48.338, lon: 17.303,
  },
];
