/**
 * Enhanced Toast Notification System
 * - Stays open until closed
 * - Quick reply functionality
 * - Quick reaction buttons (thumbs up, check, etc.)
 * - Integrates with notification sidebar
 * - Bottom-left positioning
 */

window.EnhancedToast = {
    toasts: new Map(), // Track active toasts by message_id
    reactionIcons: {
        thumbs_up: 'fa-thumbs-up',
        thumbs_down: 'fa-thumbs-down',
        check: 'fa-check',
        question: 'fa-question',
        heart: 'fa-heart',
        star: 'fa-star',
        fire: 'fa-fire',
        rocket: 'fa-rocket'
    },

    /**
     * Show message toast notification
     * @param {Object} messageData - Message data from WebSocket
     * @param {String} messageData.from_user_name - Sender name
     * @param {String} messageData.message - Message text
     * @param {String} messageData.from_user_id - Sender ID
     * @param {String} messageData.from_session_token - Sender session
     * @param {String} messageData.message_id - Unique message ID
     * @param {String} type - 'direct' or 'broadcast'
     */
    showMessageToast(messageData, type = 'direct') {
        const messageId = messageData.message_id || this._generateMessageId();
        const container = this._getToastContainer();

        // Don't show duplicate toasts
        if (this.toasts.has(messageId)) {
            return;
        }

        const toast = document.createElement('div');
        toast.className = `enhanced-toast ${type}-message`;
        toast.setAttribute('data-message-id', messageId);

        const icon = type === 'direct' ? 'fa-envelope' : 'fa-bullhorn';
        const title = type === 'direct' ? 'Direct Message' : 'Broadcast';

        toast.innerHTML = `
            <div class="toast-header">
                <div class="toast-icon">
                    <i class="fas ${icon}"></i>
                </div>
                <div class="toast-title">
                    <strong>${title}</strong> from ${messageData.from_user_name}
                </div>
                <button class="toast-close" onclick="EnhancedToast.closeToast('${messageId}')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="toast-body">
                <div class="toast-message">${this._escapeHtml(messageData.message)}</div>
            </div>
            <div class="toast-actions">
                <div class="toast-quick-reactions">
                    ${this._renderQuickReactions(messageId, messageData)}
                </div>
                <button class="toast-reply-toggle" onclick="EnhancedToast.toggleReply('${messageId}')">
                    <i class="fas fa-reply"></i> Reply
                </button>
            </div>
            <div class="toast-reply-panel" id="toast-reply-${messageId}" style="display: none;">
                <textarea 
                    class="toast-reply-input" 
                    placeholder="Type your reply..."
                    rows="2"
                    id="reply-input-${messageId}"
                ></textarea>
                <div class="toast-reply-actions">
                    <button class="toast-reply-send" onclick="EnhancedToast.sendReply('${messageId}', ${messageData.from_user_id})">
                        <i class="fas fa-paper-plane"></i> Send
                    </button>
                    <button class="toast-reply-cancel" onclick="EnhancedToast.toggleReply('${messageId}')">
                        Cancel
                    </button>
                </div>
            </div>
        `;

        container.appendChild(toast);
        this.toasts.set(messageId, {
            element: toast,
            data: messageData,
            type: type
        });

        // Animate in
        setTimeout(() => toast.classList.add('toast-show'), 10);

        // Play sound if enabled
        this._playNotificationSound();

        // Add to notification sidebar
        this._addToNotificationSidebar(messageData, type, messageId);

        // Mark message as read (auto-read on display)
        this._markMessageAsRead(messageId);
    },

    /**
     * Render quick reaction buttons
     */
    _renderQuickReactions(messageId, messageData) {
        const commonReactions = ['thumbs_up', 'check', 'heart', 'question'];

        return commonReactions.map(reaction => `
            <button 
                class="quick-reaction-btn" 
                onclick="EnhancedToast.sendReaction('${messageId}', '${reaction}', ${messageData.from_user_id})"
                title="${reaction.replace('_', ' ')}"
            >
                <i class="fas ${this.reactionIcons[reaction]}"></i>
            </button>
        `).join('');
    },

    /**
     * Toggle reply panel
     */
    toggleReply(messageId) {
        const panel = document.getElementById(`toast-reply-${messageId}`);
        const input = document.getElementById(`reply-input-${messageId}`);

        if (panel.style.display === 'none') {
            panel.style.display = 'block';
            setTimeout(() => input.focus(), 100);
        } else {
            panel.style.display = 'none';
            input.value = '';
        }
    },

    /**
     * Send reply message
     */
    sendReply(messageId, targetUserId) {
        const input = document.getElementById(`reply-input-${messageId}`);
        const message = input.value.trim();

        if (!message) {
            return;
        }

        // Send via SynergyRealtime
        if (window.SynergyRealtime && typeof SynergyRealtime.sendDirectMessage === 'function') {
            const sent = SynergyRealtime.sendDirectMessage(targetUserId, message);

            if (sent) {
                // Show confirmation
                this._showMiniToast('Reply sent!', 'success');

                // Close reply panel
                this.toggleReply(messageId);

                // Optionally close the toast
                setTimeout(() => this.closeToast(messageId), 1000);
            } else {
                this._showMiniToast('Failed to send reply', 'error');
            }
        } else {
            console.error('[TOAST] SynergyRealtime not available');
            this._showMiniToast('Messaging not available', 'error');
        }
    },

    /**
     * Send quick reaction
     */
    sendReaction(messageId, reactionType, targetUserId) {
        // Send reaction via WebSocket
        if (window.SynergyRealtime && SynergyRealtime.isConnected()) {
            SynergyRealtime.socket.emit('send_reaction', {
                message_id: messageId,
                reaction_type: reactionType,
                target_user_id: targetUserId,
                sender_user_id: SynergyRealtime._getUserId(),
                sender_user_name: SynergyRealtime._getUserName()
            });

            // Visual feedback
            const btn = event.target.closest('.quick-reaction-btn');
            if (btn) {
                btn.classList.add('reaction-sent');
                setTimeout(() => btn.classList.remove('reaction-sent'), 1000);
            }

            this._showMiniToast(`Reaction sent!`, 'success');
        }
    },

    /**
     * Close toast notification
     */
    closeToast(messageId) {
        const toastData = this.toasts.get(messageId);
        if (!toastData) return;

        const toast = toastData.element;
        toast.classList.remove('toast-show');

        setTimeout(() => {
            toast.remove();
            this.toasts.delete(messageId);
        }, 300);
    },

    /**
     * Close all toasts
     */
    closeAll() {
        this.toasts.forEach((toastData, messageId) => {
            this.closeToast(messageId);
        });
    },

    /**
     * Get or create toast container
     */
    _getToastContainer() {
        let container = document.getElementById('enhanced-toast-container');

        if (!container) {
            container = document.createElement('div');
            container.id = 'enhanced-toast-container';
            container.className = 'enhanced-toast-container';
            document.body.appendChild(container);
        }

        return container;
    },

    /**
     * Add message to notification sidebar
     */
    _addToNotificationSidebar(messageData, type, messageId) {
        // Check if notification sidebar exists
        if (typeof NotificationCenter !== 'undefined' && NotificationCenter.add) {
            NotificationCenter.add({
                type: type === 'direct' ? 'DIRECT_MESSAGE' : 'BROADCAST_MESSAGE',
                message: `${messageData.from_user_name}: ${messageData.message}`,
                metadata: {
                    message_id: messageId,
                    from_user_id: messageData.from_user_id,
                    from_user_name: messageData.from_user_name,
                    timestamp: new Date().toISOString()
                },
                action: () => {
                    // When clicked in sidebar, focus the toast if still open
                    const toast = this.toasts.get(messageId);
                    if (toast) {
                        toast.element.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                        toast.element.classList.add('toast-highlight');
                        setTimeout(() => toast.element.classList.remove('toast-highlight'), 2000);
                    }
                }
            });
        }
    },

    /**
     * Show small confirmation toast
     */
    _showMiniToast(message, type = 'info') {
        if (typeof showNotification === 'function') {
            showNotification(message, type, 2000);
        }
    },

    /**
     * Play notification sound
     */
    _playNotificationSound() {
        try {
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjCV0/LTgjMGHm7A7+OZURQMVK3m7q9YFwxIotfxx2wfCDaO0fPVhzkHImqf7OicTRANUqzn7a5aGAxIn+Hyw20jBjWM0O/Jfy0GImmb5Oebdx8TAAAB');
            audio.volume = 0.3;
            audio.play().catch(() => { }); // Ignore errors if autoplay blocked
        } catch (e) {
            // Silent fail
        }
    },

    /**
     * Generate unique message ID
     */
    _generateMessageId() {
        return 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    },

    /**
     * Escape HTML to prevent XSS
     */
    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// CSS Styles (inject into document)
const toastStyles = document.createElement('style');
toastStyles.textContent = `
    .enhanced-toast-container {
        position: fixed;
        bottom: 20px;
        left: 20px;
        z-index: 10000;
        display: flex;
        flex-direction: column-reverse;
        gap: 12px;
        max-width: 400px;
        pointer-events: none;
    }
    
    .enhanced-toast {
        background: var(--bg-secondary, #2a2a2a);
        border: 1px solid var(--border-default, #444);
        border-radius: 8px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        opacity: 0;
        transform: translateX(-100%);
        transition: all 0.3s ease;
        pointer-events: auto;
        overflow: hidden;
    }
    
    .enhanced-toast.toast-show {
        opacity: 1;
        transform: translateX(0);
    }
    
    .enhanced-toast.toast-highlight {
        border-color: var(--accent-primary, #257bdd);
        box-shadow: 0 4px 16px rgba(37, 123, 221, 0.5);
    }
    
    .enhanced-toast.direct-message {
        border-left: 4px solid #4CAF50;
    }
    
    .enhanced-toast.broadcast-message {
        border-left: 4px solid #FF9800;
    }
    
    .toast-header {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 14px;
        background: var(--bg-tertiary, #1e1e1e);
        border-bottom: 1px solid var(--border-default, #444);
    }
    
    .toast-icon {
        font-size: 18px;
        color: var(--accent-primary, #257bdd);
    }
    
    .toast-title {
        flex: 1;
        font-size: 13px;
        color: var(--text-primary, #e0e0e0);
    }
    
    .toast-title strong {
        font-weight: 600;
        color: var(--text-bright, #fff);
    }
    
    .toast-close {
        background: none;
        border: none;
        color: var(--text-secondary, #999);
        cursor: pointer;
        padding: 4px;
        border-radius: 4px;
        transition: all 0.2s;
    }
    
    .toast-close:hover {
        background: var(--bg-hover, #444);
        color: var(--text-primary, #e0e0e0);
    }
    
    .toast-body {
        padding: 14px;
    }
    
    .toast-message {
        font-size: 14px;
        color: var(--text-primary, #e0e0e0);
        line-height: 1.5;
        word-wrap: break-word;
    }
    
    .toast-actions {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 14px;
        background: var(--bg-tertiary, #1e1e1e);
        border-top: 1px solid var(--border-default, #444);
    }
    
    .toast-quick-reactions {
        display: flex;
        gap: 6px;
        flex: 1;
    }
    
    .quick-reaction-btn {
        background: var(--bg-secondary, #2a2a2a);
        border: 1px solid var(--border-default, #444);
        color: var(--text-secondary, #999);
        border-radius: 4px;
        padding: 6px 10px;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.2s;
    }
    
    .quick-reaction-btn:hover {
        background: var(--bg-hover, #444);
        color: var(--accent-primary, #257bdd);
        border-color: var(--accent-primary, #257bdd);
    }
    
    .quick-reaction-btn.reaction-sent {
        background: var(--accent-primary, #257bdd);
        color: white;
        border-color: var(--accent-primary, #257bdd);
    }
    
    .toast-reply-toggle {
        background: var(--accent-primary, #257bdd);
        border: none;
        color: white;
        border-radius: 4px;
        padding: 6px 12px;
        cursor: pointer;
        font-size: 13px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 6px;
        transition: all 0.2s;
    }
    
    .toast-reply-toggle:hover {
        background: var(--accent-hover, #1e5fb3);
    }
    
    .toast-reply-panel {
        padding: 14px;
        background: var(--bg-primary, #1a1a1a);
        border-top: 1px solid var(--border-default, #444);
    }
    
    .toast-reply-input {
        width: 100%;
        background: var(--bg-secondary, #2a2a2a);
        border: 1px solid var(--border-default, #444);
        color: var(--text-primary, #e0e0e0);
        border-radius: 4px;
        padding: 8px;
        font-size: 13px;
        font-family: inherit;
        resize: vertical;
        margin-bottom: 8px;
    }
    
    .toast-reply-input:focus {
        outline: none;
        border-color: var(--accent-primary, #257bdd);
    }
    
    .toast-reply-actions {
        display: flex;
        gap: 8px;
        justify-content: flex-end;
    }
    
    .toast-reply-send, .toast-reply-cancel {
        padding: 6px 12px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 13px;
        font-weight: 500;
        border: none;
        transition: all 0.2s;
    }
    
    .toast-reply-send {
        background: var(--success-color, #4CAF50);
        color: white;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .toast-reply-send:hover {
        background: var(--success-hover, #45a049);
    }
    
    .toast-reply-cancel {
        background: var(--bg-tertiary, #1e1e1e);
        color: var(--text-secondary, #999);
        border: 1px solid var(--border-default, #444);
    }
    
    .toast-reply-cancel:hover {
        background: var(--bg-hover, #444);
        color: var(--text-primary, #e0e0e0);
    }
`;
document.head.appendChild(toastStyles);

// Add helper methods to EnhancedToast
EnhancedToast._markMessageAsRead = function (messageId) {
    /**
     * Mark message as read via WebSocket
     * Called automatically when toast is displayed
     */
    if (!messageId) return;

    if (window.SynergyRealtime && SynergyRealtime.isConnected()) {
        const userId = SynergyRealtime._getUserId();
        if (userId) {
            SynergyRealtime.socket.emit('mark_message_read', {
                message_id: messageId,
                user_id: userId
            });

            console.log(`[TOAST] Marked message ${messageId} as read`);
        }
    }
};

console.log('[ENHANCED TOAST] Loaded - Use EnhancedToast.showMessageToast()');
