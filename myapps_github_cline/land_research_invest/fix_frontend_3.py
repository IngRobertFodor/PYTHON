"""fix_frontend_3.py — index.html P3a/P3b/P3c HTML changes"""

HTML = r'c:\__TESTAUTOMATION\SCRIPTS\PYTHON\myapps_github_cline\land_research_invest\frontend\index.html'
with open(HTML, encoding='utf-8') as f:
    html = f.read()

# P3a + P3b: Insert type filter buttons + latest-run checkbox
old_filter = ('        <button id="btn-filter-apply" class="btn btn-sm">Filtrovať</button>\n'
              '        <button id="btn-filter-reset" class="btn btn-sm btn-outline">Reset</button>')
new_filter = ('        <!-- P3a: Skupinový filter zdrojov -->\n'
              '        <div class="filter-type-group">\n'
              '          <button class="filter-type-btn btn-sm" data-ftype="drazby"   onclick="toggleTypeFilter(this)">&#128296; Dra&#382;by</button>\n'
              '          <button class="filter-type-btn btn-sm" data-ftype="inzeraty" onclick="toggleTypeFilter(this)">&#127991; Inzer&#225;ty</button>\n'
              '          <button class="filter-type-btn btn-sm" data-ftype="spf"      onclick="toggleTypeFilter(this)">&#127963; SPF</button>\n'
              '        </div>\n'
              '        <!-- P3b: Latest run dedup -->\n'
              '        <label class="filter-label" style="display:flex;align-items:center;gap:4px;cursor:pointer">\n'
              '          <input type="checkbox" id="filter-latest-run" checked onchange="applyFilter()"> &#x1F550; Posl. beh\n'
              '        </label>\n'
              '        <button id="btn-filter-apply" class="btn btn-sm">Filtrovať</button>\n'
              '        <button id="btn-filter-reset" class="btn btn-sm btn-outline">Reset</button>')

if old_filter in html:
    html = html.replace(old_filter, new_filter)
    print('P3a+P3b filter HTML added OK')
else:
    print('ERROR: filter anchor not found, checking...')
    idx = html.find('btn-filter-apply')
    print(repr(html[max(0,idx-120):idx+80]))

# P3c: sortable TH — search what we have exactly
import re
m = re.search(r'<th>Sk[oó]re</th>', html)
if m:
    print('Found score TH:', repr(m.group()))
else:
    m2 = re.search(r'<th.*?>[^<]*[Ss]k[oó]re[^<]*</th>', html)
    print('Score TH search:', m2.group() if m2 else 'NOT FOUND')

# Try to replace score/price/sqm headers
old_score_th = re.search(r'(<th>Sk[oó]re</th>)', html)
if old_score_th:
    orig = old_score_th.group(1)
    html = html.replace(orig,
        '<th data-sort="preliminary_score" class="sortable sort-desc" '
        'onclick="_setSortCol(\'preliminary_score\')" title="Triediť podľa skóre">Skóre &#8597;</th>', 1)
    print('Score TH replaced')

old_price_th = '<th>Cena EUR</th>'
if old_price_th in html:
    html = html.replace(old_price_th,
        '<th data-sort="price_eur" class="sortable" '
        'onclick="_setSortCol(\'price_eur\')" title="Triediť podľa ceny">Cena EUR &#8597;</th>')
    print('Price TH replaced')

old_sqm_th = '<th>m&sup2;</th>'
if old_sqm_th in html:
    html = html.replace(old_sqm_th,
        '<th data-sort="area_sqm" class="sortable" '
        'onclick="_setSortCol(\'area_sqm\')" title="Triediť podľa výmery">m&sup2; &#8597;</th>')
    print('Sqm TH replaced')

old_ppsm_th = '<th>EUR/m&sup2;</th>'
if old_ppsm_th in html:
    html = html.replace(old_ppsm_th,
        '<th data-sort="price_per_sqm" class="sortable" '
        'onclick="_setSortCol(\'price_per_sqm\')" title="Triediť podľa EUR/m²">EUR/m&sup2; &#8597;</th>')
    print('PPSM TH replaced')

# cache bust v22 -> v23
count = html.count('?v=22">')
html = html.replace('?v=22">', '?v=23">')
print(f'Cache bust v22->v23: {count} replaced')

with open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print('index.html saved')
