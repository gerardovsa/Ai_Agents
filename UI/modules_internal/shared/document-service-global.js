/**
 * FILE: UI/modules_internal/shared/document-service-global.js
 * PURPOSE: Non-module version of DocumentService for global window scope
 * 
 * This is a wrapper around document-service.js that makes it available
 * globally without requiring ES6 module imports.
 * 
 * CREATED: December 23, 2025
 */

(function () {
    'use strict';

    class DocumentService {
        constructor(apiBaseUrl = window.API_BASE_URL || window.location.origin) {
            this.apiBaseUrl = apiBaseUrl;
            this.cache = new Map(); // Simple in-memory cache
            this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
        }

        /**
         * Fetch single document by ID
         * @param {string} docId - Document ID
         * @param {Object} options - Options { skipCache, includeContent }
         * @returns {Promise<Object>} Document data
         */
        async fetchDocument(docId, options = {}) {
            const { skipCache = false, includeContent = true } = options;

            // Check cache first
            if (!skipCache && this.cache.has(docId)) {
                const cached = this.cache.get(docId);
                if (Date.now() - cached.timestamp < this.cacheTimeout) {
                    console.log(`[DocumentService] Cache hit for ${docId}`);
                    return cached.data;
                }
            }

            try {
                console.log(`[DocumentService] Fetching document: ${docId}`);

                const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/${docId}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();

                // Cache the result
                this.cache.set(docId, {
                    data: data,
                    timestamp: Date.now()
                });

                return data;
            } catch (error) {
                console.error(`[DocumentService] Error fetching document ${docId}:`, error);
                throw error;
            }
        }

        /**
         * Fetch multiple documents in batch
         * @param {Array<string>} docIds - Array of document IDs
         * @param {Object} options - Options { skipCache, includeContent }
         * @returns {Promise<Array<Object>>} Array of document data
         */
        async fetchDocumentsBatch(docIds, options = {}) {
            console.log(`[DocumentService] Fetching ${docIds.length} documents in batch`);

            try {
                const promises = docIds.map(docId => this.fetchDocument(docId, options));
                const results = await Promise.allSettled(promises);

                return results.map((result, index) => {
                    if (result.status === 'fulfilled') {
                        return result.value;
                    } else {
                        console.error(`[DocumentService] Failed to fetch ${docIds[index]}:`, result.reason);
                        return null;
                    }
                }).filter(doc => doc !== null);
            } catch (error) {
                console.error('[DocumentService] Batch fetch error:', error);
                return [];
            }
        }

        /**
         * Fetch sessions batch (simplified for Synergy)
         * @returns {Promise<Object>} Sessions data
         */
        async fetchSessionsBatch() {
            try {
                console.log('[DocumentService] Fetching sessions batch');

                const response = await fetch(`${this.apiBaseUrl}/api/synergy/sessions`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                return await response.json();
            } catch (error) {
                console.error('[DocumentService] Error fetching sessions:', error);
                throw error;
            }
        }

        /**
         * Clear cache for specific document
         * @param {string} docId - Document ID
         */
        clearCache(docId) {
            if (docId) {
                this.cache.delete(docId);
                console.log(`[DocumentService] Cleared cache for ${docId}`);
            } else {
                this.cache.clear();
                console.log('[DocumentService] Cleared all cache');
            }
        }

        /**
         * Clear cache entries for a session (by pattern matching)
         * @param {string} sessionId - Session ID
         */
        clearSessionCache(sessionId) {
            let removedCount = 0;
            for (const [key] of this.cache.entries()) {
                if (key.includes(sessionId)) {
                    this.cache.delete(key);
                    removedCount++;
                }
            }

            console.log(`[DocumentService] Removed ${removedCount} cached entries for session ${sessionId}`);
        }
    }

    // Create singleton instance and expose globally
    window.documentService = new DocumentService();
    window.DocumentService = DocumentService; // Also expose class for new instances

    console.log('✅ [DocumentService] Loaded globally as window.documentService');

})();
