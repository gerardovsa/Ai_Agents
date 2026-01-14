/**
 * FILE: UI/modules/onboarding/first-run-experience.js
 * PURPOSE: First-Run Experience modal with database persistence
 * 
 * DEPENDENCIES:
 * - onboarding-api.js - API wrapper
 * - Font Awesome - Icons
 * 
 * EXPORTS:
 * - FirstRunExperience class
 * 
 * NOTES:
 * - Uses database instead of localStorage
 * - Shows on first login only
 * - Can trigger tours or skip
 * 
 * LAST MODIFIED: 2025-11-29 - Database integration
 */

class FirstRunExperience {
    constructor() {
        this.modal = null;
        this.hasCompleted = false;
        this.isLoading = true;
    }

    /**
     * Initialize and check if should show FRE
     */
    async init() {
        console.log('🔧 [FRE] Initializing...');

        try {
            // Get status from database
            const response = await window.OnboardingAPI.getStatus();

            if (response.success && response.data) {
                this.hasCompleted = response.data.fre_completed;
                this.isLoading = false;

                if (!this.hasCompleted) {
                    console.log('🎯 [FRE] First-time user detected, showing welcome modal');

                    // Wait for DOM to be ready
                    if (document.readyState === 'loading') {
                        document.addEventListener('DOMContentLoaded', () => this.show());
                    } else {
                        // Small delay to let UI settle
                        setTimeout(() => this.show(), 1000);
                    }
                } else {
                    console.log('✅ [FRE] Already completed, skipping');
                }
            }
        } catch (error) {
            console.error('❌ [FRE] Failed to initialize:', error);
            this.isLoading = false;
        }
    }

    /**
     * Show the FRE modal
     */
    show() {
        this.modal = document.getElementById('fre-modal');
        if (!this.modal) {
            console.error('❌ [FRE] Modal element not found');
            return;
        }

        // Show modal with animation
        this.modal.style.display = 'flex';
        setTimeout(() => {
            this.modal.classList.add('visible');
        }, 10);

        console.log('✅ [FRE] Modal displayed');
    }

    /**
     * Hide the FRE modal
     */
    hide() {
        if (!this.modal) return;

        this.modal.classList.remove('visible');
        setTimeout(() => {
            this.modal.style.display = 'none';
        }, 300);
    }

    /**
     * Start the platform tour
     */
    async startTour() {
        console.log('🚀 [FRE] Starting platform basics tour');

        try {
            // Mark FRE as completed (not skipped)
            await window.OnboardingAPI.completeFRE(false);
            this.hasCompleted = true;

            // Hide modal
            this.hide();

            // Start Shepherd.js tour
            setTimeout(() => {
                if (window.TourManager) {
                    window.TourManager.startTour('basics');
                } else {
                    console.error('❌ [FRE] TourManager not available');
                }
            }, 400);

            console.log('✅ [FRE] Tour started');
        } catch (error) {
            console.error('❌ [FRE] Failed to start tour:', error);
        }
    }

    /**
     * Skip the FRE (user clicked "Skip for now")
     */
    async skip() {
        console.log('⏭️ [FRE] User skipped welcome modal');

        try {
            // Mark FRE as completed (skipped)
            await window.OnboardingAPI.completeFRE(true);
            this.hasCompleted = true;

            // Hide modal
            this.hide();

            // Show onboarding checklist instead
            setTimeout(() => {
                if (window.OnboardingChecklist) {
                    window.OnboardingChecklist.show();
                }
            }, 500);

            console.log('✅ [FRE] Skipped, checklist shown');
        } catch (error) {
            console.error('❌ [FRE] Failed to skip:', error);
        }
    }

    /**
     * Reset FRE (for testing or admin action)
     */
    reset() {
        console.warn('🔄 [FRE] Reset requested - requires database update');
        // This should be done via admin panel, not client-side
    }
}

// Create global instance
window.FirstRunExperience = new FirstRunExperience();

console.log('✅ First-Run Experience module loaded');
