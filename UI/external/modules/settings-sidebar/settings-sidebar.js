/**
 * FILE: UI/external/modules/settings-sidebar/settings-sidebar.js
 * PURPOSE: Settings Sidebar Module - Enhanced error recovery and tracking
 * 
 * DEPENDENCIES:
 * - UI/js/module-base.js (BaseModule class)
 * 
 * EXPORTS:
 * - SettingsSidebarModule class (extends BaseModule)
 * - window.settingsModule instance
 * 
 * FEATURES:
 * - Error Recovery Configuration (enable/disable, types, retries)
 * - Error Tracking & Logging (detailed logs, timeline, effectiveness)
 * - Display Preferences (thinking process, tool details, auto-scroll)
 * - Advanced Settings (debug mode, caching)
 * - Statistics Dashboard (total/successful/failed recoveries)
 * - Recovery Timeline Visualization
 * - Effectiveness Metrics & Analytics
 * 
 * LAST MODIFIED: 2025-11-23 - Enhanced with error tracking capabilities
 */

console.log('[Settings Sidebar] Module loading...');

class SettingsSidebarModule extends BaseModule {
    constructor(moduleId) {
        super(moduleId);

        // Configuration
        this.apiEndpoint = '/api/settings';
        this.backendUrl = 'http://localhost:5001';

        // State management
        this.currentTab = 'recovery';
        this.settings = null;
        this.errorLogs = [];
        this.recoveryTimeline = [];
        this.maxErrorLogs = 100; // Keep last 100 error logs

        // Settings manager (internal utility)
        this.settingsManager = {
            defaults: {
                autoRecovery: {
                    enabled: true,
                    toolMismatch: true,
                    invalidStructure: true,
                    contextLength: true,
                    rateLimit: true,
                    network: true,
                    maxRetries: 3,
                    showNotifications: true,
                    detailedLogging: true
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
                    totalRecoveries: 0,
                    successfulRecoveries: 0,
                    failedRecoveries: 0,
                    lastRecovery: null,
                    byErrorType: {
                        tool_use_mismatch: { total: 0, successful: 0, failed: 0 },
                        invalid_message_structure: { total: 0, successful: 0, failed: 0 },
                        context_length_exceeded: { total: 0, successful: 0, failed: 0 },
                        rate_limit_exceeded: { total: 0, successful: 0, failed: 0 },
                        network_error: { total: 0, successful: 0, failed: 0 }
                    }
                }
            },

            load() {
                const stored = localStorage.getItem('aiAgentSettings');
                if (stored) {
                    try {
                        const parsed = JSON.parse(stored);
                        // Merge with defaults to ensure new fields exist
                        return this.mergeWithDefaults(parsed);
                    } catch (e) {
                        console.error('[Settings] Failed to parse settings:', e);
                        return this.defaults;
                    }
                }
                return this.defaults;
            },

            mergeWithDefaults(settings) {
                const merged = JSON.parse(JSON.stringify(this.defaults));
                
                // Deep merge
                const deepMerge = (target, source) => {
                    for (const key in source) {
                        if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
                            target[key] = target[key] || {};
                            deepMerge(target[key], source[key]);
                        } else {
                            target[key] = source[key];
                        }
                    }
                    return target;
                };

                return deepMerge(merged, settings);
            },

            save(settings) {
                try {
                    localStorage.setItem('aiAgentSettings', JSON.stringify(settings));
                    console.log('[Settings] Settings saved');
                } catch (e) {
                    console.error('[Settings] Failed to save settings:', e);
                }
            },

            get(path, defaultValue = undefined) {
                const settings = this.load();
                const keys = path.split('.');
                let value = settings;
                for (const key of keys) {
                    if (value && value[key] !== undefined) {
                        value = value[key];
                    } else {
                        return defaultValue;
                    }
                }
                return value;
            },

            update(path, value) {
                const settings = this.load();
                const keys = path.split('.');
                let current = settings;
                for (let i = 0; i < keys.length - 1; i++) {
                    current = current[keys[i]];
                }
                current[keys[keys.length - 1]] = value;
                this.save(settings);
            },

            recordRecovery(errorType, success) {
                const settings = this.load();
                settings.statistics.totalRecoveries++;
                if (success) {
                    settings.statistics.successfulRecoveries++;
                } else {
                    settings.statistics.failedRecoveries++;
                }
                settings.statistics.lastRecovery = new Date().toISOString();

                // Record by error type
                if (errorType && settings.statistics.byErrorType[errorType]) {
                    settings.statistics.byErrorType[errorType].total++;
                    if (success) {
                        settings.statistics.byErrorType[errorType].successful++;
                    } else {
                        settings.statistics.byErrorType[errorType].failed++;
                    }
                }

                this.save(settings);
            }
        };

        // Error log manager
        this.errorLogManager = {
            load() {
                const stored = localStorage.getItem('aiAgentErrorLogs');
                if (stored) {
                    try {
                        return JSON.parse(stored);
                    } catch (e) {
                        console.error('[Error Logs] Failed to parse error logs:', e);
                        return [];
                    }
                }
                return [];
            },

            save(logs) {
                try {
                    localStorage.setItem('aiAgentErrorLogs', JSON.stringify(logs));
                } catch (e) {
                    console.error('[Error Logs] Failed to save error logs:', e);
                }
            },

            add(errorLog) {
                const logs = this.load();
                logs.unshift(errorLog); // Add to beginning
                
                // Keep only last 100 logs
                if (logs.length > 100) {
                    logs.splice(100);
                }
                
                this.save(logs);
                return logs;
            },

            clear() {
                this.save([]);
            }
        };
    }

    async initialize() {
        console.log('[Settings Sidebar] Initializing...');

        // Initialize from BaseModule
        await super.initialize();

        // Load settings
        this.settings = this.settingsManager.load();
        this.errorLogs = this.errorLogManager.load();

        // Initialize sub-tabs
        await this.initializeSubTabs();

        // Apply module colors
        this.applyModuleColors();

        console.log('[Settings Sidebar] Module ready');
    }

    async initializeSubTabs() {
        console.log('[Settings Sidebar] Initializing sub-tabs...');

        // Recovery Tab
        this.subTabs.set('recovery', async () => {
            const container = document.getElementById(`${this.moduleId}-subtab-recovery`);
            if (!container) return;

            container.innerHTML = this.renderRecoveryTab();
            this.setupRecoveryEventListeners();
            this.loadSettingsIntoUI();
        });

        // Error Tracking Tab (NEW - Enhanced)
        this.subTabs.set('tracking', async () => {
            const container = document.getElementById(`${this.moduleId}-subtab-tracking`);
            if (!container) return;

            container.innerHTML = this.renderTrackingTab();
            this.setupTrackingEventListeners();
            this.refreshTrackingData();
        });

        // Display Tab
        this.subTabs.set('display', async () => {
            const container = document.getElementById(`${this.moduleId}-subtab-display`);
            if (!container) return;

            container.innerHTML = this.renderDisplayTab();
            this.setupDisplayEventListeners();
            this.loadSettingsIntoUI();
        });

        // Advanced Tab
        this.subTabs.set('advanced', async () => {
            const container = document.getElementById(`${this.moduleId}-subtab-advanced`);
            if (!container) return;

            container.innerHTML = this.renderAdvancedTab();
            this.setupAdvancedEventListeners();
            this.loadSettingsIntoUI();
        });

        // Load default tab
        await this.switchSubTab(this.activeSubTab || 'recovery');
    }

    // ==================== RECOVERY TAB ====================

    renderRecoveryTab() {
        const settings = this.settingsManager.load();
        const stats = settings.statistics;

        // Calculate success rate
        const successRate = stats.totalRecoveries > 0 
            ? ((stats.successfulRecoveries / stats.totalRecoveries) * 100).toFixed(1)
            : 0;

        return `
            <div class="settings-tab-content">
                <!-- Statistics Dashboard -->
                <div class="settings-section">
                    <div class="settings-section-header">
                        <i class="fas fa-chart-bar"></i>
                        <span>Recovery Statistics</span>
                    </div>
                    <div class="stats-grid">
                        <div class="stat-card stat-total">
                            <div class="stat-icon"><i class="fas fa-sync-alt"></i></div>
                            <div class="stat-content">
                                <div class="stat-value" id="stat-total-recoveries">${stats.totalRecoveries}</div>
                                <div class="stat-label">Total Recoveries</div>
                            </div>
                        </div>
                        <div class="stat-card stat-success">
                            <div class="stat-icon"><i class="fas fa-check-circle"></i></div>
                            <div class="stat-content">
                                <div class="stat-value" id="stat-successful-recoveries">${stats.successfulRecoveries}</div>
                                <div class="stat-label">Successful</div>
                            </div>
                        </div>
                        <div class="stat-card stat-failed">
                            <div class="stat-icon"><i class="fas fa-times-circle"></i></div>
                            <div class="stat-content">
                                <div class="stat-value" id="stat-failed-recoveries">${stats.failedRecoveries}</div>
                                <div class="stat-label">Failed</div>
                            </div>
                        </div>
                        <div class="stat-card stat-rate">
                            <div class="stat-icon"><i class="fas fa-percentage"></i></div>
                            <div class="stat-content">
                                <div class="stat-value" id="stat-success-rate">${successRate}%</div>
                                <div class="stat-label">Success Rate</div>
                            </div>
                        </div>
                    </div>
                    <div class="stat-meta">
                        <i class="fas fa-clock"></i>
                        Last Recovery: <span id="stat-last-recovery">${stats.lastRecovery ? new Date(stats.lastRecovery).toLocaleString() : 'Never'}</span>
                    </div>
                    <button class="btn-secondary btn-sm" id="reset-statistics">
                        <i class="fas fa-redo"></i> Reset Statistics
                    </button>
                </div>

                <!-- Master Toggle -->
                <div class="settings-section">
                    <div class="settings-section-header">
                        <i class="fas fa-shield-alt"></i>
                        <span>Automatic Error Recovery</span>
                    </div>
                    <div class="settings-section-description">
                        Control how the system handles API errors and connection issues automatically.
                    </div>

                    <div class="setting-item setting-toggle-master">
                        <div class="setting-info">
                            <div class="setting-label">
                                <i class="fas fa-power-off"></i>
                                Enable Auto-Recovery
                            </div>
                            <div class="setting-description">
                                Master switch for automatic error recovery system
                            </div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="setting-auto-recovery-enabled" ${settings.autoRecovery.enabled ? 'checked' : ''}>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                </div>

                <!-- Recovery Types -->
                <div class="settings-section">
                    <div class="settings-section-header">
                        <i class="fas fa-list-check"></i>
                        <span>Recovery Types</span>
                    </div>

                    ${this.renderRecoveryTypeToggle('tool-mismatch', 'Tool Use Mismatch', 'Fixes orphaned tool_result blocks without matching tool_use', settings.autoRecovery.toolMismatch)}
                    ${this.renderRecoveryTypeToggle('invalid-structure', 'Invalid Message Structure', 'Fixes thinking blocks in wrong position', settings.autoRecovery.invalidStructure)}
                    ${this.renderRecoveryTypeToggle('context-length', 'Context Length Recovery', 'Automatically trims conversation when too large', settings.autoRecovery.contextLength)}
                    ${this.renderRecoveryTypeToggle('rate-limit', 'Rate Limit Recovery', 'Waits and retries when API rate limit is hit', settings.autoRecovery.rateLimit)}
                    ${this.renderRecoveryTypeToggle('network', 'Network Error Recovery', 'Retries on network failures (timeouts, resets)', settings.autoRecovery.network)}
                </div>

                <!-- Configuration -->
                <div class="settings-section">
                    <div class="settings-section-header">
                        <i class="fas fa-cogs"></i>
                        <span>Recovery Configuration</span>
                    </div>

                    <div class="setting-item">
                        <div class="setting-info">
                            <div class="setting-label">
                                <i class="fas fa-redo"></i>
                                Maximum Retry Attempts
                            </div>
                            <div class="setting-description">
                                How many times to retry before giving up (1-5)
                            </div>
                        </div>
                        <input type="number" id="setting-max-retries" class="setting-input" min="1" max="5" value="${settings.autoRecovery.maxRetries}">
                    </div>

                    <div class="setting-item">
                        <div class="setting-info">
                            <div class="setting-label">
                                <i class="fas fa-bell"></i>
                                Show Recovery Notifications
                            </div>
                            <div class="setting-description">
                                Display toast notification when recovery succeeds
                            </div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="setting-show-recovery-notifications" ${settings.autoRecovery.showNotifications ? 'checked' : ''}>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>

                    <div class="setting-item">
                        <div class="setting-info">
                            <div class="setting-label">
                                <i class="fas fa-file-alt"></i>
                                Detailed Logging
                            </div>
                            <div class="setting-description">
                                Log full error context and recovery steps to console
                            </div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="setting-detailed-logging" ${settings.autoRecovery.detailedLogging ? 'checked' : ''}>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                </div>

                <div class="settings-actions">
                    <button class="btn-primary" id="save-recovery-settings">
                        <i class="fas fa-save"></i> Save Settings
                    </button>
                </div>
            </div>
        `;
    }

    renderRecoveryTypeToggle(id, label, description, checked) {
        return `
            <div class="setting-item">
                <div class="setting-info">
                    <div class="setting-label">
                        <i class="fas fa-shield-check"></i>
                        ${label}
                    </div>
                    <div class="setting-description">${description}</div>
                </div>
                <label class="toggle-switch">
                    <input type="checkbox" id="setting-recovery-${id}" ${checked ? 'checked' : ''}>
                    <span class="toggle-slider"></span>
                </label>
            </div>
        `;
    }

    setupRecoveryEventListeners() {
        const saveBtn = document.getElementById('save-recovery-settings');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveRecoverySettings());
        }

        const resetBtn = document.getElementById('reset-statistics');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetStatistics());
        }

        // Master toggle controls all recovery type toggles
        const masterToggle = document.getElementById('setting-auto-recovery-enabled');
        if (masterToggle) {
            masterToggle.addEventListener('change', (e) => this.toggleRecoveryTypes(e.target.checked));
            // Set initial state
            this.toggleRecoveryTypes(masterToggle.checked);
        }
    }

    toggleRecoveryTypes(enabled) {
        // Get all recovery type toggles and related inputs
        const toggleIds = [
            'setting-recovery-tool-mismatch',
            'setting-recovery-invalid-structure',
            'setting-recovery-context-length',
            'setting-recovery-rate-limit',
            'setting-recovery-network',
            'setting-max-retries',
            'setting-show-recovery-notifications',
            'setting-detailed-logging'
        ];

        toggleIds.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.disabled = !enabled;
                
                // Add visual feedback for disabled state
                const toggleSwitch = element.closest('.toggle-switch') || element.closest('.setting-item');
                if (toggleSwitch) {
                    if (!enabled) {
                        toggleSwitch.style.opacity = '0.5';
                        toggleSwitch.style.pointerEvents = 'none';
                    } else {
                        toggleSwitch.style.opacity = '1';
                        toggleSwitch.style.pointerEvents = 'auto';
                    }
                }
            }
        });
    }

    saveRecoverySettings() {
        const settings = this.settingsManager.load();

        settings.autoRecovery.enabled = document.getElementById('setting-auto-recovery-enabled')?.checked || false;
        settings.autoRecovery.toolMismatch = document.getElementById('setting-recovery-tool-mismatch')?.checked || false;
        settings.autoRecovery.invalidStructure = document.getElementById('setting-recovery-invalid-structure')?.checked || false;
        settings.autoRecovery.contextLength = document.getElementById('setting-recovery-context-length')?.checked || false;
        settings.autoRecovery.rateLimit = document.getElementById('setting-recovery-rate-limit')?.checked || false;
        settings.autoRecovery.network = document.getElementById('setting-recovery-network')?.checked || false;
        settings.autoRecovery.maxRetries = parseInt(document.getElementById('setting-max-retries')?.value) || 3;
        settings.autoRecovery.showNotifications = document.getElementById('setting-show-recovery-notifications')?.checked || false;
        settings.autoRecovery.detailedLogging = document.getElementById('setting-detailed-logging')?.checked || false;

        this.settingsManager.save(settings);
        this.showToast('Recovery settings saved successfully', 'success');
    }

    resetStatistics() {
        if (!confirm('Are you sure you want to reset all recovery statistics? This cannot be undone.')) {
            return;
        }

        const settings = this.settingsManager.load();
        settings.statistics = {
            totalRecoveries: 0,
            successfulRecoveries: 0,
            failedRecoveries: 0,
            lastRecovery: null,
            byErrorType: {
                tool_use_mismatch: { total: 0, successful: 0, failed: 0 },
                invalid_message_structure: { total: 0, successful: 0, failed: 0 },
                context_length_exceeded: { total: 0, successful: 0, failed: 0 },
                rate_limit_exceeded: { total: 0, successful: 0, failed: 0 },
                network_error: { total: 0, successful: 0, failed: 0 }
            }
        };
        this.settingsManager.save(settings);

        // Refresh UI
        document.getElementById('stat-total-recoveries').textContent = '0';
        document.getElementById('stat-successful-recoveries').textContent = '0';
        document.getElementById('stat-failed-recoveries').textContent = '0';
        document.getElementById('stat-success-rate').textContent = '0%';
        document.getElementById('stat-last-recovery').textContent = 'Never';

        this.showToast('Statistics reset successfully', 'success');
    }

    // ==================== ERROR TRACKING TAB (NEW - ENHANCED) ====================

    renderTrackingTab() {
        const logs = this.errorLogManager.load();
        const settings = this.settingsManager.load();
        const stats = settings.statistics.byErrorType;

        return `
            <div class="settings-tab-content">
                <!-- Error Type Statistics -->
                <div class="settings-section">
                    <div class="settings-section-header">
                        <i class="fas fa-chart-pie"></i>
                        <span>Errors by Type</span>
                    </div>
                    <div class="error-type-stats">
                        ${this.renderErrorTypeStat('Tool Mismatch', 'tool_use_mismatch', stats.tool_use_mismatch)}
                        ${this.renderErrorTypeStat('Invalid Structure', 'invalid_message_structure', stats.invalid_message_structure)}
                        ${this.renderErrorTypeStat('Context Length', 'context_length_exceeded', stats.context_length_exceeded)}
                        ${this.renderErrorTypeStat('Rate Limit', 'rate_limit_exceeded', stats.rate_limit_exceeded)}
                        ${this.renderErrorTypeStat('Network Error', 'network_error', stats.network_error)}
                    </div>
                </div>

                <!-- Recovery Timeline -->
                <div class="settings-section">
                    <div class="settings-section-header">
                        <i class="fas fa-clock"></i>
                        <span>Recovery Timeline</span>
                        <button class="btn-secondary btn-sm ml-auto" id="refresh-timeline">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                    </div>
                    <div id="recovery-timeline" class="recovery-timeline">
                        ${logs.length === 0 ? '<div class="empty-state">No error logs recorded yet</div>' : this.renderTimelineItems(logs.slice(0, 20))}
                    </div>
                </div>

                <!-- Error Logs -->
                <div class="settings-section">
                    <div class="settings-section-header">
                        <i class="fas fa-list"></i>
                        <span>Recent Error Logs (Last ${logs.length})</span>
                        <button class="btn-secondary btn-sm ml-auto" id="clear-error-logs">
                            <i class="fas fa-trash"></i> Clear Logs
                        </button>
                    </div>
                    <div class="error-logs-list">
                        ${logs.length === 0 ? '<div class="empty-state">No error logs available</div>' : this.renderErrorLogsList(logs.slice(0, 50))}
                    </div>
                </div>

                <!-- Effectiveness Metrics -->
                <div class="settings-section">
                    <div class="settings-section-header">
                        <i class="fas fa-tachometer-alt"></i>
                        <span>Effectiveness Metrics</span>
                    </div>
                    ${this.renderEffectivenessMetrics(stats)}
                </div>
            </div>
        `;
    }

    renderErrorTypeStat(label, type, stat) {
        const successRate = stat.total > 0 ? ((stat.successful / stat.total) * 100).toFixed(0) : 0;
        const statusClass = successRate >= 80 ? 'success' : successRate >= 50 ? 'warning' : 'error';

        return `
            <div class="error-type-stat">
                <div class="error-type-header">
                    <span class="error-type-label">${label}</span>
                    <span class="error-type-count">${stat.total}</span>
                </div>
                <div class="error-type-bar">
                    <div class="error-type-success" style="width: ${successRate}%"></div>
                    <div class="error-type-failed" style="width: ${100 - successRate}%"></div>
                </div>
                <div class="error-type-details">
                    <span class="success-count"><i class="fas fa-check"></i> ${stat.successful}</span>
                    <span class="failed-count"><i class="fas fa-times"></i> ${stat.failed}</span>
                    <span class="success-rate ${statusClass}">${successRate}%</span>
                </div>
            </div>
        `;
    }

    renderTimelineItems(logs) {
        return logs.map(log => {
            const statusIcon = log.recovered ? 'fa-check-circle success' : 'fa-times-circle error';
            const statusText = log.recovered ? 'Recovered' : 'Failed';
            const timestamp = new Date(log.timestamp).toLocaleString();

            return `
                <div class="timeline-item">
                    <div class="timeline-icon"><i class="fas ${statusIcon}"></i></div>
                    <div class="timeline-content">
                        <div class="timeline-header">
                            <span class="timeline-type">${this.formatErrorType(log.errorType)}</span>
                            <span class="timeline-status ${log.recovered ? 'success' : 'failed'}">${statusText}</span>
                        </div>
                        <div class="timeline-message">${log.errorMessage || 'No message'}</div>
                        <div class="timeline-meta">
                            <span><i class="fas fa-clock"></i> ${timestamp}</span>
                            ${log.attemptNumber ? `<span><i class="fas fa-redo"></i> Attempt ${log.attemptNumber}</span>` : ''}
                            ${log.threadId ? `<span><i class="fas fa-comments"></i> Thread ${log.threadId}</span>` : ''}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderErrorLogsList(logs) {
        return `
            <table class="error-logs-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Type</th>
                        <th>Message</th>
                        <th>Status</th>
                        <th>Attempt</th>
                        <th>Thread</th>
                    </tr>
                </thead>
                <tbody>
                    ${logs.map(log => `
                        <tr class="${log.recovered ? 'recovered' : 'failed'}">
                            <td>${new Date(log.timestamp).toLocaleString()}</td>
                            <td><span class="error-type-badge">${this.formatErrorType(log.errorType)}</span></td>
                            <td class="error-message">${log.errorMessage || 'No message'}</td>
                            <td><span class="status-badge ${log.recovered ? 'success' : 'failed'}">${log.recovered ? 'Recovered' : 'Failed'}</span></td>
                            <td>${log.attemptNumber || 'N/A'}</td>
                            <td>${log.threadId || 'N/A'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    renderEffectivenessMetrics(stats) {
        const metrics = [
            { label: 'Tool Mismatch', ...stats.tool_use_mismatch },
            { label: 'Invalid Structure', ...stats.invalid_message_structure },
            { label: 'Context Length', ...stats.context_length_exceeded },
            { label: 'Rate Limit', ...stats.rate_limit_exceeded },
            { label: 'Network Error', ...stats.network_error }
        ];

        // Calculate overall metrics
        const totalAll = metrics.reduce((sum, m) => sum + m.total, 0);
        const successAll = metrics.reduce((sum, m) => sum + m.successful, 0);
        const overallRate = totalAll > 0 ? ((successAll / totalAll) * 100).toFixed(1) : 0;

        return `
            <div class="effectiveness-grid">
                <div class="effectiveness-card overall">
                    <div class="effectiveness-header">
                        <i class="fas fa-star"></i>
                        <span>Overall Effectiveness</span>
                    </div>
                    <div class="effectiveness-value">${overallRate}%</div>
                    <div class="effectiveness-details">
                        ${successAll} successful out of ${totalAll} attempts
                    </div>
                </div>
                
                ${metrics.map(m => {
                    const rate = m.total > 0 ? ((m.successful / m.total) * 100).toFixed(0) : 0;
                    const status = rate >= 80 ? 'excellent' : rate >= 60 ? 'good' : rate >= 40 ? 'fair' : 'poor';
                    return `
                        <div class="effectiveness-card ${status}">
                            <div class="effectiveness-header">
                                <span>${m.label}</span>
                            </div>
                            <div class="effectiveness-value">${rate}%</div>
                            <div class="effectiveness-details">
                                ${m.successful}/${m.total} successful
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }

    setupTrackingEventListeners() {
        const refreshBtn = document.getElementById('refresh-timeline');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshTrackingData());
        }

        const clearBtn = document.getElementById('clear-error-logs');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearErrorLogs());
        }
    }

    refreshTrackingData() {
        this.errorLogs = this.errorLogManager.load();
        
        // Reload tracking tab
        this.switchSubTab('tracking');
        
        this.showToast('Tracking data refreshed', 'success');
    }

    clearErrorLogs() {
        if (!confirm('Are you sure you want to clear all error logs? This cannot be undone.')) {
            return;
        }

        this.errorLogManager.clear();
        this.errorLogs = [];
        
        // Reload tracking tab
        this.switchSubTab('tracking');
        
        this.showToast('Error logs cleared', 'success');
    }

    formatErrorType(type) {
        const typeMap = {
            'tool_use_mismatch': 'Tool Mismatch',
            'invalid_message_structure': 'Invalid Structure',
            'context_length_exceeded': 'Context Length',
            'rate_limit_exceeded': 'Rate Limit',
            'network_error': 'Network Error'
        };
        return typeMap[type] || type;
    }

    // ==================== DISPLAY TAB ====================

    renderDisplayTab() {
        const settings = this.settingsManager.load();

        return `
            <div class="settings-tab-content">
                <div class="settings-section">
                    <div class="settings-section-header">
                        <i class="fas fa-eye"></i>
                        <span>Display Preferences</span>
                    </div>

                    <div class="setting-item">
                        <div class="setting-info">
                            <div class="setting-label">
                                <i class="fas fa-brain"></i>
                                Show Thinking Process
                            </div>
                            <div class="setting-description">
                                Display AI thinking blocks in chat messages
                            </div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="setting-show-thinking" ${settings.display.showThinking ? 'checked' : ''}>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>

                    <div class="setting-item">
                        <div class="setting-info">
                            <div class="setting-label">
                                <i class="fas fa-tools"></i>
                                Show Tool Details
                            </div>
                            <div class="setting-description">
                                Display tool execution details and results
                            </div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="setting-show-tool-details" ${settings.display.showToolDetails ? 'checked' : ''}>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>

                    <div class="setting-item">
                        <div class="setting-info">
                            <div class="setting-label">
                                <i class="fas fa-arrow-down"></i>
                                Auto-Scroll to Bottom
                            </div>
                            <div class="setting-description">
                                Automatically scroll to latest message
                            </div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="setting-auto-scroll" ${settings.display.autoScroll ? 'checked' : ''}>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                </div>

                <div class="settings-actions">
                    <button class="btn-primary" id="save-display-settings">
                        <i class="fas fa-save"></i> Save Settings
                    </button>
                </div>
            </div>
        `;
    }

    setupDisplayEventListeners() {
        const saveBtn = document.getElementById('save-display-settings');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveDisplaySettings());
        }
    }

    saveDisplaySettings() {
        const settings = this.settingsManager.load();

        settings.display.showThinking = document.getElementById('setting-show-thinking')?.checked || false;
        settings.display.showToolDetails = document.getElementById('setting-show-tool-details')?.checked || false;
        settings.display.autoScroll = document.getElementById('setting-auto-scroll')?.checked || false;

        this.settingsManager.save(settings);
        this.showToast('Display settings saved successfully', 'success');
    }

    // ==================== ADVANCED TAB ====================

    renderAdvancedTab() {
        const settings = this.settingsManager.load();

        return `
            <div class="settings-tab-content">
                <div class="settings-section">
                    <div class="settings-section-header">
                        <i class="fas fa-sliders-h"></i>
                        <span>Advanced Configuration</span>
                    </div>
                    <div class="settings-warning">
                        <i class="fas fa-exclamation-triangle"></i>
                        Warning: Modifying these settings may affect system performance and debugging capabilities.
                    </div>

                    <div class="setting-item">
                        <div class="setting-info">
                            <div class="setting-label">
                                <i class="fas fa-bug"></i>
                                Debug Mode
                            </div>
                            <div class="setting-description">
                                Enable detailed console logging for debugging
                            </div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="setting-debug-mode" ${settings.advanced.debugMode ? 'checked' : ''}>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>

                    <div class="setting-item">
                        <div class="setting-info">
                            <div class="setting-label">
                                <i class="fas fa-database"></i>
                                Cache API Responses
                            </div>
                            <div class="setting-description">
                                Cache API responses to improve performance
                            </div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="setting-cache-responses" ${settings.advanced.cacheResponses ? 'checked' : ''}>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                </div>

                <div class="settings-section">
                    <div class="settings-section-header">
                        <i class="fas fa-broom"></i>
                        <span>Data Management</span>
                    </div>
                    
                    <button class="btn-secondary" id="export-settings">
                        <i class="fas fa-download"></i> Export Settings
                    </button>
                    
                    <button class="btn-secondary" id="import-settings">
                        <i class="fas fa-upload"></i> Import Settings
                    </button>
                    
                    <button class="btn-danger" id="reset-all-settings">
                        <i class="fas fa-undo"></i> Reset All Settings
                    </button>
                </div>

                <div class="settings-actions">
                    <button class="btn-primary" id="save-advanced-settings">
                        <i class="fas fa-save"></i> Save Settings
                    </button>
                </div>
            </div>
        `;
    }

    setupAdvancedEventListeners() {
        const saveBtn = document.getElementById('save-advanced-settings');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveAdvancedSettings());
        }

        const exportBtn = document.getElementById('export-settings');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportSettings());
        }

        const importBtn = document.getElementById('import-settings');
        if (importBtn) {
            importBtn.addEventListener('click', () => this.importSettings());
        }

        const resetBtn = document.getElementById('reset-all-settings');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetAllSettings());
        }
    }

    saveAdvancedSettings() {
        const settings = this.settingsManager.load();

        settings.advanced.debugMode = document.getElementById('setting-debug-mode')?.checked || false;
        settings.advanced.cacheResponses = document.getElementById('setting-cache-responses')?.checked || false;

        this.settingsManager.save(settings);
        this.showToast('Advanced settings saved successfully', 'success');
    }

    exportSettings() {
        const settings = this.settingsManager.load();
        const dataStr = JSON.stringify(settings, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `ai-agent-settings-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        URL.revokeObjectURL(url);
        
        this.showToast('Settings exported successfully', 'success');
    }

    importSettings() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const settings = JSON.parse(event.target.result);
                    this.settingsManager.save(settings);
                    this.showToast('Settings imported successfully. Reloading...', 'success');
                    setTimeout(() => location.reload(), 1500);
                } catch (error) {
                    this.showToast('Failed to import settings: Invalid JSON', 'error');
                    console.error('Import error:', error);
                }
            };
            reader.readAsText(file);
        };
        input.click();
    }

    resetAllSettings() {
        if (!confirm('Are you sure you want to reset ALL settings to default? This cannot be undone.')) {
            return;
        }

        localStorage.removeItem('aiAgentSettings');
        localStorage.removeItem('aiAgentErrorLogs');
        
        this.showToast('All settings reset. Reloading...', 'success');
        setTimeout(() => location.reload(), 1500);
    }

    // ==================== UTILITY METHODS ====================

    loadSettingsIntoUI() {
        const settings = this.settingsManager.load();
        
        // This is called after tab content is rendered
        // Settings are already populated via template literals
    }

    applyModuleColors() {
        const style = document.createElement('style');
        style.textContent = `
            .module-${this.moduleId} .btn-primary {
                background-color: ${this.manifest.color};
                border-color: ${this.manifest.color};
            }
            .module-${this.moduleId} .btn-primary:hover {
                background-color: #7c3aed;
                border-color: #7c3aed;
            }
            .module-${this.moduleId} .stat-card {
                border-left: 3px solid ${this.manifest.color};
            }
        `;
        document.head.appendChild(style);
    }

    showToast(message, type = 'success') {
        // Use platform toast system if available
        if (window.showToast) {
            window.showToast(message, type);
        } else {
            console.log(`[Settings] ${type.toUpperCase()}: ${message}`);
        }
    }

    // ==================== PUBLIC API (Backward Compatibility) ====================

    isErrorRecoveryEnabled(errorType) {
        const enabled = this.settingsManager.get('autoRecovery.enabled');
        if (!enabled) return false;

        if (errorType) {
            const typeMap = {
                'tool_use_mismatch': 'toolMismatch',
                'invalid_message_structure': 'invalidStructure',
                'context_length_exceeded': 'contextLength',
                'rate_limit_exceeded': 'rateLimit',
                'network_error': 'network'
            };

            const settingKey = typeMap[errorType];
            return settingKey ? this.settingsManager.get(`autoRecovery.${settingKey}`, true) : true;
        }

        return true;
    }

    getMaxRetryAttempts() {
        return this.settingsManager.get('autoRecovery.maxRetries', 3);
    }

    shouldShowRecoveryNotifications() {
        return this.settingsManager.get('autoRecovery.showNotifications', true);
    }

    isDetailedLoggingEnabled() {
        return this.settingsManager.get('autoRecovery.detailedLogging', true);
    }

    recordRecovery(errorType, success) {
        this.settingsManager.recordRecovery(errorType, success);
        
        // Update statistics display if on recovery tab
        if (this.activeSubTab === 'recovery') {
            const settings = this.settingsManager.load();
            const stats = settings.statistics;
            const successRate = stats.totalRecoveries > 0 
                ? ((stats.successfulRecoveries / stats.totalRecoveries) * 100).toFixed(1)
                : 0;

            document.getElementById('stat-total-recoveries').textContent = stats.totalRecoveries;
            document.getElementById('stat-successful-recoveries').textContent = stats.successfulRecoveries;
            document.getElementById('stat-failed-recoveries').textContent = stats.failedRecoveries;
            document.getElementById('stat-success-rate').textContent = `${successRate}%`;
            document.getElementById('stat-last-recovery').textContent = new Date(stats.lastRecovery).toLocaleString();
        }
    }

    logError(errorType, errorMessage, recovered, attemptNumber, threadId) {
        const errorLog = {
            timestamp: new Date().toISOString(),
            errorType,
            errorMessage,
            recovered,
            attemptNumber,
            threadId
        };

        this.errorLogManager.add(errorLog);
    }

    // ==================== SIDEBAR CONTROL ====================

    open() {
        console.log('[Settings Sidebar] Opening sidebar...');
        const sidebar = document.getElementById('settings-sidebar');
        if (sidebar) {
            sidebar.classList.add('active');
            console.log('[Settings Sidebar] Sidebar opened');
        } else {
            console.error('[Settings Sidebar] Sidebar element not found!');
        }
    }

    close() {
        console.log('[Settings Sidebar] Closing sidebar...');
        const sidebar = document.getElementById('settings-sidebar');
        if (sidebar) {
            sidebar.classList.remove('active');
            console.log('[Settings Sidebar] Sidebar closed');
        } else {
            console.error('[Settings Sidebar] Sidebar element not found!');
        }
    }

    toggle() {
        const sidebar = document.getElementById('settings-sidebar');
        if (sidebar) {
            if (sidebar.classList.contains('active')) {
                this.close();
            } else {
                this.open();
            }
        }
    }

    // ==================== CLEANUP ====================

    cleanup() {
        super.cleanup();
    }
}

// Register module
if (typeof window.ModuleRegistry !== 'undefined') {
    window.ModuleRegistry['settings-sidebar'] = SettingsSidebarModule;
    console.log('[Settings Sidebar] Module registered');
}

// Create global instance for backward compatibility
window.settingsModule = null;

// Backward compatibility wrappers (temporary - 1 version)
window.isErrorRecoveryEnabled = (type) => window.settingsModule?.isErrorRecoveryEnabled(type);
window.getMaxRetryAttempts = () => window.settingsModule?.getMaxRetryAttempts();
window.shouldShowRecoveryNotifications = () => window.settingsModule?.shouldShowRecoveryNotifications();
window.isDetailedLoggingEnabled = () => window.settingsModule?.isDetailedLoggingEnabled();

// Global open/close functions for button onclick handlers
window.openSettingsSidebar = () => {
    console.log('[Settings] openSettingsSidebar called');
    if (window.settingsModule) {
        window.settingsModule.open();
    } else {
        console.error('[Settings] settingsModule not initialized!');
    }
};

window.closeSettingsSidebar = () => {
    console.log('[Settings] closeSettingsSidebar called');
    if (window.settingsModule) {
        window.settingsModule.close();
    } else {
        console.error('[Settings] settingsModule not initialized!');
    }
};

window.switchSettingsTab = (tabName) => {
    console.log('[Settings] switchSettingsTab called:', tabName);
    if (window.settingsModule) {
        window.settingsModule.switchSubTab(tabName);
    } else {
        console.error('[Settings] settingsModule not initialized!');
    }
};

console.log('[Settings Sidebar] Module loaded');
console.warn('[DEPRECATED] Global settings functions - use window.settingsModule instead');
