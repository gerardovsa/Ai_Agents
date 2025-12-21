/**
 * FILE: UI/external/modules/synergy/thread_synergy.js
 * PURPOSE: Thread-Synergy integration - Links threads to Synergy cards
 * 
 * EXTRACTED FROM: thread_manager.js (lines 421-4850)
 * DATE: November 20, 2025
 * 
 * DEPENDENCIES:
 * - ThreadManager (window.ThreadManager) - Thread management
 * - synergyBoard (window.synergyBoard) - Synergy dashboard
 * - UserAuth (window.UserAuth) - User authentication
 * - API_BASE_URL (window.API_BASE_URL) - Backend API endpoint
 * 
 * EXPORTS:
 * - ThreadSynergyIntegration.linkThreadToSynergy(threadId, synergyId, synergyName)
 * - ThreadSynergyIntegration.unlinkThreadFromSynergy(threadId)
 * - ThreadSynergyIntegration.handleThreadDrop(event, synergyId)
 * - ThreadSynergyIntegration.createThreadForSession(session)
 * - ThreadSynergyIntegration.linkThreadToSession(sessionId, threadId)
 * - ThreadSynergyIntegration.renderLinkedThreads(threadIds)
 * - ThreadSynergyIntegration.openThread(threadId, agentId)
 * - ThreadSynergyIntegration.refreshCardThreads(sessionId)
 * 
 * USED BY:
 * - synergy-board-init.js (drag-and-drop integration)
 * - synergy-card-renderer.js (thread display in cards)
 * - thread-card-actions.js (link/unlink buttons)
 * 
 * RELATED FILES:
 * - synergy-board-init.js (Synergy dashboard initialization)
 * - thread_manager.js (main thread management)
 * - thread-card-templates.js (thread card UI with Synergy badges)
 * 
 * NOTES:
 * - All functions handle thread<->Synergy bidirectional linking
 * - Integrates with ThreadManager.syncThreadLocationEverywhere()
 * - Uses unified thread-info-card rendering system
 * - Supports drag-and-drop from thread cards to Synergy cards
 * 
 * LAST MODIFIED: 2025-11-20 - Initial extraction from thread_manager.js
 */

console.log('📦 [THREAD-SYNERGY] Loading thread-synergy integration module...');

window.ThreadSynergyIntegration = {
    apiBaseUrl: window.API_BASE_URL || 'http://localhost:5001',

    /**
     * Link a thread to a Synergy session
     * Called when user drags thread to Synergy card or clicks "Link to Synergy"
     * 
     * @param {string} threadId - Thread ID (slug format: "1762828793392")
     * @param {string} synergyId - Synergy session ID
     * @param {string} synergyName - Synergy session name (optional, for caching)
     */
    async linkThreadToSynergy(threadId, synergyId, synergyName = null) {
        console.log(`🔗 [THREAD-SYNERGY] Linking thread ${threadId} to Synergy ${synergyId}`);

        try {
            // Step 1: Update thread object in memory
            const thread = window.ThreadManager?.threads?.find(t => t.id === threadId);
            if (thread) {
                thread.synergy_card_id = synergyId;
                thread.synergy_card_name = synergyName;
                thread.updated = new Date().toISOString();
            }

            // Step 2: Persist to database via /api/threads/upsert
            const userId = (window.UserAuth?.user?.id || window.UserAuth?.user?.user_id) || 1;
            const apiBaseUrl = window.API_BASE_URL || 'http://localhost:5001';

            console.log(`[THREAD-SYNERGY] Saving synergy_card_id to database...`);
            const upsertResponse = await fetch(`${apiBaseUrl}/api/threads/upsert`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${window.UserAuth?.token || localStorage.getItem('auth_token') || ''}`
                },
                body: JSON.stringify({
                    thread_id: threadId,
                    user_id: userId,
                    title: thread?.title || thread?.name || 'Untitled Thread',
                    location: thread?.location || 'prime',
                    tags: thread?.tags || [],
                    synergy_card_id: synergyId  // ✅ CRITICAL: Save synergy_card_id to database
                })
            });

            const upsertData = await upsertResponse.json();
            if (!upsertData.success) {
                throw new Error(upsertData.error || 'Failed to save synergy_card_id to database');
            }

            console.log(`✅ [THREAD-SYNERGY] synergy_card_id saved to database`);

            // Step 3: Update Synergy session with thread link (bidirectional)
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/${synergyId}/link-thread`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${window.UserAuth?.token || localStorage.getItem('auth_token') || ''}`
                },
                body: JSON.stringify({
                    thread_id: threadId,
                    user_id: userId
                })
            });

            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || 'Failed to link thread to Synergy');
            }

            console.log('✅ [THREAD-SYNERGY] Bidirectional link established (thread ↔ synergy)');

            // Step 4: Show success notification
            if (window.showNotification) {
                window.showNotification('Thread linked to Synergy card', 'success');
            }

            // Step 5: Refresh UI
            if (window.synergyBoard) {
                await window.synergyBoard.refreshCardThreads?.(synergyId);
            }

            // Step 6: Refresh thread card display to show synergy badge
            if (window.ThreadManager?.refreshAllThreadInfoCards) {
                window.ThreadManager.refreshAllThreadInfoCards(threadId);
            } else if (window.ThreadManager?.renderThreads) {
                window.ThreadManager.renderThreads();
            }

            return { success: true, threadId, synergyId };

        } catch (error) {
            console.error('❌ [THREAD-SYNERGY] Failed to link thread:', error);
            if (window.showNotification) {
                window.showNotification('Failed to link thread: ' + error.message, 'error');
            }
            return { success: false, error: error.message };
        }
    },

    /**
     * Unlink a thread from its Synergy session
     * Called when user clicks "Unlink from Synergy" on thread card
     * 
     * @param {string} threadId - Thread ID to unlink
     */
    async unlinkThreadFromSynergy(threadId) {
        console.log(`🔓 [THREAD-SYNERGY] Unlinking thread ${threadId} from Synergy`);

        try {
            // Step 1: Get thread to find current Synergy link
            const thread = window.ThreadManager?.threads.find(t => t.id === threadId);
            if (!thread) {
                throw new Error('Thread not found');
            }

            const synergyId = thread.synergy_card_id;
            if (!synergyId) {
                console.warn('[THREAD-SYNERGY] Thread not linked to any Synergy session');
                return { success: true, message: 'Thread not linked to Synergy' };
            }

            // Step 2: Update thread to remove Synergy link
            if (window.ThreadManager) {
                await window.ThreadManager.syncThreadLocationEverywhere(
                    threadId,
                    thread.agent || 'main',
                    {
                        removeLinks: ['synergy']
                    }
                );
            }

            // Step 3: Update Synergy session to remove thread link
            const userId = (window.UserAuth?.user?.id || window.UserAuth?.user?.user_id) || 1;
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/${synergyId}/unlink-thread`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${window.UserAuth?.token || localStorage.getItem('auth_token') || ''}`
                },
                body: JSON.stringify({
                    thread_id: threadId,
                    user_id: userId
                })
            });

            const result = await response.json();

            if (!result.success) {
                console.warn('[THREAD-SYNERGY] Backend unlink failed:', result.error);
                // Continue anyway - local state already updated
            }

            console.log('✅ [THREAD-SYNERGY] Thread unlinked successfully');

            // Step 4: Show success notification
            if (window.showNotification) {
                window.showNotification('Thread unlinked from Synergy card', 'success');
            }

            // Step 5: Refresh UI
            if (window.synergyBoard) {
                await window.synergyBoard.refreshCardThreads?.(synergyId);
            }

            // Step 6: Refresh thread card display
            if (window.ThreadManager?.renderThreads) {
                window.ThreadManager.renderThreads();
            }

            return { success: true, threadId, synergyId };

        } catch (error) {
            console.error('❌ [THREAD-SYNERGY] Failed to unlink thread:', error);
            if (window.showNotification) {
                window.showNotification('Failed to unlink thread: ' + error.message, 'error');
            }
            return { success: false, error: error.message };
        }
    },

    /**
     * Handle thread drop onto Synergy card (drag-and-drop integration)
     * Called from Synergy card's ondrop handler
     * 
     * @param {DragEvent} event - Drop event
     * @param {string} synergyId - Target Synergy session ID
     */
    async handleThreadDrop(event, synergyId) {
        event.preventDefault();
        event.stopPropagation();
        event.currentTarget?.classList.remove('drag-over');

        // Get dropped thread ID
        const threadId = event.dataTransfer.getData('text/plain');
        if (!threadId) {
            console.warn('[THREAD-SYNERGY] No thread ID in drop event');
            return;
        }

        console.log(`🎯 [THREAD-SYNERGY] Thread ${threadId} dropped on Synergy ${synergyId}`);

        // Hide welcome container when thread is dropped into Prime
        const welcomeContainer = document.getElementById('prime-welcome-container');
        if (welcomeContainer) {
            welcomeContainer.style.display = 'none';
            console.log('[WELCOME] Hidden - thread dropped into chat');
        }

        // Get Synergy session name for caching
        let synergyName = null;
        if (window.synergyBoard?.sessions) {
            const session = window.synergyBoard.sessions.find(s => s.session_id === synergyId);
            synergyName = session?.title || null;
        }

        // Link thread to Synergy
        await this.linkThreadToSynergy(threadId, synergyId, synergyName);
    },

    /**
     * Create a new thread for a Synergy session
     * Called when resuming work on a Synergy session that has no threads
     * 
     * @param {Object} session - Synergy session object
     * @returns {string|null} - New thread ID or null on failure
     */
    async createThreadForSession(session) {
        console.log('🆕 [THREAD-SYNERGY] Creating new thread for session:', session.title);

        try {
            // Create thread via ThreadManager API
            const response = await fetch(`${this.apiBaseUrl}/api/threads/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${window.UserAuth?.token || localStorage.getItem('auth_token') || ''}`
                },
                body: JSON.stringify({
                    title: session.title,  // Use session title as thread title
                    location: 'prime',      // Always create in Prime Agent
                    agent_id: 1,
                    synergy_card_id: session.session_id,  // Link to Synergy session
                    tags: session.tags ? JSON.parse(session.tags) : []
                })
            });

            if (!response.ok) {
                throw new Error(`API returned ${response.status}`);
            }

            const data = await response.json();
            const newThreadId = data.thread?.id || data.thread?.thread_id || data.id;

            if (!newThreadId) {
                throw new Error('No thread ID in response');
            }

            console.log('✅ [THREAD-SYNERGY] Thread created:', newThreadId);

            // Update session with new thread ID
            await this.linkThreadToSession(session.session_id, newThreadId);

            return newThreadId;

        } catch (error) {
            console.error('❌ [THREAD-SYNERGY] Failed to create thread:', error);
            if (window.showNotification) {
                window.showNotification('Failed to create thread: ' + error.message, 'error');
            }
            return null;
        }
    },

    /**
     * Link a thread to a Synergy session (backend-only update)
     * Updates the Synergy session's thread_ids array
     * 
     * @param {string} sessionId - Synergy session ID
     * @param {string} threadId - Thread ID to link
     */
    async linkThreadToSession(sessionId, threadId) {
        console.log(`🔗 [THREAD-SYNERGY] Linking thread to session:`, { sessionId, threadId });

        try {
            // Get current session
            const session = window.synergyBoard?.sessions?.find(s => s.session_id === sessionId);
            if (!session) {
                console.warn('[THREAD-SYNERGY] Session not found in synergyBoard');
                // Continue anyway - backend will handle it
            }

            // Add thread ID to array
            let threadIds = [];
            if (session?.thread_ids) {
                try {
                    threadIds = JSON.parse(session.thread_ids);
                } catch (e) {
                    threadIds = [];
                }
            }

            if (!threadIds.includes(threadId)) {
                threadIds.push(threadId);

                // Update session via API
                const response = await fetch(`${this.apiBaseUrl}/api/synergy/${sessionId}`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${window.UserAuth?.token || localStorage.getItem('auth_token') || ''}`
                    },
                    body: JSON.stringify({
                        thread_ids: JSON.stringify(threadIds),
                        agent_ids: JSON.stringify([1])  // Prime Agent
                    })
                });

                if (!response.ok) {
                    throw new Error(`API returned ${response.status}`);
                }

                const result = await response.json();
                if (!result.success) {
                    throw new Error(result.error || 'Update failed');
                }

                console.log('✅ [THREAD-SYNERGY] Thread linked to session');

                // Refresh session data
                if (window.synergyBoard?.loadSessions) {
                    await window.synergyBoard.loadSessions();
                }
            }

        } catch (error) {
            console.error('❌ [THREAD-SYNERGY] Failed to link thread to session:', error);
            if (window.showNotification) {
                window.showNotification('Failed to update Synergy session: ' + error.message, 'error');
            }
        }
    },

    /**
     * Render linked threads with agent badges
     * SYNERGY INTEGRATION FEATURE - Shows threads connected to this project
     * 
     * @param {string[]} threadIds - Array of thread IDs to render
     * @returns {string} - HTML for linked threads section
     */
    async renderLinkedThreads(threadIds) {
        if (!threadIds || !Array.isArray(threadIds) || threadIds.length === 0) {
            return '<div class="no-threads"><i class="fas fa-link-slash"></i> No threads linked</div>';
        }

        // Check if ThreadManager is available
        if (!window.ThreadManager) {
            console.error('[THREAD-SYNERGY] ThreadManager not available');
            return `<div class="threads-loading"><i class="fas fa-spinner fa-spin"></i> Loading ThreadManager...</div>`;
        }

        try {
            // Fetch thread details and agent assignments
            // Silently handle errors - don't show connection lost notifications
            let response;
            try {
                response = await fetch(`${this.apiBaseUrl}/api/threads/details`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ thread_ids: threadIds })
                });
            } catch (fetchError) {
                // Network error - silently return fallback UI
                console.warn('[THREAD-SYNERGY] Network error fetching thread details (suppressed notification)');
                return `<div class="threads-error"><i class="fas fa-exclamation-triangle"></i> ${threadIds.length} thread(s) linked</div>`;
            }

            if (!response.ok) {
                console.warn('[THREAD-SYNERGY] Failed to fetch thread details (HTTP ' + response.status + ')');
                return `<div class="threads-error"><i class="fas fa-exclamation-triangle"></i> ${threadIds.length} thread(s) linked</div>`;
            }

            const result = await response.json();
            const threads = result.data || result; // Handle both {success, data} format and direct array

            if (!threads || threads.length === 0) {
                return '<div class="no-threads"><i class="fas fa-link-slash"></i> No threads found</div>';
            }

            // Fetch synergy metadata for threads (like thread history does)
            const synergyIdsToLoad = Array.from(new Set(threads
                .map(t => t.synergy_card_id)
                .filter(Boolean)));

            // Use global synergy session cache
            if (!window._synergySessionCache) window._synergySessionCache = {};
            const cache = window._synergySessionCache;

            if (synergyIdsToLoad.length > 0) {
                try {
                    const missing = synergyIdsToLoad.filter(id => !cache[id]);
                    if (missing.length > 0) {
                        const idsParam = missing.join(',');
                        const resp = await fetch(`${this.apiBaseUrl}/api/synergy?ids=${encodeURIComponent(idsParam)}`);
                        if (resp.ok) {
                            const data = await resp.json();
                            if (data?.success && data?.sessions) {
                                Object.entries(data.sessions).forEach(([sid, session]) => {
                                    cache[sid] = session;
                                });
                            }
                        }
                    }
                } catch (err) {
                    console.warn('[THREAD-SYNERGY] Failed to fetch synergy metadata:', err);
                }
            }

            // Build unified thread-info containers for each thread
            const threadsHTML = threads.map(thread => {
                // Get synergy metadata from cache (like thread history does)
                const synergyMeta = thread.synergy_card_id ? cache[thread.synergy_card_id] : null;
                const synergyTitle = synergyMeta
                    ? (synergyMeta.title || thread.synergy_card_id)
                    : (thread.synergy_card_name || thread.synergy_card_id || 'Unknown Session');
                const synergyPriority = synergyMeta ? (synergyMeta.priority || '') : '';
                const synergyDesc = synergyMeta ? (synergyMeta.description || '') : '';
                const synergyUsers = synergyMeta
                    ? (Array.isArray(synergyMeta.assignees) ? synergyMeta.assignees.join(', ') : '')
                    : '';
                const synergyUpdated = synergyMeta
                    ? (synergyMeta.last_active ? new Date(synergyMeta.last_active).toLocaleString() : '')
                    : '';

                // Normalize thread object structure for ThreadManager
                // CRITICAL: Use thread_slug (the actual slug like "1762828793392") NOT id (numeric DB ID like 18)
                const normalizedThread = {
                    id: thread.thread_slug || thread.id,  // FIXED: Prioritize slug over numeric ID
                    title: thread.name || thread.thread_slug || thread.id,
                    created: thread.created_at || thread.created,
                    updated: thread.updated_at || thread.updated,
                    message_count: thread.message_count || 0,
                    messages: [],
                    tags: thread.tags || [],
                    synergy_card_id: thread.synergy_card_id,
                    synergy_card_name: synergyTitle,
                    synergy_card_desc: synergyDesc,
                    synergy_card_users: synergyUsers,
                    synergy_card_updated: synergyUpdated,
                    synergy_card_priority: synergyPriority,
                    agent: thread.agent_id || 'prime'
                };

                // Temporarily add to ThreadManager.threads if not exists (for rendering)
                const existingThread = window.ThreadManager.threads.find(t => t.id === normalizedThread.id);
                if (!existingThread) {
                    window.ThreadManager.threads.push(normalizedThread);
                }

                // Render unified container
                const threadInfoHTML = window.ThreadManager.renderThreadInfoContainer?.(
                    'synergy',
                    normalizedThread.id,
                    true  // compact mode
                ) || `<div class="thread-card" data-thread-id="${normalizedThread.id}">${normalizedThread.title}</div>`;

                return `
                    <div class="synergy-linked-thread-wrapper" 
                         data-thread-id="${normalizedThread.id}"
                         draggable="true"
                         ondragstart="ThreadManager.handleDragStart?.(event)"
                         onclick="ThreadSynergyIntegration.openThread('${normalizedThread.id}', '${thread.agent_id || 'prime'}')">
                        ${threadInfoHTML}
                    </div>
                `;
            }).join('');

            return `
                <div class="linked-threads-container">
                    <div class="linked-threads-list">
                        ${threadsHTML}
                    </div>
                </div>
            `;

        } catch (error) {
            console.error('[THREAD-SYNERGY] Error rendering linked threads:', error);
            return `<div class="threads-error"><i class="fas fa-exclamation-triangle"></i> Error loading threads</div>`;
        }
    },

    /**
     * Open a thread in the appropriate agent column
     * Called when clicking on a linked thread in a Synergy card
     * 
     * @param {string} threadId - Thread ID to open
     * @param {string} agentId - Agent column to open thread in ('prime', 'agent-1', etc.)
     */
    openThread(threadId, agentId) {
        console.log(`📂 [THREAD-SYNERGY] Opening thread ${threadId} in agent ${agentId}`);

        // Switch to AI Agents tab
        const agentsTab = document.querySelector('[data-tab="agents"]');
        if (agentsTab) {
            agentsTab.click();
        }

        // Load thread in the agent column
        if (window.ThreadManager?.loadThread) {
            window.ThreadManager.loadThread(threadId, agentId);
        } else if (window.threadManager?.loadThread) {
            window.threadManager.loadThread(threadId, agentId);
        } else {
            console.warn('[THREAD-SYNERGY] ThreadManager.loadThread not available');
            if (window.showNotification) {
                window.showNotification(`Opening thread ${threadId} in ${agentId}`, 'info');
            }
        }
    },

    /**
     * Refresh linked threads section for a specific Synergy card
     * Called after linking/unlinking threads to update the UI
     * 
     * @param {string} sessionId - Synergy session ID
     */
    async refreshCardThreads(sessionId) {
        console.log(`🔄 [THREAD-SYNERGY] Refreshing threads for card ${sessionId}`);

        try {
            // Fetch updated session data
            const userId = window.currentUserId || window.UserAuth?.user?.id || 14;
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/${sessionId}?user_id=${userId}`);
            if (!response.ok) {
                console.warn('[THREAD-SYNERGY] Failed to fetch session for refresh');
                return;
            }

            const result = await response.json();
            const session = result.session || result;

            if (!session) {
                console.warn('[THREAD-SYNERGY] No session data returned');
                return;
            }

            // Parse thread IDs
            let threadIds = [];
            try {
                threadIds = JSON.parse(session.thread_ids || '[]');
            } catch (e) {
                threadIds = [];
            }

            const threadsSection = document.getElementById(`threads-section-${sessionId}`);

            if (!threadsSection) {
                console.warn(`[THREAD-SYNERGY] threads-section-${sessionId} not found in DOM`);
                return;
            }

            // Find or create the container for threads
            let container = threadsSection.querySelector('.thread-list-loading, .thread-list, .no-threads, .drop-zone-prompt');

            if (threadIds.length > 0) {
                // Show loading temporarily
                if (container) {
                    container.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading linked threads...';
                }

                // Render threads
                const threadsHTML = await this.renderLinkedThreads(threadIds);
                if (container) {
                    container.outerHTML = threadsHTML;
                } else {
                    threadsSection.insertAdjacentHTML('beforeend', threadsHTML);
                }
            } else {
                // No threads: show drag-and-drop prompt
                if (container) {
                    container.innerHTML = '<i class="fas fa-hand-pointer"></i> Drag and drop a thread here to link';
                    container.className = 'thread-list-loading drop-zone-prompt';
                }
            }

            console.log(`✅ [THREAD-SYNERGY] Refreshed threads for card ${sessionId}`);
        } catch (error) {
            console.error('❌ [THREAD-SYNERGY] Error refreshing card threads:', error);
        }
    },

    /**
     * Parse JSON field safely (helper function)
     * @param {string|Array} field - JSON string or already parsed array
     * @param {Array} defaultValue - Default value if parsing fails
     * @returns {Array} - Parsed array
     */
    parseJsonField(field, defaultValue = []) {
        if (!field) return defaultValue;
        if (Array.isArray(field)) return field;
        try {
            return JSON.parse(field);
        } catch (e) {
            return defaultValue;
        }
    }
};

// Make available globally
window.ThreadSynergyIntegration = window.ThreadSynergyIntegration;

console.log('✅ [THREAD-SYNERGY] Thread-Synergy integration loaded');
