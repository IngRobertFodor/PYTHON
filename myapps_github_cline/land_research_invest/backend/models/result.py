"""
Result Model
============
Jednotny kontrakt pre vystup kazdej sluzby agenta.
Vsetky validatory vracia tento format - scoring a agent
pracuju s nimi uniformne bez ohladu na zdroj.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ServiceResult:
    """
    Jednotny vystup kazdej sluzby (validatora).

    Pouzitie:
        result = ServiceResult(
            ok=True,
            score=80,
            data={"distance_km": 45.2},
            source="distance_service"
        )
    """
    ok: bool                        # podarilo sa ziskat data?
    score: float                    # ciastkove skore 0-100
    data: dict = field(default_factory=dict)   # detaily (specificke pre kazdu sluzbu)
    error: str | None = None        # chybova sprava ak ok=False
    source: str = ""                # nazov sluzby ktora result vytvorila
    cached: bool = False            # boli data z cache?

    def to_dict(self) -> dict:
        """Serializacia pre JSON API odpovede."""
        return {
            "ok": self.ok,
            "score": self.score,
            "data": self.data,
            "error": self.error,
            "source": self.source,
            "cached": self.cached,
        }

    @staticmethod
    def error_result(source: str, message: str) -> "ServiceResult":
        """
        Pomocna metoda pre error stav - score 0, ok=False.

        Args:
            source: nazov sluzby
            message: popis chyby

        Returns:
            ServiceResult s ok=False a score=0
        """
        return ServiceResult(
            ok=False,
            score=0.0,
            data={},
            error=message,
            source=source,
        )

    @staticmethod
    def skip_result(source: str, reason: str) -> "ServiceResult":
        """
        Pomocna metoda ked je feature vypnuta (feature flag=False).
        Vrati neutralny vysledok ktory nema vplyv na scoring.

        Args:
            source: nazov sluzby
            reason: dovod preskocenia

        Returns:
            ServiceResult s ok=True, score=50 (neutralne), data={'skipped': True}
        """
        return ServiceResult(
            ok=True,
            score=50.0,
            data={"skipped": True, "reason": reason},
            error=None,
            source=source,
        )
