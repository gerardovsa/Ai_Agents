// BaseModule polyfill (required since module-base.js is not globally loaded)
class BaseModule {
    constructor(moduleId) {
        this.moduleId = moduleId;
        this.manifest = null;
        this.backendUrl = window.API_BASE_URL || 'http://localhost:5001';
        console.log(` BaseModule constructor - moduleId: ${moduleId}`);
    }

    async initialize() {
        console.log(` BaseModule.initialize() called for ${this.moduleId}`);
        try {
            const response = await fetch(`${this.backendUrl}/api/modules/${this.moduleId}`);
            if (response.ok) {
                this.manifest = await response.json();
                console.log(` Manifest loaded for ${this.moduleId}:`, this.manifest);
            }
        } catch (error) {
            console.warn(` Failed to load manifest for ${this.moduleId}:`, error);
        }
    }
}
/**
 * Shopify E-Commerce Module
 * Order management, customer analytics, product performance, and webhook monitoring
 * 
 * @class ShopifyModule
 * @extends BaseModule
 * @created November 6, 2025
 * 
 * Features:
 * - Dashboard with key metrics
 * - Order management and filtering
 * - Customer analytics and segmentation
 * - Product performance tracking
 * - Webhook monitoring
 * - SQL Viewer for direct queries
 */

// ============================================================================
// PLOTLY CHART HELPERS WITH DARK MODE SUPPORT
// ============================================================================

class PlotlyChartHelper {
    /**
     * Get theme-aware colors based on current mode
     */
    static getThemeColors() {
        const isDark = document.body.classList.contains('dark-mode') ||
            document.documentElement.getAttribute('data-theme') === 'dark';

        return {
            isDark: isDark,
            background: 'transparent',
            paper: 'transparent',
            text: isDark ? '#ffffff' : '#1f2937',
            gridColor: isDark ? '#4b5563' : '#e5e7eb',
            lineColor: isDark ? '#6b7280' : '#9ca3af',
            font: {
                family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                size: 12,
                color: isDark ? '#ffffff' : '#1f2937'
            },
            shopifyColors: ['#95bf47', '#5e8e3e', '#7ea73f', '#a5cf57', '#b8d96d', '#6fa83e', '#8bc34a', '#9e9d24'],
            statusColors: {
                success: '#10b981',
                warning: '#f59e0b',
                error: '#ef4444',
                info: '#3b82f6'
            }
        };
    }

    /**
     * Get base layout config with dark mode support
     */
    static getBaseLayout(title, height = 400) {
        const theme = this.getThemeColors();
        return {
            title: {
                text: title,
                font: {
                    ...theme.font,
                    size: 16,
                    weight: 600
                }
            },
            paper_bgcolor: theme.paper,
            plot_bgcolor: theme.background,
            font: theme.font,
            height: height,
            margin: { l: 60, r: 40, t: 60, b: 80 },
            hovermode: 'closest',
            hoverlabel: {
                bgcolor: theme.isDark ? '#1f2937' : 'white',
                bordercolor: theme.gridColor,
                font: theme.font
            },
            xaxis: {
                showgrid: true,
                gridcolor: theme.gridColor,
                linecolor: theme.lineColor,
                tickfont: theme.font,
                titlefont: { ...theme.font, size: 13 }
            },
            yaxis: {
                showgrid: true,
                gridcolor: theme.gridColor,
                linecolor: theme.lineColor,
                tickfont: theme.font,
                titlefont: { ...theme.font, size: 13 }
            },
            legend: {
                font: theme.font,
                bgcolor: 'transparent',
                bordercolor: theme.gridColor,
                borderwidth: 1
            }
        };
    }

    /**
     * Create stacked orders over time chart with product breakdown
     */
    static createOrdersChart(data, containerId) {
        const theme = this.getThemeColors();
        const layout = {
            ...this.getBaseLayout('Orders Over Time - Product Breakdown', 400),
            barmode: 'stack',
            xaxis: {
                ...this.getBaseLayout().xaxis,
                title: 'Date',
                tickangle: -45
            },
            yaxis: {
                ...this.getBaseLayout().yaxis,
                title: 'Number of Orders'
            }
        };

        // If data has product breakdown, create stacked bars
        let traces = [];
        if (data.products && Array.isArray(data.products)) {
            data.products.forEach((product, index) => {
                traces.push({
                    x: data.labels || [],
                    y: product.values || [],
                    name: product.name,
                    type: 'bar',
                    marker: {
                        color: theme.shopifyColors[index % theme.shopifyColors.length],
                        line: {
                            color: theme.isDark ? '#1f2937' : '#ffffff',
                            width: 1
                        }
                    },
                    hovertemplate: '<b>%{fullData.name}</b><br>Date: %{x}<br>Orders: %{y}<extra></extra>'
                });
            });
        } else {
            // Fallback to simple line+markers chart
            traces = [{
                x: data.labels || [],
                y: data.data || [],
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Total Orders',
                marker: {
                    color: theme.shopifyColors[0],
                    size: 8,
                    line: {
                        color: theme.isDark ? '#1f2937' : '#ffffff',
                        width: 2
                    }
                },
                line: {
                    color: theme.shopifyColors[0],
                    width: 3,
                    shape: 'spline'
                },
                hovertemplate: '<b>Orders</b><br>Date: %{x}<br>Count: %{y}<extra></extra>'
            }];
        }

        Plotly.newPlot(containerId, traces, layout, {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['lasso2d', 'select2d']
        });
    }

    /**
     * Create revenue by product stacked bar chart
     */
    static createRevenueChart(data, containerId) {
        const theme = this.getThemeColors();
        const layout = {
            ...this.getBaseLayout('Revenue by Product', 450),
            xaxis: {
                ...this.getBaseLayout().xaxis,
                title: 'Product',
                tickangle: -45
            },
            yaxis: {
                ...this.getBaseLayout().yaxis,
                title: 'Revenue ($)',
                tickprefix: '$'
            }
        };

        const trace = {
            x: data.labels || [],
            y: data.data || [],
            type: 'bar',
            marker: {
                color: theme.shopifyColors[1],
                line: {
                    color: theme.isDark ? '#1f2937' : '#ffffff',
                    width: 1
                },
                opacity: 0.9
            },
            text: data.data ? data.data.map(v => `$${v.toLocaleString(undefined, { minimumFractionDigits: 2 })}`) : [],
            textposition: 'outside',
            textfont: {
                ...theme.font,
                size: 11
            },
            hovertemplate: '<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>'
        };

        Plotly.newPlot(containerId, [trace], layout, {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['lasso2d', 'select2d']
        });
    }

    /**
     * Create customer segments pie chart with dark mode support
     */
    static createSegmentsPieChart(segments, containerId) {
        const theme = this.getThemeColors();
        const layout = {
            ...this.getBaseLayout('Customer Segments', 380),
            showlegend: true
        };

        const data = [{
            values: segments.map(s => s.count),
            labels: segments.map(s => s.segment),
            type: 'pie',
            marker: {
                colors: theme.shopifyColors,
                line: {
                    color: theme.isDark ? '#1f2937' : '#ffffff',
                    width: 2
                }
            },
            textinfo: 'label+percent',
            textfont: theme.font,
            hovertemplate: '<b>%{label}</b><br>Count: %{value:,}<br>Percent: %{percent}<extra></extra>',
            hole: 0.3
        }];

        Plotly.newPlot(containerId, data, layout, {
            responsive: true,
            displayModeBar: true,
            displaylogo: false
        });
    }

    /**
     * Create top products horizontal bar chart
     */
    static createTopProductsChart(products, containerId) {
        const theme = this.getThemeColors();
        const layout = {
            ...this.getBaseLayout('Top Selling Products', 450),
            xaxis: {
                ...this.getBaseLayout().xaxis,
                title: 'Units Sold'
            },
            yaxis: {
                ...this.getBaseLayout().yaxis,
                title: '',
                automargin: true
            }
        };

        const trace = {
            y: products.map(p => p.title).reverse(),
            x: products.map(p => p.total_quantity).reverse(),
            type: 'bar',
            orientation: 'h',
            marker: {
                color: products.map((_, i) => theme.shopifyColors[i % theme.shopifyColors.length]).reverse(),
                line: {
                    color: theme.isDark ? '#1f2937' : '#ffffff',
                    width: 1
                }
            },
            text: products.map(p => p.total_quantity).reverse(),
            textposition: 'outside',
            textfont: {
                ...theme.font,
                size: 11
            },
            hovertemplate: '<b>%{y}</b><br>Units Sold: %{x:,}<extra></extra>'
        };

        Plotly.newPlot(containerId, [trace], layout, {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['lasso2d', 'select2d']
        });
    }

    /**
     * Create webhook status donut chart
     */
    static createWebhookStatusChart(stats, containerId) {
        const theme = this.getThemeColors();
        const layout = {
            ...this.getBaseLayout('Webhook Processing Status', 350),
            showlegend: true
        };

        const data = [{
            values: [stats.processed || 0, stats.pending || 0, stats.errors || 0],
            labels: ['Processed', 'Pending', 'Errors'],
            type: 'pie',
            marker: {
                colors: [theme.statusColors.success, theme.statusColors.warning, theme.statusColors.error],
                line: {
                    color: theme.isDark ? '#1f2937' : '#ffffff',
                    width: 2
                }
            },
            textinfo: 'label+percent',
            textfont: theme.font,
            hovertemplate: '<b>%{label}</b><br>Count: %{value:,}<br>Percent: %{percent}<extra></extra>',
            hole: 0.4
        }];

        Plotly.newPlot(containerId, data, layout, {
            responsive: true,
            displayModeBar: true,
            displaylogo: false
        });
    }
}

// ============================================================================
// SQL VIEWER HELPER
// ============================================================================

class SQLViewerHelper {
    constructor(module) {
        this.module = module;
    }

    /**
     * Render SQL interface
     */
    renderInterface(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = `
            <div class="shopify-sql-viewer-container">
                <div class="shopify-sql-controls">
                    <h3>SQL Query Interface</h3>
                    <div class="shopify-query-examples">
                        <label>Quick Queries:</label>
                        <button class="shopify-quick-query-btn" data-query="SELECT * FROM shopify_orders LIMIT 10">Recent Orders</button>
                        <button class="shopify-quick-query-btn" data-query="SELECT * FROM shopify_line_items LIMIT 10">Line Items</button>
                        <button class="shopify-quick-query-btn" data-query="SELECT * FROM shopify_webhook_events LIMIT 10">Webhook Events</button>
                        <button class="shopify-quick-query-btn" data-query="SELECT name FROM sqlite_master WHERE type='table'">Show Tables</button>
                    </div>
                </div>
                
                <div class="shopify-query-editor">
                    <textarea id="shopify-sql-query" placeholder="Enter SQL query...">SELECT * FROM shopify_orders LIMIT 10</textarea>
                    <button id="shopify-execute-query" class="btn btn-primary">
                        <i class="fas fa-play"></i> Execute Query
                    </button>
                </div>
                
                <div id="shopify-sql-results" class="shopify-sql-results"></div>
            </div>
        `;

        // Attach event listeners
        this.attachListeners();
    }

    /**
     * Attach event listeners
     */
    attachListeners() {
        // Execute query button
        const executeBtn = document.getElementById('shopify-execute-query');
        if (executeBtn) {
            executeBtn.addEventListener('click', () => this.executeQuery());
        }

        // Quick query buttons
        document.querySelectorAll('.shopify-quick-query-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const query = e.target.getAttribute('data-query');
                document.getElementById('shopify-sql-query').value = query;
                this.executeQuery();
            });
        });

        // Enter key in textarea
        const textarea = document.getElementById('shopify-sql-query');
        if (textarea) {
            textarea.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.key === 'Enter') {
                    this.executeQuery();
                }
            });
        }
    }

    /**
     * Execute SQL query
     */
    async executeQuery() {
        const query = document.getElementById('shopify-sql-query').value.trim();
        if (!query) {
            UIComponents.showAlert({
                title: 'Query Required',
                message: 'Please enter a SQL query to execute.',
                variant: 'warning'
            });
            return;
        }

        const resultsDiv = document.getElementById('shopify-sql-results');
        resultsDiv.innerHTML = '<div class="shopify-loading">Executing query...</div>';

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/shopify/sql-query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            const result = await response.json();

            if (result.error) {
                this.displayError(result.error);
            } else {
                this.displayResults(result);
            }
        } catch (error) {
            this.displayError(`Network error: ${error.message}`);
        }
    }

    /**
     * Display query results
     */
    displayResults(result) {
        const resultsDiv = document.getElementById('shopify-sql-results');

        if (!result.results || result.results.length === 0) {
            resultsDiv.innerHTML = `
                <div class="shopify-no-results">
                    <i class="fas fa-info-circle"></i>
                    <p>Query executed successfully. No rows returned.</p>
                    <small>Execution time: ${result.execution_time || 'N/A'}</small>
                </div>
            `;
            return;
        }

        const columns = result.columns || [];
        const rows = result.results || [];

        let html = `
            <div class="shopify-query-info">
                <span><i class="fas fa-check-circle"></i> ${rows.length} rows returned</span>
                <span><i class="fas fa-clock"></i> ${result.execution_time || 'N/A'}</span>
            </div>
            <div class="shopify-table-wrapper">
                <table class="shopify-results-table">
                    <thead>
                        <tr>
                            ${columns.map(col => `<th>${col}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
        `;

        rows.forEach(row => {
            html += '<tr>';
            columns.forEach(col => {
                const value = row[col];
                const displayValue = value === null || value === undefined ? '<em>NULL</em>' : value;
                html += `<td>${displayValue}</td>`;
            });
            html += '</tr>';
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        resultsDiv.innerHTML = html;
    }

    /**
     * Display error message
     */
    displayError(error) {
        const resultsDiv = document.getElementById('shopify-sql-results');
        resultsDiv.innerHTML = `
            <div class="shopify-error-message">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>Query Error:</strong>
                <pre>${error}</pre>
            </div>
        `;
    }
}

// ============================================================================
// MAIN SHOPIFY MODULE
// ============================================================================

class ShopifyModule extends BaseModule {
    constructor(moduleId) {
        super(moduleId);
        this.API_BASE_URL = window.API_BASE_URL || 'http://localhost:5001';
        this.apiEndpoint = `${this.API_BASE_URL}/api/shopify`;
        this.sqlViewer = new SQLViewerHelper(this);
    }

    /**
     * Initialize module
     */
    async initialize() {
        await super.initialize();
        console.log('ShopifyModule: Initialized');

        // Store module instance globally for Tabulator actions
        window.shopifyModule = this;

        this.initializeSubTabs();
    }

    /**
     * Initialize all subtabs
     */
    initializeSubTabs() {
        console.log('[Shopify] Initializing all subtabs...');
        this.initializeDashboardTab();
        this.initializeOrdersTab();
        this.initializeCustomersTab();
        this.initializeProductsTab();
        this.initializeWebhooksTab();
        this.initializeSQLTab();
        console.log('[Shopify] All subtabs initialized');
    }

    /**
     * Handle subtab activation
     */
    onSubTabActivate(subTabId) {
        console.log('[Shopify] Sub-tab activated:', subTabId);
        this.activeSubTab = subTabId;

        // Auto-load data when tabs become visible
        switch (subTabId) {
            case 'dashboard':
                if (!this.dashboardLoaded) {
                    this.loadDashboardData('month');
                    this.dashboardLoaded = true;
                }
                break;
            case 'orders':
                if (!this.ordersLoaded) {
                    this.loadOrdersData();
                    this.ordersLoaded = true;
                }
                break;
            case 'customers':
                if (!this.customersLoaded) {
                    this.loadCustomerData();
                    this.customersLoaded = true;
                }
                break;
            case 'products':
                if (!this.productsLoaded) {
                    this.loadProductData();
                    this.productsLoaded = true;
                }
                break;
            case 'webhooks':
                if (!this.webhooksLoaded) {
                    this.loadWebhookData();
                    this.webhooksLoaded = true;
                }
                break;
            // SQL viewer doesn't need auto-loading
        }
    }

    /**
     * TAB 1: Dashboard
     */
    initializeDashboardTab() {
        const container = this.getSubTabContainer('dashboard');
        if (!container) {
            console.error('[Shopify] Dashboard container not found');
            return;
        }

        container.innerHTML = `
            <div class="shopify-dashboard">
                <div class="shopify-metrics-grid">
                    <div class="shopify-metric-card">
                        <div class="shopify-metric-icon"><i class="fas fa-shopping-cart"></i></div>
                        <div class="shopify-metric-content">
                            <h3 id="shopify-total-orders">Loading...</h3>
                            <p>Total Orders</p>
                        </div>
                    </div>
                    <div class="shopify-metric-card">
                        <div class="shopify-metric-icon"><i class="fas fa-dollar-sign"></i></div>
                        <div class="shopify-metric-content">
                            <h3 id="shopify-total-revenue">Loading...</h3>
                            <p>Total Revenue</p>
                        </div>
                    </div>
                    <div class="shopify-metric-card">
                        <div class="shopify-metric-icon"><i class="fas fa-chart-line"></i></div>
                        <div class="shopify-metric-content">
                            <h3 id="shopify-avg-order-value">Loading...</h3>
                            <p>Avg Order Value</p>
                        </div>
                    </div>
                    <div class="shopify-metric-card">
                        <div class="shopify-metric-icon"><i class="fas fa-calendar-day"></i></div>
                        <div class="shopify-metric-content">
                            <h3 id="shopify-orders-today">Loading...</h3>
                            <p>Orders Today</p>
                        </div>
                    </div>
                </div>

                <div class="shopify-charts-section">
                    <div class="shopify-chart-container">
                        <div id="shopify-orders-over-time-chart"></div>
                    </div>
                    <div class="shopify-chart-container">
                        <div id="shopify-revenue-by-product-chart"></div>
                    </div>
                </div>

                <div class="shopify-period-selector">
                    <label>Period:</label>
                    <button class="shopify-period-btn active" data-period="today">Today</button>
                    <button class="shopify-period-btn" data-period="week">Week</button>
                    <button class="shopify-period-btn" data-period="month">Month</button>
                    <button class="shopify-period-btn" data-period="all">All Time</button>
                </div>
            </div>
        `;

        // Load dashboard data
        this.loadDashboardData('month');

        // Attach period selector listeners
        document.querySelectorAll('.period-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.loadDashboardData(e.target.getAttribute('data-period'));
            });
        });
    }

    /**
     * Load dashboard metrics and charts
     */
    async loadDashboardData(period = 'month') {
        try {
            // Load metrics
            const metricsResponse = await fetch(`${this.apiEndpoint}/dashboard/metrics?period=${period}`);
            const metrics = await metricsResponse.json();

            document.getElementById('shopify-total-orders').textContent = metrics.total_orders || 0;
            document.getElementById('shopify-total-revenue').textContent = `$${(metrics.total_revenue || 0).toFixed(2)}`;
            document.getElementById('shopify-avg-order-value').textContent = `$${(metrics.avg_order_value || 0).toFixed(2)}`;
            document.getElementById('shopify-orders-today').textContent = metrics.orders_today || 0;

            // Load charts
            const ordersChartResponse = await fetch(`${this.apiEndpoint}/dashboard/charts/orders-over-time?days=30`);
            const ordersChartData = await ordersChartResponse.json();
            PlotlyChartHelper.createOrdersChart(ordersChartData, 'shopify-orders-over-time-chart');

            const revenueChartResponse = await fetch(`${this.apiEndpoint}/dashboard/charts/revenue-by-product?days=30`);
            const revenueChartData = await revenueChartResponse.json();
            PlotlyChartHelper.createRevenueChart(revenueChartData, 'shopify-revenue-by-product-chart');

        } catch (error) {
            console.error('Error loading dashboard data:', error);
            document.getElementById('shopify-total-orders').textContent = 'Error';
        }
    }

    /**
     * TAB 2: Orders
     */
    initializeOrdersTab() {
        const container = this.getSubTabContainer('orders');
        if (!container) {
            console.error('[Shopify] Orders container not found');
            return;
        }

        container.innerHTML = `
            <div class="shopify-orders-container">
                <div class="shopify-orders-filters">
                    <label>Days:</label>
                    <select id="shopify-orders-days-filter">
                        <option value="7">Last 7 Days</option>
                        <option value="30" selected>Last 30 Days</option>
                        <option value="90">Last 90 Days</option>
                        <option value="365">Last Year</option>
                    </select>

                    <label>Status:</label>
                    <select id="shopify-orders-status-filter">
                        <option value="">All</option>
                        <option value="paid">Paid</option>
                        <option value="pending">Pending</option>
                        <option value="refunded">Refunded</option>
                    </select>

                    <label>Min Value:</label>
                    <input type="number" id="shopify-orders-min-value" value="0" min="0" step="10">

                    <button id="shopify-apply-orders-filters" class="btn btn-primary">
                        <i class="fas fa-filter"></i> Apply Filters
                    </button>
                </div>

                <div id="shopify-orders-table-container" class="shopify-table-container">
                    <!-- Tabulator table will be initialized here -->
                </div>
            </div>
        `;

        // Load orders
        this.loadOrders();

        // Attach filter listener
        document.getElementById('shopify-apply-orders-filters').addEventListener('click', () => {
            this.loadOrders();
        });
    }

    /**
     * Load orders with filters
     */
    async loadOrders() {
        const days = document.getElementById('shopify-orders-days-filter').value;
        const status = document.getElementById('shopify-orders-status-filter').value;
        const minValue = document.getElementById('shopify-orders-min-value').value;

        try {
            const url = `${this.apiEndpoint}/dashboard/orders?days=${days}&status=${status}&min_value=${minValue}`;
            const response = await fetch(url);
            const data = await response.json();

            if (data.error) {
                console.error('[Shopify] Error loading orders:', data.error);
                if (this.ordersTable) {
                    this.ordersTable.clearData();
                }
                return;
            }

            this.renderOrdersTable(data.orders);

        } catch (error) {
            console.error('[Shopify] Network error loading orders:', error);
            if (this.ordersTable) {
                this.ordersTable.clearData();
            }
        }
    }

    /**
     * Render orders table with Tabulator
     */
    renderOrdersTable(orders) {
        const container = document.getElementById('shopify-orders-table-container');

        // Destroy existing table if it exists
        if (this.ordersTable) {
            this.ordersTable.destroy();
        }

        // Define Tabulator columns with enhanced formatting
        const columns = [
            {
                title: "Order #",
                field: "order_number",
                width: 120,
                headerFilter: "input",
                headerFilterPlaceholder: "Filter...",
                formatter: (cell) => {
                    const value = cell.getValue();
                    return value ? `<strong>#${value}</strong>` : '<span style="color: #999;">N/A</span>';
                }
            },
            {
                title: "Date",
                field: "created_at",
                width: 130,
                sorter: "date",
                sorterParams: { format: "iso" },
                formatter: (cell) => {
                    const value = cell.getValue();
                    if (!value) return '<span style="color: #999;">N/A</span>';
                    const date = new Date(value);
                    return date.toLocaleDateString() + '<br><small style="color: #999;">' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + '</small>';
                }
            },
            {
                title: "Customer",
                field: "customer_name",
                width: 180,
                headerFilter: "input",
                headerFilterPlaceholder: "Search...",
                formatter: (cell) => {
                    const name = cell.getValue();
                    const email = cell.getRow().getData().customer_email;
                    if (!name) return '<span style="color: #999;">Guest</span>';
                    return `<strong>${name}</strong><br><small style="color: #999;">${email || ''}</small>`;
                }
            },
            {
                title: "Total",
                field: "total_price",
                width: 120,
                hozAlign: "right",
                headerHozAlign: "right",
                sorter: "number",
                formatter: (cell) => {
                    const value = cell.getValue() || 0;
                    return `<strong style="color: #95bf47;">$${value.toFixed(2)}</strong>`;
                }
            },
            {
                title: "Financial Status",
                field: "financial_status",
                width: 140,
                hozAlign: "center",
                headerFilter: "select",
                headerFilterParams: {
                    values: { "": "All", "paid": "Paid", "pending": "Pending", "refunded": "Refunded", "partially_refunded": "Partial Refund" }
                },
                formatter: (cell) => {
                    const status = cell.getValue() || 'unknown';
                    const statusColors = {
                        'paid': '#2e7d32',
                        'pending': '#f57c00',
                        'refunded': '#c62828',
                        'partially_refunded': '#e65100',
                        'unknown': '#666'
                    };
                    const color = statusColors[status] || statusColors.unknown;
                    return `<span style="background: ${color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85em; font-weight: 600; text-transform: capitalize;">${status.replace('_', ' ')}</span>`;
                }
            },
            {
                title: "Fulfillment",
                field: "fulfillment_status",
                width: 140,
                hozAlign: "center",
                headerFilter: "select",
                headerFilterParams: {
                    values: { "": "All", "fulfilled": "Fulfilled", "unfulfilled": "Unfulfilled", "partial": "Partial" }
                },
                formatter: (cell) => {
                    const status = cell.getValue() || 'unfulfilled';
                    const statusColors = {
                        'fulfilled': '#2e7d32',
                        'unfulfilled': '#666',
                        'partial': '#f57c00'
                    };
                    const statusIcons = {
                        'fulfilled': '✓',
                        'unfulfilled': '○',
                        'partial': '◐'
                    };
                    const color = statusColors[status] || statusColors.unfulfilled;
                    const icon = statusIcons[status] || '○';
                    return `<span style="background: ${color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85em; font-weight: 600; text-transform: capitalize;">${icon} ${status}</span>`;
                }
            },
            {
                title: "Actions",
                field: "actions",
                width: 100,
                hozAlign: "center",
                headerSort: false,
                formatter: (cell) => {
                    return `<button class="action-btn" onclick="window.shopifyModule.viewOrderDetails(${cell.getRow().getData().id})" title="View Details"><i class="fas fa-eye"></i></button>`;
                }
            }
        ];

        // Initialize Tabulator with professional styling
        this.ordersTable = new Tabulator(container, {
            data: orders || [],
            columns: columns,
            layout: "fitColumns",
            height: "100%",
            pagination: true,
            paginationSize: 25,
            paginationSizeSelector: [10, 25, 50, 100],
            movableColumns: true,
            resizableColumns: true,
            resizableRows: false,
            tooltips: true,
            headerSort: true,
            headerSortTristate: true,
            placeholder: "No orders found. Try adjusting your filters.",
            responsiveLayout: "collapse",
            rowHeight: 60,
            initialSort: [
                { column: "created_at", dir: "desc" }
            ]
        });

        console.log(`[Shopify] Orders table rendered with ${orders?.length || 0} orders`);
    }

    /**
     * TAB 3: Customers
     */
    initializeCustomersTab() {
        const container = this.getSubTabContainer('customers');
        if (!container) {
            console.error('[Shopify] Customers container not found');
            return;
        }

        container.innerHTML = `
            <div class="shopify-customers-container">
                <div class="shopify-charts-row">
                    <div class="shopify-chart-container">
                        <div id="shopify-customer-segments-chart"></div>
                    </div>
                </div>

                <div class="shopify-top-customers-section">
                    <h3>Top Customers</h3>
                    <div id="shopify-top-customers-table"></div>
                </div>
            </div>
        `;

        // Data will be loaded when tab is activated
    }

    /**
     * Load customer data
     */
    async loadCustomerData() {
        try {
            // Load segments
            const segmentsResponse = await fetch(`${this.apiEndpoint}/dashboard/customers/segments?days=90`);
            const segmentsData = await segmentsResponse.json();

            if (segmentsData.segments && segmentsData.segments.length > 0) {
                PlotlyChartHelper.createSegmentsPieChart(segmentsData.segments, 'shopify-customer-segments-chart');
            }

            // Load top customers
            const topResponse = await fetch(`${this.apiEndpoint}/dashboard/customers/top?days=90`);
            const topData = await topResponse.json();

            this.renderTopCustomers(topData.customers);

        } catch (error) {
            console.error('Error loading customer data:', error);
        }
    }

    /**
     * Render top customers table
     */
    renderTopCustomers(customers) {
        const container = document.getElementById('shopify-top-customers-table');

        if (!customers || customers.length === 0) {
            container.innerHTML = '<div class="shopify-no-data">No customer data available</div>';
            return;
        }

        let html = `
            <table class="shopify-data-table">
                <thead>
                    <tr>
                        <th>Customer</th>
                        <th>Email</th>
                        <th>Total Orders</th>
                        <th>Total Spent</th>
                        <th>Avg Order</th>
                    </tr>
                </thead>
                <tbody>
        `;

        customers.forEach(customer => {
            html += `
                <tr>
                    <td>${customer.customer_name || 'N/A'}</td>
                    <td>${customer.email || 'N/A'}</td>
                    <td>${customer.order_count || 0}</td>
                    <td>$${(customer.total_spent || 0).toFixed(2)}</td>
                    <td>$${(customer.avg_order_value || 0).toFixed(2)}</td>
                </tr>
            `;
        });

        html += `
                </tbody>
            </table>
        `;

        container.innerHTML = html;
    }

    /**
     * TAB 4: Products
     */
    initializeProductsTab() {
        const container = this.getSubTabContainer('products');
        if (!container) {
            console.error('[Shopify] Products container not found');
            return;
        }

        container.innerHTML = `
            <div class="shopify-products-container">
                <div class="shopify-chart-container">
                    <div id="shopify-top-products-chart"></div>
                </div>

                <div class="shopify-products-table-section">
                    <h3>Product Catalog</h3>
                    <div id="shopify-products-table"></div>
                </div>
            </div>
        `;

        // Data will be loaded when tab is activated
    }

    /**
     * Load product data
     */
    async loadProductData() {
        try {
            // Load top sellers chart
            const topResponse = await fetch(`${this.apiEndpoint}/dashboard/products/top-sellers?days=30`);
            const topData = await topResponse.json();

            if (topData.products && topData.products.length > 0) {
                PlotlyChartHelper.createTopProductsChart(topData.products, 'shopify-top-products-chart');
            }

            // Load catalog
            const catalogResponse = await fetch(`${this.apiEndpoint}/dashboard/products/catalog?limit=50`);
            const catalogData = await catalogResponse.json();

            this.renderProductCatalog(catalogData.products);

        } catch (error) {
            console.error('Error loading product data:', error);
        }
    }

    /**
     * Render product catalog
     */
    renderProductCatalog(products) {
        const container = document.getElementById('shopify-products-table');

        if (!products || products.length === 0) {
            container.innerHTML = '<div class="shopify-no-data">No products found</div>';
            return;
        }

        let html = `
            <table class="shopify-data-table">
                <thead>
                    <tr>
                        <th>Product ID</th>
                        <th>Title</th>
                        <th>Variant</th>
                        <th>SKU</th>
                        <th>Total Sold</th>
                    </tr>
                </thead>
                <tbody>
        `;

        products.forEach(product => {
            html += `
                <tr>
                    <td>${product.product_id || 'N/A'}</td>
                    <td>${product.title || 'N/A'}</td>
                    <td>${product.variant_title || 'N/A'}</td>
                    <td>${product.sku || 'N/A'}</td>
                    <td>${product.total_quantity || 0}</td>
                </tr>
            `;
        });

        html += `
                </tbody>
            </table>
        `;

        container.innerHTML = html;
    }

    /**
     * TAB 5: Webhooks
     */
    initializeWebhooksTab() {
        const container = this.getSubTabContainer('webhooks');
        if (!container) {
            console.error('[Shopify] Webhooks container not found');
            return;
        }

        container.innerHTML = `
            <div class="shopify-webhooks-container">
                <div class="shopify-webhook-stats">
                    <div id="shopify-webhook-status-chart"></div>
                </div>

                <div class="shopify-webhooks-log-section">
                    <h3>Recent Webhook Events</h3>
                    <button id="shopify-refresh-webhooks" class="btn btn-secondary">
                        <i class="fas fa-sync"></i> Refresh
                    </button>
                    <div id="shopify-webhooks-table"></div>
                </div>
            </div>
        `;

        // Data will be loaded when tab is activated

        // Attach refresh listener
        document.getElementById('shopify-refresh-webhooks').addEventListener('click', () => {
            this.loadWebhookData();
        });
    }

    /**
     * Load webhook data
     */
    async loadWebhookData() {
        try {
            // Load health stats
            const healthResponse = await fetch(`${this.apiEndpoint}/dashboard/webhooks/health`);
            const healthData = await healthResponse.json();

            if (healthData.stats) {
                PlotlyChartHelper.createWebhookStatusChart(healthData.stats, 'shopify-webhook-status-chart');
            }

            // Load event log
            const logResponse = await fetch(`${this.apiEndpoint}/dashboard/webhooks/log?limit=50`);
            const logData = await logResponse.json();

            this.renderWebhookLog(logData.events);

        } catch (error) {
            console.error('Error loading webhook data:', error);
        }
    }

    /**
     * Render webhook log table
     */
    renderWebhookLog(events) {
        const container = document.getElementById('shopify-webhooks-table');

        if (!events || events.length === 0) {
            container.innerHTML = '<div class="shopify-no-data">No webhook events found</div>';
            return;
        }

        let html = `
            <table class="shopify-data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Topic</th>
                        <th>Shopify ID</th>
                        <th>Received</th>
                        <th>Processed</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
        `;

        events.forEach(event => {
            const statusClass = event.processed ? 'success' : (event.error ? 'error' : 'pending');
            const statusText = event.processed ? 'Processed' : (event.error ? 'Error' : 'Pending');

            html += `
                <tr>
                    <td>${event.id}</td>
                    <td>${event.topic || 'N/A'}</td>
                    <td>${event.shopify_id || 'N/A'}</td>
                    <td>${event.received_at ? new Date(event.received_at).toLocaleString() : 'N/A'}</td>
                    <td>${event.processed_at ? new Date(event.processed_at).toLocaleString() : 'N/A'}</td>
                    <td><span class="status-badge status-${statusClass}">${statusText}</span></td>
                </tr>
            `;
        });

        html += `
                </tbody>
            </table>
        `;

        container.innerHTML = html;
    }

    /**
     * View order details (called from Tabulator action button)
     */
    viewOrderDetails(orderId) {
        console.log('[Shopify] Viewing order details:', orderId);
        // TODO: Implement order details modal or navigation
        UIComponents.showAlert({
            title: 'Order Details',
            message: `Order ID: ${orderId}\n\nThis feature will open a detailed order view with:\n• Line items\n• Customer info\n• Shipping details\n• Payment history\n• Fulfillment status`,
            variant: 'info',
            okLabel: 'Got it'
        });
    }

    /**
     * TAB 6: SQL Viewer
     */
    initializeSQLTab() {
        const containerId = `${this.moduleId}-sql-viewer-content`;
        this.sqlViewer.renderInterface(containerId);
    }

    /**
     * Handle subtab activation
     */
    onSubTabActivate(tabId) {
        console.log(`ShopifyModule: Activated tab ${tabId}`);

        // Refresh data when tab is activated
        switch (tabId) {
            case 'dashboard':
                this.loadDashboardData('month');
                break;
            case 'orders':
                this.loadOrders();
                break;
            case 'customers':
                this.loadCustomerData();
                break;
            case 'products':
                this.loadProductData();
                break;
            case 'webhooks':
                this.loadWebhookData();
                break;
        }
    }
}

// Register module
window.ModuleRegistry = window.ModuleRegistry || {};
window.ModuleRegistry['shopify'] = ShopifyModule;

// Expose shopify module instance globally for Tabulator actions
window.shopifyModule = null;

console.log('ShopifyModule: Registered');


// ES6 Export
export default ShopifyModule;
