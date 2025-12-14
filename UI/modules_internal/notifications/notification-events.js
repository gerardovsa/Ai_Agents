/**
 * FILE: UI/modules_internal/notifications/notification-events.js
 * PURPOSE: Define all notification event types and their metadata
 * 
 * FEATURES:
 * - Event type definitions with icons, severity, categories
 * - Centralized notification configuration
 * - Easy to extend with new event types
 * 
 * EXPORTS:
 * - NOTIFICATION_TYPES - Object containing all event type definitions
 * - NOTIFICATION_CATEGORIES - Available categories for filtering
 * - NOTIFICATION_SEVERITIES - Available severity levels
 * 
 * LAST MODIFIED: 2024-12-14 - Initial creation
 */

/**
 * Notification Categories (for filtering)
 */
const NOTIFICATION_CATEGORIES = {
    AGENT: 'agent',
    THREAD: 'thread',
    SYNERGY: 'synergy',
    SYSTEM: 'system',
    ALL: 'all'
};

/**
 * Notification Severity Levels
 */
const NOTIFICATION_SEVERITIES = {
    INFO: 'info',
    SUCCESS: 'success',
    WARNING: 'warning',
    ERROR: 'error'
};

/**
 * Notification Event Type Definitions
 * Each type includes:
 * - title: Display title for the notification
 * - icon: Font Awesome icon class
 * - severity: info|success|warning|error
 * - category: agent|thread|synergy|system
 * - actionable: Whether clicking navigates somewhere
 */
const NOTIFICATION_TYPES = {
    // ========================================
    // MESSAGE EVENTS
    // ========================================
    MESSAGE_COMPLETE: {
        title: 'Message Complete',
        icon: 'fa-check-circle',
        severity: NOTIFICATION_SEVERITIES.SUCCESS,
        category: NOTIFICATION_CATEGORIES.AGENT,
        actionable: true
    },
    MESSAGE_ERROR: {
        title: 'Message Error',
        icon: 'fa-exclamation-triangle',
        severity: NOTIFICATION_SEVERITIES.ERROR,
        category: NOTIFICATION_CATEGORIES.AGENT,
        actionable: true
    },
    MESSAGE_STREAMING: {
        title: 'Streaming Started',
        icon: 'fa-stream',
        severity: NOTIFICATION_SEVERITIES.INFO,
        category: NOTIFICATION_CATEGORIES.AGENT,
        actionable: true
    },

    // ========================================
    // THREAD EVENTS
    // ========================================
    THREAD_CREATED: {
        title: 'Thread Created',
        icon: 'fa-plus-circle',
        severity: NOTIFICATION_SEVERITIES.SUCCESS,
        category: NOTIFICATION_CATEGORIES.THREAD,
        actionable: true
    },
    THREAD_ASSIGNED: {
        title: 'Thread Assigned',
        icon: 'fa-link',
        severity: NOTIFICATION_SEVERITIES.INFO,
        category: NOTIFICATION_CATEGORIES.THREAD,
        actionable: true
    },
    THREAD_UNASSIGNED: {
        title: 'Thread Unassigned',
        icon: 'fa-unlink',
        severity: NOTIFICATION_SEVERITIES.INFO,
        category: NOTIFICATION_CATEGORIES.THREAD,
        actionable: true
    },
    THREAD_DELETED: {
        title: 'Thread Deleted',
        icon: 'fa-trash',
        severity: NOTIFICATION_SEVERITIES.WARNING,
        category: NOTIFICATION_CATEGORIES.THREAD,
        actionable: false
    },
    THREAD_UPDATED: {
        title: 'Thread Updated',
        icon: 'fa-edit',
        severity: NOTIFICATION_SEVERITIES.INFO,
        category: NOTIFICATION_CATEGORIES.THREAD,
        actionable: true
    },
    THREAD_COMPLETED: {
        title: 'Thread Completed',
        icon: 'fa-flag-checkered',
        severity: NOTIFICATION_SEVERITIES.SUCCESS,
        category: NOTIFICATION_CATEGORIES.THREAD,
        actionable: true
    },

    // ========================================
    // AGENT EVENTS
    // ========================================
    AGENT_STARTED: {
        title: 'Agent Started',
        icon: 'fa-play',
        severity: NOTIFICATION_SEVERITIES.INFO,
        category: NOTIFICATION_CATEGORIES.AGENT,
        actionable: true
    },
    AGENT_STOPPED: {
        title: 'Agent Stopped',
        icon: 'fa-stop',
        severity: NOTIFICATION_SEVERITIES.INFO,
        category: NOTIFICATION_CATEGORIES.AGENT,
        actionable: true
    },
    AGENT_IDLE: {
        title: 'Agent Idle',
        icon: 'fa-pause',
        severity: NOTIFICATION_SEVERITIES.INFO,
        category: NOTIFICATION_CATEGORIES.AGENT,
        actionable: true
    },
    AGENT_BUSY: {
        title: 'Agent Busy',
        icon: 'fa-spinner',
        severity: NOTIFICATION_SEVERITIES.INFO,
        category: NOTIFICATION_CATEGORIES.AGENT,
        actionable: true
    },
    AGENT_ERROR: {
        title: 'Agent Error',
        icon: 'fa-exclamation-circle',
        severity: NOTIFICATION_SEVERITIES.ERROR,
        category: NOTIFICATION_CATEGORIES.AGENT,
        actionable: true
    },

    // ========================================
    // SYNERGY EVENTS
    // ========================================
    SYNERGY_CREATED: {
        title: 'Synergy Session Created',
        icon: 'fa-network-wired',
        severity: NOTIFICATION_SEVERITIES.SUCCESS,
        category: NOTIFICATION_CATEGORIES.SYNERGY,
        actionable: true
    },
    SYNERGY_UPDATED: {
        title: 'Synergy Session Updated',
        icon: 'fa-sync',
        severity: NOTIFICATION_SEVERITIES.INFO,
        category: NOTIFICATION_CATEGORIES.SYNERGY,
        actionable: true
    },
    SYNERGY_MOVED: {
        title: 'Synergy Session Moved',
        icon: 'fa-arrows-alt',
        severity: NOTIFICATION_SEVERITIES.INFO,
        category: NOTIFICATION_CATEGORIES.SYNERGY,
        actionable: true
    },
    SYNERGY_PRIORITY_CHANGED: {
        title: 'Synergy Priority Changed',
        icon: 'fa-flag',
        severity: NOTIFICATION_SEVERITIES.INFO,
        category: NOTIFICATION_CATEGORIES.SYNERGY,
        actionable: true
    },
    SYNERGY_COMPLETED: {
        title: 'Synergy Session Completed',
        icon: 'fa-check-double',
        severity: NOTIFICATION_SEVERITIES.SUCCESS,
        category: NOTIFICATION_CATEGORIES.SYNERGY,
        actionable: true
    },

    // ========================================
    // SYSTEM EVENTS
    // ========================================
    SYSTEM_INFO: {
        title: 'System Information',
        icon: 'fa-info-circle',
        severity: NOTIFICATION_SEVERITIES.INFO,
        category: NOTIFICATION_CATEGORIES.SYSTEM,
        actionable: false
    },
    SYSTEM_WARNING: {
        title: 'System Warning',
        icon: 'fa-exclamation',
        severity: NOTIFICATION_SEVERITIES.WARNING,
        category: NOTIFICATION_CATEGORIES.SYSTEM,
        actionable: false
    },
    SYSTEM_ERROR: {
        title: 'System Error',
        icon: 'fa-times-circle',
        severity: NOTIFICATION_SEVERITIES.ERROR,
        category: NOTIFICATION_CATEGORIES.SYSTEM,
        actionable: false
    },
    SYSTEM_SUCCESS: {
        title: 'System Success',
        icon: 'fa-check',
        severity: NOTIFICATION_SEVERITIES.SUCCESS,
        category: NOTIFICATION_CATEGORIES.SYSTEM,
        actionable: false
    },

    // Connection events
    CONNECTION_LOST: {
        title: 'Connection Lost',
        icon: 'fa-wifi-slash',
        severity: NOTIFICATION_SEVERITIES.ERROR,
        category: NOTIFICATION_CATEGORIES.SYSTEM,
        actionable: false
    },
    CONNECTION_RESTORED: {
        title: 'Connection Restored',
        icon: 'fa-wifi',
        severity: NOTIFICATION_SEVERITIES.SUCCESS,
        category: NOTIFICATION_CATEGORIES.SYSTEM,
        actionable: false
    },

    // ========================================
    // WORKFLOW EVENTS
    // ========================================
    WORKFLOW_STARTED: {
        title: 'Workflow Started',
        icon: 'fa-project-diagram',
        severity: NOTIFICATION_SEVERITIES.INFO,
        category: NOTIFICATION_CATEGORIES.SYSTEM,
        actionable: true
    },
    WORKFLOW_COMPLETED: {
        title: 'Workflow Completed',
        icon: 'fa-check-circle',
        severity: NOTIFICATION_SEVERITIES.SUCCESS,
        category: NOTIFICATION_CATEGORIES.SYSTEM,
        actionable: true
    },
    WORKFLOW_FAILED: {
        title: 'Workflow Failed',
        icon: 'fa-exclamation-triangle',
        severity: NOTIFICATION_SEVERITIES.ERROR,
        category: NOTIFICATION_CATEGORIES.SYSTEM,
        actionable: true
    }
};

/**
 * Helper function to get notification type metadata
 * @param {string} type - Notification type key
 * @returns {Object} Type metadata or default if not found
 */
function getNotificationTypeMetadata(type) {
    return NOTIFICATION_TYPES[type] || {
        title: 'Notification',
        icon: 'fa-bell',
        severity: NOTIFICATION_SEVERITIES.INFO,
        category: NOTIFICATION_CATEGORIES.SYSTEM,
        actionable: false
    };
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        NOTIFICATION_TYPES,
        NOTIFICATION_CATEGORIES,
        NOTIFICATION_SEVERITIES,
        getNotificationTypeMetadata
    };
}

// Export to window for browser usage
window.NOTIFICATION_TYPES = NOTIFICATION_TYPES;
window.NOTIFICATION_CATEGORIES = NOTIFICATION_CATEGORIES;
window.NOTIFICATION_SEVERITIES = NOTIFICATION_SEVERITIES;
window.getNotificationTypeMetadata = getNotificationTypeMetadata;

console.log('✅ Notification event types loaded:', Object.keys(NOTIFICATION_TYPES).length, 'types');
