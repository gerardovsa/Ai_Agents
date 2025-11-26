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

            // Generate floating toggle buttons (method is called generateFloatingToggles)
            this.generateFloatingToggles();

            // Generate main tab containers
            this.generateMainTabs();

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
            console.log(`[ModuleLoader] Available module IDs:`, data.modules.map(m => m.id));

            // Update module status
            for (const availableModule of data.modules) {
                const module = this.modules.get(availableModule.id);
                if (module) {
                    module.available = true;
                    module.has_optional = availableModule.has_optional;
                    module.available_optional = availableModule.available_optional;
                    console.log(`[ModuleLoader] Marked ${availableModule.id} as available`);
                } else {
                    console.warn(`[ModuleLoader] Module ${availableModule.id} from API not found in local registry`);
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

        // Generate button for each available module
        let availableCount = 0;

        console.log(`[ModuleLoader] Total modules in registry: ${this.modules.size}`);
        console.log(`[ModuleLoader] Modules:`, Array.from(this.modules.keys()));

        for (const [moduleId, module] of this.modules) {
            console.log(`[ModuleLoader] Checking module ${moduleId}: available=${module.available}`);
            
            if (!module.available) {
                console.log(`[ModuleLoader] Skipping unavailable module: ${moduleId}`);
                continue;
            }

            const button = document.createElement('button');
            button.className = 'sidebar-icon-btn';
            button.title = module.name;
            button.dataset.moduleId = moduleId;
            button.dataset.tab = moduleId;

            // Create icon element
            const icon = document.createElement('i');
            // Handle both formats: "fa-industry" and "fas fa-industry"
            if (module.icon.includes(' ')) {
                // Already has prefix (e.g., "fas fa-industry")
                icon.className = module.icon;
            } else {
                // Just icon name (e.g., "fa-industry"), add fas prefix
                icon.className = `fas ${module.icon}`;
            }
            if (module.color) {
                icon.style.color = module.color;
            }
            button.appendChild(icon);

            // Click handler - switch to main tab if module has main_tab, else toggle sidebar
            button.addEventListener('click', async () => {
                if (module.main_tab) {
                    // Load module first if not loaded
                    if (!this.loadedModules.has(moduleId)) {
                        console.log(`[ModuleLoader] Loading module ${moduleId} before switching to main tab...`);
                        const loaded = await this.loadModule(moduleId);
                        if (!loaded) {
                            console.error(`[ModuleLoader] Failed to load module ${moduleId}`);
                            return;
                        }
                    }
                    
                    // Switch to main tab
                    const tabId = module.main_tab_id || moduleId;
                    console.log(`[ModuleLoader] Switching to main tab: ${tabId}`);
                    
                    if (typeof switchTab === 'function') {
                        switchTab(tabId);
                    } else {
                        console.error('[ModuleLoader] switchTab function not found');
                    }
                    
                    // Update sidebar active state
                    document.querySelectorAll('.sidebar-icon-btn').forEach(b => b.classList.remove('active'));
                    button.classList.add('active');
                } else {
                    // Toggle sidebar
                    this.toggleModule(moduleId);
                }
            });

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

        // Generate floating toggle buttons and main tabs
        this.generateFloatingToggles();
        this.generateMainTabs();
    }

    /**
     * Generate floating toggle buttons for modules that request them
     */
    generateFloatingToggles() {
        console.log('[ModuleLoader] Generating floating toggle buttons...');

        for (const [moduleId, module] of this.modules) {
            if (!module.available || !module.floating_toggle) {
                continue;
            }

            // Check if button already exists
            if (document.getElementById(`${moduleId}-floating-toggle`)) {
                console.log(`[ModuleLoader] Floating toggle for ${moduleId} already exists`);
                continue;
            }

            // Create floating toggle button
            const toggle = document.createElement('button');
            toggle.id = `${moduleId}-floating-toggle`;
            toggle.className = 'module-floating-toggle';
            toggle.title = `${module.name} (Drag to reposition)`;
            toggle.dataset.moduleId = moduleId;

            // Set colors
            toggle.style.background = module.color || '#00509E';

            // Create icon
            const icon = document.createElement('i');
            if (module.icon.includes(' ')) {
                icon.className = module.icon;
            } else {
                icon.className = `fas ${module.icon}`;
            }
            toggle.appendChild(icon);

            // Add to DOM (after other toggle buttons)
            const platformContainer = document.querySelector('.platform-container');
            if (platformContainer) {
                platformContainer.appendChild(toggle);
            } else {
                document.body.appendChild(toggle);
            }

            // Initialize draggable and click behavior
            this.initializeFloatingToggle(toggle, module);

            console.log(`[ModuleLoader] Created floating toggle for ${module.name}`);
        }
    }

    /**
     * Initialize floating toggle button with drag and click
     */
    initializeFloatingToggle(toggle, module) {
        const moduleId = module.id;
        let userHasDragged = false;
        let isDragging = false;
        let hasMoved = false;
        let offsetY = 0;

        // Position toggle
        function positionToggle() {
            const savedTop = localStorage.getItem(`${moduleId}-toggle-top`);
            if (savedTop && savedTop !== 'null') {
                toggle.style.top = savedTop;
                userHasDragged = true;
            } else {
                // Default position from manifest or fallback
                const defaultTop = module.floating_toggle_default_top || 280;
                toggle.style.top = `${defaultTop}px`;
            }

            // Position based on manifest preference
            const side = module.floating_toggle_position || 'right';
            if (side === 'right') {
                toggle.style.right = '60px';
                toggle.style.left = 'auto';
                toggle.style.borderRadius = '12px 0 0 12px';
            } else {
                toggle.style.left = '60px';
                toggle.style.right = 'auto';
                toggle.style.borderRadius = '0 12px 12px 0';
            }
        }

        positionToggle();

        // Mousedown - start potential drag
        toggle.addEventListener('mousedown', (e) => {
            isDragging = true;
            hasMoved = false;
            offsetY = e.clientY - toggle.getBoundingClientRect().top;
            toggle.style.cursor = 'grabbing';
            toggle.classList.add('dragging');
            e.preventDefault();
        });

        // Mousemove - drag
        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                hasMoved = true;
                const newTop = e.clientY - offsetY;
                toggle.style.top = `${newTop}px`;
            }
        });

        // Mouseup - end drag or execute click
        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                toggle.style.cursor = 'grab';
                toggle.classList.remove('dragging');

                if (!hasMoved) {
                    // Click - switch to main tab if available, else toggle sidebar
                    if (module.main_tab) {
                        // Switch to main tab
                        if (typeof switchTab === 'function') {
                            switchTab(module.main_tab_id || moduleId);
                            // Update sidebar active state
                            document.querySelectorAll('.sidebar-icon-btn').forEach(b => b.classList.remove('active'));
                            document.querySelector(`.sidebar-icon-btn[data-tab="${module.main_tab_id || moduleId}"]`)?.classList.add('active');
                        }
                    } else {
                        // Toggle sidebar
                        this.toggleModule(moduleId);
                    }
                } else {
                    // Dragged - save position
                    userHasDragged = true;
                    localStorage.setItem(`${moduleId}-toggle-top`, toggle.style.top);
                }

                hasMoved = false;
            }
        });
    }

    /**
     * Generate main tab containers for modules that request them
     */
    generateMainTabs() {
        console.log('[ModuleLoader] Generating main tab containers...');

        const mainContent = document.querySelector('.main-content');
        if (!mainContent) {
            console.warn('[ModuleLoader] Main content area not found');
            return;
        }

        for (const [moduleId, module] of this.modules) {
            if (!module.available || !module.main_tab) {
                continue;
            }

            const tabId = module.main_tab_id || moduleId;

            // Check if tab already exists
            if (document.getElementById(`tab-${tabId}`)) {
                console.log(`[ModuleLoader] Main tab for ${moduleId} already exists`);
                continue;
            }

            // Create main tab container
            const tabContainer = document.createElement('div');
            tabContainer.id = `tab-${tabId}`;
            tabContainer.className = 'tab-content';

            // Create full Kanban board structure for inhouse-kanban
            if (moduleId === 'inhouse-kanban') {
                tabContainer.innerHTML = `
                    <div id="${moduleId}-main-container" class="active" style="height: 100%; display: flex; flex-direction: column; background: #0B0E13;">
                        <!-- Filters Bar -->
                        <div class="filters-bar">
                            <div class="filter-group">
                                <label><i class="fas fa-clock"></i> Timeframe</label>
                                <select id="timeframe-selector" class="form-control form-control-sm">
                                    <option value="1">Last Month</option>
                                    <option value="3">Last 3 Months</option>
                                    <option value="6" selected>Last 6 Months</option>
                                    <option value="12">Last Year</option>
                                    <option value="0">All Time</option>
                                </select>
                            </div>
                            <div class="filter-group">
                                <label><i class="fas fa-filter"></i> Priority</label>
                                <select id="priority-selector" class="form-control form-control-sm">
                                    <option value="all">All</option>
                                    <option value="high">High</option>
                                    <option value="medium">Medium</option>
                                    <option value="low">Low</option>
                                </select>
                            </div>
                            <div class="filter-group">
                                <label><i class="fas fa-search"></i> Search</label>
                                <input type="text" id="search-input" class="form-control form-control-sm" placeholder="Search jobs...">
                            </div>
                            <div class="filter-group">
                                <label><i class="fas fa-briefcase"></i> Workboard</label>
                                <div id="workboard-selector"></div>
                            </div>
                            <button id="inhouse-refresh-btn" class="btn btn-sm btn-primary">
                                <i class="fas fa-sync-alt"></i> Refresh
                            </button>
                        </div>
                        
                        <!-- Metrics Dashboard -->
                        <div id="kanban-metrics"></div>
                        
                        <!-- Kanban Board -->
                        <div id="kanban-board" style="flex: 1; overflow-x: auto; overflow-y: hidden; padding: 20px;"></div>
                    </div>
                `;
            } else {
                // Default loading state for other modules
                tabContainer.innerHTML = `
                    <div id="${moduleId}-main-container" class="active" style="height: 100%; overflow: auto;">
                        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: #9CA3AF;">
                            <i class="${module.icon.includes(' ') ? module.icon : 'fas ' + module.icon}" style="font-size: 3rem; color: ${module.color}; margin-bottom: 16px;"></i>
                            <p style="font-size: 16px; font-weight: 600;">Loading ${module.name}...</p>
                        </div>
                    </div>
                `;
            }

            // Insert before the last tab (or at the end)
            mainContent.appendChild(tabContainer);

            console.log(`[ModuleLoader] Created main tab for ${module.name}`);
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
            // Determine HTML path - try htmlPath from manifest first, then external/modules, then backend API
            let htmlPath = module.htmlPath || (module.html_file ? `external/modules/${moduleId}/${module.html_file}` : null);
            
            // Try external/modules path first (for external modules) - only if path is defined
            let htmlResponse = htmlPath ? await fetch(htmlPath) : null;
            
            // Fallback to backend API if external path fails or wasn't attempted
            if (!htmlResponse || !htmlResponse.ok) {
                if (htmlPath) {
                    console.log(`[ModuleLoader] External path failed, trying backend API for ${moduleId}`);
                }
                htmlResponse = await fetch(`/api/modules/${moduleId}/html`);
            }
            
            if (!htmlResponse.ok) {
                throw new Error(`Failed to load HTML for ${moduleId}: ${htmlResponse.status}`);
            }
            
            const html = await htmlResponse.text();

            // Inject HTML into DOM
            const tempContainer = document.createElement('div');
            tempContainer.innerHTML = html;
            document.body.appendChild(tempContainer.firstElementChild);

            console.log(`[ModuleLoader] Injected HTML for ${moduleId}`);

            // Load CSS via Flask API route
            if ((module.css_file || module.stylePath) && !document.querySelector(`link[data-module="${moduleId}"]`)) {
                const link = document.createElement('link');
                link.rel = 'stylesheet';
                link.dataset.module = moduleId;
                
                // Try Flask API route first, fallback to direct path
                link.href = `/api/modules/${moduleId}/css`;
                
                // Add error handler to try fallback path
                link.onerror = () => {
                    console.warn(`[ModuleLoader] Flask CSS route failed, trying direct path for ${moduleId}`);
                    link.href = module.stylePath || `external/modules/${moduleId}/${module.css_file}`;
                };
                
                document.head.appendChild(link);
                console.log(`[ModuleLoader] Loaded CSS for ${moduleId} via Flask route`);
            }

            // Load JS via Flask API route
            if ((module.js_file || module.scriptPath) && !document.querySelector(`script[data-module="${moduleId}"]`)) {
                await new Promise((resolve, reject) => {
                    const script = document.createElement('script');
                    script.dataset.module = moduleId;
                    
                    // Try Flask API route first
                    script.src = `/api/modules/${moduleId}/js`;
                    
                    script.onload = () => {
                        console.log(`[ModuleLoader] ✅ Loaded JS for ${moduleId} via Flask route`);
                        resolve();
                    };
                    
                    script.onerror = () => {
                        console.warn(`[ModuleLoader] Flask JS route failed, trying direct path for ${moduleId}`);
                        // Try fallback path
                        script.src = module.scriptPath || `external/modules/${moduleId}/${module.js_file}`;
                        
                        script.onerror = () => {
                            console.error(`[ModuleLoader] ❌ Failed to load JS for ${moduleId} from all paths`);
                            reject(new Error(`Failed to load JS for ${moduleId}`));
                        };
                    };
                    
                    document.body.appendChild(script);
                });
            }

            // Mark as loaded
            this.loadedModules.add(moduleId);

            // Initialize module if it has an init function
            await this.initializeModule(moduleId);

            console.log(`[ModuleLoader] Successfully loaded module: ${module.name}`);
            return true;

        } catch (error) {
            console.error(`[ModuleLoader] Failed to load module ${moduleId}:`, error);
            return false;
        }
    }

    /**
     * Initialize module after HTML and JS are loaded
     * 
     * @param {string} moduleId - Module ID to initialize
     */
    async initializeModule(moduleId) {
        console.log(`[ModuleLoader] Initializing module: ${moduleId}`);

        // Check if module has initialization in window.ModuleRegistry
        if (window.ModuleRegistry && window.ModuleRegistry[moduleId]) {
            if (typeof window.ModuleRegistry[moduleId].init === 'function') {
                try {
                    await window.ModuleRegistry[moduleId].init();
                    console.log(`[ModuleLoader] ✅ Module ${moduleId} initialized successfully`);
                } catch (error) {
                    console.error(`[ModuleLoader] ❌ Failed to initialize ${moduleId}:`, error);
                }
            }
        } else {
            console.log(`[ModuleLoader] No initialization function found for ${moduleId}`);
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
 * Initialize module system (wrapper for moduleLoader.initialize)
 * 
 * @param {boolean} forceReload - Force reload all modules
 */
window.initializeModuleSystem = async function(forceReload = false) {
    console.log('[ModuleSystem] initializeModuleSystem called (forceReload:', forceReload, ')');
    
    // Get user ID from session (assumes window.currentUserId is set)
    const userId = window.currentUserId || window.userProfile?.id || 14; // Default to user 14 for InHouse
    
    if (!userId) {
        console.error('[ModuleSystem] No user ID available - cannot initialize modules');
        return;
    }
    
    console.log(`[ModuleSystem] Initializing modules for user ${userId}`);
    
    try {
        await window.moduleLoader.initialize(userId);
        console.log('✅ [ModuleSystem] Module system initialized successfully');
    } catch (error) {
        console.error('❌ [ModuleSystem] Failed to initialize module system:', error);
    }
};

/**
 * Initialize module loader on page load
 * 
 * Usage in business-ai-platform-v2.html:
 * 
 * <script src="modules/module_loader.js"></script>
 * <script>
 *   document.addEventListener('DOMContentLoaded', async () => {
 *     await window.initializeModuleSystem();
 *   });
 * </script>
 */
