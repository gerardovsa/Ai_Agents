/**
 * FILE: UI/js/tabulator-toast-system.js
 * PURPOSE: Toast notification system for Tabulator enhancements - replaces alert() calls
 * 
 * FEATURES:
 * - Non-blocking notifications (success, error, warning, info)
 * - Auto-dismiss with configurable duration
 * - Stack multiple toasts
 * - Accessible (ARIA labels, keyboard support)
 * - Smooth animations
 * 
 * EXPORTS:
 * - ToastSystem class
 * 
 * LAST MODIFIED: 2025-11-07 - Initial creation
 */

class ToastSystem {
    constructor() {
        this.container = null;
        this.toasts = new Map();
        this.toastIdCounter = 0;
        this.init();
    }

    /**
     * Initialize toast container
     */
    init() {
        // Create container if it doesn't exist
        if (!document.getElementById('toast-container')) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'toast-container';
            this.container.setAttribute('role', 'region');
            this.container.setAttribute('aria-label', 'Notifications');
            this.container.setAttribute('aria-live', 'polite');
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('toast-container');
        }
    }

    /**
     * Show a toast notification
     * @param {string} message - The message to display
     * @param {string} type - Toast type: 'success', 'error', 'warning', 'info'
     * @param {Object} options - Configuration options
     * @returns {number} Toast ID for manual dismissal
     */
    show(message, type = 'info', options = {}) {
        const config = {
            duration: options.duration || 5000,
            dismissible: options.dismissible !== false,
            icon: options.icon || this.getDefaultIcon(type),
            position: options.position || 'top-right',
            ...options
        };

        const toastId = ++this.toastIdCounter;
        const toast = this.createToast(toastId, message, type, config);

        this.container.appendChild(toast);
        this.toasts.set(toastId, toast);

        // Trigger animation
        requestAnimationFrame(() => {
            toast.classList.add('toast-show');
        });

        // Auto-dismiss
        if (config.duration > 0) {
            setTimeout(() => {
                this.dismiss(toastId);
            }, config.duration);
        }

        return toastId;
    }

    /**
     * Create toast element
     */
    createToast(id, message, type, config) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.id = `toast-${id}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        const icon = document.createElement('i');
        icon.className = `fas fa-${config.icon} toast-icon`;
        icon.setAttribute('aria-hidden', 'true');

        const content = document.createElement('div');
        content.className = 'toast-content';
        content.textContent = message;

        toast.appendChild(icon);
        toast.appendChild(content);

        if (config.dismissible) {
            const closeBtn = document.createElement('button');
            closeBtn.className = 'toast-close';
            closeBtn.innerHTML = '<i class="fas fa-times"></i>';
            closeBtn.setAttribute('aria-label', 'Close notification');
            closeBtn.onclick = () => this.dismiss(id);
            toast.appendChild(closeBtn);
        }

        return toast;
    }

    /**
     * Dismiss a toast
     */
    dismiss(toastId) {
        const toast = this.toasts.get(toastId);
        if (!toast) return;

        toast.classList.add('toast-hide');

        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
            this.toasts.delete(toastId);
        }, 300);
    }

    /**
     * Get default icon for toast type
     */
    getDefaultIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    /**
     * Convenience methods
     */
    success(message, options) {
        return this.show(message, 'success', options);
    }

    error(message, options) {
        return this.show(message, 'error', options);
    }

    warning(message, options) {
        return this.show(message, 'warning', options);
    }

    info(message, options) {
        return this.show(message, 'info', options);
    }

    /**
     * Clear all toasts
     */
    clearAll() {
        this.toasts.forEach((toast, id) => {
            this.dismiss(id);
        });
    }
}

// Export to window
window.ToastSystem = ToastSystem;

// Create global instance
window.toastSystem = new ToastSystem();

console.log('[Toast System] Loaded and ready');
