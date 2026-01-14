/**
 * FILE: UI/shared/js/synergy-notification-integration.js
 * PURPOSE: Connect Synergy Realtime to Account Sidebar Notification Panel
 * 
 * FEATURES:
 * - Add Synergy notifications to notification sidebar
 * - Badge counter for new notifications
 * - Persistent notification history
 * - Click to navigate to session
 * - Filter by type (session created/updated/moved)
 * - Mark as read/unread
 * 
 * LAST MODIFIED: 2025-12-09 - Initial implementation
 */

window.SynergyNotificationIntegration = {
    notifications: [],
    maxNotifications: 50,
    unreadCount: 0,
    storageKey: 'synergy_notifications',

    /**
     * Initialize notification integration
     */
    init() {
        console.log('[SYNERGY-NOTIF] Initializing notification integration...');

        // Load stored notifications
        this.loadNotifications();

        // Hook into SynergyRealtimeEnhanced
        if (window.SynergyRealtimeEnhanced) {
            this.hookRealtime();
        } else {
            console.warn('[SYNERGY-NOTIF] SynergyRealtimeEnhanced not found');
        }

        // Inject notification panel content
        this.injectNotificationPanel();

        // Update badge
        this.updateBadge();

        console.log('[SYNERGY-NOTIF] Initialized with', this.notifications.length, 'notifications');
    },

    /**
     * Hook into Synergy realtime to intercept notifications
     */
    hookRealtime() {
        const originalShowNotification = window.SynergyRealtimeEnhanced._showNotification;

        window.SynergyRealtimeEnhanced._showNotification = (title, message, type = 'info') => {
            // Call original notification (toast)
            originalShowNotification.call(window.SynergyRealtimeEnhanced, title, message, type);

            // Add to notification sidebar
            this.addNotification({
                title,
                message,
                type,
                timestamp: Date.now(),
                read: false,
                source: 'synergy'
            });
        };

        console.log('[SYNERGY-NOTIF] Hooked into SynergyRealtimeEnhanced');
    },

    /**
     * Add notification to sidebar
     */
    addNotification(notification) {
        // Add unique ID
        notification.id = `synergy-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

        // Add to beginning of array
        this.notifications.unshift(notification);

        // Limit size
        if (this.notifications.length > this.maxNotifications) {
            this.notifications = this.notifications.slice(0, this.maxNotifications);
        }

        // Increment unread
        this.unreadCount++;

        // Save to storage
        this.saveNotifications();

        // Update UI
        this.updateBadge();
        this.renderNotifications();

        console.log('[SYNERGY-NOTIF] Added notification:', notification.title);
    },

    /**
     * Mark notification as read
     */
    markAsRead(notificationId) {
        const notif = this.notifications.find(n => n.id === notificationId);
        if (notif && !notif.read) {
            notif.read = true;
            this.unreadCount = Math.max(0, this.unreadCount - 1);
            this.saveNotifications();
            this.updateBadge();
            this.renderNotifications();
        }
    },

    /**
     * Mark all as read
     */
    markAllAsRead() {
        this.notifications.forEach(n => n.read = true);
        this.unreadCount = 0;
        this.saveNotifications();
        this.updateBadge();
        this.renderNotifications();
    },

    /**
     * Clear all notifications
     */
    clearAll() {
        if (confirm('Clear all Synergy notifications?')) {
            this.notifications = [];
            this.unreadCount = 0;
            this.saveNotifications();
            this.updateBadge();
            this.renderNotifications();
        }
    },

    /**
     * Update badge counter
     */
    updateBadge() {
        // Update notification bell badge ONLY (right sidebar button)
        // DO NOT update account profile notifications tab
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

        // REMOVED: Account profile notifications tab badge
        // Badge should ONLY appear on right sidebar notification bell button
        // Account profile notifications tab should NOT have a badge
    },

    /**
     * Render notifications in sidebar panel
     */
    renderNotifications() {
        const container = document.getElementById('synergy-notifications-list');
        if (!container) return;

        if (this.notifications.length === 0) {
            container.innerHTML = `
                <div class="empty-state" style="text-align: center; padding: 40px 20px; color: var(--text-muted);">
                    <i class="fas fa-bell-slash" style="font-size: 48px; opacity: 0.3; margin-bottom: 16px;"></i>
                    <p style="font-size: 16px; margin: 0;">No Synergy notifications yet</p>
                    <p style="font-size: 14px; margin-top: 8px; opacity: 0.7;">You'll be notified about your session updates</p>
                </div>
            `;
            return;
        }

        const html = this.notifications.map(notif => {
            const icon = this.getNotificationIcon(notif.type);
            const timeAgo = this.timeAgo(notif.timestamp);
            const readClass = notif.read ? 'read' : 'unread';

            return `
                <div class="synergy-notification-item ${readClass}" data-id="${notif.id}" onclick="SynergyNotificationIntegration.handleClick('${notif.id}')">
                    <div class="notif-icon ${notif.type}">
                        <i class="${icon}"></i>
                    </div>
                    <div class="notif-content">
                        <div class="notif-title">${this.escapeHtml(notif.title)}</div>
                        <div class="notif-message">${this.escapeHtml(notif.message)}</div>
                        <div class="notif-time">${timeAgo}</div>
                    </div>
                    <div class="notif-actions">
                        ${!notif.read ? '<span class="unread-dot"></span>' : ''}
                        <button class="notif-action-btn" onclick="event.stopPropagation(); SynergyNotificationIntegration.deleteNotification('${notif.id}')" title="Delete">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = html;
    },

    /**
     * Handle notification click
     */
    handleClick(notificationId) {
        this.markAsRead(notificationId);

        // Navigate to Synergy tab
        const synergyTab = document.querySelector('[data-tab="synergy"]');
        if (synergyTab && typeof synergyTab.click === 'function') {
            synergyTab.click();
        }

        // Close account sidebar if open
        if (window.AccountSidebar && typeof window.AccountSidebar.toggleSidebar === 'function') {
            const sidebar = document.getElementById('account-sidebar');
            if (sidebar && !sidebar.classList.contains('collapsed')) {
                window.AccountSidebar.toggleSidebar();
            }
        }
    },

    /**
     * Delete notification
     */
    deleteNotification(notificationId) {
        const index = this.notifications.findIndex(n => n.id === notificationId);
        if (index !== -1) {
            const notif = this.notifications[index];
            if (!notif.read) {
                this.unreadCount = Math.max(0, this.unreadCount - 1);
            }
            this.notifications.splice(index, 1);
            this.saveNotifications();
            this.updateBadge();
            this.renderNotifications();
        }
    },

    /**
     * Get icon for notification type
     */
    getNotificationIcon(type) {
        const icons = {
            success: 'fas fa-check-circle',
            info: 'fas fa-info-circle',
            warning: 'fas fa-exclamation-triangle',
            error: 'fas fa-exclamation-circle'
        };
        return icons[type] || 'fas fa-bell';
    },

    /**
     * Time ago helper
     */
    timeAgo(timestamp) {
        const now = Date.now();
        const diff = now - timestamp;

        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (seconds < 60) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        if (days < 7) return `${days}d ago`;

        return new Date(timestamp).toLocaleDateString();
    },

    /**
     * Escape HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Save to localStorage
     */
    saveNotifications() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify({
                notifications: this.notifications,
                unreadCount: this.unreadCount
            }));
        } catch (e) {
            console.error('[SYNERGY-NOTIF] Failed to save notifications:', e);
        }
    },

    /**
     * Load from localStorage
     */
    loadNotifications() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            if (stored) {
                const data = JSON.parse(stored);
                this.notifications = data.notifications || [];
                this.unreadCount = data.unreadCount || 0;
            }
        } catch (e) {
            console.error('[SYNERGY-NOTIF] Failed to load notifications:', e);
            this.notifications = [];
            this.unreadCount = 0;
        }
    },

    /**
     * Inject notification panel into AccountSidebar
     */
    injectNotificationPanel() {
        // Wait for AccountSidebar to load
        const checkInterval = setInterval(() => {
            const accountContent = document.getElementById('account-sidebar-content');
            if (accountContent) {
                clearInterval(checkInterval);
                this.injectPanel();
            }
        }, 500);

        // Give up after 10 seconds
        setTimeout(() => clearInterval(checkInterval), 10000);
    },

    /**
     * Actually inject the panel HTML
     */
    injectPanel() {
        // Hook into AccountSidebar switchTab to inject our content
        if (window.AccountSidebar && typeof window.AccountSidebar.switchTab === 'function') {
            const originalSwitchTab = window.AccountSidebar.switchTab;

            window.AccountSidebar.switchTab = function (tabName) {
                originalSwitchTab.call(window.AccountSidebar, tabName);

                // If notifications tab, inject Synergy notifications
                if (tabName === 'notifications') {
                    setTimeout(() => {
                        SynergyNotificationIntegration.injectSynergySection();
                    }, 100);
                }
            };

            console.log('[SYNERGY-NOTIF] Hooked into AccountSidebar.switchTab');
        }
    },

    /**
     * Inject Synergy notification section into notifications tab
     */
    injectSynergySection() {
        const accountContent = document.getElementById('account-sidebar-content');
        if (!accountContent) return;

        // Check if already injected
        if (document.getElementById('synergy-notifications-section')) {
            this.renderNotifications();
            return;
        }

        // Find a good place to inject (before or after existing content)
        const synergySection = document.createElement('div');
        synergySection.id = 'synergy-notifications-section';
        synergySection.className = 'settings-section';
        synergySection.innerHTML = `
            <div class="settings-section-header" onclick="toggleSettingsSection(this)">
                <div class="settings-section-title">
                    <i class="fas fa-project-diagram"></i> Synergy Session Updates
                    <span class="settings-section-toggle"><i class="fas fa-chevron-down"></i></span>
                </div>
                <div class="settings-section-actions">
                    <button class="btn-icon" onclick="event.stopPropagation(); SynergyNotificationIntegration.markAllAsRead()" title="Mark all as read">
                        <i class="fas fa-check-double"></i>
                    </button>
                    <button class="btn-icon" onclick="event.stopPropagation(); SynergyNotificationIntegration.clearAll()" title="Clear all">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <div class="settings-section-content">
                <div id="synergy-notifications-list" class="synergy-notifications-list">
                    <!-- Notifications rendered here -->
                </div>
            </div>
        `;

        accountContent.insertBefore(synergySection, accountContent.firstChild);

        // Render notifications
        this.renderNotifications();

        console.log('[SYNERGY-NOTIF] Injected Synergy section into notifications tab');
    }
};

// Add CSS for notifications
if (!document.getElementById('synergy-notification-styles')) {
    const style = document.createElement('style');
    style.id = 'synergy-notification-styles';
    style.textContent = `
        /* Notification badge on bell button */
        .notification-badge {
            position: absolute;
            top: 4px;
            right: 4px;
            background: #ef4444;
            color: white;
            border-radius: 10px;
            padding: 2px 6px;
            font-size: 10px;
            font-weight: 600;
            min-width: 18px;
            height: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            z-index: 10;
        }
        
        /* Tab badge */
        .tab-badge {
            position: absolute;
            top: -4px;
            right: -4px;
            background: #ef4444;
            color: white;
            border-radius: 10px;
            padding: 2px 6px;
            font-size: 10px;
            font-weight: 600;
            min-width: 18px;
            height: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* Notifications list */
        .synergy-notifications-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
            max-height: 60vh;
            overflow-y: auto;
        }
        
        /* Notification item */
        .synergy-notification-item {
            display: flex;
            gap: 12px;
            padding: 12px;
            background: var(--bg-secondary);
            border-radius: 8px;
            border-left: 3px solid transparent;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .synergy-notification-item:hover {
            background: var(--bg-tertiary);
            transform: translateX(2px);
        }
        
        .synergy-notification-item.unread {
            background: var(--bg-tertiary);
            border-left-color: var(--accent-primary);
        }
        
        .synergy-notification-item.unread .notif-title {
            font-weight: 600;
        }
        
        /* Icon */
        .notif-icon {
            flex-shrink: 0;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
        }
        
        .notif-icon.success {
            background: rgba(34, 197, 94, 0.15);
            color: #22c55e;
        }
        
        .notif-icon.info {
            background: rgba(59, 130, 246, 0.15);
            color: #3b82f6;
        }
        
        .notif-icon.warning {
            background: rgba(251, 146, 60, 0.15);
            color: #fb923c;
        }
        
        .notif-icon.error {
            background: rgba(239, 68, 68, 0.15);
            color: #ef4444;
        }
        
        /* Content */
        .notif-content {
            flex: 1;
            min-width: 0;
        }
        
        .notif-title {
            font-size: 14px;
            margin-bottom: 4px;
            color: var(--text-primary);
        }
        
        .notif-message {
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 6px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .notif-time {
            font-size: 11px;
            color: var(--text-muted);
            opacity: 0.7;
        }
        
        /* Actions */
        .notif-actions {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .unread-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-primary);
        }
        
        .notif-action-btn {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            border: none;
            background: transparent;
            color: var(--text-muted);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
            font-size: 12px;
        }
        
        .notif-action-btn:hover {
            background: var(--bg-primary);
            color: var(--text-primary);
        }
        
        /* Settings section actions */
        .settings-section-actions {
            display: flex;
            gap: 4px;
        }
        
        .settings-section-actions .btn-icon {
            width: 32px;
            height: 32px;
            border-radius: 6px;
            border: 1px solid var(--border-default);
            background: var(--bg-secondary);
            color: var(--text-secondary);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
            font-size: 14px;
        }
        
        .settings-section-actions .btn-icon:hover {
            background: var(--bg-tertiary);
            color: var(--accent-primary);
            border-color: var(--accent-primary);
        }
    `;
    document.head.appendChild(style);
}

// Auto-initialize when DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => SynergyNotificationIntegration.init(), 2000);
    });
} else {
    setTimeout(() => SynergyNotificationIntegration.init(), 2000);
}

console.log('[SYNERGY-NOTIF] Notification integration module loaded');
