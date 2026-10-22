"""
peer_analysis_service.py — Peer comparison pozemkov v rámci obce
================================================================
Porovnáva cenu pozemku voči ostatným pozemkom v tej istej obci
z aktuálneho behu scrapovania.

Signál LACNEJSI_AKO_OKOLIE:
  - "príležitosť" ak iné signály naznačujú čistý obchod
  - "riziko/háčik" ak varovné signály (záplava, chránené...)
  - "preveriť" ak nie je dosť kontextu
"""

import statistics
from typing import NamedTuple

from services.uzemny_plan_service import normalize_obec

_HAZIK_SIGNALY      = frozenset(["ZAPLAVA", "CHRANENE_UZEMIE", "DRAHE_VYNATIE", "PRILIS_DALEKO"])
_PRILEZITOST_SIGNALY = frozenset(["PREKLASIFIKACIA", "LACNE_VYNATIE", "BLIZKO_BA"])

_DEFAULTS = {
    "peer_min_count":   4,
    "peer_lacny_ratio": 0.6,
}


def _cfg() -> dict:
    try:
        from config_loader import get_criteria
        return {**_DEFAULTS, **get_criteria().get("signals", {})}
    except Exception:
        return dict(_DEFAULTS)


class ObecStats(NamedTuple):
    median_ppsm: float
    count: int
    min_ppsm: float
    max_ppsm: float


def compute_obec_stats(parcels: list[dict]) -> dict[str, ObecStats]:
    """Zoskupí pozemky podľa obce, vráti štatistiky €/m² (len obce >= peer_min_count)."""
    cfg       = _cfg()
    min_count = int(cfg.get("peer_min_count", 4))
    groups: dict[str, list[float]] = {}

    for p in parcels:
        loc  = p.get("location_text", "")
        slug = normalize_obec(loc) if loc else ""
        if not slug:
            continue
        price = float(p.get("price_eur", 0) or 0)
        area  = float(p.get("area_sqm",  0) or 0)
        if area <= 0:          # skip pozemky bez výmery (podiely, chybné dáta)
            continue
        ppsm  = float(p.get("price_per_sqm", 0) or 0)
        if ppsm <= 0 and price > 0 and area > 0:
            ppsm = price / area
        if ppsm > 0:
            groups.setdefault(slug, []).append(ppsm)

    return {
        slug: ObecStats(
            median_ppsm = statistics.median(vals),
            count       = len(vals),
            min_ppsm    = min(vals),
            max_ppsm    = max(vals),
        )
        for slug, vals in groups.items()
        if len(vals) >= min_count
    }


def peer_signal(parcel: dict, obec_stats: dict[str, ObecStats]) -> dict | None:
    """
    Ak je pozemok výrazne pod mediánom obce → signál LACNEJSI_AKO_OKOLIE.
    Krížová kontrola: varovné signály → háčik; príležitostné → silná príležitosť.
    """
    cfg        = _cfg()
    ratio_prah = float(cfg.get("peer_lacny_ratio", 0.6))

    loc  = parcel.get("location_text", "")
    slug = normalize_obec(loc) if loc else ""
    if not slug or slug not in obec_stats:
        return None

    stats = obec_stats[slug]
    price = float(parcel.get("price_eur", 0) or 0)
    area  = float(parcel.get("area_sqm",  0) or 0)
    if area <= 0:              # skip — nemá zmysel robiť peer analýzu bez výmery
        return None
    ppsm  = float(parcel.get("price_per_sqm", 0) or 0)
    if ppsm <= 0 and price > 0 and area > 0:
        ppsm = price / area
    if ppsm <= 0:
        return None

    ratio = ppsm / stats.median_ppsm if stats.median_ppsm > 0 else 1.0
    if ratio > ratio_prah:
        return None

    existing   = {s.get("kod") for s in (parcel.get("signals") or [])}
    has_hazik  = bool(existing & _HAZIK_SIGNALY)
    has_pril   = bool(existing & _PRILEZITOST_SIGNALY)
    zlava_pct  = round((1.0 - ratio) * 100, 1)
    obec_name  = loc.split(",")[0].strip()
    ctx_suffix = (
        f"({ppsm:.0f} vs. {stats.median_ppsm:.0f} €/m², n={stats.count})"
    )

    if has_hazik:
        return {
            "kod": "LACNEJSI_AKO_OKOLIE", "typ": "RIZIKO",
            "nazov": f"📊 Lacný −{zlava_pct:.0f} % (háčik?)",
            "dovod": (
                f"Cena o {zlava_pct:.0f} % pod mediánom obce {obec_name} {ctx_suffix}. "
                f"⚠️ Varovné signály prítomné — preveriť prečo je tak lacný."
            ),
            "dovera": 0.55,
            "peer_median_ppsm": round(stats.median_ppsm, 1),
            "peer_count": stats.count, "peer_ratio": round(ratio, 3),
            "peer_obec": obec_name,
        }
    elif has_pril:
        return {
            "kod": "LACNEJSI_AKO_OKOLIE", "typ": "PRILEZITOST",
            "nazov": f"📊 Lacnejší o {zlava_pct:.0f} % než okolie",
            "dovod": (
                f"O {zlava_pct:.0f} % lacnejší než okolie v obci {obec_name} {ctx_suffix}. "
                f"Kombinácia s pozitívnymi signálmi = silná príležitosť."
            ),
            "dovera": 0.80,
            "peer_median_ppsm": round(stats.median_ppsm, 1),
            "peer_count": stats.count, "peer_ratio": round(ratio, 3),
            "peer_obec": obec_name,
        }
    else:
        return {
            "kod": "LACNEJSI_AKO_OKOLIE", "typ": "PRILEZITOST",
            "nazov": f"📊 Lacnejší o {zlava_pct:.0f} % než okolie",
            "dovod": (
                f"O {zlava_pct:.0f} % lacnejší než okolie v obci {obec_name} {ctx_suffix}. "
                f"Preveriť: prístup, vecné bremená, tvar, záplava."
            ),
            "dovera": 0.65,
            "peer_median_ppsm": round(stats.median_ppsm, 1),
            "peer_count": stats.count, "peer_ratio": round(ratio, 3),
            "peer_obec": obec_name,
        }


def apply_peer_signals(parcels: list[dict]) -> list[dict]:
    """
    Hlavná funkcia: vypočíta peer štatistiky a pridá signály.
    Volá sa z scrape_routes._run() po history_signals.
    Mutuje pozemky in-place (pridá do parcel["signals"]).
    """
    stats = compute_obec_stats(parcels)
    if not stats:
        return parcels

    for p in parcels:
        sig = peer_signal(p, stats)
        if sig:
            existing = {s.get("kod") for s in (p.get("signals") or [])}
            if "LACNEJSI_AKO_OKOLIE" not in existing:
                p.setdefault("signals", []).append(sig)
            p["peer_median_ppsm"] = sig["peer_median_ppsm"]
            p["peer_count"]        = sig["peer_count"]
            p["peer_ratio"]        = sig["peer_ratio"]
    return parcels

