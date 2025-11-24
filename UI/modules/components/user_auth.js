// Use window.API_BASE_URL directly (declared in main HTML)
// No local declaration needed - access via window.API_BASE_URL

// ==================== USER AUTHENTICATION SYSTEM ====================

const UserAuth = {
    token: null,
    user: null,
    isInitialized: false, //  Prevent double initialization
    mainAppInitialized: false, //  Prevent double main app initialization

    async checkExistingSession() {
        // Check if user is already logged in
        const storedToken = localStorage.getItem('authToken');
        const storedUser = localStorage.getItem('userProfile');

        if (storedToken && storedUser) {
            this.token = storedToken;
            this.user = JSON.parse(storedUser);

            // Verify token is still valid
            const valid = await this.verifyToken();
            return valid;
        }
        return false;
    },

    init() {
        //  PREVENT DOUBLE INITIALIZATION
        if (this.isInitialized) {
            console.log(' [AUTH] Init already called, skipping duplicate initialization');
            return;
        }
        this.isInitialized = true;
        console.log(' [AUTH] Initializing UserAuth...');

        // Get loading overlay elements
        const loadingOverlay = document.getElementById('authLoadingOverlay');
        const loadingText = document.getElementById('authLoadingText');
        const progressFill = document.getElementById('authProgressFill');

        // Show loading overlay immediately
        loadingOverlay.style.display = 'flex';
        loadingOverlay.classList.remove('hidden');
        progressFill.classList.add('active');

        // Set initial progress
        this.setLoadingProgress(0, 'Checking authentication...');

        // FAILSAFE: Force hide overlay after 10 seconds no matter what
        setTimeout(() => {
            const overlay = document.getElementById('authLoadingOverlay');
            if (overlay && overlay.style.display !== 'none') {
                console.warn('⚠️ [AUTH] Failsafe: Force hiding auth overlay after 10s timeout');
                this.hideLoadingOverlay();
                const platformContainer = document.querySelector('.platform-container');
                if (platformContainer) {
                    platformContainer.style.opacity = '1';
                    platformContainer.classList.add('active');
                }
            }
        }, 10000);

        // Check if there's an OAuth callback token in the URL FIRST
        const urlParams = new URLSearchParams(window.location.search);
        const hasOAuthToken = urlParams.has('token');

        // DEVELOPMENT MODE: Auto-login for localhost testing (opt-in with ?dev=true)
        // Usage: http://localhost:5001/?dev=true to enable auto-login
        // Default: false (requires real OAuth)
        const devModeEnabled = urlParams.get('dev') === 'true';

        if (devModeEnabled && !hasOAuthToken && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
            const hasDevUser = localStorage.getItem('dev_mode_user');
            if (!hasDevUser) {
                console.log(' [DEV MODE] Dev mode enabled via ?dev=true - Auto-login as test user');
                this.setLoadingProgress(10, 'Loading dev environment...');
                // Create a mock token and user for local testing
                const mockUser = {
                    id: 1,
                    user_id: 1,
                    username: 'printing@inhouseprint.com.au',
                    email: 'printing@inhouseprint.com.au',
                    auth_platform: 'local_dev'
                };
                this.token = 'dev-mode-token-12345';
                this.user = mockUser;
                localStorage.setItem('authToken', this.token);
                localStorage.setItem('userProfile', JSON.stringify(mockUser));
                localStorage.setItem('dev_mode_user', 'true');
                console.log(' [DEV MODE] Auto-logged in as test user');
                // DON'T call showMainApp() here - let DOMContentLoaded flow handle it
                // This prevents double initialization
                return;
            }
        }

        // Check if user is already logged in
        const storedToken = localStorage.getItem('authToken');
        const storedUser = localStorage.getItem('userProfile');

        if (storedToken && storedUser) {
            console.log(' Token found, verifying...');
            this.setLoadingProgress(5, 'Verifying credentials...');

            this.token = storedToken;
            this.user = JSON.parse(storedUser);

            // Verify token is still valid
            this.verifyToken().then(valid => {
                if (valid) {
                    console.log(' Token valid, loading application...');
                    this.setLoadingProgress(10, 'Loading your workspace...');

                    // Small delay to show loading state
                    setTimeout(() => {
                        this.showMainApp();
                    }, 500);
                } else {
                    console.log(' Token invalid, showing login...');
                    this.hideLoadingOverlay();
                    this.showLogin();
                }
            }).catch(error => {
                console.error(' Token verification error:', error);
                this.hideLoadingOverlay();
                this.showLogin();
            });
        } else {
            console.log(' No token found, showing login...');
            this.hideLoadingOverlay();
            this.showLogin();
        }
    },

    async verifyToken() {
        try {
            const response = await fetch(`${window.API_BASE_URL || API_BASE_URL}/api/auth/verify`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            return response.ok;
        } catch (error) {
            console.error('Token verification failed:', error);
            return false;
        }
    },

    async login(username, password) {
        const loginBtn = document.getElementById('loginBtn');
        const errorDiv = document.getElementById('loginError');
        const loadingOverlay = document.getElementById('authLoadingOverlay');
        const loadingText = document.getElementById('authLoadingText');
        const progressFill = document.getElementById('authProgressFill');

        // Disable button, show loading in button
        loginBtn.disabled = true;
        loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing in...';
        errorDiv.classList.remove('show');

        try {
            const response = await fetch(`${window.API_BASE_URL || API_BASE_URL}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (data.success) {
                this.token = data.token;
                this.user = data.user;

                // Store in localStorage
                localStorage.setItem('authToken', this.token);
                localStorage.setItem('userProfile', JSON.stringify(this.user));

                console.log(' Login successful!');

                // Hide login overlay immediately
                document.getElementById('loginOverlay').style.display = 'none';

                // Show loading overlay with progress
                loadingOverlay.style.display = 'flex';
                loadingOverlay.classList.remove('hidden');
                progressFill.classList.add('active');
                this.setLoadingProgress(10, 'Loading your workspace...');

                // Load app with delay to show progress
                setTimeout(() => {
                    this.showMainApp();
                }, 500);

                return { success: true };
            } else {
                throw new Error(data.error || 'Login failed');
            }
        } catch (error) {
            console.error(' Login error:', error);
            errorDiv.textContent = error.message || 'Login failed. Please try again.';
            errorDiv.classList.add('show');
            loginBtn.disabled = false;
            loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Sign In';
            return { success: false, error: error.message };
        }
    },

    logout() {
        this.token = null;
        this.user = null;
        this.isInitialized = false; // Reset init flag for re-login
        this.mainAppInitialized = false; // Reset main app flag for re-login
        localStorage.removeItem('authToken');
        localStorage.removeItem('userProfile');
        localStorage.removeItem('dev_mode_user'); // Clear dev mode flag
        this.showLogin();
    },

    hideLoadingOverlay() {
        const loadingOverlay = document.getElementById('authLoadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.classList.add('hidden');
            // Force hide with important styles as failsafe
            loadingOverlay.style.opacity = '0';
            loadingOverlay.style.pointerEvents = 'none';
            setTimeout(() => {
                loadingOverlay.style.display = 'none';
            }, 300);
        }
    },

    showLogin() {
        const loginOverlay = document.getElementById('loginOverlay');
        const platformContainer = document.querySelector('.platform-container');

        // Reset display states
        loginOverlay.style.display = 'flex';
        loginOverlay.classList.remove('hidden');
        platformContainer.classList.remove('active');
        platformContainer.style.opacity = '0';

        console.log(' [AUTH] Login screen displayed');
    },

    /**
     * Update loading progress bar
     * @param {number} percent - Progress percentage (0-100)
     * @param {string} text - Loading text to display
     */
    setLoadingProgress(percent, text) {
        const progressFill = document.getElementById('authProgressFill');
        const loadingText = document.getElementById('authLoadingText');

        if (progressFill) {
            progressFill.style.width = `${Math.min(100, Math.max(0, percent))}%`;
        }
        if (loadingText && text) {
            loadingText.textContent = text;
        }

        console.log(` [LOADING] ${percent}% - ${text}`);
    },

    async showMainApp() {
        //  PREVENT DOUBLE INITIALIZATION OF MAIN APP
        if (this.mainAppInitialized) {
            console.log(' [AUTH] Main app already initialized - BLOCKING duplicate call');

            // ❌ REMOVED (Nov 24, 2025): This retry logic was causing duplicate module initialization
            // The "page refresh" scenario this was meant to handle doesn't exist because:
            //   1. On page refresh, mainAppInitialized flag resets to false (not persisted)
            //   2. Normal flow (checkExistingSession → showMainApp) handles initialization correctly
            //   3. This retry was triggered by INCORRECT double calls (from initializeAccountProfile)
            //
            // REMOVED CODE:
            // if (window.initializeModuleSystem) {
            //     console.log('🔷 [AUTH] Triggering module system initialization (retry)...');
            //     await window.initializeModuleSystem();
            // }

            return; // ← EARLY EXIT - no retry logic
        }

        // ✅ FIX (Nov 24, 2025): MOVED flag setting to AFTER successful initialization
        // Previously: Flag was set HERE (before initialization)
        // Problem: If initialization failed, flag stayed true, preventing retries
        // Solution: Set flag only after all initialization steps succeed

        console.log(' Login successful - Initializing main application...');

        // Get loading overlay elements
        const loadingText = document.getElementById('authLoadingText');
        const loginOverlay = document.getElementById('loginOverlay');
        const platformContainer = document.querySelector('.platform-container');

        // Start progress tracking
        this.setLoadingProgress(5, 'Initializing application...');

        // Hide login overlay
        loginOverlay.style.display = 'none';
        loginOverlay.classList.add('hidden');

        // Prepare platform container
        platformContainer.classList.add('active');
        platformContainer.style.opacity = '0';

        // ✅ CRITICAL FIX (Nov 24, 2025): Wait for DOM to render AND become visible
        // Multiple animation frames to ensure layout is complete
        console.log('[AUTH] Waiting for DOM to be fully rendered...');
        await new Promise(resolve => requestAnimationFrame(() =>
            requestAnimationFrame(() =>
                requestAnimationFrame(resolve)
            )
        ));

        // Verify platform container is actually active
        if (platformContainer.classList.contains('active')) {
            console.log('✅ [AUTH] Platform container is active and in layout');
        } else {
            console.error('❌ [AUTH] Platform container is NOT active!');
        }

        try {
            // PHASE 1: Initialize main app with existing libraries (15% progress)
            this.setLoadingProgress(15, 'Initializing application...');

            console.log('🔵 [AUTH] Starting initializeMainApp()...');
            await window.initializeMainApp();
            console.log('✅ [AUTH] initializeMainApp() complete');
            this.setLoadingProgress(20, 'Application initialized');

            // ✅ CRITICAL FIX: Initialize module system AFTER main app is visible
            this.setLoadingProgress(22, 'Loading modules...');
            if (window.initializeModuleSystem) {
                console.log('🔷 [AUTH] Triggering module system initialization...');
                try {
                    await window.initializeModuleSystem();
                    console.log('✅ [AUTH] Module system initialization complete');

                    // Verify modules loaded
                    if (window.ModuleManager && window.ModuleManager.getModules) {
                        const modules = window.ModuleManager.getModules();
                        console.log(`📦 [AUTH] ${modules.length} modules loaded`);
                        const kanban = modules.find(m => m.id === 'inhouse-kanban');
                        if (kanban) {
                            console.log('✅ [AUTH] InHouse Kanban module registered');
                        } else {
                            console.warn('⚠️ [AUTH] InHouse Kanban module NOT found');
                        }
                    }
                } catch (error) {
                    console.error('❌ [AUTH] Module system initialization ERROR:', error);
                    // Don't fail the entire flow if modules don't load
                }
            } else {
                console.warn('⚠️ [AUTH] initializeModuleSystem not found - modules may not load');
            }
            this.setLoadingProgress(25, 'Modules loaded');

            // PHASE 2: Load heavy libraries AFTER app is visible (25-75% progress)
            this.setLoadingProgress(30, 'Loading additional resources...');
            console.log(' [POST-AUTH] Loading heavy libraries...');
            try {
                await this.loadPostAuthLibraries();
                console.log('✅ [AUTH] Post-auth libraries loaded');
            } catch (error) {
                console.error('❌ [AUTH] Post-auth libraries ERROR:', error);
                // Don't fail the entire flow if libraries don't load
            }
            this.setLoadingProgress(75, 'Resources loaded');

            // PHASE 3: Load user profile (75-90% progress)
            this.setLoadingProgress(80, 'Loading your profile...');
            console.log('🔵 [AUTH] Loading user profile...');
            try {
                await loadUserProfile();
                console.log('✅ [AUTH] User profile loaded');
            } catch (error) {
                console.error('❌ [AUTH] User profile ERROR:', error);
                // Don't fail the entire flow if profile doesn't load - we already have basic user data
            }
            this.setLoadingProgress(90, 'Profile loaded');

            if (this.user) {
                console.log(' Logged in as:', this.user.username);
                console.log(' Gmail accounts:', this.user.gmail_accounts.length || 0);
            }

            // PHASE 4: Final setup (90-100% progress)
            this.setLoadingProgress(95, 'Almost ready...');

            // Fade in main app
            requestAnimationFrame(() => {
                platformContainer.style.transition = 'opacity 0.4s ease-in';
                platformContainer.style.opacity = '1';
            });

            // Complete progress and hide overlay
            this.setLoadingProgress(100, 'Ready!');

            // ✅ FIX (Nov 24, 2025): Set initialization flag AFTER successful completion
            // This ensures the flag is only set if all initialization steps succeeded
            this.mainAppInitialized = true;
            console.log('✅ [AUTH] Main app initialization COMPLETE - Flag set to true');

            setTimeout(() => {
                this.hideLoadingOverlay();
            }, 10000); // 10 second delay before hiding auth loading overlay

        } catch (error) {
            console.error('❌ [AUTH] Failed to initialize main app:', error);
            console.error('❌ [AUTH] Error stack:', error.stack);

            // ✅ FIX (Nov 24, 2025): Reset flag on error to allow retries
            this.mainAppInitialized = false;

            this.setLoadingProgress(0, 'Error loading application');

            // ✅ FIX (Nov 24, 2025): Show login screen on initialization failure
            // Previously: Tried to show main app even on error (broken state)
            // Now: Return to login screen so user can retry
            setTimeout(() => {
                this.hideLoadingOverlay();
                this.showLogin(); // Show login screen to allow retry
                console.log('🔄 [AUTH] Returned to login screen - User can retry');
            }, 2000); // Show error message for 2 seconds before returning to login
        }
    },

    getAuthHeaders() {
        return {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };
    },

    /**
     * Load heavy non-critical libraries AFTER authentication
     * This improves initial page load time significantly (saves ~5MB)
     */
    async loadPostAuthLibraries() {
        console.log(' [POST-AUTH] Loading heavy libraries sequentially...');
        const startTime = performance.now();

        try {
            //  SKIPPING TIPTAP: UMD builds don't expose proper globals, causing initialization errors
            // TipTap rich text editor will be added later using ES modules instead of UMD
            console.log('   Skipping TipTap libraries (not currently used in UI)');

            // STEP 4: Skip Yjs Collaboration (not implemented yet, causing 404 errors)
            // Real-time collaboration will be added in future version
            console.log('    Skipping Yjs collaboration libraries (not needed yet)');

            // STEP 5: Handsontable (1.8MB - can load in parallel with others)
            this.setLoadingProgress(40, 'Loading spreadsheet libraries...');
            await Promise.all([
                this.loadScript('handsontable', 'https://cdn.jsdelivr.net/npm/handsontable/dist/handsontable.full.min.js'),
                this.loadScript('hyperformula', 'https://cdn.jsdelivr.net/npm/hyperformula/dist/hyperformula.full.min.js'),
                this.loadScript('jspdf', 'https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js'),
                this.loadScript('html2canvas', 'https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js')
            ]);
            this.setLoadingProgress(70, 'Libraries loaded');
            console.log('   Handsontable & PDF libraries loaded');

            const endTime = performance.now();
            console.log(` [POST-AUTH] All heavy libraries loaded in ${((endTime - startTime) / 1000).toFixed(2)}s`);

            // Notify modules that libraries are ready
            window.dispatchEvent(new CustomEvent('postAuthLibrariesLoaded'));

        } catch (error) {
            console.error(' [POST-AUTH] Failed to load libraries:', error);
        }
    },

    /**
     * Load a script dynamically
     * @param {string} id - Unique ID for the script element
     * @param {string} src - URL of the script to load
     * @returns {Promise} Resolves when script loads, rejects on error
     */
    loadScript(id, src) {
        return new Promise((resolve, reject) => {
            // Check if already loaded
            if (document.getElementById(id)) {
                console.log(`    ${id} already loaded`);
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.id = id;
            script.src = src;
            script.onload = () => resolve();
            script.onerror = () => reject(new Error(`Failed to load ${src}`));
            document.head.appendChild(script);
        });
    },

    /**
     * Wait for a global variable to be available
     * @param {string} globalPath - Path to global variable (e.g., 'window.tiptapCore')
     * @param {number} timeout - Max wait time in ms (default: 2000)
     * @returns {Promise} Resolves when global is available
     */
    waitForGlobal(globalPath, timeout = 2000) {
        return new Promise((resolve, reject) => {
            const startTime = Date.now();

            const checkGlobal = () => {
                try {
                    // Evaluate the global path
                    if (eval(globalPath)) {
                        resolve();
                        return;
                    }
                } catch (e) {
                    // Path doesn't exist yet
                }

                // Check timeout
                if (Date.now() - startTime > timeout) {
                    console.warn(` Timeout waiting for ${globalPath}`);
                    resolve(); // Don't reject, just continue
                    return;
                }

                // Check again in 50ms
                setTimeout(checkGlobal, 50);
            };

            checkGlobal();
        });
    }
};

//  CRITICAL: Make UserAuth globally accessible for ThreadManager and other modules
window.UserAuth = UserAuth;
console.log('✅ [UserAuth] Module loaded and exposed globally');
