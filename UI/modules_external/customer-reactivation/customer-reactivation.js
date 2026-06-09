/**
 * Customer Reactivation Module
 * ============================
 * 
 * Module for creating and managing customer reactivation email campaigns.
 * Integrates with Xero churn-risk ML models to identify at-risk customers
 * and track campaign ROI through reorder detection.
 * 
 * Features:
 * - Dashboard with campaign metrics and performance KPIs
 * - Customer insights from Xero ML models (churn risk scores)
 * - Campaign builder with template selection and personalization
 * - Email template library with pre-built designs
 * - Analytics with open/click/reorder tracking
 * - ROI calculation from Xero invoice data
 * 
 * Created: January 18, 2026
 */

// BaseModule polyfill (required since module-base.js is not globally loaded)
class BaseModule {
    constructor(moduleId) {
        this.moduleId = moduleId;
        this.manifest = null;
        this.backendUrl = window.API_BASE_URL || 'http://localhost:5001';
        console.log(`🔧 BaseModule constructor - moduleId: ${moduleId}`);
    }

    async initialize() {
        console.log(`🔧 BaseModule.initialize() called for ${this.moduleId}`);
        try {
            const response = await fetch(`${this.backendUrl}/api/modules/${this.moduleId}`);
            if (response.ok) {
                this.manifest = await response.json();
                console.log(`✅ Manifest loaded for ${this.moduleId}:`, this.manifest);
            }
        } catch (error) {
            console.warn(`⚠️ Failed to load manifest for ${this.moduleId}:`, error);
        }
    }
}

class CustomerReactivationModule extends BaseModule {
    constructor() {
        super();
        this.moduleId = 'customer-reactivation';
        this.moduleName = 'Customer Reactivation';
        
        // State
        this.currentTab = 'dashboard';
        this.currentBusinessId = 1; // Default to Print business
        this.customersTable = null;
        this.campaignsTable = null;
        this.templatesTable = null;
        this.selectedCustomers = [];
        this.selectedCampaign = null;
        
        // Data cache
        this.atRiskCustomers = [];
        this.campaigns = [];
        this.templates = [];
        this.dashboardStats = null;
    }

    /**
     * Module lifecycle: Initialize when dashboard loads
     */
    async onDashboardLoad(container) {
        console.log('[REACTIVATION] Initializing module');
        
        // Create tab structure
        this.renderTabStructure(container);
        
        // Load initial data
        await this.loadDashboardData();
        
        // Render default tab
        this.switchTab('dashboard');
    }

    /**
     * Create 6-tab interface structure
     */
    renderTabStructure(container) {
        const html = `
            <div class="reactivation-module">
                <!-- Module Header -->
                <div class="module-header">
                    <div class="module-title">
                        <i class="fas fa-envelope-open-text"></i>
                        <h2>Customer Reactivation</h2>
                    </div>
                    <div class="module-actions">
                        <select id="reactivation-business-selector" class="business-selector">
                            <option value="1">InHouse Print</option>
                            <option value="2">InHouse Publishing</option>
                            <option value="3">InHouse Signs</option>
                        </select>
                        <button class="btn-primary" onclick="reactivationModule.createNewCampaign()">
                            <i class="fas fa-plus"></i> New Campaign
                        </button>
                    </div>
                </div>

                <!-- Tab Navigation -->
                <div class="module-tabs">
                    <button class="tab-btn active" data-tab="dashboard">
                        <i class="fas fa-tachometer-alt"></i> Dashboard
                    </button>
                    <button class="tab-btn" data-tab="customer-insights">
                        <i class="fas fa-users"></i> Customer Insights
                    </button>
                    <button class="tab-btn" data-tab="campaigns">
                        <i class="fas fa-paper-plane"></i> Campaigns
                    </button>
                    <button class="tab-btn" data-tab="templates">
                        <i class="fas fa-file-alt"></i> Templates
                    </button>
                    <button class="tab-btn" data-tab="analytics">
                        <i class="fas fa-chart-line"></i> Analytics
                    </button>
                    <button class="tab-btn" data-tab="settings">
                        <i class="fas fa-cog"></i> Settings
                    </button>
                </div>

                <!-- Tab Content Container -->
                <div id="reactivation-tab-content" class="tab-content">
                    <!-- Content rendered dynamically -->
                </div>
            </div>
        `;
        
        container.innerHTML = html;
        
        // Attach event listeners
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.currentTarget.dataset.tab;
                this.switchTab(tab);
            });
        });
        
        document.getElementById('reactivation-business-selector').addEventListener('change', (e) => {
            this.currentBusinessId = parseInt(e.target.value);
            this.refreshCurrentTab();
        });
    }

    /**
     * Switch between tabs
     */
    switchTab(tabName) {
        this.currentTab = tabName;
        
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });
        
        // Render tab content
        const contentContainer = document.getElementById('reactivation-tab-content');
        
        switch (tabName) {
            case 'dashboard':
                this.renderDashboard(contentContainer);
                break;
            case 'customer-insights':
                this.renderCustomerInsights(contentContainer);
                break;
            case 'campaigns':
                this.renderCampaigns(contentContainer);
                break;
            case 'templates':
                this.renderTemplates(contentContainer);
                break;
            case 'analytics':
                this.renderAnalytics(contentContainer);
                break;
            case 'settings':
                this.renderSettings(contentContainer);
                break;
        }
    }

    /**
     * Refresh current tab (after business selector change)
     */
    async refreshCurrentTab() {
        await this.loadDashboardData();
        this.switchTab(this.currentTab);
    }

    // ========================================================================
    // DASHBOARD TAB
    // ========================================================================

    async loadDashboardData() {
        try {
            const response = await fetch(`/api/reactivation/dashboard?user_id=1&business_id=${this.currentBusinessId}`);
            const data = await response.json();
            
            if (data.success) {
                this.dashboardStats = data.stats;
            }
        } catch (error) {
            console.error('[REACTIVATION] Failed to load dashboard:', error);
            showNotification('Failed to load dashboard data', 'error');
        }
    }

    renderDashboard(container) {
        const stats = this.dashboardStats || {};
        
        const html = `
            <div class="dashboard-view">
                <!-- KPI Metrics Cards -->
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-exclamation-triangle" style="color: #f85149;"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value">${stats.at_risk_customers?.high_risk || 0}</div>
                            <div class="metric-label">High Risk Customers</div>
                            <div class="metric-sublabel">≥80% churn probability</div>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-envelope" style="color: #58a6ff;"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value">${stats.emails_sent?.toLocaleString() || 0}</div>
                            <div class="metric-label">Emails Sent</div>
                            <div class="metric-sublabel">${stats.total_campaigns || 0} campaigns</div>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-shopping-cart" style="color: #238636;"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value">${stats.total_reorders || 0}</div>
                            <div class="metric-label">Customer Reorders</div>
                            <div class="metric-sublabel">${stats.reorder_rate?.toFixed(1) || 0}% conversion</div>
                        </div>
                    </div>
                    
                    <div class="metric-card success">
                        <div class="metric-icon">
                            <i class="fas fa-dollar-sign" style="color: #238636;"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value">$${(stats.revenue_recovered || 0).toLocaleString()}</div>
                            <div class="metric-label">Revenue Recovered</div>
                            <div class="metric-sublabel">${stats.roi_percentage?.toFixed(0) || 0}% ROI</div>
                        </div>
                    </div>
                </div>

                <!-- Performance Metrics Row -->
                <div class="performance-row">
                    <div class="performance-card">
                        <div class="performance-label">Average Open Rate</div>
                        <div class="performance-value">${stats.avg_open_rate?.toFixed(1) || 0}%</div>
                        <div class="performance-bar">
                            <div class="performance-fill" style="width: ${stats.avg_open_rate || 0}%; background: #58a6ff;"></div>
                        </div>
                    </div>
                    
                    <div class="performance-card">
                        <div class="performance-label">Average Click Rate</div>
                        <div class="performance-value">${stats.avg_click_rate?.toFixed(1) || 0}%</div>
                        <div class="performance-bar">
                            <div class="performance-fill" style="width: ${stats.avg_click_rate || 0}%; background: #1f6feb;"></div>
                        </div>
                    </div>
                </div>

                <!-- Quick Actions -->
                <div class="dashboard-actions">
                    <button class="action-btn" onclick="reactivationModule.switchTab('customer-insights')">
                        <i class="fas fa-users"></i>
                        <span>View At-Risk Customers</span>
                    </button>
                    <button class="action-btn" onclick="reactivationModule.createNewCampaign()">
                        <i class="fas fa-paper-plane"></i>
                        <span>Create Campaign</span>
                    </button>
                    <button class="action-btn" onclick="reactivationModule.syncXeroData()">
                        <i class="fas fa-sync-alt"></i>
                        <span>Sync Xero Data</span>
                    </button>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    }

    // ========================================================================
    // CUSTOMER INSIGHTS TAB
    // ========================================================================

    async renderCustomerInsights(container) {
        container.innerHTML = `
            <div class="customer-insights-view">
                <div class="insights-header">
                    <h3>At-Risk Customers from Xero</h3>
                    <div class="insights-actions">
                        <button class="btn-secondary" onclick="reactivationModule.syncXeroData()">
                            <i class="fas fa-sync-alt"></i> Sync from Xero
                        </button>
                        <button class="btn-primary" onclick="reactivationModule.createCampaignFromSelected()">
                            <i class="fas fa-paper-plane"></i> Create Campaign (${this.selectedCustomers.length} selected)
                        </button>
                    </div>
                </div>

                <!-- Filters -->
                <div class="insights-filters">
                    <label>
                        <span>Risk Level:</span>
                        <select id="risk-filter">
                            <option value="all">All</option>
                            <option value="high">High (≥80%)</option>
                            <option value="medium">Medium (60-79%)</option>
                        </select>
                    </label>
                    <label>
                        <span>Min Revenue:</span>
                        <input type="number" id="revenue-filter" placeholder="$0" />
                    </label>
                </div>

                <!-- Customers Table -->
                <div id="customers-table"></div>
            </div>
        `;
        
        // Load customers and render table
        await this.loadAtRiskCustomers();
        this.renderCustomersTable();
    }

    async loadAtRiskCustomers(sync = false) {
        try {
            const response = await fetch(
                `/api/reactivation/at-risk-customers?business_id=${this.currentBusinessId}&min_churn_risk=60&sync=${sync}`
            );
            const data = await response.json();
            
            if (data.success) {
                this.atRiskCustomers = data.customers;
            }
        } catch (error) {
            console.error('[REACTIVATION] Failed to load customers:', error);
            showNotification('Failed to load customer data', 'error');
        }
    }

    renderCustomersTable() {
        if (this.customersTable) {
            this.customersTable.destroy();
        }
        
        this.customersTable = new Tabulator("#customers-table", {
            data: this.atRiskCustomers,
            layout: "fitDataStretch",
            pagination: "local",
            paginationSize: 20,
            selectable: true,
            columns: [
                { formatter: "rowSelection", titleFormatter: "rowSelection", width: 40, hozAlign: "center", headerSort: false },
                {
                    title: "Customer Name",
                    field: "contact_name",
                    width: 200,
                    formatter: (cell) => {
                        const data = cell.getData();
                        return `<div class="customer-cell">
                            <div class="customer-name">${data.contact_name}</div>
                            <div class="customer-email">${data.email || 'No email'}</div>
                        </div>`;
                    }
                },
                {
                    title: "Risk Level",
                    field: "churn_risk_score",
                    width: 120,
                    hozAlign: "center",
                    formatter: (cell) => {
                        const score = cell.getValue();
                        const level = score >= 80 ? 'High' : 'Medium';
                        const color = score >= 80 ? '#f85149' : '#f0883e';
                        return `<div class="risk-badge" style="background: ${color}20; color: ${color}; border: 1px solid ${color};">
                            <strong>${score}%</strong> ${level}
                        </div>`;
                    },
                    sorter: "number"
                },
                {
                    title: "Months Inactive",
                    field: "months_since_last_order",
                    width: 140,
                    hozAlign: "center",
                    formatter: (cell) => {
                        const months = cell.getValue();
                        return `<span style="color: #8b949e;">${months} months</span>`;
                    }
                },
                {
                    title: "Total Revenue",
                    field: "total_revenue",
                    width: 130,
                    hozAlign: "right",
                    formatter: (cell) => {
                        return `<span style="color: #238636;">$${cell.getValue().toLocaleString()}</span>`;
                    }
                },
                {
                    title: "Avg Order",
                    field: "average_order_value",
                    width: 110,
                    hozAlign: "right",
                    formatter: (cell) => `$${cell.getValue().toLocaleString()}`
                },
                {
                    title: "Last Order",
                    field: "last_invoice_date",
                    width: 120,
                    formatter: (cell) => {
                        const date = new Date(cell.getValue());
                        return date.toLocaleDateString();
                    }
                },
                {
                    title: "Actions",
                    field: "contact_id",
                    width: 100,
                    hozAlign: "center",
                    formatter: (cell) => {
                        return `<button class="btn-link" onclick="reactivationModule.viewXeroContact('${cell.getValue()}')">
                            <i class="fas fa-external-link-alt"></i> View in Xero
                        </button>`;
                    }
                }
            ]
        });
        
        // Track selected customers
        this.customersTable.on("rowSelectionChanged", (data, rows) => {
            this.selectedCustomers = data;
            // Update button text
            const btn = document.querySelector('.insights-actions .btn-primary');
            if (btn) {
                btn.innerHTML = `<i class="fas fa-paper-plane"></i> Create Campaign (${data.length} selected)`;
            }
        });
    }

    // ========================================================================
    // CAMPAIGNS TAB
    // ========================================================================

    async renderCampaigns(container) {
        container.innerHTML = `
            <div class="campaigns-view">
                <div class="campaigns-header">
                    <h3>Email Campaigns</h3>
                    <div class="campaigns-filters">
                        <select id="campaign-status-filter">
                            <option value="">All Statuses</option>
                            <option value="draft">Draft</option>
                            <option value="sending">Sending</option>
                            <option value="completed">Completed</option>
                        </select>
                    </div>
                </div>

                <div id="campaigns-table"></div>
            </div>
        `;
        
        await this.loadCampaigns();
        this.renderCampaignsTable();
    }

    async loadCampaigns() {
        try {
            const response = await fetch(`/api/reactivation/campaigns?user_id=1&business_id=${this.currentBusinessId}`);
            const data = await response.json();
            
            if (data.success) {
                this.campaigns = data.campaigns;
            }
        } catch (error) {
            console.error('[REACTIVATION] Failed to load campaigns:', error);
        }
    }

    renderCampaignsTable() {
        if (this.campaignsTable) {
            this.campaignsTable.destroy();
        }
        
        this.campaignsTable = new Tabulator("#campaigns-table", {
            data: this.campaigns,
            layout: "fitDataStretch",
            pagination: "local",
            paginationSize: 15,
            columns: [
                {
                    title: "Campaign Name",
                    field: "campaign_name",
                    width: 250,
                    formatter: (cell) => {
                        const data = cell.getData();
                        return `<div class="campaign-cell">
                            <div class="campaign-name">${data.campaign_name}</div>
                            <div class="campaign-type">${data.campaign_type}</div>
                        </div>`;
                    }
                },
                {
                    title: "Status",
                    field: "status",
                    width: 110,
                    hozAlign: "center",
                    formatter: (cell) => {
                        const status = cell.getValue();
                        const colors = {
                            draft: '#8b949e',
                            sending: '#1f6feb',
                            completed: '#238636'
                        };
                        return `<span class="status-badge" style="background: ${colors[status]}20; color: ${colors[status]};">
                            ${status.toUpperCase()}
                        </span>`;
                    }
                },
                {
                    title: "Recipients",
                    field: "total_recipients",
                    width: 100,
                    hozAlign: "center"
                },
                {
                    title: "Opens",
                    field: "opens",
                    width: 80,
                    hozAlign: "center",
                    formatter: (cell) => {
                        const data = cell.getData();
                        const rate = data.emails_sent > 0 ? (data.opens / data.emails_sent * 100) : 0;
                        return `<div>
                            <div>${cell.getValue()}</div>
                            <div style="font-size: 11px; color: #8b949e;">${rate.toFixed(1)}%</div>
                        </div>`;
                    }
                },
                {
                    title: "Clicks",
                    field: "clicks",
                    width: 80,
                    hozAlign: "center",
                    formatter: (cell) => {
                        const data = cell.getData();
                        const rate = data.emails_sent > 0 ? (data.clicks / data.emails_sent * 100) : 0;
                        return `<div>
                            <div>${cell.getValue()}</div>
                            <div style="font-size: 11px; color: #8b949e;">${rate.toFixed(1)}%</div>
                        </div>`;
                    }
                },
                {
                    title: "Reorders",
                    field: "reorders",
                    width: 90,
                    hozAlign: "center",
                    formatter: (cell) => `<span style="color: #238636; font-weight: bold;">${cell.getValue()}</span>`
                },
                {
                    title: "Revenue",
                    field: "revenue_recovered",
                    width: 120,
                    hozAlign: "right",
                    formatter: (cell) => `<span style="color: #238636;">$${cell.getValue().toLocaleString()}</span>`
                },
                {
                    title: "ROI",
                    field: "roi_percentage",
                    width: 90,
                    hozAlign: "center",
                    formatter: (cell) => {
                        const roi = cell.getValue();
                        const color = roi > 0 ? '#238636' : '#f85149';
                        return `<span style="color: ${color}; font-weight: bold;">${roi.toFixed(0)}%</span>`;
                    }
                },
                {
                    title: "Actions",
                    field: "campaign_id",
                    width: 150,
                    hozAlign: "center",
                    formatter: (cell) => {
                        const campaignId = cell.getValue();
                        return `<div class="action-buttons">
                            <button class="btn-link" onclick="reactivationModule.viewCampaignAnalytics(${campaignId})">
                                <i class="fas fa-chart-line"></i> Analytics
                            </button>
                        </div>`;
                    }
                }
            ]
        });
    }

    // ========================================================================
    // TEMPLATES TAB
    // ========================================================================

    async renderTemplates(container) {
        container.innerHTML = `
            <div class="templates-view">
                <div class="templates-header">
                    <h3>Email Templates</h3>
                    <button class="btn-primary" onclick="reactivationModule.createNewTemplate()">
                        <i class="fas fa-plus"></i> New Template
                    </button>
                </div>

                <div id="templates-grid" class="templates-grid">
                    <!-- Templates rendered here -->
                </div>
            </div>
        `;
        
        await this.loadTemplates();
        this.renderTemplatesGrid();
    }

    async loadTemplates() {
        try {
            const response = await fetch('/api/reactivation/templates?user_id=1');
            const data = await response.json();
            
            if (data.success) {
                this.templates = data.templates;
            }
        } catch (error) {
            console.error('[REACTIVATION] Failed to load templates:', error);
        }
    }

    renderTemplatesGrid() {
        const grid = document.getElementById('templates-grid');
        
        if (this.templates.length === 0) {
            grid.innerHTML = '<div class="empty-state">No templates found. Create your first template!</div>';
            return;
        }
        
        grid.innerHTML = this.templates.map(template => `
            <div class="template-card" data-template-id="${template.template_id}">
                <div class="template-thumbnail">
                    ${template.thumbnail_url 
                        ? `<img src="${template.thumbnail_url}" alt="${template.template_name}" />`
                        : '<i class="fas fa-envelope" style="font-size: 48px; color: #58a6ff;"></i>'
                    }
                </div>
                <div class="template-info">
                    <h4>${template.template_name}</h4>
                    <p>${template.subject}</p>
                    <div class="template-meta">
                        <span class="template-category">${template.category}</span>
                        <span class="template-usage">Used ${template.usage_count} times</span>
                    </div>
                </div>
                <div class="template-actions">
                    <button class="btn-secondary" onclick="reactivationModule.previewTemplate(${template.template_id})">
                        <i class="fas fa-eye"></i> Preview
                    </button>
                    <button class="btn-primary" onclick="reactivationModule.useTemplate(${template.template_id})">
                        <i class="fas fa-paper-plane"></i> Use
                    </button>
                </div>
            </div>
        `).join('');
    }

    // ========================================================================
    // ANALYTICS TAB
    // ========================================================================

    renderAnalytics(container) {
        container.innerHTML = `
            <div class="analytics-view">
                <h3>Campaign Analytics</h3>
                <p style="color: #8b949e; margin: 20px 0;">
                    Select a campaign from the Campaigns tab to view detailed analytics.
                </p>
            </div>
        `;
    }

    async viewCampaignAnalytics(campaignId) {
        try {
            const response = await fetch(`/api/reactivation/campaigns/${campaignId}/analytics`);
            const data = await response.json();
            
            if (!data.success) {
                showNotification('Failed to load campaign analytics', 'error');
                return;
            }
            
            // Switch to analytics tab and render
            this.switchTab('analytics');
            
            const container = document.getElementById('reactivation-tab-content');
            container.innerHTML = `
                <div class="analytics-view">
                    <div class="analytics-header">
                        <h3>Campaign Analytics</h3>
                        <button class="btn-secondary" onclick="reactivationModule.checkReorders(${campaignId})">
                            <i class="fas fa-sync-alt"></i> Check for Reorders
                        </button>
                    </div>

                    <!-- KPI Cards -->
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">${data.stats.sent}</div>
                            <div class="metric-label">Emails Sent</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${data.stats.open_rate}%</div>
                            <div class="metric-label">Open Rate</div>
                            <div class="metric-sublabel">${data.stats.opened} opens</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${data.stats.click_rate}%</div>
                            <div class="metric-label">Click Rate</div>
                            <div class="metric-sublabel">${data.stats.clicked} clicks</div>
                        </div>
                        <div class="metric-card success">
                            <div class="metric-value">${data.stats.reordered}</div>
                            <div class="metric-label">Reorders</div>
                            <div class="metric-sublabel">$${data.stats.revenue_recovered.toLocaleString()} recovered</div>
                        </div>
                    </div>

                    <!-- Timeline Chart -->
                    <div class="chart-container">
                        <h4>Event Timeline</h4>
                        <div id="timeline-chart"></div>
                    </div>
                </div>
            `;
            
            // Render timeline chart
            this.renderTimelineChart(data.timeline);
            
        } catch (error) {
            console.error('[REACTIVATION] Analytics error:', error);
            showNotification('Failed to load analytics', 'error');
        }
    }

    renderTimelineChart(timeline) {
        const eventTypes = ['sent', 'open', 'click', 'reorder'];
        const traces = eventTypes.map(type => {
            const filtered = timeline.filter(t => t.event_type === type);
            return {
                x: filtered.map(t => t.date),
                y: filtered.map(t => t.count),
                name: type.charAt(0).toUpperCase() + type.slice(1),
                type: 'scatter',
                mode: 'lines+markers'
            };
        });
        
        const layout = {
            paper_bgcolor: '#0d1117',
            plot_bgcolor: '#161b22',
            font: { color: '#c9d1d9' },
            xaxis: { gridcolor: '#30363d' },
            yaxis: { gridcolor: '#30363d', title: 'Event Count' },
            showlegend: true,
            legend: { x: 0, y: 1.1, orientation: 'h' }
        };
        
        Plotly.newPlot('timeline-chart', traces, layout);
    }

    // ========================================================================
    // SETTINGS TAB
    // ========================================================================

    renderSettings(container) {
        container.innerHTML = `
            <div class="settings-view">
                <h3>Module Settings</h3>
                
                <div class="settings-section">
                    <h4>Email Configuration</h4>
                    <label>
                        <span>From Name:</span>
                        <input type="text" id="from-name" value="InHouse Print" />
                    </label>
                    <label>
                        <span>From Email:</span>
                        <input type="email" id="from-email" value="sales@inhouseprint.com.au" />
                    </label>
                </div>

                <div class="settings-section">
                    <h4>Churn Risk Thresholds</h4>
                    <label>
                        <span>High Risk (≥):</span>
                        <input type="number" id="high-risk-threshold" value="80" min="0" max="100" />
                        <span>%</span>
                    </label>
                    <label>
                        <span>Medium Risk (≥):</span>
                        <input type="number" id="medium-risk-threshold" value="60" min="0" max="100" />
                        <span>%</span>
                    </label>
                </div>

                <div class="settings-actions">
                    <button class="btn-primary" onclick="reactivationModule.saveSettings()">
                        <i class="fas fa-save"></i> Save Settings
                    </button>
                </div>
            </div>
        `;
    }

    // ========================================================================
    // ACTIONS & WORKFLOWS
    // ========================================================================

    async syncXeroData() {
        showNotification('Syncing at-risk customers from Xero...', 'info');
        
        try {
            await this.loadAtRiskCustomers(true); // Force sync
            showNotification('Successfully synced customer data from Xero', 'success');
            
            if (this.currentTab === 'customer-insights') {
                this.renderCustomersTable();
            }
            
            await this.loadDashboardData();
        } catch (error) {
            showNotification('Failed to sync Xero data', 'error');
        }
    }

    createNewCampaign() {
        // Show campaign builder modal
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal campaign-builder">
                <div class="modal-header">
                    <h3>Create New Campaign</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()"><i class="fas fa-times"></i></button>
                </div>
                <div class="modal-body">
                    <label>
                        <span>Campaign Name:</span>
                        <input type="text" id="new-campaign-name" placeholder="e.g., Q1 2026 Win-Back" />
                    </label>
                    
                    <label>
                        <span>Template:</span>
                        <select id="new-campaign-template">
                            ${this.templates.map(t => `<option value="${t.template_id}">${t.template_name}</option>`).join('')}
                        </select>
                    </label>
                    
                    <label>
                        <span>Subject Line:</span>
                        <input type="text" id="new-campaign-subject" placeholder="We miss you! Come back for 25% off" />
                    </label>
                    
                    <label>
                        <span>Discount Code:</span>
                        <input type="text" id="new-campaign-discount" placeholder="WELCOME25" />
                    </label>
                    
                    <label>
                        <span>Discount Amount:</span>
                        <input type="number" id="new-campaign-amount" value="25" min="0" />
                        <select id="new-campaign-discount-type">
                            <option value="percentage">%</option>
                            <option value="fixed">$</option>
                        </select>
                    </label>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                    <button class="btn-primary" onclick="reactivationModule.submitNewCampaign()">Create Campaign</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    async submitNewCampaign() {
        const campaignName = document.getElementById('new-campaign-name').value;
        const templateId = parseInt(document.getElementById('new-campaign-template').value);
        const subjectLine = document.getElementById('new-campaign-subject').value;
        const discountCode = document.getElementById('new-campaign-discount').value;
        const discountAmount = parseFloat(document.getElementById('new-campaign-amount').value);
        const discountType = document.getElementById('new-campaign-discount-type').value;
        
        if (!campaignName || !subjectLine) {
            showNotification('Please fill in all required fields', 'error');
            return;
        }
        
        try {
            const response = await fetch('/api/reactivation/campaigns', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: 1,
                    campaign_name: campaignName,
                    campaign_type: 'reactivation',
                    xero_business_id: this.currentBusinessId,
                    target_segment: 'at_risk',
                    churn_threshold: 60,
                    template_id: templateId,
                    subject_line: subjectLine,
                    discount_code: discountCode,
                    discount_amount: discountAmount,
                    discount_type: discountType,
                    campaign_cost: 0
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showNotification('Campaign created successfully!', 'success');
                document.querySelector('.modal-overlay').remove();
                
                // Add recipients if customers selected
                if (this.selectedCustomers.length > 0) {
                    await this.addRecipientsToNewCampaign(data.campaign_id);
                }
                
                await this.loadCampaigns();
                this.switchTab('campaigns');
            } else {
                showNotification('Failed to create campaign', 'error');
            }
        } catch (error) {
            console.error('[REACTIVATION] Create campaign error:', error);
            showNotification('Error creating campaign', 'error');
        }
    }

    async addRecipientsToNewCampaign(campaignId) {
        try {
            const recipients = this.selectedCustomers.map(c => ({
                xero_contact_id: c.contact_id,
                xero_business_id: this.currentBusinessId,
                email: c.email,
                customer_name: c.contact_name,
                first_name: c.first_name,
                last_name: c.last_name,
                phone: c.phone,
                churn_risk_score: c.churn_risk_score,
                total_revenue: c.total_revenue,
                months_since_last_order: c.months_since_last_order,
                last_product_ordered: c.last_product_ordered
            }));
            
            await fetch(`/api/reactivation/campaigns/${campaignId}/recipients`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ recipients })
            });
            
            showNotification(`Added ${recipients.length} recipients to campaign`, 'success');
        } catch (error) {
            console.error('[REACTIVATION] Add recipients error:', error);
        }
    }

    async checkReorders(campaignId) {
        showNotification('Checking Xero for new orders...', 'info');
        
        try {
            // This would call the backend check_reorders endpoint
            // Implementation would query Xero invoices and update campaign metrics
            showNotification('Reorder check complete', 'success');
        } catch (error) {
            showNotification('Failed to check reorders', 'error');
        }
    }

    viewXeroContact(contactId) {
        // Cross-module navigation to Xero module
        if (window.xeroModule) {
            window.xeroModule.viewContact(contactId);
        } else {
            window.open(`/xero/contacts/${contactId}`, '_blank');
        }
    }

    saveSettings() {
        showNotification('Settings saved successfully', 'success');
    }
}

// Initialize module
const reactivationModule = new CustomerReactivationModule();
