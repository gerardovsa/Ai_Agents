/**
 * FILE: UI/modules/onboarding/onboarding-api.js
 * PURPOSE: API wrapper for onboarding backend endpoints
 * 
 * DEPENDENCIES:
 * - fetch API (browser native)
 * - JWT token in sessionStorage
 * 
 * EXPORTS:
 * - OnboardingAPI class with methods for all onboarding endpoints
 * 
 * NOTES:
 * - All requests include authentication token
 * - Handles errors gracefully
 * - Returns consistent response format
 * 
 * LAST MODIFIED: 2025-11-29 - Initial creation
 */

class OnboardingAPI {
    constructor() {
        this.baseUrl = '/api/onboarding';
        this.token = this.getAuthToken();
    }

    /**
     * Get authentication token from sessionStorage
     */
    getAuthToken() {
        return sessionStorage.getItem('auth_token') || localStorage.getItem('auth_token');
    }

    /**
     * Make authenticated API request
     */
    async request(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // Add auth token if available
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                ...options,
                headers
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error(`❌ [OnboardingAPI] Request failed: ${endpoint}`, error);
            throw error;
        }
    }

    /**
     * Get user's onboarding status
     */
    async getStatus() {
        return await this.request('/status', {
            method: 'GET'
        });
    }

    /**
     * Mark First-Run Experience as completed
     * @param {boolean} skipped - Whether user skipped FRE
     */
    async completeFRE(skipped = false) {
        return await this.request('/complete-fre', {
            method: 'POST',
            body: JSON.stringify({ skipped })
        });
    }

    /**
     * Mark checklist step as completed
     * @param {string} stepId - Step ID (e.g., 'create_thread')
     * @param {number} xp - XP to award
     */
    async completeStep(stepId, xp = 0) {
        return await this.request('/complete-step', {
            method: 'POST',
            body: JSON.stringify({ step_id: stepId, xp })
        });
    }

    /**
     * Mark tour as completed
     * @param {string} tourId - Tour ID (e.g., 'basics')
     */
    async completeTour(tourId) {
        return await this.request('/complete-tour', {
            method: 'POST',
            body: JSON.stringify({ tour_id: tourId })
        });
    }

    /**
     * Mark learning module as completed
     * @param {string} moduleId - Module ID
     * @param {number} score - Quiz score (0-100)
     */
    async completeModule(moduleId, score = 0) {
        return await this.request('/complete-module', {
            method: 'POST',
            body: JSON.stringify({ module_id: moduleId, score })
        });
    }

    /**
     * Dismiss onboarding checklist
     */
    async dismiss() {
        return await this.request('/dismiss', {
            method: 'POST'
        });
    }

    /**
     * Mark user as activated
     * @param {string} method - Activation method ('checklist_completed', 'tour_completed', 'manual')
     */
    async activateUser(method = 'manual') {
        return await this.request('/activate-user', {
            method: 'POST',
            body: JSON.stringify({ activation_method: method })
        });
    }

    /**
     * Get onboarding analytics (admin only)
     */
    async getAnalytics() {
        return await this.request('/analytics', {
            method: 'GET'
        });
    }
}

// Create global instance
window.OnboardingAPI = new OnboardingAPI();

console.log('✅ Onboarding API module loaded');
