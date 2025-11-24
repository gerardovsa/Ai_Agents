/**
 * FILE: UI/js/supabase-heartbeat-listener.js
 * PURPOSE: Listens to server-side heartbeat broadcasts from Supabase
 * 
 * FEATURES:
 * - Subscribes to 'heartbeat-channel' for server pings
 * - Tracks last heartbeat timestamp
 * - Detects stale connections (no heartbeat in 90+ seconds)
 * - Triggers reconnection when heartbeat stops
 * - Eliminates need for frontend health check pings
 * 
 * INTEGRATION:
 * - Works with SupabaseConnectionManager
 * - Requires server-side pg_cron job (supabase_realtime_heartbeat.sql)
 * - Server broadcasts heartbeat every 60 seconds
 * 
 * EXPORTS:
 * - SupabaseHeartbeatListener.start() - Start listening for heartbeats
 * - SupabaseHeartbeatListener.stop() - Stop listening
 * - SupabaseHeartbeatListener.getLastHeartbeat() - Get last heartbeat timestamp
 * 
 * LAST MODIFIED: 2025-11-24 - Created for server-side heartbeat system
 */

window.SupabaseHeartbeatListener = {
    // State
    heartbeatChannel: null,
    lastHeartbeat: null,
    isListening: false,
    checkInterval: null,
    
    // Configuration
    heartbeatChannelName: 'heartbeat-channel',
    heartbeatStaleThreshold: 90000, // 90 seconds (1.5x heartbeat interval)
    checkIntervalMs: 30000, // Check every 30 seconds
    
    /**
     * Start listening for server heartbeats
     */
    async start() {
        if (this.isListening) {
            console.log('💓 [Heartbeat] Already listening');
            return;
        }
        
        console.log('💓 [Heartbeat] Starting listener...');
        
        // Get Supabase client
        const client = await window.SupabaseConnectionManager.getClient();
        
        if (!client) {
            console.error('❌ [Heartbeat] Cannot start - no Supabase client');
            return;
        }
        
        // Subscribe to heartbeat channel
        this.heartbeatChannel = client
            .channel(this.heartbeatChannelName)
            .on('broadcast', { event: 'heartbeat' }, (payload) => {
                this._onHeartbeat(payload);
            })
            .subscribe((status) => {
                if (status === 'SUBSCRIBED') {
                    console.log('✅ [Heartbeat] Subscribed to server heartbeat channel');
                    this.isListening = true;
                    this.lastHeartbeat = Date.now(); // Initialize on subscribe
                } else if (status === 'CHANNEL_ERROR') {
                    console.error('❌ [Heartbeat] Channel subscription error');
                } else if (status === 'TIMED_OUT') {
                    console.warn('⚠️ [Heartbeat] Channel subscription timed out');
                } else if (status === 'CLOSED') {
                    console.log('🔌 [Heartbeat] Channel closed');
                    this.isListening = false;
                }
            });
        
        // Start periodic staleness check
        this._startStaleCheck();
        
        console.log('💓 [Heartbeat] Listener started');
    },
    
    /**
     * Stop listening for heartbeats
     */
    stop() {
        console.log('💓 [Heartbeat] Stopping listener...');
        
        // Unsubscribe from channel
        if (this.heartbeatChannel) {
            this.heartbeatChannel.unsubscribe();
            this.heartbeatChannel = null;
        }
        
        // Stop staleness check
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
            this.checkInterval = null;
        }
        
        this.isListening = false;
        console.log('✅ [Heartbeat] Listener stopped');
    },
    
    /**
     * Handle incoming heartbeat
     */
    _onHeartbeat(payload) {
        const now = Date.now();
        const timeSinceLast = this.lastHeartbeat ? now - this.lastHeartbeat : 0;
        
        console.log(`💓 [Heartbeat] Server ping received (${timeSinceLast}ms since last)`, payload);
        
        this.lastHeartbeat = now;
        
        // Update connection manager's last activity
        if (window.SupabaseConnectionManager) {
            window.SupabaseConnectionManager._updateActivity();
        }
        
        // Reset reconnection attempts counter (connection is healthy)
        if (window.SupabaseConnectionManager) {
            window.SupabaseConnectionManager.reconnectAttempts = 0;
        }
    },
    
    /**
     * Start periodic staleness check
     */
    _startStaleCheck() {
        // Clear existing interval
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
        }
        
        // Check for stale heartbeat every 30 seconds
        this.checkInterval = setInterval(() => {
            this._checkHeartbeatStaleness();
        }, this.checkIntervalMs);
        
        console.log(`💓 [Heartbeat] Staleness check started (${this.checkIntervalMs / 1000}s interval)`);
    },
    
    /**
     * Check if heartbeat is stale (no heartbeat in 90+ seconds)
     */
    _checkHeartbeatStaleness() {
        // Skip check if not listening
        if (!this.isListening) {
            return;
        }
        
        // Skip check if never received heartbeat
        if (!this.lastHeartbeat) {
            console.log('💓 [Heartbeat] No heartbeat received yet (waiting for first ping)');
            return;
        }
        
        const now = Date.now();
        const timeSinceLast = now - this.lastHeartbeat;
        
        // Check if heartbeat is stale
        if (timeSinceLast > this.heartbeatStaleThreshold) {
            console.warn(`⚠️ [Heartbeat] Stale detected! No heartbeat for ${Math.round(timeSinceLast / 1000)}s`);
            console.warn('⚠️ [Heartbeat] Connection appears dead - triggering reconnection...');
            
            // Trigger reconnection in connection manager
            if (window.SupabaseConnectionManager) {
                this._triggerReconnection();
            }
        } else {
            console.log(`💓 [Heartbeat] Connection healthy (${Math.round(timeSinceLast / 1000)}s since last ping)`);
        }
    },
    
    /**
     * Trigger reconnection in connection manager
     */
    async _triggerReconnection() {
        // Stop listening during reconnection
        this.stop();
        
        // Show status indicator
        if (window.StatusIndicator) {
            window.StatusIndicator.setConnectionStatus('reconnecting', 'Supabase');
        }
        
        // Trigger reconnection
        if (window.SupabaseConnectionManager && window.SupabaseConnectionManager._handleHealthCheckFailure) {
            await window.SupabaseConnectionManager._handleHealthCheckFailure();
        }
        
        // Restart listening after reconnection
        setTimeout(() => {
            this.start();
        }, 2000);
    },
    
    /**
     * Get last heartbeat timestamp
     */
    getLastHeartbeat() {
        return this.lastHeartbeat;
    },
    
    /**
     * Get time since last heartbeat (in milliseconds)
     */
    getTimeSinceLastHeartbeat() {
        if (!this.lastHeartbeat) {
            return null;
        }
        return Date.now() - this.lastHeartbeat;
    },
    
    /**
     * Check if connection is healthy (based on heartbeat)
     */
    isConnectionHealthy() {
        if (!this.isListening || !this.lastHeartbeat) {
            return false; // Not listening or no heartbeat yet
        }
        
        const timeSinceLast = this.getTimeSinceLastHeartbeat();
        return timeSinceLast <= this.heartbeatStaleThreshold;
    }
};

// Auto-start when connection manager initializes
if (window.SupabaseConnectionManager) {
    // Hook into connection manager's init
    const originalInit = window.SupabaseConnectionManager.init;
    window.SupabaseConnectionManager.init = async function() {
        await originalInit.call(this);
        // Start heartbeat listener after connection manager initializes
        if (window.SupabaseHeartbeatListener) {
            await window.SupabaseHeartbeatListener.start();
        }
    };
}

console.log('✅ [Heartbeat] Listener module loaded');
