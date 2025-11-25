/**
 * UI COMPONENTS - Module Component Library
 * Reusable UI components for all modules
 * 
 * Components:
 * - MetricCard: Dashboard metrics with trend indicators
 * - DataTable: Tabulator wrapper with consistent styling
 * - Chart: Plotly/Chart.js wrapper for analytics
 * - Button: Standardized button component
 * - Modal: Dialog/overlay component
 * - Toast: Notification system
 * - Badge: Status badges and tags
 * - LoadingSpinner: Loading states
 * - TabSystem: Sub-tab navigation
 * - Form: Form components with validation
 * 
 * @version 1.0.0
 * @created November 11, 2025
 * @requires design-tokens.css
 */

const UIComponents = {

    /**
     * ==================== METRIC CARD COMPONENT ====================
     * Dashboard metric cards with values, labels, and trend indicators
     * 
     * @param {Object} config
     * @param {string} config.label - Metric label
     * @param {number|string} config.value - Metric value
     * @param {string} config.format - Format type: 'number', 'currency', 'percentage'
     * @param {number} config.change - Percentage change (optional)
     * @param {string} config.trend - Trend direction: 'up', 'down', 'neutral'
     * @param {string} config.icon - Font Awesome icon class (optional)
     * @param {Function} config.onClick - Click handler (optional)
     * @param {boolean} config.loading - Show loading state
     * @returns {HTMLElement}
     */
    createMetricCard: function (config) {
        const {
            label,
            value,
            format = 'number',
            change = null,
            trend = 'neutral',
            icon = null,
            onClick = null,
            loading = false
        } = config;

        const card = document.createElement('div');
        card.className = `metric-card ${onClick ? 'cursor-pointer hover-bg-hover' : ''} ${loading ? 'loading' : ''}`;

        if (onClick) {
            card.addEventListener('click', onClick);
        }

        // Format value based on type
        let formattedValue = value;
        if (!loading) {
            switch (format) {
                case 'currency':
                    formattedValue = new Intl.NumberFormat('en-US', {
                        style: 'currency',
                        currency: 'USD',
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 0
                    }).format(value);
                    break;
                case 'percentage':
                    formattedValue = `${value}%`;
                    break;
                case 'number':
                default:
                    formattedValue = new Intl.NumberFormat('en-US').format(value);
                    break;
            }
        }

        // Determine trend color
        const trendColor = trend === 'up' ? 'success' : trend === 'down' ? 'error' : 'muted';
        const trendIcon = trend === 'up' ? 'fa-arrow-up' : trend === 'down' ? 'fa-arrow-down' : 'fa-minus';

        card.innerHTML = `
            ${icon ? `<div class="metric-icon"><i class="${icon}"></i></div>` : ''}
            <div class="metric-content">
                ${loading ? `
                    <div class="metric-value-skeleton"></div>
                    <div class="metric-label-skeleton"></div>
                ` : `
                    <div class="metric-value">${formattedValue}</div>
                    <div class="metric-label">${label}</div>
                    ${change !== null ? `
                        <div class="metric-change text-${trendColor}">
                            <i class="fas ${trendIcon}"></i>
                            ${Math.abs(change)}%
                        </div>
                    ` : ''}
                `}
            </div>
        `;

        return card;
    },

    /**
     * ==================== BUTTON COMPONENT ====================
     * Standardized button with variants, sizes, loading states
     * 
     * @param {Object} config
     * @param {string} config.label - Button text
     * @param {string} config.variant - Style: 'primary', 'secondary', 'danger', 'success', 'ghost'
     * @param {string} config.size - Size: 'sm', 'md', 'lg'
     * @param {string} config.icon - Font Awesome icon class (optional)
     * @param {string} config.iconPosition - Icon position: 'left', 'right', 'only'
     * @param {boolean} config.loading - Show loading spinner
     * @param {boolean} config.disabled - Disabled state
     * @param {Function} config.onClick - Click handler
     * @param {string} config.type - Button type: 'button', 'submit'
     * @returns {HTMLElement}
     */
    createButton: function (config) {
        const {
            label,
            variant = 'primary',
            size = 'md',
            icon = null,
            iconPosition = 'left',
            loading = false,
            disabled = false,
            onClick = null,
            type = 'button'
        } = config;

        const button = document.createElement('button');
        button.type = type;
        button.className = `btn btn-${variant} btn-${size}`;
        button.disabled = disabled || loading;

        if (onClick) {
            button.addEventListener('click', onClick);
        }

        if (loading) {
            button.innerHTML = `
                <i class="fas fa-circle-notch fa-spin"></i>
                ${iconPosition !== 'only' ? '<span>Loading...</span>' : ''}
            `;
        } else if (iconPosition === 'only' && icon) {
            button.innerHTML = `<i class="${icon}"></i>`;
            button.classList.add('btn-icon');
        } else if (icon && iconPosition === 'left') {
            button.innerHTML = `<i class="${icon}"></i><span>${label}</span>`;
        } else if (icon && iconPosition === 'right') {
            button.innerHTML = `<span>${label}</span><i class="${icon}"></i>`;
        } else {
            button.textContent = label;
        }

        return button;
    },

    /**
     * ==================== BADGE COMPONENT ====================
     * Status badges and tags
     * 
     * @param {Object} config
     * @param {string} config.label - Badge text
     * @param {string} config.variant - Style: 'success', 'error', 'warning', 'info', 'primary'
     * @param {number} config.count - Count badge (optional)
     * @param {boolean} config.dot - Show dot variant
     * @param {boolean} config.removable - Show remove button
     * @param {Function} config.onRemove - Remove handler
     * @returns {HTMLElement}
     */
    createBadge: function (config) {
        const {
            label,
            variant = 'primary',
            count = null,
            dot = false,
            removable = false,
            onRemove = null
        } = config;

        const badge = document.createElement('span');
        badge.className = `badge badge-${variant} ${dot ? 'badge-dot' : ''}`;

        if (count !== null) {
            badge.innerHTML = `<span class="badge-count">${count}</span>`;
        } else if (dot) {
            badge.innerHTML = `<span class="badge-dot-indicator"></span>${label}`;
        } else {
            badge.textContent = label;
        }

        if (removable && onRemove) {
            const removeBtn = document.createElement('button');
            removeBtn.className = 'badge-remove';
            removeBtn.innerHTML = '<i class="fas fa-times"></i>';
            removeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                onRemove();
            });
            badge.appendChild(removeBtn);
        }

        return badge;
    },

    /**
     * ==================== LOADING SPINNER ====================
     * Loading indicators
     * 
     * @param {Object} config
     * @param {string} config.size - Size: 'sm', 'md', 'lg'
     * @param {string} config.type - Type: 'spinner', 'dots', 'pulse'
     * @param {string} config.overlay - Show as overlay
     * @returns {HTMLElement}
     */
    createLoadingSpinner: function (config = {}) {
        const {
            size = 'md',
            type = 'spinner',
            overlay = false
        } = config;

        const container = document.createElement('div');
        container.className = `loading-container loading-${size} ${overlay ? 'loading-overlay' : ''}`;

        if (type === 'spinner') {
            container.innerHTML = '<div class="loading-spinner"></div>';
        } else if (type === 'dots') {
            container.innerHTML = `
                <div class="loading-dots">
                    <span></span><span></span><span></span>
                </div>
            `;
        } else if (type === 'pulse') {
            container.innerHTML = '<div class="loading-pulse"></div>';
        }

        return container;
    },

    /**
     * ==================== MODAL COMPONENT ====================
     * Dialog/overlay component with actions
     * 
     * @param {Object} config
     * @param {string} config.title - Modal title
     * @param {string|HTMLElement} config.content - Modal content
     * @param {string} config.size - Size: 'sm', 'md', 'lg', 'xl', 'full'
     * @param {Array} config.actions - Action buttons [{label, variant, handler}]
     * @param {boolean} config.closeOnBackdrop - Close on backdrop click
     * @param {boolean} config.closeOnEscape - Close on escape key
     * @param {Function} config.onClose - Close callback
     * @returns {Object} Modal instance with show/hide methods
     */
    createModal: function (config) {
        const {
            title,
            content,
            size = 'md',
            actions = [],
            closeOnBackdrop = true,
            closeOnEscape = true,
            onClose = null
        } = config;

        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.style.display = 'none';

        const modalContent = document.createElement('div');
        modalContent.className = `modal-content modal-${size}`;

        // Header
        const header = document.createElement('div');
        header.className = 'modal-header';
        header.innerHTML = `
            <h3 class="modal-title">${title}</h3>
            <button class="modal-close" aria-label="Close">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Body
        const body = document.createElement('div');
        body.className = 'modal-body';
        if (typeof content === 'string') {
            body.innerHTML = content;
        } else {
            body.appendChild(content);
        }

        // Footer
        const footer = document.createElement('div');
        footer.className = 'modal-footer';
        actions.forEach(action => {
            const btn = UIComponents.createButton({
                label: action.label,
                variant: action.variant || 'secondary',
                onClick: action.handler
            });
            footer.appendChild(btn);
        });

        modalContent.appendChild(header);
        modalContent.appendChild(body);
        if (actions.length > 0) {
            modalContent.appendChild(footer);
        }

        modal.appendChild(modalContent);
        document.body.appendChild(modal);

        // Close handler
        const closeModal = () => {
            modal.style.display = 'none';
            document.body.style.overflow = '';
            if (onClose) onClose();
        };

        // Close button
        header.querySelector('.modal-close').addEventListener('click', closeModal);

        // Backdrop click
        if (closeOnBackdrop) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) closeModal();
            });
        }

        // Escape key
        if (closeOnEscape) {
            const escapeHandler = (e) => {
                if (e.key === 'Escape' && modal.style.display !== 'none') {
                    closeModal();
                }
            };
            document.addEventListener('keydown', escapeHandler);
            modal._escapeHandler = escapeHandler;
        }

        return {
            element: modal,
            show: () => {
                modal.style.display = 'flex';
                document.body.style.overflow = 'hidden';
                // Focus trap
                modalContent.querySelector('button, input, select, textarea')?.focus();
            },
            hide: closeModal,
            destroy: () => {
                if (modal._escapeHandler) {
                    document.removeEventListener('keydown', modal._escapeHandler);
                }
                modal.remove();
            }
        };
    },

    /**
     * ==================== TOAST NOTIFICATION ====================
     * Toast notification system
     * 
     * @param {Object} config
     * @param {string} config.message - Toast message
     * @param {string} config.variant - Style: 'success', 'error', 'warning', 'info'
     * @param {number} config.duration - Auto-dismiss duration (ms), 0 = no auto-dismiss
     * @param {Object} config.action - Action button {label, handler}
     * @param {string} config.position - Position: 'top-right', 'top-left', 'bottom-right', 'bottom-left'
     */
    showToast: function (config) {
        const {
            message,
            variant = 'info',
            duration = 3000,
            action = null,
            position = 'top-right'
        } = config;

        // Get or create toast container
        let container = document.querySelector(`.toast-container-${position}`);
        if (!container) {
            container = document.createElement('div');
            container.className = `toast-container toast-container-${position}`;
            document.body.appendChild(container);
        }

        // Create toast
        const toast = document.createElement('div');
        toast.className = `toast toast-${variant}`;

        const icon = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        }[variant];

        toast.innerHTML = `
            <div class="toast-icon">
                <i class="fas ${icon}"></i>
            </div>
            <div class="toast-content">
                <div class="toast-message">${message}</div>
                ${action ? `<button class="toast-action">${action.label}</button>` : ''}
            </div>
            <button class="toast-close">
                <i class="fas fa-times"></i>
            </button>
        `;

        container.appendChild(toast);

        // Animate in
        setTimeout(() => toast.classList.add('toast-show'), 10);

        // Action handler
        if (action) {
            toast.querySelector('.toast-action').addEventListener('click', () => {
                action.handler();
                removeToast();
            });
        }

        // Close handler
        const removeToast = () => {
            toast.classList.remove('toast-show');
            setTimeout(() => toast.remove(), 300);
        };

        toast.querySelector('.toast-close').addEventListener('click', removeToast);

        // Auto-dismiss
        if (duration > 0) {
            setTimeout(removeToast, duration);
        }
    },

    /**
     * ==================== TAB SYSTEM ====================
     * Sub-tab navigation system
     * 
     * @param {Object} config
     * @param {Array} config.tabs - Tab definitions [{id, label, icon, badge}]
     * @param {string} config.activeTab - Initially active tab ID
     * @param {Function} config.onTabChange - Tab change callback
     * @param {HTMLElement} config.container - Container element
     * @returns {Object} Tab system with methods
     */
    createTabSystem: function (config) {
        const {
            tabs,
            activeTab,
            onTabChange,
            container
        } = config;

        // Create tab navigation
        const tabNav = document.createElement('div');
        tabNav.className = 'module-subtabs';

        tabs.forEach(tab => {
            const btn = document.createElement('button');
            btn.className = `subtab-btn ${tab.id === activeTab ? 'active' : ''}`;
            btn.dataset.subtab = tab.id;

            btn.innerHTML = `
                ${tab.icon ? `<i class="${tab.icon}"></i>` : ''}
                <span>${tab.label}</span>
                ${tab.badge ? `<span class="badge badge-${tab.badge.variant}">${tab.badge.count}</span>` : ''}
            `;

            btn.addEventListener('click', () => {
                // Remove active from all
                tabNav.querySelectorAll('.subtab-btn').forEach(b => b.classList.remove('active'));
                // Add active to clicked
                btn.classList.add('active');
                // Trigger callback
                if (onTabChange) onTabChange(tab.id);
            });

            tabNav.appendChild(btn);
        });

        container.appendChild(tabNav);

        return {
            setActive: (tabId) => {
                const btn = tabNav.querySelector(`[data-subtab="${tabId}"]`);
                if (btn) {
                    btn.click();
                }
            },
            updateBadge: (tabId, count, variant = 'primary') => {
                const btn = tabNav.querySelector(`[data-subtab="${tabId}"]`);
                if (btn) {
                    let badge = btn.querySelector('.badge');
                    if (!badge) {
                        badge = document.createElement('span');
                        btn.appendChild(badge);
                    }
                    badge.className = `badge badge-${variant}`;
                    badge.textContent = count;
                }
            }
        };
    },

    /**
     * ==================== DATA TABLE ====================
     * Tabulator wrapper with consistent configuration
     * 
     * @param {Object} config
     * @param {HTMLElement} config.container - Container element
     * @param {Array} config.columns - Column definitions
     * @param {Array} config.data - Table data
     * @param {Object} config.options - Additional Tabulator options
     * @returns {Tabulator} Tabulator instance
     */
    createDataTable: function (config) {
        const {
            container,
            columns,
            data = [],
            options = {}
        } = config;

        const defaultOptions = {
            layout: 'fitDataStretch',
            responsiveLayout: 'collapse',
            pagination: true,
            paginationSize: 25,
            paginationSizeSelector: [10, 25, 50, 100],
            movableColumns: true,
            resizableColumns: true,
            height: '600px',
            placeholder: 'No data available',
            data: data,
            columns: columns
        };

        const table = new Tabulator(container, { ...defaultOptions, ...options });

        // Apply dark theme (if available)
        if (window.TabulatorThemeAdapter) {
            table.on('renderComplete', function () {
                window.TabulatorThemeAdapter.applyDarkTheme(this);
            });
        }

        return table;
    },

    /**
     * ==================== MODAL SHORTCUTS ====================
     * Convenience methods for common modal patterns
     * Note: These use the ModalSystem (modal-system.js) if available
     */

    /**
     * Show confirmation dialog
     * @param {Object} config
     * @param {string} config.title - Dialog title
     * @param {string} config.message - Confirmation message
     * @param {Function} config.onConfirm - Confirm callback
     * @param {Function} config.onCancel - Cancel callback
     * @param {string} config.confirmLabel - Confirm button label (default: 'Confirm')
     * @param {string} config.cancelLabel - Cancel button label (default: 'Cancel')
     * @param {string} config.variant - Variant: 'danger', 'warning', 'info' (default: 'default')
     * @returns {Object} Modal instance
     */
    showConfirmation: function (config) {
        if (window.ModalSystem) {
            const modal = window.ModalSystem.confirm({
                title: config.title || 'Confirm Action',
                message: config.message || 'Are you sure?',
                confirmLabel: config.confirmLabel || 'Confirm',
                cancelLabel: config.cancelLabel || 'Cancel',
                variant: config.variant || 'default',
                confirmVariant: config.variant === 'danger' ? 'danger' : 'primary',
                confirmIcon: config.confirmIcon || (config.variant === 'danger' ? 'fas fa-trash' : 'fas fa-check'),
                onConfirm: config.onConfirm,
                onCancel: config.onCancel
            });
            modal.show();
            return modal;
        } else {
            console.warn('[UIComponents] ModalSystem not loaded, rendering DOM confirmation modal');

            // Create a simple DOM modal as a fallback instead of using native confirm()
            const overlay = document.createElement('div');
            overlay.className = 'uicomponents-confirm-overlay';
            overlay.style.position = 'fixed';
            overlay.style.inset = '0';
            overlay.style.background = 'rgba(0,0,0,0.5)';
            overlay.style.display = 'flex';
            overlay.style.alignItems = 'center';
            overlay.style.justifyContent = 'center';
            overlay.style.zIndex = 99999;

            const dialog = document.createElement('div');
            dialog.className = 'uicomponents-confirm-dialog';
            dialog.style.background = 'var(--bg-primary, #0b1220)';
            dialog.style.color = 'var(--text-primary, #e6edf3)';
            dialog.style.border = '1px solid var(--border-color, #374151)';
            dialog.style.padding = '18px';
            dialog.style.borderRadius = '8px';
            dialog.style.minWidth = '320px';
            dialog.style.maxWidth = '480px';
            dialog.style.boxShadow = '0 8px 24px rgba(0,0,0,0.6)';

            const titleEl = document.createElement('div');
            titleEl.style.fontWeight = 700;
            titleEl.style.marginBottom = '8px';
            titleEl.textContent = config.title || 'Confirm Action';

            const msgEl = document.createElement('div');
            msgEl.style.marginBottom = '14px';
            msgEl.style.lineHeight = '1.4';
            msgEl.textContent = config.message || 'Are you sure?';

            const actions = document.createElement('div');
            actions.style.display = 'flex';
            actions.style.justifyContent = 'flex-end';
            actions.style.gap = '8px';

            const cancelBtn = document.createElement('button');
            cancelBtn.className = 'btn btn-secondary';
            cancelBtn.textContent = config.cancelLabel || 'Cancel';

            const confirmBtn = document.createElement('button');
            confirmBtn.className = 'btn btn-primary';
            confirmBtn.textContent = config.confirmLabel || 'Confirm';

            actions.appendChild(cancelBtn);
            actions.appendChild(confirmBtn);

            dialog.appendChild(titleEl);
            dialog.appendChild(msgEl);
            dialog.appendChild(actions);
            overlay.appendChild(dialog);
            document.body.appendChild(overlay);

            // Focus handling
            confirmBtn.focus();

            const cleanup = () => {
                try { overlay.remove(); } catch (e) { /* ignore */ }
            };

            cancelBtn.addEventListener('click', () => {
                cleanup();
                if (config.onCancel) config.onCancel();
            });

            confirmBtn.addEventListener('click', () => {
                cleanup();
                if (config.onConfirm) config.onConfirm();
            });

            // Return a lightweight modal-like object
            return {
                element: overlay,
                show: () => { overlay.style.display = 'flex'; },
                hide: () => { overlay.style.display = 'none'; },
                destroy: cleanup
            };
        }
    },

    /**
     * Show alert dialog
     * @param {Object} config
     * @param {string} config.title - Alert title
     * @param {string} config.message - Alert message
     * @param {string} config.variant - Variant: 'success', 'error', 'warning', 'info' (default: 'info')
     * @param {Function} config.onOk - OK callback
     * @returns {Object} Modal instance
     */
    showAlert: function (config) {
        if (window.ModalSystem) {
            const modal = window.ModalSystem.alert({
                title: config.title || 'Alert',
                message: config.message || '',
                variant: config.variant || 'info',
                okLabel: config.okLabel || 'OK',
                onOk: config.onOk
            });
            modal.show();
            return modal;
        } else {
            console.warn('[UIComponents] ModalSystem not loaded, falling back to native alert');
            alert(`${config.title}\n\n${config.message}`);
            if (config.onOk) config.onOk();
        }
    },

    /**
     * Show loading modal
     * @param {Object} config
     * @param {string} config.title - Loading title
     * @param {string} config.message - Loading message
     * @param {boolean} config.cancelable - Allow cancellation (default: false)
     * @param {number} config.progress - Progress percentage (0-100, optional)
     * @param {Function} config.onCancel - Cancel callback
     * @returns {Object} Modal instance with updateProgress(percent) method
     */
    showLoading: function (config) {
        if (window.ModalSystem) {
            const modal = window.ModalSystem.loading({
                title: config.title || 'Loading',
                message: config.message || 'Please wait...',
                cancelable: config.cancelable || false,
                progress: config.progress,
                onCancel: config.onCancel
            });

            // Add updateProgress method
            modal.updateProgress = function (percent) {
                const progressFill = modal.element.querySelector('.progress-fill');
                const progressText = modal.element.querySelector('.progress-text');
                if (progressFill) progressFill.style.width = `${percent}%`;
                if (progressText) progressText.textContent = `${percent}%`;
            };

            modal.show();
            return modal;
        } else {
            console.warn('[UIComponents] ModalSystem not loaded, using loading spinner');
            const spinner = this.createLoadingSpinner({ size: 'lg', overlay: true });
            document.body.appendChild(spinner);
            return {
                hide: () => spinner.remove(),
                destroy: () => spinner.remove(),
                updateProgress: () => { }
            };
        }
    },

    /**
     * Show wizard (multi-step) modal
     * @param {Object} config
     * @param {string} config.title - Wizard title
     * @param {Array} config.steps - Array of steps: [{ title, content }, ...]
     * @param {Function} config.onFinish - Finish callback
     * @param {string} config.size - Modal size (default: 'lg')
     * @returns {Object} Modal instance
     */
    showWizard: function (config) {
        if (window.ModalSystem) {
            const modal = window.ModalSystem.wizard({
                title: config.title || 'Wizard',
                steps: config.steps || [],
                finishLabel: config.finishLabel || 'Finish',
                size: config.size || 'lg',
                onFinish: config.onFinish
            });
            modal.show();
            return modal;
        } else {
            console.warn('[UIComponents] ModalSystem not loaded, wizard not available');
            return null;
        }
    },

    /**
     * Show drawer (side panel)
     * @param {Object} config
     * @param {string} config.title - Drawer title
     * @param {string} config.content - Drawer HTML content
     * @param {string} config.position - Position: 'left', 'right', 'top', 'bottom' (default: 'right')
     * @param {string} config.width - Drawer width (default: '400px')
     * @param {Array} config.actions - Action buttons
     * @returns {Object} Modal instance
     */
    showDrawer: function (config) {
        if (window.ModalSystem) {
            const modal = window.ModalSystem.drawer({
                title: config.title || 'Drawer',
                content: config.content || '',
                position: config.position || 'right',
                width: config.width || '400px',
                actions: config.actions || []
            });
            modal.show();
            return modal;
        } else {
            console.warn('[UIComponents] ModalSystem not loaded, drawer not available');
            return null;
        }
    },

    /**
     * Show form modal
     * @param {Object} config
     * @param {string} config.title - Form title
     * @param {Array} config.fields - Form fields array
     * @param {Function} config.onSubmit - Submit callback
     * @param {Function} config.onCancel - Cancel callback
     * @param {string} config.submitLabel - Submit button label (default: 'Submit')
     * @param {string} config.size - Modal size (default: 'md')
     * @returns {Object} Modal instance
     */
    showForm: function (config) {
        if (window.ModalSystem) {
            const modal = window.ModalSystem.form({
                title: config.title || 'Form',
                fields: config.fields || [],
                submitLabel: config.submitLabel || 'Submit',
                cancelLabel: config.cancelLabel || 'Cancel',
                size: config.size || 'md',
                onSubmit: config.onSubmit,
                onCancel: config.onCancel
            });
            modal.show();
            return modal;
        } else {
            console.warn('[UIComponents] ModalSystem not loaded, form not available');
            return null;
        }
    }
};

// Export for use in modules
if (typeof window !== 'undefined') {
    window.UIComponents = UIComponents;
}
