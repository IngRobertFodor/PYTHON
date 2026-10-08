"""
build_obce_sk.py — Vygeneruje backend/data/obce_sk.json zo suborov GeoNames SK.zip.
Pouzitie: python backend/data/build_obce_sk.py
Licencia dat: GeoNames CC-BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
"""
import zipfile, json, os, unicodedata, re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_PATH   = os.path.join(SCRIPT_DIR, "SK.zip")
OUT_PATH   = os.path.join(SCRIPT_DIR, "obce_sk.json")

KEEP_CODES = {
    "PPL","PPLA","PPLA2","PPLA3","PPLA4",
    "PPLC","PPLF","PPLG","PPLL","PPLR","PPLS","PPLX",
}

COLS = [
    "geonameid","name","asciiname","alternatenames",
    "latitude","longitude","feature_class","feature_code",
    "country_code","cc2","admin1","admin2","admin3","admin4",
    "population","elevation","dem","timezone","modification_date"
]

# Vzor pre platne SK/latinke nazvy (bez arabciny, ciricily, iny diakritickych systemov)
_LATIN_RE = re.compile(r'^[A-Za-záäčďéíľĺňóôŕšťúýžÁÄČĎÉÍĽĹŇÓÔŔŠŤÚÝŽ\s\-\.\']+$')

def norm(s):
    n = unicodedata.normalize("NFD", s.lower().strip())
    return "".join(c for c in n if unicodedata.category(c) != "Mn")

places = {}  # norm_name -> {name, lat, lon, pop, ascii}

def _add(key, name, ascii_name, lat, lon, pop):
    if not key or len(key) < 2:
        return
    if key not in places or pop > places[key]["pop"]:
        places[key] = {"name": name, "ascii": ascii_name,
                       "lat": lat, "lon": lon, "pop": pop}

with zipfile.ZipFile(ZIP_PATH) as zf:
    fname = [n for n in zf.namelist() if n.endswith(".txt") and not n.startswith("readme")][0]
    with zf.open(fname) as fh:
        for raw in fh:
            line = raw.decode("utf-8").rstrip("\n")
            parts = line.split("\t")
            if len(parts) < 15:
                continue
            row = dict(zip(COLS, parts))
            if row["feature_class"] != "P":
                continue
            if row["feature_code"] not in KEEP_CODES:
                continue
            name       = row["name"].strip()
            ascii_name = row["asciiname"].strip()
            try:
                lat = float(row["latitude"])
                lon = float(row["longitude"])
                pop = int(row["population"]) if row["population"] else 0
            except ValueError:
                continue

            # Hlavny nazov (vzdy pridame)
            _add(norm(name), name, ascii_name, lat, lon, pop)
            # ASCII nazov (len ak sa lisi)
            if ascii_name.lower() != name.lower():
                _add(norm(ascii_name), ascii_name, ascii_name, lat, lon, pop)

            # Alternativne nazvy — len latinke (ziadna arabcina, cirilika, ...)
            for alt in row.get("alternatenames","").split(","):
                alt = alt.strip()
                if not alt or len(alt) < 3:
                    continue
                if not _LATIN_RE.match(alt):
                    continue  # preskoč non-latinke varianty
                _add(norm(alt), alt, ascii_name, lat, lon, pop)

result = [
    {"name": v["name"], "ascii": v["ascii"],
     "lat": round(v["lat"], 5), "lon": round(v["lon"], 5), "pop": v["pop"]}
    for v in places.values()
]
result.sort(key=lambda x: (-len(x["name"]), x["name"]))

meta = {
    "_source": "GeoNames (https://www.geonames.org/), CC-BY 4.0",
    "_generated": "build_obce_sk.py",
    "_count": len(result),
    "places": result
}

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, separators=(",",":"))

print(f"Zapisano {len(result)} siel -> {OUT_PATH}")
