/**
 * FILE: UI/modules_internal/notifications/notification-ui.js
 * PURPOSE: Render notification panel UI
 * 
 * FEATURES:
 * - Create notification panel structure
 * - Render individual notifications
 * - Filter buttons with counts
 * - Search input
 * - Empty state display
 * 
 * DEPENDENCIES:
 * - notification-center.js (state management)
 * - notification-events.js (type metadata)
 * 
 * EXPORTS:
 * - NotificationUI.init()
 * - NotificationUI.render(notifications)
 * - NotificationUI.updateFilters()
 * 
 * LAST MODIFIED: 2024-12-14 - Initial creation
 */

const NotificationUI = {
    isInitialized: false,

    /**
     * Initialize notification UI
     */
    init() {
        if (this.isInitialized) {
            console.warn('[NotificationUI] Already initialized');
            return;
        }

        console.log('[NotificationUI] Creating notification panel...');

        // Create panel structure
        this.createPanel();

        // Setup event listeners
        this.setupEventListeners();

        this.isInitialized = true;
        console.log('[NotificationUI] Initialized');
    },

    /**
     * Create notification panel HTML structure
     */
    createPanel() {
        // Remove existing panel if present
        const existing = document.getElementById('unified-notification-panel');
        if (existing) {
            existing.remove();
        }

        // Create panel element
        const panel = document.createElement('div');
        panel.id = 'unified-notification-panel';
        panel.className = 'notification-panel collapsed';
        panel.innerHTML = `
            <!-- Header -->
            <div class="notification-header">
                <h3>
                    <i class="fas fa-bell"></i>
                    Notifications
                </h3>
                <div class="notification-actions">
                    <button class="notif-action-btn" onclick="NotificationUI.toggleSettings()" title="Settings">
                        <i class="fas fa-cog"></i>
                    </button>
                    <button class="notif-action-btn" onclick="NotificationCenter.markAllAsRead()" title="Mark all as read">
                        <i class="fas fa-check-double"></i>
                    </button>
                    <button class="notif-action-btn" onclick="NotificationCenter.clear()" title="Clear all">
                        <i class="fas fa-trash"></i>
                    </button>
                    <button class="notif-action-btn" onclick="NotificationCenter.closePanel()" title="Close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            
            <!-- Settings Panel (Collapsible) -->
            <div class="notification-settings" id="notification-settings" style="display: none;">
                <!-- Test Button -->
                <div class="settings-test-section">
                    <button class="test-notification-btn" onclick="NotificationUI.testNotification()">
                        <i class="fas fa-vial"></i> Test Notification
                    </button>
                </div>

                <!-- Global Settings -->
                <div class="settings-section-title">
                    <i class="fas fa-cog"></i> Global Settings
                </div>
                <div class="settings-group">
                    <label class="setting-item">
                        <div class="setting-label">
                            <i class="fas fa-volume-up"></i>
                            <span>Master Sound</span>
                        </div>
                        <input type="checkbox" id="notif-sound-toggle" checked onchange="NotificationUI.saveSetting('notificationSoundEnabled', this.checked)">
                    </label>
                    
                    <label class="setting-item">
                        <div class="setting-label">
                            <i class="fas fa-music"></i>
                            <span>Sound Type</span>
                        </div>
                        <div class="sound-selector">
                            <select id="notif-sound-type" onchange="NotificationUI.saveSetting('notificationSoundType', this.value)">
                                <option value="soft">Soft Beep</option>
                                <option value="classic">Classic</option>
                                <option value="alert">Alert</option>
                                <option value="chime">Chime</option>
                                <option value="ping">Ping</option>
                                <option value="bell">Bell</option>
                                <option value="bubble">Bubble</option>
                                <option value="chirp">Chirp</option>
                                <option value="pluck">Pluck</option>
                                <option value="drop">Drop</option>
                                <option value="rise">Rise</option>
                                <option value="wobble">Wobble</option>
                                <option value="beep">Beep</option>
                                <option value="boop">Boop</option>
                                <option value="click">Click</option>
                                <option value="pop">Pop</option>
                                <option value="whoosh">Whoosh</option>
                                <option value="ding">Ding</option>
                            </select>
                            <button class="preview-sound-btn" onclick="NotificationUI.previewSound()" title="Preview sound">
                                <i class="fas fa-play"></i>
                            </button>
                        </div>
                    </label>
                    
                    <label class="setting-item">
                        <div class="setting-label">
                            <i class="fas fa-volume-down"></i>
                            <span>Volume</span>
                            <span class="volume-value" id="volume-value">50%</span>
                        </div>
                        <input type="range" id="notif-volume" min="0" max="100" value="50" 
                               oninput="NotificationUI.updateVolume(this.value)" 
                               onchange="NotificationUI.saveSetting('notificationVolume', this.value)">
                    </label>
                    
                    <label class="setting-item">
                        <div class="setting-label">
                            <i class="fas fa-eye-slash"></i>
                            <span>Do Not Disturb</span>
                        </div>
                        <input type="checkbox" id="notif-dnd" onchange="NotificationUI.saveSetting('notificationDND', this.checked)">
                    </label>
                </div>

                <!-- Notification Type Controls -->
                <div class="settings-section-title">
                    <i class="fas fa-sliders-h"></i> Notification Type Controls
                </div>
                <div class="settings-group">
                    <!-- Message Notifications -->
                    <div class="notification-type-control">
                        <div class="type-control-header">
                            <i class="fas fa-comment"></i>
                            <span>Message Notifications</span>
                        </div>
                        <div class="type-control-actions">
                            <button class="control-btn" onclick="NotificationUI.toggleTypeVisibility('message')" title="Show/Hide in Panel">
                                <i class="fas fa-eye" id="toggle-message-visibility"></i>
                            </button>
                            <button class="control-btn" onclick="NotificationUI.toggleTypeSound('message')" title="Sound On/Off">
                                <i class="fas fa-volume-up" id="toggle-message-sound"></i>
                            </button>
                            <button class="control-btn" onclick="NotificationUI.toggleTypeToast('message')" title="Toast On/Off">
                                <i class="fas fa-comment-dots" id="toggle-message-toast"></i>
                            </button>
                        </div>
                    </div>

                    <!-- Thread Notifications -->
                    <div class="notification-type-control">
                        <div class="type-control-header">
                            <i class="fas fa-tasks"></i>
                            <span>Thread Notifications</span>
                        </div>
                        <div class="type-control-actions">
                            <button class="control-btn" onclick="NotificationUI.toggleTypeVisibility('thread')" title="Show/Hide in Panel">
                                <i class="fas fa-eye" id="toggle-thread-visibility"></i>
                            </button>
                            <button class="control-btn" onclick="NotificationUI.toggleTypeSound('thread')" title="Sound On/Off">
                                <i class="fas fa-volume-up" id="toggle-thread-sound"></i>
                            </button>
                            <button class="control-btn" onclick="NotificationUI.toggleTypeToast('thread')" title="Toast On/Off">
                                <i class="fas fa-comment-dots" id="toggle-thread-toast"></i>
                            </button>
                        </div>
                    </div>

                    <!-- Agent Notifications -->
                    <div class="notification-type-control">
                        <div class="type-control-header">
                            <i class="fas fa-robot"></i>
                            <span>Agent Notifications</span>
                        </div>
                        <div class="type-control-actions">
                            <button class="control-btn" onclick="NotificationUI.toggleTypeVisibility('agent')" title="Show/Hide in Panel">
                                <i class="fas fa-eye" id="toggle-agent-visibility"></i>
                            </button>
                            <button class="control-btn" onclick="NotificationUI.toggleTypeSound('agent')" title="Sound On/Off">
                                <i class="fas fa-volume-up" id="toggle-agent-sound"></i>
                            </button>
                            <button class="control-btn" onclick="NotificationUI.toggleTypeToast('agent')" title="Toast On/Off">
                                <i class="fas fa-comment-dots" id="toggle-agent-toast"></i>
                            </button>
                        </div>
                    </div>

                    <!-- Synergy Notifications -->
                    <div class="notification-type-control">
                        <div class="type-control-header">
                            <i class="fas fa-network-wired"></i>
                            <span>Synergy Notifications</span>
                        </div>
                        <div class="type-control-actions">
                            <button class="control-btn" onclick="NotificationUI.toggleTypeVisibility('synergy')" title="Show/Hide in Panel">
                                <i class="fas fa-eye" id="toggle-synergy-visibility"></i>
                            </button>
                            <button class="control-btn" onclick="NotificationUI.toggleTypeSound('synergy')" title="Sound On/Off">
                                <i class="fas fa-volume-up" id="toggle-synergy-sound"></i>
                            </button>
                            <button class="control-btn" onclick="NotificationUI.toggleTypeToast('synergy')" title="Toast On/Off">
                                <i class="fas fa-comment-dots" id="toggle-synergy-toast"></i>
                            </button>
                        </div>
                    </div>

                    <!-- System Notifications -->
                    <div class="notification-type-control">
                        <div class="type-control-header">
                            <i class="fas fa-exclamation-triangle"></i>
                            <span>System Notifications</span>
                        </div>
                        <div class="type-control-actions">
                            <button class="control-btn" onclick="NotificationUI.toggleTypeVisibility('system')" title="Show/Hide in Panel">
                                <i class="fas fa-eye" id="toggle-system-visibility"></i>
                            </button>
                            <button class="control-btn" onclick="NotificationUI.toggleTypeSound('system')" title="Sound On/Off">
                                <i class="fas fa-volume-up" id="toggle-system-sound"></i>
                            </button>
                            <button class="control-btn" onclick="NotificationUI.toggleTypeToast('system')" title="Toast On/Off">
                                <i class="fas fa-comment-dots" id="toggle-system-toast"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Advanced Settings -->
                <div class="settings-section-title">
                    <i class="fas fa-tools"></i> Advanced Settings
                </div>
                <div class="settings-group">
                    <label class="setting-item">
                        <div class="setting-label">
                            <i class="fas fa-desktop"></i>
                            <span>Desktop Notifications</span>
                        </div>
                        <input type="checkbox" id="notif-desktop-toggle" onchange="NotificationUI.toggleDesktopNotifications(this.checked)">
                    </label>
                    
                    <label class="setting-item">
                        <div class="setting-label">
                            <i class="fas fa-filter"></i>
                            <span>Auto-dismiss after action</span>
                        </div>
                        <input type="checkbox" id="notif-auto-dismiss" checked onchange="NotificationUI.saveSetting('notificationAutoDismiss', this.checked)">
                    </label>
                    
                    <label class="setting-item">
                        <div class="setting-label">
                            <i class="fas fa-clock"></i>
                            <span>Notification retention</span>
                        </div>
                        <select id="notif-retention" onchange="NotificationUI.saveSetting('notificationRetentionDays', this.value)">
                            <option value="1">1 day</option>
                            <option value="3">3 days</option>
                            <option value="7" selected>7 days</option>
                            <option value="14">14 days</option>
                            <option value="30">30 days</option>
                        </select>
                    </label>
                </div>
            </div>
            
            <!-- Filters -->
            <div class="notification-filters">
                <button class="filter-btn active" data-filter="all" onclick="NotificationUI.setFilter('all')">
                    All <span class="filter-count">0</span>
                </button>
                <button class="filter-btn" data-filter="agent" onclick="NotificationUI.setFilter('agent')">
                    Agents <span class="filter-count">0</span>
                </button>
                <button class="filter-btn" data-filter="thread" onclick="NotificationUI.setFilter('thread')">
                    Threads <span class="filter-count">0</span>
                </button>
                <button class="filter-btn" data-filter="synergy" onclick="NotificationUI.setFilter('synergy')">
                    Synergy <span class="filter-count">0</span>
                </button>
                <button class="filter-btn" data-filter="system" onclick="NotificationUI.setFilter('system')">
                    System <span class="filter-count">0</span>
                </button>
            </div>
            
            <!-- Search -->
            <div class="notification-search-container">
                <i class="fas fa-search"></i>
                <input type="text" 
                       id="notification-search-input" 
                       class="notification-search" 
                       placeholder="Search notifications..."
                       oninput="NotificationUI.handleSearch(this.value)">
            </div>
            
            <!-- Notification List (Scrollable) -->
            <div class="notification-list" id="notification-list">
                <!-- Notifications rendered here -->
            </div>
        `;

        // Append to body
        document.body.appendChild(panel);

        console.log('[NotificationUI] Panel created');
    },

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Search input debounce
        let searchTimeout;
        const searchInput = document.getElementById('notification-search-input');

        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.handleSearch(e.target.value);
                }, 300);
            });
        }

        console.log('[NotificationUI] Event listeners setup');
    },

    /**
     * Set active filter
     * @param {string} filter - Filter category
     */
    setFilter(filter) {
        // Update button states
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === filter);
        });

        // Update NotificationCenter filter
        if (typeof NotificationCenter !== 'undefined') {
            NotificationCenter.currentFilter = filter;
            this.render(NotificationCenter.getFiltered());
        }

        console.log('[NotificationUI] Filter set to:', filter);
    },

    /**
     * Handle search input
     * @param {string} query - Search query
     */
    handleSearch(query) {
        if (typeof NotificationCenter !== 'undefined') {
            const results = NotificationCenter.search(query);
            this.render(results);
            console.log('[NotificationUI] Search:', query, '- Found:', results.length);
        }
    },

    /**
     * Render notifications
     * @param {Array} notifications - Array of notification objects
     */
    render(notifications) {
        const container = document.getElementById('notification-list');

        if (!container) {
            console.warn('[NotificationUI] Notification list container not found');
            return;
        }

        // Filter out notifications based on type visibility settings
        const visibleNotifications = notifications.filter(notif => {
            const category = notif.category || 'system';
            const isVisible = localStorage.getItem(`notif_${category}_visible`) !== 'false';
            return isVisible;
        });

        // Update filter counts
        this.updateFilterCounts();

        // Empty state
        if (visibleNotifications.length === 0) {
            container.innerHTML = this.renderEmptyState();
            return;
        }

        // Render notifications
        const html = visibleNotifications.map(notif => this.renderNotification(notif)).join('');
        container.innerHTML = html;

        console.log('[NotificationUI] Rendered', visibleNotifications.length, 'of', notifications.length, 'notifications');
    },

    /**
     * Render empty state
     * @returns {string} HTML string
     */
    renderEmptyState() {
        const hasSearch = NotificationCenter.currentSearch;
        const hasFilter = NotificationCenter.currentFilter !== 'all';

        if (hasSearch || hasFilter) {
            return `
                <div class="notification-empty-state">
                    <i class="fas fa-search" style="font-size: 48px; opacity: 0.3;"></i>
                    <p>No notifications found</p>
                    <p class="empty-state-hint">Try adjusting your filters or search</p>
                </div>
            `;
        }

        return `
            <div class="notification-empty-state">
                <i class="fas fa-bell-slash" style="font-size: 48px; opacity: 0.3;"></i>
                <p>No notifications yet</p>
                <p class="empty-state-hint">You'll be notified about important events</p>
            </div>
        `;
    },

    /**
     * Render individual notification
     * @param {Object} notif - Notification object
     * @returns {string} HTML string
     */
    renderNotification(notif) {
        const readClass = notif.read ? 'read' : 'unread';
        const severityClass = `severity-${notif.severity}`;
        const timeAgo = this.timeAgo(notif.timestamp);
        const clickHandler = notif.actionable ? `onclick="NotificationCenter.handleClick('${notif.id}')"` : '';
        const cursorStyle = notif.actionable ? 'cursor: pointer;' : '';

        // Build metadata tags
        const tags = this.buildMetadataTags(notif);

        return `
            <div class="notification-item ${readClass} ${severityClass}" 
                 data-id="${notif.id}" 
                 ${clickHandler}
                 style="${cursorStyle}">
                <div class="notif-icon ${notif.severity}">
                    <i class="fas ${notif.icon}"></i>
                </div>
                <div class="notif-content">
                    <div class="notif-header-row">
                        <div class="notif-title">${this.escapeHtml(notif.title)}</div>
                        <div class="notif-time">${timeAgo}</div>
                    </div>
                    <div class="notif-message">${this.escapeHtml(notif.message)}</div>
                    ${tags ? `<div class="notif-tags">${tags}</div>` : ''}
                </div>
                <div class="notif-actions">
                    ${!notif.read ? '<span class="unread-dot"></span>' : ''}
                    <button class="notif-action-btn" 
                            onclick="event.stopPropagation(); NotificationCenter.remove('${notif.id}')" 
                            title="Dismiss">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;
    },

    /**
     * Build metadata tags HTML
     * @param {Object} notif - Notification object
     * @returns {string} HTML string
     */
    buildMetadataTags(notif) {
        const tags = [];

        // Agent tag
        if (notif.metadata.agentId) {
            const agentName = this.getAgentName(notif.metadata.agentId);
            tags.push(`<span class="tag agent">${agentName}</span>`);
        }

        // Thread tag
        if (notif.metadata.threadId) {
            const threadName = notif.metadata.threadName || notif.metadata.threadId;
            tags.push(`<span class="tag thread">${this.escapeHtml(threadName)}</span>`);
        }

        // Synergy tag
        if (notif.metadata.sessionId) {
            tags.push(`<span class="tag synergy">Synergy</span>`);
        }

        // Message count tag
        if (notif.metadata.messageCount) {
            tags.push(`<span class="tag messages">${notif.metadata.messageCount} msgs</span>`);
        }

        return tags.join('');
    },

    /**
     * Toggle notification settings panel
     */
    toggleSettings() {
        const settingsPanel = document.getElementById('notification-settings');
        if (settingsPanel) {
            const isVisible = settingsPanel.style.display !== 'none';
            settingsPanel.style.display = isVisible ? 'none' : 'block';

            if (!isVisible) {
                // Load current settings
                this.loadSettings();
            }
        }
    },

    /**
     * Load settings from localStorage
     */
    loadSettings() {
        // Sound enabled
        const soundEnabled = localStorage.getItem('notificationSoundEnabled') !== 'false';
        const soundToggle = document.getElementById('notif-sound-toggle');
        if (soundToggle) soundToggle.checked = soundEnabled;

        // Sound type
        const soundType = localStorage.getItem('notificationSoundType') || 'soft';
        const soundTypeSelect = document.getElementById('notif-sound-type');
        if (soundTypeSelect) soundTypeSelect.value = soundType;

        // Volume
        const volume = localStorage.getItem('notificationVolume') || '50';
        const volumeSlider = document.getElementById('notif-volume');
        const volumeDisplay = document.getElementById('volume-value');
        if (volumeSlider) volumeSlider.value = volume;
        if (volumeDisplay) volumeDisplay.textContent = `${volume}%`;

        // Desktop notifications
        const desktopEnabled = localStorage.getItem('notificationDesktopEnabled') === 'true';
        const desktopToggle = document.getElementById('notif-desktop-toggle');
        if (desktopToggle) desktopToggle.checked = desktopEnabled;

        // Auto-dismiss
        const autoDismiss = localStorage.getItem('notificationAutoDismiss') !== 'false';
        const autoDismissToggle = document.getElementById('notif-auto-dismiss');
        if (autoDismissToggle) autoDismissToggle.checked = autoDismiss;

        // Retention days
        const retentionDays = localStorage.getItem('notificationRetentionDays') || '7';
        const retentionSelect = document.getElementById('notif-retention');
        if (retentionSelect) retentionSelect.value = retentionDays;

        // Do Not Disturb
        const dnd = localStorage.getItem('notificationDND') === 'true';
        const dndToggle = document.getElementById('notif-dnd');
        if (dndToggle) dndToggle.checked = dnd;

        // Load notification type visibility/sound states
        this.loadTypeControls();
    },

    /**
     * Load notification type control states
     */
    loadTypeControls() {
        const types = ['message', 'thread', 'agent', 'synergy', 'system'];

        types.forEach(type => {
            // Load visibility state
            const visible = localStorage.getItem(`notif_${type}_visible`) !== 'false';
            const visIcon = document.getElementById(`toggle-${type}-visibility`);
            if (visIcon) {
                visIcon.className = visible ? 'fas fa-eye' : 'fas fa-eye-slash';
                visIcon.style.color = visible ? '' : '#94a3b8';
            }

            // Load sound state
            const soundEnabled = localStorage.getItem(`notif_${type}_sound`) !== 'false';
            const soundIcon = document.getElementById(`toggle-${type}-sound`);
            if (soundIcon) {
                soundIcon.className = soundEnabled ? 'fas fa-volume-up' : 'fas fa-volume-mute';
                soundIcon.style.color = soundEnabled ? '' : '#94a3b8';
            }

            // Load toast state
            const toastEnabled = localStorage.getItem(`notif_${type}_toast`) !== 'false';
            const toastIcon = document.getElementById(`toggle-${type}-toast`);
            if (toastIcon) {
                toastIcon.className = toastEnabled ? 'fas fa-comment-dots' : 'fas fa-comment-slash';
                toastIcon.style.color = toastEnabled ? '' : '#94a3b8';
            }
        });
    },

    /**
     * Save a setting to localStorage
     * @param {string} key - Setting key
     * @param {any} value - Setting value
     */
    saveSetting(key, value) {
        localStorage.setItem(key, value);
        console.log(`[NotificationUI] Setting saved: ${key} = ${value}`);

        // Show feedback
        if (typeof showToast === 'function') {
            showToast('Setting saved', 'success');
        }
    },

    /**
     * Update volume display
     * @param {number} value - Volume value (0-100)
     */
    updateVolume(value) {
        const volumeDisplay = document.getElementById('volume-value');
        if (volumeDisplay) {
            volumeDisplay.textContent = `${value}%`;
        }
        console.log(`[NotificationUI] Volume updated: ${value}%`);
    },

    /**
     * Toggle desktop notifications
     * @param {boolean} enabled - Whether to enable desktop notifications
     */
    async toggleDesktopNotifications(enabled) {
        if (enabled) {
            if ('Notification' in window) {
                const permission = await Notification.requestPermission();
                if (permission === 'granted') {
                    localStorage.setItem('notificationDesktopEnabled', 'true');
                    console.log('[NotificationUI] Desktop notifications enabled');

                    // Show test notification
                    new Notification('Notifications Enabled', {
                        body: 'You will now receive desktop notifications',
                        icon: '/favicon.ico'
                    });
                } else {
                    // Permission denied
                    const desktopToggle = document.getElementById('notif-desktop-toggle');
                    if (desktopToggle) desktopToggle.checked = false;

                    if (typeof showToast === 'function') {
                        showToast('Desktop notifications permission denied', 'warning');
                    }
                }
            } else {
                if (typeof showToast === 'function') {
                    showToast('Desktop notifications not supported', 'error');
                }
            }
        } else {
            localStorage.setItem('notificationDesktopEnabled', 'false');
            console.log('[NotificationUI] Desktop notifications disabled');
        }
    },

    /**
     * Get agent name from ID
     * @param {number} agentId - Agent ID
     * @returns {string} Agent name
     */
    getAgentName(agentId) {
        const names = {
            1: 'Alpha', 2: 'Bravo', 3: 'Charlie', 4: 'Delta',
            5: 'Echo', 6: 'Foxtrot', 7: 'Golf', 8: 'Hotel'
        };
        return names[agentId] || `Agent ${agentId}`;
    },

    /**
     * Test notification with current settings
     */
    testNotification() {
        const soundType = localStorage.getItem('notificationSoundType') || 'soft';
        const severities = ['info', 'success', 'warning', 'error'];
        const randomSeverity = severities[Math.floor(Math.random() * severities.length)];

        if (typeof NotificationCenter !== 'undefined' && NotificationCenter.add) {
            NotificationCenter.add({
                type: 'MESSAGE_COMPLETE',
                message: `Test notification with ${soundType} sound (${randomSeverity})`,
                severity: randomSeverity,
                metadata: {
                    agentId: 1,
                    test: true
                }
            });
        }

        if (typeof showToast === 'function') {
            showToast(`Test notification sent! (${soundType} sound)`, 'info');
        }
    },

    /**
     * Preview current sound selection
     */
    previewSound() {
        const soundType = localStorage.getItem('notificationSoundType') || 'soft';

        if (typeof NotificationCenter !== 'undefined' && NotificationCenter.playNotificationSound) {
            NotificationCenter.playNotificationSound('info');
            console.log(`[NotificationUI] Preview sound: ${soundType}`);
        }
    },

    /**
     * Toggle notification type visibility
     * @param {string} type - Notification type (message, thread, agent, synergy, system)
     */
    toggleTypeVisibility(type) {
        const currentState = localStorage.getItem(`notif_${type}_visible`) !== 'false';
        const newState = !currentState;

        localStorage.setItem(`notif_${type}_visible`, newState);

        // Update icon
        const icon = document.getElementById(`toggle-${type}-visibility`);
        if (icon) {
            icon.className = newState ? 'fas fa-eye' : 'fas fa-eye-slash';
            icon.style.color = newState ? '' : '#94a3b8';
        }

        // Re-render notifications to apply filter
        if (typeof NotificationCenter !== 'undefined' && NotificationCenter.renderNotifications) {
            NotificationCenter.renderNotifications();
        }

        if (typeof showToast === 'function') {
            showToast(`${type.charAt(0).toUpperCase() + type.slice(1)} notifications ${newState ? 'shown' : 'hidden'}`, 'info');
        }

        console.log(`[NotificationUI] ${type} visibility: ${newState}`);
    },

    /**
     * Toggle notification type sound
     * @param {string} type - Notification type (message, thread, agent, synergy, system)
     */
    toggleTypeSound(type) {
        const currentState = localStorage.getItem(`notif_${type}_sound`) !== 'false';
        const newState = !currentState;

        localStorage.setItem(`notif_${type}_sound`, newState);

        // Update icon
        const icon = document.getElementById(`toggle-${type}-sound`);
        if (icon) {
            icon.className = newState ? 'fas fa-volume-up' : 'fas fa-volume-mute';
            icon.style.color = newState ? '' : '#94a3b8';
        }

        if (typeof showToast === 'function') {
            showToast(`${type.charAt(0).toUpperCase() + type.slice(1)} sound ${newState ? 'enabled' : 'muted'}`, 'info');
        }

        console.log(`[NotificationUI] ${type} sound: ${newState}`);
    },

    /**
     * Toggle notification type toast
     * @param {string} type - Notification type (message, thread, agent, synergy, system)
     */
    toggleTypeToast(type) {
        const currentState = localStorage.getItem(`notif_${type}_toast`) !== 'false';
        const newState = !currentState;

        localStorage.setItem(`notif_${type}_toast`, newState);

        // Update icon
        const icon = document.getElementById(`toggle-${type}-toast`);
        if (icon) {
            icon.className = newState ? 'fas fa-comment-dots' : 'fas fa-comment-slash';
            icon.style.color = newState ? '' : '#94a3b8';
        }

        if (typeof showToast === 'function') {
            showToast(`${type.charAt(0).toUpperCase() + type.slice(1)} toast ${newState ? 'enabled' : 'disabled'}`, 'info');
        }

        console.log(`[NotificationUI] ${type} toast: ${newState}`);
    },

    /**
     * Update filter button counts
     */
    updateFilterCounts() {
        if (typeof NotificationCenter === 'undefined') return;

        const counts = NotificationCenter.getCategoryCounts();

        Object.keys(counts).forEach(category => {
            const btn = document.querySelector(`.filter-btn[data-filter="${category}"]`);
            if (btn) {
                const countEl = btn.querySelector('.filter-count');
                if (countEl) {
                    countEl.textContent = counts[category];
                }
            }
        });
    },

    /**
     * Format time ago string
     * @param {number} timestamp - Unix timestamp
     * @returns {string} Formatted time string
     */
    timeAgo(timestamp) {
        const seconds = Math.floor((Date.now() - timestamp) / 1000);

        if (seconds < 60) return 'Just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;

        const date = new Date(timestamp);
        return date.toLocaleDateString();
    },

    /**
     * Escape HTML characters
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationUI;
}

// Export to window for browser usage
window.NotificationUI = NotificationUI;

console.log('✅ NotificationUI module loaded');
