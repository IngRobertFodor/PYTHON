"""
Diff Service - porovnanie dvoch behov scraperov
================================================
compute_diff(prev, curr) porovnava dva zoznamy parcel (list[dict])
a vracia stitene zmeny pre investora.

Vysledok:
  new          - parcely ktore v prev neboli (nova prilezitost)
  removed      - parcely ktore uz v curr nie su (predane / stiahnuty)
  price_dropped - parcely kde cena klesla o aspon DROP_PCT percent
  still_here   - nezmenene parcely (url v oboch, cena rovnaka)

Kluc porovnania: url  (rovnaky ako dedup kluc v scraper_service)
Bez HTTP, bez dalsich zavislosti.
"""

SERVICE_NAME = "diff_service"

# Minimalny pokles ceny (%) aby sa pocital ako "zlacnenie"
DROP_PCT = 3.0


def compute_diff(prev: list, curr: list) -> dict:
    """
    Porovnaj dva zoznamy parcel.

    Args:
        prev: parcely z predosleho behu  (list[dict])
        curr: parcely z aktualneho behu  (list[dict])

    Returns dict s kluèmi:
        new          list[dict]  - nova v curr, chybala v prev
        removed      list[dict]  - bola v prev, chyba v curr
        price_dropped list[dict] - cena klesla >= DROP_PCT %
                                   kazdy zaznam ma navyse kluce:
                                   price_prev, price_curr, drop_pct
        still_here   int         - pocet nezmeneny (info)
        summary      dict        - {new, removed, price_dropped, still_here}
    """
    prev_by_url = {p["url"]: p for p in prev if p.get("url")}
    curr_by_url = {p["url"]: p for p in curr if p.get("url")}

    prev_urls = set(prev_by_url)
    curr_urls = set(curr_by_url)

    new_urls     = curr_urls - prev_urls
    removed_urls = prev_urls - curr_urls
    common_urls  = prev_urls & curr_urls

    new_parcels     = [curr_by_url[u] for u in new_urls]
    removed_parcels = [prev_by_url[u] for u in removed_urls]

    price_dropped = []
    still_here    = 0
    for u in common_urls:
        p_old = float(prev_by_url[u].get("price_eur") or 0)
        p_new = float(curr_by_url[u].get("price_eur") or 0)
        if p_old > 0 and p_new > 0 and p_new < p_old:
            drop = (p_old - p_new) / p_old * 100
            if drop >= DROP_PCT:
                entry = dict(curr_by_url[u])
                entry["price_prev"] = p_old
                entry["price_curr"] = p_new
                entry["drop_pct"]   = round(drop, 1)
                price_dropped.append(entry)
                continue
        still_here += 1

    # Zorad: nove podla prelim_score desc, zlacnene podla drop_pct desc
    new_parcels.sort(  key=lambda p: p.get("preliminary_score", 0), reverse=True)
    price_dropped.sort(key=lambda p: p.get("drop_pct", 0),          reverse=True)

    return {
        "new":           new_parcels,
        "removed":       removed_parcels,
        "price_dropped": price_dropped,
        "still_here":    still_here,
        "summary": {
            "new":           len(new_parcels),
            "removed":       len(removed_parcels),
            "price_dropped": len(price_dropped),
            "still_here":    still_here,
        },
    }
