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
     * Subscribes to INSERT, UPDATE, DELETE events
     * 
     * @returns {Promise<void>}
     */
    async initialize() {
        if (this.isInitialized) {
            console.log('[ThreadCardRealtime] Already initialized');
            return;
        }

        // ✅ Wait for Supabase client to be initialized (max 5 seconds)
        let attempts = 0;
        const maxAttempts = 50; // 50 x 100ms = 5 seconds

        while (attempts < maxAttempts) {
            const supabaseClient = window.supabaseClient || window.SUPABASE_CLIENT;
            if (supabaseClient) {
                console.log('[ThreadCardRealtime] Supabase client found, initializing...');
                break;
            }

            if (attempts === 0) {
                console.log('[ThreadCardRealtime] Waiting for Supabase client initialization...');
            }

            await new Promise(resolve => setTimeout(resolve, 100));
            attempts++;
        }

        // Check if Supabase client exists (try both lowercase and uppercase)
        const supabaseClient = window.supabaseClient || window.SUPABASE_CLIENT;
        if (!supabaseClient) {
            console.warn('[ThreadCardRealtime] Supabase client not available after 5s - skipping Realtime');
            console.warn('   Real-time thread updates will not work.');
            console.warn('   Threads will refresh on manual page reload only.');
            return;
        }

        console.log('[ThreadCardRealtime] Initializing Realtime subscriptions...');

        try {
            // Create channel for threads table
            this.channel = supabaseClient
                .channel('threads-realtime-channel')
                .on('postgres_changes', {
                    event: 'INSERT',
                    schema: 'sessions',
                    table: 'threads'
                }, (payload) => this.handleThreadInsert(payload))
                .on('postgres_changes', {
                    event: 'UPDATE',
                    schema: 'sessions',
                    table: 'threads'
                }, (payload) => this.handleThreadUpdate(payload))
                .on('postgres_changes', {
                    event: 'DELETE',
                    schema: 'sessions',
                    table: 'threads'
                }, (payload) => this.handleThreadDelete(payload))
                .subscribe((status) => {
                    if (status === 'SUBSCRIBED') {
                        console.log('[ThreadCardRealtime] Successfully subscribed to threads table');
                        this.isInitialized = true;
                    } else if (status === 'CHANNEL_ERROR') {
                        console.error('[ThreadCardRealtime] Channel error:', status);
                    } else if (status === 'TIMED_OUT') {
                        console.error('[ThreadCardRealtime] Subscription timed out');
                    } else {
                        console.log('[ThreadCardRealtime] Subscription status:', status);
                    }
                });

            console.log('[ThreadCardRealtime] Realtime subscriptions initialized');

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

        // Update thread in ThreadManager cache
        const existingIndex = ThreadManager.threads.findIndex(t => t.id === formattedThread.id);
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
            synergy_card_title: dbThread.synergy_card_title,
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
        const supabaseClient = window.supabaseClient || window.SUPABASE_CLIENT;
        if (!supabaseClient) {
            console.warn('[ThreadCardRealtime] Supabase client not available');
            return;
        }

        try {
            console.log(`[ThreadCardRealtime] Manual refresh for ${threadId}`);

            const { data, error } = await supabaseClient
                .from('threads')
                .select('*')
                .eq('thread_slug', threadId)
                .single();

            if (error) {
                console.error('[ThreadCardRealtime] Manual refresh error:', error);
                return;
            }

            if (data) {
                this._applyThreadUpdate(data);
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
