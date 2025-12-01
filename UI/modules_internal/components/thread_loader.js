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
     * @param {string} threadId - Thread ID to load messages for
     * @param {number} limit - Max messages to load (default: null = ALL messages, no pagination)
     * @param {number} offset - Messages to skip (default: 0, rarely used)
     * 
     * ✅ DEFAULT BEHAVIOR: Loads ALL messages immediately (limit=null)
     * This prevents user confusion and ensures complete conversation history
     */
    async loadMessagesForThread(threadId, limit = null, offset = 0) {
        try {
            console.log(`[ThreadLoader] Fetching messages for thread ${threadId} (limit: ${limit}, offset: ${offset})...`);

            // Build URL - if limit is null/undefined, don't include it (loads all messages)
            let url = `${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/messages/get?thread_id=${threadId}`;
            if (limit !== null && limit !== undefined) {
                url += `&limit=${limit}&offset=${offset}`;
            }

            const response = await fetch(url);
            
            // ✅ FIX: Handle 500 errors for missing threads
            if (!response.ok) {
                console.warn(`[ThreadLoader] ⚠️ Thread ${threadId} not found or error (${response.status}) - thread may have been deleted`);
                return { 
                    messages: [], 
                    pagination: { total: 0, loaded: 0, hasMore: false, nextOffset: 0 },
                    error: 'THREAD_NOT_FOUND'
                };
            }
            
            const data = await response.json();

            if (data.success && data.data) {
                const messages = data.data.messages || data.data || [];

                // If pagination data exists (paginated request), return it
                if (data.data.total !== undefined) {
                    const paginationInfo = {
                        total: data.data.total,
                        loaded: offset + messages.length,
                        hasMore: data.data.has_more || false,
                        nextOffset: offset + messages.length
                    };
                    console.log(`[ThreadLoader] Loaded ${messages.length} messages (${paginationInfo.loaded}/${paginationInfo.total})`);
                    return { messages, pagination: paginationInfo };
                } else {
                    // No pagination (loaded all messages)
                    console.log(`[ThreadLoader] Loaded ALL ${messages.length} messages`);
                    return { messages, pagination: null };
                }
            } else {
                console.error('[ThreadLoader] Failed to load messages:', data);
                return { messages: [], pagination: { total: 0, loaded: 0, hasMore: false, nextOffset: 0 } };
            }
        } catch (error) {
            console.error('[ThreadLoader] Error loading messages:', error);
            return { messages: [], pagination: { total: 0, loaded: 0, hasMore: false, nextOffset: 0 } };
        }
    },

    /**
     * Load ALL messages for a thread (no pagination)
     */
    async loadAllMessagesForThread(threadId) {
        try {
            console.log(`[ThreadLoader] Fetching ALL messages for thread ${threadId}...`);

            const response = await fetch(
                `${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/messages/get?thread_id=${threadId}`
            );
            const data = await response.json();

            if (data.success && data.data) {
                const messages = data.data.messages || data.data || [];
                console.log(`[ThreadLoader] Loaded ${messages.length} total messages`);
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
     * Save thread metadata AND messages to backend
     * UPDATED: Uses proper sessions.threads + sessions.messages schema
     */
    async saveThreadToBackend(thread) {
        // ⚠️ DEPRECATED (Nov 22, 2025): Backend auto-saves messages after stream
        // This method now only logs - does NOT save to prevent phantom threads
        console.warn('[ThreadLoader] ⚠️ saveThreadToBackend is DEPRECATED');
        console.warn('[ThreadLoader] Backend auto-saves after stream completion');

        if (thread && thread.messages) {
            console.log(`[ThreadLoader] Thread ${thread.id} has ${thread.messages.length} messages (already in database)`);
        }

        // Return success to avoid breaking code
        return true;

        /* DEPRECATED: All save logic removed to prevent phantom threads
        try {
            // Don't try to save empty threads
            if (!thread.messages || thread.messages.length === 0) {
                console.log(`[ThreadLoader] Skipping save for empty thread ${thread.id}`);
                return true;
            }

            const userId = (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1;
            const location = thread.location || 'prime';

            // STEP 1: Ensure thread exists in sessions.threads table using UPSERT
            const upsertResponse = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/upsert`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    thread_id: thread.id,
                    user_id: userId,
                    title: thread.title || thread.name || 'Untitled Thread',
                    location: location,
                    tags: thread.tags || [],
                    synergy_card_id: thread.synergy_card_id
                })
            });

            const upsertData = await upsertResponse.json();
            if (!upsertData.success) {
                console.error('[ThreadLoader] Failed to upsert thread:', upsertData.error);
                return false;
            }

            console.log(`[ThreadLoader] Thread ${thread.id} upserted to database`);

            // STEP 2: Save messages to sessions.messages table
            const saveResult = await this.saveMessagesToBackend(thread);

            if (saveResult) {
                console.log(`[ThreadLoader] Thread saved: ${thread.id} (${thread.messages.length} messages, location: ${location})`);
                return true;
            } else {
                console.error('[ThreadLoader] Failed to save messages');
                return false;
            }
        } catch (error) {
            console.error('[ThreadLoader] Save error:', error);
            return false;
        }
        */
    },

    /**
     * Save messages to backend
     * ⚠️ DEPRECATED: Backend auto-saves messages after stream completion
     * Frontend should NEVER save messages - backend is single source of truth
     */
    async saveMessagesToBackend(thread) {
        console.warn(`[ThreadLoader] ⚠️ saveMessagesToBackend is DEPRECATED`);
        console.warn(`[ThreadLoader] Backend auto-saves messages after stream completion`);
        console.warn(`[ThreadLoader] Frontend should NEVER save messages`);

        if (thread && thread.messages) {
            console.log(`[ThreadLoader] Thread ${thread.id} has ${thread.messages.length} messages (already in database)`);
        }

        // Return success to avoid breaking code that calls this
        return true;

        /* DEPRECATED CODE - Backend now handles message saving
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
        */
    },

    /**
     * Get thread location from Supabase
     */
    async getThreadLocation(threadId) {
        try {
            // Initialize Supabase client if not exists
            // NOTE: SUPABASE_CLIENT is set by SupabaseConnectionManager
            if (!window.SUPABASE_CLIENT) {
                console.warn('[ThreadLoader] Supabase connection manager not initialized yet');
                return null;
            }

            const userId = window.appUserId || 1;

            // Use Flask API instead of direct Supabase (sessions schema not exposed in REST API)
            const apiUrl = window.API_BASE_URL || 'http://localhost:5001';
            const response = await fetch(`${apiUrl}/api/thread-assignments/location/${threadId}?user_id=${userId}`);

            if (!response.ok) {
                console.warn(`[ThreadLoader] API error for thread ${threadId}:`, response.statusText);
                return null;
            }

            const result = await response.json();
            if (result.success && result.location) {
                console.log(`[ThreadLoader] Thread ${threadId} location:`, result.location || 'Prime/unassigned');
                return result.location;
            } else {
                console.warn(`[ThreadLoader] No data found for thread ${threadId}`);
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
