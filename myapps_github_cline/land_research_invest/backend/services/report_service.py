"""Report sluzba - Investicny report pozemku
Zoskupuje vysledky vsetkych sluzieb do jedneho prehladu.
Produkuje dva vystupy: data dict (strojovy) + text_report (SK text).
"""

from models.result import ServiceResult
from config_loader import get_scoring, get_criteria_section
from services.scoring_service import WEIGHT_TO_SOURCE

SERVICE_NAME = "report_service"


def generate_report(parcel):
    """Hlavna funkcia - kompletny investicny report pozemku."""
    summary    = build_summary(parcel)
    breakdown  = build_score_breakdown(parcel)
    red_flags  = build_red_flags(parcel)
    investment = build_investment_view(parcel)
    text       = format_text_report(parcel)
    return ServiceResult(
        ok=True,
        score=round(parcel.final_score, 2),
        data={
            "summary":         summary,
            "score_breakdown": breakdown,
            "red_flags":       red_flags,
            "investment":      investment,
            "recommendation":  parcel.recommendation,
            "text_report":     text,
        },
        source=SERVICE_NAME,
    )

def build_summary(parcel):
    """Zakladne udaje parcely - hlavicka reportu."""
    price_per_sqm = 0.0
    if parcel.area_sqm and parcel.area_sqm > 0:
        price_per_sqm = round(parcel.price_eur / parcel.area_sqm, 2)

    dist_km = None
    dist_r = parcel.results.get("distance_service")
    if dist_r and dist_r.ok:
        dist_km = dist_r.data.get("distance_km")

    return {
        "title":          parcel.title,
        "url":            parcel.url,
        "location":       parcel.location_text,
        "parcel_number":  parcel.parcel_number,
        "price_eur":      parcel.price_eur,
        "area_sqm":       parcel.area_sqm,
        "price_per_sqm":  price_per_sqm,
        "distance_km":    dist_km,
        "final_score":    round(parcel.final_score, 2),
        "recommendation": parcel.recommendation,
    }

def build_score_breakdown(parcel):
    """Rozpad celkoveho skore podla 8 vazenych sluzieb."""
    cfg_weights = get_scoring().get("weights", {})
    items = []
    total_weight_used = 0.0

    for weight_key, weight_val in cfg_weights.items():
        source = WEIGHT_TO_SOURCE.get(weight_key)
        if source is None:
            continue
        result = parcel.results.get(source)
        if result is None:
            items.append({
                "weight_key": weight_key,
                "source":     source,
                "weight":     weight_val,
                "score":      None,
                "contrib":    0.0,
                "status":     "missing",
            })
            continue

        if result.data.get("skipped"):
            status = "skipped"
        elif not result.ok:
            status = "error"
        else:
            status = "ok"

        contrib = round(result.score * weight_val, 4)
        total_weight_used += weight_val
        items.append({
            "weight_key": weight_key,
            "source":     source,
            "weight":     weight_val,
            "score":      result.score,
            "contrib":    contrib,
            "status":     status,
        })

    return {
        "items":             items,
        "total_weight_used": round(total_weight_used, 4),
        "final_score":       round(parcel.final_score, 2),
    }

def build_red_flags(parcel):
    """Zbiera kriticke blokanty a varovania zo vsetkych sluzieb."""
    blockers = []
    warnings = []

    # --- Rejected sluzby (ok=False, score=0, nie skipped) ---
    for source, result in parcel.results.items():
        if not result.ok and result.score == 0 and not result.data.get("skipped"):
            err_msg = result.error if result.error else "chyba sluzby"
            blockers.append(f"Sluzba {source}: {err_msg}")

    # --- Kataster: issues su blokanty, warnings su varovania ---
    cad = parcel.results.get("cadastral_service")
    if cad and cad.data.get("mode") == "evaluated":
        for issue in cad.data.get("issues", []):
            blockers.append(f"Kataster: {issue}")
        for warn in cad.data.get("warnings", []):
            warnings.append(f"Kataster: {warn}")

    # --- Povodne Q100 ---
    flood = parcel.results.get("flood_service")
    if flood and flood.ok and flood.data.get("in_flood_zone"):
        blockers.append("Povodne: parcela v zaplavovej zone Q100")

    # --- Chranene pasma: violations = blokanty ---
    prot = parcel.results.get("protected_service")
    if prot and prot.ok:
        for flag in prot.data.get("violations", []):
            blockers.append(f"Ochrana: {flag}")
        for warn in prot.data.get("warnings", []):
            warnings.append(f"Ochrana: {warn}")

    # --- BPEJ triedy 1-4 = drahe vynatie z PPF ---
    bpej = parcel.results.get("bpej_service")
    if bpej and bpej.ok:
        cls = bpej.data.get("protection_class")
        if cls is not None and cls <= 4:
            warnings.append(f"BPEJ: ochrana trieda {cls} - mozne vysoke odvody za vynatie z PPF")

    return {
        "blockers":      blockers,
        "warnings":      warnings,
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "has_blockers":  len(blockers) > 0,
    }

def build_investment_view(parcel):
    """Porovnanie ceny a rozlohy s limitmi z criteria.yaml."""
    price_cfg  = get_criteria_section("price")
    parcel_cfg = get_criteria_section("parcel")

    max_eur       = price_cfg.get("max_eur", 50000)
    min_eur       = price_cfg.get("min_eur", 10000)
    max_sqm_price = price_cfg.get("max_price_per_sqm_eur", 100)
    min_area      = parcel_cfg.get("min_area_sqm", 600)
    max_area      = parcel_cfg.get("max_area_sqm", 1500)

    price = parcel.price_eur
    area  = parcel.area_sqm
    ppsm  = round(price / area, 2) if area > 0 else 0.0

    over_budget = price > max_eur
    under_min   = price < min_eur and price > 0
    over_sqm    = ppsm > max_sqm_price
    area_ok     = (min_area <= area <= max_area) if area > 0 else False

    if over_budget and over_sqm:
        verdict = "FAIL"
    elif over_budget:
        verdict = "OVER_BUDGET"
    elif over_sqm:
        verdict = "OVER_SQM"
    elif not area_ok and area > 0:
        verdict = "AREA_MISMATCH"
    else:
        verdict = "PASS"

    return {
        "price_eur":         price,
        "min_eur":           min_eur,
        "max_eur":           max_eur,
        "over_budget":       over_budget,
        "under_min":         under_min,
        "price_per_sqm":     ppsm,
        "max_price_per_sqm": max_sqm_price,
        "over_sqm_limit":    over_sqm,
        "area_sqm":          area,
        "min_area_sqm":      min_area,
        "max_area_sqm":      max_area,
        "area_ok":           area_ok,
        "verdict":           verdict,
    }

def format_text_report(parcel):
    """Citatelny SK textovy report pre konzolu alebo subor."""
    inv  = build_investment_view(parcel)
    brkd = build_score_breakdown(parcel)
    rf   = build_red_flags(parcel)
    rec  = parcel.recommendation or "N/A"
    icon = _verdict_icon(rec)

    SEP  = "=" * 62
    SEP2 = "-" * 30

    budget_ok_str  = "PRESIAHNUTY" if inv["over_budget"]    else "OK"
    sqm_ok_str     = "PRESIAHNUTY" if inv["over_sqm_limit"] else "OK"

    lines = [
        SEP,
        f"  INVESTICNY REPORT  {icon}  {rec}",
        SEP,
        f"  {parcel.title or '(bez nazvu)'}",
        f"  {parcel.url   or '(bez URL)'}",
        SEP,
        "",
        "ZAKLADNE UDAJE",
        SEP2,
        f"  Lokalita   : {parcel.location_text or 'N/A'}",
        f"  Parcela    : {parcel.parcel_number  or 'N/A'}",
    ]

    dist_r   = parcel.results.get("distance_service")
    dist_str = "N/A"
    if dist_r and dist_r.ok:
        dist_str = str(dist_r.data.get("distance_km", "N/A")) + " km"

    lines += [
        f"  Vzdialenost: {dist_str} od Bratislavy",
        f"  Cena       : {parcel.price_eur:,.0f} EUR",
        f"  Plocha     : {parcel.area_sqm:,.0f} m2",
        f"  EUR/m2     : {inv['price_per_sqm']:.2f}  (limit {inv['max_price_per_sqm']} EUR/m2)",
        f"  Rozpocet   : {budget_ok_str}  (limit {inv['max_eur']:,.0f} EUR)",
        f"  EUR/m2 stav: {sqm_ok_str}",
        "",
    ]

    lines += [
        "CELKOVE SKORE",
        SEP2,
        f"  Skore      : {parcel.final_score:.1f} / 100",
        f"  Odporucanie: {rec}  {icon}",
        "",
    ]

    lines += [
        "ROZPAD SKORE  (8 vazenych sluzieb)",
        SEP2,
    ]
    for item in brkd["items"]:
        sc_str   = f"{item['score']:.1f}" if item["score"] is not None else "  N/A"
        cnt_str  = f"{item['contrib']:.2f}" if item["score"] is not None else "  ---"
        stat_str = f"[{item['status']}]"
        lines.append(
            f"  {item['weight_key']:<18} {sc_str:>6} pts"
            f"  vaha {item['weight']:.2f}  prispevok {cnt_str}  {stat_str}"
        )
    lines.append("")

    if rf["has_blockers"] or rf["warnings"]:
        lines += ["RED FLAGS", SEP2]
        for b in rf["blockers"]:
            lines.append(f"  [!] {b}")
        for w in rf["warnings"]:
            lines.append(f"  [?] {w}")
        lines.append("")

    lines += [
        SEP,
        f"  VERDICT: {rec}  {icon}",
        SEP,
    ]

    return "\n".join(lines)


def _verdict_icon(recommendation):
    """Vizualna ikona pre odporucanie."""
    icons = {
        "STRONG BUY":  "[**]",
        "INVESTIGATE": "[??]",
        "CONSIDER":    "[..]",
        "SKIP":        "[XX]",
    }
    return icons.get(recommendation, "[--]")
