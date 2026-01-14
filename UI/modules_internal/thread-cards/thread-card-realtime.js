/**
 * FILE: AI_infrastructure/threads/frontend/thread_card_realtime.js
 * PURPOSE: Supabase Realtime subscription manager for thread cards
 * 
 * DEPENDENCIES:
 * - Supabase client (from business-ai-platform-v2.html)
 * - ThreadManager (from business-ai-platform-v2.html)
 * 
 * EXPORTS:
 * - ThreadCardRealtime.initialize() - Start Realtime subscriptions
 * - ThreadCardRealtime.cleanup() - Stop all subscriptions
 * - ThreadCardRealtime.handleThreadUpdate(payload) - Handle UPDATE events
 * - ThreadCardRealtime.handleThreadInsert(payload) - Handle INSERT events
 * - ThreadCardRealtime.handleThreadDelete(payload) - Handle DELETE events
 * 
 * USED BY:
 * - business-ai-platform-v2.html (ThreadManager initialization)
 * 
 * RELATED FILES:
 * - AI_infrastructure/threads/frontend/thread_card_templates.js (templates)
 * - AI_infrastructure/threads/frontend/thread_card_actions.js (actions)
 * - AI_infrastructure/threads/styles/thread_card_styles.css (styling)
 * 
 * NOTES:
 * - Subscribes to sessions.threads table (INSERT, UPDATE, DELETE)
 * - Auto-refreshes affected thread cards across all locations
 * - Handles new schema columns: thread_lock_user_id, automation_slug, automation_title
 * - Debounces rapid updates to prevent UI flicker
 * - Maintains subscription state for cleanup
 * 
 * LAST MODIFIED: 2025-11-17 - Created for Phase 3 (Realtime integration)
 */

// Global namespace for thread card Realtime manager
window.ThreadCardRealtime = {

    // Subscription state
    subscription: null,
    channel: null,
    isInitialized: false,
    updateDebounceTimers: {},

    /**
     * Initialize Realtime subscriptions for threads table
     * NOW USES: SupabaseConnectionManager (prevents duplicate connections)
     * Subscribes to INSERT, UPDATE, DELETE events
     * 
     * @returns {Promise<void>}
     */
    async initialize() {
        if (this.isInitialized) {
            console.log('[ThreadCardRealtime] Already initialized');
            return;
        }

        // ✅ Wait for SupabaseConnectionManager
        if (!window.SupabaseConnectionManager) {
            console.warn('[ThreadCardRealtime] SupabaseConnectionManager not available');
            return;
        }

        console.log('[ThreadCardRealtime] Initializing with connection manager...');

        try {
            // ✨ USE CONNECTION MANAGER (prevents duplicate connections)
            this.channel = await window.SupabaseConnectionManager.subscribeChannel(
                'threads-realtime-channel',
                {
                    schema: 'sessions',
                    table: 'threads',
                    event: '*', // All events
                    callback: (payload) => {
                        // Route to appropriate handler
                        if (payload.eventType === 'INSERT') {
                            this.handleThreadInsert(payload);
                        } else if (payload.eventType === 'UPDATE') {
                            this.handleThreadUpdate(payload);
                        } else if (payload.eventType === 'DELETE') {
                            this.handleThreadDelete(payload);
                        }
                    }
                }
            );

            if (!this.channel) {
                console.warn('[ThreadCardRealtime] Realtime unavailable - using fallback mode');
                return;
            }

            this.isInitialized = true;
            console.log('[ThreadCardRealtime] Initialized with connection manager');

        } catch (error) {
            console.error('[ThreadCardRealtime] Failed to initialize Realtime:', error);
        }
    },

    /**
     * Handle INSERT event - New thread created
     * 
     * @param {Object} payload - Supabase INSERT payload
     * @param {Object} payload.new - New thread record
     */
    handleThreadInsert(payload) {
        console.log('[ThreadCardRealtime] INSERT:', payload.new.thread_slug);

        const newThread = payload.new;

        // Check if ThreadManager exists
        if (typeof ThreadManager === 'undefined') {
            console.warn('[ThreadCardRealtime] ThreadManager not available');
            return;
        }

        // Add new thread to ThreadManager cache
        const formattedThread = this._formatThread(newThread);

        // Check if thread already exists (avoid duplicates)
        const existingIndex = ThreadManager.threads.findIndex(t => t.id === formattedThread.id);
        if (existingIndex === -1) {
            ThreadManager.threads.unshift(formattedThread); // Add to beginning
            console.log(`[ThreadCardRealtime] Added new thread to cache: ${formattedThread.id}`);
        }

        // Refresh thread history sidebar if open
        if (typeof ThreadManager.refreshThreadHistorySidebar === 'function') {
            ThreadManager.refreshThreadHistorySidebar();
        }

        // Refresh agent panels if thread has agent assignment
        if (newThread.agent && typeof MultiAgent !== 'undefined') {
            const agentMatch = newThread.agent.match(/agent-(\d+)/);
            if (agentMatch) {
                MultiAgent.refreshAgentThreads(newThread.agent);
            }
        }
    },

    /**
     * Handle UPDATE event - Thread modified
     * Debounces rapid updates to prevent UI flicker
     * 
     * @param {Object} payload - Supabase UPDATE payload
     * @param {Object} payload.old - Old thread record
     * @param {Object} payload.new - Updated thread record
     */
    handleThreadUpdate(payload) {
        console.log('[ThreadCardRealtime] UPDATE:', payload.new.thread_slug);

        const updatedThread = payload.new;
        const threadId = updatedThread.thread_slug;

        // Debounce rapid updates (prevent flicker from multiple field updates)
        if (this.updateDebounceTimers[threadId]) {
            clearTimeout(this.updateDebounceTimers[threadId]);
        }

        this.updateDebounceTimers[threadId] = setTimeout(() => {
            this._applyThreadUpdate(updatedThread);
            delete this.updateDebounceTimers[threadId];
        }, 300); // 300ms debounce
    },

    /**
     * Apply thread update (internal, called after debounce)
     * @private
     */
    _applyThreadUpdate(updatedThread) {
        // Check if ThreadManager exists
        if (typeof ThreadManager === 'undefined') {
            console.warn('[ThreadCardRealtime] ThreadManager not available');
            return;
        }

        const formattedThread = this._formatThread(updatedThread);

        // 🔧 FIX 1: Check if linkage changed (before updating cache)
        let linkageChanged = false;
        const existingIndex = ThreadManager.threads.findIndex(t => t.id === formattedThread.id);
        if (existingIndex !== -1) {
            const oldThread = ThreadManager.threads[existingIndex];
            linkageChanged = (
                oldThread.synergy_card_id !== formattedThread.synergy_card_id ||
                oldThread.workflow_slug !== formattedThread.workflow_slug ||
                oldThread.automation_slug !== formattedThread.automation_slug ||
                oldThread.internal_doc_slug !== formattedThread.internal_doc_slug
            );
        }

        // Update thread in ThreadManager cache
        if (existingIndex !== -1) {
            // Preserve messages array if not included in update
            if (!formattedThread.messages && ThreadManager.threads[existingIndex].messages) {
                formattedThread.messages = ThreadManager.threads[existingIndex].messages;
            }
            ThreadManager.threads[existingIndex] = formattedThread;
            console.log(`[ThreadCardRealtime] Updated thread in cache: ${formattedThread.id}`);
        } else {
            // Thread not in cache - add it
            ThreadManager.threads.unshift(formattedThread);
            console.log(`[ThreadCardRealtime] Added updated thread to cache: ${formattedThread.id}`);
        }

        // 🔧 FIX 1: Auto-refresh badges if linkage changed
        if (linkageChanged) {
            console.log('✨ [ThreadCardRealtime] Linkage changed - refreshing badge');
            this.refreshThreadBadge(formattedThread);
        }

        // Auto-refresh all thread info cards for this thread
        if (typeof ThreadManager.refreshAllThreadInfoCards === 'function') {
            ThreadManager.refreshAllThreadInfoCards(formattedThread.id);
            console.log(`[ThreadCardRealtime] Auto-refreshed cards for: ${formattedThread.id}`);
        }

        // Refresh thread history sidebar if open
        if (typeof ThreadManager.refreshThreadHistorySidebar === 'function') {
            ThreadManager.refreshThreadHistorySidebar();
        }

        // Handle agent assignment changes
        if (updatedThread.agent && typeof MultiAgent !== 'undefined') {
            const agentMatch = updatedThread.agent.match(/agent-(\d+)/);
            if (agentMatch) {
                MultiAgent.refreshAgentThreads(updatedThread.agent);
            }
        }

        // Handle new schema columns
        this._handleNewSchemaColumns(updatedThread);
    },

    /**
     * 🔧 FIX 1: Refresh linkage badges for a thread
     * Called when linkage fields change (synergy_card_id, workflow_slug, etc.)
     * Regenerates badge HTML using integration modules
     * 
     * @param {Object} thread - Thread object with updated linkage
     */
    refreshThreadBadge(thread) {
        console.log('[ThreadCardRealtime] Refreshing badges for thread:', thread.id);

        // Find all instances of this thread card in DOM (could be in multiple locations)
        const threadCards = document.querySelectorAll(`[data-thread-slug="${thread.id}"]`);

        if (threadCards.length === 0) {
            console.log('[ThreadCardRealtime] No thread cards found in DOM for:', thread.id);
            return;
        }

        threadCards.forEach(card => {
            const badgeContainer = card.querySelector('.linkage-badges-container');
            if (!badgeContainer) {
                console.log('[ThreadCardRealtime] No badge container found in card');
                return;
            }

            // Clear old badges
            badgeContainer.innerHTML = '';

            // Render new badges using integration modules
            const badgeConfig = {
                showUnlinkButton: true,
                compact: false
            };

            // Synergy badge
            if (thread.synergy_card_id && typeof window.SynergyThreadIntegration !== 'undefined') {
                try {
                    const badgeHTML = window.SynergyThreadIntegration.renderThreadBadge(thread, badgeConfig);
                    if (badgeHTML) {
                        badgeContainer.insertAdjacentHTML('beforeend', badgeHTML);
                        console.log('[ThreadCardRealtime] ✅ Rendered Synergy badge');
                    }
                } catch (error) {
                    console.error('[ThreadCardRealtime] Error rendering Synergy badge:', error);
                }
            }

            // Workflow badge
            if (thread.workflow_slug && typeof window.WorkflowThreadIntegration !== 'undefined') {
                try {
                    const badgeHTML = window.WorkflowThreadIntegration.renderThreadBadge(thread, badgeConfig);
                    if (badgeHTML) {
                        badgeContainer.insertAdjacentHTML('beforeend', badgeHTML);
                        console.log('[ThreadCardRealtime] ✅ Rendered Workflow badge');
                    }
                } catch (error) {
                    console.error('[ThreadCardRealtime] Error rendering Workflow badge:', error);
                }
            }

            // Automation badge
            if (thread.automation_slug && typeof window.AutomationThreadIntegration !== 'undefined') {
                try {
                    const badgeHTML = window.AutomationThreadIntegration.renderThreadBadge(thread, badgeConfig);
                    if (badgeHTML) {
                        badgeContainer.insertAdjacentHTML('beforeend', badgeHTML);
                        console.log('[ThreadCardRealtime] ✅ Rendered Automation badge');
                    }
                } catch (error) {
                    console.error('[ThreadCardRealtime] Error rendering Automation badge:', error);
                }
            }

            // Internal docs badge
            if (thread.internal_doc_slug && typeof window.InternalDocsThreadIntegration !== 'undefined') {
                try {
                    const badgeHTML = window.InternalDocsThreadIntegration.renderThreadBadge(thread, badgeConfig);
                    if (badgeHTML) {
                        badgeContainer.insertAdjacentHTML('beforeend', badgeHTML);
                        console.log('[ThreadCardRealtime] ✅ Rendered Internal Docs badge');
                    }
                } catch (error) {
                    console.error('[ThreadCardRealtime] Error rendering Internal Docs badge:', error);
                }
            }

            console.log('[ThreadCardRealtime] ✅ Badge refresh complete for:', thread.id);
        });
    },

    /**
     * Handle DELETE event - Thread removed
     * 
     * @param {Object} payload - Supabase DELETE payload
     * @param {Object} payload.old - Deleted thread record
     */
    handleThreadDelete(payload) {
        console.log('[ThreadCardRealtime] DELETE:', payload.old.thread_slug);

        const deletedThreadId = payload.old.thread_slug;

        // Check if ThreadManager exists
        if (typeof ThreadManager === 'undefined') {
            console.warn('[ThreadCardRealtime] ThreadManager not available');
            return;
        }

        // Remove thread from ThreadManager cache
        const existingIndex = ThreadManager.threads.findIndex(t => t.id === deletedThreadId);
        if (existingIndex !== -1) {
            ThreadManager.threads.splice(existingIndex, 1);
            console.log(`[ThreadCardRealtime] Removed thread from cache: ${deletedThreadId}`);
        }

        // Clear from agent columns if loaded (Dec 9, 2025 FIX)
        if (typeof MultiAgent !== 'undefined') {
            [1, 2, 3, 4, 5, 6, 7, 8].forEach(agentId => {
                const loadedThread = MultiAgent.loadedThreads?.[agentId];
                if (loadedThread && loadedThread.threadId === deletedThreadId) {
                    console.log(`[ThreadCardRealtime] Clearing deleted thread from agent ${agentId}`);
                    // Use AgentColumn.unloadThread to properly show empty state
                    if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.unloadThread === 'function') {
                        AgentColumn.unloadThread(agentId);
                    } else {
                        // Fallback: clear via MultiAgent
                        MultiAgent.clearAgentThread?.(agentId);
                    }
                }
            });
        }

        // Remove thread cards from all locations
        const locations = ['prime', 'agent-1', 'agent-2', 'agent-3', 'synergy'];
        locations.forEach(location => {
            const container = document.getElementById(`${location}-thread-info`);
            if (container && container.dataset.threadId === deletedThreadId) {
                container.remove();
                console.log(`[ThreadCardRealtime] Removed card from ${location}`);
            }
        });

        // Refresh thread history sidebar if open
        if (typeof ThreadManager.refreshThreadHistorySidebar === 'function') {
            ThreadManager.refreshThreadHistorySidebar();
        }

        // If this was the current thread, clear it
        if (ThreadManager.currentThreadId === deletedThreadId) {
            ThreadManager.currentThreadId = null;
            if (typeof ThreadManager.clearCurrentThread === 'function') {
                ThreadManager.clearCurrentThread();
            }
        }
    },

    /**
     * Handle new schema columns (thread_lock_user_id, automation_slug, automation_title)
     * @private
     */
    _handleNewSchemaColumns(thread) {
        // Handle thread_lock_user_id (device lock feature)
        if (thread.thread_lock_user_id !== null && typeof DeviceLockManager !== 'undefined') {
            // Update lock UI for this thread
            DeviceLockManager.updateLockUI(thread.thread_slug, thread.thread_lock_user_id);
        }

        // Handle automation_slug and automation_title (workflow automation)
        if (thread.automation_slug || thread.automation_title) {
            // Update workflow slug display
            const workflowSlugEl = document.getElementById(`workflow-slug-${thread.thread_slug}`);
            if (workflowSlugEl) {
                const textEl = document.getElementById(`workflow-slug-text-${thread.thread_slug}`);
                if (textEl) {
                    textEl.textContent = thread.automation_slug || thread.automation_title;
                }
                workflowSlugEl.style.display = 'inline-flex';
                console.log(`[ThreadCardRealtime] Updated workflow slug for ${thread.thread_slug}`);
            }
        }
    },

    /**
     * Format thread from Supabase schema to ThreadManager format
     * Handles column name mapping (snake_case → camelCase)
     * @private
     */
    _formatThread(dbThread) {
        return {
            id: dbThread.thread_slug,
            title: dbThread.title,
            agent: dbThread.agent,
            created: dbThread.created,
            updated: dbThread.updated,
            message_count: dbThread.message_count || 0,
            token_count: dbThread.token_count || 0,
            tags: dbThread.tags || [],
            synergy_card_id: dbThread.synergy_card_id,
            synergy_card_name: dbThread.synergy_card_name,
            synergy_card_desc: dbThread.synergy_card_desc,
            synergy_card_users: dbThread.synergy_card_users,
            synergy_card_updated: dbThread.synergy_card_updated,
            workflow_id: dbThread.workflow_id,
            workflow_name: dbThread.workflow_name,
            workflow_slug: dbThread.automation_slug || dbThread.workflow_slug, // NEW COLUMN
            thread_lock_user_id: dbThread.thread_lock_user_id, // NEW COLUMN
            automation_slug: dbThread.automation_slug, // NEW COLUMN
            automation_title: dbThread.automation_title, // NEW COLUMN
            archived: dbThread.archived || false,
            messages: [] // Messages loaded separately
        };
    },

    /**
     * Cleanup - Unsubscribe from all channels
     * Call this when navigating away or before re-initializing
     * 
     * @returns {Promise<void>}
     */
    async cleanup() {
        if (!this.isInitialized) {
            console.log('[ThreadCardRealtime] Not initialized - nothing to cleanup');
            return;
        }

        console.log('[ThreadCardRealtime] Cleaning up subscriptions...');

        try {
            const supabaseClient = window.supabaseClient || window.SUPABASE_CLIENT;
            if (this.channel && supabaseClient) {
                await supabaseClient.removeChannel(this.channel);
                this.channel = null;
            }

            // Clear all debounce timers
            Object.keys(this.updateDebounceTimers).forEach(threadId => {
                clearTimeout(this.updateDebounceTimers[threadId]);
            });
            this.updateDebounceTimers = {};

            this.isInitialized = false;
            console.log('[ThreadCardRealtime] Cleanup complete');

        } catch (error) {
            console.error('[ThreadCardRealtime] Cleanup error:', error);
        }
    },

    /**
     * Manual refresh for a specific thread
     * Useful for forcing immediate update without waiting for Realtime
     * 
     * @param {string} threadId - Thread slug to refresh
     */
    async manualRefresh(threadId) {
        try {
            console.log(`[ThreadCardRealtime] Manual refresh for ${threadId}`);

            // Use Flask API instead of direct Supabase (sessions schema not exposed in REST API)
            const apiUrl = window.API_BASE_URL || 'http://localhost:5001';
            const userId = (window.UserAuth?.user?.id || window.UserAuth?.user?.user_id) || 1;
            const response = await fetch(`${apiUrl}/api/threads/get?thread_slug=${threadId}&user_id=${userId}`);

            if (!response.ok) {
                console.error('[ThreadCardRealtime] Manual refresh error:', response.statusText);
                return;
            }

            const result = await response.json();
            if (result.success && result.thread) {
                this._applyThreadUpdate(result.thread);
            }

        } catch (error) {
            console.error('[ThreadCardRealtime] Manual refresh exception:', error);
        }
    }
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        ThreadCardRealtime.initialize();
    });
} else {
    // DOM already loaded
    ThreadCardRealtime.initialize();
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    ThreadCardRealtime.cleanup();
});
