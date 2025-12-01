/**
 * ========== AUTOMATION SETTINGS SYNC MANAGER ==========
 * Central state manager for bidirectional settings sync between:
 * - Automations Sidebar (right panel)
 * - Canvas Settings Overlay (floating panel on canvas)
 * 
 * Architecture:
 * - Single source of truth for automation settings
 * - Pub/sub pattern with listeners
 * - Automatic backend sync on changes
 * - Handles draft vs production mode
 * 
 * Created: November 28, 2025
 */

const AutomationSettingsSync = {
    currentAutomation: null,
    originalSettings: null,
    listeners: [],
    isDirty: false,
    autoSaveTimeout: null,
    autoSaveDelay: 2000, // 2 seconds after last change

    /**
     * Load settings for an automation
     * @param {string} slug - Automation workflow slug
     * @returns {Promise<Object>} Automation data
     */
    async loadSettings(slug) {
        try {
            console.log('[SETTINGS-SYNC] Loading settings for:', slug);
            
            const API_BASE_URL = window.API_BASE_URL || 'http://localhost:5001';
            const response = await fetch(`${API_BASE_URL}/api/automation/${slug}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token') || ''}`
                }
            });

            if (!response.ok) {
                throw new Error(`Failed to fetch automation: ${response.status}`);
            }

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Failed to load automation');
            }

            this.currentAutomation = data.automation || data.workflow;
            this.originalSettings = JSON.parse(JSON.stringify(this.currentAutomation)); // Deep clone
            this.isDirty = false;

            console.log('[SETTINGS-SYNC] Settings loaded:', this.currentAutomation);
            this.notifyListeners('load');

            return this.currentAutomation;
        } catch (error) {
            console.error('[SETTINGS-SYNC] Failed to load settings:', error);
            if (typeof showNotification !== 'undefined') {
                showNotification(`Failed to load settings: ${error.message}`, 'error');
            }
            throw error;
        }
    },

    /**
     * Update a setting value and notify listeners
     * @param {string} path - Dot-notation path (e.g., 'schedule.cron')
     * @param {any} value - New value
     */
    updateSetting(path, value) {
        if (!this.currentAutomation) {
            console.error('[SETTINGS-SYNC] No automation loaded');
            return;
        }

        console.log(`[SETTINGS-SYNC] Updating ${path} =`, value);

        const keys = path.split('.');
        let obj = this.currentAutomation;

        // Navigate to parent object
        for (let i = 0; i < keys.length - 1; i++) {
            if (!obj[keys[i]]) {
                obj[keys[i]] = {};
            }
            obj = obj[keys[i]];
        }

        // Set value
        obj[keys[keys.length - 1]] = value;
        this.isDirty = true;

        // Notify all listeners
        this.notifyListeners('update', { path, value });

        // Schedule auto-save
        this.scheduleAutoSave();
    },

    /**
     * Toggle notification channel (special handler for array manipulation)
     * @param {string} channel - Channel name (email, slack, webhook)
     * @param {boolean} enabled - Enable or disable
     */
    toggleNotificationChannel(channel, enabled) {
        if (!this.currentAutomation.notifications) {
            this.currentAutomation.notifications = {};
        }
        if (!this.currentAutomation.notifications.channels) {
            this.currentAutomation.notifications.channels = [];
        }

        const channels = this.currentAutomation.notifications.channels;
        const index = channels.indexOf(channel);

        if (enabled && index === -1) {
            channels.push(channel);
        } else if (!enabled && index !== -1) {
            channels.splice(index, 1);
        }

        this.isDirty = true;
        this.notifyListeners('update', { path: 'notifications.channels', value: channels });
        this.scheduleAutoSave();
    },

    /**
     * Schedule auto-save after delay
     */
    scheduleAutoSave() {
        if (this.autoSaveTimeout) {
            clearTimeout(this.autoSaveTimeout);
        }

        this.autoSaveTimeout = setTimeout(() => {
            this.save(true); // Silent auto-save
        }, this.autoSaveDelay);
    },

    /**
     * Subscribe to settings changes
     * @param {Function} callback - Callback function(eventType, data)
     * @returns {Function} Unsubscribe function
     */
    subscribe(callback) {
        this.listeners.push(callback);
        console.log(`[SETTINGS-SYNC] Listener subscribed (total: ${this.listeners.length})`);

        // Return unsubscribe function
        return () => {
            const index = this.listeners.indexOf(callback);
            if (index !== -1) {
                this.listeners.splice(index, 1);
                console.log(`[SETTINGS-SYNC] Listener unsubscribed (remaining: ${this.listeners.length})`);
            }
        };
    },

    /**
     * Notify all subscribers of changes
     * @param {string} eventType - 'load', 'update', 'save', 'error'
     * @param {Object} data - Event data
     */
    notifyListeners(eventType, data = {}) {
        console.log(`[SETTINGS-SYNC] Notifying ${this.listeners.length} listeners:`, eventType, data);
        
        this.listeners.forEach(callback => {
            try {
                callback(eventType, {
                    automation: this.currentAutomation,
                    isDirty: this.isDirty,
                    ...data
                });
            } catch (error) {
                console.error('[SETTINGS-SYNC] Listener error:', error);
            }
        });
    },

    /**
     * Save settings to backend
     * @param {boolean} silent - Don't show notifications
     * @returns {Promise<Object>} Save response
     */
    async save(silent = false) {
        if (!this.currentAutomation) {
            console.error('[SETTINGS-SYNC] No automation to save');
            return null;
        }

        if (!this.isDirty) {
            console.log('[SETTINGS-SYNC] No changes to save');
            return { success: true, message: 'No changes' };
        }

        try {
            console.log('[SETTINGS-SYNC] Saving settings to backend...');

            const API_BASE_URL = window.API_BASE_URL || 'http://localhost:5001';
            const response = await fetch(`${API_BASE_URL}/api/automation/${this.currentAutomation.slug}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token') || ''}`
                },
                body: JSON.stringify(this.currentAutomation)
            });

            if (!response.ok) {
                throw new Error(`Save failed: ${response.status}`);
            }

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Failed to save settings');
            }

            this.isDirty = false;
            this.originalSettings = JSON.parse(JSON.stringify(this.currentAutomation));

            console.log('[SETTINGS-SYNC] Settings saved successfully');
            
            if (!silent && typeof showNotification !== 'undefined') {
                showNotification('Automation settings saved', 'success');
            }

            this.notifyListeners('save', { automation: data.automation });

            return data;
        } catch (error) {
            console.error('[SETTINGS-SYNC] Save failed:', error);
            
            if (!silent && typeof showNotification !== 'undefined') {
                showNotification(`Failed to save settings: ${error.message}`, 'error');
            }

            this.notifyListeners('error', { error: error.message });
            
            throw error;
        }
    },

    /**
     * Revert to original settings
     */
    revert() {
        if (!this.originalSettings) {
            console.warn('[SETTINGS-SYNC] No original settings to revert to');
            return;
        }

        console.log('[SETTINGS-SYNC] Reverting changes...');
        this.currentAutomation = JSON.parse(JSON.stringify(this.originalSettings));
        this.isDirty = false;

        this.notifyListeners('revert');

        if (typeof showNotification !== 'undefined') {
            showNotification('Changes reverted', 'info');
        }
    },

    /**
     * Check if current automation is in draft mode
     * @returns {boolean}
     */
    isDraft() {
        return this.currentAutomation && (
            this.currentAutomation.type === 'draft' || 
            this.currentAutomation.is_draft === true ||
            !this.currentAutomation.workflow_id // No workflow_id means it's in visual_automations only
        );
    },

    /**
     * Check if settings have unsaved changes
     * @returns {boolean}
     */
    hasUnsavedChanges() {
        return this.isDirty;
    },

    /**
     * Get current automation data
     * @returns {Object|null}
     */
    getCurrentAutomation() {
        return this.currentAutomation;
    },

    /**
     * Validate settings before save
     * @returns {Object} { valid: boolean, errors: string[] }
     */
    validate() {
        const errors = [];

        if (!this.currentAutomation) {
            errors.push('No automation loaded');
            return { valid: false, errors };
        }

        // Validate scheduling
        if (this.currentAutomation.schedule) {
            const schedule = this.currentAutomation.schedule;

            if (schedule.type === 'cron' && !schedule.cron) {
                errors.push('Cron expression required for cron schedule');
            }

            if (schedule.type === 'interval') {
                if (!schedule.interval_value || schedule.interval_value < 1) {
                    errors.push('Interval value must be at least 1');
                }
                if (!schedule.interval_unit) {
                    errors.push('Interval unit required');
                }
            }

            if (schedule.type === 'one-time' && !schedule.run_at) {
                errors.push('Run date/time required for one-time schedule');
            }
        }

        // Validate notifications
        if (this.currentAutomation.notifications) {
            const notif = this.currentAutomation.notifications;

            if ((notif.on_success || notif.on_failure) && (!notif.channels || notif.channels.length === 0)) {
                errors.push('At least one notification channel required');
            }

            if (notif.channels?.includes('email') && !notif.emails) {
                errors.push('Email recipients required for email notifications');
            }
        }

        // Validate execution options
        if (this.currentAutomation.execution_options) {
            const exec = this.currentAutomation.execution_options;

            if (exec.retry_policy !== 'none') {
                if (!exec.max_retries || exec.max_retries < 1) {
                    errors.push('Max retries must be at least 1');
                }
            }

            if (!exec.timeout || exec.timeout < 1) {
                errors.push('Timeout must be at least 1 second');
            }
        }

        return {
            valid: errors.length === 0,
            errors
        };
    },

    /**
     * Reset state
     */
    reset() {
        console.log('[SETTINGS-SYNC] Resetting state');
        this.currentAutomation = null;
        this.originalSettings = null;
        this.listeners = [];
        this.isDirty = false;

        if (this.autoSaveTimeout) {
            clearTimeout(this.autoSaveTimeout);
            this.autoSaveTimeout = null;
        }
    }
};

// Expose globally
window.AutomationSettingsSync = AutomationSettingsSync;

console.log('[SETTINGS-SYNC] Module loaded');
