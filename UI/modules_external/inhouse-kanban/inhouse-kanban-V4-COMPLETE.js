/**
 * ============================================================================
 * INHOUSE KANBAN MODULE - COMPLETE MODERN FRAMEWORK V4.0
 * ============================================================================
 * 
 * FILE: UI/modules_external/inhouse-kanban/inhouse-kanban-V4-COMPLETE.js
 * VERSION: 4.0.0 - Complete Modern Framework Refactor
 * ARCHITECTURE: Composition-based (NO BaseModule inheritance)
 * PATTERN: Export default object with lifecycle hooks
 * 
 * CAPABILITIES:
 * ✅ Dashboard: Full Kanban board with workboards, stages, job cards
 * ✅ Sidebar: Quick access panel with filters and analytics
 * ✅ Sub-tabs: Workboard + Analytics views
 * ✅ Advanced Color Settings: 3 customizable tables (Priority, Due Date, Banner)
 * ✅ Card Mute Management: Per-card customization with export
 * 
 * MIGRATED FROM: BaseModule class (5,650 lines) → Modern composition (4,500 lines)
 * LAST MODIFIED: 2025-11-30
 * ============================================================================
 */

export default {
    // ========================================================================
    // MODULE METADATA & STATE
    // ========================================================================

    moduleId: 'inhouse-kanban',
    version: '4.0.0',

    // Injected utilities (set by ModuleLoader via Object.assign)
    dom: null,
    api: null,
    storage: null,
    events: null,
    log: null,

    // API configuration
    API_BASE_URL: window.API_BASE_URL || 'http://localhost:5001',
    apiEndpoint: '/api/inhouse-kanban',
    analyticsApiBase: null,
    backendUrl: null,

    // Module state
    state: {
        jobs: [],
        stages: [],
        metrics: {},
        filters: {
            timeframe_months: -6,
            priority_filter: 'all',
            stage_id: null,
            search_text: ''
        },
        activeWorkboard: 'main',
        currentView: 'kanban-board',
        activeSubTab: 'workboard',
        selectedJob: null,
        lastRefresh: null,
        isLoading: false,
        initialized: false
    },

    // UI references
    ui: {
        dashboardContainer: null,
        sidebarContainer: null,
        kanbanBoard: null,
        workboardSelector: null,
        metricsContainer: null
    },

    // Event cleanup tracking
    eventCleanupFns: [],
    refreshTimer: null,

    // Stage transition cache
    stageTransitionCache: new Map(),

    // Card mute settings
    mutedCards: new Map(),
    jobsCache: new Map(),

    // Color settings
    colorSettings: null,
    colorToggles: {
        showBorderColors: true,
        showBackgroundColors: true,
        showBannerColors: true
    },

    // Drag state
    draggedJob: null,

    // Stage mapping with icons and colors
    stageMapping: {
        'ArtOnly': { icon: 'fa-brush', color: '#FF6B6B', label: 'Art Only' },
        'ArtAndPrint': { icon: 'fa-palette', color: '#FF8E53', label: 'Art & Print' },
        'OnHold': { icon: 'fa-pause-circle', color: '#FFA500', label: 'On Hold' },
        'Digital - 9110': { icon: 'fa-print', color: '#4ECDC4', label: 'Digital - 9110' },
        'Digital - Other': { icon: 'fa-print', color: '#45B7D1', label: 'Digital - Other' },
        'Digital - OutSource': { icon: 'fa-exchange', color: '#96CEB4', label: 'Digital - OutSource' },
        'Digital - Cello': { icon: 'fa-star', color: '#FFEAA7', label: 'Digital - Cello' },
        'Digital - Bindery': { icon: 'fa-book', color: '#DDA0DD', label: 'Digital - Bindery' },
        'TicketComplete': { icon: 'fa-check', color: '#98D8C8', label: 'Ticket Complete' },
        'ReadyToPrint': { icon: 'fa-hourglass-start', color: '#F7DC6F', label: 'Ready to Print' },
        'Signs - UV': { icon: 'fa-sun', color: '#BB8FCE', label: 'Signs - UV' },
        'Signs - Solvent': { icon: 'fa-droplet', color: '#AED6F1', label: 'Signs - Solvent' },
        'Signs - Laminate': { icon: 'fa-layer-group', color: '#A3E4D7', label: 'Signs - Laminate' },
        'Signs - Finishing': { icon: 'fa-toolbox', color: '#D5A6BD', label: 'Signs - Finishing' }
    },

    // Stage display order
    stageOrder: [
        'ReadyToPrint',
        'Digital - 9110',
        'Digital - Other',
        'Digital - OutSource',
        'Digital - Cello',
        'Digital - Bindery',
        'TicketComplete',
        'ArtOnly',
        'ArtAndPrint',
        'OnHold',
        'Signs - UV',
        'Signs - Solvent',
        'Signs - Laminate',
        'Signs - Finishing'
    ],

    // Workboard definitions
    workboards: {
        'main': {
            name: 'Main Workflow',
            icon: 'fa-stream',
            stages: [11, 4, 6, 8, 9]
        },
        'wide-format': {
            name: 'Wide Format',
            icon: 'fa-rectangle-landscape',
            stages: [11, 12, 13, 14, 15, 9]
        },
        'apg': {
            name: 'APG Supplies',
            icon: 'fa-box-open',
            stages: [3, 6, 8, 9]
        },
        'publishing': {
            name: 'Publishing',
            icon: 'fa-book',
            stages: [11, 4, 8, 9]
        }
    },

    // Sidebar state
    sidebar: {
        isOpen: false,
        selectedWorkboard: 'main',
        selectedColumn: null,
        expandedCards: new Set(),
        filters: {
            search: '',
            dateRange: '-6',
            priority: 'all'
        }
    },

    // ========================================================================
    // LIFECYCLE HOOKS (Modern Framework Pattern)
    // ========================================================================

    /**
     * DASHBOARD LIFECYCLE HOOK
     * Called when: User loads dashboard view
     */
    async onDashboardLoad(utilities) {
        // CRITICAL: Inject utilities first
        Object.assign(this, utilities);
        this.log.info('🏭 InHouse Kanban Dashboard loading...');

        // Prevent duplicate initialization
        if (this.state.initialized) {
            this.log.warn('⚠️ Module already initialized, skipping...');
            return;
        }

        try {
            // Initialize configuration
            this.backendUrl = this.API_BASE_URL;
            this.analyticsApiBase = this.API_BASE_URL + this.apiEndpoint;

            // Load persistent settings
            this.loadColorSettings();
            this.loadColorToggles();
            this.loadMutedCards();

            // Get container
            this.ui.dashboardContainer = this.dom.getContainer();
            if (!this.ui.dashboardContainer) {
                throw new Error('Dashboard container not found');
            }

            // Inject critical CSS
            this.injectCriticalStyles();

            // Apply module colors
            this.applyModuleColors();

            // Initialize sub-tabs (workboard + analytics)
            this.initializeSubTabs();

            // Setup event listeners
            this.setupEventListeners();

            // Load data
            await this.loadInitialData();

            // Start auto-refresh
            this.startAutoRefresh();

            // Store global reference
            window.currentKanbanModule = this;

            this.state.initialized = true;
            this.log.success('✅ Dashboard loaded successfully', {
                jobs: this.state.jobs.length,
                stages: this.state.stages.length
            });

        } catch (error) {
            this.log.error('❌ Failed to load dashboard', error);
            this.showErrorState(error);
            throw error;
        }
    },

    /**
     * SIDEBAR LIFECYCLE HOOK
     * Called when: User opens sidebar
     */
    async onSidebarLoad(utilities) {
        Object.assign(this, utilities);
        this.log.info('🔧 InHouse Kanban Sidebar loading...');

        try {
            this.ui.sidebarContainer = this.dom.getContainer();
            if (!this.ui.sidebarContainer) {
                throw new Error('Sidebar container not found');
            }

            this.sidebar.isOpen = true;
            this.setupSidebarEventListeners();

            if (this.state.jobs.length > 0) {
                this.loadSidebarWorkboardColumns(this.sidebar.selectedWorkboard);
            } else {
                const cardsContainer = this.ui.sidebarContainer.querySelector('#sidebar-cards-container');
                if (cardsContainer) {
                    cardsContainer.innerHTML = '<div class="sidebar-empty"><i class="fas fa-sync fa-spin"></i><p>Loading data...</p></div>';
                }
            }

            window.inhouseKanbanSidebar = this;
            this.log.success('✅ Sidebar loaded successfully');

        } catch (error) {
            this.log.error('❌ Failed to load sidebar', error);
            throw error;
        }
    },

    /**
     * CLEANUP LIFECYCLE HOOK
     * Called when: Module is unloaded
     */
    onUnload(utilities) {
        Object.assign(this, utilities);
        this.log.info('🧹 InHouse Kanban unloading...');

        try {
            // Cleanup event listeners
            this.eventCleanupFns.forEach(cleanup => {
                try {
                    cleanup();
                } catch (error) {
                    this.log.warn('Failed to cleanup event listener', error);
                }
            });
            this.eventCleanupFns = [];

            // Stop auto-refresh
            if (this.refreshTimer) {
                clearInterval(this.refreshTimer);
                this.refreshTimer = null;
            }

            // Save state
            this.storage.set('kanban-filters', this.state.filters);
            this.storage.set('kanban-active-workboard', this.state.activeWorkboard);

            // Clear dashboard container HTML
            if (this.ui.dashboardContainer) {
                this.ui.dashboardContainer.innerHTML = '';
            }

            // Clear sidebar container HTML
            if (this.ui.sidebarContainer) {
                this.ui.sidebarContainer.innerHTML = '';
            }

            // Clear references
            this.ui.dashboardContainer = null;
            this.ui.sidebarContainer = null;
            this.ui.kanbanBoard = null;
            this.ui.workboardSelector = null;
            this.ui.metricsContainer = null;

            // Clear state
            this.state.jobs = [];
            this.state.stages = [];
            this.state.initialized = false;
            this.state.isLoading = false;
            this.state.selectedJob = null;

            // Clear caches
            this.stageTransitionCache.clear();
            this.jobsCache.clear();
            this.mutedCards.clear();

            // Remove any open dialogs/overlays
            const dialogOverlay = document.getElementById('mute-dialog-overlay');
            if (dialogOverlay) {
                dialogOverlay.remove();
            }

            // Remove any toasts
            document.querySelectorAll('.kanban-toast').forEach(toast => toast.remove());

            // Remove injected CSS
            const injectedStyle = document.getElementById('inhouse-kanban-critical-styles');
            if (injectedStyle) {
                injectedStyle.remove();
            }

            // Clear global references
            delete window.currentKanbanModule;
            delete window.inhouseKanbanSidebar;

            this.log.success('✅ Module unloaded successfully');

        } catch (error) {
            this.log.error('Error during unload', error);
        }
    },

    // ========================================================================
    // INITIALIZATION HELPERS
    // ========================================================================

    injectCriticalStyles() {
        const styleId = 'inhouse-kanban-critical-styles';
        const existingStyle = document.getElementById(styleId);
        if (existingStyle) {
            existingStyle.remove();
        }

        const style = document.createElement('style');
        style.id = styleId;
        style.setAttribute('data-module', 'inhouse-kanban');
        style.textContent = `
            /* Critical inline styles for InHouse Kanban */
            #tab-inhouse-kanban {
                display: flex;
                flex-direction: column;
                height: 100%;
                overflow: hidden;
            }
            
            #tab-inhouse-kanban:not(.active) {
                display: none !important;
            }
            
            #tab-inhouse-kanban .dashboard-wrapper.inhouse-kanban {
                display: flex;
                flex-direction: column;
                height: 100%;
                overflow: hidden;
            }
            
            .sub-tab-content {
                display: flex;
                flex-direction: column;
                height: calc(100vh - 200px);
                overflow: hidden;
            }
            
            #tab-inhouse-kanban .workboard-container {
                overflow-y: auto;
                overflow-x: auto;
                flex: 1;
                height: 100%;
            }
            
            #tab-inhouse-kanban .inhouse-kanban-board,
            #tab-inhouse-kanban .kanban-board {
                display: flex;
                flex-direction: row;
                gap: 20px;
                padding: 20px;
                overflow-x: auto;
                min-height: min-content;
            }
            
            #tab-inhouse-kanban .column-body {
                padding: 15px;
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 12px;
                min-height: 0;
                overflow-y: visible;
            }
            
            /* Metric Cards - V9 Style */
            #tab-inhouse-kanban .metric-card {
                flex: 1;
                min-width: 200px;
                background: #1A1F2E;
                border: 1px solid #2A3142;
                border-radius: 8px;
                padding: 16px;
                display: flex;
                align-items: center;
                gap: 16px;
                transition: all 0.2s ease;
            }
            
            #tab-inhouse-kanban .metric-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                border-color: #00509E;
            }
            
            #tab-inhouse-kanban .metric-icon {
                width: 48px;
                height: 48px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                flex-shrink: 0;
            }
            
            #tab-inhouse-kanban .metric-content {
                flex: 1;
            }
            
            #tab-inhouse-kanban .metric-label {
                font-size: 12px;
                color: #9CA3AF;
                margin-bottom: 4px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            #tab-inhouse-kanban .metric-value {
                font-size: 24px;
                font-weight: 700;
                color: #E5E7EB;
            }
            
            .inhouse-kanban-board, .kanban-board {
                display: flex;
                flex-direction: row;
                gap: 20px;
                padding: 20px;
                overflow-x: auto;
                flex: 1;
            }
            
            .kanban-column, .inhouse-kanban-column {
                min-width: 340px;
                max-width: 340px;
                flex-shrink: 0;
            }
            
            .pulse-border {
                animation: pulseBorder 2s ease-in-out infinite;
            }
            
            @keyframes pulseBorder {
                0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
                50% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
            }
            
            .module-sub-tabs {
                display: flex;
                gap: 4px;
                padding: 0 20px;
                background: #1A1F2E;
                border-bottom: 2px solid #00509E;
            }
            
            .sub-tab-btn {
                padding: 12px 24px;
                background: transparent;
                border: none;
                color: #8b949e;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                border-bottom: 3px solid transparent;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .sub-tab-btn.active {
                color: #00509E;
                border-bottom-color: #00509E;
            }
            
            .sub-tab-btn:hover {
                color: #58a6ff;
            }
            
            .color-toggle-btn {
                padding: 6px 14px;
                border: 2px solid #58a6ff;
                background: #0d1117;
                color: #58a6ff;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.9em;
                display: flex;
                align-items: center;
                gap: 6px;
                transition: all 0.2s;
            }
            
            .color-toggle-btn.active {
                background: #58a6ff;
                color: #ffffff;
            }
            
            /* V9 Card Styling */
            #tab-inhouse-kanban .kanban-card {
                position: relative;
                border-radius: 8px;
                padding: 12px;
                cursor: pointer;
                transition: all 0.2s;
                margin-bottom: 12px;
            }
            
            #tab-inhouse-kanban .kanban-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }
            
            #tab-inhouse-kanban .card-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
                gap: 8px;
            }
            
            #tab-inhouse-kanban .card-header-left,
            #tab-inhouse-kanban .card-header-right {
                display: flex;
                align-items: center;
                gap: 6px;
            }
            
            #tab-inhouse-kanban .card-header-center {
                flex: 0 0 auto;
            }
            
            #tab-inhouse-kanban .card-priority {
                font-size: 18px;
            }
            
            #tab-inhouse-kanban .card-mute-btn {
                background: none;
                border: none;
                color: #6e7681;
                cursor: pointer;
                padding: 4px;
                font-size: 14px;
                transition: color 0.2s;
            }
            
            #tab-inhouse-kanban .card-mute-btn:hover {
                color: #f0f6fc;
            }
            
            #tab-inhouse-kanban .muted-card .card-mute-btn {
                color: #f85149;
            }
            
            #tab-inhouse-kanban .card-title {
                font-size: 14px;
                font-weight: 600;
                color: #f0f6fc;
                margin-bottom: 8px;
                line-height: 1.4;
                overflow: hidden;
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
            }
            
            #tab-inhouse-kanban .card-meta {
                display: flex;
                flex-direction: column;
                gap: 6px;
                margin-bottom: 8px;
            }
            
            #tab-inhouse-kanban .card-client-name {
                font-size: 12px;
                color: #8b949e;
                display: flex;
                align-items: center;
                gap: 6px;
                font-weight: 500;
            }
            
            #tab-inhouse-kanban .card-qty-label {
                font-size: 12px;
                color: #8b949e;
                font-weight: 500;
            }
            
            #tab-inhouse-kanban .card-specs-row {
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
                font-size: 11px;
                color: #6e7681;
            }
            
            #tab-inhouse-kanban .card-specs-row .spec-item {
                display: inline-flex;
                align-items: center;
                padding: 2px 6px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 3px;
            }
            
            #tab-inhouse-kanban .card-finish-row {
                display: flex;
                gap: 6px;
                flex-wrap: wrap;
            }
            
            #tab-inhouse-kanban .card-timing-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 8px;
                padding: 6px 8px;
                margin-bottom: 8px;
                border-radius: 4px;
                background: rgba(255, 255, 255, 0.03);
            }
            
            #tab-inhouse-kanban .timing-item {
                font-size: 11px;
                display: flex;
                align-items: center;
                gap: 4px;
                font-weight: 600;
            }
            
            #tab-inhouse-kanban .timing-item.stage-normal {
                color: #9ca3af;
            }
            
            #tab-inhouse-kanban .timing-item.stage-warning {
                color: #fbbf24;
            }
            
            #tab-inhouse-kanban .timing-item.stage-overdue {
                color: #fca5a5;
            }
            
            #tab-inhouse-kanban .status-badge {
                font-size: 10px;
                padding: 3px 8px;
                border-radius: 4px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            #tab-inhouse-kanban .status-badge.status-active {
                background: #1f2937;
                color: #10b981;
            }
            
            #tab-inhouse-kanban .status-badge.status-delayed {
                background: #7d1f1f;
                color: #fca5a5;
            }
            
            #tab-inhouse-kanban .status-badge.status-warning {
                background: #78350f;
                color: #fbbf24;
            }
            
            #tab-inhouse-kanban .status-badge.status-success {
                background: #14532d;
                color: #10b981;
            }
            
            #tab-inhouse-kanban .card-time {
                font-size: 11px;
                color: #6e7681;
            }
            
            #tab-inhouse-kanban .card-stage-time {
                display: flex;
                align-items: center;
                gap: 6px;
                padding: 6px 8px;
                border-radius: 4px;
                font-size: 11px;
                margin-bottom: 8px;
                font-weight: 600;
            }
            
            #tab-inhouse-kanban .stage-normal {
                background: #1f2937;
                color: #9ca3af;
            }
            
            #tab-inhouse-kanban .stage-warning {
                background: #78350f;
                color: #fbbf24;
            }
            
            #tab-inhouse-kanban .stage-overdue {
                background: #7d1f1f;
                color: #fca5a5;
            }
            
            #tab-inhouse-kanban .card-footer {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            #tab-inhouse-kanban .card-tags {
                display: flex;
                gap: 6px;
                flex-wrap: wrap;
            }
            
            #tab-inhouse-kanban .card-tag {
                font-size: 11px;
                padding: 3px 8px;
                background: #1f2937;
                color: #9ca3af;
                border-radius: 4px;
                display: flex;
                align-items: center;
                gap: 4px;
            }
            
            /* V10 Enhanced Card Elements */
            #tab-inhouse-kanban .tier-badge {
                display: flex;
                align-items: center;
                justify-content: center;
                width: 24px;
                height: 24px;
                border-radius: 50%;
                font-size: 11px;
                color: #ffffff;
                font-weight: 700;
            }
            
            #tab-inhouse-kanban .card-client-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 8px;
                margin-bottom: 4px;
            }
            
            #tab-inhouse-kanban .business-badge {
                display: inline-flex;
                align-items: center;
                gap: 4px;
                font-size: 9px;
                color: #9ca3af;
                padding: 2px 6px;
                background: rgba(107, 114, 128, 0.15);
                border: 1px solid rgba(107, 114, 128, 0.3);
                border-radius: 3px;
                white-space: nowrap;
            }
            
            #tab-inhouse-kanban .business-badge i {
                font-size: 8px;
            }
            
            #tab-inhouse-kanban .card-quantity {
                display: flex;
                align-items: center;
                gap: 4px;
                font-size: 11px;
                color: #9ca3af;
                margin-bottom: 4px;
            }
            
            #tab-inhouse-kanban .card-quantity i {
                font-size: 10px;
                opacity: 0.7;
            }
            
            #tab-inhouse-kanban .paper-specs {
                color: #6e7681;
                font-size: 10px;
                margin-left: 4px;
            }
            
            #tab-inhouse-kanban .finishing-icons {
                display: flex;
                gap: 6px;
                padding: 4px 0;
                margin-bottom: 4px;
            }
            
            #tab-inhouse-kanban .finishing-icon {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 20px;
                height: 20px;
                border-radius: 3px;
                background: rgba(59, 130, 246, 0.15);
                border: 1px solid rgba(59, 130, 246, 0.3);
                color: #3b82f6;
                font-size: 10px;
                cursor: help;
            }
            
            #tab-inhouse-kanban .finishing-icon:hover {
                background: rgba(59, 130, 246, 0.25);
                border-color: rgba(59, 130, 246, 0.5);
            }
            
            /* Modal Badge Styles */
            #tab-inhouse-kanban .badge {
                display: inline-flex;
                align-items: center;
                gap: 4px;
            }
            
            #tab-inhouse-kanban .kanban-notes-text {
                color: #d1d5db;
                line-height: 1.6;
                font-size: 13px;
            }
            
            #tab-inhouse-kanban .kanban-modal-footer {
                display: flex;
                justify-content: flex-end;
                padding: 16px 24px;
                border-top: 1px solid #30363d;
                background: #0d1117;
                border-radius: 0 0 12px 12px;
            }
        `;
        document.head.appendChild(style);
    },

    applyModuleColors() {
        const primaryColor = '#00509E';
        const container = this.ui.dashboardContainer;

        if (container) {
            container.style.setProperty('--module-primary', primaryColor);
            container.style.setProperty('--module-primary-light', this.lightenColor(primaryColor, 0.1));
        }
    },

    // ========================================================================
    // SUB-TAB SYSTEM (Workboard + Analytics Views)
    // ========================================================================

    /**
     * Get container for specific sub-tab
     */
    getSubTabContainer(tabName) {
        if (tabName) {
            const normalizedTabName = (tabName === 'kanban-board' || tabName === 'workboard') ? 'workboard' : tabName;
            const subTabContainer = document.getElementById(`inhouse-kanban-subtab-${normalizedTabName}`);

            if (subTabContainer) {
                this.log.info(`Returning sub-tab container: #inhouse-kanban-subtab-${normalizedTabName}`);
                return subTabContainer;
            }
        }

        const container = this.ui.dashboardContainer;
        if (!container) {
            throw new Error(`Cannot find container for module ${this.moduleId}`);
        }

        return container;
    },

    /**
     * Initialize sub-tabs with navigation
     */
    initializeSubTabs() {
        this.state.activeSubTab = 'workboard';
        this.createSubTabNavigation();
        this.initializeKanbanBoard();
        this.initializeAnalytics();
        this.switchSubTab('workboard');
    },

    /**
     * Create sub-tab navigation bar
     */
    createSubTabNavigation() {
        const container = this.getSubTabContainer();
        const primaryColor = '#00509E';

        const navHtml = `
            <div class="dashboard-wrapper inhouse-kanban">
                <!-- Dashboard Header -->
                <div class="dashboard-header">
                    <div class="dashboard-header-left">
                        <h2 class="dashboard-title">
                            <i class="fas fa-industry"></i>
                            InHouse Print Workboard
                        </h2>
                        <div class="dashboard-stats">
                            <span class="stat-item">
                                <i class="fas fa-tasks"></i>
                                <strong id="kanban-total-jobs">0</strong> Jobs
                            </span>
                            <span class="stat-item">
                                <i class="fas fa-exclamation-circle" style="color: #ef4444;"></i>
                                <strong id="kanban-critical-jobs">0</strong> Critical
                            </span>
                            <span class="stat-item">
                                <i class="fas fa-exclamation-triangle" style="color: #f97316;"></i>
                                <strong id="kanban-overdue-jobs">0</strong> Overdue
                            </span>
                        </div>
                    </div>
                    <div class="dashboard-header-right">
                        <button class="dashboard-action-btn" onclick="window.currentKanbanModule.refreshData()" title="Refresh data">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                    </div>
                </div>

                <!-- Quick Navigation Bar (Subtabs) -->
                <div class="quick-nav-bar">
                    <div class="quick-nav-container">
                        <button class="module-subtab-btn active" data-tab="workboard" onclick="window.currentKanbanModule.switchSubTab('workboard')">
                            <i class="fas fa-industry"></i>
                            Production Workboard
                        </button>
                        <button class="module-subtab-btn" data-tab="analytics" onclick="window.currentKanbanModule.switchSubTab('analytics')">
                            <i class="fas fa-chart-line"></i>
                            Analytics
                        </button>
                    </div>
                </div>
                
                <!-- Sub-tab content containers -->
                <div id="inhouse-kanban-subtab-workboard" class="sub-tab-content active"></div>
                <div id="inhouse-kanban-subtab-analytics" class="sub-tab-content" style="display: none;"></div>
            </div>
        `;

        container.innerHTML = navHtml;
    },

    /**
     * Switch between sub-tabs
     */
    switchSubTab(tabName) {
        this.log.info(`🔄 Switching to sub-tab: ${tabName}`);
        this.state.activeSubTab = tabName;

        // Update button states
        document.querySelectorAll('.quick-nav-bar .module-subtab-btn').forEach(btn => {
            if (btn.dataset.tab === tabName) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Show/hide content
        const workboardContent = document.getElementById('inhouse-kanban-subtab-workboard');
        const analyticsContent = document.getElementById('inhouse-kanban-subtab-analytics');

        if (tabName === 'workboard') {
            if (workboardContent) workboardContent.style.display = 'flex';
            if (analyticsContent) analyticsContent.style.display = 'none';
        } else if (tabName === 'analytics') {
            if (workboardContent) workboardContent.style.display = 'none';
            if (analyticsContent) analyticsContent.style.display = 'flex';
        }
    },

    /**
     * Initialize Kanban Board tab
     */
    initializeKanbanBoard() {
        this.log.info('Initializing Kanban board structure...');

        const container = this.getSubTabContainer('kanban-board');
        const primaryColor = '#00509E';

        container.innerHTML = `
            <div class="filters-bar" style="margin: 15px 20px; padding: 12px; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; display: flex; gap: 15px; flex-wrap: wrap; align-items: center;">
                <div class="filter-group" style="display: flex; align-items: center; gap: 8px;">
                    <label style="color: #8b949e; font-size: 0.9em; font-weight: 600;"><i class="fas fa-calendar-alt"></i> Timeframe:</label>
                    <select id="timeframe-selector" class="filter-select" style="padding: 6px 12px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6; font-size: 0.9em;">
                        <option value="-1">Last 1 month</option>
                        <option value="-2">Last 2 months</option>
                        <option value="-3">Last 3 months</option>
                        <option value="-6" selected>Last 6 months</option>
                        <option value="-9">Last 9 months</option>
                        <option value="-12">Last 12 months</option>
                    </select>
                </div>
                
                <div class="filter-group" style="display: flex; align-items: center; gap: 8px;">
                    <label style="color: #8b949e; font-size: 0.9em; font-weight: 600;"><i class="fas fa-filter"></i> Priority:</label>
                    <select id="priority-selector" class="filter-select" style="padding: 6px 12px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6; font-size: 0.9em;">
                        <option value="all">All Priorities</option>
                        <option value="critical">Critical Only</option>
                        <option value="high">High Priority</option>
                        <option value="urgent">Urgent</option>
                        <option value="normal">Normal</option>
                        <option value="low">Low Priority</option>
                    </select>
                </div>
                
                <div class="filter-group" style="flex: 1; display: flex; align-items: center; gap: 8px;">
                    <label style="color: #8b949e; font-size: 0.9em; font-weight: 600;"><i class="fas fa-search"></i> Search:</label>
                    <input type="text" id="search-input" class="filter-input" placeholder="Search by client, job, or ticket #..." style="flex: 1; padding: 6px 12px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6; font-size: 0.9em;">
                </div>
                
                <div class="filter-group" style="display: flex; align-items: center; gap: 8px;">
                    <button id="inhouse-refresh-btn" class="btn-secondary" style="padding: 6px 14px; background: #0d1117; border: 2px solid ${primaryColor}; color: ${primaryColor}; border-radius: 6px; cursor: pointer; font-size: 0.9em; display: flex; align-items: center; gap: 6px; transition: all 0.2s;">
                        <i class="fas fa-sync"></i> Refresh
                    </button>
                </div>
                
                <div class="filter-group" style="display: flex; align-items: center;">
                    <span class="last-refresh" id="last-refresh-time" style="color: #6e7681; font-size: 0.85em;">
                        <span class="time-value">Just now</span>
                    </span>
                </div>
            </div>
            
            <!-- Color Coding & Advanced Settings (Combined Collapsible Section) -->
            <div style="margin: 15px 20px; padding: 12px; background: #0d1117; border: 1px solid #30363d; border-radius: 6px;">
                <div onclick="window.currentKanbanModule.toggleAdvancedColorSettings()" style="display: flex; align-items: center; gap: 12px; cursor: pointer; user-select: none; padding-bottom: 12px; border-bottom: 1px solid #21262d;">
                    <i class="fas fa-chevron-right" id="advanced-color-toggle-icon" style="color: #8b949e; transition: transform 0.2s;"></i>
                    <div style="display: flex; align-items: center; gap: 8px; color: #8b949e; font-weight: bold;">
                        <i class="fas fa-palette"></i>
                        <span>Color Settings</span>
                    </div>
                    <div style="flex: 1;"></div>
                    <button id="toggle-border-colors" class="color-toggle-btn active" onclick="event.stopPropagation();">
                        <i class="fas fa-border-style"></i> Borders
                    </button>
                    <button id="toggle-background-colors" class="color-toggle-btn active" onclick="event.stopPropagation();">
                        <i class="fas fa-fill"></i> Backgrounds
                    </button>
                    <button id="toggle-banner-colors" class="color-toggle-btn active" onclick="event.stopPropagation();">
                        <i class="fas fa-flag"></i> Banners
                    </button>
                </div>
                
                <div id="advanced-color-settings-content" style="display: none; padding-top: 15px;">
                <!-- Mute Card Controls -->
                <div style="display: flex; gap: 10px; margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #21262d;">
                    <button onclick="window.currentKanbanModule.clearAllMutedCards()" class="btn-sm" style="padding: 6px 12px; background: #0d1117; border: 1px solid #da3633; color: #da3633; border-radius: 4px; cursor: pointer; font-size: 0.85em;">
                        <i class="fas fa-times-circle"></i> Clear Muted (<span class="muted-cards-count">0</span>)
                    </button>
                    <button onclick="window.currentKanbanModule.showMutedCardsOnly()" class="btn-sm" style="padding: 6px 12px; background: #0d1117; border: 1px solid #58a6ff; color: #58a6ff; border-radius: 4px; cursor: pointer; font-size: 0.85em;">
                        <i class="fas fa-eye"></i> Show Muted
                    </button>
                    <button onclick="window.currentKanbanModule.exportMutedCards()" class="btn-sm" style="padding: 6px 12px; background: #0d1117; border: 1px solid #238636; color: #238636; border-radius: 4px; cursor: pointer; font-size: 0.85em;">
                        <i class="fas fa-file-export"></i> Export
                    </button>
                </div>
                
                <div style="display: flex; gap: 10px; margin-bottom: 20px;">
                    <button onclick="window.currentKanbanModule.testAdvancedColorSettings()" style="padding: 6px 14px; background: #238636; border: none; color: white; border-radius: 4px; cursor: pointer; font-size: 0.9em;">
                        Test Changes
                    </button>
                    <button onclick="window.currentKanbanModule.saveAdvancedColorSettings()" style="padding: 6px 14px; background: #0969da; border: none; color: white; border-radius: 4px; cursor: pointer; font-size: 0.9em;">
                        Save Settings
                    </button>
                    <button onclick="window.currentKanbanModule.resetAdvancedColorSettings()" style="padding: 6px 14px; background: #da3633; border: none; color: white; border-radius: 4px; cursor: pointer; font-size: 0.9em;">
                        Reset to Defaults
                    </button>
                </div>
                
                <div style="margin-bottom: 25px;">
                    <h4 style="margin: 0 0 10px 0; color: #8b949e; font-size: 14px; font-weight: 600;">Priority Border Colors</h4>
                    <table style="width: 100%; border-collapse: collapse; background: #161b22; border-radius: 6px; overflow: hidden;">
                        <thead style="background: #21262d;">
                            <tr>
                                <th style="padding: 10px; text-align: left; color: #8b949e; font-size: 0.9em;">Priority Level</th>
                                <th style="padding: 10px; text-align: left; color: #8b949e; font-size: 0.9em;">Border Color</th>
                                <th style="padding: 10px; text-align: left; color: #8b949e; font-size: 0.9em;">Width</th>
                                <th style="padding: 10px; text-align: left; color: #8b949e; font-size: 0.9em;">Preview</th>
                            </tr>
                        </thead>
                        <tbody id="priority-settings-table"></tbody>
                    </table>
                </div>
                
                <div style="margin-bottom: 25px;">
                    <h4 style="margin: 0 0 10px 0; color: #8b949e; font-size: 14px; font-weight: 600;">Due Date Styling</h4>
                    <table style="width: 100%; border-collapse: collapse; background: #161b22; border-radius: 6px; overflow: hidden;">
                        <thead style="background: #21262d;">
                            <tr>
                                <th style="padding: 10px; text-align: left; color: #8b949e; font-size: 0.85em;">Timeframe</th>
                                <th style="padding: 10px; text-align: left; color: #8b949e; font-size: 0.85em;">Border Color</th>
                                <th style="padding: 10px; text-align: left; color: #8b949e; font-size: 0.85em;">Type</th>
                                <th style="padding: 10px; text-align: left; color: #8b949e; font-size: 0.85em;">Width</th>
                                <th style="padding: 10px; text-align: center; color: #8b949e; font-size: 0.85em;">Pulse</th>
                                <th style="padding: 10px; text-align: left; color: #8b949e; font-size: 0.85em;">BG Color</th>
                                <th style="padding: 10px; text-align: left; color: #8b949e; font-size: 0.85em;">Preview</th>
                            </tr>
                        </thead>
                        <tbody id="duedate-settings-table"></tbody>
                    </table>
                </div>
                
                <div>
                    <h4 style="margin: 0 0 10px 0; color: #8b949e; font-size: 14px; font-weight: 600;">Urgency Banners</h4>
                    <table style="width: 100%; border-collapse: collapse; background: #161b22; border-radius: 6px; overflow: hidden;">
                        <thead style="background: #21262d;">
                            <tr>
                                <th style="padding: 10px; text-align: left; color: #8b949e; font-size: 0.9em;">State</th>
                                <th style="padding: 10px; text-align: left; color: #8b949e; font-size: 0.9em;">Background</th>
                                <th style="padding: 10px; text-align: left; color: #8b949e; font-size: 0.9em;">Text</th>
                                <th style="padding: 10px; text-align: left; color: #8b949e; font-size: 0.9em;">Preview</th>
                            </tr>
                        </thead>
                        <tbody id="banner-settings-table"></tbody>
                    </table>
                </div>
                </div>
            </div>
            
            <!-- Workboard Selector -->
            <div class="inhouse-kanban-workboard-selector" id="workboard-selector" style="margin: 0 20px; padding: 10px; background: #161b22; border-radius: 6px; display: flex; gap: 8px;"></div>
            
            <!-- Kanban Board Container -->
            <div class="inhouse-kanban-board" id="kanban-board" style="margin: 0 20px; display: flex; gap: 20px; overflow-x: auto; flex: 1; padding: 20px 0;"></div>
        `;

        // CRITICAL: Query elements AFTER innerHTML is set - use getElementById for global search
        this.ui.kanbanBoard = document.getElementById('kanban-board');
        this.ui.workboardSelector = document.getElementById('workboard-selector');
        this.ui.metricsContainer = document.getElementById('kanban-metrics');

        // Debug: Confirm elements were found
        this.log.info('📍 Kanban UI elements initialized:', {
            kanbanBoard: !!this.ui.kanbanBoard,
            workboardSelector: !!this.ui.workboardSelector,
            metricsContainer: !!this.ui.metricsContainer,
            workboardSelectorHTML: this.ui.workboardSelector?.outerHTML?.substring(0, 100)
        });

        if (!this.ui.workboardSelector) {
            this.log.error('❌ CRITICAL: workboard-selector element not found in DOM!');
        }
    },

    /**
     * Initialize Analytics tab
     */
    initializeAnalytics() {
        const container = this.getSubTabContainer('analytics');
        if (!container) return;

        container.innerHTML = `
            <div style="padding: 30px; color: #8b949e; text-align: center;">
                <i class="fas fa-chart-line" style="font-size: 64px; opacity: 0.3; margin-bottom: 20px;"></i>
                <h2 style="color: #f0f6fc; margin: 0 0 10px 0;">Analytics Dashboard</h2>
                <p style="margin: 0;">Advanced production analytics coming soon...</p>
            </div>
        `;
    },

    // ========================================================================
    // DATA LOADING & API METHODS
    // ========================================================================

    async loadInitialData() {
        this.state.isLoading = true;
        this.log.info('📊 loadInitialData() called - about to render components');
        try {
            await Promise.all([
                this.loadJobs(),
                this.loadStages()
            ]);

            this.log.info('🎯 Rendering workboard selector buttons...');
            this.renderWorkboardSelector();

            this.log.info('📈 Rendering metrics...');
            this.renderMetrics();

            this.log.info('🏗️ Rendering kanban board...');
            this.renderKanbanBoard();

            this.log.info('🎨 Rendering color settings tables...');
            this.renderColorSettingsTables();

            this.log.info('🔇 Updating muted card count...');
            this.updateMutedCardCount();

            this.log.success('✅ All components rendered successfully');
        } catch (error) {
            this.log.error('Failed to load initial data', error);
            throw error;
        } finally {
            this.state.isLoading = false;
        }
    },

    async loadJobs() {
        try {
            const params = new URLSearchParams({
                timeframe_months: this.state.filters.timeframe_months || -6,
                priority_filter: this.state.filters.priority_filter || 'all',
                stage_id: this.state.filters.stage_id || '',
                search_text: this.state.filters.search_text || ''
            });

            const url = `${this.analyticsApiBase}/jobs?${params}`;
            const response = await fetch(url, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                throw new Error(`Failed to load jobs: ${response.statusText}`);
            }

            const data = await response.json();
            const rawJobs = Array.isArray(data) ? data : data.jobs || [];

            // ✅ FIX: Map API field names to expected format
            // API returns: TicketID, StageID, ClientName, ShortJobDesc, PriorityScore, etc.
            // Code expects: id/ticket_id, current_stage_id, client_name, description, priority_score, etc.
            this.state.jobs = rawJobs.map(job => ({
                // ID fields
                id: job.TicketID || job.id || job.ticket_id,
                ticket_id: job.TicketID || job.ticket_id || job.id,
                ticket_number: job.TicketID || job.ticket_number,

                // Stage tracking
                current_stage_id: job.StageID || job.current_stage_id || job.stage_id,
                stage_name: job.StageDescription || job.stage_name || job.StageName,

                // Client info
                client_name: job.ClientName || job.client_name,
                customer: job.ClientName || job.customer || job.client_name,

                // Job details
                description: job.ShortJobDesc || job.description || job.job_description,
                job_desc: job.ShortJobDesc || job.job_desc,

                // Priority & scoring
                priority_score: job.PriorityScore || job.priority_score || 0,
                priority: job.Priority || job.priority,

                // Timing
                due_date: job.DueDate || job.due_date,
                created_date: job.CreatedDate || job.created_date || job.created_at,

                // Financial
                job_value: job.TotalValue || job.job_value || job.value || 0,

                // Keep original fields for compatibility
                ...job
            }));

            // Update cache
            this.jobsCache.clear();
            this.state.jobs.forEach(job => {
                this.jobsCache.set(job.id || job.ticket_id, job);
            });

            this.log.info(`✅ Loaded ${this.state.jobs.length} jobs`);
            return this.state.jobs;

        } catch (error) {
            this.log.error('Error loading jobs', error);
            this.state.jobs = [];
            throw error;
        }
    },

    async loadStages() {
        try {
            const url = `${this.analyticsApiBase}/stages`;
            const response = await fetch(url, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                throw new Error(`Failed to load stages: ${response.statusText}`);
            }

            const data = await response.json();
            const rawStages = Array.isArray(data) ? data : data.stages || [];

            // ✅ FIX: Map API field names (StageID, StageDescription) to expected format (id, name)
            this.state.stages = rawStages.map(stage => ({
                id: stage.StageID || stage.id,
                name: stage.StageDescription || stage.name || stage.StageName,
                count: stage.JobCount || stage.count || 0,
                avgDays: stage.AvgDaysInStage || stage.avgDays || 0,
                totalValue: stage.TotalValue || stage.totalValue || 0
            }));

            this.log.info(`✅ Loaded ${this.state.stages.length} stages`);
            return this.state.stages;

        } catch (error) {
            this.log.error('Error loading stages', error);
            this.state.stages = [];
            throw error;
        }
    },

    async refreshData() {
        this.log.info('🔄 Refreshing data...');
        try {
            await this.loadInitialData();
            this.updateLastRefreshTime();
            this.showSuccessToast('Data refreshed successfully');
        } catch (error) {
            this.log.error('Refresh failed', error);
            this.showErrorToast('Failed to refresh data');
        }
    },

    // ========================================================================
    // RENDERING METHODS
    // ========================================================================

    renderWorkboardSelector() {
        this.log.info('🔧 renderWorkboardSelector() called');
        this.log.info('   this.ui.workboardSelector:', this.ui.workboardSelector);
        this.log.info('   this.workboards:', Object.keys(this.workboards));

        if (!this.ui.workboardSelector) {
            this.log.error('❌ CRITICAL: workboardSelector element is NULL - cannot render buttons!');
            this.log.info('   Attempting to find element by ID...');
            const found = document.getElementById('workboard-selector');
            this.log.info('   document.getElementById result:', found);
            return;
        }

        this.log.info('✅ workboardSelector element found, generating buttons...');
        const workboardButtons = Object.entries(this.workboards).map(([key, config]) => {
            const isActive = key === this.state.activeWorkboard;
            return `
                <button 
                    class="workboard-btn ${isActive ? 'active' : ''}" 
                    data-workboard="${key}"
                    style="
                        padding: 10px 20px;
                        background: ${isActive ? '#00509E' : '#0d1117'};
                        border: 2px solid ${isActive ? '#00509E' : '#30363d'};
                        color: ${isActive ? '#ffffff' : '#8b949e'};
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 0.95em;
                        font-weight: 600;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                        transition: all 0.2s;
                    "
                    onmouseover="if (!this.classList.contains('active')) { this.style.borderColor='#58a6ff'; this.style.color='#58a6ff'; }"
                    onmouseout="if (!this.classList.contains('active')) { this.style.borderColor='#30363d'; this.style.color='#8b949e'; }"
                >
                    <i class="fas ${config.icon}"></i>
                    <span>${config.name}</span>
                </button>
            `;
        }).join('');

        this.log.info('   Generated HTML length:', workboardButtons.length);
        this.ui.workboardSelector.innerHTML = workboardButtons;
        this.log.info('   innerHTML set, button count:', this.ui.workboardSelector.querySelectorAll('.workboard-btn').length);

        // Add click handlers
        this.ui.workboardSelector.querySelectorAll('.workboard-btn').forEach(btn => {
            const cleanup = this.dom.on(btn, 'click', () => {
                const workboard = btn.dataset.workboard;
                this.switchWorkboard(workboard);
            });
            this.eventCleanupFns.push(cleanup);
        });

        this.log.success('✅ Workboard selector buttons rendered successfully');
    },

    switchWorkboard(workboardKey) {
        this.log.info(`🔄 Switching to workboard: ${workboardKey}`);
        this.state.activeWorkboard = workboardKey;
        this.storage.set('kanban-active-workboard', workboardKey);

        this.renderWorkboardSelector();
        this.renderKanbanBoard();
    },

    renderMetrics() {
        // Update dashboard header stats
        const totalJobs = this.state.jobs.length;
        const criticalJobs = this.state.jobs.filter(j => j.priority === 'critical').length;
        const overdueJobs = this.state.jobs.filter(j => this.isOverdue(j.due_date)).length;

        const totalJobsEl = document.getElementById('kanban-total-jobs');
        const criticalJobsEl = document.getElementById('kanban-critical-jobs');
        const overdueJobsEl = document.getElementById('kanban-overdue-jobs');

        if (totalJobsEl) totalJobsEl.textContent = totalJobs;
        if (criticalJobsEl) criticalJobsEl.textContent = criticalJobs;
        if (overdueJobsEl) overdueJobsEl.textContent = overdueJobs;
    },

    renderKanbanBoard() {
        if (!this.ui.kanbanBoard) return;

        const workboardConfig = this.workboards[this.state.activeWorkboard];
        if (!workboardConfig) {
            this.log.warn(`Workboard config not found: ${this.state.activeWorkboard}`);
            return;
        }

        const stageIds = workboardConfig.stages;
        const filteredStages = this.state.stages.filter(stage => stageIds.includes(stage.id));

        // Sort stages by defined order
        const orderedStages = this.stageOrder
            .map(stageName => filteredStages.find(s => s.name === stageName))
            .filter(Boolean);

        const columnsHtml = orderedStages.map(stage => this.renderColumn(stage)).join('');
        this.ui.kanbanBoard.innerHTML = columnsHtml;

        // Setup drag-drop
        this.setupDragAndDrop();
    },

    renderColumn(stage) {
        const stageInfo = this.stageMapping[stage.name] || {
            icon: 'fa-cube',
            color: '#6c757d',
            label: stage.name
        };

        const jobs = this.getJobsForStage(stage.id);
        const jobsHtml = jobs.map(job => this.renderJobCard(job, stage)).join('');

        return `
            <div class="inhouse-kanban-column" data-stage-id="${stage.id}" style="
                min-width: 340px;
                max-width: 340px;
                flex-shrink: 0;
                background: #0d1117;
                border-radius: 8px;
                border: 2px solid #30363d;
                display: flex;
                flex-direction: column;
                height: fit-content;
                max-height: calc(100vh - 400px);
            ">
                <div class="column-header" style="
                    padding: 15px;
                    background: linear-gradient(135deg, ${stageInfo.color} 0%, ${this.darkenColor(stageInfo.color, 0.2)} 100%);
                    border-radius: 6px 6px 0 0;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    border-bottom: 3px solid ${stageInfo.color};
                ">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <i class="fas ${stageInfo.icon}" style="font-size: 18px; color: #ffffff;"></i>
                        <span style="font-weight: 700; font-size: 15px; color: #ffffff;">${stageInfo.label}</span>
                    </div>
                    <span class="job-count-badge" style="
                        background: rgba(255,255,255,0.2);
                        color: #ffffff;
                        padding: 4px 12px;
                        border-radius: 12px;
                        font-size: 13px;
                        font-weight: 700;
                    ">${jobs.length}</span>
                </div>
                <div class="column-body" style="
                    padding: 15px;
                    flex: 1;
                    overflow-y: auto;
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                    min-height: 100px;
                ">
                    ${jobsHtml || '<div style="text-align: center; color: #6e7681; padding: 20px; font-size: 0.9em;">No jobs</div>'}
                </div>
            </div>
        `;
    },

    getJobsForStage(stageId) {
        return this.state.jobs.filter(job => {
            if (job.current_stage_id !== stageId) return false;

            // Apply filters
            const searchText = this.state.filters.search_text?.toLowerCase() || '';
            if (searchText) {
                const matchesSearch =
                    job.ticket_number?.toLowerCase().includes(searchText) ||
                    job.client_name?.toLowerCase().includes(searchText) ||
                    job.job_name?.toLowerCase().includes(searchText);
                if (!matchesSearch) return false;
            }

            const priorityFilter = this.state.filters.priority_filter;
            if (priorityFilter && priorityFilter !== 'all' && job.priority !== priorityFilter) {
                return false;
            }

            return true;
        });
    },

    renderJobCard(job, stage) {
        const isMuted = this.isCardMuted(job.id);
        const muteSettings = this.getMuteSettings(job.id);

        // Calculate styling (V4 methods with toggles)
        const borderStyle = this.getCardBorderStyle(job, muteSettings);
        const bgStyle = this.getCardBackgroundStyle(job, muteSettings);
        const bannerHtml = this.getCardBanner(job, muteSettings);

        const cardId = `job-card-${job.id}`;
        const priorityIcon = this.getPriorityIcon(job.priority);
        const daysInStage = this.calculateDaysInStage(job);

        // V9 additions - Calculate stage time info with color coding
        const stageTimeInfo = this.calculateStageTimeInfo(job, stage, daysInStage);

        // Calculate total days in system
        const daysInSystem = this.calculateDaysInSystem(job);

        // Get status badge
        const statusClass = this.getStatusBadgeClass(job.status || job.WIPStatus);
        const statusText = (job.status || job.WIPStatus || 'ACTIVE').toUpperCase();

        // V10 Enhancements - Get enhanced display elements
        const tierInfo = this.getCustomerTierInfo(job.CustomerOrderCount || 0);
        const finishingIcons = this.getFinishingIcons(job);
        const paperSpecs = this.getPaperSpecsSummary(job);
        const businessBadge = job.InvoicingBusiness ? `<span class="business-badge" title="${this.escapeHtml(job.InvoicingBusiness)}"><i class="fas fa-building"></i> ${this.escapeHtml(job.InvoicingBusiness.substring(0, 10))}</span>` : '';
        
        // Get description with fallback priority
        const description = job.ProductionNotes || job.TicketNotes || job.ShortJobDesc || job.description || job.job_name || 'No description';
        const quantity = job.QTY || job.Quantity || job.quantity || 0;
        const cost = job.Cost || job.cost || job.job_value || 0;

        return `
            <div 
                class="kanban-card ${isMuted ? 'muted-card' : ''}" 
                id="${cardId}"
                data-job-id="${job.id}" 
                draggable="true"
                onclick="window.currentKanbanModule.openJobDetails(${job.id})"
                style="
                    background: ${bgStyle};
                    border: ${borderStyle};
                    opacity: ${isMuted ? '0.5' : '1'};
                    cursor: pointer;
                "
            >
                ${bannerHtml}
                
                <div class="card-header">
                    <div class="card-header-left">
                        <div class="card-priority">
                            ${priorityIcon}
                        </div>
                        <span class="tier-badge" style="background-color: ${tierInfo.color};" title="${tierInfo.label}">
                            <i class="fas ${tierInfo.icon}"></i>
                        </span>
                    </div>
                    <div class="card-header-center">
                        <span class="status-badge ${statusClass}">
                            ${statusText}
                        </span>
                    </div>
                    <div class="card-header-right">
                        <button 
                            class="card-mute-btn" 
                            onclick="event.stopPropagation(); window.currentKanbanModule.toggleCardMute(event, ${job.id})"
                            title="${isMuted ? 'Unmute card' : 'Mute card'}"
                        >
                            <i class="fas ${isMuted ? 'fa-bell-slash' : 'fa-bell'}"></i>
                        </button>
                    </div>
                </div>
                
                <div class="card-title">${this.escapeHtml(description)}</div>
                
                <div class="card-meta">
                    <div class="card-client-name">
                        <i class="fas fa-user"></i>
                        ${this.escapeHtml(job.ClientName || job.client_name || 'Unknown Client')}
                    </div>
                    ${quantity > 0 ? `<div class="card-qty-label">Qty: ${quantity}</div>` : ''}
                    <div class="card-specs-row">
                        ${job.PaperSize ? `<span class="spec-item">${this.escapeHtml(job.PaperSize)}</span>` : ''}
                        ${job.PaperType ? `<span class="spec-item">${this.escapeHtml(job.PaperType)}</span>` : ''}
                        ${job.GSM ? `<span class="spec-item">${this.escapeHtml(job.GSM)}</span>` : ''}
                    </div>
                    ${this.getFinishingText(job) ? `<div class="card-finish-text" style="font-size: 11px; color: #9ca3af;">${this.getFinishingText(job)}</div>` : ''}
                </div>
                
                <div class="card-timing-row">
                    <span class="timing-item">
                        <i class="fas fa-hourglass-half"></i> ${daysInSystem}d in system
                    </span>
                    <span class="timing-item ${stageTimeInfo.cssClass}">
                        <i class="fas fa-clock"></i> ${stageTimeInfo.display}
                    </span>
                </div>
                
                <div class="card-footer">
                    <div class="card-tags">
                        <span class="card-tag">
                            <i class="fas fa-ticket-alt"></i> ${job.TicketID || job.ticket_number || job.id}
                        </span>
                        ${job.OrderID ? `
                            <span class="card-tag">
                                <i class="fas fa-file-invoice"></i> ${job.OrderID}
                            </span>
                        ` : ''}
                        ${cost > 0 ? `
                            <span class="card-tag">
                                <i class="fas fa-dollar-sign"></i> ${this.formatCurrency(cost)}
                            </span>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    },

    // ========================================================================
    // V9 CARD HELPER METHODS
    // ========================================================================

    calculateDaysInSystem(job) {
        // Try multiple date fields from database
        const dateField = job.OrderDate || job.DateCreated || job.created_at || job.CreatedDate;
        if (!dateField) return 0;
        
        const created = new Date(dateField);
        const now = new Date();
        const diffTime = Math.abs(now - created);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays;
    },

    calculateStageTimeInfo(job, stage, daysInStage) {
        // Get stage entry time from job data
        const stageEntryTime = job.stage_entered_at || job.StageEnteredAt || job.LastUpdated;
        
        if (stageEntryTime) {
            const entered = new Date(stageEntryTime);
            const now = new Date();
            const diffMs = now - entered;
            const hours = Math.floor(diffMs / (1000 * 60 * 60));
            const days = Math.floor(hours / 24);
            const remainingHours = hours % 24;
            
            let cssClass = 'stage-normal';
            let display = '';
            
            if (days > 0) {
                display = `${days}d ${remainingHours}h`;
                if (days > 7) cssClass = 'stage-overdue';
                else if (days > 3) cssClass = 'stage-warning';
            } else if (hours > 0) {
                display = `${hours}h`;
                if (hours > 48) cssClass = 'stage-warning';
            } else {
                const minutes = Math.floor(diffMs / (1000 * 60));
                display = `${minutes}m`;
            }
            
            return { cssClass, display };
        }
        
        // Fallback to old calculation
        const stageName = stage?.name || 'stage';
        let cssClass = 'stage-normal';
        let display = `${daysInStage}d`;

        if (daysInStage > 7) {
            cssClass = 'stage-overdue';  // Red - over 7 days
        } else if (daysInStage > 3) {
            cssClass = 'stage-warning';   // Yellow - 4-7 days
        }
        // else 'stage-normal' (gray - 0-3 days)

        return { display, cssClass };
    },

    /**
     * Get customer tier information based on order count
     * @param {number} orderCount - Number of orders in last 12 months
     * @returns {Object} - Tier info with color, icon, and label
     */
    getCustomerTierInfo(orderCount) {
        if (orderCount >= 50) {
            return {
                color: '#8b5cf6',  // Purple
                icon: 'fa-crown',
                label: 'VIP Customer'
            };
        } else if (orderCount >= 20) {
            return {
                color: '#f59e0b',  // Amber
                icon: 'fa-star',
                label: 'Premium Customer'
            };
        } else if (orderCount >= 5) {
            return {
                color: '#10b981',  // Green
                icon: 'fa-user',
                label: 'Regular Customer'
            };
        } else {
            return {
                color: '#6b7280',  // Gray
                icon: 'fa-user-circle',
                label: 'New Customer'
            };
        }
    },

    /**
     * Get finishing options icons for card display
     * @param {Object} job - Job object
     * @returns {string} - HTML string with finishing icons
     */
    getFinishingIcons(job) {
        const icons = [];
        
        if (job.CelloYes || job.FrontCelloGloss || job.FrontCelloMatt || job.BackCelloGloss || job.BackCelloMatt) {
            icons.push('<span class="finishing-icon" title="Cellophane Finish"><i class="fas fa-star"></i></span>');
        }
        
        if (job.FoldYes || job.FoldDesc) {
            icons.push('<span class="finishing-icon" title="Folding"><i class="fas fa-folder"></i></span>');
        }
        
        if (job.StitchYes) {
            icons.push('<span class="finishing-icon" title="Stitching"><i class="fas fa-th"></i></span>');
        }
        
        if (job.RingBind) {
            icons.push('<span class="finishing-icon" title="Ring Binding"><i class="fas fa-ring"></i></span>');
        }
        
        if (job.PerfectBind) {
            icons.push('<span class="finishing-icon" title="Perfect Binding"><i class="fas fa-book"></i></span>');
        }
        
        return icons.join('');
    },

    /**
     * Get paper specifications summary for card display
     * @param {Object} job - Job object
     * @returns {string} - Formatted paper specs string
     */
    getPaperSpecsSummary(job) {
        const specs = [];
        
        if (job.PaperType) {
            specs.push(job.PaperType);
        }
        
        if (job.GSM) {
            specs.push(job.GSM);
        }
        
        if (job.PaperSize && specs.length === 0) {
            specs.push(job.PaperSize);
        }
        
        return specs.length > 0 ? `| ${specs.join(' • ')}` : '';
    },

    /**
     * Get finishing options as readable text
     * @param {Object} job - Job object
     * @returns {string} - Formatted finishing text
     */
    getFinishingText(job) {
        const finishes = [];
        
        if (job.CelloYes || job.FrontCelloGloss || job.FrontCelloMatt || job.BackCelloGloss || job.BackCelloMatt) {
            const celloTypes = [];
            if (job.FrontCelloGloss) celloTypes.push('Front Gloss');
            if (job.FrontCelloMatt) celloTypes.push('Front Matt');
            if (job.BackCelloGloss) celloTypes.push('Back Gloss');
            if (job.BackCelloMatt) celloTypes.push('Back Matt');
            finishes.push(celloTypes.length > 0 ? `Cello: ${celloTypes.join(', ')}` : 'Cello');
        }
        
        if (job.FoldYes || job.FoldDesc) {
            finishes.push(job.FoldDesc ? `Fold: ${job.FoldDesc}` : 'Folding');
        }
        
        if (job.StitchYes) {
            finishes.push('Stitching');
        }
        
        if (job.RingBind) {
            finishes.push('Ring Binding');
        }
        
        if (job.PerfectBind) {
            finishes.push('Perfect Binding');
        }
        
        return finishes.join(' | ');
    },

    getStatusBadgeClass(status) {
        if (!status) return 'status-active';
        const statusLower = status.toLowerCase();
        if (statusLower.includes('delayed')) return 'status-delayed';
        if (statusLower.includes('risk') || statusLower.includes('warning')) return 'status-warning';
        if (statusLower.includes('on track') || statusLower.includes('complete')) return 'status-success';
        return 'status-active';
    },

    // ========================================================================
    // CARD STYLING METHODS
    // ========================================================================

    getCardBorderStyle(job, muteSettings = {}) {
        // Ensure muteSettings is an object
        const settings = muteSettings || {};
        if (!this.colorToggles.showBorderColors || settings.muteBorder) {
            return '2px solid #30363d';
        }

        const colors = this.getColorSettings();

        // Priority border
        const priority = (job.priority || 'normal').toLowerCase();
        const priorityConfig = colors.priority[priority] || colors.priority.normal;

        // Due date override
        if (job.due_date) {
            const daysUntilDue = this.getDaysUntilDue(job.due_date);
            if (daysUntilDue <= 0) {
                const overdueConfig = colors.dueDate.overdue;
                if (overdueConfig.pulse) {
                    return `${overdueConfig.borderWidth}px ${overdueConfig.borderType} ${overdueConfig.borderColor}`;
                }
            } else if (daysUntilDue <= 1) {
                const dueTodayConfig = colors.dueDate.dueToday;
                return `${dueTodayConfig.borderWidth}px ${dueTodayConfig.borderType} ${dueTodayConfig.borderColor}`;
            } else if (daysUntilDue <= 2) {
                const dueSoonConfig = colors.dueDate.dueSoon;
                return `${dueSoonConfig.borderWidth}px ${dueSoonConfig.borderType} ${dueSoonConfig.borderColor}`;
            }
        }

        return `${priorityConfig.borderWidth}px solid ${priorityConfig.borderColor}`;
    },

    getCardBackgroundStyle(job, muteSettings = {}) {
        // Ensure muteSettings is an object
        const settings = muteSettings || {};
        if (!this.colorToggles.showBackgroundColors || settings.muteBackground) {
            return '#161b22';
        }

        const colors = this.getColorSettings();

        if (job.due_date) {
            const daysUntilDue = this.getDaysUntilDue(job.due_date);
            if (daysUntilDue <= 0) {
                return colors.dueDate.overdue.backgroundColor;
            } else if (daysUntilDue <= 1) {
                return colors.dueDate.dueToday.backgroundColor;
            } else if (daysUntilDue <= 2) {
                return colors.dueDate.dueSoon.backgroundColor;
            }
        }

        return '#161b22';
    },

    getCardBanner(job, muteSettings = {}) {
        // Ensure muteSettings is an object
        const settings = muteSettings || {};
        if (!this.colorToggles.showBannerColors || settings.muteBanner) {
            return '';
        }

        const colors = this.getColorSettings();

        if (job.due_date) {
            const daysUntilDue = this.getDaysUntilDue(job.due_date);
            if (daysUntilDue <= 0) {
                const banner = colors.banners.overdue;
                return `
                    <div style="
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        background: ${banner.backgroundColor};
                        color: ${banner.textColor};
                        padding: 4px 8px;
                        font-size: 11px;
                        font-weight: 700;
                        text-align: center;
                        border-radius: 6px 6px 0 0;
                        margin: -12px -12px 8px -12px;
                    ">
                        <i class="fas fa-exclamation-triangle"></i> OVERDUE
                    </div>
                `;
            } else if (daysUntilDue <= 1) {
                const banner = colors.banners.dueToday;
                return `
                    <div style="
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        background: ${banner.backgroundColor};
                        color: ${banner.textColor};
                        padding: 4px 8px;
                        font-size: 11px;
                        font-weight: 700;
                        text-align: center;
                        border-radius: 6px 6px 0 0;
                        margin: -12px -12px 8px -12px;
                    ">
                        <i class="fas fa-clock"></i> DUE ${daysUntilDue === 0 ? 'TODAY' : 'TOMORROW'}
                    </div>
                `;
            }
        }

        return '';
    },

    // ========================================================================
    // COLOR SETTINGS MANAGEMENT
    // ========================================================================

    getDefaultColorSettings() {
        return {
            priority: {
                critical: { borderColor: '#ef4444', borderWidth: 4 },
                urgent: { borderColor: '#f97316', borderWidth: 3 },
                high: { borderColor: '#eab308', borderWidth: 3 },
                normal: { borderColor: '#3b82f6', borderWidth: 2 },
                low: { borderColor: '#6b7280', borderWidth: 2 }
            },
            dueDate: {
                overdue: {
                    borderColor: '#dc2626',
                    borderType: 'solid',
                    borderWidth: 4,
                    pulse: true,
                    backgroundColor: 'rgba(220, 38, 38, 0.1)'
                },
                dueToday: {
                    borderColor: '#ea580c',
                    borderType: 'solid',
                    borderWidth: 3,
                    pulse: false,
                    backgroundColor: 'rgba(234, 88, 12, 0.1)'
                },
                dueSoon: {
                    borderColor: '#f59e0b',
                    borderType: 'dashed',
                    borderWidth: 2,
                    pulse: false,
                    backgroundColor: 'rgba(245, 158, 11, 0.05)'
                }
            },
            banners: {
                overdue: {
                    backgroundColor: '#7f1d1d',
                    textColor: '#fecaca'
                },
                dueToday: {
                    backgroundColor: '#7c2d12',
                    textColor: '#fed7aa'
                }
            }
        };
    },

    loadColorSettings() {
        const saved = this.storage.get('kanban-color-settings');
        this.colorSettings = saved || this.getDefaultColorSettings();
    },

    getColorSettings() {
        return this.colorSettings || this.getDefaultColorSettings();
    },

    loadColorToggles() {
        const saved = this.storage.get('kanban-color-toggles');
        if (saved) {
            this.colorToggles = saved;
        }
    },

    saveColorSettings() {
        this.storage.set('kanban-color-settings', this.colorSettings);
    },

    saveColorToggles() {
        this.storage.set('kanban-color-toggles', this.colorToggles);
    },

    // ========================================================================
    // ADVANCED COLOR SETTINGS UI
    // ========================================================================

    renderColorSettingsTables() {
        this.renderPrioritySettingsTable();
        this.renderDueDateSettingsTable();
        this.renderBannerSettingsTable();
    },

    renderPrioritySettingsTable() {
        const tableBody = document.getElementById('priority-settings-table');
        if (!tableBody) return;

        const colors = this.getColorSettings();
        const priorities = ['critical', 'urgent', 'high', 'normal', 'low'];

        tableBody.innerHTML = priorities.map(priority => {
            const config = colors.priority[priority];
            return `
                <tr style="border-bottom: 1px solid #21262d;">
                    <td style="padding: 12px; color: #c9d1d9; text-transform: capitalize; font-weight: 600;">
                        ${priority}
                    </td>
                    <td style="padding: 12px;">
                        <input 
                            type="color" 
                            value="${config.borderColor}" 
                            data-priority="${priority}"
                            data-property="borderColor"
                            class="priority-color-input"
                            style="width: 60px; height: 30px; border: 1px solid #30363d; border-radius: 4px; cursor: pointer;"
                        >
                    </td>
                    <td style="padding: 12px;">
                        <input 
                            type="number" 
                            value="${config.borderWidth}" 
                            min="1" 
                            max="8"
                            data-priority="${priority}"
                            data-property="borderWidth"
                            class="priority-width-input"
                            style="width: 60px; padding: 6px; background: #0d1117; border: 1px solid #30363d; border-radius: 4px; color: #f0f6fc;"
                        >
                    </td>
                    <td style="padding: 12px;">
                        <div style="
                            width: 100px;
                            height: 30px;
                            border: ${config.borderWidth}px solid ${config.borderColor};
                            border-radius: 4px;
                            background: #161b22;
                        "></div>
                    </td>
                </tr>
            `;
        }).join('');

        this.attachPriorityPreviewListeners();
    },

    renderDueDateSettingsTable() {
        const tableBody = document.getElementById('duedate-settings-table');
        if (!tableBody) return;

        const colors = this.getColorSettings();
        const states = [
            { key: 'overdue', label: 'Overdue' },
            { key: 'dueToday', label: 'Due Today/Tomorrow' },
            { key: 'dueSoon', label: 'Due Soon (2+ days)' }
        ];

        tableBody.innerHTML = states.map(({ key, label }) => {
            const config = colors.dueDate[key];
            return `
                <tr style="border-bottom: 1px solid #21262d;">
                    <td style="padding: 10px; color: #c9d1d9; font-weight: 600;">${label}</td>
                    <td style="padding: 10px;">
                        <input 
                            type="color" 
                            value="${config.borderColor}" 
                            data-duedate="${key}"
                            data-property="borderColor"
                            class="duedate-color-input"
                            style="width: 60px; height: 28px; border: 1px solid #30363d; border-radius: 4px; cursor: pointer;"
                        >
                    </td>
                    <td style="padding: 10px;">
                        <select 
                            data-duedate="${key}"
                            data-property="borderType"
                            class="duedate-type-input"
                            style="padding: 6px; background: #0d1117; border: 1px solid #30363d; border-radius: 4px; color: #f0f6fc;"
                        >
                            <option value="solid" ${config.borderType === 'solid' ? 'selected' : ''}>Solid</option>
                            <option value="dashed" ${config.borderType === 'dashed' ? 'selected' : ''}>Dashed</option>
                            <option value="dotted" ${config.borderType === 'dotted' ? 'selected' : ''}>Dotted</option>
                        </select>
                    </td>
                    <td style="padding: 10px;">
                        <input 
                            type="number" 
                            value="${config.borderWidth}" 
                            min="1" 
                            max="8"
                            data-duedate="${key}"
                            data-property="borderWidth"
                            class="duedate-width-input"
                            style="width: 60px; padding: 6px; background: #0d1117; border: 1px solid #30363d; border-radius: 4px; color: #f0f6fc;"
                        >
                    </td>
                    <td style="padding: 10px; text-align: center;">
                        <input 
                            type="checkbox" 
                            ${config.pulse ? 'checked' : ''}
                            data-duedate="${key}"
                            data-property="pulse"
                            class="duedate-pulse-input"
                            style="width: 18px; height: 18px; cursor: pointer;"
                        >
                    </td>
                    <td style="padding: 10px;">
                        <input 
                            type="color" 
                            value="${this.rgbaToHex(config.backgroundColor)}" 
                            data-duedate="${key}"
                            data-property="backgroundColor"
                            class="duedate-bgcolor-input"
                            style="width: 60px; height: 28px; border: 1px solid #30363d; border-radius: 4px; cursor: pointer;"
                        >
                    </td>
                    <td style="padding: 10px;">
                        <div style="
                            width: 100px;
                            height: 30px;
                            border: ${config.borderWidth}px ${config.borderType} ${config.borderColor};
                            border-radius: 4px;
                            background: ${config.backgroundColor};
                        "></div>
                    </td>
                </tr>
            `;
        }).join('');

        this.attachDueDatePreviewListeners();
    },

    renderBannerSettingsTable() {
        const tableBody = document.getElementById('banner-settings-table');
        if (!tableBody) return;

        const colors = this.getColorSettings();
        const states = [
            { key: 'overdue', label: 'Overdue Banner' },
            { key: 'dueToday', label: 'Due Today Banner' }
        ];

        tableBody.innerHTML = states.map(({ key, label }) => {
            const config = colors.banners[key];
            return `
                <tr style="border-bottom: 1px solid #21262d;">
                    <td style="padding: 12px; color: #c9d1d9; font-weight: 600;">${label}</td>
                    <td style="padding: 12px;">
                        <input 
                            type="color" 
                            value="${config.backgroundColor}" 
                            data-banner="${key}"
                            data-property="backgroundColor"
                            class="banner-bgcolor-input"
                            style="width: 60px; height: 30px; border: 1px solid #30363d; border-radius: 4px; cursor: pointer;"
                        >
                    </td>
                    <td style="padding: 12px;">
                        <input 
                            type="color" 
                            value="${config.textColor}" 
                            data-banner="${key}"
                            data-property="textColor"
                            class="banner-textcolor-input"
                            style="width: 60px; height: 30px; border: 1px solid #30363d; border-radius: 4px; cursor: pointer;"
                        >
                    </td>
                    <td style="padding: 12px;">
                        <div style="
                            padding: 8px 16px;
                            background: ${config.backgroundColor};
                            color: ${config.textColor};
                            border-radius: 4px;
                            font-weight: 700;
                            font-size: 12px;
                            text-align: center;
                        ">
                            ${key === 'overdue' ? 'OVERDUE' : 'DUE TODAY'}
                        </div>
                    </td>
                </tr>
            `;
        }).join('');

        this.attachBannerPreviewListeners();
    },

    // ========================================================================
    // COLOR PREVIEW LISTENERS
    // ========================================================================

    attachPriorityPreviewListeners() {
        document.querySelectorAll('.priority-color-input, .priority-width-input').forEach(input => {
            const cleanup = this.dom.on(input, 'input', (e) => {
                const priority = e.target.dataset.priority;
                const property = e.target.dataset.property;
                const row = e.target.closest('tr');
                const preview = row.querySelector('div[style*="border"]');

                if (property === 'borderColor') {
                    const width = row.querySelector('.priority-width-input').value;
                    preview.style.border = `${width}px solid ${e.target.value}`;
                } else if (property === 'borderWidth') {
                    const color = row.querySelector('.priority-color-input').value;
                    preview.style.border = `${e.target.value}px solid ${color}`;
                }
            });
            this.eventCleanupFns.push(cleanup);
        });
    },

    attachDueDatePreviewListeners() {
        document.querySelectorAll('.duedate-color-input, .duedate-width-input, .duedate-type-input, .duedate-bgcolor-input').forEach(input => {
            const cleanup = this.dom.on(input, 'input', (e) => {
                const key = e.target.dataset.duedate;
                const row = e.target.closest('tr');
                const preview = row.querySelector('div[style*="border"]');

                const color = row.querySelector('.duedate-color-input').value;
                const width = row.querySelector('.duedate-width-input').value;
                const type = row.querySelector('.duedate-type-input').value;
                const bgcolor = row.querySelector('.duedate-bgcolor-input').value;

                preview.style.border = `${width}px ${type} ${color}`;
                preview.style.background = bgcolor;
            });
            this.eventCleanupFns.push(cleanup);
        });
    },

    attachBannerPreviewListeners() {
        document.querySelectorAll('.banner-bgcolor-input, .banner-textcolor-input').forEach(input => {
            const cleanup = this.dom.on(input, 'input', (e) => {
                const key = e.target.dataset.banner;
                const row = e.target.closest('tr');
                const preview = row.querySelector('div[style*="padding"]');

                const bgcolor = row.querySelector('.banner-bgcolor-input').value;
                const textcolor = row.querySelector('.banner-textcolor-input').value;

                preview.style.background = bgcolor;
                preview.style.color = textcolor;
            });
            this.eventCleanupFns.push(cleanup);
        });
    },

    // ========================================================================
    // ADVANCED COLOR ACTIONS
    // ========================================================================

    toggleAdvancedColorSettings() {
        const content = document.getElementById('advanced-color-settings-content');
        const icon = document.getElementById('advanced-color-toggle-icon');

        if (!content || !icon) {
            this.log.error('❌ Advanced color settings elements not found');
            return;
        }

        const isHidden = content.style.display === 'none';
        content.style.display = isHidden ? 'block' : 'none';
        icon.className = isHidden ? 'fas fa-chevron-down' : 'fas fa-chevron-right';
        icon.style.transform = isHidden ? 'rotate(0deg)' : 'rotate(0deg)';

        this.log.info(`🎨 Advanced color settings ${isHidden ? 'expanded' : 'collapsed'}`);
    },

    testAdvancedColorSettings() {
        this.log.info('🎨 Testing color settings...');
        this.applyColorSettingsFromUI();
        this.renderKanbanBoard();
        this.showSuccessToast('Color settings applied (test mode)');
    },

    saveAdvancedColorSettings() {
        this.log.info('💾 Saving color settings...');
        this.applyColorSettingsFromUI();
        this.saveColorSettings();
        this.renderKanbanBoard();
        this.showSuccessToast('Color settings saved successfully');
    },

    resetAdvancedColorSettings() {
        this.log.info('🔄 Resetting color settings...');
        this.colorSettings = this.getDefaultColorSettings();
        this.saveColorSettings();
        this.renderColorSettingsTables();
        this.renderKanbanBoard();
        this.showSuccessToast('Color settings reset to defaults');
    },

    applyColorSettingsFromUI() {
        const colors = this.getColorSettings();

        // Priority colors
        document.querySelectorAll('.priority-color-input').forEach(input => {
            const priority = input.dataset.priority;
            colors.priority[priority].borderColor = input.value;
        });
        document.querySelectorAll('.priority-width-input').forEach(input => {
            const priority = input.dataset.priority;
            colors.priority[priority].borderWidth = parseInt(input.value);
        });

        // Due date colors
        document.querySelectorAll('.duedate-color-input').forEach(input => {
            const key = input.dataset.duedate;
            colors.dueDate[key].borderColor = input.value;
        });
        document.querySelectorAll('.duedate-width-input').forEach(input => {
            const key = input.dataset.duedate;
            colors.dueDate[key].borderWidth = parseInt(input.value);
        });
        document.querySelectorAll('.duedate-type-input').forEach(input => {
            const key = input.dataset.duedate;
            colors.dueDate[key].borderType = input.value;
        });
        document.querySelectorAll('.duedate-pulse-input').forEach(input => {
            const key = input.dataset.duedate;
            colors.dueDate[key].pulse = input.checked;
        });
        document.querySelectorAll('.duedate-bgcolor-input').forEach(input => {
            const key = input.dataset.duedate;
            colors.dueDate[key].backgroundColor = input.value;
        });

        // Banners
        document.querySelectorAll('.banner-bgcolor-input').forEach(input => {
            const key = input.dataset.banner;
            colors.banners[key].backgroundColor = input.value;
        });
        document.querySelectorAll('.banner-textcolor-input').forEach(input => {
            const key = input.dataset.banner;
            colors.banners[key].textColor = input.value;
        });

        this.colorSettings = colors;
    },

    // ========================================================================
    // CARD MUTE MANAGEMENT
    // ========================================================================

    loadMutedCards() {
        const saved = this.storage.get('kanban-muted-cards');
        if (saved && typeof saved === 'object') {
            this.mutedCards = new Map(Object.entries(saved));
        }
    },

    saveMutedCards() {
        const obj = Object.fromEntries(this.mutedCards);
        this.storage.set('kanban-muted-cards', obj);
    },

    getMuteSettings(jobId) {
        return this.mutedCards.get(String(jobId)) || {};
    },

    setMuteSettings(jobId, settings) {
        this.mutedCards.set(String(jobId), settings);
        this.saveMutedCards();
    },

    clearMuteSettings(jobId) {
        this.mutedCards.delete(String(jobId));
        this.saveMutedCards();
    },

    clearAllMutedCards() {
        if (this.mutedCards.size === 0) {
            this.showInfoToast('No muted cards to clear');
            return;
        }

        const count = this.mutedCards.size;
        this.mutedCards.clear();
        this.saveMutedCards();
        this.updateMutedCardCount();
        this.renderKanbanBoard();
        this.showSuccessToast(`Cleared ${count} muted card${count !== 1 ? 's' : ''}`);
    },

    updateMutedCardCount() {
        const countElements = document.querySelectorAll('.muted-cards-count');
        countElements.forEach(el => {
            el.textContent = this.mutedCards.size;
        });
    },

    isCardMuted(jobId) {
        return this.mutedCards.has(String(jobId));
    },

    toggleCardMute(event, jobId) {
        event.stopPropagation();

        const isMuted = this.isCardMuted(jobId);

        if (isMuted) {
            this.clearMuteSettings(jobId);
            this.showSuccessToast('Card unmuted');
        } else {
            // Show mute dialog
            this.showMuteDialog(jobId);
        }

        this.updateMutedCardCount();
        this.renderKanbanBoard();
    },

    showMuteDialog(jobId) {
        const job = this.jobsCache.get(jobId);
        if (!job) return;

        const dialogHtml = `
            <div id="mute-dialog-overlay" style="
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
            ">
                <div style="
                    background: #161b22;
                    border: 2px solid #30363d;
                    border-radius: 12px;
                    padding: 24px;
                    max-width: 500px;
                    width: 90%;
                ">
                    <h3 style="margin: 0 0 16px 0; color: #f0f6fc; font-size: 18px; font-weight: 700;">
                        Mute Card Options
                    </h3>
                    <p style="margin: 0 0 20px 0; color: #8b949e; font-size: 14px;">
                        Card: <strong style="color: #58a6ff;">${job.ticket_number}</strong>
                    </p>
                    
                    <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px;">
                        <label style="display: flex; align-items: center; gap: 10px; color: #c9d1d9; cursor: pointer;">
                            <input type="checkbox" id="mute-border" checked style="width: 18px; height: 18px;">
                            <span>Mute border colors</span>
                        </label>
                        <label style="display: flex; align-items: center; gap: 10px; color: #c9d1d9; cursor: pointer;">
                            <input type="checkbox" id="mute-background" checked style="width: 18px; height: 18px;">
                            <span>Mute background colors</span>
                        </label>
                        <label style="display: flex; align-items: center; gap: 10px; color: #c9d1d9; cursor: pointer;">
                            <input type="checkbox" id="mute-banner" checked style="width: 18px; height: 18px;">
                            <span>Mute urgency banners</span>
                        </label>
                    </div>
                    
                    <div style="display: flex; gap: 10px; justify-content: flex-end;">
                        <button onclick="document.getElementById('mute-dialog-overlay').remove()" style="
                            padding: 8px 16px;
                            background: #21262d;
                            border: 1px solid #30363d;
                            color: #c9d1d9;
                            border-radius: 6px;
                            cursor: pointer;
                            font-size: 14px;
                            font-weight: 600;
                        ">Cancel</button>
                        <button onclick="window.currentKanbanModule.applyMuteSettings(${jobId})" style="
                            padding: 8px 16px;
                            background: #238636;
                            border: none;
                            color: white;
                            border-radius: 6px;
                            cursor: pointer;
                            font-size: 14px;
                            font-weight: 600;
                        ">Apply</button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', dialogHtml);
    },

    applyMuteSettings(jobId) {
        const muteBorder = document.getElementById('mute-border').checked;
        const muteBackground = document.getElementById('mute-background').checked;
        const muteBanner = document.getElementById('mute-banner').checked;

        this.setMuteSettings(jobId, {
            muteBorder,
            muteBackground,
            muteBanner,
            timestamp: Date.now()
        });

        document.getElementById('mute-dialog-overlay').remove();
        this.updateMutedCardCount();
        this.renderKanbanBoard();
        this.showSuccessToast('Card muted successfully');
    },

    showMutedCardsOnly() {
        if (this.mutedCards.size === 0) {
            this.showInfoToast('No muted cards');
            return;
        }

        const mutedJobIds = Array.from(this.mutedCards.keys()).map(id => parseInt(id));
        const mutedJobs = this.state.jobs.filter(job => mutedJobIds.includes(job.id));

        this.log.info(`Showing ${mutedJobs.length} muted cards`);

        // Temporarily override jobs
        const originalJobs = [...this.state.jobs];
        this.state.jobs = mutedJobs;
        this.renderKanbanBoard();

        // Add restore button
        const board = this.ui.kanbanBoard;
        if (board) {
            const restoreBtn = document.createElement('div');
            restoreBtn.innerHTML = `
                <div style="
                    position: fixed;
                    bottom: 30px;
                    right: 30px;
                    background: #1f6feb;
                    color: white;
                    padding: 12px 24px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    cursor: pointer;
                    font-weight: 600;
                    z-index: 1000;
                " onclick="window.currentKanbanModule.restoreAllCards()">
                    <i class="fas fa-times"></i> Show All Cards
                </div>
            `;
            board.appendChild(restoreBtn);
        }

        this._originalJobs = originalJobs;
    },

    restoreAllCards() {
        if (this._originalJobs) {
            this.state.jobs = this._originalJobs;
            delete this._originalJobs;
            this.renderKanbanBoard();
            this.showSuccessToast('Showing all cards');
        }
    },

    exportMutedCards() {
        if (this.mutedCards.size === 0) {
            this.showInfoToast('No muted cards to export');
            return;
        }

        const mutedJobIds = Array.from(this.mutedCards.keys()).map(id => parseInt(id));
        const mutedJobs = this.state.jobs.filter(job => mutedJobIds.includes(job.id));

        const csv = [
            ['Ticket', 'Client', 'Job Name', 'Priority', 'Stage', 'Due Date', 'Mute Settings'].join(','),
            ...mutedJobs.map(job => {
                const settings = this.getMuteSettings(job.id);
                const muteInfo = `Border:${settings.muteBorder} BG:${settings.muteBackground} Banner:${settings.muteBanner}`;
                return [
                    job.ticket_number,
                    job.client_name,
                    job.job_name,
                    job.priority,
                    job.current_stage_name,
                    job.due_date || 'N/A',
                    muteInfo
                ].map(v => `"${v}"`).join(',');
            })
        ].join('\n');

        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `muted-cards-${Date.now()}.csv`;
        a.click();
        URL.revokeObjectURL(url);

        this.showSuccessToast(`Exported ${mutedJobs.length} muted cards`);
    },

    // ========================================================================
    // DRAG & DROP SYSTEM
    // ========================================================================

    setupDragAndDrop() {
        // Draggable cards
        document.querySelectorAll('.job-card').forEach(card => {
            const dragStartCleanup = this.dom.on(card, 'dragstart', (e) => {
                const jobId = parseInt(e.target.dataset.jobId);
                this.draggedJob = this.jobsCache.get(jobId);
                e.dataTransfer.effectAllowed = 'move';
                e.target.style.opacity = '0.4';
            });

            const dragEndCleanup = this.dom.on(card, 'dragend', (e) => {
                e.target.style.opacity = '1';
                this.draggedJob = null;
            });

            this.eventCleanupFns.push(dragStartCleanup, dragEndCleanup);
        });

        // Drop zones
        document.querySelectorAll('.inhouse-kanban-column').forEach(column => {
            const dragOverCleanup = this.dom.on(column, 'dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                column.style.background = 'rgba(88, 166, 255, 0.1)';
                column.style.borderColor = '#58a6ff';
            });

            const dragLeaveCleanup = this.dom.on(column, 'dragleave', (e) => {
                column.style.background = '';
                column.style.borderColor = '';
            });

            const dropCleanup = this.dom.on(column, 'drop', async (e) => {
                e.preventDefault();
                column.style.background = '';
                column.style.borderColor = '';

                if (!this.draggedJob) return;

                const targetStageId = parseInt(column.dataset.stageId);
                await this.moveJobToStage(this.draggedJob, targetStageId);
            });

            this.eventCleanupFns.push(dragOverCleanup, dragLeaveCleanup, dropCleanup);
        });
    },

    async moveJobToStage(job, newStageId) {
        if (job.current_stage_id === newStageId) return;

        const oldStage = this.state.stages.find(s => s.id === job.current_stage_id);
        const newStage = this.state.stages.find(s => s.id === newStageId);

        this.log.info(`Moving job ${job.id} from ${oldStage?.name} to ${newStage?.name}`);

        try {
            const response = await fetch(`${this.analyticsApiBase}/jobs/${job.id}/stage`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ stage_id: newStageId })
            });

            if (!response.ok) {
                throw new Error('Failed to update job stage');
            }

            // Update local state
            job.current_stage_id = newStageId;
            job.current_stage_name = newStage?.name;

            // Log production change
            await this.logProductionChange(job.id, oldStage?.name, newStage?.name);

            // Re-render
            this.renderKanbanBoard();
            this.showSuccessToast(`Moved to ${newStage?.name}`);

        } catch (error) {
            this.log.error('Failed to move job', error);
            this.showErrorToast('Failed to move job');
        }
    },

    async logProductionChange(jobId, fromStage, toStage) {
        try {
            await fetch(`${this.analyticsApiBase}/production-log`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    job_id: jobId,
                    from_stage: fromStage,
                    to_stage: toStage,
                    changed_by: 'User',
                    timestamp: new Date().toISOString()
                })
            });
        } catch (error) {
            this.log.warn('Failed to log production change', error);
        }
    },

    // ========================================================================
    // JOB DETAILS MODAL
    // ========================================================================

    openJobDetails(jobId) {
        const job = this.jobsCache.get(jobId);
        if (!job) {
            this.showErrorToast('Job not found');
            return;
        }

        const stage = this.state.stages.find(s => s.id === job.current_stage_id);
        const stageInfo = this.stageMapping[stage?.name] || { icon: 'fa-cube', color: '#6c757d' };
        
        // Get tier info and priority
        const tierInfo = this.getCustomerTierInfo(job.CustomerOrderCount || 0);
        const priorityIcon = this.getPriorityIcon(job.Priority || 'Normal');

        const modalHtml = `
            <div class="modal-overlay" id="job-details-modal">
                <div class="kanban-job-modal" id="draggable-modal">
                    <div class="kanban-modal-header" id="modal-header-drag">
                        <div class="kanban-modal-title">
                            <i class="fas fa-clipboard-list"></i>
                            <span>Job Details - Ticket #${job.TicketID || job.ticket_number}</span>
                        </div>
                        <button class="kanban-modal-close-btn" onclick="document.getElementById('job-details-modal').remove();">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>

                    <div class="kanban-modal-body" id="modal-body-scroll">
                        <!-- JOB STATUS SECTION -->
                        <div class="kanban-content-section">
                            <div class="kanban-section-title">
                                <i class="fas fa-tags"></i>
                                <span>Job Status</span>
                            </div>
                            <div class="kanban-section-content">
                                <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                                    <span class="badge badge-priority" style="background-color: ${job.PriorityColorHex || '#6c757d'}; padding: 10px 16px; border-radius: 6px; font-size: 14px; font-weight: 700; color: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                                        ${priorityIcon} ${job.Priority || 'Normal'} Priority ${job.AIPriorityScore ? `(Score: ${job.AIPriorityScore})` : ''}
                                    </span>
                                    <span class="badge badge-tier" style="background-color: ${tierInfo.color}; padding: 10px 16px; border-radius: 6px; font-size: 14px; font-weight: 700; color: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                                        <i class="fas ${tierInfo.icon}"></i> ${tierInfo.label} Customer
                                    </span>
                                    ${job.WIPStatus ? `
                                    <span class="badge badge-wip" style="background-color: ${job.WIPColorHex || '#6c757d'}; padding: 10px 16px; border-radius: 6px; font-size: 14px; font-weight: 700; color: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                                        ${job.WIPStatus}
                                    </span>
                                    ` : ''}
                                </div>
                            </div>
                        </div>

                        <!-- CLIENT INFORMATION SECTION -->
                        <div class="kanban-content-section">
                            <div class="kanban-section-title">
                                <i class="fas fa-building"></i>
                                <span>Client Information</span>
                            </div>
                            <div class="kanban-section-content">
                                <div class="kanban-detail-grid">
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label">Client Name</span>
                                        <span class="kanban-detail-value">${this.escapeHtml(job.ClientName || job.client_name || 'Unknown')}</span>
                                    </div>
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label">Order ID</span>
                                        <span class="kanban-detail-value">${job.OrderID || 'N/A'}</span>
                                    </div>
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label">Order Date</span>
                                        <span class="kanban-detail-value">${job.OrderDate ? this.formatDate(job.OrderDate) : 'N/A'}</span>
                                    </div>
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label">Business Division</span>
                                        <span class="kanban-detail-value">${job.BusinessDivision || 'InHousePrint'}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- JOB SPECIFICATIONS SECTION -->
                        <div class="kanban-content-section">
                            <div class="kanban-section-title">
                                <i class="fas fa-file-alt"></i>
                                <span>Job Specifications</span>
                            </div>
                            <div class="kanban-section-content">
                                <div class="kanban-detail-grid">
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label"><i class="fas fa-align-left"></i> Description</span>
                                        <span class="kanban-detail-value">${this.escapeHtml(job.ProductionNotes || job.TicketNotes || job.ShortJobDesc || job.description || 'N/A')}</span>
                                    </div>
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label"><i class="fas fa-boxes"></i> Quantity</span>
                                        <span class="kanban-detail-value">${job.QTY || job.quantity || 0}</span>
                                    </div>
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label"><i class="fas fa-dollar-sign"></i> Job Cost</span>
                                        <span class="kanban-detail-value">$${this.formatCurrency(job.Cost || job.cost || 0)}</span>
                                    </div>
                                    ${job.JobType ? `
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label"><i class="fas fa-tag"></i> Job Type</span>
                                        <span class="kanban-detail-value">${this.escapeHtml(job.JobType)}</span>
                                    </div>` : ''}
                                    ${job.ClientOrderNum ? `
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label"><i class="fas fa-hashtag"></i> Client PO</span>
                                        <span class="kanban-detail-value">${this.escapeHtml(job.ClientOrderNum)}</span>
                                    </div>` : ''}
                                </div>
                            </div>
                        </div>
                        
                        ${(job.PaperType || job.GSM || job.PaperSize || job.Pages) ? `
                        <!-- PAPER & MATERIALS SECTION -->
                        <div class="kanban-content-section">
                            <div class="kanban-section-title">
                                <i class="fas fa-copy"></i>
                                <span>Paper & Materials</span>
                            </div>
                            <div class="kanban-section-content">
                                <div class="kanban-detail-grid">
                                    ${job.PaperType ? `
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label"><i class="fas fa-file"></i> Paper Type</span>
                                        <span class="kanban-detail-value">${this.escapeHtml(job.PaperType)}</span>
                                    </div>` : ''}
                                    ${job.GSM ? `
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label"><i class="fas fa-weight"></i> GSM/Weight</span>
                                        <span class="kanban-detail-value">${this.escapeHtml(job.GSM)}</span>
                                    </div>` : ''}
                                    ${job.PaperSize ? `
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label"><i class="fas fa-ruler-combined"></i> Size</span>
                                        <span class="kanban-detail-value">${this.escapeHtml(job.PaperSize)}</span>
                                    </div>` : ''}
                                    ${job.Pages ? `
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label"><i class="fas fa-book"></i> Pages</span>
                                        <span class="kanban-detail-value">${job.Pages}</span>
                                    </div>` : ''}
                                    ${job.BindType ? `
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label"><i class="fas fa-book-open"></i> Binding</span>
                                        <span class="kanban-detail-value">${this.escapeHtml(job.BindType)}</span>
                                    </div>` : ''}
                                </div>
                            </div>
                        </div>` : ''}
                        
                        ${(job.CelloYes || job.FoldYes || job.StitchYes || job.RingBind || job.PerfectBind) ? `
                        <!-- FINISHING OPTIONS SECTION -->
                        <div class="kanban-content-section">
                            <div class="kanban-section-title">
                                <i class="fas fa-magic"></i>
                                <span>Finishing Options</span>
                            </div>
                            <div class="kanban-section-content">
                                <div class="kanban-detail-grid">
                                    ${job.FrontCelloGloss || job.FrontCelloMatt ? `
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label"><i class="fas fa-star"></i> Front Cello</span>
                                        <span class="kanban-detail-value">${job.FrontCelloGloss ? 'Gloss' : ''} ${job.FrontCelloMatt ? 'Matt' : ''}</span>
                                    </div>` : ''}
                                    ${job.BackCelloGloss || job.BackCelloMatt ? `
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label"><i class="fas fa-star-half-alt"></i> Back Cello</span>
                                        <span class="kanban-detail-value">${job.BackCelloGloss ? 'Gloss' : ''} ${job.BackCelloMatt ? 'Matt' : ''}</span>
                                    </div>` : ''}
                                    ${job.FoldDesc ? `
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label"><i class="fas fa-folder"></i> Folding</span>
                                        <span class="kanban-detail-value">${this.escapeHtml(job.FoldDesc)}</span>
                                    </div>` : ''}
                                    ${job.StitchYes ? `
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label"><i class="fas fa-compress-alt"></i> Stitching</span>
                                        <span class="kanban-detail-value">Yes</span>
                                    </div>` : ''}
                                    ${job.RingBind ? `
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label"><i class="fas fa-ring"></i> Ring Binding</span>
                                        <span class="kanban-detail-value">Yes</span>
                                    </div>` : ''}
                                    ${job.PerfectBind ? `
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label"><i class="fas fa-book-open"></i> Perfect Bind</span>
                                        <span class="kanban-detail-value">Yes</span>
                                    </div>` : ''}
                                    ${job.Books ? `
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label"><i class="fas fa-books"></i> Books</span>
                                        <span class="kanban-detail-value">${job.Books}</span>
                                    </div>` : ''}
                                </div>
                            </div>
                        </div>` : ''}
                        
                        ${job.TicketNotes ? `
                        <!-- PRODUCTION NOTES SECTION -->
                        <div class="kanban-content-section">
                            <div class="kanban-section-title">
                                <i class="fas fa-sticky-note"></i>
                                <span>Production Notes</span>
                            </div>
                            <div class="kanban-section-content">
                                <div class="kanban-notes-text" style="white-space: pre-wrap;">${this.escapeHtml(job.TicketNotes)}</div>
                            </div>
                        </div>` : ''}
                        
                        <!-- STATUS INFORMATION SECTION -->
                        <div class="kanban-content-section">
                            <div class="kanban-section-title">
                                <i class="fas fa-info-circle"></i>
                                <span>Status Information</span>
                            </div>
                            <div class="kanban-section-content">
                                <div class="kanban-detail-grid">
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label">Current Stage</span>
                                        <span class="kanban-detail-value"><i class="fas ${stageInfo.icon}" style="color: ${stageInfo.color};"></i> ${stage?.name || job.StageDescription || 'Unknown'}</span>
                                    </div>
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label">Due Date</span>
                                        <span class="kanban-detail-value" style="color: ${this.isOverdue(job.DateRequired || job.due_date) ? '#f85149' : '#f0f6fc'};">${job.DateRequired ? this.formatDate(job.DateRequired) : (job.due_date ? this.formatDate(job.due_date) : 'Not set')}</span>
                                    </div>
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label">Days in System</span>
                                        <span class="kanban-detail-value">${job.DaysInSystem || 0} days</span>
                                    </div>
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label">Urgency Level</span>
                                        <span class="kanban-detail-value">${job.UrgencyLevel || 'Normal'}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- CUSTOMER METRICS SECTION -->
                        <div class="kanban-content-section">
                            <div class="kanban-section-title">
                                <i class="fas fa-chart-line"></i>
                                <span>Customer Metrics</span>
                            </div>
                            <div class="kanban-section-content">
                                <div class="kanban-detail-grid">
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label"><i class="fas fa-trophy"></i> Customer Tier</span>
                                        <span class="kanban-detail-value">${tierInfo.label}</span>
                                    </div>
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label"><i class="fas fa-shopping-cart"></i> Orders (12mo)</span>
                                        <span class="kanban-detail-value">${job.CustomerOrderCount || 0}</span>
                                    </div>
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label"><i class="fas fa-dollar-sign"></i> Lifetime Value</span>
                                        <span class="kanban-detail-value">$${this.formatCurrency(job.CustomerLifetimeValue || 0)}</span>
                                    </div>
                                    <div class="kanban-detail-item">
                                        <span class="kanban-detail-label"><i class="fas fa-star"></i> Priority Score</span>
                                        <span class="kanban-detail-value">${job.AIPriorityScore || 0}/999</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        ${job.Shipping ? `
                        <!-- SHIPPING SECTION -->
                        <div class="kanban-content-section">
                            <div class="kanban-section-title">
                                <i class="fas fa-shipping-fast"></i>
                                <span>Shipping</span>
                            </div>
                            <div class="kanban-section-content">
                                <div class="kanban-notes-text">${this.escapeHtml(job.Shipping)}</div>
                            </div>
                        </div>` : ''}
                        
                        <!-- PRODUCTION LOG SECTION -->
                        <div class="kanban-content-section">
                            <div class="kanban-section-title">
                                <i class="fas fa-history"></i>
                                <span>Production Log</span>
                                <button class="btn btn-sm btn-primary" style="margin-left: auto; padding: 4px 12px;" onclick="window.currentKanbanModule.showClientNotificationDialog(${job.TicketID})">
                                    <i class="fas fa-envelope"></i> Notify Client
                                </button>
                            </div>
                            <div class="kanban-section-content" style="padding: 0;">
                                <div id="production-log-entries-${job.TicketID}" style="max-height: 300px; overflow-y: auto; padding: 12px;">
                                    <div style="text-align: center; padding: 20px; color: #9ca3af;">
                                        <i class="fas fa-spinner fa-spin"></i> Loading production log...
                                    </div>
                                </div>
                                
                                <!-- Add Entry Form -->
                                <div style="border-top: 1px solid #30363d; padding: 12px; background: #0d1117;">
                                    <div style="display: flex; gap: 8px; margin-bottom: 8px;">
                                        <input type="text" id="log-initials-${job.TicketID}" placeholder="Initials" maxlength="3" style="width: 70px; padding: 6px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6; font-size: 13px;" />
                                        <select id="log-type-${job.TicketID}" style="flex: 1; padding: 6px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6; font-size: 13px;">
                                            <option value="note">Note</option>
                                            <option value="wastage">Wastage</option>
                                            <option value="delay">Delay</option>
                                            <option value="stock_change">Stock Change</option>
                                        </select>
                                    </div>
                                    <textarea id="log-note-${job.TicketID}" placeholder="Enter note, wastage details, or delay reason..." rows="2" style="width: 100%; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6; font-size: 13px; margin-bottom: 8px; resize: vertical;"></textarea>
                                    <button class="btn btn-primary btn-sm" onclick="window.currentKanbanModule.addProductionLogEntry(${job.TicketID})" style="width: 100%;">
                                        <i class="fas fa-plus"></i> Add Log Entry
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- FOOTER -->
                    <div class="kanban-modal-footer">
                        <button class="btn btn-secondary" onclick="document.getElementById('job-details-modal').remove();">
                            <i class="fas fa-times"></i> Close
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Load production log entries after modal is added to DOM
        setTimeout(() => this.loadProductionLogEntries(job.TicketID), 100);
    },

    // ========================================================================
    // CLIENT NOTIFICATION
    // ========================================================================

    notifyClient(jobId) {
        const job = this.jobsCache.get(jobId);
        if (!job) return;

        const notificationHtml = `
            <div id="notify-client-modal" style="
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.85);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10001;
            ">
                <div style="
                    background: #161b22;
                    border: 2px solid #30363d;
                    border-radius: 12px;
                    padding: 24px;
                    max-width: 600px;
                    width: 90%;
                ">
                    <h3 style="margin: 0 0 16px 0; color: #f0f6fc; font-size: 20px; font-weight: 700;">
                        <i class="fas fa-paper-plane"></i> Notify Client
                    </h3>
                    
                    <div style="margin-bottom: 16px;">
                        <label style="display: block; color: #8b949e; font-size: 13px; font-weight: 600; margin-bottom: 8px;">
                            Client: ${job.client_name}
                        </label>
                        <label style="display: block; color: #8b949e; font-size: 13px; font-weight: 600; margin-bottom: 8px;">
                            Job: ${job.ticket_number}
                        </label>
                    </div>

                    <div style="margin-bottom: 16px;">
                        <label style="display: block; color: #8b949e; font-size: 13px; font-weight: 600; margin-bottom: 8px;">
                            Email Address
                        </label>
                        <input type="email" id="client-email" placeholder="client@example.com" style="
                            width: 100%;
                            padding: 10px;
                            background: #0d1117;
                            border: 1px solid #30363d;
                            border-radius: 6px;
                            color: #f0f6fc;
                            font-size: 14px;
                        ">
                    </div>

                    <div style="margin-bottom: 20px;">
                        <label style="display: block; color: #8b949e; font-size: 13px; font-weight: 600; margin-bottom: 8px;">
                            Message
                        </label>
                        <textarea id="client-message" rows="6" placeholder="Your message to the client..." style="
                            width: 100%;
                            padding: 10px;
                            background: #0d1117;
                            border: 1px solid #30363d;
                            border-radius: 6px;
                            color: #f0f6fc;
                            font-size: 14px;
                            resize: vertical;
                        "></textarea>
                    </div>

                    <div style="display: flex; gap: 10px; justify-content: flex-end;">
                        <button onclick="document.getElementById('notify-client-modal').remove()" style="
                            padding: 10px 20px;
                            background: #21262d;
                            border: 1px solid #30363d;
                            color: #c9d1d9;
                            border-radius: 6px;
                            cursor: pointer;
                            font-size: 14px;
                            font-weight: 600;
                        ">Cancel</button>
                        <button onclick="window.currentKanbanModule.sendClientNotification(${jobId})" style="
                            padding: 10px 20px;
                            background: #1f6feb;
                            border: none;
                            color: white;
                            border-radius: 6px;
                            cursor: pointer;
                            font-size: 14px;
                            font-weight: 600;
                        ">
                            <i class="fas fa-paper-plane"></i> Send
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', notificationHtml);
    },

    async sendClientNotification(jobId) {
        const email = document.getElementById('client-email').value;
        const message = document.getElementById('client-message').value;

        if (!email || !message) {
            this.showErrorToast('Please fill in all fields');
            return;
        }

        try {
            const response = await fetch(`${this.analyticsApiBase}/notify-client`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    job_id: jobId,
                    email,
                    message,
                    timestamp: new Date().toISOString()
                })
            });

            if (!response.ok) {
                throw new Error('Failed to send notification');
            }

            document.getElementById('notify-client-modal').remove();
            this.showSuccessToast('Client notified successfully');

        } catch (error) {
            this.log.error('Failed to notify client', error);
            this.showErrorToast('Failed to send notification');
        }
    },

    // ========================================================================
    // PRODUCTION LOG - V10 ADDITIONS
    // ========================================================================

    /**
     * Load and display production log entries in the job details modal
     */
    async loadProductionLogEntries(ticketId) {
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/production-log/${ticketId}`);
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.message || 'Failed to load production log');
            }

            this.renderProductionLogEntries(ticketId, data.entries || []);

        } catch (error) {
            console.error('Failed to load production log:', error);
            const container = document.getElementById(`production-log-entries-${ticketId}`);
            if (container) {
                container.innerHTML = `
                    <div style="text-align: center; padding: 20px; color: #ef4444;">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p style="margin: 8px 0 0 0;">Failed to load production log</p>
                    </div>
                `;
            }
        }
    },

    /**
     * Render production log entries in the display area
     */
    renderProductionLogEntries(ticketId, entries) {
        const container = document.getElementById(`production-log-entries-${ticketId}`);
        if (!container) return;

        if (entries.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 20px; color: #9ca3af;">
                    <i class="fas fa-clipboard-list"></i>
                    <p style="margin: 8px 0 0 0;">No production log entries yet</p>
                </div>
            `;
            return;
        }

        // Sort entries by date/time (newest first)
        entries.sort((a, b) => {
            const dateA = new Date(a.log_date + ' ' + a.log_time);
            const dateB = new Date(b.log_date + ' ' + b.log_time);
            return dateB - dateA;
        });

        const entryTypeIcons = {
            stage_change: 'fa-exchange-alt',
            note: 'fa-sticky-note',
            wastage: 'fa-trash-alt',
            delay: 'fa-clock',
            stock_change: 'fa-boxes',
            client_notification: 'fa-envelope'
        };

        const entryTypeColors = {
            stage_change: '#3b82f6',
            note: '#fbbf24',
            wastage: '#ef4444',
            delay: '#f97316',
            stock_change: '#8b5cf6',
            client_notification: '#10b981'
        };

        container.innerHTML = entries.map(entry => {
            const icon = entryTypeIcons[entry.entry_type] || 'fa-info-circle';
            const color = entryTypeColors[entry.entry_type] || '#6b7280';
            const dateTime = new Date(entry.log_date + ' ' + entry.log_time);
            const formattedDate = dateTime.toLocaleDateString() + ' ' + dateTime.toLocaleTimeString();

            return `
                <div style="display: flex; gap: 12px; padding: 12px; border-bottom: 1px solid #30363d; align-items: start;">
                    <div style="flex-shrink: 0; width: 32px; height: 32px; border-radius: 50%; background: ${color}20; display: flex; align-items: center; justify-content: center; color: ${color};">
                        <i class="fas ${icon}" style="font-size: 14px;"></i>
                    </div>
                    <div style="flex: 1;">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 4px;">
                            <div>
                                <span style="font-weight: 600; color: #f3f4f6; font-size: 13px;">${entry.user_initials || 'N/A'}</span>
                                <span style="color: #9ca3af; font-size: 12px; margin-left: 8px;">${entry.entry_type.replace('_', ' ')}</span>
                            </div>
                            <span style="color: #6b7280; font-size: 11px;">${formattedDate}</span>
                        </div>
                        <p style="margin: 0; color: #d1d5db; font-size: 13px; line-height: 1.5;">${this.escapeHtml(entry.note_text)}</p>
                        ${entry.wastage_amount ? `<p style="margin: 4px 0 0 0; color: #ef4444; font-size: 12px;">Wastage: ${entry.wastage_amount} ${entry.wastage_unit}</p>` : ''}
                        ${entry.delay_hours ? `<p style="margin: 4px 0 0 0; color: #f97316; font-size: 12px;">Delay: ${entry.delay_hours} hours</p>` : ''}
                    </div>
                </div>
            `;
        }).join('');
    },

    /**
     * Add a new production log entry
     */
    async addProductionLogEntry(ticketId) {
        const initials = document.getElementById(`log-initials-${ticketId}`)?.value.trim();
        const type = document.getElementById(`log-type-${ticketId}`)?.value;
        const note = document.getElementById(`log-note-${ticketId}`)?.value.trim();

        if (!initials) {
            alert('Please enter your initials');
            return;
        }

        if (!note) {
            alert('Please enter a note');
            return;
        }

        try {
            const payload = {
                user_initials: initials.toUpperCase(),
                entry_type: type,
                note_text: note
            };

            // Add type-specific fields based on entry type
            if (type === 'wastage') {
                const wastageAmount = prompt('Wastage amount:');
                const wastageUnit = prompt('Unit (sheets/meters/etc):') || 'sheets';
                if (wastageAmount) {
                    payload.wastage_amount = parseFloat(wastageAmount);
                    payload.wastage_unit = wastageUnit;
                    payload.wastage_reason = note;
                }
            } else if (type === 'delay') {
                const delayHours = prompt('Delay duration (hours):');
                if (delayHours) {
                    payload.delay_hours = parseFloat(delayHours);
                    payload.delay_reason = note;
                }
            }

            const response = await fetch(`${this.API_BASE_URL}/api/production-log/${ticketId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.message || 'Failed to add log entry');
            }

            // Clear form
            document.getElementById(`log-initials-${ticketId}`).value = '';
            document.getElementById(`log-note-${ticketId}`).value = '';

            // Reload entries
            this.loadProductionLogEntries(ticketId);

            this.showSuccessToast('Log entry added successfully');

        } catch (error) {
            console.error('Failed to add log entry:', error);
            alert('Failed to add log entry: ' + error.message);
        }
    },

    /**
     * Show client notification dialog
     */
    showClientNotificationDialog(ticketId) {
        // Find job to get client info
        const job = Array.from(this.jobsCache.values()).find(j => j.TicketID === ticketId);
        const clientName = job ? (job.ClientName || job.client_name) : 'Client';

        const dialogHtml = `
            <div class="modal-overlay" id="notification-dialog" style="z-index: 10002;">
                <div class="kanban-job-modal" style="width: 600px; max-width: 90%;">
                    <div class="kanban-modal-header">
                        <div class="kanban-modal-title">
                            <i class="fas fa-envelope"></i>
                            <span>Send Client Notification - Ticket #${ticketId}</span>
                        </div>
                        <button class="kanban-modal-close-btn" onclick="document.getElementById('notification-dialog').remove();">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>

                    <div class="kanban-modal-body" style="padding: 20px;">
                        <div style="margin-bottom: 16px;">
                            <label style="display: block; font-size: 13px; font-weight: 600; color: #f3f4f6; margin-bottom: 6px;">
                                <i class="fas fa-user"></i> Client Name
                            </label>
                            <input type="text" id="notif-client-name" value="${this.escapeHtml(clientName)}" 
                                   style="width: 100%; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6;" readonly />
                        </div>

                        <div style="margin-bottom: 16px;">
                            <label style="display: block; font-size: 13px; font-weight: 600; color: #f3f4f6; margin-bottom: 6px;">
                                <i class="fas fa-bell"></i> Notification Type
                            </label>
                            <select id="notif-type" style="width: 100%; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6;">
                                <option value="email">Email</option>
                                <option value="sms">SMS</option>
                                <option value="phone">Phone Call</option>
                                <option value="whatsapp">WhatsApp</option>
                                <option value="client_portal">Client Portal</option>
                            </select>
                        </div>

                        <div style="margin-bottom: 16px;">
                            <label style="display: block; font-size: 13px; font-weight: 600; color: #f3f4f6; margin-bottom: 6px;">
                                <i class="fas fa-envelope"></i> Email Address
                            </label>
                            <input type="email" id="notif-email" placeholder="client@example.com" 
                                   style="width: 100%; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6;" />
                        </div>

                        <div style="margin-bottom: 16px;">
                            <label style="display: block; font-size: 13px; font-weight: 600; color: #f3f4f6; margin-bottom: 6px;">
                                <i class="fas fa-phone"></i> Phone Number
                            </label>
                            <input type="tel" id="notif-phone" placeholder="+61 4XX XXX XXX" 
                                   style="width: 100%; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6;" />
                        </div>

                        <div style="margin-bottom: 16px;">
                            <label style="display: block; font-size: 13px; font-weight: 600; color: #f3f4f6; margin-bottom: 6px;">
                                <i class="fas fa-heading"></i> Subject
                            </label>
                            <input type="text" id="notif-subject" placeholder="Your print job update" 
                                   style="width: 100%; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6;" />
                        </div>

                        <div style="margin-bottom: 16px;">
                            <label style="display: block; font-size: 13px; font-weight: 600; color: #f3f4f6; margin-bottom: 6px;">
                                <i class="fas fa-comment-alt"></i> Message
                            </label>
                            <textarea id="notif-message" rows="4" placeholder="Enter your message to the client..." 
                                      style="width: 100%; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6; resize: vertical;"></textarea>
                        </div>

                        <div style="margin-bottom: 16px;">
                            <label style="display: block; font-size: 13px; font-weight: 600; color: #f3f4f6; margin-bottom: 6px;">
                                <i class="fas fa-user"></i> Your Initials
                            </label>
                            <input type="text" id="notif-initials" placeholder="JD" maxlength="3" 
                                   style="width: 100px; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6;" />
                        </div>

                        <div style="padding: 12px; background: #1c2128; border: 1px solid #30363d; border-radius: 6px; margin-bottom: 16px;">
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                                <input type="checkbox" id="notif-auto-send" style="width: 18px; height: 18px;" />
                                <label for="notif-auto-send" style="font-size: 13px; font-weight: 600; color: #f3f4f6; cursor: pointer;">
                                    <i class="fas fa-paper-plane"></i> Auto-send notification
                                </label>
                            </div>
                            <p style="margin: 0; font-size: 12px; color: #9ca3af; padding-left: 26px;">
                                If unchecked, notification will be logged only (not sent automatically)
                            </p>
                        </div>
                    </div>

                    <div class="kanban-modal-footer" style="display: flex; gap: 8px; justify-content: flex-end;">
                        <button class="btn btn-secondary" onclick="document.getElementById('notification-dialog').remove();">
                            <i class="fas fa-times"></i> Cancel
                        </button>
                        <button class="btn btn-primary" onclick="window.currentKanbanModule.sendNotificationToClient(${ticketId});">
                            <i class="fas fa-check"></i> Send & Log
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', dialogHtml);
    },

    /**
     * Send client notification from dialog
     */
    async sendNotificationToClient(ticketId) {
        const type = document.getElementById('notif-type')?.value;
        const email = document.getElementById('notif-email')?.value.trim();
        const phone = document.getElementById('notif-phone')?.value.trim();
        const subject = document.getElementById('notif-subject')?.value.trim();
        const message = document.getElementById('notif-message')?.value.trim();
        const initials = document.getElementById('notif-initials')?.value.trim();
        const autoSend = document.getElementById('notif-auto-send')?.checked;

        if (!initials) {
            alert('Please enter your initials');
            return;
        }

        if (!message) {
            alert('Please enter a message');
            return;
        }

        const recipient = type === 'email' ? email : phone;
        if (!recipient) {
            alert(`Please enter a ${type === 'email' ? 'email address' : 'phone number'}`);
            return;
        }

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/production-log/${ticketId}/notification`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_initials: initials.toUpperCase(),
                    notification_type: type,
                    notification_recipient: recipient,
                    notification_subject: subject || 'Print Job Update',
                    notification_message: message,
                    notification_status: autoSend ? 'sent' : 'pending',
                    auto_send: autoSend
                })
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.message || 'Failed to log notification');
            }

            // Close dialog
            document.getElementById('notification-dialog')?.remove();

            // Reload production log if modal is open
            this.loadProductionLogEntries(ticketId);

            const action = autoSend ? 'sent and logged' : 'logged (not sent)';
            this.showSuccessToast(`Client notification ${action}`);

        } catch (error) {
            console.error('Failed to send notification:', error);
            alert('Failed to send notification: ' + error.message);
        }
    },

    // ========================================================================
    // PRODUCTION LOG - LEGACY METHOD
    // ========================================================================

    async viewProductionLog(jobId) {
        try {
            const response = await fetch(`${this.analyticsApiBase}/production-log/${jobId}`);
            if (!response.ok) throw new Error('Failed to load production log');

            const logs = await response.json();

            const logHtml = `
                <div id="production-log-modal" style="
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0,0,0,0.85);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 10001;
                ">
                    <div style="
                        background: #0d1117;
                        border: 2px solid #30363d;
                        border-radius: 12px;
                        max-width: 900px;
                        width: 90%;
                        max-height: 90vh;
                        overflow: hidden;
                        display: flex;
                        flex-direction: column;
                    ">
                        <div style="
                            padding: 20px;
                            background: #161b22;
                            border-bottom: 2px solid #30363d;
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                        ">
                            <h3 style="margin: 0; color: #f0f6fc; font-size: 20px; font-weight: 700;">
                                <i class="fas fa-history"></i> Production Log
                            </h3>
                            <button onclick="document.getElementById('production-log-modal').remove()" style="
                                background: rgba(255,255,255,0.1);
                                border: none;
                                color: white;
                                width: 32px;
                                height: 32px;
                                border-radius: 6px;
                                cursor: pointer;
                                font-size: 16px;
                            ">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>

                        <div style="padding: 20px; flex: 1; overflow-y: auto;">
                            ${logs.length === 0 ? `
                                <div style="text-align: center; color: #6e7681; padding: 40px;">
                                    <i class="fas fa-inbox" style="font-size: 48px; margin-bottom: 16px; opacity: 0.3;"></i>
                                    <p>No production history available</p>
                                </div>
                            ` : logs.map(log => `
                                <div style="
                                    background: #161b22;
                                    border: 1px solid #30363d;
                                    border-radius: 8px;
                                    padding: 16px;
                                    margin-bottom: 12px;
                                ">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                        <div style="color: #f0f6fc; font-weight: 600; font-size: 14px;">
                                            ${log.from_stage} <i class="fas fa-arrow-right" style="color: #58a6ff;"></i> ${log.to_stage}
                                        </div>
                                        <div style="color: #8b949e; font-size: 13px;">
                                            ${this.formatDateTime(log.timestamp)}
                                        </div>
                                    </div>
                                    <div style="color: #8b949e; font-size: 13px;">
                                        Changed by: ${log.changed_by || 'System'}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', logHtml);

        } catch (error) {
            this.log.error('Failed to load production log', error);
            this.showErrorToast('Failed to load production log');
        }
    },

    // ========================================================================
    // EVENT LISTENERS
    // ========================================================================

    setupEventListeners() {
        // Timeframe filter
        const timeframeSelector = document.getElementById('timeframe-selector');
        if (timeframeSelector) {
            const cleanup = this.dom.on(timeframeSelector, 'change', (e) => {
                this.state.filters.timeframe_months = parseInt(e.target.value);
                this.refreshData();
            });
            this.eventCleanupFns.push(cleanup);
        }

        // Priority filter
        const prioritySelector = document.getElementById('priority-selector');
        if (prioritySelector) {
            const cleanup = this.dom.on(prioritySelector, 'change', (e) => {
                this.state.filters.priority_filter = e.target.value;
                this.renderKanbanBoard();
            });
            this.eventCleanupFns.push(cleanup);
        }

        // Search input
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            const cleanup = this.dom.on(searchInput, 'input', (e) => {
                this.state.filters.search_text = e.target.value;
                this.renderKanbanBoard();
            });
            this.eventCleanupFns.push(cleanup);
        }

        // Refresh button
        const refreshBtn = document.getElementById('inhouse-refresh-btn');
        if (refreshBtn) {
            const cleanup = this.dom.on(refreshBtn, 'click', () => {
                this.refreshData();
            });
            this.eventCleanupFns.push(cleanup);
        }

        // Color toggles
        this.setupColorToggleListeners();
    },

    setupColorToggleListeners() {
        const toggles = [
            { id: 'toggle-border-colors', key: 'showBorderColors' },
            { id: 'toggle-background-colors', key: 'showBackgroundColors' },
            { id: 'toggle-banner-colors', key: 'showBannerColors' }
        ];

        toggles.forEach(({ id, key }) => {
            const btn = document.getElementById(id);
            if (btn) {
                const cleanup = this.dom.on(btn, 'click', () => {
                    this.colorToggles[key] = !this.colorToggles[key];
                    btn.classList.toggle('active', this.colorToggles[key]);
                    this.saveColorToggles();
                    this.renderKanbanBoard();
                });
                this.eventCleanupFns.push(cleanup);
            }
        });
    },

    setupSidebarEventListeners() {
        const workboardSelect = this.ui.sidebarContainer?.querySelector('#sidebar-workboard-select');
        if (workboardSelect) {
            const cleanup = this.dom.on(workboardSelect, 'change', (e) => {
                this.sidebar.selectedWorkboard = e.target.value;
                this.loadSidebarWorkboardColumns(e.target.value);
            });
            this.eventCleanupFns.push(cleanup);
        }
    },

    loadSidebarWorkboardColumns(workboardKey) {
        // Sidebar implementation would go here
        this.log.info(`Loading sidebar for workboard: ${workboardKey}`);
    },

    // ========================================================================
    // UTILITY METHODS
    // ========================================================================

    startAutoRefresh() {
        this.refreshTimer = setInterval(() => {
            this.refreshData();
        }, 300000); // 5 minutes
    },

    updateLastRefreshTime() {
        this.state.lastRefresh = Date.now();
        const timeElement = document.querySelector('#last-refresh-time .time-value');
        if (timeElement) {
            timeElement.textContent = 'Just now';
        }
    },

    calculateDaysInStage(job) {
        if (!job.stage_entry_date) return 0;
        const entryDate = new Date(job.stage_entry_date);
        const now = new Date();
        const diff = now - entryDate;
        return Math.floor(diff / (1000 * 60 * 60 * 24));
    },

    getDaysUntilDue(dueDate) {
        if (!dueDate) return null;
        const due = new Date(dueDate);
        const now = new Date();
        now.setHours(0, 0, 0, 0);
        due.setHours(0, 0, 0, 0);
        const diff = due - now;
        return Math.ceil(diff / (1000 * 60 * 60 * 24));
    },

    isOverdue(dueDate) {
        if (!dueDate) return false;
        return this.getDaysUntilDue(dueDate) < 0;
    },

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    },

    formatDateTime(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    },

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Calculate total days in system
     */
    calculateDaysInSystem(job) {
        if (!job.created_at) return 0;
        const created = new Date(job.created_at);
        const now = new Date();
        const diffTime = Math.abs(now - created);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays;
    },

    /**
     * Calculate stage time info with color coding
     */
    calculateStageTimeInfo(job, stage, daysInStage) {
        const stageName = stage?.name || 'this stage';
        let cssClass = 'stage-normal';
        let display = `${daysInStage}d in ${stageName}`;

        // Color coding based on duration
        if (daysInStage > 7) {
            cssClass = 'stage-overdue';  // Red - over 7 days
        } else if (daysInStage > 3) {
            cssClass = 'stage-warning';   // Yellow - 4-7 days
        }
        // else 'stage-normal' (gray - 0-3 days)

        return { display, cssClass };
    },

    /**
     * Get status badge class
     */
    getStatusBadgeClass(status) {
        if (!status) return 'status-active';
        const statusLower = status.toLowerCase();
        if (statusLower.includes('delayed')) return 'status-delayed';
        if (statusLower.includes('risk') || statusLower.includes('warning')) return 'status-warning';
        if (statusLower.includes('on track') || statusLower.includes('complete')) return 'status-success';
        return 'status-active';
    },

    /**
     * Format currency
     */
    formatCurrency(amount) {
        if (amount === null || amount === undefined) return '0.00';
        return parseFloat(amount).toFixed(2);
    },

    truncate(text, maxLength) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    },

    getPriorityIcon(priority) {
        const icons = {
            critical: '<i class="fas fa-exclamation-circle" style="color: #ef4444;"></i>',
            urgent: '<i class="fas fa-exclamation-triangle" style="color: #f97316;"></i>',
            high: '<i class="fas fa-arrow-up" style="color: #eab308;"></i>',
            normal: '<i class="fas fa-circle" style="color: #3b82f6;"></i>',
            low: '<i class="fas fa-arrow-down" style="color: #6b7280;"></i>'
        };
        return icons[priority?.toLowerCase()] || icons.normal;
    },

    lightenColor(color, amount) {
        const num = parseInt(color.replace('#', ''), 16);
        const r = Math.min(255, (num >> 16) + Math.round(255 * amount));
        const g = Math.min(255, ((num >> 8) & 0x00FF) + Math.round(255 * amount));
        const b = Math.min(255, (num & 0x0000FF) + Math.round(255 * amount));
        return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
    },

    darkenColor(color, amount) {
        const num = parseInt(color.replace('#', ''), 16);
        const r = Math.max(0, (num >> 16) - Math.round(255 * amount));
        const g = Math.max(0, ((num >> 8) & 0x00FF) - Math.round(255 * amount));
        const b = Math.max(0, (num & 0x0000FF) - Math.round(255 * amount));
        return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
    },

    rgbaToHex(rgba) {
        if (rgba.startsWith('#')) return rgba;
        const match = rgba.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*[\d.]+)?\)/);
        if (!match) return '#000000';
        const r = parseInt(match[1]);
        const g = parseInt(match[2]);
        const b = parseInt(match[3]);
        return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
    },

    showSuccessToast(message) {
        this.showToast(message, '#238636');
    },

    showErrorToast(message) {
        this.showToast(message, '#da3633');
    },

    showInfoToast(message) {
        this.showToast(message, '#1f6feb');
    },

    showToast(message, color) {
        const toast = document.createElement('div');
        toast.innerHTML = `
            <div style="
                position: fixed;
                bottom: 30px;
                right: 30px;
                background: ${color};
                color: white;
                padding: 16px 24px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                font-weight: 600;
                z-index: 10002;
                animation: slideInRight 0.3s;
            ">
                ${message}
            </div>
        `;

        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    },

    showErrorState(error) {
        const container = this.ui.dashboardContainer;
        if (!container) return;

        container.innerHTML = `
            <div style="
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 400px;
                color: #8b949e;
                text-align: center;
                padding: 40px;
            ">
                <i class="fas fa-exclamation-triangle" style="font-size: 64px; color: #da3633; margin-bottom: 20px;"></i>
                <h2 style="color: #f0f6fc; margin: 0 0 10px 0;">Failed to Load Module</h2>
                <p style="margin: 0 0 20px 0; max-width: 500px;">${error.message}</p>
                <button onclick="window.location.reload()" style="
                    padding: 10px 20px;
                    background: #238636;
                    border: none;
                    color: white;
                    border-radius: 6px;
                    cursor: pointer;
                    font-weight: 600;
                ">
                    <i class="fas fa-sync"></i> Retry
                </button>
            </div>
        `;
    }
};
