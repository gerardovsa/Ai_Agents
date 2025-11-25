/**
 * FILE: UI/module_builder/templates/form-module/form-module.js
 * PURPOSE: Form module template with validation, multi-step forms, and data entry
 * 
 * TEMPLATE TYPE: Forms/Data Entry
 * USE CASE: Modules requiring complex forms, validation, multi-step wizards
 * 
 * FEATURES:
 * - Multi-step form wizard
 * - Real-time validation
 * - Auto-save functionality
 * - File upload support
 * - Progress tracking
 * - Form state management
 * 
 * DEPENDENCIES:
 * - ui-components.js (required)
 * - design-tokens.css (required)
 * - modal-system.js (required)
 * 
 * EXPORTS:
 * - FormModule class - Main form module class
 * 
 * LAST MODIFIED: 2025-11-12 - Initial template creation
 */

class FormModule {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.currentStep = 1;
        this.totalSteps = 3;
        this.formData = {};
        this.autoSaveTimer = null;
        this.config = {
            enableValidation: true,
            enableAutosave: true,
            autosaveInterval: 30000 // 30 seconds
        };

        if (!this.container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        this.init();
    }

    /**
     * Initialize the form module
     */
    init() {
        this.render();
        this.attachEventListeners();
        this.loadSavedData();

        if (this.config.enableAutosave) {
            this.startAutosave();
        }
    }

    /**
     * Render the form UI
     */
    render() {
        this.container.innerHTML = `
            <div class="form-module">
                <!-- Header -->
                <div class="form-header">
                    <h2 class="form-title">
                        <span class="form-icon">📝</span>
                        Multi-Step Form
                    </h2>
                    <div class="header-actions">
                        <button class="btn-icon" id="resetFormBtn" title="Reset Form">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                                <path d="M2.5 1a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1H3v9a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V4h.5a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H10a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1H2.5zm3 4a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5zM8 5a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7A.5.5 0 0 1 8 5zm3 .5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 1 0z"/>
                            </svg>
                        </button>
                        <button class="btn-icon" id="helpBtn" title="Help">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                                <path d="M5.255 5.786a.237.237 0 0 0 .241.247h.825c.138 0 .248-.113.266-.25.09-.656.54-1.134 1.342-1.134.686 0 1.314.343 1.314 1.168 0 .635-.374.927-.965 1.371-.673.489-1.206 1.06-1.168 1.987l.003.217a.25.25 0 0 0 .25.246h.811a.25.25 0 0 0 .25-.25v-.105c0-.718.273-.927 1.01-1.486.609-.463 1.244-.977 1.244-2.056 0-1.511-1.276-2.241-2.673-2.241-1.267 0-2.655.59-2.75 2.286zm1.557 5.763c0 .533.425.927 1.01.927.609 0 1.028-.394 1.028-.927 0-.552-.42-.94-1.029-.94-.584 0-1.009.388-1.009.94z"/>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <!-- Progress Bar -->
                <div class="form-progress">
                    <div class="progress-steps">
                        ${Array.from({ length: this.totalSteps }, (_, i) => `
                            <div class="progress-step ${i + 1 === this.currentStep ? 'active' : i + 1 < this.currentStep ? 'completed' : ''}" data-step="${i + 1}">
                                <div class="step-number">${i + 1}</div>
                                <div class="step-label">${this.getStepLabel(i + 1)}</div>
                            </div>
                            ${i < this.totalSteps - 1 ? '<div class="progress-connector"></div>' : ''}
                        `).join('')}
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${(this.currentStep / this.totalSteps) * 100}%"></div>
                    </div>
                </div>
                
                <!-- Form Content -->
                <div class="form-content">
                    <form id="mainForm" novalidate>
                        <div id="formStepsContainer"></div>
                    </form>
                </div>
                
                <!-- Form Actions -->
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" id="prevBtn" ${this.currentStep === 1 ? 'disabled' : ''}>
                        ← Previous
                    </button>
                    <div class="form-actions-right">
                        <button type="button" class="btn btn-secondary" id="saveBtn">
                            💾 Save Draft
                        </button>
                        <button type="button" class="btn btn-primary" id="nextBtn">
                            ${this.currentStep === this.totalSteps ? 'Submit' : 'Next →'}
                        </button>
                    </div>
                </div>
                
                <!-- Footer -->
                <div class="form-footer">
                    <span class="footer-text">
                        Form Module Template v1.0.0
                        ${this.config.enableAutosave ? ' • Auto-save enabled' : ''}
                    </span>
                </div>
            </div>
        `;

        this.renderCurrentStep();
    }

    /**
     * Get step label
     */
    getStepLabel(step) {
        const labels = ['Personal Info', 'Details', 'Review'];
        return labels[step - 1] || `Step ${step}`;
    }

    /**
     * Render current form step
     */
    renderCurrentStep() {
        const container = document.getElementById('formStepsContainer');
        if (!container) return;

        container.innerHTML = this.getStepContent(this.currentStep);
        this.updateProgress();
    }

    /**
     * Get form step content
     */
    getStepContent(step) {
        switch (step) {
            case 1:
                return `
                    <div class="form-step" data-step="1">
                        <h3 class="step-title">Personal Information</h3>
                        <p class="step-description">Please provide your basic information</p>
                        
                        <div class="form-group">
                            <label for="firstName" class="form-label required">First Name</label>
                            <input 
                                type="text" 
                                id="firstName" 
                                name="firstName" 
                                class="form-input" 
                                required 
                                placeholder="Enter your first name"
                                value="${this.formData.firstName || ''}"
                            >
                            <div class="form-error" id="firstName-error"></div>
                        </div>
                        
                        <div class="form-group">
                            <label for="lastName" class="form-label required">Last Name</label>
                            <input 
                                type="text" 
                                id="lastName" 
                                name="lastName" 
                                class="form-input" 
                                required 
                                placeholder="Enter your last name"
                                value="${this.formData.lastName || ''}"
                            >
                            <div class="form-error" id="lastName-error"></div>
                        </div>
                        
                        <div class="form-group">
                            <label for="email" class="form-label required">Email Address</label>
                            <input 
                                type="email" 
                                id="email" 
                                name="email" 
                                class="form-input" 
                                required 
                                placeholder="your.email@example.com"
                                value="${this.formData.email || ''}"
                            >
                            <div class="form-error" id="email-error"></div>
                        </div>
                        
                        <div class="form-group">
                            <label for="phone" class="form-label">Phone Number</label>
                            <input 
                                type="tel" 
                                id="phone" 
                                name="phone" 
                                class="form-input" 
                                placeholder="(123) 456-7890"
                                value="${this.formData.phone || ''}"
                            >
                            <div class="form-help">Optional</div>
                        </div>
                    </div>
                `;

            case 2:
                return `
                    <div class="form-step" data-step="2">
                        <h3 class="step-title">Additional Details</h3>
                        <p class="step-description">Tell us more about yourself</p>
                        
                        <div class="form-group">
                            <label for="company" class="form-label">Company Name</label>
                            <input 
                                type="text" 
                                id="company" 
                                name="company" 
                                class="form-input" 
                                placeholder="Enter company name"
                                value="${this.formData.company || ''}"
                            >
                        </div>
                        
                        <div class="form-group">
                            <label for="industry" class="form-label required">Industry</label>
                            <select id="industry" name="industry" class="form-select" required>
                                <option value="">Select an industry</option>
                                <option value="tech" ${this.formData.industry === 'tech' ? 'selected' : ''}>Technology</option>
                                <option value="finance" ${this.formData.industry === 'finance' ? 'selected' : ''}>Finance</option>
                                <option value="healthcare" ${this.formData.industry === 'healthcare' ? 'selected' : ''}>Healthcare</option>
                                <option value="retail" ${this.formData.industry === 'retail' ? 'selected' : ''}>Retail</option>
                                <option value="other" ${this.formData.industry === 'other' ? 'selected' : ''}>Other</option>
                            </select>
                            <div class="form-error" id="industry-error"></div>
                        </div>
                        
                        <div class="form-group">
                            <label for="message" class="form-label">Message</label>
                            <textarea 
                                id="message" 
                                name="message" 
                                class="form-textarea" 
                                rows="4" 
                                placeholder="Enter your message..."
                            >${this.formData.message || ''}</textarea>
                            <div class="form-help">Maximum 500 characters</div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-checkbox">
                                <input 
                                    type="checkbox" 
                                    id="newsletter" 
                                    name="newsletter" 
                                    ${this.formData.newsletter ? 'checked' : ''}
                                >
                                <span>Subscribe to newsletter</span>
                            </label>
                        </div>
                    </div>
                `;

            case 3:
                return `
                    <div class="form-step" data-step="3">
                        <h3 class="step-title">Review & Submit</h3>
                        <p class="step-description">Please review your information before submitting</p>
                        
                        <div class="review-section">
                            <h4 class="review-title">Personal Information</h4>
                            <div class="review-grid">
                                <div class="review-item">
                                    <span class="review-label">Name:</span>
                                    <span class="review-value">${this.formData.firstName || ''} ${this.formData.lastName || ''}</span>
                                </div>
                                <div class="review-item">
                                    <span class="review-label">Email:</span>
                                    <span class="review-value">${this.formData.email || ''}</span>
                                </div>
                                <div class="review-item">
                                    <span class="review-label">Phone:</span>
                                    <span class="review-value">${this.formData.phone || 'Not provided'}</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="review-section">
                            <h4 class="review-title">Additional Details</h4>
                            <div class="review-grid">
                                <div class="review-item">
                                    <span class="review-label">Company:</span>
                                    <span class="review-value">${this.formData.company || 'Not provided'}</span>
                                </div>
                                <div class="review-item">
                                    <span class="review-label">Industry:</span>
                                    <span class="review-value">${this.formData.industry || 'Not selected'}</span>
                                </div>
                                <div class="review-item">
                                    <span class="review-label">Newsletter:</span>
                                    <span class="review-value">${this.formData.newsletter ? 'Yes' : 'No'}</span>
                                </div>
                                ${this.formData.message ? `
                                <div class="review-item full-width">
                                    <span class="review-label">Message:</span>
                                    <span class="review-value">${this.formData.message}</span>
                                </div>
                                ` : ''}
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-checkbox">
                                <input 
                                    type="checkbox" 
                                    id="terms" 
                                    name="terms" 
                                    required
                                    ${this.formData.terms ? 'checked' : ''}
                                >
                                <span class="required">I agree to the terms and conditions</span>
                            </label>
                            <div class="form-error" id="terms-error"></div>
                        </div>
                    </div>
                `;

            default:
                return '<div>Invalid step</div>';
        }
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        const prevBtn = this.container.querySelector('#prevBtn');
        const nextBtn = this.container.querySelector('#nextBtn');
        const saveBtn = this.container.querySelector('#saveBtn');
        const resetBtn = this.container.querySelector('#resetFormBtn');
        const helpBtn = this.container.querySelector('#helpBtn');

        prevBtn?.addEventListener('click', () => this.previousStep());
        nextBtn?.addEventListener('click', () => this.nextStep());
        saveBtn?.addEventListener('click', () => this.saveDraft());
        resetBtn?.addEventListener('click', () => this.resetForm());
        helpBtn?.addEventListener('click', () => this.showHelp());

        // Add input listeners for validation
        this.container.addEventListener('input', (e) => {
            if (e.target.matches('.form-input, .form-select, .form-textarea')) {
                this.validateField(e.target);
            }
        });
    }

    /**
     * Next step
     */
    async nextStep() {
        // Save current step data
        this.saveStepData();

        // Validate current step
        if (this.config.enableValidation && !this.validateStep()) {
            return;
        }

        // If last step, submit form
        if (this.currentStep === this.totalSteps) {
            await this.submitForm();
            return;
        }

        // Move to next step
        this.currentStep++;
        this.render();
        this.attachEventListeners();
    }

    /**
     * Previous step
     */
    previousStep() {
        if (this.currentStep > 1) {
            this.saveStepData();
            this.currentStep--;
            this.render();
            this.attachEventListeners();
        }
    }

    /**
     * Save current step data
     */
    saveStepData() {
        const form = this.container.querySelector('#mainForm');
        if (!form) return;

        const formData = new FormData(form);
        for (const [key, value] of formData.entries()) {
            this.formData[key] = value;
        }

        // Handle checkboxes separately
        const checkboxes = form.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            this.formData[checkbox.name] = checkbox.checked;
        });
    }

    /**
     * Validate current step
     */
    validateStep() {
        const form = this.container.querySelector('#mainForm');
        if (!form) return true;

        const inputs = form.querySelectorAll('[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        return isValid;
    }

    /**
     * Validate individual field
     */
    validateField(field) {
        const errorDiv = document.getElementById(`${field.id}-error`);
        if (!errorDiv) return true;

        let error = '';

        if (field.hasAttribute('required') && !field.value.trim()) {
            error = 'This field is required';
        } else if (field.type === 'email' && field.value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(field.value)) {
                error = 'Please enter a valid email address';
            }
        }

        if (error) {
            errorDiv.textContent = error;
            field.classList.add('error');
            return false;
        } else {
            errorDiv.textContent = '';
            field.classList.remove('error');
            return true;
        }
    }

    /**
     * Submit form
     */
    async submitForm() {
        this.saveStepData();

        const loader = UIComponents.showLoading({
            title: 'Submitting Form',
            message: 'Please wait...'
        });

        try {
            // Simulate API call
            await this.delay(2000);

            loader.hide();

            UIComponents.showAlert({
                title: 'Success!',
                message: 'Your form has been submitted successfully.',
                variant: 'success',
                onOk: () => {
                    this.resetForm(false);
                }
            });
        } catch (error) {
            loader.hide();

            UIComponents.showAlert({
                title: 'Error',
                message: `Failed to submit form: ${error.message}`,
                variant: 'error'
            });
        }
    }

    /**
     * Save draft
     */
    saveDraft() {
        this.saveStepData();
        localStorage.setItem('formModule_draft', JSON.stringify(this.formData));
        UIComponents.showToast('Draft saved successfully', 'success');
    }

    /**
     * Load saved data
     */
    loadSavedData() {
        const saved = localStorage.getItem('formModule_draft');
        if (saved) {
            this.formData = JSON.parse(saved);
        }
    }

    /**
     * Reset form
     */
    resetForm(confirm = true) {
        const doReset = () => {
            this.formData = {};
            this.currentStep = 1;
            localStorage.removeItem('formModule_draft');
            this.render();
            this.attachEventListeners();
            UIComponents.showToast('Form reset successfully', 'info');
        };

        if (confirm) {
            UIComponents.showConfirmation({
                title: 'Reset Form?',
                message: 'Are you sure you want to reset the form? All entered data will be lost.',
                variant: 'warning',
                confirmLabel: 'Reset',
                onConfirm: doReset
            });
        } else {
            doReset();
        }
    }

    /**
     * Show help
     */
    showHelp() {
        UIComponents.showAlert({
            title: 'Form Help',
            message: 'This is a multi-step form template.\n\n• Fill out each step completely\n• Use Next/Previous to navigate\n• Save Draft to preserve your progress\n• Required fields are marked with *',
            variant: 'info'
        });
    }

    /**
     * Update progress
     */
    updateProgress() {
        const progressFill = this.container.querySelector('.progress-fill');
        if (progressFill) {
            progressFill.style.width = `${(this.currentStep / this.totalSteps) * 100}%`;
        }

        const prevBtn = this.container.querySelector('#prevBtn');
        const nextBtn = this.container.querySelector('#nextBtn');

        if (prevBtn) {
            prevBtn.disabled = this.currentStep === 1;
        }

        if (nextBtn) {
            nextBtn.textContent = this.currentStep === this.totalSteps ? 'Submit' : 'Next →';
        }
    }

    /**
     * Start auto-save
     */
    startAutosave() {
        this.autoSaveTimer = setInterval(() => {
            this.saveStepData();
            localStorage.setItem('formModule_draft', JSON.stringify(this.formData));
        }, this.config.autosaveInterval);
    }

    /**
     * Stop auto-save
     */
    stopAutosave() {
        if (this.autoSaveTimer) {
            clearInterval(this.autoSaveTimer);
            this.autoSaveTimer = null;
        }
    }

    /**
     * Utility: Delay helper
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Cleanup
     */
    destroy() {
        this.stopAutosave();
    }
}

// Global instance
let formModule;

// Auto-initialize if container exists
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('formModuleContainer');
    if (container) {
        formModule = new FormModule('formModuleContainer');
    }
});
