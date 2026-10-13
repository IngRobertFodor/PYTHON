"""
Testy - Rezoning service (kvantifikácia zisku z preklasifikácie)
100% offline, nula HTTP.
"""

import pytest
from models.parcel import Parcel
from models.result import ServiceResult
from services.rezoning_service import estimate_rezoning_profit, get_stavebna_cena_m2


def _sr(source, data):
    return ServiceResult(ok=True, score=80.0, data=data, source=source)

def _bpej(odvody=0.10, cls=7):
    return {"protection_class": cls, "estimated_odvody_eur_per_m2": odvody,
            "bpej_code": "07020", "high_cost_warning": cls<=4,
            "suitable_for_construction": cls>4}

def _overpass(elec_m=30.0, road_m=20.0):
    return {"electricity": {"distance_m": elec_m, "available": True},
            "road": {"distance_m": road_m, "type": "residential",
                     "width_m": 6, "accessible": True, "wide_enough": True},
            "village_position": {"position": "OKRAJ"},
            "direct_access":    {"level": "PRIAMA"}}

def _dist(km=25.0):
    return {"distance_km": km, "lat": 48.2, "lon": 17.4}

def _make_parcel(price=15000.0, area=600.0,
                 bpej=None, overpass=None, dist=None):
    p = Parcel(url="x", price_eur=price, area_sqm=area,
               source_portal="nehnutelnosti_sk",
               price_per_sqm=round(price/area,2) if area else 0,
               location_text="Senec")
    if bpej:     p.add_result(_sr("bpej_service",      bpej))
    if overpass: p.add_result(_sr("overpass_service",  overpass))
    if dist:     p.add_result(_sr("distance_service",  dist))
    return p


class TestEstimateRezoningProfit:

    def test_vracia_parcel(self):
        p = _make_parcel()
        result = estimate_rezoning_profit(p)
        assert result is p   # modifikuje in-place a vracia ten istý objekt

    def test_nastavuje_vsetky_polia(self):
        p = _make_parcel(bpej=_bpej(), overpass=_overpass(), dist=_dist())
        estimate_rezoning_profit(p)
        assert p.rezoning_profit_eur is not None
        assert p.rezoning_cost_eur is not None
        assert p.rezoning_value_eur is not None
        assert isinstance(p.rezoning_breakdown, dict)

    def test_hodnota_stavebna_je_kladna(self):
        p = _make_parcel(area=600, bpej=_bpej(), overpass=_overpass(), dist=_dist(25))
        estimate_rezoning_profit(p)
        assert p.rezoning_value_eur > 0

    def test_naklady_vynatie_correct(self):
        p = _make_parcel(area=600, bpej=_bpej(odvody=0.10), overpass=_overpass(), dist=_dist())
        estimate_rezoning_profit(p)
        assert p.rezoning_breakdown["naklad_vynatie_eur"] == pytest.approx(60.0, abs=1)

    def test_naklady_zasietovanie_correct(self):
        # elec 50 m: (50-10)*100=4000, road 30 m: (30-10)*120=2400 → 6400
        p = _make_parcel(bpej=_bpej(odvody=0.10), overpass=_overpass(50, 30), dist=_dist())
        estimate_rezoning_profit(p)
        assert p.rezoning_breakdown["naklad_zasietovanie_eur"] == pytest.approx(6400, abs=1)

    def test_zisk_je_hodnota_minus_naklady_minus_kupna(self):
        p = _make_parcel(price=10000, area=600,
                         bpej=_bpej(odvody=0.10), overpass=_overpass(10, 10), dist=_dist(25))
        estimate_rezoning_profit(p)
        bd = p.rezoning_breakdown
        assert p.rezoning_profit_eur == pytest.approx(
            bd["hodnota_stavebna_eur"] - 10000 - bd["naklad_celkom_eur"], abs=1)

    def test_lacna_orna_poda_blizko_ba_ziskova(self):
        p = _make_parcel(price=5000, area=600,
                         bpej=_bpej(odvody=0.10), overpass=_overpass(30, 20), dist=_dist(25))
        estimate_rezoning_profit(p)
        assert p.rezoning_profit_eur > 0, f"zisk={p.rezoning_profit_eur}"

    def test_draha_poda_daleko_stratova(self):
        p = _make_parcel(price=60000, area=600,
                         bpej=_bpej(odvody=3.0, cls=2),
                         overpass=_overpass(200, 150), dist=_dist(80))
        estimate_rezoning_profit(p)
        assert p.rezoning_profit_eur < 0, f"zisk={p.rezoning_profit_eur}"

    def test_bez_gis_dat_fallback(self):
        p = Parcel(url="x", price_eur=10000, area_sqm=600,
                   source_portal="nehnutelnosti_sk", location_text="Senec")
        estimate_rezoning_profit(p)
        assert p.rezoning_value_eur > 0
        assert p.rezoning_breakdown["confidence"] < 1.0

    def test_confidence_stupa_s_gis(self):
        p_bez = Parcel(url="x", price_eur=10000, area_sqm=600,
                       source_portal="nehnutelnosti_sk")
        estimate_rezoning_profit(p_bez)
        p_s = _make_parcel(bpej=_bpej(), overpass=_overpass(), dist=_dist())
        estimate_rezoning_profit(p_s)
        assert p_s.rezoning_breakdown["confidence"] > \
               p_bez.rezoning_breakdown["confidence"]

    def test_nulova_vymera_bezpecne(self):
        p = _make_parcel(area=0.0)
        estimate_rezoning_profit(p)
        assert p.rezoning_value_eur == 0.0

    def test_breakdown_poznamka(self):
        p = _make_parcel()
        estimate_rezoning_profit(p)
        assert "ORIENTACNE" in p.rezoning_breakdown.get("poznamka", "")


class TestGetStavebnaCenaM2:

    def test_blizko_ba_vyssia_cena(self):
        assert get_stavebna_cena_m2(10) > get_stavebna_cena_m2(40)

    def test_daleko_nizsia_cena(self):
        assert get_stavebna_cena_m2(200) <= get_stavebna_cena_m2(85)

    def test_vsetky_pasma_kladne(self):
        for km in [5, 20, 40, 70, 100]:
            assert get_stavebna_cena_m2(km) > 0

    def test_z_criteria_yaml(self):
        assert get_stavebna_cena_m2(25) > 0
