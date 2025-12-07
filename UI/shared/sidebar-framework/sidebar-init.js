/**
 * Sidebar Framework Initialization
 * 
 * PURPOSE: Register all module sidebars with the Universal Sidebar Framework
 * - Synergy Sessions (left side)
 * - Automations (right side)
 * - Account (right side)
 * - Debug (right side)
 * - Future modules...
 * 
 * LAST MODIFIED: 2025-11-28 - Fixed phantom "Settings" sidebar, added Account & Debug
 */

(function () {
    'use strict';

    console.log('[SIDEBAR INIT] Loading sidebar registrations...');

    /**
     * Initialize all sidebars when framework is ready
     */
    function initializeAllSidebars() {
        if (typeof SidebarManager === 'undefined') {
            console.error('[SIDEBAR INIT] SidebarManager not loaded!');
            return;
        }

        console.log('[SIDEBAR INIT] Registering sidebars...');

        // ==================== SYNERGY SESSIONS SIDEBAR ====================
        SidebarManager.register({
            id: 'synergy-sidebar',
            side: 'left',
            toggleButtonId: 'synergy-sidebar-toggle',
            width: '450px',
            icon: 'fa-hexagon-nodes-bolt',
            title: 'Synergy Sessions',
            zIndex: 9999,
            onInit: async () => {
                console.log('[SYNERGY] First open - initializing...');
                if (window.SynergySidebar && typeof SynergySidebar.init === 'function') {
                    await SynergySidebar.init();
                }
            },
            onOpen: () => {
                console.log('[SYNERGY] Sidebar opened');
            },
            onClose: () => {
                console.log('[SYNERGY] Sidebar closed');
            }
        });

        // ==================== AUTOMATIONS SIDEBAR ====================
        SidebarManager.register({
            id: 'automations-sidebar',
            side: 'right',
            toggleButtonId: 'automations-sidebar-toggle',
            width: '450px',
            icon: 'fa-robot',
            title: 'Automation Workflows',
            zIndex: 9999,
            onInit: async () => {
                console.log('[AUTOMATIONS] First open - loading workflows...');
                // Automation sidebar initialization (if needed)
                if (window.loadAutomations && typeof loadAutomations === 'function') {
                    await loadAutomations();
                }
            },
            onOpen: () => {
                console.log('[AUTOMATIONS] Sidebar opened');
                // Refresh automations list if needed
            },
            onClose: () => {
                console.log('[AUTOMATIONS] Sidebar closed');
            }
        });

        // ==================== ACCOUNT SIDEBAR ====================
        SidebarManager.register({
            id: 'account-sidebar',
            side: 'right',
            toggleButtonId: 'userProfileBtn-sidebar',
            width: '450px',
            icon: 'fa-user',
            title: 'Account Profile',
            zIndex: 10000,
            onInit: async () => {
                console.log('[ACCOUNT] First open - initializing...');
                if (window.AccountSidebar && typeof AccountSidebar.init === 'function') {
                    await AccountSidebar.init();
                }
            },
            onOpen: () => {
                console.log('[ACCOUNT] Sidebar opened');
            },
            onClose: () => {
                console.log('[ACCOUNT] Sidebar closed');
            }
        });

        // ==================== DEBUG SIDEBAR ====================
        SidebarManager.register({
            id: 'debug-sidebar',
            side: 'right',
            toggleButtonId: 'debug-toggle-btn',
            width: '600px',
            icon: 'fa-bug',
            title: 'Debug Console',
            zIndex: 9000, // Lower than production sidebars
            onInit: async () => {
                console.log('[DEBUG] First open - initializing...');
                if (window.DebugSidebar && typeof DebugSidebar.init === 'function') {
                    await DebugSidebar.init();
                }
            },
            onOpen: () => {
                console.log('[DEBUG] Sidebar opened');
            },
            onClose: () => {
                console.log('[DEBUG] Sidebar closed');
            }
        });

        // Note: Universal Search loads via ModuleLoader (hybrid module with dashboard + sidebar views)    // ==================== VECTOR DATABASE SIDEBAR ====================
        SidebarManager.register({
            id: 'vector-database',
            side: 'right',
            toggleButtonId: 'vector-database-toggle',
            width: '600px',
            icon: 'fa-database',
            title: 'Vector Database',
            zIndex: 9999,
            onInit: async () => {
                console.log('[VECTOR DATABASE] First open - loading HTML...');
                const container = document.getElementById('vector-database');
                console.log('[VECTOR DATABASE] Container element:', container);
                console.log('[VECTOR DATABASE] Container innerHTML length:', container ? container.innerHTML.length : 'N/A');
                
                if (container && !container.querySelector('#vector-db-sidebar')) {
                    try {
                        console.log('[VECTOR DATABASE] Fetching HTML from /modules_internal/vector_database/vector_database.html');
                        const response = await fetch('/modules_internal/vector_database/vector_database.html');
                        console.log('[VECTOR DATABASE] Fetch response status:', response.status, response.statusText);
                        
                        if (!response.ok) {
                            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                        }
                        
                        const html = await response.text();
                        console.log('[VECTOR DATABASE] Fetched HTML length:', html.length);
                        console.log('[VECTOR DATABASE] HTML preview:', html.substring(0, 200));
                        
                        container.innerHTML = html;
                        console.log('[VECTOR DATABASE] HTML inserted into container');

                        // Load CSS
                        if (!document.getElementById('vector-db-styles')) {
                            const link = document.createElement('link');
                            link.id = 'vector-db-styles';
                            link.rel = 'stylesheet';
                            link.href = '/modules_internal/vector_database/vector_database.css';
                            document.head.appendChild(link);
                        }

                        // Load and initialize JavaScript
                        if (!window.vectorDbSidebar) {
                            const script = document.createElement('script');
                            script.src = '/modules_internal/vector_database/vector_database.js';
                            document.body.appendChild(script);
                        }

                        console.log('[VECTOR DATABASE] HTML loaded successfully');
                    } catch (error) {
                        console.error('[VECTOR DATABASE] Failed to load HTML:', error);
                        container.innerHTML = '<div style="padding: 20px; color: #dc3545;">Failed to load Vector Database module</div>';
                    }
                }
            },
            onOpen: () => {
                console.log('[VECTOR DATABASE] Sidebar opened');
                if (window.vectorDbSidebar && typeof window.vectorDbSidebar.refresh === 'function') {
                    window.vectorDbSidebar.refresh();
                }
            },
            onClose: () => {
                console.log('[VECTOR DATABASE] Sidebar closed');
            }
        });

        console.log('[SIDEBAR INIT] All sidebars registered');
        console.log('ℹ️ [SIDEBAR INIT] Note: Communication Hub is a tab module, not a sidebar');
        console.log('[SIDEBAR INIT] Registered:', SidebarManager.getAll().map(s => s.id));
    }

    /**
     * Override existing toggle functions to use SidebarManager
     */
    function setupLegacyCompatibility() {
        // Synergy toggle compatibility
        const originalSynergyToggle = window.SynergySidebar?.toggleSidebar;
        if (window.SynergySidebar) {
            window.SynergySidebar.toggleSidebar = function () {
                if (SidebarManager.sidebars.has('synergy-sidebar')) {
                    SidebarManager.toggle('synergy-sidebar');
                } else if (originalSynergyToggle) {
                    originalSynergyToggle.call(window.SynergySidebar);
                }
            };
        }

        // Automations toggle compatibility
        const originalAutomationsToggle = window.toggleAutomationsSidebar;
        window.toggleAutomationsSidebar = function () {
            if (SidebarManager.sidebars.has('automations-sidebar')) {
                SidebarManager.toggle('automations-sidebar');
            } else if (originalAutomationsToggle) {
                originalAutomationsToggle();
            }
        };

        // Account toggle compatibility
        const originalAccountToggle = window.AccountSidebar?.toggleSidebar;
        if (window.AccountSidebar) {
            window.AccountSidebar.toggleSidebar = function () {
                if (SidebarManager.sidebars.has('account-sidebar')) {
                    SidebarManager.toggle('account-sidebar');
                } else if (originalAccountToggle) {
                    originalAccountToggle.call(window.AccountSidebar);
                }
            };
        }

        // toggleUserMenu compatibility wrapper
        const originalToggleUserMenu = window.toggleUserMenu;
        window.toggleUserMenu = function (event) {
            if (SidebarManager.sidebars.has('account-sidebar')) {
                if (event) event.preventDefault();
                SidebarManager.toggle('account-sidebar');
            } else if (originalToggleUserMenu) {
                originalToggleUserMenu(event);
            }
        };

        // Debug toggle compatibility
        const originalDebugToggle = window.DebugSidebar?.toggleSidebar;
        if (window.DebugSidebar) {
            window.DebugSidebar.toggleSidebar = function () {
                if (SidebarManager.sidebars.has('debug-sidebar')) {
                    SidebarManager.toggle('debug-sidebar');
                } else if (originalDebugToggle) {
                    originalDebugToggle.call(window.DebugSidebar);
                }
            };
        }

        console.log('[SIDEBAR INIT] Legacy compatibility layer installed');
    }

    // Wait for SidebarManager to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            // Give SidebarManager time to initialize
            setTimeout(() => {
                initializeAllSidebars();
                setupLegacyCompatibility();
            }, 100);
        });
    } else {
        setTimeout(() => {
            initializeAllSidebars();
            setupLegacyCompatibility();
        }, 100);
    }

    console.log('[SIDEBAR INIT] Module loaded');
})();
