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
 * Xero Accounting Module
 * Financial management for InHouse Print, Publishing, and Signs
 * 
 * @class XeroModule
 * @extends BaseModule
 * @created January 28, 2025
 * 
 * Features:
 * - Dashboard with financial metrics across 3 businesses
 * - Invoice management and tracking
 * - Contact (customer/supplier) management
 * - Payment tracking and reconciliation
 * - Chart of Accounts explorer
 * - Financial reports and analytics
 * - Multi-business support (Print, Publishing, Signs)
 */

// ============================================================================
// XERO MODULE CLASS
// ============================================================================

class XeroModule extends BaseModule {
    constructor() {
        super('xero');
        this.API_BASE_URL = window.API_BASE_URL || 'http://localhost:5001';
        this.currentBusiness = 1; // Default to InHouse Print
        this.data = {
            invoices: [],
            contacts: [],
            payments: [],
            accounts: [],
            stats: {}
        };
        this.tables = {};
        this.charts = {};
        this.subTabs = new Map(); // Initialize Map for sub-tabs
        this.container = null; // Will be set when module is loaded
        // Selection tracking
        this.selectedItems = {
            invoices: new Set(),
            contacts: new Set(),
            payments: new Set(),
            accounts: new Set()
        };
        // Date range filters (default to 3 months)
        this.dateRanges = {
            invoices: 3,
            contacts: 3,
            payments: 3,
            accounts: null // No date filter for accounts
        };
    }

    /**
     * Calculate date range in months
     * @param {number|null} months - Number of months back, or null for all time
     * @returns {string|null} ISO date string (YYYY-MM-DD) or null
     */
    getDateRangeStart(months) {
        if (!months) return null;
        const date = new Date();
        date.setMonth(date.getMonth() - months);
        return date.toISOString().split('T')[0];
    }

    /**
     * Parse Xero date format: /Date(1372291200000+0000)/
     * @param {string} dateStr - Xero date string
     * @returns {Date|null} JavaScript Date object or null
     */
    parseXeroDate(dateStr) {
        if (!dateStr || dateStr === 'undefined' || dateStr === 'null') return null;

        // Handle Xero format: /Date(timestamp+timezone)/
        const match = dateStr.match(/\/Date\((\d+)([\+\-]\d+)?\)\//);
        if (match) {
            const timestamp = parseInt(match[1]);
            return new Date(timestamp);
        }

        // Try standard ISO format
        try {
            const parsed = new Date(dateStr);
            if (!isNaN(parsed.getTime())) return parsed;
        } catch { }

        return null;
    }

    /**
     * Format date for display
     * @param {Date|string} date - Date object or string
     * @returns {string} Formatted date string
     */
    formatDate(date) {
        if (!date || date === 'null' || date === 'undefined') return 'N/A';
        if (typeof date === 'string') {
            date = this.parseXeroDate(date);
        }
        if (!date || isNaN(date.getTime())) return 'Invalid Date';
        return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    }

    /**
     * Initialize module
     */
    async initialize() {
        console.log('Initializing Xero module...');

        try {
            // Call parent initialization
            await super.initialize();

            // CRITICAL FIX DEC 16: Inject base HTML structure first
            this.injectBaseStructure();

            // Create business selector in header
            this.createBusinessSelector();

            // Initialize sub-tabs
            this.initializeSubTabs();

            // CRITICAL FIX DEC 21: Load data in background (don't block initialization)
            // This allows UI to render immediately while data loads
            this.loadDashboard().catch(error => {
                console.error('Failed to load dashboard:', error);
                this.showError('Failed to load dashboard: ' + error.message);
            });

            console.log('✅ Xero module initialized successfully (data loading in background)');
        } catch (error) {
            console.error('Failed to initialize Xero module:', error);
            this.showError('Failed to initialize Xero module: ' + error.message);
        }
    }

    /**
     * Inject base HTML structure into empty container
     */
    injectBaseStructure() {
        if (!this.container) {
            console.error('[Xero] Cannot inject structure - container not set');
            return;
        }

        // SHOW LOADING SPINNER IMMEDIATELY
        this.container.innerHTML = `
            <div class="xero-module-wrapper">
                <div class="module-header" style="display: flex; justify-content: space-between; align-items: center; padding: 20px; background: #0d1117; border-bottom: 1px solid #30363d;">
                    <div class="module-header-left">
                        <h2 style="margin: 0; color: #ffffff; font-size: 24px;">
                            <i class="fas fa-file-invoice-dollar" style="margin-right: 10px; color: #13B5EA;"></i>
                            Xero Accounting
                        </h2>
                    </div>
                    <div class="module-header-right"></div>
                </div>
                <div class="xero-content">
                    <div class="xero-loading-initial" style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 500px; gap: 20px;">
                        <div class="xero-spinner" style="width: 64px; height: 64px; border: 5px solid #30363d; border-top-color: #13B5EA; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                        <p style="color: #8b949e; font-size: 16px; margin: 0; font-weight: 500;">Loading Xero Accounting...</p>
                        <p style="color: #6e7681; font-size: 13px; margin: 0;">Connecting to Xero API and loading data</p>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Create business selector dropdown
     */
    createBusinessSelector() {
        if (!this.container) {
            console.warn('[Xero] Container not set, skipping business selector');
            return;
        }

        const header = this.container.querySelector('.module-header-right');
        if (!header) {
            console.warn('[Xero] Module header not found');
            return;
        }

        const businesses = [
            { id: 1, name: 'InHouse Print', color: '#00509E' },
            { id: 2, name: 'InHouse Publishing', color: '#7B2D26' },
            { id: 3, name: 'InHouse Signs', color: '#F7941D' }
        ];

        const selector = document.createElement('div');
        selector.className = 'xero-business-selector';
        selector.innerHTML = `
            <label for="xero-business-select">
                <i class="fas fa-building"></i> Business:
            </label>
            <select id="xero-business-select" class="xero-select">
                ${businesses.map(b => `
                    <option value="${b.id}" ${b.id === this.currentBusiness ? 'selected' : ''}>
                        ${b.name}
                    </option>
                `).join('')}
            </select>
        `;

        // Insert before refresh button
        const refreshBtn = header.querySelector('[data-action="refresh"]');
        header.insertBefore(selector, refreshBtn);

        // Add change event listener
        const select = selector.querySelector('select');
        select.addEventListener('change', (e) => {
            this.currentBusiness = parseInt(e.target.value);
            this.onBusinessChange();
        });
    }

    /**
     * Handle business change
     */
    async onBusinessChange() {
        console.log(`Business changed to: ${this.currentBusiness}`);

        // Reload current tab data
        const activeTab = this.activeSubTab || 'dashboard';
        switch (activeTab) {
            case 'dashboard':
                await this.loadDashboard();
                break;
            case 'invoices':
                await this.loadInvoices();
                break;
            case 'contacts':
                await this.loadContacts();
                break;
            case 'payments':
                await this.loadPayments();
                break;
            case 'accounts':
                await this.loadAccounts();
                break;
            case 'reports':
                await this.loadReports();
                break;
        }
    }

    /**
     * Initialize sub-tabs
     */
    initializeSubTabs() {
        console.log('Initializing Xero sub-tabs...');

        // REMOVE INITIAL LOADING SPINNER
        const loadingSpinner = this.container.querySelector('.xero-loading-initial');
        if (loadingSpinner) {
            loadingSpinner.remove();
        }

        // CRITICAL FIX DEC 16: Inject sub-tab navigation into content area
        const contentArea = this.container.querySelector('.xero-content');
        if (!contentArea) {
            console.error('[Xero] Content area not found - cannot inject sub-tabs');
            return;
        }

        contentArea.innerHTML = `
            <div class="xero-subtabs-nav" style="display: flex; gap: 10px; padding: 15px 20px; background: #161b22; border-bottom: 1px solid #30363d;">
                <button class="module-subtab-btn active" data-subtab="dashboard">
                    <i class="fas fa-tachometer-alt"></i> Dashboard
                </button>
                <button class="module-subtab-btn" data-subtab="invoices">
                    <i class="fas fa-file-invoice"></i> Invoices
                </button>
                <button class="module-subtab-btn" data-subtab="contacts">
                    <i class="fas fa-address-book"></i> Contacts
                </button>
                <button class="module-subtab-btn" data-subtab="payments">
                    <i class="fas fa-money-bill-wave"></i> Payments
                </button>
                <button class="module-subtab-btn" data-subtab="accounts">
                    <i class="fas fa-list"></i> Accounts
                </button>
                <button class="module-subtab-btn" data-subtab="reports">
                    <i class="fas fa-chart-bar"></i> Reports
                </button>
            </div>
            <div class="xero-tab-content-area" style="padding: 20px;">
                <!-- Tab content will be injected here -->
            </div>
        `;

        // Add click handlers to sub-tab buttons
        const buttons = contentArea.querySelectorAll('.module-subtab-btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                const tabId = btn.getAttribute('data-subtab');
                this.switchSubTab(tabId);
            });
        });

        this.subTabs.set('dashboard', {
            render: () => this.renderDashboard(),
            load: () => this.loadDashboard()
        });

        this.subTabs.set('invoices', {
            render: () => this.renderInvoices(),
            load: () => this.loadInvoices()
        });

        this.subTabs.set('contacts', {
            render: () => this.renderContacts(),
            load: () => this.loadContacts()
        });

        this.subTabs.set('payments', {
            render: () => this.renderPayments(),
            load: () => this.loadPayments()
        });

        this.subTabs.set('accounts', {
            render: () => this.renderAccounts(),
            load: () => this.loadAccounts()
        });

        this.subTabs.set('reports', {
            render: () => this.renderReports(),
            load: () => this.loadReports()
        });

        // Render initial tab
        const defaultTab = this.activeSubTab || 'dashboard';
        this.switchSubTab(defaultTab);
    }

    /**
     * Switch between sub-tabs
     */
    switchSubTab(tabId) {
        console.log(`\n========================================`);
        console.log(`[Xero] 🔄 SWITCHING TO TAB: ${tabId}`);
        console.log(`========================================`);

        // Update active button
        const buttons = this.container.querySelectorAll('.module-subtab-btn');
        console.log(`[Xero] Found ${buttons.length} tab buttons`);
        buttons.forEach(btn => {
            if (btn.getAttribute('data-subtab') === tabId) {
                btn.classList.add('active');
                console.log(`[Xero] ✅ Activated button: ${tabId}`);
            } else {
                btn.classList.remove('active');
            }
        });

        // Store active tab
        this.activeSubTab = tabId;
        console.log(`[Xero] Active tab set to: ${this.activeSubTab}`);

        // Get tab definition and render
        const tab = this.subTabs.get(tabId);
        if (!tab) {
            console.error(`[Xero] ❌ Unknown tab: ${tabId}`);
            console.error(`[Xero] Available tabs:`, Array.from(this.subTabs.keys()));
            return;
        }

        console.log(`[Xero] ✅ Tab definition found for: ${tabId}`);
        console.log(`[Xero] Tab has render function:`, typeof tab.render === 'function');
        console.log(`[Xero] Tab has load function:`, typeof tab.load === 'function');

        // Render tab content
        console.log(`[Xero] 📄 Calling render() for ${tabId}...`);
        tab.render();
        console.log(`[Xero] ✅ Render complete for ${tabId}`);

        // Load tab data
        console.log(`[Xero] 📊 Calling load() for ${tabId}...`);
        tab.load();
        console.log(`[Xero] ✅ Load initiated for ${tabId}`);
        console.log(`========================================\n`);
    }

    // ========================================================================
    // DASHBOARD TAB
    // ========================================================================

    renderDashboard() {
        console.log('[Xero] 📄 renderDashboard() STARTED');
        if (!this.container) {
            console.error('[Xero] ❌ Container not set, cannot render dashboard');
            return;
        }
        console.log('[Xero] ✅ Container found:', this.container.id);

        const contentArea = this.container.querySelector('.xero-tab-content-area');
        if (!contentArea) {
            console.error('[Xero] ❌ Content area (.xero-tab-content-area) not found');
            console.log('[Xero] Container HTML:', this.container.innerHTML.substring(0, 200));
            return;
        }
        console.log('[Xero] ✅ Content area found');

        contentArea.innerHTML = `
            <div class="xero-dashboard">
                <div class="xero-stats-grid">
                    <div class="xero-stat-card" id="xero-stat-revenue">
                        <div class="xero-stat-icon" style="background: #10b981;">
                            <i class="fas fa-dollar-sign"></i>
                        </div>
                        <div class="xero-stat-content">
                            <div class="xero-stat-label">Total Revenue</div>
                            <div class="xero-stat-value">$0.00</div>
                            <div class="xero-stat-change">Loading...</div>
                        </div>
                    </div>

                    <div class="xero-stat-card" id="xero-stat-outstanding">
                        <div class="xero-stat-icon" style="background: #f59e0b;">
                            <i class="fas fa-clock"></i>
                        </div>
                        <div class="xero-stat-content">
                            <div class="xero-stat-label">Outstanding</div>
                            <div class="xero-stat-value">$0.00</div>
                            <div class="xero-stat-change">Loading...</div>
                        </div>
                    </div>

                    <div class="xero-stat-card" id="xero-stat-overdue">
                        <div class="xero-stat-icon" style="background: #ef4444;">
                            <i class="fas fa-exclamation-triangle"></i>
                        </div>
                        <div class="xero-stat-content">
                            <div class="xero-stat-label">Overdue</div>
                            <div class="xero-stat-value">$0.00</div>
                            <div class="xero-stat-change">Loading...</div>
                        </div>
                    </div>

                    <div class="xero-stat-card" id="xero-stat-invoices">
                        <div class="xero-stat-icon" style="background: #3b82f6;">
                            <i class="fas fa-file-invoice"></i>
                        </div>
                        <div class="xero-stat-content">
                            <div class="xero-stat-label">Total Invoices</div>
                            <div class="xero-stat-value">0</div>
                            <div class="xero-stat-change">Loading...</div>
                        </div>
                    </div>
                </div>

                <div class="xero-charts-row">
                    <div class="xero-chart-container">
                        <h3 class="xero-chart-title">Revenue Over Time</h3>
                        <div id="xero-chart-revenue" class="xero-chart"></div>
                    </div>
                    <div class="xero-chart-container">
                        <h3 class="xero-chart-title">Invoice Status Distribution</h3>
                        <div id="xero-chart-status" class="xero-chart"></div>
                    </div>
                </div>

                <div class="xero-charts-row">
                    <div class="xero-chart-container">
                        <h3 class="xero-chart-title">Top Customers by Revenue</h3>
                        <div id="xero-chart-customers" class="xero-chart"></div>
                    </div>
                </div>

                <div class="xero-recent-section">
                    <h3 class="xero-section-title">Recent Invoices</h3>
                    <div id="xero-recent-invoices-table"></div>
                </div>
            </div>
        `;
    }

    async loadDashboard() {
        console.log('Loading Xero dashboard...');
        this.showLoading('Loading dashboard...');

        try {
            // Fetch dashboard data
            const response = await fetch(`${this.API_BASE_URL}/api/xero/dashboard?business_id=${this.currentBusiness}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Failed to load dashboard');
            }

            this.data.stats = data;
            this.updateDashboardStats(data);
            this.createDashboardCharts(data);

            this.hideLoading();
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.showError('Failed to load dashboard: ' + error.message);
        }
    }

    updateDashboardStats(data) {
        console.log('[Xero] Dashboard data received:', data);

        // Data structure: { success, business, stats: {...}, revenue_timeline, status_distribution, top_customers }
        const stats = data.stats || {};

        // If we have valid data, render the dashboard content
        if (stats.total_revenue !== undefined) {
            this.renderDashboardWithData(data);
        } else {
            console.error('[Xero] Invalid dashboard data structure:', data);
        }
    }

    renderDashboardWithData(data) {
        const contentArea = this.container.querySelector('.xero-tab-content-area');
        if (!contentArea) return;

        const stats = data.stats;

        contentArea.innerHTML = `
            <div class=\"xero-dashboard-wrapper\">
                <!-- Financial Overview Section -->
                <div class=\"xero-dashboard-section\" style=\"margin-bottom: 40px;\">
                    <h2 style=\"color: var(--text-primary); font-size: 20px; font-weight: 600; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #30363d;\">
                        <i class=\"fas fa-chart-line\"></i> Financial Overview
                    </h2>
                    <div class=\"xero-metrics-grid\" style=\"display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;\">
                        <div class=\"xero-metric-card\">
                            <div class=\"metric-icon\" style=\"background: #0d419d;\"><i class=\"fas fa-dollar-sign\"></i></div>
                            <div class=\"metric-content\">
                                <div class=\"metric-label\" style=\"color: var(--text-primary);\">Total Revenue (Paid)</div>
                                <div class=\"metric-value\" style=\"color: var(--text-primary);\">${this.formatCurrency(stats.total_revenue)}</div>
                                <div class=\"metric-change\" style=\"color: var(--text-secondary);\">${stats.paid_invoices} paid invoices</div>
                            </div>
                        </div>
                        <div class=\"xero-metric-card\">
                            <div class=\"metric-icon\" style=\"background: #f7941d;\"><i class=\"fas fa-clock\"></i></div>
                            <div class=\"metric-content\">
                                <div class=\"metric-label\" style=\"color: var(--text-primary);\">Outstanding</div>
                                <div class=\"metric-value\" style=\"color: var(--text-primary);\">${this.formatCurrency(stats.outstanding_amount)}</div>
                                <div class=\"metric-change\" style=\"color: var(--text-secondary);\">${stats.outstanding_count} invoices</div>
                            </div>
                        </div>
                        <div class=\"xero-metric-card\">
                            <div class=\"metric-icon\" style=\"background: #f85149;\"><i class=\"fas fa-exclamation-triangle\"></i></div>
                            <div class=\"metric-content\">
                                <div class=\"metric-label\" style=\"color: var(--text-primary);\">Overdue</div>
                                <div class=\"metric-value\" style=\"color: var(--text-primary);\">${this.formatCurrency(stats.overdue_amount)}</div>
                                <div class=\"metric-change negative\" style=\"color: #f85149;\">${stats.overdue_count} invoices</div>
                            </div>
                        </div>
                        <div class=\"xero-metric-card\">
                            <div class=\"metric-icon\" style=\"background: #238636;\"><i class=\"fas fa-file-invoice\"></i></div>
                            <div class=\"metric-content\">
                                <div class=\"metric-label\" style=\"color: var(--text-primary);\">Total Invoices</div>
                                <div class=\"metric-value\" style=\"color: var(--text-primary);\">${stats.total_invoices}</div>
                                <div class=\"metric-change\" style=\"color: var(--text-secondary);\">${stats.paid_invoices} paid</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Revenue Trends Section -->
                <div class=\"xero-dashboard-section\" style=\"margin-bottom: 40px;\">
                    <h2 style=\"color: var(--text-primary); font-size: 20px; font-weight: 600; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #30363d;\">
                        <i class=\"fas fa-chart-area\"></i> Revenue Trends
                    </h2>
                    <div class=\"xero-chart-card\">
                        <h3 style=\"color: var(--text-primary); font-size: 16px; font-weight: 500; margin-bottom: 15px;\"><i class=\"fas fa-chart-line\"></i> Revenue Trend (Last 30 Days)</h3>
                        <div id=\"xero-chart-revenue\" style=\"height: 350px;\"></div>
                    </div>
                </div>

                <!-- Invoice Analytics Section -->
                <div class=\"xero-dashboard-section\" style=\"margin-bottom: 40px;\">
                    <h2 style=\"color: var(--text-primary); font-size: 20px; font-weight: 600; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #30363d;\">
                        <i class=\"fas fa-file-invoice-dollar\"></i> Invoice Analytics
                    </h2>
                    <div class=\"xero-chart-card\">
                        <h3 style=\"color: var(--text-primary); font-size: 16px; font-weight: 500; margin-bottom: 15px;\"><i class=\"fas fa-chart-pie\"></i> Invoice Status Distribution</h3>
                        <div id=\"xero-chart-status\" style=\"height: 350px;\"></div>
                    </div>
                </div>

                <!-- Customer Insights Section -->
                <div class=\"xero-dashboard-section\">
                    <h2 style=\"color: var(--text-primary); font-size: 20px; font-weight: 600; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #30363d;\">
                        <i class=\"fas fa-users\"></i> Customer Insights
                    </h2>
                    <div class=\"xero-chart-card\">
                        <h3 style=\"color: var(--text-primary); font-size: 16px; font-weight: 500; margin-bottom: 15px;\"><i class=\"fas fa-trophy\"></i> Top 10 Customers by Revenue</h3>
                        <div id=\"xero-chart-customers\" style=\"height: 400px;\"></div>
                    </div>
                </div>
            </div>
        `;

        // Render charts
        this.createDashboardCharts(data);
    }

    updateStatCard(id, data) {
        const card = this.container.querySelector(`#xero-stat-${id}`);
        if (!card) return;

        const valueEl = card.querySelector('.xero-stat-value');
        const changeEl = card.querySelector('.xero-stat-change');

        if (valueEl) valueEl.textContent = data.value;
        if (changeEl) changeEl.textContent = data.change;
    }

    createDashboardCharts(data) {
        // Revenue over time chart
        if (data.revenue_timeline) {
            this.createRevenueChart(data.revenue_timeline);
        }

        // Status distribution chart
        if (data.status_distribution) {
            this.createStatusChart(data.status_distribution);
        }

        // Top customers chart
        if (data.top_customers) {
            this.createCustomersChart(data.top_customers);
        }
    }

    createRevenueChart(data) {
        const container = this.container.querySelector('#xero-chart-revenue');
        if (!container) return;

        const trace = {
            x: data.map(d => d.date),
            y: data.map(d => d.amount),
            type: 'scatter',
            mode: 'lines+markers',
            fill: 'tozeroy',
            line: { color: '#13B5EA', width: 3 },
            marker: { color: '#13B5EA', size: 8 }
        };

        const layout = {
            xaxis: {
                title: { text: 'Date', font: { color: '#ffffff' } },
                tickfont: { color: '#ffffff' },
                gridcolor: '#30363d'
            },
            yaxis: {
                title: { text: 'Revenue ($)', font: { color: '#ffffff' } },
                tickfont: { color: '#ffffff' },
                gridcolor: '#30363d'
            },
            margin: { l: 60, r: 40, t: 40, b: 60 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#ffffff' }
        };

        Plotly.newPlot(container, [trace], layout, { responsive: true });
    }

    createStatusChart(data) {
        const container = this.container.querySelector('#xero-chart-status');
        if (!container) return;

        const trace = {
            labels: data.map(d => d.status),
            values: data.map(d => d.count),
            type: 'pie',
            hole: 0.4,
            marker: {
                colors: ['#10b981', '#f59e0b', '#3b82f6', '#ef4444', '#8b5cf6']
            }
        };

        const layout = {
            margin: { l: 40, r: 40, t: 40, b: 40 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#ffffff' },
            legend: { font: { color: '#ffffff' } }
        };

        Plotly.newPlot(container, [trace], layout, { responsive: true });
    }

    createCustomersChart(data) {
        const container = this.container.querySelector('#xero-chart-customers');
        if (!container) return;

        const trace = {
            x: data.map(d => d.amount),
            y: data.map(d => d.name),
            type: 'bar',
            orientation: 'h',
            marker: { color: '#13B5EA' }
        };

        const layout = {
            xaxis: {
                title: { text: 'Revenue ($)', font: { color: '#ffffff' } },
                tickfont: { color: '#ffffff' },
                gridcolor: '#30363d'
            },
            yaxis: {
                title: '',
                tickfont: { color: '#ffffff' },
                automargin: true
            },
            margin: { l: 150, r: 40, t: 40, b: 60 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#ffffff' }
        };

        Plotly.newPlot(container, [trace], layout, { responsive: true });
    }

    // ========================================================================
    // INVOICES TAB
    // ========================================================================

    renderInvoices() {
        console.log('[Xero] 📄 renderInvoices() STARTED');
        const container = this.container.querySelector('.xero-tab-content-area');
        if (!container) {
            console.error('[Xero] ❌ Tab content area not found!');
            return;
        }
        console.log('[Xero] ✅ Container found for invoices');

        container.innerHTML = `
            <div class="xero-invoices">
                <!-- Toolbar with count and actions -->
                <div class="xero-toolbar" style="display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; background: #161b22; border-radius: 6px; margin-bottom: 20px;">
                    <div class="xero-toolbar-left">
                        <span id="xero-invoice-count" style="color: #8b949e; font-size: 14px;">Loading invoices...</span>
                    </div>
                    <div class="xero-toolbar-right" style="display: flex; gap: 10px;">
                        <button class="xero-btn" id="xero-export-all-invoices" style="padding: 8px 16px; background: #238636; border: none; border-radius: 6px; color: white; font-weight: 500; cursor: pointer;">
                            <i class="fas fa-download"></i> Export All
                        </button>
                        <button class="xero-btn xero-btn-primary" id="xero-create-invoice" style="padding: 8px 16px; background: var(--xero-primary); border: none; border-radius: 6px; color: white; font-weight: 500; cursor: pointer;">
                            <i class="fas fa-plus"></i> Create Invoice
                        </button>
                        <button class="xero-btn" id="xero-refresh-invoices" style="padding: 8px 16px; background: #30363d; border: none; border-radius: 6px; color: white; font-weight: 500; cursor: pointer;">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                    </div>
                </div>

                <!-- Date Range Filter Buttons -->
                <div style="margin-bottom: 15px;">
                    <label style="color: #8b949e; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; display: block;">Date Range</label>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        <button class="xero-date-filter" data-months="1" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">1 Month</button>
                        <button class="xero-date-filter" data-months="2" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">2 Months</button>
                        <button class="xero-date-filter active" data-months="3" style="padding: 6px 12px; background: var(--xero-primary); border: 1px solid var(--xero-primary); border-radius: 6px; color: white; font-size: 12px; font-weight: 500; cursor: pointer;">3 Months</button>
                        <button class="xero-date-filter" data-months="6" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">6 Months</button>
                        <button class="xero-date-filter" data-months="9" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">9 Months</button>
                        <button class="xero-date-filter" data-months="12" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">1 Year</button>
                        <button class="xero-date-filter" data-months="24" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">2 Years</button>
                        <button class="xero-date-filter" data-months="36" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">3 Years</button>
                        <button class="xero-date-filter" data-months="" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">All Time</button>
                    </div>
                </div>

                <!-- Reports Section -->
                <div class="xero-reports-section" style="margin-bottom: 15px; border: 1px solid #30363d; border-radius: 6px; overflow: hidden;">
                    <button class="xero-reports-toggle" id="xero-invoices-reports-toggle" style="width: 100%; padding: 12px 16px; background: #161b22; border: none; color: #8b949e; font-size: 13px; font-weight: 600; text-align: left; cursor: pointer; display: flex; justify-content: space-between; align-items: center;">
                        <span><i class="fas fa-chart-bar"></i> Invoice Reports</span>
                        <i class="fas fa-chevron-down"></i>
                    </button>
                    <div class="xero-reports-content" id="xero-invoices-reports-content" style="display: none; padding: 16px; background: #0d1117; border-top: 1px solid #30363d;">
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                            <button class="xero-btn xero-btn-sm" id="xero-show-aged-receivables" style="padding: 8px 12px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 12px; cursor: pointer; text-align: left;">
                                <i class="fas fa-clock" style="margin-right: 6px;"></i>Aged Receivables
                            </button>
                            <button class="xero-btn xero-btn-sm" id="xero-show-sales-summary-inv" style="padding: 8px 12px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 12px; cursor: pointer; text-align: left;">
                                <i class="fas fa-dollar-sign" style="margin-right: 6px;"></i>Sales Summary
                            </button>
                            <button class="xero-btn xero-btn-sm" id="xero-show-overdue-invoices" style="padding: 8px 12px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 12px; cursor: pointer; text-align: left;">
                                <i class="fas fa-exclamation-triangle" style="margin-right: 6px;"></i>Overdue Invoices
                            </button>
                            <button class="xero-btn xero-btn-sm" id="xero-show-revenue-trends" style="padding: 8px 12px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 12px; cursor: pointer; text-align: left;">
                                <i class="fas fa-chart-line" style="margin-right: 6px;"></i>Revenue Trends
                            </button>
                            <button class="xero-btn xero-btn-sm" id="xero-show-invoice-status" style="padding: 8px 12px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 12px; cursor: pointer; text-align: left;">
                                <i class="fas fa-info-circle" style="margin-right: 6px;"></i>Status Summary
                            </button>
                            <button class="xero-btn xero-btn-sm" id="xero-show-invoice-volume" style="padding: 8px 12px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 12px; cursor: pointer; text-align: left;">
                                <i class="fas fa-chart-bar" style="margin-right: 6px;"></i>Volume Analysis
                            </button>
                        </div>
                        <div id="xero-invoices-report-results" style="margin-top: 16px;"></div>
                    </div>
                </div>

                <!-- Status Filter Buttons -->
                <div style="margin-bottom: 15px;">
                    <label style="color: #8b949e; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; display: block;">Status</label>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        <button class="xero-status-filter active" data-status="" style="padding: 6px 12px; background: var(--xero-primary); border: 1px solid var(--xero-primary); border-radius: 6px; color: white; font-size: 12px; font-weight: 500; cursor: pointer;">All</button>
                        <button class="xero-status-filter" data-status="DRAFT" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">Draft</button>
                        <button class="xero-status-filter" data-status="SUBMITTED" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">Submitted</button>
                        <button class="xero-status-filter" data-status="AUTHORISED" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">Authorised</button>
                        <button class="xero-status-filter" data-status="PAID" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">Paid</button>
                        <button class="xero-status-filter" data-status="VOIDED" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">Voided</button>
                    </div>
                </div>

                <!-- Search Bar -->
                <div style="margin-bottom: 20px;">
                    <input type="text" id="xero-invoice-global-search" placeholder="🔍 Search invoices by number, contact, or amount..." style="width: 100%; padding: 12px 16px; background: #161b22; border: 2px solid #30363d; border-radius: 6px; color: #ffffff; font-size: 14px;">
                </div>

                <!-- Bulk Actions Toolbar -->
                <div class="xero-bulk-actions" id="xero-invoice-bulk-actions" style="display: none; padding: 12px 20px; background: #1c2128; border: 1px solid #30363d; border-radius: 6px; margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="xero-selection-count" id="xero-invoice-selection-count" style="color: #ffffff; font-weight: 600;">0 selected</span>
                        <div style="display: flex; gap: 10px;">
                            <button class="xero-btn xero-btn-sm" id="xero-export-selected" style="padding: 6px 12px; background: #238636; border: none; border-radius: 4px; color: white; font-size: 12px; cursor: pointer;">
                                <i class="fas fa-download"></i> Export Selected
                            </button>
                            <button class="xero-btn xero-btn-sm xero-btn-danger" id="xero-delete-selected" style="padding: 6px 12px; background: #f85149; border: none; border-radius: 4px; color: white; font-size: 12px; cursor: pointer;">
                                <i class="fas fa-trash"></i> Delete Selected
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Tabulator Table -->
                <div id="xero-invoices-table"></div>
            </div>
        `;

        // Add event listeners
        const createBtn = container.querySelector('#xero-create-invoice');
        const refreshBtn = container.querySelector('#xero-refresh-invoices');
        const exportAllBtn = container.querySelector('#xero-export-all-invoices');
        const globalSearch = container.querySelector('#xero-invoice-global-search');
        const statusFilters = container.querySelectorAll('.xero-status-filter');
        const exportSelectedBtn = container.querySelector('#xero-export-selected');
        const deleteSelectedBtn = container.querySelector('#xero-delete-selected');

        if (createBtn) createBtn.addEventListener('click', () => this.showCreateInvoiceModal());
        if (refreshBtn) refreshBtn.addEventListener('click', () => this.loadInvoices());
        if (exportAllBtn) exportAllBtn.addEventListener('click', () => this.exportInvoices('xlsx'));

        // Reports toggle
        const reportsToggle = container.querySelector('#xero-invoices-reports-toggle');
        const reportsContent = container.querySelector('#xero-invoices-reports-content');
        if (reportsToggle && reportsContent) {
            reportsToggle.addEventListener('click', () => {
                const isHidden = reportsContent.style.display === 'none';
                reportsContent.style.display = isHidden ? 'block' : 'none';
                const icon = reportsToggle.querySelector('i.fa-chevron-down');
                if (icon) {
                    icon.className = isHidden ? 'fas fa-chevron-up' : 'fas fa-chevron-down';
                }
            });
        }

        // Report buttons
        const agedReceivablesBtn = container.querySelector('#xero-show-aged-receivables');
        const salesSummaryBtn = container.querySelector('#xero-show-sales-summary-inv');
        const overdueInvoicesBtn = container.querySelector('#xero-show-overdue-invoices');
        const revenueTrendsBtn = container.querySelector('#xero-show-revenue-trends');
        const invoiceStatusBtn = container.querySelector('#xero-show-invoice-status');
        const invoiceVolumeBtn = container.querySelector('#xero-show-invoice-volume');

        if (agedReceivablesBtn) agedReceivablesBtn.addEventListener('click', () => this.showAgedReceivables());
        if (salesSummaryBtn) salesSummaryBtn.addEventListener('click', () => this.showSalesSummary());
        if (overdueInvoicesBtn) overdueInvoicesBtn.addEventListener('click', () => this.showOverdueInvoices());
        if (revenueTrendsBtn) revenueTrendsBtn.addEventListener('click', () => this.showRevenueTrends());
        if (invoiceStatusBtn) invoiceStatusBtn.addEventListener('click', () => this.showInvoiceStatus());
        if (invoiceVolumeBtn) invoiceVolumeBtn.addEventListener('click', () => this.showInvoiceVolume());

        // Date range filter buttons
        const dateFilters = container.querySelectorAll('.xero-date-filter');
        dateFilters.forEach(btn => {
            btn.addEventListener('click', () => {
                // Update active state
                dateFilters.forEach(b => {
                    b.style.background = '#30363d';
                    b.style.color = '#8b949e';
                    b.style.borderColor = '#30363d';
                    b.classList.remove('active');
                });
                btn.style.background = 'var(--xero-primary)';
                btn.style.color = 'white';
                btn.style.borderColor = 'var(--xero-primary)';
                btn.classList.add('active');

                // Update date range and reload
                const months = btn.dataset.months;
                this.dateRanges.invoices = months ? parseInt(months) : null;
                this.loadInvoices();
            });
        });

        // Global search across all columns
        if (globalSearch) {
            globalSearch.addEventListener('input', (e) => {
                if (this.tables.invoices) {
                    this.tables.invoices.setFilter([
                        { field: 'invoice_number', type: 'like', value: e.target.value },
                        { field: 'contact_name', type: 'like', value: e.target.value },
                        { field: 'total', type: 'like', value: e.target.value }
                    ]);
                }
            });
        }

        // Status filter buttons
        statusFilters.forEach(btn => {
            btn.addEventListener('click', () => {
                // Update active state
                statusFilters.forEach(b => {
                    b.style.background = '#30363d';
                    b.style.color = '#8b949e';
                    b.classList.remove('active');
                });
                btn.style.background = 'var(--xero-primary)';
                btn.style.color = 'white';
                btn.classList.add('active');

                // Apply filter
                const status = btn.dataset.status;
                if (this.tables.invoices) {
                    if (status) {
                        this.tables.invoices.setFilter('status', '=', status);
                    } else {
                        this.tables.invoices.clearFilter();
                    }
                }
            });
        });

        // Bulk actions
        if (exportSelectedBtn) {
            exportSelectedBtn.addEventListener('click', () => {
                if (this.tables.invoices) {
                    this.tables.invoices.download('xlsx', 'xero_invoices_selected.xlsx', {}, 'selected');
                }
            });
        }

        if (deleteSelectedBtn) {
            deleteSelectedBtn.addEventListener('click', () => this.deleteSelectedInvoices());
        }
    }

    async loadInvoices() {
        console.log('[Xero] 📊 loadInvoices() STARTED');
        console.log('[Xero] Current business ID:', this.currentBusiness);

        // Update count to show loading state
        const countEl = this.container.querySelector('#xero-invoice-count');
        if (countEl) {
            countEl.textContent = 'Loading invoices...';
            console.log('[Xero] ✅ Updated loading text in count element');
        } else {
            console.warn('[Xero] ⚠️ Invoice count element not found');
        }

        try {
            // Build URL with date filter
            let url = `${this.API_BASE_URL}/api/xero/invoices?business_id=${this.currentBusiness}`;
            const fromDate = this.getDateRangeStart(this.dateRanges.invoices);
            if (fromDate) {
                url += `&from_date=${fromDate}`;
            }
            console.log('[Xero] 🌐 Fetching invoices from:', url, `(${this.dateRanges.invoices || 'all'} months)`);

            const response = await fetch(url);
            console.log('[Xero] Response status:', response.status, response.statusText);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('[Xero] Response data:', {
                success: data.success,
                invoiceCount: data.invoices?.length || 0,
                hasError: !!data.error
            });

            if (!data.success) {
                throw new Error(data.error || 'Failed to load invoices');
            }

            this.data.invoices = data.invoices || [];
            console.log(`[Xero] ✅ Loaded ${this.data.invoices.length} invoices into memory`);

            // Create the table
            console.log('[Xero] 📊 Creating invoices table...');
            this.createInvoicesTable();
            console.log('[Xero] ✅ Invoices table created');
        } catch (error) {
            console.error('[Xero] ❌ Error loading invoices:', error);
            console.error('[Xero] Error stack:', error.stack);
            if (countEl) {
                countEl.textContent = 'Error loading invoices';
                countEl.style.color = '#f85149';
            }
        }
    }

    createInvoicesTable() {
        const container = this.container.querySelector('#xero-invoices-table');
        if (!container) return;

        // Update count
        const countEl = this.container.querySelector('#xero-invoice-count');
        if (countEl) {
            countEl.textContent = `Showing ${this.data.invoices.length} invoices`;
        }

        this.tables.invoices = new Tabulator(container, {
            data: this.data.invoices,
            layout: 'fitDataStretch',
            responsiveLayout: 'collapse',
            pagination: 'local',
            paginationSize: 25,
            paginationSizeSelector: [10, 25, 50, 100],
            movableColumns: true,
            resizableColumns: true,
            selectable: true,
            selectableRangeMode: 'click',
            placeholder: 'No invoices found',
            columns: [
                {
                    formatter: 'rowSelection',
                    titleFormatter: 'rowSelection',
                    hozAlign: 'center',
                    headerSort: false,
                    width: 40,
                    cellClick: function (e, cell) {
                        cell.getRow().toggleSelect();
                    }
                },
                {
                    title: 'Invoice #',
                    field: 'invoice_number',
                    width: 130,
                    headerSort: true,
                    headerFilter: 'input',
                    headerFilterPlaceholder: 'Search...',
                    formatter: (cell) => {
                        const value = cell.getValue();
                        return `<span style="font-weight: 600; color: #ffffff;">#${value}</span>`;
                    }
                },
                {
                    title: 'Contact',
                    field: 'contact_name',
                    width: 200,
                    headerSort: true,
                    headerFilter: 'input',
                    headerFilterPlaceholder: 'Search...',
                    formatter: (cell) => `<span style="color: #ffffff;">${cell.getValue()}</span>`
                },
                {
                    title: 'Date',
                    field: 'date',
                    width: 120,
                    headerSort: true,
                    sorter: 'datetime',
                    headerFilter: 'input',
                    headerFilterPlaceholder: 'Search...',
                    formatter: (cell) => `<span style="color: #ffffff;">${this.formatDate(cell.getValue())}</span>`
                },
                {
                    title: 'Due Date',
                    field: 'due_date',
                    width: 120,
                    headerSort: true,
                    sorter: 'datetime',
                    headerFilter: 'input',
                    headerFilterPlaceholder: 'Search...',
                    formatter: (cell) => `<span style="color: #ffffff;">${this.formatDate(cell.getValue())}</span>`
                },
                {
                    title: 'Total',
                    field: 'total',
                    width: 130,
                    headerSort: true,
                    sorter: 'number',
                    hozAlign: 'right',
                    headerFilter: 'input',
                    headerFilterPlaceholder: 'Search...',
                    formatter: (cell) => `<span style="font-weight: 600; color: #ffffff;">${this.formatCurrency(cell.getValue())}</span>`
                },
                {
                    title: 'Amount Due',
                    field: 'amount_due',
                    width: 130,
                    headerSort: true,
                    sorter: 'number',
                    hozAlign: 'right',
                    headerFilter: 'input',
                    headerFilterPlaceholder: 'Search...',
                    formatter: (cell) => `<span style="font-weight: 600; color: #ffffff;">${this.formatCurrency(cell.getValue())}</span>`
                },
                {
                    title: 'Status',
                    field: 'status',
                    width: 130,
                    headerSort: true,
                    headerFilter: 'input',
                    headerFilterPlaceholder: 'Search...',
                    formatter: (cell) => {
                        const status = cell.getValue();
                        const badge = this.getStatusBadge(status);
                        return badge;
                    }
                },
                {
                    title: 'Actions',
                    width: 100,
                    hozAlign: 'center',
                    formatter: () => `
                        <button class="xero-action-btn" title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                    `,
                    cellClick: (e, cell) => {
                        this.showInvoiceDetails(cell.getRow().getData());
                    }
                }
            ]
        });

        // Handle row selection
        this.tables.invoices.on('rowSelectionChanged', (data, rows) => {
            this.selectedItems.invoices = new Set(rows.map(r => r.getData().invoice_id));

            // Update selection count
            const countEl = this.container.querySelector('#xero-invoice-selection-count');
            const bulkActions = this.container.querySelector('#xero-invoice-bulk-actions');

            if (countEl) {
                countEl.textContent = `${rows.length} selected`;
            }

            // Show/hide bulk actions toolbar
            if (bulkActions) {
                bulkActions.style.display = rows.length > 0 ? 'block' : 'none';
            }
        });
    }

    // ========================================================================
    // CONTACTS TAB
    // ========================================================================

    renderContacts() {
        console.log('[Xero] 📄 renderContacts() STARTED');
        const container = this.container.querySelector('.xero-tab-content-area');
        if (!container) {
            console.error('[Xero] ❌ Tab content area not found for contacts!');
            return;
        }
        console.log('[Xero] ✅ Container found for contacts');

        container.innerHTML = `
            <div class="xero-contacts">
                <div class="xero-toolbar">
                    <div class="xero-toolbar-left">
                        <button class="xero-btn xero-btn-primary" id="xero-create-contact">
                            <i class="fas fa-plus"></i> Create Contact
                        </button>
                        <button class="xero-btn" id="xero-refresh-contacts">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                    </div>
                    <div class="xero-toolbar-right">
                        <input type="text" class="xero-search" id="xero-contact-search" 
                               placeholder="Search contacts...">
                    </div>
                </div>

                <!-- Date Range Filter Buttons -->
                <div style="margin-bottom: 15px;">
                    <label style="color: #8b949e; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; display: block;">Date Range</label>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        <button class="xero-date-filter" data-months="1" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">1 Month</button>
                        <button class="xero-date-filter" data-months="2" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">2 Months</button>
                        <button class="xero-date-filter active" data-months="3" style="padding: 6px 12px; background: var(--xero-primary); border: 1px solid var(--xero-primary); border-radius: 6px; color: white; font-size: 12px; font-weight: 500; cursor: pointer;">3 Months</button>
                        <button class="xero-date-filter" data-months="6" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">6 Months</button>
                        <button class="xero-date-filter" data-months="9" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">9 Months</button>
                        <button class="xero-date-filter" data-months="12" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">1 Year</button>
                        <button class="xero-date-filter" data-months="24" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">2 Years</button>
                        <button class="xero-date-filter" data-months="36" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">3 Years</button>
                        <button class="xero-date-filter" data-months="" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">All Time</button>
                    </div>
                </div>

                <!-- Reports Section -->
                <div class="xero-reports-section" style="margin-bottom: 15px; border: 1px solid #30363d; border-radius: 6px; overflow: hidden;">
                    <button class="xero-reports-toggle" id="xero-contacts-reports-toggle" style="width: 100%; padding: 12px 16px; background: #161b22; border: none; color: #8b949e; font-size: 13px; font-weight: 600; text-align: left; cursor: pointer; display: flex; justify-content: space-between; align-items: center;">
                        <span><i class="fas fa-chart-bar"></i> Contact Reports</span>
                        <i class="fas fa-chevron-down"></i>
                    </button>
                    <div class="xero-reports-content" id="xero-contacts-reports-content" style="display: none; padding: 16px; background: #0d1117; border-top: 1px solid #30363d;">
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                            <button class="xero-btn xero-btn-sm" id="xero-show-contact-activity" style="padding: 8px 12px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 12px; cursor: pointer; text-align: left;">
                                <i class="fas fa-history" style="margin-right: 6px;"></i>Contact Activity
                            </button>
                            <button class="xero-btn xero-btn-sm" id="xero-show-inactive-customers" style="padding: 8px 12px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 12px; cursor: pointer; text-align: left;">
                                <i class="fas fa-user-slash" style="margin-right: 6px;"></i>Inactive Customers
                            </button>
                            <button class="xero-btn xero-btn-sm" id="xero-show-customer-ltv" style="padding: 8px 12px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 12px; cursor: pointer; text-align: left;">
                                <i class="fas fa-gem" style="margin-right: 6px;"></i>Customer Lifetime Value
                            </button>
                            <button class="xero-btn xero-btn-sm" id="xero-show-customer-segmentation" style="padding: 8px 12px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 12px; cursor: pointer; text-align: left;">
                                <i class="fas fa-users" style="margin-right: 6px;"></i>Customer Segmentation
                            </button>
                        </div>
                        <div id="xero-contacts-report-results" style="margin-top: 16px;"></div>
                    </div>
                </div>

                <!-- Bulk Actions Toolbar -->
                <div class="xero-bulk-actions" id="xero-contacts-bulk-actions" style="display: none;">
                    <div class="xero-bulk-left">
                        <span class="xero-selection-count" id="xero-contacts-selection-count">0 selected</span>
                    </div>
                    <div class="xero-bulk-right">
                        <div class="xero-btn-group">
                            <button class="xero-btn xero-btn-sm" id="xero-export-contacts-dropdown">
                                <i class="fas fa-download"></i> Export
                                <i class="fas fa-chevron-down"></i>
                            </button>
                            <div class="xero-dropdown-menu" id="xero-export-contacts-menu" style="display: none;">
                                <a href="#" data-format="xlsx">Export to Excel</a>
                                <a href="#" data-format="csv">Export to CSV</a>
                                <a href="#" data-format="pdf">Export to PDF</a>
                            </div>
                        </div>
                        <button class="xero-btn xero-btn-sm xero-btn-danger" id="xero-delete-contacts">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </div>
                <div id="xero-contacts-table"></div>
            </div>
        `;

        // Add event listeners
        const createBtn = container.querySelector('#xero-create-contact');
        const refreshBtn = container.querySelector('#xero-refresh-contacts');
        const searchInput = container.querySelector('#xero-contact-search');

        if (createBtn) createBtn.addEventListener('click', () => this.showCreateContactModal());
        if (refreshBtn) refreshBtn.addEventListener('click', () => this.loadContacts());
        if (searchInput) searchInput.addEventListener('input', (e) => this.filterContacts(e.target.value));

        // Date range filter buttons
        const dateFilters = container.querySelectorAll('.xero-date-filter');
        dateFilters.forEach(btn => {
            btn.addEventListener('click', () => {
                dateFilters.forEach(b => {
                    b.style.background = '#30363d';
                    b.style.color = '#8b949e';
                    b.style.borderColor = '#30363d';
                    b.classList.remove('active');
                });
                btn.style.background = 'var(--xero-primary)';
                btn.style.color = 'white';
                btn.style.borderColor = 'var(--xero-primary)';
                btn.classList.add('active');

                const months = btn.dataset.months;
                this.dateRanges.contacts = months ? parseInt(months) : null;
                this.loadContacts();
            });
        });

        // Bulk actions for contacts
        const exportBtn = container.querySelector('#xero-export-contacts-dropdown');
        const exportMenu = container.querySelector('#xero-export-contacts-menu');
        const deleteBtn = container.querySelector('#xero-delete-contacts');

        if (exportBtn && exportMenu) {
            exportBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                exportMenu.style.display = exportMenu.style.display === 'none' ? 'block' : 'none';
            });

            exportMenu.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    const format = e.target.dataset.format;
                    this.exportContacts(format);
                    exportMenu.style.display = 'none';
                });
            });

            document.addEventListener('click', () => {
                exportMenu.style.display = 'none';
            });
        }

        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => this.deleteSelectedContacts());
        }

        // Contacts reports toggle
        const contactsReportsToggle = container.querySelector('#xero-contacts-reports-toggle');
        const contactsReportsContent = container.querySelector('#xero-contacts-reports-content');
        if (contactsReportsToggle && contactsReportsContent) {
            contactsReportsToggle.addEventListener('click', () => {
                const isHidden = contactsReportsContent.style.display === 'none';
                contactsReportsContent.style.display = isHidden ? 'block' : 'none';
                const icon = contactsReportsToggle.querySelector('i.fa-chevron-down');
                if (icon) {
                    icon.className = isHidden ? 'fas fa-chevron-up' : 'fas fa-chevron-down';
                }
            });
        }

        // Contacts report buttons
        const contactActivityBtn = container.querySelector('#xero-show-contact-activity');
        const inactiveCustomersBtn = container.querySelector('#xero-show-inactive-customers');
        const customerLtvBtn = container.querySelector('#xero-show-customer-ltv');
        const customerSegmentationBtn = container.querySelector('#xero-show-customer-segmentation');

        if (contactActivityBtn) contactActivityBtn.addEventListener('click', () => this.showContactActivity());
        if (inactiveCustomersBtn) inactiveCustomersBtn.addEventListener('click', () => this.showInactiveCustomers());
        if (customerLtvBtn) customerLtvBtn.addEventListener('click', () => this.showCustomerLTV());
        if (customerSegmentationBtn) customerSegmentationBtn.addEventListener('click', () => this.showCustomerSegmentation());
    }

    async loadContacts() {
        console.log('[Xero] 📊 loadContacts() STARTED');
        console.log('[Xero] Current business ID:', this.currentBusiness);

        try {
            let url = `${this.API_BASE_URL}/api/xero/contacts?business_id=${this.currentBusiness}`;

            // Add date range filter if set
            const fromDate = this.getDateRangeStart(this.dateRanges.contacts);
            if (fromDate) {
                url += `&from_date=${fromDate}`;
            }

            console.log('[Xero] 🌐 Fetching contacts from:', url);

            const response = await fetch(url);
            console.log('[Xero] Response status:', response.status, response.statusText);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('[Xero] Response data:', {
                success: data.success,
                contactCount: data.contacts?.length || 0,
                hasError: !!data.error
            });

            if (!data.success) {
                throw new Error(data.error || 'Failed to load contacts');
            }

            this.data.contacts = data.contacts || [];
            console.log(`[Xero] ✅ Loaded ${this.data.contacts.length} contacts into memory`);

            console.log('[Xero] 📊 Creating contacts table...');
            this.createContactsTable();
            console.log('[Xero] ✅ Contacts table created');
        } catch (error) {
            console.error('[Xero] ❌ Error loading contacts:', error);
            console.error('[Xero] Error stack:', error.stack);
        }
    }

    createContactsTable() {
        const container = this.container.querySelector('#xero-contacts-table');
        if (!container) return;

        this.tables.contacts = new Tabulator(container, {
            data: this.data.contacts,
            layout: 'fitDataStretch',
            responsiveLayout: 'collapse',
            pagination: true,
            paginationSize: 50,
            selectable: true,
            selectableRangeMode: 'click',
            columns: [
                {
                    formatter: 'rowSelection',
                    titleFormatter: 'rowSelection',
                    hozAlign: 'center',
                    headerSort: false,
                    width: 40,
                    cellClick: function (e, cell) {
                        cell.getRow().toggleSelect();
                    }
                },
                { title: 'Name', field: 'name', width: 250 },
                { title: 'Email', field: 'email', width: 200 },
                { title: 'Phone', field: 'phone', width: 150 },
                {
                    title: 'Type',
                    field: 'is_customer',
                    width: 120,
                    formatter: (cell) => {
                        const isCustomer = cell.getValue();
                        const row = cell.getRow().getData();
                        const types = [];
                        if (isCustomer) types.push('Customer');
                        if (row.is_supplier) types.push('Supplier');
                        return types.join(', ') || 'N/A';
                    }
                },
                {
                    title: 'Actions',
                    width: 100,
                    hozAlign: 'center',
                    formatter: () => `
                        <button class="xero-action-btn" title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                    `,
                    cellClick: (e, cell) => {
                        this.showContactDetails(cell.getRow().getData());
                    }
                }
            ]
        });

        // Handle row selection
        this.tables.contacts.on('rowSelectionChanged', (data, rows) => {
            this.selectedItems.contacts = new Set(rows.map(r => r.getData().contact_id));
            this.updateSelectionCount('contacts', rows.length);
        });
    }

    // ========================================================================
    // PAYMENTS TAB
    // ========================================================================

    renderPayments() {
        console.log('[Xero] 📄 renderPayments() STARTED');
        const container = this.container.querySelector('.xero-tab-content-area');
        if (!container) {
            console.error('[Xero] ❌ Tab content area not found for payments!');
            return;
        }
        console.log('[Xero] ✅ Container found for payments');

        container.innerHTML = `
            <div class="xero-payments">
                <div class="xero-toolbar">
                    <div class="xero-toolbar-left">
                        <button class="xero-btn" id="xero-refresh-payments">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                    </div>
                    <div class="xero-toolbar-right">
                        <input type="text" class="xero-search" id="xero-payment-search" 
                               placeholder="Search payments...">
                    </div>
                </div>

                <!-- Date Range Filter Buttons -->
                <div style="margin-bottom: 15px;">
                    <label style="color: #8b949e; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; display: block;">Date Range</label>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        <button class="xero-date-filter" data-months="1" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">1 Month</button>
                        <button class="xero-date-filter" data-months="2" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">2 Months</button>
                        <button class="xero-date-filter active" data-months="3" style="padding: 6px 12px; background: var(--xero-primary); border: 1px solid var(--xero-primary); border-radius: 6px; color: white; font-size: 12px; font-weight: 500; cursor: pointer;">3 Months</button>
                        <button class="xero-date-filter" data-months="6" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">6 Months</button>
                        <button class="xero-date-filter" data-months="9" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">9 Months</button>
                        <button class="xero-date-filter" data-months="12" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">1 Year</button>
                        <button class="xero-date-filter" data-months="24" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">2 Years</button>
                        <button class="xero-date-filter" data-months="36" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">3 Years</button>
                        <button class="xero-date-filter" data-months="" style="padding: 6px 12px; background: #30363d; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; font-size: 12px; font-weight: 500; cursor: pointer;">All Time</button>
                    </div>
                </div>

                <div id="xero-payments-table"></div>
            </div>
        `;

        // Add event listeners
        const refreshBtn = container.querySelector('#xero-refresh-payments');
        const searchInput = container.querySelector('#xero-payment-search');

        if (refreshBtn) refreshBtn.addEventListener('click', () => this.loadPayments());
        if (searchInput) searchInput.addEventListener('input', (e) => this.filterPayments(e.target.value));

        // Date range filter buttons
        const dateFilters = container.querySelectorAll('.xero-date-filter');
        dateFilters.forEach(btn => {
            btn.addEventListener('click', () => {
                dateFilters.forEach(b => {
                    b.style.background = '#30363d';
                    b.style.color = '#8b949e';
                    b.style.borderColor = '#30363d';
                    b.classList.remove('active');
                });
                btn.style.background = 'var(--xero-primary)';
                btn.style.color = 'white';
                btn.style.borderColor = 'var(--xero-primary)';
                btn.classList.add('active');

                const months = btn.dataset.months;
                this.dateRanges.payments = months ? parseInt(months) : null;
                this.loadPayments();
            });
        });
    }

    async loadPayments() {
        console.log('[Xero] 📊 loadPayments() STARTED');
        console.log('[Xero] Current business ID:', this.currentBusiness);

        try {
            let url = `${this.API_BASE_URL}/api/xero/payments?business_id=${this.currentBusiness}`;

            // Add date range filter if set
            const fromDate = this.getDateRangeStart(this.dateRanges.payments);
            if (fromDate) {
                url += `&from_date=${fromDate}`;
            }

            console.log('[Xero] 🌐 Fetching payments from:', url);

            const response = await fetch(url);
            console.log('[Xero] Response status:', response.status, response.statusText);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('[Xero] Response data:', {
                success: data.success,
                paymentCount: data.payments?.length || 0,
                hasError: !!data.error
            });

            if (!data.success) {
                throw new Error(data.error || 'Failed to load payments');
            }

            this.data.payments = data.payments || [];
            console.log(`[Xero] ✅ Loaded ${this.data.payments.length} payments into memory`);

            console.log('[Xero] 📊 Creating payments table...');
            this.createPaymentsTable();
            console.log('[Xero] ✅ Payments table created');
        } catch (error) {
            console.error('[Xero] ❌ Error loading payments:', error);
            console.error('[Xero] Error stack:', error.stack);
        }
    }

    createPaymentsTable() {
        const container = this.container.querySelector('#xero-payments-table');
        if (!container) return;

        this.tables.payments = new Tabulator(container, {
            data: this.data.payments,
            layout: 'fitColumns',
            responsiveLayout: 'collapse',
            pagination: 'local',
            paginationSize: 50,
            columns: [
                {
                    title: 'Date',
                    field: 'date',
                    width: 150,
                    formatter: (cell) => this.formatDate(cell.getValue())
                },
                { title: 'Invoice #', field: 'invoice_number', width: 150 },
                {
                    title: 'Amount',
                    field: 'amount',
                    width: 150,
                    hozAlign: 'right',
                    formatter: (cell) => this.formatCurrency(cell.getValue())
                },
                {
                    title: 'Status',
                    field: 'status',
                    width: 120,
                    formatter: (cell) => {
                        const status = cell.getValue();
                        return this.getStatusBadge(status);
                    }
                }
            ]
        });
    }

    // ========================================================================
    // ACCOUNTS TAB
    // ========================================================================

    renderAccounts() {
        console.log('[Xero] 📄 renderAccounts() STARTED');
        const contentArea = this.container.querySelector('.xero-tab-content-area');
        if (!contentArea) {
            console.error('[Xero] ❌ Content area not found for accounts!');
            return;
        }
        console.log('[Xero] ✅ Content area found for accounts');

        contentArea.innerHTML = `
            <div class="xero-accounts">
                <div class="xero-toolbar">
                    <div class="xero-toolbar-left">
                        <button class="xero-btn" id="xero-refresh-accounts">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                    </div>
                    <div class="xero-toolbar-right">
                        <input type="text" class="xero-search" id="xero-account-search" 
                               placeholder="Search accounts...">
                    </div>
                </div>
                <div id="xero-accounts-table"></div>
            </div>
        `;

        console.log('[Xero] ✅ Accounts HTML injected');

        // Add event listeners
        const refreshBtn = contentArea.querySelector('#xero-refresh-accounts');
        const searchInput = contentArea.querySelector('#xero-account-search');

        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadAccounts());
            console.log('[Xero] ✅ Refresh button event listener added');
        }
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.filterAccounts(e.target.value));
            console.log('[Xero] ✅ Search input event listener added');
        }
    }

    async loadAccounts() {
        console.log('[Xero] 📊 loadAccounts() STARTED');
        console.log('[Xero] Current business ID:', this.currentBusiness);

        try {
            const url = `${this.API_BASE_URL}/api/xero/accounts?business_id=${this.currentBusiness}`;
            console.log('[Xero] 🌐 Fetching accounts from:', url);

            const response = await fetch(url);
            console.log('[Xero] Response status:', response.status, response.statusText);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('[Xero] Response data:', {
                success: data.success,
                accountCount: data.accounts?.length || 0,
                hasError: !!data.error
            });

            if (!data.success) {
                throw new Error(data.error || 'Failed to load accounts');
            }

            this.data.accounts = data.accounts || [];
            console.log(`[Xero] ✅ Loaded ${this.data.accounts.length} accounts into memory`);

            console.log('[Xero] 📊 Creating accounts table...');
            this.createAccountsTable();
            console.log('[Xero] ✅ Accounts table created');
        } catch (error) {
            console.error('[Xero] ❌ Error loading accounts:', error);
            console.error('[Xero] Error stack:', error.stack);
        }
    }

    createAccountsTable() {
        const container = this.container.querySelector('#xero-accounts-table');
        if (!container) return;

        this.tables.accounts = new Tabulator(container, {
            data: this.data.accounts,
            layout: 'fitColumns',
            responsiveLayout: 'collapse',
            pagination: 'local',
            paginationSize: 50,
            columns: [
                { title: 'Code', field: 'code', width: 100 },
                { title: 'Name', field: 'name', width: 300 },
                { title: 'Type', field: 'type', width: 150 },
                { title: 'Tax Type', field: 'tax_type', width: 150 }
            ]
        });
    }

    // ========================================================================
    // REPORTS TAB
    // ========================================================================

    renderReports() {
        console.log('[Xero] 📄 renderReports() STARTED');
        const contentArea = this.container.querySelector('.xero-tab-content-area');
        if (!contentArea) {
            console.error('[Xero] ❌ Content area not found for reports!');
            return;
        }
        console.log('[Xero] ✅ Content area found for reports');

        contentArea.innerHTML = `
            <div class="xero-reports" style="padding: 20px;">
                <h2 style="margin-bottom: 24px; color: #c9d1d9;">Multi-Business Reports</h2>
                
                <div class="xero-reports-section" style="margin-bottom: 40px;">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px;">
                        <button class="xero-btn" id="xero-show-business-comparison" style="padding: 16px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 14px; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 12px;">
                            <i class="fas fa-building" style="font-size: 24px; color: var(--xero-primary);"></i>
                            <div>
                                <div style="font-weight: 600;">Business Comparison</div>
                                <div style="font-size: 12px; color: #8b949e;">Compare performance across all businesses</div>
                            </div>
                        </button>
                        <button class="xero-btn" id="xero-show-consolidated-revenue" style="padding: 16px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 14px; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 12px;">
                            <i class="fas fa-chart-pie" style="font-size: 24px; color: var(--xero-primary);"></i>
                            <div>
                                <div style="font-weight: 600;">Consolidated Revenue</div>
                                <div style="font-size: 12px; color: #8b949e;">Total revenue across all businesses</div>
                            </div>
                        </button>
                        <button class="xero-btn" id="xero-show-customer-overlap" style="padding: 16px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 14px; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 12px;">
                            <i class="fas fa-exchange-alt" style="font-size: 24px; color: var(--xero-primary);"></i>
                            <div>
                                <div style="font-weight: 600;">Customer Overlap</div>
                                <div style="font-size: 12px; color: #8b949e;">Customers using multiple businesses</div>
                            </div>
                        </button>
                    </div>
                </div>
                
                <h2 style="margin-bottom: 24px; color: #c9d1d9;">Advanced Analytics</h2>
                
                <div class="xero-reports-section">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px;">
                        <button class="xero-btn" id="xero-show-revenue-by-product" style="padding: 16px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 14px; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 12px;">
                            <i class="fas fa-box" style="font-size: 24px; color: var(--xero-primary);"></i>
                            <div>
                                <div style="font-weight: 600;">Revenue by Product</div>
                                <div style="font-size: 12px; color: #8b949e;">Product/service revenue breakdown</div>
                            </div>
                        </button>
                        <button class="xero-btn" id="xero-show-seasonality" style="padding: 16px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 14px; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 12px;">
                            <i class="fas fa-calendar-alt" style="font-size: 24px; color: var(--xero-primary);"></i>
                            <div>
                                <div style="font-weight: 600;">Seasonality Analysis</div>
                                <div style="font-size: 12px; color: #8b949e;">Monthly patterns and trends</div>
                            </div>
                        </button>
                        <button class="xero-btn" id="xero-show-forecast" style="padding: 16px; background: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 14px; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 12px;">
                            <i class="fas fa-chart-line" style="font-size: 24px; color: var(--xero-primary);"></i>
                            <div>
                                <div style="font-weight: 600;">Revenue Forecast</div>
                                <div style="font-size: 12px; color: #8b949e;">Predictive revenue projections</div>
                            </div>
                        </button>
                    </div>
                </div>
                
                <div id="xero-reports-results" style="margin-top: 30px;"></div>
            </div>
        `;

        // Add event listeners
        const businessComparisonBtn = contentArea.querySelector('#xero-show-business-comparison');
        const consolidatedRevenueBtn = contentArea.querySelector('#xero-show-consolidated-revenue');
        const customerOverlapBtn = contentArea.querySelector('#xero-show-customer-overlap');
        const revenueByProductBtn = contentArea.querySelector('#xero-show-revenue-by-product');
        const seasonalityBtn = contentArea.querySelector('#xero-show-seasonality');
        const forecastBtn = contentArea.querySelector('#xero-show-forecast');

        if (businessComparisonBtn) businessComparisonBtn.addEventListener('click', () => this.showBusinessComparison());
        if (consolidatedRevenueBtn) consolidatedRevenueBtn.addEventListener('click', () => this.showConsolidatedRevenue());
        if (customerOverlapBtn) customerOverlapBtn.addEventListener('click', () => this.showCustomerOverlap());
        if (revenueByProductBtn) revenueByProductBtn.addEventListener('click', () => this.showRevenueByProduct());
        if (seasonalityBtn) seasonalityBtn.addEventListener('click', () => this.showSeasonality());
        if (forecastBtn) forecastBtn.addEventListener('click', () => this.showForecast());
        console.log('[Xero] ✅ Reports HTML injected');
    }

    async loadReports() {
        console.log('[Xero] 📊 loadReports() STARTED');
        console.log('[Xero] Reports tab - no data to load yet');
        // TODO: Implement reports
    }

    // ========================================================================
    // UTILITY METHODS
    // ========================================================================

    formatCurrency(amount) {
        if (amount === null || amount === undefined) return '$0.00';
        return new Intl.NumberFormat('en-AU', {
            style: 'currency',
            currency: 'AUD'
        }).format(amount);
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-AU', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    getStatusBadge(status) {
        const colors = {
            'PAID': 'success',
            'AUTHORISED': 'info',
            'DRAFT': 'warning',
            'SUBMITTED': 'info',
            'VOIDED': 'danger'
        };
        const color = colors[status] || 'secondary';
        return `<span class="xero-badge xero-badge-${color}">${status}</span>`;
    }

    showLoading(message = 'Loading...') {
        const contentArea = this.container?.querySelector('.xero-tab-content-area');
        if (!contentArea) return;

        contentArea.innerHTML = `
            <div class="xero-loading-container" style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 400px; gap: 20px;">
                <div class="xero-spinner" style="width: 48px; height: 48px; border: 4px solid #30363d; border-top-color: #13B5EA; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                <p style="color: #8b949e; font-size: 14px; margin: 0;">${message}</p>
            </div>
        `;
    }

    hideLoading() {
        const loading = this.container?.querySelector('.xero-loading-container');
        if (loading) {
            loading.remove();
        }
    }

    showError(message) {
        console.error('[Xero Error]', message);
        const contentArea = this.container?.querySelector('.xero-tab-content-area');
        if (!contentArea) return;

        contentArea.innerHTML = `
            <div class="xero-error-container" style="padding: 40px; text-align: center;">
                <div style="max-width: 500px; margin: 0 auto; padding: 30px; background: #1c1f26; border: 1px solid #f85149; border-radius: 6px;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 48px; color: #f85149; margin-bottom: 20px;"></i>
                    <h3 style="color: #ffffff; margin-bottom: 10px;">Error Loading Data</h3>
                    <p style="color: #8b949e; margin-bottom: 20px;">${message}</p>
                    <button class="xero-btn xero-btn-primary" onclick="location.reload()">
                        <i class="fas fa-redo"></i> Retry
                    </button>
                </div>
            </div>
        `;
    }

    showInvoiceDetails(invoice) {
        console.log('Showing invoice details:', invoice);
        // TODO: Implement invoice details modal
    }

    showContactDetails(contact) {
        console.log('Showing contact details:', contact);
        // TODO: Implement contact details modal
    }

    showCreateInvoiceModal() {
        console.log('Opening create invoice modal');
        // TODO: Implement create invoice modal
    }

    showCreateContactModal() {
        console.log('Opening create contact modal');
        // TODO: Implement create contact modal
    }

    filterInvoices(searchTerm) {
        if (this.tables.invoices) {
            this.tables.invoices.setFilter([
                { field: 'invoice_number', type: 'like', value: searchTerm },
                { field: 'contact_name', type: 'like', value: searchTerm }
            ]);
        }
    }

    filterInvoicesByStatus(status) {
        if (this.tables.invoices) {
            if (status) {
                this.tables.invoices.setFilter('status', '=', status);
            } else {
                this.tables.invoices.clearFilter();
            }
        }
    }

    filterContacts(searchTerm) {
        if (this.tables.contacts) {
            this.tables.contacts.setFilter([
                { field: 'name', type: 'like', value: searchTerm },
                { field: 'email', type: 'like', value: searchTerm }
            ]);
        }
    }

    filterPayments(searchTerm) {
        if (this.tables.payments) {
            this.tables.payments.setFilter('invoice_number', 'like', searchTerm);
        }
    }

    filterAccounts(searchTerm) {
        if (this.tables.accounts) {
            this.tables.accounts.setFilter([
                { field: 'code', type: 'like', value: searchTerm },
                { field: 'name', type: 'like', value: searchTerm }
            ]);
        }
    }

    // ========================================================================
    // BULK ACTIONS
    // ========================================================================

    updateSelectionCount(type, count) {
        const countElement = document.getElementById(`xero-${type}-selection-count`);
        const bulkActionsBar = document.getElementById(`xero-${type}-bulk-actions`);

        if (countElement) {
            countElement.textContent = `${count} selected`;
        }

        if (bulkActionsBar) {
            bulkActionsBar.style.display = count > 0 ? 'flex' : 'none';
        }
    }

    exportInvoices(format) {
        if (!this.tables.invoices) return;

        const filename = `xero_invoices_${Date.now()}`;

        try {
            switch (format) {
                case 'xlsx':
                    this.tables.invoices.download('xlsx', `${filename}.xlsx`, {
                        sheetName: 'Invoices'
                    });
                    break;
                case 'csv':
                    this.tables.invoices.download('csv', `${filename}.csv`);
                    break;
                case 'pdf':
                    this.tables.invoices.download('pdf', `${filename}.pdf`, {
                        orientation: 'landscape',
                        title: 'Xero Invoices'
                    });
                    break;
            }
            console.log(`Exported ${this.selectedItems.invoices.size} invoices as ${format}`);
        } catch (error) {
            console.error('Export failed:', error);
            this.showError('Export failed', error.message, 'error');
        }
    }

    exportContacts(format) {
        if (!this.tables.contacts) return;

        const filename = `xero_contacts_${Date.now()}`;

        try {
            switch (format) {
                case 'xlsx':
                    this.tables.contacts.download('xlsx', `${filename}.xlsx`, {
                        sheetName: 'Contacts'
                    });
                    break;
                case 'csv':
                    this.tables.contacts.download('csv', `${filename}.csv`);
                    break;
                case 'pdf':
                    this.tables.contacts.download('pdf', `${filename}.pdf`, {
                        orientation: 'landscape',
                        title: 'Xero Contacts'
                    });
                    break;
            }
            console.log(`Exported ${this.selectedItems.contacts.size} contacts as ${format}`);
        } catch (error) {
            console.error('Export failed:', error);
            this.showError('Export failed', error.message, 'error');
        }
    }

    deleteSelectedInvoices() {
        const count = this.selectedItems.invoices.size;
        if (count === 0) return;

        if (confirm(`Are you sure you want to delete ${count} invoice(s)?`)) {
            console.log('Deleting invoices:', Array.from(this.selectedItems.invoices));
            // TODO: Implement actual delete API call
            this.showWarning(`Delete functionality will be implemented in next update. Would delete ${count} invoices.`);
        }
    }

    deleteSelectedContacts() {
        const count = this.selectedItems.contacts.size;
        if (count === 0) return;

        if (confirm(`Are you sure you want to delete ${count} contact(s)?`)) {
            console.log('Deleting contacts:', Array.from(this.selectedItems.contacts));
            // TODO: Implement actual delete API call
            this.showWarning(`Delete functionality will be implemented in next update. Would delete ${count} contacts.`);
        }
    }

    // Base module required methods
    onRefresh() {
        const activeTab = this.activeSubTab || 'dashboard';
        const tabConfig = this.subTabs.get(activeTab);
        if (tabConfig && tabConfig.load) {
            tabConfig.load();
        }
    }

    onSettings() {
        console.log('Opening Xero settings...');
        // TODO: Implement settings modal
    }

    // ========================================================================
    // REPORTS METHODS
    // ========================================================================

    async showAgedReceivables() {
        const resultsDiv = document.querySelector('#xero-invoices-report-results');
        if (!resultsDiv) return;

        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading aged receivables...</div>';

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/aged-receivables?business_id=${this.currentBusiness}`);
            const data = await response.json();

            if (!data.success) throw new Error(data.error);

            const { buckets, total_outstanding, total_count } = data;

            let html = `
                <div style="padding: 16px; background: #161b22; border-radius: 6px;">
                    <h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Aged Receivables Report</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="border-bottom: 1px solid #30363d;">
                                <th style="text-align: left; padding: 8px; color: #8b949e; font-size: 12px; font-weight: 600;">Age Bucket</th>
                                <th style="text-align: right; padding: 8px; color: #8b949e; font-size: 12px; font-weight: 600;">Count</th>
                                <th style="text-align: right; padding: 8px; color: #8b949e; font-size: 12px; font-weight: 600;">Amount</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            for (const [key, bucket] of Object.entries(buckets)) {
                const color = key === '90+' ? '#f85149' : key === '61-90' ? '#f0883e' : key === '31-60' ? '#f0c14e' : '#c9d1d9';
                html += `
                    <tr style="border-bottom: 1px solid #21262d;">
                        <td style="padding: 8px; color: ${color};">${bucket.label}</td>
                        <td style="text-align: right; padding: 8px; color: #c9d1d9;">${bucket.count}</td>
                        <td style="text-align: right; padding: 8px; color: #c9d1d9;">$${bucket.amount.toFixed(2)}</td>
                    </tr>
                `;
            }

            html += `
                        </tbody>
                        <tfoot>
                            <tr style="border-top: 2px solid #30363d; font-weight: 600;">
                                <td style="padding: 8px; color: #ffffff;">TOTAL</td>
                                <td style="text-align: right; padding: 8px; color: #ffffff;">${total_count}</td>
                                <td style="text-align: right; padding: 8px; color: #ffffff;">$${total_outstanding.toFixed(2)}</td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            `;

            resultsDiv.innerHTML = html;
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 16px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showSalesSummary() {
        const resultsDiv = document.querySelector('#xero-invoices-report-results');
        if (!resultsDiv) return;

        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading sales summary...</div>';

        try {
            const months = this.dateRanges.invoices || 3;
            const fromDate = this.getDateRangeStart(months);
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/sales-summary?business_id=${this.currentBusiness}&from_date=${fromDate}`);
            const data = await response.json();

            if (!data.success) throw new Error(data.error);

            const { sales, total_revenue, total_paid, total_outstanding } = data;

            let html = `
                <div style="padding: 16px; background: #161b22; border-radius: 6px;">
                    <h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Sales Summary (Last ${months} months)</h4>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;">
                        <div style="padding: 12px; background: #0d1117; border-radius: 4px;">
                            <div style="color: #8b949e; font-size: 11px; margin-bottom: 4px;">Total Revenue</div>
                            <div style="color: #ffffff; font-size: 18px; font-weight: 600;">$${total_revenue.toFixed(2)}</div>
                        </div>
                        <div style="padding: 12px; background: #0d1117; border-radius: 4px;">
                            <div style="color: #8b949e; font-size: 11px; margin-bottom: 4px;">Total Paid</div>
                            <div style="color: #3fb950; font-size: 18px; font-weight: 600;">$${total_paid.toFixed(2)}</div>
                        </div>
                        <div style="padding: 12px; background: #0d1117; border-radius: 4px;">
                            <div style="color: #8b949e; font-size: 11px; margin-bottom: 4px;">Outstanding</div>
                            <div style="color: #f0883e; font-size: 18px; font-weight: 600;">$${total_outstanding.toFixed(2)}</div>
                        </div>
                    </div>
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                        <thead>
                            <tr style="border-bottom: 1px solid #30363d;">
                                <th style="text-align: left; padding: 8px; color: #8b949e; font-weight: 600;">Customer</th>
                                <th style="text-align: right; padding: 8px; color: #8b949e; font-weight: 600;">Invoices</th>
                                <th style="text-align: right; padding: 8px; color: #8b949e; font-weight: 600;">Revenue</th>
                                <th style="text-align: right; padding: 8px; color: #8b949e; font-weight: 600;">Outstanding</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            for (const sale of sales.slice(0, 10)) {
                html += `
                    <tr style="border-bottom: 1px solid #21262d;">
                        <td style="padding: 8px; color: #c9d1d9;">${sale.contact_name}</td>
                        <td style="text-align: right; padding: 8px; color: #c9d1d9;">${sale.invoice_count}</td>
                        <td style="text-align: right; padding: 8px; color: #c9d1d9;">$${sale.total_invoiced.toFixed(2)}</td>
                        <td style="text-align: right; padding: 8px; color: #c9d1d9;">$${sale.outstanding.toFixed(2)}</td>
                    </tr>
                `;
            }

            html += `
                        </tbody>
                    </table>
                </div>
            `;

            resultsDiv.innerHTML = html;
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 16px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showOverdueInvoices() {
        const resultsDiv = document.querySelector('#xero-invoices-report-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading overdue invoices...</div>';

        try {
            const fromDate = this.getDateRangeStart(this.dateRanges.invoices);
            let url = `${this.API_BASE_URL}/api/xero/reports/overdue-invoices?business_id=${this.currentBusiness}`;
            if (fromDate) url += `&from_date=${fromDate}`;

            const response = await fetch(url);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);

            // Transform data for Tabulator
            const tableData = (data.invoices || []).map(inv => ({
                invoice_number: inv.invoice_number || inv.InvoiceNumber || 'N/A',
                contact_name: inv.contact_name || inv.contact || inv.Contact?.Name || 'Unknown',
                due_date: this.parseXeroDate(inv.due_date || inv.DueDate),
                amount_due: parseFloat(inv.amount_due || inv.AmountDue || 0),
                days_overdue: inv.days_overdue || Math.max(0, Math.floor((new Date() - this.parseXeroDate(inv.due_date || inv.DueDate)) / (1000 * 60 * 60 * 24)))
            }));

            resultsDiv.innerHTML = `<div style="padding: 16px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Overdue Invoices (${tableData.length})</h4><div id="overdue-invoices-table"></div></div>`;

            new Tabulator('#overdue-invoices-table', {
                data: tableData,
                layout: 'fitColumns',
                height: '600px',
                pagination: 'local',
                paginationSize: 25,
                paginationSizeSelector: [10, 25, 50, 100],
                columns: [
                    { title: 'Invoice #', field: 'invoice_number', sorter: 'string', headerFilter: 'input', width: 120 },
                    { title: 'Contact', field: 'contact_name', sorter: 'string', headerFilter: 'input', widthGrow: 2 },
                    {
                        title: 'Due Date',
                        field: 'due_date',
                        sorter: 'date',
                        formatter: (cell) => this.formatDate(cell.getValue()),
                        width: 130
                    },
                    {
                        title: 'Days Overdue',
                        field: 'days_overdue',
                        sorter: 'number',
                        hozAlign: 'right',
                        width: 130,
                        formatter: (cell) => {
                            const val = cell.getValue();
                            const color = val > 90 ? '#f85149' : val > 60 ? '#d29922' : '#f0883e';
                            return `<span style="color: ${color}; font-weight: bold;">${val}</span>`;
                        }
                    },
                    {
                        title: 'Amount Due',
                        field: 'amount_due',
                        sorter: 'number',
                        hozAlign: 'right',
                        formatter: 'money',
                        formatterParams: { precision: 2, symbol: '$' },
                        width: 130
                    }
                ],
                initialSort: [{ column: 'days_overdue', dir: 'desc' }]
            });
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showRevenueTrends() {
        const resultsDiv = document.querySelector('#xero-invoices-report-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading revenue trends...</div>';

        try {
            const fromDate = this.getDateRangeStart(this.dateRanges.invoices);
            let url = `${this.API_BASE_URL}/api/xero/reports/revenue-trends?business_id=${this.currentBusiness}`;
            if (fromDate) url += `&from_date=${fromDate}`;

            const response = await fetch(url);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);

            // Transform data for Tabulator
            const tableData = (data.trends || []).map(trend => ({
                month: trend.month || trend.period,
                revenue: parseFloat(trend.revenue || 0),
                invoice_count: trend.invoice_count || trend.count || 0,
                avg_value: trend.invoice_count ? (trend.revenue / trend.invoice_count) : 0
            }));

            // Calculate totals and averages
            const totalRevenue = tableData.reduce((sum, t) => sum + t.revenue, 0);
            const avgMonthlyRevenue = tableData.length > 0 ? totalRevenue / tableData.length : 0;

            resultsDiv.innerHTML = `
                <div style="padding: 16px;">
                    <h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Revenue Trends (${tableData.length} months)</h4>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 16px;">
                        <div style="padding: 12px; background: #0d1117; border-radius: 4px;">
                            <div style="color: #8b949e; font-size: 11px; margin-bottom: 4px;">Total Revenue</div>
                            <div style="color: #3fb950; font-size: 18px; font-weight: 600;">$${totalRevenue.toFixed(2)}</div>
                        </div>
                        <div style="padding: 12px; background: #0d1117; border-radius: 4px;">
                            <div style="color: #8b949e; font-size: 11px; margin-bottom: 4px;">Avg Monthly</div>
                            <div style="color: #58a6ff; font-size: 18px; font-weight: 600;">$${avgMonthlyRevenue.toFixed(2)}</div>
                        </div>
                    </div>
                    <div id="revenue-trends-table"></div>
                </div>
            `;

            new Tabulator('#revenue-trends-table', {
                data: tableData,
                layout: 'fitColumns',
                height: '500px',
                pagination: 'local',
                paginationSize: 12,
                columns: [
                    { title: 'Month', field: 'month', sorter: 'string', headerFilter: 'input', width: 150 },
                    { title: 'Revenue', field: 'revenue', sorter: 'number', hozAlign: 'right', formatter: 'money', formatterParams: { precision: 2, symbol: '$' }, widthGrow: 2 },
                    { title: 'Invoices', field: 'invoice_count', sorter: 'number', hozAlign: 'center', width: 100 },
                    { title: 'Avg Value', field: 'avg_value', sorter: 'number', hozAlign: 'right', formatter: 'money', formatterParams: { precision: 2, symbol: '$' }, width: 130 }
                ],
                initialSort: [{ column: 'month', dir: 'desc' }]
            });
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showInvoiceStatus() {
        const resultsDiv = document.querySelector('#xero-invoices-report-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading status summary...</div>';
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/invoice-status?business_id=${this.currentBusiness}`);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Invoice Status Summary</h4><table style="width: 100%; border-collapse: collapse;"><thead><tr style="border-bottom: 1px solid #30363d;"><th style="text-align: left; padding: 8px;">Status</th><th style="text-align: right; padding: 8px;">Count</th><th style="text-align: right; padding: 8px;">Total Amount</th></tr></thead><tbody>`;
            Object.entries(data.status_summary).forEach(([status, stats]) => {
                html += `<tr style="border-bottom: 1px solid #30363d;"><td style="padding: 8px; color: #c9d1d9;">${status}</td><td style="padding: 8px; text-align: right; color: #8b949e;">${stats.count}</td><td style="padding: 8px; text-align: right; color: #c9d1d9;">$${stats.total.toFixed(2)}</td></tr>`;
            });
            html += `</tbody></table></div>`;
            resultsDiv.innerHTML = html;
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showInvoiceVolume() {
        const resultsDiv = document.querySelector('#xero-invoices-report-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading volume analysis...</div>';
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/invoice-volume?business_id=${this.currentBusiness}`);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Invoice Volume Analysis</h4><div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;"><div style="padding: 12px; background: #0d1117; border-radius: 4px;"><div style="font-size: 12px; color: #8b949e; margin-bottom: 4px;">Total Invoices</div><div style="font-size: 20px; color: #c9d1d9; font-weight: 600;">${data.total_invoices}</div></div><div style="padding: 12px; background: #0d1117; border-radius: 4px;"><div style="font-size: 12px; color: #8b949e; margin-bottom: 4px;">Avg per Month</div><div style="font-size: 20px; color: #c9d1d9; font-weight: 600;">${data.avg_invoices_per_month.toFixed(1)}</div></div><div style="padding: 12px; background: #0d1117; border-radius: 4px;"><div style="font-size: 12px; color: #8b949e; margin-bottom: 4px;">Avg Value</div><div style="font-size: 20px; color: #c9d1d9; font-weight: 600;">$${data.avg_invoice_value.toFixed(2)}</div></div></div></div>`;
            resultsDiv.innerHTML = html;
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showContactActivity() {
        const resultsDiv = document.querySelector('#xero-contacts-report-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading contact activity...</div>';

        try {
            const fromDate = this.getDateRangeStart(this.dateRanges.contacts);
            let url = `${this.API_BASE_URL}/api/xero/reports/contact-activity?business_id=${this.currentBusiness}`;
            if (fromDate) url += `&from_date=${fromDate}`;

            const response = await fetch(url);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);

            const tableData = (data.contacts || []).map(c => ({
                contact_name: c.contact_name || c.contact || c.name || 'Unknown',
                invoice_count: c.invoice_count || c.total_invoices || 0,
                total_revenue: parseFloat(c.total_revenue || c.revenue || 0)
            }));

            resultsDiv.innerHTML = `<div style="padding: 16px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Contact Activity (${tableData.length})</h4><div id="contact-activity-table"></div></div>`;

            new Tabulator('#contact-activity-table', {
                data: tableData,
                layout: 'fitColumns',
                height: '600px',
                pagination: 'local',
                paginationSize: 25,
                paginationSizeSelector: [10, 25, 50, 100],
                columns: [
                    { title: 'Contact', field: 'contact_name', sorter: 'string', headerFilter: 'input', widthGrow: 2 },
                    { title: 'Invoices', field: 'invoice_count', sorter: 'number', hozAlign: 'right', width: 120, headerFilter: 'input' },
                    { title: 'Total Revenue', field: 'total_revenue', sorter: 'number', hozAlign: 'right', formatter: 'money', formatterParams: { precision: 2, symbol: '$' }, width: 150 }
                ],
                initialSort: [{ column: 'total_revenue', dir: 'desc' }]
            });
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showInactiveCustomers() {
        const resultsDiv = document.querySelector('#xero-contacts-report-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading inactive customers...</div>';

        try {
            const fromDate = this.getDateRangeStart(this.dateRanges.contacts);
            let url = `${this.API_BASE_URL}/api/xero/reports/inactive-customers?business_id=${this.currentBusiness}`;
            if (fromDate) url += `&from_date=${fromDate}`;

            const response = await fetch(url);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);

            const tableData = (data.customers || []).map(c => ({
                contact_name: c.contact_name || c.contact || c.name || 'Unknown',
                last_invoice_date: this.parseXeroDate(c.last_invoice_date),
                days_since_last: c.days_since_last || c.days_inactive || 0
            }));

            resultsDiv.innerHTML = `<div style="padding: 16px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Inactive Customers (${tableData.length})</h4><div id="inactive-customers-table"></div></div>`;

            new Tabulator('#inactive-customers-table', {
                data: tableData,
                layout: 'fitColumns',
                height: '600px',
                pagination: 'local',
                paginationSize: 25,
                paginationSizeSelector: [10, 25, 50, 100],
                columns: [
                    { title: 'Contact', field: 'contact_name', sorter: 'string', headerFilter: 'input', widthGrow: 2 },
                    { title: 'Last Invoice', field: 'last_invoice_date', sorter: 'date', formatter: (cell) => this.formatDate(cell.getValue()), width: 130 },
                    { title: 'Days Inactive', field: 'days_since_last', sorter: 'number', hozAlign: 'right', width: 130, headerFilter: 'input' }
                ],
                initialSort: [{ column: 'days_since_last', dir: 'desc' }]
            });
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showCustomerLTV() {
        const resultsDiv = document.querySelector('#xero-contacts-report-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading customer lifetime value...</div>';
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/customer-lifetime-value?business_id=${this.currentBusiness}`);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Customer Lifetime Value</h4><table style="width: 100%; border-collapse: collapse;"><thead><tr style="border-bottom: 1px solid #30363d;"><th style="text-align: left; padding: 8px;">Customer</th><th style="text-align: right; padding: 8px;">Revenue</th><th style="text-align: right; padding: 8px;">Invoices</th><th style="text-align: right; padding: 8px;">Tenure (days)</th></tr></thead><tbody>`;
            data.customers.slice(0, 20).forEach(customer => {
                html += `<tr style="border-bottom: 1px solid #30363d;"><td style="padding: 8px; color: #c9d1d9;">${customer.contact_name}</td><td style="padding: 8px; text-align: right; color: #238636; font-weight: 600;">$${customer.total_revenue.toFixed(2)}</td><td style="padding: 8px; text-align: right; color: #8b949e;">${customer.invoice_count}</td><td style="padding: 8px; text-align: right; color: #8b949e;">${customer.tenure_days}</td></tr>`;
            });
            html += `</tbody></table></div>`;
            resultsDiv.innerHTML = html;
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showCustomerSegmentation() {
        const resultsDiv = document.querySelector('#xero-contacts-report-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading customer segmentation...</div>';
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/customer-segmentation?business_id=${this.currentBusiness}`);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Customer Segmentation (RFM)</h4><div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 8px; margin-bottom: 16px;">`;
            const colors = { Champions: '#238636', 'Loyal Customers': '#1f6feb', 'Potential Loyalists': '#8957e5', 'At Risk': '#d29922', Lost: '#f85149' };
            Object.entries(data.segment_distribution).forEach(([segment, count]) => {
                html += `<div style="padding: 12px; background: #0d1117; border-radius: 4px; border-left: 3px solid ${colors[segment] || '#8b949e'};"><div style="font-size: 12px; color: #8b949e;">${segment}</div><div style="font-size: 20px; color: #c9d1d9; font-weight: 600;">${count}</div></div>`;
            });
            html += `</div></div>`;
            resultsDiv.innerHTML = html;
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showBusinessComparison() {
        const resultsDiv = document.querySelector('#xero-reports-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading business comparison...</div>';
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/business-comparison`);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Business Performance Comparison</h4><table style="width: 100%; border-collapse: collapse;"><thead><tr style="border-bottom: 1px solid #30363d;"><th style="text-align: left; padding: 8px;">Business</th><th style="text-align: right; padding: 8px;">Revenue</th><th style="text-align: right; padding: 8px;">Outstanding</th><th style="text-align: right; padding: 8px;">Invoices</th></tr></thead><tbody>`;
            data.businesses.forEach(biz => {
                html += `<tr style="border-bottom: 1px solid #30363d;"><td style="padding: 8px; color: #c9d1d9;">${biz.business_name}</td><td style="padding: 8px; text-align: right; color: #238636; font-weight: 600;">$${biz.revenue.toFixed(2)}</td><td style="padding: 8px; text-align: right; color: #d29922;">$${biz.outstanding.toFixed(2)}</td><td style="padding: 8px; text-align: right; color: #8b949e;">${biz.invoice_count}</td></tr>`;
            });
            html += `</tbody></table></div>`;
            resultsDiv.innerHTML = html;
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showConsolidatedRevenue() {
        const resultsDiv = document.querySelector('#xero-reports-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading consolidated revenue...</div>';
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/consolidated-revenue`);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Consolidated Revenue</h4><div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 16px;"><div style="padding: 16px; background: #0d1117; border-radius: 4px;"><div style="font-size: 12px; color: #8b949e; margin-bottom: 4px;">Total Revenue</div><div style="font-size: 24px; color: #238636; font-weight: 600;">$${data.consolidated.total_revenue.toFixed(2)}</div></div><div style="padding: 16px; background: #0d1117; border-radius: 4px;"><div style="font-size: 12px; color: #8b949e; margin-bottom: 4px;">Total Outstanding</div><div style="font-size: 24px; color: #d29922; font-weight: 600;">$${data.consolidated.total_outstanding.toFixed(2)}</div></div></div></div>`;
            resultsDiv.innerHTML = html;
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showCustomerOverlap() {
        const resultsDiv = document.querySelector('#xero-reports-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading customer overlap...</div>';
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/customer-overlap`);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Customer Overlap Analysis</h4><div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;"><div style="padding: 12px; background: #0d1117; border-radius: 4px;"><div style="font-size: 12px; color: #8b949e;">Total Customers</div><div style="font-size: 20px; color: #c9d1d9; font-weight: 600;">${data.total_unique_customers}</div></div><div style="padding: 12px; background: #0d1117; border-radius: 4px;"><div style="font-size: 12px; color: #8b949e;">Overlapping</div><div style="font-size: 20px; color: #1f6feb; font-weight: 600;">${data.overlapping_customer_count}</div></div><div style="padding: 12px; background: #0d1117; border-radius: 4px;"><div style="font-size: 12px; color: #8b949e;">Overlap %</div><div style="font-size: 20px; color: #8957e5; font-weight: 600;">${data.overlap_percentage}%</div></div></div></div>`;
            resultsDiv.innerHTML = html;
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showRevenueByProduct() {
        const resultsDiv = document.querySelector('#xero-reports-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading revenue by product...</div>';
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/revenue-by-product?business_id=${this.currentBusiness}`);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Revenue by Product/Service</h4><table style="width: 100%; border-collapse: collapse;"><thead><tr style="border-bottom: 1px solid #30363d;"><th style="text-align: left; padding: 8px;">Product</th><th style="text-align: right; padding: 8px;">Quantity</th><th style="text-align: right; padding: 8px;">Revenue</th></tr></thead><tbody>`;
            data.products.slice(0, 20).forEach(product => {
                html += `<tr style="border-bottom: 1px solid #30363d;"><td style="padding: 8px; color: #c9d1d9;">${product.product}</td><td style="padding: 8px; text-align: right; color: #8b949e;">${product.quantity_sold}</td><td style="padding: 8px; text-align: right; color: #238636; font-weight: 600;">$${product.revenue.toFixed(2)}</td></tr>`;
            });
            html += `</tbody></table></div>`;
            resultsDiv.innerHTML = html;
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showSeasonality() {
        const resultsDiv = document.querySelector('#xero-reports-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading seasonality analysis...</div>';
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/seasonality?business_id=${this.currentBusiness}`);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Seasonality Analysis</h4><table style="width: 100%; border-collapse: collapse;"><thead><tr style="border-bottom: 1px solid #30363d;"><th style="text-align: left; padding: 8px;">Month</th><th style="text-align: right; padding: 8px;">Avg Revenue</th><th style="text-align: right; padding: 8px;">Occurrences</th></tr></thead><tbody>`;
            data.seasonal_pattern.forEach(month => {
                html += `<tr style="border-bottom: 1px solid #30363d;"><td style="padding: 8px; color: #c9d1d9;">${month.month_name}</td><td style="padding: 8px; text-align: right; color: #238636;">$${month.avg_revenue.toFixed(2)}</td><td style="padding: 8px; text-align: right; color: #8b949e;">${month.occurrences}</td></tr>`;
            });
            html += `</tbody></table></div>`;
            resultsDiv.innerHTML = html;
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }

    async showForecast() {
        const resultsDiv = document.querySelector('#xero-reports-results');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">Loading revenue forecast...</div>';
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/reports/forecast?business_id=${this.currentBusiness}`);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);
            let html = `<div style="padding: 16px; background: #161b22; border-radius: 6px;"><h4 style="margin: 0 0 16px 0; color: #c9d1d9;">Revenue Forecast</h4><div style="margin-bottom: 16px; padding: 12px; background: #0d1117; border-radius: 4px;"><div style="font-size: 12px; color: #8b949e;">Avg Monthly Revenue</div><div style="font-size: 20px; color: #238636; font-weight: 600;">$${data.avg_monthly_revenue.toFixed(2)}</div><div style="font-size: 12px; color: #8b949e; margin-top: 8px;">Growth Rate: ${data.avg_growth_rate.toFixed(2)}%</div></div><table style="width: 100%; border-collapse: collapse;"><thead><tr style="border-bottom: 1px solid #30363d;"><th style="text-align: left; padding: 8px;">Month</th><th style="text-align: right; padding: 8px;">Forecasted Revenue</th><th style="text-align: right; padding: 8px;">Confidence</th></tr></thead><tbody>`;
            data.forecast.forEach(month => {
                html += `<tr style="border-bottom: 1px solid #30363d;"><td style="padding: 8px; color: #c9d1d9;">${month.month}</td><td style="padding: 8px; text-align: right; color: #1f6feb; font-weight: 600;">$${month.forecasted_revenue.toFixed(2)}</td><td style="padding: 8px; text-align: right; color: #8b949e;">${month.confidence}</td></tr>`;
            });
            html += `</tbody></table></div>`;
            resultsDiv.innerHTML = html;
        } catch (error) {
            resultsDiv.innerHTML = `<div style="padding: 20px; color: #f85149;">Error: ${error.message}</div>`;
        }
    }
}

// ============================================================================
// REGISTER MODULE
// ============================================================================

// Register module with ModuleLoader (V5.0 pattern)
if (window.ModuleLoader) {
    window.ModuleLoader.registerModuleClass('xero', XeroModule);
    console.log('[Xero] Module class registered with ModuleLoader');
} else {
    console.warn('[Xero] ModuleLoader not found - module may not load correctly');
}

// ES6 Export
export default XeroModule;
