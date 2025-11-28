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
            // Wait for ModuleLoader
            await this.waitForModuleLoader();

            // Check if ModuleLoader has modules
            if (!window.moduleLoader || !window.moduleLoader.modules) {
                console.warn('[ThreadCardRegistry] ModuleLoader has no modules loaded');
                this.initialized = true;
                return;
            }

            console.log(`[ThreadCardRegistry] Processing ${window.moduleLoader.modules.size} modules...`);

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
            
            // Set up real-time subscriptions
            this.setupRealtimeSubscriptions();
            
            this.initialized = true;

        } catch (error) {
            console.error('[ThreadCardRegistry] ❌ Initialization failed:', error);
            this.initialized = false;
            throw error;
        }
    }

    /**
     * Wait for ModuleLoader to complete initialization
     * 
     * @returns {Promise<void>}
     */
    async waitForModuleLoader() {
        return new Promise((resolve, reject) => {
            const timeout = 30000; // 30 seconds max wait
            const startTime = Date.now();
            
            const checkInterval = setInterval(() => {
                // Check if ModuleLoader exists and is initialized
                if (window.moduleLoader && window.moduleLoader.modules && window.moduleLoader.modules.size > 0) {
                    clearInterval(checkInterval);
                    console.log('[ThreadCardRegistry] ModuleLoader ready');
                    resolve();
                    return;
                }

                // Check timeout
                if (Date.now() - startTime > timeout) {
                    clearInterval(checkInterval);
                    reject(new Error('Timeout waiting for ModuleLoader'));
                }
            }, 100); // Check every 100ms
        });
    }

    /**
     * Register a module's thread card integration
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
     * Render all badges for a thread
     * 
     * @param {Object} thread - Thread object with linkage data
     * @returns {string} HTML string with all applicable badges
     */
    renderBadgesForThread(thread) {
        if (!this.initialized) {
            console.warn('[ThreadCardRegistry] Not initialized - returning empty');
            return '';
        }

        const badges = [];

        // Collect all applicable badges
        for (const [moduleId, badgeConfig] of this.badgeRenderers) {
            try {
                // Evaluate condition (if specified)
                if (badgeConfig.condition) {
                    const conditionMet = this.evaluateCondition(badgeConfig.condition, thread);
                    if (!conditionMet) {
                        continue; // Skip this badge
                    }
                }

                // Get render function
                const renderFn = this.resolveFunction(badgeConfig.renderFunction);
                if (!renderFn) {
                    console.warn(`[ThreadCardRegistry] Render function not found: ${badgeConfig.renderFunction}`);
                    continue;
                }

                // Call render function
                const html = renderFn(thread, badgeConfig.config);
                if (html) {
                    badges.push({
                        html,
                        priority: badgeConfig.priority,
                        moduleId
                    });
                }
            } catch (error) {
                console.error(`[ThreadCardRegistry] Error rendering badge for ${moduleId}:`, error);
            }
        }

        // Sort by priority (lower number = higher priority)
        badges.sort((a, b) => a.priority - b.priority);

        // Combine HTML
        return `<div class="thread-ui-links-row" style="display: flex; flex-direction: column; gap: 8px; margin-top: 8px;">
            ${badges.map(b => b.html).join('\n')}
        </div>`;
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
     * Resolve function from string reference
     * 
     * @param {string} functionRef - Function reference (e.g., "window.SynergyModule.renderBadge")
     * @returns {Function|null} Resolved function
     */
    resolveFunction(functionRef) {
        if (!functionRef) return null;

        try {
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
