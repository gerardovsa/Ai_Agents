/**
 * Token Count Polling System
 * 
 * FILE: UI/token_polling.js
 * PURPOSE: Poll backend for thread token counts and update UI
 * 
 * USAGE:
 *   TokenPoller.startPolling(threadId) - Start polling for a thread
 *   TokenPoller.stopPolling() - Stop current polling
 *   TokenPoller.updateOnce(threadId) - Update immediately (one-time)
 * 
 * INTEGRATION:
 *   Include in business-ai-platform-v2.html after ThreadManager definition
 *   Calls ThreadManager.updateTokenCount() to update UI
 * 
 * NOTES:
 *   - Polls every 10 seconds by default
 *   - Automatically stops when no thread active
 *   - Uses fetch API with error handling
 * 
 * LAST MODIFIED: 2025-11-14 - Initial implementation
 */

const TokenPoller = {
    intervalId: null,
    currentThreadId: null,
    pollInterval: 10000, // 10 seconds

    /**
     * Start polling for token counts
     * @param {string} threadId - Thread ID to poll
     * @param {number} interval - Polling interval in ms (default: 10000)
     */
    startPolling(threadId, interval = null) {
        // Stop existing poll
        this.stopPolling();

        if (!threadId) {
            console.warn('[TokenPoller] No thread ID provided, not starting poll');
            return;
        }

        this.currentThreadId = threadId;
        if (interval) this.pollInterval = interval;

        console.log(`[TokenPoller] Starting poll for thread ${threadId} (every ${this.pollInterval}ms)`);

        // Initial update
        this.updateOnce(threadId);

        // Start interval
        this.intervalId = setInterval(() => {
            this.updateOnce(this.currentThreadId);
        }, this.pollInterval);
    },

    /**
     * Stop polling
     */
    stopPolling() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
            console.log(`[TokenPoller] Stopped polling`);
        }
        this.currentThreadId = null;
    },

    /**
     * Update token count once (no polling)
     * @param {string} threadId - Thread ID to fetch count for
     */
    async updateOnce(threadId) {
        if (!threadId) {
            console.warn('[TokenPoller] No thread ID for update');
            return;
        }

        try {
            const apiBase = window.API_BASE_URL || 'http://localhost:5001';
            const response = await fetch(`${apiBase}/api/tokens/${threadId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                console.warn(`[TokenPoller] API returned ${response.status} for thread ${threadId}`);
                return;
            }

            const data = await response.json();

            if (data.success && typeof data.token_count !== 'undefined') {
                // Update UI via ThreadManager
                if (typeof ThreadManager !== 'undefined' && ThreadManager.updateTokenCount) {
                    ThreadManager.updateTokenCount(threadId, data.token_count);
                    console.log(`[TokenPoller] Updated thread ${threadId}: ${data.token_count} tokens (${data.status})`);
                } else {
                    console.warn('[TokenPoller] ThreadManager.updateTokenCount() not available');
                }
            }

        } catch (error) {
            console.error('[TokenPoller] Error fetching token count:', error);
        }
    },

    /**
     * Force backend update (push new token count to server)
     * @param {string} threadId - Thread ID
     * @param {number} tokenCount - New token count
     */
    async pushUpdate(threadId, tokenCount) {
        if (!threadId || typeof tokenCount === 'undefined') {
            console.warn('[TokenPoller] Missing threadId or tokenCount for push update');
            return false;
        }

        try {
            const apiBase = window.API_BASE_URL || 'http://localhost:5001';
            const response = await fetch(`${apiBase}/api/tokens/${threadId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ token_count: tokenCount })
            });

            if (!response.ok) {
                console.error(`[TokenPoller] Failed to push update: ${response.status}`);
                return false;
            }

            const data = await response.json();
            console.log(`[TokenPoller] Pushed token count to server: ${tokenCount}`);
            return data.success;

        } catch (error) {
            console.error('[TokenPoller] Error pushing token count:', error);
            return false;
        }
    }
};

// Auto-start polling when thread changes (if ThreadManager exists)
if (typeof ThreadManager !== 'undefined') {
    const originalSwitchThread = ThreadManager.switchThread;

    ThreadManager.switchThread = function (threadId, ...args) {
        // Call original method
        const result = originalSwitchThread.call(this, threadId, ...args);

        // Start token polling for new thread
        if (threadId) {
            TokenPoller.startPolling(threadId);
        } else {
            TokenPoller.stopPolling();
        }

        return result;
    };

    console.log('[TokenPoller] Auto-poll integration with ThreadManager enabled');
}

// Export for global access
window.TokenPoller = TokenPoller;
