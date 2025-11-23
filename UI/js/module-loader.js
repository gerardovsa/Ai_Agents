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
        console.log('📦 Loading modules from manifest...');
        console.log('📍 [DEBUG] loadModules() called from:', new Error().stack);

        try {
            // Check if we're running from file:// protocol
            if (window.location.protocol === 'file:') {
                console.log('⚠️ Running from file:// protocol - module loading disabled');
                console.log('ℹ️ To enable modules, serve the app via HTTP (e.g., python -m http.server)');
                return;
            }

            // Fetch module list with retry logic
            const response = await this.fetchWithRetry(this.manifestPath, 3);

            if (!response.ok) {
                throw new Error(`Failed to load manifest: HTTP ${response.status}`);
            }

            const manifest = await response.json();
            this.modules = manifest.modules || [];

            console.log(`📦 Found ${this.modules.length} modules in manifest`);

            // Register each enabled module
            for (const moduleConfig of this.modules) {
                if (moduleConfig.enabled !== false) {
                    await this.loadModule(moduleConfig);
                } else {
                    console.log(`⏭️ Skipping disabled module: ${moduleConfig.name}`);
                }
            }

            console.log(`Module loading complete: ${this.loadedCount} loaded, ${this.failedCount} failed`);

        } catch (error) {
            console.error(' Failed to load modules:', error);

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

/**
 * ✅ NEW HELPER: Wait for main app to be visible
 * This ensures modules don't load before authentication completes
 */
async function waitForMainApp(maxWait = 15000) {
    console.log('🔷 [MODULES] Waiting for main app to be visible...');
    const startTime = Date.now();

    while ((Date.now() - startTime) < maxWait) {
        // Check for main-content element AND visibility
        const mainContent = document.querySelector('.main-content');
        
        if (mainContent) {
            // Check if it's visible (not display: none)
            const isVisible = mainContent.offsetParent !== null;
            
            if (isVisible) {
                console.log('✅ [MODULES] Main content is visible and ready');
                return mainContent;
            } else {
                // Log only every 1 second to avoid spam
                if ((Date.now() - startTime) % 1000 < 200) {
                    console.log('⏳ [MODULES] Main content exists but hidden, waiting for auth...');
                }
            }
        } else {
            // Log only every 1 second to avoid spam
            if ((Date.now() - startTime) % 1000 < 200) {
                console.log('⏳ [MODULES] Main content not in DOM yet...');
            }
        }

        // Wait 200ms before next check
        await new Promise(resolve => setTimeout(resolve, 200));
    }

    console.error('❌ [MODULES] Timeout waiting for main app to become visible');
    console.log('   Hint: Main app should be shown after authentication');
    return null;
}

// Initialize module loader when DOM is ready
async function initializeModuleSystem() {
    console.log('🚀 [MODULES] Initializing module system...');

    // ✅ CRITICAL FIX: Wait for main app to be visible (auth must complete first)
    const mainApp = await waitForMainApp();
    if (!mainApp) {
        console.error('❌ [MODULES] Main app not found - modules disabled');
        console.log('   This usually means authentication hasn\'t completed yet');
        return;
    }

    console.log('✅ [MODULES] Main app visible, proceeding with module initialization...');

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
        // Create ModuleManager instance if it's still a class (not instantiated)
        if (typeof window.ModuleManager === 'function') {
            console.log('📦 Creating ModuleManager instance...');
            window.ModuleManager = new ModuleManager();
        }

        const initialized = await window.ModuleManager.initialize();

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

async function safeInitializeModuleSystem() {
    if (moduleSystemInitialized) {
        console.log('⏭️ [MODULES] Module system already initialized, skipping duplicate call');
        return;
    }
    moduleSystemInitialized = true;
    await initializeModuleSystem();
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
