/**
 * FILE: UI/modules_external/example-modern/example-modern.js
 * MODULE TYPE: external
 * ARCHITECTURE: Framework-modern (Composition pattern)
 * 
 * PURPOSE: Complete example of modern module pattern
 * 
 * CAPABILITIES:
 * ================
 * ✅ Dashboard: YES - Full-featured data management view
 *    - Container: #tab-example-modern
 *    - Rendering: JS-controlled
 *    - Features: CRUD operations, filters, search
 * 
 * ✅ Sidebar: YES - Quick actions panel
 *    - Container: #example-modern-sidebar
 *    - HTML: example-modern-SIDEBAR.html
 *    - Features: Recent items, quick create
 * 
 * DEPENDENCIES:
 * =============
 * - dom (DOM manipulation)
 * - api (Backend API calls)
 * - storage (localStorage wrapper)
 * - events (Inter-module communication)
 * - log (Module-specific logger - always included)
 * 
 * FEATURES DEMONSTRATED:
 * =====================
 * ✅ Composition-based architecture (NO inheritance)
 * ✅ Lifecycle hooks (onDashboardLoad, onSidebarLoad, onUnload)
 * ✅ Proper event cleanup
 * ✅ Error handling with try/catch
 * ✅ Loading states
 * ✅ Filters and search
 * ✅ CRUD operations
 * ✅ Inter-module communication via events
 * ✅ localStorage persistence
 * ✅ Responsive design
 * 
 * LAST MODIFIED: 2025-11-29 - Initial modern pattern example
 */

export default {
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // STATE (Private to this object)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    // Utilities (injected by ModuleLoader)
    dom: null,
    api: null,
    storage: null,
    events: null,
    log: null,

    // Module-specific state
    data: [],
    filteredData: [],
    filters: {
        search: '',
        status: 'all',
        category: 'all'
    },
    isLoading: false,
    selectedItem: null,

    // Container references
    dashboardContainer: null,
    sidebarContainer: null,

    // Event cleanup tracking
    eventCleanupFns: [],

    // Refresh interval
    refreshInterval: null,

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // LIFECYCLE HOOKS (Called by ModuleLoader)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * DASHBOARD LIFECYCLE HOOK
     * Called when: User clicks sidebar button or tab becomes active
     * 
     * @param {object} utilities - Composed utilities from ModuleLoader
     */
    async onDashboardLoad(utilities) {
        // 1. Store utilities (CRITICAL - do this first!)
        Object.assign(this, utilities);
        this.log.info('Dashboard loading...');

        try {
            // 2. Get dashboard container
            this.dashboardContainer = this.dom.getContainer('tab-example-modern');
            if (!this.dashboardContainer) {
                throw new Error('Dashboard container not found');
            }

            // 3. Load saved filters from localStorage
            this.loadFilters();

            // 4. Render dashboard UI (synchronous)
            this.renderDashboard();

            // 5. Setup event listeners
            this.setupDashboardEvents();

            // 6. Load data (asynchronous)
            await this.loadDashboardData();

            // 7. Start auto-refresh
            this.startAutoRefresh();

            // 8. Emit event for other modules
            this.events.emit('example-modern:dashboard-loaded', {
                timestamp: Date.now()
            });

            this.log.success('Dashboard loaded successfully');

        } catch (error) {
            this.log.error('Failed to load dashboard', error);
            this.showError('Failed to load dashboard. Please refresh the page.');
            throw error;
        }
    },

    /**
     * SIDEBAR LIFECYCLE HOOK
     * Called when: User clicks floating toggle button
     * 
     * @param {object} utilities - Composed utilities from ModuleLoader
     */
    async onSidebarLoad(utilities) {
        // 1. Store utilities
        Object.assign(this, utilities);
        this.log.info('Sidebar loading...');

        try {
            // 2. Get sidebar container (HTML already loaded by ModuleLoader)
            this.sidebarContainer = this.dom.getContainer('example-modern-sidebar');
            if (!this.sidebarContainer) {
                throw new Error('Sidebar container not found');
            }

            // 3. Setup event listeners (HTML template already in DOM)
            this.setupSidebarEvents();

            // 4. Load sidebar data (lightweight summary)
            await this.loadSidebarData();

            // 5. Emit event
            this.events.emit('example-modern:sidebar-loaded', {
                timestamp: Date.now()
            });

            this.log.success('Sidebar loaded successfully');

        } catch (error) {
            this.log.error('Failed to load sidebar', error);
            throw error;
        }
    },

    /**
     * CLEANUP LIFECYCLE HOOK
     * Called when: Module is unloaded or page refreshed
     */
    async onUnload() {
        this.log.info('Unloading module...');

        try {
            // 1. Clean up all event listeners
            this.eventCleanupFns.forEach(cleanup => {
                try {
                    cleanup();
                } catch (error) {
                    this.log.warn('Failed to cleanup event listener', error);
                }
            });
            this.eventCleanupFns = [];

            // 2. Stop auto-refresh
            if (this.refreshInterval) {
                clearInterval(this.refreshInterval);
                this.refreshInterval = null;
            }

            // 3. Save current state to localStorage
            this.saveFilters();

            // 4. Clear references
            this.dashboardContainer = null;
            this.sidebarContainer = null;
            this.data = [];
            this.filteredData = [];

            // 5. Emit cleanup event
            this.events.emit('example-modern:unloaded', {
                timestamp: Date.now()
            });

            this.log.success('Module unloaded successfully');

        } catch (error) {
            this.log.error('Error during unload', error);
        }
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // RENDERING (Dashboard UI)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Render dashboard HTML structure
     */
    renderDashboard() {
        const html = `
            <div class="example-modern-dashboard">
                <!-- Header -->
                <div class="dashboard-header">
                    <h2>Example Modern Module</h2>
                    <div class="header-actions">
                        <button class="btn btn-primary" id="create-new-btn">
                            <i class="fas fa-plus"></i> Create New
                        </button>
                        <button class="btn btn-secondary" id="refresh-btn">
                            <i class="fas fa-sync"></i> Refresh
                        </button>
                    </div>
                </div>

                <!-- Filters -->
                <div class="dashboard-filters">
                    <input 
                        type="text" 
                        id="search-input" 
                        placeholder="Search..." 
                        value="${this.filters.search}"
                    />
                    
                    <select id="status-filter">
                        <option value="all" ${this.filters.status === 'all' ? 'selected' : ''}>All Status</option>
                        <option value="active" ${this.filters.status === 'active' ? 'selected' : ''}>Active</option>
                        <option value="pending" ${this.filters.status === 'pending' ? 'selected' : ''}>Pending</option>
                        <option value="completed" ${this.filters.status === 'completed' ? 'selected' : ''}>Completed</option>
                    </select>
                    
                    <select id="category-filter">
                        <option value="all" ${this.filters.category === 'all' ? 'selected' : ''}>All Categories</option>
                        <option value="type-a" ${this.filters.category === 'type-a' ? 'selected' : ''}>Type A</option>
                        <option value="type-b" ${this.filters.category === 'type-b' ? 'selected' : ''}>Type B</option>
                        <option value="type-c" ${this.filters.category === 'type-c' ? 'selected' : ''}>Type C</option>
                    </select>

                    <button class="btn btn-link" id="clear-filters-btn">Clear Filters</button>
                </div>

                <!-- Loading State -->
                <div id="loading-state" class="loading-state" style="display: none;">
                    <i class="fas fa-spinner fa-spin"></i>
                    <span>Loading data...</span>
                </div>

                <!-- Error State -->
                <div id="error-state" class="error-state" style="display: none;">
                    <i class="fas fa-exclamation-circle"></i>
                    <span id="error-message"></span>
                </div>

                <!-- Data Grid -->
                <div id="data-grid" class="data-grid">
                    <!-- Rendered by renderDataGrid() -->
                </div>

                <!-- Empty State -->
                <div id="empty-state" class="empty-state" style="display: none;">
                    <i class="fas fa-inbox"></i>
                    <p>No items found</p>
                    <button class="btn btn-primary" id="create-first-btn">
                        Create Your First Item
                    </button>
                </div>
            </div>
        `;

        this.dom.injectHTML(this.dashboardContainer, html);
    },

    /**
     * Render data grid
     */
    renderDataGrid() {
        const gridContainer = this.dashboardContainer.querySelector('#data-grid');
        if (!gridContainer) return;

        // Apply filters
        this.applyFilters();

        // Show empty state if no data
        if (this.filteredData.length === 0) {
            this.dom.hide(gridContainer);
            this.dom.show(this.dashboardContainer.querySelector('#empty-state'));
            return;
        }

        // Hide empty state, show grid
        this.dom.hide(this.dashboardContainer.querySelector('#empty-state'));
        this.dom.show(gridContainer);

        // Render items
        const html = this.filteredData.map(item => `
            <div class="data-item" data-id="${item.id}">
                <div class="item-header">
                    <h4>${item.name}</h4>
                    <span class="badge badge-${item.status}">${item.status}</span>
                </div>
                <div class="item-body">
                    <p>${item.description || 'No description'}</p>
                    <div class="item-meta">
                        <span class="category">${item.category}</span>
                        <span class="date">${this.formatDate(item.created_at)}</span>
                    </div>
                </div>
                <div class="item-actions">
                    <button class="btn-icon edit-btn" data-id="${item.id}" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon delete-btn" data-id="${item.id}" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');

        this.dom.injectHTML(gridContainer, html);
    },

    /**
     * Render sidebar summary
     */
    renderSidebarSummary(summary) {
        const summaryContainer = this.sidebarContainer.querySelector('#summary-stats');
        if (!summaryContainer) return;

        const html = `
            <div class="stat-card">
                <div class="stat-value">${summary.total}</div>
                <div class="stat-label">Total Items</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${summary.active}</div>
                <div class="stat-label">Active</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${summary.pending}</div>
                <div class="stat-label">Pending</div>
            </div>
        `;

        this.dom.injectHTML(summaryContainer, html);
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // EVENT HANDLING
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Setup dashboard event listeners
     */
    setupDashboardEvents() {
        // Create button
        const createBtn = this.dashboardContainer.querySelector('#create-new-btn');
        const cleanup1 = this.dom.on(createBtn, 'click', () => this.handleCreate());
        this.eventCleanupFns.push(cleanup1);

        // Refresh button
        const refreshBtn = this.dashboardContainer.querySelector('#refresh-btn');
        const cleanup2 = this.dom.on(refreshBtn, 'click', () => this.loadDashboardData());
        this.eventCleanupFns.push(cleanup2);

        // Search input (debounced)
        const searchInput = this.dashboardContainer.querySelector('#search-input');
        let searchTimeout;
        const cleanup3 = this.dom.on(searchInput, 'input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.filters.search = e.target.value;
                this.renderDataGrid();
                this.saveFilters();
            }, 300);
        });
        this.eventCleanupFns.push(cleanup3);

        // Status filter
        const statusFilter = this.dashboardContainer.querySelector('#status-filter');
        const cleanup4 = this.dom.on(statusFilter, 'change', (e) => {
            this.filters.status = e.target.value;
            this.renderDataGrid();
            this.saveFilters();
        });
        this.eventCleanupFns.push(cleanup4);

        // Category filter
        const categoryFilter = this.dashboardContainer.querySelector('#category-filter');
        const cleanup5 = this.dom.on(categoryFilter, 'change', (e) => {
            this.filters.category = e.target.value;
            this.renderDataGrid();
            this.saveFilters();
        });
        this.eventCleanupFns.push(cleanup5);

        // Clear filters
        const clearBtn = this.dashboardContainer.querySelector('#clear-filters-btn');
        const cleanup6 = this.dom.on(clearBtn, 'click', () => this.clearFilters());
        this.eventCleanupFns.push(cleanup6);

        // Edit/Delete buttons (event delegation)
        const gridContainer = this.dashboardContainer.querySelector('#data-grid');
        const cleanup7 = this.dom.on(gridContainer, 'click', (e) => {
            if (e.target.closest('.edit-btn')) {
                const id = e.target.closest('.edit-btn').dataset.id;
                this.handleEdit(id);
            } else if (e.target.closest('.delete-btn')) {
                const id = e.target.closest('.delete-btn').dataset.id;
                this.handleDelete(id);
            }
        });
        this.eventCleanupFns.push(cleanup7);

        this.log.debug('Dashboard events setup complete');
    },

    /**
     * Setup sidebar event listeners
     */
    setupSidebarEvents() {
        // Quick create button
        const quickCreateBtn = this.sidebarContainer.querySelector('#quick-create-btn');
        if (quickCreateBtn) {
            const cleanup = this.dom.on(quickCreateBtn, 'click', () => this.handleQuickCreate());
            this.eventCleanupFns.push(cleanup);
        }

        // Recent items clicks
        const recentList = this.sidebarContainer.querySelector('#recent-items-list');
        if (recentList) {
            const cleanup = this.dom.on(recentList, 'click', (e) => {
                if (e.target.closest('.recent-item')) {
                    const id = e.target.closest('.recent-item').dataset.id;
                    this.handleViewItem(id);
                }
            });
            this.eventCleanupFns.push(cleanup);
        }

        this.log.debug('Sidebar events setup complete');
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // DATA LOADING
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Load dashboard data from API
     */
    async loadDashboardData() {
        this.log.info('Loading dashboard data...');
        this.showLoading(true);
        this.hideError();

        try {
            // Fetch data from API
            const response = await this.api.get('/api/example-modern/items');

            // Update state
            this.data = response.items || [];
            this.filteredData = [...this.data];

            // Render grid
            this.renderDataGrid();

            // Emit event
            this.events.emit('example-modern:data-loaded', {
                count: this.data.length
            });

            this.log.success(`Loaded ${this.data.length} items`);

        } catch (error) {
            this.log.error('Failed to load dashboard data', error);
            this.showError('Failed to load data. Please try again.');
        } finally {
            this.showLoading(false);
        }
    },

    /**
     * Load sidebar summary data
     */
    async loadSidebarData() {
        this.log.info('Loading sidebar data...');

        try {
            const summary = await this.api.get('/api/example-modern/summary');
            this.renderSidebarSummary(summary);
            this.log.success('Sidebar data loaded');

        } catch (error) {
            this.log.error('Failed to load sidebar data', error);
        }
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // BUSINESS LOGIC (CRUD Operations)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Handle create new item
     */
    async handleCreate() {
        this.log.info('Creating new item...');

        try {
            // TODO: Show create modal
            const newItem = {
                name: 'New Item',
                description: 'Description here',
                status: 'pending',
                category: 'type-a'
            };

            const result = await this.api.post('/api/example-modern/create', newItem);

            // Add to local data
            this.data.unshift(result.item);

            // Re-render
            this.renderDataGrid();

            // Emit event
            this.events.emit('example-modern:item-created', result.item);

            this.log.success('Item created successfully');

        } catch (error) {
            this.log.error('Failed to create item', error);
            this.showError('Failed to create item. Please try again.');
        }
    },

    /**
     * Handle edit item
     */
    async handleEdit(itemId) {
        this.log.info(`Editing item: ${itemId}`);

        try {
            // Find item
            const item = this.data.find(i => i.id === itemId);
            if (!item) throw new Error('Item not found');

            // TODO: Show edit modal
            const updates = {
                name: 'Updated Name'
            };

            const result = await this.api.put(`/api/example-modern/update/${itemId}`, updates);

            // Update local data
            const index = this.data.findIndex(i => i.id === itemId);
            if (index !== -1) {
                this.data[index] = result.item;
            }

            // Re-render
            this.renderDataGrid();

            // Emit event
            this.events.emit('example-modern:item-updated', result.item);

            this.log.success('Item updated successfully');

        } catch (error) {
            this.log.error('Failed to update item', error);
            this.showError('Failed to update item. Please try again.');
        }
    },

    /**
     * Handle delete item
     */
    async handleDelete(itemId) {
        this.log.info(`Deleting item: ${itemId}`);

        if (!confirm('Are you sure you want to delete this item?')) {
            return;
        }

        try {
            await this.api.delete(`/api/example-modern/delete/${itemId}`);

            // Remove from local data
            this.data = this.data.filter(i => i.id !== itemId);

            // Re-render
            this.renderDataGrid();

            // Emit event
            this.events.emit('example-modern:item-deleted', { id: itemId });

            this.log.success('Item deleted successfully');

        } catch (error) {
            this.log.error('Failed to delete item', error);
            this.showError('Failed to delete item. Please try again.');
        }
    },

    /**
     * Handle quick create from sidebar
     */
    async handleQuickCreate() {
        this.log.info('Quick creating item from sidebar...');
        // Reuse main create logic
        await this.handleCreate();
    },

    /**
     * Handle view item from sidebar
     */
    handleViewItem(itemId) {
        this.log.info(`Viewing item: ${itemId}`);

        // Find and select item
        this.selectedItem = this.data.find(i => i.id === itemId);

        // Switch to dashboard
        if (typeof switchTab === 'function') {
            switchTab('example-modern');
        }

        // Scroll to item
        const itemElement = this.dashboardContainer.querySelector(`[data-id="${itemId}"]`);
        if (itemElement) {
            this.dom.scrollTo(itemElement);
        }
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // FILTERING & SEARCH
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Apply filters to data
     */
    applyFilters() {
        this.filteredData = this.data.filter(item => {
            // Search filter
            if (this.filters.search) {
                const searchLower = this.filters.search.toLowerCase();
                const matchesSearch =
                    item.name.toLowerCase().includes(searchLower) ||
                    (item.description && item.description.toLowerCase().includes(searchLower));
                if (!matchesSearch) return false;
            }

            // Status filter
            if (this.filters.status !== 'all' && item.status !== this.filters.status) {
                return false;
            }

            // Category filter
            if (this.filters.category !== 'all' && item.category !== this.filters.category) {
                return false;
            }

            return true;
        });

        this.log.debug(`Filtered ${this.filteredData.length} of ${this.data.length} items`);
    },

    /**
     * Clear all filters
     */
    clearFilters() {
        this.log.info('Clearing filters...');

        this.filters = {
            search: '',
            status: 'all',
            category: 'all'
        };

        // Update UI
        const searchInput = this.dashboardContainer.querySelector('#search-input');
        const statusFilter = this.dashboardContainer.querySelector('#status-filter');
        const categoryFilter = this.dashboardContainer.querySelector('#category-filter');

        if (searchInput) searchInput.value = '';
        if (statusFilter) statusFilter.value = 'all';
        if (categoryFilter) categoryFilter.value = 'all';

        // Re-render
        this.renderDataGrid();

        // Save
        this.saveFilters();
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // PERSISTENCE (localStorage)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Load filters from localStorage
     */
    loadFilters() {
        const saved = this.storage.get('example-modern:filters');
        if (saved) {
            this.filters = { ...this.filters, ...saved };
            this.log.debug('Filters loaded from localStorage');
        }
    },

    /**
     * Save filters to localStorage
     */
    saveFilters() {
        this.storage.set('example-modern:filters', this.filters);
        this.log.debug('Filters saved to localStorage');
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // AUTO-REFRESH
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Start auto-refresh interval
     */
    startAutoRefresh() {
        // Refresh every 60 seconds
        this.refreshInterval = setInterval(() => {
            this.log.debug('Auto-refreshing data...');
            this.loadDashboardData();
        }, 60000);

        this.log.debug('Auto-refresh started (60s interval)');
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // UI HELPERS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Show/hide loading state
     */
    showLoading(show) {
        const loadingState = this.dashboardContainer.querySelector('#loading-state');
        if (loadingState) {
            this.dom[show ? 'show' : 'hide'](loadingState);
        }
        this.isLoading = show;
    },

    /**
     * Show error message
     */
    showError(message) {
        const errorState = this.dashboardContainer.querySelector('#error-state');
        const errorMessage = this.dashboardContainer.querySelector('#error-message');
        if (errorState && errorMessage) {
            errorMessage.textContent = message;
            this.dom.show(errorState);
        }
    },

    /**
     * Hide error message
     */
    hideError() {
        const errorState = this.dashboardContainer.querySelector('#error-state');
        if (errorState) {
            this.dom.hide(errorState);
        }
    },

    /**
     * Format date for display
     */
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    }
};
