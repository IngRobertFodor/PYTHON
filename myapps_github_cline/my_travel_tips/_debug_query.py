"""
Diagnostic script - simulates exact frontend request for Athens.
Run from project root: python _debug_query.py
"""
import sys
import os
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from services.overpass_service import (
    get_pois, _query_overpass, _build_query, _get_query_config
)

LAT, LON, RADIUS_KM = 37.98, 23.72, 43

print("=" * 60)
print(f"DIAG: Athens | lat={LAT} lon={LON} radius={RADIUS_KM}km")
print("=" * 60)

config = _get_query_config(RADIUS_KM)
timeout_effective = config.get('timeout', 30) + 10
print(f"\n[1] Config: {config} | effective HTTP timeout: {timeout_effective}s")

q = _build_query(LAT, LON, int(RADIUS_KM * 1000), ["tourism=museum", "historic=castle"], config)
print(f"\n[2] Sample query (museum+castle, first 500 chars):\n{q[:500]}")

print("\n[3] Direct Overpass (2 tags: museum + castle)...")
t0 = time.time()
raw2 = _query_overpass(LAT, LON, int(RADIUS_KM * 1000), ["tourism=museum", "historic=castle"], config)
print(f"    => {len(raw2)} elements in {round(time.time()-t0,1)}s")
for e in raw2[:5]:
    tgs = e.get('tags', {})
    print(f"    - {tgs.get('name', '?')} | type={e.get('type')}")

HISTORIC_TAGS = [
    "historic=castle", "historic=palace", "historic=monument", "historic=memorial",
    "historic=ruins", "historic=archaeological_site", "historic=manor",
    "historic=city_gate", "historic=city_wall", "historic=aqueduct", "historic=wreck",
    "tourism=museum", "tourism=gallery", "tourism=attraction",
    "amenity=theatre", "amenity=arts_centre",
]
print(f"\n[4] Full custom_tags mode ({len(HISTORIC_TAGS)} tags)...")
t0 = time.time()
result = get_pois(LAT, LON, RADIUS_KM, custom_tags=HISTORIC_TAGS, lang='sk')
dt4 = round(time.time() - t0, 1)
meta = result.get('_meta', {})
mainstream = result.get('mainstream', [])
alternative = result.get('alternative', [])
print(f"    => Done in {dt4}s")
print(f"    _meta:\n{json.dumps(meta, ensure_ascii=False, indent=6)}")
print(f"    mainstream={len(mainstream)}, alternative={len(alternative)}")
for p in mainstream[:5]:
    print(f"      [{p.get('score')}] {p.get('name')} ({p.get('type')}, {p.get('distance_km')}km)")
print("=" * 60)
