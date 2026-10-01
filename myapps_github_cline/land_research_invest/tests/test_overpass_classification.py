import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "backend"))
import pytest
from unittest.mock import patch
from services.overpass_service import (
    classify_access, classify_position, is_gem_candidate,
    _count_within, _analyze_elements, _calculate_score,
)

LAT, LON = 48.2195, 17.3976
NEAR, MID, FAR = 0.0004, 0.001, 0.003

def node(la, lo, tag, v): return {"type":"node","lat":la,"lon":lo,"tags":{tag:v}}
def way(la, lo, tag, v):  return {"type":"way","center":{"lat":la,"lon":lo},"tags":{tag:v}}
def bld(la, lo):   return node(la, lo, "building", "yes")
def bway(la, lo):  return way(la, lo, "building", "yes")
def road(la, lo):  return node(la, lo, "highway", "residential")

DCFG = {"direct_access":{"full_m":50,"partial_m":150},
        "village_position":{"core_count_100m":30,"edge_min_count_300m":3}}

def mk(bn, c1, c3, rd):
    return {"buildings":{"nearest_m":bn,"count_100m":c1,"count_300m":c3},
            "road":{"distance_m":rd}}

def CFG(k):
    return {
        "infrastructure":{"road":{"min_width_m":6},"electricity":{"max_distance_m":200},"water":{"max_distance_m":200}},
        "protected_zones":{"forest_buffer_m":50},
        "environment":{"landfill_buffer_m":500,"industrial_buffer_m":300},
        "noise":{"min_highway_distance_m":50,"max_railway_distance_m":150},
        "access_classification":DCFG,
    }.get(k, {})
class TestCountWithin:
    def test_two_nearby(self):
        assert _count_within([bld(LAT+NEAR,LON),bld(LAT+NEAR,LON+NEAR)],LAT,LON,"building",100)==2
    def test_excludes_far(self):
        assert _count_within([bld(LAT+FAR,LON)],LAT,LON,"building",100)==0
    def test_empty(self):
        assert _count_within([],LAT,LON,"building",100)==0
    def test_wrong_tag(self):
        assert _count_within([road(LAT+NEAR,LON)],LAT,LON,"building",100)==0
    def test_way_center(self):
        assert _count_within([bway(LAT+NEAR,LON)],LAT,LON,"building",100)==1
    def test_300m_wider(self):
        els=[bld(LAT+NEAR,LON),bld(LAT+MID,LON),bld(LAT+FAR,LON)]
        assert _count_within(els,LAT,LON,"building",300)==2
        assert _count_within(els,LAT,LON,"building",100)==1
class TestClassifyAccess:
    def test_priama(self):      assert classify_access(mk(30,5,10,20),DCFG)["level"]=="PRIAMA"
    def test_ciastocna(self):   assert classify_access(mk(80,3,8,90),DCFG)["level"]=="CIASTOCNA"
    def test_ziadna_no_bld(self):
        r=classify_access(mk(None,0,0,200),DCFG); assert r["level"]=="ZIADNA"
        assert "ziadne domy" in r["reason"]
    def test_ziadna_far_bld(self): assert classify_access(mk(200,0,2,180),DCFG)["level"]=="ZIADNA"
    def test_ziadna_far_road(self):assert classify_access(mk(40,5,10,300),DCFG)["level"]=="ZIADNA"
    def test_building_m(self):  r=classify_access(mk(25,5,12,30),DCFG); assert r["building_m"]==25
    def test_road_m(self):      r=classify_access(mk(25,5,12,30),DCFG); assert r["road_m"]==30
    def test_road_m_none(self): assert classify_access(mk(30,5,10,9999),DCFG)["road_m"] is None
    def test_custom_thresh(self):
        cfg={"direct_access":{"full_m":100,"partial_m":300},"village_position":{}}
        assert classify_access(mk(80,5,10,90),cfg)["level"]=="PRIAMA"
class TestClassifyPosition:
    def test_stred(self):  assert classify_position(mk(5,45,120,5),DCFG)["position"]=="STRED"
    def test_okraj(self):  assert classify_position(mk(60,5,15,60),DCFG)["position"]=="OKRAJ"
    def test_mimo_empty(self): assert classify_position(mk(None,0,0,9999),DCFG)["position"]=="MIMO"
    def test_mimo_few(self):   assert classify_position(mk(250,0,1,300),DCFG)["position"]=="MIMO"
    def test_counts(self):
        r=classify_position(mk(40,8,20,40),DCFG); assert r["count_100m"]==8; assert r["count_300m"]==20
    def test_exact_stred(self): assert classify_position(mk(5,30,60,5),DCFG)["position"]=="STRED"
    def test_exact_okraj(self): assert classify_position(mk(60,2,3,60),DCFG)["position"]=="OKRAJ"
class TestIsGemCandidate:
    def _a(self,l): return {"level":l}
    def _p(self,p): return {"position":p}
    def test_okraj_priama(self):    assert is_gem_candidate(self._a("PRIAMA"),   self._p("OKRAJ"))
    def test_okraj_ciastocna(self): assert is_gem_candidate(self._a("CIASTOCNA"),self._p("OKRAJ"))
    def test_stred_false(self):     assert not is_gem_candidate(self._a("PRIAMA"),self._p("STRED"))
    def test_mimo_false(self):      assert not is_gem_candidate(self._a("PRIAMA"),self._p("MIMO"))
    def test_ziadna_false(self):    assert not is_gem_candidate(self._a("ZIADNA"),self._p("OKRAJ"))
    def test_both_bad(self):        assert not is_gem_candidate(self._a("ZIADNA"),self._p("MIMO"))
class TestAnalyzeNewFields:
    @patch("services.overpass_service.get_criteria_section")
    def test_buildings_key(self,mc):
        mc.side_effect=CFG
        r=_analyze_elements([bld(LAT+NEAR,LON),road(LAT+NEAR,LON)],LAT,LON)
        assert "buildings" in r and r["buildings"]["nearest_m"] is not None
    @patch("services.overpass_service.get_criteria_section")
    def test_direct_access(self,mc):
        mc.side_effect=CFG
        r=_analyze_elements([bld(LAT+NEAR,LON),road(LAT+NEAR,LON)],LAT,LON)
        assert r["direct_access"]["level"] in {"PRIAMA","CIASTOCNA","ZIADNA"}
    @patch("services.overpass_service.get_criteria_section")
    def test_village_position(self,mc):
        mc.side_effect=CFG
        r=_analyze_elements([bld(LAT+NEAR,LON)],LAT,LON)
        assert r["village_position"]["position"] in {"STRED","OKRAJ","MIMO"}
    @patch("services.overpass_service.get_criteria_section")
    def test_gem_is_bool(self,mc):
        mc.side_effect=CFG
        r=_analyze_elements([bld(LAT+NEAR,LON)],LAT,LON)
        assert isinstance(r["is_gem_candidate"],bool)
    @patch("services.overpass_service.get_criteria_section")
    def test_old_keys_untouched(self,mc):
        mc.side_effect=CFG
        r=_analyze_elements([],LAT,LON)
        for k in ["road","electricity","water","forest_buffer","noise","environment"]: assert k in r
    @patch("services.overpass_service.get_criteria_section")
    def test_empty_buildings(self,mc):
        mc.side_effect=CFG
        r=_analyze_elements([],LAT,LON)
        assert r["buildings"]=={"nearest_m":None,"count_100m":0,"count_300m":0}
    @patch("services.overpass_service.get_criteria_section")
    def test_score_no_change(self,mc):
        mc.side_effect=CFG
        r=_analyze_elements([],LAT,LON)
        base={k:r[k] for k in ["road","electricity","water","pipeline_gas","forest_buffer","noise","environment"]}
        assert _calculate_score(r)==_calculate_score(base)
