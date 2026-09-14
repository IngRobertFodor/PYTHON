import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\__TESTAUTOMATION\SCRIPTS\PYTHON\myapps_github_cline\land_research_invest\backend")

from services.scraper_service import scrape_all, SCRAPER_REGISTRY

print("=" * 65)
print("LIVE TEST — PARALELNY SCRAPING (7 zdrojov sucasne)")
print("=" * 65)
print(f"Zdroje: {list(SCRAPER_REGISTRY.keys())}")
print()

t0 = time.monotonic()
parcels = scrape_all()
elapsed = time.monotonic() - t0

print()
print("=" * 65)
print(f"CELKOVY CAS:  {elapsed:.0f}s  ({elapsed/60:.1f} min)")
print(f"SPOLU:        {len(parcels)} unikatnych pozemkov")
print()

# Per-zdroj suhrn
from collections import Counter
by_source = Counter(p.source_portal for p in parcels)
print("Per-zdroj:")
for src, count in sorted(by_source.items(), key=lambda x: -x[1]):
    wp = sum(1 for p in parcels if p.source_portal == src and p.price_eur > 0)
    wa = sum(1 for p in parcels if p.source_portal == src and p.area_sqm > 0)
    print(f"  {src:<30} {count:>4} pozemkov  (cena={wp}, vymera={wa})")
print("=" * 65)
