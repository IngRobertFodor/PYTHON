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
            "results": {k: v.to_dict() for k, v in self.results.items()},
        }
