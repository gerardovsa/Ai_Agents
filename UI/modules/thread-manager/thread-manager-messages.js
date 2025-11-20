/**
 * FILE: UI/modules/thread-manager/thread-manager-messages.js
 * PURPOSE: Message handling and streaming for threads
 * 
 * DEPENDENCIES:
 * - UI/modules/thread-manager/thread-manager-core.js (must load first)
 * 
 * EXPORTS:
 * - Extends window.ThreadManager with message methods
 * 
 * USED BY:
 * - UI/business-ai-platform-v2.html (main application)
 * - UI/modules/thread-manager/thread-manager-ui.js (message display)
 * 
 * RELATED FILES:
 * - UI/modules/thread-manager/thread-manager-core.js (core object)
 * - UI/modules/thread-manager/thread-manager-ui.js (UI rendering)
 * 
 * NOTES:
 * - Handles message creation, streaming, and display
 * - Manages real-time message updates
 * - Handles AI response streaming
 * 
 * LAST MODIFIED: 2025-11-20 - Initial file creation
 */

// Message handling methods will be defined here
// Awaiting code paste from user


// ==================== THREAD MANAGER - MESSAGES MODULE ====================
/**
 * Message Management
 * Handles message saving, loading, and synchronization
 * 
 * ARCHITECTURE:
 * - Uses MessageStore for in-memory caching (fast)
 * - Uses ThreadLoader for backend persistence (async)
 * - Deduplication handled by MessageStore
 */

// Extend ThreadManager with message methods
window.ThreadManager = window.ThreadManager || {};
Object.assign(window.ThreadManager, {
    /**
     * Save messages to backend (DELEGATES to ThreadLoader)
     */
    async saveMessagesToBackend(thread) {
        if (!thread || !thread.id) {
            console.error('❌ [Messages] No thread provided');
            return false;
        }

        if (!thread.messages || thread.messages.length === 0) {
            console.log('⏭️ [Messages] Skipping - no messages to save');
            return true;
        }

        console.log(`💾 [Messages] Saving ${thread.messages.length} messages for thread ${thread.id}`);

        // Delegate to ThreadLoader (data layer)
        if (typeof window.ThreadLoader !== 'undefined') {
            const success = await window.ThreadLoader.saveMessagesToBackend(thread);

            if (success) {
                // Update message count
                thread.message_count = thread.messages.length;
                if (typeof this.updateMessageCount === 'function') {
                    this.updateMessageCount(thread.id);
                }
            }

            return success;
        } else {
            console.error('❌ [Messages] ThreadLoader not available');
            return false;
        }
    },



    /**
     * Load messages for a thread from backend (DELEGATES to ThreadLoader)
     */
    async loadMessagesForThread(threadId) {
        console.log(`📥 [Messages] Loading messages for thread ${threadId}...`);

        // Delegate to ThreadLoader (data layer)
        if (typeof window.ThreadLoader !== 'undefined') {
            const messages = await window.ThreadLoader.loadMessagesForThread(threadId);

            // Update thread with loaded messages
            const thread = this.threads.find(t => t.id === threadId);
            if (thread) {
                thread.messages = Array.isArray(messages) ? messages : [];
                thread.message_count = messages.length;

                // Cache in MessageStore for fast access
                if (typeof window.MessageStore !== 'undefined') {
                    messages.forEach(msg => {
                        window.MessageStore.addMessage(threadId, msg, { checkDuplicates: false, silent: true });
                    });
                }
            }

            return messages;
        } else {
            console.error('❌ [Messages] ThreadLoader not available');
            return [];
        }
    },

    /**
     * Save thread metadata to backend (DELEGATES to ThreadLoader)
     */
    async saveThreadToBackend(thread) {
        if (!thread || !thread.id) {
            console.error('❌ [Messages] No thread to save');
            return false;
        }

        // Delegate to ThreadLoader (data layer)
        if (typeof window.ThreadLoader !== 'undefined') {
            return await window.ThreadLoader.saveThreadToBackend(thread);
        } else {
            console.error('❌ [Messages] ThreadLoader not available');
            return false;
        }
    },

    /**
     * Update current thread with new messages
     */
    updateCurrentThread(messages) {
        const thread = this.getCurrentThread();
        if (!thread) {
            console.warn('⚠️ [Messages] No current thread to update');
            return;
        }

        thread.messages = messages;
        thread.updated = new Date().toISOString();
        thread.message_count = messages.length;

        // Update title from first user message if still untitled
        if (messages.length > 0 && (!thread.title || thread.title === 'Untitled Thread' || thread.title.startsWith('thread_'))) {
            const firstUserMsg = messages.find(m => m.role === 'user');
            if (firstUserMsg) {
                const content = typeof firstUserMsg.content === 'string' ?
                    firstUserMsg.content :
                    firstUserMsg.content[0]?.text || '';
                thread.title = content.substring(0, 50) + (content.length > 50 ? '...' : '');
            }
        }

        // Update UI
        if (typeof this.updateMessageCount === 'function') {
            this.updateMessageCount(thread.id);
        }
        if (typeof this.updatePrimeHeader === 'function') {
            this.updatePrimeHeader(thread.id);
        }
        if (typeof this.syncAppState === 'function') {
            this.syncAppState(thread.id);
        }

        // Save to backend (async)
        this.saveMessagesToBackend(thread);
        this.saveThreadToBackend(thread);

        // Refresh UI
        if (typeof this.renderThreadList === 'function') {
            this.renderThreadList();
        }

        console.log(`✅ [Messages] Current thread updated: ${thread.id} (${messages.length} messages)`);
    },

    /**
     * Add message to thread (with MessageStore caching)
     */
    async addMessage(threadId, message) {
        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) {
            console.error('❌ [Messages] Thread not found:', threadId);
            return null;
        }

        // Add to MessageStore (handles deduplication)
        if (typeof window.MessageStore !== 'undefined') {
            const storedMessage = await window.MessageStore.addMessage(threadId, message, {
                checkDuplicates: true,
                silent: false
            });

            // Update thread.messages from MessageStore
            thread.messages = window.MessageStore.getMessages(threadId);
            thread.message_count = thread.messages.length;
            thread.updated = new Date().toISOString();

            // Save to backend (async, non-blocking)
            this.saveMessagesToBackend(thread);

            return storedMessage;
        } else {
            // Fallback: Add directly to thread
            if (!thread.messages) thread.messages = [];
            thread.messages.push(message);
            thread.message_count = thread.messages.length;
            thread.updated = new Date().toISOString();

            // Save to backend
            this.saveMessagesToBackend(thread);

            return message;
        }
    }
});

// Extend ThreadManager with additional message utility methods
Object.assign(window.ThreadManager, {
    /**
     * Add message to thread (legacy compatibility method)
     */
    addMessageToThread(message, threadId = null) {
        const targetThreadId = threadId || this.currentThreadId;
        const thread = this.threads.find(t => t.id === targetThreadId);

        if (!thread) {
            console.warn('⚠️ [Messages] Thread not found:', targetThreadId);
            return false;
        }

        if (!thread.messages) {
            thread.messages = [];
        }

        // Check for duplicates
        const isDuplicate = thread.messages.some(existing => {
            if (existing.role !== message.role) return false;

            const normalizeContent = (content) => {
                if (typeof content === 'string') return content;
                if (Array.isArray(content)) return JSON.stringify(content);
                return JSON.stringify(content);
            };

            return normalizeContent(existing.content) === normalizeContent(message.content);
        });

        if (isDuplicate) {
            console.warn('⚠️ [Messages] Duplicate message prevented');
            return false;
        }

        // Add message
        thread.messages.push(message);
        thread.updated = new Date().toISOString();
        thread.message_count = thread.messages.length;

        // Refresh UI
        if (typeof this.refreshAllThreadInfoCards === 'function') {
            this.refreshAllThreadInfoCards(targetThreadId);
        }

        console.log(`✅ [Messages] Message added to thread ${targetThreadId}`);
        return true;
    },

    /**
     * Create message object
     */
    createMessage(role, content, metadata = {}) {
        return {
            id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            role: role,
            content: content,
            timestamp: new Date().toISOString(),
            metadata: {
                model: metadata.model || null,
                thinking_time: metadata.thinking_time || null,
                tool_calls: metadata.tool_calls || [],
                attachments: metadata.attachments || [],
                ...metadata
            }
        };
    },

    /**
     * Update message count in UI
     */
    updateMessageCount(threadId) {
        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) return;

        // Count messages (exclude thinking blocks)
        let count = 0;
        if (thread.messages && Array.isArray(thread.messages)) {
            const msgs = thread.messages;
            let i = 0;
            while (i < msgs.length) {
                const msg = msgs[i];

                if (msg.role === 'user') {
                    count += 1;
                    i += 1;
                    continue;
                }

                if (msg.role === 'assistant') {
                    let j = i;
                    let hasRealContent = false;
                    while (j < msgs.length && msgs[j].role === 'assistant') {
                        const m = msgs[j];
                        if (Array.isArray(m.content)) {
                            if (m.content.some(block =>
                                block.type === 'text' ||
                                (block.type !== 'thinking' && block.type !== 'redacted_thinking')
                            )) {
                                hasRealContent = true;
                            }
                        } else if (typeof m.content === 'string' && m.content.trim().length > 0) {
                            hasRealContent = true;
                        }
                        j += 1;
                    }

                    if (hasRealContent) count += 1;
                    i = j;
                    continue;
                }

                i += 1;
            }
        } else {
            count = thread.message_count || 0;
        }

        // Update all UI elements showing message count
        const allMetaItems = document.querySelectorAll(`[data-thread-id="${threadId}"] .thread-meta-item[title="Message count"]`);
        allMetaItems.forEach(item => {
            item.innerHTML = `<i class="fas fa-comments"></i> ${count} msgs`;
        });

        console.log(`✅ [Messages] Message count updated: ${count}`);
    },

    /**
     * Sync AppState with current thread
     */
    syncAppState(threadId) {
        const thread = this.threads.find(t => t.id === threadId);

        if (!thread) {
            if (typeof AppState !== 'undefined') {
                AppState.sessionId = null;
                AppState.chatMessages = [];
                AppState.threadTitle = null;
            }
            return;
        }

        if (typeof AppState !== 'undefined') {
            AppState.sessionId = thread.id;
            AppState.chatMessages = [...(thread.messages || [])];
            AppState.threadTitle = thread.title;
            AppState.currentLocation = thread.agent || 'main';
            console.log('✅ [Messages] AppState synced with thread:', thread.id);
        }
    }
});

console.log('✅ ThreadManager-Messages module loaded');