/**
 * SETTINGS SIDEBAR MODULE v2.0 - WITH DYNAMIC HTML LOADING
 * 
 * NEW FEATURES:
 * - Dynamic HTML loading from settings-sidebar.html
 * - Toast notifications on settings changes
 * - Detailed hover tooltips explaining impact
 * - No HTML in main file required!
 */

console.log('[Settings v2] Module loading...');

(function () {
    'use strict';

    // ==================== TOAST NOTIFICATION SYSTEM ====================
    
    const ToastManager = {
        show(message, type = 'success', duration = 3000) {
            const container = document.getElementById('notification-container') || document.body;
            
            const toast = document.createElement('div');
            toast.className = `settings-toast settings-toast-${type}`;
            toast.innerHTML = `
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            `;
            
            container.appendChild(toast);
            
            // Trigger animation
            setTimeout(() => toast.classList.add('show'), 10);
            
            // Remove after duration
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }
    };

    // ==================== SETTINGS DESCRIPTIONS & TOOLTIPS ====================
    
    const SettingDescriptions = {
        'auto-recovery-enabled': {
            title: 'Master Auto-Recovery Toggle',
            description: 'Controls all automatic error recovery attempts',
            impact: 'When OFF: You must manually retry failed requests. Useful for debugging.',
            example: 'If API fails, system will NOT automatically retry'
        },
        'recovery-tool-mismatch': {
            title: 'Tool Use Mismatch Recovery',
            description: 'Fixes orphaned tool_result blocks without matching tool_use',
            impact: 'Prevents "tool_result without tool_use" API errors',
            example: 'AI sent tool results without calling the tool first'
        },
        'recovery-invalid-structure': {
            title: 'Invalid Message Structure Recovery',
            description: 'Fixes thinking blocks in wrong position',
            impact: 'Prevents "thinking blocks must be first" API errors',
            example: 'AI put thinking after text instead of before'
        },
        'recovery-context-length': {
            title: 'Context Length Recovery',
            description: 'Automatically trims conversation when too large',
            impact: 'Prevents "context length exceeded" errors, but loses older messages',
            example: 'Conversation > 200K tokens, system removes oldest messages'
        },
        'recovery-rate-limit': {
            title: 'Rate Limit Recovery',
            description: 'Waits and retries when API rate limit is hit',
            impact: 'Adds delays (exponential backoff) but ensures request completes',
            example: 'Too many requests per minute, system waits 30s and retries'
        },
        'recovery-network': {
            title: 'Network Error Recovery',
            description: 'Retries on network failures (ERR_CONNECTION_RESET, etc.)',
            impact: 'Handles temporary network issues automatically',
            example: 'Internet connection dropped briefly, system retries automatically'
        },
        'max-retries': {
            title: 'Maximum Retry Attempts',
            description: 'How many times to retry before giving up',
            impact: 'Higher = more persistent, but longer wait on failures',
            example: '3 retries = up to 3 attempts (original + 2 retries)'
        },
        'show-recovery-notifications': {
            title: 'Recovery Success Notifications',
            description: 'Show toast notification when recovery succeeds',
            impact: 'Visual feedback when system fixes errors automatically',
            example: 'Green toast: "Recovered from network error"'
        },
        'detailed-logging': {
            title: 'Detailed Recovery Logging',
            description: 'Log full error context and recovery steps to console',
            impact: 'Helps debugging but adds console clutter',
            example: 'console.group() with error payload, thread ID, timestamp'
        }
    };

    // ==================== SETTINGS MANAGER ====================
    
    const SettingsManager = {
        storageKey: 'aiAgentSettings',
        
        defaults: {
            autoRecovery: {
                enabled: true,
                maxRetries: 3,
                showNotifications: true,
                detailedLogging: true,
                recoveryTypes: {
                    tool_mismatch: true,
                    invalid_structure: true,
                    context_length: true,
                    rate_limit: true,
                    network: true
                }
            },
            display: {
                showThinking: true,
                showToolDetails: true,
                autoScroll: true
            },
            advanced: {
                debugMode: false,
                cacheResponses: true
            },
            statistics: {
                totalAttempts: 0,
                successCount: 0,
                failureCount: 0,
                lastRecoveryTime: null
            }
        },

        load() {
            try {
                const saved = localStorage.getItem(this.storageKey);
                if (saved) {
                    return { ...this.defaults, ...JSON.parse(saved) };
                }
            } catch (error) {
                console.error('[Settings] Error loading settings:', error);
            }
            return this.defaults;
        },

        save(settings) {
            try {
                localStorage.setItem(this.storageKey, JSON.stringify(settings));
                return true;
            } catch (error) {
                console.error('[Settings] Error saving settings:', error);
                return false;
            }
        },

        get(path, defaultValue) {
            const settings = this.load();
            const keys = path.split('.');
            let value = settings;
            
            for (const key of keys) {
                value = value?.[key];
                if (value === undefined) return defaultValue;
            }
            
            return value;
        },

        update(path, value) {
            const settings = this.load();
            const keys = path.split('.');
            let obj = settings;
            
            for (let i = 0; i < keys.length - 1; i++) {
                obj = obj[keys[i]];
            }
            
            obj[keys[keys.length - 1]] = value;
            return this.save(settings);
        },

        recordRecovery(type, success, metadata = {}) {
            const settings = this.load();
            settings.statistics.totalAttempts++;
            
            if (success) {
                settings.statistics.successCount++;
            } else {
                settings.statistics.failureCount++;
            }
            
            settings.statistics.lastRecoveryTime = Date.now();
            settings.statistics.lastRecoveryType = type;
            settings.statistics.lastRecoveryMetadata = metadata;
            
            this.save(settings);
            this.updateStatisticsDisplay();
        },

        getRecoveryStats() {
            const stats = this.get('statistics');
            const successRate = stats.totalAttempts > 0 
                ? Math.round((stats.successCount / stats.totalAttempts) * 100)
                : 100;
            
            return {
                ...stats,
                successRate
            };
        },

        resetStatistics() {
            this.update('statistics', {
                totalAttempts: 0,
                successCount: 0,
                failureCount: 0,
                lastRecoveryTime: null
            });
            this.updateStatisticsDisplay();
            ToastManager.show('Statistics reset', 'success');
        },

        updateStatisticsDisplay() {
            const stats = this.getRecoveryStats();
            
            const totalEl = document.getElementById('stat-total-recoveries');
            const rateEl = document.getElementById('stat-success-rate');
            const lastEl = document.getElementById('stat-last-recovery');
            
            if (totalEl) totalEl.textContent = stats.totalAttempts;
            if (rateEl) rateEl.textContent = `${stats.successRate}%`;
            if (lastEl) {
                if (stats.lastRecoveryTime) {
                    const date = new Date(stats.lastRecoveryTime);
                    lastEl.textContent = date.toLocaleTimeString();
                } else {
                    lastEl.textContent = 'Never';
                }
            }
        }
    };

    // ==================== UI FUNCTIONS ====================

    window.openSettingsSidebar = function() {
        console.log('[Settings] openSettingsSidebar called');
        const sidebar = document.getElementById('settings-sidebar');
        if (sidebar) {
            sidebar.classList.add('show');
            loadSettingsIntoUI();
            console.log('[Settings] Sidebar opened');
        } else {
            console.warn('[Settings] Sidebar not loaded yet - loading now...');
            // Load HTML first, then open
            loadSettingsSidebarHTML().then(() => {
                const sidebar = document.getElementById('settings-sidebar');
                if (sidebar) {
                    sidebar.classList.add('show');
                    loadSettingsIntoUI();
                    console.log('[Settings] Sidebar loaded and opened');
                }
            });
        }
    };

    window.closeSettingsSidebar = function() {
        const sidebar = document.getElementById('settings-sidebar');
        if (sidebar) {
            sidebar.classList.remove('show');
            console.log('[Settings] Sidebar closed');
        }
    };

    window.switchSettingsTab = function(tabName) {
        // Update tab buttons
        document.querySelectorAll('.sidebar-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });
        
        // Update tab content
        document.querySelectorAll('.sidebar-tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `${tabName}-settings-tab`);
        });
    };

    function loadSettingsIntoUI() {
        const settings = SettingsManager.load();
        
        // Load all checkbox settings
        const checkboxes = document.querySelectorAll('#settings-sidebar input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            const settingPath = checkbox.id.replace('setting-', '').replace(/-/g, '.');
            const value = SettingsManager.get(settingPath);
            if (value !== undefined) {
                checkbox.checked = value;
            }
        });
        
        // Load max retries
        const maxRetriesInput = document.getElementById('setting-max-retries');
        if (maxRetriesInput) {
            maxRetriesInput.value = SettingsManager.get('autoRecovery.maxRetries', 3);
        }
        
        // Update statistics
        SettingsManager.updateStatisticsDisplay();
    }

    // ==================== SAVE FUNCTIONS WITH TOAST ====================

    window.saveRecoverySettings = function() {
        const enabled = document.getElementById('setting-auto-recovery-enabled')?.checked;
        const maxRetries = parseInt(document.getElementById('setting-max-retries')?.value || 3);
        const showNotifications = document.getElementById('setting-show-recovery-notifications')?.checked;
        const detailedLogging = document.getElementById('setting-detailed-logging')?.checked;
        
        const recoveryTypes = {};
        ['tool-mismatch', 'invalid-structure', 'context-length', 'rate-limit', 'network'].forEach(type => {
            const checkbox = document.getElementById(`setting-recovery-${type}`);
            if (checkbox) {
                recoveryTypes[type.replace(/-/g, '_')] = checkbox.checked;
            }
        });
        
        SettingsManager.update('autoRecovery', {
            enabled,
            maxRetries,
            showNotifications,
            detailedLogging,
            recoveryTypes
        });
        
        ToastManager.show('Recovery settings saved', 'success');
        console.log('[Settings] Recovery settings updated');
    };

    window.saveDisplaySettings = function() {
        const showThinking = document.getElementById('setting-show-thinking')?.checked;
        const showToolDetails = document.getElementById('setting-show-tool-details')?.checked;
        const autoScroll = document.getElementById('setting-auto-scroll')?.checked;
        
        SettingsManager.update('display', {
            showThinking,
            showToolDetails,
            autoScroll
        });
        
        ToastManager.show('Display settings saved', 'success');
        console.log('[Settings] Display settings updated');
    };

    window.saveAdvancedSettings = function() {
        const debugMode = document.getElementById('setting-debug-mode')?.checked;
        const cacheResponses = document.getElementById('setting-cache-responses')?.checked;
        
        SettingsManager.update('advanced', {
            debugMode,
            cacheResponses
        });
        
        ToastManager.show('Advanced settings saved', 'success');
        console.log('[Settings] Advanced settings updated');
    };

    window.resetAllSettings = function() {
        if (confirm('Reset all settings to defaults? This cannot be undone.')) {
            localStorage.removeItem(SettingsManager.storageKey);
            loadSettingsIntoUI();
            ToastManager.show('All settings reset to defaults', 'success');
            console.log('[Settings] All settings reset');
        }
    };

    window.resetRecoveryStats = function() {
        SettingsManager.resetStatistics();
    };

    // ==================== PUBLIC API ====================

    window.isErrorRecoveryEnabled = function(errorType) {
        const enabled = SettingsManager.get('autoRecovery.enabled');
        if (!enabled) return false;
        
        if (errorType) {
            return SettingsManager.get(`autoRecovery.recoveryTypes.${errorType}`, true);
        }
        
        return true;
    };

    window.getMaxRetryAttempts = function() {
        return SettingsManager.get('autoRecovery.maxRetries', 3);
    };

    window.shouldShowRecoveryNotifications = function() {
        return SettingsManager.get('autoRecovery.showNotifications', true);
    };

    window.isDetailedLoggingEnabled = function() {
        return SettingsManager.get('autoRecovery.detailedLogging', true);
    };

    window.SettingsManager = SettingsManager;

    // ==================== TOOLTIP SYSTEM ====================

    function initializeTooltips() {
        document.querySelectorAll('.setting-label').forEach(label => {
            const settingId = label.closest('.setting-item')?.querySelector('input')?.id;
            if (settingId) {
                const key = settingId.replace('setting-', '');
                const info = SettingDescriptions[key];
                
                if (info) {
                    label.setAttribute('title', `${info.description}\n\nIMPACT: ${info.impact}\n\nEXAMPLE: ${info.example}`);
                    label.style.cursor = 'help';
                    label.classList.add('has-tooltip');
                }
            }
        });
    }

    // ==================== DYNAMIC HTML LOADING ====================

    function loadSettingsSidebarHTML() {
        console.log('[Settings v2] Checking for settings sidebar HTML...');
        
        // Check if HTML already exists in the page
        const existingSidebar = document.getElementById('settings-sidebar');
        if (existingSidebar) {
            console.log('[Settings v2] HTML already present in page - skipping fetch');
            
            // Initialize tooltips and load settings
            initializeTooltips();
            loadSettingsIntoUI();
            
            return Promise.resolve(true);
        }
        
        console.log('[Settings v2] Loading HTML from module folder...');
        
        return fetch('modules/settings-sidebar/settings-sidebar.html')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.text();
            })
            .then(html => {
                // Find or create container
                let container = document.getElementById('settings-sidebar-container');
                if (!container) {
                    container = document.createElement('div');
                    container.id = 'settings-sidebar-container';
                    document.body.appendChild(container);
                }
                
                // Insert HTML
                container.innerHTML = html;
                
                console.log('[Settings v2] HTML loaded successfully');
                
                // Initialize tooltips after HTML is loaded
                initializeTooltips();
                
                // Load current settings into UI
                loadSettingsIntoUI();
                
                return true; // Success
            })
            .catch(error => {
                console.error('[Settings v2] Failed to load HTML:', error);
                console.error('[Settings v2] Make sure settings-sidebar.html exists in modules/settings-sidebar/');
                throw error;
            });
    }

    // ==================== INITIALIZATION ====================

    document.addEventListener('DOMContentLoaded', function() {
        console.log('[Settings v2] DOM Content Loaded - initializing...');
        
        // Load settings sidebar HTML dynamically
        loadSettingsSidebarHTML();
        
        // Load initial settings
        const settings = SettingsManager.load();
        console.log('[Settings v2] Loaded settings:', settings);
    });

    // Add toast CSS if not already present
    if (!document.getElementById('settings-toast-styles')) {
        const style = document.createElement('style');
        style.id = 'settings-toast-styles';
        style.textContent = `
            .settings-toast {
                position: fixed;
                top: 80px;
                right: 20px;
                background: var(--bg-secondary, #1c1c1c);
                color: var(--text-primary, #e6e6e6);
                padding: 12px 20px;
                border-radius: 8px;
                border-left: 4px solid var(--accent-primary, #58a6ff);
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                display: flex;
                align-items: center;
                gap: 10px;
                opacity: 0;
                transform: translateX(400px);
                transition: all 0.3s ease;
                z-index: 10000;
                max-width: 350px;
            }
            
            .settings-toast.show {
                opacity: 1;
                transform: translateX(0);
            }
            
            .settings-toast-success {
                border-left-color: #3fb950;
            }
            
            .settings-toast-info {
                border-left-color: #58a6ff;
            }
            
            .settings-toast i {
                font-size: 18px;
            }
            
            .settings-toast-success i {
                color: #3fb950;
            }
            
            .has-tooltip {
                text-decoration: underline dotted;
                text-underline-offset: 3px;
            }
        `;
        document.head.appendChild(style);
    }

    console.log('[Settings v2] Settings sidebar module loaded successfully');

})();
