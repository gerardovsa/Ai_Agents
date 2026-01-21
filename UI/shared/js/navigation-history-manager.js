/**
 * NAVIGATION HISTORY MANAGER
 * ===========================
 * Robust browser history management for the entire AI Agents platform
 * Enables back/forward navigation between platform sections without logging out
 * 
 * Features:
 * - Browser back/forward button support
 * - Deep linking to specific sections
 * - Preserves context (email IDs, thread IDs, subtabs)
 * - Prevents logout when navigating back
 * - URL-based state management
 * 
 * Created: January 21, 2026
 */

window.NavigationHistoryManager = (function() {
    'use strict';

    // Current state tracking
    let currentState = {
        tab: 'home',
        subtab: null,
        context: {}  // email_id, thread_id, session_id, etc.
    };

    // Flag to prevent infinite loops
    let isNavigating = false;

    /**
     * Initialize the navigation system
     * Sets up popstate listener and parses initial URL
     */
    function init() {
        console.log('[NavigationHistory] Initializing browser history management...');

        // Parse initial URL on page load
        const initialState = parseURL();
        if (initialState) {
            console.log('[NavigationHistory] Initial state from URL:', initialState);
            currentState = initialState;
            
            // Apply initial state after DOM loads
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => applyState(initialState, false));
            } else {
                applyState(initialState, false);
            }
        } else {
            // No URL state - use default home tab
            console.log('[NavigationHistory] No URL state - using default (home tab)');
            replaceState('home', null, {});
        }

        // Listen for browser back/forward button clicks
        window.addEventListener('popstate', handlePopState);

        // Intercept sidebar navigation clicks
        interceptNavigationClicks();

        console.log('✅ [NavigationHistory] Browser history management active');
    }

    /**
     * Parse current URL to extract navigation state
     * Format: /platform#tab=multi-agent&subtab=orders&email_id=123
     */
    function parseURL() {
        const hash = window.location.hash.substring(1); // Remove #
        if (!hash) return null;

        const params = new URLSearchParams(hash);
        const tab = params.get('tab');
        
        if (!tab) return null;

        const state = {
            tab: tab,
            subtab: params.get('subtab'),
            context: {}
        };

        // Extract context parameters (email_id, thread_id, etc.)
        for (const [key, value] of params.entries()) {
            if (key !== 'tab' && key !== 'subtab') {
                state.context[key] = value;
            }
        }

        return state;
    }

    /**
     * Build URL hash from state object
     */
    function buildURL(state) {
        const params = new URLSearchParams();
        params.set('tab', state.tab);
        
        if (state.subtab) {
            params.set('subtab', state.subtab);
        }

        // Add context parameters
        for (const [key, value] of Object.entries(state.context || {})) {
            if (value !== null && value !== undefined) {
                params.set(key, value);
            }
        }

        return `#${params.toString()}`;
    }

    /**
     * Handle browser back/forward button clicks
     */
    function handlePopState(event) {
        console.log('[NavigationHistory] 🔙 Back/Forward button clicked');
        
        if (isNavigating) {
            console.log('[NavigationHistory] Already navigating, ignoring popstate');
            return;
        }

        const state = event.state || parseURL();
        
        if (state) {
            console.log('[NavigationHistory] Navigating to:', state);
            applyState(state, false); // Don't push to history (already there)
        } else {
            console.log('[NavigationHistory] No state in popstate, staying on current tab');
        }
    }

    /**
     * Apply navigation state to UI
     * @param {Object} state - { tab, subtab, context }
     * @param {boolean} pushHistory - Whether to add to browser history
     */
    function applyState(state, pushHistory = true) {
        if (isNavigating) {
            console.log('[NavigationHistory] Navigation already in progress');
            return;
        }

        isNavigating = true;
        console.log(`[NavigationHistory] Applying state:`, state);

        try {
            // Update current state
            currentState = { ...state };

            // Update URL if requested
            if (pushHistory) {
                pushState(state.tab, state.subtab, state.context);
            }

            // Switch to main tab
            if (typeof switchTab === 'function') {
                switchTab(state.tab);
            } else {
                console.error('[NavigationHistory] switchTab function not found');
            }

            // Wait for tab to be visible, then handle subtabs and context
            setTimeout(() => {
                handleSubtab(state);
                handleContext(state);
            }, 100);

        } catch (error) {
            console.error('[NavigationHistory] Error applying state:', error);
        } finally {
            isNavigating = false;
        }
    }

    /**
     * Handle subtab navigation (e.g., WooCommerce Orders, Communication Hub filters)
     */
    function handleSubtab(state) {
        if (!state.subtab) return;

        console.log(`[NavigationHistory] Applying subtab: ${state.subtab}`);

        // Communication Hub subtabs (handled by module)
        if (state.tab === 'communication' && window.CommunicationHub) {
            // Let Communication Hub handle its own subtab state
            console.log('[NavigationHistory] Communication Hub will handle subtab internally');
        }

        // WooCommerce subtabs
        if (state.tab === 'sales' && state.subtab.startsWith('wc-')) {
            switchWooCommerceSubtab(state.subtab);
        }

        // Account sidebar subtabs
        if (state.tab === 'account' && window.AccountSidebar) {
            window.AccountSidebar.switchTab(state.subtab);
        }
    }

    /**
     * Handle context-specific navigation (open specific email, thread, etc.)
     */
    function handleContext(state) {
        const context = state.context || {};

        console.log('[NavigationHistory] Applying context:', context);

        // Open specific email in Communication Hub
        if (context.email_id && state.tab === 'communication') {
            setTimeout(() => {
                if (window.CommunicationHub && typeof window.CommunicationHub.openEmailPreview === 'function') {
                    console.log(`[NavigationHistory] Opening email: ${context.email_id}`);
                    window.CommunicationHub.openEmailPreview(context.email_id);
                }
            }, 300);
        }

        // Open specific thread in Command Center
        if (context.thread_id && state.tab === 'multi-agent') {
            setTimeout(() => {
                if (window.ThreadManager) {
                    console.log(`[NavigationHistory] Focusing thread: ${context.thread_id}`);
                    // ThreadManager can implement focusThread method
                }
            }, 300);
        }

        // Open specific Synergy session
        if (context.session_id && state.tab === 'synergy') {
            setTimeout(() => {
                if (window.synergyBoard) {
                    console.log(`[NavigationHistory] Opening session: ${context.session_id}`);
                    // Synergy can implement openSession method
                }
            }, 300);
        }
    }

    /**
     * Switch WooCommerce subtab
     */
    function switchWooCommerceSubtab(subtabId) {
        // Hide all WooCommerce subtabs
        document.querySelectorAll('.woocommerce-subtab-content').forEach(content => {
            content.style.display = 'none';
        });

        // Show target subtab
        const targetSubtab = document.getElementById(subtabId);
        if (targetSubtab) {
            targetSubtab.style.display = 'block';
            console.log(`[NavigationHistory] Switched to WooCommerce subtab: ${subtabId}`);
        }

        // Update subtab button active states
        document.querySelectorAll('.woocommerce-subtab').forEach(btn => {
            btn.classList.remove('active');
            if (btn.getAttribute('onclick')?.includes(subtabId)) {
                btn.classList.add('active');
            }
        });
    }

    /**
     * Push new state to browser history
     */
    function pushState(tab, subtab = null, context = {}) {
        const state = { tab, subtab, context };
        const url = buildURL(state);
        
        console.log(`[NavigationHistory] Pushing state: ${url}`);
        
        window.history.pushState(state, '', url);
        currentState = state;
    }

    /**
     * Replace current state without adding to history
     */
    function replaceState(tab, subtab = null, context = {}) {
        const state = { tab, subtab, context };
        const url = buildURL(state);
        
        console.log(`[NavigationHistory] Replacing state: ${url}`);
        
        window.history.replaceState(state, '', url);
        currentState = state;
    }

    /**
     * Intercept navigation clicks to add history support
     */
    function interceptNavigationClicks() {
        // Intercept sidebar tab clicks
        document.addEventListener('click', (event) => {
            const button = event.target.closest('.sidebar-icon-btn[data-tab]');
            if (button) {
                event.preventDefault();
                event.stopPropagation();
                
                const tab = button.getAttribute('data-tab');
                console.log(`[NavigationHistory] Sidebar click intercepted: ${tab}`);
                
                navigateTo(tab);
            }
        });

        // Intercept WooCommerce subtab clicks
        document.addEventListener('click', (event) => {
            const button = event.target.closest('.woocommerce-subtab');
            if (button && currentState.tab === 'sales') {
                const onclick = button.getAttribute('onclick');
                if (onclick) {
                    const match = onclick.match(/switchWooCommerceTab\('([^']+)'\)/);
                    if (match) {
                        event.preventDefault();
                        event.stopPropagation();
                        
                        const subtab = match[1];
                        console.log(`[NavigationHistory] WooCommerce subtab click intercepted: ${subtab}`);
                        
                        navigateTo('sales', subtab);
                    }
                }
            }
        });
    }

    /**
     * Public API: Navigate to a specific tab/subtab with context
     * @param {string} tab - Main tab ID
     * @param {string|null} subtab - Subtab ID (optional)
     * @param {Object} context - Context data (optional)
     */
    function navigateTo(tab, subtab = null, context = {}) {
        console.log(`[NavigationHistory] 🧭 Navigating to: ${tab}${subtab ? ` > ${subtab}` : ''}`, context);
        
        const state = { tab, subtab, context };
        applyState(state, true); // Push to history
    }

    /**
     * Public API: Get current navigation state
     */
    function getCurrentState() {
        return { ...currentState };
    }

    /**
     * Public API: Update context without changing tab
     * (e.g., user opens an email within Communication Hub)
     */
    function updateContext(newContext) {
        currentState.context = { ...currentState.context, ...newContext };
        replaceState(currentState.tab, currentState.subtab, currentState.context);
    }

    // Public API
    return {
        init,
        navigateTo,
        getCurrentState,
        updateContext,
        pushState,
        replaceState
    };
})();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => NavigationHistoryManager.init());
} else {
    NavigationHistoryManager.init();
}

console.log('✅ [NavigationHistory] Module loaded successfully');
