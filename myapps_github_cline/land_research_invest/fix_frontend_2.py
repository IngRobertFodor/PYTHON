"""fix_frontend_2.py — P3c sortable + P4 scroll + P3b auto-dedup"""
JS = r'c:\__TESTAUTOMATION\SCRIPTS\PYTHON\myapps_github_cline\land_research_invest\frontend\js\app.js'
with open(JS, encoding='utf-8') as f:
    js = f.read()

# P3c: Sort state before renderResultsTable
sort_state = '''// P3c: Sort state
let _sortCol = "preliminary_score";
let _sortDir = -1;  // -1 = desc, 1 = asc

function _sortItems(items) {
  return [...items].sort((a, b) => {
    let va, vb;
    if (_sortCol === "preliminary_score") {
      va = a.preliminary_score || 0; vb = b.preliminary_score || 0;
    } else if (_sortCol === "price_eur") {
      va = a.price_eur || 0; vb = b.price_eur || 0;
    } else if (_sortCol === "price_per_sqm") {
      va = a.price_per_sqm > 0 ? a.price_per_sqm : (a.area_sqm > 0 ? a.price_eur/a.area_sqm : 0);
      vb = b.price_per_sqm > 0 ? b.price_per_sqm : (b.area_sqm > 0 ? b.price_eur/b.area_sqm : 0);
    } else if (_sortCol === "area_sqm") {
      va = a.area_sqm || 0; vb = b.area_sqm || 0;
    } else { return 0; }
    return (va - vb) * _sortDir;
  });
}

function _setSortCol(col) {
  if (_sortCol === col) { _sortDir *= -1; }
  else { _sortCol = col; _sortDir = -1; }
  _updateSortHeaders();
  renderResultsTable(_filteredResults || _allResults);
}

function _updateSortHeaders() {
  document.querySelectorAll(".results-table th[data-sort]").forEach(th => {
    th.classList.remove("sort-asc", "sort-desc");
    if (th.dataset.sort === _sortCol)
      th.classList.add(_sortDir === -1 ? "sort-desc" : "sort-asc");
  });
}

'''

old_render_fn = 'function renderResultsTable(items) {'
if '_sortItems' not in js:
    js = js.replace(old_render_fn, sort_state + old_render_fn)
    print('Sort state inserted OK')
else:
    print('Sort state already present')

# Insert sort call at start of renderResultsTable body (after _filteredResults = items)
old_items_loop = '  items.forEach((p, idx) => {'
new_items_loop = '''  // P3c: Apply sort
  items = _sortItems(items);
  _updateSortHeaders();

  items.forEach((p, idx) => {'''
if old_items_loop in js and 'P3c: Apply sort' not in js:
    js = js.replace(old_items_loop, new_items_loop, 1)
    print('Sort-before-loop inserted OK')
else:
    print('Sort-before-loop: already done or not found')

# P4: scroll results-section into view after renderResults
old_render_results_end = '''  fitMapToMarkers();
}'''
new_render_results_end = '''  fitMapToMarkers();

  // P4: Ensure single-parcel VYSLEDKY section is visible
  const _sec = document.querySelector(".results-section");
  if (_sec) {
    _sec.classList.add("results-section-active");
    setTimeout(() => _sec.scrollIntoView({ behavior: "smooth", block: "nearest" }), 120);
  }
}'''

# Only patch the first occurrence (in renderResults, not renderResultsTable)
if 'P4: Ensure single-parcel' not in js:
    # The renderResults function ends with fitMapToMarkers(); }
    # but so does other code. Find it in renderResults context:
    idx = js.find('function renderResults(items)')
    if idx >= 0:
        segment = js[idx:idx+800]
        if 'fitMapToMarkers();\n}' in segment:
            patched_segment = segment.replace('fitMapToMarkers();\n}', new_render_results_end, 1)
            js = js[:idx] + patched_segment + js[idx+800:]
            print('P4 scroll patched OK')
        else:
            print('P4: fitMapToMarkers not found in renderResults segment')
    else:
        print('P4: renderResults not found')
else:
    print('P4 already patched')

# P3b: auto-dedup in _autoLoadLastResults
old_autoload = '''    _allResults = data.results;
    renderResultsTable(_allResults);
    showStatus'''
new_autoload = '''    _allResults = data.results;
    renderResultsTable(_dedupLatestRun(_allResults));
    showStatus'''

if old_autoload in js:
    js = js.replace(old_autoload, new_autoload)
    print('_autoLoadLastResults dedup OK')
else:
    print('ERROR: _autoLoadLastResults not found')

with open(JS, 'w', encoding='utf-8') as f:
    f.write(js)
print('Part 2 saved. Lines:', js.count('\n'))
