/**
 * FILE: UI/external/modules/thread-cards/thread-lock-toggle.js
 * PURPOSE: Lock/Unlock toggle button functionality for thread cards
 * 
 * DEPENDENCIES:
 * - DeviceLockManager (from business-ai-platform-v2.html)
 * 
 * EXPORTS:
 * - Extends DeviceLockManager with toggleThreadLock() method
 * - Updates lockThread() and unlockThread() to work with toggle button
 * 
 * USAGE:
 * Called automatically when toggle button is clicked
 * 
 * LAST MODIFIED: 2025-11-18 - Created for toggle button implementation
 */

// Wait for DeviceLockManager to be available
if (typeof DeviceLockManager !== 'undefined') {

    // Add toggle function
    DeviceLockManager.toggleThreadLock = async function (threadId) {
        const toggleBtn = document.getElementById(`lock-toggle-${threadId}`);
        if (!toggleBtn) {
            console.error('❌ [Device Lock] Toggle button not found');
            return;
        }

        const isCurrentlyLocked = toggleBtn.getAttribute('data-locked') === 'true';

        if (isCurrentlyLocked) {
            // Currently locked, so unlock it
            await this.unlockThread(threadId);
        } else {
            // Currently unlocked, so lock it
            await this.lockThread(threadId);
        }
    };

    // Store original lockThread method
    const originalLockThread = DeviceLockManager.lockThread;

    // Override lockThread to update toggle button
    DeviceLockManager.lockThread = async function (threadId) {
        // Call original method
        await originalLockThread.call(this, threadId);

        // Update toggle button state (in addition to original UI updates)
        const toggleBtn = document.getElementById(`lock-toggle-${threadId}`);
        if (toggleBtn) {
            toggleBtn.setAttribute('data-locked', 'true');
            toggleBtn.querySelector('i').className = 'fas fa-lock';
            const textSpan = toggleBtn.querySelector('.lock-toggle-text');
            if (textSpan) {
                textSpan.textContent = 'Unlock Thread';
            }
            toggleBtn.title = 'Unlock this thread for all devices';
        }
    };

    // Store original unlockThread method
    const originalUnlockThread = DeviceLockManager.unlockThread;

    // Override unlockThread to update toggle button
    DeviceLockManager.unlockThread = async function (threadId) {
        // Call original method
        await originalUnlockThread.call(this, threadId);

        // Update toggle button state (in addition to original UI updates)
        const toggleBtn = document.getElementById(`lock-toggle-${threadId}`);
        if (toggleBtn) {
            toggleBtn.setAttribute('data-locked', 'false');
            toggleBtn.querySelector('i').className = 'fas fa-lock-open';
            const textSpan = toggleBtn.querySelector('.lock-toggle-text');
            if (textSpan) {
                textSpan.textContent = 'Lock Thread';
            }
            toggleBtn.title = 'Lock this thread to your current device';
        }
    };

    console.log('✅ [Thread Lock Toggle] Module loaded successfully');
} else {
    console.warn('⚠️ [Thread Lock Toggle] DeviceLockManager not found - will retry on DOMContentLoaded');

    // Retry when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            // Check again if DeviceLockManager is now available
            if (typeof DeviceLockManager !== 'undefined') {
                console.log('🔷 [Thread Lock Toggle] DeviceLockManager now available, initializing...');

                // Re-run the extension code
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

                const originalLockThread = DeviceLockManager.lockThread;
                DeviceLockManager.lockThread = async function (threadId) {
                    await originalLockThread.call(this, threadId);

                    const toggleBtn = document.getElementById(`lock-toggle-${threadId}`);
                    if (toggleBtn) {
                        toggleBtn.setAttribute('data-locked', 'true');
                        toggleBtn.querySelector('i').className = 'fas fa-lock';
                        const textSpan = toggleBtn.querySelector('.lock-toggle-text');
                        if (textSpan) {
                            textSpan.textContent = 'Unlock Thread';
                        }
                        toggleBtn.title = 'Unlock this thread for all devices';
                    }
                };

                const originalUnlockThread = DeviceLockManager.unlockThread;
                DeviceLockManager.unlockThread = async function (threadId) {
                    await originalUnlockThread.call(this, threadId);

                    const toggleBtn = document.getElementById(`lock-toggle-${threadId}`);
                    if (toggleBtn) {
                        toggleBtn.setAttribute('data-locked', 'false');
                        toggleBtn.querySelector('i').className = 'fas fa-lock-open';
                        const textSpan = toggleBtn.querySelector('.lock-toggle-text');
                        if (textSpan) {
                            textSpan.textContent = 'Lock Thread';
                        }
                        toggleBtn.title = 'Lock this thread to your current device';
                    }
                };

                console.log('✅ [Thread Lock Toggle] Module loaded successfully (deferred)');
            }
        });
    }
}
