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
    }

    /**
     * Initialize module
     */
    async initialize() {
        console.log('Initializing Xero module...');
        
        try {
            // Call parent initialization
            await super.initialize();
            
            // Create business selector in header
            this.createBusinessSelector();
            
            // Initialize sub-tabs
            this.initializeSubTabs();
            
            // Load initial data
            await this.loadDashboard();
            
            console.log(' Xero module initialized successfully');
        } catch (error) {
            console.error('Failed to initialize Xero module:', error);
            this.showError('Failed to initialize Xero module: ' + error.message);
        }
    }

    /**
     * Create business selector dropdown
     */
    createBusinessSelector() {
        const header = this.container.querySelector('.module-header-right');
        if (!header) return;

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
        console.log(`Switching to Xero tab: ${tabId}`);
        
        // Update active button
        const buttons = this.container.querySelectorAll('.module-subtab-btn');
        buttons.forEach(btn => {
            if (btn.getAttribute('data-subtab') === tabId) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Hide all tab contents
        const allContents = this.container.querySelectorAll('.module-subtab-content');
        allContents.forEach(content => content.style.display = 'none');

        // Show selected tab
        const selectedContent = this.container.querySelector(`#xero-tab-${tabId}`);
        if (selectedContent) {
            selectedContent.style.display = 'block';
        }

        this.activeSubTab = tabId;

        // Load tab data if not already loaded
        const tabConfig = this.subTabs.get(tabId);
        if (tabConfig && tabConfig.load) {
            tabConfig.load();
        }
    }

    // ========================================================================
    // DASHBOARD TAB
    // ========================================================================

    renderDashboard() {
        const container = this.container.querySelector('#xero-tab-dashboard');
        if (!container) return;

        container.innerHTML = `
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
        // Update stat cards
        const stats = data.stats || {};
        
        this.updateStatCard('revenue', {
            value: this.formatCurrency(stats.total_revenue || 0),
            change: stats.revenue_change || 'N/A'
        });

        this.updateStatCard('outstanding', {
            value: this.formatCurrency(stats.outstanding_amount || 0),
            change: `${stats.outstanding_count || 0} invoices`
        });

        this.updateStatCard('overdue', {
            value: this.formatCurrency(stats.overdue_amount || 0),
            change: `${stats.overdue_count || 0} invoices`
        });

        this.updateStatCard('invoices', {
            value: stats.total_invoices || 0,
            change: `${stats.paid_invoices || 0} paid`
        });
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
            xaxis: { title: 'Date' },
            yaxis: { title: 'Revenue ($)' },
            margin: { l: 60, r: 40, t: 40, b: 60 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent'
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
            plot_bgcolor: 'transparent'
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
            xaxis: { title: 'Revenue ($)' },
            yaxis: { title: '' },
            margin: { l: 150, r: 40, t: 40, b: 60 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent'
        };

        Plotly.newPlot(container, [trace], layout, { responsive: true });
    }

    // ========================================================================
    // INVOICES TAB
    // ========================================================================

    renderInvoices() {
        const container = this.container.querySelector('#xero-tab-invoices');
        if (!container) return;

        container.innerHTML = `
            <div class="xero-invoices">
                <div class="xero-toolbar">
                    <div class="xero-toolbar-left">
                        <button class="xero-btn xero-btn-primary" id="xero-create-invoice">
                            <i class="fas fa-plus"></i> Create Invoice
                        </button>
                        <button class="xero-btn" id="xero-refresh-invoices">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                    </div>
                    <div class="xero-toolbar-right">
                        <input type="text" class="xero-search" id="xero-invoice-search" 
                               placeholder="Search invoices...">
                        <select class="xero-filter" id="xero-invoice-status">
                            <option value="">All Statuses</option>
                            <option value="DRAFT">Draft</option>
                            <option value="SUBMITTED">Submitted</option>
                            <option value="AUTHORISED">Authorised</option>
                            <option value="PAID">Paid</option>
                            <option value="VOIDED">Voided</option>
                        </select>
                    </div>
                </div>
                <div id="xero-invoices-table"></div>
            </div>
        `;

        // Add event listeners
        const createBtn = container.querySelector('#xero-create-invoice');
        const refreshBtn = container.querySelector('#xero-refresh-invoices');
        const searchInput = container.querySelector('#xero-invoice-search');
        const statusFilter = container.querySelector('#xero-invoice-status');

        if (createBtn) createBtn.addEventListener('click', () => this.showCreateInvoiceModal());
        if (refreshBtn) refreshBtn.addEventListener('click', () => this.loadInvoices());
        if (searchInput) searchInput.addEventListener('input', (e) => this.filterInvoices(e.target.value));
        if (statusFilter) statusFilter.addEventListener('change', (e) => this.filterInvoicesByStatus(e.target.value));
    }

    async loadInvoices() {
        console.log('Loading Xero invoices...');
        this.showLoading('Loading invoices...');

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/invoices?business_id=${this.currentBusiness}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to load invoices');
            }

            this.data.invoices = data.invoices || [];
            this.createInvoicesTable();
            
            this.hideLoading();
        } catch (error) {
            console.error('Error loading invoices:', error);
            this.showError('Failed to load invoices: ' + error.message);
        }
    }

    createInvoicesTable() {
        const container = this.container.querySelector('#xero-invoices-table');
        if (!container) return;

        this.tables.invoices = new Tabulator(container, {
            data: this.data.invoices,
            layout: 'fitColumns',
            responsiveLayout: 'collapse',
            pagination: 'local',
            paginationSize: 50,
            columns: [
                { 
                    title: 'Invoice #', 
                    field: 'invoice_number',
                    width: 120,
                    formatter: (cell) => {
                        const value = cell.getValue();
                        return `<span class="xero-invoice-number">${value}</span>`;
                    }
                },
                { title: 'Contact', field: 'contact_name', width: 200 },
                { 
                    title: 'Date', 
                    field: 'date',
                    width: 120,
                    formatter: (cell) => this.formatDate(cell.getValue())
                },
                { 
                    title: 'Due Date', 
                    field: 'due_date',
                    width: 120,
                    formatter: (cell) => this.formatDate(cell.getValue())
                },
                { 
                    title: 'Total', 
                    field: 'total',
                    width: 120,
                    hozAlign: 'right',
                    formatter: (cell) => this.formatCurrency(cell.getValue())
                },
                { 
                    title: 'Amount Due', 
                    field: 'amount_due',
                    width: 120,
                    hozAlign: 'right',
                    formatter: (cell) => this.formatCurrency(cell.getValue())
                },
                { 
                    title: 'Status', 
                    field: 'status',
                    width: 120,
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
    }

    // ========================================================================
    // CONTACTS TAB
    // ========================================================================

    renderContacts() {
        const container = this.container.querySelector('#xero-tab-contacts');
        if (!container) return;

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
    }

    async loadContacts() {
        console.log('Loading Xero contacts...');
        this.showLoading('Loading contacts...');

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/contacts?business_id=${this.currentBusiness}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to load contacts');
            }

            this.data.contacts = data.contacts || [];
            this.createContactsTable();
            
            this.hideLoading();
        } catch (error) {
            console.error('Error loading contacts:', error);
            this.showError('Failed to load contacts: ' + error.message);
        }
    }

    createContactsTable() {
        const container = this.container.querySelector('#xero-contacts-table');
        if (!container) return;

        this.tables.contacts = new Tabulator(container, {
            data: this.data.contacts,
            layout: 'fitColumns',
            responsiveLayout: 'collapse',
            pagination: 'local',
            paginationSize: 50,
            columns: [
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
    }

    // ========================================================================
    // PAYMENTS TAB
    // ========================================================================

    renderPayments() {
        const container = this.container.querySelector('#xero-tab-payments');
        if (!container) return;

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
                <div id="xero-payments-table"></div>
            </div>
        `;

        // Add event listeners
        const refreshBtn = container.querySelector('#xero-refresh-payments');
        const searchInput = container.querySelector('#xero-payment-search');

        if (refreshBtn) refreshBtn.addEventListener('click', () => this.loadPayments());
        if (searchInput) searchInput.addEventListener('input', (e) => this.filterPayments(e.target.value));
    }

    async loadPayments() {
        console.log('Loading Xero payments...');
        this.showLoading('Loading payments...');

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/payments?business_id=${this.currentBusiness}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to load payments');
            }

            this.data.payments = data.payments || [];
            this.createPaymentsTable();
            
            this.hideLoading();
        } catch (error) {
            console.error('Error loading payments:', error);
            this.showError('Failed to load payments: ' + error.message);
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
        const container = this.container.querySelector('#xero-tab-accounts');
        if (!container) return;

        container.innerHTML = `
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

        // Add event listeners
        const refreshBtn = container.querySelector('#xero-refresh-accounts');
        const searchInput = container.querySelector('#xero-account-search');

        if (refreshBtn) refreshBtn.addEventListener('click', () => this.loadAccounts());
        if (searchInput) searchInput.addEventListener('input', (e) => this.filterAccounts(e.target.value));
    }

    async loadAccounts() {
        console.log('Loading Xero accounts...');
        this.showLoading('Loading accounts...');

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/xero/accounts?business_id=${this.currentBusiness}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to load accounts');
            }

            this.data.accounts = data.accounts || [];
            this.createAccountsTable();
            
            this.hideLoading();
        } catch (error) {
            console.error('Error loading accounts:', error);
            this.showError('Failed to load accounts: ' + error.message);
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
        const container = this.container.querySelector('#xero-tab-reports');
        if (!container) return;

        container.innerHTML = `
            <div class="xero-reports">
                <h3>Financial Reports</h3>
                <p>Coming soon...</p>
            </div>
        `;
    }

    async loadReports() {
        console.log('Loading Xero reports...');
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
        // TODO: Implement loading indicator
        console.log(message);
    }

    hideLoading() {
        // TODO: Hide loading indicator
    }

    showError(message) {
        console.error(message);
        alert(message); // TODO: Improve error display
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
}

// ============================================================================
// REGISTER MODULE
// ============================================================================

// Auto-register when script loads
if (typeof window.moduleManager !== 'undefined') {
    window.moduleManager.registerModule('xero', XeroModule);
    console.log(' Xero module registered');
}


// ES6 Export
export default XeroModule;
