"""Script to update preliminary_score function with P1+P2 improvements."""
import re

path = r'c:\__TESTAUTOMATION\SCRIPTS\PYTHON\myapps_github_cline\land_research_invest\backend\services\scoring_service.py'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Find the start of preliminary_score function and end (next def at same indent)
start_marker = 'def preliminary_score(parcel: Parcel) -> Parcel:'
end_marker = 'def _get_recommendation(score: float, thresholds: dict) -> str:'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

if start_idx == -1 or end_idx == -1:
    print(f"ERROR: Could not find markers. start={start_idx}, end={end_idx}")
    exit(1)

old_func = content[start_idx:end_idx]
print(f"Found old function ({len(old_func)} chars, {old_func.count(chr(10))} lines)")

new_func = '''def preliminary_score(parcel: Parcel) -> Parcel:
    """
    Lacny pre-scoring pozemku BEZ HTTP volani.
    Pouziva iba data dostupne priamo po scrape_all():
      price_eur, area_sqm, price_per_sqm, source_portal, location_text.

    Nastavi parcel.preliminary_score (0-100) a parcel.prelim_recommendation.
    Modifikuje parcel in-place a vrati ho spat.

    Komponenty (vazeny priemer):
      price_score    (30%) -- cena v konfigurovanom rozsahu
      area_score     (25%) -- vymera v konfigurovanom rozsahu
      ppsm_score     (20%) -- EUR/m2 pod limitom (P1: 0 ak suspicious)
      dist_score     (10%) -- odhad vzdialenosti od BA z location_text (P2)
      source_bonus   (10%) -- drazbove zdroje = bonus (podhodnotene)
      data_quality   ( 5%) -- penalizacia za chybajuce polia

    P1: ppsm < 1.5 EUR/m2 z inzeratovych portalov -> ppsm_score=0
        (pravdepodobna parsovacia chyba, nie realna cena)
    P2: vzdialenost od BA odhadnuta z location_text pre drazbove zdroje
        -> penalizacia za priilis vzdialene lokality
    """
    from config_loader import get_criteria, get_scoring

    cfg        = get_criteria()
    price_cfg  = cfg.get("price",  {})
    parcel_cfg = cfg.get("parcel", {})
    thresholds = get_scoring().get("thresholds", {})

    min_eur   = float(price_cfg.get("min_eur",  0))
    max_eur   = float(price_cfg.get("max_eur",  10000))
    max_ppsm  = float(price_cfg.get("max_price_per_sqm_eur", 100))
    min_area  = float(parcel_cfg.get("min_area_sqm", 350))
    max_area  = float(parcel_cfg.get("max_area_sqm", 1000))
    max_km    = float(cfg.get("location", {}).get("max_distance_km", 85))

    # --- Vypocitaj price_per_sqm ak chyba ---
    if parcel.price_per_sqm == 0.0 and parcel.price_eur > 0 and parcel.area_sqm > 0:
        parcel.price_per_sqm = round(parcel.price_eur / parcel.area_sqm, 2)

    price = parcel.price_eur
    area  = parcel.area_sqm
    ppsm  = parcel.price_per_sqm

    # --- P1: Suspicious price flag (inzeratovy portal + ppsm < 1.5) ---
    is_suspicious_price = (
        parcel.source_portal in _INZERAT_SOURCES
        and ppsm > 0
        and ppsm < _SUSPICIOUS_PPSM_THRESHOLD
    )

    # --- price_score ---
    if price <= 0:
        price_score = 50.0          # neznama cena = neutral
    elif min_eur <= price <= max_eur:
        price_score = 100.0
    elif price < min_eur:
        # pod min je tiez zaujimave (lacnejsie nez ocakavame)
        price_score = 80.0
    else:
        # nad max: linearny pokles, pri 3x max -> 0
        ratio = (price - max_eur) / (2 * max_eur + 1)
        price_score = max(0.0, 100.0 - ratio * 100.0)

    # --- area_score ---
    if area <= 0:
        area_score = 50.0
    elif min_area <= area <= max_area:
        area_score = 100.0
    elif area < min_area:
        ratio = (min_area - area) / (min_area + 1)
        area_score = max(0.0, 100.0 - ratio * 60.0)
    else:
        ratio = (area - max_area) / (max_area + 1)
        area_score = max(0.0, 100.0 - ratio * 60.0)

    # --- ppsm_score (P1: nuluj pre suspicious ceny z inzeratov) ---
    if is_suspicious_price:
        ppsm_score = 0.0    # P1: nevierohodna cena z inzeratu -> penalizuj
    elif ppsm <= 0:
        ppsm_score = 50.0
    elif ppsm <= max_ppsm:
        ppsm_score = 100.0
    else:
        ratio = (ppsm - max_ppsm) / (max_ppsm + 1)
        ppsm_score = max(0.0, 100.0 - ratio * 80.0)

    # --- P2: dist_score -- odhad vzdialenosti od BA z location_text ---
    est_km = _estimate_distance_km(parcel.location_text)
    if est_km is None:
        dist_score = 40.0   # neznama poloha -> mierna penalizacia
    elif est_km <= max_km * 0.5:
        dist_score = 100.0  # blizko BA (<42.5km) -> plny bonus
    elif est_km <= max_km:
        ratio = (est_km - max_km * 0.5) / (max_km * 0.5)
        dist_score = max(60.0, 100.0 - ratio * 40.0)
    else:
        # za limitom -> vyznamna penalizacia
        ratio = (est_km - max_km) / (max_km + 1)
        dist_score = max(0.0, 60.0 - ratio * 60.0)

    # --- source_bonus ---
    source_bonus = 80.0 if parcel.source_portal in _DRAZOBNE_SOURCES else 50.0

    # --- data_quality ---
    has_price = price > 0
    has_area  = area  > 0
    if has_price and has_area:
        data_quality = 100.0
    elif has_price or has_area:
        data_quality = 50.0
    else:
        data_quality = 0.0

    # --- Vazeny priemer (sucet vah = 1.00) ---
    total = (
        price_score  * 0.30 +
        area_score   * 0.25 +
        ppsm_score   * 0.20 +
        dist_score   * 0.10 +
        source_bonus * 0.10 +
        data_quality * 0.05
    )

    parcel.preliminary_score      = round(total, 2)
    parcel.prelim_recommendation  = _get_recommendation(total, thresholds)
    return parcel


'''

new_content = content[:start_idx] + new_func + content[end_idx:]
with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("SUCCESS: preliminary_score updated with P1+P2 improvements")
print(f"New function has {new_func.count(chr(10))} lines")
