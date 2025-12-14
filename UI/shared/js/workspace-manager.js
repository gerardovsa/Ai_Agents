/**
 * FILE: UI/shared/js/workspace-manager.js
 * PURPOSE: Manage user workspace persistence (localStorage + Database sync)
 * 
 * FEATURES:
 * - Save/load agent column settings (view mode, width, collapsed state)
 * - localStorage for instant UI updates (no latency)
 * - Database sync for cross-device persistence
 * - Debounced save to reduce database writes
 * - Conflict resolution (localStorage wins, database is backup)
 * 
 * STORAGE SCHEMA:
 * - localStorage keys: viewMode_agent{id}, columnWidth_agent{id}, columnCollapsed_agent{id}
 * - Database: sessions.user_command_center table (JSONB structure)
 * 
 * DEPENDENCIES:
 * - Supabase client (for database sync)
 * - UserAuth (for user_id)
 * 
 * EXPORTS:
 * - WorkspaceManager.save(agentId, key, value) - Save setting
 * - WorkspaceManager.load(agentId, key, defaultValue) - Load setting
 * - WorkspaceManager.loadAll() - Load all workspace settings
 * - WorkspaceManager.syncToDatabase() - Sync localStorage to database
 * - WorkspaceManager.syncFromDatabase() - Load database settings to localStorage
 * 
 * USAGE:
 * ```javascript
 * // Save view mode
 * WorkspaceManager.save(1, 'viewMode', 'ai-collapsed');
 * 
 * // Load view mode
 * const viewMode = WorkspaceManager.load(1, 'viewMode', 'all-expanded');
 * 
 * // Load all settings on page load
 * await WorkspaceManager.loadAll();
 * ```
 * 
 * CREATED: December 12, 2025
 */

const WorkspaceManager = (function () {
    'use strict';

    // Configuration
    const CONFIG = {
        DEBOUNCE_DELAY: 500,      // Wait 500ms before syncing to database
        SYNC_ON_CHANGE: true,     // Auto-sync to database on change
        SYNC_ON_LOAD: true,       // Load from database on page load
        CONFLICT_STRATEGY: 'local-wins'  // 'local-wins' or 'remote-wins'
    };

    // Debounce timer for database sync
    let syncTimer = null;

    // Dirty flag (tracks if localStorage has unsaved changes)
    let isDirty = false;

    // Track if table missing warning already shown (prevents spam)
    let tableMissingWarningShown = false;

    /**
     * Save a workspace setting to localStorage (instant)
     * Optionally sync to database after debounce delay
     * 
     * @param {number|string} agentId - Agent ID (or 'prime')
     * @param {string} key - Setting key ('viewMode', 'columnWidth', 'columnCollapsed')
     * @param {any} value - Setting value
     */
    function save(agentId, key, value) {
        try {
            // Save to localStorage (instant)
            const storageKey = agentId === 'prime' ?
                `${key}_prime` :
                `${key}_agent${agentId}`;

            localStorage.setItem(storageKey, JSON.stringify(value));
            console.log(`💾 [WorkspaceManager] Saved ${storageKey} = ${JSON.stringify(value)}`);

            // Mark as dirty (needs database sync)
            isDirty = true;

            // Schedule database sync (debounced)
            if (CONFIG.SYNC_ON_CHANGE) {
                scheduleDatabaseSync();
            }
        } catch (error) {
            console.error(`❌ [WorkspaceManager] Failed to save ${key}:`, error);
        }
    }

    /**
     * Load a workspace setting from localStorage
     * 
     * @param {number|string} agentId - Agent ID (or 'prime')
     * @param {string} key - Setting key
     * @param {any} defaultValue - Default value if not found
     * @returns {any} Setting value
     */
    function load(agentId, key, defaultValue = null) {
        try {
            const storageKey = agentId === 'prime' ?
                `${key}_prime` :
                `${key}_agent${agentId}`;

            const value = localStorage.getItem(storageKey);

            if (value === null) {
                return defaultValue;
            }

            return JSON.parse(value);
        } catch (error) {
            console.error(`❌ [WorkspaceManager] Failed to load ${key}:`, error);
            return defaultValue;
        }
    }

    /**
     * Load all workspace settings from localStorage
     * Returns structured object with all agent settings
     * 
     * @returns {object} Workspace settings object
     */
    function loadAll() {
        const workspace = {
            agents: {},
            prime: {},
            columnOrder: []
        };

        try {
            // Scan localStorage for all agent settings
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);

                if (!key) continue;

                // Agent settings: viewMode_agent1, columnWidth_agent1, etc.
                const agentMatch = key.match(/(viewMode|columnWidth|columnCollapsed)_agent(\d+)/);
                if (agentMatch) {
                    const [, settingKey, agentId] = agentMatch;
                    const value = load(agentId, settingKey);

                    if (!workspace.agents[agentId]) {
                        workspace.agents[agentId] = {};
                    }

                    workspace.agents[agentId][settingKey] = value;
                }

                // Prime settings: viewMode_prime
                const primeMatch = key.match(/(viewMode)_prime/);
                if (primeMatch) {
                    const [, settingKey] = primeMatch;
                    workspace.prime[settingKey] = load('prime', settingKey);
                }
            }

            console.log(`📂 [WorkspaceManager] Loaded workspace:`, workspace);
            return workspace;
        } catch (error) {
            console.error(`❌ [WorkspaceManager] Failed to load workspace:`, error);
            return workspace;
        }
    }

    /**
     * Schedule database sync (debounced to reduce writes)
     */
    function scheduleDatabaseSync() {
        // Clear existing timer
        if (syncTimer) {
            clearTimeout(syncTimer);
        }

        // Schedule new sync after debounce delay
        syncTimer = setTimeout(() => {
            syncToDatabase();
        }, CONFIG.DEBOUNCE_DELAY);

        console.log(`⏳ [WorkspaceManager] Database sync scheduled in ${CONFIG.DEBOUNCE_DELAY}ms`);
    }

    /**
     * Sync localStorage to database (background operation)
     */
    async function syncToDatabase() {
        if (!isDirty) {
            console.log(`✅ [WorkspaceManager] No changes to sync`);
            return;
        }

        try {
            // Get current user ID
            const userId = getUserId();
            if (!userId) {
                console.warn(`⚠️ [WorkspaceManager] No user ID - skipping database sync`);
                return;
            }

            // Get Supabase client
            if (typeof SupabaseConnectionManager === 'undefined') {
                console.warn(`⚠️ [WorkspaceManager] SupabaseConnectionManager not available - skipping database sync`);
                return;
            }

            const supabase = await SupabaseConnectionManager.getClient();
            if (!supabase) {
                console.warn(`⚠️ [WorkspaceManager] Could not get Supabase client - skipping database sync`);
                return;
            }

            // Load all workspace settings from localStorage
            const workspace = loadAll();
            workspace.lastSyncedAt = new Date().toISOString();

            console.log(`☁️ [WorkspaceManager] Syncing to database for user ${userId}...`);

            // CRITICAL FIX (Dec 14, 2025): Use RPC to access sessions schema
            // PostgREST API doesn't allow .schema() for custom schemas (only public/graphql_public)
            // We use an RPC function to upsert into sessions.user_command_center
            const { data, error } = await supabase
                .rpc('upsert_workspace_settings', {
                    p_user_id: userId,
                    p_workspace_data: workspace
                });

            if (error) {
                // Check for missing RPC function (PGRST202 = function not found)
                if (error.code === 'PGRST202' || error.code === '42883' || error.message?.includes('not found') || error.message?.includes('does not exist')) {
                    if (!tableMissingWarningShown) {
                        console.warn(`⚠️ [WorkspaceManager] RPC function 'upsert_workspace_settings' not found - workspace will only persist in localStorage`);
                        console.warn(`ℹ️ [WorkspaceManager] To enable database sync, run: SQL migration to create the RPC function`);
                        tableMissingWarningShown = true;
                    }
                    return;
                }
                console.error(`❌ [WorkspaceManager] Database sync failed:`, error);
                return;
            }

            console.log(`✅ [WorkspaceManager] Synced to database successfully`);
            isDirty = false;
        } catch (error) {
            console.error(`❌ [WorkspaceManager] Database sync error:`, error);
        }
    }

    /**
     * Subscribe to real-time workspace updates (cross-tab/device sync)
     */
    function subscribeToRealtime(userId) {
        if (typeof SupabaseRealtimeManager === 'undefined') {
            console.warn(`⚠️ [WorkspaceManager] RealtimeManager not available - no live sync`);
            return;
        }

        console.log(`🔄 [WorkspaceManager] Subscribing to real-time updates for user ${userId}...`);

        SupabaseRealtimeManager.subscribeToWorkspace(userId, (remoteWorkspace) => {
            console.log(`📥 [WorkspaceManager] Received remote workspace update:`, remoteWorkspace);

            // Apply remote changes to localStorage (if different)
            applyRemoteWorkspace(remoteWorkspace);
        });

        console.log(`✅ [WorkspaceManager] Subscribed to real-time workspace updates`);
    }

    /**
     * Apply remote workspace changes to localStorage
     */
    function applyRemoteWorkspace(remoteWorkspace) {
        if (!remoteWorkspace) return;

        console.log(`🔄 [WorkspaceManager] Applying remote workspace changes...`);

        // Apply agent settings
        for (const [agentId, settings] of Object.entries(remoteWorkspace.agents || {})) {
            if (settings.viewMode !== undefined) {
                localStorage.setItem(`viewMode_agent${agentId}`, JSON.stringify(settings.viewMode));
            }
            if (settings.columnWidth !== undefined) {
                localStorage.setItem(`columnWidth_agent${agentId}`, JSON.stringify(settings.columnWidth));
            }
            if (settings.columnCollapsed !== undefined) {
                localStorage.setItem(`columnCollapsed_agent${agentId}`, JSON.stringify(settings.columnCollapsed));
            }
        }

        // Apply prime settings
        if (remoteWorkspace.prime && remoteWorkspace.prime.viewMode !== undefined) {
            localStorage.setItem('viewMode_prime', JSON.stringify(remoteWorkspace.prime.viewMode));
        }

        console.log(`✅ [WorkspaceManager] Remote workspace applied - reloading UI...`);

        // Emit event to trigger UI reload
        window.dispatchEvent(new CustomEvent('workspace:updated', {
            detail: { source: 'remote', workspace: remoteWorkspace }
        }));
    }

    /**
     * Sync database settings to localStorage (on page load)
     */
    async function syncFromDatabase() {
        try {
            // Get current user ID
            const userId = getUserId();
            if (!userId) {
                console.warn(`⚠️ [WorkspaceManager] No user ID - skipping database load`);
                return null;
            }

            // Subscribe to real-time updates
            subscribeToRealtime(userId);

            // Get Supabase client
            if (typeof SupabaseConnectionManager === 'undefined') {
                console.warn(`⚠️ [WorkspaceManager] SupabaseConnectionManager not available - skipping database load`);
                return null;
            }

            const supabase = await SupabaseConnectionManager.getClient();
            if (!supabase) {
                console.warn(`⚠️ [WorkspaceManager] Could not get Supabase client - skipping database load`);
                return null;
            }

            console.log(`☁️ [WorkspaceManager] Loading from database for user ${userId}...`);

            // CRITICAL FIX (Dec 14, 2025): Use RPC to access sessions schema
            // PostgREST API doesn't allow .schema() for custom schemas
            const { data, error } = await supabase
                .rpc('get_workspace_settings', {
                    p_user_id: userId
                });

            if (error) {
                // Check for missing RPC function
                if (error.code === 'PGRST202' || error.code === '42883' || error.message?.includes('not found')) {
                    if (!tableMissingWarningShown) {
                        console.warn(`⚠️ [WorkspaceManager] RPC function 'get_workspace_settings' not found - workspace will only persist in localStorage`);
                        tableMissingWarningShown = true;
                    }
                    return null;
                }
                // No data found is OK (new user)
                if (error.message?.includes('No rows') || error.code === 'PGRST116') {
                    console.log(`ℹ️ [WorkspaceManager] No workspace found in database (new user)`);
                    return null;
                }
                console.error(`❌ [WorkspaceManager] Database load failed:`, error);
                return null;
            }

            if (!data) {
                console.log(`ℹ️ [WorkspaceManager] No workspace data in database`);
                return null;
            }

            const workspace = data;
            console.log(`📥 [WorkspaceManager] Loaded from database:`, workspace);

            // Apply conflict resolution strategy
            if (CONFIG.CONFLICT_STRATEGY === 'local-wins') {
                // Only load database settings if localStorage is empty
                const localWorkspace = loadAll();
                const hasLocalSettings = Object.keys(localWorkspace.agents).length > 0;

                if (hasLocalSettings) {
                    console.log(`ℹ️ [WorkspaceManager] Local settings exist - keeping local (conflict strategy: local-wins)`);
                    return workspace;
                }
            }

            // Save database settings to localStorage
            // Agents
            for (const [agentId, settings] of Object.entries(workspace.agents || {})) {
                if (settings.viewMode !== undefined) {
                    save(agentId, 'viewMode', settings.viewMode);
                }
                if (settings.columnWidth !== undefined) {
                    save(agentId, 'columnWidth', settings.columnWidth);
                }
                if (settings.columnCollapsed !== undefined) {
                    save(agentId, 'columnCollapsed', settings.columnCollapsed);
                }
            }

            // Prime
            if (workspace.prime && workspace.prime.viewMode !== undefined) {
                save('prime', 'viewMode', workspace.prime.viewMode);
            }

            console.log(`✅ [WorkspaceManager] Applied database settings to localStorage`);
            isDirty = false;  // Don't sync back immediately
            return workspace;
        } catch (error) {
            console.error(`❌ [WorkspaceManager] Database load error:`, error);
            return null;
        }
    }

    /**
     * Get current user ID from UserAuth
     * @returns {number|null} User ID
     */
    function getUserId() {
        if (typeof UserAuth !== 'undefined' && UserAuth.user && UserAuth.user.id) {
            return UserAuth.user.id;
        }
        return null;
    }

    /**
     * Clear all workspace settings (reset to defaults)
     */
    function clearAll() {
        try {
            // Clear localStorage
            const keysToRemove = [];
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key && (key.startsWith('viewMode_') || key.startsWith('columnWidth_') || key.startsWith('columnCollapsed_'))) {
                    keysToRemove.push(key);
                }
            }

            keysToRemove.forEach(key => localStorage.removeItem(key));
            console.log(`🗑️ [WorkspaceManager] Cleared ${keysToRemove.length} settings from localStorage`);

            // Mark as dirty to sync deletion to database
            isDirty = true;
            if (CONFIG.SYNC_ON_CHANGE) {
                scheduleDatabaseSync();
            }
        } catch (error) {
            console.error(`❌ [WorkspaceManager] Failed to clear workspace:`, error);
        }
    }

    /**
     * Force immediate database sync (bypass debounce)
     */
    async function forceSyncToDatabase() {
        if (syncTimer) {
            clearTimeout(syncTimer);
            syncTimer = null;
        }
        await syncToDatabase();
    }

    // Public API
    return {
        save,
        load,
        loadAll,
        syncToDatabase: forceSyncToDatabase,
        syncFromDatabase,
        clearAll,

        // Configuration
        setDebounceDelay: (delay) => { CONFIG.DEBOUNCE_DELAY = delay; },
        setSyncOnChange: (enabled) => { CONFIG.SYNC_ON_CHANGE = enabled; },
        setSyncOnLoad: (enabled) => { CONFIG.SYNC_ON_LOAD = enabled; },
        setConflictStrategy: (strategy) => { CONFIG.CONFLICT_STRATEGY = strategy; }
    };
})();

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.WorkspaceManager = WorkspaceManager;
}

console.log('✅ WorkspaceManager loaded');
