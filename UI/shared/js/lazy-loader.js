/**
 * LazyLoader - Dynamic Module Loading System
 * 
 * Purpose: Load JavaScript modules and CSS files on-demand
 * Use Cases:
 * - Load feature modules when user clicks a tab
 * - Defer heavy libraries until after login
 * - Pre-fetch commonly used modules in background
 * 
 * Features:
 * - Dependency resolution (load prerequisites first)
 * - Parallel loading (load independent modules simultaneously)
 * - Caching (don't reload already-loaded modules)
 * - Progress tracking (show loading indicators)
 * - Error handling (fallback to legacy loading)
 * 
 * @version 1.0.0
 * @date December 6, 2025
 */

window.LazyLoader = (function () {
    'use strict';

    // Track loaded modules (prevent duplicate loads)
    const loadedModules = new Set();
    const loadingPromises = new Map();

    // Track loading progress
    let totalModules = 0;
    let loadedCount = 0;
    let progressCallback = null;

    /**
     * Enable all disabled data-post-auth resources
     * This activates stylesheets and scripts that were pre-loaded but disabled
     * @returns {number} Number of resources enabled
     */
    function enablePostAuthResources() {
        console.log('🔓 [LazyLoader] Enabling disabled data-post-auth resources...');

        // Find all disabled links and scripts with data-post-auth attribute
        const disabledLinks = document.querySelectorAll('link[data-post-auth][disabled]');
        const disabledScripts = document.querySelectorAll('script[data-post-auth][disabled]');

        let enabledCount = 0;

        // Enable stylesheets
        disabledLinks.forEach(link => {
            console.log(`  🔓 Enabling CSS: ${link.href}`);
            link.disabled = false;
            loadedModules.add(link.href); // Mark as loaded
            enabledCount++;
        });

        // Enable scripts (though scripts shouldn't typically be disabled)
        disabledScripts.forEach(script => {
            console.log(`  🔓 Enabling script: ${script.src}`);
            script.disabled = false;
            loadedModules.add(script.src); // Mark as loaded
            enabledCount++;
        });

        if (enabledCount > 0) {
            console.log(`✅ [LazyLoader] Enabled ${enabledCount} post-auth resources`);
        } else {
            console.log(`ℹ️ [LazyLoader] No disabled post-auth resources found`);
        }

        return enabledCount;
    }

    /**
     * Load a single JavaScript file dynamically
     * @param {string} src - URL of the script to load
     * @param {object} options - Loading options
     * @returns {Promise<void>}
     */
    async function loadScript(src, options = {}) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.async = options.async !== false; // Default: async
            script.defer = options.defer || false;

            // Add attributes
            if (options.type) script.type = options.type;
            if (options.crossOrigin) script.crossOrigin = options.crossOrigin;
            if (options.integrity) script.integrity = options.integrity;

            script.onload = () => {
                console.log(`✅ Loaded: ${src}`);
                resolve();
            };

            script.onerror = (error) => {
                console.error(`❌ Failed to load: ${src}`, error);
                reject(new Error(`Failed to load script: ${src}`));
            };

            document.head.appendChild(script);
        });
    }

    /**
     * Load a single CSS file dynamically
     * @param {string} href - URL of the stylesheet to load
     * @param {object} options - Loading options
     * @returns {Promise<void>}
     */
    async function loadCSS(href, options = {}) {
        return new Promise((resolve, reject) => {
            // Check if already loaded
            const existing = document.querySelector(`link[href="${href}"]`);
            if (existing) {
                console.log(`⚡ Already loaded: ${href}`);
                resolve();
                return;
            }

            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = href;

            if (options.media) link.media = options.media;
            if (options.crossOrigin) link.crossOrigin = options.crossOrigin;
            if (options.integrity) link.integrity = options.integrity;

            link.onload = () => {
                console.log(`✅ Loaded CSS: ${href}`);
                resolve();
            };

            link.onerror = (error) => {
                console.error(`❌ Failed to load CSS: ${href}`, error);
                reject(new Error(`Failed to load CSS: ${href}`));
            };

            document.head.appendChild(link);
        });
    }

    /**
     * Load a module (script or CSS) with caching
     * @param {string} url - URL of the module
     * @param {object} options - Loading options
     * @returns {Promise<void>}
     */
    async function loadModule(url, options = {}) {
        // Check if already loaded
        if (loadedModules.has(url)) {
            console.log(`⚡ Module already loaded: ${url}`);
            return Promise.resolve();
        }

        // Check if currently loading (avoid duplicate requests)
        if (loadingPromises.has(url)) {
            console.log(`⏳ Module already loading: ${url}`);
            return loadingPromises.get(url);
        }

        // Determine if CSS or JavaScript
        const isCSS = url.endsWith('.css');
        const loadPromise = isCSS ? loadCSS(url, options) : loadScript(url, options);

        // Store loading promise
        loadingPromises.set(url, loadPromise);

        try {
            await loadPromise;
            loadedModules.add(url);
            loadingPromises.delete(url);

            // Update progress
            loadedCount++;
            if (progressCallback) {
                progressCallback(loadedCount, totalModules);
            }
        } catch (error) {
            loadingPromises.delete(url);
            throw error;
        }
    }

    /**
     * Load multiple modules with dependency resolution
     * @param {object} manifest - Module manifest with dependencies
     * @returns {Promise<void>}
     */
    async function loadManifest(manifest) {
        console.log(`📦 Loading manifest: ${manifest.name}`);
        console.log(`📊 Modules to load: ${manifest.modules.length}`);

        totalModules = manifest.modules.length;
        loadedCount = 0;

        try {
            // Phase 1: Load dependencies first (sequential if needed)
            if (manifest.dependencies && manifest.dependencies.length > 0) {
                console.log(`🔗 Loading ${manifest.dependencies.length} dependencies first...`);
                for (const dep of manifest.dependencies) {
                    await loadModule(dep);
                }
            }

            // Phase 2: Load main modules in parallel
            console.log(`⚡ Loading ${manifest.modules.length} modules in parallel...`);
            await Promise.all(
                manifest.modules.map(module => loadModule(module.url, module.options || {}))
            );

            console.log(`✅ Manifest loaded: ${manifest.name}`);
        } catch (error) {
            console.error(`❌ Failed to load manifest: ${manifest.name}`, error);
            throw error;
        }
    }

    /**
     * Load essential post-authentication modules
     * @returns {Promise<void>}
     */
    async function loadPostAuthEssentials() {
        console.log('🚀 Loading post-authentication essentials...');

        const essentialModules = [
            // Core libraries
            'https://cdn.jsdelivr.net/npm/marked@9.1.0/marked.min.js',
            'https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js',
            'https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-tomorrow.min.css',

            // Internal modules
            'modules_internal/core/thread-manager-core.js',
            'modules_internal/core/thread-manager-ui.js',
            'modules_internal/core/message-renderer.js',
            'modules_internal/components/agent-js.js',
            'shared/js/supabase-connection-manager.js'
        ];

        try {
            await Promise.all(essentialModules.map(url => loadModule(url)));
            console.log('✅ Post-auth essentials loaded');
        } catch (error) {
            console.error('❌ Failed to load post-auth essentials:', error);
            throw error;
        }
    }

    /**
     * Pre-fetch module (load in background, don't block UI)
     * @param {string} url - URL of the module to pre-fetch
     */
    function prefetch(url) {
        // Use browser's prefetch API if available
        if ('prefetch' in document.createElement('link')) {
            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = url;
            link.as = url.endsWith('.css') ? 'style' : 'script';
            document.head.appendChild(link);
            console.log(`🔮 Pre-fetching: ${url}`);
        } else {
            // Fallback: Load in background (low priority)
            setTimeout(() => {
                loadModule(url).catch(err => {
                    console.warn(`⚠️ Pre-fetch failed (non-critical): ${url}`, err);
                });
            }, 1000);
        }
    }

    /**
     * Set progress callback for loading updates
     * @param {function} callback - Function to call with (loaded, total)
     */
    function onProgress(callback) {
        progressCallback = callback;
    }

    /**
     * Check if a module is already loaded
     * @param {string} url - URL of the module
     * @returns {boolean}
     */
    function isLoaded(url) {
        return loadedModules.has(url);
    }

    /**
     * Check if an entire manifest is already loaded
     * @param {string} manifestKey - Key from MANIFESTS object (e.g., 'synergy', 'automation')
     * @returns {boolean}
     */
    function isManifestLoaded(manifestKey) {
        if (!window.MANIFESTS || !window.MANIFESTS[manifestKey]) {
            console.warn(`[LazyLoader] Manifest "${manifestKey}" not found in MANIFESTS`);
            return false;
        }

        const manifest = window.MANIFESTS[manifestKey];

        // Check if all modules in manifest are loaded
        const allLoaded = manifest.modules.every(module => {
            const url = module.url || module; // Handle both {url: '...'} and 'url' formats
            return loadedModules.has(url);
        });

        return allLoaded;
    }

    /**
     * Get loading statistics
     * @returns {object}
     */
    function getStats() {
        return {
            loaded: loadedModules.size,
            loading: loadingPromises.size,
            total: totalModules,
            progress: totalModules > 0 ? (loadedCount / totalModules * 100).toFixed(1) : 0
        };
    }

    /**
     * Clear cache (for testing/debugging)
     */
    function clearCache() {
        loadedModules.clear();
        loadingPromises.clear();
        totalModules = 0;
        loadedCount = 0;
        console.log('🧹 LazyLoader cache cleared');
    }

    // Public API
    return {
        loadModule,
        loadManifest,
        loadPostAuthEssentials,
        enablePostAuthResources,
        prefetch,
        onProgress,
        isLoaded,
        isManifestLoaded,
        getStats,
        clearCache
    };
})();

// Log initialization
console.log('✅ LazyLoader initialized');
