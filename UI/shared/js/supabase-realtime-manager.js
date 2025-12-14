/**
 * FILE: UI/shared/js/supabase-realtime-manager.js
 * PURPOSE: Unified Supabase Real-Time Manager - ONE place for ALL real-time subscriptions
 * 
 * CONSOLIDATES:
 * - Heartbeat monitoring (server health)
 * - Workspace sync (cross-tab/device workspace state)
 * - User credentials (OAuth updates)
 * - Synergy sessions (kanban board live updates)
 * - Thread cards (chat thread changes)
 * - Future: Any new real-time features
 * 
 * REPLACES:
 * - supabase-heartbeat-listener.js (heartbeat only)
 * - synergy-realtime.js (dead Socket.IO code)
 * - synergy-realtime-enhanced.js (dead Socket.IO code)
 * - Individual postgres_changes subscriptions scattered across codebase
 * 
 * ARCHITECTURE:
 * - Single Supabase channel per table/feature
 * - Event-driven callbacks (register handlers for specific events)
 * - Auto-reconnect on disconnect
 * - Centralized error handling and logging
 * - Lazy subscription (only subscribe when feature is used)
 * 
 * USAGE:
 * ```javascript
 * // Subscribe to workspace updates
 * SupabaseRealtimeManager.subscribe('workspace', {
 *     table: 'user_command_center',
 *     schema: 'sessions',
 *     filter: `user_id=eq.${userId}`,
 *     onUpdate: (payload) => console.log('Workspace updated:', payload)
 * });
 * 
 * // Subscribe to Synergy sessions
 * SupabaseRealtimeManager.subscribe('synergy', {
 *     table: 'synergy_sessions',
 *     schema: 'synergy_sessions',
 *     filter: `user_id=eq.${userId}`,
 *     onInsert: (payload) => console.log('Session created:', payload),
 *     onUpdate: (payload) => console.log('Session updated:', payload),
 *     onDelete: (payload) => console.log('Session deleted:', payload)
 * });
 * 
 * // Unsubscribe
 * SupabaseRealtimeManager.unsubscribe('workspace');
 * ```
 * 
 * CREATED: December 14, 2025
 */

window.SupabaseRealtimeManager = (function () {
    'use strict';

    // Active subscriptions registry
    const subscriptions = {};

    // Supabase client reference
    let supabaseClient = null;

    // Connection state
    let isConnected = false;

    /**
     * Initialize the real-time manager
     * Should be called after SupabaseConnectionManager is ready
     */
    async function initialize() {
        console.log('🔄 [RealtimeManager] Initializing...');

        // Get Supabase client
        if (typeof SupabaseConnectionManager === 'undefined') {
            console.error('❌ [RealtimeManager] SupabaseConnectionManager not available');
            return false;
        }

        supabaseClient = await SupabaseConnectionManager.getClient();
        if (!supabaseClient) {
            console.error('❌ [RealtimeManager] Failed to get Supabase client');
            return false;
        }

        console.log('✅ [RealtimeManager] Initialized');
        isConnected = true;

        // Subscribe to built-in channels
        subscribeToHeartbeat();

        return true;
    }

    /**
     * Subscribe to heartbeat broadcast (server health monitoring)
     * This is ALWAYS active - monitors server availability
     */
    function subscribeToHeartbeat() {
        console.log('💓 [RealtimeManager] Subscribing to heartbeat...');

        const channel = supabaseClient
            .channel('heartbeat-channel')
            .on('broadcast', { event: 'heartbeat' }, (payload) => {
                // Heartbeat received - server is alive
                const timestamp = payload.payload?.timestamp || Date.now();
                isConnected = true;

                // Emit event for status indicator
                window.dispatchEvent(new CustomEvent('supabase:heartbeat', {
                    detail: { timestamp, connected: true }
                }));
            })
            .subscribe((status) => {
                if (status === 'SUBSCRIBED') {
                    console.log('✅ [RealtimeManager] Heartbeat subscribed');
                } else if (status === 'CHANNEL_ERROR') {
                    console.error('❌ [RealtimeManager] Heartbeat channel error');
                    isConnected = false;
                } else if (status === 'CLOSED') {
                    console.warn('⚠️ [RealtimeManager] Heartbeat channel closed');
                    isConnected = false;
                }
            });

        subscriptions['heartbeat'] = {
            channel,
            type: 'broadcast',
            active: true
        };

        // Staleness check - detect when heartbeat stops
        setInterval(() => {
            // If last heartbeat was more than 90 seconds ago, mark as disconnected
            // (Heartbeat broadcasts every 60 seconds from server)
            const lastHeartbeatEvent = window.lastHeartbeatTimestamp || 0;
            const now = Date.now();
            const stale = (now - lastHeartbeatEvent) > 90000;

            if (stale && isConnected) {
                console.warn('⚠️ [RealtimeManager] Heartbeat stale - server may be down');
                isConnected = false;
                window.dispatchEvent(new CustomEvent('supabase:heartbeat', {
                    detail: { timestamp: lastHeartbeatEvent, connected: false }
                }));
            }
        }, 30000); // Check every 30 seconds

        // Store last heartbeat timestamp globally
        window.addEventListener('supabase:heartbeat', (e) => {
            window.lastHeartbeatTimestamp = e.detail.timestamp;
        });
    }

    /**
     * Subscribe to database changes (postgres_changes)
     * 
     * @param {string} name - Unique subscription name (e.g., 'workspace', 'synergy', 'credentials')
     * @param {object} options - Subscription options
     * @param {string} options.table - Table name
     * @param {string} options.schema - Schema name (default: 'public')
     * @param {string} options.filter - PostgreSQL filter (e.g., 'user_id=eq.123')
     * @param {string} options.event - Event type ('INSERT', 'UPDATE', 'DELETE', '*' for all)
     * @param {function} options.onInsert - Callback for INSERT events
     * @param {function} options.onUpdate - Callback for UPDATE events
     * @param {function} options.onDelete - Callback for DELETE events
     * @param {function} options.onChange - Callback for any change (receives event type)
     */
    function subscribe(name, options) {
        // Check if already subscribed
        if (subscriptions[name]) {
            console.warn(`⚠️ [RealtimeManager] Already subscribed to '${name}'`);
            return subscriptions[name];
        }

        console.log(`📡 [RealtimeManager] Subscribing to '${name}'...`, options);

        // Build channel name (unique per table)
        const channelName = `${options.schema || 'public'}:${options.table}`;

        // Create channel
        let channel = supabaseClient.channel(channelName);

        // Add postgres_changes listener
        const listenerConfig = {
            event: options.event || '*',
            schema: options.schema || 'public',
            table: options.table
        };

        // Add filter if provided
        if (options.filter) {
            listenerConfig.filter = options.filter;
        }

        channel = channel.on('postgres_changes', listenerConfig, (payload) => {
            console.log(`🔔 [RealtimeManager:${name}] Event:`, payload);

            // Call event-specific callbacks
            const eventType = payload.eventType;

            if (eventType === 'INSERT' && options.onInsert) {
                options.onInsert(payload);
            } else if (eventType === 'UPDATE' && options.onUpdate) {
                options.onUpdate(payload);
            } else if (eventType === 'DELETE' && options.onDelete) {
                options.onDelete(payload);
            }

            // Call generic onChange callback
            if (options.onChange) {
                options.onChange(eventType, payload);
            }

            // Emit global event for this subscription
            window.dispatchEvent(new CustomEvent(`supabase:${name}`, {
                detail: { eventType, payload }
            }));
        });

        // Subscribe to channel
        channel.subscribe((status) => {
            if (status === 'SUBSCRIBED') {
                console.log(`✅ [RealtimeManager:${name}] Subscribed`);
                subscriptions[name].active = true;
            } else if (status === 'CHANNEL_ERROR') {
                console.error(`❌ [RealtimeManager:${name}] Channel error`);
                subscriptions[name].active = false;
            } else if (status === 'CLOSED') {
                console.log(`🔌 [RealtimeManager:${name}] Channel closed`);
                subscriptions[name].active = false;
            }
        });

        // Store subscription
        subscriptions[name] = {
            channel,
            type: 'postgres_changes',
            options,
            active: false
        };

        return subscriptions[name];
    }

    /**
     * Unsubscribe from a channel
     */
    async function unsubscribe(name) {
        const subscription = subscriptions[name];
        if (!subscription) {
            console.warn(`⚠️ [RealtimeManager] No subscription found: '${name}'`);
            return;
        }

        console.log(`🔌 [RealtimeManager] Unsubscribing from '${name}'...`);

        // Unsubscribe from channel
        await supabaseClient.removeChannel(subscription.channel);

        // Remove from registry
        delete subscriptions[name];

        console.log(`✅ [RealtimeManager] Unsubscribed from '${name}'`);
    }

    /**
     * Get subscription status
     */
    function getStatus(name) {
        if (name) {
            return subscriptions[name] || null;
        }

        // Return all subscriptions
        return {
            connected: isConnected,
            subscriptions: Object.keys(subscriptions).map(key => ({
                name: key,
                type: subscriptions[key].type,
                active: subscriptions[key].active
            }))
        };
    }

    /**
     * Subscribe to workspace changes (cross-tab/device sync)
     * Helper method for WorkspaceManager
     */
    function subscribeToWorkspace(userId, onUpdate) {
        return subscribe('workspace', {
            table: 'user_command_center',
            schema: 'sessions',
            filter: `user_id=eq.${userId}`,
            event: 'UPDATE',
            onUpdate: (payload) => {
                console.log('📥 [Workspace] Remote update:', payload);
                if (onUpdate) {
                    onUpdate(payload.new.workspace_data);
                }
            }
        });
    }

    /**
     * Subscribe to Synergy session changes (kanban board)
     * Helper method for Synergy dashboard
     */
    function subscribeToSynergy(userId, callbacks) {
        return subscribe('synergy', {
            table: 'synergy_sessions',
            schema: 'synergy_sessions',
            filter: `user_id=eq.${userId}`,
            onInsert: callbacks.onSessionCreated,
            onUpdate: callbacks.onSessionUpdated,
            onDelete: callbacks.onSessionDeleted
        });
    }

    /**
     * Subscribe to user credential changes (OAuth updates)
     * Helper method for credential manager
     */
    function subscribeToCredentials(userId, onUpdate) {
        return subscribe('credentials', {
            table: 'user_platform_credentials',
            schema: 'ai_infrastructure',
            filter: `user_id=eq.${userId}`,
            event: 'UPDATE',
            onUpdate: (payload) => {
                console.log('🔑 [Credentials] Remote update:', payload);
                if (onUpdate) {
                    onUpdate(payload.new);
                }
            }
        });
    }

    // Public API
    return {
        initialize,
        subscribe,
        unsubscribe,
        getStatus,

        // Helper methods
        subscribeToWorkspace,
        subscribeToSynergy,
        subscribeToCredentials,

        // Utility
        isConnected: () => isConnected
    };
})();

// Auto-initialize when SupabaseConnectionManager is ready
if (typeof SupabaseConnectionManager !== 'undefined') {
    // Wait for DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            SupabaseRealtimeManager.initialize();
        });
    } else {
        SupabaseRealtimeManager.initialize();
    }
}

console.log('✅ SupabaseRealtimeManager loaded');
