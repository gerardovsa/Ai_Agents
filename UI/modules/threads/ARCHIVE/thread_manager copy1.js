ded(direct assignment)
if (options.synergySessionId !== undefined) {
    thread.synergy_card_id = options.synergySessionId;
    thread.synergy_card_name = options.synergySessionName || null;
}
if (options.workflowId !== undefined) {
    thread.workflow_id = options.workflowId;
    thread.workflow_name = options.workflowName || null;
}

// Remove linkages if requested
if (options.removeLinks) {
    if (options.removeLinks.includes('synergy')) {
        thread.synergy_card_id = null;
        thread.synergy_card_name = null;
    }
    if (options.removeLinks.includes('workflow')) {
        thread.workflow_id = null;
        thread.workflow_name = null;
    }
}
                }

// STEP 3: Update backend (ensure database sync)
await this.assignThread(threadId, backendLocation);

// STEP 4: Refresh ALL thread-info cards (agent columns, Prime, Synergy cards)
this.refreshAllThreadInfoCards(threadId);

// STEP 5: Refresh sidebar (updates agent badge + UI pills)
this.renderThreadList();

// STEP 6: Update Prime header if this is current thread
if (this.currentThreadId === threadId && frontendLocation === 'main') {
    this.updatePrimeHeader(threadId);
}

// STEP 7: Sync AppState
this.syncAppState(threadId);

// STEP 8: Notify user
const locationName = frontendLocation === 'main' ? 'Prime AI' :
    frontendLocation.startsWith('agent-') ? `Agent ${frontendLocation.replace('agent-', '')}` :
        frontendLocation;
console.log(`? [syncThreadLocationEverywhere] Thread ${threadId} synced to ${locationName}`);

return { success: true, location: frontendLocation };
            },

/**
 * Refresh all thread-info cards for a specific thread across the entire UI
 * Also updates UI pills (Synergy, Workflow, etc.)
 */
refreshAllThreadInfoCards(threadId) {
    console.log(`?? [refreshAllThreadInfoCards] Refreshing all cards for thread ${threadId}`);

    // Find all thread-info cards with this thread ID
    const threadCards = document.querySelectorAll(`[data-thread-id="${threadId}"]`);

    threadCards.forEach(card => {
        // Get the location from the card's context
        const location = card.getAttribute('data-location') || 'prime';

        // Re-render the card with updated agent info AND UI pills
        const newCardHTML = this.renderThreadInfoContainer(location, threadId, card.classList.contains('compact'));

        // Replace the card's innerHTML
        card.outerHTML = newCardHTML;

        console.log(`? [refreshAllThreadInfoCards] Updated thread-info card at ${location}`);
    });

    // Also update sidebar thread items (shows UI pills)
    const thread = this.threads.find(t => t.id === threadId);
    if (thread) {
        const sidebarItem = document.querySelector(`[data-thread-id="${threadId}"].thread-item`);
        if (sidebarItem) {
            // Re-render just the pills section
            this.updateThreadPills(sidebarItem, thread);
        }
    }

    // REALTIME: No need to refresh Synergy board - Supabase realtime handles it
    // Synergy board subscribes to postgres_changes on synergy_sessions table (line ~40410)
    // Removed synergyBoard.loadSessions() to prevent unnecessary API calls
},

/**
 * Update UI pills on a thread item (Synergy=green, Workflow=orange, etc.)
 */
updateThreadPills(threadElement, thread) {
    // Find or create pills container
    let pillsContainer = threadElement.querySelector('.thread-ui-pills');
    if (!pillsContainer) {
        pillsContainer = document.createElement('div');
        pillsContainer.className = 'thread-ui-pills';
        pillsContainer.style.cssText = 'display: flex; gap: 6px; margin-top: 6px; flex-wrap: wrap;';
        threadElement.appendChild(pillsContainer);
    }

    // Clear existing pills
    pillsContainer.innerHTML = '';

    // Add Synergy pill (green)
    if (thread.synergy_card_id) {
        const synergyPill = document.createElement('span');
        synergyPill.className = 'thread-pill thread-pill-synergy';
        synergyPill.style.cssText = 'background: #10b981; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; display: flex; align-items: center; gap: 4px;';
        synergyPill.innerHTML = `<i class="fas fa-link" style="font-size: 10px;"></i> Synergy`;
        synergyPill.title = thread.synergy_card_name || thread.synergy_card_id;
        pillsContainer.appendChild(synergyPill);
    }

    // Add Workflow pill (orange)
    if (thread.workflow_id) {
        const workflowPill = document.createElement('span');
        workflowPill.className = 'thread-pill thread-pill-workflow';
        workflowPill.style.cssText = 'background: #f97316; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; display: flex; align-items: center; gap: 4px;';
        workflowPill.innerHTML = `<i class="fas fa-robot" style="font-size: 10px;"></i> Workflow`;
        workflowPill.title = thread.workflow_name || thread.workflow_id;
        pillsContainer.appendChild(workflowPill);
    }

    // Add Custom pills (extensible for future link types)
    if (thread.custom_links && Array.isArray(thread.custom_links)) {
        thread.custom_links.forEach(link => {
            const customPill = document.createElement('span');
            customPill.className = `thread-pill thread-pill-${link.type}`;
            customPill.style.cssText = `background: ${link.color || '#6366f1'}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; display: flex; align-items: center; gap: 4px;`;
            customPill.innerHTML = `<i class="fas ${link.icon || 'fa-link'}" style="font-size: 10px;"></i> ${link.label}`;
            customPill.title = link.description || link.id;
            pillsContainer.appendChild(customPill);
        });
    }
},

            /**
             * SUPABASE REALTIME: Listen to users.metadata changes for thread assignments
             * Replaces polling API calls with real-time subscriptions
             */
            async initRealtimeSubscription() {
    // ?? REALTIME: Watches sessions.threads.location for instant UI updates across all windows
    // When a thread moves between Prime/Agents, this triggers CASCADE updates:
    //   - Thread list badge updates
    //   - Thread info cards refresh
    //   - Old location clears (Prime or agent)
    //   - New location loads thread
    //   - Synergy dashboard updates if applicable

    // ?? CURRENTLY DISABLED: Enable in Supabase Dashboard first
    // Steps to enable:
    //   1. Supabase Dashboard ? Database ? Replication
    //   2. Enable replication for: sessions.threads table
    //   3. Remove the return statement below
    //   4. Refresh browser - WebSocket will connect
    console.log('?? [ThreadManager] Realtime subscriptions disabled (enable in Supabase Dashboard ? Database ? Replication)');
    this.realtimeEnabled = false;
    return;

    // eslint-disable-next-line no-unreachable
    console.log('?? [ThreadManager] Initializing Realtime subscriptions...');

    // Ensure config is loaded
    if (!window.SUPABASE_CONFIG_LOADED) {
        console.log('?? [ThreadManager] Waiting for Supabase config...');
        await window.loadSupabaseConfig();
    }

    try {
        // Check if Supabase client exists
        if (typeof window.supabase === 'undefined' || typeof window.supabase.createClient !== 'function') {
            console.warn('?? [ThreadManager] Supabase client not loaded, realtime disabled');
            return;
        }

        if (!window.SUPABASE_URL || !window.SUPABASE_ANON_KEY) {
            console.warn('?? [ThreadManager] Supabase credentials missing, realtime disabled');
            return;
        }

        // Use or create shared Supabase client (prevents multiple WebSocket connections)
        if (!window.SUPABASE_CLIENT) {
            window.SUPABASE_CLIENT = window.supabase.createClient(window.SUPABASE_URL, window.SUPABASE_ANON_KEY);
            console.log('? [ThreadManager] Created shared Supabase client');
        }
        const supabaseClient = window.SUPABASE_CLIENT;

        // Subscribe to sessions.threads location changes (when threads move between Prime/Agents)
        const userId = (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1;

        this.realtimeChannel = supabaseClient
            .channel('thread-location-changes')
            .on('postgres_changes', {
                event: 'UPDATE',
                schema: 'sessions',
                table: 'threads',
                filter: `user_id=eq.${userId}`
            }, (payload) => {
                console.log('?? [REALTIME] Thread location changed:', payload);
                this.handleThreadLocationChange(payload);
            })
            .subscribe((status) => {
                if (status === 'SUBSCRIBED') {
                    console.log('? [REALTIME] Thread assignments realtime active');
                    this.realtimeEnabled = true;
                    window.SUPABASE_REALTIME_ENABLED = true;
                } else if (status === 'CHANNEL_ERROR' || status === 'TIMED_OUT' || status === 'CLOSED') {
                    // Only show warning once
                    if (!window.SUPABASE_REALTIME_WARNED) {
                        console.warn('?? [REALTIME] Subscription failed:', status);
                        console.warn('?? [REALTIME] Running in fallback mode (no auto-sync across windows)');
                        console.warn('?? [REALTIME] To enable: Supabase Dashboard ? Database ? Replication ? Enable for ai_infrastructure.users');
                        window.SUPABASE_REALTIME_WARNED = true;
                    }
                    this.realtimeEnabled = false;
                    // DON'T unsubscribe here - it causes infinite recursion
                    // Just mark channel as null and let it fail gracefully
                    this.realtimeChannel = null;
                }
            });
    } catch (error) {
        console.error('? [ThreadManager] Failed to init realtime:', error);
    }
},

/**
 * Handle realtime thread location changes from Supabase
 * Triggered when sessions.threads.location column changes
 * This is the CASCADE TRIGGER that updates ALL UI elements
 */
handleThreadLocationChange(payload) {
    console.log('?? [REALTIME] Thread location change detected:', payload);

    // Debounce: Ignore updates within 500ms of our own changes
    const now = Date.now();
    if (this.pendingAssignment || (now - this.lastRealtimeUpdate < 500)) {
        console.log('?? [REALTIME] Ignoring update (debounce - this is our own change)');
        return;
    }

    this.lastRealtimeUpdate = now;

    const { new: newRecord, old: oldRecord } = payload;
    if (!newRecord) {
        console.warn('?? [REALTIME] No new record in payload');
        return;
    }

    const threadId = newRecord.id;
    const oldLocation = oldRecord?.location || 'prime';
    const newLocation = newRecord.location || 'prime';

    // Only process if location actually changed
    if (oldLocation === newLocation) {
        console.log('?? [REALTIME] Location unchanged, skipping');
        return;
    }

    console.log(`?? [REALTIME] Thread ${threadId}: ${oldLocation} ? ${newLocation}`);

    try {
        // STEP 1: Update thread object in memory
        const thread = this.threads.find(t => t.id === threadId);
        if (thread) {
            thread.location = newLocation;
            thread.agent = newLocation === 'prime' ? null : newLocation;
            thread.updated = new Date().toISOString();
            console.log('? [REALTIME] Updated thread object in memory');
        }

        // STEP 2: Update thread list (shows correct badge)
        this.renderThreadList();
        console.log('? [REALTIME] Thread list refreshed (badge updated)');

        // STEP 3: Update thread info cards (all locations)
        this.refreshAllThreadInfoCards(threadId);
        console.log('? [REALTIME] Thread info cards refreshed');

        // STEP 4: If thread was in Prime and moved to agent, clear Prime
        if (oldLocation === 'prime' && newLocation.startsWith('agent-')) {
            const primeMessages = document.getElementById('ai-chat-messages');
            if (primeMessages && this.currentThreadId === threadId) {
                primeMessages.innerHTML = '';
                this.currentThreadId = null;
                console.log('? [REALTIME] Cleared Prime chat (thread moved to agent)');
            }

            const primeThreadInfo = document.getElementById('prime-thread-info');
            if (primeThreadInfo) {
                primeThreadInfo.innerHTML = this.renderThreadInfoContainer('prime', null, false);
                console.log('? [REALTIME] Cleared Prime thread info');
            }

            // Clear AppState
            if (typeof AppState !== 'undefined' && AppState.sessionId === threadId) {
                AppState.sessionId = null;
                AppState.chatMessages = [];
                console.log('? [REALTIME] Cleared AppState');
            }
        }

        // STEP 5: If thread moved to agent, update that agent's header
        if (newLocation.startsWith('agent-')) {
            const agentId = parseInt(newLocation.replace('agent-', ''));
            if (typeof MultiAgent !== 'undefined' && MultiAgent.updateAgentHeader) {
                MultiAgent.updateAgentHeader(agentId);
                console.log(`? [REALTIME] Updated Agent ${agentId} header`);
            }
        }

        // STEP 6: Update thread history modal if open
        const historyModal = document.getElementById('thread-history-modal');
        if (historyModal && historyModal.style.display !== 'none') {
            const modalThreadId = historyModal.dataset.threadId;
            if (modalThreadId === threadId) {
                // Refresh the thread info section in modal
                console.log('? [REALTIME] Thread history modal updated');
            }
        }

        // STEP 7: Update Synergy dashboard if thread is in synergy session
        if (typeof window.synergyBoard !== 'undefined' && window.synergyBoard.refreshSessions) {
            // Check if thread is part of any synergy session
            setTimeout(() => {
                window.synergyBoard.refreshSessions();
                console.log('? [REALTIME] Synergy dashboard refreshed');
            }, 100);
        }

        console.log(`? [REALTIME] CASCADE COMPLETE for thread ${threadId}: ${oldLocation} ? ${newLocation}`);

    } catch (error) {
        console.error('? [REALTIME] Failed to process location change:', error);
    }
},

            // Get thread assignments from backend (NOW ONLY USED ON INITIAL LOAD)
            async getThreadAssignments() {
    try {
        const userId = (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1;
        const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/thread-assignments/list?user_id=${userId}`);
        const data = await response.json();

        if (data.success && data.assignments) {
            return data.assignments;
        }
        return {};
    } catch (error) {
        console.error('[ERROR] [getThreadAssignments] Failed to fetch:', error);
        return {};
    }
},

            // Get thread location (returns 'prime', 'agent-1', etc., or null)
            async getThreadLocation(threadId) {
    const assignments = await this.getThreadAssignments();
    for (const [location, assignedThreadId] of Object.entries(assignments)) {
        if (assignedThreadId === threadId) {
            return location;
        }
    }
    return null;
},

            // Get thread assigned to a specific location
            async getThreadAtLocation(location) {
    const assignments = await this.getThreadAssignments();
    return assignments[location] || null;
},

// Unassign thread from its current location
unassignThread(threadId) {
    return this.assignThread(threadId, null);
},

            // Clear all assignments (useful for debugging)
            async clearAllAssignments() {
    try {
        // Clear backend assignments
        const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/thread-assignments/clear`, {
            method: 'DELETE'
        });
        const data = await response.json();
        if (data.success) {
            console.log('[CLEAN] All thread assignments cleared from backend');
        }
    } catch (error) {
        console.error('[ERROR] Failed to clear assignments:', error);
    }
},

            // Validate and fix assignment inconsistencies
            async validateAssignments() {
    console.log('[SEARCH] [ThreadManager] Validating thread assignments...');

    const assignments = await this.getThreadAssignments();
    const seenThreads = new Set();
    const errors = [];
    let fixed = false;

    // Check for duplicate thread assignments (thread in multiple locations)
    Object.entries(assignments).forEach(([location, threadId]) => {
        if (seenThreads.has(threadId)) {
            errors.push(`[ERROR] Thread ${threadId} assigned to multiple locations`);
            // Keep only the first occurrence, remove duplicates
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
                    errors.push(`[WARN] Mismatch at ${location}: assignments=${assignedThread}, loadedThreads=${threadInfo.threadId}`);
                    // Trust loadedThreads as source of truth
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
            errors.push(`[WARN] Mismatch at prime: assignments=${primeAssignment}, AppState=${AppState.sessionId}`);
            assignments['prime'] = AppState.sessionId;
            fixed = true;
        }
    }

    // Save if any fixes were made
    if (fixed) {
        // Save corrected assignments to backend (not localStorage)
        for (const [location, threadId] of Object.entries(assignments)) {
            if (threadId) {
                await this.assignThread(threadId, location);
            }
        }
        console.log('[OK] Fixed assignment inconsistencies:', errors);
    } else if (errors.length === 0) {
        console.log('[OK] All thread assignments valid');
    } else {
        console.log('[WARN] Validation completed with warnings:', errors);
    }

    return {
        valid: errors.length === 0,
        errors: errors,
        fixed: fixed,
        assignments: assignments
    };
},

            async ensureCorrectUserData() {
    console.log(' [USER CHECK] Verifying user data from backend...');
    try {
        const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/auth/profile`, {
            headers: { 'Authorization': `Bearer ${UserAuth.token}` }
        });
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.profile) {
                // ✅ Backend returns both 'id' and 'user_id' for compatibility
                const backendUserId = data.profile.id || data.profile.user_id;
                const cachedUserId = (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) ?
                    (UserAuth.user.id || UserAuth.user.user_id) : null;
                console.log(' [USER CHECK] Backend user_id:', backendUserId);
                console.log(' [USER CHECK] Cached user_id:', cachedUserId);
                if (backendUserId !== cachedUserId || !cachedUserId) {
                    if (!cachedUserId) {
                        console.log(' [USER CHECK] First load - setting user data from backend');
                    } else {
                        console.warn(`⚠️ [USER CHECK] ID MISMATCH! Backend=${backendUserId}, Cached=${cachedUserId}`);
                    }
                    console.log(' [USER CHECK] Updating to backend user data...');
                    UserAuth.user = data.profile;
                    // ✅ Ensure both 'id' and 'user_id' are set for compatibility
                    UserAuth.user.id = backendUserId;
                    UserAuth.user.user_id = backendUserId;
                    window.currentUserId = backendUserId; // Initialize global user ID for settings save
                    localStorage.setItem('userProfile', JSON.stringify(data.profile));

                    // Initialize Device Lock Manager after user profile is loaded
                    if (typeof DeviceLockManager !== 'undefined' && !DeviceLockManager.deviceId) {
                        DeviceLockManager.init();
                    }

                    console.log('✅ [USER CHECK] User data updated from backend');
                } else {
                    console.log('✅ [USER CHECK] User ID verified - cached data is correct');
                }
            }
        } else {
            console.warn('⚠️ [USER CHECK] Failed to fetch profile from backend');
        }
    } catch (error) {
        console.error('❌ [USER CHECK] Error verifying user data:', error);
    }
},

            async init() {
    await this.ensureCorrectUserData();
    await this.loadThreadsFromBackend();
    this.initRealtimeSubscription();  // Start listening to thread assignment changes

    // [FIXED] AUTO-LOAD only threads that belong in Prime (location='prime' or no location)
    if (this.threads.length > 0) {
        // Find first thread that belongs in Prime (not assigned to an agent)
        const primeThread = this.threads.find(t => !t.location || t.location === 'prime');

        if (primeThread) {
            this.currentThreadId = primeThread.id;
            const thread = this.getCurrentThread();

            if (thread && thread.messages && thread.messages.length > 0) {
                console.log(`[DATA] Auto-loading Prime thread with ${thread.messages.length} messages`);

                // Load messages into chat
                const messagesContainer = document.getElementById('ai-chat-messages');
                if (messagesContainer) {
                    messagesContainer.innerHTML = '';
                    thread.messages.forEach(msg => {
                        addChatMessage(msg.role, msg.content);
                    });
                }

                // Update AppState
                if (typeof AppState !== 'undefined') {
                    AppState.chatMessages = [...thread.messages];
                    AppState.sessionId = thread.id;
                }

                // Update Prime header with current thread info
                this.updatePrimeHeader(thread);

                // Show Prime input wrapper (thread is loaded)
                const primeInputWrapper = document.querySelector('.ai-chat-input-wrapper');
                if (primeInputWrapper) {
                    primeInputWrapper.style.display = 'flex';
                    console.log('[UI] Showed Prime input wrapper (thread loaded)');
                }
            }
        } else {
            // All threads are in agent columns, show "Start New Chat" in Prime
            console.log('[DATA] No Prime threads - all threads in agent columns');
            this.showStartNewChatButton('ai-chat-messages', 'prime');
            this.initWelcomeMessage('prime');
        }
    } else {
        // No threads exist - show "Start New Chat" button
        console.log('[DATA] No existing threads, showing Start New Chat button');
        this.showStartNewChatButton('ai-chat-messages', 'prime');

        // Initialize welcome message
        this.initWelcomeMessage('prime');
    }

    this.startAutoSave();
    this.renderThreadList();

    // Note: Thread assignments are restored by initMultiAgent() after agent columns are created
    // DO NOT call restoreThreadAssignments() here - it runs too early (DOM not ready)

    // Note: Menu button uses inline onclick handler, no need for addEventListener

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        const menu = document.getElementById('thread-menu');
        const menuBtn = document.getElementById('chat-menu-btn');
        const sidebarBtn = document.getElementById('threads-btn');

        if (menu && !menu.contains(e.target)) {
            // Check if click was on either button
            const clickedMenuBtn = menuBtn && menuBtn.contains(e.target);
            const clickedSidebarBtn = sidebarBtn && sidebarBtn.contains(e.target);

            if (!clickedMenuBtn && !clickedSidebarBtn) {
                this.closeThreadMenu();
            }
        }
    });

    // Custom rich tooltip for Synergy badges
    let synergyTooltip = null;
    let tooltipTimeout = null;
    let hideTimeout = null;
    let currentTooltipBadge = null; // Track which badge is showing tooltip

    // Helper function to strip markdown formatting
    const stripMarkdown = (text) => {
        if (!text) return '';
        return text
            .replace(/\*\*(.+?)\*\*/g, '$1')  // Bold: **text** ? text
            .replace(/\*(.+?)\*/g, '$1')      // Italic: *text* ? text
            .replace(/\[(.+?)\]\(.+?\)/g, '$1')  // Links: [text](url) ? text
            .replace(/`(.+?)`/g, '$1')        // Code: `text` ? text
            .replace(/^#+\s+/gm, '')          // Headers: # text ? text
            .replace(/^>\s+/gm, '')           // Blockquotes: > text ? text
            .replace(/^[-*+]\s+/gm, '� ')     // Lists: - item ? � item
            .trim();
    };

    const showSynergyTooltip = (badge, event) => {
        // Clear any pending hide
        clearTimeout(hideTimeout);
        clearTimeout(tooltipTimeout);

        // Track current badge
        currentTooltipBadge = badge;

        // Keep thread-item open while tooltip is visible
        const threadItem = badge.closest('.thread-item');
        if (threadItem) {
            threadItem.classList.add('tooltip-active');
        }

        // Get tooltip data from badge attributes
        // Support both .thread-item-synergy and agent column badges
        const container = badge.closest('.thread-item-synergy') || badge.closest('.ai-chat-header-info');
        const sessionId = container?.getAttribute('data-synergy-id') || badge.getAttribute('data-synergy-id') || '';
        const title = badge.getAttribute('data-tooltip-title') || sessionId || 'Unknown Session';
        const rawDesc = badge.getAttribute('data-tooltip-desc') || '';
        const desc = stripMarkdown(rawDesc);  // Strip markdown formatting
        const users = badge.getAttribute('data-tooltip-users') || '';
        const updated = badge.getAttribute('data-tooltip-updated') || '';
        const priority = badge.querySelector('.synergy-badge-priority')?.textContent?.toLowerCase() || '';

        // Create tooltip if it doesn't exist
        if (!synergyTooltip) {
            synergyTooltip = document.createElement('div');
            synergyTooltip.className = 'synergy-tooltip';
            document.body.appendChild(synergyTooltip);

            // Add hover listeners to tooltip itself to keep it open
            synergyTooltip.addEventListener('mouseenter', () => {
                clearTimeout(hideTimeout);
                clearTimeout(tooltipTimeout);
                // Keep thread-item open
                if (currentTooltipBadge) {
                    const threadItem = currentTooltipBadge.closest('.thread-item');
                    if (threadItem) {
                        threadItem.classList.add('tooltip-active');
                    }
                }
            });

            synergyTooltip.addEventListener('mouseleave', () => {
                hideSynergyTooltip();
            });
        }

        // Build tooltip content
        let priorityHtml = '';
        if (priority) {
            priorityHtml = `<span class="synergy-tooltip-priority ${priority}">${priority}</span>`;
        }

        synergyTooltip.innerHTML = `
                        <button class="synergy-tooltip-close" onclick="document.querySelector('.synergy-tooltip')?.remove();" title="Close">
                            <i class="fas fa-times"></i>
                        </button>
                        <div class="synergy-tooltip-title">
                            <i class="fas fa-link"></i>
                            <span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${title}</span>
                            ${priorityHtml}
                        </div>
                        ${desc ? `<div class="synergy-tooltip-desc">${desc}</div>` : ''}
                        ${users ? `<div class="synergy-tooltip-meta"><i class="fas fa-users"></i> ${users}</div>` : ''}
                        ${updated ? `<div class="synergy-tooltip-meta"><i class="fas fa-clock"></i> ${updated}</div>` : ''}
                        ${sessionId ? `
                            <div class="synergy-tooltip-actions">
                                <a class="synergy-tooltip-link" onclick="event.stopPropagation(); if(typeof synergyBoard !== 'undefined') { if(synergyBoard.sessions.length === 0) { synergyBoard.loadSessions().then(() => synergyBoard.popOutCard('${sessionId}')); } else { synergyBoard.popOutCard('${sessionId}'); } } document.querySelector('.synergy-tooltip')?.remove();">
                                    <i class="fas fa-window-restore"></i>
                                    Open in Popup
                                </a>
                            </div>
                        ` : ''}
                    `;

        // Position tooltip
        const rect = badge.getBoundingClientRect();
        const tooltipRect = synergyTooltip.getBoundingClientRect();

        let left = rect.left + (rect.width / 2) - 160; // Center under badge
        let top = rect.bottom + 8;

        // Adjust if off-screen
        if (left < 10) left = 10;
        if (left + 320 > window.innerWidth) left = window.innerWidth - 330;
        if (top + tooltipRect.height > window.innerHeight) {
            top = rect.top - tooltipRect.height - 8; // Show above
        }

        synergyTooltip.style.left = `${left}px`;
        synergyTooltip.style.top = `${top}px`;

        // Show tooltip with longer delay for better UX
        clearTimeout(tooltipTimeout);
        tooltipTimeout = setTimeout(() => {
            synergyTooltip.classList.add('show');
        }, 500); // Increased from 200ms to 500ms
    };

    const hideSynergyTooltip = () => {
        // Add longer delay before hiding to allow mouse to move to tooltip
        clearTimeout(tooltipTimeout);
        clearTimeout(hideTimeout);
        hideTimeout = setTimeout(() => {
            if (synergyTooltip) {
                synergyTooltip.classList.remove('show');

                // Remove tooltip-active class from thread-item
                if (currentTooltipBadge) {
                    const threadItem = currentTooltipBadge.closest('.thread-item');
                    if (threadItem) {
                        threadItem.classList.remove('tooltip-active');
                    }
                }
                currentTooltipBadge = null;
            }
        }, 800); // Increased from 300ms to 800ms
    };

    // Tooltip event listeners (delegated)
    // Catch ALL synergy badges (thread-item-synergy, agent columns, anywhere)
    document.addEventListener('mouseover', (e) => {
        const badge = e.target.closest('.synergy-badge[data-tooltip-title]');
        if (badge) {
            showSynergyTooltip(badge, e);
        }
    });

    document.addEventListener('mouseout', (e) => {
        const badge = e.target.closest('.synergy-badge[data-tooltip-title]');
        if (badge) {
            // Only hide if mouse is not moving to tooltip, thread-item, or agent header
            const movingToTooltip = e.relatedTarget?.closest('.synergy-tooltip');
            const movingToThreadItem = e.relatedTarget?.closest('.thread-item');
            const movingToAgentHeader = e.relatedTarget?.closest('.ai-chat-header-info');

            if (!movingToTooltip && !movingToThreadItem && !movingToAgentHeader) {
                hideSynergyTooltip();
            }
        }
    });

    // Hide tooltip when scrolling
    document.addEventListener('scroll', hideSynergyTooltip, true);

    // Expose showSynergyTooltip globally for thread card action buttons
    window.showSynergyTooltip = showSynergyTooltip;
    window.hideSynergyTooltip = hideSynergyTooltip;

    // ==================== AGENT BADGE TOOLTIP SYSTEM ====================
    let agentTooltip = null;
    let agentTooltipTimeout = null;

    const showAgentBadgeTooltip = (badge, event) => {
        clearTimeout(agentTooltipTimeout);

        const title = badge.getAttribute('data-tooltip-title');
        const content = badge.getAttribute('data-tooltip-content');

        if (!title) return;

        // Create or get tooltip
        if (!agentTooltip) {
            agentTooltip = document.createElement('div');
            agentTooltip.className = 'agent-badge-tooltip';
            document.body.appendChild(agentTooltip);
        }

        // Build tooltip HTML
        agentTooltip.innerHTML = `
                        <div class="agent-tooltip-title">${title}</div>
                        ${content ? `<div class="agent-tooltip-content">${content}</div>` : ''}
                    `;

        // Position tooltip
        const rect = badge.getBoundingClientRect();
        const tooltipRect = agentTooltip.getBoundingClientRect();

        let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
        const top = rect.bottom + 8;

        // Keep tooltip in viewport
        if (left < 10) left = 10;
        if (left + tooltipRect.width > window.innerWidth - 10) {
            left = window.innerWidth - tooltipRect.width - 10;
        }

        agentTooltip.style.left = `${left}px`;
        agentTooltip.style.top = `${top}px`;
        agentTooltip.classList.add('show');
    };

    const hideAgentBadgeTooltip = () => {
        agentTooltipTimeout = setTimeout(() => {
            if (agentTooltip) {
                agentTooltip.classList.remove('show');
            }
        }, 300);
    };

    // Event listeners for agent badges
    document.addEventListener('mouseover', (e) => {
        const badge = e.target.closest('.agent-quick-nav-badge[data-tooltip-title]');
        if (badge) {
            showAgentBadgeTooltip(badge, e);
        }
    });

    document.addEventListener('mouseout', (e) => {
        const badge = e.target.closest('.agent-quick-nav-badge[data-tooltip-title]');
        if (badge) {
            const movingToTooltip = e.relatedTarget?.closest('.agent-badge-tooltip');
            if (!movingToTooltip) {
                hideAgentBadgeTooltip();
            }
        }
    });

    // Keep tooltip open when hovering over it
    document.addEventListener('mouseover', (e) => {
        if (e.target.closest('.agent-badge-tooltip')) {
            clearTimeout(agentTooltipTimeout);
        }
    });

    document.addEventListener('mouseout', (e) => {
        if (e.target.closest('.agent-badge-tooltip')) {
            const movingToBadge = e.relatedTarget?.closest('.agent-quick-nav-badge[data-tooltip-title]');
            if (!movingToBadge) {
                hideAgentBadgeTooltip();
            }
        }
    });

    // Click handler for Synergy badge in tooltip
    document.addEventListener('click', (e) => {
        const synergyBadge = e.target.closest('.agent-tooltip-synergy-badge');
        if (synergyBadge) {
            const synergyId = synergyBadge.getAttribute('data-synergy-id');
            if (synergyId && typeof synergyBoard !== 'undefined') {
                console.log('[Agent Badge] Opening Synergy session:', synergyId);
                // Load sessions if needed, then open popup
                if (synergyBoard.sessions.length === 0) {
                    synergyBoard.loadSessions().then(() => synergyBoard.popOutCard(synergyId));
                } else {
                    synergyBoard.popOutCard(synergyId);
                }
                // Hide tooltip after click
                if (agentTooltip) {
                    agentTooltip.classList.remove('show');
                }
            }
        }
    });

    // Hide on scroll
    document.addEventListener('scroll', hideAgentBadgeTooltip, true);
},

createThread() {
    const thread = {
        id: Date.now().toString(),
        title: 'New Chat',
        messages: [],
        created: new Date().toISOString(),
        updated: new Date().toISOString(),
        archived: false,  // NEW: Archive status
        agent: 'main'     // NEW: Which agent owns this thread
    };
    this.threads.unshift(thread);
    // Save to backend (async, don't wait - fallback for createNewThread() failure)
    this.saveThreadToBackend(thread);
    return thread.id;
},

            // Create a new Synergy session and link it to the thread in one action
            async createAndLinkSynergy(threadId) {
    try {
        const thread = this.threads.find(t => t.id === threadId);
        const title = thread && thread.title ? `${thread.title} (linked)` : `Linked from thread ${threadId}`;

        // Create session
        const resp = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/synergy/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description: `Auto-created from thread ${threadId}`, created_by: (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 'user' })
        });
        const data = await resp.json();
        if (!data || !data.success || !data.session_id) {
            console.error('[createAndLinkSynergy] Failed to create session', data);
            showNotification('Failed to create Synergy session', 'error');
            return null;
        }
        const sessionId = data.session_id;

        // Link to thread via thread update endpoint
        const updateResp = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/${threadId}/update`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: thread.title, synergy_card_id: sessionId })
        });
        const updateData = await updateResp.json();
        if (updateData && updateData.success) {
            // Update local thread state and re-render
            if (thread) {
                thread.synergy_card_id = sessionId;
                thread.updated = new Date().toISOString();
            }
            // Update thread with synergy metadata
            if (thread) {
                thread.synergy_card_name = title;
                thread.synergy_card_desc = `Auto-created from thread ${threadId}`;
            }

            // Preload the new session into cache
            try {
                const sresp = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/synergy?ids=${encodeURIComponent(sessionId)}`);
                if (sresp.ok) {
                    const sdata = await sresp.json();
                    if (sdata && sdata.success && sdata.sessions && sdata.sessions[sessionId]) {
                        if (!window._synergySessionCache) window._synergySessionCache = {};
                        window._synergySessionCache[sessionId] = sdata.sessions[sessionId];

                        // Update thread with fetched metadata
                        if (thread) {
                            thread.synergy_card_name = sdata.sessions[sessionId].title;
                            thread.synergy_card_desc = sdata.sessions[sessionId].description;
                            thread.synergy_card_priority = sdata.sessions[sessionId].priority;
                        }
                    }
                }
            } catch (e) {
                console.warn('[createAndLinkSynergy] Failed to preload new session', e);
            }

            // Refresh ALL thread info displays
            this.renderThreadList();
            this.refreshAllThreadInfoCards(threadId);

            showNotification('Synergy session created and linked', 'success');
            return sessionId;
        } else {
            console.error('[createAndLinkSynergy] Failed to link session to thread', updateData);
            showNotification('Failed to link Synergy session', 'error');
            return null;
        }
    } catch (err) {
        console.error('[createAndLinkSynergy] Exception:', err);
        showNotification('Error creating/linking Synergy session', 'error');
        return null;
    }
},

            // Unlink a synergy session from a thread quickly
            async unlinkSynergy(threadId, sessionId) {
    try {
        const resp = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/${threadId}/update`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: this.threads.find(t => t.id === threadId)?.title || '', synergy_card_id: null })
        });
        const data = await resp.json();
        if (data && data.success) {
            const thread = this.threads.find(t => t.id === threadId);
            if (thread) {
                thread.synergy_card_id = null;
                thread.synergy_card_name = null;
                thread.updated = new Date().toISOString();
            }

            // ? Use master sync to update all UI components (preserves workflow pill)
            await this.syncThreadLocationEverywhere(threadId, thread.agent || 'main', {
                removeLinks: ['synergy'],
                preserveLinks: true
            });

            showNotification('Synergy session unlinked', 'success');
            return true;
        } else {
            console.error('[unlinkSynergy] Failed:', data);
            showNotification('Failed to unlink Synergy session', 'error');
            return false;
        }
    } catch (err) {
        console.error('[unlinkSynergy] Exception:', err);
        showNotification('Error unlinking Synergy session', 'error');
        return false;
    }
},

            /**
             * ? WORKFLOW AUTOMATION LINKING
             * Link thread to workflow automation (orange pill)
             */
            async linkWorkflow(threadId, workflowId, workflowName) {
    try {
        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) {
            showNotification('Thread not found', 'error');
            return false;
        }

        // Update thread metadata in backend
        const resp = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/${threadId}/update`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: thread.title || '',
                workflow_id: workflowId,
                workflow_name: workflowName
            })
        });

        const data = await resp.json();
        if (data && data.success) {
            thread.workflow_id = workflowId;
            thread.workflow_name = workflowName;
            thread.updated = new Date().toISOString();

            // ? Use master sync to update all UI components
            await this.syncThreadLocationEverywhere(threadId, thread.agent || 'main', {
                addLinks: ['workflow'],
                workflowId: workflowId,
                workflowName: workflowName
            });

            showNotification(`Linked to workflow: ${workflowName}`, 'success');
            return true;
        } else {
            console.error('[linkWorkflow] Failed:', data);
            showNotification('Failed to link workflow', 'error');
            return false;
        }
    } catch (err) {
        console.error('[linkWorkflow] Exception:', err);
        showNotification('Error linking workflow', 'error');
        return false;
    }
},

            /**
             * Unlink workflow automation from thread
             */
            async unlinkWorkflow(threadId, workflowId) {
    try {
        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) {
            showNotification('Thread not found', 'error');
            return false;
        }

        const resp = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/${threadId}/update`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: thread.title || '',
                workflow_id: null,
                workflow_name: null
            })
        });

        const data = await resp.json();
        if (data && data.success) {
            thread.workflow_id = null;
            thread.workflow_name = null;
            thread.updated = new Date().toISOString();

            // ? Use master sync to update all UI components
            await this.syncThreadLocationEverywhere(threadId, thread.agent || 'main', {
                removeLinks: ['workflow']
            });

            showNotification('Workflow unlinked', 'success');
            return true;
        } else {
            console.error('[unlinkWorkflow] Failed:', data);
            showNotification('Failed to unlink workflow', 'error');
            return false;
        }
    } catch (err) {
        console.error('[unlinkWorkflow] Exception:', err);
        showNotification('Error unlinking workflow', 'error');
        return false;
    }
},

            /**
             * Open workflow linking modal (shows available workflows)
             */
            async openWorkflowLinkModal(threadId) {
    console.log('[openWorkflowLinkModal] Opening for thread:', threadId);

    // Get thread data
    const thread = this.threads.find(t => t.thread_id === threadId);
    if (!thread) {
        console.error('[openWorkflowLinkModal] Thread not found:', threadId);
        showNotification('Thread not found', 'error');
        return;
    }

    // Fetch available workflows from automation API
    let workflows = [];
    try {
        const response = await fetch('/api/automation/list', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            workflows = data.workflows || [];
            console.log('[openWorkflowLinkModal] Fetched workflows:', workflows.length);
        } else {
            console.error('[openWorkflowLinkModal] Failed to fetch workflows:', response.status);
        }
    } catch (err) {
        console.error('[openWorkflowLinkModal] Error fetching workflows:', err);
    }

    const modalHTML = `
                    <div class="modal-overlay" id="workflowLinkModalOverlay" onclick="if(event.target.id === 'workflowLinkModalOverlay') document.getElementById('workflowLinkModalOverlay').remove()">
                        <div class="synergy-sync-modal" onclick="event.stopPropagation()">
                            <div class="modal-header">
                                <h3><i class="fas fa-robot"></i> Link to Workflow</h3>
                                <button class="modal-close" onclick="document.getElementById('workflowLinkModalOverlay').remove()">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                            
                            <div class="modal-body">
                                <!-- Thread Info -->
                                <div class="synergy-sync-thread-info">
                                    <strong>Thread:</strong> ${thread.title || 'Untitled'}
                                </div>

                                ${workflows.length === 0 ? `
                                    <div class="synergy-sync-empty">
                                        <i class="fas fa-inbox"></i>
                                        <p>No workflows available</p>
                                        <p style="font-size: 12px; color: var(--text-muted);">Create a workflow in the Visual Automation Canvas first</p>
                                    </div>
                                ` : `
                                    <!-- Search and Sort -->
                                    <div class="synergy-sync-controls">
                                        <div class="synergy-sync-search">
                                            <i class="fas fa-search"></i>
                                            <input type="text" id="workflowLinkSearch" placeholder="Search workflows...">
                                        </div>
                                        <select id="workflowLinkSort" onchange="ThreadManager.filterWorkflows()">
                                            <option value="recent">Recent</option>
                                            <option value="title">Title</option>
                                            <option value="status">Status</option>
                                            <option value="category">Category</option>
                                        </select>
                                    </div>

                                    <!-- Workflow List -->
                                    <div class="synergy-sync-list" id="workflowLinkList">
                                        ${this.renderWorkflowLinkList(workflows)}
                                    </div>
                                `}
                            </div>
                        </div>
                    </div>
                `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Add search listener
    const searchInput = document.getElementById('workflowLinkSearch');
    if (searchInput) {
        searchInput.addEventListener('input', () => this.filterWorkflows());
    }

    // Store thread ID and workflows for later use
    window._workflowLinkThreadId = threadId;
    window._workflows = workflows;
},

/**
 * Render workflow list for linking
 */
renderWorkflowLinkList(workflows) {
    if (!workflows || workflows.length === 0) {
        return '<div class="synergy-sync-empty"><i class="fas fa-inbox"></i><p>No workflows found</p></div>';
    }

    return workflows.map(workflow => {
        const status = workflow.status || 'draft';
        const category = workflow.category || 'other';
        const statusColors = {
            'draft': '#6B7280',
            'active': '#10B981',
            'paused': '#F59E0B',
            'archived': '#EF4444'
        };
        const statusColor = statusColors[status] || '#6B7280';
        const updatedDate = workflow.updated_at ? new Date(workflow.updated_at).toLocaleDateString() : 'Never';
        const shapeCount = workflow.ui_json?.shapes?.length || 0;

        return `
                        <div class="synergy-session-item" onclick="ThreadManager.selectWorkflowToLink('${workflow.slug}', '${workflow.id || workflow.slug}', '${(workflow.title || 'Untitled').replace(/'/g, "\\'")}')">
                            <div class="synergy-session-item-header">
                                <div class="synergy-session-item-icon" style="background: #f97316;">
                                    <i class="fas fa-robot"></i>
                                </div>
                                <div class="synergy-session-item-title">
                                    ${workflow.title || 'Untitled Workflow'}
                                </div>
                                <div class="synergy-session-item-badge" style="background: ${statusColor};">
                                    ${status}
                                </div>
                            </div>
                            <div class="synergy-session-item-meta">
                                <span><i class="fas fa-shapes"></i> ${shapeCount} shapes</span>
                                <span><i class="fas fa-folder"></i> ${category}</span>
                                <span><i class="fas fa-clock"></i> ${updatedDate}</span>
                            </div>
                            <div class="synergy-session-item-slug">
                                <i class="fas fa-hashtag"></i> ${workflow.slug}
                            </div>
                            ${workflow.description ? `<div class="synergy-session-item-desc">${workflow.description}</div>` : ''}
                        </div>
                    `;
    }).join('');
},

            /**
             * Select workflow to link to thread
             */
            async selectWorkflowToLink(workflowSlug, workflowId, workflowTitle) {
    const threadId = window._workflowLinkThreadId;
    if (!threadId) {
        console.error('[selectWorkflowToLink] No thread ID stored');
        return;
    }

    console.log('[selectWorkflowToLink] Linking:', { threadId, workflowSlug, workflowId, workflowTitle });

    // Close modal
    document.getElementById('workflowLinkModalOverlay')?.remove();

    // Link workflow
    await this.linkWorkflow(threadId, workflowId, workflowTitle);
},

/**
 * Filter workflows in link modal
 */
filterWorkflows() {
    const searchInput = document.getElementById('workflowLinkSearch');
    const sortSelect = document.getElementById('workflowLinkSort');
    const listContainer = document.getElementById('workflowLinkList');

    if (!searchInput || !sortSelect || !listContainer) return;

    let workflows = window._workflows || [];
    const searchTerm = searchInput.value.toLowerCase();
    const sortBy = sortSelect.value;

    // Filter by search term
    if (searchTerm) {
        workflows = workflows.filter(workflow => {
            const title = (workflow.title || '').toLowerCase();
            const description = (workflow.description || '').toLowerCase();
            const slug = (workflow.slug || '').toLowerCase();
            const category = (workflow.category || '').toLowerCase();

            return title.includes(searchTerm) ||
                description.includes(searchTerm) ||
                slug.includes(searchTerm) ||
                category.includes(searchTerm);
        });
    }

    // Sort workflows
    workflows.sort((a, b) => {
        switch (sortBy) {
            case 'title':
                return (a.title || '').localeCompare(b.title || '');
            case 'status':
                return (a.status || '').localeCompare(b.status || '');
            case 'category':
                return (a.category || '').localeCompare(b.category || '');
            case 'recent':
            default:
                return new Date(b.updated_at || 0) - new Date(a.updated_at || 0);
        }
    });

    // Re-render list
    listContainer.innerHTML = this.renderWorkflowLinkList(workflows);
},

/**
 * Open workflow details (shows workflow configuration)
 */
openWorkflowDetails(workflowId) {
    // TODO: Implement workflow details modal
    showNotification(`Opening workflow: ${workflowId}`, 'info');
    console.log(`[WorkflowDetails] Opening workflow ${workflowId}`);
},

            // Open Synergy Sync Modal with three options
            async openSynergySyncModal(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) {
        showNotification('Thread not found', 'error');
        return;
    }

    // Fetch all Synergy sessions
    let synergySessions = [];
    try {
        // Try /api/synergy/list first (primary endpoint)
        let resp = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/synergy/list`);
        if (!resp.ok) {
            // Fallback to /api/synergy if /list doesn't exist
            resp = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/synergy`);
        }

        const data = await resp.json();
        console.log('[openSynergySyncModal] Fetched sessions:', data);

        // Handle multiple response formats
        if (Array.isArray(data)) {
            synergySessions = data;
        } else if (data && data.success && Array.isArray(data.sessions)) {
            synergySessions = data.sessions;
        } else if (data && Array.isArray(data.sessions)) {
            synergySessions = data.sessions;
        }

        console.log('[openSynergySyncModal] Parsed sessions:', synergySessions.length, 'sessions');
    } catch (err) {
        console.error('[openSynergySyncModal] Failed to fetch sessions:', err);
    }

    const modalHTML = `
                    <div class="modal-overlay" id="synergySyncModalOverlay" onclick="if(event.target.id === 'synergySyncModalOverlay') document.getElementById('synergySyncModalOverlay').remove()">
                        <div class="synergy-sync-modal" onclick="event.stopPropagation()">
                            <div class="modal-header">
                                <h3><i class="fas fa-link"></i> Link to Synergy Session</h3>
                                <button class="modal-close" onclick="document.getElementById('synergySyncModalOverlay').remove()">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                            
                            <div class="modal-body">
                                <!-- Thread Info -->
                                <div class="synergy-sync-thread-info">
                                    <strong>Thread:</strong> ${thread.title || 'Untitled'}
                                </div>

                                <!-- Tab Navigation -->
                                <div class="synergy-sync-tabs">
                                    <button class="synergy-sync-tab active" data-tab="link" onclick="ThreadManager.switchSynergySyncTab('link')">
                                        <i class="fas fa-link"></i> Link to Existing
                                    </button>
                                    <button class="synergy-sync-tab" data-tab="quick" onclick="ThreadManager.switchSynergySyncTab('quick')">
                                        <i class="fas fa-bolt"></i> Quick Create
                                    </button>
                                    <button class="synergy-sync-tab" data-tab="full" onclick="ThreadManager.switchSynergySyncTab('full')">
                                        <i class="fas fa-plus-circle"></i> Full Create
                                    </button>
                                </div>

                                <!-- Tab Content: Link to Existing -->
                                <div class="synergy-sync-tab-content active" data-tab-content="link">
                                    ${synergySessions.length === 0 ? `
                                        <div class="synergy-sync-empty">
                                            <i class="fas fa-inbox"></i>
                                            <p>No Synergy sessions available</p>
                                            <p style="font-size: 12px; color: var(--text-muted);">Create one using Quick Create or Full Create tabs</p>
                                        </div>
                                    ` : `
                                        <!-- Search and Sort -->
                                        <div class="synergy-sync-controls">
                                            <div class="synergy-sync-search">
                                                <i class="fas fa-search"></i>
                                                <input type="text" id="synergySyncSearch" placeholder="Search sessions...">
                                            </div>
                                            <select id="synergySyncSort" onchange="ThreadManager.filterSynergySessions()">
                                                <option value="recent">Recent</option>
                                                <option value="priority">Priority</option>
                                                <option value="title">Title</option>
                                                <option value="status">Status</option>
                                            </select>
                                        </div>

                                        <!-- Session List -->
                                        <div class="synergy-sync-list" id="synergySyncList">
                                            ${this.renderSynergySessionList(synergySessions)}
                                        </div>
                                    `}
                                </div>

                                <!-- Tab Content: Quick Create -->
                                <div class="synergy-sync-tab-content" data-tab-content="quick">
                                    <div class="synergy-quick-create">
                                        <div class="form-group">
                                            <label for="synergyQuickTitle">Session Title <span style="color: var(--accent-error);">*</span></label>
                                            <input type="text" id="synergyQuickTitle" placeholder="Enter session title..." value="${thread.title || ''}" autofocus>
                                        </div>
                                        <div class="form-group">
                                            <label for="synergyQuickDesc">Description <span style="color: var(--text-muted); font-weight: normal;">(optional)</span></label>
                                            <textarea id="synergyQuickDesc" placeholder="Brief description..." rows="3"></textarea>
                                        </div>
                                        <button class="btn-primary" onclick="ThreadManager.quickCreateAndLink('${threadId}')">
                                            <i class="fas fa-bolt"></i> Create & Link
                                        </button>
                                    </div>
                                </div>

                                <!-- Tab Content: Full Create -->
                                <div class="synergy-sync-tab-content" data-tab-content="full">
                                    <div class="synergy-full-create">
                                        <p style="margin-bottom: 16px; color: var(--text-secondary);">
                                            <i class="fas fa-info-circle"></i> Opens the full Synergy session creation interface with all options.
                                        </p>
                                        <button class="btn-primary" onclick="ThreadManager.fullCreateAndLink('${threadId}')">
                                            <i class="fas fa-plus-circle"></i> Open Full Creator
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Add search listener
    const searchInput = document.getElementById('synergySyncSearch');
    if (searchInput) {
        searchInput.addEventListener('input', () => this.filterSynergySessions());
    }

    // Store thread ID for later use
    window._synergySyncThreadId = threadId;
    window._synergySessions = synergySessions;
},

// Render session list for linking
renderSynergySessionList(sessions) {
    if (!sessions || sessions.length === 0) {
        return '<div class="synergy-sync-empty"><i class="fas fa-inbox"></i><p>No sessions found</p></div>';
    }

    return sessions.map(session => {
        const priority = session.priority || 'medium';
        const status = session.status || 'active';
        const title = session.title || 'Untitled';
        const desc = session.description || 'No description';
        const tags = Array.isArray(session.tags) ? session.tags : (typeof session.tags === 'string' ? JSON.parse(session.tags || '[]') : []);
        const lastActive = session.last_active ? new Date(session.last_active).toLocaleDateString() : 'Never';

        return `
                        <div class="synergy-session-item" data-session-id="${session.session_id}" 
                             data-title="${title.toLowerCase()}" 
                             data-tags="${tags.join(',').toLowerCase()}"
                             data-priority="${priority}"
                             data-status="${status}"
                             onclick="ThreadManager.linkToExistingSession('${session.session_id}')">
                            <div class="synergy-session-header">
                                <span class="synergy-session-title">${title}</span>
                                <span class="synergy-session-priority priority-${priority}">${priority}</span>
                            </div>
                            <div class="synergy-session-desc">${desc}</div>
                            <div class="synergy-session-meta">
                                <span><i class="fas fa-circle" style="color: ${status === 'active' ? 'var(--accent-success)' : 'var(--text-muted)'}; font-size: 8px;"></i> ${status}</span>
                                <span><i class="fas fa-clock"></i> ${lastActive}</span>
                                ${tags.length > 0 ? `<span><i class="fas fa-tags"></i> ${tags.slice(0, 2).join(', ')}${tags.length > 2 ? '...' : ''}</span>` : ''}
                            </div>
                        </div>
                    `;
    }).join('');
},

// Switch tabs in modal
switchSynergySyncTab(tabName) {
    document.querySelectorAll('.synergy-sync-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });
    document.querySelectorAll('.synergy-sync-tab-content').forEach(content => {
        content.classList.toggle('active', content.dataset.tabContent === tabName);
    });
},

// Filter sessions based on search and sort
filterSynergySessions() {
    const searchTerm = document.getElementById('synergySyncSearch')?.value?.toLowerCase() || '';
    const sortBy = document.getElementById('synergySyncSort')?.value || 'recent';
    const sessionItems = document.querySelectorAll('.synergy-session-item');

    // Filter
    sessionItems.forEach(item => {
        const title = item.dataset.title || '';
        const tags = item.dataset.tags || '';
        const matches = title.includes(searchTerm) || tags.includes(searchTerm);
        item.style.display = matches ? 'block' : 'none';
    });

    // Sort visible items
    const visibleItems = Array.from(sessionItems).filter(item => item.style.display !== 'none');
    const container = document.getElementById('synergySyncList');

    if (sortBy === 'title') {
        visibleItems.sort((a, b) => (a.dataset.title || '').localeCompare(b.dataset.title || ''));
    } else if (sortBy === 'priority') {
        const priorityOrder = { high: 0, medium: 1, low: 2 };
        visibleItems.sort((a, b) => priorityOrder[a.dataset.priority] - priorityOrder[b.dataset.priority]);
    } else if (sortBy === 'status') {
        visibleItems.sort((a, b) => (a.dataset.status || '').localeCompare(b.dataset.status || ''));
    }

    // Re-append in sorted order
    visibleItems.forEach(item => container.appendChild(item));
},

            // Link to existing session
            async linkToExistingSession(sessionId) {
    const threadId = window._synergySyncThreadId;
    if (!threadId) {
        showNotification('Thread ID not found', 'error');
        return;
    }

    try {
        const thread = this.threads.find(t => t.id === threadId);
        const resp = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/${threadId}/update`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: thread?.title || '', synergy_card_id: sessionId })
        });
        const data = await resp.json();

        if (data && data.success) {
            // Update local thread state
            if (thread) {
                thread.synergy_card_id = sessionId;
                thread.updated = new Date().toISOString();
            }

            // Preload session into cache and update thread metadata
            try {
                const sresp = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/synergy?ids=${encodeURIComponent(sessionId)}`);
                if (sresp.ok) {
                    const sdata = await sresp.json();
                    if (sdata && sdata.success && sdata.sessions && sdata.sessions[sessionId]) {
                        if (!window._synergySessionCache) window._synergySessionCache = {};
                        window._synergySessionCache[sessionId] = sdata.sessions[sessionId];

                        // Update thread with synergy metadata
                        if (thread) {
                            thread.synergy_card_name = sdata.sessions[sessionId].title;
                            thread.synergy_card_desc = sdata.sessions[sessionId].description;
                            thread.synergy_card_priority = sdata.sessions[sessionId].priority;
                        }
                    }
                }
            } catch (e) {
                console.warn('[linkToExistingSession] Failed to preload session', e);
            }

            // Refresh ALL thread info displays
            this.renderThreadList();
            this.refreshAllThreadInfoCards(threadId);

            document.getElementById('synergySyncModalOverlay')?.remove();
            showNotification('Linked to Synergy session', 'success');
        } else {
            showNotification('Failed to link session', 'error');
        }
    } catch (err) {
        console.error('[linkToExistingSession] Exception:', err);
        showNotification('Error linking session', 'error');
    }
},

            // Quick create and link
            async quickCreateAndLink(threadId) {
    const title = document.getElementById('synergyQuickTitle')?.value?.trim();
    const description = document.getElementById('synergyQuickDesc')?.value?.trim();

    if (!title) {
        showNotification('Please enter a session title', 'error');
        return;
    }

    try {
        // Create session
        const resp = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/synergy/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title,
                description: description || `Linked from thread: ${this.threads.find(t => t.id === threadId)?.title || threadId}`,
                created_by: (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 'user'
            })
        });
        const data = await resp.json();

        if (!data || !data.success || !data.session_id) {
            showNotification('Failed to create Synergy session', 'error');
            return;
        }

        const sessionId = data.session_id;

        // Link to thread
        const thread = this.threads.find(t => t.id === threadId);
        const updateResp = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/${threadId}/update`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: thread?.title || '', synergy_card_id: sessionId })
        });
        const updateData = await updateResp.json();

        if (updateData && updateData.success) {
            // Update local thread state
            if (thread) {
                thread.synergy_card_id = sessionId;
                thread.updated = new Date().toISOString();
                // Add the synergy metadata we just created
                thread.synergy_card_name = title;
                thread.synergy_card_desc = description || `Linked from thread: ${thread.title || threadId}`;
            }

            // Preload session
            try {
                const sresp = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/synergy?ids=${encodeURIComponent(sessionId)}`);
                if (sresp.ok) {
                    const sdata = await sresp.json();
                    if (sdata && sdata.success && sdata.sessions && sdata.sessions[sessionId]) {
                        if (!window._synergySessionCache) window._synergySessionCache = {};
                        window._synergySessionCache[sessionId] = sdata.sessions[sessionId];

                        // Update thread with fetched metadata (in case backend added more fields)
                        if (thread) {
                            thread.synergy_card_name = sdata.sessions[sessionId].title;
                            thread.synergy_card_desc = sdata.sessions[sessionId].description;
                            thread.synergy_card_priority = sdata.sessions[sessionId].priority;
                        }
                    }
                }
            } catch (e) {
                console.warn('[quickCreateAndLink] Failed to preload session', e);
            }

            // Refresh ALL thread info displays
            this.renderThreadList();
            this.refreshAllThreadInfoCards(threadId);

            document.getElementById('synergySyncModalOverlay')?.remove();
            showNotification('Session created and linked', 'success');
        } else {
            showNotification('Session created but failed to link', 'error');
        }
    } catch (err) {
        console.error('[quickCreateAndLink] Exception:', err);
        showNotification('Error creating/linking session', 'error');
    }
},

            // Full create and link
            async fullCreateAndLink(threadId) {
    // Close the Synergy Sync modal
    document.getElementById('synergySyncModalOverlay')?.remove();

    // Switch to Synergy tab
    switchTab('synergy');

    // Store thread ID for auto-linking after creation
    window._pendingLinkThreadId = threadId;

    // Wait a moment for tab to load, then open the edit modal for new session
    setTimeout(() => {
        const thread = this.threads.find(t => t.id === threadId);
        const newSession = {
            session_id: null, // null means create new
            title: thread?.title || 'New Synergy Session',
            description: `Linked from thread: ${thread?.title || threadId}`,
            project_name: '',
            priority: 'medium',
            status: 'active',
            kanban_column: 'backlog',
            tags: [],
            assignees: [],
            documents: [],
            links: [],
            next_steps: [],
            checklist: [],
            thread_ids: [threadId],
            assigned_agents: [],
            notes: '',
            due_date: null
        };

        // Open the edit modal (which also works for creating new sessions)
        if (typeof synergyBoard !== 'undefined' && synergyBoard.openEditModal) {
            synergyBoard.openEditModal(newSession);
            showNotification('Create your Synergy session', 'info');
        } else {
            showNotification('Synergy board not loaded yet. Please try again.', 'error');
        }
    }, 500);
},

getCurrentThread() {
    return this.threads.find(t => t.id === this.currentThreadId);
},

            // Get thread location from backend (more accurate than local state)
            async getThreadLocation(threadId) {
    try {
        // Note: Backend endpoint uses thread_assignments endpoint
        const response = await fetch(`/api/thread-assignments/location/${threadId}?user_id=${window.appUserId || 1}`);
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                console.log(` [getThreadLocation] Thread ${threadId} location:`, data.location || 'Prime/unassigned');
                return data.location; // 'prime', 'agent-1', 'agent-2', 'agent-3', or null
            } else {
                console.warn(`[getThreadLocation] API returned success:false for thread ${threadId}`);
                return null;
            }
        } else {
            console.warn(`[getThreadLocation] Failed to get location for thread ${threadId}: ${response.status}`);
            return null;
        }
    } catch (err) {
        console.error(`[getThreadLocation] Exception:`, err);
        return null;
    }
},

updateCurrentThread(messages) {
    const thread = this.getCurrentThread();
    if (thread) {
        thread.messages = messages;
        thread.updated = new Date().toISOString();
        // Update title from first user message ONLY if title is empty/untitled
        if (messages.length > 0 && (!thread.title || thread.title === 'Untitled Thread' || thread.title.startsWith('thread_'))) {
            const firstUserMsg = messages.find(m => m.role === 'user');
            if (firstUserMsg) {
                thread.title = firstUserMsg.content.substring(0, 50) + (firstUserMsg.content.length > 50 ? '...' : '');
            }
        }

        // UPDATE UI (Added Nov 8, 2025)
        this.updateMessageCount(thread.id);
        this.updateDateTime(thread.id);
        this.updatePrimeHeader(thread.id);
        this.syncAppState(thread.id);

        // CRITICAL: Save messages to database (not just thread metadata)
        this.saveMessagesToBackend(thread);

        // Also save thread metadata (async, don't wait)
        this.saveThreadToBackend(thread);
        this.renderThreadList();
    }
},

switchThread(threadId, forceSwitch = false) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) {
        console.warn(`[switchThread] Thread not found: ${threadId}`);
        return;
    }

    // Check thread assignment via backend (more accurate than thread.agent)
    // Only show options if: 1) Not forcing, 2) Thread assigned to agent (not Prime)
    if (!forceSwitch) {
        this.getThreadLocation(threadId).then(location => {
            // If assigned to an agent (not Prime), expand the card to show options
            if (location && location.startsWith('agent-')) {
                const agentIdMatch = location.match(/agent-(\d+)/);
                if (agentIdMatch) {
                    const agentId = parseInt(agentIdMatch[1]);
                    const threadItem = document.querySelector(`[data-thread-id="${threadId}"]`);

                    console.log(` [switchThread] Thread ${threadId} is assigned to ${location}, showing inline options`);

                    // NEW: Expand card instead of showing modal
                    if (threadItem) {
                        this.showThreadAssignmentOptions(threadId, agentId, threadItem);
                    }
                    return; // Don't proceed with normal switch
                }
            }

            // If assigned to Prime or no assignment, load directly in Prime
            console.log(`✅ [switchThread] Thread ${threadId} location: ${location || 'none'}, loading in Prime`);
            this.loadThreadInPrime(threadId);
        });
        return;
    }

    // Force switch bypasses modal check
    console.log(` [switchThread] Force switch to thread ${threadId}`);
    this.loadThreadInPrime(threadId);
},

// Load thread in Prime panel (extracted for reuse)
loadThreadInPrime(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) {
        console.error(`[loadThreadInPrime] Thread not found: ${threadId}`);
        return;
    }

    // CRITICAL: Check if thread is already loaded in an agent
    if (typeof MultiAgent !== 'undefined') {
        const currentLocation = MultiAgent.getThreadCurrentLocation(threadId);
        if (currentLocation && currentLocation.startsWith('agent-')) {
            const agentId = parseInt(currentLocation.replace('agent-', ''));
            console.warn(`[LOAD] Thread ${threadId} is already loaded in ${currentLocation}`);
            console.log(`[ISOLATION]  Clearing ${currentLocation} - thread moving to Prime`);
            MultiAgent.clearAgentThread(agentId);
            console.log(`[ISOLATION] ✅ ${currentLocation} session cleared (was: ${threadId})`);
        }
    }

    this.currentThreadId = threadId;

    //  Clear attached files when switching threads
    console.log('[CLEAN] Clearing attached files on thread switch...');
    if (window.clearChatAttachedFiles) {
        window.clearChatAttachedFiles();
    }

    // Clear current messages
    const messagesContainer = document.getElementById('ai-chat-messages');
    messagesContainer.innerHTML = '';

    // Ensure messages is always an array
    if (!Array.isArray(thread.messages)) {
        thread.messages = [];
    }

    // ALWAYS hide welcome when loading a thread (even if empty)
    const welcomeContainer = document.getElementById('prime-welcome-container');
    if (welcomeContainer) {
        welcomeContainer.style.display = 'none';
        console.log('[WELCOME] Hidden - thread loaded:', threadId);
    }                // Load thread messages from backend if not already loaded
    if (thread.messages.length === 0 && thread.message_count > 0) {
        console.log(`[THREAD LOAD] Loading ${thread.message_count} messages from backend...`);
        this.loadMessagesForThread(threadId).then(() => {
            // Messages loaded, render them
            const updatedThread = this.threads.find(t => t.id === threadId);
            if (updatedThread && Array.isArray(updatedThread.messages)) {
                updatedThread.messages.forEach(msg => {
                    addChatMessage(msg.role, msg.content);
                });
                // Update AppState
                if (typeof AppState !== 'undefined') {
                    AppState.chatMessages = [...updatedThread.messages];
                    AppState.sessionId = threadId;
                }
            }
        });
    } else {
        // Messages already in memory
        if (Array.isArray(thread.messages) && thread.messages.length > 0) {
            thread.messages.forEach(msg => {
                addChatMessage(msg.role, msg.content);
            });
            // Update AppState
            if (typeof AppState !== 'undefined') {
                AppState.chatMessages = [...thread.messages];
                AppState.sessionId = threadId;
            }
        }
    }

    // Update centralized assignment tracker - thread now in Prime
    if (typeof this.assignThread === 'function') {
        this.assignThread(threadId, 'prime');
        console.log(`[ThreadManager] [OK] Thread ${threadId} assigned to 'prime' in centralized tracker`);
    }

    // Update Prime header with thread info (using comprehensive function)
    this.updatePrimeHeader(threadId);
    this.syncAppState(threadId);

    // Show Prime input wrapper (thread is now loaded)
    const primeInputWrapper = document.querySelector('.ai-chat-input-wrapper');
    if (primeInputWrapper) {
        primeInputWrapper.style.display = 'flex';
        console.log('[UI] Showed Prime input wrapper (thread switched)');
    }

    // Enable Prime send button
    const primeSendBtn = document.querySelector('.send-btn');
    if (primeSendBtn) {
        primeSendBtn.disabled = false;
        primeSendBtn.style.opacity = '1';
        primeSendBtn.style.cursor = 'pointer';
    }

    console.log(`[ENABLED] Input enabled for Prime`);

    this.renderThreadList();
    this.closeThreadMenu();

    // ✅ VALIDATE: Check session isolation after loading
    if (typeof MultiAgent !== 'undefined') {
        setTimeout(() => {
            MultiAgent.validateSessionIsolation(threadId, 'prime');
        }, 100);
    }
},

// Show assignment options inline (expandable card)
showThreadAssignmentOptions(threadId, agentId, threadItem) {
    // Close any other expanded cards first
    document.querySelectorAll('.thread-item.show-options').forEach(item => {
        if (item.dataset.threadId !== threadId) {
            item.classList.remove('show-options');
        }
    });

    // Toggle options for this card
    const isExpanded = threadItem.classList.contains('show-options');

    if (isExpanded) {
        // Collapse if already expanded
        threadItem.classList.remove('show-options');
        console.log(`✖️ [showThreadAssignmentOptions] Collapsed options for thread ${threadId}`);
    } else {
        // Expand and show options
        threadItem.classList.add('show-options');

        // Store current context for option handlers
        threadItem.dataset.currentAgentId = agentId;

        console.log(`✅ [showThreadAssignmentOptions] Expanded options for thread ${threadId} (agent ${agentId})`);

        // Scroll card into view
        threadItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
},

            // Handle option selection from expanded card
            async handleThreadAssignmentOption(threadId, option) {
    const threadItem = document.querySelector(`[data-thread-id="${threadId}"]`);
    const agentId = threadItem?.dataset.currentAgentId;

    console.log(` [handleThreadAssignmentOption] Thread ${threadId}, Option: ${option}`);

    switch (option) {
        case 'move-to-prime':
            // Move to Prime and view
            // NOTE: loadThreadInPrime() will automatically clear agent via isolation check
            await this.assignThread(threadId, 'prime');
            this.switchThread(threadId, true); // Force switch

            // Collapse the options card
            if (threadItem) {
                threadItem.classList.remove('show-options');
            }
            break;

        case 'view-in-agent':
            // View in agent dashboard
            switchTab('multi-agent');

            // NOTE: loadThreadIntoAgent() will automatically clear Prime/other agents
            if (agentId && MultiAgent.agents[agentId]) {
                const thread = this.threads.find(t => t.id === threadId);
                if (thread) {
                    MultiAgent.loadThreadIntoAgent(parseInt(agentId), thread);
                }
            } else {
                // Agent column doesn't exist yet - create it first
                MultiAgent.addAgentColumn(parseInt(agentId));
                setTimeout(() => {
                    const thread = this.threads.find(t => t.id === threadId);
                    if (thread) {
                        MultiAgent.loadThreadIntoAgent(parseInt(agentId), thread);
                    }
                }, 100);
            }

            // Collapse the options card
            if (threadItem) {
                threadItem.classList.remove('show-options');
            }
            break;

        case 'unload-only':
            // Unload from agent without viewing
            await this.assignThread(threadId, 'prime');

            // Clear agent UI explicitly (no auto-load will trigger)
            if (agentId && typeof MultiAgent !== 'undefined') {
                MultiAgent.clearAgentThread(parseInt(agentId));
            }

            // Refresh thread list to update badges
            await this.loadThreadsFromBackend();
            await this.renderThreadList();

            showNotification('Thread unloaded from agent', 'success', 2000);
            break;
    }

    // Collapse the options card after any action
    if (threadItem) {
        threadItem.classList.remove('show-options');
    }
},

// Inline title editing (double-click to edit)
startInlineTitleEdit(location) {
    console.log(`✏️ [startInlineTitleEdit] Location: ${location}`);

    const titleEl = document.getElementById(`${location}-thread-title`);
    if (!titleEl) {
        console.error(`[ERROR] Title element not found: ${location}-thread-title`);
        return;
    }

    const threadId = titleEl.dataset.threadId;
    if (!threadId) {
        console.warn(`[WARN] No thread loaded to edit`);
        return;
    }

    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) {
        console.error(`[ERROR] Thread not found: ${threadId}`);
        return;
    }

    const currentTitle = thread.title || 'Untitled Thread';

    // Create input field
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'thread-title-input';
    input.value = currentTitle;

    // Replace content with input
    titleEl.innerHTML = '';
    titleEl.classList.add('editing');
    titleEl.appendChild(input);
    input.focus();
    input.select();

    // Save on Enter or blur
    const saveEdit = async () => {
        const newTitle = input.value.trim();

        if (newTitle && newTitle !== currentTitle) {
            console.log(` [startInlineTitleEdit] Saving title: "${currentTitle}" → "${newTitle}"`);

            // Update local thread
            thread.title = newTitle;

            // Save to backend
            try {
                const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/save`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        thread_id: threadId,
                        name: newTitle
                    })
                });

                if (response.ok) {
                    console.log(`[OK] [startInlineTitleEdit] Title saved to backend`);
                    showNotification(`Thread renamed to "${newTitle}"`, 'success');
                } else {
                    console.error(`[ERROR] [startInlineTitleEdit] Failed to save title`);
                    showNotification('Failed to save title', 'error');
                }
            } catch (error) {
                console.error(`[ERROR] [startInlineTitleEdit] Error:`, error);
                showNotification('Error saving title', 'error');
            }
        }

        // Restore display
        titleEl.classList.remove('editing');
        if (location === 'prime') {
            this.updatePrimeHeader(thread);
        } else {
            // For agent columns, update their header
            const agentId = parseInt(location.replace('agent-', ''));
            if (typeof MultiAgent !== 'undefined') {
                MultiAgent.loadedThreads[agentId].threadTitle = newTitle;
                MultiAgent.updateAgentHeader(agentId);
            }
        }

        this.renderThreadList();
    };

    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            saveEdit();
        }
    });

    input.addEventListener('blur', saveEdit);

    // Cancel on Escape
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            e.preventDefault();
            titleEl.classList.remove('editing');
            if (location === 'prime') {
                this.updatePrimeHeader(thread);
            } else {
                const agentId = parseInt(location.replace('agent-', ''));
                if (typeof MultiAgent !== 'undefined') {
                    MultiAgent.updateAgentHeader(agentId);
                }
            }
        }
    });
},

deleteThread(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;

    // Show custom confirmation modal
    showConfirmation(
        'Delete Thread?',
        `Are you sure you want to delete "${thread.title}"? This action cannot be undone.`,
        async () => {  // Make async to call backend
            // STEP 1: Call backend DELETE API
            try {
                const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/${threadId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}`
                    }
                });

                if (!response.ok) {
                    throw new Error(`Failed to delete thread from database: ${response.statusText}`);
                }

                const data = await response.json();
                console.log(`✅ Thread ${threadId} deleted from database:`, data);

            } catch (error) {
                console.error('[DELETE] Backend delete failed:', error);
                showNotification('Failed to delete thread from database', 'error');
                return; // Don't proceed with UI removal if backend fails
            }

            // STEP 2: Remove from in-memory array
            this.threads = this.threads.filter(t => t.id !== threadId);

            // STEP 3: Clear from any active location
            if (typeof MultiAgent !== 'undefined') {
                // Check if thread is loaded in any agent
                for (const [agentId, threadInfo] of Object.entries(MultiAgent.loadedThreads)) {
                    if (threadInfo && threadInfo.threadId === threadId) {
                        MultiAgent.clearAgentThread(parseInt(agentId));
                        console.log(`[DELETE] Cleared thread from agent-${agentId}`);
                    }
                }
            }

            // STEP 4: If deleting current Prime thread, show new chat modal
            if (this.currentThreadId === threadId) {
                this.currentThreadId = null;
                const primeMessages = document.getElementById('ai-chat-messages');
                if (primeMessages) primeMessages.innerHTML = '';
                this.showNewChatModal('prime');
            } else {
                this.renderThreadList();
            }

            showNotification('Thread deleted successfully', 'success');
            console.log('✅ Thread deleted:', thread.title);
        }
    );
},

startRename(threadId) {
    const titleSpan = document.getElementById(`thread-title-${threadId}`);
    if (!titleSpan) return;

    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;

    // Create input field
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'thread-item-title-input';
    input.value = thread.title;

    // Replace span with input
    titleSpan.replaceWith(input);
    input.focus();
    input.select();

    // Save on enter or blur
    const saveRename = () => {
        const newTitle = input.value.trim();
        if (newTitle && newTitle !== thread.title) {
            thread.title = newTitle;
            thread.updated = new Date().toISOString();
            // TODO: Call backend update API when implemented
            console.log('✏️ Thread renamed to:', newTitle);
        }
        this.renderThreadList();
    };

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            saveRename();
        } else if (e.key === 'Escape') {
            e.preventDefault();
            this.renderThreadList();
        }
    });

    input.addEventListener('blur', saveRename);
},

editThread(threadId) {
    // Open the thread in the main chat area for editing
    console.log(' [editThread] Opening thread for editing:', threadId);
    this.switchThread(threadId);
    this.closeThreadMenu();
},

copySessionId(sessionId, buttonElement) {
    // Copy to clipboard
    navigator.clipboard.writeText(sessionId).then(() => {
        console.log('Session ID copied:', sessionId);

        // Visual feedback
        const icon = buttonElement.querySelector('i');
        const originalClass = icon.className;
        icon.className = 'fas fa-check';
        buttonElement.classList.add('copied');

        // Show notification
        if (typeof showNotification === 'function') {
            showNotification('Session ID copied to clipboard', 'success', 2000);
        }

        // Reset after 2 seconds
        setTimeout(() => {
            icon.className = originalClass;
            buttonElement.classList.remove('copied');
        }, 2000);
    }).catch(err => {
        console.error(' Failed to copy session ID:', err);
        if (typeof showNotification === 'function') {
            showNotification('Failed to copy session ID', 'error', 2000);
        }
    });
},

copyThreadId(threadId) {
    navigator.clipboard.writeText(threadId).then(() => {
        console.log('Thread ID copied:', threadId);
        if (typeof showNotification === 'function') {
            showNotification('Thread ID copied to clipboard', 'success', 2000);
        }
    }).catch(err => {
        console.error('Failed to copy thread ID:', err);
        if (typeof showNotification === 'function') {
            showNotification('Failed to copy thread ID', 'error', 2000);
        }
    });
},

copySynergyInfo(synergyId, synergyName) {
    const text = `Session ID: ${synergyId}\nName: ${synergyName}`;
    navigator.clipboard.writeText(text).then(() => {
        console.log('Synergy info copied:', synergyId, synergyName);
        if (typeof showNotification === 'function') {
            showNotification('Synergy session info copied!', 'success', 2000);
        }
    }).catch(err => {
        console.error('Failed to copy Synergy info:', err);
        if (typeof showNotification === 'function') {
            showNotification('Failed to copy Synergy info', 'error', 2000);
        }
    });
},

            async handleThreadDoubleClick(threadId, currentLocation) {
    console.log(`?� [handleThreadDoubleClick] Thread ${threadId}, Location: ${currentLocation}`);

    // If thread is assigned to an agent, show options instead of opening
    if (currentLocation && currentLocation.startsWith('agent-')) {
        console.log(` [handleThreadDoubleClick] Thread assigned to ${currentLocation}, showing options`);

        // Get agent ID from location (e.g., "agent-2" -> 2)
        const agentIdMatch = currentLocation.match(/agent-(\d+)/);
        if (agentIdMatch) {
            const agentId = parseInt(agentIdMatch[1]);
            const threadItem = document.querySelector(`[data-thread-id="${threadId}"]`);

            if (threadItem) {
                this.showThreadAssignmentOptions(threadId, agentId, threadItem);
            }
        }
    } else {
        // Thread in Prime, thread-history, or unassigned - open in Prime
        console.log(`[handleThreadDoubleClick] Opening thread in Prime`);
        this.openThreadInPrime(threadId);
    }
},

openThreadInPrime(threadId) {
    console.log('Opening thread in Prime AI:', threadId);
    const primeTab = document.querySelector('[data-chat-id="prime"]');
    if (primeTab) primeTab.click();
    this.switchThread(threadId, true); // Force switch to bypass any checks
    this.closeThreadMenu();
    if (typeof showNotification === 'function') {
        showNotification('Thread opened in Prime AI', 'success', 2000);
    }
},

archiveThread(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;
    showConfirmation(
        'Archive Thread?',
        `Archive "${thread.title}"? You can restore it later from the Archived filter.`,
        () => {
            thread.archived = true;
            thread.updated = new Date().toISOString();
            this.saveThreadToBackend(thread);
            this.renderThreadList();
            if (typeof showNotification === 'function') {
                showNotification('Thread archived', 'success', 2000);
            }
        }
    );
},

            async unloadThread(threadId) {
    console.log(` [unloadThread] Unloading thread ${threadId} from agent`);

    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) {
        console.error('[unloadThread] Thread not found:', threadId);
        return;
    }

    try {
        // Get current location from backend (FRESH data, not cached)
        const currentLocation = await this.getThreadLocation(threadId);

        console.log(` [unloadThread] Current location from backend: ${currentLocation || 'none'}`);

        // Determine the agent from visual badge (in case backend is stale)
        const threadCard = document.querySelector(`[data-thread-id="${threadId}"]`);
        const agentBadge = threadCard?.querySelector('.thread-item-agent-badge');
        const isInAgent = agentBadge && agentBadge.classList.contains('agent');

        let locationToShow = currentLocation;

        // If visual shows agent but backend says Prime, trust the visual (stale backend)
        if ((!currentLocation || currentLocation === 'prime') && isInAgent) {
            const agentText = agentBadge.textContent.trim();
            locationToShow = agentText || 'an agent';
            console.log(`⚠️ [unloadThread] Backend says Prime but visual shows ${agentText} - proceeding with unload`);
        } else if (!currentLocation || currentLocation === 'prime') {
            // Both backend and visual agree it's in Prime
            if (typeof showNotification === 'function') {
                showNotification('Thread is already in Prime', 'info', 2000);
            }
            return;
        }

        // Show confirmation
        showConfirmation(
            'Unload Thread?',
            `Move "${thread.title}" from ${locationToShow} back to Prime?`,
            async () => {
                try {
                    console.log(` [unloadThread] Executing unload: ${threadId} → prime`);

                    // STEP 1: Assign to Prime (forces backend update)
                    await this.assignThread(threadId, 'prime');

                    // STEP 2: Clear agent columns (all of them, to be safe)
                    if (typeof MultiAgent !== 'undefined') {
                        [1, 2, 3].forEach(agentId => {
                            const loadedThread = MultiAgent.loadedThreads[agentId];
                            if (loadedThread && loadedThread.threadId === threadId) {
                                console.log(` [unloadThread] Clearing agent-${agentId}`);
                                MultiAgent.unloadThreadFromAgent(`agent-${agentId}`, threadId);
                            }
                        });
                    }

                    // STEP 3: Wait a moment for backend to process
                    console.log(`⏳ [unloadThread] Waiting for backend to sync...`);
                    await new Promise(resolve => setTimeout(resolve, 300));

                    // STEP 4: Update ONLY this thread card's badge (inline, no panel close)
                    console.log(` [unloadThread] Updating thread card badge inline...`);

                    // Find the thread card in Thread History
                    const threadCard = document.querySelector(`[data-thread-id="${threadId}"]`);
                    if (threadCard) {
                        // Update the agent badge to "Prime"
                        const agentBadge = threadCard.querySelector('.thread-item-agent-badge');
                        if (agentBadge) {
                            agentBadge.className = 'thread-item-agent-badge prime';
                            agentBadge.innerHTML = '<i class="fas fa-crown"></i> Prime';
                        }

                        // Remove the unload button (since now in Prime)
                        const unloadBtn = threadCard.querySelector('.thread-action-btn.unload');
                        if (unloadBtn) {
                            unloadBtn.remove();
                        }

                        console.log(`✅ [unloadThread] Badge updated inline (Thread History stays open)`);
                    }

                    // Refresh thread data in background for next time (but don't re-render panel)
                    await this.loadThreadsFromBackend();

                    // STEP 5: Refresh Prime header if this was the current thread
                    if (this.currentThreadId === threadId) {
                        this.updatePrimeHeader(threadId);
                    }

                    if (typeof showNotification === 'function') {
                        showNotification('Thread moved to Prime', 'success', 2000);
                    }

                    console.log(`✅ [unloadThread] Thread ${threadId} unloaded successfully`);
                } catch (error) {
                    console.error('[unloadThread] Error unloading thread:', error);
                    if (typeof showNotification === 'function') {
                        showNotification('Failed to unload thread', 'error', 3000);
                    }
                }
            }
        );
    } catch (error) {
        console.error('[unloadThread] Error checking thread location:', error);
        if (typeof showNotification === 'function') {
            showNotification('Error unloading thread', 'error', 3000);
        }
    }
},

            async saveThreadToBackend(thread) {
    // NEW: Save thread to backend database (not localStorage)
    // UPDATED: Include location for Prime/Agent assignment integration
    try {
        // 🔧 FIX: Don't try to save empty threads (backend will reject with 400)
        if (!thread.messages || thread.messages.length === 0) {
            console.log(`[SKIP] Not saving thread ${thread.id} - no messages yet`);
            return true; // Return true to avoid error logs
        }

        // Determine thread location from current assignments
        const assignments = await this.getThreadAssignments();
        let location = 'prime'; // Default to Prime

        // Check if thread is assigned to an agent
        for (const [agentLocation, sessionId] of Object.entries(assignments)) {
            if (sessionId === thread.id) {
                location = agentLocation;
                break;
            }
        }

        const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1,
                thread_id: thread.id,
                name: thread.title || thread.name || 'Untitled Thread',  // CRITICAL: Backend expects 'name' field (see sessions.threads schema)
                messages: thread.messages || [],
                agent: thread.agent || 'main',
                location: location,  // NEW: Include Prime/Agent location
                archived: thread.archived || false
            })
        });

        const data = await response.json();
        if (data.success) {
            console.log(` Thread saved to backend: ${thread.id} (location: ${location})`);
            return true;
        } else {
            console.error('[ERROR] Failed to save thread to backend:', data.error);
            return false;
        }
    } catch (error) {
        console.error('[ERROR] Backend save error:', error);
        return false;
    }
},

            async loadMessagesForThread(threadId) {
    // Load messages from backend for a specific thread
    try {
        console.log(`[MESSAGE LOAD] Fetching messages for thread ${threadId}...`);

        const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/messages/get?thread_id=${threadId}`);
        const data = await response.json();

        // API returns: {success: true, message: '...', data: {messages: [...], count: N}}
        if (data.success && data.data) {
            const messages = data.data.messages || data.data || [];
            console.log(`[MESSAGE LOAD] Loaded ${messages.length} messages`);

            // Update thread with loaded messages
            const thread = this.threads.find(t => t.id === threadId);
            if (thread) {
                thread.messages = Array.isArray(messages) ? messages : [];
                thread.message_count = messages.length;
            }

            return messages;
        } else {
            console.error('[MESSAGE LOAD ERROR] Failed:', data);
            return [];
        }
    } catch (error) {
        console.error('[MESSAGE LOAD ERROR] Exception:', error);
        return [];
    }
},

            async saveMessagesToBackend(thread) {
    // NEW: Save messages directly to messages table (CRITICAL FIX)
    // This links messages to threads so they show up in thread list with message counts
    try {
        console.log('[MESSAGE SAVE] saveMessagesToBackend called', thread);

        if (!thread || !thread.id) {
            console.error('[MESSAGE SAVE] No thread provided');
            return false;
        }

        // 🔧 CRITICAL FIX: Deduplicate message content BEFORE saving
        const messages = (thread.messages || []).map(msg => {
            if (msg.role === 'user' && Array.isArray(msg.content)) {
                // Deduplicate text blocks in user messages
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

                // Preserve non-text blocks (tool_result, etc.)
                const nonTextBlocks = msg.content.filter(b => b && b.type !== 'text');
                const deduped = [...uniqueTexts, ...nonTextBlocks];

                if (textBlocks.length > uniqueTexts.length) {
                    console.warn(`[DEDUP SAVE] User message had ${textBlocks.length} text blocks, saved ${uniqueTexts.length}`);
                }

                return { ...msg, content: deduped };
            }
            return msg;
        });

        console.log(`[MESSAGE SAVE] Thread ${thread.id} has ${messages.length} messages`, messages);

        if (messages.length === 0) {
            console.warn(`[MESSAGE SAVE] No messages to save for thread ${thread.id}`);
            return true;
        }

        const userId = (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1;

        console.log(`[MESSAGE SAVE] Saving ${messages.length} messages to thread ${thread.id}`, {
            thread_id: thread.id,
            user_id: userId,
            message_count: messages.length
        });

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
        console.log('[MESSAGE SAVE] API Response:', data);

        if (data.success) {
            const saved = data.data?.messages_saved || data.messages_saved || 0;
            console.log(`[MESSAGE SAVE] SUCCESS! Saved ${saved} messages to thread ${thread.id}`);

            // Update thread message_count
            thread.message_count = saved;
            this.updateMessageCount(thread.id);

            return true;
        } else {
            console.error('[MESSAGE SAVE ERROR] Failed:', data.error || data);
            return false;
        }
    } catch (error) {
        console.error('[MESSAGE SAVE ERROR] Exception:', error);
        return false;
    }
},

            async loadThreadsFromBackend() {
    // NEW: Load threads from backend database (not localStorage)
    try {
        // ✅ Get user_id from UserAuth (set by ensureCorrectUserData)
        // Backend returns both 'id' and 'user_id', check both for compatibility
        const userId = (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) ?
            (UserAuth.user.id || UserAuth.user.user_id) : null;

        if (!userId) {
            console.error('❌ [THREADS] Cannot load threads: user_id not available');
            console.log('⚠️ [THREADS] UserAuth.user:', UserAuth.user);
            return false;
        }

        console.log(` [THREADS] Loading threads for user_id: ${userId}`);

        const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/list?user_id=${userId}`);
        const data = await response.json();

        // Handle both response formats: {threads: [...]} and {data: {threads: [...]}}
        const threads = data.threads || (data.data && data.data.threads) || [];

        if (data.success && threads && threads.length > 0) {
            // Debug: Check first thread for location data
            if (threads[0]) {
                console.log('?? [DEBUG] First thread from backend:', {
                    id: threads[0].id,
                    location: threads[0].location,
                    agent: threads[0].agent,
                    hasLocation: 'location' in threads[0],
                    hasAgent: 'agent' in threads[0]
                });
            }

            this.threads = threads.map(thread => {
                // Backend returns 'location' field (agent-1, agent-2, etc.)
                const location = thread.location || thread.agent || 'prime';
                // CRITICAL: Backend uses 'name' field, not 'title' (see sessions.threads schema)
                const threadTitle = thread.name || thread.title || 'Untitled Thread';
                return {
                    id: thread.id || thread.thread_slug,  // Use thread_slug (e.g., 1762614784052)
                    thread_id: thread.thread_id,  // Database ID (e.g., 1)
                    title: threadTitle,  // Map 'name' field to 'title' for frontend consistency
                    name: threadTitle,   // Keep 'name' for backward compatibility
                    messages: thread.messages || [],  // Messages array (empty, loaded separately)
                    message_count: thread.message_count || 0,  // Message count from database
                    created: thread.created || thread.created_at || new Date().toISOString(),
                    updated: thread.updated || thread.updated_at || new Date().toISOString(),
                    archived: thread.archived || false,
                    location: location,  // Thread assignment location (agent-1, agent-2, prime)
                    agent: location === 'prime' ? null : location,  // Agent ID (null for prime)
                    tags: thread.tags || [],
                    synergy_card_id: thread.synergy_card_id || null
                };
            });
            console.log('✅ [DATA] Threads loaded from backend:', this.threads.length);
            console.log(' [DATA] Thread IDs:', this.threads.map(t => t.id));
            return true;
        } else {
            console.warn('[WARN] No threads from backend, starting fresh');
            console.log('[DEBUG] Response data:', data);
            this.threads = [];
            return false;
        }
    } catch (error) {
        console.error(' Failed to load threads from backend:', error);
        // Fallback to localStorage ONLY if backend fails
        try {
            const saved = localStorage.getItem('ai_chat_threads');
            if (saved) {
                this.threads = JSON.parse(saved);
                console.log('[DATA] Fallback: Loaded from localStorage:', this.threads.length);
            }
        } catch (e) {
            this.threads = [];
        }
        return false;
    }
},

startAutoSave() {
    // DISABLED: Auto-save now happens after each AI response via updateCurrentThread()
    // No need for periodic auto-save which was causing duplicate saves
    console.log('ℹ️ Auto-save disabled - saves happen after each AI response');
},

stopAutoSave() {
    if (this.autoSaveInterval) {
        clearInterval(this.autoSaveInterval);
        this.autoSaveInterval = null;
    }
},

// ========================================
// UI UPDATE FUNCTIONS (Added Nov 8, 2025)
// ========================================

/**
 * Update Prime AI Chat Header with thread info
 * NOW USES UNIVERSAL renderThreadInfoContainer() - No manual DOM manipulation
 */
updatePrimeHeader(threadId) {
    console.log('?? [updatePrimeHeader] Called with threadId:', threadId);

    const container = document.getElementById('prime-thread-info');
    if (!container) {
        console.error('? [updatePrimeHeader] Prime thread-info container not found');
        return;
    }

    if (!threadId) {
        // No thread - show welcome message
        this.initWelcomeMessage('prime');
        console.log('? [updatePrimeHeader] Prime header showing welcome message (no thread)');
    } else {
        // Verify thread exists in memory
        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) {
            console.error(`? [updatePrimeHeader] Thread ${threadId} not found in ThreadManager.threads array`);
            console.log('?? [updatePrimeHeader] Available thread IDs:', this.threads.map(t => t.id));
            console.log('?? [updatePrimeHeader] Total threads:', this.threads.length);
            return;
        }

        console.log('?? [updatePrimeHeader] Rendering thread info container for:', threadId);
        console.log('?? [updatePrimeHeader] Thread data:', { id: thread.id, title: thread.title, msgCount: thread.message_count });

        // Inject universal thread-info card
        const html = this.renderThreadInfoContainer('prime', threadId, false);
        console.log('?? [updatePrimeHeader] Generated HTML length:', html ? html.length : 0);

        container.innerHTML = html;
        console.log('? [updatePrimeHeader] Prime header updated with universal card for thread:', threadId);
        console.log('?? [updatePrimeHeader] Container innerHTML length:', container.innerHTML.length);
    }
},

/* OLD updateAgentHeader() DELETED - Now handled by MultiAgent.updateAgentHeader() which calls renderThreadInfoContainer() */

// ============================================================
// COPY THREAD FUNCTIONALITY
// ============================================================
/**
 * Toggle copy menu visibility
 * @param {string} threadId - Thread ID
 */
toggleCopyMenu(threadId) {
    const menu = document.getElementById(`copy-menu-${threadId}`);
    if (menu) {
        menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
    }
},

            /**
             * Copy thread content to clipboard in specified format
             * @param {string} threadId - Thread ID
             * @param {string} format - 'simple', 'detailed', or 'json'
             */
            async copyThreadContent(threadId, format) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) {
        console.error(`Thread ${threadId} not found`);
        return;
    }

    let content = '';
    switch (format) {
        case 'simple':
            content = this._formatSimple(thread);
            break;
        case 'detailed':
            content = this._formatDetailed(thread);
            break;
        case 'json':
            content = this._formatJSON(thread);
            break;
        default:
            console.error(`Unknown format: ${format}`);
            return;
    }

    try {
        await navigator.clipboard.writeText(content);
        console.log(`Thread ${threadId} copied to clipboard (${format} format)`);

        // Show feedback
        const copyBtn = document.querySelector(`[onclick*="copyThreadContent('${threadId}'"]`);
        if (copyBtn) {
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'Copied!';
            setTimeout(() => {
                copyBtn.textContent = originalText;
            }, 2000);
        }

        // Close menu
        this.toggleCopyMenu(threadId);
    } catch (error) {
        console.error('Failed to copy to clipboard:', error);
        alert('Failed to copy to clipboard. Please try again.');
    }
},

/**
 * Format thread as simple markdown (user-friendly)
 */
_formatSimple(thread) {
    let output = `# ${thread.title || 'Untitled Thread'}\n\n`;

    if (thread.messages && thread.messages.length > 0) {
        thread.messages.forEach((msg, index) => {
            const role = msg.role === 'user' ? 'You' : 'AI';
            const content = this._extractTextFromContent(msg.content);
            output += `**${role}:**\n${content}\n\n---\n\n`;
        });
    } else {
        output += '*No messages yet*\n';
    }

    return output;
},

/**
 * Format thread with detailed metadata
 */
_formatDetailed(thread) {
    let output = `# ${thread.title || 'Untitled Thread'}\n\n`;
    output += `**Thread ID:** ${thread.id}\n`;
    output += `**Created:** ${new Date(thread.created).toLocaleString()}\n`;
    output += `**Updated:** ${new Date(thread.updated || thread.created).toLocaleString()}\n`;
    output += `**Messages:** ${thread.message_count || (thread.messages?.length || 0)}\n`;

    if (thread.synergy_card_id) {
        output += `**Synergy Card:** ${thread.synergy_card_name || thread.synergy_card_id}\n`;
    }

    output += `\n---\n\n`;

    if (thread.messages && thread.messages.length > 0) {
        thread.messages.forEach((msg, index) => {
            const role = msg.role === 'user' ? 'You' : 'AI';
            const timestamp = msg.timestamp ? new Date(msg.timestamp).toLocaleString() : 'Unknown time';
            const content = this._extractTextFromContent(msg.content);

            output += `### Message ${index + 1} - ${role}\n`;
            output += `**Time:** ${timestamp}\n`;

            if (msg.response_time) {
                output += `**Response Time:** ${(msg.response_time / 1000).toFixed(2)}s\n`;
            }

            if (msg.tools_used) {
                output += `**Tools Used:** ${msg.tools_used}\n`;
            }

            output += `\n${content}\n\n---\n\n`;
        });
    } else {
        output += '*No messages yet*\n';
    }

    return output;
},

/**
 * Format thread as JSON (for developers/debugging)
 */
_formatJSON(thread) {
    // Create a clean copy without circular references
    const cleanThread = {
        id: thread.id,
        title: thread.title,
        created: thread.created,
        updated: thread.updated,
        message_count: thread.message_count,
        synergy_card_id: thread.synergy_card_id,
        synergy_card_name: thread.synergy_card_name,
        location: thread.location,
        messages: thread.messages?.map(msg => ({
            role: msg.role,
            content: msg.content,
            timestamp: msg.timestamp,
            response_time: msg.response_time,
            tools_used: msg.tools_used,
            thinking: msg.thinking
        })) || []
    };

    return JSON.stringify(cleanThread, null, 2);
},

/**
 * Extract text content from message (handles both string and array formats)
 */
_extractTextFromContent(content) {
    if (typeof content === 'string') {
        return content;
    }

    if (Array.isArray(content)) {
        // Extract text from content blocks
        return content
            .filter(block => block.type === 'text' || block.text)
            .map(block => block.text || block.content || '')
            .join('\n\n');
    }

    return String(content);
},

// ============================================================
// UNIVERSAL THREAD INFO CONTAINER RENDERER (REFACTORED - Phase 2)
// ============================================================
/**
 * Render Unified Thread Info Container (for Prime, Agents, and Synergy cards)
 * This replaces the old inconsistent thread-info displays with a unified structure
 * 
 * REFACTORED: Now uses ThreadCardTemplates module for HTML generation
 * 
 * @param {string} location - 'prime', 'agent-1', 'agent-2', 'synergy', etc.
 * @param {string} threadId - Thread ID
 * @param {boolean} compact - If true, use compact styling for agents/synergy
 * @returns {string} HTML string for thread-info container
 */
renderThreadInfoContainer(location, threadId, compact = false) {
    console.log(`?? [renderThreadInfoContainer] Called:`, { location, threadId, compact });
    console.log(`?? [renderThreadInfoContainer] Total threads:`, this.threads.length);
    console.log(`?? [renderThreadInfoContainer] Thread IDs available:`, this.threads.map(t => t.id));

    const thread = this.threads.find(t => t.id === threadId);
    console.log(`?? [renderThreadInfoContainer] Thread found:`, !!thread, thread ? `(title: "${thread.title}")` : '(not found)');

    if (!thread) {
        // For Prime, return welcome container with tool count
        if (location === 'prime') {
            console.log(`?? [renderThreadInfoContainer] Returning welcome container`);
            return ThreadCardTemplates.welcomeContainer(594);
        }

        // For agents/synergy, determine agent name and icon
        let agentName = 'Agent';
        let agentIcon = 'fa-robot';

        if (location === 'synergy') {
            agentName = 'Synergy';
            agentIcon = 'fa-users';
        } else {
            const match = location.match(/agent-(\d+)/);
            if (match && typeof MultiAgent !== 'undefined') {
                const agentId = parseInt(match[1]);
                agentName = MultiAgent.getAgentName(agentId);
                agentIcon = MultiAgent.getAgentIcon(agentId);
            }
        }

        console.log(`?? [renderThreadInfoContainer] Returning no thread message for ${agentName}`);
        return ThreadCardTemplates.noThreadMessage(agentName, agentIcon);
    }

    // Prepare agent metadata
    const agent = {
        name: 'Prime',
        icon: 'fa-star',
        class: 'main'
    };

    // Determine agent from location or thread.agent property
    if (location === 'synergy' && thread.agent) {
        const match = thread.agent.toString().match(/agent-(\d+)/);
        if (match) {
            const agentId = parseInt(match[1]);
            agent.name = MultiAgent ? MultiAgent.getAgentName(agentId) : `Agent-${agentId}`;
            agent.icon = MultiAgent ? MultiAgent.getAgentIcon(agentId) : 'fa-atom';
            agent.class = 'agent';
        }
    } else if (location !== 'prime' && location !== 'synergy') {
        const match = location.match(/agent-(\d+)/);
        if (match && typeof MultiAgent !== 'undefined') {
            const agentId = parseInt(match[1]);
            agent.name = MultiAgent.getAgentName(agentId);
            agent.icon = MultiAgent.getAgentIcon(agentId);
            agent.class = 'agent';
        }
    }

    // Prepare display metadata
    const updatedDate = new Date(thread.updated || thread.created);
    const meta = {
        msgCount: thread.message_count || (thread.messages && thread.messages.length) || 0,
        dateStr: updatedDate.toLocaleDateString('en-US', {
            month: 'short', day: 'numeric', year: 'numeric'
        }),
        timeStr: updatedDate.toLocaleTimeString('en-US', {
            hour: 'numeric', minute: '2-digit'
        })
    };

    // Shortened thread slug for display
    const slug = thread.id;

    // Fetch Synergy metadata from global cache
    let synergyMeta = null;
    if (thread.synergy_card_id) {
        if (!window._synergySessionCache) window._synergySessionCache = {};
        synergyMeta = window._synergySessionCache[thread.synergy_card_id];

        // REALTIME: Don't fetch synergy data here - causes infinite loop!
        // Synergy Board already has realtime subscription (line 40410)
        // If synergy metadata needed, it should be populated when linking
        // DO NOT FETCH HERE - causes repeated API calls
        if (!synergyMeta) {
            // Use placeholder data - synergy board will update via realtime
            synergyMeta = {
                title: thread.synergy_card_id || 'Synergy Session',
                description: 'Loading...',
                priority: 'medium'
            };
        }
    }

    // Use compact template for ALL locations (Prime, Agents, History)
    // Prime will use compactCard with headerRowClean (no unload button)
    // Agents will use compactCard with headerRowWithUnload ([X] button)
    console.log(`?? [renderThreadInfoContainer] Rendering compact card:`, { location, threadId: thread.id });

    let html = ThreadCardTemplates.compactCard(thread, location, agent, meta, slug, synergyMeta);

    console.log(`?? [renderThreadInfoContainer] Generated HTML length:`, html ? html.length : 0);
    return html;
},



/**
 * Update AppState synchronization
 * Keeps global AppState in sync with current thread
 */
syncAppState(threadId) {
    const thread = this.threads.find(t => t.id === threadId);

    if (!thread) {
        // Clear state
        if (typeof AppState !== 'undefined') {
            AppState.sessionId = null;
            AppState.chatMessages = [];
            AppState.threadTitle = null;
            AppState.threadTags = [];
            AppState.synergyCardId = null;
        }
        return;
    }

    // Update state
    if (typeof AppState !== 'undefined') {
        AppState.sessionId = thread.id;
        AppState.chatMessages = [...(thread.messages || [])]; // Clone array
        AppState.threadTitle = thread.title;
        AppState.threadTags = thread.tags || [];
        AppState.synergyCardId = thread.synergy_card_id;
        AppState.currentLocation = thread.agent || 'main';

        console.log('[AppState] Synced with thread:', AppState.sessionId);
    }
},

/**
 * Update message count across all UI locations
 * Updates Prime header, agent headers, and sidebar card
 * Counts only actual user/assistant exchanges (excludes thinking bubbles)
 */
updateMessageCount(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;

    // Count only actual user messages and assistant RESPONSE groups
    // Exclude thinking blocks and intermediate streaming chunks
    // Treat contiguous assistant messages as one response (counts once)
    let count = 0;
    if (thread.messages && Array.isArray(thread.messages)) {
        const msgs = thread.messages;
        let i = 0;
        while (i < msgs.length) {
            const msg = msgs[i];

            // Count user messages individually
            if (msg.role === 'user') {
                count += 1;
                i += 1;
                continue;
            }

            // Group contiguous assistant messages and count them as one response
            if (msg.role === 'assistant') {
                // Walk forward through contiguous assistant messages
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
                    } else if (typeof m.content === 'string') {
                        if (m.content.trim().length > 0) hasRealContent = true;
                    }
                    j += 1;
                }

                if (hasRealContent) count += 1; // count the whole assistant cluster once

                // Move index to first non-assistant message after the cluster
                i = j;
                continue;
            }

            // Other roles (tool/system/etc) - skip
            i += 1;
        }
    } else if (thread.message_count) {
        count = thread.message_count;
    } else {
        count = 0;
    }

    // Update all thread-meta-item elements with message count
    const allMetaItems = document.querySelectorAll(`[data-thread-id="${threadId}"] .thread-meta-item[title="Message count"]`);
    console.log(`[MESSAGE COUNT UPDATE] Thread ${threadId}: Found ${allMetaItems.length} elements to update with count ${count}`);
    allMetaItems.forEach(item => {
        item.innerHTML = `<i class="fas fa-comments"></i> ${count} msgs`;
        console.log(`[MESSAGE COUNT UPDATE] Updated element:`, item);
    });

    // Update Prime header if this is the current thread
    if (this.currentThreadId === threadId) {
        const msgCountEl = document.getElementById('prime-msg-count');
        if (msgCountEl) msgCountEl.textContent = count.toString();
    }

    // Update agent header if thread is in an agent
    if (thread.agent && thread.agent.startsWith('agent-')) {
        const agentId = thread.agent.replace('agent-', '');
        const msgCountEl = document.getElementById(`msg-count-${agentId}`);
        if (msgCountEl) msgCountEl.textContent = count.toString();
    }

    // Update sidebar card
    const cardEl = document.querySelector(`[data-thread-id="${threadId}"]`);
    if (cardEl) {
        const statsEl = cardEl.querySelector('.thread-item-stats span:first-child');
        if (statsEl) {
            statsEl.innerHTML = `<i class="fas fa-comments"></i> ${count}`;
        }
    }

    console.log('[UI UPDATE] Message count updated:', count);
},

updateTokenCount(threadId, tokenCount) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;

    if (typeof tokenCount !== 'undefined') {
        thread.token_count = tokenCount;
    }

    const el = document.getElementById(`token-count-${thread.id}`);
    if (!el) return;

    el.style.display = 'inline-flex';
    const value = (thread.token_count || 0);
    try {
        el.innerHTML = `Tokens: <strong>${value.toLocaleString()}</strong>`;
    } catch (e) {
        el.innerHTML = 'Tokens: <strong>' + (value) + '</strong>';
    }

    // Apply threshold classes
    const limit = window.SESSION_TOKEN_LIMIT || 200000;
    const pct = limit > 0 ? (value / limit) : 0;
    el.classList.remove('token-normal', 'token-caution', 'token-critical', 'token-emergency');
    if (pct >= 0.95) el.classList.add('token-emergency');
    else if (pct >= 0.8) el.classList.add('token-critical');
    else if (pct >= 0.5) el.classList.add('token-caution');
    else el.classList.add('token-normal');

    console.log('[UI UPDATE] Token count updated for', threadId, value);
},

updateDateTime(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;

    try {
        const createdDate = new Date(thread.created);
        const updatedDate = new Date(thread.updated || thread.created);

        const dateStr = createdDate.toLocaleDateString('en-US', {
            month: 'short', day: 'numeric', year: 'numeric'
        });

        const timeStr = updatedDate.toLocaleTimeString('en-US', {
            hour: 'numeric', minute: '2-digit'
        });

        // Update Prime header if current thread
        if (this.currentThreadId === threadId) {
            const dateEl = document.getElementById('prime-date');
            const timeEl = document.getElementById('prime-time');
            if (dateEl) dateEl.textContent = dateStr;
            if (timeEl) timeEl.textContent = timeStr;
        }

        // Update agent header if in agent
        if (thread.agent && thread.agent.startsWith('agent-')) {
            const agentId = thread.agent.replace('agent-', '');
            const dateEl = document.getElementById(`thread-date-${agentId}`);
            const timeEl = document.getElementById(`thread-time-${agentId}`);
            if (dateEl) dateEl.textContent = dateStr;
            if (timeEl) timeEl.textContent = timeStr;
        }
    } catch (error) {
        console.error('[UI UPDATE] Error updating date/time:', error);
    }
},

            /**
             * Tag management functions
             */
            async addTag(threadId, tag) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;

    if (!thread.tags) thread.tags = [];
    if (!thread.tags.includes(tag)) {
        thread.tags.push(tag);
        thread.updated = new Date().toISOString();

        // Save to backend
        await this.saveThreadToBackend(thread);

        // Update UI
        this.updatePrimeHeader(threadId);
        this.renderThreadList();
    }
},

            async removeTag(threadId, tag) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;

    thread.tags = (thread.tags || []).filter(t => t !== tag);
    thread.updated = new Date().toISOString();

    // Save to backend
    await this.saveThreadToBackend(thread);

    // Update UI
    this.updatePrimeHeader(threadId);
    this.renderThreadList();
},

showAddTagModal(locationOrThreadId, threadId) {
    // Support both old signature (single param) and new signature (location, threadId)
    const actualThreadId = threadId || locationOrThreadId;
    const tag = prompt('Enter tag name:');
    if (tag && tag.trim()) {
        this.addTag(actualThreadId, tag.trim());
    }
},

            /**
             * Synergy integration functions
             */
            async linkToSynergy(threadId, synergyCardId, synergyCardName) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) {
        console.error('Thread not found:', threadId);
        return;
    }

    // Update thread with synergy info
    thread.synergy_card_id = synergyCardId;
    thread.synergy_card_name = synergyCardName;
    thread.updated = new Date().toISOString();

    // Save to backend
    try {
        await this.saveThreadToBackend(thread);
        console.log(`Thread ${threadId} linked to Synergy card:`, synergyCardId);

        // Update UI
        this.updatePrimeHeader(threadId);
        this.renderThreadList();
    } catch (error) {
        console.error('Failed to link to Synergy:', error);
    }
},

            /**
             * Synergy unlink function
             */
            async unlinkFromSynergy(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;

    const synergyCardId = thread.synergy_card_id;

    thread.synergy_card_id = null;
    thread.synergy_card_name = null;
    thread.updated = new Date().toISOString();

    // Save to backend (updates threads table)
    await this.saveThreadToBackend(thread);

    // BIDIRECTIONAL SYNC: Remove from synergy_sessions.thread_ids array
    if (synergyCardId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/${synergyCardId}/unlink-thread`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ thread_id: threadId })
            });

            if (!response.ok) {
                console.warn('[SYNERGY] Failed to update Synergy session thread_ids:', response.status);
            } else {
                console.log('[SYNERGY] Successfully removed thread from Synergy session');
            }
        } catch (error) {
            console.error('[SYNERGY] Error updating Synergy session:', error);
        }
    }

    // Update UI
    this.updatePrimeHeader(threadId);
    this.renderThreadList();

    console.log('[SYNERGY] Unlinked thread from Synergy session');
},

copySynergyInfo(synergyCardId, synergyCardName) {
    const info = `Synergy Session: ${synergyCardName}\nID: ${synergyCardId}`;
    navigator.clipboard.writeText(info).then(() => {
        console.log('[SYNERGY] Copied to clipboard:', info);
        alert('Synergy info copied to clipboard!');
    }).catch(err => {
        console.error('[SYNERGY] Failed to copy:', err);
    });
},

openSynergySession(synergyCardId) {
    // TODO: Implement Synergy session opening
    console.log('[SYNERGY] Opening session:', synergyCardId);
    alert(`Opening Synergy session: ${synergyCardId}\n(Integration pending)`);
},

            /**
             * Workflow slug integration functions
             */
            async linkWorkflowSlug(threadId, workflowSlug) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;

    thread.workflow_slug = workflowSlug;
    thread.updated = new Date().toISOString();

    // Save to backend
    await this.saveThreadToBackend(thread);

    // Update UI - show the workflow slug pill
    const slugElement = document.getElementById(`workflow-slug-${threadId}`);
    const slugTextElement = document.getElementById(`workflow-slug-text-${threadId}`);
    if (slugElement && slugTextElement) {
        slugTextElement.textContent = workflowSlug;
        slugElement.style.display = 'inline-flex';

        // Show the remove button
        const removeBtn = slugElement.querySelector('button');
        if (removeBtn) {
            removeBtn.style.display = 'inline-block';
        }
    }

    console.log('[WORKFLOW] Linked workflow slug to thread:', workflowSlug);
},

            async unlinkWorkflowSlug(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;

    thread.workflow_slug = null;
    thread.updated = new Date().toISOString();

    // Save to backend
    await this.saveThreadToBackend(thread);

    // Update UI - hide the workflow slug pill
    const slugElement = document.getElementById(`workflow-slug-${threadId}`);
    if (slugElement) {
        slugElement.style.display = 'none';
    }

    console.log('[WORKFLOW] Unlinked workflow slug from thread');
},

loadWorkflowFromSlug(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread || !thread.workflow_slug) return;

    // Open Automation Canvas and load the workflow
    console.log('[WORKFLOW] Loading workflow:', thread.workflow_slug);

    // Check if automationCanvas instance exists
    if (window.automationCanvas && typeof window.automationCanvas.loadWorkflowBySlug === 'function') {
        window.automationCanvas.loadWorkflowBySlug(thread.workflow_slug);
    } else {
        alert(`Workflow slug: ${thread.workflow_slug}\n(Automation Canvas not loaded yet)`);
    }
},

/**
 * Drag and drop handlers
 */
handleDragStart(event) {
    const threadId = event.currentTarget.dataset.threadId;
    event.dataTransfer.setData('text/plain', threadId);
    event.dataTransfer.effectAllowed = 'move';

    // Add dragging class
    event.currentTarget.classList.add('dragging');

    console.log('[DRAG] Started dragging thread:', threadId);
},

handleDragEnd(event) {
    event.currentTarget.classList.remove('dragging');
},

handleDragOver(event) {
    // Prevent default to allow drop
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';

    // Add visual feedback to drop zone
    const dropZone = event.currentTarget;
    if (!dropZone.classList.contains('drag-over')) {
        dropZone.classList.add('drag-over');
    }
},

handleDragLeave(event) {
    // Remove visual feedback when leaving drop zone
    const dropZone = event.currentTarget;
    dropZone.classList.remove('drag-over');
},

            async handleDrop(event, targetLocation) {
    event.preventDefault();
    event.stopPropagation();

    // Remove visual feedback
    const dropZone = event.currentTarget;
    dropZone.classList.remove('drag-over');

    // Get dropped thread ID
    const threadId = event.dataTransfer.getData('text/plain');
    if (!threadId) {
        console.warn('[DROP] No thread ID in drop event');
        return;
    }

    console.log(`[DROP] Thread ${threadId} dropped on ${targetLocation}`);

    // Handle drop based on target
    if (targetLocation === 'prime') {
        // Move thread to Prime (unload from agent)
        await this.assignThread(threadId, 'prime');
        this.switchThread(threadId, true);
        showNotification('Thread moved to Prime AI', 'success');
    } else if (targetLocation.startsWith('agent-')) {
        // Assign thread to specific agent
        const agentId = targetLocation.replace('agent-', '');

        // Check if MultiAgent exists
        if (typeof MultiAgent !== 'undefined') {
            await this.assignThread(threadId, targetLocation);
            await MultiAgent.loadThread(parseInt(agentId), threadId);
            showNotification(`Thread assigned to ${MultiAgent.getAgentName(agentId)}`, 'success');
        }
    }

    // Refresh UI
    this.renderThreadList();
},

            // ========================================
            // END UI UPDATE FUNCTIONS
            // ========================================

            async renderThreadList() {
    const listContainer = document.getElementById('thread-list');
    if (!listContainer) return;

    if (this.threads.length === 0) {
        listContainer.innerHTML = '<div style="padding: var(--space-4); text-align: center; color: var(--text-secondary);">No threads yet</div>';
        return;
    }

    // REALTIME: No need to fetch assignments - realtime subscription keeps them updated
    // Thread locations are maintained in thread.location by realtime events
    let backendAssignments = {};

    // Build assignments from thread objects (already synced via realtime)
    console.log('[DEBUG] Building assignments from threads. Thread count:', this.threads.length);
    console.log('[DEBUG] Sample thread.location values:', this.threads.slice(0, 5).map(t => ({ id: t.id, location: t.location })));

    this.threads.forEach(thread => {
        if (thread.location && thread.location !== 'prime') {
            backendAssignments[thread.location] = thread.id;
        }
    });

    console.log('[renderThreadList] Current assignments (from realtime):', backendAssignments);

    // Create REVERSE mapping: threadId -> location
    const threadToLocation = {};
    Object.entries(backendAssignments).forEach(([location, threadId]) => {
        threadToLocation[threadId] = location;
    });

    // Filter threads based on current filter
    const filteredThreads = this.threads.filter(thread => {
        const isArchived = thread.archived || false;

        // 1. Active/Archived filter
        if (this.currentFilter === 'archived' ? !isArchived : isArchived) {
            return false;
        }

        // 2. Search query (date, title, or ID)
        if (this.searchQuery) {
            const query = this.searchQuery.toLowerCase();
            const titleMatch = thread.title.toLowerCase().includes(query);
            const idMatch = thread.id.includes(query);

            // Try parsing as date (various formats)
            let dateMatch = false;
            if (thread.updated) {
                const threadDate = new Date(thread.updated);
                const dateStr = threadDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).toLowerCase();
                const dateStr2 = threadDate.toISOString().split('T')[0]; // YYYY-MM-DD
                dateMatch = dateStr.includes(query) || dateStr2.includes(query);
            }

            if (!titleMatch && !idMatch && !dateMatch) {
                return false;
            }
        }

        // 3. Location filter (all/prime/all-agents/agent-1/agent-2/agent-3)
        if (this.locationFilter && this.locationFilter !== 'all') {
            const threadLocation = thread.location || 'prime';

            if (this.locationFilter === 'prime' && threadLocation !== 'prime') {
                return false;
            } else if (this.locationFilter === 'all-agents' && threadLocation === 'prime') {
                return false;
            } else if (this.locationFilter.startsWith('agent-') && threadLocation !== this.locationFilter) {
                return false;
            }
        }

        // 4. Tag filter (synergy/automation)
        if (this.activeTagFilter) {
            if (this.activeTagFilter === 'synergy' && !thread.synergy_card_id) {
                return false;
            }
            if (this.activeTagFilter === 'automation' && !thread.automation_workflow_id) {
                return false;
            }
        }

        // 5. Date range filter
        if (this.dateRangeFilter && this.dateRangeFilter.startDate && thread.updated) {
            const threadDate = new Date(thread.updated);
            if (threadDate < this.dateRangeFilter.startDate) {
                return false;
            }
        }

        return true;
    });

    if (filteredThreads.length === 0) {
        listContainer.innerHTML = `<div style="padding: var(--space-4); text-align: center; color: var(--text-secondary);">
                        ${this.currentFilter === 'archived' ? 'No archived threads' : 'No active threads'}
                    </div>`;
        return;
    }

    // Preload synergy session metadata for visible threads (client-side cache)
    const synergyIdsToLoad = Array.from(new Set(filteredThreads
        .map(t => t.synergy_card_id)
        .filter(Boolean)));

    // Simple in-memory cache on ThreadManager to avoid duplicate fetches
    if (!window._synergySessionCache) window._synergySessionCache = {};
    const cache = window._synergySessionCache;

    if (synergyIdsToLoad.length > 0) {
        try {
            const missing = synergyIdsToLoad.filter(id => !cache[id]);
            if (missing.length > 0) {
                // Bulk fetch missing sessions to reduce round-trips
                const idsParam = missing.join(',');
                try {
                    const resp = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/synergy?ids=${encodeURIComponent(idsParam)}`);
                    if (resp.ok) {
                        const data = await resp.json();
                        if (data && data.success && data.sessions) {
                            Object.entries(data.sessions).forEach(([sid, session]) => {
                                cache[sid] = session;
                            });
                        }
                    }
                } catch (err) {
                    // Fallback to per-id fetch if bulk fails
                    console.warn('[renderThreadList] Bulk fetch failed, falling back to individual requests', err);
                    for (const id of missing) {
                        try {
                            const r = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/synergy/${id}`);
                            if (r.ok) {
                                const d = await r.json();
                                if (d && d.success && d.session) cache[id] = d.session;
                            }
                        } catch (err2) {
                            console.warn('[renderThreadList] Failed to fetch synergy session', id, err2);
                        }
                    }
                }
            }
        } catch (err) {
            console.warn('[renderThreadList] Failed to preload synergy sessions:', err);
        }
    }

    // Sort threads by date (newest first)
    filteredThreads.sort((a, b) => new Date(b.updated) - new Date(a.updated));

    // Group threads by date
    const groupedThreads = [];
    let currentDateGroup = null;

    filteredThreads.forEach(thread => {
        const threadDate = new Date(thread.updated);
        const dateLabel = this.getDateLabel(threadDate);

        if (currentDateGroup !== dateLabel) {
            groupedThreads.push({ type: 'separator', label: dateLabel });
            currentDateGroup = dateLabel;
        }
        groupedThreads.push({ type: 'thread', data: thread });
    });

    // Render grouped threads with separators
    listContainer.innerHTML = groupedThreads.map(item => {
        if (item.type === 'separator') {
            return `<div class="thread-date-separator">
                            <span>${item.label}</span>
                        </div>`;
        }

        const thread = item.data;

        // Use ThreadCardTemplates.compactCard for consistent rendering with agent columns
        if (typeof ThreadCardTemplates !== 'undefined') {
            // Get current location
            const currentLocation = threadToLocation[thread.id] || 'prime';

            // Prepare agent metadata
            let agentName = 'Prime';
            let agentIcon = 'fa-star';
            let agentClass = 'main';

            if (currentLocation && currentLocation !== 'prime') {
                const match = currentLocation.match(/agent-(\d+)/);
                if (match && typeof MultiAgent !== 'undefined') {
                    const agentId = parseInt(match[1]);
                    agentName = MultiAgent.getAgentName(agentId);
                    agentIcon = MultiAgent.getAgentIcon(agentId);
                    agentClass = 'agent';
                }
            }

            const agent = { name: agentName, icon: agentIcon, class: agentClass };

            // Prepare meta info
            const date = new Date(thread.updated || thread.created);
            const meta = {
                msgCount: thread.message_count || (thread.messages && thread.messages.length) || 0,
                dateStr: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
                timeStr: date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
            };

            const slug = thread.id;

            // Get synergy metadata from cache
            const synergyMeta = thread.synergy_card_id ? cache[thread.synergy_card_id] : null;

            // Generate card HTML using template (if available)
            if (typeof ThreadCardTemplates !== 'undefined' && ThreadCardTemplates.compactCard) {
                const cardHtml = ThreadCardTemplates.compactCard(thread, 'thread-history', agent, meta, slug, synergyMeta, currentLocation);

                // Wrap in thread-item container with drag-and-drop and click handlers
                return `<div class="thread-item ${thread.id === this.currentThreadId ? 'active' : ''}"
                                        draggable="true"
                                        data-thread-id="${thread.id}"
                                        data-synergy-id="${thread.synergy_card_id || ''}"
                                        data-current-location="${currentLocation}"
                                        ondragstart="ThreadManager.handleDragStart(event)"
                                        ondragend="ThreadManager.handleDragEnd(event)"
                                        ondblclick="ThreadManager.handleThreadDoubleClick('${thread.id}', '${currentLocation}')">
                                        ${cardHtml}
                                    </div>`;
            }
        }

        // FALLBACK: Legacy inline HTML (if ThreadCardTemplates not loaded)
        const date = new Date(thread.updated);
        const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        const timeStr = date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });

        // Get REAL location from backend (not stale thread.agent from localStorage)
        const currentLocation = threadToLocation[thread.id] || null;

        // Determine display label
        let agentLabel = 'Prime';
        let agentIcon = 'fa-star';
        let agentClass = 'main';

        if (currentLocation && currentLocation !== 'prime') {
            // Parse agent location (e.g., "agent-2" -> "Bravo-2")
            const match = currentLocation.match(/agent-(\d+)/);
            if (match) {
                const agentId = parseInt(match[1]);
                agentLabel = MultiAgent ? MultiAgent.getAgentName(agentId) : `Agent-${agentId}`;
                agentIcon = MultiAgent ? MultiAgent.getAgentIcon(agentId) : 'fa-atom';
                agentClass = 'agent';
            }
        }

        // Get title from MultiAgent.loadedThreads (source of truth) or fallback to thread object
        let threadTitle = thread.title || 'Untitled';

        // Check if this thread is loaded in any agent - use that title (always correct)
        if (typeof MultiAgent !== 'undefined' && MultiAgent.loadedThreads) {
            for (const agentId in MultiAgent.loadedThreads) {
                const loadedThread = MultiAgent.loadedThreads[agentId];
                if (loadedThread && loadedThread.threadId === thread.id && loadedThread.threadTitle) {
                    threadTitle = loadedThread.threadTitle;
                    break;
                }
            }
        }

        const truncatedTitle = threadTitle.length > 35 ? threadTitle.substring(0, 32) + '...' : threadTitle;
        const truncatedThreadId = thread.id.length > 20 ? thread.id.substring(0, 17) + '...' : thread.id;
        const truncatedSynergyId = thread.synergy_card_id ?
            (thread.synergy_card_id.length > 30 ? thread.synergy_card_id.substring(0, 27) + '...' : thread.synergy_card_id)
            : '';

        // Try to get richer session metadata from client cache
        const synergyMeta = thread.synergy_card_id ? cache[thread.synergy_card_id] : null;
        const synergyDisplay = synergyMeta ? (synergyMeta.title || thread.synergy_card_id) : (thread.synergy_card_name || truncatedSynergyId || 'Linked Synergy');
        const synergyPriority = synergyMeta ? (synergyMeta.priority || '') : (thread.synergy_priority || '');

        return `
                                                <div class="thread-item ${thread.id === this.currentThreadId ? 'active' : ''}"
                                                    draggable="true"
                                                    data-thread-id="${thread.id}"
                                                    data-synergy-id="${thread.synergy_card_id || ''}"
                                                    data-current-location="${currentLocation || 'prime'}"
                                                    ondragstart="ThreadManager.handleDragStart(event)"
                                                    ondragend="ThreadManager.handleDragEnd(event)"
                                                    ondblclick="ThreadManager.handleThreadDoubleClick('${thread.id}', '${currentLocation || 'prime'}')">
                                                    
                                                    <!-- ROW 1: Agent Badge (LHS) + Action Buttons (RHS) -->
                                                    <div class="thread-item-header">
                                                        <div class="thread-item-agent-badge ${agentClass}">
                                                            <i class="fas ${agentIcon}"></i> ${agentLabel}
                                                        </div>
                                                        <div class="thread-item-actions">
                                                            ${currentLocation && currentLocation.startsWith('agent-') ? `
                                                            <button class="thread-action-btn unload"
                                                                onclick="event.stopPropagation(); ThreadManager.unloadThread('${thread.id}')"
                                                                title="Unload thread from agent (move to Prime)">
                                                                <i class="fas fa-sign-out-alt"></i>
                                                            </button>
                                                            ` : ''}
                                                            <button class="thread-action-btn rename"
                                                                onclick="event.stopPropagation(); ThreadManager.startRename('${thread.id}')"
                                                                title="Rename thread">
                                                                <i class="fas fa-pen"></i>
                                                            </button>
                                                            <button class="thread-action-btn edit"
                                                                onclick="event.stopPropagation(); ThreadManager.editThread('${thread.id}')"
                                                                title="Edit thread">
                                                                <i class="fas fa-edit"></i>
                                                            </button>
                                                            <button class="thread-action-btn fork"
                                                                onclick="event.stopPropagation(); ThreadManager.forkThread('${thread.id}')"
                                                                title="Fork thread (branch from current point)">
                                                                <i class="fas fa-code-branch"></i>
                                                            </button>
                                                            <button class="thread-action-btn clone"
                                                                onclick="event.stopPropagation(); ThreadManager.cloneThread('${thread.id}')"
                                                                title="Clone thread (duplicate all messages)">
                                                                <i class="fas fa-clone"></i>
                                                            </button>
                                                            <button class="thread-action-btn archive"
                                                                onclick="event.stopPropagation(); ThreadManager.archiveThread('${thread.id}')"
                                                                title="Archive thread">
                                                                <i class="fas fa-archive"></i>
                                                            </button>
                                                            <button class="thread-action-btn delete"
                                                                onclick="event.stopPropagation(); ThreadManager.deleteThread('${thread.id}')"
                                                                title="Delete thread">
                                                                <i class="fas fa-trash"></i>
                                                            </button>
                                                        </div>
                                                    </div>
                                                    
                                                    <!-- ROW 2: Title (Full Width) -->
                                                    <div class="thread-item-title-row">
                                                        <span class="thread-item-title" id="thread-title-${thread.id}" title="${threadTitle}">${truncatedTitle}</span>
                                                    </div>
                                                    
                                                    <!-- ROW 3: Meta Info + Thread Slug -->
                                                    <div class="thread-item-meta" style="display: flex; align-items: center; justify-content: space-between; gap: 12px;">
                                                        <div style="display: flex; align-items: center; gap: 12px; flex: 1;">
                                                            <span class="thread-meta-item" title="Message count">
                                                                <i class="fas fa-comments"></i> ${thread.message_count || thread.messages?.length || 0} msgs
                                                            </span>
                                                            <span class="thread-meta-item" title="Last updated">
                                                                <i class="fas fa-calendar"></i> ${dateStr}
                                                            </span>
                                                            <span class="thread-meta-item" title="Time">
                                                                <i class="fas fa-clock"></i> ${timeStr}
                                                            </span>
                                                        </div>
                                                        <button class="thread-id-badge"
                                                            onclick="event.stopPropagation(); ThreadManager.copyThreadId('${thread.id}')"
                                                            title="Copy thread slug: ${thread.id}">
                                                            <i class="fas fa-hashtag"></i> ${thread.id}
                                                        </button>
                                                    </div>
                                                    
                                                    <!-- ROW 4: Synergy Session (if present) -->
                                                    ${thread.synergy_card_id ? `
                                                        <div class="thread-item-synergy" data-synergy-id="${thread.synergy_card_id}">
                                                            <button class="synergy-badge"
                                                                onclick="event.stopPropagation(); ThreadManager.copySynergyInfo('${thread.synergy_card_id}', '${(synergyDisplay || '').replace(/'/g, "\\'")}')"
                                                                data-tooltip-title="${(synergyMeta && synergyMeta.title) ? (synergyMeta.title.replace(/\"/g, '&quot;')) : ''}"
                                                                data-tooltip-desc="${(synergyMeta && synergyMeta.description) ? (synergyMeta.description.replace(/\"/g, '&quot;')) : ''}"
                                                                data-tooltip-users="${(synergyMeta && Array.isArray(synergyMeta.assignees)) ? (synergyMeta.assignees.join(', ').replace(/\"/g, '&quot;')) : ''}"
                                                                data-tooltip-updated="${(synergyMeta && synergyMeta.last_active) ? (new Date(synergyMeta.last_active).toLocaleString()) : ''}">
                                                                <i class="fas fa-link"></i>
                                                                <span class="synergy-badge-title">${synergyDisplay}</span>
                                                                ${synergyPriority ? `<span class="synergy-badge-priority">${synergyPriority}</span>` : ''}
                                                            </button>
                                                            <button class="thread-synergy-unlink" title="Unlink Synergy session" onclick="event.stopPropagation(); ThreadManager.unlinkSynergy('${thread.id}', '${thread.synergy_card_id}')">
                                                                <i class="fas fa-unlink"></i>
                                                            </button>
                                                        </div>
                                                    ` : `
                                                        <div class="thread-item-synergy thread-item-synergy-unlinked">
                                                            <button class="synergy-create-link" onclick="event.stopPropagation(); ThreadManager.openSynergySyncModal('${thread.id}')" title="Link thread to Synergy session">
                                                                <i class="fas fa-link"></i> Synergy Sync
                                                            </button>
                                                        </div>
                                                    `}
                                                    
                                                    <!-- ROW 5: Tags + Add Tag Button -->
                                                    <div class="thread-tags-row" style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
                                                        ${thread.tags ? thread.tags.map(tag => `
                                                            <span class="thread-tag-pill">
                                                                <i class="fas fa-tag"></i> ${tag}
                                                                <button onclick="event.stopPropagation(); ThreadManager.removeTag('${thread.id}', '${tag}')" 
                                                                        class="tag-remove-btn" 
                                                                        title="Remove tag">&times;</button>
                                                            </span>
                                                        `).join('') : ''}
                                                        <button class="add-tag-btn" 
                                                                onclick="event.stopPropagation(); ThreadManager.showAddTagModal('thread-history', '${thread.id}')" 
                                                                title="Add tags to this thread">
                                                            <i class="fas fa-plus"></i> Tag
                                                        </button>
                                                    </div>

                                                    <!-- ROW 6: Assignment Warning & Options (Expandable - only for agent-assigned threads) -->
                                                    ${currentLocation && currentLocation.startsWith('agent-') ? `
                                                    <div class="thread-item-assignment-warning">
                                                        <div class="thread-assignment-notice">
                                                            <i class="fas fa-info-circle"></i>
                                                            <span>This thread is assigned to <strong>${agentLabel}</strong>. Choose an action:</span>
                                                        </div>
                                                        <div class="thread-assignment-options">
                                                            <button class="thread-assignment-option-btn prime"
                                                                    onclick="event.stopPropagation(); ThreadManager.handleThreadAssignmentOption('${thread.id}', 'move-to-prime')">
                                                                <i class="fa-solid fa-atom"></i>
                                                                <div class="option-details">
                                                                    <div class="option-title">Move to Prime & View</div>
                                                                    <div class="option-subtitle">Unload from agent and open in main chat</div>
                                                                </div>
                                                            </button>
                                                            <button class="thread-assignment-option-btn agent"
                                                                    onclick="event.stopPropagation(); ThreadManager.handleThreadAssignmentOption('${thread.id}', 'view-in-agent')">
                                                                <i class="fas fa-columns"></i>
                                                                <div class="option-details">
                                                                    <div class="option-title">View in Agent Dashboard</div>
                                                                    <div class="option-subtitle">Open Multi-Agent NATO Columns</div>
                                                                </div>
                                                            </button>
                                                            <button class="thread-assignment-option-btn unload"
                                                                    onclick="event.stopPropagation(); ThreadManager.handleThreadAssignmentOption('${thread.id}', 'unload-only')">
                                                                <i class="fas fa-sign-out-alt"></i>
                                                                <div class="option-details">
                                                                    <div class="option-title">Unload from Agent Only</div>
                                                                    <div class="option-subtitle">Move to Prime without opening</div>
                                                                </div>
                                                            </button>
                                                        </div>
                                                    </div>
                                                    ` : ''}
                                                </div>
                `}).join('');
},

            async toggleThreadMenu() {
    console.log(`[SEARCH] [toggleThreadMenu] Called`);
    const menu = document.getElementById('thread-menu');
    if (menu) {
        const wasActive = menu.classList.contains('active');
        menu.classList.toggle('active');
        const isActive = menu.classList.contains('active');
        console.log(`[SEARCH] [toggleThreadMenu] Menu toggled: ${wasActive ? 'OPEN' : 'CLOSED'} → ${isActive ? 'OPEN' : 'CLOSED'}`);

        // Load thread history when opening the menu
        if (isActive) {
            console.log(`[SEARCH] [toggleThreadMenu] Loading thread history...`);
            await this.loadThreadsFromBackend();
            await this.renderThreadList();
            console.log(`[SEARCH] [toggleThreadMenu] Thread history loaded: ${this.threads.length} threads`);
        }
    } else {
        console.error(`[ERROR] [toggleThreadMenu] Thread menu element not found!`);
    }
},

closeThreadMenu() {
    const menu = document.getElementById('thread-menu');
    const threadsBtn = document.getElementById('threads-btn');

    menu.classList.remove('active');
    if (threadsBtn) {
        threadsBtn.classList.remove('active');
    }
},

showStartNewChatButton(containerId, location = 'prime') {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`[ERROR] Container not found: ${containerId}`);
        return;
    }

    // Create welcome container UI
    const emptyStateHtml = `
                    <div class="welcome-container" id="${location}-welcome-container" style="margin-top: 40px;">
                        <div class="welcome-content">
                            <div class="welcome-icon">
                                <i class="fas fa-moon" style="color: rgb(139, 92, 246);"></i>
                            </div>
                            <h3 class="welcome-title" id="${location}-welcome-title">Midnight Momentum!</h3>
                            <p class="welcome-subtitle" id="${location}-welcome-subtitle">The quiet hours are perfect for deep work. What's the mission?</p>

                            <div class="quick-tip-card" id="${location}-quick-tip">
                                <div class="quick-tip-icon">
                                    <i class="fas fa-lightbulb"></i>
                                </div>
                                <div class="quick-tip-content">
                                    <span class="quick-tip-label">Quick Tip</span>
                                    <p class="quick-tip-text">Right-click thread cards for quick actions: archive, delete, copy ID, or export conversation history.</p>
                                </div>
                            </div>

                            <div class="welcome-stats">
                                <div class="welcome-stat-card">
                                    <i class="fas fa-tools"></i>
                                    <div class="stat-content">
                                        <strong>594 tools</strong>
                                        <span>20+ platforms</span>
                                    </div>
                                </div>
                                <div class="welcome-stat-card">
                                    <i class="fas fa-project-diagram"></i>
                                    <div class="stat-content">
                                        <strong>Interactive</strong>
                                        <span>visualizations</span>
                                    </div>
                                </div>
                            </div>

                            <div class="welcome-actions">
                                <button class="welcome-btn welcome-btn-primary" onclick="ThreadManager.showNewChatModal('${location}')">
                                    <i class="fas fa-plus"></i> Start New Chat
                                </button>
                                <button class="welcome-btn welcome-btn-secondary" onclick="ThreadManager.toggleThreadMenu(); event.stopPropagation();">
                                    <i class="fas fa-history"></i> Thread History
                                </button>
                            </div>
                        </div>
                    </div>
                `;

    container.innerHTML = emptyStateHtml;

    // CRITICAL: Hide input wrapper to prevent typing without a thread
    if (location && location.startsWith('agent-')) {
        const agentId = location.replace('agent-', '');
        const agentInputArea = document.querySelector(`#agent-${agentId} .agent-input-area`);

        if (agentInputArea) {
            agentInputArea.style.display = 'none';
            console.log(`[EMPTY STATE] Input area hidden for agent-${agentId}`);
        }
    } else if (location === 'prime') {
        // Hide Prime input wrapper when showing empty state
        const primeInputWrapper = document.querySelector('.ai-chat-input-wrapper');

        if (primeInputWrapper) {
            primeInputWrapper.style.display = 'none';
            console.log(`[EMPTY STATE] Input wrapper hidden for Prime`);
        }
    }

    console.log(`[NEW] Showing "Start New Chat" button in ${location}`);
},

            //  EDIT THREAD MODAL - EDIT EXISTING THREAD METADATA
            async editThread(threadId) {
    console.log(`✏️ [editThread] Opening edit modal for thread: ${threadId}`);

    // Find the thread
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) {
        showNotification('Thread not found', 'error');
        return;
    }

    // Predefined tag categories
    const tagCategories = {
        'Priority': ['urgent', 'high', 'medium', 'low'],
        'Type': ['research', 'implementation', 'bug-fix', 'feature', 'documentation'],
        'Status': ['in-progress', 'blocked', 'review', 'complete']
    };

    // Fetch Synergy sessions for dropdown
    let synergySessions = [];
    try {
        const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/synergy/sessions`);
        if (response.ok) {
            synergySessions = await response.json();
        }
    } catch (error) {
        console.warn(`[WARN] [editThread] Could not load Synergy sessions:`, error);
    }

    // Group sessions by column for organized display
    const sessionsByColumn = synergySessions.reduce((acc, session) => {
        const column = session.column || 'other';
        if (!acc[column]) acc[column] = [];
        acc[column].push(session);
        return acc;
    }, {});

    // Column display names (clean text for optgroup labels)
    const columnNames = {
        'backlog': 'Backlog',
        'todo': 'To Do',
        'in-progress': 'In Progress',
        'in_progress': 'In Progress',
        'review': 'Review',
        'done': 'Done',
        'other': 'Other'
    };

    // Get current location
    const currentLocation = thread.location || 'prime';
    const locationName = currentLocation === 'prime' ? 'Prime Agent' :
        (currentLocation.startsWith('agent-') ? `Agent ${currentLocation.split('-')[1]}` : currentLocation);

    const modalHTML = `
                    <div class="modal-overlay" id="editThreadModalOverlay">
                        <div class="new-chat-modal">
                            <div class="modal-header">
                                <h3>✏️ Edit Thread</h3>
                                <button class="modal-close" onclick="document.getElementById('editThreadModalOverlay').remove()">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                            <div class="modal-body">
                                <form id="editThreadForm">
                                    <!-- Thread Title -->
                                    <div class="new-chat-form-group">
                                        <label for="editThreadTitle">
                                            Thread Title
                                            <span style="color: var(--accent-error, #f85149);">*</span>
                                        </label>
                                        <input
                                            type="text"
                                            id="editThreadTitle"
                                            value="${thread.title.replace(/"/g, '&quot;')}"
                                            placeholder="Enter thread title..."
                                            required
                                            autofocus
                                        >
                                    </div>

                                    <!-- Agent Assignment (Read-only) -->
                                    <div class="new-chat-form-group">
                                        <label>Assigned To</label>
                                        <input
                                            type="text"
                                            value="${locationName}"
                                            readonly
                                            style="background: var(--bg-tertiary, #1c2128); cursor: not-allowed;"
                                        >
                                    </div>

                                    <!-- Tags -->
                                    <div class="new-chat-form-group">
                                        <label>
                                            Tags
                                            <span class="optional">(optional)</span>
                                        </label>
                                        <div class="new-chat-tag-options">
                                            ${Object.entries(tagCategories).flatMap(([category, tags]) =>
        tags.map(tag => `
                                                    <button type="button" class="new-chat-tag-btn ${thread.tags && thread.tags.includes(tag) ? 'active' : ''}" data-tag="${tag}">
                                                        ${tag}
                                                    </button>
                                                `)
    ).join('')}
                                        </div>
                                    </div>

                                    <!-- Synergy Session Link -->
                                    <div class="new-chat-form-group">
                                        <label for="editThreadSynergySession">
                                            Link to Synergy Session
                                            <span class="optional">(optional)</span>
                                        </label>
                                        <select id="editThreadSynergySession" data-sessions='${JSON.stringify(synergySessions)}'>
                                            <option value="" ${!thread.synergy_card_id ? 'selected' : ''}>No Synergy Link</option>
                                            ${Object.keys(sessionsByColumn).sort().map(column => `
                                                <optgroup label="${columnNames[column] || column}">
                                                    ${sessionsByColumn[column].map(session => `
                                                        <option value="${session.session_id}" 
                                                                ${thread.synergy_card_id === session.session_id ? 'selected' : ''}
                                                                data-description="${(session.description || '').replace(/"/g, '&quot;')}"
                                                                data-priority="${session.priority || 'medium'}">
                                                            ${session.title} ${session.priority ? `[${session.priority.toUpperCase()}]` : ''}
                                                        </option>
                                                    `).join('')}
                                                </optgroup>
                                            `).join('')}
                                        </select>
                                        ${synergySessions.length > 0 ? `
                                            <div id="editThreadSynergyDescription" style="
                                                margin-top: 8px; 
                                                padding: 8px 12px; 
                                                background: var(--bg-secondary, #1f2937);
                                                border: 1px solid var(--border-color, #374151);
                                                border-radius: 6px;
                                                font-size: 12px;
                                                color: var(--text-secondary, #9ca3af);
                                                display: none;
                                                min-height: 40px;
                                                line-height: 1.5;
                                            ">
                                                <div style="display: flex; align-items: start; gap: 8px;">
                                                    <i class="fas fa-info-circle" style="color: var(--accent-info, #3b82f6); margin-top: 2px;"></i>
                                                    <span id="editThreadSynergyDescriptionText"></span>
                                                </div>
                                            </div>
                                        ` : ''}
                                    </div>
                                </form>
                            </div>
                            <div class="modal-footer">
                                <button class="btn-secondary" onclick="document.getElementById('editThreadModalOverlay').remove()">
                                    Cancel
                                </button>
                                <button class="btn-primary" id="saveThreadBtn">
                                    Save Changes
                                </button>
                            </div>
                        </div>
                    </div>
                `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Synergy session description display for edit modal
    const editSynergySelect = document.getElementById('editThreadSynergySession');
    const editDescriptionDiv = document.getElementById('editThreadSynergyDescription');
    const editDescriptionText = document.getElementById('editThreadSynergyDescriptionText');

    if (editSynergySelect && editDescriptionDiv && editDescriptionText) {
        // Show description if a session is already selected
        const initialOption = editSynergySelect.options[editSynergySelect.selectedIndex];
        const initialDescription = initialOption.getAttribute('data-description');
        const initialPriority = initialOption.getAttribute('data-priority');

        if (editSynergySelect.value && initialDescription) {
            const priorityColors = {
                'critical': '#ef4444',
                'high': '#f97316',
                'medium': '#3b82f6',
                'low': '#10b981'
            };
            const priorityColor = priorityColors[initialPriority] || '#6b7280';
            const priorityBadge = initialPriority ? `<span style="
                            display: inline-block;
                            padding: 2px 8px;
                            background: ${priorityColor}22;
                            color: ${priorityColor};
                            border: 1px solid ${priorityColor}44;
                            border-radius: 4px;
                            font-size: 10px;
                            font-weight: 600;
                            text-transform: uppercase;
                            margin-left: 8px;
                        ">${initialPriority}</span>` : '';

            editDescriptionText.innerHTML = `${initialDescription}${priorityBadge}`;
            editDescriptionDiv.style.display = 'block';
        }

        editSynergySelect.addEventListener('change', function () {
            const selectedOption = this.options[this.selectedIndex];
            const description = selectedOption.getAttribute('data-description');
            const priority = selectedOption.getAttribute('data-priority');

            if (this.value && description) {
                const priorityColors = {
                    'critical': '#ef4444',
                    'high': '#f97316',
                    'medium': '#3b82f6',
                    'low': '#10b981'
                };
                const priorityColor = priorityColors[priority] || '#6b7280';
                const priorityBadge = priority ? `<span style="
                                display: inline-block;
                                padding: 2px 8px;
                                background: ${priorityColor}22;
                                color: ${priorityColor};
                                border: 1px solid ${priorityColor}44;
                                border-radius: 4px;
                                font-size: 10px;
                                font-weight: 600;
                                text-transform: uppercase;
                                margin-left: 8px;
                            ">${priority}</span>` : '';

                editDescriptionText.innerHTML = `${description}${priorityBadge}`;
                editDescriptionDiv.style.display = 'block';
            } else {
                editDescriptionDiv.style.display = 'none';
            }
        });
    }

    // Tag toggle functionality
    const selectedTags = [...(thread.tags || [])];
    const tagButtons = document.querySelectorAll('.new-chat-tag-btn');
    tagButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            btn.classList.toggle('active');
            const tag = btn.dataset.tag;
            if (btn.classList.contains('active')) {
                if (!selectedTags.includes(tag)) {
                    selectedTags.push(tag);
                }
            } else {
                const index = selectedTags.indexOf(tag);
                if (index > -1) {
                    selectedTags.splice(index, 1);
                }
            }
        });
    });

    // Save button handler
    document.getElementById('saveThreadBtn').addEventListener('click', async () => {
        const newTitle = document.getElementById('editThreadTitle').value.trim();
        const newSynergySessionId = document.getElementById('editThreadSynergySession').value;

        if (!newTitle) {
            showNotification('Please enter a thread title', 'error');
            return;
        }

        if (newTitle.length < 3) {
            showNotification('Thread title must be at least 3 characters', 'error');
            return;
        }

        console.log(` [editThread] Saving changes:`, { threadId, newTitle, selectedTags, newSynergySessionId });

        try {
            // Update thread via API (use PATCH /update route)
            const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/${threadId}/update`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: newTitle,
                    tags: selectedTags,
                    synergy_card_id: newSynergySessionId || null
                })
            });

            if (response.ok) {
                showNotification('Thread updated successfully', 'success');
                document.getElementById('editThreadModalOverlay').remove();

                // Reload threads
                await this.loadThreads();
                await this.renderThreadsList();
            } else {
                const error = await response.json();
                showNotification(`Failed to update thread: ${error.error || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            console.error('[editThread] Error updating thread:', error);
            showNotification('Error updating thread', 'error');
        }
    });

    // Enter key to submit
    document.getElementById('editThreadTitle').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            document.getElementById('saveThreadBtn').click();
        }
    });
},

            //  FORK THREAD - BRANCH FROM CURRENT POINT
            async forkThread(threadId) {
    console.log(` [forkThread] Forking thread: ${threadId}`);

    // Find the thread
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) {
        showNotification('Thread not found', 'error');
        return;
    }

    // Get current message count
    const messageCount = thread.message_count || thread.messages?.length || 0;

    if (messageCount === 0) {
        showNotification('Cannot fork empty thread', 'warning');
        return;
    }

    // Prompt for branch name
    const branchName = prompt(`Fork thread "${thread.title}"\n\nEnter branch name:`, `${thread.title} (fork)`);
    if (!branchName) return;

    try {
        const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/messages/fork`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                thread_id: threadId,
                message_id: null,  // Fork from last message
                branch_name: branchName,
                user_id: (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 14
            })
        });

        if (response.ok) {
            const result = await response.json();
            showNotification(`Thread forked successfully! ${result.messages_copied} messages copied.`, 'success');

            // Reload threads
            await this.loadThreads();
            await this.renderThreadsList();

            // Switch to new thread
            if (result.new_thread_id) {
                await this.switchThread(result.new_thread_id);
            }
        } else {
            const error = await response.json();
            showNotification(`Failed to fork thread: ${error.error || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        console.error('[forkThread] Error:', error);
        showNotification('Error forking thread', 'error');
    }
},

            //  CLONE THREAD - DUPLICATE ALL MESSAGES
            async cloneThread(threadId) {
    console.log(` [cloneThread] Cloning thread: ${threadId}`);

    // Find the thread
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) {
        showNotification('Thread not found', 'error');
        return;
    }

    const messageCount = thread.message_count || thread.messages?.length || 0;

    if (messageCount === 0) {
        showNotification('Cannot clone empty thread', 'warning');
        return;
    }

    // Prompt for new name
    const newName = prompt(`Clone thread "${thread.title}"\n\nEnter new thread name:`, `${thread.title} (copy)`);
    if (!newName) return;

    try {
        const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/messages/clone`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                thread_id: threadId,
                new_name: newName,
                user_id: (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 14
            })
        });

        if (response.ok) {
            const result = await response.json();
            showNotification(`Thread cloned successfully! ${result.messages_cloned} messages copied.`, 'success');

            // Reload threads
            await this.loadThreads();
            await this.renderThreadsList();

            // Switch to new thread
            if (result.new_thread_id) {
                await this.switchThread(result.new_thread_id);
            }
        } else {
            const error = await response.json();
            showNotification(`Failed to clone thread: ${error.error || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        console.error('[cloneThread] Error:', error);
        showNotification('Error cloning thread', 'error');
    }
},

            //  NEW CHAT MODAL - COMPREHENSIVE THREAD CREATION WITH SYNERGY LINKING
            async showNewChatModal(location = 'prime') {
    console.log(` [showNewChatModal] Opening modal for location: ${location}`);

    // Define priority colors, column icons, and column names at the top
    const priorityColors = {
        'critical': { bg: '#ef444422', border: '#ef444444', text: '#ef4444' },
        'high': { bg: '#f9731622', border: '#f9731644', text: '#f97316' },
        'medium': { bg: '#3b82f622', border: '#3b82f644', text: '#3b82f6' },
        'low': { bg: '#10b98122', border: '#10b98144', text: '#10b981' }
    };

    const columnIcons = {
        'backlog': 'fa-inbox',
        'in_progress': 'fa-spinner',
        'review': 'fa-eye',
        'done': 'fa-check-circle',
        'other': 'fa-folder'
    };

    const columnNames = {
        'backlog': 'Backlog',
        'todo': 'To Do',
        'in-progress': 'In Progress',
        'in_progress': 'In Progress',
        'review': 'Review',
        'done': 'Done',
        'other': 'Other'
    };

    // Predefined tag categories
    const tagCategories = {
        'Priority': ['urgent', 'high', 'medium', 'low'],
        'Type': ['research', 'implementation', 'bug-fix', 'feature', 'documentation'],
        'Status': ['in-progress', 'blocked', 'review', 'complete']
    };

    // Fetch Synergy sessions for dropdown
    let synergySessions = [];
    try {
        const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/synergy/sessions`);
        if (response.ok) {
            synergySessions = await response.json();
            console.log(`[OK] [showNewChatModal] Loaded ${synergySessions.length} Synergy sessions`);
        }
    } catch (error) {
        console.warn(`[WARN] [showNewChatModal] Could not load Synergy sessions:`, error);
    }

    // Group sessions by column for organized display
    const sessionsByColumn = synergySessions.reduce((acc, session) => {
        const column = session.column || 'other';
        if (!acc[column]) acc[column] = [];
        acc[column].push(session);
        return acc;
    }, {});

    // Get agent display name
    const locationName = location === 'prime' ? 'Prime Agent' :
        (location.startsWith('agent-') ? `Agent ${location.split('-')[1]}` : location);

    const modalHTML = `
<div class="modal-overlay" id="newChatModalOverlay" onclick="if(event.target.id === 'newChatModalOverlay') document.getElementById('newChatModalOverlay').remove()">
    <div class="new-chat-modal" onclick="event.stopPropagation()">
        <div class="modal-header">
            <h3><i class="fas fa-plus-circle"></i> Start New Chat</h3>
            <button class="modal-close" onclick="document.getElementById('newChatModalOverlay').remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
                                                        <div class="modal-body">
                                                            <form id="newChatForm">
                                                                <!-- Thread Title -->
                                                                <div class="new-chat-form-group">
                                                                    <label for="newChatTitle">
                                                                        Thread Title
                                                                        <span style="color: var(--accent-error, #f85149);">*</span>
                                                                    </label>
                                                                    <input
                                                                        type="text"
                                                                        id="newChatTitle"
                                                                        placeholder="Enter thread title..."
                                                                        required
                                                                        autofocus
                                                                    >
                                                                </div>

                                                                <!-- Agent Assignment (Read-only display) -->
                                                                <div class="new-chat-form-group">
                                                                    <label>Assigned To</label>
                                                                    <input
                                                                        type="text"
                                                                        value="${locationName}"
                                                                        readonly
                                                                        style="background: var(--bg-tertiary, #1c2128); cursor: not-allowed;"
                                                                    >
                                                                </div>

                                                                <!-- Tags -->
                                                                <div class="new-chat-form-group">
                                                                    <label>
                                                                        Tags
                                                                        <span class="optional">(optional)</span>
                                                                    </label>
                                                                    <div class="new-chat-tag-options">
                                                                        ${Object.entries(tagCategories).flatMap(([category, tags]) =>
        tags.map(tag => `
                                                    <button type="button" class="new-chat-tag-btn" data-tag="${tag}">
                                                        ${tag}
                                                    </button>
                                                `)
    ).join('')}
                                                                    </div>
                                                                </div>

                                                                <!-- Synergy Session Link -->
                                                                <div class="new-chat-form-group">
                                                                    <label>
                                                                        Link to Synergy Session
                                                                        <span class="optional">(optional)</span>
                                                                    </label>
                                                                    
                                                                    ${synergySessions.length === 0 ? `
                                                                        <p style="margin-top: 8px; font-size: 12px; color: var(--text-muted, #9ca3af);">
                                                                            <i class="fas fa-info-circle"></i> No Synergy sessions available. Create one in the Synergy dashboard first.
                                                                        </p>
                                                                    ` : `
                                                                        <!-- Search and Sort Controls -->
                                                                        <div style="display: flex; gap: 8px; margin-bottom: 8px; align-items: center;">
                                                                            <div style="flex: 0 0 60%; position: relative;">
                                                                                <i class="fas fa-search" style="position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: var(--text-tertiary, #6b7280); font-size: 12px;"></i>
                                                                                <input 
                                                                                    type="text" 
                                                                                    id="synergySessionSearch" 
                                                                                    placeholder="Search by title or tag..."
                                                                                    style="
                                                                                        width: 100%;
                                                                                        padding: 8px 8px 8px 32px;
                                                                                        background: var(--bg-tertiary, #1c2128);
                                                                                        border: 1px solid var(--border-color, #374151);
                                                                                        border-radius: 6px;
                                                                                        color: var(--text-primary, #e6edf3);
                                                                                        font-size: 13px;
                                                                                    "
                                                                                >
                                                                            </div>
                                                                            <select id="synergySessionSort" style="flex: 0 0 30%; width: 30%;
                                                                                padding: 8px 12px;
                                                                                background: var(--bg-tertiary, #1c2128);
                                                                                border: 1px solid var(--border-color, #374151);
                                                                                border-radius: 6px;
                                                                                color: var(--text-primary, #e6edf3);
                                                                                font-size: 13px;
                                                                                cursor: pointer;
                                                                            ">
                                                                                <option value="column">By Column</option>
                                                                                <option value="date">By Date</option>
                                                                                <option value="priority">By Priority</option>
                                                                                <option value="title">By Title</option>
                                                                            </select>
                                                                        </div>
                                                                        
                                                                        <!-- Hidden input to store selected session ID -->
                                                                        <input type="hidden" id="newChatSynergySession" value="">
                                                                        
                                                                        <!-- Sessions List Container -->
                                                                        <div id="synergySessionsList" style="
                                                                            max-height: 300px;
                                                                            overflow-y: auto;
                                                                            border: 1px solid var(--border-color, #374151);
                                                                            border-radius: 6px;
                                                                            background: var(--bg-secondary, #1f2937);
                                                                        ">
                                                                            <!-- Sessions will be rendered here by JavaScript -->
                                                                        </div>
                                                                    `}
                                                                </div>
                                                            </form>
                                                        </div>
                                                        <div class="modal-footer">
                                                            <button class="btn-secondary" onclick="document.getElementById('newChatModalOverlay').remove()">
                                                                Cancel
                                                            </button>
                                                            <button class="btn-primary" id="createChatBtn">
                                                                Create Chat
                                                            </button>
                                                        </div>
                                                    </div>
                                                </div>
                                                `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Verify modal was inserted
    const modalElement = document.getElementById('newChatModalOverlay');
    console.log('✅ [showNewChatModal] Modal inserted into DOM:', modalElement ? 'YES' : 'NO');
    if (modalElement) {
        console.log(' [showNewChatModal] Modal computed styles:', {
            display: window.getComputedStyle(modalElement).display,
            visibility: window.getComputedStyle(modalElement).visibility,
            opacity: window.getComputedStyle(modalElement).opacity,
            zIndex: window.getComputedStyle(modalElement).zIndex
        });
    }

    // Initialize Synergy Sessions Browser
    if (synergySessions.length > 0) {
        const sessionsList = document.getElementById('synergySessionsList');
        const sessionSearch = document.getElementById('synergySessionSearch');
        const sessionSort = document.getElementById('synergySessionSort');
        const hiddenInput = document.getElementById('newChatSynergySession');
        let selectedSessionId = null;

        function renderSessions() {
            const searchTerm = sessionSearch.value.toLowerCase();
            const sortBy = sessionSort.value;

            // Filter sessions
            let filtered = synergySessions.filter(session => {
                if (!searchTerm) return true;
                const titleMatch = (session.title || '').toLowerCase().includes(searchTerm);
                const tagsMatch = (session.tags || '').toLowerCase().includes(searchTerm);
                const descMatch = (session.description || '').toLowerCase().includes(searchTerm);
                return titleMatch || tagsMatch || descMatch;
            });

            // Sort sessions
            filtered.sort((a, b) => {
                if (sortBy === 'date') {
                    return new Date(b.last_active || b.created_at) - new Date(a.last_active || a.created_at);
                } else if (sortBy === 'priority') {
                    const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
                    return (priorityOrder[a.priority] || 999) - (priorityOrder[b.priority] || 999);
                } else if (sortBy === 'title') {
                    return (a.title || '').localeCompare(b.title || '');
                } else { // by column
                    return (a.kanban_column || a.column || '').localeCompare(b.kanban_column || b.column || '');
                }
            });

            // Group by column if sorting by column
            if (sortBy === 'column') {
                const grouped = filtered.reduce((acc, session) => {
                    const col = session.kanban_column || session.column || 'other';
                    if (!acc[col]) acc[col] = [];
                    acc[col].push(session);
                    return acc;
                }, {});

                sessionsList.innerHTML = Object.keys(grouped).map(column => `
                                <div style="margin-bottom: 4px;">
                                    <div style="
                                        padding: 8px 12px;
                                        background: var(--bg-tertiary, #1c2128);
                                        border-bottom: 1px solid var(--border-color, #374151);
                                        font-size: 11px;
                                        font-weight: 600;
                                        color: var(--text-secondary, #9ca3af);
                                        text-transform: uppercase;
                                        letter-spacing: 0.5px;
                                        display: flex;
                                        align-items: center;
                                        gap: 6px;
                                    ">
                                        <i class="fas ${columnIcons[column] || 'fa-folder'}" style="font-size: 10px;"></i>
                                        ${columnNames[column] || column}
                                    </div>
                                    ${grouped[column].map(session => renderSessionItem(session)).join('')}
                                </div>
                            `).join('');
            } else {
                sessionsList.innerHTML = filtered.map(session => renderSessionItem(session)).join('');
            }

            // Re-highlight selected
            if (selectedSessionId) {
                const selectedEl = sessionsList.querySelector(`[data-session-id="${selectedSessionId}"]`);
                if (selectedEl) selectedEl.classList.add('selected');
            }
        }

        function renderSessionItem(session) {
            const priority = (session.priority || 'medium').toLowerCase();
            const priorityStyle = priorityColors[priority] || priorityColors['medium'];
            const column = session.kanban_column || session.column || 'other';
            const tags = session.tags ? (typeof session.tags === 'string' ? JSON.parse(session.tags) : session.tags) : [];
            const lastUpdated = session.updated_at || session.last_active || session.created_at;
            const formattedDate = lastUpdated ? new Date(lastUpdated).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : 'Unknown';
            const formattedTime = lastUpdated ? new Date(lastUpdated).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) : '';

            return `
                            <div 
                                class="synergy-session-item" 
                                data-session-id="${session.session_id}"
                                style="
                                    padding: 10px 12px;
                                    border-bottom: 1px solid var(--border-color, #374151);
                                    cursor: pointer;
                                    transition: all 0.2s ease;
                                "
                                onmouseover="this.style.background='var(--bg-tertiary, #1c2128)'"
                                onmouseout="this.classList.contains('selected') ? '' : this.style.background='transparent'"
                                onclick="
                                    document.querySelectorAll('.synergy-session-item').forEach(el => {
                                        el.classList.remove('selected');
                                        el.style.background = 'transparent';
                                    });
                                    this.classList.add('selected');
                                    this.style.background = 'var(--bg-tertiary, #1c2128)';
                                    document.getElementById('newChatSynergySession').value = '${session.session_id}';
                                "
                            >
                                <div style="display: flex; align-items: start; gap: 8px; margin-bottom: 6px;">
                                    <i class="fas ${columnIcons[column] || 'fa-folder'}" style="color: var(--text-tertiary, #6b7280); font-size: 12px; margin-top: 2px;"></i>
                                    <div style="flex: 1;">
                                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                                            <div style="font-size: 13px; font-weight: 500; color: var(--text-primary, #e6edf3);">
                                                ${session.title}
                                            </div>
                                            <span style="font-size: 10px; color: var(--text-tertiary, #6b7280); white-space: nowrap; margin-left: 8px;">
                                                <i class="fas fa-clock" style="font-size: 8px;"></i> ${formattedTime}
                                            </span>
                                        </div>
                                        ${session.description ? `
                                            <div style="font-size: 11px; color: var(--text-secondary, #9ca3af); line-height: 1.4; margin-bottom: 4px;">
                                                ${session.description.substring(0, 100)}${session.description.length > 100 ? '...' : ''}
                                            </div>
                                        ` : ''}
                                        <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-bottom: 4px;">
                                            <span style="
                                                display: inline-block;
                                                padding: 2px 6px;
                                                background: ${priorityStyle.bg};
                                                color: ${priorityStyle.text};
                                                border: 1px solid ${priorityStyle.border};
                                                border-radius: 3px;
                                                font-size: 9px;
                                                font-weight: 600;
                                                text-transform: uppercase;
                                            ">${session.priority || 'medium'}</span>
                                            <span style="
                                                display: inline-block;
                                                padding: 2px 6px;
                                                background: var(--bg-secondary, #0d1117);
                                                color: var(--text-tertiary, #6b7280);
                                                border: 1px solid var(--border-color, #374151);
                                                border-radius: 3px;
                                                font-size: 9px;
                                                font-weight: 500;
                                            ">
                                                <i class="fas ${columnIcons[column] || 'fa-folder'}" style="font-size: 8px;"></i> ${column.toUpperCase()}
                                            </span>
                                            ${tags.slice(0, 2).map(tag => `
                                                <span style="
                                                    font-size: 10px;
                                                    color: var(--text-tertiary, #6b7280);
                                                    padding: 2px 6px;
                                                    background: var(--bg-tertiary, #1c2128);
                                                    border-radius: 3px;
                                                ">
                                                    <i class="fas fa-tag" style="font-size: 8px;"></i> ${tag}
                                                </span>
                                            `).join('')}
                                            ${tags.length > 2 ? `<span style="font-size: 10px; color: var(--text-tertiary, #6b7280);">+${tags.length - 2}</span>` : ''}
                                        </div>
                                        <div style="font-size: 10px; color: var(--text-tertiary, #6b7280);">
                                            <i class="fas fa-calendar" style="font-size: 8px;"></i> Updated ${formattedDate}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
        }

        // Event listeners
        sessionSearch.addEventListener('input', renderSessions);
        sessionSort.addEventListener('change', renderSessions);

        // Initial render
        renderSessions();
    }

    // Tag toggle functionality
    const selectedTags = [];
    const tagButtons = document.querySelectorAll('.new-chat-tag-btn');
    tagButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            btn.classList.toggle('active');
            const tag = btn.dataset.tag;
            if (btn.classList.contains('active')) {
                if (!selectedTags.includes(tag)) {
                    selectedTags.push(tag);
                }
            } else {
                const index = selectedTags.indexOf(tag);
                if (index > -1) {
                    selectedTags.splice(index, 1);
                }
            }
            console.log(`� [showNewChatModal] Selected tags:`, selectedTags);
        });
    });

    // Create Chat button handler
    document.getElementById('createChatBtn').addEventListener('click', async () => {
        const titleElement = document.getElementById('newChatTitle');
        const synergySessionElement = document.getElementById('newChatSynergySession');

        // Check if title element exists
        if (!titleElement) {
            console.error('[ERROR] newChatTitle element not found');
            showNotification('Form error: Title field not found', 'error');
            return;
        }

        const title = titleElement.value.trim();
        const synergySessionId = synergySessionElement ? synergySessionElement.value : '';

        // Validation
        if (!title) {
            showNotification('Please enter a thread title', 'error');
            titleElement.focus();
            return;
        }

        if (title.length < 3) {
            showNotification('Thread title must be at least 3 characters', 'error');
            titleElement.focus();
            return;
        }

        console.log(` [showNewChatModal] Creating thread:`, {
            title,
            tags: selectedTags,
            synergy: synergySessionId,
            location
        });

        // Close modal
        document.getElementById('newChatModalOverlay').remove();

        // Create thread with all metadata (includes bidirectional Synergy linking)
        await this.createThreadWithMetadata(title, selectedTags, synergySessionId, location);
    });

    // Enter key to submit
    const titleInputElement = document.getElementById('newChatTitle');
    if (titleInputElement) {
        titleInputElement.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const createBtn = document.getElementById('createChatBtn');
                if (createBtn) createBtn.click();
            }
        });
    }
},

            async createThreadWithMetadata(title, tags, synergySessionId, location) {
    try {
        console.log(` [createThreadWithMetadata] Creating thread:`, { title, tags, synergySessionId, location });

        // 1. Create thread in backend
        const createResponse = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1,
                title: title,
                tags: tags,
                synergy_card_id: synergySessionId || null,
                location: location
            })
        });

        if (!createResponse.ok) {
            const errorText = await createResponse.text();
            console.error('[ERROR] Thread creation failed:', createResponse.status, errorText);
            throw new Error(`Thread creation failed: ${createResponse.statusText}`);
        }

        const threadData = await createResponse.json();
        console.log('[DEBUG] Backend response:', threadData);

        if (!threadData.success) {
            throw new Error(`Thread creation failed: ${threadData.error || 'Unknown error'}`);
        }

        // ✅ FIX: Backend returns thread nested in 'data' object
        const newThread = threadData.thread || threadData.data?.thread;
        if (!newThread) {
            console.error('[ERROR] No thread in response:', threadData);
            throw new Error('Backend returned success but no thread data');
        }

        const newThreadId = newThread.id || newThread.thread_id;
        console.log(`✅ [OK] [createThreadWithMetadata] Thread created:`, newThreadId);

        // ✅ CRITICAL FIX: Add new thread to this.threads array so it's available immediately
        const threadForUI = {
            id: newThreadId,
            title: title || 'Untitled Thread',
            messages: [],
            tags: tags || [],
            synergy_card_id: synergySessionId || null,
            location: location || 'prime',
            agent: location === 'prime' ? 'main' : location,
            created: newThread.created_at || new Date().toISOString(),
            updated: newThread.updated_at || new Date().toISOString(),
            message_count: 0,
            archived: false
        };

        // Add to threads array
        this.threads.unshift(threadForUI);  // Add to beginning (most recent first)
        console.log(`✅ [OK] Thread added to this.threads array, total threads: ${this.threads.length}`);

        // 2. If Synergy session selected, update it bidirectionally
        if (synergySessionId) {
            console.log(` [createThreadWithMetadata] Linking to Synergy session:`, synergySessionId);

            try {
                // Fetch current session data
                const sessionResponse = await fetch(`/api/synergy/${synergySessionId}`);
                if (sessionResponse.ok) {
                    const sessionData = await sessionResponse.json();
                    const session = sessionData.session;

                    // Parse existing thread_ids and assigned_agents (handle null, "null", "None", etc.)
                    let threadIds = [];
                    let assignedAgents = [];

                    try {
                        if (session.thread_ids && session.thread_ids !== 'null' && session.thread_ids !== 'None') {
                            threadIds = JSON.parse(session.thread_ids);
                        }
                    } catch (e) {
                        console.warn('[WARN] Failed to parse thread_ids:', session.thread_ids);
                    }

                    try {
                        if (session.assigned_agents && session.assigned_agents !== 'null' && session.assigned_agents !== 'None') {
                            assignedAgents = JSON.parse(session.assigned_agents);
                        }
                    } catch (e) {
                        console.warn('[WARN] Failed to parse assigned_agents:', session.assigned_agents);
                    }

                    // Add new thread ID if not already present
                    if (!threadIds.includes(newThreadId)) {
                        threadIds.push(newThreadId);
                    }

                    // Add agent name if not already present
                    const agentName = location === 'prime' ? 'Prime Agent' :
                        (location.startsWith('agent-') ? `Agent ${location.split('-')[1]}` : location);

                    if (!assignedAgents.includes(agentName)) {
                        assignedAgents.push(agentName);
                    }

                    // Update Synergy session
                    const updateResponse = await fetch(`/api/synergy/${synergySessionId}`, {
                        method: 'PATCH',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            updates: {
                                thread_ids: threadIds,
                                assigned_agents: assignedAgents
                            }
                        })
                    });

                    if (updateResponse.ok) {
                        console.log(`[OK] [createThreadWithMetadata] Synergy session updated with thread and agent`);
                    } else {
                        console.warn(`[WARN] [createThreadWithMetadata] Failed to update Synergy session`);
                    }
                }
            } catch (synergyError) {
                console.error(`[ERROR] [createThreadWithMetadata] Synergy linking error:`, synergyError);
                // Continue anyway - thread is created
            }
        }

        // 3. Load thread into UI (same logic as original startNewChat)
        this.currentThreadId = newThreadId;

        // Determine container ID based on location
        let containerId;
        let agentId = null;

        if (location === 'prime') {
            containerId = 'ai-chat-messages';
        } else {
            const match = location.match(/agent-(\d+)/);
            if (match) {
                agentId = parseInt(match[1]);
                containerId = `messages-${agentId}`;
            }
        }

        // Clear container
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '';
        }

        // ✅ Hide welcome container when thread is created (for Prime only)
        if (location === 'prime') {
            const welcomeContainer = document.getElementById('prime-welcome-container');
            if (welcomeContainer) {
                welcomeContainer.style.display = 'none';
                console.log('[WELCOME] Hidden - new thread created:', newThreadId);
            }
        }

        // Update AppState for Prime
        // UPDATE UI (Added Nov 8, 2025)
        if (location === 'prime') {
            // Update Prime header with comprehensive function
            this.updatePrimeHeader(newThreadId);
            this.syncAppState(newThreadId);
            console.log(`[OK] [createThreadWithMetadata] Prime header updated for thread: ${newThreadId}`);
        }

        // Update agent column header if in agent
        if (agentId) {
            // Update MultiAgent state for agent columns
            if (typeof MultiAgent !== 'undefined') {
                MultiAgent.loadedThreads[agentId] = {
                    threadId: newThreadId,
                    threadTitle: title
                };
                MultiAgent.updateAgentHeader(agentId);
                MultiAgent.saveState();
            }
        }

        // Assign thread to location in database
        if (typeof this.assignThread === 'function') {
            await this.assignThread(newThreadId, location);
        }

        // Refresh thread list (updates sidebar cards)
        this.renderThreadList();

        // CRITICAL: Auto-load thread into the location it was created for
        if (location && location.startsWith('agent-')) {
            const thread = this.threads.find(t => t.id === newThreadId);
            if (thread && typeof MultiAgent !== 'undefined') {
                MultiAgent.loadThreadIntoAgent(agentId, thread);
                console.log(`✅ [createThreadWithMetadata] Thread auto-loaded into ${location}`);

                // CRITICAL: Enable input field now that thread is loaded
                const inputEl = document.querySelector(`#agent-${agentId} .agent-chat-input`);
                const sendBtn = document.querySelector(`#agent-${agentId} .agent-send-btn`);

                if (inputEl) {
                    inputEl.disabled = false;
                    inputEl.placeholder = "Type your message...";
                    inputEl.style.opacity = '1';
                    inputEl.style.cursor = 'text';
                    inputEl.focus(); // Auto-focus for immediate typing
                }

                if (sendBtn) {
                    sendBtn.disabled = false;
                    sendBtn.style.opacity = '1';
                    sendBtn.style.cursor = 'pointer';
                }

                console.log(`[ENABLED] Input enabled for agent-${agentId}`);
            }
        } else if (location === 'prime') {
            this.loadThreadInPrime(newThreadId);
            console.log(`✅ [createThreadWithMetadata] Thread auto-loaded into Prime`);

            // CRITICAL: Enable Prime input field
            const primeInput = document.getElementById('chat-input');
            const primeSendBtn = document.querySelector('.send-btn');

            if (primeInput) {
                primeInput.disabled = false;
                primeInput.placeholder = "Type your message...";
                primeInput.style.opacity = '1';
                primeInput.style.cursor = 'text';
                primeInput.focus(); // Auto-focus for immediate typing
            }

            if (primeSendBtn) {
                primeSendBtn.disabled = false;
                primeSendBtn.style.opacity = '1';
                primeSendBtn.style.cursor = 'pointer';
            }

            console.log(`[ENABLED] Input enabled for Prime`);
        }

        const locationName = location === 'prime' ? 'AI Chat' :
            (MultiAgent ? MultiAgent.getAgentName(agentId) : location);

        showNotification(`[OK] Chat "${title}" created in ${locationName}`, 'success');
        console.log(` [createThreadWithMetadata] Complete! Thread ready to use.`);

    } catch (error) {
        console.error(`[ERROR] [createThreadWithMetadata] Error:`, error);
        showNotification(`Failed to create chat: ${error.message}`, 'error');
    }
},

startNewChat(location = 'prime') {
    console.log(`[NEW] [startNewChat] Called with location: ${location}`);

    try {
        // Create new thread
        const newThreadId = this.createThread();
        this.currentThreadId = newThreadId;
        console.log(`[OK] [startNewChat] Created thread: ${newThreadId}`);

        // Determine container ID based on location
        let containerId;
        let agentId = null;

        if (location === 'prime') {
            containerId = 'ai-chat-messages';
        } else {
            // Extract agent ID from location (e.g., 'agent-2' -> 2)
            const match = location.match(/agent-(\d+)/);
            if (match) {
                agentId = parseInt(match[1]);
                containerId = `messages-${agentId}`;
                console.log(` [startNewChat] Extracted agentId: ${agentId}, containerId: ${containerId}`);
            } else {
                console.error(`[ERROR] [startNewChat] Invalid location format: ${location}`);
                return;
            }
        }

        // Clear the container
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '';
            console.log(`[OK] [startNewChat] Cleared container: ${containerId}`);
        } else {
            console.error(`[ERROR] [startNewChat] Container not found: ${containerId}`);
        }

        // Update AppState for Prime
        if (location === 'prime' && typeof AppState !== 'undefined') {
            AppState.sessionId = newThreadId;
            AppState.chatMessages = [];
            console.log(`[OK] [startNewChat] Updated AppState for Prime`);
        }

        // For agent columns, update MultiAgent state
        if (agentId && typeof MultiAgent !== 'undefined') {
            MultiAgent.loadedThreads[agentId] = {
                threadId: newThreadId,
                threadTitle: 'New Chat'
            };
            MultiAgent.updateAgentHeader(agentId);
            MultiAgent.saveState();
            console.log(`[OK] [startNewChat] Updated MultiAgent state for agent-${agentId}`);
        }

        // Assign thread to location in database
        if (typeof this.assignThread === 'function') {
            this.assignThread(newThreadId, location);
            console.log(`[OK] [startNewChat] Thread ${newThreadId} assigned to '${location}' in database`);
        } else {
            console.warn(`[WARN] [startNewChat] assignThread function not available`);
        }

        this.renderThreadList();

        // Show input area now that thread is created
        if (location === 'prime') {
            const primeInputWrapper = document.querySelector('.ai-chat-input-wrapper');
            if (primeInputWrapper) {
                primeInputWrapper.style.display = 'flex';
                console.log('[UI] Showed Prime input wrapper (new chat started)');
            }
        } else if (agentId) {
            const agentInputArea = document.querySelector(`#agent-${agentId} .agent-input-area`);
            if (agentInputArea) {
                // Use block display so attached items (if any) sit above the input
                agentInputArea.style.display = 'block';
                console.log(`[UI] Showed agent-${agentId} input area (new chat started)`);
            }
        }

        const locationName = location === 'prime' ? 'AI Chat' : (MultiAgent ? MultiAgent.getAgentName(agentId) : location);
        showNotification(`New chat started in ${locationName}`, 'success');
        console.log(` [startNewChat] Successfully started new chat in ${locationName}`);

    } catch (error) {
        console.error(`[ERROR] [startNewChat] Error:`, error);
        showNotification(`Failed to start new chat: ${error.message}`, 'error');
    }
},

            async checkAndShowEmptyState(agentId) {
    console.log(`[SEARCH] [checkAndShowEmptyState] Checking if agent-${agentId} needs empty state...`);

    try {
        // FIXED: Use thread.location field (single source of truth) instead of API call
        const agentLocation = `agent-${agentId}`;

        // Check if any thread has this agent's location
        const assignedThread = this.threads.find(t => t.location === agentLocation);

        if (!assignedThread) {
            // Agent has NO assigned threads - show "Start New Chat" button
            console.log(`[NEW] [checkAndShowEmptyState] agent-${agentId} has no assigned thread (checked thread.location field), showing empty state`);

            const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
            if (messagesContainer) {
                // Clear any existing content
                messagesContainer.innerHTML = '';

                // Create inner div for showStartNewChatButton
                const innerDiv = document.createElement('div');
                innerDiv.className = 'agent-messages';
                innerDiv.id = `agent-messages-${agentId}`;
                innerDiv.style.height = '100%';
                messagesContainer.appendChild(innerDiv);

                // Show the button
                this.showStartNewChatButton(`agent-messages-${agentId}`, agentLocation);
            }
        } else {
            // Agent HAS an assigned thread - load it!
            console.log(`[DATA] [checkAndShowEmptyState] agent-${agentId} has assigned thread "${assignedThread.title}" (from thread.location field), auto-loading...`);

            if (typeof MultiAgent !== 'undefined') {
                MultiAgent.loadThreadIntoAgent(agentId, assignedThread);
            }
        }
    } catch (error) {
        console.error('[checkAndShowEmptyState] Error:', error);
    }
},

setFilter(filter, event) {
    this.currentFilter = filter;

    // Update tab styling (check both old and new class names)
    document.querySelectorAll('.thread-filter-tab, .thread-view-tab').forEach(tab => {
        tab.classList.remove('active');
    });

    if (typeof event !== 'undefined' && event && event.target) {
        const clickedTab = event.target.closest('.thread-filter-tab') || event.target.closest('.thread-view-tab');
        if (clickedTab) {
            clickedTab.classList.add('active');
        }
    }

    this.renderThreadList();
    console.log('[SEARCH] Filter set to:', filter);
},

// Multi-capable search: date, title, ID
filterThreads(searchQuery) {
    this.searchQuery = searchQuery.toLowerCase().trim();
    this.renderThreadList();
    console.log('[SEARCH] Filtering threads with query:', this.searchQuery);
},

// Filter by location (all/prime/all-agents/agent-1/agent-2/agent-3)
filterByLocation(location) {
    this.locationFilter = location;

    // Update chip styling
    document.querySelectorAll('.thread-filter-chip').forEach(chip => {
        chip.classList.remove('active');
    });

    const activeChip = document.querySelector(`[data-filter="${location}"]`);
    if (activeChip) {
        activeChip.classList.add('active');
    }

    // Sync dropdown selector
    const agentSelect = document.getElementById('agent-select');
    if (agentSelect && agentSelect.value !== location) {
        agentSelect.value = location;
    }

    this.renderThreadList();
    console.log('[SEARCH] Location filter set to:', location);
},

// Filter by tag (synergy/automation)
filterByTag(tag) {
    if (this.activeTagFilter === tag) {
        // Toggle off if clicking same tag
        this.activeTagFilter = null;
    } else {
        this.activeTagFilter = tag;
    }

    // Update chip styling
    document.querySelectorAll('[data-filter="synergy"], [data-filter="automation"]').forEach(chip => {
        chip.classList.remove('active');
    });

    if (this.activeTagFilter) {
        const activeChip = document.querySelector(`[data-filter="${tag}"]`);
        if (activeChip) {
            activeChip.classList.add('active');
        }
    }

    this.renderThreadList();
    console.log('[SEARCH] Tag filter set to:', this.activeTagFilter);
},

// Filter by date range
filterByDateRange(range) {
    const now = new Date();
    let startDate = null;

    switch (range) {
        case 'today':
            startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            break;
        case 'yesterday':
            startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
            break;
        case '3days':
            startDate = new Date(now.getTime() - (3 * 24 * 60 * 60 * 1000));
            break;
        case 'week':
            startDate = new Date(now.getTime() - (7 * 24 * 60 * 60 * 1000));
            break;
        case 'month':
            startDate = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate());
            break;
        case 'all':
            startDate = null;
            break;
    }

    this.dateRangeFilter = { range, startDate };

    // Sync dropdown selector
    const dateSelect = document.getElementById('date-range-select');
    if (dateSelect && dateSelect.value !== range) {
        dateSelect.value = range;
    }

    this.renderThreadList();
    console.log('[SEARCH] Date filter set to:', range, startDate);
},

// Get human-readable date label for grouping
getDateLabel(date) {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const lastWeek = new Date(today);
    lastWeek.setDate(lastWeek.getDate() - 7);

    const threadDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

    if (threadDate.getTime() === today.getTime()) {
        return 'Today';
    } else if (threadDate.getTime() === yesterday.getTime()) {
        return 'Yesterday';
    } else if (threadDate >= lastWeek) {
        return 'Last 7 Days';
    } else if (threadDate.getMonth() === now.getMonth() && threadDate.getFullYear() === now.getFullYear()) {
        return 'This Month';
    } else if (threadDate.getFullYear() === now.getFullYear()) {
        return date.toLocaleDateString('en-US', { month: 'long' });
    } else {
        return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    }
},

            // Refresh threads from backend
            async refreshThreads() {
    console.log('[SEARCH] Refreshing threads...');
    await this.loadThreads();
    if (typeof showNotification === 'function') {
        showNotification('Threads refreshed', 'success', 2000);
    }
},

toggleArchive(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;

    thread.archived = !thread.archived;
    thread.updated = new Date().toISOString();
    // TODO: Call backend update API when implemented

    const action = thread.archived ? 'archived' : 'unarchived';
    console.log(`?? Thread ${action}:`, thread.title);

    if (typeof showNotification === 'function') {
        showNotification(`Thread ${action}`, 'success', 2000);
    }

    this.renderThreadList();
},

loadThreadBySessionId() {
    const input = document.getElementById('session-id-input');
    const sessionId = input.value.trim();

    if (!sessionId) {
        if (typeof showNotification === 'function') {
            showNotification('Please enter a session ID', 'error', 2000);
        }
        return;
    }

    // Find thread by ID
    const thread = this.threads.find(t => t.id === sessionId);

    if (thread) {
        // Thread exists - switch to it
        this.switchThread(sessionId);
        input.value = '';
        console.log('Loaded thread by session ID:', sessionId);
        if (typeof showNotification === 'function') {
            showNotification('Thread loaded successfully', 'success', 2000);
        }
    } else {
        // Thread not found
        console.warn('[WARN] Thread not found:', sessionId);
        if (typeof showNotification === 'function') {
            showNotification('Thread not found. Check the session ID and try again.', 'error', 3000);
        }
    }
},

showThreadManager(threadId, event) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;

    // Get available agents from DOM
    const agentColumns = document.querySelectorAll('.agent-column');

    // Build agent options
    let agentOptions = '';
    if (agentColumns.length > 0) {
        agentColumns.forEach((column) => {
            const agentId = parseInt(column.dataset.agentId);
            const agentName = MultiAgent ? MultiAgent.getAgentName(agentId) : `Agent-${agentId}`;
            const loadedThread = MultiAgent ? MultiAgent.getLoadedThread(agentId) : null;
            const isLoaded = loadedThread && loadedThread.threadId === threadId;

            agentOptions += `
                            <button class="thread-manager-option ${isLoaded ? 'active' : ''}" 
                                    onclick="ThreadManager.sendToAgent('${threadId}', 'agent-${agentId}'); ThreadManager.closeThreadManagerMenu()">
                                <i class="fas fa-${isLoaded ? 'check-circle' : 'paper-plane'}"></i> 
                                ${isLoaded ? 'Loaded in' : 'Send to'} ${agentName}
                                ${loadedThread && !isLoaded ? `<br><small style="color: var(--text-tertiary); margin-left: 24px;">Current: ${loadedThread.threadTitle}</small>` : ''}
                            </button>
                        `;
        });
    } else {
        agentOptions = '<div style="padding: var(--space-3); color: var(--text-secondary); font-size: 12px;">No agents available. Add agents in Multi-Agent view.</div>';
    }

    // Create context menu
    const menu = document.createElement('div');
    menu.className = 'thread-manager-menu';
    menu.innerHTML = `
                                                <div class="thread-manager-header">
                                                    <i class="fas fa-cog"></i> Thread Options
                                                </div>
                                                ${agentOptions}
                                                <div class="thread-manager-divider"></div>
                                                <button class="thread-manager-option" onclick="ThreadManager.duplicateThread('${threadId}'); ThreadManager.closeThreadManagerMenu()">
                                                    <i class="fas fa-clone"></i> Duplicate Thread
                                                </button>
                                                <button class="thread-manager-option" onclick="ThreadManager.exportThread('${threadId}'); ThreadManager.closeThreadManagerMenu()">
                                                    <i class="fas fa-download"></i> Export Thread
                                                </button>
                                                `;

    // Position menu
    document.body.appendChild(menu);
    const rect = event.target.closest('button').getBoundingClientRect();
    menu.style.position = 'fixed';
    menu.style.top = rect.bottom + 5 + 'px';
    menu.style.zIndex = '10002';

    // Calculate left position - keep menu on screen
    const menuWidth = 240; // approximate width
    const viewportWidth = window.innerWidth;
    const padding = 16; // padding from edge

    let leftPosition = rect.left;
    if (leftPosition + menuWidth + padding > viewportWidth) {
        // Menu would go off-screen right, align to right edge instead
        leftPosition = Math.max(padding, viewportWidth - menuWidth - padding);
    }
    menu.style.left = leftPosition + 'px';

    // Close on click outside
    setTimeout(() => {
        document.addEventListener('click', this.closeThreadManagerMenu.bind(this), { once: true });
    }, 100);
},

closeThreadManagerMenu() {
    const menu = document.querySelector('.thread-manager-menu');
    if (menu) menu.remove();
},

getThreadByAgent(agentName) {
    // Find thread assigned to this agent
    return this.threads.find(t => t.agent === agentName && !t.archived);
},

loadThreadInAgent(threadId, agentName) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) {
        console.error(' Thread not found:', threadId);
        return false;
    }

    // Assign thread to agent
    thread.agent = agentName;
    thread.updated = new Date().toISOString();
    // TODO: Call backend assignment API when implemented

    console.log(`Loaded thread "${thread.title}" into ${agentName}`);
    if (typeof showNotification === 'function') {
        showNotification(`Thread loaded in ${agentName}`, 'success', 2000);
    }

    return true;
},

            async sendToAgent(threadId, agentIdOrName) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) {
        console.error(`[ERROR] Thread ${threadId} not found`);
        return;
    }

    // Extract agent ID from target name (e.g., "agent-1" -> 1)
    const match = agentIdOrName.match(/agent-(\d+)/);
    if (!match) {
        console.error('Invalid agent target:', agentIdOrName);
        return;
    }

    const agentId = parseInt(match[1]);
    const targetLocation = agentIdOrName;

    console.log(` [sendToAgent] Moving thread "${thread.title}" to ${targetLocation}`);

    // Check if target location already has a thread
    const existingThreadAtTarget = await this.getThreadAtLocation(targetLocation);
    if (existingThreadAtTarget && existingThreadAtTarget !== threadId) {
        console.log(`[WARN] Target location ${targetLocation} has thread ${existingThreadAtTarget}, will displace it`);

        // Find and unload that thread from MultiAgent UI
        const existingThread = this.threads.find(t => t.id === existingThreadAtTarget);
        if (existingThread) {
            console.log(` Displacing thread "${existingThread.title}" from ${targetLocation}`);
        }

        // Clear from MultiAgent UI
        if (typeof MultiAgent !== 'undefined') {
            MultiAgent.clearLoadedThread(agentId);
        }
    }

    // Assign thread via API (backend handles exclusivity)
    const assignment = await this.assignThread(threadId, targetLocation);

    if (!assignment) {
        console.error(`[ERROR] Failed to assign thread to ${targetLocation}`);
        return;
    }

    // Clear thread from Prime if currently loaded there
    const currentLocation = await this.getThreadLocation(threadId);
    if (currentLocation === 'prime' || AppState.sessionId === thread.id) {
        console.log(` Clearing thread from Prime`);

        // Clear Prime messages
        const primeMessages = document.getElementById('ai-chat-messages');
        if (primeMessages) {
            // Clean up processors
            primeMessages.querySelectorAll('[data-processor-initialized]').forEach(bubble => {
                if (bubble.processor && typeof bubble.processor.cleanup === 'function') {
                    bubble.processor.cleanup();
                }
            });
            primeMessages.innerHTML = '';
        }

        // Clear Prime session
        AppState.sessionId = null;
        AppState.chatMessages = [];

        // Add welcome message back
        if (typeof addChatMessage === 'function') {
            addChatMessage('assistant', ' **Welcome to your Business AI Platform!**\n\nThread moved to ' + (typeof MultiAgent !== 'undefined' ? MultiAgent.getAgentName(agentId) : targetLocation) + ' column.');
        }
    }

    // Clear thread from other agents if loaded elsewhere
    if (typeof MultiAgent !== 'undefined') {
        Object.keys(MultiAgent.loadedThreads).forEach(otherAgentId => {
            const otherThreadInfo = MultiAgent.loadedThreads[otherAgentId];
            if (otherThreadInfo && otherThreadInfo.threadId === thread.id && parseInt(otherAgentId) !== agentId) {
                console.log(` Clearing thread from ${MultiAgent.getAgentName(parseInt(otherAgentId))} (was in wrong location)`);

                // Clear the other agent's messages
                const otherMessages = document.querySelector(`#agent-${otherAgentId} .agent-messages`);
                if (otherMessages) {
                    // Clean up processors
                    otherMessages.querySelectorAll('[data-processor-initialized]').forEach(bubble => {
                        if (bubble.processor && typeof bubble.processor.cleanup === 'function') {
                            bubble.processor.cleanup();
                        }
                    });
                    otherMessages.innerHTML = '';
                }

                // Clear from MultiAgent state
                MultiAgent.clearLoadedThread(parseInt(otherAgentId));
            }
        });
    }

    // CRITICAL: Load thread into the MultiAgent container with full rendering
    if (typeof MultiAgent !== 'undefined') {
        console.log(` [sendToAgent] Rendering thread in ${MultiAgent.getAgentName(agentId)}`);
        MultiAgent.loadThreadIntoAgent(agentId, thread);

        // Update agent header info
        MultiAgent.updateAgentHeader(agentId);

        // Refresh thread list to show updated badges
        this.renderThreadList();

        const agentName = MultiAgent.getAgentName(agentId);
        console.log(`[OK] Thread "${thread.title}" successfully loaded into ${agentName} with ${thread.messages.length} messages rendered`);
        if (typeof showNotification === 'function') {
            showNotification(`Thread loaded into ${agentName}`, 'success', 2000);
        }
    } else {
        console.warn('[WARN] MultiAgent not available');
    }
},

getAgentDisplayName(agentIdOrName) {
    // Handle null/undefined
    if (!agentIdOrName) {
        return 'Prime'; // Default to Prime if no agent assigned
    }

    // Convert agent-1 to Alpha-1, agent-2 to Bravo-2, etc.
    const match = agentIdOrName.match(/agent-(\d+)/);
    if (match && typeof MultiAgent !== 'undefined') {
        return MultiAgent.getAgentName(parseInt(match[1]));
    }
    return agentIdOrName;
},

            async restoreThreadAssignments() {
    console.log('?? [RESTORE] Starting thread restoration using thread.location field...');
    console.log('?? [RESTORE] Total threads available:', this.threads.length);
    console.log('?? [RESTORE] Thread IDs:', this.threads.map(t => `${t.id} (${t.location || 'no location'})`));

    try {
        // Wait for MultiAgent to be ready
        if (typeof MultiAgent === 'undefined') {
            console.warn('?? [RESTORE] MultiAgent not available yet, waiting...');
            await new Promise(resolve => setTimeout(resolve, 500));
        }

        // USE THREAD.LOCATION FIELD - single source of truth from sessions.threads.location
        // Threads already loaded with location field from /api/threads/list
        const threadsInAgents = this.threads.filter(t =>
            t.location &&
            t.location !== 'prime' &&
            t.location.startsWith('agent-')
        );

        console.log(`?? [RESTORE] Found ${threadsInAgents.length} threads assigned to agents`);

        if (threadsInAgents.length === 0) {
            console.log('?? [RESTORE] No threads in agent columns to restore');
            return;
        }

        // Log what we're restoring
        threadsInAgents.forEach(t => {
            const msgCount = (t.messages && t.messages.length) || 0;
            console.log(`  ?? [RESTORE] Thread "${t.title}" (ID: ${t.id}) -> ${t.location} (${msgCount} messages)`);
        });

        // Restore each thread to its assigned agent column
        for (const thread of threadsInAgents) {
            const location = thread.location;
            const agentId = parseInt(location.replace('agent-', ''));

            console.log(`?? [RESTORE] Restoring thread "${thread.title}" (ID: ${thread.id}) to ${location}...`);

            try {
                // Update thread's agent property for consistency
                thread.agent = location;

                // Load into MultiAgent with full rendering
                if (typeof MultiAgent !== 'undefined') {
                    // CRITICAL: Use loadThreadIntoAgent for full rendering with TwoRuleStreamProcessor
                    console.log(`?? [RESTORE] Calling loadThreadIntoAgent(${agentId}, thread)`);
                    await MultiAgent.loadThreadIntoAgent(agentId, thread);

                    // Update agent header info card
                    console.log(`?? [RESTORE] Calling updateAgentHeader(${agentId})`);
                    MultiAgent.updateAgentHeader(agentId);

                    console.log(`? [RESTORE] Thread "${thread.title}" restored to ${location}`);
                }
            } catch (error) {
                console.error(`? [RESTORE] Failed to restore thread "${thread.title}":`, error);
            }

            // Small delay to prevent UI blocking
            await new Promise(resolve => setTimeout(resolve, 50));
        }

        // Refresh thread list to show all agent badges
        this.renderThreadList();

        console.log(`[OK] [RESTORE] All ${threadsInAgents.length} thread assignments restored`);

    } catch (error) {
        console.error('[ERROR] [RESTORE] Error restoring thread assignments:', error);
    }
},

// ==================== DRAG & DROP HANDLERS ====================

handleDragStart(event) {
    const threadItem = event.currentTarget;
    const threadId = threadItem.dataset.threadId;

    // Set data for transfer
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/plain', threadId);

    // Add dragging state
    threadItem.classList.add('dragging');

    console.log(' Drag started:', threadId);
},

handleDragEnd(event) {
    // Remove dragging state
    event.currentTarget.classList.remove('dragging');

    // Clean up any lingering drag-over states on agents
    document.querySelectorAll('.agent-column.drag-over').forEach(column => {
        column.classList.remove('drag-over');
    });

    console.log(' Drag ended');
},

duplicateThread(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;

    const newThread = {
        ...thread,
        id: Date.now().toString(),
        title: thread.title + ' (Copy)',
        created: new Date().toISOString(),
        updated: new Date().toISOString()
    };

    this.threads.unshift(newThread);
    // TODO: Call backend create API when implemented
    this.renderThreadList();

    console.log('[ATTACH] Thread duplicated:', newThread.title);
    if (typeof showNotification === 'function') {
        showNotification('Thread duplicated', 'success', 2000);
    }
},

exportThread(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;

    const exportData = JSON.stringify(thread, null, 2);
    const blob = new Blob([exportData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `thread-${thread.id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    console.log(' Thread exported:', thread.title);
    if (typeof showNotification === 'function') {
        showNotification('Thread exported', 'success', 2000);
    }
},

            // ==================== THREAD BRANCHING METHODS ====================

            async branchThread(parentThreadId, messageId, branchName) {
    console.log(` [branchThread] Branching from thread ${parentThreadId} at message ${messageId}`);

    try {
        const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1,
                title: branchName || `Branch from ${parentThreadId.slice(0, 8)}`,
                parent_thread_id: parentThreadId,
                branch_point_message_id: messageId,
                branch_name: branchName
            })
        });

        const data = await response.json();

        if (data.success && data.thread) {
            console.log(`[OK] [branchThread] Branch created:`, data.thread);

            // Copy messages up to branch point
            const parentThread = this.threads.find(t => t.id === parentThreadId);
            if (parentThread) {
                const branchPointIndex = parentThread.messages.findIndex(m => m.id === messageId);
                const branchedMessages = branchPointIndex >= 0
                    ? parentThread.messages.slice(0, branchPointIndex + 1)
                    : [];

                const newThread = {
                    id: data.thread.id,
                    title: data.thread.title || branchName,
                    messages: branchedMessages.map(m => ({ ...m })), // Deep copy
                    created: data.thread.created || new Date().toISOString(),
                    updated: new Date().toISOString(),
                    archived: false,
                    parent_thread_id: parentThreadId,
                    branch_point_message_id: messageId,
                    branch_name: branchName,
                    tags: []
                };

                this.threads.unshift(newThread);
                // TODO: Call backend create API for branched thread
                this.renderThreadList();

                if (typeof showNotification === 'function') {
                    showNotification(`Branch created: ${branchName}`, 'success', 3000);
                }

                return newThread;
            }
        } else {
            throw new Error(data.error || 'Failed to create branch');
        }
    } catch (error) {
        console.error('[ERROR] [branchThread] Error:', error);
        if (typeof showNotification === 'function') {
            showNotification('Failed to create branch', 'error', 3000);
        }
        return null;
    }
},

showBranchModal(parentThreadId, messageId) {
    // Create modal HTML
    const modalHTML = `
                                                <div class="modal-overlay" id="branchModalOverlay">
                                                    <div class="branch-location-modal">
                                                        <div class="modal-header">
                                                            <h3> Create Branch</h3>
                                                            <button class="modal-close" onclick="document.getElementById('branchModalOverlay').remove()">
                                                                <i class="fas fa-times"></i>
                                                            </button>
                                                        </div>
                                                        <div class="modal-body">
                                                            <div class="form-group">
                                                                <label>Branch Name:</label>
                                                                <input type="text" id="branchNameInput" placeholder="e.g., Alternative approach" class="form-control">
                                                            </div>
                                                            <div class="form-group">
                                                                <label>Where to open branch?</label>
                                                                <div class="location-buttons">
                                                                    <button class="location-btn" data-location="prime">
                                                                        <i class="fas fa-star"></i> Prime Column
                                                                    </button>
                                                                    <button class="location-btn" data-location="agent-1">
                                                                        <i class="fa-solid fa-atom"></i> Agent 1
                                                                    </button>
                                                                    <button class="location-btn" data-location="agent-2">
                                                                        <i class="fa-solid fa-atom"></i> Agent 2
                                                                    </button>
                                                                    <button class="location-btn" data-location="agent-3">
                                                                        <i class="fa-solid fa-atom"></i> Agent 3
                                                                    </button>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                                `;

    // Insert modal into DOM
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Add event listeners to location buttons
    document.querySelectorAll('.location-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const location = btn.dataset.location;
            const branchName = document.getElementById('branchNameInput').value.trim() ||
                `Branch from message ${messageId.slice(0, 8)}`;

            // Create branch
            const newThread = await this.branchThread(parentThreadId, messageId, branchName);

            if (newThread) {
                // Assign to selected location
                await this.assignThread(newThread.id, location);

                // Load in selected location
                if (location === 'prime') {
                    this.loadThread(newThread.id);
                } else {
                    const agentId = location; // 'agent-1', 'agent-2', etc.
                    if (typeof MultiAgent !== 'undefined') {
                        MultiAgent.addAgentColumn(agentId);
                        setTimeout(() => {
                            MultiAgent.loadThreadInAgent(agentId, newThread.id);
                        }, 100);
                    }
                }
            }

            // Close modal
            document.getElementById('branchModalOverlay').remove();
        });
    });

    // Close on overlay click
    document.getElementById('branchModalOverlay').addEventListener('click', (e) => {
        if (e.target.id === 'branchModalOverlay') {
            e.target.remove();
        }
    });

    // Focus input
    setTimeout(() => {
        document.getElementById('branchNameInput').focus();
    }, 100);
},

// ==================== TAG MANAGEMENT METHODS ====================

showTagModal(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;

    const currentTags = thread.tags || [];

    // Predefined tag categories
    const tagCategories = {
        'Status': ['in-progress', 'blocked', 'complete', 'archived'],
        'Priority': ['urgent', 'high', 'medium', 'low'],
        'Type': ['research', 'implementation', 'bug-fix', 'feature', 'documentation'],
        'Custom': [] // User can add custom tags
    };

    const modalHTML = `
                                                <div class="modal-overlay" id="tagModalOverlay">
                                                    <div class="tag-modal">
                                                        <div class="modal-header">
                                                            <h3>� Manage Tags</h3>
                                                            <button class="modal-close" onclick="document.getElementById('tagModalOverlay').remove()">
                                                                <i class="fas fa-times"></i>
                                                            </button>
                                                        </div>
                                                        <div class="modal-body">
                                                            ${Object.entries(tagCategories).map(([category, tags]) => `
                                    <div class="tag-category">
                                        <h4>${category}</h4>
                                        <div class="tag-options">
                                            ${tags.map(tag => `
                                                <button class="tag-option ${currentTags.includes(tag) ? 'active' : ''}" 
                                                        data-tag="${tag}">
                                                    ${tag}
                                                </button>
                                            `).join('')}
                                        </div>
                                    </div>
                                `).join('')}
                                                            <div class="tag-category">
                                                                <h4>Add Custom Tag</h4>
                                                                <div class="custom-tag-input">
                                                                    <input type="text" id="customTagInput" placeholder="Enter custom tag...">
                                                                        <button id="addCustomTagBtn">Add</button>
                                                                </div>
                                                            </div>
                                                            <div class="current-tags">
                                                                <h4>Current Tags:</h4>
                                                                <div id="currentTagsList">
                                                                    ${currentTags.map(tag => `
                                            <span class="tag-badge" data-tag="${tag}">
                                                ${tag} <span class="remove-tag">×</span>
                                            </span>
                                        `).join('') || '<em>No tags</em>'}
                                                                </div>
                                                            </div>
                                                        </div>
                                                        <div class="modal-footer">
                                                            <button class="btn-secondary" onclick="document.getElementById('tagModalOverlay').remove()">Cancel</button>
                                                            <button class="btn-primary" id="saveTagsBtn">Save Tags</button>
                                                        </div>
                                                    </div>
                                                </div>
                                                `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Tag toggle functionality
    const tagOptions = document.querySelectorAll('.tag-option');
    tagOptions.forEach(btn => {
        btn.addEventListener('click', () => {
            btn.classList.toggle('active');
            const tag = btn.dataset.tag;
            const currentTagsList = document.getElementById('currentTagsList');

            if (btn.classList.contains('active')) {
                // Add tag
                if (!currentTags.includes(tag)) {
                    currentTags.push(tag);
                    currentTagsList.innerHTML = currentTags.map(t => `
                                    <span class="tag-badge" data-tag="${t}">
                                        ${t} <span class="remove-tag">×</span>
                                    </span>
                                `).join('');
                }
            } else {
                // Remove tag
                const index = currentTags.indexOf(tag);
                if (index > -1) {
                    currentTags.splice(index, 1);
                    currentTagsList.innerHTML = currentTags.map(t => `
                                    <span class="tag-badge" data-tag="${t}">
                                        ${t} <span class="remove-tag">×</span>
                                    </span>
                                `).join('') || '<em>No tags</em>';
                }
            }

            // Re-attach remove listeners
            this.attachTagRemoveListeners();
        });
    });

    // Custom tag input
    const addCustomTagBtn = document.getElementById('addCustomTagBtn');
    const customTagInput = document.getElementById('customTagInput');

    addCustomTagBtn.addEventListener('click', () => {
        const customTag = customTagInput.value.trim().toLowerCase();
        if (customTag && !currentTags.includes(customTag)) {
            currentTags.push(customTag);
            const currentTagsList = document.getElementById('currentTagsList');
            currentTagsList.innerHTML = currentTags.map(t => `
                                                <span class="tag-badge" data-tag="${t}">
                                                    ${t} <span class="remove-tag">×</span>
                                                </span>
                                                `).join('');
            customTagInput.value = '';
            this.attachTagRemoveListeners();
        }
    });

    customTagInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addCustomTagBtn.click();
        }
    });

    // Remove tag listeners
    this.attachTagRemoveListeners();

    // Save tags
    document.getElementById('saveTagsBtn').addEventListener('click', async () => {
        await this.saveTags(threadId, currentTags);
        document.getElementById('tagModalOverlay').remove();
    });

    // Close on overlay click
    document.getElementById('tagModalOverlay').addEventListener('click', (e) => {
        if (e.target.id === 'tagModalOverlay') {
            e.target.remove();
        }
    });
},

attachTagRemoveListeners() {
    document.querySelectorAll('.remove-tag').forEach(removeBtn => {
        removeBtn.addEventListener('click', (e) => {
            const tagBadge = e.target.closest('.tag-badge');
            const tag = tagBadge.dataset.tag;
            const tagOption = document.querySelector(`.tag-option[data-tag="${tag}"]`);
            if (tagOption) {
                tagOption.classList.remove('active');
            }
            tagBadge.remove();

            // Update empty state
            const currentTagsList = document.getElementById('currentTagsList');
            if (currentTagsList.children.length === 0) {
                currentTagsList.innerHTML = '<em>No tags</em>';
            }
        });
    });
},

            async saveTags(threadId, tags) {
    console.log(`� [saveTags] Saving tags for thread ${threadId}:`, tags);

    const thread = this.threads.find(t => t.id === threadId);
    if (thread) {
        thread.tags = tags;
        thread.updated = new Date().toISOString();

        // Save to backend with COMPLETE thread data (required by /api/threads/save)
        try {
            const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    thread_id: threadId,
                    title: thread.title || thread.name || 'Untitled',
                    messages: thread.messages || [],
                    agent: thread.agent || 'prime',
                    user_id: (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1,
                    location: thread.location || 'prime',
                    tags: tags,  // ✅ Updated tags
                    synergy_card_id: thread.synergy_card_id,
                    parent_thread_id: thread.parent_thread_id,
                    branch_name: thread.branch_name
                })
            });

            const data = await response.json();
            if (data.success) {
                console.log(`[OK] [saveTags] Tags saved to backend`);
            } else {
                console.error(`[ERROR] [saveTags] Backend returned error:`, data);
            }
        } catch (error) {
            console.error('[ERROR] [saveTags] Error saving to backend:', error);
        }

        // ✅ Refresh ALL thread-info cards for this thread (Prime + Agent columns)
        this.refreshAllThreadInfoCards(threadId);

        // Refresh thread list
        this.renderThreadList();

        if (typeof showNotification === 'function') {
            showNotification('Tags updated', 'success', 2000);
        }
    }
},

            // ==================== SYNERGY KANBAN INTEGRATION METHODS ====================

            async showSynergyCardPicker(threadId) {
    console.log(` [showSynergyCardPicker] Opening card picker for thread ${threadId}`);

    try {
        // Fetch available Synergy cards
        const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/synergy/sessions`);
        const sessions = await response.json();

        if (!Array.isArray(sessions)) {
            throw new Error('Invalid response from Synergy API');
        }

        const modalHTML = `
                                                <div class="modal-overlay" id="synergyPickerOverlay">
                                                    <div class="synergy-picker-modal">
                                                        <div class="modal-header">
                                                            <h3> Link to Synergy Card</h3>
                                                            <button class="modal-close" onclick="document.getElementById('synergyPickerOverlay').remove()">
                                                                <i class="fas fa-times"></i>
                                                            </button>
                                                        </div>
                                                        <div class="modal-body">
                                                            <div class="synergy-card-list">
                                                                ${sessions.length === 0 ? '<p>No Synergy cards available</p>' :
                sessions.map(card => `
                                            <div class="synergy-card-item" data-session-id="${card.session_id}">
                                                <div class="card-title">${card.title}</div>
                                                <div class="card-meta">
                                                    <span class="card-project">${card.project || 'No Project'}</span>
                                                    <span class="card-column">${card.column || 'Unknown'}</span>
                                                </div>
                                            </div>
                                        `).join('')}
                                                            </div>
                                                        </div>
                                                        <div class="modal-footer">
                                                            <button class="btn-secondary" onclick="document.getElementById('synergyPickerOverlay').remove()">Cancel</button>
                                                        </div>
                                                    </div>
                                                </div>
                                                `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Add click listeners to cards
        document.querySelectorAll('.synergy-card-item').forEach(item => {
            item.addEventListener('click', async () => {
                const sessionId = item.dataset.sessionId;
                await this.linkToSynergyCard(threadId, sessionId);
                document.getElementById('synergyPickerOverlay').remove();
            });
        });

        // Close on overlay click
        document.getElementById('synergyPickerOverlay').addEventListener('click', (e) => {
            if (e.target.id === 'synergyPickerOverlay') {
                e.target.remove();
            }
        });

    } catch (error) {
        console.error('[ERROR] [showSynergyCardPicker] Error:', error);
        if (typeof showNotification === 'function') {
            showNotification('Failed to load Synergy cards', 'error', 3000);
        }
    }
},

            async linkToSynergyCard(threadId, synergyCardId) {
    console.log(` [linkToSynergyCard] Linking thread ${threadId} to card ${synergyCardId}`);

    const thread = this.threads.find(t => t.id === threadId);
    if (thread) {
        thread.synergy_card_id = synergyCardId;
        thread.updated = new Date().toISOString();

        // Save to backend with COMPLETE thread data (required by /api/threads/save)
        try {
            const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    thread_id: threadId,
                    title: thread.title || thread.name || 'Untitled',
                    messages: thread.messages || [],
                    agent: thread.agent || 'prime',
                    user_id: (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1,
                    location: thread.location || 'prime',
                    tags: thread.tags || [],
                    synergy_card_id: synergyCardId,  // ✅ Link to Synergy card
                    parent_thread_id: thread.parent_thread_id,
                    branch_name: thread.branch_name
                })
            });

            const data = await response.json();
            if (data.success) {
                console.log(`[OK] [linkToSynergyCard] Linked to backend`);
            } else {
                console.error(`[ERROR] [linkToSynergyCard] Backend returned error:`, data);
            }
        } catch (error) {
            console.error('[ERROR] [linkToSynergyCard] Error saving to backend:', error);
        }

        // ✅ Refresh ALL thread-info cards for this thread (Prime + Agent columns)
        this.refreshAllThreadInfoCards(threadId);

        // Refresh thread list
        this.renderThreadList();

        if (typeof showNotification === 'function') {
            showNotification('Linked to Synergy card', 'success', 2000);
        }
    }
},

// Helper: Open Synergy session (navigate to Synergy dashboard)
openSynergySession(sessionId) {
    console.log(` [openSynergySession] Opening session: ${sessionId}`);

    // TODO: Implement Synergy dashboard navigation
    // For now, just show notification
    if (typeof showNotification === 'function') {
        showNotification(`Opening Synergy session: ${sessionId}`, 'info', 3000);
    }

    // Future: Navigate to Synergy dashboard tab/panel and highlight the session card
    // if (typeof SynergyDashboard !== 'undefined') {
    //     SynergyDashboard.openSession(sessionId);
    // }
},

// Helper: Unlink thread from Synergy (wrapper for clarity in header)
unlinkFromSynergy(threadId) {
    console.log(` [unlinkFromSynergy] Wrapper call for thread: ${threadId}`);

    showConfirmation(
        'Unlink from Synergy?',
        'This will remove the connection to the Synergy session. The thread will not be deleted.',
        () => {
            this.unlinkFromSynergyCard(threadId);

            // Update Prime header if this is the current thread
            if (this.currentThreadId === threadId) {
                const thread = this.threads.find(t => t.id === threadId);
                if (thread) {
                    this.updatePrimeHeader(thread);
                }
            }
        }
    );
},

            async unlinkFromSynergyCard(threadId) {
    console.log(` [unlinkFromSynergyCard] Unlinking thread ${threadId}`);

    const thread = this.threads.find(t => t.id === threadId);
    const oldSynergyCardId = thread ? thread.synergy_card_id : null;

    if (thread) {
        thread.synergy_card_id = null;
        thread.updated = new Date().toISOString();

        // Save to backend with COMPLETE thread data (required by /api/threads/save)
        try {
            const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    thread_id: threadId,
                    title: thread.title || thread.name || 'Untitled',
                    messages: thread.messages || [],
                    agent: thread.agent || 'prime',
                    user_id: (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1,
                    location: thread.location || 'prime',
                    tags: thread.tags || [],
                    synergy_card_id: null,  // ✅ Explicitly null to unlink
                    parent_thread_id: thread.parent_thread_id,
                    branch_name: thread.branch_name
                })
            });

            const data = await response.json();
            if (data.success) {
                console.log(`[OK] [unlinkFromSynergyCard] Unlinked from backend`);
            } else {
                console.error(`[ERROR] [unlinkFromSynergyCard] Backend returned error:`, data);
            }
        } catch (error) {
            console.error('[ERROR] [unlinkFromSynergyCard] Error saving to backend:', error);
        }

        // ✅ Refresh ALL thread-info cards for this thread (Prime + Agent columns)
        this.refreshAllThreadInfoCards(threadId);

        // ✅ Refresh Synergy card linked threads section
        if (oldSynergyCardId && window.synergyBoard) {
            window.synergyBoard.refreshCardThreads(oldSynergyCardId);
        }

        // Refresh thread list
        this.renderThreadList();

        if (typeof showNotification === 'function') {
            showNotification('Unlinked from Synergy card', 'success', 2000);
        }
    }
},

// ==================== MESSAGE CREATION WITH METADATA ====================

createMessage(role, content, metadata = {}) {
    const message = {
        id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        role: role, // 'user', 'assistant', 'system'
        content: content,
        timestamp: new Date().toISOString(),
        metadata: {
            model: metadata.model || null,
            thinking_time: metadata.thinking_time || null,
            tool_calls: metadata.tool_calls || [],
            attachments: metadata.attachments || [],
            edits: metadata.edits || [],
            ...metadata
        }
    };

    console.log(` [createMessage] Created ${role} message:`, message.id);
    return message;
},

// Enhanced version for agent messages with full metadata
createAgentMessage(content, agentMetadata = {}) {
    return this.createMessage('assistant', content, {
        model: agentMetadata.model || 'claude-sonnet-4',
        thinking_time: agentMetadata.thinking_time || null,
        tool_calls: agentMetadata.tool_calls || [],
        provider: agentMetadata.provider || 'anthropic',
        temperature: agentMetadata.temperature || null,
        max_tokens: agentMetadata.max_tokens || null
    });
},

// Add message to current thread
addMessageToThread(message, threadId = null) {
    const targetThreadId = threadId || this.currentThreadId;
    const thread = this.threads.find(t => t.id === targetThreadId);

    if (thread) {
        if (!thread.messages) {
            thread.messages = [];
        }

        // QUICK FIX (Nov 20, 2025): Prevent duplicate messages
        const isDuplicate = thread.messages.some(existing => {
            // Compare role
            if (existing.role !== message.role) return false;

            // Compare content (normalize both to JSON for comparison)
            const normalizeContent = (content) => {
                if (typeof content === 'string') {
                    return JSON.stringify([{ type: 'text', text: content }]);
                }
                if (Array.isArray(content)) {
                    // Deduplicate text blocks before comparison
                    const seen = new Set();
                    const deduped = content.filter(block => {
                        if (block.type === 'text') {
                            const text = block.text || block.content || '';
                            if (seen.has(text)) return false;
                            seen.add(text);
                            return true;
                        }
                        return true;
                    });
                    return JSON.stringify(deduped);
                }
                return JSON.stringify(content);
            };

            const existingContent = normalizeContent(existing.content);
            const newContent = normalizeContent(message.content);

            return existingContent === newContent;
        });

        if (isDuplicate) {
            console.warn(`[DUPLICATE PREVENTED] Message already exists in thread ${targetThreadId}`, {
                role: message.role,
                contentPreview: typeof message.content === 'string'
                    ? message.content.substring(0, 50)
                    : JSON.stringify(message.content).substring(0, 50)
            });
            return false;
        }

        // CRITICAL: Add to MessageStore (centralized storage) instead of thread.messages array
        window.MessageStore.addMessage(targetThreadId, message, {
            checkDuplicates: true,
            syncToBackend: false
        });

        thread.updated = new Date().toISOString();

        // Update message count from MessageStore
        const messages = window.MessageStore.getMessages(targetThreadId);
        thread.message_count = messages.length;

        // Refresh all thread info cards to show updated message count
        this.refreshAllThreadInfoCards(targetThreadId);

        // Note: Message already saved via backend in calling context
        console.log(`[OK] [addMessageToThread] Added message to thread ${targetThreadId}, count: ${thread.message_count}`);
        return true;
    }

    console.warn(`[WARN] [addMessageToThread] Thread ${targetThreadId} not found`);
    return false;
},

// ==================== MESSAGE BRANCH BUTTON UTILITY ====================

addBranchButtonsToMessages() {
    // Add branch buttons to all messages in chat
    const messages = document.querySelectorAll('.ai-message');

    messages.forEach((messageEl, index) => {
        // Skip if already has branch button
        if (messageEl.querySelector('.ai-message-branch-btn')) return;

        const header = messageEl.querySelector('.ai-message-header');
        if (!header) return;

        // Get or create actions container
        let actionsDiv = header.querySelector('.ai-message-actions');
        if (!actionsDiv) {
            actionsDiv = document.createElement('div');
            actionsDiv.className = 'ai-message-actions';
            header.appendChild(actionsDiv);
        }

        // Create branch button
        const branchBtn = document.createElement('button');
        branchBtn.className = 'ai-message-branch-btn';
        branchBtn.innerHTML = '<i class="fas fa-code-branch"></i> Branch';
        branchBtn.title = 'Create branch from this message';
        branchBtn.onclick = (e) => {
            e.stopPropagation();
            const messageId = `msg_${Date.now()}_${index}`; // Generate ID
            this.showBranchModal(this.currentThreadId, messageId);
        };

        // Insert at beginning of actions
        actionsDiv.insertBefore(branchBtn, actionsDiv.firstChild);
    });

    console.log(` Added branch buttons to ${messages.length} messages`);
}
        };

async function createNewThread() {
    // Save current thread first
    if (typeof AppState !== 'undefined' && AppState.chatMessages) {
        ThreadManager.updateCurrentThread(AppState.chatMessages);
    }

    // NEW: Call backend to create thread (gets proper UUID)
    try {
        const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1,
                agent_id: 'prime',
                title: 'New Chat'
            })
        });
        const data = await response.json();

        if (data.success && data.thread) {
            // Use backend-generated UUID
            const newThread = {
                id: data.thread.id,
                title: data.thread.title || 'New Chat',
                messages: [],
                created: data.thread.created || new Date().toISOString(),
                updated: new Date().toISOString(),
                archived: false,
                agent: 'main'
            };

            ThreadManager.threads.unshift(newThread);
            ThreadManager.currentThreadId = newThread.id;
            console.log('[OK] New thread created with backend UUID:', newThread.id);
        } else {
            // Fallback to local creation if backend fails
            console.warn('[WARN] Backend thread creation failed, using fallback');
            ThreadManager.currentThreadId = ThreadManager.createThread();
        }
    } catch (error) {
        console.error(' Failed to create thread via backend:', error);
        // Fallback to local creation
        ThreadManager.currentThreadId = ThreadManager.createThread();
    }

    // Clear messages
    const messagesContainer = document.getElementById('ai-chat-messages');
    messagesContainer.innerHTML = '';
    if (typeof AppState !== 'undefined') {
        AppState.chatMessages = [];
    }

    // Add welcome message (conditional based on auth platform)
    const userProfile = UserAuth.user || JSON.parse(localStorage.getItem('userProfile') || '{ }');
    const authPlatform = userProfile.auth_platform;

    let welcomeMessage = ' <strong>Welcome to your Business AI Platform!</strong><br><br>';

    if (authPlatform === 'microsoft') {
        // Microsoft 365 user - show only M365 platforms
        welcomeMessage += 'I\'m your AI assistant with access to <strong>Microsoft 365 platforms</strong> and <strong>50+ tools</strong>.<br><br>';
        welcomeMessage += 'I can help you:<br>';
        welcomeMessage += '• � Manage Outlook emails and calendar<br>';
        welcomeMessage += '•  Access OneDrive files and SharePoint<br>';
        welcomeMessage += '•  Interact with Microsoft Teams<br>';
        welcomeMessage += '•  Work with OneNote and To Do<br>';
        welcomeMessage += '• [CHART] Analyze data (Supabase, Google Analytics)<br>';
        welcomeMessage += '•  Manage orders (WooCommerce, Stripe)<br>';
        welcomeMessage += 'And much more!<br><br>';
        welcomeMessage += 'Try asking: <em>"Show me my Outlook emails"</em> or <em>"What\'s on my calendar?"</em>';
    } else if (authPlatform === 'google') {
        // Google Workspace user
        welcomeMessage += 'I\'m your AI assistant with access to <strong>Google Workspace</strong> and <strong>19 platforms</strong>.<br><br>';
        welcomeMessage += 'I can help you:<br>';
        welcomeMessage += '•  Send messages (Slack, Gmail)<br>';
        welcomeMessage += '• [CHART] Analyze data (Supabase, Google Analytics)<br>';
        welcomeMessage += '•  Manage orders (WooCommerce, Stripe)<br>';
        welcomeMessage += '•  Process documents (Google Docs, Drive)<br>';
        welcomeMessage += 'And much more!<br><br>';
        welcomeMessage += 'Try asking: <em>"Show me today\'s sales"</em> or <em>"Send a Gmail"</em>';
    } else {
        // Local/traditional auth - show all
        welcomeMessage += 'I\'m your AI assistant with access to <strong>19 platforms</strong> and <strong>114+ tools</strong>.<br><br>';
        welcomeMessage += 'I can help you:<br>';
        welcomeMessage += '•  Send messages (Slack, Gmail, Twilio)<br>';
        welcomeMessage += '• [CHART] Analyze data (Supabase, Google Analytics)<br>';
        welcomeMessage += '•  Manage orders (WooCommerce, Stripe)<br>';
        welcomeMessage += '•  Process documents (Google Docs, Drive)<br>';
        welcomeMessage += 'And much more!<br><br>';
        welcomeMessage += 'Try asking: <em>"Show me today\'s sales"</em> or <em>"Send a Slack message"</em>';
    }

    addChatMessage('assistant', welcomeMessage);

    // Update Prime header for new thread
    const newThread = ThreadManager.getCurrentThread();
    if (newThread && typeof ThreadManager.updatePrimeHeader === 'function') {
        ThreadManager.updatePrimeHeader(newThread);
    }

    ThreadManager.renderThreadList();
    ThreadManager.closeThreadMenu();
    showNotification('New chat started', 'success');
}

// ==================== EXPOSE THREADMANAGER GLOBALLY ====================
// Expose ThreadManager to window for use by Synergy Dashboard and other components
window.ThreadManager = ThreadManager;
console.log('✅ ThreadManager exposed to window.ThreadManager');