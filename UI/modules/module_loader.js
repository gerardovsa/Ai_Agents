/**
 * FILE: frontend/modules/module_loader.js
 * PURPOSE: Automatic module discovery and loading system
 * 
 * ARCHITECTURE:
 * - Fetches module list from ModuleRegistry API
 * - Checks user credentials for each module
 * - Dynamically loads HTML/CSS/JS for available modules
 * - Auto-generates sidebar buttons for enabled modules
 * - Lazy-loads modules on-demand (not all at startup)
 * 
 * PATTERN: Similar to tool registry - modules self-register
 * 
 * DEPENDENCIES:
 * - /api/modules/list (get all modules)
 * - /api/modules/available (get modules user can access)
 * - /api/modules/<id>/html (load module HTML)
 * - /api/modules/<id>/credentials-status (check credentials)
 * 
 * EXPORTS:
 * - ModuleLoader (singleton) - Load and manage modules
 * - loadAllModules() - Initialize all available modules
 * - loadModule(moduleId) - Load specific module
 * - toggleModule(moduleId) - Show/hide module sidebar
 * 
 * USED BY:
 * - frontend/business-ai-platform-v2.html (main UI initialization)
 * 
 * NOTES:
 * - Modules cached after first load (performance)
 * - Credential checks cached for 5 minutes
 * - Module HTML injected into DOM on-demand
 * - Sidebar buttons auto-generated from module manifests
 * 
 * LAST MODIFIED: 2025-11-25 - Initial module loader implementation
 */

class ModuleLoader {
    constructor() {
        if (ModuleLoader.instance) {
            return ModuleLoader.instance;
        }

        this.modules = new Map(); // moduleId → module manifest
        this.loadedModules = new Set(); // moduleIds that are loaded in DOM
        this.activeModule = null; // Currently open module
        this.credentialCache = new Map(); // moduleId → {status, timestamp}
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes

        ModuleLoader.instance = this;
    }

    /**
     * Initialize module loader and fetch module list
     * 
     * Process:
     * 1. Fetch all registered modules from API
     * 2. Check which modules user has credentials for
     * 3. Generate sidebar buttons for available modules
     * 4. Load auto-load modules
     */
    async initialize(userId) {
        console.log('[ModuleLoader] Initializing...');
        this.userId = userId;

        try {
            // Fetch all registered modules
            const response = await fetch('/api/modules/list');
            const data = await response.json();

            if (!data.modules) {
                console.error('[ModuleLoader] No modules returned from API');
                return;
            }

            console.log(`[ModuleLoader] Found ${data.count} registered modules`);

            // Store module manifests
            for (const module of data.modules) {
                this.modules.set(module.id, module);
                console.log(`[ModuleLoader] Registered module: ${module.id}`);
            }

            // Check which modules user can access
            await this.checkModuleAvailability();

            // Generate sidebar buttons
            await this.generateSidebarButtons();

            // Load auto-load modules
            await this.loadAutoLoadModules();

            console.log('[ModuleLoader] Initialization complete');

        } catch (error) {
            console.error('[ModuleLoader] Initialization failed:', error);
        }
    }

    /**
     * Check which modules user has credentials for
     */
    async checkModuleAvailability() {
        console.log('[ModuleLoader] Checking module availability...');

        try {
            const response = await fetch(`/api/modules/available?user_id=${this.userId}`);
            const data = await response.json();

            if (!data.modules) {
                console.warn('[ModuleLoader] No available modules');
                return;
            }

            console.log(`[ModuleLoader] User has access to ${data.count} modules`);

            // Update module status
            for (const availableModule of data.modules) {
                const module = this.modules.get(availableModule.id);
                if (module) {
                    module.available = true;
                    module.has_optional = availableModule.has_optional;
                    module.available_optional = availableModule.available_optional;
                }
            }

            // Check which modules need setup
            const needsSetupResponse = await fetch(`/api/modules/needs-setup?user_id=${this.userId}`);

            if (!needsSetupResponse.ok) {
                console.warn(`[ModuleLoader] needs-setup endpoint returned ${needsSetupResponse.status}`);
                return; // Skip setup check if endpoint fails
            }

            const needsSetupData = await needsSetupResponse.json();

            if (needsSetupData.modules && needsSetupData.count > 0) {
                console.log(`[ModuleLoader] ${needsSetupData.count} modules need credential setup`);

                for (const module of needsSetupData.modules) {
                    const moduleManifest = this.modules.get(module.id);
                    if (moduleManifest) {
                        moduleManifest.available = false;
                        moduleManifest.missing_required = module.missing_required;
                    }
                }
            }

        } catch (error) {
            console.error('[ModuleLoader] Failed to check availability:', error);
        }
    }

    /**
     * Generate sidebar buttons for available modules
     * 
     * Creates buttons in sidebar navigation automatically
     */
    async generateSidebarButtons(retryCount = 0) {
        const MAX_RETRIES = 5;

        console.log('[ModuleLoader] Generating sidebar buttons...');

        // Look for the sidebar modules section first (preferred), then fallback to main sidebar
        let sidebar = document.getElementById('sidebarModulesSection') || document.querySelector('.sidebar');

        if (!sidebar) {
            if (retryCount >= MAX_RETRIES) {
                console.error('[ModuleLoader] Sidebar container not found after', MAX_RETRIES, 'attempts - giving up');
                console.error('[ModuleLoader] Module buttons will NOT be available');
                return;
            }

            console.warn(`[ModuleLoader] Sidebar container not found - retry ${retryCount + 1}/${MAX_RETRIES}`);

            // Try again after a delay (DOM may still be loading)
            setTimeout(() => this.generateSidebarButtons(retryCount + 1), 1000);
            return;
        }

        console.log('[ModuleLoader] Found sidebar container:', sidebar.id || sidebar.className);

        // If we found the modules section, use it directly
        // Otherwise create a module buttons container
        let moduleButtonsContainer;

        if (sidebar.id === 'sidebarModulesSection') {
            // Use the modules section directly
            moduleButtonsContainer = sidebar;
        } else {
            // Create module buttons container inside main sidebar
            moduleButtonsContainer = document.getElementById('module-buttons-container');

            if (!moduleButtonsContainer) {
                moduleButtonsContainer = document.createElement('div');
                moduleButtonsContainer.id = 'module-buttons-container';
                moduleButtonsContainer.className = 'module-buttons-section';

                // Insert before settings button (usually last)
                const settingsButton = sidebar.querySelector('[title="Settings"]');
                if (settingsButton) {
                    sidebar.insertBefore(moduleButtonsContainer, settingsButton);
                } else {
                    sidebar.appendChild(moduleButtonsContainer);
                }
            }
        }

        // Clear existing module buttons
        moduleButtonsContainer.innerHTML = '';

        // Add separator
        const separator = document.createElement('div');
        separator.className = 'sidebar-separator';
        separator.innerHTML = '<span>Modules</span>';
        moduleButtonsContainer.appendChild(separator);

        // Generate button for each available module
        let availableCount = 0;

        for (const [moduleId, module] of this.modules) {
            if (!module.available) {
                continue;
            }

            const button = document.createElement('button');
            button.className = 'sidebar-icon';
            button.title = module.name;
            button.dataset.moduleId = moduleId;
            button.style.color = module.color;

            button.innerHTML = `<i class="fas ${module.icon}"></i>`;

            // Click handler to toggle module
            button.addEventListener('click', () => this.toggleModule(moduleId));

            moduleButtonsContainer.appendChild(button);
            availableCount++;

            console.log(`[ModuleLoader] Added button for module: ${module.name}`);
        }

        console.log(`[ModuleLoader] Generated ${availableCount} sidebar buttons`);

        // Show setup notification if modules need credentials
        const needsSetupCount = Array.from(this.modules.values())
            .filter(m => m.available === false && m.missing_required)
            .length;

        if (needsSetupCount > 0) {
            this.showSetupNotification(needsSetupCount);
        }
    }

    /**
     * Load auto-load modules
     */
    async loadAutoLoadModules() {
        console.log('[ModuleLoader] Loading auto-load modules...');

        for (const [moduleId, module] of this.modules) {
            if (module.auto_load && module.available) {
                console.log(`[ModuleLoader] Auto-loading module: ${module.name}`);
                await this.loadModule(moduleId);
            }
        }
    }

    /**
     * Load specific module (inject HTML/CSS/JS)
     * 
     * @param {string} moduleId - Module ID to load
     * @returns {Promise<boolean>} Success status
     */
    async loadModule(moduleId) {
        console.log(`[ModuleLoader] Loading module: ${moduleId}`);

        // Check if already loaded
        if (this.loadedModules.has(moduleId)) {
            console.log(`[ModuleLoader] Module ${moduleId} already loaded`);
            return true;
        }

        const module = this.modules.get(moduleId);

        if (!module) {
            console.error(`[ModuleLoader] Module ${moduleId} not found`);
            return false;
        }

        if (!module.available) {
            console.warn(`[ModuleLoader] Module ${moduleId} not available (missing credentials)`);
            this.showCredentialPrompt(module);
            return false;
        }

        try {
            // Load HTML
            const htmlResponse = await fetch(`/api/modules/${moduleId}/html`);
            const html = await htmlResponse.text();

            // Inject HTML into DOM
            const tempContainer = document.createElement('div');
            tempContainer.innerHTML = html;
            document.body.appendChild(tempContainer.firstElementChild);

            console.log(`[ModuleLoader] Injected HTML for ${moduleId}`);

            // Load CSS (if not already loaded)
            if (module.css_file && !document.querySelector(`link[href*="${module.css_file}"]`)) {
                const link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = `/modules/${moduleId}/${module.css_file}`;
                document.head.appendChild(link);

                console.log(`[ModuleLoader] Loaded CSS for ${moduleId}`);
            }

            // Load JS (if not already loaded)
            if (module.js_file && !document.querySelector(`script[src*="${module.js_file}"]`)) {
                await new Promise((resolve, reject) => {
                    const script = document.createElement('script');
                    script.src = `/modules/${moduleId}/${module.js_file}`;
                    script.onload = resolve;
                    script.onerror = reject;
                    document.body.appendChild(script);
                });

                console.log(`[ModuleLoader] Loaded JS for ${moduleId}`);
            }

            // Mark as loaded
            this.loadedModules.add(moduleId);

            console.log(`[ModuleLoader] Successfully loaded module: ${module.name}`);
            return true;

        } catch (error) {
            console.error(`[ModuleLoader] Failed to load module ${moduleId}:`, error);
            return false;
        }
    }

    /**
     * Toggle module sidebar visibility
     * 
     * @param {string} moduleId - Module ID to toggle
     */
    async toggleModule(moduleId) {
        console.log(`[ModuleLoader] Toggling module: ${moduleId}`);

        // Load module if not loaded
        if (!this.loadedModules.has(moduleId)) {
            const loaded = await this.loadModule(moduleId);
            if (!loaded) {
                return;
            }
        }

        const module = this.modules.get(moduleId);
        const sidebarElement = document.getElementById(`${moduleId}-sidebar`);

        if (!sidebarElement) {
            console.error(`[ModuleLoader] Sidebar element not found for ${moduleId}`);
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
            console.log(`[ModuleLoader] Opened module: ${module.name}`);

            // Initialize module controller (if exists)
            const controllerName = `${moduleId.replace(/_/g, '')}Controller`;
            if (window[controllerName]) {
                if (!window[controllerName].initialized) {
                    await window[controllerName].init();
                    window[controllerName].initialized = true;
                }
            }
        } else {
            this.activeModule = null;
            console.log(`[ModuleLoader] Closed module: ${module.name}`);
        }
    }

    /**
     * Show credential setup prompt
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

        // Show notification (use your notification system)
        console.warn(`[ModuleLoader] ${module.name} needs credential setup`);
        alert(`${module.name} requires credential setup. Please configure: ${module.missing_required.join(', ')}`);
    }

    /**
     * Show setup notification for modules needing credentials
     * 
     * @param {number} count - Number of modules needing setup
     */
    showSetupNotification(count) {
        console.log(`[ModuleLoader] ${count} modules need credential setup`);

        // Create notification badge on settings button
        const settingsButton = document.querySelector('.sidebar-icons [title="Settings"]');

        if (settingsButton && !settingsButton.querySelector('.badge')) {
            const badge = document.createElement('span');
            badge.className = 'badge notification-badge';
            badge.textContent = count;
            badge.style.cssText = `
                position: absolute;
                top: 5px;
                right: 5px;
                background: #ef4444;
                color: white;
                border-radius: 50%;
                width: 18px;
                height: 18px;
                font-size: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
            `;
            settingsButton.style.position = 'relative';
            settingsButton.appendChild(badge);
        }
    }

    /**
     * Open credential setup for module
     * 
     * @param {string} moduleId - Module ID
     */
    async openCredentialSetup(moduleId) {
        console.log(`[ModuleLoader] Opening credential setup for: ${moduleId}`);

        // Check credential status and get form definitions
        const response = await fetch(`/api/modules/${moduleId}/credentials-status?user_id=${this.userId}`);
        const data = await response.json();

        if (!data.credential_forms) {
            console.error('[ModuleLoader] No credential forms defined');
            return;
        }

        // Open settings sidebar with credential forms
        // TODO: Integrate with your settings system
        console.log('[ModuleLoader] Credential forms:', data.credential_forms);
    }
}

// Create singleton instance
window.moduleLoader = new ModuleLoader();

/**
 * Initialize module loader on page load
 * 
 * Usage in business-ai-platform-v2.html:
 * 
 * <script src="modules/module_loader.js"></script>
 * <script>
 *   document.addEventListener('DOMContentLoaded', async () => {
 *     const userId = 1; // Get from session
 *     await window.moduleLoader.initialize(userId);
 *   });
 * </script>
 */
