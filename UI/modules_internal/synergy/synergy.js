/**
 * Synergy Sessions Module - Modern Framework Edition
 * Framework: ModuleLoaderV4
 * Pattern: Composition-based (no inheritance)
 * Version: 2.0.0 - Integration module (no sidebar UI)
 * 
 * Purpose:
 * - Thread card integration (drag & drop, badges)
 * - Project management background functionality
 * - Document/sheet linking
 * - Milestone tracking
 * - Real-time event handling
 * 
 * Note: This module does NOT provide a sidebar UI.
 * It runs in the background to support thread card integration.
 * 
 * Dependencies:
 * - SynergyThreadIntegration (synergy-thread-integration.js)
 * - SynergySidebarController (synergy-sidebar-controller.js)
 * - Various synergy utility modules
 */

window.SynergyModule = window.SynergyModule || {
    // ==================== STATE ====================
    state: {
        initialized: false,

        // Integration state
        threadIntegrationActive: false,
        dragDropEnabled: false,
        badgesEnabled: false,
        realtimeEnabled: false,

        // Synergy components (loaded dynamically)
        threadIntegration: null,
        sidebarController: null,

        // Session data
        activeSessions: [],
        linkedThreads: new Map(),

        // Settings
        settings: {
            autoSync: true,
            showBadges: true,
            enableDragDrop: true,
            realtimeUpdates: true
        }
    },

    // ==================== LIFECYCLE: STARTUP ====================

    /**
     * Called when module loads at startup (background mode)
     * Replaces: initialize() from legacy pattern
     * @param {Object} utilities - Injected utilities { dom, api, storage, events, log }
     */
    async onLoad(utilities) {
        // Inject utilities explicitly
        Object.assign(this, utilities);

        this.log.info('Synergy Sessions loading (background mode)...');

        // Load saved settings
        await this.loadSettings();

        // Initialize Synergy components (existing code)
        await this.initializeSynergyComponents();

        // Setup thread card integration
        await this.setupThreadIntegration();

        // Subscribe to events
        this.subscribeToEvents();

        this.state.initialized = true;
        this.log.info('Synergy Sessions loaded successfully (background mode)');
    },

    /**
     * Called when module unloads
     * Replaces: cleanup() from legacy pattern
     * @param {Object} utilities - Injected utilities
     */
    onUnload(utilities) {
        Object.assign(this, utilities);
        this.log.info('Synergy Sessions unloading...');

        // Cleanup thread integration
        if (this.state.threadIntegrationActive) {
            this.cleanupThreadIntegration();
        }

        // Save settings
        this.saveSettings();

        // Framework automatically cleans up tracked event listeners
        this.log.info('Synergy Sessions unloaded successfully');
    },

    // ==================== INITIALIZATION ====================

    /**
     * Initialize Synergy components from existing files
     * Loads existing JavaScript modules dynamically
     */
    async initializeSynergyComponents() {
        try {
            // Check if SynergyThreadIntegration already exists (loaded by HTML)
            if (window.SynergyThreadIntegration) {
                this.state.threadIntegration = window.SynergyThreadIntegration;
                this.log.info('Using existing SynergyThreadIntegration');
            } else {
                // Load synergy-thread-integration.js dynamically
                await this.loadScript('modules_internal/synergy/synergy-thread-integration.js');
                this.state.threadIntegration = window.SynergyThreadIntegration;
                this.log.info('SynergyThreadIntegration loaded');
            }

            // Load other components if needed
            if (window.SynergySidebarController) {
                this.state.sidebarController = window.SynergySidebarController;
                this.log.info('Using existing SynergySidebarController');
            }

        } catch (error) {
            this.log.error('Failed to initialize Synergy components:', error);
            throw error;
        }
    },

    /**
     * Setup thread card integration
     * Configures drag & drop, badges, real-time events
     */
    async setupThreadIntegration() {
        try {
            if (!this.state.threadIntegration) {
                this.log.warn('SynergyThreadIntegration not available');
                return;
            }

            // Enable drag & drop if configured
            if (this.state.settings.enableDragDrop) {
                this.enableDragDrop();
            }

            // Enable badges if configured
            if (this.state.settings.showBadges) {
                this.enableBadges();
            }

            // Enable real-time updates if configured
            if (this.state.settings.realtimeUpdates) {
                this.enableRealtimeUpdates();
            }

            this.state.threadIntegrationActive = true;
            this.log.info('Thread card integration setup complete');

        } catch (error) {
            this.log.error('Failed to setup thread integration:', error);
        }
    },

    /**
     * Cleanup thread integration
     */
    cleanupThreadIntegration() {
        this.disableDragDrop();
        this.disableBadges();
        this.disableRealtimeUpdates();
        this.state.threadIntegrationActive = false;
    },

    // ==================== DRAG & DROP ====================

    enableDragDrop() {
        if (!this.state.threadIntegration) return;

        try {
            // Setup drag & drop handlers
            // This integrates with existing SynergyThreadIntegration code

            // Register drag provider
            if (typeof this.state.threadIntegration.startDrag === 'function') {
                this.state.dragDropEnabled = true;
                this.log.info('Drag & drop enabled');
            }

        } catch (error) {
            this.log.error('Failed to enable drag & drop:', error);
        }
    },

    disableDragDrop() {
        this.state.dragDropEnabled = false;
        this.log.info('Drag & drop disabled');
    },

    // ==================== BADGES ====================

    enableBadges() {
        if (!this.state.threadIntegration) return;

        try {
            // Enable thread card badges
            // This integrates with existing badge rendering code

            if (typeof this.state.threadIntegration.renderThreadBadge === 'function') {
                this.state.badgesEnabled = true;
                this.log.info('Thread badges enabled');
            }

        } catch (error) {
            this.log.error('Failed to enable badges:', error);
        }
    },

    disableBadges() {
        this.state.badgesEnabled = false;
        this.log.info('Thread badges disabled');
    },

    // ==================== REAL-TIME UPDATES ====================

    enableRealtimeUpdates() {
        if (!this.state.threadIntegration) return;

        try {
            // Subscribe to real-time events
            const events = [
                'thread_linked_to_synergy',
                'thread_unlinked_from_synergy',
                'synergy_session_updated',
                'synergy_session_deleted'
            ];

            events.forEach(eventName => {
                this.events.on(eventName, (data) => {
                    this.handleRealtimeUpdate(eventName, data);
                });
            });

            this.state.realtimeEnabled = true;
            this.log.info('Real-time updates enabled');

        } catch (error) {
            this.log.error('Failed to enable real-time updates:', error);
        }
    },

    disableRealtimeUpdates() {
        this.state.realtimeEnabled = false;
        this.log.info('Real-time updates disabled');
    },

    handleRealtimeUpdate(eventName, data) {
        this.log.info(`Real-time event: ${eventName}`, data);

        // Delegate to SynergyThreadIntegration if available
        if (this.state.threadIntegration &&
            typeof this.state.threadIntegration.handleRealtimeUpdate === 'function') {
            this.state.threadIntegration.handleRealtimeUpdate(eventName, data);
        }

        // Update local state
        switch (eventName) {
            case 'thread_linked_to_synergy':
                this.handleThreadLinked(data);
                break;
            case 'thread_unlinked_from_synergy':
                this.handleThreadUnlinked(data);
                break;
            case 'synergy_session_updated':
                this.handleSessionUpdated(data);
                break;
            case 'synergy_session_deleted':
                this.handleSessionDeleted(data);
                break;
        }
    },

    // ==================== EVENT HANDLERS ====================

    handleThreadLinked(data) {
        const { thread_id, synergy_card_id, synergy_card_name } = data;
        this.state.linkedThreads.set(thread_id, { synergy_card_id, synergy_card_name });
        this.log.info(`Thread ${thread_id} linked to Synergy card ${synergy_card_id}`);

        // Emit event for UI update
        this.events.emit('synergy:thread-linked', data);
    },

    handleThreadUnlinked(data) {
        const { thread_id } = data;
        this.state.linkedThreads.delete(thread_id);
        this.log.info(`Thread ${thread_id} unlinked from Synergy`);

        // Emit event for UI update
        this.events.emit('synergy:thread-unlinked', data);
    },

    handleSessionUpdated(data) {
        const { session_id } = data;
        this.log.info(`Synergy session ${session_id} updated`);

        // Emit event for UI update
        this.events.emit('synergy:session-updated', data);
    },

    handleSessionDeleted(data) {
        const { session_id } = data;
        this.log.info(`Synergy session ${session_id} deleted`);

        // Remove from active sessions
        this.state.activeSessions = this.state.activeSessions.filter(s => s.id !== session_id);

        // Emit event for UI update
        this.events.emit('synergy:session-deleted', data);
    },

    // ==================== EVENT SUBSCRIPTIONS ====================

    subscribeToEvents() {
        // Listen for thread manager events
        this.events.on('thread:created', (data) => {
            this.log.info('Thread created:', data.thread_id);
        });

        this.events.on('thread:deleted', (data) => {
            // Cleanup any Synergy links
            this.state.linkedThreads.delete(data.thread_id);
        });

        // Listen for UI events (if applicable)
        this.events.on('ui:sidebar-opened', (data) => {
            if (data.sidebar === 'synergy') {
                this.log.info('Synergy sidebar opened');
            }
        });
    },

    // ==================== PUBLIC API ====================

    /**
     * Link thread to Synergy session
     * @param {number} threadId - Thread ID
     * @param {number} sessionId - Synergy session ID
     */
    async linkThreadToSession(threadId, sessionId) {
        try {
            this.log.info(`Linking thread ${threadId} to session ${sessionId}...`);

            if (this.state.threadIntegration &&
                typeof this.state.threadIntegration.linkThreadToSession === 'function') {
                const result = await this.state.threadIntegration.linkThreadToSession(threadId, sessionId);
                this.log.info('Thread linked successfully');
                return result;
            }

            // Fallback: Direct API call
            const response = await this.api.post('/api/synergy/link-thread', {
                thread_id: threadId,
                session_id: sessionId
            });

            if (response.success) {
                this.handleThreadLinked({
                    thread_id: threadId,
                    synergy_card_id: sessionId,
                    synergy_card_name: response.session_title
                });
            }

            return response;

        } catch (error) {
            this.log.error('Failed to link thread:', error);
            throw error;
        }
    },

    /**
     * Unlink thread from Synergy session
     * @param {number} threadId - Thread ID
     */
    async unlinkThread(threadId) {
        try {
            this.log.info(`Unlinking thread ${threadId}...`);

            const response = await this.api.post('/api/synergy/unlink-thread', {
                thread_id: threadId
            });

            if (response.success) {
                this.handleThreadUnlinked({ thread_id: threadId });
            }

            return response;

        } catch (error) {
            this.log.error('Failed to unlink thread:', error);
            throw error;
        }
    },

    /**
     * Get linked Synergy session for thread
     * @param {number} threadId - Thread ID
     * @returns {Object|null} Synergy session info or null
     */
    getLinkedSession(threadId) {
        return this.state.linkedThreads.get(threadId) || null;
    },

    /**
     * Check if thread is linked to Synergy
     * @param {number} threadId - Thread ID
     * @returns {boolean} True if linked
     */
    isThreadLinked(threadId) {
        return this.state.linkedThreads.has(threadId);
    },

    // ==================== STORAGE ====================

    async loadSettings() {
        try {
            const savedSettings = this.storage.get('synergy_settings');
            if (savedSettings) {
                this.state.settings = { ...this.state.settings, ...savedSettings };
            }

            this.log.info('Settings loaded');
        } catch (error) {
            this.log.error('Failed to load settings:', error);
        }
    },

    saveSettings() {
        try {
            this.storage.set('synergy_settings', this.state.settings);
            this.log.info('Settings saved');
        } catch (error) {
            this.log.error('Failed to save settings:', error);
        }
    },

    // ==================== UTILITIES ====================

    async loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
};
