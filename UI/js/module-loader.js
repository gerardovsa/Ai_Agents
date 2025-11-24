/**
 * ModuleLoader - Loads modules from manifest list
 * Auto-loads enabled modules on page load
 * 
 * @class ModuleLoader
 * @created October 30, 2025
 */
class ModuleLoader {
    constructor() {
        // Use relative path from current page location
        this.manifestPath = 'external/modules/manifest.json';
        this.modules = [];
        this.loadedCount = 0;
        this.failedCount = 0;

        console.log('📦 ModuleLoader created');
    }

    /**
     * Fetch with retry logic (exponential backoff)
     */
    async fetchWithRetry(url, maxRetries = 3, delay = 500) {
        for (let i = 0; i < maxRetries; i++) {
            try {
                const response = await fetch(url);
                if (response.ok) {
                    return response;
                }
                console.warn(`⚠️ Fetch attempt ${i + 1}/${maxRetries} failed: HTTP ${response.status}`);
            } catch (error) {
                console.warn(`⚠️ Fetch attempt ${i + 1}/${maxRetries} error:`, error.message);
            }

            if (i < maxRetries - 1) {
                // Wait before retrying (exponential backoff)
                await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
            }
        }
        throw new Error(`Failed to fetch ${url} after ${maxRetries} attempts`);
    }

    /**
     * Load all modules from manifest
     */
    async loadModules() {
        console.log('%c🚀 [MODULE-LOADER] loadModules() CALLED', 'background: #4CAF50; color: white; padding: 4px 8px; font-weight: bold');
        console.log('📦 [MODULE-LOADER] Loading modules from manifest...');
        console.log('📍 [MODULE-LOADER] Manifest path:', this.manifestPath);
        console.log('📍 [MODULE-LOADER] Full URL:', window.location.origin + '/' + this.manifestPath);
        console.log('📍 [MODULE-LOADER] window.location.protocol:', window.location.protocol);

        try {
            // Check if we're running from file:// protocol
            if (window.location.protocol === 'file:') {
                console.log('%c⚠️ [MODULE-LOADER] Running from file:// - ABORTING', 'background: orange; color: black; padding: 4px');
                console.log('ℹ️ To enable modules, serve the app via HTTP (e.g., python -m http.server)');
                return;
            }

            console.log('✅ [MODULE-LOADER] Protocol check passed (not file://)');
            console.log('📡 [MODULE-LOADER] Fetching manifest...');

            // Fetch module list with retry logic
            const response = await this.fetchWithRetry(this.manifestPath, 3);

            console.log('✅ [MODULE-LOADER] Manifest fetch response:', response.status, response.statusText);

            if (!response.ok) {
                throw new Error(`Failed to load manifest: HTTP ${response.status}`);
            }

            const manifest = await response.json();
            console.log('📦 [MODULE-LOADER] Parsed manifest:', manifest);

            this.modules = manifest.modules || [];

            console.log(`📦 [MODULE-LOADER] Found ${this.modules.length} modules in manifest`);
            console.log('📋 [MODULE-LOADER] Module list:', this.modules.map(m => `${m.name} (${m.enabled !== false ? 'enabled' : 'disabled'})`));

            // Register each enabled module
            for (const moduleConfig of this.modules) {
                if (moduleConfig.enabled !== false) {
                    console.log(`🔄 [MODULE-LOADER] Loading module: ${moduleConfig.name}`);
                    await this.loadModule(moduleConfig);
                } else {
                    console.log(`⏭️ [MODULE-LOADER] Skipping disabled module: ${moduleConfig.name}`);
                }
            }

            console.log(`✅ [MODULE-LOADER] Module loading complete: ${this.loadedCount} loaded, ${this.failedCount} failed`);

        } catch (error) {
            console.error('❌ [MODULE-LOADER] Failed to load modules:', error);
            console.error('❌ [MODULE-LOADER] Error stack:', error.stack);

            // Show notification to user
            this.showLoadingError(error.message);
        }
    }

    /**
     * Load individual module
     */
    async loadModule(moduleConfig) {
        try {
            console.log(`📦 Loading module: ${moduleConfig.name}`);

            // Fetch module manifest if path provided
            let fullManifest = moduleConfig;

            if (moduleConfig.manifestPath) {
                try {
                    const manifestResponse = await fetch(moduleConfig.manifestPath);
                    if (manifestResponse.ok) {
                        const moduleManifest = await manifestResponse.json();
                        // Merge with config from main manifest
                        fullManifest = { ...moduleManifest, ...moduleConfig };
                    }
                } catch (error) {
                    console.warn(`⚠️ Could not load manifest for ${moduleConfig.name}, using config from main manifest`);
                }
            }

            // Register with ModuleManager
            if (window.ModuleManager) {
                // Pass full manifest to include ALL properties (dependencies, version, etc.)
                window.ModuleManager.registerModule(fullManifest);

                this.loadedCount++;
                console.log(`Module registered: ${moduleConfig.name}`);
            } else {
                throw new Error('ModuleManager not available');
            }

        } catch (error) {
            console.error(` Failed to load module ${moduleConfig.name}:`, error);
            this.failedCount++;
        }
    }

    /**
     * Show loading error notification
     */
    showLoadingError(message) {
        // Create error notification
        const notification = document.createElement('div');
        notification.className = 'module-loader-error';
        notification.innerHTML = `
            <div class="notification error">
                <i class="fas fa-exclamation-triangle"></i>
                <div class="notification-content">
                    <strong>Module Loading Error</strong>
                    <p>${message}</p>
                </div>
                <button class="notification-close" onclick="this.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 10000);
    }

    /**
     * Reload all modules
     */
    async reloadModules() {
        console.log('🔄 Reloading all modules...');

        // Clear counters
        this.loadedCount = 0;
        this.failedCount = 0;

        // Unregister all existing modules
        if (window.ModuleManager) {
            const modules = window.ModuleManager.getModules();
            modules.forEach(module => {
                if (module.id) {
                    window.ModuleManager.unregisterModule(module.id);
                }
            });
        }

        // Load modules again
        await this.loadModules();
    }
}

// Initialize module loader when DOM is ready
// ✅ REVERTED TO V5/V6 PATTERN - Simple and proven working
// Removed complex waitForMainApp() logic that was causing silent failures
async function initializeModuleSystem() {
    console.log('🚀 Initializing module system...');

    // Wait for ModuleManager class to be available (with timeout)
    const maxWait = 5000; // 5 seconds
    const startTime = Date.now();

    while (!window.ModuleManager && (Date.now() - startTime) < maxWait) {
        console.log('⏳ Waiting for ModuleManager class...');
        await new Promise(resolve => setTimeout(resolve, 100));
    }

    if (!window.ModuleManager) {
        console.error('❌ ModuleManager not found after timeout');
        console.log('Available window properties:', Object.keys(window).filter(k => k.includes('Module')));
        return;
    }

    try {
        // Create ModuleManager instance if needed
        if (!window.ModuleManager.initialize) {
            window.ModuleManager = new ModuleManager();
        }

        const initialized = window.ModuleManager.initialize();

        if (initialized) {
            // Create and run module loader
            window.ModuleLoader = new ModuleLoader();
            await window.ModuleLoader.loadModules();

            console.log('✅ Module system ready');
        } else {
            console.error('❌ ModuleManager failed to initialize - DOM elements missing?');
        }
    } catch (error) {
        console.error('❌ Module system initialization error:', error);
        // Try to show user-friendly error
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            const errorDiv = document.createElement('div');
            errorDiv.style.cssText = 'padding: 40px; text-align: center; color: var(--text-secondary);';
            errorDiv.innerHTML = `
                <i class="fas fa-exclamation-triangle" style="font-size: 48px; color: #ef4444; margin-bottom: 16px;"></i>   
                <h3 style="color: var(--text-primary); margin-bottom: 8px;">Module System Failed to Load</h3>
                <p style="margin-bottom: 20px;">${error.message}</p>
                <button class="btn btn-primary" onclick="location.reload()">
                    <i class="fas fa-sync-alt"></i> Reload Page
                </button>
            `;
            mainContent.prepend(errorDiv);
        }
    }
}

// Single initialization point with debouncing to prevent duplicate calls
let moduleSystemInitialized = false;
let moduleSystemInitializing = false;

async function safeInitializeModuleSystem(forceLoad = false) {
    console.log('🔷 [MODULES] safeInitializeModuleSystem called with forceLoad:', forceLoad, '| initialized:', moduleSystemInitialized, 'initializing:', moduleSystemInitializing);

    // ✅ FIX: Check if modules are actually loaded, not just if flag is set
    const actuallyInitialized = moduleSystemInitialized && window.ModuleManager?.getModules().length > 0;

    // If already initialized successfully, return immediately
    if (actuallyInitialized && !forceLoad) {
        console.log('⏭️ [MODULES] Module system already initialized with', window.ModuleManager.getModules().length, 'modules');
        return;
    }

    // If already initializing, ABORT to prevent recursion
    if (moduleSystemInitializing) {
        console.warn('⚠️ [MODULES] Already initializing - ABORTING to prevent recursion!');
        return;
    }

    // Reset flag if it was set but modules weren't loaded
    if (moduleSystemInitialized && window.ModuleManager?.getModules().length === 0) {
        console.log('⚠️ [MODULES] Flag was set but no modules loaded, resetting...');
        moduleSystemInitialized = false;
    }

    if (forceLoad) {
        console.log('⚡ [MODULES] Force load enabled - resetting flags and reinitializing...');
        moduleSystemInitialized = false;
        moduleSystemInitializing = false;
    }

    // Set flag BEFORE calling to prevent recursion
    moduleSystemInitializing = true;
    console.log('🚀 [MODULES] Starting module system initialization...');

    try {
        await initializeModuleSystem();
        moduleSystemInitialized = true;
    } catch (error) {
        console.error('❌ [MODULES] Module system initialization FAILED:', error);
        throw error;
    } finally {
        moduleSystemInitializing = false;
    }
}

// ❌ REMOVED: Don't initialize automatically on DOMContentLoaded
// Modules should only load AFTER authentication completes
// The auth system (user_auth.js) will call window.initializeModuleSystem() when ready

console.log('✅ ModuleLoader script loaded (waiting for auth to trigger initialization)');
console.log('   💡 Modules will load after UserAuth.showMainApp() calls initializeModuleSystem()');

// ⚠️ CRITICAL: Expose ModuleLoader class to window IMMEDIATELY (not just instance)
// This allows other code to check `if (window.ModuleLoader)` before async init completes
window.ModuleLoader = ModuleLoader;

// ✅ Expose for manual initialization by auth system
window.initializeModuleSystem = safeInitializeModuleSystem;
