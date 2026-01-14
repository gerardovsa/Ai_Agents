/**
 * Vector Database - Enhanced Features Module
 * 
 * PURPOSE: Advanced Pinecone capabilities (hybrid search, cross-namespace queries, metadata filtering)
 * FRAMEWORK: ModuleLoaderV4 composition pattern
 * 
 * FEATURES:
 * - Hybrid Search (sparse + dense vectors)
 * - Cross-Namespace Queries
 * - Advanced Metadata Filtering
 * - Namespace Management
 * - Reranking Support
 * 
 * DEPENDENCIES: Extends vector_database_modern.js
 * LAST MODIFIED: 2025-11-30 - Initial implementation
 */

export const EnhancedVectorFeatures = {

    // ==================== HYBRID SEARCH UI ====================

    renderHybridSearchTab(container, utilities) {
        const html = `
            <div class="vector-db-enhanced-section">
                <div class="section-header">
                    <h3>🔍 Hybrid Search</h3>
                    <p>Combine keyword and semantic search for better accuracy</p>
                </div>
                
                <div class="hybrid-search-form">
                    <div class="form-group">
                        <label for="hybrid-query">Search Query</label>
                        <textarea 
                            id="hybrid-query" 
                            placeholder="Enter your search query..."
                            rows="3"
                        ></textarea>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="enable-hybrid" checked />
                                Enable Hybrid Search
                            </label>
                            <small>Combines keyword matching with semantic understanding</small>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="hybrid-namespace">Namespace</label>
                            <select id="hybrid-namespace">
                                <option value="default">Default</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="hybrid-top-k">Results</label>
                            <input type="number" id="hybrid-top-k" value="10" min="1" max="100" />
                        </div>
                    </div>
                    
                    <button 
                        class="btn-primary" 
                        data-action="hybrid-search"
                    >
                        🔍 Search
                    </button>
                </div>
                
                <div id="hybrid-results" class="results-container"></div>
            </div>
        `;

        utilities.dom.html(container, html);
        this.loadNamespaceOptions('#hybrid-namespace', utilities);

        // Event listener
        utilities.dom.on(container, 'click', '[data-action="hybrid-search"]', () => {
            this.performHybridSearch(utilities);
        });
    },

    async performHybridSearch(utilities) {
        const query = utilities.dom.find('#hybrid-query')?.value.trim();
        const namespace = utilities.dom.find('#hybrid-namespace')?.value;
        const topK = parseInt(utilities.dom.find('#hybrid-top-k')?.value) || 10;
        const enableHybrid = utilities.dom.find('#enable-hybrid')?.checked;

        if (!query) {
            utilities.log.warn('[HYBRID SEARCH] Empty query');
            return;
        }

        try {
            utilities.log.info('[HYBRID SEARCH] Searching...', { query, namespace, enableHybrid });

            const response = await utilities.api.post('/api/vector-db/query', {
                query_text: query,
                namespace: namespace,
                top_k: topK,
                enable_hybrid: enableHybrid,
                include_metadata: true,
                include_values: false
            });

            this.renderSearchResults(response.data, utilities);

        } catch (error) {
            utilities.log.error('[HYBRID SEARCH] Failed:', error);
            utilities.dom.html('#hybrid-results', `
                <div class="error-message">
                    Search failed: ${error.message}
                </div>
            `);
        }
    },

    // ==================== CROSS-NAMESPACE SEARCH ====================

    renderCrossNamespaceTab(container, utilities) {
        const html = `
            <div class="vector-db-enhanced-section">
                <div class="section-header">
                    <h3>🌐 Cross-Namespace Search</h3>
                    <p>Query multiple namespaces simultaneously</p>
                </div>
                
                <div class="cross-namespace-form">
                    <div class="form-group">
                        <label for="cross-query">Search Query</label>
                        <textarea 
                            id="cross-query" 
                            placeholder="Enter your search query..."
                            rows="3"
                        ></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>Select Namespaces</label>
                        <div id="namespace-selector" class="namespace-checkboxes">
                            <div class="loading">Loading namespaces...</div>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="cross-metric">Distance Metric</label>
                            <select id="cross-metric">
                                <option value="cosine">Cosine Similarity</option>
                                <option value="euclidean">Euclidean Distance</option>
                                <option value="dotproduct">Dot Product</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="cross-top-k">Results per Namespace</label>
                            <input type="number" id="cross-top-k" value="10" min="1" max="50" />
                        </div>
                    </div>
                    
                    <button 
                        class="btn-primary" 
                        data-action="cross-namespace-search"
                    >
                        🌐 Search All Selected
                    </button>
                </div>
                
                <div id="cross-results" class="results-container"></div>
            </div>
        `;

        utilities.dom.html(container, html);
        this.loadNamespaceCheckboxes(utilities);

        // Event listener
        utilities.dom.on(container, 'click', '[data-action="cross-namespace-search"]', () => {
            this.performCrossNamespaceSearch(utilities);
        });
    },

    async loadNamespaceCheckboxes(utilities) {
        try {
            const response = await utilities.api.get('/api/vector-db/namespaces');
            const namespaces = response.data.namespaces || [];

            if (namespaces.length === 0) {
                utilities.dom.html('#namespace-selector', `
                    <div class="info-message">No namespaces found. Upload documents first.</div>
                `);
                return;
            }

            const html = namespaces.map(ns => `
                <label class="namespace-checkbox">
                    <input type="checkbox" value="${ns.name}" data-count="${ns.vector_count}" />
                    <span class="ns-name">${ns.name}</span>
                    <span class="ns-count">(${ns.vector_count} vectors)</span>
                </label>
            `).join('');

            utilities.dom.html('#namespace-selector', html);

        } catch (error) {
            utilities.log.error('[CROSS-NAMESPACE] Failed to load namespaces:', error);
            utilities.dom.html('#namespace-selector', `
                <div class="error-message">Failed to load namespaces</div>
            `);
        }
    },

    async performCrossNamespaceSearch(utilities) {
        const query = utilities.dom.find('#cross-query')?.value.trim();
        const metric = utilities.dom.find('#cross-metric')?.value;
        const topK = parseInt(utilities.dom.find('#cross-top-k')?.value) || 10;

        const selectedNamespaces = Array.from(
            utilities.dom.findAll('#namespace-selector input[type="checkbox"]:checked')
        ).map(el => el.value);

        if (!query) {
            utilities.log.warn('[CROSS-NAMESPACE] Empty query');
            return;
        }

        if (selectedNamespaces.length === 0) {
            utilities.dom.html('#cross-results', `
                <div class="warning-message">Please select at least one namespace</div>
            `);
            return;
        }

        try {
            utilities.log.info('[CROSS-NAMESPACE] Searching...', { query, namespaces: selectedNamespaces, metric });

            utilities.dom.html('#cross-results', `<div class="loading">Searching ${selectedNamespaces.length} namespaces...</div>`);

            const response = await utilities.api.post('/api/vector-db/query-namespaces', {
                query_text: query,
                namespaces: selectedNamespaces,
                metric: metric,
                top_k: topK,
                include_metadata: true
            });

            this.renderCrossNamespaceResults(response.data, utilities);

        } catch (error) {
            utilities.log.error('[CROSS-NAMESPACE] Search failed:', error);
            utilities.dom.html('#cross-results', `
                <div class="error-message">
                    Search failed: ${error.message}
                </div>
            `);
        }
    },

    renderCrossNamespaceResults(data, utilities) {
        const matches = data.matches || [];
        const usage = data.usage || {};

        if (matches.length === 0) {
            utilities.dom.html('#cross-results', `
                <div class="info-message">No results found</div>
            `);
            return;
        }

        const html = `
            <div class="search-results">
                <div class="results-header">
                    <h4>Found ${matches.length} results</h4>
                    <span class="usage-info">Read Units: ${usage.read_units || 'N/A'}</span>
                </div>
                
                <div class="results-list">
                    ${matches.map((match, idx) => `
                        <div class="result-card" data-index="${idx}">
                            <div class="result-header">
                                <span class="result-rank">#${idx + 1}</span>
                                <span class="namespace-badge">${match.namespace || 'default'}</span>
                                <span class="score-badge">Score: ${(match.score || 0).toFixed(4)}</span>
                            </div>
                            <div class="result-body">
                                <h5>${match.metadata?.title || match.id}</h5>
                                ${match.metadata?.text ? `<p class="result-text">${this.truncateText(match.metadata.text, 200)}</p>` : ''}
                            </div>
                            <div class="result-footer">
                                <small>ID: ${match.id}</small>
                                ${match.metadata?.source ? `<small>Source: ${match.metadata.source}</small>` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        utilities.dom.html('#cross-results', html);
    },

    // ==================== METADATA FILTERING ====================

    renderMetadataFilterTab(container, utilities) {
        const html = `
            <div class="vector-db-enhanced-section">
                <div class="section-header">
                    <h3>🔧 Advanced Metadata Filtering</h3>
                    <p>Query vectors by metadata without embeddings</p>
                </div>
                
                <div class="metadata-filter-form">
                    <div class="filter-builder">
                        <div id="filter-rules"></div>
                        <button class="btn-secondary" data-action="add-filter-rule">
                            ➕ Add Filter Rule
                        </button>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="metadata-namespace">Namespace</label>
                            <select id="metadata-namespace">
                                <option value="default">Default</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="metadata-limit">Limit</label>
                            <input type="number" id="metadata-limit" value="100" min="1" max="1000" />
                        </div>
                    </div>
                    
                    <button 
                        class="btn-primary" 
                        data-action="fetch-by-metadata"
                    >
                        🔍 Fetch Vectors
                    </button>
                </div>
                
                <div id="metadata-results" class="results-container"></div>
            </div>
        `;

        utilities.dom.html(container, html);
        this.loadNamespaceOptions('#metadata-namespace', utilities);

        // Event listeners
        utilities.dom.on(container, 'click', '[data-action="add-filter-rule"]', () => {
            this.addFilterRule(utilities);
        });

        utilities.dom.on(container, 'click', '[data-action="fetch-by-metadata"]', () => {
            this.fetchByMetadata(utilities);
        });

        // Add initial filter rule
        this.addFilterRule(utilities);
    },

    addFilterRule(utilities) {
        const ruleHtml = `
            <div class="filter-rule">
                <select class="filter-field">
                    <option value="">-- Select Field --</option>
                    <option value="category">Category</option>
                    <option value="year">Year</option>
                    <option value="author">Author</option>
                    <option value="title">Title</option>
                    <option value="source">Source</option>
                    <option value="type">Type</option>
                </select>
                
                <select class="filter-operator">
                    <option value="$eq">Equals</option>
                    <option value="$ne">Not Equals</option>
                    <option value="$gt">Greater Than</option>
                    <option value="$gte">Greater or Equal</option>
                    <option value="$lt">Less Than</option>
                    <option value="$lte">Less or Equal</option>
                    <option value="$in">In List</option>
                </select>
                
                <input type="text" class="filter-value" placeholder="Value" />
                
                <button class="btn-icon btn-danger" data-action="remove-filter-rule" title="Remove">
                    ✕
                </button>
            </div>
        `;

        utilities.dom.append('#filter-rules', ruleHtml);

        // Add remove listener to the new rule
        const rules = utilities.dom.findAll('.filter-rule');
        const newRule = rules[rules.length - 1];
        utilities.dom.on(newRule, 'click', '[data-action="remove-filter-rule"]', (e) => {
            e.currentTarget.closest('.filter-rule').remove();
        });
    },

    async fetchByMetadata(utilities) {
        const namespace = utilities.dom.find('#metadata-namespace')?.value;
        const limit = parseInt(utilities.dom.find('#metadata-limit')?.value) || 100;

        // Build filter object
        const filter = {};
        const rules = utilities.dom.findAll('.filter-rule');

        rules.forEach(rule => {
            const field = rule.querySelector('.filter-field')?.value;
            const operator = rule.querySelector('.filter-operator')?.value;
            const value = rule.querySelector('.filter-value')?.value.trim();

            if (field && operator && value) {
                // Parse value for numbers
                const parsedValue = isNaN(value) ? value : Number(value);

                if (!filter[field]) {
                    filter[field] = {};
                }
                filter[field][operator] = parsedValue;
            }
        });

        if (Object.keys(filter).length === 0) {
            utilities.dom.html('#metadata-results', `
                <div class="warning-message">Please add at least one filter rule</div>
            `);
            return;
        }

        try {
            utilities.log.info('[METADATA FILTER] Fetching...', { filter, namespace, limit });

            utilities.dom.html('#metadata-results', `<div class="loading">Fetching vectors...</div>`);

            const response = await utilities.api.post('/api/vector-db/fetch-by-metadata', {
                filter: filter,
                namespace: namespace,
                limit: limit
            });

            this.renderMetadataResults(response.data, utilities);

        } catch (error) {
            utilities.log.error('[METADATA FILTER] Fetch failed:', error);
            utilities.dom.html('#metadata-results', `
                <div class="error-message">
                    Fetch failed: ${error.message}
                </div>
            `);
        }
    },

    renderMetadataResults(data, utilities) {
        const vectors = data.vectors || [];

        if (vectors.length === 0) {
            utilities.dom.html('#metadata-results', `
                <div class="info-message">No vectors matched the filter</div>
            `);
            return;
        }

        const html = `
            <div class="metadata-results">
                <div class="results-header">
                    <h4>Found ${vectors.length} vectors</h4>
                    <button class="btn-secondary btn-sm" data-action="export-metadata-results">
                        📥 Export JSON
                    </button>
                </div>
                
                <div class="results-table">
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Metadata</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${vectors.map(vec => `
                                <tr>
                                    <td><code>${vec.id}</code></td>
                                    <td>
                                        <div class="metadata-preview">
                                            ${this.formatMetadata(vec.metadata)}
                                        </div>
                                    </td>
                                    <td>
                                        <button 
                                            class="btn-icon" 
                                            data-action="view-vector" 
                                            data-id="${vec.id}"
                                            title="View Details"
                                        >
                                            👁️
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        utilities.dom.html('#metadata-results', html);

        // Export listener
        utilities.dom.on('#metadata-results', 'click', '[data-action="export-metadata-results"]', () => {
            this.exportMetadataResults(vectors);
        });
    },

    // ==================== NAMESPACE MANAGEMENT ====================

    renderNamespaceManagementTab(container, utilities) {
        const html = `
            <div class="vector-db-enhanced-section">
                <div class="section-header">
                    <h3>📁 Namespace Management</h3>
                    <p>Organize vectors in isolated namespaces</p>
                </div>
                
                <div class="namespace-list-container">
                    <div class="list-header">
                        <h4>Available Namespaces</h4>
                        <button class="btn-secondary btn-sm" data-action="refresh-namespaces">
                            🔄 Refresh
                        </button>
                    </div>
                    
                    <div id="namespaces-table" class="loading">
                        Loading namespaces...
                    </div>
                </div>
            </div>
        `;

        utilities.dom.html(container, html);
        this.loadNamespaceTable(utilities);

        // Event listeners
        utilities.dom.on(container, 'click', '[data-action="refresh-namespaces"]', () => {
            this.loadNamespaceTable(utilities);
        });
    },

    async loadNamespaceTable(utilities) {
        try {
            utilities.dom.html('#namespaces-table', `<div class="loading">Loading...</div>`);

            const response = await utilities.api.get('/api/vector-db/namespaces');
            const namespaces = response.data.namespaces || [];

            if (namespaces.length === 0) {
                utilities.dom.html('#namespaces-table', `
                    <div class="info-message">No namespaces found</div>
                `);
                return;
            }

            const html = `
                <table class="namespace-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Vector Count</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${namespaces.map(ns => `
                            <tr data-namespace="${ns.name}">
                                <td><strong>${ns.name}</strong></td>
                                <td>${ns.vector_count.toLocaleString()}</td>
                                <td>
                                    <button 
                                        class="btn-icon" 
                                        data-action="describe-namespace" 
                                        data-ns="${ns.name}"
                                        title="View Details"
                                    >
                                        ℹ️
                                    </button>
                                    <button 
                                        class="btn-icon btn-danger" 
                                        data-action="delete-namespace" 
                                        data-ns="${ns.name}"
                                        title="Delete Namespace"
                                        ${ns.name === 'default' ? 'disabled' : ''}
                                    >
                                        🗑️
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;

            utilities.dom.html('#namespaces-table', html);

            // Add event listeners for actions
            utilities.dom.on('#namespaces-table', 'click', '[data-action="describe-namespace"]', (e) => {
                const namespace = e.currentTarget.dataset.ns;
                this.describeNamespace(namespace, utilities);
            });

            utilities.dom.on('#namespaces-table', 'click', '[data-action="delete-namespace"]', (e) => {
                const namespace = e.currentTarget.dataset.ns;
                this.deleteNamespace(namespace, utilities);
            });

        } catch (error) {
            utilities.log.error('[NAMESPACE MGMT] Load failed:', error);
            utilities.dom.html('#namespaces-table', `
                <div class="error-message">Failed to load namespaces</div>
            `);
        }
    },

    async describeNamespace(namespace, utilities) {
        try {
            const response = await utilities.api.get(`/api/vector-db/namespaces/${namespace}`);
            const info = response.data;

            alert(`Namespace: ${info.name}\nVectors: ${info.vector_count}\nDimension: ${info.dimension}`);

        } catch (error) {
            utilities.log.error('[NAMESPACE MGMT] Describe failed:', error);
            alert('Failed to get namespace details');
        }
    },

    async deleteNamespace(namespace, utilities) {
        if (!confirm(`Are you sure you want to delete namespace "${namespace}"?\n\nThis will permanently delete all vectors in this namespace.`)) {
            return;
        }

        try {
            await utilities.api.delete(`/api/vector-db/namespaces/${namespace}`);
            utilities.log.info('[NAMESPACE MGMT] Deleted:', namespace);
            this.loadNamespaceTable(utilities);

        } catch (error) {
            utilities.log.error('[NAMESPACE MGMT] Delete failed:', error);
            alert('Failed to delete namespace');
        }
    },

    // ==================== UTILITY METHODS ====================

    async loadNamespaceOptions(selector, utilities) {
        try {
            const response = await utilities.api.get('/api/vector-db/namespaces');
            const namespaces = response.data.namespaces || [];

            const select = utilities.dom.find(selector);
            if (!select) return;

            select.innerHTML = namespaces.map(ns => `
                <option value="${ns.name}">${ns.name} (${ns.vector_count} vectors)</option>
            `).join('');

        } catch (error) {
            utilities.log.error('[ENHANCED] Failed to load namespace options:', error);
        }
    },

    renderSearchResults(data, utilities) {
        const matches = data.matches || [];

        if (matches.length === 0) {
            return '<div class="info-message">No results found</div>';
        }

        return `
            <div class="search-results">
                <h4>Found ${matches.length} results</h4>
                ${matches.map((match, idx) => `
                    <div class="result-card">
                        <div class="result-header">
                            <span class="result-rank">#${idx + 1}</span>
                            <span class="score-badge">${(match.score || 0).toFixed(4)}</span>
                        </div>
                        <div class="result-body">
                            <h5>${match.metadata?.title || match.id}</h5>
                            ${match.metadata?.text ? `<p>${this.truncateText(match.metadata.text, 200)}</p>` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    },

    formatMetadata(metadata) {
        if (!metadata || typeof metadata !== 'object') {
            return '<em>No metadata</em>';
        }

        return Object.entries(metadata)
            .slice(0, 3)
            .map(([key, value]) => `<div><strong>${key}:</strong> ${value}</div>`)
            .join('');
    },

    truncateText(text, maxLength) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    },

    exportMetadataResults(vectors) {
        const json = JSON.stringify(vectors, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `metadata-results-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
};
