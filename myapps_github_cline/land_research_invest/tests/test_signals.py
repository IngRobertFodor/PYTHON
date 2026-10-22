"""
Testy - Investičné signály (signals.py)
========================================
Testuje gis_signals() a preliminary_signals() s PRESNÝM tvarom
ServiceResult.data z každej GIS služby (overene zo zdrojoveho kodu sluzieb).
100% offline, nula HTTP.
"""

import pytest
from models.parcel import Parcel
from models.result import ServiceResult
from services.signals import gis_signals, preliminary_signals, merge_signals, history_signals, drazba_signals


# ----------------------------------------------------------------
# Pomocné továrne — tvar data PRESNE podla zdrojoveho kodu sluzieb
# ----------------------------------------------------------------

def _bpej_data(protection_class: int, odvody: float = None) -> dict:
    """Tvar presne podla bpej_service.check() -> ServiceResult.data"""
    if odvody is None:
        from services.bpej_service import ODVODY_PER_CLASS
        odvody = ODVODY_PER_CLASS.get(protection_class, 0.0)
    return {
        "bpej_code": f"0{protection_class}020",
        "protection_class": protection_class,
        "estimated_odvody_eur_per_m2": odvody,
        "high_cost_warning": protection_class <= 4,
        "suitable_for_construction": protection_class > 4,
    }


def _zbgis_data(is_agricultural: bool = True, is_buildable: bool = False,
                druh: str = "orna_poda") -> dict:
    """Tvar presne podla zbgis_service.check() -> ServiceResult.data"""
    return {
        "area_sqm": 600.0, "width_m": 25.0, "length_m": 24.0,
        "shape_regularity": 0.9, "meets_min_area": True, "meets_min_width": True,
        "parcel_number": "1234/1", "druh_pozemku": druh,
        "druh_pozemku_raw": "Orná pôda",
        "is_agricultural": is_agricultural, "is_buildable": is_buildable,
    }


def _overpass_data(position: str = "OKRAJ", access: str = "PRIAMA",
                   elec_dist: float = 30.0, road_dist: float = 20.0) -> dict:
    """Tvar presne podla overpass_service._analyze_elements().
    KRITICKY: village_position a direct_access su VNORENE dicts!
    """
    return {
        "road":        {"distance_m": road_dist, "type": "residential",
                        "width_m": 6, "accessible": True, "wide_enough": True},
        "electricity": {"distance_m": elec_dist, "available": elec_dist <= 200},
        "water":       {"distance_m": 50.0, "available": True},
        "pipeline_gas": {"distance_m": 200.0, "nearby": False},
        "forest_buffer": {"distance_m": 120.0, "safe": True},
        "noise": {"motorway_distance_m": 500.0, "railway_distance_m": 300.0,
                  "motorway_safe": True, "railway_safe": True},
        "environment": {"landfill_distance_m": 600.0, "industrial_distance_m": 400.0,
                        "landfill_safe": True, "industrial_safe": True},
        "buildings": {"nearest_m": 30, "count_100m": 5, "count_300m": 15},
        "village_position": {"position": position, "reason": "test",
                             "count_100m": 5, "count_300m": 15},
        "direct_access":    {"level": access, "reason": "test",
                             "building_m": 30, "road_m": 20},
        "is_gem_candidate": (position == "OKRAJ" and access in ("PRIAMA", "CIASTOCNA")),
    }


def _flood_data(in_flood: bool = False) -> dict:
    """Tvar presne podla flood_service.check() -> ServiceResult.data.
    KRITICKY: klic je in_flood_zone_q100, NIE flood_zone_q100!
    """
    return {
        "in_flood_zone_q100": in_flood,
        "risk_level": "HIGH" if in_flood else "NONE",
        "lat": 48.2, "lon": 17.3,
    }


def _protected_data(natura: bool = False, chko: bool = False,
                    npr_pr: bool = False, np_: bool = False) -> dict:
    """Tvar presne podla protected_service.check() -> ServiceResult.data.
    KRITICKY: in_natura2000, in_chko (nie natura2000, chko!)
    """
    return {
        "in_natura2000": natura,
        "in_chko":       chko,
        "in_npr_pr":     npr_pr,
        "in_np":         np_,
        "findings":      {},
        "any_protected": any([natura, chko, npr_pr, np_]),
    }


def _price_data(price_per_sqm: float = 10.0, local_avg: float = 50.0) -> dict:
    """Tvar presne podla price_analysis_service.check() -> ServiceResult.data.
    KRITICKY: price_ratio a local_avg_per_sqm (nie median_ppsm!)
    """
    ratio = round(price_per_sqm / local_avg, 3) if local_avg > 0 else 1.0
    return {
        "price_eur": price_per_sqm * 600,
        "area_sqm": 600.0,
        "price_per_sqm": price_per_sqm,
        "local_avg_per_sqm": local_avg,
        "price_ratio": ratio,
        "is_underpriced": ratio <= 0.8,
        "is_overpriced": ratio > 1.2,
        "listing_age_days": 0,
        "price_drop_pct": 0.0,
        "seller_motivated": False,
        "used_fallback_avg": True,
    }




# ----------------------------------------------------------------
# BLOK 1: Testy kľúčov — regresia voči bug #1-#4
# ----------------------------------------------------------------

class TestGisSignalsKluce:
    """Každý test overuje PRESNE jeden kľúč."""

    def test_overpass_position_vnoreny_kluc(self):
        p = _make_parcel_with_gis(bpej=_bpej_data(7), zbgis=_zbgis_data(True),
                                  overpass=_overpass_data("OKRAJ","PRIAMA"))
        assert "PREKLASIFIKACIA" in [s["kod"] for s in gis_signals(p)], \
            "Bug: village_position.position nefunguje"

    def test_overpass_access_vnoreny_kluc(self):
        p = _make_parcel_with_gis(bpej=_bpej_data(7), zbgis=_zbgis_data(True),
                                  overpass=_overpass_data("OKRAJ","CIASTOCNA"))
        assert "PREKLASIFIKACIA" in [s["kod"] for s in gis_signals(p)], \
            "Bug: direct_access.level nefunguje"

    def test_flood_klic_in_flood_zone_q100(self):
        p = _make_parcel_with_gis(flood=_flood_data(in_flood=True))
        assert "ZAPLAVA" in [s["kod"] for s in gis_signals(p)], \
            "Bug: in_flood_zone_q100 nefunguje"

    def test_protected_klic_in_natura2000(self):
        p = _make_parcel_with_gis(protected=_protected_data(natura=True))
        assert "CHRANENE_UZEMIE" in [s["kod"] for s in gis_signals(p)], \
            "Bug: in_natura2000 nefunguje"

    def test_protected_klic_in_chko(self):
        p = _make_parcel_with_gis(protected=_protected_data(chko=True))
        assert "CHRANENE_UZEMIE" in [s["kod"] for s in gis_signals(p)]

    def test_price_klic_price_ratio(self):
        # ratio=0.20 < 0.30 → PODHODNOTENE
        p = _make_parcel_with_gis(
            price=_price_data(price_per_sqm=10.0, local_avg=50.0))
        assert "PODHODNOTENE" in [s["kod"] for s in gis_signals(p)], \
            "Bug: price_ratio/local_avg_per_sqm nefunguje"


# ----------------------------------------------------------------
# Testy logiky signálov
# ----------------------------------------------------------------

class TestGisSignalsLogika:

    def test_preklasifikacia_vsetky_podmienky(self):
        p = _make_parcel_with_gis(bpej=_bpej_data(7), zbgis=_zbgis_data(True),
                                  overpass=_overpass_data("OKRAJ","PRIAMA"))
        kody = [s["kod"] for s in gis_signals(p)]
        assert "PREKLASIFIKACIA" in kody
        assert "LACNE_VYNATIE"   in kody

    def test_preklasifikacia_stred_nespusti(self):
        p = _make_parcel_with_gis(bpej=_bpej_data(7), zbgis=_zbgis_data(True),
                                  overpass=_overpass_data("STRED","PRIAMA"))
        assert not any(s["kod"] == "PREKLASIFIKACIA" for s in gis_signals(p))

    def test_preklasifikacia_mimo_nespusti(self):
        p = _make_parcel_with_gis(bpej=_bpej_data(7), zbgis=_zbgis_data(True),
                                  overpass=_overpass_data("MIMO","PRIAMA"))
        assert not any(s["kod"] == "PREKLASIFIKACIA" for s in gis_signals(p))

    def test_preklasifikacia_ziadna_nespusti(self):
        p = _make_parcel_with_gis(bpej=_bpej_data(7), zbgis=_zbgis_data(True),
                                  overpass=_overpass_data("OKRAJ","ZIADNA"))
        assert not any(s["kod"] == "PREKLASIFIKACIA" for s in gis_signals(p))

    def test_preklasifikacia_bpej3_nespusti_ale_drahe(self):
        p = _make_parcel_with_gis(bpej=_bpej_data(3), zbgis=_zbgis_data(True),
                                  overpass=_overpass_data("OKRAJ","PRIAMA"))
        kody = [s["kod"] for s in gis_signals(p)]
        assert "PREKLASIFIKACIA" not in kody
        assert "DRAHE_VYNATIE"   in kody

    def test_stavebny_pozemok_nema_preklasifikacia(self):
        p = _make_parcel_with_gis(bpej=_bpej_data(9),
                                  zbgis=_zbgis_data(is_agricultural=False),
                                  overpass=_overpass_data("OKRAJ","PRIAMA"))
        assert not any(s["kod"] == "PREKLASIFIKACIA" for s in gis_signals(p))

    def test_zaplava_false_nespusti(self):
        p = _make_parcel_with_gis(flood=_flood_data(in_flood=False))
        assert not any(s["kod"] == "ZAPLAVA" for s in gis_signals(p))

    def test_chranene_np(self):
        p = _make_parcel_with_gis(protected=_protected_data(np_=True))
        assert "CHRANENE_UZEMIE" in [s["kod"] for s in gis_signals(p)]

    def test_podhodnotene_ratio_nad_limitom_nespusti(self):
        # ratio=0.80 > 0.30 → nespustí
        p = _make_parcel_with_gis(
            price=_price_data(price_per_sqm=40.0, local_avg=50.0))
        assert not any(s["kod"] == "PODHODNOTENE" for s in gis_signals(p))

    def test_dovera_priama_vyssia_nez_ciastocna(self):
        def _dov(acc):
            p = _make_parcel_with_gis(bpej=_bpej_data(7), zbgis=_zbgis_data(True),
                                      overpass=_overpass_data("OKRAJ", acc))
            return next(s["dovera"] for s in gis_signals(p)
                        if s["kod"] == "PREKLASIFIKACIA")
        assert _dov("PRIAMA") > _dov("CIASTOCNA")

    def test_prazdne_data_nevyhodi_vynimku(self):
        p = Parcel(url="x", price_eur=5000, area_sqm=600,
                   source_portal="nehnutelnosti_sk")
        assert isinstance(gis_signals(p), list)

    def test_kazdy_signal_ma_spravnu_strukturu(self):
        p = _make_parcel_with_gis(bpej=_bpej_data(7), zbgis=_zbgis_data(True),
                                  overpass=_overpass_data("OKRAJ","PRIAMA"),
                                  flood=_flood_data(False))
        for sig in gis_signals(p):
            assert {"kod","typ","nazov","dovod","dovera"} <= set(sig.keys())
            assert sig["typ"] in ("PRILEZITOST","RIZIKO")
            assert 0.0 <= sig["dovera"] <= 1.0

# ----------------------------------------------------------------
# Testy preliminary_signals
# ----------------------------------------------------------------

class TestPrelimSignals:

    def _p(self, price=5000.0, area=600.0, source="nehnutelnosti_sk",
           ppsm=0.0, location="Senec"):
        return Parcel(url="x", price_eur=price, area_sqm=area,
                      source_portal=source, price_per_sqm=ppsm,
                      location_text=location)

    def test_blizko_ba_senec(self):
        kody = [s["kod"] for s in preliminary_signals(self._p(location="Senec"))]
        assert "BLIZKO_BA" in kody

    def test_prilis_daleko_kosice(self):
        kody = [s["kod"] for s in preliminary_signals(self._p(location="Košice"))]
        assert "PRILIS_DALEKO" in kody

    def test_cena_podozriva_inzerat(self):
        p = self._p(source="nehnutelnosti_sk", price=500, area=600, ppsm=0.83)
        kody = [s["kod"] for s in preliminary_signals(p)]
        assert "CENA_PODOZRIVA" in kody

    def test_cena_podozriva_drazba_nie(self):
        p = self._p(source="ske_drazobne_vyhlasky", price=500, area=600, ppsm=0.83)
        assert not any(s["kod"] == "CENA_PODOZRIVA" for s in preliminary_signals(p))

    def test_drazba_podhodnotena(self):
        p = self._p(source="ske_drazobne_vyhlasky", price=8000)
        kody = [s["kod"] for s in preliminary_signals(p)]
        assert "DRAZBA_PODHODNOTENA" in kody

    def test_kazdy_signal_ma_spravnu_strukturu(self):
        p = self._p(source="ske_drazobne_vyhlasky", price=8000, location="Senec")
        for sig in preliminary_signals(p):
            assert {"kod","typ","nazov","dovod","dovera"} <= set(sig.keys())
            assert sig["typ"] in ("PRILEZITOST","RIZIKO")
            assert 0.0 <= sig["dovera"] <= 1.0


# ----------------------------------------------------------------
# Test merge_signals
# ----------------------------------------------------------------

class TestMergeSignals:
    pass


# ----------------------------------------------------------------
# B1 — Testy history_signals (motivovaný predajca)
# ----------------------------------------------------------------

def _hist_parcel(age_days: int = 0, drop_pct: float = 0.0,
                 history: list = None) -> Parcel:
    p = Parcel(url="x", price_eur=10000, area_sqm=500,
               source_portal="nehnutelnosti_sk")
    p.listing_age_days = age_days
    p.price_drop_pct   = drop_pct
    p.price_history    = history or []
    return p


class TestHistorySignals:

    def test_ziadne_signaly_novy_pozemok(self):
        p = _hist_parcel(age_days=0, drop_pct=0.0)
        assert history_signals(p) == []

    def test_dlho_v_ponuke_spusti_sa(self):
        p = _hist_parcel(age_days=130, drop_pct=0.0)
        kody = [s["kod"] for s in history_signals(p)]
        assert "DLHO_V_PONUKE" in kody

    def test_dlho_v_ponuke_tesne_pod_prahom(self):
        p = _hist_parcel(age_days=119, drop_pct=0.0)
        assert history_signals(p) == []

    def test_cena_klesa_spusti_sa(self):
        hist = [{"date": "2025-01-01T00:00:00+00:00", "price_eur": 10000},
                {"date": "2025-06-01T00:00:00+00:00", "price_eur": 9000}]
        p = _hist_parcel(age_days=50, drop_pct=10.0, history=hist)
        kody = [s["kod"] for s in history_signals(p)]
        assert "CENA_KLESA" in kody

    def test_cena_klesa_tesne_pod_prahom(self):
        p = _hist_parcel(age_days=50, drop_pct=4.9)
        assert not any(s["kod"] == "CENA_KLESA" for s in history_signals(p))

    def test_horice_kombinacia_dlho_aj_pokles(self):
        """age >= 180 + drop >= 5 → HORICE, nie DLHO + CENA zvlášť."""
        hist = [{"date": "2025-01-01T00:00:00+00:00", "price_eur": 45000},
                {"date": "2025-06-01T00:00:00+00:00", "price_eur": 38000}]
        p = _hist_parcel(age_days=243, drop_pct=15.6, history=hist)
        kody = [s["kod"] for s in history_signals(p)]
        assert "HORICE" in kody
        assert "DLHO_V_PONUKE" not in kody
        assert "CENA_KLESA" not in kody

    def test_horice_len_dlho_bez_poklesu_nespusti(self):
        p = _hist_parcel(age_days=243, drop_pct=0.0)
        kody = [s["kod"] for s in history_signals(p)]
        assert "HORICE" not in kody
        assert "DLHO_V_PONUKE" in kody

    def test_horice_len_pokles_bez_veku_nespusti(self):
        hist = [{"date": "2025-01-01T00:00:00+00:00", "price_eur": 10000},
                {"date": "2025-03-01T00:00:00+00:00", "price_eur": 8500}]
        p = _hist_parcel(age_days=50, drop_pct=15.0, history=hist)
        kody = [s["kod"] for s in history_signals(p)]
        assert "HORICE" not in kody
        assert "CENA_KLESA" in kody

    def test_struktury_signalu_su_spravne(self):
        hist = [{"date": "2025-01-01T00:00:00+00:00", "price_eur": 10000},
                {"date": "2025-06-01T00:00:00+00:00", "price_eur": 9000}]
        p = _hist_parcel(age_days=200, drop_pct=10.0, history=hist)
        for sig in history_signals(p):
            assert {"kod", "typ", "nazov", "dovod", "dovera"} <= set(sig.keys())
            assert sig["typ"] == "PRILEZITOST"
            assert 0.0 <= sig["dovera"] <= 1.0

    def test_dovod_obsahuje_percentualny_pokles(self):
        hist = [{"date": "2025-01-01T00:00:00+00:00", "price_eur": 50000},
                {"date": "2025-09-01T00:00:00+00:00", "price_eur": 42500}]
        p = _hist_parcel(age_days=50, drop_pct=15.0, history=hist)
        klesa = next(s for s in history_signals(p) if s["kod"] == "CENA_KLESA")
        assert "15" in klesa["dovod"]

    def test_horice_dovera_rastie_s_vekom(self):
        def _dov(age):
            hist = [{"date": "d", "price_eur": 10000}, {"date": "d2", "price_eur": 8000}]
            p = _hist_parcel(age_days=age, drop_pct=20.0, history=hist)
            return next((s["dovera"] for s in history_signals(p)
                         if s["kod"] == "HORICE"), 0)
        assert _dov(365) > _dov(180)

    def test_cena_klesa_text_viacnasobny_pokles(self):
        hist = [
            {"date": "2025-01-01T00:00:00+00:00", "price_eur": 50000},
            {"date": "2025-04-01T00:00:00+00:00", "price_eur": 45000},
            {"date": "2025-09-01T00:00:00+00:00", "price_eur": 40000},
        ]
        p = _hist_parcel(age_days=50, drop_pct=20.0, history=hist)
        klesa = next((s for s in history_signals(p) if s["kod"] == "CENA_KLESA"), None)
        assert klesa is not None
        assert "2\u00d7" in klesa["dovod"]


# ----------------------------------------------------------------
# B2 — Testy drazba_signals
# ----------------------------------------------------------------

def _draz_parcel(vyv: float = 0, znal: float = 0,
                 kolo: int = 0, source: str = "ske_drazobne_vyhlasky") -> Parcel:
    p = Parcel(url="x", price_eur=vyv, area_sqm=500, source_portal=source)
    p.vyvolavacia_cena_eur = vyv
    p.znalecka_hodnota_eur = znal
    p.drazba_kolo          = kolo
    return p


class TestDrazbaSignals:

    def test_ziadny_signal_bez_dat(self):
        p = _draz_parcel(vyv=0, znal=0, kolo=0)
        assert drazba_signals(p) == []

    def test_pod_znaleckou_spusti_sa(self):
        """vyv=70000, znal=100000 → 30 % zľava ≥ 20 % → DRAZBA_POD_ZNALECKOU."""
        p = _draz_parcel(vyv=70000, znal=100000, kolo=1)
        kody = [s["kod"] for s in drazba_signals(p)]
        assert "DRAZBA_POD_ZNALECKOU" in kody

    def test_pod_znaleckou_tesne_pod_prahom(self):
        """vyv=82000, znal=100000 → 18 % < 20 % → žiadny signál."""
        p = _draz_parcel(vyv=82000, znal=100000, kolo=1)
        assert not any(s["kod"] == "DRAZBA_POD_ZNALECKOU" for s in drazba_signals(p))

    def test_znalecka_nizsia_nez_vyvolavacia(self):
        """Ak znalecká < vyvolávacia → žiadny signál (nezvyčajné, ale nemá crashovať)."""
        p = _draz_parcel(vyv=50000, znal=30000, kolo=1)
        assert not any(s["kod"] == "DRAZBA_POD_ZNALECKOU" for s in drazba_signals(p))

    def test_bez_znaleckej_ziadny_pod_znaleckou(self):
        """OV/notárske: znalecká = 0 → DRAZBA_POD_ZNALECKOU sa nespustí."""
        p = _draz_parcel(vyv=50000, znal=0, kolo=1)
        assert not any(s["kod"] == "DRAZBA_POD_ZNALECKOU" for s in drazba_signals(p))

    def test_opakovana_drazba_kolo2(self):
        """kolo=2, bez znaleckej → DRAZBA_OPAKOVANA."""
        p = _draz_parcel(vyv=50000, znal=0, kolo=2)
        kody = [s["kod"] for s in drazba_signals(p)]
        assert "DRAZBA_OPAKOVANA" in kody

    def test_opakovana_s_znaleckou_len_pod_znaleckou(self):
        """kolo=2 + vyv pod znaleckou → iba DRAZBA_POD_ZNALECKOU (nie aj DRAZBA_OPAKOVANA)."""
        p = _draz_parcel(vyv=60000, znal=100000, kolo=2)
        kody = [s["kod"] for s in drazba_signals(p)]
        assert "DRAZBA_POD_ZNALECKOU" in kody
        assert "DRAZBA_OPAKOVANA" not in kody

    def test_pod_znaleckou_kolo2_vyssia_dovera(self):
        """Opakovaná dražba pod znaleckou → dôvera vyššia ako prvé kolo."""
        def _dov(kolo):
            p = _draz_parcel(vyv=60000, znal=100000, kolo=kolo)
            return next(s["dovera"] for s in drazba_signals(p)
                        if s["kod"] == "DRAZBA_POD_ZNALECKOU")
        assert _dov(2) > _dov(1)

    def test_dovod_obsahuje_percento_zlavy(self):
        p = _draz_parcel(vyv=70000, znal=100000, kolo=1)
        sig = next(s for s in drazba_signals(p) if s["kod"] == "DRAZBA_POD_ZNALECKOU")
        assert "30" in sig["dovod"]

    def test_dovod_obsahuje_obe_ceny(self):
        p = _draz_parcel(vyv=70000, znal=100000, kolo=1)
        sig = next(s for s in drazba_signals(p) if s["kod"] == "DRAZBA_POD_ZNALECKOU")


# ----------------------------------------------------------------
# TestPodielSignal — sanity check pre podiely a chybné dáta
# ----------------------------------------------------------------

def _prelim_parcel(price: float, area: float, source: str = "nehnutelnosti_sk") -> "Parcel":
    p = Parcel(url=f"https://test/{price}/{area}")
    p.price_eur   = price
    p.area_sqm    = area
    p.source_portal = source
    p.location_text = "Senec"
    return p


class TestPodielSignal:

    def test_mala_vymera_triggeruje(self):
        """area < 100 m² → PODIEL_ALEBO_CHYBNE_DATA"""
        p = _prelim_parcel(price=5000, area=1)
        kody = [s["kod"] for s in preliminary_signals(p)]
        assert "PODIEL_ALEBO_CHYBNE_DATA" in kody

    def test_mala_cena_a_mala_vymera_triggeruje(self):
        """price < 500 € AND area < 50 m² → trigger"""
        p = _prelim_parcel(price=380, area=9)
        kody = [s["kod"] for s in preliminary_signals(p)]
        assert "PODIEL_ALEBO_CHYBNE_DATA" in kody

    def test_normalna_parcela_netriggeruje(self):
        """Bežná parcela 800 m², 25 000 € → žiadny PODIEL signál"""
        p = _prelim_parcel(price=25000, area=800)
        kody = [s["kod"] for s in preliminary_signals(p)]
        assert "PODIEL_ALEBO_CHYBNE_DATA" not in kody

    def test_hranicna_vymera_presne_100(self):
        """area == 100 m² → NEtriggeruje (< 100, nie <=)"""
        p = _prelim_parcel(price=5000, area=100)
        kody = [s["kod"] for s in preliminary_signals(p)]
        assert "PODIEL_ALEBO_CHYBNE_DATA" not in kody

    def test_typ_je_riziko(self):
        p = _prelim_parcel(price=380, area=1)
        sig = next(s for s in preliminary_signals(p) if s["kod"] == "PODIEL_ALEBO_CHYBNE_DATA")
        assert sig["typ"] == "RIZIKO"

    def test_dovod_obsahuje_vymeru_a_cenu(self):
        p = _prelim_parcel(price=382, area=1)
        sig = next(s for s in preliminary_signals(p) if s["kod"] == "PODIEL_ALEBO_CHYBNE_DATA")
        assert "382" in sig["dovod"] and "1" in sig["dovod"]

    def test_drazobny_zdroj_tiez_triggeruje(self):
        """SKE dražba s 1 m² → trigger nezávisle od zdroja"""
        p = _prelim_parcel(price=723, area=1, source="ske_drazobne_vyhlasky")
        kody = [s["kod"] for s in preliminary_signals(p)]
        assert "PODIEL_ALEBO_CHYBNE_DATA" in kody

    def test_je_prvy_signal(self):
        """PODIEL signál musí byť prvý v zozname (pred BLIZKO_BA atď.)"""
        p = _prelim_parcel(price=380, area=1)
        sigs = preliminary_signals(p)
        assert sigs[0]["kod"] == "PODIEL_ALEBO_CHYBNE_DATA"

    def test_struktura_signalu_spravna(self):
        p = _draz_parcel(vyv=70000, znal=100000, kolo=1)
        for sig in drazba_signals(p):
            assert {"kod", "typ", "nazov", "dovod", "dovera"} <= set(sig.keys())
            assert sig["typ"] == "PRILEZITOST"
            assert 0.0 <= sig["dovera"] <= 1.0

    def test_kolo1_bez_znaleckej_nic(self):
        """kolo=1 bez znaleckej → žiadny signál."""
        p = _draz_parcel(vyv=50000, znal=0, kolo=1)
        assert drazba_signals(p) == []

    def test_kolo0_bez_dat_nic(self):
        p = _draz_parcel(vyv=0, znal=0, kolo=0)
        assert drazba_signals(p) == []

        hist = [
            {"date": "2025-01-01T00:00:00+00:00", "price_eur": 50000},
            {"date": "2025-04-01T00:00:00+00:00", "price_eur": 45000},
            {"date": "2025-09-01T00:00:00+00:00", "price_eur": 40000},
        ]
        p = _hist_parcel(age_days=50, drop_pct=20.0, history=hist)
        klesa = next((s for s in history_signals(p) if s["kod"] == "CENA_KLESA"), None)
        assert klesa is not None
        assert "2×" in klesa["dovod"]

    def test_dlho_nazov_obsahuje_mesiace(self):
        p = _hist_parcel(age_days=150, drop_pct=0.0)
        dlho = next(s for s in history_signals(p) if s["kod"] == "DLHO_V_PONUKE")
        assert "mes." in dlho["nazov"]

    def test_prazdne_history_nepadne(self):
        p = _hist_parcel(age_days=200, drop_pct=20.0, history=[])
        assert isinstance(history_signals(p), list)

    def test_gis_prepise_prelim_rovnaky_kod(self):
        prelim = [{"kod":"BLIZKO_BA","typ":"PRILEZITOST","nazov":"old","dovod":"p","dovera":0.5}]
        gis    = [{"kod":"BLIZKO_BA","typ":"PRILEZITOST","nazov":"new","dovod":"g","dovera":0.9}]
        merged = merge_signals(prelim, gis)
        assert len(merged) == 1
        assert merged[0]["dovod"] == "g"
        assert merged[0]["dovera"] == 0.9

    def test_zachova_unikatne(self):
        prelim = [{"kod":"CENA_PODOZRIVA","typ":"RIZIKO","nazov":"x","dovod":"p","dovera":0.8}]
        gis    = [{"kod":"ZAPLAVA","typ":"RIZIKO","nazov":"y","dovod":"g","dovera":0.9}]
        merged = merge_signals(prelim, gis)
        assert len(merged) == 2
        assert {s["kod"] for s in merged} == {"CENA_PODOZRIVA","ZAPLAVA"}

    def test_prazdne_zoznamy(self):
        assert merge_signals([], []) == []
        assert len(merge_signals([{"kod":"A","typ":"RIZIKO","nazov":"n","dovod":"d","dovera":0.5}], [])) == 1

        # ratio=0.80 > 0.30 → nespustí
        p = _make_parcel_with_gis(
            price=_price_data(price_per_sqm=40.0, local_avg=50.0))
        assert not any(s["kod"] == "PODHODNOTENE" for s in gis_signals(p))

    def test_dovera_priama_vyssia_nez_ciastocna(self):
        def _dov(acc):
            p = _make_parcel_with_gis(bpej=_bpej_data(7), zbgis=_zbgis_data(True),
                                      overpass=_overpass_data("OKRAJ", acc))
            return next(s["dovera"] for s in gis_signals(p) if s["kod"] == "PREKLASIFIKACIA")
        assert _dov("PRIAMA") > _dov("CIASTOCNA")

    def test_prazdne_data_nevyhodi_vynimku(self):
        p = Parcel(url="x", price_eur=5000, area_sqm=600, source_portal="nehnutelnosti_sk")
        assert isinstance(gis_signals(p), list)

    def test_kazdy_signal_ma_spravnu_strukturu(self):
        p = _make_parcel_with_gis(bpej=_bpej_data(7), zbgis=_zbgis_data(True),
                                  overpass=_overpass_data("OKRAJ","PRIAMA"),
                                  flood=_flood_data(False))
        for sig in gis_signals(p):
            assert {"kod","typ","nazov","dovod","dovera"} <= set(sig.keys())
            assert sig["typ"] in ("PRILEZITOST","RIZIKO")
            assert 0.0 <= sig["dovera"] <= 1.0


def _make_parcel_with_gis(price_eur=6000.0, area=600.0,
                           bpej=None, zbgis=None, overpass=None,
                           flood=None, protected=None, price=None) -> Parcel:
    """Parcel s GIS výsledkami — každý ServiceResult.data má reálny tvar."""
    p = Parcel(url="http://t.sk/1", price_eur=price_eur, area_sqm=area,
               source_portal="nehnutelnosti_sk",
               price_per_sqm=round(price_eur / area, 2) if area else 0)

    def _sr(source, data, score=80.0):
        return ServiceResult(ok=True, score=score, data=data, source=source)

    if bpej:      p.add_result(_sr("bpej_service",           bpej))
    if zbgis:     p.add_result(_sr("zbgis_service",          zbgis))
    if overpass:  p.add_result(_sr("overpass_service",       overpass))
    if flood:     p.add_result(_sr("flood_service",          flood))
    if protected: p.add_result(_sr("protected_service",      protected))
    if price:     p.add_result(_sr("price_analysis_service", price))
    return p
