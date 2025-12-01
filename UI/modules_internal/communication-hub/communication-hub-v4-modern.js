/**
 * FILE: UI/modules_external/communication-hub/communication-hub-v4-modern.js
 * MODULE TYPE: external
 * ARCHITECTURE: V4-Modern (Composition pattern)
 * 
 * PURPOSE: Communication Hub - Unified inbox for Gmail and Outlook with AI agent integration
 * 
 * CAPABILITIES:
 * ================
 * ✅ Dashboard: YES - Unified inbox with multi-tab interface
 *    - Container: #communication-main-container
 *    - Rendering: JS-controlled with sub-tabs
 *    - Features: Email list, compose, threads, search, drag-and-drop to AI
 * 
 * ❌ Sidebar: NO - Not applicable for this module
 * 
 * DEPENDENCIES:
 * =============
 * - dom (DOM manipulation)
 * - api (Backend API calls)
 * - storage (localStorage for filters/preferences)
 * - events (Inter-module communication)
 * - log (Module-specific logger - always included)
 * 
 * EXTERNAL LIBRARIES:
 * ===================
 * - Tabulator.js (email table rendering)
 * 
 * FEATURES:
 * =========
 * ✅ Gmail and Outlook unified inbox
 * ✅ Email tagging system (green/orange/red)
 * ✅ Drag-and-drop emails to AI sidebar
 * ✅ Right-click context menu
 * ✅ Email composition with threading
 * ✅ Full-text search across accounts
 * ✅ Export to Excel/CSV/PDF
 * ✅ Pagination and filtering
 * 
 * MIGRATION FROM: BaseModule inheritance pattern (v2.3)
 * MIGRATED TO: V4-Modern composition pattern
 * VERSION: 4.0.0
 * 
 * LAST MODIFIED: 2025-11-30 - Refactored to Modern Module Framework
 */

console.log('🔷 Communication Hub Module V4.0 - Modern Framework Pattern');

export default {
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // STATE (Private to this object)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    // Utilities (injected by ModuleLoader)
    dom: null,
    api: null,
    storage: null,
    events: null,
    log: null,

    // Module-specific state
    state: {
        // Email data
        emails: [],
        accounts: [],
        selectedEmails: new Set(),
        emailTags: {}, // { emailId: 'green' | 'orange' | 'red' | null }
        emailThreads: {}, // { emailId: thread_slug }
        threads: [], // Array of thread assignments from backend

        // UI state
        currentTab: 'unified-inbox',
        tabulatorTable: null,
        tableReady: false,
        draggedEmail: null,
        contextMenu: null,

        // Filters and pagination
        selectedAccount: 'all',
        currentPage: 1,
        pageSize: 50,
        currentAccountFilter: 'all',
        currentEmailLimit: 20,  // Reduced for faster loading

        // Backend configuration
        apiBase: null,

        // Email content cache (reduce redundant API calls)
        emailContentCache: {},

        // Loading states
        loading: {
            emails: false,
            accounts: false,
            compose: false,
            threads: false,
            search: false
        },

        // Compose state
        compose: {
            to: '',
            cc: '',
            bcc: '',
            subject: '',
            body: '',
            attachments: [],
            replyTo: null,
            account: null
        },

        // Search state
        search: {
            query: '',
            results: [],
            filters: {
                sender: '',
                dateFrom: '',
                dateTo: '',
                hasAttachment: false
            }
        },

        // Error states
        errors: {
            emails: null,
            accounts: null,
            compose: null
        }
    },

    // Container references
    dashboardContainer: null,
    inboxContainer: null,
    composeContainer: null,
    threadsContainer: null,
    searchContainer: null,

    // Event cleanup tracking
    eventCleanupFns: [],

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // LIFECYCLE HOOKS (Called by ModuleLoader)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * DASHBOARD LIFECYCLE HOOK
     * Called when: User clicks module button or tab becomes active
     * 
     * @param {object} utilities - Composed utilities from ModuleLoader
     */
    async onDashboardLoad(utilities) {
        // 1. Store utilities (CRITICAL - do this first!)
        Object.assign(this, utilities);
        this.log.info('Communication Hub V4.0 loading...');

        try {
            // 2. Initialize API base URL
            this.state.apiBase = `${window.API_BASE_URL || 'http://localhost:5001'}/api/communication-hub`;
            this.log.info(`API Base: ${this.state.apiBase}`);

            // 3. Get dashboard container
            this.dashboardContainer = this.dom.getContainer();
            if (!this.dashboardContainer) {
                throw new Error('Dashboard container not found');
            }

            // 4. Load saved preferences from localStorage
            this.loadPreferences();

            // 5. Render dashboard structure (synchronous)
            this.renderDashboard();

            // 6. Setup event listeners
            this.setupDashboardEvents();

            // 7. Load connected accounts (asynchronous)
            await this.loadAccounts();

            // 8. Initialize sub-tabs
            this.initializeSubTabs();

            // 8.5. Load thread assignments from backend
            await this.loadThreadAssignments();

            // 8.6. Auto-load 50 emails on initialization
            this.log.info('Auto-loading 50 emails on tab open...');
            await this.loadEmails();

            // 9. Setup drag-and-drop
            this.setupDragAndDrop();

            // 10. Setup context menu
            this.setupContextMenu();

            // 11. Expose globally for onclick handlers
            window.CommunicationHub = this;
            this.log.debug('Exposed CommunicationHub globally for onclick handlers');

            // 12. Emit event for other modules
            this.events.emit('communication-hub:loaded', {
                timestamp: Date.now(),
                accountCount: this.state.accounts.length
            });

            this.log.success('Communication Hub loaded successfully');

        } catch (error) {
            this.log.error('Failed to load dashboard', error);
            this.showError('Failed to load Communication Hub. Please refresh the page.');
            throw error;
        }
    },

    /**
     * CLEANUP LIFECYCLE HOOK
     * Called when: Module is unloaded or page refreshed
     */
    async onUnload() {
        this.log.info('Unloading Communication Hub...');

        try {
            // 1. Save preferences
            this.savePreferences();

            // 2. Clean up Tabulator table
            if (this.state.tabulatorTable) {
                this.state.tabulatorTable.destroy();
                this.state.tabulatorTable = null;
            }

            // 3. Clean up all event listeners (framework handles most, but we do custom ones)
            this.eventCleanupFns.forEach(cleanup => {
                try {
                    cleanup();
                } catch (error) {
                    this.log.warn('Failed to cleanup event listener', error);
                }
            });
            this.eventCleanupFns = [];

            // 4. Remove context menu
            if (this.state.contextMenu) {
                this.state.contextMenu.remove();
                this.state.contextMenu = null;
            }

            // 5. Clear references
            this.dashboardContainer = null;
            this.inboxContainer = null;
            this.composeContainer = null;
            this.threadsContainer = null;
            this.searchContainer = null;

            // 6. Reset state
            this.state.emails = [];
            this.state.selectedEmails.clear();
            this.state.emailTags = {};

            // 7. Emit cleanup event
            this.events.emit('communication-hub:unloaded', {
                timestamp: Date.now()
            });

            this.log.success('Module unloaded successfully');

        } catch (error) {
            this.log.error('Error during unload', error);
        }
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // RENDERING (Dashboard Structure)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Render main dashboard structure with sub-tabs
     */
    renderDashboard() {
        this.log.info('Rendering dashboard structure...');

        const html = `
            <div class="dashboard-wrapper" style="height: 100%; display: flex; flex-direction: column;">
                <!-- Dashboard Header -->
                <div class="dashboard-header">
                    <div class="dashboard-header-left">
                        <h2 class="dashboard-title">
                            <i class="fas fa-comments"></i>
                            Communication Hub
                        </h2>
                        <div class="dashboard-stats" style="display: flex; gap: 20px; margin-top: 8px;">
                            <!-- Metrics moved from stats-grid -->
                            <div class="stat-card" style="display: flex; align-items: center; gap: 10px; padding: 8px 16px; background: rgba(99, 102, 241, 0.1); border-radius: 6px;">
                                <div class="stat-icon primary" style="width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; background: #6366f1; border-radius: 6px;">
                                    <i class="fas fa-envelope" style="color: white; font-size: 14px;"></i>
                                </div>
                                <div class="stat-content">
                                    <div class="stat-label" style="font-size: 11px; color: #8b949e; text-transform: uppercase;">Total Emails</div>
                                    <div class="stat-value" id="total-emails-count" style="font-size: 18px; font-weight: 600; color: #f0f6fc;">-</div>
                                </div>
                            </div>
                            <div class="stat-card" style="display: flex; align-items: center; gap: 10px; padding: 8px 16px; background: rgba(34, 197, 94, 0.1); border-radius: 6px;">
                                <div class="stat-icon success" style="width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; background: #22c55e; border-radius: 6px;">
                                    <i class="fab fa-google" style="color: white; font-size: 14px;"></i>
                                </div>
                                <div class="stat-content">
                                    <div class="stat-label" style="font-size: 11px; color: #8b949e; text-transform: uppercase;">Gmail</div>
                                    <div class="stat-value" id="gmail-count" style="font-size: 18px; font-weight: 600; color: #f0f6fc;">-</div>
                                </div>
                            </div>
                            <div class="stat-card" style="display: flex; align-items: center; gap: 10px; padding: 8px 16px; background: rgba(59, 130, 246, 0.1); border-radius: 6px;">
                                <div class="stat-icon info" style="width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; background: #3b82f6; border-radius: 6px;">
                                    <i class="fab fa-microsoft" style="color: white; font-size: 14px;"></i>
                                </div>
                                <div class="stat-content">
                                    <div class="stat-label" style="font-size: 11px; color: #8b949e; text-transform: uppercase;">Outlook</div>
                                    <div class="stat-value" id="outlook-count" style="font-size: 18px; font-weight: 600; color: #f0f6fc;">-</div>
                                </div>
                            </div>
                            <div class="stat-card" style="display: flex; align-items: center; gap: 10px; padding: 8px 16px; background: rgba(251, 191, 36, 0.1); border-radius: 6px;">
                                <div class="stat-icon warning" style="width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; background: #fbbf24; border-radius: 6px;">
                                    <i class="fas fa-envelope-open" style="color: white; font-size: 14px;"></i>
                                </div>
                                <div class="stat-content">
                                    <div class="stat-label" style="font-size: 11px; color: #8b949e; text-transform: uppercase;">Unread</div>
                                    <div class="stat-value" id="unread-count" style="font-size: 18px; font-weight: 600; color: #f0f6fc;">-</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="dashboard-header-right">
                        <button class="dashboard-action-btn" onclick="window.communicationHub.refreshInbox()" title="Refresh inbox">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                        <button class="dashboard-action-btn dashboard-primary" onclick="window.communicationHub.openCompose()" title="Compose message">
                            <i class="fas fa-pen"></i>
                        </button>
                    </div>
                </div>

                <!-- Quick Nav Bar (for subtabs) -->
                <div class="quick-nav-bar" style="padding: 0 16px;">
                    <div class="quick-nav-container" style="display: flex; gap: 0;">
                        <button class="module-subtab-btn active" data-subtab="unified-inbox" 
                                style="padding: 12px 20px; background: transparent; border: none; border-bottom: 2px solid #6366f1; color: #f0f6fc; cursor: pointer; font-size: 14px;">
                            <i class="fas fa-inbox"></i> Unified Inbox
                        </button>
                        <!-- COMMENTED OUT - Not fully implemented yet
                        <button class="module-subtab-btn" data-subtab="compose" 
                                style="padding: 12px 20px; background: transparent; border: none; border-bottom: 2px solid transparent; color: #8b949e; cursor: pointer; font-size: 14px;">
                            <i class="fas fa-pen"></i> Compose
                        </button>
                        <button class="module-subtab-btn" data-subtab="threads" 
                                style="padding: 12px 20px; background: transparent; border: none; border-bottom: 2px solid transparent; color: #8b949e; cursor: pointer; font-size: 14px;">
                            <i class="fas fa-comments"></i> Threads
                        </button>
                        <button class="module-subtab-btn" data-subtab="search" 
                                style="padding: 12px 20px; background: transparent; border: none; border-bottom: 2px solid transparent; color: #8b949e; cursor: pointer; font-size: 14px;">
                            <i class="fas fa-search"></i> Search
                        </button>
                        -->
                    </div>
                </div>
                
                <!-- Content Containers -->
                <div class="module-subtabs-content" style="flex: 1; overflow: auto; margin-top: 10px;">
                    <div class="module-subtab-content active" id="communication-hub-subtab-unified-inbox" data-subtab="unified-inbox"></div>
                    <div class="module-subtab-content" id="communication-hub-subtab-compose" data-subtab="compose" style="display: none;"></div>
                    <div class="module-subtab-content" id="communication-hub-subtab-threads" data-subtab="threads" style="display: none;"></div>
                    <div class="module-subtab-content" id="communication-hub-subtab-search" data-subtab="search" style="display: none;"></div>
                </div>
            </div>
        `;

        this.dom.injectHTML(this.dashboardContainer, html);
        this.log.debug('Dashboard structure rendered');
    },

    /**
     * Helper method: Refresh inbox (called from header button)
     */
    refreshInbox() {
        this.log.info('Refreshing inbox...');
        // Switch to inbox tab if not already there
        const inboxBtn = document.querySelector('[data-subtab="unified-inbox"]');
        if (inboxBtn && !inboxBtn.classList.contains('active')) {
            inboxBtn.click();
        }
        // Reload inbox content
        if (this.inboxContainer) {
            this.renderUnifiedInbox();
        }
    },

    /**
     * Helper method: Open compose (called from header button)
     */
    openCompose() {
        this.log.info('Opening compose...');
        // Switch to compose tab
        const composeBtn = document.querySelector('[data-subtab="compose"]');
        if (composeBtn) {
            composeBtn.click();
        }
    },

    /**
     * Initialize all sub-tabs
     */
    initializeSubTabs() {
        this.log.info('Initializing sub-tabs...');

        // Get container references
        this.inboxContainer = document.getElementById('communication-hub-subtab-unified-inbox');
        this.composeContainer = document.getElementById('communication-hub-subtab-compose');
        this.threadsContainer = document.getElementById('communication-hub-subtab-threads');
        this.searchContainer = document.getElementById('communication-hub-subtab-search');

        // Render each sub-tab content
        this.renderUnifiedInbox();
        this.renderCompose();
        this.renderThreads();
        this.renderSearch();

        this.log.debug('All sub-tabs initialized');
    },

    /**
     * Render Unified Inbox tab
     */
    renderUnifiedInbox() {
        if (!this.inboxContainer) {
            this.log.error('Inbox container not found');
            return;
        }

        this.log.debug('Rendering Unified Inbox...');

        const html = `
            <div class="module-dashboard">
                <!-- Toolbar -->
                ${this.renderToolbar()}
                
                <!-- Email Table Card -->
                <div class="dashboard-card">
                    <div class="card-header">
                        <h3 class="card-title">
                            <i class="fas fa-list"></i> Email Messages
                        </h3>
                    </div>
                    <div class="card-content">
                        <!-- Ready State -->
                        <div id="inbox-ready" class="ready-state" style="text-align: center; padding: 40px; color: var(--text-secondary, #9ca3af);">
                            <i class="fas fa-info-circle" style="font-size: 32px; color: #4ec9b0; margin-bottom: 10px; display: block;"></i>
                            <p style="margin: 0; font-size: 16px;">Click the <strong>Refresh</strong> button to load your emails</p>
                            <p style="margin: 5px 0 0 0; font-size: 12px; color: var(--text-secondary, #6b7280);">Select account filter and click Refresh</p>
                        </div>
                        
                        <!-- Loading State -->
                        <div id="inbox-loading" class="loading-state" style="display: none; text-align: center; padding: 40px;">
                            <i class="fas fa-spinner fa-spin" style="font-size: 32px; color: var(--primary-color, #0078d4); margin-bottom: 10px; display: block;"></i>
                            <p style="margin: 0; font-size: 16px; color: var(--text-primary, #e5e7eb);">Loading emails...</p>
                        </div>
                        
                        <!-- Table Container -->
                        <div id="email-table-container" style="display: none; min-height: 500px;"></div>
                    </div>
                </div>
                
                <!-- Email Preview Panel (Slide-out) -->
                <div id="emailPreview" class="email-preview-panel" style="display: none;">
                    <div class="email-preview-header">
                        <div class="email-preview-title">
                            <i class="fas fa-envelope"></i>
                            Email Preview
                        </div>
                        <button class="synergy-icon-btn" data-action="close-preview" title="Close preview">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div id="previewContent" class="email-preview-body"></div>
                </div>
            </div>
        `;

        this.dom.injectHTML(this.inboxContainer, html);
    },

    /**
     * Render toolbar with filters and actions
     */
    renderToolbar() {
        return `
            <div class="filters-bar" style="margin: 15px 20px; padding: 12px; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; display: flex; gap: 15px; flex-wrap: wrap; align-items: center;">
                <!-- Read/Unread Filter -->
                <div class="filter-group" style="display: flex; align-items: center; gap: 8px;">
                    <label style="color: #8b949e; font-size: 0.9em; font-weight: 600;"><i class="fas fa-envelope"></i> Status:</label>
                    <select id="status-selector" class="filter-select" style="padding: 6px 12px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6; font-size: 0.9em;">
                        <option value="all">All Emails</option>
                        <option value="unread">Unread Only</option>
                        <option value="read">Read Only</option>
                    </select>
                </div>
                
                <!-- Account Filter -->
                <div class="filter-group" style="display: flex; align-items: center; gap: 8px;">
                    <label style="color: #8b949e; font-size: 0.9em; font-weight: 600;"><i class="fas fa-at"></i> Account:</label>
                    <select id="accountSelector" class="filter-select" style="padding: 6px 12px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6; font-size: 0.9em;">
                        <option value="all">All Accounts</option>
                        <option value="gmail">Gmail Only</option>
                        <option value="outlook">Outlook Only</option>
                    </select>
                </div>
                
                <!-- Thread Filter -->
                <div class="filter-group" style="display: flex; align-items: center; gap: 8px;">
                    <label style="color: #8b949e; font-size: 0.9em; font-weight: 600;"><i class="fas fa-comments"></i> Threads:</label>
                    <select id="thread-selector" class="filter-select" style="padding: 6px 12px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6; font-size: 0.9em;">
                        <option value="all">All Emails</option>
                        <option value="threaded">Threaded Only</option>
                        <option value="single">Single Emails</option>
                    </select>
                </div>
                
                <!-- Search Input -->
                <div class="filter-group" style="flex: 1; display: flex; align-items: center; gap: 8px;">
                    <label style="color: #8b949e; font-size: 0.9em; font-weight: 600;"><i class="fas fa-search"></i> Search:</label>
                    <input type="text" id="email-search-input" class="filter-input" placeholder="Search sender, subject, content..." style="flex: 1; padding: 6px 12px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6; font-size: 0.9em;">
                </div>
                
                <!-- Limit Selector -->
                <div class="filter-group" style="display: flex; align-items: center; gap: 8px;">
                    <label style="color: #8b949e; font-size: 0.9em; font-weight: 600;"><i class="fas fa-list"></i> Show:</label>
                    <select id="email-limit" class="filter-select" style="padding: 6px 12px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6; font-size: 0.9em;">
                        <option value="20" selected>20 emails</option>
                        <option value="50">50 emails</option>
                        <option value="100">100 emails</option>
                    </select>
                </div>
                
                <!-- Refresh Button -->
                <div class="filter-group" style="display: flex; align-items: center; gap: 8px;">
                    <button id="email-refresh-btn" class="btn-secondary" style="padding: 6px 14px; background: #0d1117; border: 2px solid #3b82f6; color: #3b82f6; border-radius: 6px; cursor: pointer; font-size: 0.9em; display: flex; align-items: center; gap: 6px; transition: all 0.2s;">
                        <i class="fas fa-sync"></i> Refresh
                    </button>
                </div>
                
                <!-- Selected Count -->
                <div class="filter-group" style="display: flex; align-items: center;">
                    <span id="selected-count" style="color: #6e7681; font-size: 0.85em;">Selected: <span class="count-value">0</span></span>
                </div>
            </div>
        `;
    },

    /**
     * Render Compose tab - Full email composition interface
     */
    renderCompose() {
        if (!this.composeContainer) {
            this.log.warn('Compose container not found');
            return;
        }
        if (!this.dom || !this.dom.injectHTML) {
            this.log.error('DOM utilities not available');
            return;
        }

        try {
            const accountOptions = this.state.accounts.map(acc =>
                `<option value="${acc.provider}">${acc.email} (${acc.provider})</option>`
            ).join('');

            const html = `
                <div class="module-dashboard">
                    <!-- Compose Header -->
                    <div class="dashboard-card">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="fas fa-pen"></i> Compose New Email
                            </h3>
                            <div style="display: flex; gap: 8px;">
                                <button class="btn btn-secondary" id="compose-save-draft">
                                    <i class="fas fa-save"></i> Save Draft
                                </button>
                                <button class="btn btn-primary" id="compose-send">
                                    <i class="fas fa-paper-plane"></i> Send Email
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Compose Form -->
                    <div class="dashboard-card" style="margin-top: 20px;">
                        <div class="card-content">
                            <!-- Account Selection -->
                            <div class="form-group" style="margin-bottom: 16px;">
                                <label style="display: block; margin-bottom: 6px; color: var(--text-primary); font-weight: 500;">
                                    <i class="fas fa-user"></i> From Account:
                                </label>
                                <select id="compose-account" class="form-control" style="width: 100%; padding: 10px; background: var(--bg-card); border: 1px solid var(--border-default); border-radius: 6px; color: var(--text-primary);">
                                    <option value="">Select account...</option>
                                    ${accountOptions}
                                </select>
                            </div>

                            <!-- To Field -->
                            <div class="form-group" style="margin-bottom: 16px;">
                                <label style="display: block; margin-bottom: 6px; color: var(--text-primary); font-weight: 500;">
                                    <i class="fas fa-envelope"></i> To:
                                </label>
                                <input type="text" id="compose-to" class="form-control" placeholder="recipient@example.com (separate multiple with commas)" 
                                       style="width: 100%; padding: 10px; background: var(--bg-card); border: 1px solid var(--border-default); border-radius: 6px; color: var(--text-primary);">
                            </div>

                            <!-- CC/BCC Toggle -->
                            <div style="margin-bottom: 16px;">
                                <button class="btn btn-sm" id="compose-toggle-cc" style="padding: 4px 12px; font-size: 12px;">
                                    <i class="fas fa-plus"></i> CC
                                </button>
                                <button class="btn btn-sm" id="compose-toggle-bcc" style="padding: 4px 12px; font-size: 12px; margin-left: 6px;">
                                    <i class="fas fa-plus"></i> BCC
                                </button>
                            </div>

                            <!-- CC Field (Hidden by default) -->
                            <div class="form-group" id="compose-cc-group" style="margin-bottom: 16px; display: none;">
                                <label style="display: block; margin-bottom: 6px; color: var(--text-primary); font-weight: 500;">
                                    <i class="fas fa-envelope"></i> CC:
                                </label>
                                <input type="text" id="compose-cc" class="form-control" placeholder="cc@example.com" 
                                       style="width: 100%; padding: 10px; background: var(--bg-card); border: 1px solid var(--border-default); border-radius: 6px; color: var(--text-primary);">
                            </div>

                            <!-- BCC Field (Hidden by default) -->
                            <div class="form-group" id="compose-bcc-group" style="margin-bottom: 16px; display: none;">
                                <label style="display: block; margin-bottom: 6px; color: var(--text-primary); font-weight: 500;">
                                    <i class="fas fa-envelope"></i> BCC:
                                </label>
                                <input type="text" id="compose-bcc" class="form-control" placeholder="bcc@example.com" 
                                       style="width: 100%; padding: 10px; background: var(--bg-card); border: 1px solid var(--border-default); border-radius: 6px; color: var(--text-primary);">
                            </div>

                            <!-- Subject Field -->
                            <div class="form-group" style="margin-bottom: 16px;">
                                <label style="display: block; margin-bottom: 6px; color: var(--text-primary); font-weight: 500;">
                                    <i class="fas fa-heading"></i> Subject:
                                </label>
                                <input type="text" id="compose-subject" class="form-control" placeholder="Email subject" 
                                       style="width: 100%; padding: 10px; background: var(--bg-card); border: 1px solid var(--border-default); border-radius: 6px; color: var(--text-primary);">
                            </div>

                            <!-- Body Field -->
                            <div class="form-group" style="margin-bottom: 16px;">
                                <label style="display: block; margin-bottom: 6px; color: var(--text-primary); font-weight: 500;">
                                    <i class="fas fa-align-left"></i> Message:
                                </label>
                                <textarea id="compose-body" class="form-control" rows="12" placeholder="Type your message here..." 
                                          style="width: 100%; padding: 12px; background: var(--bg-card); border: 1px solid var(--border-default); border-radius: 6px; color: var(--text-primary); font-family: inherit; resize: vertical;"></textarea>
                            </div>

                            <!-- Attachments -->
                            <div class="form-group" style="margin-bottom: 16px;">
                                <label style="display: block; margin-bottom: 6px; color: var(--text-primary); font-weight: 500;">
                                    <i class="fas fa-paperclip"></i> Attachments:
                                </label>
                                <input type="file" id="compose-attachments" multiple class="form-control" 
                                       style="padding: 10px; background: var(--bg-card); border: 1px solid var(--border-default); border-radius: 6px; color: var(--text-primary);">
                                <div id="compose-attachment-list" style="margin-top: 10px;"></div>
                            </div>

                            <!-- Reply Context (if replying) -->
                            <div id="compose-reply-context" style="display: none; margin-top: 20px; padding: 16px; background: var(--bg-secondary); border-left: 3px solid var(--primary-color); border-radius: 6px;">
                                <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">In reply to:</div>
                                <div id="compose-reply-original" style="color: var(--text-secondary); font-size: 13px; max-height: 200px; overflow-y: auto;"></div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            this.dom.injectHTML(this.composeContainer, html);
            this.setupComposeEvents();
            this.log.debug('Compose tab rendered');
        } catch (error) {
            this.log.error('Failed to render Compose tab', error);
        }
    },

    /**
     * Render Threads tab - Show email-to-thread assignments
     */
    renderThreads() {
        if (!this.threadsContainer) {
            this.log.warn('Threads container not found');
            return;
        }
        if (!this.dom || !this.dom.injectHTML) {
            this.log.error('DOM utilities not available');
            return;
        }

        try {
            const html = `
                <div class="module-dashboard">
                    <!-- Threads Header -->
                    <div class="dashboard-card">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="fas fa-comments"></i> Email Thread Assignments
                            </h3>
                            <div style="display: flex; gap: 8px;">
                                <button class="btn btn-secondary" id="threads-refresh">
                                    <i class="fas fa-sync-alt"></i> Refresh
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Stats Cards -->
                    <div class="stats-grid" style="margin-top: 20px;">
                        <div class="stat-card">
                            <div class="stat-icon primary">
                                <i class="fas fa-link"></i>
                            </div>
                            <div class="stat-content">
                                <div class="stat-label">Assigned Emails</div>
                                <div class="stat-value" id="threads-assigned-count">0</div>
                            </div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon success">
                                <i class="fas fa-comments"></i>
                            </div>
                            <div class="stat-content">
                                <div class="stat-label">Active Threads</div>
                                <div class="stat-value" id="threads-active-count">0</div>
                            </div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon warning">
                                <i class="fas fa-envelope-open"></i>
                            </div>
                            <div class="stat-content">
                                <div class="stat-label">Unassigned</div>
                                <div class="stat-value" id="threads-unassigned-count">0</div>
                            </div>
                        </div>
                    </div>

                    <!-- Thread List -->
                    <div class="dashboard-card" style="margin-top: 20px;">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="fas fa-list"></i> Thread Assignments
                            </h3>
                        </div>
                        <div class="card-content">
                            <!-- Loading State -->
                            <div id="threads-loading" style="display: none; text-align: center; padding: 40px;">
                                <i class="fas fa-spinner fa-spin" style="font-size: 32px; color: var(--primary-color); margin-bottom: 10px; display: block;"></i>
                                <p style="margin: 0; font-size: 16px; color: var(--text-primary);">Loading thread assignments...</p>
                            </div>

                            <!-- Threads Table -->
                            <div id="threads-table-container" style="min-height: 400px;"></div>
                        </div>
                    </div>
                </div>
            `;

            this.dom.injectHTML(this.threadsContainer, html);
            this.setupThreadsEvents();
            this.renderThreadsTable();
            this.log.debug('Threads tab rendered');
        } catch (error) {
            this.log.error('Failed to render Threads tab', error);
        }
    },

    /**
     * Render Search tab - Full-text email search
     */
    renderSearch() {
        if (!this.searchContainer) {
            this.log.warn('Search container not found');
            return;
        }
        if (!this.dom || !this.dom.injectHTML) {
            this.log.error('DOM utilities not available');
            return;
        }

        try {
            const html = `
                <div class="module-dashboard">
                    <!-- Search Header -->
                    <div class="dashboard-card">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="fas fa-search"></i> Search Emails
                            </h3>
                        </div>
                    </div>

                    <!-- Search Form -->
                    <div class="dashboard-card" style="margin-top: 20px;">
                        <div class="card-content">
                            <!-- Main Search -->
                            <div class="form-group" style="margin-bottom: 16px;">
                                <label style="display: block; margin-bottom: 6px; color: var(--text-primary); font-weight: 500;">
                                    <i class="fas fa-search"></i> Search Query:
                                </label>
                                <div style="display: flex; gap: 8px;">
                                    <input type="text" id="search-query" class="form-control" placeholder="Search subject, sender, or body..." 
                                           style="flex: 1; padding: 10px; background: var(--bg-card); border: 1px solid var(--border-default); border-radius: 6px; color: var(--text-primary);">
                                    <button class="btn btn-primary" id="search-submit" style="padding: 10px 20px;">
                                        <i class="fas fa-search"></i> Search
                                    </button>
                                    <button class="btn btn-secondary" id="search-clear" style="padding: 10px 20px;">
                                        <i class="fas fa-times"></i> Clear
                                    </button>
                                </div>
                            </div>

                            <!-- Advanced Filters Toggle -->
                            <div style="margin-bottom: 16px;">
                                <button class="btn btn-sm" id="search-toggle-filters" style="padding: 6px 12px; font-size: 12px;">
                                    <i class="fas fa-filter"></i> Advanced Filters
                                </button>
                            </div>

                            <!-- Advanced Filters (Hidden by default) -->
                            <div id="search-filters" style="display: none; padding: 16px; background: var(--bg-secondary); border-radius: 6px; margin-bottom: 16px;">
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px;">
                                    <!-- Sender Filter -->
                                    <div class="form-group">
                                        <label style="display: block; margin-bottom: 6px; color: var(--text-primary); font-size: 13px;">
                                            <i class="fas fa-user"></i> From:
                                        </label>
                                        <input type="text" id="search-filter-sender" class="form-control" placeholder="sender@example.com" 
                                               style="width: 100%; padding: 8px; background: var(--bg-card); border: 1px solid var(--border-default); border-radius: 4px; color: var(--text-primary);">
                                    </div>

                                    <!-- Date From -->
                                    <div class="form-group">
                                        <label style="display: block; margin-bottom: 6px; color: var(--text-primary); font-size: 13px;">
                                            <i class="fas fa-calendar"></i> From Date:
                                        </label>
                                        <input type="date" id="search-filter-date-from" class="form-control" 
                                               style="width: 100%; padding: 8px; background: var(--bg-card); border: 1px solid var(--border-default); border-radius: 4px; color: var(--text-primary);">
                                    </div>

                                    <!-- Date To -->
                                    <div class="form-group">
                                        <label style="display: block; margin-bottom: 6px; color: var(--text-primary); font-size: 13px;">
                                            <i class="fas fa-calendar"></i> To Date:
                                        </label>
                                        <input type="date" id="search-filter-date-to" class="form-control" 
                                               style="width: 100%; padding: 8px; background: var(--bg-card); border: 1px solid var(--border-default); border-radius: 4px; color: var(--text-primary);">
                                    </div>

                                    <!-- Has Attachment -->
                                    <div class="form-group">
                                        <label style="display: block; margin-bottom: 6px; color: var(--text-primary); font-size: 13px;">
                                            <i class="fas fa-paperclip"></i> Attachments:
                                        </label>
                                        <select id="search-filter-attachment" class="form-control" 
                                                style="width: 100%; padding: 8px; background: var(--bg-card); border: 1px solid var(--border-default); border-radius: 4px; color: var(--text-primary);">
                                            <option value="">Any</option>
                                            <option value="true">Has attachments</option>
                                            <option value="false">No attachments</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <!-- Search Tips -->
                            <div style="padding: 12px; background: var(--bg-secondary); border-left: 3px solid var(--primary-color); border-radius: 4px; font-size: 13px; color: var(--text-secondary);">
                                <div style="font-weight: 500; margin-bottom: 6px; color: var(--text-primary);">Search Tips:</div>
                                <ul style="margin: 0; padding-left: 20px;">
                                    <li>Use quotes for exact phrases: "meeting tomorrow"</li>
                                    <li>Search is case-insensitive</li>
                                    <li>Use advanced filters for precise results</li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    <!-- Search Results -->
                    <div class="dashboard-card" style="margin-top: 20px;">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="fas fa-list"></i> Search Results <span id="search-result-count" style="color: var(--text-secondary); font-size: 14px; font-weight: normal;"></span>
                            </h3>
                        </div>
                        <div class="card-content">
                            <!-- No Results -->
                            <div id="search-no-results" style="text-align: center; padding: 40px; color: var(--text-secondary);">
                                <i class="fas fa-search" style="font-size: 32px; margin-bottom: 10px; display: block;"></i>
                                <p style="margin: 0;">Enter a search query to find emails</p>
                            </div>

                            <!-- Loading State -->
                            <div id="search-loading" style="display: none; text-align: center; padding: 40px;">
                                <i class="fas fa-spinner fa-spin" style="font-size: 32px; color: var(--primary-color); margin-bottom: 10px; display: block;"></i>
                                <p style="margin: 0; font-size: 16px; color: var(--text-primary);">Searching...</p>
                            </div>

                            <!-- Results Table -->
                            <div id="search-results-container" style="display: none; min-height: 400px;"></div>
                        </div>
                    </div>
                </div>
            `;

            this.dom.injectHTML(this.searchContainer, html);
            this.setupSearchEvents();
            this.log.debug('Search tab rendered');
        } catch (error) {
            this.log.error('Failed to render Search tab', error);
        }
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // EVENT HANDLING
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Setup dashboard event listeners
     */
    setupDashboardEvents() {
        this.log.info('Setting up dashboard events...');

        // Sub-tab navigation
        const nav = this.dashboardContainer.querySelector('.quick-nav-bar');
        if (nav) {
            this.dom.on(nav, 'click', '.module-subtab-btn', (e) => {
                const tabId = e.currentTarget.dataset.subtab;
                this.switchSubTab(tabId);
            });
        }

        // Wait for toolbar to be rendered in DOM
        setTimeout(() => {
            this.setupToolbarEvents();
        }, 100);
    },

    /**
     * Setup toolbar event listeners (called after DOM is ready)
     */
    setupToolbarEvents() {
        this.log.info('Setting up toolbar events...');

        // Toolbar actions - look for filters-bar (the actual toolbar class)
        const toolbar = this.dashboardContainer.querySelector('.filters-bar');
        if (!toolbar) {
            // Limit retries to prevent infinite loop
            if (!this.toolbarRetryCount) this.toolbarRetryCount = 0;
            this.toolbarRetryCount++;

            if (this.toolbarRetryCount < 10) {
                this.log.warn(`Toolbar not found, retry ${this.toolbarRetryCount}/10 in 200ms...`);
                setTimeout(() => this.setupToolbarEvents(), 200);
            } else {
                this.log.error('Toolbar setup failed after 10 retries - toolbar may not exist in current tab');
            }
            return;
        }

        // Reset retry counter on success
        this.toolbarRetryCount = 0;

        if (toolbar) {
            // Tag buttons
            this.dom.on(toolbar, 'click', '[data-action="tag-clear"]', () => this.tagSelectedEmails('clear'));
            this.dom.on(toolbar, 'click', '[data-action="tag-green"]', () => this.tagSelectedEmails('green'));
            this.dom.on(toolbar, 'click', '[data-action="tag-orange"]', () => this.tagSelectedEmails('orange'));
            this.dom.on(toolbar, 'click', '[data-action="tag-red"]', () => this.tagSelectedEmails('red'));

            // Export buttons
            this.dom.on(toolbar, 'click', '[data-action="export-excel"]', () => this.exportEmails('excel'));
            this.dom.on(toolbar, 'click', '[data-action="export-csv"]', () => this.exportEmails('csv'));
            this.dom.on(toolbar, 'click', '[data-action="export-pdf"]', () => this.exportEmails('pdf'));

            // Send to AI - Show dropdown to select destination column
            this.dom.on(toolbar, 'click', '[data-action="send-to-ai"]', (e) => this.showAIDestinationDropdown(e));

            // Refresh button - use both delegation and direct listener
            this.dom.on(toolbar, 'click', '[data-action="refresh"]', (e) => {
                this.log.info('🔄 Refresh button clicked (delegated)');
                e.preventDefault();
                e.stopPropagation();
                this.refreshInbox();
            });

            // Direct listener on refresh button as backup
            const refreshBtn = document.getElementById('email-refresh-btn');
            if (refreshBtn) {
                this.log.info('✅ Refresh button found, attaching direct listener');
                const clickHandler = (e) => {
                    this.log.info('🔄 Refresh button clicked (direct listener)');
                    e.preventDefault();
                    e.stopPropagation();
                    this.refreshInbox();
                };
                refreshBtn.addEventListener('click', clickHandler);
                // Track for cleanup
                this.eventCleanupFns.push(() => {
                    refreshBtn.removeEventListener('click', clickHandler);
                });
            } else {
                this.log.error('❌ Refresh button (#email-refresh-btn) not found in DOM!');
            }

            // Account filter
            const accountSelector = document.getElementById('accountSelector');
            if (accountSelector) {
                this.dom.on(accountSelector, 'change', (e) => {
                    this.state.currentAccountFilter = e.target.value;
                    this.log.debug(`Account filter changed: ${e.target.value}`);
                });
            }

            // Email limit
            const emailLimit = document.getElementById('email-limit');
            if (emailLimit) {
                this.dom.on(emailLimit, 'change', (e) => {
                    this.state.currentEmailLimit = parseInt(e.target.value);
                    this.log.debug(`Email limit changed: ${e.target.value}`);
                });
            }
        }

        // Preview close button
        this.dom.on(this.dashboardContainer, 'click', '[data-action="close-preview"]', () => {
            this.closePreview();
        });

        this.log.debug('Dashboard events setup complete');
    },

    /**
     * Switch between sub-tabs
     */
    switchSubTab(tabId) {
        this.log.debug(`Switching to tab: ${tabId}`);

        const wrapper = this.dashboardContainer.querySelector('.dashboard-wrapper');
        if (!wrapper) {
            this.log.error('Dashboard wrapper not found');
            return;
        }

        // Update button states
        wrapper.querySelectorAll('.module-subtab-btn').forEach(btn => {
            if (btn.dataset.subtab === tabId) {
                btn.classList.add('active');
                btn.style.borderBottomColor = '#6366f1';
                btn.style.color = '#f0f6fc';
            } else {
                btn.classList.remove('active');
                btn.style.borderBottomColor = 'transparent';
                btn.style.color = '#8b949e';
            }
        });

        // CRITICAL FIX: Proper hide/show with complete visibility control
        wrapper.querySelectorAll('.module-subtab-content').forEach(content => {
            if (content.dataset.subtab === tabId) {
                // Show target tab
                content.classList.add('active');
                content.style.display = 'block';
                content.style.visibility = 'visible';
                content.style.opacity = '1';
                content.style.position = 'relative';
            } else {
                // Hide other tabs completely
                content.classList.remove('active');
                content.style.display = 'none';
                content.style.visibility = 'hidden';
                content.style.opacity = '0';
                content.style.position = 'absolute';
            }
        });

        // Trigger layout recalculation for Tabulator when returning to inbox
        if (tabId === 'unified-inbox' && this.state.tabulatorTable) {
            setTimeout(() => {
                this.state.tabulatorTable.redraw(true);  // Force full redraw
            }, 50);
        }

        this.state.currentTab = tabId;
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // DATA LOADING
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Load connected email accounts
     */
    async loadAccounts() {
        this.log.info('Loading connected accounts...');
        this.state.loading.accounts = true;
        this.state.errors.accounts = null;

        try {
            // Get authenticated user ID from UserAuth (NOT localStorage)
            const userId = (window.UserAuth && window.UserAuth.user &&
                (window.UserAuth.user.id || window.UserAuth.user.user_id)) || '1';
            const params = { user_id: userId };

            this.log.info(`📬 Fetching accounts for user_id=${userId}`);
            const response = await this.api.get(`${this.state.apiBase}/accounts`, { params });
            this.state.accounts = response.accounts || [];
            this.log.success(`Loaded ${this.state.accounts.length} accounts`);
        } catch (error) {
            this.log.error('Failed to load accounts', error);
            this.state.errors.accounts = error.message;
        } finally {
            this.state.loading.accounts = false;
        }
    },

    /**
     * Refresh inbox - reload emails
     */
    async refreshInbox() {
        this.log.info('🔄 Refresh inbox called');
        this.log.info(`📊 Current state: accountFilter=${this.state.currentAccountFilter}, limit=${this.state.currentEmailLimit}`);

        try {
            await this.loadEmails();
            this.log.success('✅ Refresh complete');
        } catch (error) {
            this.log.error('❌ Refresh failed', error);
            throw error;
        }
    },

    /**
     * Load emails from backend
     */
    async loadEmails() {
        this.log.info('Loading emails...');

        // Show loading state
        this.showLoadingState(true);
        this.state.loading.emails = true;
        this.state.errors.emails = null;

        try {
            // Get authenticated user ID from UserAuth (NOT localStorage)
            const userId = (window.UserAuth && window.UserAuth.user &&
                (window.UserAuth.user.id || window.UserAuth.user.user_id)) || '1';

            const params = {
                user_id: userId,
                account: this.state.currentAccountFilter,
                limit: this.state.currentEmailLimit
            };

            this.log.info(`📧 Fetching emails: user_id=${params.user_id}, account=${params.account}, limit=${params.limit}`);
            this.log.info(`📡 API URL: ${this.state.apiBase}/emails`);

            const response = await this.api.get(`${this.state.apiBase}/emails`, { params });

            this.state.emails = response.emails || [];
            this.log.success(`Loaded ${this.state.emails.length} emails`);

            // Update stats
            this.updateStats();

            // Create/update table
            this.createEmailTable();

        } catch (error) {
            this.log.error('Failed to load emails', error);
            this.state.errors.emails = error.message;
            this.showError(`Failed to load emails: ${error.message}`);
        } finally {
            this.state.loading.emails = false;
            this.showLoadingState(false);
        }
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // EMAIL TABLE (Tabulator Integration)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Create/update Tabulator email table
     */
    createEmailTable() {
        const container = document.getElementById('email-table-container');
        if (!container) {
            this.log.error('Table container not found');
            return;
        }

        // Destroy existing table
        if (this.state.tabulatorTable) {
            this.log.debug('Destroying existing table');
            this.state.tabulatorTable.destroy();
        }

        this.log.info('Creating Tabulator table...');

        // Check if Tabulator is available
        if (typeof Tabulator === 'undefined') {
            this.log.error('Tabulator library not loaded');
            this.showError('Tabulator library not available. Please refresh the page.');
            return;
        }

        // Create table
        this.state.tabulatorTable = new Tabulator(container, {
            data: this.state.emails,
            layout: "fitDataStretch",
            pagination: true,
            paginationSize: this.state.pageSize,
            selectable: true,  // Multi-selection enabled
            selectableRangeMode: "click",  // Click to select/deselect
            columns: [
                {
                    formatter: "rowSelection",
                    titleFormatter: "rowSelection",
                    hozAlign: "center",
                    headerSort: false,
                    width: 40,
                    cellClick: function (e, cell) {
                        cell.getRow().toggleSelect();
                    }
                },
                {
                    title: "Date",
                    field: "date",
                    width: 160,
                    sorter: "datetime",
                    formatter: (cell) => {
                        return this.formatDate(cell.getValue());
                    }
                },
                {
                    title: "Status",
                    field: "is_read",
                    width: 80,
                    hozAlign: "center",
                    headerSort: false,
                    formatter: (cell) => {
                        const isRead = cell.getValue();
                        return isRead
                            ? '<i class="fas fa-envelope-open" style="color: #6b7280;" title="Read"></i>'
                            : '<i class="fas fa-envelope" style="color: #3b82f6;" title="Unread"></i>';
                    }
                },
                {
                    title: "Account",
                    field: "provider",
                    width: 70,
                    hozAlign: "center",
                    headerSort: false,
                    formatter: (cell) => {
                        const provider = cell.getValue();
                        if (provider === 'gmail') {
                            return '<i class="fab fa-google" style="color: #ea4335; font-size: 16px;" title="Gmail"></i>';
                        } else if (provider === 'outlook') {
                            return '<i class="fab fa-microsoft" style="color: #0078d4; font-size: 16px;" title="Outlook"></i>';
                        }
                        return '<i class="fas fa-envelope" style="color: #6b7280;"></i>';
                    }
                },
                {
                    title: "From",
                    field: "from",
                    width: 220,
                    sorter: "string"
                },
                {
                    title: "Subject",
                    field: "subject",
                    sorter: "string",
                    formatter: (cell) => {
                        const value = cell.getValue();
                        const data = cell.getRow().getData();
                        const hasThread = this.state.emailThreads[data.id];

                        // Show thread indicator if email has thread
                        if (hasThread) {
                            return `
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <i class="fas fa-comments" style="color: #6366f1; font-size: 12px;" title="Part of thread"></i>
                                    <span>${this.escapeHtml(value)}</span>
                                </div>
                            `;
                        }

                        return this.escapeHtml(value);
                    }
                },
                {
                    title: "AI Agent",
                    field: "assigned_agent",
                    width: 120,
                    hozAlign: "center",
                    formatter: (cell) => {
                        const agent = cell.getValue();
                        if (agent) {
                            return `<span style="background: #3b82f6; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px;">${this.escapeHtml(agent)}</span>`;
                        }
                        return '<span style="color: #9ca3af; font-size: 11px;">Not assigned</span>';
                    }
                }
            ]
        });

        // Table events
        this.state.tabulatorTable.on("rowSelectionChanged", (data, rows) => {
            this.state.selectedEmails = new Set(rows.map(r => r.getData().id));
            this.updateSelectedCount();
        });

        this.state.tabulatorTable.on("rowClick", (e, row) => {
            this.showEmailPreview(row.getData());
        });

        // Show table, hide ready state
        this.dom.hide(document.getElementById('inbox-ready'));
        this.dom.show(container);

        this.state.tableReady = true;
        this.log.success('Table created successfully');
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // EMAIL ACTIONS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Tag selected emails
     */
    tagSelectedEmails(color) {
        this.log.info(`Tagging ${this.state.selectedEmails.size} emails with: ${color}`);

        this.state.selectedEmails.forEach(emailId => {
            if (color === 'clear') {
                delete this.state.emailTags[emailId];
            } else {
                this.state.emailTags[emailId] = color;
            }
        });

        // Refresh table to show updated tags
        if (this.state.tabulatorTable) {
            this.state.tabulatorTable.redraw();
        }

        this.log.success('Tags updated');
    },

    /**
     * Export emails in specified format
     */
    exportEmails(format) {
        this.log.info(`Exporting emails as ${format}...`);

        if (!this.state.tabulatorTable) {
            this.log.warn('No table to export');
            return;
        }

        try {
            switch (format) {
                case 'excel':
                    this.state.tabulatorTable.download("xlsx", `emails_${Date.now()}.xlsx`);
                    break;
                case 'csv':
                    this.state.tabulatorTable.download("csv", `emails_${Date.now()}.csv`);
                    break;
                case 'pdf':
                    this.state.tabulatorTable.download("pdf", `emails_${Date.now()}.pdf`, {
                        orientation: "landscape",
                        title: "Email Export"
                    });
                    break;
            }
            this.log.success(`Export ${format} initiated`);
        } catch (error) {
            this.log.error(`Export failed: ${error.message}`);
            this.showError(`Export failed: ${error.message}`);
        }
    },

    /**
     * Send selected emails to AI agents
     */
    /**
     * Show dropdown to select AI destination (Prime or Agent columns)
     */
    showAIDestinationDropdown(event) {
        if (this.state.selectedEmails.size === 0) {
            this.log.warn('No emails selected');
            return;
        }

        event.preventDefault();
        event.stopPropagation();

        // Remove any existing dropdown
        document.querySelectorAll('.email-ai-destination-dropdown').forEach(d => d.remove());

        const button = event.currentTarget;
        const dropdown = document.createElement('div');
        dropdown.className = 'email-ai-destination-dropdown';
        dropdown.style.cssText = `
            position: absolute;
            top: calc(100% + 4px);
            left: 0;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            min-width: 180px;
            overflow: hidden;
        `;

        // Get available AI destinations
        const destinations = [];

        // Add AI Prime
        const primeInput = document.getElementById('ai-chat-input');
        if (primeInput) {
            destinations.push({
                id: 'prime',
                name: 'AI Prime',
                icon: 'fas fa-star',
                color: '#0078d4'
            });
        }

        // Get active agent columns
        const agentColumns = document.querySelectorAll('.agent-column-container');
        agentColumns.forEach((col, index) => {
            const titleEl = col.querySelector('.agent-column-title');
            const inputEl = col.querySelector('.agent-column-input');
            if (titleEl && inputEl && !col.classList.contains('disabled')) {
                destinations.push({
                    id: `agent-${index + 1}`,
                    name: titleEl.textContent.trim() || `Agent ${index + 1}`,
                    icon: 'fas fa-robot',
                    color: '#6264a7'
                });
            }
        });

        if (destinations.length === 0) {
            this.log.error('No AI columns available');
            return;
        }

        // Build dropdown HTML
        let html = '<div style="padding: 4px 0;">';
        destinations.forEach((dest, index) => {
            if (index > 0) {
                html += '<div style="height: 1px; background: #eee; margin: 4px 0;"></div>';
            }
            html += `
                <div class="destination-option" data-dest-id="${dest.id}" 
                     style="padding: 8px 12px; cursor: pointer; display: flex; align-items: center; gap: 8px;"
                     onmouseover="this.style.background='#f5f5f5'" 
                     onmouseout="this.style.background='transparent'">
                    <i class="${dest.icon}" style="color: ${dest.color}; width: 16px;"></i>
                    <span style="font-size: 13px; color: #333;">${dest.name}</span>
                    <span style="margin-left: auto; font-size: 11px; color: #999;">${this.state.selectedEmails.size}</span>
                </div>
            `;
        });
        html += '</div>';

        dropdown.innerHTML = html;

        // Add click handlers
        dropdown.querySelectorAll('.destination-option').forEach(option => {
            option.addEventListener('click', async () => {
                const destId = option.dataset.destId;
                dropdown.remove();
                await this.sendSelectedToAIColumn(destId);
            });
        });

        // Position and show dropdown
        button.parentElement.style.position = 'relative';
        button.parentElement.appendChild(dropdown);

        // Close on outside click
        setTimeout(() => {
            const closeHandler = (e) => {
                if (!dropdown.contains(e.target) && e.target !== button) {
                    dropdown.remove();
                    document.removeEventListener('click', closeHandler);
                }
            };
            document.addEventListener('click', closeHandler);
        }, 100);

        this.log.info(`Showing AI destination dropdown with ${destinations.length} options`);
    },

    /**
     * Send selected emails to specific AI column and create thread
     */
    async sendSelectedToAIColumn(destinationId) {
        if (this.state.selectedEmails.size === 0) {
            this.log.warn('No emails selected');
            return;
        }

        this.log.info(`Sending ${this.state.selectedEmails.size} emails to ${destinationId}...`);

        // Get selected email data
        const selectedData = this.state.emails.filter(email =>
            this.state.selectedEmails.has(email.id)
        );

        // Format for AI
        const emailText = selectedData.map(email => {
            return `From: ${email.sender}\nSubject: ${email.subject}\nDate: ${email.date}\n\n${email.body || 'No body'}\n\n---\n`;
        }).join('\n');

        try {
            // Get authenticated user ID from UserAuth (NOT localStorage)
            const userId = (window.UserAuth && window.UserAuth.user &&
                (window.UserAuth.user.id || window.UserAuth.user.user_id)) || '1';
            const response = await this.api.post('/api/threads/create', {
                user_id: userId,
                name: `Emails: ${selectedData[0].subject}`,
                location: destinationId, // 'prime' or 'agent-1', 'agent-2', etc.
                initial_message: emailText,
                metadata: {
                    email_ids: Array.from(this.state.selectedEmails),
                    source: 'communication-hub',
                    email_count: selectedData.length
                }
            });

            if (response.success && response.thread_slug) {
                this.log.success(`Thread created: ${response.thread_slug}`);

                // Assign all selected emails to the new thread
                for (const emailId of this.state.selectedEmails) {
                    await this.assignEmailToThread(emailId, response.thread_slug);
                }

                // Refresh thread view if on that tab
                if (this.state.currentTab === 'threads') {
                    this.renderThreadsTable();
                }

                // Update main email table to show thread assignment
                if (this.state.tabulatorTable) {
                    this.state.tabulatorTable.redraw();
                }

                // Emit event to open the thread in sidebar
                this.events.emit('open-thread', {
                    thread_slug: response.thread_slug,
                    location: destinationId
                });

                // Clear selection
                this.state.selectedEmails.clear();
                if (this.state.tabulatorTable) {
                    this.state.tabulatorTable.deselectRow();
                }

                this.log.success(`Emails sent to ${destinationId}`);
            } else {
                throw new Error(response.error || 'Failed to create thread');
            }
        } catch (error) {
            this.log.error('Failed to send emails to AI:', error);
            alert(`Failed to send emails: ${error.message}`);
        }
    },

    /**
     * Show email preview panel
     */
    async showEmailPreview(emailData) {
        this.log.debug(`Showing preview for email: ${emailData.id}`);

        const previewPanel = document.getElementById('emailPreview');
        const previewContent = document.getElementById('previewContent');

        if (!previewPanel || !previewContent) return;

        // Show panel immediately with loading state
        const loadingHtml = `
            <div class="email-preview-subject">
                <h4>${this.escapeHtml(emailData.subject)}</h4>
            </div>
            <div class="email-preview-meta">
                <div class="meta-row">
                    <span class="meta-label">From:</span>
                    <span class="meta-value">${this.escapeHtml(emailData.from)}</span>
                </div>
                <div class="meta-row">
                    <span class="meta-label">Date:</span>
                    <span class="meta-value">${this.formatDate(emailData.date)}</span>
                </div>
                <div class="meta-row">
                    <span class="meta-label">Account:</span>
                    <span class="meta-value">${emailData.provider}</span>
                </div>
            </div>
            <div class="email-preview-content">
                <div style="text-align: center; padding: 40px; color: var(--text-secondary);">
                    <i class="fas fa-spinner fa-spin" style="font-size: 24px; margin-bottom: 12px;"></i>
                    <p>Loading email content...</p>
                </div>
            </div>
        `;

        this.dom.injectHTML(previewContent, loadingHtml);
        previewPanel.classList.add('show');
        this.dom.show(previewPanel);

        // Fetch full email content
        try {
            const fullEmail = await this.fetchEmailContent(emailData.id);

            // Check if email is part of thread
            const threadSlug = this.state.emailThreads[emailData.id];
            let threadEmails = [];

            if (threadSlug) {
                this.log.info(`📬 Email is part of thread: ${threadSlug}`);
                try {
                    threadEmails = await this.fetchThreadEmails(threadSlug);
                    this.log.success(`Fetched ${threadEmails.length} emails in thread`);
                } catch (threadError) {
                    this.log.warn('Could not fetch thread emails:', threadError);
                    // Continue with single email view
                }
            }

            // Render preview based on thread status
            let contentHtml = '';

            if (threadEmails.length > 1) {
                // Thread view with all emails
                contentHtml = this.renderThreadPreview(threadEmails, emailData.id);
            } else {
                // Single email view
                contentHtml = `
                    <div class="email-preview-subject">
                        <h4>${this.escapeHtml(fullEmail.subject)}</h4>
                    </div>
                    <div class="email-preview-meta">
                        <div class="meta-row">
                            <span class="meta-label">From:</span>
                            <span class="meta-value">${this.escapeHtml(fullEmail.from)}</span>
                        </div>
                        <div class="meta-row">
                            <span class="meta-label">To:</span>
                            <span class="meta-value">${this.escapeHtml(fullEmail.to || 'N/A')}</span>
                        </div>
                        <div class="meta-row">
                            <span class="meta-label">Date:</span>
                            <span class="meta-value">${this.formatDate(fullEmail.date)}</span>
                        </div>
                        <div class="meta-row">
                            <span class="meta-label">Account:</span>
                            <span class="meta-value">${fullEmail.provider}</span>
                        </div>
                    </div>
                    <div class="email-preview-content">
                        ${this.renderEmailBody(fullEmail)}
                    </div>
                    ${this.renderAISection(fullEmail)}
                `;
            }

            this.dom.injectHTML(previewContent, contentHtml);

        } catch (error) {
            this.log.error(`Failed to load email content: ${error}`);

            // Show error state
            const errorHtml = `
                <div class="email-preview-subject">
                    <h4>${this.escapeHtml(emailData.subject)}</h4>
                </div>
                <div class="email-preview-meta">
                    <div class="meta-row">
                        <span class="meta-label">From:</span>
                        <span class="meta-value">${this.escapeHtml(emailData.from)}</span>
                    </div>
                    <div class="meta-row">
                        <span class="meta-label">Date:</span>
                        <span class="meta-value">${this.formatDate(emailData.date)}</span>
                    </div>
                </div>
                <div class="email-preview-content">
                    <div style="padding: 20px; background: var(--bg-error, #2a1a1a); border-radius: 8px; margin-top: 16px;">
                        <p style="color: var(--text-error, #ff6b6b); margin: 0 0 8px 0;">
                            <i class="fas fa-exclamation-triangle"></i> Failed to load email content
                        </p>
                        <p style="color: var(--text-secondary); margin: 0; font-size: 12px;">
                            ${this.escapeHtml(emailData.snippet || 'Preview not available')}
                        </p>
                    </div>
                </div>
            `;

            this.dom.injectHTML(previewContent, errorHtml);
        }
    },

    /**
     * Render AI Assistant section
     */
    renderAISection(email) {
        const threadSlug = this.state.emailThreads?.[email.id];
        const hasThread = !!threadSlug;

        if (hasThread) {
            return `
                <div class="email-ai-section">
                    <h4 style="display: flex; align-items: center; gap: 8px; margin: 0 0 12px 0;">
                        <i class="fas fa-robot" style="color: var(--accent-blue, #3b82f6);"></i>
                        AI Assistant
                    </h4>
                    <div class="ai-thread-linked" style="background: var(--bg-secondary); padding: 12px; border-radius: 8px; border-left: 3px solid var(--accent-blue, #3b82f6);">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                            <i class="fas fa-link" style="color: var(--accent-blue, #3b82f6);"></i>
                            <span style="color: var(--text-primary); font-weight: 500;">Linked to AI Thread</span>
                        </div>
                        <button class="btn-primary" style="width: 100%; margin-top: 8px;"
                                onclick="window.comHub.openAIThread('${threadSlug}')">
                            <i class="fas fa-comments"></i> Continue Conversation
                        </button>
                    </div>
                </div>
            `;
        }

        return `
            <div class="email-ai-section">
                <h4 style="display: flex; align-items: center; gap: 8px; margin: 0 0 12px 0;">
                    <i class="fas fa-robot" style="color: var(--accent-blue, #3b82f6);"></i>
                    AI Assistant
                </h4>
                <div class="ai-quick-actions" style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                    <button class="ai-action-btn" onclick="window.comHub.handleAIQuickAction('summarize', '${email.id}')">
                        <i class="fas fa-file-alt"></i> Summarize
                    </button>
                    <button class="ai-action-btn" onclick="window.comHub.handleAIQuickAction('draft_reply', '${email.id}')">
                        <i class="fas fa-reply"></i> Draft Reply
                    </button>
                    <button class="ai-action-btn" onclick="window.comHub.handleAIQuickAction('extract_tasks', '${email.id}')">
                        <i class="fas fa-tasks"></i> Extract Tasks
                    </button>
                    <button class="ai-action-btn ai-action-primary" onclick="window.comHub.handleAIQuickAction('discuss', '${email.id}')">
                        <i class="fas fa-comments"></i> Discuss with AI
                    </button>
                </div>
            </div>
        `;
    },

    /**
     * Handle AI Quick Action - Creates thread and opens AI Prime with email context
     */
    async handleAIQuickAction(action, emailId) {
        try {
            this.log.debug(`AI Quick Action: ${action} for email ${emailId}`);

            const email = this.state.emails.find(e => e.id === emailId);
            if (!email) {
                throw new Error('Email not found');
            }

            // Fetch full email content for context
            const fullEmail = await this.fetchEmailContent(emailId);

            // Format email as markdown
            const emailMarkdown = this.formatEmailAsMarkdown(fullEmail);

            const userId = window.UserAuth?.user?.id || 1;

            // Create new AI thread with email context
            const threadResponse = await this.api.post('/api/threads/create', {
                user_id: userId,
                title: `Email: ${fullEmail.subject}`,
                context_type: 'email',
                tags: ['email', fullEmail.provider, action],
                metadata: {
                    email_id: emailId,
                    email_subject: fullEmail.subject,
                    email_from: fullEmail.from,
                    email_to: fullEmail.to,
                    email_date: fullEmail.date,
                    email_provider: fullEmail.provider,
                    email_has_attachments: (fullEmail.attachments?.length || 0) > 0,
                    email_attachment_count: fullEmail.attachments?.length || 0,
                    action_requested: action
                }
            });

            const threadSlug = threadResponse.thread_slug;
            this.log.success(`Thread created: ${threadSlug}`);

            // Link email to thread
            await this.api.post('/api/thread-assignments/email', {
                user_id: userId,
                thread_slug: threadSlug,
                email_thread_id: emailId,
                email_subject: fullEmail.subject,
                email_participants: fullEmail.from
            });

            // Update local state
            if (!this.state.emailThreads) {
                this.state.emailThreads = {};
            }
            this.state.emailThreads[emailId] = threadSlug;

            // Update Tabulator to show 🤖 icon
            if (this.emailTable) {
                this.emailTable.updateData([{ id: emailId }]);
            }

            // Generate context-aware initial message
            const prompts = {
                'summarize': `Please provide a clear, concise summary of this email highlighting the key points, action items, and any deadlines mentioned.\n\n${emailMarkdown}`,
                'draft_reply': `Please draft a professional reply to this email. Match the tone of the sender and address all points raised.\n\n${emailMarkdown}`,
                'extract_tasks': `Please extract all action items, tasks, and deadlines from this email. Format as a checklist with due dates and priority levels.\n\n${emailMarkdown}`,
                'discuss': `I need your assistance with this email. Here's the full content:\n\n${emailMarkdown}`
            };

            const initialMessage = prompts[action] || prompts['discuss'];

            // Open AI Prime sidebar with pre-filled context
            if (window.AIPrime?.open) {
                window.AIPrime.open({
                    threadSlug: threadSlug,
                    agent: 'communication-agent',
                    initialMessage: initialMessage,
                    autoSend: true,  // Auto-send the initial message
                    context: {
                        type: 'email',
                        email_id: emailId,
                        email_data: fullEmail
                    }
                });
            } else {
                // Fallback: Navigate to thread
                window.location.hash = `#thread/${threadSlug}`;
            }

            this.log.success('AI thread opened with email context');

            // Refresh preview to show "Linked" state
            await this.showEmailPreview(email);

        } catch (error) {
            this.log.error('Failed to create AI thread', error);
            this.showError(`Failed to start AI conversation: ${error.message}`);
        }
    },

    /**
     * Format email as compact markdown for AI consumption
     */
    formatEmailAsMarkdown(email) {
        let markdown = `# Email Details\n\n`;

        markdown += `**From:** ${email.from}\n`;
        markdown += `**To:** ${email.to || 'N/A'}\n`;
        if (email.cc) markdown += `**CC:** ${email.cc}\n`;
        markdown += `**Subject:** ${email.subject}\n`;
        markdown += `**Date:** ${email.date}\n`;
        markdown += `**Account:** ${email.provider}\n`;

        // Attachments (listed but not included)
        if (email.attachments && email.attachments.length > 0) {
            markdown += `\n**Attachments:** (${email.attachments.length} files)\n`;
            email.attachments.forEach(att => {
                markdown += `  - ${att.filename || 'Unnamed'} (${att.mimeType || 'unknown type'})\n`;
            });
            markdown += `\n*Note: Attachment contents not included in context.*\n`;
        }

        markdown += `\n---\n\n`;

        // Email body (prefer text, fallback to HTML stripped)
        if (email.body_text) {
            markdown += `## Email Content\n\n${email.body_text}\n`;
        } else if (email.body_html) {
            // Strip HTML tags for plain text
            const textContent = email.body_html
                .replace(/<style[^>]*>.*?<\/style>/gs, '')
                .replace(/<script[^>]*>.*?<\/script>/gs, '')
                .replace(/<[^>]+>/g, ' ')
                .replace(/&nbsp;/g, ' ')
                .replace(/&amp;/g, '&')
                .replace(/&lt;/g, '<')
                .replace(/&gt;/g, '>')
                .replace(/&quot;/g, '"')
                .replace(/&#39;/g, "'")
                .replace(/\s+/g, ' ')
                .trim();
            markdown += `## Email Content\n\n${textContent}\n`;
        } else {
            markdown += `## Email Content\n\n*No content available*\n`;
        }

        return markdown;
    },

    /**
     * Open existing AI thread
     */
    openAIThread(threadSlug) {
        this.log.debug(`Opening AI thread: ${threadSlug}`);

        if (window.AIPrime?.open) {
            window.AIPrime.open({
                threadSlug: threadSlug
            });
        } else {
            // Fallback: Navigate to thread
            window.location.hash = `#thread/${threadSlug}`;
        }
    },

    /**
     * Fetch full email content from backend (with caching)
     */
    async fetchEmailContent(emailId) {
        // Check cache first
        if (this.state.emailContentCache[emailId]) {
            this.log.debug(`Using cached content for email: ${emailId}`);
            return this.state.emailContentCache[emailId];
        }

        this.log.debug(`Fetching full content for email: ${emailId}`);

        const userId = window.UserAuth?.user?.id || 1;
        const url = `${this.state.apiBase}/emails/${emailId}?user_id=${userId}`;

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        // Cache the result (5 minute TTL)
        this.state.emailContentCache[emailId] = result;
        setTimeout(() => {
            delete this.state.emailContentCache[emailId];
            this.log.debug(`Cache expired for email: ${emailId}`);
        }, 5 * 60 * 1000);  // 5 minutes

        if (!result.success) {
            throw new Error(result.error || 'Failed to fetch email');
        }

        return result.email;
    },

    /**
     * Render email body with HTML support and clickable links
     * Uses DOMPurify for safe HTML rendering (industry standard approach)
     */
    renderEmailBody(email) {
        // Prefer HTML body if available, fallback to text
        let content = email.body_html || email.body_text || email.snippet || 'No content available';

        if (email.body_html) {
            // SOLUTION: Direct HTML rendering with DOMPurify sanitization
            // Same approach used by Nylas Mail, Gmail clients, etc.
            // No iframe sandbox issues - content renders directly
            return `
                <div class="email-html-content" style="
                    background: white; 
                    padding: 20px; 
                    border-radius: 8px;
                    min-height: 400px;
                    overflow-x: auto;
                    word-wrap: break-word;
                ">
                    ${this.sanitizeHTML(content)}
                </div>
            `;
        } else {
            // Plain text - convert URLs to clickable links
            const urlRegex = /(https?:\/\/[^\s]+)/g;
            const linkedContent = content.replace(urlRegex, '<a href="$1" target="_blank" style="color: var(--accent-primary, #3b82f6); text-decoration: underline;">$1</a>');

            return `
                <div class="email-text-content" style="white-space: pre-wrap; line-height: 1.6; color: var(--text-primary);">
                    ${linkedContent}
                </div>
            `;
        }
    },

    /**
     * Close email preview panel
     */
    closePreview() {
        const previewPanel = document.getElementById('emailPreview');
        if (previewPanel) {
            previewPanel.classList.remove('show');
            setTimeout(() => {
                this.dom.hide(previewPanel);
            }, 300); // Wait for slide-out animation
        }
    },

    /**
     * Sanitize HTML for safe rendering
     * Implements DOMPurify-style whitelist approach (industry standard)
     * Used by Gmail, Nylas Mail, Outlook Web, etc.
     * 
     * This is THE SOLUTION that major email clients use:
     * - Direct HTML rendering (no iframe sandbox issues)
     * - Whitelist safe tags, remove dangerous ones
     * - Strip event handlers and javascript: URLs
     * - Allows styling, formatting, images, tables
     */
    sanitizeHTML(html) {
        if (!html) return '';

        // Create temporary container for DOM manipulation
        const temp = document.createElement('div');
        temp.innerHTML = html;

        // Remove ALL dangerous tags that could execute code
        const dangerousTags = [
            'script', 'iframe', 'object', 'embed', 'link',
            'style', 'meta', 'base', 'form', 'input', 'button'
        ];

        dangerousTags.forEach(tag => {
            const elements = temp.getElementsByTagName(tag);
            while (elements.length > 0) {
                elements[0].parentNode.removeChild(elements[0]);
            }
        });

        // Remove dangerous attributes from ALL elements
        const allElements = temp.getElementsByTagName('*');
        for (let i = 0; i < allElements.length; i++) {
            const el = allElements[i];

            // Get all attributes as array (before removal)
            const attrs = Array.from(el.attributes);

            attrs.forEach(attr => {
                // Remove ALL event handlers (onclick, onload, onerror, etc.)
                if (attr.name.startsWith('on')) {
                    el.removeAttribute(attr.name);
                }

                // Remove javascript: and data:text/html URLs
                if (attr.value.toLowerCase().includes('javascript:') ||
                    attr.value.toLowerCase().includes('data:text/html')) {
                    el.removeAttribute(attr.name);
                }
            });

            // Extra safety for href/src attributes
            if (el.hasAttribute('href')) {
                const href = el.getAttribute('href');
                if (href.toLowerCase().startsWith('javascript:') ||
                    href.toLowerCase().startsWith('data:text/html')) {
                    el.removeAttribute('href');
                }
            }

            if (el.hasAttribute('src')) {
                const src = el.getAttribute('src');
                if (src.toLowerCase().startsWith('javascript:')) {
                    el.removeAttribute('src');
                }
                // Allow data: URLs for images (base64 embedded images)
                // Allow https/http URLs for external images
            }
        }

        return temp.innerHTML;
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // DRAG AND DROP (AI Integration)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Setup drag-and-drop for AI integration
     */
    setupDragAndDrop() {
        this.log.info('Setting up drag-and-drop...');

        // TODO: Implement drag-and-drop when table is ready
        // Will use Tabulator's row drag events

        this.log.debug('Drag-and-drop setup complete');
    },

    /**
     * Setup right-click context menu
     */
    setupContextMenu() {
        this.log.info('Setting up context menu...');

        // TODO: Implement context menu
        // Will show on right-click on email rows

        this.log.debug('Context menu setup complete');
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // UI HELPERS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Update stats cards
     */
    updateStats() {
        const totalCount = this.state.emails.length;
        const gmailCount = this.state.emails.filter(e => e.provider === 'gmail').length;
        const outlookCount = this.state.emails.filter(e => e.provider === 'outlook').length;
        const unreadCount = this.state.emails.filter(e => !e.is_read).length;

        this.updateStatCard('total-emails-count', totalCount);
        this.updateStatCard('gmail-count', gmailCount);
        this.updateStatCard('outlook-count', outlookCount);
        this.updateStatCard('unread-count', unreadCount);

        this.log.debug(`Stats updated: Total=${totalCount}, Gmail=${gmailCount}, Outlook=${outlookCount}, Unread=${unreadCount}`);
    },

    /**
     * Update a single stat card
     */
    updateStatCard(elementId, value) {
        const el = document.getElementById(elementId);
        if (el) {
            el.textContent = value;
        }
    },

    /**
     * Update selected count display
     */
    updateSelectedCount() {
        const el = document.getElementById('selected-count');
        if (el) {
            el.textContent = `Selected: ${this.state.selectedEmails.size}`;
        }
    },

    /**
     * Show/hide loading state
     */
    showLoadingState(show) {
        const loading = document.getElementById('inbox-loading');
        const ready = document.getElementById('inbox-ready');
        const table = document.getElementById('email-table-container');

        if (show) {
            this.dom.show(loading);
            this.dom.hide(ready);
            this.dom.hide(table);
        } else {
            this.dom.hide(loading);
            // Don't show ready state if table has data
            if (this.state.tableReady) {
                this.dom.show(table);
            } else {
                this.dom.show(ready);
            }
        }
    },

    /**
     * Show error message
     */
    showError(message) {
        // TODO: Implement proper error toast/notification
        this.log.error(message);
        alert(`Error: ${message}`);
    },

    /**
     * Format date for display
     */
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (e) {
            return dateString;
        }
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

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // PERSISTENCE (localStorage)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Load saved preferences
     */
    loadPreferences() {
        const prefs = this.storage.get('communication-hub:preferences');
        if (prefs) {
            this.state.currentAccountFilter = prefs.accountFilter || 'all';
            this.state.currentEmailLimit = prefs.emailLimit || 50;
            this.state.pageSize = prefs.pageSize || 50;
            this.state.emailTags = prefs.emailTags || {};
            this.log.debug('Preferences loaded from storage');
        }
    },

    /**
     * Save current preferences
     */
    savePreferences() {
        const prefs = {
            accountFilter: this.state.currentAccountFilter,
            emailLimit: this.state.currentEmailLimit,
            pageSize: this.state.pageSize,
            emailTags: this.state.emailTags
        };
        this.storage.set('communication-hub:preferences', prefs);
        this.log.debug('Preferences saved to storage');
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // COMPOSE FUNCTIONALITY
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Setup compose event listeners
     */
    setupComposeEvents() {
        this.log.debug('Setting up compose events...');

        // CC/BCC toggles
        const toggleCC = document.getElementById('compose-toggle-cc');
        const toggleBCC = document.getElementById('compose-toggle-bcc');
        const ccGroup = document.getElementById('compose-cc-group');
        const bccGroup = document.getElementById('compose-bcc-group');

        if (toggleCC && ccGroup) {
            this.dom.on(toggleCC, 'click', () => {
                ccGroup.style.display = ccGroup.style.display === 'none' ? 'block' : 'none';
            });
        }

        if (toggleBCC && bccGroup) {
            this.dom.on(toggleBCC, 'click', () => {
                bccGroup.style.display = bccGroup.style.display === 'none' ? 'block' : 'none';
            });
        }

        // Send button
        const sendBtn = document.getElementById('compose-send');
        if (sendBtn) {
            this.dom.on(sendBtn, 'click', () => this.sendEmail());
        }

        // Save draft button
        const draftBtn = document.getElementById('compose-save-draft');
        if (draftBtn) {
            this.dom.on(draftBtn, 'click', () => this.saveDraft());
        }

        // Auto-save draft every 30 seconds
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
        }
        this.autoSaveInterval = setInterval(() => {
            this.autoSaveDraft();
        }, 30000);
    },

    /**
     * Send email
     */
    async sendEmail() {
        this.log.info('Sending email...');

        // Get form values
        const account = document.getElementById('compose-account')?.value;
        const to = document.getElementById('compose-to')?.value;
        const cc = document.getElementById('compose-cc')?.value;
        const bcc = document.getElementById('compose-bcc')?.value;
        const subject = document.getElementById('compose-subject')?.value;
        const body = document.getElementById('compose-body')?.value;

        // Validation
        if (!account) {
            this.showError('Please select a sender account');
            return;
        }
        if (!to) {
            this.showError('Please enter recipient email address');
            return;
        }
        if (!subject) {
            this.showError('Please enter email subject');
            return;
        }

        this.state.loading.compose = true;

        try {
            // Get authenticated user ID from UserAuth (NOT localStorage)
            const userId = (window.UserAuth && window.UserAuth.user &&
                (window.UserAuth.user.id || window.UserAuth.user.user_id)) || '1';

            const response = await this.api.post(`${this.state.apiBase}/send`, {
                user_id: userId,
                provider: account,
                to: to.split(',').map(e => e.trim()),
                cc: cc ? cc.split(',').map(e => e.trim()) : [],
                bcc: bcc ? bcc.split(',').map(e => e.trim()) : [],
                subject,
                body,
                reply_to: this.state.compose.replyTo || null
            });

            this.log.success('Email sent successfully');
            this.showSuccess('Email sent successfully!');

            // Clear form
            this.clearComposeForm();

            // Switch back to inbox
            const inboxBtn = document.querySelector('[data-subtab="unified-inbox"]');
            if (inboxBtn) {
                inboxBtn.click();
            }

        } catch (error) {
            this.log.error('Failed to send email', error);
            this.showError(`Failed to send email: ${error.message}`);
        } finally {
            this.state.loading.compose = false;
        }
    },

    /**
     * Save draft
     */
    saveDraft() {
        const draft = {
            account: document.getElementById('compose-account')?.value,
            to: document.getElementById('compose-to')?.value,
            cc: document.getElementById('compose-cc')?.value,
            bcc: document.getElementById('compose-bcc')?.value,
            subject: document.getElementById('compose-subject')?.value,
            body: document.getElementById('compose-body')?.value,
            timestamp: Date.now()
        };

        this.storage.set('communication-hub:draft', draft);
        this.log.info('Draft saved');
        this.showSuccess('Draft saved!');
    },

    /**
     * Auto-save draft (silent)
     */
    autoSaveDraft() {
        const body = document.getElementById('compose-body')?.value;
        if (body && body.length > 0) {
            const draft = {
                account: document.getElementById('compose-account')?.value,
                to: document.getElementById('compose-to')?.value,
                cc: document.getElementById('compose-cc')?.value,
                bcc: document.getElementById('compose-bcc')?.value,
                subject: document.getElementById('compose-subject')?.value,
                body,
                timestamp: Date.now()
            };
            this.storage.set('communication-hub:draft', draft);
            this.log.debug('Draft auto-saved');
        }
    },

    /**
     * Clear compose form
     */
    clearComposeForm() {
        const fields = ['compose-account', 'compose-to', 'compose-cc', 'compose-bcc', 'compose-subject', 'compose-body'];
        fields.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = '';
        });
        this.storage.remove('communication-hub:draft');
    },

    /**
     * Show success message
     */
    showSuccess(message) {
        // TODO: Implement proper success toast/notification
        this.log.success(message);
        alert(message);
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // THREADS FUNCTIONALITY
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Load thread assignments from backend
     * Note: The /api/thread-assignments endpoint returns agent column assignments,
     * not email-specific assignments. Email assignments are stored in sessions.threads
     * with email_thread_id, email_subject, email_participants columns.
     */
    async loadThreadAssignments() {
        this.log.info('Loading thread assignments...');
        this.state.loading.threads = true;

        try {
            // Initialize empty structures
            this.state.threads = [];
            this.state.emailThreads = {};

            // Note: The old generic assignment system is deprecated.
            // Email-to-thread linkages are now stored directly in sessions.threads
            // with email_thread_id, email_subject, email_participants columns.
            // No need to load them here - they're loaded when viewing threads.

            this.log.info('Thread assignment system ready (email linkages stored in sessions.threads)');
        } catch (error) {
            this.log.error('Failed to initialize thread assignments', error);
            // Ensure state.threads is always an array even on error
            this.state.threads = [];
            this.state.emailThreads = {};
        } finally {
            this.state.loading.threads = false;
        }
    },

    /**
     * Setup threads event listeners
     */
    setupThreadsEvents() {
        this.log.debug('Setting up threads events...');

        const refreshBtn = document.getElementById('threads-refresh');
        if (refreshBtn) {
            this.dom.on(refreshBtn, 'click', async () => {
                await this.loadThreadAssignments();
                this.renderThreadsTable();
            });
        }
    },

    /**
     * Render threads table
     */
    renderThreadsTable() {
        const container = document.getElementById('threads-table-container');
        if (!container) {
            this.log.error('Threads table container not found');
            return;
        }

        // Update stats
        const assignedCount = Object.keys(this.state.emailThreads).length;
        const activeThreads = new Set(Object.values(this.state.emailThreads)).size;
        const unassignedCount = this.state.emails.length - assignedCount;

        const assignedEl = document.getElementById('threads-assigned-count');
        const activeEl = document.getElementById('threads-active-count');
        const unassignedEl = document.getElementById('threads-unassigned-count');

        if (assignedEl) assignedEl.textContent = assignedCount;
        if (activeEl) activeEl.textContent = activeThreads;
        if (unassignedEl) unassignedEl.textContent = unassignedCount;

        // Build thread data
        const threadData = this.state.emails.map(email => {
            const threadSlug = this.state.emailThreads[email.id];
            return {
                email_id: email.id,
                from: email.from,
                subject: email.subject,
                date: email.date,
                thread_slug: threadSlug || 'Not assigned',
                has_thread: !!threadSlug
            };
        });

        // Create Tabulator table
        if (typeof Tabulator === 'undefined') {
            this.log.error('Tabulator not loaded');
            return;
        }

        new Tabulator(container, {
            data: threadData,
            layout: "fitDataStretch",
            pagination: true,
            paginationSize: 50,
            columns: [
                {
                    title: "Status",
                    field: "has_thread",
                    width: 80,
                    hozAlign: "center",
                    formatter: (cell) => {
                        const hasThread = cell.getValue();
                        return hasThread ?
                            '<i class="fas fa-link" style="color: #2e7d32;"></i>' :
                            '<i class="fas fa-unlink" style="color: #9ca3af;"></i>';
                    }
                },
                {
                    title: "From",
                    field: "from",
                    width: 200,
                    sorter: "string"
                },
                {
                    title: "Subject",
                    field: "subject",
                    sorter: "string"
                },
                {
                    title: "Date",
                    field: "date",
                    width: 180,
                    sorter: "datetime",
                    formatter: (cell) => this.formatDate(cell.getValue())
                },
                {
                    title: "Thread Slug",
                    field: "thread_slug",
                    width: 200,
                    sorter: "string",
                    formatter: (cell) => {
                        const value = cell.getValue();
                        if (value === 'Not assigned') {
                            return `<span style="color: var(--text-secondary); font-style: italic;">${value}</span>`;
                        }
                        return `<code style="background: var(--bg-secondary); padding: 2px 6px; border-radius: 4px; font-size: 12px;">${value}</code>`;
                    }
                },
                {
                    title: "Actions",
                    width: 150,
                    hozAlign: "center",
                    formatter: (cell) => {
                        const data = cell.getRow().getData();
                        if (data.has_thread) {
                            return '<button class="btn btn-sm" onclick="window.communicationHub.openThread(\'' + data.thread_slug + '\')"><i class="fas fa-external-link-alt"></i> Open Thread</button>';
                        }
                        return '<button class="btn btn-sm btn-secondary" disabled>No thread</button>';
                    }
                }
            ]
        });

        this.log.debug('Threads table rendered');
    },

    /**
     * Open thread in AI sidebar
     */
    openThread(threadSlug) {
        this.log.info(`Opening thread: ${threadSlug}`);
        // Emit event for main UI to switch to thread
        this.events.emit('open-thread', { thread_slug: threadSlug });
    },

    /**
     * Assign email to thread
     */
    async assignEmailToThread(emailId, threadSlug) {
        this.log.info(`Assigning email ${emailId} to thread ${threadSlug}`);

        try {
            // Get authenticated user ID from UserAuth (NOT localStorage)
            const userId = (window.UserAuth && window.UserAuth.user &&
                (window.UserAuth.user.id || window.UserAuth.user.user_id)) || '1';

            // Get email details for metadata
            const email = this.state.emails.find(e => e.id === emailId);
            if (!email) {
                throw new Error('Email not found in current state');
            }

            // Build participants list (from, to, cc)
            const participants = [email.from];
            if (email.to && Array.isArray(email.to)) {
                participants.push(...email.to);
            }
            if (email.cc && Array.isArray(email.cc)) {
                participants.push(...email.cc);
            }

            // Save email thread linkage to sessions.threads table (NEW API)
            await this.api.post(`/api/thread-assignments/email`, {
                user_id: userId,
                thread_slug: threadSlug,
                email_thread_id: emailId,
                email_subject: email.subject || 'No Subject',
                email_participants: participants
            });

            // Update local state
            this.state.emailThreads[emailId] = threadSlug;

            this.log.success('Email assigned to thread');
            await this.loadThreadAssignments();
            this.renderThreadsTable();

        } catch (error) {
            this.log.error('Failed to assign email to thread', error);
            this.showError(`Failed to assign: ${error.message}`);
        }
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // SEARCH FUNCTIONALITY
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Setup search event listeners
     */
    setupSearchEvents() {
        this.log.debug('Setting up search events...');

        // Search submit
        const submitBtn = document.getElementById('search-submit');
        const queryInput = document.getElementById('search-query');

        if (submitBtn) {
            this.dom.on(submitBtn, 'click', () => this.performSearch());
        }

        if (queryInput) {
            // Allow Enter key to submit
            this.dom.on(queryInput, 'keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch();
                }
            });
        }

        // Clear button
        const clearBtn = document.getElementById('search-clear');
        if (clearBtn) {
            this.dom.on(clearBtn, 'click', () => this.clearSearch());
        }

        // Toggle filters
        const toggleFilters = document.getElementById('search-toggle-filters');
        const filtersDiv = document.getElementById('search-filters');

        if (toggleFilters && filtersDiv) {
            this.dom.on(toggleFilters, 'click', () => {
                filtersDiv.style.display = filtersDiv.style.display === 'none' ? 'block' : 'none';
            });
        }
    },

    /**
     * Perform search
     */
    async performSearch() {
        const query = document.getElementById('search-query')?.value;

        if (!query || query.trim().length === 0) {
            this.showError('Please enter a search query');
            return;
        }

        this.log.info(`Searching for: ${query}`);
        this.state.loading.search = true;

        // Show loading
        const loading = document.getElementById('search-loading');
        const noResults = document.getElementById('search-no-results');
        const resultsContainer = document.getElementById('search-results-container');

        this.dom.show(loading);
        this.dom.hide(noResults);
        this.dom.hide(resultsContainer);

        try {
            // Get filter values
            const sender = document.getElementById('search-filter-sender')?.value;
            const dateFrom = document.getElementById('search-filter-date-from')?.value;
            const dateTo = document.getElementById('search-filter-date-to')?.value;
            const hasAttachment = document.getElementById('search-filter-attachment')?.value;

            // Perform client-side search (could be backend API in future)
            const results = this.state.emails.filter(email => {
                // Text search
                const searchText = query.toLowerCase();
                const matches = (
                    email.subject?.toLowerCase().includes(searchText) ||
                    email.from?.toLowerCase().includes(searchText) ||
                    email.body?.toLowerCase().includes(searchText)
                );

                if (!matches) return false;

                // Sender filter
                if (sender && !email.from?.toLowerCase().includes(sender.toLowerCase())) {
                    return false;
                }

                // Date filters
                if (dateFrom) {
                    const emailDate = new Date(email.date);
                    const fromDate = new Date(dateFrom);
                    if (emailDate < fromDate) return false;
                }

                if (dateTo) {
                    const emailDate = new Date(email.date);
                    const toDate = new Date(dateTo);
                    toDate.setHours(23, 59, 59, 999); // End of day
                    if (emailDate > toDate) return false;
                }

                // Attachment filter
                if (hasAttachment === 'true' && !email.has_attachments) return false;
                if (hasAttachment === 'false' && email.has_attachments) return false;

                return true;
            });

            this.state.search.results = results;
            this.log.success(`Found ${results.length} results`);

            // Update result count
            const countEl = document.getElementById('search-result-count');
            if (countEl) {
                countEl.textContent = `(${results.length} found)`;
            }

            // Render results
            this.renderSearchResults();

        } catch (error) {
            this.log.error('Search failed', error);
            this.showError(`Search failed: ${error.message}`);
        } finally {
            this.state.loading.search = false;
            this.dom.hide(loading);
        }
    },

    /**
     * Render search results
     */
    renderSearchResults() {
        const container = document.getElementById('search-results-container');
        const noResults = document.getElementById('search-no-results');

        if (!container) return;

        if (this.state.search.results.length === 0) {
            this.dom.hide(container);
            noResults.innerHTML = `
                <i class="fas fa-inbox" style="font-size: 32px; margin-bottom: 10px; display: block; color: var(--text-secondary);"></i>
                <p style="margin: 0;">No emails found matching your search</p>
            `;
            this.dom.show(noResults);
            return;
        }

        this.dom.hide(noResults);
        this.dom.show(container);

        // Create Tabulator table
        if (typeof Tabulator === 'undefined') {
            this.log.error('Tabulator not loaded');
            return;
        }

        new Tabulator(container, {
            data: this.state.search.results,
            layout: "fitDataStretch",
            pagination: true,
            paginationSize: 50,
            columns: [
                {
                    title: "From",
                    field: "from",
                    width: 200,
                    sorter: "string"
                },
                {
                    title: "Subject",
                    field: "subject",
                    sorter: "string",
                    formatter: (cell) => this.escapeHtml(cell.getValue())
                },
                {
                    title: "Date",
                    field: "date",
                    width: 180,
                    sorter: "datetime",
                    formatter: (cell) => this.formatDate(cell.getValue())
                },
                {
                    title: "Account",
                    field: "provider",
                    width: 120,
                    sorter: "string"
                },
                {
                    title: "Actions",
                    width: 120,
                    hozAlign: "center",
                    formatter: () => '<button class="btn btn-sm"><i class="fas fa-eye"></i> View</button>'
                }
            ]
        });
    },

    /**
     * Clear search
     */
    clearSearch() {
        // Clear inputs
        const inputs = [
            'search-query',
            'search-filter-sender',
            'search-filter-date-from',
            'search-filter-date-to'
        ];

        inputs.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = '';
        });

        const attachmentSelect = document.getElementById('search-filter-attachment');
        if (attachmentSelect) attachmentSelect.value = '';

        // Clear results
        this.state.search.results = [];
        this.state.search.query = '';

        // Reset UI
        const noResults = document.getElementById('search-no-results');
        const resultsContainer = document.getElementById('search-results-container');
        const countEl = document.getElementById('search-result-count');

        this.dom.hide(resultsContainer);
        if (noResults) {
            noResults.innerHTML = `
                <i class="fas fa-search" style="font-size: 32px; margin-bottom: 10px; display: block;"></i>
                <p style="margin: 0;">Enter a search query to find emails</p>
            `;
            this.dom.show(noResults);
        }

        if (countEl) countEl.textContent = '';

        this.log.debug('Search cleared');
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // EMAIL THREADING (NEW - Phase 2)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Fetch all emails in a thread
     */
    async fetchThreadEmails(threadSlug) {
        this.log.info(`📬 Fetching emails for thread: ${threadSlug}`);

        const userId = window.UserAuth?.user?.id || 1;
        const url = `${this.state.apiBase}/threads/${threadSlug}/emails?user_id=${userId}`;

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || 'Failed to fetch thread emails');
            }

            return result.emails || [];
        } catch (error) {
            this.log.error('Failed to fetch thread emails:', error);
            throw error;
        }
    },

    /**
     * Render thread preview with all emails (expandable)
     */
    renderThreadPreview(emails, currentEmailId) {
        const sorted = emails.sort((a, b) => new Date(a.date) - new Date(b.date));

        let html = `
            <div class="email-preview-content" style="padding: 20px;">
                <div style="background: var(--bg-secondary); padding: 12px 16px; border-radius: 8px; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
                    <i class="fas fa-comments" style="color: #6366f1; font-size: 18px;"></i>
                    <div>
                        <div style="font-weight: 500; color: var(--text-primary);">Email Thread</div>
                        <div style="font-size: 12px; color: var(--text-secondary);">${sorted.length} messages in conversation</div>
                    </div>
                </div>
                
                <div class="thread-email-list" style="display: flex; flex-direction: column; gap: 12px;">
        `;

        sorted.forEach((email, index) => {
            const isLatest = email.id === currentEmailId;
            const isExpanded = isLatest || index === sorted.length - 1;

            html += `
                <div class="thread-email-item" data-email-id="${email.id}" style="border: 1px solid var(--border-default); border-radius: 8px; overflow: hidden; ${isLatest ? 'border-color: #6366f1; box-shadow: 0 0 0 1px #6366f1;' : ''}">
                    <div class="thread-email-header" 
                         style="padding: 12px 16px; background: var(--bg-secondary); cursor: pointer; display: flex; justify-content: space-between; align-items: center; ${isLatest ? 'background: rgba(99, 102, 241, 0.1);' : ''}" 
                         onclick="window.CommunicationHub.toggleThreadEmail('${email.id}')">
                        <div style="flex: 1;">
                            <div style="font-weight: 500; color: var(--text-primary); margin-bottom: 4px; display: flex; align-items: center; gap: 8px;">
                                ${this.escapeHtml(email.from)}
                                ${isLatest ? '<span style="background: #6366f1; color: white; padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: 600;">CURRENT</span>' : ''}
                            </div>
                            <div style="font-size: 12px; color: var(--text-secondary);">
                                ${this.formatDate(email.date)}
                            </div>
                        </div>
                        <i class="fas fa-chevron-down thread-email-toggle" id="toggle-${email.id}" style="color: var(--text-secondary); transition: transform 0.2s; ${isExpanded ? 'transform: rotate(180deg);' : ''}"></i>
                    </div>
                    <div class="thread-email-body" 
                         id="body-${email.id}" 
                         style="display: ${isExpanded ? 'block' : 'none'}; padding: 16px; background: var(--bg-card); border-top: 1px solid var(--border-default);">
                        ${this.renderEmailBody(email)}
                    </div>
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;

        return html;
    },

    /**
     * Toggle thread email expansion (called from onclick)
     */
    toggleThreadEmail(emailId) {
        const body = document.getElementById(`body-${emailId}`);
        const toggle = document.getElementById(`toggle-${emailId}`);

        if (body && toggle) {
            const isVisible = body.style.display === 'block';
            body.style.display = isVisible ? 'none' : 'block';
            toggle.style.transform = isVisible ? 'rotate(0deg)' : 'rotate(180deg)';
        }
    }
};
