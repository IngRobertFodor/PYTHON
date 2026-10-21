"""
Testy - peer_analysis_service.py
=================================
Testuje compute_obec_stats(), peer_signal(), apply_peer_signals().
100% offline — bez HTTP, bez DB.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "backend"))

import pytest
from services.peer_analysis_service import (
    compute_obec_stats, peer_signal, apply_peer_signals, ObecStats,
)


def _p(loc: str, price: float, area: float, signals: list = None) -> dict:
    ppsm = price / area if area > 0 else 0.0
    return {"url": f"http://t/{loc}/{price}", "location_text": loc,
            "price_eur": price, "area_sqm": area, "price_per_sqm": ppsm,
            "signals": signals or [], "source_portal": "nehnutelnosti_sk"}


def _lehnice(extra_ppsm: float | None = None) -> list[dict]:
    base = [_p("Lehnice", 25000, 500) for _ in range(5)]  # 50 €/m²
    if extra_ppsm is not None:
        base.append(_p("Lehnice", int(extra_ppsm * 600), 600))
    return base


class TestComputeObecStats:

    def test_prazdny(self):
        assert compute_obec_stats([]) == {}

    def test_pod_min_count(self):
        assert compute_obec_stats([_p("Senec", 20000, 500) for _ in range(3)]) == {}

    def test_na_min_count(self):
        stats = compute_obec_stats([_p("Senec", 20000, 500) for _ in range(4)])
        assert "senec" in stats

    def test_median(self):
        stats = compute_obec_stats(_lehnice())
        assert stats["lehnice"].median_ppsm == pytest.approx(50.0)

    def test_count(self):
        assert compute_obec_stats(_lehnice())["lehnice"].count == 5

    def test_min_max(self):
        parcels = [_p("Senec", 20000, 500), _p("Senec", 30000, 500),
                   _p("Senec", 25000, 500), _p("Senec", 35000, 500)]
        s = compute_obec_stats(parcels)["senec"]
        assert s.min_ppsm == pytest.approx(40.0)
        assert s.max_ppsm == pytest.approx(70.0)



class TestPeerSignal:

    def _stats(self, median: float, count: int = 5) -> dict:
        return {"senec": ObecStats(median_ppsm=median, count=count,
                                   min_ppsm=median*0.7, max_ppsm=median*1.3)}

    def test_nad_prahom_ziadny(self):
        """40/50 = ratio 0.8 > 0.6 → None."""
        assert peer_signal(_p("Senec", 20000, 500), self._stats(50.0)) is None

    def test_pod_prahom_signal(self):
        """20/50 = ratio 0.4 ≤ 0.6 → signál."""
        sig = peer_signal(_p("Senec", 12000, 600), self._stats(50.0))
        assert sig is not None and sig["kod"] == "LACNEJSI_AKO_OKOLIE"

    def test_presne_na_prahom(self):
        """30/50 = ratio 0.6 == prah → signál."""
        assert peer_signal(_p("Senec", 15000, 500), self._stats(50.0)) is not None

    def test_obec_nie_v_stats(self):
        assert peer_signal(_p("Trnava", 20000, 500), self._stats(50.0)) is None

    def test_bez_lokality(self):
        assert peer_signal(_p("", 20000, 500), self._stats(50.0)) is None

    def test_hazik_typ_riziko(self):
        p = _p("Senec", 10000, 500, signals=[{"kod": "ZAPLAVA", "typ": "RIZIKO"}])
        sig = peer_signal(p, self._stats(50.0))
        assert sig["typ"] == "RIZIKO"

    def test_hazik_dovera_055(self):
        p = _p("Senec", 10000, 500, signals=[{"kod": "CHRANENE_UZEMIE", "typ": "RIZIKO"}])
        assert peer_signal(p, self._stats(50.0))["dovera"] == pytest.approx(0.55)

    def test_prilezitost_dovera_080(self):
        p = _p("Senec", 10000, 500,
               signals=[{"kod": "PREKLASIFIKACIA", "typ": "PRILEZITOST"}])
        sig = peer_signal(p, self._stats(50.0))
        assert sig["typ"] == "PRILEZITOST"
        assert sig["dovera"] == pytest.approx(0.80)

    def test_bez_kontextu_dovera_065(self):
        sig = peer_signal(_p("Senec", 10000, 500), self._stats(50.0))
        assert sig["dovera"] == pytest.approx(0.65)

    def test_dovod_obsahuje_percento(self):
        sig = peer_signal(_p("Senec", 10000, 500), self._stats(50.0))  # 20/50 = -60%
        assert "60" in sig["dovod"]

    def test_peer_metadata(self):
        sig = peer_signal(_p("Senec", 10000, 500), self._stats(50.0, count=7))
        assert sig["peer_median_ppsm"] == pytest.approx(50.0)
        assert sig["peer_count"] == 7
        assert sig["peer_ratio"] < 1.0

    def test_struktura(self):
        sig = peer_signal(_p("Senec", 10000, 500), self._stats(50.0))
        assert {"kod", "typ", "nazov", "dovod", "dovera"} <= set(sig.keys())

    def test_bez_ceny_none(self):
        assert peer_signal(_p("Senec", 0, 500), self._stats(50.0)) is None


class TestApplyPeerSignals:

    def test_prazdny(self):
        assert apply_peer_signals([]) == []

    def test_malo_pozemkov_bez_signalu(self):
        parcels = [_p("Senec", 20000, 500) for _ in range(3)]
        apply_peer_signals(parcels)
        assert all(not any(s["kod"] == "LACNEJSI_AKO_OKOLIE"
                           for s in p["signals"]) for p in parcels)

    def test_lacny_dostane_signal(self):
        parcels = _lehnice(extra_ppsm=20.0)
        apply_peer_signals(parcels)
        lacny = next(p for p in parcels if p["price_per_sqm"] < 30)
        assert any(s["kod"] == "LACNEJSI_AKO_OKOLIE" for s in lacny["signals"])

    def test_drahy_bez_signalu(self):
        parcels = _lehnice()
        apply_peer_signals(parcels)
        assert all(not any(s["kod"] == "LACNEJSI_AKO_OKOLIE"
                           for s in p["signals"]) for p in parcels)

    def test_peer_metadata_pridana(self):
        parcels = _lehnice(extra_ppsm=20.0)
        apply_peer_signals(parcels)
        lacny = next(p for p in parcels if p["price_per_sqm"] < 30)
        assert lacny.get("peer_median_ppsm", 0) > 0
        assert lacny.get("peer_count", 0) >= 5

    def test_bez_duplikatu(self):
        parcels = _lehnice(extra_ppsm=20.0)
        apply_peer_signals(parcels)
        apply_peer_signals(parcels)  # 2×
        lacny = next(p for p in parcels if p["price_per_sqm"] < 30)
        n = sum(1 for s in lacny["signals"] if s["kod"] == "LACNEJSI_AKO_OKOLIE")
        assert n == 1

    def test_vracia_rovnaky_zoznam(self):
        parcels = _lehnice()
        assert apply_peer_signals(parcels) is parcels

    def test_rozne_obce_nezamiesaju(self):
        senec   = [_p("Senec",   50000, 500) for _ in range(4)]
        pezinok = [_p("Pezinok", 10000, 500) for _ in range(4)]
        apply_peer_signals(senec + pezinok)
        for p in senec:
            sig = next((s for s in p["signals"] if s["kod"] == "LACNEJSI_AKO_OKOLIE"), None)
            if sig:
                assert "Pezinok" not in sig["dovod"]

    def test_nulova_cena_preskoci(self):
        assert compute_obec_stats([_p("Senec", 0, 500) for _ in range(5)]) == {}

    def test_nulova_plocha_preskoci(self):
        assert compute_obec_stats([_p("Senec", 20000, 0) for _ in range(5)]) == {}

    def test_rozne_obce(self):
        s = compute_obec_stats([_p("Senec", 20000, 500)] * 4 +
                               [_p("Pezinok", 30000, 500)] * 4)
        assert "senec" in s and "pezinok" in s

    def test_ppsm_z_ceny_a_plochy(self):
        p = _p("Senec", 30000, 600)
        p["price_per_sqm"] = 0
        s = compute_obec_stats([p] + [_p("Senec", 30000, 600) for _ in range(3)])
        assert "senec" in s
        assert s["senec"].median_ppsm == pytest.approx(50.0)
