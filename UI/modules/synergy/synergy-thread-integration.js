/**
 * FILE: UI/external/modules/synergy/synergy-thread-integration.js
 * PURPOSE: Thread card integration handlers for Synergy module
 * 
 * ARCHITECTURE:
 * - Provides handlers declared in synergy/manifest.json
 * - Called by ThreadCardRegistry for badge rendering and drop handling
 * - Integrates with existing Synergy backend API
 * 
 * EXPORTS:
 * - SynergyThreadIntegration.linkThreadToSession() - Drop handler
 * - SynergyThreadIntegration.renderThreadBadge() - Badge renderer
 * - SynergyThreadIntegration.handleRealtimeUpdate() - WebSocket handler
 * - SynergyThreadIntegration.handleBadgeClick() - Badge click action
 * - SynergyThreadIntegration.startDrag() - Drag start handler
 * 
 * USED BY:
 * - ThreadCardRegistry (UI/modules/thread-cards/thread-card-registry.js)
 * 
 * LAST MODIFIED: 2025-11-28 - Initial implementation
 */

window.SynergyThreadIntegration = {
    /**
     * Link thread to Synergy session (drop handler)
     * 
     * Called when user drops a Synergy session onto a thread card
     * 
     * @param {string} sessionDataJson - JSON string with session data
     * @param {string} threadId - Thread ID to link to
     * @param {string} location - Drop location ('prime', 'agent-X', etc.)
     * @returns {Promise<void>}
     */
    async linkThreadToSession(sessionDataJson, threadId, location) {
        console.log('[SynergyThreadIntegration] Linking thread to session:', threadId);
        
        try {
            // Parse session data
            const sessionData = JSON.parse(sessionDataJson);
            const sessionId = sessionData.id || sessionData.session_id;
            
            if (!sessionId) {
                throw new Error('No session ID in drop data');
            }

            // Call backend API to create link
            const response = await fetch('/api/synergy/link-to-thread', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    thread_id: threadId,
                    linked_by: window.currentUserId || 1
                })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const result = await response.json();
            console.log('[SynergyThreadIntegration] Link created:', result);

            // Show notification
            if (typeof showNotification === 'function') {
                showNotification(`Thread linked to Synergy session: ${sessionData.title || sessionId}`, 'success');
            }

            // Refresh thread card to show new badge
            if (window.ThreadManager && typeof window.ThreadManager.refreshThreadCard === 'function') {
                window.ThreadManager.refreshThreadCard(threadId);
            }

        } catch (error) {
            console.error('[SynergyThreadIntegration] Link failed:', error);
            if (typeof showNotification === 'function') {
                showNotification(`Failed to link thread: ${error.message}`, 'error');
            }
        }
    },

    /**
     * Render badge for thread linked to Synergy session
     * 
     * @param {Object} thread - Thread object
     * @param {Object} config - Badge configuration from manifest
     * @returns {string} HTML string for badge
     */
    renderThreadBadge(thread, config) {
        const safeEscape = window.safeEscape || ((str) => String(str).replace(/[&<>"']/g, ''));
        
        const synergyDisplay = thread.synergy_card_title || thread.synergy_card_id || 'Synergy Session';
        const synergyId = thread.synergy_card_id;
        
        if (!synergyId) {
            return ''; // No badge if not linked
        }

        // Get metadata if available
        const synergyMeta = thread.synergy_meta || {};
        const priority = synergyMeta.priority || '';

        return `
            <div class="thread-item-synergy thread-item-synergy-linked" data-synergy-id="${synergyId}">
                <button class="synergy-badge" style="background: ${config.color}; color: white; border: none; padding: 6px 12px; border-radius: 6px; display: flex; align-items: center; gap: 8px; font-size: 13px; cursor: pointer; flex: 1;"
                    onclick="event.stopPropagation(); window.SynergyThreadIntegration.handleBadgeClick('${safeEscape(synergyId)}', '${safeEscape(synergyDisplay)}', '${thread.id}')"
                    data-tooltip-title="${safeEscape(synergyDisplay)}"
                    data-tooltip-desc="${synergyMeta.description ? safeEscape(synergyMeta.description) : ''}"
                    data-tooltip-users="${synergyMeta.assignees && Array.isArray(synergyMeta.assignees) ? safeEscape(synergyMeta.assignees.join(', ')) : ''}"
                    data-tooltip-updated="${synergyMeta.last_active ? new Date(synergyMeta.last_active).toLocaleString() : ''}">
                    <i class="fas ${config.icon}"></i>
                    <span class="synergy-badge-title">${synergyDisplay}</span>
                    ${priority ? `<span class="synergy-badge-priority" style="background: white; color: ${config.color}; padding: 2px 6px; border-radius: 4px; font-size: 11px; margin-left: 4px;">${priority}</span>` : ''}
                </button>
                <button class="thread-synergy-info" title="Show description" onclick="event.stopPropagation(); const badge = this.parentElement.querySelector('.synergy-badge[data-tooltip-title]'); if (badge && window.showSynergyTooltip) { window.showSynergyTooltip(badge, event); }">
                    <i class="fas fa-question-circle"></i>
                </button>
                <button class="thread-synergy-popout" title="Open in popup" onclick="event.stopPropagation(); if(window.synergyPopupModal) { window.synergyPopupModal.open('${safeEscape(synergyId)}'); } else { console.error('Synergy popup modal not loaded'); }">
                    <i class="fas fa-external-link-alt"></i>
                </button>
                <button class="thread-synergy-unlink" title="Unlink Synergy session" onclick="event.stopPropagation(); window.SynergyThreadIntegration.unlinkSession('${thread.id}', '${synergyId}')">
                    <i class="fas fa-unlink"></i>
                </button>
            </div>
        `;
    },

    /**
     * Handle badge click - copy Synergy info to clipboard
     * 
     * @param {string} synergyId - Synergy session ID
     * @param {string} synergyTitle - Synergy session title
     * @param {string} threadId - Thread ID
     */
    handleBadgeClick(synergyId, synergyTitle, threadId) {
        console.log('[SynergyThreadIntegration] Badge clicked:', synergyId);
        
        // Call existing ThreadManager function
        if (window.ThreadManager && typeof window.ThreadManager.copySynergyInfo === 'function') {
            window.ThreadManager.copySynergyInfo(synergyId, synergyTitle);
        } else {
            // Fallback: Copy to clipboard
            navigator.clipboard.writeText(`Synergy: ${synergyTitle} (${synergyId})`).then(() => {
                if (typeof showNotification === 'function') {
                    showNotification('Synergy info copied to clipboard', 'success');
                }
            });
        }
    },

    /**
     * Unlink thread from Synergy session
     * 
     * @param {string} threadId - Thread ID
     * @param {string} synergyId - Synergy session ID
     */
    async unlinkSession(threadId, synergyId) {
        console.log('[SynergyThreadIntegration] Unlinking:', threadId, synergyId);
        
        if (window.ThreadManager && typeof window.ThreadManager.unlinkSynergy === 'function') {
            await window.ThreadManager.unlinkSynergy(threadId, synergyId);
        } else {
            console.error('[SynergyThreadIntegration] ThreadManager.unlinkSynergy not available');
        }
    },

    /**
     * Start drag operation for Synergy session
     * 
     * @param {DragEvent} event - Drag event
     * @param {Object} sessionData - Synergy session data
     */
    startDrag(event, sessionData) {
        console.log('[SynergyThreadIntegration] Starting drag:', sessionData.id);
        
        // Set data transfer
        event.dataTransfer.setData('application/x-synergy-session', JSON.stringify(sessionData));
        event.dataTransfer.effectAllowed = 'link';
        
        // Visual feedback
        if (event.target) {
            event.target.style.opacity = '0.5';
        }
    },

    /**
     * Handle real-time events related to Synergy-thread linkages
     * 
     * @param {Object} eventData - Event data with thread_id, session_id, etc.
     */
    async handleRealtimeUpdate(eventData) {
        console.log('[SynergyThreadIntegration] Realtime event:', eventData);
        
        const threadId = eventData.thread_id;
        if (!threadId) {
            return;
        }

        // Refresh affected thread card
        if (window.ThreadManager && typeof window.ThreadManager.refreshThreadCard === 'function') {
            await window.ThreadManager.refreshThreadCard(threadId);
            console.log('[SynergyThreadIntegration] Thread card refreshed:', threadId);
        }

        // Show notification for important events
        if (eventData.event_type === 'thread_linked_to_synergy') {
            if (typeof showNotification === 'function') {
                showNotification(`Thread linked to Synergy session`, 'info');
            }
        } else if (eventData.event_type === 'thread_unlinked_from_synergy') {
            if (typeof showNotification === 'function') {
                showNotification(`Thread unlinked from Synergy session`, 'info');
            }
        }
    }
};

console.log('[SynergyThreadIntegration] Loaded - handlers registered for ThreadCardRegistry');
