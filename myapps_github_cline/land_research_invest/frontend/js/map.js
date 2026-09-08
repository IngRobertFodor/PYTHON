// map.js - Leaflet mapa
let _map = null;
let _markers = [];

function initMap() {
  if (_map) return;
  _map = L.map("map").setView([48.1486, 17.1077], 10);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
    maxZoom: 18,
  }).addTo(_map);
}

function clearMarkers() {
  _markers.forEach(m => _map.removeLayer(m));
  _markers = [];
}

function addParcelMarker(parcel, report, onClickCb) {
  const lat = parcel.lat || 0;
  const lon = parcel.lon || 0;
  if (!lat || !lon) return;

  const rec   = parcel.recommendation || "N/A";
  const col   = recColor(rec);
  const score = parcel.final_score || 0;

  const icon = L.divIcon({
    className: "",
    html: `<div style="
      background:${col.bg};
      color:${col.text};
      border:2px solid ${col.border};
      border-radius:50%;
      width:36px; height:36px;
      display:flex; align-items:center; justify-content:center;
      font-weight:bold; font-size:11px;
      box-shadow:0 2px 6px rgba(0,0,0,.4);
    ">${Math.round(score)}</div>`,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
  });

  const popup = `
    <b>${parcel.title || "Pozemok"}</b><br>
    <span style="color:${col.bg};font-weight:bold">${recLabel(rec)}</span>
    &nbsp; ${score.toFixed(1)}/100<br>
    Cena: <b>${(parcel.price_eur || 0).toLocaleString("sk-SK")} EUR</b><br>
    Plocha: ${(parcel.area_sqm || 0).toLocaleString("sk-SK")} m&sup2;<br>
    EUR/m&sup2;: ${(parcel.price_per_sqm || 0).toFixed(2)}<br>
    <a href="${parcel.url || "#"}" target="_blank">Inzerat &rarr;</a>
  `;

  const marker = L.marker([lat, lon], { icon })
    .addTo(_map)
    .bindPopup(popup);

  if (onClickCb) marker.on("click", () => onClickCb(parcel, report));
  _markers.push(marker);
}

function fitMapToMarkers() {
  if (_markers.length === 0) return;
  const group = L.featureGroup(_markers);
  _map.fitBounds(group.getBounds().pad(0.2));
}
