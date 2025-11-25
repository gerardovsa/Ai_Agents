/**
 * FILE: UI/module_builder/templates/dashboard-module/dashboard-module.js
 * PURPOSE: Dashboard module template with metrics, charts, and data visualization
 * 
 * TEMPLATE TYPE: Analytics/Dashboard
 * USE CASE: Modules requiring metrics display, charts, real-time data visualization
 * 
 * FEATURES:
 * - Metrics cards with KPIs
 * - Interactive charts (Plotly.js)
 * - Auto-refresh capability
 * - Date range filtering
 * - Export functionality
 * - Responsive grid layout
 * 
 * DEPENDENCIES:
 * - ui-components.js (required)
 * - design-tokens.css (required)
 * - plotly.js (required)
 * - modal-system.js (optional)
 * 
 * EXPORTS:
 * - DashboardModule class - Main dashboard class
 * 
 * LAST MODIFIED: 2025-11-12 - Initial template creation
 */

class DashboardModule {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.data = null;
        this.charts = [];
        this.refreshInterval = null;
        this.config = {
            refreshInterval: 300000, // 5 minutes
            autoRefresh: false,
            dateRange: '7d' // 7 days default
        };

        if (!this.container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        this.init();
    }

    /**
     * Initialize the dashboard
     */
    init() {
        this.render();
        this.attachEventListeners();
        this.loadData();
    }

    /**
     * Render the dashboard UI
     */
    render() {
        this.container.innerHTML = `
            <div class="dashboard-module">
                <!-- Header -->
                <div class="dashboard-header">
                    <div class="header-left">
                        <h2 class="dashboard-title">
                            <span class="dashboard-icon">📊</span>
                            Analytics Dashboard
                        </h2>
                        <span class="last-updated" id="lastUpdated">Never</span>
                    </div>
                    <div class="header-right">
                        <select class="select-input" id="dateRangeSelect">
                            <option value="24h">Last 24 Hours</option>
                            <option value="7d" selected>Last 7 Days</option>
                            <option value="30d">Last 30 Days</option>
                            <option value="90d">Last 90 Days</option>
                            <option value="custom">Custom Range</option>
                        </select>
                        <button class="btn-icon" id="refreshBtn" title="Refresh">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                                <path d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z"/>
                                <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z"/>
                            </svg>
                        </button>
                        <button class="btn-icon" id="autoRefreshBtn" title="Auto-Refresh: Off">
                            ⏱️
                        </button>
                        <button class="btn-icon" id="exportBtn" title="Export Data">
                            📥
                        </button>
                        <button class="btn-icon" id="settingsBtn" title="Settings">
                            ⚙️
                        </button>
                    </div>
                </div>
                
                <!-- Metrics Cards -->
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-icon">📈</div>
                        <div class="metric-content">
                            <div class="metric-label">Total Revenue</div>
                            <div class="metric-value" id="totalRevenue">$0</div>
                            <div class="metric-change positive" id="revenueChange">+0%</div>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-icon">👥</div>
                        <div class="metric-content">
                            <div class="metric-label">Total Users</div>
                            <div class="metric-value" id="totalUsers">0</div>
                            <div class="metric-change positive" id="usersChange">+0%</div>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-icon">📦</div>
                        <div class="metric-content">
                            <div class="metric-label">Orders</div>
                            <div class="metric-value" id="totalOrders">0</div>
                            <div class="metric-change positive" id="ordersChange">+0%</div>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-icon">⭐</div>
                        <div class="metric-content">
                            <div class="metric-label">Conversion Rate</div>
                            <div class="metric-value" id="conversionRate">0%</div>
                            <div class="metric-change positive" id="conversionChange">+0%</div>
                        </div>
                    </div>
                </div>
                
                <!-- Charts Grid -->
                <div class="charts-grid">
                    <div class="chart-card">
                        <div class="chart-header">
                            <h3 class="chart-title">Revenue Over Time</h3>
                            <button class="btn-icon btn-sm" onclick="dashboardModule.exportChart('revenueChart')" title="Export Chart">
                                📥
                            </button>
                        </div>
                        <div id="revenueChart" class="chart-container"></div>
                    </div>
                    
                    <div class="chart-card">
                        <div class="chart-header">
                            <h3 class="chart-title">User Growth</h3>
                            <button class="btn-icon btn-sm" onclick="dashboardModule.exportChart('userChart')" title="Export Chart">
                                📥
                            </button>
                        </div>
                        <div id="userChart" class="chart-container"></div>
                    </div>
                    
                    <div class="chart-card">
                        <div class="chart-header">
                            <h3 class="chart-title">Order Status Distribution</h3>
                            <button class="btn-icon btn-sm" onclick="dashboardModule.exportChart('statusChart')" title="Export Chart">
                                📥
                            </button>
                        </div>
                        <div id="statusChart" class="chart-container"></div>
                    </div>
                    
                    <div class="chart-card">
                        <div class="chart-header">
                            <h3 class="chart-title">Top Products</h3>
                            <button class="btn-icon btn-sm" onclick="dashboardModule.exportChart('productsChart')" title="Export Chart">
                                📥
                            </button>
                        </div>
                        <div id="productsChart" class="chart-container"></div>
                    </div>
                </div>
                
                <!-- Footer -->
                <div class="dashboard-footer">
                    <span class="footer-text">Dashboard Module Template v1.0.0</span>
                </div>
            </div>
        `;
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        const dateRangeSelect = this.container.querySelector('#dateRangeSelect');
        const refreshBtn = this.container.querySelector('#refreshBtn');
        const autoRefreshBtn = this.container.querySelector('#autoRefreshBtn');
        const exportBtn = this.container.querySelector('#exportBtn');
        const settingsBtn = this.container.querySelector('#settingsBtn');

        dateRangeSelect?.addEventListener('change', (e) => this.handleDateRangeChange(e.target.value));
        refreshBtn?.addEventListener('click', () => this.handleRefresh());
        autoRefreshBtn?.addEventListener('click', () => this.toggleAutoRefresh());
        exportBtn?.addEventListener('click', () => this.handleExport());
        settingsBtn?.addEventListener('click', () => this.handleSettings());
    }

    /**
     * Load dashboard data
     */
    async loadData() {
        const loader = UIComponents.showLoading({
            title: 'Loading Dashboard',
            message: 'Please wait...'
        });

        try {
            // Simulate API call
            await this.delay(1500);

            // Mock data
            this.data = this.generateMockData();

            this.updateMetrics();
            this.renderCharts();
            this.updateTimestamp();

            loader.hide();
            UIComponents.showToast('Dashboard loaded successfully', 'success');
        } catch (error) {
            loader.hide();
            UIComponents.showAlert({
                title: 'Error',
                message: `Failed to load dashboard: ${error.message}`,
                variant: 'error'
            });
        }
    }

    /**
     * Generate mock data for demonstration
     */
    generateMockData() {
        const days = 30;
        const dates = [];
        const revenue = [];
        const users = [];

        for (let i = days; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            dates.push(date.toISOString().split('T')[0]);
            revenue.push(Math.floor(Math.random() * 10000) + 5000);
            users.push(Math.floor(Math.random() * 500) + 100);
        }

        return {
            metrics: {
                totalRevenue: 245000,
                revenueChange: 12.5,
                totalUsers: 8420,
                usersChange: 8.3,
                totalOrders: 1543,
                ordersChange: 15.2,
                conversionRate: 3.8,
                conversionChange: 0.5
            },
            timeSeries: {
                dates: dates,
                revenue: revenue,
                users: users
            },
            orderStatus: {
                labels: ['Completed', 'Processing', 'Pending', 'Cancelled'],
                values: [1250, 180, 95, 18]
            },
            topProducts: {
                labels: ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'],
                values: [450, 380, 320, 290, 200]
            }
        };
    }

    /**
     * Update metrics cards
     */
    updateMetrics() {
        const { metrics } = this.data;

        this.container.querySelector('#totalRevenue').textContent = `$${metrics.totalRevenue.toLocaleString()}`;
        this.container.querySelector('#revenueChange').textContent = `+${metrics.revenueChange}%`;
        this.container.querySelector('#revenueChange').className = `metric-change ${metrics.revenueChange >= 0 ? 'positive' : 'negative'}`;

        this.container.querySelector('#totalUsers').textContent = metrics.totalUsers.toLocaleString();
        this.container.querySelector('#usersChange').textContent = `+${metrics.usersChange}%`;
        this.container.querySelector('#usersChange').className = `metric-change ${metrics.usersChange >= 0 ? 'positive' : 'negative'}`;

        this.container.querySelector('#totalOrders').textContent = metrics.totalOrders.toLocaleString();
        this.container.querySelector('#ordersChange').textContent = `+${metrics.ordersChange}%`;
        this.container.querySelector('#ordersChange').className = `metric-change ${metrics.ordersChange >= 0 ? 'positive' : 'negative'}`;

        this.container.querySelector('#conversionRate').textContent = `${metrics.conversionRate}%`;
        this.container.querySelector('#conversionChange').textContent = `+${metrics.conversionChange}%`;
        this.container.querySelector('#conversionChange').className = `metric-change ${metrics.conversionChange >= 0 ? 'positive' : 'negative'}`;
    }

    /**
     * Render all charts
     */
    renderCharts() {
        this.renderRevenueChart();
        this.renderUserChart();
        this.renderStatusChart();
        this.renderProductsChart();
    }

    /**
     * Render revenue chart (line chart)
     */
    renderRevenueChart() {
        const { dates, revenue } = this.data.timeSeries;

        const trace = {
            x: dates,
            y: revenue,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Revenue',
            line: { color: '#3b82f6', width: 2 },
            marker: { size: 6 }
        };

        const layout = {
            xaxis: { title: 'Date' },
            yaxis: { title: 'Revenue ($)' },
            margin: { l: 60, r: 40, t: 20, b: 60 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent'
        };

        Plotly.newPlot('revenueChart', [trace], layout, { responsive: true });
        this.charts.push('revenueChart');
    }

    /**
     * Render user growth chart (area chart)
     */
    renderUserChart() {
        const { dates, users } = this.data.timeSeries;

        const trace = {
            x: dates,
            y: users,
            type: 'scatter',
            mode: 'lines',
            fill: 'tozeroy',
            name: 'Users',
            line: { color: '#10b981', width: 2 },
            fillcolor: 'rgba(16, 185, 129, 0.2)'
        };

        const layout = {
            xaxis: { title: 'Date' },
            yaxis: { title: 'Users' },
            margin: { l: 60, r: 40, t: 20, b: 60 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent'
        };

        Plotly.newPlot('userChart', [trace], layout, { responsive: true });
        this.charts.push('userChart');
    }

    /**
     * Render order status chart (pie chart)
     */
    renderStatusChart() {
        const { labels, values } = this.data.orderStatus;

        const trace = {
            labels: labels,
            values: values,
            type: 'pie',
            marker: {
                colors: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444']
            }
        };

        const layout = {
            margin: { l: 20, r: 20, t: 20, b: 20 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            showlegend: true
        };

        Plotly.newPlot('statusChart', [trace], layout, { responsive: true });
        this.charts.push('statusChart');
    }

    /**
     * Render top products chart (horizontal bar chart)
     */
    renderProductsChart() {
        const { labels, values } = this.data.topProducts;

        const trace = {
            x: values,
            y: labels,
            type: 'bar',
            orientation: 'h',
            marker: { color: '#8b5cf6' }
        };

        const layout = {
            xaxis: { title: 'Sales' },
            margin: { l: 100, r: 40, t: 20, b: 60 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent'
        };

        Plotly.newPlot('productsChart', [trace], layout, { responsive: true });
        this.charts.push('productsChart');
    }

    /**
     * Handle date range change
     */
    async handleDateRangeChange(range) {
        if (range === 'custom') {
            UIComponents.showAlert({
                title: 'Custom Date Range',
                message: 'Custom date range picker would open here. Implement with date picker component.',
                variant: 'info'
            });
            return;
        }

        this.config.dateRange = range;
        UIComponents.showToast(`Date range changed to: ${range}`, 'info');
        await this.loadData();
    }

    /**
     * Handle refresh
     */
    async handleRefresh() {
        await this.loadData();
    }

    /**
     * Toggle auto-refresh
     */
    toggleAutoRefresh() {
        const btn = this.container.querySelector('#autoRefreshBtn');
        this.config.autoRefresh = !this.config.autoRefresh;

        if (this.config.autoRefresh) {
            btn.title = 'Auto-Refresh: On';
            btn.style.color = '#10b981';
            this.refreshInterval = setInterval(() => this.loadData(), this.config.refreshInterval);
            UIComponents.showToast('Auto-refresh enabled', 'success');
        } else {
            btn.title = 'Auto-Refresh: Off';
            btn.style.color = '';
            if (this.refreshInterval) {
                clearInterval(this.refreshInterval);
                this.refreshInterval = null;
            }
            UIComponents.showToast('Auto-refresh disabled', 'info');
        }
    }

    /**
     * Handle export
     */
    handleExport() {
        UIComponents.showConfirmation({
            title: 'Export Dashboard Data',
            message: 'Export all dashboard data to CSV?',
            confirmLabel: 'Export',
            onConfirm: () => {
                const csvData = this.generateCSV();
                this.downloadCSV(csvData, `dashboard-export-${Date.now()}.csv`);
                UIComponents.showToast('Data exported successfully', 'success');
            }
        });
    }

    /**
     * Export individual chart
     */
    exportChart(chartId) {
        Plotly.downloadImage(chartId, {
            format: 'png',
            width: 1200,
            height: 600,
            filename: `${chartId}-${Date.now()}`
        });
        UIComponents.showToast('Chart exported successfully', 'success');
    }

    /**
     * Generate CSV from data
     */
    generateCSV() {
        const { timeSeries } = this.data;
        let csv = 'Date,Revenue,Users\n';

        for (let i = 0; i < timeSeries.dates.length; i++) {
            csv += `${timeSeries.dates[i]},${timeSeries.revenue[i]},${timeSeries.users[i]}\n`;
        }

        return csv;
    }

    /**
     * Download CSV file
     */
    downloadCSV(csv, filename) {
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
    }

    /**
     * Handle settings
     */
    handleSettings() {
        UIComponents.showForm({
            title: 'Dashboard Settings',
            size: 'md',
            fields: [
                {
                    name: 'refreshInterval',
                    label: 'Refresh Interval (minutes)',
                    type: 'number',
                    value: this.config.refreshInterval / 60000,
                    min: 1,
                    max: 60
                },
                {
                    name: 'enableNotifications',
                    label: 'Enable Notifications',
                    type: 'checkbox',
                    value: true
                }
            ],
            onSubmit: (formData) => {
                this.config.refreshInterval = formData.refreshInterval * 60000;
                UIComponents.showToast('Settings saved', 'success');
            }
        });
    }

    /**
     * Update timestamp
     */
    updateTimestamp() {
        const now = new Date().toLocaleString();
        this.container.querySelector('#lastUpdated').textContent = `Last updated: ${now}`;
    }

    /**
     * Utility: Delay helper
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Cleanup on destroy
     */
    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        this.charts.forEach(chartId => {
            Plotly.purge(chartId);
        });
    }
}

// Global instance
let dashboardModule;

// Auto-initialize if container exists
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('dashboardModuleContainer');
    if (container) {
        dashboardModule = new DashboardModule('dashboardModuleContainer');
    }
});
