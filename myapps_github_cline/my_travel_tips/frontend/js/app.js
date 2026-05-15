/**
 * Main Application Logic - Fodor Travel TIPs
 * Handles search, categories, map interaction, and data fetching.
 */
const App = {
    selectedLocation: null,
    radiusKm: 25,
    travelDate: '',
    weatherData: null,

    init() {
        MapManager.init();

        // Set default date
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('travel-date').value = today;
        document.getElementById('travel-date').min = today;
        const maxDate = new Date();
        maxDate.setDate(maxDate.getDate() + 16);
        document.getElementById('travel-date').max = maxDate.toISOString().split('T')[0];

        this.bindEvents();
        this.bindCategoryEvents();
        setLanguage('sk');
    },

    bindEvents() {
        // Language switch
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                setLanguage(btn.dataset.lang);
            });
        });

        // Search
        document.getElementById('search-btn').addEventListener('click', () => this.searchLocation());
        document.getElementById('location-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.searchLocation();
        });

        // Live suggestions
        let searchTimeout;
        document.getElementById('location-input').addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();
            if (query.length >= 3) {
                searchTimeout = setTimeout(() => this.showSuggestions(query), 300);
            } else {
                this.hideSuggestions();
            }
        });

        // Radius
        document.getElementById('radius-km').addEventListener('change', (e) => {
            this.radiusKm = parseFloat(e.target.value) || 25;
            document.getElementById('radius-time').value = '';
            this.updateMapRadius();
        });

        document.getElementById('radius-time').addEventListener('change', (e) => {
            if (e.target.value.trim()) this.convertTimeToRadius(e.target.value.trim());
        });

        // Date
        document.getElementById('travel-date').addEventListener('change', (e) => {
            this.travelDate = e.target.value;
        });

        // Explore
        document.getElementById('explore-btn').addEventListener('click', () => this.explore());

        // Close suggestions
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.input-group')) this.hideSuggestions();
        });
    },

    // === CATEGORY CHECKBOXES ===
    bindCategoryEvents() {
        // Parent checkbox toggles all children
        document.querySelectorAll('.cat-parent').forEach(parent => {
            parent.addEventListener('change', () => {
                const group = parent.dataset.group;
                const children = document.querySelectorAll(`.cat-child[data-group="${group}"]`);
                children.forEach(child => child.checked = parent.checked);
            });
        });

        // Child checkbox updates parent state
        document.querySelectorAll('.cat-child').forEach(child => {
            child.addEventListener('change', () => {
                const group = child.dataset.group;
                const children = document.querySelectorAll(`.cat-child[data-group="${group}"]`);
                const parent = document.querySelector(`.cat-parent[data-group="${group}"]`);
                const allChecked = Array.from(children).every(c => c.checked);
                const someChecked = Array.from(children).some(c => c.checked);
                parent.checked = allChecked;
                parent.indeterminate = someChecked && !allChecked;
            });
        });

        // Select all / Deselect all
        document.getElementById('cat-select-all').addEventListener('click', () => {
            document.querySelectorAll('.cat-parent, .cat-child').forEach(cb => {
                cb.checked = true;
                cb.indeterminate = false;
            });
        });
        document.getElementById('cat-deselect-all').addEventListener('click', () => {
            document.querySelectorAll('.cat-parent, .cat-child').forEach(cb => {
                cb.checked = false;
                cb.indeterminate = false;
            });
        });
    },

    getSelectedTags() {
        /** Collect all selected tags from checked category checkboxes. */
        const tags = [];
        document.querySelectorAll('.cat-child:checked').forEach(cb => {
            const tagStr = cb.dataset.tags;
            if (tagStr) {
                tagStr.split(',').forEach(tag => {
                    if (tag && !tags.includes(tag)) tags.push(tag);
                });
            }
        });
        return tags;
    },

    // === SEARCH & LOCATION ===
    async searchLocation() {
        const query = document.getElementById('location-input').value.trim();
        if (!query) return;
        try {
            const params = new URLSearchParams({ q: query, lang: currentLang });
            const response = await fetch(`/api/geocoding/search?${params}`);
            const data = await response.json();
            if (data.results && data.results.length > 0) {
                this.selectLocation(data.results[0]);
            }
        } catch (err) {
            console.error('Search error:', err);
        }
    },

    async showSuggestions(query) {
        try {
            const params = new URLSearchParams({ q: query, lang: currentLang });
            const response = await fetch(`/api/geocoding/search?${params}`);
            const data = await response.json();
            const container = document.getElementById('search-suggestions');
            if (data.results && data.results.length > 0) {
                container.innerHTML = data.results.map(place => `
                    <div class="suggestion-item" data-lat="${place.lat}" data-lon="${place.lon}" data-name="${place.name}" data-region="${place.region}">
                        <div class="suggestion-name">${place.name.split(',')[0]}</div>
                        <div class="suggestion-details">${place.country} ${place.region ? '- ' + place.region : ''}</div>
                    </div>
                `).join('');
                container.querySelectorAll('.suggestion-item').forEach(item => {
                    item.addEventListener('click', () => {
                        this.selectLocation({
                            lat: parseFloat(item.dataset.lat),
                            lon: parseFloat(item.dataset.lon),
                            name: item.dataset.name,
                            region_type: 'default'
                        });
                        this.hideSuggestions();
                    });
                });
                container.classList.remove('hidden');
            } else {
                this.hideSuggestions();
            }
        } catch (err) {
            this.hideSuggestions();
        }
    },

    hideSuggestions() {
        document.getElementById('search-suggestions').classList.add('hidden');
    },

    selectLocation(place) {
        this.selectedLocation = {
            lat: place.lat,
            lon: place.lon,
            name: place.name,
            region_type: place.region_type || 'default'
        };
        document.getElementById('location-input').value = place.name.split(',')[0];
        MapManager.setLocation(place.lat, place.lon);
        this.updateMapRadius();

        // Apply theme + background
        ThemeManager.detectAndApply(place.lat, place.lon, place.region_type, place.name);

        document.getElementById('explore-btn').disabled = false;
    },

    async onMapClick(lat, lon) {
        try {
            const params = new URLSearchParams({ lat, lon, lang: currentLang });
            const response = await fetch(`/api/geocoding/reverse?${params}`);
            const data = await response.json();
            if (!data.error) {
                this.selectLocation({
                    lat, lon,
                    name: data.name || `${lat.toFixed(4)}, ${lon.toFixed(4)}`,
                    region_type: data.region_type || 'default'
                });
            } else {
                this.selectLocation({ lat, lon, name: `${lat.toFixed(4)}, ${lon.toFixed(4)}`, region_type: 'default' });
            }
        } catch (err) {
            this.selectLocation({ lat, lon, name: `${lat.toFixed(4)}, ${lon.toFixed(4)}`, region_type: 'default' });
        }
    },

    updateMapRadius() {
        if (this.selectedLocation) {
            MapManager.setRadius(this.selectedLocation.lat, this.selectedLocation.lon, this.radiusKm);
        }
    },

    async convertTimeToRadius(timeStr) {
        const minutes = this.parseTimeString(timeStr);
        if (!minutes || !this.selectedLocation) return;
        const mode = document.getElementById('travel-mode').value;
        try {
            const params = new URLSearchParams({
                lat: this.selectedLocation.lat, lon: this.selectedLocation.lon,
                time_minutes: minutes, mode
            });
            const response = await fetch(`/api/geocoding/travel-radius?${params}`);
            const data = await response.json();
            if (data.radius_km) {
                this.radiusKm = data.radius_km;
                document.getElementById('radius-km').value = data.radius_km;
                this.updateMapRadius();
            }
        } catch (err) {
            const speeds = { car: 60, bike: 15, walk: 5 };
            this.radiusKm = Math.round((speeds[mode] * minutes / 60) * 0.7);
            document.getElementById('radius-km').value = this.radiusKm;
            this.updateMapRadius();
        }
    },

    parseTimeString(str) {
        let totalMinutes = 0;
        str = str.toLowerCase().trim();
        const hourMatch = str.match(/(\d+\.?\d*)\s*(h|hod|hodín|hodiny|hours?)/);
        if (hourMatch) totalMinutes += parseFloat(hourMatch[1]) * 60;
        const minMatch = str.match(/(\d+)\s*(m|min|minut|minút|minutes?)/);
        if (minMatch) totalMinutes += parseInt(minMatch[1]);
        if (!hourMatch && !minMatch) {
            const num = parseFloat(str);
            if (!isNaN(num)) totalMinutes = num;
        }
        return totalMinutes > 0 ? Math.round(totalMinutes) : null;
    },

    // === EXPLORE (main action) ===
    async explore() {
        if (!this.selectedLocation) return;
        const loading = document.getElementById('loading-overlay');
        loading.classList.remove('hidden');

        try {
            this.travelDate = document.getElementById('travel-date').value;

            // Get selected category tags
            const selectedTags = this.getSelectedTags();
            if (selectedTags.length === 0) {
                alert(currentLang === 'sk' ? 'Vyberte aspoň jednu kategóriu!' : 'Select at least one category!');
                loading.classList.add('hidden');
                return;
            }

            // Fetch weather
            this.weatherData = await WeatherModule.fetchAndDisplay(
                this.selectedLocation.lat, this.selectedLocation.lon,
                this.radiusKm, this.travelDate
            );

            // Fetch POIs with selected categories
            const params = new URLSearchParams({
                lat: this.selectedLocation.lat,
                lon: this.selectedLocation.lon,
                radius_km: this.radiusKm,
                lang: currentLang,
                date: this.travelDate,
                tags: selectedTags.join(',')
            });
            const response = await fetch(`/api/poi/search?${params}`);
            const data = await response.json();

            if (data.error) {
                alert(t('error_search'));
                return;
            }

            POIModule.renderResults(data, this.weatherData);

        } catch (err) {
            console.error('Explore error:', err);
            alert(t('error_search'));
        } finally {
            loading.classList.add('hidden');
        }
    }
};

window.App = App;
document.addEventListener('DOMContentLoaded', () => App.init());