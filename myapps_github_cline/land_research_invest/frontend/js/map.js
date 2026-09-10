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
      cursor:pointer;
    ">${Math.round(score)}</div>`,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
  });

  // Hover tooltip - nazov + skore + odporucanie
  const tooltipHtml = `
    <div style="max-width:220px;line-height:1.4">
      <b style="font-size:.9rem">${parcel.title || "Pozemok"}</b><br>
      <span style="color:${col.bg};font-weight:bold">${recLabel(rec)}</span>
      &nbsp;<span style="font-size:.85rem">${score.toFixed(1)}/100</span><br>
      <span style="font-size:.8rem;color:#555">
        ${(parcel.price_eur || 0).toLocaleString("sk-SK")} EUR &bull;
        ${(parcel.area_sqm  || 0).toLocaleString("sk-SK")} m&sup2;
      </span>
    </div>
  `;

  // Popup pri kliknutí (zdroj + EUR/m2)
  const ppsm = (parcel.price_per_sqm || 0);
  const ppsmStr = ppsm > 0 ? ppsm.toFixed(2) : "N/A";
  // Link zobraz len ak URL je realna (nie demo/prazdna)
  const isRealUrl = parcel.url && parcel.url.length > 0
    && !parcel.url.includes("/demo/")
    && parcel.url.startsWith("http");
  const linkHtml = isRealUrl
    ? `<br><a href="${parcel.url}" target="_blank" style="font-size:.8rem">Inzerat &rarr;</a>`
    : "";

  const popup = `
    <b>${parcel.title || "Pozemok"}</b><br>
    <span style="color:${col.bg};font-weight:bold">${recLabel(rec)}</span>
    &nbsp; ${score.toFixed(1)}/100<br>
    Cena: <b>${(parcel.price_eur || 0).toLocaleString("sk-SK")} EUR</b><br>
    Plocha: ${(parcel.area_sqm || 0).toLocaleString("sk-SK")} m&sup2;<br>
    EUR/m&sup2;: ${ppsmStr}${linkHtml}
  `;

  const marker = L.marker([lat, lon], { icon })
    .addTo(_map)
    .bindTooltip(tooltipHtml, { direction: "top", sticky: false, offset: [0, -20] })
    .bindPopup(popup);

  if (onClickCb) marker.on("click", () => onClickCb(parcel, report));
  _markers.push(marker);
}

function fitMapToMarkers() {
  if (_markers.length === 0) return;
  const group = L.featureGroup(_markers);
  _map.fitBounds(group.getBounds().pad(0.2));
}
