/**
 * FILE: UI/modules/threads/components/thread_loader.js
 * PURPOSE: Thread loading and backend data fetching
 * 
 * EXPORTS:
 * - loadThreadsFromBackend() - Load all threads from database
 * - loadMessagesForThread(threadId) - Load messages for specific thread
 * - saveThreadToBackend(thread) - Save thread metadata
 * - saveMessagesToBackend(thread) - Save thread messages
 * - getThreadLocation(threadId) - Get thread's current location
 * 
 * DEPENDENCIES:
 * - UserAuth (global) - User authentication
 * - window.API_BASE_URL - Backend API base URL
 * 
 * LAST MODIFIED: 2025-11-20 - Extracted from thread_manager.js
 */

const ThreadLoader = {
    /**
     * Load all threads from backend database
     */
    async loadThreadsFromBackend() {
        try {
            const userId = (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1;
            const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/list?user_id=${userId}`);
            const data = await response.json();

            if (data.success && Array.isArray(data.threads)) {
                console.log(`[ThreadLoader] Loaded ${data.threads.length} threads from backend`);
                return data.threads;
            } else {
                console.error('[ThreadLoader] Failed to load threads:', data);
                return [];
            }
        } catch (error) {
            console.error('[ThreadLoader] Error loading threads:', error);
            return [];
        }
    },

    /**
     * Load messages from backend for a specific thread
     */
    async loadMessagesForThread(threadId) {
        try {
            console.log(`[ThreadLoader] Fetching messages for thread ${threadId}...`);

            const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/messages/get?thread_id=${threadId}`);
            const data = await response.json();

            if (data.success && data.data) {
                const messages = data.data.messages || data.data || [];
                console.log(`[ThreadLoader] Loaded ${messages.length} messages`);
                return messages;
            } else {
                console.error('[ThreadLoader] Failed to load messages:', data);
                return [];
            }
        } catch (error) {
            console.error('[ThreadLoader] Error loading messages:', error);
            return [];
        }
    },

    /**
     * Save thread metadata to backend
     */
    async saveThreadToBackend(thread) {
        try {
            // Don't try to save empty threads
            if (!thread.messages || thread.messages.length === 0) {
                console.log(`[ThreadLoader] Skipping save for empty thread ${thread.id}`);
                return true;
            }

            // Determine thread location
            let location = thread.location || 'prime';

            const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1,
                    thread_id: thread.id,
                    name: thread.title || thread.name || 'Untitled Thread',
                    messages: thread.messages || [],
                    agent: thread.agent || 'main',
                    location: location,
                    archived: thread.archived || false
                })
            });

            const data = await response.json();
            if (data.success) {
                console.log(`[ThreadLoader] Thread saved: ${thread.id} (location: ${location})`);
                return true;
            } else {
                console.error('[ThreadLoader] Failed to save thread:', data.error);
                return false;
            }
        } catch (error) {
            console.error('[ThreadLoader] Save error:', error);
            return false;
        }
    },

    /**
     * Save messages to backend
     */
    async saveMessagesToBackend(thread) {
        try {
            if (!thread || !thread.id) {
                console.error('[ThreadLoader] No thread provided');
                return false;
            }

            // Deduplicate message content before saving
            const messages = (thread.messages || []).map(msg => {
                if (msg.role === 'user' && Array.isArray(msg.content)) {
                    const textBlocks = msg.content.filter(b => b && b.type === 'text');
                    const uniqueTexts = [];
                    const seenTexts = new Set();

                    textBlocks.forEach(block => {
                        const text = block.text || block.content || '';
                        if (text && !seenTexts.has(text)) {
                            seenTexts.add(text);
                            uniqueTexts.push({ type: 'text', text });
                        }
                    });

                    const nonTextBlocks = msg.content.filter(b => b && b.type !== 'text');
                    return { ...msg, content: [...uniqueTexts, ...nonTextBlocks] };
                }
                return msg;
            });

            if (messages.length === 0) {
                console.warn(`[ThreadLoader] No messages to save for thread ${thread.id}`);
                return true;
            }

            const userId = (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1;

            const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/messages/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    thread_id: thread.id,
                    user_id: userId,
                    messages: messages.map(msg => ({
                        role: msg.role,
                        content: msg.content,
                        timestamp: msg.timestamp || Date.now(),
                        tool_calls: msg.tool_calls,
                        tokens_used: msg.tokens_used,
                        response_time_ms: msg.response_time_ms,
                        metadata: msg.metadata || {}
                    }))
                })
            });

            const data = await response.json();

            if (data.success) {
                const saved = data.data?.messages_saved || data.messages_saved || 0;
                console.log(`[ThreadLoader] Saved ${saved} messages to thread ${thread.id}`);
                return true;
            } else {
                console.error('[ThreadLoader] Failed to save messages:', data.error || data);
                return false;
            }
        } catch (error) {
            console.error('[ThreadLoader] Error saving messages:', error);
            return false;
        }
    },

    /**
     * Get thread location from backend
     */
    async getThreadLocation(threadId) {
        try {
            const response = await fetch(`/api/thread-assignments/location/${threadId}?user_id=${window.appUserId || 1}`);
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    console.log(`[ThreadLoader] Thread ${threadId} location:`, data.location || 'Prime/unassigned');
                    return data.location;
                } else {
                    console.warn(`[ThreadLoader] API returned success:false for thread ${threadId}`);
                    return null;
                }
            } else {
                console.warn(`[ThreadLoader] Failed to get location for thread ${threadId}: ${response.status}`);
                return null;
            }
        } catch (err) {
            console.error(`[ThreadLoader] Exception:`, err);
            return null;
        }
    }
};

// Make available globally
window.ThreadLoader = ThreadLoader;

console.log('✅ ThreadLoader module loaded');
