/**
 * FILE: UI/modules/threads/components/device_lock_manager.js
 * PURPOSE: Device locking system for multi-device thread coordination
 * 
 * EXPORTS:
 * - DeviceLockManager (object) - Device lock management singleton
 * 
 * DEPENDENCIES:
 * - UserAuth (from user_auth.js)
 * - API_BASE_URL (global)
 * 
 * LAST MODIFIED: 2025-11-20 - Extracted from thread_manager_additional.js
 */

const DeviceLockManager = {
    deviceId: null,
    deviceName: null,
    initialized: false, // ← NEW: Track initialization state

    async init() {
        // ✅ FIX (Nov 24, 2025): Prevent double initialization
        if (this.initialized) {
            console.log('[Device Lock] Already initialized - skipping duplicate call');
            return;
        }

        console.log('[Device Lock] Initializing...');
        this.initialized = true; // ← Set flag BEFORE async operations

        this.deviceId = localStorage.getItem('device_id');
        if (!this.deviceId) {
            this.deviceId = this.generateDeviceId();
            localStorage.setItem('device_id', this.deviceId);
        }

        this.deviceName = this.getDeviceName();
        await this.registerDevice();

        console.log('[Device Lock] Initialized:', { deviceId: this.deviceId, deviceName: this.deviceName });

        // Dispatch ready event for other modules (e.g., thread-lock-toggle.js)
        window.dispatchEvent(new CustomEvent('devicelockmanager-ready', {
            detail: {
                deviceId: this.deviceId,
                deviceName: this.deviceName
            }
        }));
    },

    generateDeviceId() {
        return `browser-${navigator.userAgent.substring(0, 10).replace(/\s+/g, '-')}-${Date.now()}`;
    },

    getDeviceName() {
        const customName = localStorage.getItem('device_custom_name');
        if (customName) {
            return customName;
        }

        const ua = navigator.userAgent;
        if (ua.includes('Chrome')) return 'Chrome Browser';
        if (ua.includes('Firefox')) return 'Firefox Browser';
        if (ua.includes('Safari')) return 'Safari Browser';
        if (ua.includes('Edge')) return 'Edge Browser';
        return 'Unknown Browser';
    },

    setCustomDeviceName(name) {
        if (name && name.trim().length > 0) {
            localStorage.setItem('device_custom_name', name.trim());
            this.deviceName = name.trim();
            this.registerDevice();
            const display = document.getElementById('current-device-name-display');
            if (display) {
                display.textContent = name.trim();
            }
            console.log('[Device Lock] Custom device name set:', name.trim());
        } else {
            console.error('[Device Lock] Invalid device name');
        }
    },

    showDeviceNameModal() {
        let modal = document.getElementById('device-name-modal-overlay');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'device-name-modal-overlay';
            modal.className = 'device-name-modal-overlay';
            modal.innerHTML = `
                <div class="device-name-modal">
                    <div class="device-name-modal-header">
                        <div class="device-name-modal-title">
                            <i class="fas fa-desktop"></i>
                            <span>Name This Device</span>
                        </div>
                        <button class="device-name-modal-close" onclick="DeviceLockManager.closeDeviceNameModal()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="device-name-modal-body">
                        <label class="device-name-modal-label" for="device-name-input">
                            Device Nickname
                        </label>
                        <input type="text" 
                               id="device-name-input" 
                               class="device-name-modal-input"
                               placeholder="e.g., Work Laptop, Home Desktop, John's Chrome"
                               maxlength="50"
                               value="${this.deviceName || ''}">
                        <div class="device-name-modal-hint">
                            This name will be shown when this device locks a thread. Makes it easier to identify in multi-device scenarios.
                        </div>
                    </div>
                    <div class="device-name-modal-footer">
                        <button class="device-name-modal-btn cancel" onclick="DeviceLockManager.closeDeviceNameModal()">
                            Cancel
                        </button>
                        <button class="device-name-modal-btn save" onclick="DeviceLockManager.saveDeviceName()">
                            Save Name
                        </button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);

            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeDeviceNameModal();
                }
            });

            const input = modal.querySelector('#device-name-input');
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    this.saveDeviceName();
                } else if (e.key === 'Escape') {
                    this.closeDeviceNameModal();
                }
            });
        }

        modal.classList.add('active');
        setTimeout(() => {
            const input = document.getElementById('device-name-input');
            if (input) {
                input.focus();
                input.select();
            }
        }, 100);
    },

    closeDeviceNameModal() {
        const modal = document.getElementById('device-name-modal-overlay');
        if (modal) {
            modal.classList.remove('active');
        }
    },

    saveDeviceName() {
        const input = document.getElementById('device-name-input');
        if (input && input.value.trim()) {
            this.setCustomDeviceName(input.value);
            this.closeDeviceNameModal();
            alert(`Device name updated to: "${input.value.trim()}"`);
        } else {
            alert('Please enter a valid device name');
        }
    },

    async registerDevice() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/device/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    device_id: this.deviceId,
                    device_name: this.deviceName,
                    user_id: UserAuth.user?.user_id || UserAuth.user?.id || 1,
                    device_fingerprint: navigator.userAgent
                })
            });

            const result = await response.json();
            if (result.success) {
                console.log('[Device Lock] Device registered:', result);
            } else {
                console.error('[Device Lock] Registration failed:', result.error);
            }
        } catch (error) {
            console.error('[Device Lock] Registration error:', error);
        }
    },

    async lockThread(threadId) {
        try {
            console.log(`[Device Lock] Locking thread ${threadId}...`);

            const response = await fetch(`${API_BASE_URL}/api/threads/${threadId}/lock`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    device_id: this.deviceId,
                    user_id: UserAuth.user?.user_id || UserAuth.user?.id || 1
                })
            });

            const result = await response.json();

            if (result.success) {
                console.log('[Device Lock] Thread locked:', result);

                const threadCards = document.querySelectorAll(`[data-thread-id="${threadId}"]`);
                threadCards.forEach(card => card.classList.add('locked'));

                const lockBtn = document.getElementById(`lock-btn-${threadId}`);
                const unlockBtn = document.getElementById(`unlock-btn-${threadId}`);
                const lockStatus = document.getElementById(`lock-status-${threadId}`);

                if (lockBtn) lockBtn.style.display = 'none';
                if (unlockBtn) unlockBtn.style.display = 'inline-flex';
                if (lockStatus) {
                    lockStatus.style.display = 'none';
                }

                this.showNotification(`Thread locked to ${this.deviceName}`, 'success');
            } else {
                console.error('[Device Lock] Lock failed:', result.error);
                this.showNotification(`Failed to lock: ${result.error}`, 'error');
            }
        } catch (error) {
            console.error('[Device Lock] Lock error:', error);
            this.showNotification('Failed to lock thread', 'error');
        }
    },

    async unlockThread(threadId) {
        try {
            console.log(`[Device Lock] Unlocking thread ${threadId}...`);

            const response = await fetch(`${API_BASE_URL}/api/threads/${threadId}/unlock`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    device_id: this.deviceId,
                    user_id: UserAuth.user?.user_id || UserAuth.user?.id || 1
                })
            });

            const result = await response.json();

            if (result.success) {
                console.log('[Device Lock] Thread unlocked:', result);

                const threadCards = document.querySelectorAll(`[data-thread-id="${threadId}"]`);
                threadCards.forEach(card => card.classList.remove('locked'));

                const lockBtn = document.getElementById(`lock-btn-${threadId}`);
                const unlockBtn = document.getElementById(`unlock-btn-${threadId}`);
                const lockStatus = document.getElementById(`lock-status-${threadId}`);

                if (lockBtn) lockBtn.style.display = 'inline-flex';
                if (unlockBtn) unlockBtn.style.display = 'none';
                if (lockStatus) lockStatus.style.display = 'none';

                const chatInput = document.querySelector('.ai-chat-input-container');
                if (chatInput) chatInput.classList.remove('locked-read-only');

                this.showNotification('Thread unlocked', 'success');
            } else {
                console.error('[Device Lock] Unlock failed:', result.error);
                this.showNotification(`Failed to unlock: ${result.error}`, 'error');
            }
        } catch (error) {
            console.error('[Device Lock] Unlock error:', error);
            this.showNotification('Failed to unlock thread', 'error');
        }
    },

    async checkLockStatus(threadId) {
        try {
            const response = await fetch(
                `${API_BASE_URL}/api/threads/${threadId}/lock-status?device_id=${this.deviceId}&user_id=${UserAuth.user?.user_id || UserAuth.user?.id || 1}`
            );

            const result = await response.json();

            if (result.locked) {
                if (result.is_current_device) {
                    this.showUnlockButton(threadId);
                } else {
                    this.showLockedStatus(threadId, result.locked_to_device);
                    if (!result.can_edit) {
                        this.disableChatInput();
                    }
                }
            } else {
                this.showLockButton(threadId);
            }

            return result;
        } catch (error) {
            console.error('[Device Lock] Status check error:', error);
            return null;
        }
    },

    showLockButton(threadId) {
        const container = document.getElementById(`lock-controls-${threadId}`);
        const lockBtn = document.getElementById(`lock-btn-${threadId}`);
        const unlockBtn = document.getElementById(`unlock-btn-${threadId}`);
        const lockStatus = document.getElementById(`lock-status-${threadId}`);

        if (container) container.style.display = 'flex';
        if (lockBtn) lockBtn.style.display = 'inline-flex';
        if (unlockBtn) unlockBtn.style.display = 'none';
        if (lockStatus) lockStatus.style.display = 'none';
    },

    showUnlockButton(threadId) {
        const container = document.getElementById(`lock-controls-${threadId}`);
        const lockBtn = document.getElementById(`lock-btn-${threadId}`);
        const unlockBtn = document.getElementById(`unlock-btn-${threadId}`);
        const lockStatus = document.getElementById(`lock-status-${threadId}`);

        if (container) container.style.display = 'flex';
        if (lockBtn) lockBtn.style.display = 'none';
        if (unlockBtn) unlockBtn.style.display = 'inline-flex';
        if (lockStatus) lockStatus.style.display = 'none';
    },

    showLockedStatus(threadId, deviceName) {
        const container = document.getElementById(`lock-controls-${threadId}`);
        const lockBtn = document.getElementById(`lock-btn-${threadId}`);
        const unlockBtn = document.getElementById(`unlock-btn-${threadId}`);
        const lockStatus = document.getElementById(`lock-status-${threadId}`);
        const deviceNameEl = document.getElementById(`lock-device-name-${threadId}`);

        if (container) container.style.display = 'flex';
        if (lockBtn) lockBtn.style.display = 'none';
        if (unlockBtn) unlockBtn.style.display = 'none';
        if (lockStatus) lockStatus.style.display = 'inline-flex';
        if (deviceNameEl) deviceNameEl.textContent = deviceName || 'Another Device';

        const threadCards = document.querySelectorAll(`[data-thread-id="${threadId}"]`);
        threadCards.forEach(card => card.classList.add('locked'));
    },

    disableChatInput() {
        const chatInput = document.querySelector('.ai-chat-input-container');
        if (chatInput) {
            chatInput.classList.add('locked-read-only');
        }
    },

    enableChatInput() {
        const chatInput = document.querySelector('.ai-chat-input-container');
        if (chatInput) {
            chatInput.classList.remove('locked-read-only');
        }
    },

    showNotification(message, type = 'info') {
        console.log(`${type === 'error' ? '❌' : '✅'} [Device Lock] ${message}`);
    }
};

window.DeviceLockManager = DeviceLockManager;
console.log('✅ [DeviceLockManager] Module loaded and exposed globally');
