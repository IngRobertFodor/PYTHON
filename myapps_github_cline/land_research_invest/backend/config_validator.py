"""
Config Validator
================
Overuje ze criteria.yaml je spravne nastaveny.
Zachytava: zly sucet vah, min>max, zahutane prahy, zle zony atd.
"""

from config_loader import get_config

REQUIRED_SECTIONS = ["criteria", "scoring", "sources", "features"]
VALID_ZONES = {"GREEN", "YELLOW", "RED"}
WEIGHTS_TOLERANCE = 0.01


def validate_config(config: dict | None = None) -> list[str]:
    """
    Vrati zoznam chyb (po slovensky). Prazdny = config OK.
    Args:
        config: dict alebo None (nacita z yaml)
    """
    cfg = config if config is not None else get_config()
    errors: list[str] = []
    _check_required_sections(cfg, errors)
    _check_weights(cfg, errors)
    _check_thresholds(cfg, errors)
    _check_price(cfg, errors)
    _check_parcel(cfg, errors)
    _check_location(cfg, errors)
    _check_sources(cfg, errors)
    _check_terrain(cfg, errors)
    return errors


def _is_num(v) -> bool:
    try: float(v); return True
    except (TypeError, ValueError): return False


def _check_required_sections(cfg, errors):
    for s in REQUIRED_SECTIONS:
        if s not in cfg:
            errors.append(f"Chybajuca sekcia '{s}' v criteria.yaml.")


def _check_weights(cfg, errors):
    w = cfg.get("scoring", {}).get("weights", {})
    if not w:
        errors.append("Chybaju vahy v scoring -> weights.")
        return
    for k, v in w.items():
        if not _is_num(v):
            errors.append(f"Vaha '{k}' nie je cislo: {v}")
        elif float(v) < 0:
            errors.append(f"Vaha '{k}' je zaporna ({v}).")
    total = sum(float(v) for v in w.values() if _is_num(v))
    if abs(total - 1.0) > WEIGHTS_TOLERANCE:
        errors.append(
            f"Sucet vah nie je 1.0 (aktualne: {round(total,4)}). "
            "Uprav scoring -> weights."
        )


def _check_thresholds(cfg, errors):
    t = cfg.get("scoring", {}).get("thresholds", {})
    sb, inv, con = t.get("strong_buy"), t.get("investigate"), t.get("consider")
    if not all(_is_num(v) for v in [sb, inv, con]):
        errors.append("Chybaju prahy strong_buy/investigate/consider.")
        return
    if float(sb) <= float(inv):
        errors.append(
            f"strong_buy ({sb}) musi byt vacsi ako investigate ({inv}). "
            "Poradie: strong_buy > investigate > consider."
        )
    if float(inv) <= float(con):
        errors.append(f"investigate ({inv}) musi byt vacsi ako consider ({con}).")
    if float(con) < 0 or float(sb) > 100:
        errors.append("Prahy musia byt v rozsahu 0-100.")


def _check_price(cfg, errors):
    p = cfg.get("criteria", {}).get("price", {})
    if not p: return
    mn, mx = p.get("min_eur"), p.get("max_eur")
    if _is_num(mn) and _is_num(mx) and float(mn) >= float(mx):
        errors.append(f"price.min_eur ({mn}) musi byt mensie ako max_eur ({mx}).")
    if _is_num(mx) and float(mx) <= 0:
        errors.append("price.max_eur musi byt kladne cislo.")
    sqm = p.get("max_price_per_sqm_eur")
    if _is_num(sqm) and float(sqm) <= 0:
        errors.append("price.max_price_per_sqm_eur musi byt kladne cislo.")


def _check_parcel(cfg, errors):
    p = cfg.get("criteria", {}).get("parcel", {})
    if not p: return
    mn, mx = p.get("min_area_sqm"), p.get("max_area_sqm")
    if _is_num(mn) and _is_num(mx) and float(mn) >= float(mx):
        errors.append(
            f"parcel.min_area_sqm ({mn}) musi byt mensie ako max_area_sqm ({mx})."
        )
    w = p.get("min_width_m")
    if _is_num(w) and float(w) <= 0:
        errors.append("parcel.min_width_m musi byt kladne cislo.")


def _check_location(cfg, errors):
    loc = cfg.get("criteria", {}).get("location", {})
    if not loc: return
    km = loc.get("max_distance_km")
    if _is_num(km) and float(km) <= 0:
        errors.append("location.max_distance_km musi byt kladne cislo.")
    for coord in ("center_lat", "center_lon"):
        v = loc.get(coord)
        if v is not None and not _is_num(v):
            errors.append(f"location.{coord} nie je cislo: {v}")


def _check_sources(cfg, errors):
    for name, src in cfg.get("sources", {}).items():
        if not isinstance(src, dict): continue
        enabled = src.get("enabled")
        if enabled is not None and not isinstance(enabled, bool):
            errors.append(
                f"sources.{name}.enabled musi byt true/false (nie: {enabled})."
            )
        zone = src.get("zone")
        if zone is not None and zone not in VALID_ZONES:
            errors.append(
                f"sources.{name}.zone '{zone}' neplatna. "
                f"Platne: {', '.join(sorted(VALID_ZONES))}."
            )


def _check_terrain(cfg, errors):
    t = cfg.get("criteria", {}).get("terrain", {})
    if not t: return
    mx, pref = t.get("max_slope_percent"), t.get("preferred_slope_percent")
    if _is_num(mx) and _is_num(pref) and float(pref) >= float(mx):
        errors.append(
            f"terrain.preferred_slope_percent ({pref}) musi byt "
            f"mensie ako max_slope_percent ({mx})."
        )
    e = t.get("max_elevation_m")
    if _is_num(e) and float(e) <= 0:
        errors.append("terrain.max_elevation_m musi byt kladne cislo.")
    r = t.get("max_radon_risk_class")
    if r is not None and _is_num(r) and int(float(r)) not in (1, 2, 3):
        errors.append(f"terrain.max_radon_risk_class musi byt 1, 2 alebo 3 (nie: {r}).")
