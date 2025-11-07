/**
 * ModuleLoader - Loads modules from manifest list
 * Auto-loads enabled modules on page load
 * 
 * @class ModuleLoader
 * @created October 30, 2025
 */
class ModuleLoader {
    constructor() {
        this.manifestPath = 'external/modules/manifest.json';
        this.modules = [];
        this.loadedCount = 0;
        this.failedCount = 0;

        console.log('📦 ModuleLoader created');
    }

    /**
     * Load all modules from manifest
     */
    async loadModules() {
        console.log('📦 Loading modules from manifest...');

        try {
            // Fetch module list
            const response = await fetch(this.manifestPath);

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

            console.log(`✅ Module loading complete: ${this.loadedCount} loaded, ${this.failedCount} failed`);

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
                window.ModuleManager.registerModule({
                    id: fullManifest.id,
                    name: fullManifest.name,
                    icon: fullManifest.icon,
                    color: fullManifest.color,
                    description: fullManifest.description,
                    scriptPath: fullManifest.scriptPath,
                    tabs: fullManifest.tabs,
                    settings: fullManifest.settings
                });

                this.loadedCount++;
                console.log(`✅ Module registered: ${moduleConfig.name}`);
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
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 DOM ready, initializing module system...');

    // Wait for ModuleManager to initialize
    if (window.ModuleManager) {
        const initialized = window.ModuleManager.initialize();

        if (initialized) {
            // Create and run module loader
            window.ModuleLoader = new ModuleLoader();
            await window.ModuleLoader.loadModules();

            console.log('✅ Module system ready');
        } else {
            console.error(' ModuleManager failed to initialize');
        }
    } else {
        console.error(' ModuleManager not found');
    }
});

console.log('✅ ModuleLoader script loaded');
