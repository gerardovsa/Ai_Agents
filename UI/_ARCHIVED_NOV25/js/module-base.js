/**
 * BaseModule - Base class for all external modules
 * Provides standard interface and utilities
 * 
 * @class BaseModule
 * @created October 30, 2025
 */
class BaseModule {
    constructor(moduleId, modulePath = null) {
        this.moduleId = moduleId;
        this.modulePath = modulePath || moduleId; // Allow custom folder path
        this.container = null;
        this.subTabs = new Map();
        this.activeSubTab = null;
        this.manifest = null;

        console.log(`🔧 BaseModule created for ${moduleId} (path: ${this.modulePath})`);
    }

    /**
     * Initialize module (override in child)
     */
    async initialize() {
        console.log(`🔧 Initializing ${this.moduleId}`);

        // Get container
        this.container = document.getElementById(`tab-${this.moduleId}`);
        if (!this.container) {
            throw new Error(`Container not found for module: ${this.moduleId}`);
        }

        // Load manifest
        await this.loadManifest();

        // Create UI structure
        this.createModuleStructure();

        // Note: Sub-tabs initialization is handled by child classes
        // Child modules call initializeSubTabs() explicitly after their setup completes

        console.log(`✅ ${this.moduleId} initialized`);
    }

    /**
     * Load module manifest
     */
    async loadManifest() {
        try {
            console.log(`📥 Loading manifest for ${this.moduleId} from: external/modules/${this.modulePath}/manifest.json`);
            const manifestUrl = `external/modules/${this.modulePath}/manifest.json`;
            const response = await fetch(manifestUrl);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            this.manifest = await response.json();
            console.log(`Manifest loaded for ${this.moduleId}`);

        } catch (error) {
            console.error(` Failed to load manifest for ${this.moduleId}:`, error);
            // Create minimal manifest
            this.manifest = {
                id: this.moduleId,
                name: this.moduleId.charAt(0).toUpperCase() + this.moduleId.slice(1),
                icon: 'fas fa-cube',
                color: 'var(--accent-primary)',
                description: 'No manifest found',
                tabs: []
            };
        }
    }

    /**
     * Create module UI structure
     */
    createModuleStructure() {
        console.log(`🎨 Creating UI structure for ${this.moduleId}...`);

        // Clear loading state
        this.container.innerHTML = '';

        // Module header
        const header = document.createElement('div');
        header.className = 'module-header';
        header.innerHTML = `
            <div class="module-header-left">
                <h2 class="module-title">
                    <i class="${this.manifest.icon}" style="color: ${this.manifest.color}"></i>
                    ${this.manifest.name}
                </h2>
                <p class="module-description">${this.manifest.description || ''}</p>
            </div>
            <div class="module-header-right">
                <button class="module-action-btn" data-action="refresh" title="Refresh">
                    <i class="fas fa-sync-alt"></i> Refresh
                </button>
                <button class="module-action-btn" data-action="settings" title="Settings">
                    <i class="fas fa-cog"></i> Settings
                </button>
            </div>
        `;

        // Add event listeners to header buttons
        const refreshBtn = header.querySelector('[data-action="refresh"]');
        const settingsBtn = header.querySelector('[data-action="settings"]');

        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.onRefresh());
        }
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => this.onSettings());
        }

        this.container.appendChild(header);

        // Sub-tabs navigation (if module has tabs)
        if (this.manifest.tabs && this.manifest.tabs.length > 0) {
            const subTabsNav = document.createElement('div');
            subTabsNav.className = 'module-subtabs-nav';

            this.manifest.tabs.forEach((tab, index) => {
                const button = document.createElement('button');
                button.className = 'module-subtab-btn';

                // Set first tab or default tab as active
                if (tab.default || index === 0) {
                    button.classList.add('active');
                    this.activeSubTab = tab.id;
                }

                button.setAttribute('data-subtab', tab.id);
                button.innerHTML = `<i class="${tab.icon}"></i> ${tab.name}`;
                button.addEventListener('click', () => this.switchSubTab(tab.id));
                subTabsNav.appendChild(button);
            });

            this.container.appendChild(subTabsNav);
        }

        // Sub-tabs content container
        const subTabsContent = document.createElement('div');
        subTabsContent.className = 'module-subtabs-content';
        subTabsContent.id = `${this.moduleId}-subtabs-content`;
        this.container.appendChild(subTabsContent);

        // Create sub-tab containers
        if (this.manifest.tabs && this.manifest.tabs.length > 0) {
            console.log(`📦 [DOM] Creating ${this.manifest.tabs.length} sub-tab containers for ${this.moduleId}...`);
            this.manifest.tabs.forEach((tab, index) => {
                const subTabDiv = document.createElement('div');
                subTabDiv.className = 'module-subtab-content';

                // Set first tab or default tab as active
                if (tab.default || index === 0) {
                    subTabDiv.classList.add('active');
                }

                const containerId = `${this.moduleId}-subtab-${tab.id}`;
                subTabDiv.id = containerId;
                subTabDiv.setAttribute('data-subtab', tab.id);
                subTabsContent.appendChild(subTabDiv);
                console.log(`   ✅ Created container: ${containerId}`);
            });
        } else {
            // If no sub-tabs, create single content area
            const singleContent = document.createElement('div');
            singleContent.className = 'module-subtab-content active';
            singleContent.id = `${this.moduleId}-content`;
            subTabsContent.appendChild(singleContent);
        }

        console.log(`✅ UI structure created for ${this.moduleId}`);
        console.log(`📍 [DOM] Sub-tabs container appended to: #${this.container.id}`);
    }

    /**
     * Initialize sub-tabs (override in child class)
     */
    initializeSubTabs() {
        console.log(`📋 Initialize sub-tabs for ${this.moduleId} (override this method)`);
    }

    /**
     * Switch sub-tab
     */
    switchSubTab(subTabId) {
        console.log(`🔄 Switching to sub-tab: ${subTabId}`);

        // Hide all sub-tabs
        this.container.querySelectorAll('.module-subtab-content').forEach(tab => {
            tab.classList.remove('active');
        });

        // Remove active from all buttons
        this.container.querySelectorAll('.module-subtab-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Show selected sub-tab
        const subTab = document.getElementById(`${this.moduleId}-subtab-${subTabId}`);
        if (subTab) {
            subTab.classList.add('active');
        } else {
            console.error(` Sub-tab not found: ${this.moduleId}-subtab-${subTabId}`);
            return;
        }

        // Activate button
        const button = this.container.querySelector(`[data-subtab="${subTabId}"]`);
        if (button) {
            button.classList.add('active');
        }

        this.activeSubTab = subTabId;

        // Trigger sub-tab refresh
        this.onSubTabActivate(subTabId);
    }

    /**
     * Called when module becomes active
     */
    onActivate() {
        console.log(`▶️ ${this.moduleId} activated`);
        // Override in child class
    }

    /**
     * Called when sub-tab becomes active
     */
    onSubTabActivate(subTabId) {
        console.log(`▶️ Sub-tab ${subTabId} activated`);
        // Override in child class
    }

    /**
     * Called when refresh button is clicked
     */
    onRefresh() {
        console.log(`🔄 Refresh requested for ${this.moduleId}`);
        // Override in child class
        location.reload();
    }

    /**
     * Called when settings button is clicked
     */
    onSettings() {
        console.log(`⚙️ Settings requested for ${this.moduleId}`);
        // Override in child class
        alert(`Settings for ${this.manifest.name} coming soon!`);
    }

    /**
     * Utility: Create dashboard card
     */
    createCard(title, icon, content, actions = '') {
        const card = document.createElement('div');
        card.className = 'dashboard-card';
        card.innerHTML = `
            <div class="card-header">
                <h3 class="card-title">
                    <i class="${icon}"></i> ${title}
                </h3>
                ${actions ? `<div class="card-actions">${actions}</div>` : ''}
            </div>
            <div class="card-content">
                ${content}
            </div>
        `;
        return card;
    }

    /**
     * Utility: Create stat card
     */
    createStatCard(label, value, icon, iconClass = 'primary', change = '') {
        const card = document.createElement('div');
        card.className = 'stat-card';
        card.innerHTML = `
            <div class="stat-icon ${iconClass}">
                <i class="${icon}"></i>
            </div>
            <div class="stat-content">
                <div class="stat-label">${label}</div>
                <div class="stat-value">${value}</div>
                ${change ? `<div class="stat-change">${change}</div>` : ''}
            </div>
        `;
        return card;
    }

    /**
     * Utility: Show loading spinner
     */
    showLoading(container, message = 'Loading...') {
        container.innerHTML = `
            <div class="loading-state">
                <div class="loading-spinner"></div>
                <p>${message}</p>
            </div>
        `;
    }

    /**
     * Utility: Show error message
     */
    showError(container, message) {
        container.innerHTML = `
            <div class="error-state">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${message}</p>
            </div>
        `;
    }

    /**
     * Utility: Show empty state
     */
    showEmpty(container, message, icon = 'fas fa-inbox') {
        container.innerHTML = `
            <div class="empty-state">
                <i class="${icon}"></i>
                <p>${message}</p>
            </div>
        `;
    }

    /**
     * Utility: Get sub-tab container
     */
    getSubTabContainer(subTabId) {
        return document.getElementById(`${this.moduleId}-subtab-${subTabId}`);
    }

    /**
     * Utility: Get main content container (if no sub-tabs)
     */
    getContentContainer() {
        return document.getElementById(`${this.moduleId}-content`);
    }

    /**
     * Cleanup (called when module is unloaded)
     */
    destroy() {
        console.log(`🗑️ Destroying ${this.moduleId}`);
        // Override in child class to cleanup resources
        // Clear any intervals, websockets, etc.
    }
}

// Make BaseModule available globally
window.BaseModule = BaseModule;
console.log('BaseModule available globally');
