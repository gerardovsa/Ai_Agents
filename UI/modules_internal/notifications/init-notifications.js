/**
 * FILE: UI/modules_internal/notifications/init-notifications.js
 * PURPOSE: Initialize the unified notification system
 * 
 * LOADING ORDER:
 * 1. notification-events.js (type definitions)
 * 2. notification-storage.js (persistence)
 * 3. notification-center.js (state management)
 * 4. notification-ui.js (UI rendering)
 * 5. This file (initialization)
 * 
 * FEATURES:
 * - Initialize all notification modules
 * - Create UI panel
 * - Load persisted notifications
 * - Setup integrations
 * 
 * USAGE:
 * Include this script LAST in the HTML after all other notification scripts
 * 
 * LAST MODIFIED: 2024-12-14 - Initial creation
 */

(function () {
    'use strict';

    console.log('🔔 [NotificationSystem] Starting initialization...');

    // Wait for DOM to be ready
    function init() {
        try {
            // Verify all dependencies are loaded
            const dependencies = [
                'NOTIFICATION_TYPES',
                'NotificationStorage',
                'NotificationCenter',
                'NotificationUI'
            ];

            const missing = dependencies.filter(dep => typeof window[dep] === 'undefined');

            if (missing.length > 0) {
                console.error('[NotificationSystem] Missing dependencies:', missing);
                console.error('[NotificationSystem] Make sure all notification scripts are loaded in correct order');
                return;
            }

            console.log('[NotificationSystem] All dependencies loaded');

            // Step 1: Initialize UI
            if (typeof NotificationUI !== 'undefined' && NotificationUI.init) {
                NotificationUI.init();
                console.log('✅ [NotificationSystem] UI initialized');
            }

            // Step 2: Initialize NotificationCenter
            if (typeof NotificationCenter !== 'undefined' && NotificationCenter.init) {
                NotificationCenter.init();
                console.log('✅ [NotificationSystem] NotificationCenter initialized');
            }

            // Step 3: Render initial state
            if (typeof NotificationCenter !== 'undefined' && NotificationCenter.renderNotifications) {
                NotificationCenter.renderNotifications();
                console.log('✅ [NotificationSystem] Initial notifications rendered');
            }

            // Step 4: Setup periodic cleanup (run once per day)
            setInterval(() => {
                if (typeof NotificationCenter !== 'undefined' && NotificationCenter.cleanupOldNotifications) {
                    NotificationCenter.cleanupOldNotifications();
                    console.log('[NotificationSystem] Ran periodic cleanup');
                }
            }, 24 * 60 * 60 * 1000); // 24 hours

            // Step 5: Migrate Synergy notifications (if present)
            migrateSynergyNotifications();

            // Step 6: Setup global error handler
            setupGlobalErrorHandler();

            console.log('✅ [NotificationSystem] Initialization complete');
            console.log(`📊 [NotificationSystem] ${NotificationCenter.notifications.length} notifications loaded`);
            console.log(`📊 [NotificationSystem] ${NotificationCenter.unreadCount} unread`);

            // Expose stats method globally for debugging
            window.getNotificationStats = () => {
                if (typeof NotificationCenter !== 'undefined' && NotificationCenter.getStats) {
                    return NotificationCenter.getStats();
                }
                return null;
            };

        } catch (error) {
            console.error('[NotificationSystem] Initialization failed:', error);
        }
    }

    /**
     * Migrate existing Synergy notifications to unified system
     */
    function migrateSynergyNotifications() {
        try {
            // Check if SynergyNotificationIntegration exists
            if (typeof SynergyNotificationIntegration !== 'undefined') {
                console.log('[NotificationSystem] Migrating Synergy notifications...');

                const synergyNotifs = SynergyNotificationIntegration.notifications || [];
                let migratedCount = 0;

                synergyNotifs.forEach(notif => {
                    // Only migrate if not already in unified system
                    const exists = NotificationCenter.notifications.some(n =>
                        n.metadata?.sessionId === notif.metadata?.sessionId &&
                        n.timestamp === notif.timestamp
                    );

                    if (!exists) {
                        // Add to unified system without showing toast
                        const unified = {
                            id: notif.id,
                            timestamp: notif.timestamp,
                            type: 'SYNERGY_UPDATED',
                            category: 'synergy',
                            severity: notif.type || 'info',
                            title: notif.title,
                            message: notif.message,
                            icon: 'fa-network-wired',
                            metadata: notif.metadata || {},
                            read: notif.read || false,
                            dismissed: false,
                            actionable: true,
                            action: {
                                type: 'view_synergy',
                                target: { sessionId: notif.metadata?.sessionId }
                            }
                        };

                        NotificationCenter.notifications.push(unified);

                        if (!unified.read) {
                            NotificationCenter.unreadCount++;
                        }

                        migratedCount++;
                    }
                });

                if (migratedCount > 0) {
                    NotificationCenter.save();
                    NotificationCenter.updateBadge();
                    console.log(`✅ [NotificationSystem] Migrated ${migratedCount} Synergy notifications`);
                }

                // Hook future Synergy notifications
                if (SynergyNotificationIntegration.addNotification) {
                    const original = SynergyNotificationIntegration.addNotification;

                    SynergyNotificationIntegration.addNotification = function (notification) {
                        // Call original
                        original.call(this, notification);

                        // Also add to unified system
                        if (typeof NotificationCenter !== 'undefined') {
                            NotificationCenter.add({
                                type: 'SYNERGY_UPDATED',
                                message: notification.message,
                                metadata: {
                                    sessionId: notification.metadata?.sessionId,
                                    ...notification.metadata
                                },
                                action: {
                                    type: 'view_synergy',
                                    target: { sessionId: notification.metadata?.sessionId }
                                }
                            });
                        }
                    };

                    console.log('✅ [NotificationSystem] Hooked Synergy notification system');
                }
            }
        } catch (error) {
            console.warn('[NotificationSystem] Synergy migration failed (non-critical):', error);
        }
    }

    /**
     * Setup global error handler for system errors
     */
    function setupGlobalErrorHandler() {
        // Capture unhandled errors
        window.addEventListener('error', (event) => {
            if (typeof NotificationCenter !== 'undefined' && NotificationCenter.add) {
                // Avoid notification spam - only log critical errors
                if (event.error && !event.error.logged) {
                    NotificationCenter.add({
                        type: 'SYSTEM_ERROR',
                        message: event.message || 'An error occurred',
                        metadata: {
                            filename: event.filename,
                            lineno: event.lineno,
                            colno: event.colno,
                            stack: event.error?.stack
                        }
                    });

                    // Mark as logged to avoid duplicates
                    if (event.error) {
                        event.error.logged = true;
                    }
                }
            }
        });

        // Capture unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            if (typeof NotificationCenter !== 'undefined' && NotificationCenter.add) {
                NotificationCenter.add({
                    type: 'SYSTEM_ERROR',
                    message: event.reason?.message || 'Unhandled promise rejection',
                    metadata: {
                        reason: String(event.reason)
                    }
                });
            }
        });

        console.log('✅ [NotificationSystem] Global error handler setup');
    }

    /**
     * Add connection status notifications
     */
    function setupConnectionMonitoring() {
        window.addEventListener('online', () => {
            if (typeof NotificationCenter !== 'undefined' && NotificationCenter.add) {
                NotificationCenter.add({
                    type: 'CONNECTION_RESTORED',
                    message: 'Internet connection restored'
                });
            }
        });

        window.addEventListener('offline', () => {
            if (typeof NotificationCenter !== 'undefined' && NotificationCenter.add) {
                NotificationCenter.add({
                    type: 'CONNECTION_LOST',
                    message: 'Internet connection lost'
                });
            }
        });

        console.log('✅ [NotificationSystem] Connection monitoring setup');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        // DOM already loaded
        setTimeout(init, 100); // Small delay to ensure all scripts loaded
    }

    // Also setup connection monitoring
    setupConnectionMonitoring();

})();

console.log('✅ Notification initialization script loaded');
