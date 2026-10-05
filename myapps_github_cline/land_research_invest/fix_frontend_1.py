"""fix_frontend_1.py — P3a/P3b/P3c/P4 changes to app.js part 1"""
JS = r'c:\__TESTAUTOMATION\SCRIPTS\PYTHON\myapps_github_cline\land_research_invest\frontend\js\app.js'
with open(JS, encoding='utf-8') as f:
    js = f.read()

# P3a+P3b: Replace applyFilter
old_apply = '''function applyFilter() {
  const zdroj = document.getElementById("filter-zdroj").value;
  const cena  = parseFloat(document.getElementById("filter-cena").value) || Infinity;
  const vym   = parseFloat(document.getElementById("filter-vymera").value) || 0;
  const skore = parseFloat(document.getElementById("filter-skore").value) || 0;
  const gemOnly = document.getElementById("filter-gem")?.checked || false;
  const wlOnly  = document.getElementById("filter-watchlist")?.checked || false;
  const wl = wlOnly ? wlLoad() : null;
  renderResultsTable(_allResults.filter(p => {
    if (zdroj && p.source_portal !== zdroj) return false;
    if (p.price_eur > 0 && p.price_eur > cena) return false;
    if (p.area_sqm  > 0 && p.area_sqm  < vym)  return false;
    if ((p.preliminary_score || 0) < skore) return false;
    if (gemOnly) {
      const ov = p.results && p.results.overpass_service && p.results.overpass_service.data;
      if (!ov || !ov.is_gem_candidate) return false;
    }
    if (wl && !wl.has(p.url)) return false;
    return true;
  }));
}'''

new_apply = '''// P3b: Dedup — zobraz len najnovsí run_id pre kazdu URL
function _dedupLatestRun(items) {
  let maxRun = 0;
  items.forEach(p => { if ((p.run_id || 0) > maxRun) maxRun = p.run_id || 0; });
  if (maxRun === 0) return items;
  return items.filter(p => (p.run_id || 0) === maxRun);
}

// P3a: Skupinovy filter zdrojov
const _DRAZOBNE_SOURCES_UI  = ["ske_drazobne_vyhlasky", "notarske_drazby", "obchodny_vestnik"];
const _INZERAT_SOURCES_UI   = ["nehnutelnosti_sk", "topreality_sk", "reality_sk"];

function applyFilter() {
  const zdroj     = document.getElementById("filter-zdroj").value;
  const cena      = parseFloat(document.getElementById("filter-cena").value) || Infinity;
  const vym       = parseFloat(document.getElementById("filter-vymera").value) || 0;
  const skore     = parseFloat(document.getElementById("filter-skore").value) || 0;
  const gemOnly   = document.getElementById("filter-gem")?.checked || false;
  const wlOnly    = document.getElementById("filter-watchlist")?.checked || false;
  const latestRun = document.getElementById("filter-latest-run")?.checked !== false;
  const typeFilter = document.querySelector(".filter-type-btn.active")?.dataset.ftype || "";
  const wl = wlOnly ? wlLoad() : null;
  let data = latestRun ? _dedupLatestRun(_allResults) : _allResults;
  renderResultsTable(data.filter(p => {
    if (zdroj && p.source_portal !== zdroj) return false;
    if (typeFilter === "drazby"   && !_DRAZOBNE_SOURCES_UI.includes(p.source_portal))  return false;
    if (typeFilter === "inzeraty" && !_INZERAT_SOURCES_UI.includes(p.source_portal)) return false;
    if (typeFilter === "spf"      && p.source_portal !== "spf") return false;
    if (p.price_eur > 0 && p.price_eur > cena) return false;
    if (p.area_sqm  > 0 && p.area_sqm  < vym)  return false;
    if ((p.preliminary_score || 0) < skore) return false;
    if (gemOnly) {
      const ov = p.results && p.results.overpass_service && p.results.overpass_service.data;
      if (!ov || !ov.is_gem_candidate) return false;
    }
    if (wl && !wl.has(p.url)) return false;
    return true;
  }));
}'''

if old_apply in js:
    js = js.replace(old_apply, new_apply)
    print('applyFilter patched OK')
else:
    print('ERROR: applyFilter not found')

# P3b reset
old_reset = '''function resetFilter() {
  document.getElementById("filter-zdroj").value  = "";
  document.getElementById("filter-cena").value   = "";
  document.getElementById("filter-vymera").value = "";
  document.getElementById("filter-skore").value  = "";
  const gemChk = document.getElementById("filter-gem");
  if (gemChk) gemChk.checked = false;
  const wlChk = document.getElementById("filter-watchlist");
  if (wlChk) wlChk.checked = false;
  renderResultsTable(_allResults);
}'''

new_reset = '''function resetFilter() {
  document.getElementById("filter-zdroj").value  = "";
  document.getElementById("filter-cena").value   = "";
  document.getElementById("filter-vymera").value = "";
  document.getElementById("filter-skore").value  = "";
  const gemChk = document.getElementById("filter-gem");
  if (gemChk) gemChk.checked = false;
  const wlChk = document.getElementById("filter-watchlist");
  if (wlChk) wlChk.checked = false;
  document.querySelectorAll(".filter-type-btn").forEach(b => b.classList.remove("active"));
  renderResultsTable(_dedupLatestRun(_allResults));
}'''

if old_reset in js:
    js = js.replace(old_reset, new_reset)
    print('resetFilter patched OK')
else:
    print('ERROR: resetFilter not found')

with open(JS, 'w', encoding='utf-8') as f:
    f.write(js)
print('Part 1 saved. Lines:', js.count('\n'))
