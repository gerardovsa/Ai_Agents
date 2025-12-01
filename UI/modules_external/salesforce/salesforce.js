/**
 * Salesforce Module
 * Example module demonstrating the modular architecture
 * Extends BaseModule to provide Salesforce integration
 * 
 * @class SalesforceModule
 * @extends BaseModule
 * @created October 30, 2025
 */
class SalesforceModule extends BaseModule {
    constructor(moduleId) {
        super(moduleId);
        this.apiEndpoint = null;
        this.accessToken = null;
        this.leads = [];
        this.accounts = [];
        this.opportunities = [];

        console.log('🔧 SalesforceModule created');
    }

    async initialize() {
        await super.initialize();

        // Load settings
        this.apiEndpoint = this.manifest.settings.api_endpoint;

        // Note: In production, authenticate via parent platform
        // For demo, we'll show mock data
        console.log('🔐 Salesforce authentication would happen here');

        // Load initial data
        await this.loadInitialData();
    }

    async loadInitialData() {
        console.log('📊 Loading Salesforce data...');

        // Load data for default tab
        if (this.activeSubTab === 'leads') {
            await this.loadLeads();
        }
    }

    initializeSubTabs() {
        console.log('📋 Initializing Salesforce sub-tabs...');

        // Populate each sub-tab with its content
        this.initializeLeadsTab();
        this.initializeAccountsTab();
        this.initializeOpportunitiesTab();
        this.initializeReportsTab();
    }

    /**
     * LEADS TAB
     */
    initializeLeadsTab() {
        const leadsTab = this.getSubTabContainer('leads');
        if (!leadsTab) return;

        // Create leads dashboard
        leadsTab.innerHTML = `
            <div class="module-dashboard">
                <!-- Stats Cards -->
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon primary">
                            <i class="fas fa-user-plus"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">New Leads</div>
                            <div class="stat-value" id="leads-new-count">-</div>
                            <div class="stat-change">This week</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon success">
                            <i class="fas fa-check-circle"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Qualified</div>
                            <div class="stat-value" id="leads-qualified-count">-</div>
                            <div class="stat-change">Ready for sales</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon warning">
                            <i class="fas fa-clock"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Pending</div>
                            <div class="stat-value" id="leads-pending-count">-</div>
                            <div class="stat-change">Needs follow-up</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon error">
                            <i class="fas fa-times-circle"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Unqualified</div>
                            <div class="stat-value" id="leads-unqualified-count">-</div>
                            <div class="stat-change">Not a fit</div>
                        </div>
                    </div>
                </div>

                <!-- Leads Table -->
                <div class="dashboard-card">
                    <div class="card-header">
                        <h3 class="card-title">
                            <i class="fas fa-users"></i> Recent Leads
                        </h3>
                        <div class="card-actions">
                            <button class="btn btn-primary" onclick="alert('Create lead feature coming soon!')">
                                <i class="fas fa-plus"></i> New Lead
                            </button>
                        </div>
                    </div>
                    <div class="card-content">
                        <div id="leads-table-container"></div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Load leads (mock data for demo)
     */
    async loadLeads() {
        const tableContainer = document.getElementById('leads-table-container');
        if (!tableContainer) return;

        this.showLoading(tableContainer, 'Loading leads...');

        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 800));

        // Mock data
        this.leads = [
            { id: 1, name: 'John Smith', company: 'Acme Corp', email: 'john@acme.com', status: 'New', phone: '555-0101' },
            { id: 2, name: 'Jane Doe', company: 'Tech Solutions', email: 'jane@techsol.com', status: 'Qualified', phone: '555-0102' },
            { id: 3, name: 'Bob Johnson', company: 'StartupXYZ', email: 'bob@startupxyz.com', status: 'Working', phone: '555-0103' },
            { id: 4, name: 'Alice Williams', company: 'Enterprise Inc', email: 'alice@enterprise.com', status: 'Qualified', phone: '555-0104' },
            { id: 5, name: 'Charlie Brown', company: 'Small Biz', email: 'charlie@smallbiz.com', status: 'Unqualified', phone: '555-0105' }
        ];

        // Render leads table
        this.renderLeadsTable(tableContainer);

        // Update stats
        this.updateLeadsStats();

        console.log(` Loaded ${this.leads.length} leads`);
    }

    renderLeadsTable(container) {
        const table = document.createElement('table');
        table.className = 'data-table';
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Company</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${this.leads.map(lead => `
                    <tr>
                        <td><strong>${lead.name}</strong></td>
                        <td>${lead.company}</td>
                        <td>${lead.email}</td>
                        <td>${lead.phone}</td>
                        <td><span class="status-badge status-${lead.status.toLowerCase()}">${lead.status}</span></td>
                        <td>
                            <button class="btn btn-sm" onclick="alert('View lead: ${lead.name}')">
                                <i class="fas fa-eye"></i> View
                            </button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        `;

        container.innerHTML = '';
        container.appendChild(table);
    }

    updateLeadsStats() {
        const newCount = this.leads.filter(l => l.status === 'New').length;
        const qualifiedCount = this.leads.filter(l => l.status === 'Qualified').length;
        const pendingCount = this.leads.filter(l => l.status === 'Working').length;
        const unqualifiedCount = this.leads.filter(l => l.status === 'Unqualified').length;

        document.getElementById('leads-new-count').textContent = newCount;
        document.getElementById('leads-qualified-count').textContent = qualifiedCount;
        document.getElementById('leads-pending-count').textContent = pendingCount;
        document.getElementById('leads-unqualified-count').textContent = unqualifiedCount;
    }

    /**
     * ACCOUNTS TAB
     */
    initializeAccountsTab() {
        const accountsTab = this.getSubTabContainer('accounts');
        if (!accountsTab) return;

        accountsTab.innerHTML = `
            <div class="module-dashboard">
                <div class="dashboard-card">
                    <div class="card-header">
                        <h3 class="card-title">
                            <i class="fas fa-building"></i> Accounts
                        </h3>
                        <div class="card-actions">
                            <button class="btn btn-primary" onclick="alert('Create account feature coming soon!')">
                                <i class="fas fa-plus"></i> New Account
                            </button>
                        </div>
                    </div>
                    <div class="card-content">
                        <div class="empty-state">
                            <i class="fas fa-building"></i>
                            <p>Accounts feature coming soon...</p>
                            <p class="text-secondary">This will show all your Salesforce accounts with filtering and search.</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * OPPORTUNITIES TAB
     */
    initializeOpportunitiesTab() {
        const oppTab = this.getSubTabContainer('opportunities');
        if (!oppTab) return;

        oppTab.innerHTML = `
            <div class="module-dashboard">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon success">
                            <i class="fas fa-dollar-sign"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Total Pipeline</div>
                            <div class="stat-value">$2.4M</div>
                            <div class="stat-change">Active opportunities</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon primary">
                            <i class="fas fa-trophy"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Win Rate</div>
                            <div class="stat-value">68%</div>
                            <div class="stat-change">Last 90 days</div>
                        </div>
                    </div>
                </div>
                
                <div class="dashboard-card">
                    <div class="card-header">
                        <h3 class="card-title">
                            <i class="fas fa-handshake"></i> Opportunities Pipeline
                        </h3>
                    </div>
                    <div class="card-content">
                        <div class="empty-state">
                            <i class="fas fa-handshake"></i>
                            <p>Opportunities feature coming soon...</p>
                            <p class="text-secondary">This will show your sales pipeline with stage tracking and forecasting.</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * REPORTS TAB
     */
    initializeReportsTab() {
        const reportsTab = this.getSubTabContainer('reports');
        if (!reportsTab) return;

        reportsTab.innerHTML = `
            <div class="module-dashboard">
                <div class="dashboard-card">
                    <div class="card-header">
                        <h3 class="card-title">
                            <i class="fas fa-chart-bar"></i> Sales Reports
                        </h3>
                    </div>
                    <div class="card-content">
                        <div class="empty-state">
                            <i class="fas fa-chart-bar"></i>
                            <p>Reports feature coming soon...</p>
                            <p class="text-secondary">This will show customizable reports and analytics dashboards.</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Called when Salesforce tab is activated
     */
    onActivate() {
        console.log('▶️ Salesforce module activated');

        // Refresh data when tab is opened
        if (this.activeSubTab === 'leads') {
            this.loadLeads();
        }
    }

    /**
     * Called when sub-tab is switched
     */
    onSubTabActivate(subTabId) {
        console.log(`▶️ Salesforce sub-tab ${subTabId} activated`);

        // Load data for the active sub-tab
        switch (subTabId) {
            case 'leads':
                this.loadLeads();
                break;
            case 'accounts':
                console.log('📊 Accounts tab - no data to load yet');
                break;
            case 'opportunities':
                console.log('📊 Opportunities tab - no data to load yet');
                break;
            case 'reports':
                console.log('📊 Reports tab - no data to load yet');
                break;
        }
    }

    /**
     * Called when refresh button is clicked
     */
    onRefresh() {
        console.log('🔄 Refreshing Salesforce data...');

        // Reload current tab data
        if (this.activeSubTab === 'leads') {
            this.loadLeads();
        }
    }

    /**
     * Cleanup
     */
    destroy() {
        console.log('🗑️ Salesforce module destroyed');
        // Clear cached data
        this.leads = [];
        this.accounts = [];
        this.opportunities = [];
    }
}

// Register module in global registry
window.ModuleRegistry['salesforce'] = SalesforceModule;
console.log(' SalesforceModule registered in ModuleRegistry');
