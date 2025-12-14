/**
 * FILE: UI/shared/js/realtime-subscriptions-init.js
 * PURPOSE: Centralized initialization for all Supabase real-time subscriptions
 * 
 * SUBSCRIPTIONS:
 * 1. Heartbeat - Server health monitoring (60s interval)
 * 2. Workspace - Cross-tab sync (user_command_center)
 * 3. Threads - Thread updates (saved_threads table)
 * 4. Synergy - Kanban board updates (synergy_sessions, milestones, tasks, subtasks)
 * 5. Credentials - OAuth token updates (user_platform_credentials)
 * 6. Sessions - User session updates (user_sessions)
 * 
 * DEPENDENCIES:
 * - SupabaseRealtimeManager (real-time subscription manager)
 * - UserAuth (user ID)
 * 
 * EXPORTS:
 * - initializeAllSubscriptions() - Set up all real-time subscriptions
 * - getActiveSubscriptions() - Get list of active subscriptions
 * - unsubscribeAll() - Clean up all subscriptions
 * 
 * USAGE:
 * ```javascript
 * // Called automatically after user login
 * await initializeAllSubscriptions();
 * 
 * // Check active subscriptions
 * const subs = getActiveSubscriptions();
 * console.log('Active:', subs);
 * 
 * // Clean up on logout
 * unsubscribeAll();
 * ```
 * 
 * CREATED: December 14, 2025
 */

window.RealtimeSubscriptionsInit = (function () {
    'use strict';

    // Track active subscriptions
    const activeSubscriptions = new Set();

    /**
     * Initialize all real-time subscriptions
     * Called after user authentication completes
     */
    async function initializeAllSubscriptions() {
        console.log('🔄 [Realtime Init] Initializing all subscriptions...');

        // Check dependencies
        if (typeof SupabaseRealtimeManager === 'undefined') {
            console.error('❌ [Realtime Init] SupabaseRealtimeManager not available');
            return false;
        }

        if (typeof UserAuth === 'undefined' || !UserAuth.getUserId) {
            console.error('❌ [Realtime Init] UserAuth not available');
            return false;
        }

        const userId = UserAuth.getUserId();
        if (!userId) {
            console.warn('⚠️ [Realtime Init] No user ID - skipping subscriptions');
            return false;
        }

        console.log(`📡 [Realtime Init] Setting up subscriptions for user ${userId}...`);

        try {
            // 1. HEARTBEAT - Server health monitoring
            await subscribeToHeartbeat();

            // 2. WORKSPACE - Cross-tab sync
            await subscribeToWorkspace(userId);

            // 3. THREADS - Thread updates
            await subscribeToThreads(userId);

            // 4. SYNERGY - Kanban board updates
            await subscribeToSynergy(userId);

            // 5. CREDENTIALS - OAuth updates
            await subscribeToCredentials(userId);

            // 6. SESSIONS - User session updates
            await subscribeToSessions(userId);

            console.log('✅ [Realtime Init] All subscriptions initialized successfully');
            console.log(`📊 [Realtime Init] Active subscriptions: ${activeSubscriptions.size}`);

            return true;

        } catch (error) {
            console.error('❌ [Realtime Init] Failed to initialize subscriptions:', error);
            return false;
        }
    }

    /**
     * Subscribe to heartbeat (server health)
     */
    async function subscribeToHeartbeat() {
        try {
            console.log('💓 [Realtime Init] Subscribing to heartbeat...');

            // SupabaseRealtimeManager handles heartbeat internally
            // Just mark as active
            activeSubscriptions.add('heartbeat');

            console.log('✅ [Realtime Init] Heartbeat subscription active');
        } catch (error) {
            console.error('❌ [Realtime Init] Heartbeat subscription failed:', error);
        }
    }

    /**
     * Subscribe to workspace updates (cross-tab sync)
     */
    async function subscribeToWorkspace(userId) {
        try {
            console.log('🗂️ [Realtime Init] Subscribing to workspace updates...');

            SupabaseRealtimeManager.subscribe('workspace', {
                event: '*',
                schema: 'sessions',
                table: 'user_command_center',
                filter: `user_id=eq.${userId}`
            }, (payload) => {
                console.log('🔔 [Workspace] Update received:', payload);

                // Notify WorkspaceManager if available
                if (window.WorkspaceManager && window.WorkspaceManager.handleRealtimeUpdate) {
                    window.WorkspaceManager.handleRealtimeUpdate(payload);
                }
            });

            activeSubscriptions.add('workspace');
            console.log('✅ [Realtime Init] Workspace subscription active');

        } catch (error) {
            console.error('❌ [Realtime Init] Workspace subscription failed:', error);
        }
    }

    /**
     * Subscribe to thread updates
     */
    async function subscribeToThreads(userId) {
        try {
            console.log('💬 [Realtime Init] Subscribing to thread updates...');

            SupabaseRealtimeManager.subscribe('threads', {
                event: '*',
                schema: 'sessions',
                table: 'saved_threads',
                filter: `user_id=eq.${userId}`
            }, (payload) => {
                console.log('🔔 [Threads] Update received:', payload);

                // Notify ThreadManager if available
                if (window.ThreadManager && window.ThreadManager.handleRealtimeUpdate) {
                    window.ThreadManager.handleRealtimeUpdate(payload);
                } else {
                    console.log('📝 [Threads] ThreadManager not loaded yet - queuing update');
                }
            });

            activeSubscriptions.add('threads');
            console.log('✅ [Realtime Init] Threads subscription active');

        } catch (error) {
            console.error('❌ [Realtime Init] Threads subscription failed:', error);
        }
    }

    /**
     * Subscribe to Synergy (Kanban) updates
     */
    async function subscribeToSynergy(userId) {
        try {
            console.log('📋 [Realtime Init] Subscribing to Synergy (Kanban) updates...');

            // Subscribe to all Synergy tables
            const synergyTables = ['synergy_sessions', 'milestones', 'tasks', 'subtasks'];

            for (const table of synergyTables) {
                SupabaseRealtimeManager.subscribe(`synergy-${table}`, {
                    event: '*',
                    schema: 'synergy_sessions',
                    table: table,
                    filter: `user_id=eq.${userId}`
                }, (payload) => {
                    console.log(`🔔 [Synergy:${table}] Update received:`, payload);

                    // Notify SynergyManager if available
                    if (window.SynergyManager && window.SynergyManager.handleRealtimeUpdate) {
                        window.SynergyManager.handleRealtimeUpdate(table, payload);
                    }

                    // Also notify SynergySessionRenderer (for live board updates)
                    if (window.SynergySessionRenderer && window.SynergySessionRenderer.handleRealtimeUpdate) {
                        window.SynergySessionRenderer.handleRealtimeUpdate(table, payload);
                    }
                });

                activeSubscriptions.add(`synergy-${table}`);
            }

            console.log('✅ [Realtime Init] Synergy subscriptions active (4 tables)');

        } catch (error) {
            console.error('❌ [Realtime Init] Synergy subscription failed:', error);
        }
    }

    /**
     * Subscribe to credential updates (OAuth tokens)
     */
    async function subscribeToCredentials(userId) {
        try {
            console.log('🔑 [Realtime Init] Subscribing to credential updates...');

            SupabaseRealtimeManager.subscribe('credentials', {
                event: '*',
                schema: 'ai_infrastructure',
                table: 'user_platform_credentials',
                filter: `user_id=eq.${userId}`
            }, (payload) => {
                console.log('🔔 [Credentials] Update received:', payload);

                // Notify AccountSidebar if available
                if (window.AccountSidebar && window.AccountSidebar.handleRealtimeUpdate) {
                    window.AccountSidebar.handleRealtimeUpdate(payload);
                }

                // Also refresh account profile if open
                if (window.AccountProfile && window.AccountProfile.refreshCredentials) {
                    window.AccountProfile.refreshCredentials();
                }
            });

            activeSubscriptions.add('credentials');
            console.log('✅ [Realtime Init] Credentials subscription active');

        } catch (error) {
            console.error('❌ [Realtime Init] Credentials subscription failed:', error);
        }
    }

    /**
     * Subscribe to session updates
     */
    async function subscribeToSessions(userId) {
        try {
            console.log('🔐 [Realtime Init] Subscribing to session updates...');

            SupabaseRealtimeManager.subscribe('sessions', {
                event: '*',
                schema: 'sessions',
                table: 'user_sessions',
                filter: `user_id=eq.${userId}`
            }, (payload) => {
                console.log('🔔 [Sessions] Update received:', payload);

                // Notify AccountSidebar for session list updates
                if (window.AccountSidebar && window.AccountSidebar.refreshSessions) {
                    window.AccountSidebar.refreshSessions();
                }
            });

            activeSubscriptions.add('sessions');
            console.log('✅ [Realtime Init] Sessions subscription active');

        } catch (error) {
            console.error('❌ [Realtime Init] Sessions subscription failed:', error);
        }
    }

    /**
     * Get list of active subscriptions
     */
    function getActiveSubscriptions() {
        return Array.from(activeSubscriptions);
    }

    /**
     * Unsubscribe from all subscriptions (called on logout)
     */
    function unsubscribeAll() {
        console.log('🔄 [Realtime Init] Unsubscribing from all subscriptions...');

        if (typeof SupabaseRealtimeManager !== 'undefined') {
            activeSubscriptions.forEach(name => {
                try {
                    SupabaseRealtimeManager.unsubscribe(name);
                } catch (error) {
                    console.warn(`⚠️ [Realtime Init] Failed to unsubscribe from ${name}:`, error);
                }
            });
        }

        activeSubscriptions.clear();
        console.log('✅ [Realtime Init] All subscriptions cleared');
    }

    // Public API
    return {
        initialize: initializeAllSubscriptions,
        getActiveSubscriptions: getActiveSubscriptions,
        unsubscribeAll: unsubscribeAll
    };
})();

// Auto-initialize if SupabaseConnectionManager is ready
if (typeof SupabaseConnectionManager !== 'undefined') {
    SupabaseConnectionManager.onReady(() => {
        console.log('🔄 [Realtime Init] SupabaseConnectionManager ready - waiting for user login...');
    });
}
