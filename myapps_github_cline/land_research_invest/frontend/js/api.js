// api.js - fetch wrappery pre backend API
async function apiGetConfig() {
  const r = await fetch(API_BASE + "/api/config/");
  if (!r.ok) throw new Error("Config fetch failed: " + r.status);
  return r.json();
}

async function apiAnalyzeOne(parcel) {
  const r = await fetch(API_BASE + "/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(parcel),
  });
  const data = await r.json();
  if (!r.ok) throw new Error(data.error || "Analyze failed");
  return data;
}

async function apiAnalyzeBatch(parcels) {
  const r = await fetch(API_BASE + "/api/parcels/analyze-batch", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ parcels }),
  });
  const data = await r.json();
  if (!r.ok) throw new Error(data.error || "Batch failed");
  return data;
}

// --- Scrape API ---
async function apiScrapeStart() {
  const r = await fetch(API_BASE + "/api/scrape/start", { method: "POST" });
  const data = await r.json();
  if (!r.ok) throw new Error(data.error || "Start failed (" + r.status + ")");
  return data;
}

async function apiScrapeProgress() {
  const r = await fetch(API_BASE + "/api/scrape/progress");
  if (!r.ok) throw new Error("Progress fetch failed: " + r.status);
  return r.json();
}

async function apiScrapeResults() {
  const r = await fetch(API_BASE + "/api/scrape/results");
  if (!r.ok) throw new Error("Results fetch failed: " + r.status);
  return r.json();
}

async function apiScoreSelected(urls) {
  const r = await fetch(API_BASE + "/api/scrape/score-selected", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ urls }),
  });
  const data = await r.json();
  if (!r.ok) throw new Error(data.error || "Score-selected failed (" + r.status + ")");
  return data;
}

async function apiScoreProgress() {
  const r = await fetch(API_BASE + "/api/scrape/score-progress");
  if (!r.ok) throw new Error("Score-progress fetch failed: " + r.status);
  return r.json();
}

