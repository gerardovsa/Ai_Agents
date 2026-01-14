/**
 * FILE: UI/external/modules/communication-hub/communication-hub.js
 * PURPOSE: Communication Hub module - Unified inbox with AI agent integration
 * 
 * FEATURES:
 * - Gmail and Outlook unified inbox
 * - Drag-and-drop emails to AI sidebar
 * - Right-click context menu to send to AI agents
 * - Email composition and threading
 * - Full-text search across accounts
 * 
 * DEPENDENCIES:
 * - BaseModule (module-base.js)
 * - Tabulator.js (for email table)
 * - AI Chat system (for drag-and-drop integration)
 * 
 * EXPORTS:
 * - CommunicationHubModule class
 * 
 * LAST MODIFIED: 2025-11-27 - Fixed initialization with BaseModule polyfill
 */

console.log('🔷 Communication Hub Module Loading - VERSION 2.3 - Uses Global BaseModule');

// ============================================================
// IMPORTANT: This module extends the global BaseModule from
// UI/js/module-base.js - BaseModule loaded globally in HTML
// ============================================================

// Safety check: Ensure BaseModule exists globally
if (typeof BaseModule === 'undefined') {
    console.error('❌ [Communication Hub] CRITICAL: BaseModule not found! Module cannot load.');
    console.error('   Ensure UI/js/module-base.js is loaded in business-ai-platform-v2.html.');
    throw new Error('BaseModule is required but not defined');
}

console.log('✅ [Communication Hub] BaseModule found globally, extending it...');

class CommunicationHubModule extends BaseModule {
    constructor(moduleId) {
        super(moduleId);

        // State
        this.emails = [];
        this.selectedAccount = 'all';
        this.accounts = [];
        this.tabulatorTable = null;
        this.tableReady = false;
        this.selectedEmails = new Set();
        this.draggedEmail = null;

        // Row tagging system
        this.emailTags = {}; // { emailId: 'green' | 'orange' | 'red' | null }

        // Export and pagination state
        this.currentPage = 1;
        this.pageSize = 50;
        this.currentAccountFilter = 'all';
        this.currentEmailLimit = 20;

        // Backend URL - dynamic detection (base URL only, endpoints will be appended)
        // FIXED NOV 29: Simplified to use window.API_BASE_URL consistently
        this.apiBase = `${window.API_BASE_URL || 'http://localhost:5001'}/api/communication-hub`;

        // IMPORTANT: Keep backendUrl as base for manifest loading (no /api/communication-hub path)
        // Parent BaseModule.initialize() needs clean base URL to fetch manifest
        this.backendUrl = window.API_BASE_URL || 'http://localhost:5001';

        // Context menu
        this.contextMenu = null;
    }

    async initialize() {
        console.log('[Communication Hub] Initializing...');

        // Call parent initialize
        await super.initialize();

        // Fallback: If manifest not loaded from backend, use hardcoded version
        if (!this.manifest) {
            console.log('[Communication Hub] Using hardcoded manifest (standalone mode)');
            this.manifest = {
                id: 'communication-hub',
                name: 'Communication Hub',
                main_tab_id: 'communication',
                icon: 'fas fa-comments',
                color: '#6366f1',
                description: 'Unified inbox for Gmail and Outlook with AI agent integration',
                tabs: [
                    { id: 'unified-inbox', name: 'Unified Inbox', icon: 'fas fa-inbox', default: true },
                    { id: 'compose', name: 'Compose', icon: 'fas fa-pen' },
                    { id: 'threads', name: 'Threads', icon: 'fas fa-comments' },
                    { id: 'search', name: 'Search', icon: 'fas fa-search' }
                ]
            };
        }

        // Ensure base UI structure (header + sub-tabs) exists
        try {
            await this.createModuleStructure();
        } catch (e) {
            console.warn('[Communication Hub] createModuleStructure failed:', e);
        }

        // Load connected accounts
        await this.loadAccounts();

        // Initialize tabs
        try {
            this.initializeSubTabs();
        } catch (e) {
            console.error('[Communication Hub] Failed to initialize sub-tabs:', e);
            throw e;  // Re-throw to ensure failure is visible
        }

        // Setup drag-and-drop
        try {
            this.setupDragAndDrop();
        } catch (e) {
            console.warn('[Communication Hub] Failed to setup drag-and-drop:', e);
        }

        // Setup context menu
        try {
            this.setupContextMenu();
        } catch (e) {
            console.warn('[Communication Hub] Failed to setup context menu:', e);
        }

        console.log('[Communication Hub] ✅ Initialized successfully');
    }

    // ==================== TAB INITIALIZATION ====================

    initializeSubTabs() {
        console.log('[Communication Hub] initializeSubTabs() called');

        // Get the main container
        const mainContainer = this.getSubTabContainer('main');
        if (!mainContainer) {
            console.error('[Communication Hub] Main container not found!');
            return;
        }

        // Create sub-tab navigation and content containers
        mainContainer.innerHTML = `
            <div class="communication-hub-wrapper" style="height: 100%; display: flex; flex-direction: column;">
                <!-- Sub-tab Navigation -->
                <div class="module-subtabs-nav" style="display: flex; gap: 0; background: #161b22; border-bottom: 1px solid #30363d; padding: 0 16px;">
                    <button class="module-subtab-btn active" data-subtab="unified-inbox" style="padding: 12px 20px; background: transparent; border: none; border-bottom: 2px solid #6366f1; color: #f0f6fc; cursor: pointer; font-size: 14px;">
                        <i class="fas fa-inbox"></i> Unified Inbox
                    </button>
                    <button class="module-subtab-btn" data-subtab="compose" style="padding: 12px 20px; background: transparent; border: none; border-bottom: 2px solid transparent; color: #8b949e; cursor: pointer; font-size: 14px;">
                        <i class="fas fa-pen"></i> Compose
                    </button>
                    <button class="module-subtab-btn" data-subtab="threads" style="padding: 12px 20px; background: transparent; border: none; border-bottom: 2px solid transparent; color: #8b949e; cursor: pointer; font-size: 14px;">
                        <i class="fas fa-comments"></i> Threads
                    </button>
                    <button class="module-subtab-btn" data-subtab="search" style="padding: 12px 20px; background: transparent; border: none; border-bottom: 2px solid transparent; color: #8b949e; cursor: pointer; font-size: 14px;">
                        <i class="fas fa-search"></i> Search
                    </button>
                </div>
                
                <!-- Sub-tab Content Containers -->
                <div class="module-subtabs-content" style="flex: 1; overflow: auto;">
                    <div class="module-subtab-content active" id="communication-hub-subtab-unified-inbox" data-subtab="unified-inbox"></div>
                    <div class="module-subtab-content" id="communication-hub-subtab-compose" data-subtab="compose" style="display: none;"></div>
                    <div class="module-subtab-content" id="communication-hub-subtab-threads" data-subtab="threads" style="display: none;"></div>
                    <div class="module-subtab-content" id="communication-hub-subtab-search" data-subtab="search" style="display: none;"></div>
                </div>
            </div>
        `;

        // Attach sub-tab click handlers
        mainContainer.querySelectorAll('.module-subtab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tabId = btn.dataset.subtab;
                this.switchSubTab(tabId);
            });
        });

        // Now initialize each sub-tab content
        this.initializeUnifiedInbox();
        this.initializeCompose();
        this.initializeThreads();
        this.initializeSearch();

        console.log('[Communication Hub] All sub-tabs initialized');
    }

    // Switch between sub-tabs
    switchSubTab(tabId) {
        console.log(`[Communication Hub] Switching to sub-tab: ${tabId}`);

        const wrapper = document.querySelector('.communication-hub-wrapper');
        if (!wrapper) return;

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

        // Update content visibility
        wrapper.querySelectorAll('.module-subtab-content').forEach(content => {
            if (content.dataset.subtab === tabId) {
                content.classList.add('active');
                content.style.display = 'block';
            } else {
                content.classList.remove('active');
                content.style.display = 'none';
            }
        });
    }

    // Get specific sub-tab container
    getSubTabContainer(tabName) {
        // For 'main', return the main tab container
        if (tabName === 'main') {
            const moduleId = this.manifest?.id || this.moduleId;
            const mainTabId = this.manifest?.main_tab_id || 'communication';

            return document.getElementById(`${moduleId}-main-container`) ||
                document.getElementById(`tab-${mainTabId}`) ||
                document.getElementById(`tab-${moduleId}`);
        }

        // For sub-tabs, return the specific sub-tab container
        return document.getElementById(`communication-hub-subtab-${tabName}`);
    }

    // ==================== TAB 1: UNIFIED INBOX ====================

    initializeUnifiedInbox() {
        const container = this.getSubTabContainer('unified-inbox');
        if (!container) {
            console.error('[Communication Hub] Cannot initialize Unified Inbox - container not found');
            return;
        }

        console.log('[Communication Hub] Initializing Unified Inbox tab...');

        container.innerHTML = `
            <div class="module-dashboard">
                <!-- Header -->
                <div class="dashboard-card">
                    <div class="card-header">
                        <div class="header-left" style="width: 100%; display: flex; flex-direction: column; gap: 8px; text-align: center;">
                            <h3 class="card-title" style="font-size: 24px; margin: 0;">
                                <i class="fas fa-inbox"></i> Unified Inbox
                            </h3>
                            <div class="card-subtitle" style="margin: 0;">
                                All messages from Gmail and Outlook
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Stat Cards -->
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon primary">
                            <i class="fas fa-envelope"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Total Emails</div>
                            <div class="stat-value" id="total-emails-count">-</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon success">
                            <i class="fab fa-google"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Gmail</div>
                            <div class="stat-value" id="gmail-count">-</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon info">
                            <i class="fab fa-microsoft"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Outlook</div>
                            <div class="stat-value" id="outlook-count">-</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon warning">
                            <i class="fas fa-envelope-open"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Unread</div>
                            <div class="stat-value" id="unread-count">-</div>
                        </div>
                    </div>
                </div>
                
                <!-- Toolbar -->
                <div class="bulk-operations-toolbar" style="display: flex; align-items: center; gap: 12px; padding: 16px 20px; background: var(--bg-secondary, #1a1f2e); border-bottom: 1px solid var(--border-default, #2a3142); margin-bottom: 20px; flex-wrap: wrap;">
                    <!-- Tag Buttons -->
                    <div style="display: flex; gap: 6px; align-items: center;">
                        <span style="font-size: 12px; color: var(--text-secondary, #7d8590); margin-right: 4px;">Tag:</span>
                        <button class="btn btn-sm" onclick="communicationHub.tagSelectedEmails('clear')" style="padding: 4px 10px; background: #6c757d; border-radius: 6px; font-size: 11px;">
                            <i class="fas fa-times"></i> Clear
                        </button>
                        <button class="btn btn-sm" onclick="communicationHub.tagSelectedEmails('green')" style="padding: 4px 10px; background: #2e7d32; border-radius: 6px; font-size: 11px;">
                            <i class="fas fa-circle"></i> Green
                        </button>
                        <button class="btn btn-sm" onclick="communicationHub.tagSelectedEmails('orange')" style="padding: 4px 10px; background: #e65100; border-radius: 6px; font-size: 11px;">
                            <i class="fas fa-circle"></i> Orange
                        </button>
                        <button class="btn btn-sm" onclick="communicationHub.tagSelectedEmails('red')" style="padding: 4px 10px; background: #c62828; border-radius: 6px; font-size: 11px;">
                            <i class="fas fa-circle"></i> Red
                        </button>
                    </div>
                    
                    <div style="height: 20px; width: 1px; background: var(--border-default, #2a3142);"></div>
                    
                    <!-- Account Filter -->
                    <select id="accountSelector" class="form-control" style="margin: 0; width: auto; padding: 6px 10px; background: var(--bg-card, #0B0E13); border: 1px solid var(--border-default, #2A3142); border-radius: 6px; color: var(--text-primary, #E5E7EB); font-size: 12px;">
                        <option value="all">All Accounts</option>
                        <option value="gmail">Gmail Only</option>
                        <option value="outlook">Outlook Only</option>
                    </select>
                    
                    <!-- Limit Selector -->
                    <select id="email-limit" class="form-control" style="margin: 0; width: auto; padding: 6px 10px; background: var(--bg-card, #0B0E13); border: 1px solid var(--border-default, #2A3142); border-radius: 6px; color: var(--text-primary, #E5E7EB); font-size: 12px;">
                        <option value="20" selected>Show 20</option>
                        <option value="50">Show 50</option>
                        <option value="100">Show 100</option>
                        <option value="200">Show 200</option>
                    </select>
                    
                    <!-- Refresh Button -->
                    <button class="btn btn-primary" id="email-refresh-btn" onclick="communicationHub.refreshInbox()" style="padding: 6px 12px; font-size: 12px;">
                        <i class="fas fa-sync-alt"></i> Refresh
                    </button>
                    
                    <div style="flex: 1;"></div>
                    
                    <!-- Selected Count -->
                    <span id="selected-count" style="font-size: 12px; color: var(--text-secondary, #7d8590);">Selected: 0</span>
                    
                    <!-- Export Buttons -->
                    <div style="display: flex; gap: 6px;">
                        <button class="btn btn-secondary" onclick="communicationHub.exportEmails('excel')" style="padding: 6px 10px; font-size: 11px;">
                            <i class="fas fa-file-excel"></i> Excel
                        </button>
                        <button class="btn btn-secondary" onclick="communicationHub.exportEmails('csv')" style="padding: 6px 10px; font-size: 11px;">
                            <i class="fas fa-file-csv"></i> CSV
                        </button>
                        <button class="btn btn-secondary" onclick="communicationHub.exportEmails('pdf')" style="padding: 6px 10px; font-size: 11px;">
                            <i class="fas fa-file-pdf"></i> PDF
                        </button>
                    </div>
                    
                    <!-- Send to AI Button -->
                    <button class="btn btn-secondary" onclick="communicationHub.sendSelectedToAI()" style="padding: 6px 12px; font-size: 12px;">
                        <i class="fas fa-robot"></i> Send to AI
                    </button>
                </div>
                
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
                
                <!-- Pagination Controls (in footer) -->
                <div id="email-pagination" style="display: none; padding: 16px 20px; background: var(--bg-secondary, #1a1f2e); border-top: 1px solid var(--border-default, #2a3142); border-radius: 0 0 8px 8px; display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <span style="font-size: 12px; color: var(--text-secondary, #7d8590);">Page:</span>
                        <button id="btn-first-page" class="btn btn-sm" style="padding: 4px 8px; font-size: 11px;">
                            <i class="fas fa-angle-double-left"></i>
                        </button>
                        <button id="btn-prev-page" class="btn btn-sm" style="padding: 4px 8px; font-size: 11px;">
                            <i class="fas fa-angle-left"></i>
                        </button>
                        <span id="page-info" style="font-size: 12px; color: var(--text-primary, #e5e7eb); min-width: 100px; text-align: center;">Page 1 of 1</span>
                        <button id="btn-next-page" class="btn btn-sm" style="padding: 4px 8px; font-size: 11px;">
                            <i class="fas fa-angle-right"></i>
                        </button>
                        <button id="btn-last-page" class="btn btn-sm" style="padding: 4px 8px; font-size: 11px;">
                            <i class="fas fa-angle-double-right"></i>
                        </button>
                    </div>
                    
                    <select id="page-size-selector" class="form-control" style="width: auto; padding: 4px 8px; font-size: 11px; margin: 0;">
                        <option value="25">25 per page</option>
                        <option value="50" selected>50 per page</option>
                        <option value="100">100 per page</option>
                    </select>
                </div>
                
                <!-- Email Preview Panel (Slide-out) -->
                <div id="emailPreview" class="email-preview-panel" style="display: none;">
                    <div class="preview-header">
                        <h3>Email Preview</h3>
                        <button class="btn-close" onclick="window.communicationHub.closePreview()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div id="previewContent" class="preview-content"></div>
                </div>
            </div>
        `;

        // Setup event listeners
        this.setupInboxEventListeners();

        console.log('[Communication Hub] Unified Inbox initialized (awaiting user Refresh)');
    }

    setupInboxEventListeners() {
        // Account filter
        document.getElementById('accountSelector')?.addEventListener('change', (e) => {
            this.currentAccountFilter = e.target.value;
        });

        // Email limit
        document.getElementById('email-limit')?.addEventListener('change', (e) => {
            this.currentEmailLimit = parseInt(e.target.value);
        });

        // Page size
        document.getElementById('page-size-selector')?.addEventListener('change', (e) => {
            this.pageSize = parseInt(e.target.value);
            if (this.tabulatorTable) {
                this.tabulatorTable.setPageSize(this.pageSize);
            }
        });

        // Pagination buttons
        document.getElementById('btn-first-page')?.addEventListener('click', () => {
            if (this.tabulatorTable) this.tabulatorTable.setPage(1);
        });

        document.getElementById('btn-prev-page')?.addEventListener('click', () => {
            if (this.tabulatorTable) this.tabulatorTable.previousPage();
        });

        document.getElementById('btn-next-page')?.addEventListener('click', () => {
            if (this.tabulatorTable) this.tabulatorTable.nextPage();
        });

        document.getElementById('btn-last-page')?.addEventListener('click', () => {
            if (this.tabulatorTable) this.tabulatorTable.setPage('last');
        });

        console.log('[Communication Hub] Event listeners registered');
    }

    createEmailTable() {
        const container = document.getElementById('email-table-container');
        if (!container) {
            console.error('[Communication Hub] Cannot find email-table-container');
            return;
        }

        // Destroy existing table
        if (this.tabulatorTable) {
            console.log('[Communication Hub] Destroying existing Tabulator instance');
            this.tabulatorTable.destroy();
        }

        const self = this;

        console.log('[Communication Hub] Creating enhanced Tabulator instance...');

        this.tabulatorTable = new Tabulator(container, {
            data: [],
            layout: "fitDataStretch",
            height: "100%",
            pagination: "local",
            paginationSize: this.pageSize,
            paginationSizeSelector: [25, 50, 100, 200],
            movableColumns: true,
            resizableColumns: true,
            selectable: true,
            selectableRangeMode: "click",
            placeholder: "No emails found. Click Refresh to load your emails.",
            renderComplete: () => {
                this.tableReady = true;
                console.log('[Communication Hub] Tabulator render complete, table ready');
            },

            rowFormatter: (row) => {
                const element = row.getElement();
                const emailData = row.getData();

                // Make row draggable
                element.setAttribute('draggable', 'true');
                element.style.cursor = 'grab';

                // Drag start handler
                element.addEventListener('dragstart', (e) => {
                    element.style.cursor = 'grabbing';
                    element.style.opacity = '0.5';

                    // Store email data for transfer
                    const emailPayload = {
                        id: emailData.id,
                        from: emailData.from,
                        to: emailData.to,
                        subject: emailData.subject,
                        snippet: emailData.snippet,
                        body_text: emailData.body_text,
                        body_html: emailData.body_html,
                        date: emailData.date,
                        provider: emailData.provider,
                        is_read: emailData.is_read,
                        account_email: emailData.account_email
                    };

                    e.dataTransfer.setData('application/json', JSON.stringify({
                        type: 'email',
                        data: emailPayload
                    }));
                    e.dataTransfer.effectAllowed = 'copy';

                    console.log('[Communication Hub] Drag started for email:', emailData.subject);
                });

                // Drag end handler
                element.addEventListener('dragend', (e) => {
                    element.style.cursor = 'grab';
                    element.style.opacity = '1';
                    console.log('[Communication Hub] Drag ended');
                });
            },

            columns: [
                // Drag handle
                {
                    title: '<i class="fas fa-grip-vertical" title="Drag to AI Agent"></i>',
                    field: "_drag",
                    width: 40,
                    hozAlign: "center",
                    headerSort: false,
                    frozen: true,
                    formatter: (cell) => {
                        return '<i class="fas fa-hand-pointer" style="cursor: grab; color: #6366f1; font-size: 14px;" title="Drag to AI Agent or Prime Chat"></i>';
                    },
                    cellClick: (e, cell) => {
                        e.stopPropagation();
                    }
                },

                // Selection checkbox
                {
                    formatter: "rowSelection",
                    titleFormatter: "rowSelection",
                    hozAlign: "center",
                    headerSort: false,
                    width: 50,
                    frozen: true,
                    cellClick: (e, cell) => {
                        e.stopPropagation();
                    }
                },

                // Tag column
                {
                    title: "Tag",
                    field: "_tag",
                    width: 60,
                    hozAlign: "center",
                    headerSort: false,
                    frozen: true,
                    formatter: (cell) => {
                        const emailId = cell.getRow().getData().id;
                        const tag = self.emailTags[emailId];

                        if (!tag) {
                            return '<i class="fas fa-circle" style="color: #6c757d; font-size: 10px;"></i>';
                        }

                        const colors = {
                            'green': '#2e7d32',
                            'orange': '#e65100',
                            'red': '#c62828'
                        };

                        return `<i class="fas fa-circle" style="color: ${colors[tag]}; font-size: 10px;"></i>`;
                    },
                    tooltip: true
                },

                // Provider
                {
                    title: "Provider",
                    field: "provider",
                    width: 100,
                    hozAlign: "center",
                    headerFilter: "list",
                    headerFilterParams: {
                        values: {
                            "": "All",
                            "gmail": "Gmail",
                            "outlook": "Outlook"
                        },
                        clearable: true
                    },
                    formatter: (cell) => {
                        const provider = cell.getValue();
                        const icons = {
                            'gmail': '<i class="fab fa-google" style="color: #EA4335; font-size: 16px;"></i>',
                            'outlook': '<i class="fab fa-microsoft" style="color: #0078D4; font-size: 16px;"></i>'
                        };
                        return icons[provider] || provider;
                    },
                    tooltip: (cell) => {
                        const provider = cell.getValue();
                        return provider.charAt(0).toUpperCase() + provider.slice(1);
                    }
                },

                // From
                {
                    title: "From",
                    field: "from",
                    width: 220,
                    headerFilter: "input",
                    headerFilterPlaceholder: "Search sender...",
                    formatter: (cell) => {
                        const value = cell.getValue() || '';
                        return `<span style="font-weight: 500;">${value}</span>`;
                    },
                    tooltip: true
                },

                // Subject
                {
                    title: "Subject",
                    field: "subject",
                    minWidth: 300,
                    headerFilter: "input",
                    headerFilterPlaceholder: "Search subject...",
                    formatter: (cell) => {
                        const row = cell.getRow().getData();
                        const subject = cell.getValue() || '';
                        const isUnread = !row.is_read;
                        return `<span style="font-weight: ${isUnread ? '700' : '400'}; color: ${isUnread ? 'var(--text-primary)' : 'var(--text-secondary)'}">${subject}</span>`;
                    },
                    tooltip: true
                },

                // Preview
                {
                    title: "Preview",
                    field: "snippet",
                    minWidth: 200,
                    headerFilter: "input",
                    headerFilterPlaceholder: "Search content...",
                    formatter: (cell) => {
                        const snippet = cell.getValue() || '';
                        return `<span style="color: var(--text-secondary, #7d8590); font-size: 12px;">${snippet}</span>`;
                    },
                    tooltip: true
                },

                // Date
                {
                    title: "Date",
                    field: "date",
                    width: 160,
                    headerSort: true,
                    formatter: (cell) => {
                        const dateStr = cell.getValue();
                        if (!dateStr) return '';

                        const date = new Date(dateStr);
                        const now = new Date();
                        const diff = now - date;
                        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

                        if (days === 0) {
                            return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
                        } else if (days === 1) {
                            return 'Yesterday';
                        } else if (days < 7) {
                            return date.toLocaleDateString('en-US', { weekday: 'short' });
                        } else {
                            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                        }
                    },
                    tooltip: (cell) => {
                        const dateStr = cell.getValue();
                        if (!dateStr) return '';
                        return new Date(dateStr).toLocaleString();
                    }
                },

                // Status
                {
                    title: "Status",
                    field: "is_read",
                    width: 100,
                    hozAlign: "center",
                    headerFilter: "list",
                    headerFilterParams: {
                        values: {
                            "": "All",
                            "false": "Unread",
                            "true": "Read"
                        },
                        clearable: true
                    },
                    formatter: (cell) => {
                        const isRead = cell.getValue();
                        if (isRead) {
                            return '<span style="background: rgba(16, 185, 129, 0.2); color: #10b981; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600; text-transform: uppercase;">Read</span>';
                        } else {
                            return '<span style="background: rgba(245, 158, 11, 0.2); color: #f59e0b; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600; text-transform: uppercase;">Unread</span>';
                        }
                    },
                    tooltip: true
                },

                // Actions
                {
                    title: "Actions",
                    width: 120,
                    hozAlign: "center",
                    headerSort: false,
                    formatter: () => {
                        return `
                            <button class="action-btn action-btn-ai" style="margin: 0 4px; padding: 4px 10px; font-size: 11px; background: var(--primary-color, #0078d4); color: white; border: none; border-radius: 4px; cursor: pointer;" title="Send to AI">
                                <i class="fas fa-robot"></i>
                            </button>
                            <button class="action-btn action-btn-reply" style="margin: 0 4px; padding: 4px 10px; font-size: 11px; background: var(--secondary-color, #6c757d); color: white; border: none; border-radius: 4px; cursor: pointer;" title="Reply">
                                <i class="fas fa-reply"></i>
                            </button>
                        `;
                    },
                    cellClick: (e, cell) => {
                        e.stopPropagation();
                        const email = cell.getRow().getData();

                        if (e.target.closest('.action-btn-ai')) {
                            self.sendEmailToAI(email);
                        } else if (e.target.closest('.action-btn-reply')) {
                            self.replyToEmail(email.id);
                        }
                    },
                    tooltip: true
                }
            ],

            // Event handlers
            rowClick: (e, row) => {
                // Don't open preview if clicking checkbox or action buttons
                if (e.target.closest('.tabulator-row-handle') ||
                    e.target.closest('.action-btn')) {
                    return;
                }
                this.openEmailPreview(row.getData());
            },

            rowContext: (e, row) => {
                e.preventDefault();
                this.showContextMenu(e, row.getData());
            },

            rowSelectionChanged: (data, rows) => {
                self.selectedEmails.clear();
                data.forEach(email => {
                    self.selectedEmails.add(email.id);
                });
                self.updateSelectionUI();
                console.log(`[Communication Hub] ${data.length} rows selected`);
            },

            cellDblClick: (e, cell) => {
                // Show cell popup if content is long
                const value = cell.getValue();
                if (value && value.length > 100) {
                    this.showCellPopup(e, cell);
                }
            },

            rowFormatter: (row) => {
                const emailId = row.getData().id;
                const tag = self.emailTags[emailId];

                if (tag) {
                    const colors = {
                        'green': 'rgba(46, 125, 50, 0.1)',
                        'orange': 'rgba(230, 81, 0, 0.1)',
                        'red': 'rgba(198, 40, 40, 0.1)'
                    };
                    const borderColors = {
                        'green': '#2e7d32',
                        'orange': '#e65100',
                        'red': '#c62828'
                    };

                    row.getElement().style.background = colors[tag];
                    row.getElement().style.borderLeft = `4px solid ${borderColors[tag]}`;
                }
            },

            dataLoaded: (data) => {
                console.log(`[Communication Hub] Data loaded: ${data.length} emails`);
                self.updatePaginationUI();
            },

            pageLoaded: (pageno) => {
                self.currentPage = pageno;
                self.updatePaginationUI();
                console.log(`[Communication Hub] Page ${pageno} loaded`);
            }
        });

        // Make rows draggable
        this.makeRowsDraggable();

        console.log('[Communication Hub] Tabulator table created successfully');
    }

    async loadAccounts() {
        try {
            const token = localStorage.getItem('authToken') || localStorage.getItem('auth_token') || '';
            const response = await fetch(`${this.apiBase}/accounts`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            const data = await response.json();

            if (data.success) {
                this.accounts = data.accounts;

                // Populate account selector
                const selector = document.getElementById('accountSelector');
                if (selector) {
                    // Clear existing options except "All Accounts"
                    selector.innerHTML = '<option value="all">All Accounts</option>';

                    this.accounts.forEach(account => {
                        const option = document.createElement('option');
                        option.value = account.id;
                        const icon = account.provider === 'gmail' ? '📧' : '📬';
                        option.textContent = `${icon} ${account.email}`;
                        selector.appendChild(option);
                    });

                    selector.addEventListener('change', (e) => {
                        this.selectedAccount = e.target.value;
                        this.loadEmails();
                    });
                }
            }
        } catch (error) {
            console.error('[Communication Hub] Failed to load accounts:', error);
        }
    }

    async loadEmails() {
        console.log(`[Communication Hub] Loading emails... (filter: ${this.currentAccountFilter}, limit: ${this.currentEmailLimit})`);

        const loadingDiv = document.getElementById('inbox-loading');
        const readyDiv = document.getElementById('inbox-ready');
        const tableContainer = document.getElementById('email-table-container');
        const paginationDiv = document.getElementById('email-pagination');

        // Show loading state
        if (this.tabulatorTable) {
            // Table exists - show loading in Tabulator's placeholder
            console.log('[Communication Hub] Showing loading state in existing table...');
            this.tabulatorTable.clearData();
        } else {
            // First load - show loading spinner in container
            if (tableContainer) {
                tableContainer.innerHTML = `
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 400px; color: var(--text-secondary);">
                        <div class="spinner" style="border: 3px solid var(--border-color); border-top: 3px solid var(--accent-primary); border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin-bottom: 15px;"></div>
                        <div style="font-size: 14px;">Loading emails...</div>
                    </div>
                `;
                tableContainer.style.display = 'block';
            }
        }
        if (loadingDiv) loadingDiv.style.display = 'none';
        if (readyDiv) readyDiv.style.display = 'none';
        if (paginationDiv) paginationDiv.style.display = 'none';

        try {
            const params = new URLSearchParams({
                account: this.currentAccountFilter,
                limit: this.currentEmailLimit
            });

            const token = localStorage.getItem('authToken') || localStorage.getItem('auth_token') || '';
            const response = await fetch(`${this.apiBase}/emails?${params}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            const data = await response.json();

            if (data.success) {
                this.emails = data.emails;

                // Create table if not exists
                if (!this.tabulatorTable) {
                    this.createEmailTable();
                    // Wait for table to be fully built before setting data
                    await new Promise(resolve => {
                        const checkReady = () => {
                            if (this.tableReady) {
                                resolve();
                            } else {
                                setTimeout(checkReady, 50);
                            }
                        };
                        checkReady();
                    });
                }

                // Update table data (only after table is ready)
                if (this.tabulatorTable && this.tableReady) {
                    this.tabulatorTable.setData(this.emails);
                } else if (this.tabulatorTable) {
                    // Fallback: wait for tableBuilt event
                    this.tabulatorTable.on('tableBuilt', () => {
                        this.tabulatorTable.setData(this.emails);
                    });
                }

                // Update stat cards
                const totalCount = this.emails.length;
                const gmailCount = this.emails.filter(e => e.provider === 'gmail').length;
                const outlookCount = this.emails.filter(e => e.provider === 'outlook').length;
                const unreadCount = this.emails.filter(e => !e.is_read).length;

                document.getElementById('total-emails-count').textContent = totalCount;
                document.getElementById('gmail-count').textContent = gmailCount;
                document.getElementById('outlook-count').textContent = outlookCount;
                document.getElementById('unread-count').textContent = unreadCount;

                // Update header stats (new header bar)
                const headerTotalCount = document.getElementById('comm-hub-total-count');
                const headerUnreadCount = document.getElementById('comm-hub-unread-count');
                const headerAccountsCount = document.getElementById('comm-hub-accounts-count');

                if (headerTotalCount) headerTotalCount.textContent = totalCount;
                if (headerUnreadCount) headerUnreadCount.textContent = unreadCount;

                // Count unique accounts (gmail + outlook)
                const uniqueAccounts = new Set();
                this.emails.forEach(email => {
                    if (email.account_email) uniqueAccounts.add(email.account_email);
                });
                if (headerAccountsCount) headerAccountsCount.textContent = uniqueAccounts.size;

                // Update selected count
                document.getElementById('selected-count').textContent = `Selected: 0`;

                // Show table and pagination (table container content already set by Tabulator)
                if (tableContainer) tableContainer.style.display = 'block';
                if (loadingDiv) loadingDiv.style.display = 'none';
                if (paginationDiv) paginationDiv.style.display = 'flex';

                console.log(`[Communication Hub] Loaded ${totalCount} emails (Gmail: ${gmailCount}, Outlook: ${outlookCount}, Unread: ${unreadCount})`);

                // Setup drag-and-drop zones
                setTimeout(() => this.setupEmailDragAndDrop(), 500);
            }
        } catch (error) {
            console.error('[Communication Hub] Failed to load emails:', error);

            // Show error state in table container (replaces loading spinner)
            if (tableContainer) {
                tableContainer.innerHTML = `
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 400px;">
                        <i class="fas fa-exclamation-triangle" style="font-size: 32px; color: #ef4444; margin-bottom: 10px;"></i>
                        <p style="margin: 0; font-size: 16px; color: var(--text-primary, #e5e7eb);">Failed to load emails</p>
                        <p style="margin: 5px 0 15px 0; font-size: 12px; color: var(--text-secondary, #7d8590);">${error.message}</p>
                        <button class="btn btn-primary" onclick="window.communicationHub.refreshInbox()" style="padding: 6px 12px; font-size: 12px;">
                            <i class="fas fa-redo"></i> Retry
                        </button>
                    </div>
                `;
                tableContainer.style.display = 'block';
            }
        }
    }

    setupEmailDragAndDrop() {
        console.log('[Communication Hub] Setting up email drag-and-drop zones...');

        // Setup drop zones for Prime AI chat
        const primeChat = document.querySelector('.ai-chat-panel');
        if (primeChat) {
            this.setupDropZone(primeChat, 'prime');
        }

        // Setup drop zones for agent columns
        const agentColumns = document.querySelectorAll('.agent-column');
        agentColumns.forEach((column, index) => {
            const agentId = column.dataset.agentId || (index + 1);
            this.setupDropZone(column, `agent-${agentId}`);
        });

        console.log('[Communication Hub] Drop zones initialized');
    }

    setupDropZone(element, targetId) {
        // Prevent default drag behaviors
        element.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            e.dataTransfer.dropEffect = 'copy';
            element.classList.add('drag-over');
        });

        element.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            element.classList.remove('drag-over');
        });

        element.addEventListener('drop', async (e) => {
            e.preventDefault();
            e.stopPropagation();
            element.classList.remove('drag-over');

            try {
                const transferData = e.dataTransfer.getData('application/json');
                if (!transferData) return;

                const payload = JSON.parse(transferData);
                if (payload.type !== 'email') return;

                const email = payload.data;
                console.log('[Communication Hub] Email dropped on:', targetId, email.subject);

                // Handle drop based on target
                if (targetId === 'prime') {
                    this.sendEmailToPrimeChat(email);
                } else if (targetId.startsWith('agent-')) {
                    const agentId = targetId.replace('agent-', '');
                    this.sendEmailToAgent(email, agentId);
                }
            } catch (error) {
                console.error('[Communication Hub] Failed to handle email drop:', error);
            }
        });
    }

    async sendEmailToPrimeChat(email) {
        console.log('[Communication Hub] Sending email to Prime Chat:', email.subject);

        // Format email message for Prime AI
        const message = `📧 **Email Analysis Request**

**From:** ${email.from}
**To:** ${email.to || 'N/A'}
**Subject:** ${email.subject}
**Date:** ${new Date(email.date).toLocaleString()}
**Provider:** ${email.provider}

**Email Body:**
${email.body_text || email.body_html || email.snippet || 'No content available'}

---

Please analyze this email and provide:
1. Summary of key points
2. Action items or requests
3. Sentiment analysis
4. Suggested response (if needed)`;

        // Send to Prime AI chat
        if (window.sendToPrimeAI) {
            window.sendToPrimeAI(message);
            this.showNotification('Email sent to Prime AI', 'success');
        } else if (window.PrimeAI && window.PrimeAI.sendMessage) {
            window.PrimeAI.sendMessage(message);
            this.showNotification('Email sent to Prime AI', 'success');
        } else {
            // Fallback: Try to find and fill the chat input
            const chatInput = document.querySelector('.ai-chat-input-container textarea') ||
                document.querySelector('#ai-chat-input') ||
                document.querySelector('textarea[placeholder*="message"]');

            if (chatInput) {
                chatInput.value = message;
                chatInput.dispatchEvent(new Event('input', { bubbles: true }));
                chatInput.focus();
                this.showNotification('Email loaded into Prime AI input', 'success');
            } else {
                console.warn('[Communication Hub] Could not find Prime AI chat input');
                this.showNotification('Could not send to Prime AI - chat not found', 'error');
            }
        }
    }

    async sendEmailToAgent(email, agentId) {
        console.log(`[Communication Hub] Sending email to Agent ${agentId}:`, email.subject);

        // Format email message
        const message = `📧 **Email Analysis Request**

**From:** ${email.from}
**To:** ${email.to || 'N/A'}
**Subject:** ${email.subject}
**Date:** ${new Date(email.date).toLocaleString()}
**Provider:** ${email.provider}

**Email Body:**
${email.body_text || email.body_html || email.snippet || 'No content available'}

---

Please analyze this email.`;

        // Send to specific agent column
        if (window.MultiAgent && window.MultiAgent.sendMessageToAgent) {
            window.MultiAgent.sendMessageToAgent(agentId, message);
            this.showNotification(`Email sent to Agent ${agentId}`, 'success');
        } else {
            // Fallback: Try to find the agent's input field
            const agentColumn = document.querySelector(`[data-agent-id="${agentId}"]`);
            if (agentColumn) {
                const agentInput = agentColumn.querySelector('textarea') ||
                    agentColumn.querySelector('.agent-input');

                if (agentInput) {
                    agentInput.value = message;
                    agentInput.dispatchEvent(new Event('input', { bubbles: true }));
                    agentInput.focus();
                    this.showNotification(`Email loaded into Agent ${agentId} input`, 'success');
                } else {
                    console.warn(`[Communication Hub] Could not find input for Agent ${agentId}`);
                    this.showNotification(`Could not send to Agent ${agentId}`, 'error');
                }
            } else {
                console.warn(`[Communication Hub] Agent column ${agentId} not found`);
                this.showNotification(`Agent ${agentId} not found`, 'error');
            }
        }
    }

    showNotification(message, type = 'info') {
        // Use existing notification system if available
        if (window.showNotification) {
            window.showNotification(message, type);
        } else if (window.Notification && Notification.permission === 'granted') {
            new Notification('Communication Hub', { body: message });
        } else {
            // Fallback to console
            console.log(`[Communication Hub] ${type.toUpperCase()}: ${message}`);

            // Simple toast notification
            const toast = document.createElement('div');
            toast.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#6366f1'};
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                z-index: 10000;
                animation: slideIn 0.3s ease-out;
            `;
            toast.textContent = message;
            document.body.appendChild(toast);

            setTimeout(() => {
                toast.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }
    }

    async refreshInbox() {
        console.log('[Communication Hub] Refreshing inbox...');
        const btn = document.querySelector('.btn-refresh i');
        if (btn) {
            btn.classList.add('fa-spin');
        }

        await this.loadEmails();

        // Setup drag-and-drop after emails are loaded
        this.setupEmailDragAndDrop();

        if (btn) {
            btn.classList.remove('fa-spin');
        }
    }

    // ==================== DRAG AND DROP ====================

    setupDragAndDrop() {
        console.log('[Communication Hub] Setting up drag-and-drop...');
    }

    makeRowsDraggable() {
        const self = this;

        // Add drag handlers to table rows
        this.tabulatorTable.on("rowMouseEnter", function (e, row) {
            const rowElement = row.getElement();
            rowElement.draggable = true;

            rowElement.addEventListener('dragstart', (event) => {
                self.handleDragStart(event, row.getData());
            });

            rowElement.addEventListener('dragend', (event) => {
                self.handleDragEnd(event);
            });
        });
    }

    handleDragStart(event, email) {
        this.draggedEmail = email;

        // Create metadata package for AI
        const emailMetadata = {
            type: 'email',
            provider: email.provider,
            id: email.id,
            from: email.from,
            to: email.to,
            subject: email.subject,
            date: email.date,
            snippet: email.snippet,
            is_read: email.is_read,
            body_preview: email.snippet,
            full_email_id: email.id
        };

        // Set drag data
        event.dataTransfer.effectAllowed = 'copy';
        event.dataTransfer.setData('application/json', JSON.stringify(emailMetadata));
        event.dataTransfer.setData('text/plain', `Email: ${email.subject}\nFrom: ${email.from}\nDate: ${email.date}\n\n${email.snippet}`);

        // Visual feedback
        const dragImage = document.createElement('div');
        dragImage.className = 'drag-preview';
        dragImage.innerHTML = `
            <div class="drag-preview-content">
                <i class="fas fa-envelope"></i>
                <span>${email.subject}</span>
            </div>
        `;
        dragImage.style.position = 'absolute';
        dragImage.style.top = '-1000px';
        document.body.appendChild(dragImage);
        event.dataTransfer.setDragImage(dragImage, 0, 0);

        setTimeout(() => document.body.removeChild(dragImage), 0);

        console.log('[Communication Hub] Dragging email:', email.subject);
    }

    handleDragEnd(event) {
        this.draggedEmail = null;
    }

    // ==================== CONTEXT MENU (RIGHT-CLICK) ====================

    setupContextMenu() {
        // Create context menu element
        const menu = document.createElement('div');
        menu.id = 'email-context-menu';
        menu.className = 'context-menu';
        menu.style.display = 'none';
        menu.innerHTML = `
            <div class="context-menu-item" data-action="send-to-prime">
                <i class="fas fa-robot"></i> Send to AI Prime
            </div>
            <div class="context-menu-item" data-action="send-to-agent">
                <i class="fas fa-users"></i> Send to Agent...
            </div>
            <div class="context-menu-divider"></div>
            <div class="context-menu-item" data-action="reply">
                <i class="fas fa-reply"></i> Reply
            </div>
            <div class="context-menu-item" data-action="forward">
                <i class="fas fa-forward"></i> Forward
            </div>
            <div class="context-menu-divider"></div>
            <div class="context-menu-item" data-action="mark-read">
                <i class="fas fa-eye"></i> Mark as Read
            </div>
            <div class="context-menu-item" data-action="mark-unread">
                <i class="fas fa-eye-slash"></i> Mark as Unread
            </div>
            <div class="context-menu-divider"></div>
            <div class="context-menu-item context-menu-danger" data-action="delete">
                <i class="fas fa-trash"></i> Delete
            </div>
        `;
        document.body.appendChild(menu);
        this.contextMenu = menu;

        // Click handlers
        menu.addEventListener('click', (e) => {
            const item = e.target.closest('.context-menu-item');
            if (!item) return;

            const action = item.dataset.action;
            this.handleContextMenuAction(action);
            this.hideContextMenu();
        });

        // Hide on outside click
        document.addEventListener('click', () => this.hideContextMenu());
    }

    showContextMenu(event, email) {
        if (!this.contextMenu) return;

        this.contextMenuEmail = email;

        const x = event.clientX;
        const y = event.clientY;

        this.contextMenu.style.left = `${x}px`;
        this.contextMenu.style.top = `${y}px`;
        this.contextMenu.style.display = 'block';

        // Adjust if off-screen
        const rect = this.contextMenu.getBoundingClientRect();
        if (rect.right > window.innerWidth) {
            this.contextMenu.style.left = `${x - rect.width}px`;
        }
        if (rect.bottom > window.innerHeight) {
            this.contextMenu.style.top = `${y - rect.height}px`;
        }
    }

    hideContextMenu() {
        if (this.contextMenu) {
            this.contextMenu.style.display = 'none';
        }
    }

    handleContextMenuAction(action) {
        const email = this.contextMenuEmail;
        if (!email) return;

        switch (action) {
            case 'send-to-prime':
                this.sendEmailToAI(email, 'AI Prime');
                break;
            case 'send-to-agent':
                this.showAgentSelector(email);
                break;
            case 'reply':
                this.replyToEmail(email.id);
                break;
            case 'forward':
                this.forwardEmail(email.id);
                break;
            case 'mark-read':
                this.markAsRead(email.id);
                break;
            case 'mark-unread':
                this.markAsUnread(email.id);
                break;
            case 'delete':
                this.deleteEmail(email.id);
                break;
        }
    }

    showAgentSelector(email) {
        // Show modal to select agent
        const agents = ['AI Prime', 'Data Agent', 'Email Agent', 'Research Agent', 'Writing Agent'];

        const modal = document.createElement('div');
        modal.className = 'agent-selector-modal';
        modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-content">
                <h3>Send Email to Agent</h3>
                <p>Choose an AI agent to analyze this email:</p>
                <div class="agent-list">
                    ${agents.map(agent => `
                        <button class="agent-option" data-agent="${agent}">
                            <i class="fas fa-robot"></i> ${agent}
                        </button>
                    `).join('')}
                </div>
                <button class="btn-cancel" onclick="this.closest('.agent-selector-modal').remove()">Cancel</button>
            </div>
        `;
        document.body.appendChild(modal);

        // Handle agent selection
        modal.querySelectorAll('.agent-option').forEach(btn => {
            btn.addEventListener('click', () => {
                const agentName = btn.dataset.agent;
                this.sendEmailToAI(email, agentName);
                modal.remove();
            });
        });
    }

    async sendEmailToAI(email, agentName = 'AI Prime') {
        console.log(`[Communication Hub] Sending email to ${agentName}:`, email.subject);

        // Fetch full email content first
        try {
            const response = await fetch(`${this.apiBase}/emails/${email.id}`);
            const data = await response.json();

            if (data.success) {
                const fullEmail = data.email;

                // Format message for AI
                const message = `
📧 **Email Analysis Request**

**From:** ${fullEmail.from}
**To:** ${fullEmail.to || 'N/A'}
**Subject:** ${fullEmail.subject}
**Date:** ${new Date(fullEmail.date).toLocaleString()}
**Provider:** ${fullEmail.provider}

**Email Body:**
${fullEmail.body_text || fullEmail.body_html || fullEmail.snippet || 'No content available'}

---

Please analyze this email and provide:
1. Summary of key points
2. Suggested actions
3. Important dates or deadlines
4. Any concerns or flags
                `.trim();

                // Send to AI chat (integrate with existing chat system)
                if (window.aiChat && typeof window.aiChat.addMessageToChat === 'function') {
                    window.aiChat.addMessageToChat(message, agentName);

                    // Show success notification
                    this.showNotification(`Email sent to ${agentName}`, 'success');
                } else {
                    console.error('[Communication Hub] AI Chat system not available');
                    this.showNotification('AI Chat system not available', 'error');
                }
            }
        } catch (error) {
            console.error('[Communication Hub] Failed to send email to AI:', error);
            this.showNotification('Failed to send email to AI', 'error');
        }
    }

    // ==================== SELECTION MODE ====================

    toggleSelectMode() {
        this.selectMode = !this.selectMode;
        const btn = document.querySelector('.btn-select-mode');
        const sendBtn = document.querySelector('.btn-send-selected');

        if (this.selectMode) {
            btn.classList.add('active');
            sendBtn.style.display = 'inline-block';
        } else {
            btn.classList.remove('active');
            sendBtn.style.display = 'none';
            this.selectedEmails.clear();
            this.updateSelectionUI();
        }
    }

    updateSelectionUI() {
        const sendBtn = document.querySelector('.btn-send-selected');
        if (sendBtn) {
            const count = this.selectedEmails.size;
            if (count > 0) {
                sendBtn.innerHTML = `<i class="fas fa-robot"></i> Send ${count} to AI`;
            } else {
                sendBtn.innerHTML = `<i class="fas fa-robot"></i> Send to AI`;
            }
        }
    }

    async sendSelectedToAI() {
        if (this.selectedEmails.size === 0) {
            this.showNotification('No emails selected', 'warning');
            return;
        }

        const selectedEmailData = this.emails.filter(e => this.selectedEmails.has(e.id));

        const message = `
📧 **Batch Email Analysis Request**

**Selected Emails:** ${selectedEmailData.length}

${selectedEmailData.map((email, i) => `
**Email ${i + 1}:**
- **From:** ${email.from}
- **Subject:** ${email.subject}
- **Date:** ${new Date(email.date).toLocaleDateString()}
- **Preview:** ${email.snippet}
`).join('\n')}

Please analyze these emails and provide:
1. Common themes or topics
2. Priority order for responses
3. Suggested actions for each
4. Any important deadlines
        `.trim();

        if (window.aiChat && typeof window.aiChat.addMessageToChat === 'function') {
            window.aiChat.addMessageToChat(message, 'AI Prime');
            this.showNotification(`${selectedEmailData.length} emails sent to AI Prime`, 'success');

            // Clear selection
            this.selectedEmails.clear();
            this.updateSelectionUI();
            this.toggleSelectMode();
        } else {
            this.showNotification('AI Chat system not available', 'error');
        }
    }

    // ==================== EMAIL PREVIEW ====================

    async openEmailPreview(email) {
        const previewPanel = document.getElementById('emailPreview');
        const previewContent = document.getElementById('previewContent');

        if (!previewPanel || !previewContent) return;

        // Fetch full email content
        try {
            const response = await fetch(`${this.apiBase}/emails/${email.id}`);
            const data = await response.json();

            if (data.success) {
                const fullEmail = data.email;

                previewContent.innerHTML = `
                    <div class="email-header">
                        <h3>${fullEmail.subject}</h3>
                        <div class="email-meta">
                            <p><strong>From:</strong> ${fullEmail.from}</p>
                            <p><strong>To:</strong> ${fullEmail.to || 'N/A'}</p>
                            <p><strong>Date:</strong> ${new Date(fullEmail.date).toLocaleString()}</p>
                            <p><strong>Provider:</strong> ${fullEmail.provider}</p>
                        </div>
                    </div>
                    <div class="email-body">
                        ${fullEmail.body_html || fullEmail.body_text || fullEmail.snippet || 'No content available'}
                    </div>
                    <div class="email-actions">
                        <button class="btn-action" onclick="window.communicationHub.sendEmailToAI(${JSON.stringify(fullEmail).replace(/"/g, '&quot;')})">
                            <i class="fas fa-robot"></i> Send to AI
                        </button>
                        <button class="btn-action" onclick="window.communicationHub.replyToEmail('${email.id}')">
                            <i class="fas fa-reply"></i> Reply
                        </button>
                        <button class="btn-action" onclick="window.communicationHub.forwardEmail('${email.id}')">
                            <i class="fas fa-forward"></i> Forward
                        </button>
                        <button class="btn-action btn-danger" onclick="window.communicationHub.deleteEmail('${email.id}')">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                `;

                previewPanel.style.display = 'block';

                // Mark as read
                if (!email.is_read) {
                    this.markAsRead(email.id);
                }
            }
        } catch (error) {
            console.error('[Communication Hub] Failed to load email:', error);
        }
    }

    closePreview() {
        const previewPanel = document.getElementById('emailPreview');
        if (previewPanel) {
            previewPanel.style.display = 'none';
        }
    }

    async markAsRead(emailId) {
        try {
            await fetch(`${this.apiBase}/emails/${emailId}/read`, {
                method: 'POST'
            });

            // Update the email in the local array instead of reloading
            const email = this.emails.find(e => e.id === emailId);
            if (email) {
                email.is_read = true;
                // Update the table if it exists
                if (this.tabulatorTable && this.tableReady) {
                    this.tabulatorTable.updateData([{ id: emailId, is_read: true }]);
                }
            }

            console.log(`[Communication Hub] Marked email ${emailId} as read`);
        } catch (error) {
            console.error('[Communication Hub] Failed to mark as read:', error);
        }
    }

    async markAsUnread(emailId) {
        try {
            await fetch(`${this.apiBase}/emails/${emailId}/unread`, {
                method: 'POST'
            });

            // Update the email in the local array instead of reloading
            const email = this.emails.find(e => e.id === emailId);
            if (email) {
                email.is_read = false;
                // Update the table if it exists
                if (this.tabulatorTable && this.tableReady) {
                    this.tabulatorTable.updateData([{ id: emailId, is_read: false }]);
                }
            }

            console.log(`[Communication Hub] Marked email ${emailId} as unread`);
        } catch (error) {
            console.error('[Communication Hub] Failed to mark as unread:', error);
        }
    }

    // ==================== TAB 2: COMPOSE ====================

    initializeCompose() {
        const container = this.getSubTabContainer('compose');
        if (!container) return;

        container.innerHTML = `
            <div class="compose-email">
                <h3><i class="fas fa-pen"></i> Compose New Email</h3>
                <form id="composeForm">
                    <div class="form-group">
                        <label>From Account:</label>
                        <select id="composeFrom" required>
                            <option value="">Select account...</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>To:</label>
                        <input type="email" id="composeTo" placeholder="recipient@example.com" required />
                    </div>
                    <div class="form-group">
                        <label>Cc:</label>
                        <input type="text" id="composeCc" placeholder="Optional" />
                    </div>
                    <div class="form-group">
                        <label>Subject:</label>
                        <input type="text" id="composeSubject" placeholder="Email subject" required />
                    </div>
                    <div class="form-group">
                        <label>Message:</label>
                        <textarea id="composeBody" rows="15" placeholder="Type your message..."></textarea>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn-primary">
                            <i class="fas fa-paper-plane"></i> Send Email
                        </button>
                        <button type="button" class="btn-secondary" onclick="window.communicationHub.clearCompose()">
                            <i class="fas fa-times"></i> Clear
                        </button>
                    </div>
                </form>
            </div>
        `;

        // Populate "From" dropdown
        const fromSelect = document.getElementById('composeFrom');
        if (fromSelect && this.accounts) {
            this.accounts.forEach(account => {
                const option = document.createElement('option');
                option.value = account.id;
                const icon = account.provider === 'gmail' ? '📧' : '📬';
                option.textContent = `${icon} ${account.email}`;
                fromSelect.appendChild(option);
            });
        }

        // Handle form submission
        const form = document.getElementById('composeForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.sendEmail();
            });
        }
    }

    async sendEmail() {
        const from = document.getElementById('composeFrom').value;
        const to = document.getElementById('composeTo').value;
        const cc = document.getElementById('composeCc').value;
        const subject = document.getElementById('composeSubject').value;
        const body = document.getElementById('composeBody').value;

        try {
            const response = await fetch(`${this.apiBase}/send`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ from, to, cc, subject, body })
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('Email sent successfully!', 'success');
                this.clearCompose();
                this.switchSubTab('unified-inbox');
                this.loadEmails();
            } else {
                this.showNotification(`Failed to send email: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('[Communication Hub] Failed to send email:', error);
            this.showNotification('Network error while sending email', 'error');
        }
    }

    clearCompose() {
        document.getElementById('composeFrom').value = '';
        document.getElementById('composeTo').value = '';
        document.getElementById('composeCc').value = '';
        document.getElementById('composeSubject').value = '';
        document.getElementById('composeBody').value = '';
    }

    replyToEmail(emailId) {
        // Switch to compose tab and pre-fill reply fields
        console.log('[Communication Hub] Reply to:', emailId);
        this.switchSubTab('compose');
        // TODO: Pre-fill compose form with reply data
    }

    forwardEmail(emailId) {
        console.log('[Communication Hub] Forward:', emailId);
        this.switchSubTab('compose');
        // TODO: Pre-fill compose form with forward data
    }

    async deleteEmail(emailId) {
        if (!confirm('Are you sure you want to delete this email?')) return;

        try {
            await fetch(`${this.apiBase}/emails/${emailId}`, {
                method: 'DELETE'
            });
            this.showNotification('Email deleted', 'success');
            this.closePreview();
            this.loadEmails();
        } catch (error) {
            console.error('[Communication Hub] Failed to delete email:', error);
            this.showNotification('Failed to delete email', 'error');
        }
    }

    // ==================== TAB 3: THREADS ====================

    initializeThreads() {
        const container = this.getSubTabContainer('threads');
        if (!container) return;

        container.innerHTML = `
            <div class="email-threads">
                <h3><i class="fas fa-comments"></i> Email Threads</h3>
                <p class="coming-soon">Thread view coming soon... This will group related emails into conversations.</p>
            </div>
        `;
    }

    // ==================== TAB 4: SEARCH ====================

    initializeSearch() {
        const container = this.getSubTabContainer('search');
        if (!container) return;

        container.innerHTML = `
            <div class="email-search">
                <h3><i class="fas fa-search"></i> Search Emails</h3>
                <div class="search-form">
                    <input type="text" id="searchQuery" placeholder="Search by subject, sender, or content..." />
                    <button class="btn-primary" onclick="window.communicationHub.searchEmails()">
                        <i class="fas fa-search"></i> Search
                    </button>
                </div>
                <div id="searchResults" class="search-results"></div>
            </div>
        `;

        // Enter key to search
        const searchInput = document.getElementById('searchQuery');
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.searchEmails();
                }
            });
        }
    }

    async searchEmails() {
        const query = document.getElementById('searchQuery').value.trim();
        if (!query) {
            this.showNotification('Please enter a search query', 'warning');
            return;
        }

        const resultsDiv = document.getElementById('searchResults');
        resultsDiv.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Searching...</div>';

        try {
            const response = await fetch(`${this.apiBase}/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (data.success && data.emails.length > 0) {
                resultsDiv.innerHTML = `
                    <div class="search-count">Found ${data.emails.length} result(s)</div>
                    ${data.emails.map(email => `
                        <div class="search-result" onclick="window.communicationHub.openEmailPreview(${JSON.stringify(email).replace(/"/g, '&quot;')})">
                            <div class="result-header">
                                <strong>${email.subject}</strong>
                                <span class="result-date">${new Date(email.date).toLocaleDateString()}</span>
                            </div>
                            <div class="result-from">${email.from}</div>
                            <div class="result-snippet">${email.snippet || 'No preview available'}</div>
                        </div>
                    `).join('')}
                `;
            } else {
                resultsDiv.innerHTML = '<div class="no-results"><i class="fas fa-inbox"></i> No emails found matching your search.</div>';
            }
        } catch (error) {
            console.error('[Communication Hub] Search failed:', error);
            resultsDiv.innerHTML = '<div class="error-results"><i class="fas fa-exclamation-triangle"></i> Search failed. Please try again.</div>';
        }
    }

    // ==================== TAGGING & EXPORT METHODS ====================

    tagSelectedEmails(color) {
        if (this.selectedEmails.size === 0) {
            this.showNotification('No emails selected', 'warning');
            return;
        }

        this.selectedEmails.forEach(emailId => {
            if (color === 'clear') {
                delete this.emailTags[emailId];
            } else {
                this.emailTags[emailId] = color;
            }
        });

        // Refresh table to show updated tags
        if (this.tabulatorTable) {
            this.tabulatorTable.redraw(true);
        }

        const colorNames = {
            'clear': 'cleared',
            'green': 'green',
            'orange': 'orange',
            'red': 'red'
        };

        this.showNotification(`${this.selectedEmails.size} emails tagged ${colorNames[color]}`, 'success');
        console.log(`[Communication Hub] Tagged ${this.selectedEmails.size} emails with ${color}`);
    }

    exportEmails(format) {
        if (!this.tabulatorTable) {
            this.showNotification('No emails to export', 'warning');
            return;
        }

        const data = this.tabulatorTable.getData();
        if (data.length === 0) {
            this.showNotification('No emails to export', 'warning');
            return;
        }

        const filename = `emails_export_${new Date().toISOString().split('T')[0]}`;

        try {
            if (format === 'excel') {
                this.tabulatorTable.download("xlsx", `${filename}.xlsx`, {
                    sheetName: "Emails"
                });
            } else if (format === 'csv') {
                this.tabulatorTable.download("csv", `${filename}.csv`);
            } else if (format === 'pdf') {
                this.tabulatorTable.download("pdf", `${filename}.pdf`, {
                    orientation: "landscape",
                    title: "Email Export"
                });
            }

            this.showNotification(`Exporting ${data.length} emails as ${format.toUpperCase()}`, 'success');
            console.log(`[Communication Hub] Exported ${data.length} emails as ${format}`);
        } catch (error) {
            console.error('[Communication Hub] Export failed:', error);
            this.showNotification(`Export failed: ${error.message}`, 'error');
        }
    }

    updatePaginationUI() {
        const pageInfo = document.getElementById('page-info');
        const btnFirst = document.getElementById('btn-first-page');
        const btnPrev = document.getElementById('btn-prev-page');
        const btnNext = document.getElementById('btn-next-page');
        const btnLast = document.getElementById('btn-last-page');

        if (!this.tabulatorTable || !pageInfo) return;

        const page = this.tabulatorTable.getPage();
        const pageMax = this.tabulatorTable.getPageMax();

        // Update page info text
        pageInfo.textContent = `Page ${page} of ${pageMax}`;

        // Enable/disable buttons
        if (btnFirst) btnFirst.disabled = (page === 1);
        if (btnPrev) btnPrev.disabled = (page === 1);
        if (btnNext) btnNext.disabled = (page === pageMax);
        if (btnLast) btnLast.disabled = (page === pageMax);

        console.log(`[Communication Hub] Pagination: Page ${page} of ${pageMax}`);
    }

    showCellPopup(e, cell) {
        const value = cell.getValue();
        const field = cell.getField();

        if (!value || value.length < 50) {
            return; // Don't show popup for short content
        }

        // Create popup overlay
        const overlay = document.createElement('div');
        overlay.className = 'cell-popup-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 100000;
        `;

        const popup = document.createElement('div');
        popup.className = 'cell-popup';
        popup.style.cssText = `
            background: var(--bg-card, #1e1e1e);
            border: 1px solid var(--border-default, #444);
            border-radius: 8px;
            padding: 20px;
            max-width: 800px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        `;

        popup.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid var(--border-default, #444); padding-bottom: 10px;">
                <h3 style="margin: 0; color: var(--text-primary, #e5e7eb); font-size: 18px;">
                    ${field.charAt(0).toUpperCase() + field.slice(1)}
                </h3>
                <button class="btn-close" style="background: none; border: none; color: var(--text-secondary, #999); font-size: 24px; cursor: pointer; padding: 0; width: 30px; height: 30px;">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div style="color: var(--text-primary, #e5e7eb); line-height: 1.6; white-space: pre-wrap; word-wrap: break-word;">
                ${value}
            </div>
        `;

        overlay.appendChild(popup);
        document.body.appendChild(overlay);

        // Close popup on overlay click or close button
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay || e.target.closest('.btn-close')) {
                overlay.remove();
            }
        });

        console.log(`[Communication Hub] Cell popup shown for field: ${field}`);
    }

    // ==================== UTILITY METHODS ====================
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;

        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };

        notification.innerHTML = `
            <i class="fas ${icons[type]}"></i>
            <span>${message}</span>
        `;

        document.body.appendChild(notification);

        // Show notification
        setTimeout(() => notification.classList.add('show'), 10);

        // Hide after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    switchSubTab(tabName) {
        // Trigger tab switch via ModuleManager
        const tabButton = document.querySelector(`[data-subtab="${tabName}"]`);
        if (tabButton) {
            tabButton.click();
        }
    }
}

// Module Registry Registration - NEW SIMPLIFIED PATTERN (from inhouse-kanban)
window.ModuleRegistry = window.ModuleRegistry || {};
window.ModuleRegistry['communication-hub'] = {
    instance: null,

    init: async () => {
        console.log('📧 Initializing Communication Hub Module...');
        try {
            const module = new CommunicationHubModule('communication-hub');
            await module.initialize();

            // Store instance in registry
            window.ModuleRegistry['communication-hub'].instance = module;

            // ALSO expose a global shortcut for inline onclick handlers and debugging
            // Many templates use `window.communicationHub.*` in onclick attributes — ensure it's defined
            try {
                window.communicationHub = module;
                // Helpful aliases
                window.communicationHub.sendEmail = (data) => module.sendEmail(data);
                window.communicationHub.loadEmails = () => module.loadEmails();
                window.communicationHub.refreshInbox = () => module.loadEmails();
            } catch (e) {
                console.warn('[Communication Hub] Failed to expose global communicationHub:', e);
            }

            // Expose methods for easy access
            window.ModuleRegistry['communication-hub'].sendEmail = (data) => module.sendEmail(data);
            window.ModuleRegistry['communication-hub'].loadEmails = () => module.loadEmails();
            window.ModuleRegistry['communication-hub'].refreshInbox = () => module.loadEmails();

            console.log('✅ Communication Hub Module initialized successfully');
            return module;
        } catch (error) {
            console.error('❌ Failed to initialize Communication Hub Module:', error);
            throw error;
        }
    }
};

console.log('📦 Communication Hub Module script loaded');

// ==================== DEBUG COMMAND ====================
// Run in browser console: debugCommunicationHub()
window.debugCommunicationHub = function () {
    console.log('🔍 ========== COMMUNICATION HUB DEBUG ==========');

    // 1. Check if module is registered
    console.log('\n📋 MODULE REGISTRY CHECK:');
    if (window.ModuleRegistry && window.ModuleRegistry['communication-hub']) {
        console.log('✅ Module registered in window.ModuleRegistry');
        console.log('   Instance:', window.ModuleRegistry['communication-hub'].instance);
        console.log('   Has init():', typeof window.ModuleRegistry['communication-hub'].init === 'function');
    } else {
        console.error('❌ Module NOT registered in window.ModuleRegistry');
        return;
    }

    // 2. Check DOM containers
    console.log('\n📦 DOM CONTAINER CHECK:');
    const commTab = document.getElementById('tab-communication');
    const commHubTab = document.getElementById('tab-communication-hub');
    console.log('   #tab-communication:', commTab ? '✅ EXISTS' : '❌ MISSING');
    console.log('   #tab-communication-hub:', commHubTab ? '✅ EXISTS' : '❌ MISSING');

    const container = commTab || commHubTab;
    if (container) {
        console.log('   Container innerHTML length:', container.innerHTML.length);
        console.log('   Has .module-header:', !!container.querySelector('.module-header'));
        console.log('   Has .module-subtabs-nav:', !!container.querySelector('.module-subtabs-nav'));
        console.log('   Sub-tab buttons found:', container.querySelectorAll('.module-subtab-btn').length);
        console.log('   Sub-tab content areas:', container.querySelectorAll('.module-subtab-content').length);
    }

    // 3. Check sidebar button
    console.log('\n🔘 SIDEBAR BUTTON CHECK:');
    const sidebarBtn = document.querySelector('[data-tab="communication"]');
    console.log('   Button exists:', sidebarBtn ? '✅ YES' : '❌ NO');
    if (sidebarBtn) {
        const computed = window.getComputedStyle(sidebarBtn);
        console.log('   Display:', computed.display);
        console.log('   Visibility:', computed.visibility);
        console.log('   Opacity:', computed.opacity);
        console.log('   Is active:', sidebarBtn.classList.contains('active'));
    }

    // 4. Check module loader
    console.log('\n🔧 MODULE LOADER CHECK:');
    if (window.moduleLoader) {
        console.log('✅ ModuleLoader exists');
        console.log('   Loaded modules:', Array.from(window.moduleLoader.loadedModules || []));
        const commModule = window.moduleLoader.modules?.get('communication-hub');
        if (commModule) {
            console.log('   Module manifest:', commModule);
            console.log('   Module available:', commModule.available);
            console.log('   Main tab:', commModule.main_tab);
            console.log('   Main tab ID:', commModule.main_tab_id);
        } else {
            console.warn('⚠️ Module not in moduleLoader.modules');
        }
    } else {
        console.error('❌ window.moduleLoader not found');
    }

    // 5. Check manifest
    console.log('\n📄 MANIFEST CHECK:');
    const instance = window.ModuleRegistry['communication-hub']?.instance;
    if (instance) {
        console.log('   Module ID:', instance.moduleId);
        console.log('   Manifest loaded:', !!instance.manifest);
        if (instance.manifest) {
            console.log('   Manifest tabs:', instance.manifest.tabs?.length || 0);
            console.log('   Tabs:', instance.manifest.tabs?.map(t => t.id).join(', '));
        }
        console.log('   Container property:', instance.container ? `#${instance.container.id}` : 'NOT SET');
    }

    // 6. Try to force initialization
    console.log('\n🚀 FORCE INITIALIZATION:');
    try {
        if (!window.ModuleRegistry['communication-hub'].instance) {
            console.log('⚡ Calling init()...');
            window.ModuleRegistry['communication-hub'].init().then(() => {
                console.log('✅ Init completed');
                console.log('   Instance now exists:', !!window.ModuleRegistry['communication-hub'].instance);
            }).catch(err => {
                console.error('❌ Init failed:', err);
            });
        } else {
            console.log('✅ Already initialized');
            // Try to show the tab
            if (typeof switchTab === 'function') {
                console.log('⚡ Attempting switchTab("communication")...');
                switchTab('communication');
            }
        }
    } catch (error) {
        console.error('❌ Force init error:', error);
    }

    console.log('\n🔍 ========== DEBUG COMPLETE ==========');
    console.log('💡 TIP: If module is registered but not visible, try: switchTab("communication")');
    console.log('💡 TIP: To reinitialize, run: window.ModuleRegistry["communication-hub"].init()');
};

console.log('💡 Debug command loaded! Run: debugCommunicationHub()');
