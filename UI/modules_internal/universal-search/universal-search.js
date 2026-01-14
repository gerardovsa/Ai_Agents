/**
 * Universal Search Module - Modern Framework (V4.0)
 * 
 * FILE: UI/modules_internal/universal-search/universal-search-modern.js
 * PURPOSE: Search across all connected platforms in one unified interface
 * PATTERN: Composition-based (no inheritance)
 * 
 * FEATURES:
 * - Single search box for all platforms
 * - Multi-platform results (documents, threads, Gmail, Slack, Synergy)
 * - Real-time search with debouncing
 * - Faceted filters
 * - Result grouping by source
 * 
 * LAST MODIFIED: 2025-11-30
 */

window.UniversalSearchModule = {
    // ==================== STATE ====================
    state: {
        query: '',
        results: [],
        loading: false,
        error: null,
        selectedSources: new Set(['documents', 'threads', 'messages', 'synergy', 'vector-database']),
        availableSources: {
            'documents': true,
            'threads': true,
            'messages': true,
            'vector-database': true,
            'synergy': true,
            'automations': true,
            'gmail': false,
            'outlook': false,
            'slack': false,
            'google-drive': false,
            'onedrive': false,
            'sharepoint': false,
            'xero': false,
            'inhouseprint': true
        },
        searchTimeout: null,
        stats: {
            total: 0,
            bySource: {}
        }
    },

    // ==================== LIFECYCLE: LOAD ====================

    /**
     * Called once when module first loads
     * @param {Object} utilities - Injected utilities { dom, api, storage, events, log }
     */
    async onLoad(utilities) {
        Object.assign(this, utilities);
        this.log.info('Universal Search module loading...');

        // Register in global registry for backward compatibility
        if (!window.ModuleRegistry) window.ModuleRegistry = {};
        window.ModuleRegistry['universal-search'] = this;

        // Load available sources
        await this.loadAvailableSources();

        this.log.info('Universal Search module loaded successfully');
    },

    // ==================== LIFECYCLE: DASHBOARD ====================

    /**
     * Called when dashboard tab is activated
     * @param {Object} utilities - Injected utilities { dom, api, storage, events, log }
     */
    async onDashboardLoad(utilities) {
        Object.assign(this, utilities);
        this.log.info('Universal Search dashboard loading...');

        // Get dashboard container
        this.container = this.dom.getContainer();

        // Render full dashboard UI
        this.renderDashboard();

        // Setup event listeners (tracked automatically)
        this.setupEventListeners();

        // Re-check available sources on load
        await this.loadAvailableSources();

        // Re-render checkboxes with updated status
        const sourcesContainer = this.container.querySelector('.source-categories');
        if (sourcesContainer) {
            sourcesContainer.innerHTML = this.renderSourceCheckboxes();
            // Re-attach checkbox listeners
            const checkboxes = this.container.querySelectorAll('input[data-source]');
            checkboxes.forEach(checkbox => {
                this.dom.on(checkbox, 'change', (e) => {
                    const source = e.target.dataset.source;
                    if (e.target.checked) {
                        this.state.selectedSources.add(source);
                    } else {
                        this.state.selectedSources.delete(source);
                    }
                    this.savePreferences();
                    this.log.info('Selected sources:', Array.from(this.state.selectedSources));
                });
            });
        }

        this.log.info('Universal Search dashboard loaded successfully');
    },

    // ==================== LIFECYCLE: SIDEBAR ====================

    /**
     * Called when sidebar loads
     * @param {Object} utilities - Injected utilities { dom, api, storage, events, log }
     */
    async onSidebarLoad(utilities) {
        Object.assign(this, utilities);
        this.log.info('Universal Search sidebar loading...');

        // Get sidebar container
        this.container = this.dom.getContainer();

        // Render compact sidebar UI
        this.renderSidebar();

        // Setup event listeners
        this.setupEventListeners();

        // Load saved preferences
        this.loadPreferences();

        // Show empty state
        this.showEmptyState();

        this.log.info('Universal Search sidebar loaded successfully');
    },

    /**
     * Called when module unloads
     * @param {Object} utilities - Injected utilities
     */
    onUnload(utilities) {
        Object.assign(this, utilities);
        this.log.info('Universal Search unloading...');

        // Save preferences
        this.savePreferences();

        // Clear search timeout
        if (this.state.searchTimeout) {
            clearTimeout(this.state.searchTimeout);
        }

        // Framework handles event cleanup automatically
        this.log.info('Universal Search unloaded');
    },

    // ==================== DATA LOADING ====================

    /**
     * Load available search sources - auto-detect authenticated services
     */
    async loadAvailableSources() {
        try {
            // Auto-detect authenticated services
            const userId = window.UserAuth?.user?.id || 1;

            // Check Gmail authentication
            let gmailConnected = false;
            try {
                const gmailAuth = await this.api.get('/api/auth/google/status');
                gmailConnected = gmailAuth.connected === true;
                this.log.info('Gmail auth status:', gmailAuth);
            } catch (e) {
                this.log.warn('Failed to check Gmail auth:', e);
            }

            // Check Outlook authentication
            let outlookConnected = false;
            try {
                const outlookAuth = await this.api.get('/api/auth/microsoft/status');
                outlookConnected = outlookAuth.connected === true;
                this.log.info('Outlook auth status:', outlookAuth);
            } catch (e) {
                this.log.warn('Failed to check Outlook auth:', e);
            }

            // Check Xero authentication
            let xeroConnected = false;
            try {
                const xeroAuth = await this.api.get('/api/xero/status');
                xeroConnected = xeroAuth.connected === true || xeroAuth.authenticated === true;
                this.log.info('Xero auth status:', xeroAuth);
            } catch (e) {
                this.log.warn('Failed to check Xero auth:', e);
            }

            this.state.availableSources = {
                // Internal sources (always available)
                'documents': true,
                'threads': true,
                'messages': true,
                'vector-database': true,
                'synergy': true,
                'automations': true,

                // External integrations (check authentication)
                'gmail': gmailConnected,
                'outlook': outlookConnected,
                'slack': false, // TODO: Add Slack auth check
                'google-drive': gmailConnected, // Uses same OAuth
                'onedrive': outlookConnected, // Uses same OAuth
                'sharepoint': outlookConnected, // Uses same OAuth
                'xero': xeroConnected,
                'inhouseprint': true // Internal database
            };

            // Auto-select connected sources
            if (gmailConnected) {
                this.state.selectedSources.add('gmail');
                this.state.selectedSources.add('google-drive');
            }
            if (outlookConnected) {
                this.state.selectedSources.add('outlook');
                this.state.selectedSources.add('onedrive');
                this.state.selectedSources.add('sharepoint');
            }
            if (xeroConnected) {
                this.state.selectedSources.add('xero');
            }

            this.log.info('Available sources:', this.state.availableSources);
            this.log.info('Auto-selected sources:', Array.from(this.state.selectedSources));
        } catch (error) {
            this.log.warn('Failed to load sources, using defaults:', error);
            // Fallback to internal sources only
            this.state.availableSources = {
                'documents': true,
                'threads': true,
                'messages': true,
                'vector-database': true,
                'synergy': true,
                'automations': true,
                'gmail': false,
                'outlook': false,
                'slack': false,
                'google-drive': false,
                'onedrive': false,
                'sharepoint': false,
                'xero': false,
                'inhouseprint': true
            };
        }
    },

    /**
     * Perform search
     */
    async search() {
        const query = this.state.query.trim();

        if (!query || query.length < 2) {
            this.showEmptyState();
            return;
        }

        try {
            this.state.loading = true;
            this.state.error = null;
            this.showLoadingState();

            const params = {
                query: query,
                sources: Array.from(this.state.selectedSources),
                limit: 50
            };

            this.log.info('Searching:', params);

            const response = await this.api.get('/api/universal-search/search', { params });

            // Backend returns: {success, query, search_type, total_results, sources: {...}}
            if (!response.success) {
                throw new Error(response.error || 'Search failed');
            }

            // Convert backend format to frontend format
            this.state.results = this.flattenResults(response.sources || {});
            this.state.stats = {
                total: response.total_results || 0,
                bySource: this.getSourceStats(response.sources || {})
            };

            this.log.info(`Found ${this.state.stats.total} results across ${Object.keys(response.sources || {}).length} sources`);

            // Show results
            if (this.state.results.length > 0) {
                this.showResults();
            } else {
                this.showNoResults();
            }

        } catch (error) {
            this.log.error('Search failed:', error);
            this.state.error = error.message;
            this.showError();
        } finally {
            this.state.loading = false;
        }
    },

    /**
     * Convert backend sources object to flat results array
     */
    flattenResults(sources) {
        const results = [];

        for (const [sourceName, sourceData] of Object.entries(sources)) {
            if (sourceData.error) {
                this.log.warn(`Source ${sourceName} returned error:`, sourceData.error);
                continue;
            }

            const items = sourceData.results || [];
            items.forEach(item => {
                results.push({
                    ...item,
                    source: sourceName
                });
            });
        }

        return results;
    },

    /**
     * Get stats per source from backend response
     */
    getSourceStats(sources) {
        const stats = {};

        for (const [sourceName, sourceData] of Object.entries(sources)) {
            if (!sourceData.error) {
                stats[sourceName] = sourceData.count || (sourceData.results || []).length;
            }
        }

        return stats;
    },

    // ==================== UI RENDERING ====================

    /**
     * Render full dashboard UI (tab content)
     */
    renderDashboard() {
        if (!this.container) {
            this.log.warn('Container not found for dashboard');
            return;
        }

        this.container.innerHTML = `
            <div class="module-dashboard">
                <!-- Search Bar Card -->
                <div class="dashboard-card">
                    <div class="card-header">
                        <h3 class="card-title">
                            <i class="fas fa-search"></i> Search Query
                        </h3>
                    </div>
                    <div class="card-content" style="padding: var(--space-4);">
                        <div class="search-input-wrapper" style="display: flex; gap: var(--space-2); align-items: center;">
                            <input 
                                type="text" 
                                id="universal-search-input" 
                                class="search-input"
                                placeholder="Search documents, messages, threads, Synergy sessions, automations, Gmail, Slack..."
                                autocomplete="off"
                                style="flex: 1; padding: 12px 16px; background: var(--bg-secondary); border: 1px solid var(--border-default); border-radius: 6px; color: var(--text-primary); font-size: 14px;"
                            />
                            <button id="universal-search-btn" style="padding: 12px 24px; background: var(--accent-primary); border: none; border-radius: 6px; cursor: pointer; color: white; font-weight: 600; font-size: 14px; transition: opacity 0.2s;" onmouseover="this.style.opacity='0.8'" onmouseout="this.style.opacity='1'">
                                <i class="fas fa-search"></i> Search
                            </button>
                            <button class="search-clear-btn" id="search-clear" style="visibility: hidden; padding: 8px 16px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 6px; cursor: pointer;">
                                <i class="fas fa-times"></i> Clear
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- Filters & Options Card -->
                <div class="dashboard-card">
                    <div class="card-header">
                        <h3 class="card-title">
                            <i class="fas fa-filter"></i> Search Options
                        </h3>
                    </div>
                    <div class="card-content" style="padding: var(--space-4);">
                        <div class="universal-search-filters" style="display: flex; gap: var(--space-4); flex-wrap: wrap;">
                            <div class="filter-group" style="flex: 1; min-width: 200px;">
                                <label style="display: block; margin-bottom: var(--space-2); color: var(--text-secondary); font-size: 13px;">Search Type:</label>
                                <select id="search-type" class="filter-select" style="width: 100%; padding: 8px 12px; background: var(--bg-secondary); border: 1px solid var(--border-default); border-radius: 6px; color: var(--text-primary);">
                                    <option value="hybrid">Hybrid (Best Results)</option>
                                    <option value="semantic">Semantic (AI-Powered)</option>
                                    <option value="fulltext">Full-Text (Exact Match)</option>
                                </select>
                            </div>
                            
                            <div class="filter-group" style="flex: 2; min-width: 300px;">
                                <label style="display: block; margin-bottom: var(--space-2); color: var(--text-secondary); font-size: 13px;">Sources:</label>
                                <div class="source-checkboxes" style="display: flex; gap: var(--space-3); flex-wrap: wrap;">
                                    ${this.renderSourceCheckboxes()}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Search States & Results Card -->
                <div class="dashboard-card">
                    <div class="card-header">
                        <h3 class="card-title">
                            <i class="fas fa-list"></i> Search Results
                        </h3>
                    </div>
                    <div class="card-content">
                        <!-- Empty State -->
                        <div id="universal-search-empty" class="search-state empty-state" style="text-align: center; padding: 60px 20px;">
                            <i class="fas fa-search empty-icon" style="font-size: 48px; color: var(--text-tertiary); margin-bottom: var(--space-3);"></i>
                            <h3 style="margin-bottom: var(--space-2); color: var(--text-primary);">Start Searching</h3>
                            <p style="color: var(--text-secondary);">Enter a query to search across all your connected platforms</p>
                        </div>
                        
                        <!-- Loading State -->
                        <div id="universal-search-loading" class="search-state loading-state" style="display: none; text-align: center; padding: 60px 20px;">
                            <i class="fas fa-spinner fa-spin loading-icon" style="font-size: 48px; color: var(--accent-primary); margin-bottom: var(--space-3);"></i>
                            <h3 style="margin-bottom: var(--space-2); color: var(--text-primary);">Searching...</h3>
                            <p style="color: var(--text-secondary);">Searching across your platforms</p>
                        </div>
                        
                        <!-- No Results State -->
                        <div id="universal-search-no-results" class="search-state no-results-state" style="display: none; text-align: center; padding: 60px 20px;">
                            <i class="fas fa-inbox empty-icon" style="font-size: 48px; color: var(--text-tertiary); margin-bottom: var(--space-3);"></i>
                            <h3 style="margin-bottom: var(--space-2); color: var(--text-primary);">No Results Found</h3>
                            <p style="color: var(--text-secondary);">Try different keywords or search across more platforms</p>
                        </div>
                        
                        <!-- Results Container -->
                        <div id="universal-search-results" class="search-results-container" style="display: none;">
                            <!-- Results will be rendered here -->
                        </div>
                    </div>
                </div>
            </div>
            </div>
        `;
    },

    /**
     * Render compact sidebar UI
     */
    renderSidebar() {
        if (!this.container) {
            this.log.warn('Container not found for sidebar');
            return;
        }

        this.container.innerHTML = `
            <div class="universal-search-sidebar">
                <!-- Compact Header -->
                <div class="sidebar-header">
                    <h3><i class="fas fa-search"></i> Quick Search</h3>
                </div>
                
                <!-- Compact Search Bar -->
                <div class="sidebar-search-bar">
                    <input 
                        type="text" 
                        id="universal-search-input" 
                        class="sidebar-search-input"
                        placeholder="Search everything..."
                        autocomplete="off"
                    />
                </div>
                
                <!-- Compact Filters -->
                <div class="sidebar-filters">
                    ${this.renderSourceCheckboxes()}
                </div>
                
                <!-- Search States -->
                <div id="universal-search-empty" class="sidebar-state empty-state">
                    <i class="fas fa-search"></i>
                    <p>Start typing to search</p>
                </div>
                
                <div id="universal-search-loading" class="sidebar-state loading-state" style="display: none;">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>Searching...</p>
                </div>
                
                <div id="universal-search-no-results" class="sidebar-state no-results-state" style="display: none;">
                    <i class="fas fa-inbox"></i>
                    <p>No results</p>
                </div>
                
                <!-- Results Container -->
                <div id="universal-search-results" class="sidebar-results" style="display: none;">
                    <!-- Results will be rendered here -->
                </div>
            </div>
        `;
    },

    /**
     * Render source checkboxes
     */
    renderSourceCheckboxes() {
        const categories = [
            {
                name: 'Internal Sources',
                sources: [
                    { id: 'documents', label: 'Documents', icon: 'fa-file-alt' },
                    { id: 'vector-database', label: 'Vector Database (AI Search)', icon: 'fa-database' },
                    { id: 'threads', label: 'Threads', icon: 'fa-comments' },
                    { id: 'messages', label: 'Messages', icon: 'fa-envelope' }
                ]
            },
            {
                name: 'AI & Automation',
                sources: [
                    { id: 'synergy', label: 'Synergy Sessions', icon: 'fa-users' },
                    { id: 'automations', label: 'Automations', icon: 'fa-robot' }
                ]
            },
            {
                name: 'Email & Communication',
                sources: [
                    { id: 'gmail', label: 'Gmail', icon: 'fa-google' },
                    { id: 'outlook', label: 'Outlook', icon: 'fa-envelope-open' },
                    { id: 'slack', label: 'Slack', icon: 'fa-slack' }
                ]
            },
            {
                name: 'Cloud Storage',
                sources: [
                    { id: 'google-drive', label: 'Google Drive', icon: 'fa-google-drive' },
                    { id: 'onedrive', label: 'OneDrive', icon: 'fa-cloud' },
                    { id: 'sharepoint', label: 'SharePoint', icon: 'fa-share-alt' }
                ]
            },
            {
                name: 'Business Systems',
                sources: [
                    { id: 'xero', label: 'Xero Accounting', icon: 'fa-file-invoice' },
                    { id: 'inhouseprint', label: 'InHousePrint Projects', icon: 'fa-print' }
                ]
            }
        ];

        let html = '<div class="source-categories" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: var(--space-4); width: 100%;">';

        for (const category of categories) {
            html += `
                <div class="source-category" style="background: transparent; padding: var(--space-3); border-radius: 8px; border: 1px solid var(--border-default);">
                    <h4 style="margin: 0 0 var(--space-2) 0; font-size: 12px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px;">${category.name}</h4>
                    <div class="category-sources" style="display: flex; flex-direction: column; gap: var(--space-2);">
            `;

            for (const source of category.sources) {
                const available = this.state.availableSources[source.id];
                const checked = this.state.selectedSources.has(source.id);
                const disabled = !available;
                const statusColor = available ? '#10b981' : '#ef4444';
                const statusText = available ? '● Connected' : '● Not Connected';
                const borderColor = available ? 'rgba(16, 185, 129, 0.3)' : 'var(--border-default)';
                const bgHover = available ? 'rgba(16, 185, 129, 0.1)' : 'var(--bg-tertiary)';

                html += `
                    <label class="source-checkbox ${disabled ? 'disabled' : ''}" style="display: flex; align-items: center; gap: var(--space-2); padding: 10px 12px; border-radius: 6px; border: 1px solid ${borderColor}; cursor: ${disabled ? 'not-allowed' : 'pointer'}; transition: all 0.2s; ${disabled ? 'opacity: 0.5;' : ''}" onmouseover="if(!this.classList.contains('disabled')) { this.style.background='${bgHover}'; this.style.borderColor='${available ? '#10b981' : 'var(--border-default)'}'; }" onmouseout="this.style.background='transparent'; this.style.borderColor='${borderColor}';">
                        <input 
                            type="checkbox" 
                            value="${source.id}" 
                            ${checked ? 'checked' : ''}
                            ${disabled ? 'disabled' : ''}
                            data-source="${source.id}"
                            class="source-checkbox-input"
                            style="cursor: ${disabled ? 'not-allowed' : 'pointer'}; accent-color: #10b981;"
                        />
                        <i class="fas ${source.icon}" style="width: 16px; color: ${available ? '#10b981' : 'var(--text-secondary)'};"></i>
                        <span style="flex: 1; font-size: 13px; color: var(--text-primary); font-weight: ${available ? '500' : '400'};">${source.label}</span>
                        <span style="font-size: 11px; color: ${statusColor}; font-weight: 600; letter-spacing: 0.3px;">${statusText}</span>
                    </label>
                `;
            }

            html += `
                    </div>
                </div>
            `;
        }

        html += '</div>';
        return html;
    },

    showEmptyState() {
        const empty = this.container.querySelector('#universal-search-empty');
        const loading = this.container.querySelector('#universal-search-loading');
        const results = this.container.querySelector('#universal-search-results');
        const noResults = this.container.querySelector('#universal-search-no-results');

        if (empty) empty.style.display = 'flex';
        if (loading) loading.style.display = 'none';
        if (results) results.style.display = 'none';
        if (noResults) noResults.style.display = 'none';
    },

    showLoadingState() {
        const empty = this.container.querySelector('#universal-search-empty');
        const loading = this.container.querySelector('#universal-search-loading');
        const results = this.container.querySelector('#universal-search-results');
        const noResults = this.container.querySelector('#universal-search-no-results');

        if (empty) empty.style.display = 'none';
        if (loading) loading.style.display = 'flex';
        if (results) results.style.display = 'none';
        if (noResults) noResults.style.display = 'none';
    },

    showResults() {
        const empty = this.container.querySelector('#universal-search-empty');
        const loading = this.container.querySelector('#universal-search-loading');
        const results = this.container.querySelector('#universal-search-results');
        const noResults = this.container.querySelector('#universal-search-no-results');

        if (empty) empty.style.display = 'none';
        if (loading) loading.style.display = 'none';
        if (results) {
            results.style.display = 'block';
            results.innerHTML = this.renderResults();
        }
        if (noResults) noResults.style.display = 'none';
    },

    showNoResults() {
        const empty = this.container.querySelector('#universal-search-empty');
        const loading = this.container.querySelector('#universal-search-loading');
        const results = this.container.querySelector('#universal-search-results');
        const noResults = this.container.querySelector('#universal-search-no-results');

        if (empty) empty.style.display = 'none';
        if (loading) loading.style.display = 'none';
        if (results) results.style.display = 'none';
        if (noResults) noResults.style.display = 'flex';
    },

    showError() {
        const resultsContainer = this.container.querySelector('#universal-search-results');
        if (resultsContainer) {
            resultsContainer.style.display = 'block';
            resultsContainer.innerHTML = `
                <div class="universal-search-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Search Error</h3>
                    <p>${this.escapeHtml(this.state.error)}</p>
                </div>
            `;
        }
    },

    renderResults() {
        const grouped = this.groupResultsBySource();

        let html = `<div class="universal-search-results-wrapper">`;

        // Stats header
        html += `
            <div class="universal-search-results-header">
                <h3>Found ${this.state.stats.total} results</h3>
                <p>Searched across ${this.state.selectedSources.size} sources</p>
            </div>
        `;

        // Group results by source
        for (const [source, items] of Object.entries(grouped)) {
            if (items.length === 0) continue;

            html += `
                <div class="universal-search-source-group">
                    <h4 class="universal-search-source-title">
                        <i class="${this.getSourceIcon(source)}"></i>
                        ${this.getSourceLabel(source)} (${items.length})
                    </h4>
                    <div class="universal-search-items">
                        ${items.map(item => this.renderResultItem(item)).join('')}
                    </div>
                </div>
            `;
        }

        html += `</div>`;
        return html;
    },

    renderResultItem(item) {
        const hasLink = item.link || item.webLink || item.webUrl || item.webViewLink || item.url;
        const isClickable = true; // All results are now clickable
        
        return `
            <div class="universal-search-item" data-id="${item.id}" data-source="${item.source}" style="cursor: pointer; padding: 16px; border: 1px solid var(--border-default); border-radius: 8px; background: var(--bg-secondary); transition: all 0.2s; margin-bottom: 12px;" onmouseover="this.style.background='var(--bg-tertiary)'; this.style.borderColor='var(--accent-primary)'; this.style.transform='translateX(4px)';" onmouseout="this.style.background='var(--bg-secondary)'; this.style.borderColor='var(--border-default)'; this.style.transform='translateX(0)';">
                <div class="universal-search-item-header" style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                    <h5 class="universal-search-item-title" style="margin: 0; font-size: 14px; font-weight: 600; color: var(--text-primary); flex: 1;">${this.escapeHtml(item.title || 'Untitled')}</h5>
                    <span class="universal-search-item-source" style="font-size: 11px; padding: 4px 8px; background: var(--accent-primary); color: white; border-radius: 4px; margin-left: 12px; white-space: nowrap;">${this.getSourceLabel(item.source)}</span>
                </div>
                ${item.snippet || item.preview || item.bodyPreview ? `
                    <p class="universal-search-item-snippet" style="margin: 8px 0; font-size: 13px; color: var(--text-secondary); line-height: 1.5;">${this.escapeHtml((item.snippet || item.preview || item.bodyPreview || '').substring(0, 200))}${(item.snippet || item.preview || item.bodyPreview || '').length > 200 ? '...' : ''}</p>
                ` : ''}
                <div class="universal-search-item-footer" style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px; font-size: 12px; color: var(--text-secondary);">
                    <span class="universal-search-item-date">
                        <i class="fas fa-clock" style="margin-right: 4px;"></i>
                        ${this.formatDate(item.date || item.created_at || item.createdDateTime || item.receivedDateTime || item.modified || item.timestamp)}
                    </span>
                    <div style="display: flex; gap: 12px; align-items: center;">
                        ${item.type ? `<span style="font-size: 11px; color: var(--text-secondary);"><i class="fas fa-tag" style="margin-right: 4px;"></i>${item.type}</span>` : ''}
                        ${item.agent_count ? `<span style="font-size: 11px; color: var(--text-secondary);"><i class="fas fa-users" style="margin-right: 4px;"></i>${item.agent_count} agents</span>` : ''}
                        ${item.score ? `<span class="universal-search-item-score" style="font-size: 11px; color: var(--accent-primary); font-weight: 600;">Relevance: ${Math.round(item.score * 100)}%</span>` : ''}
                        <span style="color: var(--accent-primary); font-size: 11px; font-weight: 600;">
                            <i class="fas fa-arrow-right" style="margin-left: 4px;"></i>
                        </span>
                    </div>
                </div>
            </div>
        `;
    },

    // ==================== EVENT HANDLING ====================

    setupEventListeners() {
        // Search input
        const searchInput = this.container.querySelector('#universal-search-input');
        if (searchInput) {
            this.dom.on(searchInput, 'input', (e) => {
                this.state.query = e.target.value;
                const clearBtn = this.container.querySelector('#search-clear');
                if (clearBtn) {
                    clearBtn.style.visibility = this.state.query ? 'visible' : 'hidden';
                }
            });

            // Enter key triggers search
            this.dom.on(searchInput, 'keypress', (e) => {
                if (e.key === 'Enter') {
                    this.search();
                }
            });
        }

        // Search button
        const searchBtn = this.container.querySelector('#universal-search-btn');
        if (searchBtn) {
            this.dom.on(searchBtn, 'click', () => {
                this.search();
            });
        }

        // Clear button
        const clearBtn = this.container.querySelector('#search-clear');
        if (clearBtn) {
            this.dom.on(clearBtn, 'click', () => {
                const input = this.container.querySelector('#universal-search-input');
                if (input) {
                    input.value = '';
                    this.state.query = '';
                }
                clearBtn.style.visibility = 'hidden';
                this.showEmptyState();
            });
        }

        // Refresh button
        this.dom.on(this.container, 'click', '[data-action="refresh"]', () => {
            if (this.state.query) {
                this.search();
            }
        });

        // Close button
        this.dom.on(this.container, 'click', '[data-action="close"]', () => {
            this.events.emit('sidebar-close');
        });

        // Source checkboxes
        const checkboxes = this.container.querySelectorAll('input[data-source]');
        checkboxes.forEach(checkbox => {
            this.dom.on(checkbox, 'change', (e) => {
                const source = e.target.dataset.source;
                if (e.target.checked) {
                    this.state.selectedSources.add(source);
                } else {
                    this.state.selectedSources.delete(source);
                }
                this.savePreferences();
                this.log.info('Selected sources:', Array.from(this.state.selectedSources));
            });
        });

        // Result item clicks
        this.dom.on(this.container, 'click', '.universal-search-item', (e) => {
            const item = e.currentTarget;
            const id = item.dataset.id;
            const source = item.dataset.source;

            this.openResult(id, source);
        });
    },

    // ==================== ACTIONS ====================

    openResult(id, source) {
        this.log.info('Opening result:', { id, source });

        // Route to appropriate handler based on source
        switch (source) {
            case 'documents':
                // Open document in document viewer/preview
                if (window.DocumentService) {
                    window.DocumentService.openDocument(id);
                } else if (window.switchTab) {
                    window.switchTab('documents');
                }
                break;

            case 'threads':
                // Threads are displayed in HOME tab (main dashboard with agent columns)
                // Load thread into Prime AI or agent column
                if (window.switchTab) {
                    window.switchTab('home');
                    setTimeout(() => {
                        // Load thread into Prime AI column
                        if (window.ThreadManager && window.ThreadManager.loadThreadIntoPrime) {
                            window.ThreadManager.loadThreadIntoPrime(id);
                        } else if (window.loadThread) {
                            window.loadThread(id);
                        } else {
                            this.log.warn('Thread loading function not available');
                        }
                    }, 300);
                }
                break;

            case 'messages':
                // Messages are also in HOME tab (within threads)
                if (window.switchTab) {
                    window.switchTab('home');
                    // Messages belong to threads, so we'd need the thread_id
                    const messageResult = this.state.results.find(r => r.id === id);
                    if (messageResult?.thread_id) {
                        setTimeout(() => {
                            if (window.ThreadManager && window.ThreadManager.loadThreadIntoPrime) {
                                window.ThreadManager.loadThreadIntoPrime(messageResult.thread_id);
                            }
                        }, 300);
                    }
                }
                break;

            case 'synergy':
                // Open Synergy session or document
                const sessionId = this.state.results.find(r => r.id === id)?.session_id || id;
                const docId = this.state.results.find(r => r.id === id)?.doc_id;
                
                if (window.switchTab) {
                    window.switchTab('synergy');
                    setTimeout(() => {
                        if (docId) {
                            // Open specific document within session
                            window.location.hash = `#/synergy/${sessionId}/doc/${docId}`;
                        } else {
                            // Open session
                            window.location.hash = `#/synergy/${sessionId}`;
                        }
                    }, 300);
                }
                break;

            case 'gmail':
            case 'outlook':
                // Open email in new tab (webmail)
                const result = this.state.results.find(r => r.id === id);
                if (result?.link || result?.webLink) {
                    window.open(result.link || result.webLink, '_blank');
                } else {
                    this.log.warn('No link available for email:', id);
                }
                break;

            case 'google-drive':
            case 'onedrive':
            case 'sharepoint':
                // Open cloud file in new tab
                const cloudResult = this.state.results.find(r => r.id === id);
                if (cloudResult?.link || cloudResult?.webUrl || cloudResult?.webViewLink) {
                    window.open(cloudResult.link || cloudResult.webUrl || cloudResult.webViewLink, '_blank');
                } else {
                    this.log.warn('No link available for cloud file:', id);
                }
                break;

            case 'xero':
                // Open Xero invoice/contact in new tab
                if (window.switchTab) {
                    window.switchTab('xero');
                    setTimeout(() => {
                        // Let Xero module handle the specific record
                        this.events.emit('xero-open-record', { id, source });
                    }, 300);
                }
                break;

            case 'inhouseprint':
                // Open InHousePrint project (custom handling)
                this.log.info('InHousePrint project:', id);
                // TODO: Add InHousePrint navigation logic
                break;

            case 'vector-database':
                // Vector DB results should link to original document
                const vectorResult = this.state.results.find(r => r.id === id);
                if (vectorResult?.document_id) {
                    this.openResult(vectorResult.document_id, 'documents');
                } else {
                    this.log.warn('Vector result has no document_id:', id);
                }
                break;

            case 'automations':
                // Open automation workflow
                if (window.switchTab) {
                    window.switchTab('automation');
                }
                break;

            default:
                this.log.warn('Unknown source type:', source);
                // Emit generic event for custom handling
                this.events.emit('universal-search-result-opened', { id, source });
        }
    },

    // ==================== UTILITIES ====================

    groupResultsBySource() {
        const grouped = {};

        for (const result of this.state.results) {
            const source = result.source || 'unknown';
            if (!grouped[source]) {
                grouped[source] = [];
            }
            grouped[source].push(result);
        }

        return grouped;
    },

    getSourceIcon(source) {
        const icons = {
            documents: 'fas fa-file-alt',
            'vector-database': 'fas fa-database',
            threads: 'fas fa-comments',
            gmail: 'fas fa-envelope',
            outlook: 'fas fa-envelope-open',
            slack: 'fab fa-slack',
            synergy: 'fas fa-brain',
            'google-drive': 'fab fa-google-drive',
            onedrive: 'fas fa-cloud',
            sharepoint: 'fas fa-share-alt',
            xero: 'fas fa-file-invoice',
            inhouseprint: 'fas fa-print'
        };
        return icons[source] || 'fas fa-question-circle';
    },

    getSourceLabel(source) {
        const labels = {
            documents: 'Documents',
            'vector-database': 'Vector Database (AI Search)',
            threads: 'Chat Threads',
            gmail: 'Gmail',
            outlook: 'Outlook',
            slack: 'Slack',
            synergy: 'Synergy Sessions',
            'google-drive': 'Google Drive',
            onedrive: 'OneDrive',
            sharepoint: 'SharePoint',
            xero: 'Xero Accounting',
            inhouseprint: 'InHousePrint Projects'
        };
        return labels[source] || source;
    },

    formatDate(dateString) {
        if (!dateString) return 'Unknown';

        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;

        // Less than 1 hour
        if (diff < 3600000) {
            const mins = Math.floor(diff / 60000);
            return `${mins} min${mins !== 1 ? 's' : ''} ago`;
        }

        // Less than 1 day
        if (diff < 86400000) {
            const hours = Math.floor(diff / 3600000);
            return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
        }

        // Less than 7 days
        if (diff < 604800000) {
            const days = Math.floor(diff / 86400000);
            return `${days} day${days !== 1 ? 's' : ''} ago`;
        }

        // Older - show date
        return date.toLocaleDateString();
    },

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    // ==================== PREFERENCES ====================

    loadPreferences() {
        const saved = this.storage.get('universal-search-preferences');
        if (saved) {
            this.state.selectedSources = new Set(saved.selectedSources || ['documents', 'threads']);
            this.log.info('Loaded preferences:', saved);
        }
    },

    savePreferences() {
        this.storage.set('universal-search-preferences', {
            selectedSources: Array.from(this.state.selectedSources)
        });
        this.log.info('Saved preferences');
    }
};
