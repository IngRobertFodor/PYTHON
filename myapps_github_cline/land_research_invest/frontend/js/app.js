// app.js - hlavna logika

document.addEventListener("DOMContentLoaded", async () => {
  initMap();
  await loadConfigDefaults();
  document.getElementById("btn-analyze").addEventListener("click", onAnalyzeClick);
  document.getElementById("btn-demo").addEventListener("click",    onDemoClick);
  document.getElementById("btn-research").addEventListener("click", onResearchClick);
  document.getElementById("btn-score-selected").addEventListener("click", onScoreSelectedClick);
  document.getElementById("btn-filter-apply").addEventListener("click", applyFilter);
  document.getElementById("btn-filter-reset").addEventListener("click", resetFilter);
  document.getElementById("chk-all").addEventListener("change", onChkAllChange);
  document.getElementById("modal-close").addEventListener("click",  closeModal);
  document.getElementById("modal-overlay").addEventListener("click", e => {
    if (e.target.id === "modal-overlay") closeModal();
  });

  // Auto-resume: ak scraping prave bezi (napr. po refreshi F5), obnov progress bar
  try {
    const p = await apiScrapeProgress();
    if (p.running) {
      const btn = document.getElementById("btn-research");
      btn.disabled = true;
      btn.textContent = "⏳ Prebieha prieskum...";
      showProgressSection(true);
      updateProgressUI(p);
      startProgressPolling();
    }
  } catch (e) { /* backend nedostupny - ignoruj */ }
});

// --- Config ---
async function loadConfigDefaults() {
  try {
    const cfg = await apiGetConfig();
    const price  = cfg.criteria?.price    || {};
    const parcel = cfg.criteria?.parcel   || {};
    const loc    = cfg.criteria?.location || {};
    setVal("f-price-max",   price.max_eur            || 50000);
    setVal("f-area-min",    parcel.min_area_sqm       || 600);
    setVal("f-area-max",    parcel.max_area_sqm       || 1500);
    setVal("f-dist-max",    loc.max_distance_km       || 70);
  } catch (e) {
    console.warn("Config load failed:", e);
  }
}

// --- Formular - analyza 1 pozemku ---
async function onAnalyzeClick() {
  const parcel = {
    title:         getVal("f-title")    || "Moj pozemok",
    url:           getVal("f-url")      || "",
    price_eur:     parseFloat(getVal("f-price"))  || 0,
    area_sqm:      parseFloat(getVal("f-area"))   || 0,
    location_text: getVal("f-location") || "",
    parcel_number: getVal("f-parcel")   || "",
  };
  if (!parcel.location_text || !parcel.price_eur || !parcel.area_sqm) {
    showStatus("Vyplnte: lokalita, cena, vymera.", "error");
    return;
  }
  showStatus("Analyzujem...", "info");
  setLoading(true);
  try {
    const res = await apiAnalyzeOne(parcel);
    renderResults([{ parcel: res.parcel, report: res.report }]);
    showStatus("Analyza dokoncena.", "ok");
  } catch (e) {
    showStatus("Chyba: " + e.message, "error");
  } finally {
    setLoading(false);
  }
}

// --- Demo ---
async function onDemoClick() {
  showStatus("Nacitavam demo pozemky...", "info");
  setLoading(true);
  try {
    const res = await apiAnalyzeBatch(DEMO_PARCELS);
    const items = res.results.map(p => ({ parcel: p, report: p.results?.report_service?.data || {} }));
    renderResults(items);
    showStatus("Demo: " + res.count + " pozemkov analysovanych.", "ok");
  } catch (e) {
    showStatus("Chyba: " + e.message, "error");
  } finally {
    setLoading(false);
  }
}

// --- Render ---
function renderResults(items) {
  clearMarkers();
  const panel = document.getElementById("results-panel");
  panel.innerHTML = "";

  if (!items || items.length === 0) {
    panel.innerHTML = "<p class='no-results'>Ziadne vysledky.</p>";
    return;
  }

  items.forEach(({ parcel, report }) => {
    const card = buildCard(parcel, report);
    panel.appendChild(card);
    addParcelMarker(parcel, report, openModal);
  });

  fitMapToMarkers();
}

function buildCard(parcel, report) {
  const rec  = parcel.recommendation || "N/A";
  const col  = recColor(rec);
  const rf   = report?.red_flags || {};
  const inv  = report?.investment || {};
  const blockers  = rf.blockers || [];
  const warnings  = rf.warnings || [];

  const card = document.createElement("div");
  card.className = "card";
  card.style.borderLeft = "5px solid " + col.bg;

  const budget_st = inv.over_budget    ? "<span class='flag-err'>Nad limitom</span>" : "<span class='flag-ok'>OK</span>";
  const sqm_st    = inv.over_sqm_limit ? "<span class='flag-err'>EUR/m2 vysoke</span>" : "";
  const flags_html = blockers.map(b => `<li class='flag-err'>&#9888; ${b}</li>`).join("") +
                     warnings.map(w => `<li class='flag-warn'>&#9432; ${w}</li>`).join("");

  // EUR/m2 - pouzij z parcely (nastavene pipeline) alebo vypocitaj lokalne
  const ppsm = parcel.price_per_sqm > 0
    ? parcel.price_per_sqm
    : (parcel.area_sqm > 0 ? parcel.price_eur / parcel.area_sqm : 0);
  const ppsmStr = ppsm > 0 ? ppsm.toFixed(2) : "N/A";

  // Link - zobraz len ak URL je realna (nie demo/prazdna)
  const isRealUrl = parcel.url && parcel.url.length > 0
    && !parcel.url.includes("/demo/")
    && parcel.url.startsWith("http");

  // Popisok odkazu podla zdroja:
  // - drazobne zdroje -> "Oznamenie o drazbe (PDF)" (klik = stiahne sken s cenou/vymerou)
  // - realitne portaly -> "Inzerat"
  const DRAZOBNE = ["notarske_drazby", "ske_drazobne_vyhlasky", "obchodny_vestnik"];
  const linkLabel = DRAZOBNE.includes(parcel.source_portal)
    ? "Ozn\u00e1menie o dra\u017ebe (PDF) \u2192"
    : "Inzer\u00e1t \u2192";
  const linkHtml = isRealUrl
    ? `<a class="card-link" href="${parcel.url}" target="_blank">${linkLabel}</a>`
    : "";

  card.innerHTML = `
    <div class="card-header" style="background:${col.bg};color:${col.text}">
      <span class="card-rec">${recLabel(rec)}</span>
      <span class="card-score">${(parcel.final_score||0).toFixed(1)}/100</span>
    </div>
    <div class="card-body">
      <div class="card-title">${parcel.title || "Pozemok"}</div>
      <div class="card-loc">&#128205; ${parcel.location_text || ""}</div>
      <div class="card-nums">
        <span><b>${(parcel.price_eur||0).toLocaleString("sk-SK")} EUR</b></span>
        <span>${(parcel.area_sqm||0).toLocaleString("sk-SK")} m&sup2;</span>
        <span>${ppsmStr} EUR/m&sup2;</span>
        ${budget_st} ${sqm_st}
      </div>
      ${flags_html ? `<ul class="card-flags">${flags_html}</ul>` : ""}
      ${linkHtml}
    </div>
  `;
  card.addEventListener("click", () => openModal(parcel, report));
  return card;
}

// --- Modal ---
function openModal(parcel, report) {
  const text = report?.text_report || "(bez reportu)";
  document.getElementById("modal-title").textContent = parcel.title || "Detail";
  document.getElementById("modal-body").textContent  = text;
  document.getElementById("modal-overlay").style.display = "flex";
}

function closeModal() {
  document.getElementById("modal-overlay").style.display = "none";
}

// --- Helpers ---
function getVal(id) { return (document.getElementById(id)?.value || "").trim(); }
function setVal(id, v) { const el=document.getElementById(id); if(el) el.value=v; }
function setLoading(on) {
  document.getElementById("btn-analyze").disabled = on;
  document.getElementById("btn-demo").disabled    = on;
}
function showStatus(msg, type) {
  const el = document.getElementById("status");
  el.textContent  = msg;
  el.className    = "status " + (type || "");
}

// ----------------------------------------------------------------
// Spustit prieskum — scrape_all + analyze + progress bar
// ----------------------------------------------------------------

let _pollTimer = null;

async function onResearchClick() {
  const btn = document.getElementById("btn-research");
  if (btn.disabled) return;

  try {
    await apiScrapeStart();
  } catch (e) {
    // 409 = uz bezi -> pokracuj v pollingu
    if (!e.message.includes("bezi")) {
      showStatus("Chyba spustenia: " + e.message, "error");
      return;
    }
  }

  btn.disabled = true;
  btn.textContent = "⏳ Prebieha prieskum...";
  showProgressSection(true);
  updateProgressUI({ done: 0, total: 0, percent: 0, running: true, per_source: {} });
  startProgressPolling();
}

function startProgressPolling() {
  if (_pollTimer) clearInterval(_pollTimer);
  _pollTimer = setInterval(async () => {
    try {
      const p = await apiScrapeProgress();
      updateProgressUI(p);
      if (p.finished) {
        stopProgressPolling();
        await onResearchFinished();
      }
    } catch (e) {
      // sietova chyba - pokracuj v pollingu
    }
  }, 2000);
}

function stopProgressPolling() {
  if (_pollTimer) { clearInterval(_pollTimer); _pollTimer = null; }
}

function showProgressSection(visible) {
  const el = document.getElementById("research-progress");
  if (el) el.classList.toggle("hidden", !visible);
}

function updateProgressUI(p) {
  const pct   = p.percent || 0;
  const done  = p.done    || 0;
  const total = p.total   || 0;

  const bar   = document.getElementById("progress-bar");
  const text  = document.getElementById("progress-text");
  const pctEl = document.getElementById("progress-pct");
  const srcs  = document.getElementById("progress-sources");

  if (bar)   bar.style.width = pct + "%";
  if (pctEl) pctEl.textContent = pct + " %";

// ----------------------------------------------------------------
// Výsledková tabuľka + filter
// ----------------------------------------------------------------

let _allResults = [];
let _filteredResults = [];
const _DRAZOBNE_UI = ["notarske_drazby", "ske_drazobne_vyhlasky", "obchodny_vestnik"];

function showTableSection(visible) {
  const el = document.getElementById("results-table-section");
  if (el) el.classList.toggle("hidden", !visible);
}

function prelim_color(score) {
  if (score >= 85) return "#2e7d32";
  if (score >= 70) return "#1565c0";
  if (score >= 50) return "#e65100";
  return "#757575";
}

function renderResultsTable(items) {
  showTableSection(items && items.length > 0);
  const tbody = document.getElementById("results-tbody");
  if (!tbody) return;
  tbody.innerHTML = "";
  _filteredResults = items;
  updateScoreButton();
  const fc = document.getElementById("filter-count");
  if (fc) fc.textContent = (items.length) + " pozemkov";

  items.forEach((p, idx) => {
    const score = (p.preliminary_score || 0).toFixed(1);
    const col   = prelim_color(p.preliminary_score || 0);
    const ppsm  = p.price_per_sqm > 0
      ? p.price_per_sqm.toFixed(0)
      : (p.area_sqm > 0 ? (p.price_eur / p.area_sqm).toFixed(0) : "—");
    const isRealUrl = p.url && p.url.startsWith("http") && !p.url.includes("/demo/");
    const label = _DRAZOBNE_UI.includes(p.source_portal) ? "Dražba PDF →" : "Inzerát →";
    const link  = isRealUrl
      ? `<a href="${p.url}" target="_blank" class="tbl-link">${label}</a>`
      : "—";
    const tr = document.createElement("tr");
    tr.dataset.url = p.url || "";
    tr.innerHTML = `
      <td><input type="checkbox" class="row-chk" data-url="${p.url || ""}"></td>
      <td class="tbl-num">${idx + 1}</td>
      <td><span class="prelim-badge" style="background:${col}">${score}</span></td>
      <td class="tbl-src">${(p.source_portal||"").replace(/_/g," ")}</td>
      <td class="tbl-loc">${p.location_text||"—"}</td>
      <td class="tbl-price">${p.price_eur>0?p.price_eur.toLocaleString("sk-SK"):"—"}</td>
      <td>${p.area_sqm>0?p.area_sqm.toLocaleString("sk-SK"):"—"}</td>
      <td>${ppsm}</td>
      <td>${link}</td>`;
    tr.addEventListener("click", e => {
      if (e.target.tagName==="INPUT"||e.target.tagName==="A") return;
      openModal(p, p.results?.report_service?.data||{});
    });
    tr.querySelector(".row-chk").addEventListener("change", () => updateScoreButton());
    tbody.appendChild(tr);
  });
}

function applyFilter() {
  const zdroj = document.getElementById("filter-zdroj").value;
  const cena  = parseFloat(document.getElementById("filter-cena").value) || Infinity;
  const vym   = parseFloat(document.getElementById("filter-vymera").value) || 0;
  renderResultsTable(_allResults.filter(p =>
    (!zdroj || p.source_portal === zdroj) &&
    (p.price_eur === 0 || p.price_eur <= cena) &&
    (p.area_sqm  === 0 || p.area_sqm  >= vym)
  ));
}

function resetFilter() {
  document.getElementById("filter-zdroj").value  = "";
  document.getElementById("filter-cena").value   = "";
  document.getElementById("filter-vymera").value = "";
  renderResultsTable(_allResults);
}

function onChkAllChange(e) {
  document.querySelectorAll(".row-chk").forEach(c => { c.checked = e.target.checked; });
  updateScoreButton();
}

function getSelectedUrls() {

// ----------------------------------------------------------------
// Plný scoring vybraných parciel
// ----------------------------------------------------------------

let _scoreTimer = null;

async function onScoreSelectedClick() {
  const btn  = document.getElementById("btn-score-selected");
  const urls = getSelectedUrls();
  if (!urls.length) return;
  try {
    await apiScoreSelected(urls);
  } catch (e) {
    showStatus("Chyba scoringu: " + e.message, "error");
    return;
  }
  btn.disabled = true;
  showScoreProgress(true);
  updateScoreProgressUI({ done: 0, total: urls.length, percent: 0, running: true });
  startScorePolling(urls);
}

function startScorePolling(urls) {
  if (_scoreTimer) clearInterval(_scoreTimer);
  _scoreTimer = setInterval(async () => {
    try {
      const p = await apiScoreProgress();
      updateScoreProgressUI(p);
      if (p.finished) { stopScorePolling(); await onScoringFinished(urls); }
    } catch (e) {}
  }, 2000);
}

function stopScorePolling() {
  if (_scoreTimer) { clearInterval(_scoreTimer); _scoreTimer = null; }
}

function showScoreProgress(visible) {
  const el = document.getElementById("score-progress-wrap");
  if (el) el.classList.toggle("hidden", !visible);
}

function updateScoreProgressUI(p) {
  const pct  = p.percent || 0;
  const bar  = document.getElementById("score-progress-bar");
  const text = document.getElementById("score-progress-text");
  const pctE = document.getElementById("score-progress-pct");
  if (bar)  bar.style.width  = pct + "%";
  if (pctE) pctE.textContent = pct + " %";
  if (text) text.textContent = p.finished
    ? "Hotovo"
    : (p.done||0) + " / " + (p.total||0) + " skórovaných";
}

async function onScoringFinished(scoredUrls) {
  const btn = document.getElementById("btn-score-selected");
  try {
    const data  = await apiScrapeResults();
    _allResults = data.results || [];
    renderResultsTable(_allResults);
    // Mapa len pre skórované parcely s GPS
    const scored = _allResults.filter(p =>
      scoredUrls.includes(p.url) && p.final_score > 0 && p.lat && p.lon);
    if (scored.length > 0) {
      clearMarkers();
      scored.forEach(p => addParcelMarker(p, p.results?.report_service?.data||{}, openModal));
      fitMapToMarkers();
    }
    showStatus("Scoring dokonceny: " + scoredUrls.length + " pozemkov.", "ok");
    if (btn) btn.disabled = false;
    showScoreProgress(false);
  } catch (e) {
    showStatus("Chyba po scoringu: " + e.message, "error");
    if (btn) btn.disabled = false;
  }
}

  return Array.from(document.querySelectorAll(".row-chk:checked"))
    .map(c => c.dataset.url).filter(Boolean);
}

function updateScoreButton() {
  const btn = document.getElementById("btn-score-selected");
  const n   = getSelectedUrls().length;
  if (!btn) return;
  btn.disabled    = n === 0;
  btn.textContent = `★ Skórovať vybrané (${n})`;
}


  if (p.finished) {
    if (text) text.textContent = "Hotovo — " + (p.total_parcels || 0) + " pozemkov";
  } else if (p.running) {
    if (text) text.textContent = done + " / " + total + " zdrojov";
  } else {
    if (text) text.textContent = "Pripravujem...";
  }

  // Per-source tabuľka
  if (srcs && p.per_source) {
    srcs.innerHTML = Object.entries(p.per_source).map(([src, cnt]) => {
      const val = cnt === null ? "⏳" : cnt;
      const cls = cnt === null ? "src-running" : (cnt > 0 ? "src-done" : "src-zero");
      return `<span class="src-chip ${cls}">${src.replace(/_/g," ")}: ${val}</span>`;
    }).join("");
  }
}

async function onResearchFinished() {
  const btn = document.getElementById("btn-research");
  try {
    const data = await apiScrapeResults();
    _allResults = data.results || [];
    renderResultsTable(_allResults);
    showStatus("Prieskum dokonceny: " + data.count + " pozemkov.", "ok");
    if (btn) { btn.disabled = false; btn.textContent = "▶▶ Spustiť prieskum"; }
    showProgressSection(false);
  } catch (e) {
    showStatus("Chyba nacitania vysledkov: " + e.message, "error");
    if (btn) { btn.disabled = false; btn.textContent = "▶▶ Spustiť prieskum"; }
  }
}

