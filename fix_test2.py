import pathlib
p = pathlib.Path(r'C:\__TESTAUTOMATION\SCRIPTS\PYTHON\myapps_github_cline\land_research_invest\tests\test_scraper_service.py')
lines = p.read_text(encoding='utf-8').splitlines(keepends=True)
# Keep only lines 1-354 (index 0-353), drop 354+ (duplicates in TestFetchHtmlRetry)
clean = lines[:354]
# Ensure file ends with newline
if clean and not clean[-1].endswith('\n'):
    clean[-1] += '\n'
p.write_text(''.join(clean), encoding='utf-8')
print('OK, lines:', len(clean))
# Verify no stray scrape_all without _scrape_one mock after line 222
text = ''.join(clean)
# Find all scrape_all() calls (rough check)
import re
calls = [(i+1, l.strip()) for i, l in enumerate(clean) if 'scrape_all()' in l]
for ln, c in calls:
    print(f'  L{ln}: {c}')
