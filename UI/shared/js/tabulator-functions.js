/**
 * Tabulator Utility Functions
 * Reusable functions for Tabulator tables across all modules
 * Version: 1.0.0
 * Last Updated: October 30, 2025
 */

// ============================================================================
// ROW TAGGING SYSTEM
// ============================================================================

/**
 * Get the tag color for a specific row by ID
 * @param {string} rowId - Unique identifier for the row
 * @param {string} storageKey - localStorage key (default: 'row_tags')
 * @returns {string|null} - Tag color ('green', 'orange', 'red') or null
 */
function getRowTag(rowId, storageKey = 'row_tags') {
    const tags = JSON.parse(localStorage.getItem(storageKey) || '{}');
    return tags[rowId] || null;
}

/**
 * Set a tag color for a specific row
 * @param {string} rowId - Unique identifier for the row
 * @param {string|null} color - Tag color or null to clear
 * @param {string} storageKey - localStorage key (default: 'row_tags')
 */
function setRowTag(rowId, color, storageKey = 'row_tags') {
    const tags = JSON.parse(localStorage.getItem(storageKey) || '{}');
    
    if (color === null) {
        delete tags[rowId];
    } else {
        tags[rowId] = color;
    }
    
    localStorage.setItem(storageKey, JSON.stringify(tags));
}

/**
 * Remove tag for a specific row
 * @param {string} rowId - Unique identifier for the row
 * @param {string} storageKey - localStorage key (default: 'row_tags')
 */
function removeRowTag(rowId, storageKey = 'row_tags') {
    setRowTag(rowId, null, storageKey);
}

/**
 * Toggle row tag through cycle: untagged → green → orange → red → untagged
 * @param {Event} event - Click event
 * @param {string} rowId - Unique identifier for the row
 * @param {Object} table - Tabulator table instance
 * @param {string} storageKey - localStorage key (default: 'row_tags')
 */
function toggleRowTag(event, rowId, table, storageKey = 'row_tags') {
    event.stopPropagation();
    
    const currentTag = getRowTag(rowId, storageKey);
    let nextTag;
    
    // Cycle: untagged → green → orange → red → untagged
    switch (currentTag) {
        case null:
            nextTag = 'green';
            break;
        case 'green':
            nextTag = 'orange';
            break;
        case 'orange':
            nextTag = 'red';
            break;
        case 'red':
            nextTag = null;
            break;
        default:
            nextTag = 'green';
    }
    
    // Update localStorage
    setRowTag(rowId, nextTag, storageKey);
    
    // Update button visual state
    const button = event.currentTarget || event.target.closest('.action-btn-tag');
    if (button) {
        button.classList.remove('tag-green', 'tag-orange', 'tag-red');
        if (nextTag) {
            button.classList.add(`tag-${nextTag}`);
        }
        
        // Update cell border
        const cell = button.closest('.tabulator-cell');
        if (cell) {
            cell.classList.add('tagged-cell');
            cell.classList.remove('tag-green', 'tag-orange', 'tag-red');
            if (nextTag) {
                cell.classList.add(`tag-${nextTag}`);
            } else {
                cell.classList.remove('tagged-cell');
            }
        }
        
        // Update row background
        const row = button.closest('.tabulator-row');
        if (row) {
            row.classList.remove('tagged-row-green', 'tagged-row-orange', 'tagged-row-red');
            if (nextTag) {
                row.classList.add(`tagged-row-${nextTag}`);
            }
        }
    }
    
    return nextTag;
}

/**
 * Bulk tag selected rows
 * @param {Object} table - Tabulator table instance
 * @param {string|null} tagColor - Tag color or null/'clear' to clear tags
 * @param {string} idField - Field name for row ID (default: 'id')
 * @param {string} storageKey - localStorage key (default: 'row_tags')
 * @returns {number} - Number of rows tagged
 */
function bulkTagRows(table, tagColor, idField = 'id', storageKey = 'row_tags') {
    const selectedRows = table.getSelectedRows();
    
    if (selectedRows.length === 0) {
        return 0;
    }
    
    selectedRows.forEach(row => {
        const rowData = row.getData();
        const rowId = rowData[idField];
        
        // Update localStorage
        if (tagColor === 'clear' || tagColor === null) {
            removeRowTag(rowId, storageKey);
        } else {
            setRowTag(rowId, tagColor, storageKey);
        }
        
        // Update row classes
        row.getElement().classList.remove('tagged-row-green', 'tagged-row-orange', 'tagged-row-red');
        if (tagColor && tagColor !== 'clear') {
            row.getElement().classList.add(`tagged-row-${tagColor}`);
        }
        
        // Update tag button in row
        row.reformat();
    });
    
    return selectedRows.length;
}

/**
 * Row formatter function to apply tag styling
 * @param {Object} row - Tabulator row object
 * @param {string} idField - Field name for row ID (default: 'id')
 * @param {string} storageKey - localStorage key (default: 'row_tags')
 */
function applyRowTagFormatter(row, idField = 'id', storageKey = 'row_tags') {
    const data = row.getData();
    const rowId = data[idField];
    const tagColor = getRowTag(rowId, storageKey);
    
    // Remove all tagged row classes first
    row.getElement().classList.remove('tagged-row-green', 'tagged-row-orange', 'tagged-row-red');
    
    // Add tagged row class if row is tagged
    if (tagColor) {
        row.getElement().classList.add(`tagged-row-${tagColor}`);
    }
}

/**
 * Create tag button formatter for Tabulator column
 * @param {string} idField - Field name for row ID (default: 'id')
 * @param {Object} table - Tabulator table instance
 * @param {string} storageKey - localStorage key (default: 'row_tags')
 * @returns {Function} - Formatter function for Tabulator
 */
function createTagButtonFormatter(idField = 'id', table, storageKey = 'row_tags') {
    return function(cell) {
        const row = cell.getRow().getData();
        const rowId = row[idField];
        const currentTag = getRowTag(rowId, storageKey);
        const tagClass = currentTag ? `tag-${currentTag}` : '';
        
        // Store table reference for the toggle function
        const tableRef = cell.getTable();
        
        return `
            <button class="action-btn action-btn-tag ${tagClass}" 
                    onclick="window.TabulatorFunctions.toggleRowTag(event, '${rowId}', window.tabulatorInstance_${tableRef.element.id}, '${storageKey}')" 
                    title="Tag Row (Click to cycle: Untagged → Green → Orange → Red)">
                <i class="fas fa-tag"></i>
            </button>
        `;
    };
}

// ============================================================================
// CELL POPUP VIEWER
// ============================================================================

/**
 * Show popup with full cell content
 * @param {Event} event - Double-click event
 * @param {Object} cell - Tabulator cell object
 */
function showCellPopup(event, cell) {
    // Remove any existing popup
    const existingPopup = document.getElementById('cell-popup');
    if (existingPopup) {
        existingPopup.remove();
    }
    
    const cellData = cell.getValue();
    const fieldName = cell.getColumn().getField();
    
    // Only show popup for text fields with content
    if (!cellData || fieldName === 'actions') return;
    
    const popup = document.createElement('div');
    popup.id = 'cell-popup';
    popup.className = 'cell-popup';
    
    // Limit to 50,000 characters for performance
    const displayText = String(cellData).substring(0, 50000);
    const charCount = String(cellData).length;
    
    // Calculate approximate token count (rough estimate: ~4 chars per token)
    const tokenCount = Math.ceil(charCount / 4);
    
    popup.innerHTML = `
        <div class="cell-popup-header" id="popup-header">
            <div class="cell-popup-header-left">
                <strong style="font-size: 18px;">${escapeHtml(fieldName)}</strong>
                <span style="font-size: 12px; color: #999;">
                    ${charCount.toLocaleString()} characters | ~${tokenCount.toLocaleString()} tokens
                </span>
            </div>
            <div class="cell-popup-header-buttons">
                <button onclick="window.TabulatorFunctions.copyCellContent('${escapeHtml(fieldName)}')" class="action-btn" style="background: #28a745; padding: 6px 12px; cursor: pointer;">
                    <i class="fas fa-copy"></i> Copy
                </button>
                <button onclick="window.TabulatorFunctions.closeCellPopup()" class="action-btn" style="background: #6c757d; padding: 6px 12px; cursor: pointer;">
                    Close
                </button>
            </div>
        </div>
        <div class="cell-popup-content">
            <pre style="white-space: pre-wrap; word-wrap: break-word; margin: 0; font-family: monospace; font-size: 13px;">${escapeHtml(displayText)}</pre>
        </div>
        <div class="cell-popup-footer"></div>
    `;
    
    document.body.appendChild(popup);
    
    // Store full content for copy function
    popup.dataset.fullContent = String(cellData);
    
    // Position popup (centered by default)
    popup.style.display = 'flex';
    
    // Make popup draggable by header
    makeDraggable(popup, document.getElementById('popup-header'));
}

/**
 * Close cell popup
 */
function closeCellPopup() {
    const popup = document.getElementById('cell-popup');
    if (popup) {
        popup.remove();
    }
}

/**
 * Copy cell content to clipboard
 * @param {string} fieldName - Field name for notification
 */
function copyCellContent(fieldName) {
    const popup = document.getElementById('cell-popup');
    if (popup && popup.dataset.fullContent) {
        navigator.clipboard.writeText(popup.dataset.fullContent)
            .then(() => {
                console.log(`Copied ${fieldName} to clipboard`);
            })
            .catch(err => {
                console.error('Copy failed:', err);
            });
    }
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} - Escaped HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Make element draggable
 * @param {HTMLElement} popup - Popup element
 * @param {HTMLElement} header - Header element (drag handle)
 */
function makeDraggable(popup, header) {
    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;
    let xOffset = 0;
    let yOffset = 0;
    
    header.addEventListener('mousedown', dragStart);
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', dragEnd);
    
    function dragStart(e) {
        // Don't start dragging if clicking on a button
        if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
            return;
        }
        
        initialX = e.clientX - xOffset;
        initialY = e.clientY - yOffset;
        
        if (e.target === header || header.contains(e.target)) {
            isDragging = true;
        }
    }
    
    function drag(e) {
        if (isDragging) {
            e.preventDefault();
            
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
            
            xOffset = currentX;
            yOffset = currentY;
            
            // Update popup position (override centered transform)
            popup.style.transform = `translate(calc(-50% + ${currentX}px), calc(-50% + ${currentY}px))`;
        }
    }
    
    function dragEnd(e) {
        initialX = currentX;
        initialY = currentY;
        isDragging = false;
    }
}

// ============================================================================
// BULK OPERATIONS
// ============================================================================

/**
 * Bulk delete selected rows with confirmation
 * @param {Object} table - Tabulator table instance
 * @param {Function} deleteCallback - Async function to delete rows (receives array of row data)
 * @param {string} confirmMessage - Custom confirmation message
 * @returns {Promise<Object>} - Result object with success status and count
 */
async function bulkDeleteRows(table, deleteCallback, confirmMessage = null) {
    const selectedRows = table.getSelectedRows();
    
    if (selectedRows.length === 0) {
        return { success: false, message: 'No rows selected', count: 0 };
    }
    
    const message = confirmMessage || `Are you sure you want to delete ${selectedRows.length} rows? This cannot be undone.`;
    
    if (!confirm(message)) {
        return { success: false, message: 'Cancelled', count: 0 };
    }
    
    try {
        const rowData = selectedRows.map(row => row.getData());
        const result = await deleteCallback(rowData);
        
        if (result.success) {
            // Remove rows from table
            selectedRows.forEach(row => row.delete());
        }
        
        return result;
    } catch (error) {
        return { success: false, message: error.message, count: 0 };
    }
}

/**
 * Update selection count display
 * @param {Object} table - Tabulator table instance
 * @param {string} elementId - ID of element to update with count
 */
function updateSelectionCount(table, elementId) {
    const selectedRows = table.getSelectedRows();
    const countElement = document.getElementById(elementId);
    
    if (countElement) {
        countElement.textContent = `${selectedRows.length} selected`;
    }
}

// ============================================================================
// COLUMN MANAGEMENT
// ============================================================================

/**
 * Create column title formatter with hide button
 * @param {Object} cell - Tabulator cell object
 * @returns {string} - HTML for column header
 */
function columnTitleWithHideButton(cell) {
    const column = cell.getColumn();
    const title = column.getDefinition().title;
    
    return `
        <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
            <span>${title}</span>
            <button onclick="event.stopPropagation(); window.TabulatorFunctions.hideColumn('${column.getField()}')" 
                    style="background: none; border: none; color: #999; cursor: pointer; padding: 2px 4px; opacity: 0.6; transition: opacity 0.2s;"
                    onmouseover="this.style.opacity='1'"
                    onmouseout="this.style.opacity='0.6'"
                    title="Hide Column">
                <i class="fas fa-eye-slash" style="font-size: 10px;"></i>
            </button>
        </div>
    `;
}

/**
 * Hide a specific column
 * @param {Object} table - Tabulator table instance
 * @param {string} fieldName - Field name of column to hide
 */
function hideColumn(table, fieldName) {
    const column = table.getColumn(fieldName);
    if (column) {
        column.hide();
    }
}

/**
 * Show all columns in table
 * @param {Object} table - Tabulator table instance
 */
function showAllColumns(table) {
    table.getColumns().forEach(col => {
        if (!col.getDefinition().frozen) {
            col.show();
        }
    });
}

/**
 * Create header menu with hide/show options
 * @returns {Array} - Header menu configuration for Tabulator
 */
function createColumnHeaderMenu() {
    return [
        {
            label: "<i class='fas fa-eye-slash'></i> Hide Column",
            action: function(e, column) {
                column.hide();
            }
        },
        {
            separator: true,
        },
        {
            label: "<i class='fas fa-eye'></i> Show All Columns",
            action: function(e, column) {
                const table = column.getTable();
                table.getColumns().forEach(col => {
                    if (!col.getDefinition().frozen) {
                        col.show();
                    }
                });
            }
        },
        {
            separator: true,
        },
        {
            label: "<i class='fas fa-compress'></i> Collapse Column",
            action: function(e, column) {
                const currentWidth = column.getWidth();
                if (currentWidth > 40) {
                    column.setWidth(30);
                    column.updateDefinition({
                        titleFormatter: function(cell) {
                            const title = cell.getValue();
                            return `<div style="writing-mode: vertical-rl; transform: rotate(180deg); white-space: nowrap; height: 100%; display: flex; align-items: center; justify-content: center;">${title}</div>`;
                        }
                    });
                } else {
                    column.setWidth(200);
                    column.updateDefinition({
                        titleFormatter: undefined
                    });
                }
            }
        },
        {
            label: "<i class='fas fa-expand'></i> Expand Column",
            action: function(e, column) {
                column.setWidth(200);
                column.updateDefinition({
                    titleFormatter: undefined
                });
            }
        }
    ];
}

// ============================================================================
// ENHANCED SELECTION
// ============================================================================

/**
 * Setup enhanced cell click for checkbox column
 * Allows clicking anywhere in the checkbox cell to toggle selection
 * @param {Object} table - Tabulator table instance
 */
function setupEnhancedCheckboxClick(table) {
    table.on("cellClick", function(e, cell) {
        const column = cell.getColumn();
        const field = column.getField();
        
        // If clicking on the row selection cell (checkbox column)
        if (field === undefined && column.getDefinition().formatter === "rowSelection") {
            const row = cell.getRow();
            
            // Only toggle on normal click (let Tabulator handle shift+click)
            if (!e.shiftKey) {
                row.toggleSelect();
            }
        }
    });
}

/**
 * Setup selection count updater
 * @param {Object} table - Tabulator table instance
 * @param {string} elementId - ID of element to display count
 */
function setupSelectionCounter(table, elementId) {
    table.on("rowSelectionChanged", function(data, rows) {
        updateSelectionCount(table, elementId);
    });
}

// ============================================================================
// VIEW FULL ROW
// ============================================================================

/**
 * View full row data as JSON popup
 * @param {Object} table - Tabulator table instance
 * @param {string} rowId - Row identifier
 * @param {string} idField - Field name for row ID (default: 'id')
 */
function viewFullRow(table, rowId, idField = 'id') {
    const rowData = table.getData().find(r => r[idField] === rowId);
    
    if (!rowData) {
        console.error('Row not found:', rowId);
        return;
    }
    
    // Create a formatted JSON view
    const jsonContent = JSON.stringify(rowData, null, 2);
    
    // Remove any existing popup
    const existingPopup = document.getElementById('cell-popup');
    if (existingPopup) {
        existingPopup.remove();
    }
    
    const popup = document.createElement('div');
    popup.id = 'cell-popup';
    popup.className = 'cell-popup';
    
    // Calculate token count (rough estimate: 4 chars ≈ 1 token)
    const charCount = jsonContent.length;
    const estimatedTokens = Math.ceil(charCount / 4);
    
    popup.innerHTML = `
        <div class="cell-popup-header" id="popup-header">
            <div class="cell-popup-header-left">
                <strong style="font-size: 18px;">Full Row Data: ${rowId}</strong>
                <span style="font-size: 12px; color: #999;">(${Object.keys(rowData).length} fields, ${charCount.toLocaleString()} chars, ~${estimatedTokens.toLocaleString()} tokens)</span>
            </div>
            <div class="cell-popup-header-buttons">
                <button onclick="window.TabulatorFunctions.copyFullRowData()" class="action-btn" style="background: #28a745; padding: 6px 12px;">
                    <i class="fas fa-copy"></i> Copy JSON
                </button>
                <button onclick="window.TabulatorFunctions.closeCellPopup()" class="action-btn" style="background: #6c757d; padding: 6px 12px;">
                    Close
                </button>
            </div>
        </div>
        <div class="cell-popup-content">
            <pre style="white-space: pre-wrap; word-wrap: break-word; margin: 0; font-family: monospace; font-size: 13px;">${escapeHtml(jsonContent)}</pre>
        </div>
        <div class="cell-popup-footer"></div>
    `;
    
    document.body.appendChild(popup);
    
    // Store full content for copy function
    popup.dataset.fullContent = jsonContent;
    
    // Position popup (centered)
    popup.style.display = 'flex';
    
    // Make draggable
    makeDraggable(popup, document.getElementById('popup-header'));
}

/**
 * Copy full row data to clipboard
 */
function copyFullRowData() {
    const popup = document.getElementById('cell-popup');
    if (popup && popup.dataset.fullContent) {
        navigator.clipboard.writeText(popup.dataset.fullContent)
            .then(() => {
                console.log('Copied full row data to clipboard');
            })
            .catch(err => {
                console.error('Copy failed:', err);
            });
    }
}

// ============================================================================
// EXPORT FUNCTIONS TO WINDOW
// ============================================================================

window.TabulatorFunctions = {
    // Row Tagging
    getRowTag,
    setRowTag,
    removeRowTag,
    toggleRowTag,
    bulkTagRows,
    applyRowTagFormatter,
    createTagButtonFormatter,
    
    // Cell Popup
    showCellPopup,
    closeCellPopup,
    copyCellContent,
    escapeHtml,
    makeDraggable,
    
    // Bulk Operations
    bulkDeleteRows,
    updateSelectionCount,
    
    // Column Management
    columnTitleWithHideButton,
    hideColumn,
    showAllColumns,
    createColumnHeaderMenu,
    
    // Enhanced Selection
    setupEnhancedCheckboxClick,
    setupSelectionCounter,
    
    // View Full Row
    viewFullRow,
    copyFullRowData
};

console.log('Tabulator utility functions loaded');
