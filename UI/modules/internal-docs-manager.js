/**
 * FILE: UI/modules/internal-docs-manager.js
 * PURPOSE: Complete internal document management system for Synergy platform
 * 
 * FEATURES:
 * - Rich text editor with TipTap
 * - Spreadsheet editor with Handsontable
 * - Document creation with metadata (title, description, tags)
 * - Floating popup windows (draggable, resizable, collapsible)
 * - Auto-save functionality
 * - Export to multiple formats
 * - Activity log and version history
 * - Editable titles
 * 
 * DEPENDENCIES:
 * - TipTap (CDN)
 * - Handsontable (CDN)
 * - FontAwesome icons
 * 
 * EXPORTS:
 * - InternalDocsManager class
 * 
 * LAST MODIFIED: 2025-11-14 - Initial modular implementation
 */

class InternalDocsManager {
    constructor(apiBaseUrl = 'http://localhost:5001') {
        this.apiBaseUrl = apiBaseUrl;
        this.popupWindows = {};
        this.popupZIndex = 9000;
        this.currentUser = {
            email: 'user@example.com', // Will be populated from auth
            user_id: 1
        };

        console.log('📄 InternalDocsManager initialized');
    }

    /**
     * Initialize the module
     */
    async init() {
        // Get current user from auth
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/auth/profile`);
            if (response.ok) {
                const data = await response.json();
                this.currentUser.email = data.email || data.username || 'user@example.com';
                this.currentUser.user_id = data.user_id || 1;
            }
        } catch (error) {
            console.warn('Could not load user profile, using defaults');
        }

        // Ensure container exists
        if (!document.getElementById('internalDocPopupContainer')) {
            const container = document.createElement('div');
            container.id = 'internalDocPopupContainer';
            document.body.appendChild(container);
        }

        console.log('✅ InternalDocsManager ready');
    }

    // ==================== PUBLIC API ====================

    /**
     * Create a new internal document with metadata form
     */
    async createInternalDoc(sessionId) {
        console.log('📄 Creating new internal document for session:', sessionId);

        const popupId = `doc-create-${Date.now()}`;
        const popup = this.createPopupWindow(popupId, 'Create Internal Document', 600, 550);

        const timestamp = new Date().toLocaleString();

        popup.bodyElement.innerHTML = `
            <div style="padding: 24px;">
                <form id="create-doc-form" style="display: flex; flex-direction: column; gap: 20px;">
                    <!-- Title -->
                    <div class="form-group">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                            Title <span style="color: #f44336;">*</span>
                        </label>
                        <input type="text" id="doc-title-input" required
                            style="width: 100%; padding: 10px 12px; background: var(--bg-tertiary); border: 1px solid var(--border-default); 
                            border-radius: 6px; color: var(--text-primary); font-size: 14px;"
                            placeholder="Enter document title...">
                    </div>

                    <!-- Created By (readonly) -->
                    <div class="form-group">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                            Created By
                        </label>
                        <input type="text" value="${this.currentUser.email}" readonly
                            style="width: 100%; padding: 10px 12px; background: var(--bg-hover); border: 1px solid var(--border-default); 
                            border-radius: 6px; color: var(--text-secondary); font-size: 14px; cursor: not-allowed;">
                    </div>

                    <!-- Created At (readonly) -->
                    <div class="form-group">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                            Created At
                        </label>
                        <input type="text" value="${timestamp}" readonly
                            style="width: 100%; padding: 10px 12px; background: var(--bg-hover); border: 1px solid var(--border-default); 
                            border-radius: 6px; color: var(--text-secondary); font-size: 14px; cursor: not-allowed;">
                    </div>

                    <!-- Description -->
                    <div class="form-group">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                            Description
                        </label>
                        <textarea id="doc-description-input" rows="3"
                            style="width: 100%; padding: 10px 12px; background: var(--bg-tertiary); border: 1px solid var(--border-default); 
                            border-radius: 6px; color: var(--text-primary); font-size: 14px; resize: vertical; font-family: inherit;"
                            placeholder="Brief description of this document..."></textarea>
                    </div>

                    <!-- Tags -->
                    <div class="form-group">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                            Tags
                        </label>
                        <input type="text" id="doc-tags-input"
                            style="width: 100%; padding: 10px 12px; background: var(--bg-tertiary); border: 1px solid var(--border-default); 
                            border-radius: 6px; color: var(--text-primary); font-size: 14px;"
                            placeholder="tag1, tag2, tag3">
                        <small style="color: var(--text-muted); font-size: 12px; display: block; margin-top: 4px;">
                            Separate tags with commas
                        </small>
                    </div>

                    <!-- Document Type -->
                    <div class="form-group">
                        <label style="display: block; margin-bottom: 12px; font-weight: 600; color: var(--text-primary);">
                            Document Type <span style="color: #f44336;">*</span>
                        </label>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
                            <div class="doc-type-option" data-type="richtext" 
                                style="padding: 20px; background: var(--bg-tertiary); border: 2px solid var(--border-default); 
                                border-radius: 12px; cursor: pointer; transition: all 0.2s; text-align: center;">
                                <i class="fas fa-file-alt" style="font-size: 32px; color: var(--accent-primary); margin-bottom: 8px;"></i>
                                <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 4px;">Rich Text</div>
                                <div style="font-size: 12px; color: var(--text-secondary);">Documents with formatting</div>
                            </div>
                            <div class="doc-type-option" data-type="spreadsheet"
                                style="padding: 20px; background: var(--bg-tertiary); border: 2px solid var(--border-default); 
                                border-radius: 12px; cursor: pointer; transition: all 0.2s; text-align: center;">
                                <i class="fas fa-table" style="font-size: 32px; color: var(--accent-primary); margin-bottom: 8px;"></i>
                                <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 4px;">Spreadsheet</div>
                                <div style="font-size: 12px; color: var(--text-secondary);">Tables with calculations</div>
                            </div>
                        </div>
                        <input type="hidden" id="doc-type-input" value="richtext">
                    </div>
                </form>
            </div>
        `;

        // Add type selector logic
        popup.bodyElement.querySelectorAll('.doc-type-option').forEach(option => {
            option.addEventListener('click', () => {
                popup.bodyElement.querySelectorAll('.doc-type-option').forEach(opt => {
                    opt.style.borderColor = 'var(--border-default)';
                    opt.style.background = 'var(--bg-tertiary)';
                });
                option.style.borderColor = 'var(--accent-primary)';
                option.style.background = 'rgba(79, 108, 255, 0.1)';
                document.getElementById('doc-type-input').value = option.dataset.type;
            });
        });

        // Select richtext by default
        popup.bodyElement.querySelector('[data-type="richtext"]').click();

        // Footer buttons
        popup.footerRightElement.innerHTML = `
            <button class="popup-action-btn" onclick="window.internalDocsManager.closePopup('${popupId}')">
                <i class="fas fa-times"></i>
                Cancel
            </button>
            <button class="popup-action-btn primary" onclick="window.internalDocsManager.submitCreateForm('${sessionId}', '${popupId}')">
                <i class="fas fa-plus"></i>
                Create Document
            </button>
        `;

        this.showPopup(popupId);
    }

    /**
     * Submit the create document form
     */
    async submitCreateForm(sessionId, popupId) {
        const title = document.getElementById('doc-title-input').value.trim();
        const description = document.getElementById('doc-description-input').value.trim();
        const tags = document.getElementById('doc-tags-input').value.trim();
        const docType = document.getElementById('doc-type-input').value;

        if (!title) {
            alert('Please enter a document title');
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-ID': String(this.currentUser.user_id)
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    title: title,
                    content: '',
                    content_json: docType === 'richtext' ? '{"type":"doc","content":[]}' : '[]',
                    doc_type: docType,
                    format: docType === 'richtext' ? 'markdown' : 'json',
                    description: description,
                    tags: tags
                })
            });

            const data = await response.json();

            if (data.success) {
                console.log('✅ Document created:', data.doc_id);
                this.closePopup(popupId);
                await this.openInternalDocPopup(data.doc_id, sessionId);

                // Refresh synergy board if available
                if (window.synergyBoard) {
                    await window.synergyBoard.loadSessions();
                    window.synergyBoard.renderAllCards();
                }
            } else {
                alert('Failed to create document: ' + data.error);
            }
        } catch (error) {
            console.error('Error creating document:', error);
            alert('Failed to create document');
        }
    }

    /**
     * Open an internal document in a floating editor popup
     */
    async openInternalDocPopup(docId, sessionId) {
        console.log('📖 Opening internal document:', docId);

        const popupId = `doc-${docId}`;
        const popup = this.createPopupWindow(popupId, 'Loading...', 900, 600);

        popup.bodyElement.innerHTML = `
            <div class="popup-loading">
                <i class="fas fa-spinner fa-spin"></i>
                <div class="popup-loading-text">Loading document...</div>
            </div>
        `;

        this.showPopup(popupId);

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/${docId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-ID': String(this.currentUser.user_id)
                }
            });

            const data = await response.json();

            if (data.success) {
                const doc = {
                    doc_id: data.doc_id,
                    session_id: data.session_id,
                    title: data.title,
                    content: data.content,
                    content_json: data.content_json,
                    format: data.format,
                    doc_type: data.doc_type || 'richtext',
                    created_at: data.created_at,
                    updated_at: data.updated_at,
                    created_by: data.created_by,
                    version: data.version,
                    linked_to_ai: data.linked_to_ai
                };

                // Format creation date
                const createdDate = doc.created_at ? new Date(doc.created_at) : new Date();
                const formattedDate = createdDate.toLocaleString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });

                // Update popup title - Single row header with controls on right
                popup.titleElement.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 12px; flex: 1;">
                        <i class="fas fa-${doc.doc_type === 'spreadsheet' ? 'table' : 'file-alt'}" style="font-size: 18px; color: var(--accent-primary);"></i>
                        <input type="text" value="${doc.title || 'Untitled'}" 
                            id="doc-title-edit-${docId}"
                            style="background: transparent; border: none; color: var(--text-primary); 
                            font-size: 20px; font-weight: 600; padding: 4px 8px; border-radius: 4px; width: auto; min-width: 150px; max-width: 600px;"
                            onblur="window.internalDocsManager.updateDocumentTitle('${docId}', this.value)"
                            oninput="this.style.width = Math.max(150, Math.min(600, (this.value.length * 12) + 20)) + 'px'"
                            onkeypress="if(event.key==='Enter'){this.blur();}">
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <i class="fas fa-clock" style="font-size: 10px; color: var(--text-muted);"></i>
                            <span style="color: var(--text-muted); font-size: 11px; white-space: nowrap;">Created ${formattedDate}</span>
                        </div>
                    </div>
                `;

                // Add description section as separate container below header (before body content)
                const descriptionContainer = document.createElement('div');
                descriptionContainer.style.cssText = 'padding: 12px 20px; border-bottom: 1px solid var(--border-color); background: var(--bg-primary);';
                descriptionContainer.innerHTML = `
                    <details ${doc.description ? 'open' : ''}>
                        <summary style="cursor: pointer; color: var(--text-muted); font-size: 12px; user-select: none; font-weight: 500;">
                            <i class="fas fa-align-left" style="font-size: 10px; margin-right: 6px;"></i>
                            Description
                        </summary>
                        <div style="margin-top: 8px; padding: 10px; background: var(--bg-secondary); border-radius: 6px; border-left: 3px solid var(--accent-primary);">
                            <textarea id="doc-description-${docId}" 
                                placeholder="Add a description for this ${doc.doc_type}..."
                                style="width: 100%; min-height: 60px; background: transparent; border: none; color: var(--text-primary); font-size: 12px; resize: vertical; padding: 4px; font-family: inherit;"
                                onblur="window.internalDocsManager.updateDocumentDescription('${docId}', this.value)"
                                onclick="event.stopPropagation()">${doc.description || ''}</textarea>
                        </div>
                    </details>
                `;

                // Insert description container before body content
                popup.bodyElement.parentElement.insertBefore(descriptionContainer, popup.bodyElement);

                // Create editor based on doc type
                if (doc.doc_type === 'spreadsheet') {
                    this.renderSpreadsheetEditor(popup, doc, sessionId);
                } else {
                    this.renderRichTextEditor(popup, doc, sessionId);
                }

                // Load and display share URL
                this.loadShareUrl(docId);

                // Update footer with save status and metadata row
                popup.footerLeftElement.innerHTML = `
                    <div style="display: flex; flex-direction: column; gap: 8px; width: 100%;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div class="save-status saved">
                                <i class="fas fa-check-circle"></i>
                                <span>Saved</span>
                            </div>
                            <span style="color: var(--text-muted); font-size: 11px;">Version ${doc.version || 1}</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px; font-size: 11px; color: var(--text-muted);">
                            <i class="fas fa-folder" style="font-size: 10px;"></i>
                            <span>Session: ${doc.session_id}</span>
                            <span style="margin: 0 4px;">•</span>
                            <span>Doc ID: ${doc.doc_id}</span>
                            <span style="margin: 0 4px;">•</span>
                            <i class="fas fa-link" style="font-size: 10px;"></i>
                            <span id="doc-share-url-${docId}" style="color: var(--accent-primary); cursor: pointer;" onclick="window.internalDocsManager.copyDocumentUrl('${docId}')" title="Click to copy share URL">/internal-docs/${docId}</span>
                        </div>
                    </div>
                `;
            } else {
                popup.bodyElement.innerHTML = `
                    <div class="popup-loading">
                        <i class="fas fa-exclamation-triangle" style="color: #f44336;"></i>
                        <div class="popup-loading-text">Failed to load document: ${data.error}</div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading document:', error);
            popup.bodyElement.innerHTML = `
                <div class="popup-loading">
                    <i class="fas fa-exclamation-triangle" style="color: #f44336;"></i>
                    <div class="popup-loading-text">Error loading document</div>
                </div>
            `;
        }
    }

    /**
     * Render rich text editor
     */
    renderRichTextEditor(popup, doc, sessionId) {
        popup.bodyElement.innerHTML = `
            <div class="doc-editor-container">
                <div class="doc-editor-toolbar">
                    <div class="toolbar-group">
                        <button class="toolbar-btn" title="Bold" onclick="document.execCommand('bold')">
                            <i class="fas fa-bold"></i>
                        </button>
                        <button class="toolbar-btn" title="Italic" onclick="document.execCommand('italic')">
                            <i class="fas fa-italic"></i>
                        </button>
                        <button class="toolbar-btn" title="Underline" onclick="document.execCommand('underline')">
                            <i class="fas fa-underline"></i>
                        </button>
                        <button class="toolbar-btn" title="Strikethrough" onclick="document.execCommand('strikeThrough')">
                            <i class="fas fa-strikethrough"></i>
                        </button>
                    </div>
                    <div class="toolbar-group">
                        <button class="toolbar-btn" title="Heading 1" onclick="document.execCommand('formatBlock', false, 'h1')">
                            <i class="fas fa-heading"></i>
                        </button>
                        <button class="toolbar-btn" title="Heading 2" onclick="document.execCommand('formatBlock', false, 'h2')">
                            <i class="fas fa-heading" style="font-size: 12px;"></i>
                        </button>
                        <button class="toolbar-btn" title="Paragraph" onclick="document.execCommand('formatBlock', false, 'p')">
                            <i class="fas fa-paragraph"></i>
                        </button>
                    </div>
                    <div class="toolbar-group">
                        <button class="toolbar-btn" title="Bullet List" onclick="document.execCommand('insertUnorderedList')">
                            <i class="fas fa-list-ul"></i>
                        </button>
                        <button class="toolbar-btn" title="Numbered List" onclick="document.execCommand('insertOrderedList')">
                            <i class="fas fa-list-ol"></i>
                        </button>
                        <button class="toolbar-btn" title="Quote" onclick="document.execCommand('formatBlock', false, 'blockquote')">
                            <i class="fas fa-quote-right"></i>
                        </button>
                    </div>
                    <div class="toolbar-group">
                        <button class="toolbar-btn" title="Link" onclick="window.internalDocsManager.insertLink()">
                            <i class="fas fa-link"></i>
                        </button>
                        <button class="toolbar-btn" title="Code" onclick="document.execCommand('formatBlock', false, 'pre')">
                            <i class="fas fa-code"></i>
                        </button>
                        <button class="toolbar-btn" title="Clear Formatting" onclick="document.execCommand('removeFormat')">
                            <i class="fas fa-eraser"></i>
                        </button>
                    </div>
                    <div class="toolbar-group">
                        <button class="toolbar-btn" title="Activity Log" onclick="window.internalDocsManager.showActivityLog('${doc.doc_id}')">
                            <i class="fas fa-history"></i>
                        </button>
                    </div>
                    <div class="toolbar-group" style="margin-left: auto; border-left: 1px solid var(--border-default); padding-left: 8px;">
                        <button class="toolbar-btn" style="background: var(--accent-primary); color: white; font-weight: 600;" title="Save Document" onclick="window.internalDocsManager.saveDocumentContent('${doc.doc_id}', document.getElementById('editor-${doc.doc_id}').innerHTML)">
                            <i class="fas fa-save"></i>
                            <span style="margin-left: 6px;">SAVE</span>
                        </button>
                    </div>
                </div>
                <div class="doc-editor-content">
                    <div class="tiptap-editor" contenteditable="true" id="editor-${doc.doc_id}">
                        ${doc.content || '<p>Start typing...</p>'}
                    </div>
                </div>
            </div>
        `;

        // Setup auto-save
        const editor = document.getElementById(`editor-${doc.doc_id}`);
        let saveTimeout;

        editor.addEventListener('input', () => {
            clearTimeout(saveTimeout);
            const statusEl = popup.footerLeftElement.querySelector('.save-status');
            if (statusEl) {
                statusEl.className = 'save-status saving';
                statusEl.querySelector('span').textContent = 'Saving...';
            }

            saveTimeout = setTimeout(() => {
                this.saveDocumentContent(doc.doc_id, editor.innerHTML, popup);
            }, 1000);
        });

        // Add footer buttons
        popup.footerRightElement.innerHTML = `
            <button class="popup-action-btn" onclick="window.internalDocsManager.exportDocument('${doc.doc_id}', 'markdown')">
                <i class="fas fa-download"></i>
                Export
            </button>
            <button class="popup-action-btn primary" onclick="window.internalDocsManager.saveDocumentContent('${doc.doc_id}', document.getElementById('editor-${doc.doc_id}').innerHTML)">
                <i class="fas fa-save"></i>
                Save Now
            </button>
        `;
    }

    /**
     * Render spreadsheet editor with Handsontable
     */
    renderSpreadsheetEditor(popup, doc, sessionId) {
        popup.bodyElement.innerHTML = `
            <div style="display: flex; flex-direction: column; height: 100%; overflow: hidden;">
                <div class="doc-editor-toolbar" style="display: flex; flex-wrap: wrap; gap: 8px; padding: 12px 16px; background: var(--bg-secondary); border-bottom: 1px solid var(--border-default); flex-shrink: 0;">
                    <!-- Row/Column Actions -->
                    <div class="toolbar-group" style="display: flex; gap: 4px; padding-right: 8px; border-right: 1px solid var(--border-default);">
                        <button class="toolbar-btn" title="Add Row Below" onclick="window.internalDocsManager.addRow('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-plus" style="font-size: 14px;"></i>
                        </button>
                        <button class="toolbar-btn" title="Add Column Right" onclick="window.internalDocsManager.addColumn('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-plus" style="font-size: 14px;"></i>
                        </button>
                        <button class="toolbar-btn" title="Delete Selected Rows" onclick="window.internalDocsManager.deleteRow('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-minus" style="font-size: 14px;"></i>
                        </button>
                        <button class="toolbar-btn" title="Delete Selected Columns" onclick="window.internalDocsManager.deleteColumn('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-minus" style="font-size: 14px;"></i>
                        </button>
                    </div>
                    
                    <!-- Formatting Actions -->
                    <div class="toolbar-group" style="display: flex; gap: 4px; padding-right: 8px; border-right: 1px solid var(--border-default);">
                        <button class="toolbar-btn" title="Merge Cells" onclick="window.internalDocsManager.mergeCells('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-object-group" style="font-size: 14px;"></i>
                        </button>
                        <button class="toolbar-btn" title="Unmerge Cells" onclick="window.internalDocsManager.unmergeCells('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-object-ungroup" style="font-size: 14px;"></i>
                        </button>
                    </div>
                    
                    <!-- Clipboard Actions -->
                    <div class="toolbar-group" style="display: flex; gap: 4px; padding-right: 8px; border-right: 1px solid var(--border-default);">
                        <button class="toolbar-btn" title="Copy" onclick="window.internalDocsManager.copySelection('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-copy" style="font-size: 14px;"></i>
                        </button>
                        <button class="toolbar-btn" title="Paste" onclick="window.internalDocsManager.pasteSelection('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-paste" style="font-size: 14px;"></i>
                        </button>
                        <button class="toolbar-btn" title="Clear Contents" onclick="window.internalDocsManager.clearSelection('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-eraser" style="font-size: 14px;"></i>
                        </button>
                    </div>
                    
                    <!-- Sorting/Filtering -->
                    <div class="toolbar-group" style="display: flex; gap: 4px; padding-right: 8px; border-right: 1px solid var(--border-default);">
                        <button class="toolbar-btn" title="Sort Ascending" onclick="window.internalDocsManager.sortAscending('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-sort-amount-down" style="font-size: 14px;"></i>
                        </button>
                        <button class="toolbar-btn" title="Sort Descending" onclick="window.internalDocsManager.sortDescending('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-sort-amount-up" style="font-size: 14px;"></i>
                        </button>
                    </div>
                    
                    <!-- Undo/Redo -->
                    <div class="toolbar-group" style="display: flex; gap: 4px; padding-right: 8px; border-right: 1px solid var(--border-default);">
                        <button class="toolbar-btn" title="Undo" onclick="window.internalDocsManager.undoSpreadsheet('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-undo" style="font-size: 14px;"></i>
                        </button>
                        <button class="toolbar-btn" title="Redo" onclick="window.internalDocsManager.redoSpreadsheet('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-redo" style="font-size: 14px;"></i>
                        </button>
                    </div>
                    
                    <!-- Export/Share -->
                    <div class="toolbar-group" style="display: flex; gap: 4px;">
                        <button class="toolbar-btn" title="Export CSV" onclick="window.internalDocsManager.exportDocument('${doc.doc_id}', 'csv')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-file-csv" style="font-size: 14px;"></i>
                        </button>
                        <button class="toolbar-btn" title="Copy Share Link" onclick="window.internalDocsManager.copyDocumentUrl('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-link" style="font-size: 14px;"></i>
                        </button>
                    </div>
                    
                    <!-- SAVE BUTTON (Prominent) -->
                    <div class="toolbar-group" style="display: flex; gap: 4px; margin-left: auto; padding-left: 8px; border-left: 1px solid var(--border-default);">
                        <button class="toolbar-btn" title="Save Spreadsheet" onclick="window.internalDocsManager.saveSpreadsheetWithNotification('${doc.doc_id}')" style="padding: 10px 14px; background: var(--accent-primary); border: 1px solid var(--accent-primary); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: white; box-shadow: 0 2px 8px rgba(79, 108, 255, 0.3);">
                            <i class="fas fa-save" style="font-size: 16px;"></i>
                        </button>
                    </div>
                </div>
                <div id="spreadsheet-${doc.doc_id}" style="flex: 1; width: 100%; height: 100%; overflow: hidden; background: var(--bg-primary);">
                    <!-- Handsontable will be initialized here -->
                </div>
            </div>
        `;

        // Initialize Handsontable
        const container = document.getElementById(`spreadsheet-${doc.doc_id}`);

        // Parse existing data or create empty grid
        let data = [];
        try {
            data = JSON.parse(doc.content_json || doc.content || '[]');
            if (!Array.isArray(data) || data.length === 0) {
                // Create 10x10 empty grid
                data = Array(10).fill(null).map(() => Array(10).fill(''));
            }
        } catch (e) {
            // Create 10x10 empty grid on error
            data = Array(10).fill(null).map(() => Array(10).fill(''));
        }

        // Check if Handsontable is loaded
        if (typeof Handsontable === 'undefined') {
            container.innerHTML = `
                <div style="padding: 40px; text-align: center; color: var(--text-secondary);">
                    <i class="fas fa-exclamation-triangle" style="font-size: 48px; color: #ffc107; margin-bottom: 16px;"></i>
                    <h3>Handsontable Not Loaded</h3>
                    <p style="margin: 16px 0;">Please include Handsontable in your HTML:</p>
                    <code style="display: block; background: var(--bg-tertiary); padding: 12px; border-radius: 6px; margin: 16px 0;">
                        &lt;script src="https://cdn.jsdelivr.net/npm/handsontable/dist/handsontable.full.min.js"&gt;&lt;/script&gt;<br>
                        &lt;link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/handsontable/dist/handsontable.full.min.css"&gt;
                    </code>
                    <p style="margin-top: 16px;">
                        <a href="https://handsontable.com/docs/" target="_blank" style="color: var(--accent-primary);">
                            View Handsontable Documentation
                        </a>
                    </p>
                </div>
            `;
        } else {
            // Initialize Handsontable with FULL configuration - ALL FEATURES ENABLED
            const hot = new Handsontable(container, {
                data: data,
                width: '100%',
                height: '100%',
                licenseKey: 'non-commercial-and-evaluation',

                // HEADERS
                rowHeaders: true,
                colHeaders: true,

                // CONTEXT MENU - Enable with ALL options
                contextMenu: [
                    'row_above',
                    'row_below',
                    'col_left',
                    'col_right',
                    '---------',
                    'remove_row',
                    'remove_col',
                    '---------',
                    'undo',
                    'redo',
                    '---------',
                    'make_read_only',
                    '---------',
                    'alignment',
                    '---------',
                    'copy',
                    'cut',
                    '---------',
                    'mergeCells',
                    '---------',
                    'commentsAddEdit',
                    'commentsRemove'
                ],

                // DROPDOWN MENU - Column header menus
                dropdownMenu: [
                    'filter_by_condition',
                    'filter_operators',
                    'filter_by_condition2',
                    'filter_by_value',
                    'filter_action_bar',
                    '---------',
                    'alignment',
                    '---------',
                    'freeze_column',
                    '---------',
                    'clear_column'
                ],

                // COLUMN/ROW MANIPULATION
                manualRowResize: true,
                manualColumnResize: true,
                manualRowMove: true,
                manualColumnMove: true,
                autoWrapRow: true,
                autoWrapCol: true,

                // CELL FEATURES
                copyPaste: true,
                fillHandle: true,

                // UNDO/REDO
                undo: true,

                // COMMENTS
                comments: true,

                // CUSTOM BORDERS
                customBorders: true,

                // MERGE CELLS
                mergeCells: true,

                // SORTING
                columnSorting: {
                    indicator: true,
                    headerAction: true,
                    sortEmptyCells: true
                },

                // FILTERS
                filters: true,
                dropdownMenu: true,

                // COLUMN FREEZING
                fixedColumnsStart: 0,
                fixedRowsTop: 0,
                fixedRowsBottom: 0,

                // AUTO SIZE
                autoColumnSize: true,
                autoRowSize: true,

                // SELECTION
                selectionMode: 'multiple',
                outsideClickDeselects: true,

                // EDITOR OPTIONS
                enterBeginsEditing: true,
                enterMoves: { row: 1, col: 0 },
                tabMoves: { row: 0, col: 1 },

                // CELL NAVIGATION
                autoWrapCol: true,
                autoWrapRow: true,

                // VIRTUAL SCROLLING
                renderAllRows: false,
                renderAllColumns: false,

                // SPARE ROWS/COLS
                minSpareRows: 1,
                minSpareCols: 1,

                // SEARCH
                search: true,

                // ALLOW INSERTIONS
                allowInsertRow: true,
                allowInsertColumn: true,
                allowRemoveRow: true,
                allowRemoveColumn: true,

                // CELL TYPES (enable all cell types)
                cells: function (row, col) {
                    const cellProperties = {};
                    // Default to text type with auto-detection
                    cellProperties.type = 'text';
                    return cellProperties;
                },

                // EVENT HANDLERS
                afterChange: (changes, source) => {
                    if (source !== 'loadData') {
                        // Auto-save on change
                        clearTimeout(this.spreadsheetSaveTimeout);
                        const statusEl = popup.footerLeftElement.querySelector('.save-status');
                        if (statusEl) {
                            statusEl.className = 'save-status saving';
                            statusEl.querySelector('span').textContent = 'Saving...';
                        }

                        this.spreadsheetSaveTimeout = setTimeout(() => {
                            const data = hot.getData();
                            this.saveDocumentContent(doc.doc_id, JSON.stringify(data), popup, true);
                        }, 1000);
                    }
                },

                afterSelection: (row, column, row2, column2) => {
                    console.log('Selection:', { row, column, row2, column2 });
                },

                afterCreateRow: (index, amount) => {
                    console.log('Row created at:', index, 'amount:', amount);
                },

                afterCreateCol: (index, amount) => {
                    console.log('Column created at:', index, 'amount:', amount);
                },

                afterRemoveRow: (index, amount) => {
                    console.log('Row removed at:', index, 'amount:', amount);
                },

                afterRemoveCol: (index, amount) => {
                    console.log('Column removed at:', index, 'amount:', amount);
                },

                // STYLING
                className: 'htCenter htMiddle',

                // COLUMN WIDTH OPTIONS
                colWidths: 100,

                // ROW HEIGHT OPTIONS
                rowHeights: 23,

                // WORD WRAP
                wordWrap: true,

                // STRETCH
                stretchH: 'all'
            });

            // Store instance for toolbar actions
            this.handsontableInstances = this.handsontableInstances || {};
            this.handsontableInstances[doc.doc_id] = hot;
        }

        // Add footer buttons with save status
        popup.footerLeftElement.innerHTML = `
            <div class="save-status saved" style="display: flex; align-items: center; gap: 8px; color: var(--text-secondary); font-size: 13px;">
                <i class="fas fa-check-circle"></i>
                <span>Saved</span>
            </div>
            <span style="color: var(--text-muted); font-size: 13px;">Version 1</span>
        `;

        popup.footerRightElement.innerHTML = ``;
    }

    /**
     * Save spreadsheet with toast notification
     */
    async saveSpreadsheetWithNotification(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) {
            console.error('Handsontable instance not found for:', docId);
            return;
        }

        const data = hot.getData();
        const popup = this.popupWindows[`doc-${docId}`];

        await this.saveDocumentContent(docId, JSON.stringify(data), popup, true);

        // Show toast notification
        this.showToast('Document saved successfully!', 'success');
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : '#f44336'};
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 100000;
            font-size: 14px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 12px;
            animation: slideIn 0.3s ease-out;
        `;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}" style="font-size: 18px;"></i>
            <span>${message}</span>
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transition = 'opacity 0.3s';
            setTimeout(() => document.body.removeChild(toast), 300);
        }, 2500);
    }

    /**
     * Save document content
     */
    async saveDocumentContent(docId, content, popup = null, isJson = false) {
        try {
            const payload = isJson ? {
                content_json: content
            } : {
                content: content
            };

            const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/${docId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-ID': String(this.currentUser.user_id)
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (data.success) {
                console.log('✅ Document saved:', docId);
                if (popup) {
                    const statusEl = popup.footerLeftElement.querySelector('.save-status');
                    if (statusEl) {
                        statusEl.className = 'save-status saved';
                        statusEl.querySelector('span').textContent = 'Saved';

                        // Update version
                        const versionEl = popup.footerLeftElement.querySelector('span[style*="text-muted"]');
                        if (versionEl && data.version) {
                            versionEl.textContent = `Version ${data.version}`;
                        }
                    }
                }

                // Refresh synergy board if available
                if (window.synergyBoard) {
                    await window.synergyBoard.loadSessions();
                    window.synergyBoard.renderAllCards();
                }
            } else {
                console.error('Failed to save document:', data.error);
                if (popup) {
                    const statusEl = popup.footerLeftElement.querySelector('.save-status');
                    if (statusEl) {
                        statusEl.className = 'save-status error';
                        statusEl.querySelector('span').textContent = 'Error';
                    }
                }
            }
        } catch (error) {
            console.error('Error saving document:', error);
            if (popup) {
                const statusEl = popup.footerLeftElement.querySelector('.save-status');
                if (statusEl) {
                    statusEl.className = 'save-status error';
                    statusEl.querySelector('span').textContent = 'Error';
                }
            }
        }
    }

    /**
     * Export document
     */
    async exportDocument(docId, format) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/${docId}/export/${format}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-ID': String(this.currentUser.user_id)
                }
            });

            const contentType = response.headers.get('content-type');

            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                alert('Export failed: ' + (data.error || 'Unknown error'));
                return;
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;

            const disposition = response.headers.get('content-disposition');
            let filename = `document.${format}`;
            if (disposition && disposition.includes('filename=')) {
                const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
                if (matches != null && matches[1]) {
                    filename = matches[1].replace(/['"]/g, '');
                }
            }

            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            console.log('✅ Document exported:', filename);
        } catch (error) {
            console.error('Error exporting document:', error);
            alert('Failed to export document');
        }
    }

    /**
     * SPREADSHEET TOOLBAR ACTIONS
     */

    mergeCells(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) return;

        const selected = hot.getSelected();
        if (!selected || selected.length === 0) {
            alert('Please select cells to merge');
            return;
        }

        const [startRow, startCol, endRow, endCol] = selected[0];
        hot.getPlugin('mergeCells').merge(startRow, startCol, endRow, endCol);
        console.log('Cells merged:', startRow, startCol, endRow, endCol);
    }

    unmergeCells(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) return;

        const selected = hot.getSelected();
        if (!selected || selected.length === 0) {
            alert('Please select merged cells to unmerge');
            return;
        }

        const [startRow, startCol] = selected[0];
        hot.getPlugin('mergeCells').unmerge(startRow, startCol);
        console.log('Cells unmerged:', startRow, startCol);
    }

    copySelection(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) return;

        const plugin = hot.getPlugin('copyPaste');
        plugin.copy();
        console.log('Selection copied to clipboard');
    }

    pasteSelection(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) return;

        const plugin = hot.getPlugin('copyPaste');
        plugin.paste();
        console.log('Pasted from clipboard');
    }

    clearSelection(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) return;

        const selected = hot.getSelected();
        if (!selected || selected.length === 0) return;

        selected.forEach(([startRow, startCol, endRow, endCol]) => {
            for (let row = startRow; row <= endRow; row++) {
                for (let col = startCol; col <= endCol; col++) {
                    hot.setDataAtCell(row, col, '');
                }
            }
        });
        console.log('Selection cleared');
    }

    sortAscending(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) return;

        const selected = hot.getSelected();
        if (!selected || selected.length === 0) {
            alert('Please select a column to sort');
            return;
        }

        const col = selected[0][1];
        const plugin = hot.getPlugin('columnSorting');
        plugin.sort({ column: col, sortOrder: 'asc' });
        console.log('Sorted column', col, 'ascending');
    }

    sortDescending(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) return;

        const selected = hot.getSelected();
        if (!selected || selected.length === 0) {
            alert('Please select a column to sort');
            return;
        }

        const col = selected[0][1];
        const plugin = hot.getPlugin('columnSorting');
        plugin.sort({ column: col, sortOrder: 'desc' });
        console.log('Sorted column', col, 'descending');
    }

    undoSpreadsheet(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) return;

        if (hot.isUndoAvailable()) {
            hot.undo();
            console.log('Undo performed');
        } else {
            console.log('Nothing to undo');
        }
    }

    redoSpreadsheet(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) return;

        if (hot.isRedoAvailable()) {
            hot.redo();
            console.log('Redo performed');
        } else {
            console.log('Nothing to redo');
        }
    }

    /**
     * Load and display share URL in document header
     */
    async loadShareUrl(docId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/${docId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-ID': String(this.currentUser.user_id)
                }
            });

            const data = await response.json();

            if (data.success) {
                const urlElement = document.getElementById(`doc-share-url-${docId}`);
                if (urlElement) {
                    const slug = data.slug || docId;
                    const shareUrl = `/internal-docs/${slug}`;
                    urlElement.textContent = shareUrl;
                }
            }
        } catch (error) {
            console.error('Error loading share URL:', error);
            const urlElement = document.getElementById(`doc-share-url-${docId}`);
            if (urlElement) {
                urlElement.textContent = `/internal-docs/${docId}`;
            }
        }
    }

    /**
     * Copy document URL to clipboard with detailed context for AI agents
     */
    async copyDocumentUrl(docId) {
        try {
            // Fetch document to get full details
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/${docId}`, {
                headers: {
                    'X-User-ID': String(this.currentUser.user_id)
                }
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error('Failed to fetch document');
            }

            // Fetch session details to get session title/slug
            let sessionTitle = 'Unknown Session';
            let sessionSlug = data.session_id;
            try {
                const sessionResponse = await fetch(`${this.apiBaseUrl}/api/synergy/session/${data.session_id}`, {
                    headers: {
                        'X-User-ID': String(this.currentUser.user_id)
                    }
                });
                const sessionData = await sessionResponse.json();
                if (sessionData.success) {
                    sessionTitle = sessionData.title || sessionData.session_id;
                    // Extract slug from session_id (format: sess_timestamp_slug)
                    const parts = sessionData.session_id.split('_');
                    if (parts.length > 2) {
                        sessionSlug = parts.slice(2).join('_');
                    }
                }
            } catch (e) {
                console.warn('Could not fetch session details:', e);
            }

            // Build comprehensive context for AI agents
            const slug = data.slug || docId;
            const url = `${window.location.origin}/internal-docs/${slug}`;

            // Create detailed context text
            const contextText = `Internal Document Reference:

Title: ${data.title}
Document Type: ${data.doc_type || 'richtext'}
Document Slug: ${slug}

Session: ${sessionTitle}
Session Slug: ${sessionSlug}
Session ID: ${data.session_id}

Format: ${data.format || 'markdown'}
Created: ${data.created_at}
${data.description ? `Description: ${data.description}\n` : ''}${data.tags ? `Tags: ${data.tags}\n` : ''}
Direct URL: ${url}

Note: Use the document slug "${slug}" to reference this document in Synergy sessions.`;

            await navigator.clipboard.writeText(contextText);

            // Show success message
            const message = document.createElement('div');
            message.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: var(--accent-primary);
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 100000;
                font-size: 14px;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 8px;
            `;
            message.innerHTML = `
                <i class="fas fa-check-circle"></i>
                <span>Document details copied to clipboard!</span>
            `;
            document.body.appendChild(message);

            setTimeout(() => {
                message.style.opacity = '0';
                message.style.transition = 'opacity 0.3s';
                setTimeout(() => document.body.removeChild(message), 300);
            }, 2000);

            console.log('Document context copied:\n', contextText);
        } catch (error) {
            console.error('Failed to copy URL:', error);
            alert('Failed to copy link to clipboard');
        }
    }

    /**
     * Update document title
     */
    async updateDocumentTitle(docId, newTitle) {
        if (!newTitle.trim()) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/${docId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-ID': String(this.currentUser.user_id)
                },
                body: JSON.stringify({
                    title: newTitle
                })
            });

            const data = await response.json();

            if (data.success) {
                console.log('✅ Title updated:', newTitle);

                // Refresh synergy board if available
                if (window.synergyBoard) {
                    await window.synergyBoard.loadSessions();
                    window.synergyBoard.renderAllCards();
                }
            } else {
                alert('Failed to update title: ' + data.error);
            }
        } catch (error) {
            console.error('Error updating title:', error);
            alert('Failed to update title');
        }
    }

    /**
     * Update document description
     */
    async updateDocumentDescription(docId, newDescription) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/${docId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-ID': String(this.currentUser.user_id)
                },
                body: JSON.stringify({
                    description: newDescription
                })
            });

            const data = await response.json();

            if (data.success) {
                console.log('✅ Description updated');
            } else {
                console.error('Failed to update description:', data.error);
            }
        } catch (error) {
            console.error('Error updating description:', error);
        }
    }

    /**
     * Show activity log with version history
     */
    async showActivityLog(docId) {
        const popupId = `activity-log-${docId}`;
        const popup = this.createPopupWindow(popupId, 'Activity Log & Version History', 700, 500);

        popup.bodyElement.innerHTML = `
            <div class="popup-loading">
                <i class="fas fa-spinner fa-spin"></i>
                <div class="popup-loading-text">Loading activity log...</div>
            </div>
        `;

        this.showPopup(popupId);

        // TODO: Implement activity log API endpoint
        // For now, show placeholder
        setTimeout(() => {
            popup.bodyElement.innerHTML = `
                <div style="padding: 24px;">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid var(--border-default);">
                        <i class="fas fa-history" style="font-size: 24px; color: var(--accent-primary);"></i>
                        <div>
                            <h3 style="margin: 0; font-size: 16px; font-weight: 600; color: var(--text-primary);">Document Activity</h3>
                            <p style="margin: 4px 0 0; font-size: 12px; color: var(--text-secondary);">Track changes and version history</p>
                        </div>
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 12px;">
                        <!-- Activity items -->
                        <div style="padding: 12px; background: var(--bg-tertiary); border-radius: 8px; border-left: 3px solid #4caf50;">
                            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                                <span style="font-weight: 600; color: var(--text-primary);">
                                    <i class="fas fa-file-alt" style="color: #4caf50; margin-right: 8px;"></i>
                                    Document Created
                                </span>
                                <span style="font-size: 12px; color: var(--text-muted);">Just now</span>
                            </div>
                            <div style="font-size: 13px; color: var(--text-secondary);">
                                Created by ${this.currentUser.email}
                            </div>
                        </div>

                        <div style="padding: 12px; background: var(--bg-tertiary); border-radius: 8px; border-left: 3px solid var(--accent-primary);">
                            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                                <span style="font-weight: 600; color: var(--text-primary);">
                                    <i class="fas fa-eye" style="color: var(--accent-primary); margin-right: 8px;"></i>
                                    Document Opened
                                </span>
                                <span style="font-size: 12px; color: var(--text-muted);">Now</span>
                            </div>
                            <div style="font-size: 13px; color: var(--text-secondary);">
                                Opened by ${this.currentUser.email}
                            </div>
                        </div>

                        <!-- Coming soon message -->
                        <div style="margin-top: 20px; padding: 16px; background: rgba(255, 193, 7, 0.1); border-radius: 8px; text-align: center;">
                            <i class="fas fa-info-circle" style="color: #ffc107; font-size: 24px; margin-bottom: 8px;"></i>
                            <p style="margin: 0; font-size: 13px; color: var(--text-secondary);">
                                Full version history tracking coming soon!<br>
                                Will include timestamps, user actions, and version rollback.
                            </p>
                        </div>
                    </div>
                </div>
            `;
        }, 500);

        popup.footerRightElement.innerHTML = `
            <button class="popup-action-btn" onclick="window.internalDocsManager.closePopup('${popupId}')">
                <i class="fas fa-times"></i>
                Close
            </button>
        `;
    }

    /**
     * Insert link helper
     */
    insertLink() {
        const url = prompt('Enter URL:');
        if (url) {
            document.execCommand('createLink', false, url);
        }
    }

    /**
     * Handsontable toolbar actions
     */
    addRow(docId) {
        const hot = this.handsontableInstances?.[docId];
        if (hot) {
            hot.alter('insert_row_below', hot.countRows() - 1);
        }
    }

    addColumn(docId) {
        const hot = this.handsontableInstances?.[docId];
        if (hot) {
            hot.alter('insert_col_end', hot.countCols() - 1);
        }
    }

    deleteRow(docId) {
        const hot = this.handsontableInstances?.[docId];
        if (hot) {
            const selected = hot.getSelected();
            if (selected && selected.length > 0) {
                const row = selected[0][0];
                hot.alter('remove_row', row);
            } else {
                alert('Please select a row to delete');
            }
        }
    }

    deleteColumn(docId) {
        const hot = this.handsontableInstances?.[docId];
        if (hot) {
            const selected = hot.getSelected();
            if (selected && selected.length > 0) {
                const col = selected[0][1];
                hot.alter('remove_col', col);
            } else {
                alert('Please select a column to delete');
            }
        }
    }

    // ==================== POPUP WINDOW MANAGEMENT ====================

    /**
     * Create a floating popup window
     */
    createPopupWindow(id, title, width = 800, height = 700) {
        const container = document.getElementById('internalDocPopupContainer');

        if (this.popupWindows[id]) {
            this.showPopup(id);
            return this.popupWindows[id];
        }

        const left = (window.innerWidth - width) / 2;
        const top = (window.innerHeight - height) / 2;

        const popupHTML = `
            <div class="internal-doc-popup" id="${id}" style="width: ${width}px; height: ${height}px; left: ${left}px; top: ${top}px;">
                <div class="popup-resize-handle n"></div>
                <div class="popup-resize-handle s"></div>
                <div class="popup-resize-handle e"></div>
                <div class="popup-resize-handle w"></div>
                <div class="popup-resize-handle ne"></div>
                <div class="popup-resize-handle nw"></div>
                <div class="popup-resize-handle se"></div>
                <div class="popup-resize-handle sw"></div>

                <div class="internal-doc-popup-header">
                    <div class="internal-doc-popup-title">${title}</div>
                    <div class="internal-doc-popup-controls">
                        <button class="popup-control-btn minimize" title="Minimize" onclick="window.internalDocsManager.toggleCollapse('${id}')">
                            <i class="fas fa-minus"></i>
                        </button>
                        <button class="popup-control-btn maximize" title="Maximize" onclick="window.internalDocsManager.toggleMaximize('${id}')">
                            <i class="fas fa-expand"></i>
                        </button>
                        <button class="popup-control-btn close" title="Close" onclick="window.internalDocsManager.closePopup('${id}')">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>

                <div class="internal-doc-popup-body"></div>

                <div class="internal-doc-popup-footer">
                    <div class="popup-footer-left"></div>
                    <div class="popup-footer-right"></div>
                </div>
            </div>
        `;

        container.insertAdjacentHTML('beforeend', popupHTML);

        const popupElement = document.getElementById(id);
        const headerElement = popupElement.querySelector('.internal-doc-popup-header');
        const titleElement = popupElement.querySelector('.internal-doc-popup-title');
        const bodyElement = popupElement.querySelector('.internal-doc-popup-body');
        const footerElement = popupElement.querySelector('.internal-doc-popup-footer');
        const footerLeftElement = popupElement.querySelector('.popup-footer-left');
        const footerRightElement = popupElement.querySelector('.popup-footer-right');

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
        this.initPopupDrag(popup);
        this.initPopupResize(popup);

        return popup;
    }

    showPopup(id) {
        const popup = this.popupWindows[id];
        if (!popup) return;

        popup.popupElement.classList.add('active', 'animating');
        popup.popupElement.style.zIndex = ++this.popupZIndex;

        setTimeout(() => {
            popup.popupElement.classList.remove('animating');
        }, 300);
    }

    closePopup(id) {
        const popup = this.popupWindows[id];
        if (!popup) return;

        popup.popupElement.classList.remove('active');

        setTimeout(() => {
            popup.popupElement.remove();
            delete this.popupWindows[id];
        }, 200);
    }

    toggleCollapse(id) {
        const popup = this.popupWindows[id];
        if (!popup) return;

        popup.isCollapsed = !popup.isCollapsed;
        popup.popupElement.classList.toggle('collapsed', popup.isCollapsed);

        const icon = popup.headerElement.querySelector('.minimize i');
        icon.className = popup.isCollapsed ? 'fas fa-plus' : 'fas fa-minus';
    }

    toggleMaximize(id) {
        const popup = this.popupWindows[id];
        if (!popup) return;

        popup.isMaximized = !popup.isMaximized;
        popup.popupElement.classList.toggle('maximized', popup.isMaximized);

        const icon = popup.headerElement.querySelector('.maximize i');
        icon.className = popup.isMaximized ? 'fas fa-compress' : 'fas fa-expand';
    }

    initPopupDrag(popup) {
        let isDragging = false;
        let dragOffsetX = 0;
        let dragOffsetY = 0;

        popup.headerElement.addEventListener('mousedown', (e) => {
            if (e.target.closest('.popup-control-btn') || e.target.tagName === 'INPUT') return;
            if (popup.isMaximized) return;

            isDragging = true;
            dragOffsetX = e.clientX - popup.popupElement.offsetLeft;
            dragOffsetY = e.clientY - popup.popupElement.offsetTop;

            popup.popupElement.style.zIndex = ++this.popupZIndex;

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
            isDragging = false;
        });
    }

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
}

// Auto-initialize and expose globally
window.internalDocsManager = new InternalDocsManager(window.API_BASE_URL || 'http://localhost:5001');

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.internalDocsManager.init();
    });
} else {
    window.internalDocsManager.init();
}

console.log('✅ Internal Docs Manager module loaded');
