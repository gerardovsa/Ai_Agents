/**
 * FILE: UI/js/tabulator-network-utils.js
 * PURPOSE: Network utilities with retry logic and timeout handling
 * 
 * FEATURES:
 * - Automatic retry with exponential backoff
 * - Configurable timeout
 * - Request cancellation
 * - Error handling
 * 
 * EXPORTS:
 * - NetworkHelper class
 * 
 * LAST MODIFIED: 2025-11-07 - Initial creation
 */

class NetworkHelper {
    /**
     * Fetch with retry logic and timeout
     * @param {string} url - URL to fetch
     * @param {Object} options - Fetch options
     * @param {Object} config - Retry configuration
     * @returns {Promise<Response>}
     */
    static async fetchWithRetry(url, options = {}, config = {}) {
        const {
            retries = 3,
            timeout = 30000,
            backoffMultiplier = 2,
            initialDelay = 1000
        } = config;

        let lastError;

        for (let attempt = 0; attempt < retries; attempt++) {
            try {
                const response = await this.fetchWithTimeout(url, options, timeout);

                // If successful, return response
                if (response.ok) {
                    return response;
                }

                // If 4xx error (client error), don't retry
                if (response.status >= 400 && response.status < 500) {
                    throw new Error(`Client error: ${response.status} ${response.statusText}`);
                }

                // For 5xx errors, retry
                lastError = new Error(`Server error: ${response.status} ${response.statusText}`);

            } catch (error) {
                lastError = error;

                // If it's a client error or last attempt, throw
                if (error.message.includes('Client error') || attempt === retries - 1) {
                    throw error;
                }

                // Wait before retrying (exponential backoff)
                const delay = initialDelay * Math.pow(backoffMultiplier, attempt);
                console.log(`[Network] Retry ${attempt + 1}/${retries} after ${delay}ms delay`);
                await this.sleep(delay);
            }
        }

        throw lastError;
    }

    /**
     * Fetch with timeout
     */
    static async fetchWithTimeout(url, options = {}, timeout = 30000) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error(`Request timeout after ${timeout}ms`);
            }
            throw error;
        }
    }

    /**
     * POST with retry
     */
    static async post(url, data, config = {}) {
        return this.fetchWithRetry(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...config.headers
            },
            body: JSON.stringify(data)
        }, config);
    }

    /**
     * GET with retry
     */
    static async get(url, config = {}) {
        return this.fetchWithRetry(url, {
            method: 'GET',
            headers: config.headers || {}
        }, config);
    }

    /**
     * PUT with retry
     */
    static async put(url, data, config = {}) {
        return this.fetchWithRetry(url, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                ...config.headers
            },
            body: JSON.stringify(data)
        }, config);
    }

    /**
     * DELETE with retry
     */
    static async delete(url, config = {}) {
        return this.fetchWithRetry(url, {
            method: 'DELETE',
            headers: config.headers || {}
        }, config);
    }

    /**
     * Sleep utility
     */
    static sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Check if error is network-related
     */
    static isNetworkError(error) {
        return error.message.includes('timeout') ||
            error.message.includes('network') ||
            error.message.includes('Failed to fetch');
    }
}

// Export to window
window.NetworkHelper = NetworkHelper;

console.log('[Network Helper] Loaded and ready');
