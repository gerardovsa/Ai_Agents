
// ==================== THREAD MANAGER ====================
const ThreadManager = {
    currentThreadId: null,
    threads: [],
    threadsLoaded: false,  // ? LAZY LOADING: Track if threads have been loaded
    autoSaveInterval: null,
    currentFilter: 'active',  // NEW: Filter state (active/archived)
    searchQuery: '',  // Multi-capable search query
    locationFilter: 'all',  // Location filter (all/prime/all-agents/agent-1/etc)
    activeTagFilter: null,  // Tag filter (synergy/automation)
    dateRangeFilter: { range: 'all', startDate: null },  // Date range filter
    realtimeChannel: null,
    realtimeEnabled: false,
    lastRealtimeUpdate: null,
    pendingAssignment: false,
    threads: [],
    threadsLoaded: false,  // ? LAZY LOADING: Track if threads have been loaded
    autoSaveInterval: null,
    currentFilter: 'active',  // NEW: Filter state (active/archived)
    realtimeChannel: null,
    realtimeEnabled: false,
    lastRealtimeUpdate: null,
    pendingAssignment: false,

    // Welcome System - Time-based greetings and rotating tips
    quickTips: [
        "Drag & drop threads from the sidebar to move conversations between agents. All formatting, context, and history stays intact!",
        "Use Ctrl+Enter to send messages quickly, or Shift+Enter to add new lines without sending.",
        "Click the thread ID badge to copy it - perfect for sharing specific conversations or linking in Synergy cards.",
        "Double-click any thread title to edit it inline. Give your conversations memorable names!",
        "Archive old threads to keep your workspace clean. Archived threads are still searchable and can be restored anytime.",
        "Use the session loader (ID input) to instantly jump to any thread by pasting its ID - works even if it's not in your visible list.",
        "Tag your threads for easy filtering! Add tags like 'urgent', 'research', or 'client-work' to organize conversations.",
        "Link threads to Synergy cards to track multi-step projects. One card can coordinate multiple AI conversations!",
        "Right-click thread cards for quick actions: archive, delete, copy ID, or export conversation history.",
        "Press '/' to focus the message input and start typing immediately. Small shortcuts = big productivity gains!"
    ],
    currentTipIndex: -1,

    // Welcome message variations per time period
    welcomeVariations: {
        morning: [
            { title: "Good Morning!", subtitle: "Ready to tackle today's tasks? Start a new chat or continue where you left off.", icon: "fa-sun", color: "#fbbf24" },
            { title: "Rise & Shine!", subtitle: "A fresh day, fresh possibilities. What shall we build together today?", icon: "fa-sunrise", color: "#f59e0b" },
            { title: "Morning, Champion!", subtitle: "The early bird catches the worm! Let's make today productive.", icon: "fa-coffee", color: "#fb923c" },
            { title: "New Day, New Ideas!", subtitle: "Your morning boost is here. Ready to turn ideas into reality?", icon: "fa-lightbulb", color: "#fbbf24" },
            { title: "Start Strong!", subtitle: "Morning energy is the best energy. What's first on your agenda?", icon: "fa-bolt", color: "#facc15" }
        ],
        afternoon: [
            { title: "Good Afternoon!", subtitle: "Making great progress! Need help with anything? I'm here to assist.", icon: "fa-cloud-sun", color: "#60a5fa" },
            { title: "Midday Check-In!", subtitle: "Halfway through the day. Let's power through together!", icon: "fa-chart-line", color: "#3b82f6" },
            { title: "Afternoon Momentum!", subtitle: "Keep the energy flowing. What's next on your list?", icon: "fa-fire", color: "#6366f1" },
            { title: "Productive Afternoon!", subtitle: "The day's rhythm is strong. Let's maintain that momentum!", icon: "fa-rocket", color: "#60a5fa" },
            { title: "Power Hour!", subtitle: "Peak productivity time. Let's make the most of it together.", icon: "fa-gem", color: "#8b5cf6" }
        ],
        evening: [
            { title: "Good Evening!", subtitle: "Finishing up for the day? Let's wrap up those final tasks together.", icon: "fa-moon", color: "#79c0ff" },
            { title: "Evening Wrap-Up!", subtitle: "Time to tie up loose ends. What needs your attention before wrapping up?", icon: "fa-check-circle", color: "#8b5cf6" },
            { title: "Sunset Session!", subtitle: "The golden hour of productivity. Let's end the day strong!", icon: "fa-cloud-moon", color: "#a855f7" },
            { title: "Evening Wind-Down!", subtitle: "Finishing touches time. Need help closing out your day?", icon: "fa-star", color: "#c084fc" },
            { title: "Last Sprint!", subtitle: "Final push before rest. Let's make these last hours count!", icon: "fa-flag-checkered", color: "#79c0ff" }
        ],
        night: [
            { title: "Working Late?", subtitle: "Burning the midnight oil? I'm here 24/7 to help you achieve your goals.", icon: "fa-moon", color: "#818cf8" },
            { title: "Night Owl Mode!", subtitle: "The world sleeps, but great ideas never do. Let's create magic!", icon: "fa-star", color: "#6366f1" },
            { title: "Late Night Hustle!", subtitle: "Dedication level: Expert. I'm with you all the way!", icon: "fa-rocket", color: "#7c3aed" },
            { title: "Midnight Momentum!", subtitle: "The quiet hours are perfect for deep work. What's the mission?", icon: "fa-moon", color: "#8b5cf6" },
            { title: "After Hours!", subtitle: "No rest for the ambitious! Let's knock this out together.", icon: "fa-certificate", color: "#a855f7" }
        ]
    },

    // Get time-based greeting with random variation
    getTimeBasedGreeting(agentName = null) {
        const hour = new Date().getHours();
        let variations;

        if (hour >= 5 && hour < 12) {
            variations = this.welcomeVariations.morning;
        } else if (hour >= 12 && hour < 17) {
            variations = this.welcomeVariations.afternoon;
        } else if (hour >= 17 && hour < 21) {
            variations = this.welcomeVariations.evening;
        } else {
            variations = this.welcomeVariations.night;
        }

        // Pick random variation
        const greeting = variations[Math.floor(Math.random() * variations.length)];

        // Personalize for specific agents
        if (agentName && agentName !== 'Prime') {
            greeting.title = `${agentName} Ready!`;
            greeting.subtitle = greeting.subtitle.replace(/I'm|I am/gi, `${agentName} is`);
        }

        return greeting;
    },

    // Get random quick tip (no repeats until all tips shown)
    getNextQuickTip() {
        if (this.currentTipIndex === -1 || this.currentTipIndex >= this.quickTips.length - 1) {
            // Shuffle tips array for fresh rotation
            this.quickTips = this.quickTips.sort(() => Math.random() - 0.5);
            this.currentTipIndex = 0;
        } else {
            this.currentTipIndex++;
        }
        return this.quickTips[this.currentTipIndex];
    },

    // Initialize welcome message (call on load and when thread cleared)
    initWelcomeMessage(location = 'prime') {
        const container = document.getElementById(`${location}-welcome-container`);
        if (!container) return;

        const greeting = this.getTimeBasedGreeting();
        const tip = this.getNextQuickTip();

        // Update greeting
        const titleEl = document.getElementById(`${location}-welcome-title`);
        const subtitleEl = document.getElementById(`${location}-welcome-subtitle`);
        const iconEl = container.querySelector('.welcome-icon i');

        if (titleEl) titleEl.textContent = greeting.title;
        if (subtitleEl) subtitleEl.textContent = greeting.subtitle;
        if (iconEl) {
            iconEl.className = `fas ${greeting.icon}`;
            iconEl.style.color = greeting.color;
        }

        // Update quick tip
        const tipTextEl = container.querySelector('.quick-tip-text');
        if (tipTextEl) tipTextEl.textContent = tip;

        console.log(`Welcome message initialized for ${location}:`, greeting.title);
    },

    // Generate AI-powered personalized welcome message
    async generateAIWelcome(location = 'prime', agentName = 'Prime') {
        console.log(` Generating AI welcome for ${agentName}...`);

        try {
            // Get user context from preferences API
            const prefsResponse = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/user/preferences`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });

            let userContext = {
                nickname: '',
                location: 'Brisbane, Australia',
                timezone: 'Australia/Brisbane',
                preferences: []
            };

            if (prefsResponse.ok) {
                const prefsData = await prefsResponse.json();
                const data = prefsData.data || prefsData;
                userContext = {
                    nickname: data.nickname || '',
                    location: data.use_manual_location ? data.manual_location_override : data.detected_city,
                    timezone: data.use_manual_timezone ? data.manual_timezone_override : data.detected_timezone,
                    preferences: data.custom_preferences || []
                };
            }

            // Create mini welcome-generation prompt
            const welcomePrompt = `Generate a brief, warm welcome message for ${agentName} AI assistant.

USER CONTEXT:
- Name: ${userContext.nickname || 'User'}
- Location: ${userContext.location}
- Time: ${new Date().toLocaleTimeString()} (${userContext.timezone})
- Day: ${new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
- Season: ${this.getCurrentSeason()}
- Weather: ${await this.getLocalWeather(userContext.location)}

REQUIREMENTS:
1. Single sentence greeting (max 15 words)
2. Reference time of day, weather, or season naturally
3. Be encouraging and friendly
4. Specific to ${agentName === 'Prime' ? 'general assistance' : agentName + ' specialty'}
5. NO generic corporate speak - be genuine and human

Return ONLY the greeting text, no quotes or extra formatting.`;

            // Send mini request to AI
            const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/agent/welcome`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: welcomePrompt,
                    agent_name: agentName,
                    user_context: userContext
                })
            });

            if (response.ok) {
                const data = await response.json();
                return data.welcome_message || this.getTimeBasedGreeting(agentName).subtitle;
            }
        } catch (error) {
            console.warn('Failed to generate AI welcome, using default:', error);
        }

        // Fallback to static greeting
        return this.getTimeBasedGreeting(agentName).subtitle;
    },

    // Get current season based on location
    getCurrentSeason() {
        const month = new Date().getMonth() + 1; // 1-12
        // Southern Hemisphere (assume AU)
        if (month >= 12 || month <= 2) return 'Summer';
        if (month >= 3 && month <= 5) return 'Autumn';
        if (month >= 6 && month <= 8) return 'Winter';
        return 'Spring';
    },

    // Get local weather (simplified)
    async getLocalWeather(location) {
        try {
            // This would call a weather API in production
            // For now, return placeholder
            return 'pleasant conditions';
        } catch {
            return 'pleasant conditions';
        }
    },

    // REMOVED: localStorage fallback - now using backend API only

    // REMOVED: localStorage save - now using backend API only

    // Assign thread to location (prime, agent-1, agent-2, etc.)
    /**
     * CASCADE PATTERN: Database-First Thread Assignment
     * 
     * CRITICAL RULE: Database ALWAYS updated FIRST, then UI cascades from DB state
     * This prevents UI/DB mismatches where thread appears in two places
     * 
     * Flow: assignThread() ? UPDATE DATABASE ? _cascadeThreadAssignment() ? UPDATE UI
     */
    async assignThread(threadId, location) {
        console.log(`?? [assignThread] START: ${threadId} ? ${location}`);

        try {
            // Set pending flag to prevent realtime loop
            this.pendingAssignment = true;

            // PHASE 1: UPDATE DATABASE FIRST (single source of truth)
            const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/thread-assignments/assign`, {
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
            console.log(`? [assignThread] Database updated:`, data.assignment);

            // PHASE 2: CASCADE UI UPDATES (only after DB success)
            // Realtime subscription will handle updates for other windows
            await this._cascadeThreadAssignment(threadId, location, data.assignment);

            // Clear pending flag after 500ms
            setTimeout(() => {
                this.pendingAssignment = false;
            }, 500);

            return data;

        } catch (error) {
            this.pendingAssignment = false;  // Clear on error
            console.error(`? [assignThread] Failed:`, error);
            if (typeof showNotification === 'function') {
                showNotification(`Failed to assign thread: ${error.message}`, 'error', 3000);
            }
            throw error;
        }
    },

    /**
     * CASCADE UI UPDATES: Update UI after database assignment succeeds
     * 
     * This function ONLY runs after database update succeeds
     * Handles: clearing old location, updating thread object, rendering new location
     */
    async _cascadeThreadAssignment(threadId, newLocation, assignment) {
        console.log(`?? [CASCADE] Starting UI updates for thread ${threadId}`);

        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) {
            console.warn(`[CASCADE] Thread not found: ${threadId}`);
            return;
        }

        // STEP 1: Update thread object FIRST (before clearing UI)
        // This ensures checkAndShowEmptyState sees the correct location
        thread.location = newLocation;
        thread.agent = newLocation === 'prime' ? null : newLocation;
        thread.updated = new Date().toISOString();
        console.log(`? [CASCADE] Updated thread object: location=${newLocation}`);

        // STEP 2: Clear OLD location UI (now that thread.location is updated)
        if (assignment.previous_location) {
            console.log(`?? [CASCADE] Clearing ${assignment.previous_location}`);
            await this._clearLocationUI(assignment.previous_location, threadId);
        }

        // STEP 3: Handle DISPLACED thread (if any)
        if (assignment.displaced_thread) {
            console.log(`?? [CASCADE] Handling displaced thread: ${assignment.displaced_thread}`);
            const displacedThread = this.threads.find(t => t.id === assignment.displaced_thread);
            if (displacedThread) {
                // Displaced thread goes to Prime (backend already updated location)
                displacedThread.location = 'prime';
                displacedThread.agent = null;
                displacedThread.updated = new Date().toISOString();

                // Clear displaced thread from agent UI
                await this._clearLocationUI(newLocation, assignment.displaced_thread);
            }
        }

        // STEP 4: Update thread-info container in NEW location
        if (newLocation && newLocation.startsWith('agent-')) {
            const agentId = newLocation.replace('agent-', '');
            const threadInfoEl = document.getElementById(`thread-info-${agentId}`);
            if (threadInfoEl) {
                threadInfoEl.innerHTML = this.renderThreadInfoContainer(newLocation, threadId, true);
                console.log(`? [CASCADE] Updated thread-info for ${newLocation}`);
            }
        } else if (newLocation === 'prime') {
            const primeThreadInfo = document.getElementById('thread-info-prime');
            if (primeThreadInfo && AppState.sessionId === threadId) {
                primeThreadInfo.innerHTML = this.renderThreadInfoContainer('prime', threadId, false);
                console.log(`? [CASCADE] Updated thread-info for Prime`);
            }
        }

        // STEP 5: Refresh UI components
        this.renderThreadList();  // Update sidebar
        this.refreshAllThreadInfoCards(threadId);  // Update all thread-info cards

        console.log(`? [CASCADE] Complete for thread ${threadId}`);
    },

    /**
     * CLEAR OLD LOCATION UI: Remove thread from old location
     * 
     * Only clears UI if this specific thread is loaded in that location
     * Prevents clearing wrong thread when displacement happens
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
                if (primeThreadInfo) {
                    primeThreadInfo.innerHTML = this.renderThreadInfoContainer('prime', null, false);
                }

                console.log(`? [CASCADE] Cleared Prime UI (thread ${threadId})`);
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
                    if (headerEl) {
                        headerEl.innerHTML = this.renderThreadInfoContainer(location, null, true);
                    }

                    console.log(`? [CASCADE] Cleared ${location} UI (thread ${threadId})`);
                }
            }
        }
    },

    /**
     * ? MASTER SYNC FUNCTION ?
     * Synchronize thread location + UI links (Synergy, Workflows, etc.) across ALL UI components
     * Call this after ANY operation that changes thread location or linkages
     * 
     * @param {string} threadId - Thread ID
     * @param {string} newLocation - New location ('main', 'agent-1', 'agent-2', 'agent-3')
     * @param {Object} options - Optional linkage updates
     *   - synergySessionId: Link/unlink Synergy session
     *   - workflowId: Link/unlink Workflow automation
     *   - removeLinks: Array of link types to remove ['synergy', 'workflow']
     */
    async syncThreadLocationEverywhere(threadId, newLocation, options = {}) {
        console.log(`?? [syncThreadLocationEverywhere] Syncing ${threadId} ? ${newLocation}`, options);

        // STEP 1: Normalize location name (frontend uses 'main', backend uses 'prime')
        const backendLocation = newLocation === 'main' ? 'prime' : newLocation;
        const frontendLocation = newLocation;  // Keep as-is for UI

        // STEP 2: Update local thread object
        const thread = this.threads.find(t => t.id === threadId);
        if (thread) {
            thread.agent = frontendLocation;
            thread.updated = new Date().toISOString();

            // Add linkages if provided (for linking operations)
            if (options.addLinks) {
                if (options.addLinks.includes('synergy') && options.synergySessionId) {
                    thread.synergy_card_id = options.synergySessionId;
                    thread.synergy_card_name = options.synergySessionName || null;
                }
                if (options.addLinks.includes('workflow') && options.workflowId) {
                    thread.workflow_id = options.workflowId;
                    thread.workflow_name = options.workflowName || null;
                }
            }

            // Update linkages if provided (for unlinking operations)
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
    },

    /**
     * Restore thread assignments from backend
     * Called during app initialization to sync UI with database state
     */
    async restoreThreadAssignments() {
        console.log('[ThreadManager] Restoring thread assignments from backend...');

        try {
            const userId = (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1;
            const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/thread-assignments/list?user_id=${userId}`, {
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
            } else if (data && typeof data === 'object') {
                console.warn('[ThreadManager] Unexpected response format:', data);
                assignments = [];
            }

            console.log(`[ThreadManager] Restored ${assignments.length} thread assignments`);

            // Update local thread objects with assignment data
            for (const assignment of assignments) {
                const thread = this.threads.find(t => t.id === assignment.session_id);
                if (thread) {
                    thread.location = assignment.location;
                    thread.agent = assignment.location === 'prime' ? null : assignment.location;
                }
            }

            return assignments;
        } catch (error) {
            console.error('[ThreadManager] Failed to restore assignments:', error);
            return [];
        }
    },

    // Toggle thread menu sidebar
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

    // Close thread menu sidebar
    closeThreadMenu() {
        console.log(`[SEARCH] [closeThreadMenu] Called`);
        const menu = document.getElementById('thread-menu');
        if (menu) {
            menu.classList.remove('active');
            console.log(`[SEARCH] [closeThreadMenu] Menu closed`);
        } else {
            console.error(`[ERROR] [closeThreadMenu] Thread menu element not found!`);
        }
    },

    // Refresh thread list
    async refreshThreads() {
        console.log(`[SEARCH] [refreshThreads] Refreshing thread list...`);
        try {
            await this.loadThreadsFromBackend();
            await this.renderThreadList();
            console.log(`[SEARCH] [refreshThreads] Thread list refreshed: ${this.threads.length} threads`);
        } catch (error) {
            console.error(`[ERROR] [refreshThreads] Failed to refresh threads:`, error);
        }
    },

    // Load threads from backend database
    async loadThreadsFromBackend() {
        try {
            const userId = (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) ?
                (UserAuth.user.id || UserAuth.user.user_id) : null;

            if (!userId) {
                console.error('[THREADS] Cannot load threads: user_id not available');
                return false;
            }

            console.log(`[THREADS] Loading threads for user_id: ${userId}`);

            const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/list?user_id=${userId}`);
            const data = await response.json();

            const threads = data.threads || (data.data && data.data.threads) || [];

            if (data.success && threads && threads.length > 0) {
                this.threads = threads.map(thread => {
                    const location = thread.location || thread.agent || 'prime';
                    const threadTitle = thread.name || thread.title || 'Untitled Thread';
                    return {
                        id: thread.id || thread.thread_slug,
                        thread_id: thread.thread_id,
                        title: threadTitle,
                        name: threadTitle,
                        messages: thread.messages || [],
                        message_count: thread.message_count || 0,
                        created: thread.created || thread.created_at || new Date().toISOString(),
                        updated: thread.updated || thread.updated_at || new Date().toISOString(),
                        archived: thread.archived || false,
                        location: location,
                        agent: location === 'prime' ? null : location,
                        tags: thread.tags || [],
                        synergy_card_id: thread.synergy_card_id || null,
                        workflow_slug: thread.workflow_slug || null,
                        workflow_title: thread.workflow_title || null,
                        internal_doc_slug: thread.internal_doc_slug || null,
                        internal_doc_title: thread.internal_doc_title || null
                    };
                });
                console.log('[DATA] Threads loaded from backend:', this.threads.length);
                return true;
            } else {
                console.warn('[WARN] No threads from backend, starting fresh');
                this.threads = [];
                return false;
            }
        } catch (error) {
            console.error('Failed to load threads from backend:', error);
            this.threads = [];
            return false;
        }
    },

    // Show new chat modal
    async showNewChatModal(location = 'prime') {
        console.log(` [showNewChatModal] Opening modal for location: ${location}`);

        const locationName = location === 'prime' ? 'Prime Agent' :
            (location.startsWith('agent-') ? `Agent ${location.split('-')[1]}` : location);

        const modalHTML = `
<div class="modal-overlay" id="newChatModalOverlay" onclick="if(event.target.id === 'newChatModalOverlay') document.getElementById('newChatModalOverlay').remove()">
    <div class="new-chat-modal" onclick="event.stopPropagation()">
        <div class="modal-header">
            <h3><i class="fas fa-plus-circle"></i> Start New Chat in ${locationName}</h3>
            <button class="modal-close" onclick="document.getElementById('newChatModalOverlay').remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="modal-body">
            <form id="newChatForm">
                <div class="form-group">
                    <label for="threadTitle">Thread Title</label>
                    <input type="text" id="threadTitle" class="form-control" placeholder="Enter thread title..." required>
                </div>
                <div class="form-group">
                    <label for="initialMessage">Initial Message (Optional)</label>
                    <textarea id="initialMessage" class="form-control" rows="4" placeholder="Start the conversation..."></textarea>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="document.getElementById('newChatModalOverlay').remove()">
                        Cancel
                    </button>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-plus"></i> Create Thread
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>`;

        // Remove existing modal if present
        const existingModal = document.getElementById('newChatModalOverlay');
        if (existingModal) existingModal.remove();

        // Insert modal
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Handle form submission
        const form = document.getElementById('newChatForm');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const title = document.getElementById('threadTitle').value.trim();
            const initialMessage = document.getElementById('initialMessage').value.trim();

            if (!title) {
                alert('Please enter a thread title');
                return;
            }

            console.log(` [showNewChatModal] Creating thread:`, { title, location, initialMessage });

            // Create thread
            try {
                const newThreadId = Date.now();
                const newThread = {
                    id: newThreadId,
                    title: title,
                    created_at: new Date().toISOString(),
                    location: location,
                    agent: location === 'prime' ? null : location,
                    messages: initialMessage ? [{
                        role: 'user',
                        content: initialMessage,
                        timestamp: new Date().toISOString()
                    }] : []
                };

                // Add to threads array
                this.threads.unshift(newThread);

                // Save to backend
                await this.assignThread(newThreadId, location);

                // Close modal
                document.getElementById('newChatModalOverlay').remove();

                // Load thread in the specified location
                if (location === 'prime') {
                    await this.loadThread(newThreadId);
                } else {
                    // Load in agent column
                    const agentId = location.replace('agent-', '');
                    if (window.loadAgentThread) {
                        window.loadAgentThread(agentId, newThreadId);
                    }
                }

                console.log(` [showNewChatModal] Thread created successfully: ${newThreadId}`);
            } catch (error) {
                console.error('[ERROR] [showNewChatModal] Failed to create thread:', error);
                alert('Failed to create thread. Please try again.');
            }
        });
    },

    // ==================== MISSING METHODS - RESTORED FROM ORIGINAL ====================


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
    }
};

// ==================== EXPOSE THREADMANAGER GLOBALLY ====================
window.ThreadManager = ThreadManager;
console.log('✅ ThreadManager exposed to window.ThreadManager');

// ✅ FIX: ThreadManager.init() moved to initializeMainApp() (after authentication)
// This ensures UserAuth.token is set before calling /api/auth/profile
// Previously initialized on page load, causing 401 errors for real users

// ==================== SYNERGY DASHBOARD JAVASCRIPT ====================
// ✅ FULLY MODULARIZED - November 20, 2025
// All Synergy code moved to: UI/external/modules/synergy/
//
// Available modules:
// - synergy-board-init.js (412 lines) - Core dashboard initialization
// - synergy-card-renderer.js - Card rendering logic
// - synergy-functions.js (1,446 lines) - Utility functions
// - synergy-milestone-renderer.js - Milestone UI
// - synergy-milestone-interactions.js - Milestone interactions
// - synergy-sidebar-controller.js - Sidebar controller
// - synergy-sidebar-renderer.js - Sidebar rendering
// - thread_synergy.js (700 lines) - Thread-Synergy integration
//
// Global objects available:
// - window.synergyBoard
// - window.SynergySidebar
// - window.ThreadSynergyIntegration
//
// DELETED FROM thread_manager.js: 5,251 lines (Nov 20, 2025)
// Original size: 6,883 lines → New size: 1,632 lines

// ========================================
//  UNIVERSAL SSE STREAM HANDLER
// Unified streaming for BOTH Prime and Multi-Agent
// November 4, 2025
// ========================================

/**
 * Universal SSE Stream Handler
 * Handles thinking blocks, tool calls, text streaming, markdown rendering
 * Works for both Prime (agent_id='1') and Multi-Agent columns (agent_id=1-3)
 */
async function handleUniversalStream(agentId, sessionId, containerId) {
    console.log(` [Universal Stream] Starting for agent ${agentId}, container: ${containerId}`);

    // CRITICAL FIX: Use thread_slug for stream isolation
    // Use getAgentName() for consistent agent name format (e.g., "Alpha-8", not "Agent 8")
    const agentName = getAgentName(agentId);
    const currentThread = ThreadManager.getThreadByAgent(agentName);
    const threadSlug = currentThread ? currentThread.id : sessionId;
    const streamUrl = `${API_BASE_URL}/api/agent/stream/${agentId}?thread_slug=${threadSlug}`;
    console.log(`[Universal Stream] Agent: ${agentName}, Thread: ${threadSlug}, Container: ${containerId}`);
    const response = await fetch(streamUrl);

    if (!response.ok) {
        throw new Error(`Stream error! status: ${response.status}`);
    }

    // Get container element
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`? [Universal Stream] Container '${containerId}' not found!`);
        throw new Error(`Container ${containerId} not found`);
    }

    // Set up MutationObserver for automatic processor cleanup
    if (!window._twoRuleCleanupObserver) {
        window._twoRuleCleanupObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.removedNodes.forEach((node) => {
                    if (node._twoRuleProcessor && window._twoRuleProcessors) {
                        console.log('[CLEANUP] Removing processor for detached bubble');
                        window._twoRuleProcessors.delete(node._twoRuleProcessor);
                        node._twoRuleProcessor = null;
                    }
                    // Also check children for processors
                    if (node.querySelectorAll) {
                        node.querySelectorAll('[data-bubble-id]').forEach(bubble => {
                            if (bubble._twoRuleProcessor && window._twoRuleProcessors) {
                                console.log('[CLEANUP] Removing processor for detached child bubble');
                                window._twoRuleProcessors.delete(bubble._twoRuleProcessor);
                                bubble._twoRuleProcessor = null;
                            }
                        });
                    }
                });
            });
        });

        // Observe all message containers
        const primeContainer = document.getElementById('ai-chat-messages');
        if (primeContainer) {
            window._twoRuleCleanupObserver.observe(primeContainer, { childList: true, subtree: true });
        }

        // Observe agent containers
        document.querySelectorAll('[id^="agent-messages-"]').forEach(agentContainer => {
            window._twoRuleCleanupObserver.observe(agentContainer, { childList: true, subtree: true });
        });

        console.log('[OK] MutationObserver installed for TwoRule processor cleanup');
    }
    console.log(`? [Universal Stream] Container found: ${containerId}`);
    console.log(`   ? Container actual ID: ${container.id}`);
    console.log(`   ? Container className: ${container.className}`);
    console.log(`   ? Container parent ID: ${container.parentElement?.id || 'none'}`);
    console.log(`   ? Is Prime container?: ${container.id === 'ai-chat-messages'}`);

    // Remove typing indicator only when first content arrives
    let typingIndicatorRemoved = false;
    const removeTypingIndicator = () => {
        if (!typingIndicatorRemoved) {
            const typingIndicator = container.querySelector('.typing-indicator');
            if (typingIndicator) {
                typingIndicator.parentElement?.remove();
                typingIndicatorRemoved = true;
                console.log('[OK] Removed typing indicator - content arrived');
            }
        }
    };

    // Tracking variables
    let thinkingBubble = null;
    let textBubble = null;
    let toolBubbles = [];
    let currentToolGroup = null; // NEW: Track current tool group
    let fullResponse = '';
    let fullThinkingContent = '';
    let firstContentReceived = false;
    let lastEventType = null;

    // Reset round counter for new stream
    window._thinkingRoundCounter = 0;

    // Track previous thinking block index to detect when block changes (NEW round)
    let previousThinkingBlockIndex = -1;

    // SSE Reader setup
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    console.log(' [Universal Stream] Connected to SSE stream');

    while (true) {
        const { done, value } = await reader.read();
        if (done) {
            console.log('[OK] [Universal Stream] Stream complete');
            break;
        }

        // Decode and buffer
        buffer += decoder.decode(value, { stream: true });
        const messages = buffer.split('\n\n');
        buffer = messages.pop() || '';

        // Process complete SSE messages
        for (const message of messages) {
            const lines = message.split('\n');
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const jsonStr = line.substring(6).trim();
                        if (!jsonStr) continue;

                        const data = JSON.parse(jsonStr);

                        // Route to appropriate handler
                        if (data.type === 'thinking' || data.type === 'thinking_block') {
                            removeTypingIndicator(); // Remove dots when thinking starts
                            // Pass the thinking bubble through handler (may return new bubble for new rounds)
                            const result = handleThinkingEvent(data, container, thinkingBubble, firstContentReceived, previousThinkingBlockIndex);
                            // IMPORTANT: Update references
                            thinkingBubble = result.bubble;
                            previousThinkingBlockIndex = result.blockIndex;
                            if (thinkingBubble && !firstContentReceived) firstContentReceived = true;
                            fullThinkingContent += (data.content || data.thinking || '');
                            lastEventType = 'thinking';
                            // Close tool group when non-tool event occurs
                            currentToolGroup = null;

                        } else if (data.type === 'tool_use') {
                            removeTypingIndicator(); // Remove dots when tool starts
                            // Create tool bubble (standalone initially)
                            const toolBubble = handleToolUseEvent(data, container, firstContentReceived);
                            toolBubbles.push(toolBubble);

                            // If this is the first tool in a sequence, it becomes the group container
                            if (lastEventType !== 'tool_use') {
                                currentToolGroup = toolBubble;
                                console.log(' [Tool Group] Started new tool group');
                            }

                            if (!firstContentReceived) firstContentReceived = true;
                            lastEventType = 'tool_use';

                        } else if (data.type === 'tool_result') {
                            // Handle tool result and move to group if needed
                            handleToolResultEvent(data, toolBubbles, currentToolGroup);

                        } else if (data.type === 'text' || data.type === 'content_delta') {
                            // CRITICAL FIX (Nov 19, 2025): Only process text events with actual content
                            // Empty text events between tool_use blocks create empty bubbles that break API
                            const textContent = data.content || data.text || '';
                            if (!textContent.trim()) {
                                console.log('[SKIP] [Text] Empty text event - not creating bubble');
                                continue; // Skip empty text events
                            }

                            removeTypingIndicator(); // Remove dots when text starts
                            // Create new text bubble if switching from non-text event
                            if (lastEventType !== 'text' && lastEventType !== 'content_delta' && lastEventType !== null) {
                                textBubble = null;
                            }

                            textBubble = handleTextEvent(data, container, textBubble, firstContentReceived);
                            if (!firstContentReceived) firstContentReceived = true;
                            fullResponse += textContent;
                            lastEventType = 'text';
                            // Close tool group when non-tool event occurs
                            currentToolGroup = null;

                        } else if (data.type === 'thinking_stop' || data.type === 'content_block_stop') {
                            // Remove streaming class when thinking completes
                            if (thinkingBubble && thinkingBubble.classList.contains('streaming')) {
                                thinkingBubble.classList.remove('streaming');
                                console.log(' [Thinking] Stopped - removed streaming class (pulse stopped)');
                            }

                        } else if (data.type === 'complete') {
                            handleCompleteEvent(thinkingBubble, textBubble);
                            currentToolGroup = null;

                        } else if (data.type === 'error') {
                            handleErrorEvent(data, container, textBubble);
                            currentToolGroup = null;
                        }
                    } catch (e) {
                        console.error('[ERROR] [Universal Stream] Parse error:', e);
                    }
                }
            }
        }
    }

    // Scroll to bottom
    container.scrollTop = container.scrollHeight;

    // Return results
    return {
        fullResponse,
        fullThinkingContent,
        toolBubbles,
        thinkingBubble,
        textBubble
    };
}

/**
 * Handle thinking block events
 * ENHANCED: Detects new rounds (block_index === 0) and creates separate bubbles
 */
function handleThinkingEvent(data, container, existingBubble, firstContentReceived, previousBlockIndex) {
    const thinkingText = data.content || data.thinking || '';
    if (!thinkingText || thinkingText.trim().length === 0) {
        return { bubble: existingBubble, blockIndex: previousBlockIndex };
    }

    console.log(' [Thinking] Content:', thinkingText.substring(0, 50) + '...');

    // ROUND DETECTION: Check if block_index CHANGED (means new thinking block = new round)
    const blockIndex = typeof data.block_index === 'number' ? data.block_index : -1;
    const isNewRound = (blockIndex !== previousBlockIndex) && (previousBlockIndex !== -1) && existingBubble;

    // If new round detected (block index changed), finalize existing bubble and create new one
    if (isNewRound) {
        console.log(` [Thinking] New round detected (block_index changed: ${previousBlockIndex} -> ${blockIndex}) - creating new thinking bubble`);

        // Add round separator
        const separator = document.createElement('div');
        separator.className = 'thinking-round-separator';
        const roundNum = (window._thinkingRoundCounter || 0) + 1;
        window._thinkingRoundCounter = roundNum;
        separator.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 8px; margin: 12px 0; opacity: 0.4;">
                        <div style="flex: 1; height: 1px; background: linear-gradient(90deg, transparent, currentColor, transparent);"></div>
                        <div style="font-size: 11px; color: #888; font-weight: 500; letter-spacing: 0.5px;">Round ${roundNum}</div>
                        <div style="flex: 1; height: 1px; background: linear-gradient(90deg, currentColor, transparent);"></div>
                    </div>
                `;
        container.appendChild(separator);

        // Force creation of new bubble below
        existingBubble = null;
    }

    if (!existingBubble) {
        // Create new thinking bubble
        existingBubble = document.createElement('div');
        existingBubble.className = 'ai-message assistant thinking-bubble collapsed streaming';

        // Store block index for tracking
        existingBubble.dataset.blockIndex = blockIndex;

        // Header with brain icon
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
            existingBubble.classList.toggle('collapsed');
        });

        headerDiv.appendChild(avatar);
        headerDiv.appendChild(toggleBtn);

        // Actions
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'ai-message-actions';

        const copyBtn = document.createElement('button');
        copyBtn.className = 'ai-message-copy-btn';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        copyBtn.title = 'Copy thinking';
        copyBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const content = existingBubble.querySelector('.ai-message-content').textContent;
            navigator.clipboard.writeText(content).then(() => {
                copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => { copyBtn.innerHTML = '<i class="fas fa-copy"></i>'; }, 2000);
            });
        });

        actionsDiv.appendChild(copyBtn);
        headerDiv.appendChild(actionsDiv);

        // Content
        const contentDiv = document.createElement('div');
        contentDiv.className = 'ai-message-content';
        existingBubble._fullThinkingText = '';

        existingBubble.appendChild(headerDiv);
        existingBubble.appendChild(contentDiv);
        container.appendChild(existingBubble);

        console.log('[OK] [Thinking] Created bubble');
    }

    // Append content with markdown rendering
    existingBubble._fullThinkingText = (existingBubble._fullThinkingText || '') + thinkingText;
    const contentDiv = existingBubble.querySelector('.ai-message-content');

    if (window.marked) {
        try {
            contentDiv.innerHTML = marked.parse(existingBubble._fullThinkingText, { breaks: true, gfm: true });
        } catch (e) {
            contentDiv.textContent = existingBubble._fullThinkingText;
        }
    } else {
        contentDiv.textContent = existingBubble._fullThinkingText;
    }

    // Scroll
    container.scrollTop = container.scrollHeight;

    return { bubble: existingBubble, blockIndex: blockIndex };
}

/**
 * Handle tool use events
 * NEW: Supports grouping consecutive tool calls
 */
function handleToolUseEvent(data, container, firstContentReceived) {
    const toolId = data.tool_id || data.tool_use_id || data.id;
    const toolName = data.name || data.tool_name;
    const toolInput = data.input || data.tool_input;

    console.log(' [Tool Use]', toolName, 'ID:', toolId);

    const toolBubble = document.createElement('div');
    toolBubble.className = 'ai-message assistant tool-bubble collapsed tool-status-running';
    toolBubble.setAttribute('data-tool-id', toolId);

    // Header with cog icon (will glow orange and spin)
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

    // Actions
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

    // Content
    const contentDiv = document.createElement('div');
    contentDiv.className = 'ai-message-content';

    // Build detailed tool information display
    let toolInputDisplay = '{ }';
    if (toolInput && typeof toolInput === 'object' && Object.keys(toolInput).length > 0) {
        toolInputDisplay = JSON.stringify(toolInput, null, 2);
    } else if (typeof toolInput === 'string') {
        toolInputDisplay = toolInput;
    }

    contentDiv.innerHTML = `
                <div style="margin-bottom: 8px;"><strong>Tool:</strong> ${toolName}</div>
                <div style="margin-bottom: 8px;"><strong>Tool ID:</strong> <code style="background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 3px; font-size: 11px;">${toolId}</code></div>
                <details style="margin-bottom: 8px;">
                    <summary style="cursor: pointer; font-weight: 600; margin-bottom: 4px;">[LOAD] Input Parameters</summary>
                    <pre style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 6px; overflow-x: auto; margin-left: 12px;">${toolInputDisplay}</pre>
                </details>
                <div class="tool-status" style="margin-top: 8px; color: #eab308; font-weight: 600;"><i class="fas fa-spinner fa-spin"></i> Running...</div>
            `;

    toolBubble.appendChild(headerDiv);
    toolBubble.appendChild(contentDiv);

    // Always add to main container initially (will be moved to group on completion)
    container.appendChild(toolBubble);
    console.log('[OK] [Tool Use] Created standalone tool bubble (will group on completion)');

    // Scroll
    container.scrollTop = container.scrollHeight;

    return toolBubble;
}

/**
 * Handle tool result events - CREATE SEPARATE RESULT BUBBLE
 */
function handleToolResultEvent(data, toolBubbles, currentToolGroup) {
    const toolId = data.tool_id || data.tool_use_id || data.id;
    const toolBubble = toolBubbles.find(b => b.getAttribute('data-tool-id') === toolId);

    if (!toolBubble) {
        console.warn('[WARN] [Tool Result] Tool bubble not found for ID:', toolId);
        return;
    }

    console.log('[OK] [Tool Result] Creating SEPARATE result bubble for:', toolId);

    // Update tool-use bubble status to complete
    toolBubble.classList.remove('tool-status-running');
    toolBubble.classList.add('tool-status-complete');

    const statusDiv = toolBubble.querySelector('.tool-status');
    if (statusDiv) {
        statusDiv.innerHTML = '<i class="fas fa-check-circle"></i> Complete';
        statusDiv.style.color = '#22c55e';
    }

    // CREATE SEPARATE TOOL-RESULT BUBBLE
    const container = toolBubble.parentElement;
    const resultBubble = document.createElement('div');

    // Set class based on error status
    if (data.is_error) {
        resultBubble.className = 'ai-message assistant tool-result-bubble collapsed tool-status-error';
    } else {
        resultBubble.className = 'ai-message assistant tool-result-bubble collapsed tool-status-complete';
    }

    resultBubble.setAttribute('data-tool-result-id', toolId);

    // Header with flag icon (blue for success, red for error)
    const headerDiv = document.createElement('div');
    headerDiv.className = 'ai-message-header';

    const avatar = document.createElement('div');
    avatar.className = 'ai-message-avatar';
    avatar.innerHTML = '<i class="fas fa-flag"></i>';

    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'ai-message-toggle';
    toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
    toggleBtn.title = 'Collapse/Expand result';
    toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        resultBubble.classList.toggle('collapsed');
    });

    headerDiv.appendChild(avatar);
    headerDiv.appendChild(toggleBtn);

    // Actions
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'ai-message-actions';

    const copyBtn = document.createElement('button');
    copyBtn.className = 'ai-message-copy-btn';
    copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
    copyBtn.title = 'Copy result';
    copyBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const content = resultBubble.querySelector('.ai-message-content').textContent;
        navigator.clipboard.writeText(content).then(() => {
            copyBtn.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(() => { copyBtn.innerHTML = '<i class="fas fa-copy"></i>'; }, 2000);
        });
    });

    actionsDiv.appendChild(copyBtn);
    headerDiv.appendChild(actionsDiv);

    // Content
    const contentDiv = document.createElement('div');
    contentDiv.className = 'ai-message-content';

    // Format result content
    let resultText = data.content || data.result || 'No result content';

    // Try to parse and pretty-print JSON
    try {
        if (typeof resultText === 'string' && (resultText.startsWith('{') || resultText.startsWith('['))) {
            const parsed = JSON.parse(resultText);
            resultText = JSON.stringify(parsed, null, 2);
        } else if (typeof resultText === 'object') {
            resultText = JSON.stringify(resultText, null, 2);
        }
    } catch (e) {
        // Keep as-is if not JSON
    }

    contentDiv.innerHTML = `
                <div style="margin-bottom: 8px;">
                    <strong>${data.is_error ? 'Error' : 'Result'}:</strong> 
                    <span style="color: ${data.is_error ? '#ef4444' : '#22c55e'};">
                        <i class="fas ${data.is_error ? 'fa-times-circle' : 'fa-check-circle'}"></i>
                        ${data.is_error ? 'Error' : 'Complete'}
                    </span>
                </div>
                <details open>
                    <summary style="cursor: pointer; font-weight: 600; margin-bottom: 4px;">[OK] Result</summary>
                    <pre style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 6px; overflow-x: auto; margin-left: 12px; white-space: pre-wrap; font-size: 12px; max-height: 400px; overflow-y: auto;">${resultText}</pre>
                </details>
            `;

    resultBubble.appendChild(headerDiv);
    resultBubble.appendChild(contentDiv);

    // Insert AFTER the tool-use bubble
    if (toolBubble.nextSibling) {
        container.insertBefore(resultBubble, toolBubble.nextSibling);
    } else {
        container.appendChild(resultBubble);
    }

    console.log(`[OK] [Tool Result] Created SEPARATE ${data.is_error ? 'ERROR' : 'SUCCESS'} bubble`);

    // Scroll
    container.scrollTop = container.scrollHeight;
}

/**
 * Handle text streaming events
 */
function handleTextEvent(data, container, existingBubble, firstContentReceived) {
    const textContent = data.content || data.text || '';
    if (!textContent) return existingBubble;

    console.log(` [Text] Chunk: ${textContent.substring(0, 50)}... | Container: ${container.id}`);

    if (!existingBubble) {
        // Create new text bubble
        existingBubble = document.createElement('div');
        existingBubble.className = 'ai-message assistant text-bubble';

        // Header with robot icon
        const headerDiv = document.createElement('div');
        headerDiv.className = 'ai-message-header';

        const avatar = document.createElement('div');
        avatar.className = 'ai-message-avatar';
        avatar.innerHTML = '<i class="fa-solid fa-atom"></i>';

        headerDiv.appendChild(avatar);

        // Actions
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'ai-message-actions';

        const copyBtn = document.createElement('button');
        copyBtn.className = 'ai-message-copy-btn';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        copyBtn.title = 'Copy message';
        copyBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const content = existingBubble.querySelector('.ai-message-content').textContent;
            navigator.clipboard.writeText(content).then(() => {
                copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => { copyBtn.innerHTML = '<i class="fas fa-copy"></i>'; }, 2000);
            });
        });

        actionsDiv.appendChild(copyBtn);
        headerDiv.appendChild(actionsDiv);

        // Content
        const contentDiv = document.createElement('div');
        contentDiv.className = 'ai-message-content';
        existingBubble._fullText = '';

        existingBubble.appendChild(headerDiv);
        existingBubble.appendChild(contentDiv);

        // DEBUG: Log container details before append
        console.log(`[DEBUG] [Text] About to append bubble to container:`);
        console.log(`   ? Container ID: ${container.id}`);
        console.log(`   ? Container class: ${container.className}`);
        console.log(`   ? Container children count: ${container.children.length}`);
        console.log(`   ? Is Prime?: ${container.id === 'ai-chat-messages'}`);

        container.appendChild(existingBubble);

        console.log(`[OK] [Text] Bubble appended! Container now has ${container.children.length} children`);

        // VERIFY: Check where the bubble actually is in the DOM
        console.log(`[VERIFY] [Text] Bubble parent ID after append: ${existingBubble.parentElement?.id || 'UNKNOWN'}`);
        console.log(`[VERIFY] [Text] Bubble is in Prime?: ${existingBubble.parentElement?.id === 'ai-chat-messages'}`);
    }

    // Append text with markdown rendering
    existingBubble._fullText = (existingBubble._fullText || '') + textContent;
    const contentDiv = existingBubble.querySelector('.ai-message-content');

    // DEBUG: Verify we're updating the right bubble
    if (!existingBubble.hasAttribute('data-bubble-id')) {
        existingBubble.setAttribute('data-bubble-id', `bubble-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
    }
    console.log(`[DEBUG] [Text] Updating content in bubble:`);
    console.log(`   ? Bubble ID: ${existingBubble.getAttribute('data-bubble-id')}`);
    console.log(`   ? Bubble parent ID: ${existingBubble.parentElement?.id || 'UNKNOWN'}`);
    console.log(`   ? ContentDiv found?: ${contentDiv ? 'YES' : 'NO'}`);
    console.log(`   ? ContentDiv container: ${contentDiv?.closest('[id^="agent-messages-"]')?.id || contentDiv?.closest('#ai-chat-messages')?.id || 'UNKNOWN'}`);
    console.log(`   ? Is Prime bubble?: ${existingBubble.parentElement?.id === 'ai-chat-messages'}`);

    // Use TwoRule streaming renderer if available (prefer bubble-specific processor)
    const _proc = existingBubble._twoRuleProcessor || window.globalTwoRuleProcessor || null;

    // Deprecation warning for global processor usage
    if (!existingBubble._twoRuleProcessor && window.globalTwoRuleProcessor) {
        console.warn('[DEPRECATED] Using global TwoRule processor - should use per-bubble instance');
    }

    if (_proc && typeof _proc.processChunk === 'function') {
        // CRITICAL FIX: Ensure processor is targeting the correct container
        console.log(`[FIX] [Text] Setting TwoRule container to: ${contentDiv?.closest('[id^="agent-messages-"]')?.id || 'UNKNOWN'}`);
        console.log(`[FIX] [Text] Old markdownContainer parent: ${_proc.markdownContainer?.parentElement?.closest('[id^="agent-messages-"]')?.id || 'NONE'}`);

        // If processor was created for another container, reset its markdown container and point it at this contentDiv
        try {
            if (_proc.container !== contentDiv) {
                // Verify container mismatch is intentional
                const procParent = _proc.container?.closest('[id^="agent-messages-"]')?.id;
                const targetParent = contentDiv?.closest('[id^="agent-messages-"]')?.id;
                if (procParent && targetParent && procParent !== targetParent) {
                    console.error(`[CRITICAL] Processor container mismatch! Proc: ${procParent}, Target: ${targetParent}`);
                }

                _proc.markdownContainer = null;
                _proc.container = contentDiv;
                console.log(`[FIX] [Text] Reset markdownContainer - will be recreated in correct location`);
            }
        } catch (e) {
            console.warn('[WARN] Error updating TwoRule processor container:', e);
        }

        _proc.processChunk(textContent).then(() => {
            // processed
        }).catch((e) => {
            console.warn('[WARN] TwoRule processor failed to process chunk, falling back to markdown:', e);
            if (window.marked) {
                try {
                    contentDiv.innerHTML = marked.parse(existingBubble._fullText, { breaks: true, gfm: true });
                } catch (e2) {
                    contentDiv.textContent = existingBubble._fullText;
                }
            } else {
                contentDiv.textContent = existingBubble._fullText;
            }
        });
    } else if (window.marked) {
        try {
            contentDiv.innerHTML = marked.parse(existingBubble._fullText, { breaks: true, gfm: true });
        } catch (e) {
            contentDiv.textContent = existingBubble._fullText;
        }
    } else {
        contentDiv.textContent = existingBubble._fullText;
    }

    // Scroll
    container.scrollTop = container.scrollHeight;

    return existingBubble;
}

/**
 * Handle stream completion
 */
function handleCompleteEvent(thinkingBubble, textBubble) {
    console.log('[OK] [Complete] Stream finished');

    // Remove streaming animation and collapse thinking bubble
    if (thinkingBubble) {
        thinkingBubble.classList.remove('streaming');
        thinkingBubble.classList.add('collapsed');
    }

    // Finalize text rendering for this bubble (flush its processor if present)
    if (textBubble && textBubble._twoRuleProcessor && typeof textBubble._twoRuleProcessor.forceFlush === 'function') {
        try {
            textBubble._twoRuleProcessor.forceFlush();
        } catch (e) {
            console.warn('[WARN] Error flushing TwoRule processor on complete:', e);
        }
    }
}

/**
 * Handle error events
 */
function handleErrorEvent(data, container, textBubble) {
    console.error('[ERROR] [Error]', data.error || 'Unknown error');

    // Finalize any active processor before showing error
    if (textBubble && textBubble._twoRuleProcessor) {
        try {
            if (typeof textBubble._twoRuleProcessor.finalizeStream === 'function') {
                textBubble._twoRuleProcessor.finalizeStream();
            }
            if (window._twoRuleProcessors) {
                window._twoRuleProcessors.delete(textBubble._twoRuleProcessor);
            }
            textBubble._twoRuleProcessor = null;
        } catch (e) {
            console.warn('[WARN] Error finalizing processor on error:', e);
        }
    }

    const errorBubble = document.createElement('div');
    errorBubble.className = 'ai-message error';
    errorBubble.innerHTML = `
                                                                                                                                                                                    <div class="ai-message-header">
                                                                                                                                                                                        <div class="ai-message-avatar" style="background: rgba(239, 68, 68, 0.2);">
                                                                                                                                                                                            <i class="fas fa-exclamation-triangle" style="color: #ef4444;"></i>
                                                                                                                                                                                        </div>
                                                                                                                                                                                    </div>
                                                                                                                                                                                    <div class="ai-message-content" style="color: #ef4444;">
                                                                                                                                                                                        <strong>Error:</strong> ${data.error || 'Unknown error occurred'}
                                                                                                                                                                                    </div>
            `;
    container.appendChild(errorBubble);
    container.scrollTop = container.scrollHeight;
}

// ========================================
//  CACHE BUSTER - v2.1 (Nov 1, 2025)
// ========================================
console.log('%c SYNERGY DASHBOARD v2.1 LOADED', 'background: #22c55e; color: white; padding: 8px; font-weight: bold; font-size: 14px;');
console.log('%c[OK] JSON Parser Active', 'color: #22c55e; font-weight: bold;');
console.log('%c[OK] API Response Handler Active', 'color: #22c55e; font-weight: bold;');
console.log('%c[OK] 5 Comprehensive Demos Ready', 'color: #22c55e; font-weight: bold;');
console.log('%cIf you see this message, cache has been cleared successfully!', 'color: #3b82f6; font-style: italic;');
console.log('%c Universal Stream Handler Active', 'color: #8b5cf6; font-weight: bold;');

// Update header date/time display
function updateHeaderDateTime() {
    const now = new Date();

    // Day of week
    const days = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY'];
    const dayElement = document.getElementById('datetimeDay');
    if (dayElement) {
        dayElement.textContent = days[now.getDay()];
    }

    // Date (Day Month Year)
    const months = ['January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'];
    const dateElement = document.getElementById('datetimeDate');
    if (dateElement) {
        dateElement.textContent = `${now.getDate()} ${months[now.getMonth()]} ${now.getFullYear()}`;
    }

    // Time (12-hour format with AM/PM)
    const timeElement = document.getElementById('datetimeTime');
    if (timeElement) {
        let hours = now.getHours();
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12 || 12;
        timeElement.textContent = `${hours}:${minutes}:${seconds} ${ampm}`;
    }
}

// Initialize Synergy Dashboard when tab is activated
document.addEventListener('DOMContentLoaded', () => {
    // Update date/time immediately and then every second
    updateHeaderDateTime();
    setInterval(updateHeaderDateTime, 1000);

    // Initialize AI Prime button active state to match default chatOpen: true
    const aiPrimeBtn = document.getElementById('ai-prime-toggle-btn');
    if (aiPrimeBtn && AppState.chatOpen) {
        aiPrimeBtn.classList.add('active');
    }

    const synergyTab = document.querySelector('.sidebar-icon-btn[data-tab="synergy"]');
    if (synergyTab) {
        let initialized = false;
        synergyTab.addEventListener('click', async () => {
            if (!initialized) {
                // Ensure Supabase config is loaded before initializing
                await window.loadSupabaseConfig();
                await synergyBoard.init();
                // Initialize sidebar renderer
                SynergySidebar.init();
                initialized = true;
            }
        });
    }

    // Initialize link interception for Synergy sessions
    if (typeof synergyBoard !== 'undefined') {
        synergyBoard.initializeLinkInterception();
    }

    // Initialize notification system
    if (typeof NotificationSystem !== 'undefined') {
        NotificationSystem.init();
    }
});
