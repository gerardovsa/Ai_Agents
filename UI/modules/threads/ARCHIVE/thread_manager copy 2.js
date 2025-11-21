
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
        console.log(`[AssignThread] START: ${threadId} ? ${location}`);

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
        console.log(`[CASCADE] Starting UI updates for thread ${threadId}`);

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
            console.log(`[CASCADE] Clearing ${assignment.previous_location}`);
            await this._clearLocationUI(assignment.previous_location, threadId);
        }

        // STEP 3: Handle DISPLACED thread (if any)
        if (assignment.displaced_thread) {
            console.log(`[CASCADE] Handling displaced thread: ${assignment.displaced_thread}`);
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
        console.log(`[syncThreadLocationEverywhere] Syncing ${threadId} ? ${newLocation}`, options);

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

            // Update linkages if provi

            // ✅ FIX: ThreadManager.init() moved to initializeMainApp() (after authentication)
            // This ensures UserAuth.token is set before calling /api/auth/profile
            // Previously initialized on page load, causing 401 errors for real users

            // ==================== MESSAGE STORE (MINIMAL V1) ====================
            /**
             * MessageStore - Centralized message storage (Minimal Implementation)
             * 
             * Single source of truth for messages - eliminates duplicate storage.
             * This is a minimal implementation to test the concept.
             */
            class MessageStore {
                constructor() {
                    this._messages = new Map(); // threadId -> Message[]
                    this._messageIndex = new Map(); // messageId -> Message
                    console.log('[MessageStore] Initialized (minimal v1)');
                }

                /**
                 * Add message with duplicate detection
                 */
                async addMessage(threadId, message, options = {}) {
                    const {
                        checkDuplicates = true,
                        syncToBackend = false, // Disabled for now - test locally first
                        silent = false
                    } = options;

                    // Normalize content for comparison
                    const normalizedContent = this._normalizeContent(message.content);

                    // Check for duplicates
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
                                return existing; // Return existing message
                            }
                        }
                    }

                    // Add unique ID if not present
                    if (!message.id) {
                        message.id = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
                    }

                    // Add timestamp if not present
                    if (!message.created_at) {
                        message.created_at = new Date().toISOString();
                    }

                    // Store message
                    if (!this._messages.has(threadId)) {
                        this._messages.set(threadId, []);
                    }
                    this._messages.get(threadId).push(message);
                    this._messageIndex.set(message.id, message);

                    if (!silent) {
                        console.log(`[MessageStore] Message added: ${message.id} to thread ${threadId}`);
                    }

                    // Emit change event
                    this._emitChange('message-added', { threadId, message });

                    return message;
                }

                /**
                 * Get all messages for a thread
                 */
                getMessages(threadId) {
                    return this._messages.get(threadId) || [];
                }

                /**
                 * Get specific message by ID
                 */
                getMessage(messageId) {
                    return this._messageIndex.get(messageId);
                }

                /**
                 * Get message count for a thread
                 */
                getMessageCount(threadId) {
                    const messages = this._messages.get(threadId);
                    return messages ? messages.length : 0;
                }

                /**
                 * Clear messages for a thread
                 */
                clearThread(threadId) {
                    const messages = this._messages.get(threadId) || [];

                    // Remove from index
                    for (const msg of messages) {
                        this._messageIndex.delete(msg.id);
                    }

                    // Remove from thread storage
                    this._messages.delete(threadId);

                    console.log(`[MessageStore] Cleared ${messages.length} messages from thread ${threadId}`);
                }

                /**
                 * Normalize content for duplicate detection
                 */
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

                /**
                 * Emit change event for UI updates
                 */
                _emitChange(eventType, data) {
                    const event = new CustomEvent('messagestore-change', {
                        detail: { type: eventType, ...data }
                    });
                    window.dispatchEvent(event);
                }

                /**
                 * Get statistics
                 */
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

                /**
                 * Clear all data (for testing)
                 */
                clearAll() {
                    this._messages.clear();
                    this._messageIndex.clear();
                    console.log('[MessageStore] All data cleared');
                }
            }

            // Initialize global MessageStore
            window.MessageStore = new MessageStore();
            console.log('✅ MessageStore initialized at window.MessageStore');

            // ==================== DEVICE LOCK MANAGER ====================

            const DeviceLockManager = {
                deviceId: null,
                deviceName: null,

                async init() {
                    console.log(' [Device Lock] Initializing...');

                    // Generate or retrieve device ID
                    this.deviceId = localStorage.getItem('device_id');
                    if (!this.deviceId) {
                        this.deviceId = this.generateDeviceId();
                        localStorage.setItem('device_id', this.deviceId);
                    }

                    // Set device name
                    this.deviceName = this.getDeviceName();

                    // Register device with backend
                    await this.registerDevice();

                    console.log('✅ [Device Lock] Initialized:', { deviceId: this.deviceId, deviceName: this.deviceName });
                },

                generateDeviceId() {
                    return `browser-${navigator.userAgent.substring(0, 10).replace(/\s+/g, '-')}-${Date.now()}`;
                },

                getDeviceName() {
                    // Check for custom device name first
                    const customName = localStorage.getItem('device_custom_name');
                    if (customName) {
                        return customName;
                    }

                    // Fall back to auto-detected name
                    const ua = navigator.userAgent;
                    if (ua.includes('Chrome')) return 'Chrome Browser';
                    if (ua.includes('Firefox')) return 'Firefox Browser';
                    if (ua.includes('Safari')) return 'Safari Browser';
                    if (ua.includes('Edge')) return 'Edge Browser';
                    return 'Unknown Browser';
                },

                setCustomDeviceName(name) {
                    if (name && name.trim().length > 0) {
                        localStorage.setItem('device_custom_name', name.trim());
                        this.deviceName = name.trim();
                        // Re-register device with new name
                        this.registerDevice();
                        // Update all UI displays
                        const display = document.getElementById('current-device-name-display');
                        if (display) {
                            display.textContent = name.trim();
                        }
                        console.log('✅ [Device Lock] Custom device name set:', name.trim());
                    } else {
                        console.error('❌ [Device Lock] Invalid device name');
                    }
                },

                showDeviceNameModal() {
                    // Create modal if it doesn't exist
                    let modal = document.getElementById('device-name-modal-overlay');
                    if (!modal) {
                        modal = document.createElement('div');
                        modal.id = 'device-name-modal-overlay';
                        modal.className = 'device-name-modal-overlay';
                        modal.innerHTML = `
                        <div class="device-name-modal">
                            <div class="device-name-modal-header">
                                <div class="device-name-modal-title">
                                    <i class="fas fa-desktop"></i>
                                    <span>Name This Device</span>
                                </div>
                                <button class="device-name-modal-close" onclick="DeviceLockManager.closeDeviceNameModal()">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                            <div class="device-name-modal-body">
                                <label class="device-name-modal-label" for="device-name-input">
                                    Device Nickname
                                </label>
                                <input type="text" 
                                       id="device-name-input" 
                                       class="device-name-modal-input"
                                       placeholder="e.g., Work Laptop, Home Desktop, John's Chrome"
                                       maxlength="50"
                                       value="${this.deviceName || ''}">
                                <div class="device-name-modal-hint">
                                    This name will be shown when this device locks a thread. Makes it easier to identify in multi-device scenarios.
                                </div>
                            </div>
                            <div class="device-name-modal-footer">
                                <button class="device-name-modal-btn cancel" onclick="DeviceLockManager.closeDeviceNameModal()">
                                    Cancel
                                </button>
                                <button class="device-name-modal-btn save" onclick="DeviceLockManager.saveDeviceName()">
                                    Save Name
                                </button>
                            </div>
                        </div>
                    `;
                        document.body.appendChild(modal);

                        // Add click-outside-to-close
                        modal.addEventListener('click', (e) => {
                            if (e.target === modal) {
                                this.closeDeviceNameModal();
                            }
                        });

                        // Add Enter key to save
                        const input = modal.querySelector('#device-name-input');
                        input.addEventListener('keydown', (e) => {
                            if (e.key === 'Enter') {
                                this.saveDeviceName();
                            } else if (e.key === 'Escape') {
                                this.closeDeviceNameModal();
                            }
                        });
                    }

                    // Show modal
                    modal.classList.add('active');
                    setTimeout(() => {
                        const input = document.getElementById('device-name-input');
                        if (input) {
                            input.focus();
                            input.select();
                        }
                    }, 100);
                },

                closeDeviceNameModal() {
                    const modal = document.getElementById('device-name-modal-overlay');
                    if (modal) {
                        modal.classList.remove('active');
                    }
                },

                saveDeviceName() {
                    const input = document.getElementById('device-name-input');
                    if (input && input.value.trim()) {
                        this.setCustomDeviceName(input.value);
                        this.closeDeviceNameModal();
                        alert(`Device name updated to: "${input.value.trim()}"`);
                    } else {
                        alert('Please enter a valid device name');
                    }
                },

                async registerDevice() {
                    try {
                        const response = await fetch(`${API_BASE_URL}/api/device/register`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                device_id: this.deviceId,
                                device_name: this.deviceName,
                                user_id: UserAuth.user?.user_id || UserAuth.user?.id || 1,
                                device_fingerprint: navigator.userAgent
                            })
                        });

                        const result = await response.json();
                        if (result.success) {
                            console.log('✅ [Device Lock] Device registered:', result);
                        } else {
                            console.error('❌ [Device Lock] Registration failed:', result.error);
                        }
                    } catch (error) {
                        console.error('❌ [Device Lock] Registration error:', error);
                    }
                },

                async lockThread(threadId) {
                    try {
                        console.log(` [Device Lock] Locking thread ${threadId}...`);

                        const response = await fetch(`${API_BASE_URL}/api/threads/${threadId}/lock`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                device_id: this.deviceId,
                                user_id: UserAuth.user?.user_id || UserAuth.user?.id || 1
                            })
                        });

                        const result = await response.json();

                        if (result.success) {
                            console.log('✅ [Device Lock] Thread locked:', result);

                            // Update UI - add locked border
                            const threadCards = document.querySelectorAll(`[data-thread-id="${threadId}"]`);
                            threadCards.forEach(card => card.classList.add('locked'));

                            // Show unlock button, hide lock button
                            const lockBtn = document.getElementById(`lock-btn-${threadId}`);
                            const unlockBtn = document.getElementById(`unlock-btn-${threadId}`);
                            const lockStatus = document.getElementById(`lock-status-${threadId}`);

                            if (lockBtn) lockBtn.style.display = 'none';
                            if (unlockBtn) unlockBtn.style.display = 'inline-flex';
                            if (lockStatus) {
                                lockStatus.style.display = 'none';
                            }

                            this.showNotification(`Thread locked to ${this.deviceName}`, 'success');
                        } else {
                            console.error('❌ [Device Lock] Lock failed:', result.error);
                            this.showNotification(`Failed to lock: ${result.error}`, 'error');
                        }
                    } catch (error) {
                        console.error('❌ [Device Lock] Lock error:', error);
                        this.showNotification('Failed to lock thread', 'error');
                    }
                },

                async unlockThread(threadId) {
                    try {
                        console.log(` [Device Lock] Unlocking thread ${threadId}...`);

                        const response = await fetch(`${API_BASE_URL}/api/threads/${threadId}/unlock`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                device_id: this.deviceId,
                                user_id: UserAuth.user?.user_id || UserAuth.user?.id || 1
                            })
                        });

                        const result = await response.json();

                        if (result.success) {
                            console.log('✅ [Device Lock] Thread unlocked:', result);

                            // Update UI - remove locked border
                            const threadCards = document.querySelectorAll(`[data-thread-id="${threadId}"]`);
                            threadCards.forEach(card => card.classList.remove('locked'));

                            // Show lock button, hide unlock button
                            const lockBtn = document.getElementById(`lock-btn-${threadId}`);
                            const unlockBtn = document.getElementById(`unlock-btn-${threadId}`);
                            const lockStatus = document.getElementById(`lock-status-${threadId}`);

                            if (lockBtn) lockBtn.style.display = 'inline-flex';
                            if (unlockBtn) unlockBtn.style.display = 'none';
                            if (lockStatus) lockStatus.style.display = 'none';

                            // Re-enable chat input if this was the active thread
                            const chatInput = document.querySelector('.ai-chat-input-container');
                            if (chatInput) chatInput.classList.remove('locked-read-only');

                            this.showNotification('Thread unlocked', 'success');
                        } else {
                            console.error('❌ [Device Lock] Unlock failed:', result.error);
                            this.showNotification(`Failed to unlock: ${result.error}`, 'error');
                        }
                    } catch (error) {
                        console.error('❌ [Device Lock] Unlock error:', error);
                        this.showNotification('Failed to unlock thread', 'error');
                    }
                },

                async checkLockStatus(threadId) {
                    try {
                        const response = await fetch(
                            `${API_BASE_URL}/api/threads/${threadId}/lock-status?device_id=${this.deviceId}&user_id=${UserAuth.user?.user_id || UserAuth.user?.id || 1}`
                        );

                        const result = await response.json();

                        if (result.locked) {
                            // Thread is locked
                            if (result.is_current_device) {
                                // Locked by this device - show unlock button
                                this.showUnlockButton(threadId);
                            } else {
                                // Locked by another device - show status badge + disable editing
                                this.showLockedStatus(threadId, result.locked_to_device);
                                if (!result.can_edit) {
                                    this.disableChatInput();
                                }
                            }
                        } else {
                            // Thread is unlocked - show lock button
                            this.showLockButton(threadId);
                        }

                        return result;
                    } catch (error) {
                        console.error('❌ [Device Lock] Status check error:', error);
                        return null;
                    }
                },

                showLockButton(threadId) {
                    const container = document.getElementById(`lock-controls-${threadId}`);
                    const lockBtn = document.getElementById(`lock-btn-${threadId}`);
                    const unlockBtn = document.getElementById(`unlock-btn-${threadId}`);
                    const lockStatus = document.getElementById(`lock-status-${threadId}`);

                    if (container) container.style.display = 'flex';
                    if (lockBtn) lockBtn.style.display = 'inline-flex';
                    if (unlockBtn) unlockBtn.style.display = 'none';
                    if (lockStatus) lockStatus.style.display = 'none';
                },

                showUnlockButton(threadId) {
                    const container = document.getElementById(`lock-controls-${threadId}`);
                    const lockBtn = document.getElementById(`lock-btn-${threadId}`);
                    const unlockBtn = document.getElementById(`unlock-btn-${threadId}`);
                    const lockStatus = document.getElementById(`lock-status-${threadId}`);

                    if (container) container.style.display = 'flex';
                    if (lockBtn) lockBtn.style.display = 'none';
                    if (unlockBtn) unlockBtn.style.display = 'inline-flex';
                    if (lockStatus) lockStatus.style.display = 'none';
                },

                showLockedStatus(threadId, deviceName) {
                    const container = document.getElementById(`lock-controls-${threadId}`);
                    const lockBtn = document.getElementById(`lock-btn-${threadId}`);
                    const unlockBtn = document.getElementById(`unlock-btn-${threadId}`);
                    const lockStatus = document.getElementById(`lock-status-${threadId}`);
                    const deviceNameEl = document.getElementById(`lock-device-name-${threadId}`);

                    if (container) container.style.display = 'flex';
                    if (lockBtn) lockBtn.style.display = 'none';
                    if (unlockBtn) unlockBtn.style.display = 'none';
                    if (lockStatus) lockStatus.style.display = 'inline-flex';
                    if (deviceNameEl) deviceNameEl.textContent = deviceName || 'Another Device';

                    // Add locked border to thread card
                    const threadCards = document.querySelectorAll(`[data-thread-id="${threadId}"]`);
                    threadCards.forEach(card => card.classList.add('locked'));
                },

                disableChatInput() {
                    const chatInput = document.querySelector('.ai-chat-input-container');
                    if (chatInput) {
                        chatInput.classList.add('locked-read-only');
                    }
                },

                enableChatInput() {
                    const chatInput = document.querySelector('.ai-chat-input-container');
                    if (chatInput) {
                        chatInput.classList.remove('locked-read-only');
                    }
                },

                showNotification(message, type = 'info') {
                    console.log(`${type === 'error' ? '❌' : '✅'} [Device Lock] ${message}`);
                    // TODO: Add toast notification UI
                }
            };

            // ==================== USER AUTHENTICATION SYSTEM ====================

            const UserAuth = {
                token: null,
                user: null,
                isInitialized: false, // Prevent double initialization
                mainAppInitialized: false, // Prevent double main app initialization

                async checkExistingSession() {
                    // Check if user is already logged in
                    const storedToken = localStorage.getItem('authToken');
                    const storedUser = localStorage.getItem('userProfile');

                    if (storedToken && storedUser) {
                        this.token = storedToken;
                        this.user = JSON.parse(storedUser);

                        // Verify token is still valid
                        const valid = await this.verifyToken();
                        return valid;
                    }
                    return false;
                },

                init() {
                    // PREVENT DOUBLE INITIALIZATION
                    if (this.isInitialized) {
                        console.log('[AUTH] Init already called, skipping duplicate initialization');
                        return;
                    }
                    this.isInitialized = true;
                    console.log('[AUTH] Initializing UserAuth...');

                    // Get loading overlay elements
                    const loadingOverlay = document.getElementById('authLoadingOverlay');
                    const loadingText = document.getElementById('authLoadingText');
                    const progressFill = document.getElementById('authProgressFill');

                    // Show loading overlay immediately
                    loadingOverlay.style.display = 'flex';
                    loadingOverlay.classList.remove('hidden');
                    progressFill.classList.add('active');

                    // Set initial progress
                    this.setLoadingProgress(0, 'Checking authentication...');

                    // Check if there's an OAuth callback token in the URL FIRST
                    const urlParams = new URLSearchParams(window.location.search);
                    const hasOAuthToken = urlParams.has('token');

                    // DEVELOPMENT MODE: Auto-login for localhost testing (opt-in with ?dev=true)
                    // Usage: http://localhost:5001/?dev=true to enable auto-login
                    // Default: false (requires real OAuth)
                    const devModeEnabled = urlParams.get('dev') === 'true';

                    if (devModeEnabled && !hasOAuthToken && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
                        const hasDevUser = localStorage.getItem('dev_mode_user');
                        if (!hasDevUser) {
                            console.log('[DEV MODE] Dev mode enabled via ?dev=true - Auto-login as test user');
                            this.setLoadingProgress(10, 'Loading dev environment...');
                            // Create a mock token and user for local testing
                            const mockUser = {
                                id: 1,
                                user_id: 1,
                                username: 'printing@inhouseprint.com.au',
                                email: 'printing@inhouseprint.com.au',
                                auth_platform: 'local_dev'
                            };
                            this.token = 'dev-mode-token-12345';
                            this.user = mockUser;
                            localStorage.setItem('authToken', this.token);
                            localStorage.setItem('userProfile', JSON.stringify(mockUser));
                            localStorage.setItem('dev_mode_user', 'true');
                            console.log('? [DEV MODE] Auto-logged in as test user');
                            // DON'T call showMainApp() here - let DOMContentLoaded flow handle it
                            // This prevents double initialization
                            return;
                        }
                    }

                    // Check if user is already logged in
                    const storedToken = localStorage.getItem('authToken');
                    const storedUser = localStorage.getItem('userProfile');

                    if (storedToken && storedUser) {
                        console.log('Token found, verifying...');
                        this.setLoadingProgress(5, 'Verifying credentials...');

                        this.token = storedToken;
                        this.user = JSON.parse(storedUser);

                        // Verify token is still valid
                        this.verifyToken().then(valid => {
                            if (valid) {
                                console.log('? Token valid, loading application...');
                                this.setLoadingProgress(10, 'Loading your workspace...');

                                // Small delay to show loading state
                                setTimeout(() => {
                                    this.showMainApp();
                                }, 500);
                            } else {
                                console.log('? Token invalid, showing login...');
                                this.hideLoadingOverlay();
                                this.showLogin();
                            }
                        }).catch(error => {
                            console.error('? Token verification error:', error);
                            this.hideLoadingOverlay();
                            this.showLogin();
                        });
                    } else {
                        console.log('No token found, showing login...');
                        this.hideLoadingOverlay();
                        this.showLogin();
                    }
                },

                async verifyToken() {
                    try {
                        const response = await fetch(`${window.API_BASE_URL || API_BASE_URL}/api/auth/verify`, {
                            method: 'GET',
                            headers: {
                                'Authorization': `Bearer ${this.token}`
                            }
                        });

                        return response.ok;
                    } catch (error) {
                        console.error('Token verification failed:', error);
                        return false;
                    }
                },

                async login(username, password) {
                    const loginBtn = document.getElementById('loginBtn');
                    const errorDiv = document.getElementById('loginError');
                    const loadingOverlay = document.getElementById('authLoadingOverlay');
                    const loadingText = document.getElementById('authLoadingText');
                    const progressFill = document.getElementById('authProgressFill');

                    // Disable button, show loading in button
                    loginBtn.disabled = true;
                    loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing in...';
                    errorDiv.classList.remove('show');

                    try {
                        const response = await fetch(`${window.API_BASE_URL || API_BASE_URL}/api/auth/login`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ username, password })
                        });

                        const data = await response.json();

                        if (data.success) {
                            this.token = data.token;
                            this.user = data.user;

                            // Store in localStorage
                            localStorage.setItem('authToken', this.token);
                            localStorage.setItem('userProfile', JSON.stringify(this.user));

                            console.log('? Login successful!');

                            // Hide login overlay immediately
                            document.getElementById('loginOverlay').style.display = 'none';

                            // Show loading overlay with progress
                            loadingOverlay.style.display = 'flex';
                            loadingOverlay.classList.remove('hidden');
                            progressFill.classList.add('active');
                            this.setLoadingProgress(10, 'Loading your workspace...');

                            // Load app with delay to show progress
                            setTimeout(() => {
                                this.showMainApp();
                            }, 500);

                            return { success: true };
                        } else {
                            throw new Error(data.error || 'Login failed');
                        }
                    } catch (error) {
                        console.error('? Login error:', error);
                        errorDiv.textContent = error.message || 'Login failed. Please try again.';
                        errorDiv.classList.add('show');
                        loginBtn.disabled = false;
                        loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Sign In';
                        return { success: false, error: error.message };
                    }
                },

                logout() {
                    this.token = null;
                    this.user = null;
                    this.isInitialized = false; // Reset init flag for re-login
                    this.mainAppInitialized = false; // Reset main app flag for re-login
                    localStorage.removeItem('authToken');
                    localStorage.removeItem('userProfile');
                    localStorage.removeItem('dev_mode_user'); // Clear dev mode flag
                    this.showLogin();
                },

                hideLoadingOverlay() {
                    const loadingOverlay = document.getElementById('authLoadingOverlay');
                    if (loadingOverlay) {
                        loadingOverlay.classList.add('hidden');
                        setTimeout(() => {
                            loadingOverlay.style.display = 'none';
                        }, 300);
                    }
                },

                showLogin() {
                    const loginOverlay = document.getElementById('loginOverlay');
                    const platformContainer = document.querySelector('.platform-container');

                    // Reset display states
                    loginOverlay.style.display = 'flex';
                    loginOverlay.classList.remove('hidden');
                    platformContainer.classList.remove('active');
                    platformContainer.style.opacity = '0';

                    console.log('[AUTH] Login screen displayed');
                },

                /**
                 * Update loading progress bar
                 * @param {number} percent - Progress percentage (0-100)
                 * @param {string} text - Loading text to display
                 */
                setLoadingProgress(percent, text) {
                    const progressFill = document.getElementById('authProgressFill');
                    const loadingText = document.getElementById('authLoadingText');

                    if (progressFill) {
                        progressFill.style.width = `${Math.min(100, Math.max(0, percent))}%`;
                    }
                    if (loadingText && text) {
                        loadingText.textContent = text;
                    }

                    console.log(`[LOADING] ${percent}% - ${text}`);
                },

                async showMainApp() {
                    // PREVENT DOUBLE INITIALIZATION OF MAIN APP
                    if (this.mainAppInitialized) {
                        console.log('[AUTH] Main app already initialized, skipping duplicate call');
                        return;
                    }
                    this.mainAppInitialized = true;

                    console.log('? Login successful - Initializing main application...');

                    // Get loading overlay elements
                    const loadingText = document.getElementById('authLoadingText');
                    const loginOverlay = document.getElementById('loginOverlay');
                    const platformContainer = document.querySelector('.platform-container');

                    // Start progress tracking
                    this.setLoadingProgress(5, 'Initializing application...');

                    // Hide login overlay
                    loginOverlay.style.display = 'none';
                    loginOverlay.classList.add('hidden');

                    // Prepare platform container
                    platformContainer.classList.add('active');
                    platformContainer.style.opacity = '0';

                    try {
                        // PHASE 1: Initialize main app with existing libraries (15% progress)
                        this.setLoadingProgress(15, 'Loading modules...');
                        await window.initializeMainApp();
                        this.setLoadingProgress(25, 'Modules loaded');

                        // PHASE 2: Load heavy libraries AFTER app is visible (25-75% progress)
                        this.setLoadingProgress(30, 'Loading additional resources...');
                        console.log('[POST-AUTH] Loading heavy libraries...');
                        await this.loadPostAuthLibraries();
                        this.setLoadingProgress(75, 'Resources loaded');

                        // PHASE 3: Load user profile (75-90% progress)
                        this.setLoadingProgress(80, 'Loading your profile...');
                        await loadUserProfile();
                        this.setLoadingProgress(90, 'Profile loaded');

                        if (this.user) {
                            console.log('? Logged in as:', this.user.username);
                            console.log('Gmail accounts:', this.user.gmail_accounts?.length || 0);
                        }

                        // PHASE 4: Final setup (90-100% progress)
                        this.setLoadingProgress(95, 'Almost ready...');

                        // Fade in main app
                        requestAnimationFrame(() => {
                            platformContainer.style.transition = 'opacity 0.4s ease-in';
                            platformContainer.style.opacity = '1';
                        });

                        // Complete progress and hide overlay
                        this.setLoadingProgress(100, 'Ready!');
                        setTimeout(() => {
                            this.hideLoadingOverlay();
                        }, 500);

                    } catch (error) {
                        console.error('? [AUTH] Failed to initialize main app:', error);
                        this.setLoadingProgress(0, 'Error loading application');
                        // Still hide loading overlay on error
                        setTimeout(() => {
                            this.hideLoadingOverlay();
                        }, 1000);
                    }
                },

                getAuthHeaders() {
                    return {
                        'Authorization': `Bearer ${this.token}`,
                        'Content-Type': 'application/json'
                    };
                },

                /**
                 * Load heavy non-critical libraries AFTER authentication
                 * This improves initial page load time significantly (saves ~5MB)
                 */
                async loadPostAuthLibraries() {
                    console.log('[POST-AUTH] Loading heavy libraries sequentially...');
                    const startTime = performance.now();

                    try {
                        // SKIPPING TIPTAP: UMD builds don't expose proper globals, causing initialization errors
                        // TipTap rich text editor will be added later using ES modules instead of UMD
                        console.log('  Skipping TipTap libraries (not currently used in UI)');

                        // STEP 4: Skip Yjs Collaboration (not implemented yet, causing 404 errors)
                        // Real-time collaboration will be added in future version
                        console.log('   Skipping Yjs collaboration libraries (not needed yet)');

                        // STEP 5: Handsontable (1.8MB - can load in parallel with others)
                        this.setLoadingProgress(40, 'Loading spreadsheet libraries...');
                        await Promise.all([
                            this.loadScript('handsontable', 'https://cdn.jsdelivr.net/npm/handsontable/dist/handsontable.full.min.js'),
                            this.loadScript('hyperformula', 'https://cdn.jsdelivr.net/npm/hyperformula/dist/hyperformula.full.min.js'),
                            this.loadScript('jspdf', 'https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js'),
                            this.loadScript('html2canvas', 'https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js')
                        ]);
                        this.setLoadingProgress(70, 'Libraries loaded');
                        console.log('  ? Handsontable & PDF libraries loaded');

                        const endTime = performance.now();
                        console.log(`? [POST-AUTH] All heavy libraries loaded in ${((endTime - startTime) / 1000).toFixed(2)}s`);

                        // Notify modules that libraries are ready
                        window.dispatchEvent(new CustomEvent('postAuthLibrariesLoaded'));

                    } catch (error) {
                        console.error('? [POST-AUTH] Failed to load libraries:', error);
                    }
                },

                /**
                 * Load a script dynamically
                 * @param {string} id - Unique ID for the script element
                 * @param {string} src - URL of the script to load
                 * @returns {Promise} Resolves when script loads, rejects on error
                 */
                loadScript(id, src) {
                    return new Promise((resolve, reject) => {
                        // Check if already loaded
                        if (document.getElementById(id)) {
                            console.log(`   ${id} already loaded`);
                            resolve();
                            return;
                        }

                        const script = document.createElement('script');
                        script.id = id;
                        script.src = src;
                        script.onload = () => resolve();
                        script.onerror = () => reject(new Error(`Failed to load ${src}`));
                        document.head.appendChild(script);
                    });
                },

                /**
                 * Wait for a global variable to be available
                 * @param {string} globalPath - Path to global variable (e.g., 'window.tiptapCore')
                 * @param {number} timeout - Max wait time in ms (default: 2000)
                 * @returns {Promise} Resolves when global is available
                 */
                waitForGlobal(globalPath, timeout = 2000) {
                    return new Promise((resolve, reject) => {
                        const startTime = Date.now();

                        const checkGlobal = () => {
                            try {
                                // Evaluate the global path
                                if (eval(globalPath)) {
                                    resolve();
                                    return;
                                }
                            } catch (e) {
                                // Path doesn't exist yet
                            }

                            // Check timeout
                            if (Date.now() - startTime > timeout) {
                                console.warn(`Timeout waiting for ${globalPath}`);
                                resolve(); // Don't reject, just continue
                                return;
                            }

                            // Check again in 50ms
                            setTimeout(checkGlobal, 50);
                        };

                        checkGlobal();
                    });
                }
            };

            // ✅ CRITICAL: Make UserAuth globally accessible for ThreadManager and other modules
            window.UserAuth = UserAuth;
            console.log(' [INIT] UserAuth attached to window object');

            // Login form handler
            async function handleLogin(event) {
                event.preventDefault();

                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                const loginBtn = document.getElementById('loginBtn');
                const errorDiv = document.getElementById('loginError');

                // Disable button
                loginBtn.disabled = true;
                loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing in...';
                errorDiv.classList.remove('show');

                // Attempt login
                const result = await UserAuth.login(username, password);

                if (result.success) {
                    // Success - UserAuth.showMainApp() already called
                    console.log('Login successful');
                } else {
                    // Show error
                    errorDiv.textContent = result.error;
                    errorDiv.classList.add('show');

                    // Re-enable button
                    loginBtn.disabled = false;
                    loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Sign In';
                }
            }

            // Logout handler
            // Inline DOM confirmation helper (used when UIComponents isn't available)
            function createInlineConfirm(opts) {
                const title = opts.title || 'Confirm Action';
                const message = opts.message || 'Are you sure?';
                const confirmLabel = opts.confirmLabel || 'Confirm';
                const cancelLabel = opts.cancelLabel || 'Cancel';

                const overlay = document.createElement('div');
                overlay.className = 'inline-confirm-overlay';
                overlay.style.position = 'fixed';
                overlay.style.inset = '0';
                overlay.style.background = 'rgba(0,0,0,0.45)';
                overlay.style.display = 'flex';
                overlay.style.alignItems = 'center';
                overlay.style.justifyContent = 'center';
                overlay.style.zIndex = 2147483647;

                const dialog = document.createElement('div');
                dialog.className = 'inline-confirm-dialog';
                dialog.style.background = 'var(--bg-primary, #0b1220)';
                dialog.style.color = 'var(--text-primary, #e6edf3)';
                dialog.style.padding = '18px';
                dialog.style.borderRadius = '10px';
                dialog.style.minWidth = '320px';
                dialog.style.maxWidth = '540px';
                dialog.style.boxShadow = '0 12px 40px rgba(0,0,0,0.6)';

                const titleEl = document.createElement('div');
                titleEl.style.fontWeight = 700;
                titleEl.style.marginBottom = '8px';
                titleEl.textContent = title;

                const msgEl = document.createElement('div');
                msgEl.style.marginBottom = '14px';
                msgEl.style.lineHeight = '1.4';
                msgEl.textContent = message;

                const actions = document.createElement('div');
                actions.style.display = 'flex';
                actions.style.justifyContent = 'flex-end';
                actions.style.gap = '10px';

                const cancelBtn = document.createElement('button');
                cancelBtn.className = 'btn btn-secondary';
                cancelBtn.textContent = cancelLabel;

                const confirmBtn = document.createElement('button');
                confirmBtn.className = 'btn btn-primary';
                confirmBtn.textContent = confirmLabel;

                actions.appendChild(cancelBtn);
                actions.appendChild(confirmBtn);

                dialog.appendChild(titleEl);
                dialog.appendChild(msgEl);
                dialog.appendChild(actions);
                overlay.appendChild(dialog);
                document.body.appendChild(overlay);

                // Focus
                confirmBtn.focus();

                function cleanup() {
                    try { overlay.remove(); } catch (e) { }
                }

                cancelBtn.addEventListener('click', () => {
                    cleanup();
                    if (typeof opts.onCancel === 'function') opts.onCancel();
                });

                confirmBtn.addEventListener('click', () => {
                    cleanup();
                    if (typeof opts.onConfirm === 'function') opts.onConfirm();
                });

                return {
                    element: overlay,
                    destroy: cleanup,
                    hide: () => overlay.style.display = 'none',
                    show: () => overlay.style.display = 'flex'
                };
            }

            function handleLogout() {
                try {
                    if (window.UIComponents && typeof UIComponents.showConfirmation === 'function') {
                        UIComponents.showConfirmation({
                            title: 'Logout?',
                            message: 'Are you sure you want to logout?',
                            variant: 'warning',
                            confirmLabel: 'Logout',
                            cancelLabel: 'Stay Logged In',
                            onConfirm: () => { UserAuth.logout(); }
                        });
                    } else {
                        // Use inline DOM modal instead of native confirm()
                        console.warn('[UI] UIComponents not available, using inline DOM confirmation for logout');
                        createInlineConfirm({
                            title: 'Logout?',
                            message: 'Are you sure you want to logout?',
                            confirmLabel: 'Logout',
                            cancelLabel: 'Stay Logged In',
                            onConfirm: () => { UserAuth.logout(); },
                            onCancel: () => { /* no-op */ }
                        });
                    }
                } catch (err) {
                    console.error('[UI] handleLogout error:', err);
                    // As a last resort, show inline confirm
                    createInlineConfirm({
                        title: 'Logout?',
                        message: 'Are you sure you want to logout?',
                        confirmLabel: 'Logout',
                        cancelLabel: 'Stay Logged In',
                        onConfirm: () => { try { UserAuth.logout(); } catch (e) { console.error('Logout failed', e); } }
                    });
                }
            }

            // ==================== USER PROFILE DROPDOWN ====================

            function toggleUserMenu(event) {
                // Prevent event bubbling to avoid immediate close
                if (event) {
                    event.stopPropagation();
                }

                const menu = document.getElementById('userDropdownMenu');
                const btnHeader = document.getElementById('userProfileBtn');
                const btnSidebar = document.getElementById('userProfileBtn-sidebar');

                if (!menu) {
                    console.error(' Profile dropdown elements not found');
                    return;
                }

                menu.classList.toggle('active');

                // Toggle active state on both buttons
                if (btnHeader) btnHeader.classList.toggle('active');
                if (btnSidebar) btnSidebar.classList.toggle('active');

                console.log(' Profile menu toggled:', menu.classList.contains('active') ? 'OPEN' : 'CLOSED');
            }

            function toggleNotificationPanel(event) {
                // Prevent event bubbling
                if (event) {
                    event.stopPropagation();
                }

                let panel = document.getElementById('synergy-notifications');

                // Create panel if it doesn't exist
                if (!panel) {
                    if (typeof NotificationSystem !== 'undefined' && NotificationSystem.createNotificationPanel) {
                        NotificationSystem.createNotificationPanel();
                        panel = document.getElementById('synergy-notifications');
                    }

                    if (!panel) {
                        console.warn('Notification system not initialized yet');
                        return;
                    }
                }

                const isOpen = panel.classList.toggle('show');
                const notifBtn = document.getElementById('notificationBellBtn-sidebar');
                if (notifBtn) {
                    notifBtn.classList.toggle('active', isOpen);
                }
                console.log('Notification panel toggled:', panel.classList.contains('show') ? 'OPEN' : 'CLOSED');
            }

            // Initialize right sidebar buttons
            function initRightSidebar() {
                // Prevent duplicate initialization
                if (window._rightSidebarInitialized) {
                    console.warn('Right sidebar already initialized, skipping...');
                    return;
                }
                window._rightSidebarInitialized = true;
                console.log('? Initializing right sidebar buttons...');

                // AI Prime Toggle - Always works regardless of chat state
                const aiPrimeBtn = document.getElementById('ai-prime-toggle-btn');
                if (aiPrimeBtn) {
                    aiPrimeBtn.addEventListener('click', function () {
                        const panel = document.getElementById('ai-chat-panel');
                        const wrapper = document.getElementById('main-content-wrapper');

                        if (panel && wrapper) {
                            // Toggle chat state
                            AppState.chatOpen = !AppState.chatOpen;

                            if (AppState.chatOpen) {
                                wrapper.classList.remove('chat-collapsed');
                                panel.style.display = 'flex';
                                this.classList.add('active');
                                console.log('AI Prime chat OPENED');
                            } else {
                                wrapper.classList.add('chat-collapsed');
                                panel.style.display = 'none';
                                this.classList.remove('active');
                                console.log('AI Prime chat CLOSED');
                            }
                        } else {
                            console.warn('Chat panel or wrapper not found');
                        }
                    });
                }

                // New Chat - Opens new chat modal
                const newChatBtn = document.getElementById('new-chat-btn');
                if (newChatBtn) {
                    newChatBtn.addEventListener('click', function (event) {
                        event.preventDefault();
                        event.stopPropagation();

                        // Check if modal already exists
                        const existingModal = document.getElementById('newChatModalOverlay');
                        if (existingModal) {
                            console.warn('Modal already open, skipping...');
                            return;
                        }

                        console.log('New chat button clicked from right sidebar');
                        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.showNewChatModal === 'function') {
                            ThreadManager.showNewChatModal('prime');
                        } else {
                            console.error('ThreadManager.showNewChatModal function not found');
                        }
                    });
                }

                // Threads button now has onclick in HTML to call ThreadManager.toggleThreadMenu()
                // No event listener needed here

                // Quick Actions - Toggles prompt sidebar
                const quickActionsBtn = document.getElementById('quick-actions-btn');
                if (quickActionsBtn) {
                    quickActionsBtn.addEventListener('click', function (event) {
                        event.preventDefault();
                        event.stopPropagation();
                        console.log('? Quick actions button clicked');

                        // Toggle prompt sidebar
                        const promptSidebar = document.getElementById('prompt-sidebar');
                        if (promptSidebar) {
                            const isOpen = promptSidebar.classList.toggle('show');
                            this.classList.toggle('active', isOpen);
                            console.log('? Prompt sidebar toggled:', promptSidebar.classList.contains('show') ? 'VISIBLE' : 'HIDDEN');
                        } else {
                            console.warn('Prompt sidebar not found - may not be initialized yet');
                        }
                    });
                }
            }

            // Close dropdown when clicking outside
            document.addEventListener('click', (e) => {
                const container = document.getElementById('userProfileContainer');
                const menu = document.getElementById('userDropdownMenu');
                const btnHeader = document.getElementById('userProfileBtn');
                const btnSidebar = document.getElementById('userProfileBtn-sidebar');

                // Check if click is outside both the container and the sidebar button
                const clickedSidebarBtn = btnSidebar && btnSidebar.contains(e.target);
                const clickedContainer = container && container.contains(e.target);

                if (!clickedContainer && !clickedSidebarBtn) {
                    if (menu?.classList.contains('active')) {
                        menu.classList.remove('active');
                        if (btnHeader) btnHeader.classList.remove('active');
                        if (btnSidebar) btnSidebar.classList.remove('active');
                        console.log(' Profile menu closed (click outside)');
                    }
                }
            });

            // Load user profile data
            async function loadUserProfile() {
                console.log(' Loading user profile...');
                console.log(' Token available:', !!UserAuth.token);
                console.log(' User data:', UserAuth.user);

                try {
                    const response = await fetch(`${API_BASE_URL}/api/auth/profile`, {
                        headers: {
                            'Authorization': `Bearer ${UserAuth.token}`
                        }
                    });

                    console.log(' Profile API response status:', response.status);

                    if (!response.ok) {
                        throw new Error(`Failed to load profile: ${response.status} ${response.statusText}`);
                    }

                    const data = await response.json();
                    console.log('Profile data received:', data);

                    if (data.success) {
                        const profile = data.profile;

                        console.log('✅ User profile loaded:', profile);
                        console.log(' User ID (id):', profile.id);
                        console.log(' User ID (user_id):', profile.user_id);

                        // CRITICAL: Save user data to UserAuth AND localStorage
                        // ✅ Ensure both 'id' and 'user_id' are present
                        if (profile.user_id && !profile.id) profile.id = profile.user_id;
                        if (profile.id && !profile.user_id) profile.user_id = profile.id;

                        UserAuth.user = profile;
                        window.currentUserId = profile.id || profile.user_id; // Initialize global user ID for settings save
                        localStorage.setItem('userProfile', JSON.stringify(profile));

                        // Initialize Device Lock Manager after user profile is loaded
                        if (typeof DeviceLockManager !== 'undefined' && !DeviceLockManager.deviceId) {
                            DeviceLockManager.init();
                        }

                        // Update header button
                        const userNameEl = document.getElementById('userName');
                        const userRoleEl = document.getElementById('userRoleText');

                        if (userNameEl) userNameEl.textContent = profile.username;
                        if (userRoleEl) userRoleEl.textContent = profile.role;

                        // Update dropdown header
                        const dropdownNameEl = document.getElementById('dropdownUserName');
                        const dropdownEmailEl = document.getElementById('dropdownUserEmail');

                        if (dropdownNameEl) dropdownNameEl.textContent = profile.username;
                        if (dropdownEmailEl) dropdownEmailEl.textContent = profile.email;

                        const roleBadge = document.getElementById('roleBadge');
                        if (roleBadge) {
                            roleBadge.textContent = profile.role;
                            if (profile.role === 'admin') {
                                roleBadge.classList.add('admin');
                            }
                        }

                        // Update Gmail accounts count and populate list
                        // If user logged in via Google OAuth, automatically add their email
                        let gmailAccounts = profile.gmail_accounts || [];
                        if (profile.email && profile.email.includes('@') && gmailAccounts.length === 0) {
                            // Auto-add the user's login email as primary Gmail account
                            gmailAccounts = [{
                                email: profile.email,
                                display_name: profile.username || 'Primary Account',
                                is_primary: true
                            }];
                            console.log('Auto-added Gmail account:', profile.email);
                        }

                        const gmailCount = gmailAccounts.length;
                        const gmailCountEl = document.getElementById('gmailCount');
                        if (gmailCountEl) {
                            gmailCountEl.textContent = `${gmailCount} connected`;
                            gmailCountEl.style.color = gmailCount > 0 ? 'var(--success-color, #22c55e)' : 'var(--text-muted)';
                        }

                        // Populate Gmail accounts list
                        const gmailListEl = document.getElementById('gmailAccountsList');
                        if (gmailListEl && gmailAccounts.length > 0) {
                            gmailListEl.innerHTML = gmailAccounts.map((account, index) => `
                            <div class="service-item" style="flex-direction: row; gap: var(--space-2);">
                                <i class="fas fa-envelope" style="color: var(--accent-primary); font-size: 14px;"></i>
                                <span style="font-size: 13px; color: var(--text-primary); flex: 1;">${account.email}</span>
                                ${account.is_primary || index === 0 ? '<span style="font-size: 11px; padding: 2px 8px; background: var(--accent-primary); color: white; border-radius: 4px;">Primary</span>' : ''}
                            </div>
                        `).join('');
                        }

                        // Check OAuth status from backend (checks actual tokens in database)
                        const googleOAuthConnected = profile.google_oauth_connected || false;
                        const microsoftOAuthConnected = profile.microsoft_oauth_connected || false;

                        console.log(' Google OAuth connected:', googleOAuthConnected);
                        console.log(' Microsoft OAuth connected:', microsoftOAuthConnected);

                        // CONDITIONAL OAUTH UI: Show only relevant OAuth section based on auth platform
                        const authPlatform = profile.auth_platform; // 'google' | 'microsoft' | null
                        console.log(' Auth Platform:', authPlatform);

                        // Get all platform sections
                        const googleWorkspaceSection = document.getElementById('googleWorkspaceSection');
                        const microsoft365Section = document.getElementById('microsoft365Section');
                        const gmailSmtpSection = document.getElementById('gmailSmtpSection');

                        const isGoogleUser = authPlatform === 'google';
                        const isMicrosoftUser = authPlatform === 'microsoft';
                        const isLocalUser = !authPlatform; // Local accounts rely on service-account provisioning

                        if (googleWorkspaceSection) {
                            googleWorkspaceSection.style.display = (isGoogleUser || isLocalUser) ? 'block' : 'none';
                        }

                        if (microsoft365Section) {
                            microsoft365Section.style.display = (isMicrosoftUser || isLocalUser) ? 'block' : 'none';
                        }

                        if (gmailSmtpSection) {
                            // Gmail management is relevant for Google-connected or manually provisioned local users
                            gmailSmtpSection.style.display = (isGoogleUser || isLocalUser) ? 'block' : 'none';
                        }

                        if (isGoogleUser) {
                            console.log('Google OAuth user - showing Google Workspace + Gmail management');
                        } else if (isMicrosoftUser) {
                            console.log('Microsoft OAuth user - showing Microsoft 365 section (hiding Google Gmail blocks)');
                        } else {
                            console.log('Local auth user - showing both OAuth connectors for onboarding and Gmail management');
                        }

                        // Update Google OAuth UI status based on actual token presence
                        const oauthStatus = document.getElementById('oauthStatus');
                        const googleTokensExist = profile.google_oauth_connected || false;

                        if (oauthStatus) {
                            if (googleTokensExist) {
                                oauthStatus.innerHTML = 'Connected';
                                updateOAuthServicesStatus(true);
                                console.log('Google Workspace OAuth tokens found - services connected');

                                // Update Google Tools status to Enabled
                                const googleToolsStatus = document.getElementById('googleToolsStatus');
                                if (googleToolsStatus) {
                                    googleToolsStatus.textContent = 'Enabled';
                                    googleToolsStatus.style.background = 'var(--success-bg)';
                                    googleToolsStatus.style.color = 'var(--success-text)';
                                }
                            } else {
                                oauthStatus.innerHTML = ' Not connected';
                                updateOAuthServicesStatus(false);
                                console.log('[WARN] No Google OAuth tokens - services disconnected');

                                // Update Google Tools status to Disabled
                                const googleToolsStatus = document.getElementById('googleToolsStatus');
                                if (googleToolsStatus) {
                                    googleToolsStatus.textContent = 'Disabled';
                                    googleToolsStatus.style.background = 'var(--error-bg)';
                                    googleToolsStatus.style.color = 'var(--error-text)';
                                }
                            }
                        }

                        // Update Microsoft 365 OAuth status based on actual token presence
                        const microsoft365Status = document.getElementById('microsoft365Status');
                        const microsoftTokensExist = profile.microsoft_oauth_connected || false;

                        if (microsoft365Status) {
                            if (microsoftTokensExist) {
                                microsoft365Status.innerHTML = 'Connected';
                                updateMicrosoft365ServicesStatus(true);
                                console.log('Microsoft 365 OAuth tokens found - services connected');

                                // Update Microsoft Tools status to Enabled
                                const microsoftToolsStatus = document.getElementById('microsoftToolsStatus');
                                if (microsoftToolsStatus) {
                                    microsoftToolsStatus.textContent = 'Enabled';
                                    microsoftToolsStatus.style.background = 'var(--success-bg)';
                                    microsoftToolsStatus.style.color = 'var(--success-text)';
                                }
                            } else {
                                microsoft365Status.innerHTML = ' Not connected';
                                updateMicrosoft365ServicesStatus(false);
                                console.log('[WARN] No Microsoft 365 OAuth tokens - services disconnected');

                                // Update Microsoft Tools status to Disabled
                                const microsoftToolsStatus = document.getElementById('microsoftToolsStatus');
                                if (microsoftToolsStatus) {
                                    microsoftToolsStatus.textContent = 'Disabled';
                                    microsoftToolsStatus.style.background = 'var(--error-bg)';
                                    microsoftToolsStatus.style.color = 'var(--error-text)';
                                }
                            }
                        }

                        // Show profile container
                        const profileContainer = document.getElementById('userProfileContainer');
                        if (profileContainer) {
                            // Use flex so avatar + name align properly regardless of platform
                            profileContainer.style.display = 'flex';
                            console.log('Profile button displayed');
                            console.log('[SEARCH] Profile container visibility:', window.getComputedStyle(profileContainer).display);
                        } else {
                            console.error(' Profile container element not found!');
                        }

                        // Load additional Microsoft profile data if Microsoft user with tokens
                        if (isMicrosoftUser && microsoftTokensExist) {
                            loadMicrosoft365Profile();
                        }

                        // Debug: Check if platform sections are visible
                        console.log('[SEARCH] Google Workspace section display:', googleWorkspaceSection ? window.getComputedStyle(googleWorkspaceSection).display : 'NOT FOUND');
                        console.log('[SEARCH] Microsoft 365 section display:', microsoft365Section ? window.getComputedStyle(microsoft365Section).display : 'NOT FOUND');
                        console.log('[SEARCH] Gmail SMTP section display:', gmailSmtpSection ? window.getComputedStyle(gmailSmtpSection).display : 'NOT FOUND');
                    } else {
                        console.error(' Profile API returned success=false');
                    }

                } catch (error) {
                    console.error(' Failed to load user profile:', error);
                    console.error('Error details:', error.message);

                    // Fallback: Show profile button with basic user info from UserAuth
                    if (UserAuth.user) {
                        console.log('[WARN] Using fallback user data from UserAuth');
                        const userNameEl = document.getElementById('userName');
                        const dropdownNameEl = document.getElementById('dropdownUserName');
                        const dropdownEmailEl = document.getElementById('dropdownUserEmail');

                        if (userNameEl) userNameEl.textContent = UserAuth.user.username || 'User';
                        if (dropdownNameEl) dropdownNameEl.textContent = UserAuth.user.username || 'User';
                        if (dropdownEmailEl) dropdownEmailEl.textContent = UserAuth.user.email || 'No email';

                        const profileContainer = document.getElementById('userProfileContainer');
                        if (profileContainer) {
                            profileContainer.style.display = 'flex';
                            console.log('Profile button displayed (fallback mode)');
                        }
                    }
                } finally {
                    // Safety: ensure profile container never stays hidden due to intermediate errors
                    const profileContainer = document.getElementById('userProfileContainer');
                    if (profileContainer && profileContainer.style.display === 'none') {
                        profileContainer.style.display = 'flex';
                        console.log('[WARN] Profile container forced visible in finally block');
                    }
                }
            }  // CLOSING BRACE FOR loadUserProfile() function

            /**
             * Trigger full re-authentication flow
             * Clears existing OAuth tokens and restarts OAuth flow
             */
            async function triggerReauthentication() {
                console.log(' [REAUTH] Starting re-authentication flow...');

                // Debug: Log full user profile
                console.log(' [REAUTH] Current user profile:', JSON.stringify(UserAuth.user, null, 2));

                try {
                    // 1. Show confirmation dialog
                    UIComponents.showConfirmation({
                        title: 'Re-authentication Required',
                        message: 'This will:\n• Sign you out of your current session\n• Clear all OAuth tokens\n• Redirect you to Google/Microsoft login\n\nContinue?',
                        variant: 'warning',
                        confirmLabel: 'Continue',
                        cancelLabel: 'Cancel',
                        onConfirm: async () => {
                            await this.executeReauth();
                        },
                        onCancel: () => {
                            console.log('[ERROR] [REAUTH] User cancelled re-authentication');
                        }
                    });
                } catch (error) {
                    console.error('[ERROR] [REAUTH] Error showing confirmation:', error);
                }
            }

            async function executeReauth() {
                try {
                    // 2. Get user's authentication platform
                    const profile = UserAuth.user;

                    // Smart detection: Check multiple indicators
                    let authPlatform = profile?.auth_platform;

                    // Fallback 1: Check if user email is Microsoft domain
                    if (!authPlatform && profile?.email) {
                        if (profile.email.includes('@minivetguide.onmicrosoft.com') ||
                            profile.email.includes('.onmicrosoft.com') ||
                            profile.email.includes('@outlook.com') ||
                            profile.email.includes('@hotmail.com') ||
                            profile.email.includes('@live.com')) {
                            authPlatform = 'microsoft';
                            console.log('[SEARCH] [REAUTH] Detected Microsoft from email domain');
                        }
                    }

                    // Fallback 2: Check OAuth connection flags
                    if (!authPlatform) {
                        if (profile?.microsoft_oauth_connected) {
                            authPlatform = 'microsoft';
                            console.log('[SEARCH] [REAUTH] Detected Microsoft from oauth_connected flag');
                        } else if (profile?.google_oauth_connected) {
                            authPlatform = 'google';
                            console.log('[SEARCH] [REAUTH] Detected Google from oauth_connected flag');
                        }
                    }

                    // Fallback 3: Default to google
                    if (!authPlatform) {
                        authPlatform = 'google';
                        console.log('[WARN] [REAUTH] No platform detected, defaulting to Google');
                    }

                    console.log(` [REAUTH] Auth platform: ${authPlatform}`);

                    // 3. Call backend to revoke tokens
                    console.log('�� [REAUTH] Revoking existing tokens...');
                    const revokeResponse = await fetch(`${API_BASE_URL}/api/auth/revoke-tokens`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${UserAuth.token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            platform: authPlatform
                        })
                    });

                    const revokeData = await revokeResponse.json();
                    console.log(' [REAUTH] Revoke response:', revokeData);

                    // 4. Clear local storage
                    console.log('[CLEAN] [REAUTH] Clearing local storage...');
                    localStorage.removeItem('auth_token');
                    localStorage.removeItem('userProfile');
                    UserAuth.token = null;
                    UserAuth.user = null;
                    window.currentUserId = undefined; // Clear global user ID on logout

                    // 5. Show loading state
                    const reauthBtn = document.getElementById('reauthBtn');
                    if (reauthBtn) {
                        reauthBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Redirecting...</span>';
                        reauthBtn.disabled = true;
                    }

                    // 6. Redirect to OAuth flow
                    console.log(' [REAUTH] Redirecting to OAuth flow...');

                    if (authPlatform === 'google') {
                        // Google OAuth flow with forced consent
                        window.location.href = `${API_BASE_URL}/api/auth/google/login?force_consent=true`;
                    } else if (authPlatform === 'microsoft') {
                        // Microsoft OAuth flow with forced consent
                        window.location.href = `${API_BASE_URL}/api/auth/microsoft/login?force_consent=true`;
                    } else {
                        // Fallback to login page
                        window.location.href = '/login.html';
                    }

                } catch (error) {
                    console.error('[ERROR] [REAUTH] Re-authentication failed:', error);
                    alert('[ERROR] Re-authentication failed: ' + error.message);

                    // Reset button state
                    const reauthBtn = document.getElementById('reauthBtn');
                    if (reauthBtn) {
                        reauthBtn.innerHTML = '<i class="fas fa-sync-alt"></i> <span>Re-authenticate Account</span>';
                        reauthBtn.disabled = false;
                    }
                }
            }

            // Toggle OAuth services details
            function toggleOAuthDetails() {
                const detailsEl = document.getElementById('oauthDetails');
                const arrowEl = document.getElementById('oauthArrow');

                if (detailsEl && arrowEl) {
                    const isVisible = detailsEl.style.display !== 'none';
                    detailsEl.style.display = isVisible ? 'none' : 'block';
                    arrowEl.style.transform = isVisible ? 'rotate(0deg)' : 'rotate(180deg)';
                    arrowEl.style.transition = 'transform 0.2s ease';
                    console.log(' OAuth details toggled:', isVisible ? 'CLOSED' : 'OPEN');
                }
            }

            // Toggle Gmail accounts details
            function toggleGmailDetails() {
                const detailsEl = document.getElementById('gmailDetails');
                const arrowEl = document.getElementById('gmailArrow');

                if (detailsEl && arrowEl) {
                    const isVisible = detailsEl.style.display !== 'none';
                    detailsEl.style.display = isVisible ? 'none' : 'block';
                    arrowEl.style.transform = isVisible ? 'rotate(0deg)' : 'rotate(180deg)';
                    arrowEl.style.transition = 'transform 0.2s ease';
                    console.log(' Gmail details toggled:', isVisible ? 'CLOSED' : 'OPEN');
                }
            }

            // Update OAuth service statuses
            function updateOAuthServicesStatus(connected) {
                const services = ['gmail', 'calendar', 'tasks', 'forms', 'docs', 'sheets', 'slides', 'drive'];
                const statusIcon = connected ? '' : '';
                const statusColor = connected ? 'var(--success-color, #22c55e)' : 'var(--text-muted)';

                services.forEach(service => {
                    const serviceEl = document.getElementById(`oauth-${service}`);
                    if (serviceEl) {
                        const statusSpan = serviceEl.querySelector('.service-status');
                        if (statusSpan) {
                            statusSpan.textContent = statusIcon;
                            statusSpan.style.color = statusColor;
                        }
                    }
                });

                console.log(` Updated OAuth services: ${connected ? 'CONNECTED' : 'DISCONNECTED'}`);
            }

            // Connect OAuth handler
            function connectOAuth() {
                console.log(' Starting OAuth connection...');
                window.location.href = `${API_BASE_URL}/api/oauth/workspace/start?email=${UserAuth.user?.email || ''}`;
            }

            // Add Gmail account handler
            function addGmailAccount() {
                console.log(' Adding Gmail account...');
                alert('Add Gmail Account\n\nThis will open the Gmail authorization flow.\n\nComing soon!');
                // TODO: Implement Gmail-specific OAuth flow
            }

            // ==================== MICROSOFT 365 OAUTH UI ====================

            // Toggle Microsoft 365 OAuth details
            function toggleMicrosoft365Details() {
                const detailsEl = document.getElementById('microsoft365Details');
                const arrowEl = document.getElementById('microsoft365Arrow');

                if (detailsEl && arrowEl) {
                    const isVisible = detailsEl.style.display !== 'none';
                    detailsEl.style.display = isVisible ? 'none' : 'block';
                    arrowEl.style.transform = isVisible ? 'rotate(0deg)' : 'rotate(180deg)';
                    arrowEl.style.transition = 'transform 0.2s ease';
                    console.log(' Microsoft 365 details toggled:', isVisible ? 'CLOSED' : 'OPEN');
                }
            }

            // Update Microsoft 365 service statuses
            function updateMicrosoft365ServicesStatus(connected) {
                const services = ['outlook', 'calendar', 'onedrive', 'sharepoint', 'teams', 'onenote', 'todo'];
                const statusIcon = connected ? '' : '';
                const statusColor = connected ? 'var(--success-color, #22c55e)' : 'var(--text-muted)';

                services.forEach(service => {
                    const serviceEl = document.getElementById(`microsoft365-${service}`);
                    if (serviceEl) {
                        const statusSpan = serviceEl.querySelector('.service-status');
                        if (statusSpan) {
                            statusSpan.textContent = statusIcon;
                            statusSpan.style.color = statusColor;
                        }
                    }
                });

                console.log(` Updated Microsoft 365 services: ${connected ? 'CONNECTED' : 'DISCONNECTED'}`);
            }

            // Connect Microsoft 365 handler
            function connectMicrosoft365() {
                console.log(' Starting Microsoft 365 OAuth connection...');
                window.location.href = `${API_BASE_URL}/api/auth/microsoft/login`;
            }

            // Load Microsoft 365 profile from backend status endpoint
            async function loadMicrosoft365Profile() {
                console.log(' Loading Microsoft 365 profile...');

                try {
                    const response = await fetch(`${API_BASE_URL}/api/auth/microsoft/status`, {
                        headers: {
                            'Authorization': `Bearer ${UserAuth.token}`
                        }
                    });

                    console.log(' Microsoft status API response:', response.status);

                    if (!response.ok) {
                        console.error(' Failed to fetch Microsoft status:', response.status);
                        return;
                    }

                    const data = await response.json();
                    console.log('Microsoft status data:', data);

                    if (data.success && data.connected) {
                        const displayName = data.display_name || 'Microsoft User';
                        const email = data.microsoft_email || '';
                        const microsoftId = data.microsoft_id || '';

                        // Update Microsoft 365 status section in dropdown
                        const statusEl = document.getElementById('microsoft365Status');
                        if (statusEl) {
                            statusEl.innerHTML = `
                            <div style="display: flex; flex-direction: column; gap: 2px;">
                                <span style="color: var(--success-color, #22c55e);">${displayName}</span>
                                ${email ? `<span style="font-size: 11px; color: var(--text-muted);">${email}</span>` : ''}
                            </div>
                        `;
                        }

                        // Mark all services as connected
                        updateMicrosoft365ServicesStatus(true);

                        console.log('Microsoft 365 profile loaded:', { displayName, email, microsoftId });
                    } else {
                        console.log('[WARN] Microsoft 365 not connected');
                        updateMicrosoft365ServicesStatus(false);
                    }

                } catch (error) {
                    console.error(' Failed to load Microsoft 365 profile:', error);
                }
            }

            // Profile menu actions (legacy - kept for compatibility)
            function showOAuthStatus() {
                toggleOAuthDetails();
            }

            function showGmailAccounts() {
                toggleGmailDetails();
            }

            function showAccountSettings() {
                // Load saved settings or defaults
                loadAccountSettings();

                // Load user memories
                refreshMemories();

                // Load user preferences (tags)
                loadUserPreferences();

                // Show modal
                const modal = document.getElementById('account-settings-modal');
                if (modal) {
                    modal.style.display = 'flex';

                    // Expand all sections by default - show content divs
                    const sectionContents = modal.querySelectorAll('.settings-section-content');
                    sectionContents.forEach(content => {
                        content.style.display = 'block';
                    });

                    // Update toggle icons to show expanded state
                    const toggleIcons = modal.querySelectorAll('.settings-section-toggle i');
                    toggleIcons.forEach(icon => {
                        icon.classList.remove('fa-chevron-down');
                        icon.classList.add('fa-chevron-up');
                    });
                }

                // Close dropdown after clicking
                const userDropdown = document.querySelector('.user-dropdown-menu');
                if (userDropdown) {
                    userDropdown.classList.remove('active');
                    document.querySelector('.user-profile-btn').classList.remove('active');
                }
            }

            function closeAccountSettings() {
                const modal = document.getElementById('account-settings-modal');
                if (modal) {
                    modal.style.display = 'none';
                }
            }

            function saveAndCloseSettings() {
                try {
                    console.log('saveAndCloseSettings() called');
                    saveSettings();
                    closeAccountSettings();
                } catch (error) {
                    console.error('Error in saveAndCloseSettings():', error);
                    showNotification('Error saving settings: ' + error.message, 'error', 4000);
                }
            }

            function toggleSettingsSection(headerElement) {
                const section = headerElement.closest('.settings-section');
                if (section) {
                    section.classList.toggle('collapsed');
                }
            }

            // Default settings configuration
            const DEFAULT_SETTINGS = {
                model: 'claude-sonnet-4-5-20250929',
                temperature: 1.0,
                topP: 1.0,
                enableThinking: false,
                maxRounds: 20,
                roundTimeout: 30,
                enableStreaming: true,
                maxTokens: 16000,
                thinkingBudget: 10000
            };

            const SETTINGS_STORAGE_KEY = 'accountSettings';

            function loadAccountSettings() {
                // Try to load from localStorage, fallback to defaults
                const stored = localStorage.getItem(SETTINGS_STORAGE_KEY);
                const settings = stored ? JSON.parse(stored) : DEFAULT_SETTINGS;

                // Update UI with loaded settings - Model Options
                document.getElementById('modelSelect').value = settings.model || DEFAULT_SETTINGS.model;
                document.getElementById('temperature').value = settings.temperature || DEFAULT_SETTINGS.temperature;
                document.getElementById('tempValue').textContent = settings.temperature || DEFAULT_SETTINGS.temperature;
                document.getElementById('topP').value = settings.topP || DEFAULT_SETTINGS.topP;
                document.getElementById('toppValue').textContent = settings.topP || DEFAULT_SETTINGS.topP;
                document.getElementById('enableThinking').checked = settings.enableThinking || false;

                // Update UI - Round Parameters
                document.getElementById('maxRounds').value = settings.maxRounds || DEFAULT_SETTINGS.maxRounds;
                document.getElementById('roundsValue').textContent = settings.maxRounds || DEFAULT_SETTINGS.maxRounds;
                document.getElementById('roundTimeout').value = settings.roundTimeout || DEFAULT_SETTINGS.roundTimeout;
                document.getElementById('timeoutValue').textContent = settings.roundTimeout || DEFAULT_SETTINGS.roundTimeout;
                document.getElementById('enableStreaming').checked = settings.enableStreaming !== false;

                // Update UI - Token Parameters
                document.getElementById('maxTokens').value = settings.maxTokens || DEFAULT_SETTINGS.maxTokens;
                document.getElementById('tokensValue').textContent = settings.maxTokens || DEFAULT_SETTINGS.maxTokens;
                document.getElementById('thinkingBudgetSlider').value = settings.thinkingBudget || DEFAULT_SETTINGS.thinkingBudget;
                document.getElementById('thinkingValue').textContent = settings.thinkingBudget || DEFAULT_SETTINGS.thinkingBudget;

                // Update UI - Personalisation Settings (NEW)
                if (document.getElementById('userNickname')) {
                    document.getElementById('userNickname').value = settings.nickname || '';
                }
                if (document.getElementById('communicationStyle')) {
                    document.getElementById('communicationStyle').value = settings.communicationStyle || 'professional';
                }
                if (document.querySelector('input[name="detailLevel"]')) {
                    const detailLevelRadio = document.querySelector(`input[name="detailLevel"][value="${settings.detailLevel || 'standard'}"]`);
                    if (detailLevelRadio) {
                        detailLevelRadio.checked = true;
                    }
                }
                if (document.getElementById('authPlatform')) {
                    document.getElementById('authPlatform').value = settings.authPlatform || 'auto';
                }

                // Update UI - Location & Timezone (NEW)
                if (document.getElementById('useManualLocation')) {
                    document.getElementById('useManualLocation').checked = settings.useManualLocation || false;
                    document.getElementById('manualLocation').disabled = !settings.useManualLocation;
                }
                if (document.getElementById('useManualTimezone')) {
                    document.getElementById('useManualTimezone').checked = settings.useManualTimezone || false;
                    document.getElementById('manualTimezone').disabled = !settings.useManualTimezone;
                }
                if (document.getElementById('manualLocation')) {
                    document.getElementById('manualLocation').value = settings.manualLocation || '';
                }
                if (document.getElementById('manualTimezone')) {
                    document.getElementById('manualTimezone').value = settings.manualTimezone || '';
                }

                // Load and display detected geolocation
                if (document.getElementById('detectedLocation')) {
                    detectAndDisplayGeolocation();
                }

                // Enable/disable thinking budget slider based on extended thinking checkbox
                const thinkingBudgetSlider = document.getElementById('thinkingBudgetSlider');
                if (thinkingBudgetSlider) {
                    thinkingBudgetSlider.disabled = !document.getElementById('enableThinking').checked;
                }
            }

            function saveSettings() {
                try {
                    console.log('saveSettings() called');

                    // Get current values from UI with error checking
                    const modelSelect = document.getElementById('modelSelect');
                    const temperature = document.getElementById('temperature');
                    const topP = document.getElementById('topP');
                    const enableThinking = document.getElementById('enableThinking');
                    const maxRounds = document.getElementById('maxRounds');
                    const roundTimeout = document.getElementById('roundTimeout');
                    const enableStreaming = document.getElementById('enableStreaming');
                    const maxTokens = document.getElementById('maxTokens');
                    const thinkingBudget = document.getElementById('thinkingBudget');
                    const userNickname = document.getElementById('userNickname');
                    const communicationStyle = document.getElementById('communicationStyle');
                    const detailLevelRadio = document.querySelector('input[name="detailLevel"]:checked');
                    const authPlatform = document.getElementById('authPlatform');
                    const useManualLocation = document.getElementById('useManualLocation');
                    const useManualTimezone = document.getElementById('useManualTimezone');
                    const manualLocation = document.getElementById('manualLocation');
                    const manualTimezone = document.getElementById('manualTimezone');

                    const settings = {
                        // Model Options
                        model: modelSelect ? modelSelect.value : 'claude-sonnet-4-5-20250929',
                        temperature: temperature ? parseFloat(temperature.value) : 1.0,
                        topP: topP ? parseFloat(topP.value) : 1.0,
                        enableThinking: enableThinking ? enableThinking.checked : false,

                        // Round Parameters
                        maxRounds: maxRounds ? parseInt(maxRounds.value) : 10,
                        roundTimeout: roundTimeout ? parseInt(roundTimeout.value) : 60,
                        enableStreaming: enableStreaming ? enableStreaming.checked : true,

                        // Token Parameters
                        maxTokens: maxTokens ? parseInt(maxTokens.value) : 4096,
                        thinkingBudget: thinkingBudget ? parseInt(thinkingBudget.value) : 10000,

                        // Personalisation Settings
                        nickname: userNickname ? userNickname.value : '',
                        communicationStyle: communicationStyle ? communicationStyle.value : 'professional',
                        detailLevel: detailLevelRadio ? detailLevelRadio.value : 'standard',
                        authPlatform: authPlatform ? authPlatform.value : 'auto',

                        // Location & Timezone
                        useManualLocation: useManualLocation ? useManualLocation.checked : false,
                        useManualTimezone: useManualTimezone ? useManualTimezone.checked : false,
                        manualLocation: manualLocation ? manualLocation.value : '',
                        manualTimezone: manualTimezone ? manualTimezone.value : '',

                        // Metadata
                        lastUpdated: new Date().toISOString()
                    };

                    console.log('Settings object created:', settings);

                    // Save to localStorage
                    localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(settings));
                    console.log('Saved to localStorage');

                    // Save to backend if user is authenticated
                    if (window.currentUserId) {
                        console.log('Saving ALL settings to backend for user:', window.currentUserId);
                        saveAllSettingsToBackend(window.currentUserId, settings);
                    } else {
                        console.log('No currentUserId - skipping backend save');
                    }

                    // Show notification
                    showNotification('Account Settings Saved Successfully!', 'success', 3000);

                    console.log('Account settings saved successfully:', settings);
                    return settings;
                } catch (error) {
                    console.error('Error in saveSettings():', error);
                    showNotification('Failed to save settings: ' + error.message, 'error', 4000);
                    throw error;
                }
            }

            // UNIFIED: Save ALL settings to backend database in one call
            async function saveAllSettingsToBackend(userId, settings) {
                try {
                    const backendUrl = window.API_BASE_URL || 'http://localhost:5001';

                    // Get detected geolocation data from UI
                    const detectedLocation = document.getElementById('detectedLocation').textContent;
                    const detectedIP = document.getElementById('detectedIP').textContent;
                    const detectedTimezone = document.getElementById('detectedTimezone').textContent;

                    // Parse detected location into city and country
                    let detectedCity = '';
                    let detectedCountry = '';
                    if (detectedLocation && detectedLocation !== 'Detecting...' && detectedLocation !== 'Unable to detect') {
                        const parts = detectedLocation.split(', ');
                        if (parts.length >= 2) {
                            detectedCity = parts[0];
                            detectedCountry = parts[1];
                        } else {
                            detectedCountry = parts[0];
                        }
                    }

                    // Build comprehensive payload with ALL fields from the modal
                    const payload = {
                        user_id: userId,

                        // Personalisation Settings
                        nickname: settings.nickname || '',
                        communication_style: settings.communicationStyle || 'professional',
                        detail_level: settings.detailLevel || 'standard',
                        auth_platform: settings.authPlatform || 'auto',

                        // Location & Timezone
                        use_manual_location: settings.useManualLocation || false,
                        use_manual_timezone: settings.useManualTimezone || false,
                        manual_location_override: settings.manualLocation || '',
                        manual_timezone_override: settings.manualTimezone || '',
                        detected_country: detectedCountry,
                        detected_city: detectedCity,
                        detected_timezone: detectedTimezone,
                        detected_ip_address: detectedIP,

                        // User Preferences (from tag system)
                        preferred_tools: JSON.stringify(preferredTools || []),
                        custom_preferences: JSON.stringify(customPreferences || [])
                    };

                    console.log('Sending comprehensive payload to backend:', payload);

                    const response = await fetch(`${backendUrl}/api/user/preferences`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                        },
                        body: JSON.stringify(payload)
                    });

                    if (!response.ok) {
                        const errorText = await response.text();
                        console.error('Backend save failed:', response.statusText, errorText);
                        showNotification('Failed to save to backend: ' + response.statusText, 'warning', 3000);
                    } else {
                        const data = await response.json();
                        console.log('All settings saved to backend successfully:', data);
                    }
                } catch (error) {
                    console.error('Error saving settings to backend:', error);
                    showNotification('Warning: Settings saved locally but backend sync failed', 'warning', 3000);
                }
            }

            // NEW: Detect geolocation from IP address
            async function detectAndDisplayGeolocation() {
                try {
                    // Try to get geolocation from backend first
                    const backendUrl = window.API_BASE_URL || 'http://localhost:5001';
                    const response = await fetch(`${backendUrl}/api/geolocation/detect`, {
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                        }
                    });

                    if (response.ok) {
                        const data = await response.json();
                        displayGeolocationData(data);
                    } else {
                        // Fallback to ipapi service
                        const ipResponse = await fetch('https://ipapi.co/json/');
                        const ipData = await ipResponse.json();
                        displayGeolocationData({
                            country: ipData.country_name,
                            city: ipData.city,
                            timezone: ipData.timezone,
                            ip_address: ipData.ip
                        });
                    }
                } catch (error) {
                    console.warn('Geolocation detection failed:', error);
                    document.getElementById('detectedLocation').textContent = 'Unable to detect';
                    document.getElementById('detectedTimezone').textContent = 'Unable to detect';
                }
            }

            function displayGeolocationData(data) {
                const location = data.city && data.country ? `${data.city}, ${data.country}` : data.country || 'Unknown';
                const timezone = data.timezone || 'Unknown';
                const ip = data.ip_address || 'Unknown';

                document.getElementById('detectedLocation').textContent = location;
                document.getElementById('detectedTimezone').textContent = timezone;
                document.getElementById('detectedIP').textContent = ip;

                // Update current time based on timezone
                updateCurrentTime(timezone);
            }

            function updateCurrentTime(timezone) {
                try {
                    // CRITICAL FIX: Don't attempt to use 'Unknown' or invalid timezones
                    if (!timezone || timezone === 'Unknown' || timezone.trim() === '') {
                        document.getElementById('currentTime').textContent = 'Timezone not set';
                        return;
                    }

                    const now = new Date();
                    const timeString = now.toLocaleString('en-US', { timeZone: timezone, hour12: true });
                    document.getElementById('currentTime').textContent = timeString;
                } catch (error) {
                    console.warn('Failed to display time:', error);
                    document.getElementById('currentTime').textContent = 'Invalid timezone';
                }
            }

            // NEW: Toggle manual location override
            function toggleManualLocation() {
                const checkbox = document.getElementById('useManualLocation');
                const input = document.getElementById('manualLocation');
                input.disabled = !checkbox.checked;
                if (checkbox.checked) {
                    input.focus();
                }
                saveSettings();
            }

            // NEW: Toggle manual timezone override
            function toggleManualTimezone() {
                const checkbox = document.getElementById('useManualTimezone');
                const select = document.getElementById('manualTimezone');
                select.disabled = !checkbox.checked;
                if (checkbox.checked) {
                    select.focus();
                }
                saveSettings();
            }

            function resetAccountSettings() {
                UIComponents.showConfirmation({
                    title: 'Reset Settings?',
                    message: 'This will reset all settings to defaults. This action cannot be undone.',
                    variant: 'danger',
                    confirmLabel: 'Reset',
                    cancelLabel: 'Cancel',
                    onConfirm: () => {
                        localStorage.removeItem(SETTINGS_STORAGE_KEY);
                        loadAccountSettings();
                        showSettingsSaved('Settings reset to defaults');
                    }
                });
            }

            function showSettingsSaved(message = 'Settings saved!') {
                // Show brief toast notification
                const toast = document.createElement('div');
                toast.style.cssText = `
                                                                                                                                    position: fixed;
                                                                                                                                    bottom: 20px;
                                                                                                                                    right: 20px;
                                                                                                                                    background: var(--accent-primary);
                                                                                                                                    color: white;
                                                                                                                                    padding: 12px 20px;
                                                                                                                                    border-radius: 6px;
                                                                                                                                    font-size: 14px;
                                                                                                                                    z-index: 10001;
                                                                                                                                    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
                                                                                                                                    animation: slideIn 0.3s ease;
                                                                                                                                    `;
                toast.textContent = message;
                document.body.appendChild(toast);

                setTimeout(() => {
                    toast.style.opacity = '0';
                    toast.style.transition = 'opacity 0.3s ease';
                    setTimeout(() => toast.remove(), 300);
                }, 2000);
            }

            function getAccountSettings() {
                // Get current settings (for use by AI agent)
                const stored = localStorage.getItem(SETTINGS_STORAGE_KEY);
                return stored ? JSON.parse(stored) : DEFAULT_SETTINGS;
            }

            // When extended thinking is toggled, enable/disable the thinking budget slider
            document.addEventListener('DOMContentLoaded', function () {
                const enableThinking = document.getElementById('enableThinking');
                if (enableThinking) {
                    enableThinking.addEventListener('change', function () {
                        const thinkingBudgetSlider = document.getElementById('thinkingBudgetSlider');
                        if (thinkingBudgetSlider) {
                            thinkingBudgetSlider.disabled = !this.checked;
                        }
                    });
                }
            });

            function showNotifications() {
                // TODO: Implement notifications panel
                alert('Notification Preferences\n\nThis will open notification settings.\n\nComing soon!');
            }

            function showAppearance() {
                // Already has theme toggle, could expand
                const currentTheme = document.body.classList.contains('dark-theme') ? 'Dark' : 'Light';
                alert(`Appearance Settings\n\nCurrent theme: ${currentTheme}\n\nUse the moon/sun icon in the header to toggle themes.\n\nMore appearance options coming soon!`);
            }

            function showSecurity() {
                // TODO: Implement security panel
                alert('Security Settings\n\n• Change password\n• Two-factor authentication\n• Active sessions\n• Login history\n\nComing soon!');
            }

            function showHelp() {
                window.open('https://github.com/gerardovsa/AI_agents/blob/main/README.md', '_blank');
            }

            function showKeyboardShortcuts() {
                alert('Keyboard Shortcuts\n\n' +
                    'Ctrl + K - Search platforms\n' +
                    'Ctrl + / - Show shortcuts\n' +
                    'Ctrl + B - Toggle sidebar\n' +
                    'Ctrl + Enter - Send AI message\n' +
                    'Esc - Close dropdowns/modals');
            }

            // ==================== MEMORY MANAGEMENT FUNCTIONS ====================

            async function loadUserMemories() {
                try {
                    const backendUrl = window.API_BASE_URL || 'http://localhost:5001';
                    const response = await fetch(`${backendUrl}/api/user/preferences`, {
                        method: 'GET',
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                        }
                    });

                    if (!response.ok) {
                        console.error('Failed to load user preferences');
                        return [];
                    }

                    const data = await response.json();
                    const memoriesJSON = data.data.ai_memories || '[]';
                    const memories = JSON.parse(memoriesJSON);

                    // Update memory count badge
                    const memoryCountBadge = document.getElementById('memoryCount');
                    if (memoryCountBadge) {
                        memoryCountBadge.textContent = memories.length;
                    }

                    return memories;
                } catch (error) {
                    console.error('Error loading memories:', error);
                    return [];
                }
            }

            async function refreshMemories() {
                try {
                    const memories = await loadUserMemories();
                    renderMemories(memories);
                } catch (error) {
                    console.error('Error refreshing memories:', error);
                }
            }

            function renderMemories(memories) {
                const container = document.getElementById('memoriesContainer');
                if (!container) return;

                if (!memories || memories.length === 0) {
                    container.innerHTML = `
                    <div style="text-align: center; padding: 24px; color: var(--text-muted);">
                        <i class="fas fa-brain" style="font-size: 32px; margin-bottom: 12px; opacity: 0.5;"></i>
                        <p>No memories stored yet</p>
                        <small>Click "Add Memory" above to create your first memory</small>
                    </div>
                `;
                    return;
                }

                // Sort by created_at descending (newest first)
                memories.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

                // Render memory cards
                container.innerHTML = memories.map(memory => `
                                                                                                                                    <div class="memory-card" data-memory-id="${memory.id}" style="
                    background: var(--bg-tertiary);
                    border: 1px solid var(--border-default);
                    border-radius: 8px;
                    padding: 12px;
                    margin-bottom: 12px;
                ">
                                                                                                                                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                                                                                                                                            <div style="flex: 1;">
                                                                                                                                                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                                                                                                                                                    <span class="memory-category-badge" style="
                                    background: ${getCategoryColor(memory.category)};
                                    color: white;
                                    padding: 2px 8px;
                                    border-radius: 4px;
                                    font-size: 11px;
                                    font-weight: 600;
                                    text-transform: uppercase;
                                ">${memory.category}</span>
                                                                                                                                                    ${memory.tags && memory.tags.length > 0 ? memory.tags.map(tag => `
                                    <span style="
                                        background: var(--bg-hover);
                                        color: var(--text-secondary);
                                        padding: 2px 6px;
                                        border-radius: 3px;
                                        font-size: 10px;
                                    ">${tag}</span>
                                `).join('') : ''}
                                                                                                                                                </div>
                                                                                                                                                <p style="
                                margin: 0;
                                font-size: 14px;
                                color: var(--text-primary);
                                line-height: 1.4;
                            ">${escapeHtml(memory.content)}</p>
                                                                                                                                                <small style="
                                color: var(--text-muted);
                                font-size: 11px;
                                display: block;
                                margin-top: 6px;
                            ">
                                                                                                                                                    <i class="fas fa-clock"></i> ${formatMemoryDate(memory.created_at)}
                                                                                                                                                </small>
                                                                                                                                            </div>
                                                                                                                                            <div style="display: flex; gap: 4px;">
                                                                                                                                                <button onclick='showEditMemoryModal(${JSON.stringify(memory)})' style="
                                background: transparent;
                                border: none;
                                color: var(--text-muted);
                                cursor: pointer;
                                padding: 4px 8px;
                                border-radius: 4px;
                                transition: all 0.2s;
                            " onmouseover="this.style.background='rgba(59, 130, 246, 0.1)'; this.style.color='#3b82f6';"
                                                                                                                                                    onmouseout="this.style.background='transparent'; this.style.color='var(--text-muted)';"
                                                                                                                                                    title="Edit memory">
                                                                                                                                                    <i class="fas fa-edit"></i>
                                                                                                                                                </button>
                                                                                                                                                <button onclick="deleteMemory('${memory.id}')" style="
                                background: transparent;
                                border: none;
                                color: var(--text-muted);
                                cursor: pointer;
                                padding: 4px 8px;
                                border-radius: 4px;
                                transition: all 0.2s;
                            " onmouseover="this.style.background='rgba(239, 68, 68, 0.1)'; this.style.color='#ef4444';"
                                                                                                                                                    onmouseout="this.style.background='transparent'; this.style.color='var(--text-muted)';"
                                                                                                                                                    title="Delete memory">
                                                                                                                                                    <i class="fas fa-trash"></i>
                                                                                                                                                </button>
                                                                                                                                            </div>
                                                                                                                                        </div>
                                                                                                                                    </div>
                                                                                                                                    `).join('');
            }

            async function deleteMemory(memoryId) {
                UIComponents.showConfirmation({
                    title: 'Delete Memory?',
                    message: 'This memory will be permanently deleted. This action cannot be undone.',
                    variant: 'danger',
                    confirmLabel: 'Delete',
                    cancelLabel: 'Cancel',
                    onConfirm: async () => {
                        await executeDeleteMemory(memoryId);
                    }
                });
            }

            async function executeDeleteMemory(memoryId) {
                try {
                    const memories = await loadUserMemories();
                    const updatedMemories = memories.filter(m => m.id !== memoryId);

                    const backendUrl = window.API_BASE_URL || 'http://localhost:5001';
                    const response = await fetch(`${backendUrl}/api/user/preferences`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                        },
                        body: JSON.stringify({
                            ai_memories: JSON.stringify(updatedMemories)
                        })
                    });

                    if (!response.ok) {
                        throw new Error('Failed to delete memory');
                    }

                    // Refresh UI
                    await refreshMemories();
                    showToast('Memory deleted successfully');
                } catch (error) {
                    console.error('Error deleting memory:', error);
                    alert('Failed to delete memory. Please try again.');
                }
            }

            function getCategoryColor(category) {
                const colors = {
                    'preferences': '#8b5cf6',
                    'personal': '#3b82f6',
                    'work': '#10b981',
                    'health': '#ef4444',
                    'general': '#6b7280'
                };
                return colors[category] || colors.general;
            }

            function formatMemoryDate(isoString) {
                const date = new Date(isoString);
                const now = new Date();
                const diffMs = now - date;
                const diffMins = Math.floor(diffMs / 60000);
                const diffHours = Math.floor(diffMs / 3600000);
                const diffDays = Math.floor(diffMs / 86400000);

                if (diffMins < 1) return 'Just now';
                if (diffMins < 60) return `${diffMins}m ago`;
                if (diffHours < 24) return `${diffHours}h ago`;
                if (diffDays < 7) return `${diffDays}d ago`;

                return date.toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
                });
            }

            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }

            // Escape text for use in JavaScript strings (onclick handlers, etc.)
            function escapeJs(text) {
                if (!text) return '';
                return text
                    .replace(/\\/g, '\\\\')  // Escape backslashes first
                    .replace(/'/g, "\\'")     // Escape single quotes
                    .replace(/"/g, '\\"')     // Escape double quotes
                    .replace(/`/g, '\\`')     // Escape backticks (template literals)
                    .replace(/\$/g, '\\$')    // Escape dollar signs (template literal injection)
                    .replace(/\n/g, '\\n')    // Escape newlines
                    .replace(/\r/g, '\\r')    // Escape carriage returns
                    .replace(/\t/g, '\\t')    // Escape tabs
                    .replace(/\u2028/g, '\\u2028')  // Escape unicode line separator
                    .replace(/\u2029/g, '\\u2029'); // Escape unicode paragraph separator
            }

            // Safe wrapper for escapeJs with error handling
            function safeEscape(value) {
                if (value === null || value === undefined) return '';
                try {
                    return escapeJs(String(value));
                } catch (error) {
                    console.error('[ERROR] safeEscape failed:', error, 'value:', value);
                    return '';
                }
            }

            // Open dialog to add new agent column
            function openAddAgentDialog() {
                const agentName = prompt('Enter agent name (e.g., Delta-4):');
                if (agentName && agentName.trim()) {
                    console.log('[Multi-Agent] Adding new agent:', agentName);
                    // Create new agent column
                    const agentCount = document.querySelectorAll('.agent-column').length + 1;
                    const newAgentId = `agent-${agentCount}`;
                    const agentContainer = document.getElementById('agent-columns-container');
                    if (agentContainer) {
                        createAgentColumn(newAgentId, agentName.trim(), null, 'expanded');
                        showToast(`Agent ${agentName} added successfully`);
                    } else {
                        console.error('[Multi-Agent] Agent container not found');
                    }
                }
            }

            function showToast(message) {
                const toast = document.createElement('div');
                toast.style.cssText = `
                                                                                                                                    position: fixed;
                                                                                                                                    bottom: 20px;
                                                                                                                                    right: 20px;
                                                                                                                                    background: var(--accent-success);
                                                                                                                                    color: white;
                                                                                                                                    padding: 12px 20px;
                                                                                                                                    border-radius: 6px;
                                                                                                                                    font-size: 14px;
                                                                                                                                    z-index: 10001;
                                                                                                                                    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
                                                                                                                                    `;
                toast.textContent = message;
                document.body.appendChild(toast);

                setTimeout(() => {
                    toast.style.opacity = '0';
                    toast.style.transition = 'opacity 0.3s ease';
                    setTimeout(() => toast.remove(), 300);
                }, 2000);
            }

            // ==================== ADD/EDIT MEMORY FUNCTIONS ====================

            function showAddMemoryModal() {
                // Clear form for new memory
                document.getElementById('editMemoryId').value = '';
                document.getElementById('memoryContent').value = '';
                document.getElementById('memoryCategory').value = 'general';
                document.getElementById('memoryTags').value = '';
                document.getElementById('cancelMemoryBtn').style.display = 'none';
                // No modal to show - form is already visible in settings
            }

            function showEditMemoryModal(memory) {
                // Populate form with memory data for editing
                document.getElementById('editMemoryId').value = memory.id;
                document.getElementById('memoryContent').value = memory.content;
                document.getElementById('memoryCategory').value = memory.category;
                document.getElementById('memoryTags').value = memory.tags ? memory.tags.join(', ') : '';
                document.getElementById('cancelMemoryBtn').style.display = 'block';

                // Scroll to the form
                const memoryContent = document.getElementById('memoryContent');
                memoryContent.scrollIntoView({ behavior: 'smooth', block: 'center' });
                memoryContent.focus();
            }

            function cancelMemoryEdit() {
                // Clear the form and hide cancel button
                document.getElementById('editMemoryId').value = '';
                document.getElementById('memoryContent').value = '';
                document.getElementById('memoryCategory').value = 'general';
                document.getElementById('memoryTags').value = '';
                document.getElementById('cancelMemoryBtn').style.display = 'none';
            }

            function closeMemoryModal() {
                // Keep for backwards compatibility but does nothing now
                cancelMemoryEdit();
            }

            async function saveMemory() {
                const content = document.getElementById('memoryContent').value.trim();
                const category = document.getElementById('memoryCategory').value;
                const tagsInput = document.getElementById('memoryTags').value;
                const editId = document.getElementById('editMemoryId').value;

                if (!content) {
                    alert('Please enter memory content');
                    return;
                }

                const tags = tagsInput.split(',').map(t => t.trim()).filter(t => t.length > 0);

                try {
                    const memories = await loadUserMemories();

                    if (editId) {
                        // Edit existing memory
                        const index = memories.findIndex(m => m.id === editId);
                        if (index !== -1) {
                            memories[index] = {
                                ...memories[index],
                                content: content,
                                category: category,
                                tags: tags
                            };
                        }
                    } else {
                        // Add new memory
                        const newMemory = {
                            id: 'mem_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
                            content: content,
                            category: category,
                            tags: tags,
                            created_at: new Date().toISOString(),
                            relevance_score: 1.0
                        };
                        memories.unshift(newMemory);
                    }

                    // Save to backend
                    const backendUrl = window.API_BASE_URL || 'http://localhost:5001';
                    const response = await fetch(`${backendUrl}/api/user/preferences`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                        },
                        body: JSON.stringify({
                            ai_memories: JSON.stringify(memories)
                        })
                    });

                    if (!response.ok) {
                        throw new Error('Failed to save memory');
                    }

                    // Clear form and refresh
                    cancelMemoryEdit();
                    await refreshMemories();

                    // Show success notification
                    if (editId) {
                        showNotification('Memory updated successfully!', 'success', 3000);
                    } else {
                        showNotification('Memory added successfully!', 'success', 3000);
                    }
                } catch (error) {
                    console.error('Error saving memory:', error);
                    showNotification('Failed to save memory. Please try again.', 'error', 3000);
                }
            }

            // ==================== END ADD/EDIT MEMORY FUNCTIONS ====================

            // ==================== USER PREFERENCES TAG SYSTEM ====================

            let preferredTools = [];
            let customPreferences = [];

            function addPreferredTool() {
                const input = document.getElementById('newToolInput');
                const tool = input.value.trim();

                if (!tool) return;
                if (preferredTools.includes(tool)) {
                    alert('This tool is already in your preferences');
                    return;
                }

                preferredTools.push(tool);
                input.value = '';
                renderPreferredTools();
                savePreferencesToBackend();
            }

            function removePreferredTool(tool) {
                preferredTools = preferredTools.filter(t => t !== tool);
                renderPreferredTools();
                savePreferencesToBackend();
            }

            function renderPreferredTools() {
                const container = document.getElementById('preferredToolsContainer');

                // Ensure preferredTools is an array (defensive programming)
                if (!Array.isArray(preferredTools)) {
                    console.warn('preferredTools is not an array, resetting to empty array');
                    preferredTools = [];
                }

                if (preferredTools.length === 0) {
                    container.innerHTML = '<span style="color: var(--text-muted); font-size: 13px;">No tools added yet. Type a tool name and click Add.</span>';
                    updatePreferencesCount();
                    return;
                }

                container.innerHTML = preferredTools.map(tool => `
                                                                                                                                    <div style="
                    background: var(--accent-info);
                    color: white;
                    padding: 4px 10px;
                    border-radius: 16px;
                    font-size: 12px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    cursor: pointer;
                    transition: all 0.2s;
                " onclick="removePreferredTool('${tool.replace(/'/g, "\\'")}')"
                                                                                                                                    onmouseover="this.style.background='#dc3545'"
                   onmouseout="this.style.background='var(--accent-info)'">
                                                                                                                                    ${tool}
                                                                                                                                    <i class="fas fa-times" style="font-size: 10px;"></i>
                                                                                                                                </div>
                                                                                                                                    `).join('');

                updatePreferencesCount();
            }

            function addCustomPreference() {
                const input = document.getElementById('newPreferenceInput');
                const preference = input.value.trim();

                if (!preference) return;
                if (customPreferences.includes(preference)) {
                    alert('This preference is already saved');
                    return;
                }

                customPreferences.push(preference);
                input.value = '';
                renderCustomPreferences();
                savePreferencesToBackend();
            }

            function removeCustomPreference(preference) {
                customPreferences = customPreferences.filter(p => p !== preference);
                renderCustomPreferences();
                savePreferencesToBackend();
            }

            function renderCustomPreferences() {
                const container = document.getElementById('customPreferencesContainer');

                // Ensure customPreferences is an array (defensive programming)
                if (!Array.isArray(customPreferences)) {
                    console.warn('customPreferences is not an array, resetting to empty array');
                    customPreferences = [];
                }

                if (customPreferences.length === 0) {
                    container.innerHTML = '<span style="color: var(--text-muted); font-size: 13px;">No preferences added yet. Type a preference and click Add.</span>';
                    updatePreferencesCount();
                    return;
                }

                container.innerHTML = customPreferences.map(pref => `
                                                                                                                                    <div style="
                    background: var(--accent-primary);
                    color: white;
                    padding: 4px 10px;
                    border-radius: 16px;
                    font-size: 12px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    cursor: pointer;
                    transition: all 0.2s;
                " onclick="removeCustomPreference('${pref.replace(/'/g, "\\'")}')"
                                                                                                                                    onmouseover="this.style.background='#dc3545'"
                   onmouseout="this.style.background='var(--accent-primary)'">
                                                                                                                                    ${pref}
                                                                                                                                    <i class="fas fa-times" style="font-size: 10px;"></i>
                                                                                                                                </div>
                                                                                                                                `).join('');

                updatePreferencesCount();
            }

            function updatePreferencesCount() {
                const count = preferredTools.length + customPreferences.length;
                const badge = document.getElementById('preferencesCount');
                if (badge) {
                    badge.textContent = count;
                }
            }

            async function savePreferencesToBackend() {
                // This function is called when adding/removing preferred tools or custom preferences
                // We need to save ONLY the preferences fields, not trigger a full settings save
                try {
                    if (!window.currentUserId) {
                        console.warn('No user ID available, skipping backend save');
                        return;
                    }

                    const backendUrl = window.API_BASE_URL || 'http://localhost:5001';

                    // Get current geolocation data
                    const detectedLocation = document.getElementById('detectedLocation').textContent;
                    const detectedIP = document.getElementById('detectedIP').textContent;
                    const detectedTimezone = document.getElementById('detectedTimezone').textContent;

                    let detectedCity = '';
                    let detectedCountry = '';
                    if (detectedLocation && detectedLocation !== 'Detecting...' && detectedLocation !== 'Unable to detect') {
                        const parts = detectedLocation.split(', ');
                        if (parts.length >= 2) {
                            detectedCity = parts[0];
                            detectedCountry = parts[1];
                        } else {
                            detectedCountry = parts[0];
                        }
                    }

                    // Send only the preferences that changed
                    const response = await fetch(`${backendUrl}/api/user/preferences`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                        },
                        body: JSON.stringify({
                            user_id: window.currentUserId,
                            preferred_tools: JSON.stringify(preferredTools || []),
                            custom_preferences: JSON.stringify(customPreferences || []),
                            detected_country: detectedCountry,
                            detected_city: detectedCity,
                            detected_timezone: detectedTimezone,
                            detected_ip_address: detectedIP
                        })
                    });

                    if (!response.ok) {
                        throw new Error('Failed to save preferences');
                    }

                    console.log('Preferences saved to backend successfully');
                } catch (error) {
                    console.error('Error saving preferences:', error);
                    // Don't show notification for every tag add/remove
                }
            }

            async function loadUserPreferences() {
                try {
                    const backendUrl = window.API_BASE_URL || 'http://localhost:5001';
                    const response = await fetch(`${backendUrl}/api/user/preferences`, {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                        }
                    });

                    if (!response.ok) {
                        throw new Error('Failed to load preferences');
                    }

                    const result = await response.json();
                    const data = result.data || result;  // Handle both response formats

                    // Parse preferred tools
                    if (data.preferred_tools) {
                        try {
                            const parsed = JSON.parse(data.preferred_tools);
                            // Ensure it's an array, not null or other type
                            preferredTools = Array.isArray(parsed) ? parsed : [];
                        } catch (e) {
                            console.error('Failed to parse preferred_tools:', e);
                            preferredTools = [];
                        }
                    } else {
                        preferredTools = [];
                    }

                    // Parse custom preferences
                    if (data.custom_preferences) {
                        try {
                            const parsed = JSON.parse(data.custom_preferences);
                            // Ensure it's an array, not null or other type
                            customPreferences = Array.isArray(parsed) ? parsed : [];
                        } catch (e) {
                            console.error('Failed to parse custom_preferences:', e);
                            customPreferences = [];
                        }
                    } else {
                        customPreferences = [];
                    }

                    // CRITICAL FIX: Display IP-based geolocation data from backend
                    if (data.detected_country || data.detected_city || data.detected_timezone) {
                        console.log('Using stored IP-based geolocation data from backend');
                        displayGeolocationData({
                            country: data.detected_country || 'Unknown',
                            city: data.detected_city || '',
                            timezone: data.detected_timezone || 'Unknown',
                            ip_address: data.detected_ip_address || 'Unknown'
                        });
                    } else {
                        // No stored geolocation - trigger fresh detection
                        console.log('No stored geolocation found, detecting from IP...');
                        detectAndDisplayGeolocation();
                    }

                    renderPreferredTools();
                    renderCustomPreferences();
                } catch (error) {
                    console.error('Error loading preferences:', error);
                    renderPreferredTools();
                    renderCustomPreferences();
                    // Fallback to IP detection on error
                    detectAndDisplayGeolocation();
                }
            }

            // ==================== END USER PREFERENCES TAG SYSTEM ====================

            function reportBug() {
                window.open('https://github.com/gerardovsa/AI_agents/issues/new', '_blank');
            }

            // User menu (placeholder for future expansion)
            function showUserMenu() {
                // Legacy function - now using toggleUserMenu()
                toggleUserMenu();
            }

            // Override fetch to include auth token in all API requests
            const originalFetch = window.fetch;
            window.fetch = function (...args) {
                const [url, options = {}] = args;

                // Only add auth to API requests
                if (typeof url === 'string' && (url.includes('/api/') || url.includes('/agent/'))) {
                    options.headers = options.headers || {};

                    // Add auth token if available
                    if (UserAuth.token) {
                        if (typeof options.headers === 'object' && !(options.headers instanceof Headers)) {
                            options.headers['Authorization'] = `Bearer ${UserAuth.token}`;
                        } else if (options.headers instanceof Headers) {
                            options.headers.set('Authorization', `Bearer ${UserAuth.token}`);
                        }
                    }
                }

                return originalFetch.apply(this, [url, options]);
            };

            // Initialize authentication on page load
            // IMPORTANT: Handle OAuth callback token BEFORE initializing UserAuth
            async function initializeApp() {
                // Check for OAuth callback token in URL
                const urlParams = new URLSearchParams(window.location.search);
                const token = urlParams.get('token');
                const error = urlParams.get('error');

                if (error) {
                    console.error(' OAuth error:', error);
                    const errorDiv = document.getElementById('loginError');
                    if (errorDiv) {
                        errorDiv.textContent = `OAuth login failed: ${error}`;
                        errorDiv.classList.add('show');
                    }
                    // Clean URL
                    window.history.replaceState({}, document.title, window.location.pathname);
                } else if (token) {
                    console.log('OAuth successful, token received');

                    // Clear dev mode flag - real OAuth login succeeded
                    localStorage.removeItem('dev_mode_user');

                    // Store token
                    localStorage.setItem('authToken', token);
                    UserAuth.token = token;

                    // Load user profile first to detect auth_platform from backend
                    await loadUserProfile();

                    // Mark OAuth as connected based on backend's auth_platform
                    const userProfile = UserAuth.user || JSON.parse(localStorage.getItem('userProfile') || '{ }');
                    const authPlatform = userProfile.auth_platform;

                    console.log(' Detected auth platform:', authPlatform);

                    if (authPlatform === 'microsoft') {
                        localStorage.setItem('oauth_connected_microsoft', 'true');
                        console.log(' Marked Microsoft 365 OAuth as connected');
                    } else if (authPlatform === 'google') {
                        localStorage.setItem('oauth_connected', 'true');
                        console.log(' Marked Google OAuth as connected');
                    }

                    // Show main app
                    await UserAuth.showMainApp();

                    // Clean URL
                    window.history.replaceState({}, document.title, window.location.pathname);
                    return; // Don't call init() - we already initialized
                }

                // No OAuth token in URL - proceed with normal init
                UserAuth.init();

                // Initialize Device Lock Manager after authentication
                setTimeout(() => {
                    if (UserAuth.user) {
                        DeviceLockManager.init();
                    }
                }, 1000);
            }

            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => {
                    initializeApp();
                });
            } else {
                initializeApp();
            }

