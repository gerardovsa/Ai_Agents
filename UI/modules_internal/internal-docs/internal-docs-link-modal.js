/**
 * INTERNAL DOCS LINK MODAL
 * Modal interface for linking Internal Docs/Sheets (synergy_internal_docs) to threads
 * Matches synergy-sync-modal structure for consistency
 * Color theme: Amber (#f59e0b)
 */

window.ThreadManager = window.ThreadManager || {};

// Ensure a global wrapper exists early so integrations can call it before full init
window.InternalDocsLinkModal = window.InternalDocsLinkModal || {
    open: function (threadId) {
        window.__modalCallQueue = window.__modalCallQueue || [];
        window.__modalCallQueue.push({ method: 'openInternalDocsLinkModal', args: [threadId] });
        if (!window.__modalCallQueue._polling) {
            window.__modalCallQueue._polling = true;
            const poll = setInterval(() => {
                if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.openInternalDocsLinkModal === 'function') {
                    try {
                        while (window.__modalCallQueue.length > 0) {
                            const job = window.__modalCallQueue.shift();
                            if (typeof ThreadManager[job.method] === 'function') {
                                ThreadManager[job.method].apply(ThreadManager, job.args);
                            }
                        }
                    } catch (e) {
                        console.error('[InternalDocsLinkModal] Error flushing queue', e);
                    }
                    clearInterval(poll);
                    window.__modalCallQueue._polling = false;
                }
            }, 200);
        }
    }
};

/**
 * Open the internal docs link modal for a specific thread
 * @param {number} threadId - Thread ID to link doc to
 */
ThreadManager.openInternalDocsLinkModal = async function (threadId) {
    // Store thread ID for later use
    window._internalDocsLinkThreadId = threadId;

    // Get thread title for display
    const threadCard = document.querySelector(`[data-thread-id="${threadId}"]`);
    const threadTitle = threadCard ?
        (threadCard.querySelector('.thread-title')?.textContent || 'Unknown Thread') :
        'Unknown Thread';

    // Fetch available internal docs
    let internalDocs = [];
    try {
        const response = await fetch('/api/synergy/internal-docs/list', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
        });

        if (response.ok) {
            const data = await response.json();
            // Handle different response formats
            if (Array.isArray(data)) {
                internalDocs = data;
            } else if (data && data.success && Array.isArray(data.docs)) {
                internalDocs = data.docs;
            } else if (data && Array.isArray(data.docs)) {
                internalDocs = data.docs;
            }
            window._internalDocs = internalDocs; // Store for filtering
            console.log('[Internal Docs Modal] Fetched:', internalDocs.length, 'docs');
        } else {
            console.error('[Internal Docs Modal] API error:', response.status, response.statusText);
        }
    } catch (error) {
        console.error('[Internal Docs Modal] Failed to fetch internal docs:', error);
    }

    // Generate modal HTML
    const modalHTML = `
        <div class="modal-overlay" onclick="ThreadManager.closeInternalDocsLinkModal(event)">
            <div class="internal-docs-link-modal" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3><i class="fas fa-file-alt"></i> Link Synergy Doc/Sheet</h3>
                    <button class="modal-close" onclick="ThreadManager.closeInternalDocsLinkModal()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="modal-body">
                    <div class="internal-docs-link-thread-info">
                        Linking to thread: <strong>${threadTitle}</strong>
                    </div>
                    
                    <!-- Tab Navigation -->
                    <div class="internal-docs-link-tabs">
                        <button class="internal-docs-link-tab active" 
                                onclick="ThreadManager.switchInternalDocsLinkTab('existing')">
                            <i class="fas fa-link"></i> Link Existing
                        </button>
                        <button class="internal-docs-link-tab" 
                                onclick="ThreadManager.switchInternalDocsLinkTab('quick')">
                            <i class="fas fa-plus-circle"></i> Quick Create
                        </button>
                        <button class="internal-docs-link-tab" 
                                onclick="ThreadManager.switchInternalDocsLinkTab('full')">
                            <i class="fas fa-external-link-alt"></i> Full Create
                        </button>
                    </div>
                    
                    <!-- Tab 1: Link Existing Doc -->
                    <div id="internalDocsLinkTabExisting" class="internal-docs-link-tab-content active">
                        <div class="internal-docs-link-controls">
                            <div class="internal-docs-link-search">
                                <i class="fas fa-search"></i>
                                <input type="text" id="internalDocsLinkSearch" 
                                       placeholder="Search docs and sheets..." 
                                       oninput="ThreadManager.filterInternalDocsList()">
                            </div>
                            <select id="internalDocsLinkSort" onchange="ThreadManager.filterInternalDocsList()">
                                <option value="recent">Most Recent</option>
                                <option value="name">Name (A-Z)</option>
                                <option value="type">By Type</option>
                                <option value="modified">Last Modified</option>
                            </select>
                        </div>
                        
                        <div class="internal-docs-link-list" id="internalDocsLinkList">
                            ${ThreadManager.renderInternalDocsList(internalDocs)}
                        </div>
                    </div>
                    
                    <!-- Tab 2: Quick Create -->
                    <div id="internalDocsLinkTabQuick" class="internal-docs-link-tab-content">
                        <div class="internal-docs-quick-create">
                            <div class="form-group">
                                <label for="quickDocTitle">Document Name</label>
                                <input type="text" id="quickDocTitle" 
                                       placeholder="e.g., Project Requirements">
                            </div>
                            
                            <div class="form-group">
                                <label for="quickDocType">Document Type</label>
                                <select id="quickDocType">
                                    <option value="doc">Document (Google Doc)</option>
                                    <option value="sheet">Spreadsheet (Google Sheet)</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label for="quickDocDesc">Description (Optional)</label>
                                <textarea id="quickDocDesc" 
                                          placeholder="Brief description of the document..."></textarea>
                            </div>
                            
                            <button class="btn btn-primary" 
                                    onclick="ThreadManager.quickCreateInternalDocAndLink(${threadId})">
                                <i class="fas fa-plus-circle"></i> Create & Link Document
                            </button>
                        </div>
                    </div>
                    
                    <!-- Tab 3: Full Create -->
                    <div id="internalDocsLinkTabFull" class="internal-docs-link-tab-content">
                        <div class="internal-docs-full-create">
                            <p>Open Google Drive to create a new document or spreadsheet with full formatting options.</p>
                            <button class="btn btn-primary" 
                                    onclick="ThreadManager.fullCreateInternalDocAndLink(${threadId})">
                                <i class="fas fa-external-link-alt"></i> Open Google Drive
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Inject modal into DOM
    const existingModal = document.querySelector('.modal-overlay');
    if (existingModal) {
        existingModal.remove();
        console.log('[Internal Docs Modal] Removed existing modal');
    }

    document.body.insertAdjacentHTML('beforeend', modalHTML);
    console.log('[Internal Docs Modal] ✅ Modal HTML inserted into DOM');

    // Verify modal was added
    const addedModal = document.querySelector('.internal-docs-link-modal');
    if (addedModal) {
        console.log('[Internal Docs Modal] ✅ Modal element found in DOM');
    } else {
        console.error('[Internal Docs Modal] ❌ Modal element NOT found after insertion!');
    }
};

// Persistence helper: ensure main modal function stays attached to ThreadManager
// even if ThreadManager is reassigned by other scripts
(function ensureInternalDocsMethodsAttached() {
    // Capture the main open function (others are helper methods, not on ThreadManager)
    const openModalFn = ThreadManager.openInternalDocsLinkModal;

    if (typeof openModalFn !== 'function') {
        console.warn('[InternalDocsLinkModal] openInternalDocsLinkModal not yet defined, will retry');
    }

    let attempts = 0;
    const maxAttempts = 60; // ~12 seconds
    const iv = setInterval(() => {
        attempts += 1;
        if (typeof window.ThreadManager !== 'undefined' && typeof openModalFn === 'function') {
            try {
                window.ThreadManager.openInternalDocsLinkModal = openModalFn;
                console.debug('[InternalDocsLinkModal] Attached openInternalDocsLinkModal to window.ThreadManager');
                clearInterval(iv);
                return;
            } catch (e) {
                console.warn('[InternalDocsLinkModal] attach attempt failed, will retry', e);
            }
        }

        if (attempts >= maxAttempts) {
            clearInterval(iv);
            console.warn('[InternalDocsLinkModal] Giving up attaching after 12 seconds');
        }
    }, 200);
})();

/**
 * Render list of internal doc items
 * ✅ UPDATED: Now uses centralized SynergyDocCardRenderer
 * @param {Array} docs - Array of internal doc objects
 * @returns {string} HTML string
 */
ThreadManager.renderInternalDocsList = function (docs) {
    // Use centralized renderer
    if (!window.SynergyDocCardRenderer) {
        console.error('[INTERNAL DOCS LINK MODAL] SynergyDocCardRenderer not loaded!');
        return '<div class="internal-docs-link-empty"><p>Card renderer not available</p></div>';
    }

    return window.SynergyDocCardRenderer.renderList(docs, {
        selectable: false,
        onClick: 'ThreadManager.linkToExistingInternalDoc',
        showDescription: true,
        showType: true,
        showCreated: true,
        showModified: true,
        showOwner: true,
        showTags: false,
        variant: 'detailed',
        emptyMessage: 'No Internal Docs Found. Create your first document using the Quick Create or Full Create tabs.'
    });
};

/**
 * Switch between tabs in the internal docs link modal
 * @param {string} tabName - 'existing', 'quick', or 'full'
 */
ThreadManager.switchInternalDocsLinkTab = function (tabName) {
    // Update tab buttons
    document.querySelectorAll('.internal-docs-link-tab').forEach(tab => {
        tab.classList.remove('active');
    });

    const tabMap = {
        'existing': 0,
        'quick': 1,
        'full': 2
    };

    const activeTab = document.querySelectorAll('.internal-docs-link-tab')[tabMap[tabName]];
    if (activeTab) {
        activeTab.classList.add('active');
    }

    // Update tab content
    document.querySelectorAll('.internal-docs-link-tab-content').forEach(content => {
        content.classList.remove('active');
    });

    const contentMap = {
        'existing': 'internalDocsLinkTabExisting',
        'quick': 'internalDocsLinkTabQuick',
        'full': 'internalDocsLinkTabFull'
    };

    const activeContent = document.getElementById(contentMap[tabName]);
    if (activeContent) {
        activeContent.classList.add('active');
    }
};

/**
 * Filter and sort internal docs list based on search and sort inputs
 */
ThreadManager.filterInternalDocsList = function () {
    const searchTerm = document.getElementById('internalDocsLinkSearch')?.value.toLowerCase() || '';
    const sortBy = document.getElementById('internalDocsLinkSort')?.value || 'recent';

    let filteredDocs = window._internalDocs || [];

    // Apply search filter
    if (searchTerm) {
        filteredDocs = filteredDocs.filter(doc => {
            return (doc.doc_name?.toLowerCase().includes(searchTerm) ||
                doc.description?.toLowerCase().includes(searchTerm) ||
                doc.owner?.toLowerCase().includes(searchTerm));
        });
    }

    // Apply sorting
    filteredDocs = [...filteredDocs].sort((a, b) => {
        switch (sortBy) {
            case 'name':
                return (a.doc_name || '').localeCompare(b.doc_name || '');

            case 'type':
                return (a.doc_type || '').localeCompare(b.doc_type || '');

            case 'modified':
                return new Date(b.last_modified || b.created_at || 0) -
                    new Date(a.last_modified || a.created_at || 0);

            case 'recent':
            default:
                return new Date(b.created_at || 0) - new Date(a.created_at || 0);
        }
    });

    // Re-render list
    const listContainer = document.getElementById('internalDocsLinkList');
    if (listContainer) {
        listContainer.innerHTML = ThreadManager.renderInternalDocsList(filteredDocs);
    }
};

/**
 * Link an existing internal doc to the current thread
 * @param {string} docId - Document ID to link
 */
ThreadManager.linkToExistingInternalDoc = async function (docId) {
    const threadId = window._internalDocsLinkThreadId;
    if (!threadId) {
        console.error('No thread ID stored for linking');
        return;
    }

    try {
        const response = await fetch(`/api/threads/${threadId}/link-internal-doc`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify({ doc_id: docId })
        });

        if (response.ok) {
            console.log('Internal doc linked successfully');

            // Close modal
            ThreadManager.closeInternalDocsLinkModal();

            // Refresh thread card to show new badge
            if (ThreadManager.refreshThreadCard) {
                ThreadManager.refreshThreadCard(threadId);
            }

            // Show success notification
            if (window.showNotification) {
                window.showNotification('Document linked successfully', 'success');
            }
        } else {
            console.error('Failed to link internal doc');
            if (window.showNotification) {
                window.showNotification('Failed to link document', 'error');
            }
        }
    } catch (error) {
        console.error('Error linking internal doc:', error);
        if (window.showNotification) {
            window.showNotification('Error linking document', 'error');
        }
    }
};

/**
 * Quick create a new internal doc and link it to the thread
 * @param {number} threadId - Thread ID to link to
 */
ThreadManager.quickCreateInternalDocAndLink = async function (threadId) {
    const title = document.getElementById('quickDocTitle')?.value.trim();
    const description = document.getElementById('quickDocDesc')?.value.trim();
    const docType = document.getElementById('quickDocType')?.value || 'doc';

    if (!title) {
        if (window.showNotification) {
            window.showNotification('Please enter a document name', 'warning');
        }
        return;
    }

    try {
        // Create internal doc via API
        const response = await fetch('/api/internal-docs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify({
                doc_name: title,
                description,
                doc_type: docType
            })
        });

        if (response.ok) {
            const data = await response.json();
            const docId = data.doc_id;

            // Link to thread
            await ThreadManager.linkToExistingInternalDoc(docId);

            console.log('Internal doc created and linked:', docId);
        } else {
            console.error('Failed to create internal doc');
            if (window.showNotification) {
                window.showNotification('Failed to create document', 'error');
            }
        }
    } catch (error) {
        console.error('Error creating internal doc:', error);
        if (window.showNotification) {
            window.showNotification('Error creating document', 'error');
        }
    }
};

/**
 * Open Google Drive to create a full document and link to thread
 * @param {number} threadId - Thread ID to link to
 */
ThreadManager.fullCreateInternalDocAndLink = function (threadId) {
    // Store thread ID for linking after creation
    sessionStorage.setItem('pendingInternalDocLink', threadId);

    // Close modal
    ThreadManager.closeInternalDocsLinkModal();

    // Open Google Drive in new window
    window.open('https://drive.google.com/drive/my-drive', '_blank');

    // Show notification with instructions
    if (window.showNotification) {
        window.showNotification('Create your document in Google Drive, then return to link it', 'info');
    }
};

/**
 * Close the internal docs link modal
 * @param {Event} event - Optional click event
 */
ThreadManager.closeInternalDocsLinkModal = function (event) {
    if (event && event.target.classList.contains('internal-docs-link-modal')) {
        return; // Don't close if clicking inside modal content
    }

    const modal = document.querySelector('.modal-overlay');
    if (modal) {
        modal.remove();
    }

    // Clean up stored data
    delete window._internalDocsLinkThreadId;
    delete window._internalDocs;
};

/**
 * Global wrapper for integration files
 * Makes InternalDocsLinkModal available as window.InternalDocsLinkModal
 * MUST be at end after ThreadManager.openInternalDocsLinkModal is defined
 */
window.InternalDocsLinkModal = {
    open: function (threadId) {
        // Immediate attempt
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.openInternalDocsLinkModal === 'function') {
            return ThreadManager.openInternalDocsLinkModal(threadId);
        }

        // Queue and poll until ThreadManager method is available
        window.__modalCallQueue = window.__modalCallQueue || [];
        window.__modalCallQueue.push({ method: 'openInternalDocsLinkModal', args: [threadId] });

        if (!window.__modalCallQueue._polling) {
            window.__modalCallQueue._polling = true;
            const poll = setInterval(() => {
                if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.openInternalDocsLinkModal === 'function') {
                    try {
                        while (window.__modalCallQueue.length > 0) {
                            const job = window.__modalCallQueue.shift();
                            if (typeof ThreadManager[job.method] === 'function') {
                                ThreadManager[job.method].apply(ThreadManager, job.args);
                            }
                        }
                    } catch (e) {
                        console.error('[InternalDocsLinkModal] Error flushing queue', e);
                    }
                    clearInterval(poll);
                    window.__modalCallQueue._polling = false;
                }
            }, 200);
        }
    }
};

console.log('✅ [Internal Docs Link Modal] Initialized with global wrapper: window.InternalDocsLinkModal');
