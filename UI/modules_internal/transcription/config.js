/**
 * FILE: UI/modules/transcription/config.js
 * PURPOSE: Centralized configuration for transcription module
 * 
 * ARCHITECTURE:
 * - Auto-detects environment (local vs production)
 * - Provides dynamic API endpoint resolution
 * - No hardcoded URLs - all configuration centralized here
 * 
 * USAGE:
 *   import { TranscriptionConfig } from './config.js';
 *   const endpoint = TranscriptionConfig.getEndpoint('transcribe');
 * 
 * ENVIRONMENT DETECTION:
 * - localhost:* → Local development (port 5001)
 * - render.com → Production Render backend
 * - Custom → User can override via localStorage
 * 
 * LAST MODIFIED: 2025-11-26 - Created centralized config system
 */

class TranscriptionConfig {
    constructor() {
        // ✅ Use existing global API_BASE_URL (set in business-ai-platform-v2.html)
        // This provides automatic local/Render detection consistent with other modules
        this.globalApiBaseUrl = window.API_BASE_URL || 'http://localhost:5001';
        
        // API endpoints (relative paths)
        this.endpoints = {
            transcribe: '/api/transcribe',
            systemCheck: '/api/system/check',
            transcribeV1: '/api/v1/transcribe', // Legacy endpoint
            systemCheckV1: '/api/v1/system/check' // Legacy endpoint
        };
        
        console.log('[Transcription Config] Using global API_BASE_URL:', this.globalApiBaseUrl);
        
        // Load custom configuration from localStorage
        this.loadCustomConfig();
    }
    
    /**
     * Get the base URL for API requests
     * Priority: localStorage override > global API_BASE_URL
     */
    getBaseUrl() {
        // Check for user override in localStorage
        const customUrl = localStorage.getItem('transcription-backend-url');
        if (customUrl) {
            console.log('[Transcription Config] Using custom backend URL:', customUrl);
            return customUrl;
        }
        
        // Use global API_BASE_URL (already detects local vs Render)
        console.log('[Transcription Config] Using global API_BASE_URL:', this.globalApiBaseUrl);
        return this.globalApiBaseUrl;
    }
    
    /**
     * Get full endpoint URL
     * @param {string} endpointKey - Key from this.endpoints object
     * @returns {string} Full URL (e.g., "http://localhost:5001/api/transcribe")
     */
    getEndpoint(endpointKey) {
        const baseUrl = this.getBaseUrl();
        const path = this.endpoints[endpointKey];
        
        if (!path) {
            console.error('[Transcription Config] Unknown endpoint key:', endpointKey);
            return baseUrl + this.endpoints.transcribe; // Fallback to default
        }
        
        return baseUrl + path;
    }
    
    /**
     * Load custom configuration from localStorage
     */
    loadCustomConfig() {
        try {
            const customEndpoints = localStorage.getItem('transcription-custom-endpoints');
            if (customEndpoints) {
                const parsed = JSON.parse(customEndpoints);
                Object.assign(this.endpoints, parsed);
                console.log('[Transcription Config] Loaded custom endpoints:', parsed);
            }
        } catch (error) {
            console.error('[Transcription Config] Failed to load custom config:', error);
        }
    }
    
    /**
     * Set custom backend URL (stored in localStorage)
     * @param {string} url - Custom backend URL (e.g., "https://my-backend.onrender.com")
     */
    setCustomBackendUrl(url) {
        if (!url) {
            localStorage.removeItem('transcription-backend-url');
            console.log('[Transcription Config] Removed custom backend URL');
        } else {
            // Validate URL format
            try {
                new URL(url);
                localStorage.setItem('transcription-backend-url', url);
                console.log('[Transcription Config] Set custom backend URL:', url);
            } catch (error) {
                console.error('[Transcription Config] Invalid URL format:', url);
                throw new Error('Invalid URL format');
            }
        }
    }
    
    /**
     * Get all current configuration
     */
    getConfig() {
        const isLocal = this.globalApiBaseUrl.includes('localhost') || 
                        this.globalApiBaseUrl.includes('127.0.0.1');
        
        return {
            environment: isLocal ? 'local' : 'production',
            baseUrl: this.getBaseUrl(),
            globalApiBaseUrl: this.globalApiBaseUrl,
            endpoints: this.endpoints,
            customUrl: localStorage.getItem('transcription-backend-url')
        };
    }
    
    /**
     * Reset to default configuration
     */
    reset() {
        localStorage.removeItem('transcription-backend-url');
        localStorage.removeItem('transcription-custom-endpoints');
        console.log('[Transcription Config] Reset to defaults');
    }
    
    /**
     * Test backend connection
     * @returns {Promise<boolean>} True if backend is reachable
     */
    async testConnection() {
        const endpoint = this.getEndpoint('systemCheck');
        console.log('[Transcription Config] Testing connection to:', endpoint);
        
        try {
            const response = await fetch(endpoint, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                console.log('[Transcription Config] ✅ Backend is reachable');
                return true;
            } else {
                console.warn('[Transcription Config] ⚠️ Backend returned:', response.status);
                return false;
            }
        } catch (error) {
            console.error('[Transcription Config] ❌ Backend unreachable:', error.message);
            return false;
        }
    }
}

// Export singleton instance
window.TranscriptionConfig = new TranscriptionConfig();

// Expose configuration to global scope for debugging
window.getTranscriptionConfig = () => window.TranscriptionConfig.getConfig();
window.setTranscriptionBackend = (url) => window.TranscriptionConfig.setCustomBackendUrl(url);
window.testTranscriptionBackend = () => window.TranscriptionConfig.testConnection();

const isLocal = window.API_BASE_URL ? 
    (window.API_BASE_URL.includes('localhost') || window.API_BASE_URL.includes('127.0.0.1')) : 
    true;

console.log('[Transcription Config] ✅ Initialized');
console.log('[Transcription Config] 🌐 Using global API_BASE_URL:', window.API_BASE_URL);
console.log('[Transcription Config] 📍 Environment:', isLocal ? '🔧 LOCAL (localhost:5001)' : '🚀 PRODUCTION (Render)');
console.log('[Transcription Config] 🔗 Transcribe endpoint:', window.TranscriptionConfig.getEndpoint('transcribe'));
console.log('[Transcription Config] 💡 Available commands:');
console.log('  - getTranscriptionConfig() - View current config');
console.log('  - setTranscriptionBackend("https://your-backend.com") - Set custom URL');
console.log('  - testTranscriptionBackend() - Test backend connection');
