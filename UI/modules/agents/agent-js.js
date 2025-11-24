
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

// ==================== MULTI-AGENT NATO COLUMNS ====================
const MultiAgent = {
    nextAgentId: 4,
    agentNames: ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel',
        'India', 'Juliet', 'Kilo', 'Lima', 'Mike', 'November', 'Oscar', 'Papa',
        'Quebec', 'Romeo', 'Sierra', 'Tango', 'Uniform', 'Victor', 'Whiskey', 'X-ray', 'Yankee', 'Zulu'],

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

        // Clear loaded thread state
        delete this.loadedThreads[agentId];
        this.sessions[agentId] = null;
        console.log(`[ISOLATION] ✅ Agent-${agentId} session cleared`);

        // Clear UI
        const messagesContainer = document.querySelector(`#agent-${agentId} .agent-messages-container`);
        if (messagesContainer) {
            messagesContainer.innerHTML = '';
        }

        // Update thread info header - Show thread selector dropdown
        const threadInfoContainer = document.getElementById(`thread-info-${agentId}`);
        if (threadInfoContainer) {
            threadInfoContainer.innerHTML = `
                <div class="thread-info-wrapper">
                    <div class="no-thread-message clickable" onclick="AgentColumn.showThreadSelector(${agentId})">
                        <i class="fas fa-inbox"></i> 
                        <span>Click to select a thread</span>
                        <i class="fas fa-chevron-down" style="margin-left: auto; font-size: 10px;"></i>
                    </div>
                    <div class="thread-selector-dropdown" id="thread-selector-${agentId}" style="display: none;"></div>
                </div>
            `;
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

            badge.innerHTML = `
                        <i class="fas ${agentIcon}"></i>
                        <span>${agentName}</span>
                        ${messageCount > 0 ? `<span class="thread-indicator">${messageCount}</span>` : ''}
                    `;

            badge.onclick = () => this.scrollToAgent(i);
            navContainer.appendChild(badge);
        }

        console.log(`✅ [Command Center] Quick nav built with ${maxAgentId} agent badges (from backend assignments)`);
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
    },

    // Remove badge when agent closed
    removeQuickNavBadge(agentId) {
        const badge = document.getElementById(`quick-nav-badge-${agentId}`);
        if (badge) {
            badge.remove();
            console.log(`[Command Center] Removed badge for ${this.getAgentName(agentId)}`);
            this.updateDashboardStats();
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

        // Synergy link (clickable)
        if (threadInfo?.synergyCardId) {
            const synergyName = threadInfo.synergySessionName || threadInfo.synergyCardId;
            links.push(`<div class="agent-tooltip-synergy-badge" data-synergy-id="${threadInfo.synergyCardId}" style="display: inline-flex; align-items: center; gap: 4px; padding: 6px 10px; background: #10b981; border-radius: 4px; font-size: 11px; cursor: pointer; transition: all 0.2s ease;" onmouseover="this.style.background='#059669'" onmouseout="this.style.background='#10b981'" title="Click to open Synergy session">
                        <i class="fas fa-link"></i>
                        <span>${synergyName}</span>
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

        // Get actual message count from thread data
        let messageCount = 0;
        if (threadInfo?.threadId && typeof ThreadManager !== 'undefined' && Array.isArray(ThreadManager.threads)) {
            const thread = ThreadManager.threads.find(t => t.id === threadInfo.threadId);
            if (thread) {
                messageCount = thread.messages?.length || thread.message_count || 0;
            }
        }

        // Highlight badge if has thread or messages
        if (threadInfo || messageCount > 0) {
            badge.classList.add('has-thread');

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
    scrollToAgent(agentId) {
        const column = document.getElementById(`agent-${agentId}`);
        if (!column) {
            console.warn(`[MultiAgent] Column agent-${agentId} not found`);
            return;
        }

        // Expand if collapsed
        if (column.classList.contains('collapsed')) {
            this.expandColumn(agentId);
        }

        // Scroll into view
        column.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest',
            inline: 'center'
        });

        // Highlight briefly
        column.style.transition = 'all 0.3s ease';
        column.style.boxShadow = '0 0 20px rgba(37, 123, 221, 0.6)';
        setTimeout(() => {
            column.style.boxShadow = '';
        }, 1000);

        // Update active state in nav
        document.querySelectorAll('.agent-quick-nav-badge').forEach(b => {
            b.classList.toggle('active', parseInt(b.dataset.agentId) === agentId);
        });

        console.log(`[Command Center] Scrolled to ${this.getAgentName(agentId)}`);
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

    // Refresh all agents
    refreshAllAgents() {
        console.log('[Command Center] Refreshing all agents...');
        Object.keys(this.loadedThreads).forEach(agentId => {
            this.updateAgentHeader(parseInt(agentId));
        });
        this.updateDashboardStats();
        if (typeof showNotification === 'function') {
            showNotification('All agents refreshed', 'success');
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
        const messagesContainer = document.querySelector(`#agent-${agentId} .agent-messages-container`);
        if (messagesContainer) {
            // Clean up processors
            messagesContainer.querySelectorAll('[data-processor-initialized]').forEach(bubble => {
                if (bubble.processor && typeof bubble.processor.cleanup === 'function') {
                    bubble.processor.cleanup();
                }
            });
            messagesContainer.innerHTML = '';
        }

        // 2. Unassign thread from database (removes agent assignment)
        if (typeof ThreadManager !== 'undefined') {
            await ThreadManager.unassignThread(threadId);
            console.log(`[OK] Thread ${threadId} unassigned from database`);
        }

        // 3. Remove from MultiAgent state
        delete this.loadedThreads[agentId];
        delete this.sessions[agentId];

        // 4. Update agent header to show empty state
        this.updateAgentHeader(agentId);

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
            UIComponents.showConfirmation({
                title: 'Replace Prime Session?',
                message: 'Prime panel has an active session. Moving this thread will replace the current Prime session. Continue?',
                variant: 'warning',
                confirmLabel: 'Replace',
                cancelLabel: 'Cancel',
                onConfirm: () => {
                    this.executeThreadMove(agentId, threadInfo);
                }
            });
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
            // First, assign to prime-loaded (this updates database and enables page reload restoration)
            await ThreadManager.assignThread(threadInfo.threadId, 'prime-loaded');
            console.log(`[MultiAgent] [OK] Thread ${threadInfo.threadId} assigned to 'prime-loaded' in centralized tracker`);

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
                                    Thread History
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
    loadThreadIntoAgent(agentId, thread) {
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
                threadInfoContainer.innerHTML = cardHtml;
                console.log(`✅ [LOAD] Thread info card rendered (${cardHtml.length} chars)`);
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
        const messagesContainer = document.querySelector(`#agent-${agentId} .agent-messages-container`);
        if (!messagesContainer) {
            console.error(`[ERROR] Messages container not found for agent-${agentId}`);
            return;
        }

        messagesContainer.innerHTML = '';

        // CRITICAL FIX: Remove empty state first, then create messages container
        const emptyState = messagesContainer.querySelector('.empty-state');
        if (emptyState) {
            emptyState.remove();
            console.log(`[LOAD] Removed empty state for agent-${agentId}`);
        }

        // CRITICAL FIX: Always create messages container first
        const messagesDiv = document.createElement('div');
        messagesDiv.className = 'agent-messages';
        messagesDiv.id = `messages-${agentId}`;
        messagesContainer.appendChild(messagesDiv);

        // Load messages from MessageStore (centralized storage)
        const storedMessages = window.MessageStore.getMessages(thread.id);
        console.log(`📦 [MessageStore] Retrieved ${storedMessages.length} messages for Agent ${agentId}`);

        if (!storedMessages || storedMessages.length === 0) {
            if (thread.message_count > 0) {
                console.log(`[LOAD] Fetching ${thread.message_count} messages for thread ${thread.id} from backend...`);

                // Show processing indicator while loading messages
                const processingIndicator = createProcessingIndicator(agentId);
                messagesDiv.appendChild(processingIndicator);

                if (typeof ThreadManager !== 'undefined' && ThreadManager.loadMessagesForThread) {
                    ThreadManager.loadMessagesForThread(thread.id).then(() => {
                        // Re-fetch from MessageStore after backend load
                        const loadedMessages = window.MessageStore.getMessages(thread.id);
                        if (loadedMessages && loadedMessages.length > 0) {
                            console.log(`[LOAD] Rendering ${loadedMessages.length} messages...`);

                            // Remove processing indicator before rendering messages
                            removeProcessingIndicator(agentId);

                            loadedMessages.forEach((msg, index) => {
                                // USE SAME PATHWAY AS AI PRIME: UnifiedMessageRenderer
                                console.log(`[LOAD] Rendering message ${index + 1}/${loadedMessages.length} (${msg.role})`);

                                if (typeof UnifiedMessageRenderer !== 'undefined') {
                                    // PRIME PATHWAY: Use UnifiedMessageRenderer for ALL messages
                                    UnifiedMessageRenderer.render(
                                        messagesDiv,
                                        msg.role,
                                        msg.content,
                                        {
                                            threadId: thread.id,
                                            syncToBackend: false,
                                            scrollToBottom: false  // Manual scroll at end
                                        }
                                    );
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
                            });
                            messagesContainer.scrollTop = messagesContainer.scrollHeight;
                            console.log(`[OK] All ${loadedMessages.length} messages rendered for agent-${agentId}`);
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
            console.log(`[LOAD] Rendering ${storedMessages.length} messages from MessageStore...`);
            storedMessages.forEach((msg, index) => {
                // USE SAME PATHWAY AS AI PRIME: UnifiedMessageRenderer
                console.log(`[LOAD] Rendering message ${index + 1}/${storedMessages.length} (${msg.role})`);

                if (typeof UnifiedMessageRenderer !== 'undefined') {
                    // PRIME PATHWAY: Use UnifiedMessageRenderer for ALL messages
                    UnifiedMessageRenderer.render(
                        messagesDiv,
                        msg.role,
                        msg.content,
                        {
                            threadId: thread.id,
                            syncToBackend: false,
                            scrollToBottom: false  // Manual scroll at end
                        }
                    );
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
            });
            console.log(`[OK] All ${storedMessages.length} messages rendered for agent-${agentId}`);
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

        // CRITICAL: Show input area wrapper now that thread is loaded
        const agentInputArea = document.querySelector(`#agent-${agentId} .agent-input-area`);
        if (agentInputArea) {
            // Ensure input area stacks vertically (attached files above input)
            agentInputArea.style.display = 'block';
            console.log(`[UI] Showed agent-${agentId} input area (thread loaded)`);
        }

        // Also ensure input field is enabled
        const inputEl = document.querySelector(`#agent-${agentId} textarea`);
        const sendBtn = document.querySelector(`#agent-${agentId} .agent-send-btn`);

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
    },

    // Unload thread from agent and move to Prime
    async unloadThreadFromAgent(location, threadId) {
        console.log(`[UNLOAD] Unloading thread ${threadId} from ${location}`);

        // Extract agent ID from location (e.g., "agent-2" -> 2)
        const agentId = parseInt(location.replace('agent-', ''));

        if (!agentId || isNaN(agentId)) {
            console.error('[UNLOAD] Invalid agent location:', location);
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

        // Clear agent column UI - Show thread selector dropdown
        const threadInfoContainer = document.getElementById(`thread-info-${agentId}`);
        if (threadInfoContainer) {
            threadInfoContainer.innerHTML = `
                <div class="thread-info-wrapper">
                    <div class="no-thread-message clickable" onclick="AgentColumn.showThreadSelector(${agentId})">
                        <i class="fas fa-inbox"></i> 
                        <span>Click to select a thread</span>
                        <i class="fas fa-chevron-down" style="margin-left: auto; font-size: 10px;"></i>
                    </div>
                    <div class="thread-selector-dropdown" id="thread-selector-${agentId}" style="display: none;"></div>
                </div>
            `;
        }

        // Clear messages
        const messagesContainer = document.querySelector(`#agent-${agentId} .agent-messages-container`);
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
                                        Thread History
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
        // Calling it here would close the Thread History panel before the inline update can happen
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

        // Toggle wide class
        const isWide = column.classList.contains('wide');

        if (isWide) {
            // Shrink to normal width
            column.classList.remove('wide');
            // Show chevron-right (→) to indicate "click to widen"
            icon.className = 'fas fa-chevron-right';
            console.log(`[SIZE] ${this.getAgentName(agentId)} width: 400px(normal)`);
        } else {
            // Expand to wide width
            column.classList.add('wide');
            // Show chevron-left (←) to indicate "click to narrow"
            icon.className = 'fas fa-chevron-left';
            console.log(`[SIZE] ${this.getAgentName(agentId)} width: 600px(wide)`);
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
                    messagesContainer.innerHTML = '';

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

    // Clear any stale localStorage data (backend is source of truth)
    MultiAgent.loadState();

    const container = document.getElementById('multi-agent-container');
    if (!container) {
        console.error('❌ [Multi-Agent] Container not found');
        return;
    }

    // CRITICAL: Load all threads FIRST before trying to use them
    if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.loadThreadsFromBackend === 'function') {
        console.log('📥 [initMultiAgent] Loading threads from backend FIRST...');
        await ThreadManager.loadThreadsFromBackend();
        console.log(`✅ [initMultiAgent] Threads loaded: ${ThreadManager.threads?.length || 0} threads in memory`);
    } else {
        console.error('❌ [initMultiAgent] ThreadManager.loadThreadsFromBackend not available!');
    }

    // STEP 1: Fetch thread assignments from backend (authoritative source)
    let assignments = {};
    if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.getThreadAssignments === 'function') {
        assignments = await ThreadManager.getThreadAssignments();
        console.log('✅ [Multi-Agent] Fetched thread assignments from backend:', assignments);
    } else {
        console.warn('⚠️ [Multi-Agent] ThreadManager.getThreadAssignments not available');
    }

    // STEP 2: Calculate agent count from ACTUAL backend assignments
    const agentIdsWithThreads = Object.keys(assignments)
        .filter(loc => loc.startsWith('agent-'))
        .map(loc => parseInt(loc.replace('agent-', '')))
        .filter(id => !isNaN(id));

    // Calculate max agent ID (minimum 3, or highest assigned + 1)
    const maxAssignedAgent = agentIdsWithThreads.length > 0 ? Math.max(...agentIdsWithThreads) : 0;
    const maxAgentId = Math.max(maxAssignedAgent + 1, 3);  // Always create at least 3 agents

    // Update nextAgentId based on actual usage (not localStorage)
    MultiAgent.nextAgentId = maxAgentId + 1;

    console.log(`📊 [Multi-Agent] Creating ${maxAgentId} agents (assigned agents: [${agentIdsWithThreads.sort().join(', ')}])`);

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

        // [NEW] STEP 4: Check if this agent has a thread assigned
        const hasThread = assignments[`agent-${i}`];

        // ALL agents are EXPANDED by default now (no auto-collapse)
        console.log(`[OK][Multi-Agent] ${MultiAgent.getAgentName(i)} is EXPANDED (has thread: ${!!hasThread})`);
    }

    // Build agent quick-nav bar (using actual agent count from backend)
    MultiAgent.buildQuickNav(maxAgentId, assignments);
    console.log(`✅ [Command Center] Quick nav built with ${maxAgentId} agent badges (from backend assignments)`);

    // Update stats
    MultiAgent.updateDashboardStats();

    // STEP 4.5: GUARANTEE DOM container existence before loading threads
    // Wait for all agent column DOM elements to be fully created and inserted
    console.log(`⏳ [initMultiAgent] Verifying DOM containers for ${maxAgentId} agents...`);
    const containerVerificationPromises = [];

    for (let i = 1; i <= maxAgentId; i++) {
        const promise = new Promise((resolve) => {
            // Check immediately first
            let container = document.getElementById(`thread-info-${i}`);
            if (container) {
                console.log(`✅ [initMultiAgent] Agent-${i} container ready (immediate)`);
                resolve();
                return;
            }

            // If not found, wait with short timeout for DOM insertion
            let attempts = 0;
            const maxAttempts = 10;
            const checkInterval = setInterval(() => {
                container = document.getElementById(`thread-info-${i}`);
                attempts++;

                if (container) {
                    console.log(`✅ [initMultiAgent] Agent-${i} container ready (after ${attempts * 50}ms)`);
                    clearInterval(checkInterval);
                    resolve();
                } else if (attempts >= maxAttempts) {
                    console.error(`❌ [initMultiAgent] Agent-${i} container NOT created after ${maxAttempts * 50}ms!`);
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

    // STEP 5: LOAD threads on page initialization (not just restore to memory)
    // CRITICAL: Load prime-loaded thread FIRST, then agent threads

    // STEP 5A: INITIALIZE PRIME PANEL (same pattern as agent columns)
    // Check if prime-loaded thread exists and render appropriate content
    const primeThreadInfoContainer = document.getElementById('prime-thread-info');
    if (!primeThreadInfoContainer) {
        console.warn(`⚠️ [initMultiAgent] Prime thread-info container NOT FOUND - thread info cards won't render`);
    } else {
        console.log(`✅ [initMultiAgent] Prime thread-info container ready`);

        // Check for prime-loaded thread assignment
        const primeLoadedThreadId = assignments['prime-loaded'];
        const primeLoadedThread = primeLoadedThreadId
            ? ThreadManager.threads.find(t => t.id === primeLoadedThreadId)
            : null;

        if (primeLoadedThread && typeof ThreadManager !== 'undefined') {
            // Thread is assigned - load and render thread card
            console.log(`🎯 [initMultiAgent] Prime has prime-loaded thread: ${primeLoadedThreadId}, loading...`);
            await ThreadManager.loadThreadInPrime(primeLoadedThreadId);

            // Update thread info card for Prime
            if (typeof ThreadManager.renderThreadInfoContainer === 'function') {
                // Render with compact=false for full card display
                const cardHtml = ThreadManager.renderThreadInfoContainer('prime', primeLoadedThreadId, false);
                if (cardHtml) {
                    primeThreadInfoContainer.innerHTML = cardHtml;
                    console.log(`✅ [initMultiAgent] Prime thread card rendered (${cardHtml.length} chars, replaced empty state)`);
                } else {
                    console.error(`❌ [initMultiAgent] Prime card HTML is empty!`);
                }
            }
        } else {
            // No prime-loaded thread - ensure empty state is shown
            console.log(`📭 [initMultiAgent] No prime-loaded thread assigned, keeping empty state`);
            // Empty state already in HTML, no action needed
        }
    }

    // Then load all agent-assigned threads
    const agentLoadPromises = [];
    Object.keys(assignments).forEach(location => {
        const threadId = assignments[location];
        if (!threadId) return;

        if (location === 'prime' || location === 'prime-loaded') {
            // Already handled above or not a loaded thread
            return;
        } else if (location.startsWith('agent-')) {
            // Thread assigned to agent column
            const agentId = parseInt(location.replace('agent-', ''));
            if (!isNaN(agentId) && typeof ThreadManager !== 'undefined' && Array.isArray(ThreadManager.threads)) {
                const thread = ThreadManager.threads.find(t => t.id === threadId);
                if (thread) {
                    // Update MultiAgent state
                    MultiAgent.loadedThreads[agentId] = {
                        threadId: thread.id,
                        threadTitle: thread.title
                    };
                    MultiAgent.sessions[agentId] = threadId;

                    // Tag thread with agent name
                    const agentName = MultiAgent.getAgentName(agentId);
                    thread.agent = agentName;
                    console.log(`[OK] Tagged thread "${thread.title}" with agent: ${agentName}`);

                    // Load thread immediately (no setTimeout delay)
                    const loadPromise = (async () => {
                        // Clear welcome message
                        const messagesContainer = document.querySelector(`#agent-${agentId} .agent-messages-container`);
                        if (messagesContainer) {
                            messagesContainer.innerHTML = '<div class="agent-messages" id="agent-messages-' + agentId + '"></div>';
                        }

                        // Load thread with full rendering
                        await MultiAgent.loadThreadIntoAgent(agentId, thread);
                        console.log(`✅ [initMultiAgent] Loaded thread "${thread.title}" into ${agentName}`);

                        // Update thread info card for agent column
                        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.renderThreadInfoContainer === 'function') {
                            console.log(`📋 [initMultiAgent] Rendering thread info card for agent-${agentId}, thread: ${thread.id}`);
                            // Use compact=true for agent columns (matches initial render during createAgentColumn)
                            const cardHtml = ThreadManager.renderThreadInfoContainer(`agent-${agentId}`, thread.id, true);
                            console.log(`📋 [initMultiAgent] Card HTML generated: ${cardHtml ? cardHtml.length + ' chars' : 'NULL'}`);

                            const threadInfoContainer = document.getElementById(`thread-info-${agentId}`);
                            console.log(`📋 [initMultiAgent] Container element:`, threadInfoContainer ? 'FOUND' : 'NOT FOUND');

                            if (threadInfoContainer && cardHtml) {
                                // CRITICAL: Replace entire innerHTML (removes empty state if present)
                                threadInfoContainer.innerHTML = cardHtml;
                                console.log(`✅ [initMultiAgent] Updated thread info card for ${agentName} (replaced empty state with thread card)`);
                                console.log(`✅ [initMultiAgent] Container HTML after injection:`, threadInfoContainer.innerHTML.substring(0, 100) + '...');
                            } else if (!threadInfoContainer) {
                                console.error(`❌ [initMultiAgent] thread-info-${agentId} container NOT FOUND in DOM!`);
                            } else {
                                console.error(`❌ [initMultiAgent] Card HTML is empty or null!`);
                            }
                        } else {
                            console.error(`❌ [initMultiAgent] ThreadManager or renderThreadInfoContainer NOT available!`);
                        }

                        // Update header
                        MultiAgent.updateAgentHeader(agentId);
                    })();

                    agentLoadPromises.push(loadPromise);
                } else {
                    console.warn(`[WARN] Thread ${threadId} not found for location ${location}`);
                }
            }
        }
    });

    // Wait for all agent threads to finish loading
    if (agentLoadPromises.length > 0) {
        console.log(`⏳ [initMultiAgent] Waiting for ${agentLoadPromises.length} agent threads to load...`);
        await Promise.all(agentLoadPromises);
        console.log(`✅ [initMultiAgent] All agent threads loaded successfully`);
    }

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
                            messagesContainer.innerHTML = '<div class="agent-messages" id="agent-messages-' + agentIdNum + '"></div>';
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

    // Setup thread history as "dead zone" - drops here are ignored (no action)
    setTimeout(() => {
        const threadMenu = document.getElementById('thread-menu');
        if (threadMenu) {
            threadMenu.addEventListener('drop', (e) => {
                e.stopPropagation();
                e.preventDefault();
                console.log('🛑 [Drop] Dropped in thread history - no action (dead zone)');
                // Clear all drag-over states
                document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
            });
            threadMenu.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'none'; // Show "not allowed" cursor
            });
            console.log('✅ [Drop Zone] Thread history configured as dead zone (drops ignored)');
        }
    }, 150);

    // Validate and fix any assignment inconsistencies
    if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.validateAssignments === 'function') {
        setTimeout(async () => {
            const validation = await ThreadManager.validateAssignments();
            if (validation.fixed) {
                console.log(' [Multi-Agent] Assignment inconsistencies detected and fixed on page load');
            }
        }, 500);
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

function createAgentColumn(agentId) {
    const container = document.getElementById('multi-agent-container');
    const agentName = MultiAgent.getAgentName(agentId);

    // Check if agent column already exists (prevent duplicates)
    const existingColumn = document.getElementById(`agent-${agentId}`);
    if (existingColumn) {
        console.log(`[Multi-Agent] Agent ${agentName} already exists, skipping creation`);
        return;
    }

    // Generate session ID for this agent if not exists
    if (!MultiAgent.sessions[agentId]) {
        MultiAgent.sessions[agentId] = generateSessionId();
    }

    const column = document.createElement('div');
    column.className = 'agent-column';
    column.id = `agent-${agentId}`;
    column.dataset.agentId = agentId;

    // FIXED: Get thread by checking thread.location (database source of truth)
    // Don't rely on loadedThreads (in-memory state that can be stale)
    const location = `agent-${agentId}`;
    const threadInAgent = (typeof ThreadManager !== 'undefined' && ThreadManager.threads && Array.isArray(ThreadManager.threads))
        ? ThreadManager.threads.find(t => t.location === location)
        : null;

    const threadId = threadInAgent ? threadInAgent.id : null;

    // Use unified thread-info container (same as Prime)
    // Thread info card will be populated when thread is loaded via initMultiAgent()
    // Show loading spinner ONLY if thread is assigned, otherwise show nothing (thread loads during init)
    let threadInfoHtml = threadInAgent 
        ? '<div class="agent-thread-placeholder" style="padding: 12px; color: var(--text-muted); font-size: 13px;"><i class="fas fa-spinner fa-spin"></i> Loading...</div>'
        : '<div class="agent-thread-placeholder" style="padding: 12px; color: var(--text-muted); font-size: 13px; opacity: 0;"></div>';

    column.innerHTML = `
            <!-- Collapsed Column Bar (hidden by default) -->
            <div class="collapsed-column-bar" onclick="MultiAgent.expandColumn(${agentId})">
                    <button class="expand-btn" title="Expand column">
                        <i class="fas fa-chevron-right"></i>
                    </button>
                    <div class="agent-name-vertical">${agentName}</div>
                    <div class="thread-info-vertical">
                        <div class="thread-status-vertical" id="collapsed-status-${agentId}">No Thread</div>
                        <div class="thread-timestamp-vertical" id="collapsed-timestamp-${agentId}"></div>
                    </div>
                </div>

                <div class="agent-header">
                    <!-- Header Top Row: [Collapse] [Agent Title] [Width Toggle] [Hamburger] -->
                    <div class="agent-header-top" style="position: relative; display: flex; align-items: center; justify-content: center; padding: 0px;">
                        <button class="collapse-btn" onclick="event.stopPropagation(); MultiAgent.collapseColumn(${agentId})" title="Collapse column" style="position: absolute; left: 10px; z-index: 10;">
                            <i class="fas fa-chevron-down"></i>
                        </button>
                        
                        <div class="agent-title-wrapper" style="display: flex; align-items: center; justify-content: center; gap: 10px;">
                            <i class="fas ${MultiAgent.getAgentIcon(agentId)}" style="font-size: 1.2em; color: white;"></i>
                            <h2 style="margin: 0;">${agentName}</h2>
                        </div>
                        
                        <div class="agent-header-controls" style="position: absolute; right: 12px; z-index: 10; display: flex; gap: 8px;">
                            <button class="width-toggle-btn" onclick="event.stopPropagation(); MultiAgent.toggleColumnWidth(${agentId})" title="Toggle column width">
                                <i class="fas fa-chevron-right" id="width-icon-${agentId}"></i>
                            </button>
                            <button class="agent-hamburger-button" onclick="event.stopPropagation(); toggleAgentMenu(${agentId})">
                                <i class="fas fa-ellipsis-v"></i>
                            </button>
                        </div>
                    </div>

                    <div class="agent-menu-dropdown" id="menu-${agentId}">
                        <div class="agent-menu-item" onclick="event.stopPropagation(); ThreadManager.showNewChatModal('agent-${agentId}'); toggleAgentMenu(${agentId})">
                            <i class="fas fa-plus"></i> New Thread
                        </div>
                        <div class="agent-menu-divider"></div>
                        <div class="agent-menu-item" onclick="event.stopPropagation(); ThreadManager.toggleThreadMenu(); toggleAgentMenu(${agentId})">
                            <i class="fas fa-history"></i> Thread History
                        </div>
                        <div class="agent-menu-divider"></div>
                        <div class="agent-menu-item close-agent" onclick="event.stopPropagation(); closeAgentColumn(${agentId})">
                            <i class="fas fa-times"></i> Close Agent
                        </div>
                    </div>

                    <!-- Universal thread-info container (uses ai-chat-header-info structure) -->
                    <div id="thread-info-${agentId}">
                        ${threadInfoHtml}
                    </div>

                </div>
                
                <div class="agent-messages-container" id="agent-messages-${agentId}">
                    <div class="empty-state" style="padding-top: 60%; text-align: center;">
                        <div style="line-height: 1.8; padding: 0 20px; max-width: 500px; margin: 0 auto;">
                            <div style="font-size: 2em; margin-bottom: 15px;">
                                
                            </div>
                            <div style="font-size: 1.2em; margin-bottom: 12px; font-weight: 600; color: var(--text-primary, #e5e7eb);">
                                ${agentName} Ready
                            </div>
                            <div style="margin-bottom: 20px; opacity: 0.8; font-size: 0.95em; color: var(--text-secondary, #9ca3af);">
                                No active thread — start a new chat or load from history
                            </div>
                            <div style="background: rgba(255, 255, 255, 0.05); padding: 14px; border-radius: 8px; border-left: 3px solid var(--accent-primary, #667eea); margin-bottom: 20px; text-align: left;">
                                <div style="font-weight: 600; margin-bottom: 8px; font-size: 0.9em; color: var(--text-primary, #e5e7eb);"> Quick Tip</div>
                                <div style="opacity: 0.85; font-size: 0.85em; line-height: 1.6; color: var(--text-secondary, #9ca3af);">
                                    <strong>Drag & drop threads</strong> from the sidebar to move conversations between agents. 
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
                                    Thread History
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="agent-input-area">
                    <!-- File attachment preview -->
                    <div id="agent-attached-files-${agentId}" class="agent-attached-files"></div>
                    
                    <div class="agent-input-group">
                        <!-- Center: Textarea -->
                        <div class="agent-input-center">
                            <textarea id="input-${agentId}" onkeydown="handleAgentKeypress(event, ${agentId})"></textarea>
                        </div>

                        <!-- Right: Action buttons -->
                        <div class="agent-input-right-buttons">
                            <button id="attach-${agentId}" class="agent-attach-btn" title="Attach files">
                                <i class="fas fa-paperclip"></i>
                            </button>
                            <button id="send-${agentId}" class="agent-send-btn" onclick="sendAgentMessage(${agentId})">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </div>

                        <input type="file" id="file-input-${agentId}" class="agent-file-input" multiple accept="application/pdf,image/*" style="display: none;">
                    </div>
                </div>
        `;

    // Insert before the add-agent-bar (if it exists), otherwise just append
    const addAgentBar = container.querySelector('.add-agent-bar');
    if (addAgentBar) {
        container.insertBefore(column, addAgentBar);
    } else {
        container.appendChild(column);
    }

    // Enable workflow slug drag-and-drop on textarea
    const textarea = document.getElementById(`input-${agentId}`);
    if (textarea) {
        setupWorkflowSlugDropTarget(textarea, agentId);
        setupAgentInputPadding(agentId);
    }
}

// Setup padding adjustment for agent input area (same as AI Prime)
function setupAgentInputPadding(agentId) {
    const textarea = document.getElementById(`input-${agentId}`);
    const messagesContainer = document.querySelector(`#agent-${agentId} .agent-messages-container`);
    const inputArea = document.querySelector(`#agent-${agentId} .agent-input-area`);

    if (!textarea || !messagesContainer || !inputArea) return;

    // Add padding when user focuses input
    textarea.addEventListener('focus', () => {
        const inputHeight = inputArea.offsetHeight;
        messagesContainer.style.paddingBottom = `${inputHeight + LAYOUT_CONSTANTS.PADDING_BUFFER}px`;
        console.log(`[AGENT ${getAgentName(agentId)}] Focus - Input height: ${inputHeight}px, Padding: ${inputHeight + LAYOUT_CONSTANTS.PADDING_BUFFER}px`);
    });

    // Remove padding when user leaves input (if empty)
    textarea.addEventListener('blur', () => {
        setTimeout(() => {
            if (document.activeElement !== textarea && textarea.value.trim() === '') {
                messagesContainer.style.paddingBottom = 'var(--space-4)';
                console.log(`[AGENT ${getAgentName(agentId)}] Blur - Padding reset`);
            }
        }, LAYOUT_CONSTANTS.BLUR_DELAY);
    });

    // Update padding as textarea expands
    textarea.addEventListener('input', () => {
        if (document.activeElement === textarea) {
            setTimeout(() => {
                const inputHeight = inputArea.offsetHeight;
                messagesContainer.style.paddingBottom = `${inputHeight + LAYOUT_CONSTANTS.PADDING_BUFFER}px`;
            }, 0);
        }
    });
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
        const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
        if (!validTypes.includes(file.type)) {
            showNotification(`Invalid file type: ${file.name}. Only PDF and images are supported.`, 'error');
            continue;
        }

        // Check file size (32MB max for PDFs, 5MB for images)
        const maxSize = file.type === 'application/pdf' ? 32 * 1024 * 1024 : 5 * 1024 * 1024;
        if (file.size > maxSize) {
            showNotification(`File too large: ${file.name}. Max size: ${maxSize / 1024 / 1024} MB`, 'error');
            continue;
        }

        window.agentAttachedFiles[agentId].push(file);
    }

    updateAgentAttachedFilesUI(agentId);

    // Reset file input
    const fileInput = document.getElementById(`file-input-${agentId}`);
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
    const textarea = document.getElementById(`input-${agentId}`);
    const messagesContainer = document.querySelector(`#agent-${agentId} .agent-messages-container`);
    const inputArea = document.querySelector(`#agent-${agentId} .agent-input-area`);
    if (textarea === document.activeElement && messagesContainer && inputArea) {
        setTimeout(() => {
            const inputHeight = inputArea.offsetHeight;
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
        const textarea = document.getElementById(`input-${agentId}`);
        const messagesContainer = document.querySelector(`#agent-${agentId} .agent-messages-container`);
        const inputArea = document.querySelector(`#agent-${agentId} .agent-input-area`);
        if (textarea === document.activeElement && messagesContainer && inputArea) {
            setTimeout(() => {
                const inputHeight = inputArea.offsetHeight;
                messagesContainer.style.paddingBottom = `${inputHeight + LAYOUT_CONSTANTS.PADDING_BUFFER}px`;
            }, 0);
        }
    }
}

function createAddAgentBar() {
    const existingBar = document.querySelector('.add-agent-bar');
    if (existingBar) return;

    const bar = document.createElement('div');
    bar.className = 'add-agent-bar';
    bar.onclick = addAgentColumn;
    bar.innerHTML = `
            <div class="add-agent-bar-content">
                <i class="fas fa-plus"></i>
                    ADD AGENT
                </div>
            `;

    // Only show if multi-agent tab is currently active
    if (AppState.currentTab === 'multi-agent') {
        bar.classList.add('visible');
    }

    // Append to multi-agent-container (as last flex item)
    const container = document.getElementById('multi-agent-container');
    if (container) {
        container.appendChild(bar);
        console.log('[Multi-Agent] Add Agent bar appended to container');
    }
}

function addAgentColumn() {
    const agentId = MultiAgent.nextAgentId++;
    if (agentId > 26) {
        showNotification('Maximum 26 agents reached (NATO alphabet limit)', 'warning');
        return;
    }

    createAgentColumn(agentId);

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
function loadThreadIntoAgent(agentId, sessionId) {
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
        messagesContainer.innerHTML = '';

        // Get messages from MessageStore (centralized storage)
        const messages = window.MessageStore.getMessages(thread.id);
        console.log(`📦 [MessageStore] Loading ${messages.length} messages into Agent ${agentId} from thread ${thread.id}`);

        // Add each message
        messages.forEach(msg => {
            const messageDiv = document.createElement('div');
            messageDiv.className = `agent-message ${msg.role === 'user' ? 'user' : 'assistant'}`;
            messageDiv.innerHTML = `
            <div class="agent-message-bubble">
                ${msg.content}
                        </div>
            `;
            messagesContainer.appendChild(messageDiv);
        });

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
    UIComponents.showConfirmation({
        title: `Close ${getAgentName(agentId)}?`,
        message: `This will close the agent column and clear its conversation.`,
        variant: 'warning',
        confirmLabel: 'Close',
        cancelLabel: 'Cancel',
        onConfirm: () => {
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

                showNotification(`Agent ${getAgentName(agentId)} closed`, 'info');
            }
        }
    });
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

async function sendAgentMessage(agentId) {
    const input = document.getElementById(`input-${agentId}`);
    const sendBtn = document.getElementById(`send-${agentId}`);
    const message = input.value.trim();

    if (!message) return;

    const attachedFiles = window.agentAttachedFiles && window.agentAttachedFiles[agentId] ? window.agentAttachedFiles[agentId] : [];
    const hasFiles = attachedFiles.length > 0;

    const messageToSend = message;
    input.value = '';
    input.style.height = 'auto';
    clearAgentAttachedFiles(agentId);

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
            syncToBackend: false
        }
    );
    console.log(`[Agent ${agentId}] User message rendered`);
    scrollAgentToBottom(agentId);

    updateAgentStatus(agentId, 'thinking', 'Thinking...');
    if (typeof AgentStatusIndicator !== 'undefined') {
        AgentStatusIndicator.update('thinking', agentId);
    }
    sendBtn.disabled = true;

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
                },
                body: formData
            });
        } else {
            const workflowContext = window.agentWorkflowContext && window.agentWorkflowContext[agentId];

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
                preferences: {
                    use_tools: true,
                    verbose_tool_output: true,
                    streaming: true
                }
            };

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
                },
                body: JSON.stringify(requestBody)
            });
        }

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const startData = await response.json();
        console.log(`[Agent ${agentId}] Agent started:`, startData);

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

        const streamUrl = `${window.API_BASE_URL || 'http://localhost:5001'}/api/agent/stream/${agentId}?thread_slug=${threadSlug}`;
        console.log(`[Agent ${agentId}] Stream URL:`, streamUrl);

        const streamResponse = await fetch(streamUrl);

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

        console.log(`[Agent ${agentId}] 🔵 STREAMING FUNCTION LOADED (v20251122d)`);

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

        while (true) {
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

                        console.log(`[Agent ${agentId}] 📨 Event:`, data.type, data);

                        // CONVERSATION_SYNC EVENT - Receive backend's authoritative conversation (Nov 22, 2025 FIX)
                        // Backend sends complete conversation_history BEFORE 'complete' event
                        // This prevents duplicate saves and ensures complete block structure
                        if (data.type === 'conversation_sync') {
                            console.log(`[Agent ${agentId}] 📥 [SYNC] Received conversation_sync: ${data.message_count} messages`);

                            if (data.conversation_history && Array.isArray(data.conversation_history)) {
                                // Get current thread from AppState
                                const thread = AppState.agentThreads && AppState.agentThreads[agentId];

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
                                    console.warn(`[Agent ${agentId}] ⚠️ [SYNC] Thread not found in AppState.agentThreads`);
                                }
                            } else {
                                console.warn(`[Agent ${agentId}] ⚠️ [SYNC] Invalid conversation_history in conversation_sync event`);
                            }
                        }

                        // THINKING EVENT - Create THINKING BUBBLE (purple BRAIN icon)
                        else if ((data.type === 'thinking_block' || data.type === 'thinking') && (data.content || data.thinking)) {
                            const thinkingText = data.content || data.thinking || '';
                            if (thinkingText && thinkingText.trim().length > 0) {
                                console.log(`[Agent ${agentId}] 💭 THINKING: ${thinkingText.substring(0, 50)}...`);

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

                                    actionsDiv.appendChild(copyBtn);
                                    actionsDiv.appendChild(copyRawBtn);
                                    headerDiv.appendChild(actionsDiv);

                                    // Content div
                                    const contentDiv = document.createElement('div');
                                    contentDiv.className = 'ai-message-content';
                                    thinkingBubble.appendChild(headerDiv);
                                    thinkingBubble.appendChild(contentDiv);
                                    thinkingBubble.classList.add('collapsed'); // Start collapsed
                                    messagesContainer.appendChild(thinkingBubble);

                                    thinkingBubble._fullThinkingText = '';
                                }

                                // Accumulate thinking text
                                thinkingBubble._fullThinkingText = thinkingBubble._fullThinkingText || '';
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

                            actionsDiv.appendChild(copyBtn);
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

                            actionsDiv.appendChild(copyBtn);
                            actionsDiv.appendChild(copyRawBtn);
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

                            contentDiv.innerHTML = `
                                <div style="margin-bottom: 8px; color: ${isError ? '#ef4444' : '#60A5FA'};">
                                    <strong><i class="fas ${isError ? 'fa-times-circle' : 'fa-check-circle'}"></i> Tool Result: ${data.tool_name || 'Unknown'}</strong>
                                </div>
                                <pre style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 6px; max-height: 400px; overflow-y: auto;">${formattedResult}</pre>
                            `;

                            toolResultBubble.appendChild(headerDiv);
                            toolResultBubble.appendChild(contentDiv);
                            toolResultBubble.classList.add('collapsed'); // Start collapsed
                            messagesContainer.appendChild(toolResultBubble);

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

                                actionsDiv.appendChild(copyBtn);
                                actionsDiv.appendChild(copyRawBtn);
                                headerDiv.appendChild(actionsDiv);

                                textBubble.appendChild(headerDiv);

                                // Content div
                                const contentDiv = document.createElement('div');
                                contentDiv.className = 'ai-message-content';
                                textBubble.appendChild(contentDiv);

                                messagesContainer.appendChild(textBubble);
                                console.log(`[Agent ${agentId}] Text bubble created`);

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
                                textBubble.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                            }
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

        console.log(`[Agent ${agentId}] Stream complete. Response length: ${fullResponse.length}`);

        // Clear status indicator
        if (typeof AgentStatusIndicator !== 'undefined') {
            AgentStatusIndicator.clear(agentId);
        }

        // Finalize TwoRuleStreamProcessor (render any pending visualizations)
        if (textBubble && textBubble._twoRuleProcessor) {
            console.log(`[Agent ${agentId}] Finalizing TwoRuleStreamProcessor...`);
            try {
                if (typeof textBubble._twoRuleProcessor.finalize === 'function') {
                    await textBubble._twoRuleProcessor.finalize();
                    console.log(`[Agent ${agentId}] ✅ Processor finalized`);

                    // Force render if still no content visible
                    const textContent = textBubble.querySelector('.ai-message-content');
                    if (textContent && (!textContent.innerHTML || textContent.innerHTML.trim() === '')) {
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

        addAgentMessage(agentId, 'ai', ` Error: ${error.message}`);
        updateAgentStatus(agentId, 'error', 'Error');
        if (typeof AgentStatusIndicator !== 'undefined') {
            AgentStatusIndicator.clear(agentId);
        }
    } finally {
        updateAgentStatus(agentId, 'ready', 'Ready');
        if (typeof AgentStatusIndicator !== 'undefined') {
            AgentStatusIndicator.clear(agentId);
        }
        sendBtn.disabled = false;

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
            syncToBackend: false
        }
    );

    if (!messageDiv) {
        console.error(`[Agent ${agentId}] Failed to render message`);
        return;
    }

    console.log(`[Agent ${agentId}] Message rendered using unified renderer`);
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

// ==================== EXPOSE TO GLOBAL SCOPE ====================
// Required for main app initialization
window.initMultiAgent = initMultiAgent;
window.MultiAgent = MultiAgent;
console.log('✅ [AGENT-JS] Module loaded successfully - initMultiAgent and MultiAgent exported to window scope');
console.log(`✅ [AGENT-JS] File size: ${document.currentScript?.src || 'unknown'} - ready for initialization`);