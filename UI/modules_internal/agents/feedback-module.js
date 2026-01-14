/**
 * ====================================================================
 * FEEDBACK MODULE - External Module Architecture
 * ====================================================================
 * 
 * A reusable, portable feedback widget system for AI agent interactions
 * 
 * FEATURES:
 * - Class-based singleton pattern for global instance management
 * - Event-driven architecture with custom events
 * - Multiple feedback contexts (per-agent, per-widget, global)
 * - Quick feedback templates (pause, stop, explain, etc.)
 * - API integration for feedback submission
 * - Theme support (dark/light)
 * - Keyboard shortcuts and accessibility
 * - LocalStorage persistence
 * 
 * USAGE:
 * ```javascript
 * // Initialize feedback module
 * const feedback = FeedbackModule.getInstance();
 * 
 * // Create feedback widget for an agent
 * feedback.createWidget('agent-1', {
 *     contextType: 'agent',
 *     contextId: 123,
 *     placeholder: 'Provide guidance to AI...',
 *     onSend: (text, context) => console.log('Feedback sent:', text)
 * });
 * 
 * // Show/hide widget
 * feedback.toggle('agent-1');
 * 
 * // Listen to events
 * document.addEventListener('feedback:sent', (e) => {
 *     console.log('Feedback sent:', e.detail);
 * });
 * ```
 * 
 * @module FeedbackModule
 * @version 2.0.0
 * @author Valor AI
 */

const FeedbackModule = (function () {
    'use strict';

    // ========================================
    // SINGLETON INSTANCE
    // ========================================
    let instance = null;

    // ========================================
    // QUICK FEEDBACK TEMPLATES
    // ========================================
    const QUICK_TEMPLATES = {
        pause: {
            icon: 'fa-pause',
            text: 'Please pause and wait for my next instruction.',
            label: 'Pause AI',
            color: '#f59e0b'
        },
        stop: {
            icon: 'fa-stop',
            text: 'Stop the current operation immediately.',
            label: 'Stop AI',
            color: '#ef4444'
        },
        explain: {
            icon: 'fa-question-circle',
            text: 'Please explain what you just did in more detail.',
            label: 'Explain',
            color: '#3b82f6'
        },
        clarify: {
            icon: 'fa-lightbulb',
            text: 'I need clarification on your last response.',
            label: 'Clarify',
            color: '#8b5cf6'
        },
        continue: {
            icon: 'fa-play',
            text: 'Continue with the current task.',
            label: 'Continue',
            color: '#10b981'
        },
        retry: {
            icon: 'fa-redo',
            text: 'Please retry the last operation with corrections.',
            label: 'Retry',
            color: '#f97316'
        }
    };

    // ========================================
    // DEFAULT CONFIGURATION
    // ========================================
    const DEFAULT_CONFIG = {
        theme: 'dark',
        enableKeyboardShortcuts: true,
        enableLocalStorage: true,
        animationDuration: 200,
        maxHistoryItems: 50,
        apiEndpoint: '/api/feedback'
    };

    // ========================================
    // FEEDBACK MODULE CLASS
    // ========================================
    class Feedback {
        constructor(config = {}) {
            if (instance) {
                console.warn('[FeedbackModule] Instance already exists, returning existing instance');
                return instance;
            }

            this.config = { ...DEFAULT_CONFIG, ...config };
            this.widgets = new Map(); // widgetId -> widget instance
            this.history = []; // Feedback history
            this.eventListeners = new Map(); // Custom event listeners

            this._init();

            instance = this;
        }

        /**
         * Initialize module
         * @private
         */
        _init() {
            console.log('[FeedbackModule] Initializing...');

            // Load history from localStorage
            if (this.config.enableLocalStorage) {
                this._loadHistory();
            }

            // Setup keyboard shortcuts
            if (this.config.enableKeyboardShortcuts) {
                this._setupKeyboardShortcuts();
            }

            // Setup global event listeners
            this._setupGlobalListeners();

            console.log('[FeedbackModule] ✅ Initialized successfully');
        }

        /**
         * Get singleton instance
         * @static
         * @param {Object} config - Configuration object
         * @returns {Feedback} Singleton instance
         */
        static getInstance(config = {}) {
            if (!instance) {
                instance = new Feedback(config);
            }
            return instance;
        }

        /**
         * Create a new feedback widget
         * @param {string} widgetId - Unique widget identifier (e.g., 'agent-1')
         * @param {Object} options - Widget configuration
         * @param {string} options.contextType - Context type ('agent', 'global', 'custom')
         * @param {number|string} options.contextId - Context identifier (e.g., agent ID)
         * @param {string} options.placeholder - Textarea placeholder text
         * @param {Function} options.onSend - Callback when feedback is sent
         * @param {Function} options.onCancel - Callback when widget is closed
         * @param {Array} options.quickButtons - Custom quick feedback buttons
         * @param {HTMLElement} options.container - Container element (if not using default)
         * @returns {Object} Widget instance
         */
        createWidget(widgetId, options = {}) {
            if (this.widgets.has(widgetId)) {
                console.warn(`[FeedbackModule] Widget '${widgetId}' already exists`);
                return this.widgets.get(widgetId);
            }

            const widget = {
                id: widgetId,
                contextType: options.contextType || 'global',
                contextId: options.contextId || null,
                placeholder: options.placeholder || 'Type instructions or guidance...',
                onSend: options.onSend || null,
                onCancel: options.onCancel || null,
                quickButtons: options.quickButtons || ['pause', 'stop', 'explain'],
                container: options.container || null,
                isVisible: false,
                element: null,
                textareaElement: null
            };

            // Build widget DOM
            widget.element = this._buildWidgetDOM(widget);

            // Store widget instance
            this.widgets.set(widgetId, widget);

            console.log(`[FeedbackModule] ✅ Created widget '${widgetId}'`);

            // Emit event
            this._emit('widget:created', { widgetId, widget });

            return widget;
        }

        /**
         * Build widget DOM structure
         * @private
         * @param {Object} widget - Widget configuration
         * @returns {HTMLElement} Widget DOM element
         */
        _buildWidgetDOM(widget) {
            const container = document.createElement('div');
            container.className = `feedback-widget feedback-widget-${widget.id}`;
            container.dataset.widgetId = widget.id;
            container.dataset.theme = this.config.theme;

            // Build quick buttons HTML
            const quickButtonsHTML = widget.quickButtons.map(templateKey => {
                const template = QUICK_TEMPLATES[templateKey];
                if (!template) return '';

                return `
                    <button class="feedback-quick-btn" 
                            data-template="${templateKey}"
                            title="${template.label}"
                            aria-label="${template.label}"
                            style="--btn-color: ${template.color}">
                        <i class="fas ${template.icon}"></i>
                    </button>
                `;
            }).join('');

            container.innerHTML = `
                <div class="feedback-header">
                    <div class="feedback-header-left">
                        <i class="fas fa-comment-dots"></i>
                        <span class="feedback-header-text">Provide guidance to AI</span>
                    </div>
                    <button class="feedback-close-btn" 
                            aria-label="Close feedback area">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="feedback-body">
                    <textarea class="feedback-textarea"
                              placeholder="${widget.placeholder}"
                              rows="3"
                              aria-label="Feedback text"></textarea>
                    <div class="feedback-quick-buttons">
                        ${quickButtonsHTML}
                        <button class="feedback-send-btn"
                                title="Send feedback"
                                aria-label="Send feedback">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            `;

            // Attach event listeners
            this._attachWidgetListeners(widget, container);

            // Store textarea reference
            widget.textareaElement = container.querySelector('.feedback-textarea');

            return container;
        }

        /**
         * Attach event listeners to widget DOM
         * @private
         * @param {Object} widget - Widget instance
         * @param {HTMLElement} container - Widget DOM element
         */
        _attachWidgetListeners(widget, container) {
            // Close button
            const closeBtn = container.querySelector('.feedback-close-btn');
            closeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.hide(widget.id);
            });

            // Send button
            const sendBtn = container.querySelector('.feedback-send-btn');
            sendBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.send(widget.id);
            });

            // Quick buttons
            const quickBtns = container.querySelectorAll('.feedback-quick-btn');
            quickBtns.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const templateKey = btn.dataset.template;
                    this.insertQuickFeedback(widget.id, templateKey);
                });
            });

            // Textarea keyboard shortcuts
            const textarea = container.querySelector('.feedback-textarea');
            textarea.addEventListener('keydown', (e) => {
                // Ctrl/Cmd + Enter to send
                if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                    e.preventDefault();
                    this.send(widget.id);
                }
                // Escape to close
                if (e.key === 'Escape') {
                    e.preventDefault();
                    this.hide(widget.id);
                }
            });
        }

        /**
         * Show feedback widget
         * @param {string} widgetId - Widget ID
         */
        show(widgetId) {
            const widget = this.widgets.get(widgetId);
            if (!widget) {
                console.error(`[FeedbackModule] Widget '${widgetId}' not found`);
                return;
            }

            if (widget.isVisible) return;

            widget.isVisible = true;
            widget.element.classList.add('visible');

            // Focus textarea
            setTimeout(() => {
                if (widget.textareaElement) {
                    widget.textareaElement.focus();
                }
            }, this.config.animationDuration);

            console.log(`[FeedbackModule] Showed widget '${widgetId}'`);
            this._emit('widget:shown', { widgetId, widget });
        }

        /**
         * Hide feedback widget
         * @param {string} widgetId - Widget ID
         */
        hide(widgetId) {
            const widget = this.widgets.get(widgetId);
            if (!widget) {
                console.error(`[FeedbackModule] Widget '${widgetId}' not found`);
                return;
            }

            if (!widget.isVisible) return;

            widget.isVisible = false;
            widget.element.classList.remove('visible');

            // Call onCancel callback
            if (widget.onCancel) {
                widget.onCancel(widget);
            }

            console.log(`[FeedbackModule] Hid widget '${widgetId}'`);
            this._emit('widget:hidden', { widgetId, widget });
        }

        /**
         * Toggle feedback widget visibility
         * @param {string} widgetId - Widget ID
         */
        toggle(widgetId) {
            const widget = this.widgets.get(widgetId);
            if (!widget) {
                console.error(`[FeedbackModule] Widget '${widgetId}' not found`);
                return;
            }

            if (widget.isVisible) {
                this.hide(widgetId);
            } else {
                this.show(widgetId);
            }
        }

        /**
         * Insert quick feedback template into textarea
         * @param {string} widgetId - Widget ID
         * @param {string} templateKey - Template key (pause, stop, explain, etc.)
         */
        insertQuickFeedback(widgetId, templateKey) {
            const widget = this.widgets.get(widgetId);
            const template = QUICK_TEMPLATES[templateKey];

            if (!widget || !template) {
                console.error(`[FeedbackModule] Widget or template not found`);
                return;
            }

            if (widget.textareaElement) {
                widget.textareaElement.value = template.text;
                widget.textareaElement.focus();
            }

            console.log(`[FeedbackModule] Inserted template '${templateKey}' into widget '${widgetId}'`);
            this._emit('template:inserted', { widgetId, templateKey, text: template.text });
        }

        /**
         * Send feedback from widget
         * @param {string} widgetId - Widget ID
         */
        async send(widgetId) {
            const widget = this.widgets.get(widgetId);
            if (!widget) {
                console.error(`[FeedbackModule] Widget '${widgetId}' not found`);
                return;
            }

            const text = widget.textareaElement ? widget.textareaElement.value.trim() : '';

            if (!text) {
                console.warn(`[FeedbackModule] Cannot send empty feedback`);
                return;
            }

            const feedbackData = {
                text,
                contextType: widget.contextType,
                contextId: widget.contextId,
                timestamp: new Date().toISOString(),
                widgetId: widget.id
            };

            console.log(`[FeedbackModule] Sending feedback from '${widgetId}':`, feedbackData);

            // Add to history
            this._addToHistory(feedbackData);

            // Call custom onSend callback
            if (widget.onSend) {
                try {
                    await widget.onSend(text, feedbackData);
                } catch (error) {
                    console.error('[FeedbackModule] Error in onSend callback:', error);
                }
            }

            // Emit event
            this._emit('feedback:sent', feedbackData);

            // Clear textarea
            if (widget.textareaElement) {
                widget.textareaElement.value = '';
            }

            // Hide widget
            this.hide(widgetId);

            console.log(`[FeedbackModule] ✅ Feedback sent successfully`);
        }

        /**
         * Get widget element for manual attachment
         * @param {string} widgetId - Widget ID
         * @returns {HTMLElement|null} Widget DOM element
         */
        getWidgetElement(widgetId) {
            const widget = this.widgets.get(widgetId);
            return widget ? widget.element : null;
        }

        /**
         * Destroy widget and clean up
         * @param {string} widgetId - Widget ID
         */
        destroyWidget(widgetId) {
            const widget = this.widgets.get(widgetId);
            if (!widget) return;

            // Remove DOM element
            if (widget.element && widget.element.parentElement) {
                widget.element.parentElement.removeChild(widget.element);
            }

            // Remove from map
            this.widgets.delete(widgetId);

            console.log(`[FeedbackModule] ✅ Destroyed widget '${widgetId}'`);
            this._emit('widget:destroyed', { widgetId });
        }

        /**
         * Get feedback history
         * @param {Object} filters - Filter options
         * @param {string} filters.contextType - Filter by context type
         * @param {number|string} filters.contextId - Filter by context ID
         * @param {number} filters.limit - Limit number of results
         * @returns {Array} Filtered history items
         */
        getHistory(filters = {}) {
            let history = [...this.history];

            if (filters.contextType) {
                history = history.filter(item => item.contextType === filters.contextType);
            }

            if (filters.contextId !== undefined) {
                history = history.filter(item => item.contextId === filters.contextId);
            }

            if (filters.limit) {
                history = history.slice(-filters.limit);
            }

            return history;
        }

        /**
         * Clear feedback history
         */
        clearHistory() {
            this.history = [];
            if (this.config.enableLocalStorage) {
                localStorage.removeItem('feedbackModule_history');
            }
            console.log('[FeedbackModule] ✅ History cleared');
            this._emit('history:cleared', {});
        }

        /**
         * Add feedback to history
         * @private
         * @param {Object} feedbackData - Feedback data
         */
        _addToHistory(feedbackData) {
            this.history.push(feedbackData);

            // Limit history size
            if (this.history.length > this.config.maxHistoryItems) {
                this.history.shift();
            }

            // Save to localStorage
            if (this.config.enableLocalStorage) {
                this._saveHistory();
            }
        }

        /**
         * Save history to localStorage
         * @private
         */
        _saveHistory() {
            try {
                localStorage.setItem('feedbackModule_history', JSON.stringify(this.history));
            } catch (error) {
                console.error('[FeedbackModule] Failed to save history:', error);
            }
        }

        /**
         * Load history from localStorage
         * @private
         */
        _loadHistory() {
            try {
                const stored = localStorage.getItem('feedbackModule_history');
                if (stored) {
                    this.history = JSON.parse(stored);
                    console.log(`[FeedbackModule] Loaded ${this.history.length} history items from localStorage`);
                }
            } catch (error) {
                console.error('[FeedbackModule] Failed to load history:', error);
            }
        }

        /**
         * Setup global keyboard shortcuts
         * @private
         */
        _setupKeyboardShortcuts() {
            document.addEventListener('keydown', (e) => {
                // Ctrl/Cmd + Shift + F to toggle first visible widget
                if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'F') {
                    e.preventDefault();
                    const firstWidget = this.widgets.values().next().value;
                    if (firstWidget) {
                        this.toggle(firstWidget.id);
                    }
                }
            });
        }

        /**
         * Setup global event listeners
         * @private
         */
        _setupGlobalListeners() {
            // Click outside to close visible widgets (optional)
            document.addEventListener('click', (e) => {
                this.widgets.forEach(widget => {
                    if (widget.isVisible && !widget.element.contains(e.target)) {
                        // Optional: close on outside click
                        // this.hide(widget.id);
                    }
                });
            });
        }

        /**
         * Emit custom event
         * @private
         * @param {string} eventName - Event name (e.g., 'feedback:sent')
         * @param {Object} detail - Event detail data
         */
        _emit(eventName, detail) {
            const event = new CustomEvent(eventName, { detail });
            document.dispatchEvent(event);

            // Also call internal listeners
            if (this.eventListeners.has(eventName)) {
                const listeners = this.eventListeners.get(eventName);
                listeners.forEach(callback => {
                    try {
                        callback(detail);
                    } catch (error) {
                        console.error(`[FeedbackModule] Error in event listener for '${eventName}':`, error);
                    }
                });
            }
        }

        /**
         * Add event listener
         * @param {string} eventName - Event name
         * @param {Function} callback - Callback function
         */
        on(eventName, callback) {
            if (!this.eventListeners.has(eventName)) {
                this.eventListeners.set(eventName, []);
            }
            this.eventListeners.get(eventName).push(callback);
        }

        /**
         * Remove event listener
         * @param {string} eventName - Event name
         * @param {Function} callback - Callback function
         */
        off(eventName, callback) {
            if (!this.eventListeners.has(eventName)) return;

            const listeners = this.eventListeners.get(eventName);
            const index = listeners.indexOf(callback);
            if (index > -1) {
                listeners.splice(index, 1);
            }
        }

        /**
         * Set theme (dark/light)
         * @param {string} theme - Theme name ('dark' or 'light')
         */
        setTheme(theme) {
            this.config.theme = theme;
            this.widgets.forEach(widget => {
                widget.element.dataset.theme = theme;
            });
            console.log(`[FeedbackModule] Theme set to '${theme}'`);
        }

        /**
         * Get module statistics
         * @returns {Object} Statistics object
         */
        getStats() {
            return {
                widgetCount: this.widgets.size,
                historyCount: this.history.length,
                activeWidgets: Array.from(this.widgets.values()).filter(w => w.isVisible).length
            };
        }
    }

    // ========================================
    // PUBLIC API
    // ========================================
    return {
        getInstance: Feedback.getInstance,
        QUICK_TEMPLATES,
        DEFAULT_CONFIG
    };
})();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FeedbackModule;
}
