/**
 * FILE: UI/modules/threads/components/message_store.js
 * PURPOSE: Centralized message storage with duplicate detection and caching
 * 
 * EXPORTS:
 * - MessageStore (class instance) - Singleton message store
 * 
 * DEPENDENCIES:
 * - None (standalone)
 * 
 * LAST MODIFIED: 2025-11-20 - Extracted from thread_manager_additional.js
 */

class MessageStore {
    constructor() {
        this._messages = new Map(); // threadId -> Message[]
        this._messageIndex = new Map(); // messageId -> Message
        this._realtimeEnabled = false;  // Track if real-time is active
        console.log('[MessageStore] Initialized (real-time ready v2)');
    }

    async addMessage(threadId, message, options = {}) {
        const {
            checkDuplicates = true,
            syncToBackend = false,
            silent = false
        } = options;

        const normalizedContent = this._normalizeContent(message.content);

        if (checkDuplicates) {
            const existingMessages = this._messages.get(threadId) || [];
            const recentMessages = existingMessages.slice(-20);

            for (const existing of recentMessages) {
                const existingNormalized = this._normalizeContent(existing.content);

                if (existingNormalized === normalizedContent && existing.role === message.role) {
                    if (!silent) {
                        console.warn(
                            `[MessageStore] DUPLICATE PREVENTED: Message already exists in thread ${threadId}`,
                            `Existing ID: ${existing.id}`
                        );
                    }
                    // Mark as duplicate so caller can skip DOM creation
                    return { ...existing, _isDuplicate: true };
                }
            }
        }

        if (!message.id) {
            message.id = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        }

        if (!message.created_at) {
            message.created_at = new Date().toISOString();
        }

        if (!this._messages.has(threadId)) {
            this._messages.set(threadId, []);
        }
        this._messages.get(threadId).push(message);
        this._messageIndex.set(message.id, message);

        if (!silent) {
            console.log(`[MessageStore] Message added: ${message.id} to thread ${threadId}`);
        }

        this._emitChange('message-added', { threadId, message });

        return message;
    }

    getMessages(threadId) {
        return this._messages.get(threadId) || [];
    }

    getMessage(messageId) {
        return this._messageIndex.get(messageId);
    }

    getMessageCount(threadId) {
        const messages = this._messages.get(threadId);
        return messages ? messages.length : 0;
    }

    clearThread(threadId) {
        const messages = this._messages.get(threadId) || [];

        for (const msg of messages) {
            this._messageIndex.delete(msg.id);
        }

        this._messages.delete(threadId);

        console.log(`[MessageStore] Cleared ${messages.length} messages from thread ${threadId}`);
    }

    _normalizeContent(content) {
        if (typeof content === 'string') {
            return content.replace(/\s+/g, ' ').trim();
        }

        if (Array.isArray(content)) {
            const textParts = [];
            for (const item of content) {
                if (typeof item === 'object' && item.text) {
                    textParts.push(item.text);
                } else if (typeof item === 'string') {
                    textParts.push(item);
                }
            }
            return textParts.join(' ').replace(/\s+/g, ' ').trim();
        }

        if (typeof content === 'object') {
            return JSON.stringify(content);
        }

        return String(content);
    }

    _emitChange(eventType, data) {
        const event = new CustomEvent('messagestore-change', {
            detail: { type: eventType, ...data }
        });
        window.dispatchEvent(event);
    }

    getStats() {
        return {
            totalThreads: this._messages.size,
            totalMessages: this._messageIndex.size,
            threads: Array.from(this._messages.entries()).map(([threadId, messages]) => ({
                threadId,
                messageCount: messages.length
            }))
        };
    }

    clearAll() {
        this._messages.clear();
        this._messageIndex.clear();
        console.log('[MessageStore] All data cleared');
    }

    /**
     * ✅ NEW: Enable real-time synchronization
     * Called when Supabase real-time subscriptions are active
     */
    enableRealtime() {
        this._realtimeEnabled = true;
        console.log('[MessageStore] ✅ Real-time synchronization ENABLED (multi-session mode)');
    }

    /**
     * ✅ NEW: Disable real-time (fallback to local-only)
     */
    disableRealtime() {
        this._realtimeEnabled = false;
        console.log('[MessageStore] ⚠️ Real-time synchronization DISABLED (local-only mode)');
    }

    /**
     * ✅ NEW: Check if real-time is enabled
     */
    isRealtimeEnabled() {
        return this._realtimeEnabled;
    }

    /**
     * ✅ NEW: Delete a message (for real-time DELETE events)
     */
    deleteMessage(messageId) {
        const message = this._messageIndex.get(messageId);
        if (!message) {
            console.warn(`[MessageStore] Cannot delete message ${messageId} - not found`);
            return false;
        }

        // Find thread containing this message
        for (const [threadId, messages] of this._messages.entries()) {
            const index = messages.findIndex(m => m.id === messageId);
            if (index !== -1) {
                messages.splice(index, 1);
                this._messageIndex.delete(messageId);
                console.log(`[MessageStore] Deleted message ${messageId} from thread ${threadId}`);
                this._emitChange('message-deleted', { threadId, messageId });
                return true;
            }
        }

        return false;
    }

    /**
     * ✅ NEW: Update an existing message (for real-time UPDATE events)
     */
    updateMessage(messageId, updates) {
        const message = this._messageIndex.get(messageId);
        if (!message) {
            console.warn(`[MessageStore] Cannot update message ${messageId} - not found`);
            return false;
        }

        Object.assign(message, updates);
        console.log(`[MessageStore] Updated message ${messageId}`);

        // Find thread ID for event emission
        for (const [threadId, messages] of this._messages.entries()) {
            if (messages.some(m => m.id === messageId)) {
                this._emitChange('message-updated', { threadId, messageId, updates });
                break;
            }
        }

        return true;
    }
}

// Initialize global MessageStore
window.MessageStore = new MessageStore();
console.log('MessageStore module loaded (real-time ready)');
