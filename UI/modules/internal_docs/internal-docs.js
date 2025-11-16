/**
 * FILE: UI/modules/internal-docs.js
 * PURPOSE: Complete internal documents module with rich text, spreadsheets, and collaboration
 * 
 * FEATURES:
 * - Rich text editor (TipTap) with all formatting
 * - Spreadsheet editor (Handsontable) with formulas
 * - Real-time collaboration (Y.js)
 * - AI integration (drag & drop to sessions)
 * - Copy doc ID to clipboard
 * - Version tracking
 * - Export to multiple formats
 * 
 * DEPENDENCIES:
 * - TipTap (rich text)
 * - Handsontable (spreadsheet)
 * - Y.js (collaboration)
 * - HyperFormula (spreadsheet formulas)
 * 
 * EXPORTS:
 * - InternalDocsManager class
 * 
 * LAST MODIFIED: 2025-11-14 - Initial module creation
 */

class InternalDocsManager {
    constructor(config = {}) {
        this.apiBaseUrl = config.apiBaseUrl || '/api/synergy';
        this.userId = config.userId || 1;
        this.sessionId = config.sessionId || null;

        // Editor instances
        this.richTextEditor = null;
        this.spreadsheetEditor = null;
        this.collaborationProvider = null;

        // Current document state
        this.currentDoc = null;
        this.autoSaveInterval = null;
        this.collaborators = new Map();

        // Configuration
        this.autoSaveDelay = config.autoSaveDelay || 30000; // 30 seconds
        this.enableCollaboration = config.enableCollaboration !== false;
        this.enableAI = config.enableAI !== false;

        console.log('[InternalDocs] Module initialized', {
            collaboration: this.enableCollaboration,
            ai: this.enableAI
        });
    }

    // ============================================================================
    // INITIALIZATION
    // ============================================================================

    /**
     * Initialize the internal docs system
     * Call this once on page load
     */
    async init() {
        await this.loadDependencies();
        this.setupEventListeners();
        console.log('[InternalDocs] System ready');
    }

    /**
     * Load required external libraries
     */
    async loadDependencies() {
        const dependencies = [
            // TipTap
            { id: 'tiptap-core', src: 'https://unpkg.com/@tiptap/core@2.1.13/dist/tiptap-core.umd.min.js' },
            { id: 'tiptap-starterkit', src: 'https://unpkg.com/@tiptap/starter-kit@2.1.13/dist/tiptap-starter-kit.umd.min.js' },
            { id: 'tiptap-collaboration', src: 'https://unpkg.com/@tiptap/extension-collaboration@2.1.13/dist/tiptap-extension-collaboration.umd.min.js' },

            // Handsontable
            { id: 'handsontable-css', type: 'css', href: 'https://cdn.jsdelivr.net/npm/handsontable/dist/handsontable.full.min.css' },
            { id: 'handsontable-js', src: 'https://cdn.jsdelivr.net/npm/handsontable/dist/handsontable.full.min.js' },
            { id: 'hyperformula', src: 'https://cdn.jsdelivr.net/npm/hyperformula/dist/hyperformula.full.min.js' },

            // Y.js (collaboration)
            { id: 'yjs', src: 'https://cdn.jsdelivr.net/npm/yjs@13.6.10/dist/yjs.js' },
            { id: 'y-websocket', src: 'https://cdn.jsdelivr.net/npm/y-websocket@1.5.0/dist/y-websocket.js' }
        ];

        for (const dep of dependencies) {
            if (document.getElementById(dep.id)) continue; // Already loaded

            if (dep.type === 'css') {
                const link = document.createElement('link');
                link.id = dep.id;
                link.rel = 'stylesheet';
                link.href = dep.href;
                document.head.appendChild(link);
            } else {
                await this.loadScript(dep.id, dep.src);
            }
        }
    }

    /**
     * Load script dynamically
     */
    loadScript(id, src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.id = id;
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    /**
     * Setup global event listeners
     */
    setupEventListeners() {
        // Drag & drop for AI integration
        document.addEventListener('dragstart', (e) => {
            if (e.target.classList.contains('doc-item')) {
                e.dataTransfer.setData('doc-id', e.target.dataset.docId);
                e.dataTransfer.setData('doc-title', e.target.dataset.docTitle);
                e.dataTransfer.effectAllowed = 'copy';
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 's':
                        e.preventDefault();
                        this.saveCurrentDoc();
                        break;
                    case 'k':
                        if (this.currentDoc) {
                            e.preventDefault();
                            this.copyDocIdToClipboard(this.currentDoc.doc_id);
                        }
                        break;
                }
            }
        });
    }

    // ============================================================================
    // DOCUMENT CREATION & MANAGEMENT
    // ============================================================================

    /**
     * Create a new document
     */
    async createDocument(options = {}) {
        const {
            sessionId,
            title = 'Untitled Document',
            type = 'richtext', // 'richtext' or 'spreadsheet'
            content = '',
            format = 'markdown'
        } = options;

        try {
            const response = await fetch(`${this.apiBaseUrl}/internal-doc/create`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId || this.sessionId,
                    title,
                    content,
                    format,
                    doc_type: type,
                    created_by: this.userId
                })
            });

            const data = await response.json();

            if (data.success) {
                console.log('[InternalDocs] Document created:', data.doc_id);
                return data;
            } else {
                throw new Error(data.error || 'Failed to create document');
            }
        } catch (error) {
            console.error('[InternalDocs] Create error:', error);
            throw error;
        }
    }

    /**
     * Open document in editor modal
     */
    async openDocument(docId, options = {}) {
        try {
            // Fetch document
            const response = await fetch(`${this.apiBaseUrl}/internal-doc/${docId}`);
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Failed to load document');
            }

            this.currentDoc = data;

            // Create modal
            const modal = this.createDocumentModal(data, options);
            document.body.appendChild(modal);

            // Initialize appropriate editor
            if (data.doc_type === 'spreadsheet') {
                await this.initSpreadsheetEditor(data);
            } else {
                await this.initRichTextEditor(data);
            }

            // Setup collaboration if enabled
            if (this.enableCollaboration) {
                await this.initCollaboration(docId);
            }

            // Setup auto-save
            this.startAutoSave();

            console.log('[InternalDocs] Document opened:', docId);
            return data;
        } catch (error) {
            console.error('[InternalDocs] Open error:', error);
            throw error;
        }
    }

    /**
     * Create document editor modal
     */
    createDocumentModal(doc, options = {}) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay internal-doc-modal';
        modal.id = 'internal-doc-modal';

        modal.innerHTML = `
            <div class="modal-content" style="width: 95%; max-width: 1600px; height: 90vh;">
                <div class="modal-header">
                    <div class="doc-header-top">
                        <div class="doc-title-section">
                            <input type="text" 
                                   id="doc-title" 
                                   value="${this.escapeHtml(doc.title)}" 
                                   class="doc-title-input"
                                   placeholder="Document Title" />
                            <div class="doc-meta">
                                <span><i class="fas fa-file-alt"></i> ${doc.doc_type || 'document'}</span>
                                <span><i class="fas fa-code"></i> ${doc.format || 'markdown'}</span>
                                <span><i class="fas fa-layer-group"></i> v${doc.version || 1}</span>
                                <span><i class="fas fa-user"></i> ${doc.created_by || 'unknown'}</span>
                            </div>
                        </div>
                        
                        <!-- COPY DOC ID BUTTON (Prominent) -->
                        <button class="btn-copy-doc-id" 
                                onclick="internalDocs.copyDocIdToClipboard('${doc.doc_id}')"
                                title="Copy document ID to paste in chat (Ctrl+K)">
                            <i class="fas fa-copy"></i>
                            <span class="doc-id-text">${doc.doc_id}</span>
                            <span class="copy-hint">Click to copy • Paste in chat to reference</span>
                        </button>
                    </div>
                    
                    <!-- Collaboration Bar -->
                    <div class="collaboration-bar" id="collaboration-bar" style="display: none;">
                        <div class="collaborators" id="collaborators-list">
                            <i class="fas fa-users"></i>
                            <span id="collaborator-count">0 active</span>
                        </div>
                        <div class="sync-status" id="sync-status">
                            <i class="fas fa-check-circle"></i>
                            <span>Synced</span>
                        </div>
                    </div>
                    
                    <button class="modal-close" onclick="internalDocs.closeDocument()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="modal-body">
                    <!-- Rich Text Editor -->
                    <div id="richtext-container" style="display: ${doc.doc_type === 'spreadsheet' ? 'none' : 'block'};">
                        <div class="editor-toolbar" id="editor-toolbar"></div>
                        <div id="tiptap-editor" class="tiptap-editor-content"></div>
                    </div>
                    
                    <!-- Spreadsheet Editor -->
                    <div id="spreadsheet-container" style="display: ${doc.doc_type === 'spreadsheet' ? 'block' : 'none'};">
                        <div class="spreadsheet-toolbar" id="spreadsheet-toolbar"></div>
                        <div id="handsontable-editor" class="handsontable-container"></div>
                    </div>
                    
                    <!-- AI Suggestion Panel (Collapsible) -->
                    <div class="ai-panel" id="ai-panel" style="display: none;">
                        <div class="ai-panel-header" onclick="this.parentElement.classList.toggle('collapsed')">
                            <i class="fas fa-robot"></i>
                            <span>AI Assistant</span>
                            <i class="fas fa-chevron-down"></i>
                        </div>
                        <div class="ai-panel-content">
                            <div id="ai-suggestions"></div>
                            <button class="btn-ai-action" onclick="internalDocs.askAI()">
                                <i class="fas fa-magic"></i> Ask AI to improve this
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="modal-footer">
                    <div class="footer-left">
                        <!-- Export Options -->
                        <div class="dropdown">
                            <button class="btn-secondary dropdown-toggle">
                                <i class="fas fa-download"></i> Export
                            </button>
                            <div class="dropdown-menu">
                                <button onclick="internalDocs.exportDocument('${doc.doc_id}', 'markdown')">
                                    <i class="fab fa-markdown"></i> Markdown
                                </button>
                                <button onclick="internalDocs.exportDocument('${doc.doc_id}', 'html')">
                                    <i class="fas fa-code"></i> HTML
                                </button>
                                <button onclick="internalDocs.exportDocument('${doc.doc_id}', 'word')">
                                    <i class="fab fa-microsoft"></i> Word DOCX
                                </button>
                                <button onclick="internalDocs.exportDocument('${doc.doc_id}', 'google_doc')">
                                    <i class="fab fa-google"></i> Google Doc
                                </button>
                                <button onclick="internalDocs.exportDocument('${doc.doc_id}', 'pdf')">
                                    <i class="fas fa-file-pdf"></i> PDF
                                </button>
                                ${doc.doc_type === 'spreadsheet' ? `
                                <button onclick="internalDocs.exportDocument('${doc.doc_id}', 'excel')">
                                    <i class="fas fa-file-excel"></i> Excel
                                </button>
                                <button onclick="internalDocs.exportDocument('${doc.doc_id}', 'csv')">
                                    <i class="fas fa-file-csv"></i> CSV
                                </button>
                                ` : ''}
                            </div>
                        </div>
                        
                        <!-- Share Button -->
                        <button class="btn-secondary" onclick="internalDocs.shareDocument('${doc.doc_id}')">
                            <i class="fas fa-share-alt"></i> Share
                        </button>
                        
                        <!-- Version History -->
                        <button class="btn-secondary" onclick="internalDocs.showVersionHistory('${doc.doc_id}')">
                            <i class="fas fa-history"></i> History
                        </button>
                        
                        <!-- AI Link (Drag to Sessions) -->
                        <div class="ai-link-indicator ${doc.linked_to_ai ? 'active' : ''}" 
                             id="ai-link-indicator"
                             title="${doc.linked_to_ai ? 'Linked to AI session' : 'Drag this doc to a session to link'}">
                            <i class="fas fa-link"></i>
                            <span>${doc.linked_to_ai ? 'AI Linked' : 'Not Linked'}</span>
                        </div>
                    </div>
                    
                    <div class="footer-right">
                        <!-- Auto-save indicator -->
                        <div class="auto-save-indicator" id="auto-save-indicator">
                            <i class="fas fa-check-circle"></i>
                            <span>Saved 2 min ago</span>
                        </div>
                        
                        <!-- Word count -->
                        <div class="word-count" id="word-count">
                            <i class="fas fa-font"></i>
                            <span>0 words</span>
                        </div>
                        
                        <button class="btn-secondary" onclick="internalDocs.closeDocument()">
                            <i class="fas fa-times"></i> Close
                        </button>
                        <button class="btn-primary" onclick="internalDocs.saveCurrentDoc()">
                            <i class="fas fa-save"></i> Save
                        </button>
                    </div>
                </div>
            </div>
        `;

        return modal;
    }

    // ============================================================================
    // RICH TEXT EDITOR (TipTap)
    // ============================================================================

    async initRichTextEditor(doc) {
        const container = document.getElementById('tiptap-editor');
        const toolbar = document.getElementById('editor-toolbar');

        // Create toolbar
        toolbar.innerHTML = this.createRichTextToolbar();

        // Initialize TipTap editor
        const extensions = [
            window.TiptapStarterKit.StarterKit,
            // Add more extensions as needed
        ];

        if (this.enableCollaboration && window.TiptapCollaboration) {
            // Add collaboration extension
            extensions.push(
                window.TiptapCollaboration.Collaboration.configure({
                    document: this.collaborationProvider.doc,
                })
            );
        }

        this.richTextEditor = new window.TiptapCore.Editor({
            element: container,
            extensions: extensions,
            content: doc.content || '',
            onUpdate: ({ editor }) => {
                this.scheduleAutoSave();
                this.updateWordCount();
            },
            editorProps: {
                attributes: {
                    class: 'prose prose-invert max-w-none',
                    spellcheck: 'true'
                }
            }
        });

        // Setup toolbar event listeners
        this.setupRichTextToolbarEvents();

        console.log('[InternalDocs] Rich text editor initialized');
    }

    createRichTextToolbar() {
        return `
            <div class="toolbar-group">
                <button class="toolbar-btn" data-action="undo" title="Undo (Ctrl+Z)">
                    <i class="fas fa-undo"></i>
                </button>
                <button class="toolbar-btn" data-action="redo" title="Redo (Ctrl+Y)">
                    <i class="fas fa-redo"></i>
                </button>
            </div>
            
            <div class="toolbar-group">
                <button class="toolbar-btn" data-action="bold" title="Bold (Ctrl+B)">
                    <i class="fas fa-bold"></i>
                </button>
                <button class="toolbar-btn" data-action="italic" title="Italic (Ctrl+I)">
                    <i class="fas fa-italic"></i>
                </button>
                <button class="toolbar-btn" data-action="underline" title="Underline (Ctrl+U)">
                    <i class="fas fa-underline"></i>
                </button>
                <button class="toolbar-btn" data-action="strike" title="Strikethrough">
                    <i class="fas fa-strikethrough"></i>
                </button>
                <button class="toolbar-btn" data-action="code" title="Code">
                    <i class="fas fa-code"></i>
                </button>
            </div>
            
            <div class="toolbar-group">
                <select class="toolbar-select" data-action="heading" title="Heading">
                    <option value="">Normal</option>
                    <option value="1">Heading 1</option>
                    <option value="2">Heading 2</option>
                    <option value="3">Heading 3</option>
                    <option value="4">Heading 4</option>
                    <option value="5">Heading 5</option>
                    <option value="6">Heading 6</option>
                </select>
            </div>
            
            <div class="toolbar-group">
                <button class="toolbar-btn" data-action="bulletList" title="Bullet List">
                    <i class="fas fa-list-ul"></i>
                </button>
                <button class="toolbar-btn" data-action="orderedList" title="Numbered List">
                    <i class="fas fa-list-ol"></i>
                </button>
                <button class="toolbar-btn" data-action="taskList" title="Task List">
                    <i class="fas fa-tasks"></i>
                </button>
            </div>
            
            <div class="toolbar-group">
                <button class="toolbar-btn" data-action="alignLeft" title="Align Left">
                    <i class="fas fa-align-left"></i>
                </button>
                <button class="toolbar-btn" data-action="alignCenter" title="Align Center">
                    <i class="fas fa-align-center"></i>
                </button>
                <button class="toolbar-btn" data-action="alignRight" title="Align Right">
                    <i class="fas fa-align-right"></i>
                </button>
                <button class="toolbar-btn" data-action="alignJustify" title="Justify">
                    <i class="fas fa-align-justify"></i>
                </button>
            </div>
            
            <div class="toolbar-group">
                <button class="toolbar-btn" data-action="insertTable" title="Insert Table">
                    <i class="fas fa-table"></i>
                </button>
                <button class="toolbar-btn" data-action="insertImage" title="Insert Image">
                    <i class="fas fa-image"></i>
                </button>
                <button class="toolbar-btn" data-action="insertLink" title="Insert Link (Ctrl+K)">
                    <i class="fas fa-link"></i>
                </button>
                <button class="toolbar-btn" data-action="insertCodeBlock" title="Code Block">
                    <i class="fas fa-file-code"></i>
                </button>
            </div>
            
            <div class="toolbar-group">
                <button class="toolbar-btn" data-action="blockquote" title="Blockquote">
                    <i class="fas fa-quote-right"></i>
                </button>
                <button class="toolbar-btn" data-action="horizontalRule" title="Horizontal Rule">
                    <i class="fas fa-minus"></i>
                </button>
            </div>
            
            <div class="toolbar-group">
                <input type="color" class="toolbar-color" data-action="textColor" title="Text Color" />
                <input type="color" class="toolbar-color" data-action="backgroundColor" title="Highlight" />
            </div>
            
            <div class="toolbar-group">
                <button class="toolbar-btn" data-action="clearFormat" title="Clear Formatting">
                    <i class="fas fa-eraser"></i>
                </button>
            </div>
        `;
    }

    setupRichTextToolbarEvents() {
        const toolbar = document.getElementById('editor-toolbar');

        toolbar.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-action]');
            if (!btn || !this.richTextEditor) return;

            const action = btn.dataset.action;
            this.executeEditorAction(action);
        });

        toolbar.addEventListener('change', (e) => {
            if (e.target.matches('[data-action="heading"]')) {
                const level = parseInt(e.target.value);
                if (level) {
                    this.richTextEditor.chain().focus().toggleHeading({ level }).run();
                } else {
                    this.richTextEditor.chain().focus().setParagraph().run();
                }
            }
        });
    }

    executeEditorAction(action) {
        if (!this.richTextEditor) return;

        const actions = {
            undo: () => this.richTextEditor.chain().focus().undo().run(),
            redo: () => this.richTextEditor.chain().focus().redo().run(),
            bold: () => this.richTextEditor.chain().focus().toggleBold().run(),
            italic: () => this.richTextEditor.chain().focus().toggleItalic().run(),
            underline: () => this.richTextEditor.chain().focus().toggleUnderline().run(),
            strike: () => this.richTextEditor.chain().focus().toggleStrike().run(),
            code: () => this.richTextEditor.chain().focus().toggleCode().run(),
            bulletList: () => this.richTextEditor.chain().focus().toggleBulletList().run(),
            orderedList: () => this.richTextEditor.chain().focus().toggleOrderedList().run(),
            blockquote: () => this.richTextEditor.chain().focus().toggleBlockquote().run(),
            horizontalRule: () => this.richTextEditor.chain().focus().setHorizontalRule().run(),
            clearFormat: () => this.richTextEditor.chain().focus().clearNodes().unsetAllMarks().run(),
            insertTable: () => this.insertTable(),
            insertLink: () => this.insertLink(),
            // Add more actions as needed
        };

        if (actions[action]) {
            actions[action]();
        }
    }

    insertTable() {
        const rows = prompt('Number of rows:', '3');
        const cols = prompt('Number of columns:', '3');

        if (rows && cols && this.richTextEditor) {
            this.richTextEditor.chain().focus().insertTable({
                rows: parseInt(rows),
                cols: parseInt(cols),
                withHeaderRow: true
            }).run();
        }
    }

    insertLink() {
        const url = prompt('Enter URL:');
        if (url && this.richTextEditor) {
            this.richTextEditor.chain().focus().setLink({ href: url }).run();
        }
    }

    // ============================================================================
    // SPREADSHEET EDITOR (Handsontable)
    // ============================================================================

    async initSpreadsheetEditor(doc) {
        const container = document.getElementById('handsontable-editor');
        const toolbar = document.getElementById('spreadsheet-toolbar');

        // Create toolbar
        toolbar.innerHTML = this.createSpreadsheetToolbar();

        // Parse content (should be JSON)
        let data = [];
        try {
            if (doc.content_json) {
                data = JSON.parse(doc.content_json);
            } else if (doc.content) {
                data = JSON.parse(doc.content);
            }
        } catch (e) {
            // Default empty spreadsheet
            data = Array(20).fill().map(() => Array(10).fill(''));
        }

        // Initialize Handsontable
        this.spreadsheetEditor = new Handsontable(container, {
            data: data,
            rowHeaders: true,
            colHeaders: true,
            width: '100%',
            height: 600,
            licenseKey: 'non-commercial-and-evaluation',
            formulas: {
                engine: HyperFormula
            },
            contextMenu: true,
            manualColumnResize: true,
            manualRowResize: true,
            columnSorting: true,
            filters: true,
            dropdownMenu: ['filter_by_condition', 'filter_action_bar'],
            mergeCells: true,
            comments: this.enableCollaboration,
            afterChange: (changes, source) => {
                if (source !== 'loadData') {
                    this.scheduleAutoSave();
                }
            }
        });

        // Setup toolbar events
        this.setupSpreadsheetToolbarEvents();

        console.log('[InternalDocs] Spreadsheet editor initialized');
    }

    createSpreadsheetToolbar() {
        return `
            <div class="toolbar-group">
                <button class="toolbar-btn" data-action="undo" title="Undo">
                    <i class="fas fa-undo"></i>
                </button>
                <button class="toolbar-btn" data-action="redo" title="Redo">
                    <i class="fas fa-redo"></i>
                </button>
            </div>
            
            <div class="toolbar-group">
                <button class="toolbar-btn" data-action="addRowAbove" title="Insert Row Above">
                    <i class="fas fa-plus"></i> Row Above
                </button>
                <button class="toolbar-btn" data-action="addRowBelow" title="Insert Row Below">
                    <i class="fas fa-plus"></i> Row Below
                </button>
                <button class="toolbar-btn" data-action="removeRow" title="Delete Row">
                    <i class="fas fa-minus"></i> Row
                </button>
            </div>
            
            <div class="toolbar-group">
                <button class="toolbar-btn" data-action="addColumnLeft" title="Insert Column Left">
                    <i class="fas fa-plus"></i> Column Left
                </button>
                <button class="toolbar-btn" data-action="addColumnRight" title="Insert Column Right">
                    <i class="fas fa-plus"></i> Column Right
                </button>
                <button class="toolbar-btn" data-action="removeColumn" title="Delete Column">
                    <i class="fas fa-minus"></i> Column
                </button>
            </div>
            
            <div class="toolbar-group">
                <button class="toolbar-btn" data-action="mergeCells" title="Merge Cells">
                    <i class="fas fa-compress"></i> Merge
                </button>
                <button class="toolbar-btn" data-action="unmergeCells" title="Unmerge Cells">
                    <i class="fas fa-expand"></i> Unmerge
                </button>
            </div>
            
            <div class="toolbar-group">
                <button class="toolbar-btn" data-action="sort" title="Sort Data">
                    <i class="fas fa-sort"></i> Sort
                </button>
                <button class="toolbar-btn" data-action="filter" title="Filter Data">
                    <i class="fas fa-filter"></i> Filter
                </button>
            </div>
            
            <div class="toolbar-group">
                <button class="toolbar-btn" data-action="formatCurrency" title="Currency Format">
                    <i class="fas fa-dollar-sign"></i>
                </button>
                <button class="toolbar-btn" data-action="formatPercent" title="Percent Format">
                    <i class="fas fa-percentage"></i>
                </button>
                <button class="toolbar-btn" data-action="formatNumber" title="Number Format">
                    <i class="fas fa-hashtag"></i>
                </button>
            </div>
            
            <div class="toolbar-group">
                <button class="toolbar-btn" data-action="insertChart" title="Insert Chart">
                    <i class="fas fa-chart-bar"></i> Chart
                </button>
            </div>
        `;
    }

    setupSpreadsheetToolbarEvents() {
        const toolbar = document.getElementById('spreadsheet-toolbar');

        toolbar.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-action]');
            if (!btn || !this.spreadsheetEditor) return;

            const action = btn.dataset.action;
            this.executeSpreadsheetAction(action);
        });
    }

    executeSpreadsheetAction(action) {
        if (!this.spreadsheetEditor) return;

        const selected = this.spreadsheetEditor.getSelected();

        const actions = {
            undo: () => this.spreadsheetEditor.undo(),
            redo: () => this.spreadsheetEditor.redo(),
            addRowAbove: () => this.spreadsheetEditor.alter('insert_row_above'),
            addRowBelow: () => this.spreadsheetEditor.alter('insert_row_below'),
            removeRow: () => selected && this.spreadsheetEditor.alter('remove_row', selected[0][0]),
            addColumnLeft: () => this.spreadsheetEditor.alter('insert_col_start'),
            addColumnRight: () => this.spreadsheetEditor.alter('insert_col_end'),
            removeColumn: () => selected && this.spreadsheetEditor.alter('remove_col', selected[0][1]),
            mergeCells: () => this.mergeCells(),
            unmergeCells: () => this.unmergeCells(),
            // Add more actions
        };

        if (actions[action]) {
            actions[action]();
        }
    }

    mergeCells() {
        const selected = this.spreadsheetEditor.getSelected();
        if (selected && selected.length > 0) {
            const [startRow, startCol, endRow, endCol] = selected[0];
            this.spreadsheetEditor.getPlugin('mergeCells').merge(startRow, startCol, endRow, endCol);
        }
    }

    unmergeCells() {
        const selected = this.spreadsheetEditor.getSelected();
        if (selected && selected.length > 0) {
            const [startRow, startCol] = selected[0];
            this.spreadsheetEditor.getPlugin('mergeCells').unmerge(startRow, startCol);
        }
    }

    // ============================================================================
    // COLLABORATION (Y.js)
    // ============================================================================

    async initCollaboration(docId) {
        if (!window.Y || !window.WebsocketProvider) {
            console.warn('[InternalDocs] Collaboration libraries not loaded');
            return;
        }

        try {
            // Create Y.js document
            const ydoc = new window.Y.Doc();

            // Connect to WebSocket server
            const wsUrl = `ws://${window.location.host}/collab`;
            this.collaborationProvider = new window.WebsocketProvider(wsUrl, docId, ydoc);

            // Setup awareness (user presence)
            const awareness = this.collaborationProvider.awareness;
            awareness.setLocalStateField('user', {
                id: this.userId,
                name: `User ${this.userId}`,
                color: this.generateUserColor(this.userId)
            });

            // Listen for awareness changes
            awareness.on('change', () => {
                this.updateCollaborators();
            });

            // Show collaboration bar
            document.getElementById('collaboration-bar').style.display = 'flex';

            console.log('[InternalDocs] Collaboration initialized');
        } catch (error) {
            console.error('[InternalDocs] Collaboration error:', error);
        }
    }

    updateCollaborators() {
        if (!this.collaborationProvider) return;

        const awareness = this.collaborationProvider.awareness;
        const states = awareness.getStates();

        const collaboratorsList = document.getElementById('collaborators-list');
        const collaboratorCount = document.getElementById('collaborator-count');

        // Update count (exclude self)
        const count = states.size - 1;
        collaboratorCount.textContent = `${count} active`;

        // Update list
        let html = '<i class="fas fa-users"></i> ';
        states.forEach((state, clientId) => {
            if (clientId !== awareness.clientID && state.user) {
                html += `<span class="collaborator-avatar" 
                              style="background: ${state.user.color}"
                              title="${state.user.name}">
                            ${state.user.name[0]}
                        </span>`;
            }
        });
        html += `<span id="collaborator-count">${count} active</span>`;

        collaboratorsList.innerHTML = html;
    }

    generateUserColor(userId) {
        const colors = [
            '#4f6cff', '#10b981', '#f59e0b', '#ef4444',
            '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'
        ];
        return colors[userId % colors.length];
    }

    // ============================================================================
    // AI INTEGRATION
    // ============================================================================

    /**
     * Copy document ID to clipboard for AI reference
     */
    async copyDocIdToClipboard(docId) {
        try {
            const doc = await this.getDocument(docId);
            const copyText = `[DOC:${docId}:${doc.title}]`;

            await navigator.clipboard.writeText(copyText);

            // Visual feedback
            const btn = document.querySelector('.btn-copy-doc-id');
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-check"></i> Copied! Paste in chat to reference';
            btn.style.background = '#10b981';

            setTimeout(() => {
                btn.innerHTML = originalHTML;
                btn.style.background = '';
            }, 2000);

            console.log('[InternalDocs] Doc ID copied:', copyText);
        } catch (error) {
            console.error('[InternalDocs] Copy error:', error);
            alert('Failed to copy: ' + error.message);
        }
    }

    /**
     * Link document to AI session
     */
    async linkToAISession(docId, sessionId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/internal-doc/${docId}/link-ai`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    user_id: this.userId
                })
            });

            const data = await response.json();

            if (data.success) {
                // Update UI
                const indicator = document.getElementById('ai-link-indicator');
                if (indicator) {
                    indicator.classList.add('active');
                    indicator.querySelector('span').textContent = 'AI Linked';
                    indicator.title = `Linked to session ${sessionId}`;
                }

                console.log('[InternalDocs] Doc linked to AI session:', sessionId);
                return true;
            }

            return false;
        } catch (error) {
            console.error('[InternalDocs] Link error:', error);
            return false;
        }
    }

    /**
     * Ask AI to improve document
     */
    async askAI() {
        if (!this.currentDoc) return;

        const content = this.richTextEditor ?
            this.richTextEditor.getText() :
            JSON.stringify(this.spreadsheetEditor.getData());

        try {
            const response = await fetch('/api/agent/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: `Please improve this document:\n\n${content}`,
                    user_id: this.userId,
                    context: {
                        doc_id: this.currentDoc.doc_id,
                        doc_type: this.currentDoc.doc_type
                    }
                })
            });

            const data = await response.json();

            if (data.success) {
                // Show AI suggestions
                const panel = document.getElementById('ai-suggestions');
                panel.innerHTML = `<div class="ai-suggestion">${data.response}</div>`;
                document.getElementById('ai-panel').style.display = 'block';
            }
        } catch (error) {
            console.error('[InternalDocs] AI error:', error);
        }
    }

    // ============================================================================
    // AUTO-SAVE & SAVING
    // ============================================================================

    scheduleAutoSave() {
        if (this.autoSaveTimeout) {
            clearTimeout(this.autoSaveTimeout);
        }

        this.autoSaveTimeout = setTimeout(() => {
            this.saveCurrentDoc(true);
        }, 2000); // 2 second debounce
    }

    startAutoSave() {
        this.stopAutoSave();

        this.autoSaveInterval = setInterval(() => {
            this.saveCurrentDoc(true);
        }, this.autoSaveDelay);
    }

    stopAutoSave() {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
            this.autoSaveInterval = null;
        }

        if (this.autoSaveTimeout) {
            clearTimeout(this.autoSaveTimeout);
            this.autoSaveTimeout = null;
        }
    }

    async saveCurrentDoc(isAutoSave = false) {
        if (!this.currentDoc) return;

        try {
            // Get content based on editor type
            let content, contentJson;

            if (this.richTextEditor) {
                content = this.richTextEditor.getText(); // Markdown
                contentJson = JSON.stringify(this.richTextEditor.getJSON());
            } else if (this.spreadsheetEditor) {
                const data = this.spreadsheetEditor.getData();
                content = JSON.stringify(data);
                contentJson = content;
            }

            // Get title
            const titleInput = document.getElementById('doc-title');
            const title = titleInput ? titleInput.value : this.currentDoc.title;

            // Save to backend
            const response = await fetch(`${this.apiBaseUrl}/internal-doc/${this.currentDoc.doc_id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title,
                    content,
                    content_json: contentJson
                })
            });

            const data = await response.json();

            if (data.success) {
                // Update UI
                this.currentDoc.version = data.version;
                this.updateSaveIndicator(isAutoSave);

                if (!isAutoSave) {
                    console.log('[InternalDocs] Document saved:', this.currentDoc.doc_id);
                }
            }
        } catch (error) {
            console.error('[InternalDocs] Save error:', error);
        }
    }

    updateSaveIndicator(isAutoSave) {
        const indicator = document.getElementById('auto-save-indicator');
        if (!indicator) return;

        const icon = indicator.querySelector('i');
        const text = indicator.querySelector('span');

        icon.className = 'fas fa-check-circle';
        icon.style.color = '#10b981';
        text.textContent = isAutoSave ? 'Auto-saved just now' : 'Saved';

        // Update sync status for collaboration
        const syncStatus = document.getElementById('sync-status');
        if (syncStatus && this.enableCollaboration) {
            syncStatus.querySelector('i').className = 'fas fa-check-circle';
            syncStatus.querySelector('span').textContent = 'Synced';
        }
    }

    updateWordCount() {
        if (!this.richTextEditor) return;

        const text = this.richTextEditor.getText();
        const words = text.trim().split(/\s+/).filter(w => w.length > 0).length;
        const chars = text.length;

        const wordCount = document.getElementById('word-count');
        if (wordCount) {
            wordCount.innerHTML = `
                <i class="fas fa-font"></i>
                <span>${words} words • ${chars} chars</span>
            `;
        }
    }

    // ============================================================================
    // EXPORT
    // ============================================================================

    async exportDocument(docId, format) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/internal-doc/${docId}/export/${format}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: this.userId })
            });

            if (format === 'word' || format === 'excel' || format === 'pdf') {
                // Download file
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `document.${format === 'word' ? 'docx' : format === 'excel' ? 'xlsx' : 'pdf'}`;
                a.click();
            } else {
                // Show URL or content
                const data = await response.json();
                if (data.url) {
                    window.open(data.url, '_blank');
                }
            }

            console.log('[InternalDocs] Exported as:', format);
        } catch (error) {
            console.error('[InternalDocs] Export error:', error);
            alert('Export failed: ' + error.message);
        }
    }

    // ============================================================================
    // UTILITIES
    // ============================================================================

    async getDocument(docId) {
        const response = await fetch(`${this.apiBaseUrl}/internal-doc/${docId}`);
        const data = await response.json();
        return data;
    }

    closeDocument() {
        // Stop auto-save
        this.stopAutoSave();

        // Destroy editors
        if (this.richTextEditor) {
            this.richTextEditor.destroy();
            this.richTextEditor = null;
        }

        if (this.spreadsheetEditor) {
            this.spreadsheetEditor.destroy();
            this.spreadsheetEditor = null;
        }

        // Disconnect collaboration
        if (this.collaborationProvider) {
            this.collaborationProvider.disconnect();
            this.collaborationProvider = null;
        }

        // Remove modal
        const modal = document.getElementById('internal-doc-modal');
        if (modal) {
            modal.remove();
        }

        this.currentDoc = null;

        console.log('[InternalDocs] Document closed');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    shareDocument(docId) {
        // TODO: Implement sharing dialog
        alert('Sharing coming soon!');
    }

    showVersionHistory(docId) {
        // TODO: Implement version history
        alert('Version history coming soon!');
    }
}

// Export as global
window.InternalDocsManager = InternalDocsManager;

// Create default instance
window.internalDocs = new InternalDocsManager({
    apiBaseUrl: '/api/synergy',
    userId: 1, // Get from session
    enableCollaboration: true,
    enableAI: true
});

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.internalDocs.init();
    });
} else {
    window.internalDocs.init();
}
