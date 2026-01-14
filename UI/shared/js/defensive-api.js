/**
 * Defensive API Call Wrappers
 * Adds retry logic and error handling to critical API endpoints
 */

const DefensiveAPI = {
    /**
     * Wrapper for /api/auth/team-ids with retry and fallback
     */
    async loadTeamIds(options = {}) {
        const {
            retries = 3,
            fallback = []
        } = options;

        if (!window.BackendHealthCheck) {
            console.warn('⚠️ [Defensive API] BackendHealthCheck not available');
        }

        try {
            const token = localStorage.getItem('authToken');
            if (!token) {
                console.warn('⚠️ [Defensive API] No auth token - returning empty Team IDs');
                return { success: true, data: { team_ids: fallback } };
            }

            const fetchFn = window.BackendHealthCheck?.fetchWithRetry || fetch;
            const response = await fetchFn('/api/auth/team-ids', {
                headers: { 'Authorization': `Bearer ${token}` }
            }, retries);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const safeParse = window.BackendHealthCheck?.safeJsonParse;
            const data = safeParse
                ? await safeParse(response)
                : await response.json();

            return { success: true, data };

        } catch (error) {
            console.error('❌ [Defensive API] loadTeamIds failed:', error);
            console.warn(`⚠️ [Defensive API] Using fallback (empty Team IDs list)`);
            return { success: false, data: { team_ids: fallback }, error: error.message };
        }
    },

    /**
     * Wrapper for /api/auth/profile with retry and fallback
     */
    async loadProfile(options = {}) {
        const {
            retries = 3,
            fallback = null
        } = options;

        try {
            const token = localStorage.getItem('authToken');
            if (!token) {
                console.warn('⚠️ [Defensive API] No auth token - returning null profile');
                return { success: false, data: fallback };
            }

            const fetchFn = window.BackendHealthCheck?.fetchWithRetry || fetch;
            const response = await fetchFn('/api/auth/profile', {
                headers: { 'Authorization': `Bearer ${token}` }
            }, retries);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const safeParse = window.BackendHealthCheck?.safeJsonParse;
            const data = safeParse
                ? await safeParse(response)
                : await response.json();

            return { success: true, data };

        } catch (error) {
            console.error('❌ [Defensive API] loadProfile failed:', error);
            return { success: false, data: fallback, error: error.message };
        }
    },

    /**
     * Wrapper for /api/modules/list with retry and graceful degradation
     */
    async loadModules(options = {}) {
        const {
            retries = 3,
            fallback = { modules: [], count: 0 }
        } = options;

        try {
            const fetchFn = window.BackendHealthCheck?.fetchWithRetry || fetch;
            const response = await fetchFn('/api/modules/list', {}, retries);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const safeParse = window.BackendHealthCheck?.safeJsonParse;
            const data = safeParse
                ? await safeParse(response)
                : await response.json();

            return { success: true, data };

        } catch (error) {
            console.error('❌ [Defensive API] loadModules failed:', error);
            console.warn('⚠️ [Defensive API] App will run without external modules');
            return { success: false, data: fallback, error: error.message };
        }
    },

    /**
     * Generic wrapper for any API call
     */
    async fetchWithRetry(url, options = {}, config = {}) {
        const {
            retries = 3,
            fallback = null,
            throwOnError = false
        } = config;

        try {
            const fetchFn = window.BackendHealthCheck?.fetchWithRetry || fetch;
            const response = await fetchFn(url, options, retries);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType?.includes('application/json')) {
                const safeParse = window.BackendHealthCheck?.safeJsonParse;
                const data = safeParse
                    ? await safeParse(response)
                    : await response.json();
                return { success: true, data };
            }

            const text = await response.text();
            return { success: true, data: text };

        } catch (error) {
            console.error(`❌ [Defensive API] ${url} failed:`, error);

            if (throwOnError) {
                throw error;
            }

            return { success: false, data: fallback, error: error.message };
        }
    }
};

// Make globally available
window.DefensiveAPI = DefensiveAPI;
