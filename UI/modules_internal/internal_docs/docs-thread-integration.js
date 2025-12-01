/**
 * FILE: UI/modules_internal/internal_docs/docs-thread-integration.js
 * PURPOSE: Internal docs/sheets badge rendering and integration for thread cards
 * 
 * DEPENDENCIES:
 * - thread-card-registry.js (ThreadCardRegistry global)
 * - thread-manager-ui.js (ThreadManager global)
 * 
 * EXPORTS:
 * - window.InternalDocsThreadIntegration.renderThreadBadge() - Render linked doc badge
 * - window.InternalDocsThreadIntegration.openDoc() - Open internal document
 * - window.InternalDocsThreadIntegration.unlinkDoc() - Unlink document from thread
 * - window.InternalDocsThreadIntegration.openLinkModal() - Show modal to link document
 * 
 * USED BY:
 * - ThreadCardRegistry (badge rendering system)
 * - Thread info cards (UI links row)
 * 
 * NOTES:
 * - Registers with ThreadCardRegistry on load
 * - Yellow badge color (#eab308) for internal docs
 * - Supports drag-and-drop document IDs onto threads
 * - Works with both internal docs and sheets
 * 
 * LAST MODIFIED: 2025-11-29 - Created module for internal docs badge integration
 */

window.InternalDocsThreadIntegration = {
    /**
     * Render linked internal document badge for thread card
     * 
     * @param {Object} thread - Thread object with internal_doc_id field
     * @param {Object} config - Badge configuration {icon, color, label}
     * @returns {string} HTML string for internal doc badge
     */
    renderThreadBadge(thread, config) {
        if (!thread.internal_doc_id) return '';

        const safeEscape = window.safeEscape || ((str) => String(str).replace(/[&<>"']/g, ''));
        const docTitle = thread.internal_doc_title || thread.internal_doc_id;
        const docType = thread.internal_doc_type || 'doc'; // 'doc' or 'sheet'
        const icon = docType === 'sheet' ? 'fa-table' : config.icon;

        return `
            <div class="thread-item-internal-doc thread-item-internal-doc-linked" 
                 data-doc-id="${safeEscape(thread.internal_doc_id)}"
                 data-doc-type="${docType}"
                 style="display: flex; align-items: center; gap: 8px;">
                <button class="internal-doc-badge" 
                        style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; border: none; padding: 8px 14px; border-radius: 8px; display: flex; align-items: center; gap: 10px; font-size: 13px; font-weight: 500; cursor: pointer; flex: 1; box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3); transition: all 0.2s ease;"
                        onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 12px rgba(245, 158, 11, 0.4)'"
                        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(245, 158, 11, 0.3)'"
                        onclick="event.stopPropagation(); window.InternalDocsThreadIntegration.openDoc('${safeEscape(thread.internal_doc_id)}', '${docType}')"
                        title="${safeEscape(docTitle)}">
                    <i class="fas ${icon}" style="font-size: 14px; opacity: 0.95;"></i>
                    <span class="internal-doc-badge-title" style="letter-spacing: 0.01em;">${safeEscape(docTitle)}</span>
                </button>
                <button class="doc-info" 
                        style="background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); padding: 6px 10px; border-radius: 6px; cursor: pointer; transition: all 0.2s ease;" 
                        onmouseover="this.style.background='rgba(245, 158, 11, 0.25)'; this.style.borderColor='rgba(245, 158, 11, 0.5)'"
                        onmouseout="this.style.background='rgba(245, 158, 11, 0.15)'; this.style.borderColor='rgba(245, 158, 11, 0.3)'"
                        title="View document details" 
                        onclick="event.stopPropagation(); window.InternalDocsThreadIntegration.showDocInfo('${safeEscape(thread.internal_doc_id)}')">
                    <i class="fas fa-info-circle"></i>
                </button>
                <button class="doc-unlink" 
                        style="background: rgba(220, 38, 38, 0.1); color: #dc2626; border: 1px solid rgba(220, 38, 38, 0.3); padding: 6px 10px; border-radius: 6px; cursor: pointer; transition: all 0.2s ease;" 
                        onmouseover="this.style.background='rgba(220, 38, 38, 0.2)'; this.style.borderColor='rgba(220, 38, 38, 0.5)'"
                        onmouseout="this.style.background='rgba(220, 38, 38, 0.1)'; this.style.borderColor='rgba(220, 38, 38, 0.3)'"
                        title="Unlink document" 
                        onclick="event.stopPropagation(); window.InternalDocsThreadIntegration.unlinkDoc('${thread.id}', '${safeEscape(thread.internal_doc_id)}')">
                    <i class="fas fa-unlink"></i>
                </button>
            </div>
        `;
    },

    /**
     * Open internal document in viewer/editor
     * 
     * @param {string} docId - Document ID
     * @param {string} docType - Document type ('doc' or 'sheet')
     */
    openDoc(docId, docType = 'doc') {
        console.log('[InternalDocsThreadIntegration] Opening document:', { docId, docType });

        // TODO: Implement document viewer/editor modal
        if (window.showNotification) {
            window.showNotification(`Opening ${docType}: ${docId}`, 'info');
        }

        // Placeholder - open document in modal or new tab
        alert(`TODO: Open internal ${docType} ${docId}`);
    },

    /**
     * Show document details tooltip/modal
     * 
     * @param {string} docId - Document ID
     */
    showDocInfo(docId) {
        console.log('[InternalDocsThreadIntegration] Showing doc info:', docId);

        // TODO: Fetch and display document metadata (created, modified, owner, etc.)
        alert(`TODO: Show document info for ${docId}`);
    },

    /**
     * Unlink internal document from thread
     * 
     * @param {string} threadId - Thread ID
     * @param {string} docId - Document ID to unlink
     */
    async unlinkDoc(threadId, docId) {
        console.log('[InternalDocsThreadIntegration] Unlinking document:', { threadId, docId });

        try {
            const response = await fetch(`${window.API_BASE_URL || ''}/api/internal-docs/${docId}/unlink-thread`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ thread_id: threadId })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || 'Failed to unlink document');
            }

            console.log('[InternalDocsThreadIntegration] Unlink successful');

            if (window.showNotification) {
                window.showNotification('Document unlinked successfully', 'success');
            }

            // Refresh thread card to show placeholder
            if (window.ThreadManager?.refreshThreadCard) {
                window.ThreadManager.refreshThreadCard(threadId);
            }
        } catch (error) {
            console.error('[InternalDocsThreadIntegration] Unlink failed:', error);

            if (window.showNotification) {
                window.showNotification(`Failed to unlink document: ${error.message}`, 'error');
            }
        }
    },

    /**
     * Open modal to link internal document to thread
     * 
     * @param {string} threadId - Thread ID to link document to
     */
    openLinkModal(threadId) {
        console.log('[InternalDocsThreadIntegration] Opening link modal for thread:', threadId);

        // Open the new Internal Docs Link Modal UI
        if (window.InternalDocsLinkModal && typeof window.InternalDocsLinkModal.open === 'function') {
            window.InternalDocsLinkModal.open(threadId);
        } else {
            console.error('[InternalDocsThreadIntegration] InternalDocsLinkModal not available');
            if (window.showNotification) {
                window.showNotification('Internal Docs modal not loaded', 'error');
            }
        }
    },

    /**
     * Link internal document to thread
     * 
     * @param {string} threadId - Thread ID
     * @param {string} docId - Document ID to link
     * @param {string} docType - Document type ('doc' or 'sheet')
     */
    async linkDoc(threadId, docId, docType = 'doc') {
        console.log('[InternalDocsThreadIntegration] Linking document:', { threadId, docId, docType });

        try {
            const response = await fetch(`${window.API_BASE_URL || ''}/api/internal-docs/${docId}/link-thread`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    thread_id: threadId,
                    doc_type: docType
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || 'Failed to link document');
            }

            console.log('[InternalDocsThreadIntegration] Link successful');

            if (window.showNotification) {
                window.showNotification('Document linked successfully', 'success');
            }

            // Refresh thread card to show badge
            if (window.ThreadManager?.refreshThreadCard) {
                window.ThreadManager.refreshThreadCard(threadId);
            }
        } catch (error) {
            console.error('[InternalDocsThreadIntegration] Link failed:', error);

            if (window.showNotification) {
                window.showNotification(`Failed to link document: ${error.message}`, 'error');
            }
        }
    }
};

// Register with ThreadCardRegistry when ready
if (window.ThreadCardRegistry && typeof window.ThreadCardRegistry.registerBadgeRenderer === 'function') {
    window.ThreadCardRegistry.registerBadgeRenderer('internal_docs', {
        condition: 'thread.internal_doc_id !== null',
        renderFunction: 'window.InternalDocsThreadIntegration.renderThreadBadge', // ✅ FIX: Use string reference
        config: {
            icon: 'fa-file-alt',
            color: '#eab308',
            label: 'Internal Docs',
            priority: 4
        },
        placeholderClick: 'window.InternalDocsThreadIntegration.openLinkModal'
    });
    console.log('[InternalDocsThreadIntegration] Registered with ThreadCardRegistry');
} else {
    console.warn('[InternalDocsThreadIntegration] ThreadCardRegistry not available yet');

    // Retry on DOMContentLoaded
    document.addEventListener('DOMContentLoaded', () => {
        if (window.ThreadCardRegistry && typeof window.ThreadCardRegistry.registerBadgeRenderer === 'function') {
            window.ThreadCardRegistry.registerBadgeRenderer('internal_docs', {
                condition: 'thread.internal_doc_id !== null',
                renderFunction: 'window.InternalDocsThreadIntegration.renderThreadBadge',
                config: {
                    icon: 'fa-file-alt',
                    color: '#eab308',
                    label: 'Internal Docs',
                    priority: 4
                },
                placeholderClick: 'window.InternalDocsThreadIntegration.openLinkModal'
            });
            console.log('[InternalDocsThreadIntegration] Registered with ThreadCardRegistry (deferred)');
        }
    });
}

console.log('[InternalDocsThreadIntegration] Module loaded');
