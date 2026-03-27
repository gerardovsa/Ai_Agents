/**
 * FILE: UI/shared/js/module-api.js
 * PURPOSE: Shared auth-aware API client for all V4 modules
 * ARCHITECTURE: ES Module — import with `import { ModuleAPI } from '../../shared/js/module-api.js'`
 *
 * USAGE:
 *   import { ModuleAPI } from '../../shared/js/module-api.js';
 *   const api = new ModuleAPI({ moduleId: 'xero' });
 *   const data = await api.get('/api/xero/dashboard');
 *
 * AUTH:
 *   Reads localStorage.getItem('authToken') automatically on every request.
 *   On 401, emits window event 'module:auth-expired' so the app can handle
 *   session expiry (show login prompt, redirect, etc.) without each module
 *   duplicating that logic.
 *
 * ERROR HANDLING:
 *   All non-2xx responses throw an Error with the server's error message
 *   (or HTTP status text as fallback). Callers use try/catch.
 *
 * LAST MODIFIED: 2026-03-27 — Initial implementation (Phase 1 module redesign)
 */

// ─────────────────────────────────────────────────────────────────────────────
// ModuleAPI class
// ─────────────────────────────────────────────────────────────────────────────

export class ModuleAPI {
    /**
     * @param {object} [options]
     * @param {string} [options.baseUrl]   - API base URL. Defaults to window.API_BASE_URL or ''.
     * @param {string} [options.moduleId]  - Module identifier used in log/event messages.
     */
    constructor({ baseUrl = '', moduleId = '' } = {}) {
        this.baseUrl  = baseUrl || window.API_BASE_URL || '';
        this.moduleId = moduleId;
    }

    // ── Private helpers ──────────────────────────────────────────────────────

    /**
     * Build request headers, injecting the auth token from localStorage.
     * Always reads localStorage fresh so token refreshes are picked up automatically.
     * @param {object} [extra] - Additional headers to merge.
     * @returns {object}
     */
    _headers(extra = {}) {
        const token = localStorage.getItem('authToken') || '';
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            ...extra,
        };
    }

    /**
     * Core request dispatcher.
     * @param {string}      method  - HTTP verb: GET | POST | PUT | DELETE | PATCH
     * @param {string}      path    - URL path, e.g. '/api/xero/invoices'
     * @param {object|null} [body]  - JSON body (omitted for GET/DELETE)
     * @returns {Promise<any>} Parsed JSON response body
     * @throws {Error} On non-2xx response or network failure
     */
    async _request(method, path, body = null) {
        const url  = `${this.baseUrl}${path}`;
        const opts = {
            method,
            headers: this._headers(),
        };
        if (body !== null) {
            opts.body = JSON.stringify(body);
        }

        let res;
        try {
            res = await fetch(url, opts);
        } catch (networkErr) {
            // Network-level failure (offline, DNS, CORS preflight rejected, etc.)
            throw new Error(`[${this.moduleId}] Network error: ${networkErr.message}`);
        }

        // ── 401 — session expired ────────────────────────────────────────────
        if (res.status === 401) {
            window.dispatchEvent(new CustomEvent('module:auth-expired', {
                detail: { module: this.moduleId, url },
            }));
            throw new Error('Session expired. Please log in again.');
        }

        // ── Other non-2xx ────────────────────────────────────────────────────
        if (!res.ok) {
            let errMsg = `HTTP ${res.status}`;
            try {
                const errBody = await res.json();
                errMsg = errBody.error || errBody.message || errMsg;
            } catch (_) {
                // Response wasn't JSON — use status text
                errMsg = res.statusText || errMsg;
            }
            throw new Error(`[${this.moduleId}] ${errMsg}`);
        }

        // ── Success — parse JSON ─────────────────────────────────────────────
        // Handle 204 No Content (no body to parse)
        if (res.status === 204) return null;

        return res.json();
    }

    // ── Public HTTP methods ──────────────────────────────────────────────────

    /**
     * GET request. No body.
     * @param {string} path
     * @returns {Promise<any>}
     */
    get(path) {
        return this._request('GET', path);
    }

    /**
     * POST request with JSON body.
     * @param {string} path
     * @param {object} body
     * @returns {Promise<any>}
     */
    post(path, body) {
        return this._request('POST', path, body);
    }

    /**
     * PUT request with JSON body.
     * @param {string} path
     * @param {object} body
     * @returns {Promise<any>}
     */
    put(path, body) {
        return this._request('PUT', path, body);
    }

    /**
     * DELETE request. No body.
     * @param {string} path
     * @returns {Promise<any>}
     */
    delete(path) {
        return this._request('DELETE', path);
    }

    /**
     * PATCH request with JSON body.
     * @param {string} path
     * @param {object} body
     * @returns {Promise<any>}
     */
    patch(path, body) {
        return this._request('PATCH', path, body);
    }

    // ── Convenience: upload a file (multipart/form-data) ────────────────────

    /**
     * POST a FormData payload (file uploads, etc.).
     * Content-Type is intentionally omitted so the browser sets the boundary.
     * @param {string}   path
     * @param {FormData} formData
     * @returns {Promise<any>}
     */
    async upload(path, formData) {
        const token = localStorage.getItem('authToken') || '';
        const url   = `${this.baseUrl}${path}`;

        let res;
        try {
            res = await fetch(url, {
                method:  'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body:    formData,
            });
        } catch (networkErr) {
            throw new Error(`[${this.moduleId}] Upload network error: ${networkErr.message}`);
        }

        if (res.status === 401) {
            window.dispatchEvent(new CustomEvent('module:auth-expired', {
                detail: { module: this.moduleId, url },
            }));
            throw new Error('Session expired. Please log in again.');
        }

        if (!res.ok) {
            let errMsg = `HTTP ${res.status}`;
            try {
                const errBody = await res.json();
                errMsg = errBody.error || errBody.message || errMsg;
            } catch (_) {
                errMsg = res.statusText || errMsg;
            }
            throw new Error(`[${this.moduleId}] Upload failed: ${errMsg}`);
        }

        if (res.status === 204) return null;
        return res.json();
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Factory helper — used by module-loader-v4.js to inject into utilities
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Create a ModuleAPI instance bound to a specific module.
 * This is what module-loader-v4.js calls when building the `utilities` object.
 *
 * @param {string} moduleId
 * @returns {ModuleAPI}
 */
export function createModuleAPI(moduleId) {
    return new ModuleAPI({ moduleId });
}
