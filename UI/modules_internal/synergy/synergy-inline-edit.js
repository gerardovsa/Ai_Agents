/**
 * FILE: UI/external/modules/synergy/synergy-inline-edit.js
 * PURPOSE: Inline editing for synergy milestones/tasks/subtasks/documents
 * 
 * FEATURES:
 * - Edit directly in expanded card (NO popup)
 * - ContentEditable fields for immediate editing
 * - Save/Cancel buttons appear when editing
 * - API integration for persistence
 * 
 * ARCHITECTURE FIX (Nov 24, 2025):
 * - CRITICAL: Instance created IMMEDIATELY (not at bottom of file)
 * - Prevents "SynergyInlineEdit.editMilestone is not a function" errors
 * - Ensures global availability before any HTML injection
 * 
 * LAST MODIFIED: 2025-11-24 - Fixed timing issue with immediate registration
 */

class SynergyInlineEditClass {
    constructor() {
        this.API_BASE_URL = window.API_BASE_URL || 'http://localhost:5001';
        this.originalContent = {};
        console.log('[SYNERGY INLINE EDIT] Instance created');
    }

    // ==================== CONTEXT HELPER ====================

    /**
     * Get context-aware root element for querySelector scoping
     * Prevents cross-contamination when same session open in multiple places
     */
    getContextRoot() {
        // Check if we're in an active editing context
        const editingInSidebar = document.querySelector('#synergy-sidebar [data-editing="true"]');
        const editingInDashboard = document.querySelector('#synergy-dashboard-container [data-editing="true"]');
        const editingInPopup = document.querySelector('.synergy-popup-container [data-editing="true"]');

        // Return the specific context if something is being edited
        if (editingInSidebar) return document.querySelector('#synergy-sidebar');
        if (editingInDashboard) return document.querySelector('#synergy-dashboard-container');
        if (editingInPopup) return document.querySelector('.synergy-popup-container');

        // Fallback: try to detect from most recent event
        // This helps with initial edit button clicks before data-editing is set
        const sidebar = document.querySelector('#synergy-sidebar');
        const dashboard = document.querySelector('#synergy-dashboard-container');
        const popup = document.querySelector('.synergy-popup-container');

        // Check which context has focus or recent interaction
        if (sidebar && sidebar.querySelector(':focus')) return sidebar;
        if (dashboard && dashboard.querySelector(':focus')) return dashboard;
        if (popup && popup.querySelector(':focus')) return popup;

        // Final fallback: search all contexts, prefer sidebar > dashboard > popup
        return sidebar || dashboard || popup || document;
    }

    // ==================== MILESTONE EDITING ====================

    editMilestone(sessionId, milestoneId) {
        const contextRoot = this.getContextRoot();
        const container = contextRoot.querySelector(`[data-milestone-id="${milestoneId}"]`);
        if (!container) {
            console.warn(`[SYNERGY INLINE EDIT] Milestone ${milestoneId} not found in current context`);
            return;
        }

        // Store original content
        const titleEl = container.querySelector('.synergy-flat-milestone-title');
        const descEl = container.querySelector('.synergy-flat-milestone-desc');

        this.originalContent[milestoneId] = {
            title: titleEl ? titleEl.textContent : '',
            description: descEl ? descEl.textContent : ''
        };

        // Enable editing
        container.setAttribute('data-editing', 'true');
        if (titleEl) {
            titleEl.setAttribute('contenteditable', 'true');
            titleEl.focus();
        }
        if (descEl) descEl.setAttribute('contenteditable', 'true');

        // Show save/cancel, hide edit/delete
        this.toggleEditMode(container, true);
    }

    async saveMilestone(sessionId, milestoneId) {
        const contextRoot = this.getContextRoot();
        const container = contextRoot.querySelector(`[data-milestone-id="${milestoneId}"]`);
        if (!container) {
            console.warn(`[SYNERGY INLINE EDIT] Milestone ${milestoneId} not found for save`);
            return;
        }

        const titleEl = container.querySelector('.synergy-flat-milestone-title');
        const descEl = container.querySelector('.synergy-flat-milestone-desc');
        const priorityEl = container.querySelector('.synergy-priority-select');

        const data = {
            milestone: titleEl ? titleEl.textContent.trim() : '',
            description: descEl ? descEl.textContent.trim() : '',
            priority: priorityEl ? priorityEl.value : 'medium'
        };

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/milestone/${milestoneId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!response.ok) throw new Error('Save failed');

            // Disable editing
            container.setAttribute('data-editing', 'false');
            if (titleEl) titleEl.setAttribute('contenteditable', 'false');
            if (descEl) descEl.setAttribute('contenteditable', 'false');
            this.toggleEditMode(container, false);
            delete this.originalContent[milestoneId];

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Save error:', error);
            alert('Failed to save milestone. Please try again.');
        }
    }

    cancelEdit(sessionId, itemId) {
        const contextRoot = this.getContextRoot();
        const container = contextRoot.querySelector(`[data-milestone-id="${itemId}"], [data-task-id="${itemId}"], [data-subtask-id="${itemId}"]`);
        if (!container) return;

        // Restore original content
        if (this.originalContent[itemId]) {
            const titleEl = container.querySelector('[contenteditable]');
            if (titleEl && this.originalContent[itemId].title) {
                titleEl.textContent = this.originalContent[itemId].title;
            }
        }

        // Disable editing
        container.setAttribute('data-editing', 'false');
        container.querySelectorAll('[contenteditable]').forEach(el => {
            el.setAttribute('contenteditable', 'false');
        });
        this.toggleEditMode(container, false);
        delete this.originalContent[itemId];
    }

    async deleteMilestone(sessionId, milestoneId) {
        if (!confirm('Delete this milestone? This cannot be undone.')) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/milestone/${milestoneId}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Delete failed');

            // Remove from DOM
            const contextRoot = this.getContextRoot();
            const container = contextRoot.querySelector(`[data-milestone-id="${milestoneId}"]`);
            if (container) container.remove();

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Delete error:', error);
            alert('Failed to delete milestone.');
        }
    }

    linkMilestone(sessionId, milestoneId) {
        // TODO: Implement milestone linking functionality
        console.log('[SYNERGY INLINE EDIT] Link milestone:', milestoneId);
    }

    async toggleMilestoneComplete(sessionId, milestoneId, completed) {
        try {
            await fetch(`${this.API_BASE_URL}/api/synergy/milestone/${milestoneId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ completed })
            });
        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Toggle error:', error);
        }
    }

    // ==================== SESSION-LEVEL EDITING ====================

    editSessionTitle(sessionId) {
        const titleEl = document.querySelector('.synergy-session-title-editable');
        if (!titleEl) return;

        this.originalContent['session_title'] = titleEl.textContent;
        titleEl.setAttribute('contenteditable', 'true');
        titleEl.focus();

        // Select all text
        const range = document.createRange();
        range.selectNodeContents(titleEl);
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
    }

    async saveSessionTitle(sessionId) {
        const titleEl = document.querySelector('.synergy-session-title-editable');
        if (!titleEl) return;

        const newTitle = titleEl.textContent.trim();
        if (!newTitle) {
            alert('Title cannot be empty');
            return;
        }

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/${sessionId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: newTitle })
            });

            if (!response.ok) throw new Error('Save failed');

            titleEl.setAttribute('contenteditable', 'false');
            delete this.originalContent['session_title'];

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Save title error:', error);
            alert('Failed to save title');
        }
    }

    editDescription(sessionId) {
        const section = document.querySelector('[data-section="description"]');
        if (!section) return;

        const container = section.querySelector('.synergy-flat-description-container');
        const descEl = section.querySelector('.synergy-flat-description');

        if (!descEl) return;

        this.originalContent['description'] = descEl.textContent;
        container.setAttribute('data-editing', 'true');
        descEl.setAttribute('contenteditable', 'true');
        descEl.focus();

        // Show save/cancel buttons
        const actions = section.querySelector('.synergy-flat-edit-actions');
        if (actions) actions.style.display = 'flex';
    }

    async saveDescription(sessionId) {
        const section = document.querySelector('[data-section="description"]');
        if (!section) return;

        const container = section.querySelector('.synergy-flat-description-container');
        const descEl = section.querySelector('.synergy-flat-description');
        const newDesc = descEl.textContent.trim();

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/${sessionId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ description: newDesc })
            });

            if (!response.ok) throw new Error('Save failed');

            container.setAttribute('data-editing', 'false');
            descEl.setAttribute('contenteditable', 'false');
            delete this.originalContent['description'];

            // Hide save/cancel buttons
            const actions = section.querySelector('.synergy-flat-edit-actions');
            if (actions) actions.style.display = 'none';

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Save description error:', error);
            alert('Failed to save description');
        }
    }

    cancelDescription() {
        const section = document.querySelector('[data-section="description"]');
        if (!section) return;

        const container = section.querySelector('.synergy-flat-description-container');
        const descEl = section.querySelector('.synergy-flat-description');

        if (this.originalContent['description']) {
            descEl.textContent = this.originalContent['description'];
        }

        container.setAttribute('data-editing', 'false');
        descEl.setAttribute('contenteditable', 'false');
        delete this.originalContent['description'];

        // Hide save/cancel buttons
        const actions = section.querySelector('.synergy-flat-edit-actions');
        if (actions) actions.style.display = 'none';
    }

    // Add/Edit Tags
    async addTag(sessionId) {
        const tagName = prompt('Enter tag name:');
        if (!tagName) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/${sessionId}/tags`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tag: tagName.trim() })
            });

            if (!response.ok) throw new Error('Add tag failed');

            // Reload card to show new tag
            await this.reloadCard(sessionId);

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Add tag error:', error);
            alert('Failed to add tag');
        }
    }

    async removeTag(sessionId, tagName) {
        if (!confirm(`Remove tag "${tagName}"?`)) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/${sessionId}/tags/${encodeURIComponent(tagName)}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Remove tag failed');

            // Reload card to update UI
            await this.reloadCard(sessionId);

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Remove tag error:', error);
            alert('Failed to remove tag');
        }
    }

    // Add/Edit Links
    async addLink(sessionId) {
        const linkData = await this.showAddLinkModal();
        if (!linkData) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/${sessionId}/link-document`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: linkData.url, title: linkData.title || linkData.url })
            });

            if (!response.ok) throw new Error('Add link failed');

            // Reload card
            await this.reloadCard(sessionId);

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Add link error:', error);
            alert('Failed to add link');
        }
    }

    // Show add link modal
    showAddLinkModal() {
        return new Promise((resolve) => {
            const modalHTML = `
                <div id="synergy-add-link-modal" class="synergy-doc-choice-overlay">
                    <div class="synergy-doc-choice-modal">
                        <div class="synergy-doc-choice-header">
                            <h3>Add Link</h3>
                            <button onclick="document.getElementById('synergy-add-link-modal').dispatchEvent(new CustomEvent('cancel')); return false;">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        <div style="padding: 24px;">
                            <div style="margin-bottom: 16px;">
                                <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">URL *</label>
                                <input type="url" id="synergy-link-url" placeholder="https://example.com" 
                                    style="width: 100%; padding: 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 6px; color: var(--text-primary); font-size: 14px;">
                            </div>
                            <div style="margin-bottom: 24px;">
                                <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">Title (optional)</label>
                                <input type="text" id="synergy-link-title" placeholder="Link title" 
                                    style="width: 100%; padding: 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 6px; color: var(--text-primary); font-size: 14px;">
                            </div>
                            <div style="display: flex; gap: 12px; justify-content: flex-end;">
                                <button onclick="document.getElementById('synergy-add-link-modal').dispatchEvent(new CustomEvent('cancel'))" 
                                    style="padding: 10px 20px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 6px; cursor: pointer; color: var(--text-primary); font-size: 14px;">
                                    Cancel
                                </button>
                                <button onclick="document.getElementById('synergy-add-link-modal').dispatchEvent(new CustomEvent('submit'))" 
                                    style="padding: 10px 20px; background: var(--accent-primary); border: none; border-radius: 6px; cursor: pointer; color: white; font-weight: 600; font-size: 14px;">
                                    Add Link
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', modalHTML);
            const modal = document.getElementById('synergy-add-link-modal');
            const urlInput = document.getElementById('synergy-link-url');

            // Focus URL input
            setTimeout(() => urlInput.focus(), 100);

            // Handle enter key
            urlInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    modal.dispatchEvent(new CustomEvent('submit'));
                }
            });

            modal.addEventListener('submit', () => {
                const url = urlInput.value.trim();
                const title = document.getElementById('synergy-link-title').value.trim();

                if (!url) {
                    alert('URL is required');
                    urlInput.focus();
                    return;
                }

                modal.remove();
                resolve({ url, title });
            });

            modal.addEventListener('cancel', () => {
                modal.remove();
                resolve(null);
            });
        });
    }

    // Add Document - with picker and create options
    async addDocument(sessionId) {
        console.log('[SYNERGY INLINE EDIT] 🚀 addDocument method called for session:', sessionId);

        // Show choice modal: Create New or Link Existing
        console.log('[SYNERGY INLINE EDIT] Showing document choice modal...');
        const choice = await this.showDocumentChoice();
        console.log('[SYNERGY INLINE EDIT] User choice:', choice);

        if (choice === 'create') {
            // Use the existing working UI from internalDocsManager
            if (window.internalDocsManager && typeof window.internalDocsManager.createInternalDoc === 'function') {
                console.log('[SYNERGY INLINE EDIT] Opening document creation UI...');
                await window.internalDocsManager.createInternalDoc(sessionId);
            } else {
                console.error('[SYNERGY INLINE EDIT] ❌ internalDocsManager not available');
                alert('Document creation UI not loaded. Please refresh the page.');
            }
        } else if (choice === 'existing') {
            // Show document picker
            try {
                const documents = await this.fetchInternalDocs(sessionId);

                if (documents.length === 0) {
                    alert('No documents available to link');
                    return;
                }

                const selectedDoc = await this.showDocumentPicker(documents);

                if (selectedDoc) {
                    console.log('[SYNERGY INLINE EDIT] Linking doc:', selectedDoc.doc_id);
                    await this.linkDocument(sessionId, selectedDoc.doc_id, selectedDoc);
                }
            } catch (error) {
                console.error('[SYNERGY INLINE EDIT] Error in document picker:', error);
                alert('Failed to load documents: ' + error.message);
            }
        }
    }

    // Fetch internal documents for picker
    async fetchInternalDocs(sessionId) {
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/internal-docs/list`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error('Failed to fetch documents');

            const data = await response.json();
            return data.documents || [];

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Fetch documents error:', error);
            throw error;
        }
    }

    // Show document picker modal
    showDocumentPicker(documents) {
        return new Promise((resolve) => {
            const modalHTML = `
                <div id="synergy-doc-picker-modal" class="synergy-doc-choice-overlay">
                    <div class="synergy-doc-choice-modal" style="max-width: 600px; max-height: 80vh; overflow: hidden; display: flex; flex-direction: column;">
                        <div class="synergy-doc-choice-header">
                            <h3>Link Document</h3>
                            <button onclick="document.getElementById('synergy-doc-picker-modal').dispatchEvent(new CustomEvent('cancel')); return false;">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        <div style="padding: 16px; flex: 1; overflow-y: auto;">
                            <input type="text" id="doc-search-input" placeholder="Search documents..." 
                                style="width: 100%; padding: 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 6px; color: var(--text-primary); font-size: 14px; margin-bottom: 16px;">
                            <div id="doc-list" style="display: flex; flex-direction: column; gap: 8px;">
                                ${documents.map(doc => `
                                    <div class="doc-picker-item" data-doc-id="${doc.doc_id}" 
                                        style="padding: 12px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 6px; cursor: pointer; transition: all 0.2s;">
                                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                                            <i class="fas fa-${doc.doc_type === 'spreadsheet' ? 'table' : 'file-alt'}" style="color: var(--accent-primary);"></i>
                                            <div style="font-weight: 600; color: var(--text-primary);">
                                                ${doc.title || 'Untitled Document'}
                                            </div>
                                        </div>
                                        ${doc.description ? `<div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">${doc.description}</div>` : ''}
                                        <div style="font-size: 11px; color: var(--text-muted);">
                                            Created: ${new Date(doc.created_at).toLocaleDateString()}
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', modalHTML);
            const modal = document.getElementById('synergy-doc-picker-modal');
            const searchInput = document.getElementById('doc-search-input');
            const docList = document.getElementById('doc-list');

            // Focus search input
            setTimeout(() => searchInput.focus(), 100);

            // Search functionality
            searchInput.addEventListener('input', (e) => {
                const query = e.target.value.toLowerCase();
                const items = docList.querySelectorAll('.doc-picker-item');

                items.forEach(item => {
                    const text = item.textContent.toLowerCase();
                    item.style.display = text.includes(query) ? 'block' : 'none';
                });
            });

            // Doc item click handlers
            docList.querySelectorAll('.doc-picker-item').forEach(item => {
                item.addEventListener('mouseenter', () => {
                    item.style.borderColor = 'var(--accent-primary)';
                    item.style.background = 'rgba(79, 108, 255, 0.1)';
                });

                item.addEventListener('mouseleave', () => {
                    item.style.borderColor = 'var(--border-default)';
                    item.style.background = 'var(--bg-tertiary)';
                });

                item.addEventListener('click', () => {
                    const docId = item.dataset.docId;
                    const doc = documents.find(d => String(d.doc_id) === String(docId));
                    modal.remove();
                    resolve(doc);
                });
            });

            modal.addEventListener('cancel', () => {
                modal.remove();
                resolve(null);
            });

            // ESC key to cancel
            const escHandler = (e) => {
                if (e.key === 'Escape') {
                    modal.dispatchEvent(new CustomEvent('cancel'));
                    document.removeEventListener('keydown', escHandler);
                }
            };
            document.addEventListener('keydown', escHandler);
        });
    }

    // Show document choice modal (Create New vs Link Existing)
    showDocumentChoice() {
        return new Promise((resolve) => {
            const modalHTML = `
                <div id="synergy-doc-choice-modal" class="synergy-doc-choice-overlay">
                    <div class="synergy-doc-choice-modal">
                        <div class="synergy-doc-choice-header">
                            <h3>Add Document</h3>
                            <button onclick="document.getElementById('synergy-doc-choice-modal').remove(); return false;">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        <div class="synergy-doc-choice-buttons">
                            <button class="synergy-doc-choice-btn create" onclick="document.getElementById('synergy-doc-choice-modal').dispatchEvent(new CustomEvent('choice', {detail: 'create'}))">
                                <i class="fas fa-plus-circle"></i>
                                <div>
                                    <strong>Create New</strong>
                                    <small>Start a fresh document or spreadsheet</small>
                                </div>
                            </button>
                            <button class="synergy-doc-choice-btn existing" onclick="document.getElementById('synergy-doc-choice-modal').dispatchEvent(new CustomEvent('choice', {detail: 'existing'}))">
                                <i class="fas fa-link"></i>
                                <div>
                                    <strong>Link Existing</strong>
                                    <small>Select from your internal documents</small>
                                </div>
                            </button>
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', modalHTML);
            const modal = document.getElementById('synergy-doc-choice-modal');

            modal.addEventListener('choice', (e) => {
                modal.remove();
                resolve(e.detail);
            });
        });
    }

    // Link an existing document to session
    async linkDocument(sessionId, docId, docData) {
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/${sessionId}/link-document`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    doc_id: docId,
                    title: docData.title,
                    doc_type: docData.doc_type
                })
            });

            if (!response.ok) throw new Error('Link document failed');

            console.log('[SYNERGY INLINE EDIT] Document linked:', docId);

            // Reload card to show new document
            await this.reloadCard(sessionId);

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Link document error:', error);
            alert('Failed to link document');
        }
    }

    async removeLink(sessionId, linkIndex) {
        if (!confirm('Remove this link?')) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/${sessionId}/links/${linkIndex}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Remove link failed');

            // Reload card
            await this.reloadCard(sessionId);

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Remove link error:', error);
            alert('Failed to remove link');
        }
    }

    // Add Thread - Link existing thread to Synergy session
    async addThread(sessionId) {
        console.log('[SYNERGY INLINE EDIT] 🚀 addThread method called for session:', sessionId);

        try {
            // Fetch user's threads
            const userId = (window.UserAuth && window.UserAuth.user && (window.UserAuth.user.id || window.UserAuth.user.user_id)) || 1;
            const response = await fetch(`${this.API_BASE_URL}/api/threads/list?user_id=${userId}`);

            if (!response.ok) throw new Error('Failed to fetch threads');

            const data = await response.json();
            const threads = data.threads || [];

            if (threads.length === 0) {
                alert('No threads available to link');
                return;
            }

            // Show thread picker
            const selectedThread = await this.showThreadPicker(threads);

            if (!selectedThread) {
                console.log('[SYNERGY INLINE EDIT] Thread picker cancelled');
                return;
            }

            console.log('[SYNERGY INLINE EDIT] Linking thread:', selectedThread);

            // Link thread to session
            const linkResponse = await fetch(`${this.API_BASE_URL}/api/synergy/${sessionId}/link-thread`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    thread_id: selectedThread.thread_id,
                    user_id: userId
                })
            });

            if (!linkResponse.ok) throw new Error('Failed to link thread');

            const result = await linkResponse.json();

            if (result.success) {
                console.log('[SYNERGY INLINE EDIT] ✅ Thread linked successfully');
                if (window.showNotification) {
                    window.showNotification('Thread linked to Synergy session', 'success');
                }

                // Reload card to show new thread
                await this.reloadCard(sessionId);
            } else {
                throw new Error(result.error || 'Unknown error');
            }

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Add thread error:', error);
            alert('Failed to link thread: ' + error.message);
        }
    }

    // Show thread picker modal
    showThreadPicker(threads) {
        return new Promise((resolve) => {
            const modalHTML = `
                <div id="synergy-thread-picker-modal" class="synergy-doc-choice-overlay">
                    <div class="synergy-doc-choice-modal" style="max-width: 600px; max-height: 80vh; overflow: hidden; display: flex; flex-direction: column;">
                        <div class="synergy-doc-choice-header">
                            <h3>Link Thread</h3>
                            <button onclick="document.getElementById('synergy-thread-picker-modal').dispatchEvent(new CustomEvent('cancel')); return false;">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        <div style="padding: 16px; flex: 1; overflow-y: auto;">
                            <input type="text" id="thread-search-input" placeholder="Search threads..." 
                                style="width: 100%; padding: 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 6px; color: var(--text-primary); font-size: 14px; margin-bottom: 16px;">
                            <div id="thread-list" style="display: flex; flex-direction: column; gap: 8px;">
                                ${threads.map(thread => `
                                    <div class="thread-picker-item" data-thread-id="${thread.thread_id}" 
                                        style="padding: 12px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 6px; cursor: pointer; transition: all 0.2s;">
                                        <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 4px;">
                                            ${thread.thread_name || 'Untitled Thread'}
                                        </div>
                                        <div style="font-size: 12px; color: var(--text-secondary);">
                                            Created: ${new Date(thread.created_at).toLocaleDateString()}
                                            ${thread.message_count ? ` • ${thread.message_count} messages` : ''}
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', modalHTML);
            const modal = document.getElementById('synergy-thread-picker-modal');
            const searchInput = document.getElementById('thread-search-input');
            const threadList = document.getElementById('thread-list');

            // Focus search input
            setTimeout(() => searchInput.focus(), 100);

            // Search functionality
            searchInput.addEventListener('input', (e) => {
                const query = e.target.value.toLowerCase();
                const items = threadList.querySelectorAll('.thread-picker-item');

                items.forEach(item => {
                    const text = item.textContent.toLowerCase();
                    item.style.display = text.includes(query) ? 'block' : 'none';
                });
            });

            // Thread item click handlers
            threadList.querySelectorAll('.thread-picker-item').forEach(item => {
                item.addEventListener('mouseenter', () => {
                    item.style.borderColor = 'var(--accent-primary)';
                    item.style.background = 'rgba(79, 108, 255, 0.1)';
                });

                item.addEventListener('mouseleave', () => {
                    item.style.borderColor = 'var(--border-default)';
                    item.style.background = 'var(--bg-tertiary)';
                });

                item.addEventListener('click', () => {
                    const threadId = item.dataset.threadId;
                    const thread = threads.find(t => String(t.thread_id) === String(threadId));
                    modal.remove();
                    resolve(thread);
                });
            });

            modal.addEventListener('cancel', () => {
                modal.remove();
                resolve(null);
            });

            // ESC key to cancel
            const escHandler = (e) => {
                if (e.key === 'Escape') {
                    modal.dispatchEvent(new CustomEvent('cancel'));
                    document.removeEventListener('keydown', escHandler);
                }
            };
            document.addEventListener('keydown', escHandler);
        });
    }

    // Add Milestone
    async addMilestone(sessionId) {
        const milestoneName = prompt('Enter milestone name:');
        if (!milestoneName) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/${sessionId}/milestones`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    milestone_name: milestoneName.trim(),
                    description: '',
                    priority: 'medium'
                })
            });

            if (!response.ok) throw new Error('Add milestone failed');

            // Reload card
            await this.reloadCard(sessionId);

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Add milestone error:', error);
            alert('Failed to add milestone');
        }
    }

    // Add Task to Milestone
    async addTask(sessionId, milestoneId) {
        const taskName = prompt('Enter task name:');
        if (!taskName) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/milestone/${milestoneId}/tasks`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    task: taskName.trim(),
                    priority: 'medium'
                })
            });

            if (!response.ok) throw new Error('Add task failed');

            // Reload card
            await this.reloadCard(sessionId);

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Add task error:', error);
            alert('Failed to add task');
        }
    }

    // Add Subtask to Task
    async addSubtask(sessionId, taskId) {
        const subtaskName = prompt('Enter subtask name:');
        if (!subtaskName) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/task/${taskId}/subtasks`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    task: subtaskName.trim(),
                    priority: 'medium'
                })
            });

            if (!response.ok) throw new Error('Add subtask failed');

            // Reload card
            await this.reloadCard(sessionId);

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Add subtask error:', error);
            alert('Failed to add subtask');
        }
    }

    // Reload card helper
    async reloadCard(sessionId) {
        const contextRoot = this.getContextRoot();
        const cardElement = contextRoot.querySelector(`[data-session-id="${sessionId}"]`);
        if (!cardElement) return;

        // Use renderer to reload
        if (window.SynergySidebarRenderer) {
            await window.SynergySidebarRenderer.loadAndRenderFullCard(sessionId, cardElement);
        }
    }

    // ==================== TASK EDITING ====================

    editTask(sessionId, taskId) {
        const contextRoot = this.getContextRoot();
        const container = contextRoot.querySelector(`[data-task-id="${taskId}"]`);
        if (!container) {
            console.warn(`[SYNERGY INLINE EDIT] Task ${taskId} not found in current context`);
            return;
        }

        const titleEl = container.querySelector('.synergy-flat-task-title');
        this.originalContent[taskId] = {
            title: titleEl ? titleEl.textContent : ''
        };

        container.setAttribute('data-editing', 'true');
        if (titleEl) {
            titleEl.setAttribute('contenteditable', 'true');
            titleEl.focus();
        }
        this.toggleEditMode(container, true);
    }

    async saveTask(sessionId, taskId) {
        const contextRoot = this.getContextRoot();
        const container = contextRoot.querySelector(`[data-task-id="${taskId}"]`);
        if (!container) {
            console.warn(`[SYNERGY INLINE EDIT] Task ${taskId} not found for save`);
            return;
        }

        const titleEl = container.querySelector('.synergy-flat-task-title');
        const priorityEl = container.querySelector('.synergy-priority-select');

        const data = {
            task: titleEl ? titleEl.textContent.trim() : '',
            priority: priorityEl ? priorityEl.value : 'medium'
        };

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/task/${taskId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!response.ok) throw new Error('Save failed');

            container.setAttribute('data-editing', 'false');
            if (titleEl) titleEl.setAttribute('contenteditable', 'false');
            this.toggleEditMode(container, false);
            delete this.originalContent[taskId];

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Save error:', error);
            alert('Failed to save task.');
        }
    }

    async deleteTask(sessionId, taskId) {
        if (!confirm('Delete this task?')) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/task/${taskId}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Delete failed');

            const contextRoot = this.getContextRoot();
            const container = contextRoot.querySelector(`[data-task-id="${taskId}"]`);
            if (container) container.remove();

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Delete error:', error);
            alert('Failed to delete task.');
        }
    }

    linkTask(sessionId, taskId) {
        console.log('[SYNERGY INLINE EDIT] Link task:', taskId);
    }

    async toggleTaskComplete(sessionId, taskId, completed) {
        try {
            await fetch(`${this.API_BASE_URL}/api/synergy/task/${taskId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ completed })
            });
        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Toggle error:', error);
        }
    }

    // ==================== SUBTASK EDITING ====================

    editSubtask(sessionId, subtaskId) {
        const contextRoot = this.getContextRoot();
        const container = contextRoot.querySelector(`[data-subtask-id="${subtaskId}"]`);
        if (!container) {
            console.warn(`[SYNERGY INLINE EDIT] Subtask ${subtaskId} not found in current context`);
            return;
        }

        const titleEl = container.querySelector('.synergy-flat-subtask-title');
        this.originalContent[subtaskId] = {
            title: titleEl ? titleEl.textContent : ''
        };

        container.setAttribute('data-editing', 'true');
        if (titleEl) {
            titleEl.setAttribute('contenteditable', 'true');
            titleEl.focus();
        }
        this.toggleEditMode(container, true);
    }

    async saveSubtask(sessionId, subtaskId) {
        const contextRoot = this.getContextRoot();
        const container = contextRoot.querySelector(`[data-subtask-id="${subtaskId}"]`);
        if (!container) {
            console.warn(`[SYNERGY INLINE EDIT] Subtask ${subtaskId} not found for save`);
            return;
        }

        const titleEl = container.querySelector('.synergy-flat-subtask-title');
        const priorityEl = container.querySelector('.synergy-priority-select');

        const data = {
            subtask: titleEl ? titleEl.textContent.trim() : '',
            priority: priorityEl ? priorityEl.value : 'medium'
        };

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/subtask/${subtaskId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!response.ok) throw new Error('Save failed');

            container.setAttribute('data-editing', 'false');
            if (titleEl) titleEl.setAttribute('contenteditable', 'false');
            this.toggleEditMode(container, false);
            delete this.originalContent[subtaskId];

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Save error:', error);
            alert('Failed to save subtask.');
        }
    }

    async deleteSubtask(sessionId, subtaskId) {
        if (!confirm('Delete this subtask?')) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/synergy/subtask/${subtaskId}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Delete failed');

            const contextRoot = this.getContextRoot();
            const container = contextRoot.querySelector(`[data-subtask-id="${subtaskId}"]`);
            if (container) container.remove();

        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Delete error:', error);
            alert('Failed to delete subtask.');
        }
    }

    async toggleSubtaskComplete(sessionId, subtaskId, completed) {
        try {
            await fetch(`${this.API_BASE_URL}/api/synergy/subtask/${subtaskId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ completed })
            });
        } catch (error) {
            console.error('[SYNERGY INLINE EDIT] Toggle error:', error);
        }
    }

    // ==================== DOCUMENT EDITING ====================

    editDoc(sessionId, docId) {
        console.log('[SYNERGY INLINE EDIT] Edit document:', docId);
        // TODO: Implement document editing
    }

    deleteDoc(sessionId, docId) {
        console.log('[SYNERGY INLINE EDIT] Delete document:', docId);
        // TODO: Implement document deletion
    }

    openDoc(sessionId, docId) {
        console.log('[SYNERGY INLINE EDIT] Open document:', docId);
        // TODO: Implement document opening
    }

    // ==================== HELPER METHODS ====================

    toggleEditMode(container, isEditing) {
        // Toggle button visibility
        const editActions = container.querySelector('.synergy-flat-edit-actions');
        const headerRight = container.querySelector('.synergy-flat-header-right');

        if (isEditing) {
            if (editActions) editActions.style.display = 'flex';
            if (headerRight) {
                const editBtn = headerRight.querySelector('.synergy-edit-btn');
                const deleteBtn = headerRight.querySelector('.synergy-delete-btn');
                const priorityDisplay = headerRight.querySelector('.synergy-priority-display');
                const prioritySelect = headerRight.querySelector('.synergy-priority-select');

                if (editBtn) editBtn.style.display = 'none';
                if (deleteBtn) deleteBtn.style.display = 'none';

                // Show priority dropdown, hide badge
                if (priorityDisplay) priorityDisplay.style.display = 'none';
                if (prioritySelect) prioritySelect.style.display = 'inline-block';
            }
        } else {
            if (editActions) editActions.style.display = 'none';
            if (headerRight) {
                const editBtn = headerRight.querySelector('.synergy-edit-btn');
                const deleteBtn = headerRight.querySelector('.synergy-delete-btn');
                const priorityDisplay = headerRight.querySelector('.synergy-priority-display');
                const prioritySelect = headerRight.querySelector('.synergy-priority-select');

                if (editBtn) editBtn.style.display = 'inline-block';
                if (deleteBtn) deleteBtn.style.display = 'inline-block';

                // Hide priority dropdown, show badge
                if (priorityDisplay) priorityDisplay.style.display = 'inline-flex';
                if (prioritySelect) prioritySelect.style.display = 'none';
            }
        }
    }
}

// ==================== EVENT DELEGATION SETUP (RECOMMENDED PATTERN) ====================
// Use event delegation instead of inline onclick handlers for better performance and reliability
// This eliminates timing issues and reduces HTML bloat

// Create global instance
window.SynergyInlineEdit = new SynergyInlineEditClass();
console.log('[SYNERGY INLINE EDIT] ✅ Instance created with event delegation');

// Setup event delegation on document level
document.addEventListener('click', function (e) {
    const target = e.target;

    // CRITICAL FIX: Determine if click is in sidebar, dashboard, or popup modal
    // This prevents cross-container editing (sidebar → dashboard, popup → sidebar, etc.)
    const clickedInSidebar = target.closest('#synergy-sidebar');
    const clickedInDashboard = target.closest('#synergy-dashboard-container, .synergy-dashboard-wrapper');
    const clickedInPopup = target.closest('.synergy-popup-container');

    // If not in any synergy container, ignore
    if (!clickedInSidebar && !clickedInDashboard && !clickedInPopup) return;

    // Edit button clicked
    if (target.classList.contains('synergy-edit-btn')) {
        const container = target.closest('[data-milestone-id], [data-task-id], [data-subtask-id]');
        if (!container) return;

        // Verify container is in the same context (sidebar, dashboard, or popup)
        const containerInSidebar = container.closest('#synergy-sidebar');
        const containerInDashboard = container.closest('#synergy-dashboard-container, .synergy-dashboard-wrapper');
        const containerInPopup = container.closest('.synergy-popup-container');

        // Only allow editing if click and container are in the SAME context
        if (clickedInSidebar && !containerInSidebar) {
            console.warn('[SYNERGY EDIT] Ignoring sidebar click - target not in sidebar');
            return;
        }
        if (clickedInDashboard && !containerInDashboard) {
            console.warn('[SYNERGY EDIT] Ignoring dashboard click - target not in dashboard');
            return;
        }
        if (clickedInPopup && !containerInPopup) {
            console.warn('[SYNERGY EDIT] Ignoring popup click - target not in popup');
            return;
        }

        const milestoneId = container.getAttribute('data-milestone-id');
        const taskId = container.getAttribute('data-task-id');
        const subtaskId = container.getAttribute('data-subtask-id');
        const sessionId = container.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';

        if (milestoneId) window.SynergyInlineEdit.editMilestone(sessionId, milestoneId);
        else if (taskId) window.SynergyInlineEdit.editTask(sessionId, taskId);
        else if (subtaskId) window.SynergyInlineEdit.editSubtask(sessionId, subtaskId);
        return;
    }

    // Save button clicked
    if (target.classList.contains('synergy-save-btn')) {
        const container = target.closest('[data-milestone-id], [data-task-id], [data-subtask-id]');
        if (!container) return;

        // Verify container is in the same context
        const containerInSidebar = container.closest('#synergy-sidebar');
        const containerInDashboard = container.closest('#synergy-dashboard-container, .synergy-dashboard-wrapper');
        const containerInPopup = container.closest('.synergy-popup-container');

        if (clickedInSidebar && !containerInSidebar) {
            console.warn('[SYNERGY SAVE] Ignoring sidebar click - target not in sidebar');
            return;
        }
        if (clickedInDashboard && !containerInDashboard) {
            console.warn('[SYNERGY SAVE] Ignoring dashboard click - target not in dashboard');
            return;
        }
        if (clickedInPopup && !containerInPopup) {
            console.warn('[SYNERGY SAVE] Ignoring popup click - target not in popup');
            return;
        }

        const milestoneId = container.getAttribute('data-milestone-id');
        const taskId = container.getAttribute('data-task-id');
        const subtaskId = container.getAttribute('data-subtask-id');
        const sessionId = container.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';

        if (milestoneId) window.SynergyInlineEdit.saveMilestone(sessionId, milestoneId);
        else if (taskId) window.SynergyInlineEdit.saveTask(sessionId, taskId);
        else if (subtaskId) window.SynergyInlineEdit.saveSubtask(sessionId, subtaskId);
        return;
    }

    // Cancel button clicked
    if (target.classList.contains('synergy-cancel-btn')) {
        const container = target.closest('[data-milestone-id], [data-task-id], [data-subtask-id]');
        if (!container) return;

        // Verify container is in the same context
        const containerInSidebar = container.closest('#synergy-sidebar');
        const containerInDashboard = container.closest('#synergy-dashboard-container, .synergy-dashboard-wrapper');
        const containerInPopup = container.closest('.synergy-popup-container');

        if (clickedInSidebar && !containerInSidebar) {
            console.warn('[SYNERGY CANCEL] Ignoring sidebar click - target not in sidebar');
            return;
        }
        if (clickedInDashboard && !containerInDashboard) {
            console.warn('[SYNERGY CANCEL] Ignoring dashboard click - target not in dashboard');
            return;
        }
        if (clickedInPopup && !containerInPopup) {
            console.warn('[SYNERGY CANCEL] Ignoring popup click - target not in popup');
            return;
        }

        const milestoneId = container.getAttribute('data-milestone-id');
        const taskId = container.getAttribute('data-task-id');
        const subtaskId = container.getAttribute('data-subtask-id');
        const sessionId = container.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';

        const itemId = milestoneId || taskId || subtaskId;
        window.SynergyInlineEdit.cancelEdit(sessionId, itemId);
        return;
    }

    // Delete button clicked
    if (target.classList.contains('synergy-delete-btn')) {
        const container = target.closest('[data-milestone-id], [data-task-id], [data-subtask-id]');
        if (!container) return;

        // Verify container is in the same context
        const containerInSidebar = container.closest('#synergy-sidebar');
        const containerInDashboard = container.closest('#synergy-dashboard-container, .synergy-dashboard-wrapper');
        const containerInPopup = container.closest('.synergy-popup-container');

        if (clickedInSidebar && !containerInSidebar) {
            console.warn('[SYNERGY DELETE] Ignoring sidebar click - target not in sidebar');
            return;
        }
        if (clickedInDashboard && !containerInDashboard) {
            console.warn('[SYNERGY DELETE] Ignoring dashboard click - target not in dashboard');
            return;
        }
        if (clickedInPopup && !containerInPopup) {
            console.warn('[SYNERGY DELETE] Ignoring popup click - target not in popup');
            return;
        }

        const milestoneId = container.getAttribute('data-milestone-id');
        const taskId = container.getAttribute('data-task-id');
        const subtaskId = container.getAttribute('data-subtask-id');
        const sessionId = container.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';

        if (milestoneId) window.SynergyInlineEdit.deleteMilestone(sessionId, milestoneId);
        else if (taskId) window.SynergyInlineEdit.deleteTask(sessionId, taskId);
        else if (subtaskId) window.SynergyInlineEdit.deleteSubtask(sessionId, subtaskId);
        return;
    }

    // Link button clicked
    if (target.classList.contains('synergy-link-btn')) {
        const container = target.closest('[data-milestone-id], [data-task-id]');
        if (!container) return;

        // Verify container is in the same context
        const containerInSidebar = container.closest('#synergy-sidebar');
        const containerInDashboard = container.closest('#synergy-dashboard-container, .synergy-dashboard-wrapper');
        const containerInPopup = container.closest('.synergy-popup-container');

        if (clickedInSidebar && !containerInSidebar) {
            console.warn('[SYNERGY LINK] Ignoring sidebar click - target not in sidebar');
            return;
        }
        if (clickedInDashboard && !containerInDashboard) {
            console.warn('[SYNERGY LINK] Ignoring dashboard click - target not in dashboard');
            return;
        }
        if (clickedInPopup && !containerInPopup) {
            console.warn('[SYNERGY LINK] Ignoring popup click - target not in popup');
            return;
        }

        const milestoneId = container.getAttribute('data-milestone-id');
        const taskId = container.getAttribute('data-task-id');
        const sessionId = container.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';

        if (milestoneId) window.SynergyInlineEdit.linkMilestone(sessionId, milestoneId);
        else if (taskId) window.SynergyInlineEdit.linkTask(sessionId, taskId);
        return;
    }

    // SESSION-LEVEL EDITING BUTTONS (these are safe - only appear once per container)

    // Edit description button
    if (target.classList.contains('synergy-edit-description-btn')) {
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        window.SynergyInlineEdit.editDescription(sessionId);
        return;
    }

    // Save description button
    if (target.classList.contains('synergy-save-description-btn')) {
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        window.SynergyInlineEdit.saveDescription(sessionId);
        return;
    }

    // Cancel description button
    if (target.classList.contains('synergy-cancel-description-btn')) {
        window.SynergyInlineEdit.cancelDescription();
        return;
    }

    // Add milestone button
    if (target.classList.contains('synergy-add-milestone-btn')) {
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        window.SynergyInlineEdit.addMilestone(sessionId);
        return;
    }

    // Add document button
    if (target.classList.contains('synergy-add-document-btn')) {
        console.log('[SYNERGY INLINE EDIT] 📄 Add document button clicked');
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        console.log('[SYNERGY INLINE EDIT] Session ID:', sessionId);
        if (window.SynergyInlineEdit) {
            console.log('[SYNERGY INLINE EDIT] Calling addDocument method...');
            window.SynergyInlineEdit.addDocument(sessionId);
        } else {
            console.error('[SYNERGY INLINE EDIT] ❌ SynergyInlineEdit not found on window');
        }
        return;
    }

    // Open thread history button (for linking threads)
    if (target.classList.contains('synergy-open-thread-history-btn')) {
        console.log('[SYNERGY INLINE EDIT] 🔗 Link thread button clicked');
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        console.log('[SYNERGY INLINE EDIT] Session ID:', sessionId);
        if (window.SynergyInlineEdit) {
            console.log('[SYNERGY INLINE EDIT] Calling addThread method...');
            window.SynergyInlineEdit.addThread(sessionId);
        } else {
            console.error('[SYNERGY INLINE EDIT] ❌ SynergyInlineEdit not found on window');
        }
        return;
    }

    // Add task button
    if (target.classList.contains('synergy-add-task-btn')) {
        // Verify button is in a synergy container
        if (!clickedInSidebar && !clickedInDashboard && !clickedInPopup) return;

        const milestoneId = target.getAttribute('data-milestone-id') || target.closest('[data-milestone-id]')?.getAttribute('data-milestone-id');
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        if (milestoneId) {
            window.SynergyInlineEdit.addTask(sessionId, milestoneId);
        }
        return;
    }

    // Add subtask button
    if (target.classList.contains('synergy-add-subtask-btn')) {
        // Verify button is in a synergy container
        if (!clickedInSidebar && !clickedInDashboard && !clickedInPopup) return;

        const taskId = target.getAttribute('data-task-id') || target.closest('[data-task-id]')?.getAttribute('data-task-id');
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        if (taskId) {
            window.SynergyInlineEdit.addSubtask(sessionId, taskId);
        }
        return;
    }

    // Add tag button
    if (target.classList.contains('synergy-add-tag-btn')) {
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        window.SynergyInlineEdit.addTag(sessionId);
        return;
    }

    // Remove tag button
    if (target.classList.contains('synergy-remove-tag-btn')) {
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        const tagName = target.getAttribute('data-tag-name');
        if (tagName) {
            window.SynergyInlineEdit.removeTag(sessionId, tagName);
        }
        return;
    }

    // Add link button
    if (target.classList.contains('synergy-add-link-btn')) {
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        window.SynergyInlineEdit.addLink(sessionId);
        return;
    }

    // Remove link button
    if (target.classList.contains('synergy-remove-link-btn')) {
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        const linkIndex = target.getAttribute('data-link-index');
        if (linkIndex !== null) {
            window.SynergyInlineEdit.removeLink(sessionId, parseInt(linkIndex));
        }
        return;
    }

    // Edit session title (double-click on title)
    if (target.classList.contains('synergy-session-title-editable')) {
        const sessionId = target.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        window.SynergyInlineEdit.editSessionTitle(sessionId);
        return;
    }
});

// Setup checkbox change delegation
document.addEventListener('change', function (e) {
    const target = e.target;

    // Checkbox toggle for milestone/task/subtask completion
    if (target.classList.contains('synergy-flat-checkbox')) {
        // CRITICAL FIX: Verify checkbox is in correct container (sidebar, dashboard, or popup)
        const clickedInSidebar = target.closest('#synergy-sidebar');
        const clickedInDashboard = target.closest('#synergy-dashboard-container');
        const clickedInPopup = target.closest('.synergy-popup-container');

        if (!clickedInSidebar && !clickedInDashboard && !clickedInPopup) return;

        const container = target.closest('[data-milestone-id], [data-task-id], [data-subtask-id]');
        if (!container) return;

        // Verify container is in the same context
        const containerInSidebar = container.closest('#synergy-sidebar');
        const containerInDashboard = container.closest('#synergy-dashboard-container, .synergy-dashboard-wrapper');
        const containerInPopup = container.closest('.synergy-popup-container');

        if (clickedInSidebar && !containerInSidebar) {
            console.warn('[SYNERGY CHECKBOX] Ignoring sidebar change - target not in sidebar');
            return;
        }
        if (clickedInDashboard && !containerInDashboard) {
            console.warn('[SYNERGY CHECKBOX] Ignoring dashboard change - target not in dashboard');
            return;
        }
        if (clickedInPopup && !containerInPopup) {
            console.warn('[SYNERGY CHECKBOX] Ignoring popup change - target not in popup');
            return;
        }

        const milestoneId = container.getAttribute('data-milestone-id');
        const taskId = container.getAttribute('data-task-id');
        const subtaskId = container.getAttribute('data-subtask-id');
        const sessionId = container.closest('.synergy-flat-container')?.getAttribute('data-session-id') || '';
        const checked = target.checked;

        if (milestoneId) window.SynergyInlineEdit.toggleMilestoneComplete(sessionId, milestoneId, checked);
        else if (taskId) window.SynergyInlineEdit.toggleTaskComplete(sessionId, taskId, checked);
        else if (subtaskId) window.SynergyInlineEdit.toggleSubtaskComplete(sessionId, subtaskId, checked);
    }
});

console.log('[SYNERGY INLINE EDIT] ✅ Event delegation initialized (no inline handlers needed)');
