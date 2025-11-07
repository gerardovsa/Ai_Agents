/**
 * Stock Table Enhancements
 * =========================
 * Add-on module for stock-management.js
 * Provides row tagging, cell popups, bulk operations, and more
 * 
 * Usage:
 * 1. Include this file AFTER stock-management.js
 * 2. Call StockTableEnhancements.init(stockModule) in your initialize function
 * 3. All features automatically enabled
 * 
 * Features:
 * - Row Tagging System (Green/Orange/Red)
 * - Double-Click Cell Popup
 * - Draggable Popups
 * - Bulk Tag Operations
 * - Shift+Click Range Selection
 * - Row Number Display
 * - Selection Count Display
 * 
 * @created October 30, 2025
 */

const StockTableEnhancements = {
    // Reference to parent module
    module: null,

    // State
    lastCheckedIndex: null,

    /**
     * Initialize enhancements
     * @param {Object} stockModule - Reference to StockManagementModule instance
     */
    init(stockModule) {
        this.module = stockModule;
        console.log('[ENHANCEMENTS] Initializing stock table enhancements...');

        // Add methods to stock module
        this.injectMethods();

        // Add CSS styles
        this.injectStyles();

        console.log('[ENHANCEMENTS] Stock table enhancements ready');
    },

    /**
     * Inject enhancement methods into stock module
     */
    injectMethods() {
        // Row Tagging
        this.module.getRowTag = this.getRowTag.bind(this);
        this.module.toggleRowTag = this.toggleRowTag.bind(this);
        this.module.bulkTagRows = this.bulkTagRows.bind(this);

        // Cell Popup
        this.module.showCellPopup = this.showCellPopup.bind(this);
        this.module.closeCellPopup = this.closeCellPopup.bind(this);
        this.module.copyCellContent = this.copyCellContent.bind(this);
        this.module.makeDraggable = this.makeDraggable.bind(this);
        this.module.escapeHtml = this.escapeHtml.bind(this);

        // Selection
        this.module.updateSelectionCount = this.updateSelectionCount.bind(this);
        this.module.initializeShiftClickSelection = this.initializeShiftClickSelection.bind(this);

        // Table Helpers
        this.module.attachTableEnhancements = this.attachTableEnhancements.bind(this);
        this.module.addTagColumn = this.addTagColumn.bind(this);
        this.module.addRowNumbers = this.addRowNumbers.bind(this);
    },

    /**
     * Inject CSS styles for enhancements
     */
    injectStyles() {
        const styleId = 'stock-table-enhancements-css';
        if (document.getElementById(styleId)) return; // Already injected

        const style = document.createElement('style');
        style.id = styleId;
        style.textContent = `
            /* Tagged Row Styling */
            tr.tagged-row-green,
            .tabulator-row.tagged-row-green {
                border-left: 4px solid #28a745 !important;
                background: rgba(40, 167, 69, 0.05) !important;
            }
            
            tr.tagged-row-orange,
            .tabulator-row.tagged-row-orange {
                border-left: 4px solid #fd7e14 !important;
                background: rgba(253, 126, 20, 0.05) !important;
            }
            
            tr.tagged-row-red,
            .tabulator-row.tagged-row-red {
                border-left: 4px solid #dc3545 !important;
                background: rgba(220, 53, 69, 0.05) !important;
            }
            
            /* Tag Button */
            .tag-btn {
                background: #6c757d;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                transition: all 0.2s;
            }
            
            .tag-btn:hover {
                opacity: 0.8;
            }
            
            .tag-btn.tag-green { background: #28a745; }
            .tag-btn.tag-orange { background: #fd7e14; }
            .tag-btn.tag-red { background: #dc3545; }
            
            /* Cell Popup */
            .cell-popup {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: #21262d;
                border: 2px solid #30363d;
                border-radius: 8px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.5);
                z-index: 10000;
                max-width: 800px;
                max-height: 80vh;
                width: 90%;
                display: flex;
                flex-direction: column;
            }
            
            .cell-popup-header {
                padding: 16px;
                background: #161b22;
                border-bottom: 1px solid #30363d;
                display: flex;
                justify-content: space-between;
                align-items: center;
                cursor: move;
                user-select: none;
            }
            
            .cell-popup-content {
                padding: 20px;
                overflow-y: auto;
                flex: 1;
                color: #c9d1d9;
            }
            
            /* Bulk Operations Toolbar */
            .bulk-operations-toolbar {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px;
                background: #161b22;
                border: 1px solid #30363d;
                border-radius: 6px;
                margin-bottom: 12px;
            }
            
            .selected-count {
                font-size: 14px;
                color: #8b949e;
            }
            
            .bulk-actions {
                display: flex;
                gap: 8px;
            }
            
            /* Table Cell Double-Click Hint */
            td:hover {
                cursor: pointer;
                background: rgba(88, 166, 255, 0.05);
            }
        `;

        document.head.appendChild(style);
    },

    // ============================================================================
    // ROW TAGGING SYSTEM
    // ============================================================================

    /**
     * Get tag color for a stock
     * @param {string|number} stockId - Stock ID
     * @returns {string|null} Tag color ('green', 'orange', 'red', or null)
     */
    getRowTag(stockId) {
        const tags = JSON.parse(localStorage.getItem('stock_row_tags') || '{}');
        return tags[stockId] || null;
    },

    /**
     * Toggle tag color for a stock (cycles: null → green → orange → red → null)
     * @param {Event} event - Click event
     * @param {string|number} stockId - Stock ID
     */
    toggleRowTag(event, stockId) {
        event.stopPropagation();

        const currentTag = this.getRowTag(stockId);
        let nextTag;

        switch (currentTag) {
            case null: nextTag = 'green'; break;
            case 'green': nextTag = 'orange'; break;
            case 'orange': nextTag = 'red'; break;
            case 'red': nextTag = null; break;
            default: nextTag = 'green';
        }

        // Update localStorage
        const tags = JSON.parse(localStorage.getItem('stock_row_tags') || '{}');
        if (nextTag === null) {
            delete tags[stockId];
        } else {
            tags[stockId] = nextTag;
        }
        localStorage.setItem('stock_row_tags', JSON.stringify(tags));

        // Update button visual
        const button = event.currentTarget;
        button.className = `tag-btn ${nextTag ? 'tag-' + nextTag : ''}`;

        // Update row background
        const row = button.closest('tr');
        if (row) {
            row.classList.remove('tagged-row-green', 'tagged-row-orange', 'tagged-row-red');
            if (nextTag) {
                row.classList.add(`tagged-row-${nextTag}`);
            }
        }

        if (this.module && this.module.showNotification) {
            this.module.showNotification(`Stock #${stockId} tagged as ${nextTag || 'untagged'}`, 'success');
        }
    },

    /**
     * Bulk tag multiple selected rows
     * @param {string|null} tagColor - Color to tag ('green', 'orange', 'red', or null to clear)
     */
    bulkTagRows(tagColor) {
        const checkboxes = document.querySelectorAll('.stock-checkbox:checked');

        if (checkboxes.length === 0) {
            if (this.module && this.module.showNotification) {
                this.module.showNotification('No rows selected', 'warning');
            }
            return;
        }

        const tags = JSON.parse(localStorage.getItem('stock_row_tags') || '{}');

        checkboxes.forEach(checkbox => {
            const stockId = checkbox.dataset.stockId || checkbox.value;

            if (tagColor === null) {
                delete tags[stockId];
            } else {
                tags[stockId] = tagColor;
            }

            // Update row visual
            const row = checkbox.closest('tr');
            if (row) {
                row.classList.remove('tagged-row-green', 'tagged-row-orange', 'tagged-row-red');
                if (tagColor) {
                    row.classList.add(`tagged-row-${tagColor}`);
                }
            }

            // Update tag button if exists
            const tagBtn = row?.querySelector('.tag-btn');
            if (tagBtn) {
                tagBtn.className = `tag-btn ${tagColor ? 'tag-' + tagColor : ''}`;
            }
        });

        localStorage.setItem('stock_row_tags', JSON.stringify(tags));

        if (this.module && this.module.showNotification) {
            this.module.showNotification(
                `${checkboxes.length} stocks ${tagColor ? 'tagged ' + tagColor : 'untagged'}`,
                'success'
            );
        }
    },

    // ============================================================================
    // CELL POPUP VIEWER
    // ============================================================================

    /**
     * Show popup with full cell content
     * @param {Event} event - Double-click event
     * @param {string} cellData - Cell content
     * @param {string} fieldName - Field/column name
     */
    showCellPopup(event, cellData, fieldName) {
        // Remove existing popup
        const existingPopup = document.getElementById('cell-popup');
        if (existingPopup) existingPopup.remove();

        if (!cellData) return;

        const popup = document.createElement('div');
        popup.id = 'cell-popup';
        popup.className = 'cell-popup';

        const displayText = String(cellData).substring(0, 50000);
        const charCount = String(cellData).length;
        const tokenCount = Math.ceil(charCount / 4);

        popup.innerHTML = `
            <div class="cell-popup-header" id="popup-header">
                <div>
                    <strong style="font-size: 16px; color: #c9d1d9;">${fieldName}</strong>
                    <div style="font-size: 12px; color: #8b949e; margin-top: 4px;">
                        ${charCount.toLocaleString()} characters | ~${tokenCount.toLocaleString()} tokens
                    </div>
                </div>
                <div style="display: flex; gap: 8px;">
                    <button onclick="stockModule.copyCellContent()" class="btn btn-sm" style="background: #28a745; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer;">
                        <i class="fas fa-copy"></i> Copy
                    </button>
                    <button onclick="stockModule.closeCellPopup()" class="btn btn-sm" style="background: #6c757d; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer;">
                        Close
                    </button>
                </div>
            </div>
            <div class="cell-popup-content">
                <pre style="white-space: pre-wrap; word-wrap: break-word; margin: 0; font-family: monospace; font-size: 13px;">${this.escapeHtml(displayText)}</pre>
            </div>
        `;

        document.body.appendChild(popup);
        popup.dataset.fullContent = String(cellData);
        this.makeDraggable(popup, document.getElementById('popup-header'));
    },

    /**
     * Close cell popup
     */
    closeCellPopup() {
        const popup = document.getElementById('cell-popup');
        if (popup) popup.remove();
    },

    /**
     * Copy cell content to clipboard
     */
    copyCellContent() {
        const popup = document.getElementById('cell-popup');
        if (popup && popup.dataset.fullContent) {
            navigator.clipboard.writeText(popup.dataset.fullContent)
                .then(() => {
                    if (this.module && this.module.showNotification) {
                        this.module.showNotification('Copied to clipboard', 'success');
                    }
                })
                .catch(() => {
                    if (this.module && this.module.showNotification) {
                        this.module.showNotification('Copy failed', 'error');
                    }
                });
        }
    },

    /**
     * Make popup draggable
     * @param {HTMLElement} popup - Popup element
     * @param {HTMLElement} header - Header element to use as drag handle
     */
    makeDraggable(popup, header) {
        let isDragging = false, currentX, currentY, initialX, initialY, xOffset = 0, yOffset = 0;

        header.addEventListener('mousedown', dragStart);
        document.addEventListener('mousemove', drag);
        document.addEventListener('mouseup', dragEnd);

        function dragStart(e) {
            if (e.target.tagName === 'BUTTON' || e.target.closest('button')) return;
            initialX = e.clientX - xOffset;
            initialY = e.clientY - yOffset;
            if (e.target === header || header.contains(e.target)) isDragging = true;
        }

        function drag(e) {
            if (isDragging) {
                e.preventDefault();
                currentX = e.clientX - initialX;
                currentY = e.clientY - initialY;
                xOffset = currentX;
                yOffset = currentY;
                popup.style.transform = `translate(calc(-50% + ${currentX}px), calc(-50% + ${currentY}px))`;
            }
        }

        function dragEnd() {
            initialX = currentX;
            initialY = currentY;
            isDragging = false;
        }
    },

    /**
     * Escape HTML for safe display
     * @param {string} text - Text to escape
     * @returns {string} Escaped HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    // ============================================================================
    // SELECTION & BULK OPERATIONS
    // ============================================================================

    /**
     * Update selection count display
     */
    updateSelectionCount() {
        const checkboxes = document.querySelectorAll('.stock-checkbox:checked');
        const countElement = document.getElementById('selected-count');
        if (countElement) {
            countElement.textContent = `${checkboxes.length} selected`;
        }
    },

    /**
     * Initialize shift+click range selection
     */
    initializeShiftClickSelection() {
        const checkboxes = document.querySelectorAll('.stock-checkbox');

        checkboxes.forEach((checkbox, index) => {
            checkbox.addEventListener('click', (e) => {
                if (e.shiftKey && this.lastCheckedIndex !== null) {
                    // Shift+click range selection
                    const start = Math.min(this.lastCheckedIndex, index);
                    const end = Math.max(this.lastCheckedIndex, index);

                    for (let i = start; i <= end; i++) {
                        checkboxes[i].checked = checkbox.checked;
                    }

                    this.updateSelectionCount();
                }

                this.lastCheckedIndex = index;
                this.updateSelectionCount();
            });
        });
    },

    // ============================================================================
    // TABLE HELPERS
    // ============================================================================

    /**
     * Attach all enhancements to a table
     * @param {HTMLElement} table - Table element
     */
    attachTableEnhancements(table) {
        // Add double-click handlers to cells
        const cells = table.querySelectorAll('td');
        cells.forEach(cell => {
            cell.addEventListener('dblclick', (e) => {
                const cellData = cell.textContent.trim();
                const fieldName = cell.dataset.field || cell.cellIndex.toString();
                if (cellData) {
                    this.showCellPopup(e, cellData, fieldName);
                }
            });
        });

        // Initialize checkboxes
        this.initializeShiftClickSelection();

        // Apply existing tags to rows
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const checkbox = row.querySelector('.stock-checkbox');
            if (checkbox) {
                const stockId = checkbox.dataset.stockId || checkbox.value;
                const tag = this.getRowTag(stockId);
                if (tag) {
                    row.classList.add(`tagged-row-${tag}`);
                }
            }
        });
    },

    /**
     * Add tag column to existing table
     * @param {HTMLElement} table - Table element
     */
    addTagColumn(table) {
        // Add header
        const thead = table.querySelector('thead tr');
        if (thead) {
            const th = document.createElement('th');
            th.style.width = '60px';
            th.style.textAlign = 'center';
            th.textContent = 'Tag';
            thead.insertBefore(th, thead.firstChild.nextSibling); // After checkbox
        }

        // Add cells
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const checkbox = row.querySelector('.stock-checkbox');
            if (checkbox) {
                const stockId = checkbox.dataset.stockId || checkbox.value;
                const tag = this.getRowTag(stockId);

                const td = document.createElement('td');
                td.style.textAlign = 'center';
                td.innerHTML = `
                    <button class="tag-btn ${tag ? 'tag-' + tag : ''}" 
                            onclick="stockModule.toggleRowTag(event, '${stockId}')" 
                            title="Tag Row (Click to cycle)">
                        <i class="fas fa-tag"></i>
                    </button>
                `;

                row.insertBefore(td, row.firstChild.nextSibling); // After checkbox
            }
        });
    },

    /**
     * Add row number column to existing table
     * @param {HTMLElement} table - Table element
     */
    addRowNumbers(table) {
        // Add header
        const thead = table.querySelector('thead tr');
        if (thead) {
            const th = document.createElement('th');
            th.style.width = '50px';
            th.style.textAlign = 'center';
            th.textContent = '#';
            thead.insertBefore(th, thead.firstChild);
        }

        // Add cells
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach((row, index) => {
            const td = document.createElement('td');
            td.style.textAlign = 'center';
            td.textContent = index + 1;
            row.insertBefore(td, row.firstChild);
        });
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = StockTableEnhancements;
}
