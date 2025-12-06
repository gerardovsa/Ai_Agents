/**
 * VSA Veterinary Alerts Module
 * Framework: ModuleLoaderV4 (Modern Composition Pattern)
 * Version: 1.0.0
 * 
 * Displays real-time veterinary call alerts and follow-up actions
 * Connected to SQL_Data_AI_UI_v5 Supabase database
 */

// V4 Module Pattern - Modern Framework
// Auto-registers in ModuleLoaderV4's module registry on import
const VSAVeterinaryAlerts = {
    // ==================== METADATA ====================
    moduleId: 'vsa-veterinary-alerts',
    version: '1.0.0',
    framework: 'v4',
    // Declare runtime dependencies so the UtilityComposer composes required utilities
    // UtilityComposer will always add a module-specific `log` regardless of this list
    dependencies: {
        utilities: ['dom', 'api', 'storage', 'events']
    },

    // ==================== STATE ====================
    state: {
        // Supabase connection
        supabaseUrl: 'https://wuwmvtslltqhaycyukxk.supabase.co',
        supabaseKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1d212dHNsbHRxaGF5Y3l1a3hrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTIyNDMzNCwiZXhwIjoyMDY2ODAwMzM0fQ.tUJ473GHC139vvH0X6fIgaFtgmLTl-VaUCf9kY6xQj4',
        supabaseClient: null,

        // Data
        alerts: [],
        followUps: [],
        veterinaryCalls: [],

        // Filters
        filters: {
            severity: 'all',        // all, high, medium, low
            priority: 'all',        // all, high, medium, low
            dateRange: 'all',       // today, week, month, all (DEFAULT: show all)
            search: '',
            category: 'all'
        },

        // UI State
        loading: false,
        error: null,
        view: 'alerts',             // alerts, followups, both
        selectedAlert: null,
        selectedFollowUp: null,

        // Refresh
        refreshInterval: null,
        lastRefresh: null,

        // Stats
        stats: {
            totalAlerts: 0,
            highPriority: 0,
            pending: 0,
            resolved: 0,
            totalFollowUps: 0
        }
    },

    // ==================== LIFECYCLE: DASHBOARD ====================

    async onDashboardLoad(utilities) {
        // Store utilities reference for V4 composition pattern - inject utilities properly
        Object.assign(this, utilities);

        this.log.info('🔷 VSA Alerts Dashboard loading (V4 Modern Framework)...');

        try {
            // ✅ USE FRAMEWORK UTILITY (matches InHouse Kanban pattern)
            // Gets 'tab-vsa-veterinary-alerts' automatically
            this.container = this.dom.getContainer();
            
            if (!this.container) {
                throw new Error('Dashboard container not found');
            }
            
            this.log.info('✅ Container found:', this.container.id);

            // ❌ REMOVED: Do NOT override display property
            // The tab system (.tab-content / .tab-content.active) handles visibility
            // Overriding display breaks tab switching - multiple tabs show at once
            // The CSS already defines:
            //   .tab-content { display: none; }
            //   .tab-content.active { display: block; }
            // Let the framework handle tab visibility - module just renders content

            // Initialize V4 dashboard structure (wrapper + header + sub-tabs)
            this.initializeSubTabs();

            // Initialize Supabase client
            await this.initializeSupabase();

            // Setup event listeners
            this.setupEventListeners();

            // Initial data load
            await this.loadAllData();

            // Render dashboard content
            this.renderDashboardContent();

            // Setup auto-refresh
            this.startAutoRefresh();

            this.log.info('VSA Alerts Dashboard loaded successfully');

        } catch (error) {
            this.log.error('Failed to load VSA Alerts Dashboard:', error);
            this.state.error = error.message;
            this.renderError();
        }
    },

    // ==================== LIFECYCLE: SIDEBAR ====================

    async onSidebarLoad(utilities) {
        // Store utilities reference for V4 composition pattern
        this.utilities = utilities;
        const { dom, api, storage, events, log } = utilities;

        // Store all utilities for access in all methods
        this.dom = dom;
        this.api = api;
        this.storage = storage;
        this.events = events;
        this.log = log;

        this.log.info('🔷 VSA Alerts Sidebar loading (V4 Modern Framework)...');

        try {
            // Check if using SidebarManager framework (V4 integration)
            if (window.SidebarManager && window.SidebarManager.sidebars.has('vsa-veterinary-alerts-sidebar')) {
                log.info('✅ Using SidebarManager framework');
                this.sidebarContainer = document.getElementById('vsa-veterinary-alerts-sidebar') ||
                    document.getElementById('vsa-sidebar-container');
            } else {
                // Fallback: Look for container created by V4 loader or HTML file
                this.sidebarContainer = document.getElementById('vsa-sidebar-container') ||
                    document.querySelector('[data-module-sidebar="vsa-veterinary-alerts"]');
            }

            if (!this.sidebarContainer) {
                throw new Error('Sidebar container not found - SidebarManager or HTML not loaded');
            }

            log.info('✅ Sidebar container found:', this.sidebarContainer.id);

            // Initialize Supabase if not already done
            if (!this.state.supabaseClient) {
                await this.initializeSupabase();
            }

            // Setup sidebar event listeners
            this.setupSidebarListeners();

            // Load quick alerts
            await this.loadQuickAlerts();

            // Render sidebar
            this.renderSidebar();

            this.log.info('VSA Alerts Sidebar loaded successfully');

        } catch (error) {
            this.log.error('Failed to load VSA Alerts Sidebar:', error);
            this.renderSidebarError(error.message);
        }
    },

    // ==================== LIFECYCLE: CLEANUP ====================

    onUnload(utilities) {
        const { log } = utilities;
        this.log = log;

        this.log.info('VSA Alerts Module unloading...');

        // Clear refresh interval
        if (this.state.refreshInterval) {
            clearInterval(this.state.refreshInterval);
            this.state.refreshInterval = null;
        }

        // Framework automatically cleans up tracked event listeners
        this.log.info('VSA Alerts Module unloaded successfully');
    },

    // ==================== V4 MODULE REGISTRY ====================

    /**
     * Module metadata for V4 ModuleLoaderV4 registry
     * Called by loader to verify module compliance
     */
    getModuleInfo() {
        return {
            id: this.moduleId,
            version: this.version,
            framework: this.framework,
            type: 'modern',
            pattern: 'composition',
            capabilities: {
                dashboard: true,
                sidebar: true,
                realtime: true,
                supabase: true
            },
            performance: {
                lazyLoad: true,
                asyncInit: true,
                compositionBased: true
            }
        };
    },

    // ==================== CONTAINER MANAGEMENT (V4) ====================

    /**
     * Get container for specific sub-tab
     */
    getSubTabContainer(tabName) {
        if (tabName) {
            const subTabContainer = document.getElementById(`vsa-subtab-${tabName}`);
            if (subTabContainer) {
                this.log.info(`Returning sub-tab container: #vsa-subtab-${tabName}`);
                return subTabContainer;
            }
        }

        const container = this.container;
        if (!container) {
            throw new Error(`Cannot find container for module ${this.moduleId}`);
        }

        return container;
    },

    /**
     * Initialize sub-tabs with V4 framework structure
     */
    initializeSubTabs() {
        this.state.activeSubTab = 'alerts';
        this.createSubTabNavigation();
        this.switchSubTab('alerts');
    },

    /**
     * Create V4 framework-standard dashboard wrapper and header
     */
    createSubTabNavigation() {
        const container = this.container;

        const navHtml = `
            <div class="dashboard-wrapper vsa-veterinary-alerts">
                <!-- Dashboard Header (V4 Framework Standard) -->
                <div class="dashboard-header">
                    <div class="dashboard-header-left">
                        <h2 class="dashboard-title">
                            <i class="fas fa-bell"></i>
                            VSA Veterinary Alerts
                        </h2>
                        <div class="dashboard-stats">
                            <span class="stat-item">
                                <i class="fas fa-bell"></i>
                                <strong id="vsa-total-alerts">0</strong> Alerts
                            </span>
                            <span class="stat-item">
                                <i class="fas fa-exclamation-circle" style="color: #ef4444;"></i>
                                <strong id="vsa-high-priority">0</strong> High Priority
                            </span>
                            <span class="stat-item">
                                <i class="fas fa-clock" style="color: #f59e0b;"></i>
                                <strong id="vsa-pending">0</strong> Pending
                            </span>
                            <span class="stat-item">
                                <i class="fas fa-check-circle" style="color: #10b981;"></i>
                                <strong id="vsa-resolved">0</strong> Resolved
                            </span>
                        </div>
                    </div>
                    <div class="dashboard-header-right">
                        <div class="dashboard-refresh-info" id="vsa-last-refresh">
                            Last updated: Never
                        </div>
                        <button class="dashboard-action-btn" data-action="refresh" title="Refresh data">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                    </div>
                </div>

                <!-- Quick Navigation Bar (Sub-tabs) -->
                <div class="quick-nav-bar">
                    <div class="quick-nav-container">
                        <button class="module-subtab-btn active" data-tab="alerts" onclick="window.vsaAlertsModule?.switchSubTab('alerts')">
                            <i class="fas fa-bell"></i>
                            Alerts
                        </button>
                        <button class="module-subtab-btn" data-tab="followups" onclick="window.vsaAlertsModule?.switchSubTab('followups')">
                            <i class="fas fa-tasks"></i>
                            Follow-ups
                        </button>
                    </div>
                </div>
                
                <!-- Sub-tab content containers -->
                <div id="vsa-subtab-alerts" class="sub-tab-content active"></div>
                <div id="vsa-subtab-followups" class="sub-tab-content" style="display: none;"></div>
            </div>
        `;

        container.innerHTML = navHtml;

        // Store global reference for onclick handlers
        window.vsaAlertsModule = this;
    },

    /**
     * Switch between sub-tabs
     */
    switchSubTab(tabName) {
        this.log.info(`🔄 Switching to sub-tab: ${tabName}`);
        this.state.activeSubTab = tabName;
        this.state.view = tabName; // Update view state

        // Update button states
        document.querySelectorAll('.quick-nav-bar .module-subtab-btn').forEach(btn => {
            if (btn.dataset.tab === tabName) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Show/hide content
        const alertsContent = document.getElementById('vsa-subtab-alerts');
        const followupsContent = document.getElementById('vsa-subtab-followups');

        if (tabName === 'alerts') {
            if (alertsContent) alertsContent.style.display = 'flex';
            if (followupsContent) followupsContent.style.display = 'none';
        } else if (tabName === 'followups') {
            if (alertsContent) alertsContent.style.display = 'none';
            if (followupsContent) followupsContent.style.display = 'flex';
        }

        // Re-render content for active tab
        this.renderDashboardContent();
    },

    createFallbackContainer() {
        // Create container if V4 loader didn't (edge case fallback)
        const container = document.createElement('div');
        container.id = 'vsa-alerts-dashboard';
        container.className = 'vsa-alerts-container';
        container.style.cssText = 'width: 100%; height: 100%; overflow: auto; padding: 20px;';

        // Find main content area and append
        const mainContent = document.querySelector('.main-content') || document.body;
        mainContent.appendChild(container);

        this.log.info('✅ Created fallback container for VSA Alerts');
        return container;
    },

    // ==================== SUPABASE INITIALIZATION ====================

    async initializeSupabase() {
        try {
            // Check if Supabase library is available
            if (typeof window.supabase === 'undefined') {
                // Load Supabase client library dynamically
                await this.loadSupabaseLibrary();
            }

            // Create Supabase client
            this.state.supabaseClient = window.supabase.createClient(
                this.state.supabaseUrl,
                this.state.supabaseKey
            );

            this.log.info('Supabase client initialized successfully');

        } catch (error) {
            this.log.error('Failed to initialize Supabase:', error);
            throw new Error('Supabase initialization failed: ' + error.message);
        }
    },

    async loadSupabaseLibrary() {
        return new Promise((resolve, reject) => {
            if (typeof window.supabase !== 'undefined') {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2';
            script.onload = () => {
                this.log.info('Supabase library loaded from CDN');
                resolve();
            };
            script.onerror = () => reject(new Error('Failed to load Supabase library'));
            document.head.appendChild(script);
        });
    },

    // ==================== DATA LOADING ====================

    async loadAllData() {
        this.state.loading = true;
        this.state.error = null;

        try {
            // Load veterinary calls with alerts
            await this.loadVeterinaryCalls();

            // Process alerts from veterinary calls
            await this.processAlerts();

            // Process follow-ups
            await this.processFollowUps();

            // Calculate stats
            this.calculateStats();

            this.state.lastRefresh = new Date();

        } catch (error) {
            this.log.error('Failed to load data:', error);
            this.state.error = error.message;
        } finally {
            this.state.loading = false;
        }
    },

    async loadVeterinaryCalls() {
        try {
            const { data, error } = await this.state.supabaseClient
                .from('veterinary_calls')
                .select('*')
                .order('key_call_date', { ascending: false })
                .limit(500);

            if (error) throw error;

            this.state.veterinaryCalls = data || [];
            this.log.info(`Loaded ${this.state.veterinaryCalls.length} veterinary calls`);

        } catch (error) {
            this.log.error('Failed to load veterinary calls:', error);
            throw error;
        }
    },

    async processAlerts() {
        try {
            // Extract alerts from key_details_reasoning_analysis field (SQL_Data_AI_UI_v5 schema)
            this.state.alerts = [];

            for (const call of this.state.veterinaryCalls) {
                const alertTags = call.key_details_reasoning_analysis;

                if (!alertTags || alertTags.trim() === '') continue;

                // Parse alerts (format: "Alert Type: Description")
                const alertLines = alertTags.split('\n').filter(line => line.trim());

                for (const line of alertLines) {
                    const match = line.match(/^(.*?):\s*(.*)$/);
                    if (match) {
                        const [, type, description] = match;

                        // Determine severity
                        const severity = this.determineSeverity(type, description);

                        this.state.alerts.push({
                            id: `${call.call_id}_${this.state.alerts.length}`,
                            callId: call.call_id,
                            callDate: call.key_call_date,
                            clientName: `${call.key_otherspeaker_firstname || ''} ${call.key_otherspeaker_lastname || ''}`.trim() || 'Unknown',
                            staffName: call.key_staffname || 'Unknown',
                            type: type.trim(),
                            description: description.trim(),
                            severity: severity,
                            status: 'pending',
                            created: call.key_call_date
                        });
                    }
                }
            }

            this.log.info(`Processed ${this.state.alerts.length} alerts`);

        } catch (error) {
            this.log.error('Failed to process alerts:', error);
            throw error;
        }
    },

    async processFollowUps() {
        try {
            // Extract follow-ups from key_details_reasoning_analysis field (SQL_Data_AI_UI_v5 schema)
            this.state.followUps = [];

            for (const call of this.state.veterinaryCalls) {
                const followUpText = call.key_details_reasoning_analysis;

                if (!followUpText || followUpText.trim() === '') continue;

                // Parse follow-ups (look for action items in analysis)
                const followUpLines = followUpText.split('\n').filter(line => line.trim());

                for (const line of followUpLines) {
                    const match = line.match(/^(.*?):\s*(.*)$/);
                    if (match) {
                        const [, category, action] = match;

                        // Determine priority
                        const priority = this.determinePriority(category, action);

                        this.state.followUps.push({
                            id: `${call.call_id}_${this.state.followUps.length}`,
                            callId: call.call_id,
                            callDate: call.key_call_date,
                            clientName: `${call.key_otherspeaker_firstname || ''} ${call.key_otherspeaker_lastname || ''}`.trim() || 'Unknown',
                            staffName: call.key_staffname || 'Unknown',
                            category: category.trim(),
                            action: action.trim(),
                            priority: priority,
                            status: 'pending',
                            created: call.key_call_date
                        });
                    }
                }
            }

            this.log.info(`Processed ${this.state.followUps.length} follow-ups`);

        } catch (error) {
            this.log.error('Failed to process follow-ups:', error);
            throw error;
        }
    },

    determineSeverity(type, description) {
        const highKeywords = ['critical', 'urgent', 'emergency', 'complaint', 'escalation', 'serious'];
        const medKeywords = ['concern', 'issue', 'problem', 'warning', 'attention'];

        const text = (type + ' ' + description).toLowerCase();

        if (highKeywords.some(kw => text.includes(kw))) return 'high';
        if (medKeywords.some(kw => text.includes(kw))) return 'medium';
        return 'low';
    },

    determinePriority(category, action) {
        const highCategories = ['Client Experience', 'Revenue Opportunity'];
        const medCategories = ['Quality Assurance', 'Staff Training'];

        if (highCategories.includes(category)) return 'high';
        if (medCategories.includes(category)) return 'medium';
        return 'low';
    },

    calculateStats() {
        this.state.stats = {
            totalAlerts: this.state.alerts.length,
            highPriority: this.state.alerts.filter(a => a.severity === 'high').length,
            pending: this.state.alerts.filter(a => a.status === 'pending').length,
            resolved: this.state.alerts.filter(a => a.status === 'resolved').length,
            totalFollowUps: this.state.followUps.length
        };
    },

    async loadQuickAlerts() {
        // Load only high priority alerts for sidebar
        await this.loadVeterinaryCalls();
        await this.processAlerts();

        // Filter to high priority only
        this.state.alerts = this.state.alerts.filter(a => a.severity === 'high').slice(0, 10);
    },

    // ==================== FILTERING ====================

    getFilteredAlerts() {
        let filtered = [...this.state.alerts];

        // Severity filter
        if (this.state.filters.severity !== 'all') {
            filtered = filtered.filter(a => a.severity === this.state.filters.severity);
        }

        // Date range filter
        const now = new Date();
        if (this.state.filters.dateRange !== 'all') {
            const daysBack = {
                'today': 1,
                'week': 7,
                'month': 30
            }[this.state.filters.dateRange] || 7;

            const cutoff = new Date(now.getTime() - (daysBack * 24 * 60 * 60 * 1000));
            filtered = filtered.filter(a => new Date(a.callDate) >= cutoff);
        }

        // Search filter
        if (this.state.filters.search) {
            const search = this.state.filters.search.toLowerCase();
            filtered = filtered.filter(a =>
                a.type.toLowerCase().includes(search) ||
                a.description.toLowerCase().includes(search) ||
                a.clientName.toLowerCase().includes(search) ||
                a.staffName.toLowerCase().includes(search)
            );
        }

        return filtered;
    },

    getFilteredFollowUps() {
        let filtered = [...this.state.followUps];

        // Priority filter
        if (this.state.filters.priority !== 'all') {
            filtered = filtered.filter(f => f.priority === this.state.filters.priority);
        }

        // Date range filter
        const now = new Date();
        if (this.state.filters.dateRange !== 'all') {
            const daysBack = {
                'today': 1,
                'week': 7,
                'month': 30
            }[this.state.filters.dateRange] || 7;

            const cutoff = new Date(now.getTime() - (daysBack * 24 * 60 * 60 * 1000));
            filtered = filtered.filter(f => new Date(f.callDate) >= cutoff);
        }

        // Search filter
        if (this.state.filters.search) {
            const search = this.state.filters.search.toLowerCase();
            filtered = filtered.filter(f =>
                f.category.toLowerCase().includes(search) ||
                f.action.toLowerCase().includes(search) ||
                f.clientName.toLowerCase().includes(search)
            );
        }

        return filtered;
    },

    // ==================== AUTO REFRESH ====================

    startAutoRefresh() {
        // Refresh every 60 seconds
        this.state.refreshInterval = setInterval(() => {
            this.log.info('Auto-refreshing alerts...');
            this.refreshData();
        }, 60000);
    },

    async refreshData() {
        try {
            await this.loadAllData();
            this.renderDashboard();
        } catch (error) {
            this.log.error('Failed to refresh data:', error);
        }
    },

    // ==================== EVENT LISTENERS ====================

    setupEventListeners() {
        // View toggle
        this.dom.on(this.container, 'click', '[data-view]', (e) => {
            this.state.view = e.currentTarget.dataset.view;
            this.renderDashboard();
        });

        // Severity filter
        this.dom.on(this.container, 'change', '[data-filter="severity"]', (e) => {
            this.state.filters.severity = e.target.value;
            this.renderDashboard();
        });

        // Priority filter
        this.dom.on(this.container, 'change', '[data-filter="priority"]', (e) => {
            this.state.filters.priority = e.target.value;
            this.renderDashboard();
        });

        // Date range filter
        this.dom.on(this.container, 'change', '[data-filter="dateRange"]', (e) => {
            this.state.filters.dateRange = e.target.value;
            this.renderDashboard();
        });

        // Search
        let searchTimeout;
        this.dom.on(this.container, 'input', '[data-search]', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.state.filters.search = e.target.value;
                this.renderDashboard();
            }, 300);
        });

        // Refresh button
        this.dom.on(this.container, 'click', '[data-action="refresh"]', () => {
            this.refreshData();
        });

        // Alert details
        this.dom.on(this.container, 'click', '[data-alert-id]', (e) => {
            const alertId = e.currentTarget.dataset.alertId;
            this.viewAlertDetails(alertId);
        });

        // Follow-up details
        this.dom.on(this.container, 'click', '[data-followup-id]', (e) => {
            const followUpId = e.currentTarget.dataset.followupId;
            this.viewFollowUpDetails(followUpId);
        });
    },

    setupSidebarListeners() {
        // Alert click
        this.dom.on(this.sidebarContainer, 'click', '[data-alert-id]', (e) => {
            const alertId = e.currentTarget.dataset.alertId;
            this.viewAlertDetails(alertId);
        });

        // View all
        this.dom.on(this.sidebarContainer, 'click', '[data-action="view-all"]', () => {
            // Switch to main dashboard
            this.events.emit('switch-tab', { tabId: 'vsa-alerts' });
        });
    },

    // ==================== RENDERING: DASHBOARD ====================

    /**
     * Render dashboard content into active sub-tab container
     */
    renderDashboardContent() {
        const container = this.getSubTabContainer(this.state.activeSubTab);
        if (!container) return;

        if (this.state.loading) {
            container.innerHTML = this.renderLoading();
            return;
        }

        if (this.state.error) {
            container.innerHTML = this.renderError();
            return;
        }

        // Update stats in header
        this.updateHeaderStats();

        // Update last refresh time
        this.updateLastRefreshTime();

        // Render content based on active view
        container.innerHTML = `
            <div class="vsa-content-wrapper">
                ${this.renderFilters()}
                ${this.renderContent()}
            </div>
        `;
    },

    /**
     * Update header statistics (called after data load)
     */
    updateHeaderStats() {
        const totalAlertsEl = document.getElementById('vsa-total-alerts');
        const highPriorityEl = document.getElementById('vsa-high-priority');
        const pendingEl = document.getElementById('vsa-pending');
        const resolvedEl = document.getElementById('vsa-resolved');

        if (totalAlertsEl) totalAlertsEl.textContent = this.state.stats.totalAlerts;
        if (highPriorityEl) highPriorityEl.textContent = this.state.stats.highPriority;
        if (pendingEl) pendingEl.textContent = this.state.stats.pending;
        if (resolvedEl) resolvedEl.textContent = this.state.stats.resolved;
    },

    /**
     * Update last refresh time display
     */
    updateLastRefreshTime() {
        const refreshEl = document.getElementById('vsa-last-refresh');
        if (refreshEl && this.state.lastRefresh) {
            const timeStr = new Date(this.state.lastRefresh).toLocaleTimeString();
            refreshEl.textContent = `Last updated: ${timeStr}`;
        }
    },

    /**
     * Legacy renderDashboard method for compatibility
     */
    renderDashboard() {
        this.renderDashboardContent();
    },

    renderStats() {
        return `
            <div class="vsa-stats">
                <div class="vsa-stat-card vsa-stat-primary">
                    <div class="vsa-stat-icon"><i class="fas fa-bell"></i></div>
                    <div class="vsa-stat-content">
                        <div class="vsa-stat-value">${this.state.stats.totalAlerts}</div>
                        <div class="vsa-stat-label">Total Alerts</div>
                    </div>
                </div>
                
                <div class="vsa-stat-card vsa-stat-danger">
                    <div class="vsa-stat-icon"><i class="fas fa-exclamation-circle"></i></div>
                    <div class="vsa-stat-content">
                        <div class="vsa-stat-value">${this.state.stats.highPriority}</div>
                        <div class="vsa-stat-label">High Priority</div>
                    </div>
                </div>
                
                <div class="vsa-stat-card vsa-stat-warning">
                    <div class="vsa-stat-icon"><i class="fas fa-clock"></i></div>
                    <div class="vsa-stat-content">
                        <div class="vsa-stat-value">${this.state.stats.pending}</div>
                        <div class="vsa-stat-label">Pending</div>
                    </div>
                </div>
                
                <div class="vsa-stat-card vsa-stat-success">
                    <div class="vsa-stat-icon"><i class="fas fa-check-circle"></i></div>
                    <div class="vsa-stat-content">
                        <div class="vsa-stat-value">${this.state.stats.resolved}</div>
                        <div class="vsa-stat-label">Resolved</div>
                    </div>
                </div>
                
                <div class="vsa-stat-card vsa-stat-info">
                    <div class="vsa-stat-icon"><i class="fas fa-tasks"></i></div>
                    <div class="vsa-stat-content">
                        <div class="vsa-stat-value">${this.state.stats.totalFollowUps}</div>
                        <div class="vsa-stat-label">Follow-ups</div>
                    </div>
                </div>
            </div>
        `;
    },

    renderFilters() {
        return `
            <div class="vsa-filters">
                <div class="vsa-view-toggle">
                    <button class="vsa-view-btn ${this.state.view === 'alerts' ? 'active' : ''}" data-view="alerts">
                        <i class="fas fa-bell"></i> Alerts
                    </button>
                    <button class="vsa-view-btn ${this.state.view === 'followups' ? 'active' : ''}" data-view="followups">
                        <i class="fas fa-tasks"></i> Follow-ups
                    </button>
                    <button class="vsa-view-btn ${this.state.view === 'both' ? 'active' : ''}" data-view="both">
                        <i class="fas fa-th-large"></i> Both
                    </button>
                </div>
                
                <div class="vsa-filter-controls">
                    ${this.state.view !== 'followups' ? `
                        <select class="vsa-select" data-filter="severity">
                            <option value="all">All Severities</option>
                            <option value="high" ${this.state.filters.severity === 'high' ? 'selected' : ''}>High</option>
                            <option value="medium" ${this.state.filters.severity === 'medium' ? 'selected' : ''}>Medium</option>
                            <option value="low" ${this.state.filters.severity === 'low' ? 'selected' : ''}>Low</option>
                        </select>
                    ` : ''}
                    
                    ${this.state.view !== 'alerts' ? `
                        <select class="vsa-select" data-filter="priority">
                            <option value="all">All Priorities</option>
                            <option value="high" ${this.state.filters.priority === 'high' ? 'selected' : ''}>High</option>
                            <option value="medium" ${this.state.filters.priority === 'medium' ? 'selected' : ''}>Medium</option>
                            <option value="low" ${this.state.filters.priority === 'low' ? 'selected' : ''}>Low</option>
                        </select>
                    ` : ''}
                    
                    <select class="vsa-select" data-filter="dateRange">
                        <option value="all" ${this.state.filters.dateRange === 'all' ? 'selected' : ''}>All Time</option>
                        <option value="today" ${this.state.filters.dateRange === 'today' ? 'selected' : ''}>Today</option>
                        <option value="week" ${this.state.filters.dateRange === 'week' ? 'selected' : ''}>This Week</option>
                        <option value="month" ${this.state.filters.dateRange === 'month' ? 'selected' : ''}>This Month</option>
                    </select>
                    
                    <input 
                        type="text" 
                        class="vsa-search" 
                        data-search
                        placeholder="Search alerts..."
                        value="${this.state.filters.search}"
                    />
                </div>
            </div>
        `;
    },

    renderContent() {
        if (this.state.view === 'alerts') {
            return this.renderAlertsList();
        } else if (this.state.view === 'followups') {
            return this.renderFollowUpsList();
        } else {
            return `
                <div class="vsa-split-view">
                    <div class="vsa-split-left">${this.renderAlertsList()}</div>
                    <div class="vsa-split-right">${this.renderFollowUpsList()}</div>
                </div>
            `;
        }
    },

    renderAlertsList() {
        const alerts = this.getFilteredAlerts();

        if (alerts.length === 0) {
            return `
                <div class="vsa-empty-state">
                    <i class="fas fa-bell-slash"></i>
                    <h3>No alerts found</h3>
                    <p>Try adjusting your filters</p>
                </div>
            `;
        }

        return `
            <div class="vsa-alerts-list">
                <h2 class="vsa-list-title">
                    <i class="fas fa-bell"></i> 
                    Alerts (${alerts.length})
                </h2>
                ${alerts.map(alert => this.renderAlertCard(alert)).join('')}
            </div>
        `;
    },

    renderAlertCard(alert) {
        const severityClass = `vsa-severity-${alert.severity}`;
        const severityBadge = {
            high: '<span class="vsa-badge vsa-badge-danger">HIGH</span>',
            medium: '<span class="vsa-badge vsa-badge-warning">MED</span>',
            low: '<span class="vsa-badge vsa-badge-success">LOW</span>'
        }[alert.severity];

        const date = new Date(alert.callDate).toLocaleDateString();
        const time = new Date(alert.callDate).toLocaleTimeString();

        return `
            <div class="vsa-alert-card ${severityClass}" data-alert-id="${alert.id}">
                <div class="vsa-alert-header">
                    <div class="vsa-alert-title-row">
                        <h4 class="vsa-alert-type">${this.escapeHtml(alert.type)}</h4>
                        ${severityBadge}
                    </div>
                    <div class="vsa-alert-meta">
                        <span><i class="fas fa-calendar"></i> ${date} ${time}</span>
                        <span><i class="fas fa-user"></i> ${this.escapeHtml(alert.clientName)}</span>
                        <span><i class="fas fa-user-md"></i> ${this.escapeHtml(alert.staffName)}</span>
                    </div>
                </div>
                <div class="vsa-alert-body">
                    <p>${this.escapeHtml(alert.description)}</p>
                </div>
                <div class="vsa-alert-footer">
                    <span class="vsa-alert-status">Status: ${alert.status}</span>
                    <button class="vsa-btn-link" data-alert-id="${alert.id}">
                        View Details <i class="fas fa-arrow-right"></i>
                    </button>
                </div>
            </div>
        `;
    },

    renderFollowUpsList() {
        const followUps = this.getFilteredFollowUps();

        if (followUps.length === 0) {
            return `
                <div class="vsa-empty-state">
                    <i class="fas fa-tasks"></i>
                    <h3>No follow-ups found</h3>
                    <p>Try adjusting your filters</p>
                </div>
            `;
        }

        return `
            <div class="vsa-followups-list">
                <h2 class="vsa-list-title">
                    <i class="fas fa-tasks"></i> 
                    Follow-ups (${followUps.length})
                </h2>
                ${followUps.map(followUp => this.renderFollowUpCard(followUp)).join('')}
            </div>
        `;
    },

    renderFollowUpCard(followUp) {
        const priorityClass = `vsa-priority-${followUp.priority}`;
        const priorityBadge = {
            high: '<span class="vsa-badge vsa-badge-danger">HIGH</span>',
            medium: '<span class="vsa-badge vsa-badge-warning">MED</span>',
            low: '<span class="vsa-badge vsa-badge-success">LOW</span>'
        }[followUp.priority];

        const date = new Date(followUp.callDate).toLocaleDateString();

        return `
            <div class="vsa-followup-card ${priorityClass}" data-followup-id="${followUp.id}">
                <div class="vsa-followup-header">
                    <div class="vsa-followup-title-row">
                        <h4 class="vsa-followup-category">${this.escapeHtml(followUp.category)}</h4>
                        ${priorityBadge}
                    </div>
                    <div class="vsa-followup-meta">
                        <span><i class="fas fa-calendar"></i> ${date}</span>
                        <span><i class="fas fa-user"></i> ${this.escapeHtml(followUp.clientName)}</span>
                    </div>
                </div>
                <div class="vsa-followup-body">
                    <p>${this.escapeHtml(followUp.action)}</p>
                </div>
                <div class="vsa-followup-footer">
                    <span class="vsa-followup-status">Status: ${followUp.status}</span>
                    <button class="vsa-btn-link" data-followup-id="${followUp.id}">
                        View Details <i class="fas fa-arrow-right"></i>
                    </button>
                </div>
            </div>
        `;
    },

    // ==================== RENDERING: SIDEBAR ====================

    renderSidebar() {
        if (!this.sidebarContainer) return;

        this.sidebarContainer.innerHTML = `
            <div class="vsa-sidebar">
                <div class="vsa-sidebar-header">
                    <h3><i class="fas fa-bell"></i> Quick Alerts</h3>
                    <button class="vsa-btn-link" data-action="view-all">View All</button>
                </div>
                <div class="vsa-sidebar-content">
                    ${this.renderQuickAlerts()}
                </div>
            </div>
        `;
    },

    renderQuickAlerts() {
        if (this.state.alerts.length === 0) {
            return '<div class="vsa-sidebar-empty">No high priority alerts</div>';
        }

        return this.state.alerts.slice(0, 10).map(alert => `
            <div class="vsa-sidebar-alert" data-alert-id="${alert.id}">
                <div class="vsa-sidebar-alert-header">
                    <span class="vsa-badge vsa-badge-danger">HIGH</span>
                    <span class="vsa-sidebar-alert-time">${new Date(alert.callDate).toLocaleTimeString()}</span>
                </div>
                <div class="vsa-sidebar-alert-type">${this.escapeHtml(alert.type)}</div>
                <div class="vsa-sidebar-alert-client">${this.escapeHtml(alert.clientName)}</div>
            </div>
        `).join('');
    },

    renderSidebarError(message) {
        if (!this.sidebarContainer) return;

        this.sidebarContainer.innerHTML = `
            <div class="vsa-sidebar-error">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${this.escapeHtml(message)}</p>
            </div>
        `;
    },

    // ==================== RENDERING: STATES ====================

    renderLoading() {
        return `
            <div class="vsa-loading">
                <div class="vsa-loading-spinner">
                    <i class="fas fa-spinner fa-spin"></i>
                </div>
                <p>Loading veterinary alerts...</p>
            </div>
        `;
    },

    renderError() {
        return `
            <div class="vsa-error">
                <div class="vsa-error-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h3>Error Loading Alerts</h3>
                <p>${this.escapeHtml(this.state.error || 'Unknown error')}</p>
                <button class="vsa-btn" data-action="refresh">
                    <i class="fas fa-sync-alt"></i> Try Again
                </button>
            </div>
        `;
    },

    // ==================== ACTIONS ====================

    viewAlertDetails(alertId) {
        const alert = this.state.alerts.find(a => a.id === alertId);
        if (!alert) return;

        this.log.info('Viewing alert details:', alertId);
        this.state.selectedAlert = alert;

        // Emit event for cross-component communication
        this.events.emit('alert-selected', { alert });

        // Could open a modal here
        // For now, log to console
        console.log('Alert Details:', alert);
    },

    viewFollowUpDetails(followUpId) {
        const followUp = this.state.followUps.find(f => f.id === followUpId);
        if (!followUp) return;

        this.log.info('Viewing follow-up details:', followUpId);
        this.state.selectedFollowUp = followUp;

        // Emit event
        this.events.emit('followup-selected', { followUp });

        // Log to console
        console.log('Follow-up Details:', followUp);
    },

    // ==================== UTILITIES ====================

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// ==================== V4 MODULE REGISTRY INTEGRATION ====================
// Register with ModuleLoaderV4's global registry (required for V4 framework)
if (typeof window !== 'undefined') {
    window.ModuleRegistry = window.ModuleRegistry || {};
    window.ModuleRegistry['vsa-veterinary-alerts'] = VSAVeterinaryAlerts;
    console.log('🔷 VSA Veterinary Alerts registered in ModuleRegistry');
}

// ES6 Export (V4 ModuleLoaderV4 uses dynamic import())
export default VSAVeterinaryAlerts;
