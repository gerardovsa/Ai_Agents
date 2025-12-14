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
        // Supabase connection - credentials loaded from environment
        supabaseUrl: null,  // Set from window.ENV or environment config
        supabaseKey: null,  // Set from window.ENV or environment config
        supabaseClient: null,

        // Expansion state tracking (prevents loss on re-render)
        expandedCards: new Set(),

        // Cache for performance
        groupedAlertsCache: null,
        lastGroupedHash: null,

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
            category: 'all',
            alertTypes: []          // Array of selected alert types to filter by
        },

        // UI State for multi-select
        alertTypeDropdownOpen: false,

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

            // 🔧 FIX: Framework bug - getContainer() sometimes returns button instead of content
            if (!this.container || this.container.tagName === 'BUTTON') {
                console.warn('⚠️ getContainer() returned wrong element, using fallback');
                this.container = document.getElementById('tab-vsa-veterinary-alerts') ||
                    document.getElementById('vsa-veterinary-alerts-main-container');
            }

            if (!this.container) {
                throw new Error('Dashboard container not found');
            }

            this.log.info('✅ Container found:', this.container.id);

            // 🔧 FIX: Ensure container has proper height for scrolling
            if (this.container.id === 'tab-vsa-veterinary-alerts' ||
                this.container.id === 'vsa-veterinary-alerts-main-container') {
                this.container.style.height = '100%';
                this.container.style.overflow = 'hidden'; // Parent hides overflow, child scrolls
            }

            // ❌ REMOVED: Do NOT override display property
            // The tab system (.tab-content / .tab-content.active) handles visibility
            // Overriding display breaks tab switching - multiple tabs show at once
            // The CSS already defines:
            //   .tab-content { display: none; }
            //   .tab-content.active { display: block; }
            // Let the framework handle tab visibility - module just renders content

            // Initialize V4 dashboard structure (wrapper + header + sub-tabs)
            this.initializeSubTabs();

            // Load Supabase credentials from environment
            this.loadSupabaseConfig();

            // Load saved filters from storage
            this.loadFiltersFromStorage();

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

    // ==================== CONFIGURATION ====================

    loadSupabaseConfig() {
        // Load from window.ENV or environment config
        // In production, these should be set in .env.master or environment variables
        this.state.supabaseUrl = window.ENV?.SUPABASE_VSA_URL || 'https://wuwmvtslltqhaycyukxk.supabase.co';
        this.state.supabaseKey = window.ENV?.SUPABASE_VSA_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1d212dHNsbHRxaGF5Y3l1a3hrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTIyNDMzNCwiZXhwIjoyMDY2ODAwMzM0fQ.tUJ473GHC139vvH0X6fIgaFtgmLTl-VaUCf9kY6xQj4';

        this.log.info('Supabase config loaded');
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

        // Clear state to prevent memory leaks
        this.state.alerts = [];
        this.state.followUps = [];
        this.state.expandedCards.clear();
        this.state.groupedAlertsCache = null;

        // Disconnect Supabase client
        if (this.state.supabaseClient) {
            this.state.supabaseClient = null;
        }

        // Framework automatically cleans up tracked event listeners (container-scoped only)
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
            // Load structured alerts from call_manager_alerts table
            // This table contains properly formatted alert data with tags, severity, priority
            // Schema: alert_1_code, alert_1_severity, alert_1_core_reason, etc. for each slot (1-3)
            const { data, error } = await this.state.supabaseClient
                .from('call_manager_alerts')
                .select('*')
                .neq('manager_alerts_tags', 'NONE')  // Exclude non-alerts
                .order('created_at', { ascending: false })
                .limit(500);

            if (error) throw error;

            this.state.alerts = [];

            // Process each alert record (each call can have up to 3 alert slots)
            for (const alertData of (data || [])) {
                // Skip if no tags
                if (!alertData.manager_alerts_tags || alertData.manager_alerts_tags === 'NONE') {
                    continue;
                }

                // Get corresponding call data for client/staff info
                const call = this.state.veterinaryCalls.find(c => c.call_id === alertData.call_id);

                // Debug logging for first alert to check field names
                if (this.state.alerts.length === 0 && call) {
                    this.log.info('Sample call data fields:', {
                        call_id: call.call_id,
                        staffname_field: call.key_staffname,
                        firstname_field: call.key_otherspeaker_firstname,
                        lastname_field: call.key_otherspeaker_lastname,
                        all_keys: Object.keys(call).filter(k => k.includes('staff') || k.includes('speaker') || k.includes('name'))
                    });
                }

                // Process each slot (1-3) if it has an alert
                for (let slot = 1; slot <= 3; slot++) {
                    const alertCode = alertData[`alert_${slot}_code`];

                    // Skip empty slots
                    if (!alertCode || alertCode === 'NONE' || alertCode.trim() === '') {
                        continue;
                    }

                    // Extract slot-specific fields
                    const severity = alertData[`alert_${slot}_severity`] || 'LOW';
                    const priority = alertData[`alert_${slot}_priority`] || 3;
                    const coreReason = alertData[`alert_${slot}_core_reason`] || 'No description available';
                    const triggersMet = alertData[`alert_${slot}_triggers_met`];
                    const callSummary = alertData[`alert_${slot}_call_summary`];
                    const evidence = alertData[`alert_${slot}_evidence`];
                    const alterOutcome = alertData[`alert_${slot}_alteroutcome`];
                    const riskIfIgnored = alertData[`alert_${slot}_risk_if_ignored`];
                    const managerActionBrief = alertData[`alert_${slot}_manager_action_brief`];
                    const managerActionSteps = alertData[`alert_${slot}_manager_action_steps`];
                    const communicationGuide = alertData[`alert_${slot}_communication_guide_staff`];
                    const coachingFocus = alertData[`alert_${slot}_coaching_focus`];
                    const followUpWindow = alertData[`alert_${slot}_follow_up_window`];
                    const keyMetrics = alertData[`alert_${slot}_key_metrics`];

                    // Extract time from key_time field with fallback to created_at
                    let callTime = 'Time N/A';
                    if (call && call.key_time) {
                        // key_time format: "17:21:00" -> extract "17:21"
                        callTime = call.key_time.substring(0, 5);
                    } else if (alertData.created_at) {
                        // Fallback: extract time from created_at timestamp
                        try {
                            const timestamp = new Date(alertData.created_at);
                            callTime = timestamp.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
                        } catch (e) {
                            this.log.warn('Could not parse time from created_at:', alertData.created_at);
                        }
                    }

                    this.state.alerts.push({
                        id: `${alertData.call_id}_${slot}`,
                        callId: alertData.call_id,
                        alertSlot: slot,
                        callDate: call ? call.key_call_date : alertData.created_at,
                        callTime: callTime,
                        clientName: call ? `${call.key_otherspeaker_firstname || ''} ${call.key_otherspeaker_lastname || ''}`.trim() : 'UNKNOWN',
                        staffName: call ? call.key_staffname : 'UNKNOWN',
                        petName: call ? call.key_pet_petname : null,
                        petSpecies: call ? call.key_pet_species : null,
                        petAge: call ? call.key_pet_age : null,
                        phoneNumber: call ? call.key_phonenumber : null,
                        // Alert data from slot-specific columns
                        type: alertCode,  // REVENUE_LEAKAGE, MISSED_OPPORTUNITY, etc.
                        description: coreReason,
                        severity: severity.toLowerCase(),  // HIGH -> high
                        priority: priority,
                        status: 'pending',
                        created: alertData.created_at,
                        // Additional structured data for detail modal
                        triggersMet: triggersMet,
                        callSummary: callSummary,
                        evidence: evidence,
                        alterOutcome: alterOutcome,
                        riskIfIgnored: riskIfIgnored,
                        managerActionBrief: managerActionBrief,
                        managerActionSteps: managerActionSteps,
                        communicationGuide: communicationGuide,
                        coachingFocus: coachingFocus,
                        followUpWindow: followUpWindow,
                        keyMetrics: keyMetrics
                    });
                }
            }

            this.log.info(`Processed ${this.state.alerts.length} structured alerts from call_manager_alerts table`);

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

        // Alert type filter (multi-select)
        if (this.state.filters.alertTypes && this.state.filters.alertTypes.length > 0) {
            filtered = filtered.filter(a => this.state.filters.alertTypes.includes(a.type));
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

    getUniqueAlertTypes() {
        const types = new Set();
        this.state.alerts.forEach(alert => types.add(alert.type));
        return Array.from(types).sort();
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
        // Refresh every 5 minutes (300 seconds) to avoid disrupting user
        this.state.refreshInterval = setInterval(() => {
            this.log.info('Auto-refreshing alerts...');
            this.refreshData();
        }, 300000); // 5 minutes instead of 60 seconds
    },

    async refreshData() {
        try {
            // Save expanded state before refresh
            const expandedCallIds = [];
            const expandedTranscripts = [];

            document.querySelectorAll('.vsa-expander-content[aria-hidden="false"]').forEach(el => {
                const callId = el.getAttribute('data-call-id');
                if (callId) expandedCallIds.push(callId);
            });

            document.querySelectorAll('.vsa-transcript-content[aria-hidden="false"]').forEach(el => {
                const id = el.id;
                if (id) expandedTranscripts.push(id);
            });

            await this.loadAllData();
            this.renderDashboard();

            // Restore expanded state after a short delay for DOM rendering
            setTimeout(() => {
                expandedCallIds.forEach(callId => {
                    const expander = document.querySelector(`[data-call-id="${callId}"].vsa-expander-content`);
                    const toggle = document.querySelector(`[data-expander][aria-controls="${expander?.id}"]`);
                    if (expander && toggle) {
                        expander.style.display = 'block';
                        expander.setAttribute('aria-hidden', 'false');
                        toggle.setAttribute('aria-expanded', 'true');
                        toggle.querySelector('i').classList.replace('fa-chevron-down', 'fa-chevron-up');
                    }
                });

                expandedTranscripts.forEach(transcriptId => {
                    const transcript = document.getElementById(transcriptId);
                    const toggle = document.querySelector(`[aria-controls="${transcriptId}"]`);
                    if (transcript && toggle) {
                        transcript.style.display = 'block';
                        transcript.setAttribute('aria-hidden', 'false');
                        toggle.setAttribute('aria-expanded', 'true');
                        toggle.querySelector('.vsa-toggle-icon')?.classList.replace('fa-chevron-down', 'fa-chevron-up');
                    }
                });
            }, 100);
        } catch (error) {
            this.log.error('Failed to refresh data:', error);
        }
    },

    // ==================== EVENT LISTENERS ====================

    setupEventListeners() {
        // 🔧 FIX: Prevent duplicate listener registration
        if (this._listenersSetup) {
            console.warn('⚠️ Event listeners already setup, skipping duplicate registration');
            return;
        }
        this._listenersSetup = true;
        console.log('✅ Setting up event listeners (first time only)');

        // View toggle
        this.dom.on(this.container, 'click', '[data-view]', (e) => {
            this.state.view = e.currentTarget.dataset.view;
            this.saveFiltersToStorage();
            this.updateFilteredAlertsList();
        });

        // Severity filter
        this.dom.on(this.container, 'change', '[data-filter="severity"]', (e) => {
            this.state.filters.severity = e.target.value;
            this.saveFiltersToStorage();
            this.updateFilteredAlertsList();
        });

        // Expander toggle (Phase 1: Tiered hierarchy)
        this.dom.on(this.container, 'click', '.vsa-expander-toggle', (e) => {
            console.log('🔵 Expander toggle clicked!', e.currentTarget);
            console.log('🎯 Event target:', e.target);
            console.log('🎯 Event currentTarget:', e.currentTarget);
            console.log('🎯 Are they same?', e.target === e.currentTarget);

            // 🔧 FIX: Prevent double-firing by checking if event is already being processed
            const button = e.currentTarget;
            const expanderId = button.getAttribute('data-expander');

            // Debounce: Ignore rapid clicks on same expander (within 300ms)
            const now = Date.now();
            const lastClickKey = `expander-click-${expanderId}`;
            const lastClickTime = this[lastClickKey] || 0;

            if (now - lastClickTime < 300) {
                console.warn('⚠️ Rapid click detected, ignoring duplicate');
                return;
            }
            this[lastClickKey] = now;

            e.preventDefault();
            e.stopPropagation();

            console.log('🔍 Expander ID:', expanderId);

            if (!expanderId) {
                console.error('❌ No expander ID found on button', button);
                this.log.error('No expander ID found on button');
                return;
            }

            const content = document.getElementById(expanderId);
            console.log('🔍 Content element:', content);

            if (!content) {
                console.error(`❌ Expander content not found: ${expanderId}`);
                this.log.error(`Expander content not found: ${expanderId}`);
                return;
            }

            const isExpanded = button.getAttribute('aria-expanded') === 'true';
            const newExpandedState = !isExpanded;

            console.log(`📊 Toggle state: ${isExpanded} → ${newExpandedState}`);

            // Toggle ARIA states
            button.setAttribute('aria-expanded', newExpandedState.toString());
            content.setAttribute('aria-hidden', (!newExpandedState).toString());

            // Toggle display with transition
            if (newExpandedState) {
                content.style.display = 'block';
                // Force reflow for animation
                content.offsetHeight;
                console.log('✅ Expanded:', expanderId);

                // Load shared context for TIER 3 call containers (if not already loaded)
                if (content.hasAttribute('data-shared-context-needed')) {
                    const callId = content.getAttribute('data-call-id');
                    const placeholder = content.querySelector('.vsa-shared-context-placeholder');

                    if (callId && placeholder) {
                        this.loadSharedContext(callId, placeholder);
                        content.removeAttribute('data-shared-context-needed'); // Only load once
                    }
                }

                // Load transcript for transcript sections (if not already loaded)
                if (content.hasAttribute('data-transcript-needed')) {
                    const callId = button.getAttribute('data-call-id') ||
                        content.closest('[data-call-id]')?.getAttribute('data-call-id');

                    if (callId && content.classList.contains('vsa-transcript-content')) {
                        this.loadTranscript(callId, content);
                        content.removeAttribute('data-transcript-needed'); // Only load once
                    }
                }
            } else {
                // Delay hiding to allow animation
                setTimeout(() => {
                    content.style.display = 'none';
                }, 300); // Match CSS transition duration
                console.log('✅ Collapsed:', expanderId);
            }

            // Log for debugging
            this.log.info(`Expander ${expanderId} ${newExpandedState ? 'expanded' : 'collapsed'}`);
        });

        // Keyboard navigation for expanders (Phase 3: Professional touch)
        this.dom.on(this.container, 'keydown', '.vsa-expander-toggle', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                e.currentTarget.click();
            }
        });

        // Search input with debounce (Phase 3: Search functionality)
        let searchTimeout;
        this.dom.on(this.container, 'input', '[data-search]', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.state.filters.search = e.target.value;
                this.saveFiltersToStorage();
                this.updateFilteredAlertsList();
                this.log.info(`Search filter applied: "${e.target.value}"`);
            }, 300); // 300ms debounce
        });

        // Alert type multi-select dropdown toggle
        this.dom.on(this.container, 'click', '[data-action="toggle-alert-types"]', (e) => {
            e.stopPropagation();
            this.state.alertTypeDropdownOpen = !this.state.alertTypeDropdownOpen;
            this.updateDropdownVisibility();
        });

        // Close dropdown when clicking in filter area (NOT document level)
        this.dom.on(this.container, 'click', (e) => {
            // Ignore clicks on expander buttons
            if (e.target.closest('.vsa-expander-toggle')) {
                return;
            }

            // Only close if clicking in filter area, not in alerts list
            if (this.state.alertTypeDropdownOpen &&
                e.target.closest('.vsa-filters') &&
                !e.target.closest('.vsa-multiselect-wrapper')) {
                this.state.alertTypeDropdownOpen = false;
                this.updateDropdownVisibility();
            }
        });

        // Alert type checkbox change
        this.dom.on(this.container, 'change', '[data-alert-type]', (e) => {
            const type = e.target.value;
            if (e.target.checked) {
                if (!this.state.filters.alertTypes.includes(type)) {
                    this.state.filters.alertTypes.push(type);
                }
            } else {
                const index = this.state.filters.alertTypes.indexOf(type);
                if (index > -1) {
                    this.state.filters.alertTypes.splice(index, 1);
                }
            }
            this.saveFiltersToStorage();
            this.updateFilteredAlertsList();
        });

        // Clear all alert types
        this.dom.on(this.container, 'click', '[data-action="clear-alert-types"]', (e) => {
            e.stopPropagation();
            this.state.filters.alertTypes = [];
            this.saveFiltersToStorage();
            this.updateFilteredAlertsList();
        });

        // Action buttons
        this.dom.on(this.container, 'click', '[data-action="view-full"]', (e) => {
            e.stopPropagation();
            const alertId = e.currentTarget.dataset.alertId;
            this.viewAlertDetails(alertId);
        });

        this.dom.on(this.container, 'click', '[data-action="email"]', (e) => {
            e.stopPropagation();
            const alertId = e.currentTarget.dataset.alertId;
            const alert = this.state.alerts.find(a => a.id === alertId);
            if (alert) {
                this.log.info('Email action triggered for alert:', alertId);
                alert('Email notification feature coming soon!');
            }
        });

        // Priority filter
        this.dom.on(this.container, 'change', '[data-filter="priority"]', (e) => {
            this.state.filters.priority = e.target.value;
            this.saveFiltersToStorage();
            this.updateFilteredAlertsList();
        });

        // Date range filter
        this.dom.on(this.container, 'change', '[data-filter="dateRange"]', (e) => {
            this.state.filters.dateRange = e.target.value;
            this.saveFiltersToStorage();
            this.updateFilteredAlertsList();
        });

        // Search with enhanced logging (already handled above)
        // Duplicate removed - search functionality is in setupEventListeners

        // Refresh button
        this.dom.on(this.container, 'click', '[data-action="refresh"]', () => {
            this.refreshData();
        });

        // Alert card clicks now handled by expander toggles
        // Legacy click handler removed in favor of tier expansion system

        // Follow-up details
        this.dom.on(this.container, 'click', '[data-followup-id]', (e) => {
            const followUpId = e.currentTarget.dataset.followupId;
            this.viewFollowUpDetails(followUpId);
        });

        // Generate AI Coaching button
        this.dom.on(this.container, 'click', '.vsa-generate-coaching-btn', (e) => {
            e.stopPropagation();
            const button = e.currentTarget;
            const callId = button.getAttribute('data-call-id');

            if (!callId) {
                this.log.error('No call ID found for coaching generation');
                alert('Error: No call ID found');
                return;
            }

            this.generateCoaching(callId, button);
        });

        // View existing coaching (if button is added later)
        this.dom.on(this.container, 'click', '.vsa-view-coaching-btn', (e) => {
            e.stopPropagation();
            const button = e.currentTarget;
            const callId = button.getAttribute('data-call-id');

            if (!callId) {
                this.log.error('No call ID found for coaching view');
                return;
            }

            this.viewCoaching(callId);
        });

        // Delete coaching button
        this.dom.on(this.container, 'click', '.vsa-delete-coaching-btn', (e) => {
            e.stopPropagation();
            const button = e.currentTarget;
            const callId = button.getAttribute('data-call-id');

            if (!callId) {
                this.log.error('No call ID found for coaching deletion');
                return;
            }

            if (confirm('Are you sure you want to delete this coaching document?')) {
                this.deleteCoaching(callId);
            }
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
                        
                        <div class="vsa-multiselect-wrapper">
                            <button class="vsa-multiselect-toggle" data-action="toggle-alert-types">
                                <i class="fas fa-filter"></i>
                                Alert Types
                                ${this.state.filters.alertTypes.length > 0 ? `<span class="vsa-filter-badge">${this.state.filters.alertTypes.length}</span>` : ''}
                                <i class="fas fa-chevron-down"></i>
                            </button>
                            <div class="vsa-multiselect-dropdown ${this.state.alertTypeDropdownOpen ? 'open' : ''}">
                                <div class="vsa-multiselect-header">
                                    <span>Select Alert Types</span>
                                    <button class="vsa-multiselect-clear" data-action="clear-alert-types">
                                        Clear All
                                    </button>
                                </div>
                                <div class="vsa-multiselect-options">
                                    ${this.getUniqueAlertTypes().map(type => `
                                        <label class="vsa-multiselect-option">
                                            <input 
                                                type="checkbox" 
                                                value="${this.escapeHtml(type)}"
                                                ${this.state.filters.alertTypes.includes(type) ? 'checked' : ''}
                                                data-alert-type
                                            />
                                            <span>${this.escapeHtml(type)}</span>
                                        </label>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
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

        // Group alerts by date first (TIER 2)
        const groupedByDate = this.groupAlertsByDate(alerts);

        return `
            <div class="vsa-alerts-list">
                <h2 class="vsa-list-title">
                    <i class="fas fa-bell"></i> 
                    Alerts (${alerts.length})
                </h2>
                ${groupedByDate.map(dateGroup => `
                    <div class="vsa-date-group">
                        <div class="vsa-date-separator">
                            <span class="vsa-date-label">${dateGroup.dateLabel}</span>
                            <span class="vsa-date-count">${dateGroup.alerts.length} alerts</span>
                        </div>
                        ${this.renderCallGroups(dateGroup.alerts)}
                    </div>
                `).join('')}
            </div>
        `;
    },

    // ==================== TIER 3: CALL-LEVEL GROUPING ====================
    renderCallGroups(alerts) {
        // Group alerts by call_id (TIER 3)
        const callGroups = {};

        alerts.forEach(alert => {
            if (!callGroups[alert.callId]) {
                callGroups[alert.callId] = [];
            }
            callGroups[alert.callId].push(alert);
        });

        // Render each call container with its alerts
        return Object.entries(callGroups)
            .map(([callId, callAlerts]) => this.renderTier3CallContainer(callId, callAlerts))
            .join('');
    },

    renderTier3CallContainer(callId, callAlerts) {
        // Sort alerts by slot number within the call
        const sortedAlerts = callAlerts.sort((a, b) => a.alertSlot - b.alertSlot);

        // Get shared context from first alert (all alerts in same call share this data)
        const firstAlert = sortedAlerts[0];
        const callDate = firstAlert.callDate ? new Date(firstAlert.callDate) : new Date();
        const dateStr = callDate.toLocaleDateString('en-US', { month: 'numeric', day: 'numeric', year: 'numeric' });

        // Use the extracted callTime directly (format: "09:37" or "17:21")
        const timeStr = firstAlert.callTime || 'UNKNOWN';

        // Determine highest severity for container styling
        const highestSeverity = this.getHighestSeverity(sortedAlerts);
        const severityColors = {
            HIGH: { border: '#d32f2f', gradient: '#d32f2f', gradientEnd: 'rgba(13,23,32,0.95)' },
            MED: { border: '#f57c00', gradient: '#f57c00', gradientEnd: 'rgba(13,23,32,0.95)' },
            LOW: { border: '#ffeb3b', gradient: '#ffeb3b', gradientEnd: 'rgba(13,23,32,0.95)' }
        };
        const colors = severityColors[highestSeverity.toUpperCase()] || severityColors.MED;

        // Generate unique ID for call container
        const containerId = `call-container-${callId}`;
        const expanderId = `call-expander-${callId}`;

        return `
            <div class="vsa-call-container vsa-tier-3" 
                 data-call-id="${callId}"
                 role="region"
                 aria-labelledby="${containerId}-title">
                
                <!-- TIER 3 Header: Call-level information -->
                <div class="vsa-tier3-header" 
                     style="background: linear-gradient(135deg, ${colors.gradient} 0%, ${colors.gradientEnd} 78%);
                            border-left: 6px solid ${colors.border};"
                     role="heading"
                     aria-level="3">
                    <div class="vsa-tier3-title" id="${containerId}-title">
                        <span class="vsa-title-text" style="text-shadow: 0 2px 4px rgba(0,0,0,0.6), 0 0 3px ${colors.border};">
                            <i class="fas fa-user-md"></i> ${this.escapeHtml(firstAlert.staffName && firstAlert.staffName !== 'UNKNOWN' ? firstAlert.staffName : 'Staff Member')} - ${timeStr} - ${dateStr}
                        </span>
                        <span class="vsa-alert-count-badge">${sortedAlerts.length} Alert${sortedAlerts.length > 1 ? 's' : ''}</span>
                    </div>
                    <button class="vsa-expander-toggle" 
                            data-expander="${expanderId}"
                            aria-expanded="false"
                            aria-controls="${expanderId}"
                            aria-label="Expand call details">
                        <i class="fas fa-chevron-down"></i>
                    </button>
                </div>

                <!-- TIER 3 Description: Client, Pet, Phone, Call ID -->
                <div class="vsa-tier3-description">
                    <strong>Client:</strong> ${this.escapeHtml(firstAlert.clientName && firstAlert.clientName !== 'UNKNOWN' ? firstAlert.clientName : 'Client Name N/A')} • 
                    ${firstAlert.petName ? `<strong>Pet:</strong> ${this.escapeHtml(firstAlert.petName)} • ` : ''}
                    ${firstAlert.phoneNumber ? `<strong>Ph:</strong> ${this.escapeHtml(firstAlert.phoneNumber)} • ` : ''}
                    <strong>Call ID:</strong> <code>${this.escapeHtml(callId)}</code>
                </div>

                <!-- TIER 3 Expandable Content -->
                <div class="vsa-expander-content" 
                     id="${expanderId}" 
                     aria-hidden="true"
                     style="display: none;"
                     data-call-id="${callId}"
                     data-shared-context-needed="true">
                    
                    <!-- Call ID Context (explicitly shown) -->
                    <div class="vsa-call-id-context">
                        <h4><i class="fas fa-id-card"></i> Call ID: <strong>${this.escapeHtml(callId)}</strong></h4>
                    </div>

                    <!-- Shared Context Section (loaded dynamically when expanded) -->
                    <div class="vsa-shared-context-placeholder">
                        <div class="vsa-loading-spinner">
                            <i class="fas fa-spinner fa-spin"></i> Loading call context...
                        </div>
                    </div>

                    <!-- Transcript Section -->
                    <div class="vsa-transcript-section">
                        <button class="vsa-expander-toggle vsa-transcript-toggle" 
                                data-expander="transcript-${callId}"
                                data-call-id="${callId}"
                                aria-expanded="false"
                                aria-controls="transcript-${callId}"
                                aria-label="View call transcript">
                            <i class="fas fa-file-alt"></i> 📄 Call Transcript
                            <i class="fas fa-chevron-down vsa-toggle-icon"></i>
                        </button>
                        <div class="vsa-expander-content vsa-transcript-content" 
                             id="transcript-${callId}" 
                             aria-hidden="true"
                             style="display: none;"
                             data-transcript-needed="true">
                            <div class="vsa-transcript-loading">
                                <i class="fas fa-spinner fa-spin"></i> Loading transcript...
                            </div>
                        </div>
                    </div>

                    <hr class="vsa-section-divider">

                    <!-- TIER 4: Individual Alerts (nested within call container) -->
                    <div class="vsa-tier4-alerts-container">
                        <h4 class="vsa-tier4-header-label">
                            <i class="fas fa-exclamation-triangle"></i> Individual Alerts
                        </h4>
                        ${sortedAlerts.map((alert, index) => this.renderTier4Alert(alert, index + 1)).join('')}
                    </div>

                    <!-- Manager Follow-up Section (placeholder - Phase 2) -->
                    <div class="vsa-manager-followup-placeholder">
                        <h4><i class="fas fa-user-edit"></i> Manager Follow-up</h4>
                        <p class="vsa-coming-soon">Status tracking, notes, and actions coming in Phase 2...</p>
                    </div>

                    <!-- AI Coaching Section -->
                    <div class="vsa-ai-coaching-section">
                        <div class="vsa-coaching-header">
                            <h4><i class="fas fa-brain"></i> AI Coaching Support</h4>
                            <div class="vsa-coaching-actions">
                                <button class="vsa-btn vsa-btn-primary vsa-generate-coaching-btn" 
                                        data-call-id="${callId}"
                                        aria-label="Generate AI coaching">
                                    <i class="fas fa-magic"></i> Generate AI Coaching
                                </button>
                            </div>
                        </div>
                        <div class="vsa-coaching-content" id="coaching-content-${callId}">
                            <div class="vsa-coaching-placeholder">
                                <i class="fas fa-brain vsa-coaching-icon"></i>
                                <p>Click "Generate AI Coaching" to create a personalized coaching document based on this call's transcript and analysis.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    getHighestSeverity(alerts) {
        // HIGH > MED > LOW
        const severityPriority = { high: 3, medium: 2, med: 2, low: 1 };
        let highest = 'low';
        let highestValue = 0;

        alerts.forEach(alert => {
            const severity = alert.severity.toLowerCase();
            const value = severityPriority[severity] || 0;
            if (value > highestValue) {
                highestValue = value;
                highest = severity === 'medium' || severity === 'med' ? 'med' : severity;
            }
        });

        return highest.toUpperCase();
    },

    async loadSharedContext(callId, placeholderElement) {
        // Fetch shared context from call_manager_alerts table
        try {
            const { data, error } = await this.state.supabaseClient
                .from('call_manager_alerts')
                .select('manager_alerts_tags, manager_summary, manager_alerts_reasoning_analysis')
                .eq('call_id', callId)
                .single();

            if (error) throw error;

            const tags = data?.manager_alerts_tags || 'N/A';
            const summary = data?.manager_summary || 'No summary available';
            const reasoning = data?.manager_alerts_reasoning_analysis || 'No reasoning available';

            // Update placeholder with actual content
            placeholderElement.innerHTML = `
                <div class="vsa-shared-context">
                    <h4 class="vsa-section-title">
                        <i class="fas fa-info-circle"></i> Call Context (Shared)
                    </h4>
                    <div class="vsa-shared-context-grid">
                        <div class="vsa-context-item">
                            <label><i class="fas fa-tags"></i> Tags:</label>
                            <span class="vsa-tags">${this.escapeHtml(tags)}</span>
                        </div>
                        <div class="vsa-context-item vsa-context-full-width">
                            <label><i class="fas fa-file-alt"></i> Summary:</label>
                            <p>${this.escapeHtml(summary)}</p>
                        </div>
                        <div class="vsa-context-item vsa-context-full-width">
                            <label><i class="fas fa-lightbulb"></i> Reasoning:</label>
                            <p>${this.escapeHtml(reasoning)}</p>
                        </div>
                    </div>
                    <hr class="vsa-section-divider">
                </div>
            `;
        } catch (error) {
            this.log.error('Failed to fetch shared context:', error);
            placeholderElement.innerHTML = `
                <div class="vsa-shared-context">
                    <p class="vsa-error-text">Unable to load shared context</p>
                    <hr class="vsa-section-divider">
                </div>
            `;
        }
    },

    async loadTranscript(callId, transcriptElement) {
        // Fetch transcript from call_full_transcript_and_full_analysis table
        try {
            const { data, error } = await this.state.supabaseClient
                .from('call_full_transcript_and_full_analysis')
                .select('full_transcript_text')
                .eq('call_id', callId)
                .single();

            if (error) throw error;

            const transcript = data?.full_transcript_text || '';

            if (transcript && transcript.trim()) {
                // Update with actual transcript
                transcriptElement.innerHTML = `
                    <div class="vsa-transcript-container">
                        <textarea class="vsa-transcript-textarea" 
                                  readonly 
                                  rows="20">${this.escapeHtml(transcript)}</textarea>
                    </div>
                `;
            } else {
                transcriptElement.innerHTML = `
                    <div class="vsa-transcript-empty">
                        <p><i class="fas fa-info-circle"></i> No transcript text available for this call.</p>
                    </div>
                `;
            }
        } catch (error) {
            this.log.error('Failed to fetch transcript:', error);
            transcriptElement.innerHTML = `
                <div class="vsa-transcript-error">
                    <p class="vsa-error-text"><i class="fas fa-exclamation-triangle"></i> Unable to load transcript: ${error.message}</p>
                </div>
            `;
        }
    },

    async generateCoaching(callId, button) {
        const contentElement = document.getElementById(`coaching-content-${callId}`);

        if (!contentElement) {
            this.log.error('Coaching content element not found');
            return;
        }

        // Disable button and show loading state
        const originalButtonHTML = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';

        // Show loading in content area
        contentElement.innerHTML = `
            <div class="vsa-coaching-loading">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Generating AI coaching document...</p>
                <p class="vsa-coaching-loading-note">This may take 30-60 seconds</p>
            </div>
        `;

        try {
            // Call API to generate coaching
            const response = await fetch('/api/vsa-alerts/generate-coaching', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ call_id: callId })
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(result.error || 'Failed to generate coaching');
            }

            // Display coaching document
            this.displayCoaching(callId, result.coaching, result.generated_date);

            // Update button to show view/regenerate options
            button.innerHTML = '<i class="fas fa-sync"></i> Regenerate';
            button.classList.remove('vsa-btn-primary');
            button.classList.add('vsa-btn-secondary');

            this.log.success(`Coaching generated for call ${callId}`);

        } catch (error) {
            this.log.error('Failed to generate coaching:', error);

            // Show error message
            contentElement.innerHTML = `
                <div class="vsa-coaching-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p class="vsa-error-text">Failed to generate coaching: ${error.message}</p>
                    <button class="vsa-btn vsa-btn-secondary" onclick="this.closest('.vsa-ai-coaching-section').querySelector('.vsa-generate-coaching-btn').click()">
                        <i class="fas fa-redo"></i> Try Again
                    </button>
                </div>
            `;

            // Reset button
            button.disabled = false;
            button.innerHTML = originalButtonHTML;
        }
    },

    displayCoaching(callId, coachingContent, generatedDate) {
        const contentElement = document.getElementById(`coaching-content-${callId}`);

        if (!contentElement) {
            this.log.error('Coaching content element not found');
            return;
        }

        // Format date
        let dateStr = 'Just now';
        if (generatedDate) {
            try {
                const date = new Date(generatedDate);
                dateStr = date.toLocaleString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                    hour: 'numeric',
                    minute: '2-digit',
                    hour12: true
                });
            } catch (e) {
                // Use raw date string if parsing fails
                dateStr = generatedDate;
            }
        }

        // Convert markdown to HTML (basic formatting)
        const htmlContent = this.markdownToHtml(coachingContent);

        // Display coaching document
        contentElement.innerHTML = `
            <div class="vsa-coaching-document">
                <div class="vsa-coaching-meta">
                    <span class="vsa-coaching-date">
                        <i class="fas fa-clock"></i> Generated: ${this.escapeHtml(dateStr)}
                    </span>
                    <button class="vsa-btn vsa-btn-sm vsa-btn-danger vsa-delete-coaching-btn" 
                            data-call-id="${callId}"
                            title="Delete coaching document">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
                <div class="vsa-coaching-body">
                    ${htmlContent}
                </div>
            </div>
        `;
    },

    async viewCoaching(callId) {
        try {
            const response = await fetch(`/api/vsa-alerts/coaching/${callId}`);
            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(result.error || 'Failed to load coaching');
            }

            this.displayCoaching(callId, result.coaching, result.generated_date);

        } catch (error) {
            this.log.error('Failed to load coaching:', error);
            alert(`Failed to load coaching: ${error.message}`);
        }
    },

    async deleteCoaching(callId) {
        const contentElement = document.getElementById(`coaching-content-${callId}`);
        const button = document.querySelector(`.vsa-generate-coaching-btn[data-call-id="${callId}"]`);

        try {
            const response = await fetch(`/api/vsa-alerts/coaching/${callId}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(result.error || 'Failed to delete coaching');
            }

            // Reset to placeholder state
            if (contentElement) {
                contentElement.innerHTML = `
                    <div class="vsa-coaching-placeholder">
                        <i class="fas fa-brain vsa-coaching-icon"></i>
                        <p>Click "Generate AI Coaching" to create a personalized coaching document based on this call's transcript and analysis.</p>
                    </div>
                `;
            }

            // Reset button
            if (button) {
                button.innerHTML = '<i class="fas fa-magic"></i> Generate AI Coaching';
                button.classList.add('vsa-btn-primary');
                button.classList.remove('vsa-btn-secondary');
                button.disabled = false;
            }

            this.log.success(`Coaching deleted for call ${callId}`);

        } catch (error) {
            this.log.error('Failed to delete coaching:', error);
            alert(`Failed to delete coaching: ${error.message}`);
        }
    },

    markdownToHtml(markdown) {
        // Basic markdown to HTML conversion
        let html = this.escapeHtml(markdown);

        // Headers
        html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
        html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
        html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>');

        // Bold
        html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

        // Italic
        html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

        // Code
        html = html.replace(/`(.+?)`/g, '<code>$1</code>');

        // Lists
        html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
        html = html.replace(/^• (.+)$/gm, '<li>$1</li>');
        html = html.replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>');

        // Wrap consecutive <li> in <ul>
        html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');

        // Horizontal rules
        html = html.replace(/^---$/gm, '<hr>');

        // Paragraphs (lines separated by double newlines)
        html = html.replace(/\n\n/g, '</p><p>');
        html = '<p>' + html + '</p>';

        // Clean up empty paragraphs
        html = html.replace(/<p><\/p>/g, '');
        html = html.replace(/<p>\s*<\/p>/g, '');

        return html;
    },

    // ==================== TIER 4: INDIVIDUAL ALERTS ====================
    renderTier4Alert(alert, alertNumber) {
        // Get severity styling
        const severityUpper = alert.severity.toUpperCase();
        const severityBadge = {
            HIGH: '<span class="vsa-badge vsa-badge-danger" role="status">HIGH</span>',
            MED: '<span class="vsa-badge vsa-badge-warning" role="status">MED</span>',
            LOW: '<span class="vsa-badge vsa-badge-success" role="status">LOW</span>'
        }[severityUpper] || '<span class="vsa-badge vsa-badge-warning">MED</span>';

        const alertId = `alert-tier4-${alert.id}`;
        const expanderId = `alert-tier4-expander-${alert.id}`;

        return `
            <div class="vsa-tier4-alert vsa-severity-${alert.severity}" 
                 data-alert-id="${alert.id}"
                 role="article"
                 aria-labelledby="${alertId}-title">
                
                <!-- TIER 4 Header -->
                <div class="vsa-tier4-header" 
                     role="heading"
                     aria-level="4">
                    <div class="vsa-tier4-title" id="${alertId}-title">
                        <span class="vsa-alert-number">Alert ${alertNumber}</span>
                        <span class="vsa-alert-type">${this.escapeHtml(alert.type)}</span>
                        ${severityBadge}
                    </div>
                    <button class="vsa-expander-toggle" 
                            data-expander="${expanderId}"
                            aria-expanded="false"
                            aria-controls="${expanderId}"
                            aria-label="Expand alert ${alertNumber} details">
                        <i class="fas fa-chevron-down"></i>
                    </button>
                </div>

                <!-- TIER 4 Expandable Content -->
                <div class="vsa-expander-content" 
                     id="${expanderId}" 
                     aria-hidden="true"
                     style="display: none;">
                    
                    ${this.renderAlertSections(alert)}
                </div>
            </div>
        `;
    },

    renderAlertSections(alert) {
        return `
            <!-- Alert Overview (4-column grid) -->
            <div class="vsa-detail-section">
                <h5 class="vsa-subsection-title">
                    <i class="fas fa-th"></i> Alert Overview
                </h5>
                <div class="vsa-overview-grid">
                    <div class="vsa-overview-item">
                        <label>Priority</label>
                        <span class="vsa-priority-${alert.priority}">${alert.priority || 'N/A'}</span>
                    </div>
                    <div class="vsa-overview-item">
                        <label>Severity</label>
                        <span>${alert.severity.toUpperCase()}</span>
                    </div>
                    <div class="vsa-overview-item">
                        <label>Follow-up Window</label>
                        <span>${this.escapeHtml(alert.followUpWindow || 'N/A')}</span>
                    </div>
                    <div class="vsa-overview-item">
                        <label>Status</label>
                        <span class="vsa-status-${alert.status}">${alert.status}</span>
                    </div>
                </div>
            </div>

            <hr class="vsa-section-divider">

            <!-- Core Information -->
            <div class="vsa-detail-section">
                <h5 class="vsa-subsection-title">
                    <i class="fas fa-info-circle"></i> Core Information
                </h5>
                <div style="margin-bottom: 12px;"><strong style="color: #3b82f6; font-size: 0.9rem;">Core Reason:</strong> <span style="font-size: 0.9rem; line-height: 1.6;">${this.escapeHtml(alert.description)}</span></div>
                ${alert.triggersMet ? `<div style="margin-bottom: 12px;"><strong style="color: #3b82f6; font-size: 0.9rem;">Triggers Met:</strong> <span style="font-size: 0.9rem; line-height: 1.6;">${this.escapeHtml(alert.triggersMet)}</span></div>` : ''}
                ${alert.keyMetrics ? `<div style="margin-bottom: 12px;"><strong style="color: #3b82f6; font-size: 0.9rem;">Key Metrics:</strong> <span style="font-size: 0.9rem; line-height: 1.6;">${this.escapeHtml(alert.keyMetrics)}</span></div>` : ''}
                ${alert.callSummary ? `<div style="margin-bottom: 12px;"><strong style="color: #3b82f6; font-size: 0.9rem;">Call Summary:</strong> <span style="font-size: 0.9rem; line-height: 1.6;">${this.escapeHtml(alert.callSummary)}</span></div>` : ''}
            </div>

            <hr class="vsa-section-divider">

            <!-- Evidence -->
            ${alert.evidence ? `
                <div class="vsa-detail-section">
                    <h5 class="vsa-subsection-title">
                        <i class="fas fa-quote-right"></i> Evidence
                    </h5>
                    <div class="vsa-evidence">${this.formatEvidence(alert.evidence)}</div>
                </div>
                <hr class="vsa-section-divider">
            ` : ''}

            <!-- Risk If Ignored -->
            ${alert.riskIfIgnored ? `
                <div class="vsa-detail-section vsa-warning-section">
                    <h5 class="vsa-subsection-title">
                        <i class="fas fa-exclamation-circle"></i> Risk If Ignored
                    </h5>
                    ${this.formatTextContent(alert.riskIfIgnored)}
                </div>
                <hr class="vsa-section-divider">
            ` : ''}

            <!-- Manager Actions -->
            ${alert.managerActionBrief || alert.managerActionSteps ? `
                <div class="vsa-detail-section vsa-action-section">
                    <h5 class="vsa-subsection-title">
                        <i class="fas fa-tasks"></i> Manager Actions
                    </h5>
                    ${this.formatManagerActions(alert.managerActionBrief, alert.managerActionSteps)}
                </div>
                <hr class="vsa-section-divider">
            ` : ''}

            <!-- Communication Guide -->
            ${alert.communicationGuide ? `
                <div class="vsa-detail-section">
                    <h5 class="vsa-subsection-title">
                        <i class="fas fa-comments"></i> Communication Guide
                    </h5>
                    ${this.formatTextContent(alert.communicationGuide)}
                </div>
                <hr class="vsa-section-divider">
            ` : ''}

            <!-- Coaching Focus -->
            ${alert.coachingFocus ? `
                <div class="vsa-detail-section">
                    <h5 class="vsa-subsection-title">
                        <i class="fas fa-graduation-cap"></i> Coaching Focus
                    </h5>
                    ${this.formatTextContent(alert.coachingFocus)}
                </div>
            ` : ''}
        `;
    },

    groupAlertsByDate(alerts) {
        // Use cache if data hasn't changed
        const hash = alerts.map(a => a.id).join(',');
        if (this.state.lastGroupedHash === hash && this.state.groupedAlertsCache) {
            return this.state.groupedAlertsCache;
        }

        // Sort alerts by date descending (newest first)
        const sortedAlerts = [...alerts].sort((a, b) =>
            new Date(b.callDate) - new Date(a.callDate)
        );

        // Group by date
        const groups = {};
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);

        sortedAlerts.forEach(alert => {
            const alertDate = new Date(alert.callDate);
            alertDate.setHours(0, 0, 0, 0);

            let dateKey, dateLabel;

            if (alertDate.getTime() === today.getTime()) {
                dateKey = 'today';
                dateLabel = 'Today';
            } else if (alertDate.getTime() === yesterday.getTime()) {
                dateKey = 'yesterday';
                dateLabel = 'Yesterday';
            } else {
                dateKey = alertDate.toISOString().split('T')[0];
                dateLabel = alertDate.toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });
            }

            if (!groups[dateKey]) {
                groups[dateKey] = {
                    dateLabel,
                    date: alertDate,
                    alerts: []
                };
            }
            groups[dateKey].alerts.push(alert);
        });

        // Convert to array and sort by date
        const result = Object.values(groups).sort((a, b) => b.date - a.date);

        // Cache result
        this.state.lastGroupedHash = hash;
        this.state.groupedAlertsCache = result;

        return result;
    },

    // Old renderAlertCard method removed - replaced by TIER 3 call grouping + TIER 4 alert rendering
    // See renderTier3CallContainer() and renderTier4Alert() methods above

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

        // Show alert details modal
        this.showAlertDetailsModal(alert);
    },

    showAlertDetailsModal(alert) {
        // Create modal overlay
        const modal = document.createElement('div');
        modal.className = 'vsa-modal-overlay';
        modal.innerHTML = `
            <div class="vsa-modal-content">
                <div class="vsa-modal-header">
                    <h2>
                        <i class="fas fa-bell"></i>
                        Alert Details
                    </h2>
                    <button class="vsa-modal-close" onclick="this.closest('.vsa-modal-overlay').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="vsa-modal-body">
                    <!-- Alert Summary -->
                    <div class="vsa-detail-section">
                        <h3><i class="fas fa-exclamation-triangle"></i> Alert Summary</h3>
                        <div class="vsa-detail-grid">
                            <div class="vsa-detail-item">
                                <label>Type:</label>
                                <span class="vsa-badge vsa-badge-${alert.severity}">${this.escapeHtml(alert.type)}</span>
                            </div>
                            <div class="vsa-detail-item">
                                <label>Severity:</label>
                                <span class="vsa-badge vsa-badge-${alert.severity === 'high' ? 'danger' : alert.severity === 'medium' ? 'warning' : 'success'}">${alert.severity.toUpperCase()}</span>
                            </div>
                            <div class="vsa-detail-item">
                                <label>Status:</label>
                                <span>${alert.status}</span>
                            </div>
                            <div class="vsa-detail-item">
                                <label>Date:</label>
                                <span>${new Date(alert.callDate).toLocaleDateString()} ${new Date(alert.callDate).toLocaleTimeString()}</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Call Information -->
                    <div class="vsa-detail-section">
                        <h3><i class="fas fa-phone"></i> Call Information</h3>
                        <div class="vsa-detail-grid">
                            <div class="vsa-detail-item">
                                <label>Call ID:</label>
                                <span><code>${this.escapeHtml(alert.callId)}</code></span>
                            </div>
                            <div class="vsa-detail-item">
                                <label>Client Name:</label>
                                <span>${this.escapeHtml(alert.clientName)}</span>
                            </div>
                            <div class="vsa-detail-item">
                                <label>Staff Member:</label>
                                <span>${this.escapeHtml(alert.staffName)}</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Alert Description -->
                    <div class="vsa-detail-section">
                        <h3><i class="fas fa-file-alt"></i> Description</h3>
                        <div class="vsa-detail-description">
                            <p>${this.escapeHtml(alert.description)}</p>
                        </div>
                    </div>
                    
                    <!-- Action Items (if available) -->
                    ${alert.managerActionSteps ? `
                    <div class="vsa-detail-section">
                        <h3><i class="fas fa-tasks"></i> Recommended Actions</h3>
                        <div class="vsa-detail-description">
                            <p>${this.escapeHtml(alert.managerActionSteps)}</p>
                        </div>
                    </div>
                    ` : ''}
                </div>
                
                <div class="vsa-modal-footer">
                    <button class="vsa-btn vsa-btn-secondary" onclick="this.closest('.vsa-modal-overlay').remove()">
                        Close
                    </button>
                    <button class="vsa-btn" onclick="alert('Email notification feature coming soon!')">
                        <i class="fas fa-envelope"></i> Send Email Alert
                    </button>
                </div>
            </div>
        `;

        // Close on overlay click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });

        // Close on Escape key
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);

        // Add to DOM
        document.body.appendChild(modal);
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
    },

    /**
     * Format evidence text with proper structure:
     * - Timestamps (00:00:00-00:00:00) in bold
     * - Quoted text with special styling
     * - Preserve line breaks and structure
     */
    formatEvidence(evidence) {
        if (!evidence) return '';

        // Escape HTML first for safety
        let formatted = this.escapeHtml(evidence);

        // Format timestamps: 00:00:00-00:00:00 or 00:00:00
        formatted = formatted.replace(
            /(\d{2}:\d{2}:\d{2}(?:-\d{2}:\d{2}:\d{2})?)/g,
            '<strong style="color: #3b82f6; font-weight: 600;">$1</strong>'
        );

        // Format quoted text: "text"
        formatted = formatted.replace(
            /&quot;([^&]+)&quot;/g,
            '<span style="background: rgba(59, 130, 246, 0.1); padding: 3px 8px; border-left: 3px solid #3b82f6; display: inline-block; margin: 4px 0; font-size: 0.9rem;">&quot;$1&quot;</span>'
        );

        // Format speaker labels: [STAFF_Name] or [CLIENT_Name]
        formatted = formatted.replace(
            /\[(STAFF|CLIENT|SERVICEPROV)_([^\]]+)\]/g,
            '<span style="color: #10b981; font-weight: 600; font-size: 0.9rem;">[$1_$2]</span>'
        );

        // Preserve line breaks - convert double newlines to paragraphs
        formatted = formatted.replace(/\n\n+/g, '</p><p style="margin-top: 8px; font-size: 0.9rem; line-height: 1.6;">');
        formatted = formatted.replace(/\n/g, '<br>');

        // Wrap in scrollable container with max-height
        return `<div style="max-height: 300px; overflow-y: auto; padding: 12px; background: rgba(255, 255, 255, 0.02); border-radius: 6px; border: 1px solid rgba(255, 255, 255, 0.05);"><p style="line-height: 1.6; font-size: 0.9rem; margin: 0;">${formatted}</p></div>`;
    },

    /**
     * Format manager actions with proper structure and list formatting
     */
    formatManagerActions(brief, steps) {
        let html = '';

        if (brief) {
            html += `<div style="margin-bottom: 12px; padding: 10px; background: rgba(59, 130, 246, 0.08); border-left: 3px solid #3b82f6; border-radius: 4px;"><strong style="color: #3b82f6; font-size: 0.9rem;">Brief:</strong> <span style="font-size: 0.9rem; line-height: 1.6;">${this.escapeHtml(brief)}</span></div>`;
        }

        if (steps) {
            // Try to parse as numbered list
            const stepText = this.escapeHtml(steps);
            const lines = stepText.split('\n').filter(line => line.trim());

            if (lines.length > 1) {
                // Multi-line - format as ordered list
                html += '<div style="padding-left: 8px;"><strong style="color: #3b82f6; font-size: 0.9rem; display: block; margin-bottom: 8px;">Steps:</strong><ol style="margin: 0; padding-left: 24px; font-size: 0.9rem; line-height: 1.8;">';
                lines.forEach(line => {
                    const cleaned = line.replace(/^\d+\.\s*/, '').trim();
                    if (cleaned) {
                        html += `<li style="margin-bottom: 6px;">${cleaned}</li>`;
                    }
                });
                html += '</ol></div>';
            } else {
                // Single line
                html += `<div style="margin-top: 8px; padding: 10px; background: rgba(59, 130, 246, 0.08); border-left: 3px solid #3b82f6; border-radius: 4px;"><strong style="color: #3b82f6; font-size: 0.9rem;">Steps:</strong> <span style="font-size: 0.9rem; line-height: 1.6;">${stepText}</span></div>`;
            }
        }

        return html;
    },

    /**
     * Format text content with consistent styling and line breaks
     */
    formatTextContent(text) {
        if (!text) return '';

        let formatted = this.escapeHtml(text);

        // Convert line breaks
        formatted = formatted.replace(/\n\n+/g, '</p><p style="margin-top: 10px; font-size: 0.9rem; line-height: 1.6;">');
        formatted = formatted.replace(/\n/g, '<br>');

        return `<p style="font-size: 0.9rem; line-height: 1.6; margin: 0;">${formatted}</p>`;
    },

    // ==================== GRANULAR UPDATE METHODS ====================

    /**
     * Update dropdown visibility without full re-render
     */
    updateDropdownVisibility() {
        const dropdown = this.container.querySelector('.vsa-multiselect-dropdown');
        if (dropdown) {
            dropdown.style.display = this.state.alertTypeDropdownOpen ? 'block' : 'none';
        }
    },

    /**
     * Update only the alerts list without rebuilding filters
     */
    updateFilteredAlertsList() {
        console.log('🔄 updateFilteredAlertsList() called - this will destroy DOM!');
        console.trace('Call stack:');
        this.saveExpandedState();

        const container = this.getSubTabContainer(this.state.activeSubTab);
        if (!container) return;

        const contentWrapper = container.querySelector('.vsa-content-wrapper');
        if (!contentWrapper) {
            // First render, do full render
            this.renderDashboardContent();
            return;
        }

        // Update only the content area
        const contentArea = contentWrapper.querySelector('.vsa-split-view, .vsa-alerts-list, .vsa-followups-list');
        if (contentArea && contentArea.parentElement) {
            const newContent = this.renderContent();
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = newContent;
            contentArea.parentElement.replaceChild(tempDiv.firstElementChild, contentArea);
        } else {
            // Fallback to full render if structure changed
            this.renderDashboardContent();
        }

        this.restoreExpandedState();
    },

    /**
     * Save expansion state before re-render
     */
    saveExpandedState() {
        this.state.expandedCards.clear();
        const expandedButtons = this.container.querySelectorAll('.vsa-expander-toggle[aria-expanded="true"]');
        expandedButtons.forEach(btn => {
            const id = btn.getAttribute('data-expander');
            if (id) {
                this.state.expandedCards.add(id);
            }
        });
    },

    /**
     * Restore expansion state after re-render
     */
    restoreExpandedState() {
        this.state.expandedCards.forEach(id => {
            const button = this.container.querySelector(`[data-expander="${id}"]`);
            const content = document.getElementById(id);
            if (button && content) {
                button.setAttribute('aria-expanded', 'true');
                content.setAttribute('aria-hidden', 'false');
                content.style.display = 'block';
            }
        });
    },

    /**
     * Load filters from localStorage
     */
    loadFiltersFromStorage() {
        try {
            const saved = this.storage.get('vsa-filters');
            if (saved) {
                this.state.filters = { ...this.state.filters, ...saved };
                this.state.view = saved.view || this.state.view;
            }
        } catch (error) {
            this.log.warn('Failed to load filters from storage:', error);
        }
    },

    /**
     * Save filters to localStorage
     */
    saveFiltersToStorage() {
        try {
            this.storage.set('vsa-filters', {
                ...this.state.filters,
                view: this.state.view
            });
        } catch (error) {
            this.log.warn('Failed to save filters to storage:', error);
        }
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
