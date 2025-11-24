/**
 * FILE: UI/js/status-indicator.js
 * PURPOSE: Bottom-left status indicator for loading states, connections, and background operations
 * 
 * FEATURES:
 * - Shows Supabase connection status
 * - Shows loading operations (Synergy, DataLoader, etc.)
 * - Auto-hides after inactivity
 * - Expandable to show details
 * - Integration with existing modules
 * 
 * EXPORTS:
 * - StatusIndicator.show(message, type, duration)
 * - StatusIndicator.hide()
 * - StatusIndicator.setStatus(status, message)
 * 
 * LAST MODIFIED: 2025-11-24 - Created status indicator system
 */

window.StatusIndicator = {
    container: null,
    statusText: null,
    statusIcon: null,
    detailsPanel: null,
    hideTimeout: null,
    currentOperations: new Map(), // Track multiple concurrent operations

    /**
     * Initialize status indicator
     */
    init() {
        if (this.container) return; // Already initialized

        // Create container
        this.container = document.createElement('div');
        this.container.id = 'status-indicator';
        this.container.className = 'status-indicator';
        this.container.innerHTML = `
            <div class="status-main">
                <span class="status-icon">⚡</span>
                <span class="status-text">Ready</span>
            </div>
            <div class="status-details" style="display: none;">
                <div class="status-operations"></div>
            </div>
        `;

        document.body.appendChild(this.container);

        // Get references
        this.statusIcon = this.container.querySelector('.status-icon');
        this.statusText = this.container.querySelector('.status-text');
        this.detailsPanel = this.container.querySelector('.status-details');
        this.operationsList = this.container.querySelector('.status-operations');

        // Add click to expand
        this.container.querySelector('.status-main').addEventListener('click', () => {
            this.toggleDetails();
        });

        console.log('✅ [Status Indicator] Initialized');

        // Auto-hide after 5 seconds of inactivity
        this.scheduleAutoHide();
    },

    /**
     * Show status message
     */
    show(message, type = 'info', duration = 3000) {
        this.init();

        // Update icon and color based on type
        const icons = {
            'loading': '⏳',
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'syncing': '🔄',
            'connected': '🔌',
            'disconnected': '🔌'
        };

        const colors = {
            'loading': '#3b82f6',
            'success': '#10b981',
            'error': '#ef4444',
            'warning': '#f59e0b',
            'info': '#6b7280',
            'syncing': '#8b5cf6',
            'connected': '#10b981',
            'disconnected': '#ef4444'
        };

        this.statusIcon.textContent = icons[type] || icons.info;
        this.statusText.textContent = message;
        this.container.style.borderLeftColor = colors[type] || colors.info;

        // Show container
        this.container.classList.remove('hidden');
        this.container.classList.add('visible');

        // Auto-hide if duration specified
        if (duration > 0 && type !== 'loading' && type !== 'syncing') {
            this.scheduleAutoHide(duration);
        } else {
            // Don't auto-hide loading/syncing states
            clearTimeout(this.hideTimeout);
        }
    },

    /**
     * Hide status indicator
     */
    hide() {
        if (this.container) {
            this.container.classList.remove('visible');
            this.container.classList.add('hidden');

            // Clear after animation
            setTimeout(() => {
                if (this.container.classList.contains('hidden')) {
                    this.container.style.display = 'none';
                }
            }, 300);
        }
    },

    /**
     * Schedule auto-hide
     */
    scheduleAutoHide(delay = 5000) {
        clearTimeout(this.hideTimeout);
        this.hideTimeout = setTimeout(() => {
            // Only hide if no active operations
            if (this.currentOperations.size === 0) {
                this.hide();
            }
        }, delay);
    },

    /**
     * Add operation to tracking
     */
    addOperation(id, message) {
        this.init();
        this.currentOperations.set(id, {
            message,
            startTime: Date.now()
        });

        this.updateOperations();
        this.show(message, 'loading', 0); // Don't auto-hide
    },

    /**
     * Remove operation from tracking
     */
    removeOperation(id, successMessage = null) {
        const operation = this.currentOperations.get(id);
        this.currentOperations.delete(id);

        this.updateOperations();

        // Show success message if provided
        if (successMessage && operation) {
            const duration = Date.now() - operation.startTime;
            this.show(`${successMessage} (${duration}ms)`, 'success', 3000);
        } else if (this.currentOperations.size === 0) {
            // All operations complete
            this.show('Ready', 'info', 3000);
        }
    },

    /**
     * Update operations display
     */
    updateOperations() {
        if (this.currentOperations.size === 0) {
            this.detailsPanel.style.display = 'none';
            return;
        }

        // Show operations in details panel
        this.operationsList.innerHTML = Array.from(this.currentOperations.entries())
            .map(([id, op]) => {
                const elapsed = ((Date.now() - op.startTime) / 1000).toFixed(1);
                return `<div class="operation-item">
                    <span class="op-spinner">⏳</span>
                    <span class="op-text">${op.message}</span>
                    <span class="op-time">${elapsed}s</span>
                </div>`;
            })
            .join('');
    },

    /**
     * Toggle details panel
     */
    toggleDetails() {
        if (this.currentOperations.size > 0) {
            const isVisible = this.detailsPanel.style.display !== 'none';
            this.detailsPanel.style.display = isVisible ? 'none' : 'block';
        }
    },

    /**
     * Set connection status
     */
    setConnectionStatus(status, service = 'Supabase') {
        const messages = {
            'connecting': `Connecting to ${service}...`,
            'connected': `${service} connected`,
            'disconnected': `${service} disconnected`,
            'reconnecting': `Reconnecting to ${service}...`
        };

        const types = {
            'connecting': 'loading',
            'connected': 'connected',
            'disconnected': 'disconnected',
            'reconnecting': 'syncing'
        };

        this.show(messages[status] || status, types[status] || 'info',
            status === 'connected' ? 2000 : 0);
    }
};

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => StatusIndicator.init());
} else {
    StatusIndicator.init();
}

console.log('📊 [Status Indicator] Module loaded');
