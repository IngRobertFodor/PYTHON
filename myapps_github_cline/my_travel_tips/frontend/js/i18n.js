/**
 * Internationalization (i18n) - SK/EN translations
 */
const I18N = {
    sk: {
        search_title: 'Kam cestujete?',
        search_placeholder: 'Zadajte názov miesta...',
        search_btn: 'Hľadať',
        search_hint: 'alebo kliknite na mapu',
        radius_title: 'Okruh hľadania',
        radius_km_label: 'Vzdialenosť (km)',
        radius_time_label: 'Čas cestovania',
        or: 'alebo',
        mode_car: '🚗 Autom',
        mode_bike: '🚴 Bicyklom',
        mode_walk: '🚶 Pešo',
        date_title: 'Dátum cestovania',
        explore_btn: '🔍 Objaviť miesta',
        weather_title: '🌤️ Počasie v oblasti',
        mainstream_title: 'Mainstream – Top 10',
        mainstream_desc: 'Najpopulárnejšie a najnavštevovanejšie miesta v oblasti',
        alternative_title: 'Alternatívne & Zaujímavé – Top 10',
        alternative_desc: 'Skryté poklady, menej preskúmané a unikátne miesta',
        loading: 'Hľadám zaujímavé miesta...',
        footer_data: 'Dáta: OpenStreetMap, Wikipedia, Open-Meteo',
        distance_from_center: 'km od centra',
        outdoor: 'Outdoor',
        indoor: 'Indoor',
        best_weather: 'Najlepšie počasie',
        worst_weather: 'Horšie počasie',
        outdoor_friendly: 'Vhodné na outdoor',
        avg_temp: 'Priemerná teplota',
        precipitation: 'Zrážky max',
        no_results: 'Žiadne výsledky. Skúste väčší okruh.',
        error_search: 'Chyba pri hľadaní. Skúste znova.',
    },
    en: {
        search_title: 'Where are you traveling?',
        search_placeholder: 'Enter place name...',
        search_btn: 'Search',
        search_hint: 'or click on the map',
        radius_title: 'Search radius',
        radius_km_label: 'Distance (km)',
        radius_time_label: 'Travel time',
        or: 'or',
        mode_car: '🚗 By car',
        mode_bike: '🚴 By bike',
        mode_walk: '🚶 On foot',
        date_title: 'Travel date',
        explore_btn: '🔍 Discover places',
        weather_title: '🌤️ Area Weather',
        mainstream_title: 'Mainstream – Top 10',
        mainstream_desc: 'Most popular and most visited places in the area',
        alternative_title: 'Alternative & Interesting – Top 10',
        alternative_desc: 'Hidden gems, less explored and unique places',
        loading: 'Searching for interesting places...',
        footer_data: 'Data: OpenStreetMap, Wikipedia, Open-Meteo',
        distance_from_center: 'km from center',
        outdoor: 'Outdoor',
        indoor: 'Indoor',
        best_weather: 'Best weather',
        worst_weather: 'Worse weather',
        outdoor_friendly: 'Outdoor friendly',
        avg_temp: 'Average temperature',
        precipitation: 'Max precipitation',
        no_results: 'No results. Try a larger radius.',
        error_search: 'Search error. Please try again.',
    }
};

let currentLang = 'sk';

function setLanguage(lang) {
    currentLang = lang;
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (I18N[lang][key]) {
            el.textContent = I18N[lang][key];
        }
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (I18N[lang][key]) {
            el.placeholder = I18N[lang][key];
        }
    });
    document.documentElement.lang = lang;
}

function t(key) {
    return I18N[currentLang][key] || I18N['en'][key] || key;
}