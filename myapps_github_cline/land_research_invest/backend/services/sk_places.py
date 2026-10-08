"""
sk_places.py — Centralny register sidiel Slovenska.
Zdroj: GeoNames SK.zip, CC-BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
Nacita backend/data/obce_sk.json (vygenerovany cez build_obce_sk.py).
Fallback na hardcoded mini-zoznam ak JSON chyba.

Exportuje:
  PLACE_NORM  : dict[norm_key -> original_name]   (~9 200 poloziek)
  PLACE_COORDS: dict[norm_key -> (lat, lon)]       (rovnake kluce)
  find_place(text)  -> (original_name, lat, lon) | None
  dist_to_ba(name)  -> km | None
"""
import os
import math
import unicodedata

_BA_LAT, _BA_LON = 48.1486, 17.1077

# ---------------------------------------------------------------------------
# Normalizacia
# ---------------------------------------------------------------------------
def _norm(s: str) -> str:
    n = unicodedata.normalize("NFD", s.lower().strip())
    return "".join(c for c in n if unicodedata.category(c) != "Mn")


def _haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


# ---------------------------------------------------------------------------
# Nacitanie dat
# ---------------------------------------------------------------------------
_DATA_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
_JSON_PATH = os.path.normpath(os.path.join(_DATA_DIR, "obce_sk.json"))

# Fallback mini-zoznam (len najdolezitejsie mesta) — pouzije sa ak JSON chyba
_FALLBACK = {
    "bratislava": (48.14816, 17.10674), "senec": (48.21951, 17.40043),
    "pezinok": (48.28935, 17.26743),    "malacky": (48.43604, 17.02188),
    "dunajska streda": (47.99268, 17.61211), "nitra": (48.30763, 18.08453),
    "trnava": (48.37749, 17.58723),     "trencin": (48.8942, 18.0442),
    "senica": (48.67922, 17.36697),     "samorin": (48.03015, 17.30972),
    "lehnice": (48.05577, 17.46337),    "devinska nova ves": (48.20711, 16.9786),
    "raca": (48.2061, 17.1464),         "modra": (48.33439, 17.31317),
    "svaty jur": (48.25251, 17.21808),  "bernolakovo": (48.17483, 17.30286),
    "chorvat sky grob": (48.27093, 17.36007), "ivanka pri dunaji": (48.15588, 17.27222),
    "stupava": (48.26933, 17.03207),    "zohor": (48.35538, 16.97197),
}

PLACE_NORM:   dict[str, str]           = {}  # norm -> original name
PLACE_COORDS: dict[str, tuple[float,float]] = {}  # norm -> (lat, lon)

def _load():
    global PLACE_NORM, PLACE_COORDS
    if PLACE_NORM:
        return  # uz nacitane
    try:
        import json
        with open(_JSON_PATH, encoding="utf-8") as f:
            data = json.load(f)
        for p in data["places"]:
            key = _norm(p["name"])
            if key and key not in PLACE_NORM:
                PLACE_NORM[key]   = p["name"]
                PLACE_COORDS[key] = (p["lat"], p["lon"])
        # ASCII kluce
        for p in data["places"]:
            akey = _norm(p["ascii"])
            if akey and akey not in PLACE_NORM:
                PLACE_NORM[akey]   = p["name"]
                PLACE_COORDS[akey] = (p["lat"], p["lon"])
    except Exception:
        # Fallback
        for k, coords in _FALLBACK.items():
            PLACE_NORM[k]   = k.title()
            PLACE_COORDS[k] = coords

_load()


# ---------------------------------------------------------------------------
# Verejne API
# ---------------------------------------------------------------------------
def find_place(text: str):
    """
    Hlada sidlo v texte.
    Vracia (original_name, lat, lon) alebo None.
    Stratégia: presná zhoda -> substring zhoda -> None.
    POZNAMKA: stem-match sa NEPOUZIVA (false positive riziko pri 8000+ sidlach).
    """
    if not text:
        return None
    _load()
    key = _norm(text)
    # 1. Presna zhoda
    if key in PLACE_COORDS:
        return PLACE_NORM[key], PLACE_COORDS[key][0], PLACE_COORDS[key][1]
    # 2. Hladame kluc ktory je presne obsazeny v texte alebo text v kluchi
    #    Triedime od najdlhsich nazvov (znizi false positive)
    for place_key in sorted(PLACE_COORDS, key=lambda k: -len(k)):
        if len(place_key) < 3:
            continue
        if place_key in key or key in place_key:
            return PLACE_NORM[place_key], PLACE_COORDS[place_key][0], PLACE_COORDS[place_key][1]
    return None


def dist_to_ba(name: str) -> float | None:
    """Vzdialenost sidla od Bratislavy v km. None ak nenajdene."""
    r = find_place(name)
    if r is None:
        return None
    _, lat, lon = r
    return round(_haversine(_BA_LAT, _BA_LON, lat, lon), 1)
