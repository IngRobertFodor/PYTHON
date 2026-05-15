/**
 * Weather Module - Displays weather data and grid visualization
 */
const WeatherModule = {
    async fetchAndDisplay(lat, lon, radiusKm, date) {
        const section = document.getElementById('weather-section');
        
        try {
            // Fetch weather grid
            const params = new URLSearchParams({
                lat, lon, radius_km: radiusKm, date: date || ''
            });
            const response = await fetch(`/api/weather/grid?${params}`);
            const data = await response.json();

            if (data.error) {
                section.classList.add('hidden');
                return null;
            }

            // Display weather
            this.renderWeatherCenter(data);
            this.renderWeatherGrid(data.grid_points);
            this.renderWeatherSummary(data.summary);
            
            // Add weather markers to map
            MapManager.addWeatherGrid(data.grid_points);

            section.classList.remove('hidden');
            return data;

        } catch (err) {
            console.error('Weather fetch error:', err);
            section.classList.add('hidden');
            return null;
        }
    },

    renderWeatherCenter(data) {
        const container = document.getElementById('weather-center');
        const centerPoint = data.grid_points.find(p => p.grid_position === 'C') || data.grid_points[4] || data.grid_points[0];
        
        if (!centerPoint) {
            container.innerHTML = '';
            return;
        }

        const langKey = currentLang === 'sk' ? 'weather_description_sk' : 'weather_description_en';
        const recKey = currentLang === 'sk' ? 'outdoor_recommendation_sk' : 'outdoor_recommendation_en';

        container.innerHTML = `
            <div class="weather-center-icon">${centerPoint.weather_icon}</div>
            <div class="weather-center-info">
                <h3>${centerPoint[langKey]}</h3>
                <p>${centerPoint[recKey]}</p>
                <p>💨 ${centerPoint.wind_speed_max} km/h | 💧 ${centerPoint.precipitation_mm} mm | ☀️ UV ${centerPoint.uv_index}</p>
            </div>
            <div class="weather-center-temp">${centerPoint.temperature_max}°C</div>
        `;
    },

    renderWeatherGrid(gridPoints) {
        const container = document.getElementById('weather-grid');
        
        if (!gridPoints || gridPoints.length === 0) {
            container.innerHTML = '';
            return;
        }

        const positionLabels = {
            'NW': currentLang === 'sk' ? 'SZ' : 'NW',
            'N': currentLang === 'sk' ? 'S' : 'N',
            'NE': currentLang === 'sk' ? 'SV' : 'NE',
            'W': currentLang === 'sk' ? 'Z' : 'W',
            'C': currentLang === 'sk' ? 'Centrum' : 'Center',
            'E': currentLang === 'sk' ? 'V' : 'E',
            'SW': currentLang === 'sk' ? 'JZ' : 'SW',
            'S': currentLang === 'sk' ? 'J' : 'S',
            'SE': currentLang === 'sk' ? 'JV' : 'SE'
        };

        container.innerHTML = gridPoints.map(point => `
            <div class="weather-grid-item">
                <div class="weather-grid-icon">${point.weather_icon}</div>
                <div class="weather-grid-temp">${point.temperature_max}°/${point.temperature_min}°</div>
                <div class="weather-grid-position">${positionLabels[point.grid_position] || point.grid_position}</div>
            </div>
        `).join('');
    },

    renderWeatherSummary(summary) {
        const container = document.getElementById('weather-summary');
        
        if (!summary || summary.message_sk) {
            container.innerHTML = '';
            return;
        }

        const isRainy = summary.max_precipitation_mm > 5;
        container.className = `weather-summary ${isRainy ? 'rainy' : ''}`;

        container.innerHTML = `
            <div class="weather-summary-item">
                <strong>${t('avg_temp')}:</strong> ${summary.avg_temp_max}°C
            </div>
            <div class="weather-summary-item">
                <strong>${t('precipitation')}:</strong> ${summary.max_precipitation_mm} mm
            </div>
            <div class="weather-summary-item">
                <strong>${t('outdoor_friendly')}:</strong> ${summary.outdoor_friendly_ratio}
            </div>
            <div class="weather-summary-item">
                ${summary.best_weather_icon} <strong>${t('best_weather')}:</strong> ${summary.best_weather_area}
            </div>
            <div class="weather-summary-item">
                ${summary.worst_weather_icon} <strong>${t('worst_weather')}:</strong> ${summary.worst_weather_area}
            </div>
        `;
    }
};