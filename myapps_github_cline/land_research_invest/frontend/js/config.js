// config.js - API konstanty a mapovanie farieb
const API_BASE = "";

const REC_COLORS = {
  "STRONG BUY":  { bg: "#10b981", text: "#fff", border: "#047857", marker: "green"  },  // emerald-500
  "INVESTIGATE": { bg: "#f59e0b", text: "#fff", border: "#b45309", marker: "gold"   },  // amber-500
  "CONSIDER":    { bg: "#f97316", text: "#fff", border: "#c2410c", marker: "orange" },  // orange-500
  "SKIP":        { bg: "#ef4444", text: "#fff", border: "#b91c1c", marker: "red"    },  // red-500
  "N/A":         { bg: "#64748b", text: "#fff", border: "#334155", marker: "grey"   },  // slate-500
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
