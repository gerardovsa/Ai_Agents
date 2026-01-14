/**
 * FILE: UI/modules/internal_docs/internal-docs-additional.js
 * PURPOSE: Additional methods for internal docs (extends synergyBoard)
 * 
 * IMPORTANT: This file contains methods that should be added to synergyBoard object
 * These are legacy methods that integrate with the Synergy platform
 * 
 * USAGE: Include after synergyBoard is defined in business-ai-platform-v2.html
 */

// Extend synergyBoard with internal docs methods
if (typeof synergyBoard !== 'undefined') {

    // ==================== INTERNAL DOCUMENT POPUP MANAGEMENT ====================

    /**
     * Create a new internal document with type selection
     * @param {string} sessionId - Session ID to link the document to
     */
    synergyBoard.createInternalDoc = async function (sessionId) {
        console.log(' Creating new internal document for session:', sessionId);

        // Get current user email (from profile or default)
        const userEmail = window.currentUserEmail || 'user@example.com';
        const timestamp = new Date().toLocaleString();

        // Create popup window with metadata form
        const popupId = `doc-new-${Date.now()}`;
        const popup = this.createPopupWindow(popupId, 'Create Internal Document', 600, 650);

        // Add comprehensive creation form
        popup.bodyElement.innerHTML = `
                    <div style="padding: 24px; overflow-y: auto;">
                        <div class="form-group">
                            <label for="doc-title-input">Title *</label>
                            <input type="text" id="doc-title-input" class="form-control" placeholder="Enter document title" value="" required>
                        </div>

                        <div class="form-group">
                            <label>Created By</label>
                            <input type="text" class="form-control" value="${userEmail}" readonly style="background: var(--bg-tertiary); cursor: not-allowed;">
                        </div>

                        <div class="form-group">
                            <label>Created At</label>
                            <input type="text" class="form-control" value="${timestamp}" readonly style="background: var(--bg-tertiary); cursor: not-allowed;">
                        </div>

                        <div class="form-group">
                            <label for="doc-description-input">Description</label>
                            <textarea id="doc-description-input" class="form-control" rows="3" placeholder="Brief description of this document"></textarea>
                        </div>

                        <div class="form-group">
                            <label for="doc-tags-input">Tags</label>
                            <input type="text" id="doc-tags-input" class="form-control" placeholder="e.g., invoice, draft, urgent (comma-separated)">
                        </div>

                        <div class="form-group">
                            <label>Document Type *</label>
                            <div class="doc-type-options" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 8px;">
                                <div class="doc-type-option" id="doc-type-richtext" onclick="document.querySelectorAll('.doc-type-option').forEach(el => el.classList.remove('selected')); this.classList.add('selected');" style="cursor: pointer; padding: 16px; background: var(--bg-tertiary); border: 2px solid var(--border-default); border-radius: 8px; text-align: center; transition: all 0.2s;">
                                    <i class="fas fa-file-alt" style="font-size: 24px; color: var(--accent-primary); margin-bottom: 8px;"></i>
                                    <div style="font-weight: 600; font-size: 14px; color: var(--text-primary);">Rich Text</div>
                                    <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">Formatted documents</div>
                                </div>
                                <div class="doc-type-option" id="doc-type-spreadsheet" onclick="document.querySelectorAll('.doc-type-option').forEach(el => el.classList.remove('selected')); this.classList.add('selected');" style="cursor: pointer; padding: 16px; background: var(--bg-tertiary); border: 2px solid var(--border-default); border-radius: 8px; text-align: center; transition: all 0.2s;">
                                    <i class="fas fa-table" style="font-size: 24px; color: var(--accent-primary); margin-bottom: 8px;"></i>
                                    <div style="font-weight: 600; font-size: 14px; color: var(--text-primary);">Spreadsheet</div>
                                    <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">Data tables with formulas</div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

        // Select rich text by default
        setTimeout(() => {
            document.getElementById('doc-type-richtext').classList.add('selected');
        }, 10);

        // Add footer buttons
        popup.footerRightElement.innerHTML = `
                    <button class="popup-action-btn" onclick="synergyBoard.closePopup('${popupId}')">
                        <i class="fas fa-times"></i>
                        Cancel
                    </button>
                    <button class="popup-action-btn primary" onclick="synergyBoard.submitNewDocument('${sessionId}', '${popupId}')">
                        <i class="fas fa-plus"></i>
                        Create Document
                    </button>
                `;

        // Show popup centered
        this.showPopup(popupId);
    },

        /**
         * Submit new document creation with metadata
         */
        async submitNewDocument(sessionId, popupId) {
        const title = document.getElementById('doc-title-input').value.trim();
        const description = document.getElementById('doc-description-input').value.trim();
        const tags = document.getElementById('doc-tags-input').value.trim();

        // Get selected type
        const docType = document.querySelector('.doc-type-option.selected')?.id.includes('spreadsheet') ? 'spreadsheet' : 'richtext';

        // Validate
        if (!title) {
            alert('Please enter a document title');
            return;
        }

        console.log(` Creating ${docType} document:`, { title, description, tags });

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-ID': '1'
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    title: title,
                    content: description ? `# ${title}\n\n${description}\n\n` : `# ${title}\n\n`,
                    content_json: docType === 'richtext' ? '{"type":"doc","content":[]}' : '[["A1","B1","C1"],["A2","B2","C2"]]',
                    doc_type: docType,
                    format: docType === 'richtext' ? 'markdown' : 'json',
                    tags: tags
                })
            });

            const data = await response.json();

            if (data.success) {
                console.log('✅ Document created:', data.doc_id);
                this.closePopup(popupId);
                await this.openInternalDocPopup(data.doc_id, sessionId);
                await this.loadSessions();
                this.renderAllCards();
            } else {
                alert('Failed to create document: ' + data.error);
            }
        } catch (error) {
            console.error('Error creating document:', error);
            alert('Failed to create document');
        }
    };

    /**
     * Submit new document creation with metadata
     */
    synergyBoard.submitNewDocument = async function (sessionId, popupId) {
        const title = document.getElementById('doc-title-input').value.trim();
        const description = document.getElementById('doc-description-input').value.trim();
        const tags = document.getElementById('doc-tags-input').value.trim();

        // Get selected type
        const docType = document.querySelector('.doc-type-option.selected')?.id.includes('spreadsheet') ? 'spreadsheet' : 'richtext';

        // Validate
        if (!title) {
            alert('Please enter a document title');
            return;
        }

        console.log(` Creating ${docType} document:`, { title, description, tags });

        try {
            const response = await fetch(`${synergyBoard.apiBaseUrl}/api/synergy/internal-doc/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-ID': '1'
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    title: title,
                    content: description ? `# ${title}\n\n${description}\n\n` : `# ${title}\n\n`,
                    content_json: docType === 'richtext' ? '{"type":"doc","content":[]}' : '[["A1","B1","C1"],["A2","B2","C2"]]',
                    doc_type: docType,
                    format: docType === 'richtext' ? 'markdown' : 'json',
                    tags: tags
                })
            });

            const data = await response.json();

            if (data.success) {
                console.log('✅ Document created:', data.doc_id);
                synergyBoard.closePopup(popupId);
                await synergyBoard.openInternalDocPopup(data.doc_id, sessionId);
                await synergyBoard.loadSessions();
                synergyBoard.renderAllCards();
            } else {
                alert('Failed to create document: ' + data.error);
            }
        } catch (error) {
            console.error('Error creating document:', error);
            alert('Failed to create document');
        }
    };



    /**
     * INTERNAL DOCUMENT METHODS - Delegated to internalDocsManager module
     * These methods are now handled by modules/internal_docs/manager.js
     * References remain here for backward compatibility
     */

    synergyBoard.attachExistingDoc = async function (sessionId) {
        // Delegate to internalDocsManager module
        if (window.internalDocsManager) {
            return window.internalDocsManager.attachExistingDoc(sessionId);
        }
        console.error('internalDocsManager not loaded');
    };

    synergyBoard.openInternalDocPopup = async function (docId, sessionId) {
        // Delegate to internalDocsManager module
        if (window.internalDocsManager) {
            return window.internalDocsManager.openInternalDocPopup(docId, sessionId);
        }
        console.error('internalDocsManager not loaded');
    }
};

synergyBoard.updateDocumentTitle = async function (docId, newTitle, inputElement) {
    // Delegate to internalDocsManager module  
    if (window.internalDocsManager) {
        return window.internalDocsManager.updateDocumentTitle(docId, newTitle);
    }
    console.error('internalDocsManager not loaded');
};

synergyBoard.updateDocumentDescription = async function (docId, newDescription) {
    // Delegate to internalDocsManager module
    if (window.internalDocsManager) {
        return window.internalDocsManager.updateDocumentDescription(docId, newDescription);
    }
    console.error('internalDocsManager not loaded');
};

// END OF DELEGATED METHODS - Original implementations removed to avoid conflicts



// ==================== SPREADSHEET HELPERS ====================

/**
 * Update spreadsheet cell
 */
synergyBoard.updateSpreadsheetCell = function (docId, row, col, value) {
    const data = window[`spreadsheet_data_${docId}`];
    if (data && data[row]) {
        data[row][col] = value;
        console.log(`Updated cell [${row}][${col}] = ${value}`);
    }
};

/**
 * Save spreadsheet data
 */
synergyBoard.saveSpreadsheetData = async function (docId) {
    const data = window[`spreadsheet_data_${docId}`];
    if (!data) {
        alert('No spreadsheet data to save');
        return;
    }

    try {
        const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/${docId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-User-ID': '1'
            },
            body: JSON.stringify({
                content_json: JSON.stringify(data),
                content: JSON.stringify(data)
            })
        });

        const result = await response.json();

        if (result.success) {
            console.log('✅ Spreadsheet saved');
            alert('Spreadsheet saved successfully!');
            await this.loadSessions();
            this.renderAllCards();
        } else {
            alert('Failed to save: ' + result.error);
        }
    } catch (error) {
        console.error('Error saving spreadsheet:', error);
        alert('Failed to save spreadsheet');
    }
};

/**
 * Add spreadsheet row
 */
synergyBoard.addSpreadsheetRow = function (docId) {
    const data = window[`spreadsheet_data_${docId}`];
    if (data) {
        const newRow = Array(data[0]?.length || 3).fill('');
        data.push(newRow);
        // Refresh spreadsheet view
        alert('Row added! Save to persist changes.');
    }
};

/**
 * Add spreadsheet column
 */
synergyBoard.addSpreadsheetColumn = function (docId) {
    const data = window[`spreadsheet_data_${docId}`];
    if (data) {
        data.forEach(row => row.push(''));
        alert('Column added! Save to persist changes.');
    }
};

/**
 * Delete spreadsheet row
 */
synergyBoard.deleteSpreadsheetRow = function (docId) {
    const data = window[`spreadsheet_data_${docId}`];
    const rowIndex = prompt('Enter row number to delete (0-based):');
    if (rowIndex !== null && data && data[parseInt(rowIndex)]) {
        data.splice(parseInt(rowIndex), 1);
        alert('Row deleted! Save to persist changes.');
    }
};

/**
 * Delete spreadsheet column
 */
synergyBoard.deleteSpreadsheetColumn = function (docId) {
    const data = window[`spreadsheet_data_${docId}`];
    const colIndex = prompt('Enter column number to delete (0-based):');
    if (colIndex !== null && data) {
        data.forEach(row => row.splice(parseInt(colIndex), 1));
        alert('Column deleted! Save to persist changes.');
    }
};

/**
 * Sort spreadsheet
 */
synergyBoard.sortSpreadsheet = function (docId, direction) {
    alert(`Sort ${direction} feature coming soon!`);
};

/**
 * Toggle spreadsheet filter
 */
synergyBoard.toggleSpreadsheetFilter = function (docId) {
    alert('Filter feature coming soon!');
};

/**
 * Format spreadsheet cells
 */
synergyBoard.formatSpreadsheetCells = function (docId, format) {
    alert(`Format as ${format} feature coming soon!`);
};

// ==================== POPUP WINDOW MANAGEMENT ====================

// Initialize popup tracking objects if not already present
if (!synergyBoard.popupWindows) {
    synergyBoard.popupWindows = {};
}
if (!synergyBoard.popupZIndex) {
    synergyBoard.popupZIndex = 9000;
}

/**
 * Create a floating popup window
 * @param {string} id - Unique popup ID
 * @param {string} title - Window title
 * @param {number} width - Window width in pixels
 * @param {number} height - Window height in pixels
 * @returns {Object} Popup object with element references
 */
synergyBoard.createPopupWindow = function (id, title, width = 800, height = 600) {
    const container = document.getElementById('internalDocPopupContainer');

    // Check if popup already exists
    if (this.popupWindows[id]) {
        this.showPopup(id);
        return this.popupWindows[id];
    }

    // Calculate centered position
    const left = (window.innerWidth - width) / 2;
    const top = (window.innerHeight - height) / 2;

    // Create popup HTML
    const popupHTML = `
                    <div class="internal-doc-popup" id="${id}" style="width: ${width}px; height: ${height}px; left: ${left}px; top: ${top}px;">
                        <!-- Resize handles -->
                        <div class="popup-resize-handle n"></div>
                        <div class="popup-resize-handle s"></div>
                        <div class="popup-resize-handle e"></div>
                        <div class="popup-resize-handle w"></div>
                        <div class="popup-resize-handle ne"></div>
                        <div class="popup-resize-handle nw"></div>
                        <div class="popup-resize-handle se"></div>
                        <div class="popup-resize-handle sw"></div>

                        <!-- Header -->
                        <div class="internal-doc-popup-header">
                            <div class="internal-doc-popup-title">
                                ${title}
                            </div>
                            <div class="internal-doc-popup-controls">
                                <button class="popup-control-btn minimize" title="Minimize" onclick="synergyBoard.toggleCollapse('${id}')">
                                    <i class="fas fa-minus"></i>
                                </button>
                                <button class="popup-control-btn maximize" title="Maximize" onclick="synergyBoard.toggleMaximize('${id}')">
                                    <i class="fas fa-expand"></i>
                                </button>
                                <button class="popup-control-btn close" title="Close" onclick="synergyBoard.closePopup('${id}')">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                        </div>

                        <!-- Body -->
                        <div class="internal-doc-popup-body">
                            <!-- Content will be dynamically added here -->
                        </div>

                        <!-- Footer -->
                        <div class="internal-doc-popup-footer">
                            <div class="popup-footer-left">
                                <!-- Status indicators -->
                            </div>
                            <div class="popup-footer-right">
                                <!-- Action buttons -->
                            </div>
                        </div>
                    </div>
                `;

    // Add to container
    container.insertAdjacentHTML('beforeend', popupHTML);

    // Get element references
    const popupElement = document.getElementById(id);
    const headerElement = popupElement.querySelector('.internal-doc-popup-header');
    const titleElement = popupElement.querySelector('.internal-doc-popup-title');
    const bodyElement = popupElement.querySelector('.internal-doc-popup-body');
    const footerElement = popupElement.querySelector('.internal-doc-popup-footer');
    const footerLeftElement = popupElement.querySelector('.popup-footer-left');
    const footerRightElement = popupElement.querySelector('.popup-footer-right');

    // Store popup object
    const popup = {
        id,
        popupElement,
        headerElement,
        titleElement,
        bodyElement,
        footerElement,
        footerLeftElement,
        footerRightElement,
        width,
        height,
        left,
        top,
        isCollapsed: false,
        isMaximized: false
    };

    this.popupWindows[id] = popup;

    // Initialize dragging
    this.initPopupDrag(popup);

    // Initialize resizing
    this.initPopupResize(popup);

    return popup;
};

/**
 * Show popup window
 */
synergyBoard.showPopup = function (id) {
    const popup = this.popupWindows[id];
    if (!popup) return;

    popup.popupElement.classList.add('active', 'animating');
    popup.popupElement.style.zIndex = ++this.popupZIndex;

    // Remove animation class after animation completes
    setTimeout(() => {
        popup.popupElement.classList.remove('animating');
    }, 300);
},

    /**
     * Close popup window
     */
    async closePopup(id) {
    const popup = this.popupWindows[id];
    if (!popup) return;

    // Auto-save document content before closing
    await this.autoSavePopupContent(id, popup);

    popup.popupElement.classList.remove('active');

    // Remove from DOM after fade out
    setTimeout(() => {
        popup.popupElement.remove();
        delete this.popupWindows[id];
    }, 200);
},

            /**
             * Toggle collapse state
             */
            async toggleCollapse(id) {
    const popup = this.popupWindows[id];
    if (!popup) return;

    // Auto-save before collapsing
    if (!popup.isCollapsed) {
        await this.autoSavePopupContent(id, popup);
    }

    popup.isCollapsed = !popup.isCollapsed;
    popup.popupElement.classList.toggle('collapsed', popup.isCollapsed);

    // Update icon
    const icon = popup.headerElement.querySelector('.minimize i');
    icon.className = popup.isCollapsed ? 'fas fa-plus' : 'fas fa-minus';
},

            /**
             * Toggle maximize state
             */
            async toggleMaximize(id) {
    const popup = this.popupWindows[id];
    if (!popup) return;

    // Auto-save before maximizing/restoring
    await this.autoSavePopupContent(id, popup);

    popup.isMaximized = !popup.isMaximized;
    popup.popupElement.classList.toggle('maximized', popup.isMaximized);

    // Update icon
    const icon = popup.headerElement.querySelector('.maximize i');
    icon.className = popup.isMaximized ? 'fas fa-compress' : 'fas fa-expand';
},

/**
 * Initialize dragging for popup
 */
initPopupDrag(popup) {
    let isDragging = false;
    let dragOffsetX = 0;
    let dragOffsetY = 0;

    // Only allow dragging from header area, not title
    popup.headerElement.addEventListener('mousedown', (e) => {
        // Don't drag if clicking buttons or title
        if (e.target.closest('.popup-control-btn')) return;
        if (e.target.closest('.internal-doc-popup-title')) return;
        if (popup.isMaximized) return;

        isDragging = true;
        dragOffsetX = e.clientX - popup.popupElement.offsetLeft;
        dragOffsetY = e.clientY - popup.popupElement.offsetTop;

        popup.popupElement.style.zIndex = ++this.popupZIndex;
        popup.popupElement.classList.add('dragging');
        popup.headerElement.classList.add('draggable-area');

        e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;

        const newLeft = e.clientX - dragOffsetX;
        const newTop = e.clientY - dragOffsetY;

        popup.popupElement.style.left = `${newLeft}px`;
        popup.popupElement.style.top = `${newTop}px`;
    });

    document.addEventListener('mouseup', () => {
        if (isDragging) {
            popup.popupElement.classList.remove('dragging');
            popup.headerElement.classList.remove('draggable-area');
        }
        isDragging = false;
    });

    // Make title editable on double-click
    popup.titleElement.addEventListener('dblclick', (e) => {
        e.stopPropagation();
        popup.titleElement.setAttribute('contenteditable', 'true');
        popup.titleElement.focus();

        // Select all text
        const range = document.createRange();
        range.selectNodeContents(popup.titleElement);
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
    });

    // Handle title editing blur/enter
    popup.titleElement.addEventListener('blur', async () => {
        popup.titleElement.removeAttribute('contenteditable');
        // Auto-save when title is edited
        await this.autoSavePopupContent(id, popup);
    });

    popup.titleElement.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            popup.titleElement.blur();
        }
        if (e.key === 'Escape') {
            e.preventDefault();
            popup.titleElement.blur();
        }
    });
},

            /**
             * Auto-save popup content (document or spreadsheet)
             */
            async autoSavePopupContent(popupId, popup) {
    // Extract docId from popup ID (format: "doc-{docId}")
    if (!popupId.startsWith('doc-')) return;

    const docId = popupId.replace('doc-', '');

    // Check if there's an editor in the popup
    const editor = popup.bodyElement.querySelector('.tiptap-editor');
    const spreadsheet = popup.bodyElement.querySelector('.spreadsheet-wrapper table');

    if (editor) {
        // Rich text document - save HTML content
        const content = editor.innerHTML;
        console.log(`[AUTOSAVE] Saving document ${docId} before state change...`);

        try {
            await this.saveDocumentContent(docId, content, popup);
            console.log(`? [AUTOSAVE] Document ${docId} saved successfully`);
        } catch (error) {
            console.error(`? [AUTOSAVE] Failed to save document ${docId}:`, error);
        }
    } else if (spreadsheet) {
        // Spreadsheet - save table data
        console.log(`[AUTOSAVE] Saving spreadsheet ${docId} before state change...`);

        try {
            // Extract spreadsheet data from table
            const data = this.extractSpreadsheetData(spreadsheet);
            await this.saveSpreadsheetContent(docId, data, popup);
            console.log(`? [AUTOSAVE] Spreadsheet ${docId} saved successfully`);
        } catch (error) {
            console.error(`? [AUTOSAVE] Failed to save spreadsheet ${docId}:`, error);
        }
    }
},

/**
 * Extract data from spreadsheet table
 */
extractSpreadsheetData(table) {
    const data = [];
    const rows = table.querySelectorAll('tr');

    rows.forEach(row => {
        const rowData = [];
        const cells = row.querySelectorAll('th, td');
        cells.forEach(cell => {
            rowData.push(cell.textContent.trim());
        });
        data.push(rowData);
    });

    return data;
},

            /**
             * Save spreadsheet content
             */
            async saveSpreadsheetContent(docId, data, popup = null) {
    try {
        const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/${docId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-User-ID': '1'
            },
            body: JSON.stringify({
                content_json: data
            })
        });

        const result = await response.json();

        if (result.success) {
            console.log('? Spreadsheet saved:', docId);
            if (popup && popup.footerLeftElement) {
                const saveStatus = popup.footerLeftElement.querySelector('.save-status');
                if (saveStatus) {
                    saveStatus.className = 'save-status saved';
                    const statusText = saveStatus.querySelector('span');
                    if (statusText) statusText.textContent = 'Saved';
                }
            }
        } else {
            console.error('Failed to save spreadsheet:', result.error);
            if (popup && popup.footerLeftElement) {
                const saveStatus = popup.footerLeftElement.querySelector('.save-status');
                if (saveStatus) {
                    saveStatus.className = 'save-status error';
                    const statusText = saveStatus.querySelector('span');
                    if (statusText) statusText.textContent = 'Error';
                }
            }
        }
    } catch (error) {
        console.error('Error saving spreadsheet:', error);
    }
},

/**
 * Initialize resizing for popup
 */
initPopupResize(popup) {
    const handles = popup.popupElement.querySelectorAll('.popup-resize-handle');

    handles.forEach(handle => {
        let isResizing = false;
        let startX, startY, startWidth, startHeight, startLeft, startTop;
        const direction = handle.className.split(' ')[1];

        handle.addEventListener('mousedown', (e) => {
            if (popup.isMaximized) return;

            isResizing = true;
            startX = e.clientX;
            startY = e.clientY;
            startWidth = popup.popupElement.offsetWidth;
            startHeight = popup.popupElement.offsetHeight;
            startLeft = popup.popupElement.offsetLeft;
            startTop = popup.popupElement.offsetTop;

            e.preventDefault();
            e.stopPropagation();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;

            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;

            // Handle different resize directions
            if (direction.includes('e')) {
                popup.popupElement.style.width = `${Math.max(400, startWidth + deltaX)}px`;
            }
            if (direction.includes('w')) {
                const newWidth = Math.max(400, startWidth - deltaX);
                popup.popupElement.style.width = `${newWidth}px`;
                popup.popupElement.style.left = `${startLeft + (startWidth - newWidth)}px`;
            }
            if (direction.includes('s')) {
                popup.popupElement.style.height = `${Math.max(300, startHeight + deltaY)}px`;
            }
            if (direction.includes('n')) {
                const newHeight = Math.max(300, startHeight - deltaY);
                popup.popupElement.style.height = `${newHeight}px`;
                popup.popupElement.style.top = `${startTop + (startHeight - newHeight)}px`;
            }
        });

        document.addEventListener('mouseup', () => {
            isResizing = false;
        });
    });
}
    };

// ==================== INTERNAL DOC VIEWER/EDITOR METHODS ====================

/**
 * Open internal document viewer/editor
 */
synergyBoard.openInternalDocViewer = function (docId, sessionId) {
    // Fetch document
    fetch(`/api/synergy/internal-doc/${docId}`)
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                alert('Failed to load document: ' + data.error);
                return;
            }

            // Show modal
            const modal = document.createElement('div');
            modal.className = 'modal-overlay';
            modal.id = 'internal-doc-modal';
            modal.innerHTML = `
                    <div class="modal-content internal-doc-modal">
                        <div class="modal-header">
                            <div class="header-title-row">
                                <h3>
                                    <i class="fas fa-file-alt"></i>
                                    <input type="text" id="doc-title" value="${synergyBoard.escapeHtml(data.title)}" 
                                           class="doc-title-input" />
                                </h3>
                                <button class="btn-copy-id" onclick="synergyBoard.copyDocIdToClipboard('${docId}')" title="Copy Doc ID to Clipboard">
                                    <i class="fas fa-copy"></i> ${docId}
                                </button>
                            </div>
                            <div class="doc-meta">
                                <span><i class="fas fa-code"></i> ${data.format}</span>
                                <span><i class="fas fa-layer-group"></i> v${data.version}</span>
                                <span><i class="fas fa-calendar"></i> ${new Date(data.updated_at).toLocaleString()}</span>
                                <span><i class="fas fa-user"></i> ${data.created_by}</span>
                            </div>
                            <button class="modal-close" onclick="synergyBoard.closeInternalDocModal()">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        
                        <div class="modal-body">
                            <div class="doc-editor-container">
                                ${data.format === 'markdown' ? `
                                    <div class="editor-tabs">
                                        <button class="tab-btn active" onclick="synergyBoard.switchDocTab('edit')">
                                            <i class="fas fa-edit"></i> Edit
                                        </button>
                                        <button class="tab-btn" onclick="synergyBoard.switchDocTab('preview')">
                                            <i class="fas fa-eye"></i> Preview
                                        </button>
                                    </div>
                                    <textarea id="doc-content" class="doc-editor markdown-editor">${synergyBoard.escapeHtml(data.content)}</textarea>
                                    <div id="doc-preview" class="doc-preview markdown-content" style="display: none;"></div>
                                ` : `
                                    <div contenteditable="true" id="doc-content" class="doc-editor html-editor">${data.content}</div>
                                `}
                            </div>
                        </div>
                        
                        <div class="modal-footer">
                            <div class="footer-left">
                                <button class="btn-secondary btn-export" onclick="synergyBoard.exportInternalDoc('${docId}', 'word')">
                                    <i class="fab fa-microsoft"></i> Word
                                </button>
                                <button class="btn-secondary btn-export" onclick="synergyBoard.exportInternalDoc('${docId}', 'google_doc')">
                                    <i class="fab fa-google"></i> Google Doc
                                </button>
                                <button class="btn-secondary btn-export" onclick="synergyBoard.exportInternalDoc('${docId}', 'pdf')">
                                    <i class="fas fa-file-pdf"></i> PDF
                                </button>
                                <button class="btn-secondary btn-export" onclick="synergyBoard.exportInternalDoc('${docId}', 'email')">
                                    <i class="fas fa-envelope"></i> Email
                                </button>
                            </div>
                            <div class="footer-right">
                                <button class="btn-secondary" onclick="synergyBoard.closeInternalDocModal()">
                                    <i class="fas fa-times"></i> Cancel
                                </button>
                                <button class="btn-primary" onclick="synergyBoard.saveInternalDoc('${docId}')">
                                    <i class="fas fa-save"></i> Save Changes
                                </button>
                            </div>
                        </div>
                    </div>
                `;

            document.body.appendChild(modal);

            // Auto-save every 30 seconds
            synergyBoard.docAutoSaveInterval = setInterval(() => {
                synergyBoard.saveInternalDoc(docId, true);
            }, 30000);
        })
        .catch(err => {
            console.error('Error loading document:', err);
            alert('Failed to load document');
        });
};

synergyBoard.closeInternalDocModal = function () {
    const modal = document.getElementById('internal-doc-modal');
    if (modal) {
        modal.remove();
    }
    if (synergyBoard.docAutoSaveInterval) {
        clearInterval(synergyBoard.docAutoSaveInterval);
        synergyBoard.docAutoSaveInterval = null;
    }
};

synergyBoard.switchDocTab = function (tab) {
    const editBtn = document.querySelector('.editor-tabs .tab-btn:nth-child(1)');
    const previewBtn = document.querySelector('.editor-tabs .tab-btn:nth-child(2)');
    const editor = document.getElementById('doc-content');
    const preview = document.getElementById('doc-preview');

    if (tab === 'edit') {
        editBtn.classList.add('active');
        previewBtn.classList.remove('active');
        editor.style.display = 'block';
        preview.style.display = 'none';
    } else {
        editBtn.classList.remove('active');
        previewBtn.classList.add('active');
        editor.style.display = 'none';
        preview.style.display = 'block';

        // Render markdown preview
        preview.innerHTML = synergyBoard.renderMarkdown(editor.value);
    }
};

synergyBoard.saveInternalDoc = function (docId, isAutoSave = false) {
    const title = document.getElementById('doc-title')?.value;
    const contentElem = document.getElementById('doc-content');
    if (!contentElem) return;

    const content = contentElem.value || contentElem.innerHTML;

    fetch(`/api/synergy/internal-doc/${docId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                if (!isAutoSave) {
                    synergyBoard.closeInternalDocModal();
                    synergyBoard.loadSessions();
                } else {
                    // Show auto-save indicator briefly
                    const footer = document.querySelector('.internal-doc-modal .modal-footer .footer-right');
                    if (footer) {
                        const indicator = document.createElement('span');
                        indicator.className = 'auto-save-indicator';
                        indicator.innerHTML = '<i class="fas fa-check"></i> Auto-saved';
                        footer.insertBefore(indicator, footer.firstChild);
                        setTimeout(() => indicator.remove(), 2000);
                    }
                }
            } else {
                if (!isAutoSave) {
                    alert('Failed to save: ' + data.error);
                }
            }
        })
        .catch(err => {
            console.error('Error saving document:', err);
            if (!isAutoSave) {
                alert('Failed to save document');
            }
        });
};

synergyBoard.exportInternalDoc = function (docId, format) {
    if (format === 'email') {
        const email = prompt('Enter recipient email address:');
        if (!email) return;

        const subject = prompt('Email subject (optional - press Enter to use document title):');

        fetch(`/api/synergy/internal-doc/${docId}/export/email`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-ID': '1'
            },
            body: JSON.stringify({
                to: email,
                ...(subject && { subject })
            })
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert(`Email sent successfully to ${data.to}`);
                } else {
                    alert('Failed to send email: ' + data.error);
                }
            })
            .catch(err => {
                console.error('Error sending email:', err);
                alert('Failed to send email');
            });
    } else {
        // Export to Word/Google Doc/PDF
        const exportBtn = event.target.closest('.btn-export');
        if (exportBtn) {
            exportBtn.disabled = true;
            exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Exporting...';
        }

        fetch(`/api/synergy/internal-doc/${docId}/export/${format}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-ID': '1'
            }
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    if (data.url) {
                        window.open(data.url, '_blank');
                        alert(`Document exported successfully! Opening in new tab...`);
                    } else {
                        alert(`Document exported successfully!${data.note ? '\\n\\n' + data.note : ''}`);
                    }
                } else {
                    alert('Failed to export: ' + data.error);
                }
            })
            .catch(err => {
                console.error('Error exporting document:', err);
                alert('Failed to export document');
            })
            .finally(() => {
                if (exportBtn) {
                    exportBtn.disabled = false;
                    const icon = format === 'word' ? 'fab fa-microsoft' :
                        format === 'google_doc' ? 'fab fa-google' :
                            'fas fa-file-pdf';
                    const label = format === 'word' ? 'Word' :
                        format === 'google_doc' ? 'Google Doc' :
                            'PDF';
                    exportBtn.innerHTML = `<i class="${icon}"></i> ${label}`;
                }
            });
    }
};

synergyBoard.copyDocIdToClipboard = function (docId) {
    navigator.clipboard.writeText(docId).then(() => {
        const btn = event.target.closest('.btn-copy-id');
        if (btn) {
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
            btn.style.background = '#27ae60';
            setTimeout(() => {
                btn.innerHTML = originalHTML;
                btn.style.background = '';
            }, 2000);
        }
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('Failed to copy to clipboard');
    });
};

console.log('[InternalDocs] Additional methods loaded and attached to synergyBoard');
    
} else {
    console.error('[InternalDocs] synergyBoard not found - additional methods not loaded');
}
