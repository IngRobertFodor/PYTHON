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
  document.getElementById("btn-export-csv").addEventListener("click",       onExportCsv);
  document.getElementById("btn-export-json").addEventListener("click",      onExportJson);
  document.getElementById("btn-export-json-slim").addEventListener("click", onExportJsonSlim);
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
    } else {
      // Auto-load: nacitaj posledny beh z DB (perzistencia medzi restartmi)
      await _autoLoadLastResults();
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
    setVal("f-price-max", price.max_eur          ?? 10000);
    setVal("f-area-min",  parcel.min_area_sqm     ?? 350);
    setVal("f-area-max",  parcel.max_area_sqm     ?? 1000);
    setVal("f-dist-max",  loc.max_distance_km     ?? 70);
    const km  = loc.max_distance_km ?? 70;
    const sub = document.getElementById("app-subtitle");
    if (sub) sub.textContent =
      "AI agent pre vyhľadávanie stavebných pozemkov do " + km + " km od Bratislavy";
  } catch (e) {
    const sub = document.getElementById("app-subtitle");
    if (sub) sub.textContent = "Config error: " + e.message;
    console.warn("loadConfigDefaults failed:", e);
  }
}

// --- Auto-load posledneho behu pri starte (F5 / restart servera) ---
async function _autoLoadLastResults() {
  try {
    const data = await apiScrapeResults();
    if (!data.results || data.results.length === 0) return;
    _allResults = data.results;
    renderResultsTable(_allResults);
    showStatus("Načítaných " + data.count + " pozemkov z posledného behu.", "info");
    // Nacitaj diff (ticho)
    loadDiffBanner().catch(() => {});
  } catch (e) { /* prazdna DB alebo backend nedostupny */ }
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
    d: r => {
      const parts = [];
      const ppsm = r.data?.price_per_sqm;
      const avg  = r.data?.local_avg_per_sqm;
      const ratio = r.data?.price_ratio;
      if (ppsm != null) parts.push(ppsm.toFixed(0)+" EUR/m²");
      if (avg  != null) parts.push("priemer "+avg.toFixed(0));
      if (r.data?.is_underpriced) parts.push("📉 podhodnotené");
      if (r.data?.is_overpriced)  parts.push("📈 nadhodnotené");
      if (r.data?.seller_motivated) parts.push("⏰ motivovaný predajca");
      return parts.join(" · ");
    }},
  flood_service:          { e: "🌊", n: "Záplavy",
    d: r => r.data?.in_flood_zone_q100 === true ? "⚠️ Q100 záplava!" : (r.data?.in_flood_zone_q100 === false ? "✅ mimo záplavy" : "") },
  terrain_service:        { e: "⛰️",  n: "Terén",
    d: r => {
      const parts = [];
      if (r.data?.slope_percent  != null) parts.push("sklon "+r.data.slope_percent+"%");
      if (r.data?.elevation_m    != null) parts.push(r.data.elevation_m+" m n.m.");
      if (r.data?.in_landslide_zone === true)  parts.push("⚠️ zosuv");
      if (r.data?.radon_risk_class  != null)  parts.push("radon tr."+r.data.radon_risk_class);
      return parts.join(", ");
    }},
  bpej_service:           { e: "🌱", n: "Pôda (BPEJ)",
    d: r => {
      const parts = [];
      const cls  = r.data?.protection_class;
      const odv  = r.data?.estimated_odvody_eur_per_m2;
      const suit = r.data?.suitable_for_construction;
      const code = r.data?.bpej_code;
      if (cls  != null) parts.push("trieda "+cls);
      if (code)         parts.push("("+code+")");
      if (odv  != null) parts.push("odvody "+odv.toFixed(2)+" €/m²");
      if (suit === true)  parts.push("✅ vhodná na stavbu");
      if (suit === false) parts.push("⚠️ nevhodná (drahé vyňatie)");
      return parts.join(" · ");
    }},
  overpass_service:       { e: "🛣️",  n: "Infraštruktúra",
    d: r => {
      const parts = [];
      const road = r.data?.road || {};
      const elec = r.data?.electricity || {};
      const noise = r.data?.noise || {};
      const env  = r.data?.environment || {};
      if (road.distance_m != null && road.distance_m < 9999) parts.push("cesta "+Math.round(road.distance_m)+"m");
      if (elec.distance_m != null && elec.distance_m < 9999) parts.push("el. "+Math.round(elec.distance_m)+"m");
      if (noise.motorway_safe === false) parts.push("⚠️ diaľnica");
      if (env.landfill_safe   === false) parts.push("⚠️ skládka");
      if (env.industrial_safe === false) parts.push("⚠️ priemysel");
      return parts.join(", ");
    }},
  protected_service:      { e: "🛡️",  n: "Ochranné pásma",
    d: r => {
      const parts = [];
      if (r.data?.in_natura2000) parts.push("⚠️ Natura 2000");
      if (r.data?.in_chko)       parts.push("⚠️ CHKO");
      if (r.data?.in_np)         parts.push("⚠️ NP");
      if (r.data?.in_npr_pr)     parts.push("⚠️ NPR/PR");
      return parts.length ? parts.join(", ") : "✅ bez ochrany";
    }},
  zbgis_service:          { e: "📐", n: "Geometria (KN)",
    d: r => {
      const parts = [];
      if (r.data?.area_sqm != null) parts.push(r.data.area_sqm+" m²");
      if (r.data?.druh_pozemku && r.data.druh_pozemku !== "neznamy")
        parts.push(r.data.druh_pozemku.replace(/_/g," "));
      return parts.join(" · ");
    }},
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

      // M4: Odhad nakladov na zasietovanie
      const costLines = _estimateConnectionCosts(ov);
      if (costLines.length > 0) {
        html += `<div class="modal-section-title">Odhad nákladov na prípojky</div>
          <div class="modal-infra-row" style="flex-direction:column;align-items:flex-start;gap:4px">`;
        costLines.forEach(l => { html += `<span style="font-size:.76rem">${l}</span>`; });
        html += `<span style="font-size:.68rem;color:#aaa">* orientačný odhad, overenie u dodávateľa nutné</span></div>`;
      }
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

// ----------------------------------------------------------------
// Watchlist — localStorage perzistencia hviezdicky
// ----------------------------------------------------------------

const _WL_KEY = "lri_watchlist";

function wlLoad() {
  try { return new Set(JSON.parse(localStorage.getItem(_WL_KEY) || "[]")); }
  catch { return new Set(); }
}

function wlSave(set) {
  try { localStorage.setItem(_WL_KEY, JSON.stringify([...set])); } catch {}
}

function wlToggle(url) {
  const s = wlLoad();
  if (s.has(url)) s.delete(url); else s.add(url);
  wlSave(s);
  return s.has(url);
}

function wlHas(url) { return wlLoad().has(url); }

function wlCount() { return wlLoad().size; }

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

  // Aktualizuj mapu s dostupnymi suradnicami
  renderPrelimMap(items);

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
    const starred = wlHas(p.url || "");
    tr.innerHTML = `
      <td><input type="checkbox" class="row-chk" data-url="${p.url || ""}"></td>
      <td class="tbl-num">${idx + 1}</td>
      <td><button class="star-btn${starred ? " active" : ""}" data-url="${p.url || ""}" title="Sledovať">${starred ? "★" : "☆"}</button></td>
      <td><span class="prelim-badge" style="background:${col}">${score}</span></td>
      <td class="tbl-src">${(p.source_portal||"").replace(/_/g," ")}</td>
      <td class="tbl-loc">${p.location_text||"—"}</td>
      <td class="tbl-price">${p.price_eur>0?p.price_eur.toLocaleString("sk-SK"):"—"}</td>
      <td>${p.area_sqm>0?p.area_sqm.toLocaleString("sk-SK"):"—"}</td>
      <td>${ppsm}</td>
      <td>${infraHtml}</td>
      <td>${link}</td>`;
    tr.addEventListener("click", e => {
      if (e.target.tagName==="INPUT"||e.target.tagName==="A"||e.target.classList.contains("star-btn")) return;
      openModal(p, p.results?.report_service?.data||{});
    });
    tr.querySelector(".row-chk").addEventListener("change", () => updateScoreButton());
    tr.querySelector(".star-btn").addEventListener("click", e => {
      e.stopPropagation();
      const btn = e.currentTarget;
      const url = btn.dataset.url;
      const isNow = wlToggle(url);
      btn.textContent = isNow ? "★" : "☆";
      btn.classList.toggle("active", isNow);
    });
    tbody.appendChild(tr);
  });
}
// Globalne dostupna
window.renderResultsTable = renderResultsTable;

// --- Mapa pre pre-scored parcely (zobraz ihned po nacitani, bez GIS) ---
function renderPrelimMap(items) {
  clearMarkers();
  let shown = 0;
  items.forEach(p => {
    const lat = p.lat || 0;
    const lon = p.lon || 0;
    if (!lat || !lon) return;
    // Pouzij final_score ak je, inak preliminary_score
    const hasFinal = p.final_score && p.final_score > 0;
    const score = hasFinal ? p.final_score : (p.preliminary_score || 0);
    const rec   = hasFinal
      ? (p.recommendation || "N/A")
      : (p.prelim_recommendation || "N/A");
    // Prelim farba = seda odtien aby sa odlisila od plneho GIS
    const col = hasFinal ? recColor(rec) : _prelimMapColor(score);
    const icon = L.divIcon({
      className: "",
      html: `<div style="background:${col.bg};color:${col.text};border:2px solid ${col.border};
        border-radius:50%;width:30px;height:30px;display:flex;align-items:center;
        justify-content:center;font-weight:bold;font-size:10px;
        box-shadow:0 1px 4px rgba(0,0,0,.35);cursor:pointer;
        opacity:${hasFinal ? 1 : 0.75}">${Math.round(score)}</div>`,
      iconSize: [30, 30], iconAnchor: [15, 15],
    });
    const isReal = p.url && p.url.startsWith("http") && !p.url.includes("/demo/");
    const linkHtml = isReal ? `<br><a href="${p.url}" target="_blank" style="font-size:.78rem">Inzerát →</a>` : "";
    const popup = `<b>${p.title||"Pozemok"}</b><br>
      ${hasFinal ? `<span style="color:${col.bg};font-weight:bold">${rec}</span> ${score.toFixed(1)}/100` : `Prelim: ${score.toFixed(1)}`}<br>
      ${(p.price_eur||0).toLocaleString("sk-SK")} EUR &bull; ${(p.area_sqm||0).toLocaleString("sk-SK")} m²${linkHtml}`;
    const marker = L.marker([lat, lon], { icon })
      .addTo(_map)
      .bindTooltip(`<b>${p.title||"Pozemok"}</b><br>${score.toFixed(1)}${hasFinal?"/100":" pre"}`, { direction:"top", offset:[0,-16] })
      .bindPopup(popup);
    marker.on("click", () => openModal(p, p.results?.report_service?.data||{}));
    _markers.push(marker);
    shown++;
  });
  if (shown > 0) fitMapToMarkers();
}

function _prelimMapColor(score) {
  // Tlmene farby pre pre-scored markery (bez GIS)
  if (score >= 85) return { bg:"#4caf7d", text:"#fff", border:"#2e7d32" };
  if (score >= 70) return { bg:"#5b8fc9", text:"#fff", border:"#1565c0" };
  if (score >= 50) return { bg:"#f0a060", text:"#fff", border:"#e65100" };
  return             { bg:"#bdbdbd", text:"#fff", border:"#757575" };
}

function applyFilter() {
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
}

function resetFilter() {
  document.getElementById("filter-zdroj").value  = "";
  document.getElementById("filter-cena").value   = "";
  document.getElementById("filter-vymera").value = "";
  document.getElementById("filter-skore").value  = "";
  const gemChk = document.getElementById("filter-gem");
  if (gemChk) gemChk.checked = false;
  const wlChk = document.getElementById("filter-watchlist");
  if (wlChk) wlChk.checked = false;
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

function onExportJsonSlim() {
  // Slim export — bez results{} (GIS detaily) — menší súbor pre zdieľanie
  const src = (_filteredResults && _filteredResults.length > 0) ? _filteredResults : _allResults;
  if (!src || src.length === 0) {
    showStatus('Žiadne výsledky na export.', 'error');
    return;
  }
  const slim = src.map(p => ({
    url:                  p.url,
    source_portal:        p.source_portal,
    title:                p.title,
    location_text:        p.location_text,
    price_eur:            p.price_eur,
    area_sqm:             p.area_sqm,
    price_per_sqm:        p.price_per_sqm,
    lat:                  p.lat,
    lon:                  p.lon,
    preliminary_score:    p.preliminary_score,
    prelim_recommendation:p.prelim_recommendation,
    final_score:          p.final_score,
    recommendation:       p.recommendation,
    // J1 skvostu z overpass (len kľúčové polia)
    direct_access:        p.results?.overpass_service?.data?.direct_access?.level  || null,
    village_position:     p.results?.overpass_service?.data?.village_position?.position || null,
    is_gem_candidate:     p.results?.overpass_service?.data?.is_gem_candidate       || false,
    // L3 druh pozemku
    druh_pozemku:         p.results?.zbgis_service?.data?.druh_pozemku || null,
    is_agricultural:      p.results?.zbgis_service?.data?.is_agricultural || false,
  }));
  const blob = new Blob([JSON.stringify(slim, null, 2)], { type: 'application/json;charset=utf-8' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href = url; a.download = 'pozemky_slim.json';
  document.body.appendChild(a); a.click();
  document.body.removeChild(a); URL.revokeObjectURL(url);
  showStatus('Exportovaných ' + slim.length + ' záznamov (JSON slim).', 'ok');
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
  if (!s.new && !s.removed && !s.price_dropped) {
    banner.classList.add("hidden");
    return;
  }
  banner.classList.remove("hidden");

  // Watchlist prienik — koľko sledovaných sa zmenilo
  const wl = wlLoad();
  const wlNew     = wl.size > 0 ? (d.new           || []).filter(p => wl.has(p.url)).length : 0;
  const wlCheap   = wl.size > 0 ? (d.price_dropped || []).filter(p => wl.has(p.url)).length : 0;
  const wlRemoved = wl.size > 0 ? (d.removed       || []).filter(p => wl.has(p.url)).length : 0;

  const chips = [];
  if (s.new)           chips.push(`<span class="diff-chip diff-new"   data-filter="new">✨ ${s.new} nových${wlNew ? ` <b>(⭐${wlNew})</b>` : ""}</span>`);
  if (s.price_dropped) chips.push(`<span class="diff-chip diff-cheap" data-filter="price_dropped">📉 ${s.price_dropped} zlacneli${wlCheap ? ` <b>(⭐${wlCheap})</b>` : ""}</span>`);
  if (s.removed)       chips.push(`<span class="diff-chip diff-gone"  data-filter="removed">🗑️ ${s.removed} zmizlo${wlRemoved ? ` <b>(⭐${wlRemoved})</b>` : ""}</span>`);
  if (s.still_here)    chips.push(`<span class="diff-chip diff-same"  data-filter="none">${s.still_here} nezmenených</span>`);

  const note = d.note ? `<span style="font-size:.70rem;color:#888;margin-left:4px">${d.note}</span>` : "";
  banner.innerHTML = `<span class="diff-title">Zmeny od minulého behu:</span>${chips.join("")}${note}`;

  banner.querySelectorAll(".diff-chip[data-filter]").forEach(chip => {
    chip.addEventListener("click", () => {
      const f = chip.dataset.filter;
      if (_diffFilter === f) {
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

  const urls = new Set(subset.map(p => p.url));
  const filtered = _allResults.filter(p => urls.has(p.url));
  if (filter === "price_dropped") {
    const byUrl = Object.fromEntries((subset).map(p => [p.url, p]));
    renderResultsTable(filtered.map(p => Object.assign({}, byUrl[p.url] || p, p)));
  } else {
    renderResultsTable(filtered);
  }
}

// ----------------------------------------------------------------
// M4: Odhad nakladov na zasietovanie (orientacny sadzobnik)
// Vstup: overpass_service.data
// ----------------------------------------------------------------
function _estimateConnectionCosts(ov) {
  const lines = [];
  if (!ov) return lines;

  const road  = ov.road        || {};
  const elec  = ov.electricity || {};
  const water = ov.water       || {};
  const acc   = ov.direct_access || {};

  // Elektrina - ~100 EUR/m pri podzemnom vedeni, min 2000 EUR
  const elecM = elec.distance_m;
  if (elecM != null && elecM < 9999) {
    if (elecM <= 50) {
      lines.push("⚡ Elektrina: " + Math.round(elecM) + " m → ✅ pri plote (~0–2 000 €)");
    } else if (elecM <= 150) {
      const est = Math.round(elecM * 100 / 1000) * 1000;
      lines.push("⚡ Elektrina: " + Math.round(elecM) + " m → ~" + est.toLocaleString("sk-SK") + " € (odhad)");
    } else {
      const est = Math.round(elecM * 100 / 1000) * 1000;
      lines.push("⚡ Elektrina: " + Math.round(elecM) + " m → ⚠️ ~" + est.toLocaleString("sk-SK") + " € (drahé, overte s ZSDIS)");
    }
  }

  // Cesta - pristupova cesta ~50-200 EUR/m (povrch), min 5000 EUR
  const roadM = road.distance_m;
  if (roadM != null && roadM < 9999) {
    if (roadM <= 20) {
      lines.push("🛣️  Cesta:     " + Math.round(roadM) + " m → ✅ priamy prístup");
    } else if (roadM <= 100) {
      const est = Math.round(roadM * 100 / 1000) * 1000;
      lines.push("🛣️  Cesta:     " + Math.round(roadM) + " m → ~" + est.toLocaleString("sk-SK") + " € (prístupovka)");
    } else {
      const est = Math.round(roadM * 150 / 1000) * 1000;
      lines.push("🛣️  Cesta:     " + Math.round(roadM) + " m → ⚠️ ~" + est.toLocaleString("sk-SK") + " € (drahá prístupovka)");
    }
  }

  // Voda - OSM waterway = vodny tok, NIE vodovod -> upozornenie
  const waterM = water.distance_m;
  if (waterM != null && waterM < 9999 && waterM <= 200) {
    lines.push("💧 Vodný tok:  " + Math.round(waterM) + " m (OSM) — pre vodovod overiť u obce samostatne");
  } else {
    lines.push("💧 Voda:       nezistená do 200 m — studňa alebo obecný vodovod (overiť)");
  }

  return lines;
}

