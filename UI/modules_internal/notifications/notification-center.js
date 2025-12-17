/**
 * FILE: UI/modules_internal/notifications/notification-center.js
 * PURPOSE: Unified notification management system
 * 
 * FEATURES:
 * - Centralized notification bus
 * - Add/remove/update notifications
 * - Filter by category
 * - Search functionality
 * - Persistent storage
 * - Badge counter management
 * - Click-to-navigate actions
 * 
 * DEPENDENCIES:
 * - notification-events.js (event type definitions)
 * - notification-storage.js (persistence)
 * - notification-ui.js (UI rendering)
 * 
 * EXPORTS:
 * - NotificationCenter.add(notification)
 * - NotificationCenter.remove(id)
 * - NotificationCenter.markAsRead(id)
 * - NotificationCenter.markAllAsRead()
 * - NotificationCenter.filter(category)
 * - NotificationCenter.search(query)
 * - NotificationCenter.clear()
 * 
 * LAST MODIFIED: 2024-12-14 - Initial creation
 */

const NotificationCenter = {
    // State
    notifications: [],
    unreadCount: 0,
    currentFilter: 'all',
    currentSearch: '',
    isInitialized: false,

    // UI references
    panelElement: null,
    listElement: null,
    badgeElement: null,

    /**
     * Initialize the notification center
     */
    init() {
        if (this.isInitialized) {
            console.warn('[NotificationCenter] Already initialized');
            return;
        }

        console.log('[NotificationCenter] Initializing...');

        // Load from storage
        const stored = NotificationStorage.load();
        this.notifications = stored.notifications;
        this.unreadCount = stored.unreadCount;

        // Initialize UI (will be created by notification-ui.js)
        this.initializeUI();

        // Update badge
        this.updateBadge();

        // Setup event listeners
        this.setupEventListeners();

        // Run cleanup on old notifications
        this.cleanupOldNotifications();

        this.isInitialized = true;
        console.log('[NotificationCenter] Initialized with', this.notifications.length, 'notifications');
    },

    /**
     * Initialize UI elements
     */
    initializeUI() {
        // UI elements will be set by NotificationUI module
        this.panelElement = document.getElementById('unified-notification-panel');
        this.listElement = document.getElementById('notification-list');
        this.badgeElement = document.querySelector('#notificationBellBtn-sidebar .notification-badge');

        // Restore panel state from localStorage
        this.restorePanelState();
    },

    /**
     * Restore panel open/closed state from localStorage
     */
    restorePanelState() {
        const wasOpen = localStorage.getItem('notificationPanelOpen') === 'true';
        if (wasOpen && this.panelElement) {
            // Restore open state without triggering notifications render
            this.panelElement.classList.add('show');
            console.log('[NotificationCenter] Restored panel to open state');
        }
    },

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Close panel when clicking outside
        document.addEventListener('click', (e) => {
            if (this.panelElement && !this.panelElement.contains(e.target)) {
                const bellBtn = document.getElementById('notificationBellBtn-sidebar');
                if (bellBtn && !bellBtn.contains(e.target)) {
                    this.closePanel();
                }
            }
        });

        console.log('[NotificationCenter] Event listeners setup');
    },

    /**
     * Add a new notification
     * @param {Object} notification - Notification object
     * @returns {Object} Created notification with ID
     */
    add(notification) {
        // Generate unique ID
        const id = `notif-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

        // Get type metadata
        const typeMetadata = getNotificationTypeMetadata(notification.type);

        // Create full notification object
        const fullNotification = {
            id,
            timestamp: Date.now(),
            type: notification.type,
            category: notification.category || typeMetadata.category,
            severity: notification.severity || typeMetadata.severity,
            title: notification.title || typeMetadata.title,
            message: notification.message,
            icon: notification.icon || typeMetadata.icon,
            metadata: notification.metadata || {},
            read: false,
            dismissed: false,
            actionable: notification.actionable !== undefined ? notification.actionable : typeMetadata.actionable,
            action: notification.action || null
        };

        // Add to beginning of array (most recent first)
        this.notifications.unshift(fullNotification);

        // Limit size
        if (this.notifications.length > NotificationStorage.MAX_NOTIFICATIONS) {
            this.notifications = this.notifications.slice(0, NotificationStorage.MAX_NOTIFICATIONS);
        }

        // Increment unread count
        this.unreadCount++;

        // Save to storage
        this.save();

        // Update UI
        this.updateBadge();
        this.renderNotifications();

        // Play notification sound if enabled (check type-specific settings)
        this.playNotificationSound(fullNotification.severity, fullNotification.category);

        // Show toast based on type-specific settings
        this.showToastNotification(fullNotification);

        console.log('[NotificationCenter] Added:', fullNotification.type, '-', fullNotification.message);

        return fullNotification;
    },

    /**
     * Show toast notification based on type settings
     * @param {Object} notification - Notification object
     */
    showToastNotification(notification) {
        // Check if toast should be shown for this type
        const category = notification.category || 'system';
        const toastEnabled = localStorage.getItem(`notif_${category}_toast`) !== 'false';

        if (!toastEnabled) {
            console.log(`[NotificationCenter] Toast disabled for ${category}`);
            return;
        }

        // Show toast for errors/warnings OR if type-specific toast is enabled
        if (typeof showToast === 'function') {
            showToast(notification.message, notification.severity);
        }
    },

    /**
     * Play notification sound based on severity
     * @param {string} severity - Notification severity (info, success, warning, error)
     * @param {string} category - Notification category (for type-specific muting)
     */
    playNotificationSound(severity, category) {
        // Check Do Not Disturb mode first
        const dndEnabled = localStorage.getItem('notificationDND') === 'true';
        if (dndEnabled) {
            console.log('[NotificationCenter] Do Not Disturb enabled - sound muted');
            return;
        }

        // Check if master sound is enabled
        const soundEnabled = localStorage.getItem('notificationSoundEnabled');
        if (soundEnabled === 'false') {
            return;
        }

        // Check type-specific sound setting
        if (category) {
            const typeSoundEnabled = localStorage.getItem(`notif_${category}_sound`) !== 'false';
            if (!typeSoundEnabled) {
                console.log(`[NotificationCenter] ${category} sounds muted`);
                return;
            }
        }

        // Get sound type for this category (per-type sound assignment)
        let soundType;
        if (category) {
            soundType = localStorage.getItem(`notif_${category}_sound`) || null;
        }
        // Fallback to global sound type if no category-specific sound is set
        if (!soundType || soundType === 'true' || soundType === 'false') {
            soundType = localStorage.getItem('notificationSoundType') || 'soft';
        }

        const volume = (parseInt(localStorage.getItem('notificationVolume')) || 50) / 100;

        // Use NotificationSounds library if available
        if (typeof NotificationSounds !== 'undefined' && NotificationSounds.isReady()) {
            NotificationSounds.play(soundType, volume);
            return;
        }

        // Fallback: Use NotificationSounds Web Audio API fallback
        console.log('[NotificationCenter] Using NotificationSounds Web Audio fallback');

        try {
            if (typeof NotificationSounds !== 'undefined' && NotificationSounds.playWithWebAudio) {
                NotificationSounds.playWithWebAudio(soundType, volume);
            } else {
                console.warn('[NotificationCenter] NotificationSounds not available - no sound played');
            }
        } catch (error) {
            console.error('[NotificationCenter] Fallback sound playback failed:', error);
        }
    },

    /**
     * Remove a notification
     * @param {string} id - Notification ID
     */
    remove(id) {
        const index = this.notifications.findIndex(n => n.id === id);

        if (index !== -1) {
            const notif = this.notifications[index];

            // Decrement unread if it was unread
            if (!notif.read) {
                this.unreadCount = Math.max(0, this.unreadCount - 1);
            }

            // Remove from array
            this.notifications.splice(index, 1);

            // Save and update UI
            this.save();
            this.updateBadge();
            this.renderNotifications();

            console.log('[NotificationCenter] Removed:', id);
        }
    },

    /**
     * Mark notification as read
     * @param {string} id - Notification ID
     */
    markAsRead(id) {
        const notif = this.notifications.find(n => n.id === id);

        if (notif && !notif.read) {
            notif.read = true;
            this.unreadCount = Math.max(0, this.unreadCount - 1);

            this.save();
            this.updateBadge();
            this.renderNotifications();

            console.log('[NotificationCenter] Marked as read:', id);
        }
    },

    /**
     * Mark all notifications as read
     */
    markAllAsRead() {
        this.notifications.forEach(n => n.read = true);
        this.unreadCount = 0;

        this.save();
        this.updateBadge();
        this.renderNotifications();

        console.log('[NotificationCenter] Marked all as read');
    },

    /**
     * Clear all notifications
     */
    clear() {
        if (confirm('Clear all notifications? This cannot be undone.')) {
            this.notifications = [];
            this.unreadCount = 0;

            this.save();
            this.updateBadge();
            this.renderNotifications();

            console.log('[NotificationCenter] Cleared all notifications');
        }
    },

    /**
     * Filter notifications by category
     * @param {string} category - Category filter
     * @returns {Array} Filtered notifications
     */
    filter(category) {
        this.currentFilter = category;

        if (category === 'all') {
            return this.notifications;
        }

        return this.notifications.filter(n => n.category === category);
    },

    /**
     * Search notifications
     * @param {string} query - Search query
     * @returns {Array} Matching notifications
     */
    search(query) {
        this.currentSearch = query.toLowerCase();

        if (!query) {
            return this.filter(this.currentFilter);
        }

        const filtered = this.filter(this.currentFilter);

        return filtered.filter(n =>
            n.title.toLowerCase().includes(this.currentSearch) ||
            n.message.toLowerCase().includes(this.currentSearch) ||
            (n.metadata && JSON.stringify(n.metadata).toLowerCase().includes(this.currentSearch))
        );
    },

    /**
     * Get notifications with current filter and search applied
     * @returns {Array} Filtered/searched notifications
     */
    getFiltered() {
        if (this.currentSearch) {
            return this.search(this.currentSearch);
        }
        return this.filter(this.currentFilter);
    },

    /**
     * Get notification counts by category
     * @returns {Object} Category counts
     */
    getCategoryCounts() {
        const counts = {
            all: this.notifications.length,
            agent: 0,
            thread: 0,
            synergy: 0,
            system: 0
        };

        this.notifications.forEach(n => {
            if (counts[n.category] !== undefined) {
                counts[n.category]++;
            }
        });

        return counts;
    },

    /**
     * Handle notification click
     * @param {string} id - Notification ID
     */
    handleClick(id) {
        const notif = this.notifications.find(n => n.id === id);

        if (!notif) return;

        // Mark as read
        this.markAsRead(id);

        // Execute action if actionable
        if (notif.actionable && notif.action) {
            this.executeAction(notif.action);
        }

        // Close panel
        this.closePanel();
    },

    /**
     * Execute notification action
     * @param {Object} action - Action object {type, target}
     */
    executeAction(action) {
        console.log('[NotificationCenter] Executing action:', action.type);

        switch (action.type) {
            case 'navigate_to_agent':
                if (action.target && action.target.agentId) {
                    // Switch to multi-agent tab
                    if (typeof switchTab === 'function') {
                        switchTab('multi-agent');
                    }

                    // Scroll to agent
                    if (typeof MultiAgent !== 'undefined' && MultiAgent.scrollToAgent) {
                        setTimeout(() => {
                            MultiAgent.scrollToAgent(action.target.agentId);
                        }, 300);
                    }
                }
                break;

            case 'open_thread':
                if (action.target && action.target.threadId) {
                    // Switch thread
                    if (typeof ThreadManager !== 'undefined' && ThreadManager.switchThread) {
                        ThreadManager.switchThread(action.target.threadId);
                    }
                }
                break;

            case 'view_synergy':
                if (action.target && action.target.sessionId) {
                    // Switch to synergy tab
                    const synergyTab = document.querySelector('[data-tab="synergy"]');
                    if (synergyTab && typeof synergyTab.click === 'function') {
                        synergyTab.click();
                    }

                    // Open session if popup available
                    setTimeout(() => {
                        if (window.synergyPopupModal && typeof window.synergyPopupModal.open === 'function') {
                            window.synergyPopupModal.open(action.target.sessionId);
                        }
                    }, 300);
                }
                break;

            default:
                console.warn('[NotificationCenter] Unknown action type:', action.type);
        }
    },

    /**
     * Open notification panel
     */
    openPanel() {
        if (this.panelElement) {
            this.panelElement.classList.add('show');
            localStorage.setItem('notificationPanelOpen', 'true');
            console.log('[NotificationCenter] Panel opened');
        }
    },

    /**
     * Close notification panel
     */
    closePanel() {
        if (this.panelElement) {
            this.panelElement.classList.remove('show');
            localStorage.setItem('notificationPanelOpen', 'false');
            console.log('[NotificationCenter] Panel closed');
        }
    },

    /**
     * Toggle notification panel
     */
    togglePanel() {
        if (this.panelElement) {
            if (this.panelElement.classList.contains('show')) {
                this.closePanel();
            } else {
                this.openPanel();
                this.renderNotifications();
            }
        }
    },

    /**
     * Update badge counter
     */
    updateBadge() {
        // Update notification bell badge ONLY (not account profile)
        const bellBtn = document.getElementById('notificationBellBtn-sidebar');

        if (bellBtn) {
            let badge = bellBtn.querySelector('.notification-badge');

            if (this.unreadCount > 0) {
                if (!badge) {
                    badge = document.createElement('span');
                    badge.className = 'notification-badge';
                    bellBtn.appendChild(badge);
                }
                badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
                badge.style.display = 'flex';
            } else if (badge) {
                badge.style.display = 'none';
            }
        }

        // DO NOT update account profile button badge
        // Badge should only appear on notification bell button
    },

    /**
     * Render notifications in UI
     */
    renderNotifications() {
        // Delegate to NotificationUI module if available
        if (typeof NotificationUI !== 'undefined' && NotificationUI.render) {
            NotificationUI.render(this.getFiltered());
        } else {
            console.warn('[NotificationCenter] NotificationUI not available');
        }
    },

    /**
     * Save to storage
     */
    save() {
        NotificationStorage.save(this.notifications, this.unreadCount);
    },

    /**
     * Cleanup old notifications (7+ days)
     */
    cleanupOldNotifications() {
        const originalLength = this.notifications.length;
        this.notifications = NotificationStorage.cleanupOldNotifications(this.notifications);

        const removed = originalLength - this.notifications.length;
        if (removed > 0) {
            console.log('[NotificationCenter] Cleaned up', removed, 'old notifications');
            this.save();
        }
    },

    /**
     * Get statistics
     * @returns {Object} Notification statistics
     */
    getStats() {
        return {
            total: this.notifications.length,
            unread: this.unreadCount,
            read: this.notifications.filter(n => n.read).length,
            bycategory: this.getCategoryCounts(),
            storage: NotificationStorage.getStats()
        };
    }
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationCenter;
}

// Export to window for browser usage
window.NotificationCenter = NotificationCenter;

console.log('✅ NotificationCenter module loaded');
