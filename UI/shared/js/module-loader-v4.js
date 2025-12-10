/**
 * FILE: UI/shared/js/module-loader-v4.js
 * PURPOSE: Modern composition-based module loader
 * 
 * ARCHITECTURE: Functional composition with manifest-driven lifecycle
 * - NO BaseModule inheritance
 * - Modules are plain objects with lifecycle hooks
 * - Utilities passed via composition (not inheritance)
 * - Manifest declares dependencies and lifecycle
 * - Supports BOTH modern (composition) and legacy (BaseModule) modules
 * 
 * LIFECYCLE:
 * 1. ModuleLoader.loadModule(moduleId)
 * 2. Fetch manifest from API
 * 3. Load module JS file (dynamic import)
 * 4. Detect pattern (modern vs legacy)
 * 5. Compose utilities based on dependencies
 * 6. Call lifecycle hook (onLoad, onDashboardLoad, onSidebarLoad)
 * 7. Module initializes with composed utilities
 * 
 * EXPORTS:
 * - ModuleLoaderV4 (singleton)
 * 
 * LAST MODIFIED: 2025-11-29 - Initial composition-based implementation
 */

// Cache-busting timestamp added to force reload of module-utilities.js
import { UtilityComposer } from './module-utilities.js?v=20251130235959';

class ModuleLoaderV4 {
    constructor() {
        if (ModuleLoaderV4.instance) {
            return ModuleLoaderV4.instance;
        }

        this.modules = new Map(); // moduleId → manifest
        this.loadedModules = new Map(); // moduleId → module instance
        this.activeModule = null;
        this.userId = null;

        // Track initialization state
        this.initialized = false;
        this.initializing = false;

        ModuleLoaderV4.instance = this;
        console.log('🔷 ModuleLoaderV4 initialized (Composition pattern)');
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // INITIALIZATION
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Initialize module loader
     */
    async initialize(userId) {
        if (this.initialized) {
            console.warn('[ModuleLoaderV4] Already initialized');
            return;
        }

        if (this.initializing) {
            console.warn('[ModuleLoaderV4] Initialization in progress');
            return;
        }

        this.initializing = true;
        this.userId = userId;

        try {
            // Fetch all registered modules from API
            const response = await fetch('/api/modules/list');
            const data = await response.json();

            if (!data.modules) {
                throw new Error('No modules returned from API');
            }

            console.log(`[ModuleLoaderV4] Found ${data.count} registered modules`);

            // Store module manifests
            data.modules.forEach(module => {
                if (module.enabled !== false) {
                    this.modules.set(module.id, module);
                }
            });

            // Check which modules user can access
            await this.checkModuleAvailability();

            // Generate UI elements
            await this.generateSidebarButtons();
            this.generateFloatingToggles();
            this.generateMainTabs();

            // Load auto-load modules
            await this.loadAutoLoadModules();

            this.initialized = true;
            this.initializing = false;
            console.log('[ModuleLoaderV4] ✅ Initialization complete');

        } catch (error) {
            console.error('[ModuleLoaderV4] Initialization failed:', error);
            this.initializing = false;
            throw error;
        }
    }

    /**
     * Check which modules user has credentials for
     */
    async checkModuleAvailability() {
        try {
            const response = await fetch(`/api/modules/available?user_id=${this.userId}`);
            const data = await response.json();

            if (!data.modules) return;

            data.modules.forEach(availableModule => {
                const module = this.modules.get(availableModule.id);
                if (module) {
                    module.available = true;
                }
            });

        } catch (error) {
            console.error('[ModuleLoaderV4] Failed to check availability:', error);
        }
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // MODULE LOADING (Core Logic)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Load module (detects pattern and routes accordingly)
     * 
     * @param {string} moduleId - Module ID
     * @param {string} view - 'dashboard' | 'sidebar' | 'auto'
     */
    async loadModule(moduleId, view = 'auto') {
        const manifest = this.modules.get(moduleId);
        if (!manifest) {
            throw new Error(`Module not found: ${moduleId}`);
        }

        console.log(`[ModuleLoaderV4] Loading ${moduleId} (view: ${view})`);

        // Check if already loaded
        if (this.loadedModules.has(moduleId)) {
            console.log(`[ModuleLoaderV4] ${moduleId} already loaded, calling lifecycle hook`);
            return this.callLifecycleHook(moduleId, view);
        }

        try {
            // 1. Load CSS file first (if specified)
            if (manifest.css_file || manifest.stylePath) {
                await this.loadCSS(moduleId, manifest);
            }

            // 2. Load module JS file (dynamic import)
            // Check multiple manifest formats for compatibility:
            // - manifest.paths.script (V4 format)
            // - manifest.paths.js (alternative V4 format)
            // - manifest.scriptPath (legacy)
            // - manifest.js_file (V3 format)
            // - fallback: external/modules/{moduleId}/{moduleId}.js
            const modulePath = manifest.paths?.script
                || manifest.paths?.js
                || manifest.scriptPath
                || (manifest.js_file ? `external/modules/${moduleId}/${manifest.js_file}` : null)
                || `external/modules/${moduleId}/${manifest.files?.js || moduleId + '.js'}`;
            const moduleExports = await this.importModule(modulePath);

            // 2. Detect pattern (modern vs legacy)
            let pattern = this.detectPattern(moduleExports);
            console.log(`[ModuleLoaderV4] Initial pattern detection: ${pattern}`);

            // FIXED (Dec 10, 2025): If pattern is unknown, check again after module execution
            // Some legacy modules register themselves to window.ModuleRegistry during execution
            if (pattern === 'unknown') {
                // Wait a bit for module to execute and register itself
                await new Promise(resolve => setTimeout(resolve, 50));
                pattern = this.detectPattern(moduleExports);
                console.log(`[ModuleLoaderV4] Re-checked pattern after delay: ${pattern}`);

                // If still unknown, default to legacy (most backward-compatible)
                if (pattern === 'unknown') {
                    console.warn(`[ModuleLoaderV4] Pattern still unknown for ${moduleId}, defaulting to legacy`);
                    pattern = 'legacy';
                }
            }

            // 3. Load based on pattern
            if (pattern === 'modern') {
                await this.loadModernModule(moduleId, manifest, moduleExports, view);
            } else if (pattern === 'legacy') {
                await this.loadLegacyModule(moduleId, manifest, moduleExports, view);
            } else {
                throw new Error(`Unknown module pattern: ${pattern}`);
            }

            console.log(`[ModuleLoaderV4] ✅ ${moduleId} loaded successfully`);

        } catch (error) {
            console.error(`[ModuleLoaderV4] Failed to load ${moduleId}:`, error);
            throw error;
        }
    }

    /**
     * Import module file (handles both ES6 and legacy script loading)
     */
    async importModule(modulePath) {
        try {
            // Normalize path for Flask routing
            let importPath = modulePath;

            // Strip UI/modules_external/ or UI/modules_internal/ prefix if present
            // Flask serves modules at /external/modules/ and /internal/modules/
            if (importPath.includes('UI/modules_external/')) {
                importPath = importPath.replace('UI/modules_external/', 'external/modules/');
            } else if (importPath.includes('UI/modules_internal/')) {
                importPath = importPath.replace('UI/modules_internal/', 'internal/modules/');
            }

            // Ensure path is absolute or starts with / for ES6 import
            if (!importPath.startsWith('/') && !importPath.startsWith('http') && !importPath.startsWith('./') && !importPath.startsWith('../')) {
                // Relative path - convert to absolute by adding leading /
                importPath = '/' + importPath;
            }

            console.log(`[ModuleLoaderV4] 🔷 Importing ES6 module: ${importPath}`);

            // Try ES6 dynamic import
            return await import(importPath);
        } catch (error) {
            console.warn(`[ModuleLoaderV4] ES6 import failed for ${modulePath}, trying script tag fallback:`, error.message);
            // Fallback: Load as script tag (for legacy modules)
            return await this.loadScriptTag(modulePath);
        }
    }

    /**
     * Load script as <script> tag (fallback for legacy modules)
     */
    async loadScriptTag(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = () => resolve(window); // Legacy modules export to window
            script.onerror = () => reject(new Error(`Failed to load script: ${src}`));
            document.head.appendChild(script);
        });
    }

    /**
     * Detect module pattern
     * 
     * @returns {'modern' | 'legacy' | 'unknown'}
     */
    detectPattern(moduleExports) {
        const moduleId = this.activeModuleId;

        // PRIORITY 1: Check ModuleRegistry first (most common legacy pattern)
        if (window.ModuleRegistry && window.ModuleRegistry[moduleId]) {
            const ModuleClass = window.ModuleRegistry[moduleId];
            if (typeof ModuleClass === 'function') {
                console.log(`[ModuleLoaderV4] Detected legacy via ModuleRegistry for ${moduleId}`);
                return 'legacy';
            }
        }

        // PRIORITY 2: Modern pattern - Exports object with lifecycle hooks
        if (moduleExports.default && typeof moduleExports.default === 'object') {
            if (typeof moduleExports.default.onLoad === 'function' ||
                typeof moduleExports.default.onDashboardLoad === 'function' ||
                typeof moduleExports.default.onSidebarLoad === 'function') {
                return 'modern';
            }
        }

        // PRIORITY 3: Legacy pattern - ES6 exported class (check if it's a constructor function)
        if (moduleExports.default && typeof moduleExports.default === 'function') {
            // Check if it's a class constructor
            if (moduleExports.default.prototype && moduleExports.default.prototype.constructor === moduleExports.default) {
                return 'legacy';
            }
        }

        // PRIORITY 4: Legacy pattern - Class extends BaseModule (check prototype chain)
        if (typeof BaseModule !== 'undefined') {
            if (moduleExports.default &&
                moduleExports.default.prototype instanceof BaseModule) {
                return 'legacy';
            }
        }

        // PRIORITY 5: Check window for legacy global instantiation
        if (window[moduleId] && typeof window[moduleId].initialize === 'function') {
            return 'legacy';
        }

        return 'unknown';
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // MODERN MODULE LOADING (Composition pattern)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Load modern module (composition-based)
     */
    async loadModernModule(moduleId, manifest, moduleExports, view) {
        console.log(`[ModuleLoaderV4] Loading MODERN module: ${moduleId}`);

        const module = moduleExports.default;

        // 1. Compose utilities based on manifest dependencies
        const utilities = UtilityComposer.compose(manifest.dependencies, moduleId);

        // 2. Load HTML if specified
        if (view === 'dashboard' && manifest.dashboard_html) {
            await this.loadHTML(moduleId, manifest.dashboard_html, 'dashboard');
        }
        // Support both manifest.html_file and manifest.files.html for sidebar HTML
        const sidebarHtmlFile = manifest.html_file || manifest.files?.html;
        if (view === 'sidebar' && sidebarHtmlFile) {
            await this.loadHTML(moduleId, sidebarHtmlFile, 'sidebar');
        }

        // 3. Store module instance
        this.loadedModules.set(moduleId, {
            type: 'modern',
            module: module,
            utilities: utilities,
            manifest: manifest
        });

        // 4. Call appropriate lifecycle hook
        if (view === 'dashboard' && module.onDashboardLoad) {
            await module.onDashboardLoad(utilities);
        } else if (view === 'sidebar' && module.onSidebarLoad) {
            await module.onSidebarLoad(utilities);
        } else if (module.onLoad) {
            await module.onLoad(utilities);
        }
    }

    /**
     * Call lifecycle hook on already-loaded modern module
     */
    async callLifecycleHook(moduleId, view) {
        const loaded = this.loadedModules.get(moduleId);
        if (!loaded || loaded.type !== 'modern') return;

        const { module, utilities } = loaded;

        if (view === 'dashboard' && module.onDashboardLoad) {
            await module.onDashboardLoad(utilities);
        } else if (view === 'sidebar' && module.onSidebarLoad) {
            await module.onSidebarLoad(utilities);
        }
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // LEGACY MODULE LOADING (BaseModule pattern)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Load legacy module (BaseModule inheritance)
     */
    async loadLegacyModule(moduleId, manifest, moduleExports, view) {
        console.log(`[ModuleLoaderV4] Loading LEGACY module: ${moduleId}`);

        // Check if instance already exists on window
        let instance = window[moduleId];

        // If no instance, try to get class from ES6 export
        if (!instance && moduleExports.default && typeof moduleExports.default === 'function') {
            const ModuleClass = moduleExports.default;
            console.log(`[ModuleLoaderV4] Instantiating ${moduleId} from ES6 export`);
            instance = new ModuleClass(moduleId);
            window[moduleId] = instance; // Store on window for global access
        }

        // If still no instance, check ModuleRegistry for class and instantiate
        if (!instance && window.ModuleRegistry && window.ModuleRegistry[moduleId]) {
            const ModuleClass = window.ModuleRegistry[moduleId];
            console.log(`[ModuleLoaderV4] Instantiating ${moduleId} from ModuleRegistry`);
            instance = new ModuleClass(moduleId);
            window[moduleId] = instance; // Store on window for global access
        }

        if (!instance) {
            console.warn(`[ModuleLoaderV4] Legacy module ${moduleId} not found on window, ES6 export, or ModuleRegistry`);
            return;
        }

        // Set container reference (legacy modules expect this.container)
        const tabId = manifest.main_tab_id || manifest.capabilities?.dashboard?.tab_id || moduleId;
        const container = document.getElementById(`tab-${tabId}`);
        if (container) {
            instance.container = container;
            console.log(`[ModuleLoaderV4] Set container for ${moduleId}: tab-${tabId}`);
        } else {
            console.warn(`[ModuleLoaderV4] Container tab-${tabId} not found for ${moduleId}`);
        }

        // Store module instance
        this.loadedModules.set(moduleId, {
            type: 'legacy',
            module: instance,
            manifest: manifest
        });

        // Call initialize if not already initialized
        if (typeof instance.initialize === 'function' && !instance.initialized) {
            await instance.initialize();
            instance.initialized = true;
        }
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // CSS LOADING
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Load CSS file and inject into DOM
     */
    async loadCSS(moduleId, manifest) {
        // Check if already loaded
        if (document.querySelector(`link[data-module="${moduleId}"]`)) {
            console.log(`[ModuleLoaderV4] CSS already loaded for ${moduleId}`);
            return;
        }

        try {
            // Check multiple manifest formats for compatibility:
            // - manifest.paths.style (V4 format)
            // - manifest.paths.css (alternative V4 format)
            // - manifest.stylePath (legacy)
            // - manifest.css_file (V3 format)
            // - fallback: external/modules/{moduleId}/{moduleId}.css
            let cssPath = manifest.paths?.style
                || manifest.paths?.css
                || manifest.stylePath
                || (manifest.css_file ? `external/modules/${moduleId}/${manifest.css_file}` : null)
                || `external/modules/${moduleId}/${manifest.files?.css || moduleId + '.css'}`;

            // Normalize path for Flask routing
            // Strip UI/modules_external/ or UI/modules_internal/ prefix if present
            if (cssPath.includes('UI/modules_external/')) {
                cssPath = cssPath.replace('UI/modules_external/', 'external/modules/');
            } else if (cssPath.includes('UI/modules_internal/')) {
                cssPath = cssPath.replace('UI/modules_internal/', 'internal/modules/');
            }

            // Ensure absolute path
            if (!cssPath.startsWith('/') && !cssPath.startsWith('http')) {
                cssPath = '/' + cssPath;
            }

            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = cssPath;
            link.dataset.module = moduleId;

            link.onerror = () => {
                console.warn(`[ModuleLoaderV4] Failed to load CSS for ${moduleId} from ${cssPath}`);
            };

            link.onload = () => {
                console.log(`[ModuleLoaderV4] ✅ Loaded CSS for ${moduleId}`);
            };

            document.head.appendChild(link);

        } catch (error) {
            console.error(`[ModuleLoaderV4] CSS load error for ${moduleId}:`, error);
        }
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // HTML LOADING
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Load HTML file and inject into DOM
     */
    async loadHTML(moduleId, htmlFile, type = 'sidebar') {
        try {
            // Support full paths (manifest.paths.sidebar_html) or just filenames
            const htmlPath = htmlFile.startsWith('http') || htmlFile.includes('/')
                ? htmlFile
                : `external/modules/${moduleId}/${htmlFile}`;

            const response = await fetch(htmlPath);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const html = await response.text();

            if (type === 'sidebar') {
                // Inject sidebar HTML into body
                const temp = document.createElement('div');
                temp.innerHTML = html;
                const sidebarElement = temp.firstElementChild;
                if (sidebarElement) {
                    document.body.appendChild(sidebarElement);
                }
            } else if (type === 'dashboard') {
                // Inject dashboard HTML into tab container
                const container = document.getElementById(`tab-${moduleId}`);
                if (container) {
                    container.innerHTML = html;
                }
            }

            console.log(`[ModuleLoaderV4] ✅ Loaded ${type} HTML for ${moduleId}`);

        } catch (error) {
            console.error(`[ModuleLoaderV4] Failed to load ${type} HTML:`, error);
            throw error;
        }
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // UI GENERATION (Sidebar buttons, floating toggles, tabs)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Generate sidebar buttons for available modules
     */
    async generateSidebarButtons() {
        const sidebar = document.getElementById('sidebarModulesSection') ||
            document.querySelector('.sidebar');

        if (!sidebar) {
            console.warn('[ModuleLoaderV4] Sidebar container not found');
            return;
        }

        let container = sidebar.id === 'sidebarModulesSection'
            ? sidebar
            : document.getElementById('module-buttons-container');

        if (!container) {
            container = document.createElement('div');
            container.id = 'module-buttons-container';
            sidebar.appendChild(container);
        }

        container.innerHTML = '';

        // Generate button for each available module
        for (const [moduleId, module] of this.modules) {
            if (!module.available) continue;
            if (module.module_type === 'component') continue;

            const button = document.createElement('button');
            button.className = 'sidebar-icon-btn';
            button.title = module.name;
            button.dataset.moduleId = moduleId;

            const icon = document.createElement('i');
            icon.className = module.icon.includes(' ') ? module.icon : `fas ${module.icon}`;
            if (module.color) icon.style.color = module.color;
            button.appendChild(icon);

            // Click handler
            button.addEventListener('click', async () => {
                await this.onSidebarButtonClick(moduleId);
            });

            container.appendChild(button);
        }

        console.log(`[ModuleLoaderV4] Generated ${container.children.length} sidebar buttons`);
    }

    /**
     * Generate floating toggle buttons
     */
    generateFloatingToggles() {
        for (const [moduleId, module] of this.modules) {
            if (!module.available) continue;
            if (!module.floating_toggle && !module.capabilities?.sidebar?.toggle_button) continue;

            const toggle = document.createElement('button');
            toggle.id = `${moduleId}-floating-toggle`;
            toggle.className = 'floating-toggle-btn';
            toggle.dataset.moduleId = moduleId;

            const icon = document.createElement('i');
            icon.className = module.icon.includes(' ') ? module.icon : `fas ${module.icon}`;
            if (module.color) icon.style.color = module.color;
            toggle.appendChild(icon);

            // Click handler
            toggle.addEventListener('click', async () => {
                await this.onFloatingToggleClick(moduleId);
            });

            document.body.appendChild(toggle);
            this.initializeFloatingToggle(toggle, module);
        }
    }

    /**
     * Initialize floating toggle (drag, positioning)
     */
    initializeFloatingToggle(toggle, module) {
        const moduleId = module.id;
        const side = localStorage.getItem(`${moduleId}-toggle-side`) ||
            module.floating_toggle_position || 'left';
        const top = localStorage.getItem(`${moduleId}-toggle-top`) ||
            `${module.floating_toggle_default_top || 280}px`;

        toggle.style.top = top;
        toggle.style[side] = '60px';
    }

    /**
     * Generate main tab containers
     */
    generateMainTabs() {
        console.log('[ModuleLoaderV4] 🔧 generateMainTabs() called');

        const mainContent = document.querySelector('.main-content') ||
            document.getElementById('main-content');

        if (!mainContent) {
            console.warn('[ModuleLoaderV4] ❌ Main content area not found');
            return;
        }

        console.log(`[ModuleLoaderV4] ✅ Main content found, has ${mainContent.children.length} children`);
        let tabsCreated = 0;

        for (const [moduleId, module] of this.modules) {
            if (!module.available) {
                console.log(`[ModuleLoaderV4]   ⏭️ Skipping ${moduleId} - not available`);
                continue;
            }
            if (!module.main_tab && !module.capabilities?.dashboard?.enabled) {
                console.log(`[ModuleLoaderV4]   ⏭️ Skipping ${moduleId} - no dashboard capability`);
                continue;
            }

            const tabId = module.main_tab_id || module.capabilities?.dashboard?.tab_id || moduleId;

            if (document.getElementById(`tab-${tabId}`)) {
                console.log(`[ModuleLoaderV4]   ⏭️ Tab tab-${tabId} already exists`);
                continue;
            }

            const tab = document.createElement('div');
            tab.className = 'tab-content';  // MUST be tab-content, not content-section
            tab.id = `tab-${tabId}`;
            // Don't set inline display:none - let CSS handle visibility via .tab-content/.active classes
            mainContent.appendChild(tab);
            tabsCreated++;
            console.log(`[ModuleLoaderV4]   ✅ Created tab-${tabId} for ${moduleId}`);
        }

        console.log(`[ModuleLoaderV4] 🎉 Generated ${tabsCreated} new tabs. Total tabs now: ${document.querySelectorAll('.tab-content').length}`);
    }

    /**
     * Load auto-load modules
     */
    async loadAutoLoadModules() {
        for (const [moduleId, module] of this.modules) {
            if (module.available && module.auto_load) {
                await this.loadModule(moduleId, 'auto');
            }
        }
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // EVENT HANDLERS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Handle sidebar button click
     */
    async onSidebarButtonClick(moduleId) {
        const module = this.modules.get(moduleId);

        // Load module if not loaded
        if (!this.loadedModules.has(moduleId)) {
            await this.loadModule(moduleId, 'dashboard');
        }

        // Switch to dashboard tab
        const tabId = module.main_tab_id || module.capabilities?.dashboard?.tab_id || moduleId;
        if (typeof switchTab === 'function') {
            switchTab(tabId);
        }

        // Call dashboard lifecycle hook if modern
        const loaded = this.loadedModules.get(moduleId);
        if (loaded && loaded.type === 'modern' && loaded.module.onDashboardLoad) {
            await loaded.module.onDashboardLoad(loaded.utilities);
        }
    }

    /**
     * Handle floating toggle click
     */
    async onFloatingToggleClick(moduleId) {
        const module = this.modules.get(moduleId);

        // Load module if not loaded
        if (!this.loadedModules.has(moduleId)) {
            await this.loadModule(moduleId, 'sidebar');
        }

        // Open sidebar
        const sidebarId = `${moduleId}-sidebar`;
        if (window.SidebarManager) {
            window.SidebarManager.toggle(sidebarId);
        } else {
            const sidebar = document.getElementById(sidebarId);
            if (sidebar) sidebar.classList.toggle('active');
        }

        // Call sidebar lifecycle hook if modern
        const loaded = this.loadedModules.get(moduleId);
        if (loaded && loaded.type === 'modern' && loaded.module.onSidebarLoad) {
            await loaded.module.onSidebarLoad(loaded.utilities);
        }
    }

    /**
     * Toggle module sidebar visibility (CRITICAL METHOD)
     * Used by sidebar buttons and floating toggles throughout the system
     * 
     * @param {string} moduleId - Module ID to toggle
     */
    async toggleModule(moduleId) {
        console.log(`[ModuleLoaderV4] Toggling module: ${moduleId}`);

        // Load module if not loaded
        if (!this.loadedModules.has(moduleId)) {
            const loaded = await this.loadModule(moduleId, 'sidebar');
            if (!loaded) {
                return;
            }
        }

        const module = this.modules.get(moduleId);
        const sidebarElement = document.getElementById(`${moduleId}-sidebar`);

        if (!sidebarElement) {
            console.error(`[ModuleLoaderV4] Sidebar element not found for ${moduleId}`);
            return;
        }

        // Close currently active module
        if (this.activeModule && this.activeModule !== moduleId) {
            const activeElement = document.getElementById(`${this.activeModule}-sidebar`);
            if (activeElement) {
                activeElement.classList.remove('active');
            }
        }

        // Toggle this module
        const isActive = sidebarElement.classList.toggle('active');

        if (isActive) {
            this.activeModule = moduleId;
            console.log(`[ModuleLoaderV4] Opened module: ${module.name}`);

            // Call sidebar lifecycle hook if modern
            const loaded = this.loadedModules.get(moduleId);
            if (loaded && loaded.type === 'modern' && loaded.module.onSidebarLoad) {
                await loaded.module.onSidebarLoad(loaded.utilities);
            }

            // Initialize legacy module controller (if exists)
            const controllerName = `${moduleId.replace(/-/g, '')}Controller`;
            if (window[controllerName]) {
                if (!window[controllerName].initialized && typeof window[controllerName].init === 'function') {
                    await window[controllerName].init();
                    window[controllerName].initialized = true;
                }
            }
        } else {
            this.activeModule = null;
            console.log(`[ModuleLoaderV4] Closed module: ${module.name}`);
        }
    }

    /**
     * Show credential setup prompt to user
     * 
     * @param {Object} module - Module manifest
     */
    showCredentialPrompt(module) {
        const message = `
            <div class="credential-prompt">
                <h3>${module.name} Setup Required</h3>
                <p>This module requires credentials for:</p>
                <ul>
                    ${module.missing_required.map(p => `<li>${p}</li>`).join('')}
                </ul>
                <button onclick="window.moduleLoader.openCredentialSetup('${module.id}')">
                    Configure Credentials
                </button>
            </div>
        `;

        console.warn(`[ModuleLoaderV4] ${module.name} needs credential setup`);

        // Use native alert as fallback (can be replaced with custom notification system)
        alert(`${module.name} requires credential setup. Please configure: ${module.missing_required.join(', ')}`);
    }

    /**
     * Show setup notification badge for modules needing credentials
     * 
     * @param {number} count - Number of modules needing setup
     */
    showSetupNotification(count) {
        console.log(`[ModuleLoaderV4] ${count} modules need credential setup`);

        // Create notification badge on settings button
        const settingsButton = document.querySelector('.sidebar-icons [title="Settings"]') ||
            document.querySelector('[data-tab="settings"]');

        if (settingsButton && !settingsButton.querySelector('.badge')) {
            const badge = document.createElement('span');
            badge.className = 'badge notification-badge';
            badge.textContent = count;
            badge.style.cssText = `
                position: absolute;
                top: 5px;
                right: 5px;
                background: #ff4444;
                color: white;
                border-radius: 10px;
                padding: 2px 6px;
                font-size: 10px;
                font-weight: bold;
            `;
            settingsButton.style.position = 'relative';
            settingsButton.appendChild(badge);
        }
    }

    /**
     * Open credential setup interface
     * 
     * @param {string} moduleId - Module ID to configure
     */
    openCredentialSetup(moduleId) {
        console.log(`[ModuleLoaderV4] Opening credential setup for ${moduleId}`);

        // Switch to settings tab and navigate to credentials section
        if (typeof switchTab === 'function') {
            switchTab('settings');
        }

        // Highlight module in credentials list (if UI supports it)
        setTimeout(() => {
            const moduleCredentialRow = document.querySelector(`[data-module="${moduleId}"]`);
            if (moduleCredentialRow) {
                moduleCredentialRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
                moduleCredentialRow.classList.add('highlight');
                setTimeout(() => moduleCredentialRow.classList.remove('highlight'), 3000);
            }
        }, 500);
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // PUBLIC API
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Get module instance
     */
    getModule(moduleId) {
        return this.loadedModules.get(moduleId);
    }

    /**
     * Check if module is loaded
     */
    isModuleLoaded(moduleId) {
        return this.loadedModules.has(moduleId);
    }

    /**
     * Check if module is available for user
     */
    isModuleAvailable(moduleId) {
        const module = this.modules.get(moduleId);
        return module && module.available === true;
    }

    /**
     * Get module manifest
     */
    getModuleManifest(moduleId) {
        return this.modules.get(moduleId);
    }

    /**
     * Get all loaded modules
     */
    getLoadedModules() {
        return Array.from(this.loadedModules.keys());
    }

    /**
     * Get all available modules
     */
    getAvailableModules() {
        return Array.from(this.modules.values()).filter(m => m.available);
    }

    /**
     * Reload module (unload + load)
     */
    async reloadModule(moduleId, view = 'auto') {
        console.log(`[ModuleLoaderV4] Reloading ${moduleId}...`);
        await this.unloadModule(moduleId);
        await this.loadModule(moduleId, view);
    }

    /**
     * Unload module
     */
    async unloadModule(moduleId) {
        const loaded = this.loadedModules.get(moduleId);
        if (!loaded) {
            console.warn(`[ModuleLoaderV4] Module not loaded: ${moduleId}`);
            return;
        }

        console.log(`[ModuleLoaderV4] Unloading ${moduleId}...`);

        try {
            // Call onUnload lifecycle hook if exists
            if (loaded.type === 'modern' && loaded.module.onUnload) {
                await loaded.module.onUnload(loaded.utilities);
            }

            this.loadedModules.delete(moduleId);
            console.log(`[ModuleLoaderV4] ✅ ${moduleId} unloaded`);

        } catch (error) {
            console.error(`[ModuleLoaderV4] Failed to unload ${moduleId}:`, error);
            throw error;
        }
    }

    /**
     * Unload all modules
     */
    async unloadAllModules() {
        console.log(`[ModuleLoaderV4] Unloading all modules...`);
        const moduleIds = Array.from(this.loadedModules.keys());

        for (const moduleId of moduleIds) {
            await this.unloadModule(moduleId);
        }

        console.log(`[ModuleLoaderV4] ✅ All modules unloaded`);
    }

    /**
     * Get module loading statistics
     */
    getStats() {
        return {
            total: this.modules.size,
            available: Array.from(this.modules.values()).filter(m => m.available).length,
            loaded: this.loadedModules.size,
            modern: Array.from(this.loadedModules.values()).filter(m => m.type === 'modern').length,
            legacy: Array.from(this.loadedModules.values()).filter(m => m.type === 'legacy').length
        };
    }

    /**
     * Enable debug mode
     */
    enableDebug() {
        localStorage.setItem('module-loader-debug', 'true');
        console.log('[ModuleLoaderV4] Debug mode enabled');
    }

    /**
     * Disable debug mode
     */
    disableDebug() {
        localStorage.removeItem('module-loader-debug');
        console.log('[ModuleLoaderV4] Debug mode disabled');
    }

    /**
     * Check if debug mode enabled
     */
    isDebugEnabled() {
        return localStorage.getItem('module-loader-debug') === 'true';
    }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// EXPORT SINGLETON
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
const moduleLoader = new ModuleLoaderV4();
export default moduleLoader;
