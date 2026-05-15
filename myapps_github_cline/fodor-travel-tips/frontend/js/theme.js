/**
 * Theme Manager - Dynamic color themes and background images
 * Background changes based on destination type using Unsplash
 */
const ThemeManager = {
    currentTheme: 'default',

    // Unsplash background keywords by region type
    backgrounds: {
        mountain: 'mountain,alps,hiking,peaks',
        coastal: 'ocean,beach,coast,mediterranean',
        urban: 'city,architecture,europe,urban',
        rural: 'countryside,village,fields,nature',
        default: 'travel,adventure,landscape,europe'
    },

    applyTheme(themeName) {
        document.body.classList.remove(
            'theme-mountain', 'theme-coastal', 'theme-urban',
            'theme-rural', 'theme-default'
        );
        const validThemes = ['mountain', 'coastal', 'urban', 'rural', 'default'];
        const theme = validThemes.includes(themeName) ? themeName : 'default';
        document.body.classList.add(`theme-${theme}`);
        this.currentTheme = theme;
    },

    changeBackground(regionType, placeName) {
        const heroBg = document.getElementById('hero-bg');
        if (!heroBg) return;

        // Build Unsplash URL with destination keywords
        let keywords = this.backgrounds[regionType] || this.backgrounds.default;
        
        // Add place name for more relevant photos
        if (placeName) {
            const cleanName = placeName.split(',')[0].trim();
            keywords = `${cleanName},${keywords}`;
        }

        // Use Unsplash source (random photo by keyword)
        const url = `https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1920&q=80`;
        
        // Try Unsplash source API for keyword-based images
        const unsplashUrl = `https://source.unsplash.com/1920x1080/?${encodeURIComponent(keywords)}`;
        
        // Preload image then apply
        const img = new Image();
        img.onload = () => {
            heroBg.style.backgroundImage = `url('${unsplashUrl}')`;
        };
        img.onerror = () => {
            // Fallback - keep current or use default
            console.log('Background image load failed, keeping current');
        };
        img.src = unsplashUrl;
    },

    async detectAndApply(lat, lon, regionType, placeName) {
        // Apply color theme
        if (regionType && regionType !== 'default') {
            this.applyTheme(regionType);
        } else {
            this.applyTheme('default');
        }
        // Change background
        this.changeBackground(regionType || 'default', placeName);
    }
};