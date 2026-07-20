/**
 * FILE: UI/shared/js/module-utilities.js
 * PURPOSE: Composable utility functions for modern module system
 * 
 * ARCHITECTURE: Composition-based (NOT inheritance)
 * - Modules request utilities via manifest.dependencies
 * - ModuleLoader composes utility object at runtime
 * - No global dependencies, everything passed explicitly
 * 
 * EXPORTS:
 * - DOMUtils - DOM manipulation utilities
 * - APIClient - Backend API communication
 * - StorageUtils - localStorage/sessionStorage wrapper
 * - EventBus - Inter-module communication
 * - LoggerUtils - Structured logging
 * 
 * USAGE:
 * const module = await import('./my-module.js');
 * await module.MyModule.onLoad({
 *     dom: DOMUtils,
 *     api: APIClient,
 *     storage: StorageUtils
 * });
 * 
 * LAST MODIFIED: 2025-11-29 - Initial composition system implementation
 */

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// DOM UTILITIES
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
export const DOMUtils = {
    /**
     * Get container element by ID (with error handling)
     */
    getContainer(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            throw new Error(`Container not found: #${containerId}`);
        }
        return container;
    },

    /**
     * Create element with attributes and children
     * 
     * @example
     * const btn = dom.createElement('button', {
     *     class: 'btn btn-primary',
     *     'data-action': 'save'
     * }, ['Save']);
     */
    createElement(tag, attributes = {}, children = []) {
        const element = document.createElement(tag);

        // Set attributes
        Object.entries(attributes).forEach(([key, value]) => {
            if (key === 'class') {
                element.className = value;
            } else if (key.startsWith('data-')) {
                element.setAttribute(key, value);
            } else if (key === 'style' && typeof value === 'object') {
                Object.assign(element.style, value);
            } else {
                element[key] = value;
            }
        });

        // Append children
        children.forEach(child => {
            if (typeof child === 'string') {
                element.appendChild(document.createTextNode(child));
            } else if (child instanceof Node) {
                element.appendChild(child);
            }
        });

        return element;
    },

    /**
     * Clear element content safely
     */
    clearElement(element) {
        while (element.firstChild) {
            element.removeChild(element.firstChild);
        }
    },

    /**
     * Show element (remove 'hidden' class, set display)
     */
    show(element, displayType = 'block') {
        element.classList.remove('hidden');
        element.style.display = displayType;
    },

    /**
     * Hide element (add 'hidden' class, set display none)
     */
    hide(element) {
        element.classList.add('hidden');
        element.style.display = 'none';
    },

    /**
     * Toggle element visibility
     */
    toggle(element, displayType = 'block') {
        if (element.classList.contains('hidden') || element.style.display === 'none') {
            this.show(element, displayType);
        } else {
            this.hide(element);
        }
    },

    /**
     * Query selector with error handling
     */
    query(selector, context = document) {
        const elements = context.querySelectorAll(selector);
        return Array.from(elements);
    },

    /**
     * Add event listener with cleanup tracking
     * Supports event delegation (jQuery-style)
     * 
     * Usage:
     *   dom.on(element, 'click', handler)  // Direct
     *   dom.on(element, 'click', '.btn', handler)  // Delegated
     */
    on(element, event, selectorOrHandler, handlerOrOptions) {
        // Check if using delegation pattern (4 params with selector)
        if (typeof selectorOrHandler === 'string') {
            // Delegation: dom.on(element, event, selector, handler)
            const selector = selectorOrHandler;
            const handler = handlerOrOptions;

            const delegatedHandler = (e) => {
                // Find closest matching element (supports event bubbling)
                const target = e.target.closest(selector);
                if (target && element.contains(target)) {
                    // Call handler with matched element as currentTarget
                    Object.defineProperty(e, 'currentTarget', {
                        value: target,
                        writable: false,
                        configurable: true
                    });
                    handler.call(target, e);
                }
            };

            element.addEventListener(event, delegatedHandler);
            return () => element.removeEventListener(event, delegatedHandler);
        } else {
            // Direct: dom.on(element, event, handler, options)
            const handler = selectorOrHandler;
            const options = handlerOrOptions || {};

            element.addEventListener(event, handler, options);
            return () => element.removeEventListener(event, handler, options);
        }
    },

    /**
     * Batch add event listeners (returns cleanup function)
     */
    onAll(elements, event, handler, options = {}) {
        const cleanupFns = elements.map(el =>
            this.on(el, event, handler, options)
        );

        return () => cleanupFns.forEach(fn => fn());
    },

    /**
     * Wait for element to appear in DOM
     */
    async waitForElement(selector, timeout = 5000) {
        const startTime = Date.now();

        while (Date.now() - startTime < timeout) {
            const element = document.querySelector(selector);
            if (element) return element;
            await new Promise(resolve => setTimeout(resolve, 100));
        }

        throw new Error(`Element not found after ${timeout}ms: ${selector}`);
    },

    /**
     * Inject HTML safely (sanitized)
     */
    injectHTML(container, html) {
        // Basic XSS protection (strip <script> tags)
        const sanitized = html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
        container.innerHTML = sanitized;
    },

    /**
     * Get computed style value
     */
    getStyle(element, property) {
        return window.getComputedStyle(element).getPropertyValue(property);
    },

    /**
     * Scroll element into view smoothly
     */
    scrollTo(element, options = {}) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
            ...options
        });
    }
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// API CLIENT
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
export const APIClient = {
    baseURL: window.API_BASE_URL || 'http://localhost:5001',
    defaultTimeout: 30000,

    /**
     * Get authentication headers with JWT token
     * @private
     * @returns {Object} Headers object with Authorization if token exists
     */
    _getAuthHeaders() {
        const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
        return {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        };
    },

    /**
     * Generic HTTP request
     */
    async request(endpoint, options = {}) {
        const url = endpoint.startsWith('http')
            ? endpoint
            : `${this.baseURL}${endpoint}`;

        const config = {
            method: options.method || 'GET',
            headers: {
                ...this._getAuthHeaders(),
                ...options.headers  // Allow override of default headers
            },
            ...options
        };

        // Add body if present
        if (options.body && typeof options.body === 'object') {
            config.body = JSON.stringify(options.body);
        }

        // Timeout handling
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), options.timeout || this.defaultTimeout);
        config.signal = controller.signal;

        try {
            const response = await fetch(url, config);
            clearTimeout(timeout);

            // Handle authentication failures
            if (response.status === 401 || response.status === 403) {
                console.warn('Authentication failed, redirecting to login');
                window.location.href = '/login';
                throw new Error('Unauthorized - redirecting to login');
            }

            // Handle non-OK responses
            if (!response.ok) {
                const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
                error.status = response.status;
                error.response = response;
                throw error;
            }

            // Parse JSON response
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }

            return await response.text();

        } catch (error) {
            clearTimeout(timeout);

            if (error.name === 'AbortError') {
                throw new Error(`Request timeout after ${options.timeout || this.defaultTimeout}ms`);
            }

            throw error;
        }
    },

    /**
     * GET request
     * Supports both modern and legacy signatures:
     *   - Modern: api.get(endpoint, params, options)
     *   - Legacy: api.get(endpoint, {params, ...options})
     */
    async get(endpoint, paramsOrOptions = {}, options = {}) {
        let queryParams = {};
        let requestOptions = {};

        // Detect legacy signature: api.get(url, {params: {...}, headers: {...}})
        if (paramsOrOptions.params && typeof paramsOrOptions.params === 'object') {
            queryParams = paramsOrOptions.params;
            requestOptions = { ...paramsOrOptions };
            delete requestOptions.params;
        }
        // Modern signature: api.get(url, {key: value}, {headers: {...}})
        else {
            queryParams = paramsOrOptions;
            requestOptions = options;
        }

        // Build query string
        const queryString = new URLSearchParams(queryParams).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;

        return this.request(url, { ...requestOptions, method: 'GET' });
    },

    /**
     * POST request
     */
    async post(endpoint, body = {}, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'POST',
            body
        });
    },

    /**
     * PUT request
     */
    async put(endpoint, body = {}, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'PUT',
            body
        });
    },

    /**
     * DELETE request
     */
    async delete(endpoint, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'DELETE'
        });
    },

    /**
     * PATCH request
     */
    async patch(endpoint, body = {}, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'PATCH',
            body
        });
    },

    /**
     * Upload file
     */
    async upload(endpoint, file, additionalData = {}) {
        const formData = new FormData();
        formData.append('file', file);

        Object.entries(additionalData).forEach(([key, value]) => {
            formData.append(key, value);
        });

        return this.request(endpoint, {
            method: 'POST',
            body: formData,
            headers: {} // Let browser set Content-Type with boundary
        });
    }
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// STORAGE UTILITIES
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
export const StorageUtils = {
    /**
     * Get item from localStorage (with JSON parsing)
     */
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error(`Failed to get ${key} from storage:`, error);
            return defaultValue;
        }
    },

    /**
     * Set item in localStorage (with JSON serialization)
     */
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error(`Failed to set ${key} in storage:`, error);
            return false;
        }
    },

    /**
     * Remove item from localStorage
     */
    remove(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error(`Failed to remove ${key} from storage:`, error);
            return false;
        }
    },

    /**
     * Clear all items from localStorage
     */
    clear() {
        try {
            localStorage.clear();
            return true;
        } catch (error) {
            console.error('Failed to clear storage:', error);
            return false;
        }
    },

    /**
     * Session storage (same API as localStorage)
     */
    session: {
        get(key, defaultValue = null) {
            try {
                const item = sessionStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (error) {
                console.error(`Failed to get ${key} from session:`, error);
                return defaultValue;
            }
        },

        set(key, value) {
            try {
                sessionStorage.setItem(key, JSON.stringify(value));
                return true;
            } catch (error) {
                console.error(`Failed to set ${key} in session:`, error);
                return false;
            }
        },

        remove(key) {
            try {
                sessionStorage.removeItem(key);
                return true;
            } catch (error) {
                console.error(`Failed to remove ${key} from session:`, error);
                return false;
            }
        },

        clear() {
            try {
                sessionStorage.clear();
                return true;
            } catch (error) {
                console.error('Failed to clear session:', error);
                return false;
            }
        }
    }
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// EVENT BUS (Inter-module communication)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
export const EventBus = {
    listeners: new Map(),

    /**
     * Subscribe to event
     */
    on(event, handler) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, new Set());
        }
        this.listeners.get(event).add(handler);

        // Return unsubscribe function
        return () => this.off(event, handler);
    },

    /**
     * Unsubscribe from event
     */
    off(event, handler) {
        if (!this.listeners.has(event)) return;
        this.listeners.get(event).delete(handler);
    },

    /**
     * Emit event to all subscribers
     */
    emit(event, data) {
        if (!this.listeners.has(event)) return;

        this.listeners.get(event).forEach(handler => {
            try {
                handler(data);
            } catch (error) {
                console.error(`Error in event handler for ${event}:`, error);
            }
        });
    },

    /**
     * Subscribe once (auto-unsubscribe after first call)
     */
    once(event, handler) {
        const wrappedHandler = (data) => {
            handler(data);
            this.off(event, wrappedHandler);
        };
        return this.on(event, wrappedHandler);
    },

    /**
     * Clear all listeners for event (or all events)
     */
    clear(event = null) {
        if (event) {
            this.listeners.delete(event);
        } else {
            this.listeners.clear();
        }
    }
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// LOGGER UTILITIES
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
export const LoggerUtils = {
    enabledLevels: new Set(['info', 'warn', 'error', 'debug']),

    /**
     * Configure logger
     */
    configure(options = {}) {
        if (options.levels) {
            this.enabledLevels = new Set(options.levels);
        }
    },

    /**
     * Log info message
     */
    info(module, message, ...args) {
        if (!this.enabledLevels.has('info')) return;
        console.log(`[${module}] ℹ️ ${message}`, ...args);
    },

    /**
     * Log warning message
     */
    warn(module, message, ...args) {
        if (!this.enabledLevels.has('warn')) return;
        console.warn(`[${module}] ⚠️ ${message}`, ...args);
    },

    /**
     * Log error message
     */
    error(module, message, error, ...args) {
        if (!this.enabledLevels.has('error')) return;
        console.error(`[${module}] ❌ ${message}`, error, ...args);
    },

    /**
     * Log debug message
     */
    debug(module, message, ...args) {
        if (!this.enabledLevels.has('debug')) return;
        console.debug(`[${module}] 🔍 ${message}`, ...args);
    },

    /**
     * Log success message
     */
    success(module, message, ...args) {
        if (!this.enabledLevels.has('info')) return;
        console.log(`[${module}] ✅ ${message}`, ...args);
    },

    /**
     * Create module-specific logger
     */
    createLogger(moduleName) {
        return {
            info: (msg, ...args) => this.info(moduleName, msg, ...args),
            warn: (msg, ...args) => this.warn(moduleName, msg, ...args),
            error: (msg, error, ...args) => this.error(moduleName, msg, error, ...args),
            debug: (msg, ...args) => this.debug(moduleName, msg, ...args),
            success: (msg, ...args) => this.success(moduleName, msg, ...args)
        };
    }
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// UTILITY COMPOSER (Used by ModuleLoader)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
export const UtilityComposer = {
    availableUtilities: {
        dom: DOMUtils,
        api: APIClient,
        storage: StorageUtils,
        events: EventBus,
        logger: LoggerUtils
    },

    /**
     * Compose utilities based on manifest dependencies
     * 
     * @param {object} dependencies - From manifest.dependencies
     * @param {string} moduleId - Module ID for logger creation
     * @returns {object} Composed utilities object
     */
    compose(dependencies = {}, moduleId = 'unknown') {
        // Default parameters only apply for `undefined`, not `null`. Catalog rows
        // whose `dependencies` column is absent get returned as null from the API,
        // so coerce here to keep callers from having to defensively pass `|| {}`.
        dependencies = dependencies || {};
        const composed = {};

        // Add requested utilities
        const requestedUtils = dependencies.utilities || [];

        console.log(`[UtilityComposer] Composing for ${moduleId}, requested:`, requestedUtils);

        requestedUtils.forEach(utilName => {
            if (this.availableUtilities[utilName]) {
                // For DOM utilities, create module-aware wrapper
                if (utilName === 'dom') {
                    composed.dom = {
                        ...this.availableUtilities.dom,
                        // Override getContainer to default to module's container
                        getContainer(containerId) {
                            const id = containerId || `tab-${moduleId}`;
                            console.log(`[DOM Utils] getContainer called for module ${moduleId}, containerId: ${containerId}, resolved: ${id}`);
                            const container = document.getElementById(id);
                            if (!container) {
                                console.error(`[DOM Utils] Container not found: #${id}, available containers:`,
                                    Array.from(document.querySelectorAll('[id^="tab-"]')).map(el => el.id));
                                throw new Error(`Container not found: #${id}`);
                            }
                            console.log(`[DOM Utils] Found container:`, container);
                            return container;
                        }
                    };
                    console.log(`[UtilityComposer] Added DOM utility wrapper for ${moduleId}`);
                } else {
                    composed[utilName] = this.availableUtilities[utilName];
                }
            } else {
                console.warn(`[UtilityComposer] Unknown utility requested: ${utilName}`);
            }
        });

        // Always include module-specific logger
        composed.log = LoggerUtils.createLogger(moduleId);

        console.log(`[UtilityComposer] Composed utilities for ${moduleId}:`, Object.keys(composed));

        return composed;
    },

    /**
     * Register custom utility
     */
    register(name, utility) {
        this.availableUtilities[name] = utility;
    }
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// EXPORT ALL
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
export default {
    DOMUtils,
    APIClient,
    StorageUtils,
    EventBus,
    LoggerUtils,
    UtilityComposer
};
