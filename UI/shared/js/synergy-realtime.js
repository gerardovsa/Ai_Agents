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
    sessionToken: null,  // Unique browser session identifier
    sessionDisplayName: null,  // Per-session display name for multi-user collaboration
    heartbeatInterval: null,
    otherSessionsViewingAgents: {},  // Track other sessions' agent viewing: { agentId: [{ session_token, device, user_name }] }
    presenceContext: {
        room: 'synergy_board',
        scope: null,
        badgeContainerId: 'active-users-badge',
        badgeCountId: 'active-users-count'
    },
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
            // Check if Socket.IO is available
            if (typeof io === 'undefined') {
                console.warn('[REALTIME] Socket.IO library not loaded - real-time updates disabled');
                return;
            }

            const apiUrl = window.API_BASE_URL || 'http://localhost:5001';

            this._log('Connecting to WebSocket:', apiUrl + this.config.namespace);

            // ========================================
            // INTELLIGENT TRANSPORT SELECTION
            // ========================================
            // Render production: WebSocket-first (avoids load balancer polling issues)
            // Local development: Polling-first (more reliable for localhost)
            const isRenderProduction = apiUrl.includes('onrender.com');
            const isLocalhost = apiUrl.includes('localhost') || apiUrl.includes('127.0.0.1');
            
            // Transport priority based on environment
            const transports = isRenderProduction 
                ? ['websocket', 'polling']  // Render: Try WebSocket first to avoid load balancer interference
                : ['polling', 'websocket']; // Local: Polling first (more stable for dev)
            
            // Timeout configuration based on environment
            const timeout = isRenderProduction ? 30000 : 20000;  // 30s for Render cold starts, 20s local
            
            this._log(`Environment: ${isRenderProduction ? 'Render Production' : isLocalhost ? 'Local Development' : 'Unknown'}`);
            this._log(`Transport priority: ${transports.join(' -> ')}`);
            this._log(`Connection timeout: ${timeout}ms`);

            // Create Socket.IO connection with environment-aware configuration
            // Server config: ping_interval=25s, ping_timeout=60s
            // Client heartbeat: 20s (see _startHeartbeat) - must be < server ping_interval
            this.socket = io(apiUrl + this.config.namespace, {
                // Intelligent transport selection (see above)
                transports: transports,
                reconnection: true,
                reconnectionAttempts: this.maxReconnectAttempts,
                reconnectionDelay: this.reconnectDelay,
                reconnectionDelayMax: 10000,
                timeout: timeout,  // Environment-aware timeout
                forceNew: false,
                upgrade: true,  // Allow transport upgrade (polling -> WebSocket or vice versa)
                rememberUpgrade: true,
                autoConnect: true,
                // Render-specific: Explicit path to avoid proxy routing issues
                path: '/socket.io/',
                // Disable credentials to prevent CORS issues on Render
                withCredentials: false,
                // Enhanced error recovery
                closeOnBeforeunload: false  // Keep connection alive during page navigation
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

            // User presence events (multi-user collaboration)
            this.socket.on('user_joined', (data) => this._handleUserJoined(data));
            this.socket.on('user_session_left', (data) => this._handleUserSessionLeft(data));
            this.socket.on('presence_confirmed', (data) => this._handlePresenceConfirmed(data));

            // Internal messaging events
            this.socket.on('direct_message_received', (data) => this._handleDirectMessageReceived(data));
            this.socket.on('broadcast_message_received', (data) => this._handleBroadcastMessageReceived(data));
            this.socket.on('message_delivered', (data) => this._handleMessageDelivered(data));
            this.socket.on('message_delivery_failed', (data) => this._handleMessageDeliveryFailed(data));

            // Command Center: agent thread synchronization across sessions
            this.socket.on('agent_thread_updated', (data) => this._handleAgentThreadUpdated(data));

            // Ping/pong for connection monitoring
            this.socket.on('pong', (data) => {
                this._log('Pong received:', data);
            });

        } catch (error) {
            console.error('[REALTIME] Connection failed:', error);
            console.warn('[REALTIME] Real-time updates disabled - dashboard will work in polling mode');
            // Don't schedule reconnect if connection fundamentally fails
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

        // Subscribe to current presence room
        const room = this.presenceContext?.room || this.config.room;
        this.socket.emit('subscribe', { room });

        // Announce user presence (for multi-user collaboration)
        this._announcePresence();

        // Show connection indicator
        this._showConnectionStatus('connected');

        // Start periodic ping
        this._startHeartbeat();
    },

    /**
     * Update presence room + badge mapping (e.g. Synergy vs Command Center)
     * Keeps the same socket connection.
     */
    setPresenceContext({ room, badgeContainerId, badgeCountId } = {}) {
        const previousRoom = this.presenceContext?.room;
        if (room) this.presenceContext.room = room;
        if (badgeContainerId) this.presenceContext.badgeContainerId = badgeContainerId;
        if (badgeCountId) this.presenceContext.badgeCountId = badgeCountId;

        if (!this.isConnected()) return;

        // Switch Socket.IO room subscriptions
        if (previousRoom && previousRoom !== this.presenceContext.room) {
            this.socket.emit('unsubscribe', { room: previousRoom });
        }
        this.socket.emit('subscribe', { room: this.presenceContext.room });

        // Announce presence in new context
        this._announcePresence();
    },

    /**
     * Update the user's active scope within the current room (e.g. agent:1)
     */
    setPresenceScope(scope) {
        this.presenceContext.scope = scope || null;
        if (this.isConnected()) {
            this._announcePresence();
        }
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
        // Only log first 3 errors to avoid console spam
        if (this.reconnectAttempts <= 3) {
            console.error('[REALTIME] Connection error:', error);
        }

        // Provide helpful error messages
        if (error.message === 'timeout') {
            if (this.reconnectAttempts <= 3) {
                console.warn('[REALTIME] Connection timeout - Backend server not responding.');
            }
            this._showConnectionStatus('disconnected', 'Backend server offline');

            // Stop retrying after 5 attempts to avoid infinite console spam
            if (this.reconnectAttempts >= 5) {
                if (this.reconnectAttempts === 5) {
                    console.warn('[REALTIME] ⚠️ Backend server is DOWN. Stopping reconnection attempts. Working in offline mode.');
                }
                this.maxReconnectAttempts = this.reconnectAttempts; // Stop further attempts
                if (this.socket) {
                    this.socket.close();
                }
            }
        } else if (error.message && error.message.includes('Invalid frame header')) {
            if (this.reconnectAttempts <= 3) {
                console.warn('[REALTIME] WebSocket handshake failed - Server may not be running or Socket.IO not initialized');
            }
            this._showConnectionStatus('disconnected', 'Backend not responding. Working in offline mode.');
            // Stop trying to reconnect after 3 attempts for this specific error
            if (this.reconnectAttempts >= 3) {
                if (this.reconnectAttempts === 3) {
                    console.warn('[REALTIME] Stopping reconnection attempts - working in offline mode');
                }
                this.maxReconnectAttempts = this.reconnectAttempts; // Stop further attempts
            }
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

    _handleAgentThreadUpdated(data) {
        // Broadcast a DOM event so modules can react without importing this file.
        this._log('🔄 Agent thread updated (Command Center):', data);

        try {
            window.dispatchEvent(new CustomEvent('synergyrealtime:agent_thread_updated', {
                detail: data
            }));
        } catch (e) {
            console.warn('[REALTIME] Failed to dispatch agent_thread_updated event:', e);
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

    _showNotification(arg1, arg2 = 'info', arg3 = null) {
        // Supports BOTH call styles used in this file:
        // 1) _showNotification(title, message, type)
        // 2) _showNotification(message, type, subtitle)

        const knownTypes = new Set(['success', 'info', 'warning', 'error']);

        let message;
        let type;
        let subtitle = null;

        // Presence-style: (message, type, subtitle)
        if (typeof arg2 === 'string' && knownTypes.has(arg2)) {
            message = String(arg1 ?? '');
            type = arg2;
            subtitle = arg3;
        } else {
            // Title/message-style: (title, message, type)
            const title = String(arg1 ?? '');
            const body = String(arg2 ?? '');
            type = typeof arg3 === 'string' ? arg3 : 'info';
            message = body ? `${title}: ${body}` : title;
        }

        if (window.showNotification && typeof window.showNotification === 'function') {
            window.showNotification(message, type);
            return;
        }

        const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
        console.log(`${icon} [REALTIME] ${message}${subtitle ? ` - ${subtitle}` : ''}`);
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

            // Send presence heartbeat
            if (this.sessionToken && this.isConnected()) {
                this.socket.emit('user_heartbeat', {
                    user_id: this._getUserId(),
                    session_token: this.sessionToken
                });
            }
        }, 20000); // Ping every 20 seconds (faster than server's 25s ping_interval to prevent timeouts)
    },

    _stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    },

    // ========================================
    // USER PRESENCE (Multi-User Collaboration)
    // ========================================

    _generateSessionToken() {
        // Generate unique session token for this browser tab
        if (!this.sessionToken) {
            this.sessionToken = 'session_' + Math.random().toString(36).substring(2) + '_' + Date.now();
        }
        return this.sessionToken;
    },

    async _getSessionDisplayName() {
        // Get or prompt for per-session display name (for multi-user collaboration)
        if (this.sessionDisplayName) {
            return this.sessionDisplayName;
        }

        // Check localStorage first (persists across page reloads for this browser)
        const stored = localStorage.getItem('session_display_name');
        if (stored) {
            this.sessionDisplayName = stored;
            return stored;
        }

        // Use username as default
        const defaultName = this._getUserName();
        this.sessionDisplayName = defaultName;
        localStorage.setItem('session_display_name', defaultName);
        return defaultName;
    },

    _getUserId() {
        // CRITICAL FIX: Wait for UserAuth to load before falling back
        if (typeof window.UserAuth === 'undefined') {
            console.warn('[REALTIME] UserAuth not loaded yet - presence may be inaccurate');
            return null; // Return null instead of fallback to prevent collisions
        }

        if (window.UserAuth && window.UserAuth.user) {
            return window.UserAuth.user.id || window.UserAuth.user.user_id;
        }

        // Only use fallback if UserAuth exists but has no user
        console.warn('[REALTIME] UserAuth loaded but no user - using fallback user_id');
        return 1;
    },

    _getUserName() {
        if (window.UserAuth && window.UserAuth.user) {
            return window.UserAuth.user.username || window.UserAuth.user.email || 'User';
        }
        return 'User';
    },

    _getDeviceInfo() {
        const ua = navigator.userAgent;
        if (/iPhone|iPad|iPod/.test(ua)) return 'iPhone';
        if (/Android/.test(ua)) return 'Android';
        if (/Mac/.test(ua)) return 'Mac';
        if (/Windows/.test(ua)) return 'Windows';
        if (/Linux/.test(ua)) return 'Linux';
        return 'Desktop';
    },

    async _announcePresence() {
        if (!this.isConnected()) return;

        const userId = this._getUserId();
        if (!userId) {
            console.warn('[REALTIME] Cannot announce presence - user_id not available yet');
            // Retry after UserAuth loads
            setTimeout(() => this._announcePresence(), 1000);
            return;
        }

        // Get per-session display name for multi-user collaboration
        const displayName = await this._getSessionDisplayName();

        const presenceData = {
            user_id: userId,
            user_name: this._getUserName(),
            display_name: displayName,  // Per-session identity
            device: this._getDeviceInfo(),
            session_token: this._generateSessionToken(),
            room: this.presenceContext?.room || this.config.room,
            scope: this.presenceContext?.scope || null,
            privacy_mode: this.getPrivacyMode(),  // 'central' or 'local'
            team_id: this._getTeamId()  // For team-based privacy routing
        };

        this._log('Announcing presence:', presenceData);
        this.socket.emit('user_presence', presenceData);
    },

    // ✨ NEW: Update agent viewing scope and broadcast to other users
    updateAgentViewingScope(agentId) {
        // Update local context
        this.presenceContext.scope = agentId ? `agent:${agentId}` : null;

        // Re-announce presence with new scope (reuses existing infrastructure)
        this._announcePresence();

        this._log(`Updated viewing scope to agent: ${agentId}`);
    },

    // ========================================
    // INTERNAL MESSAGING
    // ========================================

    /**
     * Send direct message to specific user
     * @param {number} targetUserId - Target user's ID
     * @param {string} message - Message content
     * @param {string} [targetSessionToken] - Optional: specific session token
     */
    sendDirectMessage(targetUserId, message, targetSessionToken = null) {
        if (!this.isConnected()) {
            console.warn('[REALTIME] Cannot send message - not connected');
            return false;
        }

        const userId = this._getUserId();
        if (!userId) {
            console.warn('[REALTIME] Cannot send message - user_id not available');
            return false;
        }

        this.socket.emit('send_direct_message', {
            target_user_id: targetUserId,
            target_session_token: targetSessionToken,
            message: message,
            sender_user_id: userId,
            sender_user_name: this._getUserName(),
            sender_session_token: this.sessionToken
        });

        this._log(`Sent direct message to user ${targetUserId}:`, message);
        return true;
    },

    /**
     * Broadcast message to all users in room
     * @param {string} message - Message content
     * @param {string} [room] - Target room (default: current room)
     */
    broadcastMessage(message, room = null) {
        if (!this.isConnected()) {
            console.warn('[REALTIME] Cannot broadcast - not connected');
            return false;
        }

        const userId = this._getUserId();
        if (!userId) {
            console.warn('[REALTIME] Cannot broadcast - user_id not available');
            return false;
        }

        this.socket.emit('broadcast_message', {
            message: message,
            sender_user_id: userId,
            sender_user_name: this._getUserName(),
            room: room || this.presenceContext?.room || this.config.room
        });

        this._log(`Broadcast message to room:`, message);
        return true;
    },

    _handleDirectMessageReceived(data) {
        this._log('Direct message received:', data);

        // Show enhanced toast notification (if available)
        if (typeof EnhancedToast !== 'undefined' && EnhancedToast.showMessageToast) {
            EnhancedToast.showMessageToast(data, 'direct');
        } else {
            // Fallback to basic notification
            this._showNotification(
                `Message from ${data.from_user_name}: ${data.message}`,
                'info'
            );
        }

        // Dispatch custom event for UI to handle
        window.dispatchEvent(new CustomEvent('synergy:direct_message', {
            detail: data
        }));
    },

    _handleBroadcastMessageReceived(data) {
        this._log('Broadcast message received:', data);

        // Show enhanced toast notification (if available)
        if (typeof EnhancedToast !== 'undefined' && EnhancedToast.showMessageToast) {
            EnhancedToast.showMessageToast(data, 'broadcast');
        } else {
            // Fallback to basic notification
            this._showNotification(
                `${data.from_user_name} (broadcast): ${data.message}`,
                'info'
            );
        }

        // Dispatch custom event for UI to handle
        window.dispatchEvent(new CustomEvent('synergy:broadcast_message', {
            detail: data
        }));
    },

    _handleMessageDelivered(data) {
        this._log('Message delivered:', data);

        if (data.delivered_count === 0) {
            this._showNotification('Message not delivered - user has no active sessions', 'warning');
        } else {
            this._showNotification(`Message delivered to ${data.delivered_count} session(s)`, 'success');
        }
    },

    _handleMessageDeliveryFailed(data) {
        this._log('Message delivery failed:', data);
        this._showNotification(`Message failed: ${data.reason}`, 'error');
    },

    _handleUserJoined(data) {
        this._log('👤 User joined:', data);

        // Don't show notification for our own session
        if (data.session_token === this.sessionToken) return;

        // Command Centers are per-user: only show/track multiple sessions for the SAME user_id
        // (ignore other users entirely at this stage)
        const currentUserId = this._getUserId();
        if (currentUserId && data.user_id && String(data.user_id) !== String(currentUserId)) {
            return;
        }

        // ✨ Track other session viewing agent (could be same user, different device)
        if (data.scope) {
            if (!this.otherSessionsViewingAgents[data.scope]) {
                this.otherSessionsViewingAgents[data.scope] = [];
            }

            // Add or update this session
            const existingIndex = this.otherSessionsViewingAgents[data.scope].findIndex(
                s => s.session_token === data.session_token
            );

            const sessionInfo = {
                session_token: data.session_token,
                device: data.device,
                user_name: data.user_name,
                display_name: data.display_name || data.user_name,  // Use display_name if available
                user_id: data.user_id
            };

            if (existingIndex >= 0) {
                this.otherSessionsViewingAgents[data.scope][existingIndex] = sessionInfo;
            } else {
                this.otherSessionsViewingAgents[data.scope].push(sessionInfo);
            }

            // Update Command Center UI for agent scopes
            const agentId = this._getAgentIdFromScope(data.scope);
            if (agentId && typeof MultiAgent !== 'undefined' && typeof MultiAgent.updateBadgeForOtherSessions === 'function') {
                MultiAgent.updateBadgeForOtherSessions(agentId, this.otherSessionsViewingAgents[data.scope]);
            }
        }

        // Show notification
        this._showNotification(
            `${data.user_name} joined from ${data.device}`,
            'info',
            `${data.active_session_count} active session(s)`
        );

        // Update active users count in UI
        this._updateActiveUsersCount(data.active_session_count, data.room);
        this._updateScopeCount(data);
    },

    _handleUserSessionLeft(data) {
        this._log('👋 User session left:', data);

        // Command Centers are per-user: only show/track multiple sessions for the SAME user_id
        const currentUserId = this._getUserId();
        if (currentUserId && data.user_id && String(data.user_id) !== String(currentUserId)) {
            return;
        }

        // ✨ Remove session from tracking
        if (data.scope && this.otherSessionsViewingAgents[data.scope]) {
            this.otherSessionsViewingAgents[data.scope] = this.otherSessionsViewingAgents[data.scope].filter(
                s => s.session_token !== data.session_token
            );

            // If no more sessions viewing this agent, clean up
            if (this.otherSessionsViewingAgents[data.scope].length === 0) {
                delete this.otherSessionsViewingAgents[data.scope];
            }

            // Update Command Center UI for agent scopes
            const agentId = this._getAgentIdFromScope(data.scope);
            if (agentId && typeof MultiAgent !== 'undefined' && typeof MultiAgent.updateBadgeForOtherSessions === 'function') {
                const remainingSessions = this.otherSessionsViewingAgents[data.scope] || [];
                MultiAgent.updateBadgeForOtherSessions(agentId, remainingSessions);
            }
        }

        this._showNotification(
            `${data.user_name} disconnected (${data.device})`,
            'info',
            `${data.active_session_count} active session(s)`
        );

        this._updateActiveUsersCount(data.active_session_count, data.room);
        this._updateScopeCount(data);
    },

    _handlePresenceConfirmed(data) {
        this._log('✅ Presence confirmed:', data);

        if (data.other_sessions && data.other_sessions.length > 0) {
            this._log(`ℹ️  Found ${data.other_sessions.length} other active session(s):`, data.other_sessions);

            // ✨ Track what agents YOUR other sessions are viewing
            data.other_sessions.forEach(session => {
                if (session.scope) {
                    if (!this.otherSessionsViewingAgents[session.scope]) {
                        this.otherSessionsViewingAgents[session.scope] = [];
                    }

                    // Add YOUR other session to tracking (same user_id, different device)
                    const sessionInfo = {
                        session_token: session.session_token,
                        device: session.device,
                        user_name: this._getUserName(),  // It's YOUR session
                        user_id: this._getUserId(),
                        isYourOtherSession: true  // Flag to show "You (Desktop)" instead of user name
                    };

                    const existingIndex = this.otherSessionsViewingAgents[session.scope].findIndex(
                        s => s.session_token === session.session_token
                    );

                    if (existingIndex >= 0) {
                        this.otherSessionsViewingAgents[session.scope][existingIndex] = sessionInfo;
                    } else {
                        this.otherSessionsViewingAgents[session.scope].push(sessionInfo);
                    }

                    // Update Command Center UI for agent scopes
                    const agentId = this._getAgentIdFromScope(session.scope);
                    if (agentId && typeof MultiAgent !== 'undefined' && typeof MultiAgent.updateBadgeForOtherSessions === 'function') {
                        MultiAgent.updateBadgeForOtherSessions(agentId, this.otherSessionsViewingAgents[session.scope]);
                    }
                }
            });

            this._showNotification(
                `You have ${data.other_sessions.length} other active session(s)`,
                'info',
                'Changes sync across all your devices'
            );
        }

        this._updateActiveUsersCount(data.active_session_count, data.room);
        this._updateScopeCount(data);
    },

    _getAgentIdFromScope(scope) {
        if (!scope || typeof scope !== 'string') return null;
        if (!scope.startsWith('agent:')) return null;
        const agentId = scope.split(':')[1];
        if (!agentId) return null;
        return agentId;
    },

    _updateActiveUsersCount(count, room = null) {
        // Only update the currently active room's badge
        const activeRoom = this.presenceContext?.room;
        if (room && activeRoom && room !== activeRoom) return;

        const badgeContainer = document.getElementById(this.presenceContext?.badgeContainerId || 'active-users-badge');
        const countEl = document.getElementById(this.presenceContext?.badgeCountId || 'active-users-count');

        if (countEl) {
            countEl.textContent = count;
            countEl.title = `${count} active session${count !== 1 ? 's' : ''}`;
        }

        // Toggle the container (the HTML sets it to display:none initially)
        if (badgeContainer) {
            badgeContainer.style.display = count > 1 ? 'inline-flex' : 'none';
            badgeContainer.title = `${count} active session${count !== 1 ? 's' : ''}`;
        }
    },

    _updateScopeCount(data) {
        // Optional per-agent badges (Command Center)
        // Convention: scope = `agent:<id>` maps to DOM ids:
        // - agent-active-users-badge-<id>
        // - agent-active-users-count-<id>
        if (!data || !data.scope || typeof data.scope !== 'string') return;
        if (!data.scope.startsWith('agent:')) return;

        const agentId = data.scope.split(':')[1];
        if (!agentId) return;

        const badgeContainer = document.getElementById(`agent-active-users-badge-${agentId}`);
        const countEl = document.getElementById(`agent-active-users-count-${agentId}`);

        if (countEl && typeof data.active_scope_session_count === 'number') {
            countEl.textContent = data.active_scope_session_count;
            countEl.title = `${data.active_scope_session_count} active session${data.active_scope_session_count !== 1 ? 's' : ''}`;
        }

        if (badgeContainer && typeof data.active_scope_session_count === 'number') {
            badgeContainer.style.display = data.active_scope_session_count > 1 ? 'inline-flex' : 'none';
            badgeContainer.title = `${data.active_scope_session_count} active session${data.active_scope_session_count !== 1 ? 's' : ''}`;
        }
    },

    // ========================================
    // PRIVACY MODE (Central HQ / Local Ops)
    // ========================================

    /**
     * Get current privacy mode from localStorage
     * @returns {string} 'central' or 'local'
     */
    getPrivacyMode() {
        return localStorage.getItem('privacy_mode') || 'central';
    },

    /**
     * Set privacy mode and save to localStorage
     * @param {string} mode - 'central' or 'local'
     */
    setPrivacyMode(mode) {
        if (mode !== 'central' && mode !== 'local') {
            console.warn('[REALTIME] Invalid privacy mode:', mode);
            return;
        }

        localStorage.setItem('privacy_mode', mode);
        this._log('Privacy mode set to:', mode);

        // Re-announce presence with new privacy mode
        if (this.isConnected()) {
            this._announcePresence();
        }
    },

    /**
     * Get team ID for privacy mode (user_id for team sharing)
     */
    _getTeamId() {
        if (window.UserAuth && window.UserAuth.user) {
            return window.UserAuth.user.id || window.UserAuth.user.username || 'unknown';
        }
        return 'unknown';
    },

    _log(...args) {
        if (this.config.enableLogging) {
            console.log('[REALTIME]', ...args);
        }
    }
};

// Add CSS for highlight animation
if (!document.getElementById('synergy-realtime-styles')) {
    const synergyRealtimeStyle = document.createElement('style');
    synergyRealtimeStyle.id = 'synergy-realtime-styles';
    synergyRealtimeStyle.textContent = `
        @keyframes highlight {
            0%, 100% { box-shadow: none; }
            50% { box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.5); }
        }
    `;
    document.head.appendChild(synergyRealtimeStyle);
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('[REALTIME] Module loaded - Ready to connect');
    });
} else {
    console.log('[REALTIME] Module loaded - Ready to connect');
}

console.log('[REALTIME] WebSocket manager loaded - Use SynergyRealtime.connect()');
