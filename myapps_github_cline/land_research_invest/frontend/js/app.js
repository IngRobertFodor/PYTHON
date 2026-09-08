// app.js - hlavna logika

document.addEventListener("DOMContentLoaded", async () => {
  initMap();
  await loadConfigDefaults();
  document.getElementById("btn-analyze").addEventListener("click", onAnalyzeClick);
  document.getElementById("btn-demo").addEventListener("click",    onDemoClick);
  document.getElementById("modal-close").addEventListener("click",  closeModal);
  document.getElementById("modal-overlay").addEventListener("click", e => {
    if (e.target.id === "modal-overlay") closeModal();
  });
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
        <span>${(parcel.price_per_sqm||0).toFixed(0)} EUR/m&sup2;</span>
        ${budget_st} ${sqm_st}
      </div>
      ${flags_html ? `<ul class="card-flags">${flags_html}</ul>` : ""}
      ${parcel.url ? `<a class="card-link" href="${parcel.url}" target="_blank">Inzerat &rarr;</a>` : ""}
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
