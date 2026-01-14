/**
 * FILE: UI/external/modules/synergy/synergy-doc-picker.js
 * PURPOSE: Internal document picker modal for Synergy sessions
 * 
 * FEATURES:
 * - Search documents by title/description
 * - Filter by type (richtext/spreadsheet)
 * - Filter by date range
 * - Filter by tags
 * - Sort by date/title/type
 * - Select document to link to session
 * 
 * LAST MODIFIED: 2025-11-24 - Initial implementation
 */

import { documentService } from '../shared/document-service.js';

class SynergyDocPicker {
    constructor() {
        this.API_BASE_URL = window.API_BASE_URL || 'http://localhost:5001';
        this.isOpen = false;
        this.documents = [];
        this.filteredDocs = [];
        this.selectedDocId = null;
        this.callback = null;
        this.filters = {
            search: '',
            type: 'all',
            dateFrom: '',
            dateTo: '',
            tags: []
        };
        this.sortBy = 'date_desc';

        console.log('[SYNERGY DOC PICKER] Initialized');
    }

    /**
     * Open the document picker modal
     * 
     * @param {Function} callback - Function to call when document is selected: callback(docId, docData)
     */
    async open(callback) {
        if (this.isOpen) return;

        this.callback = callback;
        this.isOpen = true;

        // Create modal if it doesn't exist
        if (!document.getElementById('synergy-doc-picker-modal')) {
            this.createModal();
        }

        // Show modal
        const modal = document.getElementById('synergy-doc-picker-modal');
        modal.style.display = 'flex';

        // Load documents
        await this.loadDocuments();
    }

    /**
     * Close the document picker modal
     */
    close() {
        const modal = document.getElementById('synergy-doc-picker-modal');
        if (modal) {
            modal.style.display = 'none';
        }
        this.isOpen = false;
        this.selectedDocId = null;
        this.callback = null;
    }

    /**
     * Create the modal HTML structure
     */
    createModal() {
        const modalHTML = `
            <div id="synergy-doc-picker-modal" class="synergy-doc-picker-overlay" style="display: none;">
                <div class="synergy-doc-picker-modal">
                    <!-- Header -->
                    <div class="synergy-doc-picker-header">
                        <div class="synergy-doc-picker-title">
                            <i class="fas fa-file-alt"></i>
                            Select Internal Document
                        </div>
                        <button class="synergy-doc-picker-close" onclick="window.SynergyDocPicker.close()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>

                    <!-- Filters Section -->
                    <div class="synergy-doc-picker-filters">
                        <!-- Search Bar -->
                        <div class="synergy-doc-picker-search">
                            <i class="fas fa-search"></i>
                            <input 
                                type="text" 
                                id="synergy-doc-search-input"
                                placeholder="Search by title or description..."
                                oninput="window.SynergyDocPicker.onSearchChange(this.value)"
                            >
                        </div>

                        <!-- Filter Row -->
                        <div class="synergy-doc-picker-filter-row">
                            <!-- Type Filter -->
                            <div class="synergy-doc-filter-group">
                                <label>Type:</label>
                                <select id="synergy-doc-type-filter" onchange="window.SynergyDocPicker.onTypeChange(this.value)">
                                    <option value="all">All Types</option>
                                    <option value="richtext">Rich Text</option>
                                    <option value="spreadsheet">Spreadsheet</option>
                                </select>
                            </div>

                            <!-- Date From -->
                            <div class="synergy-doc-filter-group">
                                <label>From:</label>
                                <input 
                                    type="date" 
                                    id="synergy-doc-date-from"
                                    onchange="window.SynergyDocPicker.onDateChange()"
                                >
                            </div>

                            <!-- Date To -->
                            <div class="synergy-doc-filter-group">
                                <label>To:</label>
                                <input 
                                    type="date" 
                                    id="synergy-doc-date-to"
                                    onchange="window.SynergyDocPicker.onDateChange()"
                                >
                            </div>

                            <!-- Sort -->
                            <div class="synergy-doc-filter-group">
                                <label>Sort:</label>
                                <select id="synergy-doc-sort" onchange="window.SynergyDocPicker.onSortChange(this.value)">
                                    <option value="date_desc">Newest First</option>
                                    <option value="date_asc">Oldest First</option>
                                    <option value="title_asc">Title A-Z</option>
                                    <option value="title_desc">Title Z-A</option>
                                    <option value="type_asc">Type A-Z</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <!-- Results Count -->
                    <div class="synergy-doc-picker-results-count">
                        <span id="synergy-doc-results-count">0 documents</span>
                    </div>

                    <!-- Document List -->
                    <div class="synergy-doc-picker-list" id="synergy-doc-picker-list">
                        <!-- Documents will be rendered here -->
                        <div class="synergy-doc-picker-loading">
                            <i class="fas fa-spinner fa-spin"></i>
                            <div>Loading documents...</div>
                        </div>
                    </div>

                    <!-- Footer -->
                    <div class="synergy-doc-picker-footer">
                        <button class="synergy-doc-picker-btn cancel" onclick="window.SynergyDocPicker.close()">
                            Cancel
                        </button>
                        <button class="synergy-doc-picker-btn select" onclick="window.SynergyDocPicker.selectDocument()" disabled id="synergy-doc-select-btn">
                            <i class="fas fa-check"></i>
                            Select Document
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    /**
     * Load documents from backend
     */
    async loadDocuments() {
        const listEl = document.getElementById('synergy-doc-picker-list');
        listEl.innerHTML = `
            <div class="synergy-doc-picker-loading">
                <i class="fas fa-spinner fa-spin"></i>
                <div>Loading documents...</div>
            </div>
        `;

        try {
            const data = await documentService.fetchAllDocuments();
            this.documents = data.documents || data || [];
            this.applyFilters();

        } catch (error) {
            console.error('[SYNERGY DOC PICKER] Load error:', error);
            listEl.innerHTML = `
                <div class="synergy-doc-picker-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <div>Failed to load documents</div>
                    <button onclick="window.SynergyDocPicker.loadDocuments()" class="synergy-doc-retry-btn">
                        Retry
                    </button>
                </div>
            `;
        }
    }

    /**
     * Apply filters and render documents
     */
    applyFilters() {
        let filtered = [...this.documents];

        // Search filter
        if (this.filters.search) {
            const searchLower = this.filters.search.toLowerCase();
            filtered = filtered.filter(doc =>
                doc.title.toLowerCase().includes(searchLower) ||
                (doc.description && doc.description.toLowerCase().includes(searchLower))
            );
        }

        // Type filter
        if (this.filters.type !== 'all') {
            filtered = filtered.filter(doc => doc.doc_type === this.filters.type);
        }

        // Date range filter
        if (this.filters.dateFrom) {
            const fromDate = new Date(this.filters.dateFrom);
            filtered = filtered.filter(doc => new Date(doc.created_at) >= fromDate);
        }
        if (this.filters.dateTo) {
            const toDate = new Date(this.filters.dateTo);
            toDate.setHours(23, 59, 59, 999); // End of day
            filtered = filtered.filter(doc => new Date(doc.created_at) <= toDate);
        }

        // Sort
        filtered = this.sortDocuments(filtered);

        this.filteredDocs = filtered;
        this.renderDocuments();
    }

    /**
     * Sort documents based on current sort option
     */
    sortDocuments(docs) {
        const sorted = [...docs];

        switch (this.sortBy) {
            case 'date_desc':
                sorted.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
                break;
            case 'date_asc':
                sorted.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
                break;
            case 'title_asc':
                sorted.sort((a, b) => a.title.localeCompare(b.title));
                break;
            case 'title_desc':
                sorted.sort((a, b) => b.title.localeCompare(a.title));
                break;
            case 'type_asc':
                sorted.sort((a, b) => a.doc_type.localeCompare(b.doc_type));
                break;
        }

        return sorted;
    }

    /**
     * Render filtered documents
     * ✅ UPDATED: Now uses centralized SynergyDocCardRenderer
     */
    renderDocuments() {
        const listEl = document.getElementById('synergy-doc-picker-list');
        const countEl = document.getElementById('synergy-doc-results-count');

        // Update count
        const count = this.filteredDocs.length;
        countEl.textContent = `${count} document${count !== 1 ? 's' : ''}`;

        // Use centralized renderer
        if (!window.SynergyDocCardRenderer) {
            console.error('[SYNERGY DOC PICKER] SynergyDocCardRenderer not loaded!');
            listEl.innerHTML = '<div class="synergy-doc-picker-error">Card renderer not available</div>';
            return;
        }

        const itemsHTML = window.SynergyDocCardRenderer.renderList(this.filteredDocs, {
            selectable: true,
            selected: false, // Will be applied per-item below
            onClick: 'window.SynergyDocPicker.selectItem',
            showDescription: true,
            showType: true,
            showCreated: true,
            showTags: true,
            maxTags: 2,
            variant: 'default',
            emptyMessage: 'No documents found. Try adjusting your filters.'
        });

        listEl.innerHTML = itemsHTML;

        // Apply selection state to individual cards
        if (this.selectedDocId) {
            const selectedCard = listEl.querySelector(`[data-doc-id="${this.selectedDocId}"]`);
            if (selectedCard) {
                selectedCard.classList.add('selected');
            }
        }
    }

    /**
     * Handle item selection
     * ✅ UPDATED: Works with centralized card renderer classes
     */
    selectItem(docId) {
        // Toggle selection
        if (this.selectedDocId === docId) {
            this.selectedDocId = null;
        } else {
            this.selectedDocId = docId;
        }

        // Update UI - works with both old and new class names
        document.querySelectorAll('.synergy-doc-picker-item, .synergy-doc-card').forEach(item => {
            if (item.getAttribute('data-doc-id') === docId) {
                item.classList.toggle('selected');
            } else {
                item.classList.remove('selected');
            }
        });

        // Enable/disable select button
        const selectBtn = document.getElementById('synergy-doc-select-btn');
        if (selectBtn) {
            selectBtn.disabled = !this.selectedDocId;
        }
    }

    /**
     * Confirm document selection
     */
    selectDocument() {
        if (!this.selectedDocId) return;

        const doc = this.filteredDocs.find(d => d.doc_id === this.selectedDocId);
        if (!doc) return;

        // Call callback with selected document
        if (this.callback) {
            this.callback(doc.doc_id, doc);
        }

        this.close();
    }

    /**
     * Filter change handlers
     */
    onSearchChange(value) {
        this.filters.search = value;
        this.applyFilters();
    }

    onTypeChange(value) {
        this.filters.type = value;
        this.applyFilters();
    }

    onDateChange() {
        this.filters.dateFrom = document.getElementById('synergy-doc-date-from').value;
        this.filters.dateTo = document.getElementById('synergy-doc-date-to').value;
        this.applyFilters();
    }

    onSortChange(value) {
        this.sortBy = value;
        this.applyFilters();
    }

    /**
     * Escape HTML for safe rendering
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Create global instance
window.SynergyDocPicker = new SynergyDocPicker();

console.log('[SYNERGY DOC PICKER] Module loaded and ready');
