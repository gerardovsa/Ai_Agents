
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

    </script>

    <!-- ==================== SYNERGY DASHBOARD STYLES ==================== -->
    <style>
        /* Synergy Dashboard Container */
        .synergy-dashboard-wrapper {
            height: calc(100vh - var(--header-height) - 40px);
            display: flex;
            flex-direction: column;
            background: var(--bg-primary);
            overflow: hidden;
        }

        /* Dashboard Header */
        .synergy-dashboard-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: var(--space-5);
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-default);
            flex-shrink: 0;
        }

        .synergy-header-left {
            display: flex;
            align-items: center;
            gap: var(--space-5);
        }

        .synergy-title {
            display: flex;
            align-items: center;
            gap: var(--space-3);
            font-size: 24px;
            font-weight: 600;
            color: var(--text-primary);
            margin: 0;
        }

        .synergy-title i {
            color: var(--accent-primary);
        }

        .synergy-stats {
            display: flex;
            gap: var(--space-4);
        }

        .stat-item {
            display: flex;
            align-items: center;
            gap: var(--space-2);
            font-size: 14px;
            color: var(--text-secondary);
        }

        .stat-item i {
            color: var(--accent-primary);
        }

        .stat-item strong {
            color: var(--text-primary);
            font-size: 16px;
        }

        .synergy-header-right {
            display: flex;
            gap: var(--space-3);
        }

        .synergy-action-btn {
            width: 32px;
            height: 32px;
            padding: 0;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-default);
            border-radius: 6px;
            color: var(--text-primary);
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }

        .synergy-action-btn:hover {
            background: var(--bg-hover);
            border-color: var(--accent-primary);
            transform: translateY(-1px);
        }

        .synergy-action-btn.synergy-primary {
            background: var(--accent-primary);
            color: white;
            border-color: var(--accent-primary);
        }

        .synergy-action-btn.synergy-primary:hover {
            background: #1c5fa8;
        }

        /* Real-time Connection Status Indicator */
        .realtime-status-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .realtime-status {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-default);
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .realtime-status:hover {
            background: var(--bg-secondary);
            border-color: var(--accent-primary);
        }

        .realtime-status i {
            font-size: 8px;
            animation: pulse 2s ease-in-out infinite;
        }

        .realtime-status.status-connected {
            border-color: #10b981;
            background: rgba(16, 185, 129, 0.1);
        }

        .realtime-status.status-connected i {
            color: #10b981;
            animation: none;
        }

        .realtime-status.status-connecting {
            border-color: #f59e0b;
            background: rgba(245, 158, 11, 0.1);
        }

        .realtime-status.status-connecting i {
            color: #f59e0b;
        }

        .realtime-status.status-error {
            border-color: #ef4444;
            background: rgba(239, 68, 68, 0.1);
        }

        .realtime-status.status-error i {
            color: #ef4444;
            animation: none;
        }

        @keyframes pulse {

            0%,
            100% {
                opacity: 1;
            }

            50% {
                opacity: 0.5;
            }
        }

        /* Kanban Board */
        .kanban-board-container {
            display: flex;
            gap: 16px;
            padding: var(--space-5);
            overflow-x: auto;
            overflow-y: auto;
            flex: 1;
        }

        .kanban-column {
            min-width: 360px;
            max-width: 360px;
            background: transparent;
            border: 1px solid var(--border-default);
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            height: fit-content;
        }

        .kanban-column-header {
            padding: var(--space-3);
            border-bottom: 1px solid var(--border-default);
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-shrink: 0;
        }

        .column-header-left {
            display: flex;
            align-items: center;
            gap: var(--space-2);
        }

        .column-icon {
            font-size: 18px;
            color: var(--accent-primary);
        }

        .column-title {
            font-size: 16px;
            font-weight: 600;
            color: var(--text-primary);
            margin: 0;
        }

        .column-count {
            background: var(--bg-tertiary);
            color: var(--text-secondary);
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }

        .column-menu-btn {
            background: transparent;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            padding: var(--space-1);
            border-radius: 4px;
            transition: all 0.2s ease;
        }

        .column-menu-btn:hover {
            background: var(--bg-hover);
            color: var(--text-primary);
        }

        /* ==================== MULTI-AGENT DASHBOARD HEADER ==================== */
        .multi-agent-dashboard-wrapper {
            display: flex;
            flex-direction: column;
            height: 100%;
            overflow: hidden;
        }

        .multi-agent-dashboard-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: var(--space-5);
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-default);
            flex-shrink: 0;
        }

        .multi-agent-header-left {
            display: flex;
            align-items: center;
            gap: var(--space-5);
        }

        .multi-agent-title {
            display: flex;
            align-items: center;
            gap: var(--space-3);
            font-size: 24px;
            font-weight: 600;
            color: var(--text-primary);
            margin: 0;
        }

        .multi-agent-title i {
            color: var(--accent-primary);
        }

        .multi-agent-stats {
            display: flex;
            gap: var(--space-4);
        }

        .multi-agent-header-right {
            display: flex;
            gap: var(--space-3);
        }

        .multi-agent-action-btn {
            width: 32px;
            height: 32px;
            padding: 0;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-default);
            border-radius: 6px;
            color: var(--text-primary);
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }

        .multi-agent-action-btn:hover {
            background: var(--bg-hover);
            border-color: var(--accent-primary);
            transform: translateY(-1px);
        }

        .multi-agent-action-btn.multi-agent-primary {
            background: var(--accent-primary);
            color: white;
            border-color: var(--accent-primary);
        }

        .multi-agent-action-btn.multi-agent-primary:hover {
            background: #1c5fa8;
        }

        /* Agent Quick Nav Bar */
        .agent-quick-nav-bar {
            background: var(--bg-tertiary);
            border-bottom: 1px solid var(--border-default);
            padding: var(--space-3) var(--space-5);
            flex-shrink: 0;
            overflow-x: auto;
            overflow-y: hidden;
        }

        .agent-quick-nav-container {
            display: flex;
            gap: var(--space-2);
            min-height: 36px;
        }

        .agent-quick-nav-badge {
            display: flex;
            align-items: center;
            gap: var(--space-2);
            padding: var(--space-2) var(--space-3);
            background: var(--bg-secondary);
            border: 1px solid var(--border-default);
            border-radius: 6px;
            color: var(--text-primary);
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
            flex-shrink: 0;
        }

        .agent-quick-nav-badge:hover {
            background: var(--bg-hover);
            border-color: var(--accent-primary);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        .agent-quick-nav-badge.active {
            background: var(--accent-primary);
            border-color: var(--accent-primary);
            color: white;
        }

        /* Highlight badge when agent has thread/messages */
        .agent-quick-nav-badge.has-thread {
            background: var(--accent-primary);
            border-color: var(--accent-primary);
            color: white;
            box-shadow: 0 2px 8px rgba(37, 123, 221, 0.3);
        }

        .agent-quick-nav-badge.has-thread:hover {
            background: #1c5fa8;
            box-shadow: 0 4px 12px rgba(37, 123, 221, 0.5);
        }

        .agent-quick-nav-badge i {
            font-size: 12px;
        }

        .agent-quick-nav-badge .thread-indicator {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 2px 6px;
            font-size: 11px;
            font-weight: 700;
            min-width: 20px;
        }

        .agent-quick-nav-badge.active .thread-indicator,
        .agent-quick-nav-badge.has-thread .thread-indicator {
            background: rgba(255, 255, 255, 0.3);
        }

        /* Agent Badge Tooltip */
        .agent-badge-tooltip {
            position: fixed;
            background: #1e293b;
            color: white;
            padding: 12px;
            border-radius: 8px;
            font-size: 12px;
            min-width: 220px;
            max-width: 320px;
            z-index: 10000;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.1);
            opacity: 0;
            visibility: hidden;
            transform: translateY(-8px);
            transition: all 0.2s ease;
            pointer-events: none;
        }

        .agent-badge-tooltip.show {
            opacity: 1;
            visibility: visible;
            transform: translateY(0);
            pointer-events: auto;
        }

        .agent-tooltip-title {
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 8px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .agent-tooltip-content {
            line-height: 1.6;
        }

        .agent-tooltip-content>div {
            margin-bottom: 6px;
        }

        .agent-tooltip-content>div:last-child {
            margin-bottom: 0;
        }

        .kanban-cards-container {
            padding: var(--space-2);
            overflow-y: visible;
            flex: 1;
            min-height: 100px;
        }

        /* Kanban Card */
        .kanban-card {
            background: var(--bg-tertiary);
            border: 2px solid var(--border-default);
            border-radius: 6px;
            padding: var(--space-1);
            margin-bottom: var(--space-3);
            cursor: grab;
            transition: all 0.2s ease;
            user-select: none;
        }

        .kanban-card:hover {
            background: var(--bg-hover);
            border-color: var(--accent-primary);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            cursor: pointer;
        }

        .kanban-card:active {
            cursor: grabbing;
        }

        .kanban-card.gu-mirror {
            opacity: 0.9;
            transform: rotate(2deg);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            cursor: grabbing;
        }

        .kanban-card.gu-transit {
            opacity: 0.3;
        }

        /* Card Header */
        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: var(--space-2);
        }

        .card-priority {
            font-size: 16px;
            display: flex;
            align-items: center;
        }

        .card-menu {
            position: relative;
            color: var(--text-muted);
            cursor: pointer;
            padding: 4px 6px;
            border-radius: 4px;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
        }

        .card-menu:hover {
            background: var(--bg-hover);
            color: var(--text-primary);
        }

        /* Hover-Expand Menu Container - creates hover zone */
        .card-menu {
            position: relative;
        }

        .card-menu:hover .card-menu-expanded {
            display: flex;
            opacity: 1;
        }

        /* Hover-Expand Menu - Expands down vertically, aligned with trigger */
        .card-menu-expanded {
            position: absolute;
            right: 10px;
            top: 0;
            background: var(--bg-secondary);
            border: 1px solid var(--border-default);
            border-radius: 6px;
            padding: 6px;
            display: none;
            opacity: 0;
            flex-direction: column;
            gap: 4px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 100;
            transition: opacity 0.2s ease;
            white-space: nowrap;
            pointer-events: auto;
            min-width: 140px;
        }

        /* Create an invisible bridge between trigger and menu */
        .card-menu::after {
            content: '';
            position: absolute;
            right: 0;
            top: 0;
            height: 30px;
            width: 100%;
            pointer-events: auto;
        }

        .card-menu-action {
            padding: 8px 12px;
            color: var(--text-secondary);
            background: var(--bg-tertiary);
            border: 1px solid var(--border-default);
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: 8px;
            font-size: 13px;
            width: 100%;
        }

        .card-menu-action:hover {
            background: var(--accent-primary);
            color: white;
            border-color: var(--accent-primary);
            transform: scale(1.05);
        }

        .card-menu-action.popout:hover {
            background: #9333ea;
            border-color: #9333ea;
        }

        .card-menu-action.resume:hover {
            background: #22c55e;
            border-color: #22c55e;
        }

        .card-menu-action.delete:hover {
            background: #ef4444;
            border-color: #ef4444;
        }

        /* Card Title */
        .card-title {
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: var(--space-3);
            line-height: 1.4;
            word-break: break-word;
        }

        /* Card Metadata */
        .card-meta {
            display: flex;
            flex-direction: column;
            gap: var(--space-1);
            margin-bottom: var(--space-3);
        }

        .card-project {
            font-size: 12px;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: var(--space-1);
            margin-bottom: var(--space-3);
        }

        .card-status-row {
            display: flex;
            align-items: center;
            gap: var(--space-2);
            font-size: 12px;
        }

        .status-badge {
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: 500;
            font-size: 11px;
        }

        .status-active {
            background: rgba(34, 197, 94, 0.1);
            color: #22c55e;
        }

        .status-paused {
            background: rgba(251, 191, 36, 0.1);
            color: #fbbf24;
        }

        .status-completed {
            background: rgba(59, 130, 246, 0.1);
            color: #3b82f6;
        }

        .card-time {
            color: var(--text-muted);
        }

        /* Card Stats */
        .card-stats {
            display: flex;
            gap: var(--space-3);
            margin-bottom: var(--space-3);
            flex-wrap: wrap;
        }

        .card-stat {
            font-size: 11px;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .card-stat i {
            color: var(--accent-primary);
            font-size: 12px;
        }

        /* Card Activity */
        .card-activity {
            margin-bottom: var(--space-2);
        }

        .activity-title {
            font-size: 10px;
            color: var(--text-muted);
            margin-bottom: var(--space-1);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }

        .activity-item {
            font-size: 11px;
            color: var(--text-secondary);
            padding: 2px 0;
            display: flex;
            align-items: flex-start;
            gap: var(--space-1);
            line-height: 1.4;
        }

        .activity-item::before {
            content: "•";
            color: var(--accent-primary);
            font-weight: bold;
            margin-top: 1px;
        }

        /* Card Footer */
        .card-footer {
            display: flex;
            flex-direction: column;
            gap: var(--space-3);
            padding-top: var(--space-2);
            border-top: 1px solid var(--border-muted);
            margin-top: var(--space-3);
        }

        .card-session-id {
            font-size: 10px;
            color: var(--text-secondary);
            font-family: var(--font-mono);
            font-weight: 500;
            width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .card-tags {
            display: flex;
            gap: 4px;
            flex-wrap: wrap;
            width: 100%;
        }

        .card-tag {
            background: var(--bg-hover);
            color: var(--text-primary);
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }

        /* Card Actions */
        .card-actions {
            margin-top: var(--space-2);
            display: flex;
            gap: var(--space-2);
            justify-content: space-between;
        }

        .card-action-icon {
            flex: 1;
            padding: var(--space-2);
            background: var(--bg-tertiary);
            color: var(--text-secondary);
            border: 1px solid var(--border-default);
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .card-action-icon:hover {
            background: var(--accent-primary);
            color: white;
            border-color: var(--accent-primary);
            transform: translateY(-1px);
        }

        .card-action-icon.popout:hover {
            background: #9333ea;
            border-color: #9333ea;
        }

        .card-action-icon.resume:hover {
            background: #22c55e;
            border-color: #22c55e;
        }

        .card-action-icon.edit:hover {
            background: #f59e0b;
            border-color: #f59e0b;
        }

        .card-resume-btn {
            width: 100%;
            padding: var(--space-2);
            background: var(--accent-primary);
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: var(--space-2);
        }

        .card-resume-btn:hover {
            background: #1c5fa8;
            transform: translateY(-1px);
        }

        /* Add Card Button */
        .add-card-btn {
            width: calc(100% - 24px);
            padding: var(--space-3);
            margin: 0 12px 12px 12px;
            background: var(--accent-primary);
            border: 1px solid var(--accent-primary);
            border-radius: 6px;
            color: white;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: var(--space-2);
            transition: all 0.2s ease;
        }

        .add-card-btn:hover {
            background: #1c5fa8;
            border-color: #1c5fa8;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3);
        }

        /* Sync Indicator */
        .sync-indicator {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: var(--space-3) var(--space-4);
            background: var(--bg-secondary);
            border: 1px solid var(--border-default);
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: var(--space-2);
            font-size: 13px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 10000;
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s ease;
            pointer-events: none;
        }

        .sync-indicator.show {
            opacity: 1;
            transform: translateY(0);
        }

        .sync-indicator.syncing {
            border-color: var(--accent-primary);
        }

        .sync-indicator.success {
            border-color: var(--accent-success);
        }

        .sync-indicator.error {
            border-color: var(--accent-error);
        }

        .sync-spinner {
            width: 16px;
            height: 16px;
            border: 2px solid var(--border-default);
            border-top-color: var(--accent-primary);
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
        }

        @keyframes spin {
            to {
                transform: rotate(360deg);
            }
        }

        /* Dragula Overrides */
        .gu-mirror {
            position: fixed !important;
            margin: 0 !important;
            z-index: 9999 !important;
            opacity: 0.9;
        }

        .gu-hide {
            display: none !important;
        }

        .gu-unselectable {
            -webkit-user-select: none !important;
            -moz-user-select: none !important;
            -ms-user-select: none !important;
            user-select: none !important;
        }

        .gu-transit {
            opacity: 0.3;
        }

        /* ==================== EXPANDED CARD STYLES ==================== */



        /* ========================================
         * Card Collapsed/Expanded View Visibility
         * ========================================
         * Note: No transitions on these views - display: none/block cannot be animated
         * Attempting to transition causes visual glitches (spasm/merge) on initial load
         * Specific transitions are applied to child elements that need animation
         */

        /* Control visibility based on data-expanded attribute */
        .kanban-card[data-expanded="false"] .card-collapsed-view {
            display: block !important;
        }

        .kanban-card[data-expanded="false"] .card-expanded-view {
            display: none !important;
        }

        .kanban-card[data-expanded="true"] .card-collapsed-view {
            display: none !important;
        }

        .kanban-card[data-expanded="true"] .card-expanded-view {
            display: block !important;
        }

        /*  FIX: Hide bottom action buttons in collapsed view */
        .card-collapsed-view>.card-actions {
            display: none !important;
        }

        .card-collapsed-view {
            padding: var(--space-3);
        }

        .card-expanded-view {
            padding: var(--space-3);
        }

        /* Smooth transitions for animatable properties only */
        .kanban-card[data-expanded="true"] {
            transition: height 0.3s ease, max-height 0.3s ease;
        }

        /* Prevent layout shift during transitions */
        .kanban-card {
            will-change: auto;
        }

        .card-title-large {
            font-size: 18px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: var(--space-4);
        }

        .card-description {
            margin: var(--space-2) 0;

        }

        .card-description p {
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.6;
            margin: 0;
        }

        /* Thread list loading placeholder styling */
        .thread-list-loading {
            font-size: 13px;
            /* match click list item font size */
            color: var(--text-secondary);
            padding: 6px 0;
            display: block;
        }

        .thread-list-loading i {
            margin-right: 8px;
            font-size: 12px;
            vertical-align: middle;
        }

        /* Drop zone prompt styling */
        .thread-list-loading.drop-zone-prompt {
            font-style: italic;
            color: var(--text-tertiary);
            opacity: 0.85;
        }

        /* Documents list placeholder styling */
        .docs-list .no-docs-message {
            font-size: 13px;
            color: var(--text-secondary);
            padding: 8px 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .docs-list .doc-item {
            font-size: 13px;
            color: var(--text-primary);
            padding: 6px 0;
        }

        /* Ensure the description text inside Synergy/Popout cards wraps properly */
        .card-description.markdown-content .description-text,
        .popout-card-content .card-description .description-text {
            white-space: normal;
            word-wrap: break-word;
            overflow-wrap: anywhere;
            hyphens: auto;
            background: var(--bg-secondary);
            padding: var(--space-2);
        }

        /* Markdown Rendering Styles */
        .markdown-content h1 {
            font-size: 1.5em;
            font-weight: 700;
            color: var(--text-primary);
            margin-top: 8px;
            margin-bottom: 4px;
            line-height: 1.3;
        }

        .markdown-content h2 {
            font-size: 1.3em;
            font-weight: 600;
            color: var(--text-primary);
            margin-top: 6px;
            margin-bottom: 3px;
            line-height: 1.3;
        }

        .markdown-content h3 {
            font-size: 1.15em;
            font-weight: 600;
            color: var(--text-primary);
            margin-top: 5px;
            margin-bottom: 3px;
            line-height: 1.3;
        }

        .markdown-content strong {
            font-weight: 600;
            color: var(--text-primary);
        }

        .markdown-content em {
            font-style: italic;
            color: var(--text-secondary);
        }

        .markdown-content ul {
            margin: 0.5em 0;
            padding-left: 1.5em;
            list-style-type: disc;
        }

        .markdown-content ol {
            margin: 0.5em 0;
            padding-left: 1.5em;
        }

        .markdown-content li {
            margin: 0.2em 0;
            color: var(--text-primary);
            font-size: 12px;
            line-height: 1.4;
        }

        .markdown-content p {
            margin: 0.5em 0;
            line-height: 1.6;
        }

        .markdown-content .md-checkbox {
            display: flex;
            align-items: center;
            margin: 0.4em 0;
            gap: 0.5em;
        }

        .markdown-content .md-checkbox input[type="checkbox"] {
            cursor: default;
            margin: 0;
        }

        .markdown-content .md-checkbox span {
            color: var(--text-primary);
            line-height: 1.5;
        }

        .card-section {
            margin: var(--space-2) 0;
            padding: var(--space-2);
            background: var(--bg-tertiary);
            border-radius: 6px;
        }

        .section-title {
            font-size: 14px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: var(--space-4);
            margin-top: var(--space-4);
            display: flex;
            align-items: center;
            gap: var(--space-3);
            justify-content: flex-start;
            text-align: left;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(15, 23, 42, 0.06);
        }

        .section-title i {
            color: var(--accent-primary);
        }

        .card-meta-expanded {
            display: flex;
            align-items: center;
            gap: var(--space-3);
            flex-wrap: wrap;
            margin-top: var(--space-4);
            margin-bottom: var(--space-4);
            font-size: 12px;
        }

        .card-assignees {
            display: flex;
            align-items: center;
            gap: var(--space-2);
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: var(--space-4);
            margin-bottom: var(--space-4);
        }

        .card-assignees i {
            color: var(--accent-primary);
        }

        .card-dates {
            display: flex;
            flex-wrap: wrap;
            gap: var(--space-2);
            margin-top: var(--space-4);
            margin-bottom: var(--space-4);
        }

        .date-item {
            display: flex;
            align-items: center;
            gap: var(--space-1);
            font-size: 12px;
            color: var(--text-secondary);
            padding: 4px 8px;
            background: var(--bg-tertiary);
            border-radius: 4px;
        }

        .date-item.overdue {
            color: var(--accent-error);
            background: rgba(239, 68, 68, 0.1);
        }

        .date-item i {
            color: var(--accent-primary);
        }

        .date-item.overdue i {
            color: var(--accent-error);
        }

        /* Document List */
        .document-list,
        .link-list,
        .thread-list,
        .agent-list {
            display: flex;
            flex-direction: column;
            gap: var(--space-2);
        }

        .document-item,
        .link-item,
        .thread-item,
        .agent-item {
            display: flex;
            align-items: center;
            gap: var(--space-2);
            padding: var(--space-2);
            background: var(--bg-tertiary);
            border-radius: 4px;
            transition: all 0.2s ease;
        }

        .document-item:hover,
        .link-item:hover,
        .thread-item:hover,
        .agent-item:hover {
            background: var(--bg-hover);
        }

        .document-item i,
        .link-item i,
        .thread-item i,
        .agent-item i {
            color: var(--accent-primary);
            font-size: 12px;
        }

        .thread-id,
        .agent-name {
            flex: 1;
            font-size: 12px;
            color: var(--text-primary);
            font-family: 'Courier New', monospace;
        }

        .agent-name {
            font-family: inherit;
            font-weight: 500;
        }

        .document-link,
        .link-url {
            flex: 1;
            color: var(--accent-primary);
            text-decoration: none;
            font-size: 12px;
            font-weight: 500;
        }

        .document-link:hover,
        .link-url:hover {
            text-decoration: underline;
        }

        .doc-info {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        .doc-name {
            font-size: 12px;
            color: var(--text-primary);
            font-weight: 500;
        }

        .doc-type {
            font-size: 10px;
            color: var(--text-muted);
        }

        .doc-link {
            color: var(--accent-primary);
            text-decoration: none;
            padding: 4px;
            border-radius: 3px;
            transition: all 0.2s ease;
        }

        .doc-link:hover {
            background: var(--bg-hover);
            color: var(--accent-secondary);
        }

        .doc-link i {
            font-size: 12px;
        }

        .document-type,
        .link-type {
            font-size: 10px;
            color: var(--text-muted);
            background: var(--bg-tertiary);
            padding: 2px 6px;
            border-radius: 3px;
            text-transform: uppercase;
        }

        /* Steps List */
        .steps-list {
            display: flex;
            flex-direction: column;
            gap: var(--space-2);
        }

        .step-item {
            display: flex;
            align-items: center;
            gap: var(--space-2);
            padding: var(--space-2);
            background: var(--bg-secondary);
            border-radius: 4px;
            font-size: 12px;
        }

        .step-item.completed {
            opacity: 0.6;
        }

        .step-item.completed .step-description {
            text-decoration: line-through;
        }

        .step-item input[type="checkbox"] {
            cursor: pointer;
            width: 16px;
            height: 16px;
        }

        .step-description {
            flex: 1;
            color: var(--text-primary);
        }

        .step-due {
            font-size: 10px;
            color: var(--text-muted);
            background: var(--bg-tertiary);
            padding: 2px 6px;
            border-radius: 3px;
        }

        /* Checklist */
        .checklist {
            display: flex;
            flex-direction: column;
            gap: var(--space-2);
        }

        .checklist-item {
            display: flex;
            align-items: center;
            gap: var(--space-2);
            padding: var(--space-2);
            background: var(--bg-secondary);
            border-radius: 4px;
            font-size: 12px;
            color: var(--text-primary);
        }

        .checklist-item.completed {
            opacity: 0.6;
        }

        .checklist-item.completed span {
            text-decoration: line-through;
        }

        .checklist-item input[type="checkbox"] {
            cursor: pointer;
            width: 16px;
            height: 16px;
        }

        /* Notes */
        .card-notes {
            font-size: 12px;
            color: var(--text-secondary);
            line-height: 1.6;
            padding: var(--space-2);
            background: var(--bg-secondary);
            border-radius: 4px;
            white-space: pre-wrap;
        }

        /* Activity Log */
        .activity-log {
            display: flex;
            flex-direction: column;
            gap: var(--space-1);
        }

        .activity-log-item {
            font-size: 11px;
            color: var(--text-secondary);
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: var(--space-1);
        }

        .activity-time {
            color: var(--text-muted);
            font-size: 10px;
        }

        .card-footer-expanded {
            display: flex;
            flex-direction: column;
            gap: var(--space-2);
            padding-top: var(--space-3);
            border-top: 1px solid var(--border-muted);
            margin-top: var(--space-3);
        }

        .card-session-id-full {
            font-size: 10px;
            color: var(--text-muted);
            font-family: var(--font-mono);
            word-break: break-all;
        }

        .card-actions-expanded {
            display: flex;
            gap: var(--space-2);
            margin-top: var(--space-3);
            padding-top: var(--space-3);
            border-top: 1px solid var(--border-default);
            justify-content: flex-end;
        }

        .card-actions-expanded .card-action-icon {
            flex: 0 0 auto;
            width: 32px;
            height: 32px;
            padding: 0;
        }

        .card-expand-btn,
        .card-collapse-btn {
            padding: var(--space-2);
            background: var(--bg-hover);
            color: var(--text-primary);
            border: 1px solid var(--border-default);
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: var(--space-2);
        }

        .card-expand-btn:hover,
        .card-collapse-btn:hover {
            background: var(--bg-tertiary);
            border-color: var(--accent-primary);
            color: var(--accent-primary);
        }

        .card-expand-btn {
            flex: 1;
        }

        .card-collapse-btn {
            flex: 1;
        }

        .card-actions button {
            flex: 1;
        }

        /* Card action icons already styled above */

        .card-edit-btn {
            background: transparent;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            padding: var(--space-1);
            border-radius: 4px;
            transition: all 0.2s ease;
        }

        .card-edit-btn:hover {
            background: var(--bg-hover);
            color: var(--accent-primary);
        }

        .card-header-actions {
            display: flex;
            align-items: center;
            gap: var(--space-2);
        }

        /* ==================== POP-OUT CARD WINDOW ==================== */
        .popout-card-window {
            position: fixed;
            background: var(--bg-secondary);
            border: 2px solid var(--border-default);
            border-radius: 12px;
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.5);
            z-index: 10000;
            display: flex;
            flex-direction: column;
            min-width: 650px;
            min-height: 500px;
            width: 850px;
            height: 800px;
            max-width: 95vw;
            max-height: 95vh;
            overflow: hidden;
            resize: both;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
            line-height: 1.6;
        }

        .popout-card-window.active {
            border-color: var(--accent-primary);
            z-index: 10001;
        }

        .popout-card-header {
            background: var(--bg-tertiary);
            border-bottom: 1px solid var(--border-default);
            padding: var(--space-3);
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: move;
            user-select: none;
        }

        .popout-card-window.expanded .popout-card-header {
            cursor: not-allowed;
        }

        .popout-card-title {
            font-size: 15px;
            font-weight: 600;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: var(--space-2);
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .popout-card-controls {
            display: flex;
            gap: var(--space-1);
        }

        .popout-control-btn {
            width: 28px;
            height: 28px;
            background: transparent;
            border: 1px solid var(--border-default);
            border-radius: 4px;
            color: var(--text-secondary);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            font-size: 12px;
        }

        .popout-control-btn:hover {
            background: var(--bg-hover);
            border-color: var(--accent-primary);
            color: var(--accent-primary);
        }

        .popout-control-btn.close:hover {
            background: #ef4444;
            border-color: #ef4444;
            color: white;
        }

        .popout-card-content {
            flex: 1;
            overflow-y: auto;
            padding: var(--space-5);
            background: var(--bg-secondary);
            font-size: 14px;
        }

        .popout-card-content::-webkit-scrollbar {
            width: 8px;
        }

        .popout-card-content::-webkit-scrollbar-track {
            background: var(--bg-tertiary);
        }

        .popout-card-content::-webkit-scrollbar-thumb {
            background: var(--border-default);
            border-radius: 4px;
        }

        /* Enhanced spacing for content inside popout */
        .popout-card-content .card-expanded-view {
            padding: 0;
        }

        .popout-card-content .card-title-large {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: var(--space-4);
        }

        .popout-card-content .card-description {
            margin: var(--space-4) 0;
            padding: var(--space-3);
            background: var(--bg-secondary);
            border-radius: 6px;
        }

        .popout-card-content .card-section {
            margin: var(--space-4) 0;
            padding: var(--space-4);
        }

        .popout-card-content .section-title {
            margin-top: 0;
            margin-bottom: var(--space-3);
            font-size: 15px;
            justify-content: flex-start;
            text-align: left;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(15, 23, 42, 0.06);
        }

        .popout-card-content .card-meta-expanded {
            margin: var(--space-4) 0;
            padding: var(--space-3);
            background: var(--bg-tertiary);
            border-radius: 6px;
        }

        .popout-card-content .card-header-actions {
            margin-bottom: var(--space-4);
            padding-bottom: var(--space-3);
            border-bottom: 1px solid var(--border-muted);
        }

        .popout-card-content .card-actions-expanded {
            margin-top: var(--space-4);
            padding-top: var(--space-4);
        }

        .popout-card-footer {
            background: var(--bg-tertiary);
            border-top: 1px solid var(--border-default);
            padding: var(--space-2) var(--space-3);
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 11px;
            color: var(--text-muted);
        }

        .popout-move-warning {
            display: none;
            align-items: center;
            gap: var(--space-1);
            padding: 4px 8px;
            background: rgba(251, 191, 36, 0.1);
            border: 1px solid var(--accent-warning);
            border-radius: 4px;
            color: var(--accent-warning);
            font-size: 11px;
        }

        .popout-card-window.expanded .popout-move-warning {
            display: flex;
        }

        /* Popup Edit Mode Styles */
        .popout-card-window.popup-edit-mode {
            border-color: var(--accent-warning);
        }

        .popout-card-window.popup-edit-mode .popout-card-header {
            background: linear-gradient(135deg, rgba(251, 191, 36, 0.1), rgba(251, 191, 36, 0.05));
            border-bottom-color: var(--accent-warning);
        }

        .popout-control-btn.edit {
            color: var(--accent-primary);
        }

        .popout-control-btn.edit:hover {
            background: var(--accent-primary);
            color: white;
        }

        .popout-control-btn.save {
            color: var(--accent-success);
        }

        .popout-control-btn.save:hover {
            background: var(--accent-success);
            color: white;
        }

        .popout-control-btn.cancel {
            color: var(--text-muted);
        }

        .popout-control-btn.cancel:hover {
            background: var(--bg-hover);
            color: var(--text-primary);
        }

        .popout-control-btn.delete {
            color: var(--accent-error);
        }

        .popout-control-btn.delete:hover {
            background: var(--accent-error);
            color: white;
        }

        .editable-mode {
            background: var(--bg-tertiary);
            padding: var(--space-4);
            border-radius: 8px;
        }

        .editable-mode .form-group {
            margin-bottom: var(--space-3);
        }

        .editable-mode .form-group label {
            display: flex;
            align-items: center;
            gap: var(--space-2);
            font-size: 13px;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: var(--space-2);
        }

        .editable-mode .form-group label i {
            color: var(--accent-primary);
        }

        .editable-mode .form-control {
            width: 100%;
            background: var(--bg-secondary);
            border: 1px solid var(--border-default);
            border-radius: 6px;
            padding: 8px 12px;
            color: var(--text-primary);
            font-size: 14px;
            transition: all 0.2s ease;
        }

        .editable-mode .form-control:focus {
            outline: none;
            border-color: var(--accent-primary);
            box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.1);
        }

        .editable-mode textarea.form-control {
            min-height: 80px;
            resize: vertical;
            font-family: inherit;
        }

        .editable-mode .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: var(--space-3);
            margin-bottom: var(--space-3);
        }

        .editable-mode select.form-control {
            cursor: pointer;
        }

        .edit-mode-badge {
            display: flex;
            align-items: center;
            gap: var(--space-2);
            padding: 6px 12px;
            background: var(--accent-warning);
            color: var(--bg-primary);
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.5px;
        }

        .readonly-sections {
            margin-top: var(--space-4);
            padding: var(--space-3);
            background: var(--bg-secondary);
            border: 1px dashed var(--border-default);
            border-radius: 6px;
        }

        .readonly-sections .info-message {
            display: flex;
            align-items: center;
            gap: var(--space-2);
            color: var(--text-muted);
            font-size: 13px;
            font-style: italic;
        }

        .readonly-sections .info-message i {
            color: var(--accent-info);
        }

        /* ==================== EDIT MODAL STYLES ==================== */

        .edit-card-modal {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 10000;
            pointer-events: none;
            /* Allow clicks to pass through to UI behind */
        }

        .modal-content {
            position: fixed;
            /* Changed from relative to fixed for draggability */
            top: 10%;
            left: 50%;
            transform: translateX(-50%);
            background: var(--bg-secondary);
            border: 2px solid var(--border-default);
            border-radius: 12px;
            width: 800px;
            min-height: 400px;
            max-height: 80vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            animation: modalSlideIn 0.3s ease;
            z-index: 10001;
            pointer-events: auto;
            /* Modal itself is clickable */
            resize: vertical;
            /* Enable vertical resizing */
            overflow: hidden;
            /* Required for resize to work */
        }

        @keyframes modalSlideIn {
            from {
                opacity: 0;
                transform: translateY(-20px) scale(0.95);
            }

            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        .modal-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: var(--space-4);
            border-bottom: 1px solid var(--border-default);
            cursor: move;
            /* Indicate draggable area */
            user-select: none;
            /* Prevent text selection while dragging */
        }

        .modal-header h3 {
            margin: 0;
            font-size: 18px;
            font-weight: 700;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: var(--space-2);
        }

        .modal-header h3 i {
            color: var(--accent-primary);
        }

        .modal-close-btn {
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-size: 20px;
            cursor: pointer;
            padding: var(--space-2);
            border-radius: 6px;
            transition: all 0.2s ease;
        }

        .modal-close-btn:hover {
            background: var(--bg-hover);
            color: var(--text-primary);
        }

        .modal-body {
            padding: 28px 24px;
            overflow-y: auto;
            flex: 1;
            line-height: 1.6;
        }

        .modal-body::-webkit-scrollbar {
            width: 10px;
        }

        .modal-body::-webkit-scrollbar-track {
            background: var(--bg-tertiary);
            border-radius: 5px;
        }

        .modal-body::-webkit-scrollbar-thumb {
            background: var(--border-default);
            border-radius: 5px;
            transition: background 0.2s;
        }

        .modal-body::-webkit-scrollbar-thumb:hover {
            background: var(--text-muted);
        }

        .form-group {
            margin-bottom: var(--space-3);
        }

        .form-group label {
            display: block;
            font-size: 14px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: var(--space-2);
        }

        .form-group label .required {
            color: var(--accent-error);
        }

        .form-control {
            width: 100%;
            padding: var(--space-2) var(--space-3);
            background: var(--bg-tertiary);
            border: 1px solid var(--border-default);
            border-radius: 6px;
            color: var(--text-primary);
            font-size: 13px;
            font-family: var(--font-sans);
            transition: all 0.2s ease;
        }

        .form-control:focus {
            outline: none;
            border-color: var(--accent-primary);
            background: var(--bg-secondary);
        }

        .form-control::placeholder {
            color: var(--text-muted);
        }

        textarea.form-control {
            resize: vertical;
            font-family: var(--font-sans);
            line-height: 1.5;
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: var(--space-3);
        }

        .form-section {
            margin-top: var(--space-4);
            padding-top: var(--space-4);
        }

        .section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: var(--space-3);
        }

        .section-header label {
            font-size: 14px;
            font-weight: 700;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: var(--space-2);
            margin: 0;
        }

        .section-header label i {
            color: var(--accent-primary);
        }

        .btn-add-item {
            padding: 6px 12px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-default);
            border-radius: 6px;
            color: var(--text-primary);
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
        }

        .btn-add-item:hover {
            background: var(--accent-primary);
            border-color: var(--accent-primary);
            color: white;
        }

        .items-list {
            display: flex;
            flex-direction: column;
            gap: var(--space-2);
        }

        .item-row {
            display: flex;
            gap: var(--space-2);
            align-items: flex-start;
        }

        .item-row .form-control {
            flex: 1;
        }

        /* Display Number Badges */
        .item-number-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 40px;
            height: 32px;
            background: linear-gradient(135deg, #58a6ff 0%, #4a8fe7 100%);
            color: white;
            font-weight: 700;
            border-radius: 6px;
            font-size: 13px;
            padding: 0 8px;
            white-space: nowrap;
            box-shadow: 0 2px 4px rgba(88, 166, 255, 0.2);
        }

        .item-number {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 32px;
            height: 28px;
            background: #e3f2fd;
            color: #1976d2;
            font-weight: 600;
            border-radius: 4px;
            font-size: 13px;
            padding: 0 6px;
            margin-right: 6px;
        }

        .sub-number {
            display: inline-block;
            min-width: 42px;
            padding: 2px 2px;
            background: #fafafa;
            border: 1px solid #e0e0e0;
            border-radius: 3px;
            font-size: 12px;
            color: #666;
            text-align: center;
            font-weight: 600;
        }

        .item-row input[type="checkbox"] {
            width: 18px;
            height: 18px;
            cursor: pointer;
            margin-top: 8px;
        }

        .btn-remove-item {
            padding: 8px 12px;
            background: transparent;
            border: 1px solid var(--border-default);
            border-radius: 6px;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
        }

        .btn-remove-item:hover {
            background: var(--accent-error);
            border-color: var(--accent-error);
            color: white;
        }

        .google-sync-options {
            display: flex;
            flex-direction: column;
            gap: var(--space-2);
        }

        .checkbox-label {
            display: flex;
            align-items: center;
            gap: var(--space-2);
            padding: var(--space-2);
            background: var(--bg-tertiary);
            border: 1px solid var(--border-default);
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .checkbox-label:hover {
            background: var(--bg-hover);
            border-color: var(--accent-primary);
        }

        .checkbox-label input[type="checkbox"] {
            width: 18px;
            height: 18px;
            cursor: pointer;
        }

        .checkbox-label span {
            font-size: 13px;
            color: var(--text-primary);
            font-weight: 500;
        }

        .modal-footer {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: var(--space-2);
            padding: var(--space-4);
            border-top: 1px solid var(--border-default);
        }

        .btn-primary,
        .btn-secondary {
            padding: var(--space-2) var(--space-4);
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: var(--space-2);
            transition: all 0.2s ease;
        }

        .btn-primary {
            background: var(--accent-primary);
            color: white;
            border: 1px solid var(--accent-primary);
        }

        .btn-primary:hover {
            background: #1c5fa8;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }

        .btn-secondary {
            background: var(--bg-tertiary);
            color: var(--text-primary);
            border: 1px solid var(--border-default);
        }

        .btn-secondary:hover {
            background: var(--bg-hover);
            border-color: var(--accent-primary);
            transform: translateY(-1px);
        }

        /* ==================== ACCOUNT SETTINGS STYLES ==================== */

        .settings-section {
            margin-bottom: 24px;
            border: 1px solid var(--border-default);
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }

        .settings-section:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }

        .settings-section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 18px 20px;
            background: var(--bg-tertiary);
            cursor: pointer;
            user-select: none;
            transition: all 0.2s ease;
            border-bottom: 1px solid transparent;
        }

        .settings-section-header:hover {
            background: var(--bg-hover);
            border-bottom-color: var(--border-default);
        }

        .settings-section-title {
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 600;
            color: var(--text-primary);
            font-size: 16px;
        }

        .settings-section-title i {
            color: var(--accent-primary);
            font-size: 18px;
        }

        .settings-section-toggle {
            display: flex;
            align-items: center;
            color: var(--text-secondary);
            font-size: 16px;
            transition: transform 0.2s ease;
        }

        .settings-section.collapsed .settings-section-toggle {
            transform: rotate(-90deg);
        }

        .settings-section-content {
            padding: 24px 20px;
            background: var(--bg-secondary);
            display: flex;
            flex-direction: column;
            gap: 24px;
            max-height: 500px;
            overflow-y: auto;
            transition: all 0.3s ease;
        }

        .settings-section.collapsed .settings-section-content {
            display: none;
            max-height: 0;
            padding: 0;
            overflow: hidden;
        }

        .settings-field {
            display: flex;
            flex-direction: column;
            gap: 10px;
            padding-bottom: 16px;
            border-bottom: 1px solid rgba(128, 128, 128, 0.1);
        }

        .settings-field:last-child {
            border-bottom: none;
            padding-bottom: 0;
        }

        .settings-field label {
            font-weight: 600;
            color: var(--text-primary);
            font-size: 14.5px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 4px;
        }

        .settings-value {
            font-weight: 700;
            color: var(--accent-primary);
            font-size: 13px;
            background: var(--bg-tertiary);
            padding: 2px 8px;
            border-radius: 4px;
        }

        .settings-field input[type="range"] {
            height: 6px;
            border-radius: 3px;
            background: var(--bg-tertiary);
            outline: none;
            -webkit-appearance: none;
            appearance: none;
        }

        .settings-field input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: var(--accent-primary);
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 2px 6px rgba(37, 99, 235, 0.3);
        }

        .settings-field input[type="range"]::-webkit-slider-thumb:hover {
            transform: scale(1.2);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.5);
        }

        .settings-field input[type="range"]::-moz-range-thumb {
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: var(--accent-primary);
            cursor: pointer;
            border: none;
            transition: all 0.2s ease;
            box-shadow: 0 2px 6px rgba(37, 99, 235, 0.3);
        }

        .settings-field input[type="range"]::-moz-range-thumb:hover {
            transform: scale(1.2);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.5);
        }

        .settings-field select {
            padding: 11px 14px;
            background: var(--bg-tertiary);
            border: 1.5px solid var(--border-default);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .settings-field select:hover {
            border-color: var(--accent-primary);
            background: var(--bg-hover);
            transform: translateY(-1px);
        }

        .settings-field select:focus {
            outline: none;
            border-color: var(--accent-primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }

        .settings-field input[type="text"] {
            padding: 11px 14px;
            background: var(--bg-tertiary);
            border: 1.5px solid var(--border-default);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 14px;
            transition: all 0.2s ease;
        }

        .settings-field input[type="text"]:hover {
            border-color: var(--accent-primary);
            transform: translateY(-1px);
        }

        .settings-field input[type="text"]:focus {
            outline: none;
            border-color: var(--accent-primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }

        .settings-field small {
            font-size: 12.5px;
            line-height: 1.6;
            color: var(--text-muted);
            margin-top: 2px;
        }

        .settings-checkbox {
            display: flex;
            align-items: center;
            gap: var(--space-2);
            padding: var(--space-2);
            background: var(--bg-tertiary);
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .settings-checkbox:hover {
            background: var(--bg-hover);
        }

        .settings-checkbox input[type="checkbox"] {
            width: 18px;
            height: 18px;
            cursor: pointer;
            accent-color: var(--accent-primary);
        }

        .settings-checkbox label {
            flex: 1;
            cursor: pointer;
            font-weight: 500;
            color: var(--text-primary);
            margin: 0;
            font: 14px;
            gap: 0;
        }

        .settings-info {
            display: flex;
            align-items: flex-start;
            gap: var(--space-2);
            padding: var(--space-2);
            background: var(--bg-tertiary);
            border-left: 3px solid var(--accent-primary);
            border-radius: 4px;
            font-size: 13px;
            color: var(--text-secondary);
        }

        .settings-info i {
            color: var(--accent-primary);
            margin-top: 2px;
            flex-shrink: 0;
        }

        .settings-footer {
            font-size: 13px;
            color: var(--text-muted);
            padding: var(--space-3);
            background: var(--bg-tertiary);
            border-radius: 6px;
            margin-top: var(--space-2);
        }

        .settings-footer i {
            color: var(--accent-primary);
            margin-right: 4px;
        }

        /* Real-time collaboration indicators */
        .realtime-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: var(--space-2) var(--space-3);
            background: var(--bg-secondary);
            border: 1px solid var(--border-default);
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: var(--space-2);
            font-size: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            z-index: 9999;
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .realtime-indicator.show {
            opacity: 1;
        }

        .realtime-indicator.connected {
            border-color: var(--accent-success);
        }

        .realtime-indicator.disconnected {
            border-color: var(--accent-error);
        }

        .realtime-pulse {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-success);
            animation: pulse 2s ease infinite;
        }

        .realtime-indicator.disconnected .realtime-pulse {
            background: var(--accent-error);
            animation: none;
        }

        @keyframes pulse {

            0%,
            100% {
                opacity: 1;
            }

            50% {
                opacity: 0.3;
            }
        }

        /* Edit Modal Styles */
        .modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        }

        .edit-modal-content {
            background: white;
            border-radius: 12px;
            width: 90%;
            max-width: 900px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 30px;
            border-bottom: 2px solid #f0f0f0;
        }

        .modal-header h2 {
            margin: 0;
            font-size: 24px;
            color: #2c3e50;
        }



        .modal-close {
            background: transparent;
            border: 1px solid var(--border-default);
            font-size: 24px;
            color: var(--text-secondary);
            cursor: pointer;
            padding: 0;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
            transition: all 0.2s;
        }

        .modal-close:hover {
            color: var(--accent-error);
            border: 1px solid var(--accent-error);
        }

        .modal-body {
            padding: 30px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            font-size: 14px;
        }

        .form-control {
            width: 100%;
            padding: 10px 15px;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.2s;
        }

        .form-control:focus {
            outline: none;
            border-color: #3498db;
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .form-section {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #f0f0f0;
        }

        .form-section label {
            display: block;
            margin-bottom: 15px;
            font-weight: 600;
            color: #34495e;
            font-size: 16px;
        }

        .items-container {
            margin-bottom: 15px;
        }

        .item-row {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
            align-items: center;
        }

        .item-row input[type="text"],
        .item-row input[type="url"],
        .item-row input[type="date"],
        .item-row select,
        .item-row textarea {
            flex: 1;
            padding: 8px 12px;
            border: 1px solid var(--border-default);
            border-radius: 6px;
            font-size: 14px;
        }

        .item-row input[type="checkbox"] {
            width: 150x;
            height: 15px;
            cursor: pointer;
        }

        .btn-add-item {
            padding: 8px 16px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.2s;
        }

        .btn-add-item:hover {
            background: #2980b9;
        }

        .btn-remove-item {
            padding: 8px 12px;
            background: #e74c3c;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s;
        }

        .btn-remove-item:hover {
            background: #c0392b;
        }

        .modal-footer {
            display: flex;
            justify-content: flex-end;
            gap: 15px;
            padding: 20px 30px;
            border-top: 2px solid #f0f0f0;
        }

        .btn {
            padding: 10px 24px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-primary {
            background: #3498db;
            color: white;
        }

        .btn-primary:hover {
            background: #2980b9;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
        }

        .btn-secondary {
            background: #95a5a6;
            color: white;
        }

        .btn-secondary:hover {
            background: #7f8c8d;
        }

        /* Step Wrapper & Sub-Checklist Styles */
        .step-wrapper {
            margin-bottom: 15px;
            border-left: 3px solid #3498db;
            padding-left: 10px;
        }

        .step-main {
            margin-bottom: 8px;
        }

        .sub-checklist {
            margin-left: 35px;
            margin-top: 5px;
        }

        .sub-checklist-item {
            display: flex;
            gap: 8px;
            margin-bottom: 6px;
            align-items: center;
            padding: 6px;
            border-radius: 4px;
        }

        .sub-checklist-item input[type="text"] {
            flex: 1;
            padding: 6px 10px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            font-size: 13px;
        }

        .btn-add-subtask {
            padding: 8px 12px;
            background: #27ae60;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s;
            font-size: 12px;
        }

        .btn-add-subtask:hover {
            background: #229954;
        }

        .btn-remove-subtask {
            padding: 4px 8px;
            background: #e74c3c;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
            font-size: 12px;
        }

        .btn-remove-subtask:hover {
            background: #c0392b;
        }

        /* Sub-Checklist Display in Cards */
        .step-item-wrapper {
            margin-bottom: 12px;
        }

        .sub-checklist-display {
            margin-left: 30px;
            margin-top: 3px;
        }

        .sub-checklist-display .sub-item {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 2px 0;
            font-size: 11px;
            color: var(--text-primary);
        }

        .sub-checklist-display .sub-item.completed {
            text-decoration: line-through;
            opacity: 0.6;
        }

        .sub-checklist-display .sub-item i {
            color: #3498db;
            font-size: 10px;
        }

        .sub-checklist-display .sub-item input[type="checkbox"] {
            width: 14px;
            height: 14px;
            cursor: pointer;
        }

        .step-item .sub-count {
            font-size: 11px;
            color: #7f8c8d;
            margin-left: 8px;
            font-weight: 600;
        }

        /* ============================================================================
           INTERNAL DOCUMENT MODAL STYLES
           ============================================================================ */

        .internal-doc-modal {
            max-width: 1200px;
            width: 90%;
            max-height: 90vh;
        }

        .header-title-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            width: 100%;
        }

        .doc-title-input {
            border: none;
            background: transparent;
            font-size: inherit;
            font-weight: inherit;
            flex: 1;
            padding: 4px 8px;
            border-radius: 4px;
            color: var(--text-primary);
        }

        .doc-title-input:focus {
            background: var(--bg-tertiary);
            outline: 2px solid var(--accent-blue);
        }

        .btn-copy-id {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            color: var(--text-secondary);
            transition: all 0.2s;
            font-family: 'Courier New', monospace;
        }

        .btn-copy-id:hover {
            background: var(--accent-blue);
            color: white;
            transform: translateY(-1px);
        }

        .doc-meta {
            display: flex;
            gap: 16px;
            font-size: 13px;
            color: var(--text-secondary);
            margin-top: 8px;
            flex-wrap: wrap;
        }

        .doc-meta span {
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .doc-editor-container {
            height: 600px;
            display: flex;
            flex-direction: column;
        }

        .editor-tabs {
            display: flex;
            gap: 8px;
            border-bottom: 2px solid var(--border-color);
            margin-bottom: 16px;
        }

        .tab-btn {
            padding: 8px 16px;
            background: transparent;
            border: none;
            border-bottom: 2px solid transparent;
            cursor: pointer;
            color: var(--text-secondary);
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .tab-btn.active {
            color: var(--accent-blue);
            border-bottom-color: var(--accent-blue);
        }

        .tab-btn:hover {
            background: var(--bg-secondary);
        }

        .doc-editor {
            flex: 1;
            width: 100%;
            padding: 16px;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.6;
            resize: none;
        }

        .markdown-editor {
            background: var(--bg-secondary);
            color: var(--text-primary);
        }

        .html-editor {
            background: var(--bg-primary);
            color: var(--text-primary);
        }

        .doc-preview {
            flex: 1;
            padding: 16px;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            background: var(--bg-primary);
            overflow-y: auto;
        }

        .internal-doc-item {
            cursor: pointer;
            transition: all 0.2s;
        }

        .internal-doc-item:hover {
            background: var(--bg-secondary);
            transform: translateX(2px);
        }

        .doc-preview {
            font-size: 11px;
            color: var(--text-tertiary);
            font-style: italic;
            margin-top: 4px;
            display: block;
        }

        .internal-doc-btn {
            background: var(--accent-blue);
            color: white;
        }

        .internal-doc-btn:hover {
            background: #2980b9;
        }

        .footer-left,
        .footer-right {
            display: flex;
            gap: 8px;
            align-items: center;
        }

        .modal-footer {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
        }

        .btn-export {
            font-size: 13px;
            padding: 8px 14px;
        }

        .auto-save-indicator {
            color: #27ae60;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 4px;
            animation: fadeIn 0.3s;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(-5px);
            }

            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    </style>

    <!-- ==================== SYNERGY DASHBOARD JAVASCRIPT ==================== -->
    <script>
        // Synergy Dashboard - Complete Kanban Board Implementation
        // Initialize as window.synergyBoard to make it available globally immediately
        console.log('📦 [SYNERGY] Starting synergyBoard initialization...');

        window.synergyBoard = {
            drake: null,
            sessions: [],
            apiBaseUrl: window.API_BASE_URL || 'http://localhost:5001',
            initialized: false,

            // Safe wrapper for methods that require initialization
            async ensureInitialized() {
                if (!this.initialized) {
                    console.log('[SYNERGY] Auto-initializing synergyBoard...');
                    await this.init();
                }
            },

            async init() {
                if (this.initialized) {
                    console.log('? [SYNERGY] Already initialized');
                    return;
                }
                console.log('Initializing Synergy Dashboard...');

                // Initialize Supabase client for real-time updates
                this.initializeSupabase();

                // Load sessions from API
                await this.loadSessions();

                // Initialize drag and drop
                this.initializeDragula();

                // Render all cards
                this.renderAllCards();

                // Update stats
                this.updateStats();

                // Subscribe to real-time database changes (replaces polling)
                // Auto-refresh polling will only start if real-time subscription fails after 3 retries
                this.subscribeToRealtimeChanges();

                // Initialize WebSocket for real-time updates (legacy - keep for backwards compatibility)
                if (typeof SynergyRealtime !== 'undefined') {
                    try {
                        await SynergyRealtime.connect();
                        console.log('? [SYNERGY] Real-time WebSocket connected');
                    } catch (error) {
                        console.error('[SYNERGY] Failed to connect WebSocket:', error);
                    }
                }

                // Initialize Google Services
                // DISABLED: Requires OAuth configuration in Google Cloud Console
                // Add http://localhost:5001 to authorized origins to enable
                // this.initGoogleServices();

                this.initialized = true;
                console.log('? Synergy Dashboard initialized with Supabase real-time updates');
            },

            // Escape text for use in JavaScript strings (onclick handlers)
            escapeJs(text) {
                if (!text) return '';
                return text
                    .replace(/\\/g, '\\\\')  // Escape backslashes first
                    .replace(/'/g, "\\'")     // Escape single quotes
                    .replace(/"/g, '\\"')     // Escape double quotes
                    .replace(/\n/g, '\\n')    // Escape newlines
                    .replace(/\r/g, '\\r');   // Escape carriage returns
            },

            async loadSessions() {
                try {
                    console.log('[SYNERGY] Loading sessions with DataLoader (cached + batched)...');
                    const startTime = performance.now();

                    // Use DataLoader for caching and batching
                    if (typeof DataLoader !== 'undefined' && DataLoader.synergy) {
                        this.sessions = await DataLoader.synergy.loadAll();
                        const endTime = performance.now();
                        const loadTime = (endTime - startTime).toFixed(0);
                        console.log(`[SYNERGY] ? Loaded ${this.sessions.length} sessions via DataLoader in ${loadTime}ms`);
                    } else {
                        // Fallback: Direct API call if DataLoader not available
                        console.warn('[SYNERGY] DataLoader not available, using direct API call');
                        const response = await fetch(`${this.apiBaseUrl}/api/synergy/sessions/batch`, {
                            method: 'GET',
                            headers: { 'Content-Type': 'application/json' }
                        });

                        if (!response.ok) {
                            throw new Error(`API error: ${response.status}`);
                        }

                        const data = await response.json();
                        if (data.success) {
                            this.sessions = data.sessions || [];
                            const endTime = performance.now();
                            const loadTime = (endTime - startTime).toFixed(0);
                            console.log(`[SYNERGY] ? Batch loaded ${this.sessions.length} sessions in ${loadTime}ms`);
                        } else {
                            throw new Error(data.error || 'Batch load failed');
                        }
                    }

                    // Calculate total internal docs
                    const totalDocs = this.sessions.reduce((sum, s) => sum + (s.internal_docs_count || 0), 0);
                    console.log(`[SYNERGY] Total internal docs: ${totalDocs}`);

                } catch (error) {
                    console.warn('[SYNERGY] API unavailable, using mock data:', error.message);
                    // Fallback to mock data if API is unavailable
                    this.sessions = this.getMockSessions();
                    console.log('[SYNERGY] Mock sessions loaded:', this.sessions.length);
                }
            },

            // DEPRECATED: Old N+1 query pattern (kept for reference)
            // This method was making 1 API call per session, causing 30+ concurrent connections.
            // Now using batch endpoint /api/synergy/sessions/batch instead.
            async loadInternalDocsForSessions_DEPRECATED() {
                console.warn('[INTERNAL DOCS] This method is deprecated - use batch endpoint instead');
                console.log('[INTERNAL DOCS] Loading internal docs for all sessions (N+1 pattern)...');
                const promises = this.sessions.map(async (session) => {
                    try {
                        const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/list/${session.session_id}`, {
                            method: 'GET',
                            headers: {
                                'Content-Type': 'application/json'
                            }
                        });

                        if (response.ok) {
                            const data = await response.json();
                            if (data.success && data.documents && data.documents.length > 0) {
                                // Ensure documents is an array
                                if (!Array.isArray(session.documents)) {
                                    session.documents = [];
                                }

                                // Convert internal docs to document format and add type marker
                                const internalDocs = data.documents.map(doc => ({
                                    doc_id: doc.doc_id,
                                    title: doc.title,
                                    type: 'internal_doc',
                                    doc_type: doc.doc_type || 'richtext',
                                    version: doc.version || 1,
                                    created_at: doc.created_at,
                                    updated_at: doc.updated_at,
                                    slug: doc.slug,
                                    share_url: doc.share_url
                                }));

                                // Merge with existing documents
                                session.documents = [...session.documents, ...internalDocs];
                                console.log(`[INTERNAL DOCS] Loaded ${internalDocs.length} docs for session ${session.session_id}`);
                            }
                        }
                    } catch (error) {
                        console.warn(`[INTERNAL DOCS] Failed to load docs for ${session.session_id}:`, error);
                    }
                });

                await Promise.all(promises);
                console.log('[INTERNAL DOCS] Finished loading all internal docs');
            },

            getMockSessions() {
                return [
                    {
                        session_id: 'sess_20251028_1430_john_email_campaign',
                        title: 'Email Marketing Campaign',
                        description: 'Create and launch Q4 email marketing campaign targeting existing customers with personalized content and A/B testing.',
                        project_name: 'Q4 Marketing',
                        priority: 'high',
                        status: 'active',
                        kanban_column: 'in_progress',
                        message_count: 12,
                        active_docs: 3,
                        pending_steps: 4,
                        last_active: new Date(Date.now() - 2 * 3600000).toISOString(),
                        created_at: new Date(Date.now() - 7 * 86400000).toISOString(),
                        due_date: new Date(Date.now() + 5 * 86400000).toISOString(),
                        assignees: ['John Doe', 'AI Assistant'],
                        tags: ['email', 'marketing', 'campaign'],
                        notes: 'Customer segmentation complete. Need to finalize email templates and set up automation workflow. Target: 10K recipients.',
                        documents: [
                            {
                                title: 'Email Templates Draft',
                                url: 'https://docs.google.com/document/d/abc123',
                                type: 'google_doc',
                                created_at: new Date(Date.now() - 3 * 3600000).toISOString()
                            },
                            {
                                title: 'Customer Segmentation List',
                                url: 'https://sheets.google.com/spreadsheets/d/xyz789',
                                type: 'google_sheet',
                                created_at: new Date(Date.now() - 5 * 3600000).toISOString()
                            },
                            {
                                title: 'Campaign Performance Dashboard',
                                url: 'https://datastudio.google.com/reporting/def456',
                                type: 'dashboard',
                                created_at: new Date(Date.now() - 1 * 3600000).toISOString()
                            }
                        ],
                        links: [
                            { title: 'Campaign Brief', url: 'https://notion.so/campaign-brief', type: 'notion' },
                            { title: 'Design Mockups', url: 'https://figma.com/mockups', type: 'figma' },
                            { title: 'Analytics Dashboard', url: 'https://analytics.google.com/dashboard', type: 'analytics' }
                        ],
                        next_steps: [
                            { description: 'Upload customer CSV', completed: false, due_date: new Date(Date.now() + 1 * 86400000).toISOString() },
                            { description: 'Review email templates', completed: false, due_date: new Date(Date.now() + 2 * 86400000).toISOString() },
                            { description: 'Set up A/B test', completed: false, due_date: new Date(Date.now() + 3 * 86400000).toISOString() },
                            { description: 'Schedule send time', completed: false, due_date: new Date(Date.now() + 4 * 86400000).toISOString() }
                        ],
                        checklist: [
                            { item: 'Customer segmentation', completed: true },
                            { item: 'Email template design', completed: true },
                            { item: 'Copy writing', completed: false },
                            { item: 'Legal review', completed: false },
                            { item: 'QA testing', completed: false }
                        ],
                        recent_activity: [
                            { description: 'Assistant message added', timestamp: new Date(Date.now() - 2 * 3600000).toISOString() },
                            { description: 'Doc created: Customer List Template', timestamp: new Date(Date.now() - 3 * 3600000).toISOString() },
                            { description: 'Next step: Upload customer CSV', timestamp: new Date(Date.now() - 4 * 3600000).toISOString() }
                        ]
                    },
                    {
                        session_id: 'sess_20251028_0900_john_research',
                        title: 'Research Campaign Ideas',
                        description: 'Research and brainstorm Q4 marketing campaign ideas focusing on holiday promotions and customer retention strategies.',
                        project_name: 'Q4 Marketing',
                        priority: 'low',
                        status: 'paused',
                        kanban_column: 'backlog',
                        message_count: 5,
                        active_docs: 1,
                        pending_steps: 2,
                        last_active: new Date(Date.now() - 5 * 86400000).toISOString(),
                        created_at: new Date(Date.now() - 5 * 86400000).toISOString(),
                        due_date: new Date(Date.now() + 10 * 86400000).toISOString(),
                        assignees: ['John Doe'],
                        tags: ['research', 'marketing', 'brainstorm'],
                        notes: 'Focus on holiday themes and customer pain points. Review competitor campaigns from last year.',
                        documents: [
                            {
                                title: 'Research Notes',
                                url: 'https://docs.google.com/document/d/research123',
                                type: 'google_doc',
                                created_at: new Date(Date.now() - 5 * 86400000).toISOString()
                            }
                        ],
                        links: [
                            { title: 'Competitor Analysis', url: 'https://docs.google.com/spreadsheets/competitor', type: 'google_sheet' },
                            { title: 'Industry Report', url: 'https://marketingland.com/industry-report', type: 'external' }
                        ],
                        next_steps: [
                            { description: 'Review competitor campaigns', completed: false, due_date: new Date(Date.now() + 3 * 86400000).toISOString() },
                            { description: 'Conduct customer surveys', completed: false, due_date: new Date(Date.now() + 7 * 86400000).toISOString() }
                        ],
                        checklist: [
                            { item: 'Identify target audience', completed: false },
                            { item: 'Research competitor campaigns', completed: false },
                            { item: 'Brainstorm campaign themes', completed: false }
                        ],
                        recent_activity: [
                            { description: 'Session created', timestamp: new Date(Date.now() - 5 * 86400000).toISOString() }
                        ]
                    },
                    {
                        session_id: 'sess_20251027_1200_john_report',
                        title: 'Report Analysis Dashboard',
                        description: 'Build comprehensive analytics dashboard to visualize Q3 performance metrics and identify trends for Q4 planning.',
                        project_name: 'Analytics',
                        priority: 'medium',
                        status: 'active',
                        kanban_column: 'review',
                        message_count: 8,
                        active_docs: 2,
                        pending_steps: 1,
                        last_active: new Date(Date.now() - 1 * 86400000).toISOString(),
                        created_at: new Date(Date.now() - 3 * 86400000).toISOString(),
                        due_date: new Date(Date.now() + 2 * 86400000).toISOString(),
                        assignees: ['John Doe', 'Data Team'],
                        tags: ['analysis', 'dashboard', 'visualization'],
                        notes: 'Dashboard now includes Plotly charts for sales trends, customer retention, and conversion rates. Ready for stakeholder review.',
                        documents: [
                            {
                                title: 'Q3 Performance Data',
                                url: 'https://sheets.google.com/spreadsheets/q3_data',
                                type: 'google_sheet',
                                created_at: new Date(Date.now() - 2 * 86400000).toISOString()
                            },
                            {
                                title: 'Dashboard Mockups',
                                url: 'https://figma.com/dashboard_mockups',
                                type: 'figma',
                                created_at: new Date(Date.now() - 2 * 86400000).toISOString()
                            }
                        ],
                        links: [
                            { title: 'Plotly Documentation', url: 'https://plotly.com/python/', type: 'documentation' },
                            { title: 'Stakeholder Requirements', url: 'https://notion.so/stakeholder-req', type: 'notion' },
                            { title: 'Live Dashboard Preview', url: 'https://analytics-preview.app', type: 'preview' }
                        ],
                        next_steps: [
                            { description: 'Final stakeholder review', completed: false, due_date: new Date(Date.now() + 2 * 86400000).toISOString() }
                        ],
                        checklist: [
                            { item: 'Data extraction complete', completed: true },
                            { item: 'Plotly charts implemented', completed: true },
                            { item: 'Interactive filters added', completed: true },
                            { item: 'Stakeholder review scheduled', completed: false }
                        ],
                        recent_activity: [
                            { description: 'Plotly chart created', timestamp: new Date(Date.now() - 1 * 86400000).toISOString() },
                            { description: 'Data analysis completed', timestamp: new Date(Date.now() - 1 * 86400000).toISOString() },
                            { description: 'Scheduled review meeting', timestamp: new Date(Date.now() - 1 * 3600000).toISOString() }
                        ]
                    },
                    {
                        session_id: 'sess_20251021_0800_john_api',
                        title: 'API Integration Setup',
                        description: 'Complete REST API integration with third-party payment gateway and customer CRM system. Includes authentication, webhooks, and error handling.',
                        project_name: 'Backend',
                        priority: 'high',
                        status: 'completed',
                        kanban_column: 'done',
                        message_count: 23,
                        active_docs: 5,
                        pending_steps: 0,
                        last_active: new Date(Date.now() - 7 * 86400000).toISOString(),
                        created_at: new Date(Date.now() - 14 * 86400000).toISOString(),
                        due_date: new Date(Date.now() - 7 * 86400000).toISOString(),
                        assignees: ['John Doe', 'Backend Team', 'AI Assistant'],
                        tags: ['api', 'backend', 'integration', 'payment', 'completed'],
                        notes: 'Successfully integrated with Stripe payment API and Salesforce CRM. All unit tests and integration tests passing. Deployed to production without issues. Monitoring metrics show healthy performance.',
                        documents: [
                            {
                                title: 'API Integration Spec',
                                url: 'https://docs.google.com/document/d/api_spec',
                                type: 'google_doc',
                                created_at: new Date(Date.now() - 14 * 86400000).toISOString()
                            },
                            {
                                title: 'Test Results Report',
                                url: 'https://docs.google.com/spreadsheets/test_results',
                                type: 'google_sheet',
                                created_at: new Date(Date.now() - 8 * 86400000).toISOString()
                            },
                            {
                                title: 'Production Deployment Log',
                                url: 'https://github.com/repo/deployment_log',
                                type: 'github',
                                created_at: new Date(Date.now() - 7 * 86400000).toISOString()
                            },
                            {
                                title: 'Performance Monitoring Dashboard',
                                url: 'https://grafana.app/dashboard',
                                type: 'dashboard',
                                created_at: new Date(Date.now() - 7 * 86400000).toISOString()
                            },
                            {
                                title: 'Webhook Configuration',
                                url: 'https://docs.google.com/document/webhook_config',
                                type: 'google_doc',
                                created_at: new Date(Date.now() - 10 * 86400000).toISOString()
                            }
                        ],
                        links: [
                            { title: 'Stripe API Docs', url: 'https://stripe.com/docs/api', type: 'documentation' },
                            { title: 'Salesforce REST API', url: 'https://developer.salesforce.com/docs/api', type: 'documentation' },
                            { title: 'GitHub Pull Request', url: 'https://github.com/repo/pull/123', type: 'github' },
                            { title: 'Production Endpoint', url: 'https://api.production.com/v1', type: 'api' }
                        ],
                        next_steps: [],
                        checklist: [
                            { item: 'Stripe API integration', completed: true },
                            { item: 'Salesforce CRM connection', completed: true },
                            { item: 'Authentication implementation', completed: true },
                            { item: 'Webhook endpoints setup', completed: true },
                            { item: 'Error handling', completed: true },
                            { item: 'Unit tests', completed: true },
                            { item: 'Integration tests', completed: true },
                            { item: 'Production deployment', completed: true },
                            { item: 'Monitoring setup', completed: true }
                        ],
                        recent_activity: [
                            { description: 'All tests passed', timestamp: new Date(Date.now() - 7 * 86400000).toISOString() },
                            { description: 'Deployed to production', timestamp: new Date(Date.now() - 7 * 86400000).toISOString() },
                            { description: 'Monitoring configured', timestamp: new Date(Date.now() - 7 * 86400000).toISOString() },
                            { description: 'Documentation updated', timestamp: new Date(Date.now() - 7 * 86400000).toISOString() }
                        ]
                    }
                ];
            },

            initializeDragula() {
                const containers = [
                    document.getElementById('backlog-cards'),
                    document.getElementById('in_progress-cards'),
                    document.getElementById('review-cards'),
                    document.getElementById('done-cards')
                ];

                this.drake = dragula(containers, {
                    moves: (el, container, handle) => {
                        return el.classList.contains('kanban-card');
                    },
                    accepts: (el, target) => {
                        return target.classList.contains('kanban-cards-container');
                    },
                    invalid: (el, handle) => {
                        return false;
                    },
                    direction: 'vertical',
                    copy: false,
                    copySortSource: false,
                    revertOnSpill: true,
                    removeOnSpill: false,
                    mirrorContainer: document.body
                });

                // Event listeners
                this.drake.on('drop', (el, target, source, sibling) => {
                    this.handleCardDrop(el, target, source);
                });

                console.log('Dragula initialized');
            },

            async renderAllCards() {
                // Save expanded states before clearing
                const expandedCards = new Set();
                document.querySelectorAll('.kanban-card[data-expanded="true"]').forEach(card => {
                    expandedCards.add(card.dataset.sessionId);
                });

                // Clear all containers
                ['backlog', 'in_progress', 'review', 'done'].forEach(column => {
                    const container = document.getElementById(`${column}-cards`);
                    if (container) container.innerHTML = '';
                });

                // Render cards by column
                for (const session of this.sessions) {
                    await this.renderCard(session);
                }

                // Restore expanded states
                expandedCards.forEach(sessionId => {
                    const card = document.querySelector(`.kanban-card[data-session-id="${sessionId}"]`);
                    if (card) {
                        card.dataset.expanded = 'true';
                    }
                });

                // Update column counts
                this.updateColumnCounts();
            },

            renderMarkdown(text) {
                if (!text) return '';

                // Simple markdown parser for common patterns
                let html = text
                    // Bold: **text** or __text__
                    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                    .replace(/__(.+?)__/g, '<strong>$1</strong>')
                    // Italic: *text* or _text_
                    .replace(/\*(.+?)\*/g, '<em>$1</em>')
                    .replace(/_(.+?)_/g, '<em>$1</em>')
                    // Headers: # H1, ## H2, ### H3
                    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
                    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
                    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
                    // Checkboxes: - [ ] unchecked, - [x] checked
                    .replace(/^- \[ \] (.+)$/gm, '<div class="md-checkbox"><input type="checkbox" disabled> <span>$1</span></div>')
                    .replace(/^- \[x\] (.+)$/gm, '<div class="md-checkbox"><input type="checkbox" checked disabled> <span>$1</span></div>')
                    // Bullet lists: - item or * item
                    .replace(/^[\-\*] (.+)$/gm, '<li>$1</li>')
                    // Numbered lists: 1. item
                    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
                    // Emoji shortcuts (common ones)
                    .replace(/:check:/g, '✅')
                    .replace(/:cross:/g, '❌')
                    .replace(/:warning:/g, '⚠️')
                    .replace(/:star:/g, '⭐')
                    .replace(/:rocket:/g, '')
                    // Paragraphs (double line breaks only)
                    .replace(/\n\n/g, '</p><p>');

                // Wrap consecutive <li> tags in <ul>
                html = html.replace(/(<li>.*?<\/li>\s*)+/g, (match) => {
                    return '<ul>' + match + '</ul>';
                });

                // Detect and linkify Synergy session IDs (sess_XXXXX pattern)
                html = html.replace(/\b(sess_[a-zA-Z0-9]{8,})\b/g, (match, sessionId) => {
                    return '<a href="#" class="synergy-internal-link session-id-link" data-session-id="' + sessionId + '" title="Click to open ' + sessionId + '"><i class="fas fa-link" style="margin-right: 4px;"></i>' + sessionId + '</a>';
                });

                // Detect and linkify localhost URLs
                html = html.replace(/(https?:\/\/localhost:[0-9]{4,5}[^\s<]*)/g, (match, url) => {
                    const hasSynergy = url.includes('/synergy/') || url.includes('session=') || url.includes('session_id=');
                    if (hasSynergy) {
                        const sessionIdMatch = url.match(/sess_[a-zA-Z0-9]{8,}/);
                        const sessionId = sessionIdMatch ? sessionIdMatch[0] : null;
                        if (sessionId) {
                            return '<a href="' + url + '" class="synergy-internal-link localhost-link" data-session-id="' + sessionId + '" title="Click to open ' + sessionId + '"><i class="fas fa-external-link-alt" style="margin-right: 4px;"></i>' + url + '</a>';
                        }
                    }
                    return '<a href="' + url + '" class="localhost-link" target="_blank" title="Open in browser">' + url + '</a>';
                });

                // Detect and linkify regular URLs (http/https)
                html = html.replace(/(https?:\/\/[^\s<]+)/g, (match, url) => {
                    if (html.includes('href="' + url + '"')) return match;
                    return '<a href="' + url + '" target="_blank" rel="noopener noreferrer">' + url + '</a>';
                });

                // Wrap in paragraph if no block elements
                if (!html.match(/<(h[1-6]|ul|ol|div)/)) {
                    html = '<p>' + html + '</p>';
                }

                return html;
            },

            initializeLinkInterception() {
                document.addEventListener('click', (e) => {
                    const link = e.target.closest('.synergy-internal-link');
                    if (!link) return;

                    e.preventDefault();
                    e.stopPropagation();

                    const sessionId = link.dataset.sessionId;
                    if (!sessionId) {
                        console.warn('[LINK INTERCEPTION] No session ID found on link:', link);
                        return;
                    }

                    console.log('[LINK INTERCEPTION] Opening Synergy session:', sessionId);

                    if (typeof SynergySidebar !== 'undefined') {
                        SynergySidebar.toggleSidebar();
                        setTimeout(() => {
                            SynergySidebar.expandSessionAsTile(sessionId);
                        }, 200);
                    } else if (typeof synergyBoard !== 'undefined') {
                        synergyBoard.popOutCard(sessionId);
                    } else {
                        console.warn('[LINK INTERCEPTION] No Synergy interface available');
                    }
                });

                console.log('[LINK INTERCEPTION] Initialized link interception for Synergy sessions');
            },

            async renderCard(session) {
                const container = document.getElementById(`${session.kanban_column}-cards`);
                if (!container) return;

                const card = document.createElement('div');
                card.className = 'kanban-card';
                card.dataset.sessionId = session.session_id;
                card.dataset.expanded = 'false';

                // Add double-click event listener to expand/collapse card
                card.addEventListener('dblclick', (e) => {
                    e.preventDefault();
                    this.toggleCardExpand(session.session_id);
                });

                // DRAG-DROP: Add drop zone listeners to the card itself
                card.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    card.classList.add('drag-over');
                });

                card.addEventListener('dragleave', (e) => {
                    // Only remove if leaving the card entirely (not child elements)
                    if (!card.contains(e.relatedTarget)) {
                        card.classList.remove('drag-over');
                    }
                });

                card.addEventListener('drop', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    card.classList.remove('drag-over');
                    this.handleThreadDrop(e, session.session_id);
                });

                const priorityEmoji = {
                    'low': '<i class="fas fa-circle" style="color: #22c55e;"></i>',
                    'medium': '<i class="fas fa-circle" style="color: #fbbf24;"></i>',
                    'high': '<i class="fas fa-circle" style="color: #ef4444;"></i>',
                    'critical': '<i class="fas fa-exclamation-circle" style="color: #dc2626;"></i>'
                }[session.priority] || '<i class="fas fa-circle" style="color: #9ca3af;"></i>';

                const statusClass = {
                    'active': 'status-active',
                    'paused': 'status-paused',
                    'completed': 'status-completed'
                }[session.status] || 'status-active';

                const timeAgo = this.formatTimeAgo(session.last_active);

                // Collapsed view (default)
                let collapsedHTML = this.renderCardCollapsed(session, priorityEmoji, statusClass, timeAgo);

                // Expanded view - AWAIT the async function
                let expandedHTML = await this.renderCardExpanded(session, priorityEmoji, statusClass, timeAgo);

                card.innerHTML = `
                                                                                                                                        ${collapsedHTML}
                                                                                                                                        ${expandedHTML}
                                                                                                                                        `;

                // Add card to DOM first (before triggering any transitions)
                container.appendChild(card);

                // Force browser reflow to prevent FOUC (Flash of Unstyled Content)
                // This ensures the card is fully rendered before any CSS transitions apply
                void card.offsetHeight;

                // DRAG-DROP INTEGRATION: Drop zone is handled by inline HTML attributes
                // See line ~28925: ondrop="synergyBoard.handleThreadDrop(event, '${session.session_id}')"
                // This ensures drop works on both collapsed and expanded cards

                // SYNERGY INTEGRATION: Load linked threads asynchronously
                const threadIds = this.parseJsonField(session.thread_ids, []);
                const threadsSection = document.getElementById(`threads-section-${session.session_id}`);
                const loadingDiv = threadsSection ? threadsSection.querySelector('.thread-list-loading') : null;

                if (threadIds.length > 0 && threadsSection) {
                    // Show a spinner while we load (only when there are thread IDs)
                    if (loadingDiv) {
                        loadingDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading linked threads...';
                    }

                    this.renderLinkedThreads(threadIds).then(threadsHTML => {
                        if (threadsSection) {
                            // Replace the placeholder with the rendered threads list
                            if (loadingDiv) {
                                loadingDiv.outerHTML = threadsHTML;
                            } else {
                                threadsSection.insertAdjacentHTML('beforeend', threadsHTML);
                            }
                        }
                    }).catch(err => {
                        console.warn('[WARN] Failed to load linked threads', err);
                        if (loadingDiv) {
                            loadingDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> Failed to load linked threads';
                        }
                    });
                } else if (loadingDiv) {
                    // No linked threads: show drag-and-drop prompt
                    loadingDiv.innerHTML = '<i class="fas fa-hand-pointer"></i> Drag and drop a thread here to link';
                    loadingDiv.classList.add('drop-zone-prompt');
                }
            },

            renderCardCollapsed(session, priorityEmoji, statusClass, timeAgo) {
                // Parse JSON fields safely - ensure arrays with fallback wrapper
                let tags = this.parseJsonField(session.tags, []);
                let nextSteps = this.parseJsonField(session.next_steps, []);
                let documents = this.parseJsonField(session.documents, []);

                // ? NEW: Merge batch-loaded internal_docs with existing documents
                const internalDocs = session.internal_docs || [];
                if (internalDocs.length > 0) {
                    documents = [...documents, ...internalDocs];
                }

                // Force to array if parseJsonField failed
                if (!Array.isArray(nextSteps)) {
                    console.warn('[WARN] nextSteps not array, forcing to empty array. Type:', typeof nextSteps);
                    nextSteps = [];
                }
                if (!Array.isArray(documents)) {
                    console.warn('[WARN] documents not array, forcing to empty array. Type:', typeof documents);
                    documents = [];
                }
                if (!Array.isArray(tags)) {
                    console.warn('[WARN] tags not array, forcing to empty array. Type:', typeof tags);
                    tags = [];
                }

                let tagsHTML = '';
                if (Array.isArray(tags) && tags.length > 0) {
                    tagsHTML = `
                        <div class="card-tags">
                            ${tags.slice(0, 3).map(tag => `
                                <span class="card-tag">${this.escapeHtml(tag)}</span>
                            `).join('')}
                        </div>
                    `;
                }

                return `
                                                                                                                                        <div class="card-collapsed-view">
                                                                                                                                            <div class="card-header">
                                                                                                                                                <span class="card-priority">${priorityEmoji}</span>
                                                                                                                                                <div class="card-header-actions">
                                                                                                                                                    <button class="card-action-icon" onclick="event.stopPropagation(); synergyBoard.toggleCardExpand('${this.escapeJs(session.session_id)}')" title="Expand">
                                                                                                                                                        <i class="fas fa-expand-alt"></i>
                                                                                                                                                    </button>
                                                                                                                                                    <button class="card-action-icon popout" onclick="event.stopPropagation(); synergyBoard.popOutCard('${this.escapeJs(session.session_id)}')" title="Pop Out">
                                                                                                                                                        <i class="fas fa-external-link-alt"></i>
                                                                                                                                                    </button>
                                                                                                                                                    <button class="card-action-icon resume" onclick="event.stopPropagation(); synergyBoard.resumeSession('${this.escapeJs(session.session_id)}')" title="Resume">
                                                                                                                                                        <i class="fas fa-play"></i>
                                                                                                                                                    </button>
                                                                                                                                                    <button class="card-action-icon edit" onclick="event.stopPropagation(); synergyBoard.editCard('${this.escapeJs(session.session_id)}')" title="Edit">
                                                                                                                                                        <i class="fas fa-edit"></i>
                                                                                                                                                    </button>
                                                                                                                                                    <button class="card-action-icon delete" onclick="event.stopPropagation(); synergyBoard.deleteCard('${this.escapeJs(session.session_id)}')" title="Delete">
                                                                                                                                                        <i class="fas fa-trash"></i>
                                                                                                                                                    </button>
                                                                                                                                                </div>
                                                                                                                                            </div>

                                                                                                                                            <div class="card-title">${this.escapeHtml(session.title)}</div>

                                                                                                                                            <div class="card-meta">
                                                                                                                                                <div class="card-project">
                                                                                                                                                    <i class="fas fa-folder"></i>
                                                                                                                                                    ${this.escapeHtml(session.project_name || 'No Project')}
                                                                                                                                                </div>
                                                                                                                                                <div class="card-status-row">
                                                                                                                                                    <span class="status-badge ${statusClass}">${session.status}</span>
                                                                                                                                                    <span class="card-time">${timeAgo}</span>
                                                                                                                                                </div>
                                                                                                                                            </div>

                                                                                                                                            <div class="card-stats">
                                                                                                                                                <span class="card-stat">
                                                                                                                                                    <i class="fas fa-comments"></i> ${session.message_count || 0}
                                                                                                                                                </span>
                                                                                                                                                <span class="card-stat">
                                                                                                                                                    <i class="fas fa-file"></i> ${Array.isArray(documents) ? documents.length : 0}
                                                                                                                                                </span>
                                                                                                                                                <span class="card-stat">
                                                                                                                                                    <i class="fas fa-tasks"></i> ${Array.isArray(nextSteps) ? nextSteps.filter(s => s && !s.completed).length : 0}
                                                                                                                                                </span>
                                                                                                                                            </div>

                                                                                                                                            <div class="card-footer">
                                                                                                                                                <span class="card-session-id">${session.session_id}</span>
                                                                                                                                                ${tagsHTML}
                                                                                                                                            </div>
                                                                                                                                        </div>
                                                                                                                                        `;
            },

            addCard(column) {
                this.createNewSession();
            },

            columnMenu(column) {
                console.log(' Column menu:', column);
                // Could add: Clear column, Sort by, etc.
            },

            openCardMenu(sessionId) {
                console.log(' Card menu:', sessionId);
                // Could add: Edit, Delete, Archive, etc.
            },

            async renderCardExpanded(session, priorityEmoji, statusClass, timeAgo, milestones = null) {
                // Parse JSON fields safely
                let documents = this.parseJsonField(session.documents, []);
                const links = this.parseJsonField(session.links, []);
                const nextSteps = this.parseJsonField(session.next_steps, []);
                const assignees = this.parseJsonField(session.assignees, []);
                const tags = this.parseJsonField(session.tags, []);
                const recentActivity = this.parseJsonField(session.recent_activity, []);
                const checklist = this.parseJsonField(session.checklist, []);

                // ? NEW: Merge batch-loaded internal_docs with existing documents
                const internalDocs = session.internal_docs || [];
                if (internalDocs.length > 0) {
                    documents = [...documents, ...internalDocs];
                }

                // ? MILESTONE SYSTEM: Render milestones if available
                let milestonesHTML = '';
                if (milestones && milestones.length > 0) {
                    const completedCount = milestones.filter(m => m.completed).length;
                    milestonesHTML = `
                        <div class="card-section milestone-section">
                            <div class="section-title">
                                <span><i class="fas fa-flag-checkered"></i> Milestones (${completedCount}/${milestones.length})</span>
                            </div>
                            <div class="milestones-list" style="display: flex; flex-direction: column; gap: 12px;">
                                ${milestones.map((milestone, idx) => this.renderMilestone(milestone, idx + 1, session.session_id)).join('')}
                            </div>
                        </div>
                    `;
                }

                // Documents - Always show section, filter empty items
                let docsHTML = '';
                const validDocuments = Array.isArray(documents) ? documents.filter(doc => doc && doc.title && doc.title.trim() !== '') : [];

                docsHTML = `
                    <div class="card-section">
                        <div class="section-title">
                            <span><i class="fas fa-folder-open"></i> Project Documents ${validDocuments.length > 0 ? `(${validDocuments.length})` : ''}</span>
                            <div class="section-actions">
                                <button class="btn-section-action" onclick="event.stopPropagation(); window.internalDocsManager.createInternalDoc('${session.session_id}')" title="Create Internal Document">
                                    <i class="fas fa-plus"></i>
                                </button>
                                <button class="btn-section-action" onclick="event.stopPropagation(); window.internalDocsManager.attachExistingDoc('${session.session_id}')" title="Attach Existing Document">
                                    <i class="fas fa-paperclip"></i>
                                </button>
                            </div>
                        </div>
                        <div class="document-list">
                            ${validDocuments.length > 0 ? validDocuments.map((doc, idx) => {
                    const displayNumber = idx + 1;

                    // Handle internal docs differently
                    if (doc.type === 'internal_doc') {
                        return `
                            <div class="document-item internal-doc-item" ondblclick="event.stopPropagation(); window.internalDocsManager.openInternalDocPopup('${doc.doc_id}', '${session.session_id}')">
                                <span class="item-number">D${displayNumber}</span>
                                <i class="fas fa-${doc.doc_type === 'spreadsheet' ? 'table' : 'file-alt'}"></i>
                                <div class="doc-info" style="cursor: pointer;" onclick="event.stopPropagation(); window.internalDocsManager.openInternalDocPopup('${doc.doc_id}', '${session.session_id}')" title="Click to open ${this.escapeHtml(doc.title)}">
                                    <span class="doc-name" style="cursor: pointer;">${this.escapeHtml(doc.title)}</span>
                                    <span class="doc-type">${doc.doc_type === 'spreadsheet' ? 'Spreadsheet' : 'Document'} (v${doc.version || 1})</span>
                                    ${doc.preview ? `<span class="doc-preview">${this.escapeHtml(doc.preview)}</span>` : ''}
                                </div>
                                <button class="doc-link internal-doc-btn" onclick="event.stopPropagation(); window.internalDocsManager.openInternalDocPopup('${doc.doc_id}', '${session.session_id}')" title="Open internal document">
                                    <i class="fas fa-edit"></i>
                                </button>
                            </div>
                        `;
                    } else {
                        // External doc (existing code)
                        const typeLabels = {
                            'google_doc': 'Google Doc',
                            'google_sheet': 'Google Sheet',
                            'google_slides': 'Google Slides',
                            'google_form': 'Google Form',
                            'word': 'Word',
                            'excel': 'Excel',
                            'powerpoint': 'PowerPoint',
                            'onenote': 'OneNote',
                            'pdf': 'PDF',
                            'dashboard': 'Dashboard',
                            'spreadsheet': 'Spreadsheet',
                            'presentation': 'Presentation',
                            'file': 'File'
                        };
                        const typeLabel = typeLabels[doc.type] || doc.type || 'File';
                        return `
                            <div class="document-item">
                                <span class="item-number">D${displayNumber}</span>
                                <i class="fas fa-file-alt"></i>
                                <div class="doc-info">
                                    <span class="doc-name">${this.escapeHtml(doc.title || 'Untitled')}</span>
                                    <span class="doc-type">${typeLabel}</span>
                                </div>
                                ${doc.url ? `<a href="${this.escapeHtml(doc.url)}" target="_blank" class="doc-link" title="Open document">
                                    <i class="fas fa-external-link-alt"></i>
                                </a>` : ''}
                            </div>
                        `;
                    }
                }).join('') : '<div class="document-item" style="opacity: 0.6; font-style: italic;">No documents added</div>'}
                        </div>
                    </div>
                `;

                // Links
                let linksHTML = '';
                if (Array.isArray(links) && links.length > 0) {
                    linksHTML = `
                        <div class="card-section">
                            <div class="section-title"><i class="fas fa-external-link-alt"></i> Project Links (${links.length})</div>
                            <div class="link-list">
                                ${links.map((link, idx) => {
                        const displayNumber = idx + 1;
                        return `
                                    <div class="link-item">
                                        <span class="item-number">L${displayNumber}</span>
                                        <i class="fas fa-external-link-alt"></i>
                                        <a href="${link.url}" target="_blank" class="link-url">
                                            ${this.escapeHtml(link.title)}
                                        </a>
                                        <span class="link-type">${link.type}</span>
                                    </div>
                                `;
                    }).join('')}
                            </div>
                        </div>
                    `;
                }

                // Milestones - Tiered structure (replaces Next Steps and Checklist)
                const sessionMilestones = this.parseJsonField(session.milestones, []);
                const completedMilestones = sessionMilestones.filter(m => m && m.completed).length;

                const tieredMilestonesHTML = `
                                                                                                                                        <div class="card-section">
                                                                                                                                            <div class="section-title">
                                                                                                                                                <i class="fas fa-flag-checkered"></i> 
                                                                                                                                                Milestones ${sessionMilestones.length > 0 ? `(${completedMilestones}/${sessionMilestones.length})` : ''}
                                                                                                                                            </div>
                                                                                                                                            <div class="milestones-list">
                                                                                                                                                ${sessionMilestones.length > 0 ? sessionMilestones.map((milestone, idx) => {
                    const displayNumber = idx + 1;
                    const milestoneTitle = milestone.title || milestone.name || 'Untitled Milestone';
                    const milestoneDesc = milestone.description || '';
                    const tasks = milestone.tasks || [];
                    const completedTasks = tasks.filter(t => t.completed).length;
                    const tier = milestone.tier || 1;

                    const tierColors = {
                        1: { bg: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%)', badge: '#dc2626', text: 'Critical' },
                        2: { bg: 'linear-gradient(135deg, #ffd93d 0%, #f6c700 100%)', badge: '#d97706', text: 'Important' },
                        3: { bg: 'linear-gradient(135deg, #6bcf7f 0%, #51b368 100%)', badge: '#16a34a', text: 'Standard' }
                    };
                    const tierStyle = tierColors[tier] || tierColors[3];

                    let milestoneHtml = `
                                        <div class="milestone-item" style="margin-bottom: 16px; border: 1px solid var(--border-color); border-radius: 8px; overflow: hidden; background: var(--bg-tertiary);">
                                            <div class="milestone-header" style="display: flex; align-items: center; gap: 10px; padding: 12px; background: var(--bg-quaternary); border-bottom: 1px solid var(--border-color);">
                                                <span class="item-number" style="display: inline-flex; align-items: center; justify-content: center; min-width: 36px; height: 28px; background: ${tierStyle.bg}; color: white; font-weight: 700; border-radius: 6px; font-size: 11px; padding: 0 10px;">M${displayNumber}</span>
                                                <input type="checkbox" 
                                                    ${milestone.completed ? 'checked' : ''}
                                                    onchange="event.stopPropagation(); synergyBoard.toggleMilestone('${this.escapeJs(session.session_id)}', ${idx});"
                                                    style="cursor: pointer;">
                                                <div style="flex: 1;">
                                                    <div class="milestone-title" style="font-weight: 600; font-size: 14px; ${milestone.completed ? 'text-decoration: line-through; opacity: 0.6;' : ''}">
                                                        ${this.escapeHtml(milestoneTitle)}
                                                    </div>
                                                    ${milestoneDesc ? `<div class="milestone-desc" style="font-size: 12px; color: var(--text-muted); margin-top: 3px;">${this.escapeHtml(milestoneDesc)}</div>` : ''}
                                                </div>
                                                <span class="tier-badge" style="font-size: 10px; padding: 4px 10px; background: ${tierStyle.badge}; color: white; border-radius: 12px; font-weight: 600; white-space: nowrap;">${tierStyle.text}</span>
                                                ${milestone.due_date ? `<span class="milestone-due" style="font-size: 11px; color: var(--text-muted);"><i class="fas fa-calendar"></i> ${new Date(milestone.due_date).toLocaleDateString()}</span>` : ''}
                                            </div>
                                            
                                            ${tasks.length > 0 ? `
                                            <div class="milestone-tasks" style="padding: 10px;">
                                                <div class="tasks-header" style="font-size: 11px; color: var(--text-muted); margin-bottom: 8px; font-weight: 600; padding-left: 4px;">
                                                    <i class="fas fa-tasks"></i> Tasks (${completedTasks}/${tasks.length})
                                                </div>
                                                ${tasks.map((task, taskIdx) => {
                        const taskNumber = `${displayNumber}.${taskIdx + 1}`;
                        const taskText = task.title || task.description || task.text || 'Untitled Task';
                        return `
                                                    <div class="task-item" style="display: flex; align-items: flex-start; gap: 8px; padding: 8px; margin-bottom: 6px; background: var(--bg-secondary); border-radius: 6px;">
                                                        <span class="sub-number" style="display: inline-block; min-width: 42px; padding: 3px 8px; background: #f0f0f0; border: 1px solid #ddd; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 9px; color: #666; text-align: center; font-weight: 600;">T${taskNumber}</span>
                                                        <input type="checkbox" 
                                                            ${task.completed ? 'checked' : ''}
                                                            onchange="event.stopPropagation(); synergyBoard.toggleMilestoneTask('${this.escapeJs(session.session_id)}', ${idx}, ${taskIdx});"
                                                            style="margin-top: 2px; cursor: pointer;">
                                                        <span style="flex: 1; font-size: 13px; ${task.completed ? 'text-decoration: line-through; opacity: 0.6;' : ''}">
                                                            ${this.escapeHtml(taskText)}
                                                        </span>
                                                        ${task.assignee ? `<span style="font-size: 11px; color: var(--text-muted);"><i class="fas fa-user"></i> ${this.escapeHtml(task.assignee)}</span>` : ''}
                                                    </div>
                                                    `;
                    }).join('')}
                                            </div>
                                            ` : ''}
                                        </div>
                                    `;
                    return milestoneHtml;
                }).join('') : '<div class="milestone-item" style="opacity: 0.6; font-style: italic; padding: 12px;"><i class="fas fa-info-circle"></i> No milestones added</div>'}
                                                                                                                                            </div>
                                                                                                                                        </div>
                                                                                                                                        `;

                // Assignees
                let assigneesHTML = '';
                if (assignees && assignees.length > 0) {
                    assigneesHTML = `
                        <div class="card-assignees">
                            <i class="fas fa-users"></i>
                            ${assignees.join(', ')}
                        </div>
                    `;
                }

                // Dates
                let datesHTML = '';
                if (session.due_date) {
                    const dueDate = new Date(session.due_date);
                    const isOverdue = dueDate < new Date();
                    datesHTML = `
                                                                                                                                        <div class="card-dates">
                                                                                                                                            <span class="date-item ${isOverdue ? 'overdue' : ''}">
                                                                                                                                                <i class="fas fa-calendar"></i>
                                                                                                                                                Due: ${dueDate.toLocaleDateString()}
                                                                                                                                            </span>
                                                                                                                                        </div>
                                                                                                                                        `;
                }

                return `
                                                                                                                                        <div class="card-expanded-view">
                                                                                                                                        <div class="card-header">
                                                                                                                                            <span class="card-priority">${priorityEmoji}</span>
                                                                                                                                            <div class="card-header-actions">
                                                                                                                                                <button class="card-action-icon" onclick="event.stopPropagation(); synergyBoard.toggleCardExpand('${this.escapeJs(session.session_id)}')" title="Collapse">
                                                                                                                                                    <i class="fas fa-compress-alt"></i>
                                                                                                                                                </button>
                                                                                                                                                <button class="card-action-icon popout" onclick="event.stopPropagation(); synergyBoard.popOutCard('${this.escapeJs(session.session_id)}')" title="Pop Out">
                                                                                                                                                    <i class="fas fa-external-link-alt"></i>
                                                                                                                                                </button>
                                                                                                                                                <button class="card-action-icon resume" onclick="event.stopPropagation(); synergyBoard.resumeSession('${this.escapeJs(session.session_id)}')" title="Resume">
                                                                                                                                                    <i class="fas fa-play"></i>
                                                                                                                                                </button>
                                                                                                                                                <button class="card-action-icon edit" onclick="event.stopPropagation(); synergyBoard.popOutCard('${this.escapeJs(session.session_id)}'); setTimeout(() => { const popout = Array.from(document.querySelectorAll('.popout-card-window')).find(w => w.dataset.sessionId === '${this.escapeJs(session.session_id)}'); if (popout) synergyBoard.togglePopupEdit(popout.id, '${this.escapeJs(session.session_id)}'); }, 100);" title="Edit (opens in popup)">
                                                                                                                                                    <i class="fas fa-edit"></i>
                                                                                                                                                </button>
                                                                                                                                                <button class="card-action-icon delete" onclick="event.stopPropagation(); synergyBoard.deleteCard('${this.escapeJs(session.session_id)}')" title="Delete">
                                                                                                                                                    <i class="fas fa-trash"></i>
                                                                                                                                                </button>
                                                                                                                                            </div>
                                                                                                                                        </div>                                                                                                                                            <div class="card-title-large">${this.escapeHtml(session.title)}</div>

                                                                                                                                            ${session.description ? `
                            <div class="card-description markdown-content">
                                <div class="section-title"><i class="fas fa-align-left"></i> Description</div>
                                <div class="description-text">${this.renderMarkdown(session.description)}</div>
                            </div>
                        ` : ''}

                                                                                                                                            <div class="card-meta-expanded">
                                                                                                                                                <div class="card-project">
                                                                                                                                                    <i class="fas fa-folder"></i>
                                                                                                                                                    ${this.escapeHtml(session.project_name || 'No Project')}
                                                                                                                                                </div>
                                                                                                                                                <span class="status-badge ${statusClass}">${session.status}</span>
                                                                                                                                                <span class="card-time"><i class="fas fa-clock"></i> ${timeAgo}</span>
                                                                                                                                            </div>

                                                                                                                                            ${assigneesHTML}
                                                                                                                                            ${datesHTML}

                                                                                                                                            ${docsHTML}
                                                                                                                                            ${linksHTML}
                                                                                                                                            ${tieredMilestonesHTML}
                                                                                                                                            ${milestonesHTML}

                                                                                                                                            

                                                                                                                                            ${session.notes ? `
                            <div class="card-section">
                                <div class="section-title"><i class="fas fa-sticky-note"></i> Notes</div>
                                <div class="card-notes">${this.escapeHtml(session.notes)}</div>
                            </div>
                        ` : ''}

                                                                                                                                            <div class="card-section" 
                                                                                                                                                 id="threads-section-${session.session_id}"
                                                                                                                                                 data-synergy-id="${session.session_id}">
                                                                                                                                                <div class="section-title"><i class="fas fa-comments"></i> Linked Threads</div>
                                                                                                                                                <div class="thread-list-loading">
                                                                                                                                                    <i class="fas fa-spinner fa-spin"></i> Loading linked threads...
                                                                                                                                                </div>
                                                                                                                                            </div>

                                                                                                                                            <div class="card-section">
                                                                                                                                                <div class="section-title"><i class="fas fa-history"></i> Activity Log</div>
                                                                                                                                                <div class="activity-log">
                                                                                                                                                    ${recentActivity && recentActivity.length > 0 ? recentActivity.map(activity => `
                                    <div class="activity-log-item">
                                        • ${this.escapeHtml(activity.description)}
                                        <span class="activity-time">${this.formatTimeAgo(activity.timestamp)}</span>
                                    </div>
                                `).join('') : '<div class="activity-log-item">No activity yet</div>'}
                                                                                                                                                </div>
                                                                                                                                            </div>

                                                                                                                                            <div class="card-footer-expanded">
                                                                                                                                                <div class="card-tags">
                                                                                                                                                    ${tags && tags.length > 0 ? tags.map(tag => `
                                    <span class="card-tag">${this.escapeHtml(tag)}</span>
                                `).join('') : ''}
                                                                                                                                                </div>
                                                                                                                                                <span class="card-session-id-full">${session.session_id}</span>
                                                                                                                                            </div>

                                                                                                                                            <div class="card-actions-expanded">
                                                                                                                                                <button class="card-action-icon" onclick="event.stopPropagation(); synergyBoard.toggleCardExpand('${this.escapeJs(session.session_id)}')" title="Collapse">
                                                                                                                                                    <i class="fas fa-compress-alt"></i>
                                                                                                                                                </button>
                                                                                                                                                <button class="card-action-icon popout" onclick="event.stopPropagation(); synergyBoard.popOutCard('${this.escapeJs(session.session_id)}')" title="Pop Out">
                                                                                                                                                    <i class="fas fa-external-link-alt"></i>
                                                                                                                                                </button>
                                                                                                                                                <button class="card-action-icon resume" onclick="event.stopPropagation(); synergyBoard.resumeSession('${this.escapeJs(session.session_id)}')" title="Resume">
                                                                                                                                                    <i class="fas fa-play"></i>
                                                                                                                                                </button>
                                                                                                                                                <button class="card-action-icon edit" onclick="event.stopPropagation(); synergyBoard.toggleCardInlineEdit('${this.escapeJs(session.session_id)}')" title="Edit Inline">
                                                                                                                                                    <i class="fas fa-pen"></i>
                                                                                                                                                </button>
                                                                                                                                                <button class="card-action-icon delete" onclick="event.stopPropagation(); synergyBoard.deleteCard('${this.escapeJs(session.session_id)}')" title="Delete">
                                                                                                                                                    <i class="fas fa-trash"></i>
                                                                                                                                                </button>
                                                                                                                                            </div>
                                                                                                                                        </div>
                                                                                                                                        `;
            },

            renderCardExpandedEditable(session, priorityEmoji, statusClass, timeAgo) {
                // Parse JSON fields safely
                const documents = this.parseJsonField(session.documents, []);
                const links = this.parseJsonField(session.links, []);
                const nextSteps = this.parseJsonField(session.next_steps, []);
                const assignees = this.parseJsonField(session.assignees, []);
                const tags = this.parseJsonField(session.tags, []);
                const threadIds = this.parseJsonField(session.thread_ids, []);
                const assignedAgents = this.parseJsonField(session.assigned_agents, []);

                return `
                    <div class="card-expanded-view editable-mode">
                        <div class="card-header">
                            <span class="card-priority">${priorityEmoji}</span>
                            <div class="edit-mode-badge">
                                <i class="fas fa-edit"></i> EDITING
                            </div>
                        </div>

                        <!-- Title (Editable) -->
                        <div class="form-group">
                            <label><i class="fas fa-heading"></i> Title</label>
                            <input type="text" class="form-control edit-field-title" value="${this.escapeHtml(session.title || '')}" placeholder="Enter title">
                        </div>

                        <!-- Description (Editable) -->
                        <div class="form-group">
                            <label><i class="fas fa-align-left"></i> Description</label>
                            <textarea class="form-control edit-field-description" rows="3" placeholder="Enter description">${this.escapeHtml(session.description || '')}</textarea>
                        </div>

                        <!-- Project & Priority Row -->
                        <div class="form-row">
                            <div class="form-group">
                                <label><i class="fas fa-folder"></i> Project</label>
                                <input type="text" class="form-control edit-field-project" value="${this.escapeHtml(session.project_name || '')}" placeholder="Project name">
                            </div>
                            <div class="form-group">
                                <label><i class="fas fa-flag"></i> Priority</label>
                                <select class="form-control edit-field-priority">
                                    <option value="low" ${session.priority === 'low' ? 'selected' : ''}>Low</option>
                                    <option value="medium" ${session.priority === 'medium' ? 'selected' : ''}>Medium</option>
                                    <option value="high" ${session.priority === 'high' ? 'selected' : ''}>High</option>
                                    <option value="critical" ${session.priority === 'critical' ? 'selected' : ''}>Critical</option>
                                </select>
                            </div>
                        </div>

                        <!-- Status & Column Row -->
                        <div class="form-row">
                            <div class="form-group">
                                <label><i class="fas fa-circle"></i> Status</label>
                                <select class="form-control edit-field-status">
                                    <option value="active" ${session.status === 'active' ? 'selected' : ''}>Active</option>
                                    <option value="paused" ${session.status === 'paused' ? 'selected' : ''}>Paused</option>
                                    <option value="completed" ${session.status === 'completed' ? 'selected' : ''}>Completed</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label><i class="fas fa-columns"></i> Column</label>
                                <select class="form-control edit-field-column">
                                    <option value="backlog" ${session.kanban_column === 'backlog' ? 'selected' : ''}>Backlog</option>
                                    <option value="in_progress" ${session.kanban_column === 'in_progress' ? 'selected' : ''}>In Progress</option>
                                    <option value="review" ${session.kanban_column === 'review' ? 'selected' : ''}>Review</option>
                                    <option value="done" ${session.kanban_column === 'done' ? 'selected' : ''}>Done</option>
                                </select>
                            </div>
                        </div>

                        <!-- Due Date & Due Time Row -->
                        <div class="form-row">
                            <div class="form-group">
                                <label><i class="fas fa-calendar"></i> Due Date</label>
                                <input type="date" class="form-control edit-field-due-date" value="${session.due_date ? new Date(session.due_date).toISOString().split('T')[0] : ''}">
                            </div>
                            <div class="form-group">
                                <label><i class="fas fa-clock"></i> Due Time</label>
                                <input type="time" class="form-control edit-field-due-time" value="${session.due_time || ''}">
                            </div>
                        </div>

                        <!-- Assignees -->
                        <div class="form-group">
                            <label><i class="fas fa-users"></i> Assignees (comma-separated)</label>
                            <input type="text" class="form-control edit-field-assignees" value="${assignees.join(', ')}" placeholder="John, Sarah, AI">
                        </div>

                        <!-- Tags -->
                        <div class="form-group">
                            <label><i class="fas fa-tags"></i> Tags (comma-separated)</label>
                            <input type="text" class="form-control edit-field-tags" value="${tags.join(', ')}" placeholder="marketing, urgent, backend">
                        </div>

                        <!-- Thread IDs -->
                        <div class="form-group">
                            <label><i class="fas fa-comments"></i> Thread IDs (comma-separated)</label>
                            <input type="text" class="form-control edit-field-thread-ids" value="${threadIds.join(', ')}" placeholder="thread_abc123, thread_def456">
                        </div>

                        <!-- Assigned Agents -->
                        <div class="form-group">
                            <label><i class="fa-solid fa-atom"></i> Assigned Agents (comma-separated)</label>
                            <input type="text" class="form-control edit-field-assigned-agents" value="${assignedAgents.join(', ')}" placeholder="Research Agent, Email Agent">
                        </div>

                        <!-- Notes -->
                        <div class="form-group">
                            <label><i class="fas fa-sticky-note"></i> Notes</label>
                            <textarea class="form-control edit-field-notes" rows="4" placeholder="Additional context and updates">${this.escapeHtml(session.notes || '')}</textarea>
                        </div>

                        <!-- Read-only sections (not editable in popup) -->
                        <div class="readonly-sections">
                            <div class="info-message">
                                <i class="fas fa-info-circle"></i> Documents, links, next steps, and checklists can be edited after saving.
                            </div>
                        </div>

                        <div class="card-footer-expanded">
                            <span class="card-session-id-full">${session.session_id}</span>
                        </div>
                    </div>
                `;
            },

            async handleCardDrop(el, target, source) {
                const sessionId = el.dataset.sessionId;
                const newColumn = target.dataset.column;
                const oldColumn = source.dataset.column;

                if (newColumn === oldColumn) return;

                console.log(` Card moved: ${sessionId} → ${newColumn}`);

                // Show sync indicator
                this.showSyncIndicator('syncing', 'Syncing to database...');

                try {
                    // Update local session data
                    const session = this.sessions.find(s => s.session_id === sessionId);
                    if (session) {
                        session.kanban_column = newColumn;

                        // Update status based on column
                        const statusMap = {
                            'backlog': 'paused',
                            'in_progress': 'active',
                            'review': 'active',
                            'done': 'completed'
                        };
                        session.status = statusMap[newColumn] || 'active';
                    }

                    // Simulate API call (replace with actual API call)
                    await this.updateSessionColumn(sessionId, newColumn);

                    // Update UI
                    this.updateColumnCounts();
                    this.updateStats();

                    // Show success
                    this.showSyncIndicator('success', 'Synced successfully!', 2000);

                } catch (error) {
                    console.error(' Sync failed:', error);
                    this.showSyncIndicator('error', 'Sync failed - please try again', 3000);

                    // Revert on error
                    source.appendChild(el);
                }
            },

            async updateSessionColumn(sessionId, newColumn) {
                try {
                    console.log(` Updating ${sessionId} column to ${newColumn}...`);
                    const response = await fetch(`${this.apiBaseUrl}/api/synergy/${sessionId}/column`, {
                        method: 'PATCH',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ column: newColumn })
                    });

                    if (!response.ok) {
                        throw new Error(`API error: ${response.status}`);
                    }

                    const result = await response.json();
                    console.log(`Updated ${sessionId} to ${newColumn}`);

                    // Broadcast update via WebSocket
                    this.broadcastUpdate('column_change', { sessionId, newColumn });

                    return result;
                } catch (error) {
                    console.error(' Failed to update column:', error);
                    // Continue with local update even if API fails
                    return { success: false, error: error.message };
                }
            },

            updateColumnCounts() {
                ['backlog', 'in_progress', 'review', 'done'].forEach(column => {
                    const container = document.getElementById(`${column}-cards`);
                    const countEl = document.querySelector(`.column-count[data-column="${column}"]`);
                    if (container && countEl) {
                        const count = container.querySelectorAll('.kanban-card').length;
                        countEl.textContent = count;
                    }
                });
            },

            updateStats() {
                const totalEl = document.getElementById('total-sessions');
                const activeEl = document.getElementById('active-sessions');
                const completedEl = document.getElementById('completed-sessions');

                if (totalEl) totalEl.textContent = this.sessions.length;
                if (activeEl) {
                    const activeCount = this.sessions.filter(s => s.status === 'active').length;
                    activeEl.textContent = activeCount;
                }
                if (completedEl) {
                    const completedCount = this.sessions.filter(s => s.status === 'completed').length;
                    completedEl.textContent = completedCount;
                }
            },

            // ==================== REAL-TIME WEBSOCKET UPDATE METHODS ====================

            /**
             * Add new session card in real-time (WebSocket event handler)
             * @param {Object} session - Session data from WebSocket
             */
            async addCardRealtime(session) {
                console.log('[REALTIME] Adding new session card:', session.session_id);

                // Check if card already exists
                const existingCard = document.querySelector(`.kanban-card[data-session-id="${session.session_id}"]`);
                if (existingCard) {
                    console.log('[REALTIME] Card already exists, updating instead');
                    this.updateCardRealtime(session.session_id, session);
                    return;
                }

                // Add to sessions array
                this.sessions.push(session);

                // Render the new card
                await this.renderCard(session);

                // Update column counts and stats
                this.updateColumnCounts();
                this.updateStats();

                // Add entrance animation
                const card = document.querySelector(`.kanban-card[data-session-id="${session.session_id}"]`);
                if (card) {
                    card.style.animation = 'slideInFromTop 0.3s ease-out';
                    setTimeout(() => {
                        card.style.animation = '';
                    }, 300);
                }
            },

            /**
             * Update existing session card in real-time (WebSocket event handler)
             * @param {string} sessionId - Session ID to update
             * @param {Object} updates - Updated fields
             */
            async updateCardRealtime(sessionId, updates) {
                console.log('[REALTIME] Updating session card:', sessionId, updates);

                // Find and update session in array
                const sessionIndex = this.sessions.findIndex(s => s.session_id === sessionId);
                if (sessionIndex === -1) {
                    console.warn('[REALTIME] Session not found in local cache:', sessionId);
                    return;
                }

                // Merge updates into existing session
                const session = this.sessions[sessionIndex];
                Object.assign(session, updates);

                // Find the card element
                const card = document.querySelector(`.kanban-card[data-session-id="${sessionId}"]`);
                if (!card) {
                    console.warn('[REALTIME] Card element not found:', sessionId);
                    return;
                }

                // Check if column changed (move to different column)
                const currentColumn = card.closest('.kanban-cards-container');
                const newColumnId = `${updates.kanban_column || session.kanban_column}-cards`;
                const newColumn = document.getElementById(newColumnId);

                if (currentColumn && newColumn && currentColumn !== newColumn) {
                    // Column changed - move card with animation
                    card.style.opacity = '0.3';
                    setTimeout(() => {
                        newColumn.appendChild(card);
                        card.style.animation = 'slideInFromRight 0.3s ease-out';
                        card.style.opacity = '1';
                        setTimeout(() => {
                            card.style.animation = '';
                        }, 300);
                        this.updateColumnCounts();
                    }, 200);
                } else {
                    // Same column - update in place with subtle flash
                    card.style.transition = 'background-color 0.3s ease';
                    card.style.backgroundColor = 'rgba(88, 166, 255, 0.1)';

                    // Save expanded state
                    const wasExpanded = card.dataset.expanded === 'true';

                    // Re-render the card
                    const container = card.parentElement;
                    const oldCard = card;
                    await this.renderCard(session);
                    const newCard = container.querySelector(`.kanban-card[data-session-id="${sessionId}"]`);

                    // Restore expanded state
                    if (newCard && wasExpanded) {
                        newCard.dataset.expanded = 'true';
                    }

                    // Fade background back
                    setTimeout(() => {
                        if (newCard) {
                            newCard.style.backgroundColor = '';
                        }
                    }, 300);
                }

                this.updateStats();
            },

            /**
             * Remove session card in real-time (WebSocket event handler)
             * @param {string} sessionId - Session ID to remove
             */
            removeCardRealtime(sessionId) {
                console.log('[REALTIME] Removing session card:', sessionId);

                // Remove from sessions array
                const sessionIndex = this.sessions.findIndex(s => s.session_id === sessionId);
                if (sessionIndex !== -1) {
                    this.sessions.splice(sessionIndex, 1);
                }

                // Find and remove card with fade-out animation
                const card = document.querySelector(`.kanban-card[data-session-id="${sessionId}"]`);
                if (card) {
                    card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                    card.style.opacity = '0';
                    card.style.transform = 'scale(0.9)';

                    setTimeout(() => {
                        card.remove();
                        this.updateColumnCounts();
                        this.updateStats();
                    }, 300);
                } else {
                    // Card not found, still update counts/stats
                    this.updateColumnCounts();
                    this.updateStats();
                }
            },

            // ==================== END REAL-TIME METHODS ====================

            async refreshBoard() {
                await this.ensureInitialized();
                console.log('Refreshing board...');
                this.showSyncIndicator('syncing', 'Refreshing...');

                await this.loadSessions();
                this.renderAllCards();
                this.updateStats();

                this.showSyncIndicator('success', 'Refreshed!', 1500);
            },

            async createNewSession(column = 'backlog') {
                await this.ensureInitialized();
                console.log('Opening Synergy Session Card modal for new session in column:', column);

                // Create a new empty session object
                const newSession = {
                    session_id: null, // null means create new
                    title: '',
                    description: '',
                    project_name: '',
                    priority: 'medium',
                    status: 'active',
                    kanban_column: column, // Use the specified column
                    platforms_involved: [],
                    tags: [],
                    documents: [],
                    links: [],
                    next_steps: [],
                    assignees: [],
                    checklist: [],
                    thread_ids: [],
                    assigned_agents: [],
                    notes: '',
                    due_date: null
                };

                // Open the edit modal (which also works for creating new sessions)
                this.openEditModal(newSession);
            },

            async addCard(column) {
                await this.ensureInitialized();
                // Open the modal with the specified column pre-selected
                await this.createNewSession(column);
            },

            async columnMenu(column) {
                await this.ensureInitialized();
                console.log('Column menu:', column);
                // Could add: Clear column, Sort by, etc.
            },

            openCardMenu(sessionId) {
                console.log(' Card menu:', sessionId);
                // Could add: Edit, Delete, Archive, etc.
            },

            toggleCardExpand(sessionId) {
                const card = document.querySelector(`.kanban-card[data-session-id="${sessionId}"]`);
                if (!card) return;

                const isExpanded = card.dataset.expanded === 'true';

                if (isExpanded) {
                    // Collapse
                    card.dataset.expanded = 'false';
                    console.log('[CHART] Card collapsed:', sessionId);
                } else {
                    // Expand
                    card.dataset.expanded = 'true';
                    console.log('[CHART] Card expanded:', sessionId);
                }
            },

            toggleCardInlineEdit(sessionId) {
                const card = document.querySelector(`.kanban-card[data-session-id="${sessionId}"]`);
                if (!card) return;

                const isEditing = card.dataset.editing === 'true';
                const session = this.sessions.find(s => s.session_id === sessionId);
                if (!session) return;

                if (isEditing) {
                    // Cancel edit - return to view mode
                    card.dataset.editing = 'false';
                    this.renderCardInline(card, session, false);
                    console.log('[INLINE EDIT] Edit cancelled:', sessionId);
                } else {
                    // Enter edit mode
                    card.dataset.editing = 'true';
                    this.renderCardInline(card, session, true);
                    console.log('[INLINE EDIT] Edit mode enabled:', sessionId);
                }
            },

            renderCardInline(cardElement, session, isEditing) {
                const expandedView = cardElement.querySelector('.card-expanded-view');
                if (!expandedView) return;

                const priorityEmoji = this.getPriorityEmoji(session.priority);
                const statusClass = this.getStatusClass(session.status);
                const timeAgo = this.getTimeAgo(session.created_at);

                if (isEditing) {
                    // Render editable view
                    expandedView.innerHTML = this.renderCardExpandedEditable(session, priorityEmoji, statusClass, timeAgo);

                    // Add save/cancel buttons
                    const footer = expandedView.querySelector('.card-footer-expanded');
                    if (footer) {
                        const editControls = document.createElement('div');
                        editControls.className = 'inline-edit-controls';
                        editControls.innerHTML = `
                            <button class="btn-inline-save" onclick="event.stopPropagation(); synergyBoard.saveCardInlineEdit('${this.escapeJs(session.session_id)}')">
                                <i class="fas fa-check"></i> Save Changes
                            </button>
                            <button class="btn-inline-cancel" onclick="event.stopPropagation(); synergyBoard.toggleCardInlineEdit('${this.escapeJs(session.session_id)}')">
                                <i class="fas fa-times"></i> Cancel
                            </button>
                        `;
                        footer.appendChild(editControls);
                    }
                } else {
                    // Render read-only view
                    expandedView.innerHTML = this.renderCardExpanded(session, priorityEmoji, statusClass, timeAgo);
                }
            },

            async saveCardInlineEdit(sessionId) {
                const card = document.querySelector(`.kanban-card[data-session-id="${sessionId}"]`);
                if (!card) return;

                const expandedView = card.querySelector('.card-expanded-view');
                if (!expandedView) return;

                // Collect edited values
                const updatedData = {
                    title: expandedView.querySelector('.edit-field-title')?.value || '',
                    description: expandedView.querySelector('.edit-field-description')?.value || '',
                    project_name: expandedView.querySelector('.edit-field-project')?.value || '',
                    priority: expandedView.querySelector('.edit-field-priority')?.value || 'medium',
                    status: expandedView.querySelector('.edit-field-status')?.value || 'active',
                    kanban_column: expandedView.querySelector('.edit-field-column')?.value || 'backlog',
                    due_date: expandedView.querySelector('.edit-field-due-date')?.value || null,
                    due_time: expandedView.querySelector('.edit-field-due-time')?.value || null,
                    assignees: expandedView.querySelector('.edit-field-assignees')?.value.split(',').map(a => a.trim()).filter(a => a) || [],
                    tags: expandedView.querySelector('.edit-field-tags')?.value.split(',').map(t => t.trim()).filter(t => t) || [],
                    thread_ids: expandedView.querySelector('.edit-field-thread-ids')?.value.split(',').map(t => t.trim()).filter(t => t) || [],
                    assigned_agents: expandedView.querySelector('.edit-field-assigned-agents')?.value.split(',').map(a => a.trim()).filter(a => a) || [],
                    notes: expandedView.querySelector('.edit-field-notes')?.value || ''
                };

                // Validate required fields
                if (!updatedData.title.trim()) {
                    alert('Title is required');
                    return;
                }

                console.log('[INLINE EDIT] Saving changes:', sessionId, updatedData);

                try {
                    // Call API to save
                    await this.apiEditCard(sessionId, updatedData);

                    // Update local session data
                    const session = this.sessions.find(s => s.session_id === sessionId);
                    if (session) {
                        Object.assign(session, updatedData);
                    }

                    // Exit edit mode and re-render
                    card.dataset.editing = 'false';
                    this.renderCardInline(card, session, false);

                    // Show success notification
                    if (typeof showNotification === 'function') {
                        showNotification('Changes saved successfully', 'success');
                    }

                    console.log('[INLINE EDIT] Changes saved successfully:', sessionId);

                    // Check if column changed - if so, move card
                    const currentColumn = card.closest('.kanban-column')?.dataset.column;
                    if (currentColumn && currentColumn !== updatedData.kanban_column) {
                        const newColumn = document.querySelector(`.kanban-column[data-column="${updatedData.kanban_column}"] .kanban-cards-container`);
                        if (newColumn) {
                            newColumn.appendChild(card);
                            this.updateColumnCounts();
                            console.log('[INLINE EDIT] Card moved to new column:', updatedData.kanban_column);
                        }
                    }

                } catch (error) {
                    console.error('[INLINE EDIT] Failed to save changes:', error);
                    if (typeof showNotification === 'function') {
                        showNotification('Failed to save changes', 'error');
                    } else {
                        alert('Failed to save changes. Please try again.');
                    }
                }
            },

            async toggleStep(sessionId, stepIndex) {
                const session = this.sessions.find(s => s.session_id === sessionId);
                if (!session || !session.next_steps) return;

                // Toggle in local data
                session.next_steps[stepIndex].completed = !session.next_steps[stepIndex].completed;
                const isCompleted = session.next_steps[stepIndex].completed;

                // Optimistic UI update - update checkbox and styling immediately
                const allStepCheckboxes = document.querySelectorAll(
                    `input[type="checkbox"][onchange*="toggleStep('${sessionId}', ${stepIndex})"]`
                );
                allStepCheckboxes.forEach(checkbox => {
                    checkbox.checked = isCompleted;
                    const parent = checkbox.closest('.step-item, div[style*="display: flex"]');
                    if (parent) {
                        const textSpan = parent.querySelector('span.step-description, span[style*="flex: 1"]');
                        if (textSpan) {
                            if (isCompleted) {
                                textSpan.style.textDecoration = 'line-through';
                                textSpan.style.opacity = '0.6';
                            } else {
                                textSpan.style.textDecoration = 'none';
                                textSpan.style.opacity = '1';
                            }
                        }
                        if (parent.classList.contains('step-item')) {
                            parent.classList.toggle('completed', isCompleted);
                        }
                    }
                });

                // Persist to database silently in background
                try {
                    await this.apiEditCard(sessionId, {
                        next_steps: session.next_steps
                    });
                    console.log('? Step toggled and saved:', sessionId, stepIndex);
                } catch (error) {
                    console.warn('Failed to save step toggle:', error);
                    // Revert UI on error
                    session.next_steps[stepIndex].completed = !isCompleted;
                    allStepCheckboxes.forEach(checkbox => {
                        checkbox.checked = !isCompleted;
                    });
                }

                // NO card re-render - user keeps working without interruption
            },

            async toggleSubItem(sessionId, stepIndex, subIndex) {
                const session = this.sessions.find(s => s.session_id === sessionId);
                if (!session || !session.next_steps) return;

                const step = session.next_steps[stepIndex];
                if (!step || !step.sub_checklist || !step.sub_checklist[subIndex]) return;

                // Toggle in local data
                step.sub_checklist[subIndex].completed = !step.sub_checklist[subIndex].completed;
                const isCompleted = step.sub_checklist[subIndex].completed;

                // Optimistic UI update
                const allSubCheckboxes = document.querySelectorAll(
                    `input[type="checkbox"][onchange*="toggleStepSubItem('${sessionId}', ${stepIndex}, ${subIndex})"]`
                );
                allSubCheckboxes.forEach(checkbox => {
                    checkbox.checked = isCompleted;
                    const parent = checkbox.closest('.sub-item, div[style*="display: flex"]');
                    if (parent) {
                        const textSpan = parent.querySelector('span:not(.sub-number)');
                        if (textSpan) {
                            if (isCompleted) {
                                textSpan.style.textDecoration = 'line-through';
                                textSpan.style.opacity = '0.6';
                            } else {
                                textSpan.style.textDecoration = 'none';
                                textSpan.style.opacity = '1';
                            }
                        }
                        if (parent.classList) {
                            parent.classList.toggle('completed', isCompleted);
                        }
                    }
                });

                // Persist to database silently
                try {
                    await this.apiEditCard(sessionId, {
                        next_steps: session.next_steps
                    });
                    console.log('? Sub-item toggled and saved:', sessionId, stepIndex, subIndex);
                } catch (error) {
                    console.warn('Failed to save sub-item toggle:', error);
                    step.sub_checklist[subIndex].completed = !isCompleted;
                    allSubCheckboxes.forEach(checkbox => {
                        checkbox.checked = !isCompleted;
                    });
                }
            },

            // Alias for toggleSubItem (called from HTML as toggleStepSubItem)
            async toggleStepSubItem(sessionId, stepIndex, subIndex) {
                return this.toggleSubItem(sessionId, stepIndex, subIndex);
            },

            async toggleChecklistItem(sessionId, itemIndex) {
                const session = this.sessions.find(s => s.session_id === sessionId);
                if (!session || !session.checklist) return;

                session.checklist[itemIndex].completed = !session.checklist[itemIndex].completed;

                // Persist to database
                try {
                    await this.apiEditCard(sessionId, {
                        checklist: session.checklist
                    });
                    console.log('✅ Checklist item toggled and saved:', sessionId, itemIndex);
                } catch (error) {
                    console.warn('⚠️ Failed to save checklist toggle:', error);
                }

                // Optimistic UI update - find and update ALL checkboxes immediately
                const allCheckboxes = document.querySelectorAll(
                    `input[type="checkbox"][onchange*="toggleChecklistItem('${sessionId}', ${itemIndex})"]`
                );
                const isCompleted = session.checklist[itemIndex].completed;
                allCheckboxes.forEach(checkbox => {
                    checkbox.checked = isCompleted;
                    const parent = checkbox.closest('.checklist-item, div[style*="display: flex"]');
                    if (parent) {
                        const textSpan = parent.querySelector('span:not(.item-number):not(.sub-number)');
                        if (textSpan) {
                            textSpan.style.textDecoration = isCompleted ? 'line-through' : 'none';
                            textSpan.style.opacity = isCompleted ? '0.6' : '1';
                        }
                        if (parent.classList.contains('checklist-item')) {
                            parent.classList.toggle('completed', isCompleted);
                        }
                    }
                });
                // NO card re-render - user keeps working without interruption
            },

            async toggleChecklistSubtask(sessionId, itemIndex, subtaskIndex) {
                const session = this.sessions.find(s => s.session_id === sessionId);
                if (!session || !session.checklist || !session.checklist[itemIndex]) return;

                const item = session.checklist[itemIndex];
                if (!item.subtasks || !item.subtasks[subtaskIndex]) return;

                // Toggle subtask completion
                item.subtasks[subtaskIndex].completed = !item.subtasks[subtaskIndex].completed;

                // Persist to database
                try {
                    await this.apiEditCard(sessionId, {
                        checklist: session.checklist
                    });
                    console.log('✅ Checklist subtask toggled and saved:', sessionId, itemIndex, subtaskIndex);
                } catch (error) {
                    console.warn('⚠️ Failed to save subtask toggle:', error);
                }

                // Optimistic UI update - find and update ALL subtask checkboxes immediately
                const allSubCheckboxes = document.querySelectorAll(
                    `input[type="checkbox"][onchange*="toggleChecklistSubtask('${sessionId}', ${itemIndex}, ${subtaskIndex})"]`
                );
                const isCompleted = item.subtasks[subtaskIndex].completed;
                allSubCheckboxes.forEach(checkbox => {
                    checkbox.checked = isCompleted;
                    const parent = checkbox.closest('.sub-item, div[style*="display: flex"]');
                    if (parent) {
                        const textSpan = parent.querySelector('span:not(.sub-number)');
                        if (textSpan) {
                            textSpan.style.textDecoration = isCompleted ? 'line-through' : 'none';
                            textSpan.style.opacity = isCompleted ? '0.6' : '1';
                        }
                        if (parent.classList) {
                            parent.classList.toggle('completed', isCompleted);
                        }
                    }
                });
                // NO card re-render - user keeps working without interruption
            },

            editCard(sessionId) {
                console.log('✏️ Opening edit modal for:', sessionId);
                const session = this.sessions.find(s => s.session_id === sessionId);
                if (!session) {
                    console.error(' Session not found:', sessionId);
                    return;
                }

                this.openEditModal(session);
            },

            async toggleMilestone(sessionId, milestoneId) {
                console.log('[SYNERGY] Toggling milestone:', milestoneId);
                try {
                    const response = await fetch(`${this.apiBaseUrl}/api/synergy/${sessionId}/milestones/${milestoneId}/toggle`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' }
                    });
                    if (response.ok) {
                        console.log('[SYNERGY] Milestone toggled successfully');
                        await this.refreshCard(sessionId);
                    }
                } catch (error) {
                    console.error('[SYNERGY] Failed to toggle milestone:', error);
                }
            },

            async toggleTask(sessionId, taskId) {
                console.log('[SYNERGY] Toggling task:', taskId);
                try {
                    const response = await fetch(`${this.apiBaseUrl}/api/synergy/${sessionId}/tasks/${taskId}/toggle`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' }
                    });
                    if (response.ok) {
                        console.log('[SYNERGY] Task toggled successfully');
                        await this.refreshCard(sessionId);
                    }
                } catch (error) {
                    console.error('[SYNERGY] Failed to toggle task:', error);
                }
            },

            async toggleSubtask(sessionId, subtaskId) {
                console.log('[SYNERGY] Toggling subtask:', subtaskId);
                try {
                    const response = await fetch(`${this.apiBaseUrl}/api/synergy/${sessionId}/subtasks/${subtaskId}/toggle`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' }
                    });
                    if (response.ok) {
                        console.log('[SYNERGY] Subtask toggled successfully');
                        await this.refreshCard(sessionId);
                    }
                } catch (error) {
                    console.error('[SYNERGY] Failed to toggle subtask:', error);
                }
            },

            async refreshCard(sessionId) {
                const popoutWindows = document.querySelectorAll('.popout-card-window');
                for (const window of popoutWindows) {
                    if (window.dataset.sessionId === sessionId) {
                        const windowId = window.id;
                        await this.closePopout(windowId);
                        await this.popOutCard(sessionId);
                    }
                }
                await this.loadSessions();
                this.renderAllCards();
            },

            openCardMenu(sessionId) {
                console.log(' Card menu:', sessionId);
                // TODO: Implement card menu (delete, duplicate, move, etc.)
            },

            // ============================================
            // AI CARD MANAGEMENT FUNCTIONS
            // ============================================

            /**
             * AI function to create a new card/session
             * @param {Object} cardData - Card data object
                                                                                                                                        * @returns {string} Session ID of created card
                                                                                                                                        */
            async aiCreateCard(cardData) {
                console.log(' AI Creating card:', cardData.title);

                // Generate session ID
                const timestamp = Date.now();
                const userIdentifier = cardData.assignees ? cardData.assignees[0].toLowerCase().replace(/\s+/g, '_') : 'ai';
                const titleSlug = cardData.title.toLowerCase().replace(/\s+/g, '_').substring(0, 20);
                const sessionId = `sess_${timestamp}_${userIdentifier}_${titleSlug}`;

                // Create session object with defaults
                const newSession = {
                    session_id: sessionId,
                    title: cardData.title || 'Untitled Task',
                    description: cardData.description || '',
                    project_name: cardData.project_name || 'AI Generated',
                    priority: cardData.priority || 'medium',
                    status: cardData.status || 'active',
                    kanban_column: cardData.kanban_column || 'backlog',
                    message_count: cardData.message_count || 0,
                    active_docs: cardData.active_docs || 0,
                    pending_steps: cardData.pending_steps || 0,
                    last_active: new Date().toISOString(),
                    created_at: new Date().toISOString(),
                    due_date: cardData.due_date || null,
                    assignees: cardData.assignees || ['AI Assistant'],
                    tags: cardData.tags || [],
                    notes: cardData.notes || '',
                    documents: cardData.documents || [],
                    links: cardData.links || [],
                    next_steps: cardData.next_steps || [],
                    checklist: cardData.checklist || [],
                    recent_activity: [{
                        description: 'Card created by AI',
                        timestamp: new Date().toISOString()
                    }]
                };

                // Add to sessions array
                this.sessions.push(newSession);

                // Render card
                await this.renderCard(newSession);

                // Update UI
                this.updateColumnCounts();
                this.updateStats();

                // Show sync indicator
                this.showSyncIndicator('success', `Created: ${newSession.title}`, 3000);

                console.log('AI Created card:', sessionId);
                return sessionId;
            },

            /**
             * AI function to edit an existing card
             * @param {string} sessionId - Session ID to edit
                                                                                                                                        * @param {Object} updates - Fields to update
                                                                                                                                        * @returns {boolean} Success status
                                                                                                                                        */
            async aiEditCard(sessionId, updates) {
                console.log(' AI Editing card:', sessionId, updates);

                const session = this.sessions.find(s => s.session_id === sessionId);
                if (!session) {
                    console.error(' Session not found:', sessionId);
                    return false;
                }

                // Merge updates into session
                Object.keys(updates).forEach(key => {
                    if (key in session) {
                        session[key] = updates[key];
                    }
                });

                // Update last_active
                session.last_active = new Date().toISOString();

                // Add activity
                if (!session.recent_activity) session.recent_activity = [];
                session.recent_activity.unshift({
                    description: `AI updated: ${Object.keys(updates).join(', ')}`,
                    timestamp: new Date().toISOString()
                });

                // Re-render card
                const oldCard = document.querySelector(`.kanban-card[data-session-id="${sessionId}"]`);
                const wasExpanded = oldCard && oldCard.dataset.expanded === 'true';

                if (oldCard) oldCard.remove();
                await this.renderCard(session);

                if (wasExpanded) {
                    this.toggleCardExpand(sessionId);
                }

                // Update UI
                this.updateColumnCounts();
                this.updateStats();

                this.showSyncIndicator('success', `Updated: ${session.title}`, 2000);

                console.log('AI Edited card:', sessionId);
                return true;
            },

            /**
             * AI function to add a document to a card
             * @param {string} sessionId - Session ID
                                                                                                                                        * @param {Object} document - Document object {title, url, type}
                                                                                                                                        * @returns {boolean} Success status
                                                                                                                                        */
            async aiAddDocument(sessionId, document) {
                console.log(' AI Adding document:', sessionId, document.title);

                const session = this.sessions.find(s => s.session_id === sessionId);
                if (!session) {
                    console.error(' Session not found:', sessionId);
                    return false;
                }

                // Parse documents if it's a JSON string
                const documents = this.parseJsonField(session.documents, []);

                documents.push({
                    title: document.title,
                    url: document.url,
                    type: document.type || 'file',
                    created_at: new Date().toISOString()
                });

                session.documents = documents;
                session.active_docs = documents.length;
                session.last_active = new Date().toISOString();

                // Add activity
                const recentActivity = this.parseJsonField(session.recent_activity, []);
                recentActivity.unshift({
                    description: `Added document: ${document.title}`,
                    timestamp: new Date().toISOString()
                });
                session.recent_activity = recentActivity;

                // Re-render if card exists
                const oldCard = document.querySelector(`.kanban-card[data-session-id="${sessionId}"]`);
                if (oldCard) {
                    const wasExpanded = oldCard.dataset.expanded === 'true';
                    oldCard.remove();
                    await this.renderCard(session);
                    if (wasExpanded) this.toggleCardExpand(sessionId);
                }

                console.log('AI Added document:', sessionId);
                return true;
            },

            /**
             * AI function to add a link to a card
             * @param {string} sessionId - Session ID
                                                                                                                                        * @param {Object} link - Link object {title, url, type}
                                                                                                                                        * @returns {boolean} Success status
                                                                                                                                        */
            async aiAddLink(sessionId, link) {
                console.log(' AI Adding link:', sessionId, link.title);

                const session = this.sessions.find(s => s.session_id === sessionId);
                if (!session) {
                    console.error(' Session not found:', sessionId);
                    return false;
                }

                // Parse links if it's a JSON string
                const links = this.parseJsonField(session.links, []);

                links.push({
                    title: link.title,
                    url: link.url,
                    type: link.type || 'external'
                });

                session.links = links;
                session.last_active = new Date().toISOString();

                // Add activity
                const recentActivity = this.parseJsonField(session.recent_activity, []);
                recentActivity.unshift({
                    description: `Added link: ${link.title}`,
                    timestamp: new Date().toISOString()
                });
                session.recent_activity = recentActivity;

                // Re-render if card exists
                const oldCard = document.querySelector(`.kanban-card[data-session-id="${sessionId}"]`);
                if (oldCard) {
                    const wasExpanded = oldCard.dataset.expanded === 'true';
                    oldCard.remove();
                    await this.renderCard(session);
                    if (wasExpanded) this.toggleCardExpand(sessionId);
                }

                console.log('AI Added link:', sessionId);
                return true;
            },

            /**
             * AI function to add a next step to a card
             * @param {string} sessionId - Session ID
                                                                                                                                        * @param {Object} step - Step object {description, due_date}
                                                                                                                                        * @returns {boolean} Success status
                                                                                                                                        */
            async aiAddNextStep(sessionId, step) {
                console.log(' AI Adding next step:', sessionId, step.description);

                const session = this.sessions.find(s => s.session_id === sessionId);
                if (!session) {
                    console.error(' Session not found:', sessionId);
                    return false;
                }

                if (!session.next_steps) session.next_steps = [];

                // Parse next_steps if it's a JSON string
                const nextSteps = this.parseJsonField(session.next_steps, []);

                nextSteps.push({
                    description: step.description,
                    completed: false,
                    due_date: step.due_date || null
                });

                session.next_steps = nextSteps;
                session.pending_steps = nextSteps.filter(s => !s.completed).length;
                session.last_active = new Date().toISOString();

                // Add activity
                const recentActivity = this.parseJsonField(session.recent_activity, []);
                recentActivity.unshift({
                    description: `Added step: ${step.description}`,
                    timestamp: new Date().toISOString()
                });
                session.recent_activity = recentActivity;

                // Re-render if card exists
                const oldCard = document.querySelector(`.kanban-card[data-session-id="${sessionId}"]`);
                if (oldCard) {
                    const wasExpanded = oldCard.dataset.expanded === 'true';
                    oldCard.remove();
                    await this.renderCard(session);
                    if (wasExpanded) this.toggleCardExpand(sessionId);
                }

                console.log('AI Added next step:', sessionId);
                return true;
            },

            /**
             * AI function to update checklist items
             * @param {string} sessionId - Session ID
                                                                                                                                        * @param {Array} checklistItems - Array of {item, completed}
                                                                                                                                        * @returns {boolean} Success status
                                                                                                                                        */
            async aiUpdateChecklist(sessionId, checklistItems) {
                console.log(' AI Updating checklist:', sessionId);

                const session = this.sessions.find(s => s.session_id === sessionId);
                if (!session) {
                    console.error(' Session not found:', sessionId);
                    return false;
                }

                session.checklist = checklistItems;
                session.last_active = new Date().toISOString();

                // Add activity
                if (!session.recent_activity) session.recent_activity = [];
                session.recent_activity.unshift({
                    description: `Updated checklist (${checklistItems.filter(c => c.completed).length}/${checklistItems.length} complete)`,
                    timestamp: new Date().toISOString()
                });

                // Re-render if card exists
                const oldCard = document.querySelector(`.kanban-card[data-session-id="${sessionId}"]`);
                if (oldCard) {
                    const wasExpanded = oldCard.dataset.expanded === 'true';
                    oldCard.remove();
                    await this.renderCard(session);
                    if (wasExpanded) this.toggleCardExpand(sessionId);
                }

                console.log('AI Updated checklist:', sessionId);
                return true;
            },

            /**
             * AI function to move a card to a different column
             * @param {string} sessionId - Session ID
                                                                                                                                        * @param {string} newColumn - Target column (backlog, in_progress, review, done)
                                                                                                                                        * @returns {boolean} Success status
                                                                                                                                        */
            async aiMoveCard(sessionId, newColumn) {
                console.log(' AI Moving card:', sessionId, '→', newColumn);

                const session = this.sessions.find(s => s.session_id === sessionId);
                if (!session) {
                    console.error(' Session not found:', sessionId);
                    return false;
                }

                const oldColumn = session.kanban_column;
                session.kanban_column = newColumn;

                // Update status based on column
                const statusMap = {
                    'backlog': 'paused',
                    'in_progress': 'active',
                    'review': 'active',
                    'done': 'completed'
                };
                session.status = statusMap[newColumn] || 'active';
                session.last_active = new Date().toISOString();

                // Add activity
                if (!session.recent_activity) session.recent_activity = [];
                session.recent_activity.unshift({
                    description: `Moved from ${oldColumn} to ${newColumn}`,
                    timestamp: new Date().toISOString()
                });

                // Remove old card and render in new column
                const oldCard = document.querySelector(`.kanban-card[data-session-id="${sessionId}"]`);
                if (oldCard) oldCard.remove();

                await this.renderCard(session);
                this.updateColumnCounts();
                this.updateStats();

                console.log('AI Moved card:', sessionId);
                return true;
            },

            /**
             * AI function to add notes to a card
             * @param {string} sessionId - Session ID
                                                                                                                                        * @param {string} noteText - Note content to append
                                                                                                                                        * @returns {boolean} Success status
                                                                                                                                        */
            async aiAddNote(sessionId, noteText) {
                console.log(' AI Adding note:', sessionId);

                const session = this.sessions.find(s => s.session_id === sessionId);
                if (!session) {
                    console.error(' Session not found:', sessionId);
                    return false;
                }

                if (!session.notes) {
                    session.notes = noteText;
                } else {
                    session.notes += `\n\n${noteText}`;
                }

                session.last_active = new Date().toISOString();

                // Add activity
                if (!session.recent_activity) session.recent_activity = [];
                session.recent_activity.unshift({
                    description: 'Added note',
                    timestamp: new Date().toISOString()
                });

                // Re-render if card exists
                const oldCard = document.querySelector(`.kanban-card[data-session-id="${sessionId}"]`);
                if (oldCard) {
                    const wasExpanded = oldCard.dataset.expanded === 'true';
                    oldCard.remove();
                    await this.renderCard(session);
                    if (wasExpanded) this.toggleCardExpand(sessionId);
                }

                console.log('AI Added note:', sessionId);
                return true;
            },

            async resumeSession(sessionId) {
                console.log('▶️ Resuming session:', sessionId);

                const session = this.sessions.find(s => s.session_id === sessionId);
                if (!session) {
                    showNotification('Session not found', 'error');
                    return;
                }

                // Parse thread IDs
                const threadIds = this.parseJsonField(session.thread_ids, []);

                if (threadIds.length === 0) {
                    // No threads linked - just open AI chat with session context
                    this.resumeInNewThread(session);
                } else if (threadIds.length === 1) {
                    // Single thread - load it directly
                    await this.resumeInThread(session, threadIds[0]);
                } else {
                    // Multiple threads - show picker modal
                    this.showThreadPickerModal(session, threadIds);
                }
            },

            async resumeInNewThread(session) {
                console.log('▶️ [RESUME] No threads linked - creating new thread in Prime Agent');

                try {
                    // Switch to AI Chat tab (Prime Agent sidebar)
                    const chatPanel = document.getElementById('ai-chat-panel');
                    if (chatPanel) {
                        chatPanel.classList.add('visible');
                    }

                    // Create new thread with session title
                    const newThreadId = await this.createThreadForSession(session);

                    if (newThreadId) {
                        // Load the new thread
                        if (typeof ThreadManager !== 'undefined' && ThreadManager.loadThread) {
                            await ThreadManager.loadThread(newThreadId);
                        }

                        // Build system prompt
                        const systemPrompt = this.buildSessionContext(session);

                        // Send as system message (prepend special marker for backend)
                        await this.sendSystemMessage(systemPrompt);

                        showNotification(` Resuming session: ${session.title}`, 'success');
                    } else {
                        throw new Error('Failed to create thread');
                    }
                } catch (error) {
                    console.error('❌ [RESUME] Failed to resume in new thread:', error);
                    showNotification('Failed to create resume thread', 'error');
                }
            },

            async resumeInThread(session, threadId) {
                console.log('▶️ [RESUME] Loading existing thread:', threadId);

                try {
                    // Fetch thread details to determine agent/location
                    const thread = await this.getThreadDetails(threadId);
                    if (!thread) {
                        throw new Error('Thread not found');
                    }

                    // Determine agent from thread location
                    const agentId = this.detectAgentFromLocation(thread.location);

                    // Route to correct UI
                    if (agentId === 1) {
                        // Prime Agent - open sidebar
                        console.log('▶️ [RESUME] Routing to Prime Agent (sidebar)');
                        const chatPanel = document.getElementById('ai-chat-panel');
                        if (chatPanel) {
                            chatPanel.classList.add('visible');
                        }

                        // Load thread in sidebar
                        if (typeof ThreadManager !== 'undefined' && ThreadManager.loadThread) {
                            await ThreadManager.loadThread(threadId);
                        }
                    } else if (agentId >= 2 && agentId <= 3) {
                        // Agent 2 or 3 - open multi-agent view
                        console.log(`▶️ [RESUME] Routing to Agent ${agentId} (column)`);

                        // Switch to multi-agent tab
                        switchTab('multi-agent');

                        // Ensure agent column exists
                        if (typeof MultiAgent !== 'undefined' && MultiAgent.addAgentColumn) {
                            MultiAgent.addAgentColumn(agentId);
                        }

                        // Load thread into agent column
                        if (typeof MultiAgent !== 'undefined' && MultiAgent.loadThreadInAgent) {
                            await MultiAgent.loadThreadInAgent(agentId, threadId);
                        }
                    }

                    // Build system prompt
                    const systemPrompt = this.buildSessionContext(session);

                    // Send as system message
                    await this.sendSystemMessage(systemPrompt, agentId);

                    showNotification(` Resuming session: ${session.title}`, 'success');
                } catch (error) {
                    console.error('❌ [RESUME] Failed to resume in thread:', error);
                    showNotification('Failed to load thread', 'error');
                }
            },

            buildSessionContext(session) {
                const threadIds = this.parseJsonField(session.thread_ids, []);
                const nextSteps = this.parseJsonField(session.next_steps, []).filter(s => !s.completed);
                const documents = this.parseJsonField(session.documents, []);
                const tags = this.parseJsonField(session.tags, []);

                let context = `Resume Synergy Session: "${session.title}"\n\n`;

                if (session.project_name) {
                    context += `Project: ${session.project_name}\n`;
                }

                if (session.description) {
                    context += `Description: ${session.description}\n\n`;
                }

                context += `Priority: ${session.priority || 'medium'}\n`;
                context += `Status: ${session.status || 'active'}\n`;
                context += `Last Active: ${this.formatTimeAgo(session.last_active)}\n\n`;

                if (nextSteps.length > 0) {
                    context += `Next Steps:\n`;
                    nextSteps.slice(0, 5).forEach((step, idx) => {
                        context += `${idx + 1}. ${step.description}\n`;
                    });
                    context += '\n';
                }

                if (documents.length > 0) {
                    context += `Documents: ${documents.length} file(s)\n`;
                }

                if (tags.length > 0) {
                    context += `Tags: ${tags.join(', ')}\n`;
                }

                if (session.notes) {
                    context += `\nNotes:\n${session.notes}\n`;
                }

                context += `\n---\nPlease help me continue working on this session.`;

                return context;
            },

            async createThreadForSession(session) {
                console.log(' [RESUME] Creating new thread for session:', session.title);

                try {
                    // Create thread via ThreadManager API
                    const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/create`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`
                        },
                        body: JSON.stringify({
                            title: session.title,  // Use session title as thread title
                            location: 'prime',      // Always create in Prime Agent
                            agent_id: 1,
                            synergy_card_id: session.session_id,  // Link to Synergy session
                            tags: session.tags ? JSON.parse(session.tags) : []
                        })
                    });

                    if (!response.ok) {
                        throw new Error(`API returned ${response.status}`);
                    }

                    const data = await response.json();
                    const newThreadId = data.thread?.id || data.thread?.thread_id || data.id;

                    if (!newThreadId) {
                        throw new Error('No thread ID in response');
                    }

                    console.log('✅ [RESUME] Thread created:', newThreadId);

                    // Update session with new thread ID
                    await this.linkThreadToSession(session.session_id, newThreadId);

                    return newThreadId;
                } catch (error) {
                    console.error('❌ [RESUME] Failed to create thread:', error);
                    return null;
                }
            },

            async linkThreadToSession(sessionId, threadId) {
                console.log(' [RESUME] Linking thread to session:', { sessionId, threadId });

                try {
                    // Get current session
                    const session = this.sessions.find(s => s.session_id === sessionId);
                    if (!session) return;

                    // Add thread ID to array
                    const threadIds = this.parseJsonField(session.thread_ids, []);
                    if (!threadIds.includes(threadId)) {
                        threadIds.push(threadId);

                        // Update session via API
                        const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/synergy/${sessionId}`, {
                            method: 'PATCH',
                            headers: {
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`
                            },
                            body: JSON.stringify({
                                thread_ids: JSON.stringify(threadIds),
                                agent_ids: JSON.stringify([1])  // Prime Agent
                            })
                        });

                        if (response.ok) {
                            console.log('✅ [RESUME] Thread linked to session');
                            // Refresh session data
                            await this.loadSessions();
                        }
                    }
                } catch (error) {
                    console.error('❌ [RESUME] Failed to link thread:', error);
                }
            },

            async getThreadDetails(threadId) {
                console.log(' [RESUME] Fetching thread details:', threadId);

                try {
                    const response = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/${threadId}`, {
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`
                        }
                    });

                    if (!response.ok) {
                        throw new Error(`API returned ${response.status}`);
                    }

                    const data = await response.json();
                    const thread = data.thread || data;

                    console.log('✅ [RESUME] Thread details:', thread);
                    return thread;
                } catch (error) {
                    console.error('❌ [RESUME] Failed to fetch thread:', error);
                    return null;
                }
            },

            detectAgentFromLocation(location) {
                // Detect agent ID from thread location
                if (!location) return 1;  // Default to Prime

                if (location.includes('prime') || location === 'main') {
                    return 1;  // Prime Agent
                } else if (location.includes('agent-2')) {
                    return 2;  // Agent 2
                } else if (location.includes('agent-3')) {
                    return 3;  // Agent 3
                }

                return 1;  // Default to Prime
            },

            async sendSystemMessage(systemPrompt, agentId = 1) {
                console.log(' [RESUME] Sending system message to agent:', agentId);

                try {
                    // Get current input element
                    const inputElement = agentId === 1
                        ? document.getElementById('ai-chat-input')  // Prime sidebar
                        : document.getElementById(`input-${agentId}`);  // Agent column

                    if (!inputElement) {
                        console.warn('❌ [RESUME] Input element not found');
                        return;
                    }

                    // Temporarily set input value (will be cleared by send function)
                    inputElement.value = `[SYSTEM] ${systemPrompt}`;

                    // Trigger send function
                    if (agentId === 1) {
                        // Prime Agent - use sidebar send function
                        if (typeof sendChatMessage === 'function') {
                            await sendChatMessage();
                        }
                    } else {
                        // Agent 2/3 - use multi-agent send function
                        if (typeof sendAgentMessage === 'function') {
                            await sendAgentMessage(agentId);
                        }
                    }

                    console.log('✅ [RESUME] System message sent');
                } catch (error) {
                    console.error('❌ [RESUME] Failed to send system message:', error);
                }
            },

            showThreadPickerModal(session, threadIds) {
                console.log(' Showing thread picker for', threadIds.length, 'threads');

                const modalHTML = `
                    <div class="modal-overlay" id="threadPickerModalOverlay" onclick="if(event.target.id === 'threadPickerModalOverlay') document.getElementById('threadPickerModalOverlay').remove()">
                        <div class="thread-picker-modal" onclick="event.stopPropagation()">
                            <div class="modal-header">
                                <h3><i class="fas fa-play"></i> Resume Session: ${this.escapeHtml(session.title)}</h3>
                                <button class="modal-close" onclick="document.getElementById('threadPickerModalOverlay').remove()">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                            
                            <div class="modal-body">
                                <p style="margin-bottom: 20px; color: var(--text-secondary);">
                                    This session is linked to <strong>${threadIds.length} threads</strong>. 
                                    Which thread would you like to resume in?
                                </p>

                                <div class="thread-picker-list" id="threadPickerList">
                                    <div style="text-align: center; padding: 20px; color: var(--text-muted);">
                                        <i class="fas fa-spinner fa-spin"></i> Loading threads...
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                document.body.insertAdjacentHTML('beforeend', modalHTML);

                // Load thread details asynchronously
                this.loadThreadDetailsForPicker(session, threadIds);
            },

            async loadThreadDetailsForPicker(session, threadIds) {
                const container = document.getElementById('threadPickerList');
                if (!container) return;

                try {
                    // Fetch thread details
                    const threads = [];
                    for (const threadId of threadIds) {
                        try {
                            const resp = await fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/threads/${threadId}`);
                            if (resp.ok) {
                                const data = await resp.json();
                                if (data.success && data.thread) {
                                    threads.push(data.thread);
                                }
                            }
                        } catch (err) {
                            console.warn('Failed to fetch thread:', threadId, err);
                        }
                    }

                    if (threads.length === 0) {
                        container.innerHTML = `
                            <div style="text-align: center; padding: 20px; color: var(--text-muted);">
                                <i class="fas fa-exclamation-triangle"></i>
                                <p>Could not load thread details. They may have been deleted.</p>
                            </div>
                        `;
                        return;
                    }

                    // Render thread list
                    container.innerHTML = threads.map(thread => {
                        const lastUpdated = thread.updated_at ? new Date(thread.updated_at).toLocaleString() : 'Unknown';
                        const messageCount = thread.message_count || 0;

                        return `
                            <div class="thread-picker-item" onclick="synergyBoard.resumeInThread(synergyBoard.sessions.find(s => s.session_id === '${this.escapeJs(session.session_id)}'), '${thread.id}'); document.getElementById('threadPickerModalOverlay').remove();">
                                <div class="thread-picker-header">
                                    <span class="thread-picker-title">
                                        <i class="fas fa-comments"></i>
                                        ${this.escapeHtml(thread.name || thread.title || 'Untitled Thread')}
                                    </span>
                                    <span class="thread-picker-badge">${messageCount} messages</span>
                                </div>
                                <div class="thread-picker-meta">
                                    <span><i class="fas fa-hashtag"></i> ${thread.thread_slug || thread.id}</span>
                                    <span><i class="fas fa-clock"></i> ${lastUpdated}</span>
                                </div>
                            </div>
                        `;
                    }).join('');

                } catch (error) {
                    console.error('Failed to load threads:', error);
                    container.innerHTML = `
                        <div style="text-align: center; padding: 20px; color: var(--accent-error);">
                            <i class="fas fa-times-circle"></i>
                            <p>Error loading threads. Please try again.</p>
                        </div>
                    `;
                }
            },

            async deleteCard(sessionId) {
                try {
                    // Try UIComponents first
                    if (window.UIComponents && typeof UIComponents.showConfirmation === 'function') {
                        UIComponents.showConfirmation({
                            title: 'Delete Session?',
                            message: 'This action cannot be undone. All session data will be permanently deleted.',
                            variant: 'danger',
                            confirmLabel: 'Delete',
                            cancelLabel: 'Cancel',
                            onConfirm: async () => {
                                console.log('Deleting session:', sessionId);
                                await this.executeDelete(sessionId);
                            }
                        });
                    } else {
                        // Fallback to native confirm if UIComponents not available
                        console.warn('[SYNERGY] UIComponents not available, using native confirm');
                        if (confirm('Delete Session?\n\nThis action cannot be undone. All session data will be permanently deleted.')) {
                            console.log('Deleting session:', sessionId);
                            await this.executeDelete(sessionId);
                        }
                    }
                } catch (error) {
                    console.error('[SYNERGY] Delete confirmation error:', error);
                    // Final fallback
                    if (confirm('Delete this session? This action cannot be undone.')) {
                        await this.executeDelete(sessionId);
                    }
                }
            },

            async executeDelete(sessionId) {
                console.log('Executing delete for session:', sessionId);
                this.showSyncIndicator('syncing', 'Deleting session...');

                try {
                    const response = await fetch(`${this.apiBaseUrl}/api/synergy/${sessionId}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });

                    if (!response.ok) {
                        throw new Error(`API error: ${response.status}`);
                    }

                    const result = await response.json();

                    if (result.success) {
                        // Remove from sessions array
                        this.sessions = this.sessions.filter(s => s.session_id !== sessionId);

                        // Remove from DOM
                        const card = document.querySelector(`.kanban-card[data-session-id="${sessionId}"]`);
                        if (card) {
                            card.style.transition = 'all 0.3s ease';
                            card.style.opacity = '0';
                            card.style.transform = 'scale(0.8)';
                            setTimeout(() => card.remove(), 300);
                        }

                        // Update stats
                        this.updateColumnCounts();
                        this.updateStats();

                        this.showSyncIndicator('success', 'Session deleted!', 2000);
                        console.log('Session deleted from database:', sessionId);
                    } else {
                        throw new Error(result.error || 'Failed to delete session');
                    }

                } catch (error) {
                    console.error('Failed to delete session:', error);
                    this.showSyncIndicator('error', 'Failed to delete - please try again', 3000);
                }
            },

            popOutCard(sessionId) {
                console.log(' Popping out card:', sessionId);

                const session = this.sessions.find(s => s.session_id === sessionId);
                if (!session) return;

                // Get or create popout windows container
                let container = document.getElementById('popout-windows-container');
                if (!container) {
                    container = document.createElement('div');
                    container.id = 'popout-windows-container';
                    document.body.appendChild(container);
                }

                // Create unique window ID
                const windowId = `popout-${sessionId}-${Date.now()}`;

                // Create popout window
                const popoutWindow = document.createElement('div');
                popoutWindow.className = 'popout-card-window';
                popoutWindow.id = windowId;
                popoutWindow.dataset.sessionId = sessionId;

                // Calculate initial position (cascade windows)
                const existingWindows = container.querySelectorAll('.popout-card-window');
                const offset = existingWindows.length * 30;
                popoutWindow.style.top = `${100 + offset}px`;
                popoutWindow.style.left = `${200 + offset}px`;

                // Render card content
                const priorityEmoji = { 'critical': '<i class="fas fa-exclamation-circle" style="color: #dc2626;"></i>', 'high': '<i class="fas fa-circle" style="color: #ef4444;"></i>', 'medium': '<i class="fas fa-circle" style="color: #fbbf24;"></i>', 'low': '<i class="fas fa-circle" style="color: #22c55e;"></i>' }[session.priority] || '<i class="fas fa-circle" style="color: #9ca3af;"></i>';
                const statusClass = {
                    'active': 'status-active',
                    'paused': 'status-paused',
                    'completed': 'status-completed'
                }[session.status] || 'status-active';
                const timeAgo = this.formatTimeAgo(session.last_active);

                popoutWindow.innerHTML = `
                                                                                                                                        <div class="popout-card-header">
                                                                                                                                            <div class="popout-card-title">
                                                                                                                                                <span>Synergy Pop-Out</span>
                                                                                                                                            </div>
                                                                                                                                            <div class="popout-card-controls">
                                                                                                                                                <button class="popout-control-btn edit" onclick="synergyBoard.togglePopupEdit('${windowId}', '${this.escapeJs(sessionId)}')" title="Edit">
                                                                                                                                                    <i class="fas fa-edit"></i>
                                                                                                                                                </button>
                                                                                                                                                <button class="popout-control-btn delete" onclick="synergyBoard.deleteCardFromPopup('${windowId}', '${this.escapeJs(sessionId)}')" title="Delete">
                                                                                                                                                    <i class="fas fa-trash"></i>
                                                                                                                                                </button>
                                                                                                                                                <button class="popout-control-btn close" onclick="synergyBoard.closePopout('${windowId}')" title="Close">
                                                                                                                                                    <i class="fas fa-times"></i>
                                                                                                                                                </button>
                                                                                                                                            </div>
                                                                                                                                        </div>
                                                                                                                                        <div class="popout-card-content">
                                                                                                                                            ${this.renderCardExpanded(session, priorityEmoji, statusClass, timeAgo)}
                                                                                                                                        </div>
                                                                                                                                        <div class="popout-card-footer">
                                                                                                                                            <div>
                                                                                                                                                <i class="fas fa-clock"></i> Popped out: ${new Date().toLocaleTimeString()}
                                                                                                                                            </div>
                                                                                                                                            <div class="popout-move-warning">
                                                                                                                                                <i class="fas fa-exclamation-triangle"></i> Collapse to move
                                                                                                                                            </div>
                                                                                                                                            <div>
                                                                                                                                                Session ID: ${session.session_id.substring(0, 15)}...
                                                                                                                                            </div>
                                                                                                                                        </div>
                                                                                                                                        `;

                container.appendChild(popoutWindow);

                // Make window draggable
                this.makePopoutDraggable(windowId);

                // Make window focusable
                this.makePopoutFocusable(windowId);

                // Track pop-out event
                this.trackCardMovement(sessionId, 'popped_out', {
                    windowId: windowId,
                    timestamp: new Date().toISOString(),
                    user: this.getCurrentUser()
                });

                console.log('Card popped out to new window');
            },

            makePopoutDraggable(windowId) {
                const window = document.getElementById(windowId);
                if (!window) return;

                const header = window.querySelector('.popout-card-header');
                let isDragging = false;
                let currentX, currentY, initialX, initialY;

                header.addEventListener('mousedown', (e) => {
                    // Only allow drag if window is collapsed (not expanded)
                    if (window.classList.contains('expanded')) {
                        return;
                    }

                    isDragging = true;
                    initialX = e.clientX - (parseInt(window.style.left) || 0);
                    initialY = e.clientY - (parseInt(window.style.top) || 0);

                    window.classList.add('active');
                });

                document.addEventListener('mousemove', (e) => {
                    if (!isDragging) return;

                    e.preventDefault();
                    currentX = e.clientX - initialX;
                    currentY = e.clientY - initialY;

                    window.style.left = `${currentX}px`;
                    window.style.top = `${currentY}px`;

                    // Track movement
                    const sessionId = window.dataset.sessionId;
                    this.trackCardMovement(sessionId, 'moved', {
                        position: { x: currentX, y: currentY },
                        timestamp: new Date().toISOString()
                    });
                });

                document.addEventListener('mouseup', () => {
                    isDragging = false;
                });
            },

            makePopoutFocusable(windowId) {
                const window = document.getElementById(windowId);
                if (!window) return;

                window.addEventListener('mousedown', () => {
                    // Remove active class from all windows
                    document.querySelectorAll('.popout-card-window').forEach(w => {
                        w.classList.remove('active');
                    });

                    // Add active class to this window
                    window.classList.add('active');
                });
            },

            togglePopoutExpand(windowId) {
                const window = document.getElementById(windowId);
                if (!window) return;

                window.classList.toggle('expanded');

                const btn = window.querySelector('.popout-control-btn i');
                if (window.classList.contains('expanded')) {
                    btn.className = 'fas fa-compress-alt';
                } else {
                    btn.className = 'fas fa-expand-alt';
                }

                console.log(' Popout window toggled:', window.classList.contains('expanded') ? 'expanded' : 'collapsed');
            },

            closePopout(windowId) {
                const window = document.getElementById(windowId);
                if (!window) return;

                const sessionId = window.dataset.sessionId;

                // Track close event
                this.trackCardMovement(sessionId, 'closed', {
                    windowId: windowId,
                    timestamp: new Date().toISOString(),
                    user: this.getCurrentUser()
                });

                // Animate close
                window.style.transition = 'all 0.3s ease';
                window.style.opacity = '0';
                window.style.transform = 'scale(0.9)';

                setTimeout(() => window.remove(), 300);

                console.log('Popout window closed');
            },

            // ============================================
            // INLINE EDITING FOR POPUP WINDOWS
            // ============================================

            togglePopupEdit(windowId, sessionId) {
                console.log(' Toggling popup edit mode:', windowId, sessionId);

                const popoutWindow = document.getElementById(windowId);
                if (!popoutWindow) return;

                const isEditing = popoutWindow.classList.contains('popup-edit-mode');

                if (isEditing) {
                    // Cancel edit mode
                    this.cancelPopupEdit(windowId, sessionId);
                } else {
                    // Enter edit mode
                    this.enablePopupEdit(windowId, sessionId);
                }
            },

            enablePopupEdit(windowId, sessionId) {
                const popoutWindow = document.getElementById(windowId);
                if (!popoutWindow) return;

                const session = this.sessions.find(s => s.session_id === sessionId);
                if (!session) return;

                // Mark as editing
                popoutWindow.classList.add('popup-edit-mode');

                // Re-render with editable fields
                const priorityEmoji = { 'critical': '<i class="fas fa-exclamation-circle" style="color: #dc2626;"></i>', 'high': '<i class="fas fa-circle" style="color: #ef4444;"></i>', 'medium': '<i class="fas fa-circle" style="color: #fbbf24;"></i>', 'low': '<i class="fas fa-circle" style="color: #22c55e;"></i>' }[session.priority] || '<i class="fas fa-circle" style="color: #9ca3af;"></i>';
                const statusClass = {
                    'active': 'status-active',
                    'paused': 'status-paused',
                    'completed': 'status-completed'
                }[session.status] || 'status-active';
                const timeAgo = this.formatTimeAgo(session.last_active);

                const contentArea = popoutWindow.querySelector('.popout-card-content');
                if (contentArea) {
                    contentArea.innerHTML = this.renderCardExpandedEditable(session, priorityEmoji, statusClass, timeAgo);
                }

                // Update header buttons
                const header = popoutWindow.querySelector('.popout-card-header');
                if (header) {
                    const controlsArea = header.querySelector('.popout-card-controls');
                    controlsArea.innerHTML = `
                        <button class="popout-control-btn save" onclick="synergyBoard.savePopupEdit('${windowId}', '${sessionId}')" title="Save Changes">
                            <i class="fas fa-save"></i>
                        </button>
                        <button class="popout-control-btn cancel" onclick="synergyBoard.cancelPopupEdit('${windowId}', '${sessionId}')" title="Cancel">
                            <i class="fas fa-times"></i>
                        </button>
                    `;
                }

                console.log('✅ Popup edit mode enabled');
            },

            async savePopupEdit(windowId, sessionId) {
                console.log(' Saving popup edits:', windowId, sessionId);

                const popoutWindow = document.getElementById(windowId);
                if (!popoutWindow) return;

                // Collect values from editable fields
                const updates = this.collectPopupEditValues(popoutWindow);

                try {
                    // Call API to save
                    await this.apiEditCard(sessionId, updates);

                    // Exit edit mode and re-render
                    popoutWindow.classList.remove('popup-edit-mode');

                    const session = this.sessions.find(s => s.session_id === sessionId);
                    if (session) {
                        Object.assign(session, updates);

                        const priorityEmoji = { 'critical': '<i class="fas fa-exclamation-circle" style="color: #dc2626;"></i>', 'high': '<i class="fas fa-circle" style="color: #ef4444;"></i>', 'medium': '<i class="fas fa-circle" style="color: #fbbf24;"></i>', 'low': '<i class="fas fa-circle" style="color: #22c55e;"></i>' }[session.priority] || '<i class="fas fa-circle" style="color: #9ca3af;"></i>';
                        const statusClass = {
                            'active': 'status-active',
                            'paused': 'status-paused',
                            'completed': 'status-completed'
                        }[session.status] || 'status-active';
                        const timeAgo = this.formatTimeAgo(session.last_active);

                        const contentArea = popoutWindow.querySelector('.popout-card-content');
                        if (contentArea) {
                            contentArea.innerHTML = this.renderCardExpanded(session, priorityEmoji, statusClass, timeAgo);
                        }
                    }

                    // Restore header controls
                    const header = popoutWindow.querySelector('.popout-card-header');
                    if (header) {
                        const controlsArea = header.querySelector('.popout-card-controls');
                        controlsArea.innerHTML = `
                            <button class="popout-control-btn edit" onclick="synergyBoard.togglePopupEdit('${windowId}', '${sessionId}')" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="popout-control-btn delete" onclick="synergyBoard.deleteCardFromPopup('${windowId}', '${sessionId}')" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                            <button class="popout-control-btn close" onclick="synergyBoard.closePopout('${windowId}')" title="Close">
                                <i class="fas fa-times"></i>
                            </button>
                        `;
                    }

                    console.log('✅ Popup changes saved');
                    this.showNotification('Changes saved successfully', 'success');

                } catch (error) {
                    console.error('❌ Failed to save popup edits:', error);
                    this.showNotification('Failed to save changes', 'error');
                }
            },

            cancelPopupEdit(windowId, sessionId) {
                console.log('❌ Cancelling popup edit:', windowId, sessionId);

                const popoutWindow = document.getElementById(windowId);
                if (!popoutWindow) return;

                const session = this.sessions.find(s => s.session_id === sessionId);
                if (!session) return;

                // Exit edit mode
                popoutWindow.classList.remove('popup-edit-mode');

                // Re-render with original data
                const priorityEmoji = { 'critical': '<i class="fas fa-exclamation-circle" style="color: #dc2626;"></i>', 'high': '<i class="fas fa-circle" style="color: #ef4444;"></i>', 'medium': '<i class="fas fa-circle" style="color: #fbbf24;"></i>', 'low': '<i class="fas fa-circle" style="color: #22c55e;"></i>' }[session.priority] || '<i class="fas fa-circle" style="color: #9ca3af;"></i>';
                const statusClass = {
                    'active': 'status-active',
                    'paused': 'status-paused',
                    'completed': 'status-completed'
                }[session.status] || 'status-active';
                const timeAgo = this.formatTimeAgo(session.last_active);

                const contentArea = popoutWindow.querySelector('.popout-card-content');
                if (contentArea) {
                    contentArea.innerHTML = this.renderCardExpanded(session, priorityEmoji, statusClass, timeAgo);
                }

                // Restore header controls
                const header = popoutWindow.querySelector('.popout-card-header');
                if (header) {
                    const controlsArea = header.querySelector('.popout-card-controls');
                    controlsArea.innerHTML = `
                        <button class="popout-control-btn edit" onclick="synergyBoard.togglePopupEdit('${windowId}', '${sessionId}')" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="popout-control-btn delete" onclick="synergyBoard.deleteCardFromPopup('${windowId}', '${sessionId}')" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                        <button class="popout-control-btn close" onclick="synergyBoard.closePopout('${windowId}')" title="Close">
                            <i class="fas fa-times"></i>
                        </button>
                    `;
                }

                console.log('✅ Popup edit cancelled');
            },

            collectPopupEditValues(popoutWindow) {
                const getValue = (selector) => {
                    const el = popoutWindow.querySelector(selector);
                    return el ? el.value || el.textContent : '';
                };

                const getArrayValue = (selector) => {
                    const value = getValue(selector);
                    return value ? value.split(',').map(s => s.trim()).filter(Boolean) : [];
                };

                return {
                    title: getValue('.edit-field-title'),
                    description: getValue('.edit-field-description'),
                    project_name: getValue('.edit-field-project'),
                    priority: getValue('.edit-field-priority'),
                    status: getValue('.edit-field-status'),
                    kanban_column: getValue('.edit-field-column'),
                    due_date: getValue('.edit-field-due-date'),
                    due_time: getValue('.edit-field-due-time'),
                    notes: getValue('.edit-field-notes'),
                    tags: getArrayValue('.edit-field-tags'),
                    assignees: getArrayValue('.edit-field-assignees'),
                    thread_ids: getArrayValue('.edit-field-thread-ids'),
                    assigned_agents: getArrayValue('.edit-field-assigned-agents')
                };
            },

            async deleteCardFromPopup(windowId, sessionId) {
                if (!confirm('Are you sure you want to delete this card? This action cannot be undone.')) {
                    return;
                }

                console.log('�� Deleting card from popup:', sessionId);

                try {
                    // Close popup first
                    this.closePopout(windowId);

                    // Delete the card
                    await this.deleteCard(sessionId);

                    console.log('✅ Card deleted successfully');
                    this.showNotification('Card deleted successfully', 'success');

                } catch (error) {
                    console.error('❌ Failed to delete card:', error);
                    this.showNotification('Failed to delete card', 'error');
                }
            },

            trackCardMovement(sessionId, action, metadata = {}) {
                const movementData = {
                    session_id: sessionId,
                    action: action,
                    metadata: metadata,
                    timestamp: new Date().toISOString(),
                    user: this.getCurrentUser()
                };

                console.log(' Card movement tracked:', movementData);

                // Store in session storage
                const key = `card_movements_${sessionId}`;
                const existing = JSON.parse(sessionStorage.getItem(key) || '[]');
                existing.push(movementData);
                sessionStorage.setItem(key, JSON.stringify(existing));

                // TODO: Send to API for persistent tracking
                // await fetch(`${this.apiBaseUrl}/api/sessions/${sessionId}/track-movement`, {
                //     method: 'POST',
                //     body: JSON.stringify(movementData)
                // });
            },

            getCurrentUser() {
                // Get from session or localStorage
                return sessionStorage.getItem('current_user') ||
                    localStorage.getItem('user_email') ||
                    'Anonymous';
            },

            // ==================== SUPABASE REAL-TIME METHODS ====================

            initializeSupabase() {
                try {
                    // Check if Supabase global config is available
                    if (!window.SUPABASE_URL || !window.SUPABASE_ANON_KEY) {
                        console.error('? [SYNERGY] Supabase configuration not found in window object');
                        this.updateRealtimeStatus('error', 'Configuration missing');
                        return;
                    }

                    // Check if Supabase library is loaded
                    if (typeof supabase === 'undefined' || typeof supabase.createClient !== 'function') {
                        console.error('? [SYNERGY] Supabase JS library not loaded');
                        this.updateRealtimeStatus('error', 'Library not loaded');
                        return;
                    }

                    const { createClient } = supabase;
                    this.supabaseClient = createClient(window.SUPABASE_URL, window.SUPABASE_ANON_KEY);
                    console.log('? [SYNERGY] Supabase client initialized');
                    this.updateRealtimeStatus('connecting', 'Connecting...');
                } catch (error) {
                    console.error('? [SYNERGY] Failed to initialize Supabase:', error);
                    this.updateRealtimeStatus('error', 'Connection failed');
                }
            },

            subscribeToRealtimeChanges() {
                // Check if config is loaded
                if (!window.SUPABASE_CONFIG_LOADED || !window.SUPABASE_ANON_KEY) {
                    console.warn('[SYNERGY] Supabase config not loaded yet, skipping real-time subscription');
                    return;
                }

                if (!this.supabaseClient) {
                    console.warn('[SYNERGY] Supabase client not initialized, skipping real-time subscription');
                    return;
                }

                // Prevent multiple simultaneous subscription attempts
                if (this.isSubscribing) {
                    console.log('[SYNERGY] Subscription already in progress, skipping...');
                    return;
                }
                this.isSubscribing = true;

                // Track retry attempts
                if (!this.realtimeRetryCount) {
                    this.realtimeRetryCount = 0;
                }

                // Stop retrying after 3 failed attempts
                if (this.realtimeRetryCount >= 3) {
                    console.warn('⚠️ [SYNERGY] Real-time subscription failed after 3 attempts');
                    console.warn('⚠️ [SYNERGY] Possible causes:');
                    console.warn('   1. Table not added to supabase_realtime publication');
                    console.warn('   2. Row Level Security blocking access');
                    console.warn('   3. Replica identity not set (for UPDATE/DELETE)');
                    console.warn('💡 [SYNERGY] Run this in SQL Editor:');
                    console.warn('   ALTER PUBLICATION supabase_realtime ADD TABLE synergy_sessions.synergy_sessions;');
                    console.warn('   ALTER TABLE synergy_sessions.synergy_sessions REPLICA IDENTITY FULL;');
                    console.warn('🔄 [SYNERGY] Falling back to auto-refresh polling (15s interval)');
                    // Start auto-refresh as fallback
                    this.startAutoRefresh();
                    return;
                }

                console.log(`[SYNERGY] Subscribing to real-time changes (attempt ${this.realtimeRetryCount + 1}/3)...`);

                // Remove existing channel if reconnecting
                if (this.realtimeChannel) {
                    this.supabaseClient.removeChannel(this.realtimeChannel);
                    this.realtimeChannel = null;
                }

                this.realtimeChannel = this.supabaseClient
                    .channel('synergy-realtime')
                    .on(
                        'postgres_changes',
                        {
                            event: '*',
                            schema: 'synergy_sessions',
                            table: 'synergy_sessions'
                        },
                        (payload) => {
                            console.log('[SYNERGY] Real-time update received:', payload.eventType, payload);
                            this.handleRealtimeChange(payload);
                        }
                    )
                    .subscribe((status) => {
                        console.log('[SYNERGY] Subscription status:', status);

                        if (status === 'SUBSCRIBED') {
                            console.log('✅ [SYNERGY] Successfully subscribed to real-time changes');
                            console.log('   Real-time updates active - polling disabled');
                            this.realtimeRetryCount = 0; // Reset retry count on success
                            this.isSubscribing = false; // Allow future subscriptions
                            this.isSubscribed = true; // Mark as subscribed
                            this.updateRealtimeStatus('connected', 'Live (Real-time)');
                        } else if (status === 'CHANNEL_ERROR') {
                            this.isSubscribing = false; // Allow retry
                            this.realtimeRetryCount++;
                            this.updateRealtimeStatus('error', 'Connection Error');

                            // Retry with exponential backoff
                            const retryDelay = Math.min(5000 * this.realtimeRetryCount, 15000);
                            console.warn(`[SYNERGY] Retrying in ${retryDelay / 1000} seconds...`);
                            setTimeout(() => this.subscribeToRealtimeChanges(), retryDelay);
                        } else if (status === 'TIMED_OUT') {
                            this.isSubscribing = false; // Allow retry
                            this.realtimeRetryCount++;
                            this.updateRealtimeStatus('error', 'Timed Out');
                            setTimeout(() => this.subscribeToRealtimeChanges(), 3000);
                        } else if (status === 'CLOSED') {
                            // Only reconnect if we were previously subscribed (disconnect, not initial state)
                            if (this.isSubscribed) {
                                console.log('[SYNERGY] Channel closed, attempting reconnect...');
                                this.isSubscribing = false; // Allow retry
                                this.isSubscribed = false; // Mark as disconnected
                                this.realtimeRetryCount++;
                                setTimeout(() => this.subscribeToRealtimeChanges(), 2000);
                            } else {
                                // Initial CLOSED state before SUBSCRIBED - ignore it
                                console.log('[SYNERGY] Initial channel state (CLOSED), waiting for SUBSCRIBED...');
                            }
                        }
                    });
            },

            handleRealtimeChange(payload) {
                const { eventType, new: newRecord, old: oldRecord } = payload;

                switch (eventType) {
                    case 'INSERT':
                        console.log('? [SYNERGY] New session inserted:', newRecord);
                        this.addCardToBoard(newRecord);
                        this.updateStats();
                        this.showSyncIndicator('success', 'New card added', 2000);

                        // Send real-time notification
                        if (typeof NotificationSystem !== 'undefined') {
                            NotificationSystem.addRealtimeNotification(
                                newRecord.session_id,
                                newRecord.title,
                                'session_created',
                                'New session created',
                                newRecord
                            );
                        }
                        break;

                    case 'UPDATE':
                        console.log('[SYNERGY] Session updated:', newRecord);

                        // Detect what changed for better notifications
                        const changes = this.detectUpdateChanges(oldRecord, newRecord);

                        this.updateExistingCard(newRecord);
                        this.updateStats();
                        this.showSyncIndicator('success', 'Card updated', 2000);

                        // Send real-time notification with specific change info
                        if (typeof NotificationSystem !== 'undefined' && changes.length > 0) {
                            changes.forEach(change => {
                                NotificationSystem.addRealtimeNotification(
                                    newRecord.session_id,
                                    newRecord.title,
                                    change.type,
                                    change.message,
                                    newRecord
                                );
                            });
                        }
                        break;

                    case 'DELETE':
                        console.log('?[SYNERGY] Session deleted:', oldRecord);
                        this.removeCardFromBoard(oldRecord.session_id);
                        this.updateStats();
                        this.showSyncIndicator('success', 'Card removed', 2000);

                        // Send real-time notification
                        if (typeof NotificationSystem !== 'undefined') {
                            NotificationSystem.addRealtimeNotification(
                                oldRecord.session_id,
                                oldRecord.title,
                                'session_deleted',
                                'Session deleted',
                                oldRecord
                            );
                        }
                        break;
                }
            },

            detectUpdateChanges(oldRecord, newRecord) {
                const changes = [];

                if (!oldRecord) return changes;

                // Status change
                if (oldRecord.status !== newRecord.status) {
                    changes.push({
                        type: 'status_change',
                        message: `Status changed from ${oldRecord.status} to ${newRecord.status}`
                    });
                }

                // Priority change
                if (oldRecord.priority !== newRecord.priority) {
                    changes.push({
                        type: 'priority_change',
                        message: `Priority changed from ${oldRecord.priority} to ${newRecord.priority}`
                    });
                }

                // Column change (moved)
                if (oldRecord.kanban_column !== newRecord.kanban_column) {
                    changes.push({
                        type: 'column_moved',
                        message: `Moved from ${oldRecord.kanban_column} to ${newRecord.kanban_column}`
                    });
                }

                // Title change
                if (oldRecord.title !== newRecord.title) {
                    changes.push({
                        type: 'title_change',
                        message: `Title updated`
                    });
                }

                // If no specific changes detected, show generic update
                if (changes.length === 0) {
                    changes.push({
                        type: 'session_updated',
                        message: 'Session updated'
                    });
                }

                return changes;
            },

            addCardToBoard(session) {
                // Check if card already exists (prevent duplicates)
                const existingCard = document.querySelector(`[data-session-id="${session.session_id}"]`);
                if (existingCard) {
                    console.log('[SYNERGY] Card already exists, updating instead:', session.session_id);
                    this.updateExistingCard(session);
                    return;
                }

                // Add to sessions array
                this.sessions.push(session);

                // Get target column
                const column = session.kanban_column || 'backlog';
                const columnContainer = document.querySelector(`[data-column="${column}"] .kanban-cards-container`);

                if (!columnContainer) {
                    console.warn('[SYNERGY] Column not found:', column);
                    return;
                }

                // Generate card HTML
                const cardHTML = this.generateCardHTML(session);
                columnContainer.insertAdjacentHTML('beforeend', cardHTML);

                console.log('? [SYNERGY] Card added to board:', session.session_id);
            },

            updateExistingCard(session) {
                const card = document.querySelector(`[data-session-id="${session.session_id}"]`);
                if (!card) {
                    console.warn('[SYNERGY] Card not found for update, adding as new:', session.session_id);
                    this.addCardToBoard(session);
                    return;
                }

                // Update in sessions array
                const index = this.sessions.findIndex(s => s.session_id === session.session_id);
                if (index !== -1) {
                    this.sessions[index] = session;
                }

                // Check if column changed (need to move card)
                const currentColumn = card.closest('.kanban-cards-container').dataset.column;
                const newColumn = session.kanban_column || 'backlog';

                if (currentColumn !== newColumn) {
                    // Move card to new column
                    const newColumnContainer = document.querySelector(`[data-column="${newColumn}"] .kanban-cards-container`);
                    if (newColumnContainer) {
                        card.remove();
                        const cardHTML = this.generateCardHTML(session);
                        newColumnContainer.insertAdjacentHTML('beforeend', cardHTML);
                        console.log('[SYNERGY] Card moved to new column:', session.session_id, currentColumn, '->', newColumn);
                        return;
                    }
                }

                // Update card content in place
                const newCardHTML = this.generateCardHTML(session);
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = newCardHTML;
                const newCard = tempDiv.firstElementChild;

                // Replace card while preserving position
                card.replaceWith(newCard);
                console.log('? [SYNERGY] Card updated in place:', session.session_id);
            },

            removeCardFromBoard(sessionId) {
                const card = document.querySelector(`[data-session-id="${sessionId}"]`);
                if (card) {
                    // Remove from sessions array
                    this.sessions = this.sessions.filter(s => s.session_id !== sessionId);

                    // Remove from DOM with animation
                    card.style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';
                    card.style.opacity = '0';
                    card.style.transform = 'scale(0.9)';

                    setTimeout(() => {
                        card.remove();
                        console.log('? [SYNERGY] Card removed from board:', sessionId);
                    }, 300);
                } else {
                    console.warn('[SYNERGY] Card not found for removal:', sessionId);
                }
            },

            updateRealtimeStatus(status, text) {
                const statusContainer = document.getElementById('realtime-status');
                const statusIcon = document.getElementById('realtime-status-icon');
                const statusText = document.getElementById('realtime-status-text');

                if (!statusContainer || !statusIcon || !statusText) return;

                // Update icon and text
                statusText.textContent = text;

                // Update styling based on status
                statusContainer.className = 'realtime-status';
                statusIcon.className = 'fas fa-circle';

                switch (status) {
                    case 'connected':
                        statusContainer.classList.add('status-connected');
                        break;
                    case 'connecting':
                        statusContainer.classList.add('status-connecting');
                        break;
                    case 'error':
                        statusContainer.classList.add('status-error');
                        break;
                }
            },

            showRealtimeDiagnostics() {
                const diagnosticInfo = {
                    status: this.realtimeChannel?.state || 'Not initialized',
                    retryCount: this.realtimeRetryCount || 0,
                    maxRetries: 3,
                    supabaseConnected: !!this.supabaseClient,
                    channelName: this.realtimeChannel?.topic || 'N/A'
                };

                const sqlFix = `-- Run in Supabase SQL Editor:
ALTER PUBLICATION supabase_realtime ADD TABLE synergy_sessions.synergy_sessions;
ALTER TABLE synergy_sessions.synergy_sessions REPLICA IDENTITY FULL;

-- Verify:
SELECT * FROM pg_publication_tables 
WHERE pubname = 'supabase_realtime' 
AND schemaname = 'synergy_sessions'
AND tablename = 'synergy_sessions';`;

                const message = `
                    <div style="text-align: left; font-family: monospace; font-size: 12px;">
                        <h3 style="margin-top: 0;">Realtime Diagnostics</h3>
                        
                        <p><strong>Current Status:</strong> ${diagnosticInfo.status}</p>
                        <p><strong>Retry Attempts:</strong> ${diagnosticInfo.retryCount}/${diagnosticInfo.maxRetries}</p>
                        <p><strong>Supabase Client:</strong> ${diagnosticInfo.supabaseConnected ? '? Connected' : '? Not connected'}</p>
                        <p><strong>Channel Name:</strong> ${diagnosticInfo.channelName}</p>
                        
                        <hr style="margin: 16px 0;">
                        
                        <h4>Common Issues & Fixes:</h4>
                        <ol style="margin: 8px 0; padding-left: 20px;">
                            <li><strong>Table not in publication</strong><br>
                                Go to Supabase Dashboard ? Database ? Publications<br>
                                Add <code>synergy_sessions</code> to <code>supabase_realtime</code>
                            </li>
                            <li><strong>RLS blocking access</strong><br>
                                Ensure there's a policy allowing SELECT for authenticated users
                            </li>
                            <li><strong>Replica identity not set</strong><br>
                                Required for UPDATE/DELETE events
                            </li>
                        </ol>
                        
                        <h4>SQL Fix (Copy & Run in Supabase):</h4>
                        <pre style="background: #1e1e1e; color: #d4d4d4; padding: 12px; border-radius: 4px; overflow-x: auto;">${sqlFix}</pre>
                        
                        <p style="margin-top: 16px;"><strong>Docs:</strong> <a href="https://supabase.com/docs/guides/realtime/postgres-changes" target="_blank">Supabase Realtime Guide</a></p>
                    </div>
                `;

                showAlert(message, 'info');
            },

            manualRefresh() {
                console.log('[SYNERGY] Manual refresh triggered');

                // Show loading indicator
                const refreshBtn = document.getElementById('manual-refresh-btn');
                if (refreshBtn) {
                    const icon = refreshBtn.querySelector('i');
                    icon.classList.add('fa-spin');
                }

                // Reload sessions
                this.loadSessions().then(() => {
                    console.log('? [SYNERGY] Manual refresh complete');

                    // Stop spin animation
                    if (refreshBtn) {
                        const icon = refreshBtn.querySelector('i');
                        setTimeout(() => icon.classList.remove('fa-spin'), 500);
                    }

                    // Show success message
                    this.showSyncIndicator('success', 'Sessions refreshed', 2000);
                }).catch(error => {
                    console.error('? [SYNERGY] Manual refresh failed:', error);

                    // Stop spin animation
                    if (refreshBtn) {
                        const icon = refreshBtn.querySelector('i');
                        icon.classList.remove('fa-spin');
                    }

                    showAlert('Failed to refresh sessions: ' + error.message, 'error');
                });
            },

            startAutoRefresh() {
                // Auto-refresh every 15 seconds as fallback (when Realtime unavailable)
                if (this.autoRefreshInterval) {
                    clearInterval(this.autoRefreshInterval);
                }

                this.autoRefreshInterval = setInterval(async () => {
                    console.log('[SYNERGY] Auto-refresh (15s interval)...');
                    await this.smartRefresh();
                }, 15000); // 15 seconds

                // Set status to green with "Auto-refresh" text
                this.updateRealtimeStatus('connected', 'Auto-refresh (15s)');
                console.log('? [SYNERGY] Auto-refresh enabled (every 15 seconds)');
            },

            async smartRefresh() {
                // Smart refresh that only updates what changed
                try {
                    // Save current UI state
                    const expandedCards = new Set();
                    const scrollPositions = {};

                    document.querySelectorAll('.kanban-card[data-expanded="true"]').forEach(card => {
                        expandedCards.add(card.dataset.sessionId);
                    });

                    ['backlog', 'in_progress', 'review', 'done'].forEach(column => {
                        const container = document.getElementById(`${column}-cards`);
                        if (container && container.parentElement) {
                            scrollPositions[column] = container.parentElement.scrollTop;
                        }
                    });

                    // Load fresh data
                    const oldSessions = [...this.sessions];
                    await this.loadSessions();

                    // Detect changes
                    const changes = this.detectChanges(oldSessions, this.sessions);

                    if (changes.added.length === 0 && changes.updated.length === 0 && changes.removed.length === 0) {
                        console.log('? [SYNERGY] No changes detected');
                        return;
                    }

                    console.log(`[SYNERGY] Changes detected: ${changes.added.length} added, ${changes.updated.length} updated, ${changes.removed.length} removed`);

                    // Apply incremental updates
                    for (const sessionId of changes.removed) {
                        const card = document.querySelector(`.kanban-card[data-session-id="${sessionId}"]`);
                        if (card) {
                            card.style.opacity = '0';
                            setTimeout(() => card.remove(), 300);
                        }
                    }

                    for (const session of changes.added) {
                        await this.renderCard(session);
                        const card = document.querySelector(`.kanban-card[data-session-id="${session.session_id}"]`);
                        if (card) {
                            card.style.opacity = '0';
                            setTimeout(() => card.style.opacity = '1', 50);
                        }
                    }

                    for (const session of changes.updated) {
                        const card = document.querySelector(`.kanban-card[data-session-id="${session.session_id}"]`);
                        if (card) {
                            // Check if card moved columns
                            const currentColumn = card.closest('.kanban-cards-container')?.parentElement?.dataset?.column;
                            if (currentColumn !== session.kanban_column) {
                                // Card moved - remove and re-render
                                card.remove();
                                await this.renderCard(session);
                            } else {
                                // Update in place
                                this.updateCardInPlace(card, session);
                            }
                        }
                    }

                    // Restore UI state
                    expandedCards.forEach(sessionId => {
                        const card = document.querySelector(`.kanban-card[data-session-id="${sessionId}"]`);
                        if (card) card.dataset.expanded = 'true';
                    });

                    Object.entries(scrollPositions).forEach(([column, scrollTop]) => {
                        const container = document.getElementById(`${column}-cards`);
                        if (container && container.parentElement) {
                            container.parentElement.scrollTop = scrollTop;
                        }
                    });

                    // Update stats
                    this.updateStats();
                    this.updateColumnCounts();

                } catch (error) {
                    console.error('? [SYNERGY] Smart refresh failed:', error);
                }
            },

            detectChanges(oldSessions, newSessions) {
                const oldMap = new Map(oldSessions.map(s => [s.session_id, s]));
                const newMap = new Map(newSessions.map(s => [s.session_id, s]));

                const added = [];
                const updated = [];
                const removed = [];

                // Find added and updated
                newSessions.forEach(newSession => {
                    const oldSession = oldMap.get(newSession.session_id);
                    if (!oldSession) {
                        added.push(newSession);
                    } else if (JSON.stringify(oldSession) !== JSON.stringify(newSession)) {
                        updated.push(newSession);
                    }
                });

                // Find removed
                oldSessions.forEach(oldSession => {
                    if (!newMap.has(oldSession.session_id)) {
                        removed.push(oldSession.session_id);
                    }
                });

                return { added, updated, removed };
            },

            updateCardInPlace(cardElement, session) {
                // Update only changed elements without full re-render
                const titleEl = cardElement.querySelector('.kanban-card-title');
                if (titleEl && titleEl.textContent !== session.title) {
                    titleEl.textContent = session.title;
                }

                const statusBadge = cardElement.querySelector('.kanban-status-badge');
                if (statusBadge) {
                    statusBadge.className = `kanban-status-badge status-${session.status}`;
                    statusBadge.textContent = session.status.charAt(0).toUpperCase() + session.status.slice(1);
                }

                const priorityBadge = cardElement.querySelector('.kanban-priority-badge');
                if (priorityBadge) {
                    priorityBadge.className = `kanban-priority-badge priority-${session.priority}`;
                    priorityBadge.textContent = session.priority.charAt(0).toUpperCase() + session.priority.slice(1);
                }

                // Update other fields as needed
                console.log(`? [SYNERGY] Updated card ${session.session_id} in place`);
            },

            showSyncIndicator(type, message, duration = null) {
                let indicator = document.getElementById('sync-indicator');

                if (!indicator) {
                    indicator = document.createElement('div');
                    indicator.id = 'sync-indicator';
                    indicator.className = 'sync-indicator';
                    indicator.innerHTML = `
                                                                                                                                        <div class="sync-spinner"></div>
                                                                                                                                        <span class="sync-message"></span>
                                                                                                                                        `;
                    document.body.appendChild(indicator);
                }

                const messageEl = indicator.querySelector('.sync-message');
                if (messageEl) messageEl.textContent = message;

                indicator.className = `sync-indicator show ${type}`;

                if (duration) {
                    setTimeout(() => {
                        indicator.classList.remove('show');
                    }, duration);
                }
            },

            formatTimeAgo(timestamp) {
                if (!timestamp) return 'Never';

                const now = new Date();
                const then = new Date(timestamp);
                const seconds = Math.floor((now - then) / 1000);

                if (seconds < 60) return 'just now';
                if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
                if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
                if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
                return `${Math.floor(seconds / 604800)}w ago`;
            },

            escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            },

            parseJsonField(field, fallback = []) {
                // Handle null or undefined
                if (field === null || field === undefined) {
                    return fallback;
                }

                // Already an array - return as-is (backend already parsed it)
                if (Array.isArray(field)) {
                    return field;
                }

                // Already an object - return as-is (backend already parsed it)  
                if (typeof field === 'object' && field !== null) {
                    return field;
                }

                // Handle JSON string (only for legacy data)
                if (typeof field === 'string' && field.trim()) {
                    try {
                        const parsed = JSON.parse(field);
                        // Return parsed value directly - backend handles type correctness
                        return parsed;
                    } catch (e) {
                        // Not valid JSON, return fallback
                        return fallback;
                    }
                }

                // Empty string or non-string primitive
                return fallback;
            },

            /**
             * Render a single milestone with tasks and subtasks
             */
            renderMilestone(milestone, milestoneNumber, sessionId) {
                const tasks = milestone.tasks || [];
                const completedTasks = tasks.filter(t => t.completed).length;
                const blockedTasks = tasks.filter(t => t.blocked).length;

                return `
                    <div class="milestone-card" style="background: var(--bg-secondary); border: 1px solid var(--border-default); border-radius: 8px; padding: 16px;">
                        <div class="milestone-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <input type="checkbox" ${milestone.completed ? 'checked' : ''} 
                                    onclick="synergyBoard.toggleMilestone('${sessionId}', '${milestone.milestone_id}')"
                                    style="width: 18px; height: 18px; cursor: pointer;">
                                <span style="font-weight: 600; font-size: 15px; ${milestone.completed ? 'text-decoration: line-through; opacity: 0.7;' : ''}">
                                    M${milestoneNumber}: ${this.escapeHtml(milestone.milestone_name)}
                                </span>
                            </div>
                            <div style="display: flex; gap: 8px; align-items: center;">
                                ${blockedTasks > 0 ? '<span style="background: #dc2626; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;"><i class="fas fa-hand-paper"></i> ' + blockedTasks + ' BLOCKED</span>' : ''}
                                <span style="font-size: 12px; opacity: 0.8;">${completedTasks}/${tasks.length} tasks</span>
                            </div>
                        </div>
                        ${milestone.description ? `<div style="font-size: 13px; opacity: 0.8; margin-bottom: 12px;">${this.escapeHtml(milestone.description)}</div>` : ''}
                        ${tasks.length > 0 ? `
                            <div class="milestone-tasks" style="display: flex; flex-direction: column; gap: 8px;">
                                ${tasks.map((task, idx) => this.renderTask(task, milestoneNumber, idx + 1, sessionId)).join('')}
                            </div>
                        ` : '<div style="opacity: 0.6; font-style: italic; font-size: 12px;">No tasks yet</div>'}
                    </div>
                `;
            },

            /**
             * Render a single task with subtasks
             */
            renderTask(task, milestoneNumber, taskNumber, sessionId) {
                const subtasks = task.subtasks || [];
                const completedSubtasks = subtasks.filter(s => s.completed).length;

                return `
                    <div class="task-item" style="background: var(--bg-tertiary); border-left: 3px solid ${task.blocked ? '#dc2626' : task.completed ? '#22c55e' : 'var(--accent-primary)'}; padding: 10px; border-radius: 4px; ${task.completed ? 'opacity: 0.7;' : ''}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: ${subtasks.length > 0 ? '8px' : '0'};">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <input type="checkbox" ${task.completed ? 'checked' : ''} ${task.blocked ? 'disabled' : ''}
                                    onclick="synergyBoard.toggleTask('${sessionId}', '${task.task_id}')"
                                    style="width: 16px; height: 16px; cursor: ${task.blocked ? 'not-allowed' : 'pointer'};">
                                <span style="font-size: 14px; ${task.completed ? 'text-decoration: line-through;' : ''}">
                                    T${milestoneNumber}.${taskNumber}: ${this.escapeHtml(task.task)}
                                </span>
                            </div>
                            ${task.blocked ? `<span style="background: #dc2626; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: 600;" title="${this.escapeHtml(task.blocker_reason || 'Task is blocked')}"><i class="fas fa-hand-paper"></i> BLOCKED</span>` : ''}
                        </div>
                        ${task.blocked && task.blocker_reason ? `<div style="font-size: 11px; color: #dc2626; margin-left: 24px; font-style: italic;">${this.escapeHtml(task.blocker_reason)}</div>` : ''}
                        ${subtasks.length > 0 ? `
                            <div class="subtasks-list" style="margin-left: 24px; display: flex; flex-direction: column; gap: 6px;">
                                ${subtasks.map((subtask, idx) => `
                                    <div style="display: flex; align-items: center; gap: 6px; font-size: 13px;">
                                        <input type="checkbox" ${subtask.completed ? 'checked' : ''}
                                            onclick="synergyBoard.toggleSubtask('${sessionId}', '${subtask.subtask_id}')"
                                            style="width: 14px; height: 14px; cursor: pointer;">
                                        <span style="${subtask.completed ? 'text-decoration: line-through; opacity: 0.7;' : ''}">
                                            S${milestoneNumber}.${taskNumber}.${idx + 1}: ${this.escapeHtml(subtask.task)}
                                        </span>
                                    </div>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                `;
            },

            /**
             * Render linked threads with agent badges
             * SYNERGY INTEGRATION FEATURE - Shows threads connected to this project
             */
            async renderLinkedThreads(threadIds) {
                if (!threadIds || !Array.isArray(threadIds) || threadIds.length === 0) {
                    return '<div class="no-threads"><i class="fas fa-link-slash"></i> No threads linked</div>';
                }

                // Check if ThreadManager is available
                if (!window.ThreadManager) {
                    console.error('[SYNERGY] ThreadManager not available');
                    return `<div class="threads-loading"><i class="fas fa-spinner fa-spin"></i> Loading ThreadManager...</div>`;
                }

                try {
                    // Fetch thread details and agent assignments
                    // Silently handle errors - don't show connection lost notifications
                    let response;
                    try {
                        response = await fetch(`${this.apiBaseUrl}/api/threads/details`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ thread_ids: threadIds })
                        });
                    } catch (fetchError) {
                        // Network error - silently return fallback UI
                        console.warn('[SYNERGY] Network error fetching thread details (suppressed notification)');
                        return `<div class="threads-error"><i class="fas fa-exclamation-triangle"></i> ${threadIds.length} thread(s) linked</div>`;
                    }

                    if (!response.ok) {
                        console.warn('[SYNERGY] Failed to fetch thread details (HTTP ' + response.status + ')');
                        return `<div class="threads-error"><i class="fas fa-exclamation-triangle"></i> ${threadIds.length} thread(s) linked</div>`;
                    }

                    const result = await response.json();
                    const threads = result.data || result; // Handle both {success, data} format and direct array

                    if (!threads || threads.length === 0) {
                        return '<div class="no-threads"><i class="fas fa-link-slash"></i> No threads found</div>';
                    }

                    // Fetch synergy metadata for threads (like thread history does)
                    const synergyIdsToLoad = Array.from(new Set(threads
                        .map(t => t.synergy_card_id)
                        .filter(Boolean)));

                    // Use global synergy session cache
                    if (!window._synergySessionCache) window._synergySessionCache = {};
                    const cache = window._synergySessionCache;

                    if (synergyIdsToLoad.length > 0) {
                        try {
                            const missing = synergyIdsToLoad.filter(id => !cache[id]);
                            if (missing.length > 0) {
                                const idsParam = missing.join(',');
                                const resp = await fetch(`${this.apiBaseUrl}/api/synergy?ids=${encodeURIComponent(idsParam)}`);
                                if (resp.ok) {
                                    const data = await resp.json();
                                    if (data && data.success && data.sessions) {
                                        Object.entries(data.sessions).forEach(([sid, session]) => {
                                            cache[sid] = session;
                                        });
                                    }
                                }
                            }
                        } catch (err) {
                            console.warn('[SYNERGY] Failed to fetch synergy metadata:', err);
                        }
                    }

                    // Build unified thread-info containers for each thread
                    const threadsHTML = threads.map(thread => {
                        // Get synergy metadata from cache (like thread history does)
                        const synergyMeta = thread.synergy_card_id ? cache[thread.synergy_card_id] : null;
                        const synergyTitle = synergyMeta ? (synergyMeta.title || thread.synergy_card_id) : (thread.synergy_card_name || thread.synergy_card_id || 'Unknown Session');
                        const synergyPriority = synergyMeta ? (synergyMeta.priority || '') : '';
                        const synergyDesc = synergyMeta ? (synergyMeta.description || '') : '';
                        const synergyUsers = synergyMeta ? (Array.isArray(synergyMeta.assignees) ? synergyMeta.assignees.join(', ') : '') : '';
                        const synergyUpdated = synergyMeta ? (synergyMeta.last_active ? new Date(synergyMeta.last_active).toLocaleString() : '') : '';

                        // Normalize thread object structure for ThreadManager
                        // CRITICAL: Use thread_slug (the actual slug like "1762828793392") NOT id (numeric DB ID like 18)
                        const normalizedThread = {
                            id: thread.thread_slug || thread.id,  // FIXED: Prioritize slug over numeric ID
                            title: thread.name || thread.thread_slug || thread.id,
                            created: thread.created_at || thread.created,
                            updated: thread.updated_at || thread.updated,
                            message_count: thread.message_count || 0,
                            messages: [],
                            tags: thread.tags || [],
                            synergy_card_id: thread.synergy_card_id,
                            synergy_card_name: synergyTitle,
                            synergy_card_desc: synergyDesc,
                            synergy_card_users: synergyUsers,
                            synergy_card_updated: synergyUpdated,
                            synergy_card_priority: synergyPriority,
                            agent: thread.agent_id || 'prime'
                        };

                        // Temporarily add to ThreadManager.threads if not exists (for rendering)
                        const existingThread = window.ThreadManager.threads.find(t => t.id === normalizedThread.id);
                        if (!existingThread) {
                            window.ThreadManager.threads.push(normalizedThread);
                        }

                        // Render unified container
                        const threadInfoHTML = window.ThreadManager.renderThreadInfoContainer(
                            'synergy',
                            normalizedThread.id,
                            true  // compact mode
                        );

                        return `
                            <div class="synergy-linked-thread-wrapper" 
                                 data-thread-id="${normalizedThread.id}"
                                 draggable="true"
                                 ondragstart="ThreadManager.handleDragStart(event)"
                                 onclick="synergyBoard.openThread('${normalizedThread.id}', '${thread.agent_id || 'prime'}')">
                                ${threadInfoHTML}
                            </div>
                        `;
                    }).join('');

                    return `
                        <div class="linked-threads-container">
                            <div class="linked-threads-list">
                                ${threadsHTML}
                            </div>
                        </div>
                    `;

                } catch (error) {
                    console.error('[SYNERGY] Error rendering linked threads:', error);
                    return `<div class="threads-error"><i class="fas fa-exclamation-triangle"></i> Error loading threads</div>`;
                }
            },

            /**
             * Open a thread in the appropriate agent column
             */
            openThread(threadId, agentId) {
                console.log(`[SYNERGY] Opening thread ${threadId} in agent ${agentId}`);

                // Switch to AI Agents tab
                const agentsTab = document.querySelector('[data-tab="agents"]');
                if (agentsTab) {
                    agentsTab.click();
                }

                // Load thread in the agent column
                // This would need to integrate with your existing ThreadManager
                if (window.threadManager && typeof window.threadManager.loadThread === 'function') {
                    window.threadManager.loadThread(threadId, agentId);
                } else {
                    alert(`Would open thread: ${threadId} in agent: ${agentId}\n(ThreadManager integration pending)`);
                }
            },

            /**
             * Handle thread drop onto Synergy card
             */
            async handleThreadDrop(event, synergyId) {
                event.preventDefault();
                event.stopPropagation();
                event.currentTarget.classList.remove('drag-over');

                // Get dropped thread ID
                const threadId = event.dataTransfer.getData('text/plain');
                if (!threadId) {
                    console.warn('[SYNERGY] No thread ID in drop event');
                    return;
                }

                console.log(`[SYNERGY] Thread ${threadId} dropped on session ${synergyId}`);

                // Hide welcome container when thread is dropped into Prime
                const welcomeContainer = document.getElementById('prime-welcome-container');
                if (welcomeContainer) {
                    welcomeContainer.style.display = 'none';
                    console.log('[WELCOME] Hidden - thread dropped into chat');
                }

                try {
                    // Link thread to synergy card
                    const userId = (window.UserAuth && window.UserAuth.user && (window.UserAuth.user.id || window.UserAuth.user.user_id)) || 1;
                    const response = await fetch(`${this.apiBaseUrl}/api/synergy/${synergyId}/link-thread`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            thread_id: threadId,
                            user_id: userId
                        })
                    });

                    const result = await response.json();

                    if (result.success) {
                        console.log('[SYNERGY] Thread linked successfully');
                        if (window.showNotification) {
                            window.showNotification('Thread linked to Synergy card', 'success');
                        }

                        // Refresh the specific card's linked threads section
                        await this.refreshCardThreads(synergyId);
                    } else {
                        console.error('[SYNERGY] Failed to link thread:', result.error);
                        if (window.showNotification) {
                            window.showNotification('Failed to link thread: ' + (result.error || 'Unknown error'), 'error');
                        }
                    }
                } catch (error) {
                    console.error('[SYNERGY] Error linking thread:', error);
                    if (window.showNotification) {
                        window.showNotification('Error linking thread', 'error');
                    }
                }
            },

            // Refresh linked threads section for a specific card
            async refreshCardThreads(sessionId) {
                console.log(`[SYNERGY] Refreshing threads for card ${sessionId}`);

                try {
                    // Fetch updated session data
                    const response = await fetch(`${this.apiBaseUrl}/api/synergy/${sessionId}`);
                    if (!response.ok) {
                        console.warn('[SYNERGY] Failed to fetch session for refresh');
                        return;
                    }

                    const result = await response.json();
                    const session = result.session || result;

                    if (!session) {
                        console.warn('[SYNERGY] No session data returned');
                        return;
                    }

                    // Parse thread IDs
                    const threadIds = this.parseJsonField(session.thread_ids, []);
                    const threadsSection = document.getElementById(`threads-section-${sessionId}`);

                    if (!threadsSection) {
                        console.warn(`[SYNERGY] threads-section-${sessionId} not found in DOM`);
                        return;
                    }

                    // Find or create the container for threads
                    let container = threadsSection.querySelector('.thread-list-loading, .thread-list, .no-threads, .drop-zone-prompt');

                    if (threadIds.length > 0) {
                        // Show loading temporarily
                        if (container) {
                            container.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading linked threads...';
                        }

                        // Render threads
                        const threadsHTML = await this.renderLinkedThreads(threadIds);
                        if (container) {
                            container.outerHTML = threadsHTML;
                        } else {
                            threadsSection.insertAdjacentHTML('beforeend', threadsHTML);
                        }
                    } else {
                        // No threads: show drag-and-drop prompt
                        if (container) {
                            container.innerHTML = '<i class="fas fa-hand-pointer"></i> Drag and drop a thread here to link';
                            container.className = 'thread-list-loading drop-zone-prompt';
                        }
                    }

                    console.log(`[SYNERGY] Refreshed threads for card ${sessionId}`);
                } catch (error) {
                    console.error('[SYNERGY] Error refreshing card threads:', error);
                }
            },

            // ============================================
            // EDIT MODAL FUNCTIONS
            // ============================================

            openEditModal(session) {
                console.log(' Opening edit modal for:', session.session_id || 'new session');

                const modal = document.getElementById('edit-card-modal');
                if (!modal) return;

                // Populate form fields
                document.getElementById('edit-session-id').value = session.session_id || '';
                document.getElementById('edit-title').value = session.title || '';
                document.getElementById('edit-description').value = session.description || '';
                document.getElementById('edit-project').value = session.project_name || '';
                document.getElementById('edit-priority').value = session.priority || 'medium';
                // Parse JSON fields safely
                const tags = this.parseJsonField(session.tags, []);
                const assignees = this.parseJsonField(session.assignees, []);
                const documents = this.parseJsonField(session.documents, []);
                const links = this.parseJsonField(session.links, []);
                const nextSteps = this.parseJsonField(session.next_steps, []);
                const checklist = this.parseJsonField(session.checklist, []);
                const threadIds = this.parseJsonField(session.thread_ids, []);
                const assignedAgents = this.parseJsonField(session.assigned_agents, []);

                document.getElementById('edit-status').value = session.status || 'active';
                document.getElementById('edit-column').value = session.kanban_column || 'backlog';
                document.getElementById('edit-tags').value = tags.length > 0 ? tags.join(', ') : '';
                document.getElementById('edit-notes').value = session.notes || '';
                document.getElementById('edit-assignees').value = assignees.length > 0 ? assignees.join(', ') : '';
                document.getElementById('edit-thread-ids').value = threadIds.length > 0 ? threadIds.join(', ') : '';
                document.getElementById('edit-assigned-agents').value = assignedAgents.length > 0 ? assignedAgents.join(', ') : '';

                // Due date and time
                if (session.due_date) {
                    const date = new Date(session.due_date);
                    document.getElementById('edit-due-date').value = date.toISOString().split('T')[0];
                    const hours = date.getHours().toString().padStart(2, '0');
                    const minutes = date.getMinutes().toString().padStart(2, '0');
                    document.getElementById('edit-due-time').value = `${hours}:${minutes}`;
                }

                // Populate documents
                const docsList = document.getElementById('documents-list');
                docsList.innerHTML = '';
                if (documents.length > 0) {
                    documents.forEach((doc, idx) => {
                        this.addDocumentField(doc.title, doc.url, doc.type);
                    });
                }

                // Populate links
                const linksList = document.getElementById('links-list');
                linksList.innerHTML = '';
                if (links.length > 0) {
                    links.forEach((link, idx) => {
                        this.addLinkField(link.title, link.url, link.type);
                    });
                }

                // Populate next steps with sub-checklists
                const stepsList = document.getElementById('next-steps-list');
                stepsList.innerHTML = '';
                if (nextSteps.length > 0) {
                    nextSteps.forEach((step, idx) => {
                        this.addNextStepField(step.description, step.due_date, step.completed, step.sub_checklist || []);
                    });
                }

                // Populate checklist with subtasks support
                const checklistList = document.getElementById('checklist-list');
                checklistList.innerHTML = '';
                if (checklist.length > 0) {
                    checklist.forEach((item, idx) => {
                        const taskText = item.task || item.item || item.text;
                        const subtasks = item.subtasks || [];
                        this.addChecklistField(taskText, item.completed, subtasks);
                    });
                }

                // Show modal
                modal.style.display = 'block';

                // Initialize drag functionality if not already done
                if (!modal.dataset.dragInitialized) {
                    this.initModalDrag();
                    modal.dataset.dragInitialized = 'true';
                }
            },

            closeEditModal() {
                const modal = document.getElementById('edit-card-modal');
                if (modal) modal.style.display = 'none';
            },

            // Initialize draggable modal functionality
            initModalDrag() {
                const modalContent = document.getElementById('edit-modal-content');
                const modalHeader = document.getElementById('edit-modal-header');

                if (!modalContent || !modalHeader) return;

                let isDragging = false;
                let currentX;
                let currentY;
                let initialX;
                let initialY;
                let xOffset = 0;
                let yOffset = 0;

                modalHeader.addEventListener('mousedown', dragStart);
                document.addEventListener('mousemove', drag);
                document.addEventListener('mouseup', dragEnd);

                function dragStart(e) {
                    // Don't drag if clicking on buttons
                    if (e.target.closest('button')) return;

                    initialX = e.clientX - xOffset;
                    initialY = e.clientY - yOffset;

                    if (e.target === modalHeader || e.target.closest('.modal-header h3')) {
                        isDragging = true;
                        modalContent.style.transition = 'none';
                    }
                }

                function drag(e) {
                    if (isDragging) {
                        e.preventDefault();

                        currentX = e.clientX - initialX;
                        currentY = e.clientY - initialY;

                        xOffset = currentX;
                        yOffset = currentY;

                        // Update position
                        modalContent.style.left = '50%';
                        modalContent.style.top = '10%';
                        modalContent.style.transform = `translate(calc(-50% + ${currentX}px), ${currentY}px)`;
                    }
                }

                function dragEnd(e) {
                    if (isDragging) {
                        initialX = currentX;
                        initialY = currentY;
                        isDragging = false;
                    }
                }
            },

            /**
             * Calculate display number for an item (e.g., "1", "1.2", "2.3")
             * @param {number} index - Index within siblings
             * @param {string} parentNumber - Parent's display number (optional)
             * @returns {string} Display number like "1" or "1.2"
             */
            getDisplayNumber(index, parentNumber = null) {
                const displayIndex = index + 1;
                return parentNumber ? `${parentNumber}.${displayIndex}` : `${displayIndex}`;
            },

            addDocumentField(title = '', url = '', type = 'google_doc') {
                const container = document.getElementById('documents-list');
                const index = container.querySelectorAll('.item-row').length;
                const displayNumber = this.getDisplayNumber(index);
                const row = document.createElement('div');
                row.className = 'item-row';
                row.innerHTML = `
                                                                                                                                        <span class="item-number-badge">D${displayNumber}</span>
                                                                                                                                        <input type="text" class="form-control" placeholder="Document title" value="${this.escapeHtml(title)}">
                                                                                                                                            <input type="url" class="form-control" placeholder="URL" value="${this.escapeHtml(url)}">
                                                                                                                                                <select class="form-control" style="max-width: 180px;">
                                                                                                                                                    <optgroup label="Google">
                                                                                                                                                        <option value="google_doc" ${type === 'google_doc' ? 'selected' : ''}>Google Doc</option>
                                                                                                                                                        <option value="google_sheet" ${type === 'google_sheet' ? 'selected' : ''}>Google Sheet</option>
                                                                                                                                                        <option value="google_slides" ${type === 'google_slides' ? 'selected' : ''}>Google Slides</option>
                                                                                                                                                        <option value="google_form" ${type === 'google_form' ? 'selected' : ''}>Google Form</option>
                                                                                                                                                    </optgroup>
                                                                                                                                                    <optgroup label="Microsoft">
                                                                                                                                                        <option value="word" ${type === 'word' ? 'selected' : ''}>Word</option>
                                                                                                                                                        <option value="excel" ${type === 'excel' ? 'selected' : ''}>Excel</option>
                                                                                                                                                        <option value="powerpoint" ${type === 'powerpoint' ? 'selected' : ''}>PowerPoint</option>
                                                                                                                                                        <option value="onenote" ${type === 'onenote' ? 'selected' : ''}>OneNote</option>
                                                                                                                                                    </optgroup>
                                                                                                                                                    <optgroup label="Other">
                                                                                                                                                        <option value="pdf" ${type === 'pdf' ? 'selected' : ''}>PDF</option>
                                                                                                                                                        <option value="dashboard" ${type === 'dashboard' ? 'selected' : ''}>Dashboard</option>
                                                                                                                                                        <option value="spreadsheet" ${type === 'spreadsheet' ? 'selected' : ''}>Spreadsheet</option>
                                                                                                                                                        <option value="presentation" ${type === 'presentation' ? 'selected' : ''}>Presentation</option>
                                                                                                                                                        <option value="file" ${type === 'file' ? 'selected' : ''}>File</option>
                                                                                                                                                    </optgroup>
                                                                                                                                                </select>
                                                                                                                                                <button type="button" class="btn-remove-item" onclick="this.parentElement.remove()">
                                                                                                                                                    <i class="fas fa-trash"></i>
                                                                                                                                                </button>
                                                                                                                                                `;
                container.appendChild(row);
            },

            addLinkField(title = '', url = '', type = 'external') {
                const container = document.getElementById('links-list');
                const index = container.querySelectorAll('.item-row').length;
                const displayNumber = this.getDisplayNumber(index);
                const row = document.createElement('div');
                row.className = 'item-row';
                row.innerHTML = `
                                                                                                                                                <span class="item-number-badge">L${displayNumber}</span>
                                                                                                                                                <input type="text" class="form-control" placeholder="Link title" value="${this.escapeHtml(title)}">
                                                                                                                                                    <input type="url" class="form-control" placeholder="URL" value="${this.escapeHtml(url)}">
                                                                                                                                                        <select class="form-control" style="max-width: 180px;">
                                                                                                                                                            <optgroup label="Project Management">
                                                                                                                                                                <option value="notion" ${type === 'notion' ? 'selected' : ''}>Notion</option>
                                                                                                                                                                <option value="jira" ${type === 'jira' ? 'selected' : ''}>Jira</option>
                                                                                                                                                                <option value="asana" ${type === 'asana' ? 'selected' : ''}>Asana</option>
                                                                                                                                                                <option value="trello" ${type === 'trello' ? 'selected' : ''}>Trello</option>
                                                                                                                                                            </optgroup>
                                                                                                                                                            <optgroup label="Design & Development">
                                                                                                                                                                <option value="figma" ${type === 'figma' ? 'selected' : ''}>Figma</option>
                                                                                                                                                                <option value="github" ${type === 'github' ? 'selected' : ''}>GitHub</option>
                                                                                                                                                                <option value="gitlab" ${type === 'gitlab' ? 'selected' : ''}>GitLab</option>
                                                                                                                                                                <option value="codepen" ${type === 'codepen' ? 'selected' : ''}>CodePen</option>
                                                                                                                                                            </optgroup>
                                                                                                                                                            <optgroup label="Research & Reference">
                                                                                                                                                                <option value="research" ${type === 'research' ? 'selected' : ''}>Research</option>
                                                                                                                                                                <option value="documentation" ${type === 'documentation' ? 'selected' : ''}>Documentation</option>
                                                                                                                                                                <option value="tutorial" ${type === 'tutorial' ? 'selected' : ''}>Tutorial</option>
                                                                                                                                                                <option value="article" ${type === 'article' ? 'selected' : ''}>Article</option>
                                                                                                                                                            </optgroup>
                                                                                                                                                            <optgroup label="Analytics & Reporting">
                                                                                                                                                                <option value="analytics" ${type === 'analytics' ? 'selected' : ''}>Analytics</option>
                                                                                                                                                                <option value="dashboard" ${type === 'dashboard' ? 'selected' : ''}>Dashboard</option>
                                                                                                                                                                <option value="report" ${type === 'report' ? 'selected' : ''}>Report</option>
                                                                                                                                                            </optgroup>
                                                                                                                                                            <optgroup label="Other">
                                                                                                                                                                <option value="external" ${type === 'external' ? 'selected' : ''}>External</option>
                                                                                                                                                                <option value="reference" ${type === 'reference' ? 'selected' : ''}>Reference</option>
                                                                                                                                                            </optgroup>
                                                                                                                                                        </select>
                                                                                                                                                        <button type="button" class="btn-remove-item" onclick="this.parentElement.remove()">
                                                                                                                                                            <i class="fas fa-trash"></i>
                                                                                                                                                        </button>
                                                                                                                                                        `;
                container.appendChild(row);
            },

            addNextStepField(description = '', dueDate = '', completed = false, subChecklist = []) {
                const container = document.getElementById('next-steps-list');
                const index = container.querySelectorAll('.step-wrapper').length;
                const displayNumber = this.getDisplayNumber(index);
                const stepId = `step-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
                const dueDateValue = dueDate ? new Date(dueDate).toISOString().split('T')[0] : '';

                const stepWrapper = document.createElement('div');
                stepWrapper.className = 'step-wrapper';
                stepWrapper.dataset.displayNumber = displayNumber;
                stepWrapper.innerHTML = `
                                                                                                                                                        <div class="item-row step-main">
                                                                                                                                                            <span class="item-number-badge">N${displayNumber}</span>
                                                                                                                                                            <input type="checkbox" class="step-checkbox" ${completed ? 'checked' : ''}>
                                                                                                                                                                <input type="text" class="form-control step-description" placeholder="Step description" value="${this.escapeHtml(description)}">
                                                                                                                                                                    <input type="date" class="form-control" style="max-width: 150px;" value="${dueDateValue}">
                                                                                                                                                                        <button type="button" class="btn-add-subtask" onclick="synergyBoard.addSubChecklistItem('${stepId}')" title="Add sub-task">
                                                                                                                                                                            <i class="fas fa-plus"></i>
                                                                                                                                                                        </button>
                                                                                                                                                                        <button type="button" class="btn-remove-item" onclick="this.parentElement.parentElement.remove()">
                                                                                                                                                                            <i class="fas fa-trash"></i>
                                                                                                                                                                        </button>
                                                                                                                                                                    </div>
                                                                                                                                                                    <div class="sub-checklist" id="${stepId}"></div>
                                                                                                                                                                    `;

                container.appendChild(stepWrapper);

                // Add existing sub-checklist items
                if (subChecklist && subChecklist.length > 0) {
                    subChecklist.forEach(item => {
                        this.addSubChecklistItem(stepId, item.item, item.completed);
                    });
                }
            },

            addSubChecklistItem(stepId, itemText = '', completed = false) {
                const container = document.getElementById(stepId);
                if (!container) return;

                const stepWrapper = container.closest('.step-wrapper');
                const parentNumber = stepWrapper ? stepWrapper.dataset.displayNumber : '';
                const subIndex = container.querySelectorAll('.sub-checklist-item').length;
                const displayNumber = this.getDisplayNumber(subIndex, parentNumber);

                const subItem = document.createElement('div');
                subItem.className = 'sub-checklist-item';
                subItem.innerHTML = `
                                                                                                                                                                    <span class="sub-number">N${displayNumber}</span>
                                                                                                                                                                    <input type="checkbox" class="sub-checkbox" ${completed ? 'checked' : ''}>
                                                                                                                                                                        <input type="text" class="form-control" placeholder="Sub-task" value="${this.escapeHtml(itemText)}">
                                                                                                                                                                            <button type="button" class="btn-remove-subtask" onclick="this.parentElement.remove()">
                                                                                                                                                                                <i class="fas fa-times"></i>
                                                                                                                                                                            </button>
                                                                                                                                                                            `;
                container.appendChild(subItem);
            },

            addChecklistField(task = '', completed = false, subtasks = []) {
                const container = document.getElementById('checklist-list');
                const index = container.querySelectorAll('.item-wrapper').length;
                const displayNumber = this.getDisplayNumber(index);
                const itemId = `checklist-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

                const wrapper = document.createElement('div');
                wrapper.className = 'item-wrapper';
                wrapper.dataset.displayNumber = displayNumber;
                wrapper.innerHTML = `
                    <div class="item-row" data-item-id="${itemId}">
                        <span class="item-number-badge">C${displayNumber}</span>
                        <input type="checkbox" ${completed ? 'checked' : ''}>
                        <input type="text" class="form-control" placeholder="Checklist item" value="${this.escapeHtml(task)}">
                        <button type="button" class="btn-add-subtask" onclick="synergyBoard.addChecklistSubtask('${itemId}')" title="Add Subtask">
                            <i class="fas fa-plus"></i>
                        </button>
                        <button type="button" class="btn-remove-item" onclick="this.parentElement.parentElement.remove()">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                    <div class="sub-checklist" id="subchecklist-${itemId}">
                        ${subtasks.map(sub => {
                    const subtaskText = sub.task || sub.item || sub.text || '';
                    return `<div class="sub-checklist-item">
                                <input type="checkbox" class="sub-checkbox" ${sub.completed ? 'checked' : ''}>
                                <input type="text" class="form-control" placeholder="Subtask" value="${this.escapeHtml(subtaskText)}">
                                <button type="button" class="btn-remove-subtask" onclick="this.parentElement.remove()">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>`;
                }).join('')}
                    </div>
                `;
                container.appendChild(wrapper);
            },

            addChecklistSubtask(itemId) {
                const subChecklistDiv = document.getElementById(`subchecklist-${itemId}`);
                if (!subChecklistDiv) {
                    console.error('❌ Subchecklist container not found:', itemId);
                    return;
                }

                const itemWrapper = subChecklistDiv.closest('.item-wrapper');
                const parentNumber = itemWrapper ? itemWrapper.dataset.displayNumber : '';
                const subIndex = subChecklistDiv.querySelectorAll('.sub-checklist-item').length;
                const displayNumber = this.getDisplayNumber(subIndex, parentNumber);

                const subItem = document.createElement('div');
                subItem.className = 'sub-checklist-item';
                subItem.innerHTML = `
                    <span class="sub-number">C${displayNumber}</span>
                    <input type="checkbox" class="sub-checkbox">
                    <input type="text" class="form-control" placeholder="Subtask description">
                    <button type="button" class="btn-remove-subtask" onclick="this.parentElement.remove()">
                        <i class="fas fa-times"></i>
                    </button>
                `;

                subChecklistDiv.appendChild(subItem);
                console.log('➕ Added subtask to checklist item:', itemId);
            },

            async saveCardEdit() {
                console.log(' Saving card edits...');

                const sessionId = document.getElementById('edit-session-id').value;
                const isNewSession = !sessionId || sessionId === 'null' || sessionId === '';

                if (!isNewSession) {
                    const session = this.sessions.find(s => s.session_id === sessionId);
                    if (!session) {
                        console.error('❌ Session not found:', sessionId);
                        return;
                    }
                }

                // Collect form data
                const dueDate = document.getElementById('edit-due-date').value;
                const dueTime = document.getElementById('edit-due-time').value;
                let dueDateTimestamp = null;
                if (dueDate) {
                    if (dueTime) {
                        dueDateTimestamp = new Date(`${dueDate}T${dueTime}`).toISOString();
                    } else {
                        dueDateTimestamp = new Date(`${dueDate}T00:00`).toISOString();
                    }
                }

                const updates = {
                    title: document.getElementById('edit-title').value,
                    description: document.getElementById('edit-description').value,
                    project_name: document.getElementById('edit-project').value,
                    priority: document.getElementById('edit-priority').value,
                    status: document.getElementById('edit-status').value,
                    kanban_column: document.getElementById('edit-column').value,
                    tags: document.getElementById('edit-tags').value.split(',').map(t => t.trim()).filter(t => t),
                    notes: document.getElementById('edit-notes').value,
                    assignees: document.getElementById('edit-assignees').value.split(',').map(a => a.trim()).filter(a => a),
                    thread_ids: document.getElementById('edit-thread-ids').value.split(',').map(t => t.trim()).filter(t => t),
                    assigned_agents: document.getElementById('edit-assigned-agents').value.split(',').map(a => a.trim()).filter(a => a),
                    due_date: dueDateTimestamp
                };

                // Collect documents
                const docRows = document.querySelectorAll('#documents-list .item-row');
                updates.documents = Array.from(docRows).map(row => ({
                    title: row.children[0].value,
                    url: row.children[1].value,
                    type: row.children[2].value,
                    created_at: new Date().toISOString()
                })).filter(d => d.title && d.url);

                // Collect links
                const linkRows = document.querySelectorAll('#links-list .item-row');
                updates.links = Array.from(linkRows).map(row => ({
                    title: row.children[0].value,
                    url: row.children[1].value,
                    type: row.children[2].value
                })).filter(l => l.title && l.url);

                // Collect next steps with sub-checklists
                const stepWrappers = document.querySelectorAll('#next-steps-list .step-wrapper');
                updates.next_steps = Array.from(stepWrappers).map(wrapper => {
                    const mainRow = wrapper.querySelector('.step-main');
                    const subChecklistDiv = wrapper.querySelector('.sub-checklist');
                    const subItems = Array.from(subChecklistDiv.querySelectorAll('.sub-checklist-item')).map(subItem => ({
                        item: subItem.querySelector('input[type="text"]').value,
                        completed: subItem.querySelector('.sub-checkbox').checked
                    })).filter(item => item.item);

                    return {
                        completed: mainRow.querySelector('.step-checkbox').checked,
                        description: mainRow.querySelector('.step-description').value,
                        due_date: mainRow.querySelector('input[type="date"]').value ? new Date(mainRow.querySelector('input[type="date"]').value).toISOString() : null,
                        sub_checklist: subItems
                    };
                }).filter(s => s.description);

                // Collect checklist with subtasks
                const checklistWrappers = document.querySelectorAll('#checklist-list .item-wrapper');
                updates.checklist = Array.from(checklistWrappers).map(wrapper => {
                    const mainRow = wrapper.querySelector('.item-row');
                    const subChecklistDiv = wrapper.querySelector('.sub-checklist');

                    // Collect subtasks if present
                    const subtasks = Array.from(subChecklistDiv.querySelectorAll('.sub-checklist-item')).map(subItem => ({
                        task: subItem.querySelector('input[type="text"]').value,
                        completed: subItem.querySelector('.sub-checkbox').checked
                    })).filter(item => item.task);

                    return {
                        completed: mainRow.children[0].checked,
                        task: mainRow.children[1].value,  // Changed from 'item' to 'task'
                        subtasks: subtasks
                    };
                }).filter(c => c.task);

                // Check Google sync options
                const syncTasks = document.getElementById('sync-google-tasks').checked;
                const syncCalendar = document.getElementById('sync-google-calendar').checked;

                // Save via API
                try {
                    let newSessionId = sessionId;

                    if (isNewSession) {
                        // Create new session
                        console.log(' Creating new session...');
                        const createResp = await fetch(`${this.apiBaseUrl}/api/synergy/create`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(updates)
                        });

                        if (!createResp.ok) {
                            throw new Error(`Failed to create session: ${createResp.status}`);
                        }

                        const createData = await createResp.json();
                        newSessionId = createData.session_id;
                        console.log('✅ Created new session:', newSessionId);

                        // Auto-link to pending thread if exists
                        if (window._pendingLinkThreadId && typeof ThreadManager !== 'undefined') {
                            console.log(' Auto-linking to thread:', window._pendingLinkThreadId);
                            await ThreadManager.linkToExistingSession(newSessionId);
                            window._pendingLinkThreadId = null;
                        }
                    } else {
                        // Update existing session
                        await this.apiEditCard(sessionId, updates, { syncTasks, syncCalendar });
                    }

                    // Reload sessions to get fresh data
                    await this.loadSessions();
                    this.renderAllCards();
                    this.updateStats();

                    // Close modal
                    this.closeEditModal();

                    // Show success
                    this.showSyncIndicator('success', isNewSession ? 'Session created successfully!' : 'Card updated successfully!', 2000);

                } catch (error) {
                    console.error('❌ Failed to save:', error);
                    this.showSyncIndicator('error', 'Failed to save changes', 3000);
                }
            },

            // ============================================
            // BACKEND API INTEGRATION
            // ============================================

            async apiEditCard(sessionId, updates, options = {}) {
                try {
                    console.log(' Saving card to API:', sessionId);

                    const response = await fetch(`${this.apiBaseUrl}/api/synergy/${sessionId}`, {
                        method: 'PATCH',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            updates,
                            sync: {
                                google_tasks: options.syncTasks || false,
                                google_calendar: options.syncCalendar || false
                            }
                        })
                    });

                    if (!response.ok) {
                        throw new Error(`API error: ${response.status}`);
                    }

                    const updatedSession = await response.json();

                    // Update local session
                    const session = this.sessions.find(s => s.session_id === sessionId);
                    if (session) {
                        Object.assign(session, updatedSession);
                    }

                    // Re-render card
                    const oldCard = document.querySelector(`.kanban-card[data-session-id="${sessionId}"]`);
                    const wasExpanded = oldCard && oldCard.dataset.expanded === 'true';
                    const oldColumn = oldCard ? oldCard.closest('.kanban-cards-container').dataset.column : null;

                    if (oldCard) oldCard.remove();
                    await this.renderCard(session);

                    if (wasExpanded) {
                        this.toggleCardExpand(sessionId);
                    }

                    // Update UI
                    this.updateColumnCounts();
                    this.updateStats();

                    // Broadcast update via WebSocket
                    this.broadcastUpdate('card_edit', { sessionId, updates });

                    console.log('Card saved to API:', sessionId);
                    return updatedSession;

                } catch (error) {
                    console.warn('[WARN] API unavailable, updating locally:', error.message);

                    // Fallback to local update
                    const session = this.sessions.find(s => s.session_id === sessionId);
                    if (session) {
                        Object.assign(session, updates);
                        session.last_active = new Date().toISOString();

                        // Re-render card
                        const oldCard = document.querySelector(`.kanban-card[data-session-id="${sessionId}"]`);
                        const wasExpanded = oldCard && oldCard.dataset.expanded === 'true';

                        if (oldCard) oldCard.remove();
                        await this.renderCard(session);

                        if (wasExpanded) {
                            this.toggleCardExpand(sessionId);
                        }

                        this.updateColumnCounts();
                        this.updateStats();
                    }

                    throw error;
                }
            },

            // ============================================
            // WEBSOCKET REAL-TIME COLLABORATION
            // ============================================

            websocket: null,
            wsReconnectAttempts: 0,
            wsMaxReconnectAttempts: 5,

            initWebSocket() {
                const wsUrl = this.apiBaseUrl.replace('http', 'ws') + '/ws/synergy';
                console.log(' Connecting to WebSocket:', wsUrl);

                try {
                    this.websocket = new WebSocket(wsUrl);

                    this.websocket.onopen = () => {
                        console.log('WebSocket connected');
                        this.wsReconnectAttempts = 0;
                        this.showRealtimeIndicator('connected', 'Connected - Live updates enabled');

                        // Subscribe to board updates
                        this.websocket.send(JSON.stringify({
                            type: 'subscribe',
                            channel: 'synergy_board'
                        }));
                    };

                    this.websocket.onmessage = (event) => {
                        try {
                            const message = JSON.parse(event.data);
                            this.handleWebSocketMessage(message);
                        } catch (error) {
                            console.error(' WebSocket message error:', error);
                        }
                    };

                    this.websocket.onerror = (error) => {
                        console.error(' WebSocket error:', error);
                    };

                    this.websocket.onclose = () => {
                        console.log(' WebSocket disconnected');
                        this.showRealtimeIndicator('disconnected', 'Disconnected - Attempting to reconnect...');
                        this.attemptReconnect();
                    };

                } catch (error) {
                    console.warn('[WARN] WebSocket not available:', error.message);
                    this.showRealtimeIndicator('disconnected', 'Real-time updates unavailable');
                }
            },

            attemptReconnect() {
                if (this.wsReconnectAttempts >= this.wsMaxReconnectAttempts) {
                    console.log(' Max reconnect attempts reached');
                    return;
                }

                this.wsReconnectAttempts++;
                const delay = Math.min(1000 * Math.pow(2, this.wsReconnectAttempts), 30000);
                console.log(` Reconnecting in ${delay}ms (attempt ${this.wsReconnectAttempts}/${this.wsMaxReconnectAttempts})...`);

                setTimeout(() => {
                    this.initWebSocket();
                }, delay);
            },

            handleWebSocketMessage(message) {
                console.log(' WebSocket message:', message.type);

                switch (message.type) {
                    case 'card_created':
                        this.handleRemoteCardCreated(message.data);
                        break;
                    case 'card_edited':
                        this.handleRemoteCardEdited(message.data);
                        break;
                    case 'card_moved':
                        this.handleRemoteCardMoved(message.data);
                        break;
                    case 'card_deleted':
                        this.handleRemoteCardDeleted(message.data);
                        break;
                    case 'column_change':
                        this.handleRemoteColumnChange(message.data);
                        break;
                    default:
                        console.log('Unknown message type:', message.type);
                }
            },

            async handleRemoteCardCreated(data) {
                console.log('[NEW] Remote card created:', data.sessionId);

                // Check if we already have this card
                if (this.sessions.find(s => s.session_id === data.sessionId)) {
                    return; // Already have it
                }

                // Add to sessions
                this.sessions.push(data.session);

                // Render card
                await this.renderCard(data.session);
                this.updateColumnCounts();
                this.updateStats();

                // Show notification
                this.showSyncIndicator('success', `New card created by ${data.user || 'another user'}`, 3000);
            },

            async handleRemoteCardEdited(data) {
                console.log('✏️ Remote card edited:', data.sessionId);

                const session = this.sessions.find(s => s.session_id === data.sessionId);
                if (!session) return;

                // Update session
                Object.assign(session, data.updates);

                // Re-render card
                const oldCard = document.querySelector(`.kanban-card[data-session-id="${data.sessionId}"]`);
                const wasExpanded = oldCard && oldCard.dataset.expanded === 'true';

                if (oldCard) oldCard.remove();
                await this.renderCard(session);

                if (wasExpanded) {
                    this.toggleCardExpand(data.sessionId);
                }

                this.updateColumnCounts();
                this.updateStats();

                // Show notification
                this.showSyncIndicator('success', `Card updated by ${data.user || 'another user'}`, 2000);
            },

            async handleRemoteCardMoved(data) {
                console.log(' Remote card moved:', data.sessionId);

                const session = this.sessions.find(s => s.session_id === data.sessionId);
                if (!session) return;

                session.kanban_column = data.newColumn;

                // Remove and re-render in new column
                const oldCard = document.querySelector(`.kanban-card[data-session-id="${data.sessionId}"]`);
                if (oldCard) oldCard.remove();

                await this.renderCard(session);
                this.updateColumnCounts();

                // Show notification
                this.showSyncIndicator('success', `Card moved by ${data.user || 'another user'}`, 2000);
            },

            handleRemoteCardDeleted(data) {
                console.log('�� Remote card deleted:', data.sessionId);

                // Remove from sessions
                this.sessions = this.sessions.filter(s => s.session_id !== data.sessionId);

                // Remove card element
                const card = document.querySelector(`.kanban-card[data-session-id="${data.sessionId}"]`);
                if (card) card.remove();

                this.updateColumnCounts();
                this.updateStats();

                // Show notification
                this.showSyncIndicator('success', `Card deleted by ${data.user || 'another user'}`, 2000);
            },

            handleRemoteColumnChange(data) {
                console.log('[CHART] Remote column change:', data);
                // Could implement column-level changes here
            },

            broadcastUpdate(type, data) {
                if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
                    return; // WebSocket not connected
                }

                this.websocket.send(JSON.stringify({
                    type: 'broadcast',
                    messageType: type,
                    data: data,
                    timestamp: new Date().toISOString()
                }));
            },

            showRealtimeIndicator(status, message) {
                let indicator = document.getElementById('realtime-indicator');

                if (!indicator) {
                    indicator = document.createElement('div');
                    indicator.id = 'realtime-indicator';
                    indicator.className = 'realtime-indicator';
                    indicator.innerHTML = `
                                                                                                                                                                                    <div class="realtime-pulse"></div>
                                                                                                                                                                                    <span class="realtime-message"></span>
                                                                                                                                                                                    `;
                    document.body.appendChild(indicator);
                }

                const messageEl = indicator.querySelector('.realtime-message');
                if (messageEl) messageEl.textContent = message;

                indicator.className = `realtime-indicator ${status} show`;

                // Auto-hide after 5 seconds
                setTimeout(() => {
                    indicator.classList.remove('show');
                }, 5000);
            },

            // ============================================
            // GOOGLE SERVICES INTEGRATION
            // ============================================

            googleAuth: null,
            googleTasksEnabled: false,
            googleCalendarEnabled: false,

            async initGoogleServices() {
                try {
                    console.log(' Initializing Google Services...');

                    // Check if Google API is loaded
                    if (typeof gapi === 'undefined') {
                        console.warn('[WARN] Google API not loaded');
                        return;
                    }

                    // Initialize Google API client
                    await gapi.load('client:auth2', async () => {
                        await gapi.client.init({
                            // OAuth credentials from .env.master
                            clientId: '382050681725-9cc4ppne6k1d1arvadrj4f3ainjpcrun.apps.googleusercontent.com',
                            discoveryDocs: [
                                'https://www.googleapis.com/discovery/v1/apis/tasks/v1/rest',
                                'https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest'
                            ],
                            scope: 'https://www.googleapis.com/auth/tasks https://www.googleapis.com/auth/calendar'
                        });

                        this.googleAuth = gapi.auth2.getAuthInstance();
                        console.log('Google Services initialized');
                    });

                } catch (error) {
                    console.warn('[WARN] Google Services unavailable:', error.message);
                }
            },

            async syncToGoogleTasks(session) {
                if (!this.googleAuth || !this.googleAuth.isSignedIn.get()) {
                    console.log(' Signing in to Google...');
                    await this.googleAuth.signIn();
                }

                try {
                    console.log(' Syncing to Google Tasks:', session.title);

                    const task = {
                        title: session.title,
                        notes: session.description || '',
                        due: session.due_date,
                        status: session.status === 'completed' ? 'completed' : 'needsAction'
                    };

                    const response = await gapi.client.tasks.tasks.insert({
                        tasklist: '@default',
                        resource: task
                    });

                    console.log('Synced to Google Tasks:', response.result.id);

                    // Store Google Task ID in session
                    session.google_task_id = response.result.id;

                    return response.result;

                } catch (error) {
                    console.error(' Failed to sync to Google Tasks:', error);
                    throw error;
                }
            },

            async syncToGoogleCalendar(session) {
                if (!this.googleAuth || !this.googleAuth.isSignedIn.get()) {
                    console.log(' Signing in to Google...');
                    await this.googleAuth.signIn();
                }

                try {
                    console.log(' Syncing to Google Calendar:', session.title);

                    const event = {
                        summary: session.title,
                        description: session.description || '',
                        start: {
                            dateTime: session.due_date || new Date().toISOString(),
                            timeZone: 'UTC'
                        },
                        end: {
                            dateTime: session.due_date || new Date(Date.now() + 3600000).toISOString(),
                            timeZone: 'UTC'
                        }
                    };

                    const response = await gapi.client.calendar.events.insert({
                        calendarId: 'primary',
                        resource: event
                    });

                    console.log('Synced to Google Calendar:', response.result.id);

                    // Store Google Calendar event ID in session
                    session.google_calendar_event_id = response.result.id;

                    return response.result;

                } catch (error) {
                    console.error(' Failed to sync to Google Calendar:', error);
                    throw error;
                }
            },

            // ============================================================================
            // INTERNAL DOCUMENTS UI
            // ============================================================================

            // ==================== INTERNAL DOCS METHODS MOVED ====================
            // These methods have been moved to UI/modules/internal_docs/internal-docs-additional.js
            // References now point to synergyBoard.openInternalDocViewer, etc.
            // Moved on: November 20, 2025

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
    </script>

    <!-- Add/Edit Memory Modal -->
    <div id="memoryModal" class="modal-overlay" style="display: none;">
        <div class="modal-content" style="max-width: 600px;">
            <div class="modal-header">
                <h3 id="memoryModalTitle" style="margin: 0; font-size: 18px; color: var(--text-primary);">Add New Memory
                </h3>
                <button class="modal-close-btn" onclick="closeMemoryModal()"
                    style="background: transparent; border: none; font-size: 24px; color: var(--text-secondary); cursor: pointer;">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body" style="padding: 24px;">
                <input type="hidden" id="modalEditMemoryId" value="">

                <div class="form-group" style="margin-bottom: 20px;">
                    <label for="modalMemoryContent"
                        style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">Memory
                        Content</label>
                    <textarea id="modalMemoryContent" class="form-control" rows="4"
                        style="width: 100%; padding: 12px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 6px; color: var(--text-primary); font-size: 14px; resize: vertical;"
                        placeholder="Enter what you want the AI to remember..." required></textarea>
                </div>

                <div class="form-group" style="margin-bottom: 20px;">
                    <label for="modalMemoryCategory"
                        style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">Category</label>
                    <select id="modalMemoryCategory" class="form-control"
                        style="width: 100%; padding: 12px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 6px; color: var(--text-primary); font-size: 14px;">
                        <option value="general">General</option>
                        <option value="preferences">Preferences</option>
                        <option value="personal">Personal</option>
                        <option value="work">Work</option>
                        <option value="health">Health</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="modalMemoryTags"
                        style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">Tags
                        (comma-separated)</label>
                    <input type="text" id="modalMemoryTags" class="form-control"
                        style="width: 100%; padding: 12px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 6px; color: var(--text-primary); font-size: 14px;"
                        placeholder="e.g., timezone, location, preferences">
                    <small style="color: var(--text-muted); font-size: 12px; display: block; margin-top: 4px;">
                        Separate multiple tags with commas
                    </small>
                </div>
            </div>
            <div class="modal-footer"
                style="padding: 16px 24px; border-top: 1px solid var(--border-default); display: flex; justify-content: flex-end; gap: 12px;">
                <button class="btn btn-secondary" onclick="closeMemoryModal()">Cancel</button>
                <button class="btn btn-primary" onclick="saveMemory()">
                    <i class="fas fa-save"></i> Save Memory
                </button>
            </div>
        </div>
    </div>

    <!-- ==================== PROMPT LIBRARY MODAL ==================== -->
    <!-- Modal is dynamically created by modules/prompt-library.js -->

    <!-- ==================== MODULE SYSTEM SCRIPTS ==================== -->
    <script src="js/module-manager.js"></script>
    <script src="js/module-base.js"></script>
    <script src="js/module-loader.js"></script>

    <!-- ==================== MODULE SYSTEM INITIALIZATION ==================== -->
    <script>
        // Module system auto-initializes via module-loader.js
        // Diagnostic logs only
        console.log('='.repeat(60));
        console.log(' MODULE SYSTEM DEBUG');
        console.log('='.repeat(60));
        console.log('✅ ModuleManager:', typeof window.ModuleManager);
        console.log('✅ BaseModule:', typeof window.BaseModule);
        console.log('✅ ModuleLoader:', typeof window.ModuleLoader);
        console.log('✅ initializeModuleSystem:', typeof window.initializeModuleSystem);
        console.log('✅ DOM State:', document.readyState);
        console.log('✅ Protocol:', window.location.protocol);
        console.log('✅ URL:', window.location.href);

        // Check for required DOM elements
        const sidebar = document.querySelector('.sidebar');
        const mainContent = document.querySelector('.main-content');
        console.log('✅ Sidebar found:', !!sidebar);
        console.log('✅ Main content found:', !!mainContent);
        console.log('='.repeat(60));
        console.log(' Waiting for module-loader.js to auto-initialize...');
    </script>

    <!-- ==================== FEEDBACK AREA COMPONENT ==================== -->
    <script src="components/feedback-area-new.js"></script>

    <!-- ==================== PROMPT LIBRARY MODULE ==================== -->
    <!-- Modular prompt library JavaScript with API integration -->
    <script src="modules/prompt-library.js"></script>

    <!-- ==================== AUTOMATION WORKFLOWS MODULE ==================== -->
    <!-- Visual automation canvas JavaScript with drag-and-drop functionality -->
    <script src="external/modules/automation-workflows/automation-workflows.js"></script>

    <!-- ==================== INTERNAL DOCS MANAGER MODULE ==================== -->
    <!-- Complete document management system with TipTap and Handsontable -->
    <script src="modules/internal_docs/manager.js"></script>

    <!-- ==================== INTERNAL DOCUMENT POPUP CONTAINER ==================== -->
    <div id="internalDocPopupContainer">
        <!-- Popup windows will be dynamically created here -->
    </div>

    <!-- ==================== DIAGNOSTIC SCRIPT ==================== -->
    <script>
        // Diagnostic function to test right sidebar buttons
        window.testRightSidebarButtons = function () {
            console.log('%cRIGHT SIDEBAR BUTTONS DIAGNOSTIC TEST', 'background: #257bdd; color: white; padding: 4px 8px; font-weight: bold; font-size: 14px;');
            console.log('%c==================================================', 'color: #257bdd; font-weight: bold;');

            const tests = {
                newChatBtn: document.getElementById('new-chat-btn'),
                threadsBtn: document.getElementById('threads-btn'),
                quickActionsBtn: document.getElementById('quick-actions-btn'),
                themeToggleBtn: document.getElementById('theme-toggle-btn-sidebar'),
                threadMenuOverlay: document.getElementById('thread-menu'),
                quickActionsPanel: document.getElementById('quick-actions-panel'),
                newChatModal: document.getElementById('newChatModalOverlay')
            };

            // Test 1: Button Elements
            console.log('%c\nTEST 1: Button Elements', 'color: #22c55e; font-weight: bold;');
            Object.entries(tests).forEach(([name, element]) => {
                const exists = element !== null;
                const visible = exists && element.offsetParent !== null;
                console.log(`  ${exists ? '?' : '?'} ${name}:`, {
                    exists,
                    visible: visible ? 'YES' : 'NO',
                    element
                });
            });

            // Test 2: Event Listeners
            console.log('%c\nTEST 2: Event Listeners Check', 'color: #22c55e; font-weight: bold;');
            const listeners = {
                'new-chat-btn': tests.newChatBtn ? getEventListeners(tests.newChatBtn) : null,
                'quick-actions-btn': tests.quickActionsBtn ? getEventListeners(tests.quickActionsBtn) : null,
                'theme-toggle-btn-sidebar': tests.themeToggleBtn ? getEventListeners(tests.themeToggleBtn) : null
            };

            Object.entries(listeners).forEach(([id, listenerObj]) => {
                if (listenerObj) {
                    const clickListeners = listenerObj.click || [];
                    console.log(`  ${clickListeners.length > 0 ? '?' : '?'} ${id}: ${clickListeners.length} click listener(s)`, listenerObj);
                } else {
                    console.log(`  ? ${id}: Element not found`);
                }
            });

            // Test 3: ThreadManager
            console.log('%c\nTEST 3: ThreadManager Functions', 'color: #22c55e; font-weight: bold;');
            if (typeof ThreadManager !== 'undefined') {
                console.log('  ? ThreadManager exists');
                console.log('    - showNewChatModal:', typeof ThreadManager.showNewChatModal === 'function' ? '? FUNCTION' : '? NOT A FUNCTION');
                console.log('    - toggleThreadMenu:', typeof ThreadManager.toggleThreadMenu === 'function' ? '? FUNCTION' : '? NOT A FUNCTION');
            } else {
                console.log('  ? ThreadManager not defined');
            }

            // Test 4: Theme Toggle
            console.log('%c\nTEST 4: Theme Toggle Function', 'color: #22c55e; font-weight: bold;');
            if (typeof initThemeToggle !== 'undefined') {
                console.log('  ? initThemeToggle function exists');
            } else {
                console.log('  ? initThemeToggle function not defined');
            }

            // Test 5: Click Tests
            console.log('%c\nTEST 5: Simulated Click Tests', 'color: #f59e0b; font-weight: bold;');
            console.log('  Run these commands manually to test:');
            console.log('    testNewChatButton() - Test new chat modal');
            console.log('    testQuickActionsButton() - Test quick actions panel');
            console.log('    testThemeToggleButton() - Test theme toggle');
            console.log('    testThreadsButton() - Test thread menu');

            console.log('%c\n==================================================', 'color: #257bdd; font-weight: bold;');
            console.log('%c? Diagnostic test complete! Check results above.', 'background: #22c55e; color: white; padding: 4px 8px; font-weight: bold;');

            return tests;
        };

        // Individual button tests
        window.testNewChatButton = function () {
            console.log('%cTesting New Chat Button...', 'background: #257bdd; color: white; padding: 2px 6px;');
            const btn = document.getElementById('new-chat-btn');
            if (btn) {
                btn.click();
                setTimeout(() => {
                    const modal = document.getElementById('newChatModalOverlay');
                    console.log(modal ? '? Modal created' : '? Modal NOT created', modal);
                }, 100);
            } else {
                console.log('? Button not found');
            }
        };

        window.testQuickActionsButton = function () {
            console.log('%cTesting Quick Actions Button...', 'background: #257bdd; color: white; padding: 2px 6px;');
            const btn = document.getElementById('quick-actions-btn');
            if (btn) {
                btn.click();
                setTimeout(() => {
                    const panel = document.getElementById('quick-actions-panel');
                    console.log(panel ? '? Panel created' : '? Panel NOT created', panel);
                    if (panel) {
                        console.log('Panel active:', panel.classList.contains('active'));
                        console.log('Panel position:', window.getComputedStyle(panel).right);
                    }
                }, 100);
            } else {
                console.log('? Button not found');
            }
        };

        window.testThemeToggleButton = function () {
            console.log('%cTesting Theme Toggle Button...', 'background: #257bdd; color: white; padding: 2px 6px;');
            const btn = document.getElementById('theme-toggle-btn-sidebar');
            const currentTheme = document.documentElement.getAttribute('data-theme');
            console.log('Current theme:', currentTheme);
            if (btn) {
                btn.click();
                setTimeout(() => {
                    const newTheme = document.documentElement.getAttribute('data-theme');
                    console.log(currentTheme !== newTheme ? '? Theme changed' : '? Theme NOT changed');
                    console.log('New theme:', newTheme);
                }, 100);
            } else {
                console.log('? Button not found');
            }
        };

        window.testThreadsButton = function () {
            console.log('%cTesting Threads Button...', 'background: #257bdd; color: white; padding: 2px 6px;');
            const btn = document.getElementById('threads-btn');
            if (btn) {
                btn.click();
                setTimeout(() => {
                    const menu = document.getElementById('thread-menu');
                    console.log(menu ? '? Menu exists' : '? Menu NOT found', menu);
                    if (menu) {
                        console.log('Menu active:', menu.classList.contains('active'));
                        console.log('Menu position:', window.getComputedStyle(menu).right);
                    }
                }, 100);
            } else {
                console.log('? Button not found');
            }
        };

        // Auto-run diagnostic on page load (after a short delay)
        setTimeout(() => {
            console.log('%c\nTIP: Run testRightSidebarButtons() in console for full diagnostic', 'background: #f59e0b; color: white; padding: 4px 8px; font-style: italic;');
        }, 2000);