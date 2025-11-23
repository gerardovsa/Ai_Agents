// ==================== SETTINGS SIDEBAR FUNCTIONALITY ====================

// Settings State (stored in localStorage)
const SettingsManager = {
    // Default settings
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
            lastRecovery: null
        }
    },

    // Load settings from localStorage
    load() {
        const stored = localStorage.getItem('aiAgentSettings');
        if (stored) {
            try {
                return JSON.parse(stored);
            } catch (e) {
                console.error('[Settings] Failed to parse settings:', e);
                return this.defaults;
            }
        }
        return this.defaults;
    },

    // Save settings to localStorage
    save(settings) {
        try {
            localStorage.setItem('aiAgentSettings', JSON.stringify(settings));
            console.log('[Settings] Settings saved:', settings);
        } catch (e) {
            console.error('[Settings] Failed to save settings:', e);
        }
    },

    // Get specific setting
    get(path) {
        const settings = this.load();
        const keys = path.split('.');
        let value = settings;
        for (const key of keys) {
            value = value?.[key];
        }
        return value;
    },

    // Set specific setting
    set(path, value) {
        const settings = this.load();
        const keys = path.split('.');
        let obj = settings;
        for (let i = 0; i < keys.length - 1; i++) {
            obj = obj[keys[i]];
        }
        obj[keys[keys.length - 1]] = value;
        this.save(settings);
    },

    // Increment recovery statistics
    recordRecovery(success) {
        const settings = this.load();
        settings.statistics.totalRecoveries++;
        if (success) {
            settings.statistics.successfulRecoveries++;
        } else {
            settings.statistics.failedRecoveries++;
        }
        settings.statistics.lastRecovery = new Date().toISOString();
        this.save(settings);
        this.updateStatisticsDisplay();
    },

    // Update statistics display
    updateStatisticsDisplay() {
        const stats = this.get('statistics');
        const totalEl = document.getElementById('stat-total-recoveries');
        const successEl = document.getElementById('stat-success-rate');
        const lastEl = document.getElementById('stat-last-recovery');

        if (totalEl) {
            totalEl.textContent = stats.totalRecoveries || 0;
        }

        if (successEl) {
            const successRate = stats.totalRecoveries > 0
                ? Math.round((stats.successfulRecoveries / stats.totalRecoveries) * 100)
                : 100;
            successEl.textContent = `${successRate}%`;
        }

        if (lastEl && stats.lastRecovery) {
            const date = new Date(stats.lastRecovery);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            
            if (diffMins < 1) {
                lastEl.textContent = 'Just now';
            } else if (diffMins < 60) {
                lastEl.textContent = `${diffMins} min ago`;
            } else if (diffMins < 1440) {
                const hours = Math.floor(diffMins / 60);
                lastEl.textContent = `${hours} hour${hours > 1 ? 's' : ''} ago`;
            } else {
                lastEl.textContent = date.toLocaleDateString();
            }
        } else if (lastEl) {
            lastEl.textContent = 'Never';
        }
    }
};

// Open settings sidebar
window.openSettingsSidebar = function() {
    const sidebar = document.getElementById('settings-sidebar');
    if (sidebar) {
        sidebar.classList.add('show');
        loadSettingsUI();
        console.log('[Settings] Sidebar opened');
    }
};

// Close settings sidebar
window.closeSettingsSidebar = function() {
    const sidebar = document.getElementById('settings-sidebar');
    if (sidebar) {
        sidebar.classList.remove('show');
        console.log('[Settings] Sidebar closed');
    }
};

// Switch settings tabs
window.switchSettingsTab = function(tabName) {
    // Update tab buttons
    document.querySelectorAll('#settings-sidebar .sidebar-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    const activeTab = document.querySelector(`#settings-sidebar .sidebar-tab[data-tab="${tabName}"]`);
    if (activeTab) {
        activeTab.classList.add('active');
    }

    // Update tab content
    document.querySelectorAll('#settings-sidebar .sidebar-tab-content').forEach(content => {
        content.classList.remove('active');
    });
    const activeContent = document.getElementById(`${tabName}-settings-tab`);
    if (activeContent) {
        activeContent.classList.add('active');
    }

    console.log(`[Settings] Switched to tab: ${tabName}`);
};

// Load settings into UI
function loadSettingsUI() {
    const settings = SettingsManager.load();

    // Recovery settings
    document.getElementById('setting-auto-recovery-enabled').checked = settings.autoRecovery.enabled;
    document.getElementById('setting-recovery-tool-mismatch').checked = settings.autoRecovery.toolMismatch;
    document.getElementById('setting-recovery-invalid-structure').checked = settings.autoRecovery.invalidStructure;
    document.getElementById('setting-recovery-context-length').checked = settings.autoRecovery.contextLength;
    document.getElementById('setting-recovery-rate-limit').checked = settings.autoRecovery.rateLimit;
    document.getElementById('setting-recovery-network').checked = settings.autoRecovery.network;
    document.getElementById('setting-max-retries').value = settings.autoRecovery.maxRetries;
    document.getElementById('setting-show-recovery-notifications').checked = settings.autoRecovery.showNotifications;
    document.getElementById('setting-detailed-logging').checked = settings.autoRecovery.detailedLogging;

    // Display settings
    document.getElementById('setting-show-thinking').checked = settings.display.showThinking;
    document.getElementById('setting-show-tool-details').checked = settings.display.showToolDetails;
    document.getElementById('setting-auto-scroll').checked = settings.display.autoScroll;

    // Advanced settings
    document.getElementById('setting-debug-mode').checked = settings.advanced.debugMode;
    document.getElementById('setting-cache-responses').checked = settings.advanced.cacheResponses;

    // Update disabled state of recovery options
    updateRecoveryOptionsState();

    // Update statistics
    SettingsManager.updateStatisticsDisplay();
}

// Save recovery settings
window.saveRecoverySettings = function() {
    const settings = SettingsManager.load();

    settings.autoRecovery.enabled = document.getElementById('setting-auto-recovery-enabled').checked;
    settings.autoRecovery.toolMismatch = document.getElementById('setting-recovery-tool-mismatch').checked;
    settings.autoRecovery.invalidStructure = document.getElementById('setting-recovery-invalid-structure').checked;
    settings.autoRecovery.contextLength = document.getElementById('setting-recovery-context-length').checked;
    settings.autoRecovery.rateLimit = document.getElementById('setting-recovery-rate-limit').checked;
    settings.autoRecovery.network = document.getElementById('setting-recovery-network').checked;
    settings.autoRecovery.maxRetries = parseInt(document.getElementById('setting-max-retries').value);
    settings.autoRecovery.showNotifications = document.getElementById('setting-show-recovery-notifications').checked;
    settings.autoRecovery.detailedLogging = document.getElementById('setting-detailed-logging').checked;

    SettingsManager.save(settings);
    updateRecoveryOptionsState();
    showSettingSavedFeedback();
    
    console.log('[Settings] Recovery settings saved:', settings.autoRecovery);
};

// Save display settings
window.saveDisplaySettings = function() {
    const settings = SettingsManager.load();

    settings.display.showThinking = document.getElementById('setting-show-thinking').checked;
    settings.display.showToolDetails = document.getElementById('setting-show-tool-details').checked;
    settings.display.autoScroll = document.getElementById('setting-auto-scroll').checked;

    SettingsManager.save(settings);
    showSettingSavedFeedback();
    
    console.log('[Settings] Display settings saved:', settings.display);
};

// Save advanced settings
window.saveAdvancedSettings = function() {
    const settings = SettingsManager.load();

    settings.advanced.debugMode = document.getElementById('setting-debug-mode').checked;
    settings.advanced.cacheResponses = document.getElementById('setting-cache-responses').checked;

    SettingsManager.save(settings);
    showSettingSavedFeedback();
    
    console.log('[Settings] Advanced settings saved:', settings.advanced);
};

// Update recovery options disabled state
function updateRecoveryOptionsState() {
    const enabled = document.getElementById('setting-auto-recovery-enabled').checked;
    const recoveryOptions = document.getElementById('recovery-options');
    
    if (enabled) {
        recoveryOptions.classList.remove('disabled');
    } else {
        recoveryOptions.classList.add('disabled');
    }
}

// Show visual feedback when settings are saved
function showSettingSavedFeedback() {
    const items = document.querySelectorAll('.setting-item');
    items.forEach(item => {
        item.classList.add('saved');
        setTimeout(() => item.classList.remove('saved'), 600);
    });
}

// Reset recovery statistics
window.resetRecoveryStats = function() {
    if (confirm('Reset all recovery statistics? This cannot be undone.')) {
        const settings = SettingsManager.load();
        settings.statistics = {
            totalRecoveries: 0,
            successfulRecoveries: 0,
            failedRecoveries: 0,
            lastRecovery: null
        };
        SettingsManager.save(settings);
        SettingsManager.updateStatisticsDisplay();
        
        console.log('[Settings] Recovery statistics reset');
        
        if (typeof showNotification === 'function') {
            showNotification('Recovery statistics reset', 'info');
        }
    }
};

// Reset all settings to defaults
window.resetAllSettings = function() {
    if (confirm('Reset all settings to defaults? This cannot be undone.')) {
        SettingsManager.save(SettingsManager.defaults);
        loadSettingsUI();
        
        console.log('[Settings] All settings reset to defaults');
        
        if (typeof showNotification === 'function') {
            showNotification('All settings reset to defaults', 'info');
        }
    }
};

// Check if error recovery is enabled
window.isErrorRecoveryEnabled = function(errorType) {
    const settings = SettingsManager.load();
    
    // Master switch
    if (!settings.autoRecovery.enabled) {
        console.log('[Settings] Error recovery disabled globally');
        return false;
    }

    // Check specific error type
    const typeMap = {
        'tool_use_mismatch': 'toolMismatch',
        'invalid_message_structure': 'invalidStructure',
        'context_length_exceeded': 'contextLength',
        'rate_limit_exceeded': 'rateLimit',
        'network_error': 'network'
    };

    const settingKey = typeMap[errorType];
    if (settingKey && !settings.autoRecovery[settingKey]) {
        console.log(`[Settings] Error recovery disabled for type: ${errorType}`);
        return false;
    }

    return true;
};

// Get max retry attempts
window.getMaxRetryAttempts = function() {
    return SettingsManager.get('autoRecovery.maxRetries') || 3;
};

// Check if recovery notifications should be shown
window.shouldShowRecoveryNotifications = function() {
    return SettingsManager.get('autoRecovery.showNotifications');
};

// Check if detailed logging is enabled
window.isDetailedLoggingEnabled = function() {
    return SettingsManager.get('autoRecovery.detailedLogging');
};

// Initialize settings on page load
document.addEventListener('DOMContentLoaded', function() {
    // Load initial settings
    const settings = SettingsManager.load();
    console.log('[Settings] Loaded settings:', settings);
    
    // Update statistics display if sidebar is visible
    SettingsManager.updateStatisticsDisplay();
});

// Export for use in error recovery
window.SettingsManager = SettingsManager;

console.log('[Settings] Settings sidebar module loaded');
