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
        selectedSources: new Set(['documents', 'threads']),
        availableSources: {},
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
     * Load available search sources
     */
    async loadAvailableSources() {
        try {
            const response = await this.api.get('/api/universal-search/sources');

            this.state.availableSources = response.sources || {
                documents: true,
                threads: true,
                gmail: false,
                slack: false,
                synergy: true
            };

            this.log.info('Available sources:', this.state.availableSources);
        } catch (error) {
            this.log.warn('Failed to load sources, using defaults:', error);
            this.state.availableSources = {
                documents: true,
                threads: true,
                gmail: false,
                slack: false,
                synergy: true
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

            this.state.results = response.results || [];
            this.state.stats = response.stats || { total: 0, bySource: {} };

            this.log.info(`Found ${this.state.results.length} results`);

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
            <div class="universal-search-dashboard">
                <!-- Header -->
                <div class="universal-search-header">
                    <div class="header-left">
                        <h1><i class="fas fa-search"></i> Universal Search</h1>
                        <p>Search across all your connected platforms in one place</p>
                    </div>
                </div>
                
                <!-- Search Bar -->
                <div class="universal-search-bar">
                    <div class="search-input-wrapper">
                        <i class="fas fa-search search-icon"></i>
                        <input 
                            type="text" 
                            id="universal-search-input" 
                            class="search-input"
                            placeholder="Search documents, messages, threads, Synergy sessions, automations, Gmail, Slack..."
                            autocomplete="off"
                        />
                        <button class="search-clear-btn" id="search-clear" style="display: none;">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                
                <!-- Filters & Options -->
                <div class="universal-search-filters">
                    <div class="filter-group">
                        <label>Search Type:</label>
                        <select id="search-type" class="filter-select">
                            <option value="hybrid">🎯 Hybrid (Best Results)</option>
                            <option value="semantic">🧠 Semantic (AI-Powered)</option>
                            <option value="fulltext">📝 Full-Text (Exact Match)</option>
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label>Sources:</label>
                        <div class="source-checkboxes">
                            ${this.renderSourceCheckboxes()}
                        </div>
                    </div>
                </div>
                
                <!-- Search States -->
                <div id="universal-search-empty" class="search-state empty-state">
                    <i class="fas fa-search empty-icon"></i>
                    <h3>Start Searching</h3>
                    <p>Enter a query to search across all your connected platforms</p>
                </div>
                
                <div id="universal-search-loading" class="search-state loading-state" style="display: none;">
                    <i class="fas fa-spinner fa-spin loading-icon"></i>
                    <h3>Searching...</h3>
                    <p>Searching across your platforms</p>
                </div>
                
                <div id="universal-search-no-results" class="search-state no-results-state" style="display: none;">
                    <i class="fas fa-inbox empty-icon"></i>
                    <h3>No Results Found</h3>
                    <p>Try different keywords or search across more platforms</p>
                </div>
                
                <!-- Results Container -->
                <div id="universal-search-results" class="search-results-container" style="display: none;">
                    <!-- Results will be rendered here -->
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
        const sources = [
            { id: 'documents', label: 'Documents', icon: 'fa-file-alt' },
            { id: 'threads', label: 'Threads', icon: 'fa-comments' },
            { id: 'messages', label: 'Messages', icon: 'fa-envelope' },
            { id: 'synergy', label: 'Synergy Sessions', icon: 'fa-users' },
            { id: 'automations', label: 'Automations', icon: 'fa-robot' },
            { id: 'gmail', label: 'Gmail', icon: 'fa-google' },
            { id: 'slack', label: 'Slack', icon: 'fa-slack' }
        ];

        return sources.map(source => {
            const available = this.state.availableSources[source.id];
            const checked = this.state.selectedSources.has(source.id);
            const disabled = !available;

            return `
                <label class="source-checkbox ${disabled ? 'disabled' : ''}">
                    <input 
                        type="checkbox" 
                        value="${source.id}" 
                        ${checked ? 'checked' : ''}
                        ${disabled ? 'disabled' : ''}
                        data-source="${source.id}"
                    />
                    <i class="fas ${source.icon}"></i>
                    <span>${source.label}</span>
                    ${!available ? '<span class="not-connected">(Not Connected)</span>' : ''}
                </label>
            `;
        }).join('');
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
        return `
            <div class="universal-search-item" data-id="${item.id}" data-source="${item.source}">
                <div class="universal-search-item-header">
                    <h5 class="universal-search-item-title">${this.escapeHtml(item.title)}</h5>
                    <span class="universal-search-item-source">${this.getSourceLabel(item.source)}</span>
                </div>
                <p class="universal-search-item-snippet">${this.escapeHtml(item.snippet || '')}</p>
                <div class="universal-search-item-footer">
                    <span class="universal-search-item-date">
                        <i class="fas fa-clock"></i>
                        ${this.formatDate(item.created_at || item.timestamp)}
                    </span>
                    ${item.score ? `<span class="universal-search-item-score">Relevance: ${Math.round(item.score * 100)}%</span>` : ''}
                </div>
            </div>
        `;
    },

    // ==================== EVENT HANDLING ====================

    setupEventListeners() {
        // Search input with debouncing
        const searchInput = this.container.querySelector('#universal-search-input');
        if (searchInput) {
            this.dom.on(searchInput, 'input', (e) => {
                this.state.query = e.target.value;

                // Show/hide clear button
                const clearBtn = this.container.querySelector('[data-action="clear"]');
                if (clearBtn) {
                    clearBtn.style.display = this.state.query ? 'block' : 'none';
                }

                // Debounced search
                if (this.state.searchTimeout) {
                    clearTimeout(this.state.searchTimeout);
                }

                this.state.searchTimeout = setTimeout(() => {
                    this.search();
                }, 500);
            });
        }

        // Clear button
        this.dom.on(this.container, 'click', '[data-action="clear"]', () => {
            const input = this.container.querySelector('#universal-search-input');
            if (input) {
                input.value = '';
                this.state.query = '';
                this.showEmptyState();
            }
        });

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

        // Source filters
        this.dom.on(this.container, 'change', '.universal-search-filter-label input', (e) => {
            const source = e.target.value;

            if (e.target.checked) {
                this.state.selectedSources.add(source);
            } else {
                this.state.selectedSources.delete(source);
            }

            this.log.info('Selected sources:', Array.from(this.state.selectedSources));

            // Re-search if query exists
            if (this.state.query) {
                this.search();
            }
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

        // Emit event for other modules to handle
        this.events.emit('universal-search-result-opened', { id, source });

        // TODO: Implement source-specific opening logic
        // - documents: Open document viewer
        // - threads: Open thread in chat
        // - gmail: Open Gmail integration
        // - slack: Open Slack integration
        // - synergy: Open Synergy session
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
            threads: 'fas fa-comments',
            gmail: 'fas fa-envelope',
            slack: 'fab fa-slack',
            synergy: 'fas fa-brain'
        };
        return icons[source] || 'fas fa-question-circle';
    },

    getSourceLabel(source) {
        const labels = {
            documents: 'Documents',
            threads: 'Chat Threads',
            gmail: 'Gmail',
            slack: 'Slack',
            synergy: 'Synergy Sessions'
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
