"""url_fetch_service — stiahne a vyparsuje detail pozemku z URL."""
import re
import json


def _normalize_price(raw: str) -> float:
    if not raw: return 0.0
    s = re.sub(r"[\u20acEUReur\s]", "", raw.strip())
    if re.search(r",\d{3}$", s): s = s.replace(",", "")
    elif re.search(r"\.\d{3}$", s): s = s.replace(".", "")
    else: s = s.replace(",", "").replace(".", "")
    try: return float(s)
    except ValueError: return 0.0


def _detect_portal(url: str) -> str:
    u = url.lower()
    if "nehnutelnosti.sk" in u: return "nehnutelnosti_sk"
    if "topreality.sk"    in u: return "topreality_sk"
    if "reality.sk"       in u: return "reality_sk"
    raise ValueError(f"Nepodporovany portal: {url}")


def _extract_og_title(html: str) -> str:
    m = re.search(r'property="og:title"\s+content="([^"]+)"', html)
    if m: return m.group(1).split(" | ")[0].strip()
    m = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
    if m:
        raw = m.group(1)
        for sep in [" | ", " \u2013 ", " - "]:
            if sep in raw: return raw.split(sep)[0].strip()
        return raw.strip()
    return ""


def _extract_desc(html: str, marker: str, max_len: int = 500) -> str:
    m = re.search(marker, html, re.IGNORECASE)
    if not m: return ""
    seg  = html[m.end(): m.end() + 3000]
    text = re.sub(r"<[^>]+>", " ", seg)
    return re.sub(r"\s+", " ", text).strip()[:max_len]


def _title_to_loc(title: str) -> str:
    if not title: return ""
    SKIP = {"pozemok","pozemky","predaj","stavebny","stavebne",
            "stavebny","stavebne","ibv","rodinne","rodinne",
            "na","pre","do","od","v","m2","uz","top","reality"}
    words = title.replace(",", " ").replace("-", " ").split()
    for w in reversed(words):
        wc = w.strip("()[]")
        if len(wc) >= 3 and wc.lower() not in SKIP and not wc[0].isdigit():
            return wc
    return ""


def _parse_nehnutelnosti(html: str, url: str) -> dict:
    from services.scrapers.nehnutelnosti_scraper import (
        extract_jsonld, extract_items_from_graph, _extract_location)
    title = loc = desc = ""
    price_f = area_f = 0.0
    quality = "partial"
    try:
        jsonld = extract_jsonld(html)
        def _deep(obj, k1, k2):
            v1 = v2 = None
            if isinstance(obj, dict):
                if k1 in obj: v1 = obj[k1]
                if k2 in obj: v2 = obj[k2]
                for val in obj.values():
                    r1, r2 = _deep(val, k1, k2)
                    v1 = v1 if v1 is not None else r1
                    v2 = v2 if v2 is not None else r2
            elif isinstance(obj, list):
                for item in obj:
                    r1, r2 = _deep(item, k1, k2)
                    v1 = v1 if v1 is not None else r1
                    v2 = v2 if v2 is not None else r2
            return v1, v2
        ps_obj, fs_obj = _deep(jsonld, "priceSpecification", "floorSize")
        if isinstance(ps_obj, dict):
            raw_p = str(ps_obj.get("price","") or ps_obj.get("minPrice",""))
            pv = _normalize_price(raw_p) if raw_p else 0.0
            if pv > 0: price_f = pv; quality = "structured"
        if isinstance(fs_obj, dict) and fs_obj.get("value"):
            try:
                av = float(str(fs_obj["value"]).replace(" ",""))
                if av > 0: area_f = av; quality = "structured"
            except ValueError: pass
        # Hladame name/description v uzle ktory obsahuje priceSpec alebo floorSize
        def _find_listing_node(obj):
            """Najde uzol obsahujuci priceSpecification alebo floorSize."""
            if isinstance(obj, dict):
                if "priceSpecification" in obj or "floorSize" in obj:
                    return obj
                for v in obj.values():
                    found = _find_listing_node(v)
                    if found: return found
            elif isinstance(obj, list):
                for item in obj:
                    found = _find_listing_node(item)
                    if found: return found
            return None
        listing_node = _find_listing_node(jsonld)
        if listing_node:
            if not title: title = str(listing_node.get("name",""))
            if not desc:  desc  = str(listing_node.get("description",""))[:500]
        if title and not loc: loc = _extract_location(title, url)
    except Exception: pass
    if not title: title = _extract_og_title(html)
    if not loc:
        from services.scrapers.nehnutelnosti_scraper import _extract_location as _el
        loc = _el(title, url)
    if price_f <= 0:
        for pat in [r"(\d{2,3}[\s.]\d{3})\s*[\u20ac]", r"(\d{4,7})\s*[\u20ac]"]:
            pm = re.search(pat, html)
            if pm:
                price_f = _normalize_price(pm.group(1))
                if price_f > 0: break
    if area_f <= 0:
        for pat in [r"(\d{3,5})\s*m\s*[\u00b2\xb2]",  # 984 m²
                    r"Plocha pozemku[^\d]*(\d+)\s*m"]:   # Plocha pozemku: 984 m
            am = re.search(pat, html)
            if am:
                try:
                    area_f = float(am.group(1).replace(" ", ""))
                    if area_f > 0: break
                except ValueError: pass
    if not desc: desc = _extract_desc(html, r"Popis nehnutel")
    ppsm = round(price_f/area_f, 2) if area_f > 0 and price_f > 0 else 0.0
    return {"title": title, "price_eur": price_f, "area_sqm": area_f,
            "location_text": loc, "description": desc,
            "source_portal": "nehnutelnosti_sk", "url": url,
            "price_per_sqm": ppsm, "parse_quality": quality}

def _parse_topreality(html: str, url: str) -> dict:
    title   = _extract_og_title(html)
    title   = re.sub(r"^TOP\s+Reality\s*[-\u2013]\s*", "", title).strip()
    price_f = area_f = ppsm_f = 0.0
    quality = "partial"
    dp = re.search(r'data-price="([\d.]+)"', html)
    if dp:
        val = _normalize_price(dp.group(1))
        if val > 5000:   price_f = val; quality = "structured"
        elif val > 0:    ppsm_f  = val; quality = "structured"
    for pat in [r"(\d+)\s*\n?\s*m\s*<sup>\s*2\s*</sup>",
                r"(\d+)\s*m\s*\u00b2", r"(\d{2,4})\s*m2"]:
        am = re.search(pat, html, re.IGNORECASE)
        if am:
            try:
                v = float(am.group(1).replace(" ",""))
                if 50 <= v <= 50000: area_f = v; break
            except ValueError: pass
    if price_f <= 0 and ppsm_f > 0 and area_f > 0:
        price_f = round(ppsm_f * area_f, 0)
    clean = re.sub(r"<[^>]+>", " ", html)
    lm    = re.search(r"Lokalita\s+([A-Z\u00c0-\u017e][^\s\n]{2,40})", clean)
    loc   = lm.group(1).strip() if lm else _title_to_loc(title)
    desc  = _extract_desc(html, r"Kateg\u00f3ria")
    ppsm  = round(price_f/area_f,2) if area_f > 0 and price_f > 0 else ppsm_f
    return {"title": title, "price_eur": price_f, "area_sqm": area_f,
            "location_text": loc, "description": desc,
            "source_portal": "topreality_sk", "url": url,
            "price_per_sqm": ppsm, "parse_quality": quality}

def _parse_reality(html: str, url: str) -> dict:
    title = loc = desc = ""
    price_f = area_f = ppsm_f = 0.0
    quality = "partial"
    jld_pat = re.compile(
        r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>',
        re.DOTALL | re.IGNORECASE)
    for block in jld_pat.findall(html):
        try: d = json.loads(block.strip())
        except Exception: continue
        t = d.get("@type", "")
        if t == "Product":
            title = title or d.get("name", "")
            offers = d.get("offers", {})
            if isinstance(offers, dict):
                raw_p = str(offers.get("price","") or offers.get("lowPrice",""))
                if raw_p:
                    pv = _normalize_price(raw_p)
                    if pv > 2000:
                        price_f = pv; quality = "structured"
                    elif pv > 0:
                        ppsm_f = pv; quality = "structured"
        if t in ("SingleFamilyResidence","RealEstateListing","House","Place","Residence"):
            fs = d.get("floorSize", {})
            if isinstance(fs, dict) and fs.get("value"):
                try:
                    av = float(fs["value"])
                    if av > 0: area_f = av; quality = "structured"
                except (ValueError, TypeError): pass
            addr = d.get("address", {})
            if isinstance(addr, dict):
                lc = addr.get("streetAddress") or ""
                if not lc or lc.lower() in ("slovensko","slovakia",""):
                    lc = addr.get("addressLocality") or addr.get("name","")
                skip_loc = ("slovensko","slovakia","reality nitra","reality bratislava","")
                if lc and lc.lower() not in skip_loc:
                    loc = loc or lc
    if not title: title = _extract_og_title(html)
    if not loc:   loc   = _title_to_loc(title)
    if area_f <= 0:
        pm = re.search(r"Plocha pozemku[^<\d]*(\d+)", html, re.IGNORECASE)
        if pm:
            try: area_f = float(pm.group(1).replace(" ",""))
            except ValueError: pass
    if price_f <= 0:
        tp = re.search(r"([\d,]+)\s*[\u20ac]", title)
        if tp: price_f = _normalize_price(tp.group(1))
    if price_f <= 0:
        clean = re.sub(r"<[^>]+>", " ", html)
        for pat in [r"(\d{2,3}[,\s]\d{3})\s*[\u20ac]",
                    r"Celkov\u00e1 cena[:\s]*([\d\s,\.]+)\s*[\u20ac]"]:
            m2 = re.search(pat, clean, re.IGNORECASE)
            if m2:
                price_f = _normalize_price(m2.group(1))
                if price_f > 0: break
    if price_f <= 0 and area_f > 0:
        ppm = re.search(r"(\d+)\s*[\u20ac]/m", title, re.IGNORECASE)
        if not ppm: ppm = re.search(r"(\d+)\s*[\u20ac]/m", html[:2000], re.IGNORECASE)
        if ppm: ppsm_f = float(ppm.group(1)); price_f = round(ppsm_f*area_f, 0)
    desc = _extract_desc(html, r"Popis nehnutel|Info\b")
    fm   = re.search(r"Funk[c\u010d].{0,4}vyu\u017eitie[:\s]*([^\n<]{3,60})", html)
    if fm: desc = ("Funkc. vyuzitie: "+fm.group(1).strip()+"\n"+desc)[:500]
    ppsm = round(price_f/area_f,2) if area_f > 0 and price_f > 0 else ppsm_f
    return {"title": title, "price_eur": price_f, "area_sqm": area_f,
            "location_text": loc, "description": desc,
            "source_portal": "reality_sk", "url": url,
            "price_per_sqm": ppsm, "parse_quality": quality}


def fetch_parcel_from_url(url: str) -> dict:
    """Stiahne a vyparsuje detail-stranku pozemku z URL."""
    if not url or not url.startswith("http"):
        raise ValueError(f"Neplatna URL: {url!r}")
    portal = _detect_portal(url)
    html   = _fetch_html(url, portal)
    parsers = {
        "nehnutelnosti_sk": _parse_nehnutelnosti,
        "topreality_sk":    _parse_topreality,
        "reality_sk":       _parse_reality,
    }
    r = parsers[portal](html, url)
    if r["price_per_sqm"] == 0 and r["price_eur"] > 0 and r["area_sqm"] > 0:
        r["price_per_sqm"] = round(r["price_eur"] / r["area_sqm"], 2)
    return r


def _fetch_html(url: str, portal: str) -> str:
    from services.scrapers.nehnutelnosti_scraper import NehnutelnostiScraper
    from services.scrapers.topreality_scraper    import TopRealityScraper
    from services.scrapers.reality_sk_scraper    import RealitySkScraper
    m = {"nehnutelnosti_sk": NehnutelnostiScraper,
         "topreality_sk":    TopRealityScraper,
         "reality_sk":       RealitySkScraper}
    return m[portal]().fetch_html(url)
