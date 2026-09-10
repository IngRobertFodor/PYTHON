// demo.js - vzorove pozemky pre ukazku UI
const DEMO_PARCELS = [
  {
    // PASS - idealna cena aj vymera v limitoch (0-10000 EUR, 350-1000 m2)
    title: "IBV pozemok Senec - pri centre",
    url: "https://nehnutelnosti.sk/demo/1",
    price_eur: 8000,
    area_sqm: 700,
    location_text: "Senec, Bratislavsky kraj",
    parcel_number: "1234/5",
    lat: 48.219, lon: 17.397,
  },
  {
    // PASS - horná hranica ceny, vymera OK
    title: "Stavebny pozemok Pezinok - tichy okraj",
    url: "https://nehnutelnosti.sk/demo/2",
    price_eur: 9500,
    area_sqm: 900,
    location_text: "Pezinok, Bratislavsky kraj",
    parcel_number: "567/8",
    lat: 48.289, lon: 17.266,
  },
  {
    // OVER_BUDGET - cena 22000 > max 10000
    title: "Lacny pozemok Malacky - velka plocha",
    url: "https://nehnutelnosti.sk/demo/3",
    price_eur: 22000,
    area_sqm: 800,
    location_text: "Malacky, Bratislavsky kraj",
    parcel_number: "891/2",
    lat: 48.434, lon: 17.024,
  },
  {
    // AREA_MISMATCH - vymera 300 < min 350
    title: "Pozemok Stupava - mala parcela",
    url: "https://nehnutelnosti.sk/demo/4",
    price_eur: 6000,
    area_sqm: 300,
    location_text: "Stupava, Bratislavsky kraj",
    parcel_number: "321/6",
    lat: 48.274, lon: 17.027,
  },
  {
    // AREA_MISMATCH - vymera 1400 > max 1000
    title: "Oracia poda Gbely - prilis velka",
    url: "https://nehnutelnosti.sk/demo/5",
    price_eur: 7000,
    area_sqm: 1400,
    location_text: "Gbely, Skalica okres",
    parcel_number: "741/3",
    lat: 48.718, lon: 17.115,
  },
];
