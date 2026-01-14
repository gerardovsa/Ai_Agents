/**
 * FILE: UI/modules_[internal|external]/[module-name]/[module-name].js
 * MODULE TYPE: [internal|external|component]
 * ARCHITECTURE: Framework-modern (Composition pattern)
 * 
 * CAPABILITIES:
 * ================
 * DASHBOARD: [ENABLED|DISABLED]
 *   - Container ID: #tab-[module-name]
 *   - Rendering: [js-controlled|html-template]
 *   - Init Hook: onDashboardLoad()
 * 
 * SIDEBAR: [ENABLED|DISABLED]
 *   - Container ID: #[module-name]-sidebar
 *   - HTML File: [filename].html
 *   - Rendering: [js-controlled|html-template]
 *   - Init Hook: onSidebarLoad()
 * 
 * DEPENDENCIES:
 * =============
 * - ModuleLoaderV4 (module loading framework)
 * - Utilities: dom, api, storage, events (from module-utilities.js)
 * 
 * LAST MODIFIED: [YYYY-MM-DD] - [Description]
 */

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// MODULE DEFINITION (Composition pattern - NO class, NO inheritance)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

export default {
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // MODULE STATE (Private to this object)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    // Utilities (injected by ModuleLoader)
    dom: null,
    api: null,
    storage: null,
    events: null,
    log: null,

    // Module-specific state
    data: [],
    filters: {
        search: '',
        status: 'all'
    },
    dashboardContainer: null,
    sidebarContainer: null,
    eventCleanupFns: [],

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // LIFECYCLE HOOKS (Called by ModuleLoader)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * DASHBOARD LIFECYCLE HOOK
     * Called when: User clicks sidebar button
     * 
     * @param {object} utilities - Composed utilities from ModuleLoader
     */
    async onDashboardLoad(utilities) {
        // 1. Store utilities
        this.dom = utilities.dom;
        this.api = utilities.api;
        this.storage = utilities.storage;
        this.events = utilities.events;
        this.log = utilities.log;

        this.log.info('Dashboard loading...');

        try {
            // 2. Get dashboard container
            this.dashboardContainer = this.dom.getContainer('tab-module-name');

            // 3. Render UI
            this.renderDashboard();

            // 4. Setup event listeners
            this.setupDashboardEvents();

            // 5. Load data
            await this.loadDashboardData();

            this.log.success('Dashboard loaded successfully');

        } catch (error) {
            this.log.error('Failed to load dashboard', error);
            throw error;
        }
    },

    /**
     * SIDEBAR LIFECYCLE HOOK
     * Called when: User clicks floating toggle
     * 
     * @param {object} utilities - Composed utilities from ModuleLoader
     */
    async onSidebarLoad(utilities) {
        // 1. Store utilities
        this.dom = utilities.dom;
        this.api = utilities.api;
        this.storage = utilities.storage;
        this.events = utilities.events;
        this.log = utilities.log;

        this.log.info('Sidebar loading...');

        try {
            // 2. Get sidebar container (HTML already injected by ModuleLoader)
            this.sidebarContainer = this.dom.getContainer('module-name-sidebar');

            // 3. Setup event listeners (HTML already loaded)
            this.setupSidebarEvents();

            // 4. Load data
            await this.loadSidebarData();

            this.log.success('Sidebar loaded successfully');

        } catch (error) {
            this.log.error('Failed to load sidebar', error);
            throw error;
        }
    },

    /**
     * GENERIC LOAD HOOK (Fallback if no specific hook)
     * Called when: Module loaded without specifying view
     * 
     * @param {object} utilities - Composed utilities from ModuleLoader
     */
    async onLoad(utilities) {
        // Store utilities
        this.dom = utilities.dom;
        this.api = utilities.api;
        this.storage = utilities.storage;
        this.events = utilities.events;
        this.log = utilities.log;

        this.log.info('Module loading...');

        // Call both dashboard and sidebar if available
        if (this.dashboardContainer) {
            await this.onDashboardLoad(utilities);
        }
        if (this.sidebarContainer) {
            await this.onSidebarLoad(utilities);
        }
    },

    /**
     * UNLOAD HOOK
     * Called when: Module is being unloaded/cleaned up
     * 
     * @param {object} utilities - Composed utilities from ModuleLoader
     */
    async onUnload(utilities) {
        this.log.info('Module unloading...');

        // 1. Cleanup event listeners
        this.eventCleanupFns.forEach(cleanup => cleanup());
        this.eventCleanupFns = [];

        // 2. Clear containers
        if (this.dashboardContainer) {
            this.dom.clearElement(this.dashboardContainer);
        }
        if (this.sidebarContainer) {
            this.dom.clearElement(this.sidebarContainer);
        }

        // 3. Clear state
        this.data = [];
        this.filters = { search: '', status: 'all' };

        this.log.success('Module unloaded');
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // DASHBOARD METHODS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Render dashboard UI
     */
    renderDashboard() {
        this.log.debug('Rendering dashboard...');

        // Create UI structure using DOM utilities
        const header = this.dom.createElement('div', {
            class: 'module-header'
        }, [
            this.dom.createElement('h1', {}, ['Module Dashboard']),
            this.dom.createElement('button', {
                class: 'btn btn-primary',
                id: 'btn-refresh'
            }, ['Refresh'])
        ]);

        const content = this.dom.createElement('div', {
            class: 'module-content',
            id: 'dashboard-content'
        }, ['Loading...']);

        this.dom.clearElement(this.dashboardContainer);
        this.dashboardContainer.appendChild(header);
        this.dashboardContainer.appendChild(content);
    },

    /**
     * Setup dashboard event listeners
     */
    setupDashboardEvents() {
        this.log.debug('Setting up dashboard events...');

        // Refresh button click
        const refreshBtn = document.getElementById('btn-refresh');
        if (refreshBtn) {
            const cleanup = this.dom.on(refreshBtn, 'click', () => {
                this.loadDashboardData();
            });
            this.eventCleanupFns.push(cleanup);
        }

        // Subscribe to global events
        const unsubscribe = this.events.on('data-updated', (data) => {
            this.log.debug('Data updated event received', data);
            this.loadDashboardData();
        });
        this.eventCleanupFns.push(unsubscribe);
    },

    /**
     * Load dashboard data
     */
    async loadDashboardData() {
        this.log.debug('Loading dashboard data...');

        try {
            // Use API client to fetch data
            const response = await this.api.get('/api/module-name/data', {
                status: this.filters.status
            });

            this.data = response.data || [];
            this.renderDashboardData();

        } catch (error) {
            this.log.error('Failed to load dashboard data', error);
            this.renderError(error.message);
        }
    },

    /**
     * Render dashboard data
     */
    renderDashboardData() {
        const content = document.getElementById('dashboard-content');
        if (!content) return;

        this.dom.clearElement(content);

        if (this.data.length === 0) {
            content.appendChild(
                this.dom.createElement('p', {}, ['No data available'])
            );
            return;
        }

        // Render data items
        this.data.forEach(item => {
            const itemEl = this.dom.createElement('div', {
                class: 'data-item',
                'data-id': item.id
            }, [
                this.dom.createElement('h3', {}, [item.title]),
                this.dom.createElement('p', {}, [item.description])
            ]);
            content.appendChild(itemEl);
        });
    },

    /**
     * Render error message
     */
    renderError(message) {
        const content = document.getElementById('dashboard-content');
        if (!content) return;

        this.dom.clearElement(content);
        content.appendChild(
            this.dom.createElement('div', {
                class: 'error-message'
            }, [message])
        );
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // SIDEBAR METHODS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Setup sidebar event listeners (HTML already loaded)
     */
    setupSidebarEvents() {
        this.log.debug('Setting up sidebar events...');

        // Search input
        const searchInput = this.sidebarContainer.querySelector('#sidebar-search');
        if (searchInput) {
            const cleanup = this.dom.on(searchInput, 'input', (e) => {
                this.filters.search = e.target.value;
                this.filterSidebarData();
            });
            this.eventCleanupFns.push(cleanup);
        }

        // Filter buttons
        const filterBtns = this.dom.query('.sidebar-filter-btn', this.sidebarContainer);
        const cleanup = this.dom.onAll(filterBtns, 'click', (e) => {
            this.filters.status = e.target.dataset.status;
            this.filterSidebarData();
        });
        this.eventCleanupFns.push(cleanup);
    },

    /**
     * Load sidebar data
     */
    async loadSidebarData() {
        this.log.debug('Loading sidebar data...');

        try {
            const response = await this.api.get('/api/module-name/sidebar-data');
            this.data = response.data || [];
            this.renderSidebarData();

        } catch (error) {
            this.log.error('Failed to load sidebar data', error);
        }
    },

    /**
     * Render sidebar data
     */
    renderSidebarData() {
        const container = this.sidebarContainer.querySelector('#sidebar-data-container');
        if (!container) return;

        this.dom.clearElement(container);

        this.data.forEach(item => {
            const itemEl = this.dom.createElement('div', {
                class: 'sidebar-item'
            }, [item.title]);
            container.appendChild(itemEl);
        });
    },

    /**
     * Filter sidebar data
     */
    filterSidebarData() {
        this.log.debug('Filtering sidebar data...', this.filters);

        // Filter data based on current filters
        const filtered = this.data.filter(item => {
            const matchesSearch = item.title.toLowerCase().includes(this.filters.search.toLowerCase());
            const matchesStatus = this.filters.status === 'all' || item.status === this.filters.status;
            return matchesSearch && matchesStatus;
        });

        // Re-render with filtered data
        this.renderSidebarData(filtered);
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // MODULE-SPECIFIC METHODS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Create new item
     */
    async createItem(title, description) {
        this.log.debug('Creating item...', { title, description });

        try {
            const response = await this.api.post('/api/module-name/items', {
                title,
                description
            });

            this.data.push(response.data);
            this.renderDashboardData();

            // Emit event for other modules
            this.events.emit('item-created', response.data);

            return response.data;

        } catch (error) {
            this.log.error('Failed to create item', error);
            throw error;
        }
    },

    /**
     * Delete item
     */
    async deleteItem(itemId) {
        this.log.debug('Deleting item...', { itemId });

        try {
            await this.api.delete(`/api/module-name/items/${itemId}`);

            this.data = this.data.filter(item => item.id !== itemId);
            this.renderDashboardData();

            // Emit event
            this.events.emit('item-deleted', { id: itemId });

        } catch (error) {
            this.log.error('Failed to delete item', error);
            throw error;
        }
    }
};
