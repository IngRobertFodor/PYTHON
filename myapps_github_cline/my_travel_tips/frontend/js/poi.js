/**
 * POI Module - Renders POI cards with links
 */
const POIModule = {
    renderResults(data, weatherData) {
        const section = document.getElementById('results-section');
        const mainstreamContainer = document.getElementById('mainstream-results');
        const alternativeContainer = document.getElementById('alternative-results');

        if (!data.mainstream.length && !data.alternative.length) {
            section.classList.add('hidden');
            mainstreamContainer.innerHTML = `<p class="no-results">${t('no_results')}</p>`;
            alternativeContainer.innerHTML = '';
            section.classList.remove('hidden');
            return;
        }

        // Render mainstream POIs
        mainstreamContainer.innerHTML = data.mainstream.map((poi, i) => 
            this.renderCard(poi, i + 1, 'mainstream', weatherData)
        ).join('');

        // Render alternative POIs
        alternativeContainer.innerHTML = data.alternative.map((poi, i) => 
            this.renderCard(poi, i + 1, 'alternative', weatherData)
        ).join('');

        // Add POI markers to map
        MapManager.clearPOIMarkers();
        MapManager.addPOIMarkers(data.mainstream, 'mainstream');
        MapManager.addPOIMarkers(data.alternative, 'alternative');

        section.classList.remove('hidden');

        // Scroll to results
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    },

    renderCard(poi, number, category, weatherData) {
        const name = currentLang === 'sk' && poi.name_sk ? poi.name_sk : poi.name;
        const description = poi.description || '';
        const isOutdoor = poi.is_outdoor;
        
        // Weather warning for outdoor POIs
        let weatherBadge = '';
        if (isOutdoor && weatherData) {
            const centerWeather = weatherData.grid_points ? 
                weatherData.grid_points.find(p => p.grid_position === 'C') : null;
            if (centerWeather && !centerWeather.is_outdoor_friendly) {
                weatherBadge = `<span class="poi-card-badge weather-warn">⚠️ ${currentLang === 'sk' ? 'Dážď' : 'Rain'}</span>`;
            }
        }

        // Type badge (localized)
        const typeLabels = currentLang === 'sk' ? {
            nature: '🌿 Príroda',
            historic: '🏛️ História',
            cultural: '🎭 Kultúra',
            religious: '⛪ Sakrálne',
            geology: '🪨 Geológia',
            hiking: '🥾 Turistika',
            cycling: '🚴 Cyklo',
            peak: '⛰️ Vrchol',
            viewpoint: '👁️ Vyhliadka',
            waterfall: '🌊 Vodopád',
            volcano: '🌋 Sopka',
            beach: '🏖️ Pláž',
            archaeology: '⛏️ Archeológia',
            national_park: '🌲 Nár. park',
            hut: '🏕️ Chata',
        } : {
            nature: '🌿 Nature',
            historic: '🏛️ Historic',
            cultural: '🎭 Cultural',
            religious: '⛪ Religious',
            geology: '🪨 Geology',
            hiking: '🥾 Hiking',
            cycling: '🚴 Cycling',
            peak: '⛰️ Peak',
            viewpoint: '👁️ Viewpoint',
            waterfall: '🌊 Waterfall',
            volcano: '🌋 Volcano',
            beach: '🏖️ Beach',
            archaeology: '⛏️ Archaeology',
            national_park: '🌲 National Park',
            hut: '🏕️ Mountain Hut',
        };
        const typeBadge = typeLabels[poi.type] || '📍 POI';

        // Links
        const linksHtml = (poi.links || []).map(link => `
            <a href="${link.url}" target="_blank" rel="noopener noreferrer" class="poi-link">
                <span class="poi-link-icon">${link.icon}</span>
                ${link.label}
            </a>
        `).join('');

        return `
            <div class="poi-card ${category}">
                <div class="poi-card-header">
                    <div class="poi-card-number">${number}</div>
                    <div class="poi-card-meta">
                        <span class="poi-card-badge">${typeBadge}</span>
                        ${isOutdoor ? `<span class="poi-card-badge outdoor">${t('outdoor')}</span>` : ''}
                        ${weatherBadge}
                    </div>
                </div>
                <div class="poi-card-body">
                    <h3 class="poi-card-name">${name}</h3>
                    ${description ? `<p class="poi-card-description">${description}</p>` : ''}
                    <p class="poi-card-distance">📍 ${poi.distance_km} ${t('distance_from_center')}</p>
                </div>
                <div class="poi-card-links">
                    ${linksHtml}
                </div>
            </div>
        `;
    }
};