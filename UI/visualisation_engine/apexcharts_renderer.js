/**
 * APEXCHARTS RENDERER MODULE
 * ===========================
 * 
 * Renders ApexCharts visualizations with dark theme support.
 * ApexCharts is a modern charting library with interactive charts.
 * 
 * Supported chart types:
 * - area, line, bar, column, pie, donut, radialBar, scatter
 * - heatmap, treemap, candlestick, radar, polarArea
 * 
 * CDN: https://cdn.jsdelivr.net/npm/apexcharts
 * Docs: https://apexcharts.com/
 */

class ApexChartsRenderer {
    constructor(visualizationEngine) {
        this.vizEngine = visualizationEngine;
        this.charts = new Map(); // Track chart instances for cleanup
    }

    /**
     * Render ApexCharts visualization
     * @param {Object} item - Visualization item with content
     * @param {HTMLElement} contentArea - Target container
     * @param {string} chartId - Unique chart identifier
     */
    async render(item, contentArea, chartId) {
        // Ensure ApexCharts library is loaded
        if (!window.ApexCharts) {
            await this.loadLibrary();
        }

        // DOM validation
        if (!contentArea || !document.contains(contentArea)) {
            throw new Error('ApexCharts: Invalid content area');
        }

        // Parse configuration - handle both JSON and JS object notation
        let config;
        if (typeof item.content === 'string') {
            const cleanContent = item.content.replace(/<\/?APEXCHARTS>/g, '').trim();
            try {
                // Try standard JSON parse first
                config = JSON.parse(cleanContent);
            } catch (e) {
                // If JSON fails, try eval for JS object notation (with functions)
                console.log('ℹ️ ApexCharts: Using JavaScript eval for object literal syntax');
                try {
                    // Use Function constructor for safer eval
                    config = (new Function('return ' + cleanContent))();
                    console.log('✅ ApexCharts: Config parsed successfully');
                } catch (evalError) {
                    console.error('❌ ApexCharts: Config parsing failed:', evalError.message);
                    console.error('📄 Config preview:', cleanContent.substring(0, 200));
                    throw new Error(`Invalid ApexCharts config: ${evalError.message}`);
                }
            }
        } else {
            config = item.content;
        }

        // Convert string functions to real functions (CRITICAL FIX)
        this.convertStringFunctionsToReal(config);

        // Apply theme with dynamic detection
        const isDark = window.ThemeDetector ? window.ThemeDetector.isDark() :
            (this.vizEngine?.options?.theme === 'dark');
        this.applyTheme(config, isDark);

        // Create container
        const chartContainer = document.createElement('div');
        chartContainer.id = chartId;
        chartContainer.style.cssText = `
            width: 100%;
            min-height: ${config.chart?.height || 400}px;
            position: relative;
        `;

        contentArea.appendChild(chartContainer);

        // Render chart
        const chart = new ApexCharts(chartContainer, config);
        await chart.render();

        // Store instance for cleanup
        this.charts.set(chartId, chart);

        // Add action bar
        const vizContainer = contentArea.closest('.viz-container');
        if (vizContainer && this.vizEngine?.addUnifiedActionBar) {
            this.vizEngine.addUnifiedActionBar(vizContainer, item, chartId, 'apexcharts');
        }

        return chart;
    }

    /**
     * Convert string functions to real JavaScript functions
     * Recursively walks the config object and converts strings like 
     * "function(val) { return val; }" into actual executable functions.
     * 
     * @param {Object} obj - Config object to process (mutated in place)
     */
    convertStringFunctionsToReal(obj) {
        if (!obj || typeof obj !== 'object') return;

        for (const key in obj) {
            const value = obj[key];

            // Check if value is a string that looks like a function
            if (typeof value === 'string' && 
                value.trim().startsWith('function') && 
                value.includes('(') && 
                value.includes(')')) {
                try {
                    // Convert string to actual function
                    obj[key] = new Function('return ' + value)();
                    console.log(`✅ ApexCharts: Converted formatter "${key}" from string to function`);
                } catch (e) {
                    console.warn(`⚠️ ApexCharts: Failed to convert formatter "${key}":`, e.message);
                }
            }
            // Recursively process nested objects/arrays
            else if (typeof value === 'object' && value !== null) {
                this.convertStringFunctionsToReal(value);
            }
        }
    }

    /**
     * Apply theme styling to chart config
     */
    applyTheme(config, isDark) {
        // Get dynamic theme colors
        const colors = window.ThemeDetector ? window.ThemeDetector.getColors() : null;

        if (!colors) {
            console.warn('ThemeDetector not available, using defaults');
            return;
        }

        // Theme defaults for both modes
        const themeConfig = {
            mode: isDark ? 'dark' : 'light',
            palette: 'palette1',
            monochrome: {
                enabled: false
            }
        };

        const chartConfig = {
            background: colors.background,
            foreColor: colors.text
        };

        const gridConfig = {
            borderColor: colors.border
        };

        const tooltipConfig = {
            theme: isDark ? 'dark' : 'light',
            style: {
                background: colors.backgroundSecondary,
                color: colors.text
            }
        };

        // Apply theme settings
        config.theme = { ...themeConfig, ...(config.theme || {}) };
        config.chart = { ...chartConfig, ...(config.chart || {}) };
        config.grid = { ...gridConfig, ...(config.grid || {}) };
        config.tooltip = { ...tooltipConfig, ...(config.tooltip || {}) };

        // Title styling
        if (config.title) {
            config.title.style = {
                color: colors.text,
                ...(config.title.style || {})
            };
        }

        // Legend styling
        if (config.legend) {
            config.legend.labels = {
                colors: colors.text,
                ...(config.legend.labels || {})
            };
        }

        // Axis styling
        if (config.xaxis) {
            config.xaxis.labels = {
                style: { colors: colors.textSecondary },
                ...(config.xaxis.labels || {})
            };
        }
        if (config.yaxis) {
            config.yaxis.labels = {
                style: { colors: colors.textSecondary },
                ...(config.yaxis.labels || {})
            };
        }
    }

    /**
     * Load ApexCharts library dynamically
     */
    async loadLibrary() {
        return new Promise((resolve, reject) => {
            if (window.ApexCharts) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/apexcharts@3.45.1/dist/apexcharts.min.js';
            script.onload = () => {
                console.log('✅ ApexCharts library loaded');
                resolve();
            };
            script.onerror = () => reject(new Error('Failed to load ApexCharts library'));
            document.head.appendChild(script);
        });
    }

    /**
     * Destroy chart instance and cleanup
     */
    destroy(chartId) {
        const chart = this.charts.get(chartId);
        if (chart) {
            chart.destroy();
            this.charts.delete(chartId);
        }
    }

    /**
     * Destroy all chart instances
     */
    destroyAll() {
        this.charts.forEach((chart, chartId) => {
            chart.destroy();
        });
        this.charts.clear();
    }
}

// Export for use in visualization engine
if (typeof window !== 'undefined') {
    window.ApexChartsRenderer = ApexChartsRenderer;
}
