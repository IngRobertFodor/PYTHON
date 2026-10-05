"""fix_frontend_4.py — style.css P3/P4 rules + app.js helpers"""

# ===== style.css =====
CSS = r'c:\__TESTAUTOMATION\SCRIPTS\PYTHON\myapps_github_cline\land_research_invest\frontend\css\style.css'
with open(CSS, encoding='utf-8') as f:
    css = f.read()

if '.filter-type-group' not in css:
    extra = (
        '\n/* P3a type-filter buttons */\n'
        '.filter-type-group { display:flex; gap:3px; }\n'
        '.filter-type-btn { background:#e8f0fe; color:#1a3a5c; border:1px solid #c8d8f0;\n'
        '  border-radius:4px; padding:3px 8px; font-size:.73rem; cursor:pointer;\n'
        '  transition:background .12s,color .12s; }\n'
        '.filter-type-btn:hover  { background:#c8d8f0; }\n'
        '.filter-type-btn.active { background:#1a3a5c; color:#fff; border-color:#1a3a5c; }\n'
        '\n/* P3c sortable headers */\n'
        '.results-table th.sortable { cursor:pointer; user-select:none; }\n'
        '.results-table th.sortable:hover { background:#24548a; }\n'
        '.results-table th.sort-asc  { background:#1a5c3a !important; }\n'
        '.results-table th.sort-desc { background:#1a3a5c !important; }\n'
        '\n/* P4 VYSLEDKY section active */\n'
        '.results-section { margin-top:12px; border-top:2px solid transparent;\n'
        '  transition:border-color .3s; }\n'
        '.results-section-active { border-top:2px solid #2e7d32; background:#f0fff4;\n'
        '  border-radius:0 0 8px 8px; padding:4px 0 8px; }\n'
        '.results-section h2 { font-size:.88rem; color:#1a3a5c; margin:8px 0 6px; }\n'
    )
    css = css.rstrip() + '\n' + extra
    with open(CSS, 'w', encoding='utf-8') as f:
        f.write(css)
    print('style.css P3/P4 rules added OK')
else:
    print('style.css already has P3 rules')

# ===== app.js: toggleTypeFilter helper =====
JS = r'c:\__TESTAUTOMATION\SCRIPTS\PYTHON\myapps_github_cline\land_research_invest\frontend\js\app.js'
with open(JS, encoding='utf-8') as f:
    js = f.read()

if 'toggleTypeFilter' not in js:
    helper = (
        '\n// P3a: Toggle skupinovy filter\n'
        'function toggleTypeFilter(btn) {\n'
        '  const wasActive = btn.classList.contains("active");\n'
        '  document.querySelectorAll(".filter-type-btn").forEach(b => b.classList.remove("active"));\n'
        '  if (!wasActive) btn.classList.add("active");\n'
        '  applyFilter();\n'
        '}\n'
        'window.toggleTypeFilter = toggleTypeFilter;\n'
        'window._setSortCol = _setSortCol;\n'
    )
    js = js.rstrip() + '\n' + helper
    with open(JS, 'w', encoding='utf-8') as f:
        f.write(js)
    print('toggleTypeFilter + _setSortCol exported OK. Lines:', js.count('\n'))
else:
    print('toggleTypeFilter already present')

print('\n=== All frontend changes applied ===')
