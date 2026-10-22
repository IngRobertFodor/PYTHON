"""
Testy - opportunity_service.py
================================
Testuje investment_index(), explain(), apply_opportunity().
100% offline.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "backend"))
import pytest
from services.opportunity_service import (
    investment_index, explain, apply_opportunity, _EXPLAIN_MIN_INDEX,
)


def _p(signals=None, confidence=1.0, profit=0.0,
       loc="Senec", price=20000.0, area=500.0) -> dict:
    return {
        "url": "http://t/1", "location_text": loc,
        "price_eur": price, "area_sqm": area,
        "price_per_sqm": price/area if area > 0 else 0,
        "preliminary_score": 70.0, "prelim_confidence": confidence,
        "prelim_missing": [], "prelim_breakdown": {},
        "signals": signals or [],
        "rezoning_profit_eur": profit,
        "investment_index": 0, "investment_summary": "",
    }


def _sig(kod, typ="PRILEZITOST", dovera=0.8):
    return {"kod": kod, "typ": typ, "nazov": kod, "dovod": "test", "dovera": dovera}


class TestInvestmentIndex:

    def test_nulovy_parcel_len_confidence(self):
        idx = investment_index(_p())
        assert 0 <= idx <= 20   # len confidence_pts = 15

    def test_rezoning_zisk_zvysuje(self):
        assert investment_index(_p(profit=50000)) > investment_index(_p())

    def test_horice_signal_zvysuje(self):
        assert investment_index(_p(signals=[_sig("HORICE")])) > investment_index(_p())

    def test_zaplava_znizuje(self):
        assert investment_index(_p(signals=[_sig("ZAPLAVA","RIZIKO")])) < investment_index(_p())

    def test_viac_signálov_viac_bodov(self):
        one = investment_index(_p(signals=[_sig("HORICE")]))
        two = investment_index(_p(signals=[_sig("HORICE"), _sig("LACNEJSI_AKO_OKOLIE")]))
        assert two >= one

    def test_lacnejsi_hazik_nerata(self):
        hazik = _sig("LACNEJSI_AKO_OKOLIE", "RIZIKO")
        pril  = _sig("LACNEJSI_AKO_OKOLIE", "PRILEZITOST")
        assert investment_index(_p(signals=[pril])) > investment_index(_p(signals=[hazik]))

    def test_nizka_confidence_znizuje(self):
        assert investment_index(_p(confidence=1.0)) > investment_index(_p(confidence=0.3))

    def test_range_0_100(self):
        for c in [_p(), _p(profit=1_000_000, signals=[_sig("HORICE")]),
                  _p(signals=[_sig("ZAPLAVA","RIZIKO"), _sig("CHRANENE_UZEMIE","RIZIKO")])]:
            assert 0 <= investment_index(c) <= 100

    def test_rezoning_plus_signaly(self):
        only_p = investment_index(_p(profit=100_000))
        only_s = investment_index(_p(signals=[_sig("HORICE")]))
        combo  = investment_index(_p(profit=100_000, signals=[_sig("HORICE")]))
        assert combo > only_p and combo > only_s

    def test_max_penalty_clip_to_zero(self):
        many = [_sig("ZAPLAVA","RIZIKO",1.0), _sig("CHRANENE_UZEMIE","RIZIKO",1.0),
                _sig("DRAHE_VYNATIE","RIZIKO",1.0), _sig("PRILIS_DALEKO","RIZIKO",1.0)]
        assert investment_index(_p(signals=many, confidence=1.0)) == 0

    def test_drazba_signal(self):
        assert investment_index(_p(signals=[_sig("DRAZBA_POD_ZNALECKOU",dovera=0.85)])) > investment_index(_p())

    def test_vrati_int(self):
        assert isinstance(investment_index(_p()), int)


class TestExplain:

    def test_nizky_index_prazdny(self):
        p = _p(confidence=0.1); p["investment_index"] = _EXPLAIN_MIN_INDEX - 1
        assert explain(p) == ""

    def test_obsahuje_lokalitu(self):
        p = _p(profit=50000, loc="Lehnice"); p["investment_index"] = 60
        assert "Lehnice" in explain(p)

    def test_obsahuje_profit(self):
        p = _p(profit=58000); p["investment_index"] = 60
        r = explain(p)
        assert "58" in r or "preklasifik" in r.lower()

    def test_riziko_upozornenie(self):
        p = _p(signals=[_sig("ZAPLAVA","RIZIKO")]); p["investment_index"] = 50
        r = explain(p)
        assert "\u26a0\ufe0f" in r or "Rizik" in r

    def test_bez_rizika_preverit(self):
        p = _p(profit=30000); p["investment_index"] = 50
        assert "Preveriť" in explain(p) or "preverit" in explain(p).lower()

    def test_vracia_string(self):
        assert isinstance(explain(_p()), str)


class TestPodielCap:

    def _podiel_sig(self):
        return {"kod": "PODIEL_ALEBO_CHYBNE_DATA", "typ": "RIZIKO",
                "nazov": "Pravdepodobne podiel", "dovod": "1 m² za 382 €", "dovera": 0.85}

    def test_cap_na_30(self):
        """Aj s veľkým rezoning profitom nesmie index presiahnuť 30."""
        p = _p(profit=500_000, signals=[self._podiel_sig()])
        assert investment_index(p) <= 30

    def test_cap_neovplyvni_normalnu_parcelu(self):
        """Bez PODIEL signálu cap neplatí."""
        p = _p(profit=500_000, signals=[_sig("HORICE")])
        assert investment_index(p) > 30

    def test_explain_obsahuje_varovanie(self):
        """explain() pri PODIEL signáli začína výstrahou."""
        p = _p(area=1.0, price=382.0, signals=[self._podiel_sig()])
        p["investment_index"] = 15
        r = explain(p)
        assert "podiel" in r.lower() or "⚠" in r

    def test_explain_podiel_pri_nizkom_indexe(self):
        """explain() vráti výstrahu aj keď index < _EXPLAIN_MIN_INDEX (výnimka pre PODIEL)."""
        p = _p(area=1.0, price=382.0, signals=[self._podiel_sig()])
        p["investment_index"] = 5
        r = explain(p)
        assert r != ""  # výstraha sa zobrazí vždy, nie len pri idx >= 30

        p = _p(profit=50000, signals=[_sig("HORICE")]); p["investment_index"] = 70
        assert isinstance(explain(p), str)


class TestApplyOpportunity:

    def test_prazdny(self):
        assert apply_opportunity([]) == []

    def test_plni_index(self):
        parcels = [_p(), _p(profit=80000, signals=[_sig("HORICE")])]
        apply_opportunity(parcels)
        assert all(isinstance(p["investment_index"], int) for p in parcels)

    def test_plni_summary(self):
        parcels = [_p(profit=80000, signals=[_sig("HORICE")])]
        apply_opportunity(parcels)
        assert isinstance(parcels[0]["investment_summary"], str)

    def test_zoradenie_silny_viac(self):
        p_s = _p(profit=100_000, signals=[_sig("HORICE")])
        p_w = _p()
        apply_opportunity([p_s, p_w])
        assert p_s["investment_index"] > p_w["investment_index"]

    def test_vracia_rovnaky_zoznam(self):
        parcels = [_p()]
        assert apply_opportunity(parcels) is parcels

    def test_viac_pozemkov_range(self):
        parcels = [_p(profit=i * 10000) for i in range(10)]
        apply_opportunity(parcels)
        assert all(0 <= p["investment_index"] <= 100 for p in parcels)
        assert parcels[-1]["investment_index"] >= parcels[0]["investment_index"]
