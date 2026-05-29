
// ==================== PROCESSING INDICATOR ====================
/**
 * Create a processing/typing indicator that shows until first message bubble appears
 * Used for both streaming responses and thread loading
 */
function createProcessingIndicator(agentId) {
    const indicator = document.createElement('div');
    indicator.className = 'processing-indicator';
    indicator.id = `processing-indicator-${agentId}`;
    indicator.innerHTML = `
        <div class="processing-dots">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
        <span class="processing-text">Processing...</span>
    `;
    return indicator;
}

/**
 * Remove processing indicator for an agent
 */
function removeProcessingIndicator(agentId) {
    const indicator = document.getElementById(`processing-indicator-${agentId}`);
    if (indicator) {
        indicator.remove();
        console.log(`[Agent ${agentId}] Processing indicator removed`);
    }
}

/**
 * Create a sticky render-progress indicator that sits at the bottom of the messages container.
 * Shows "Loading messages… X of Y" with a thin fill bar as historical messages render one-by-one.
 */
function createRenderProgressIndicator(agentId, totalCount) {
    const el = document.createElement('div');
    el.className = 'render-progress-indicator';
    el.id = `render-progress-${agentId}`;
    // Sits as a sibling BELOW the messages container — no sticky/absolute needed
    el.style.cssText = [
        'background: var(--bg-primary, #0d1117)',
        'border-top: 1px solid var(--border-color, #30363d)',
        'padding: 8px 16px',
        'display: flex',
        'align-items: center',
        'gap: 10px',
        'font-size: 12px',
        'color: var(--text-secondary, #8b949e)',
        'z-index: 10',
        'user-select: none',
        'box-sizing: border-box',
        'flex-shrink: 0',
    ].join('; ');
    el.innerHTML = `
        <i class="fas fa-spinner fa-spin" style="color:var(--accent-primary,#58a6ff);font-size:11px;flex-shrink:0;"></i>
        <span class="rpi-text">Loading messages\u2026 0 of ${totalCount}</span>
        <div style="flex:1;height:3px;background:var(--border-color,#30363d);border-radius:2px;overflow:hidden;min-width:40px;">
            <div class="rpi-bar" style="height:100%;width:0%;background:var(--accent-primary,#58a6ff);transition:width 0.15s ease;border-radius:2px;"></div>
        </div>
    `;
    return el;
}

/** Update the render-progress indicator with current count (call every N messages). */
function updateRenderProgressIndicator(agentId, current, total) {
    const el = document.getElementById(`render-progress-${agentId}`);
    if (!el) return;
    const text = el.querySelector('.rpi-text');
    const bar = el.querySelector('.rpi-bar');
    if (text) text.textContent = `Loading messages\u2026 ${current} of ${total}`;
    if (bar) bar.style.width = `${Math.round((current / total) * 100)}%`;
}

/** Remove the render-progress indicator once all messages have been rendered. */
function removeRenderProgressIndicator(agentId) {
    const el = document.getElementById(`render-progress-${agentId}`);
    if (el) el.remove();
}

/**
 * Setup scroll detection for a messages container.
 * - Attaches a throttled scroll handler that: 
 *   - triggers a load-older callback when near the top
 *   - toggles a `user-scrolled` marker when the user scrolls away from bottom
 *
 * This is intentionally defensive: it will try several well-known callbacks if present
 * and will not throw if those callbacks are missing.
 */
function setupScrollDetection(agentId, messagesContainer) {
    try {
        if (!messagesContainer) return;

        // Simple throttle implementation (per-container)
        let lastCall = 0;
        function throttle(fn, wait) {
            return function (...args) {
                const now = Date.now();
                if (now - lastCall >= wait) {
                    lastCall = now;
                    fn.apply(this, args);
                }
            };
        }

        // Remove any existing handler to avoid duplicates
        if (messagesContainer._agentScrollHandler) {
            messagesContainer.removeEventListener('scroll', messagesContainer._agentScrollHandler);
            messagesContainer._agentScrollHandler = null;
        }

        const handler = throttle(function () {
            try {
                const atTop = messagesContainer.scrollTop <= 120;
                const atBottom = (messagesContainer.scrollTop + messagesContainer.clientHeight) >= (messagesContainer.scrollHeight - 20);

                if (atTop) {
                    console.log(`[SCROLL] Agent ${agentId}: near top — requesting older messages`);
                    // Try ThreadManager hook, or global fallback
                    if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.loadOlderMessagesForAgent === 'function') {
                        ThreadManager.loadOlderMessagesForAgent(agentId);
                    } else if (typeof loadOlderMessagesForAgent === 'function') {
                        loadOlderMessagesForAgent(agentId);
                    }
                }

                // Mark container when user has scrolled away from bottom to pause autoscroll behavior
                if (!atBottom) {
                    messagesContainer.classList.add('user-scrolled');
                } else {
                    messagesContainer.classList.remove('user-scrolled');
                }
            } catch (e) {
                console.error('[setupScrollDetection] handler error:', e);
            }
        }, 150);

        messagesContainer._agentScrollHandler = handler;
        messagesContainer.addEventListener('scroll', handler, { passive: true });

        // Run once to set initial state
        handler();
    } catch (err) {
        console.error('[setupScrollDetection] Error attaching handler:', err);
    }
}

// ==================== AGENT STOP BUTTON HELPERS ====================
/**
 * Show stop button for an agent (called when streaming starts)
 */
function showAgentStopButton(agentId) {
    const sendBtn = document.getElementById(`agent-send-${agentId}`);
    if (!sendBtn) {
        console.warn(`[Stop Button] Send button not found for agent ${agentId}`);
        return;
    }
    
    let stopBtn = document.getElementById(`agent-stop-btn-${agentId}`);
    if (!stopBtn) {
        // Create stop button if it doesn't exist
        stopBtn = document.createElement('button');
        stopBtn.id = `agent-stop-btn-${agentId}`;
        stopBtn.className = 'agent-stop-btn';
        stopBtn.innerHTML = '<i class="fas fa-stop-circle"></i>';
        stopBtn.title = 'Stop AI response';
        stopBtn.addEventListener('click', () => stopAgentStream(agentId));
        sendBtn.parentElement.appendChild(stopBtn);
    }
    
    stopBtn.style.display = 'inline-flex';
    sendBtn.style.display = 'none';
}

/**
 * Hide stop button for an agent (called when streaming ends)
 */
function hideAgentStopButton(agentId) {
    const stopBtn = document.getElementById(`agent-stop-btn-${agentId}`);
    const sendBtn = document.getElementById(`agent-send-${agentId}`);
    
    if (stopBtn) stopBtn.style.display = 'none';
    if (sendBtn) sendBtn.style.display = 'inline-flex';
}

/**
 * Stop streaming for an agent (abort the fetch request)
 */
function stopAgentStream(agentId) {
    if (MultiAgent.agentStreamControllers[agentId]) {
        console.log(`[Agent ${agentId}] 🛑 User requested stop - aborting stream`);
        MultiAgent.agentStreamControllers[agentId].abort();
        MultiAgent.agentStreamControllers[agentId] = null;
        MultiAgent.agentStreamingStates[agentId] = false;
        
        hideAgentStopButton(agentId);
        
        // Add system message to chat
        const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
        if (messagesContainer) {
            const systemMsg = document.createElement('div');
            systemMsg.className = 'message system-message';
            systemMsg.textContent = '⏸️ Response stopped by user';
            messagesContainer.appendChild(systemMsg);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }
}

// ==================== MULTI-AGENT NATO COLUMNS ====================
const MultiAgent = {
    nextAgentId: 4,
    agentNames: ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel',
        'India', 'Juliet', 'Kilo', 'Lima', 'Mike', 'November', 'Oscar', 'Papa',
        'Quebec', 'Romeo', 'Sierra', 'Tango', 'Uniform', 'Victor', 'Whiskey', 'X-ray', 'Yankee', 'Zulu'],

    // AI streaming control - AbortControllers for each agent
    agentStreamControllers: {},  // key = agentId, value = AbortController
    agentStreamingStates: {},     // key = agentId, value = boolean

    // Rainbow color palette for session presence
    PRESENCE_COLORS: [
        '#3b82f6', // blue
        '#10b981', // green
        '#f59e0b', // orange
        '#ef4444', // red
        '#8b5cf6', // purple
        '#ec4899', // pink
        '#14b8a6', // teal
        '#f97316'  // dark orange
    ],

    // Semantic icon mapping - icons represent the NATO phonetic word itself
    agentIcons: [
        'fa-crosshairs',        // Alpha-1 (precision)
        'fa-thumbs-up',         // Bravo-2 (well done!) [NEW]
        'fa-satellite-dish',    // Charlie-3 (comms - CURRENT)
        'fa-rocket',            // Delta-4 (speed/change)
        'fa-volume-up',         // Echo-5 (sound reflection) [NEW]
        'fa-paw',               // Foxtrot-6 (fox prints) [NEW]
        'fa-golf-ball',         // Golf-7 (sport) [NEW]
        'fa-hotel',             // Hotel-8 (lodging) [NEW]
        'fa-flag',              // India-9 (nation) [NEW]
        'fa-female',            // Juliet-10 (character) [NEW]
        'fa-dumbbell',          // Kilo-11 (weight) [NEW]
        'fa-lemon',             // Lima-12 (citrus) [NEW]
        'fa-microphone',        // Mike-13 (audio) [NEW]
        'fa-calendar-alt',      // November-14 (month) [NEW]
        'fa-award',             // Oscar-15 (award statue) [NEW]
        'fa-church',            // Papa-16 (Pope) [NEW]
        'fa-map-marked-alt',    // Quebec-17 (province mapping) [NEW]
        'fa-heart',             // Romeo-18 (romance) [NEW]
        'fa-mountain',          // Sierra-19 (range) [NEW]
        'fa-music',             // Tango-20 (dance music) [NEW]
        'fa-user-tie',          // Uniform-21 (professional) [NEW]
        'fa-trophy',            // Victor-22 (victory) [NEW]
        'fa-glass-whiskey',     // Whiskey-23 (drink) [NEW]
        'fa-x-ray',             // X-ray-24 (medical) [NEW]
        'fa-flag-usa',          // Yankee-25 (American) [NEW]
        'fa-shield',            // Zulu-26 (warrior) [NEW]
    ],
    sessions: {},
    streams: {},
    loadedThreads: {},  // Track which thread is loaded in each agent

    // Get NATO name with dash-number format
    getAgentName(agentId) {
        const natoName = this.agentNames[agentId - 1] || `Agent`;
        return `${natoName}-${agentId}`;
    },

    // Get Font Awesome icon class for agent
    getAgentIcon(agentId) {
        return this.agentIcons[agentId - 1] || 'fa-atom';
    },

    // Get bespoke welcome message for each agent
    getAgentWelcomeMessage(agentId, agentName) {
        // Get user info from AppState or localStorage
        const userData = AppState.user || JSON.parse(localStorage.getItem('user_profile') || '{}');
        const userName = userData.username || userData.nickname || userData.email?.split('@')[0] || 'there';

        // Get time-based greeting and context
        const hour = new Date().getHours();
        const day = new Date().getDay(); // 0 = Sunday, 1 = Monday, etc.
        let timeGreeting = 'Hi';
        let timeContext = '';

        // Morning greetings (5am-12pm)
        const morningContexts = [
            'Ready to start the day strong?',
            'Let\'s make today productive!',
            'Coffee ready? Let\'s do this!',
            'Fresh start, fresh ideas!',
            'What are we tackling first today?',
            day === 1 ? 'Happy Monday! Let\'s conquer this week!' : 'Feeling energized?'
        ];

        // Afternoon greetings (12pm-5pm)
        const afternoonContexts = [
            'How\'s your day going?',
            'Making good progress?',
            'Need a hand with anything?',
            'Afternoon hustle time!',
            'Let\'s keep the momentum going!',
            'What can I help you wrap up?'
        ];

        // Evening greetings (5pm-10pm)
        const eveningContexts = [
            'Hope you had a great day!',
            'Wrapping things up?',
            'Still going strong, I see!',
            'Evening productivity mode?',
            'Let\'s finish strong!',
            day === 5 ? 'Almost the weekend! What do you need?' : 'How can I help wrap up your day?'
        ];

        // Late night greetings (10pm-5am)
        const lateNightContexts = [
            'Burning the midnight oil?',
            'Night owl session?',
            'Late night grind mode activated!',
            'Can\'t sleep either? Let\'s work!',
            'Your dedication is impressive!',
            'The quiet hours are the best for focus, right?'
        ];

        if (hour >= 5 && hour < 12) {
            timeGreeting = 'Good morning';
            timeContext = morningContexts[Math.floor(Math.random() * morningContexts.length)];
        } else if (hour >= 12 && hour < 17) {
            timeGreeting = 'Good afternoon';
            timeContext = afternoonContexts[Math.floor(Math.random() * afternoonContexts.length)];
        } else if (hour >= 17 && hour < 22) {
            timeGreeting = 'Good evening';
            timeContext = eveningContexts[Math.floor(Math.random() * eveningContexts.length)];
        } else {
            timeGreeting = 'Hey';
            timeContext = lateNightContexts[Math.floor(Math.random() * lateNightContexts.length)];
        }

        // Array of conversational welcome messages (expanded to 12 variations)
        const welcomeVariations = [
            {
                greeting: `${timeGreeting} ${userName}! `,
                main: `I'm ${agentName}, ready to rock and roll.`,
                action: `You can <strong>drag a thread</strong> from the sidebar to continue working, or just let me know what you need assistance with!`
            },
            {
                greeting: `${timeGreeting}! `,
                main: `${timeContext} I'm here to help with whatever you need.`,
                action: `Have a project for me? Or maybe a conversation thread you'd like me to continue?`
            },
            {
                greeting: `Hey ${userName}! `,
                main: `${agentName} reporting for duty.`,
                action: `Want to give me a rundown of what you need? Or drop a thread here and I'll pick up where you left off.`
            },
            {
                greeting: `${timeGreeting}! [NEW]`,
                main: `Ready when you are.`,
                action: `Just <strong>drag and drop a thread</strong> here to continue working, or start fresh with a new task!`
            },
            {
                greeting: `Hi there! `,
                main: `${agentName} is online and ready to help.`,
                action: `Need assistance with something? Or have a chat thread you want me to continue working through?`
            },
            {
                greeting: `${timeGreeting} ${userName}! `,
                main: `${timeContext}`,
                action: `I can jump into an existing conversation thread or start something new. What sounds good?`
            },
            {
                greeting: `Yo ${userName}! `,
                main: `${agentName} here, standing by.`,
                action: `Drop a thread my way to pick up where you left off, or tell me what's on your mind!`
            },
            {
                greeting: `${timeGreeting}! ⚡`,
                main: `Let's get to work! ${timeContext}`,
                action: `You can <strong>drag any conversation thread</strong> here to continue, or we can start something fresh.`
            },
            {
                greeting: `Hey hey ${userName}! `,
                main: `${agentName} at your service!`,
                action: `What are we working on? Got a thread for me to continue, or a new challenge to tackle?`
            },
            {
                greeting: `${timeGreeting}! `,
                main: `${timeContext} Let's make something happen!`,
                action: `Whether it's a new project or continuing an existing conversation, I'm ready to dive in.`
            },
            {
                greeting: `Well hello ${userName}! `,
                main: `${agentName} is ready to roll up the sleeves.`,
                action: `Need me to continue a chat? Just <strong>drag the thread here</strong>. Or let's start something new!`
            },
            {
                greeting: `${timeGreeting}! `,
                main: `What's on the agenda today?`,
                action: `I can pick up where any conversation left off, or we can start fresh. Your call, ${userName}!`
            }
        ];

        // Pick a random variation
        const variation = welcomeVariations[Math.floor(Math.random() * welcomeVariations.length)];

        // Get tool count for footer
        const toolCount = ToolManager?.availableTools?.length || 594;
        const platformCount = ToolManager?.toolsByPlatform?.size || 20;

        return `
                    <div style="line-height: 1.8; padding: 10px;">
                        <div style="font-size: 1.3em; margin-bottom: 12px; font-weight: 500;">
                            ${variation.greeting}
                        </div>
                        <div style="margin-bottom: 15px; font-size: 1.05em;">
                            ${variation.main}
                        </div>
                        <div style="margin-bottom: 20px; opacity: 0.9;">
                            ${variation.action}
                        </div>
                        <div style="background: rgba(255, 255, 255, 0.05); padding: 14px; border-radius: 8px; border-left: 3px solid #58a6ff; margin-bottom: 15px;">
                            <div style="font-weight: 600; margin-bottom: 8px; font-size: 0.95em;"> Quick Tip</div>
                            <div style="opacity: 0.9; font-size: 0.95em; line-height: 1.6;">
                                <strong>Drag & drop threads</strong> from the sidebar to move conversations between agents. 
                                All formatting, context, and history stays intact!
                            </div>
                        </div>
                        <div style="margin-top: 15px; padding: 12px; background: rgba(88, 166, 255, 0.12); border: 1px solid rgba(88, 166, 255, 0.25); border-radius: 8px; text-align: center;">
                            <div style="font-size: 0.9em; opacity: 0.85;">
                                <strong>[NEW] Enhanced AI Platform</strong><br>
                                <span style="font-size: 0.85em;">${toolCount} tools • ${platformCount}+ platforms • Interactive visualizations</span>
                            </div>
                        </div>
                    </div>
                `;
    },

    // Set loaded thread for agent
    setLoadedThread(agentId, threadId, threadTitle, messageCount = 0, metadata = {}) {
        console.log(`📌 [setLoadedThread] Agent ${agentId}: thread ${threadId}, title "${threadTitle}"`);
        this.loadedThreads[agentId] = {
            threadId,
            threadTitle,
            messageCount,
            loadedAt: new Date().toISOString(),
            synergyCardId: metadata.synergyCardId || null,
            synergySessionName: metadata.synergySessionName || null,
            workflowId: metadata.workflowId || null,
            automationId: metadata.automationId || null
        };

        // Update header immediately
        this.updateAgentHeader(agentId);

        // If ThreadManager not ready yet (during startup), retry after delay
        if (typeof ThreadManager === 'undefined' || typeof ThreadManager.renderThreadInfoContainer !== 'function') {
            console.log(`⏳ [setLoadedThread] ThreadManager not ready, will retry in 500ms`);
            setTimeout(() => {
                console.log(`🔄 [setLoadedThread] Retrying header update for agent ${agentId}`);
                this.updateAgentHeader(agentId);
            }, 500);
        }

        this.saveState();
    },

    // Get loaded thread for agent
    getLoadedThread(agentId) {
        return this.loadedThreads[agentId] || null;
    },

    // CRITICAL: Get current location of a thread (Prime or agent-X)
    getThreadCurrentLocation(threadId) {
        // Check if thread is in Prime
        if (typeof ThreadManager !== 'undefined' && ThreadManager.currentThreadId === threadId) {
            return 'prime';
        }

        // Check if thread is loaded in any agent
        for (const [agentId, threadInfo] of Object.entries(this.loadedThreads)) {
            if (threadInfo && threadInfo.threadId === threadId) {
                return `agent-${agentId}`;
            }
        }

        return null; // Thread not currently loaded anywhere
    },

    // CRITICAL: Clear thread from agent (used when moving to Prime or another agent)
    clearAgentThread(agentId) {
        const oldThreadId = this.sessions[agentId];
        console.log(`[CLEAR] Clearing thread from agent-${agentId} (threadId: ${oldThreadId})`);

        // ✅ CRITICAL FIX: Clear MessageStore for this thread
        if (oldThreadId && typeof window.MessageStore !== 'undefined') {
            window.MessageStore.clearThread(oldThreadId);
            console.log(`[CLEAR] ✅ Cleared ${window.MessageStore.getMessageCount(oldThreadId)} messages from MessageStore for thread ${oldThreadId}`);
        }

        // Clear loaded thread state
        delete this.loadedThreads[agentId];
        this.sessions[agentId] = null;
        console.log(`[ISOLATION] ✅ Agent-${agentId} session cleared`);

        // Clear UI and show empty state (Dec 9, 2025 FIX)
        if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.unloadThread === 'function') {
            // Use AgentColumn.unloadThread to properly show empty state with welcome message
            AgentColumn.unloadThread(agentId);
            console.log(`[CLEAR] Called AgentColumn.unloadThread for agent ${agentId}`);
        } else {
            // Fallback: Clear UI manually (preserve scroll controls)
            const messagesContainer = document.querySelector(`#agent-column-${agentId} .agent-messages-container`);
            if (messagesContainer) {
                const messages = messagesContainer.querySelectorAll('.message-bubble, .ai-message');
                console.log(`[CLEAR] Removing ${messages.length} old messages from DOM for agent-${agentId}`);
                messages.forEach(msg => msg.remove());
            }

            // Update thread info header - Keep EMPTY when no thread loaded
            const threadInfoContainer = document.getElementById(`thread-info-${agentId}`);
            if (threadInfoContainer) {
                threadInfoContainer.innerHTML = `
                    <div class="thread-info-wrapper">
                    </div>
                `;
            }
        }

        this.saveState();
        this.updateQuickNavBadge(agentId);

        console.log(`[OK] Agent ${agentId} cleared`);
    },

    // CRITICAL: Validate session isolation (prevents duplicate sessions)
    validateSessionIsolation(threadId, expectedLocation) {
        // NOTE: This is a DIAGNOSTIC function only - it logs warnings but NEVER blocks user actions
        // Users can freely move threads at any time - this just helps track state consistency
        console.log(`[ISOLATION CHECK] Thread ${threadId} should be in ${expectedLocation}`);

        const issues = [];

        // Check Prime
        if (typeof ThreadManager !== 'undefined' && ThreadManager.currentThreadId === threadId) {
            if (expectedLocation !== 'prime') {
                issues.push(`Prime has thread but location is ${expectedLocation}`);
                console.warn(`⚠️ [ISOLATION VIOLATION] Prime has thread ${threadId} but location is ${expectedLocation}`);
            }
        }

        // Check AppState.sessionId (critical for Prime)
        if (typeof AppState !== 'undefined' && AppState.sessionId === threadId) {
            if (expectedLocation !== 'prime') {
                issues.push(`AppState.sessionId has thread but location is ${expectedLocation}`);
                console.warn(`⚠️ [ISOLATION VIOLATION] AppState.sessionId has thread ${threadId} but location is ${expectedLocation}`);
            }
        }

        // Check agents
        [1, 2, 3].forEach(agentId => {
            const hasThread = this.sessions[agentId] === threadId;
            const shouldHave = expectedLocation === `agent-${agentId}`;

            if (hasThread && !shouldHave) {
                issues.push(`Agent-${agentId} has thread but location is ${expectedLocation}`);
                console.warn(`⚠️ [ISOLATION VIOLATION] Agent-${agentId} has thread ${threadId} but location is ${expectedLocation}`);
            }

            if (!hasThread && shouldHave) {
                issues.push(`Agent-${agentId} should have thread but doesn't`);
                console.warn(`⚠️ [ISOLATION VIOLATION] Agent-${agentId} should have thread ${threadId} but doesn't`);
            }
        });

        if (issues.length > 0) {
            console.error(` [ISOLATION VIOLATION] ${issues.length} issue(s):`, issues);
            return false;
        }

        console.log(`✅ [ISOLATION OK] Thread correctly isolated to ${expectedLocation}`);
        return true;
    },

    // Clear loaded thread
    clearLoadedThread(agentId) {
        delete this.loadedThreads[agentId];
        this.updateAgentHeader(agentId);
        this.saveState();

        // [NEW] After clearing, check if this agent has any OTHER assigned threads from database
        // If not, show "Start New Chat" button
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.checkAndShowEmptyState === 'function') {
            ThreadManager.checkAndShowEmptyState(agentId);
        }
    },

    // Build agent quick-nav bar (backend-driven)
    buildQuickNav(maxAgentId, assignments) {
        const navContainer = document.querySelector('.agent-quick-nav-container');
        if (!navContainer) {
            console.warn('⚠️ [Multi-Agent] Quick nav container not found');
            return;
        }

        navContainer.innerHTML = '';

        // Create badges ONLY for agents that exist (1 to maxAgentId)
        for (let i = 1; i <= maxAgentId; i++) {
            const agentName = this.getAgentName(i);
            const agentIcon = this.getAgentIcon(i);
            const location = `agent-${i}`;
            const threadInfo = assignments[location];

            // Get actual message count from ThreadManager (if available)
            let messageCount = 0;
            if (threadInfo && typeof ThreadManager !== 'undefined' && Array.isArray(ThreadManager.threads)) {
                const thread = ThreadManager.threads.find(t => t.id === threadInfo);
                if (thread) {
                    messageCount = thread.messages?.length || thread.message_count || 0;
                }
            }

            const badge = document.createElement('div');
            badge.className = 'agent-quick-nav-badge';
            badge.id = `quick-nav-badge-${i}`;
            badge.dataset.agentId = i;

            // Highlight if agent has thread assignment
            if (threadInfo) {
                badge.classList.add('has-thread');

                // Get full thread info for tooltip
                let fullThreadInfo = null;
                if (typeof ThreadManager !== 'undefined' && Array.isArray(ThreadManager.threads)) {
                    const thread = ThreadManager.threads.find(t => t.id === threadInfo);
                    if (thread) {
                        fullThreadInfo = {
                            threadId: thread.id,
                            threadTitle: thread.title,
                            messageCount: messageCount,
                            synergyCardId: thread.synergy_card_id || null,
                            synergySessionName: thread.synergy_card_name || null,
                            workflowId: thread.workflow_id || null,
                            automationId: thread.automation_id || null
                        };
                    }
                }

                // Add tooltip data
                this.addBadgeTooltipData(badge, i, fullThreadInfo, messageCount);
            }

            // Initialize message count tracking (for new message detection)
            badge.dataset.messageCount = messageCount.toString();

            badge.innerHTML = `
                        <i class="fas ${agentIcon}"></i>
                        <span>${agentName}</span>
                        ${messageCount > 0 ? `<span class="thread-indicator">${messageCount}</span>` : ''}
                    `;

            badge.onclick = () => this.scrollToAgent(i);
            navContainer.appendChild(badge);
        }

        console.log(`✅ [Command Center] Quick nav built with ${maxAgentId} agent badges (from backend assignments)`);
        
        // Update scroll button visibility
        if (typeof updateQuickNavScrollButtons === 'function') {
            setTimeout(updateQuickNavScrollButtons, 100);
        }
    },            // Add badge for new agent
    addQuickNavBadge(agentId) {
        const navContainer = document.querySelector('.agent-quick-nav-container');
        if (!navContainer) return;

        // Check if badge already exists
        if (document.getElementById(`quick-nav-badge-${agentId}`)) {
            console.log(`[Command Center] Badge for ${this.getAgentName(agentId)} already exists`);
            return;
        }

        const agentName = this.getAgentName(agentId);
        const agentIcon = this.getAgentIcon(agentId);

        const badge = document.createElement('div');
        badge.className = 'agent-quick-nav-badge';
        badge.id = `quick-nav-badge-${agentId}`;
        badge.dataset.agentId = agentId;
        badge.innerHTML = `
                    <i class="fas ${agentIcon}"></i>
                    <span>${agentName}</span>
                `;

        badge.onclick = () => this.scrollToAgent(agentId);
        navContainer.appendChild(badge);

        console.log(`[Command Center] Added badge for ${agentName}`);
        this.updateDashboardStats();
        
        // Update scroll button visibility
        if (typeof updateQuickNavScrollButtons === 'function') {
            setTimeout(updateQuickNavScrollButtons, 100);
        }
    },

    // Remove badge when agent closed
    removeQuickNavBadge(agentId) {
        const badge = document.getElementById(`quick-nav-badge-${agentId}`);
        if (badge) {
            badge.remove();
            console.log(`[Command Center] Removed badge for ${this.getAgentName(agentId)}`);
            this.updateDashboardStats();
            
            // Update scroll button visibility
            if (typeof updateQuickNavScrollButtons === 'function') {
                setTimeout(updateQuickNavScrollButtons, 100);
            }
        }
    },

    // Add tooltip data to badge
    addBadgeTooltipData(badge, agentId, threadInfo, messageCount) {
        if (!badge) return;

        const agentName = this.getAgentName(agentId);
        let tooltipTitle = agentName;
        let tooltipLines = [];

        // Thread title
        if (threadInfo?.threadTitle) {
            tooltipTitle = threadInfo.threadTitle;
            tooltipLines.push(`<div style="color: #94a3b8; font-size: 12px; margin-bottom: 4px;">${agentName}</div>`);
        }

        // Message count
        tooltipLines.push(`<div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
                    <i class="fas fa-comments" style="color: #60a5fa;"></i>
                    <span><strong>${messageCount}</strong> message${messageCount !== 1 ? 's' : ''}</span>
                </div>`);

        // Last activity - get from actual thread.updated, not loadedAt
        if (threadInfo?.threadId && typeof ThreadManager !== 'undefined' && Array.isArray(ThreadManager.threads)) {
            const thread = ThreadManager.threads.find(t => t.id === threadInfo.threadId);
            if (thread && (thread.updated || thread.updated_at)) {
                const lastActive = this.getRelativeTime(thread.updated || thread.updated_at);
                tooltipLines.push(`<div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
                            <i class="fas fa-clock" style="color: #a78bfa;"></i>
                            <span>Updated ${lastActive}</span>
                        </div>`);
            }
        }

        // Links row
        let links = [];

        // Synergy link (clickable) - Enhanced with more info
        if (threadInfo?.synergyCardId) {
            const synergyName = threadInfo.synergySessionName || threadInfo.synergyCardId;
            const synergyDesc = threadInfo.synergyDescription || '';
            const synergyPriority = threadInfo.synergyPriority || '';

            // Build tooltip text with description and priority
            let tooltipText = `Click to open Synergy session: ${synergyName}`;
            if (synergyDesc) {
                tooltipText += `\n\n${synergyDesc.substring(0, 150)}${synergyDesc.length > 150 ? '...' : ''}`;
            }
            if (synergyPriority) {
                tooltipText += `\n\nPriority: ${synergyPriority}`;
            }

            links.push(`<div class="agent-tooltip-synergy-badge" data-synergy-id="${threadInfo.synergyCardId}" style="display: inline-flex; align-items: center; gap: 4px; padding: 6px 10px; background: #10b981; border-radius: 4px; font-size: 11px; cursor: pointer; transition: all 0.2s ease;" onmouseover="this.style.background='#059669'" onmouseout="this.style.background='#10b981'" title="${tooltipText.replace(/"/g, '&quot;')}">
                        <i class="fas fa-link"></i>
                        <span>${synergyName}</span>
                        ${synergyPriority ? `<span style="background: white; color: #10b981; padding: 2px 4px; border-radius: 3px; font-size: 10px; font-weight: 600; margin-left: 4px;">${synergyPriority.toUpperCase()}</span>` : ''}
                    </div>`);
            // Store synergy ID on badge for click handler
            badge.setAttribute('data-synergy-id', threadInfo.synergyCardId);
        }

        // Workflow link
        if (threadInfo?.workflowId) {
            links.push(`<div style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 8px; background: #3b82f6; border-radius: 4px; font-size: 11px;">
                        <i class="fas fa-project-diagram"></i>
                        <span>Workflow</span>
                    </div>`);
        }

        // Automation link
        if (threadInfo?.automationId) {
            links.push(`<div style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 8px; background: #8b5cf6; border-radius: 4px; font-size: 11px;">
                        <i class="fas fa-bolt"></i>
                        <span>Automation</span>
                    </div>`);
        }

        if (links.length > 0) {
            tooltipLines.push(`<div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.1);">
                        ${links.join('')}
                    </div>`);
        }

        // Set tooltip attributes
        badge.setAttribute('data-tooltip-title', tooltipTitle);
        badge.setAttribute('data-tooltip-content', tooltipLines.join(''));
    },

    // Get relative time string
    getRelativeTime(isoString) {
        const date = new Date(isoString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        return date.toLocaleDateString();
    },

    // Update badge state (highlight if has thread/messages)
    updateQuickNavBadge(agentId) {
        const badge = document.getElementById(`quick-nav-badge-${agentId}`);
        if (!badge) return;

        // Check if agent has loaded thread
        const threadInfo = this.loadedThreads[agentId];

        // Get previous message count (for change detection)
        const prevMessageCount = parseInt(badge.dataset.messageCount || '0');

        // Get actual message count from thread data
        let messageCount = 0;
        if (threadInfo?.threadId && typeof ThreadManager !== 'undefined' && Array.isArray(ThreadManager.threads)) {
            const thread = ThreadManager.threads.find(t => t.id === threadInfo.threadId);
            if (thread) {
                messageCount = thread.messages?.length || thread.message_count || 0;
            }
        }

        // Detect NEW message (count increased)
        const hasNewMessage = messageCount > prevMessageCount && prevMessageCount > 0;
        badge.dataset.messageCount = messageCount.toString();

        // Highlight badge if has thread or messages
        if (threadInfo || messageCount > 0) {
            badge.classList.add('has-thread');

            // Add pulse glow if new message (unless already viewed)
            if (hasNewMessage && !badge.dataset.viewed) {
                badge.classList.add('has-new-message');

                // Show toast notification
                const agentName = this.getAgentName(agentId);
                if (typeof showToast === 'function') {
                    showToast(`New message in ${agentName}`, 'info');
                }
            }

            // Update tooltip data
            this.addBadgeTooltipData(badge, agentId, threadInfo, messageCount);

            // Add/update thread indicator with actual count
            let indicator = badge.querySelector('.thread-indicator');
            if (!indicator) {
                indicator = document.createElement('span');
                indicator.className = 'thread-indicator';
                badge.appendChild(indicator);
            }
            indicator.textContent = messageCount.toString();
        } else {
            badge.classList.remove('has-thread');
            badge.classList.remove('has-new-message');
            delete badge.dataset.messageCount;
            delete badge.dataset.viewed;
            // Remove thread indicator and tooltip
            const indicator = badge.querySelector('.thread-indicator');
            if (indicator) {
                indicator.remove();
            }
            badge.removeAttribute('data-tooltip-title');
            badge.removeAttribute('data-tooltip-content');
        }

        this.updateDashboardStats();
    },            // Scroll to agent and expand if collapsed
    scrollToAgent(agentId, options = {}) {
        const column = document.getElementById(`agent-column-${agentId}`);
        if (!column) {
            console.warn(`[MultiAgent] Column agent-column-${agentId} not found`);
            return;
        }

        // Mark badge as viewed (remove pulse glow)
        const badge = document.getElementById(`quick-nav-badge-${agentId}`);
        if (badge) {
            badge.classList.remove('has-new-message');
            badge.classList.remove('message-complete');  // ✨ Remove green completion indicator
            badge.dataset.viewed = 'true';
            console.log(`[Agent ${agentId}] Badge viewed - removed completion indicator`);
        }

        // ✨ NEW: Set as currently viewing agent
        this.setCurrentlyViewing(agentId);

        // Expand if collapsed
        if (column.classList.contains('collapsed')) {
            this.expandColumn(agentId);
        }

        // Only scroll column into view if explicitly requested (user click, not auto-streaming)
        if (options.scrollColumn !== false) {
            column.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest',
                inline: 'center'
            });
        }

        // Highlight briefly
        column.style.transition = 'all 0.3s ease';
        column.style.boxShadow = '0 0 20px rgba(37, 123, 221, 0.6)';
        setTimeout(() => {
            column.style.boxShadow = '';
        }, 1000);

        // DON'T toggle 'active' class here - it conflicts with 'has-thread' state
        // The 'has-thread' class is managed by updateQuickNavBadge() based on actual thread data
        // Clicking a badge should just scroll, not change its highlight state

        console.log(`[Command Center] Scrolled to ${this.getAgentName(agentId)}`);
    },

    // Set currently viewing agent (tracks which agent current user is viewing)
    setCurrentlyViewing(agentId) {
        // Remove viewing from all badges
        document.querySelectorAll('.agent-quick-nav-badge').forEach(badge => {
            badge.classList.remove('viewing');
        });

        // Add viewing to current agent
        const badge = document.getElementById(`quick-nav-badge-${agentId}`);
        if (badge) {
            badge.classList.add('viewing');
            console.log(`[Agent ${agentId}] 👁️ Marked as currently viewing`);
        }

        // Broadcast to other users via existing WebSocket presence system
        if (window.SynergyRealtime && typeof SynergyRealtime.updateAgentViewingScope === 'function') {
            SynergyRealtime.updateAgentViewingScope(agentId);
        }
    },

    // Update badge to show OTHER sessions viewing this agent (can be same user on different device)
    updateBadgeForOtherSessions(agentId, sessions) {
        const column = document.getElementById(`agent-column-${agentId}`);
        const badge = document.getElementById(`quick-nav-badge-${agentId}`);
        if (!badge && !column) return;

        if (!sessions || sessions.length === 0) {
            // No other sessions viewing - remove indicator
            if (badge) {
                badge.classList.remove('other-user');
                badge.removeAttribute('data-user-initials');
                badge.removeAttribute('data-session-devices');
                badge.removeAttribute('title');
            }

            if (column) {
                column.classList.remove('other-session-viewing');
                column.style.border = '';
                column.style.boxShadow = '';
            }
            console.log(`[Agent ${agentId}] 👥 No other sessions viewing`);
            return;
        }

        // Get rainbow color for this session
        const sessionColor = this.getSessionColor(sessions[0].session_token);

        if (column) {
            column.classList.add('other-session-viewing');
            // Dashed border with device-specific color
            column.style.border = `3px dashed ${sessionColor}`;
            column.style.boxShadow = `0 0 0 4px ${sessionColor}33`; // 20% opacity for outer glow
            // Set CSS variable for potential CSS usage
            column.style.setProperty('--session-color', sessionColor);
        }

        // Show indicator for multiple sessions
        if (badge) {
            badge.classList.add('other-user');
            // Apply same session color to quick nav badge
            badge.style.setProperty('--session-color', sessionColor);
        }

        // Build display text (no emojis)
        if (sessions.length === 1) {
            const session = sessions[0];
            const displayName = session.display_name || session.user_name;

            if (session.isYourOtherSession) {
                // Your other device/session - show device label
                const deviceLabel = this.getDeviceLabel(session.device);
                if (badge) {
                    badge.setAttribute('data-user-initials', deviceLabel);
                    badge.setAttribute('title', `${displayName} viewing on ${session.device}`);
                }
            } else {
                // Different person (same account) - show their display name initials
                const initials = this.getInitials(displayName);
                if (badge) {
                    badge.setAttribute('data-user-initials', initials);
                    badge.setAttribute('title', `${displayName} viewing on ${session.device}`);
                }
            }
        } else {
            // Multiple sessions - show count
            if (badge) badge.setAttribute('data-user-initials', `${sessions.length}`);
            const deviceList = sessions.map(s => {
                const displayName = s.display_name || s.user_name;
                if (s.isYourOtherSession) {
                    return `${displayName} (${s.device})`;
                } else {
                    return `${displayName} (${s.device})`;
                }
            }).join('\n');
            if (badge) badge.setAttribute('title', `${sessions.length} people viewing:\n${deviceList}`);
        }

        // Store session info for hover tooltip
        if (badge) badge.setAttribute('data-session-devices', JSON.stringify(sessions.map(s => s.device)));

        console.log(`[Agent ${agentId}] 👥 ${sessions.length} session(s) viewing:`, sessions);
    },

    // Get device label from device string (no emojis)
    getDeviceLabel(deviceStr) {
        if (!deviceStr) return 'PC';
        if (deviceStr.includes('iPhone')) return 'iPhone';
        if (deviceStr.includes('Android')) return 'Phone';
        if (deviceStr.includes('Mac')) return 'Mac';
        if (deviceStr.includes('Windows')) return 'Win';
        if (deviceStr.includes('Linux')) return 'Linux';
        if (deviceStr.includes('Desktop')) return 'PC';
        if (deviceStr.includes('Phone') || deviceStr.includes('Mobile')) return 'Mobile';
        return 'PC';
    },

    // Get color for session based on hash of session token
    // Static map to persist session colors across all calls
    sessionColorMap: new Map(),

    getSessionColor(sessionToken) {
        if (!sessionToken) return this.PRESENCE_COLORS[0];

        // Check if we already assigned a color to this session
        if (this.sessionColorMap.has(sessionToken)) {
            return this.sessionColorMap.get(sessionToken);
        }

        // Assign new color based on hash
        const hash = sessionToken.split('').reduce((acc, char) =>
            acc + char.charCodeAt(0), 0);
        const color = this.PRESENCE_COLORS[hash % this.PRESENCE_COLORS.length];

        // Store for future lookups
        this.sessionColorMap.set(sessionToken, color);
        return color;
    },

    // Show lock banner when agent is locked by another session
    showLockBanner(agentId, lockedByDisplayName) {
        const column = document.getElementById(`agent-column-${agentId}`);
        if (!column) return;

        // Add locked state
        column.classList.add('locked-by-other');

        // Create lock banner if it doesn't exist
        let banner = column.querySelector('.agent-lock-banner');
        if (!banner) {
            banner = document.createElement('div');
            banner.className = 'agent-lock-banner';
            banner.innerHTML = `<i class="fas fa-lock"></i> Locked by ${lockedByDisplayName || 'another user'}`;
            column.appendChild(banner);
        } else {
            banner.innerHTML = `<i class="fas fa-lock"></i> Locked by ${lockedByDisplayName || 'another user'}`;
            banner.style.display = 'flex';
        }

        console.log(`🔒 [Agent ${agentId}] Locked by ${lockedByDisplayName}`);
    },

    // Hide lock banner when agent is unlocked
    hideLockBanner(agentId) {
        const column = document.getElementById(`agent-column-${agentId}`);
        if (!column) return;

        // Remove locked state
        column.classList.remove('locked-by-other');

        // Hide banner
        const banner = column.querySelector('.agent-lock-banner');
        if (banner) {
            banner.style.display = 'none';
        }

        console.log(`🔓 [Agent ${agentId}] Unlocked`);
    },

    // Disable agent input when locked by another session
    disableAgentInput(agentId) {
        // Try multiple possible input IDs
        const input = document.getElementById(`agent-input-${agentId}`) ||
            document.getElementById(`input-${agentId}`);

        if (input) {
            input.disabled = true;
            input.placeholder = 'This agent is locked by another user...';
            console.log(`⛔ [Agent ${agentId}] Input disabled`);
        }
    },

    // Enable agent input when unlocked
    enableAgentInput(agentId) {
        // Try multiple possible input IDs
        const input = document.getElementById(`agent-input-${agentId}`) ||
            document.getElementById(`input-${agentId}`);

        if (input) {
            input.disabled = false;
            input.placeholder = 'Message AI Agent...';
            console.log(`✅ [Agent ${agentId}] Input enabled`);
        }
    },

    // Legacy method - kept for backwards compatibility but redirects to new method
    updateBadgeForOtherUser(agentId, userName, sessionToken, action = 'add') {
        // This is now handled by updateBadgeForOtherSessions
        // Kept for backwards compatibility
        console.warn('[DEPRECATED] updateBadgeForOtherUser - use updateBadgeForOtherSessions instead');
    },

    // Get initials from user name
    getInitials(name) {
        if (!name) return '??';
        const parts = name.trim().split(/\s+/);
        if (parts.length === 1) {
            return parts[0].substring(0, 2).toUpperCase();
        }
        return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    },

    // Update dashboard stats
    updateDashboardStats() {
        const agentCount = document.querySelectorAll('.agent-column').length;
        const activeThreads = Object.keys(this.loadedThreads).length;

        const agentCountEl = document.getElementById('active-agents-count');
        const threadCountEl = document.getElementById('active-threads-count');

        if (agentCountEl) agentCountEl.textContent = agentCount;
        if (threadCountEl) threadCountEl.textContent = activeThreads;
    },

    // Refresh all agents - reload threads and messages
    async refreshAllAgents() {
        console.log('[Command Center] 🔄 Refreshing all agents - reloading threads and messages...');

        const agentIds = Object.keys(this.loadedThreads);

        if (agentIds.length === 0) {
            console.log('[Command Center] No agents with loaded threads to refresh');
            if (typeof showNotification === 'function') {
                showNotification('No active agents to refresh', 'info', 2000);
            }
            return;
        }

        // Get refresh button and add spinning animation
        const refreshBtn = document.querySelector('button[onclick*="refreshAllAgents"]');
        const refreshIcon = refreshBtn?.querySelector('i');
        if (refreshIcon) {
            refreshIcon.classList.add('fa-spin');
        }

        // Track scroll positions before refresh
        const scrollPositions = {};
        agentIds.forEach(agentIdStr => {
            const agentId = parseInt(agentIdStr);
            const messagesContainer = document.querySelector(`#agent-column-${agentId} .agent-messages-container`);
            if (messagesContainer) {
                scrollPositions[agentId] = messagesContainer.scrollTop;
                console.log(`[Refresh] Saved scroll position for agent ${agentId}: ${scrollPositions[agentId]}px`);
            }
        });

        let successCount = 0;
        let errorCount = 0;
        const totalCount = agentIds.length;

        try {
            // Reload each agent's thread and messages
            for (let i = 0; i < agentIds.length; i++) {
                const agentIdStr = agentIds[i];
                const currentIndex = i + 1;

                // Update progress indicator
                if (typeof showNotification === 'function') {
                    showNotification(`Refreshing agent ${currentIndex}/${totalCount}...`, 'info', 1000);
                }

                const agentId = parseInt(agentIdStr);
                const threadInfo = this.loadedThreads[agentId];

                if (!threadInfo || !threadInfo.threadId) {
                    console.warn(`[Command Center] Agent ${agentId} has no thread loaded, skipping`);
                    errorCount++;
                    continue;
                }

                console.log(`[Command Center] 🔄 Refreshing agent ${agentId} - thread ${threadInfo.threadId}`);

                try {
                    // Get the thread data
                    const thread = {
                        id: threadInfo.threadId,
                        title: threadInfo.threadTitle,
                        message_count: threadInfo.messageCount || 0,
                        location: `agent-${agentId}`
                    };

                    // Clear MessageStore for this thread to force fresh load
                    if (typeof window.MessageStore !== 'undefined') {
                        const oldCount = window.MessageStore.getMessageCount(thread.id);
                        window.MessageStore.clearThread(thread.id);
                        console.log(`[Command Center] ✅ Cleared ${oldCount} messages from MessageStore for thread ${thread.id}`);
                    }

                    // Clear the agent's messages container
                    const messagesContainer = document.querySelector(`#agent-column-${agentId} .agent-messages-container`);
                    if (messagesContainer) {
                        const messages = messagesContainer.querySelectorAll('.message-bubble, .ai-message');
                        console.log(`[Command Center] 🗑️ Clearing ${messages.length} old messages from DOM for agent ${agentId}`);
                        messages.forEach(msg => msg.remove());

                        // Show loading indicator
                        const processingIndicator = createProcessingIndicator(agentId);
                        messagesContainer.appendChild(processingIndicator);
                    }

                    // Reload messages from backend
                    if (typeof ThreadManager !== 'undefined' && ThreadManager.loadMessagesForThread) {
                        console.log(`[Command Center] 📥 Fetching fresh messages for thread ${thread.id}...`);

                        const result = await ThreadManager.loadMessagesForThread(thread.id, null, 0);

                        if (result?.error === 'THREAD_NOT_FOUND') {
                            console.warn(`[Command Center] ⚠️ Thread ${thread.id} not found - removing from agent ${agentId}`);
                            removeProcessingIndicator(agentId);
                            continue;
                        }

                        // Get freshly loaded messages from MessageStore
                        const loadedMessages = window.MessageStore.getMessages(thread.id);

                        if (loadedMessages && loadedMessages.length > 0) {
                            console.log(`[Command Center] ✅ Rendering ${loadedMessages.length} messages for agent ${agentId}...`);

                            // Remove processing indicator
                            removeProcessingIndicator(agentId);

                            // Render each message using UnifiedMessageRenderer
                            for (const [index, msg] of loadedMessages.entries()) {
                                if (typeof UnifiedMessageRenderer !== 'undefined') {
                                    await UnifiedMessageRenderer.render(
                                        messagesContainer,
                                        msg.role,
                                        msg.content,
                                        {
                                            threadId: thread.id,
                                            syncToBackend: false,
                                            scrollToBottom: false,
                                            createdAt: msg.created_at,
                                            checkDuplicates: false,
                                            messageId: msg.id
                                        }
                                    );
                                }
                            }

                            // Restore scroll position after messages rendered
                            if (messagesContainer && scrollPositions[agentId] !== undefined) {
                                setTimeout(() => {
                                    messagesContainer.scrollTop = scrollPositions[agentId];
                                    console.log(`[Refresh] ✅ Restored scroll position for agent ${agentId}: ${scrollPositions[agentId]}px`);
                                }, 150);
                            }

                            console.log(`[Command Center] ✅ Agent ${agentId} refreshed successfully`);
                            successCount++;
                        } else {
                            removeProcessingIndicator(agentId);
                            console.log(`[Command Center] No messages to render for agent ${agentId}`);
                            successCount++;
                        }
                    }

                    // Update agent header with fresh data
                    this.updateAgentHeader(agentId);

                } catch (error) {
                    console.error(`[Command Center] Error refreshing agent ${agentId}:`, error);
                    removeProcessingIndicator(agentId);
                    errorCount++;
                    // Continue with next agent (don't stop entire refresh)
                }
            }

            // Update dashboard stats
            this.updateDashboardStats();

            // Remove spinning animation
            if (refreshIcon) {
                refreshIcon.classList.remove('fa-spin');
            }

            // Success notification with count
            if (typeof showNotification === 'function') {
                if (errorCount === 0) {
                    showNotification(`✅ Refreshed ${successCount}/${totalCount} agents`, 'success', 3000);
                } else {
                    showNotification(`⚠️ Refreshed ${successCount}/${totalCount} agents (${errorCount} failed)`, 'warning', 4000);
                }
            }

            console.log(`[Command Center] ✅ Refresh complete: ${successCount} success, ${errorCount} failed`);

        } catch (error) {
            console.error('[Command Center] Error during refresh:', error);
            // Remove spinning animation on error
            if (refreshIcon) {
                refreshIcon.classList.remove('fa-spin');
            }
            if (typeof showNotification === 'function') {
                showNotification('Error refreshing agents', 'error', 3000);
            }
        }
    },

    // Toggle visibility of empty agent columns
    toggleEmptyAgents() {
        const btn = document.getElementById('toggle-empty-agents-btn');
        const icon = btn?.querySelector('i');

        // Get current state from button or default to false (all expanded initially)
        const currentlyCollapsed = btn?.dataset.collapseEmpty === 'true';
        const newState = !currentlyCollapsed;

        // Update button state
        if (btn) btn.dataset.collapseEmpty = newState.toString();

        // Find all agent columns
        const allColumns = document.querySelectorAll('.agent-column');
        let collapsedCount = 0;

        allColumns.forEach(column => {
            const agentId = parseInt(column.id.replace('agent-column-', ''));
            const hasThread = this.loadedThreads[agentId]?.threadId;

            if (!hasThread && newState) {
                // Collapse empty agents (using AgentColumn.collapse function)
                if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.collapse === 'function') {
                    AgentColumn.collapse(agentId);
                    collapsedCount++;
                } else {
                    // Fallback: add collapsed class manually
                    column.classList.add('collapsed');
                    collapsedCount++;
                }
            } else if (!hasThread && !newState) {
                // Expand empty agents (using AgentColumn.expand function)
                if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.expand === 'function') {
                    AgentColumn.expand(agentId);
                } else {
                    // Fallback: remove collapsed class manually
                    column.classList.remove('collapsed');
                }
            }
        });

        // Update button icon and tooltip (FIXED: swapped icons)
        if (icon && btn) {
            if (newState) {
                // Empty agents ARE collapsed, show expand icon
                icon.className = 'fas fa-expand';
                btn.title = 'Expand empty agents';
            } else {
                // Empty agents ARE expanded, show collapse icon
                icon.className = 'fas fa-compress';
                btn.title = 'Collapse empty agents';
            }
        }

        console.log(`[Command Center] ${newState ? 'Collapsing' : 'Expanding'} empty agents (${collapsedCount} affected)`);

        if (typeof showNotification === 'function') {
            if (newState) {
                showNotification(`${collapsedCount} empty agents collapsed`, 'info');
            } else {
                showNotification('All agents expanded', 'info');
            }
        }
    },

    // Unload thread to Prime (removes from agent, unassigns from database)
    async unloadToPrime(agentId) {
        const threadInfo = this.loadedThreads[agentId];
        if (!threadInfo || !threadInfo.threadId) {
            console.warn(`[MultiAgent] No thread loaded in ${this.getAgentName(agentId)}`);
            return;
        }

        const threadId = threadInfo.threadId;
        const threadTitle = threadInfo.threadTitle;

        console.log(`[UNLOAD] Unloading thread "${threadTitle}" from ${this.getAgentName(agentId)} to Prime`);

        // 1. Clear messages from agent column
        const messagesContainer = document.querySelector(`#agent-column-${agentId} .agent-messages-container`);
        if (messagesContainer) {
            // Clean up processors
            messagesContainer.querySelectorAll('[data-processor-initialized]').forEach(bubble => {
                if (bubble.processor && typeof bubble.processor.cleanup === 'function') {
                    bubble.processor.cleanup();
                }
            });
            // Remove only messages, preserve scroll controls
            const messages = messagesContainer.querySelectorAll('.ai-message');
            messages.forEach(msg => msg.remove());
        }

        // 2. Unassign thread from database (removes agent assignment)
        if (typeof ThreadManager !== 'undefined') {
            await ThreadManager.unassignThread(threadId);
            console.log(`[OK] Thread ${threadId} unassigned from database`);
        }

        // 3. Remove from MultiAgent state
        delete this.loadedThreads[agentId];
        delete this.sessions[agentId];

        // 4. Update agent header AND badge to show empty state
        this.updateAgentHeader(agentId);
        this.updateQuickNavBadge(agentId);  // ✨ Update badge to remove 'has-thread' class

        // 5. Save state
        this.saveState();

        // 6. Refresh thread list to update badges
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.renderThreadList === 'function') {
            ThreadManager.renderThreadList();
        }

        // 7. Show notification
        if (typeof showNotification === 'function') {
            showNotification(`Thread "${threadTitle}" unloaded to Prime`, 'success');
        }

        console.log(`[OK] Thread unloaded successfully - agent ${agentId} now empty`);
    },

    // Move thread from column to Prime panel
    async moveToPrime(agentId) {
        const threadInfo = this.loadedThreads[agentId];
        if (!threadInfo || !threadInfo.threadId) {
            console.warn(`[MultiAgent] No thread loaded in ${this.getAgentName(agentId)}`);
            return;
        }

        // Get full thread from ThreadManager
        if (typeof ThreadManager === 'undefined') {
            console.error('[MultiAgent] ThreadManager not available');
            return;
        }

        const thread = Array.isArray(ThreadManager.threads) ? ThreadManager.threads.find(t => t.id === threadInfo.threadId) : null;
        if (!thread) {
            console.error(`[MultiAgent] Thread ${threadInfo.threadId} not found in ThreadManager`);
            return;
        }

        console.log(`[MultiAgent] Moving thread "${threadInfo.threadTitle}" from ${this.getAgentName(agentId)} to Prime`);

        // Check if Prime already has this thread
        if (AppState.sessionId === threadInfo.threadId) {
            alert(`This thread is already active in Prime panel.`);
            return;
        }

        // Confirm if Prime has a different active session
        if (AppState.sessionId && AppState.sessionId !== threadInfo.threadId) {
            if (!confirm('Replace Prime Session?\n\nPrime panel has an active session. Moving this thread will replace the current Prime session. Continue?')) {
                return;
            }
            this.executeThreadMove(agentId, threadInfo);
            return;
        }

        // Clear Prime messages
        const primeMessages = document.getElementById('ai-chat-messages');
        if (primeMessages) {
            // Clean up any existing processors
            primeMessages.querySelectorAll('[data-processor-initialized]').forEach(bubble => {
                if (bubble.processor && typeof bubble.processor.cleanup === 'function') {
                    bubble.processor.cleanup();
                }
            });
            primeMessages.innerHTML = '';
        }

        // Load thread messages from MessageStore (centralized storage)
        const storedMessages = window.MessageStore.getMessages(thread.id);
        console.log(`📦 [MessageStore] Retrieved ${storedMessages.length} messages for Prime AI`);

        if (storedMessages && storedMessages.length > 0) {
            storedMessages.forEach((msg, index) => {
                // CRITICAL FIX: Check content structure FIRST (not role)
                const isStructuredContent = Array.isArray(msg.content) &&
                    msg.content.length > 0 &&
                    msg.content[0]?.type &&
                    ['thinking', 'tool_use', 'tool_result', 'text'].includes(msg.content[0].type);

                if (isStructuredContent) {
                    // Structured content (thinking, tool_use, tool_result) - use structured rendering
                    console.log(`[RENDER PRIME] Structured content detected: ${msg.content.map(b => b.type).join(', ')}`);

                    // Use TwoRuleStreamProcessor for structured content in Prime
                    msg.content.forEach(block => {
                        if (block.type === 'thinking' || block.type === 'tool_use' || block.type === 'tool_result') {
                            // Create bubble for each structured block
                            const messageDiv = document.createElement('div');
                            messageDiv.className = `ai-message assistant ${block.type === 'thinking' ? 'thinking-bubble' : 'tool-bubble'} collapsed`;

                            messageDiv.innerHTML = `
                                <div class="ai-message-header">
                                    <div class="ai-message-avatar">
                                        <i class="fa-solid ${block.type === 'thinking' ? 'fa-atom' : 'fa-cog'}"></i>
                                    </div>
                                    <button class="ai-message-toggle">
                                        <i class="fas fa-chevron-down"></i>
                                    </button>
                                </div>
                                <div class="ai-message-content"></div>
                            `;
                            primeMessages.appendChild(messageDiv);

                            const bubble = messageDiv.querySelector('.ai-message-content');
                            const content = block.content || JSON.stringify(block.input || block);

                            if (typeof TwoRuleStreamProcessor !== 'undefined') {
                                const processor = new TwoRuleStreamProcessor(bubble);
                                processor.processChunk(content);
                            } else {
                                bubble.textContent = content;
                            }
                        } else if (block.type === 'text') {
                            // Regular text block - render normally
                            if (typeof addChatMessage === 'function') {
                                addChatMessage('assistant', block.text);
                            }
                        }
                    });

                } else if (msg.role === 'user') {
                    // User messages render normally
                    if (typeof addChatMessage === 'function') {
                        const content = typeof msg.content === 'string' ? msg.content :
                            (Array.isArray(msg.content) ? msg.content.map(b => b.text || '').join('\n') :
                                JSON.stringify(msg.content));
                        addChatMessage('user', content);
                    }

                } else if (msg.role === 'assistant') {
                    // AI messages need processor rendering
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'ai-message assistant';
                    messageDiv.innerHTML = `
                                <div class="ai-message-header">
                                    <div class="ai-message-avatar">
                                        <i class="fa-solid fa-atom"></i>
                                    </div>
                                    <button class="ai-message-toggle">
                                        <i class="fas fa-chevron-down"></i>
                                    </button>
                                </div>
                                <div class="ai-message-content">
                                    <div class="typing-indicator" style="display: none;">
                                        <span></span><span></span><span></span>
                                    </div>
                                </div>
                            `;
                    primeMessages.appendChild(messageDiv);

                    const bubble = messageDiv.querySelector('.ai-message-content');

                    // Extract text content from various formats (same as addChatMessage)
                    let contentStr = '';
                    const content = msg.content;

                    if (typeof content === 'string') {
                        contentStr = content;
                    } else if (Array.isArray(content)) {
                        // Array of content blocks (Claude API format)
                        contentStr = content
                            .filter(block => block.type === 'text')
                            .map(block => block.text)
                            .join('\n\n');
                    } else if (content && typeof content === 'object') {
                        // Single content block object
                        if (content.type === 'text' && content.text) {
                            contentStr = content.text;
                        } else if (content.content) {
                            contentStr = typeof content.content === 'string'
                                ? content.content
                                : JSON.stringify(content);
                        } else {
                            contentStr = JSON.stringify(content);
                        }
                    }

                    // Render with TwoRuleStreamProcessor (same as addChatMessage)
                    if (!window.USE_BASIC_RENDERER && typeof TwoRuleStreamProcessor !== 'undefined' && contentStr) {
                        try {
                            const processor = new TwoRuleStreamProcessor(bubble);
                            processor.processChunk(contentStr);
                            // TwoRuleStreamProcessor auto-renders, no finalize needed
                            console.log(`[OK] Prime message ${index + 1} rendered with TwoRuleStreamProcessor`);
                        } catch (error) {
                            console.error(`[ERROR] Processor failed, fallback to markdown:`, error);
                            bubble.innerHTML = renderBasicMarkdown(contentStr);
                        }
                    } else {
                        // Fallback to basic markdown
                        bubble.innerHTML = renderBasicMarkdown(contentStr);
                    }
                }
            });
            console.log(`[OK] Loaded ${storedMessages.length} messages into Prime with TwoRule rendering`);
        }

        // Update Prime session (Note: AppState.chatMessages deprecated - use MessageStore)
        AppState.sessionId = threadInfo.threadId;

        // DO NOT switch to Prime tab - stay on multi-agent
        // User can see the thread in Prime by clicking the AI Chat tab themselves
        // This prevents the multi-agent panel from disappearing

        // Clear thread from column (both header AND messages)
        this.clearLoadedThread(agentId);

        // Clear session ID from column
        delete this.sessions[agentId];
        this.saveState();

        // Update centralized assignment tracker - thread now in Prime
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.assignThread === 'function') {
            // First, assign to prime (this updates database and enables page reload restoration)
            await ThreadManager.assignThread(threadInfo.threadId, 'prime');
            console.log(`[MultiAgent] [OK] Thread ${threadInfo.threadId} assigned to 'prime' in centralized tracker`);

            // Then check if agent has any other assigned threads, if not show "Start New Chat"
            if (typeof ThreadManager.checkAndShowEmptyState === 'function') {
                await ThreadManager.checkAndShowEmptyState(agentId);
            }
        }

        // Scroll Prime to bottom
        if (primeMessages) {
            primeMessages.scrollTop = primeMessages.scrollHeight;
        }

        // Show success message
        setTimeout(() => {
            alert(`[OK] Thread "${threadInfo.threadTitle}" moved to Prime panel!\n\nClick the "AI Chat" tab to view it.`);
        }, 100);

        console.log(`[MultiAgent] [OK] Thread successfully moved to Prime and column cleared`);
    },

    // Execute thread move after confirmation
    executeThreadMove(agentId, threadInfo) {
        const thread = this.loadedThreads[agentId];
        if (!thread) {
            console.error(`[MultiAgent] No thread loaded in agent ${agentId}`);
            return;
        }

        // Clear Prime messages
        const primeMessages = document.getElementById('ai-chat-messages');
        if (primeMessages) {
            primeMessages.querySelectorAll('[data-processor-initialized]').forEach(bubble => {
                if (bubble.processor && typeof bubble.processor.cleanup === 'function') {
                    bubble.processor.cleanup();
                }
            });
            primeMessages.innerHTML = '';
        }

        // Load thread messages
        if (thread.messages && thread.messages.length > 0) {
            thread.messages.forEach((msg) => {
                if (msg.role === 'user' && typeof addChatMessage === 'function') {
                    addChatMessage('user', msg.content);
                }
            });
        }

        // Update Prime session
        AppState.sessionId = threadInfo.threadId;
        AppState.messages = thread.messages || [];

        // Clear agent column
        this.loadedThreads[agentId] = null;
        this.updateAgentHeader(agentId);
        const messagesEl = document.getElementById(`agent-${agentId}-messages`);
        if (messagesEl) messagesEl.innerHTML = '';

        // Auto-scroll
        if (primeMessages) {
            primeMessages.scrollTop = primeMessages.scrollHeight;
        }

        // Success notification
        setTimeout(() => {
            UIComponents.showAlert({
                title: 'Thread Moved',
                message: `Thread "${threadInfo.threadTitle}" moved to Prime panel successfully!\n\nClick the "AI Chat" tab to view it.`,
                variant: 'success'
            });
        }, 100);

        console.log(`[MultiAgent] [OK] Thread successfully moved to Prime`);
    },

    // Update agent header to show loaded thread with unified thread-info card
    updateAgentHeader(agentId) {
        const threadInfo = this.loadedThreads[agentId];
        const headerEl = document.querySelector(`#thread-info-${agentId}`);

        console.log(`[updateAgentHeader] Agent ${agentId}:`, {
            hasThreadInfo: !!threadInfo,
            hasHeaderEl: !!headerEl,
            threadId: threadInfo?.threadId
        });

        // Early exit if header element doesn't exist yet (timing issue during initialization)
        if (!headerEl) {
            console.warn(`[updateAgentHeader] Header element not found for thread-info-${agentId}, skipping update`);
            return;
        }

        // Also update collapsed bar status
        this.updateCollapsedStatus(agentId);

        if (threadInfo && typeof ThreadManager !== 'undefined') {
            // Use ThreadManager.renderThreadInfoContainer() - returns full 7-row structure
            console.log(`[updateAgentHeader] Rendering thread card for agent-${agentId} with thread ${threadInfo.threadId}`);
            const html = ThreadManager.renderThreadInfoContainer(
                `agent-${agentId}`,
                threadInfo.threadId,
                true  // compact mode (for agent columns)
            );

            if (html) {
                headerEl.innerHTML = html;
                console.log(`[updateAgentHeader] Thread card rendered for thread-info-${agentId}`);

                // CRITICAL: Show agent input container when thread is loaded (expandable Prime-style)
                const agentInputContainer = document.querySelector(`#agent-column-${agentId} .agent-input-container`);
                if (agentInputContainer) {
                    agentInputContainer.style.display = 'block';
                    console.log(`[updateAgentHeader] Showed input container for agent-${agentId} (thread loaded)`);

                    // Initialize input handlers if not already done
                    if (typeof AgentInput !== 'undefined' && typeof AgentInput.setupHandlers === 'function') {
                        AgentInput.setupHandlers(agentId);
                    }
                }

                // CRITICAL: Show resize handle when thread is loaded
                const resizeHandle = document.querySelector(`.agent-resize-handle[data-agent-id="${agentId}"]`);
                if (resizeHandle) {
                    resizeHandle.style.display = 'block';
                    console.log(`[updateAgentHeader] Showed resize handle for agent-${agentId} (thread loaded)`);
                }
            } else {
                console.warn(`[updateAgentHeader] Empty HTML returned for thread ${threadInfo.threadId}`);
                headerEl.innerHTML = ThreadManager.renderEmptyThreadInfo(`agent-${agentId}`);
            }
        } else {
            // No thread loaded - show empty state using ThreadManager
            console.log(`[updateAgentHeader] No thread info, showing empty state`);
            if (typeof ThreadManager !== 'undefined' && ThreadManager.renderEmptyThreadInfo) {
                headerEl.innerHTML = ThreadManager.renderEmptyThreadInfo(`agent-${agentId}`);
            } else {
                // Fallback if ThreadManager not available
                headerEl.innerHTML = `
                    <div class="no-thread-message" style="padding: 20px; text-align: center; color: #666;">
                        <i class="fas fa-inbox" style="font-size: 48px; margin-bottom: 12px; opacity: 0.5;"></i>
                        <div style="font-size: 16px; font-weight: 500;">No thread loaded</div>
                    </div>
                `;
            }

            // CRITICAL: Hide agent input container when no thread loaded
            const agentInputContainer = document.querySelector(`#agent-column-${agentId} .agent-input-container`);
            if (agentInputContainer) {
                agentInputContainer.style.display = 'none';
                console.log(`[updateAgentHeader] Hid input container for agent-${agentId} (no thread)`);

                // Cleanup input handlers
                if (typeof AgentInput !== 'undefined' && typeof AgentInput.cleanupHandlers === 'function') {
                    AgentInput.cleanupHandlers(agentId);
                }
            }

            // CRITICAL: Hide resize handle when no thread loaded
            const resizeHandle = document.querySelector(`.agent-resize-handle[data-agent-id="${agentId}"]`);
            if (resizeHandle) {
                resizeHandle.style.display = 'none';
                console.log(`[updateAgentHeader] Hid resize handle for agent-${agentId} (no thread)`);
            }

            // Also clear messages container when no thread loaded
            const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
            if (messagesContainer) {
                messagesContainer.innerHTML = `
                    <div class="empty-state" style="padding-top: 60%; text-align: center;">
                        <div style="line-height: 1.8; padding: 0 20px; max-width: 500px; margin: 0 auto;">
                            <div style="font-size: 2em; margin-bottom: 15px;">
                                
                            </div>
                            <div style="font-size: 1.2em; margin-bottom: 12px; font-weight: 600; color: var(--text-primary, #e5e7eb);">
                                ${this.getAgentName(agentId)} Ready
                            </div>
                            <div style="margin-bottom: 20px; opacity: 0.8; font-size: 0.95em; color: var(--text-secondary, #9ca3af);">
                                No active thread — start a new chat or load from history
                            </div>
                            <div style="background: rgba(255, 255, 255, 0.05); padding: 14px; border-radius: 8px; border-left: 3px solid var(--accent-primary, #58a6ff); margin-bottom: 20px; text-align: left;">
                                <div style="font-weight: 600; margin-bottom: 8px; font-size: 0.9em; color: var(--text-primary, #e5e7eb);"> Quick Tip</div>
                                <div style="opacity: 0.85; font-size: 0.85em; line-height: 1.6; color: var(--text-secondary, #9ca3af);">
                                    <strong>Drag &amp; drop threads</strong> from the sidebar to move conversations between agents. 
                                    All formatting, context, and history stays intact!
                                </div>
                            </div>
                            <div style="display: flex; gap: 12px; margin-top: 24px; justify-content: center;">
                                <button class="btn btn-primary" onclick="event.stopPropagation(); ThreadManager.showNewChatModal('agent-${agentId}')" style="display: flex; align-items: center; gap: 8px; font-size: 14px;">
                                    <i class="fas fa-plus" style="font-size: 12px;"></i>
                                    Start New Chat
                                </button>
                                <button class="btn btn-secondary" onclick="event.stopPropagation(); ThreadManager.toggleThreadMenu()" style="display: flex; align-items: center; gap: 8px; font-size: 14px;">
                                    <i class="fas fa-history" style="font-size: 12px;"></i>
                                    Threads Catalogue
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                console.log(`[updateAgentHeader] Cleared messages for agent-${agentId}`);
            }
        }
    },

    // Save multi-agent state to localStorage [DISABLED - Backend is source of truth]
    saveState() {
        // DO NOT save to localStorage - backend database is authoritative source
        // All agent/thread assignments are stored in database via ThreadManager
        console.log('⚠️ [Multi-Agent] localStorage saving disabled - backend is source of truth');
        return;

        /* OLD CODE - DISABLED:
        try {
            const state = {
                nextAgentId: this.nextAgentId,
                loadedThreads: this.loadedThreads,
                sessions: this.sessions
            };
            localStorage.setItem('multi_agent_state', JSON.stringify(state));
            console.log('💾 Multi-agent state saved');
        } catch (error) {
            console.error('❌ Failed to save multi-agent state:', error);
        }
        */
    },

    // Load multi-agent state from localStorage [DISABLED - Backend is source of truth]
    loadState() {
        // DO NOT load from localStorage - backend database is authoritative source
        // Agent count and assignments are calculated from actual backend thread assignments
        console.log('⚠️ [Multi-Agent] localStorage loading disabled - using backend only');

        // Clear any stale localStorage data
        try {
            localStorage.removeItem('multi_agent_state');
            console.log('🗑️ [Multi-Agent] Cleared stale localStorage');
        } catch (error) {
            console.error('❌ Failed to clear localStorage:', error);
        }

        return;

        /* OLD CODE - DISABLED:
        try {
            const saved = localStorage.getItem('multi_agent_state');
            if (saved) {
                const state = JSON.parse(saved);
                this.nextAgentId = state.nextAgentId || 4;
                this.loadedThreads = state.loadedThreads || {};
                this.sessions = state.sessions || {};
                console.log('[DATA] Multi-agent state loaded');
            }
        } catch (error) {
            console.error('❌ Failed to load multi-agent state:', error);
        }
        */
    },

    // Load thread into agent
    async loadThreadIntoAgent(agentId, thread) {
        // SAFETY CHECK: Ensure UnifiedMessageRenderer is loaded before proceeding
        if (typeof UnifiedMessageRenderer === 'undefined') {
            console.error('[loadThreadIntoAgent] UnifiedMessageRenderer not loaded yet - deferring load');
            setTimeout(() => this.loadThreadIntoAgent(agentId, thread), 100);
            return;
        }

        // GUARD: Prevent concurrent loads of same thread in same agent
        if (!window.ThreadManager._loadingThreads) {
            window.ThreadManager._loadingThreads = new Map();
        }

        const loadState = window.ThreadManager._loadingThreads.get(thread.id) || { prime: false, agents: new Set() };
        if (loadState.agents.has(agentId)) {
            console.warn(`⚠️ [LOAD] Thread ${thread.id} already loading in agent-${agentId}, skipping duplicate load`);
            return;
        }

        loadState.agents.add(agentId);
        window.ThreadManager._loadingThreads.set(thread.id, loadState);

        try {
            console.log(`[LOAD] Loading thread "${thread.title}" into agent ${agentId} `);

            // CRITICAL: Check if thread is already loaded elsewhere (Prime or another Agent)
            const currentLocation = this.getThreadCurrentLocation(thread.id);
            if (currentLocation) {
                console.warn(`[LOAD] Thread ${thread.id} is already loaded in ${currentLocation}`);

                // Unload from current location first
                if (currentLocation === 'prime') {
                    console.log(`[ISOLATION]  Clearing Prime - thread moving to agent-${agentId}`);
                    // CRITICAL FIX: ALWAYS clear Prime, not just when ThreadManager.currentThreadId matches
                    if (typeof ThreadManager !== 'undefined') {
                        ThreadManager.currentThreadId = null;
                    }

                    // Clear Prime chat container
                    const primeMessages = document.getElementById('ai-chat-messages');
                    if (primeMessages) {
                        // CLEANUP: Destroy any active TwoRuleStreamProcessors before clearing
                        const bubbles = primeMessages.querySelectorAll('[data-processor-initialized="true"]');
                        bubbles.forEach(bubble => {
                            if (bubble._processor) {
                                console.log(`[CLEANUP] Destroying TwoRuleStreamProcessor for Prime (thread moving)`);
                                if (window._twoRuleProcessors) {
                                    window._twoRuleProcessors.delete(bubble._processor);
                                }
                                bubble._processor = null;
                            }
                        });
                        primeMessages.innerHTML = '';
                    }

                    // Clear Prime thread info container and show no-thread message
                    const primeThreadInfo = document.getElementById('prime-thread-info');
                    if (primeThreadInfo && typeof ThreadManager !== 'undefined') {
                        primeThreadInfo.innerHTML = ThreadManager.renderThreadInfoContainer('prime', null, false);
                        console.log(`[ISOLATION] Prime thread info cleared - showing welcome message`);
                    }

                    // CRITICAL: Always clear AppState when thread leaves Prime
                    if (typeof AppState !== 'undefined' && AppState.sessionId === thread.id) {
                        AppState.sessionId = null;
                        AppState.chatMessages = [];
                        console.log(`[ISOLATION] Prime AppState cleared (was: ${thread.id})`);
                    }

                    console.log(`[ISOLATION] Prime fully cleared`);
                } else if (currentLocation.startsWith('agent-')) {
                    // Unload from another agent
                    const oldAgentId = parseInt(currentLocation.replace('agent-', ''));
                    if (oldAgentId !== agentId) {
                        console.log(`[ISOLATION]  Clearing ${currentLocation} - thread moving to agent-${agentId}`);

                        // CLEANUP: Destroy any active TwoRuleStreamProcessors before clearing
                        const oldMessagesContainer = document.getElementById(`agent-messages-${oldAgentId}`);
                        if (oldMessagesContainer) {
                            const bubbles = oldMessagesContainer.querySelectorAll('[data-processor-initialized="true"]');
                            bubbles.forEach(bubble => {
                                if (bubble._processor) {
                                    console.log(`[CLEANUP] Destroying TwoRuleStreamProcessor for agent-${oldAgentId} (thread moving)`);
                                    if (window._twoRuleProcessors) {
                                        window._twoRuleProcessors.delete(bubble._processor);
                                    }
                                    bubble._processor = null;
                                    bubble._agentId = null;
                                    bubble._threadSlug = null;
                                }
                            });
                        }

                        this.clearAgentThread(oldAgentId);
                        console.log(`[ISOLATION] ✅ ${currentLocation} cleared and processors destroyed`);
                    }
                }
            }

            // Store thread info with message count
            // CRITICAL: Preserve original database message_count (don't overwrite with 0!)
            // thread.messages may be empty/undefined when loading metadata, but message_count from DB is accurate
            const originalMessageCount = thread.message_count || 0;
            const messageCount = thread.messages ? thread.messages.length : originalMessageCount;

            const metadata = {
                synergyCardId: thread.synergy_card_id || null,
                synergySessionName: thread.synergy_card_name || null,
                workflowId: thread.workflow_id || null,
                automationId: thread.automation_id || null
            };
            this.setLoadedThread(agentId, thread.id, thread.title, originalMessageCount, metadata);

            // CRITICAL: DON'T overwrite thread.message_count if it's already set from database
            // Only update if we have loaded messages in thread.messages array
            if (typeof ThreadManager !== 'undefined' && ThreadManager.threads) {
                const threadInArray = ThreadManager.threads.find(t => t.id === thread.id);
                if (threadInArray && thread.messages && thread.messages.length > 0) {
                    threadInArray.message_count = messageCount;
                    console.log(`[LOAD] Updated thread.message_count in ThreadManager.threads: ${messageCount}`);
                } else if (threadInArray) {
                    console.log(`[LOAD] Preserving database message_count: ${threadInArray.message_count}`);
                }
            }

            // CRITICAL: Clear AppState.sessionId when thread loads into agent
            // (Thread is now in agent, NOT in Prime)
            if (typeof AppState !== 'undefined' && AppState.sessionId === thread.id) {
                console.log(`[ISOLATION FIX] Clearing AppState.sessionId (thread ${thread.id} now in agent-${agentId})`);
                AppState.sessionId = null;
                AppState.chatMessages = [];
            }

            // Update thread-info container with unified structure
            const threadInfoContainer = document.getElementById(`thread-info-${agentId}`);
            if (threadInfoContainer) {
                if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.renderThreadInfoContainer === 'function') {
                    console.log(`[LOAD] Rendering thread info card for agent-${agentId}, thread ${thread.id}`);
                    const cardHtml = ThreadManager.renderThreadInfoContainer(
                        `agent-${agentId}`,
                        thread.id,
                        true  // compact mode
                    );

                    if (cardHtml) {
                        threadInfoContainer.innerHTML = cardHtml;
                        console.log(`✅ [LOAD] Thread info card rendered (${cardHtml.length} chars)`);
                    } else {
                        console.warn(`⚠️ [LOAD] Thread info card HTML is empty (ThreadManagerUI may not be loaded yet)`);
                        threadInfoContainer.innerHTML = '<div class="empty-thread-info">Loading...</div>';
                    }
                } else {
                    console.error(`❌ [LOAD] ThreadManager.renderThreadInfoContainer not available!`);
                    console.log('   ThreadManager exists?', typeof ThreadManager !== 'undefined');
                    console.log('   renderThreadInfoContainer exists?', typeof ThreadManager?.renderThreadInfoContainer);
                }
            } else {
                console.error(`❌ [LOAD] thread-info-${agentId} container not found in DOM!`);
            }

            // CRITICAL: Always sync session_id with thread.id when loading thread
            this.sessions[agentId] = thread.id;  // ? Use thread_slug as session_id
            console.log(`[LOAD] Agent ${agentId} session_id synced to thread_slug: ${thread.id}`);

            // Assign thread to this agent in backend ONLY if location changed
            // During restoration, skip this call (thread.location already correct from database)
            const expectedLocation = `agent-${agentId}`;
            if (typeof ThreadManager !== 'undefined' && thread.location !== expectedLocation) {
                console.log(` [loadThreadIntoAgent] Assigning thread ${thread.id} to ${expectedLocation} (location changed)`);
                ThreadManager.assignThread(thread.id, expectedLocation);
            } else {
                console.log(` [loadThreadIntoAgent] Thread ${thread.id} already at ${expectedLocation} (skipping backend call)`);
            }

            // Clear agent's messages
            const messagesContainer = document.querySelector(`#agent-column-${agentId} .agent-messages-container`);
            if (!messagesContainer) {
                console.error(`[ERROR] Messages container not found for agent-${agentId}`);
                return;
            }

            // ✅ CRITICAL FIX: Clear old thread from MessageStore if different thread being loaded
            const oldThreadId = this.sessions[agentId];
            if (oldThreadId && oldThreadId !== thread.id && typeof window.MessageStore !== 'undefined') {
                const oldCount = window.MessageStore.getMessageCount(oldThreadId);
                window.MessageStore.clearThread(oldThreadId);
                console.log(`[LOAD] ✅ Cleared ${oldCount} messages from MessageStore for old thread ${oldThreadId}`);
            }

            // Clear ALL old messages (preserve scroll controls)
            const messages = messagesContainer.querySelectorAll('.message-bubble, .ai-message');
            console.log(`[LOAD] Clearing ${messages.length} old messages from DOM for agent-${agentId}`);
            messages.forEach(msg => msg.remove());

            // Remove any empty-state node if present (keeps outer container)
            const emptyState = messagesContainer.querySelector('.empty-state');
            if (emptyState) {
                emptyState.remove();
                console.log(`[LOAD] Removed empty state for agent-${agentId}`);
            }

            // CRITICAL FIX: Always use container directly for message rendering
            // Container already has id="agent-messages-${agentId}" from agent-column.js
            // DO NOT create child divs with duplicate IDs - causes messages to render out of order!
            const messagesDiv = messagesContainer;
            console.log(`[LOAD] Using container as messagesDiv: ${messagesContainer.id}`);

            // Load messages from MessageStore (centralized storage)
            const storedMessages = window.MessageStore.getMessages(thread.id);
            console.log(`📦 [MessageStore] Retrieved ${storedMessages.length} messages for Agent ${agentId}`);

            // ✅ REMOVED: Pagination state initialization - we load all messages immediately

            if (!storedMessages || storedMessages.length === 0) {
                if (thread.message_count > 0) {
                    console.log(`[LOAD] Fetching initial 5 messages for thread ${thread.id} from backend...`);

                    // Show processing indicator while loading messages
                    const processingIndicator = createProcessingIndicator(agentId);
                    messagesDiv.appendChild(processingIndicator);

                    if (typeof ThreadManager !== 'undefined' && ThreadManager.loadMessagesForThread) {
                        // ✅ FIX: Load ALL messages (no pagination) - same as AI Prime
                        // Changed from limit=5 to limit=null to load complete conversation history
                        ThreadManager.loadMessagesForThread(thread.id, null, 0).then(async (result) => {
                            // ✅ FIX: Handle missing threads gracefully
                            if (result?.error === 'THREAD_NOT_FOUND') {
                                console.warn(`[LOAD] ⚠️ Thread ${thread.id} not found in database - removing from UI`);
                                removeProcessingIndicator(agentId);

                                // Remove thread card from UI
                                const threadCard = document.querySelector(`[data-thread-id="${thread.id}"]`);
                                if (threadCard) {
                                    threadCard.remove();
                                }

                                // Clean up localStorage
                                const storedThreads = JSON.parse(localStorage.getItem('agent_threads') || '{}');
                                if (storedThreads[agentId]) {
                                    const filteredThreads = storedThreads[agentId].filter(t => t.id !== thread.id);
                                    storedThreads[agentId] = filteredThreads;
                                    localStorage.setItem('agent_threads', JSON.stringify(storedThreads));
                                }

                                return; // Exit early
                            }

                            // ✅ REMOVED: Pagination state - all messages loaded immediately

                            // Re-fetch from MessageStore after backend load
                            const loadedMessages = window.MessageStore.getMessages(thread.id);
                            if (loadedMessages && loadedMessages.length > 0) {
                                console.log(`[LOAD] 📨 Rendering ${loadedMessages.length} messages for "${thread.title}"`);

                                // Remove processing indicator before rendering messages
                                removeProcessingIndicator(agentId);

                                // Insert progress bar as a sibling AFTER the messages container
                                // (not inside it — appending inside would place it above rendered messages)
                                const _rpIndicator = createRenderProgressIndicator(agentId, loadedMessages.length);
                                messagesContainer.insertAdjacentElement('afterend', _rpIndicator);

                                // CRITICAL: Use for...of with await instead of forEach
                                for (const [index, msg] of loadedMessages.entries()) {
                                    // USE SAME PATHWAY AS AI PRIME: UnifiedMessageRenderer
                                    // console.log(`[LOAD] 📝 Rendering message ${index + 1}/${loadedMessages.length}`);
                                    // console.log(`[LOAD]    Role: ${msg.role}`);
                                    // console.log(`[LOAD]    Content type: ${typeof msg.content}`);
                                    // console.log(`[LOAD]    Content preview:`, Array.isArray(msg.content) ? `Array[${msg.content.length}]` : String(msg.content).substring(0, 100));

                                    if (typeof UnifiedMessageRenderer !== 'undefined') {
                                        // PRIME PATHWAY: Use UnifiedMessageRenderer for ALL messages
                                        const rendered = await UnifiedMessageRenderer.render(
                                            messagesDiv,
                                            msg.role,
                                            msg.content,
                                            {
                                                threadId: thread.id,
                                                syncToBackend: false,
                                                scrollToBottom: false,  // Manual scroll at end
                                                createdAt: msg.created_at,  // Pass timestamp
                                                checkDuplicates: false,  // Historical load, already in MessageStore
                                                messageId: msg.id  // CRITICAL FIX: Pass message ID from database
                                            }
                                        );

                                        if (!rendered) {
                                            console.warn(`[LOAD] ❌ Message ${index + 1} NOT RENDERED (${msg.role})`);
                                        } else {
                                            // console.log(`[LOAD] ✅ Message ${index + 1} rendered successfully`);
                                        }
                                        // Update progress bar every 5 messages (keeps UI responsive)
                                        if ((index + 1) % 5 === 0 || index + 1 === loadedMessages.length) {
                                            updateRenderProgressIndicator(agentId, index + 1, loadedMessages.length);
                                        }
                                    } else {
                                        console.error(`[LOAD] UnifiedMessageRenderer not available! Falling back to manual rendering`);
                                        // Fallback: manual rendering (old pathway)
                                        if (msg.role === 'user') {
                                            let content;
                                            if (typeof msg.content === 'string') {
                                                content = msg.content;
                                            } else if (Array.isArray(msg.content)) {
                                                content = msg.content
                                                    .filter(block => !block.type || block.type === 'text')
                                                    .map(block => block.text || block.content || '')
                                                    .join('\n') || msg.content[0]?.text || JSON.stringify(msg.content);
                                            } else {
                                                content = String(msg.content);
                                            }
                                            addAgentMessage(agentId, 'user', content);
                                        } else if (msg.role === 'assistant') {
                                            const content = typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content);
                                            addAgentMessage(agentId, 'ai', content);
                                        }
                                    }
                                }
                                // All messages rendered — remove progress bar and scroll to bottom
                                removeRenderProgressIndicator(agentId);
                                messagesContainer.scrollTop = messagesContainer.scrollHeight;
                                console.log(`[LOAD] ✅ Completed - ${loadedMessages.length} messages rendered for agent-${agentId}`);

                                // ✅ Update scroll controls visibility after loading messages
                                if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.updateScrollControlsVisibility === 'function') {
                                    AgentColumn.updateScrollControlsVisibility(agentId);
                                }

                                // Setup scroll detection for infinite scroll
                                setupScrollDetection(agentId, messagesContainer);
                            } else {
                                console.warn(`[WARN] No messages found after loading thread ${thread.id}`);
                            }
                        }).catch(err => {
                            console.error(`[ERROR] Failed to load messages for thread ${thread.id}:`, err);
                        });
                    }
                } else {
                    console.log(`[INFO] Thread ${thread.id} has no messages yet`);
                }
            } else {
                // Load thread messages from MessageStore with proper rendering
                console.log(`[LOAD] 📨 Rendering ${storedMessages.length} messages from MessageStore for "${thread.title}"`);

                // Insert progress bar as a sibling AFTER the messages container
                // (not inside it — appending inside would place it above rendered messages)
                const _rpIndicator2 = createRenderProgressIndicator(agentId, storedMessages.length);
                messagesContainer.insertAdjacentElement('afterend', _rpIndicator2);

                // CRITICAL: Use for...of with await instead of forEach
                for (const [index, msg] of storedMessages.entries()) {
                    // USE SAME PATHWAY AS AI PRIME: UnifiedMessageRenderer
                    // console.log(`[LOAD] Rendering message ${index + 1}/${storedMessages.length} (${msg.role})`);

                    if (typeof UnifiedMessageRenderer !== 'undefined') {
                        // PRIME PATHWAY: Use UnifiedMessageRenderer for ALL messages
                        const rendered = await UnifiedMessageRenderer.render(
                            messagesDiv,
                            msg.role,
                            msg.content,
                            {
                                threadId: thread.id,
                                syncToBackend: false,
                                scrollToBottom: false,  // Manual scroll at end
                                checkDuplicates: false,  // Historical load, already in MessageStore
                                messageId: msg.id  // CRITICAL FIX: Pass message ID from database
                            }
                        );

                        if (!rendered) {
                            console.log(`[LOAD] Message ${index + 1} skipped (duplicate or tool_result-only)`);
                        }
                        // Update progress bar every 5 messages
                        if ((index + 1) % 5 === 0 || index + 1 === storedMessages.length) {
                            updateRenderProgressIndicator(agentId, index + 1, storedMessages.length);
                        }
                    } else {
                        console.error(`[LOAD] UnifiedMessageRenderer not available! Falling back to manual rendering`);
                        // Fallback: manual rendering (old pathway)
                        if (msg.role === 'user') {
                            let content;
                            if (typeof msg.content === 'string') {
                                content = msg.content;
                            } else if (Array.isArray(msg.content)) {
                                content = msg.content
                                    .filter(block => !block.type || block.type === 'text')
                                    .map(block => block.text || block.content || '')
                                    .join('\n') || msg.content[0]?.text || JSON.stringify(msg.content);
                            } else {
                                content = String(msg.content);
                            }
                            addAgentMessage(agentId, 'user', content);
                        } else if (msg.role === 'assistant') {
                            const content = typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content);
                            addAgentMessage(agentId, 'ai', content);
                        }
                    }
                }
                removeRenderProgressIndicator(agentId);
                console.log(`[OK] All ${storedMessages.length} messages rendered for agent-${agentId}`);

                // ✅ Update scroll controls visibility after loading messages from MessageStore
                if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.updateScrollControlsVisibility === 'function') {
                    AgentColumn.updateScrollControlsVisibility(agentId);
                }
            }

            // Update agent's session to use thread ID
            this.sessions[agentId] = thread.id;
            this.saveState();

            // Scroll to bottom
            if (messagesContainer) {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }

            // Update quick-nav badge to highlight it
            this.updateQuickNavBadge(agentId);

            // CRITICAL: Show input container wrapper now that thread is loaded (expandable Prime-style)
            const agentInputContainer = document.querySelector(`#agent-column-${agentId} .agent-input-container`);
            if (agentInputContainer) {
                agentInputContainer.style.display = 'block';
                console.log(`[UI] Showed agent-${agentId} input container (thread loaded)`);

                // Initialize input handlers if not already done
                if (typeof AgentInput !== 'undefined' && typeof AgentInput.setupHandlers === 'function') {
                    AgentInput.setupHandlers(agentId);
                }
            } else {
                console.warn(`[UI] Input container not found for agent-${agentId}`);
            }

            // CRITICAL: Show resize handle when thread is loaded
            const resizeHandle = document.querySelector(`.agent-resize-handle[data-agent-id="${agentId}"]`);
            if (resizeHandle) {
                resizeHandle.style.display = 'block';
                console.log(`[UI] Showed resize handle for agent-${agentId} (thread loaded)`);
            }

            // Also ensure input field is enabled
            const inputEl = document.querySelector(`#agent-column-${agentId} textarea`);
            const sendBtn = document.querySelector(`#agent-column-${agentId} .agent-send-btn`);

            if (inputEl) {
                inputEl.disabled = false;
                inputEl.placeholder = "Type your message...";
            }

            if (sendBtn) {
                sendBtn.disabled = false;
            }

            console.log(`[OK] Thread loaded into ${this.getAgentName(agentId)} with ${thread.messages ? thread.messages.length : 0} messages (TwoRule rendering)`);

            // Update agent header with thread info card
            this.updateAgentHeader(agentId);

            // ✅ VALIDATE: Check session isolation after loading
            setTimeout(() => {
                this.validateSessionIsolation(thread.id, `agent-${agentId}`);
            }, 100);
        } finally {
            // GUARD: Release loading lock
            const loadState = window.ThreadManager._loadingThreads.get(thread.id);
            if (loadState) {
                loadState.agents.delete(agentId);
                if (!loadState.prime && loadState.agents.size === 0) {
                    window.ThreadManager._loadingThreads.delete(thread.id);
                }
            }
        }
    },

    // Unload thread from agent and move to Prime
    async unloadThreadFromAgent(agentIdOrLocation, threadId) {
        console.log(`[UNLOAD] Unloading thread ${threadId} from ${agentIdOrLocation}`);

        // Handle both agentId (number) and location string ("agent-4")
        let agentId;
        if (typeof agentIdOrLocation === 'number') {
            agentId = agentIdOrLocation;
        } else if (typeof agentIdOrLocation === 'string' && agentIdOrLocation.startsWith('agent-')) {
            agentId = parseInt(agentIdOrLocation.replace('agent-', ''));
        } else {
            console.error('[UNLOAD] Invalid agent parameter:', agentIdOrLocation);
            return;
        }

        if (!agentId || isNaN(agentId)) {
            console.error('[UNLOAD] Invalid agent ID:', agentIdOrLocation);
            return;
        }

        // Find the thread
        const thread = Array.isArray(ThreadManager.threads) ? ThreadManager.threads.find(t => t.id === threadId) : null;
        if (!thread) {
            console.error('[UNLOAD] Thread not found:', threadId);
            return;
        }

        // Update thread assignment to Prime
        thread.location = 'prime';
        thread.agent = 'Prime';
        thread.updated = new Date().toISOString();

        // Save to backend
        await ThreadManager.saveThreadToBackend(thread);
        console.log(`[UNLOAD] Thread ${threadId} reassigned to Prime`);

        // Update backend assignment table
        try {
            const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/agent/threads/${threadId}/assign`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    location: 'prime',
                    agent_name: 'Prime'
                })
            });

            if (!response.ok) {
                console.warn('[UNLOAD] Failed to update assignment in backend');
            }
        } catch (error) {
            console.error('[UNLOAD] Error updating backend assignment:', error);
        }

        // Clear agent column UI - Keep EMPTY when no thread loaded
        const threadInfoContainer = document.getElementById(`thread-info-${agentId}`);
        if (threadInfoContainer) {
            threadInfoContainer.innerHTML = `
                <div class="thread-info-wrapper">
                </div>
            `;
        }

        // Clear messages
        const messagesContainer = document.querySelector(`#agent-column-${agentId} .agent-messages-container`);
        if (messagesContainer) {
            messagesContainer.innerHTML = `
                        <div class="empty-state" style="padding-top: 60%; text-align: center;">
                            <div style="line-height: 1.8; padding: 0 20px; max-width: 500px; margin: 0 auto;">
                                <div style="font-size: 2em; margin-bottom: 15px;">
                                    
                                </div>
                                <div style="font-size: 1.2em; margin-bottom: 12px; font-weight: 600; color: var(--text-primary, #e5e7eb);">
                                    ${this.getAgentName(agentId)} Ready
                                </div>
                                <div style="margin-bottom: 20px; opacity: 0.8; font-size: 0.95em; color: var(--text-secondary, #9ca3af);">
                                    No active thread — start a new chat or load from history
                                </div>
                                <div style="background: rgba(255, 255, 255, 0.05); padding: 14px; border-radius: 8px; border-left: 3px solid var(--accent-primary, #58a6ff); margin-bottom: 20px; text-align: left;">
                                    <div style="font-weight: 600; margin-bottom: 8px; font-size: 0.9em; color: var(--text-primary, #e5e7eb);"> Quick Tip</div>
                                    <div style="opacity: 0.85; font-size: 0.85em; line-height: 1.6; color: var(--text-secondary, #9ca3af);">
                                        <strong>Drag &amp; drop threads</strong> from the sidebar to move conversations between agents. 
                                        All formatting, context, and history stays intact!
                                    </div>
                                </div>
                                <div style="display: flex; gap: 12px; margin-top: 24px; justify-content: center;">
                                    <button class="btn btn-primary" onclick="event.stopPropagation(); ThreadManager.showNewChatModal('agent-${agentId}')" style="display: flex; align-items: center; gap: 8px; font-size: 14px;">
                                        <i class="fas fa-plus" style="font-size: 12px;"></i>
                                        Start New Chat
                                    </button>
                                    <button class="btn btn-secondary" onclick="event.stopPropagation(); ThreadManager.toggleThreadMenu()" style="display: flex; align-items: center; gap: 8px; font-size: 14px;">
                                        <i class="fas fa-history" style="font-size: 12px;"></i>
                                        Threads Catalogue
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
        }

        // Clear agent's loaded thread state
        delete this.loadedThreads[agentId];
        this.sessions[agentId] = null;
        this.saveState();

        // Update quick-nav badge
        this.updateQuickNavBadge(agentId);

        // NOTE: Don't call renderThreadList() here - ThreadManager.unloadThread() handles inline badge update
        // Calling it here would close the Threads Catalogue panel before the inline update can happen
        // ThreadManager.unloadThread() already calls loadThreadsFromBackend() to refresh data

        // Load thread in Prime if AI Agents tab is active
        const aiAgentsTab = document.querySelector('[data-tab="ai-agents"]');
        if (aiAgentsTab && aiAgentsTab.classList.contains('active')) {
            console.log('[UNLOAD] Loading thread in Prime panel');
            ThreadManager.switchThread(threadId);
        }

        // Show notification
        if (typeof showNotification !== 'undefined') {
            showNotification(`Thread moved to Prime`, 'success', 2000);
        }

        console.log(`[OK] Thread ${threadId} unloaded from ${this.getAgentName(agentId)}`);
    },

    // Collapse column to vertical bar
    collapseColumn(agentId) {
        const column = document.getElementById(`agent-${agentId}`);
        if (!column) return;

        // Add collapsed class
        column.classList.add('collapsed');

        // Update collapsed bar status
        this.updateCollapsedStatus(agentId);

        console.log(`[LAYOUT] Collapsed ${this.getAgentName(agentId)} to vertical bar`);
    },

    // Expand column from vertical bar
    expandColumn(agentId) {
        const column = document.getElementById(`agent-${agentId}`);
        if (!column) return;

        // Remove collapsed class
        column.classList.remove('collapsed');

        console.log(`[LAYOUT] Expanded ${this.getAgentName(agentId)} to full column`);
    },

    // Toggle column width between normal (400px) and wide (600px)
    toggleColumnWidth(agentId) {
        const column = document.getElementById(`agent-${agentId}`);
        const icon = document.getElementById(`width-icon-${agentId}`);
        if (!column || !icon) return;

        // Three states: normal(400px) → wide(600px) → extra-wide(800px) → normal
        const isWide = column.classList.contains('wide');
        const isExtraWide = column.classList.contains('extra-wide');

        if (isExtraWide) {
            // State 3 → State 1: Shrink to normal width
            column.classList.remove('extra-wide');
            column.classList.remove('wide');
            // Show chevron-right (>) to indicate "click to widen"
            icon.className = 'fas fa-chevron-right';
            console.log(`[SIZE] ${this.getAgentName(agentId)} width: 400px (normal)`);
        } else if (isWide) {
            // State 2 → State 3: Expand to extra-wide
            column.classList.remove('wide');
            column.classList.add('extra-wide');
            // Show double chevron-right (>>) to indicate "click to widen more"
            icon.className = 'fas fa-angle-double-right';
            console.log(`[SIZE] ${this.getAgentName(agentId)} width: 800px (extra-wide)`);
        } else {
            // State 1 → State 2: Expand to wide width
            column.classList.add('wide');
            // Show double chevron-right (>>) to indicate "click to widen more"
            icon.className = 'fas fa-angle-double-right';
            console.log(`[SIZE] ${this.getAgentName(agentId)} width: 600px (wide)`);
        }
    },

    // Update collapsed bar status text
    updateCollapsedStatus(agentId) {
        const threadInfo = this.loadedThreads[agentId];
        const statusEl = document.getElementById(`collapsed-status-${agentId}`);
        const timestampEl = document.getElementById(`collapsed-timestamp-${agentId}`);

        if (!statusEl) return;

        if (threadInfo && threadInfo.threadTitle) {
            // Show thread title
            statusEl.textContent = threadInfo.threadTitle;

            // Show timestamp if available
            if (timestampEl && typeof ThreadManager !== 'undefined' && Array.isArray(ThreadManager.threads)) {
                const thread = ThreadManager.threads.find(t => t.id === threadInfo.threadId);
                if (thread && (thread.updatedAt || thread.updated)) {
                    const date = new Date(thread.updatedAt || thread.updated);
                    const timeStr = date.toLocaleTimeString('en-US', {
                        hour: 'numeric',
                        minute: '2-digit',
                        hour12: true
                    });
                    const dateStr = date.toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric'
                    });
                    timestampEl.textContent = `${dateStr} ${timeStr} `;
                } else {
                    timestampEl.textContent = '';
                }
            }
        } else {
            // No thread loaded
            statusEl.textContent = 'No Thread';
            if (timestampEl) {
                timestampEl.textContent = '';
            }
        }
    },

    // Show "Start New Chat" button in agent columns that have no assigned thread
    showEmptyStateButtons(assignments = {}) {
        console.log('[SEARCH] [EMPTY STATE] Checking agent columns for empty states...');

        // Check all agent columns (1, 2, 3)
        for (let agentId = 1; agentId <= 3; agentId++) {
            const agentLocation = `agent-${agentId}`;
            const hasAssignment = Object.values(assignments).includes(agentLocation) ||
                Object.keys(assignments).includes(agentLocation);

            if (!hasAssignment) {
                // Agent column has NO assigned thread - show button
                const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
                if (messagesContainer) {
                    console.log(`[NEW][EMPTY STATE] Showing "Start New Chat" button in agent-${agentId} `);

                    // Clear existing content
                    // Clear only messages, preserve scroll controls
                    const messages = messagesContainer.querySelectorAll('.ai-message');
                    messages.forEach(msg => msg.remove());

                    // Create inner div for button
                    const innerDiv = document.createElement('div');
                    innerDiv.className = 'agent-messages';
                    innerDiv.id = `agent-messages-${agentId}`;
                    innerDiv.style.height = '100%';
                    messagesContainer.appendChild(innerDiv);

                    // Show button
                    if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.showStartNewChatButton === 'function') {
                        ThreadManager.showStartNewChatButton(`agent-messages-${agentId}`, agentLocation);
                    }
                }
            } else {
                console.log(`[OK][EMPTY STATE] agent-${agentId} has assigned thread, skipping...`);
            }
        }
    }
};

async function initMultiAgent() {
    console.log('🚀 [Multi-Agent] Initializing NATO AI Columns...');

    // ✅ FIX (Apr 9, 2026): Declare maxAgentId at function scope so it's accessible after .then()
    // Default to 3 (minimum NATO agents), will be updated in .then() after threads load
    let maxAgentId = 3;
    let agentIdsWithThreads = [];

    // Clear any stale localStorage data (backend is source of truth)
    MultiAgent.loadState();

    const container = document.getElementById('multi-agent-container');
    if (!container) {
        console.error('❌ [Multi-Agent] Container not found');
        return;
    }

    // Load threads in BACKGROUND (non-blocking) - UI renders immediately with empty agents
    // Threads populate the columns after they load (via loadDeferredThreadMessages after UI is visible)
    if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.loadThreadsFromBackend === 'function') {
        console.log('📥 [initMultiAgent] Loading threads in background (non-blocking)...');
        ThreadManager.loadThreadsFromBackend()  // NO AWAIT - fire and forget, UI renders immediately
            .then(() => {
                console.log(`✅ [initMultiAgent] Threads loaded: ${ThreadManager.threads?.length || 0} threads in memory`);
                
                // STEP 1: Calculate agent count from threads' location field (source of truth)
                // ✅ FIX DEC 28: Use thread.location from database instead of separate assignments API
                // Note: Update the function-scoped variables (not const - would shadow outer scope)
                agentIdsWithThreads = [];

                if (typeof ThreadManager !== 'undefined' && Array.isArray(ThreadManager.threads)) {
                    ThreadManager.threads.forEach(thread => {
                        if (thread.location && thread.location.startsWith('agent-')) {
                            const agentId = parseInt(thread.location.replace('agent-', ''));
                            if (!isNaN(agentId) && !agentIdsWithThreads.includes(agentId)) {
                                agentIdsWithThreads.push(agentId);
                            }
                        }
                    });
                    agentIdsWithThreads.sort((a, b) => a - b);
                }

                // Calculate max agent ID (minimum 3, or highest assigned + 1)
                const maxAssignedAgent = agentIdsWithThreads.length > 0 ? Math.max(...agentIdsWithThreads) : 0;
                maxAgentId = Math.max(maxAssignedAgent + 1, 3);  // Update the function-scoped maxAgentId

                // Update nextAgentId based on actual usage (not localStorage)
                MultiAgent.nextAgentId = maxAgentId + 1;

                console.log(`📊 [Multi-Agent] Creating ${maxAgentId} agents (threads assigned to: [${agentIdsWithThreads.join(', ')}])`);

                // STEP 3: Create ALL agents from 1 to maxAgentId
                for (let i = 1; i <= maxAgentId; i++) {
                    createAgentColumn(i);

                    // [NEW] GUARANTEE default width (400px) - remove any 'wide' class
                    const column = document.getElementById(`agent-${i}`);
                    if (column) {
                        column.classList.remove('wide');
                        // Make columns EXPANDED by default (not collapsed)
                        column.classList.remove('collapsed');
                        console.log(`[SIZE][Multi-Agent] ${MultiAgent.getAgentName(i)} initialized at default width(400px)`);
                    }
                }

                // ✅ FIX DEC 28: Build assignments map BEFORE using it
                // Create assignments map from thread locations for buildQuickNav and hasThread checks
                const assignments = {};
                if (typeof ThreadManager !== 'undefined' && Array.isArray(ThreadManager.threads)) {
                    ThreadManager.threads.forEach(thread => {
                        if (thread.location) {
                            assignments[thread.location] = thread.id;
                        }
                    });
                }

                // Now check which agents have threads (after assignments map is created)
                for (let i = 1; i <= maxAgentId; i++) {
                    const hasThread = assignments[`agent-${i}`];
                    // ALL agents are EXPANDED by default now (no auto-collapse)
                    console.log(`[OK][Multi-Agent] ${MultiAgent.getAgentName(i)} is EXPANDED (has thread: ${!!hasThread})`);
                }

                MultiAgent.buildQuickNav(maxAgentId, assignments);
                console.log(`✅ [Command Center] Quick nav built with ${maxAgentId} agent badges`);

                // Update stats
                MultiAgent.updateDashboardStats();
                // ✅ FIX (Apr 8, 2026): Restore thread assignments into columns immediately after threads load.
                // This ensures columns are populated regardless of whether ThreadManager.init() fires.
                if (typeof ThreadManager.restoreThreadAssignments === 'function') {
                    ThreadManager.restoreThreadAssignments()
                        .then(() => {
                            ThreadManager._assignmentsRestored = true;
                            console.log('✅ [initMultiAgent] Thread assignments restored into columns');
                            if (typeof MultiAgent.updateDashboardStats === 'function') {
                                MultiAgent.updateDashboardStats();
                            }
                        })
                        .catch(err => console.warn('⚠️ [initMultiAgent] Assignment restore error (non-fatal):', err));
                } else {
                    // Assignment module not yet loaded — fall back to dashboard stats only
                    if (typeof MultiAgent !== 'undefined' && typeof MultiAgent.updateDashboardStats === 'function') {
                        MultiAgent.updateDashboardStats();
                        console.log('🔄 [initMultiAgent] Dashboard stats updated with loaded threads');
                    }
                }
            })
            .catch(err => console.error('❌ [initMultiAgent] Thread loading failed:', err));
    } else {
        console.error('❌ [initMultiAgent] ThreadManager.loadThreadsFromBackend not available!');
    }
}

/**
 * Load all deferred thread messages AFTER the UI has rendered.
 *
 * Strategy: initMultiAgent() renders thread INFO cards instantly using cached thread list data.
 * The expensive per-thread message history API calls are deferred here, so the loading overlay
 * hides in ~5s instead of ~60s. Called from user_auth.js after hideLoadingOverlay().
 *
 * Sequential loading is intentional — prevents connection pool exhaustion on Render.
 */
window.loadDeferredThreadMessages = async function () {

    // 🔍 DEBUG: Check parent container state
    const multiAgentContainer = document.getElementById('multi-agent-container');
    console.log('🔍 [initMultiAgent] Parent container state:', {
        exists: !!multiAgentContainer,
        isConnected: multiAgentContainer?.isConnected,
        offsetWidth: multiAgentContainer?.offsetWidth,
        offsetHeight: multiAgentContainer?.offsetHeight,
        computedDisplay: multiAgentContainer ? window.getComputedStyle(multiAgentContainer).display : 'N/A',
        childrenCount: multiAgentContainer?.children.length || 0
    });

    const containerVerificationPromises = [];

    for (let i = 1; i <= maxAgentId; i++) {
        const promise = new Promise((resolve) => {
            // Check immediately first
            let container = document.getElementById(`thread-info-${i}`);
            if (container) {
                console.log(`✅ [initMultiAgent] Agent-${i} container ready (immediate)`);
                console.log(`   ├─ Container ID: ${container.id}`);
                console.log(`   ├─ IsConnected: ${container.isConnected}`);
                console.log(`   ├─ OffsetWidth: ${container.offsetWidth}px`);
                console.log(`   └─ Parent: ${container.parentElement?.id || 'unknown'}`);
                resolve();
                return;
            }

            // If not found, wait with short timeout for DOM insertion
            let attempts = 0;
            const maxAttempts = 20; // Increased from 10 to 20 (1 second total)
            const checkInterval = setInterval(() => {
                container = document.getElementById(`thread-info-${i}`);
                attempts++;

                if (container) {
                    console.log(`✅ [initMultiAgent] Agent-${i} container ready (after ${attempts * 50}ms)`);
                    console.log(`   ├─ Container ID: ${container.id}`);
                    console.log(`   ├─ IsConnected: ${container.isConnected}`);
                    console.log(`   ├─ OffsetWidth: ${container.offsetWidth}px`);
                    console.log(`   └─ Parent: ${container.parentElement?.id || 'unknown'}`);
                    clearInterval(checkInterval);
                    resolve();
                } else if (attempts >= maxAttempts) {
                    console.error(`❌ [initMultiAgent] Agent-${i} container NOT created after ${maxAttempts * 50}ms!`);
                    console.error(`   └─ This will cause thread loading to fail!`);

                    // Try to find the agent column itself
                    const agentColumn = document.getElementById(`agent-${i}`);
                    if (agentColumn) {
                        console.error(`   ├─ Agent column exists: agent-${i}`);
                        console.error(`   ├─ Column innerHTML length: ${agentColumn.innerHTML.length}`);
                        console.error(`   └─ But thread-info-${i} is missing from it!`);
                    } else {
                        console.error(`   └─ Agent column agent-${i} doesn't exist either!`);
                    }

                    clearInterval(checkInterval);
                    resolve(); // Don't block - continue anyway
                }
            }, 50);
        });

        containerVerificationPromises.push(promise);
    }

    // Wait for all containers to be ready
    await Promise.all(containerVerificationPromises);
    console.log(`✅ [initMultiAgent] All agent column containers verified and ready`);

    // Final verification: Check all containers one more time
    const missingContainers = [];
    for (let i = 1; i <= maxAgentId; i++) {
        const container = document.getElementById(`thread-info-${i}`);
        if (!container) {
            missingContainers.push(i);
        }
    }

    if (missingContainers.length > 0) {
        console.error(`❌ [initMultiAgent] CRITICAL: ${missingContainers.length} containers still missing after verification!`);
        console.error(`   Missing: thread-info-${missingContainers.join(', thread-info-')}`);
        console.error(`   This will cause thread loading failures. Aborting initialization.`);
        throw new Error(`Multi-agent initialization failed: ${missingContainers.length} DOM containers missing`);
    } else {
        console.log(`✅ [initMultiAgent] Final check: All ${maxAgentId} containers confirmed present`);
    }

    // STEP 5: LOAD threads on page initialization (not just restore to memory)
    // CRITICAL: Load prime thread FIRST, then agent threads

    // STEP 5A: INITIALIZE PRIME PANEL (same pattern as agent columns)
    // Check if prime thread exists and render appropriate content
    const primeThreadInfoContainer = document.getElementById('prime-thread-info');
    if (!primeThreadInfoContainer) {
        console.warn(`⚠️ [initMultiAgent] Prime thread-info container NOT FOUND - thread info cards won't render`);
    } else {
        console.log(`✅ [initMultiAgent] Prime thread-info container ready`);

        // ✅ FIX DEC 28: Find prime thread using thread.location field
        const primeLoadedThread = typeof ThreadManager !== 'undefined' && Array.isArray(ThreadManager.threads)
            ? ThreadManager.threads.find(t => t.location === 'prime')
            : null;

        if (primeLoadedThread && typeof ThreadManager !== 'undefined') {
            // Thread is assigned - render info card immediately, defer message loading to post-render
            console.log(`🎯 [initMultiAgent] Prime has thread: ${primeLoadedThread.id}, rendering card (messages deferred)...`);

            // ✅ Render thread info card immediately (data already in ThreadManager.threads - no API call)
            if (typeof ThreadManager.renderThreadInfoContainer === 'function') {
                // Render with compact=false for full card display
                // Use 'prime' location to show correct badge styling
                const cardHtml = ThreadManager.renderThreadInfoContainer('prime', primeLoadedThread.id, false);
                if (cardHtml) {
                    primeThreadInfoContainer.innerHTML = cardHtml;
                    console.log(`✅ [initMultiAgent] Prime thread card rendered (${cardHtml.length} chars)`);
                } else {
                    console.error(`❌ [initMultiAgent] Prime card HTML is empty!`);
                }
            }

            // ⏳ Queue Prime message loading to run AFTER UI renders (was blocking ~15s on cold start)
            window._pendingMessageLoads = window._pendingMessageLoads || [];
            window._pendingMessageLoads.push({ type: 'prime', threadId: primeLoadedThread.id });

            // Show loading state in Prime messages container while messages are deferred
            const primeMsgContainer = document.getElementById('ai-chat-messages');
            if (primeMsgContainer && typeof AgentColumn !== 'undefined' && typeof AgentColumn.renderLoadingState === 'function') {
                primeMsgContainer.innerHTML = AgentColumn.renderLoadingState(null, 'Prime');
            }
            console.log(`⏳ [initMultiAgent] Prime messages queued for post-render load`);
        } else {
            // No prime thread - ensure empty state is shown
            console.log(`📭 [initMultiAgent] No prime thread assigned, keeping empty state`);
            // Empty state already in HTML, no action needed
        }
    }

    // Then load all agent-assigned threads
    // ✅ FIX DEC 28: Use thread.location as source of truth (not separate assignments API)
    // The database sessions.threads.location field already contains the correct assignment
    const agentLoadPromises = [];

    if (typeof ThreadManager !== 'undefined' && Array.isArray(ThreadManager.threads)) {
        // Iterate through ALL threads and load those with agent locations
        ThreadManager.threads.forEach(thread => {
            const location = thread.location;

            // Skip if not an agent location
            if (!location || !location.startsWith('agent-')) {
                return;
            }

            // Extract agent ID from location (e.g., "agent-4" -> 4)
            const agentId = parseInt(location.replace('agent-', ''));
            if (isNaN(agentId)) {
                console.warn(`[WARN] Invalid agent ID in location: ${location}`);
                return;
            }

            console.log(`✅ [initMultiAgent] Found thread "${thread.title}" (${thread.id}) assigned to ${location}`);

            // Only load if agent column exists (within maxAgentId range)
            if (agentId <= maxAgentId) {
                // Update MultiAgent state
                MultiAgent.loadedThreads[agentId] = {
                    threadId: thread.id,
                    threadTitle: thread.title
                };
                MultiAgent.sessions[agentId] = thread.id;

                // Tag thread with agent name
                const agentName = MultiAgent.getAgentName(agentId);
                thread.agent = agentName;
                console.log(`[OK] Tagged thread "${thread.title}" with agent: ${agentName}`);

                // ✅ Render thread info card immediately (data already in ThreadManager.threads - no API call)
                requestAnimationFrame(() => {
                    if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.renderThreadInfoContainer === 'function') {
                        const cardHtml = ThreadManager.renderThreadInfoContainer(`agent-${agentId}`, thread.id, true);
                        const threadInfoContainer = document.getElementById(`thread-info-${agentId}`);
                        if (threadInfoContainer && cardHtml) {
                            threadInfoContainer.innerHTML = cardHtml;
                            console.log(`✅ [initMultiAgent] Agent-${agentId} thread card rendered (${cardHtml.length} chars)`);
                        } else if (!threadInfoContainer) {
                            console.error(`❌ [initMultiAgent] thread-info-${agentId} container NOT FOUND in DOM!`);
                        } else {
                            console.error(`❌ [initMultiAgent] Card HTML is empty or null for agent-${agentId}!`);
                        }
                    }
                    MultiAgent.updateAgentHeader(agentId);
                });

                // ⏳ Queue agent message loading to run AFTER UI renders (was blocking ~15s per agent on cold start)
                window._pendingMessageLoads = window._pendingMessageLoads || [];
                window._pendingMessageLoads.push({ type: 'agent', agentId, thread });

                // Show loading state in agent messages container while messages are deferred
                const agentMsgContainer = document.getElementById(`agent-messages-${agentId}`);
                if (agentMsgContainer && typeof AgentColumn !== 'undefined' && typeof AgentColumn.renderLoadingState === 'function') {
                    agentMsgContainer.innerHTML = AgentColumn.renderLoadingState(agentId, agentName);
                }
                console.log(`⏳ [initMultiAgent] Agent-${agentId} messages queued for post-render load`);
            } else {
                console.warn(`[WARN] Thread "${thread.title}" assigned to ${location} but agent column doesn't exist (maxAgentId=${maxAgentId})`);
            }
        });
    } else {
        console.error(`❌ [initMultiAgent] ThreadManager.threads not available!`);
    }

    // ✅ PERF: Agent message loads are deferred to window.loadDeferredThreadMessages() (post-render)
    // Previously: sequential loop here caused ~15s delay per agent (total startup ~60s)
    // Now: thread INFO cards are rendered immediately above; messages load after hideLoadingOverlay()
    console.log(`✅ [initMultiAgent] Agent thread cards rendered; ${(window._pendingMessageLoads || []).length} panel(s) queued for post-render message load`);

    // Legacy fallback: Restore threads from old MultiAgent.loadedThreads if not in assignments
    // This handles migration from old system to new centralized tracker
    Object.keys(MultiAgent.loadedThreads).forEach(agentId => {
        const threadInfo = MultiAgent.loadedThreads[agentId];
        if (threadInfo && threadInfo.threadId) {
            const location = `agent-${agentId}`;

            // Check if already restored from centralized assignments
            if (assignments[location] === threadInfo.threadId) {
                console.log(`[OK] Thread ${threadInfo.threadId} already restored from assignments`);
                return;
            }

            // Not in assignments - migrate it
            console.warn(`[WARN] Migrating thread ${threadInfo.threadId} to centralized tracker`);

            if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.assignThread === 'function') {
                ThreadManager.assignThread(threadInfo.threadId, location);

                const thread = Array.isArray(ThreadManager.threads) ? ThreadManager.threads.find(t => t.id === threadInfo.threadId) : null;
                if (thread) {
                    const agentIdNum = parseInt(agentId);
                    MultiAgent.sessions[agentIdNum] = threadInfo.threadId;

                    const agentName = MultiAgent.getAgentName(agentIdNum);
                    thread.agent = agentName;
                    // Note: Thread saved via backend API, no manual save needed

                    setTimeout(() => {
                        const messagesContainer = document.querySelector(`#agent-${agentIdNum} .agent-messages-container`);
                        if (messagesContainer) {
                            // Clear old messages but preserve scroll controls
                            const oldMessages = messagesContainer.querySelectorAll('.ai-message, .message-bubble');
                            oldMessages.forEach(msg => msg.remove());
                            console.log(`[Restore] Cleared ${oldMessages.length} old messages from agent-${agentIdNum}`);
                        }

                        MultiAgent.loadThreadIntoAgent(agentIdNum, thread);
                        console.log(`[OK] Migrated and restored thread "${thread.title}" to ${agentName}`);

                        setTimeout(() => {
                            MultiAgent.updateAgentHeader(agentIdNum);
                        }, 50);
                    }, 200);
                }
            }
        }
    });

    // Log final initialization status
    const assignedCount = agentIdsWithThreads.length;
    const collapsedCount = maxAgentId - assignedCount;
    console.log(`✅ [Multi-Agent] Initialized with ${maxAgentId} NATO agents (${assignedCount} with threads, ${collapsedCount} empty) - Backend is source of truth`);

    // CRITICAL FIX NOV 29: Ensure all thread info cards are rendered after initialization
    console.log(`🔄 [initMultiAgent] Final pass: Ensuring all thread info cards are visible...`);
    await new Promise(resolve => {
        requestAnimationFrame(() => {
            // Refresh all agent thread info cards
            for (let agentId = 1; agentId <= maxAgentId; agentId++) {
                const threadInfo = MultiAgent.loadedThreads[agentId];
                if (threadInfo && threadInfo.threadId) {
                    const container = document.getElementById(`thread-info-${agentId}`);
                    if (container && typeof ThreadManager !== 'undefined' && typeof ThreadManager.renderThreadInfoContainer === 'function') {
                        const cardHtml = ThreadManager.renderThreadInfoContainer(`agent-${agentId}`, threadInfo.threadId, true);
                        if (cardHtml && cardHtml.length > 600) { // Only inject if valid card (not empty state)
                            container.innerHTML = cardHtml;
                            console.log(`✅ [initMultiAgent] Final refresh: Agent ${agentId} thread card rendered (${cardHtml.length} chars)`);
                        }
                    }
                }
            }

            // Refresh Prime thread info card
            const primeContainer = document.getElementById('prime-thread-info');
            if (primeContainer && assignments['prime']) {
                if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.renderThreadInfoContainer === 'function') {
                    const cardHtml = ThreadManager.renderThreadInfoContainer('prime', assignments['prime'], false);
                    if (cardHtml && cardHtml.length > 600) {
                        primeContainer.innerHTML = cardHtml;
                        console.log(`✅ [initMultiAgent] Final refresh: Prime thread card rendered (${cardHtml.length} chars)`);
                    }
                }
            }

            resolve();
        });
    });
    console.log(`✅ [initMultiAgent] All thread info cards refreshed`);

    // ✅ FIX (Jan 3, 2026): Emit event to notify other modules (e.g., CommunicationHub) that agent threads are loaded
    window.dispatchEvent(new CustomEvent('multiagent-threads-loaded', {
        detail: {
            agentCount: maxAgentId,
            threadsLoaded: agentIdsWithThreads.length,
            timestamp: new Date().toISOString()
        }
    }));
    console.log(`📢 [initMultiAgent] Emitted 'multiagent-threads-loaded' event`);

    // Add the "Add Agent" bar
    createAddAgentBar();

    // Setup drag/drop zones for agent columns
    if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.setupAgentDropZones === 'function') {
        setTimeout(() => {
            ThreadManager.setupAgentDropZones();
        }, 100);
    }

    // Setup drag/drop zone for Prime chat container
    if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.setupPrimeDropZone === 'function') {
        setTimeout(() => {
            ThreadManager.setupPrimeDropZone();
        }, 100);
    }

    // Setup threads catalogue as "dead zone" - drops here are ignored (no action)
    setTimeout(() => {
        const threadMenu = document.getElementById('thread-menu');
        if (threadMenu) {
            threadMenu.addEventListener('drop', (e) => {
                e.stopPropagation();
                e.preventDefault();
                console.log('🛑 [Drop] Dropped in threads catalogue - no action (dead zone)');
                // Clear all drag-over states
                document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
            });
            threadMenu.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'none'; // Show "not allowed" cursor
            });
            console.log('✅ [Drop Zone] Threads catalogue configured as dead zone (drops ignored)');
        }
    }, 150);

    // Validate and fix any assignment inconsistencies
    if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.validateAssignments === 'function') {
        setTimeout(async () => {
            try {
                const validation = await ThreadManager.validateAssignments();
                if (validation.fixed) {
                    console.log(' [Multi-Agent] Assignment inconsistencies detected and fixed on page load');
                }
            } catch (validationErr) {
                // Non-fatal: validation may fail on cold start (502) - app still works
                console.warn('⚠️ [Multi-Agent] validateAssignments error (non-fatal):', validationErr.message);
            }
        }, 500);
    }

    // Setup Socket.IO event listeners for real-time lock state changes
    if (window.SynergyRealtime && window.SynergyRealtime.socket) {
        const socket = window.SynergyRealtime.socket;
        const mySessionToken = window.SynergyRealtime.sessionToken;

        // Listen for thread lock events
        socket.on('thread_locked', (data) => {
            console.log('🔒 [Socket.IO] Received thread_locked event:', data);

            // Don't show lock UI to the user who locked it
            if (data.session_token === mySessionToken) {
                console.log('🔒 [Socket.IO] This is my lock, skipping UI update');
                return;
            }

            // Find which agent has this thread
            const agentId = Object.keys(MultiAgent.loadedThreads).find(agentIdKey => {
                const threadInfo = MultiAgent.loadedThreads[agentIdKey];
                return threadInfo && threadInfo.threadId === data.thread_id;
            });

            if (agentId) {
                const displayName = data.locked_by || 'another user';
                MultiAgent.showLockBanner(parseInt(agentId), displayName);
                MultiAgent.disableAgentInput(parseInt(agentId));
                console.log(`🔒 [Socket.IO] Agent ${agentId} locked by ${displayName}`);
            }
        });

        // Listen for thread unlock events
        socket.on('thread_unlocked', (data) => {
            console.log('🔓 [Socket.IO] Received thread_unlocked event:', data);

            // Find which agent has this thread
            const agentId = Object.keys(MultiAgent.loadedThreads).find(agentIdKey => {
                const threadInfo = MultiAgent.loadedThreads[agentIdKey];
                return threadInfo && threadInfo.threadId === data.thread_id;
            });

            if (agentId) {
                MultiAgent.hideLockBanner(parseInt(agentId));
                MultiAgent.enableAgentInput(parseInt(agentId));
                console.log(`🔓 [Socket.IO] Agent ${agentId} unlocked`);
            }
        });

        // Listen for real-time messages from other sessions
        socket.on('agent_message_received', (data) => {
            console.log('💬 [Socket.IO] Received agent_message_received event:', data);

            // Don't render message if it's from this session (already rendered)
            if (data.session_token === mySessionToken) {
                console.log('💬 [Socket.IO] Message from my session, skipping');
                return;
            }

            // Find which agent has this thread
            const agentId = Object.keys(MultiAgent.loadedThreads).find(agentIdKey => {
                const threadInfo = MultiAgent.loadedThreads[agentIdKey];
                return threadInfo && threadInfo.threadId === data.thread_id;
            });

            if (agentId) {
                const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
                if (!messagesContainer) {
                    console.warn(`💬 [Socket.IO] Messages container not found for agent ${agentId}`);
                    return;
                }

                // Render the message
                const messageDiv = UnifiedMessageRenderer.render(
                    `#agent-messages-${agentId}`,
                    data.role,
                    data.message,
                    {
                        threadId: data.thread_id,
                        syncToBackend: false,
                        contentBlocks: data.content_blocks,
                        messageId: data.message_id || null  // Socket messages may not have ID yet
                    }
                );

                if (messageDiv && typeof AgentColumn !== 'undefined' && typeof AgentColumn.applyViewModeToMessage === 'function') {
                    AgentColumn.applyViewModeToMessage(parseInt(agentId), messageDiv);
                }

                scrollAgentToBottom(parseInt(agentId));
                console.log(`💬 [Socket.IO] Rendered message in Agent ${agentId} from other session`);
            } else {
                console.log(`💬 [Socket.IO] Thread ${data.thread_id} not loaded in any agent`);
            }
        });

        // Store Prime thread ID for lock checking (updated when Prime loads a thread)
        window._primeThreadId = assignments['prime'] || null;

        // Listen for Prime AI lock/unlock events
        socket.on('thread_locked', (data) => {
            if (data.session_token === mySessionToken) return;

            // Check if Prime has this thread
            if (window._primeThreadId && window._primeThreadId === data.thread_id) {
                const displayName = data.locked_by || 'another user';
                if (typeof PrimeAI !== 'undefined') {
                    PrimeAI.showLockBanner(displayName);
                    PrimeAI.disableInput();
                    console.log(`🔒 [Socket.IO] Prime locked by ${displayName}`);
                }
            }
        });

        socket.on('thread_unlocked', (data) => {
            if (data.session_token === mySessionToken) return;

            // Check if Prime has this thread
            if (window._primeThreadId && window._primeThreadId === data.thread_id) {
                if (typeof PrimeAI !== 'undefined') {
                    PrimeAI.hideLockBanner();
                    PrimeAI.enableInput();
                    console.log(`🔓 [Socket.IO] Prime unlocked`);
                }
            }
        });

        // Listen for Prime AI messages from other sessions
        socket.on('agent_message_received', (data) => {
            if (data.session_token === mySessionToken) return;

            // Check if Prime has this thread
            if (window._primeThreadId && window._primeThreadId === data.thread_id) {
                const messagesContainer = document.getElementById('ai-chat-messages');
                if (!messagesContainer) {
                    console.warn(`💬 [Socket.IO] Prime messages container not found`);
                    return;
                }

                // Render the message in Prime
                const messageDiv = UnifiedMessageRenderer.render(
                    '#ai-chat-messages',
                    data.role,
                    data.message,
                    {
                        threadId: data.thread_id,
                        syncToBackend: false,
                        contentBlocks: data.content_blocks,
                        messageId: data.message_id || null  // Socket messages may not have ID yet
                    }
                );

                if (messageDiv && typeof PrimeAI !== 'undefined' && typeof PrimeAI.applyViewModeToMessage === 'function') {
                    PrimeAI.applyViewModeToMessage(messageDiv);
                }

                if (typeof PrimeChat !== 'undefined' && typeof PrimeChat.scrollToBottom === 'function') {
                    PrimeChat.scrollToBottom();
                }
                console.log(`💬 [Socket.IO] Rendered message in Prime from other session`);
            }
        });

        console.log('✅ [Socket.IO] Lock and message event listeners registered (Agents + Prime)');
    } else {
        console.warn('⚠️ [Socket.IO] SynergyRealtime not available, real-time features will not work');
    }

    // [LOCK] FINAL WIDTH ENFORCEMENT: Ensure ALL columns (especially Delta+) load at default 400px
    // This runs AFTER thread restorations complete (1000ms delay covers all setTimeout operations)
    setTimeout(() => {
        for (let i = 1; i <= maxAgentId; i++) {
            const column = document.getElementById(`agent-${i}`);
            const icon = document.getElementById(`width-icon-${i}`);

            if (column) {
                // Force remove 'wide' class regardless of current state
                const hadWide = column.classList.contains('wide');
                column.classList.remove('wide');

                // Reset icon to chevron-right (→) for default 400px width
                if (icon) {
                    icon.className = 'fas fa-chevron-right';
                }

                if (hadWide) {
                    console.log(`[LOCK][WIDTH ENFORCEMENT] Removed 'wide' from ${MultiAgent.getAgentName(i)} after restoration`);
                }
            }
        }
        console.log(`[OK][WIDTH ENFORCEMENT] All ${maxAgentId} columns guaranteed at 400px default width with correct icons`);
    }, 1000);

    // [LOCK] ADDITIONAL WIDTH ENFORCEMENT: Run multiple checks to catch any late 'wide' class additions
    [1500, 2000, 3000].forEach(delay => {
        setTimeout(() => {
            for (let i = 1; i <= maxAgentId; i++) {
                const column = document.getElementById(`agent-${i}`);
                const icon = document.getElementById(`width-icon-${i}`);

                if (column && column.classList.contains('wide')) {
                    column.classList.remove('wide');

                    // Reset icon to chevron-right for default width
                    if (icon) {
                        icon.className = 'fas fa-chevron-right';
                    }

                    console.log(`[LOCK][LATE WIDTH ENFORCEMENT @${delay}ms] Removed 'wide' from ${MultiAgent.getAgentName(i)} `);
                }
            }
        }, delay);
    });

    console.log(`[Multi - Agent] [OK] Initialized with ${maxAgentId} NATO agents(${agentIdsWithThreads.length} with threads, ${maxAgentId - agentIdsWithThreads.length} collapsed)`);
}

/**
 * Load all deferred thread messages AFTER the UI has rendered.
 *
 * Strategy: initMultiAgent() renders thread INFO cards instantly using cached thread list data.
 * The expensive per-thread message history API calls are deferred here, so the loading overlay
 * hides in ~5s instead of ~60s. Called from user_auth.js after hideLoadingOverlay().
 *
 * Sequential loading is intentional — prevents connection pool exhaustion on Render.
 */
window.loadDeferredThreadMessages = async function () {
    const loads = window._pendingMessageLoads || [];
    window._pendingMessageLoads = []; // Clear to prevent double-run

    if (loads.length === 0) {
        console.log('✅ [DeferredLoad] No deferred messages to load');
        return;
    }

    // Sort: Prime first, then agents in numerical order (agent-1 → agent-2 → ... → agent-N)
    loads.sort((a, b) => {
        if (a.type === 'prime') return -1;
        if (b.type === 'prime') return 1;
        return (a.agentId || 0) - (b.agentId || 0);
    });

    console.log(`⏳ [DeferredLoad] Loading order: ${loads.map(l => l.type === 'prime' ? 'Prime' : `Agent-${l.agentId}`).join(' → ')}`);

    for (const item of loads) {
        try {
            if (item.type === 'prime') {
                console.log(`⏳ [DeferredLoad] Loading Prime messages (thread ${item.threadId})...`);

                // Clear loading state before rendering
                const primeMsgContainer = document.getElementById('ai-chat-messages');
                if (primeMsgContainer) {
                    primeMsgContainer.querySelectorAll('.loading-thread-state, .empty-state').forEach(el => el.remove());
                }

                if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.loadThreadInPrime === 'function') {
                    await ThreadManager.loadThreadInPrime(item.threadId);
                    console.log(`✅ [DeferredLoad] Prime messages loaded`);
                }

            } else if (item.type === 'agent') {
                const { agentId, thread } = item;
                console.log(`⏳ [DeferredLoad] Loading agent-${agentId} messages (thread ${thread.id})...`);

                // Clear loading state + any stale messages
                const messagesContainer = document.querySelector(`#agent-column-${agentId} .agent-messages-container`);
                if (messagesContainer) {
                    const oldMessages = messagesContainer.querySelectorAll('.ai-message, .message-bubble, .loading-thread-state, .empty-state');
                    oldMessages.forEach(msg => msg.remove());
                }

                // Pre-load messages into MessageStore
                if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.loadMessagesForThread === 'function') {
                    await ThreadManager.loadMessagesForThread(thread.id, null, 0);
                    const messageCount = (window.MessageStore?.getMessages(thread.id) || []).length;
                    console.log(`✅ [DeferredLoad] ${messageCount} messages in MessageStore for thread ${thread.id}`);
                }

                // Render messages into the agent column
                if (typeof MultiAgent !== 'undefined' && typeof MultiAgent.loadThreadIntoAgent === 'function') {
                    await MultiAgent.loadThreadIntoAgent(agentId, thread);
                }

                // Refresh agent header
                if (typeof MultiAgent !== 'undefined' && typeof MultiAgent.updateAgentHeader === 'function') {
                    MultiAgent.updateAgentHeader(agentId);
                }

                console.log(`✅ [DeferredLoad] Agent-${agentId} messages loaded`);
            }
        } catch (err) {
            console.warn(`⚠️ [DeferredLoad] Failed to load ${item.type} messages (non-fatal):`, err.message);
            // Continue loading remaining panels
        }
    }

    window.dispatchEvent(new CustomEvent('multiagent-messages-loaded', {
        detail: { loaded: loads.length, timestamp: new Date().toISOString() }
    }));
    console.log(`✅ [DeferredLoad] All ${loads.length} deferred message load(s) complete`);
};

function createAgentColumn(agentId) {
    const container = document.getElementById('multi-agent-container');
    const agentName = MultiAgent.getAgentName(agentId);

    // Check if agent column already exists (prevent duplicates)
    const existingColumn = document.getElementById(`agent-column-${agentId}`);
    if (existingColumn) {
        console.log(`[Multi-Agent] Agent ${agentName} already exists, skipping creation`);
        return;
    }

    // Generate session ID for this agent if not exists
    if (!MultiAgent.sessions[agentId]) {
        MultiAgent.sessions[agentId] = generateSessionId();
    }

    // Use AgentColumn.create() to generate expandable input container structure
    let column;
    if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.create === 'function') {
        column = AgentColumn.create(agentId, agentName);
    } else {
        console.error(`[createAgentColumn] AgentColumn module not loaded, cannot create agent ${agentId}`);
        return;
    }

    // Insert before the add-agent-bar (if it exists), otherwise just append
    const addAgentBar = container.querySelector('.add-agent-bar');
    if (addAgentBar) {
        container.insertBefore(column, addAgentBar);
    } else {
        container.appendChild(column);
    }

    // Add click handler to column to mark badge as viewed (deactivate pulse)
    column.addEventListener('click', () => {
        const badge = document.getElementById(`quick-nav-badge-${agentId}`);
        if (badge) {
            badge.classList.remove('has-new-message');
            badge.classList.remove('message-complete');  // ✨ Remove green completion indicator
            badge.dataset.viewed = 'true';
            console.log(`[Agent ${agentId}] Column clicked - removed completion indicator`);
        }
    });

    // Enable workflow slug drag-and-drop on NEW textarea ID (agent-input-{agentId})
    const textarea = document.getElementById(`agent-input-${agentId}`);
    if (textarea) {
        setupWorkflowSlugDropTarget(textarea, agentId);
    }

    // Setup expandable input handlers (NEW - Prime-style)
    if (typeof AgentInput !== 'undefined' && typeof AgentInput.setupHandlers === 'function') {
        AgentInput.setupHandlers(agentId);
        console.log(`[createAgentColumn] Agent-${agentId} expandable input handlers initialized`);
    }

    // Setup file input handler
    setupAgentFileInput(agentId);
}

// Setup file input change handler for agent
function setupAgentFileInput(agentId) {
    const fileInput = document.getElementById(`agent-file-input-${agentId}`);
    const attachBtn = document.getElementById(`agent-attach-${agentId}`);

    if (!fileInput || !attachBtn) return;

    // Attach button clicks file input
    attachBtn.addEventListener('click', () => {
        fileInput.click();
    });

    // File selection handled by AgentInput.setupHandlers
    console.log(`[setupAgentFileInput] Agent-${agentId} file input configured`);
}

// Setup drag-and-drop for workflow slugs on agent textarea
function setupWorkflowSlugDropTarget(textarea, agentId) {
    textarea.addEventListener('dragover', (e) => {
        // Check if dragging a workflow slug
        const types = e.dataTransfer.types;
        if (types.includes('workflow-slug')) {
            e.preventDefault();
            textarea.classList.add('drag-over');
        }
    });

    textarea.addEventListener('dragleave', () => {
        textarea.classList.remove('drag-over');
    });

    textarea.addEventListener('drop', (e) => {
        const workflowSlug = e.dataTransfer.getData('workflow-slug');
        const workflowId = e.dataTransfer.getData('workflow-id');

        if (workflowSlug) {
            e.preventDefault();
            textarea.classList.remove('drag-over');

            // Inject workflow designer system prompt
            injectWorkflowDesignerPrompt(textarea, agentId, workflowSlug, workflowId);
        }
    });
}

// Inject workflow designer context when slug is dropped
function injectWorkflowDesignerPrompt(textarea, agentId, slug, workflowId) {
    // Store workflow context for this agent (will be injected in system prompt)
    if (!window.agentWorkflowContext) {
        window.agentWorkflowContext = {};
    }
    window.agentWorkflowContext[agentId] = {
        slug: slug,
        workflowId: workflowId,
        mode: 'designer',
        activated: new Date().toISOString()
    };

    // Show visual indicator in UI
    const statusBadge = document.getElementById(`status-${agentId}`);
    if (statusBadge) {
        const originalHTML = statusBadge.innerHTML;
        statusBadge.innerHTML = `<i class="fas fa-project-diagram"></i> Workflow Designer: ${slug}`;
        statusBadge.style.background = 'rgba(88, 166, 255, 0.15)';
        statusBadge.style.color = '#58a6ff';
    }

    // Set placeholder to show workflow context
    textarea.placeholder = `Design workflow [${slug}]... (AI Workflow Designer Mode active)`;
    textarea.focus();

    console.log(`? Workflow Designer Mode activated for agent ${agentId}, workflow: ${slug}`);
    console.log(`   Context will be injected in system prompt on next message`);
}

// Handle file selection for agent columns
function handleAgentFileSelection(agentId, files) {
    if (!window.agentAttachedFiles[agentId]) {
        window.agentAttachedFiles[agentId] = [];
    }

    for (let file of files) {
        // Check file type
        const _nativeTypes = new Set(['application/pdf','image/png','image/jpeg','image/jpg','image/gif','image/webp']);
        const _extractableTypes = new Set([
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/msword','application/vnd.ms-excel','application/vnd.ms-powerpoint',
            'text/plain','text/csv','text/markdown','text/html','text/css',
            'application/json','application/xml','text/xml',
            'application/javascript','text/javascript','text/x-python',
            'application/x-python','application/x-sh','text/x-sh','application/rtf','text/rtf'
        ]);
        const _extractableExts = new Set(['docx','doc','xlsx','xls','pptx','ppt','txt','csv','md','html','htm','css','json','xml','js','ts','py','sh','rb','java','cpp','c','cs','go','rs','rtf']);
        const _fileExt = (file.name.split('.').pop() || '').toLowerCase();
        const _isNative = _nativeTypes.has(file.type);
        const _isExtractable = _extractableTypes.has(file.type) || _extractableExts.has(_fileExt);
        if (!_isNative && !_isExtractable) {
            showNotification(`Unsupported file type: ${file.name}. Supported: PDF, images, Word, Excel, PowerPoint, text and code files.`, 'error');
            continue;
        }

        // Check file size: 32MB for PDF, 5MB for images, 20MB for extractable
        let maxSize;
        if (file.type === 'application/pdf') { maxSize = 32 * 1024 * 1024; }
        else if (_isNative && file.type.startsWith('image/')) { maxSize = 5 * 1024 * 1024; }
        else { maxSize = 20 * 1024 * 1024; }
        if (file.size > maxSize) {
            showNotification(`File too large: ${file.name}. Max size: ${maxSize / 1024 / 1024} MB`, 'error');
            continue;
        }

        window.agentAttachedFiles[agentId].push(file);
    }

    updateAgentAttachedFilesUI(agentId);

    // Reset file input
    const fileInput = document.getElementById(`agent-file-input-${agentId}`) || document.getElementById(`file-input-${agentId}`);
    if (fileInput) fileInput.value = '';
}

// Update attached files UI for agent
function updateAgentAttachedFilesUI(agentId) {
    const container = document.getElementById(`agent-attached-files-${agentId}`);
    if (!container) return;

    const files = window.agentAttachedFiles[agentId] || [];
    container.innerHTML = '';

    files.forEach((file, index) => {
        const chip = document.createElement('div');
        chip.className = 'agent-file-chip';

        const icon = file.type === 'application/pdf' ? 'fa-file-pdf' : 'fa-image';
        const size = (file.size / 1024).toFixed(1);

        chip.innerHTML = `
            < i class="fas ${icon}" ></i >
                    <span>${file.name} (${size}KB)</span>
                    <button class="agent-file-chip-remove" data-index="${index}">×</button>
        `;

        chip.querySelector('.agent-file-chip-remove').addEventListener('click', () => {
            window.agentAttachedFiles[agentId].splice(index, 1);
            updateAgentAttachedFilesUI(agentId);
        });

        container.appendChild(chip);
    });

    // Update padding when files change (if input is focused)
    const textarea = document.getElementById(`agent-input-${agentId}`) || document.getElementById(`input-${agentId}`);
    const messagesContainer = document.querySelector(`#agent-column-${agentId} .agent-messages-container`);
    const inputContainer = document.querySelector(`#agent-column-${agentId} .agent-input-container`);
    if (textarea === document.activeElement && messagesContainer && inputContainer) {
        setTimeout(() => {
            const inputHeight = inputContainer.offsetHeight;
            messagesContainer.style.paddingBottom = `${inputHeight + LAYOUT_CONSTANTS.PADDING_BUFFER}px`;
        }, 0);
    }
}

// Clear attached files for agent
function clearAgentAttachedFiles(agentId) {
    if (window.agentAttachedFiles && window.agentAttachedFiles[agentId]) {
        window.agentAttachedFiles[agentId] = [];
        updateAgentAttachedFilesUI(agentId);

        // Update padding when files are cleared (if input is focused)
        const textarea = document.getElementById(`agent-input-${agentId}`) || document.getElementById(`input-${agentId}`);
        const messagesContainer = document.querySelector(`#agent-column-${agentId} .agent-messages-container`);
        const inputContainer = document.querySelector(`#agent-column-${agentId} .agent-input-container`);
        if (textarea === document.activeElement && messagesContainer && inputContainer) {
            setTimeout(() => {
                const inputHeight = inputContainer.offsetHeight;
                messagesContainer.style.paddingBottom = `${inputHeight + LAYOUT_CONSTANTS.PADDING_BUFFER}px`;
            }, 0);
        }
    }
}

function createAddAgentBar() {
    console.log('[Multi-Agent] createAddAgentBar() called');

    const existingBar = document.querySelector('.add-agent-bar');
    if (existingBar) {
        console.log('[Multi-Agent] Add Agent bar already exists, skipping creation');
        return;
    }

    const bar = document.createElement('div');
    bar.className = 'add-agent-bar';
    bar.onclick = addAgentColumn;
    bar.innerHTML = `
            <div class="add-agent-bar-content">
                <i class="fas fa-plus"></i>
                    ADD AGENT
                </div>
            `;

    // Append to multi-agent-container (as last flex item)
    const container = document.getElementById('multi-agent-container');
    console.log('[Multi-Agent] Container found?', !!container);

    if (container) {
        container.appendChild(bar);
        console.log('[Multi-Agent] ✅ Add Agent bar appended to container');

        // Check if multi-agent tab is visible right now (most reliable method)
        setTimeout(() => {
            const multiAgentTabActive = document.getElementById('tab-multi-agent')?.classList.contains('active');
            console.log('[Multi-Agent] Multi-agent tab DOM active?', multiAgentTabActive);
            console.log('[Multi-Agent] AppState.currentTab:', AppState?.currentTab);

            // If multi-agent tab DOM is active OR AppState says so, show the bar
            if (multiAgentTabActive || AppState?.currentTab === 'multi-agent') {
                bar.classList.add('visible');
                console.log('[Multi-Agent] ✅ Add Agent bar set to VISIBLE');
            } else {
                console.log('[Multi-Agent] ⚠️ Multi-agent tab NOT active, bar will be hidden');
            }
        }, 200);
    } else {
        console.error('[Multi-Agent] ❌ Container #multi-agent-container NOT FOUND');
    }
}

function addAgentColumn() {
    // Count actual visible columns (not nextAgentId) so closing a column re-enables adding
    const activeCount = document.querySelectorAll('#multi-agent-container .agent-column').length;
    if (activeCount >= 26) {
        showNotification('Command Centre is full (26/26) — close a column to add a new one', 'warning');
        return;
    }

    const agentId = MultiAgent.nextAgentId++;
    createAgentColumn(agentId);

    // Disable bar if we just hit the 26-column limit
    const newCount = document.querySelectorAll('#multi-agent-container .agent-column').length;
    if (newCount >= 26) {
        const bar = document.querySelector('.add-agent-bar');
        if (bar) bar.classList.add('disabled');
    }

    // [LOCK] IMMEDIATE WIDTH ENFORCEMENT: Ensure new column starts at 400px
    setTimeout(() => {
        const column = document.getElementById(`agent-${agentId}`);
        const icon = document.getElementById(`width-icon-${agentId}`);
        if (column) {
            column.classList.remove('wide');
            // Set icon to chevron-right for default 400px width
            if (icon) {
                icon.className = 'fas fa-chevron-right';
            }
            console.log(`[LOCK][NEW COLUMN] ${getAgentName(agentId)} enforced to 400px default width`);
        }
    }, 50);

    // ✅ CRITICAL FIX: Re-setup drag/drop zones for the new column
    // Without this, newly created columns won't accept dropped threads
    if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.setupAgentDropZones === 'function') {
        setTimeout(() => {
            ThreadManager.setupAgentDropZones();
            console.log(`✅ [addAgentColumn] Re-initialized drop zones for agent-${agentId}`);
        }, 100);
    }

    // Add badge to quick-nav bar
    MultiAgent.addQuickNavBadge(agentId);

    showNotification(`Agent ${getAgentName(agentId)} added!`, 'success');
}

function getAgentName(agentId) {
    return MultiAgent.getAgentName(agentId);
}

// Show dialog to load thread into agent
function showLoadThreadDialog(agentId) {
    const agentName = MultiAgent.getAgentName(agentId);
    const modal = document.getElementById('confirmation-modal');
    const titleEl = document.getElementById('confirmation-title');
    const messageEl = document.getElementById('confirmation-message');
    const confirmBtn = document.getElementById('confirmation-btn');

    titleEl.textContent = `Load Thread into ${agentName} `;
    messageEl.innerHTML = `
            < div style = "margin-bottom: 12px;" > Enter Session ID to load:</div >
                <input type="text" 
                       id="agent-load-session-input" 
                       class="session-loader-input" 
                       placeholder="Paste session ID here..." 
                       style="width: 100%; margin-bottom: 12px;" />
                <div style="font-size: 12px; color: var(--text-secondary);">
                    <i class="fas fa-info-circle"></i> Copy a session ID from the thread menu in the main AI chat.
                </div>
        `;

    confirmBtn.innerHTML = '<i class="fas fa-download"></i> Load Thread';
    confirmBtn.style.background = '#3b82f6';

    modal.classList.add('active');

    // Focus input after modal opens
    setTimeout(() => {
        document.getElementById('agent-load-session-input')?.focus();
    }, 100);

    confirmBtn.onclick = () => {
        const sessionId = document.getElementById('agent-load-session-input')?.value.trim();
        if (sessionId) {
            loadThreadIntoAgent(agentId, sessionId);
        }
        closeConfirmation();
    };
}

// Load thread into specific agent
async function loadThreadIntoAgent(agentId, sessionId) {
    // Find thread by session ID
    const thread = Array.isArray(ThreadManager.threads) ? ThreadManager.threads.find(t => t.id === sessionId) : null;

    if (!thread) {
        showNotification('Thread not found. Check the session ID.', 'error', 3000);
        return;
    }

    const agentName = MultiAgent.getAgentName(agentId);

    // Check if this thread was in AI Prime - if so, clear Prime
    if (ThreadManager.currentThreadId === sessionId) {
        console.log(`[THREAD MOVE] Thread moved from Prime to ${agentName} - clearing Prime`);

        // Clear Prime's current thread
        ThreadManager.currentThreadId = null;

        // Clear Prime thread info container
        const primeThreadInfo = document.getElementById('prime-thread-info');
        if (primeThreadInfo) {
            primeThreadInfo.innerHTML = '';
        }

        // Show welcome container in Prime
        const welcomeContainer = document.getElementById('prime-welcome-container');
        if (welcomeContainer) {
            welcomeContainer.style.display = 'flex';
            ThreadManager.initWelcomeMessage('prime');
        }

        console.log(`[THREAD MOVE] Prime cleared and welcome message shown`);
    }

    // Load messages into agent - READ FROM MESSAGESTORE
    const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
    if (messagesContainer) {
        // Clear only messages, preserve scroll controls
        const oldMessages = messagesContainer.querySelectorAll('.ai-message');
        oldMessages.forEach(msg => msg.remove());

        // Get messages from MessageStore (centralized storage)
        const messages = window.MessageStore.getMessages(thread.id);
        console.log(`📦 [MessageStore] Loading ${messages.length} messages into Agent ${agentId} from thread ${thread.id}`);

        // CRITICAL FIX (Jan 4, 2026): FORCE SEQUENTIAL RENDERING WITH BATCHING
        // TwoRuleStreamProcessor synchronous DOM operations can overwhelm browser
        // Solution: Render in batches of 10, with delays between batches
        const BATCH_SIZE = 10;
        const BATCH_DELAY_MS = 100; // Delay between batches to let DOM settle
        const MESSAGE_DELAY_MS = 10; // Tiny delay between messages for forced order

        console.log(`[LOAD] 🔄 Starting BATCHED render of ${messages.length} messages (${BATCH_SIZE} per batch)`);

        // Add loading indicator
        const loadingIndicator = document.createElement('div');
        loadingIndicator.style.cssText = 'padding: 20px; text-align: center; color: #666; font-style: italic; background: #f0f0f0; border-radius: 8px; margin: 10px 0;';
        loadingIndicator.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Loading messages... <span id="load-progress">0/${messages.length}</span>`;
        messagesContainer.appendChild(loadingIndicator);

        for (let batchStart = 0; batchStart < messages.length; batchStart += BATCH_SIZE) {
            const batchEnd = Math.min(batchStart + BATCH_SIZE, messages.length);
            const batchNum = Math.floor(batchStart / BATCH_SIZE) + 1;
            const totalBatches = Math.ceil(messages.length / BATCH_SIZE);

            console.log(`[LOAD] 📦 Batch ${batchNum}/${totalBatches}: Rendering messages ${batchStart + 1}-${batchEnd}`);

            for (let index = batchStart; index < batchEnd; index++) {
                const msg = messages[index];

                try {
                    console.log(`[LOAD] 🎯 Message ${index + 1}/${messages.length} (${msg.role}) - RENDER START`);

                    if (typeof UnifiedMessageRenderer !== 'undefined') {
                        // PRIME PATHWAY: Use UnifiedMessageRenderer for proper content block handling
                        const renderResult = await UnifiedMessageRenderer.render(
                            messagesContainer,
                            msg.role,
                            msg.content,
                            {
                                threadId: thread.id,
                                syncToBackend: false,
                                scrollToBottom: false,  // Manual scroll at end
                                createdAt: msg.created_at,
                                messageId: msg.id  // CRITICAL: Pass message ID from database
                            }
                        );

                        if (renderResult) {
                            console.log(`[LOAD] ✅ Message ${index + 1} RENDERED SUCCESSFULLY`);
                        } else {
                            console.log(`[LOAD] ⏭️ Message ${index + 1} SKIPPED (duplicate or tool_result-only)`);
                        }

                        // FORCE DOM UPDATE: Tiny delay to ensure message appears in correct order
                        await new Promise(resolve => setTimeout(resolve, MESSAGE_DELAY_MS));

                    } else {
                        console.warn(`[LOAD] ⚠️ UnifiedMessageRenderer not available! Using improved fallback renderer`);

                        // IMPROVED FALLBACK RENDERER: Handle structured content blocks
                        const messageDiv = document.createElement('div');
                        messageDiv.className = `ai-message ${msg.role === 'user' ? 'user' : 'assistant'}`;
                        messageDiv.dataset.messageId = msg.id;

                        const contentDiv = document.createElement('div');
                        contentDiv.className = 'agent-message-bubble';

                        if (typeof msg.content === 'string') {
                            // Simple string content
                            contentDiv.textContent = msg.content;
                            console.log(`[LOAD] Rendered string content (${msg.content.length} chars)`);

                        } else if (Array.isArray(msg.content)) {
                            // CRITICAL FIX: Handle array content blocks properly
                            let hasVisibleContent = false;

                            msg.content.forEach((block, blockIdx) => {
                                console.log(`[LOAD]   Block ${blockIdx + 1}: type=${block.type}`);

                                if (block.type === 'thinking' && block.thinking) {
                                    // Render thinking block with icon
                                    const thinkingDiv = document.createElement('div');
                                    thinkingDiv.className = 'content-block thinking-block';
                                    thinkingDiv.innerHTML = `
                                <div style="display: flex; align-items: center; gap: 8px; color: #888; font-style: italic; margin-bottom: 8px;">
                                    <i class="fas fa-brain"></i>
                                    <span style="font-size: 0.9em;">Extended Thinking</span>
                                </div>
                                <div style="font-size: 0.85em; color: #666; border-left: 2px solid #ddd; padding-left: 12px;">
                                    ${block.thinking.substring(0, 200)}${block.thinking.length > 200 ? '...' : ''}
                                </div>
                            `;
                                    contentDiv.appendChild(thinkingDiv);
                                    hasVisibleContent = true;

                                } else if (block.type === 'tool_use' && block.name) {
                                    // Render tool_use block with icon
                                    const toolDiv = document.createElement('div');
                                    toolDiv.className = 'content-block tool-use-block';
                                    toolDiv.innerHTML = `
                                <div style="display: flex; align-items: center; gap: 8px; color: #4a90e2; font-weight: 500; margin-bottom: 4px;">
                                    <i class="fas fa-cog"></i>
                                    <span>Tool: ${block.name}</span>
                                </div>
                                <div style="font-size: 0.85em; color: #666; margin-left: 24px;">
                                    ${JSON.stringify(block.input || {}, null, 2).substring(0, 100)}${JSON.stringify(block.input || {}).length > 100 ? '...' : ''}
                                </div>
                            `;
                                    contentDiv.appendChild(toolDiv);
                                    hasVisibleContent = true;

                                } else if (block.type === 'text' && block.text) {
                                    // Render text block
                                    const textDiv = document.createElement('div');
                                    textDiv.className = 'content-block text-block';
                                    textDiv.style.marginTop = '8px';
                                    textDiv.textContent = block.text;
                                    contentDiv.appendChild(textDiv);
                                    hasVisibleContent = true;

                                } else if (block.type === 'tool_result') {
                                    // Render tool_result block (shouldn't be in assistant messages, but handle gracefully)
                                    const resultDiv = document.createElement('div');
                                    resultDiv.className = 'content-block tool-result-block';
                                    resultDiv.innerHTML = `
                                <div style="display: flex; align-items: center; gap: 8px; color: #e6edf3; font-weight: 500; margin-bottom: 4px;">
                                    <i class="fas fa-check-circle"></i>
                                    <span>Tool Result</span>
                                </div>
                            `;
                                    contentDiv.appendChild(resultDiv);
                                    hasVisibleContent = true;
                                }
                            });

                            if (!hasVisibleContent) {
                                console.warn(`[LOAD] ⚠️ Message ${index + 1} has array content but no renderable blocks!`);
                                contentDiv.innerHTML = `<em style="color: #999;">[Message with ${msg.content.length} content blocks]</em>`;
                            } else {
                                console.log(`[LOAD] ✅ Rendered ${msg.content.length} content blocks`);
                            }

                        } else {
                            // Unknown format - stringify
                            contentDiv.textContent = String(msg.content);
                            console.warn(`[LOAD] ⚠️ Unknown content format: ${typeof msg.content}`);
                        }

                        messageDiv.appendChild(contentDiv);
                        messagesContainer.appendChild(messageDiv);
                    }

                    // Update progress indicator
                    document.getElementById('load-progress').textContent = `${index + 1}/${messages.length}`;

                } catch (renderError) {
                    console.error(`[LOAD] ❌ Failed to render message ${index + 1} (ID: ${msg.id}):`, renderError);
                    console.error('[LOAD]   Message role:', msg.role);
                    console.error('[LOAD]   Content type:', Array.isArray(msg.content) ? `array[${msg.content.length}]` : typeof msg.content);

                    // Create error placeholder so user knows a message failed
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'ai-message assistant error';
                    errorDiv.innerHTML = `
                    <div class="ai-message-content" style="background: #ffebee; border: 1px solid #ef5350; padding: 10px; border-radius: 4px;">
                        <div style="color: #c62828; font-weight: 500;">⚠️ Message Rendering Error</div>
                        <div style="font-size: 0.85em; color: #666; margin-top: 5px;">
                            Message #${index + 1} (ID: ${msg.id}) failed to render. Check console for details.
                        </div>
                    </div>
                `;
                    messagesContainer.appendChild(errorDiv);

                    // Continue with next message instead of stopping the loop
                    console.log('[LOAD] Continuing with next message...');
                }
            } // End of batch message loop

            // BATCH DELAY: Give DOM time to settle before next batch
            if (batchEnd < messages.length) {
                console.log(`[LOAD] 🛑 Batch ${batchNum} complete. Pausing ${BATCH_DELAY_MS}ms before next batch...`);
                await new Promise(resolve => setTimeout(resolve, BATCH_DELAY_MS));
            }

        } // End of batch loop

        // Remove loading indicator
        loadingIndicator.remove();
        console.log(`[LOAD] ✅ ALL ${messages.length} messages rendered successfully in ${Math.ceil(messages.length / BATCH_SIZE)} batches`);

        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Update agent thread info
    const messageCount = thread.messages ? thread.messages.length : 0;
    const metadata = {
        synergyCardId: thread.synergy_card_id || null,
        synergySessionName: thread.synergy_card_name || null,
        workflowId: thread.workflow_id || null,
        automationId: thread.automation_id || null
    };
    MultiAgent.setLoadedThread(agentId, thread.id, thread.title, messageCount, metadata);

    // Update thread's agent assignment
    thread.agent = `multi-agent-${agentId}`;
    // Note: Thread saved via backend API, no manual save needed

    console.log(`Thread "${thread.title}" loaded into ${agentName}`);
    showNotification(`Thread loaded into ${agentName}`, 'success', 2000);
}

function toggleAgentMenu(agentId) {
    const menu = document.getElementById(`menu-${agentId}`);
    const button = event.currentTarget;
    const allMenus = document.querySelectorAll('.agent-menu-dropdown');

    // Check if menu exists
    if (!menu) {
        console.error(`Menu not found for agent ${agentId}`);
        return;
    }

    // Close all other menus
    allMenus.forEach(m => {
        if (m.id !== `menu-${agentId} `) {
            m.classList.remove('show');
        }
    });

    // Toggle visibility
    const isShowing = menu.classList.toggle('show');

    // If showing, calculate position relative to button
    if (isShowing && button) {
        const buttonRect = button.getBoundingClientRect();

        // Position dropdown: 195px to the LEFT of button's left edge, 50px BELOW button's top edge
        menu.style.top = `${buttonRect.top + 50} px`;
        menu.style.left = `${buttonRect.left - 195} px`;
        menu.style.right = 'auto';

        console.log(`Menu positioned: top = ${menu.style.top}, left = ${menu.style.left}, buttonRect: `, buttonRect);
    }
}

/**
 * Filter content blocks for API requests
 * 
 * CRITICAL: Remove thinking and tool_result blocks before sending to Claude API
 * - thinking blocks cause format errors ("first block must be thinking")
 * - tool_result blocks are too verbose and not needed for context
 * 
 * Keep only:
 * - text blocks (main response content)
 * - tool_use blocks (shows what tools AI requested)
 * 
 * This matches the backend filtering in agent_worker.py
 */
function filterContentForAPI(content) {
    if (typeof content === 'string') {
        // Simple text content - return as-is
        return content;
    }

    if (Array.isArray(content)) {
        // Content blocks array - filter out ONLY thinking blocks
        // CRITICAL: Must keep tool_result! Claude API requires tool_use + tool_result pairs
        return content.filter(block =>
            block.type === 'text' ||
            block.type === 'tool_use' ||
            block.type === 'tool_result'  // KEEP tool_result (was missing!)
        );
    }

    // Unknown format - return as-is
    return content;
}

/**
 * Build properly formatted conversation history for Anthropic API
 * PATTERN: Based on AnythingLLM's #prepareMessages method
 * 
 * CRITICAL FIXES:
 * 1. Converts tool_result from assistant messages to user messages
 * 2. Adds default text to assistant messages with tool_use but no text
 * 3. Ensures proper message alternation (assistant → user → assistant)
 * 4. Ensures first message is from user
 * 5. Merges consecutive messages from same role
 * 
 * Input format (saved in DB):
 *   assistant: [thinking, tool_use]
 *   user: [tool_result]  ← Already separate in DB!
 *   assistant: [thinking, text]
 * 
 * Output format (for Anthropic API):
 *   Same structure, but validated and cleaned
 */
function buildConversationHistoryForAPI(messages) {
    console.log(`[BUILD API HISTORY] Processing ${messages.length} messages for Anthropic API...`);
    const result = [];

    messages.forEach((msg, index) => {
        if (msg.role === 'user') {
            // User messages: keep as-is, but normalize content
            let userContent;
            if (typeof msg.content === 'string') {
                userContent = msg.content;
            } else if (Array.isArray(msg.content)) {
                // Check if this is a tool_result message (array of tool_result blocks)
                const toolResultBlocks = msg.content.filter(b => b.type === 'tool_result');
                if (toolResultBlocks.length > 0) {
                    // This is a tool_result message - keep as array
                    userContent = toolResultBlocks;
                } else {
                    // This is a text message - extract and deduplicate text
                    const textBlocks = msg.content.filter(b => b.type === 'text');
                    const uniqueTexts = [];
                    const seenTexts = new Set();

                    textBlocks.forEach(block => {
                        const text = block.text || block.content || '';
                        if (text && !seenTexts.has(text)) {
                            seenTexts.add(text);
                            uniqueTexts.push(text);
                        }
                    });

                    userContent = uniqueTexts.join('\n') || JSON.stringify(msg.content);

                    if (textBlocks.length > uniqueTexts.length) {
                        console.warn(`[DEDUP] User message had ${textBlocks.length} text blocks, deduplicated to ${uniqueTexts.length}`);
                    }
                }
            } else {
                userContent = String(msg.content);
            }

            result.push({
                role: 'user',
                content: userContent
            });
        } else if (msg.role === 'assistant') {
            // Assistant messages: validate and normalize
            if (typeof msg.content === 'string') {
                // Simple text - keep as-is
                result.push({ role: 'assistant', content: msg.content });
            } else if (Array.isArray(msg.content)) {
                // Structured content - validate and order properly
                const thinkingBlocks = msg.content.filter(b => b.type === 'thinking');
                const toolUseBlocks = msg.content.filter(b => b.type === 'tool_use');
                const textBlocks = msg.content.filter(b => b.type === 'text');

                // Filter out empty text blocks (Anthropic requirement)
                const nonEmptyTextBlocks = textBlocks.filter(block => {
                    const text = block.text || block.content || '';
                    return text.trim().length > 0;
                });

                // Build assistant content array: [thinking, tool_use, text]
                const assistantContent = [];

                // 1. Add thinking blocks first
                if (thinkingBlocks.length > 0) {
                    thinkingBlocks.forEach(block => {
                        const preservedBlock = {
                            type: block.type,
                            thinking: block.thinking || block.content || ''
                        };
                        if (block.signature) {
                            preservedBlock.signature = block.signature;
                        }
                        assistantContent.push(preservedBlock);
                    });
                }

                // 2. Add tool_use blocks
                if (toolUseBlocks.length > 0) {
                    assistantContent.push(...toolUseBlocks);
                }

                // 3. Add text blocks (only non-empty)
                if (nonEmptyTextBlocks.length > 0) {
                    assistantContent.push(...nonEmptyTextBlocks);
                }

                // ANYTHINGLLM PATTERN: If assistant has tool_use but no text, add default text
                if (toolUseBlocks.length > 0 && nonEmptyTextBlocks.length === 0) {
                    assistantContent.push({
                        type: 'text',
                        text: "I'll use a tool to help answer this question."
                    });
                    console.log(`[FIX] Added default text to assistant message with tool_use`);
                }

                // Push assistant message if it has content
                if (assistantContent.length > 0) {
                    result.push({
                        role: 'assistant',
                        content: assistantContent
                    });
                }
            } else {
                // Unknown format - keep as-is
                result.push({ role: 'assistant', content: msg.content });
            }
        }
    });

    // ANYTHINGLLM PATTERN: Ensure first message is from user
    if (result.length > 0 && result[0].role !== 'user') {
        console.warn(`[FIX] First message was ${result[0].role}, removing it (Anthropic requires first message to be from user)`);
        result.shift();
    }

    // ANYTHINGLLM PATTERN: Merge consecutive messages from same role
    const merged = [];
    result.forEach(msg => {
        const lastMsg = merged[merged.length - 1];
        if (lastMsg && lastMsg.role === msg.role) {
            // Merge with previous message of same role
            console.log(`[FIX] Merging consecutive ${msg.role} messages`);
            if (Array.isArray(lastMsg.content) && Array.isArray(msg.content)) {
                lastMsg.content.push(...msg.content);
            } else if (typeof lastMsg.content === 'string' && typeof msg.content === 'string') {
                lastMsg.content += '\n' + msg.content;
            } else {
                // Mixed types - convert both to arrays
                const lastContent = Array.isArray(lastMsg.content) ? lastMsg.content : [{ type: 'text', text: lastMsg.content }];
                const msgContent = Array.isArray(msg.content) ? msg.content : [{ type: 'text', text: msg.content }];
                lastMsg.content = [...lastContent, ...msgContent];
            }
        } else {
            merged.push(msg);
        }
    });

    console.log(`[BUILD API HISTORY] Result: ${merged.length} messages (${result.length - merged.length} merged)`);
    console.log(`[BUILD API HISTORY] Message roles:`, merged.map((m, i) => `${i}: ${m.role}${Array.isArray(m.content) ? '(' + m.content.map(b => b.type).join(',') + ')' : '(text)'}`).join(' | '));
    return merged;
}

// CRITICAL: Expose buildConversationHistoryForAPI globally for prime_ai_chat.js and other modules
window.buildConversationHistoryForAPI = buildConversationHistoryForAPI;

function closeAgentColumn(agentId) {
    // Simple confirmation dialog
    if (!confirm(`Close ${getAgentName(agentId)}?\n\nThis will close the agent column and unload the thread. The thread will remain visible in the Threads Catalogue.`)) {
        return;
    }

    const column = document.getElementById(`agent-${agentId}`);
    if (column) {
        // Clean up visualization processors before removing
        column.querySelectorAll('[data-processor-initialized]').forEach(bubble => {
            if (bubble.processor && typeof bubble.processor.cleanup === 'function') {
                bubble.processor.cleanup();
                console.log(`[CLEAN] Cleaned up processor for Agent ${agentId}`);
            }
        });

        column.remove();
        delete MultiAgent.sessions[agentId];
        delete MultiAgent.streams[agentId];
        delete MultiAgent.loadedThreads[agentId];

        // Remove badge from quick-nav bar
        MultiAgent.removeQuickNavBadge(agentId);

        // Re-enable add bar now that a slot is free
        const bar = document.querySelector('.add-agent-bar');
        if (bar) bar.classList.remove('disabled');

        // Show notification if available
        if (typeof window.showNotification === 'function') {
            window.showNotification(`Agent ${getAgentName(agentId)} closed`, 'info');
        }
    }
}

function newChat(agentId) {
    const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
    if (messagesContainer) {
        // Clean up any existing processors
        messagesContainer.querySelectorAll('[data-processor-initialized]').forEach(bubble => {
            if (bubble.processor && typeof bubble.processor.cleanup === 'function') {
                bubble.processor.cleanup();
            }
        });

        messagesContainer.innerHTML = `
            < div class="agent-message assistant" >
                <div class="agent-message-bubble">
                     <strong>Agent ${getAgentName(agentId)} ready!</strong><br><br>
                        New conversation started!
                    </div>
                </div>
        `;
    }

    // Reset session
    MultiAgent.sessions[agentId] = generateSessionId();
    toggleAgentMenu(agentId);
    showNotification('New chat started', 'success');
}

function handleAgentKeypress(event, agentId) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendAgentMessage(agentId);
    }
}

// ============================================================
// REALTIME: Cross-session agent message sync (Socket.IO -> DOM event)
// ============================================================

(function setupAgentThreadRealtimeSync() {
    if (window.__agentThreadRealtimeSyncInstalled) return;
    window.__agentThreadRealtimeSyncInstalled = true;

    // Deduplicate rapid-fire updates (same agent/thread) within a short window
    const recentRefreshes = new Map(); // key -> timestamp
    const REFRESH_DEDUP_MS = 1500;

    window.addEventListener('synergyrealtime:agent_thread_updated', async (evt) => {
        try {
            const data = (evt && evt.detail) ? evt.detail : {};
            const updatedAgentId = data.agent_id || data.agentId;
            const threadSlug = data.thread_slug || data.threadSlug;

            if (!updatedAgentId || !threadSlug) return;
            if (typeof window.MultiAgent === 'undefined' || typeof window.ThreadManager === 'undefined') return;
            if (typeof ThreadManager.loadMessagesForThread !== 'function') return;

            const dedupKey = `${updatedAgentId}:${threadSlug}`;
            const last = recentRefreshes.get(dedupKey);
            if (last && (Date.now() - last) < REFRESH_DEDUP_MS) {
                return;
            }
            recentRefreshes.set(dedupKey, Date.now());

            const agentIdNum = parseInt(updatedAgentId);
            if (Number.isNaN(agentIdNum)) return;

            // Ensure ThreadManager has a current view of thread assignments (location fields)
            if (!ThreadManager.threadsLoaded && typeof ThreadManager.loadThreadsFromBackend === 'function') {
                await ThreadManager.loadThreadsFromBackend();
            }

            // AUTHORITATIVE APPLY:
            // When a thread update arrives for agent-X + threadSlug, make this browser's
            // agent-X column reflect that thread (even if empty or currently showing another thread).
            const expectedLocation = `agent-${agentIdNum}`;
            const loadedInfo = MultiAgent.loadedThreads?.[agentIdNum];
            const isEmptyAgentHere = !loadedInfo || !loadedInfo.threadId;
            const isDifferentThreadLoaded = !!loadedInfo?.threadId && loadedInfo.threadId !== threadSlug;

            if (isEmptyAgentHere || isDifferentThreadLoaded) {
                // Try to locate thread metadata from ThreadManager.threads; fall back to a stub.
                let threadMeta = (ThreadManager.threads || []).find(t => t && t.id === threadSlug) || null;

                if (threadMeta) {
                    // Prevent loadThreadIntoAgent() from re-assigning in backend by aligning location.
                    threadMeta = { ...threadMeta, location: expectedLocation };
                } else {
                    threadMeta = {
                        id: threadSlug,
                        title: (loadedInfo && loadedInfo.threadTitle) ? loadedInfo.threadTitle : `Agent ${agentIdNum} Chat`,
                        message_count: data.message_count || 0,
                        location: expectedLocation
                    };
                }

                console.log(`[REALTIME] ✅ Applying thread ${threadSlug} to agent-${agentIdNum} (empty=${isEmptyAgentHere}, switched=${isDifferentThreadLoaded})`);

                // Pull latest messages first so the render uses fresh MessageStore contents.
                await ThreadManager.loadMessagesForThread(threadSlug, null, 0);

                if (typeof MultiAgent.loadThreadIntoAgent === 'function') {
                    MultiAgent.loadThreadIntoAgent(agentIdNum, threadMeta);
                }
            }

            // Refresh only if this browser has the thread loaded in an agent column.
            // Prefer the payload agent_id, but also support cases where the same thread is loaded elsewhere.
            const candidates = [];
            if (MultiAgent.loadedThreads && MultiAgent.loadedThreads[updatedAgentId]?.threadId) {
                candidates.push(parseInt(updatedAgentId));
            }

            if (MultiAgent.loadedThreads) {
                Object.keys(MultiAgent.loadedThreads).forEach((aid) => {
                    const num = parseInt(aid);
                    if (!Number.isNaN(num) && candidates.indexOf(num) === -1) {
                        candidates.push(num);
                    }
                });
            }

            for (const agentId of candidates) {
                const loaded = MultiAgent.loadedThreads?.[agentId];
                if (!loaded || loaded.threadId !== threadSlug) continue;

                console.log(`[REALTIME] 🔄 Refreshing agent-${agentId} thread ${threadSlug} (external update)`);

                // Pull latest messages from backend into MessageStore (source of truth)
                await ThreadManager.loadMessagesForThread(threadSlug, null, 0);

                // Re-render the agent column using existing load pathway (reads from MessageStore)
                const agentName = MultiAgent.getAgentName ? MultiAgent.getAgentName(agentId) : null;
                const thread = (agentName && typeof ThreadManager.getThreadByAgent === 'function')
                    ? ThreadManager.getThreadByAgent(agentName)
                    : null;

                const fallbackThread = ThreadManager.threads
                    ? ThreadManager.threads.find(t => t.id === threadSlug)
                    : null;

                const threadToRender = thread || fallbackThread || {
                    id: threadSlug,
                    title: loaded.threadTitle || `Agent ${agentId} Chat`,
                    message_count: data.message_count || 0,
                    location: `agent-${agentId}`
                };

                if (typeof MultiAgent.loadThreadIntoAgent === 'function') {
                    MultiAgent.loadThreadIntoAgent(agentId, threadToRender);
                }
            }
        } catch (e) {
            console.warn('[REALTIME] Failed to refresh agent thread from realtime update:', e);
        }
    });
})();

async function sendAgentMessage(agentId) {
    // Try new naming convention first (agent-input-*), fall back to old (input-*)
    const input = document.getElementById(`agent-input-${agentId}`) || document.getElementById(`input-${agentId}`);
    const sendBtn = document.getElementById(`agent-send-${agentId}`) || document.getElementById(`send-${agentId}`);

    if (!input) {
        console.error(`[sendAgentMessage] Input not found for agent ${agentId}`);
        return;
    }

    const message = input.value.trim();

    if (!message) return;

    const attachedFiles = window.agentAttachedFiles && window.agentAttachedFiles[agentId] ? window.agentAttachedFiles[agentId] : [];
    const hasFiles = attachedFiles.length > 0;

    const messageToSend = message;
    input.value = '';
    input.style.height = 'auto';
    clearAgentAttachedFiles(agentId);
    
    // Clear attached prompts UI (they'll be cleared from storage after successful send)
    if (window.AgentInput && typeof window.AgentInput.clearPrompts === 'function') {
        window.AgentInput.clearPrompts(agentId);
    }

    // Get thread for this agent
    const agentName = getAgentName(agentId);
    let currentThread = ThreadManager.getThreadByAgent(agentName);
    if (!currentThread) {
        const threadId = ThreadManager.createThread();
        currentThread = ThreadManager.threads.find(t => t.id === threadId);
        currentThread.location = agentName;
        currentThread.title = `${agentName} Chat`;
    }

    // Render user message
    let displayMessage = messageToSend;
    if (hasFiles) {
        const fileList = attachedFiles.map(f => f.name).join(', ');
        displayMessage = `${messageToSend}\n\n*[Attached files: ${fileList}]*`;
    }

    const userMessageDiv = UnifiedMessageRenderer.render(
        `#agent-messages-${agentId}`,
        'user',
        displayMessage,
        {
            threadId: currentThread.id,
            syncToBackend: true,  // ✅ FIX: Save user message to database
            messageId: null  // User-typed message, ID assigned after backend sync
        }
    );
    // console.log(`[Agent ${agentId}] User message rendered`);

    // ✅ BROADCAST: Emit message to other sessions
    if (window.SynergyRealtime && window.SynergyRealtime.socket) {
        window.SynergyRealtime.socket.emit('agent_message_sent', {
            thread_id: currentThread.id,
            agent_id: agentId,
            message: displayMessage,
            role: 'user',
            user_id: window.currentUserId || null,
            session_token: window.SynergyRealtime.sessionToken,
            privacy_mode: window.SynergyRealtime.getPrivacyMode ? window.SynergyRealtime.getPrivacyMode() : 'central',
            team_id: window.SynergyRealtime._getTeamId ? window.SynergyRealtime._getTeamId() : null
        });
        console.log(`📡 [Agent ${agentId}] Broadcasted user message to other sessions (mode: ${window.SynergyRealtime.getPrivacyMode ? window.SynergyRealtime.getPrivacyMode() : 'central'})`);
    }

    // ✅ APPLY VIEW MODE TO USER MESSAGE
    if (userMessageDiv && typeof AgentColumn !== 'undefined' && typeof AgentColumn.applyViewModeToMessage === 'function') {
        AgentColumn.applyViewModeToMessage(agentId, userMessageDiv);
    }

    scrollAgentToBottom(agentId);

    updateAgentStatus(agentId, 'thinking', 'Thinking...');
    if (typeof AgentStatusIndicator !== 'undefined') {
        AgentStatusIndicator.update('thinking', agentId);
    }
    if (sendBtn) {
        sendBtn.disabled = true;
    }

    // Show processing indicator (will be removed when first bubble appears)
    const processingIndicator = createProcessingIndicator(agentId);
    const messagesContainerForIndicator = document.getElementById(`agent-messages-${agentId}`);
    if (messagesContainerForIndicator) {
        messagesContainerForIndicator.appendChild(processingIndicator);
    }

    const startTime = Date.now();
    let requestBody = null; // Declare here for error logging

    // ✅ FIX: Declare threadSlug outside try block so it's accessible in catch
    const threadSlug = currentThread.id;
    const sessionId = threadSlug;

    // ✅ CROSS-SESSION SYNC: Get or create session token
    let mySessionToken = localStorage.getItem('session_token');
    if (!mySessionToken) {
        mySessionToken = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('session_token', mySessionToken);
        console.log(`[Agent ${getAgentName(agentId)}] Created new session token: ${mySessionToken.substr(0, 20)}...`);
    }

    try {
        // ============================================
        // ✅ DATABASE AS SOURCE OF TRUTH
        // ============================================

        if (!MultiAgent.sessions[agentId] || MultiAgent.sessions[agentId] !== sessionId) {
            console.log(`[Agent ${getAgentName(agentId)}] Syncing session_id with thread_slug: ${sessionId}`);
            MultiAgent.sessions[agentId] = sessionId;
        }

        // ❌ REMOVED: Don't build conversation history
        // const storedMessages = window.MessageStore.getMessages(currentThread.id);
        // const conversationHistory = buildConversationHistoryForAPI(storedMessages);

        // ✅ NEW: Backend will load from database
        console.log(`📦 [DATABASE] Backend will load conversation from database for Agent ${agentId}`);

        console.log(`[Agent ${getAgentName(agentId)}] Thread slug: ${threadSlug}`);
        console.log(`[Agent ${getAgentName(agentId)}] Session ID: ${sessionId}`);

        let response;

        if (hasFiles) {
            const workflowContext = window.agentWorkflowContext && window.agentWorkflowContext[agentId];

            const formData = new FormData();
            formData.append('message', message);
            formData.append('session_id', sessionId);
            formData.append('thread_slug', threadSlug);
            formData.append('agent_name', getAgentName(agentId));
            // ❌ REMOVED: formData.append('conversation_history', JSON.stringify(conversationHistory));
            formData.append('thread_id', currentThread.id);
            formData.append('tools_enabled', 'true');
            formData.append('available_tools', ToolManager.availableTools.length);

            if (workflowContext) {
                formData.append('workflow_designer', JSON.stringify({
                    active: true,
                    workflow_slug: workflowContext.slug,
                    workflow_id: workflowContext.workflowId,
                    mode: workflowContext.mode
                }));
            }

            attachedFiles.forEach((file) => {
                formData.append('files', file);
            });

            response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/agent/agent/${agentId}/start`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
                    'X-Session-Token': mySessionToken  // ✅ Add session token
                },
                body: formData
            });
        } else {
            const workflowContext = window.agentWorkflowContext && window.agentWorkflowContext[agentId];

            // ✅ GET PENDING PROMPTS
            const pendingPrompts = window.AgentInput?.getPendingPrompts ? window.AgentInput.getPendingPrompts(agentId) : [];
            let quickActions = [];
            let libraryPrompts = [];
            
            if (pendingPrompts.length > 0) {
                quickActions = pendingPrompts.filter(p => p.type === 'quick_action').map(p => p.name);
                libraryPrompts = pendingPrompts.filter(p => p.type === 'full_prompt').map(p => p.name);
                console.log(`[Agent ${agentId}] Including ${pendingPrompts.length} prompts in request (${quickActions.length} quick, ${libraryPrompts.length} full)`);
            }

            // ✅ SIMPLIFIED REQUEST: No conversation_history
            requestBody = {
                message: message,
                session_id: sessionId,
                thread_slug: threadSlug,
                agent_name: getAgentName(agentId),
                // ❌ REMOVED: conversation_history: conversationHistory,
                thread_id: currentThread.id,
                tools_enabled: true,
                available_tools: ToolManager.availableTools.length,
                google_auth: AuthManager.isAuthenticated ? AuthManager.getAccessToken() : null,
                session_token: mySessionToken,  // ✅ Add session token
                preferences: {
                    use_tools: true,
                    verbose_tool_output: true,
                    streaming: true
                },
                // ✅ NEW: Team ID routing for multi-user collaboration
                sender_team_id: window.UserAuth?.user?.username || null,  // Current user's username
                recipient_team_id: _getRecipientTeamId(),  // Respects privacy mode
                message_type: 'direct',  // User-to-agent message
                privacy_mode: window.SynergyRealtime?.getPrivacyMode ? window.SynergyRealtime.getPrivacyMode() : 'central',
                // ✅ PROMPTS: Include assigned prompts
                quick_actions: quickActions.length > 0 ? quickActions.join(',') : undefined,
                library_prompts: libraryPrompts.length > 0 ? libraryPrompts.join(',') : undefined
            };

            // Helper: Determine recipient based on privacy mode
            function _getRecipientTeamId() {
                const privacyMode = window.SynergyRealtime?.getPrivacyMode ? window.SynergyRealtime.getPrivacyMode() : 'central';
                const myUsername = window.UserAuth?.user?.username || null;

                if (privacyMode === 'local') {
                    // Local Ops: Message only for me
                    return myUsername;
                } else {
                    // Central HQ: Broadcast to all team members
                    return null;
                }
            }

            if (workflowContext) {
                requestBody.workflow_designer = {
                    active: true,
                    workflow_slug: workflowContext.slug,
                    workflow_id: workflowContext.workflowId,
                    mode: workflowContext.mode
                };
            }

            response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/agent/agent/${agentId}/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
                    'X-Session-Token': mySessionToken  // ✅ Add session token
                },
                body: JSON.stringify(requestBody)
            });
        }

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const startData = await response.json();
        console.log(`[Agent ${agentId}] Agent started:`, startData);

        // ✅ ROBUST FIX (Jan 23, 2026): Extract LSN and message_id for read-after-write consistency
        // Issue: Race condition where /stream called before /start's DB write visible
        // Solution: Pass LSN to /stream endpoint - backend waits for exact transaction
        const writeLsn = startData.write_lsn;
        const messageId = startData.message_id;
        
        if (writeLsn) {
            console.log(`[Agent ${agentId}] 🔒 Write LSN captured: ${writeLsn} (ensures read-after-write consistency)`);
        }
        if (messageId) {
            console.log(`[Agent ${agentId}] 🆔 Message ID captured: ${messageId} (for verification)`);
        }

        // ✅ NEW: Accept backend's conversation
        if (startData.conversation && Array.isArray(startData.conversation)) {
            console.log(`✅ [Agent ${agentId}] Backend returned ${startData.conversation.length} messages (authoritative)`);
            console.log(`📥 [Agent ${agentId}] Syncing frontend state with backend conversation`);

            // Update MessageStore with backend's conversation
            if (window.MessageStore) {
                window.MessageStore.clearThread(currentThread.id);

                for (const msg of startData.conversation) {
                    await window.MessageStore.addMessage(currentThread.id, msg, {
                        checkDuplicates: false,
                        silent: true
                    });
                }
                console.log(`✅ [Agent ${agentId}] MessageStore synced from backend`);
            }

            // Update AppState
            if (!AppState.agentThreads) AppState.agentThreads = {};
            AppState.agentThreads[agentId] = {
                id: currentThread.id,
                messages: startData.conversation,
                message_count: startData.conversation.length
            };
        }

        // Step 2: Connect to SSE stream (SAME AS PRIME!)
        console.log(`[Agent ${agentId}] Connecting to SSE stream...`);

        // ✅ ROBUST FIX (Jan 23, 2026): Pass LSN and message_id for read-after-write consistency
        let streamUrl = `${window.API_BASE_URL || 'http://localhost:5001'}/api/agent/stream/${agentId}?thread_slug=${threadSlug}`;
        
        // Add LSN if available (backend will wait for this transaction to be visible)
        if (writeLsn) {
            streamUrl += `&write_lsn=${encodeURIComponent(writeLsn)}`;
            console.log(`[Agent ${agentId}] 🔒 Stream URL includes LSN for guaranteed consistency`);
        }
        
        // Add message_id if available (backend will verify message exists)
        if (messageId) {
            streamUrl += `&message_id=${encodeURIComponent(messageId)}`;
            console.log(`[Agent ${agentId}] 🆔 Stream URL includes message_id for verification`);
        }
        
        console.log(`[Agent ${agentId}] Stream URL:`, streamUrl);

        // Create AbortController for this agent's stream
        MultiAgent.agentStreamControllers[agentId] = new AbortController();
        MultiAgent.agentStreamingStates[agentId] = true;
        
        // Show stop button in agent input area
        showAgentStopButton(agentId);

        // ✅ TEAM COLLABORATION FIX: Send socket ID to prevent message echo
        const headers = {};
        if (window.SynergyRealtime?.socket?.id) {
            headers['X-Socket-ID'] = window.SynergyRealtime.socket.id;
            console.log(`[Agent ${agentId}] Adding X-Socket-ID header:`, window.SynergyRealtime.socket.id);
        }

        const streamResponse = await fetch(streamUrl, { 
            signal: MultiAgent.agentStreamControllers[agentId].signal,
            headers: headers
        });

        if (!streamResponse.ok) {
            throw new Error(`Stream error! status: ${streamResponse.status}`);
        }

        updateAgentStatus(agentId, 'working', 'Responding...');
        if (typeof AgentStatusIndicator !== 'undefined') {
            AgentStatusIndicator.update('writing', agentId);
        }

        // CRITICAL: Capture thread location BEFORE streaming starts (isolation)
        const expectedAgentLocation = `agent-${agentId}`;
        const streamThreadSlug = threadSlug; // Freeze thread slug at stream start
        const streamStartTime = Date.now();

        console.log(`[Agent ${agentId}] 🔒 STREAM ISOLATION: thread=${streamThreadSlug}, location=${expectedAgentLocation}, timestamp=${streamStartTime}`);

        // ✨ NEW: Mark badge as processing (pulsing orange border)
        const badge = document.getElementById(`quick-nav-badge-${agentId}`);
        if (badge) {
            badge.classList.add('processing');
            console.log(`[Agent ${agentId}] 🔄 Badge marked as processing`);
        }

        // HANDLE STREAMING RESPONSE - Use shared TwoRule pathway
        console.log(`[Agent ${agentId}] Receiving streamed response...`);

        // ✅ FIX: Declare messagesContainer (it was missing!)
        const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
        if (!messagesContainer) {
            console.error(`[Agent ${agentId}] Could not find messages container!`);
            throw new Error('Messages container not found');
        }

        // VALIDATION: Verify container matches expected agent (isolation check)
        const containerAgentId = messagesContainer.id.replace('agent-messages-', '');
        if (containerAgentId !== agentId.toString()) {
            console.error(`[Agent ${agentId}] ❌ ISOLATION ERROR: Container mismatch! Expected agent-${agentId}, got ${containerAgentId}`);
            throw new Error(`Container isolation violation: expected agent-${agentId}, got agent-${containerAgentId}`);
        }

        // EXACTLY LIKE PRIME AI: Track bubbles (create them as events arrive)
        let textBubble = null;  // Current text bubble (ATOM icon)
        let thinkingBubble = null;  // Thinking bubble (if needed)
        let lastEventType = null;  // Track event transitions to create new bubbles

        // console.log(`[Agent ${agentId}] 🔵 STREAMING FUNCTION LOADED (v20251122d)`);

        // ISOLATION FIX: Thread-specific error tracking (prevents one agent breaking others)
        let threadErrorCount = 0;
        const maxThreadErrors = 10;  // Allow some parse errors before stopping THIS agent only
        let threadFailed = false;

        let fullResponse = '';
        let fullThinkingContent = '';
        let toolsUsed = [];
        let toolResults = [];

        const reader = streamResponse.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        console.log(`[Agent ${agentId}] 🎬 Stream processing started - thread: ${streamThreadSlug}`);

        while (true) {
            // Check if user stopped this agent's stream
            if (MultiAgent.agentStreamControllers[agentId]?.signal.aborted) {
                console.log(`[Agent ${agentId}] 🛑 Stream aborted by user`);
                break;
            }
            
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const messages = buffer.split('\n\n');
            buffer = messages.pop() || '';

            for (const message of messages) {
                const lines = message.split('\n');
                for (const line of lines) {
                    if (!line.startsWith('data: ')) continue;

                    const dataStr = line.slice(6);
                    if (dataStr === '[DONE]') continue;

                    try {
                        const data = JSON.parse(dataStr);

                        // console.log(`[Agent ${agentId}] 📨 Event:`, data.type, data);

                        // CONVERSATION_SYNC EVENT - Receive backend's authoritative conversation (Nov 22, 2025 FIX)
                        // Backend sends complete conversation_history BEFORE 'complete' event
                        // This prevents duplicate saves and ensures complete block structure
                        if (data.type === 'conversation_sync') {
                            console.log(`[Agent ${agentId}] 📥 [SYNC] Received conversation_sync: ${data.message_count} messages`);

                            if (data.conversation_history && Array.isArray(data.conversation_history)) {
                                // CRITICAL FIX (Dec 15, 2025): Use ThreadManager.getThreadByAgent() instead of AppState.agentThreads
                                // AppState.agentThreads does NOT exist - threads are stored in ThreadManager.threads array
                                // This fix mirrors AGENT_SAVE_THREAD_FIX_NOV22.md (same bug, different location)
                                const agentName = MultiAgent.getAgentName(agentId);
                                const thread = ThreadManager.getThreadByAgent(agentName);

                                if (thread) {
                                    // Update thread with backend's authoritative conversation
                                    thread.messages = data.conversation_history;
                                    thread.message_count = data.message_count;

                                    console.log(`[Agent ${agentId}] ✅ [SYNC] Thread.messages updated with ${data.message_count} messages from backend`);

                                    // Sync to MessageStore (FROM backend's data, not creating new)
                                    for (const msg of data.conversation_history) {
                                        await window.MessageStore.addMessage(thread.id, msg, {
                                            checkDuplicates: true,
                                            silent: true
                                        });
                                    }

                                    console.log(`[Agent ${agentId}] ✅ [SYNC] MessageStore synced from backend's conversation`);
                                } else {
                                    console.warn(`[Agent ${agentId}] ⚠️ [SYNC] Thread not found via ThreadManager.getThreadByAgent("${agentName}")`);
                                }
                            } else {
                                console.warn(`[Agent ${agentId}] ⚠️ [SYNC] Invalid conversation_history in conversation_sync event`);
                            }
                        }

                        // THINKING EVENT - Create THINKING BUBBLE (purple BRAIN icon)
                        else if ((data.type === 'thinking_block' || data.type === 'thinking') && (data.content || data.thinking)) {
                            const thinkingText = data.content || data.thinking || '';
                            if (thinkingText && thinkingText.trim().length > 0) {
                                // console.log(`[Agent ${agentId}] 💭 THINKING: ${thinkingText.substring(0, 50)}...`);

                                // Update status
                                if (typeof AgentStatusIndicator !== 'undefined') {
                                    AgentStatusIndicator.update('thinking', agentId);
                                }

                                // Create thinking bubble if doesn't exist - USING PRIME STRUCTURE
                                if (!thinkingBubble) {
                                    console.log(`[Agent ${agentId}] Creating thinking bubble with Prime structure...`);

                                    // Remove processing indicator when first bubble appears
                                    removeProcessingIndicator(agentId);

                                    thinkingBubble = document.createElement('div');
                                    thinkingBubble.className = 'ai-message assistant';  // ✅ Same as Prime (no extra classes)
                                    thinkingBubble.dataset.agentId = agentId;
                                    thinkingBubble.dataset.threadSlug = streamThreadSlug;
                                    thinkingBubble.setAttribute('data-raw-content', '');  // ✅ Same as Prime

                                    // Header with BRAIN avatar (PURPLE)
                                    const headerDiv = document.createElement('div');
                                    headerDiv.className = 'ai-message-header';

                                    const avatar = document.createElement('div');
                                    avatar.className = 'ai-message-avatar';
                                    avatar.style.background = '#8b5cf6'; // Purple
                                    avatar.innerHTML = '<i class="fa-solid fa-brain" style="color: white;"></i>';

                                    const toggleBtn = document.createElement('button');
                                    toggleBtn.className = 'ai-message-toggle';
                                    toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
                                    toggleBtn.title = 'Collapse/Expand thinking';
                                    toggleBtn.addEventListener('click', (e) => {
                                        e.stopPropagation();
                                        thinkingBubble.classList.toggle('collapsed');
                                    });

                                    headerDiv.appendChild(avatar);
                                    headerDiv.appendChild(toggleBtn);

                                    // Copy buttons
                                    const actionsDiv = document.createElement('div');
                                    actionsDiv.className = 'ai-message-actions';

                                    const copyBtn = document.createElement('button');
                                    copyBtn.className = 'ai-message-copy-btn';
                                    copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                                    copyBtn.title = 'Copy thinking content';
                                    copyBtn.addEventListener('click', (e) => {
                                        e.stopPropagation();
                                        const content = thinkingBubble.querySelector('.ai-message-content').textContent;
                                        navigator.clipboard.writeText(content).then(() => {
                                            copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                                            setTimeout(() => {
                                                copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                                            }, 2000);
                                        });
                                    });

                                    const copyRawBtn = document.createElement('button');
                                    copyRawBtn.className = 'ai-message-copy-btn';
                                    copyRawBtn.innerHTML = '<i class="fas fa-code"></i>';
                                    copyRawBtn.title = 'Copy raw thinking';
                                    copyRawBtn.addEventListener('click', (e) => {
                                        e.stopPropagation();
                                        const content = thinkingBubble.querySelector('.ai-message-content').textContent;
                                        navigator.clipboard.writeText(content).then(() => {
                                            copyRawBtn.innerHTML = '<i class="fas fa-check"></i>';
                                            setTimeout(() => {
                                                copyRawBtn.innerHTML = '<i class="fas fa-code"></i>';
                                            }, 2000);
                                        });
                                    });

                                    const expandBtn = document.createElement('button');
                                    expandBtn.className = 'ai-message-copy-btn';
                                    expandBtn.innerHTML = '<i class="fas fa-expand-alt"></i>';
                                    expandBtn.title = 'Expand message fullscreen';
                                    expandBtn.addEventListener('click', (e) => {
                                        e.stopPropagation();
                                        if (typeof window.openMessageFullscreen === 'function') {
                                            window.openMessageFullscreen(thinkingBubble);
                                        }
                                    });

                                    actionsDiv.appendChild(copyBtn);
                                    actionsDiv.appendChild(copyRawBtn);
                                    actionsDiv.appendChild(expandBtn);
                                    headerDiv.appendChild(actionsDiv);

                                    // Content div
                                    const contentDiv = document.createElement('div');
                                    contentDiv.className = 'ai-message-content';
                                    thinkingBubble.appendChild(headerDiv);
                                    thinkingBubble.appendChild(contentDiv);
                                    thinkingBubble.classList.add('collapsed'); // Start collapsed
                                    messagesContainer.appendChild(thinkingBubble);

                                    // ✅ APPLY VIEW MODE TO NEW BUBBLE
                                    if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.applyViewModeToMessage === 'function') {
                                        AgentColumn.applyViewModeToMessage(agentId, thinkingBubble);
                                    }

                                    // Add fullscreen double-click handler
                                    if (typeof window.addMessageFullscreenHandler === 'function') {
                                        window.addMessageFullscreenHandler(thinkingBubble);
                                    }

                                    thinkingBubble._fullThinkingText = '';
                                }

                                // Accumulate thinking text
                                thinkingBubble._fullThinkingText = thinkingBubble._fullThinkingText || '';

                                // AUTO SEPARATOR: Add visual break when new thinking block starts
                                if (data.delta_type === 'start' && thinkingBubble._fullThinkingText.trim()) {
                                    // New thinking block detected - add separator before it
                                    thinkingBubble._fullThinkingText += '\n\n---\n\n';
                                    console.log(`[Agent ${agentId}] 🔄 [THINKING] New thinking block detected, added visual separator`);
                                }

                                thinkingBubble._fullThinkingText += thinkingText;
                                fullThinkingContent += thinkingText;

                                // ✅ UPDATE RAW CONTENT ATTRIBUTE (SAME AS PRIME)
                                thinkingBubble.setAttribute('data-raw-content', thinkingBubble._fullThinkingText);

                                // Render markdown
                                const thinkingContent = thinkingBubble.querySelector('.ai-message-content');
                                if (thinkingContent) {
                                    if (window.marked) {
                                        try {
                                            thinkingContent.innerHTML = marked.parse(thinkingBubble._fullThinkingText, {
                                                breaks: true,
                                                gfm: true
                                            });
                                        } catch (e) {
                                            console.error(`[Agent ${agentId}] Markdown parse error in thinking:`, e);
                                            thinkingContent.textContent = thinkingBubble._fullThinkingText;
                                        }
                                    } else {
                                        thinkingContent.textContent = thinkingBubble._fullThinkingText;
                                    }
                                }

                                lastEventType = 'thinking';
                            }
                        }

                        // TOOL USE EVENT - Create TOOL BUBBLE (yellow COG icon)
                        else if (data.type === 'tool_use') {
                            const toolId = data.tool_id || data.tool_use_id || data.id;
                            console.log(`[Agent ${agentId}] ⚙️ TOOL_USE: ${data.tool_name} (${toolId})`);

                            // Update status
                            if (typeof AgentStatusIndicator !== 'undefined') {
                                AgentStatusIndicator.update('tool-running', agentId);
                            }

                            // Remove processing indicator when first bubble appears
                            removeProcessingIndicator(agentId);

                            // Create tool bubble - USING PRIME STRUCTURE
                            const toolBubble = document.createElement('div');
                            toolBubble.className = 'ai-message tool';  // ✅ Same as Prime (use 'tool' role)
                            toolBubble.setAttribute('data-tool-id', toolId);
                            toolBubble.dataset.agentId = agentId;
                            toolBubble.dataset.threadSlug = streamThreadSlug;
                            toolBubble.setAttribute('data-raw-content', '');  // ✅ Same as Prime

                            // Header with COG avatar (YELLOW)
                            const headerDiv = document.createElement('div');
                            headerDiv.className = 'ai-message-header';

                            const avatar = document.createElement('div');
                            avatar.className = 'ai-message-avatar';
                            avatar.style.background = '#eab308'; // Yellow
                            avatar.innerHTML = '<i class="fas fa-cog" style="color: white;"></i>';

                            const toggleBtn = document.createElement('button');
                            toggleBtn.className = 'ai-message-toggle';
                            toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
                            toggleBtn.title = 'Collapse/Expand tool';
                            toggleBtn.addEventListener('click', (e) => {
                                e.stopPropagation();
                                toolBubble.classList.toggle('collapsed');
                            });

                            headerDiv.appendChild(avatar);
                            headerDiv.appendChild(toggleBtn);

                            // Copy button
                            const actionsDiv = document.createElement('div');
                            actionsDiv.className = 'ai-message-actions';

                            const copyBtn = document.createElement('button');
                            copyBtn.className = 'ai-message-copy-btn';
                            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                            copyBtn.title = 'Copy tool content';
                            copyBtn.addEventListener('click', (e) => {
                                e.stopPropagation();
                                const contentDiv = toolBubble.querySelector('.ai-message-content');
                                const content = contentDiv ? contentDiv.textContent : '';
                                navigator.clipboard.writeText(content).then(() => {
                                    copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                                    setTimeout(() => {
                                        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                                    }, 2000);
                                });
                            });

                            const expandBtn = document.createElement('button');
                            expandBtn.className = 'ai-message-copy-btn';
                            expandBtn.innerHTML = '<i class="fas fa-expand-alt"></i>';
                            expandBtn.title = 'Expand message fullscreen';
                            expandBtn.addEventListener('click', (e) => {
                                e.stopPropagation();
                                if (typeof window.openMessageFullscreen === 'function') {
                                    window.openMessageFullscreen(toolBubble);
                                }
                            });

                            actionsDiv.appendChild(copyBtn);
                            actionsDiv.appendChild(expandBtn);
                            headerDiv.appendChild(actionsDiv);

                            // Content
                            const contentDiv = document.createElement('div');
                            contentDiv.className = 'ai-message-content';
                            contentDiv.innerHTML = `
                                <div style="margin-bottom: 8px;"><strong>Tool:</strong> ${data.name || data.tool_name}</div>
                                <pre>${JSON.stringify(data.input || data.tool_input, null, 2)}</pre>
                            `;

                            toolBubble.appendChild(headerDiv);
                            toolBubble.appendChild(contentDiv);
                            toolBubble.classList.add('collapsed'); // Start collapsed
                            messagesContainer.appendChild(toolBubble);

                            // ✅ APPLY VIEW MODE TO NEW BUBBLE
                            if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.applyViewModeToMessage === 'function') {
                                AgentColumn.applyViewModeToMessage(agentId, toolBubble);
                            }

                            // Add fullscreen double-click handler
                            if (typeof window.addMessageFullscreenHandler === 'function') {
                                window.addMessageFullscreenHandler(toolBubble);
                            }

                            lastEventType = 'tool_use';
                            toolsUsed.push({
                                name: data.name || data.tool_name,
                                input: data.input || data.tool_input,
                                id: toolId
                            });
                        }

                        // TOOL RESULT EVENT - Create SEPARATE tool result bubble (like Prime AI)
                        else if (data.type === 'tool_result') {
                            const toolId = data.tool_id || data.tool_use_id || data.id;
                            console.log(`[Agent ${agentId}] 📊 TOOL_RESULT for ${toolId}`);

                            // Update the original tool bubble avatar to green (complete)
                            const toolBubble = messagesContainer.querySelector(`[data-tool-id="${toolId}"]`);
                            if (toolBubble) {
                                const avatar = toolBubble.querySelector('.ai-message-avatar');
                                if (avatar) {
                                    avatar.style.background = '#10b981'; // Green (success)
                                }
                            }

                            // Remove processing indicator when first bubble appears
                            removeProcessingIndicator(agentId);

                            // Create SEPARATE tool result bubble
                            const isError = data.is_error || !data.success;
                            const resultText = typeof data.result === 'string' ? data.result : JSON.stringify(data.result, null, 2);
                            const rawResult = data.result || '';

                            const toolResultBubble = document.createElement('div');
                            toolResultBubble.className = 'ai-message tool';  // ✅ Same as Prime (use 'tool' role)
                            toolResultBubble.setAttribute('data-tool-result-id', toolId);
                            toolResultBubble.dataset.agentId = agentId;
                            toolResultBubble.dataset.threadSlug = streamThreadSlug;
                            toolResultBubble.setAttribute('data-raw-content', resultText);  // ✅ Same as Prime

                            // Header with white flag icon
                            const headerDiv = document.createElement('div');
                            headerDiv.className = 'ai-message-header';

                            const avatar = document.createElement('div');
                            avatar.className = 'ai-message-avatar';
                            avatar.style.background = isError ? '#ef4444' : '#60A5FA'; // Red for error, Blue for success
                            avatar.innerHTML = '<i class="fas fa-flag" style="color: white; font-size: 14px;"></i>';

                            const toggleBtn = document.createElement('button');
                            toggleBtn.className = 'ai-message-toggle';
                            toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
                            toggleBtn.title = 'Collapse/Expand result';
                            toggleBtn.addEventListener('click', (e) => {
                                e.stopPropagation();
                                toolResultBubble.classList.toggle('collapsed');
                            });

                            headerDiv.appendChild(avatar);
                            headerDiv.appendChild(toggleBtn);

                            // Copy buttons
                            const actionsDiv = document.createElement('div');
                            actionsDiv.className = 'ai-message-actions';

                            // Copy formatted button
                            const copyBtn = document.createElement('button');
                            copyBtn.className = 'ai-message-copy-btn';
                            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                            copyBtn.title = 'Copy result';
                            copyBtn.addEventListener('click', (e) => {
                                e.stopPropagation();
                                const content = toolResultBubble.querySelector('.ai-message-content').textContent;
                                navigator.clipboard.writeText(content).then(() => {
                                    copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                                    setTimeout(() => {
                                        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                                    }, 2000);
                                });
                            });

                            // Copy raw button
                            const copyRawBtn = document.createElement('button');
                            copyRawBtn.className = 'ai-message-copy-btn';
                            copyRawBtn.innerHTML = '<i class="fas fa-code"></i>';
                            copyRawBtn.title = 'Copy raw result';
                            copyRawBtn.addEventListener('click', (e) => {
                                e.stopPropagation();
                                navigator.clipboard.writeText(typeof rawResult === 'string' ? rawResult : JSON.stringify(rawResult, null, 2)).then(() => {
                                    copyRawBtn.innerHTML = '<i class="fas fa-check"></i>';
                                    setTimeout(() => {
                                        copyRawBtn.innerHTML = '<i class="fas fa-code"></i>';
                                    }, 2000);
                                });
                            });

                            const expandBtn = document.createElement('button');
                            expandBtn.className = 'ai-message-copy-btn';
                            expandBtn.innerHTML = '<i class="fas fa-expand-alt"></i>';
                            expandBtn.title = 'Expand message fullscreen';
                            expandBtn.addEventListener('click', (e) => {
                                e.stopPropagation();
                                if (typeof window.openMessageFullscreen === 'function') {
                                    window.openMessageFullscreen(toolResultBubble);
                                }
                            });

                            actionsDiv.appendChild(copyBtn);
                            actionsDiv.appendChild(copyRawBtn);
                            actionsDiv.appendChild(expandBtn);
                            headerDiv.appendChild(actionsDiv);

                            // Content
                            const contentDiv = document.createElement('div');
                            contentDiv.className = 'ai-message-content';

                            // Format result nicely
                            let formattedResult = resultText;
                            try {
                                const parsed = JSON.parse(resultText);
                                formattedResult = JSON.stringify(parsed, null, 2);
                            } catch (e) {
                                // Keep as-is if not JSON
                            }

                            // Create elements separately to avoid escaping issues with .innerHTML
                            const headerTextDiv = document.createElement('div');
                            headerTextDiv.style.marginBottom = '8px';
                            headerTextDiv.style.color = isError ? '#ef4444' : '#60A5FA';
                            headerTextDiv.innerHTML = `<strong><i class="fas ${isError ? 'fa-times-circle' : 'fa-check-circle'}"></i> Tool Result: ${data.tool_name || 'Unknown'}</strong>`;

                            const preElement = document.createElement('pre');
                            preElement.style.background = 'rgba(0,0,0,0.3)';
                            preElement.style.padding = '12px';
                            preElement.style.borderRadius = '6px';
                            preElement.style.maxHeight = '400px';
                            preElement.style.overflowY = 'auto';
                            preElement.textContent = formattedResult; // Use textContent to prevent escaping

                            contentDiv.appendChild(headerTextDiv);
                            contentDiv.appendChild(preElement);

                            toolResultBubble.appendChild(headerDiv);
                            toolResultBubble.appendChild(contentDiv);
                            toolResultBubble.classList.add('collapsed'); // Start collapsed
                            messagesContainer.appendChild(toolResultBubble);

                            // ✅ APPLY VIEW MODE TO NEW BUBBLE
                            if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.applyViewModeToMessage === 'function') {
                                AgentColumn.applyViewModeToMessage(agentId, toolResultBubble);
                            }

                            // Add fullscreen double-click handler
                            if (typeof window.addMessageFullscreenHandler === 'function') {
                                window.addMessageFullscreenHandler(toolResultBubble);
                            }

                            if (typeof AgentStatusIndicator !== 'undefined') {
                                AgentStatusIndicator.update('tool-success', agentId);
                            }

                            toolResults.push(data);
                        }

                        // CONTENT DELTA - Text streaming (ATOM icon)
                        else if (data.type === 'content_delta' && data.text) {
                            console.log(`[Agent ${agentId}] 📝 CONTENT_DELTA: ${data.text.substring(0, 50)}...`);

                            // Create NEW text bubble when switching from non-text to text
                            if (lastEventType !== 'content_delta' && lastEventType !== null) {
                                if (textBubble) {
                                    console.log(`[Agent ${agentId}] Creating new text bubble (switching from ${lastEventType})`);
                                    const oldBubble = textBubble;
                                    textBubble = null;
                                    fullResponse = '';
                                    // Flush old processor
                                    if (oldBubble && oldBubble._twoRuleProcessor) {
                                        try {
                                            if (typeof oldBubble._twoRuleProcessor.forceFlush === 'function') {
                                                oldBubble._twoRuleProcessor.forceFlush();
                                            }
                                        } catch (e) {
                                            console.warn(`[Agent ${agentId}] Error flushing processor:`, e);
                                        }
                                    }
                                }
                            }

                            fullResponse += data.text;
                            lastEventType = 'content_delta';

                            // ✅ UPDATE RAW CONTENT ATTRIBUTE (SAME AS PRIME)
                            if (textBubble) {
                                textBubble.setAttribute('data-raw-content', fullResponse);
                            }

                            // Create text bubble if doesn't exist - USING PRIME STRUCTURE
                            if (!textBubble) {
                                console.log(`[Agent ${agentId}] Creating text bubble with Prime structure...`);

                                // Remove processing indicator when first bubble appears
                                removeProcessingIndicator(agentId);

                                textBubble = document.createElement('div');
                                textBubble.className = 'ai-message assistant';  // ✅ Same as Prime
                                textBubble.dataset.agentId = agentId;
                                textBubble.dataset.threadSlug = streamThreadSlug;
                                textBubble.setAttribute('data-raw-content', '');  // ✅ Same as Prime

                                // Header with ATOM ICON (SAME AS PRIME)
                                const headerDiv = document.createElement('div');
                                headerDiv.className = 'ai-message-header';  // ✅ Same as Prime

                                const avatar = document.createElement('div');
                                avatar.className = 'ai-message-avatar';  // ✅ Same as Prime
                                avatar.innerHTML = '<i class="fa-solid fa-atom"></i>';  // ✅ Same as Prime

                                const toggleBtn = document.createElement('button');
                                toggleBtn.className = 'ai-message-toggle';  // ✅ Same as Prime
                                toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
                                toggleBtn.title = 'Collapse/Expand message';
                                toggleBtn.addEventListener('click', (e) => {
                                    e.stopPropagation();
                                    textBubble.classList.toggle('collapsed');
                                });

                                headerDiv.appendChild(avatar);
                                headerDiv.appendChild(toggleBtn);

                                // Copy buttons (SAME AS PRIME)
                                const actionsDiv = document.createElement('div');
                                actionsDiv.className = 'ai-message-actions';  // ✅ Same as Prime

                                const copyBtn = document.createElement('button');
                                copyBtn.className = 'ai-message-copy-btn';  // ✅ Same as Prime
                                copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                                copyBtn.title = 'Copy rendered text';
                                copyBtn.addEventListener('click', (e) => {
                                    e.stopPropagation();
                                    const content = textBubble.querySelector('.ai-message-content').textContent;
                                    navigator.clipboard.writeText(content).then(() => {
                                        copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                                        setTimeout(() => {
                                            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                                        }, 2000);
                                    });
                                });

                                // ✅ RAW COPY BUTTON (SAME AS PRIME) - uses data-raw-content attribute
                                const copyRawBtn = document.createElement('button');
                                copyRawBtn.className = 'ai-message-copy-btn';
                                copyRawBtn.innerHTML = '<i class="fas fa-code"></i>';
                                copyRawBtn.title = 'Copy raw content';
                                copyRawBtn.addEventListener('click', (e) => {
                                    e.stopPropagation();
                                    const rawContent = textBubble.getAttribute('data-raw-content') || fullResponse;
                                    navigator.clipboard.writeText(rawContent).then(() => {
                                        copyRawBtn.innerHTML = '<i class="fas fa-check"></i>';
                                        setTimeout(() => {
                                            copyRawBtn.innerHTML = '<i class="fas fa-code"></i>';
                                        }, 2000);
                                    });
                                });

                                const expandBtn = document.createElement('button');
                                expandBtn.className = 'ai-message-copy-btn';
                                expandBtn.innerHTML = '<i class="fas fa-expand-alt"></i>';
                                expandBtn.title = 'Expand message fullscreen';
                                expandBtn.addEventListener('click', (e) => {
                                    e.stopPropagation();
                                    if (typeof window.openMessageFullscreen === 'function') {
                                        window.openMessageFullscreen(textBubble);
                                    }
                                });

                                actionsDiv.appendChild(copyBtn);
                                actionsDiv.appendChild(copyRawBtn);
                                actionsDiv.appendChild(expandBtn);
                                headerDiv.appendChild(actionsDiv);

                                textBubble.appendChild(headerDiv);

                                // Content div
                                const contentDiv = document.createElement('div');
                                contentDiv.className = 'ai-message-content';
                                textBubble.appendChild(contentDiv);

                                messagesContainer.appendChild(textBubble);
                                console.log(`[Agent ${agentId}] Text bubble created`);

                                // ✅ APPLY VIEW MODE TO NEW BUBBLE
                                if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.applyViewModeToMessage === 'function') {
                                    AgentColumn.applyViewModeToMessage(agentId, textBubble);
                                }

                                // Add fullscreen double-click handler
                                if (typeof window.addMessageFullscreenHandler === 'function') {
                                    window.addMessageFullscreenHandler(textBubble);
                                }

                                // Initialize TwoRuleStreamProcessor
                                if (typeof TwoRuleStreamProcessor !== 'undefined') {
                                    try {
                                        const processor = new TwoRuleStreamProcessor(contentDiv);
                                        textBubble._twoRuleProcessor = processor;
                                        console.log(`[Agent ${agentId}] 🔷 TwoRuleStreamProcessor initialized`);
                                    } catch (e) {
                                        console.warn(`[Agent ${agentId}] TwoRuleStreamProcessor failed:`, e);
                                    }
                                }
                            }

                            // Process chunk through TwoRuleStreamProcessor
                            const textContent = textBubble.querySelector('.ai-message-content');
                            if (textContent) {
                                const processor = textBubble._twoRuleProcessor;
                                if (processor && typeof processor.processChunk === 'function') {
                                    processor.processChunk(data.text).then(() => {
                                        console.log(`[Agent ${agentId}] Chunk processed`);
                                    }).catch((e) => {
                                        console.error(`[Agent ${agentId}] Process error:`, e);
                                        textContent.innerHTML = marked.parse(fullResponse);
                                    });
                                } else {
                                    // Fallback
                                    if (window.marked) {
                                        textContent.innerHTML = marked.parse(fullResponse);
                                    } else {
                                        textContent.textContent = fullResponse;
                                    }
                                }
                                // Only scroll within message container, don't force page/column jump
                                const messagesContainer = document.getElementById(`agent-${agentId}-messages`);
                                if (messagesContainer && !messagesContainer.classList.contains('user-scrolled')) {
                                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                                }
                            }
                        }

                        // ERROR EVENT - Log but DON'T stop stream (Dec 15, 2025 FIX)
                        // Backend sends error events during multi-turn conversations (e.g., API errors from tool execution)
                        // Frontend must acknowledge and continue listening for subsequent events
                        else if (data.type === 'error') {
                            console.warn(`[Agent ${agentId}] ⚠️ ERROR EVENT:`, data.error_type, data.error_message);

                            // Create error bubble (red exclamation triangle)
                            removeProcessingIndicator(agentId);

                            const errorBubble = document.createElement('div');
                            errorBubble.className = 'ai-message error';
                            errorBubble.dataset.agentId = agentId;
                            errorBubble.dataset.threadSlug = streamThreadSlug;

                            // Header with RED TRIANGLE avatar
                            const headerDiv = document.createElement('div');
                            headerDiv.className = 'ai-message-header';

                            const avatar = document.createElement('div');
                            avatar.className = 'ai-message-avatar';
                            avatar.style.background = '#ef4444'; // Red
                            avatar.innerHTML = '<i class="fas fa-exclamation-triangle" style="color: white;"></i>';

                            const toggleBtn = document.createElement('button');
                            toggleBtn.className = 'ai-message-toggle';
                            toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
                            toggleBtn.title = 'Collapse/Expand error';
                            toggleBtn.addEventListener('click', (e) => {
                                e.stopPropagation();
                                errorBubble.classList.toggle('collapsed');
                            });

                            headerDiv.appendChild(avatar);
                            headerDiv.appendChild(toggleBtn);

                            // Content
                            const contentDiv = document.createElement('div');
                            contentDiv.className = 'ai-message-content';
                            contentDiv.style.color = '#ef4444';

                            const errorMsg = data.error_message || 'Unknown error';
                            const truncated = errorMsg.length > 500 ? errorMsg.substring(0, 500) + '...' : errorMsg;

                            contentDiv.innerHTML = `
                                <strong><i class="fas fa-times-circle"></i> API Error: ${data.error_type || 'Unknown'}</strong><br>
                                <pre style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 6px; margin-top: 8px; white-space: pre-wrap;">${truncated}</pre>
                            `;

                            errorBubble.appendChild(headerDiv);
                            errorBubble.appendChild(contentDiv);
                            errorBubble.classList.add('collapsed'); // Start collapsed
                            messagesContainer.appendChild(errorBubble);

                            // Apply view mode
                            if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.applyViewModeToMessage === 'function') {
                                AgentColumn.applyViewModeToMessage(agentId, errorBubble);
                            }

                            // DON'T break stream - backend may continue with more events
                            // This is critical for multi-turn conversations where one tool may fail but agent continues
                        }

                    } catch (e) {
                        // ISOLATION FIX: Only increment error count for THIS agent
                        threadErrorCount++;
                        console.error(`[Agent ${agentId}] SSE parse error (${threadErrorCount}/${maxThreadErrors}):`, e);

                        // If too many errors in THIS agent, stop THIS agent only
                        if (threadErrorCount >= maxThreadErrors) {
                            threadFailed = true;
                            console.error(`[Agent ${agentId}] Thread failed after ${maxThreadErrors} errors - stopping THIS agent only`);
                            break;  // Exit line loop
                        }
                        // Otherwise continue - don't let one bad event break the whole stream
                    }
                }

                // If thread failed, break outer message loop too
                if (threadFailed) {
                    console.error(`[Agent ${agentId}] Exiting stream reader for failed thread`);
                    break;
                }
            }
        }

        // Thread-specific cleanup
        if (threadFailed) {
            addAgentMessage(agentId, 'ai', ` Thread error: Too many parse errors. Please try again.`);
        }

        console.log(`[Agent ${agentId}] ✅ Stream complete - ${fullResponse.length} chars received`);

        // Clean up stream controls
        MultiAgent.agentStreamControllers[agentId] = null;
        MultiAgent.agentStreamingStates[agentId] = false;
        hideAgentStopButton(agentId);

        // Clear status indicator
        if (typeof AgentStatusIndicator !== 'undefined') {
            AgentStatusIndicator.clear(agentId);
        }

        // ✅ CRITICAL FIX: Ensure fullResponse is visible in DOM after streaming
        // Sometimes TwoRuleStreamProcessor loses content or fails silently
        // ⚠️ IMPORTANT: Skip the text-length check when the response contains viz delimiters.
        // Visualizations (React, HTML, Plotly, Mermaid, etc.) render inside iframes/canvases
        // and contribute ZERO to .textContent, making the 50% threshold always trigger
        // and overwriting the correctly-rendered viz with raw markdown.
        const VIZ_DELIMITER_RE = /<(EXECUTE_REACT|EXECUTE_HTML|PLOTLY|MERMAID|CHARTJS|APEXCHARTS|THREEJS|GSAP|LOTTIE|SVG_VISUAL|CAD|SCHEMATIC|BLUEPRINT|MOLECULE|GRAPH|LATEX|ENGINEERING_CAD|TECHNICAL_DRAWING)>/i;
        const responseHasViz = VIZ_DELIMITER_RE.test(fullResponse);
        if (textBubble && fullResponse && fullResponse.trim().length > 0 && !responseHasViz) {
            const textContent = textBubble.querySelector('.ai-message-content');
            if (textContent) {
                // Check if content is actually visible (not empty or just whitespace)
                const visibleText = textContent.textContent?.trim() || '';
                if (visibleText.length === 0 || visibleText.length < fullResponse.length * 0.5) {
                    console.warn(`[Agent ${agentId}] ⚠️ Content missing or incomplete in DOM (${visibleText.length} vs ${fullResponse.length} chars) - forcing full render`);
                    if (window.marked) {
                        textContent.innerHTML = marked.parse(fullResponse, { breaks: true, gfm: true });
                    } else {
                        textContent.textContent = fullResponse;
                    }
                    console.log(`[Agent ${agentId}] ✅ Forced full content render - ${fullResponse.length} chars`);
                }
            }
        } else if (responseHasViz) {
            console.log(`[Agent ${agentId}] ℹ️ Skipping fallback text-ratio check — response contains viz delimiters (iframes don't count toward textContent)`);
        }

        // Finalize TwoRuleStreamProcessor (render any pending visualizations)
        if (textBubble && textBubble._twoRuleProcessor) {
            console.log(`[Agent ${agentId}] Finalizing TwoRuleStreamProcessor...`);
            try {
                if (typeof textBubble._twoRuleProcessor.finalize === 'function') {
                    await textBubble._twoRuleProcessor.finalize();
                    console.log(`[Agent ${agentId}] ✅ Processor finalized`);

                    // Force render if still no content visible (skip if viz was rendered)
                    const textContent = textBubble.querySelector('.ai-message-content');
                    const hasRenderedViz = textContent && textContent.querySelector('.viz-container, iframe, canvas') !== null;
                    if (textContent && !hasRenderedViz && (!textContent.innerHTML || textContent.innerHTML.trim() === '')) {
                        console.warn(`[Agent ${agentId}] No content visible after finalize - forcing markdown render`);
                        if (window.marked) {
                            textContent.innerHTML = marked.parse(fullResponse, { breaks: true, gfm: true });
                        } else {
                            textContent.textContent = fullResponse;
                        }
                    }
                }
            } catch (e) {
                console.error(`[Agent ${agentId}] Finalize error:`, e);
            }
        }

        // Store raw markdown for copy-raw button
        if (textBubble) {
            textBubble.dataset.rawMarkdown = fullResponse;
        }

        // SMART SAVE: Find thread by slug (even if user moved it during stream)
        const agentName = getAgentName(agentId);
        let threadForSaving = ThreadManager.getThreadByAgent(agentName);

        // If thread not at this agent, find it by slug (user may have moved it)
        if (!threadForSaving || threadForSaving.id !== streamThreadSlug) {
            console.warn(`[Agent ${agentId}] ⚠️ Thread moved during stream! Looking up by slug...`);
            threadForSaving = ThreadManager.threads.find(t => t.id === streamThreadSlug);

            if (threadForSaving) {
                const newLocation = threadForSaving.location || 'prime';
                console.log(`[Agent ${agentId}] ✅ Found thread at new location: ${newLocation}`);
                console.log(`[Agent ${agentId}] Saving response to thread ${streamThreadSlug} (user moved it, that's OK)`);
            } else {
                console.error(`[Agent ${agentId}] ❌ Cannot find thread ${streamThreadSlug} anywhere!`);
                console.error(`[Agent ${agentId}] Response will be discarded (thread may have been deleted)`);
                return; // Only discard if thread genuinely doesn't exist
            }
        } else {
            console.log(`[Agent ${agentId}] ✅ Thread ${streamThreadSlug} still at ${agentName} - saving response`);
        }

        // Save AI response to thread with FULL content structure
        const responseTime = Date.now() - startTime;

        if (threadForSaving) {
            // Add AI message with FULL content blocks (for display)
            const fullContent = [];

            // Add thinking block if present
            if (fullThinkingContent && fullThinkingContent.trim()) {
                fullContent.push({
                    type: 'thinking',
                    content: fullThinkingContent
                });
            }

            // Add tool_use blocks
            toolsUsed.forEach(tool => {
                fullContent.push({
                    type: 'tool_use',
                    id: tool.id,
                    name: tool.tool_name,
                    input: tool.input
                });
            });

            // Add tool_result blocks
            toolResults.forEach(toolResult => {
                fullContent.push({
                    type: 'tool_result',
                    tool_use_id: toolResult.tool_use_id,
                    content: toolResult.content
                });
            });

            // Add text content block if present
            if (fullResponse && fullResponse.trim()) {
                fullContent.push({
                    type: 'text',
                    text: fullResponse
                });
            }

            // ========================================================================
            // CRITICAL FIX (Nov 22, 2025): DO NOT create message independently!
            // Backend already sent complete conversation via 'conversation_sync' event
            // MessageStore was synced from backend's authoritative conversation_history
            // Creating message here would race with backend's data → corruption
            // ========================================================================
            console.log(`[Agent ${agentId}] ✅ [SYNC] Message already synced via conversation_sync event`);
            console.log(`[Agent ${agentId}] 📊 Stream summary: ${toolsUsed.length} tools, thinking: ${fullThinkingContent ? 'yes' : 'no'}, text length: ${fullResponse.length}`);

            // ✅ BROADCAST: Emit AI response to other sessions
            if (window.SynergyRealtime && window.SynergyRealtime.socket) {
                window.SynergyRealtime.socket.emit('agent_message_sent', {
                    thread_id: threadForSaving.id,
                    agent_id: agentId,
                    message: fullResponse,
                    role: 'assistant',
                    content_blocks: fullContent,
                    user_id: window.currentUserId || null,
                    session_token: window.SynergyRealtime.sessionToken,
                    privacy_mode: window.SynergyRealtime.getPrivacyMode ? window.SynergyRealtime.getPrivacyMode() : 'central',
                    team_id: window.SynergyRealtime._getTeamId ? window.SynergyRealtime._getTeamId() : null
                });
                console.log(`📡 [Agent ${agentId}] Broadcasted AI response to other sessions (mode: ${window.SynergyRealtime.getPrivacyMode ? window.SynergyRealtime.getPrivacyMode() : 'central'})`);
            }

            // Update thread timestamp to NOW (actual last activity)
            threadForSaving.updated = new Date().toISOString();

            // CRITICAL FIX: Refresh thread-info card to show updated timestamp
            if (typeof MultiAgent !== 'undefined' && MultiAgent.updateAgentHeader) {
                MultiAgent.updateAgentHeader(agentId);
                console.log(`[Agent ${agentId}] Refreshed agent header with new timestamp`);
            }

            // Update quick-nav badge to reflect new message count (real-time update)
            if (typeof MultiAgent !== 'undefined' && MultiAgent.updateQuickNavBadge) {
                MultiAgent.updateQuickNavBadge(agentId);
                console.log(`[Agent ${agentId}] Updated quick-nav badge`);

                // ✨ Remove processing state and add completion indicator
                const badge = document.getElementById(`quick-nav-badge-${agentId}`);
                if (badge) {
                    badge.classList.remove('processing');
                    badge.classList.add('message-complete');
                    console.log(`[Agent ${agentId}] ✅ Badge marked as message-complete (green), processing removed`);
                }
            }

            // 🔔 NEW: Add notification for message completion
            if (typeof NotificationCenter !== 'undefined' && NotificationCenter.add) {
                const agentName = MultiAgent.getAgentName ? MultiAgent.getAgentName(agentId) : `Agent ${agentId}`;
                const thread = ThreadManager.getThreadByAgent ? ThreadManager.getThreadByAgent(agentName) : null;
                const threadName = thread?.name || 'Unknown Thread';
                const messageCount = thread?.messages?.length || 0;

                NotificationCenter.add({
                    type: 'MESSAGE_COMPLETE',
                    message: `${agentName} completed response in "${threadName}"`,
                    metadata: {
                        agentId: agentId,
                        threadId: thread?.id,
                        threadName: threadName,
                        messageCount: messageCount,
                        responseLength: fullResponse.length
                    },
                    action: {
                        type: 'navigate_to_agent',
                        target: { agentId: agentId }
                    }
                });

                console.log(`[Agent ${agentId}] 🔔 Notification added for message completion`);
            }

            // CRITICAL: Save thread to backend using backend's synced conversation
            // Use thread.messages (synced from conversation_sync) instead of MessageStore.getMessages()
            // This ensures we save backend's authoritative data, not frontend-accumulated data
            console.log(`[Agent ${agentId}] Saving thread to backend...`);
            try {
                // FIXED: Use ThreadManager.getThreadByAgent() instead of AppState lookup
                const thread = ThreadManager.getThreadByAgent(agentName);

                if (thread && thread.messages) {
                    // Use backend's conversation (from conversation_sync event)
                    threadForSaving.messages = thread.messages;
                    threadForSaving.message_count = thread.messages.length;
                    threadForSaving.updated = new Date().toISOString();

                    console.log(`[Agent ${agentId}] 📤 [SAVE] Backend's conversation: ${thread.messages.length} messages`);

                    // ✅ BACKEND AUTO-SAVE: Backend saves messages after stream completion
                    // Frontend should NOT save - backend already persisted to sessions.messages
                    console.log(`[Agent ${agentId}] ✅ [SAVE] Messages already saved by backend (auto-save after stream)`);
                    console.log(`[Agent ${agentId}] ℹ️ [SAVE] Frontend does not save - backend is single source of truth`);
                } else {
                    console.error(`[Agent ${agentId}] ❌ [SAVE] Thread or messages not found via ThreadManager - cannot save`);
                }
            } catch (saveError) {
                console.error(`[Agent ${agentId}] ❌ [SAVE] Error saving thread:`, saveError);
            }
        }

    } catch (error) {
        console.error(`[Agent ${agentId}] Error:`, error);

        // CRITICAL: Attempt auto-recovery with ErrorRecoveryManager FIRST
        if (window.ErrorRecoveryManager && error.message) {
            const errorMsg = error.message.toLowerCase();
            const isRecoverable = errorMsg.includes('invalid_request_error') ||
                errorMsg.includes('tool_use_id') ||
                errorMsg.includes('first block must be') ||
                errorMsg.includes('thinking') ||
                errorMsg.includes('rate limit') ||
                errorMsg.includes('context_length') ||
                errorMsg.includes('prompt is too long') ||
                errorMsg.includes('overloaded');

            // DETAILED LOGGING FOR ERROR RECOVERY DEBUGGING
            console.group(`🔴 ERROR RECOVERY SYSTEM TRIGGERED - Agent ${agentId}`);
            console.log('📍 Location: Agent Chat System');
            console.log('🤖 Agent ID:', agentId);
            console.log('⚠️ Error Object:', error);
            console.log('📝 Error Message:', error.message);
            console.log('🔍 Error Type:', error.name);
            console.log('🎯 Is Recoverable:', isRecoverable);
            console.log('📦 Request Payload:', requestBody);
            console.log('🧵 Thread Slug:', threadSlug);
            console.log('⏰ Timestamp:', new Date().toISOString());
            console.groupEnd();

            if (isRecoverable) {
                // Check if auto-recovery is enabled in settings
                const recoveryEnabled = typeof window.isErrorRecoveryEnabled === 'function'
                    ? window.isErrorRecoveryEnabled(errorType)
                    : true;

                if (!recoveryEnabled) {
                    console.log(`[Agent ${agentId}] ⛔ Auto-recovery disabled in settings - skipping recovery`);
                    throw error; // Rethrow to show error normally
                }

                console.log(`[Agent ${agentId}] Attempting auto-recovery...`);

                try {
                    // Create recovery manager
                    const recoveryManager = new ErrorRecoveryManager(
                        `agent-${agentId}`,
                        threadForSaving.id,
                        agentId
                    );

                    // Attempt recovery with original request payload
                    const recoveryResponse = await recoveryManager.handleError(error, requestBody);

                    // If recovery succeeded
                    if (recoveryResponse) {
                        console.log(`[Agent ${agentId}] Auto-recovery successful!`);

                        // Show recovery log
                        const recoveryLog = recoveryManager.exportRecoveryLog();
                        console.log(`=== RECOVERY LOG (Agent ${agentId}) ===\\n` + recoveryLog);

                        // Show success notification
                        if (typeof showNotification === 'function') {
                            showNotification(`Agent ${getAgentName(agentId)}: Auto-recovery successful`, 'success');
                        }

                        // Exit - recovery handled resubmission
                        return;
                    }
                } catch (recoveryError) {
                    console.error(`[Agent ${agentId}] Auto-recovery failed:`, recoveryError);
                    // Fall through to normal error handling
                }
            }
        }

        // Clean up stream controls on error
        MultiAgent.agentStreamControllers[agentId] = null;
        MultiAgent.agentStreamingStates[agentId] = false;
        hideAgentStopButton(agentId);
        
        // Don't show error message if user intentionally stopped the response
        if (!error.message.includes('aborted') && !error.message.includes('BodyStreamBuffer')) {
            addAgentMessage(agentId, 'ai', ` Error: ${error.message}`);
            updateAgentStatus(agentId, 'error', 'Error');
        }
        if (typeof AgentStatusIndicator !== 'undefined') {
            AgentStatusIndicator.clear(agentId);
        }
    } finally {
        updateAgentStatus(agentId, 'ready', 'Ready');
        if (typeof AgentStatusIndicator !== 'undefined') {
            AgentStatusIndicator.clear(agentId);
        }
        if (sendBtn) {
            sendBtn.disabled = false;
        }

        // Update quick-nav badge to highlight it (has messages now)
        MultiAgent.updateQuickNavBadge(agentId);
    }
}

function handleAgentStreamEvent(agentId, data, bubble) {
    // Initialize processor for this bubble if not exists
    if (!bubble.dataset.processorInitialized && typeof TwoRuleStreamProcessor !== 'undefined') {
        try {
            const _p = new TwoRuleStreamProcessor(bubble);
            // store canonical processor reference on bubble
            bubble._twoRuleProcessor = _p;
            // maintain legacy property if other code expects it
            bubble.processor = _p;
            bubble.dataset.processorInitialized = 'true';
            // register globally for cross-bubble flush if needed
            window._twoRuleProcessors = window._twoRuleProcessors || new Set();
            window._twoRuleProcessors.add(_p);

            // Monitor registry size
            if (window._twoRuleProcessors.size > 50) {
                console.warn(`[PERFORMANCE] ${window._twoRuleProcessors.size} active TwoRule processors`);
            }

            console.log(` Initialized TwoRuleStreamProcessor for Agent ${getAgentName(agentId)}`);
        } catch (error) {
            console.error(` Failed to initialize processor for Agent ${agentId}:`, error);
            bubble.dataset.processorInitialized = 'failed';
        }
    }

    if (data.type === 'content_block_delta') {
        if (data.delta_type === 'text_delta') {
            const text = data.text || '';

            // USE VISUALIZATION ENGINE for streaming
            const _agentProc = bubble._twoRuleProcessor || bubble.processor || null;
            if (_agentProc && bubble.dataset.processorInitialized === 'true') {
                try {
                    const result = _agentProc.processChunk(text);
                    // Handle both sync and async processChunk
                    if (result && typeof result.catch === 'function') {
                        result.catch(err => {
                            console.warn('[WARN] agentProc.processChunk error:', err);
                            bubble.innerHTML += text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
                        });
                    }
                } catch (error) {
                    console.error(` Processor error for Agent ${agentId}:`, error);
                    bubble.innerHTML += text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
                }
            } else {
                // Fallback to plain HTML (escape for safety)
                bubble.innerHTML += text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
            }

            scrollAgentToBottom(agentId);
        }
    } else if (data.type === 'done') {
        // Finalize visualization processing
        const _agentFinal = bubble._twoRuleProcessor || bubble.processor || null;
        if (_agentFinal && bubble.dataset.processorInitialized === 'true') {
            try {
                if (typeof _agentFinal.finalize === 'function') {
                    _agentFinal.finalize();
                }
                console.log(`Finalized visualization for Agent ${getAgentName(agentId)}`);
            } catch (error) {
                console.error(` Finalization error for Agent ${agentId}:`, error);
            }
        }
    }
}

/**
 * Render loaded assistant message with structured content (thinking, tool_use, tool_result, text blocks)
 * This recreates the bubble structure as if it was streamed live
 */
function renderStructuredAgentMessage(agentId, messageContent, threadId = null) {
    const container = document.getElementById(`agent-messages-${agentId}`);
    if (!container) {
        console.error(`Container agent-messages-${agentId} not found`);
        return;
    }

    const threadSlug = threadId || 'unknown';

    console.log(`[Render Structured] Agent ${agentId}, ${messageContent.length} blocks`);

    // Process each block in order
    messageContent.forEach((block, index) => {
        if (block.type === 'thinking') {
            // Create thinking bubble
            const thinkingBubble = document.createElement('div');
            thinkingBubble.className = 'ai-message assistant thinking-bubble collapsed';
            thinkingBubble.dataset.agentId = agentId;
            thinkingBubble.dataset.threadSlug = threadSlug;

            const headerDiv = document.createElement('div');
            headerDiv.className = 'ai-message-header';

            const avatar = document.createElement('div');
            avatar.className = 'ai-message-avatar';
            avatar.innerHTML = '<i class="fa-solid fa-atom"></i>';

            const toggleBtn = document.createElement('button');
            toggleBtn.className = 'ai-message-toggle';
            toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
            toggleBtn.title = 'Collapse/Expand thinking';
            toggleBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                thinkingBubble.classList.toggle('collapsed');
            });

            headerDiv.appendChild(avatar);
            headerDiv.appendChild(toggleBtn);

            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'ai-message-actions';

            const copyBtn = document.createElement('button');
            copyBtn.className = 'ai-message-copy-btn';
            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            copyBtn.title = 'Copy thinking';
            copyBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const content = thinkingBubble.querySelector('.ai-message-content').textContent;
                navigator.clipboard.writeText(content).then(() => {
                    copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                    setTimeout(() => { copyBtn.innerHTML = '<i class="fas fa-copy"></i>'; }, 2000);
                });
            });

            actionsDiv.appendChild(copyBtn);
            headerDiv.appendChild(actionsDiv);

            const contentDiv = document.createElement('div');
            contentDiv.className = 'ai-message-content';
            const thinkingText = block.content || '';
            if (window.marked) {
                try {
                    contentDiv.innerHTML = marked.parse(thinkingText, { breaks: true, gfm: true });
                } catch (e) {
                    contentDiv.textContent = thinkingText;
                }
            } else {
                contentDiv.textContent = thinkingText;
            }

            thinkingBubble.appendChild(headerDiv);
            thinkingBubble.appendChild(contentDiv);
            container.appendChild(thinkingBubble);

            console.log(`[OK] Rendered thinking bubble (${thinkingText.length} chars)`);

        } else if (block.type === 'tool_use') {
            // Create tool bubble
            const toolId = block.id || `tool_${index}`;
            const toolName = block.name || 'unknown_tool';
            const toolInput = block.input || {};

            const toolBubble = document.createElement('div');
            toolBubble.className = 'ai-message assistant tool-bubble collapsed tool-status-complete';
            toolBubble.setAttribute('data-tool-id', toolId);
            toolBubble.dataset.agentId = agentId;
            toolBubble.dataset.threadSlug = threadSlug;

            const headerDiv = document.createElement('div');
            headerDiv.className = 'ai-message-header';

            const avatar = document.createElement('div');
            avatar.className = 'ai-message-avatar';
            avatar.innerHTML = '<i class="fas fa-cog"></i>';

            const toggleBtn = document.createElement('button');
            toggleBtn.className = 'ai-message-toggle';
            toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
            toggleBtn.title = 'Collapse/Expand tool';
            toggleBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                toolBubble.classList.toggle('collapsed');
            });

            headerDiv.appendChild(avatar);
            headerDiv.appendChild(toggleBtn);

            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'ai-message-actions';

            const copyBtn = document.createElement('button');
            copyBtn.className = 'ai-message-copy-btn';
            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            copyBtn.title = 'Copy tool';
            copyBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const content = toolBubble.querySelector('.ai-message-content').textContent;
                navigator.clipboard.writeText(content).then(() => {
                    copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                    setTimeout(() => { copyBtn.innerHTML = '<i class="fas fa-copy"></i>'; }, 2000);
                });
            });

            actionsDiv.appendChild(copyBtn);
            headerDiv.appendChild(actionsDiv);

            const contentDiv = document.createElement('div');
            contentDiv.className = 'ai-message-content';

            let toolInputDisplay = '{ }';
            if (toolInput && typeof toolInput === 'object' && Object.keys(toolInput).length > 0) {
                toolInputDisplay = JSON.stringify(toolInput, null, 2);
            } else if (typeof toolInput === 'string') {
                toolInputDisplay = toolInput;
            }

            contentDiv.innerHTML = `
                        <div><strong>Tool:</strong> ${toolName}</div>
                        <details class="tool-input-details" open>
                            <summary><strong>Input</strong></summary>
                            <pre style="margin-top: 8px; padding: 12px; background: rgba(0,0,0,0.05); border-radius: 6px; overflow-x: auto; font-size: 12px; line-height: 1.4;"><code>${toolInputDisplay}</code></pre>
                        </details>
                    `;

            toolBubble.appendChild(headerDiv);
            toolBubble.appendChild(contentDiv);
            container.appendChild(toolBubble);

            console.log(`[OK] Rendered tool_use bubble: ${toolName}`);

        } else if (block.type === 'tool_result') {
            // Create SEPARATE tool result bubble (matching Prime AI and streaming behavior)
            const toolId = block.tool_use_id;
            const isError = block.is_error || false;
            const resultContent = block.content || '';

            // Update original tool bubble avatar to green (complete)
            const toolBubble = container.querySelector(`[data-tool-id="${toolId}"]`);
            if (toolBubble) {
                toolBubble.classList.remove('tool-status-running', 'tool-status-complete', 'tool-status-error');
                toolBubble.classList.add(isError ? 'tool-status-error' : 'tool-status-complete');
                const avatar = toolBubble.querySelector('.ai-message-avatar');
                if (avatar) {
                    avatar.style.background = isError ? '#ef4444' : '#10b981'; // Red or Green
                }
            }

            // Create SEPARATE tool-result-bubble
            const toolResultBubble = document.createElement('div');
            toolResultBubble.className = 'ai-message assistant tool-result-bubble collapsed';
            toolResultBubble.setAttribute('data-tool-result-id', toolId);
            toolResultBubble.dataset.agentId = agentId;
            toolResultBubble.dataset.threadSlug = threadSlug;

            // Header with white flag icon
            const headerDiv = document.createElement('div');
            headerDiv.className = 'ai-message-header';

            const avatar = document.createElement('div');
            avatar.className = 'ai-message-avatar';
            avatar.style.background = isError ? '#ef4444' : '#60A5FA'; // Red for error, Blue for success
            avatar.innerHTML = '<i class="fas fa-flag" style="color: white; font-size: 14px;"></i>';

            const toggleBtn = document.createElement('button');
            toggleBtn.className = 'ai-message-toggle';
            toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
            toggleBtn.title = 'Collapse/Expand result';
            toggleBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                toolResultBubble.classList.toggle('collapsed');
            });

            headerDiv.appendChild(avatar);
            headerDiv.appendChild(toggleBtn);

            // Copy buttons
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'ai-message-actions';

            // Copy formatted button
            const copyBtn = document.createElement('button');
            copyBtn.className = 'ai-message-copy-btn';
            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            copyBtn.title = 'Copy result';
            copyBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const content = toolResultBubble.querySelector('.ai-message-content').textContent;
                navigator.clipboard.writeText(content).then(() => {
                    copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                    setTimeout(() => { copyBtn.innerHTML = '<i class="fas fa-copy"></i>'; }, 2000);
                });
            });

            // Copy raw button
            const copyRawBtn = document.createElement('button');
            copyRawBtn.className = 'ai-message-copy-btn';
            copyRawBtn.innerHTML = '<i class="fas fa-code"></i>';
            copyRawBtn.title = 'Copy raw result';
            copyRawBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                navigator.clipboard.writeText(resultContent).then(() => {
                    copyRawBtn.innerHTML = '<i class="fas fa-check"></i>';
                    setTimeout(() => { copyRawBtn.innerHTML = '<i class="fas fa-code"></i>'; }, 2000);
                });
            });

            actionsDiv.appendChild(copyBtn);
            actionsDiv.appendChild(copyRawBtn);
            headerDiv.appendChild(actionsDiv);

            // Content
            const contentDiv = document.createElement('div');
            contentDiv.className = 'ai-message-content';

            // Format result nicely
            let formattedResult = resultContent;
            try {
                const parsed = JSON.parse(resultContent);
                formattedResult = JSON.stringify(parsed, null, 2);
            } catch (e) {
                // Keep as-is if not JSON
            }

            const toolName = toolBubble ? toolBubble.querySelector('.ai-message-content')?.textContent.match(/Tool:\s*(.+)/)?.[1] : 'Unknown';

            contentDiv.innerHTML = `
                <div style="margin-bottom: 8px; color: ${isError ? '#ef4444' : '#60A5FA'};">
                    <strong><i class="fas ${isError ? 'fa-times-circle' : 'fa-check-circle'}"></i> Tool Result: ${toolName}</strong>
                </div>
                <pre style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 6px; max-height: 400px; overflow-y: auto;">${formattedResult}</pre>
            `;

            toolResultBubble.appendChild(headerDiv);
            toolResultBubble.appendChild(contentDiv);
            container.appendChild(toolResultBubble);

            console.log(`[OK] Rendered SEPARATE tool-result-bubble for ${toolId} (${isError ? 'ERROR' : 'SUCCESS'})`);

        } else if (block.type === 'text') {
            // Create text bubble (matching streaming behavior)
            const textBubble = document.createElement('div');
            textBubble.className = 'ai-message assistant text-bubble';
            textBubble.dataset.agentId = agentId;
            textBubble.dataset.threadSlug = threadSlug;

            // Extract text content
            const textContent = block.text || block.content || '';
            textBubble.dataset.rawMarkdown = textContent;

            const headerDiv = document.createElement('div');
            headerDiv.className = 'ai-message-header';

            const avatar = document.createElement('div');
            avatar.className = 'ai-message-avatar';
            avatar.innerHTML = `<i class="fas ${MultiAgent.getAgentIcon(agentId)}"></i>`;

            const toggleBtn = document.createElement('button');
            toggleBtn.className = 'ai-message-toggle';
            toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
            toggleBtn.title = 'Collapse/Expand message';
            toggleBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                textBubble.classList.toggle('collapsed');
            });

            headerDiv.appendChild(avatar);
            headerDiv.appendChild(toggleBtn);

            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'ai-message-actions';

            // Copy formatted button
            const copyBtn = document.createElement('button');
            copyBtn.className = 'ai-message-copy-btn';
            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            copyBtn.title = 'Copy message';
            copyBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const content = textBubble.querySelector('.ai-message-content').textContent;
                navigator.clipboard.writeText(content).then(() => {
                    copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                    setTimeout(() => { copyBtn.innerHTML = '<i class="fas fa-copy"></i>'; }, 2000);
                });
            });

            // Copy raw markdown button
            const copyRawBtn = document.createElement('button');
            copyRawBtn.className = 'ai-message-copy-btn';
            copyRawBtn.innerHTML = '<i class="fas fa-code"></i>';
            copyRawBtn.title = 'Copy raw markdown';
            copyRawBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                navigator.clipboard.writeText(textContent).then(() => {
                    copyRawBtn.innerHTML = '<i class="fas fa-check"></i>';
                    setTimeout(() => { copyRawBtn.innerHTML = '<i class="fas fa-code"></i>'; }, 2000);
                });
            });

            actionsDiv.appendChild(copyBtn);
            actionsDiv.appendChild(copyRawBtn);
            headerDiv.appendChild(actionsDiv);

            const contentDiv = document.createElement('div');
            contentDiv.className = 'ai-message-content';
            if (window.marked) {
                try {
                    contentDiv.innerHTML = marked.parse(textContent, { breaks: true, gfm: true });
                } catch (e) {
                    contentDiv.textContent = textContent;
                }
            } else {
                contentDiv.textContent = textContent;
            }

            textBubble.appendChild(headerDiv);
            textBubble.appendChild(contentDiv);
            container.appendChild(textBubble);

            console.log(`[OK] Rendered text bubble (${textContent.length} chars)`);
        }
    });

    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

async function addAgentMessage(agentId, role, content) {
    // Safety check: Ensure UnifiedMessageRenderer is loaded
    if (typeof UnifiedMessageRenderer === 'undefined') {
        console.error('[addAgentMessage] UnifiedMessageRenderer not loaded yet - deferring render');
        // Retry after a short delay to allow script to load
        setTimeout(() => addAgentMessage(agentId, role, content), 100);
        return;
    }

    // Get current thread for this agent
    const currentThread = ThreadManager.getThreadByAgent(getAgentName(agentId));
    const threadId = currentThread ? currentThread.id : 'agent-' + agentId;

    // Use unified message renderer (AI Prime structure)
    const messageDiv = UnifiedMessageRenderer.render(
        `#agent-messages-${agentId}`,
        role === 'ai' ? 'assistant' : role,
        content,
        {
            isThinking: false,
            scrollToBottom: true,
            threadId: threadId,
            syncToBackend: false,
            messageId: null  // Rendered without DB ID context
        }
    );

    if (!messageDiv) {
        console.error(`[Agent ${agentId}] Failed to render message`);
        return;
    }

    // console.log(`[Agent ${agentId}] Message rendered using unified renderer`);
    return messageDiv;

    // OLD CODE BELOW (REPLACED BY UNIFIED RENDERER)
    /*
    const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
    const messageDiv = document.createElement('div');
    messageDiv.className = `agent-message ${role}`;

    // Store raw content for copy functionality
    messageDiv.setAttribute('data-raw-content', content);

    // Create header with avatar, toggle, and actions
    const headerDiv = document.createElement('div');
    headerDiv.className = 'agent-message-header';

    const avatar = document.createElement('div');
    avatar.className = 'agent-message-avatar';
    // Set icon based on role
    if (role === 'user') {
        avatar.innerHTML = '<i class="fas fa-user"></i>';
    } else if (role === 'tool') {
        avatar.innerHTML = '<i class="fas fa-wrench"></i>';
    } else {
        avatar.innerHTML = '<i class="fa-solid fa-atom"></i>';
    }

    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'agent-message-toggle';
    toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
    toggleBtn.title = 'Collapse/Expand message';
    toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        messageDiv.classList.toggle('collapsed');
    });

    headerDiv.appendChild(avatar);
    headerDiv.appendChild(toggleBtn);

    // Add copy buttons
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'agent-message-actions';

    // Copy rendered text button
    const copyRenderedBtn = document.createElement('button');
    copyRenderedBtn.className = 'agent-message-copy-btn';
    copyRenderedBtn.innerHTML = '<i class="fas fa-copy"></i>';
    copyRenderedBtn.title = 'Copy rendered text';
    copyRenderedBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const text = bubbleDiv.innerText || bubbleDiv.textContent;
        navigator.clipboard.writeText(text).then(() => {
            copyRenderedBtn.classList.add('copied');
            copyRenderedBtn.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(() => {
                copyRenderedBtn.classList.remove('copied');
                copyRenderedBtn.innerHTML = '<i class="fas fa-copy"></i>';
            }, 2000);
        });
    });

    // Copy raw content button
    const copyRawBtn = document.createElement('button');
    copyRawBtn.className = 'agent-message-copy-btn';
    copyRawBtn.innerHTML = '<i class="fas fa-code"></i>';
    copyRawBtn.title = 'Copy raw content';
    copyRawBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const rawContent = messageDiv.getAttribute('data-raw-content') || content;
        navigator.clipboard.writeText(rawContent).then(() => {
            copyRawBtn.classList.add('copied');
            copyRawBtn.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(() => {
                copyRawBtn.classList.remove('copied');
                copyRawBtn.innerHTML = '<i class="fas fa-code"></i>';
            }, 2000);
        });
    });

    actionsDiv.appendChild(copyRenderedBtn);
    actionsDiv.appendChild(copyRawBtn);
    headerDiv.appendChild(actionsDiv);

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'agent-message-bubble';

    // CHECK FOR USER INTERACTION REQUEST
    let interactionData = null;
    try {
        // Try to parse content as JSON to detect interaction requests
        const parsed = JSON.parse(content);
        if (parsed.type === 'user_interaction_request_v2' || parsed.type === 'user_interaction_request') {
            interactionData = parsed;
        }
    } catch (e) {
        // Not JSON, continue with normal rendering
    }

    // RENDER USER INTERACTION REQUEST
    if (interactionData) {
        console.log(' Detected user interaction request:', interactionData.interaction_mode);
        bubbleDiv.innerHTML = renderUserInteraction(interactionData, agentId);
    }
    // RENDER AI RESPONSES
    else if (role === 'ai') {
        console.log(` Rendering message for Agent ${agentId}...`);
        console.log(`[DEBUG] Content type: ${typeof content}, length: ${content ? content.length : 0}`);
        console.log(`[DEBUG] Content preview:`, content ? content.substring(0, 200) : 'empty');

        // TRY VISUALIZATION ENGINE FIRST
        if (!window.USE_BASIC_RENDERER && typeof TwoRuleStreamProcessor !== 'undefined') {
            try {
                console.log(` Using TwoRuleStreamProcessor for Agent ${agentId}...`);
                const processor = new TwoRuleStreamProcessor(bubbleDiv);
                processor.processChunk(content);
                // TwoRuleStreamProcessor auto-renders, no finalize needed

                console.log(`Visualization processing complete for Agent ${agentId}`);

                // Verify content was rendered
                if (!bubbleDiv.innerHTML || bubbleDiv.innerHTML.trim() === '') {
                    console.warn(`[WARN] Visualization engine produced empty content for Agent ${agentId}, using basic renderer`);
                    bubbleDiv.innerHTML = renderBasicMarkdown(content);
                }
            } catch (error) {
                console.error(` Visualization engine error for Agent ${agentId}:`, error);
                console.log('↩️ Falling back to basic markdown renderer');
                bubbleDiv.innerHTML = renderBasicMarkdown(content);
            }
        } else {
            // USE BASIC MARKDOWN RENDERER
            console.log(` Using basic markdown renderer for Agent ${agentId}`);
            bubbleDiv.innerHTML = renderBasicMarkdown(content);
        }

        // FINAL SAFETY CHECK
        if (!bubbleDiv.innerHTML || bubbleDiv.innerHTML.trim() === '') {
            console.error(` All rendering methods failed for Agent ${agentId}! Using raw text.`);
            bubbleDiv.textContent = content;
        }

        console.log(`Agent ${agentId} message rendered successfully`);
    } else {
        // For user messages, ensure content is a string
        let displayContent = content;

        // TRIPLE-LAYER SAFETY CHECK: Convert any non-string content to string
        if (typeof displayContent !== 'string') {
            console.warn(`[WARN] User message content is not a string (type: ${typeof displayContent}), converting...`);

            if (displayContent === null || displayContent === undefined) {
                displayContent = '';
            } else if (Array.isArray(displayContent)) {
                // CRITICAL FIX: Handle arrays (Anthropic multi-block format)
                console.log(`[USER MESSAGE] Content is ARRAY with ${displayContent.length} items, extracting text...`);
                displayContent = displayContent
                    .filter(block => block && (block.type === 'text' || block.text || block.content))
                    .map(block => block.text || block.content || '')
                    .join('\n') || JSON.stringify(displayContent, null, 2);
            } else if (typeof displayContent === 'object') {
                // Handle single objects
                displayContent = displayContent.text || displayContent.content || JSON.stringify(displayContent, null, 2);
            } else {
                displayContent = String(displayContent);
            }
            console.log(`[USER MESSAGE] Converted content: "${displayContent.substring(0, 100)}..."`);
        }

        // Final validation before rendering
        if (typeof displayContent !== 'string') {
            console.error(`[ERROR] Content STILL not a string after conversion!`, displayContent);
            displayContent = JSON.stringify(displayContent, null, 2);
        }

        // Render as HTML (preserves line breaks, etc.)
        bubbleDiv.innerHTML = displayContent;
    }                    // Add header and bubble to message
    messageDiv.appendChild(headerDiv);
    messageDiv.appendChild(bubbleDiv);
    messagesContainer.appendChild(messageDiv);
    scrollAgentToBottom(agentId);
    */
}

function scrollAgentToBottom(agentId) {
    const container = document.getElementById(`agent-messages-${agentId}`);
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}

/**
 * Update live viewers badge to show cross-session presence
 * Shows when other sessions/devices are actively viewing this agent
 * @param {number} agentId - Agent column ID
 * @param {number} viewerCount - Number of other sessions viewing (0 to hide badge)
 */
window.updateLiveViewersBadge = function (agentId, viewerCount) {
    const agentColumn = document.getElementById(`agent-${agentId}`);
    if (!agentColumn) {
        console.warn(`[Live Viewers] Agent column ${agentId} not found`);
        return;
    }

    const header = agentColumn.querySelector('.agent-header');
    if (!header) {
        console.warn(`[Live Viewers] Agent ${agentId} header not found`);
        return;
    }

    let badge = header.querySelector('.live-viewers-badge');

    if (viewerCount > 0) {
        if (!badge) {
            // Create badge if it doesn't exist
            badge = document.createElement('div');
            badge.className = 'live-viewers-badge';
            badge.innerHTML = `
                <span class="pulse-dot"></span>
                <span class="viewer-count">${viewerCount}</span>
                <span class="viewer-label">live</span>
            `;
            badge.title = `${viewerCount} other session${viewerCount > 1 ? 's' : ''} viewing`;

            // Insert after agent name
            const agentName = header.querySelector('.agent-name');
            if (agentName && agentName.nextSibling) {
                header.insertBefore(badge, agentName.nextSibling);
            } else {
                header.appendChild(badge);
            }

            console.log(`✅ [Live Viewers] Added badge to Agent ${agentId}: ${viewerCount} viewer(s)`);
        } else {
            // Update existing badge
            const countSpan = badge.querySelector('.viewer-count');
            if (countSpan) {
                countSpan.textContent = viewerCount;
            }
            badge.title = `${viewerCount} other session${viewerCount > 1 ? 's' : ''} viewing`;
            console.log(`🔄 [Live Viewers] Updated badge for Agent ${agentId}: ${viewerCount} viewer(s)`);
        }

        // Add visual highlight to column
        agentColumn.classList.add('other-session-viewing');

        // Auto-remove after 30 seconds (session timeout)
        setTimeout(() => {
            const stillVisible = header.contains(badge);
            if (stillVisible) {
                console.log(`⏰ [Live Viewers] Auto-removing badge from Agent ${agentId} (timeout)`);
                if (badge) badge.remove();
                agentColumn.classList.remove('other-session-viewing');
            }
        }, 30000);

    } else if (badge) {
        // Remove badge if viewer count is 0
        badge.remove();
        agentColumn.classList.remove('other-session-viewing');
        console.log(`🚫 [Live Viewers] Removed badge from Agent ${agentId} (no viewers)`);
    }
};

// Render user interaction UI
function renderUserInteraction(data, agentId) {
    const { message, context, interaction_mode, options, allow_custom_input, button_behavior, level, metadata } = data;

    let html = '<div class="user-interaction-container" data-level="' + (level || 'medium') + '">';

    // Message
    html += '<div class="user-interaction-message">';
    html += '<i class="fas fa-hand-pointer"></i> ';
    html += message;
    html += '</div>';

    // Context (if provided)
    if (context) {
        html += '<div class="user-interaction-context">' + context + '</div>';
    }

    // Metadata (cost/tokens)
    if (metadata && (metadata.estimated_tokens || metadata.estimated_cost_usd)) {
        html += '<div class="user-interaction-metadata">';
        if (metadata.estimated_tokens) {
            html += '<span><i class="fas fa-microchip"></i> ~' + metadata.estimated_tokens + ' tokens</span>';
        }
        if (metadata.estimated_cost_usd) {
            html += '<span><i class="fas fa-dollar-sign"></i> ~$' + metadata.estimated_cost_usd + '</span>';
        }
        html += '</div>';
    }

    // Buttons
    if (options && options.length > 0) {
        html += '<div class="user-interaction-buttons">';
        options.forEach((opt, idx) => {
            const optData = typeof opt === 'string' ? JSON.parse(opt) : opt;
            const btnClass = 'user-interaction-btn';
            const value = optData.value || optData.label;
            const behavior = button_behavior || 'submit';

            html += '<button class="' + btnClass + '" ';
            html += 'data-value="' + value + '" ';
            html += 'data-behavior="' + behavior + '" ';
            html += 'onclick="handleUserInteractionClick(\'' + agentId + '\', \'' + value + '\', \'' + behavior + '\')" ';
            html += 'title="' + (optData.description || '') + '">';
            html += optData.label;
            html += '</button>';
        });
        html += '</div>';
    }

    // Text input (if allowed)
    if (allow_custom_input) {
        html += '<div class="user-interaction-input-wrapper">';
        html += '<textarea class="user-interaction-input" ';
        html += 'id="interaction-input-' + agentId + '" ';
        html += 'placeholder="' + (data.input_placeholder || 'Type your response...') + '">';
        html += '</textarea>';
        html += '<button class="user-interaction-submit-btn" ';
        html += 'onclick="handleUserInteractionSubmit(\'' + agentId + '\')">';
        html += '<i class="fas fa-paper-plane"></i> Send';
        html += '</button>';
        html += '</div>';
    }

    html += '</div>';
    return html;
}

// Handle interaction button click
function handleUserInteractionClick(agentId, value, behavior) {
    if (behavior === 'submit') {
        // Immediate submit
        sendAgentMessage(agentId, value);
    } else if (behavior === 'insert') {
        // Insert into text field
        const input = document.getElementById('interaction-input-' + agentId);
        if (input) {
            input.value = value;
            input.focus();
        }
    }
}

// Handle interaction text submit
function handleUserInteractionSubmit(agentId) {
    const input = document.getElementById('interaction-input-' + agentId);
    if (input && input.value.trim()) {
        sendAgentMessage(agentId, input.value.trim());
        input.value = '';
    }
}

// Update agent status indicator
function updateAgentStatus(agentId, status, text = null) {
    const statusIndicator = document.getElementById(`status-${agentId}`);
    if (!statusIndicator) return;

    statusIndicator.setAttribute('data-status', status);

    const statusText = statusIndicator.querySelector('.status-text');
    if (statusText && text) {
        statusText.textContent = text;
    } else if (statusText) {
        // Default text based on status
        const statusTexts = {
            'ready': 'Ready',
            'thinking': 'Thinking...',
            'working': 'Working...',
            'error': 'Error'
        };
        statusText.textContent = statusTexts[status] || 'Unknown';
    }

    console.log(` Agent ${getAgentName(agentId)} status: ${status}${text ? ` (${text})` : ''}`);
}

function saveThread(agentId) {
    // TODO: Implement thread saving
    toggleAgentMenu(agentId);
    showNotification(`Thread saved for Agent ${getAgentName(agentId)}`, 'success');
}

// ==================== TOOL STATISTICS DISPLAY ====================
function displayToolStats() {
    console.log('[CHART] Displaying tool statistics...');

    const stats = {
        totalTools: ToolManager.availableTools.length,
        platforms: ToolManager.toolsByPlatform.size,
        byPlatform: {}
    };

    // Get tool counts by platform
    for (const [platform, tools] of ToolManager.toolsByPlatform.entries()) {
        stats.byPlatform[platform] = tools.length;
    }

    console.log('[CHART] Tool Statistics:');
    console.log(`   Total Tools: ${stats.totalTools}`);
    console.log(`   Platforms: ${stats.platforms}`);
    console.log('   By Platform:', stats.byPlatform);

    // Display top platforms
    const topPlatforms = Object.entries(stats.byPlatform)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);

    console.log('[CHART] Top 10 Platforms:');
    topPlatforms.forEach(([platform, count], index) => {
        console.log(`   ${index + 1}. ${platform}: ${count} tools`);
    });
}

// ==================== TOOL USAGE MONITOR ====================
function showToolUsageStats() {
    const stats = ToolManager.getToolStats();

    showNotification('Tool usage stats logged to console', 'info');
    console.log('[CHART] TOOL USAGE STATISTICS:');
    console.log(`   Total Calls: ${stats.totalCalls}`);
    console.log(`   Success Rate: ${stats.successRate}%`);
    console.log(`   Average Duration: ${stats.avgDuration}ms`);
    console.log('   Top Tools:', stats.topTools);
}

// Close menus when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.agent-hamburger-menu')) {
        document.querySelectorAll('.agent-menu-dropdown').forEach(menu => {
            menu.classList.remove('show');
        });
    }
});

// ==================== PAGINATION REMOVED ====================
// ✅ ALL messages now load immediately - no delayed loading or scroll triggers
// This prevents user confusion and ensures complete conversation history is always visible

// ==================== EXPOSE TO GLOBAL SCOPE ====================
// NOTE: initMultiAgent is defined at line 1928 (comprehensive implementation)
// DO NOT add duplicate definition here - it will overwrite the original!
// Required for main app initialization
window.initMultiAgent = initMultiAgent;
window.MultiAgent = MultiAgent;
console.log('✅ [AGENT-JS] Module loaded successfully - initMultiAgent and MultiAgent exported to window scope');
console.log(`✅ [AGENT-JS] File size: ${document.currentScript?.src || 'unknown'} - ready for initialization`);