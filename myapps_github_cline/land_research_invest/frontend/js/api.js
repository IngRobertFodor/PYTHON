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
