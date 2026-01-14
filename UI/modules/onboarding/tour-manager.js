/**
 * FILE: UI/modules/onboarding/tour-manager.js
 * PURPOSE: Shepherd.js tour orchestration for interactive platform tours
 * 
 * FEATURES:
 * - 4 pre-configured tours (Basics, Multi-Agent, Automation, Synergy)
 * - 26 total tour steps with smart targeting
 * - Database persistence via OnboardingAPI
 * - Progress tracking and completion analytics
 * - Dynamic element detection with fallback
 * - Custom theme integration
 * 
 * TOURS:
 * 1. Platform Basics (5 steps) - Navigation, threads, messages
 * 2. Multi-Agent Mastery (6 steps) - Agent selection, multi-agent threads
 * 3. Automation Workflows (8 steps) - Visual workflows, scheduling, execution
 * 4. Synergy Sessions (7 steps) - Linking threads, multi-agent collaboration
 * 
 * DEPENDENCIES:
 * - Shepherd.js 11.2.0 (loaded via CDN)
 * - window.OnboardingAPI (onboarding-api.js)
 * - onboarding.css (.shepherd-theme-custom)
 * 
 * EVENTS DISPATCHED:
 * - onboarding:tour-started (detail: {tourId})
 * - onboarding:tour-completed (detail: {tourId, stepsCompleted})
 * - onboarding:tour-cancelled (detail: {tourId, currentStep})
 * 
 * USAGE:
 * const tourManager = new TourManager();
 * await tourManager.startTour('basics');
 * 
 * LAST MODIFIED: 2025-11-30 - Initial implementation
 */

class TourManager {
    constructor() {
        this.currentTour = null;
        this.shepherdInstance = null;
        this.tourConfigs = this.initializeTourConfigs();
        this.isShepherdLoaded = false;
    }

    /**
     * Initialize tour configurations
     */
    initializeTourConfigs() {
        return {
            basics: {
                id: 'basics',
                title: 'Platform Basics',
                description: 'Learn navigation, threads, and messaging',
                steps: [
                    {
                        id: 'welcome',
                        title: 'Welcome to the AI Platform!',
                        text: 'Let\'s take a quick tour to get you started. You can exit anytime by pressing ESC.',
                        attachTo: { element: 'body', on: 'center' },
                        buttons: [
                            { text: 'Skip Tour', action: 'cancel' },
                            { text: 'Start Tour', action: 'next' }
                        ]
                    },
                    {
                        id: 'sidebar',
                        title: 'Navigation Sidebar',
                        text: 'Access all platform features from this sidebar. Threads, Quick Actions, Automation, and more!',
                        attachTo: { element: '#sidebar, .sidebar, [data-sidebar]', on: 'right' },
                        buttons: [
                            { text: 'Back', action: 'back' },
                            { text: 'Next', action: 'next' }
                        ]
                    },
                    {
                        id: 'threads',
                        title: 'Threads Section',
                        text: 'Threads are your conversations with AI agents. Create, organize, and manage all your AI interactions here.',
                        attachTo: { element: '#threads-section, [data-module="threads"]', on: 'right' },
                        buttons: [
                            { text: 'Back', action: 'back' },
                            { text: 'Next', action: 'next' }
                        ]
                    },
                    {
                        id: 'new-thread',
                        title: 'Create a Thread',
                        text: 'Click here to start a new conversation. Choose your AI agent and begin chatting!',
                        attachTo: { element: '#new-thread-btn, .new-thread-button, [data-action="new-thread"]', on: 'bottom' },
                        buttons: [
                            { text: 'Back', action: 'back' },
                            { text: 'Next', action: 'next' }
                        ]
                    },
                    {
                        id: 'chat-interface',
                        title: 'Chat Interface',
                        text: 'This is where your conversations happen. Type messages, attach files, and see AI responses in real-time.',
                        attachTo: { element: '#chat-container, .chat-interface, [data-chat-area]', on: 'top' },
                        buttons: [
                            { text: 'Back', action: 'back' },
                            { text: 'Finish', action: 'complete' }
                        ]
                    }
                ]
            },

            multiagent: {
                id: 'multiagent',
                title: 'Multi-Agent Mastery',
                description: 'Master multi-agent conversations and collaboration',
                steps: [
                    {
                        id: 'multiagent-intro',
                        title: 'Multi-Agent Power',
                        text: 'The platform supports multiple AI agents working together. Let\'s explore how to leverage this capability!',
                        attachTo: { element: 'body', on: 'center' },
                        buttons: [
                            { text: 'Skip', action: 'cancel' },
                            { text: 'Continue', action: 'next' }
                        ]
                    },
                    {
                        id: 'agent-selector',
                        title: 'Agent Selection',
                        text: 'Choose which AI agents to include in your conversation. Each agent brings unique capabilities.',
                        attachTo: { element: '#agent-selector, .agent-picker, [data-agent-select]', on: 'bottom' },
                        buttons: [
                            { text: 'Back', action: 'back' },
                            { text: 'Next', action: 'next' }
                        ]
                    },
                    {
                        id: 'agent-profiles',
                        title: 'Agent Capabilities',
                        text: 'View each agent\'s specialties: coding, research, creative writing, data analysis, and more.',
                        attachTo: { element: '.agent-card, [data-agent-profile]', on: 'right' },
                        buttons: [
                            { text: 'Back', action: 'back' },
                            { text: 'Next', action: 'next' }
                        ]
                    },
                    {
                        id: 'multi-select',
                        title: 'Select Multiple Agents',
                        text: 'Hold Ctrl/Cmd to select multiple agents. They\'ll collaborate on complex tasks!',
                        attachTo: { element: '.agent-list, [data-agent-list]', on: 'left' },
                        buttons: [
                            { text: 'Back', action: 'back' },
                            { text: 'Next', action: 'next' }
                        ]
                    },
                    {
                        id: 'agent-responses',
                        title: 'Agent Responses',
                        text: 'Each agent\'s response is color-coded. You\'ll see their unique perspectives on your question.',
                        attachTo: { element: '.agent-response, [data-agent-message]', on: 'top' },
                        buttons: [
                            { text: 'Back', action: 'back' },
                            { text: 'Next', action: 'next' }
                        ]
                    },
                    {
                        id: 'multiagent-finish',
                        title: 'Multi-Agent Mastery!',
                        text: 'You\'re ready to harness the power of multiple AI agents. Try creating a multi-agent thread now!',
                        attachTo: { element: 'body', on: 'center' },
                        buttons: [
                            { text: 'Finish', action: 'complete' }
                        ]
                    }
                ]
            },

            automation: {
                id: 'automation',
                title: 'Automation Workflows',
                description: 'Create visual workflows to automate tasks',
                steps: [
                    {
                        id: 'automation-intro',
                        title: 'Automate Everything',
                        text: 'Create visual workflows to automate repetitive tasks. No coding required!',
                        attachTo: { element: 'body', on: 'center' },
                        buttons: [
                            { text: 'Skip', action: 'cancel' },
                            { text: 'Let\'s Go', action: 'next' }
                        ]
                    },
                    {
                        id: 'automation-tab',
                        title: 'Automation Section',
                        text: 'Find all your workflows here. Create, edit, and manage automated tasks.',
                        attachTo: { element: '#automation-tab, [data-module="automation"]', on: 'right' },
                        buttons: [
                            { text: 'Back', action: 'back' },
                            { text: 'Next', action: 'next' }
                        ]
                    },
                    {
                        id: 'new-workflow',
                        title: 'Create Workflow',
                        text: 'Start building your first automation by clicking this button.',
                        attachTo: { element: '#new-workflow-btn, [data-action="new-workflow"]', on: 'bottom' },
                        buttons: [
                            { text: 'Back', action: 'back' },
                            { text: 'Next', action: 'next' }
                        ]
                    },
                    {
                        id: 'workflow-canvas',
                        title: 'Visual Canvas',
                        text: 'Drag and drop nodes to build your workflow. Connect them to create automation logic.',
                        attachTo: { element: '#workflow-canvas, .workflow-editor, [data-workflow-canvas]', on: 'top' },
                        buttons: [
                            { text: 'Back', action: 'back' },
                            { text: 'Next', action: 'next' }
                        ]
                    },
                    {
                        id: 'node-palette',
                        title: 'Node Library',
                        text: 'Choose from triggers, actions, conditions, and integrations. Drag them onto the canvas.',
                        attachTo: { element: '.node-palette, [data-node-library]', on: 'right' },
                        buttons: [
                            { text: 'Back', action: 'back' },
                            { text: 'Next', action: 'next' }
                        ]
                    },
                    {
                        id: 'workflow-triggers',
                        title: 'Set Triggers',
                        text: 'Choose when your workflow runs: schedule, webhook, manual, or event-based.',
                        attachTo: { element: '.trigger-config, [data-trigger-settings]', on: 'left' },
                        buttons: [
                            { text: 'Back', action: 'back' },
                            { text: 'Next', action: 'next' }
                        ]
                    },
                    {
                        id: 'workflow-test',
                        title: 'Test Your Workflow',
                        text: 'Always test before deploying. Click "Test Run" to see your automation in action.',
                        attachTo: { element: '#test-workflow-btn, [data-action="test-workflow"]', on: 'bottom' },
                        buttons: [
                            { text: 'Back', action: 'back' },
                            { text: 'Next', action: 'next' }
                        ]
                    },
                    {
                        id: 'automation-finish',
                        title: 'Automation Expert!',
                        text: 'You now know how to create powerful automations. Start building your first workflow!',
                        attachTo: { element: 'body', on: 'center' },
                        buttons: [
                            { text: 'Finish', action: 'complete' }
                        ]
                    }
                ]
            },

            synergy: {
                id: 'synergy',
                title: 'Synergy Sessions',
                description: 'Link threads for multi-agent collaboration',
                steps: [
                    {
                        id: 'synergy-intro',
                        title: 'Synergy Power',
                        text: 'Link multiple threads together for collaborative AI problem-solving. Let\'s learn how!',
                        attachTo: { element: 'body', on: 'center' },
                        buttons: [
                            { text: 'Skip', action: 'cancel' },
                            { text: 'Show Me', action: 'next' }
                        ]
                    },
                    {
                        id: 'synergy-tab',
                        title: 'Synergy Section',
                        text: 'Manage all your multi-thread collaborations here.',
                        attachTo: { element: '#synergy-tab, [data-module="synergy"]', on: 'right' },
                        buttons: [
                            { text: 'Back', action: 'back' },
                            { text: 'Next', action: 'next' }
                        ]
                    },
                    {
                        id: 'create-synergy',
                        title: 'Create Synergy Session',
                        text: 'Start a new collaborative session by linking existing threads.',
                        attachTo: { element: '#new-synergy-btn, [data-action="new-synergy"]', on: 'bottom' },
                        buttons: [
                            { text: 'Back', action: 'back' },
                            { text: 'Next', action: 'next' }
                        ]
                    },
                    {
                        id: 'select-threads',
                        title: 'Select Threads',
                        text: 'Choose which threads to link together. Each thread brings its AI agent and context.',
                        attachTo: { element: '.thread-selector, [data-thread-picker]', on: 'left' },
                        buttons: [
                            { text: 'Back', action: 'back' },
                            { text: 'Next', action: 'next' }
                        ]
                    },
                    {
                        id: 'synergy-canvas',
                        title: 'Visual Collaboration',
                        text: 'See all linked threads visually. Watch as agents collaborate on your task.',
                        attachTo: { element: '#synergy-canvas, [data-synergy-view]', on: 'top' },
                        buttons: [
                            { text: 'Back', action: 'back' },
                            { text: 'Next', action: 'next' }
                        ]
                    },
                    {
                        id: 'synergy-broadcast',
                        title: 'Broadcast Messages',
                        text: 'Send messages to all linked threads at once. Get diverse perspectives instantly.',
                        attachTo: { element: '.synergy-broadcast, [data-broadcast-input]', on: 'top' },
                        buttons: [
                            { text: 'Back', action: 'back' },
                            { text: 'Next', action: 'next' }
                        ]
                    },
                    {
                        id: 'synergy-finish',
                        title: 'Synergy Master!',
                        text: 'You\'re ready to create powerful multi-agent collaborations. Try linking threads now!',
                        attachTo: { element: 'body', on: 'center' },
                        buttons: [
                            { text: 'Finish', action: 'complete' }
                        ]
                    }
                ]
            }
        };
    }

    /**
     * Ensure Shepherd.js is loaded
     */
    async ensureShepherdLoaded() {
        if (this.isShepherdLoaded && window.Shepherd) {
            return true;
        }

        // Check if already in DOM
        if (window.Shepherd) {
            this.isShepherdLoaded = true;
            return true;
        }

        // Load Shepherd.js from CDN
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/shepherd.js@11.2.0/dist/js/shepherd.min.js';
            script.onload = () => {
                this.isShepherdLoaded = true;
                console.log('✅ Shepherd.js loaded successfully');
                resolve(true);
            };
            script.onerror = () => {
                console.error('❌ Failed to load Shepherd.js');
                reject(new Error('Failed to load Shepherd.js'));
            };
            document.head.appendChild(script);
        });
    }

    /**
     * Start a tour by ID
     */
    async startTour(tourId) {
        try {
            console.log(`🔧 Starting tour: ${tourId}`);

            // Validate tour ID
            if (!this.tourConfigs[tourId]) {
                console.error(`❌ Tour not found: ${tourId}`);
                return;
            }

            // Ensure Shepherd.js is loaded
            await this.ensureShepherdLoaded();

            // Create Shepherd tour instance
            this.shepherdInstance = new Shepherd.Tour({
                defaultStepOptions: {
                    classes: 'shepherd-theme-custom',
                    scrollTo: { behavior: 'smooth', block: 'center' },
                    cancelIcon: {
                        enabled: true
                    }
                },
                useModalOverlay: true
            });

            const tourConfig = this.tourConfigs[tourId];
            this.currentTour = tourId;

            // Add steps to tour
            tourConfig.steps.forEach(stepConfig => {
                this.addStep(stepConfig);
            });

            // Tour event handlers
            this.shepherdInstance.on('complete', () => {
                this.handleTourComplete(tourId);
            });

            this.shepherdInstance.on('cancel', () => {
                this.handleTourCancel(tourId);
            });

            // Dispatch start event
            window.dispatchEvent(new CustomEvent('onboarding:tour-started', {
                detail: { tourId }
            }));

            // Start the tour
            this.shepherdInstance.start();

            console.log(`✅ Tour started: ${tourId}`);

        } catch (error) {
            console.error(`❌ Error starting tour ${tourId}:`, error);
        }
    }

    /**
     * Add a step to the Shepherd tour
     */
    addStep(stepConfig) {
        const step = {
            id: stepConfig.id,
            title: stepConfig.title,
            text: stepConfig.text,
            buttons: this.buildButtons(stepConfig.buttons)
        };

        // Handle element attachment with fallback
        if (stepConfig.attachTo) {
            const element = this.findElement(stepConfig.attachTo.element);
            if (element) {
                step.attachTo = {
                    element: element,
                    on: stepConfig.attachTo.on
                };
            } else {
                // Fallback to center if element not found
                console.warn(`⚠️ Element not found for step ${stepConfig.id}: ${stepConfig.attachTo.element}`);
                step.attachTo = { element: 'body', on: 'center' };
            }
        }

        this.shepherdInstance.addStep(step);
    }

    /**
     * Find element with multiple selector fallbacks
     */
    findElement(selector) {
        if (!selector || selector === 'body') {
            return document.body;
        }

        // Try multiple selectors (comma-separated)
        const selectors = selector.split(',').map(s => s.trim());

        for (const sel of selectors) {
            const element = document.querySelector(sel);
            if (element) {
                return element;
            }
        }

        return null;
    }

    /**
     * Build Shepherd button configurations
     */
    buildButtons(buttonConfigs) {
        if (!buttonConfigs) return [];

        return buttonConfigs.map(btnConfig => {
            const button = {
                text: btnConfig.text,
                classes: btnConfig.action === 'next' || btnConfig.action === 'complete' ? 'shepherd-button-primary' : 'shepherd-button-secondary'
            };

            switch (btnConfig.action) {
                case 'next':
                    button.action = () => this.shepherdInstance.next();
                    break;
                case 'back':
                    button.action = () => this.shepherdInstance.back();
                    break;
                case 'complete':
                    button.action = () => this.shepherdInstance.complete();
                    break;
                case 'cancel':
                    button.action = () => this.shepherdInstance.cancel();
                    break;
                default:
                    button.action = btnConfig.action;
            }

            return button;
        });
    }

    /**
     * Handle tour completion
     */
    async handleTourComplete(tourId) {
        try {
            console.log(`🎉 Tour completed: ${tourId}`);

            const tourConfig = this.tourConfigs[tourId];
            const stepsCompleted = tourConfig.steps.length;

            // Call API to mark tour complete
            const result = await window.OnboardingAPI.completeTour(tourId);

            if (result && result.success) {
                // Show completion toast
                this.showToast('Tour Completed!', `You finished the ${tourConfig.title} tour!`, 'success');

                // Dispatch completion event
                window.dispatchEvent(new CustomEvent('onboarding:tour-completed', {
                    detail: { tourId, stepsCompleted }
                }));
            }

            this.cleanup();

        } catch (error) {
            console.error(`❌ Error completing tour ${tourId}:`, error);
        }
    }

    /**
     * Handle tour cancellation
     */
    handleTourCancel(tourId) {
        console.log(`⚠️ Tour cancelled: ${tourId}`);

        const currentStep = this.shepherdInstance.getCurrentStep();

        window.dispatchEvent(new CustomEvent('onboarding:tour-cancelled', {
            detail: {
                tourId,
                currentStep: currentStep ? currentStep.id : null
            }
        }));

        this.cleanup();
    }

    /**
     * Show toast notification
     */
    showToast(title, message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `onboarding-toast toast-${type}`;

        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        toast.innerHTML = `
            <div class="toast-icon">${icons[type]}</div>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
            </div>
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('toast-visible');
        }, 100);

        setTimeout(() => {
            toast.classList.remove('toast-visible');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3000);
    }

    /**
     * Cleanup tour instance
     */
    cleanup() {
        if (this.shepherdInstance) {
            this.shepherdInstance = null;
        }
        this.currentTour = null;
    }

    /**
     * Get available tours
     */
    getAvailableTours() {
        return Object.keys(this.tourConfigs).map(tourId => {
            const config = this.tourConfigs[tourId];
            return {
                id: config.id,
                title: config.title,
                description: config.description,
                stepCount: config.steps.length
            };
        });
    }
}

// Create global instance
window.TourManager = new TourManager();
