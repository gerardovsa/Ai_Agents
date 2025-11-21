/**
 * FILE: AI_infrastructure/threads/frontend/thread_card_actions.js
 * PURPOSE: Action handlers for thread card operations (extracted from business-ai-platform-v2.html)
 * 
 * DEPENDENCIES:
 * - ThreadManager (from business-ai-platform-v2.html)
 * - MultiAgent (from business-ai-platform-v2.html)
 * - DeviceLockManager (from business-ai-platform-v2.html)
 * 
 * EXPORTS:
 * - ThreadCardActions.renameThread(threadId) - Rename thread title
 * - ThreadCardActions.editThread(threadId) - Edit thread messages
 * - ThreadCardActions.forkThread(threadId) - Fork thread from current point
 * - ThreadCardActions.cloneThread(threadId) - Clone entire thread
 * - ThreadCardActions.archiveThread(threadId) - Archive thread
 * - ThreadCardActions.deleteThread(threadId) - Delete thread
 * - ThreadCardActions.unloadThread(threadId) - Unload from agent to Prime
 * - ThreadCardActions.unlinkSynergy(threadId, synergyId) - Unlink Synergy session
 * - ThreadCardActions.unlinkWorkflow(threadId, workflowId) - Unlink workflow
 * - ThreadCardActions.toggleCopyMenu(threadId) - Toggle copy dropdown
 * - ThreadCardActions.copyThreadContent(threadId, format) - Copy thread (simple/detailed/json)
 * - ThreadCardActions.copyThreadId(threadId) - Copy thread slug
 * - ThreadCardActions.copySynergyInfo(synergyId, title) - Copy Synergy info
 * - ThreadCardActions.addTag(threadId) - Show add tag modal
 * - ThreadCardActions.removeTag(threadId, tag) - Remove tag
 * 
 * USED BY:
 * - business-ai-platform-v2.html (onclick handlers in templates)
 * - AI_infrastructure/threads/frontend/thread_card_templates.js (templates reference these)
 * 
 * RELATED FILES:
 * - AI_infrastructure/threads/frontend/thread_card_templates.js (templates)
 * - AI_infrastructure/threads/frontend/thread_card_realtime.js (Realtime)
 * - AI_infrastructure/threads/styles/thread_card_styles.css (styling)
 * 
 * NOTES:
 * - All functions delegate to existing ThreadManager methods
 * - Provides cleaner namespace for template onclick handlers
 * - Can be extended with custom logic before delegating
 * - Includes event.stopPropagation() where needed
 * 
 * LAST MODIFIED: 2025-11-17 - Created for Phase 4 (Action Handler Extraction)
 */

// Global namespace for thread card actions
window.ThreadCardActions = {

    /**
     * Rename Thread - Start inline rename
     * 
     * @param {string} threadId - Thread slug
     */
    renameThread(threadId) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.startRename === 'function') {
            ThreadManager.startRename(threadId);
        } else if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.renameThread === 'function') {
            ThreadManager.renameThread(threadId);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.renameThread not available');
        }
    },

    /**
     * Edit Thread - Open thread editor
     * 
     * @param {string} threadId - Thread slug
     */
    editThread(threadId) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.editThread === 'function') {
            ThreadManager.editThread(threadId);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.editThread not available');
        }
    },

    /**
     * Fork Thread - Branch from current point
     * 
     * @param {string} threadId - Thread slug
     */
    forkThread(threadId) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.forkThread === 'function') {
            ThreadManager.forkThread(threadId);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.forkThread not available');
        }
    },

    /**
     * Clone Thread - Duplicate entire thread
     * 
     * @param {string} threadId - Thread slug
     */
    cloneThread(threadId) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.cloneThread === 'function') {
            ThreadManager.cloneThread(threadId);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.cloneThread not available');
        }
    },

    /**
     * Archive Thread - Move to archive
     * 
     * @param {string} threadId - Thread slug
     */
    archiveThread(threadId) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.archiveThread === 'function') {
            ThreadManager.archiveThread(threadId);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.archiveThread not available');
        }
    },

    /**
     * Delete Thread - Permanently delete
     * 
     * @param {string} threadId - Thread slug
     */
    deleteThread(threadId) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.deleteThread === 'function') {
            ThreadManager.deleteThread(threadId);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.deleteThread not available');
        }
    },

    /**
     * Unload Thread - Move from agent to Prime
     * 
     * @param {string} threadId - Thread slug
     */
    unloadThread(threadId) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.unloadThread === 'function') {
            ThreadManager.unloadThread(threadId);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.unloadThread not available');
        }
    },

    /**
     * Unlink Synergy Session
     * 
     * @param {string} threadId - Thread slug
     * @param {string} synergyId - Synergy card ID
     */
    unlinkSynergy(threadId, synergyId) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.unlinkSynergy === 'function') {
            ThreadManager.unlinkSynergy(threadId, synergyId);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.unlinkSynergy not available');
        }
    },

    /**
     * Unlink Workflow Automation
     * 
     * @param {string} threadId - Thread slug
     * @param {string} workflowId - Workflow ID
     */
    unlinkWorkflow(threadId, workflowId) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.unlinkWorkflow === 'function') {
            ThreadManager.unlinkWorkflow(threadId, workflowId);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.unlinkWorkflow not available');
        }
    },

    /**
     * Unlink Workflow Slug
     * 
     * @param {string} threadId - Thread slug
     */
    unlinkWorkflowSlug(threadId) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.unlinkWorkflowSlug === 'function') {
            ThreadManager.unlinkWorkflowSlug(threadId);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.unlinkWorkflowSlug not available');
        }
    },

    /**
     * Toggle Copy Menu Dropdown
     * 
     * @param {string} threadId - Thread slug
     */
    toggleCopyMenu(threadId) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.toggleCopyMenu === 'function') {
            ThreadManager.toggleCopyMenu(threadId);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.toggleCopyMenu not available');
        }
    },

    /**
     * Copy Thread Content
     * 
     * @param {string} threadId - Thread slug
     * @param {string} format - Format: 'simple', 'detailed', or 'json'
     */
    copyThreadContent(threadId, format) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.copyThreadContent === 'function') {
            ThreadManager.copyThreadContent(threadId, format);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.copyThreadContent not available');
        }
    },

    /**
     * Copy Full Thread Conversation
     * 
     * @param {string} threadId - Thread slug
     */
    copyThreadConversation(threadId) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.copyThreadConversation === 'function') {
            ThreadManager.copyThreadConversation(threadId);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.copyThreadConversation not available');
        }
    },

    /**
     * Copy Thread ID (slug) to clipboard
     * 
     * @param {string} threadId - Thread slug
     */
    copyThreadId(threadId) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.copyThreadId === 'function') {
            ThreadManager.copyThreadId(threadId);
        } else {
            // Fallback: direct clipboard copy
            navigator.clipboard.writeText(threadId).then(() => {
                console.log(`[ThreadCardActions] Copied thread ID: ${threadId}`);
                // Show toast notification if available
                if (typeof window.showToast === 'function') {
                    window.showToast('Thread ID copied!', 'success');
                }
            }).catch(err => {
                console.error('[ThreadCardActions] Failed to copy thread ID:', err);
            });
        }
    },

    /**
     * Copy Synergy Info
     * 
     * @param {string} synergyId - Synergy card ID
     * @param {string} title - Synergy card title
     */
    copySynergyInfo(synergyId, title) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.copySynergyInfo === 'function') {
            ThreadManager.copySynergyInfo(synergyId, title);
        } else {
            // Fallback: copy Synergy ID
            navigator.clipboard.writeText(synergyId).then(() => {
                console.log(`[ThreadCardActions] Copied Synergy ID: ${synergyId}`);
                if (typeof window.showToast === 'function') {
                    window.showToast('Synergy ID copied!', 'success');
                }
            }).catch(err => {
                console.error('[ThreadCardActions] Failed to copy Synergy ID:', err);
            });
        }
    },

    /**
     * Show Add Tag Modal
     * 
     * @param {string} location - Location identifier ('prime', 'agent-1', etc.)
     * @param {string} threadId - Thread slug
     */
    showAddTagModal(location, threadId) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.showAddTagModal === 'function') {
            ThreadManager.showAddTagModal(location, threadId);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.showAddTagModal not available');
        }
    },

    /**
     * Remove Tag
     * 
     * @param {string} threadId - Thread slug
     * @param {string} tag - Tag to remove
     */
    removeTag(threadId, tag) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.removeTag === 'function') {
            ThreadManager.removeTag(threadId, tag);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.removeTag not available');
        }
    },

    /**
     * Open Synergy Sync Modal
     * 
     * @param {string} threadId - Thread slug
     */
    openSynergySyncModal(threadId) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.openSynergySyncModal === 'function') {
            ThreadManager.openSynergySyncModal(threadId);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.openSynergySyncModal not available');
        }
    },

    /**
     * Open Workflow Link Modal
     * 
     * @param {string} threadId - Thread slug
     */
    openWorkflowLinkModal(threadId) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.openWorkflowLinkModal === 'function') {
            ThreadManager.openWorkflowLinkModal(threadId);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.openWorkflowLinkModal not available');
        }
    },

    /**
     * Open Workflow Details
     * 
     * @param {string} workflowId - Workflow ID
     */
    openWorkflowDetails(workflowId) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.openWorkflowDetails === 'function') {
            ThreadManager.openWorkflowDetails(workflowId);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.openWorkflowDetails not available');
        }
    },

    /**
     * Load Workflow From Slug
     * 
     * @param {string} threadId - Thread slug
     */
    loadWorkflowFromSlug(threadId) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.loadWorkflowFromSlug === 'function') {
            ThreadManager.loadWorkflowFromSlug(threadId);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.loadWorkflowFromSlug not available');
        }
    },

    /**
     * Create New Thread
     * 
     * @param {string} location - Location identifier ('prime', 'agent-1', etc.)
     */
    createNewThread(location) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.showNewChatModal === 'function') {
            ThreadManager.showNewChatModal(location);
        } else if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.createNewThread === 'function') {
            ThreadManager.createNewThread(location);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.createNewThread not available');
        }
    },

    /**
     * Show Thread History
     * 
     * @param {string} location - Location identifier ('prime', 'agent-1', etc.)
     */
    showThreadHistory(location) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.toggleThreadMenu === 'function') {
            ThreadManager.toggleThreadMenu();
        } else if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.showThreadHistory === 'function') {
            ThreadManager.showThreadHistory(location);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.showThreadHistory not available');
        }
    },

    /**
     * Load Thread
     * 
     * @param {string} threadId - Thread slug
     */
    loadThread(threadId) {
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.loadThread === 'function') {
            ThreadManager.loadThread(threadId);
        } else {
            console.warn('[ThreadCardActions] ThreadManager.loadThread not available');
        }
    }
};
