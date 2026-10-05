"""verify_all.py — sanity checks on all changed files"""
import re

JS   = r'c:\__TESTAUTOMATION\SCRIPTS\PYTHON\myapps_github_cline\land_research_invest\frontend\js\app.js'
HTML = r'c:\__TESTAUTOMATION\SCRIPTS\PYTHON\myapps_github_cline\land_research_invest\frontend\index.html'
CSS  = r'c:\__TESTAUTOMATION\SCRIPTS\PYTHON\myapps_github_cline\land_research_invest\frontend\css\style.css'
SVC  = r'c:\__TESTAUTOMATION\SCRIPTS\PYTHON\myapps_github_cline\land_research_invest\backend\services\scoring_service.py'
TST  = r'c:\__TESTAUTOMATION\SCRIPTS\PYTHON\myapps_github_cline\land_research_invest\tests\test_scoring_service.py'

checks = {
    JS: [
        '_dedupLatestRun',
        '_sortItems', '_setSortCol', '_updateSortHeaders',
        'toggleTypeFilter', 'filter-latest-run',
        'results-section-active',
        '_DRAZOBNE_SOURCES_UI',
        'window._setSortCol',
    ],
    HTML: [
        'filter-type-group', 'filter-latest-run',
        'data-sort="preliminary_score"',
        'data-sort="price_eur"',
        'data-sort="area_sqm"',
        'data-sort="price_per_sqm"',
        '?v=23"',
    ],
    CSS: [
        '.filter-type-group', '.filter-type-btn',
        'sort-asc', 'sort-desc',
        'results-section-active',
    ],
    SVC: [
        '_estimate_distance_km',
        '_normalize_loc',
        '_INZERAT_SOURCES',
        '_SUSPICIOUS_PPSM_THRESHOLD',
        'kosice',
    ],
    TST: [
        'TestPrelimScoringP1SuspiciousPrice',
        'TestPrelimScoringP2DistanceEstimate',
        '_estimate_distance_km',
        '_INZERAT_SOURCES',
    ],
}

all_ok = True
for path, patterns in checks.items():
    short = path.split('\\')[-1]
    with open(path, encoding='utf-8') as f:
        content = f.read()
    for p in patterns:
        found = bool(re.search(re.escape(p), content))
        if not found:
            print(f'MISSING in {short}: {p!r}')
            all_ok = False
        else:
            print(f'  OK {short}: {p!r}')

print()
print('=== ALL CHECKS PASSED ===' if all_ok else '=== SOME CHECKS FAILED ===')
