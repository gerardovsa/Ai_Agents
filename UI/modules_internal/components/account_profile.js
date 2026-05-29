// Use window.API_BASE_URL directly (declared in main HTML)
// No local declaration needed - access via window.API_BASE_URL

// Login form handler
async function handleLogin(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const loginBtn = document.getElementById('loginBtn');
    const errorDiv = document.getElementById('loginError');

    // Disable button
    loginBtn.disabled = true;
    loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing in...';
    errorDiv.classList.remove('show');

    // Attempt login
    const result = await UserAuth.login(username, password);

    if (result.success) {
        // Success - UserAuth.showMainApp() already called
        console.log('Login successful');
        // Check for any pending org invite stored before login
        await checkPendingInvite();
    } else {
        // Show error
        errorDiv.textContent = result.error;
        errorDiv.classList.add('show');

        // Re-enable button
        loginBtn.disabled = false;
        loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Sign In';
    }
}

// Logout handler
// Inline DOM confirmation helper (used when UIComponents isn't available)
function createInlineConfirm(opts) {
    const title = opts.title || 'Confirm Action';
    const message = opts.message || 'Are you sure?';
    const confirmLabel = opts.confirmLabel || 'Confirm';
    const cancelLabel = opts.cancelLabel || 'Cancel';

    const overlay = document.createElement('div');
    overlay.className = 'inline-confirm-overlay';
    overlay.style.position = 'fixed';
    overlay.style.inset = '0';
    overlay.style.background = 'rgba(0,0,0,0.45)';
    overlay.style.display = 'flex';
    overlay.style.alignItems = 'center';
    overlay.style.justifyContent = 'center';
    overlay.style.zIndex = 2147483647;

    const dialog = document.createElement('div');
    dialog.className = 'inline-confirm-dialog';
    dialog.style.background = 'var(--bg-primary, #0b1220)';
    dialog.style.color = 'var(--text-primary, #e6edf3)';
    dialog.style.padding = '18px';
    dialog.style.borderRadius = '10px';
    dialog.style.minWidth = '320px';
    dialog.style.maxWidth = '540px';
    dialog.style.boxShadow = '0 12px 40px rgba(0,0,0,0.6)';

    const titleEl = document.createElement('div');
    titleEl.style.fontWeight = 700;
    titleEl.style.marginBottom = '8px';
    titleEl.textContent = title;

    const msgEl = document.createElement('div');
    msgEl.style.marginBottom = '14px';
    msgEl.style.lineHeight = '1.4';
    msgEl.textContent = message;

    const actions = document.createElement('div');
    actions.style.display = 'flex';
    actions.style.justifyContent = 'flex-end';
    actions.style.gap = '10px';

    const cancelBtn = document.createElement('button');
    cancelBtn.className = 'btn btn-secondary';
    cancelBtn.textContent = cancelLabel;

    const confirmBtn = document.createElement('button');
    confirmBtn.className = 'btn btn-primary';
    confirmBtn.textContent = confirmLabel;

    actions.appendChild(cancelBtn);
    actions.appendChild(confirmBtn);

    dialog.appendChild(titleEl);
    dialog.appendChild(msgEl);
    dialog.appendChild(actions);
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);

    // Focus
    confirmBtn.focus();

    function cleanup() {
        try { overlay.remove(); } catch (e) { }
    }

    cancelBtn.addEventListener('click', () => {
        cleanup();
        if (typeof opts.onCancel === 'function') opts.onCancel();
    });

    confirmBtn.addEventListener('click', () => {
        cleanup();
        if (typeof opts.onConfirm === 'function') opts.onConfirm();
    });

    return {
        element: overlay,
        destroy: cleanup,
        hide: () => overlay.style.display = 'none',
        show: () => overlay.style.display = 'flex'
    };
}

function handleLogout() {
    try {
        if (window.UIComponents && typeof UIComponents.showConfirmation === 'function') {
            UIComponents.showConfirmation({
                title: 'Logout?',
                message: 'Are you sure you want to logout?',
                variant: 'warning',
                confirmLabel: 'Logout',
                cancelLabel: 'Stay Logged In',
                onConfirm: () => { UserAuth.logout(); }
            });
        } else {
            // Use inline DOM modal instead of native confirm()
            console.warn('[UI] UIComponents not available, using inline DOM confirmation for logout');
            createInlineConfirm({
                title: 'Logout?',
                message: 'Are you sure you want to logout?',
                confirmLabel: 'Logout',
                cancelLabel: 'Stay Logged In',
                onConfirm: () => { UserAuth.logout(); },
                onCancel: () => { /* no-op */ }
            });
        }
    } catch (err) {
        console.error('[UI] handleLogout error:', err);
        // As a last resort, show inline confirm
        createInlineConfirm({
            title: 'Logout?',
            message: 'Are you sure you want to logout?',
            confirmLabel: 'Logout',
            cancelLabel: 'Stay Logged In',
            onConfirm: () => { try { UserAuth.logout(); } catch (e) { console.error('Logout failed', e); } }
        });
    }
}

// ==================== USER PROFILE SIDEBAR ====================

function toggleUserMenu(event) {
    // Prevent event bubbling to avoid immediate close
    if (event) {
        event.stopPropagation();
    }

    // Open Account Sidebar instead of dropdown menu
    if (window.AccountSidebar) {
        window.AccountSidebar.toggleSidebar();

        const btnHeader = document.getElementById('userProfileBtn');
        const btnSidebar = document.getElementById('userProfileBtn-sidebar');
        const sidebar = document.getElementById('account-sidebar');

        // Update button active states based on sidebar state
        const isOpen = sidebar && !sidebar.classList.contains('collapsed');
        if (btnHeader) {
            if (isOpen) {
                btnHeader.classList.add('active');
            } else {
                btnHeader.classList.remove('active');
            }
        }
        if (btnSidebar) {
            if (isOpen) {
                btnSidebar.classList.add('active');
            } else {
                btnSidebar.classList.remove('active');
            }
        }

        console.log('[ACCOUNT] Profile sidebar toggled:', isOpen ? 'OPEN' : 'CLOSED');
    } else {
        console.error('[ACCOUNT] AccountSidebar not found');
    }
}

function toggleNotificationPanel(event) {
    // Prevent event bubbling
    if (event) {
        event.stopPropagation();
    }

    // Use unified NotificationCenter if available (new system)
    if (typeof NotificationCenter !== 'undefined' && NotificationCenter.togglePanel) {
        NotificationCenter.togglePanel();

        // Toggle active state on button
        const notifBtn = document.getElementById('notificationBellBtn-sidebar');
        if (notifBtn) {
            const panel = document.getElementById('unified-notification-panel');
            const isOpen = panel && panel.classList.contains('show');
            notifBtn.classList.toggle('active', isOpen);
        }

        console.log('[Notifications] Toggled unified notification panel');
        return;
    }

    // FALLBACK: Legacy Synergy notification panel
    let panel = document.getElementById('synergy-notifications');

    // Create panel if it doesn't exist
    if (!panel) {
        if (typeof NotificationSystem !== 'undefined' && NotificationSystem.createNotificationPanel) {
            NotificationSystem.createNotificationPanel();
            panel = document.getElementById('synergy-notifications');
        }

        if (!panel) {
            console.warn('Notification system not initialized yet');
            return;
        }
    }

    const isOpen = panel.classList.toggle('show');
    const notifBtn = document.getElementById('notificationBellBtn-sidebar');
    if (notifBtn) {
        notifBtn.classList.toggle('active', isOpen);
    }
    console.log('Notification panel toggled (legacy):', panel.classList.contains('show') ? 'OPEN' : 'CLOSED');
}

// Initialize right sidebar buttons
function initRightSidebar() {
    // Prevent duplicate initialization
    if (window._rightSidebarInitialized) {
        console.warn('Right sidebar already initialized, skipping...');
        return;
    }
    window._rightSidebarInitialized = true;
    console.log('? Initializing right sidebar buttons...');

    // AI Prime Toggle - Always works regardless of chat state
    const aiPrimeBtn = document.getElementById('ai-prime-toggle-btn');
    if (aiPrimeBtn) {
        aiPrimeBtn.addEventListener('click', function () {
            const panel = document.getElementById('ai-chat-panel');
            const wrapper = document.getElementById('main-content-wrapper');

            if (panel && wrapper) {
                // Toggle chat state
                AppState.chatOpen = !AppState.chatOpen;

                if (AppState.chatOpen) {
                    wrapper.classList.remove('chat-collapsed');
                    panel.style.display = 'flex';
                    this.classList.add('active');
                    console.log('AI Prime chat OPENED');
                } else {
                    wrapper.classList.add('chat-collapsed');
                    panel.style.display = 'none';
                    this.classList.remove('active');
                    console.log('AI Prime chat CLOSED');
                }
            } else {
                console.warn('Chat panel or wrapper not found');
            }
        });
    }

    // New Chat - Opens new chat modal
    const newChatBtn = document.getElementById('new-chat-btn');
    if (newChatBtn) {
        newChatBtn.addEventListener('click', function (event) {
            event.preventDefault();
            event.stopPropagation();

            // Check if modal already exists
            const existingModal = document.getElementById('newChatModalOverlay');
            if (existingModal) {
                console.warn('Modal already open, skipping...');
                return;
            }

            console.log('New chat button clicked from right sidebar');
            if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.showNewChatModal === 'function') {
                ThreadManager.showNewChatModal('prime');
            } else {
                console.error('ThreadManager.showNewChatModal function not found');
            }
        });
    }

    // Threads button now has onclick in HTML to call ThreadManager.toggleThreadMenu()
    // No event listener needed here

    // Quick Actions - Toggles prompt sidebar
    const quickActionsBtn = document.getElementById('quick-actions-btn');
    if (quickActionsBtn) {
        quickActionsBtn.addEventListener('click', function (event) {
            event.preventDefault();
            event.stopPropagation();
            console.log('? Quick actions button clicked');

            // Toggle prompt sidebar
            const promptSidebar = document.getElementById('prompt-sidebar');
            if (promptSidebar) {
                const isOpen = promptSidebar.classList.toggle('show');
                this.classList.toggle('active', isOpen);
                console.log('? Prompt sidebar toggled:', promptSidebar.classList.contains('show') ? 'VISIBLE' : 'HIDDEN');
            } else {
                console.warn('Prompt sidebar not found - may not be initialized yet');
            }
        });
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    const container = document.getElementById('userProfileContainer');
    const menu = document.getElementById('userDropdownMenu');
    const btnHeader = document.getElementById('userProfileBtn');
    const btnSidebar = document.getElementById('userProfileBtn-sidebar');

    // Check if click is outside both the container and the sidebar button
    const clickedSidebarBtn = btnSidebar && btnSidebar.contains(e.target);
    const clickedContainer = container && container.contains(e.target);

    if (!clickedContainer && !clickedSidebarBtn) {
        if (menu?.classList.contains('active')) {
            menu.classList.remove('active');
            if (btnHeader) btnHeader.classList.remove('active');
            if (btnSidebar) btnSidebar.classList.remove('active');
            console.log(' Profile menu closed (click outside)');
        }
    }
});

// Load OAuth connections for sidebar display
async function loadSidebarOAuthConnections() {
    const connectionsList = document.getElementById('oauthConnectionsList');
    if (!connectionsList) {
        console.warn('[OAUTH] oauthConnectionsList element not found');
        return;
    }

    try {
        // Check if user has Google OAuth
        const hasGoogle = UserAuth.user?.google_oauth_connected || false;
        const hasMicrosoft = UserAuth.user?.microsoft_oauth_connected || false;

        if (!hasGoogle && !hasMicrosoft) {
            connectionsList.innerHTML = `
                <div style="text-align: center; padding: 12px; color: var(--text-muted); font-size: 12px;">
                    <i class="fas fa-link-slash" style="margin-bottom: 6px; font-size: 16px;"></i>
                    <div>No OAuth connections</div>
                    <div style="margin-top: 4px; font-size: 11px;">Connect accounts in settings</div>
                </div>
            `;
            return;
        }

        let html = '';

        if (hasGoogle) {
            html += `
                <div class="oauth-connection-item" style="display: flex; align-items: center; gap: 8px; padding: 8px; background: var(--bg-secondary); border-radius: 6px;">
                    <i class="fab fa-google" style="color: #4285F4; font-size: 16px;"></i>
                    <div style="flex: 1;">
                        <div style="font-size: 12px; font-weight: 500; color: var(--text-primary);">Google Workspace</div>
                        <div style="font-size: 11px; color: var(--text-muted);">${UserAuth.user.email || 'Connected'}</div>
                    </div>
                    <i class="fas fa-check-circle" style="color: var(--success-color, #22c55e); font-size: 14px;"></i>
                </div>
            `;
        }

        if (hasMicrosoft) {
            html += `
                <div class="oauth-connection-item" style="display: flex; align-items: center; gap: 8px; padding: 8px; background: var(--bg-secondary); border-radius: 6px;">
                    <i class="fab fa-microsoft" style="color: #00A4EF; font-size: 16px;"></i>
                    <div style="flex: 1;">
                        <div style="font-size: 12px; font-weight: 500; color: var(--text-primary);">Microsoft 365</div>
                        <div style="font-size: 11px; color: var(--text-muted);">${UserAuth.user.email || 'Connected'}</div>
                    </div>
                    <i class="fas fa-check-circle" style="color: var(--success-color, #22c55e); font-size: 14px;"></i>
                </div>
            `;
        }

        connectionsList.innerHTML = html;
        console.log('✅ [OAUTH] Loaded sidebar OAuth connections:', { google: hasGoogle, microsoft: hasMicrosoft });
    } catch (error) {
        console.error('❌ [OAUTH] Failed to load sidebar connections:', error);
        connectionsList.innerHTML = `
            <div style="text-align: center; padding: 12px; color: var(--error-text); font-size: 12px;">
                <i class="fas fa-exclamation-triangle" style="margin-bottom: 6px;"></i>
                <div>Failed to load connections</div>
            </div>
        `;
    }
}

// Load user profile data
async function loadUserProfile() {
    console.log('📋 [PROFILE] Loading user profile...');
    console.log('📋 [PROFILE] Token available:', !!UserAuth.token);
    console.log('📋 [PROFILE] Token preview:', UserAuth.token ? UserAuth.token.substring(0, 30) + '...' : 'null');
    console.log('📋 [PROFILE] Existing user data:', UserAuth.user ? 'Present' : 'None');

    // Guard: Skip if profile already loaded and token hasn't changed
    if (UserAuth.user && UserAuth.user.user_id && UserAuth.token === UserAuth._lastTokenUsed) {
        console.log('✅ [PROFILE] Profile already loaded, skipping duplicate call');
        return UserAuth.user;
    }

    try {
        const apiUrl = `${API_BASE_URL}/api/auth/profile`;
        console.log('📋 [PROFILE] Fetching from:', apiUrl);
        console.log('📋 [PROFILE] Authorization header:', `Bearer ${UserAuth.token.substring(0, 30)}...`);

        const response = await fetch(apiUrl, {
            headers: {
                'Authorization': `Bearer ${UserAuth.token}`
            }
        });

        console.log('📋 [PROFILE] Response status:', response.status);
        console.log('📋 [PROFILE] Response ok:', response.ok);

        if (!response.ok) {
            // Handle 401 gracefully - use cached profile if available
            if (response.status === 401 && UserAuth.user && UserAuth.user.user_id) {
                console.warn('⚠️ [PROFILE] Token expired (401), using cached profile');
                return UserAuth.user;
            }

            // Log full error details
            let errorText = '';
            try {
                errorText = await response.text();
                console.error('❌ [PROFILE] Error response body:', errorText);
            } catch (e) {
                console.error('❌ [PROFILE] Could not read error response');
            }

            throw new Error(`Failed to load profile: ${response.status} ${response.statusText}. ${errorText}`);
        }

        const data = await response.json();
        console.log('Profile data received:', data);

        if (data.success) {
            const profile = data.profile;

            console.log('✅ User profile loaded:', profile);
            console.log(' User ID (id):', profile.id);
            console.log(' User ID (user_id):', profile.user_id);

            // CRITICAL: Save user data to UserAuth AND localStorage
            // ✅ Ensure both 'id' and 'user_id' are present
            if (profile.user_id && !profile.id) profile.id = profile.user_id;
            if (profile.id && !profile.user_id) profile.user_id = profile.id;

            UserAuth.user = profile;
            UserAuth._lastTokenUsed = UserAuth.token; // Track token to prevent duplicate calls
            window.currentUserId = profile.id || profile.user_id; // Initialize global user ID for settings save
            localStorage.setItem('userProfile', JSON.stringify(profile));

            // Initialize Device Lock Manager after user profile is loaded
            if (typeof DeviceLockManager !== 'undefined' && !DeviceLockManager.deviceId) {
                DeviceLockManager.init();
            }

            // Update header button
            const userNameEl = document.getElementById('userName');
            const userRoleEl = document.getElementById('userRoleText');

            if (userNameEl) userNameEl.textContent = profile.username;
            if (userRoleEl) userRoleEl.textContent = profile.role;

            // Update dropdown header
            const dropdownNameEl = document.getElementById('dropdownUserName');
            const dropdownEmailEl = document.getElementById('dropdownUserEmail');

            if (dropdownNameEl) dropdownNameEl.textContent = profile.username;
            if (dropdownEmailEl) dropdownEmailEl.textContent = profile.email;

            const roleBadge = document.getElementById('roleBadge');
            if (roleBadge) {
                // Show org name + org role when available, fallback to system role
                if (profile.org_name && profile.org_role) {
                    roleBadge.textContent = `${profile.org_name}  [${profile.org_role}]`;
                } else {
                    roleBadge.textContent = profile.role || 'user';
                }
                roleBadge.classList.toggle('admin', profile.role === 'admin');
            }

            // Update loading screen org badge
            const authOrgBadge = document.getElementById('authOrgBadge');
            if (authOrgBadge) {
                if (profile.org_name) {
                    authOrgBadge.textContent = profile.org_name;
                    authOrgBadge.style.display = 'block';
                } else {
                    authOrgBadge.style.display = 'none';
                }
            }

            // ✅ FIX: Update account sidebar user info
            const sidebarUserName = document.getElementById('sidebarUserName');
            const sidebarUserEmail = document.getElementById('sidebarUserEmail');
            const sidebarRoleBadge = document.getElementById('sidebarRoleBadge');
            const authStatusDot = document.getElementById('authStatusDot');

            if (sidebarUserName) sidebarUserName.textContent = profile.username || 'User';
            if (sidebarUserEmail) sidebarUserEmail.textContent = profile.email || 'No email';
            if (sidebarRoleBadge) {
                if (profile.org_name && profile.org_role) {
                    sidebarRoleBadge.textContent = `${profile.org_name}  [${profile.org_role}]`;
                } else {
                    sidebarRoleBadge.textContent = profile.role || 'user';
                }
                sidebarRoleBadge.className = 'role-badge';
                if (profile.role === 'admin') sidebarRoleBadge.classList.add('admin');
            }
            if (authStatusDot) {
                // Green dot for authenticated
                authStatusDot.style.color = 'var(--success-color, #22c55e)';
            }

            console.log('✅ [PROFILE] Updated sidebar user info:', {
                name: profile.username,
                email: profile.email,
                role: profile.role
            });

            // Update Gmail accounts count and populate list
            // If user logged in via Google OAuth, automatically add their email
            let gmailAccounts = profile.gmail_accounts || [];
            if (profile.email && profile.email.includes('@') && gmailAccounts.length === 0) {
                // Auto-add the user's login email as primary Gmail account
                gmailAccounts = [{
                    email: profile.email,
                    display_name: profile.username || 'Primary Account',
                    is_primary: true
                }];
                console.log('Auto-added Gmail account:', profile.email);
            }

            const gmailCount = gmailAccounts.length;
            const gmailCountEl = document.getElementById('gmailCount');
            if (gmailCountEl) {
                gmailCountEl.textContent = `${gmailCount} connected`;
                gmailCountEl.style.color = gmailCount > 0 ? 'var(--success-color, #22c55e)' : 'var(--text-muted)';
            }

            // Populate Gmail accounts list
            const gmailListEl = document.getElementById('gmailAccountsList');
            if (gmailListEl && gmailAccounts.length > 0) {
                gmailListEl.innerHTML = gmailAccounts.map((account, index) => `
                            <div class="service-item" style="flex-direction: row; gap: var(--space-2);">
                                <i class="fas fa-envelope" style="color: var(--accent-primary); font-size: 14px;"></i>
                                <span style="font-size: 13px; color: var(--text-primary); flex: 1;">${account.email}</span>
                                ${account.is_primary || index === 0 ? '<span style="font-size: 11px; padding: 2px 8px; background: var(--accent-primary); color: white; border-radius: 4px;">Primary</span>' : ''}
                            </div>
                        `).join('');
            }

            // Check OAuth status from backend (checks actual tokens in database)
            const googleOAuthConnected = profile.google_oauth_connected || false;
            const microsoftOAuthConnected = profile.microsoft_oauth_connected || false;

            console.log(' Google OAuth connected:', googleOAuthConnected);
            console.log(' Microsoft OAuth connected:', microsoftOAuthConnected);

            // CONDITIONAL OAUTH UI: Show only relevant OAuth section based on auth platform
            const authPlatform = profile.auth_platform; // 'google' | 'microsoft' | null
            console.log(' Auth Platform:', authPlatform);

            // Get all platform sections
            const googleWorkspaceSection = document.getElementById('googleWorkspaceSection');
            const microsoft365Section = document.getElementById('microsoft365Section');
            const gmailSmtpSection = document.getElementById('gmailSmtpSection');

            const isGoogleUser = authPlatform === 'google';
            const isMicrosoftUser = authPlatform === 'microsoft';
            const isLocalUser = !authPlatform; // Local accounts rely on service-account provisioning

            // ✅ ALWAYS show both sections - change labels based on primary vs storage-only
            if (googleWorkspaceSection) {
                googleWorkspaceSection.style.display = 'block'; // Always show

                const connectBtn = googleWorkspaceSection.querySelector('button[onclick*="connectOAuth"]');
                const titleEl = googleWorkspaceSection.querySelector('.dropdown-item-title');
                const subtitleEl = googleWorkspaceSection.querySelector('.dropdown-item-subtitle');

                if (authPlatform === 'google') {
                    // User logged in with Google - this is primary account (full access)
                    if (titleEl) titleEl.textContent = 'Google Workspace OAuth';
                    if (subtitleEl) subtitleEl.textContent = googleOAuthConnected ? 'Connected (Primary Account)' : 'Not connected';
                    if (connectBtn && googleOAuthConnected) {
                        connectBtn.innerHTML = '<i class="fas fa-check"></i> Connected';
                        connectBtn.disabled = true;
                    }
                } else {
                    // User logged in with Microsoft - Google is for STORAGE ONLY
                    if (titleEl) titleEl.textContent = 'Google Drive (Storage)';
                    if (subtitleEl) {
                        subtitleEl.textContent = googleOAuthConnected
                            ? 'Linked for File Storage'
                            : 'Link for additional storage';
                        subtitleEl.style.color = googleOAuthConnected ? 'var(--success-color)' : 'var(--text-muted)';
                    }
                    if (connectBtn) {
                        connectBtn.innerHTML = googleOAuthConnected
                            ? '<i class="fas fa-check"></i> Linked for Storage'
                            : '<i class="fas fa-link"></i> Link Google Drive';
                    }
                }
            }

            if (microsoft365Section) {
                microsoft365Section.style.display = 'block'; // Always show

                const connectBtn = microsoft365Section.querySelector('button[onclick*="connectMicrosoft365"]');
                const titleEl = microsoft365Section.querySelector('.dropdown-item-title');
                const subtitleEl = microsoft365Section.querySelector('.dropdown-item-subtitle');

                if (authPlatform === 'microsoft') {
                    // User logged in with Microsoft - this is primary account (full access)
                    if (titleEl) titleEl.textContent = 'Microsoft 365 OAuth';
                    if (subtitleEl) subtitleEl.textContent = microsoftOAuthConnected ? 'Connected (Primary Account)' : 'Not connected';
                    if (connectBtn && microsoftOAuthConnected) {
                        connectBtn.innerHTML = '<i class="fas fa-check"></i> Connected';
                        connectBtn.disabled = true;
                    }
                } else {
                    // User logged in with Google - Microsoft is for STORAGE ONLY
                    if (titleEl) titleEl.textContent = 'OneDrive (Storage)';
                    if (subtitleEl) {
                        subtitleEl.textContent = microsoftOAuthConnected
                            ? 'Linked for File Storage'
                            : 'Link for additional storage';
                        subtitleEl.style.color = microsoftOAuthConnected ? 'var(--success-color)' : 'var(--text-muted)';
                    }
                    if (connectBtn) {
                        connectBtn.innerHTML = microsoftOAuthConnected
                            ? '<i class="fas fa-check"></i> Linked for Storage'
                            : '<i class="fas fa-link"></i> Link OneDrive';
                    }
                }
            }

            if (gmailSmtpSection) {
                // Gmail management is relevant for Google-connected or manually provisioned local users
                gmailSmtpSection.style.display = (isGoogleUser || isLocalUser) ? 'block' : 'none';
            }

            if (isGoogleUser) {
                console.log('Google OAuth user - showing Google Workspace + Gmail management');
            } else if (isMicrosoftUser) {
                console.log('Microsoft OAuth user - showing Microsoft 365 section (hiding Google Gmail blocks)');
            } else {
                console.log('Local auth user - showing both OAuth connectors for onboarding and Gmail management');
            }

            // Update Google OAuth UI status based on actual token presence
            const oauthStatus = document.getElementById('oauthStatus');
            const googleTokensExist = profile.google_oauth_connected || false;

            if (oauthStatus) {
                if (googleTokensExist) {
                    oauthStatus.innerHTML = 'Connected';
                    updateOAuthServicesStatus(true);
                    console.log('Google Workspace OAuth tokens found - services connected');

                    // Update Google Tools status to Enabled
                    const googleToolsStatus = document.getElementById('googleToolsStatus');
                    if (googleToolsStatus) {
                        googleToolsStatus.textContent = 'Enabled';
                        googleToolsStatus.style.background = 'var(--success-bg)';
                        googleToolsStatus.style.color = 'var(--success-text)';
                    }
                } else {
                    oauthStatus.innerHTML = ' Not connected';
                    updateOAuthServicesStatus(false);
                    console.log('[WARN] No Google OAuth tokens - services disconnected');

                    // Update Google Tools status to Disabled
                    const googleToolsStatus = document.getElementById('googleToolsStatus');
                    if (googleToolsStatus) {
                        googleToolsStatus.textContent = 'Disabled';
                        googleToolsStatus.style.background = 'var(--error-bg)';
                        googleToolsStatus.style.color = 'var(--error-text)';
                    }
                }
            }

            // Update Microsoft 365 OAuth status based on actual token presence
            const microsoft365Status = document.getElementById('microsoft365Status');
            const microsoftTokensExist = profile.microsoft_oauth_connected || false;

            if (microsoft365Status) {
                if (microsoftTokensExist) {
                    microsoft365Status.innerHTML = 'Connected';
                    updateMicrosoft365ServicesStatus(true);
                    console.log('Microsoft 365 OAuth tokens found - services connected');

                    // Update Microsoft Tools status to Enabled
                    const microsoftToolsStatus = document.getElementById('microsoftToolsStatus');
                    if (microsoftToolsStatus) {
                        microsoftToolsStatus.textContent = 'Enabled';
                        microsoftToolsStatus.style.background = 'var(--success-bg)';
                        microsoftToolsStatus.style.color = 'var(--success-text)';
                    }
                } else {
                    microsoft365Status.innerHTML = ' Not connected';
                    updateMicrosoft365ServicesStatus(false);
                    console.log('[WARN] No Microsoft 365 OAuth tokens - services disconnected');

                    // Update Microsoft Tools status to Disabled
                    const microsoftToolsStatus = document.getElementById('microsoftToolsStatus');
                    if (microsoftToolsStatus) {
                        microsoftToolsStatus.textContent = 'Disabled';
                        microsoftToolsStatus.style.background = 'var(--error-bg)';
                        microsoftToolsStatus.style.color = 'var(--error-text)';
                    }
                }
            }

            // Show profile container
            const profileContainer = document.getElementById('userProfileContainer');
            if (profileContainer) {
                // Use flex so avatar + name align properly regardless of platform
                profileContainer.style.display = 'flex';
                console.log('Profile button displayed');
                console.log('[SEARCH] Profile container visibility:', window.getComputedStyle(profileContainer).display);
            } else {
                console.error(' Profile container element not found!');
            }

            // ✅ LAZY LOAD: Microsoft profile data will load when dropdown opens
            // Removed eager loading to reduce startup connection pool exhaustion
            // loadMicrosoft365Profile() now called on-demand (see setupMicrosoft365LazyLoad)

            // Debug: Check if platform sections are visible
            console.log('[SEARCH] Google Workspace section display:', googleWorkspaceSection ? window.getComputedStyle(googleWorkspaceSection).display : 'NOT FOUND');
            console.log('[SEARCH] Microsoft 365 section display:', microsoft365Section ? window.getComputedStyle(microsoft365Section).display : 'NOT FOUND');
            console.log('[SEARCH] Gmail SMTP section display:', gmailSmtpSection ? window.getComputedStyle(gmailSmtpSection).display : 'NOT FOUND');

            // ✅ Load OAuth connections for sidebar
            await loadSidebarOAuthConnections();

            // ✅ Return profile data for caller
            return profile;
        } else {
            console.error(' Profile API returned success=false');
            return null;
        }

    } catch (error) {
        console.error(' Failed to load user profile:', error);
        console.error('Error details:', error.message);

        // Fallback: Show profile button with basic user info from UserAuth
        if (UserAuth.user) {
            console.log('[WARN] Using fallback user data from UserAuth');
            const userNameEl = document.getElementById('userName');
            const dropdownNameEl = document.getElementById('dropdownUserName');
            const dropdownEmailEl = document.getElementById('dropdownUserEmail');

            if (userNameEl) userNameEl.textContent = UserAuth.user.username || 'User';
            if (dropdownNameEl) dropdownNameEl.textContent = UserAuth.user.username || 'User';
            if (dropdownEmailEl) dropdownEmailEl.textContent = UserAuth.user.email || 'No email';

            const profileContainer = document.getElementById('userProfileContainer');
            if (profileContainer) {
                profileContainer.style.display = 'flex';
                console.log('Profile button displayed (fallback mode)');
            }
        }
    } finally {
        // Safety: ensure profile container never stays hidden due to intermediate errors
        const profileContainer = document.getElementById('userProfileContainer');
        if (profileContainer && profileContainer.style.display === 'none') {
            profileContainer.style.display = 'flex';
            console.log('[WARN] Profile container forced visible in finally block');
        }
    }
}  // CLOSING BRACE FOR loadUserProfile() function

/**
 * Trigger full re-authentication flow
 * Clears existing OAuth tokens and restarts OAuth flow
 */
async function triggerReauthentication() {
    console.log(' [REAUTH] Starting re-authentication flow...');

    // Debug: Log full user profile
    console.log(' [REAUTH] Current user profile:', JSON.stringify(UserAuth.user, null, 2));

    try {
        // 1. Show confirmation dialog
        UIComponents.showConfirmation({
            title: 'Re-authentication Required',
            message: 'This will:\n• Sign you out of your current session\n• Clear all OAuth tokens\n• Redirect you to Google/Microsoft login\n\nContinue?',
            variant: 'warning',
            confirmLabel: 'Continue',
            cancelLabel: 'Cancel',
            onConfirm: async () => {
                await this.executeReauth();
            },
            onCancel: () => {
                console.log('[ERROR] [REAUTH] User cancelled re-authentication');
            }
        });
    } catch (error) {
        console.error('[ERROR] [REAUTH] Error showing confirmation:', error);
    }
}

async function executeReauth() {
    try {
        // 2. Get user's authentication platform
        const profile = UserAuth.user;

        // Smart detection: Check multiple indicators
        let authPlatform = profile?.auth_platform;

        // Fallback 1: Check if user email is Microsoft domain
        if (!authPlatform && profile?.email) {
            if (profile.email.includes('@minivetguide.onmicrosoft.com') ||
                profile.email.includes('.onmicrosoft.com') ||
                profile.email.includes('@outlook.com') ||
                profile.email.includes('@hotmail.com') ||
                profile.email.includes('@live.com')) {
                authPlatform = 'microsoft';
                console.log('[SEARCH] [REAUTH] Detected Microsoft from email domain');
            }
        }

        // Fallback 2: Check OAuth connection flags
        if (!authPlatform) {
            if (profile?.microsoft_oauth_connected) {
                authPlatform = 'microsoft';
                console.log('[SEARCH] [REAUTH] Detected Microsoft from oauth_connected flag');
            } else if (profile?.google_oauth_connected) {
                authPlatform = 'google';
                console.log('[SEARCH] [REAUTH] Detected Google from oauth_connected flag');
            }
        }

        // Fallback 3: Default to google
        if (!authPlatform) {
            authPlatform = 'google';
            console.log('[WARN] [REAUTH] No platform detected, defaulting to Google');
        }

        console.log(` [REAUTH] Auth platform: ${authPlatform}`);

        // 3. Call backend to revoke tokens
        console.log('�� [REAUTH] Revoking existing tokens...');
        const revokeResponse = await fetch(`${API_BASE_URL}/api/auth/revoke-tokens`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${UserAuth.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                platform: authPlatform
            })
        });

        const revokeData = await revokeResponse.json();
        console.log(' [REAUTH] Revoke response:', revokeData);

        // 4. Clear local storage
        console.log('[CLEAN] [REAUTH] Clearing local storage...');
        localStorage.removeItem('auth_token');
        localStorage.removeItem('userProfile');
        UserAuth.token = null;
        UserAuth.user = null;
        window.currentUserId = undefined; // Clear global user ID on logout

        // 5. Show loading state
        const reauthBtn = document.getElementById('reauthBtn');
        if (reauthBtn) {
            reauthBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Redirecting...</span>';
            reauthBtn.disabled = true;
        }

        // 6. Redirect to OAuth flow
        console.log(' [REAUTH] Redirecting to OAuth flow...');

        if (authPlatform === 'google') {
            // Google OAuth flow with forced consent
            window.location.href = `${API_BASE_URL}/api/auth/google/login?force_consent=true`;
        } else if (authPlatform === 'microsoft') {
            // Microsoft OAuth flow with forced consent
            window.location.href = `${API_BASE_URL}/api/auth/microsoft/login?force_consent=true`;
        } else {
            // Fallback to login page
            window.location.href = '/login.html';
        }

    } catch (error) {
        console.error('[ERROR] [REAUTH] Re-authentication failed:', error);
        alert('[ERROR] Re-authentication failed: ' + error.message);

        // Reset button state
        const reauthBtn = document.getElementById('reauthBtn');
        if (reauthBtn) {
            reauthBtn.innerHTML = '<i class="fas fa-sync-alt"></i> <span>Re-authenticate Account</span>';
            reauthBtn.disabled = false;
        }
    }
}

// Toggle OAuth services details
function toggleOAuthDetails() {
    const detailsEl = document.getElementById('oauthDetails');
    const arrowEl = document.getElementById('oauthArrow');

    if (detailsEl && arrowEl) {
        const isVisible = detailsEl.style.display !== 'none';
        detailsEl.style.display = isVisible ? 'none' : 'block';
        arrowEl.style.transform = isVisible ? 'rotate(0deg)' : 'rotate(180deg)';
        arrowEl.style.transition = 'transform 0.2s ease';
        console.log(' OAuth details toggled:', isVisible ? 'CLOSED' : 'OPEN');
    }
}

// Toggle Gmail accounts details
function toggleGmailDetails() {
    const detailsEl = document.getElementById('gmailDetails');
    const arrowEl = document.getElementById('gmailArrow');

    if (detailsEl && arrowEl) {
        const isVisible = detailsEl.style.display !== 'none';
        detailsEl.style.display = isVisible ? 'none' : 'block';
        arrowEl.style.transform = isVisible ? 'rotate(0deg)' : 'rotate(180deg)';
        arrowEl.style.transition = 'transform 0.2s ease';
        console.log(' Gmail details toggled:', isVisible ? 'CLOSED' : 'OPEN');
    }
}

// Update OAuth service statuses
function updateOAuthServicesStatus(connected) {
    const services = ['gmail', 'calendar', 'tasks', 'forms', 'docs', 'sheets', 'slides', 'drive'];
    const statusIcon = connected ? '' : '';
    const statusColor = connected ? 'var(--success-color, #22c55e)' : 'var(--text-muted)';

    services.forEach(service => {
        const serviceEl = document.getElementById(`oauth-${service}`);
        if (serviceEl) {
            const statusSpan = serviceEl.querySelector('.service-status');
            if (statusSpan) {
                statusSpan.textContent = statusIcon;
                statusSpan.style.color = statusColor;
            }
        }
    });

    console.log(` Updated OAuth services: ${connected ? 'CONNECTED' : 'DISCONNECTED'}`);
}

// Connect OAuth handler
function connectOAuth() {
    console.log(' Starting OAuth connection...');
    window.location.href = `${API_BASE_URL}/api/oauth/workspace/start?email=${UserAuth.user?.email || ''}`;
}

// Add Gmail account handler
function addGmailAccount() {
    console.log(' Adding Gmail account...');
    alert('Add Gmail Account\n\nThis will open the Gmail authorization flow.\n\nComing soon!');
    // TODO: Implement Gmail-specific OAuth flow
}

// ==================== MICROSOFT 365 OAUTH UI ====================

// Toggle Microsoft 365 OAuth details
function toggleMicrosoft365Details() {
    const detailsEl = document.getElementById('microsoft365Details');
    const arrowEl = document.getElementById('microsoft365Arrow');

    if (detailsEl && arrowEl) {
        const isVisible = detailsEl.style.display !== 'none';
        detailsEl.style.display = isVisible ? 'none' : 'block';
        arrowEl.style.transform = isVisible ? 'rotate(0deg)' : 'rotate(180deg)';
        arrowEl.style.transition = 'transform 0.2s ease';
        console.log(' Microsoft 365 details toggled:', isVisible ? 'CLOSED' : 'OPEN');
    }
}

// Update Microsoft 365 service statuses
function updateMicrosoft365ServicesStatus(connected) {
    const services = ['outlook', 'calendar', 'onedrive', 'sharepoint', 'teams', 'onenote', 'todo'];
    const statusIcon = connected ? '' : '';
    const statusColor = connected ? 'var(--success-color, #22c55e)' : 'var(--text-muted)';

    services.forEach(service => {
        const serviceEl = document.getElementById(`microsoft365-${service}`);
        if (serviceEl) {
            const statusSpan = serviceEl.querySelector('.service-status');
            if (statusSpan) {
                statusSpan.textContent = statusIcon;
                statusSpan.style.color = statusColor;
            }
        }
    });

    console.log(` Updated Microsoft 365 services: ${connected ? 'CONNECTED' : 'DISCONNECTED'}`);
}

// Connect Microsoft 365 handler
function connectMicrosoft365() {
    console.log(' Starting Microsoft 365 OAuth connection...');
    window.location.href = `${API_BASE_URL}/api/auth/microsoft/login`;
}

// Load Microsoft 365 profile from backend status endpoint
async function loadMicrosoft365Profile() {
    console.log(' Loading Microsoft 365 profile...');

    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/microsoft/status`, {
            headers: {
                'Authorization': `Bearer ${UserAuth.token}`
            }
        });

        console.log(' Microsoft status API response:', response.status);

        if (!response.ok) {
            console.error(' Failed to fetch Microsoft status:', response.status);
            return;
        }

        const data = await response.json();
        console.log('Microsoft status data:', data);

        if (data.success && data.connected) {
            const displayName = data.display_name || 'Microsoft User';
            const email = data.microsoft_email || '';
            const microsoftId = data.microsoft_id || '';

            // Update Microsoft 365 status section in dropdown
            const statusEl = document.getElementById('microsoft365Status');
            if (statusEl) {
                statusEl.innerHTML = `
                            <div style="display: flex; flex-direction: column; gap: 2px;">
                                <span style="color: var(--success-color, #22c55e);">${displayName}</span>
                                ${email ? `<span style="font-size: 11px; color: var(--text-muted);">${email}</span>` : ''}
                            </div>
                        `;
            }

            // Mark all services as connected
            updateMicrosoft365ServicesStatus(true);

            console.log('Microsoft 365 profile loaded:', { displayName, email, microsoftId });
        } else {
            console.log('[WARN] Microsoft 365 not connected');
            updateMicrosoft365ServicesStatus(false);
        }

    } catch (error) {
        console.error(' Failed to load Microsoft 365 profile:', error);
    }
}

// Profile menu actions (legacy - kept for compatibility)
function showOAuthStatus() {
    toggleOAuthDetails();
}

function showGmailAccounts() {
    toggleGmailDetails();
}

function showAccountSettings() {
    // Load saved settings or defaults
    loadAccountSettings();

    // Load user memories
    refreshMemories();

    // Load user preferences (tags)
    loadUserPreferences();

    // Show modal
    const modal = document.getElementById('account-settings-modal');
    if (modal) {
        modal.style.display = 'flex';

        // Expand all sections by default - show content divs
        const sectionContents = modal.querySelectorAll('.settings-section-content');
        sectionContents.forEach(content => {
            content.style.display = 'block';
        });

        // Update toggle icons to show expanded state
        const toggleIcons = modal.querySelectorAll('.settings-section-toggle i');
        toggleIcons.forEach(icon => {
            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-up');
        });
    }

    // Close dropdown after clicking
    const userDropdown = document.querySelector('.user-dropdown-menu');
    const userProfileBtn = document.querySelector('.user-profile-btn');
    if (userDropdown) {
        userDropdown.classList.remove('active');
    }
    if (userProfileBtn) {
        userProfileBtn.classList.remove('active');
    }
}

function closeAccountSettings() {
    const modal = document.getElementById('account-settings-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function saveAndCloseSettings() {
    try {
        console.log('saveAndCloseSettings() called');
        saveSettings();
        closeAccountSettings();
    } catch (error) {
        console.error('Error in saveAndCloseSettings():', error);
        showNotification('Error saving settings: ' + error.message, 'error', 4000);
    }
}

// Expose to global scope for HTML inline handlers
window.toggleSettingsSection = function toggleSettingsSection(headerElement) {
    const section = headerElement.closest('.settings-section');
    if (section) {
        section.classList.toggle('collapsed');
    }
}

// Default settings configuration
const DEFAULT_SETTINGS = {
    model: 'claude-sonnet-4-5-20250929',
    temperature: 1.0,
    topP: 1.0,
    enableThinking: false,
    maxRounds: 20,
    roundTimeout: 30,
    enableStreaming: true,
    maxTokens: 16000,
    thinkingBudget: 10000
};

const SETTINGS_STORAGE_KEY = 'accountSettings';

async function loadAccountSettings() {
    console.log('📥 [ACCOUNT SETTINGS] Loading from backend database...');

    try {
        // 1. Fetch from backend database
        const backendUrl = window.API_BASE_URL || 'http://localhost:5001';
        const token = localStorage.getItem('authToken');

        if (!token) {
            console.warn('⚠️ No auth token - using localStorage fallback');
            throw new Error('No auth token');
        }

        const response = await fetch(`${backendUrl}/api/user/preferences`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            console.warn('⚠️ Backend fetch failed - using localStorage fallback');
            throw new Error(`Backend returned ${response.status}`);
        }

        const result = await response.json();
        const data = result.data || result;

        console.log('✅ [ACCOUNT SETTINGS] Loaded from backend:', {
            nickname: data.nickname,
            communication_style: data.communication_style,
            ai_model: data.ai_model,
            ai_temperature: data.ai_temperature
        });

        // 2. Populate UI from backend data
        // AI Model Options
        if (document.getElementById('modelSelect')) {
            document.getElementById('modelSelect').value = data.ai_model || DEFAULT_SETTINGS.model;
        }
        if (document.getElementById('temperature')) {
            const temp = data.ai_temperature || DEFAULT_SETTINGS.temperature;
            document.getElementById('temperature').value = temp;
            document.getElementById('tempValue').textContent = temp;
        }
        if (document.getElementById('topP')) {
            const topP = data.ai_top_p || DEFAULT_SETTINGS.topP;
            document.getElementById('topP').value = topP;
            document.getElementById('toppValue').textContent = topP;
        }
        if (document.getElementById('enableThinking')) {
            document.getElementById('enableThinking').checked = data.ai_thinking_enabled === 1;
        }

        // Token Parameters
        if (document.getElementById('maxTokens')) {
            const maxTokens = data.ai_max_tokens || DEFAULT_SETTINGS.maxTokens;
            document.getElementById('maxTokens').value = maxTokens;
            document.getElementById('tokensValue').textContent = maxTokens;
        }
        if (document.getElementById('thinkingBudgetSlider')) {
            const thinkingBudget = data.ai_thinking_budget || DEFAULT_SETTINGS.thinkingBudget;
            document.getElementById('thinkingBudgetSlider').value = thinkingBudget;
            document.getElementById('thinkingValue').textContent = thinkingBudget;
        }
        if (document.getElementById('enableStreaming')) {
            document.getElementById('enableStreaming').checked = data.ai_streaming_enabled !== 0;
        }

        // Round Parameters (fallback to localStorage/defaults for non-DB fields)
        const stored = localStorage.getItem(SETTINGS_STORAGE_KEY);
        const localSettings = stored ? JSON.parse(stored) : DEFAULT_SETTINGS;

        if (document.getElementById('maxRounds')) {
            document.getElementById('maxRounds').value = localSettings.maxRounds || DEFAULT_SETTINGS.maxRounds;
            document.getElementById('roundsValue').textContent = localSettings.maxRounds || DEFAULT_SETTINGS.maxRounds;
        }
        if (document.getElementById('roundTimeout')) {
            document.getElementById('roundTimeout').value = localSettings.roundTimeout || DEFAULT_SETTINGS.roundTimeout;
            document.getElementById('timeoutValue').textContent = localSettings.roundTimeout || DEFAULT_SETTINGS.roundTimeout;
        }

        // Personalisation Settings
        if (document.getElementById('userNickname')) {
            document.getElementById('userNickname').value = data.nickname || '';
        }
        if (document.getElementById('communicationStyle')) {
            document.getElementById('communicationStyle').value = data.communication_style || 'professional';
        }
        if (document.querySelector('input[name="detailLevel"]')) {
            const detailLevelRadio = document.querySelector(`input[name="detailLevel"][value="${data.detail_level || 'standard'}"]`);
            if (detailLevelRadio) {
                detailLevelRadio.checked = true;
            }
        }
        if (document.getElementById('authPlatform')) {
            document.getElementById('authPlatform').value = data.auth_platform || 'auto';
        }

        // Location & Timezone
        if (document.getElementById('useManualLocation')) {
            document.getElementById('useManualLocation').checked = data.use_manual_location === 1;
            if (document.getElementById('manualLocation')) {
                document.getElementById('manualLocation').disabled = data.use_manual_location !== 1;
            }
        }
        if (document.getElementById('useManualTimezone')) {
            document.getElementById('useManualTimezone').checked = data.use_manual_timezone === 1;
            if (document.getElementById('manualTimezone')) {
                document.getElementById('manualTimezone').disabled = data.use_manual_timezone !== 1;
            }
        }
        if (document.getElementById('manualLocation')) {
            document.getElementById('manualLocation').value = data.manual_location_override || '';
        }
        if (document.getElementById('manualTimezone')) {
            document.getElementById('manualTimezone').value = data.manual_timezone_override || '';
        }

        // Display detected geolocation from backend
        if (data.detected_country || data.detected_city || data.detected_timezone) {
            displayGeolocationData({
                country: data.detected_country || 'Unknown',
                city: data.detected_city || '',
                timezone: data.detected_timezone || 'Unknown',
                ip_address: data.detected_ip_address || 'Unknown'
            });
        } else if (document.getElementById('detectedLocation')) {
            detectAndDisplayGeolocation();
        }

        // Enable/disable thinking budget slider based on extended thinking checkbox
        const thinkingBudgetSlider = document.getElementById('thinkingBudgetSlider');
        if (thinkingBudgetSlider) {
            thinkingBudgetSlider.disabled = !document.getElementById('enableThinking').checked;
        }

        console.log('✅ [ACCOUNT SETTINGS] UI populated from backend database');

    } catch (error) {
        console.error('❌ [ACCOUNT SETTINGS] Backend fetch failed, using localStorage fallback:', error);

        // FALLBACK: Load from localStorage if backend fails
        const stored = localStorage.getItem(SETTINGS_STORAGE_KEY);
        const settings = stored ? JSON.parse(stored) : DEFAULT_SETTINGS;

        // Update UI with localStorage settings - Model Options
        document.getElementById('modelSelect').value = settings.model || DEFAULT_SETTINGS.model;
        document.getElementById('temperature').value = settings.temperature || DEFAULT_SETTINGS.temperature;
        document.getElementById('tempValue').textContent = settings.temperature || DEFAULT_SETTINGS.temperature;
        document.getElementById('topP').value = settings.topP || DEFAULT_SETTINGS.topP;
        document.getElementById('toppValue').textContent = settings.topP || DEFAULT_SETTINGS.topP;
        document.getElementById('enableThinking').checked = settings.enableThinking || false;

        // Update UI - Round Parameters
        document.getElementById('maxRounds').value = settings.maxRounds || DEFAULT_SETTINGS.maxRounds;
        document.getElementById('roundsValue').textContent = settings.maxRounds || DEFAULT_SETTINGS.maxRounds;
        document.getElementById('roundTimeout').value = settings.roundTimeout || DEFAULT_SETTINGS.roundTimeout;
        document.getElementById('timeoutValue').textContent = settings.roundTimeout || DEFAULT_SETTINGS.roundTimeout;
        document.getElementById('enableStreaming').checked = settings.enableStreaming !== false;

        // Update UI - Token Parameters
        document.getElementById('maxTokens').value = settings.maxTokens || DEFAULT_SETTINGS.maxTokens;
        document.getElementById('tokensValue').textContent = settings.maxTokens || DEFAULT_SETTINGS.maxTokens;
        document.getElementById('thinkingBudgetSlider').value = settings.thinkingBudget || DEFAULT_SETTINGS.thinkingBudget;
        document.getElementById('thinkingValue').textContent = settings.thinkingBudget || DEFAULT_SETTINGS.thinkingBudget;

        // Update UI - Personalisation Settings
        if (document.getElementById('userNickname')) {
            document.getElementById('userNickname').value = settings.nickname || '';
        }
        if (document.getElementById('communicationStyle')) {
            document.getElementById('communicationStyle').value = settings.communicationStyle || 'professional';
        }
        if (document.querySelector('input[name="detailLevel"]')) {
            const detailLevelRadio = document.querySelector(`input[name="detailLevel"][value="${settings.detailLevel || 'standard'}"]`);
            if (detailLevelRadio) {
                detailLevelRadio.checked = true;
            }
        }
        if (document.getElementById('authPlatform')) {
            document.getElementById('authPlatform').value = settings.authPlatform || 'auto';
        }

        // Update UI - Location & Timezone
        if (document.getElementById('useManualLocation')) {
            document.getElementById('useManualLocation').checked = settings.useManualLocation || false;
            document.getElementById('manualLocation').disabled = !settings.useManualLocation;
        }
        if (document.getElementById('useManualTimezone')) {
            document.getElementById('useManualTimezone').checked = settings.useManualTimezone || false;
            document.getElementById('manualTimezone').disabled = !settings.useManualTimezone;
        }
        if (document.getElementById('manualLocation')) {
            document.getElementById('manualLocation').value = settings.manualLocation || '';
        }
        if (document.getElementById('manualTimezone')) {
            document.getElementById('manualTimezone').value = settings.manualTimezone || '';
        }

        // Load and display detected geolocation
        if (document.getElementById('detectedLocation')) {
            detectAndDisplayGeolocation();
        }

        // Enable/disable thinking budget slider based on extended thinking checkbox
        const thinkingBudgetSlider = document.getElementById('thinkingBudgetSlider');
        if (thinkingBudgetSlider) {
            thinkingBudgetSlider.disabled = !document.getElementById('enableThinking').checked;
        }

        console.log('✅ [ACCOUNT SETTINGS] UI populated from localStorage (fallback mode)');
    }
}

// Expose to global scope so HTML inline handlers can call it
window.saveSettings = async function saveSettings() {
    try {
        console.log('🔧 [ACCOUNT SETTINGS] saveSettings() called');

        // Get current values from UI with error checking
        const modelSelect = document.getElementById('modelSelect');
        const temperature = document.getElementById('temperature');
        const topP = document.getElementById('topP');
        const enableThinking = document.getElementById('enableThinking');
        const maxRounds = document.getElementById('maxRounds');
        const roundTimeout = document.getElementById('roundTimeout');
        const enableStreaming = document.getElementById('enableStreaming');
        const maxTokens = document.getElementById('maxTokens');
        const thinkingBudget = document.getElementById('thinkingBudget');
        const userNickname = document.getElementById('userNickname');
        const communicationStyle = document.getElementById('communicationStyle');
        const detailLevelRadio = document.querySelector('input[name="detailLevel"]:checked');
        const authPlatform = document.getElementById('authPlatform');
        const useManualLocation = document.getElementById('useManualLocation');
        const useManualTimezone = document.getElementById('useManualTimezone');
        const manualLocation = document.getElementById('manualLocation');
        const manualTimezone = document.getElementById('manualTimezone');

        const settings = {
            // Model Options
            model: modelSelect ? modelSelect.value : 'claude-sonnet-4-5-20250929',
            temperature: temperature ? parseFloat(temperature.value) : 1.0,
            topP: topP ? parseFloat(topP.value) : 1.0,
            enableThinking: enableThinking ? enableThinking.checked : false,

            // Round Parameters
            maxRounds: maxRounds ? parseInt(maxRounds.value) : 10,
            roundTimeout: roundTimeout ? parseInt(roundTimeout.value) : 60,
            enableStreaming: enableStreaming ? enableStreaming.checked : true,

            // Token Parameters
            maxTokens: maxTokens ? parseInt(maxTokens.value) : 4096,
            thinkingBudget: thinkingBudget ? parseInt(thinkingBudget.value) : 10000,

            // Personalisation Settings
            nickname: userNickname ? userNickname.value : '',
            communicationStyle: communicationStyle ? communicationStyle.value : 'professional',
            detailLevel: detailLevelRadio ? detailLevelRadio.value : 'standard',
            authPlatform: authPlatform ? authPlatform.value : 'auto',

            // Location & Timezone
            useManualLocation: useManualLocation ? useManualLocation.checked : false,
            useManualTimezone: useManualTimezone ? useManualTimezone.checked : false,
            manualLocation: manualLocation ? manualLocation.value : '',
            manualTimezone: manualTimezone ? manualTimezone.value : '',

            // Metadata
            lastUpdated: new Date().toISOString()
        };

        console.log('Settings object created:', settings);

        // Save to localStorage
        localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(settings));
        console.log('Saved to localStorage');

        // Save to backend if user is authenticated
        if (window.currentUserId) {
            console.log('Saving ALL settings to backend for user:', window.currentUserId);
            saveAllSettingsToBackend(window.currentUserId, settings);
        } else {
            console.log('No currentUserId - skipping backend save');
        }

        // Show notification
        showNotification('Account Settings Saved Successfully!', 'success', 3000);

        console.log('Account settings saved successfully:', settings);
        return settings;
    } catch (error) {
        console.error('Error in saveSettings():', error);
        showNotification('Failed to save settings: ' + error.message, 'error', 4000);
        throw error;
    }
}

// UNIFIED: Save ALL settings to backend database in one call
async function saveAllSettingsToBackend(userId, settings) {
    try {
        const backendUrl = window.API_BASE_URL || 'http://localhost:5001';

        // Get detected geolocation data from UI
        const detectedLocation = document.getElementById('detectedLocation').textContent;
        const detectedIP = document.getElementById('detectedIP').textContent;
        const detectedTimezone = document.getElementById('detectedTimezone').textContent;

        // Parse detected location into city and country
        let detectedCity = '';
        let detectedCountry = '';
        if (detectedLocation && detectedLocation !== 'Detecting...' && detectedLocation !== 'Unable to detect') {
            const parts = detectedLocation.split(', ');
            if (parts.length >= 2) {
                detectedCity = parts[0];
                detectedCountry = parts[1];
            } else {
                detectedCountry = parts[0];
            }
        }

        // Build comprehensive payload with ALL fields from the modal
        const payload = {
            user_id: userId,

            // Personalisation Settings
            nickname: settings.nickname || '',
            communication_style: settings.communicationStyle || 'professional',
            detail_level: settings.detailLevel || 'standard',
            auth_platform: settings.authPlatform || 'auto',

            // Location & Timezone
            use_manual_location: settings.useManualLocation || false,
            use_manual_timezone: settings.useManualTimezone || false,
            manual_location_override: settings.manualLocation || '',
            manual_timezone_override: settings.manualTimezone || '',
            detected_country: detectedCountry,
            detected_city: detectedCity,
            detected_timezone: detectedTimezone,
            detected_ip_address: detectedIP,

            // User Preferences (from tag system)
            preferred_tools: JSON.stringify(preferredTools || []),
            custom_preferences: JSON.stringify(customPreferences || [])
        };

        console.log('Sending comprehensive payload to backend:', payload);

        const response = await fetch(`${backendUrl}/api/user/preferences`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Backend save failed:', response.statusText, errorText);
            showNotification('Failed to save to backend: ' + response.statusText, 'warning', 3000);
        } else {
            const data = await response.json();
            console.log('All settings saved to backend successfully:', data);
        }
    } catch (error) {
        console.error('Error saving settings to backend:', error);
        showNotification('Warning: Settings saved locally but backend sync failed', 'warning', 3000);
    }
}

// NEW: Detect geolocation from IP address
async function detectAndDisplayGeolocation() {
    try {
        // Try to get geolocation from backend first
        const backendUrl = window.API_BASE_URL || 'http://localhost:5001';
        const response = await fetch(`${backendUrl}/api/geolocation/detect`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            displayGeolocationData(data);
        } else {
            // Fallback to ipapi service
            const ipResponse = await fetch('https://ipapi.co/json/');
            const ipData = await ipResponse.json();
            displayGeolocationData({
                country: ipData.country_name,
                city: ipData.city,
                timezone: ipData.timezone,
                ip_address: ipData.ip
            });
        }
    } catch (error) {
        console.warn('Geolocation detection failed:', error);
        document.getElementById('detectedLocation').textContent = 'Unable to detect';
        document.getElementById('detectedTimezone').textContent = 'Unable to detect';
    }
}

function displayGeolocationData(data) {
    const location = data.city && data.country ? `${data.city}, ${data.country}` : data.country || 'Unknown';
    const timezone = data.timezone || 'Unknown';
    const ip = data.ip_address || 'Unknown';

    document.getElementById('detectedLocation').textContent = location;
    document.getElementById('detectedTimezone').textContent = timezone;
    document.getElementById('detectedIP').textContent = ip;

    // Update current time based on timezone
    updateCurrentTime(timezone);
}

function updateCurrentTime(timezone) {
    try {
        // CRITICAL FIX: Don't attempt to use 'Unknown' or invalid timezones
        if (!timezone || timezone === 'Unknown' || timezone.trim() === '') {
            document.getElementById('currentTime').textContent = 'Timezone not set';
            return;
        }

        const now = new Date();
        const timeString = now.toLocaleString('en-US', { timeZone: timezone, hour12: true });
        document.getElementById('currentTime').textContent = timeString;
    } catch (error) {
        console.warn('Failed to display time:', error);
        document.getElementById('currentTime').textContent = 'Invalid timezone';
    }
}

// Expose to global scope for HTML inline handlers
window.toggleManualLocation = function toggleManualLocation() {
    const checkbox = document.getElementById('useManualLocation');
    const input = document.getElementById('manualLocation');
    input.disabled = !checkbox.checked;
    if (checkbox.checked) {
        input.focus();
    }
    saveSettings();
}

// Expose to global scope for HTML inline handlers
window.toggleManualTimezone = function toggleManualTimezone() {
    const checkbox = document.getElementById('useManualTimezone');
    const select = document.getElementById('manualTimezone');
    select.disabled = !checkbox.checked;
    if (checkbox.checked) {
        select.focus();
    }
    saveSettings();
}

// Expose to global scope for HTML inline handlers
window.resetAccountSettings = function resetAccountSettings() {
    UIComponents.showConfirmation({
        title: 'Reset Settings?',
        message: 'This will reset all settings to defaults. This action cannot be undone.',
        variant: 'danger',
        confirmLabel: 'Reset',
        cancelLabel: 'Cancel',
        onConfirm: () => {
            localStorage.removeItem(SETTINGS_STORAGE_KEY);
            loadAccountSettings();
            showSettingsSaved('Settings reset to defaults');
        }
    });
}

function showSettingsSaved(message = 'Settings saved!') {
    // Show brief toast notification
    const toast = document.createElement('div');
    toast.style.cssText = `
                                                                                                                                    position: fixed;
                                                                                                                                    bottom: 20px;
                                                                                                                                    right: 20px;
                                                                                                                                    background: var(--accent-primary);
                                                                                                                                    color: white;
                                                                                                                                    padding: 12px 20px;
                                                                                                                                    border-radius: 6px;
                                                                                                                                    font-size: 14px;
                                                                                                                                    z-index: 10001;
                                                                                                                                    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
                                                                                                                                    animation: slideIn 0.3s ease;
                                                                                                                                    `;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

function getAccountSettings() {
    // Get current settings (for use by AI agent)
    const stored = localStorage.getItem(SETTINGS_STORAGE_KEY);
    return stored ? JSON.parse(stored) : DEFAULT_SETTINGS;
}

// When extended thinking is toggled, enable/disable the thinking budget slider
document.addEventListener('DOMContentLoaded', function () {
    const enableThinking = document.getElementById('enableThinking');
    if (enableThinking) {
        enableThinking.addEventListener('change', function () {
            const thinkingBudgetSlider = document.getElementById('thinkingBudgetSlider');
            if (thinkingBudgetSlider) {
                thinkingBudgetSlider.disabled = !this.checked;
            }
        });
    }
});

function showNotifications() {
    // TODO: Implement notifications panel
    alert('Notification Preferences\n\nThis will open notification settings.\n\nComing soon!');
}

function showAppearance() {
    // Already has theme toggle, could expand
    const currentTheme = document.body.classList.contains('dark-theme') ? 'Dark' : 'Light';
    alert(`Appearance Settings\n\nCurrent theme: ${currentTheme}\n\nUse the moon/sun icon in the header to toggle themes.\n\nMore appearance options coming soon!`);
}

function showSecurity() {
    // TODO: Implement security panel
    alert('Security Settings\n\n• Change password\n• Two-factor authentication\n• Active sessions\n• Login history\n\nComing soon!');
}

function showHelp() {
    window.open('https://github.com/gerardovsa/AI_agents/blob/main/README.md', '_blank');
}

function showKeyboardShortcuts() {
    alert('Keyboard Shortcuts\n\n' +
        'Ctrl + K - Search platforms\n' +
        'Ctrl + / - Show shortcuts\n' +
        'Ctrl + B - Toggle sidebar\n' +
        'Ctrl + Enter - Send AI message\n' +
        'Esc - Close dropdowns/modals');
}

// ==================== MEMORY MANAGEMENT FUNCTIONS ====================

async function loadUserMemories() {
    try {
        const backendUrl = window.API_BASE_URL || 'http://localhost:5001';
        const response = await fetch(`${backendUrl}/api/user/preferences`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });

        if (!response.ok) {
            console.error('Failed to load user preferences');
            return [];
        }

        const data = await response.json();
        const memoriesJSON = data.data.ai_memories || '[]';
        const memories = JSON.parse(memoriesJSON);

        // Update memory count badge
        const memoryCountBadge = document.getElementById('memoryCount');
        if (memoryCountBadge) {
            memoryCountBadge.textContent = memories.length;
        }

        return memories;
    } catch (error) {
        console.error('Error loading memories:', error);
        return [];
    }
}

async function refreshMemories() {
    try {
        const memories = await loadUserMemories();
        renderMemories(memories);
    } catch (error) {
        console.error('Error refreshing memories:', error);
    }
}

function renderMemories(memories) {
    const container = document.getElementById('memoriesContainer');
    if (!container) return;

    if (!memories || memories.length === 0) {
        container.innerHTML = `
                    <div style="text-align: center; padding: 24px; color: var(--text-muted);">
                        <i class="fas fa-brain" style="font-size: 32px; margin-bottom: 12px; opacity: 0.5;"></i>
                        <p>No memories stored yet</p>
                        <small>Click "Add Memory" above to create your first memory</small>
                    </div>
                `;
        return;
    }

    // Sort by created_at descending (newest first)
    memories.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    // Render memory cards
    container.innerHTML = memories.map(memory => `
                                                                                                                                    <div class="memory-card" data-memory-id="${memory.id}" style="
                    background: var(--bg-tertiary);
                    border: 1px solid var(--border-default);
                    border-radius: 8px;
                    padding: 12px;
                    margin-bottom: 12px;
                ">
                                                                                                                                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                                                                                                                                            <div style="flex: 1;">
                                                                                                                                                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                                                                                                                                                    <span class="memory-category-badge" style="
                                    background: ${getCategoryColor(memory.category)};
                                    color: white;
                                    padding: 2px 8px;
                                    border-radius: 4px;
                                    font-size: 11px;
                                    font-weight: 600;
                                    text-transform: uppercase;
                                ">${memory.category}</span>
                                                                                                                                                    ${memory.tags && memory.tags.length > 0 ? memory.tags.map(tag => `
                                    <span style="
                                        background: var(--bg-hover);
                                        color: var(--text-secondary);
                                        padding: 2px 6px;
                                        border-radius: 3px;
                                        font-size: 10px;
                                    ">${tag}</span>
                                `).join('') : ''}
                                                                                                                                                </div>
                                                                                                                                                <p style="
                                margin: 0;
                                font-size: 14px;
                                color: var(--text-primary);
                                line-height: 1.4;
                            ">${escapeHtml(memory.content)}</p>
                                                                                                                                                <small style="
                                color: var(--text-muted);
                                font-size: 11px;
                                display: block;
                                margin-top: 6px;
                            ">
                                                                                                                                                    <i class="fas fa-clock"></i> ${formatMemoryDate(memory.created_at)}
                                                                                                                                                </small>
                                                                                                                                            </div>
                                                                                                                                            <div style="display: flex; gap: 4px;">
                                                                                                                                                <button onclick='showEditMemoryModal(${JSON.stringify(memory)})' style="
                                background: transparent;
                                border: none;
                                color: var(--text-muted);
                                cursor: pointer;
                                padding: 4px 8px;
                                border-radius: 4px;
                                transition: all 0.2s;
                            " onmouseover="this.style.background='rgba(59, 130, 246, 0.1)'; this.style.color='#3b82f6';"
                                                                                                                                                    onmouseout="this.style.background='transparent'; this.style.color='var(--text-muted)';"
                                                                                                                                                    title="Edit memory">
                                                                                                                                                    <i class="fas fa-edit"></i>
                                                                                                                                                </button>
                                                                                                                                                <button onclick="deleteMemory('${memory.id}')" style="
                                background: transparent;
                                border: none;
                                color: var(--text-muted);
                                cursor: pointer;
                                padding: 4px 8px;
                                border-radius: 4px;
                                transition: all 0.2s;
                            " onmouseover="this.style.background='rgba(239, 68, 68, 0.1)'; this.style.color='#ef4444';"
                                                                                                                                                    onmouseout="this.style.background='transparent'; this.style.color='var(--text-muted)';"
                                                                                                                                                    title="Delete memory">
                                                                                                                                                    <i class="fas fa-trash"></i>
                                                                                                                                                </button>
                                                                                                                                            </div>
                                                                                                                                        </div>
                                                                                                                                    </div>
                                                                                                                                    `).join('');
}

async function deleteMemory(memoryId) {
    UIComponents.showConfirmation({
        title: 'Delete Memory?',
        message: 'This memory will be permanently deleted. This action cannot be undone.',
        variant: 'danger',
        confirmLabel: 'Delete',
        cancelLabel: 'Cancel',
        onConfirm: async () => {
            await executeDeleteMemory(memoryId);
        }
    });
}

async function executeDeleteMemory(memoryId) {
    try {
        const memories = await loadUserMemories();
        const updatedMemories = memories.filter(m => m.id !== memoryId);

        const backendUrl = window.API_BASE_URL || 'http://localhost:5001';
        const response = await fetch(`${backendUrl}/api/user/preferences`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify({
                ai_memories: JSON.stringify(updatedMemories)
            })
        });

        if (!response.ok) {
            throw new Error('Failed to delete memory');
        }

        // Refresh UI
        await refreshMemories();
        showToast('Memory deleted successfully');
    } catch (error) {
        console.error('Error deleting memory:', error);
        alert('Failed to delete memory. Please try again.');
    }
}

function getCategoryColor(category) {
    const colors = {
        'preferences': '#8b5cf6',
        'personal': '#3b82f6',
        'work': '#10b981',
        'health': '#ef4444',
        'general': '#6b7280'
    };
    return colors[category] || colors.general;
}

function formatMemoryDate(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Escape text for use in JavaScript strings (onclick handlers, etc.)
function escapeJs(text) {
    if (!text) return '';
    return text
        .replace(/\\/g, '\\\\')  // Escape backslashes first
        .replace(/'/g, "\\'")     // Escape single quotes
        .replace(/"/g, '\\"')     // Escape double quotes
        .replace(/`/g, '\\`')     // Escape backticks (template literals)
        .replace(/\$/g, '\\$')    // Escape dollar signs (template literal injection)
        .replace(/\n/g, '\\n')    // Escape newlines
        .replace(/\r/g, '\\r')    // Escape carriage returns
        .replace(/\t/g, '\\t')    // Escape tabs
        .replace(/\u2028/g, '\\u2028')  // Escape unicode line separator
        .replace(/\u2029/g, '\\u2029'); // Escape unicode paragraph separator
}

// Safe wrapper for escapeJs with error handling
function safeEscape(value) {
    if (value === null || value === undefined) return '';
    try {
        return escapeJs(String(value));
    } catch (error) {
        console.error('[ERROR] safeEscape failed:', error, 'value:', value);
        return '';
    }
}

// Open dialog to add new agent column
function openAddAgentDialog() {
    const agentName = prompt('Enter agent name (e.g., Delta-4):');
    if (agentName && agentName.trim()) {
        console.log('[Multi-Agent] Adding new agent:', agentName);
        // Create new agent column
        const agentCount = document.querySelectorAll('.agent-column').length + 1;
        const newAgentId = `agent-${agentCount}`;
        const agentContainer = document.getElementById('agent-columns-container');
        if (agentContainer) {
            createAgentColumn(newAgentId, agentName.trim(), null, 'expanded');
            showToast(`Agent ${agentName} added successfully`);
        } else {
            console.error('[Multi-Agent] Agent container not found');
        }
    }
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.style.cssText = `
                                                                                                                                    position: fixed;
                                                                                                                                    bottom: 20px;
                                                                                                                                    right: 20px;
                                                                                                                                    background: var(--accent-success);
                                                                                                                                    color: white;
                                                                                                                                    padding: 12px 20px;
                                                                                                                                    border-radius: 6px;
                                                                                                                                    font-size: 14px;
                                                                                                                                    z-index: 10001;
                                                                                                                                    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
                                                                                                                                    `;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

// ==================== ADD/EDIT MEMORY FUNCTIONS ====================

function showAddMemoryModal() {
    // Clear form for new memory
    document.getElementById('editMemoryId').value = '';
    document.getElementById('memoryContent').value = '';
    document.getElementById('memoryCategory').value = 'general';
    document.getElementById('memoryTags').value = '';
    document.getElementById('cancelMemoryBtn').style.display = 'none';
    // No modal to show - form is already visible in settings
}

function showEditMemoryModal(memory) {
    // Populate form with memory data for editing
    document.getElementById('editMemoryId').value = memory.id;
    document.getElementById('memoryContent').value = memory.content;
    document.getElementById('memoryCategory').value = memory.category;
    document.getElementById('memoryTags').value = memory.tags ? memory.tags.join(', ') : '';
    document.getElementById('cancelMemoryBtn').style.display = 'block';

    // Scroll to the form
    const memoryContent = document.getElementById('memoryContent');
    memoryContent.scrollIntoView({ behavior: 'smooth', block: 'center' });
    memoryContent.focus();
}

function cancelMemoryEdit() {
    // Clear the form and hide cancel button
    document.getElementById('editMemoryId').value = '';
    document.getElementById('memoryContent').value = '';
    document.getElementById('memoryCategory').value = 'general';
    document.getElementById('memoryTags').value = '';
    document.getElementById('cancelMemoryBtn').style.display = 'none';
}

function closeMemoryModal() {
    // Keep for backwards compatibility but does nothing now
    cancelMemoryEdit();
}

async function saveMemory() {
    const content = document.getElementById('memoryContent').value.trim();
    const category = document.getElementById('memoryCategory').value;
    const tagsInput = document.getElementById('memoryTags').value;
    const editId = document.getElementById('editMemoryId').value;

    if (!content) {
        alert('Please enter memory content');
        return;
    }

    const tags = tagsInput.split(',').map(t => t.trim()).filter(t => t.length > 0);

    try {
        const memories = await loadUserMemories();

        if (editId) {
            // Edit existing memory
            const index = memories.findIndex(m => m.id === editId);
            if (index !== -1) {
                memories[index] = {
                    ...memories[index],
                    content: content,
                    category: category,
                    tags: tags
                };
            }
        } else {
            // Add new memory
            const newMemory = {
                id: 'mem_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
                content: content,
                category: category,
                tags: tags,
                created_at: new Date().toISOString(),
                relevance_score: 1.0
            };
            memories.unshift(newMemory);
        }

        // Save to backend
        const backendUrl = window.API_BASE_URL || 'http://localhost:5001';
        const response = await fetch(`${backendUrl}/api/user/preferences`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify({
                ai_memories: JSON.stringify(memories)
            })
        });

        if (!response.ok) {
            throw new Error('Failed to save memory');
        }

        // Clear form and refresh
        cancelMemoryEdit();
        await refreshMemories();

        // Show success notification
        if (editId) {
            showNotification('Memory updated successfully!', 'success', 3000);
        } else {
            showNotification('Memory added successfully!', 'success', 3000);
        }
    } catch (error) {
        console.error('Error saving memory:', error);
        showNotification('Failed to save memory. Please try again.', 'error', 3000);
    }
}

// ==================== END ADD/EDIT MEMORY FUNCTIONS ====================

// ==================== USER PREFERENCES TAG SYSTEM ====================

let preferredTools = [];
let customPreferences = [];

function addPreferredTool() {
    const input = document.getElementById('newToolInput');
    const tool = input.value.trim();

    if (!tool) return;
    if (preferredTools.includes(tool)) {
        _showGeneralNotification('This instruction is already in your preferences.', 'warning');
        return;
    }

    preferredTools.push(tool);
    input.value = '';
    renderPreferredTools();
    savePreferencesToBackend();
}

function removePreferredTool(tool) {
    preferredTools = preferredTools.filter(t => t !== tool);
    renderPreferredTools();
    savePreferencesToBackend();
}

function renderPreferredTools() {
    const container = document.getElementById('preferredToolsContainer');

    console.log('🔧 renderPreferredTools called:', {
        containerFound: !!container,
        preferredToolsLength: preferredTools?.length || 0,
        preferredTools: preferredTools
    });

    if (!container) {
        console.error('❌ preferredToolsContainer not found in DOM');
        return;
    }

    // Ensure preferredTools is an array (defensive programming)
    if (!Array.isArray(preferredTools)) {
        console.warn('⚠️ preferredTools is not an array, resetting to empty array');
        preferredTools = [];
    }

    if (preferredTools.length === 0) {
        container.innerHTML = '<span style="color: var(--text-muted); font-size: 13px;">No mandatory instructions added yet. Type an instruction and click Add.</span>';
        updatePreferencesCount();
        return;
    }

    container.innerHTML = preferredTools.map(tool => `
                                                                                                                                    <div style="
                    background: var(--accent-info);
                    color: white;
                    padding: 4px 10px;
                    border-radius: 16px;
                    font-size: 12px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    cursor: pointer;
                    transition: all 0.2s;
                " onclick="removePreferredTool('${tool.replace(/'/g, "\\'")}')"
                                                                                                                                    onmouseover="this.style.background='#dc3545'"
                   onmouseout="this.style.background='var(--accent-info)'">
                                                                                                                                    ${tool}
                                                                                                                                    <i class="fas fa-times" style="font-size: 10px;"></i>
                                                                                                                                </div>
                                                                                                                                    `).join('');

    updatePreferencesCount();
}

function addCustomPreference() {
    const input = document.getElementById('newPreferenceInput');
    const preference = input.value.trim();

    if (!preference) return;
    if (customPreferences.includes(preference)) {
        _showGeneralNotification('This preference is already saved.', 'warning');
        return;
    }

    customPreferences.push(preference);
    input.value = '';
    renderCustomPreferences();
    savePreferencesToBackend();
}

function removeCustomPreference(preference) {
    customPreferences = customPreferences.filter(p => p !== preference);
    renderCustomPreferences();
    savePreferencesToBackend();
}

function renderCustomPreferences() {
    const container = document.getElementById('customPreferencesContainer');

    console.log('🔧 renderCustomPreferences called:', {
        containerFound: !!container,
        customPreferencesLength: customPreferences?.length || 0,
        customPreferences: customPreferences
    });

    if (!container) {
        console.error('❌ customPreferencesContainer not found in DOM');
        return;
    }

    // Ensure customPreferences is an array (defensive programming)
    if (!Array.isArray(customPreferences)) {
        console.warn('⚠️ customPreferences is not an array, resetting to empty array');
        customPreferences = [];
    }

    if (customPreferences.length === 0) {
        container.innerHTML = '<span style="color: var(--text-muted); font-size: 13px;">No custom preferences added yet. Type a preference and click Add.</span>';
        updatePreferencesCount();
        return;
    }

    container.innerHTML = customPreferences.map(pref => `
                                                                                                                                    <div style="
                    background: var(--accent-primary);
                    color: white;
                    padding: 4px 10px;
                    border-radius: 16px;
                    font-size: 12px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    cursor: pointer;
                    transition: all 0.2s;
                " onclick="removeCustomPreference('${pref.replace(/'/g, "\\'")}')"
                                                                                                                                    onmouseover="this.style.background='#dc3545'"
                   onmouseout="this.style.background='var(--accent-primary)'">
                                                                                                                                    ${pref}
                                                                                                                                    <i class="fas fa-times" style="font-size: 10px;"></i>
                                                                                                                                </div>
                                                                                                                                `).join('');

    updatePreferencesCount();
}

function updatePreferencesCount() {
    const count = preferredTools.length + customPreferences.length;
    const badge = document.getElementById('preferencesCount');
    if (badge) {
        badge.textContent = count;
    }
}

async function savePreferencesToBackend() {
    // This function is called when adding/removing preferred tools or custom preferences
    // We need to save ONLY the preferences fields, not trigger a full settings save
    try {
        if (!window.currentUserId) {
            console.warn('No user ID available, skipping backend save');
            return;
        }

        const backendUrl = window.API_BASE_URL || 'http://localhost:5001';

        // Get current geolocation data
        const detectedLocation = document.getElementById('detectedLocation').textContent;
        const detectedIP = document.getElementById('detectedIP').textContent;
        const detectedTimezone = document.getElementById('detectedTimezone').textContent;

        let detectedCity = '';
        let detectedCountry = '';
        if (detectedLocation && detectedLocation !== 'Detecting...' && detectedLocation !== 'Unable to detect') {
            const parts = detectedLocation.split(', ');
            if (parts.length >= 2) {
                detectedCity = parts[0];
                detectedCountry = parts[1];
            } else {
                detectedCountry = parts[0];
            }
        }

        // Send only the preferences that changed
        const response = await fetch(`${backendUrl}/api/user/preferences`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify({
                user_id: window.currentUserId,
                preferred_tools: JSON.stringify(preferredTools || []),
                custom_preferences: JSON.stringify(customPreferences || []),
                detected_country: detectedCountry,
                detected_city: detectedCity,
                detected_timezone: detectedTimezone,
                detected_ip_address: detectedIP
            })
        });

        if (!response.ok) {
            throw new Error('Failed to save preferences');
        }

        console.log('Preferences saved to backend successfully');
    } catch (error) {
        console.error('Error saving preferences:', error);
        // Don't show notification for every tag add/remove
    }
}

async function loadUserPreferences() {
    try {
        const backendUrl = window.API_BASE_URL || 'http://localhost:5001';
        const response = await fetch(`${backendUrl}/api/user/preferences`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load preferences');
        }

        const result = await response.json();
        const data = result.data || result;  // Handle both response formats

        // Parse preferred tools
        if (data.preferred_tools) {
            try {
                const parsed = JSON.parse(data.preferred_tools);
                // Ensure it's an array, not null or other type
                preferredTools = Array.isArray(parsed) ? parsed : [];
            } catch (e) {
                console.error('Failed to parse preferred_tools:', e);
                preferredTools = [];
            }
        } else {
            preferredTools = [];
        }

        // Parse custom preferences
        if (data.custom_preferences) {
            try {
                const parsed = JSON.parse(data.custom_preferences);
                // Ensure it's an array, not null or other type
                customPreferences = Array.isArray(parsed) ? parsed : [];
            } catch (e) {
                console.error('Failed to parse custom_preferences:', e);
                customPreferences = [];
            }
        } else {
            customPreferences = [];
        }

        // CRITICAL FIX: Display IP-based geolocation data from backend
        if (data.detected_country || data.detected_city || data.detected_timezone) {
            console.log('Using stored IP-based geolocation data from backend');
            displayGeolocationData({
                country: data.detected_country || 'Unknown',
                city: data.detected_city || '',
                timezone: data.detected_timezone || 'Unknown',
                ip_address: data.detected_ip_address || 'Unknown'
            });
        } else {
            // No stored geolocation - trigger fresh detection
            console.log('No stored geolocation found, detecting from IP...');
            detectAndDisplayGeolocation();
        }

        // Render after data is loaded
        renderPreferredTools();
        renderCustomPreferences();

        console.log('✅ User preferences loaded:', {
            preferredTools: preferredTools.length,
            customPreferences: customPreferences.length
        });
    } catch (error) {
        console.error('❌ Error loading preferences:', error);
        // Still render with empty arrays
        renderPreferredTools();
        renderCustomPreferences();
        // Fallback to IP detection on error
        detectAndDisplayGeolocation();
    }
}

// ==================== END USER PREFERENCES TAG SYSTEM ====================

function reportBug() {
    window.open('https://github.com/gerardovsa/AI_agents/issues/new', '_blank');
}

// User menu (placeholder for future expansion)
function showUserMenu() {
    // Legacy function - now using toggleUserMenu()
    toggleUserMenu();
}

// Override fetch to include auth token in all API requests
const originalFetch = window.fetch;
window.fetch = function (...args) {
    const [url, options = {}] = args;

    // Only add auth to API requests (EXCEPT module endpoints in dev mode)
    if (typeof url === 'string' && (url.includes('/api/') || url.includes('/agent/'))) {
        // Skip auth for module discovery endpoints (they use user_id in query params)
        const skipAuthEndpoints = [
            '/api/modules/list',
            '/api/modules/available',
            '/api/modules/needs-setup'
        ];

        const shouldSkipAuth = skipAuthEndpoints.some(endpoint => url.includes(endpoint));

        if (!shouldSkipAuth) {
            options.headers = options.headers || {};

            // Add auth token if available (check UserAuth exists first)
            if (typeof UserAuth !== 'undefined' && UserAuth.token) {
                if (typeof options.headers === 'object' && !(options.headers instanceof Headers)) {
                    options.headers['Authorization'] = `Bearer ${UserAuth.token}`;
                } else if (options.headers instanceof Headers) {
                    options.headers.set('Authorization', `Bearer ${UserAuth.token}`);
                }
            }
        }
    }

    return originalFetch.apply(this, [url, options]);
};

// Initialize authentication on page load
// IMPORTANT: Handle OAuth callback token BEFORE initializing UserAuth

// Track if initializeApp has already run to prevent duplicate calls
let isInitialized = false;

async function initializeApp() {
    // ✅ GUARD #1: Prevent duplicate initialization
    if (isInitialized) {
        console.log('[AUTH] Account profile already initialized, skipping duplicate call');
        return;
    }

    // ✅ GUARD #2 (Nov 24, 2025): If user is ALREADY authenticated (via checkExistingSession)
    // don't call UserAuth.init() again - this prevents double initialization
    if (UserAuth.mainAppInitialized) {
        console.log('[AUTH] Main app already initialized by checkExistingSession path - BLOCKING duplicate init');
        isInitialized = true;
        return;
    }

    // Check for OAuth callback token in URL
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const error = urlParams.get('error');
    const acceptInviteToken = urlParams.get('accept_invite');

    // If an invite token is in the URL, stash it for after login and clean the URL
    if (acceptInviteToken) {
        sessionStorage.setItem('pendingInviteToken', acceptInviteToken);
        urlParams.delete('accept_invite');
        const newSearch = urlParams.toString();
        window.history.replaceState({}, document.title,
            window.location.pathname + (newSearch ? '?' + newSearch : ''));
        console.log('[INVITE] Pending invite token stored from URL');
    }

    if (error) {
        console.error(' OAuth error:', error);

        // Clean URL first
        window.history.replaceState({}, document.title, window.location.pathname);

        // Show login screen with error message
        UserAuth.showLogin();

        // Display error message after login screen is rendered
        setTimeout(() => {
            const errorDiv = document.getElementById('loginError');
            if (errorDiv) {
                let message = urlParams.get('message') || error;

                // Provide user-friendly messages for common OAuth errors
                if (error === 'invalid_state') {
                    message = 'Session expired during login. Please try signing in again.';
                } else if (error === 'access_denied') {
                    message = 'Login was cancelled or access was denied.';
                } else if (error === 'invalid_token') {
                    message = 'Invalid authentication token. Please try signing in again.';
                } else if (error === 'oauth_failed' || error === 'http_error') {
                    // Show detailed error message from backend
                    const detailedMsg = urlParams.get('message');
                    if (detailedMsg) {
                        message = `OAuth login failed: ${decodeURIComponent(detailedMsg)}`;
                        console.error('🚨 [OAUTH ERROR DETAILS]:', decodeURIComponent(detailedMsg));
                    } else {
                        message = `OAuth login failed (${error}). Check browser console for details.`;
                    }
                } else {
                    message = `OAuth login failed: ${decodeURIComponent(message)}`;
                }

                errorDiv.textContent = message;
                errorDiv.classList.add('show');
            }
        }, 100);

        isInitialized = true;
        return;
    } else if (token) {
        console.log('🔐 [OAUTH CALLBACK] OAuth successful, token received');
        console.log('🔐 [OAUTH CALLBACK] Token length:', token.length);
        console.log('🔐 [OAUTH CALLBACK] Token preview:', token.substring(0, 50) + '...');

        // Clear dev mode flag - real OAuth login succeeded
        try {
            localStorage.removeItem('dev_mode_user');
        } catch (e) {
            sessionStorage.removeItem('dev_mode_user');
        }

        // Store token with fallback to sessionStorage
        try {
            localStorage.setItem('authToken', token);
            console.log('✅ [OAUTH CALLBACK] Token stored in localStorage');
        } catch (e) {
            console.warn('⚠️ [OAUTH CALLBACK] localStorage blocked (private browsing?), using sessionStorage:', e);
            sessionStorage.setItem('authToken', token);
            if (typeof UserAuth !== 'undefined' && UserAuth.showPrivateBrowsingWarning) {
                UserAuth.showPrivateBrowsingWarning();
            }
        }
        UserAuth.token = token;
        console.log('✅ [OAUTH CALLBACK] Token set in UserAuth.token');

        // Clean URL IMMEDIATELY for security (remove token from browser history)
        window.history.replaceState({}, document.title, window.location.pathname);
        console.log('✅ [OAUTH CALLBACK] URL cleaned (token removed from browser history)');

        // Load user profile first to detect auth_platform from backend
        console.log('📋 [OAUTH CALLBACK] Loading user profile from backend...');
        try {
            await loadUserProfile();
            console.log('✅ [OAUTH CALLBACK] User profile loaded successfully');
        } catch (error) {
            console.error('❌ [OAUTH CALLBACK] Failed to load user profile:', error);
            // Show login screen with error
            UserAuth.showLogin();
            const errorDiv = document.getElementById('loginError');
            if (errorDiv) {
                errorDiv.textContent = 'Failed to load user profile. Please try again.';
                errorDiv.classList.add('show');
            }
            return;
        }

        // Mark OAuth as connected based on backend's auth_platform
        const userProfile = UserAuth.user || JSON.parse(localStorage.getItem('userProfile') || '{ }');
        const authPlatform = userProfile.auth_platform;

        console.log('🔍 [OAUTH CALLBACK] Detected auth platform:', authPlatform);

        if (authPlatform === 'microsoft') {
            localStorage.setItem('oauth_connected_microsoft', 'true');
            console.log('✅ [OAUTH CALLBACK] Marked Microsoft 365 OAuth as connected');
        } else if (authPlatform === 'google') {
            localStorage.setItem('oauth_connected', 'true');
            console.log('✅ [OAUTH CALLBACK] Marked Google OAuth as connected');
        }

        // Show main app
        console.log('🚀 [OAUTH CALLBACK] Calling UserAuth.showMainApp()...');
        await UserAuth.showMainApp();
        console.log('✅ [OAUTH CALLBACK] Main app initialized successfully');

        // Check for pending org invite (stored before login)
        await checkPendingInvite();

        // Mark as initialized to prevent duplicate calls
        isInitialized = true;

        return; // Don't call init() - we already initialized
    }

    // Check if token exists in localStorage (set by main HTML OAuth detection)
    const storedToken = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');

    if (storedToken && !isInitialized) {
        // Token exists but not in URL - OAuth callback already processed by main HTML
        console.log('🔐 [AUTH] Token found in localStorage - continuing OAuth flow...');
        UserAuth.token = storedToken;

        // Load user profile
        console.log('📋 [AUTH] Loading user profile from backend...');
        try {
            const profile = await loadUserProfile();
            if (!profile) {
                console.error('❌ [AUTH] Failed to load profile');
                throw new Error('Profile load failed');
            }
            console.log('✅ [AUTH] User profile loaded successfully');

            // Show main app with profile (don't reload)
            console.log('🚀 [AUTH] Calling UserAuth.showMainApp() with profile data...');
            await UserAuth.showMainApp(profile);
            console.log('✅ [AUTH] Main app initialized successfully');

            // Check for pending org invite (stored before login)
            await checkPendingInvite();

            isInitialized = true;
            return;
        } catch (error) {
            console.error('❌ [AUTH] Failed to load user profile:', error);
            // Token invalid - clear and show login
            localStorage.removeItem('authToken');
            sessionStorage.removeItem('authToken');
        }
    }

    // No OAuth token in URL AND no valid stored token - proceed with normal init
    console.log('[AUTH] No OAuth token, no existing session - Showing login screen');
    UserAuth.init();

    // Mark as initialized to prevent duplicate calls
    isInitialized = true;

    // ❌ REMOVED (Nov 24, 2025): Causes double DeviceLockManager initialization
    // DeviceLockManager.init() is already called earlier in this file (line 368)
    // after successful OAuth callback handling
    //
    // setTimeout(() => {
    //     if (UserAuth.user) {
    //         DeviceLockManager.init();
    //     }
    // }, 1000);
}

// ✅ LAZY LOAD: Setup Microsoft 365 profile loading on dropdown open (Dec 5, 2025)
function setupMicrosoft365LazyLoad() {
    let loaded = false;

    // Find the account dropdown trigger
    const profileButton = document.getElementById('profileButton');
    if (!profileButton) return;

    // Load on first dropdown open
    profileButton.addEventListener('click', async () => {
        if (loaded) return; // Already loaded

        const isMicrosoftUser = UserAuth?.authMethod === 'microsoft';
        const microsoftTokensExist = UserAuth?.microsoft?.tokens?.access_token;

        if (isMicrosoftUser && microsoftTokensExist) {
            console.log('🔄 [LAZY LOAD] Loading Microsoft 365 profile on first dropdown open...');
            await loadMicrosoft365Profile();
            loaded = true;
        }
    }, { once: false }); // Keep listener active but use loaded flag
}

// Initialize lazy loading after DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupMicrosoft365LazyLoad);
} else {
    setupMicrosoft365LazyLoad();
}

// ============================================================================
// NOTIFICATION HELPERS  (General tab, Team tab, Org tab)
// ============================================================================

function _showGeneralNotification(message, type) {
    const existing = document.getElementById('generalNotification');
    if (existing) existing.remove();
    const palette = {
        error:   { bg: 'rgba(239,68,68,0.12)',  border: '#ef4444', icon: 'fa-exclamation-circle',   color: '#ef4444' },
        warning: { bg: 'rgba(245,158,11,0.12)', border: '#f59e0b', icon: 'fa-exclamation-triangle', color: '#f59e0b' },
        success: { bg: 'rgba(34,197,94,0.12)',  border: '#22c55e', icon: 'fa-check-circle',         color: '#22c55e' }
    };
    const c = palette[type] || palette.error;
    const el = document.createElement('div');
    el.id = 'generalNotification';
    el.setAttribute('role', 'alert');
    el.style.cssText = `margin:0 0 16px;padding:10px 14px;background:${c.bg};border:1px solid ${c.border};` +
        `border-radius:6px;font-size:13px;color:${c.color};display:flex;align-items:center;gap:8px;flex-shrink:0;`;
    el.innerHTML = `<i class="fas ${c.icon}"></i>` +
        `<span style="flex:1;">${message}</span>` +
        `<button onclick="this.closest('#generalNotification').remove()" aria-label="Dismiss"` +
        ` style="background:none;border:none;cursor:pointer;color:${c.color};padding:0;font-size:14px;line-height:1;">` +
        `<i class="fas fa-times"></i></button>`;
    const body = document.querySelector('#settings-tab-general .modal-body');
    if (body) body.insertBefore(el, body.firstChild);
    if (type === 'success' || type === 'warning') setTimeout(() => el.remove(), 3500);
}

function _showOrgNotification(message, type) {
    const existing = document.getElementById('orgNotification');
    if (existing) existing.remove();
    const palette = {
        error:   { bg: 'rgba(239,68,68,0.12)',  border: '#ef4444', icon: 'fa-exclamation-circle',   color: '#ef4444' },
        warning: { bg: 'rgba(245,158,11,0.12)', border: '#f59e0b', icon: 'fa-exclamation-triangle', color: '#f59e0b' },
        success: { bg: 'rgba(34,197,94,0.12)',  border: '#22c55e', icon: 'fa-check-circle',         color: '#22c55e' },
        info:    { bg: 'rgba(59,130,246,0.12)', border: '#3b82f6', icon: 'fa-info-circle',          color: '#3b82f6' }
    };
    const c = palette[type] || palette.error;
    const el = document.createElement('div');
    el.id = 'orgNotification';
    el.setAttribute('role', 'alert');
    el.style.cssText = `margin:0 0 14px;padding:10px 14px;background:${c.bg};border:1px solid ${c.border};` +
        `border-radius:6px;font-size:13px;color:${c.color};display:flex;align-items:flex-start;gap:8px;flex-shrink:0;`;
    el.innerHTML = `<i class="fas ${c.icon}" style="margin-top:1px;"></i>` +
        `<span style="flex:1;line-height:1.45;">${message}</span>` +
        `<button onclick="this.closest('#orgNotification').remove()" aria-label="Dismiss"` +
        ` style="background:none;border:none;cursor:pointer;color:${c.color};padding:0;font-size:14px;line-height:1;flex-shrink:0;">` +
        `<i class="fas fa-times"></i></button>`;
    // Insert at top of active sub-panel, or fall back to orgPanel
    const activeSubPanel = Array.from(document.querySelectorAll('.org-sub-panel')).find(p => p.style.display === 'flex');
    const target = activeSubPanel || document.getElementById('orgDashboard') || document.getElementById('orgPanel');
    if (target) target.insertBefore(el, target.firstChild);
    if (type === 'success') setTimeout(() => el.remove(), 3000);
}

// ============================================================================
// TEAM MEMBERS TAB
// ============================================================================

function showAddTeamMemberForm() {
    const form = document.getElementById('addTeamMemberForm');
    const btn  = document.getElementById('addTeamMemberBtn');
    if (form) form.style.display = 'block';
    if (btn)  btn.style.display  = 'none';
    setTimeout(() => {
        const first = document.getElementById('newTeamUsername');
        if (first) first.focus();
    }, 50);
}

function hideAddTeamMemberForm() {
    const form = document.getElementById('addTeamMemberForm');
    const btn  = document.getElementById('addTeamMemberBtn');
    if (form) form.style.display = 'none';
    if (btn)  btn.style.display  = 'inline-flex';
    ['newTeamUsername', 'newTeamEmail', 'newTeamPassword'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    const scope = document.getElementById('newTeamDataScope');
    if (scope) scope.value = 'own';
    const limit = document.getElementById('newTeamUsageLimit');
    if (limit) limit.value = '1000';
    const existing = document.getElementById('teamNotification');
    if (existing) existing.remove();
}

async function addTeamMember() {
    const username  = document.getElementById('newTeamUsername')?.value.trim();
    const email     = document.getElementById('newTeamEmail')?.value.trim();
    const password  = document.getElementById('newTeamPassword')?.value.trim();
    const dataScope = document.getElementById('newTeamDataScope')?.value || 'own';
    const usageLimit = parseInt(document.getElementById('newTeamUsageLimit')?.value || '1000', 10);
    const saveBtn = document.getElementById('saveNewTeamMemberBtn');

    if (!username) { _showTeamError('Please enter a Username / Team ID.'); return; }
    if (username.length < 2) { _showTeamError('Team ID must be at least 2 characters.'); return; }

    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating…';
    }

    try {
        const body = { team_id: username, data_access_scope: dataScope, usage_limit_daily: usageLimit };
        if (email)    body.email    = email;
        if (password) body.password = password;

        const res  = await fetch(`${window.API_BASE_URL || ''}/api/auth/team-ids/add`, {
            method: 'POST',
            headers: {
                'Content-Type':  'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}`
            },
            body: JSON.stringify(body)
        });
        const data = await res.json();
        if (!res.ok || !data.success) throw new Error(data.error || `Server error (${res.status})`);

        hideAddTeamMemberForm();
        await loadTeamMembers();
        _showTeamSuccess(`Team member "${username}" created successfully.`);
    } catch (err) {
        console.error('[TEAM] addTeamMember error:', err);
        _showTeamError(`Failed to create team member: ${err.message}`);
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="fas fa-save"></i> Create Member';
        }
    }
}

async function loadTeamMembers() {
    const loadingEl = document.getElementById('teamMembersLoading');
    const emptyEl   = document.getElementById('teamMembersEmpty');
    const tableEl   = document.getElementById('teamMembersTable');

    if (loadingEl) { loadingEl.style.display = 'flex'; }
    if (emptyEl)   { emptyEl.style.display   = 'none'; }
    if (tableEl)   { tableEl.style.display   = 'none'; }

    try {
        const res  = await fetch(`${window.API_BASE_URL || ''}/api/auth/team-ids`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}` }
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || `Server error (${res.status})`);

        const members = data.team_ids || [];
        if (loadingEl) loadingEl.style.display = 'none';

        const badge = document.getElementById('teamMemberCount');
        if (badge) badge.textContent = members.length;

        if (members.length === 0) {
            if (emptyEl) emptyEl.style.display = 'flex';
            return;
        }

        if (tableEl) {
            tableEl.style.display = 'block';
            const scopeColors = { own: '#22c55e', team: '#3b82f6', all: '#f59e0b' };
            tableEl.innerHTML = members.map(m => {
                const sc = scopeColors[m.data_access_scope] || '#64748b';
                const lastActive = m.last_active
                    ? new Date(m.last_active).toLocaleDateString('en-AU', { day: '2-digit', month: 'short', year: 'numeric' })
                    : 'Never';
                const safeId = m.team_id.replace(/[^a-zA-Z0-9_-]/g, '_');
                return `<div id="team-item-${safeId}" style="border-bottom:1px solid var(--border-default);">
                    <div style="display:flex;align-items:center;justify-content:space-between;padding:12px 0;">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <div style="width:34px;height:34px;border-radius:50%;background:var(--accent-primary);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;color:white;flex-shrink:0;">
                            ${(m.team_id || 'T')[0].toUpperCase()}
                        </div>
                        <div>
                            <div style="font-size:13px;font-weight:600;color:var(--text-primary);">${m.team_id}</div>
                            <div style="font-size:11px;color:var(--text-muted);">${m.email || 'No email'} &mdash; Last active: ${lastActive}</div>
                        </div>
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;flex-shrink:0;">
                        <span style="font-size:11px;font-weight:600;padding:3px 8px;border-radius:4px;background:${sc}22;color:${sc};">${m.data_access_scope || 'own'}</span>
                        <span style="font-size:11px;color:var(--text-muted);"><i class="fas fa-comment-alt" style="font-size:10px;margin-right:3px;"></i>${m.usage_limit_daily || 0}/day</span>
                        <span style="font-size:11px;padding:3px 8px;border-radius:4px;background:${m.is_active ? 'var(--accent-success)' : 'var(--text-muted)'}22;color:${m.is_active ? 'var(--accent-success)' : 'var(--text-muted)'};"
                        >${m.is_active ? 'Active' : 'Inactive'}</span>
                        <button onclick="editTeamMember('${safeId}')" title="Edit member"
                            style="background:transparent;border:1px solid var(--border-default);color:var(--text-muted);cursor:pointer;padding:4px 8px;border-radius:4px;font-size:11px;">
                            <i class="fas fa-pencil-alt"></i>
                        </button>
                        <button onclick="deleteTeamMember('${m.team_id}')" title="Remove member"
                            style="background:transparent;border:1px solid var(--border-default);color:var(--text-muted);cursor:pointer;padding:4px 8px;border-radius:4px;font-size:11px;">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    </div>
                    <div id="team-edit-${safeId}" data-team-id="${m.team_id}"
                         style="display:none;background:var(--bg-secondary);border-radius:6px;padding:14px 16px;margin-bottom:10px;">
                        <div style="font-size:12px;font-weight:700;color:var(--text-secondary);margin-bottom:10px;text-transform:uppercase;letter-spacing:.4px;">
                            <i class="fas fa-pencil-alt" style="margin-right:5px;"></i>Edit ${m.team_id}
                        </div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">
                            <label style="font-size:12px;color:var(--text-secondary);display:flex;flex-direction:column;gap:4px;">
                                Daily message limit
                                <input type="number" id="edit-limit-${safeId}" value="${m.usage_limit_daily || 1000}" min="0"
                                    style="padding:6px 10px;background:var(--bg-primary);border:1px solid var(--border-default);border-radius:5px;color:var(--text-primary);font-size:12px;">
                            </label>
                            <label style="font-size:12px;color:var(--text-secondary);display:flex;flex-direction:column;gap:4px;">
                                New password <span style="color:var(--text-muted);font-weight:400;">(leave blank to keep)</span>
                                <input type="password" id="edit-pass-${safeId}" placeholder="unchanged"
                                    style="padding:6px 10px;background:var(--bg-primary);border:1px solid var(--border-default);border-radius:5px;color:var(--text-primary);font-size:12px;">
                            </label>
                        </div>
                        <label style="font-size:12px;color:var(--text-secondary);display:inline-flex;align-items:center;gap:6px;margin-bottom:12px;cursor:pointer;">
                            <input type="checkbox" id="edit-active-${safeId}" ${m.is_active ? 'checked' : ''}
                                style="width:14px;height:14px;accent-color:var(--accent-primary);cursor:pointer;">
                            Account active
                        </label>
                        <div style="display:flex;gap:8px;">
                            <button onclick="saveTeamMemberEdit('${safeId}')"
                                style="padding:6px 14px;background:var(--accent-primary);color:white;border:none;border-radius:5px;font-size:12px;cursor:pointer;display:flex;align-items:center;gap:5px;">
                                <i class="fas fa-save"></i> Save changes
                            </button>
                            <button onclick="editTeamMember('${safeId}')"
                                style="padding:6px 14px;background:transparent;border:1px solid var(--border-default);color:var(--text-secondary);border-radius:5px;font-size:12px;cursor:pointer;">
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>`;
            }).join('');
        }
    } catch (err) {
        console.error('[TEAM] loadTeamMembers error:', err);
        if (loadingEl) loadingEl.style.display = 'none';
        if (tableEl) {
            tableEl.style.display = 'block';
            tableEl.innerHTML = `<div style="padding:20px;text-align:center;color:var(--text-muted);">
                <i class="fas fa-exclamation-triangle" style="color:var(--accent-warning);font-size:22px;margin-bottom:8px;display:block;"></i>
                <div style="font-size:13px;margin-bottom:4px;">Failed to load team members</div>
                <div style="font-size:11px;">${err.message}</div>
                <button onclick="loadTeamMembers()" style="margin-top:12px;padding:6px 14px;border-radius:6px;border:1px solid var(--border-default);background:var(--bg-secondary);color:var(--text-primary);cursor:pointer;font-size:12px;">
                    <i class="fas fa-sync"></i> Retry
                </button>
            </div>`;
        }
    }
}

async function deleteTeamMember(teamId) {
    createInlineConfirm({
        title:        'Remove Team Member?',
        message:      `Remove "${teamId}"? They will no longer be able to log in. This cannot be undone.`,
        confirmLabel: 'Remove',
        cancelLabel:  'Cancel',
        onConfirm: async () => {
            try {
                const res  = await fetch(`${window.API_BASE_URL || ''}/api/auth/team-ids/${encodeURIComponent(teamId)}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}` }
                });
                const data = await res.json();
                if (!res.ok || !data.success) throw new Error(data.error || `Server error (${res.status})`);
                await loadTeamMembers();
                _showTeamSuccess(`"${teamId}" removed.`);
            } catch (err) {
                console.error('[TEAM] deleteTeamMember error:', err);
                _showTeamError(`Failed to remove team member: ${err.message}`);
            }
        }
    });
}

function editTeamMember(safeId) {
    const panel = document.getElementById(`team-edit-${safeId}`);
    if (!panel) return;
    const isOpen = panel.style.display !== 'none';
    panel.style.display = isOpen ? 'none' : 'block';
    if (!isOpen) {
        const passInput = panel.querySelector('input[type="password"]');
        if (passInput) passInput.value = '';
        const numInput = panel.querySelector('input[type="number"]');
        if (numInput) numInput.focus();
    }
}

async function saveTeamMemberEdit(safeId) {
    const panel  = document.getElementById(`team-edit-${safeId}`);
    const teamId = panel?.dataset.teamId;
    if (!teamId) return;

    const limit    = parseInt(document.getElementById(`edit-limit-${safeId}`)?.value || '1000', 10);
    const isActive = document.getElementById(`edit-active-${safeId}`)?.checked ?? true;
    const password = document.getElementById(`edit-pass-${safeId}`)?.value.trim();
    const saveBtn  = panel?.querySelector('button[onclick*="saveTeamMemberEdit"]');

    const body = { is_active: isActive, usage_limit_daily: limit };
    if (password) body.password = password;

    if (saveBtn) { saveBtn.disabled = true; saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving…'; }

    try {
        const res  = await fetch(`${window.API_BASE_URL || ''}/api/auth/team-ids/${encodeURIComponent(teamId)}`, {
            method: 'PUT',
            headers: {
                'Content-Type':  'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}`
            },
            body: JSON.stringify(body)
        });
        const data = await res.json();
        if (!res.ok || !data.success) throw new Error(data.error || `Server error (${res.status})`);
        await loadTeamMembers();
        _showTeamSuccess(`"${teamId}" updated successfully.`);
    } catch (err) {
        console.error('[TEAM] saveTeamMemberEdit error:', err);
        _showTeamError(`Failed to update "${teamId}": ${err.message}`);
        if (saveBtn) { saveBtn.disabled = false; saveBtn.innerHTML = '<i class="fas fa-save"></i> Save changes'; }
    }
}

async function exportTeamIdsCsv() {
    try {
        const res = await fetch(`${window.API_BASE_URL || ''}/api/auth/team-ids/export`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}` }
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.error || `Server error (${res.status})`);
        }
        const blob = await res.blob();
        const url  = URL.createObjectURL(blob);
        const a    = document.createElement('a');
        a.href     = url;
        a.download = `team-members-${new Date().toISOString().slice(0, 10)}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    } catch (err) {
        console.error('[TEAM] exportTeamIdsCsv error:', err);
        _showTeamError(`Failed to export team members: ${err.message}`);
    }
}

async function importTeamIdsCsv(fileInput) {
    const file = fileInput?.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const res  = await fetch(`${window.API_BASE_URL || ''}/api/auth/team-ids/import`, {
            method:  'POST',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}` },
            body:    formData
        });
        const data = await res.json();
        if (!res.ok || !data.success) throw new Error(data.error || `Server error (${res.status})`);
        await loadTeamMembers();
        _showTeamSuccess(data.message || 'Team members imported successfully.');
    } catch (err) {
        console.error('[TEAM] importTeamIdsCsv error:', err);
        _showTeamError(`Failed to import team members: ${err.message}`);
    } finally {
        if (fileInput) fileInput.value = '';
    }
}

function _showTeamError(message)   { _showTeamNotification(message, 'error'); }
function _showTeamSuccess(message) { _showTeamNotification(message, 'success'); }

function _showTeamNotification(message, type) {
    const existing = document.getElementById('teamNotification');
    if (existing) existing.remove();

    const palette = {
        error:   { bg: 'rgba(239,68,68,0.12)',   border: '#ef4444', icon: 'fa-exclamation-circle', color: '#ef4444' },
        success: { bg: 'rgba(34,197,94,0.12)',   border: '#22c55e', icon: 'fa-check-circle',       color: '#22c55e' }
    };
    const c = palette[type] || palette.error;

    const el = document.createElement('div');
    el.id = 'teamNotification';
    el.setAttribute('role', 'alert');
    el.style.cssText = `margin:0 20px 12px;padding:10px 14px;background:${c.bg};border:1px solid ${c.border};` +
        `border-radius:6px;font-size:13px;color:${c.color};display:flex;align-items:center;gap:8px;flex-shrink:0;`;
    el.innerHTML = `<i class="fas ${c.icon}"></i>` +
        `<span style="flex:1;">${message}</span>` +
        `<button onclick="this.closest('#teamNotification').remove()" aria-label="Dismiss"` +
        ` style="background:none;border:none;cursor:pointer;color:${c.color};padding:0;font-size:14px;line-height:1;">` +
        `<i class="fas fa-times"></i></button>`;

    const form    = document.getElementById('addTeamMemberForm');
    const teamTab = document.getElementById('settings-tab-team');
    if (form && form.style.display !== 'none') {
        form.parentNode.insertBefore(el, form.nextSibling);
    } else if (teamTab) {
        const header = teamTab.querySelector('.team-tab-header');
        if (header) header.parentNode.insertBefore(el, header.nextSibling);
    }

    if (type === 'success') setTimeout(() => el.remove(), 3000);
}

// ============================================================================
// ORGANISATION TAB
// ============================================================================

// State shared across org functions
let _orgData = null;

/** Tab switcher: General / Team Members / Organisation */
function switchSettingsTab(tab, btn) {
    document.querySelectorAll('.acct-tab-panel').forEach(p => p.style.display = 'none');
    document.querySelectorAll('.acct-tab-btn').forEach(b => b.classList.remove('active'));
    const panel = document.getElementById(`settings-tab-${tab}`);
    if (panel) panel.style.display = 'flex';
    if (btn)  btn.classList.add('active');
    if (tab === 'org')  loadOrgTab();
    if (tab === 'team') loadTeamMembers();
}

/** Sub-tab switcher inside the org dashboard */
function switchOrgSubTab(subtab, btn) {
    document.querySelectorAll('.org-sub-panel').forEach(p => { p.style.display = 'none'; });
    document.querySelectorAll('.org-sub-tab').forEach(b => b.classList.remove('active'));
    const panel = document.getElementById(`org-subtab-${subtab}`);
    if (panel) panel.style.display = 'flex';
    if (btn)  btn.classList.add('active');
    if (subtab === 'members')     loadOrgMembers();
    if (subtab === 'invitations') loadOrgInvitations();
    if (subtab === 'modules' && typeof OrgManager !== 'undefined') OrgManager.loadModuleCatalog();
    if (subtab === 'vault' && typeof OrgManager !== 'undefined') {
        const userLevel = OrgManager._userLevel || 0;
        const addBtn = document.getElementById('orgAddCredBtn');
        if (addBtn) addBtn.style.display = userLevel >= 4 ? 'flex' : 'none';
        if (userLevel >= 3) OrgManager.loadCredentials();
    }
    if (subtab === 'audit' && typeof OrgManager !== 'undefined') {
        if ((OrgManager._userLevel || 0) >= 4) OrgManager.loadAuditLog();
    }
}

/** Entry point: called when user opens the Organisation tab */
async function loadOrgTab() {
    const loading   = document.getElementById('orgLoading');
    const empty     = document.getElementById('orgEmpty');
    const dashboard = document.getElementById('orgDashboard');
    const createForm= document.getElementById('orgCreateForm');

    if (loading)    loading.style.display   = 'flex';
    if (empty)      empty.style.display     = 'none';
    if (dashboard)  dashboard.style.display = 'none';
    if (createForm) createForm.style.display= 'none';

    try {
        const res  = await fetch(`${API_BASE_URL}/api/org/info`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}` }
        });
        const data = await res.json();

        if (loading) loading.style.display = 'none';

        if (!data.success || !data.organisation) {
            if (empty) empty.style.display = 'flex';
            return;
        }

        _orgData = data.organisation;
        // Merge your_role (top-level in API response) into org object so _renderOrgDashboard can display it
        if (data.your_role) _orgData.your_role = data.your_role;
        // GAP-H4: Sync OrgManager role state so Vault / Audit subtabs can gate access
        if (typeof OrgManager !== 'undefined') {
            const ROLE_LEVELS = { viewer: 1, member: 2, manager: 3, admin: 4, owner: 5, platform_developer: 10 };
            const userRole = data.your_role || data.organisation?.your_role || null;
            OrgManager._userRole  = userRole;
            OrgManager._userLevel = ROLE_LEVELS[userRole] || 0;
            OrgManager._orgInfo   = data.organisation;
            OrgManager._orgName   = data.organisation?.display_name || data.organisation?.name || 'our organisation';
        }
        _renderOrgDashboard(_orgData);
        _gateOrgSubTabs(_orgData.your_role);
    } catch (err) {
        console.error('[ORG] Failed to load org tab:', err);
        if (loading) loading.style.display = 'none';
        if (empty)   empty.style.display   = 'flex';
    }
}

/**
 * Hide org sub-tab buttons the current user's role is not permitted to access.
 * Vault: admin+, Modules: member+, Audit: admin+
 * Members + Invitations: hidden entirely for personal orgs (is_personal_org=TRUE).
 */
function _gateOrgSubTabs(userRole) {
    const ROLE_LEVELS = { viewer: 1, member: 2, manager: 3, admin: 4, owner: 5, platform_developer: 10 };
    const level = ROLE_LEVELS[userRole] || 0;
    const rules = {
        vault:   ROLE_LEVELS.admin,     // admin+ only (owners/admins see credentials)
        modules: ROLE_LEVELS.member,    // member+
        audit:   ROLE_LEVELS.admin,     // admin+
    };
    Object.entries(rules).forEach(([subtab, minLevel]) => {
        const btn = document.querySelector(`.org-sub-tab[data-subtab="${subtab}"]`);
        if (btn) btn.style.display = level >= minLevel ? '' : 'none';
    });

    // Personal org (is_personal_org=TRUE) — solo workspace, no team to manage.
    // Hide Members and Invitations subtabs: there are no other members to invite/manage.
    const isPersonal = !!(window._orgIsPersonal);
    ['members', 'invitations'].forEach(subtab => {
        const btn = document.querySelector(`.org-sub-tab[data-subtab="${subtab}"]`);
        if (btn) btn.style.display = isPersonal ? 'none' : '';
    });
}

function _renderOrgDashboard(org) {
    const dashboard = document.getElementById('orgDashboard');
    if (!dashboard) return;
    dashboard.style.display = 'flex';

    // Header identity card
    const headerCard = document.getElementById('orgHeaderCard');
    if (headerCard) {
        const initials = (org.name || 'O').substring(0, 2).toUpperCase();
        headerCard.style.cssText = 'display:flex;align-items:center;gap:14px;padding:18px 24px;border-bottom:1px solid var(--border-default);flex-shrink:0;';
        headerCard.innerHTML = `
                <div class="org-header-avatar">${initials}</div>
                <div>
                    <div class="org-header-name">${org.display_name || org.name}</div>
                    <div class="org-header-meta">
                        <span><i class="fas fa-tag"></i> ${org.slug}</span>
                        <span><i class="fas fa-users"></i> <span id="orgMemberCountInline">...</span> members</span>
                        <span style="color:var(--accent-primary);font-weight:700;">Your role: ${org.your_role || '—'}</span>
                    </div>
                </div>`;
    }

    // Populate overview form
    const nameEl = document.getElementById('editOrgName');
    const descEl = document.getElementById('editOrgDescription');
    const visEl  = document.getElementById('editOrgVisibility');
    const slugEl = document.getElementById('editOrgSlug');

    if (nameEl) nameEl.value = org.display_name || org.name || '';
    if (descEl) descEl.value = org.description || '';
    if (visEl)  visEl.value  = org.visibility   || 'private';
    if (slugEl) slugEl.value = org.slug          || '';

    // Populate allowed_domains (SSO auto-provisioning)
    const domainsEl = document.getElementById('editOrgAllowedDomains');
    if (domainsEl) {
        const domains = Array.isArray(org.allowed_domains) ? org.allowed_domains : [];
        domainsEl.value = domains.join(', ');
    }

    // Populate AI provider/model (GAP-M3)
    const aiProviderEl = document.getElementById('editOrgAiProvider');
    const aiModelEl    = document.getElementById('editOrgAiModel');
    if (aiProviderEl) {
        aiProviderEl.value = org.ai_provider || 'anthropic';
        // Add event listener to update models when provider changes
        aiProviderEl.addEventListener('change', updateOrgAiModelDropdown);
    }
    if (aiModelEl) {
        // Store current value in data attribute for restoration after dropdown rebuild
        const currentModel = org.ai_model || '';
        aiModelEl.setAttribute('data-current-value', currentModel);
        aiModelEl.value = currentModel;
    }
    // Populate the model dropdown based on selected provider
    if (typeof updateOrgAiModelDropdown === 'function') {
        updateOrgAiModelDropdown();
    }

    // Hide save button for non-owners
    const saveBtn = document.getElementById('saveOrgSettingsBtn');
    const isOwner = ['owner', 'admin'].includes(org.your_role);
    if (saveBtn) saveBtn.style.display = isOwner ? 'inline-flex' : 'none';

    // Load member count in the subtab badge
    loadOrgMembers(/* countOnly */ true);
}

async function saveOrgSettings() {
    const nameEl       = document.getElementById('editOrgName');
    const descEl       = document.getElementById('editOrgDescription');
    const visEl        = document.getElementById('editOrgVisibility');
    const domainsEl    = document.getElementById('editOrgAllowedDomains');
    const aiProviderEl = document.getElementById('editOrgAiProvider');
    const aiModelEl    = document.getElementById('editOrgAiModel');
    const btn          = document.getElementById('saveOrgSettingsBtn');

    const name = nameEl?.value.trim();
    if (!name) { _showOrgNotification('Organisation name is required.', 'error'); return; }

    // Parse comma/space-separated domains, lowercase, strip empties
    const rawDomains = domainsEl?.value || '';
    const allowedDomains = rawDomains
        .split(/[\s,]+/)
        .map(d => d.trim().toLowerCase())
        .filter(d => d.length > 0 && d.includes('.'));

    if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...'; }

    try {
        const payload = {
            name:            name,
            description:     descEl?.value.trim() || '',
            visibility:      visEl?.value || 'private',
            allowed_domains: allowedDomains,
        };
        // GAP-M3: include AI provider/model if the fields exist in the DOM
        if (aiProviderEl) payload.ai_provider = aiProviderEl.value || 'anthropic';
        if (aiModelEl)    payload.ai_model    = aiModelEl.value.trim();

        const res  = await fetch(`${API_BASE_URL}/api/org/info`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}`
            },
            body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!data.success) throw new Error(data.error || 'Save failed');

        const headerName = document.querySelector('.org-header-name');
        if (headerName) headerName.textContent = name;
        if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fas fa-check"></i> Saved'; }
        setTimeout(() => { if (btn) btn.innerHTML = '<i class="fas fa-save"></i> Save Settings'; }, 2000);
    } catch (err) {
        console.error('[ORG] saveOrgSettings error:', err);
        _showOrgNotification(`Failed to save: ${err.message}`, 'error');
        if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fas fa-save"></i> Save Settings'; }
    }
}

/** Create-org form helpers */
function showCreateOrgForm() {
    const empty = document.getElementById('orgEmpty');
    const form  = document.getElementById('orgCreateForm');
    if (empty) empty.style.display = 'none';
    if (form)  form.style.display  = 'flex';
}
function hideCreateOrgForm() {
    const empty = document.getElementById('orgEmpty');
    const form  = document.getElementById('orgCreateForm');
    if (form)  form.style.display  = 'none';
    if (empty) empty.style.display = 'flex';
}
function updateOrgSlugPreview() {
    const nameEl = document.getElementById('createOrgName');
    const slugEl = document.getElementById('createOrgSlug');
    if (!nameEl || !slugEl) return;
    slugEl.value = (nameEl.value || '')
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .trim()
        .replace(/\s+/g, '-')
        .substring(0, 50);
}
async function createOrganisation() {
    const name   = document.getElementById('createOrgName')?.value.trim();
    const slug   = document.getElementById('createOrgSlug')?.value.trim();
    const desc   = document.getElementById('createOrgDescription')?.value.trim();
    const vis    = document.getElementById('createOrgVisibility')?.value || 'private';
    const btn    = document.getElementById('createOrgBtn');

    if (!name) { _showOrgNotification('Organisation name is required.', 'error'); return; }

    if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...'; }

    try {
        const res  = await fetch(`${API_BASE_URL}/api/org/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}`
            },
            body: JSON.stringify({ name, slug, description: desc, visibility: vis }),
        });
        const data = await res.json();
        if (!data.success) throw new Error(data.error || 'Create failed');

        // Reload the org tab to show the dashboard
        await loadOrgTab();
        document.getElementById('orgCreateForm').style.display = 'none';
    } catch (err) {
        console.error('[ORG] createOrganisation error:', err);
        _showOrgNotification(`Failed to create organisation: ${err.message}`, 'error');
        if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fas fa-plus"></i> Create Organisation'; }
    }
}

/** Load and render org members list */
async function loadOrgMembers(countOnly = false) {
    const listEl   = document.getElementById('orgMembersList');
    const countEl  = document.getElementById('orgMemberCount');
    const inlineEl = document.getElementById('orgMemberCountInline');

    try {
        const res  = await fetch(`${API_BASE_URL}/api/org/members`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}` }
        });
        const data = await res.json();
        if (!data.success) throw new Error(data.error);

        const members = data.members || [];
        const count   = members.length;

        if (countEl)  countEl.textContent  = count;
        if (inlineEl) inlineEl.textContent = count;

        if (countOnly || !listEl) return;

        const myUserId = UserAuth?.user?.user_id || UserAuth?.user?.id;
        const isOwnerOrAdmin = _orgData && ['owner', 'admin'].includes(_orgData.your_role);

        listEl.innerHTML = members.map(m => {
            const isMe = m.id === myUserId;
            const roleBadgeColor = { owner: '#f59e0b', admin: '#6366f1', manager: '#3b82f6', member: '#22c55e', viewer: '#64748b' }[m.org_role] || '#64748b';
            const canManage = isOwnerOrAdmin && !isMe && m.org_role !== 'owner';
            return `
                <div id="member-wrapper-${m.id}" style="border-bottom:1px solid var(--border-default);">
                    <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 0;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <div style="width:34px;height:34px;border-radius:50%;background:var(--bg-tertiary);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;">
                                ${(m.username || 'U')[0].toUpperCase()}
                            </div>
                            <div>
                                <div style="font-size:13px;font-weight:600;">${m.username}${isMe ? ' <span style="font-size:10px;color:var(--text-muted)">(you)</span>' : ''}</div>
                                <div style="font-size:11px;color:var(--text-muted);">${m.email}</div>
                            </div>
                        </div>
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="font-size:11px;font-weight:700;padding:3px 8px;border-radius:4px;background:${roleBadgeColor}22;color:${roleBadgeColor};">${m.org_role}</span>
                            ${canManage ? `
                            <button onclick="toggleMemberModulesPanel(${m.id})" class="btn btn-sm"
                                style="padding:4px 8px;font-size:11px;background:transparent;border:1px solid var(--border-default);color:var(--text-muted);cursor:pointer;border-radius:4px;"
                                title="Manage module access for this member" id="member-modules-btn-${m.id}">
                                <i class="fas fa-puzzle-piece"></i>
                            </button>
                            <button onclick="removeMemberFromOrg(${m.id},'${m.username}')" class="btn btn-sm" style="padding:4px 8px;font-size:11px;background:transparent;border:1px solid var(--border-default);color:var(--text-muted);cursor:pointer;border-radius:4px;" title="Remove member">
                                <i class="fas fa-times"></i>
                            </button>` : ''}
                        </div>
                    </div>
                    <div id="member-modules-panel-${m.id}" style="display:none;"></div>
                </div>`;
        }).join('') || '<div style="padding:24px 0;text-align:center;color:var(--text-muted);font-size:13px;">No members found.</div>';

    } catch (err) {
        console.error('[ORG] loadOrgMembers error:', err);
        if (listEl) listEl.innerHTML = '<div style="padding:20px;color:var(--text-muted);">Failed to load members.</div>';
    }
}

function removeMemberFromOrg(userId, username) {
    createInlineConfirm({
        title:        'Remove Member?',
        message:      `Remove "${username}" from the organisation? They will lose access immediately.`,
        confirmLabel: 'Remove',
        cancelLabel:  'Cancel',
        onConfirm: async () => {
            try {
                const res  = await fetch(`${API_BASE_URL}/api/org/members/${userId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}` }
                });
                const data = await res.json();
                if (!data.success) throw new Error(data.error);
                loadOrgMembers();
                _showOrgNotification(`${username} removed from the organisation.`, 'success');
            } catch (err) {
                _showOrgNotification(`Failed to remove member: ${err.message}`, 'error');
            }
        }
    });
}

/**
 * Toggle the per-member module access panel below the member row.
 * Opens on first click (fetches live data), closes on second click.
 */
async function toggleMemberModulesPanel(userId) {
    const panel = document.getElementById(`member-modules-panel-${userId}`);
    const btn   = document.getElementById(`member-modules-btn-${userId}`);
    if (!panel) return;

    // If already open, close it
    if (panel.style.display !== 'none') {
        panel.style.display = 'none';
        if (btn) btn.style.borderColor = '';
        return;
    }

    // Open and load
    panel.style.display = 'block';
    if (btn) btn.style.borderColor = 'var(--accent-primary)';
    panel.innerHTML = '<div style="padding:10px 12px 12px 44px;"><i class="fas fa-spinner fa-spin" style="color:var(--text-muted);"></i></div>';

    try {
        const res  = await fetch(`${API_BASE_URL}/api/org/members/${userId}/modules`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}` }
        });
        const data = await res.json();
        if (!data.success) throw new Error(data.error || 'Failed to load module access');

        const modules  = data.modules || [];
        const username = data.username || 'this member';

        if (!modules.length) {
            panel.innerHTML = `
                <div style="padding:10px 12px 14px 44px;font-size:12px;color:var(--text-muted);">
                    No modules currently enabled for this organisation.
                </div>`;
            return;
        }

        const rows = modules.map(m => `
            <div style="display:flex;align-items:center;gap:10px;padding:6px 0;border-bottom:1px solid var(--border-default);">
                <div style="width:24px;height:24px;border-radius:5px;flex-shrink:0;
                            background:${m.icon_color || '#6B7280'}22;
                            display:flex;align-items:center;justify-content:center;">
                    <i class="${m.icon_class || 'fas fa-cube'}" style="color:${m.icon_color || '#6B7280'};font-size:11px;"></i>
                </div>
                <span style="flex:1;font-size:12px;color:var(--text-primary);">${m.display_name}</span>
                <label style="display:inline-flex;align-items:center;gap:5px;cursor:pointer;flex-shrink:0;">
                    <input type="checkbox" ${m.effective ? 'checked' : ''}
                        onchange="setMemberModuleAccess(${userId}, '${m.module_name}', this.checked)"
                        style="width:14px;height:14px;cursor:pointer;accent-color:var(--accent-primary);">
                    <span id="umf-label-${userId}-${m.module_name}"
                          style="font-size:11px;color:${m.effective ? 'var(--success,#22c55e)' : 'var(--text-muted)'};"
                    >${m.effective ? 'On' : 'Restricted'}</span>
                </label>
            </div>`).join('');

        panel.innerHTML = `
            <div style="background:var(--bg-secondary);border-top:1px solid var(--border-default);
                        border-radius:0 0 6px 6px;padding:12px 12px 14px 44px;margin-bottom:2px;">
                <div style="font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;
                            color:var(--text-muted);margin-bottom:4px;">
                    <i class="fas fa-puzzle-piece" style="margin-right:5px;"></i>Module Access — ${username}
                </div>
                <div style="font-size:11px;color:var(--text-muted);margin-bottom:10px;">
                    Uncheck to restrict this member from an org-enabled module.
                    Changes take effect on their next page load.
                </div>
                ${rows}
                <div style="margin-top:10px;">
                    <button onclick="resetMemberModuleAccess(${userId})" style="
                        font-size:11px;padding:4px 10px;background:transparent;
                        border:1px solid var(--border-default);color:var(--text-muted);
                        border-radius:4px;cursor:pointer;">
                        <i class="fas fa-undo"></i> Reset to org defaults
                    </button>
                </div>
            </div>`;

    } catch (err) {
        panel.innerHTML = `<div style="padding:8px 12px 12px 44px;font-size:12px;color:var(--danger,#ef4444);">${err.message}</div>`;
    }
}

/**
 * Set (or remove) a per-user module restriction.
 * enabled=true  → removes restriction (inherits org access)
 * enabled=false → writes restriction row (user cannot use this module)
 */
async function setMemberModuleAccess(userId, moduleName, enabled) {
    try {
        const res  = await fetch(`${API_BASE_URL}/api/org/members/${userId}/modules/${moduleName}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}`
            },
            body: JSON.stringify({ enabled })
        });
        const data = await res.json();
        if (!data.success) {
            _showOrgNotification(data.error || 'Failed to update module access', 'error');
            // Re-open panel to restore correct checkbox state
            const panel = document.getElementById(`member-modules-panel-${userId}`);
            if (panel) { panel.style.display = 'none'; }
            toggleMemberModulesPanel(userId);
            return;
        }
        // Update label inline without reloading the panel
        const label = document.getElementById(`umf-label-${userId}-${moduleName}`);
        if (label) {
            label.textContent = enabled ? 'On' : 'Restricted';
            label.style.color = enabled ? 'var(--success,#22c55e)' : 'var(--text-muted)';
        }
    } catch (err) {
        _showOrgNotification('Error updating module access: ' + err.message, 'error');
    }
}

/**
 * Reset ALL per-user module overrides for a member (restore org defaults).
 */
function resetMemberModuleAccess(userId) {
    createInlineConfirm({
        title:        'Reset Module Access?',
        message:      'Reset all module restrictions for this member? They will inherit the organisation defaults.',
        confirmLabel: 'Reset',
        cancelLabel:  'Cancel',
        onConfirm: async () => {
            try {
                const res  = await fetch(`${API_BASE_URL}/api/org/members/${userId}/modules`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}` }
                });
                const data = await res.json();
                if (!data.success) throw new Error(data.error);
                const panel = document.getElementById(`member-modules-panel-${userId}`);
                if (panel) { panel.style.display = 'none'; }
                toggleMemberModulesPanel(userId);
            } catch (err) {
                _showOrgNotification('Failed to reset: ' + err.message, 'error');
            }
        }
    });
}
window.removeMemberFromOrg = removeMemberFromOrg;
window.toggleMemberModulesPanel  = toggleMemberModulesPanel;
window.setMemberModuleAccess     = setMemberModuleAccess;
window.resetMemberModuleAccess   = resetMemberModuleAccess;

/** Invite member inline form */
function showInviteMemberUI() {
    const form = document.getElementById('inviteMemberForm');
    if (form) form.style.display = 'block';
    document.getElementById('inviteEmail')?.focus();
}
function hideInviteMemberUI() {
    const form = document.getElementById('inviteMemberForm');
    if (form) form.style.display = 'none';
    if (document.getElementById('inviteEmail'))   document.getElementById('inviteEmail').value   = '';
    if (document.getElementById('inviteRole'))    document.getElementById('inviteRole').value    = 'member';
}

/** Confirm invite with user's email address before sending */
function confirmInviteWithEmailAddress(inviteeEmail, role) {
    return new Promise((resolve) => {
        const userEmail = window.UserAuth?.user?.email || 'your email account';
        
        const overlay = document.createElement('div');
        overlay.className = 'inline-confirm-overlay';
        overlay.style.position = 'fixed';
        overlay.style.inset = '0';
        overlay.style.background = 'rgba(0,0,0,0.5)';
        overlay.style.display = 'flex';
        overlay.style.alignItems = 'center';
        overlay.style.justifyContent = 'center';
        overlay.style.zIndex = '9999';
        
        const dialog = document.createElement('div');
        dialog.style.background = 'var(--bg-primary)';
        dialog.style.color = 'var(--text-primary)';
        dialog.style.padding = '24px';
        dialog.style.borderRadius = '8px';
        dialog.style.maxWidth = '420px';
        dialog.style.boxShadow = '0 20px 60px rgba(0,0,0,0.3)';
        dialog.style.border = '1px solid var(--border-default)';
        
        dialog.innerHTML = `
            <div style="margin-bottom:20px;">
                <div style="font-size:18px;font-weight:700;margin-bottom:12px;color:var(--text-primary);">
                    <i class="fas fa-envelope" style="margin-right:8px;color:var(--accent-primary);"></i>
                    Confirm Invite
                </div>
                <div style="font-size:14px;color:var(--text-secondary);line-height:1.6;">
                    <div style="margin-bottom:12px;">
                        This invitation will be sent <strong>from:</strong><br>
                        <code style="display:block;padding:8px 10px;background:var(--bg-secondary);border-left:3px solid var(--accent-primary);margin-top:6px;border-radius:4px;font-size:13px;word-break:break-all;">${userEmail}</code>
                    </div>
                    <div style="margin-bottom:12px;">
                        <strong>To:</strong><br>
                        <code style="display:block;padding:8px 10px;background:var(--bg-secondary);border-left:3px solid var(--accent-success,#4caf50);margin-top:6px;border-radius:4px;font-size:13px;word-break:break-all;">${inviteeEmail}</code>
                    </div>
                    <div>
                        <strong>Role:</strong> ${role.charAt(0).toUpperCase() + role.slice(1)}
                    </div>
                </div>
            </div>
            <div style="display:flex;gap:10px;justify-content:flex-end;">
                <button id="confirm-cancel" style="padding:10px 18px;background:transparent;border:1px solid var(--border-color);color:var(--text-secondary);border-radius:6px;cursor:pointer;font-weight:500;">
                    Cancel
                </button>
                <button id="confirm-send" style="padding:10px 18px;background:var(--accent-primary);color:#fff;border:none;border-radius:6px;cursor:pointer;font-weight:600;">
                    <i class="fas fa-paper-plane" style="margin-right:6px;"></i>Send Invite
                </button>
            </div>
        `;
        
        overlay.appendChild(dialog);
        document.body.appendChild(overlay);
        
        document.getElementById('confirm-cancel').onclick = () => {
            overlay.remove();
            resolve(false);
        };
        
        document.getElementById('confirm-send').onclick = () => {
            overlay.remove();
            resolve(true);
        };
        
        // Close on ESC
        const handleEsc = (e) => {
            if (e.key === 'Escape') {
                overlay.remove();
                document.removeEventListener('keydown', handleEsc);
                resolve(false);
            }
        };
        document.addEventListener('keydown', handleEsc);
    });
}

async function inviteOrgMember() {
    const email    = document.getElementById('inviteEmail')?.value.trim();
    const role     = document.getElementById('inviteRole')?.value || 'member';
    const provider = document.getElementById('inviteProvider')?.value || '';
    const btn      = document.getElementById('sendInviteBtn');

    if (!email || !email.includes('@')) { _showOrgNotification('Please enter a valid email address.', 'error'); return; }

    // Show confirmation dialog with user's email
    const confirmed = await confirmInviteWithEmailAddress(email, role);
    if (!confirmed) { return; }

    if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...'; }

    try {
        const body = { email, role };
        if (provider) body.provider = provider;

        const res  = await fetch(`${API_BASE_URL}/api/org/invite`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}`
            },
            body: JSON.stringify(body),
        });
        const data = await res.json();
        if (!data.success) throw new Error(data.error || 'Invite failed');

        hideInviteMemberUI();

        if (data.email_sent) {
            _showOrgNotification(`✅ Invitation sent to ${email} — they will receive a join link via their email.`, 'success');
        } else if (data.email_error) {
            // Email failed — show error and provide manual link
            const escapedUrl = (data.accept_url || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            const copied     = await navigator.clipboard.writeText(data.accept_url).then(() => true).catch(() => false);
            const expires    = data.expires_at ? new Date(data.expires_at).toLocaleDateString() : 'in 7 days';
            
            let msg = `<strong>⚠️ Email delivery failed</strong><br>`;
            msg += `<span style="font-size:12px;color:#ff9800;margin-bottom:8px;display:block;">${data.email_error}</span>`;
            msg += `<span style="font-size:12px;opacity:.8;">Share this link with them instead:</span><br>` +
                `<code style="display:block;margin-top:6px;font-size:11px;word-break:break-all;padding:4px 6px;background:rgba(0,0,0,0.2);border-radius:4px;">${escapedUrl}</code>` +
                `<span style="display:block;margin-top:4px;font-size:11px;opacity:.7;">Expires: ${expires}${copied ? ' &mdash; copied' : ''}</span>`;
            
            _showOrgNotification(msg, 'warning');
        }

        loadOrgInvitations();
    } catch (err) {
        console.error('[ORG] inviteOrgMember error:', err);
        _showOrgNotification(`Failed to send invitation: ${err.message}`, 'error');
    } finally {
        if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Invite'; }
    }
}

/** Load and render pending invitations */
async function loadOrgInvitations() {
    const listEl   = document.getElementById('orgInvitationsList');
    const countEl  = document.getElementById('orgPendingCount');
    if (!listEl) return;

    listEl.innerHTML = '<div style="color:var(--text-muted);font-size:13px;"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';

    try {
        const res  = await fetch(`${API_BASE_URL}/api/org/invite/pending`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}` }
        });
        const data = await res.json();
        if (!data.success) throw new Error(data.error);

        const invites = data.invitations || [];
        const pending = invites.filter(i => i.status === 'pending');
        if (countEl) countEl.textContent = pending.length || '0';

        if (!invites.length) {
            listEl.innerHTML = '<div style="padding:24px 0;text-align:center;color:var(--text-muted);font-size:13px;">No invitations sent yet.</div>';
            return;
        }

        listEl.innerHTML = invites.map(inv => {
            const isPending  = inv.status === 'pending';
            const isExpired  = inv.expires_at && new Date(inv.expires_at) < new Date();
            const statusColor = isPending ? (isExpired ? '#ef4444' : '#f59e0b') :
                                inv.status === 'accepted' ? '#22c55e' : '#64748b';
            const statusText  = isExpired && isPending ? 'expired' : inv.status;
            const expiry      = inv.expires_at ? new Date(inv.expires_at).toLocaleDateString() : '—';

            return `
                <div style="display:flex;justify-content:space-between;align-items:center;padding:11px 0;border-bottom:1px solid var(--border-default);gap:10px;">
                    <div style="flex:1;min-width:0;">
                        <div style="font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${inv.invited_email}</div>
                        <div style="font-size:11px;color:var(--text-muted);margin-top:2px;">Role: ${inv.invited_role} &middot; Sent by ${inv.invited_by_username || 'admin'} &middot; Expires ${expiry}</div>
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;flex-shrink:0;">
                        <span style="font-size:11px;font-weight:700;padding:3px 8px;border-radius:4px;background:${statusColor}22;color:${statusColor};">${statusText}</span>
                        ${isPending && !isExpired ? `
                        <button onclick="revokeOrgInvite(${inv.id},'${inv.invited_email}')" class="btn btn-sm" style="padding:4px 8px;font-size:11px;background:transparent;border:1px solid var(--border-default);color:var(--text-muted);cursor:pointer;border-radius:4px;" title="Revoke invite">
                            <i class="fas fa-times"></i>
                        </button>` : ''}
                    </div>
                </div>`;
        }).join('');
    } catch (err) {
        console.error('[ORG] loadOrgInvitations error:', err);
        listEl.innerHTML = '<div style="padding:20px;color:var(--text-muted);">Failed to load invitations.</div>';
    }
}

function revokeOrgInvite(inviteId, email) {
    createInlineConfirm({
        title:        'Revoke Invitation?',
        message:      `Revoke the invitation for ${email}? The link will stop working immediately.`,
        confirmLabel: 'Revoke',
        cancelLabel:  'Cancel',
        onConfirm: async () => {
            try {
                const res  = await fetch(`${API_BASE_URL}/api/org/invite/${inviteId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}` }
                });
                const data = await res.json();
                if (!data.success) throw new Error(data.error);
                loadOrgInvitations();
                _showOrgNotification(`Invitation for ${email} revoked.`, 'success');
            } catch (err) {
                _showOrgNotification(`Failed to revoke: ${err.message}`, 'error');
            }
        }
    });
}
window.revokeOrgInvite = revokeOrgInvite;

// Expose org functions globally (called from inline HTML onclick handlers)
window.switchSettingsTab  = switchSettingsTab;
window.switchOrgSubTab    = switchOrgSubTab;
window.loadOrgTab         = loadOrgTab;
window.saveOrgSettings    = saveOrgSettings;
window.showCreateOrgForm  = showCreateOrgForm;
window.hideCreateOrgForm  = hideCreateOrgForm;
window.updateOrgSlugPreview = updateOrgSlugPreview;
// ==================== ACCEPT INVITE FLOW ====================

/**
 * Checks sessionStorage for a pending invite token (stored when user arrived
 * via an `?accept_invite=<token>` URL) and triggers the accept-invite modal.
 */
async function checkPendingInvite() {
    const pendingToken = sessionStorage.getItem('pendingInviteToken');
    if (!pendingToken) return;
    sessionStorage.removeItem('pendingInviteToken');
    await handleAcceptInvite(pendingToken);
}

/**
 * Validates the invite token with the backend, then shows an accept dialog.
 * Handles: email mismatch, already accepted, expired, and success cases.
 */
async function handleAcceptInvite(inviteToken) {
    let inviteInfo;
    try {
        const resp = await fetch(
            `${window.API_BASE_URL}/api/org/invite/accept?token=${encodeURIComponent(inviteToken)}`
        );
        inviteInfo = await resp.json();
    } catch (e) {
        console.error('[INVITE] Failed to fetch invite info:', e);
        return;
    }

    if (!inviteInfo.success) {
        _showInviteNotice('error', 'Invitation Invalid', inviteInfo.error || 'This invitation is no longer valid.');
        return;
    }

    const { org_name, invited_role } = inviteInfo;

    _showInviteAcceptDialog(org_name, invited_role, async (onDone) => {
        try {
            const authToken = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
            const acceptResp = await fetch(`${window.API_BASE_URL}/api/org/invite/accept`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({ token: inviteToken })
            });
            const result = await acceptResp.json();

            if (result.success) {
                onDone('success', `You have joined <strong>${org_name}</strong> as ${invited_role}.`);
                setTimeout(async () => {
                    try { await loadUserProfile(); } catch (e) { /* non-fatal */ }
                }, 1200);
            } else {
                onDone('error', result.error || 'Failed to accept invitation.');
            }
        } catch (e) {
            onDone('error', 'Network error. Please try again.');
        }
    });
}

/** Renders the accept-invite confirmation dialog. */
function _showInviteAcceptDialog(orgName, role, onAccept) {
    const overlay = document.createElement('div');
    overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.55);display:flex;align-items:center;justify-content:center;z-index:2147483647';

    const dialog = document.createElement('div');
    dialog.style.cssText = 'background:var(--bg-primary,#0b1220);color:var(--text-primary,#e6edf3);padding:24px;border-radius:12px;min-width:340px;max-width:480px;box-shadow:0 16px 48px rgba(0,0,0,0.7);border:1px solid var(--border-color,rgba(255,255,255,0.08))';
    dialog.innerHTML = `
        <div style="font-size:1.1rem;font-weight:700;margin-bottom:16px;">
            <i class="fas fa-envelope-open-text" style="color:#58a6ff;margin-right:8px;"></i>
            Organisation Invitation
        </div>
        <div style="margin-bottom:20px;line-height:1.5;color:var(--text-secondary,#8b949e)">
            You have been invited to join
            <strong style="color:var(--text-primary,#e6edf3)">${orgName}</strong>
            as <span style="background:var(--bg-tertiary,#161b22);padding:2px 8px;border-radius:4px;font-family:monospace;font-size:0.9em">${role}</span>.
        </div>
        <div id="_invite-dialog-status" style="display:none;margin-bottom:12px;padding:10px 12px;border-radius:6px;font-size:0.88rem"></div>
        <div style="display:flex;justify-content:flex-end;gap:10px">
            <button id="_invite-cancel-btn" class="btn btn-secondary" style="min-width:80px">Decline</button>
            <button id="_invite-accept-btn" class="btn btn-primary" style="min-width:80px">
                <i class="fas fa-check"></i> Accept
            </button>
        </div>
    `;

    overlay.appendChild(dialog);
    document.body.appendChild(overlay);

    const statusEl  = dialog.querySelector('#_invite-dialog-status');
    const acceptBtn = dialog.querySelector('#_invite-accept-btn');
    const cancelBtn = dialog.querySelector('#_invite-cancel-btn');
    const closeDialog = () => { try { overlay.remove(); } catch (e) {} };

    cancelBtn.addEventListener('click', closeDialog);
    acceptBtn.addEventListener('click', () => {
        acceptBtn.disabled = true;
        cancelBtn.disabled = true;
        acceptBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Joining...';

        onAccept((type, message) => {
            statusEl.style.display = 'block';
            if (type === 'success') {
                statusEl.style.cssText += ';background:rgba(63,185,80,0.1);color:#3fb950;border:1px solid rgba(63,185,80,0.3)';
                statusEl.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
                acceptBtn.innerHTML = '<i class="fas fa-check"></i> Done';
                cancelBtn.style.display = 'none';
                setTimeout(closeDialog, 2500);
            } else {
                statusEl.style.cssText += ';background:rgba(248,81,73,0.1);color:#f85149;border:1px solid rgba(248,81,73,0.3)';
                statusEl.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
                acceptBtn.disabled = false;
                cancelBtn.disabled = false;
                acceptBtn.innerHTML = '<i class="fas fa-check"></i> Accept';
            }
        });
    });
}

/** Simple info/error notice dialog (no accept action). */
function _showInviteNotice(type, title, message) {
    const overlay = document.createElement('div');
    overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.55);display:flex;align-items:center;justify-content:center;z-index:2147483647';

    const icon  = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
    const color = type === 'success' ? '#3fb950' : '#f85149';
    const dialog = document.createElement('div');
    dialog.style.cssText = 'background:var(--bg-primary,#0b1220);color:var(--text-primary,#e6edf3);padding:24px;border-radius:12px;min-width:320px;max-width:440px;box-shadow:0 16px 48px rgba(0,0,0,0.7);border:1px solid var(--border-color,rgba(255,255,255,0.08));text-align:center';
    dialog.innerHTML = `
        <div style="font-size:2rem;margin-bottom:12px;color:${color}"><i class="fas ${icon}"></i></div>
        <div style="font-weight:700;font-size:1.05rem;margin-bottom:8px">${title}</div>
        <div style="color:var(--text-secondary,#8b949e);margin-bottom:20px;line-height:1.4">${message}</div>
        <button class="btn btn-primary" id="_invite-notice-close">Close</button>
    `;
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);
    dialog.querySelector('#_invite-notice-close').addEventListener('click', () => {
        try { overlay.remove(); } catch (e) {}
    });
}

// ==================== EXPORTS ====================

window.createOrganisation = createOrganisation;
window.showInviteMemberUI = showInviteMemberUI;
window.hideInviteMemberUI = hideInviteMemberUI;
window.inviteOrgMember    = inviteOrgMember;
window.handleAcceptInvite = handleAcceptInvite;

// ✅ Export functions for external use
window.initializeAccountProfile = initializeApp;
window.initRightSidebar = initRightSidebar;
window.loadUserProfile = loadUserProfile; // ✅ FIX: Expose loadUserProfile globally for user_auth.js

// Log that module is loaded and awaiting initialization
console.log('✅ [account_profile.js] Account profile module loaded (awaiting initialization)');
