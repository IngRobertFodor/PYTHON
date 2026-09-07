"""
Price Analysis Service
======================
Cenova analyza pozemku - porovnanie s lokalnym priemerom,
vyhodnotenie podhodnotenia a motivacie predajcu.

Zdroj: Vlastna DB nazbieranych inzeratov + fallback regionalne hodnoty.
Automatizacia: AUTO (bezi bez brzdenia, ziadne externe API)
"""

from models.result import ServiceResult
from config_loader import is_feature_enabled, get_criteria_section

SERVICE_NAME = "price_analysis_service"

# Fallback regionalne priemerné EUR/m2 (orientacne, region BA kraj 2024-2026)
# Klesaju s vzdialenostou od Bratislavy
REGIONAL_AVG_EUR_PER_SQM = [
    (20,  80.0),   # do 20 km od BA
    (35,  55.0),   # 20-35 km
    (50,  35.0),   # 35-50 km
    (70,  22.0),   # 50-70 km
    (999, 15.0),   # dalej
]


def check(
    price_eur: float,
    area_sqm: float,
    distance_km: float,
    listing_age_days: int = 0,
    price_history: list | None = None,
    local_avg_eur_per_sqm: float | None = None,
) -> ServiceResult:
    """
    Hlavna funkcia - cenova analyza pozemku.

    Args:
        price_eur: cena v EUR z inzeratu
        area_sqm: vymera v m2
        distance_km: vzdialenost od BA (pre fallback priemer)
        listing_age_days: kolko dni je inzerat aktivny
        price_history: [{date, price_eur}] od najstarsieho
        local_avg_eur_per_sqm: lokalny priemer z DB (None = fallback)

    Returns:
        ServiceResult so score 0-100 a cenovymi detailmi
    """
    if not is_feature_enabled("use_price_analysis"):
        return ServiceResult.skip_result(SERVICE_NAME, "use_price_analysis=false")

    if area_sqm <= 0 or price_eur <= 0:
        return ServiceResult.error_result(
            SERVICE_NAME,
            f"Neplatne data: price={price_eur}, area={area_sqm}"
        )

    cfg = get_criteria_section("market")
    price_per_sqm = price_eur / area_sqm
    avg = local_avg_eur_per_sqm or get_fallback_avg(distance_km)
    ratio = price_per_sqm / avg if avg > 0 else 1.0

    underpriced_thr = cfg.get("underpriced_threshold_ratio", 0.8)
    overpriced_thr  = cfg.get("price_vs_local_avg_max_ratio", 1.2)

    price_drop = _calculate_price_drop(price_history or [])
    score = _calculate_score(ratio, listing_age_days, price_drop, cfg)

    return ServiceResult(
        ok=True,
        score=score,
        data={
            "price_eur":          price_eur,
            "area_sqm":           area_sqm,
            "price_per_sqm":      round(price_per_sqm, 2),
            "local_avg_per_sqm":  round(avg, 2),
            "price_ratio":        round(ratio, 3),
            "is_underpriced":     ratio <= underpriced_thr,
            "is_overpriced":      ratio > overpriced_thr,
            "listing_age_days":   listing_age_days,
            "price_drop_pct":     price_drop,
            "seller_motivated":   _is_seller_motivated(
                listing_age_days, cfg.get("max_listing_age_days", 180)
            ),
            "used_fallback_avg":  local_avg_eur_per_sqm is None,
        },
        source=SERVICE_NAME,
    )


def get_fallback_avg(distance_km: float) -> float:
    """
    Regionálny fallback priemer EUR/m2 podla vzdialenosti od BA.
    Pouziva sa ked vlastna DB este nema dostatok dat.
    """
    for max_km, avg in REGIONAL_AVG_EUR_PER_SQM:
        if distance_km <= max_km:
            return avg
    return REGIONAL_AVG_EUR_PER_SQM[-1][1]


def calculate_local_avg(prices_per_sqm: list[float]) -> float | None:
    """
    Trimmovany priemer EUR/m2 z nazbieranych inzeratov (odstrihne 10% extremov).
    Vrati None ak malo dat (< 3).
    """
    if len(prices_per_sqm) < 3:
        return None
    s = sorted(prices_per_sqm)
    t = max(1, len(s) // 10)
    trimmed = s[t:-t] if t > 0 else s
    return round(sum(trimmed) / len(trimmed), 2)


def _calculate_price_drop(price_history: list) -> float:
    """
    Percentualny pokles ceny od prveho inzerovania (kladne = cena klesla).
    Vrati 0 ak ziadna historia alebo len 1 zaznam.
    """
    if len(price_history) < 2:
        return 0.0
    try:
        first = float(price_history[0].get("price_eur", 0))
        last  = float(price_history[-1].get("price_eur", 0))
        if first <= 0:
            return 0.0
        return round((first - last) / first * 100.0, 2)
    except (TypeError, KeyError, ZeroDivisionError):
        return 0.0


def _is_seller_motivated(listing_age_days: int, max_days: int) -> bool:
    """True ak inzerat visi dlhsie ako prah (predajca je motivovany)."""
    return listing_age_days > max_days


def _calculate_score(
    price_ratio: float,
    listing_age_days: int,
    price_drop_pct: float,
    cfg: dict,
) -> float:
    """
    Score 0-100 z cenovej analyzy.

    Zakladne pasma:
      ratio <= 0.8  (podhodnoteny)  -> 85-100
      ratio <= 1.0  (pod priemerom) -> 70-85
      ratio <= 1.2  (nad priemerom) -> 40-70
      ratio >  1.2  (predrazeny)    -> 0-40

    Bonusy: dlha inzercia (+5), pokles ceny (+5)
    """
    under = cfg.get("underpriced_threshold_ratio", 0.8)
    over  = cfg.get("price_vs_local_avg_max_ratio", 1.2)
    max_d = cfg.get("max_listing_age_days", 180)

    if price_ratio <= under:
        score = 100.0 - (price_ratio / under) * 15.0
    elif price_ratio <= 1.0:
        score = 85.0 - ((price_ratio - under) / max(1.0 - under, 0.001)) * 15.0
    elif price_ratio <= over:
        score = 70.0 - ((price_ratio - 1.0) / max(over - 1.0, 0.001)) * 30.0
    else:
        excess = min(price_ratio - over, 1.0)
        score  = max(0.0, 40.0 - excess * 40.0)

    if listing_age_days > max_d:
        score = min(100.0, score + 5.0)
    if price_drop_pct >= 5.0:
        score = min(100.0, score + 5.0)

    return round(max(0.0, min(100.0, score)), 2)
