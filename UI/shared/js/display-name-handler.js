/**
 * Display Name Handler for Multi-Person Collaboration
 * Shows UI modal instead of browser prompt for better UX
 */

// Show the display name prompt modal
function showDisplayNamePrompt() {
    const modal = document.getElementById('displayNamePrompt');
    const input = document.getElementById('displayNameInput');

    if (modal && input) {
        // Pre-fill with current value if exists
        const stored = localStorage.getItem('session_display_name');
        if (stored) {
            input.value = stored;
        } else {
            // Default to user's name from UserAuth
            const defaultName = window.UserAuth?.user?.username || 'User';
            input.placeholder = `e.g. "${defaultName}"`;
        }

        modal.style.display = 'block';
        input.focus();

        // Allow Enter key to save
        input.onkeydown = (e) => {
            if (e.key === 'Enter') {
                saveDisplayName();
            } else if (e.key === 'Escape') {
                skipDisplayName();
            }
        };
    }
}

// Save display name to localStorage and backend
async function saveDisplayName() {
    const input = document.getElementById('displayNameInput');
    const modal = document.getElementById('displayNamePrompt');

    if (!input || !modal) return;

    const displayName = input.value.trim();

    if (!displayName) {
        input.style.borderColor = 'var(--error-primary)';
        input.placeholder = 'Please enter a name';
        input.focus();
        return;
    }

    // Sanitize (max 50 chars)
    const sanitized = displayName.substring(0, 50);

    // Save to localStorage (immediate)
    localStorage.setItem('session_display_name', sanitized);

    // Update SynergyRealtime
    if (window.SynergyRealtime) {
        window.SynergyRealtime.sessionDisplayName = sanitized;

        // Re-announce presence with new name
        if (window.SynergyRealtime.presenceContext) {
            await window.SynergyRealtime._announcePresence();
        }
    }

    // Save to backend database
    await saveDisplayNameToBackend(sanitized);

    // Update Account Sidebar display
    const sidebarDisplayNameEl = document.getElementById('sidebarDisplayName');
    if (sidebarDisplayNameEl) {
        sidebarDisplayNameEl.textContent = sanitized;
        sidebarDisplayNameEl.style.fontStyle = 'normal';
        sidebarDisplayNameEl.style.color = 'var(--text-primary)';
    }

    // Hide modal
    modal.style.display = 'none';

    console.log('[DISPLAY NAME] Set to:', sanitized);
}

// Skip display name setup (use default)
function skipDisplayName() {
    const modal = document.getElementById('displayNamePrompt');
    if (modal) {
        modal.style.display = 'none';
    }

    // Set default from username
    const defaultName = window.UserAuth?.user?.username || 'User';
    localStorage.setItem('session_display_name', defaultName);

    if (window.SynergyRealtime) {
        window.SynergyRealtime.sessionDisplayName = defaultName;
    }

    console.log('[DISPLAY NAME] Skipped - using default:', defaultName);
}

// Save display name to backend
async function saveDisplayNameToBackend(displayName) {
    try {
        const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
        if (!token) {
            console.warn('[DISPLAY NAME] No auth token - skipping backend save');
            return;
        }

        const response = await fetch(`${API_BASE_URL}/api/auth/update-display-name`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ display_name: displayName })
        });

        if (response.ok) {
            console.log('[DISPLAY NAME] Saved to backend');
        } else {
            console.warn('[DISPLAY NAME] Backend save failed:', response.status);
        }
    } catch (error) {
        console.error('[DISPLAY NAME] Error saving to backend:', error);
    }
}

// Check if display name needs to be prompted (called after login)
async function checkDisplayNamePrompt() {
    // Only prompt if:
    // 1. Not set in localStorage
    // 2. User is logged in
    // 3. Not in first-time setup flow

    const stored = localStorage.getItem('session_display_name');
    if (stored) {
        console.log('[DISPLAY NAME] Already set:', stored);
        return; // Already configured
    }

    // Check if backend has a saved display_name
    try {
        const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
        if (!token) return;

        const response = await fetch(`${API_BASE_URL}/api/auth/profile`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            const profile = data.profile || data;

            if (profile.display_name) {
                // Use display_name from backend
                localStorage.setItem('session_display_name', profile.display_name);
                if (window.SynergyRealtime) {
                    window.SynergyRealtime.sessionDisplayName = profile.display_name;
                }
                console.log('[DISPLAY NAME] Loaded from backend:', profile.display_name);
                return;
            }
        }
    } catch (error) {
        console.error('[DISPLAY NAME] Error checking backend:', error);
    }

    // Show prompt after a short delay (let auth animation finish)
    setTimeout(() => {
        showDisplayNamePrompt();
    }, 1000);
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Will be called after successful login
        console.log('[DISPLAY NAME] Handler loaded');
    });
} else {
    console.log('[DISPLAY NAME] Handler loaded');
}
