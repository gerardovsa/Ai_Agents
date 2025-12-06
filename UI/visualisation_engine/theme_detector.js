/**
 * THEME DETECTOR UTILITY
 * ======================
 * 
 * Detects light/dark mode from UI and provides consistent theme colors
 * for all visualization renderers.
 * 
 * Works with:
 * - CSS media queries (prefers-color-scheme)
 * - Data attributes (data-theme on html/body)
 * - CSS variables (--theme-mode)
 * - Class names (.dark-mode, .light-mode)
 * 
 * Usage:
 *   const theme = ThemeDetector.getTheme();
 *   const colors = ThemeDetector.getColors();
 */

class ThemeDetector {
    /**
     * Detect current theme (light/dark)
     * @returns {string} 'dark' or 'light'
     */
    static getTheme() {
        // Method 1: Check data-theme attribute
        const htmlTheme = document.documentElement.getAttribute('data-theme');
        if (htmlTheme === 'dark' || htmlTheme === 'light') {
            return htmlTheme;
        }

        const bodyTheme = document.body.getAttribute('data-theme');
        if (bodyTheme === 'dark' || bodyTheme === 'light') {
            return bodyTheme;
        }

        // Method 2: Check CSS classes
        if (document.documentElement.classList.contains('dark') || 
            document.documentElement.classList.contains('dark-mode') ||
            document.body.classList.contains('dark') ||
            document.body.classList.contains('dark-mode')) {
            return 'dark';
        }

        if (document.documentElement.classList.contains('light') || 
            document.documentElement.classList.contains('light-mode') ||
            document.body.classList.contains('light') ||
            document.body.classList.contains('light-mode')) {
            return 'light';
        }

        // Method 3: Check CSS variable
        const themeVar = getComputedStyle(document.documentElement)
            .getPropertyValue('--theme-mode')
            .trim();
        if (themeVar === 'dark' || themeVar === 'light') {
            return themeVar;
        }

        // Method 4: Check media query
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }

        // Method 5: Check background color brightness
        const bgColor = getComputedStyle(document.body).backgroundColor;
        if (bgColor && bgColor !== 'rgba(0, 0, 0, 0)') {
            const brightness = this.getColorBrightness(bgColor);
            return brightness < 128 ? 'dark' : 'light';
        }

        // Default to light
        return 'light';
    }

    /**
     * Check if current theme is dark
     * @returns {boolean}
     */
    static isDark() {
        return this.getTheme() === 'dark';
    }

    /**
     * Check if current theme is light
     * @returns {boolean}
     */
    static isLight() {
        return this.getTheme() === 'light';
    }

    /**
     * Get theme-appropriate colors
     * @returns {Object} Color palette for current theme
     */
    static getColors() {
        const isDark = this.isDark();

        return {
            // Background colors
            background: isDark ? '#0d1117' : '#ffffff',
            backgroundSecondary: isDark ? '#161b22' : '#f6f8fa',
            backgroundTertiary: isDark ? '#21262d' : '#eaeef2',

            // Text colors
            text: isDark ? '#e6edf3' : '#24292f',
            textSecondary: isDark ? '#8b949e' : '#656d76',
            textTertiary: isDark ? '#6e7681' : '#8c959f',

            // Border colors
            border: isDark ? '#30363d' : '#d0d7de',
            borderSecondary: isDark ? '#21262d' : '#e1e4e8',

            // Grid/lines
            grid: isDark ? 'rgba(255,255,255,0.15)' : '#e1e4e8',
            gridLight: isDark ? 'rgba(255,255,255,0.08)' : '#f0f0f0',

            // Accent colors
            primary: isDark ? '#58a6ff' : '#0969da',
            success: isDark ? '#3fb950' : '#1a7f37',
            danger: isDark ? '#f85149' : '#cf222e',
            warning: isDark ? '#d29922' : '#9a6700',
            info: isDark ? '#79c0ff' : '#0969da',

            // Chart-specific colors
            chartColors: isDark 
                ? ['#58a6ff', '#3fb950', '#d29922', '#f85149', '#bc8cff', '#56d4dd', '#ffa657']
                : ['#0969da', '#1a7f37', '#9a6700', '#cf222e', '#8250df', '#0969da', '#bf4b00']
        };
    }

    /**
     * Calculate brightness of a color (0-255)
     * @param {string} color - CSS color string
     * @returns {number} Brightness value
     */
    static getColorBrightness(color) {
        // Parse RGB values
        let r, g, b;

        // Handle rgb/rgba
        const rgbMatch = color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
        if (rgbMatch) {
            [, r, g, b] = rgbMatch.map(Number);
        } 
        // Handle hex
        else if (color.startsWith('#')) {
            const hex = color.replace('#', '');
            if (hex.length === 3) {
                r = parseInt(hex[0] + hex[0], 16);
                g = parseInt(hex[1] + hex[1], 16);
                b = parseInt(hex[2] + hex[2], 16);
            } else {
                r = parseInt(hex.substr(0, 2), 16);
                g = parseInt(hex.substr(2, 2), 16);
                b = parseInt(hex.substr(4, 2), 16);
            }
        } else {
            return 255; // Assume light if can't parse
        }

        // Calculate perceived brightness (ITU-R BT.709)
        return (0.2126 * r + 0.7152 * g + 0.0722 * b);
    }

    /**
     * Watch for theme changes
     * @param {Function} callback - Called when theme changes
     * @returns {Function} Cleanup function to stop watching
     */
    static watchTheme(callback) {
        let currentTheme = this.getTheme();

        // Watch media query
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        const mediaHandler = () => {
            const newTheme = this.getTheme();
            if (newTheme !== currentTheme) {
                currentTheme = newTheme;
                callback(newTheme);
            }
        };

        if (mediaQuery.addEventListener) {
            mediaQuery.addEventListener('change', mediaHandler);
        } else {
            mediaQuery.addListener(mediaHandler); // Fallback for older browsers
        }

        // Watch DOM mutations for data-theme changes
        const observer = new MutationObserver(() => {
            const newTheme = this.getTheme();
            if (newTheme !== currentTheme) {
                currentTheme = newTheme;
                callback(newTheme);
            }
        });

        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-theme', 'class']
        });

        observer.observe(document.body, {
            attributes: true,
            attributeFilter: ['data-theme', 'class']
        });

        // Return cleanup function
        return () => {
            if (mediaQuery.removeEventListener) {
                mediaQuery.removeEventListener('change', mediaHandler);
            } else {
                mediaQuery.removeListener(mediaHandler);
            }
            observer.disconnect();
        };
    }

    /**
     * Apply theme to an element
     * @param {HTMLElement} element - Element to theme
     * @param {Object} options - Theme options
     */
    static applyTheme(element, options = {}) {
        const colors = this.getColors();
        const isDark = this.isDark();

        element.style.setProperty('--theme-mode', isDark ? 'dark' : 'light');
        element.style.setProperty('--theme-bg', colors.background);
        element.style.setProperty('--theme-text', colors.text);
        element.style.setProperty('--theme-border', colors.border);
        element.style.setProperty('--theme-grid', colors.grid);

        if (options.backgroundColor !== false) {
            element.style.backgroundColor = colors.background;
        }
        if (options.color !== false) {
            element.style.color = colors.text;
        }
        if (options.borderColor !== false) {
            element.style.borderColor = colors.border;
        }
    }

    /**
     * Get font family based on system
     * @returns {string} CSS font-family string
     */
    static getFontFamily() {
        return '"Roboto", -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", "Helvetica Neue", Arial, sans-serif';
    }
}

// Export for use in visualization renderers
if (typeof window !== 'undefined') {
    window.ThemeDetector = ThemeDetector;
    console.log('✅ ThemeDetector loaded - Current theme:', ThemeDetector.getTheme());
}
