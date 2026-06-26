"""Weather Service - Open-Meteo API. Batch grid."""
import requests, math
from datetime import datetime, timedelta

URL = "https://api.open-meteo.com/v1/forecast"
WC = {0:{"s":"Jasno","e":"Clear","i":"sunny"},1:{"s":"Jasno","e":"Clear","i":"sunny"},
2:{"s":"Oblacno","e":"Cloudy","i":"cloud"},3:{"s":"Zamracene","e":"Overcast","i":"cloud"},
45:{"s":"Hmla","e":"Fog","i":"fog"},51:{"s":"Mrholenie","e":"Drizzle","i":"rain"},
61:{"s":"Dazd","e":"Rain","i":"rain"},63:{"s":"Dazd","e":"Rain","i":"rain"},
65:{"s":"Silny dazd","e":"Heavy rain","i":"rain"},71:{"s":"Sneh","e":"Snow","i":"snow"},
73:{"s":"Sneh","e":"Snow","i":"snow"},80:{"s":"Prehanky","e":"Showers","i":"rain"},
95:{"s":"Burka","e":"Storm","i":"storm"},96:{"s":"Burka","e":"Storm","i":"storm"}}
D = "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,windspeed_10m_max,uv_index_max"

def get_weather_for_point(lat, lon, date=""):
    td = _parse_date(date); ds = td.strftime("%Y-%m-%d")
    params = {"latitude":lat,"longitude":lon,"daily":D,"timezone":"auto","start_date":ds,"end_date":ds}
    try:
        r = requests.get(URL, params=params, timeout=10); r.raise_for_status()
        d = r.json().get("daily",{})
        if not d.get("time"): return {"error":"No data"}
        wc = d.get("weathercode",[0])[0]; wi = WC.get(wc, WC[0])
        return {"date":ds,"lat":lat,"lon":lon,
            "temperature_max":d.get("temperature_2m_max",[0])[0],
            "temperature_min":d.get("temperature_2m_min",[0])[0],
            "precipitation_mm":d.get("precipitation_sum",[0])[0],
            "wind_speed_max":d.get("windspeed_10m_max",[0])[0],
            "uv_index":d.get("uv_index_max",[0])[0],
            "weather_code":wc,"weather_description_sk":wi.get("s",""),
            "weather_description_en":wi.get("e",""),"weather_icon":wi.get("i",""),
            "is_outdoor_friendly":_isof(wc,d),
            "outdoor_recommendation_sk":_rec(wc,"sk"),
            "outdoor_recommendation_en":_rec(wc,"en")}
    except requests.RequestException as e: return {"error":str(e)}

def get_weather_grid(lat, lon, radius_km, date=""):
    td = _parse_date(date); ds = td.strftime("%Y-%m-%d")
    pts = _grid(lat, lon, radius_km); pos = ["NW","N","NE","W","C","E","SW","S","SE"]
    lats = ",".join(str(p[0]) for p in pts)
    lons = ",".join(str(p[1]) for p in pts)
    params = {"latitude":lats,"longitude":lons,"daily":D,"timezone":"auto","start_date":ds,"end_date":ds}
    results = []
    try:
        r = requests.get(URL, params=params, timeout=15); r.raise_for_status()
        data = r.json(); items = data if isinstance(data, list) else [data]
        for i, item in enumerate(items):
            d = item.get("daily",{})
            if d and d.get("time"):
                wc = d.get("weathercode",[0])[0]; wi = WC.get(wc, WC[0])
                results.append({"lat":pts[i][0] if i<len(pts) else lat,
                    "lon":pts[i][1] if i<len(pts) else lon,
                    "grid_position":pos[i] if i<len(pos) else "",
                    "temperature_max":d.get("temperature_2m_max",[0])[0],
                    "temperature_min":d.get("temperature_2m_min",[0])[0],
                    "precipitation_mm":d.get("precipitation_sum",[0])[0],
                    "wind_speed_max":d.get("windspeed_10m_max",[0])[0],
                    "weather_code":wc,"weather_icon":wi.get("i",""),
                    "weather_description_sk":wi.get("s",""),
                    "weather_description_en":wi.get("e",""),
                    "is_outdoor_friendly":_isof(wc,d)})
    except requests.RequestException:
        for i, pt in enumerate(pts):
            w = get_weather_for_point(pt[0], pt[1], ds)
            if not w.get("error"):
                w["grid_position"] = pos[i] if i<len(pos) else ""
                results.append(w)
    sm = _summary(results)
    return {"date":ds,"center":{"lat":lat,"lon":lon},"radius_km":radius_km,"grid_points":results,"summary":sm}

def _grid(clat, clon, rkm):
    lo = rkm/111.0; la = rkm/(111.0*math.cos(math.radians(clat)))
    return [(round(clat+lo*(1-i),4), round(clon+la*(j-1),4)) for i in range(3) for j in range(3)]

def _summary(results):
    if not results: return {"message":"No data"}
    tm = [r["temperature_max"] for r in results if r.get("temperature_max") is not None]
    pr = [r["precipitation_mm"] for r in results if r.get("precipitation_mm") is not None]
    oc = sum(1 for r in results if r.get("is_outdoor_friendly"))
    return {"avg_temp_max":round(sum(tm)/len(tm),1) if tm else 0,
            "max_precipitation_mm":round(max(pr),1) if pr else 0,
            "outdoor_friendly_ratio":str(oc)+"/"+str(len(results))}

def _parse_date(ds):
    if ds:
        try:
            p = datetime.strptime(ds, "%Y-%m-%d")
            mx = datetime.now() + timedelta(days=16)
            if p > mx: return mx
            if p < datetime.now(): return datetime.now()
            return p
        except ValueError: pass
    return datetime.now()

def _isof(wc, d):
    if wc in [0,1,2,3]:
        return (d.get("precipitation_sum",[0])[0] or 0) < 2 and (d.get("windspeed_10m_max",[0])[0] or 0) < 40
    return False

def _rec(wc, lang="en"):
    if wc in [0,1]: return "Idealne na outdoor" if lang=="sk" else "Ideal for outdoor"
    if wc in [2,3]: return "Vhodne, oblacno" if lang=="sk" else "Good, cloudy"
    if wc in [45,48]: return "Hmla" if lang=="sk" else "Fog"
    if wc in [51,53,61,80]: return "Dazd" if lang=="sk" else "Rain - indoor recommended"
    if wc in [55,63,65,81,82]: return "Silny dazd" if lang=="sk" else "Heavy rain"
    if wc in [71,73,75,85,86]: return "Sneh" if lang=="sk" else "Snow"
    if wc in [95,96,99]: return "Burka!" if lang=="sk" else "Storm - stay indoors"
    return "Skontrolujte pocasie" if lang=="sk" else "Check weather"
