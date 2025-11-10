/**
 * ModuleManager - Dynamic module registration system
 * Allows external modules to integrate into the UI
 * 
 * @class ModuleManager
 * @created October 30, 2025
 */
class ModuleManager {
    constructor() {
        this.modules = new Map();
        this.activeModule = null;
        this.sidebar = null;
        this.mainContent = null;

        console.log('📦 ModuleManager initialized');
    }

    /**
     * Initialize manager (called after DOM is ready)
     */
    initialize() {
        this.sidebar = document.querySelector('.sidebar');
        this.mainContent = document.querySelector('.main-content');

        if (!this.sidebar || !this.mainContent) {
            console.error(' Required DOM elements not found (sidebar, main-content)');
            return false;
        }

        console.log('ModuleManager ready');
        return true;
    }

    /**
     * Register a new module
     * @param {Object} moduleConfig - Module configuration
     * @param {string} moduleConfig.id - Unique module identifier
     * @param {string} moduleConfig.name - Display name
     * @param {string} moduleConfig.icon - FontAwesome icon class
     * @param {string} moduleConfig.color - Icon/theme color
     * @param {string} moduleConfig.scriptPath - Path to module JS file
     * @param {Array} moduleConfig.tabs - Sub-tabs configuration
     * @param {Array} moduleConfig.dependencies - Dependencies to load
     */
    registerModule(moduleConfig) {
        console.log(`📦 Registering module: ${moduleConfig.name}`);

        // Validate module config
        if (!this.validateModule(moduleConfig)) {
            throw new Error(`Invalid module config for ${moduleConfig.id}`);
        }

        // Check if already registered
        if (this.modules.has(moduleConfig.id)) {
            console.warn(`⚠️ Module ${moduleConfig.id} already registered`);
            return;
        }

        // Store module
        this.modules.set(moduleConfig.id, {
            ...moduleConfig,
            loaded: false,
            instance: null
        });

        // Add to sidebar
        this.addSidebarIcon(moduleConfig);

        // Create tab content container
        this.createTabContainer(moduleConfig);

        // Load dependencies first, then module script
        this.loadModuleDependencies(moduleConfig).then(() => {
            this.loadModuleScript(moduleConfig);
        });

        console.log(`Module registered: ${moduleConfig.name} (${this.modules.size} total)`);
    }

    /**
     * Validate module configuration
     */
    validateModule(config) {
        const required = ['id', 'name', 'icon', 'scriptPath'];
        const missing = required.filter(field => !config[field]);

        if (missing.length > 0) {
            console.error(` Missing required fields: ${missing.join(', ')}`);
            return false;
        }

        return true;
    }

    /**
     * Add icon to sidebar
     */
    addSidebarIcon(config) {
        // Find insertion point (before last divider or end of sidebar)
        const dividers = this.sidebar.querySelectorAll('.sidebar-divider');
        const lastDivider = dividers[dividers.length - 1];

        // Create button
        const button = document.createElement('button');
        button.className = 'sidebar-icon-btn';
        button.setAttribute('data-tab', config.id);
        button.setAttribute('data-module', 'true');
        button.setAttribute('title', config.name);

        // Icon
        const icon = document.createElement('i');
        icon.className = config.icon;
        if (config.color) {
            icon.style.color = config.color;
        }
        button.appendChild(icon);

        // Event listener
        button.addEventListener('click', () => {
            this.switchToModule(config.id);
        });

        // Insert before last divider (settings section) or at end
        if (lastDivider) {
            this.sidebar.insertBefore(button, lastDivider);
        } else {
            this.sidebar.appendChild(button);
        }

        console.log(`Sidebar icon added for ${config.name}`);
    }

    /**
     * Create tab content container
     */
    createTabContainer(config) {
        const tabContent = document.createElement('div');
        tabContent.className = 'tab-content';
        tabContent.id = `tab-${config.id}`;
        tabContent.setAttribute('data-module', 'true');

        // Add loading state
        tabContent.innerHTML = `
            <div class="module-loading">
                <i class="${config.icon}" style="font-size: 48px; color: ${config.color || 'var(--accent-primary)'}"></i>
                <h3>Loading ${config.name}...</h3>
                <div class="loading-spinner"></div>
            </div>
        `;

        // Append to main content
        this.mainContent.appendChild(tabContent);

        console.log(`Tab container created for ${config.name}`);
    }

    /**
     * Load module dependencies (CSS/JS files)
     */
    async loadModuleDependencies(config) {
        // Check if dependencies exist and is an array
        if (!config.dependencies || !Array.isArray(config.dependencies) || config.dependencies.length === 0) {
            console.log(`📦 No dependencies for ${config.name}`);
            return;
        }

        console.log(`📦 Loading ${config.dependencies.length} dependencies for ${config.name}...`);

        const loadPromises = config.dependencies.map(async (dep) => {
            // Skip if already loaded
            const selector = dep.endsWith('.css')
                ? `link[href*="${dep.split('/').pop().split('?')[0]}"]`
                : `script[src*="${dep.split('/').pop().split('?')[0]}"]`;

            if (document.querySelector(selector)) {
                console.log(`⏭️ Already loaded: ${dep}`);
                return;
            }

            // Load CSS or JS
            if (dep.endsWith('.css')) {
                return this.loadCSS(dep);
            } else {
                return this.loadJS(dep);
            }
        });

        await Promise.all(loadPromises);
        console.log(`✅ All dependencies loaded for ${config.name}`);
    }

    /**
     * Load CSS file
     */
    loadCSS(url) {
        return new Promise((resolve, reject) => {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = url;
            link.onload = () => {
                console.log(`✅ CSS loaded: ${url}`);
                resolve();
            };
            link.onerror = () => {
                console.warn(`⚠️ Failed to load CSS: ${url}`);
                resolve(); // Don't reject, continue anyway
            };
            document.head.appendChild(link);
        });
    }

    /**
     * Load JS file
     */
    loadJS(url) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = url;
            script.onload = () => {
                console.log(`✅ JS loaded: ${url}`);
                resolve();
            };
            script.onerror = () => {
                console.warn(`⚠️ Failed to load JS: ${url}`);
                resolve(); // Don't reject, continue anyway
            };
            document.head.appendChild(script);
        });
    }

    /**
     * Load module script dynamically
     */
    async loadModuleScript(config) {
        try {
            console.log(`📥 Loading script for ${config.name}...`);

            const script = document.createElement('script');
            // Add DUAL cache-busting: version + random to force fresh load every time
            const version = config.version || '1.0.0';
            const random = Math.random().toString(36).substring(7);
            const cacheBuster = `?v=${version}&t=${Date.now()}&r=${random}`;
            script.src = config.scriptPath + cacheBuster;
            script.type = 'module';
            console.log(`🔄 Cache-busting URL: ${script.src}`);

            script.onload = () => {
                console.log(`Script loaded for ${config.name}`);
                // Lazy load: Don't initialize yet, wait for tab click
                this.initializeModule(config.id, true);
            };

            script.onerror = (error) => {
                console.error(` Failed to load module script: ${config.name}`, error);
                this.showModuleError(config.id, 'Failed to load module script');
            };

            document.head.appendChild(script);

        } catch (error) {
            console.error(` Error loading module ${config.name}:`, error);
            this.showModuleError(config.id, error.message);
        }
    }

    /**
     * Initialize module after script loads
     * @param {string} moduleId - Module ID
     * @param {boolean} lazy - If true, register but don't initialize yet (wait for tab click)
     */
    async initializeModule(moduleId, lazy = false) {
        const module = this.modules.get(moduleId);
        if (!module) {
            console.error(` Module ${moduleId} not found in registry`);
            return;
        }

        // LAZY LOADING: If lazy=true, mark ready but don't initialize
        if (lazy) {
            module.lazyLoadReady = true;
            console.log(`📦 Module ${module.name} ready for lazy loading (will init on first tab view)`);
            return;
        }

        console.log(`🔧 Initializing module: ${module.name}`);

        try {
            if (window.ModuleRegistry && window.ModuleRegistry[moduleId]) {
                const ModuleClass = window.ModuleRegistry[moduleId];
                module.instance = new ModuleClass(moduleId);

                await module.instance.initialize();
                module.loaded = true;

                // FIX: Store BOTH class and instance with clear naming
                window.ModuleRegistry[moduleId] = module.instance;

                // FIX: Create global wrapper functions for onclick handlers
                window[`${moduleId}_instance`] = module.instance;

                // CRITICAL FIX: Create shortened global references for HTML onclick handlers
                // This ensures modules can be called via onclick="stockModule.method()"
                const shortNames = {
                    'stock-management': 'stockModule',
                    'inhouse-kanban': 'kanbanModule',
                    'quote-calculator': 'quoteModule'
                };

                if (shortNames[moduleId]) {
                    const shortName = shortNames[moduleId];
                    window[shortName] = module.instance;
                    console.log(`✅ Global reference created: window.${shortName} = ${moduleId} instance`);
                }

                console.log(`✅ Module initialized: ${module.name}`);
            } else {
                throw new Error(`Module ${moduleId} not found in window.ModuleRegistry`);
            }
        } catch (error) {
            console.error(` Failed to initialize ${module.name}:`, error);
            this.showModuleError(moduleId, error.message);
        }
    }


    /**
     * Lazy initialize module when tab is first clicked
     * @param {string} moduleId - Module ID
     */
    async lazyInitModule(moduleId) {
        const module = this.modules.get(moduleId);
        if (!module) {
            return; // Not a module tab
        }

        // Already loaded? Skip
        if (module.loaded) {
            return;
        }

        // Ready for lazy loading? Initialize now
        if (module.lazyLoadReady) {
            console.log(`🚀 [LAZY LOAD] Initializing ${module.name} on first tab view...`);
            await this.initializeModule(moduleId); // No parameter = actually initialize (lazy defaults to false)
        }
    }

    /**
     * Switch to module tab
     */
    switchToModule(moduleId) {
        const module = this.modules.get(moduleId);
        if (!module) {
            console.error(` Module ${moduleId} not found`);
            return;
        }

        console.log(`🔄 Switching to module: ${module.name}`);

        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });

        // Remove active from all sidebar buttons
        document.querySelectorAll('.sidebar-icon-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Show module tab
        const tabContent = document.getElementById(`tab-${moduleId}`);
        if (tabContent) {
            tabContent.classList.add('active');
        } else {
            console.error(` Tab content not found: tab-${moduleId}`);
            return;
        }

        // Activate sidebar button
        const button = this.sidebar.querySelector(`[data-tab="${moduleId}"]`);
        if (button) {
            button.classList.add('active');
        }

        // Notify module it's active (if initialized)
        if (module.loaded && module.instance && module.instance.onActivate) {
            module.instance.onActivate();
        }

        this.activeModule = moduleId;

        console.log(`Switched to ${module.name}`);
    }

    /**
     * Show module error
     */
    showModuleError(moduleId, errorMessage = 'Unknown error') {
        const tabContent = document.getElementById(`tab-${moduleId}`);
        if (tabContent) {
            tabContent.innerHTML = `
                <div class="module-error">
                    <i class="fas fa-exclamation-triangle" style="font-size: 48px; color: var(--accent-error, #ef4444)"></i>
                    <h3>Failed to Load Module</h3>
                    <p>${errorMessage}</p>
                    <button class="btn btn-primary" onclick="location.reload()">
                        <i class="fas fa-sync-alt"></i> Reload Page
                    </button>
                </div>
            `;
        }
    }

    /**
     * Unregister module (cleanup)
     */
    unregisterModule(moduleId) {
        const module = this.modules.get(moduleId);
        if (!module) {
            console.warn(`⚠️ Module ${moduleId} not found`);
            return;
        }

        console.log(`🗑️ Unregistering module: ${module.name}`);

        // Cleanup module instance
        if (module.instance && module.instance.destroy) {
            module.instance.destroy();
        }

        // Remove sidebar button
        const button = this.sidebar.querySelector(`[data-tab="${moduleId}"]`);
        if (button) button.remove();

        // Remove tab content
        const tabContent = document.getElementById(`tab-${moduleId}`);
        if (tabContent) tabContent.remove();

        // Remove from registry
        this.modules.delete(moduleId);

        console.log(`Module unregistered: ${module.name}`);
    }

    /**
     * Get all registered modules
     */
    getModules() {
        return Array.from(this.modules.values());
    }

    /**
     * Get module by ID
     */
    getModule(moduleId) {
        return this.modules.get(moduleId);
    }


    getModuleInstance(moduleId) {
        const module = this.modules.get(moduleId);
        if (!module) {
            console.error(` Module ${moduleId} not found`);
            return null;
        }
        if (!module.instance) {
            console.warn(`⚠️ Module ${moduleId} not initialized yet`);
            return null;
        }
        return module.instance;
    }

}

// Initialize global module manager
console.log('🔧 Creating ModuleManager instance...');
window.ModuleManager = new ModuleManager();
window.ModuleRegistry = {}; // Modules register themselves here

console.log('ModuleManager available globally');
