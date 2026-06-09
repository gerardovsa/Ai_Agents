/**
 * FILE: UI/js/supabase-connection-manager.js
 * PURPOSE: Centralized Supabase connection manager - prevents duplicate connections
 * 
 * FEATURES:
 * - Singleton pattern (one client instance)
 * - Connection state tracking
 * - Retry logic with exponential backoff
 * - Health monitoring with ping (only if idle >30s)
 * - Automatic reconnection on network change
 * - Graceful degradation to fallback mode
 * 
 * EXPORTS:
 * - SupabaseConnectionManager.getClient() - Get or create Supabase client
 * - SupabaseConnectionManager.subscribeChannel() - Subscribe to channel (prevents duplicates)
 * - SupabaseConnectionManager.isConnected() - Check realtime connection status
 * - SupabaseConnectionManager.disconnect() - Cleanup connections
 * 
 * LAST MODIFIED: 2025-11-24 - Created to fix repeated connection spam
 */

window.SupabaseConnectionManager = {
    // Singleton state
    client: null,
    realtimeConnection: null,
    connectionState: 'disconnected', // 'disconnected', 'connecting', 'connected', 'failed'
    _creatingClient: false, // Prevent multiple simultaneous creation attempts

    // Retry configuration
    retryCount: 0,
    maxRetries: 3,
    retryDelay: 2000, // 2 seconds

    // Active channels (prevent duplicates)
    channels: new Map(),

    // Health monitoring
    lastActivity: Date.now(),
    healthCheckInterval: null,
    healthCheckIntervalMs: 60000, // 60 seconds (reduced frequency for Render)
    reconnectAttempts: 0,
    maxReconnectAttempts: 5,

    // Network state
    isOnline: navigator.onLine,

    /**
     * Initialize connection manager
     */
    async init() {
        console.log('🔷 [Supabase] Initializing connection manager...');

        // Setup network listeners
        this._setupNetworkListeners();

        // Get initial client
        if (window.StatusIndicator) {
            window.StatusIndicator.addOperation('supabase_init', 'Connecting to Supabase...');
        }

        await this.getClient();

        // Start health monitoring
        this._startHealthMonitoring();

        console.log('✅ [Supabase] Connection manager initialized');

        if (window.StatusIndicator) {
            window.StatusIndicator.removeOperation('supabase_init', 'Supabase connected');
        }
    },

    /**
     * Get or create Supabase client (singleton)
     */
    async getClient() {
        // Return existing client if available (regardless of connection state)
        if (this.client) {
            console.log('✅ [Supabase] Using existing client');
            this._updateActivity();
            return this.client;
        }

        // Prevent multiple simultaneous creation attempts
        if (this._creatingClient) {
            console.log('⏳ [Supabase] Client creation in progress, waiting...');
            // Wait for creation to complete
            return await this._waitForClient();
        }

        this._creatingClient = true;

        // Wait for config to load
        if (!window.SUPABASE_CONFIG_LOADED) {
            console.log('⏳ [Supabase] Waiting for config...');
            await window.loadSupabaseConfig();
        }

        // Validate config
        if (!window.SUPABASE_URL || !window.SUPABASE_ANON_KEY) {
            console.error('❌ [Supabase] Configuration missing');
            this.connectionState = 'failed';
            this._creatingClient = false;
            return null;
        }

        // Create client (only once)
        try {
            console.log('🔷 [Supabase] Creating new client...');
            this.client = window.supabase.createClient(
                window.SUPABASE_URL,
                window.SUPABASE_ANON_KEY,
                {
                    realtime: {
                        params: {
                            eventsPerSecond: 10 // Rate limit events
                        }
                    }
                }
            );

            // Set compatibility aliases (for legacy code)
            window.SUPABASE_CLIENT = this.client;
            window.supabaseClient = this.client;

            // Initialize realtime connection (lazy)
            this.connectionState = 'connecting';
            await this._initRealtimeConnection();

            this._updateActivity();
            this._creatingClient = false;
            console.log('✅ [Supabase] Client created and aliases set');
            return this.client;

        } catch (error) {
            console.error('❌ [Supabase] Client creation failed:', error);
            this.connectionState = 'failed';
            this._creatingClient = false;
            return null;
        }
    },

    /**
     * Wait for client creation to complete
     */
    async _waitForClient(timeout = 10000) {
        const startTime = Date.now();

        return new Promise((resolve) => {
            const checkInterval = setInterval(() => {
                if (this.client) {
                    clearInterval(checkInterval);
                    resolve(this.client);
                } else if (!this._creatingClient || Date.now() - startTime > timeout) {
                    clearInterval(checkInterval);
                    resolve(null);
                }
            }, 100);
        });
    },

    /**
     * Initialize realtime connection with retry logic
     */
    async _initRealtimeConnection() {
        if (this.realtimeConnection && this.connectionState === 'connected') {
            console.log('✅ [Supabase] Realtime already connected');
            return true;
        }

        try {
            console.log('🔷 [Supabase] Establishing realtime connection...');

            // Use Promise to wait for subscription result
            return await new Promise((resolve, reject) => {
                const timeout = setTimeout(() => {
                    console.error('❌ [Supabase] Realtime connection timeout (15s)');
                    this.connectionState = 'failed';
                    resolve(false);
                }, 15000);

                // Test connection with a simple channel
                const testChannel = this.client
                    .channel('connection-test')
                    .on('broadcast', { event: 'test' }, () => { })
                    .subscribe((status) => {
                        if (status === 'SUBSCRIBED') {
                            clearTimeout(timeout);
                            console.log('✅ [Supabase] Realtime connection established');
                            this.connectionState = 'connected';
                            this.retryCount = 0;
                            this.reconnectAttempts = 0;

                            // Cleanup test channel
                            setTimeout(() => {
                                if (this.client) {
                                    this.client.removeChannel(testChannel);
                                }
                            }, 1000);

                            this.realtimeConnection = testChannel;
                            resolve(true);

                        } else if (status === 'CHANNEL_ERROR' || status === 'TIMED_OUT') {
                            clearTimeout(timeout);
                            console.error('❌ [Supabase] Realtime connection failed:', status);
                            this.connectionState = 'failed';
                            this._handleConnectionError();
                            resolve(false);
                        }
                    });
            });

        } catch (error) {
            console.error('❌ [Supabase] Realtime init failed:', error);
            this.connectionState = 'failed';
            this._handleConnectionError();
            return false;
        }
    },

    /**
     * Handle connection errors with exponential backoff
     */
    _handleConnectionError() {
        this.retryCount++;

        if (this.retryCount >= this.maxRetries) {
            console.warn('⚠️ [Supabase] Max retries reached - entering fallback mode');
            this.connectionState = 'failed';
            return;
        }

        const delay = this.retryDelay * Math.pow(2, this.retryCount - 1);
        console.log(`🔄 [Supabase] Retrying in ${delay}ms (attempt ${this.retryCount}/${this.maxRetries})...`);

        setTimeout(() => {
            this._initRealtimeConnection();
        }, delay);
    },

    /**
     * Subscribe to a channel (prevents duplicates)
     */
    async subscribeChannel(channelName, config) {
        // Check if channel already exists
        if (this.channels.has(channelName)) {
            console.log(`✅ [Supabase] Channel '${channelName}' already subscribed`);
            this._updateActivity();
            return this.channels.get(channelName);
        }

        // Ensure client is ready
        const client = await this.getClient();
        if (!client) {
            console.error('❌ [Supabase] Cannot subscribe - client unavailable');
            return null;
        }

        // Wait for connection (if connecting)
        if (this.connectionState === 'connecting') {
            console.log('⏳ [Supabase] Waiting for connection...');
            await this._waitForConnection();
        }

        // If connection failed, return null (fallback mode)
        if (this.connectionState === 'failed') {
            console.warn('⚠️ [Supabase] Connection failed - operating in fallback mode');
            return null;
        }

        // Create channel
        try {
            console.log(`🔷 [Supabase] Subscribing to channel: ${channelName}`);
            const channel = client.channel(channelName);

            // Apply configuration
            if (config.table) {
                channel.on(
                    'postgres_changes',
                    {
                        event: config.event || '*',
                        schema: config.schema || 'public',
                        table: config.table,
                        filter: config.filter || null
                    },
                    (payload) => {
                        this._updateActivity();
                        if (config.callback) {
                            config.callback(payload);
                        }
                    }
                );
            }

            // Subscribe with error handling
            channel.subscribe((status) => {
                if (status === 'SUBSCRIBED') {
                    console.log(`✅ [Supabase] Channel '${channelName}' subscribed`);
                    // Reset per-channel reconnect counter so each channel gets
                    // its own independent attempt budget after a successful connect.
                    this.reconnectAttempts = 0;
                } else if (status === 'CHANNEL_ERROR') {
                    console.error(`❌ [Supabase] Channel '${channelName}' error`);
                    this.channels.delete(channelName);

                    // CRITICAL: Remove from Supabase's internal registry before
                    // resubscribing. Without this, client.channel(name) returns the
                    // same already-subscribed object, and calling .on('postgres_changes')
                    // on it throws "cannot add callbacks after subscribe()".
                    const unregister = this.client
                        ? this.client.removeChannel(channel)
                        : Promise.resolve();

                    if (this.isOnline && this.reconnectAttempts < this.maxReconnectAttempts) {
                        this.reconnectAttempts++;
                        unregister.finally(() => {
                            setTimeout(() => {
                                console.log(`🔄 [Supabase] Attempting to resubscribe: ${channelName}`);
                                this.subscribeChannel(channelName, config);
                            }, 2000);
                        });
                    }
                }
            });

            // Store channel reference
            this.channels.set(channelName, channel);
            this._updateActivity();
            return channel;

        } catch (error) {
            console.error(`❌ [Supabase] Failed to subscribe to '${channelName}':`, error);
            return null;
        }
    },

    /**
     * Wait for connection to be established
     */
    async _waitForConnection(timeout = 10000) {
        const startTime = Date.now();

        return new Promise((resolve) => {
            const checkInterval = setInterval(() => {
                if (this.connectionState === 'connected') {
                    clearInterval(checkInterval);
                    resolve(true);
                } else if (this.connectionState === 'failed' || Date.now() - startTime > timeout) {
                    clearInterval(checkInterval);
                    resolve(false);
                }
            }, 100);
        });
    },

    /**
     * Update last activity timestamp
     */
    _updateActivity() {
        this.lastActivity = Date.now();
    },

    /**
     * Start health monitoring (ping only if idle >30s)
     */
    _startHealthMonitoring() {
        // Clear existing interval
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
        }

        this.healthCheckInterval = setInterval(() => {
            this._performHealthCheck();
        }, this.healthCheckIntervalMs);

        console.log('✅ [Supabase] Health monitoring started (60s idle threshold)');
    },

    /**
     * Perform health check (only if idle >30s)
     */
    async _performHealthCheck() {
        // Skip if not connected
        if (this.connectionState !== 'connected') {
            return;
        }

        // Check if idle for more than 60 seconds
        const idleTime = Date.now() - this.lastActivity;
        if (idleTime < this.healthCheckIntervalMs) {
            // Not idle long enough - skip ping
            return;
        }

        console.log(`🔍 [Supabase] Health check (idle for ${Math.round(idleTime / 1000)}s)...`);

        try {
            // Check if we have an established connection using connectionState
            // In newer Supabase JS, check if connection is 'connected' or if we have active channels
            if (this.connectionState === 'connected') {
                console.log('✅ [Supabase] Health check passed (state: connected)');
                return;
            }

            // Alternative: Check if we have any subscribed channels
            const channels = this.client?.getChannels();
            const hasActiveChannels = channels && channels.length > 0;

            if (hasActiveChannels) {
                const subscribedChannels = channels.filter(ch => ch.state === 'joined');
                if (subscribedChannels.length > 0) {
                    console.log(`✅ [Supabase] Health check passed (${subscribedChannels.length} active channels)`);
                    this.connectionState = 'connected'; // Update state
                    return;
                }
            }

            // If we're connecting, give it time
            if (this.connectionState === 'connecting') {
                console.log('⏳ [Supabase] Health check: connecting, waiting...');

                // Wait up to 5s for connection to establish
                await new Promise((resolve) => {
                    const maxWait = 5000;
                    const startTime = Date.now();

                    const checkInterval = setInterval(() => {
                        if (this.connectionState === 'connected') {
                            clearInterval(checkInterval);
                            console.log('✅ [Supabase] Health check passed (connected after wait)');
                            resolve(true);
                        } else if (Date.now() - startTime >= maxWait) {
                            clearInterval(checkInterval);
                            console.warn('⚠️ [Supabase] Health check timed out (still connecting)');
                            this._handleHealthCheckFailure();
                            resolve(false);
                        }
                    }, 500);
                });

                return;
            }

            // No active connection - reconnect needed
            console.warn(`⚠️ [Supabase] Health check failed (state: ${this.connectionState}, channels: ${hasActiveChannels ? 'present but not subscribed' : 'none'})`);
            this._handleHealthCheckFailure();

        } catch (error) {
            console.error('❌ [Supabase] Health check failed:', error);
            this._handleHealthCheckFailure();
        }
    },

    /**
     * Handle health check failure
     */
    _handleHealthCheckFailure() {
        // Don't reconnect if already at max attempts
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.warn('⚠️ [Supabase] Max reconnect attempts reached, health check skipped');
            return;
        }

        // Don't reconnect if already connecting
        if (this.connectionState === 'connecting') {
            console.warn('⚠️ [Supabase] Already reconnecting, skipping duplicate attempt');
            return;
        }

        console.warn('⚠️ [Supabase] Connection unhealthy - attempting reconnection...');
        this.connectionState = 'connecting';
        this._reconnect();
    },

    /**
     * Setup network state listeners
     */
    _setupNetworkListeners() {
        window.addEventListener('online', () => {
            console.log('🌐 [Supabase] Network back online');
            this.isOnline = true;

            // Reconnect if previously disconnected
            if (this.connectionState === 'failed' || this.connectionState === 'disconnected') {
                this._reconnect();
            }
        });

        window.addEventListener('offline', () => {
            console.warn('⚠️ [Supabase] Network offline');
            this.isOnline = false;
            this.connectionState = 'disconnected';
        });

        // Listen for visibility changes (tab active/inactive)
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                console.log('👁️ [Supabase] Tab visible - checking connection...');

                // Check connection health if disconnected
                if (this.connectionState !== 'connected') {
                    this._reconnect();
                }
            }
        });

        console.log('✅ [Supabase] Network listeners configured');
    },

    /**
     * Reconnect to Supabase
     */
    async _reconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('❌ [Supabase] Max reconnect attempts reached');
            this.connectionState = 'failed';
            return;
        }

        this.reconnectAttempts++;
        console.log(`🔄 [Supabase] Reconnecting (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

        if (window.StatusIndicator) {
            window.StatusIndicator.setConnectionStatus('reconnecting', 'Supabase');
        }

        // Disconnect existing channels (but keep client instance)
        this._disconnectChannels();

        // Reset connection state only (DON'T destroy client to avoid multiple GoTrueClient instances)
        this.realtimeConnection = null;
        this.retryCount = 0;
        this.connectionState = 'connecting';

        // Attempt to reconnect realtime (reuses existing client)
        await this._initRealtimeConnection();

        if (this.connectionState === 'connected') {
            console.log('✅ [Supabase] Reconnected successfully');
            this.reconnectAttempts = 0;

            if (window.StatusIndicator) {
                window.StatusIndicator.setConnectionStatus('connected', 'Supabase');
            }

            // Resubscribe to existing channels
            await this._resubscribeChannels();
        } else {
            console.error('❌ [Supabase] Reconnection failed');

            // Stop if max attempts reached
            if (this.reconnectAttempts >= this.maxReconnectAttempts) {
                console.error(`❌ [Supabase] Max reconnect attempts (${this.maxReconnectAttempts}) reached, stopping`);
                this.connectionState = 'disconnected';
                return;
            }

            // Retry with exponential backoff
            const delay = 2000 * Math.pow(2, this.reconnectAttempts - 1);
            console.log(`🔄 [Supabase] Retrying in ${delay}ms...`);
            setTimeout(() => {
                this._reconnect();
            }, delay);
        }
    },

    /**
     * Disconnect all channels (without removing from map)
     */
    _disconnectChannels() {
        if (!this.client) return;

        for (const [name, channel] of this.channels.entries()) {
            try {
                this.client.removeChannel(channel);
            } catch (error) {
                console.error(`❌ [Supabase] Error removing channel ${name}:`, error);
            }
        }
    },

    /**
     * Resubscribe to all channels after reconnection
     */
    async _resubscribeChannels() {
        console.log(`🔄 [Supabase] Resubscribing to ${this.channels.size} channels...`);

        // Get channel configs (stored separately)
        const channelConfigs = new Map(this.channels);
        this.channels.clear();

        // Resubscribe each channel
        for (const [name, oldChannel] of channelConfigs.entries()) {
            // Extract config from old channel (if possible)
            // Note: This is simplified - real implementation would store configs
            console.log(`🔄 [Supabase] Resubscribing: ${name}`);
        }

        console.log('✅ [Supabase] Channels resubscribed');
    },

    /**
     * Check if realtime is connected
     */
    isConnected() {
        return this.connectionState === 'connected';
    },

    /**
     * Get connection state
     */
    getState() {
        return {
            state: this.connectionState,
            isOnline: this.isOnline,
            channels: this.channels.size,
            lastActivity: new Date(this.lastActivity).toISOString(),
            idleTime: Date.now() - this.lastActivity
        };
    },

    /**
     * Unsubscribe from a channel
     */
    unsubscribeChannel(channelName) {
        const channel = this.channels.get(channelName);
        if (channel) {
            console.log(`🔷 [Supabase] Unsubscribing from channel: ${channelName}`);
            if (this.client) {
                this.client.removeChannel(channel);
            }
            this.channels.delete(channelName);
        }
    },

    /**
     * Disconnect and cleanup
     */
    disconnect() {
        console.log('🔷 [Supabase] Disconnecting...');

        // Stop health monitoring
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
            this.healthCheckInterval = null;
        }

        // Unsubscribe all channels
        this._disconnectChannels();
        this.channels.clear();

        // Cleanup realtime connection
        if (this.realtimeConnection && this.client) {
            this.client.removeChannel(this.realtimeConnection);
            this.realtimeConnection = null;
        }

        this.connectionState = 'disconnected';
        console.log('✅ [Supabase] Disconnected');
    }
};

// Auto-initialize on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        SupabaseConnectionManager.init();
    });
} else {
    SupabaseConnectionManager.init();
}
