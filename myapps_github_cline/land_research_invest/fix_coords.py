"""Add ASCII fallback keys and fix _estimate_distance_km to also strip diacritics."""
import unicodedata

path = r'c:\__TESTAUTOMATION\SCRIPTS\PYTHON\myapps_github_cline\land_research_invest\backend\services\scoring_service.py'

with open(path, encoding='utf-8') as f:
    content = f.read()

# 1. Add ASCII fallback entries to _SK_TOWN_COORDS (before closing })
ascii_entries = '''    # ASCII verzie (bez diakritiky) -- automaticky normalizovane v _estimate_distance_km
    "kosice": (48.7167, 21.2500),
    "presov": (49.0022, 21.2394),
    "zilina": (49.2234, 18.7403),
    "trencin": (48.8942, 18.0442),
    "banska bystrica": (48.7361, 19.1533),
    "piestany": (48.5883, 17.8306),
    "stara lubovna": (49.3000, 20.6833),
    "raca": (48.2061, 17.1464),
    "devin": (48.1736, 17.0358),
    "devinska nova ves": (48.1983, 17.0628),
    "dubravka": (48.1725, 17.0567),
    "petrzalka": (48.0908, 17.0956),
    "ruzinov": (48.1483, 17.1578),
    "vrakuna": (48.1400, 17.1994),
    "lamac": (48.1878, 17.0467),
    "kamenny most": (47.9667, 18.5500),
    "blatne": (48.2500, 17.2833),
    "halic": (48.4003, 19.7181),
    "varhanovce": (49.0833, 21.3167),
    "skalite": (49.4667, 18.9833),
    "ladomirova": (49.3833, 21.8000),
    "vernar": (48.8500, 20.3167),
    "sunava": (49.0167, 20.1667),
    "hanigovce": (49.0833, 21.1833),
    "vitazovce": (48.3833, 19.7167),
    "ihrac": (48.3750, 18.7500),
    "velke pole": (48.4267, 18.9575),
    "velka lomnica": (49.1500, 20.3833),
    "stebnik": (49.4000, 21.5833),
    "bzince pod javorinou": (48.7167, 17.7500),
    "gbelany": (49.1833, 18.7500),
    "sobos": (49.2167, 21.5167),
    "diakovce": (47.9833, 17.9333),
    "bilkove humence": (48.5167, 17.8000),
    "hurbanovo": (47.8706, 18.1908),
    "vistuk": (48.2997, 17.3631),
    "podhorany": (48.4667, 18.2500),
    "bruty": (48.1833, 18.2500),
    "kamenný most": (47.9667, 18.5500),
}
'''

# Replace the closing } of _SK_TOWN_COORDS
old_close = '    "opiná": (48.6667, 21.3333),\n}'
new_close = '    "opiná": (48.6667, 21.3333),\n' + ascii_entries

if old_close in content:
    content = content.replace(old_close, new_close)
    print('ASCII entries added OK')
else:
    # Try without accent
    old_close2 = '    "opina": (48.6667, 21.3333),\n}'
    if old_close2 in content:
        content = content.replace(old_close2, '    "opina": (48.6667, 21.3333),\n' + ascii_entries)
        print('ASCII entries added (no accent version) OK')
    else:
        idx = content.rfind('"opiná"')
        if idx == -1:
            idx = content.rfind('"opina"')
        print(f'Marker at {idx}: {repr(content[idx:idx+60])}')

# 2. Update _estimate_distance_km to normalize text (remove diacritics)
old_func = '''def _estimate_distance_km(location_text: str) -> float | None:
    """
    Odhadne vzdialenosť od BA na základe location_text (bez GPS).
    Prehľadá slovník SK miest. Vracia km alebo None ak nenájde.
    """
    if not location_text:
        return None
    loc = location_text.lower().strip()
    # Najprv presná zhoda
    if loc in _SK_TOWN_COORDS:
        lat, lon = _SK_TOWN_COORDS[loc]
        return _haversine_km(_BA_LAT, _BA_LON, lat, lon)
    # Čiastočná zhoda (location_text obsahuje názov mesta)
    for town, coords in _SK_TOWN_COORDS.items():
        if town in loc or loc in town:
            return _haversine_km(_BA_LAT, _BA_LON, coords[0], coords[1])
    return None'''

new_func = '''def _normalize_loc(text: str) -> str:
    """Normalizuje text: lowercase, bez diakritiky, strip."""
    import unicodedata
    nfkd = unicodedata.normalize("NFKD", text.lower().strip())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _estimate_distance_km(location_text: str) -> float | None:
    """
    Odhadne vzdialenosť od BA na základe location_text (bez GPS).
    Prehľadá slovník SK miest (s diakritikou aj bez). Vracia km alebo None.
    """
    if not location_text:
        return None
    loc     = location_text.lower().strip()
    loc_asc = _normalize_loc(location_text)

    # 1. Presná zhoda (s diakritikou aj bez)
    for key in (loc, loc_asc):
        if key in _SK_TOWN_COORDS:
            lat, lon = _SK_TOWN_COORDS[key]
            return _haversine_km(_BA_LAT, _BA_LON, lat, lon)

    # 2. Čiastočná zhoda — town IN loc alebo loc IN town (obe varianty)
    for town, coords in _SK_TOWN_COORDS.items():
        town_asc = _normalize_loc(town)
        if (town in loc or loc_asc in town_asc
                or town_asc in loc_asc or loc in town):
            return _haversine_km(_BA_LAT, _BA_LON, coords[0], coords[1])
    return None'''

if old_func in content:
    content = content.replace(old_func, new_func)
    print('_estimate_distance_km updated OK')
else:
    idx = content.find('def _estimate_distance_km')
    print(f'Function at {idx}, checking...')
    print(repr(content[idx:idx+200]))

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('File saved. Total lines:', content.count('\n'))
