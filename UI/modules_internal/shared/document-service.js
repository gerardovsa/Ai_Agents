/**
 * FILE: UI/modules_internal/shared/document-service.js
 * PURPOSE: Shared utility for internal document operations
 * 
 * FEATURES:
 * - Centralized document fetching logic
 * - Standardized error handling
 * - Consistent data formatting
 * - Single source of truth for document operations
 * 
 * USAGE:
 * import { DocumentService } from './shared/document-service.js';
 * const docService = new DocumentService();
 * const doc = await docService.fetchDocument(docId);
 * 
 * CREATED: December 21, 2025
 * LAST MODIFIED: December 21, 2025
 */

export class DocumentService {
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
                },
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            const doc = data.document || data;

            // Cache the result
            this.cache.set(docId, {
                data: doc,
                timestamp: Date.now()
            });

            return doc;

        } catch (error) {
            console.error(`[DocumentService] Error fetching document ${docId}:`, error);
            throw new Error(`Failed to fetch document: ${error.message}`);
        }
    }

    /**
     * Fetch documents for a synergy session
     * @param {string} sessionId - Synergy session ID
     * @returns {Promise<Array>} Array of documents
     */
    async fetchSessionDocuments(sessionId) {
        try {
            console.log(`[DocumentService] Fetching documents for session: ${sessionId}`);

            const response = await fetch(`${this.apiBaseUrl}/api/synergy/sessions/${sessionId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            const session = data.session || data;
            return session.internal_docs || [];

        } catch (error) {
            console.error(`[DocumentService] Error fetching session documents:`, error);
            throw new Error(`Failed to fetch session documents: ${error.message}`);
        }
    }

    /**
     * Download document
     * @param {string} docId - Document ID
     * @param {string} filename - Filename for download
     * @returns {Promise<void>}
     */
    async downloadDocument(docId, filename) {
        try {
            console.log(`[DocumentService] Downloading document: ${docId}`);

            const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-docs/${docId}/download`, {
                method: 'GET',
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename || `document-${docId}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            console.log(`[DocumentService] Download complete: ${filename}`);

        } catch (error) {
            console.error(`[DocumentService] Error downloading document:`, error);
            throw new Error(`Failed to download document: ${error.message}`);
        }
    }

    /**
     * Create new document
     * @param {Object} docData - Document data
     * @returns {Promise<Object>} Created document
     */
    async createDocument(docData) {
        try {
            console.log(`[DocumentService] Creating document:`, docData.title);

            const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify(docData)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return data.document || data;

        } catch (error) {
            console.error(`[DocumentService] Error creating document:`, error);
            throw new Error(`Failed to create document: ${error.message}`);
        }
    }

    /**
     * Update existing document
     * @param {string} docId - Document ID
     * @param {Object} updates - Fields to update
     * @returns {Promise<Object>} Updated document
     */
    async updateDocument(docId, updates) {
        try {
            console.log(`[DocumentService] Updating document: ${docId}`);

            const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/${docId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify(updates)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            // Invalidate cache
            this.cache.delete(docId);

            return data.document || data;

        } catch (error) {
            console.error(`[DocumentService] Error updating document:`, error);
            throw new Error(`Failed to update document: ${error.message}`);
        }
    }

    /**
     * Delete document
     * @param {string} docId - Document ID
     * @returns {Promise<void>}
     */
    async deleteDocument(docId) {
        try {
            console.log(`[DocumentService] Deleting document: ${docId}`);

            const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/${docId}`, {
                method: 'DELETE',
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            // Invalidate cache
            this.cache.delete(docId);

        } catch (error) {
            console.error(`[DocumentService] Error deleting document:`, error);
            throw new Error(`Failed to delete document: ${error.message}`);
        }
    }

    /**
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
        console.log('[DocumentService] Cache cleared');
    }

    /**
     * Get cache stats
     * @returns {Object} Cache statistics
     */
    getCacheStats() {
        return {
            size: this.cache.size,
            keys: Array.from(this.cache.keys())
        };
    }

    /**
     * Fetch multiple sessions with counts (batch operation)
     * @param {Array<string>|null} sessionIds - Optional array of session IDs to fetch
     * @returns {Promise<Array>} Array of session objects with document counts
     */
    async fetchSessionsBatch(sessionIds = null) {
        try {
            const url = sessionIds && sessionIds.length > 0
                ? `${this.apiBaseUrl}/api/synergy/sessions/batch?ids=${sessionIds.join(',')}`
                : `${this.apiBaseUrl}/api/synergy/sessions/batch`;

            console.log(`[DocumentService] Fetching sessions batch${sessionIds ? ` (${sessionIds.length} IDs)` : ''}`);

            const response = await fetch(url, {
                method: 'GET',
                credentials: 'include'
            });

            if (!response.ok) {
                // Fallback to non-batch endpoint
                console.log('[DocumentService] Batch endpoint failed, trying fallback');
                const fallbackResponse = await fetch(`${this.apiBaseUrl}/api/synergy/sessions`, {
                    method: 'GET',
                    credentials: 'include'
                });

                if (!fallbackResponse.ok) {
                    throw new Error(`Failed to fetch sessions: ${fallbackResponse.status}`);
                }

                return await fallbackResponse.json();
            }

            return await response.json();
        } catch (error) {
            console.error('[DocumentService] Error fetching sessions batch:', error);
            throw error;
        }
    }

    /**
     * Fetch all documents with optional filters
     * @param {Object} filters - Filter parameters (session_id, doc_type, etc.)
     * @returns {Promise<Array>} Array of document objects
     */
    async fetchAllDocuments(filters = {}) {
        try {
            const params = new URLSearchParams();
            Object.entries(filters).forEach(([key, value]) => {
                if (value !== null && value !== undefined) {
                    params.append(key, value);
                }
            });

            const url = `${this.apiBaseUrl}/api/synergy/internal-docs/list${params.toString() ? '?' + params.toString() : ''}`;

            console.log(`[DocumentService] Fetching all documents${params.toString() ? ` with filters: ${params.toString()}` : ''}`);

            const response = await fetch(url, {
                method: 'GET',
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`Failed to fetch documents: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('[DocumentService] Error fetching all documents:', error);
            throw error;
        }
    }

    /**
     * Invalidate cache for specific session
     * Removes all cached entries related to the session
     * @param {string} sessionId - Session ID to invalidate
     */
    invalidateSession(sessionId) {
        console.log(`[DocumentService] Invalidating cache for session: ${sessionId}`);

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

// Export singleton instance
export const documentService = new DocumentService();
