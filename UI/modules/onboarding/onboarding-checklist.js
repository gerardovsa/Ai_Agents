/**
 * FILE: UI/modules/onboarding/onboarding-checklist.js
 * PURPOSE: Floating onboarding checklist widget with database-backed progress tracking
 * 
 * FEATURES:
 * - 5-step activation checklist (first thread, send message, use Quick Action, create workflow, link Synergy)
 * - Real-time progress updates via CustomEvents
 * - XP awards on step completion
 * - Database persistence via OnboardingAPI
 * - Celebration animations on completion
 * - Collapsible/expandable widget
 * - Auto-dismissal on 100% completion
 * 
 * DEPENDENCIES:
 * - window.OnboardingAPI (onboarding-api.js)
 * - onboarding.css for styling
 * 
 * EVENTS LISTENED:
 * - thread:created
 * - message:sent
 * - quickaction:used
 * - workflow:created
 * - synergy:linked
 * 
 * EVENTS DISPATCHED:
 * - onboarding:step-completed (detail: {stepId, xp, progress})
 * - onboarding:checklist-completed (detail: {totalXp, completedSteps})
 * 
 * USAGE:
 * const checklist = new OnboardingChecklist();
 * await checklist.init();
 * checklist.show();
 * 
 * LAST MODIFIED: 2025-11-30 - Initial implementation
 */

class OnboardingChecklist {
    constructor() {
        // Checklist configuration
        this.steps = [
            {
                id: 'first-thread',
                title: 'Create Your First Thread',
                description: 'Start a conversation with an AI agent',
                xp: 50,
                icon: '💬',
                completed: false,
                event: 'thread:created'
            },
            {
                id: 'send-message',
                title: 'Send a Message',
                description: 'Chat with your AI agent',
                xp: 30,
                icon: '✉️',
                completed: false,
                event: 'message:sent'
            },
            {
                id: 'use-quickaction',
                title: 'Try a Quick Action',
                description: 'Use a pre-built prompt template',
                xp: 40,
                icon: '⚡',
                completed: false,
                event: 'quickaction:used'
            },
            {
                id: 'create-workflow',
                title: 'Create a Workflow',
                description: 'Automate a task with visual workflows',
                xp: 100,
                icon: '🔄',
                completed: false,
                event: 'workflow:created'
            },
            {
                id: 'link-synergy',
                title: 'Link to Synergy',
                description: 'Connect threads for multi-agent collaboration',
                xp: 80,
                icon: '🔗',
                completed: false,
                event: 'synergy:linked'
            }
        ];

        this.container = null;
        this.isExpanded = true;
        this.isDismissed = false;
        this.totalXp = 0;
        this.completedCount = 0;
    }

    /**
     * Initialize checklist by fetching user's onboarding status from database
     */
    async init() {
        try {
            console.log('🔧 Initializing onboarding checklist...');

            // Check if already dismissed
            const dismissedFlag = sessionStorage.getItem('onboarding-checklist-dismissed');
            if (dismissedFlag === 'true') {
                this.isDismissed = true;
                console.log('✅ Checklist already dismissed this session');
                return;
            }

            // Fetch user's onboarding status from database
            const status = await window.OnboardingAPI.getStatus();

            if (!status || !status.data) {
                console.error('❌ Failed to fetch onboarding status');
                return;
            }

            const userData = status.data;
            const completedSteps = userData.completed_steps || [];
            this.totalXp = userData.total_xp || 0;

            // Update step completion status
            this.steps.forEach(step => {
                if (completedSteps.includes(step.id)) {
                    step.completed = true;
                    this.completedCount++;
                }
            });

            // Check if checklist is 100% complete
            if (this.completedCount === this.steps.length) {
                console.log('✅ All onboarding steps completed!');
                this.isDismissed = true;
                return;
            }

            // Render the checklist widget
            this.render();

            // Attach event listeners for step completion
            this.attachEventListeners();

            console.log(`✅ Checklist initialized: ${this.completedCount}/${this.steps.length} steps completed`);

        } catch (error) {
            console.error('❌ Error initializing onboarding checklist:', error);
        }
    }

    /**
     * Render the checklist widget HTML
     */
    render() {
        // Check if already rendered
        if (this.container) {
            console.log('⚠️ Checklist already rendered');
            return;
        }

        // Create container
        this.container = document.createElement('div');
        this.container.className = 'onboarding-checklist';
        this.container.setAttribute('data-expanded', this.isExpanded);

        // Calculate progress
        const progress = Math.round((this.completedCount / this.steps.length) * 100);

        // Build HTML
        this.container.innerHTML = `
            <div class="checklist-header">
                <div class="checklist-title">
                    <span class="checklist-icon">🎯</span>
                    <span>Getting Started</span>
                </div>
                <div class="checklist-actions">
                    <button class="checklist-toggle" title="Toggle checklist">
                        <span class="toggle-icon">▼</span>
                    </button>
                    <button class="checklist-dismiss" title="Dismiss checklist">✕</button>
                </div>
            </div>

            <div class="checklist-progress">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${progress}%"></div>
                </div>
                <div class="progress-text">${this.completedCount} of ${this.steps.length} completed</div>
            </div>

            <div class="checklist-body">
                <ul class="checklist-steps">
                    ${this.steps.map(step => this.renderStep(step)).join('')}
                </ul>
                <div class="checklist-xp">
                    <span class="xp-icon">⭐</span>
                    <span class="xp-amount">${this.totalXp} XP</span>
                </div>
            </div>
        `;

        // Append to body
        document.body.appendChild(this.container);

        // Attach UI event listeners
        this.attachUIListeners();

        // Animate in
        setTimeout(() => {
            this.container.classList.add('checklist-visible');
        }, 100);
    }

    /**
     * Render a single checklist step
     */
    renderStep(step) {
        const statusClass = step.completed ? 'step-completed' : 'step-pending';
        const checkIcon = step.completed ? '✓' : '';

        return `
            <li class="checklist-step ${statusClass}" data-step-id="${step.id}">
                <div class="step-icon">${step.icon}</div>
                <div class="step-content">
                    <div class="step-title">${step.title}</div>
                    <div class="step-description">${step.description}</div>
                </div>
                <div class="step-status">
                    <span class="step-check">${checkIcon}</span>
                    <span class="step-xp">+${step.xp} XP</span>
                </div>
            </li>
        `;
    }

    /**
     * Attach UI event listeners (collapse, dismiss)
     */
    attachUIListeners() {
        if (!this.container) return;

        // Toggle collapse/expand
        const toggleBtn = this.container.querySelector('.checklist-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                this.isExpanded = !this.isExpanded;
                this.container.setAttribute('data-expanded', this.isExpanded);
                const icon = toggleBtn.querySelector('.toggle-icon');
                icon.textContent = this.isExpanded ? '▼' : '▲';
            });
        }

        // Dismiss checklist
        const dismissBtn = this.container.querySelector('.checklist-dismiss');
        if (dismissBtn) {
            dismissBtn.addEventListener('click', async () => {
                await this.dismiss();
            });
        }
    }

    /**
     * Attach event listeners for step completion triggers
     */
    attachEventListeners() {
        this.steps.forEach(step => {
            if (!step.completed) {
                window.addEventListener(step.event, (e) => {
                    this.completeStep(step.id);
                });
            }
        });
    }

    /**
     * Mark a step as completed (triggered by CustomEvent)
     */
    async completeStep(stepId) {
        const step = this.steps.find(s => s.id === stepId);
        if (!step || step.completed) return;

        try {
            console.log(`🔧 Completing onboarding step: ${stepId}`);

            // Call API to mark step complete and award XP
            const result = await window.OnboardingAPI.completeStep(stepId, step.xp);

            if (result && result.success) {
                // Update local state
                step.completed = true;
                this.completedCount++;
                this.totalXp = result.data.total_xp;

                // Update UI
                this.updateStepUI(stepId);
                this.updateProgress();
                this.showCelebration(step);

                // Dispatch event
                window.dispatchEvent(new CustomEvent('onboarding:step-completed', {
                    detail: {
                        stepId: stepId,
                        xp: step.xp,
                        progress: (this.completedCount / this.steps.length) * 100
                    }
                }));

                // Check if all steps completed
                if (this.completedCount === this.steps.length) {
                    await this.handleAllStepsCompleted();
                }

                console.log(`✅ Step completed: ${stepId} (+${step.xp} XP)`);
            }

        } catch (error) {
            console.error(`❌ Error completing step ${stepId}:`, error);
        }
    }

    /**
     * Update step UI after completion
     */
    updateStepUI(stepId) {
        if (!this.container) return;

        const stepElement = this.container.querySelector(`[data-step-id="${stepId}"]`);
        if (stepElement) {
            stepElement.classList.remove('step-pending');
            stepElement.classList.add('step-completed');

            const checkSpan = stepElement.querySelector('.step-check');
            if (checkSpan) {
                checkSpan.textContent = '✓';
            }

            // Add celebration animation
            stepElement.classList.add('step-celebrating');
            setTimeout(() => {
                stepElement.classList.remove('step-celebrating');
            }, 1000);
        }
    }

    /**
     * Update progress bar and XP display
     */
    updateProgress() {
        if (!this.container) return;

        const progress = Math.round((this.completedCount / this.steps.length) * 100);

        const progressFill = this.container.querySelector('.progress-fill');
        if (progressFill) {
            progressFill.style.width = `${progress}%`;
        }

        const progressText = this.container.querySelector('.progress-text');
        if (progressText) {
            progressText.textContent = `${this.completedCount} of ${this.steps.length} completed`;
        }

        const xpAmount = this.container.querySelector('.xp-amount');
        if (xpAmount) {
            xpAmount.textContent = `${this.totalXp} XP`;
            // Add pulse animation
            xpAmount.classList.add('xp-pulse');
            setTimeout(() => {
                xpAmount.classList.remove('xp-pulse');
            }, 600);
        }
    }

    /**
     * Show celebration toast for completed step
     */
    showCelebration(step) {
        const toast = document.createElement('div');
        toast.className = 'onboarding-toast toast-success';
        toast.innerHTML = `
            <div class="toast-icon">🎉</div>
            <div class="toast-content">
                <div class="toast-title">Step Completed!</div>
                <div class="toast-message">${step.title} (+${step.xp} XP)</div>
            </div>
        `;

        document.body.appendChild(toast);

        // Animate in
        setTimeout(() => {
            toast.classList.add('toast-visible');
        }, 100);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            toast.classList.remove('toast-visible');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3000);
    }

    /**
     * Handle completion of all checklist steps
     */
    async handleAllStepsCompleted() {
        try {
            console.log('🎉 All onboarding steps completed!');

            // Show completion modal
            this.showCompletionModal();

            // Dispatch completion event
            window.dispatchEvent(new CustomEvent('onboarding:checklist-completed', {
                detail: {
                    totalXp: this.totalXp,
                    completedSteps: this.steps.map(s => s.id)
                }
            }));

            // Auto-dismiss checklist after 5 seconds
            setTimeout(() => {
                this.dismiss(false); // Don't call API, already marked complete
            }, 5000);

        } catch (error) {
            console.error('❌ Error handling checklist completion:', error);
        }
    }

    /**
     * Show completion celebration modal
     */
    showCompletionModal() {
        const modal = document.createElement('div');
        modal.className = 'activation-modal';
        modal.innerHTML = `
            <div class="activation-content">
                <div class="activation-icon">🏆</div>
                <h2 class="activation-title">Congratulations!</h2>
                <p class="activation-message">You've completed all onboarding steps and earned <strong>${this.totalXp} XP</strong>!</p>
                <button class="activation-button">Continue Exploring</button>
            </div>
        `;

        document.body.appendChild(modal);

        // Animate in
        setTimeout(() => {
            modal.classList.add('modal-visible');
        }, 100);

        // Close on button click
        const closeBtn = modal.querySelector('.activation-button');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                modal.classList.remove('modal-visible');
                setTimeout(() => {
                    modal.remove();
                }, 300);
            });
        }
    }

    /**
     * Dismiss the checklist widget
     */
    async dismiss(callAPI = true) {
        try {
            if (callAPI) {
                await window.OnboardingAPI.dismiss();
            }

            this.isDismissed = true;
            sessionStorage.setItem('onboarding-checklist-dismissed', 'true');

            if (this.container) {
                this.container.classList.remove('checklist-visible');
                setTimeout(() => {
                    this.container.remove();
                    this.container = null;
                }, 300);
            }

            console.log('✅ Onboarding checklist dismissed');

        } catch (error) {
            console.error('❌ Error dismissing checklist:', error);
        }
    }

    /**
     * Show the checklist if it was hidden
     */
    show() {
        if (this.isDismissed) {
            console.log('⚠️ Checklist is dismissed, cannot show');
            return;
        }

        if (!this.container) {
            this.render();
        } else {
            this.container.classList.add('checklist-visible');
        }
    }

    /**
     * Hide the checklist without dismissing
     */
    hide() {
        if (this.container) {
            this.container.classList.remove('checklist-visible');
        }
    }
}

// Create global instance
window.OnboardingChecklist = new OnboardingChecklist();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.OnboardingChecklist.init();
    });
} else {
    window.OnboardingChecklist.init();
}
