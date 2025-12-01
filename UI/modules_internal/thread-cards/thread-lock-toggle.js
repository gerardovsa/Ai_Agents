/**
 * FILE: UI/external/modules/thread-cards/thread-lock-toggle.js
 * PURPOSE: Lock/Unlock toggle button functionality for thread cards
 * 
 * DEPENDENCIES:
 * - DeviceLockManager (from device_lock_manager.js component)
 * 
 * EXPORTS:
 * - Extends DeviceLockManager with toggleThreadLock() method
 * - Updates lockThread() and unlockThread() to work with toggle button
 * 
 * USAGE:
 * Called automatically when toggle button is clicked
 * 
 * LAST MODIFIED: 2025-11-20 - Fixed timing issue with DeviceLockManager initialization
 */

(function () {
    console.log('🔷 [Thread Lock Toggle] Module loading...');

    // Function to initialize toggle functionality
    function initializeToggle() {
        if (typeof DeviceLockManager === 'undefined' || !DeviceLockManager) {
            console.log('✅ [Thread Lock Toggle] DeviceLockManager loaded and available');
            return false;
        }

        // Check if already initialized
        if (DeviceLockManager.toggleThreadLock) {
            console.log('🔷 [Thread Lock Toggle] Already initialized, skipping');
            return true;
        }

        console.log('🔷 [Thread Lock Toggle] Initializing toggle functionality...');

        // Add toggle function
        DeviceLockManager.toggleThreadLock = async function (threadId) {
            const toggleBtn = document.getElementById(`lock-toggle-${threadId}`);
            if (!toggleBtn) {
                console.error('❌ [Device Lock] Toggle button not found');
                return;
            }

            const isCurrentlyLocked = toggleBtn.getAttribute('data-locked') === 'true';

            if (isCurrentlyLocked) {
                await this.unlockThread(threadId);
            } else {
                await this.lockThread(threadId);
            }
        };

        // Store original methods with proper binding
        const originalLockThread = DeviceLockManager.lockThread.bind(DeviceLockManager);
        const originalUnlockThread = DeviceLockManager.unlockThread.bind(DeviceLockManager);

        // Override lockThread to update toggle button
        DeviceLockManager.lockThread = async function (threadId) {
            // Call original method
            await originalLockThread(threadId);

            // Update toggle button state (in addition to original UI updates)
            const toggleBtn = document.getElementById(`lock-toggle-${threadId}`);
            if (toggleBtn) {
                toggleBtn.setAttribute('data-locked', 'true');
                const iconEl = toggleBtn.querySelector('i');
                if (iconEl) iconEl.className = 'fas fa-lock';
                const textSpan = toggleBtn.querySelector('.lock-toggle-text');
                if (textSpan) textSpan.textContent = 'Unlock Thread';
                toggleBtn.title = 'Unlock this thread for all devices';
            }
        };

        // Override unlockThread to update toggle button
        DeviceLockManager.unlockThread = async function (threadId) {
            // Call original method
            await originalUnlockThread(threadId);

            // Update toggle button state (in addition to original UI updates)
            const toggleBtn = document.getElementById(`lock-toggle-${threadId}`);
            if (toggleBtn) {
                toggleBtn.setAttribute('data-locked', 'false');
                const iconEl = toggleBtn.querySelector('i');
                if (iconEl) iconEl.className = 'fas fa-lock-open';
                const textSpan = toggleBtn.querySelector('.lock-toggle-text');
                if (textSpan) textSpan.textContent = 'Lock Thread';
                toggleBtn.title = 'Lock this thread to your current device';
            }
        };

        console.log('✅ [Thread Lock Toggle] Toggle functionality initialized');
        return true;
    }

    // Try immediate initialization
    if (initializeToggle()) {
        return;
    }

    // If not available, listen for custom event from DeviceLockManager
    console.log('🔷 [Thread Lock Toggle] Waiting for DeviceLockManager initialization...');

    window.addEventListener('devicelockmanager-ready', function () {
        console.log('🔷 [Thread Lock Toggle] DeviceLockManager ready event received');
        initializeToggle();
    });

    // Fallback: also try on DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            setTimeout(function () {
                if (typeof DeviceLockManager !== 'undefined' && !DeviceLockManager.toggleThreadLock) {
                    console.log('🔷 [Thread Lock Toggle] Retry after DOMContentLoaded');
                    initializeToggle();
                }
            }, 500); // Give DeviceLockManager time to initialize
        });
    }
})();
