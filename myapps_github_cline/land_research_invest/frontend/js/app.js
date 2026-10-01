// app.js - hlavna logika

document.addEventListener("DOMContentLoaded", async () => {
  // Listenery registrujeme IHNED - pred akymkolvek await
  // (ak await hodi exception, listenery by sa nezaregistrovali)
  initMap();
  document.getElementById("btn-analyze").addEventListener("click", onAnalyzeClick);
  document.getElementById("btn-demo").addEventListener("click",    onDemoClick);
  document.getElementById("btn-research").addEventListener("click", onResearchClick);
  document.getElementById("btn-score-selected").addEventListener("click", onScoreSelectedClick);
  document.getElementById("btn-filter-apply").addEventListener("click", applyFilter);
  document.getElementById("btn-filter-reset").addEventListener("click", resetFilter);
  document.getElementById("chk-all").addEventListener("change", onChkAllChange);
  document.getElementById("btn-export-csv").addEventListener("click",  onExportCsv);
  document.getElementById("btn-export-json").addEventListener("click", onExportJson);
  document.getElementById("modal-close").addEventListener("click",  closeModal);
  document.getElementById("modal-overlay").addEventListener("click", e => {
    if (e.target.id === "modal-overlay") closeModal();
  });

  // Az po registracii listenerov - moze trvat dlhsie / hodit exception
  await loadConfigDefaults();

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
    // Polia "Limity" v sidebari
    setVal("f-price-max", price.max_eur          ?? 10000);
    setVal("f-area-min",  parcel.min_area_sqm     ?? 350);
    setVal("f-area-max",  parcel.max_area_sqm     ?? 1000);
    setVal("f-dist-max",  loc.max_distance_km     ?? 70);
    // Subtitle v hlavicke - reflektuje max_distance_km z criteria.yaml
    const km  = loc.max_distance_km ?? 70;
    const sub = document.getElementById("app-subtitle");
    if (sub) sub.textContent =
      "AI agent pre vyhľadávanie stavebných pozemkov do " + km + " km od Bratislavy";
  } catch (e) {
    // Diagnostika: zobraz chybu priamo v subtitle (viditelne bez konzoly)
    const sub = document.getElementById("app-subtitle");
    if (sub) sub.textContent = "Config error: " + e.message;
    console.warn("loadConfigDefaults failed:", e);
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

// Mapovanie source -> { emoji, label, detailFn }
const _COMP_META = {
  distance_service:       { e: "📍", n: "Vzdialenosť od BA",
    d: r => r.data?.distance_km != null ? r.data.distance_km.toFixed(1)+" km" : "" },
  price_analysis_service: { e: "💰", n: "Cenová analýza",
    d: r => r.data?.price_per_sqm_eur != null ? r.data.price_per_sqm_eur.toFixed(0)+" EUR/m²" : "" },
  flood_service:          { e: "🌊", n: "Záplavy",
    d: r => r.data?.flood_zone ?? "" },
  terrain_service:        { e: "⛰️",  n: "Terén",
    d: r => r.data?.slope_percent != null ? "sklon "+r.data.slope_percent+"%" : "" },
  bpej_service:           { e: "🌱", n: "Pôda (BPEJ)",
    d: r => r.data?.protection_class != null
      ? "trieda "+r.data.protection_class+(r.data.suitable_for_construction?" ✅":" ⚠️") : "" },
  overpass_service:       { e: "🛣️",  n: "Infraštruktúra",
    d: r => {
      const rd = r.data?.road?.distance_m; const el = r.data?.electricity?.distance_m;
      const p = [];
      if (rd != null && rd < 9999) p.push("cesta "+Math.round(rd)+"m");
      if (el != null && el < 9999) p.push("el. "+Math.round(el)+"m");
      return p.join(", ");
    }},
  protected_service:      { e: "🛡️",  n: "Ochranné pásma",
    d: r => r.data?.vvn_safe === false ? "⚠️ VVN" : (r.data?.vtl_safe === false ? "⚠️ VTL" : "OK") },
  zbgis_service:          { e: "📐", n: "Geometria (KN)",
    d: r => r.data?.area_sqm != null ? r.data.area_sqm+" m²" : "" },
  cadastral_service:      { e: "📋", n: "Kataster",
    d: r => r.data?.has_plombs ? "⚠️ plomba" : "" },
};

function _scoreColor(s) {
  if (s == null) return "#aaa";
  if (s >= 85) return "#2e7d32";
  if (s >= 70) return "#1565c0";
  if (s >= 50) return "#e65100";
  return "#a02020";
}

function _recStyle(rec) {
  return { "STRONG BUY": ["#2e7d32","#fff"], "INVESTIGATE": ["#1565c0","#fff"],
           "CONSIDER":   ["#e65100","#fff"], "SKIP":        ["#a02020","#fff"] }[rec] || ["#888","#fff"];
}

function _buildModalHtml(parcel) {
  const results  = parcel.results || {};
  const fs       = parcel.final_score;
  const hasFinal = fs != null && fs > 0;
  const rec      = parcel.recommendation || parcel.prelim_recommendation || "";
  const ps       = parcel.preliminary_score || 0;

  const [rbg, rtx] = _recStyle(rec);
  const scoreHtml = hasFinal
    ? `<div class="modal-final-score">${fs.toFixed(1)}<span style="font-size:.9rem;font-weight:400">/100</span></div>`
    : `<div class="modal-final-score" style="color:#888">${ps.toFixed(1)}<span style="font-size:.9rem;font-weight:400"> pre</span></div>`;
  const recHtml = rec ? `<span class="modal-rec-badge" style="background:${rbg};color:${rtx}">${rec}</span>` : "";
  const labelHtml = hasFinal
    ? `<div class="modal-prelim">Finálne skóre (GIS)</div>`
    : `<div class="modal-prelim">Predbežné skóre — spusti <b>Skórovať</b> pre plný GIS</div>`;

  let html = `<div class="modal-score-header">${scoreHtml}<div>${recHtml}${labelHtml}</div></div>`;

  if (hasFinal && Object.keys(results).length > 0) {
    html += `<div class="modal-section-title">Rozpad skóre — GIS komponenty</div><div class="modal-components">`;
    const ORDER = ["distance_service","price_analysis_service","flood_service","terrain_service",
                   "bpej_service","overpass_service","protected_service","zbgis_service","cadastral_service"];
    ORDER.forEach(src => {
      const r = results[src]; if (!r) return;
      const meta = _COMP_META[src] || { e: "🔹", n: src, d: () => "" };
      const skipped = r.data?.skipped;
      const isErr   = !r.ok && !skipped;
      const s       = skipped ? "—" : (r.score != null ? r.score.toFixed(0) : "—");
      const scolor  = skipped ? "#aaa" : _scoreColor(r.score);
      const detail  = skipped ? "preskočené" : (isErr ? (r.error||"chyba") : meta.d(r));
      const cls     = skipped ? "modal-comp modal-comp-skip" : (isErr ? "modal-comp modal-comp-err" : "modal-comp");
      html += `<div class="${cls}">
        <div class="modal-comp-score" style="color:${scolor}">${s}</div>
        <div class="modal-comp-info">
          <div class="modal-comp-name">${meta.e} ${meta.n}</div>
          ${detail ? `<div class="modal-comp-detail">${detail}</div>` : ""}
        </div></div>`;
    });
    html += `</div>`;

    const ov = results.overpass_service?.data;
    if (ov) {
      const acc = ov.direct_access || {}; const pos = ov.village_position || {};
      html += `<div class="modal-section-title">Infraštruktúra — dostupnosť &amp; poloha</div><div class="modal-infra-row">`;
      if (ov.is_gem_candidate) html += `<span class="gem-badge gem-skvost">🏆 Skvost</span>`;
      if (acc.level) {
        const ac = acc.level==="PRIAMA" ? "gem-priama" : acc.level==="CIASTOCNA" ? "gem-ciastocna" : "";
        html += `<span class="gem-badge ${ac}">🔌 ${acc.level}</span>`;
        if (acc.reason) html += `<span style="font-size:.72rem;color:#555;align-self:center">${acc.reason}</span>`;
      }
      if (pos.position) {
        const pc = pos.position==="OKRAJ" ? "gem-okraj" : pos.position==="STRED" ? "gem-stred" : "gem-mimo";
        const pe = pos.position==="OKRAJ" ? "🏘️" : pos.position==="STRED" ? "🏙️" : "🌾";
        html += `<span class="gem-badge ${pc}">${pe} ${pos.position}</span>`;
        if (pos.reason) html += `<span style="font-size:.72rem;color:#555;align-self:center">${pos.reason}</span>`;
      }
      const bld = ov.buildings || {};
      if (bld.nearest_m != null)
        html += `<span style="font-size:.72rem;color:#555;align-self:center">dom: ${bld.nearest_m} m | 100m: ${bld.count_100m} dom. | 300m: ${bld.count_300m} dom.</span>`;
      html += `</div>`;
    }
  }

  const rep = results.report_service?.data?.text_report;
  if (rep) {
    html += `<div class="modal-section-title">Investičný report</div>
      <div class="modal-report-pre">${rep.replace(/</g,"&lt;").replace(/>/g,"&gt;")}</div>`;
  } else if (!hasFinal) {
    html += `<div style="font-size:.78rem;color:#888;margin-top:8px">Detailný report bude dostupný po GIS scorovaní.</div>`;
  }
  return html;
}

function closeModal() {
  const ov = document.getElementById("modal-overlay");
  if (ov) ov.style.setProperty("display", "none", "important");
}
window.closeModal = closeModal;

function openModal(parcel, _reportLegacy) {
  document.getElementById("modal-title").textContent = parcel.title || "Detail pozemku";
  document.getElementById("modal-body").innerHTML = _buildModalHtml(parcel);
  const ov = document.getElementById("modal-overlay");
  ov.style.removeProperty("display");
  ov.style.setProperty("display", "flex", "important");
}

document.addEventListener("keydown", e => { if (e.key === "Escape") closeModal(); });

// --- Helpers ---
function getVal(id) { return (document.getElementById(id)?.value || "").trim(); }
function setVal(id, v) { const el=document.getElementById(id); if(el) el.value=v; }
function setLoading(on) {
  const ba = document.getElementById("btn-analyze");
  const bd = document.getElementById("btn-demo");
  if (ba) ba.disabled = on;
  if (bd) bd.disabled = on;
}
function showStatus(msg, type) {
  const el = document.getElementById("status");
  if (!el) return;
  el.textContent  = msg;
  el.className    = "status " + (type || "");
}

// ----------------------------------------------------------------
// Spustiť prieskum — scrape_all + analyze + progress bar
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

  if (text) {
    if (p.finished) {
      text.textContent = "Hotovo — " + (p.total_parcels || p.total || 0) + " pozemkov";
    } else if (p.running) {
      text.textContent = done + " / " + total + " zdrojov";
    } else {
      text.textContent = "Pripravávam...";
    }
  }
  if (srcs && p.per_source) {
    srcs.innerHTML = Object.entries(p.per_source).map(([src, cnt]) => {
      const val = cnt === null ? "⏳" : cnt;
      const cls = cnt === null ? "src-running" : (cnt > 0 ? "src-done" : "src-zero");
      return "<span class=\"src-chip " + cls + "\">" + src.replace(/_/g," ") + ": " + val + "</span>";
    }).join("");
  }
}

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

    // Infra badges z overpass_service (dostupne len po plnom GIS scorovani)
    const ov  = p.results && p.results.overpass_service && p.results.overpass_service.data;
    let infraHtml = "—";
    if (ov) {
      const acc = ov.direct_access   || {};
      const pos = ov.village_position || {};
      const gem = ov.is_gem_candidate;
      const accLevel  = acc.level   || "";
      const posLevel  = pos.position || "";
      const accClass  = accLevel === "PRIAMA"    ? "gem-priama"
                      : accLevel === "CIASTOCNA" ? "gem-ciastocna" : "";
      const posClass  = posLevel === "OKRAJ" ? "gem-okraj"
                      : posLevel === "STRED" ? "gem-stred"
                      : posLevel === "MIMO"  ? "gem-mimo" : "";
      const accLabel  = accLevel === "PRIAMA"    ? "🔌 Priama"
                      : accLevel === "CIASTOCNA" ? "🔌 Čiastočná"
                      : accLevel === "ZIADNA"    ? "❌ Žiadna" : "";
      const posLabel  = posLevel === "OKRAJ" ? "🏘️ Okraj"
                      : posLevel === "STRED" ? "🏙️ Stred"
                      : posLevel === "MIMO"  ? "🌾 Mimo" : "";
      const gemHtml   = gem ? `<span class="gem-badge gem-skvost">🏆 Skvost</span>` : "";
      const accHtml   = accLabel ? `<span class="gem-badge ${accClass}">${accLabel}</span>` : "";
      const posHtml   = posLabel ? `<span class="gem-badge ${posClass}">${posLabel}</span>` : "";
      if (gemHtml || accHtml || posHtml) {
        infraHtml = `<div class="badges-cell">${gemHtml}${accHtml}${posHtml}</div>`;
      }
    }

    const tr = document.createElement("tr");
    tr.dataset.url = p.url || "";
    if (ov && ov.is_gem_candidate) tr.classList.add("gem-row");
    tr.innerHTML = `
      <td><input type="checkbox" class="row-chk" data-url="${p.url || ""}"></td>
      <td class="tbl-num">${idx + 1}</td>
      <td><span class="prelim-badge" style="background:${col}">${score}</span></td>
      <td class="tbl-src">${(p.source_portal||"").replace(/_/g," ")}</td>
      <td class="tbl-loc">${p.location_text||"—"}</td>
      <td class="tbl-price">${p.price_eur>0?p.price_eur.toLocaleString("sk-SK"):"—"}</td>
      <td>${p.area_sqm>0?p.area_sqm.toLocaleString("sk-SK"):"—"}</td>
      <td>${ppsm}</td>
      <td>${infraHtml}</td>
      <td>${link}</td>`;
    tr.addEventListener("click", e => {
      if (e.target.tagName==="INPUT"||e.target.tagName==="A") return;
      openModal(p, p.results?.report_service?.data||{});
    });
    tr.querySelector(".row-chk").addEventListener("change", () => updateScoreButton());
    tbody.appendChild(tr);
  });
}
// Globalne dostupna
window.renderResultsTable = renderResultsTable;

function applyFilter() {
  const zdroj = document.getElementById("filter-zdroj").value;
  const cena  = parseFloat(document.getElementById("filter-cena").value) || Infinity;
  const vym   = parseFloat(document.getElementById("filter-vymera").value) || 0;
  const skore = parseFloat(document.getElementById("filter-skore").value) || 0;
  const gemOnly = document.getElementById("filter-gem")?.checked || false;
  renderResultsTable(_allResults.filter(p => {
    if (zdroj && p.source_portal !== zdroj) return false;
    if (p.price_eur > 0 && p.price_eur > cena) return false;
    if (p.area_sqm  > 0 && p.area_sqm  < vym)  return false;
    if ((p.preliminary_score || 0) < skore) return false;
    if (gemOnly) {
      const ov = p.results && p.results.overpass_service && p.results.overpass_service.data;
      if (!ov || !ov.is_gem_candidate) return false;
    }
    return true;
  }));
}

function resetFilter() {
  document.getElementById("filter-zdroj").value  = "";
  document.getElementById("filter-cena").value   = "";
  document.getElementById("filter-vymera").value = "";
  document.getElementById("filter-skore").value  = "";
  const gemChk = document.getElementById("filter-gem");
  if (gemChk) gemChk.checked = false;
  renderResultsTable(_allResults);
}

function onChkAllChange(e) {
  document.querySelectorAll(".row-chk").forEach(c => { c.checked = e.target.checked; });
  updateScoreButton();
}

function getSelectedUrls() {
  return Array.from(document.querySelectorAll('.row-chk:checked'))
    .map(c => c.dataset.url).filter(Boolean);
}

function updateScoreButton() {
  const btn = document.getElementById('btn-score-selected');
  const n   = getSelectedUrls().length;
  if (!btn) return;
  btn.disabled    = n === 0;
  btn.textContent = '★ Skórovať vybrané (' + n + ')';
}

// ----------------------------------------------------------------
// Plýn scoring vybraných parciel
// ----------------------------------------------------------------

let _scoreTimer = null;

async function onScoreSelectedClick() {
  const btn  = document.getElementById('btn-score-selected');
  const urls = getSelectedUrls();
  if (!urls.length) return;
  try {
    await apiScoreSelected(urls);
  } catch (e) {
    showStatus('Chyba skórovania: ' + e.message, 'error');
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
      const prog = await apiScoreProgress();
      updateScoreProgressUI(prog);
      if (prog.finished) { stopScorePolling(); await onScoringFinished(urls); }
    } catch (e) {}
  }, 2000);
}

function stopScorePolling() {
  if (_scoreTimer) { clearInterval(_scoreTimer); _scoreTimer = null; }
}

function showScoreProgress(visible) {
  const el = document.getElementById('score-progress-wrap');
  if (el) el.classList.toggle('hidden', !visible);
}

function updateScoreProgressUI(p) {
  const pct  = p.percent || 0;
  const bar  = document.getElementById('score-progress-bar');
  const txt  = document.getElementById('score-progress-text');
  const pctE = document.getElementById('score-progress-pct');
  if (bar)  bar.style.width  = pct + '%';
  if (pctE) pctE.textContent = pct + ' %';
  if (txt)  txt.textContent  = p.finished
    ? 'Hotovo'
    : (p.done||0) + ' / ' + (p.total||0) + ' skórovaných';
}

async function onScoringFinished(scoredUrls) {
  const btn = document.getElementById('btn-score-selected');
  try {
    const data  = await apiScrapeResults();
    _allResults = data.results || [];
    renderResultsTable(_allResults);
    // Mapa len pre skórované parcely s GPS
    const scored = _allResults.filter(p =>
      scoredUrls.includes(p.url) && p.final_score > 0 && p.lat && p.lon);
    if (scored.length > 0) {
      clearMarkers();
      scored.forEach(q => addParcelMarker(q, q.results?.report_service?.data||{}, openModal));
      fitMapToMarkers();
    }
    showStatus('Skórovanie dokončené: ' + scoredUrls.length + ' pozemkov.', 'ok');
    if (btn) { btn.disabled = false; }
    showScoreProgress(false);
  } catch (e) {
    showStatus('Chyba po skórovaní: ' + e.message, 'error');
    if (btn) btn.disabled = false;
  }
}

// ----------------------------------------------------------------
// Export výsledkov (D5)
// ----------------------------------------------------------------

function onExportCsv() {
  if (!_allResults || _allResults.length === 0) {
    showStatus('Žiadne výsledky na export — najskôr spustite prieskum.', 'error');
    return;
  }
  window.location = API_BASE + '/api/scrape/results.csv';
}

function onExportJson() {
  const data = _filteredResults && _filteredResults.length > 0
    ? _filteredResults
    : _allResults;
  if (!data || data.length === 0) {
    showStatus('Žiadne výsledky na export — najskôr spustite prieskum.', 'error');
    return;
  }
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a   = document.createElement('a');
  a.href     = url;
  a.download = 'pozemky.json';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showStatus('Exportovaných ' + data.length + ' záznamov (JSON).', 'ok');
}

async function onResearchFinished() {
  const btn = document.getElementById("btn-research");
  try {
    const data = await apiScrapeResults();
    _allResults = data.results || [];
    renderResultsTable(_allResults);
    showStatus("Prieskum dokončený: " + data.count + " pozemkov.", "ok");
    if (btn) { btn.disabled = false; btn.textContent = "▶▶ Spustiť prieskum"; }
    showProgressSection(false);
    // Nacitaj diff po dokonceni prieskumu (async, neblokuje UI)
    loadDiffBanner().catch(() => {});
  } catch (e) {
    showStatus("Chyba načítania výsledkov: " + e.message, "error");
    if (btn) { btn.disabled = false; btn.textContent = "▶▶ Spustiť prieskum"; }
  }
}

// ----------------------------------------------------------------
// Diff banner — porovnanie s predoslym behom
// ----------------------------------------------------------------

let _diffData = null;   // posledny nacitany diff
let _diffFilter = null; // aktualny aktivny filter: null | "new" | "price_dropped"

async function loadDiffBanner() {
  const banner = document.getElementById("diff-banner");
  if (!banner) return;
  try {
    const d = await apiScrapeDiff();
    _diffData = d;
    _renderDiffBanner(d);
  } catch (e) {
    // tichy fail — diff nie je kriticka funkcia
  }
}

function _renderDiffBanner(d) {
  const banner = document.getElementById("diff-banner");
  if (!banner) return;
  const s = d.summary || {};
  // Ak prvy beh (note = iba jeden beh) alebo vsetko je "nove" a nic ine -> skry
  if (!s.new && !s.removed && !s.price_dropped) {
    banner.classList.add("hidden");
    return;
  }
  banner.classList.remove("hidden");

  const chips = [];
  if (s.new)           chips.push(`<span class="diff-chip diff-new"   data-filter="new">✨ ${s.new} nových</span>`);
  if (s.price_dropped) chips.push(`<span class="diff-chip diff-cheap" data-filter="price_dropped">📉 ${s.price_dropped} zlacneli</span>`);
  if (s.removed)       chips.push(`<span class="diff-chip diff-gone"  data-filter="removed">🗑️ ${s.removed} zmizlo</span>`);
  if (s.still_here)    chips.push(`<span class="diff-chip diff-same"  data-filter="none">${s.still_here} nezmenených</span>`);

  const note = d.note ? `<span style="font-size:.70rem;color:#888;margin-left:4px">${d.note}</span>` : "";
  banner.innerHTML = `<span class="diff-title">Zmeny od minulého behu:</span>${chips.join("")}${note}`;

  // Listenery na chipy — filter tabulky
  banner.querySelectorAll(".diff-chip[data-filter]").forEach(chip => {
    chip.addEventListener("click", () => {
      const f = chip.dataset.filter;
      if (_diffFilter === f) {
        // Druhy klik = zrus filter
        _diffFilter = null;
        banner.querySelectorAll(".diff-chip").forEach(c => c.classList.remove("diff-filter-active"));
        renderResultsTable(_allResults);
      } else {
        _diffFilter = f;
        banner.querySelectorAll(".diff-chip").forEach(c => c.classList.remove("diff-filter-active"));
        chip.classList.add("diff-filter-active");
        _applyDiffFilter(f);
      }
    });
  });
}

function _applyDiffFilter(filter) {
  if (!_diffData) return;
  let subset;
  if (filter === "new")           subset = _diffData.new           || [];
  else if (filter === "price_dropped") subset = _diffData.price_dropped || [];
  else if (filter === "removed")  subset = _diffData.removed       || [];
  else { renderResultsTable(_allResults); return; }

  // Zobraz len parcely ktore su v submnozine (podla URL)
  const urls = new Set(subset.map(p => p.url));
  const filtered = _allResults.filter(p => urls.has(p.url));
  // Doplnim price_dropped data (price_prev, drop_pct) do zobrazenych zaznamov
  if (filter === "price_dropped") {
    const byUrl = Object.fromEntries((subset).map(p => [p.url, p]));
    renderResultsTable(filtered.map(p => Object.assign({}, byUrl[p.url] || p, p)));
  } else {
    renderResultsTable(filtered);
  }
}

