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
 * - ✅ 2025-12-02: Added deduplication to prevent triple assignment calls
 * 
 * LAST MODIFIED: 2025-12-02 - Added assignment deduplication
 */

// ==================== THREAD MANAGER - ASSIGNMENT MODULE ====================

/**
 * ✅ FIX: Assignment Deduplication System
 * Prevents duplicate API calls within 1 second window
 * Fixes issue where same thread assigned 3x in 4 seconds
 */
const AssignmentQueue = {
    pending: new Map(),  // key: "threadId-location" → {timestamp, promise}

    isRecentDuplicate(threadId, location) {
        const key = `${threadId}-${location}`;
        const pending = this.pending.get(key);

        if (pending) {
            const timeSince = Date.now() - pending.timestamp;
            if (timeSince < 1000) {
                console.warn(`⏭️ [Assignment Queue] Skipping duplicate: ${threadId} → ${location} (${timeSince}ms ago)`);
                return true;
            }
        }
        return false;
    },

    register(threadId, location, promise) {
        const key = `${threadId}-${location}`;
        this.pending.set(key, {
            timestamp: Date.now(),
            promise: promise
        });

        // Auto-cleanup after 2 seconds
        setTimeout(() => {
            this.pending.delete(key);
        }, 2000);
    },

    clear() {
        this.pending.clear();
    }
};

// Export for debugging
window.AssignmentQueue = AssignmentQueue;
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
    async assignThread(threadId, location, options = {}) {
        // options.swap: boolean — when true, the displaced thread is routed to
        // the source thread's previous location instead of 'unassigned'.
        // (Backend enforces; if source has no previous_location or it is
        // 'unassigned', the swap collapses to unassign automatically.)
        const swap = options.swap === true;
        console.log(`🔄 [Assignment] START: ${threadId} → ${location}${swap ? ' [swap mode]' : ''}`);

        // ✅ FIX: Check for duplicate assignment within 1 second
        if (AssignmentQueue.isRecentDuplicate(threadId, location)) {
            console.warn(`⏭️ [Assignment] Skipping duplicate assignment (within 1s window)`);
            return { skipped: true, reason: 'duplicate_within_1s' };
        }

        // CRITICAL: Enforce single prime thread
        if (location === 'prime') {
            const existingPrimeLoaded = this.threads.find(t => t.location === 'prime' && t.id !== threadId);
            if (existingPrimeLoaded) {
                console.log(`🔄 [Assignment] Clearing previous prime: ${existingPrimeLoaded.id}`);
                existingPrimeLoaded.location = 'unassigned'; // Reset to resting state
                // Update backend for cleared thread
                try {
                    const apiUrl = window.API_BASE_URL || 'http://localhost:5001';
                    const userId = (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1;
                    await fetch(`${apiUrl}/api/thread-assignments/assign`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            session_id: existingPrimeLoaded.id,
                            location: 'unassigned',
                            user_id: userId
                        })
                    });
                } catch (err) {
                    console.error('Failed to clear previous prime:', err);
                }
            }
        }

        try {
            // Set pending flag to prevent realtime loop
            this.pendingAssignment = true;

            // PHASE 1: UPDATE via Flask API (sessions schema not exposed in REST API)
            // NOTE: SUPABASE_CLIENT is set by SupabaseConnectionManager
            const userId = (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1;

            // Use Flask API instead of direct Supabase (sessions schema not exposed in REST API)
            const apiUrl = window.API_BASE_URL || 'http://localhost:5001';

            // ✅ FIX: Register assignment start to prevent duplicates (wrapping fetch in promise)
            const assignmentBody = JSON.stringify({
                session_id: threadId,
                location: location || 'unassigned',
                user_id: userId,
                swap: swap
            });
            const assignmentPromise = fetch(`${apiUrl}/api/thread-assignments/assign`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: assignmentBody
            });

            AssignmentQueue.register(threadId, location, assignmentPromise);

            let response = await assignmentPromise;

            // ✅ FIX: Retry on 502/503/504 (Render cold start) with exponential backoff
            // After max retries, fall back gracefully so the UI still loads.
            if (!response.ok && [502, 503, 504].includes(response.status)) {
                const maxRetries = 3;
                let retryDelay = 1500;
                let retryResponse = null;
                for (let attempt = 1; attempt <= maxRetries; attempt++) {
                    console.warn(`⚠️ [Assignment] Server returned ${response.status}, retrying in ${retryDelay}ms (attempt ${attempt}/${maxRetries})...`);
                    await new Promise(resolve => setTimeout(resolve, retryDelay));
                    retryDelay = Math.min(retryDelay * 1.5, 8000);
                    try {
                        retryResponse = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/thread-assignments/assign`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: assignmentBody
                        });
                        if (retryResponse.ok) {
                            response = retryResponse;
                            console.log(`✅ [Assignment] Retry ${attempt} succeeded`);
                            break;
                        }
                    } catch (retryErr) {
                        console.warn(`⚠️ [Assignment] Retry ${attempt} fetch error:`, retryErr.message);
                    }
                }
                // After all retries, if still not OK, update local state only (non-fatal)
                if (!response.ok) {
                    console.warn(`⚠️ [Assignment] Backend unreachable after ${maxRetries} retries - updating local state only (will sync on next interaction)`);
                    // Update local thread state so UI is consistent
                    const localThread = this.threads.find(t => t.id === threadId);
                    if (localThread) { localThread.location = location || 'unassigned'; }
                    this.pendingAssignment = false;
                    return { success: true, localOnly: true, assignment: { session_id: threadId, location: location || 'unassigned' } };
                }
            } else if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                throw new Error(`API update failed: ${errorData.error || response.statusText}`);
            }

            const updateData = await response.json();
            console.log(`✅ [Assignment] API updated:`, updateData);

            // Merge the API response into our local assignment payload so the
            // CASCADE step receives everything the backend decided — including
            // previous_location, displaced_thread, and displaced_new_location
            // (the latter only present when swap=true).
            const apiAssignment = updateData?.assignment || {};
            const data = {
                success: true,
                assignment: {
                    session_id: threadId,
                    location: location || 'unassigned',
                    user_id: userId,
                    previous_location: apiAssignment.previous_location ?? null,
                    displaced_thread: apiAssignment.displaced_thread ?? null,
                    displaced_new_location: apiAssignment.displaced_new_location ?? null,
                    swap: swap
                }
            };

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
        thread.agent = newLocation === 'unassigned' ? null : newLocation;
        thread.updated = new Date().toISOString();
        console.log(`✅ [CASCADE] Updated thread object: location=${newLocation}`);

        // 🔔 NEW: Add notification for thread assignment
        if (typeof NotificationCenter !== 'undefined' && NotificationCenter.add) {
            // Use the human-friendly display name (e.g. "Agent-3 Charlie" instead of "agent-3")
            const locationName = this.formatLocationName ? this.formatLocationName(newLocation) : newLocation;

            NotificationCenter.add({
                type: 'THREAD_ASSIGNED',
                message: `Thread "${thread.title || 'Untitled'}" assigned to ${locationName}`,
                metadata: {
                    threadId: threadId,
                    threadName: thread.title || 'Untitled',
                    location: newLocation,
                    agentId: newLocation.startsWith('agent-') ? parseInt(newLocation.replace('agent-', '')) : null
                },
                action: {
                    type: newLocation.startsWith('agent-') ? 'navigate_to_agent' : 'open_thread',
                    target: newLocation.startsWith('agent-') ?
                        { agentId: parseInt(newLocation.replace('agent-', '')) } :
                        { threadId: threadId }
                }
            });
            console.log(`[CASCADE] 🔔 Notification added for thread assignment: ${threadId} → ${newLocation}`);
        }

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
        // The backend now reports where the displaced thread was sent to via
        // assignment.displaced_new_location. Default to 'unassigned' if absent
        // (legacy responses or local-only fallback path).
        if (assignment.displaced_thread) {
            const displacedNewLocation = assignment.displaced_new_location || 'unassigned';
            console.log(`🔄 [CASCADE] Handling displaced thread: ${assignment.displaced_thread} → ${displacedNewLocation}`);
            const displacedThread = this.threads.find(t => t.id === assignment.displaced_thread);
            if (displacedThread) {
                displacedThread.location = displacedNewLocation;
                displacedThread.agent = displacedNewLocation.startsWith('agent-') ? displacedNewLocation : null;
                displacedThread.updated = new Date().toISOString();
                // Clear UI from the source target column (where the displaced
                // thread USED to be rendered).
                await this._clearLocationUI(newLocation, assignment.displaced_thread);

                // Surface a toast so the user knows the displaced thread moved.
                if (typeof showNotification === 'function') {
                    const displacedTitle = this.formatThreadTitle ? this.formatThreadTitle(displacedThread) : `"${displacedThread.title || 'Untitled'}"`;
                    const destName = this.formatLocationName ? this.formatLocationName(displacedNewLocation) : displacedNewLocation;
                    showNotification(`${displacedTitle} moved to ${destName}`, 'info', 2500);
                }
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
        } else if (newLocation === 'unassigned') {
            const primeThreadInfo = document.getElementById('thread-info-prime');
            if (primeThreadInfo && AppState.sessionId === threadId && typeof this.renderThreadInfoContainer === 'function') {
                primeThreadInfo.innerHTML = this.renderThreadInfoContainer('prime', threadId, false);
                console.log(`✅ [CASCADE] Updated thread-info for Prime`);
            }
        }

        // STEP 5: Refresh UI components
        // ✅ FIX #3: Functions now auto-debounced by wrapper (300ms)
        // Reduces redundant renders from 4→1, saves ~500ms per update
        if (typeof this.renderThreadList === 'function') {
            this.renderThreadList(); // Auto-debounced
        }
        if (typeof this.refreshAllThreadInfoCards === 'function') {
            this.refreshAllThreadInfoCards(threadId); // Auto-debounced
        }

        // NOTE: Thread location already updated at line 148-151 above
        // No need for redundant update here (removed duplicate 'const thread' declaration)

        // ✅ OPTIMIZATION (Nov 28, 2025): Only verify from backend every 10th update
        // This saves 90% of unnecessary API calls while still catching sync issues
        if (!window._cascadeUpdateCount) window._cascadeUpdateCount = 0;
        window._cascadeUpdateCount++;

        if (window._cascadeUpdateCount % 10 === 0) {
            console.log(`🔍 [CASCADE] Periodic verification (every 10th update): Refreshing from backend`);
            try {
                await this.loadThreadsFromBackend();
                const verifiedThread = this.threads.find(t => t.id === threadId);
                if (verifiedThread && verifiedThread.location === newLocation) {
                    console.log(`✅ [CASCADE] Periodic verification passed: ${verifiedThread.location}`);
                } else {
                    console.warn(`⚠️ [CASCADE] Verification failed! Expected: ${newLocation}, Got: ${verifiedThread?.location || 'NOT FOUND'}`);
                }
            } catch (error) {
                console.error(`❌ [CASCADE] Verification failed:`, error);
            }
        } else {
            console.log(`⏭️ [CASCADE] Skipping backend verification (${window._cascadeUpdateCount % 10}/10)`);
        }

        console.log(`✅ [CASCADE] Complete for thread ${threadId}`);
        this.cascadeInProgress = false;  // Allow UI refreshes

        // ✨ Update agent badge if thread was assigned to an agent
        if (newLocation && newLocation.startsWith('agent-') && typeof MultiAgent !== 'undefined' && typeof MultiAgent.updateQuickNavBadge === 'function') {
            const agentId = parseInt(newLocation.replace('agent-', ''));
            MultiAgent.updateQuickNavBadge(agentId);
            console.log(`✅ [CASCADE] Updated quick nav badge for agent ${agentId}`);
        }
    },

    /**
     * CLEAR OLD LOCATION UI: Remove thread from old location
     * Only clears UI if this specific thread is loaded in that location
     */
    async _clearLocationUI(location, threadId) {
        if (location === 'unassigned') {
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
        console.log('\n🔄 [Assignment] ========== RESTORING THREAD ASSIGNMENTS ==========');
        console.log('📊 [Assignment] Current threads in memory:', this.threads.length);
        console.log('📍 [Assignment] Current locations:', this.threads.map(t => `${t.id}→${t.location}`));

        try {
            // NOTE: SUPABASE_CLIENT is set by SupabaseConnectionManager
            const userId = (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1;
            console.log('👤 [Assignment] User ID:', userId);
            console.log('🌐 [Assignment] Fetching from Flask API...');

            // Use Flask API instead of direct Supabase (sessions schema not exposed in REST API)
            const apiUrl = window.API_BASE_URL || 'http://localhost:5001';
            const response = await fetch(`${apiUrl}/api/thread-assignments?user_id=${userId}`);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                throw new Error(`Failed to fetch assignments: ${errorData.error || response.statusText}`);
            }

            const result = await response.json();
            const assignmentsObj = result.assignments || {};
            console.log('📦 [Assignment] API response:', assignmentsObj);

            // Convert API response {location: thread_slug} to array format [{session_id, location}]
            const assignments = Object.entries(assignmentsObj).map(([location, thread_slug]) => ({
                session_id: thread_slug,
                location: location
            }));

            console.log(`✅ [Assignment] Restored ${assignments.length} thread assignments`);
            console.log('📋 [Assignment] Assignments:', assignments);

            // Update local thread objects with assignment data
            let updatedCount = 0;
            for (const assignment of assignments) {
                const thread = this.threads.find(t => t.id === assignment.session_id);
                if (thread) {
                    const oldLocation = thread.location;
                    thread.location = assignment.location;
                    thread.agent = assignment.location === 'unassigned' ? null : assignment.location;
                    console.log(`   🔄 Updated thread ${thread.id}: "${thread.title}" | ${oldLocation} → ${assignment.location}`);
                    updatedCount++;
                } else {
                    console.warn(`   ⚠️ Assignment for ${assignment.session_id} but thread not found in memory`);
                }
            }
            console.log(`✅ [Assignment] Updated ${updatedCount}/${assignments.length} threads with locations`);

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
                const threadsToLoad = assignments.map(a => this.threads.find(t => t.id === a.session_id)).filter(Boolean);
                console.log(`\n📍 [Assignment] ========== LOADING THREADS INTO AGENTS ==========`);
                console.log(`📍 [Assignment] ${threadsToLoad.length} threads need to be loaded`);
                threadsToLoad.forEach(t => {
                    console.log(`   🎯 ${t.id}: "${t.title}" → ${t.location}`);
                });

                for (const assignment of assignments) {
                    const thread = this.threads.find(t => t.id === assignment.session_id);
                    if (!thread) {
                        console.warn(`⚠️ [Assignment] Thread ${assignment.session_id} not found for loading`);
                        continue;
                    }

                    if (assignment.location && assignment.location.startsWith('agent-')) {
                        const agentId = parseInt(assignment.location.replace('agent-', ''));

                        // CRITICAL: Skip if thread is already loaded in this agent
                        // Check MultiAgent.loadedThreads to avoid duplicate loading
                        const alreadyLoaded = MultiAgent.loadedThreads &&
                            MultiAgent.loadedThreads[agentId] &&
                            MultiAgent.loadedThreads[agentId].threadId === thread.id;

                        if (alreadyLoaded) {
                            console.log(`✅ [Assignment] Thread "${thread.title}" already loaded in agent-${agentId}, skipping duplicate load`);
                            continue;
                        }

                        console.log(`🔄 [Assignment] Loading "${thread.title}" (${thread.id}) into agent-${agentId}...`);

                        try {
                            await MultiAgent.loadThreadIntoAgent(agentId, thread);
                            console.log(`✅ [Assignment] Loaded thread "${thread.title}" into agent-${agentId}`);
                        } catch (error) {
                            console.error(`❌ [Assignment] Failed to load thread into agent-${agentId}:`, error);
                        }
                    } else if (assignment.location === 'unassigned' && assignment.session_id === this.currentThreadId) {
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
     * Get thread assignments from Supabase
     */
    async getThreadAssignments() {
        try {
            // NOTE: SUPABASE_CLIENT is set by SupabaseConnectionManager
            const userId = (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1;

            // Use Flask API instead of direct Supabase (sessions schema not exposed in REST API)
            const apiUrl = window.API_BASE_URL || 'http://localhost:5001';
            const response = await fetch(`${apiUrl}/api/thread-assignments?user_id=${userId}`);

            if (!response.ok) {
                console.error('❌ [Assignment] API error:', response.statusText);
                return {};
            }

            const result = await response.json();
            const assignments = result.assignments || {};

            // API already returns {location: thread_slug} format
            console.log('✅ [Assignment] Fetched assignments:', assignments);
            return assignments;
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
        // ✅ Check for SupabaseConnectionManager
        if (!window.SupabaseConnectionManager) {
            console.warn('⚠️ [Assignment] SupabaseConnectionManager not available, realtime disabled');
            this.realtimeEnabled = false;
            return;
        }

        try {
            console.log('🔷 [Assignment] Subscribing with connection manager...');
            const userId = (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1;

            // ✨ USE CONNECTION MANAGER (prevents duplicate connections)
            this.realtimeChannel = await window.SupabaseConnectionManager.subscribeChannel(
                'thread-location-changes',
                {
                    schema: 'sessions',
                    table: 'threads',
                    event: 'UPDATE',
                    filter: `user_id=eq.${userId}`,
                    callback: (payload) => {
                        this.handleThreadLocationChange(payload);
                    }
                }
            );

            if (!this.realtimeChannel) {
                console.warn('⚠️ [Assignment] Realtime failed, using fallback mode');
                this.realtimeEnabled = false;
            } else {
                console.log('✅ [Assignment] Realtime active with connection manager');
                this.realtimeEnabled = true;
            }
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
        const oldLocation = oldRecord?.location || 'unassigned';
        const newLocation = newRecord.location || 'unassigned';

        if (oldLocation === newLocation) return;

        console.log(`🔄 [Assignment] Realtime: Thread ${threadId}: ${oldLocation} → ${newLocation}`);

        // Update thread object
        const thread = this.threads.find(t => t.id === threadId);
        if (thread) {
            thread.location = newLocation;
            thread.agent = newLocation === 'unassigned' ? null : newLocation;
        }

        // CRITICAL (Dec 12, 2025): Clear old location UI when realtime update arrives
        // This handles cross-tab/window updates where another session moved the thread
        if (oldLocation && oldLocation !== newLocation) {
            console.log(`🧹 [Assignment] Realtime: Clearing old location ${oldLocation}`);
            this._clearLocationUI(oldLocation, threadId);
        }

        // Refresh UI
        // ✅ FIX #3: Functions now auto-debounced by wrapper (300ms)
        if (typeof this.renderThreadList === 'function') {
            this.renderThreadList(); // Auto-debounced
        }
        if (typeof this.refreshAllThreadInfoCards === 'function') {
            this.refreshAllThreadInfoCards(threadId); // Auto-debounced
        }
    },



    // ==================== ADD TO thread-manager-assignment.js ====================

    /**
     * Clear all assignments (useful for debugging)
     */
    async clearAllAssignments() {
        try {
            // NOTE: SUPABASE_CLIENT is set by SupabaseConnectionManager
            const userId = (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1;

            // Use Flask API instead of direct Supabase (sessions schema not exposed in REST API)
            const apiUrl = window.API_BASE_URL || 'http://localhost:5001';
            const response = await fetch(`${apiUrl}/api/thread-assignments/clear/all`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId })
            });

            if (!response.ok) {
                console.error('❌ [Assignment] API error:', response.statusText);
            } else {
                console.log('✅ [Assignment] All thread assignments cleared via API');
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

            // Only fix if there's a mismatch
            if (primeAssignment !== AppState.sessionId) {
                errors.push(`⚠️ Mismatch at prime: assignments=${primeAssignment}, AppState=${AppState.sessionId}`);
                assignments['prime'] = AppState.sessionId;
                fixed = true;
            } else {
                console.log('✅ [Assignment] AppState thread is correctly in prime');
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
    },

    /**
     * Helper: Get agent name from ID
     * @param {string|number} agentId - Agent ID
     * @returns {string} Agent name
     */
    getAgentName(agentId) {
        const names = {
            1: 'Alpha', 2: 'Bravo', 3: 'Charlie', 4: 'Delta',
            5: 'Echo', 6: 'Foxtrot', 7: 'Golf', 8: 'Hotel'
        };
        return names[parseInt(agentId)] || `Agent ${agentId}`;
    }
});

// Signal that assignment module is fully loaded
window.ThreadManager._assignmentModuleLoaded = true;
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