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

        // 🔒 CRITICAL: Prevent duplicate initialization (root cause of instability)
        this.initialized = false;
        this.initializing = false;

        ModuleLoader.instance = this;
    }

    /**
     * Create a minimal UI container for a module when HTML fetch fails.
     * This provides a sidebar element and basic header/content so modules
     * that expect DOM nodes can initialize even when external assets are unavailable.
     *
     * @param {string} moduleId
     * @param {object} module
     */
    _createModuleUIFromJS(moduleId, module) {
        const sidebarId = `${moduleId}-sidebar`;

        if (document.getElementById(sidebarId)) {
            return; // already created
        }

        const sidebar = document.createElement('div');
        sidebar.id = sidebarId;
        sidebar.className = 'module-sidebar';

        // Header
        const header = document.createElement('div');
        header.className = 'module-sidebar-header';
        const title = document.createElement('h3');
        title.textContent = module.name || moduleId;
        const closeBtn = document.createElement('button');
        closeBtn.className = 'close-module-btn';
        closeBtn.textContent = '✕';
        closeBtn.onclick = () => sidebar.classList.remove('active');
        header.appendChild(title);
        header.appendChild(closeBtn);

        // Content
        const content = document.createElement('div');
        content.className = 'module-sidebar-content';
        content.innerHTML = `<div class="module-placeholder">No HTML available for <strong>${moduleId}</strong>. This is a fallback UI.</div>`;

        sidebar.appendChild(header);
        sidebar.appendChild(content);

        // Append to body
        document.body.appendChild(sidebar);
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
        console.log('🔵 [ModuleLoader.initialize] FUNCTION CALLED with userId:', userId);

        // 🔒 CRITICAL: Prevent duplicate initialization
        if (this.initialized) {
            console.warn('[ModuleLoader.initialize] ⚠️ Already initialized, skipping duplicate call');
            return;
        }

        if (this.initializing) {
            console.warn('[ModuleLoader.initialize] ⚠️ Initialization already in progress, skipping duplicate call');
            return;
        }

        this.initializing = true;
        console.log('[ModuleLoader.initialize] 🚀 Starting initialization...');
        this.userId = userId;

        try {
            // Fetch all registered modules
            const response = await fetch('/api/modules/list');
            const data = await response.json();

            if (!data.modules) {
                console.error('[ModuleLoader] No modules returned from API');
                this.initializing = false;
                return;
            }

            console.log(`[ModuleLoader] Found ${data.count} registered modules`);

            // Store module manifests (filter out disabled modules)
            for (const module of data.modules) {
                // Check if module is explicitly disabled
                if (module.enabled === false) {
                    console.log(`[ModuleLoader] Skipping disabled module: ${module.id}`);
                    continue;
                }

                // Mark modules without credential requirements as always available
                if (module.credentials_required === false) {
                    module.available = true;
                    console.log(`[ModuleLoader] Module ${module.id} marked as available (no credentials required)`);
                }

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

            this.initialized = true;
            this.initializing = false;
            console.log('[ModuleLoader] ✅ Initialization complete');

        } catch (error) {
            console.error('[ModuleLoader] Initialization failed:', error);
            this.initializing = false;
            this.initialized = false;
        }
    }

    /**
     * Check which modules user has credentials for
     */
    async checkModuleAvailability() {
        console.log('🔵 [ModuleLoader.checkModuleAvailability] FUNCTION CALLED');
        console.log('[ModuleLoader.checkModuleAvailability] Checking module availability for userId:', this.userId);

        try {
            console.log('[ModuleLoader.checkModuleAvailability] → Fetching /api/modules/available?user_id=' + this.userId);
            const response = await fetch(`/api/modules/available?user_id=${this.userId}`);
            const data = await response.json();
            console.log('[ModuleLoader.checkModuleAvailability] ✅ API response received:', data);

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
        console.log('🔵 [ModuleLoader.generateSidebarButtons] FUNCTION CALLED (retry:', retryCount, ')');
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

            // Skip components (they don't get sidebar buttons)
            if (module.module_type === 'component' || module.is_component === true) {
                console.log(`[ModuleLoader] Skipping component (no sidebar button): ${moduleId}`);
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
                        console.log(`[ModuleLoader] 🎯 Loading module ${moduleId} for MAIN TAB (JS only, no HTML sidebar)...`);
                        const loaded = await this.loadModule(moduleId, { skipHtml: true, source: 'main-tab-button' });
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
        console.log('🔵 [ModuleLoader.generateFloatingToggles] FUNCTION CALLED');
        console.log('[ModuleLoader] Generating floating toggle buttons...');

        for (const [moduleId, module] of this.modules) {
            // Skip components (they don't get floating toggles)
            if (module.module_type === 'component' || module.is_component === true) {
                continue;
            }

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

            // Register with Universal Sidebar Framework if available
            if (window.SidebarManager && module.sidebar && module.sidebar.enabled) {
                this.registerModuleSidebarWithFramework(moduleId, module);
            }

            console.log(`[ModuleLoader] Created floating toggle for ${module.name}`);
        }
    }

    /**
     * Register module sidebar with Universal Sidebar Framework
     * AUTO-INTEGRATION: Called when module has sidebar configuration
     * 
     * @param {string} moduleId - Module ID
     * @param {object} module - Module manifest
     */
    registerModuleSidebarWithFramework(moduleId, module) {
        if (!window.SidebarManager) {
            console.warn('[ModuleLoader] SidebarManager not available');
            return;
        }

        const sidebarConfig = module.sidebar || {};
        const toggleButtonId = `${moduleId}-floating-toggle`;

        // Build registration config from manifest
        const config = {
            id: `${moduleId}-sidebar`,
            side: sidebarConfig.position || sidebarConfig.side || 'left',
            toggleButtonId: toggleButtonId,
            width: sidebarConfig.width ? `${sidebarConfig.width}px` : '450px',
            icon: module.icon || 'fa-cube',
            title: module.name,
            onInit: async () => {
                console.log(`[${moduleId.toUpperCase()}] First open - initializing via framework...`);

                // Initialize module controller (if exists)
                const controllerName = `${moduleId.replace(/-/g, '')}Controller`;
                if (window[controllerName]) {
                    if (typeof window[controllerName].init === 'function' && !window[controllerName].initialized) {
                        await window[controllerName].init();
                        window[controllerName].initialized = true;
                    }
                }
            },
            onOpen: () => {
                console.log(`[${moduleId.toUpperCase()}] Sidebar opened via framework`);
                this.activeModule = moduleId;
            },
            onClose: () => {
                console.log(`[${moduleId.toUpperCase()}] Sidebar closed via framework`);
                if (this.activeModule === moduleId) {
                    this.activeModule = null;
                }
            }
        };

        // Register with framework
        window.SidebarManager.register(config);
        console.log(`[ModuleLoader] ✅ Registered ${moduleId} with Universal Sidebar Framework`);
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
        let lastClickTime = 0;
        let currentSide = localStorage.getItem(`${moduleId}-toggle-side`) || module.floating_toggle_position || 'left';

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

            // Position based on current side (60px from edge, matching Synergy toggle)
            if (currentSide === 'right') {
                toggle.style.right = '60px';
                toggle.style.left = 'auto';
                toggle.dataset.side = 'right';
            } else {
                toggle.style.left = '60px';
                toggle.style.right = 'auto';
                toggle.dataset.side = 'left';
            }

            // Update sidebar position if it exists
            updateSidebarPosition();
        }

        // Update sidebar to match toggle side
        function updateSidebarPosition() {
            const sidebar = document.getElementById(`${moduleId}-sidebar`);
            if (!sidebar) return;

            sidebar.dataset.side = currentSide;
            sidebar.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';

            if (currentSide === 'right') {
                sidebar.style.left = 'auto';
                sidebar.style.right = '60px';  // 60px from right edge
                sidebar.style.borderLeft = '1px solid var(--border-default)';
                sidebar.style.borderRight = 'none';
                sidebar.style.boxShadow = '-4px 0 24px rgba(0, 0, 0, 0.3)';
                if (!sidebar.classList.contains('active')) {
                    sidebar.style.transform = 'translateX(calc(100% + 60px))';  // Hidden beyond right edge
                }
            } else {
                sidebar.style.left = '60px';  // 60px from left edge (clear of main sidebar)
                sidebar.style.right = 'auto';
                sidebar.style.borderRight = '1px solid var(--border-default)';
                sidebar.style.borderLeft = 'none';
                sidebar.style.boxShadow = '4px 0 24px rgba(0, 0, 0, 0.3)';
                if (!sidebar.classList.contains('active')) {
                    sidebar.style.transform = 'translateX(calc(-100% - 60px))';  // Hidden beyond left edge
                }
            }

            // Also update sidebar controller if it exists
            if (moduleId === 'inhouse-kanban' && window.inhouseKanbanSidebar) {
                window.inhouseKanbanSidebar.updateSidebarPosition(currentSide);
            }
        }

        positionToggle();

        // Click handler - handle single/double clicks
        toggle.addEventListener('click', async (e) => {
            // Don't process click if user was dragging
            if (hasMoved) {
                hasMoved = false;
                return;
            }

            e.stopPropagation();
            const now = Date.now();
            const timeSinceLastClick = now - lastClickTime;
            lastClickTime = now;

            // Double-click detection (within 400ms)
            if (timeSinceLastClick < 400) {
                // Double-click - switch sides
                currentSide = currentSide === 'left' ? 'right' : 'left';
                localStorage.setItem(`${moduleId}-toggle-side`, currentSide);
                positionToggle();
                console.log(`[ModuleLoader] Switched ${moduleId} toggle to ${currentSide} side`);
                return;
            }

            // Single click - check if floating toggle should open sidebar or main tab
            // Check for sidebar config in both root and capabilities (supports both manifest formats)
            const hasSidebar = module.sidebar?.enabled || module.capabilities?.sidebar?.enabled;

            if (module.floating_toggle_opens_sidebar && hasSidebar) {
                // Open sidebar instead of switching tab
                console.log(`[ModuleLoader] 🎯 Opening SIDEBAR for ${moduleId} (floating toggle clicked, NOT loading dashboard)`);

                // ✅ Check if sidebar HTML is loaded (need HTML in DOM, but don't initialize JS dashboard)
                if (!this.loadedModules.has(moduleId)) {
                    console.log(`[ModuleLoader] ⏳ Sidebar not loaded yet, loading HTML only...`);
                    await this.loadModule(moduleId, { skipJsInit: false, onlyHtml: true, source: 'floating-toggle' });
                }

                // ✅ Use SidebarManager framework to open sidebar
                if (window.SidebarManager) {
                    const sidebarId = `${moduleId}-sidebar`;
                    console.log(`[ModuleLoader] ✅ Opening sidebar via SidebarManager: ${sidebarId}`);
                    window.SidebarManager.toggle(sidebarId);
                } else {
                    console.error(`[ModuleLoader] ❌ SidebarManager not available`);
                    // Fallback: Try direct sidebar toggle
                    const sidebar = document.getElementById(`${moduleId}-sidebar`);
                    if (sidebar) {
                        sidebar.classList.toggle('active');
                        console.log(`[ModuleLoader] ⚠️ Fallback: Toggled sidebar directly (without framework)`);
                    } else {
                        console.error(`[ModuleLoader] ❌ Sidebar element not found: ${moduleId}-sidebar`);
                    }
                }
            } else if (module.main_tab) {
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
        });

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

        // Mouseup - end drag and save position
        document.addEventListener('mouseup', async () => {
            if (isDragging) {
                isDragging = false;
                toggle.style.cursor = 'grab';
                toggle.classList.remove('dragging');

                if (hasMoved) {
                    // User dragged - save position
                    userHasDragged = true;
                    localStorage.setItem(`${moduleId}-toggle-top`, toggle.style.top);

                    // Determine which side based on toggle position
                    const windowWidth = window.innerWidth;
                    const toggleRect = toggle.getBoundingClientRect();
                    const toggleCenterX = toggleRect.left + (toggleRect.width / 2);

                    // If toggle is in left half of screen, use left side; otherwise right side
                    const detectedSide = toggleCenterX < (windowWidth / 2) ? 'left' : 'right';

                    // Update side if it changed
                    if (detectedSide !== currentSide) {
                        console.log(`[ModuleLoader] Toggle moved to ${detectedSide} side for ${moduleId}`);
                        currentSide = detectedSide;
                        localStorage.setItem(`${moduleId}-toggle-side`, currentSide);
                        positionToggle();

                        // Update SidebarManager if module is registered
                        if (window.SidebarManager && window.SidebarManager.sidebars.has(`${moduleId}-sidebar`)) {
                            const sidebarConfig = window.SidebarManager.sidebars.get(`${moduleId}-sidebar`);
                            sidebarConfig.side = currentSide;
                            const sidebarElement = sidebarConfig.element;
                            if (sidebarElement) {
                                window.SidebarManager.applySidebarStyles(sidebarElement, sidebarConfig);
                            }
                        }
                    }
                }

                hasMoved = false;
            }
        });
    }

    /**
     * Generate main tab containers for modules that request them
     */
    generateMainTabs() {
        console.log('🔵 [ModuleLoader.generateMainTabs] FUNCTION CALLED');
        console.log('🔍 [DIAGNOSTIC - generateMainTabs] ========== GENERATE MAIN TABS START ==========');
        console.log('[ModuleLoader] Generating main tab containers...');

        const mainContent = document.querySelector('.main-content');
        console.log('🔍 [DIAGNOSTIC - generateMainTabs] .main-content exists:', !!mainContent);

        if (!mainContent) {
            console.error('❌ [CRITICAL - generateMainTabs] Main content area not found! Cannot generate tabs!');
            return;
        }

        console.log('🔍 [DIAGNOSTIC - generateMainTabs] .main-content children BEFORE generation:', mainContent.children.length);
        console.log('🔍 [DIAGNOSTIC - generateMainTabs] Existing tab IDs:',
            Array.from(mainContent.querySelectorAll('.tab-content')).map(t => t.id));

        for (const [moduleId, module] of this.modules) {
            if (!module.available || !module.main_tab) {
                continue;
            }

            const tabId = module.main_tab_id || moduleId;
            console.log(`🔍 [DIAGNOSTIC - generateMainTabs] Processing module: ${moduleId}, tabId: ${tabId}`);

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
            } else if (moduleId === 'quote-calculator') {
                // Create Quote Calculator main tab container
                tabContainer.innerHTML = `
                    <div id="${moduleId}-main-container" class="active" style="height: 100%; display: flex; flex-direction: column; background: #0B0E13; padding: 20px; overflow: auto;">
                        <div style="max-width: 1200px; margin: 0 auto; width: 100%;">
                            <h1 style="color: #fff; margin-bottom: 20px;">
                                <i class="fas fa-calculator" style="color: ${module.color || '#ffb347'};"></i>
                                Quote Calculator
                            </h1>
                            
                            <!-- Quote calculator content will be injected here by quote-calculator.js -->
                            <div id="quote-calculator-main-content">
                                <div style="text-align: center; padding: 40px; color: #9CA3AF;">
                                    <i class="fas fa-calculator" style="font-size: 3rem; color: ${module.color || '#ffb347'}; margin-bottom: 16px;"></i>
                                    <p style="font-size: 16px;">Loading Quote Calculator...</p>
                                </div>
                            </div>
                        </div>
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

            console.log(`✅ [ModuleLoader] Created main tab for ${module.name} (ID: tab-${tabId})`);
            console.log(`🔍 [DIAGNOSTIC - generateMainTabs] Tab appended to mainContent, new child count:`, mainContent.children.length);
        }

        console.log('🔍 [DIAGNOSTIC - generateMainTabs] .main-content children AFTER generation:', mainContent.children.length);
        console.log('🔍 [DIAGNOSTIC - generateMainTabs] Final tab IDs:',
            Array.from(mainContent.querySelectorAll('.tab-content')).map(t => t.id));
        console.log('🔍 [DIAGNOSTIC - generateMainTabs] ========== GENERATE MAIN TABS COMPLETE ==========');
    }

    /**
     * Load auto-load modules
     */
    async loadAutoLoadModules() {
        console.log('🔵 [ModuleLoader.loadAutoLoadModules] FUNCTION CALLED');
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
    async loadModule(moduleId, options = {}) {
        const { skipHtml = false, onlyHtml = false, source = 'unknown' } = options;
        console.log(`🔵 [ModuleLoader.loadModule] FUNCTION CALLED with moduleId: ${moduleId}`);
        console.log(`[ModuleLoader] Loading module: ${moduleId} (source: ${source}, skipHtml: ${skipHtml}, onlyHtml: ${onlyHtml})`);

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
            // Check if module has HTML file - some modules create UI purely in JavaScript
            const hasHtmlFile = module.html_file || module.htmlPath;

            let createdUiFallback = false;
            if (hasHtmlFile && !skipHtml) {
                console.log(`[ModuleLoader] 📄 Loading HTML for ${moduleId} (skipHtml: ${skipHtml})...`);
                // Determine HTML path - try htmlPath from manifest first, then external/modules (Flask route), then backend API
                let htmlPath = module.htmlPath || (module.html_file ? `external/modules/${moduleId}/${module.html_file}` : null);

                // Attempt to fetch HTML; if fetch fails (network error, connection refused) fall back to JS UI
                try {
                    // Try external/modules path first (for external modules) - only if path is defined
                    let htmlResponse = htmlPath ? await fetch(htmlPath) : null;

                    // Fallback to backend API if modules_external path fails or wasn't attempted
                    if (!htmlResponse || !htmlResponse.ok) {
                        if (htmlPath) {
                            console.log(`[ModuleLoader] modules_external path failed, trying backend API for ${moduleId}`);
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
                } catch (e) {
                    // Network errors (ERR_CONNECTION_REFUSED) or other fetch failures end up here
                    console.warn(`[ModuleLoader] ⚠️ Could not fetch HTML for ${moduleId}: ${e}. Falling back to JS UI creation.`);
                    createdUiFallback = true;
                }
            } else if (skipHtml) {
                console.log(`[ModuleLoader] ⏭️ Skipping HTML for ${moduleId} (skipHtml: true)`);
                createdUiFallback = false; // Don't create fallback UI when explicitly skipping HTML
            } else {
                console.log(`[ModuleLoader] Module ${moduleId} has no HTML file - will create UI in JavaScript`);
                createdUiFallback = true;
            }

            // If HTML wasn't injected, create a minimal UI container via JavaScript so module can initialize
            if (createdUiFallback) {
                try {
                    this._createModuleUIFromJS(moduleId, module);
                    console.log(`[ModuleLoader] Created JS fallback UI for ${moduleId}`);
                } catch (e) {
                    console.error(`[ModuleLoader] Failed to create JS fallback UI for ${moduleId}:`, e);
                }
            }

            // Load CSS - use direct path (more reliable)
            if ((module.css_file || module.stylePath) && !document.querySelector(`link[data-module="${moduleId}"]`)) {
                const link = document.createElement('link');
                link.rel = 'stylesheet';
                link.dataset.module = moduleId;

                // Use direct path from manifest (matches Flask route /external/modules/)
                const cssPath = module.stylePath || `external/modules/${moduleId}/${module.css_file}`;
                link.href = cssPath;

                link.onerror = () => {
                    console.warn(`[ModuleLoader] ⚠️ Failed to load CSS for ${moduleId} from ${cssPath}`);
                };

                document.head.appendChild(link);
                console.log(`[ModuleLoader] Loaded CSS for ${moduleId} from ${cssPath}`);
            }

            // Load JS - try direct path first (more reliable than Flask API route)
            if ((module.js_file || module.scriptPath) && !document.querySelector(`script[data-module="${moduleId}"]`) && !onlyHtml) {
                console.log(`[ModuleLoader] 📜 Loading JS for ${moduleId} (onlyHtml: ${onlyHtml})...`);

                // Check if module uses Modern Framework V4 (ES6 modules)
                // ONLY use ES6 if explicitly marked with framework: "v4" in manifest
                const isModernFramework = module.loading?.framework === 'v4';

                if (isModernFramework) {
                    // ES6 module loading with dynamic import
                    const jsPath = module.scriptPath || `external/modules/${moduleId}/${module.js_file}`;
                    console.log(`[ModuleLoader] 🔷 Loading ES6 module for ${moduleId} from ${jsPath}`);

                    try {
                        // Use absolute URL for import (relative to page, not this script)
                        const baseUrl = window.location.origin + window.location.pathname.substring(0, window.location.pathname.lastIndexOf('/') + 1);
                        const absoluteUrl = new URL(jsPath, baseUrl).href;

                        console.log(`[ModuleLoader] 📦 Importing from absolute URL: ${absoluteUrl}`);
                        const moduleExport = await import(absoluteUrl);
                        const moduleDefinition = moduleExport.default;

                        if (moduleDefinition) {
                            // Store module definition in registry
                            if (!window.ModuleRegistry) window.ModuleRegistry = {};
                            window.ModuleRegistry[moduleId] = moduleDefinition;
                            console.log(`[ModuleLoader] ✅ ES6 module loaded and registered: ${moduleId}`);
                        } else {
                            console.error(`[ModuleLoader] ❌ ES6 module ${moduleId} has no default export`);
                            // Fall back to classic loading
                            await this._loadClassicScript(moduleId, jsPath);
                        }
                    } catch (error) {
                        console.error(`[ModuleLoader] ❌ Failed to load ES6 module ${moduleId}:`, error);
                        console.warn(`[ModuleLoader] ⚠️ Trying fallback classic script loading...`);

                        // Fallback to classic script loading
                        const jsPath = module.scriptPath || `external/modules/${moduleId}/${module.js_file}`;
                        await this._loadClassicScript(moduleId, jsPath);
                    }
                } else {
                    // Classic script loading (legacy modules - DEFAULT)
                    const jsPath = module.scriptPath || `external/modules/${moduleId}/${module.js_file}`;
                    await this._loadClassicScript(moduleId, jsPath);
                }
            } else if (onlyHtml) {
                console.log(`[ModuleLoader] ⏭️ Skipping JS for ${moduleId} (onlyHtml: true)`);
            }

            // Load additional scripts (if any) - useful for dependencies like Supabase integrations
            if (module.additional_scripts && Array.isArray(module.additional_scripts) && !onlyHtml) {
                for (const additionalScriptPath of module.additional_scripts) {
                    const scriptId = `${moduleId}-${additionalScriptPath.split('/').pop().replace('.js', '')}`;

                    if (!document.querySelector(`script[data-additional-script="${scriptId}"]`)) {
                        await new Promise((resolve) => {
                            const script = document.createElement('script');
                            script.dataset.additionalScript = scriptId;
                            script.dataset.module = moduleId;
                            script.src = additionalScriptPath;

                            script.onload = () => {
                                console.log(`[ModuleLoader] ✅ Loaded additional script for ${moduleId}: ${additionalScriptPath}`);
                                resolve();
                            };

                            script.onerror = () => {
                                console.error(`[ModuleLoader] ❌ Failed to load additional script: ${additionalScriptPath}`);
                                resolve(); // Don't block module load on additional script failure
                            };

                            document.body.appendChild(script);
                        });
                    }
                }
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
     * Load classic script (non-ES6 modules)
     * @private
     */
    async _loadClassicScript(moduleId, jsPath) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.dataset.module = moduleId;
            script.src = jsPath;

            script.onload = () => {
                console.log(`[ModuleLoader] ✅ Loaded JS for ${moduleId} from ${jsPath}`);
                resolve();
            };

            script.onerror = () => {
                console.error(`[ModuleLoader] ❌ Failed to load JS for ${moduleId} from ${jsPath}`);
                console.warn(`[ModuleLoader] ⚠️ Module ${moduleId} JS failed to load, continuing anyway...`);
                resolve(); // Resolve instead of reject to allow module to continue
            };

            document.body.appendChild(script);
        });
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
            const moduleDefinition = window.ModuleRegistry[moduleId];

            // Check if it's a Modern Framework V4 module (has onDashboardLoad)
            const isModernV4 = typeof moduleDefinition.onDashboardLoad === 'function';

            if (isModernV4) {
                console.log(`[ModuleLoader] 🔷 Modern Framework V4 module detected: ${moduleId}`);

                // Prepare utilities for injection (Modern Framework pattern)
                const utilities = this._prepareUtilities(moduleId);

                // Call onDashboardLoad lifecycle hook with utilities
                try {
                    await moduleDefinition.onDashboardLoad(utilities);
                    console.log(`[ModuleLoader] ✅ Modern V4 module ${moduleId} initialized via onDashboardLoad`);
                } catch (error) {
                    console.error(`[ModuleLoader] ❌ Failed to initialize Modern V4 module ${moduleId}:`, error);
                }
            } else if (typeof moduleDefinition.init === 'function') {
                // Legacy module with init() method
                try {
                    await moduleDefinition.init();
                    console.log(`[ModuleLoader] ✅ Module ${moduleId} initialized successfully`);
                } catch (error) {
                    console.error(`[ModuleLoader] ❌ Failed to initialize ${moduleId}:`, error);
                }
            } else {
                console.log(`[ModuleLoader] No initialization function found for ${moduleId}`);
            }
        } else {
            console.log(`[ModuleLoader] No initialization function found for ${moduleId}`);
        }
    }

    /**
     * Prepare utilities object for Modern Framework V4 modules
     * @private
     */
    _prepareUtilities(moduleId) {
        return {
            // DOM utilities
            dom: {
                getContainer: () => document.getElementById(`${moduleId}-main-container`) ||
                    document.getElementById(`tab-${moduleId}`) ||
                    document.querySelector(`[data-module="${moduleId}"]`),
                createElement: (tag, attrs = {}, children = []) => {
                    const el = document.createElement(tag);
                    Object.entries(attrs).forEach(([key, value]) => el.setAttribute(key, value));
                    children.forEach(child => el.appendChild(typeof child === 'string' ? document.createTextNode(child) : child));
                    return el;
                },
                on: (element, event, selectorOrHandler, handler) => {
                    // Event delegation support
                    if (typeof selectorOrHandler === 'string') {
                        element.addEventListener(event, (e) => {
                            if (e.target.matches(selectorOrHandler) || e.target.closest(selectorOrHandler)) {
                                handler(e);
                            }
                        });
                    } else {
                        element.addEventListener(event, selectorOrHandler);
                    }
                }
            },

            // API client
            api: {
                get: async (url, options = {}) => {
                    const token = localStorage.getItem('authToken');
                    const response = await fetch(url, {
                        ...options,
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json',
                            ...options.headers
                        }
                    });
                    return response.json();
                },
                post: async (url, data, options = {}) => {
                    const token = localStorage.getItem('authToken');
                    const response = await fetch(url, {
                        method: 'POST',
                        body: JSON.stringify(data),
                        ...options,
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json',
                            ...options.headers
                        }
                    });
                    return response.json();
                }
            },

            // Storage utilities
            storage: {
                get: (key, defaultValue = null) => {
                    try {
                        const value = localStorage.getItem(key);
                        return value ? JSON.parse(value) : defaultValue;
                    } catch {
                        return defaultValue;
                    }
                },
                set: (key, value) => {
                    localStorage.setItem(key, JSON.stringify(value));
                },
                remove: (key) => localStorage.removeItem(key)
            },

            // Event bus
            events: {
                on: (eventName, handler) => window.addEventListener(eventName, handler),
                emit: (eventName, data) => window.dispatchEvent(new CustomEvent(eventName, { detail: data })),
                off: (eventName, handler) => window.removeEventListener(eventName, handler)
            },

            // Logger
            log: {
                info: (...args) => console.log(`[${moduleId}]`, ...args),
                warn: (...args) => console.warn(`[${moduleId}]`, ...args),
                error: (...args) => console.error(`[${moduleId}]`, ...args),
                debug: (...args) => console.debug(`[${moduleId}]`, ...args),
                success: (...args) => console.log(`[${moduleId}] ✅`, ...args)
            }
        };
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
window.initializeModuleSystem = async function (forceReload = false) {
    console.log('🔵 [window.initializeModuleSystem] FUNCTION CALLED (forceReload:', forceReload, ')');
    console.log('[ModuleSystem] initializeModuleSystem called (forceReload:', forceReload, ')');

    // Get user ID from session (assumes window.currentUserId is set)
    const userId = window.currentUserId || window.userProfile?.id || 14; // Default to user 14 for InHouse
    console.log('🔵 [window.initializeModuleSystem] Resolved userId:', userId);

    if (!userId) {
        console.error('❌ [window.initializeModuleSystem] No user ID available - cannot initialize modules');
        console.error('[ModuleSystem] No user ID available - cannot initialize modules');
        return;
    }

    console.log(`🔵 [window.initializeModuleSystem] Calling moduleLoader.initialize(${userId})...`);
    console.log(`[ModuleSystem] Initializing modules for user ${userId}`);

    try {
        await window.moduleLoader.initialize(userId);
        console.log('✅ [window.initializeModuleSystem] moduleLoader.initialize() COMPLETED SUCCESSFULLY');
        console.log('✅ [ModuleSystem] Module system initialized successfully');
    } catch (error) {
        console.error('❌ [window.initializeModuleSystem] moduleLoader.initialize() FAILED:', error);
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
