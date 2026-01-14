/**
 * Backend Health Check Module
 * Prevents 502 errors by verifying backend availability before API calls
 * 
 * Usage:
 *   await BackendHealthCheck.waitForBackend();
 *   // Now safe to make API calls
 */

const BackendHealthCheck = {
    healthEndpoint: '/api/health',
    maxRetries: 10,
    retryDelay: 2000, // 2 seconds
    timeout: 5000, // 5 second timeout per request
    isHealthy: false,

    /**
     * Check if backend is responding
     */
    async checkHealth() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);

            const response = await fetch(this.healthEndpoint, {
                method: 'GET',
                signal: controller.signal,
                headers: {
                    'Accept': 'application/json'
                }
            });

            clearTimeout(timeoutId);

            if (response.ok) {
                const data = await response.json();
                this.isHealthy = data.status === 'healthy';
                return this.isHealthy;
            }

            return false;
        } catch (error) {
            if (error.name === 'AbortError') {
                console.warn('⏱️ [Health Check] Backend health check timed out');
            } else {
                console.warn('❌ [Health Check] Backend unavailable:', error.message);
            }
            this.isHealthy = false;
            return false;
        }
    },

    /**
     * Wait for backend to become available (with retries)
     */
    async waitForBackend(onRetry = null) {
        console.log('🔍 [Health Check] Checking backend availability...');

        for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
            const healthy = await this.checkHealth();

            if (healthy) {
                console.log('✅ [Health Check] Backend is healthy and ready');
                return true;
            }

            if (attempt < this.maxRetries) {
                console.log(`🔄 [Health Check] Retry ${attempt}/${this.maxRetries} - Backend not ready, waiting ${this.retryDelay}ms...`);

                if (onRetry) {
                    onRetry(attempt, this.maxRetries);
                }

                await new Promise(resolve => setTimeout(resolve, this.retryDelay));
            }
        }

        console.error('❌ [Health Check] Backend failed to become available after max retries');
        return false;
    },

    /**
     * Wrap API fetch with automatic retry on 502
     */
    async fetchWithRetry(url, options = {}, maxRetries = 3) {
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                const response = await fetch(url, options);

                // If 502, wait and retry
                if (response.status === 502) {
                    console.warn(`⚠️ [Fetch Retry] Got 502 from ${url}, attempt ${attempt}/${maxRetries}`);

                    if (attempt < maxRetries) {
                        await new Promise(resolve => setTimeout(resolve, this.retryDelay));
                        continue;
                    }
                }

                // Return response (even if error status like 404, 500)
                return response;

            } catch (error) {
                console.error(`❌ [Fetch Retry] Request failed (attempt ${attempt}/${maxRetries}):`, error);

                if (attempt < maxRetries) {
                    await new Promise(resolve => setTimeout(resolve, this.retryDelay));
                } else {
                    throw error;
                }
            }
        }
    },

    /**
     * Safe JSON parse with error handling for HTML responses
     */
    async safeJsonParse(response) {
        const contentType = response.headers.get('content-type');

        if (!contentType || !contentType.includes('application/json')) {
            console.error('❌ [JSON Parse] Response is not JSON:', contentType);
            const text = await response.text();
            console.error('Response body:', text.substring(0, 200));
            throw new Error(`Expected JSON but received ${contentType}`);
        }

        try {
            return await response.json();
        } catch (error) {
            console.error('❌ [JSON Parse] Failed to parse JSON:', error);
            const text = await response.text();
            console.error('Response body:', text.substring(0, 200));
            throw new Error('Invalid JSON response from server');
        }
    }
};

// Make globally available
window.BackendHealthCheck = BackendHealthCheck;
