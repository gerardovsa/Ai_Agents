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

const ThreadManager = {
    // ==================== STATE ====================
    currentThreadId: null,
    threads: [],
    threadsLoaded: false,
    autoSaveInterval: null,

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

    // REPLACE the existing init() with this enhanced version:
    async init() {
        console.log('🚀 [ThreadManager] Initializing...');

        try {
            await this.loadModules();
            await this.ensureCorrectUserData();
            await this.loadThreadsFromBackend();
            await this.restoreThreadAssignments();
            await this.initRealtimeSubscription();
            this.initWelcomeMessage('prime');
            this.startAutoSave();
            this.renderThreadList();
            await this.autoLoadPrimeThread();

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

        } catch (error) {
            console.error('❌ [ThreadManager] Initialization failed:', error);
            throw error;
        }
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
        const directExtensions = ['assignThread', 'createThread', 'saveMessagesToBackend', 'toggleThreadMenu'];
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
            const response = await fetch(`${this.apiBaseUrl}/api/auth/profile`, {
                headers: { 'Authorization': `Bearer ${UserAuth.token}` }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success && data.profile) {
                    const backendUserId = data.profile.id || data.profile.user_id;
                    const cachedUserId = (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || null;

                    if (backendUserId !== cachedUserId || !cachedUserId) {
                        UserAuth.user = data.profile;
                        UserAuth.user.id = backendUserId;
                        UserAuth.user.user_id = backendUserId;
                        window.currentUserId = backendUserId;
                        // localStorage removed - backend is source of truth
                        console.log('✅ [ThreadManager] User data updated from backend');
                    } else {
                        console.log('✅ [ThreadManager] User ID verified');
                    }
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
            console.log(`📦 [ThreadManager] Raw response:`, data);

            const threads = data.threads || (data.data && data.data.threads) || [];
            console.log(`🔢 [ThreadManager] Extracted ${threads.length} threads from response`);

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
                console.log('📋 [ThreadManager] All thread locations:', this.threads.map(t => `${t.id}: ${t.location}`));

                // REMOVED: refreshAllAgentThreadInfos() call - it interferes with CASCADE pattern
                // CASCADE handles UI updates properly, this was resetting agent UIs prematurely
                // Only call on initial load (in init()), not on every reload

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

        // Find first thread that belongs in Prime
        const primeThread = this.threads.find(t => !t.location || t.location === 'prime');

        if (primeThread) {
            console.log(`📖 [ThreadManager] Auto-loading Prime thread: ${primeThread.title}`);
            await this.loadThreadInPrime(primeThread.id);
        } else {
            console.log('📝 [ThreadManager] No Prime threads - all in agent columns');
            this.showStartNewChatButton('ai-chat-messages', 'prime');
        }
    },

    startAutoSave() {
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
    renderThreadList(...args) { return window.ThreadManagerUI.renderThreadList(...args); },
    renderThreadInfoContainer(...args) { return window.ThreadManagerUI.renderThreadInfoContainer(...args); },
    updatePrimeHeader(...args) { return window.ThreadManagerUI.updatePrimeHeader(...args); },
    refreshAllThreadInfoCards(...args) { return window.ThreadManagerUI.refreshAllThreadInfoCards(...args); },
    updateThreadPills(...args) { return window.ThreadManagerUI.updateThreadPills(...args); },
    showStartNewChatButton(...args) { return window.ThreadManagerUI.showStartNewChatButton(...args); },

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

        const showSynergyTooltip = (badge, event) => {
            clearTimeout(hideTimeout);
            clearTimeout(tooltipTimeout);
            currentTooltipBadge = badge;

            const threadItem = badge.closest('.thread-item');
            if (threadItem) {
                threadItem.classList.add('tooltip-active');
            }

            const container = badge.closest('.thread-item-synergy') || badge.closest('.ai-chat-header-info');
            const sessionId = container?.getAttribute('data-synergy-id') || badge.getAttribute('data-synergy-id') || '';
            const title = badge.getAttribute('data-tooltip-title') || sessionId || 'Unknown Session';
            const rawDesc = badge.getAttribute('data-tooltip-desc') || '';
            const desc = stripMarkdown(rawDesc);
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
                        <a class="synergy-tooltip-link" onclick="event.stopPropagation(); if(typeof synergyBoard !== 'undefined') { if(synergyBoard.sessions.length === 0) { synergyBoard.loadSessions().then(() => synergyBoard.popOutCard('${sessionId}')); } else { synergyBoard.popOutCard('${sessionId}'); } } document.querySelector('.synergy-tooltip')?.remove();">
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
        document.addEventListener('mouseover', (e) => {
            const badge = e.target.closest('.synergy-badge[data-tooltip-title]');
            if (badge) {
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
                if (synergyId && typeof synergyBoard !== 'undefined') {
                    console.log('[Agent Badge] Opening Synergy session:', synergyId);
                    if (synergyBoard.sessions.length === 0) {
                        synergyBoard.loadSessions().then(() => synergyBoard.popOutCard(synergyId));
                    } else {
                        synergyBoard.popOutCard(synergyId);
                    }
                    const agentTooltip = document.querySelector('.agent-badge-tooltip');
                    if (agentTooltip) {
                        agentTooltip.classList.remove('show');
                    }
                }
            }
        });

        console.log('✅ [ThreadManager] Menu handlers initialized');
    }
};

// ==================== EXPOSE GLOBALLY ====================
window.ThreadManager = ThreadManager;
console.log('✅ ThreadManager-Core loaded and exposed globally');