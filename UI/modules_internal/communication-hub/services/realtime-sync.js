/**
 * Real-Time Synchronization Service
 * Manages Supabase Realtime subscriptions for multi-device synchronization
 * 
 * Features:
 * - Subscribe to database changes (sessions.threads, sessions.messages)
 * - Handle INSERT/UPDATE/DELETE events
 * - Broadcast changes to UI components
 * - Manage connection lifecycle (connect/disconnect/reconnect)
 * - Handle offline/online transitions
 * - Prevent duplicate subscriptions
 */

class RealtimeSyncService {
    constructor() {
        this.supabase = null;
        this.subscriptions = new Map(); // channelName -> subscription
        this.listeners = new Map(); // eventType -> Set of callbacks
        this.isConnected = false;
        this.deviceId = this.generateDeviceId();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
    }

    /**
     * Initialize the service with Supabase client
     * @param {object} supabaseClient - Supabase client instance
     */
    initialize(supabaseClient) {
        this.supabase = supabaseClient;
        this.setupConnectionMonitoring();
        console.log('[RealtimeSync] Service initialized with device ID:', this.deviceId);
    }

    /**
     * Generate unique device ID for this session
     * @returns {string} Unique device identifier
     */
    generateDeviceId() {
        const stored = sessionStorage.getItem('deviceId');
        if (stored) return stored;

        const deviceId = `device-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        sessionStorage.setItem('deviceId', deviceId);
        return deviceId;
    }

    /**
     * Subscribe to messages for a specific thread
     * @param {number} threadId - Thread ID to subscribe to
     * @param {function} onMessage - Callback for new messages
     * @returns {string} Channel name for this subscription
     */
    subscribeToThreadMessages(threadId, onMessage) {
        const channelName = `thread-${threadId}-messages`;

        // Prevent duplicate subscriptions
        if (this.subscriptions.has(channelName)) {
            console.log(`[RealtimeSync] Already subscribed to ${channelName}`);
            return channelName;
        }

        console.log(`[RealtimeSync] Subscribing to messages for thread ${threadId}`);

        const subscription = this.supabase
            .channel(channelName)
            .on(
                'postgres_changes',
                {
                    event: 'INSERT',
                    schema: 'sessions',
                    table: 'messages',
                    filter: `thread_id=eq.${threadId}`
                },
                (payload) => {
                    console.log('[RealtimeSync] New message received:', payload.new);
                    onMessage(payload.new);
                    this.emitEvent('message:new', { threadId, message: payload.new });
                }
            )
            .on(
                'postgres_changes',
                {
                    event: 'UPDATE',
                    schema: 'sessions',
                    table: 'messages',
                    filter: `thread_id=eq.${threadId}`
                },
                (payload) => {
                    console.log('[RealtimeSync] Message updated:', payload.new);
                    this.emitEvent('message:update', { threadId, message: payload.new, old: payload.old });
                }
            )
            .on(
                'postgres_changes',
                {
                    event: 'DELETE',
                    schema: 'sessions',
                    table: 'messages',
                    filter: `thread_id=eq.${threadId}`
                },
                (payload) => {
                    console.log('[RealtimeSync] Message deleted:', payload.old);
                    this.emitEvent('message:delete', { threadId, message: payload.old });
                }
            )
            .subscribe((status) => {
                console.log(`[RealtimeSync] Subscription status for ${channelName}:`, status);
                if (status === 'SUBSCRIBED') {
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    this.emitEvent('connection:established', { channelName });
                } else if (status === 'CLOSED') {
                    this.handleDisconnection(channelName);
                }
            });

        this.subscriptions.set(channelName, subscription);
        return channelName;
    }

    /**
     * Subscribe to thread list changes (new threads, updates, deletions)
     * @param {number} userId - User ID to filter threads
     * @param {function} onThreadChange - Callback for thread changes
     * @returns {string} Channel name for this subscription
     */
    subscribeToThreadList(userId, onThreadChange) {
        const channelName = `user-${userId}-threads`;

        if (this.subscriptions.has(channelName)) {
            console.log(`[RealtimeSync] Already subscribed to ${channelName}`);
            return channelName;
        }

        console.log(`[RealtimeSync] Subscribing to thread list for user ${userId}`);

        const subscription = this.supabase
            .channel(channelName)
            .on(
                'postgres_changes',
                {
                    event: 'INSERT',
                    schema: 'sessions',
                    table: 'threads',
                    filter: `user_id=eq.${userId}`
                },
                (payload) => {
                    console.log('[RealtimeSync] New thread created:', payload.new);
                    onThreadChange({ type: 'INSERT', thread: payload.new });
                    this.emitEvent('thread:new', { thread: payload.new });
                }
            )
            .on(
                'postgres_changes',
                {
                    event: 'UPDATE',
                    schema: 'sessions',
                    table: 'threads',
                    filter: `user_id=eq.${userId}`
                },
                (payload) => {
                    console.log('[RealtimeSync] Thread updated:', payload.new);
                    onThreadChange({ type: 'UPDATE', thread: payload.new, old: payload.old });
                    this.emitEvent('thread:update', { thread: payload.new, old: payload.old });
                }
            )
            .on(
                'postgres_changes',
                {
                    event: 'DELETE',
                    schema: 'sessions',
                    table: 'threads',
                    filter: `user_id=eq.${userId}`
                },
                (payload) => {
                    console.log('[RealtimeSync] Thread deleted:', payload.old);
                    onThreadChange({ type: 'DELETE', thread: payload.old });
                    this.emitEvent('thread:delete', { thread: payload.old });
                }
            )
            .subscribe((status) => {
                console.log(`[RealtimeSync] Subscription status for ${channelName}:`, status);
                if (status === 'SUBSCRIBED') {
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                }
            });

        this.subscriptions.set(channelName, subscription);
        return channelName;
    }

    /**
     * Unsubscribe from a specific channel
     * @param {string} channelName - Channel to unsubscribe from
     */
    unsubscribe(channelName) {
        const subscription = this.subscriptions.get(channelName);
        if (!subscription) {
            console.warn(`[RealtimeSync] No subscription found for ${channelName}`);
            return;
        }

        console.log(`[RealtimeSync] Unsubscribing from ${channelName}`);
        subscription.unsubscribe();
        this.subscriptions.delete(channelName);
    }

    /**
     * Unsubscribe from all channels
     */
    unsubscribeAll() {
        console.log('[RealtimeSync] Unsubscribing from all channels');
        for (const [channelName, subscription] of this.subscriptions) {
            subscription.unsubscribe();
        }
        this.subscriptions.clear();
        this.isConnected = false;
    }

    /**
     * Register event listener for custom events
     * @param {string} eventType - Event type to listen for
     * @param {function} callback - Callback function
     */
    addEventListener(eventType, callback) {
        if (!this.listeners.has(eventType)) {
            this.listeners.set(eventType, new Set());
        }
        this.listeners.get(eventType).add(callback);
    }

    /**
     * Remove event listener
     * @param {string} eventType - Event type
     * @param {function} callback - Callback to remove
     */
    removeEventListener(eventType, callback) {
        const listeners = this.listeners.get(eventType);
        if (listeners) {
            listeners.delete(callback);
        }
    }

    /**
     * Emit custom event to all registered listeners
     * @param {string} eventType - Event type
     * @param {object} data - Event data
     */
    emitEvent(eventType, data) {
        const listeners = this.listeners.get(eventType);
        if (!listeners) return;

        for (const callback of listeners) {
            try {
                callback(data);
            } catch (error) {
                console.error(`[RealtimeSync] Error in event listener for ${eventType}:`, error);
            }
        }
    }

    /**
     * Setup connection monitoring for online/offline transitions
     */
    setupConnectionMonitoring() {
        window.addEventListener('online', () => {
            console.log('[RealtimeSync] Network online, attempting to reconnect...');
            this.reconnectAll();
        });

        window.addEventListener('offline', () => {
            console.log('[RealtimeSync] Network offline');
            this.isConnected = false;
            this.emitEvent('connection:offline', {});
        });
    }

    /**
     * Handle disconnection and attempt reconnection
     * @param {string} channelName - Channel that disconnected
     */
    handleDisconnection(channelName) {
        console.warn(`[RealtimeSync] Disconnected from ${channelName}`);
        this.isConnected = false;
        this.emitEvent('connection:lost', { channelName });

        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff
            console.log(`[RealtimeSync] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

            setTimeout(() => {
                this.reconnectChannel(channelName);
            }, delay);
        } else {
            console.error(`[RealtimeSync] Max reconnect attempts reached for ${channelName}`);
            this.emitEvent('connection:failed', { channelName });
        }
    }

    /**
     * Reconnect to a specific channel
     * @param {string} channelName - Channel to reconnect
     */
    reconnectChannel(channelName) {
        // Implementation depends on stored subscription metadata
        // For now, emit event so UI can re-subscribe
        console.log(`[RealtimeSync] Manual reconnect needed for ${channelName}`);
        this.emitEvent('connection:reconnect-needed', { channelName });
    }

    /**
     * Reconnect all subscriptions
     */
    reconnectAll() {
        for (const channelName of this.subscriptions.keys()) {
            this.reconnectChannel(channelName);
        }
    }

    /**
     * Get current connection status
     * @returns {boolean} True if connected
     */
    isConnectionActive() {
        return this.isConnected;
    }

    /**
     * Get device ID for this session
     * @returns {string} Device ID
     */
    getDeviceId() {
        return this.deviceId;
    }

    /**
     * Get all active subscriptions
     * @returns {Array<string>} List of channel names
     */
    getActiveSubscriptions() {
        return Array.from(this.subscriptions.keys());
    }
}

// Export singleton instance
export const realtimeSyncService = new RealtimeSyncService();
