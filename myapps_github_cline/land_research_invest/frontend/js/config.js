// config.js - API konstanty a mapovanie farieb
const API_BASE = "";

const REC_COLORS = {
  "STRONG BUY":  { bg: "#2d7a2d", text: "#fff", border: "#1e5c1e", marker: "green" },
  "INVESTIGATE": { bg: "#c8a000", text: "#fff", border: "#a07800", marker: "gold" },
  "CONSIDER":    { bg: "#c85a00", text: "#fff", border: "#a04000", marker: "orange" },
  "SKIP":        { bg: "#a02020", text: "#fff", border: "#7a1010", marker: "red" },
  "N/A":         { bg: "#555",    text: "#fff", border: "#333",    marker: "grey" },
};

function recColor(rec) {
  return REC_COLORS[rec] || REC_COLORS["N/A"];
}

function recLabel(rec) {
  const labels = {
    "STRONG BUY":  "SILNA KUPA",
    "INVESTIGATE": "PREVERIT",
    "CONSIDER":    "ZVAZIT",
    "SKIP":        "PRESKOCIT",
  };
  return labels[rec] || rec;
}
