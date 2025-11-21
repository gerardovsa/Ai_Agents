/**
 * FILE: UI/modules/thread-manager/thread-manager-assignment.js
 * PURPOSE: CASCADE pattern for agent assignment in ThreadManager
 * 
 * DEPENDENCIES:
 * - UI/modules/thread-manager/thread-manager-core.js (must load first)
 * 
 * EXPORTS:
 * - Extends window.ThreadManager with CASCADE assignment methods
 * 
 * USED BY:
 * - UI/business-ai-platform-v2.html (main application)
 * - UI/modules/thread-manager/thread-manager-ui.js (thread cards)
 * 
 * RELATED FILES:
 * - UI/modules/thread-manager/thread-manager-core.js (core object)
 * - UI/modules/thread-manager/thread-manager-ui.js (UI rendering)
 * 
 * NOTES:
 * - Implements CASCADE pattern for agent assignment
 * - Updated module from previous version
 * - Handles agent selection and assignment flow
 * 
 * LAST MODIFIED: 2025-11-20 - Initial file creation
 */

// ==================== THREAD MANAGER - ASSIGNMENT MODULE ====================
/**
 * Thread Assignment System - CASCADE Pattern
 * Database-first approach prevents UI/DB mismatches
 * From updated version - superior architecture
 */

// Ensure ThreadManager exists before extending
if (typeof window.ThreadManager === 'undefined') {
    console.error('❌ [Assignment] window.ThreadManager not found! Core module must load first.');
    throw new Error('ThreadManager core module not loaded');
}

Object.assign(window.ThreadManager, {
    /**
     * CASCADE PATTERN: Database-First Thread Assignment
     * 
     * CRITICAL RULE: Database ALWAYS updated FIRST, then UI cascades from DB state
     * This prevents UI/DB mismatches where thread appears in two places
     * 
     * Flow: assignThread() → UPDATE DATABASE → _cascadeThreadAssignment() → UPDATE UI
     */
    async assignThread(threadId, location) {
        console.log(`🔄 [Assignment] START: ${threadId} → ${location}`);

        try {
            // Set pending flag to prevent realtime loop
            this.pendingAssignment = true;

            // PHASE 1: UPDATE DATABASE FIRST (single source of truth)
            const response = await fetch(`${this.apiBaseUrl}/api/thread-assignments/assign`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1,
                    session_id: threadId,
                    location: location || 'prime'
                })
            });

            if (!response.ok) {
                throw new Error(`Database update failed: ${response.statusText}`);
            }

            const data = await response.json();
            console.log(`✅ [Assignment] Database updated:`, data.assignment);

            // PHASE 2: CASCADE UI UPDATES (only after DB success)
            await this._cascadeThreadAssignment(threadId, location, data.assignment);

            // Clear pending flag after 500ms
            setTimeout(() => {
                this.pendingAssignment = false;
            }, 500);

            return data;

        } catch (error) {
            this.pendingAssignment = false;
            console.error(`❌ [Assignment] Failed:`, error);
            if (typeof showNotification === 'function') {
                showNotification(`Failed to assign thread: ${error.message}`, 'error', 3000);
            }
            throw error;
        }
    },

    /**
     * CASCADE UI UPDATES: Update UI after database assignment succeeds
     * Handles: clearing old location, updating thread object, rendering new location
     */
    async _cascadeThreadAssignment(threadId, newLocation, assignment) {
        console.log(`🔄 [CASCADE] Starting UI updates for thread ${threadId}`);

        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) {
            console.warn(`[CASCADE] Thread not found: ${threadId}`);
            return;
        }

        // STEP 1: Update thread object FIRST (before clearing UI)
        thread.location = newLocation;
        thread.agent = newLocation === 'prime' ? null : newLocation;
        thread.updated = new Date().toISOString();
        console.log(`✅ [CASCADE] Updated thread object: location=${newLocation}`);

        // STEP 2: Clear OLD location UI (only if location ACTUALLY CHANGED)
        // CRITICAL FIX (Nov 21): Don't clear if previous_location === newLocation
        // This prevents threads from being cleared when re-assigned to same location
        if (assignment.previous_location && assignment.previous_location !== newLocation) {
            console.log(`🧹 [CASCADE] Clearing ${assignment.previous_location} (moved to ${newLocation})`);
            await this._clearLocationUI(assignment.previous_location, threadId);
        } else if (assignment.previous_location === newLocation) {
            console.log(`✅ [CASCADE] Thread ${threadId} staying at ${newLocation}, skipping clear`);
        }

        // STEP 3: Handle DISPLACED thread (if any)
        if (assignment.displaced_thread) {
            console.log(`🔄 [CASCADE] Handling displaced thread: ${assignment.displaced_thread}`);
            const displacedThread = this.threads.find(t => t.id === assignment.displaced_thread);
            if (displacedThread) {
                displacedThread.location = 'prime';
                displacedThread.agent = null;
                displacedThread.updated = new Date().toISOString();
                await this._clearLocationUI(newLocation, assignment.displaced_thread);
            }
        }

        // STEP 4: Update thread-info container in NEW location
        if (newLocation && newLocation.startsWith('agent-')) {
            const agentId = newLocation.replace('agent-', '');
            const threadInfoEl = document.getElementById(`thread-info-${agentId}`);
            if (threadInfoEl && typeof this.renderThreadInfoContainer === 'function') {
                threadInfoEl.innerHTML = this.renderThreadInfoContainer(newLocation, threadId, true);
                console.log(`✅ [CASCADE] Updated thread-info for ${newLocation}`);
            }
        } else if (newLocation === 'prime') {
            const primeThreadInfo = document.getElementById('thread-info-prime');
            if (primeThreadInfo && AppState.sessionId === threadId && typeof this.renderThreadInfoContainer === 'function') {
                primeThreadInfo.innerHTML = this.renderThreadInfoContainer('prime', threadId, false);
                console.log(`✅ [CASCADE] Updated thread-info for Prime`);
            }
        }

        // STEP 5: Refresh UI components
        if (typeof this.renderThreadList === 'function') {
            this.renderThreadList();
        }
        if (typeof this.refreshAllThreadInfoCards === 'function') {
            this.refreshAllThreadInfoCards(threadId);
        }

        console.log(`✅ [CASCADE] Complete for thread ${threadId}`);
    },

    /**
     * CLEAR OLD LOCATION UI: Remove thread from old location
     * Only clears UI if this specific thread is loaded in that location
     */
    async _clearLocationUI(location, threadId) {
        if (location === 'prime') {
            // Clear Prime panel ONLY if this thread is loaded
            if (AppState.sessionId === threadId) {
                AppState.sessionId = null;
                AppState.chatMessages = [];

                const messagesContainer = document.getElementById('ai-chat-messages');
                if (messagesContainer) {
                    messagesContainer.querySelectorAll('[data-processor-initialized]').forEach(bubble => {
                        if (bubble.processor && typeof bubble.processor.cleanup === 'function') {
                            bubble.processor.cleanup();
                        }
                    });
                    messagesContainer.innerHTML = '';
                }

                // Show welcome message
                const welcomeContainer = document.getElementById('prime-welcome-container');
                if (welcomeContainer) welcomeContainer.style.display = 'block';

                // Update Prime header
                const primeThreadInfo = document.getElementById('thread-info-prime');
                if (primeThreadInfo && typeof this.renderThreadInfoContainer === 'function') {
                    primeThreadInfo.innerHTML = this.renderThreadInfoContainer('prime', null, false);
                }

                console.log(`✅ [CASCADE] Cleared Prime UI (thread ${threadId})`);
            }

        } else if (location.startsWith('agent-')) {
            // Clear Agent column
            const agentId = parseInt(location.replace('agent-', ''));

            if (typeof MultiAgent !== 'undefined') {
                const loadedThread = MultiAgent.loadedThreads[agentId];

                // Clear ONLY if this thread is loaded in this agent
                if (loadedThread && loadedThread.threadId === threadId) {
                    MultiAgent.clearLoadedThread(agentId);

                    // Update agent header to show "no thread"
                    const headerEl = document.getElementById(`thread-info-${agentId}`);
                    if (headerEl && typeof this.renderThreadInfoContainer === 'function') {
                        headerEl.innerHTML = this.renderThreadInfoContainer(location, null, true);
                    }

                    console.log(`✅ [CASCADE] Cleared ${location} UI (thread ${threadId})`);
                }
            }
        }
    },

    /**
     * Restore thread assignments from backend
     * Called during app initialization to sync UI with database state
     */
    async restoreThreadAssignments() {
        console.log('🔄 [Assignment] Restoring thread assignments from backend...');
        console.log('📊 [Assignment] Current threads:', this.threads.length);

        try {
            const userId = (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1;
            const response = await fetch(`${this.apiBaseUrl}/api/thread-assignments/list?user_id=${userId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${UserAuth.token}`
                }
            });

            if (!response.ok) {
                throw new Error(`Failed to fetch assignments: ${response.statusText}`);
            }

            const data = await response.json();

            // Handle different response formats
            let assignments = [];
            if (Array.isArray(data)) {
                assignments = data;
            } else if (data && Array.isArray(data.assignments)) {
                assignments = data.assignments;
            } else if (data && data.assignments && typeof data.assignments === 'object') {
                // Handle {assignments: {"agent-1": "session_id"}} format from backend
                console.log('[Assignment] Converting object-based assignments to array');
                assignments = Object.entries(data.assignments).map(([location, session_id]) => ({
                    session_id,
                    location
                }));
            } else if (data && typeof data === 'object') {
                console.warn('[Assignment] Unexpected response format:', data);
                assignments = [];
            }

            console.log(`✅ [Assignment] Restored ${assignments.length} thread assignments`);

            // Update local thread objects with assignment data
            for (const assignment of assignments) {
                const thread = this.threads.find(t => t.id === assignment.session_id);
                if (thread) {
                    thread.location = assignment.location;
                    thread.agent = assignment.location === 'prime' ? null : assignment.location;
                }
            }

            // Wait for MultiAgent to be ready, then load threads
            const loadThreadsIntoAgents = async () => {
                // Check if MultiAgent is ready
                if (typeof MultiAgent === 'undefined' || !MultiAgent.loadThreadIntoAgent) {
                    console.log('⏳ [Assignment] Waiting for MultiAgent to initialize...');
                    setTimeout(loadThreadsIntoAgents, 500);
                    return;
                }

                console.log('✅ [Assignment] MultiAgent ready, loading threads into agents...');

                // Load threads into their assigned locations
                for (const assignment of assignments) {
                    const thread = this.threads.find(t => t.id === assignment.session_id);
                    if (!thread) continue;

                    if (assignment.location && assignment.location.startsWith('agent-')) {
                        const agentId = parseInt(assignment.location.replace('agent-', ''));

                        try {
                            await MultiAgent.loadThreadIntoAgent(agentId, thread);
                            console.log(`✅ [Assignment] Loaded thread "${thread.title}" into agent-${agentId}`);
                        } catch (error) {
                            console.error(`❌ [Assignment] Failed to load thread into agent-${agentId}:`, error);
                        }
                    } else if (assignment.location === 'prime' && assignment.session_id === this.currentThreadId) {
                        // Load into Prime if it's the current thread
                        if (typeof this.loadThreadInPrime === 'function') {
                            await this.loadThreadInPrime(assignment.session_id);
                        }
                    }
                }
            };

            // Start loading threads (async, don't wait)
            loadThreadsIntoAgents();

            return assignments;
        } catch (error) {
            console.error('❌ [Assignment] Failed to restore assignments:', error);
            return [];
        }
    },

    /**
     * Get thread assignments from backend
     */
    async getThreadAssignments() {
        try {
            const userId = (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1;
            const response = await fetch(`${this.apiBaseUrl}/api/thread-assignments/list?user_id=${userId}`);
            const data = await response.json();

            if (data.success && data.assignments) {
                return data.assignments;
            }
            return {};
        } catch (error) {
            console.error('❌ [Assignment] Failed to fetch:', error);
            return {};
        }
    },

    /**
     * Get thread location (returns 'prime', 'agent-1', etc., or null)
     */
    async getThreadLocation(threadId) {
        const assignments = await this.getThreadAssignments();
        for (const [location, assignedThreadId] of Object.entries(assignments)) {
            if (assignedThreadId === threadId) {
                return location;
            }
        }
        return null;
    },

    /**
     * Get thread assigned to a specific location
     */
    async getThreadAtLocation(location) {
        const assignments = await this.getThreadAssignments();
        return assignments[location] || null;
    },

    /**
     * Unassign thread from its current location
     */
    unassignThread(threadId) {
        return this.assignThread(threadId, null);
    },

    /**
     * Realtime subscription initialization
     */
    async initRealtimeSubscription() {
        console.log('🔄 [Assignment] Initializing Realtime subscriptions...');

        // Check if Supabase is available
        if (typeof window.supabase === 'undefined') {
            console.warn('⚠️ [Assignment] Supabase not loaded, realtime disabled');
            this.realtimeEnabled = false;
            return;
        }

        try {
            if (!window.SUPABASE_CLIENT) {
                window.SUPABASE_CLIENT = window.supabase.createClient(
                    window.SUPABASE_URL,
                    window.SUPABASE_ANON_KEY
                );
            }

            const userId = (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1;

            this.realtimeChannel = window.SUPABASE_CLIENT
                .channel('thread-location-changes')
                .on('postgres_changes', {
                    event: 'UPDATE',
                    schema: 'sessions',
                    table: 'threads',
                    filter: `user_id=eq.${userId}`
                }, (payload) => {
                    this.handleThreadLocationChange(payload);
                })
                .subscribe((status) => {
                    if (status === 'SUBSCRIBED') {
                        console.log('✅ [Assignment] Realtime active');
                        this.realtimeEnabled = true;
                    } else if (status === 'CHANNEL_ERROR' || status === 'TIMED_OUT') {
                        console.warn('⚠️ [Assignment] Realtime failed, using fallback mode');
                        this.realtimeEnabled = false;
                    }
                });
        } catch (error) {
            console.error('❌ [Assignment] Failed to init realtime:', error);
            this.realtimeEnabled = false;
        }
    },

    /**
     * Handle realtime thread location changes
     */
    handleThreadLocationChange(payload) {
        // Debounce: Ignore updates within 500ms of our own changes
        const now = Date.now();
        if (this.pendingAssignment || (now - this.lastRealtimeUpdate < 500)) {
            console.log('⏭️ [Assignment] Ignoring update (debounce)');
            return;
        }

        this.lastRealtimeUpdate = now;

        const { new: newRecord, old: oldRecord } = payload;
        if (!newRecord) return;

        const threadId = newRecord.id;
        const oldLocation = oldRecord?.location || 'prime';
        const newLocation = newRecord.location || 'prime';

        if (oldLocation === newLocation) return;

        console.log(`🔄 [Assignment] Realtime: Thread ${threadId}: ${oldLocation} → ${newLocation}`);

        // Update thread object
        const thread = this.threads.find(t => t.id === threadId);
        if (thread) {
            thread.location = newLocation;
            thread.agent = newLocation === 'prime' ? null : newLocation;
        }

        // Refresh UI
        if (typeof this.renderThreadList === 'function') {
            this.renderThreadList();
        }
        if (typeof this.refreshAllThreadInfoCards === 'function') {
            this.refreshAllThreadInfoCards(threadId);
        }
    },



    // ==================== ADD TO thread-manager-assignment.js ====================

    /**
     * Clear all assignments (useful for debugging)
     */
    async clearAllAssignments() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/thread-assignments/clear`, {
                method: 'DELETE'
            });
            const data = await response.json();
            if (data.success) {
                console.log('✅ [Assignment] All thread assignments cleared from backend');
            }
        } catch (error) {
            console.error('❌ [Assignment] Failed to clear assignments:', error);
        }
    },

    /**
     * Validate and fix assignment inconsistencies
     */
    async validateAssignments() {
        console.log('🔍 [Assignment] Validating thread assignments...');

        const assignments = await this.getThreadAssignments();
        const seenThreads = new Set();
        const errors = [];
        let fixed = false;

        // Check for duplicate thread assignments
        Object.entries(assignments).forEach(([location, threadId]) => {
            if (seenThreads.has(threadId)) {
                errors.push(`❌ Thread ${threadId} assigned to multiple locations`);
                delete assignments[location];
                fixed = true;
            } else {
                seenThreads.add(threadId);
            }
        });

        // Validate against MultiAgent.loadedThreads
        if (typeof MultiAgent !== 'undefined') {
            Object.entries(MultiAgent.loadedThreads).forEach(([agentId, threadInfo]) => {
                if (threadInfo && threadInfo.threadId) {
                    const location = `agent-${agentId}`;
                    const assignedThread = assignments[location];

                    if (assignedThread !== threadInfo.threadId) {
                        errors.push(`⚠️ Mismatch at ${location}: assignments=${assignedThread}, loadedThreads=${threadInfo.threadId}`);
                        assignments[location] = threadInfo.threadId;
                        fixed = true;
                    }
                }
            });
        }

        // Validate against AppState (Prime panel)
        if (typeof AppState !== 'undefined' && AppState.sessionId) {
            const primeAssignment = assignments['prime'];
            if (primeAssignment !== AppState.sessionId) {
                errors.push(`⚠️ Mismatch at prime: assignments=${primeAssignment}, AppState=${AppState.sessionId}`);
                assignments['prime'] = AppState.sessionId;
                fixed = true;
            }
        }

        // Save if any fixes were made
        if (fixed) {
            for (const [location, threadId] of Object.entries(assignments)) {
                if (threadId) {
                    await this.assignThread(threadId, location);
                }
            }
            console.log('✅ [Assignment] Fixed assignment inconsistencies:', errors);
        } else if (errors.length === 0) {
            console.log('✅ [Assignment] All thread assignments valid');
        } else {
            console.log('⚠️ [Assignment] Validation completed with warnings:', errors);
        }

        return {
            valid: errors.length === 0,
            errors: errors,
            fixed: fixed,
            assignments: assignments
        };
    }




});

console.log('✅ ThreadManager-Assignment module loaded');
console.log('🔍 [Assignment] restoreThreadAssignments exists?', typeof window.ThreadManager.restoreThreadAssignments === 'function');

// Add window command for manual testing
window.manualRestoreThreads = async function () {
    console.log('🔄 [Manual] Starting manual thread restoration...');
    if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.restoreThreadAssignments === 'function') {
        await ThreadManager.restoreThreadAssignments();
        console.log('✅ [Manual] Thread restoration complete!');
    } else {
        console.error('❌ [Manual] ThreadManager.restoreThreadAssignments not available');
    }
};