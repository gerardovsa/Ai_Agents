/**
 * MODAL SYSTEM - Complete Modal Management Framework
 * Version: 1.0.0
 * Created: November 12, 2025
 * 
 * Features:
 * - 8 Modal Variants: Base, Confirmation, Alert, Loading, Wizard, Drawer, Form, Multi-Action
 * - Focus Trap & Scroll Lock
 * - Keyboard Navigation (ESC, Tab, Enter)
 * - Size Variants (sm, md, lg, xl, full)
 * - Animations (fade, slide, scale)
 * - Modal Stacking & Z-index Management
 * - Responsive Design
 * - ARIA Accessibility
 * 
 * @requires design-tokens.css
 */

class ModalSystem {
    constructor() {
        this.activeModals = [];
        this.baseZIndex = 1050;
        this.modalCounter = 0;
        this.originalOverflow = '';

        console.log('[ModalSystem] Initialized');

        // Listen for ESC key globally
        document.addEventListener('keydown', (e) => this.handleGlobalKeydown(e));
    }

    /**
     * CREATE BASE MODAL
     * Foundation for all other modal types
     */
    createModal(config = {}) {
        const modal = {
            id: `modal-${++this.modalCounter}-${Date.now()}`,
            title: config.title || 'Modal',
            content: config.content || '',
            size: config.size || 'md', // sm, md, lg, xl, full
            variant: config.variant || 'default', // default, danger, warning, info, success
            animation: config.animation || 'fade', // fade, slide, scale, none
            closeOnBackdrop: config.closeOnBackdrop !== false,
            closeOnEscape: config.closeOnEscape !== false,
            showCloseButton: config.showCloseButton !== false,
            scrollLock: config.scrollLock !== false,
            focusTrap: config.focusTrap !== false,
            actions: config.actions || [],
            onOpen: config.onOpen || null,
            onClose: config.onClose || null,
            zIndex: this.baseZIndex + (this.activeModals.length * 10),
            element: null,
            backdropElement: null,
            isOpen: false
        };

        // Build modal HTML
        modal.element = this.buildModalElement(modal);
        modal.backdropElement = this.buildBackdropElement(modal);

        // Attach to body
        document.body.appendChild(modal.backdropElement);
        document.body.appendChild(modal.element);

        // Methods
        modal.show = () => this.showModal(modal);
        modal.hide = () => this.hideModal(modal);
        modal.destroy = () => this.destroyModal(modal);
        modal.updateContent = (newContent) => this.updateModalContent(modal, newContent);
        modal.updateActions = (newActions) => this.updateModalActions(modal, newActions);

        return modal;
    }

    /**
     * Build modal element
     */
    buildModalElement(modal) {
        const div = document.createElement('div');
        div.id = modal.id;
        div.className = `modal-container modal-${modal.size} modal-${modal.variant} modal-animation-${modal.animation}`;
        div.style.zIndex = modal.zIndex + 1;
        div.setAttribute('role', 'dialog');
        div.setAttribute('aria-modal', 'true');
        div.setAttribute('aria-labelledby', `${modal.id}-title`);

        const closeBtn = modal.showCloseButton
            ? `<button class="modal-close-btn" aria-label="Close modal">
                   <i class="fas fa-times"></i>
               </button>`
            : '';

        const actionsHTML = modal.actions.length > 0
            ? `<div class="modal-actions">
                   ${modal.actions.map((action, index) => this.buildActionButton(action, index)).join('')}
               </div>`
            : '';

        div.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3 class="modal-title" id="${modal.id}-title">${modal.title}</h3>
                    ${closeBtn}
                </div>
                <div class="modal-body">
                    ${modal.content}
                </div>
                ${actionsHTML}
            </div>
        `;

        // Event listeners
        if (modal.showCloseButton) {
            div.querySelector('.modal-close-btn').addEventListener('click', () => modal.hide());
        }

        // Action button listeners
        modal.actions.forEach((action, index) => {
            const btn = div.querySelector(`[data-action-index="${index}"]`);
            if (btn && action.handler) {
                btn.addEventListener('click', async () => {
                    if (action.loading) return;

                    // Show loading state
                    if (action.showLoading !== false) {
                        btn.disabled = true;
                        btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${action.loadingLabel || 'Processing...'}`;
                    }

                    try {
                        await action.handler(modal);
                    } finally {
                        if (action.showLoading !== false) {
                            btn.disabled = false;
                            btn.innerHTML = `${action.icon ? `<i class="${action.icon}"></i>` : ''} ${action.label}`;
                        }
                    }
                });
            }
        });

        return div;
    }

    /**
     * Build backdrop element
     */
    buildBackdropElement(modal) {
        const backdrop = document.createElement('div');
        backdrop.id = `${modal.id}-backdrop`;
        backdrop.className = 'modal-backdrop';
        backdrop.style.zIndex = modal.zIndex;

        if (modal.closeOnBackdrop) {
            backdrop.addEventListener('click', () => modal.hide());
        }

        return backdrop;
    }

    /**
     * Build action button
     */
    buildActionButton(action, index) {
        const variant = action.variant || 'secondary';
        const icon = action.icon ? `<i class="${action.icon}"></i>` : '';
        const disabled = action.disabled ? 'disabled' : '';

        return `
            <button class="btn btn-${variant}" 
                    data-action-index="${index}"
                    ${disabled}>
                ${icon} ${action.label}
            </button>
        `;
    }

    /**
     * Show modal
     */
    showModal(modal) {
        if (modal.isOpen) return;

        modal.isOpen = true;
        this.activeModals.push(modal);

        // Scroll lock
        if (modal.scrollLock && this.activeModals.length === 1) {
            this.originalOverflow = document.body.style.overflow;
            document.body.style.overflow = 'hidden';
        }

        // Show elements
        modal.backdropElement.classList.add('show');
        modal.element.classList.add('show');

        // Focus trap
        if (modal.focusTrap) {
            setTimeout(() => this.setFocusTrap(modal), 100);
        }

        // Callback
        if (modal.onOpen) {
            modal.onOpen(modal);
        }

        console.log(`[ModalSystem] Showed modal: ${modal.id}`);
    }

    /**
     * Hide modal
     */
    hideModal(modal) {
        if (!modal.isOpen) return;

        modal.isOpen = false;
        this.activeModals = this.activeModals.filter(m => m.id !== modal.id);

        // Remove show classes
        modal.backdropElement.classList.remove('show');
        modal.element.classList.remove('show');

        // Scroll unlock (if last modal)
        if (modal.scrollLock && this.activeModals.length === 0) {
            document.body.style.overflow = this.originalOverflow;
        }

        // Callback
        if (modal.onClose) {
            modal.onClose(modal);
        }

        console.log(`[ModalSystem] Hid modal: ${modal.id}`);
    }

    /**
     * Destroy modal
     */
    destroyModal(modal) {
        this.hideModal(modal);

        setTimeout(() => {
            modal.element?.remove();
            modal.backdropElement?.remove();
        }, 300); // Wait for animation
    }

    /**
     * Update modal content
     */
    updateModalContent(modal, newContent) {
        const body = modal.element.querySelector('.modal-body');
        if (body) {
            body.innerHTML = newContent;
        }
    }

    /**
     * Update modal actions
     */
    updateModalActions(modal, newActions) {
        modal.actions = newActions;
        const actionsContainer = modal.element.querySelector('.modal-actions');
        if (actionsContainer) {
            actionsContainer.innerHTML = newActions.map((action, index) =>
                this.buildActionButton(action, index)
            ).join('');
        }
    }

    /**
     * Focus trap implementation
     */
    setFocusTrap(modal) {
        const focusableElements = modal.element.querySelectorAll(
            'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
        );

        if (focusableElements.length === 0) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        // Focus first element
        firstElement.focus();

        // Tab trap
        modal.element.addEventListener('keydown', (e) => {
            if (e.key !== 'Tab') return;

            if (e.shiftKey) {
                if (document.activeElement === firstElement) {
                    lastElement.focus();
                    e.preventDefault();
                }
            } else {
                if (document.activeElement === lastElement) {
                    firstElement.focus();
                    e.preventDefault();
                }
            }
        });
    }

    /**
     * Global keydown handler
     */
    handleGlobalKeydown(e) {
        if (e.key === 'Escape' && this.activeModals.length > 0) {
            const topModal = this.activeModals[this.activeModals.length - 1];
            if (topModal.closeOnEscape) {
                topModal.hide();
            }
        }
    }

    /**
     * CONFIRMATION MODAL
     */
    confirm(config = {}) {
        return this.createModal({
            title: config.title || 'Confirm Action',
            content: `<p class="modal-message">${config.message || 'Are you sure?'}</p>`,
            size: config.size || 'sm',
            variant: config.variant || 'default',
            actions: [
                {
                    label: config.cancelLabel || 'Cancel',
                    variant: 'secondary',
                    icon: 'fas fa-times',
                    handler: (modal) => {
                        if (config.onCancel) config.onCancel();
                        modal.hide();
                    }
                },
                {
                    label: config.confirmLabel || 'Confirm',
                    variant: config.confirmVariant || 'primary',
                    icon: config.confirmIcon || 'fas fa-check',
                    handler: async (modal) => {
                        if (config.onConfirm) await config.onConfirm();
                        modal.hide();
                    }
                }
            ],
            onOpen: config.onOpen,
            onClose: config.onClose
        });
    }

    /**
     * ALERT MODAL
     */
    alert(config = {}) {
        return this.createModal({
            title: config.title || 'Alert',
            content: `<p class="modal-message">${config.message || ''}</p>`,
            size: config.size || 'sm',
            variant: config.variant || 'info',
            actions: [
                {
                    label: config.okLabel || 'OK',
                    variant: 'primary',
                    handler: (modal) => {
                        if (config.onOk) config.onOk();
                        modal.hide();
                    }
                }
            ],
            onOpen: config.onOpen,
            onClose: config.onClose
        });
    }

    /**
     * LOADING MODAL
     */
    loading(config = {}) {
        const spinnerId = `loading-spinner-${Date.now()}`;

        return this.createModal({
            title: config.title || 'Loading',
            content: `
                <div class="loading-modal-content">
                    <div class="loading-spinner" id="${spinnerId}">
                        <i class="fas fa-spinner fa-spin fa-3x"></i>
                    </div>
                    <p class="loading-message">${config.message || 'Please wait...'}</p>
                    ${config.progress !== undefined ? `<div class="loading-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${config.progress}%"></div>
                        </div>
                        <span class="progress-text">${config.progress}%</span>
                    </div>` : ''}
                </div>
            `,
            size: 'sm',
            showCloseButton: false,
            closeOnBackdrop: config.cancelable || false,
            closeOnEscape: config.cancelable || false,
            actions: config.cancelable ? [
                {
                    label: 'Cancel',
                    variant: 'secondary',
                    handler: (modal) => {
                        if (config.onCancel) config.onCancel();
                        modal.hide();
                    }
                }
            ] : [],
            onOpen: config.onOpen,
            onClose: config.onClose
        });
    }

    /**
     * WIZARD MODAL (Multi-step)
     */
    wizard(config = {}) {
        const steps = config.steps || [];
        let currentStep = 0;

        const renderStep = () => {
            const step = steps[currentStep];
            const isFirst = currentStep === 0;
            const isLast = currentStep === steps.length - 1;

            return `
                <div class="wizard-modal">
                    <div class="wizard-progress">
                        ${steps.map((s, i) => `
                            <div class="wizard-step ${i === currentStep ? 'active' : ''} ${i < currentStep ? 'completed' : ''}">
                                <div class="step-number">${i < currentStep ? '<i class="fas fa-check"></i>' : i + 1}</div>
                                <div class="step-title">${s.title}</div>
                            </div>
                        `).join('')}
                    </div>
                    <div class="wizard-content">
                        ${step.content}
                    </div>
                </div>
            `;
        };

        const modal = this.createModal({
            title: config.title || 'Wizard',
            content: renderStep(),
            size: config.size || 'lg',
            actions: [],
            onOpen: config.onOpen,
            onClose: config.onClose
        });

        const updateActions = () => {
            const isFirst = currentStep === 0;
            const isLast = currentStep === steps.length - 1;

            const actions = [];

            if (!isFirst) {
                actions.push({
                    label: 'Previous',
                    variant: 'secondary',
                    icon: 'fas fa-arrow-left',
                    handler: () => {
                        currentStep--;
                        modal.updateContent(renderStep());
                        updateActions();
                    }
                });
            }

            if (isLast) {
                actions.push({
                    label: config.finishLabel || 'Finish',
                    variant: 'primary',
                    icon: 'fas fa-check',
                    handler: async () => {
                        if (config.onFinish) await config.onFinish();
                        modal.hide();
                    }
                });
            } else {
                actions.push({
                    label: 'Next',
                    variant: 'primary',
                    icon: 'fas fa-arrow-right',
                    handler: () => {
                        currentStep++;
                        modal.updateContent(renderStep());
                        updateActions();
                    }
                });
            }

            modal.updateActions(actions);
        };

        updateActions();
        return modal;
    }

    /**
     * DRAWER MODAL (Side panel)
     */
    drawer(config = {}) {
        const position = config.position || 'right'; // left, right, top, bottom
        const width = config.width || '400px';

        const modal = this.createModal({
            title: config.title || 'Drawer',
            content: config.content || '',
            size: 'drawer',
            animation: 'slide',
            actions: config.actions || [],
            onOpen: config.onOpen,
            onClose: config.onClose
        });

        // Add drawer-specific classes
        modal.element.classList.add(`drawer-${position}`);
        modal.element.style.width = width;

        return modal;
    }

    /**
     * FORM MODAL (With validation)
     */
    form(config = {}) {
        const fields = config.fields || [];

        const renderForm = () => {
            return `
                <form class="modal-form" id="modal-form-${Date.now()}">
                    ${fields.map(field => this.buildFormField(field)).join('')}
                </form>
            `;
        };

        const modal = this.createModal({
            title: config.title || 'Form',
            content: renderForm(),
            size: config.size || 'md',
            actions: [
                {
                    label: config.cancelLabel || 'Cancel',
                    variant: 'secondary',
                    handler: (modal) => {
                        if (config.onCancel) config.onCancel();
                        modal.hide();
                    }
                },
                {
                    label: config.submitLabel || 'Submit',
                    variant: 'primary',
                    icon: 'fas fa-check',
                    handler: async (modal) => {
                        const formData = this.getFormData(modal);
                        const validation = this.validateForm(formData, fields);

                        if (!validation.valid) {
                            this.showFormErrors(modal, validation.errors);
                            return;
                        }

                        if (config.onSubmit) await config.onSubmit(formData);
                        modal.hide();
                    }
                }
            ],
            onOpen: config.onOpen,
            onClose: config.onClose
        });

        return modal;
    }

    /**
     * Build form field
     */
    buildFormField(field) {
        const required = field.required ? 'required' : '';
        const value = field.value || '';

        switch (field.type) {
            case 'text':
            case 'email':
            case 'number':
            case 'password':
                return `
                    <div class="form-field">
                        <label>${field.label}${field.required ? ' *' : ''}</label>
                        <input type="${field.type}" 
                               name="${field.name}" 
                               value="${value}"
                               placeholder="${field.placeholder || ''}"
                               ${required}>
                        <span class="field-error" data-field="${field.name}"></span>
                    </div>
                `;

            case 'textarea':
                return `
                    <div class="form-field">
                        <label>${field.label}${field.required ? ' *' : ''}</label>
                        <textarea name="${field.name}" 
                                  rows="${field.rows || 4}"
                                  placeholder="${field.placeholder || ''}"
                                  ${required}>${value}</textarea>
                        <span class="field-error" data-field="${field.name}"></span>
                    </div>
                `;

            case 'select':
                return `
                    <div class="form-field">
                        <label>${field.label}${field.required ? ' *' : ''}</label>
                        <select name="${field.name}" ${required}>
                            <option value="">Select...</option>
                            ${(field.options || []).map(opt =>
                    `<option value="${opt.value}" ${opt.value === value ? 'selected' : ''}>${opt.label}</option>`
                ).join('')}
                        </select>
                        <span class="field-error" data-field="${field.name}"></span>
                    </div>
                `;

            case 'checkbox':
                return `
                    <div class="form-field form-field-checkbox">
                        <label>
                            <input type="checkbox" 
                                   name="${field.name}"
                                   ${value ? 'checked' : ''}>
                            ${field.label}
                        </label>
                        <span class="field-error" data-field="${field.name}"></span>
                    </div>
                `;

            default:
                return '';
        }
    }

    /**
     * Get form data
     */
    getFormData(modal) {
        const form = modal.element.querySelector('form');
        const formData = new FormData(form);
        const data = {};

        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        return data;
    }

    /**
     * Validate form
     */
    validateForm(data, fields) {
        const errors = {};
        let valid = true;

        fields.forEach(field => {
            if (field.required && !data[field.name]) {
                errors[field.name] = field.errorMessage || `${field.label} is required`;
                valid = false;
            }

            if (field.validation && data[field.name]) {
                const validationResult = field.validation(data[field.name]);
                if (!validationResult) {
                    errors[field.name] = field.errorMessage || 'Invalid value';
                    valid = false;
                }
            }
        });

        return { valid, errors };
    }

    /**
     * Show form errors
     */
    showFormErrors(modal, errors) {
        // Clear previous errors
        modal.element.querySelectorAll('.field-error').forEach(el => {
            el.textContent = '';
            el.previousElementSibling?.classList.remove('error');
        });

        // Show new errors
        Object.entries(errors).forEach(([field, message]) => {
            const errorEl = modal.element.querySelector(`[data-field="${field}"]`);
            const inputEl = modal.element.querySelector(`[name="${field}"]`);

            if (errorEl) errorEl.textContent = message;
            if (inputEl) inputEl.classList.add('error');
        });
    }

    /**
     * Hide all modals
     */
    hideAll() {
        [...this.activeModals].forEach(modal => modal.hide());
    }

    /**
     * Destroy all modals
     */
    destroyAll() {
        [...this.activeModals].forEach(modal => modal.destroy());
    }
}

// Create global instance
if (typeof window !== 'undefined') {
    window.ModalSystem = new ModalSystem();
    console.log('[ModalSystem] Global instance created: window.ModalSystem');
}
