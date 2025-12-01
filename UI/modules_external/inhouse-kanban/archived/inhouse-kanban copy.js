/**
 * InHousePrint Production Workflow Module
 * AI-Integrated Kanban board for production tracking
 * 
 * Features:
 * - Real-time job tracking from SQL Server
 * - AI-powered priority scoring (0-999)
 * - Customer tier badges (VIP/Premium/Regular/New)
 * - WIP status indicators (DELAYED/AT_RISK/ON_TRACK)
 * - Multi-stage workflow visualization
 * - Advanced filtering and search
 * - Responsive Kanban layout
 * - Job detail modals
 * 
 * @class InhouseKanbanModule
 * @extends BaseModule
 * @created 2025-11-03
 */
class InhouseKanbanModule extends BaseModule {
    constructor(moduleId) {
        super(moduleId);

        // Configuration
        this.apiEndpoint = '/api/inhouse-kanban';
        this.backendUrl = 'http://localhost:5001';

        // State management
        this.jobs = [];
        this.stages = [];
        this.metrics = {};
        this.filters = {
            timeframe_months: -6,
            priority_filter: 'all',
            stage_id: null,
            search_text: ''
        };

        // UI State
        this.currentView = 'kanban-board';
        this.selectedJob = null;

        // Data cache
        this.dataCache = new Map();
        this.lastRefresh = null;

        // Auto-refresh timer
        this.refreshTimer = null;
    }

    /**
     * Initialize module
     */
    async initialize() {
        console.log('🔧 Initializing InHouse Print Production Workflow module...');

        // Initialize UI from BaseModule (loads manifest first)
        await super.initialize();

        // Apply module colors (after manifest is loaded)
        this.applyModuleColors();

        // Load initial data
        await this.loadInitialData();

        // Set up event listeners
        this.setupEventListeners();

        // Start auto-refresh
        this.startAutoRefresh();

        console.log('✅ InHouse Print Production Workflow module ready');
    }

    /**
     * Apply module-specific colors as CSS variables
     */
    applyModuleColors() {
        // CRITICAL: Safe null-checking for manifest colors
        // Manifest is loaded by super.initialize(), check it exists
        if (!this.manifest || !this.manifest.colors) {
            console.warn('⚠️ Manifest or colors not available, using defaults');
            return;
        }

        const colors = this.manifest.colors;
        const tabContainer = document.getElementById(`tab-${this.moduleId}`);

        if (tabContainer) {
            tabContainer.style.setProperty('--module-primary', colors.primary);
            tabContainer.style.setProperty('--module-secondary', colors.secondary);
            tabContainer.style.setProperty('--module-hover', colors.hover);
            tabContainer.style.setProperty('--module-primary-light', this.lightenColor(colors.primary, 0.1));
        }
    }

    /**
     * Lighten color for backgrounds
     */
    lightenColor(color, opacity) {
        const hex = color.replace('#', '');
        const r = parseInt(hex.substr(0, 2), 16);
        const g = parseInt(hex.substr(2, 2), 16);
        const b = parseInt(hex.substr(4, 2), 16);
        return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    }

    /**
     * Load initial data
     */
    async loadInitialData() {
        try {
            await Promise.all([
                this.loadJobs(),
                this.loadStages(),
                this.loadMetrics()
            ]);
            this.lastRefresh = new Date();
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.showNotification('error', 'Failed to load data from InHouse Print system');
        }
    }

    /**
     * Load jobs from backend
     */
    async loadJobs() {
        try {
            const params = new URLSearchParams({
                timeframe_months: this.filters.timeframe_months,
                priority_filter: this.filters.priority_filter,
                limit: 200
            });

            if (this.filters.stage_id) {
                params.append('stage_id', this.filters.stage_id);
            }

            const response = await fetch(`${this.backendUrl}${this.apiEndpoint}/jobs?${params}`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.jobs = data.jobs || [];

            // Apply client-side search filter
            if (this.filters.search_text) {
                this.jobs = this.jobs.filter(job =>
                    job.ClientName?.toLowerCase().includes(this.filters.search_text.toLowerCase()) ||
                    job.ShortJobDesc?.toLowerCase().includes(this.filters.search_text.toLowerCase()) ||
                    job.TicketID?.toString().includes(this.filters.search_text)
                );
            }

            console.log(`Loaded ${this.jobs.length} jobs`);

        } catch (error) {
            console.error('Failed to load jobs:', error);
            throw error;
        }
    }

    /**
     * Load stages summary
     */
    async loadStages() {
        try {
            const response = await fetch(
                `${this.backendUrl}${this.apiEndpoint}/stages?timeframe_months=${this.filters.timeframe_months}`
            );

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.stages = data.stages || [];

        } catch (error) {
            console.error('Failed to load stages:', error);
            throw error;
        }
    }

    /**
     * Load dashboard metrics
     */
    async loadMetrics() {
        try {
            const response = await fetch(
                `${this.backendUrl}${this.apiEndpoint}/metrics?timeframe_months=${this.filters.timeframe_months}`
            );

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.metrics = data.metrics || {};

        } catch (error) {
            console.error('Failed to load metrics:', error);
            throw error;
        }
    }

    /**
     * Refresh all data
     */
    async refreshData() {
        console.log('Refreshing InHouse Print data...');
        const refreshBtn = document.getElementById('inhouse-refresh-btn');
        if (refreshBtn) {
            refreshBtn.innerHTML = '<i class="fas fa-sync fa-spin"></i> Refreshing...';
            refreshBtn.disabled = true;
        }

        try {
            await this.loadInitialData();

            // Re-render current view
            if (this.currentView === 'kanban-board') {
                this.renderKanbanBoard();
            } else if (this.currentView === 'analytics') {
                this.renderAnalytics();
            }

            this.showNotification('success', 'Data refreshed successfully');

        } catch (error) {
            this.showNotification('error', 'Failed to refresh data');
        } finally {
            if (refreshBtn) {
                refreshBtn.innerHTML = '<i class="fas fa-sync"></i> Refresh';
                refreshBtn.disabled = false;
            }
        }
    }

    /**
     * Initialize sub-tabs
     */
    initializeSubTabs() {
        this.initializeKanbanBoard();
        this.initializeAnalytics();
    }

    /**
     * Initialize Kanban Board tab
     */
    initializeKanbanBoard() {
        const container = this.getSubTabContainer('kanban-board');
        const primaryColor = this.manifest?.colors?.primary || '#00509E';

        container.innerHTML = `
            <div class="module-header" style="border-bottom-color: ${primaryColor};">
                <div class="module-header-left">
                    <h2 class="module-title">
                        <i class="fas fa-industry" style="color: ${primaryColor};"></i>
                        InHouse Print Production Workflow
                    </h2>
                    <p class="module-description">Real-time production tracking with AI priority scoring</p>
                </div>
                <div class="module-header-right">
                    <button id="inhouse-refresh-btn" class="btn-secondary" style="border-color: ${primaryColor};">
                        <i class="fas fa-sync"></i> Refresh
                    </button>
                </div>
            </div>
            
            <!-- Filters Bar -->
            <div class="filters-bar">
                <div class="filter-group">
                    <label><i class="fas fa-calendar-alt"></i> Timeframe:</label>
                    <select id="timeframe-selector" class="filter-select">
                        <option value="-1">Last 1 month</option>
                        <option value="-2">Last 2 months</option>
                        <option value="-3">Last 3 months</option>
                        <option value="-6" selected>Last 6 months</option>
                        <option value="-9">Last 9 months</option>
                        <option value="-12">Last 12 months</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label><i class="fas fa-filter"></i> Priority:</label>
                    <select id="priority-selector" class="filter-select">
                        <option value="all">All Priorities</option>
                        <option value="critical">Critical Only</option>
                        <option value="high">High Priority</option>
                        <option value="urgent">Urgent</option>
                        <option value="normal">Normal</option>
                        <option value="low">Low Priority</option>
                    </select>
                </div>
                
                <div class="filter-group" style="flex: 1;">
                    <label><i class="fas fa-search"></i> Search:</label>
                    <input type="text" id="search-input" class="filter-input" placeholder="Search by client, job, or ticket #...">
                </div>
                
                <div class="filter-group">
                    <span class="last-refresh" id="last-refresh-time">
                        Last refresh: <span class="time-value">-</span>
                    </span>
                </div>
            </div>
            
            <!-- Metrics Row -->
            <div class="kanban-metrics" id="kanban-metrics"></div>
            
            <!-- Kanban Board -->
            <div class="kanban-board" id="kanban-board"></div>
        `;

        // Render initial content
        this.renderMetrics();
        this.renderKanbanBoard();
        this.updateLastRefreshTime();
    }

    /**
     * Render top metrics row
     */
    renderMetrics() {
        const container = document.getElementById('kanban-metrics');
        if (!container) return;

        const primaryColor = this.manifest?.colors?.primary || '#00509E';

        container.innerHTML = `
            ${this.createMetricCard('Total Active Jobs', this.metrics.total_jobs || 0, 'fas fa-clipboard-list', primaryColor)}
            ${this.createMetricCard('Pipeline Value', '$' + this.formatCurrency(this.metrics.pipeline_value || 0), 'fas fa-dollar-sign', '#22c55e')}
            ${this.createMetricCard('Overdue Jobs', this.metrics.overdue_jobs || 0, 'fas fa-exclamation-triangle', '#ef4444')}
            ${this.createMetricCard('Avg Days in System', (this.metrics.avg_days_in_system || 0).toFixed(1), 'fas fa-clock', '#f97316')}
        `;
    }

    /**
     * Create metric card HTML
     */
    createMetricCard(label, value, icon, color) {
        return `
            <div class="metric-card">
                <div class="metric-icon" style="background: ${this.lightenColor(color, 0.1)}; color: ${color};">
                    <i class="${icon}"></i>
                </div>
                <div class="metric-content">
                    <div class="metric-value">${value}</div>
                    <div class="metric-label">${label}</div>
                </div>
            </div>
        `;
    }

    /**
     * Render Kanban board
     */
    renderKanbanBoard() {
        const container = document.getElementById('kanban-board');
        if (!container) return;

        // Group jobs by stage
        const jobsByStage = {};
        this.stages.forEach(stage => {
            jobsByStage[stage.StageID] = [];
        });

        this.jobs.forEach(job => {
            if (jobsByStage[job.StageID]) {
                jobsByStage[job.StageID].push(job);
            }
        });

        // Render columns
        container.innerHTML = this.stages
            .map(stage => this.renderStageColumn(stage, jobsByStage[stage.StageID] || []))
            .join('');
    }

    /**
     * Render stage column
     */
    renderStageColumn(stage, jobs) {
        const primaryColor = this.manifest?.colors?.primary || '#00509E';

        return `
            <div class="kanban-column" data-stage-id="${stage.StageID}">
                <div class="column-header" style="border-bottom-color: ${primaryColor};">
                    <h3 class="column-title">${this.escapeHtml(stage.StageDescription || 'Unknown Stage')}</h3>
                    <div class="column-metrics">
                        <span class="job-count"><i class="fas fa-box"></i> ${stage.JobCount || 0} jobs</span>
                        <span class="stage-value"><i class="fas fa-dollar-sign"></i> ${this.formatCurrency(stage.TotalValue || 0)}</span>
                    </div>
                </div>
                
                <div class="column-body">
                    ${jobs.length > 0 ? jobs.map(job => this.renderJobCard(job)).join('') : '<div class="empty-column">No jobs in this stage</div>'}
                </div>
            </div>
        `;
    }

    /**
     * Render job card (using Streamlit data fields)
     */
    renderJobCard(job) {
        const priorityColor = job.PriorityColorHex || '#6b7280';
        const tierColor = job.CustomerTierColorHex || '#6b7280';
        const wipColor = job.WIPColorHex || '#6b7280';

        return `
            <div class="kanban-card" 
                 data-job-id="${job.TicketID}"
                 data-priority="${job.PriorityLabel}"
                 style="border-left: 4px solid ${priorityColor};">
                
                <div class="card-header-row">
                    <div class="priority-badge" style="background-color: ${priorityColor};">
                        ${job.PriorityLabel || 'NORMAL'}
                    </div>
                    <div class="customer-tier" style="background-color: ${tierColor};">
                        ${job.CustomerTier || 'Regular'}
                    </div>
                </div>
                
                <div class="card-body">
                    <div class="client-name">
                        <i class="fas fa-building"></i>
                        ${this.escapeHtml(job.ClientName || 'Unknown Client')}
                    </div>
                    
                    <div class="job-description">
                        ${this.escapeHtml(job.ShortJobDesc || 'No description')}
                    </div>
                    
                    <div class="job-specs">
                        <span class="spec-item"><i class="fas fa-hashtag"></i> ${job.TicketID}</span>
                        <span class="spec-item"><i class="fas fa-boxes"></i> ${job.QTY || 0}</span>
                        <span class="spec-item"><i class="fas fa-dollar-sign"></i> ${this.formatCurrency(job.Cost || 0)}</span>
                    </div>
                    
                    ${this.renderJobDetails(job)}
                    
                    <div class="card-footer-row">
                        <div class="due-date ${this.getDueDateClass(job.UrgencyLevel)}">
                            <i class="fas fa-calendar-alt"></i>
                            ${this.formatDate(job.DateRequired)}
                        </div>
                        <div class="wip-status" style="color: ${wipColor};">
                            <i class="fas fa-hourglass-half"></i>
                            ${job.WIPStatus} (${job.DaysInSystem || 0}d)
                        </div>
                    </div>
                </div>
                
                <div class="card-actions">
                    <button class="view-details-btn" onclick="window.ModuleRegistry['inhouse-kanban'].showJobDetailsModal(${job.TicketID})">
                        <i class="fas fa-eye"></i> View Details
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Render job detail fields
     */
    renderJobDetails(job) {
        const details = [];

        if (job.Paper) details.push(`<span><strong>Paper:</strong> ${job.Paper}</span>`);
        if (job.GSM) details.push(`<span><strong>GSM:</strong> ${job.GSM}</span>`);
        if (job.JobSize) details.push(`<span><strong>Size:</strong> ${job.JobSize}</span>`);
        if (job.Pages) details.push(`<span><strong>Pages:</strong> ${job.Pages}</span>`);
        if (job.Binding) details.push(`<span><strong>Binding:</strong> ${job.Binding}</span>`);

        if (details.length === 0) return '';

        return `<div class="job-details">${details.join('')}</div>`;
    }

    /**
     * Get due date CSS class
     */
    getDueDateClass(urgencyLevel) {
        if (!urgencyLevel) return '';
        return urgencyLevel.toLowerCase();
    }

    /**
     * Show job details modal
     */
    async showJobDetailsModal(jobId) {
        try {
            // Show loading
            this.showLoadingModal();

            // Fetch job details
            const response = await fetch(`${this.backendUrl}${this.apiEndpoint}/jobs/${jobId}`);

            if (!response.ok) {
                throw new Error('Failed to fetch job details');
            }

            const data = await response.json();
            const job = data.job;

            // Create modal
            const modalHtml = `
                <div class="modal-overlay" id="job-details-modal" onclick="if(event.target === this) this.remove();">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h2>
                                <i class="fas fa-clipboard-list"></i>
                                Job Details - Ticket #${job.TicketID}
                            </h2>
                            <button class="modal-close" onclick="document.getElementById('job-details-modal').remove();">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        
                        <div class="modal-body">
                            <!-- Status Badges -->
                            <div class="status-badges">
                                <span class="badge badge-priority" style="background-color: ${job.PriorityColorHex};">
                                    ${job.PriorityLabel} Priority (Score: ${job.AIPriorityScore})
                                </span>
                                <span class="badge badge-tier" style="background-color: ${job.CustomerTierColorHex};">
                                    ${job.CustomerTier} Customer
                                </span>
                                <span class="badge badge-wip" style="background-color: ${job.WIPColorHex};">
                                    ${job.WIPStatus}
                                </span>
                            </div>
                            
                            <!-- Client Information -->
                            <div class="detail-section">
                                <h3><i class="fas fa-building"></i> Client Information</h3>
                                <div class="detail-grid">
                                    <div class="detail-item">
                                        <span class="detail-label">Client Name:</span>
                                        <span class="detail-value">${this.escapeHtml(job.ClientName)}</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="detail-label">Order ID:</span>
                                        <span class="detail-value">${job.OrderID}</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="detail-label">Order Date:</span>
                                        <span class="detail-value">${this.formatDate(job.OrderDate)}</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="detail-label">Business Division:</span>
                                        <span class="detail-value">${job.BusinessDivision || 'InHousePrint'}</span>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Job Specifications -->
                            <div class="detail-section">
                                <h3><i class="fas fa-file-alt"></i> Job Specifications</h3>
                                <div class="detail-grid">
                                    <div class="detail-item">
                                        <span class="detail-label">Description:</span>
                                        <span class="detail-value">${this.escapeHtml(job.ShortJobDesc || 'N/A')}</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="detail-label">Quantity:</span>
                                        <span class="detail-value">${job.QTY || 0}</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="detail-label">Cost:</span>
                                        <span class="detail-value">$${this.formatCurrency(job.Cost || 0)}</span>
                                    </div>
                                    ${job.Paper ? `
                                    <div class="detail-item">
                                        <span class="detail-label">Paper:</span>
                                        <span class="detail-value">${job.Paper}</span>
                                    </div>` : ''}
                                    ${job.GSM ? `
                                    <div class="detail-item">
                                        <span class="detail-label">GSM:</span>
                                        <span class="detail-value">${job.GSM}</span>
                                    </div>` : ''}
                                    ${job.JobSize ? `
                                    <div class="detail-item">
                                        <span class="detail-label">Size:</span>
                                        <span class="detail-value">${job.JobSize}</span>
                                    </div>` : ''}
                                    ${job.Pages ? `
                                    <div class="detail-item">
                                        <span class="detail-label">Pages:</span>
                                        <span class="detail-value">${job.Pages}</span>
                                    </div>` : ''}
                                    ${job.Binding ? `
                                    <div class="detail-item">
                                        <span class="detail-label">Binding:</span>
                                        <span class="detail-value">${job.Binding}</span>
                                    </div>` : ''}
                                </div>
                            </div>
                            
                            <!-- Finishing Options -->
                            ${job.Cello || job.Folding || job.Stitching ? `
                            <div class="detail-section">
                                <h3><i class="fas fa-magic"></i> Finishing Options</h3>
                                <div class="detail-grid">
                                    ${job.Cello ? `
                                    <div class="detail-item">
                                        <span class="detail-label">Cello:</span>
                                        <span class="detail-value">${job.Cello}</span>
                                    </div>` : ''}
                                    ${job.Folding ? `
                                    <div class="detail-item">
                                        <span class="detail-label">Folding:</span>
                                        <span class="detail-value">${job.Folding}</span>
                                    </div>` : ''}
                                    ${job.Stitching ? `
                                    <div class="detail-item">
                                        <span class="detail-label">Stitching:</span>
                                        <span class="detail-value">${job.Stitching}</span>
                                    </div>` : ''}
                                </div>
                            </div>` : ''}
                            
                            <!-- Production Notes -->
                            ${job.TicketNotes ? `
                            <div class="detail-section">
                                <h3><i class="fas fa-sticky-note"></i> Production Notes</h3>
                                <div class="notes-content">
                                    ${this.escapeHtml(job.TicketNotes)}
                                </div>
                            </div>` : ''}
                            
                            <!-- Status Information -->
                            <div class="detail-section">
                                <h3><i class="fas fa-info-circle"></i> Status Information</h3>
                                <div class="detail-grid">
                                    <div class="detail-item">
                                        <span class="detail-label">Current Stage:</span>
                                        <span class="detail-value">${job.StageDescription}</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="detail-label">Due Date:</span>
                                        <span class="detail-value ${this.getDueDateClass(job.UrgencyLevel)}">${this.formatDate(job.DateRequired)}</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="detail-label">Days in System:</span>
                                        <span class="detail-value">${job.DaysInSystem || 0} days</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="detail-label">Urgency Level:</span>
                                        <span class="detail-value">${job.UrgencyLevel}</span>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Shipping -->
                            ${job.Shipping ? `
                            <div class="detail-section">
                                <h3><i class="fas fa-shipping-fast"></i> Shipping</h3>
                                <div class="notes-content">
                                    ${this.escapeHtml(job.Shipping)}
                                </div>
                            </div>` : ''}
                        </div>
                        
                        <div class="modal-footer">
                            <button class="btn-secondary" onclick="document.getElementById('job-details-modal').remove();">
                                <i class="fas fa-times"></i> Close
                            </button>
                        </div>
                    </div>
                </div>
            `;

            // Remove loading modal
            const loadingModal = document.getElementById('loading-modal');
            if (loadingModal) loadingModal.remove();

            // Add modal to DOM
            document.body.insertAdjacentHTML('beforeend', modalHtml);

        } catch (error) {
            console.error('Failed to show job details:', error);
            const loadingModal = document.getElementById('loading-modal');
            if (loadingModal) loadingModal.remove();
            this.showNotification('error', 'Failed to load job details');
        }
    }

    /**
     * Show loading modal
     */
    showLoadingModal() {
        const modalHtml = `
            <div class="modal-overlay" id="loading-modal">
                <div class="loading-spinner">
                    <i class="fas fa-spinner fa-spin fa-3x"></i>
                    <p>Loading job details...</p>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }

    /**
     * Initialize Analytics tab
     */
    initializeAnalytics() {
        const container = this.getSubTabContainer('analytics');
        const primaryColor = this.manifest?.colors?.primary || '#00509E';

        container.innerHTML = `
            <div class="module-header" style="border-bottom-color: ${primaryColor};">
                <div class="module-header-left">
                    <h2 class="module-title">
                        <i class="fas fa-chart-line" style="color: ${primaryColor};"></i>
                        Workflow Analytics
                    </h2>
                    <p class="module-description">Performance metrics and bottleneck detection</p>
                </div>
            </div>
            
            <div class="analytics-container">
                <div class="dashboard-card">
                    <div class="card-header">
                        <h3 class="card-title">
                            <i class="fas fa-chart-bar" style="color: ${primaryColor};"></i>
                            Coming Soon
                        </h3>
                    </div>
                    <div class="card-content">
                        <p class="text-secondary">Advanced analytics features will be available in the next version:</p>
                        <ul class="feature-list">
                            <li><i class="fas fa-check"></i> Stage efficiency analysis</li>
                            <li><i class="fas fa-check"></i> Bottleneck detection</li>
                            <li><i class="fas fa-check"></i> Customer performance trends</li>
                            <li><i class="fas fa-check"></i> Priority distribution charts</li>
                            <li><i class="fas fa-check"></i> WIP aging reports</li>
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('inhouse-refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }

        // Timeframe selector
        const timeframeSelector = document.getElementById('timeframe-selector');
        if (timeframeSelector) {
            timeframeSelector.addEventListener('change', (e) => {
                this.filters.timeframe_months = parseInt(e.target.value);
                this.refreshData();
            });
        }

        // Priority filter
        const prioritySelector = document.getElementById('priority-selector');
        if (prioritySelector) {
            prioritySelector.addEventListener('change', (e) => {
                this.filters.priority_filter = e.target.value;
                this.refreshData();
            });
        }

        // Search input
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.filters.search_text = e.target.value.trim();
                    this.refreshData();
                }, 500);
            });
        }
    }

    /**
     * Start auto-refresh timer
     */
    startAutoRefresh() {
        // Clear existing timer
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }

        // Set up new timer (5 minutes)
        const refreshInterval = (this.manifest?.settings?.refresh_interval || 300) * 1000;
        this.refreshTimer = setInterval(() => {
            console.log('Auto-refreshing InHouse Print data...');
            this.refreshData();
        }, refreshInterval);
    }

    /**
     * Update last refresh time display
     */
    updateLastRefreshTime() {
        const timeElement = document.querySelector('#last-refresh-time .time-value');
        if (timeElement && this.lastRefresh) {
            timeElement.textContent = this.lastRefresh.toLocaleTimeString();
        }
    }

    /**
     * Format currency
     */
    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value || 0);
    }

    /**
     * Format date
     */
    formatDate(dateStr) {
        if (!dateStr) return 'N/A';
        try {
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-AU', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric'
            });
        } catch {
            return 'Invalid Date';
        }
    }

    /**
     * Escape HTML
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Show notification
     */
    showNotification(type, message) {
        console.log(`[${type.toUpperCase()}] ${message}`);

        // You can integrate with a toast notification system here
        if (type === 'error') {
            alert(`Error: ${message}`);
        }
    }

    /**
     * Cleanup
     */
    cleanup() {
        // Clear auto-refresh timer
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }

        // Clear cache
        this.dataCache.clear();

        // Call parent cleanup
        super.cleanup();
    }
}

// Register module
window.ModuleRegistry = window.ModuleRegistry || {};
window.ModuleRegistry['inhouse-kanban'] = InhouseKanbanModule;
