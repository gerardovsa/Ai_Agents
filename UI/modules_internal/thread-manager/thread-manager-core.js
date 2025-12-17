/**
 * FILE: UI/modules/thread-manager/thread-manager-core.js
 * PURPOSE: Main ThreadManager object, state management, and initialization
 * 
 * DEPENDENCIES:
 * - None (core module, loaded first)
 * 
 * EXPORTS:
 * - window.ThreadManager (global object)
 * 
 * USED BY:
 * - UI/modules/thread-manager/thread-manager-*.js (all other thread manager modules)
 * - UI/business-ai-platform-v2.html (main application)
 * 
 * RELATED FILES:
 * - UI/modules/thread-manager/thread-manager-welcome.js (welcome system)
 * - UI/modules/thread-manager/thread-manager-assignment.js (CASCADE pattern)
 * - UI/modules/thread-manager/thread-manager-crud.js (CRUD operations)
 * - UI/modules/thread-manager/thread-manager-ui.js (UI rendering)
 * - UI/modules/thread-manager/thread-manager-messages.js (message handling)
 * - UI/modules/thread-manager/thread-manager-interactions.js (interactions)
 * - UI/modules/thread-manager/thread-manager-filters.js (filtering)
 * 
 * NOTES:
 * - This is the core module that must load first
 * - Contains main state and initialization logic
 * - Other modules extend this core object
 * 
 * LAST MODIFIED: 2025-11-20 - Initial file creation
 */

// Core ThreadManager object will be defined here
// Awaiting code paste from user



// ==================== THREAD MANAGER - CORE MODULE ====================
/**
 * ThreadManager - Centralized Thread Management System
 * Version: 3.0 - Modular Architecture (Nov 2025)
 * 
 * Main entry point that initializes all modules and exposes unified API
 */

// ==================== DEBOUNCE UTILITY ====================
/**
 * ✅ FIX #3: Universal debounce utility for performance optimization
 * Creates a debounced version of a function that delays execution
 * @param {Function} func - Function to debounce
 * @param {number} delay - Delay in milliseconds
 * @param {Object} options - Configuration options
 * @returns {Function} Debounced function
 */
function createDebounce(func, delay, options = {}) {
    let timer = null;
    const immediate = options.immediate || false;

    return function debounced(...args) {
        const context = this;
        const shouldCallImmediately = immediate && !timer;

        clearTimeout(timer);

        if (shouldCallImmediately) {
            func.apply(context, args);
        }

        timer = setTimeout(() => {
            timer = null;
            if (!immediate) {
                func.apply(context, args);
            }
        }, delay);
    };
}

const ThreadManager = {
    // ==================== STATE ====================
    currentThreadId: null,
    threads: [],
    threadsLoaded: false,
    autoSaveInterval: null,
    _initialized: false,  // ✅ NEW: Flag to prevent duplicate initialization
    _initializationPromise: null,  // ✅ NEW: Track ongoing initialization

    /**
     * Sanitize thread ID by removing whitespace and newlines
     * @param {string} threadId - Thread ID to sanitize
     * @returns {string} Cleaned thread ID
     */
    sanitizeThreadId(threadId) {
        if (!threadId) return '';
        return String(threadId).trim().replace(/[\r\n\t]/g, '');
    },

    /**
     * Get thread assigned to a specific agent
     * @param {string} agentName - Agent name (e.g., 'Charlie-3' or just 'agent-3')
     * @returns {Object|null} Thread object or null if not found
     */
    getThreadByAgent(agentName) {
        // Normalize agent name to location format (agent-3)
        let location = agentName;
        if (!agentName.startsWith('agent-')) {
            // Convert 'Charlie-3' to 'agent-3'
            const match = agentName.match(/(\d+)$/);
            if (match) {
                location = `agent-${match[1]}`;
            }
        }

        // Find thread assigned to this agent location
        const thread = this.threads.find(t => t.location === location && !t.archived);
        console.log(`[getThreadByAgent] Looking for thread at ${location}, found:`, thread?.title || 'none');
        return thread || null;
    },
    currentFilter: 'active',
    searchQuery: '',
    locationFilter: 'all',
    activeTagFilter: null,
    dateRangeFilter: { range: 'all', startDate: null },
    sortOrder: 'updated', // 'updated' (recent activity) or 'created' (chronological)
    realtimeChannel: null,
    realtimeEnabled: false,
    lastRealtimeUpdate: 0,
    pendingAssignment: false,
    cascadeInProgress: false,  // Prevent UI refreshes during CASCADE
    apiBaseUrl: window.API_BASE_URL || 'http://localhost:5001',

    // ==================== INITIALIZATION ====================
    // Helper method
    getCurrentThread() {
        return this.threads.find(t => t.id === this.currentThreadId);
    },

    // Get active AI Prime thread ID for workflow linking
    getActiveThreadId() {
        // Check AppState.currentThreadId (AI Prime active thread)
        if (typeof AppState !== 'undefined' && AppState.currentThreadId) {
            return AppState.currentThreadId;
        }

        // Fallback: Find thread at location='prime-loaded'
        const primeThread = this.threads.find(t => t.location === 'prime-loaded');
        if (primeThread) {
            return primeThread.id;
        }

        return null;
    },

    // REPLACE the existing init() with this enhanced version:
    async init() {
        // ✅ GUARD: Prevent duplicate initialization
        if (this._initialized) {
            console.log('⏭️ [ThreadManager] Already initialized, skipping duplicate init');
            return;
        }

        // ✅ GUARD: If initialization is in progress, wait for it
        if (this._initializationPromise) {
            console.log('⏳ [ThreadManager] Initialization in progress, waiting...');
            return await this._initializationPromise;
        }

        console.log('🚀 [ThreadManager] Initializing...');

        // Store initialization promise to prevent concurrent calls
        this._initializationPromise = (async () => {
            try {
                await this.loadModules();
                await this.ensureCorrectUserData();

                // ✅ FIX: Check if MultiAgent already loaded threads (prevents duplicate load + assignment query)
                const multiAgentAlreadyLoaded = typeof MultiAgent !== 'undefined' &&
                    MultiAgent.loadedThreads && Object.keys(MultiAgent.loadedThreads).length > 0;

                // ✅ SMART: Only load threads if not already loaded by initMultiAgent
                if (!this.threadsLoaded || this.threads.length === 0) {
                    if (multiAgentAlreadyLoaded) {
                        console.log('⏭️ [ThreadManager] Skipping loadThreadsFromBackend (MultiAgent already loaded ' +
                            Object.keys(MultiAgent.loadedThreads).length + ' threads)');
                        this.threads = Object.values(MultiAgent.loadedThreads);
                        this.threadsLoaded = true;
                    } else {
                        console.log('📥 [ThreadManager] Loading threads (not yet loaded)...');
                        await this.loadThreadsFromBackend();
                    }
                } else {
                    console.log('✅ [ThreadManager] Threads already loaded (count: ' + this.threads.length + '), skipping reload');
                }

                // ✅ SMART: Only restore assignments if not already done by initMultiAgent
                if (typeof MultiAgent !== 'undefined' && MultiAgent.loadedThreads && Object.keys(MultiAgent.loadedThreads).length > 0) {
                    console.log('✅ [ThreadManager] Threads already assigned by initMultiAgent, skipping restoreThreadAssignments');
                } else if (typeof this.restoreThreadAssignments === 'function') {
                    console.log('📥 [ThreadManager] Restoring thread assignments...');
                    await this.restoreThreadAssignments();
                } else {
                    console.warn('⚠️ [ThreadManager] restoreThreadAssignments not loaded yet (assignment module loading asynchronously)');
                    console.warn('This is expected if modules load asynchronously - assignments will be handled by initMultiAgent');
                }

                // ✅ FIX: Make realtime subscription optional (loads asynchronously)
                if (typeof this.initRealtimeSubscription === 'function') {
                    await this.initRealtimeSubscription();
                } else {
                    console.warn('⚠️ [ThreadManager] initRealtimeSubscription not loaded yet (realtime module loading asynchronously)');
                    console.warn('This is expected if modules load asynchronously - realtime will initialize when module loads');
                }

                this.initWelcomeMessage('prime');
                this.startAutoSave();
                this.renderThreadList();

                // ✅ SMART: Only auto-load prime if not already loaded
                const primeThreadId = this.threads.find(t => t.location === 'prime-loaded')?.id;
                const primeAlreadyLoaded = typeof AppState !== 'undefined' && AppState.currentThreadId === primeThreadId;

                if (!primeAlreadyLoaded && primeThreadId) {
                    console.log('📥 [ThreadManager] Auto-loading prime thread...');
                    // Wait for assignment module to load (it extends ThreadManager with assignThread)
                    await this.waitForAssignmentModule();
                    await this.autoLoadPrimeThread();
                } else {
                    console.log('✅ [ThreadManager] Prime thread already loaded, skipping auto-load');
                }

                // ✅ ENHANCED: Initialize tooltips and menu handlers
                this.initTooltips();
                this.initMenuHandlers();

                // ✅ NEW: Initialize thread selectors for agents and Prime
                setTimeout(() => {
                    if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.refreshAllAgentThreadInfos === 'function') {
                        AgentColumn.refreshAllAgentThreadInfos();
                        console.log('✅ [ThreadManager] Thread selectors initialized');
                    }
                }, 500);

                console.log('✅ [ThreadManager] Initialization complete');
                console.log(`📊 [ThreadManager] Loaded ${this.threads.length} threads`);

                // Mark as initialized
                this._initialized = true;

            } catch (error) {
                console.error('❌ [ThreadManager] Initialization failed:', error);
                throw error;
            } finally {
                // Clear the initialization promise
                this._initializationPromise = null;
            }
        })();

        return this._initializationPromise;
    },







    async waitForAssignmentModule() {
        // Wait for assignment module to load (max 5 seconds)
        const maxWait = 5000;
        const startTime = Date.now();

        while (!this._assignmentModuleLoaded && (Date.now() - startTime) < maxWait) {
            await new Promise(resolve => setTimeout(resolve, 50));
        }

        if (!this._assignmentModuleLoaded) {
            throw new Error('Assignment module failed to load within 5 seconds');
        }

        console.log('✅ [ThreadManager] Assignment module ready');
    },

    async loadModules() {
        console.log('📦 [ThreadManager] Loading modules...');

        // Modules are loaded via script tags in HTML
        // Verify they're present

        // Modules with separate global objects
        const separateGlobals = [
            'ThreadManagerWelcome',
            'ThreadManagerUI',
            'ThreadManagerFilters'
        ];

        for (const moduleName of separateGlobals) {
            if (typeof window[moduleName] === 'undefined') {
                throw new Error(`Required module ${moduleName} not loaded`);
            }
        }

        // Modules that extend ThreadManager directly via Object.assign
        // (Assignment, CRUD, Messages, Interactions)
        // These don't have separate globals - they add methods to window.ThreadManager
        // Setup drag/drop zones for agent columns and Prime (called after agents load)
        const directExtensions = [
            'assignThread', 'createThread', 'saveMessagesToBackend', 'toggleThreadMenu',
            'setupPrimeDropZone', 'handleThreadDoubleClick', 'handleDragStart', 'handleDragEnd', 'handleDrop'
        ];
        const missingMethods = directExtensions.filter(method => typeof this[method] !== 'function');

        if (missingMethods.length > 0) {
            console.warn(`⚠️ [ThreadManager] Some module methods not yet loaded: ${missingMethods.join(', ')}`);
            console.warn('This is expected if modules load asynchronously');
        }

        console.log('✅ [ThreadManager] Module verification complete');
    },

    async ensureCorrectUserData() {
        console.log('👤 [ThreadManager] Verifying user data...');

        try {
            // ✅ FIX: Profile already loaded during authentication, no need to fetch again
            if (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) {
                const userId = UserAuth.user.id || UserAuth.user.user_id;
                window.currentUserId = userId;
                console.log('✅ [ThreadManager] Using existing profile data (user_id:', userId, ')');
                return; // Skip duplicate profile fetch
            }

            // ⚠️ FALLBACK ONLY: If profile somehow not loaded, fetch it
            console.warn('⚠️ [ThreadManager] Profile not found in UserAuth, fetching from backend...');
            const response = await fetch(`${this.apiBaseUrl}/api/auth/profile`, {
                headers: { 'Authorization': `Bearer ${UserAuth.token}` }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success && data.profile) {
                    const backendUserId = data.profile.id || data.profile.user_id;
                    UserAuth.user = data.profile;
                    UserAuth.user.id = backendUserId;
                    UserAuth.user.user_id = backendUserId;
                    window.currentUserId = backendUserId;
                    console.log('✅ [ThreadManager] User data loaded from backend');
                }
            }
        } catch (error) {
            console.error('❌ [ThreadManager] Error verifying user data:', error);
        }
    },

    async loadThreadsFromBackend() {
        try {
            const userId = (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || null;

            if (!userId) {
                console.error('❌ [ThreadManager] Cannot load threads: user_id not available');
                return false;
            }

            console.log(`📥 [ThreadManager] Loading threads for user_id: ${userId}`);
            console.log(`🌐 [ThreadManager] API URL: ${this.apiBaseUrl}/api/threads/list?user_id=${userId}`);

            const response = await fetch(`${this.apiBaseUrl}/api/threads/list?user_id=${userId}`);
            console.log(`📡 [ThreadManager] Response status: ${response.status} ${response.statusText}`);

            const data = await response.json();
            console.log(`📦 [ThreadManager] API response keys:`, Object.keys(data));

            const threads = data.threads || (data.data && data.data.threads) || [];
            console.log(`🔢 [ThreadManager] Loaded ${threads.length} threads`);

            if (data.success && threads.length > 0) {
                console.log(`🔄 [ThreadManager] Processing ${threads.length} threads...`);

                this.threads = threads.map((thread, idx) => {
                    const location = thread.location || thread.agent || 'prime';
                    const threadTitle = thread.name || thread.title || 'Untitled Thread';

                    // Sanitize thread ID to remove any whitespace/newlines
                    const threadId = this.sanitizeThreadId(thread.id || thread.thread_slug);

                    // Log location for first 5 threads
                    if (idx < 5) {
                        console.log(`   📍 Thread ${idx + 1}: "${threadTitle}" (${threadId}) → location="${location}"`);
                    }

                    // Parse message content if it's a JSON string (from database)
                    const messages = (thread.messages || []).map(msg => {
                        // If content is a string, try to parse it as JSON
                        if (typeof msg.content === 'string') {
                            try {
                                return {
                                    ...msg,
                                    content: JSON.parse(msg.content)
                                };
                            } catch (e) {
                                console.warn(`⚠️ [ThreadManager] Failed to parse content for message in thread ${threadId}:`, e);
                                return msg; // Return as-is if parsing fails
                            }
                        }
                        return msg; // Already an object/array
                    });

                    return {
                        id: threadId,
                        thread_id: thread.thread_id,
                        title: threadTitle,
                        name: threadTitle,
                        messages: messages,
                        message_count: thread.message_count || 0,
                        created: thread.created || thread.created_at || new Date().toISOString(),
                        updated: thread.updated || thread.updated_at || new Date().toISOString(),
                        archived: thread.archived || false,
                        location: location,
                        agent: location === 'prime' ? null : location,
                        tags: thread.tags || [],
                        synergy_card_id: thread.synergy_card_id || null,
                        workflow_slug: thread.workflow_slug || null,
                        workflow_title: thread.workflow_title || null
                    };
                });

                this.threadsLoaded = true;

                // Calculate location distribution
                const locationCounts = {};
                this.threads.forEach(t => {
                    const loc = t.location || 'prime';
                    locationCounts[loc] = (locationCounts[loc] || 0) + 1;
                });

                console.log('✅ [ThreadManager] Threads loaded:', this.threads.length);
                console.log('📊 [ThreadManager] Location distribution:', locationCounts);

                return true;
            } else {
                console.warn('⚠️ [ThreadManager] No threads from backend');
                this.threads = [];
                return false;
            }
        } catch (error) {
            console.error('❌ [ThreadManager] Failed to load threads:', error);
            this.threads = [];
            return false;
        }
    },

    async autoLoadPrimeThread() {
        if (this.threads.length === 0) {
            console.log('📝 [ThreadManager] No threads - showing welcome');
            this.showStartNewChatButton('ai-chat-messages', 'prime');
            return;
        }

        // ONLY load prime-loaded thread (explicit startup thread)
        // Do NOT fallback to first prime thread - show empty state instead
        const primeLoadedThread = this.threads.find(t => t.location === 'prime-loaded');

        if (primeLoadedThread) {
            // ✅ FIX: Skip if already loaded AND assigned by initMultiAgent (prevents duplicate assignment query)
            const alreadyLoadedByMultiAgent = typeof MultiAgent !== 'undefined' &&
                MultiAgent.loadedThreads && MultiAgent.loadedThreads[primeLoadedThread.id];

            if (alreadyLoadedByMultiAgent) {
                console.log(`⏭️ [ThreadManager] Prime thread "${primeLoadedThread.title}" already loaded by initMultiAgent, skipping auto-load`);
                return;
            }

            // ✅ CHECK: Skip if already loaded (by previous call)
            if (typeof AppState !== 'undefined' && AppState.currentThreadId === primeLoadedThread.id) {
                console.log(`⏭️ [ThreadManager] Prime thread "${primeLoadedThread.title}" already loaded (ID: ${primeLoadedThread.id}), skipping auto-load`);
                return;
            }

            console.log(`🎯 [ThreadManager] Auto-loading PRIME-LOADED thread: ${primeLoadedThread.title}`);
            await this.loadThreadInPrime(primeLoadedThread.id);

            // Update thread info card after loading
            if (typeof this.renderThreadInfoContainer === 'function') {
                this.renderThreadInfoContainer('prime', primeLoadedThread.id, true);
            }
            return;
        }

        // No prime-loaded thread - show empty state with thread selector
        console.log('📝 [ThreadManager] No prime-loaded thread - showing empty state');
        this.showStartNewChatButton('ai-chat-messages', 'prime');
    },


    startAutoSave() {
        // ⚠️ AUTO-SAVE DISABLED (Nov 22, 2025)
        // Backend now auto-saves messages after stream completion
        // Frontend auto-save was causing phantom threads via UPSERT
        console.log('ℹ️ [ThreadManager] Auto-save disabled - backend handles saves');

        /* DEPRECATED: Frontend auto-save removed
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
        }

        // Auto-save every 60 seconds (reduced from 30s to prevent excessive DB writes)
        this.autoSaveInterval = setInterval(() => {
            if (this.currentThreadId) {
                const thread = this.threads.find(t => t.id === this.currentThreadId);
                if (thread && thread.messages && thread.messages.length > 0) {
                    console.log(`💾 [AutoSave] Saving thread ${thread.id} (${thread.messages.length} messages)`);
                    this.saveThreadToBackend(thread);
                }
            }
        }, 60000);

        console.log('✅ [ThreadManager] Auto-save enabled (60s interval)');
        */
    },

    stopAutoSave() {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
            this.autoSaveInterval = null;
            console.log('⏹️ [ThreadManager] Auto-save stopped');
        }
    },

    // ==================== MODULE DELEGATION ====================
    // Delegate to appropriate modules (these will be implemented in separate files)

    // Welcome System (from thread-manager-welcome.js)
    // NOTE: Don't use .call(this) - let methods use their own 'this' context
    getTimeBasedGreeting(...args) { return window.ThreadManagerWelcome.getTimeBasedGreeting(...args); },
    getNextQuickTip(...args) { return window.ThreadManagerWelcome.getNextQuickTip(...args); },
    initWelcomeMessage(...args) { return window.ThreadManagerWelcome.initWelcomeMessage(...args); },
    getCurrentSeason(...args) { return window.ThreadManagerWelcome.getCurrentSeason(...args); },

    // NOTE: Assignment, CRUD, Messages, Interactions modules now use Object.assign(window.ThreadManager, {...})
    // so their methods are directly available - no proxies needed

    // UI (from thread-manager-ui.js) - still uses separate global with proxies
    // NOTE: Don't use .call(this) for UI methods - they need their own context to access internal methods
    // SAFETY: Check if ThreadManagerUI is loaded before calling (fixes race condition)
    renderThreadList(...args) {
        if (!window.ThreadManagerUI) {
            console.warn('⚠️ ThreadManagerUI not loaded yet, skipping renderThreadList');
            return;
        }
        return window.ThreadManagerUI.renderThreadList(...args);
    },
    renderThreadInfoContainer(...args) {
        if (!window.ThreadManagerUI) {
            console.warn('⚠️ ThreadManagerUI not loaded yet, skipping renderThreadInfoContainer');
            return;
        }
        return window.ThreadManagerUI.renderThreadInfoContainer(...args);
    },
    updatePrimeHeader(...args) {
        if (!window.ThreadManagerUI) {
            console.warn('⚠️ ThreadManagerUI not loaded yet, skipping updatePrimeHeader');
            return;
        }
        return window.ThreadManagerUI.updatePrimeHeader(...args);
    },
    refreshAllThreadInfoCards(...args) {
        if (!window.ThreadManagerUI) {
            console.warn('⚠️ ThreadManagerUI not loaded yet, skipping refreshAllThreadInfoCards');
            return;
        }
        return window.ThreadManagerUI.refreshAllThreadInfoCards(...args);
    },
    updateThreadPills(...args) {
        if (!window.ThreadManagerUI) {
            console.warn('⚠️ ThreadManagerUI not loaded yet, skipping updateThreadPills');
            return;
        }
        return window.ThreadManagerUI.updateThreadPills(...args);
    },
    showStartNewChatButton(...args) {
        if (!window.ThreadManagerUI) {
            console.warn('⚠️ ThreadManagerUI not loaded yet, skipping showStartNewChatButton');
            return;
        }
        return window.ThreadManagerUI.showStartNewChatButton(...args);
    },
    renderEmptyThreadInfo(...args) {
        if (!window.ThreadManagerUI) {
            console.warn('⚠️ ThreadManagerUI not loaded yet, skipping renderEmptyThreadInfo');
            return '<div class="empty-thread-info">Loading...</div>';
        }
        return window.ThreadManagerUI.renderEmptyThreadInfo(...args);
    },

    // NOTE: Messages and Interactions modules now use Object.assign(window.ThreadManager, {...})
    // so their methods are directly available - no proxies needed

    // Filters (from thread-manager-filters.js) - still uses separate global
    setFilter(...args) { return window.ThreadManagerFilters.setFilter.call(this, ...args); },
    filterThreads(...args) { return window.ThreadManagerFilters.filterThreads.call(this, ...args); },
    filterByLocation(...args) { return window.ThreadManagerFilters.filterByLocation.call(this, ...args); },
    filterByTag(...args) { return window.ThreadManagerFilters.filterByTag.call(this, ...args); },
    filterByDateRange(...args) { return window.ThreadManagerFilters.filterByDateRange.call(this, ...args); },
    setSortOrder(...args) { return window.ThreadManagerFilters.setSortOrder.call(this, ...args); },
    getDateLabel(...args) { return window.ThreadManagerFilters.getDateLabel.call(this, ...args); },
    populateAgentDropdown(...args) { return window.ThreadManagerFilters.populateAgentDropdown.call(this, ...args); },
    populateTagsDropdown(...args) { return window.ThreadManagerFilters.populateTagsDropdown.call(this, ...args); },
    applyCustomDateRange(...args) { return window.ThreadManagerFilters.applyCustomDateRange.call(this, ...args); },
    toggleCustomDateRange(...args) { return window.ThreadManagerFilters.toggleCustomDateRange.call(this, ...args); },

    // Helper methods
    getCurrentThread() {
        return this.threads.find(t => t.id === this.currentThreadId);
    },

    async refreshThreads() {
        console.log('🔄 [ThreadManager] Refreshing threads...');
        await this.loadThreadsFromBackend();
        await this.renderThreadList();
    },





    // ✅ NEW: Initialize tooltip system
    initTooltips() {
        console.log('🎨 [ThreadManager] Initializing tooltips...');

        // Custom rich tooltip for Synergy badges
        let synergyTooltip = null;
        let tooltipTimeout = null;
        let hideTimeout = null;
        let currentTooltipBadge = null;

        // Helper function to strip markdown formatting
        const stripMarkdown = (text) => {
            if (!text) return '';
            return text
                .replace(/\*\*(.+?)\*\*/g, '$1')  // Bold
                .replace(/\*(.+?)\*/g, '$1')      // Italic
                .replace(/\[(.+?)\]\(.+?\)/g, '$1')  // Links
                .replace(/`(.+?)`/g, '$1')        // Code
                .replace(/^#+\s+/gm, '')          // Headers
                .replace(/^>\s+/gm, '')           // Blockquotes
                .replace(/^[-*+]\s+/gm, '• ')     // Lists
                .trim();
        };

        const showSynergyTooltip = async (badge, event) => {
            clearTimeout(hideTimeout);
            clearTimeout(tooltipTimeout);
            currentTooltipBadge = badge;

            const threadItem = badge.closest('.thread-item');
            if (threadItem) {
                threadItem.classList.add('tooltip-active');
            }

            const container = badge.closest('.thread-item-synergy') || badge.closest('.ai-chat-header-info');
            const sessionId = container?.getAttribute('data-synergy-id') || badge.getAttribute('data-synergy-id') || '';

            // Default/placeholder values (will be overridden by DB fetch when available)
            let title = badge.getAttribute('data-tooltip-title') || sessionId || 'Unknown Session';
            let rawDesc = badge.getAttribute('data-tooltip-desc') || '';
            let desc = stripMarkdown(rawDesc);

            // If we have a sessionId, prefer authoritative data from the backend
            if (sessionId) {
                try {
                    // Include user_id for permission check
                    const userId = window.currentUserId || window.UserAuth?.user?.id || 14;
                    const resp = await fetch(`${ThreadManager.apiBaseUrl}/api/synergy/${encodeURIComponent(sessionId)}?user_id=${userId}`);
                    if (resp && resp.ok) {
                        const json = await resp.json();
                        if (json && json.success && json.session) {
                            const s = json.session;
                            // Use session fields returned by backend
                            title = s.title || title;
                            rawDesc = s.description || rawDesc || '';
                            // If description is stored as JSON string, attempt parse
                            if (typeof rawDesc === 'object') {
                                // If the DB returns an object, stringify primary text
                                rawDesc = rawDesc.description || JSON.stringify(rawDesc);
                            }
                            desc = stripMarkdown(rawDesc || '');
                        }
                    }
                } catch (err) {
                    console.warn('[ThreadManager] Failed to fetch synergy session', sessionId, err);
                    // fall back to badge-provided data
                }
            }
            const users = badge.getAttribute('data-tooltip-users') || '';
            const updated = badge.getAttribute('data-tooltip-updated') || '';
            const priority = badge.querySelector('.synergy-badge-priority')?.textContent?.toLowerCase() || '';

            if (!synergyTooltip) {
                synergyTooltip = document.createElement('div');
                synergyTooltip.className = 'synergy-tooltip';
                document.body.appendChild(synergyTooltip);

                synergyTooltip.addEventListener('mouseenter', () => {
                    clearTimeout(hideTimeout);
                    clearTimeout(tooltipTimeout);
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
                        <a class="synergy-tooltip-link" onclick="event.stopPropagation(); if(window.synergyPopupModal && typeof window.synergyPopupModal.open === 'function') { window.synergyPopupModal.open('${sessionId}'); } else if(typeof synergyBoard !== 'undefined' && typeof synergyBoard.popOutCard === 'function') { if(synergyBoard.sessions.length === 0) { synergyBoard.loadSessions().then(() => synergyBoard.popOutCard('${sessionId}')); } else { synergyBoard.popOutCard('${sessionId}'); } } else { console.error('Synergy popup not available'); alert('Synergy popup not loaded. Please refresh the page.'); } document.querySelector('.synergy-tooltip')?.remove();">
                            <i class="fas fa-window-restore"></i>
                            Open in Popup
                        </a>
                    </div>
                ` : ''}
            `;

            const rect = badge.getBoundingClientRect();
            let left = rect.left + (rect.width / 2) - 160;
            let top = rect.bottom + 8;

            if (left < 10) left = 10;
            if (left + 320 > window.innerWidth) left = window.innerWidth - 330;

            synergyTooltip.style.left = `${left}px`;
            synergyTooltip.style.top = `${top}px`;

            tooltipTimeout = setTimeout(() => {
                synergyTooltip.classList.add('show');
            }, 500);
        };

        const hideSynergyTooltip = () => {
            clearTimeout(tooltipTimeout);
            clearTimeout(hideTimeout);
            hideTimeout = setTimeout(() => {
                if (synergyTooltip) {
                    synergyTooltip.classList.remove('show');
                    if (currentTooltipBadge) {
                        const threadItem = currentTooltipBadge.closest('.thread-item');
                        if (threadItem) {
                            threadItem.classList.remove('tooltip-active');
                        }
                    }
                    currentTooltipBadge = null;
                }
            }, 800);
        };

        // Tooltip event listeners (delegated)
        // NOTE: Skip automatic hover tooltip when the badge is rendered inside
        // a thread info card ('.thread-item-synergy'). Those cards expose a
        // dedicated "Show description" button and a popup button — to avoid
        // duplicate/annoying hover behavior we only show the tooltip on hover
        // for badges outside thread-item-synergy containers. Explicit calls to
        // `showSynergyTooltip(badge, event)` (e.g. from the Info button) still work.
        document.addEventListener('mouseover', (e) => {
            const badge = e.target.closest('.synergy-badge[data-tooltip-title]');
            if (badge) {
                // If badge is inside a thread info card that already has
                // its own description/popup controls, skip the automatic hover
                // tooltip to avoid duplication.
                const inThreadInfo = Boolean(badge.closest('.thread-item-synergy'));
                if (inThreadInfo) return;

                showSynergyTooltip(badge, e);
            }
        });

        document.addEventListener('mouseout', (e) => {
            const badge = e.target.closest('.synergy-badge[data-tooltip-title]');
            if (badge) {
                const movingToTooltip = e.relatedTarget?.closest('.synergy-tooltip');
                const movingToThreadItem = e.relatedTarget?.closest('.thread-item');
                const movingToAgentHeader = e.relatedTarget?.closest('.ai-chat-header-info');

                if (!movingToTooltip && !movingToThreadItem && !movingToAgentHeader) {
                    hideSynergyTooltip();
                }
            }
        });

        document.addEventListener('scroll', hideSynergyTooltip, true);

        // Expose globally
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

            if (!agentTooltip) {
                agentTooltip = document.createElement('div');
                agentTooltip.className = 'agent-badge-tooltip';
                document.body.appendChild(agentTooltip);
            }

            agentTooltip.innerHTML = `
                <div class="agent-tooltip-title">${title}</div>
                ${content ? `<div class="agent-tooltip-content">${content}</div>` : ''}
            `;

            const rect = badge.getBoundingClientRect();
            let left = rect.left + (rect.width / 2) - (agentTooltip.offsetWidth / 2);
            const top = rect.bottom + 8;

            if (left < 10) left = 10;
            if (left + agentTooltip.offsetWidth > window.innerWidth - 10) {
                left = window.innerWidth - agentTooltip.offsetWidth - 10;
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

        // Agent badge listeners
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

        document.addEventListener('scroll', hideAgentBadgeTooltip, true);

        console.log('✅ [ThreadManager] Tooltips initialized');
    },

    // ✅ NEW: Initialize menu handlers
    initMenuHandlers() {
        console.log('🎯 [ThreadManager] Initializing menu handlers...');

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            const menu = document.getElementById('thread-menu');
            const menuBtn = document.getElementById('chat-menu-btn');
            const sidebarBtn = document.getElementById('threads-btn');

            if (menu && !menu.contains(e.target)) {
                const clickedMenuBtn = menuBtn && menuBtn.contains(e.target);
                const clickedSidebarBtn = sidebarBtn && sidebarBtn.contains(e.target);

                if (!clickedMenuBtn && !clickedSidebarBtn) {
                    this.closeThreadMenu();
                }
            }
        });

        // Click handler for Synergy badge in tooltip
        document.addEventListener('click', (e) => {
            const synergyBadge = e.target.closest('.agent-tooltip-synergy-badge');
            if (synergyBadge) {
                const synergyId = synergyBadge.getAttribute('data-synergy-id');
                if (synergyId) {
                    console.log('[Agent Badge] Opening Synergy session:', synergyId);

                    // Use modern popup modal if available, otherwise fallback to popOutCard
                    if (window.synergyPopupModal && typeof window.synergyPopupModal.open === 'function') {
                        window.synergyPopupModal.open(synergyId);
                    } else if (typeof synergyBoard !== 'undefined' && typeof synergyBoard.popOutCard === 'function') {
                        if (synergyBoard.sessions.length === 0) {
                            synergyBoard.loadSessions().then(() => synergyBoard.popOutCard(synergyId));
                        } else {
                            synergyBoard.popOutCard(synergyId);
                        }
                    } else {
                        console.error('[Agent Badge] Synergy popup methods not available');
                        alert('Synergy popup not loaded. Please refresh the page.');
                    }

                    // Close agent tooltip
                    const agentTooltip = document.querySelector('.agent-badge-tooltip');
                    if (agentTooltip) {
                        agentTooltip.classList.remove('show');
                    }
                }
            }
        });

        console.log('✅ [ThreadManager] Menu handlers initialized');
    },

    /**
     * NEW: Filter threads by Team ID
     * Delegates to ThreadManagerFilters module
     */
    filterByTeamId(teamId) {
        if (typeof window.ThreadManagerFilters !== 'undefined' &&
            typeof window.ThreadManagerFilters.filterByTeamId === 'function') {
            window.ThreadManagerFilters.filterByTeamId(teamId);
        } else {
            console.warn('⚠️ [ThreadManager] ThreadManagerFilters not loaded yet');
            // Fallback: show notification
            if (typeof showNotification === 'function') {
                showNotification(`Filtering by Team ID: ${teamId}`, 'info');
            }
        }
    },

    /**
     * NEW: Clear Team ID filter
     * Delegates to ThreadManagerFilters module
     */
    clearTeamIdFilter() {
        if (typeof window.ThreadManagerFilters !== 'undefined' &&
            typeof window.ThreadManagerFilters.clearTeamIdFilter === 'function') {
            window.ThreadManagerFilters.clearTeamIdFilter();
        } else {
            console.warn('⚠️ [ThreadManager] ThreadManagerFilters not loaded yet');
        }
    }
};

// ==================== EXPOSE GLOBALLY ====================
window.ThreadManager = ThreadManager;
console.log('✅ ThreadManager-Core loaded and exposed globally');