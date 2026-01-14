/**
 * EXAMPLE MODULE - Full-Featured Template
 * Complete implementation demonstrating all UI components and best practices
 * 
 * @class ExampleModule
 * @version 1.0.0
 * @created November 11, 2025
 * 
 * Features Demonstrated:
 * - Metric cards with trends
 * - Data tables with Tabulator
 * - Charts with Plotly
 * - Modals and dialogs
 * - Toast notifications
 * - Forms with validation
 * - Tab navigation
 * - Loading states
 * - Error handling
 * 
 * @requires UIComponents (from ui-components.js)
 * @requires design-tokens.css
 * @requires ui-components.css
 */

class ExampleModule {
    constructor() {
        this.id = 'example-module';
        this.name = 'Example Module';
        this.container = null;
        this.config = null;
        this.activeTab = 'dashboard';

        // Data storage
        this.data = {
            metrics: null,
            tableData: null,
            chartData: null
        };

        // Component instances
        this.tables = {};
        this.charts = {};
        this.modals = {};

        // API configuration
        this.apiEndpoint = '/api/example-module';
        this.backendUrl = 'http://localhost:5001';

        console.log(`[${this.name}] Module created`);
    }

    /**
     * Initialize the module
     * @param {HTMLElement} container - Module container element
     * @param {Object} config - Module configuration from manifest
     */
    async initialize(container, config) {
        console.log(`[${this.name}] Initializing...`);

        this.container = container;
        this.config = config;
        this.activeTab = config.tabs.find(t => t.default)?.id || config.tabs[0].id;

        try {
            // Render module structure
            this.render();

            // Load initial data
            await this.loadData();

            // Initialize active tab
            this.renderTab(this.activeTab);

            console.log(`[${this.name}] Initialized successfully`);

        } catch (error) {
            console.error(`[${this.name}] Initialization failed:`, error);
            this.showError('Failed to initialize module', error.message);
        }
    }

    /**
     * Render module structure with tabs
     */
    render() {
        this.container.innerHTML = `
            <div class="module-wrapper">
                <div class="module-header">
                    <div class="flex items-center gap-4">
                        <h2 class="text-2xl font-bold">
                            <i class="${this.config.icon}"></i>
                            ${this.name}
                        </h2>
                        <p class="text-secondary">${this.config.description}</p>
                    </div>
                    <div class="flex gap-2">
                        ${UIComponents.createButton({
            label: 'Refresh',
            variant: 'secondary',
            icon: 'fas fa-sync-alt',
            size: 'sm',
            onClick: () => this.refresh()
        }).outerHTML}
                        ${UIComponents.createButton({
            label: 'Settings',
            variant: 'ghost',
            icon: 'fas fa-cog',
            size: 'sm',
            onClick: () => this.showSettings()
        }).outerHTML}
                    </div>
                </div>
                
                <!-- Tab Navigation -->
                <div id="${this.id}-tabs"></div>
                
                <!-- Tab Content Area -->
                <div class="module-content" id="${this.id}-content">
                    <!-- Tab content will be rendered here -->
                </div>
            </div>
        `;

        // Initialize tab system
        this.tabSystem = UIComponents.createTabSystem({
            tabs: this.config.tabs,
            activeTab: this.activeTab,
            onTabChange: (tabId) => this.switchTab(tabId),
            container: this.container.querySelector(`#${this.id}-tabs`)
        });
    }

    /**
     * Load data from API
     */
    async loadData() {
        try {
            // Show loading state
            const content = this.container.querySelector(`#${this.id}-content`);
            content.innerHTML = '';
            content.appendChild(UIComponents.createLoadingSpinner({ size: 'lg' }));

            // Fetch data (example endpoints)
            const [metricsRes, tableRes, chartRes] = await Promise.all([
                fetch(`${this.backendUrl}${this.apiEndpoint}/metrics`),
                fetch(`${this.backendUrl}${this.apiEndpoint}/data`),
                fetch(`${this.backendUrl}${this.apiEndpoint}/analytics`)
            ]);

            // Check responses
            if (!metricsRes.ok || !tableRes.ok || !chartRes.ok) {
                throw new Error('Failed to load data from API');
            }

            // Parse data
            this.data.metrics = await metricsRes.json();
            this.data.tableData = await tableRes.json();
            this.data.chartData = await chartRes.json();

        } catch (error) {
            console.error(`[${this.name}] Failed to load data:`, error);

            // Use mock data for demonstration
            this.data.metrics = this.getMockMetrics();
            this.data.tableData = this.getMockTableData();
            this.data.chartData = this.getMockChartData();
        }
    }

    /**
     * Switch to a different tab
     * @param {string} tabId - Tab identifier
     */
    switchTab(tabId) {
        console.log(`[${this.name}] Switching to tab: ${tabId}`);
        this.activeTab = tabId;
        this.renderTab(tabId);
    }

    /**
     * Render specific tab content
     * @param {string} tabId - Tab identifier
     */
    renderTab(tabId) {
        const content = this.container.querySelector(`#${this.id}-content`);

        switch (tabId) {
            case 'dashboard':
                this.renderDashboard(content);
                break;
            case 'data-table':
                this.renderDataTable(content);
                break;
            case 'analytics':
                this.renderAnalytics(content);
                break;
            case 'settings':
                this.renderSettings(content);
                break;
            default:
                content.innerHTML = '<p class="text-muted">Tab not implemented</p>';
        }
    }

    /**
     * Render dashboard tab with metrics
     * @param {HTMLElement} container - Content container
     */
    renderDashboard(container) {
        container.innerHTML = `
            <div class="p-6">
                <h3 class="text-xl font-semibold mb-4">Overview</h3>
                
                <!-- Metrics Row -->
                <div class="grid grid-cols-4 gap-4 mb-6" id="${this.id}-metrics"></div>
                
                <!-- Quick Actions -->
                <div class="mb-6">
                    <h4 class="text-lg font-semibold mb-3">Quick Actions</h4>
                    <div class="flex gap-3">
                        ${UIComponents.createButton({
            label: 'Create New',
            variant: 'primary',
            icon: 'fas fa-plus',
            onClick: () => this.showCreateModal()
        }).outerHTML}
                        ${UIComponents.createButton({
            label: 'Import Data',
            variant: 'secondary',
            icon: 'fas fa-file-import',
            onClick: () => this.showImportModal()
        }).outerHTML}
                        ${UIComponents.createButton({
            label: 'Export Report',
            variant: 'secondary',
            icon: 'fas fa-download',
            onClick: () => this.exportReport()
        }).outerHTML}
                    </div>
                </div>
                
                <!-- Recent Activity -->
                <div>
                    <h4 class="text-lg font-semibold mb-3">Recent Activity</h4>
                    <div id="${this.id}-activity" class="bg-secondary rounded-lg p-4">
                        <p class="text-muted">Loading recent activity...</p>
                    </div>
                </div>
            </div>
        `;

        // Render metric cards
        const metricsContainer = container.querySelector(`#${this.id}-metrics`);
        this.data.metrics.forEach(metric => {
            metricsContainer.appendChild(UIComponents.createMetricCard(metric));
        });
    }

    /**
     * Render data table tab
     * @param {HTMLElement} container - Content container
     */
    renderDataTable(container) {
        container.innerHTML = `
            <div class="p-6">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-semibold">Data Table</h3>
                    <div class="flex gap-2">
                        ${UIComponents.createButton({
            label: 'Add Row',
            variant: 'primary',
            icon: 'fas fa-plus',
            size: 'sm',
            onClick: () => this.addTableRow()
        }).outerHTML}
                        ${UIComponents.createButton({
            label: 'Export CSV',
            variant: 'secondary',
            icon: 'fas fa-file-csv',
            size: 'sm',
            onClick: () => this.exportTableData()
        }).outerHTML}
                    </div>
                </div>
                
                <!-- Table Container -->
                <div id="${this.id}-table" class="bg-secondary rounded-lg"></div>
            </div>
        `;

        // Initialize Tabulator table
        this.initializeTable(container.querySelector(`#${this.id}-table`));
    }

    /**
     * Initialize data table with Tabulator
     * @param {HTMLElement} container - Table container
     */
    initializeTable(container) {
        const columns = [
            { title: 'ID', field: 'id', width: 80 },
            { title: 'Name', field: 'name', editor: 'input' },
            {
                title: 'Status', field: 'status', formatter: (cell) => {
                    const value = cell.getValue();
                    const badge = UIComponents.createBadge({
                        label: value,
                        variant: value === 'Active' ? 'success' : value === 'Pending' ? 'warning' : 'error'
                    });
                    return badge.outerHTML;
                }
            },
            { title: 'Value', field: 'value', formatter: 'money', formatterParams: { precision: 0 } },
            { title: 'Created', field: 'created', formatter: 'datetime', formatterParams: { outputFormat: 'MMM DD, YYYY' } },
            {
                title: 'Actions',
                field: 'actions',
                formatter: () => {
                    return `
                        <div class="flex gap-2">
                            ${UIComponents.createButton({
                        label: '',
                        variant: 'ghost',
                        icon: 'fas fa-edit',
                        size: 'sm',
                        iconPosition: 'only'
                    }).outerHTML}
                            ${UIComponents.createButton({
                        label: '',
                        variant: 'ghost',
                        icon: 'fas fa-trash',
                        size: 'sm',
                        iconPosition: 'only'
                    }).outerHTML}
                        </div>
                    `;
                },
                cellClick: (e, cell) => {
                    if (e.target.closest('.fa-edit')) {
                        this.editRow(cell.getRow().getData());
                    } else if (e.target.closest('.fa-trash')) {
                        this.deleteRow(cell.getRow().getData());
                    }
                }
            }
        ];

        this.tables.main = UIComponents.createDataTable({
            container: container,
            columns: columns,
            data: this.data.tableData
        });
    }

    /**
     * Render analytics tab with charts
     * @param {HTMLElement} container - Content container
     */
    renderAnalytics(container) {
        container.innerHTML = `
            <div class="p-6">
                <h3 class="text-xl font-semibold mb-4">Analytics</h3>
                
                <div class="grid grid-cols-2 gap-6">
                    <div class="bg-secondary rounded-lg p-4">
                        <h4 class="text-lg font-semibold mb-3">Trend Over Time</h4>
                        <div id="${this.id}-chart-1" style="height: 400px;"></div>
                    </div>
                    
                    <div class="bg-secondary rounded-lg p-4">
                        <h4 class="text-lg font-semibold mb-3">Distribution</h4>
                        <div id="${this.id}-chart-2" style="height: 400px;"></div>
                    </div>
                </div>
            </div>
        `;

        // Render charts
        this.renderCharts();
    }

    /**
     * Render charts using Plotly
     */
    renderCharts() {
        // Line chart
        const trace1 = {
            x: this.data.chartData.dates,
            y: this.data.chartData.values,
            type: 'scatter',
            mode: 'lines+markers',
            marker: { color: '#58a6ff' },
            line: { width: 3 }
        };

        const layout1 = {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#f3f4f6' },
            margin: { l: 60, r: 30, t: 30, b: 60 },
            xaxis: { gridcolor: '#30363d' },
            yaxis: { gridcolor: '#30363d' }
        };

        Plotly.newPlot(`${this.id}-chart-1`, [trace1], layout1, { responsive: true });

        // Pie chart
        const trace2 = {
            labels: this.data.chartData.categories,
            values: this.data.chartData.counts,
            type: 'pie',
            marker: {
                colors: ['#3fb950', '#58a6ff', '#d29922', '#f85149']
            }
        };

        const layout2 = {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#f3f4f6' },
            margin: { l: 30, r: 30, t: 30, b: 30 }
        };

        Plotly.newPlot(`${this.id}-chart-2`, [trace2], layout2, { responsive: true });
    }

    /**
     * Render settings tab
     * @param {HTMLElement} container - Content container
     */
    renderSettings(container) {
        container.innerHTML = `
            <div class="p-6">
                <h3 class="text-xl font-semibold mb-4">Settings</h3>
                
                <div class="bg-secondary rounded-lg p-6 max-w-2xl">
                    <form id="${this.id}-settings-form">
                        <div class="mb-4">
                            <label class="block text-sm font-medium mb-2">API Endpoint</label>
                            <input type="text" class="form-input w-full" value="${this.apiEndpoint}" disabled>
                        </div>
                        
                        <div class="mb-4">
                            <label class="block text-sm font-medium mb-2">Refresh Interval (seconds)</label>
                            <input type="number" class="form-input w-full" value="300" min="30" max="3600">
                        </div>
                        
                        <div class="mb-4">
                            <label class="flex items-center gap-2">
                                <input type="checkbox" class="form-checkbox" checked>
                                <span class="text-sm">Enable cache</span>
                            </label>
                        </div>
                        
                        <div class="mb-4">
                            <label class="flex items-center gap-2">
                                <input type="checkbox" class="form-checkbox" checked>
                                <span class="text-sm">Show notifications</span>
                            </label>
                        </div>
                        
                        <div class="flex gap-3 mt-6">
                            ${UIComponents.createButton({
            label: 'Save Changes',
            variant: 'primary',
            type: 'submit'
        }).outerHTML}
                            ${UIComponents.createButton({
            label: 'Reset to Defaults',
            variant: 'secondary',
            onClick: () => this.resetSettings()
        }).outerHTML}
                        </div>
                    </form>
                </div>
            </div>
        `;

        // Form submit handler
        container.querySelector(`#${this.id}-settings-form`).addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveSettings();
        });
    }

    /**
     * Show create modal
     */
    showCreateModal() {
        const modal = UIComponents.createModal({
            title: 'Create New Item',
            size: 'md',
            content: `
                <form id="create-form">
                    <div class="mb-4">
                        <label class="block text-sm font-medium mb-2">Name</label>
                        <input type="text" class="form-input w-full" required>
                    </div>
                    <div class="mb-4">
                        <label class="block text-sm font-medium mb-2">Status</label>
                        <select class="form-select w-full">
                            <option>Active</option>
                            <option>Pending</option>
                            <option>Inactive</option>
                        </select>
                    </div>
                    <div class="mb-4">
                        <label class="block text-sm font-medium mb-2">Value</label>
                        <input type="number" class="form-input w-full" required>
                    </div>
                </form>
            `,
            actions: [
                {
                    label: 'Cancel',
                    variant: 'secondary',
                    handler: () => modal.hide()
                },
                {
                    label: 'Create',
                    variant: 'primary',
                    handler: () => {
                        // Handle form submission
                        UIComponents.showToast({
                            message: 'Item created successfully',
                            variant: 'success'
                        });
                        modal.hide();
                    }
                }
            ]
        });

        modal.show();
        this.modals.create = modal;
    }

    /**
     * Refresh module data
     */
    async refresh() {
        UIComponents.showToast({
            message: 'Refreshing data...',
            variant: 'info',
            duration: 1000
        });

        await this.loadData();
        this.renderTab(this.activeTab);

        UIComponents.showToast({
            message: 'Data refreshed successfully',
            variant: 'success'
        });
    }

    /**
     * Show settings modal
     */
    showSettings() {
        this.tabSystem.setActive('settings');
    }

    /**
     * Show error message
     * @param {string} title - Error title
     * @param {string} message - Error message
     */
    showError(title, message) {
        UIComponents.showToast({
            message: `${title}: ${message}`,
            variant: 'error',
            duration: 5000
        });
    }

    /**
     * Get mock metrics data
     * @returns {Array}
     */
    getMockMetrics() {
        return [
            {
                label: 'Total Items',
                value: 1234,
                format: 'number',
                change: 12,
                trend: 'up',
                icon: 'fas fa-box'
            },
            {
                label: 'Revenue',
                value: 145000,
                format: 'currency',
                change: 8,
                trend: 'up',
                icon: 'fas fa-dollar-sign'
            },
            {
                label: 'Active Users',
                value: 892,
                format: 'number',
                change: -3,
                trend: 'down',
                icon: 'fas fa-users'
            },
            {
                label: 'Success Rate',
                value: 94,
                format: 'percentage',
                change: 2,
                trend: 'up',
                icon: 'fas fa-check-circle'
            }
        ];
    }

    /**
     * Get mock table data
     * @returns {Array}
     */
    getMockTableData() {
        return [
            { id: 1, name: 'Item Alpha', status: 'Active', value: 1250, created: '2025-01-15' },
            { id: 2, name: 'Item Beta', status: 'Pending', value: 2340, created: '2025-02-20' },
            { id: 3, name: 'Item Gamma', status: 'Active', value: 890, created: '2025-03-10' },
            { id: 4, name: 'Item Delta', status: 'Inactive', value: 450, created: '2025-04-05' },
            { id: 5, name: 'Item Epsilon', status: 'Active', value: 3200, created: '2025-05-18' }
        ];
    }

    /**
     * Get mock chart data
     * @returns {Object}
     */
    getMockChartData() {
        return {
            dates: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            values: [120, 145, 132, 168, 190, 175],
            categories: ['Category A', 'Category B', 'Category C', 'Category D'],
            counts: [35, 28, 22, 15]
        };
    }

    /**
     * Destroy module and cleanup
     */
    destroy() {
        console.log(`[${this.name}] Destroying module...`);

        // Destroy tables
        Object.values(this.tables).forEach(table => {
            if (table && table.destroy) table.destroy();
        });

        // Destroy modals
        Object.values(this.modals).forEach(modal => {
            if (modal && modal.destroy) modal.destroy();
        });

        // Clear container
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// Register module globally
if (typeof window !== 'undefined') {
    window.ExampleModule = ExampleModule;
}
