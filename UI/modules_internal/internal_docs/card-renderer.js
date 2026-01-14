/**
 * FILE: UI/modules_internal/internal_docs/card-renderer.js
 * PURPOSE: Centralized card rendering for Synergy Internal Documents/Sheets
 * 
 * This is the SINGLE SOURCE OF TRUTH for rendering document cards across the entire application.
 * All document list UIs should use this renderer for consistency.
 * 
 * FEATURES:
 * - Unified card structure
 * - Support for both richtext and spreadsheet types
 * - Rich metadata display (date, owner, tags, modified date)
 * - Customizable appearance (selectable, clickable, inline)
 * - HTML escaping for security
 * - Consistent styling
 * 
 * USAGE:
 * ```javascript
 * const html = SynergyDocCardRenderer.render(doc, {
 *     selectable: true,
 *     onClick: 'myFunction',
 *     showOwner: true,
 *     showTags: true
 * });
 * ```
 * 
 * LAST MODIFIED: 2025-12-13 - Centralized from synergy-doc-picker.js and internal-docs-link-modal.js
 */

window.SynergyDocCardRenderer = {
    /**
     * Render a single document card
     * 
     * @param {Object} doc - Document object
     * @param {string} doc.doc_id - Document ID
     * @param {string} doc.title - Document title (also accepts doc_name)
     * @param {string} doc.description - Document description
     * @param {string} doc.doc_type - Document type ('richtext' or 'spreadsheet')
     * @param {string} doc.created_at - Creation date
     * @param {string} doc.updated_at - Last update date
     * @param {string} doc.last_modified - Last modified date (fallback to updated_at)
     * @param {string} doc.tags - Comma-separated tags
     * @param {string} doc.owner - Document owner
     * @param {string} doc.slug - Document slug
     * @param {string} doc.session_id - Associated session ID
     * 
     * @param {Object} options - Rendering options
     * @param {boolean} options.selectable - Show selection checkmark (default: false)
     * @param {boolean} options.selected - Is this card selected (default: false)
     * @param {string} options.onClick - Function name to call on click (e.g., 'myFunction')
     * @param {boolean} options.showDescription - Show description field (default: true)
     * @param {boolean} options.showType - Show type badge (default: true)
     * @param {boolean} options.showCreated - Show created date (default: true)
     * @param {boolean} options.showModified - Show modified date (default: true)
     * @param {boolean} options.showOwner - Show owner (default: false)
     * @param {boolean} options.showTags - Show tags (default: true)
     * @param {boolean} options.showSlug - Show slug/ID (default: false)
     * @param {boolean} options.showSession - Show session linkage (default: false)
     * @param {number} options.maxTags - Maximum number of tags to display (default: 2)
     * @param {string} options.variant - Card style variant: 'default', 'compact', 'detailed' (default: 'default')
     * @param {Object} options.customClass - Additional CSS classes
     * 
     * @returns {string} HTML string for the document card
     */
    render(doc, options = {}) {
        // Default options
        const opts = {
            selectable: false,
            selected: false,
            onClick: null,
            showDescription: true,
            showType: true,
            showCreated: true,
            showModified: true,
            showOwner: false,
            showTags: true,
            showSlug: false,
            showSession: false,
            maxTags: 2,
            variant: 'default',
            customClass: '',
            ...options
        };

        // Normalize document fields (handle both title/doc_name naming conventions)
        const docId = doc.doc_id || doc.id;
        const title = doc.title || doc.doc_name || 'Untitled';
        const description = doc.description || '';
        const docType = doc.doc_type || 'richtext';
        const createdAt = doc.created_at;
        const modifiedAt = doc.last_modified || doc.updated_at;
        const tags = doc.tags || '';
        const owner = doc.owner || '';
        const slug = doc.slug || '';
        const sessionId = doc.session_id || '';

        // Type-based styling
        const typeIcon = docType === 'spreadsheet' ? 'fa-table' : 'fa-file-alt';
        const typeLabel = docType === 'spreadsheet' ? 'Spreadsheet' : 'Rich Text';
        const typeClass = docType === 'spreadsheet' ? 'type-sheet' : 'type-doc';

        // Date formatting
        const createdDate = createdAt ? this.formatDate(createdAt) : 'Unknown';
        const modifiedDate = modifiedAt ? this.formatDate(modifiedAt) : createdDate;

        // Build onclick handler
        const clickHandler = opts.onClick ? `onclick="${opts.onClick}('${this.escapeAttr(docId)}')"` : '';

        // Build data attributes
        const dataAttrs = `
            data-doc-id="${this.escapeAttr(docId)}"
            data-doc-title="${this.escapeAttr(title)}"
            data-doc-type="${this.escapeAttr(docType)}"
        `;

        // Build CSS classes
        const cardClasses = [
            'synergy-doc-card',
            `variant-${opts.variant}`,
            opts.selected ? 'selected' : '',
            opts.selectable ? 'selectable' : '',
            opts.customClass
        ].filter(Boolean).join(' ');

        // Render based on variant
        if (opts.variant === 'compact') {
            return this.renderCompact(doc, opts, { docId, title, typeIcon, typeLabel, clickHandler, dataAttrs, cardClasses });
        } else if (opts.variant === 'detailed') {
            return this.renderDetailed(doc, opts, { docId, title, description, typeIcon, typeLabel, typeClass, createdDate, modifiedDate, tags, owner, slug, sessionId, clickHandler, dataAttrs, cardClasses });
        } else {
            return this.renderDefault(doc, opts, { docId, title, description, typeIcon, typeLabel, typeClass, createdDate, modifiedDate, tags, owner, slug, sessionId, clickHandler, dataAttrs, cardClasses });
        }
    },

    /**
     * Render default card variant (used by synergy-doc-picker)
     */
    renderDefault(doc, opts, data) {
        const { docId, title, description, typeIcon, typeLabel, typeClass, createdDate, modifiedDate, tags, owner, slug, sessionId, clickHandler, dataAttrs, cardClasses } = data;

        return `
            <div class="${cardClasses}" ${clickHandler} ${dataAttrs}>
                <div class="synergy-doc-card-icon">
                    <i class="fas ${typeIcon}"></i>
                </div>
                <div class="synergy-doc-card-content">
                    <div class="synergy-doc-card-title">${this.escapeHtml(title)}</div>
                    ${opts.showDescription && description ? `
                        <div class="synergy-doc-card-desc">${this.escapeHtml(description)}</div>
                    ` : ''}
                    <div class="synergy-doc-card-meta">
                        ${opts.showType ? `
                            <span class="synergy-doc-meta-type">
                                <i class="fas ${typeIcon}"></i>
                                ${typeLabel}
                            </span>
                        ` : ''}
                        ${opts.showCreated ? `
                            <span class="synergy-doc-meta-date">
                                <i class="far fa-calendar"></i>
                                ${createdDate}
                            </span>
                        ` : ''}
                        ${opts.showModified && modifiedDate !== createdDate ? `
                            <span class="synergy-doc-meta-modified">
                                <i class="fas fa-edit"></i>
                                ${modifiedDate}
                            </span>
                        ` : ''}
                        ${opts.showOwner && owner ? `
                            <span class="synergy-doc-meta-owner">
                                <i class="fas fa-user"></i>
                                ${this.escapeHtml(owner)}
                            </span>
                        ` : ''}
                        ${opts.showTags && tags ? `
                            <span class="synergy-doc-meta-tags">
                                <i class="fas fa-tags"></i>
                                ${this.formatTags(tags, opts.maxTags)}
                            </span>
                        ` : ''}
                        ${opts.showSlug && slug ? `
                            <span class="synergy-doc-meta-slug">
                                <i class="fas fa-tag"></i>
                                ${this.escapeHtml(slug)}
                            </span>
                        ` : ''}
                        ${opts.showSession && sessionId ? `
                            <span class="synergy-doc-meta-session">
                                <i class="fas fa-link"></i>
                                ${sessionId.substring(0, 8)}...
                            </span>
                        ` : ''}
                    </div>
                </div>
                ${opts.selectable ? `
                    <div class="synergy-doc-card-select">
                        <i class="fas fa-check-circle"></i>
                    </div>
                ` : ''}
            </div>
        `;
    },

    /**
     * Render compact card variant (minimal info)
     */
    renderCompact(doc, opts, data) {
        const { docId, title, typeIcon, typeLabel, clickHandler, dataAttrs, cardClasses } = data;

        return `
            <div class="${cardClasses}" ${clickHandler} ${dataAttrs}>
                <i class="fas ${typeIcon}" style="color: var(--accent-primary); margin-right: 8px;"></i>
                <span class="synergy-doc-card-title-compact">${this.escapeHtml(title)}</span>
                ${opts.showType ? `<span class="synergy-doc-type-badge">${typeLabel}</span>` : ''}
            </div>
        `;
    },

    /**
     * Render detailed card variant (all info - used by internal-docs-link-modal)
     */
    renderDetailed(doc, opts, data) {
        const { docId, title, description, typeIcon, typeLabel, typeClass, createdDate, modifiedDate, tags, owner, slug, sessionId, clickHandler, dataAttrs, cardClasses } = data;

        return `
            <div class="${cardClasses}" ${clickHandler} ${dataAttrs}>
                <div class="synergy-doc-card-header">
                    <div class="synergy-doc-card-title-row">
                        <i class="fas ${typeIcon}"></i>
                        <span>${this.escapeHtml(title)}</span>
                    </div>
                    ${opts.showType ? `
                        <div class="synergy-doc-type-badge ${typeClass}">${typeLabel}</div>
                    ` : ''}
                </div>
                
                ${opts.showDescription && description ? `
                    <div class="synergy-doc-card-desc">${this.escapeHtml(description)}</div>
                ` : ''}
                
                <div class="synergy-doc-card-meta-detailed">
                    ${opts.showCreated ? `
                        <span>
                            <i class="fas fa-calendar-alt"></i>
                            Created ${createdDate}
                        </span>
                    ` : ''}
                    ${opts.showModified && modifiedDate !== createdDate ? `
                        <span>
                            <i class="fas fa-edit"></i>
                            Modified ${modifiedDate}
                        </span>
                    ` : ''}
                    ${opts.showOwner && owner ? `
                        <span>
                            <i class="fas fa-user"></i>
                            ${this.escapeHtml(owner)}
                        </span>
                    ` : ''}
                    ${opts.showTags && tags ? `
                        <span>
                            <i class="fas fa-tags"></i>
                            ${this.formatTags(tags, opts.maxTags)}
                        </span>
                    ` : ''}
                    ${opts.showSlug && slug ? `
                        <span>
                            <i class="fas fa-tag"></i>
                            ${this.escapeHtml(slug)}
                        </span>
                    ` : ''}
                    ${opts.showSession && sessionId ? `
                        <span>
                            <i class="fas fa-link"></i>
                            Session: ${sessionId.substring(0, 8)}...
                        </span>
                    ` : ''}
                </div>
            </div>
        `;
    },

    /**
     * Render multiple documents as a list
     * 
     * @param {Array} docs - Array of document objects
     * @param {Object} options - Rendering options (same as render())
     * @param {string} options.emptyMessage - Message to show when no docs (default: 'No documents found')
     * @returns {string} HTML string for the document list
     */
    renderList(docs, options = {}) {
        if (!docs || docs.length === 0) {
            const emptyMessage = options.emptyMessage || 'No documents found';
            return `
                <div class="synergy-doc-card-empty">
                    <i class="fas fa-folder-open"></i>
                    <p>${this.escapeHtml(emptyMessage)}</p>
                </div>
            `;
        }

        return docs.map(doc => this.render(doc, options)).join('');
    },

    /**
     * Format date for display
     * @param {string|Date} date - Date to format
     * @returns {string} Formatted date string
     */
    formatDate(date) {
        if (!date) return 'Unknown';

        try {
            const d = new Date(date);
            return d.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch (e) {
            return 'Invalid Date';
        }
    },

    /**
     * Format tags for display
     * @param {string} tags - Comma-separated tags
     * @param {number} maxTags - Maximum number of tags to show
     * @returns {string} Formatted tags string
     */
    formatTags(tags, maxTags = 2) {
        if (!tags) return '';

        const tagArray = tags.split(',').map(t => t.trim()).filter(Boolean);
        const displayed = tagArray.slice(0, maxTags);
        const remaining = tagArray.length - maxTags;

        let result = displayed.join(', ');
        if (remaining > 0) {
            result += ` +${remaining}`;
        }

        return this.escapeHtml(result);
    },

    /**
     * Escape HTML for safe rendering
     * @param {string} text - Text to escape
     * @returns {string} Escaped HTML
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Escape attribute values for safe rendering
     * @param {string} text - Text to escape
     * @returns {string} Escaped attribute value
     */
    escapeAttr(text) {
        if (!text) return '';
        return String(text)
            .replace(/&/g, '&amp;')
            .replace(/'/g, '&#39;')
            .replace(/"/g, '&quot;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }
};

// Make globally available
window.SynergyDocCardRenderer = window.SynergyDocCardRenderer;

console.log('✅ [Synergy Doc Card Renderer] Centralized card renderer loaded');
