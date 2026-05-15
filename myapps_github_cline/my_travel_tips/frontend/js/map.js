/**
 * Map Module - Leaflet map with search circle and weather grid
 */
const MapManager = {
    map: null,
    marker: null,
    circle: null,
    weatherMarkers: [],
    poiMarkers: [],

    init() {
        this.map = L.map('map', {
            center: [48.15, 17.11], // Bratislava default
            zoom: 8,
            zoomControl: true
        });

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
            maxZoom: 18
        }).addTo(this.map);

        // Click on map to set location
        this.map.on('click', (e) => {
            this.setLocation(e.latlng.lat, e.latlng.lng);
            // Trigger reverse geocoding
            if (window.App) {
                window.App.onMapClick(e.latlng.lat, e.latlng.lng);
            }
        });
    },

    setLocation(lat, lon) {
        // Remove old marker
        if (this.marker) this.map.removeLayer(this.marker);
        
        // Add new marker
        this.marker = L.marker([lat, lon], {
            icon: L.divIcon({
                className: 'custom-marker',
                html: '<div style="background:var(--primary);width:20px;height:20px;border-radius:50%;border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,.3)"></div>',
                iconSize: [20, 20],
                iconAnchor: [10, 10]
            })
        }).addTo(this.map);

        this.map.setView([lat, lon], 10);
    },

    setRadius(lat, lon, radiusKm) {
        // Remove old circle
        if (this.circle) this.map.removeLayer(this.circle);

        // Draw radius circle
        this.circle = L.circle([lat, lon], {
            radius: radiusKm * 1000,
            color: getComputedStyle(document.documentElement).getPropertyValue('--primary').trim() || '#1b5e83',
            fillColor: getComputedStyle(document.documentElement).getPropertyValue('--secondary').trim() || '#2e86ab',
            fillOpacity: 0.1,
            weight: 2,
            dashArray: '5, 5'
        }).addTo(this.map);

        // Fit map to circle bounds
        this.map.fitBounds(this.circle.getBounds(), { padding: [20, 20] });
    },

    addWeatherGrid(gridPoints) {
        // Clear old weather markers
        this.weatherMarkers.forEach(m => this.map.removeLayer(m));
        this.weatherMarkers = [];

        gridPoints.forEach(point => {
            const marker = L.marker([point.lat, point.lon], {
                icon: L.divIcon({
                    className: 'weather-map-marker',
                    html: `<div style="text-align:center;background:white;border-radius:8px;padding:3px 6px;box-shadow:0 2px 4px rgba(0,0,0,.2);font-size:12px;white-space:nowrap">
                        <span>${point.weather_icon}</span>
                        <span style="font-weight:600">${point.temperature_max}°</span>
                    </div>`,
                    iconSize: [60, 30],
                    iconAnchor: [30, 15]
                })
            }).addTo(this.map);
            this.weatherMarkers.push(marker);
        });
    },

    addPOIMarkers(pois, category) {
        pois.forEach((poi, index) => {
            const color = category === 'mainstream' ? '#1b5e83' : '#7c3aed';
            const marker = L.marker([poi.lat, poi.lon], {
                icon: L.divIcon({
                    className: 'poi-map-marker',
                    html: `<div style="background:${color};color:white;width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;border:2px solid white;box-shadow:0 2px 4px rgba(0,0,0,.3)">${index + 1}</div>`,
                    iconSize: [24, 24],
                    iconAnchor: [12, 12]
                })
            }).addTo(this.map);

            marker.bindPopup(`<strong>${poi.name}</strong><br><small>${poi.distance_km} km</small>`);
            this.poiMarkers.push(marker);
        });
    },

    clearPOIMarkers() {
        this.poiMarkers.forEach(m => this.map.removeLayer(m));
        this.poiMarkers = [];
    },

    invalidateSize() {
        if (this.map) this.map.invalidateSize();
    }
};