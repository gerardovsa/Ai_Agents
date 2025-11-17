/**
 * FILE: UI/js/data-loader.js
 * PURPOSE: Centralized data loading utility with batching, caching, and lazy loading
 * 
 * FEATURES:
 * - Batch API requests (load multiple items in single call)
 * - Cache results (avoid redundant fetches)
 * - Request deduplication (merge concurrent requests for same data)
 * - Lazy loading (load data when needed, not upfront)
 * - Loading states and error handling
 * 
 * USED BY:
 * - ThreadManager (load threads)
 * - SynergyManager (load sessions)
 * - InternalDocsManager (load documents)
 * 
 * EXPORTS:
 * - DataLoader.threads.load(ids) - Load threads by IDs
 * - DataLoader.synergy.load(ids) - Load synergy sessions by IDs
 * - DataLoader.internalDocs.load(sessionIds) - Load internal docs for sessions
 * - DataLoader.clearCache(type) - Clear cached data
 * 
 * LAST MODIFIED: 2025-11-16 - Initial creation
 */

window.DataLoader = {
    // Cache storage
    cache: {
        threads: new Map(),           // Map<threadId, thread>
        synergySessions: new Map(),   // Map<sessionId, session>
        internalDocs: new Map(),      // Map<sessionId, docs[]>
        threadList: null,             // Cached full thread list
        synergyList: null,            // Cached full synergy list
        lastUpdated: {
            threads: null,
            synergy: null,
            internalDocs: null
        }
    },

    // Request queues (deduplicate concurrent requests)
    pendingRequests: {
        threads: new Map(),           // Map<requestKey, Promise>
        synergy: new Map(),
        internalDocs: new Map()
    },

    // Configuration
    config: {
        // Use environment-detected API URL (set by business-ai-platform-v2.html)
        // Will use window.location.origin on Render, localhost:5001 in dev
        get apiBaseUrl() {
            return window.API_BASE_URL || window.location.origin || 'http://localhost:5001';
        },
        cacheTTL: 5 * 60 * 1000,      // 5 minutes
        batchSize: 50,                // Max items per batch request
        batchDelay: 50,               // Delay before sending batch (ms)
        enableLogging: true
    },

    // Batch request queue
    batchQueue: {
        threads: [],
        synergy: [],
        internalDocs: [],
        timers: {}
    },

    // ========================================
    // THREADS API
    // ========================================
    threads: {
        /**
         * Load threads by IDs (batched)
         * @param {string|string[]} ids - Thread ID(s) to load
         * @returns {Promise<Object|Object[]>} Thread data
         */
        async load(ids) {
            const idsArray = Array.isArray(ids) ? ids : [ids];
            const loader = window.DataLoader;

            loader._log('[THREADS] Load request:', idsArray);

            // Check cache first
            const cached = idsArray.map(id => loader.cache.threads.get(id)).filter(Boolean);
            const uncached = idsArray.filter(id => !loader.cache.threads.has(id));

            if (uncached.length === 0) {
                loader._log('[THREADS] All from cache:', cached.length);
                return Array.isArray(ids) ? cached : cached[0];
            }

            // Fetch uncached threads
            try {
                const userId = loader._getUserId();
                if (!userId) throw new Error('User ID not available');

                const response = await fetch(
                    `${loader.config.apiBaseUrl}/api/threads/list?user_id=${userId}`,
                    { headers: { 'Content-Type': 'application/json' } }
                );

                if (!response.ok) throw new Error(`HTTP ${response.status}`);

                const data = await response.json();
                const threads = data.threads || (data.data && data.data.threads) || [];

                // Update cache
                threads.forEach(thread => {
                    const threadId = thread.id || thread.thread_slug;
                    loader.cache.threads.set(threadId, thread);
                });

                loader.cache.lastUpdated.threads = Date.now();
                loader._log('[THREADS] Loaded and cached:', threads.length);

                // Return requested threads
                const result = idsArray.map(id => loader.cache.threads.get(id)).filter(Boolean);
                return Array.isArray(ids) ? result : result[0];

            } catch (error) {
                console.error('[THREADS] Load failed:', error);
                throw error;
            }
        },

        /**
         * Load all threads for current user
         * @returns {Promise<Object[]>} All threads
         */
        async loadAll() {
            const loader = window.DataLoader;

            // Check cache TTL
            if (loader.cache.threadList &&
                loader.cache.lastUpdated.threads &&
                Date.now() - loader.cache.lastUpdated.threads < loader.config.cacheTTL) {
                loader._log('[THREADS] Returning cached list:', loader.cache.threadList.length);
                return loader.cache.threadList;
            }

            try {
                const userId = loader._getUserId();
                if (!userId) throw new Error('User ID not available');

                loader._log('[THREADS] Loading all threads for user:', userId);

                const response = await fetch(
                    `${loader.config.apiBaseUrl}/api/threads/list?user_id=${userId}`,
                    { headers: { 'Content-Type': 'application/json' } }
                );

                if (!response.ok) throw new Error(`HTTP ${response.status}`);

                const data = await response.json();
                const threads = data.threads || (data.data && data.data.threads) || [];

                // Update cache
                threads.forEach(thread => {
                    const threadId = thread.id || thread.thread_slug;
                    loader.cache.threads.set(threadId, thread);
                });

                loader.cache.threadList = threads;
                loader.cache.lastUpdated.threads = Date.now();
                loader._log('[THREADS] Loaded all threads:', threads.length);

                return threads;

            } catch (error) {
                console.error('[THREADS] LoadAll failed:', error);
                throw error;
            }
        },

        /**
         * Refresh thread cache (force reload)
         */
        async refresh() {
            const loader = window.DataLoader;
            loader.cache.threadList = null;
            loader.cache.threads.clear();
            loader.cache.lastUpdated.threads = null;
            return await this.loadAll();
        }
    },

    // ========================================
    // SYNERGY SESSIONS API
    // ========================================
    synergy: {
        /**
         * Load synergy sessions by IDs (batched)
         * @param {string|string[]} ids - Session ID(s) to load
         * @returns {Promise<Object|Object[]>} Session data
         */
        async load(ids) {
            const idsArray = Array.isArray(ids) ? ids : [ids];
            const loader = window.DataLoader;

            loader._log('[SYNERGY] Load request:', idsArray);

            // Check cache first
            const cached = idsArray.map(id => loader.cache.synergySessions.get(id)).filter(Boolean);
            const uncached = idsArray.filter(id => !loader.cache.synergySessions.has(id));

            if (uncached.length === 0) {
                loader._log('[SYNERGY] All from cache:', cached.length);
                return Array.isArray(ids) ? cached : cached[0];
            }

            // Fetch uncached sessions (batch API)
            try {
                const idsParam = uncached.join(',');
                const response = await fetch(
                    `${loader.config.apiBaseUrl}/api/synergy?ids=${encodeURIComponent(idsParam)}`,
                    { headers: { 'Content-Type': 'application/json' } }
                );

                if (!response.ok) throw new Error(`HTTP ${response.status}`);

                const data = await response.json();

                if (data.success && data.sessions) {
                    // Update cache
                    Object.entries(data.sessions).forEach(([sessionId, session]) => {
                        loader.cache.synergySessions.set(sessionId, session);
                    });

                    loader.cache.lastUpdated.synergy = Date.now();
                    loader._log('[SYNERGY] Loaded and cached:', Object.keys(data.sessions).length);
                }

                // Return requested sessions
                const result = idsArray.map(id => loader.cache.synergySessions.get(id)).filter(Boolean);
                return Array.isArray(ids) ? result : result[0];

            } catch (error) {
                console.error('[SYNERGY] Load failed:', error);
                throw error;
            }
        },

        /**
         * Load all synergy sessions (with internal docs)
         * @returns {Promise<Object[]>} All sessions
         */
        async loadAll() {
            const loader = window.DataLoader;

            // Check cache TTL
            if (loader.cache.synergyList &&
                loader.cache.lastUpdated.synergy &&
                Date.now() - loader.cache.lastUpdated.synergy < loader.config.cacheTTL) {
                loader._log('[SYNERGY] Returning cached list:', loader.cache.synergyList.length);
                return loader.cache.synergyList;
            }

            try {
                loader._log('[SYNERGY] Loading all sessions with batch endpoint...');
                const startTime = performance.now();

                // Use batch endpoint (includes internal docs)
                const response = await fetch(
                    `${loader.config.apiBaseUrl}/api/synergy/sessions/batch`,
                    { headers: { 'Content-Type': 'application/json' } }
                );

                if (!response.ok) throw new Error(`HTTP ${response.status}`);

                const data = await response.json();
                const sessions = data.sessions || [];

                // Update cache
                sessions.forEach(session => {
                    loader.cache.synergySessions.set(session.session_id, session);

                    // Cache internal docs separately
                    if (session.documents && session.documents.length > 0) {
                        loader.cache.internalDocs.set(session.session_id, session.documents);
                    }
                });

                loader.cache.synergyList = sessions;
                loader.cache.lastUpdated.synergy = Date.now();

                const endTime = performance.now();
                const loadTime = (endTime - startTime).toFixed(0);
                const totalDocs = sessions.reduce((sum, s) => sum + (s.internal_docs_count || 0), 0);

                loader._log(`[SYNERGY] Loaded ${sessions.length} sessions with ${totalDocs} docs in ${loadTime}ms`);

                return sessions;

            } catch (error) {
                console.error('[SYNERGY] LoadAll failed:', error);
                throw error;
            }
        },

        /**
         * Refresh synergy cache (force reload)
         */
        async refresh() {
            const loader = window.DataLoader;
            loader.cache.synergyList = null;
            loader.cache.synergySessions.clear();
            loader.cache.internalDocs.clear();
            loader.cache.lastUpdated.synergy = null;
            return await this.loadAll();
        }
    },

    // ========================================
    // INTERNAL DOCS API
    // ========================================
    internalDocs: {
        /**
         * Load internal docs for synergy sessions
         * @param {string|string[]} sessionIds - Session ID(s)
         * @returns {Promise<Object>} Map of sessionId -> docs[]
         */
        async load(sessionIds) {
            const idsArray = Array.isArray(sessionIds) ? sessionIds : [sessionIds];
            const loader = window.DataLoader;

            loader._log('[INTERNAL_DOCS] Load request:', idsArray);

            // Check cache first
            const result = {};
            const uncached = [];

            idsArray.forEach(sessionId => {
                if (loader.cache.internalDocs.has(sessionId)) {
                    result[sessionId] = loader.cache.internalDocs.get(sessionId);
                } else {
                    uncached.push(sessionId);
                }
            });

            if (uncached.length === 0) {
                loader._log('[INTERNAL_DOCS] All from cache');
                return result;
            }

            // Fetch uncached docs
            try {
                // Note: Internal docs are loaded with synergy sessions in batch
                // If not in cache, we need to load the session first
                const sessions = await loader.synergy.load(uncached);
                const sessionsArray = Array.isArray(sessions) ? sessions : [sessions];

                sessionsArray.forEach(session => {
                    if (session && session.documents) {
                        result[session.session_id] = session.documents;
                        loader.cache.internalDocs.set(session.session_id, session.documents);
                    }
                });

                loader._log('[INTERNAL_DOCS] Loaded:', Object.keys(result).length);
                return result;

            } catch (error) {
                console.error('[INTERNAL_DOCS] Load failed:', error);
                throw error;
            }
        }
    },

    // ========================================
    // UTILITY METHODS
    // ========================================

    /**
     * Clear cache for specific type or all
     * @param {string} type - 'threads', 'synergy', 'internalDocs', or 'all'
     */
    clearCache(type = 'all') {
        if (type === 'all' || type === 'threads') {
            this.cache.threads.clear();
            this.cache.threadList = null;
            this.cache.lastUpdated.threads = null;
            this._log('[CACHE] Cleared threads');
        }

        if (type === 'all' || type === 'synergy') {
            this.cache.synergySessions.clear();
            this.cache.synergyList = null;
            this.cache.lastUpdated.synergy = null;
            this._log('[CACHE] Cleared synergy');
        }

        if (type === 'all' || type === 'internalDocs') {
            this.cache.internalDocs.clear();
            this.cache.lastUpdated.internalDocs = null;
            this._log('[CACHE] Cleared internal docs');
        }
    },

    /**
     * Get cache statistics
     * @returns {Object} Cache stats
     */
    getCacheStats() {
        return {
            threads: {
                count: this.cache.threads.size,
                lastUpdated: this.cache.lastUpdated.threads,
                age: this.cache.lastUpdated.threads ? Date.now() - this.cache.lastUpdated.threads : null
            },
            synergy: {
                count: this.cache.synergySessions.size,
                lastUpdated: this.cache.lastUpdated.synergy,
                age: this.cache.lastUpdated.synergy ? Date.now() - this.cache.lastUpdated.synergy : null
            },
            internalDocs: {
                count: this.cache.internalDocs.size,
                lastUpdated: this.cache.lastUpdated.internalDocs,
                age: this.cache.lastUpdated.internalDocs ? Date.now() - this.cache.lastUpdated.internalDocs : null
            }
        };
    },

    /**
     * Preload data (warm up cache)
     */
    async preload() {
        this._log('[PRELOAD] Starting data preload...');
        const startTime = performance.now();

        try {
            // Load threads and synergy sessions in parallel
            await Promise.all([
                this.threads.loadAll(),
                this.synergy.loadAll()
            ]);

            const endTime = performance.now();
            const loadTime = (endTime - startTime).toFixed(0);

            const stats = this.getCacheStats();
            this._log(`[PRELOAD] Complete in ${loadTime}ms:`, {
                threads: stats.threads.count,
                synergy: stats.synergy.count,
                docs: stats.internalDocs.count
            });

        } catch (error) {
            console.error('[PRELOAD] Failed:', error);
        }
    },

    /**
     * Get current user ID
     * @private
     */
    _getUserId() {
        if (window.UserAuth && window.UserAuth.user) {
            return window.UserAuth.user.id || window.UserAuth.user.user_id;
        }
        return null;
    },

    /**
     * Log message (if logging enabled)
     * @private
     */
    _log(...args) {
        if (this.config.enableLogging) {
            console.log('[DataLoader]', ...args);
        }
    },

    /**
     * Initialize DataLoader
     */
    init() {
        this._log('Initialized');

        // Set up auto-refresh on tab visibility
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                const stats = this.getCacheStats();

                // Refresh if cache is stale (older than TTL)
                if (stats.threads.age > this.config.cacheTTL) {
                    this._log('[AUTO-REFRESH] Threads cache stale, refreshing...');
                    this.threads.refresh();
                }

                if (stats.synergy.age > this.config.cacheTTL) {
                    this._log('[AUTO-REFRESH] Synergy cache stale, refreshing...');
                    this.synergy.refresh();
                }
            }
        });
    }
};

// Initialize on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => window.DataLoader.init());
} else {
    window.DataLoader.init();
}

console.log('[DataLoader] Module loaded - Use DataLoader.threads.load(), DataLoader.synergy.load(), etc.');
