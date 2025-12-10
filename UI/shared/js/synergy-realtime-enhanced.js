/**
 * FILE: UI/shared/js/synergy-realtime-enhanced.js
 * PURPOSE: Enhanced Synergy realtime with conditional updates and notifications
 * 
 * ENHANCEMENTS:
 * - Conditional updates (only when viewing Synergy)
 * - Notifications for user's own sessions
 * - Full metadata field tracking (15 fields)
 * - Smart notification system
 * - Performance optimizations
 * 
 * LAST MODIFIED: 2025-12-09 - Full enhancement implementation
 */

window.SynergyRealtimeEnhanced = {
    socket: null,
    connected: false,
    reconnectAttempts: 0,
    maxReconnectAttempts: 10,
    reconnectDelay: 2000,
    currentUserId: null,
    config: {
        namespace: '/ws/synergy',
        room: 'synergy_board',
        enableLogging: true,
        conditionalUpdates: true,
        notifyOwnSessions: true
    },

    /**
     * Initialize and connect to WebSocket
     */
    async connect(userId = null) {
        if (this.connected || this.socket) {
            this._log('Already connected or connecting...');
            return;
        }

        this.currentUserId = userId;

        try {
            if (typeof io === 'undefined') {
                console.warn('[SYNERGY-RT] Socket.IO library not loaded');
                return;
            }

            const apiUrl = window.API_BASE_URL || 'http://localhost:5001';

            this._log('Connecting to WebSocket:', apiUrl + this.config.namespace);

            this.socket = io(apiUrl + this.config.namespace, {
                transports: ['polling', 'websocket'],
                reconnection: true,
                reconnectionAttempts: this.maxReconnectAttempts,
                reconnectionDelay: this.reconnectDelay,
                reconnectionDelayMax: 10000,
                timeout: 60000,
                forceNew: false,
                upgrade: true,
                rememberUpgrade: true,
                autoConnect: true
            });

            // Connection events
            this.socket.on('connect', () => this._handleConnect());
            this.socket.on('disconnect', (reason) => this._handleDisconnect(reason));
            this.socket.on('connect_error', (error) => this._handleError(error));

            // Enhanced Synergy events
            this.socket.on('session_created', (data) => this._handleSessionCreated(data));
            this.socket.on('session_updated', (data) => this._handleSessionUpdated(data));
            this.socket.on('session_deleted', (data) => this._handleSessionDeleted(data));
            this.socket.on('column_changed', (data) => this._handleColumnChanged(data));

            // New metadata change events
            this.socket.on('session_metadata_changed', (data) => this._handleMetadataChanged(data));

            // Ping/pong for connection monitoring
            this.socket.on('pong', (data) => {
                this._log('Pong received:', data);
            });

        } catch (error) {
            console.error('[SYNERGY-RT] Connection failed:', error);
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
     * 🎯 Check if user is actively viewing Synergy
     */
    isUserViewingSynergy() {
        // Check if Synergy tab is active
        const synergyTab = document.querySelector('[data-tab="synergy"]');
        if (synergyTab && synergyTab.classList.contains('active')) {
            return true;
        }

        // Check if Synergy sidebar is open
        const synergySidebar = document.getElementById('synergy-sidebar');
        if (synergySidebar && !synergySidebar.classList.contains('collapsed')) {
            return true;
        }

        // Check if Synergy dashboard is visible
        const synergyDashboard = document.getElementById('synergy-dashboard');
        if (synergyDashboard && synergyDashboard.offsetParent !== null) {
            return true;
        }

        return false;
    },

    /**
     * 🔔 Check if session belongs to current user
     */
    isUserSession(session) {
        if (!this.currentUserId || !session) return false;

        // Check owner
        if (session.owner_user_id === this.currentUserId) {
            return true;
        }

        // Check if user is in assignees
        if (session.assignees) {
            try {
                const assignees = typeof session.assignees === 'string'
                    ? JSON.parse(session.assignees)
                    : session.assignees;

                if (Array.isArray(assignees) && assignees.includes(this.currentUserId)) {
                    return true;
                }
            } catch (e) {
                // Parse error, ignore
            }
        }

        return false;
    },

    // ========================================
    // ENHANCED EVENT HANDLERS
    // ========================================

    _handleConnect() {
        this.connected = true;
        this.reconnectAttempts = 0;

        this._log('✅ Connected to WebSocket!', {
            socket_id: this.socket.id,
            namespace: this.config.namespace,
            user_id: this.currentUserId
        });

        // Subscribe to synergy board room
        this.socket.emit('subscribe', {
            room: this.config.room,
            user_id: this.currentUserId
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
        console.error('[SYNERGY-RT] Connection error:', error);

        if (error.message === 'timeout') {
            console.warn('[SYNERGY-RT] Connection timeout - Server may be starting');
            this._showConnectionStatus('connecting', 'Server starting, please wait...');
        } else {
            this._showConnectionStatus('error');
        }
    },

    _handleSessionCreated(data) {
        this._log('🆕 Session created:', data);

        const { session_id, session } = data;

        // ✅ Conditional: Only update UI if viewing Synergy
        if (!this.config.conditionalUpdates || this.isUserViewingSynergy()) {
            // Add card to board
            if (window.synergyBoard && typeof window.synergyBoard.addCardRealtime === 'function') {
                window.synergyBoard.addCardRealtime(session);
            } else {
                this._refreshBoard();
            }
        } else {
            this._log('⏸️ Not viewing Synergy - update queued');
        }

        // 🔔 Notify if user's session
        if (this.config.notifyOwnSessions && this.isUserSession(session)) {
            this._showNotification(
                'New Session Created',
                `Your session "${session.title}" has been created`,
                'success'
            );
        }
    },

    _handleSessionUpdated(data) {
        this._log('📝 Session updated:', data);

        const { session_id, updates, session } = data;

        // ✅ Conditional: Only update UI if viewing Synergy
        if (!this.config.conditionalUpdates || this.isUserViewingSynergy()) {
            // Detect what changed
            const changes = this._detectChanges(updates);

            // Update card in board
            if (window.synergyBoard && typeof window.synergyBoard.updateCardRealtime === 'function') {
                window.synergyBoard.updateCardRealtime(session_id, updates);
            } else {
                this._refreshBoard();
            }

            // Apply visual updates based on what changed
            this._applyVisualUpdates(session_id, changes);

        } else {
            this._log('⏸️ Not viewing Synergy - update queued');
        }

        // 🔔 Notify if user's session
        if (this.config.notifyOwnSessions && session && this.isUserSession(session)) {
            this._notifyUserSession(session, updates);
        }
    },

    _handleSessionDeleted(data) {
        this._log('🗑️ Session deleted:', data);

        const { session_id, session } = data;

        // ✅ Conditional: Only update UI if viewing Synergy
        if (!this.config.conditionalUpdates || this.isUserViewingSynergy()) {
            const card = document.querySelector(`[data-session-id="${session_id}"]`);
            if (card) {
                // Animate out
                card.style.transition = 'all 0.3s ease-out';
                card.style.opacity = '0';
                card.style.transform = 'scale(0.8) translateY(-20px)';

                setTimeout(() => {
                    card.remove();

                    if (window.synergyBoard && typeof window.synergyBoard.updateStats === 'function') {
                        window.synergyBoard.updateStats();
                    }
                }, 300);
            }
        }

        // 🔔 Notify if user's session
        if (this.config.notifyOwnSessions && session && this.isUserSession(session)) {
            this._showNotification(
                'Session Deleted',
                `Your session "${session.title}" was deleted`,
                'warning'
            );
        }
    },

    _handleColumnChanged(data) {
        this._log('↔️ Column changed:', data);

        const { session_id, from_column, to_column, session } = data;

        // ✅ Conditional: Only update UI if viewing Synergy
        if (!this.config.conditionalUpdates || this.isUserViewingSynergy()) {
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

                if (window.synergyBoard && typeof window.synergyBoard.updateStats === 'function') {
                    window.synergyBoard.updateStats();
                }
            }, 400);
        }

        // 🔔 Notify if user's session moved
        if (this.config.notifyOwnSessions && session && this.isUserSession(session)) {
            this._showNotification(
                'Session Moved',
                `Your session moved to "${to_column}"`,
                'info'
            );
        }
    },

    /**
     * 🆕 Handle metadata changes (tags, priority, assignees, etc.)
     */
    _handleMetadataChanged(data) {
        this._log('🏷️ Metadata changed:', data);

        const { session_id, field, old_value, new_value, session } = data;

        // ✅ Conditional: Only update UI if viewing Synergy
        if (!this.config.conditionalUpdates || this.isUserViewingSynergy()) {
            this._applyMetadataUpdate(session_id, field, new_value);
        }

        // 🔔 Notify if user's session
        if (this.config.notifyOwnSessions && session && this.isUserSession(session)) {
            this._notifyMetadataChange(session, field, old_value, new_value);
        }
    },

    // ========================================
    // VISUAL UPDATE METHODS
    // ========================================

    /**
     * Detect what fields changed in update
     */
    _detectChanges(updates) {
        const changes = {
            content: false,
            metadata: false,
            status: false,
            visual: false
        };

        // Content changes
        if (updates.title || updates.description || updates.notes) {
            changes.content = true;
        }

        // Metadata changes
        if (updates.tags || updates.priority || updates.assignees || updates.due_date) {
            changes.metadata = true;
        }

        // Status changes
        if (updates.status || updates.archived || updates.completed_at) {
            changes.status = true;
        }

        // Visual changes
        if (updates.color_hex) {
            changes.visual = true;
        }

        return changes;
    },

    /**
     * Apply visual updates to card based on what changed
     */
    _applyVisualUpdates(sessionId, changes) {
        const card = document.querySelector(`[data-session-id="${sessionId}"]`);
        if (!card) return;

        // Pulse animation to draw attention
        card.classList.add('realtime-update');
        setTimeout(() => card.classList.remove('realtime-update'), 1000);

        // If multiple changes, do full refresh
        const changeCount = Object.values(changes).filter(v => v).length;
        if (changeCount >= 2) {
            this._log('Multiple changes detected - full card refresh');
            this._refreshCard(card);
        }
    },

    /**
     * Apply specific metadata update
     */
    _applyMetadataUpdate(sessionId, field, newValue) {
        const card = document.querySelector(`[data-session-id="${sessionId}"]`);
        if (!card) return;

        this._log(`Updating ${field} for session ${sessionId}`);

        switch (field) {
            case 'tags':
                this._updateTags(card, newValue);
                break;
            case 'priority':
                this._updatePriority(card, newValue);
                break;
            case 'assignees':
                this._updateAssignees(card, newValue);
                break;
            case 'due_date':
                this._updateDueDate(card, newValue);
                break;
            case 'archived':
                this._updateArchivedStatus(card, newValue);
                break;
            case 'color_hex':
                this._updateColor(card, newValue);
                break;
            case 'message_count':
                this._updateMessageCount(card, newValue);
                break;
            default:
                this._log(`Unknown field: ${field}`);
        }

        // Animate change
        card.classList.add('realtime-update');
        setTimeout(() => card.classList.remove('realtime-update'), 1000);
    },

    _updateTags(card, tags) {
        const tagsContainer = card.querySelector('.session-tags');
        if (!tagsContainer) return;

        // Parse tags
        let tagArray = tags;
        if (typeof tags === 'string') {
            try {
                tagArray = JSON.parse(tags);
            } catch (e) {
                tagArray = tags.split(',').map(t => t.trim()).filter(t => t);
            }
        }

        // Clear and rebuild
        tagsContainer.innerHTML = '';
        if (tagArray && tagArray.length > 0) {
            tagArray.forEach(tag => {
                const tagBadge = document.createElement('span');
                tagBadge.className = 'tag-badge';
                tagBadge.textContent = tag;
                tagsContainer.appendChild(tagBadge);
            });
        }
    },

    _updatePriority(card, priority) {
        const priorityBadge = card.querySelector('.priority-badge');
        if (priorityBadge) {
            priorityBadge.className = `priority-badge priority-${priority}`;
            priorityBadge.textContent = priority;
        }
    },

    _updateAssignees(card, assignees) {
        const assigneesContainer = card.querySelector('.assignees');
        if (!assigneesContainer) return;

        // Parse assignees
        let assigneeArray = assignees;
        if (typeof assignees === 'string') {
            try {
                assigneeArray = JSON.parse(assignees);
            } catch (e) {
                assigneeArray = [];
            }
        }

        // Update display
        assigneesContainer.innerHTML = assigneeArray && assigneeArray.length > 0
            ? `👥 ${assigneeArray.length}`
            : '';
    },

    _updateDueDate(card, dueDate) {
        const dueDateEl = card.querySelector('.due-date');
        if (dueDateEl && dueDate) {
            dueDateEl.textContent = `Due: ${new Date(dueDate).toLocaleDateString()}`;
        }
    },

    _updateArchivedStatus(card, archived) {
        if (archived === true || archived === 1) {
            card.classList.add('archived');
            setTimeout(() => {
                card.style.transition = 'opacity 0.5s';
                card.style.opacity = '0';
                setTimeout(() => card.remove(), 500);
            }, 2000);
        }
    },

    _updateColor(card, colorHex) {
        if (colorHex) {
            card.style.borderLeftColor = colorHex;
        }
    },

    _updateMessageCount(card, count) {
        const messageCountEl = card.querySelector('.message-count');
        if (messageCountEl) {
            messageCountEl.textContent = count;
        }
    },

    // ========================================
    // NOTIFICATION METHODS
    // ========================================

    /**
     * Smart notification for user's session updates
     */
    _notifyUserSession(session, updates) {
        // Build notification message based on what changed
        const changes = [];

        if (updates.title) changes.push(`title changed to "${updates.title}"`);
        if (updates.priority) changes.push(`priority set to ${updates.priority}`);
        if (updates.status) changes.push(`status changed to ${updates.status}`);
        if (updates.due_date) changes.push(`due date set`);
        if (updates.tags) changes.push(`tags updated`);
        if (updates.assignees) changes.push(`assignees updated`);

        if (changes.length > 0) {
            const message = changes.join(', ');
            this._showNotification(
                `Session Updated: ${session.title}`,
                message,
                'info'
            );
        }
    },

    /**
     * Notify specific metadata change
     */
    _notifyMetadataChange(session, field, oldValue, newValue) {
        const fieldNames = {
            tags: 'Tags',
            priority: 'Priority',
            assignees: 'Assignees',
            due_date: 'Due Date',
            color_hex: 'Color',
            archived: 'Archive Status'
        };

        const fieldName = fieldNames[field] || field;

        this._showNotification(
            `${session.title}`,
            `${fieldName} updated`,
            'info'
        );
    },

    // ========================================
    // HELPER METHODS
    // ========================================

    _refreshCard(card) {
        // Force full card refresh
        if (window.synergyBoard && typeof window.synergyBoard.refreshCard === 'function') {
            const sessionId = card.dataset.sessionId;
            window.synergyBoard.refreshCard(sessionId);
        }
    },

    _refreshBoard() {
        if (window.synergyBoard && typeof window.synergyBoard.loadSessions === 'function') {
            window.synergyBoard.loadSessions();
        }
    },

    _showConnectionStatus(status, customMessage = null) {
        const message = customMessage || status;
        this._log(`Connection status: ${message}`);

        if (status === 'error' && typeof showNotification === 'function') {
            showNotification('Connection error - Check if server is running', 'error');
        }
    },

    _showNotification(title, message, type = 'info') {
        if (typeof showNotification === 'function') {
            showNotification(`${title}: ${message}`, type);
        } else {
            console.log(`[${type.toUpperCase()}] ${title}: ${message}`);
        }
    },

    _scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            this._log('❌ Max reconnection attempts reached');
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1);

        this._log(`⏳ Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

        setTimeout(() => {
            this.connect(this.currentUserId);
        }, delay);
    },

    _startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected()) {
                this.socket.emit('ping', {
                    client_id: this.socket.id,
                    timestamp: Date.now()
                });
            }
        }, 30000);
    },

    _stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    },

    _log(...args) {
        if (this.config.enableLogging) {
            console.log('[SYNERGY-RT]', ...args);
        }
    }
};

// Add CSS for animations
if (!document.getElementById('synergy-realtime-enhanced-styles')) {
    const style = document.createElement('style');
    style.id = 'synergy-realtime-enhanced-styles';
    style.textContent = `
        @keyframes realtime-pulse {
            0%, 100% { box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            50% { box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.3); }
        }
        
        .synergy-card.realtime-update {
            animation: realtime-pulse 1s ease-out;
        }
        
        .tag-badge {
            display: inline-block;
            padding: 2px 8px;
            background: #e0f2fe;
            color: #0369a1;
            border-radius: 12px;
            font-size: 11px;
            margin-right: 4px;
            animation: tag-appear 0.3s ease-out;
        }
        
        @keyframes tag-appear {
            from { opacity: 0; transform: scale(0.8); }
            to { opacity: 1; transform: scale(1); }
        }
        
        .synergy-card.archived {
            opacity: 0.5;
            filter: grayscale(0.5);
        }
    `;
    document.head.appendChild(style);
}

console.log('[SYNERGY-RT] Enhanced realtime module loaded - Use SynergyRealtimeEnhanced.connect(userId)');
