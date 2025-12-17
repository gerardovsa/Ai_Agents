/**
 * CHAT SIDEBAR - WhatsApp-Style Messaging with Voice Calls
 * Modern chat interface with message bubbles, voice calling, and rich interactions
 */

window.ChatSidebar = {
    // State
    isOpen: false,
    currentView: 'chat-list', // 'chat-list', 'conversation', 'call'
    activeConversation: null,
    conversations: new Map(),
    unreadCount: 0,
    
    // Voice call state
    currentCall: null,
    localStream: null,
    remoteStream: null,
    peerConnection: null,
    
    // Configuration
    config: {
        iceServers: [
            { urls: 'stun:stun.l.google.com:19302' },
            { urls: 'stun:stun1.l.google.com:19302' }
        ]
    },
    
    /**
     * Initialize chat sidebar
     */
    init() {
        console.log('[CHAT SIDEBAR] Initializing...');
        
        // Wait for WebSocket connection
        if (typeof SynergyRealtime !== 'undefined' && SynergyRealtime.isConnected()) {
            this.setupWebSocketListeners();
        } else {
            // Retry after WebSocket connects
            setTimeout(() => this.init(), 1000);
            return;
        }
        
        // Load conversation history
        this.loadConversationHistory();
        
        // Setup UI event listeners
        this.setupUIListeners();
        
        console.log('[CHAT SIDEBAR] Initialized');
    },
    
    /**
     * Setup WebSocket event listeners
     */
    setupWebSocketListeners() {
        if (!SynergyRealtime.socket) return;
        
        // Direct messages
        window.addEventListener('synergy:direct_message', (e) => {
            this.handleIncomingMessage(e.detail, 'direct');
        });
        
        // Broadcast messages
        window.addEventListener('synergy:broadcast_message', (e) => {
            this.handleIncomingMessage(e.detail, 'broadcast');
        });
        
        // Typing indicators
        SynergyRealtime.socket.on('user_typing_start', (data) => {
            this.showTypingIndicator(data.user_name, data.user_id);
        });
        
        SynergyRealtime.socket.on('user_typing_stop', (data) => {
            this.hideTypingIndicator(data.user_id);
        });
        
        // Voice call signaling
        SynergyRealtime.socket.on('voice_call_offer', (data) => {
            this.handleCallOffer(data);
        });
        
        SynergyRealtime.socket.on('voice_call_answer', (data) => {
            this.handleCallAnswer(data);
        });
        
        SynergyRealtime.socket.on('voice_call_ice_candidate', (data) => {
            this.handleIceCandidate(data);
        });
        
        SynergyRealtime.socket.on('voice_call_ended', (data) => {
            this.handleCallEnded(data);
        });
        
        // User presence
        SynergyRealtime.socket.on('user_joined', (data) => {
            this.updateOnlineStatus(data.user_id, true);
        });
        
        SynergyRealtime.socket.on('user_session_left', (data) => {
            this.updateOnlineStatus(data.user_id, false);
        });
    },
    
    /**
     * Setup UI event listeners
     */
    setupUIListeners() {
        // Escape key to close sidebar
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                if (this.currentView === 'conversation') {
                    this.showChatList();
                } else {
                    this.close();
                }
            }
        });
        
        // Message input - Enter to send
        const messageInput = document.getElementById('chat-message-input');
        if (messageInput) {
            messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
            
            // Typing indicators
            let typingTimeout;
            messageInput.addEventListener('input', () => {
                if (this.activeConversation) {
                    SynergyRealtime.socket.emit('typing_start', {
                        user_id: SynergyRealtime._getUserId(),
                        user_name: SynergyRealtime._getUserName(),
                        recipient_id: this.activeConversation
                    });
                    
                    clearTimeout(typingTimeout);
                    typingTimeout = setTimeout(() => {
                        SynergyRealtime.socket.emit('typing_stop', {
                            user_id: SynergyRealtime._getUserId(),
                            recipient_id: this.activeConversation
                        });
                    }, 2000);
                }
            });
        }
    },
    
    /**
     * Toggle sidebar open/close
     */
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    },
    
    /**
     * Open sidebar
     */
    open() {
        const sidebar = document.getElementById('chat-sidebar');
        if (!sidebar) return;
        
        sidebar.classList.remove('collapsed');
        this.isOpen = true;
        
        // Load initial data
        this.refreshChatList();
        
        console.log('[CHAT SIDEBAR] Opened');
    },
    
    /**
     * Close sidebar
     */
    close() {
        const sidebar = document.getElementById('chat-sidebar');
        if (!sidebar) return;
        
        sidebar.classList.add('collapsed');
        this.isOpen = false;
        
        // End any active call
        if (this.currentCall) {
            this.endCall();
        }
        
        console.log('[CHAT SIDEBAR] Closed');
    },
    
    /**
     * Show chat list view
     */
    showChatList() {
        this.currentView = 'chat-list';
        document.getElementById('chat-list-view').style.display = 'flex';
        document.getElementById('chat-conversation-view').style.display = 'none';
        document.getElementById('chat-call-view').style.display = 'none';
        this.activeConversation = null;
    },
    
    /**
     * Open conversation with user
     */
    openConversation(userId, userName, userDevice) {
        this.currentView = 'conversation';
        this.activeConversation = userId;
        
        // Update header
        document.getElementById('conv-user-name').textContent = userName;
        document.getElementById('conv-user-device').textContent = userDevice || '';
        
        // Load messages
        this.loadConversationMessages(userId);
        
        // Show conversation view
        document.getElementById('chat-list-view').style.display = 'none';
        document.getElementById('chat-conversation-view').style.display = 'flex';
        
        // Mark messages as read
        this.markConversationRead(userId);
        
        console.log(`[CHAT SIDEBAR] Opened conversation with user ${userId}`);
    },
    
    /**
     * Load conversation messages
     */
    async loadConversationMessages(userId) {
        try {
            const response = await fetch(`/api/messages/history?user_id=${userId}&limit=50`);
            const data = await response.json();
            
            const messagesContainer = document.getElementById('chat-messages-container');
            messagesContainer.innerHTML = '';
            
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(msg => {
                    this.appendMessageBubble(msg);
                });
                
                // Scroll to bottom
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        } catch (error) {
            console.error('[CHAT SIDEBAR] Error loading messages:', error);
        }
    },
    
    /**
     * Append message bubble to conversation
     */
    appendMessageBubble(message) {
        const messagesContainer = document.getElementById('chat-messages-container');
        const currentUserId = SynergyRealtime._getUserId();
        const isSent = message.from_user_id === currentUserId;
        
        const bubble = document.createElement('div');
        bubble.className = `chat-message-bubble ${isSent ? 'sent' : 'received'}`;
        bubble.dataset.messageId = message.message_id;
        
        bubble.innerHTML = `
            <div class="chat-message-content">
                ${this.escapeHtml(message.message)}
            </div>
            <div class="chat-message-meta">
                <span class="chat-message-time">${this.formatTime(message.timestamp)}</span>
                ${isSent ? this.getReadStatus(message) : ''}
            </div>
            <div class="chat-message-actions">
                <button class="chat-msg-action-btn" onclick="ChatSidebar.copyMessage('${message.message_id}')" title="Copy">
                    <i class="fas fa-copy"></i>
                </button>
                <button class="chat-msg-action-btn" onclick="ChatSidebar.replyToMessage('${message.message_id}')" title="Reply">
                    <i class="fas fa-reply"></i>
                </button>
                ${isSent ? `
                    <button class="chat-msg-action-btn" onclick="ChatSidebar.deleteMessage('${message.message_id}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                ` : ''}
            </div>
        `;
        
        messagesContainer.appendChild(bubble);
    },
    
    /**
     * Get read status icon
     */
    getReadStatus(message) {
        if (!message.delivered_to || message.delivered_to.length === 0) {
            return '<i class="fas fa-clock chat-msg-status pending"></i>';
        } else if (!message.read_by || message.read_by.length === 0) {
            return '<i class="fas fa-check chat-msg-status delivered"></i>';
        } else {
            return '<i class="fas fa-check-double chat-msg-status read"></i>';
        }
    },
    
    /**
     * Send message
     */
    sendMessage() {
        const input = document.getElementById('chat-message-input');
        const message = input.value.trim();
        
        if (!message || !this.activeConversation) return;
        
        // Send via WebSocket
        SynergyRealtime.sendDirectMessage(this.activeConversation, message);
        
        // Add to UI immediately (optimistic update)
        const messageData = {
            message_id: `temp_${Date.now()}`,
            from_user_id: SynergyRealtime._getUserId(),
            to_user_id: this.activeConversation,
            message: message,
            timestamp: new Date().toISOString(),
            delivered_to: [],
            read_by: []
        };
        
        this.appendMessageBubble(messageData);
        
        // Clear input
        input.value = '';
        input.style.height = 'auto';
        
        // Scroll to bottom
        const container = document.getElementById('chat-messages-container');
        container.scrollTop = container.scrollHeight;
    },
    
    /**
     * Copy message text
     */
    copyMessage(messageId) {
        const bubble = document.querySelector(`[data-message-id="${messageId}"]`);
        if (!bubble) return;
        
        const messageText = bubble.querySelector('.chat-message-content').textContent;
        
        navigator.clipboard.writeText(messageText).then(() => {
            // Show toast
            if (typeof EnhancedToast !== 'undefined') {
                EnhancedToast.show('Message copied to clipboard', 'success', 2000);
            }
        }).catch(err => {
            console.error('[CHAT SIDEBAR] Copy failed:', err);
        });
    },
    
    /**
     * Reply to message
     */
    replyToMessage(messageId) {
        const bubble = document.querySelector(`[data-message-id="${messageId}"]`);
        if (!bubble) return;
        
        const messageText = bubble.querySelector('.chat-message-content').textContent;
        const input = document.getElementById('chat-message-input');
        
        // Add reply context
        input.value = `> ${messageText.substring(0, 50)}${messageText.length > 50 ? '...' : ''}\n\n`;
        input.focus();
    },
    
    /**
     * Delete message
     */
    async deleteMessage(messageId) {
        if (!confirm('Delete this message?')) return;
        
        try {
            const response = await fetch(`/api/messages/${messageId}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (response.ok) {
                // Remove from UI
                const bubble = document.querySelector(`[data-message-id="${messageId}"]`);
                if (bubble) {
                    bubble.remove();
                }
            }
        } catch (error) {
            console.error('[CHAT SIDEBAR] Error deleting message:', error);
        }
    },
    
    /**
     * Handle incoming message
     */
    handleIncomingMessage(messageData, type) {
        console.log('[CHAT SIDEBAR] Incoming message:', messageData);
        
        // If conversation is open and message is from active user, append it
        if (this.activeConversation === messageData.from_user_id) {
            this.appendMessageBubble(messageData);
            
            // Scroll to bottom
            const container = document.getElementById('chat-messages-container');
            container.scrollTop = container.scrollHeight;
            
            // Mark as read
            this.markMessageRead(messageData.message_id);
        } else {
            // Update unread count
            this.unreadCount++;
            this.updateUnreadBadge();
        }
        
        // Refresh chat list
        this.refreshChatList();
    },
    
    /**
     * Mark message as read
     */
    markMessageRead(messageId) {
        if (SynergyRealtime.isConnected()) {
            SynergyRealtime.socket.emit('mark_message_read', {
                message_id: messageId,
                user_id: SynergyRealtime._getUserId()
            });
        }
    },
    
    /**
     * Mark entire conversation as read
     */
    async markConversationRead(userId) {
        try {
            await fetch('/api/messages/mark-read', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId })
            });
            
            this.updateUnreadBadge();
        } catch (error) {
            console.error('[CHAT SIDEBAR] Error marking conversation read:', error);
        }
    },
    
    /**
     * Update unread badge
     */
    updateUnreadBadge() {
        const badge = document.getElementById('chat-unread-badge');
        if (badge) {
            badge.textContent = this.unreadCount;
            badge.style.display = this.unreadCount > 0 ? 'block' : 'none';
        }
    },
    
    /**
     * Refresh chat list
     */
    async refreshChatList() {
        try {
            const response = await fetch('/api/messages/conversations');
            const data = await response.json();
            
            const listContainer = document.getElementById('chat-list-container');
            listContainer.innerHTML = '';
            
            if (data.conversations && data.conversations.length > 0) {
                data.conversations.forEach(conv => {
                    this.appendChatListItem(conv);
                });
            } else {
                listContainer.innerHTML = `
                    <div class="chat-empty-state">
                        <i class="fas fa-comments"></i>
                        <p>No conversations yet</p>
                        <p class="chat-empty-hint">Start chatting with online users</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('[CHAT SIDEBAR] Error loading conversations:', error);
        }
    },
    
    /**
     * Append chat list item
     */
    appendChatListItem(conversation) {
        const listContainer = document.getElementById('chat-list-container');
        
        const item = document.createElement('div');
        item.className = `chat-list-item ${conversation.unread_count > 0 ? 'unread' : ''}`;
        item.onclick = () => this.openConversation(
            conversation.user_id,
            conversation.user_name,
            conversation.device
        );
        
        item.innerHTML = `
            <div class="chat-list-avatar">
                <img src="/api/user/avatar/${conversation.user_id}" alt="${conversation.user_name}">
                <span class="chat-online-indicator ${conversation.is_online ? 'online' : ''}"></span>
            </div>
            <div class="chat-list-info">
                <div class="chat-list-header">
                    <span class="chat-list-name">${this.escapeHtml(conversation.user_name)}</span>
                    <span class="chat-list-time">${this.formatTime(conversation.last_message_time)}</span>
                </div>
                <div class="chat-list-preview">
                    <span class="chat-list-last-message">${this.escapeHtml(conversation.last_message || 'No messages')}</span>
                    ${conversation.unread_count > 0 ? `<span class="chat-unread-count">${conversation.unread_count}</span>` : ''}
                </div>
            </div>
        `;
        
        listContainer.appendChild(item);
    },
    
    /**
     * Load conversation history from database
     */
    async loadConversationHistory() {
        try {
            const response = await fetch('/api/messages/all-conversations');
            const data = await response.json();
            
            if (data.conversations) {
                this.conversations = new Map(
                    data.conversations.map(c => [c.user_id, c])
                );
            }
        } catch (error) {
            console.error('[CHAT SIDEBAR] Error loading conversation history:', error);
        }
    },
    
    // ==================== VOICE CALLING ====================
    
    /**
     * Start voice call
     */
    async startVoiceCall() {
        if (!this.activeConversation) return;
        
        try {
            // Get user media
            this.localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Create peer connection
            this.peerConnection = new RTCPeerConnection(this.config);
            
            // Add local stream
            this.localStream.getTracks().forEach(track => {
                this.peerConnection.addTrack(track, this.localStream);
            });
            
            // Handle ICE candidates
            this.peerConnection.onicecandidate = (event) => {
                if (event.candidate) {
                    SynergyRealtime.socket.emit('voice_call_ice_candidate', {
                        to_user_id: this.activeConversation,
                        candidate: event.candidate
                    });
                }
            };
            
            // Handle remote stream
            this.peerConnection.ontrack = (event) => {
                this.remoteStream = event.streams[0];
                const remoteAudio = document.getElementById('chat-remote-audio');
                if (remoteAudio) {
                    remoteAudio.srcObject = this.remoteStream;
                }
            };
            
            // Create offer
            const offer = await this.peerConnection.createOffer();
            await this.peerConnection.setLocalDescription(offer);
            
            // Send offer
            SynergyRealtime.socket.emit('voice_call_offer', {
                to_user_id: this.activeConversation,
                offer: offer
            });
            
            // Show call UI
            this.showCallUI('outgoing');
            
            console.log('[CHAT SIDEBAR] Voice call started');
            
        } catch (error) {
            console.error('[CHAT SIDEBAR] Error starting call:', error);
            alert('Could not access microphone. Please check permissions.');
        }
    },
    
    /**
     * Handle incoming call offer
     */
    async handleCallOffer(data) {
        // Show incoming call UI
        const accept = confirm(`Incoming call from ${data.from_user_name}. Accept?`);
        
        if (!accept) {
            // Reject call
            SynergyRealtime.socket.emit('voice_call_ended', {
                to_user_id: data.from_user_id,
                reason: 'rejected'
            });
            return;
        }
        
        try {
            // Get user media
            this.localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Create peer connection
            this.peerConnection = new RTCPeerConnection(this.config);
            
            // Add local stream
            this.localStream.getTracks().forEach(track => {
                this.peerConnection.addTrack(track, this.localStream);
            });
            
            // Handle ICE candidates
            this.peerConnection.onicecandidate = (event) => {
                if (event.candidate) {
                    SynergyRealtime.socket.emit('voice_call_ice_candidate', {
                        to_user_id: data.from_user_id,
                        candidate: event.candidate
                    });
                }
            };
            
            // Handle remote stream
            this.peerConnection.ontrack = (event) => {
                this.remoteStream = event.streams[0];
                const remoteAudio = document.getElementById('chat-remote-audio');
                if (remoteAudio) {
                    remoteAudio.srcObject = this.remoteStream;
                }
            };
            
            // Set remote description
            await this.peerConnection.setRemoteDescription(new RTCSessionDescription(data.offer));
            
            // Create answer
            const answer = await this.peerConnection.createAnswer();
            await this.peerConnection.setLocalDescription(answer);
            
            // Send answer
            SynergyRealtime.socket.emit('voice_call_answer', {
                to_user_id: data.from_user_id,
                answer: answer
            });
            
            // Show call UI
            this.activeConversation = data.from_user_id;
            this.showCallUI('incoming');
            
            console.log('[CHAT SIDEBAR] Call accepted');
            
        } catch (error) {
            console.error('[CHAT SIDEBAR] Error accepting call:', error);
        }
    },
    
    /**
     * Handle call answer
     */
    async handleCallAnswer(data) {
        try {
            await this.peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer));
            console.log('[CHAT SIDEBAR] Call connected');
            this.updateCallUI('connected');
        } catch (error) {
            console.error('[CHAT SIDEBAR] Error handling call answer:', error);
        }
    },
    
    /**
     * Handle ICE candidate
     */
    async handleIceCandidate(data) {
        try {
            await this.peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));
        } catch (error) {
            console.error('[CHAT SIDEBAR] Error adding ICE candidate:', error);
        }
    },
    
    /**
     * End voice call
     */
    endCall() {
        // Stop local stream
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
            this.localStream = null;
        }
        
        // Close peer connection
        if (this.peerConnection) {
            this.peerConnection.close();
            this.peerConnection = null;
        }
        
        // Notify other user
        if (this.activeConversation) {
            SynergyRealtime.socket.emit('voice_call_ended', {
                to_user_id: this.activeConversation,
                reason: 'ended'
            });
        }
        
        // Hide call UI
        this.hideCallUI();
        
        console.log('[CHAT SIDEBAR] Call ended');
    },
    
    /**
     * Handle call ended
     */
    handleCallEnded(data) {
        this.endCall();
        alert(`Call ended: ${data.reason}`);
    },
    
    /**
     * Show call UI
     */
    showCallUI(type) {
        document.getElementById('chat-conversation-view').style.display = 'none';
        const callView = document.getElementById('chat-call-view');
        callView.style.display = 'flex';
        
        document.getElementById('chat-call-status').textContent = 
            type === 'outgoing' ? 'Calling...' : 'Call connected';
    },
    
    /**
     * Update call UI
     */
    updateCallUI(status) {
        const statusText = {
            'connecting': 'Connecting...',
            'connected': 'Call connected',
            'ended': 'Call ended'
        };
        
        document.getElementById('chat-call-status').textContent = statusText[status] || status;
    },
    
    /**
     * Hide call UI
     */
    hideCallUI() {
        document.getElementById('chat-call-view').style.display = 'none';
        document.getElementById('chat-conversation-view').style.display = 'flex';
    },
    
    /**
     * Toggle mute
     */
    toggleMute() {
        if (!this.localStream) return;
        
        const audioTrack = this.localStream.getAudioTracks()[0];
        if (audioTrack) {
            audioTrack.enabled = !audioTrack.enabled;
            const muteBtn = document.getElementById('chat-mute-btn');
            muteBtn.innerHTML = audioTrack.enabled 
                ? '<i class="fas fa-microphone"></i>' 
                : '<i class="fas fa-microphone-slash"></i>';
        }
    },
    
    // ==================== UTILITY FUNCTIONS ====================
    
    /**
     * Show typing indicator
     */
    showTypingIndicator(userName, userId) {
        if (this.activeConversation !== userId) return;
        
        const container = document.getElementById('chat-typing-indicator');
        if (container) {
            container.style.display = 'flex';
            container.innerHTML = `
                <span class="chat-typing-text">${this.escapeHtml(userName)} is typing</span>
                <span class="chat-typing-dots">
                    <span>.</span><span>.</span><span>.</span>
                </span>
            `;
        }
    },
    
    /**
     * Hide typing indicator
     */
    hideTypingIndicator(userId) {
        if (this.activeConversation !== userId) return;
        
        const container = document.getElementById('chat-typing-indicator');
        if (container) {
            container.style.display = 'none';
        }
    },
    
    /**
     * Update online status
     */
    updateOnlineStatus(userId, isOnline) {
        const indicator = document.querySelector(`[data-user-id="${userId}"] .chat-online-indicator`);
        if (indicator) {
            indicator.classList.toggle('online', isOnline);
        }
    },
    
    /**
     * Format timestamp
     */
    formatTime(timestamp) {
        if (!timestamp) return '';
        
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        // Less than 1 minute
        if (diff < 60000) {
            return 'Just now';
        }
        
        // Less than 1 hour
        if (diff < 3600000) {
            const mins = Math.floor(diff / 60000);
            return `${mins}m ago`;
        }
        
        // Less than 24 hours
        if (diff < 86400000) {
            return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
        }
        
        // Less than 7 days
        if (diff < 604800000) {
            const days = Math.floor(diff / 86400000);
            return `${days}d ago`;
        }
        
        // Older
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    },
    
    /**
     * Escape HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    ChatSidebar.init();
});
