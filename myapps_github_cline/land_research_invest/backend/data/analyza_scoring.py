"""
analyza_scoring.py  —  READ-ONLY diagnostika preliminary_score
===============================================================
Spustenie (z rootu projektu):
    python backend/data/analyza_scoring.py

Cita iba data/parcels.db, nic nemeni.
"""
import sqlite3
from pathlib import Path
from collections import defaultdict

DB_PATH = Path(__file__).parent.parent.parent / "data" / "parcels.db"

def pct(n, total):
    return f"{n:5d}  ({100*n/total:5.1f}%)" if total else f"{n:5d}  (  n/a)"

def avg(lst):
    return sum(lst)/len(lst) if lst else 0.0

def median(lst):
    if not lst: return 0.0
    s = sorted(lst)
    m = len(s)//2
    return (s[m]+s[m-1])/2 if len(s)%2==0 else s[m]

conn = sqlite3.connect(str(DB_PATH))
conn.row_factory = sqlite3.Row
last_run = conn.execute("SELECT MAX(id) FROM runs").fetchone()[0]
rows = conn.execute("""
    SELECT source_portal, price_eur, area_sqm, location_text,
           preliminary_score, prelim_recommendation
    FROM parcels WHERE run_id = ?
""", (last_run,)).fetchall()
N = len(rows)

print(f"\n{'='*65}")
print(f"  DIAGNOSTIKA PREDBEŽNÉHO SCORINGU  —  beh id={last_run}, n={N}")
print(f"{'='*65}")

no_price   = [r for r in rows if (r["price_eur"]  or 0) <= 0]
no_area    = [r for r in rows if (r["area_sqm"]   or 0) <= 0]
no_both    = [r for r in rows if (r["price_eur"]  or 0) <= 0 and (r["area_sqm"] or 0) <= 0]
no_loc     = [r for r in rows if not (r["location_text"] or "").strip()]
incomplete = [r for r in rows if (r["price_eur"] or 0) <= 0 or  (r["area_sqm"] or 0) <= 0]
complete   = [r for r in rows if (r["price_eur"] or 0) > 0  and (r["area_sqm"] or 0) > 0]

# ── O2: Score neuplnych vs kompletnych ───────────────────────────────────────
print(f"\n{'─'*65}")
print(f"  OTÁZKA 2: Skóre neúplných vs. kompletných pozemkov")
print(f"{'─'*65}")
sc_inc  = [r["preliminary_score"] or 0 for r in incomplete]
sc_comp = [r["preliminary_score"] or 0 for r in complete]
print(f"  {'Skupina':<30} {'Počet':>6}  {'Priemer':>8}  {'Medián':>8}  {'Min':>6}  {'Max':>6}")
print(f"  {'─'*30} {'─'*6}  {'─'*8}  {'─'*8}  {'─'*6}  {'─'*6}")
for label, lst in [("Kompletné (cena+výmera)", sc_comp),
                   ("Neúplné (aspoň jedno chýba)", sc_inc)]:
    if lst:
        print(f"  {label:<30} {len(lst):>6}  {avg(lst):>8.1f}  {median(lst):>8.1f}  "
              f"{min(lst):>6.1f}  {max(lst):>6.1f}")

print(f"\n  Priemerné skóre podľa zdroja:")
src_scores = defaultdict(list)
for r in rows:
    src_scores[r["source_portal"] or "?"].append(r["preliminary_score"] or 0)
for s, lst in sorted(src_scores.items(), key=lambda x: -avg(x[1])):
    print(f"    {s:<28}  avg={avg(lst):5.1f}  med={median(lst):5.1f}  n={len(lst)}")

# ── O3: Zmiznutie pri roznych pragoch ────────────────────────────────────────
print(f"\n{'─'*65}")
print(f"  OTÁZKA 3: Koľko pozemkov zmizne pri rôznych prahoch posuvníka?")
print(f"{'─'*65}")
print(f"  {'Prah':>5}  {'Skryté spolu':>14}  {'z toho NEÚPLNÉ':>16}  {'z toho KOMPLET.':>17}")
print(f"  {'─'*5}  {'─'*14}  {'─'*16}  {'─'*17}")
for thr in (30, 40, 50, 60, 70, 75, 80):
    ha = [r for r in rows       if (r["preliminary_score"] or 0) < thr]
    hi = [r for r in incomplete if (r["preliminary_score"] or 0) < thr]
    hc = [r for r in complete   if (r["preliminary_score"] or 0) < thr]
    print(f"  {thr:>5}  {len(ha):>6} ({100*len(ha)/N:4.1f}%)  "
          f"  {len(hi):>6} ({100*len(hi)/max(len(incomplete),1):4.1f}% neúpl)  "
          f"  {len(hc):>6} ({100*len(hc)/max(len(complete),1):4.1f}% kompl)")

# ── O4: Histogram ────────────────────────────────────────────────────────────
print(f"\n{'─'*65}")
print(f"  OTÁZKA 4: Rozdelenie skóre (histogram)")
print(f"{'─'*65}")
bands = [(0,50,"SKIP/CONSIDER    (<50)"),
         (50,70,"CONSIDER/INVEST (50-70)"),
         (70,85,"INVESTIGATE     (70-85)"),
         (85,101,"STRONG BUY      (85+) ")]
for lo, hi, label in bands:
    band = [r for r in rows if lo <= (r["preliminary_score"] or 0) < hi]
    bar = "█" * max(1, len(band)*40//N) if band else ""
    print(f"  {label:<28} {pct(len(band),N)}  {bar}")

# ── O5: Konkretne podozrive pripady ──────────────────────────────────────────
print(f"\n{'─'*65}")
print(f"  OTÁZKA 5: Pozemky — nízke skóre LEN kvôli chýbajúcim dátam")
print(f"  (dražby/SPF, niečo chýba, skóre < 70)")
print(f"{'─'*65}")
DRAZBY = {"ske_drazobne_vyhlasky","notarske_drazby","obchodny_vestnik","spf"}
sus = [r for r in rows
       if (r["source_portal"] or "") in DRAZBY
       and ((r["price_eur"] or 0) <= 0 or (r["area_sqm"] or 0) <= 0)
       and (r["preliminary_score"] or 0) < 70]
sus.sort(key=lambda r: r["preliminary_score"] or 0, reverse=True)
print(f"  Dražby/SPF s chýb. dátami a skóre < 70: {len(sus)} pozemkov\n")
print(f"  {'Skóre':>6}  {'Odp.':>12}  {'Cena':>8}  {'Vým.':>6}  {'Zdroj':<24}  Lokalita")
print(f"  {'─'*6}  {'─'*12}  {'─'*8}  {'─'*6}  {'─'*24}  {'─'*20}")
for r in sus[:20]:
    cena = f"{r['price_eur']:.0f}" if (r["price_eur"] or 0) > 0 else "???"
    vym  = f"{r['area_sqm']:.0f}"  if (r["area_sqm"]  or 0) > 0 else "???"
    lok  = (r["location_text"] or "???")[:22]
    src  = (r["source_portal"] or "?")[:24]
    rec  = (r["prelim_recommendation"] or "?")[:12]
    sc   = r["preliminary_score"] or 0
    print(f"  {sc:>6.1f}  {rec:>12}  {cena:>8}  {vym:>6}  {src:<24}  {lok}")

# ── BONUS: Simulacia "neviem" ─────────────────────────────────────────────────
print(f"\n{'─'*65}")
print(f"  BONUS: Simulácia — chýbajúce dáto = 'neviem' (renorm. váhy)")
print(f"{'─'*65}")
W = {"price":0.30,"area":0.25,"ppsm":0.20,"dist":0.10,"src":0.10,"qual":0.05}
MAX_EUR=10000.0; MIN_AREA=300.0; MAX_AREA=800.0

def sim_score(r):
    price = r["price_eur"] or 0
    area  = r["area_sqm"]  or 0
    loc   = (r["location_text"] or "").strip()
    src   = r["source_portal"] or ""
    comp  = {}
    if price > 0:
        comp["price"] = 100.0 if price<=MAX_EUR else max(0,100-((price-MAX_EUR)/(2*MAX_EUR+1))*100)
    if area > 0:
        if MIN_AREA<=area<=MAX_AREA: comp["area"]=100.0
        elif area<MIN_AREA: comp["area"]=max(0,100-((MIN_AREA-area)/(MIN_AREA+1))*60)
        else:               comp["area"]=max(0,100-((area-MAX_AREA)/(MAX_AREA+1))*60)
    if loc:  comp["dist"] = 80.0
    comp["src"]  = 80.0 if src in DRAZBY else 50.0
    comp["qual"] = 100.0*sum(1 for k in ("price","area","dist") if k in comp)/3
    tw = sum(W[k] for k in comp)
    if tw <= 0: return None, 0.0
    return round(sum(W[k]*v for k,v in comp.items())/tw, 1), round(tw, 2)

upgraded=[]
for r in rows:
    old=r["preliminary_score"] or 0
    new,conf=sim_score(r)
    if new is None: continue
    def band(x): return "SKIP" if x<50 else "CONSIDER" if x<70 else "INVESTIGATE" if x<85 else "STRONG BUY"
    if band(new)!=band(old) and new>old:
        upgraded.append((old,new,conf,r["source_portal"] or "?",r["location_text"] or "?",band(old),band(new)))
upgraded.sort(key=lambda x:x[1],reverse=True)
print(f"  Pozemkov, čo by sa ZLEPŠILI v pásme: {len(upgraded)}")
print(f"  {'Staré':>6}  {'Nové':>6}  {'Ist.':>5}  {'Zdroj':<25}  Zmena pásma")
print(f"  {'─'*6}  {'─'*6}  {'─'*5}  {'─'*25}  {'─'*30}")
for old,new,conf,src,loc,ob,nb in upgraded[:15]:
    print(f"  {old:>6.1f}  {new:>6.1f}  {conf:>5.2f}  {src:<25}  {ob} → {nb}")

print(f"\n{'='*65}")
print(f"  KONIEC DIAGNOSTIKY")
print(f"{'='*65}\n")
conn.close()

