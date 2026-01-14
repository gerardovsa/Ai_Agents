/**
 * Universal Search Module
 * 
 * FILE: UI/modules_internal/universal-search/universal-search.js
 * PURPOSE: Search across all connected platforms in one unified interface
 * 
 * FEATURES:
 * - Single search box for all platforms
 * - Multi-platform results (documents, messages, threads, Synergy, Gmail, Slack)
 * - Search type selector (full-text, semantic, hybrid)
 * - Faceted filters sidebar
 * - Real-time search suggestions
 * - Result grouping by source
 * 
 * LAST MODIFIED: 2025-11-30
 */

class UniversalSearchModule {
    constructor() {
        this.moduleId = 'universal-search';
        this.searchTimeout = null;
        this.currentResults = {};
        this.selectedSources = new Set(['documents', 'threads', 'messages', 'synergy']);
        this.searchType = 'hybrid'; // fulltext, semantic, hybrid
        this.facets = {};
    }

    /**
     * Initialize module
     */
    async initialize() {
        console.log('[Universal Search] Initializing...');
        
        try {
            // Check available sources
            await this.loadAvailableSources();
            
            // Load search interface
            this.renderSearchInterface();
            
            console.log('[Universal Search] Initialized successfully');
            return true;
        } catch (error) {
            console.error('[Universal Search] Initialization error:', error);
            return false;
        }
    }

    /**
     * Load available search sources
     */
    async loadAvailableSources() {
        try {
            const response = await fetch('/api/universal-search/sources', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) throw new Error('Failed to load sources');

            const data = await response.json();
            this.availableSources = data.sources || {};
            
            console.log('[Universal Search] Available sources:', this.availableSources);
        } catch (error) {
            console.error('[Universal Search] Error loading sources:', error);
            this.availableSources = {
                documents: true,
                threads: true,
                messages: true,
                synergy: true
            };
        }
    }

    /**
     * Render search interface
     */
    renderSearchInterface() {
        const container = document.getElementById('universal-search-container');
        if (!container) {
            console.error('[Universal Search] Container not found');
            return;
        }

        container.innerHTML = `
            <div class="universal-search-wrapper">
                <!-- Search Header -->
                <div class="search-header">
                    <h2>🔍 Universal Search</h2>
                    <p>Search across all your connected platforms in one place</p>
                </div>

                <!-- Search Input Row -->
                <div class="search-input-row">
                    <div class="search-box">
                        <input 
                            type="text" 
                            id="universal-search-input" 
                            placeholder="Search documents, messages, threads, Synergy sessions..." 
                            autocomplete="off"
                        />
                        <button id="search-btn" class="search-btn">
                            <span class="search-icon">🔍</span>
                        </button>
                    </div>
                </div>

                <!-- Search Options -->
                <div class="search-options">
                    <div class="search-type-selector">
                        <label>Search Type:</label>
                        <select id="search-type">
                            <option value="hybrid">🎯 Hybrid (Best Results)</option>
                            <option value="semantic">🧠 Semantic (AI-Powered)</option>
                            <option value="fulltext">📝 Full-Text (Exact Match)</option>
                        </select>
                    </div>

                    <div class="source-filters">
                        <label>Sources:</label>
                        ${this.renderSourceCheckboxes()}
                    </div>
                </div>

                <!-- Results Container -->
                <div class="search-results-container">
                    <div id="search-results" class="search-results">
                        <!-- Results will be rendered here -->
                        <div class="empty-state">
                            <div class="empty-icon">🔍</div>
                            <h3>Start Searching</h3>
                            <p>Enter a query to search across all your connected platforms</p>
                        </div>
                    </div>

                    <!-- Facets Sidebar -->
                    <div id="search-facets" class="search-facets">
                        <!-- Facets will be rendered here -->
                    </div>
                </div>
            </div>
        `;

        // Attach event listeners
        this.attachEventListeners();
    }

    /**
     * Render source checkboxes
     */
    renderSourceCheckboxes() {
        const sources = [
            { id: 'documents', label: 'Documents', icon: '📄' },
            { id: 'threads', label: 'Threads', icon: '💬' },
            { id: 'messages', label: 'Messages', icon: '✉️' },
            { id: 'synergy', label: 'Synergy', icon: '🤝' },
            { id: 'gmail', label: 'Gmail', icon: '📧' },
            { id: 'slack', label: 'Slack', icon: '💼' }
        ];

        return sources.map(source => {
            const available = this.availableSources[source.id];
            const checked = this.selectedSources.has(source.id);
            const disabled = !available ? 'disabled' : '';
            
            return `
                <label class="source-checkbox ${disabled}">
                    <input 
                        type="checkbox" 
                        value="${source.id}" 
                        ${checked ? 'checked' : ''}
                        ${disabled}
                        data-source="${source.id}"
                    />
                    <span>${source.icon} ${source.label}</span>
                    ${!available ? '<span class="not-connected">(Not Connected)</span>' : ''}
                </label>
            `;
        }).join('');
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Search input (debounced)
        const searchInput = document.getElementById('universal-search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                clearTimeout(this.searchTimeout);
                const query = e.target.value.trim();
                
                if (query.length >= 2) {
                    this.searchTimeout = setTimeout(() => {
                        this.performSearch(query);
                    }, 300); // 300ms debounce
                } else if (query.length === 0) {
                    this.clearResults();
                }
            });

            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    clearTimeout(this.searchTimeout);
                    this.performSearch(e.target.value.trim());
                }
            });
        }

        // Search button
        const searchBtn = document.getElementById('search-btn');
        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                const query = document.getElementById('universal-search-input').value.trim();
                if (query) {
                    this.performSearch(query);
                }
            });
        }

        // Search type selector
        const searchType = document.getElementById('search-type');
        if (searchType) {
            searchType.addEventListener('change', (e) => {
                this.searchType = e.target.value;
                const query = document.getElementById('universal-search-input').value.trim();
                if (query) {
                    this.performSearch(query);
                }
            });
        }

        // Source checkboxes
        const checkboxes = document.querySelectorAll('.source-checkbox input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const source = e.target.dataset.source;
                if (e.target.checked) {
                    this.selectedSources.add(source);
                } else {
                    this.selectedSources.delete(source);
                }
                
                const query = document.getElementById('universal-search-input').value.trim();
                if (query) {
                    this.performSearch(query);
                }
            });
        });
    }

    /**
     * Perform universal search
     */
    async performSearch(query) {
        if (!query || query.length < 2) return;

        console.log('[Universal Search] Searching:', query);

        const resultsContainer = document.getElementById('search-results');
        resultsContainer.innerHTML = '<div class="loading-spinner">🔄 Searching across platforms...</div>';

        try {
            const response = await fetch('/api/universal-search/search', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    search_type: this.searchType,
                    sources: Array.from(this.selectedSources),
                    limit: 50
                })
            });

            if (!response.ok) throw new Error('Search failed');

            const data = await response.json();
            this.currentResults = data.results || {};
            this.facets = data.facets || {};

            console.log('[Universal Search] Results:', this.currentResults);

            this.renderResults(query);
            this.renderFacets();

        } catch (error) {
            console.error('[Universal Search] Search error:', error);
            resultsContainer.innerHTML = `
                <div class="error-state">
                    <div class="error-icon">❌</div>
                    <h3>Search Error</h3>
                    <p>${error.message}</p>
                </div>
            `;
        }
    }

    /**
     * Render search results
     */
    renderResults(query) {
        const resultsContainer = document.getElementById('search-results');
        
        const sources = Object.keys(this.currentResults);
        if (sources.length === 0) {
            resultsContainer.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🔍</div>
                    <h3>No Results Found</h3>
                    <p>Try different keywords or search across more platforms</p>
                </div>
            `;
            return;
        }

        let html = `<div class="results-summary">Found ${this.getTotalResultCount()} results across ${sources.length} platforms</div>`;

        // Group results by source
        sources.forEach(source => {
            const results = this.currentResults[source];
            if (!results || results.length === 0) return;

            const sourceIcon = this.getSourceIcon(source);
            const sourceName = this.getSourceName(source);

            html += `
                <div class="result-group" data-source="${source}">
                    <div class="result-group-header">
                        <span class="source-icon">${sourceIcon}</span>
                        <h3>${sourceName}</h3>
                        <span class="result-count">${results.length} results</span>
                    </div>
                    <div class="result-items">
                        ${results.map(result => this.renderResultItem(result, source)).join('')}
                    </div>
                </div>
            `;
        });

        resultsContainer.innerHTML = html;

        // Attach result item click listeners
        this.attachResultClickListeners();
    }

    /**
     * Render single result item
     */
    renderResultItem(result, source) {
        const icon = this.getSourceIcon(source);
        const score = result.score ? (result.score * 100).toFixed(1) : 'N/A';
        
        return `
            <div class="result-item" data-id="${result.id}" data-source="${source}">
                <div class="result-icon">${icon}</div>
                <div class="result-content">
                    <h4 class="result-title">${this.highlightText(result.title || result.subject || 'Untitled', result.query)}</h4>
                    <p class="result-snippet">${this.highlightText(this.truncateText(result.content || result.body || '', 200), result.query)}</p>
                    <div class="result-meta">
                        <span class="result-date">${this.formatDate(result.created_at || result.timestamp)}</span>
                        ${result.author ? `<span class="result-author">by ${result.author}</span>` : ''}
                        <span class="result-score">Score: ${score}%</span>
                    </div>
                </div>
                <div class="result-actions">
                    <button class="result-open-btn" data-id="${result.id}" data-source="${source}">Open</button>
                </div>
            </div>
        `;
    }

    /**
     * Render facets sidebar
     */
    renderFacets() {
        const facetsContainer = document.getElementById('search-facets');
        if (!facetsContainer) return;

        if (!this.facets || Object.keys(this.facets).length === 0) {
            facetsContainer.innerHTML = '';
            return;
        }

        let html = '<div class="facets-header"><h3>Filters</h3></div>';

        // Document sources facet
        if (this.facets.document_sources && this.facets.document_sources.length > 0) {
            html += `
                <div class="facet-group">
                    <h4>Document Sources</h4>
                    ${this.facets.document_sources.map(item => `
                        <label class="facet-item">
                            <input type="checkbox" value="${item.source}" />
                            <span>${item.source}</span>
                            <span class="facet-count">${item.count}</span>
                        </label>
                    `).join('')}
                </div>
            `;
        }

        // Document types facet
        if (this.facets.document_types && this.facets.document_types.length > 0) {
            html += `
                <div class="facet-group">
                    <h4>Document Types</h4>
                    ${this.facets.document_types.map(item => `
                        <label class="facet-item">
                            <input type="checkbox" value="${item.type}" />
                            <span>${item.type}</span>
                            <span class="facet-count">${item.count}</span>
                        </label>
                    `).join('')}
                </div>
            `;
        }

        facetsContainer.innerHTML = html;
    }

    /**
     * Attach result click listeners
     */
    attachResultClickListeners() {
        const openButtons = document.querySelectorAll('.result-open-btn');
        openButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.dataset.id;
                const source = e.target.dataset.source;
                this.openResult(id, source);
            });
        });
    }

    /**
     * Open result item
     */
    openResult(id, source) {
        console.log('[Universal Search] Opening result:', id, source);
        
        // TODO: Implement result opening based on source type
        switch(source) {
            case 'documents':
                window.open(`/documents/${id}`, '_blank');
                break;
            case 'threads':
                window.location.href = `/threads/${id}`;
                break;
            case 'messages':
                // Navigate to thread containing message
                break;
            case 'synergy':
                window.location.href = `/synergy/${id}`;
                break;
            case 'gmail':
                window.open(`https://mail.google.com/mail/u/0/#inbox/${id}`, '_blank');
                break;
            case 'slack':
                // Open Slack link
                break;
        }
    }

    /**
     * Helper: Get source icon
     */
    getSourceIcon(source) {
        const icons = {
            documents: '📄',
            threads: '💬',
            messages: '✉️',
            synergy: '🤝',
            gmail: '📧',
            slack: '💼',
            supabase: '🗄️'
        };
        return icons[source] || '📎';
    }

    /**
     * Helper: Get source name
     */
    getSourceName(source) {
        const names = {
            documents: 'Documents',
            threads: 'Threads',
            messages: 'Messages',
            synergy: 'Synergy Sessions',
            gmail: 'Gmail',
            slack: 'Slack',
            supabase: 'Database'
        };
        return names[source] || source;
    }

    /**
     * Helper: Get total result count
     */
    getTotalResultCount() {
        let total = 0;
        Object.values(this.currentResults).forEach(results => {
            total += results.length;
        });
        return total;
    }

    /**
     * Helper: Highlight search terms
     */
    highlightText(text, query) {
        if (!query || !text) return text;
        
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    /**
     * Helper: Truncate text
     */
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    /**
     * Helper: Format date
     */
    formatDate(dateStr) {
        if (!dateStr) return 'Unknown';
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });
    }

    /**
     * Clear results
     */
    clearResults() {
        const resultsContainer = document.getElementById('search-results');
        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🔍</div>
                    <h3>Start Searching</h3>
                    <p>Enter a query to search across all your connected platforms</p>
                </div>
            `;
        }

        const facetsContainer = document.getElementById('search-facets');
        if (facetsContainer) {
            facetsContainer.innerHTML = '';
        }
    }

    /**
     * Get sub-tab container
     */
    getSubTabContainer() {
        return document.getElementById('universal-search-container');
    }
}

// Export module
window.UniversalSearchModule = UniversalSearchModule;

// Auto-initialize if container exists
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('universal-search-container')) {
        window.universalSearchModule = new UniversalSearchModule();
        window.universalSearchModule.initialize();
    }
});
