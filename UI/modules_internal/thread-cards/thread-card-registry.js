/**
 * FILE: UI/modules/thread-cards/thread-card-registry.js
 * PURPOSE: Central registry for thread card integrations from all modules
 * 
 * ARCHITECTURE:
 * - Lightweight integration layer on top of existing ModuleLoader
 * - Reads thread_card_integration section from module manifests
 * - Provides dynamic badge rendering and drop handling
 * - Manages real-time WebSocket subscriptions for thread updates
 * 
 * PATTERN: Consumer of ModuleLoader data (NOT parallel system)
 * 
 * DEPENDENCIES:
 * - ModuleLoader (singleton) - Must be initialized first
 * - RealtimeManager (if available) - For WebSocket subscriptions
 * 
 * EXPORTS:
 * - ThreadCardRegistry (singleton)
 * - renderBadgesForThread(thread) - Dynamic badge HTML generation
 * - handleDrop(event, threadId, location) - Multi-MIME-type drop handling
 * - handleRealtimeEvent(eventName, data) - WebSocket event handler
 * 
 * USED BY:
 * - UI/external/modules/thread-cards/thread-card-templates.js (badge rendering)
 * - UI/modules/thread-manager/thread-manager-interactions.js (drop handling)
 * 
 * NOTES:
 * - Waits for ModuleLoader.initialize() before reading manifests
 * - Registers only modules with thread_card_integration.enabled = true
 * - Backward compatible - existing modules work without changes
 * - Real-time updates trigger automatic thread card refresh
 * 
 * LAST MODIFIED: 2025-11-28 - Initial implementation
 */

class ThreadCardRegistry {
    constructor() {
        // Singleton pattern
        if (ThreadCardRegistry.instance) {
            return ThreadCardRegistry.instance;
        }

        // Core storage
        this.modules = new Map();                      // moduleId → full manifest
        this.dragHandlers = new Map();                 // mimeType → {moduleId, handler}
        this.badgeRenderers = new Map();               // moduleId → badge config
        this.realtimeSubscriptions = new Map();        // eventName → [handlers]

        // State
        this.initialized = false;
        this.initPromise = null;

        ThreadCardRegistry.instance = this;

        console.log('[ThreadCardRegistry] Instance created (waiting for initialization)');
    }

    /**
     * Initialize registry by reading from ModuleLoader
     * 
     * Process:
     * 1. Wait for ModuleLoader to complete initialization
     * 2. Iterate through ModuleLoader.modules
     * 3. Register modules with thread_card_integration.enabled
     * 4. Set up real-time subscriptions
     */
    async initialize() {
        // Prevent duplicate initialization
        if (this.initialized) {
            console.log('[ThreadCardRegistry] Already initialized');
            return;
        }

        // Return existing promise if initialization in progress
        if (this.initPromise) {
            return this.initPromise;
        }

        this.initPromise = this._doInitialize();
        return this.initPromise;
    }

    async _doInitialize() {
        console.log('[ThreadCardRegistry] Starting initialization...');

        try {
            // Wait for ModuleLoader (backward compatibility check)
            await this.waitForModuleLoader();

            // Check if ModuleLoader has modules (legacy support)
            if (window.moduleLoader && window.moduleLoader.modules && window.moduleLoader.modules.size > 0) {
                console.log(`[ThreadCardRegistry] Processing ${window.moduleLoader.modules.size} modules from ModuleLoader...`);

                // Iterate through ModuleLoader's modules
                let registeredCount = 0;
                for (const [moduleId, manifest] of window.moduleLoader.modules) {
                    const integration = manifest.thread_card_integration;

                    if (integration && integration.enabled) {
                        await this.registerThreadCardIntegration(moduleId, manifest);
                        registeredCount++;
                        console.log(`[ThreadCardRegistry] ✅ Registered: ${moduleId}`);
                    } else {
                        console.log(`[ThreadCardRegistry] ⏭️  Skipped: ${moduleId} (no thread_card_integration)`);
                    }
                }

                console.log(`[ThreadCardRegistry] ✅ Initialization complete (${registeredCount} modules with thread card integration)`);
            } else {
                // No ModuleLoader - register built-in integrations directly
                console.log('[ThreadCardRegistry] No ModuleLoader - registering built-in integrations...');

                // Register built-in Synergy integration if available
                if (typeof SynergyThreadIntegration !== 'undefined') {
                    console.log('[ThreadCardRegistry] ✅ Registered built-in: Synergy');
                    // Synergy integration is standalone - no registration needed
                }

                console.log('[ThreadCardRegistry] ✅ Initialization complete (standalone mode)');
            }

            // Set up real-time subscriptions
            this.setupRealtimeSubscriptions();

            this.initialized = true;

        } catch (error) {
            console.error('[ThreadCardRegistry] ❌ Initialization failed:', error);
            this.initialized = false;
            // Don't throw - allow graceful degradation
            this.initialized = true; // Mark as initialized to prevent retry loops
        }
    }

    /**
     * Wait for ModuleLoader to complete initialization
     * 
     * UPDATED: ModuleLoader was archived - now operates independently
     * 
     * @returns {Promise<void>}
     */
    async waitForModuleLoader() {
        // ModuleLoader was archived - ThreadCardRegistry now operates independently
        // Check if there are any legacy module integrations we should support

        if (window.moduleLoader && window.moduleLoader.modules && window.moduleLoader.modules.size > 0) {
            console.log('[ThreadCardRegistry] ModuleLoader found (legacy mode)');
            return Promise.resolve();
        }

        // No ModuleLoader - continue without it
        console.log('[ThreadCardRegistry] Operating without ModuleLoader (post-archive mode)');
        return Promise.resolve();
    }

    /**
     * PUBLIC API: Register a badge renderer directly (for standalone modules)
     * 
     * This method allows modules to register themselves without needing a manifest.
     * Used by legacy badge modules that predate the registry system.
     * 
     * @param {string} moduleId - Unique module identifier (e.g., 'synergy_sessions', 'workflows')
     * @param {Object} badgeConfig - Badge configuration
     * @param {string} badgeConfig.condition - JavaScript condition to check for linkage (e.g., 'thread.synergy_card_id !== null')
     * @param {string} badgeConfig.renderFunction - Fully qualified function name (e.g., 'window.SynergyThreadIntegration.renderThreadBadge')
     * @param {Object} badgeConfig.config - Badge appearance config (icon, color, label, priority)
     * @param {string} [badgeConfig.placeholderClick] - Function to call when placeholder is clicked
     */
    registerBadgeRenderer(moduleId, badgeConfig) {
        if (!moduleId || !badgeConfig) {
            console.error('[ThreadCardRegistry] registerBadgeRenderer: Missing required parameters');
            return;
        }

        // Validate required fields
        if (!badgeConfig.renderFunction) {
            console.error(`[ThreadCardRegistry] Badge config for ${moduleId} missing renderFunction`);
            return;
        }

        // Store badge renderer
        this.badgeRenderers.set(moduleId, {
            condition: badgeConfig.condition,
            renderFunction: badgeConfig.renderFunction,
            config: badgeConfig.config || {},
            priority: badgeConfig.config?.priority || 999,
            placeholderClick: badgeConfig.placeholderClick
        });

        console.log(`[ThreadCardRegistry] ✅ Registered badge renderer: ${moduleId} (priority ${badgeConfig.config?.priority || 999})`);
    }

    /**
     * Register a module's thread card integration (from manifest)
     * 
     * @param {string} moduleId - Module identifier
     * @param {Object} manifest - Full module manifest
     */
    async registerThreadCardIntegration(moduleId, manifest) {
        const integration = manifest.thread_card_integration;

        if (!integration || !integration.enabled) {
            console.warn(`[ThreadCardRegistry] Module ${moduleId} has no enabled integration`);
            return;
        }

        // Store full manifest
        this.modules.set(moduleId, manifest);

        // Register drag-and-drop handlers
        if (integration.drag_and_drop) {
            // Register accepts (drop handlers)
            if (Array.isArray(integration.drag_and_drop.accepts)) {
                for (const accept of integration.drag_and_drop.accepts) {
                    const mimeType = accept.mime_type || accept.data_type;
                    this.dragHandlers.set(mimeType, {
                        moduleId,
                        handler: accept.handler,
                        dataType: accept.data_type
                    });
                    console.log(`[ThreadCardRegistry]   📥 Registered drop handler: ${mimeType} → ${accept.handler}`);
                }
            }

            // Register provides (drag handlers)
            if (Array.isArray(integration.drag_and_drop.provides)) {
                for (const provide of integration.drag_and_drop.provides) {
                    console.log(`[ThreadCardRegistry]   📤 Module provides: ${provide.data_type}`);
                    // Stored for reference, drag initiation is handled by each module
                }
            }
        }

        // Register badge renderer
        if (integration.badge && integration.badge.enabled) {
            this.badgeRenderers.set(moduleId, {
                condition: integration.badge.condition,
                renderFunction: integration.badge.render_function,
                config: integration.badge.config || {},
                priority: integration.badge.config?.priority || 999
            });
            console.log(`[ThreadCardRegistry]   🎨 Registered badge: ${integration.badge.render_function}`);
        }

        // Store real-time event handlers
        if (integration.realtime_events && integration.realtime_events.enabled) {
            const events = integration.realtime_events.events || [];
            for (const eventName of events) {
                if (!this.realtimeSubscriptions.has(eventName)) {
                    this.realtimeSubscriptions.set(eventName, []);
                }
                this.realtimeSubscriptions.get(eventName).push({
                    moduleId,
                    handler: integration.realtime_events.handler
                });
                console.log(`[ThreadCardRegistry]   📡 Registered realtime: ${eventName} → ${integration.realtime_events.handler}`);
            }
        }
    }

    /**
     * Render all badges for a thread (LINKED BADGES ONLY - NO PLACEHOLDERS)
     * 
     * ✅ CRITICAL FIX (Dec 1, 2025): Registry now returns ONLY linked badges
     * - Placeholders are handled by ThreadCardTemplates._fallbackBadgeRendering()
     * - This prevents malformed placeholder HTML with wrong class names/functions
     * - Returns empty string if no linked badges (triggers fallback system)
     * 
     * @param {Object} thread - Thread object with linkage data
     * @param {string} location - Location identifier ('prime', 'synergy', etc.)
     * @returns {string} HTML string with ONLY linked badges (or empty for fallback)
     */
    renderBadgesForThread(thread, location = 'prime') {
        if (!this.initialized) {
            // Silent return - fallback system will handle it
            return '';
        }

        const badges = [];

        // ✅ Collect ONLY linked badges (NO PLACEHOLDERS)
        for (const [moduleId, badgeConfig] of this.badgeRenderers) {
            try {
                // Evaluate condition (if specified)
                const hasLinkage = badgeConfig.condition ?
                    this.evaluateCondition(badgeConfig.condition, thread) : false;

                if (hasLinkage) {
                    // Render linked badge ONLY
                    const renderFn = this.resolveFunction(badgeConfig.renderFunction);
                    if (!renderFn) {
                        console.warn(`[ThreadCardRegistry] Render function not found: ${badgeConfig.renderFunction}`);
                        continue;
                    }

                    const html = renderFn(thread, badgeConfig.config);
                    if (html) {
                        badges.push({
                            html,
                            priority: badgeConfig.priority,
                            moduleId
                        });
                    }
                }
                // ❌ REMOVED: Placeholder rendering (causes malformed HTML)
                // Placeholders are now handled by ThreadCardTemplates._fallbackBadgeRendering()
            } catch (error) {
                console.error(`[ThreadCardRegistry] Error rendering badge for ${moduleId}:`, error);
            }
        }

        // If no linked badges, return empty (triggers fallback system)
        if (badges.length === 0) {
            // Log once per session to avoid spam
            if (!this._loggedNoLinkedBadges) {
                console.log('[ThreadCardRegistry] No linked badges - using fallback system for placeholders');
                this._loggedNoLinkedBadges = true;
            }
            return '';
        }

        // Sort by priority (lower number = higher priority)
        badges.sort((a, b) => a.priority - b.priority);

        // Return ONLY linked badges wrapped in container
        return `<div class="thread-ui-links-row" style="display: flex; flex-direction: column; gap: 8px; margin-top: 8px;">
            ${badges.map(item => item.html).join('\n')}
        </div>`;
    }

    /**
     * DEPRECATED: renderPlaceholder() - REMOVED (Dec 1, 2025)
     * 
     * ❌ This method generated malformed placeholder HTML:
     * - Wrong class names: thread-item-workflow_automation (should be thread-item-workflow)
     * - Wrong functions: ThreadManager.openLinkModal_workflow_automation (doesn't exist)
     * - Missing colored borders (no proper CSS classes)
     * - Wrong icons (fa-link instead of fa-robot, fa-cogs, etc.)
     * 
     * ✅ Solution: Let ThreadCardTemplates._fallbackBadgeRendering() handle placeholders
     * - It has the correct HTML structure, class names, colors, and icons
     * - renderBadgesForThread() now returns empty string when no linked badges
     * - This triggers the fallback system automatically
     * 
     * @deprecated Use ThreadCardTemplates._fallbackBadgeRendering() instead
     */
    renderPlaceholder(moduleId, threadId, config) {
        // ❌ DISABLED - This method is no longer used
        console.warn('[ThreadCardRegistry] renderPlaceholder() is deprecated - fallback system handles placeholders');
        return '';
    }

    /**
     * Handle drop event with registered handlers
     * 
     * @param {DragEvent} event - Drag event
     * @param {string} threadId - Target thread ID
     * @param {string} location - Drop location ('prime', 'agent-X', etc.)
     * @returns {Promise<boolean>} True if handled
     */
    async handleDrop(event, threadId, location) {
        if (!this.initialized) {
            console.warn('[ThreadCardRegistry] Not initialized - cannot handle drop');
            return false;
        }

        // Check all registered MIME types
        for (const [mimeType, handlerInfo] of this.dragHandlers) {
            const data = event.dataTransfer.getData(mimeType);

            if (data) {
                console.log(`[ThreadCardRegistry] 📥 Drop detected: ${mimeType} → thread ${threadId}`);

                try {
                    // Resolve handler function
                    const handlerFn = this.resolveFunction(handlerInfo.handler);
                    if (!handlerFn) {
                        console.error(`[ThreadCardRegistry] Handler not found: ${handlerInfo.handler}`);
                        continue;
                    }

                    // Call handler: handler(data, threadId, location)
                    await handlerFn(data, threadId, location);

                    console.log(`[ThreadCardRegistry] ✅ Drop handled by ${handlerInfo.moduleId}`);
                    return true;

                } catch (error) {
                    console.error(`[ThreadCardRegistry] ❌ Drop handler error (${handlerInfo.moduleId}):`, error);
                    // Continue checking other handlers
                }
            }
        }

        return false; // No handler found
    }

    /**
     * Handle real-time event
     * 
     * @param {string} eventName - Event name (e.g., 'thread_linked_to_synergy')
     * @param {Object} data - Event data
     */
    async handleRealtimeEvent(eventName, data) {
        if (!this.initialized) {
            return;
        }

        const handlers = this.realtimeSubscriptions.get(eventName);
        if (!handlers || handlers.length === 0) {
            return;
        }

        console.log(`[ThreadCardRegistry] 📡 Realtime event: ${eventName}`);

        for (const handlerInfo of handlers) {
            try {
                const handlerFn = this.resolveFunction(handlerInfo.handler);
                if (handlerFn) {
                    await handlerFn(data);
                }
            } catch (error) {
                console.error(`[ThreadCardRegistry] Realtime handler error (${handlerInfo.moduleId}):`, error);
            }
        }
    }

    /**
     * Set up real-time WebSocket subscriptions
     */
    setupRealtimeSubscriptions() {
        if (!window.RealtimeManager) {
            console.warn('[ThreadCardRegistry] RealtimeManager not available - skipping subscriptions');
            return;
        }

        console.log('[ThreadCardRegistry] Setting up real-time subscriptions...');

        for (const [eventName, handlers] of this.realtimeSubscriptions) {
            window.RealtimeManager.subscribe(eventName, (data) => {
                this.handleRealtimeEvent(eventName, data);
            });
            console.log(`[ThreadCardRegistry] ✅ Subscribed to: ${eventName}`);
        }
    }

    /**
     * Evaluate condition string against thread object
     * 
     * @param {string} condition - Condition expression (e.g., "thread.synergy_session_id !== null")
     * @param {Object} thread - Thread object
     * @returns {boolean} Condition result
     */
    evaluateCondition(condition, thread) {
        try {
            // Create safe evaluation context
            const evalFunc = new Function('thread', `return ${condition};`);
            return evalFunc(thread);
        } catch (error) {
            console.error('[ThreadCardRegistry] Condition evaluation error:', error);
            return false;
        }
    }

    /**
     * Resolve function from string reference or direct function
     * 
     * @param {string|Function} functionRef - Function reference (e.g., "window.SynergyModule.renderBadge") or direct function
     * @returns {Function|null} Resolved function
     */
    resolveFunction(functionRef) {
        if (!functionRef) return null;

        try {
            // ✅ FIX: Handle direct function objects (backward compatibility)
            if (typeof functionRef === 'function') {
                return functionRef;
            }

            // Handle string references
            if (typeof functionRef !== 'string') {
                console.warn('[ThreadCardRegistry] functionRef must be string or function, got:', typeof functionRef);
                return null;
            }

            const parts = functionRef.split('.');
            let obj = window;

            for (const part of parts) {
                if (part === 'window') continue;
                obj = obj[part];
                if (!obj) return null;
            }

            return typeof obj === 'function' ? obj : null;
        } catch (error) {
            console.error('[ThreadCardRegistry] Function resolution error:', error);
            return null;
        }
    }

    /**
     * Get all registered modules with thread card integration
     * 
     * @returns {Array} Array of {moduleId, manifest}
     */
    getRegisteredModules() {
        return Array.from(this.modules.entries()).map(([moduleId, manifest]) => ({
            moduleId,
            manifest
        }));
    }

    /**
     * Check if a specific module is registered
     * 
     * @param {string} moduleId - Module identifier
     * @returns {boolean}
     */
    hasModule(moduleId) {
        return this.modules.has(moduleId);
    }
}

// Create singleton instance
const threadCardRegistry = new ThreadCardRegistry();

// Export to window for global access
window.ThreadCardRegistry = threadCardRegistry;

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('[ThreadCardRegistry] DOMContentLoaded - scheduling initialization');
        // Wait 1 second for ModuleLoader to initialize first
        setTimeout(() => {
            threadCardRegistry.initialize().catch(error => {
                console.error('[ThreadCardRegistry] Auto-initialization failed:', error);
            });
        }, 1000);
    });
} else {
    // DOM already loaded
    console.log('[ThreadCardRegistry] DOM already loaded - scheduling initialization');
    setTimeout(() => {
        threadCardRegistry.initialize().catch(error => {
            console.error('[ThreadCardRegistry] Auto-initialization failed:', error);
        });
    }, 1000);
}

console.log('[ThreadCardRegistry] Module loaded (singleton created)');
