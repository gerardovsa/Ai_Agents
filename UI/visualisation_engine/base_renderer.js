/**
 * BASE VISUALIZATION RENDERER
 * ===========================
 * 
 * Foundation class that all visualization renderers extend.
 * Provides shared functionality for security, memory management,
 * theme detection, and configuration handling.
 * 
 * Features:
 * - Config cloning (prevents mutation)
 * - DOM validation (prevents timing errors)
 * - Theme detection (consistent dark/light mode)
 * - HTML sanitization (XSS prevention)
 * - Instance tracking (memory leak prevention)
 * - JavaScript eval fallback (handles AI-generated configs)
 * - Universal cleanup (proper resource disposal)
 * 
 * Usage:
 * ```javascript
 * class ChartJSRenderer extends BaseVisualizationRenderer {
 *     async render(item, contentArea, chartId) {
 *         this.validateDOM(contentArea);
 *         const config = this.cloneConfig(
 *             this.parseConfig(item.content, /<\/?CHARTJS>/g)
 *         );
 *         // Renderer-specific logic...
 *         const chart = new Chart(canvas, config);
 *         this.instances.set(chartId, chart);
 *     }
 * }
 * ```
 * 
 * Created: December 2025
 * Purpose: Consolidate duplicate code, improve security, prevent memory leaks
 */

class BaseVisualizationRenderer {
    /**
     * Constructor
     * @param {Object} visualizationEngine - Reference to main visualization engine
     */
    constructor(visualizationEngine) {
        this.vizEngine = visualizationEngine;
        this.instances = new Map(); // Universal instance tracking
        this.animationFrames = new Map(); // Track animation frame IDs
        this.eventListeners = new Map(); // Track event listeners for cleanup
    }

    /**
     * Clone configuration to prevent mutation
     * Deep clones object to ensure AI-generated configs can be reused safely
     * 
     * @param {Object} config - Configuration object to clone
     * @returns {Object} Deep clone of config
     */
    cloneConfig(config) {
        try {
            return JSON.parse(JSON.stringify(config));
        } catch (error) {
            console.warn(`${this.constructor.name}: Failed to clone config, using original (risk of mutation)`);
            return config;
        }
    }

    /**
     * Validate DOM element exists and is attached
     * Prevents "element not in DOM" errors from async operations
     * 
     * @param {HTMLElement} contentArea - Element to validate
     * @param {string} context - Context for error message
     * @throws {Error} If element is null or not in DOM
     */
    validateDOM(contentArea, context = '') {
        if (!contentArea) {
            throw new Error(`${this.constructor.name}: Content area is null ${context}`);
        }
        if (!document.contains(contentArea)) {
            throw new Error(`${this.constructor.name}: Content area not in DOM ${context}`);
        }
        return true;
    }

    /**
     * Parse configuration with JavaScript eval fallback
     * Handles both JSON and JavaScript object notation from AI
     * 
     * @param {string|Object} content - Content to parse
     * @param {RegExp} delimiters - Regex to remove delimiters (e.g., /<\/?CHARTJS>/g)
     * @returns {Object} Parsed configuration
     * @throws {Error} If both JSON and eval parsing fail
     */
    parseConfig(content, delimiters = null) {
        // If already an object, return as-is
        if (typeof content === 'object' && content !== null) {
            return content;
        }

        // Must be a string
        if (typeof content !== 'string') {
            throw new Error(`${this.constructor.name}: Invalid content type (expected string or object)`);
        }

        // Remove delimiters if provided
        const cleanContent = delimiters ? content.replace(delimiters, '').trim() : content.trim();

        // Try JSON first (standard format)
        try {
            return JSON.parse(cleanContent);
        } catch (jsonError) {
            // Fallback to JavaScript eval (for object literals with functions)
            console.log(`${this.constructor.name}: JSON parse failed, using JavaScript eval`);
            try {
                // Use Function constructor (safer than eval)
                const config = (new Function('return ' + cleanContent))();
                console.log(`✅ ${this.constructor.name}: JavaScript eval successful`);
                return config;
            } catch (evalError) {
                throw new Error(
                    `${this.constructor.name}: Parse failed. JSON: ${jsonError.message}, Eval: ${evalError.message}`
                );
            }
        }
    }

    /**
     * Sanitize HTML content to prevent XSS attacks
     * Uses DOMPurify if available, otherwise basic tag stripping
     * 
     * @param {string} html - HTML to sanitize
     * @param {Object} options - Sanitization options
     * @param {Array} options.allowedTags - Tags to allow
     * @param {Array} options.forbiddenTags - Tags to forbid
     * @returns {string} Sanitized HTML
     */
    sanitizeHTML(html, options = {}) {
        // Check if DOMPurify is loaded
        if (typeof DOMPurify !== 'undefined' && DOMPurify.sanitize) {
            const config = {
                ALLOWED_TAGS: options.allowedTags || [
                    'div', 'span', 'p', 'b', 'i', 'strong', 'em', 'br',
                    'svg', 'path', 'rect', 'circle', 'line', 'polygon', 'text', 'g'
                ],
                FORBID_TAGS: options.forbiddenTags || ['script', 'iframe', 'object', 'embed', 'link'],
                ALLOW_DATA_ATTR: false,
                ALLOW_UNKNOWN_PROTOCOLS: false
            };

            return DOMPurify.sanitize(html, config);
        }

        // Fallback: Basic script tag removal (less secure)
        console.warn(`${this.constructor.name}: DOMPurify not loaded - using basic sanitization (XSS risk!)`);
        return html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
            .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '');
    }

    /**
     * Get current theme information
     * Provides consistent theme detection across all renderers
     * 
     * @returns {Object} Theme information { isDark: boolean, colors: Object }
     */
    getTheme() {
        // Try ThemeDetector if available
        if (typeof window !== 'undefined' && window.ThemeDetector) {
            return {
                isDark: window.ThemeDetector.isDark(),
                colors: window.ThemeDetector.getColors()
            };
        }

        // Fallback to visualization engine options
        if (this.vizEngine && this.vizEngine.options) {
            const isDark = this.vizEngine.options.theme === 'dark';
            return {
                isDark,
                colors: this.getDefaultColors(isDark)
            };
        }

        // Default to light mode
        return {
            isDark: false,
            colors: this.getDefaultColors(false)
        };
    }

    /**
     * Get default theme colors when ThemeDetector not available
     * 
     * @param {boolean} isDark - Whether dark mode is active
     * @returns {Object} Color palette
     */
    getDefaultColors(isDark) {
        if (isDark) {
            return {
                background: '#0d1117',
                backgroundSecondary: '#161b22',
                text: '#e6edf3',
                textSecondary: '#8b949e',
                border: '#30363d',
                accent: '#677eea'
            };
        } else {
            return {
                background: '#ffffff',
                backgroundSecondary: '#f5f5f5',
                text: '#24292f',
                textSecondary: '#57606a',
                border: '#d0d7de',
                accent: '#677eea'
            };
        }
    }

    /**
     * Track animation frame for cleanup
     * Prevents memory leaks from infinite animation loops
     * 
     * @param {string} chartId - Unique chart identifier
     * @param {number} frameId - requestAnimationFrame ID
     */
    trackAnimationFrame(chartId, frameId) {
        this.animationFrames.set(chartId, frameId);
    }

    /**
     * Cancel tracked animation frame
     * 
     * @param {string} chartId - Unique chart identifier
     */
    cancelAnimationFrame(chartId) {
        const frameId = this.animationFrames.get(chartId);
        if (frameId) {
            cancelAnimationFrame(frameId);
            this.animationFrames.delete(chartId);
        }
    }

    /**
     * Track event listener for cleanup
     * 
     * @param {string} chartId - Unique chart identifier
     * @param {HTMLElement} element - Element with listener
     * @param {string} event - Event name
     * @param {Function} handler - Event handler
     */
    trackEventListener(chartId, element, event, handler) {
        if (!this.eventListeners.has(chartId)) {
            this.eventListeners.set(chartId, []);
        }
        this.eventListeners.get(chartId).push({ element, event, handler });
    }

    /**
     * Remove tracked event listeners
     * 
     * @param {string} chartId - Unique chart identifier
     */
    removeEventListeners(chartId) {
        const listeners = this.eventListeners.get(chartId);
        if (listeners) {
            listeners.forEach(({ element, event, handler }) => {
                element.removeEventListener(event, handler);
            });
            this.eventListeners.delete(chartId);
        }
    }

    /**
     * Validate configuration has required fields
     * Prevents cryptic errors from libraries
     * 
     * @param {Object} config - Configuration to validate
     * @param {Array} requiredFields - Array of required field paths (e.g., ['data', 'options.responsive'])
     * @throws {Error} If required field is missing
     */
    validateConfig(config, requiredFields) {
        for (const field of requiredFields) {
            const parts = field.split('.');
            let value = config;

            for (const part of parts) {
                if (value === undefined || value === null || !(part in value)) {
                    throw new Error(
                        `${this.constructor.name}: Missing required field '${field}' in configuration`
                    );
                }
                value = value[part];
            }
        }
    }

    /**
     * Universal cleanup method
     * Destroys chart instance and cleans up resources
     * 
     * @param {string} chartId - Unique chart identifier
     */
    destroy(chartId) {
        const instance = this.instances.get(chartId);

        if (instance) {
            // Try different cleanup methods (different libraries use different names)
            if (typeof instance.destroy === 'function') {
                instance.destroy(); // Chart.js, ApexCharts
            } else if (typeof instance.kill === 'function') {
                instance.kill(); // GSAP timelines
            } else if (typeof instance.dispose === 'function') {
                instance.dispose(); // Three.js
            }

            this.instances.delete(chartId);
        }

        // Cancel animation frames
        this.cancelAnimationFrame(chartId);

        // Remove event listeners
        this.removeEventListeners(chartId);
    }

    /**
     * Destroy all instances managed by this renderer
     * Called when renderer is being unloaded
     */
    destroyAll() {
        // Destroy all tracked instances
        this.instances.forEach((instance, chartId) => {
            this.destroy(chartId);
        });
        this.instances.clear();

        // Cancel all animation frames
        this.animationFrames.forEach((frameId, chartId) => {
            this.cancelAnimationFrame(chartId);
        });
        this.animationFrames.clear();

        // Remove all event listeners
        this.eventListeners.forEach((listeners, chartId) => {
            this.removeEventListeners(chartId);
        });
        this.eventListeners.clear();
    }

    /**
     * Handle errors with consistent messaging
     * 
     * @param {Error} error - Error object
     * @param {string} context - Context where error occurred
     * @param {HTMLElement} contentArea - Element to show error in (optional)
     */
    handleError(error, context, contentArea = null) {
        const errorMessage = `${this.constructor.name} error in ${context}: ${error.message}`;
        console.error(errorMessage, error);

        // Show user-friendly error if contentArea provided
        if (contentArea && document.contains(contentArea)) {
            const theme = this.getTheme();
            contentArea.innerHTML = `
                <div style="
                    padding: 20px;
                    text-align: center;
                    color: ${theme.isDark ? '#f85149' : '#cf222e'};
                    background: ${theme.isDark ? 'rgba(248, 81, 73, 0.1)' : 'rgba(207, 34, 46, 0.1)'};
                    border: 1px solid ${theme.isDark ? '#f85149' : '#cf222e'};
                    border-radius: 6px;
                ">
                    <h4 style="margin: 0 0 10px 0;">⚠️ Visualization Error</h4>
                    <p style="margin: 0; font-size: 14px;">${error.message}</p>
                </div>
            `;
        }

        return errorMessage;
    }

    /**
     * Wait for DOM element to be ready
     * Useful for animations that need DOM to settle
     * 
     * @returns {Promise} Resolves after next animation frame
     */
    async waitForDOM() {
        return new Promise(resolve => requestAnimationFrame(resolve));
    }

    /**
     * Load external library dynamically
     * 
     * @param {string} url - CDN URL of library
     * @param {string} globalName - Global variable name to check (e.g., 'Chart')
     * @param {number} timeout - Timeout in milliseconds (default 10000)
     * @returns {Promise} Resolves when library loaded
     */
    async loadLibrary(url, globalName, timeout = 10000) {
        // Check if already loaded
        if (typeof window[globalName] !== 'undefined') {
            return Promise.resolve();
        }

        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = url;

            script.onload = () => {
                console.log(`✅ ${this.constructor.name}: ${globalName} library loaded`);
                resolve();
            };

            script.onerror = () => {
                document.head.removeChild(script);
                reject(new Error(`Failed to load ${globalName} library from ${url}`));
            };

            document.head.appendChild(script);

            // Timeout fallback
            setTimeout(() => {
                if (typeof window[globalName] === 'undefined') {
                    document.head.removeChild(script);
                    reject(new Error(`${globalName} library failed to load within ${timeout}ms`));
                }
            }, timeout);
        });
    }
}

// Export for use in visualization engine
if (typeof window !== 'undefined') {
    window.BaseVisualizationRenderer = BaseVisualizationRenderer;
}

// Also support module exports for Node.js environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BaseVisualizationRenderer;
}
