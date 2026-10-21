"""
Parcel Model
============
Datovy model pozemku - zhromazduje data zo vsetkych sluzieb.
Jedna instancia = jeden kandidatsky pozemok.
"""

from dataclasses import dataclass, field
from typing import Any
from models.result import ServiceResult


@dataclass
class Parcel:
    """
    Kandidatsky pozemok so vsetkymi nazbieranymi datami.

    Plnenie:
        1. Scraper vytvori Parcel zo zakladnych udajov inzeratu
        2. Kazda sluzba doplni svoj ServiceResult do results{}
        3. ScoringService vypocita final_score z results
    """

    # --- Zakladne udaje z inzeratu ---
    url: str = ""                   # URL inzeratu
    source_portal: str = ""         # napr. "nehnutelnosti_sk"
    title: str = ""                 # nazov inzeratu
    price_eur: float = 0.0          # cena v EUR
    area_sqm: float = 0.0           # vymera v m2
    location_text: str = ""         # textova adresa z inzeratu
    parcel_number: str = ""         # cislo parcely (ak je v inzeráte)
    description: str = ""           # popis z inzeratu

    # --- GPS suradnice (doplni geocoding_service) ---
    lat: float = 0.0
    lon: float = 0.0

    # --- Vypoctove polia ---
    price_per_sqm: float = 0.0      # EUR/m2 (vypocitane)

    # --- Vysledky sluzieb ---
    # kluc = nazov sluzby, hodnota = ServiceResult
    results: dict[str, ServiceResult] = field(default_factory=dict)

    # --- Finalne skore (doplni scoring_service) ---
    final_score: float = 0.0
    recommendation: str = ""        # STRONG BUY / INVESTIGATE / CONSIDER / SKIP

    # --- Lacny pre-scoring (bez HTTP, instantny po scrape_all) ---
    preliminary_score: float = 0.0
    prelim_recommendation: str = "" # STRONG BUY / INVESTIGATE / CONSIDER / SKIP / NEDOSTATOK_DAT
    prelim_confidence: float = 1.0  # 0.0-1.0: podiel vah pouzitych pri vypocte skore
    prelim_missing: list = field(default_factory=list)   # ["cena", "poloha"] atd.
    prelim_breakdown: dict = field(default_factory=dict) # {"price": 100.0, "area": None, ...}
    signals: list = field(default_factory=list)          # investicne signaly (prelim + GIS)

    # --- Rezoning — kvantifikácia zisku z preklasifikácie (rezoning_service) ---
    rezoning_profit_eur: float = 0.0    # čistý odhadovaný zisk v EUR
    rezoning_cost_eur:   float = 0.0    # náklady (vyňatie + zasieťovanie)
    rezoning_value_eur:  float = 0.0    # odhadovaná hodnota ako stavebný
    rezoning_breakdown:  dict  = field(default_factory=dict)  # rozpis položiek

    # --- B1: História cien a čas na trhu ---
    listing_age_days: int   = 0         # počet dní od first_seen (z DB po save_run)
    price_drop_pct:   float = 0.0       # % pokles ceny (prvá vs. posledná v histórii)
    price_history:    list  = field(default_factory=list)  # [{date, price_eur}, ...]

    # --- B2: Dražobné polia ---
    vyvolavacia_cena_eur:  float = 0.0  # najnižšie podanie (vyvolávacia cena dražby)
    znalecka_hodnota_eur:  float = 0.0  # odhad/znalecká hodnota predmetu dražby
    drazba_kolo:           int   = 0    # 0=neznáme, 1=prvé kolo, 2+=opakovaná dražba

    def add_result(self, result: ServiceResult) -> None:
        """Prida vysledok sluzby do results dict."""
        self.results[result.source] = result

    def get_result(self, source: str) -> ServiceResult | None:
        """Vrati vysledok danej sluzby, alebo None ak chyba."""
        return self.results.get(source)

    def is_rejected(self) -> bool:
        """
        Vrati True ak ktokolvek validátor oznacil pozemok za nevhodny
        (ok=False a score=0 - nie skip_result).
        """
        for result in self.results.values():
            if not result.ok and result.score == 0 and not result.data.get("skipped"):
                return True
        return False

    def to_dict(self) -> dict:
        """Serializacia pre JSON API odpovede."""
        return {
            "url": self.url,
            "source_portal": self.source_portal,
            "title": self.title,
            "price_eur": self.price_eur,
            "area_sqm": self.area_sqm,
            "location_text": self.location_text,
            "parcel_number": self.parcel_number,
            "lat": self.lat,
            "lon": self.lon,
            "price_per_sqm": self.price_per_sqm,
            "final_score": self.final_score,
            "recommendation": self.recommendation,
            "preliminary_score": self.preliminary_score,
            "prelim_recommendation": self.prelim_recommendation,
            "prelim_confidence": self.prelim_confidence,
            "prelim_missing": self.prelim_missing,
            "prelim_breakdown": self.prelim_breakdown,
            "signals": self.signals,
            "rezoning_profit_eur":  self.rezoning_profit_eur,
            "rezoning_cost_eur":    self.rezoning_cost_eur,
            "rezoning_value_eur":   self.rezoning_value_eur,
            "rezoning_breakdown":   self.rezoning_breakdown,
            "listing_age_days":     self.listing_age_days,
            "price_drop_pct":       self.price_drop_pct,
            "price_history":        self.price_history,
            "vyvolavacia_cena_eur": self.vyvolavacia_cena_eur,
            "znalecka_hodnota_eur": self.znalecka_hodnota_eur,
            "drazba_kolo":          self.drazba_kolo,
            "results": {k: v.to_dict() for k, v in self.results.items()},
        }
