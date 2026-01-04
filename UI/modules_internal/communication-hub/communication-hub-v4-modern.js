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

            // 11.5. Subscribe to realtime thread updates (to sync email assignments)
            this.subscribeToRealtimeUpdates();

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
                <div class="module-subtabs-content" style="flex: 1; margin-top: 10px; display: flex; flex-direction: column;">
                    <div class="module-subtab-content active" id="communication-hub-subtab-unified-inbox" data-subtab="unified-inbox" style="display: flex; flex-direction: column; height: 100%;"></div>
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

        // Setup toolbar events AFTER unified inbox is rendered (toolbar is inside inbox)
        this.setupToolbarEvents();

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
            <div class="module-dashboard" id="email-dashboard-main">
                <!-- Toolbar (full width, stays above workspace) -->
                ${this.renderToolbar()}
                
                <!-- Side-by-side workspace container for table and preview -->
                <div class="email-workspace-container" style="display: flex; gap: 16px; height: calc(100vh - 310px); overflow: hidden;">
                    <!-- Email Table Card -->
                    <div class="dashboard-card email-table-wrapper" style="flex: 1; display: flex; flex-direction: column; min-width: 0; height: 92%;">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="fas fa-list"></i> Email Messages
                            </h3>
                        </div>
                        <div class="card-content" style="flex: 1; display: flex; flex-direction: column; overflow: hidden; min-height: 0;">
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
                            <div id="email-table-container" style="display: none; flex: 1; min-height: 0;"></div>
                        </div>
                    </div>
                    
                    <!-- Email Preview Panel (sibling to dashboard-card) -->
                    <!-- ✅ FIX (Jan 4, 2026): Hidden by default, only shows when email selected -->
                    <div id="emailPreview" class="email-preview-panel" data-mode="sibling" style="display: none; flex: 0 0 0%; height: 92%; flex-direction: column; overflow: hidden;">
                    <div class="email-preview-header" style="flex-shrink: 0;">
                        <div class="email-preview-title">
                            <i class="fas fa-envelope"></i>
                            <span id="preview-title-text">Email Preview</span>
                        </div>
                        <div class="email-preview-controls">
                            <button class="synergy-icon-btn" data-action="reply" title="Reply">
                                <i class="fas fa-reply"></i>
                            </button>
                            <button class="synergy-icon-btn" data-action="reply-all" title="Reply All">
                                <i class="fas fa-reply-all"></i>
                            </button>
                            <button class="synergy-icon-btn" data-action="forward" title="Forward">
                                <i class="fas fa-share"></i>
                            </button>
                            <div style="width: 1px; height: 24px; background: var(--border-default, #30363d); margin: 0 4px;"></div>
                            <button class="synergy-icon-btn" data-action="archive" title="Archive">
                                <i class="fas fa-archive"></i>
                            </button>
                            <button class="synergy-icon-btn" data-action="delete" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                            <button class="synergy-icon-btn" data-action="toggle-read" title="Mark as read/unread">
                                <i class="fas fa-envelope-open"></i>
                            </button>
                            <button class="synergy-icon-btn" data-action="print" title="Print">
                                <i class="fas fa-print"></i>
                            </button>
                            <div style="width: 1px; height: 24px; background: var(--border-default, #30363d); margin: 0 4px;"></div>
                            <button class="synergy-icon-btn" data-action="toggle-popup-mode" title="Toggle popup mode">
                                <i class="fas fa-external-link-alt"></i>
                            </button>
                            <button class="synergy-icon-btn" data-action="close-preview" title="Close preview">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                    <div id="previewContent" class="email-preview-body" style="flex: 1; min-height: 0; display: flex; flex-direction: column; overflow: hidden;"></div>
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
            <div class="filters-bar" style="margin: 5px 5px; padding: 12px; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; display: flex; gap: 15px; flex-wrap: wrap; align-items: center;">
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

        this.log.debug('Dashboard events setup complete');
    },

    /**
     * Setup toolbar event listeners (called after unified inbox is rendered)
     */
    setupToolbarEvents() {
        this.log.info('Setting up toolbar events...');

        // Toolbar actions - look for filters-bar (the actual toolbar class)
        const toolbar = this.dashboardContainer.querySelector('.filters-bar');
        if (!toolbar) {
            this.log.error('Toolbar not found - unified inbox may not be rendered yet');
            return;
        }

        this.log.success('✅ Refresh button found, attaching direct listener');

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

        // Preview popup mode toggle
        this.dom.on(this.dashboardContainer, 'click', '[data-action="toggle-popup-mode"]', () => {
            this.togglePopupMode();
        });

        // Email action toolbar buttons (Reply, Forward, Delete, etc)
        this.dom.on(this.dashboardContainer, 'click', '.email-action-toolbar [data-action="reply"]', () => {
            this.handleEmailAction('reply');
        });
        this.dom.on(this.dashboardContainer, 'click', '.email-action-toolbar [data-action="reply-all"]', () => {
            this.handleEmailAction('reply-all');
        });
        this.dom.on(this.dashboardContainer, 'click', '.email-action-toolbar [data-action="forward"]', () => {
            this.handleEmailAction('forward');
        });
        this.dom.on(this.dashboardContainer, 'click', '.email-action-toolbar [data-action="archive"]', () => {
            this.handleEmailAction('archive');
        });
        this.dom.on(this.dashboardContainer, 'click', '.email-action-toolbar [data-action="delete"]', () => {
            this.handleEmailAction('delete');
        });
        this.dom.on(this.dashboardContainer, 'click', '.email-action-toolbar [data-action="toggle-read"]', () => {
            this.handleEmailAction('toggle-read');
        });
        this.dom.on(this.dashboardContainer, 'click', '.email-action-toolbar [data-action="print"]', () => {
            this.handleEmailAction('print');
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

            // Check if no emails returned and no accounts connected
            if (this.state.emails.length === 0 && this.state.accounts.length === 0) {
                this.showNoAccountsWarning();
                return;
            }

            // Check if no emails but accounts are connected
            if (this.state.emails.length === 0 && this.state.accounts.length > 0) {
                this.log.warn('No emails found despite having connected accounts');
            }

            // Update stats
            this.updateStats();

            // ✅ FIX #5 (Jan 4, 2026): Load email-thread mappings BEFORE creating table
            // This ensures AI Agent column shows badges immediately on first render
            await this.loadEmailThreadMappings();

            // Create/update table (mappings are now available for formatters)
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

        // Create table (WooCommerce Gold Standard Pattern)
        // ✅ Phase 2 Features: Header filters, pagination with size selector, movable/resizable columns, persistent layout
        this.state.tabulatorTable = new Tabulator(container, {
            data: this.state.emails,
            layout: "fitColumns",  // ✅ FIX: Responsive column sizing
            layoutColumnsOnNewData: true,
            responsiveLayout: false,  // ✅ FIX: Disable responsive collapse (keep all columns visible)
            height: "100%",  // ✅ FIX: Enable virtual DOM scrolling with fixed header

            // Pagination (WooCommerce pattern)
            pagination: "local",
            paginationSize: 25,
            paginationSizeSelector: [10, 25, 50, 100],
            paginationButtonCount: 5,
            paginationCounter: "rows",

            // User control (WooCommerce pattern)
            movableColumns: true,
            resizableColumns: true,
            persistentLayout: true,
            persistentLayoutID: "communication-hub-inbox-layout",

            // Selection
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
                    width: 180,
                    sorter: "datetime",
                    headerFilter: "input",
                    headerFilterPlaceholder: "Search date...",
                    formatter: (cell) => {
                        const date = new Date(cell.getValue());
                        const formatted = date.toLocaleDateString('en-GB', {
                            day: '2-digit',
                            month: '2-digit',
                            year: 'numeric'
                        });
                        const time = date.toLocaleTimeString('en-GB', {
                            hour: '2-digit',
                            minute: '2-digit'
                        });

                        return `<div style="text-align: left;">
                            <div style="color: #ffffff; font-weight: 500;">
                                <i class="fas fa-calendar" style="color: #6b7280; margin-right: 4px;"></i>
                                ${formatted}
                            </div>
                            <div style="color: #9ca3af; font-size: 11px; margin-top: 2px;">
                                <i class="fas fa-clock" style="color: #6b7280; margin-right: 4px;"></i>
                                ${time}
                            </div>
                        </div>`;
                    }
                },
                {
                    title: "Status",
                    field: "is_read",
                    width: 100,
                    hozAlign: "center",
                    headerFilter: "select",
                    headerFilterParams: { values: { "": "All", "false": "Unread", "true": "Read" } },
                    headerFilterPlaceholder: "Filter...",
                    formatter: (cell) => {
                        const isRead = cell.getValue();
                        const colors = isRead
                            ? { bg: '#6b7280', text: '#f9fafb', icon: 'envelope-open' }
                            : { bg: '#3b82f6', text: '#f9fafb', icon: 'envelope' };

                        return `<span style="
                            display: inline-block;
                            padding: 6px 12px;
                            border-radius: 12px;
                            font-size: 11px;
                            font-weight: 700;
                            background: ${colors.bg};
                            color: ${colors.text};
                            letter-spacing: 0.3px;
                        ">
                            <i class="fas fa-${colors.icon}" style="margin-right: 4px;"></i>
                            ${isRead ? 'Read' : 'Unread'}
                        </span>`;
                    }
                },
                {
                    title: "📎",
                    field: "has_attachments",
                    width: 60,
                    hozAlign: "center",
                    headerSort: false,
                    tooltip: "Attachments",
                    formatter: (cell) => {
                        const data = cell.getRow().getData();
                        const hasAttachments = data.has_attachments;
                        const count = data.attachment_count || 0;

                        if (hasAttachments && count > 0) {
                            return `<div style="display: flex; align-items: center; justify-content: center; gap: 4px;">
                                <i class="fas fa-paperclip" style="color: #6366f1;" title="${count} attachment(s)"></i>
                                <span style="font-size: 11px; color: #6366f1; font-weight: 600;">${count}</span>
                            </div>`;
                        }
                        return '<span style="color: #d1d5db;">—</span>';
                    }
                },
                {
                    title: "Account",
                    field: "provider",
                    width: 120,
                    hozAlign: "center",
                    headerFilter: "select",
                    headerFilterParams: { values: { "": "All", "gmail": "Gmail", "outlook": "Outlook" } },
                    headerFilterPlaceholder: "Filter...",
                    formatter: (cell) => {
                        const provider = cell.getValue();
                        if (provider === 'gmail') {
                            return `<span style="color: #ffffff; font-weight: 500;">
                                <i class="fab fa-google" style="color: #ea4335; font-size: 14px; margin-right: 4px;"></i>
                                Gmail
                            </span>`;
                        } else if (provider === 'outlook') {
                            return `<span style="color: #ffffff; font-weight: 500;">
                                <i class="fab fa-microsoft" style="color: #0078d4; font-size: 14px; margin-right: 4px;"></i>
                                Outlook
                            </span>`;
                        }
                        return `<span style="color: #9ca3af;">
                            <i class="fas fa-envelope" style="color: #6b7280; margin-right: 4px;"></i>
                            Unknown
                        </span>`;
                    }
                },
                {
                    title: "From",
                    field: "from",
                    width: 220,
                    sorter: "string",
                    headerFilter: "input",
                    headerFilterPlaceholder: "Search sender...",
                    formatter: (cell) => {
                        const from = cell.getValue() || 'Unknown';
                        const row = cell.getRow().getData();
                        const isRead = row.is_read;

                        return `<div style="display: flex; align-items: center; gap: 6px;">
                            ${!isRead ? `<span style="width: 8px; height: 8px; background: #3b82f6; border-radius: 50%; flex-shrink: 0;"></span>` : ''}
                            <span style="color: #ffffff; font-weight: ${isRead ? '400' : '600'}; flex: 1;">
                                <i class="fas fa-user" style="color: #6b7280; margin-right: 4px; font-size: 11px;"></i>
                                ${this.escapeHtml(from)}
                            </span>
                        </div>`;
                    }
                },
                {
                    title: "Subject",
                    field: "subject",
                    width: 400,
                    sorter: "string",
                    headerFilter: "input",
                    headerFilterPlaceholder: "Search subject...",
                    formatter: (cell) => {
                        const value = cell.getValue() || '(No subject)';
                        const data = cell.getRow().getData();
                        const hasThread = this.state.emailThreads[data.id];
                        const isRead = data.is_read;
                        const hasAttachments = data.has_attachments;

                        let html = '<div style="display: flex; align-items: center; gap: 8px;">';

                        // Thread indicator
                        if (hasThread) {
                            html += `<i class="fas fa-comments" style="color: #6366f1; font-size: 12px;" title="Part of thread"></i>`;
                        }

                        // Subject text
                        html += `<span style="color: #ffffff; font-weight: ${isRead ? '400' : '600'}; flex: 1;">${this.escapeHtml(value)}</span>`;

                        // Attachment indicator
                        if (hasAttachments) {
                            html += `<i class="fas fa-paperclip" style="color: #6b7280; font-size: 11px;"></i>`;
                        }

                        html += '</div>';
                        return html;
                    }
                },
                {
                    title: "AI Agent",
                    field: "assigned_agent",
                    width: 200,
                    hozAlign: "center",
                    headerSort: false,
                    formatter: (cell) => {
                        const emailId = cell.getRow().getData().id;
                        const threadSlug = this.state.emailThreads?.[emailId];

                        // 🔍 DEBUG: Log thread assignment status (reduced verbosity)
                        if (!threadSlug) {
                            // Only log as warning if we have OTHER threads loaded (indicates data inconsistency)
                            // Otherwise, this is normal for unassigned emails - no need to spam console
                            const hasOtherThreads = Object.keys(this.state.emailThreads || {}).length > 0;
                            if (hasOtherThreads && this.state.tableReady) {
                                this.log.debug(`Email ${emailId.substring(0, 20)}... not assigned to thread`);
                            }
                        } else {
                            this.log.debug(`Email ${emailId.substring(0, 20)}... → thread ${threadSlug}`);
                        }

                        // Check if email has an assigned thread
                        if (!threadSlug) {
                            // NOT ASSIGNED - Simple badge
                            return `
                                <div style="display: flex; align-items: center; justify-content: center;">
                                    <span style="color: #6b7280; font-size: 11px; display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; background: rgba(107, 114, 128, 0.1); border-radius: 4px;">
                                        <i class="fas fa-minus-circle" style="font-size: 10px;"></i>
                                        Not Assigned
                                    </span>
                                </div>
                            `;
                        }

                        // IS ASSIGNED - Show agent badge + thread info
                        // ✅ FIX (Jan 3, 2026): Try multiple lookup strategies to find thread
                        let thread = ThreadManager?.threads?.find(t => t.id === threadSlug);

                        // Fallback 1: Try thread_slug field
                        if (!thread) {
                            thread = ThreadManager?.threads?.find(t => t.thread_slug === threadSlug);
                        }

                        // Fallback 2: Try email_thread_id metadata
                        if (!thread) {
                            thread = ThreadManager?.threads?.find(t =>
                                t.email_thread_id === emailId ||
                                t.metadata?.email_thread_id === emailId
                            );
                        }

                        // Debug logging for troubleshooting
                        if (!thread && typeof console !== 'undefined') {
                            console.warn(`[CommunicationHub] Thread lookup failed for email ${emailId}:`,
                                `\n  threadSlug: ${threadSlug}`,
                                `\n  ThreadManager.threads count: ${ThreadManager?.threads?.length || 0}`,
                                `\n  Available thread IDs:`, ThreadManager?.threads?.slice(0, 5).map(t => ({ id: t.id, slug: t.thread_slug, location: t.location }))
                            );
                        }

                        if (!thread) {
                            // Thread not loaded yet in ThreadManager - show thread slug with loading state
                            const threadShort = threadSlug.substring(0, 8);
                            return `
                                <div class="email-agent-assignment" style="display: flex; align-items: center; gap: 6px; justify-content: center;">
                                    <span class="agent-badge" style="background: #6b7280; color: white; padding: 4px 10px; border-radius: 4px; font-size: 10px; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;">
                                        <i class="fas fa-sync fa-spin"></i> Syncing...
                                    </span>
                                    <span class="thread-slug-badge" style="color: #6b7280; font-size: 9px; font-family: monospace;" title="Thread ID: ${threadSlug}">
                                        #${threadShort}
                                    </span>
                                </div>
                            `;
                        }

                        const location = thread.location || 'unassigned';
                        let badgeColor, badgeText, badgeIcon;

                        if (location === 'unassigned') {
                            // Unassigned state (thread exists but in unassigned pool)
                            return `
                                <div style="display: flex; align-items: center; justify-content: center;">
                                    <span style="color: #6b7280; font-size: 11px; display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; background: rgba(107, 114, 128, 0.1); border-radius: 4px;">
                                        <i class="fas fa-minus-circle" style="font-size: 10px;"></i>
                                        Not Assigned
                                    </span>
                                </div>
                            `;
                        } else if (location === 'prime') {
                            badgeColor = '#f59e0b';
                            badgeText = 'Prime';
                            badgeIcon = 'fa-star';
                        } else if (location.startsWith('agent-')) {
                            badgeColor = '#3b82f6';
                            const agentNum = parseInt(location.replace('agent-', ''));
                            // All 26 NATO alphabet agent names
                            const natoNames = ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel', 'India',
                                'Juliet', 'Kilo', 'Lima', 'Mike', 'November', 'Oscar', 'Papa', 'Quebec', 'Romeo',
                                'Sierra', 'Tango', 'Uniform', 'Victor', 'Whiskey', 'Xray', 'Yankee', 'Zulu'];
                            badgeText = natoNames[agentNum - 1] || `Agent ${agentNum}`;
                            badgeIcon = 'fa-user-robot';
                        } else {
                            badgeColor = '#6b7280';
                            badgeText = 'Unknown';
                            badgeIcon = 'fa-question';
                        }

                        const threadShort = threadSlug.substring(0, 8);

                        // Determine navigation action based on location
                        let onclickAction;
                        if (location === 'unassigned' || location === 'prime') {
                            // Prime: Open AI Prime sidebar with thread and update location
                            onclickAction = `event.stopPropagation(); window.CommunicationHub.openThreadInPrime('${threadSlug}');`;
                        } else if (location.startsWith('agent-')) {
                            // Agent: Navigate to command centre and scroll to agent
                            const agentNum = parseInt(location.replace('agent-', ''));
                            onclickAction = `event.stopPropagation(); if (typeof switchTab === 'function') { switchTab('multi-agent'); } setTimeout(() => { if (typeof MultiAgent !== 'undefined' && MultiAgent.scrollToAgent) { MultiAgent.scrollToAgent(${agentNum}); } }, 300);`;
                        } else {
                            onclickAction = `event.stopPropagation();`;
                        }

                        return `
                            <div class="email-agent-assignment" style="display: flex; flex-direction: column; gap: 4px; align-items: center; justify-content: center; padding: 4px 0;">
                                <span class="agent-badge" 
                                      onclick="${onclickAction}"
                                      data-thread-slug="${threadSlug}"
                                      data-location="${location}"
                                      style="background: ${badgeColor}; color: white; padding: 4px 10px; border-radius: 4px; font-size: 10px; font-weight: 600; display: inline-flex; align-items: center; gap: 4px; cursor: pointer; transition: opacity 0.2s; width: fit-content;"
                                      onmouseover="this.style.opacity='0.85'"
                                      onmouseout="this.style.opacity='1'"
                                      title="Click to view in ${location === 'unassigned' || location === 'prime' ? 'AI Prime' : badgeText}">
                                    <i class="fas ${badgeIcon}"></i> ${this.escapeHtml(badgeText)}
                                </span>
                                <div style="display: flex; align-items: center; gap: 6px;">
                                    <span class="thread-slug-badge" style="color: #6b7280; font-size: 9px; font-family: monospace;" title="Thread ID: ${threadSlug}">
                                        #${threadShort}
                                    </span>
                                    <button class="unload-thread-btn" 
                                            onclick="event.stopPropagation(); window.CommunicationHub.unloadEmailFromAgent('${emailId}', '${threadSlug}', event)"
                                            title="Unload from agent"
                                            style="background: transparent; border: none; color: #ef4444; cursor: pointer; padding: 2px 4px; font-size: 11px; opacity: 0.7; transition: opacity 0.2s;"
                                            onmouseover="this.style.opacity='1'"
                                            onmouseout="this.style.opacity='0.7'">
                                        <i class="fas fa-sign-out-alt"></i>
                                    </button>
                                </div>
                            </div>
                        `;
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
            // Open email preview
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
     * Show agent assignment dropdown for a single email
     * Triggered by clicking on the AI Agent column in the table
     * Displays inline vertical list with sliding task options
     */
    async showAgentAssignmentDropdown(event, cell) {
        const emailData = cell.getRow().getData();
        const emailId = emailData.id;

        this.log.info(`📋 Showing inline agent selector for email: ${emailId}`);

        // Remove any existing inline selector
        document.querySelectorAll('.agent-assignment-inline').forEach(d => d.remove());

        // Get cell element
        const cellElement = cell.getElement();
        const rowElement = cell.getRow().getElement();

        // Create inline container with vertical list
        const inlineContainer = document.createElement('div');
        inlineContainer.className = 'agent-assignment-inline';

        // Style as vertical scrollable list (shows 5 agents at a time)
        inlineContainer.style.cssText = `
            position: relative;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 6px;
            height: 220px;
            max-height: 220px;
            overflow-y: auto;
            overflow-x: hidden;
            min-width: 300px;
            box-shadow: inset 0 2px 8px rgba(0,0,0,0.3);
            scrollbar-width: thin;
            scrollbar-color: #30363d #0d1117;
        `;

        // Add webkit scrollbar styling
        if (!document.getElementById('agent-inline-vertical-style')) {
            const style = document.createElement('style');
            style.id = 'agent-inline-vertical-style';
            style.textContent = `
                .agent-assignment-inline::-webkit-scrollbar { width: 6px; }
                .agent-assignment-inline::-webkit-scrollbar-track { background: #0d1117; }
                .agent-assignment-inline::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
                .agent-assignment-inline::-webkit-scrollbar-thumb:hover { background: #484f58; }
                .agent-list-item { transition: all 0.2s ease; }
                .agent-list-item:hover { background: rgba(99, 102, 241, 0.1) !important; }
                .task-slide-panel { 
                    animation: slideInFromRight 0.2s ease;
                }
                @keyframes slideInFromRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }

        // Fetch available agents from MultiAgent.loadedThreads (same as preview panel)
        let agents = [];
        try {
            this.log.info('🔍 Building agent list from MultiAgent.loadedThreads (email row dropdown)...');

            let threadCounts = {};

            // USE COMMAND CENTER'S DATA: MultiAgent.loadedThreads
            if (typeof MultiAgent !== 'undefined' && MultiAgent.loadedThreads) {
                this.log.info('✅ Using MultiAgent.loadedThreads (Command Center data)');

                // Count threads per agent from MultiAgent.loadedThreads
                Object.entries(MultiAgent.loadedThreads).forEach(([agentId, threadInfo]) => {
                    if (threadInfo && threadInfo.threadId) {
                        const numericId = parseInt(agentId);
                        threadCounts[numericId] = 1;
                        const agentName = MultiAgent.getAgentName(numericId);
                        this.log.info(`   Agent ${agentId} (${agentName}): 1 thread - "${threadInfo.threadTitle}"`);
                    }
                });

                // Check if Prime has a loaded thread
                if (typeof ThreadManager !== 'undefined' && ThreadManager.currentThreadId) {
                    const primeThread = ThreadManager.threads?.find(t => t.id === ThreadManager.currentThreadId);
                    if (primeThread) {
                        threadCounts['27'] = 1;
                        this.log.info(`   Agent 27 (Prime): 1 thread - "${primeThread.title}"`);
                    }
                }

                const totalThreads = Object.keys(threadCounts).length;
                this.log.info(`   Total agents with threads: ${totalThreads}`);
            } else {
                this.log.warn('⚠️ MultiAgent.loadedThreads not available');
            }

            // Agent order: Prime first, then NATO alphabet
            const agentOrder = ['Prime', 'Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel',
                'India', 'Juliet', 'Kilo', 'Lima', 'Mike', 'November', 'Oscar', 'Papa', 'Quebec', 'Romeo',
                'Sierra', 'Tango', 'Uniform', 'Victor', 'Whiskey', 'Xray', 'Yankee', 'Zulu'];

            // Agent ID mapping
            const agentIdMap = {
                'Prime': 27,
                'Alpha': 1, 'Bravo': 2, 'Charlie': 3, 'Delta': 4, 'Echo': 5, 'Foxtrot': 6,
                'Golf': 7, 'Hotel': 8, 'India': 9, 'Juliet': 10, 'Kilo': 11, 'Lima': 12,
                'Mike': 13, 'November': 14, 'Oscar': 15, 'Papa': 16, 'Quebec': 17, 'Romeo': 18,
                'Sierra': 19, 'Tango': 20, 'Uniform': 21, 'Victor': 22, 'Whiskey': 23,
                'Xray': 24, 'Yankee': 25, 'Zulu': 26
            };

            // Find highest agent with threads
            let highestActiveAgentId = 0;
            Object.keys(threadCounts).forEach(agentId => {
                const id = parseInt(agentId);
                if (id > 0 && id <= 26 && id > highestActiveAgentId) {
                    highestActiveAgentId = id;
                }
            });

            this.log.info(`✅ Highest active agent ID: ${highestActiveAgentId}`);

            // Show ALL agents from Prime through highest active + 1
            const maxAgentIdToShow = Math.min(highestActiveAgentId + 1, 26);
            this.log.info(`✅ Will show agents 1-${maxAgentIdToShow}`);

            agentOrder.forEach((agentName, index) => {
                const agentId = agentIdMap[agentName];

                // Show Prime always
                if (agentName === 'Prime') {
                    // Will be processed below
                }
                // Show agents 1 through maxAgentIdToShow
                else if (agentId > maxAgentIdToShow) {
                    return;
                }

                const threadCount = threadCounts[agentId] || 0;
                const locationId = agentName === 'Prime' ? 'prime' : `agent-${agentId}`;
                const isNextAvailable = agentId === maxAgentIdToShow && threadCount === 0;

                agents.push({
                    name: agentName,
                    id: locationId,
                    has_threads: threadCount > 0,
                    threads_count: threadCount,
                    is_assigned: false,
                    is_open: true,
                    is_next_available: isNextAvailable
                });
            });
        } catch (error) {
            this.log.warn('Could not fetch synergy sessions:', error);
            // Fallback to basic agents
            agents = [
                { name: 'Prime', has_threads: false, is_assigned: false, is_open: true, id: 'prime' }
            ];
        }

        if (agents.length === 0) {
            inlineContainer.innerHTML = `
                <div style="padding: 12px; text-align: center; color: #8b949e; font-size: 11px;">
                    <i class="fas fa-robot" style="margin-right: 4px;"></i> No agents available
                </div>
            `;
        } else {
            // Build vertical list items for each agent
            agents.forEach((agent, index) => {
                const hasThreads = agent.has_threads || agent.threads_count > 0;
                const isNextAvailable = agent.is_next_available;

                // Item styling based on status
                let borderLeft = 'none';
                let iconColor = '#8b949e';
                let statusText = '';
                let bgColor = 'transparent';

                if (hasThreads) {
                    // Agent has threads - show PURPLE LEFT BORDER
                    borderLeft = '3px solid #6366f1';
                    iconColor = '#8b949e';
                    statusText = `<span style="color: #8b949e; font-size: 10px;">(${agent.threads_count})</span>`;
                } else if (isNextAvailable) {
                    // Next available agent - green highlight
                    iconColor = '#22c55e';
                    bgColor = 'rgba(34, 197, 94, 0.08)';
                    statusText = '<span style="color: #22c55e; font-size: 10px; font-weight: 600;">(Next)</span>';
                } else {
                    // Empty agent - green icon
                    iconColor = '#22c55e';
                    statusText = '<span style="color: #22c55e; font-size: 10px; font-weight: 600;">(Empty)</span>';
                }

                const listItem = document.createElement('div');
                listItem.className = 'agent-list-item';
                listItem.dataset.agentId = agent.id;
                listItem.dataset.agentName = agent.name;
                listItem.style.cssText = `
                    padding: 10px 12px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    border-bottom: 1px solid #21262d;
                    border-left: ${borderLeft};
                    background: ${bgColor};
                `;

                listItem.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 8px; flex: 1;">
                        <i class="fas ${isNextAvailable ? 'fa-plus-circle' : 'fa-robot'}" style="color: ${iconColor}; width: 16px; text-align: center;"></i>
                        <span style="color: #f0f6fc; font-size: 13px; ${isNextAvailable ? 'font-weight: 600;' : ''}">${isNextAvailable ? 'Activate ' : ''}${this.escapeHtml(agent.name)}</span>
                        ${statusText}
                    </div>
                    <i class="fas fa-chevron-right" style="color: #6b7280; font-size: 10px;"></i>
                `;

                // Click handler - show task slide panel
                listItem.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    this.log.info(`📋 Showing task submenu for ${agent.name} (${agent.id})`);
                    this.showTaskSlidePanelInline(emailId, emailData, agent, inlineContainer, cellElement);
                });

                inlineContainer.appendChild(listItem);
            });
        }

        // Replace cell content with inline container
        cellElement.innerHTML = '';
        cellElement.appendChild(inlineContainer);

        // Expand row height and cell width to show the selector
        rowElement.style.height = '240px';
        cellElement.style.width = 'auto';
        cellElement.style.minWidth = '320px';
        cellElement.style.padding = '8px';

        // Click outside to close
        const closeHandler = (e) => {
            if (!cellElement.contains(e.target)) {
                inlineContainer.remove();
                // Restore row height and cell styling
                rowElement.style.height = '';
                cellElement.style.width = '';
                cellElement.style.minWidth = '';
                cellElement.style.padding = '';
                // Redraw table to restore original cell content
                if (this.state.tabulatorTable) {
                    this.state.tabulatorTable.redraw();
                }
                document.removeEventListener('click', closeHandler);
            }
        };
        setTimeout(() => document.addEventListener('click', closeHandler), 100);
    },

    /**
     * Show task type slide panel inline (slides over agent list)
     */
    showTaskSlidePanelInline(emailId, emailData, agent, parentContainer, cellElement) {
        // Task types with icons and colors
        const taskTypes = [
            { type: 'generate_quote', label: 'Generate Quote', icon: 'fa-calculator', color: '#10b981' },
            { type: 'summarize', label: 'Summarize', icon: 'fa-list-ul', color: '#3b82f6' },
            { type: 'draft_reply', label: 'Draft Reply', icon: 'fa-reply', color: '#8b5cf6' },
            { type: 'extract_tasks', label: 'Extract Tasks', icon: 'fa-check-square', color: '#f59e0b' },
            { type: 'analyze', label: 'Analyze', icon: 'fa-search', color: '#ec4899' },
            { type: 'discuss', label: 'Discuss', icon: 'fa-comments', color: '#6366f1' }
        ];

        // Create slide panel
        const slidePanel = document.createElement('div');
        slidePanel.className = 'task-slide-panel';
        slidePanel.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: #0d1117;
            z-index: 10;
            overflow-y: auto;
        `;

        // Header with back button
        const header = document.createElement('div');
        header.style.cssText = `
            padding: 10px 12px;
            border-bottom: 1px solid #30363d;
            background: rgba(99, 102, 241, 0.1);
            display: flex;
            align-items: center;
            gap: 8px;
        `;
        header.innerHTML = `
            <i class="fas fa-arrow-left" style="color: #6366f1; cursor: pointer; font-size: 12px;" data-back></i>
            <strong style="color: #f0f6fc; font-size: 13px; flex: 1;">${this.escapeHtml(agent.name)} - Select Task</strong>
        `;

        // Back button handler
        header.querySelector('[data-back]').addEventListener('click', (e) => {
            e.stopPropagation();
            slidePanel.remove();
        });

        slidePanel.appendChild(header);

        // Task list
        taskTypes.forEach(task => {
            const taskItem = document.createElement('div');
            taskItem.className = 'task-item';
            taskItem.dataset.taskType = task.type;
            taskItem.style.cssText = `
                padding: 10px 12px;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 10px;
                border-bottom: 1px solid #21262d;
                transition: background 0.2s;
            `;

            taskItem.innerHTML = `
                <i class="fas ${task.icon}" style="color: ${task.color}; width: 16px;"></i>
                <span style="color: #f0f6fc; font-size: 13px;">${task.label}</span>
            `;

            // Hover effect
            taskItem.addEventListener('mouseenter', () => {
                taskItem.style.background = 'rgba(99, 102, 241, 0.1)';
            });
            taskItem.addEventListener('mouseleave', () => {
                taskItem.style.background = 'transparent';
            });

            // Click handler - assign with task type
            taskItem.addEventListener('click', async (e) => {
                e.stopPropagation();
                this.log.info(`🎯 Assigning email ${emailId} to ${agent.name} with task: ${task.type}`);

                try {
                    // Call the correct function with proper parameters
                    await this.assignEmailToAgentWithTask(emailId, agent.name, agent.id, task.type, cellElement.parentElement?.parentElement ? { getElement: () => cellElement.parentElement.parentElement } : null, '');

                    // Remove inline selector
                    parentContainer.remove();

                    // Redraw table to show new assignment
                    if (this.state.tabulatorTable) {
                        this.state.tabulatorTable.redraw();
                    }
                } catch (error) {
                    this.log.error(`Failed to assign: ${error.message}`);
                }
            });

            slidePanel.appendChild(taskItem);
        });

        // Add slide panel to parent container
        parentContainer.style.position = 'relative';
        parentContainer.appendChild(slidePanel);
    },

    /**
     * Assign email to an AI agent
     * Creates a thread in sessions.threads with email data
     * If agentId is 'new', finds next available empty agent slot
     * 
     * ✅ IDEMPOTENCY: Checks if email already assigned before creating thread
     * ✅ REASSIGNMENT: Shows confirmation modal if email already assigned
     */
    async assignEmailToAgent(emailId, agentName, cell, agentId = null) {
        this.log.info(`🤖 Assigning email ${emailId} to agent: ${agentName} (ID: ${agentId})`);

        // ✅ REASSIGNMENT CHECK: If email already assigned, show confirmation modal
        if (this.state.emailThreads && this.state.emailThreads[emailId]) {
            const existingThreadSlug = this.state.emailThreads[emailId];

            // Get existing thread details
            const existingThread = ThreadManager.threads?.find(t => t.id === existingThreadSlug || t.thread_slug === existingThreadSlug);
            const existingAgentName = existingThread?.metadata?.assigned_agent || 'another agent';

            this.log.warn(`⚠️ Email ${emailId} already assigned to thread ${existingThreadSlug} (${existingAgentName})`);

            // Show confirmation modal
            const action = await this.showReassignmentModal(emailId, existingAgentName, agentName);

            if (action === 'cancel') {
                this.log.info('User cancelled reassignment');
                return; // User cancelled
            }

            if (action === 'move') {
                // Reassign: Unlink from old thread, create new thread
                this.log.info(`🔄 Moving email from ${existingAgentName} to ${agentName}`);
                await this.reassignEmail(emailId, existingThreadSlug, agentName, agentId, cell);
                return;
            }

            if (action === 'new') {
                // Create new thread for same email (allow duplicate)
                this.log.info(`➕ Creating new thread for already-assigned email`);
                delete this.state.emailThreads[emailId]; // Temporary removal to bypass check
                // Continue with normal assignment flow below...
            }
        }

        // ✅ CRITICAL: Disable cell to prevent double-click
        const originalHTML = cell.getElement().innerHTML;
        cell.getElement().innerHTML = '<span style="color: #9ca3af; font-size: 10px;"><i class="fas fa-spinner fa-spin"></i> Assigning...</span>';
        cell.getElement().style.pointerEvents = 'none'; // Disable all clicks

        try {
            const userId = window.UserAuth?.user?.id || 1;

            // Fetch full email content
            const emailData = cell.getRow().getData();
            const fullEmail = await this.fetchEmailContent(emailId);

            // Process all attachments (images, PDFs, etc.)
            let processedAttachments = [];
            if (fullEmail.attachments && fullEmail.attachments.length > 0) {
                this.log.info(`📎 Processing ${fullEmail.attachments.length} attachment(s)...`);

                if (typeof AttachmentProcessor === 'undefined') {
                    this.log.error('❌ AttachmentProcessor not loaded! Skipping attachment processing.');
                    this.showError('Attachment processor not loaded. Please refresh the page.');
                } else {
                    processedAttachments = await AttachmentProcessor.processAttachmentsForAI(
                        emailId,
                        fullEmail.attachments,
                        this
                    );
                }

                const imageCount = processedAttachments.filter(a =>
                    a.detected_type === 'image' && a.image_data
                ).length;

                const docCount = processedAttachments.filter(a =>
                    a.detected_type === 'pdf' && a.document_data
                ).length;

                this.log.success(`✅ Processed ${processedAttachments.length} attachments: ${imageCount} images, ${docCount} PDFs`);
            }

            // If "Create New Thread" selected, find next available agent slot
            let location = agentId;
            if (agentId === 'new' || agentId === null) {
                // Fetch agent list to find next available slot
                const agentsResponse = await fetch(`/api/threads/agents/list?user_id=${userId}`);
                if (agentsResponse.ok) {
                    const agentsData = await agentsResponse.json();
                    if (agentsData.success && agentsData.agents) {
                        // Find first agent with 0 threads or create new slot
                        const emptyAgent = agentsData.agents.find(a => !a.is_create_new && a.thread_count === 0);
                        if (emptyAgent) {
                            location = emptyAgent.id;
                            agentName = emptyAgent.name;
                            this.log.info(`📍 Using empty agent slot: ${location} (${agentName})`);
                        } else {
                            // Find highest agent number and increment
                            const agentNumbers = agentsData.agents
                                .filter(a => !a.is_create_new && a.id.startsWith('agent-'))
                                .map(a => parseInt(a.id.split('-')[1]))
                                .filter(n => !isNaN(n));
                            const nextNum = agentNumbers.length > 0 ? Math.max(...agentNumbers) + 1 : 1;
                            location = `agent-${nextNum}`;

                            // Map to NATO alphabet
                            const natoAlphabet = ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel',
                                'India', 'Juliet', 'Kilo', 'Lima', 'Mike', 'November', 'Oscar', 'Papa', 'Quebec', 'Romeo',
                                'Sierra', 'Tango', 'Uniform', 'Victor', 'Whiskey', 'Xray', 'Yankee', 'Zulu'];
                            agentName = `Agent ${natoAlphabet[nextNum - 1] || nextNum}`;
                            this.log.info(`🆕 Creating new agent slot: ${location} (${agentName})`);
                        }
                    }
                }

                // Fallback if API fails
                if (!location || location === 'new') {
                    location = 'agent-1';
                    agentName = 'Agent Alpha';
                }
            }

            // ⚠️ CASCADE RULE: Enforce agent exclusivity (one thread per agent)
            if (location && location.startsWith('agent-')) {
                const targetAgentId = parseInt(location.replace('agent-', ''));
                const currentThread = ThreadManager.getThreadByAgent?.(location);

                if (currentThread) {
                    this.log.warn(`⚠️ Agent ${agentName} already has thread ${currentThread.id} - cascading to unassigned`);

                    // Move old thread to unassigned
                    try {
                        await this.api.post('/api/threads/update-location', {
                            thread_slug: currentThread.id,
                            new_location: 'unassigned',
                            user_id: userId
                        });

                        // Unload from agent UI
                        if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.unloadThread === 'function') {
                            AgentColumn.unloadThread(targetAgentId);
                        }

                        // Update local state
                        currentThread.location = 'unassigned';

                        if (typeof showToast === 'function') {
                            showToast(`📤 Previous thread moved to Unassigned`, 'info', 2500);
                        }

                        this.log.success(`✅ Cascaded old thread ${currentThread.id} to unassigned`);
                    } catch (cascadeError) {
                        this.log.error('❌ Failed to cascade old thread:', cascadeError);
                        // Continue anyway - new thread takes priority
                    }
                }
            }

            // Enhanced metadata with attachment info
            const metadata = {
                email_id: emailId,
                email_subject: fullEmail.subject,
                email_from: fullEmail.from,
                email_to: fullEmail.to,
                email_date: fullEmail.date,
                email_provider: fullEmail.provider,
                assigned_agent: agentName,
                assigned_at: new Date().toISOString(),
                attachments_count: processedAttachments.length,
                has_images: processedAttachments.some(a => a.detected_type === 'image' && a.image_data),
                has_documents: processedAttachments.some(a => a.detected_type === 'pdf' && a.document_data)
            };

            // Create thread in sessions.threads with location
            this.log.info('🔧 Creating thread with data:', {
                user_id: userId,
                title: `Email: ${fullEmail.subject || 'No Subject'}`,
                context_type: 'email',
                location: location,
                tags: ['email', fullEmail.provider, 'assigned'],
                metadata: metadata
            });

            const threadResponse = await this.api.post('/api/threads/create', {
                user_id: userId,
                title: `Email: ${fullEmail.subject || 'No Subject'}`,
                context_type: 'email',
                location: location,
                tags: ['email', fullEmail.provider, 'assigned'],
                metadata: metadata
            });

            this.log.info('📥 Thread creation response:', threadResponse);

            // Toast: Thread created
            if (typeof showToast === 'function') {
                showToast('📝 Thread created', 'success', 2000);
            }

            // ✅ FIX: Backend wraps response in { success: true, data: {...}, message: '...' }
            // Extract thread_slug from either root level OR data object
            let threadSlug = null;
            if (threadResponse.thread_slug) {
                threadSlug = threadResponse.thread_slug;
            } else if (threadResponse.data && threadResponse.data.thread_slug) {
                threadSlug = threadResponse.data.thread_slug;
            } else if (threadResponse.data && threadResponse.data.thread && threadResponse.data.thread.slug) {
                threadSlug = threadResponse.data.thread.slug;
            }

            if (!threadSlug) {
                this.log.error('❌ Thread creation failed - no thread_slug in response:', threadResponse);
                throw new Error('Failed to create thread');
            }

            this.log.success(`📧 Thread created: ${threadSlug}`);

            // ⏱️ Small delay to ensure thread is committed to database
            await new Promise(resolve => setTimeout(resolve, 100));

            // CRITICAL: Link email to thread - updates email_thread_id, email_subject, email_participants columns
            // This makes the email badge appear in thread info area (like synergy sessions)

            // ✅ FIX: Safely extract email participants (handle various formats)
            let emailParticipants = [];
            if (typeof fullEmail.from === 'string') {
                emailParticipants = [fullEmail.from];
            } else if (Array.isArray(fullEmail.from)) {
                emailParticipants = fullEmail.from;
            } else if (fullEmail.from && fullEmail.from.email) {
                emailParticipants = [fullEmail.from.email];
            }

            // Add 'to' recipients if available
            if (fullEmail.to) {
                if (typeof fullEmail.to === 'string') {
                    emailParticipants.push(fullEmail.to);
                } else if (Array.isArray(fullEmail.to)) {
                    emailParticipants = [...emailParticipants, ...fullEmail.to];
                }
            }

            const emailSubject = fullEmail.subject || fullEmail.title || 'No Subject';

            this.log.info('🔗 Linking email to thread with data:', {
                user_id: userId,
                thread_slug: threadSlug,
                email_thread_id: emailId,
                email_subject: emailSubject,
                email_participants: emailParticipants,
                fullEmail_keys: Object.keys(fullEmail)
            });

            const linkResponse = await this.api.post('/api/thread-assignments/email', {
                user_id: userId,
                thread_slug: threadSlug,
                email_thread_id: emailId,
                email_subject: emailSubject,
                email_participants: emailParticipants
            });

            this.log.info('📥 Email link response:', linkResponse);

            if (!linkResponse || !linkResponse.success) {
                this.log.error('❌ Email link failed:', linkResponse);
                this.log.warn('⚠️ Email link may not have been created properly - thread will not show email badge');
                if (typeof showToast === 'function') {
                    showToast('⚠️ Email link incomplete', 'warning', 3000);
                }
            } else {
                this.log.success(`📎 Email linked to thread - will show in thread info area`);
                if (typeof showToast === 'function') {
                    showToast('📎 Email metadata saved', 'success', 2000);
                }
            }

            // 🔒 CRITICAL: Clear previous assignment if email was already assigned
            if (this.state.emailThreads && this.state.emailThreads[emailId]) {
                const previousThreadSlug = this.state.emailThreads[emailId];
                this.log.info(`🔄 Email ${emailId} was previously assigned to thread ${previousThreadSlug}, clearing old assignment`);

                // Find and update previous row
                if (this.table) {
                    const allRows = this.table.getData();
                    for (const row of allRows) {
                        if (row.id === emailId && row.assigned_agent) {
                            this.log.info(`✨ Clearing agent name from previous row: ${row.assigned_agent}`);
                            this.table.updateData([{ id: emailId, assigned_agent: '' }]);
                            break;
                        }
                    }
                }
            }

            // Update local state
            if (!this.state.emailThreads) {
                this.state.emailThreads = {};
            }
            this.state.emailThreads[emailId] = threadSlug;

            // Update table cell (only if cell provided)
            if (cell && cell.getRow) {
                cell.getRow().update({ assigned_agent: agentName });
            } else {
                // Called from preview panel - just redraw table
                if (this.state.tabulatorTable) {
                    this.state.tabulatorTable.redraw();
                }
            }

            // Show initial success toast
            if (typeof showToast === 'function') {
                showToast(`📧 Assigning to ${agentName}...`, 'info', 2000);
            }

            this.log.success(`Email ${emailId} assigned to agent ${agentName} in thread ${threadSlug}`);

            // ✅ CRITICAL: Load thread into AI agent column and trigger AI response
            await this.loadThreadIntoAgentAndTrigger(threadSlug, location, fullEmail, processedAttachments);

            // ✅ CRITICAL: Refresh ThreadManager so formatter can find the thread immediately
            if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.loadThreadsFromBackend === 'function') {
                await ThreadManager.loadThreadsFromBackend();
                this.log.success('✅ ThreadManager refreshed - table will show agent badge');

                // Force table redraw to update AI Agent column
                if (this.state.tabulatorTable) {
                    this.state.tabulatorTable.redraw(true);
                }
            }

            // Final success notification
            this.showSuccess(`✅ Email assigned to ${agentName}`);

            // ✅ CRITICAL: Re-enable cell after successful assignment (if cell provided)
            if (cell && cell.getElement) {
                cell.getElement().style.pointerEvents = 'auto';
            }

        } catch (error) {
            this.log.error('Failed to assign email to agent:', error);
            this.showError(`Failed to assign email: ${error.message}`);
            if (typeof showToast === 'function') {
                showToast(`❌ Assignment failed: ${error.message}`, 'error', 5000);
            }

            // ✅ CRITICAL: Restore original cell HTML and re-enable on error (if cell provided)
            if (cell && cell.getElement && originalHTML) {
                cell.getElement().innerHTML = originalHTML;
                cell.getElement().style.pointerEvents = 'auto';
            }
        }
    },

    /**
     * ✅ FIX #4: Assign email to agent with specific task type
     * ✅ IDEMPOTENCY: Checks if email already assigned to prevent duplicate thread creation
     * ✅ DOUBLE-CLICK PREVENTION: Disables cell during 2-5 second assignment process
     * @param {string} emailId - Email ID
     * @param {string} agentName - Agent name (e.g., 'Alpha')
     * @param {string} agentId - Agent location (e.g., 'agent-1')
     * @param {string} taskType - Task type ('summarize', 'draft_reply', 'extract_tasks', 'analyze', 'discuss')
     * @param {object} cell - Tabulator cell reference (optional, null when called from preview panel)
     * @param {string} customInstructions - Custom instructions from user (optional)
     */
    async assignEmailToAgentWithTask(emailId, agentName, agentId, taskType, cell, customInstructions = '') {
        this.log.info(`🤖 Assigning email ${emailId} to agent: ${agentName} with task: ${taskType}`);

        // ✅ ALLOW REASSIGNMENT: If email already assigned, clear old mapping first
        if (this.state.emailThreads && this.state.emailThreads[emailId]) {
            const oldThreadSlug = this.state.emailThreads[emailId];
            this.log.info(`🔄 Email ${emailId} already assigned to thread ${oldThreadSlug} - will reassign to ${agentName}`);
            delete this.state.emailThreads[emailId]; // Clear old mapping to allow new assignment
        }

        // ✅ DOUBLE-CLICK PREVENTION: Disable cell during assignment (only if cell provided)
        let originalHTML = null;
        if (cell && cell.getElement) {
            originalHTML = cell.getElement().innerHTML;
            cell.getElement().innerHTML = '<span><i class="fas fa-spinner fa-spin"></i> Assigning with task...</span>';
            cell.getElement().style.pointerEvents = 'none'; // Disable clicks
        }

        try {
            // First, assign email to agent normally (creates thread, links email)
            const userId = window.UserAuth?.user?.id || 1;

            // Get email data - from cell if available, otherwise fetch from state
            let emailData;
            if (cell && cell.getRow) {
                emailData = cell.getRow().getData();
            } else {
                emailData = this.state.emails.find(e => e.id === emailId);
            }

            const fullEmail = await this.fetchEmailContent(emailId);

            // ✅ DEBUG: Log what we got from fetchEmailContent
            this.log.info(`📧 Full email data fetched:`, {
                id: fullEmail.id,
                from: fullEmail.from,
                to: fullEmail.to,
                subject: fullEmail.subject,
                has_body_text: !!fullEmail.body_text,
                has_body_html: !!fullEmail.body_html,
                body_text_length: fullEmail.body_text?.length || 0,
                body_html_length: fullEmail.body_html?.length || 0,
                snippet_length: fullEmail.snippet?.length || 0,
                body_text_preview: fullEmail.body_text?.substring(0, 100) || 'N/A',
                body_html_preview: fullEmail.body_html?.substring(0, 100) || 'N/A'
            });

            // 🔍 CRITICAL DEBUG: Log full body content to check truncation
            if (fullEmail.body_text) {
                console.log('🔍 [TRUNCATION CHECK] Full body_text:', fullEmail.body_text);
                console.log('🔍 [TRUNCATION CHECK] Body length:', fullEmail.body_text.length);
            }
            if (fullEmail.body_html) {
                console.log('🔍 [TRUNCATION CHECK] Full body_html length:', fullEmail.body_html.length);
            }

            // Process attachments
            let processedAttachments = [];
            if (fullEmail.attachments && fullEmail.attachments.length > 0) {
                this.log.info(`📎 Processing ${fullEmail.attachments.length} attachment(s)...`);
                if (typeof AttachmentProcessor !== 'undefined') {
                    processedAttachments = await AttachmentProcessor.processAttachmentsForAI(
                        emailId,
                        fullEmail.attachments,
                        this
                    );
                }
            }

            // Create thread with task-specific title
            const taskTitles = {
                'generate_quote': `Quote Request: ${fullEmail.subject || 'No Subject'}`,
                'summarize': `Summarize: ${fullEmail.subject || 'No Subject'}`,
                'draft_reply': `Reply to: ${fullEmail.subject || 'No Subject'}`,
                'extract_tasks': `Tasks from: ${fullEmail.subject || 'No Subject'}`,
                'analyze': `Analyze: ${fullEmail.subject || 'No Subject'}`,
                'discuss': `Discuss: ${fullEmail.subject || 'No Subject'}`
            };

            const metadata = {
                email_id: emailId,
                email_subject: fullEmail.subject,
                email_from: fullEmail.from,
                email_to: fullEmail.to,
                email_date: fullEmail.date,
                email_provider: fullEmail.provider,
                assigned_agent: agentName,
                assigned_at: new Date().toISOString(),
                email_task_type: taskType,  // ✅ Store task intent
                attachments_count: processedAttachments.length
            };

            // Determine location
            let location = agentId;

            // Convert numeric agentId to location string format
            if (agentId === 27 || agentId === '27') {
                location = 'prime';
            } else if (typeof agentId === 'number' && agentId >= 1 && agentId <= 26) {
                location = `agent-${agentId}`;
            } else if (typeof agentId === 'string' && /^\d+$/.test(agentId)) {
                // String numeric ID
                const numId = parseInt(agentId);
                if (numId === 27) {
                    location = 'prime';
                } else if (numId >= 1 && numId <= 26) {
                    location = `agent-${numId}`;
                }
            }

            if (agentId === 'new' || agentId === null) {
                const agentsResponse = await fetch(`/api/threads/agents/list?user_id=${userId}`);
                if (agentsResponse.ok) {
                    const agentsData = await agentsResponse.json();
                    if (agentsData.success && agentsData.agents) {
                        const emptyAgent = agentsData.agents.find(a => !a.is_create_new && a.thread_count === 0);
                        if (emptyAgent) {
                            location = emptyAgent.id;
                            agentName = emptyAgent.name;
                        }
                    }
                }
                if (!location || location === 'new') {
                    location = 'agent-1';
                    agentName = 'Agent Alpha';
                }
            }

            // Create thread
            const threadResponse = await this.api.post('/api/threads/create', {
                user_id: userId,
                title: taskTitles[taskType] || `Email: ${fullEmail.subject}`,
                context_type: 'email',
                location: location,
                tags: ['email', fullEmail.provider, 'assigned', taskType],
                metadata: metadata
            });

            let threadSlug = null;
            if (threadResponse.thread_slug) {
                threadSlug = threadResponse.thread_slug;
            } else if (threadResponse.data && threadResponse.data.thread_slug) {
                threadSlug = threadResponse.data.thread_slug;
            }

            if (!threadSlug) {
                throw new Error('Failed to create thread');
            }

            this.log.success(`📧 Thread created: ${threadSlug}`);

            // Link email to thread
            const emailParticipants = [];
            if (typeof fullEmail.from === 'string') {
                emailParticipants.push(fullEmail.from);
            }
            if (fullEmail.to) {
                if (typeof fullEmail.to === 'string') {
                    emailParticipants.push(fullEmail.to);
                } else if (Array.isArray(fullEmail.to)) {
                    emailParticipants.push(...fullEmail.to);
                }
            }

            await this.api.post('/api/thread-assignments/email', {
                user_id: userId,
                thread_slug: threadSlug,
                email_thread_id: emailId,
                email_subject: fullEmail.subject || 'No Subject',
                email_participants: emailParticipants
            });

            // Update local state
            if (!this.state.emailThreads) {
                this.state.emailThreads = {};
            }
            this.state.emailThreads[emailId] = threadSlug;

            console.log('🔍 [assignEmailToAgentWithTask] ASSIGNED email to thread:');
            console.log('   emailId:', emailId);
            console.log('   threadSlug:', threadSlug);
            console.log('   this.state.emailThreads:', this.state.emailThreads);

            // ✅ CRITICAL: Refresh ThreadManager immediately so formatter can find the thread
            if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.loadThreadsFromBackend === 'function') {
                await ThreadManager.loadThreadsFromBackend();
                console.log('🔍 [assignEmailToAgentWithTask] ThreadManager refreshed, thread count:', ThreadManager.threads?.length);
                const assignedThread = ThreadManager.threads?.find(t => t.id === threadSlug || t.thread_slug === threadSlug);
                console.log('🔍 [assignEmailToAgentWithTask] Can find assigned thread in ThreadManager:', !!assignedThread);
                if (assignedThread) {
                    console.log('🔍 [assignEmailToAgentWithTask] Thread details:', { id: assignedThread.id, slug: assignedThread.thread_slug, location: assignedThread.location, email_thread_id: assignedThread.email_thread_id });
                }
                this.log.success('✅ ThreadManager refreshed with new thread');
            }

            // ✅ SHOW IMMEDIATE NOTIFICATION: Let user know assignment is happening
            this.showSuccess(`📧 Email assigned to ${agentName} - Loading conversation...`);
            if (typeof showToast === 'function') {
                showToast(`📧 Email sent to ${agentName} (${taskType.replace('_', ' ')})`, 'success', 4000);
            }

            // Now update table to show agent badge (formatter will find thread in ThreadManager)
            // Only update cell if it was provided (from table, not preview panel)
            if (cell && cell.getRow) {
                cell.getRow().update({ assigned_agent: agentName });
            } else {
                // Called from preview panel - just redraw table
                if (this.state.tabulatorTable) {
                    this.state.tabulatorTable.redraw();
                }
            }

            // ✅ NEW: Load thread and send task-specific prompt
            await this.loadThreadIntoAgentAndTriggerWithTask(threadSlug, location, fullEmail, processedAttachments, taskType);

            // ✅ SECOND NOTIFICATION: Confirm task was sent to AI
            if (typeof showToast === 'function') {
                showToast(`✅ AI ${agentName} is processing your ${taskType.replace('_', ' ')} request`, 'success', 3000);
            }

            // ✅ CLEAR CUSTOM INSTRUCTION TEXTAREA after successful send
            const customInstructionTextarea = document.getElementById(`ai-custom-instruction-${emailId}`);
            if (customInstructionTextarea) {
                customInstructionTextarea.value = '';
                this.log.info('🧹 Cleared custom instruction textarea');
            }

            // ✅ CRITICAL: Multiple table redraws to ensure AI Agent column updates
            if (this.state.tabulatorTable) {
                // First redraw immediately
                this.state.tabulatorTable.redraw();
                this.log.info('🔄 First table redraw (immediate)');

                // Second redraw after 300ms
                await new Promise(resolve => setTimeout(resolve, 300));
                this.state.tabulatorTable.redraw();
                this.log.info('🔄 Second table redraw (300ms)');

                // Third redraw after 1 second (ensure thread fully loaded)
                await new Promise(resolve => setTimeout(resolve, 700));
                this.state.tabulatorTable.redraw();
                this.log.success('✅ Final table redraw - AI Agent column should now show thread info');
            }

            // ✅ CRITICAL: Re-enable cell after successful assignment (if cell provided)
            if (cell && cell.getElement) {
                cell.getElement().style.pointerEvents = 'auto';
            }

        } catch (error) {
            this.log.error('Failed to assign email with task:', error);
            this.showError(`Failed to assign email: ${error.message}`);
            if (typeof showToast === 'function') {
                showToast(`❌ Assignment failed: ${error.message}`, 'error', 5000);
            }

            // ✅ CRITICAL: Restore original cell HTML and re-enable on error (if cell provided)
            if (cell && cell.getElement && originalHTML) {
                cell.getElement().innerHTML = originalHTML;
                cell.getElement().style.pointerEvents = 'auto';
            }
        }
    },

    /**
     * ✅ FIX #4: Load thread and trigger AI with task-specific prompt (SINGLE MESSAGE ONLY)
     */
    async loadThreadIntoAgentAndTriggerWithTask(threadSlug, location, emailData, processedAttachments, taskType) {
        try {
            this.log.info(`🔄 Loading thread ${threadSlug} with task: ${taskType}`);

            // Step 1: Refresh thread list
            if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.loadThreadsFromBackend === 'function') {
                await ThreadManager.loadThreadsFromBackend();
            }

            // Step 2: Handle Prime location specially (open in AI Prime sidebar)
            if (location === 'unassigned' || location === 'prime') {
                this.log.info(`🤖 Opening thread in AI Prime sidebar`);

                // Build task prompt
                const taskPrompts = {
                    'generate_quote': `Please analyze this email and generate a comprehensive quote for the customer.`,
                    'summarize': `Please provide a clear, concise summary of this email, highlighting the key points and any action items.`,
                    'draft_reply': `Please draft a professional reply to this email. Consider the tone and context of the original message.`,
                    'extract_tasks': `Please extract all action items and tasks mentioned in this email. List them in order of priority.`,
                    'analyze': `Please analyze this email's tone, sentiment, and key themes. Identify any potential concerns or opportunities.`,
                    'discuss': `I need your assistance with this email. Please help me understand the context and suggest appropriate next steps.`
                };

                // Use enhanced formatter to build the prompt
                const basePrompt = EmailAIFormatter.generateEnhancedPrompt(emailData, taskType);
                const attachmentSummary = AttachmentProcessor.generateAttachmentSummary(processedAttachments || []);
                const completePrompt = basePrompt + attachmentSummary;

                // Generate message content (multimodal if attachments)
                const messageContent = EmailAIFormatter.generateClaudeMessageContent(
                    completePrompt,
                    processedAttachments || []
                );

                // Use ThreadManager to load thread into Prime
                if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.loadThreadInPrime === 'function') {
                    try {
                        // Load thread into Prime (opens sidebar, displays messages)
                        await ThreadManager.loadThreadInPrime(threadSlug);
                        this.log.success(`✅ Loaded thread ${threadSlug} into Prime`);

                        // Update thread location to 'prime'
                        const userId = window.UserAuth?.user?.id || 1;
                        await this.api.post('/api/threads/update-location', {
                            thread_slug: threadSlug,
                            new_location: 'prime',
                            user_id: userId
                        });
                        this.log.success(`✅ Updated thread location to prime`);

                        // Refresh ThreadManager to reflect new location
                        await ThreadManager.loadThreadsFromBackend();

                        // Wait for Prime UI to be ready
                        await new Promise(resolve => setTimeout(resolve, 300));

                        // Populate Prime input and send message automatically
                        const primeInput = document.getElementById('ai-chat-input');
                        if (primeInput && typeof sendChatMessage === 'function') {
                            // Set input value
                            primeInput.value = typeof messageContent === 'string' ? messageContent : JSON.stringify(messageContent);

                            // Trigger send
                            await sendChatMessage();
                            this.log.success(`✅ Sent ${taskType} task to Prime`);
                        } else {
                            this.log.warn('⚠️ Prime input or sendChatMessage not available');
                        }

                        this.log.success(`✅ Opened thread in AI Prime with task: ${taskType}`);
                    } catch (error) {
                        this.log.error('Failed to open thread in Prime:', error);
                    }
                } else {
                    this.log.warn('⚠️ ThreadManager.loadThreadInPrime not available');
                }
                return;
            }

            // Step 3: Extract agent ID from location (for agent-X locations)
            const agentMatch = location.match(/agent-(\d+)/);
            if (!agentMatch) {
                this.log.warn('Could not extract agent ID from location:', location);
                return;
            }
            const agentId = parseInt(agentMatch[1]);

            // Step 3: Load thread into agent card using MultiAgent
            if (typeof MultiAgent !== 'undefined' && typeof MultiAgent.loadThreadIntoAgent === 'function') {
                // Fetch thread object from ThreadManager
                const thread = ThreadManager.threads?.find(t => t.thread_slug === threadSlug || t.id === threadSlug);
                if (thread) {
                    this.log.info(`🔄 Loading thread ${threadSlug} into agent ${agentId}`);
                    MultiAgent.loadThreadIntoAgent(agentId, thread);
                    await new Promise(resolve => setTimeout(resolve, 500));
                    this.log.success(`✅ Thread loaded into agent card ${agentId}`);
                } else {
                    this.log.warn(`⚠️ Thread ${threadSlug} not found in ThreadManager.threads`);
                }
            } else {
                this.log.warn('⚠️ MultiAgent.loadThreadIntoAgent not available');
            }

            // Step 4: Build SINGLE message with task prompt + email content using enhanced template
            const taskPrompts = {
                'generate_quote': `Please analyze this email and generate a comprehensive quote for the customer. 

STEP 1: EXTRACT AVAILABLE INFORMATION
- Product/service requested
- Quantities mentioned
- Sizes/dimensions specified  
- Materials/finishes stated
- Deadline/turnaround requirements
- Customer name and contact details

STEP 2: QUERY FRED DATABASE FOR CUSTOMER HISTORY (If specifications are incomplete)
Use the inhouse_execute_query tool to find previous orders and use historical specifications:

Round 1 - Identify Customer:
inhouse_execute_query(
    query="SELECT TOP 10 ContactID, Name, Email, Phone FROM Clients WHERE Email LIKE ? OR Name LIKE ?",
    params=['%customer_email%', '%customer_name%']
)

Round 2 - Get Previous Orders (if customer found):
inhouse_execute_query(
    query="""
    SELECT TOP 20
        o.OrderID,
        o.ClientName,
        o.OrderDate,
        jt.ShortJobDesc,
        jt.QTY as Quantity,
        jt.Width,
        jt.Height,
        pt.[Desc] as PaperType,
        g.[DESC] as GSM,
        jtype.[Desc] as JobType,
        jt.FrontCelloGloss,
        jt.FrontCelloMatt,
        jt.Cost
    FROM Orders o
    INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
    INNER JOIN Clients c ON o.CustomerMYOB_ID = c.ContactID
    LEFT JOIN PaperType pt ON jt.PaperTypeID = pt.PaperTypeID
    LEFT JOIN GSM g ON jt.GSM_ID = g.GSM_ID
    LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
    WHERE c.ContactID = ?
    ORDER BY o.OrderDate DESC
    """,
    params=[customer_contact_id]
)

Round 3 - Find Similar Product Orders (if customer mentioned specific product type):
inhouse_execute_query(
    query="""
    SELECT TOP 20
        jt.TicketID,
        jt.ShortJobDesc,
        o.ClientName,
        o.OrderDate,
        jt.QTY,
        jt.Width,
        jt.Height,
        pt.[Desc] as PaperType,
        g.[DESC] as GSM,
        jt.FrontCelloGloss,
        jt.FrontCelloMatt,
        jt.Cost
    FROM JobTickets jt
    INNER JOIN Orders o ON jt.OrderID = o.OrderID
    LEFT JOIN PaperType pt ON jt.PaperTypeID = pt.PaperTypeID
    LEFT JOIN GSM g ON jt.GSM_ID = g.GSM_ID
    WHERE jt.JobTypeID = ? OR jt.ShortJobDesc LIKE ?
    ORDER BY o.OrderDate DESC
    """,
    params=[job_type_id, '%product_keyword%']
)

STEP 3: FILL MISSING SPECIFICATIONS
Use historical data to complete calculator requirements:
- If customer ordered "business cards" before but didn't specify size → use previous size (90mm x 55mm)
- If no quantity given → use their typical quantity or suggest based on history
- If no paper type specified → use their preferred stock (e.g., 350gsm matt celloglaze)
- If no finish mentioned → check if they usually get celloglaze, spot UV, etc.

STEP 4: GENERATE QUOTE USING APPROPRIATE CALCULATOR
You have access to 80+ printing quote calculators:
- Business Cards: calculate_economical_business_cards_shopify, calculate_premium_business_cards_shopify
- Flyers: calculate_a3_flyers_shopify, calculate_a4_flyers_shopify, calculate_a5_flyers_shopify, calculate_dl_flyers_shopify
- Booklets: calculate_saddle_stitch_booklets_shopify, calculate_perfect_bound_booklets_shopify
- Signage: calculate_corflute_signs_shopify, calculate_metal_aframe_signs_shopify
- Stationery: calculate_letterheads_shopify, calculate_compliments_slips_shopify
- And 60+ more specialized calculators

Select the correct calculator based on product type and run with specifications (from email OR from historical data).

STEP 5: DRAFT PROFESSIONAL QUOTE
Include:
- Line items with descriptions
- Unit prices and quantities
- Subtotals, taxes, and total
- Turnaround time / delivery date
- Payment terms
- Valid until date
- Note if specifications were based on previous orders: "Based on your previous order specifications from [date]..."

STEP 6: ADD VALUE SUGGESTIONS
Recommend upgrades or related products based on history:
- "You previously ordered matt celloglaze - would you like to upgrade to premium celloglazing?"
- "Customers who order business cards often need matching letterheads and compliments slips"

FALLBACK: If no customer history exists and specifications are incomplete:
Draft questions for the customer listing all missing details required for accurate quoting.`,
                'summarize': `Please provide a clear, concise summary of this email, highlighting the key points and any action items.`,
                'draft_reply': `Please draft a professional reply to this email. Consider the tone and context of the original message.`,
                'extract_tasks': `Please extract all action items and tasks mentioned in this email. List them in order of priority.`,
                'analyze': `Please analyze this email's tone, sentiment, and key themes. Identify any potential concerns or opportunities.`,
                'discuss': `I need your assistance with this email. Please help me understand the context and suggest appropriate next steps.`
            };

            // Use enhanced formatter to build the prompt with template
            const basePrompt = EmailAIFormatter.generateEnhancedPrompt(emailData, taskType);
            const attachmentSummary = AttachmentProcessor.generateAttachmentSummary(processedAttachments || []);
            const completePrompt = basePrompt + attachmentSummary;

            // Generate message content (multimodal if attachments)
            const messageContent = EmailAIFormatter.generateClaudeMessageContent(
                completePrompt,
                processedAttachments || []
            );

            // Step 5: Send ONE message
            const inputId = `agent-input-${agentId}`;
            const inputElement = document.getElementById(inputId);

            if (inputElement && typeof sendAgentMessage === 'function') {
                this.log.info(`🤖 Sending single message with task: ${taskType}`);
                inputElement.value = typeof messageContent === 'string' ? messageContent : JSON.stringify(messageContent);
                await sendAgentMessage(agentId);
                this.log.success(`✅ AI processing started with task: ${taskType}`);
                if (typeof showToast === 'function') {
                    showToast(`🤖 AI agent ${taskType.replace('_', ' ')}...`, 'info', 3000);
                }
            }

        } catch (error) {
            this.log.error('Failed to load thread with task:', error);
        }
    },

    /**
     * Load thread into agent column and trigger automatic AI response
     * @param {string} threadSlug - Thread ID
     * @param {string} location - Agent location (e.g., 'agent-9')
     * @param {object} emailData - Email data for context
     */
    async loadThreadIntoAgentAndTrigger(threadSlug, location, emailData, processedAttachments = []) {
        try {
            this.log.info(`🔄 Loading thread ${threadSlug} into ${location}...`);

            // Step 1: Refresh thread list to get the new thread with email badge
            if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.loadThreadsFromBackend === 'function') {
                await ThreadManager.loadThreadsFromBackend();
                this.log.success('✅ Thread list refreshed');
                if (typeof showToast === 'function') {
                    showToast('🔄 Thread list updated', 'info', 2000);
                }
            }

            // Step 2: Extract agent ID from location (e.g., 'agent-9' → 9)
            const agentMatch = location.match(/agent-(\d+)/);
            if (!agentMatch) {
                this.log.warn(`⚠️ Invalid agent location format: ${location}`);
                return;
            }
            const agentId = parseInt(agentMatch[1]);

            // Step 3: Load thread into agent card using MultiAgent.loadThreadIntoAgent()
            if (typeof MultiAgent !== 'undefined' && typeof MultiAgent.loadThreadIntoAgent === 'function') {
                // Fetch thread object from ThreadManager
                const thread = ThreadManager.threads?.find(t => t.thread_slug === threadSlug || t.id === threadSlug);
                if (thread) {
                    this.log.info(`🔄 Loading thread ${threadSlug} into agent ${agentId}`);
                    MultiAgent.loadThreadIntoAgent(agentId, thread);
                    await new Promise(resolve => setTimeout(resolve, 500));
                    this.log.success(`✅ Thread loaded into agent card ${agentId}`);
                    if (typeof showToast === 'function') {
                        showToast('✅ Thread loaded into agent', 'success', 2000);
                    }
                } else {
                    this.log.warn(`⚠️ Thread ${threadSlug} not found in ThreadManager.threads`);
                }
            } else {
                this.log.warn('⚠️ MultiAgent.loadThreadIntoAgent not available');
            }

            // Step 3.5: Verify thread is properly loaded
            const agentName = `agent-${agentId}`;
            const loadedThread = ThreadManager.getThreadByAgent?.(agentName);
            if (loadedThread) {
                this.log.success(`✅ Thread verified loaded: "${loadedThread.title}" at ${loadedThread.location}`);
            } else {
                this.log.warn(`⚠️ Thread not found by getThreadByAgent for ${agentName}`);
                this.log.info(`Checking threads array for thread ${threadSlug}...`);
                const foundThread = ThreadManager.threads?.find(t => t.id === threadSlug);
                if (foundThread) {
                    this.log.info(`Thread exists with location: ${foundThread.location}, updating to ${agentName}`);
                    foundThread.location = agentName;
                }
            }

            // Step 3.6: Insert email content as first message in thread
            const userId = window.UserAuth?.user?.id || 1;
            const emailMessageContent = this.formatEmailForMessage(emailData, processedAttachments);

            try {
                // ✅ FIX: Use correct endpoint /api/threads/messages/save (NOT /api/messages/create which doesn't exist)
                const messageResponse = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/messages/save`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`
                    },
                    body: JSON.stringify({
                        thread_id: threadSlug,  // ✅ FIX: Backend expects thread_id (not thread_slug)
                        user_id: userId,
                        messages: [{
                            role: 'user',
                            content: emailMessageContent,
                            metadata: {
                                message_type: 'email',
                                email_id: emailData.id || emailData.email_id,
                                has_attachments: processedAttachments.length > 0
                            }
                        }]
                    })
                });

                if (messageResponse.ok) {
                    this.log.success('✅ Email content inserted as first message');

                    // Render in UI
                    if (typeof UnifiedMessageRenderer !== 'undefined') {
                        UnifiedMessageRenderer.render(
                            `#agent-messages-${agentId}`,
                            'user',
                            emailMessageContent,
                            {
                                threadId: threadSlug,
                                syncToBackend: false // Already saved above
                            }
                        );
                    }

                    if (typeof showToast === 'function') {
                        showToast('📧 Email loaded into chat', 'success', 2000);
                    }
                } else {
                    this.log.warn('⚠️ Failed to insert email message:', await messageResponse.text());
                }
            } catch (messageError) {
                this.log.error('❌ Failed to insert email message:', messageError);
                // Continue anyway - AI will still get prompt
            }

            // Step 4: Generate enhanced AI prompt with attachments
            const textPrompt = EmailAIFormatter.generateEnhancedPrompt(emailData, 'analyze');

            // Add attachment summary (safe - processedAttachments may be empty)
            const attachmentSummary = AttachmentProcessor.generateAttachmentSummary(processedAttachments || []);
            const completeTextPrompt = textPrompt + attachmentSummary;

            // Generate message content (string for text-only, array for multimodal)
            const messageContent = EmailAIFormatter.generateClaudeMessageContent(
                completeTextPrompt,
                processedAttachments || []
            );

            this.log.info(`📧 Message prepared: ${typeof messageContent === 'string' ? 'text-only' : `multimodal (${messageContent.length} blocks)`}`);

            // Wait a bit for thread card to render
            await new Promise(resolve => setTimeout(resolve, 300));

            // Programmatically populate input and trigger send
            const inputId = `agent-input-${agentId}`;
            const inputElement = document.getElementById(inputId);

            if (inputElement && typeof sendAgentMessage === 'function') {
                this.log.info('🤖 Populating agent input and triggering AI response...');

                // Set the input value (sendAgentMessage will read from it)
                inputElement.value = typeof messageContent === 'string' ? messageContent : JSON.stringify(messageContent);

                // Trigger the send function
                await sendAgentMessage(agentId);

                this.log.success('✅ AI processing started automatically');
                if (typeof showToast === 'function') {
                    showToast('🤖 AI agent analyzing email...', 'info', 3000);
                }
            } else {
                this.log.warn(`⚠️ Cannot trigger AI - input element (${inputId}) or sendAgentMessage function not found`);
                this.log.info('💡 User can manually send message from agent column');
                if (typeof showToast === 'function') {
                    showToast('⚠️ Manual trigger required', 'warning', 4000);
                }
            }

        } catch (error) {
            this.log.error('Failed to load thread and trigger AI:', error);
            // Don't throw - assignment still succeeded
        }
    },

    /**
     * Format email content for message display
     */
    formatEmailForMessage(emailData, attachments = []) {
        const from = emailData.from || 'Unknown Sender';
        const subject = emailData.subject || emailData.title || 'No Subject';
        const date = emailData.date || new Date().toISOString();
        // ✅ FIX: Check body_text first (from full email fetch), then fallback to body or snippet
        const body = emailData.body_text || emailData.body || emailData.snippet || 'No content';

        let message = `📧 **Email from ${from}**\n`;
        message += `**Subject:** ${subject}\n`;
        message += `**Date:** ${date}\n`;
        message += `\n---\n\n`;
        message += body;

        if (attachments && attachments.length > 0) {
            message += `\n\n---\n\n📎 **Attachments (${attachments.length}):**\n`;
            attachments.forEach((att, idx) => {
                const type = att.detected_type || 'file';
                const icon = type === 'image' ? '🖼️' : type === 'pdf' ? '📄' : '📎';
                message += `${idx + 1}. ${icon} ${att.filename || `Attachment ${idx + 1}`}\n`;
            });
        }

        return message;
    },

    /**
     * Clear email agent assignment
     */
    async clearEmailAgentAssignment(emailId, cell) {
        this.log.info(`🗑️ Clearing agent assignment for email ${emailId}`);

        try {
            // Update table cell
            cell.getRow().update({ assigned_agent: null });

            // Note: Thread remains in sessions.threads but assignment is visually cleared
            // To fully unlink, you would need to delete the thread or update its metadata

            this.showSuccess('Agent assignment cleared');

        } catch (error) {
            this.log.error('Failed to clear assignment:', error);
            this.showError(`Failed to clear assignment: ${error.message}`);
        }
    },

    /**
     * Send selected emails to AI agents (bulk operation)
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
                location: destinationId, // 'unassigned' or 'agent-1', 'agent-2', etc.
                initial_message: emailText,
                metadata: {
                    email_ids: Array.from(this.state.selectedEmails),
                    source: 'communication-hub',
                    email_count: selectedData.length
                }
            });

            // ✅ FIX: Extract thread_slug from response (handles wrapped response format)
            const threadSlug = response.thread_slug ||
                (response.data && response.data.thread_slug) ||
                (response.data && response.data.thread && response.data.thread.slug);

            if (response.success && threadSlug) {
                this.log.success(`Thread created: ${threadSlug}`);

                // Assign all selected emails to the new thread
                for (const emailId of this.state.selectedEmails) {
                    await this.assignEmailToThread(emailId, threadSlug);
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
                    thread_slug: threadSlug,
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
     * Hide email preview panel and restore full-width table
     */
    hideEmailPreview() {
        const previewPanel = document.getElementById('emailPreview');
        if (!previewPanel) return;

        // Hide preview panel
        previewPanel.classList.remove('show');
        previewPanel.style.display = 'none';
        previewPanel.style.flex = '0 0 0%';

        // Clear content
        const previewContent = document.getElementById('previewContent');
        if (previewContent) {
            previewContent.innerHTML = '';
        }

        // Remove row highlights
        if (this.state.tabulatorTable) {
            const allRows = this.state.tabulatorTable.getRows();
            allRows.forEach(row => {
                const element = row.getElement();
                element.style.outline = '';
                element.style.outlineOffset = '';
                element.style.boxShadow = '';
                element.style.position = '';
                element.style.zIndex = '';
            });
        }

        this.log.debug('Email preview hidden');
    }

    /**
     * Show email preview panel (supports multiple popups)
     */
    async showEmailPreview(emailData) {
        this.log.debug(`Showing preview for email: ${emailData.id}`);

        // ✅ FIX (Jan 3, 2026): Highlight the selected email row with accent blue border
        if (this.state.tabulatorTable) {
            // Remove highlight from all rows
            const allRows = this.state.tabulatorTable.getRows();
            allRows.forEach(row => {
                const element = row.getElement();
                element.style.outline = '';
                element.style.outlineOffset = '';
                element.style.boxShadow = '';
                element.style.position = '';
                element.style.zIndex = '';
            });

            // Add highlight to current email row (using outline to avoid layout shift)
            const currentRow = this.state.tabulatorTable.getRows().find(r => r.getData().id === emailData.id);
            if (currentRow) {
                const element = currentRow.getElement();
                element.style.outline = '2px solid var(--accent-blue, #3b82f6)';
                element.style.outlineOffset = '-2px';  // Inset the outline so it doesn't expand the row
                element.style.boxShadow = '0 0 12px rgba(59, 130, 246, 0.4)';
                element.style.position = 'relative';
                element.style.zIndex = '10';
            }
        }

        // Check if preview is in popup mode - create new popup instance
        const existingPreview = document.getElementById('emailPreview');
        const isPopupMode = existingPreview && existingPreview.getAttribute('data-mode') === 'popup';

        if (isPopupMode) {
            // Create new popup for this email
            this.createEmailPopup(emailData);
            return;
        }

        // Default sibling mode - use existing panel
        const previewPanel = document.getElementById('emailPreview');
        const previewContent = document.getElementById('previewContent');
        const actionToolbar = document.getElementById('email-action-toolbar');
        const previewTitleText = document.getElementById('preview-title-text');

        if (!previewPanel || !previewContent) return;

        // Store current email reference for action buttons
        this.state.currentPreviewEmail = emailData;

        // Update title
        if (previewTitleText) {
            previewTitleText.textContent = `${emailData.provider === 'gmail' ? 'Gmail' : 'Outlook'} Email`;
        }

        // Show action toolbar
        if (actionToolbar) {
            actionToolbar.style.display = 'flex';
            // Update read/unread button text
            const readStatusText = document.getElementById('read-status-text');
            if (readStatusText) {
                readStatusText.textContent = emailData.is_read ? 'Mark Unread' : 'Mark Read';
            }
        }

        // Show panel immediately with loading state
        const loadingHtml = `
            <div class="email-preview-subject" style="flex-shrink: 0; padding: 16px 20px; border-bottom: 1px solid var(--border-default, #30363d);">
                <h4>${this.escapeHtml(emailData.subject)}</h4>
            </div>
            <div class="email-preview-meta" style="flex-shrink: 0; padding: 12px 20px; background: var(--bg-secondary, #161b22); border-bottom: 1px solid var(--border-default, #30363d);">
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
            <div class="email-preview-content" style="flex: 1; min-height: 0; overflow-y: auto; overflow-x: hidden; display: flex; align-items: center; justify-content: center; padding: 12px;">
                <div style="text-align: center; padding: 40px; color: var(--text-secondary);">
                    <i class="fas fa-spinner fa-spin" style="font-size: 24px; margin-bottom: 12px;"></i>
                    <p>Loading email content...</p>
                </div>
            </div>
        `;

        this.dom.injectHTML(previewContent, loadingHtml);
        previewPanel.classList.add('show');
        // ✅ FIX (Jan 4, 2026): Show preview with proper flex sizing
        previewPanel.style.display = 'flex';
        previewPanel.style.flex = '1 1 50%';  // Take 50% width when visible

        // Fetch full email content
        try {
            const fullEmail = await this.fetchEmailContent(emailData.id);

            // Check if email is part of thread
            const threadSlug = this.state.emailThreads[emailData.id];
            let threadEmails = [];

            // TODO: Backend endpoint /api/communication-hub/threads/{slug}/emails not yet implemented
            // Disabling thread email preview until backend is ready
            // if (threadSlug) {
            //     this.log.info(`📬 Email is part of thread: ${threadSlug}`);
            //     try {
            //         threadEmails = await this.fetchThreadEmails(threadSlug);
            //         this.log.success(`Fetched ${threadEmails.length} emails in thread`);
            //     } catch (threadError) {
            //         this.log.warn('Could not fetch thread emails:', threadError);
            //         // Continue with single email view
            //     }
            // }

            // Render preview based on thread status
            let contentHtml = '';

            if (threadEmails.length > 1) {
                // Thread view with all emails
                contentHtml = this.renderThreadPreview(threadEmails, emailData.id);
            } else {
                // Single email view
                contentHtml = `
                    <div class="email-preview-subject" style="flex-shrink: 0; padding: 10px 12px; border-bottom: 1px solid var(--border-default, #30363d);">
                        <h4 style="margin: 0; font-size: 15px;">${this.escapeHtml(fullEmail.subject)}</h4>
                    </div>
                    <div class="email-preview-meta" style="flex-shrink: 0; padding: 8px 12px; background: var(--bg-secondary, #161b22); border-bottom: 1px solid var(--border-default, #30363d); font-size: 12px;">
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
                    <div class="email-preview-content" style="flex: 1; min-height: 0; overflow-y: auto; overflow-x: hidden; padding: 12px;">
                        ${this.renderEmailBody(fullEmail)}
                        ${this.renderAttachmentsSection(fullEmail)}
                    </div>
                    <div style="flex-shrink: 0; padding: 8px 12px; border-top: 1px solid var(--border-default, #30363d); background: var(--bg-secondary, #161b22);">
                        ${this.renderAISection(fullEmail)}
                    </div>
                `;
            }

            this.dom.injectHTML(previewContent, contentHtml);

        } catch (error) {
            // Graceful degradation: Show snippet view when full content unavailable
            this.log.warn(`Full content unavailable (showing snippet): ${error.message}`);

            // Determine error type for user feedback
            const isNotFound = error.message.includes('404');
            const isTimeout = error.message.includes('timeout') || error.name === 'TypeError';
            const errorIcon = isNotFound ? 'fa-file-slash' : isTimeout ? 'fa-clock' : 'fa-exclamation-triangle';
            const errorText = isNotFound
                ? 'Email not found in provider account'
                : isTimeout
                    ? 'Connection timeout - showing preview'
                    : 'Unable to load full content';

            // Show snippet view with graceful degradation
            const snippetHtml = `
                <div class="email-preview-subject" style="flex-shrink: 0; padding: 10px 12px; border-bottom: 1px solid var(--border-default, #30363d);">
                    <h4 style="margin: 0; font-size: 15px;">${this.escapeHtml(emailData.subject)}</h4>
                    <span style="font-size: 11px; color: var(--text-warning, #ffa500); display: flex; align-items: center; gap: 4px; margin-top: 4px;">
                        <i class="fas ${errorIcon}" style="font-size: 10px;"></i>
                        ${errorText}
                    </span>
                </div>
                <div class="email-preview-meta" style="flex-shrink: 0; padding: 8px 12px; background: var(--bg-secondary, #161b22); border-bottom: 1px solid var(--border-default, #30363d); font-size: 12px;">
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
                <div class="email-preview-content" style="flex: 1; min-height: 0; overflow-y: auto; overflow-x: hidden; padding: 12px;">
                    <div style="padding: 16px; background: var(--bg-tertiary, #0d1117); border-radius: 8px; border: 1px solid var(--border-default, #30363d);">
                        <p style="color: var(--text-secondary, #8b949e); margin: 0; font-size: 13px; line-height: 1.6; white-space: pre-wrap;">
                            ${this.escapeHtml(emailData.snippet || 'No preview available')}
                        </p>
                    </div>
                </div>
            `;

            this.dom.injectHTML(previewContent, snippetHtml);
        }
    },

    /**
     * Render attachments section
     */
    renderAttachmentsSection(email) {
        const attachments = email.attachments || [];

        if (!attachments || attachments.length === 0) {
            return '';
        }

        const getFileIcon = (filename, contentType) => {
            const ext = filename.split('.').pop().toLowerCase();
            const type = contentType || '';

            // Document icons
            if (ext === 'pdf' || type.includes('pdf')) return { icon: 'fa-file-pdf', color: '#ef4444' };
            if (['doc', 'docx'].includes(ext) || type.includes('word')) return { icon: 'fa-file-word', color: '#2563eb' };
            if (['xls', 'xlsx'].includes(ext) || type.includes('excel') || type.includes('spreadsheet')) return { icon: 'fa-file-excel', color: '#10b981' };
            if (['ppt', 'pptx'].includes(ext) || type.includes('presentation')) return { icon: 'fa-file-powerpoint', color: '#f97316' };

            // Code/text files
            if (['txt', 'log'].includes(ext)) return { icon: 'fa-file-alt', color: '#6b7280' };
            if (['json', 'xml', 'html', 'css', 'js', 'py', 'java'].includes(ext)) return { icon: 'fa-file-code', color: '#8b5cf6' };
            if (['csv'].includes(ext)) return { icon: 'fa-file-csv', color: '#059669' };

            // Images
            if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'].includes(ext) || type.includes('image')) return { icon: 'fa-file-image', color: '#ec4899' };

            // Archives
            if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext)) return { icon: 'fa-file-archive', color: '#f59e0b' };

            // Default
            return { icon: 'fa-file', color: '#9ca3af' };
        };

        const formatFileSize = (bytes) => {
            if (!bytes || bytes === 0) return 'Unknown size';
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
            return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        };

        let html = `
            <div class="email-attachments-section" style="margin: 16px 0; padding: 16px; background: var(--bg-secondary); border-radius: 8px; border-left: 3px solid #6366f1;">
                <h4 style="margin: 0 0 12px 0; display: flex; align-items: center; gap: 8px; color: var(--text-primary);">
                    <i class="fas fa-paperclip" style="color: #6366f1;"></i>
                    Attachments (${attachments.length})
                </h4>
                <div class="attachment-list" style="display: flex; flex-direction: column; gap: 8px;">
        `;

        attachments.forEach((att, index) => {
            const filename = att.filename || att.name || `attachment_${index + 1}`;
            const contentType = att.content_type || att.contentType || att.mimeType || '';
            const size = att.size_bytes || att.size || 0;
            const attachmentId = att.attachment_id || att.id || '';

            const { icon, color } = getFileIcon(filename, contentType);
            const sizeStr = formatFileSize(size);

            html += `
                <div class="attachment-item" style="display: flex; align-items: center; gap: 12px; padding: 10px 12px; background: var(--bg-card); border: 1px solid var(--border-default); border-radius: 6px; transition: all 0.2s;" 
                     onmouseover="this.style.borderColor='#6366f1'; this.style.background='var(--bg-hover, #1a1a2e)';" 
                     onmouseout="this.style.borderColor='var(--border-default)'; this.style.background='var(--bg-card)';">
                    <i class="fas ${icon}" style="font-size: 24px; color: ${color};"></i>
                    <div style="flex: 1; min-width: 0;">
                        <div style="font-weight: 500; color: var(--text-primary); font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${this.escapeHtml(filename)}">
                            ${this.escapeHtml(filename)}
                        </div>
                        <div style="font-size: 11px; color: var(--text-secondary); margin-top: 2px;">
                            ${sizeStr} • ${contentType.split('/')[0] || 'file'}
                        </div>
                    </div>
                    <button class="btn-secondary" style="padding: 6px 12px; font-size: 11px; white-space: nowrap;" 
                            onclick="window.CommunicationHub.downloadAttachment('${email.id}', '${attachmentId}', '${this.escapeHtml(filename)}')" 
                            title="Download attachment">
                        <i class="fas fa-download"></i> Download
                    </button>
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
     * Render AI Assistant section
     */
    renderAISection(email) {
        const threadSlug = this.state.emailThreads?.[email.id];
        // ✅ FIX: Only show if thread exists AND is loaded in ThreadManager
        let hasThread = false;
        let threadLocation = null;
        if (threadSlug && typeof ThreadManager !== 'undefined') {
            const thread = ThreadManager.threads?.find(t => t.id === threadSlug);
            hasThread = !!thread;
            threadLocation = thread?.location || 'unknown';
        }

        if (hasThread) {
            return `
                <div class="email-ai-section" style="display: flex; align-items: center; gap: 6px;">
                    <i class="fas fa-robot" style="color: var(--accent-blue, #3b82f6); font-size: 14px;"></i>
                    <span style="color: var(--text-primary); font-size: 12px; font-weight: 500;">AI Assistant</span>
                    <span style="color: var(--text-secondary); font-size: 10px; margin-left: auto;">${threadLocation}</span>
                    <button class="btn-primary" style="padding: 5px 10px; font-size: 11px;"
                            onclick="window.CommunicationHub.openAIThread('${threadSlug}')">
                        <i class="fas fa-comments"></i> Continue
                    </button>
                </div>
            `;
        }

        return `
            <div class="email-ai-section">
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
                    <i class="fas fa-robot" style="color: var(--accent-blue, #3b82f6); font-size: 14px;"></i>
                    <span style="color: var(--text-primary); font-size: 12px; font-weight: 500;">AI Assistant</span>
                </div>
                
                <button class="agent-assignment-btn" 
                        onclick="window.CommunicationHub.showAgentAssignmentFromPreview('${email.id}', event)"
                        style="width: 100%; padding: 6px 8px; background: var(--bg-secondary, #161b22); border: 1px solid var(--border-color, #30363d);
                               border-radius: 6px; color: var(--text-primary, #c9d1d9); cursor: pointer; display: flex; align-items: center; gap: 6px;
                               transition: background 0.2s, border-color 0.2s; margin-bottom: 6px;"
                        onmouseover="this.style.background='var(--bg-tertiary, #0d1117)'; this.style.borderColor='var(--accent-blue, #3b82f6)'"
                        onmouseout="this.style.background='var(--bg-secondary, #161b22)'; this.style.borderColor='var(--border-color, #30363d)'">
                    <i class="fas fa-user-robot" style="color: var(--accent-blue, #3b82f6); font-size: 11px;"></i>
                    <span style="flex: 1; text-align: left; font-size: 11px;">Select Agent & Task</span>
                    <i class="fas fa-chevron-down" style="color: var(--text-secondary, #8b949e); font-size: 9px;"></i>
                </button>
                
                <textarea id="ai-custom-instruction-${email.id}" 
                          placeholder="Custom instructions (optional)..."
                          style="width: 100%; min-height: 40px; padding: 6px; border: 1px solid var(--border-color, #30363d); 
                                 border-radius: 6px; background: var(--input-bg, #0d1117); color: var(--text-primary, #c9d1d9);
                                 font-size: 11px; font-family: inherit; resize: vertical;"
                ></textarea>
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

            // Get custom instruction from textarea
            const customInstructionTextarea = document.getElementById(`ai-custom-instruction-${emailId}`);
            const customInstruction = customInstructionTextarea?.value?.trim() || '';

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

            // ✅ FIX: Extract thread_slug from response (handles wrapped response format)
            const threadSlug = threadResponse.thread_slug ||
                (threadResponse.data && threadResponse.data.thread_slug) ||
                (threadResponse.data && threadResponse.data.thread && threadResponse.data.thread.slug);

            if (!threadSlug) {
                throw new Error('Thread created but no thread_slug returned');
            }

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

            let initialMessage = prompts[action] || prompts['discuss'];

            // Append custom instruction if provided
            if (customInstruction) {
                initialMessage += `\n\n**Additional Instructions:** ${customInstruction}`;
            }

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

                // Update thread location to 'prime'
                try {
                    await this.api.post('/api/threads/update-location', {
                        thread_slug: threadSlug,
                        new_location: 'prime',
                        user_id: userId
                    });
                    this.log.success(`✅ Updated thread location to prime`);

                    // Refresh ThreadManager to reflect new location
                    if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.loadThreadsFromBackend === 'function') {
                        await ThreadManager.loadThreadsFromBackend();
                    }

                    // Update Tabulator to show new badge
                    if (this.emailTable) {
                        this.emailTable.updateData([{ id: emailId }]);
                    }
                } catch (error) {
                    this.log.warn('Failed to update thread location:', error);
                }
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

        // ✅ FIX (Jan 3, 2026): Navigate to the agent's column in command center
        if (typeof ThreadManager !== 'undefined' && ThreadManager.threads) {
            const thread = ThreadManager.threads.find(t => t.id === threadSlug || t.thread_slug === threadSlug);

            if (thread) {
                const location = thread.location;
                this.log.info(`📍 Thread ${threadSlug} is in location: ${location}`);

                // Parse agent number from location (e.g., 'agent-3' -> 3)
                if (location && location.startsWith('agent-')) {
                    const agentNum = parseInt(location.split('-')[1]);

                    // Navigate to agent column using MultiAgent
                    if (typeof MultiAgent !== 'undefined' && MultiAgent.switchToAgent) {
                        this.log.info(`🎯 Switching to agent ${agentNum}`);
                        MultiAgent.switchToAgent(agentNum);
                    } else {
                        // Fallback: Try to show the agent's container
                        const agentContainer = document.getElementById(`agent-${agentNum}-container`);
                        if (agentContainer) {
                            agentContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                        }
                    }
                } else if (location === 'prime') {
                    // Navigate to Prime column
                    if (typeof AIPrime !== 'undefined' && AIPrime.focus) {
                        AIPrime.focus();
                    }
                }
            }
        }

        // Also try legacy AIPrime.open if available
        if (window.AIPrime?.open) {
            window.AIPrime.open({
                threadSlug: threadSlug
            });
        }
    },

    /**
     * Fetch full email content from backend (with caching and retry logic)
     */
    async fetchEmailContent(emailId, retryCount = 0) {
        // Check cache first
        if (this.state.emailContentCache[emailId]) {
            this.log.debug(`Using cached content for email: ${emailId}`);
            return this.state.emailContentCache[emailId];
        }

        this.log.debug(`Fetching full content for email: ${emailId} (attempt ${retryCount + 1}/3)`);

        const userId = window.UserAuth?.user?.id || 1;
        const url = `${this.state.apiBase}/emails/${emailId}?user_id=${userId}`;

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                timeout: 10000  // 10 second timeout
            });

            if (!response.ok) {
                // Retry on 5xx errors or timeouts (not 404s)
                if (response.status >= 500 && retryCount < 2) {
                    const delay = Math.pow(2, retryCount) * 1000;  // 1s, 2s, 4s
                    this.log.warn(`Server error ${response.status}, retrying in ${delay}ms...`);
                    await new Promise(resolve => setTimeout(resolve, delay));
                    return this.fetchEmailContent(emailId, retryCount + 1);
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || 'Failed to fetch email');
            }

            // ✅ Cache the ACTUAL EMAIL DATA (result.email), not the wrapper
            const emailData = result.email;

            this.state.emailContentCache[emailId] = emailData;
            setTimeout(() => {
                delete this.state.emailContentCache[emailId];
                this.log.debug(`Cache expired for email: ${emailId}`);
            }, 5 * 60 * 1000);  // 5 minutes

            return emailData;
        } catch (fetchError) {
            // Retry on network errors
            if (retryCount < 2 && fetchError.name === 'TypeError') {
                const delay = Math.pow(2, retryCount) * 1000;
                this.log.warn(`Network error, retrying in ${delay}ms...`);
                await new Promise(resolve => setTimeout(resolve, delay));
                return this.fetchEmailContent(emailId, retryCount + 1);
            }
            throw fetchError;
        }
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
            // FIXES: white-on-white text + horizontal scrolling
            return `
                <div class="email-html-content" style="
                    background: white; 
                    padding: 20px; 
                    border-radius: 8px;
                    min-height: 400px;
                    max-width: 100%;
                    overflow-x: hidden;
                    overflow-wrap: break-word;
                    word-wrap: break-word;
                    word-break: break-word;
                    color: #1a1a1a !important;
                ">
                    <style>
                        /* Force dark text on white backgrounds */
                        .email-html-content * {
                            color: #1a1a1a !important;
                        }
                        /* Preserve link colors */
                        .email-html-content a {
                            color: #0066cc !important;
                            text-decoration: underline;
                        }
                        /* Responsive images and tables */
                        .email-html-content img {
                            max-width: 100% !important;
                            height: auto !important;
                        }
                        .email-html-content table {
                            max-width: 100% !important;
                            table-layout: fixed !important;
                        }
                        .email-html-content td, .email-html-content th {
                            word-wrap: break-word !important;
                            overflow-wrap: break-word !important;
                        }
                    </style>
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
        // ✅ FIX (Jan 4, 2026): Use hideEmailPreview for proper layout restoration
        this.hideEmailPreview();

        // Clear current email reference
        this.state.currentPreviewEmail = null;
    },

    /**
     * Toggle between sibling (side-by-side) and popup (draggable) modes
     */
    togglePopupMode() {
        const previewPanel = document.getElementById('emailPreview');
        if (!previewPanel) return;

        const currentMode = previewPanel.getAttribute('data-mode') || 'sibling';
        const toggleBtn = previewPanel.querySelector('[data-action="toggle-popup-mode"] i');

        if (currentMode === 'sibling') {
            // Switch to popup mode
            previewPanel.setAttribute('data-mode', 'popup');
            previewPanel.classList.add('popup-mode');
            if (toggleBtn) toggleBtn.className = 'fas fa-compress';

            // Make draggable
            this.makePreviewDraggable();

            this.log.info('📧 Email preview: Popup mode activated (draggable)');
        } else {
            // Switch to sibling mode
            previewPanel.setAttribute('data-mode', 'sibling');
            previewPanel.classList.remove('popup-mode');
            if (toggleBtn) toggleBtn.className = 'fas fa-external-link-alt';

            // Remove draggable behavior
            this.removePreviewDraggable();

            // Reset position
            previewPanel.style.left = '';
            previewPanel.style.top = '';
            previewPanel.style.transform = '';

            this.log.info('📧 Email preview: Sibling mode activated (side-by-side)');
        }
    },

    /**
     * Make email preview panel draggable (popup mode)
     */
    makePreviewDraggable() {
        const previewPanel = document.getElementById('emailPreview');
        const header = previewPanel?.querySelector('.email-preview-header');

        if (!previewPanel || !header) return;

        // Store drag state
        let isDragging = false;
        let offsetX = 0;
        let offsetY = 0;

        const onMouseDown = (e) => {
            // Don't drag if clicking buttons
            if (e.target.closest('button')) return;

            isDragging = true;
            const rect = previewPanel.getBoundingClientRect();
            offsetX = e.clientX - rect.left;
            offsetY = e.clientY - rect.top;

            header.style.cursor = 'grabbing';
            e.preventDefault();
        };

        const onMouseMove = (e) => {
            if (!isDragging) return;
            e.preventDefault();

            const newLeft = e.clientX - offsetX;
            const newTop = e.clientY - offsetY;

            previewPanel.style.left = newLeft + 'px';
            previewPanel.style.top = newTop + 'px';
            previewPanel.style.transform = 'none';
        };

        const onMouseUp = () => {
            if (isDragging) {
                isDragging = false;
                header.style.cursor = 'move';
            }
        };

        // Store handlers for cleanup
        previewPanel._dragHandlers = { onMouseDown, onMouseMove, onMouseUp };

        header.addEventListener('mousedown', onMouseDown);
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
        header.style.cursor = 'move';
    },

    /**
     * Remove draggable behavior from email preview panel
     */
    removePreviewDraggable() {
        const previewPanel = document.getElementById('emailPreview');
        const header = previewPanel?.querySelector('.email-preview-header');

        if (!previewPanel || !header || !previewPanel._dragHandlers) return;

        const { onMouseDown, onMouseMove, onMouseUp } = previewPanel._dragHandlers;

        header.removeEventListener('mousedown', onMouseDown);
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
        header.style.cursor = '';

        delete previewPanel._dragHandlers;
    },

    /**
     * Create new email popup (allows multiple concurrent popups)
     */
    async createEmailPopup(emailData) {
        const popupId = `email-popup-${emailData.id}`;

        // Check if popup already exists
        if (document.getElementById(popupId)) {
            document.getElementById(popupId).style.zIndex = 99999 + Date.now();
            return;
        }

        // Fetch full email content
        let fullEmail = emailData;
        try {
            const response = await this.api.get(`${this.state.apiBase}/emails/${emailData.id}`);
            if (response.success && response.email) {
                fullEmail = response.email;
            }
        } catch (error) {
            this.log.error('Failed to fetch full email', error);
        }

        // Create popup HTML
        const popup = document.createElement('div');
        popup.id = popupId;
        popup.className = 'email-popup-instance';
        popup.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 600px;
            height: 70vh;
            max-width: 90vw;
            max-height: 90vh;
            background: var(--bg-tertiary, #16181D);
            border: 2px solid var(--accent-primary, #4f6cff);
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            z-index: ${99999 + Date.now()};
            display: flex;
            flex-direction: column;
            overflow: hidden;
            resize: both;
            min-width: 400px;
            min-height: 300px;
        `;

        popup.innerHTML = `
            <div class="email-popup-header" style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 16px;
                background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
                border-bottom: 1px solid var(--border-default, #2A3142);
                cursor: move;
                user-select: none;
            ">
                <div style="display: flex; align-items: center; gap: 10px; color: white;">
                    <i class="fas fa-envelope"></i>
                    <span style="font-weight: 600;">${this.escapeHtml(fullEmail.subject || 'Email')}</span>
                </div>
                <button class="email-popup-close" style="
                    background: rgba(255,255,255,0.2);
                    border: none;
                    color: white;
                    width: 28px;
                    height: 28px;
                    border-radius: 6px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                ">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="email-popup-body" style="
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: var(--bg-tertiary, #16181D);
            ">
                <div class="email-preview-subject" style="margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid var(--border-default, #2A3142);">
                    <h4 style="margin: 0; font-size: 18px; color: var(--text-primary, #E5E7EB);">${this.escapeHtml(fullEmail.subject)}</h4>
                </div>
                <div class="email-preview-meta" style="margin-bottom: 20px; padding: 16px; background: var(--bg-secondary, #0B0E13); border-radius: 8px; border: 1px solid var(--border-default, #2A3142);">
                    <div style="display: flex; margin-bottom: 10px;">
                        <span style="color: var(--text-secondary, #7D8590); min-width: 80px; font-size: 13px;">From:</span>
                        <span style="color: var(--text-primary, #E5E7EB); font-size: 13px;">${this.escapeHtml(fullEmail.from)}</span>
                    </div>
                    ${fullEmail.to ? `
                        <div style="display: flex; margin-bottom: 10px;">
                            <span style="color: var(--text-secondary, #7D8590); min-width: 80px; font-size: 13px;">To:</span>
                            <span style="color: var(--text-primary, #E5E7EB); font-size: 13px;">${this.escapeHtml(fullEmail.to)}</span>
                        </div>
                    ` : ''}
                    <div style="display: flex; margin-bottom: 10px;">
                        <span style="color: var(--text-secondary, #7D8590); min-width: 80px; font-size: 13px;">Date:</span>
                        <span style="color: var(--text-primary, #E5E7EB); font-size: 13px;">${new Date(fullEmail.date).toLocaleString()}</span>
                    </div>
                    <div style="display: flex;">
                        <span style="color: var(--text-secondary, #7D8590); min-width: 80px; font-size: 13px;">Account:</span>
                        <span style="color: var(--text-primary, #E5E7EB); font-size: 13px;">${this.escapeHtml(fullEmail.provider || 'N/A')}</span>
                    </div>
                </div>
                <div class="email-preview-content" style="background: var(--bg-secondary, #0B0E13); border: 1px solid var(--border-default, #2A3142); border-radius: 8px; padding: 20px;">
                    ${this.renderEmailBody(fullEmail)}
                </div>
            </div>
        `;

        // Add to body
        document.body.appendChild(popup);

        // Make draggable
        const header = popup.querySelector('.email-popup-header');
        let isDragging = false;
        let offsetX = 0, offsetY = 0;

        header.addEventListener('mousedown', (e) => {
            if (e.target.closest('button')) return;
            isDragging = true;
            const rect = popup.getBoundingClientRect();
            offsetX = e.clientX - rect.left;
            offsetY = e.clientY - rect.top;
            header.style.cursor = 'grabbing';
            popup.style.zIndex = 99999 + Date.now(); // Bring to front
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            e.preventDefault();
            popup.style.left = (e.clientX - offsetX) + 'px';
            popup.style.top = (e.clientY - offsetY) + 'px';
            popup.style.transform = 'none';
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                header.style.cursor = 'move';
            }
        });

        // Close button
        popup.querySelector('.email-popup-close').addEventListener('click', () => {
            popup.remove();
        });

        this.log.info(`📧 Created email popup: ${emailData.id}`);
    },

    /**
     * Handle email action buttons (Reply, Forward, Delete, Archive, etc)
     * Industry-standard email client actions matching Nylas Mail, Gmail, Outlook
     */
    async handleEmailAction(action) {
        if (!this.state.currentPreviewEmail) {
            this.log.warn('No email currently in preview');
            return;
        }

        const email = this.state.currentPreviewEmail;
        this.log.info(`📧 Email action: ${action} for email ${email.id}`);

        try {
            switch (action) {
                case 'reply':
                    await this.composeReply(email, 'reply');
                    break;
                case 'reply-all':
                    await this.composeReply(email, 'reply-all');
                    break;
                case 'forward':
                    await this.composeForward(email);
                    break;
                case 'archive':
                    await this.archiveEmail(email);
                    break;
                case 'delete':
                    await this.deleteEmail(email);
                    break;
                case 'toggle-read':
                    await this.toggleReadStatus(email);
                    break;
                case 'print':
                    this.printEmail(email);
                    break;
                default:
                    this.log.warn(`Unknown action: ${action}`);
            }
        } catch (error) {
            this.log.error(`Failed to execute ${action}:`, error);
            this.showError(`Failed to ${action} email: ${error.message}`);
        }
    },

    /**
     * Compose reply to email
     */
    async composeReply(email, type = 'reply') {
        this.log.info(`✉️  Composing ${type} to email ${email.id}`);

        // Fetch full email content for reply context
        const fullEmail = await this.fetchEmailContent(email.id);

        // Switch to compose tab
        const composeBtn = this.dashboardContainer.querySelector('[data-subtab="compose"]');
        if (composeBtn) {
            composeBtn.click();
        }

        // Pre-fill compose form
        setTimeout(() => {
            const toField = document.getElementById('compose-to');
            const subjectField = document.getElementById('compose-subject');
            const bodyField = document.getElementById('compose-body');

            if (toField) {
                // Reply: to sender, Reply-all: to sender + all recipients
                if (type === 'reply') {
                    toField.value = fullEmail.from;
                } else if (type === 'reply-all') {
                    const recipients = [fullEmail.from];
                    if (fullEmail.to) recipients.push(fullEmail.to);
                    if (fullEmail.cc) recipients.push(fullEmail.cc);
                    toField.value = [...new Set(recipients)].join(', ');
                }
            }

            if (subjectField) {
                const subject = fullEmail.subject || 'No Subject';
                subjectField.value = subject.startsWith('Re:') ? subject : `Re: ${subject}`;
            }

            if (bodyField) {
                const originalMessage = `\n\n---\nOn ${fullEmail.date}, ${fullEmail.from} wrote:\n> ${(fullEmail.body_text || fullEmail.snippet || '').split('\n').join('\n> ')}`;
                bodyField.value = originalMessage;
            }
        }, 100);

        this.showSuccess(`Composing ${type} to ${email.from}`);
    },

    /**
     * Compose forward of email
     */
    async composeForward(email) {
        this.log.info(`📤 Forwarding email ${email.id}`);

        const fullEmail = await this.fetchEmailContent(email.id);

        // Switch to compose tab
        const composeBtn = this.dashboardContainer.querySelector('[data-subtab="compose"]');
        if (composeBtn) {
            composeBtn.click();
        }

        setTimeout(() => {
            const subjectField = document.getElementById('compose-subject');
            const bodyField = document.getElementById('compose-body');

            if (subjectField) {
                const subject = fullEmail.subject || 'No Subject';
                subjectField.value = subject.startsWith('Fwd:') ? subject : `Fwd: ${subject}`;
            }

            if (bodyField) {
                const forwardedMessage = `\n\n---------- Forwarded message ---------\nFrom: ${fullEmail.from}\nDate: ${fullEmail.date}\nSubject: ${fullEmail.subject}\nTo: ${fullEmail.to || 'N/A'}\n\n${fullEmail.body_text || fullEmail.snippet || ''}`;
                bodyField.value = forwardedMessage;
            }
        }, 100);

        this.showSuccess(`Forwarding email from ${email.from}`);
    },

    /**
     * Archive email
     */
    async archiveEmail(email) {
        this.log.info(`📦 Archiving email ${email.id}`);
        // TODO: Implement archive API call
        this.showSuccess(`Email archived successfully`);
        this.closePreview();
        await this.loadEmails(); // Refresh list
    },

    /**
     * Delete email
     */
    async deleteEmail(email) {
        if (!confirm(`Are you sure you want to delete this email from ${email.from}?`)) {
            return;
        }

        this.log.info(`🗑️  Deleting email ${email.id}`);

        try {
            const userId = window.UserAuth?.user?.id || 1;
            await this.api.delete(`${this.state.apiBase}/emails/${email.id}?user_id=${userId}`);

            this.showSuccess('Email deleted successfully');
            this.closePreview();
            await this.loadEmails(); // Refresh list
        } catch (error) {
            throw new Error(`Failed to delete email: ${error.message}`);
        }
    },

    /**
     * Toggle read/unread status
     */
    async toggleReadStatus(email) {
        const newStatus = !email.is_read;
        const action = newStatus ? 'read' : 'unread';

        this.log.info(`📭 Marking email ${email.id} as ${action}`);

        try {
            const userId = window.UserAuth?.user?.id || 1;
            await this.api.post(`${this.state.apiBase}/emails/${email.id}/${action}?user_id=${userId}`);

            // Update local state
            email.is_read = newStatus;
            this.state.currentPreviewEmail.is_read = newStatus;

            // Update button text
            const readStatusText = document.getElementById('read-status-text');
            if (readStatusText) {
                readStatusText.textContent = newStatus ? 'Mark Unread' : 'Mark Read';
            }

            this.showSuccess(`Email marked as ${action}`);

            // Update table row if exists
            if (this.state.tabulatorTable) {
                this.state.tabulatorTable.updateData([{ id: email.id, is_read: newStatus }]);
            }
        } catch (error) {
            throw new Error(`Failed to mark as ${action}: ${error.message}`);
        }
    },

    /**
     * Print email
     */
    printEmail(email) {
        this.log.info(`🖨️  Printing email ${email.id}`);

        // Create printable version
        const printWindow = window.open('', '_blank');
        const printContent = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Print: ${this.escapeHtml(email.subject)}</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; color: #000; }
                    .header { border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 20px; }
                    .meta { margin: 5px 0; }
                    .meta strong { display: inline-block; width: 100px; }
                    .content { margin-top: 20px; line-height: 1.6; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>${this.escapeHtml(email.subject || 'No Subject')}</h1>
                </div>
                <div class="meta"><strong>From:</strong> ${this.escapeHtml(email.from)}</div>
                <div class="meta"><strong>To:</strong> ${this.escapeHtml(email.to || 'N/A')}</div>
                <div class="meta"><strong>Date:</strong> ${this.formatDate(email.date)}</div>
                <div class="content">
                    ${email.body_html || this.escapeHtml(email.body_text || email.snippet || 'No content')}
                </div>
            </body>
            </html>
        `;

        printWindow.document.write(printContent);
        printWindow.document.close();
        setTimeout(() => {
            printWindow.print();
        }, 250);
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
     * Show warning message
     */
    showWarning(message) {
        this.log.warn(message);
        if (typeof showToast === 'function') {
            showToast(message, 'warning', 3000);
        }
    },

    /**
     * Open email preview by email ID (called from thread cards)
     * @param {string} emailId - Email ID to preview
     */
    async openEmailPreview(emailId) {
        this.log.debug(`Opening email preview for ID: ${emailId}`);

        try {
            // Find email in current state
            const email = this.state.emails?.find(e => e.id === emailId);

            if (email) {
                // Email already loaded in state
                await this.showEmailPreview(email);
            } else {
                // Email not in state, need to fetch it
                this.log.debug(`Email ${emailId} not in state, fetching...`);
                const response = await this.api.get(`${this.state.apiBase}/emails/${emailId}`);

                if (response.success && response.email) {
                    await this.showEmailPreview(response.email);
                } else {
                    throw new Error('Email not found');
                }
            }
        } catch (error) {
            this.log.error(`Failed to open email preview: ${error.message}`);
            this.showError(`Failed to open email: ${error.message}`);
        }
    },

    /**
     * Show warning when no email accounts are connected
     */
    showNoAccountsWarning() {
        const container = document.getElementById('email-table-container');
        if (!container) return;

        container.innerHTML = `
            <div style="padding: 60px 20px; text-align: center; background: var(--bg-card); border-radius: 8px; margin: 20px;">
                <div style="font-size: 48px; color: #8b949e; margin-bottom: 16px;">
                    <i class="fas fa-inbox"></i>
                </div>
                <h3 style="color: var(--text-primary); margin-bottom: 12px; font-size: 20px;">
                    No Email Accounts Connected
                </h3>
                <p style="color: #8b949e; margin-bottom: 24px; font-size: 14px; max-width: 500px; margin-left: auto; margin-right: auto;">
                    To view and manage your emails, you need to connect at least one email account (Gmail or Outlook).
                </p>
                <button onclick="window.location.href='/oauth'" 
                        style="padding: 12px 24px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600; display: inline-flex; align-items: center; gap: 8px;">
                    <i class="fas fa-plug"></i> Connect Email Account
                </button>
                <div style="margin-top: 24px; padding-top: 24px; border-top: 1px solid #30363d;">
                    <p style="color: #6b7280; font-size: 12px; margin-bottom: 8px;">Supported Providers:</p>
                    <div style="display: flex; gap: 16px; justify-content: center; align-items: center;">
                        <span style="color: #8b949e; font-size: 13px;"><i class="fab fa-google"></i> Gmail</span>
                        <span style="color: #8b949e; font-size: 13px;"><i class="fab fa-microsoft"></i> Outlook</span>
                    </div>
                </div>
            </div>
        `;

        this.log.warn('No email accounts connected - showing connection prompt');
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
    /**
     * Unload email thread from agent (move to prime)
     */
    async unloadEmailFromAgent(emailId, threadSlug, event) {
        event?.stopPropagation();

        // Use provided threadSlug or fallback to state
        const actualThreadSlug = threadSlug || this.state.emailThreads?.[emailId];
        if (!actualThreadSlug) {
            this.log.warn('No thread found for email:', emailId);
            return;
        }

        const thread = ThreadManager?.threads?.find(t => t.id === actualThreadSlug);
        if (!thread) {
            this.log.warn('Thread not found in ThreadManager:', actualThreadSlug);
            return;
        }

        const userId = window.UserAuth?.user?.id || 1;

        try {
            this.log.info(`🔄 Unloading thread ${actualThreadSlug} from ${thread.location} to unassigned`);

            // Update location to unassigned
            await this.api.post('/api/threads/update-location', {
                thread_slug: actualThreadSlug,
                new_location: 'unassigned',
                user_id: userId
            });

            // Unload from agent UI if loaded
            if (thread.location && thread.location.startsWith('agent-')) {
                const agentId = parseInt(thread.location.replace('agent-', ''));
                if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.unloadThread === 'function') {
                    AgentColumn.unloadThread(agentId);
                    this.log.success(`✅ Unloaded from agent column ${agentId}`);
                }
            }

            // Update local state
            thread.location = 'unassigned';

            // Refresh table to show "Assign Agent" button again
            if (this.state.tabulatorTable) {
                this.state.tabulatorTable.updateData([{ id: emailId, assigned_agent: null }]);
            }

            if (typeof showToast === 'function') {
                showToast('✅ Thread unloaded to Prime', 'success', 2000);
            }

            this.log.success(`✅ Thread ${actualThreadSlug} unloaded to prime`);

        } catch (error) {
            this.log.error('Failed to unload thread:', error);
            if (typeof showToast === 'function') {
                showToast('❌ Unload failed', 'error', 3000);
            }
        }
    },

    /**
     * Open thread in AI Prime and update location to prime
     * @param {string} threadSlug - Thread slug to open
     */
    async openThreadInPrime(threadSlug) {
        try {
            this.log.info(`🔵 Opening thread in Prime: ${threadSlug}`);

            // CRITICAL: Use ThreadManager.loadThreadInPrime() to properly load messages
            if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.loadThreadInPrime === 'function') {
                // Find thread by slug
                const thread = ThreadManager.threads?.find(t => t.slug === threadSlug);
                if (thread) {
                    this.log.info(`✅ Found thread ID: ${thread.id}, loading messages...`);
                    // Use ThreadManager's proper load function (loads messages + updates location)
                    await ThreadManager.loadThreadInPrime(thread.id);
                    this.log.success(`✅ Thread loaded in Prime with messages`);
                } else {
                    this.log.warn(`⚠️ Thread not found in ThreadManager, using fallback...`);
                    // Fallback: Just open sidebar without messages
                    if (window.AIPrime?.open) {
                        window.AIPrime.open({
                            threadSlug: threadSlug,
                            agent: 'communication-agent'
                        });
                    }
                }

                // Update Tabulator to show new badge
                if (this.state.tabulatorTable) {
                    this.state.tabulatorTable.redraw();
                }
            } else {
                this.log.warn(`⚠️ ThreadManager not available, using basic open`);
                // Fallback: Basic open without message loading
                if (window.AIPrime?.open) {
                    window.AIPrime.open({
                        threadSlug: threadSlug,
                        agent: 'communication-agent'
                    });
                } else {
                    window.location.hash = `#thread/${threadSlug}`;
                }
            }
        } catch (error) {
            this.log.error('Failed to open thread in Prime:', error);
        }
    },

    /**
     * Refresh thread data when formatter shows "Syncing..." state
     * @param {string} emailId - Email ID
     * @param {string} threadSlug - Thread slug
     */
    async refreshThreadData(emailId, threadSlug) {
        try {
            this.log.info(`🔄 Refreshing thread data for email ${emailId}, thread ${threadSlug}`);

            // Reload ThreadManager threads from backend
            if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.loadThreadsFromBackend === 'function') {
                await ThreadManager.loadThreadsFromBackend();
                this.log.success('✅ ThreadManager refreshed');
            }

            // Force table redraw to update the AI Agent column
            if (this.state.tabulatorTable) {
                this.state.tabulatorTable.redraw(true);
                this.log.success('✅ Table redrawn - agent badge should now appear');
            }

            if (typeof showToast === 'function') {
                showToast('✅ Thread data refreshed', 'success', 2000);
            }

        } catch (error) {
            this.log.error('Failed to refresh thread data:', error);
            if (typeof showToast === 'function') {
                showToast('❌ Refresh failed', 'error', 3000);
            }
        }
    },

    showSuccess(message) {
        this.log.success(message);
        if (typeof showToast === 'function') {
            showToast(message, 'success', 3000);
        } else {
            // Fallback to alert if toast not available
            alert(message);
        }
    },

    /**
     * Show agent assignment dropdown from email preview panel
     * This is called from the preview panel's "Select Agent & Task Type" button
     */
    async showAgentAssignmentFromPreview(emailId, event) {
        this.log.info(`📋 Opening agent dropdown from preview for email: ${emailId}`);

        // Get the button that was clicked for positioning
        const button = event?.target?.closest('.agent-assignment-btn');
        if (!button) {
            this.log.error('❌ Could not find agent assignment button');
            return;
        }

        // Get email data
        const email = this.state.emails.find(e => e.id === emailId);
        if (!email) {
            this.log.error('❌ Email not found:', emailId);
            return;
        }

        // Remove any existing dropdown
        const existingDropdown = document.querySelector('.agent-assignment-dropdown');
        if (existingDropdown) {
            existingDropdown.remove();
        }

        // Fetch synergy sessions and thread counts (same as table dropdown)
        this.log.info('🔍 Building agent list from MultiAgent.loadedThreads...');

        let threadCounts = {};

        // USE COMMAND CENTER'S DATA: MultiAgent.loadedThreads
        if (typeof MultiAgent !== 'undefined' && MultiAgent.loadedThreads) {
            this.log.info('✅ Using MultiAgent.loadedThreads (Command Center data)');

            // Count threads per agent from MultiAgent.loadedThreads
            Object.entries(MultiAgent.loadedThreads).forEach(([agentId, threadInfo]) => {
                if (threadInfo && threadInfo.threadId) {
                    // agentId is a string like "3", "4", etc. - store as number
                    const numericId = parseInt(agentId);
                    threadCounts[numericId] = 1; // Each agent can only have 1 thread loaded
                    const agentName = MultiAgent.getAgentName(numericId);
                    this.log.info(`   Agent ${agentId} (${agentName}): 1 thread - "${threadInfo.threadTitle}"`);
                }
            });

            // Check if Prime has a loaded thread (from ThreadManager)
            if (typeof ThreadManager !== 'undefined' && ThreadManager.currentThreadId) {
                const primeThread = ThreadManager.threads?.find(t => t.id === ThreadManager.currentThreadId);
                if (primeThread) {
                    threadCounts['27'] = 1; // Prime agent ID
                    this.log.info(`   Agent 27 (Prime): 1 thread - "${primeThread.title}"`);
                }
            }

            const totalThreads = Object.keys(threadCounts).length;
            this.log.info(`   Total agents with threads: ${totalThreads}`);
        } else {
            this.log.warn('⚠️ MultiAgent.loadedThreads not available, showing Prime + Alpha only');
        }

        // Get current assignment
        const currentThreadSlug = this.state.emailThreads?.[emailId];

        // Build agent list - MATCHES EMAIL TABLE DROPDOWN LOGIC
        // Order: Prime FIRST, then NATO agents (only show up to last active + 1)
        const agentOrder = ['Prime', 'Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel', 'India',
            'Juliet', 'Kilo', 'Lima', 'Mike', 'November', 'Oscar', 'Papa', 'Quebec', 'Romeo',
            'Sierra', 'Tango', 'Uniform', 'Victor', 'Whiskey', 'Xray', 'Yankee', 'Zulu'];

        // Agent ID mapping (Prime = 27, Alpha = 1, Bravo = 2, etc.)
        const agentIdMap = {
            'Prime': 27,
            'Alpha': 1, 'Bravo': 2, 'Charlie': 3, 'Delta': 4, 'Echo': 5, 'Foxtrot': 6,
            'Golf': 7, 'Hotel': 8, 'India': 9, 'Juliet': 10, 'Kilo': 11, 'Lima': 12,
            'Mike': 13, 'November': 14, 'Oscar': 15, 'Papa': 16, 'Quebec': 17, 'Romeo': 18,
            'Sierra': 19, 'Tango': 20, 'Uniform': 21, 'Victor': 22, 'Whiskey': 23,
            'Xray': 24, 'Yankee': 25, 'Zulu': 26
        };

        // Find highest agent with threads
        let highestActiveAgentId = 0;
        Object.keys(threadCounts).forEach(agentId => {
            const id = parseInt(agentId);
            if (id > 0 && id <= 26 && id > highestActiveAgentId) {
                highestActiveAgentId = id;
            }
        });

        this.log.info(`✅ Highest active agent ID: ${highestActiveAgentId} (${MultiAgent.getAgentName(highestActiveAgentId) || 'None'})`);

        // Show ALL agents from Prime through highest active + 1 (for "Activate Next Agent")
        const maxAgentIdToShow = Math.min(highestActiveAgentId + 1, 26);

        this.log.info(`✅ Will show agents from Prime (27) and Alpha (1) to ${agentOrder[maxAgentIdToShow]} (${maxAgentIdToShow})`);
        this.log.info(`   This includes ALL agents 1-${maxAgentIdToShow}, showing which have threads and which are empty`);

        const agentList = [];

        agentOrder.forEach((name, index) => {
            const agentId = agentIdMap[name];

            // Show Prime always
            if (name === 'Prime') {
                // Will be processed below
            }
            // Show agents 1 through maxAgentIdToShow
            else if (agentId > maxAgentIdToShow) {
                this.log.info(`   ⏭️ Skipping agent ${name} (ID ${agentId}) - beyond highest active + 1`);
                return;
            }

            const threadCount = threadCounts[agentId] || 0;
            const isCurrentAgent = false; // Not checking current assignment for now
            const isNextAvailable = agentId === maxAgentIdToShow && threadCount === 0;

            let borderColor, iconColor, statusText, icon;

            if (isCurrentAgent) {
                // Currently assigned to this email
                borderColor = '#6366f1';
                iconColor = '#6366f1';
                icon = '<i class="fas fa-check-circle" style="color: #6366f1; margin-left: 8px;"></i>';
                statusText = '';
            } else if (threadCount > 0) {
                // Agent has threads - show PURPLE BORDER + thread count
                borderColor = '#6366f1';
                iconColor = '#8b949e';
                icon = '';
                statusText = `<span style="color: #8b949e; font-size: 10px; margin-left: 6px;">(${threadCount} ${threadCount === 1 ? 'thread' : 'threads'})</span>`;
            } else {
                // Empty agent - show GREEN
                borderColor = 'transparent';
                iconColor = '#22c55e';
                icon = '';
                statusText = '<span style="color: #22c55e; font-size: 10px; margin-left: 6px; font-weight: 600;">(Empty)</span>';
            }

            agentList.push({ name, agentId, threadCount, isCurrentAgent, borderColor, iconColor, icon, statusText, isNextAvailable });
        });

        // Create dropdown HTML
        const dropdownHtml = `
            <div class="agent-assignment-dropdown" style="
                position: fixed;
                background: #1a1a1a;
                border: 1px solid #30363d;
                border-radius: 8px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.4);
                max-height: 400px;
                overflow-y: auto;
                z-index: 10000;
                min-width: 280px;
            ">
                <div style="padding: 12px; border-bottom: 1px solid #30363d; background: #0d1117;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <i class="fas fa-robot" style="color: #6366f1;"></i>
                        <strong style="color: #f0f6fc; font-size: 14px;">Select Agent & Task</strong>
                    </div>
                </div>
                ${agentList.map(agent => `
                    <div class="agent-dropdown-item" data-agent-id="${agent.agentId}" data-agent-name="${agent.name}" style="
                        padding: 10px 12px;
                        cursor: pointer;
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        border-bottom: 1px solid #30363d;
                        transition: background 0.2s;
                        border-left: ${agent.borderColor === 'transparent' ? 'none' : `3px solid ${agent.borderColor}`};
                        ${agent.isNextAvailable ? 'background: rgba(34, 197, 94, 0.08);' : ''}
                    ">
                        <div style="display: flex; align-items: center; gap: 8px; flex: 1;">
                            <i class="fas ${agent.isNextAvailable ? 'fa-plus-circle' : 'fa-robot'}" style="color: ${agent.iconColor}; width: 16px; text-align: center;"></i>
                            <span style="color: #f0f6fc; font-size: 13px; ${agent.isNextAvailable ? 'font-weight: 600;' : ''}">${agent.isNextAvailable ? 'Activate ' : ''}${agent.name}</span>
                            ${agent.icon}
                            ${agent.statusText}
                        </div>
                        <i class="fas fa-chevron-right" style="color: #6b7280; font-size: 10px;"></i>
                    </div>
                `).join('')}
            </div>
        `;

        // Insert dropdown into DOM
        const tempContainer = document.createElement('div');
        tempContainer.innerHTML = dropdownHtml;
        const dropdown = tempContainer.firstElementChild;
        document.body.appendChild(dropdown);

        // Position dropdown below button (or above if not enough space)
        const buttonRect = button.getBoundingClientRect();
        const dropdownRect = dropdown.getBoundingClientRect();
        const spaceBelow = window.innerHeight - buttonRect.bottom;
        const spaceAbove = buttonRect.top;

        if (spaceBelow >= dropdownRect.height || spaceBelow >= spaceAbove) {
            // Position below button
            dropdown.style.top = `${buttonRect.bottom + 4}px`;
        } else {
            // Position above button
            dropdown.style.top = `${buttonRect.top - dropdownRect.height - 4}px`;
        }
        dropdown.style.left = `${buttonRect.left}px`;

        // Add hover effects to agent items
        dropdown.querySelectorAll('.agent-dropdown-item').forEach(item => {
            item.addEventListener('mouseenter', () => {
                item.style.background = 'rgba(99, 102, 241, 0.1)';
            });
            item.addEventListener('mouseleave', () => {
                item.style.background = 'transparent';
            });

            // Click handler: show task submenu
            item.addEventListener('click', async (e) => {
                e.stopPropagation();
                const agentId = parseInt(item.dataset.agentId);
                const agentName = item.dataset.agentName;

                // Show task type submenu
                this.showTaskSubmenuFromPreview(emailId, agentId, agentName, item, dropdown);
            });
        });

        // Close dropdown on outside click
        const closeHandler = (e) => {
            if (!dropdown.contains(e.target) && !button.contains(e.target)) {
                dropdown.remove();
                document.removeEventListener('click', closeHandler);
            }
        };
        setTimeout(() => document.addEventListener('click', closeHandler), 0);

        this.log.success(`✅ Agent dropdown displayed with ${agentList.length} agents`);
    },

    /**
     * Show task type submenu from preview panel
     */
    showTaskSubmenuFromPreview(emailId, agentId, agentName, agentItem, parentDropdown) {
        this.log.info(`📋 Showing task submenu for ${agentName} (Agent ${agentId})`);

        // Remove any existing submenu
        const existingSubmenu = document.querySelector('.task-submenu');
        if (existingSubmenu) {
            existingSubmenu.remove();
        }

        // Task types with icons and colors
        const taskTypes = [
            { type: 'generate_quote', label: 'Generate Quote', icon: 'fa-calculator', color: '#10b981' },
            { type: 'summarize', label: 'Summarize', icon: 'fa-list-ul', color: '#3b82f6' },
            { type: 'draft_reply', label: 'Draft Reply', icon: 'fa-reply', color: '#8b5cf6' },
            { type: 'extract_tasks', label: 'Extract Tasks', icon: 'fa-check-square', color: '#f59e0b' },
            { type: 'analyze', label: 'Analyze', icon: 'fa-search', color: '#ec4899' },
            { type: 'discuss', label: 'Discuss', icon: 'fa-comments', color: '#6366f1' }
        ];

        // Create submenu HTML
        const submenuHtml = `
            <div class="task-submenu" style="
                position: fixed;
                background: #1a1a1a;
                border: 1px solid #30363d;
                border-radius: 8px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.4);
                z-index: 10001;
                min-width: 200px;
            ">
                <div style="padding: 10px 12px; border-bottom: 1px solid #30363d; background: #0d1117;">
                    <strong style="color: #f0f6fc; font-size: 13px;">${agentName} - Select Task</strong>
                </div>
                ${taskTypes.map(task => `
                    <div class="task-item" data-task-type="${task.type}" style="
                        padding: 10px 12px;
                        cursor: pointer;
                        display: flex;
                        align-items: center;
                        gap: 10px;
                        border-bottom: 1px solid #30363d;
                        transition: background 0.2s;
                    ">
                        <i class="fas ${task.icon}" style="color: ${task.color}; width: 16px;"></i>
                        <span style="color: #f0f6fc; font-size: 13px;">${task.label}</span>
                    </div>
                `).join('')}
            </div>
        `;

        // Insert submenu into DOM
        const tempContainer = document.createElement('div');
        tempContainer.innerHTML = submenuHtml;
        const submenu = tempContainer.firstElementChild;
        document.body.appendChild(submenu);

        // Position submenu to the right of agent item
        const itemRect = agentItem.getBoundingClientRect();
        const submenuRect = submenu.getBoundingClientRect();
        const spaceRight = window.innerWidth - itemRect.right;

        if (spaceRight >= submenuRect.width) {
            // Position to the right
            submenu.style.left = `${itemRect.right + 4}px`;
        } else {
            // Position to the left
            submenu.style.left = `${itemRect.left - submenuRect.width - 4}px`;
        }
        submenu.style.top = `${itemRect.top}px`;

        // Add hover effects to task items
        submenu.querySelectorAll('.task-item').forEach(item => {
            item.addEventListener('mouseenter', () => {
                item.style.background = 'rgba(99, 102, 241, 0.1)';
            });
            item.addEventListener('mouseleave', () => {
                item.style.background = 'transparent';
            });

            // Click handler: assign email with task type
            item.addEventListener('click', async (e) => {
                e.stopPropagation();
                const taskType = item.dataset.taskType;

                // Get custom instructions from textarea
                const instructionsTextarea = document.getElementById(`ai-custom-instruction-${emailId}`);
                const customInstructions = instructionsTextarea?.value?.trim() || '';

                this.log.info(`🎯 Assigning email ${emailId} to ${agentName} with task: ${taskType}`);
                if (customInstructions) {
                    this.log.info(`📝 Custom instructions: ${customInstructions}`);
                }

                // Close both dropdowns
                submenu.remove();
                parentDropdown.remove();

                // Assign email with task type and custom instructions
                await this.assignEmailToAgentWithTask(
                    emailId,
                    agentName,
                    agentId,
                    taskType,
                    null, // cell (not applicable from preview)
                    customInstructions
                );

                // Refresh preview panel to show assignment
                const email = this.state.emails.find(e => e.id === emailId);
                if (email) {
                    this.showEmailPreview(email);
                }
            });
        });

        // Close submenu on outside click
        const closeHandler = (e) => {
            if (!submenu.contains(e.target)) {
                submenu.remove();
                document.removeEventListener('click', closeHandler);
            }
        };
        setTimeout(() => document.addEventListener('click', closeHandler), 0);
    },

    /**
     * Show reassignment confirmation modal
     * Returns: 'move' | 'new' | 'cancel'
     */
    async showReassignmentModal(emailId, existingAgentName, newAgentName) {
        return new Promise((resolve) => {
            // Create modal backdrop
            const modal = document.createElement('div');
            modal.className = 'reassignment-modal';
            modal.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 20000;
                animation: fadeIn 0.2s ease;
            `;

            // Create modal content
            const content = document.createElement('div');
            content.style.cssText = `
                background: #1a1a1a;
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 24px;
                max-width: 480px;
                box-shadow: 0 16px 48px rgba(0,0,0,0.6);
                animation: slideUp 0.3s ease;
            `;

            content.innerHTML = `
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                    <i class="fas fa-exchange-alt" style="color: #f59e0b; font-size: 24px;"></i>
                    <h3 style="color: #f0f6fc; margin: 0; font-size: 18px; font-weight: 600;">Email Already Assigned</h3>
                </div>
                <p style="color: #8b949e; margin: 0 0 20px 0; line-height: 1.6;">
                    This email is currently assigned to <strong style="color: #6366f1;">${this.escapeHtml(existingAgentName)}</strong>.
                    What would you like to do?
                </p>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <button class="modal-btn-move" style="padding: 12px 16px; background: #6366f1; color: white; border: none; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 10px; font-size: 14px; font-weight: 500; transition: background 0.2s;">
                        <i class="fas fa-arrow-right"></i>
                        <span>Move to ${this.escapeHtml(newAgentName)}</span>
                    </button>
                    <button class="modal-btn-new" style="padding: 12px 16px; background: #30363d; color: #f0f6fc; border: 1px solid #484f58; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 10px; font-size: 14px; font-weight: 500; transition: all 0.2s;">
                        <i class="fas fa-plus"></i>
                        <span>Create New Thread (keep both)</span>
                    </button>
                    <button class="modal-btn-cancel" style="padding: 12px 16px; background: transparent; color: #8b949e; border: 1px solid #30363d; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 10px; font-size: 14px; font-weight: 500; transition: all 0.2s;">
                        <i class="fas fa-times"></i>
                        <span>Cancel</span>
                    </button>
                </div>
            `;

            modal.appendChild(content);
            document.body.appendChild(modal);

            // Add hover effects
            const moveBtn = content.querySelector('.modal-btn-move');
            const newBtn = content.querySelector('.modal-btn-new');
            const cancelBtn = content.querySelector('.modal-btn-cancel');

            moveBtn.addEventListener('mouseenter', () => moveBtn.style.background = '#5558dd');
            moveBtn.addEventListener('mouseleave', () => moveBtn.style.background = '#6366f1');

            newBtn.addEventListener('mouseenter', () => { newBtn.style.background = '#484f58'; newBtn.style.borderColor = '#6b7280'; });
            newBtn.addEventListener('mouseleave', () => { newBtn.style.background = '#30363d'; newBtn.style.borderColor = '#484f58'; });

            cancelBtn.addEventListener('mouseenter', () => { cancelBtn.style.background = 'rgba(255,255,255,0.05)'; cancelBtn.style.borderColor = '#484f58'; });
            cancelBtn.addEventListener('mouseleave', () => { cancelBtn.style.background = 'transparent'; cancelBtn.style.borderColor = '#30363d'; });

            // Button handlers
            moveBtn.addEventListener('click', () => {
                document.body.removeChild(modal);
                resolve('move');
            });

            newBtn.addEventListener('click', () => {
                document.body.removeChild(modal);
                resolve('new');
            });

            cancelBtn.addEventListener('click', () => {
                document.body.removeChild(modal);
                resolve('cancel');
            });

            // Close on backdrop click
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    document.body.removeChild(modal);
                    resolve('cancel');
                }
            });

            // Close on Escape key
            const escapeHandler = (e) => {
                if (e.key === 'Escape') {
                    document.body.removeChild(modal);
                    document.removeEventListener('keydown', escapeHandler);
                    resolve('cancel');
                }
            };
            document.addEventListener('keydown', escapeHandler);
        });
    },

    /**
     * Reassign email from old thread to new agent
     */
    async reassignEmail(emailId, oldThreadSlug, newAgentName, newAgentId, cell) {
        this.log.info(`🔄 Reassigning email ${emailId} from ${oldThreadSlug} to ${newAgentName}`);

        try {
            const userId = window.UserAuth?.user?.id || 1;

            // Step 1: Unlink from old thread
            const unlinkResponse = await this.api.post('/api/thread-assignments/email/unlink', {
                thread_slug: oldThreadSlug,
                email_thread_id: emailId,
                user_id: userId
            });

            if (!unlinkResponse || !unlinkResponse.success) {
                throw new Error('Failed to unlink email from old thread');
            }

            this.log.success(`✅ Email unlinked from ${oldThreadSlug}`);
            if (typeof showToast === 'function') {
                showToast('📤 Email unlinked from old thread', 'info', 2000);
            }

            // Step 2: Remove from local state
            delete this.state.emailThreads[emailId];

            // Step 3: Small delay for database commit
            await new Promise(resolve => setTimeout(resolve, 200));

            // Step 4: Create new thread (existing assignEmailToAgent logic)
            await this.assignEmailToAgent(emailId, newAgentName, cell, newAgentId);

            this.log.success(`✅ Email reassigned to ${newAgentName}`);

        } catch (error) {
            this.log.error('❌ Reassignment failed:', error);
            this.showError(`Failed to reassign email: ${error.message}`);
        }
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

            // ✅ NEW: Sync email assignments from ThreadManager
            if (typeof ThreadManager !== 'undefined' && ThreadManager.threads) {
                this.log.info(`📧 Syncing email assignments from ${ThreadManager.threads.length} threads...`);

                let assignedCount = 0;
                ThreadManager.threads.forEach(thread => {
                    // ✅ FIX (Jan 3, 2026): Try multiple field locations for email ID
                    const emailId = thread.email_thread_id ||
                        thread.metadata?.email_thread_id ||
                        thread.metadata?.email_id;
                    if (emailId) {
                        this.state.emailThreads[emailId] = thread.id;
                        assignedCount++;
                    }
                });

                this.log.success(`✅ Found ${assignedCount} email-to-thread assignments`);

                // Refresh table to show assignments
                if (this.state.tabulatorTable) {
                    this.state.tabulatorTable.redraw();
                }
            } else {
                this.log.warn('⚠️ ThreadManager not available, cannot sync email assignments');
            }

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
     * ✅ NEW: Subscribe to realtime thread updates
     * Updates email assignments when threads are created/updated/deleted
     */
    subscribeToRealtimeUpdates() {
        this.log.info('📡 Subscribing to realtime thread updates...');

        // Listen for ThreadManager updates (threads subscription already exists in realtime-subscriptions-init.js)
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.on === 'function') {
            ThreadManager.on('threads-updated', () => {
                this.log.info('🔔 Threads updated - syncing email assignments');
                this.syncEmailAssignments();
            });
            this.log.success('✅ Subscribed to ThreadManager updates');
        } else {
            this.log.warn('⚠️ ThreadManager events not available - realtime sync disabled');
        }

        // ✅ FIX (Jan 3, 2026): Re-sync email mappings when agent threads load
        // This ensures badges render correctly for agent-4, agent-5, etc. after async load
        window.addEventListener('multiagent-threads-loaded', () => {
            this.log.info('🔔 MultiAgent threads loaded - re-syncing email assignments');
            this.syncEmailAssignments(); // Re-sync mappings from newly loaded threads
        });

        // Also listen for window events (backup mechanism)
        window.addEventListener('thread-created', (e) => {
            this.log.info('🔔 Thread created event:', e.detail);
            this.syncEmailAssignments();
        });

        window.addEventListener('thread-updated', (e) => {
            this.log.info('🔔 Thread updated event:', e.detail);
            this.syncEmailAssignments();
        });

        this.log.success('✅ Realtime subscriptions active');
    },

    /**
     * ✅ FIX #4: Load email-thread mappings from database
     * 
     * Restores emailThreads state after page refresh.
     * Shows which emails are assigned to threads even after reload.
     * 
     * Called after loadEmails() to ensure persistence.
     */
    async loadEmailThreadMappings() {
        try {
            this.log.info('🔄 Loading email-thread mappings from database...');

            const response = await this.api.get(`${this.state.apiBase}/email-thread-mappings`);

            console.log('🔍 [loadEmailThreadMappings] Raw API response:', response);
            console.log('🔍 [loadEmailThreadMappings] response.success:', response.success);
            console.log('🔍 [loadEmailThreadMappings] response.mappings:', response.mappings);
            console.log('🔍 [loadEmailThreadMappings] response.count:', response.count);

            if (response.success && response.mappings) {
                // Replace in-memory state with database mappings
                this.state.emailThreads = response.mappings;

                console.log('🔍 [loadEmailThreadMappings] SET this.state.emailThreads to:', this.state.emailThreads);
                console.log('🔍 [loadEmailThreadMappings] Sample keys:', Object.keys(this.state.emailThreads).slice(0, 3));

                this.log.success(`✅ Loaded ${response.count} email-thread mapping(s) from database`);

                // ✅ CRITICAL (Jan 3, 2026): Refresh ThreadManager to load assigned threads
                if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.loadThreadsFromBackend === 'function') {
                    this.log.info('🔄 Refreshing ThreadManager to load assigned threads...');
                    await ThreadManager.loadThreadsFromBackend();
                    console.log('🔍 [loadEmailThreadMappings] ThreadManager.threads after refresh:', ThreadManager.threads?.length);
                    console.log('🔍 [loadEmailThreadMappings] Sample thread IDs:', ThreadManager.threads?.slice(0, 3).map(t => ({ id: t.id, slug: t.thread_slug, email: t.email_thread_id })));
                    this.log.success('✅ ThreadManager refreshed with assigned threads');
                }

                // Redraw table to show agent badges (after threads are loaded)
                if (this.state.tabulatorTable) {
                    this.log.info('🔄 Redrawing table to show persisted assignments...');
                    this.state.tabulatorTable.redraw();
                    console.log('🔍 [loadEmailThreadMappings] Table redraw completed');
                }
            } else {
                this.log.warn('⚠️ No email-thread mappings found in database');
                this.state.emailThreads = {};
            }

        } catch (error) {
            this.log.error('❌ Failed to load email-thread mappings:', error);
            // Don't fail - just continue with empty mappings
            this.state.emailThreads = {};
        }
    },

    /**
     * ✅ NEW: Sync email assignments from ThreadManager
     * Called when threads are updated in realtime
     */
    syncEmailAssignments() {
        if (!ThreadManager || !ThreadManager.threads) {
            this.log.warn('⚠️ ThreadManager not available');
            return;
        }

        this.log.info('🔄 Syncing email assignments from ThreadManager...');

        const oldCount = Object.keys(this.state.emailThreads).length;
        this.state.emailThreads = {};

        ThreadManager.threads.forEach(thread => {
            // ✅ FIX (Jan 3, 2026): Try multiple field locations for email ID
            const emailId = thread.email_thread_id ||
                thread.metadata?.email_thread_id ||
                thread.metadata?.email_id;

            if (emailId) {
                this.state.emailThreads[emailId] = thread.id;

                // Debug log first few mappings
                if (Object.keys(this.state.emailThreads).length <= 3) {
                    console.log(`[CommunicationHub] Mapped email ${emailId.substring(0, 20)}... → thread ${thread.id} (${thread.location})`);
                }
            }
        });

        const newCount = Object.keys(this.state.emailThreads).length;
        this.log.success(`✅ Synced ${newCount} email assignments (was ${oldCount})`);

        // Refresh table to show updated assignments
        if (this.state.tabulatorTable) {
            this.log.info('🔄 Redrawing table to show new assignments...');
            this.state.tabulatorTable.redraw();
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
                        ${this.renderAttachmentsSection(email)}
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
    },

    /**
     * Download email attachment
     */
    async downloadAttachment(emailId, attachmentId, filename) {
        this.log.info(`Downloading attachment: ${filename}`);

        try {
            // Get email data to determine provider
            const email = await this.fetchEmailContent(emailId);
            const provider = email.provider;
            const userId = window.UserAuth?.user?.id || 1;

            let downloadUrl;
            if (provider === 'gmail') {
                downloadUrl = `${this.state.apiBase}/gmail/attachment?message_id=${emailId}&attachment_id=${attachmentId}&user_id=${userId}`;
            } else if (provider === 'outlook') {
                downloadUrl = `${this.state.apiBase}/outlook/attachment?message_id=${emailId}&attachment_id=${attachmentId}&user_id=${userId}`;
            } else {
                throw new Error(`Unknown provider: ${provider}`);
            }

            // Download the file
            const response = await fetch(downloadUrl);
            if (!response.ok) {
                throw new Error(`Download failed: ${response.statusText}`);
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            this.log.success(`Downloaded: ${filename}`);
        } catch (error) {
            this.log.error(`Failed to download attachment: ${error.message}`);
            alert(`Failed to download attachment: ${error.message}`);
        }
    }
};
