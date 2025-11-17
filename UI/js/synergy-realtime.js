/**
 * FILE: UI/js/synergy-realtime.js
 * PURPOSE: Real-time WebSocket manager for Synergy dashboard with instant updates
 * 
 * FEATURES:
 * - WebSocket connection to Flask-SocketIO backend
 * - Real-time session updates (create, update, delete, move)
 * - Animated card transitions
 * - Multi-user collaboration support
 * - Auto-reconnection on disconnect
 * 
 * USED BY:
 * - business-ai-platform-v2.html (Synergy dashboard)
 * - SynergyBoard.js (Kanban board)
 * 
 * EXPORTS:
 * - SynergyRealtime.connect() - Connect to WebSocket
 * - SynergyRealtime.disconnect() - Disconnect from WebSocket
 * - SynergyRealtime.isConnected() - Check connection status
 * 
 * LAST MODIFIED: 2025-11-16 - Initial creation with WebSocket integration
 */

window.SynergyRealtime = {
    socket: null,
    connected: false,
    reconnectAttempts: 0,
    maxReconnectAttempts: 10,
    reconnectDelay: 2000,
    config: {
        namespace: '/ws/synergy',
        room: 'synergy_board',
        enableLogging: true
    },

    /**
     * Initialize and connect to WebSocket
     */
    async connect() {
        if (this.connected || this.socket) {
            this._log('Already connected or connecting...');
            return;
        }

        try {
            const apiUrl = window.API_BASE_URL || 'http://localhost:5001';

            this._log('Connecting to WebSocket:', apiUrl + this.config.namespace);

            // Create Socket.IO connection
            // Increased timeout for Render cold starts (can take 30-60 seconds)
            this.socket = io(apiUrl + this.config.namespace, {
                transports: ['websocket', 'polling'],
                reconnection: true,
                reconnectionAttempts: this.maxReconnectAttempts,
                reconnectionDelay: this.reconnectDelay,
                reconnectionDelayMax: 10000,
                timeout: 60000,  // 60 seconds (handles Render cold starts)
                forceNew: false,
                upgrade: true,
                rememberUpgrade: true
            });

            // Connection events
            this.socket.on('connect', () => this._handleConnect());
            this.socket.on('disconnect', (reason) => this._handleDisconnect(reason));
            this.socket.on('connect_error', (error) => this._handleError(error));

            // Synergy-specific events
            this.socket.on('session_created', (data) => this._handleSessionCreated(data));
            this.socket.on('session_updated', (data) => this._handleSessionUpdated(data));
            this.socket.on('session_deleted', (data) => this._handleSessionDeleted(data));
            this.socket.on('column_changed', (data) => this._handleColumnChanged(data));

            // Ping/pong for connection monitoring
            this.socket.on('pong', (data) => {
                this._log('Pong received:', data);
            });

        } catch (error) {
            console.error('[REALTIME] Connection failed:', error);
            this._scheduleReconnect();
        }
    },

    /**
     * Disconnect from WebSocket
     */
    disconnect() {
        if (this.socket) {
            this._log('Disconnecting from WebSocket...');
            this.socket.disconnect();
            this.socket = null;
            this.connected = false;
        }
    },

    /**
     * Check if connected
     */
    isConnected() {
        return this.connected && this.socket && this.socket.connected;
    },

    /**
     * Send ping to server (health check)
     */
    ping() {
        if (this.isConnected()) {
            this.socket.emit('ping', {
                client_id: this.socket.id,
                timestamp: Date.now()
            });
        }
    },

    // ========================================
    // EVENT HANDLERS
    // ========================================

    _handleConnect() {
        this.connected = true;
        this.reconnectAttempts = 0;

        this._log('✅ Connected to WebSocket!', {
            socket_id: this.socket.id,
            namespace: this.config.namespace
        });

        // Subscribe to synergy board room
        this.socket.emit('subscribe', {
            room: this.config.room
        });

        // Show connection indicator
        this._showConnectionStatus('connected');

        // Start periodic ping
        this._startHeartbeat();
    },

    _handleDisconnect(reason) {
        this.connected = false;

        this._log('❌ Disconnected from WebSocket:', reason);

        // Show disconnection indicator
        this._showConnectionStatus('disconnected');

        // Stop heartbeat
        this._stopHeartbeat();

        // Attempt reconnection if not intentional
        if (reason !== 'io client disconnect') {
            this._scheduleReconnect();
        }
    },

    _handleError(error) {
        console.error('[REALTIME] Connection error:', error);
        
        // Provide helpful error messages
        if (error.message === 'timeout') {
            console.warn('[REALTIME] Connection timeout - Server may be starting (Render cold start). Retrying...');
            this._showConnectionStatus('connecting', 'Server starting, please wait...');
        } else {
            this._showConnectionStatus('error');
        }
    },

    _handleSessionCreated(data) {
        this._log('🆕 Session created:', data);

        const { session_id, session } = data;

        // Add card to board
        if (window.synergyBoard && typeof window.synergyBoard.addCardRealtime === 'function') {
            window.synergyBoard.addCardRealtime(session);
        } else {
            // Fallback: Refresh board
            this._refreshBoard();
        }

        // Show notification
        this._showNotification('New session created', session.title, 'success');
    },

    _handleSessionUpdated(data) {
        this._log('📝 Session updated:', data);

        const { session_id, updates } = data;

        // Update card in board
        if (window.synergyBoard && typeof window.synergyBoard.updateCardRealtime === 'function') {
            window.synergyBoard.updateCardRealtime(session_id, updates);
        } else {
            // Fallback: Refresh entire board if no realtime method available
            this._log('⚠️ updateCardRealtime not available, refreshing board');
            this._refreshBoard();
        }

        // Show notification
        if (updates.title) {
            this._showNotification('Session updated', updates.title, 'info');
        }
    },

    _handleSessionDeleted(data) {
        this._log('🗑️ Session deleted:', data);

        const { session_id } = data;

        // Remove card from board with animation
        const card = document.querySelector(`[data-session-id="${session_id}"]`);
        if (card) {
            // Animate out
            card.style.transition = 'all 0.3s ease-out';
            card.style.opacity = '0';
            card.style.transform = 'scale(0.8) translateY(-20px)';

            setTimeout(() => {
                card.remove();

                // Update stats
                if (window.synergyBoard && typeof window.synergyBoard.updateStats === 'function') {
                    window.synergyBoard.updateStats();
                }
            }, 300);
        }

        // Show notification
        this._showNotification('Session deleted', session_id, 'warning');
    },

    _handleColumnChanged(data) {
        this._log('↔️ Column changed:', data);

        const { session_id, from_column, to_column } = data;

        const card = document.querySelector(`[data-session-id="${session_id}"]`);
        if (!card) return;

        const targetColumn = document.querySelector(`[data-column="${to_column}"] .kanban-cards`);
        if (!targetColumn) return;

        // Animate card move
        card.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
        card.style.opacity = '0';
        card.style.transform = 'scale(0.95)';

        setTimeout(() => {
            // Move to new column
            targetColumn.prepend(card);

            // Animate in
            requestAnimationFrame(() => {
                card.style.opacity = '1';
                card.style.transform = 'scale(1)';
            });

            // Update stats
            if (window.synergyBoard && typeof window.synergyBoard.updateStats === 'function') {
                window.synergyBoard.updateStats();
            }
        }, 400);

        // Show notification
        this._showNotification('Card moved', `Moved to ${to_column}`, 'info');
    },

    // ========================================
    // HELPER METHODS
    // ========================================

    _updateCardElement(card, updates) {
        // Update title
        if (updates.title) {
            const titleEl = card.querySelector('.synergy-card-title');
            if (titleEl) titleEl.textContent = updates.title;
        }

        // Update priority
        if (updates.priority) {
            const priorityBadge = card.querySelector('.priority-badge');
            if (priorityBadge) {
                priorityBadge.className = `priority-badge priority-${updates.priority}`;
                priorityBadge.textContent = updates.priority;
            }
        }

        // Update status
        if (updates.status) {
            const statusBadge = card.querySelector('.status-badge');
            if (statusBadge) {
                statusBadge.textContent = updates.status;
            }
        }

        // Highlight card briefly
        card.style.animation = 'highlight 1s ease-out';
        setTimeout(() => {
            card.style.animation = '';
        }, 1000);
    },

    _refreshBoard() {
        // Fallback: Reload entire board
        if (window.synergyBoard && typeof window.synergyBoard.loadSessions === 'function') {
            window.synergyBoard.loadSessions();
        }
    },

    _showConnectionStatus(status, customMessage = null) {
        // Log to console for debugging
        const message = customMessage || status;
        this._log(`Connection status: ${message}`);

        // Show visual indicator only for important states
        if (status === 'connecting' && customMessage) {
            // Show connection status for cold starts
            if (typeof showNotification === 'function') {
                showNotification(customMessage, 'info');
            }
        } else if (status === 'error') {
            // Show error notification
            if (typeof showNotification === 'function') {
                showNotification('Connection error - Check if server is running', 'error');
            }
        }
    },

    _showNotification(title, message, type = 'info') {
        // Use existing notification system if available
        if (typeof showNotification === 'function') {
            showNotification(`${title}: ${message}`, type);
        } else {
            console.log(`[${type.toUpperCase()}] ${title}: ${message}`);
        }
    },

    _scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            this._log('❌ Max reconnection attempts reached');
            this._showConnectionStatus('error');
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1);

        this._log(`⏳ Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

        setTimeout(() => {
            this.connect();
        }, delay);
    },

    _startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            this.ping();
        }, 30000); // Ping every 30 seconds
    },

    _stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    },

    _log(...args) {
        if (this.config.enableLogging) {
            console.log('[REALTIME]', ...args);
        }
    }
};

// Add CSS for highlight animation
const style = document.createElement('style');
style.textContent = `
    @keyframes highlight {
        0%, 100% { box-shadow: none; }
        50% { box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.5); }
    }
`;
document.head.appendChild(style);

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('[REALTIME] Module loaded - Ready to connect');
    });
} else {
    console.log('[REALTIME] Module loaded - Ready to connect');
}

console.log('[REALTIME] WebSocket manager loaded - Use SynergyRealtime.connect()');
