"""
opportunity_service.py — Investičný index + zdôvodnenie
=========================================================
B4: Kombinovaný index (0–100) + textové „prečo toto".
Váhy a penalizácie sa načítajú z criteria.yaml (sekcia opportunity).
"""

import math

# Fallback váhy ak criteria.yaml sekcia opportunity chýba
_DEFAULT_MISPRICING_WEIGHTS = {
    "HORICE":               1.00,
    "DRAZBA_POD_ZNALECKOU": 0.90,
    "LACNEJSI_AKO_OKOLIE":  0.75,
    "CENA_KLESA":           0.60,
    "DLHO_V_PONUKE":        0.50,
    "DRAZBA_OPAKOVANA":     0.45,
    "DRAZBA_PODHODNOTENA":  0.30,
}

_DEFAULT_RISK_PENALTIES = {
    "ZAPLAVA":         20,
    "CHRANENE_UZEMIE": 15,
    "DRAHE_VYNATIE":   12,
    "PRILIS_DALEKO":   10,
    "CENA_PODOZRIVA":   8,
}

_EXPLAIN_MIN_INDEX = 30


def _get_weights() -> tuple[dict, dict]:
    """Načíta váhy z criteria.yaml sekcia opportunity, alebo použije defaults."""
    try:
        from config_loader import get_criteria
        opp = get_criteria().get("opportunity", {})
        weights  = opp.get("mispricing_weights", _DEFAULT_MISPRICING_WEIGHTS)
        penalties = opp.get("risk_penalties",    _DEFAULT_RISK_PENALTIES)
        return weights, penalties
    except Exception:
        return _DEFAULT_MISPRICING_WEIGHTS, _DEFAULT_RISK_PENALTIES


# Pre spätnu kompatibilitu (testy importujú priamo)
_MISPRICING_WEIGHTS = _DEFAULT_MISPRICING_WEIGHTS
_RISK_PENALTIES     = _DEFAULT_RISK_PENALTIES


def investment_index(parcel: dict) -> int:
    """Investičný index 0–100.

    Zložky:
      rezoning_pts   (0–35): log rast s odh. ziskom z preklasifikácie
      misprint_pts   (0–35): váhované mispricingové signály (B1+B2+B3)
      confidence_pts (0–15): prelim_confidence × 15
      risk_penalty   (0–25): rizikové signály odpočítajú body

    Váhy sa načítavajú z criteria.yaml sekcia opportunity
    (fallback na hardcoded defaults ak sekcia chýba).
    """
    mispricing_weights, risk_penalties = _get_weights()
    sigs       = parcel.get("signals") or []
    confidence = float(parcel.get("prelim_confidence") or 1.0)

    # 1. Rezoning (0–35) — log rast: 10k€→10b, 50k€→24b, 100k€→30b, 300k€→35b
    profit = float(parcel.get("rezoning_profit_eur") or 0)
    rezoning_pts = min(35.0, 10.0 * math.log10(max(1, profit / 1000) + 1)) if profit > 0 else 0.0

    # 2. Mispricing (0–35)
    misprint_pts = 0.0
    for sig in sigs:
        kod = sig.get("kod", "")
        if kod not in mispricing_weights:
            continue
        if kod == "LACNEJSI_AKO_OKOLIE" and sig.get("typ") != "PRILEZITOST":
            continue
        misprint_pts += mispricing_weights[kod] * float(sig.get("dovera") or 0.5) * 35.0
    misprint_pts = min(35.0, misprint_pts)

    # 3. Confidence (0–15)
    confidence_pts = confidence * 15.0

    # 4. Penalty (0–25)
    penalty = 0.0
    for sig in sigs:
        p = risk_penalties.get(sig.get("kod", ""), 0)
        if p:
            penalty += p * float(sig.get("dovera") or 0.5)
    penalty = min(25.0, penalty)

    return max(0, min(100, round(rezoning_pts + misprint_pts + confidence_pts - penalty)))


def explain(parcel: dict) -> str:
    """Stručné textové zdôvodnenie (2–4 vety) prečo je pozemok zaujímavý."""
    idx = parcel.get("investment_index") or investment_index(parcel)
    if idx < _EXPLAIN_MIN_INDEX:
        return ""

    sigs     = parcel.get("signals") or []
    sig_map  = {s["kod"]: s for s in sigs}
    parts    = []

    # Základ: lokácia + parametre
    loc   = parcel.get("location_text") or ""
    area  = float(parcel.get("area_sqm")  or 0)
    price = float(parcel.get("price_eur") or 0)
    obec  = loc.split(",")[0].strip() if loc else ""
    if obec and area > 0 and price > 0:
        ppsm_str = f", {price/area:.0f} €/m²" if area > 0 else ""
        parts.append(f"Pozemok v {obec} ({area:,.0f} m², {price:,.0f} €{ppsm_str}).")

    # Rezoning zisk
    profit = float(parcel.get("rezoning_profit_eur") or 0)
    if profit > 0:
        parts.append(f"Kandidát na preklasifikáciu — est. zisk +{profit:,.0f} €.")

    # Mispricingové signály
    misprints = []
    if "HORICE" in sig_map:
        misprints.append(sig_map["HORICE"]["nazov"].replace("🔥 ", "").replace("Horúce — ", ""))
    else:
        if "DLHO_V_PONUKE" in sig_map:
            misprints.append(sig_map["DLHO_V_PONUKE"]["nazov"])
        if "CENA_KLESA" in sig_map:
            misprints.append(sig_map["CENA_KLESA"]["nazov"])
    if "DRAZBA_POD_ZNALECKOU" in sig_map:
        misprints.append(sig_map["DRAZBA_POD_ZNALECKOU"]["nazov"])
    if "LACNEJSI_AKO_OKOLIE" in sig_map and sig_map["LACNEJSI_AKO_OKOLIE"].get("typ") == "PRILEZITOST":
        misprints.append(sig_map["LACNEJSI_AKO_OKOLIE"]["nazov"])
    if misprints:
        parts.append(" + ".join(misprints) + ".")

    # Riziká alebo odporúčanie
    risky = [sig_map[k]["nazov"] for k in ("ZAPLAVA", "CHRANENE_UZEMIE", "DRAHE_VYNATIE") if k in sig_map]
    if risky:
        parts.append(f"\u26a0\ufe0f Riziká: {', '.join(risky)}.")
    else:
        parts.append("Preveriť: prístup, bremená, LV.")

    return " ".join(parts)


def apply_opportunity(parcels: list[dict]) -> list[dict]:
    """Vypočíta investment_index a investment_summary pre všetky pozemky.
    Volá sa z scrape_routes._run() po apply_peer_signals. Mutuje in-place."""
    for p in parcels:
        idx = investment_index(p)
        p["investment_index"]   = idx
        p["investment_summary"] = explain(p) if idx >= _EXPLAIN_MIN_INDEX else ""
    return parcels

