/**
 * FILE: UI/modules_internal/notifications/notification-storage.js
 * PURPOSE: Handle notification persistence to localStorage
 * 
 * FEATURES:
 * - localStorage persistence
 * - Automatic cleanup (7-day retention)
 * - Size limit management (max 100 notifications)
 * - Efficient read/write operations
 * 
 * EXPORTS:
 * - NotificationStorage.save(notifications, unreadCount)
 * - NotificationStorage.load()
 * - NotificationStorage.clear()
 * - NotificationStorage.cleanup()
 * 
 * LAST MODIFIED: 2024-12-14 - Initial creation
 */

const NotificationStorage = {
    // Storage configuration
    STORAGE_KEY: 'unified_notifications',
    MAX_NOTIFICATIONS: 100,
    RETENTION_DAYS: 7,

    /**
     * Save notifications to localStorage
     * @param {Array} notifications - Array of notification objects
     * @param {number} unreadCount - Number of unread notifications
     */
    save(notifications, unreadCount) {
        try {
            const data = {
                notifications: notifications.slice(0, this.MAX_NOTIFICATIONS),
                unreadCount: unreadCount,
                lastUpdated: Date.now(),
                version: '1.0'
            };

            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
            console.log('[NotificationStorage] Saved', notifications.length, 'notifications');

            return true;
        } catch (error) {
            console.error('[NotificationStorage] Save failed:', error);

            // If quota exceeded, try clearing old notifications
            if (error.name === 'QuotaExceededError') {
                console.warn('[NotificationStorage] Storage quota exceeded, clearing old notifications');
                this.cleanup(true);

                // Retry with fewer notifications
                try {
                    const reducedData = {
                        notifications: notifications.slice(0, 50),
                        unreadCount: unreadCount,
                        lastUpdated: Date.now(),
                        version: '1.0'
                    };
                    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(reducedData));
                    return true;
                } catch (retryError) {
                    console.error('[NotificationStorage] Retry save failed:', retryError);
                    return false;
                }
            }

            return false;
        }
    },

    /**
     * Load notifications from localStorage
     * @returns {Object} {notifications: Array, unreadCount: number}
     */
    load() {
        try {
            const stored = localStorage.getItem(this.STORAGE_KEY);

            if (!stored) {
                console.log('[NotificationStorage] No stored notifications found');
                return {
                    notifications: [],
                    unreadCount: 0
                };
            }

            const data = JSON.parse(stored);

            // Validate data structure
            if (!data.notifications || !Array.isArray(data.notifications)) {
                console.warn('[NotificationStorage] Invalid data structure, resetting');
                return {
                    notifications: [],
                    unreadCount: 0
                };
            }

            // Cleanup old notifications
            const cleanedNotifications = this.cleanupOldNotifications(data.notifications);

            console.log('[NotificationStorage] Loaded', cleanedNotifications.length, 'notifications');

            return {
                notifications: cleanedNotifications,
                unreadCount: data.unreadCount || 0
            };
        } catch (error) {
            console.error('[NotificationStorage] Load failed:', error);
            return {
                notifications: [],
                unreadCount: 0
            };
        }
    },

    /**
     * Clean up old notifications (older than RETENTION_DAYS)
     * @param {Array} notifications - Array of notification objects
     * @returns {Array} Filtered notifications
     */
    cleanupOldNotifications(notifications) {
        const cutoffTime = Date.now() - (this.RETENTION_DAYS * 24 * 60 * 60 * 1000);

        const filtered = notifications.filter(notif => {
            return notif.timestamp > cutoffTime;
        });

        const removedCount = notifications.length - filtered.length;
        if (removedCount > 0) {
            console.log('[NotificationStorage] Removed', removedCount, 'old notifications');
        }

        return filtered;
    },

    /**
     * Clear all notifications from storage
     */
    clear() {
        try {
            localStorage.removeItem(this.STORAGE_KEY);
            console.log('[NotificationStorage] Cleared all notifications');
            return true;
        } catch (error) {
            console.error('[NotificationStorage] Clear failed:', error);
            return false;
        }
    },

    /**
     * Cleanup storage (remove old notifications, optimize size)
     * @param {boolean} aggressive - If true, remove more aggressively
     */
    cleanup(aggressive = false) {
        try {
            const data = this.load();

            if (aggressive) {
                // Keep only recent 50 notifications
                data.notifications = data.notifications
                    .sort((a, b) => b.timestamp - a.timestamp)
                    .slice(0, 50);
                console.log('[NotificationStorage] Aggressive cleanup: keeping', data.notifications.length, 'notifications');
            } else {
                // Normal cleanup (remove old)
                data.notifications = this.cleanupOldNotifications(data.notifications);
            }

            this.save(data.notifications, data.unreadCount);
            return true;
        } catch (error) {
            console.error('[NotificationStorage] Cleanup failed:', error);
            return false;
        }
    },

    /**
     * Get storage statistics
     * @returns {Object} Storage stats
     */
    getStats() {
        try {
            const data = this.load();
            const stored = localStorage.getItem(this.STORAGE_KEY);
            const sizeBytes = stored ? new Blob([stored]).size : 0;
            const sizeKB = (sizeBytes / 1024).toFixed(2);

            return {
                totalNotifications: data.notifications.length,
                unreadCount: data.unreadCount,
                storageSize: `${sizeKB} KB`,
                storageSizeBytes: sizeBytes,
                oldestNotification: data.notifications.length > 0
                    ? new Date(Math.min(...data.notifications.map(n => n.timestamp)))
                    : null,
                newestNotification: data.notifications.length > 0
                    ? new Date(Math.max(...data.notifications.map(n => n.timestamp)))
                    : null
            };
        } catch (error) {
            console.error('[NotificationStorage] Stats failed:', error);
            return null;
        }
    },

    /**
     * Export notifications as JSON (for backup)
     * @returns {string} JSON string
     */
    export() {
        try {
            const data = this.load();
            return JSON.stringify(data, null, 2);
        } catch (error) {
            console.error('[NotificationStorage] Export failed:', error);
            return null;
        }
    },

    /**
     * Import notifications from JSON (for restore)
     * @param {string} jsonString - JSON string to import
     * @returns {boolean} Success
     */
    import(jsonString) {
        try {
            const data = JSON.parse(jsonString);

            if (!data.notifications || !Array.isArray(data.notifications)) {
                console.error('[NotificationStorage] Invalid import data');
                return false;
            }

            this.save(data.notifications, data.unreadCount || 0);
            console.log('[NotificationStorage] Imported', data.notifications.length, 'notifications');
            return true;
        } catch (error) {
            console.error('[NotificationStorage] Import failed:', error);
            return false;
        }
    }
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationStorage;
}

// Export to window for browser usage
window.NotificationStorage = NotificationStorage;

console.log('✅ NotificationStorage module loaded');
