/**
 * FILE: UI/external/modules/settings-sidebar/settings-button-integration.js
 * PURPOSE: Settings button integration with enhanced error handling and tracing
 * 
 * This file handles the settings button in the main UI header and provides
 * comprehensive error tracking for debugging module loading issues.
 * 
 * LAST MODIFIED: 2025-11-23 - Created for enhanced debugging
 */

console.log('%c[Settings Button] Module integration script loading...', 'color: #8b5cf6; font-weight: bold;');

(function() {
    'use strict';

    // Enhanced logging utility
    const SettingsLogger = {
        prefix: '[Settings Button]',
        
        log(message, data = null) {
            console.log(`%c${this.prefix} ${message}`, 'color: #8b5cf6;', data || '');
        },
        
        success(message, data = null) {
            console.log(`%c${this.prefix} ✅ ${message}`, 'color: #0f0; font-weight: bold;', data || '');
        },
        
        error(message, error = null) {
            console.error(`%c${this.prefix} ❌ ${message}`, 'color: #f00; font-weight: bold;', error || '');
            if (error && error.stack) {
                console.error('Stack trace:', error.stack);
            }
        },
        
        warn(message, data = null) {
            console.warn(`%c${this.prefix} ⚠️ ${message}`, 'color: #ff0;', data || '');
        },
        
        info(message, data = null) {
            console.info(`%c${this.prefix} ℹ️ ${message}`, 'color: #58a6ff;', data || '');
        },
        
        group(title) {
            console.group(`%c${this.prefix} ${title}`, 'color: #8b5cf6; font-weight: bold;');
        },
        
        groupEnd() {
            console.groupEnd();
        }
    };

    // Settings Button Manager
    const SettingsButtonManager = {
        buttonSelector: '[data-module-action="settings"], #settings-button, .settings-icon-btn',
        button: null,
        module: null,
        initialized: false,

        /**
         * Initialize the settings button integration
         */
        init() {
            SettingsLogger.group('Initializing Settings Button Integration');
            
            try {
                // Find settings button
                this.findSettingsButton();
                
                // Check module availability
                this.checkModuleAvailability();
                
                // Setup event listeners
                this.setupEventListeners();
                
                // Output CSS for debugging
                this.outputCSSToConsole();
                
                this.initialized = true;
                SettingsLogger.success('Settings button integration initialized');
                
            } catch (error) {
                SettingsLogger.error('Failed to initialize settings button', error);
            } finally {
                SettingsLogger.groupEnd();
            }
        },

        /**
         * Find the settings button in the DOM
         */
        findSettingsButton() {
            SettingsLogger.info('Searching for settings button...');
            
            // Try multiple selectors
            const selectors = [
                '[data-module-action="settings"]',
                '#settings-button',
                '.settings-icon-btn',
                'button[title*="Settings"]',
                'button[aria-label*="Settings"]'
            ];

            for (const selector of selectors) {
                this.button = document.querySelector(selector);
                if (this.button) {
                    SettingsLogger.success(`Found settings button: ${selector}`, this.button);
                    break;
                }
            }

            if (!this.button) {
                SettingsLogger.warn('Settings button not found. Creating fallback button...');
                this.createFallbackButton();
            }
        },

        /**
         * Create fallback settings button if not found
         */
        createFallbackButton() {
            try {
                const button = document.createElement('button');
                button.id = 'settings-button-fallback';
                button.className = 'settings-icon-btn';
                button.setAttribute('data-module-action', 'settings');
                button.setAttribute('title', 'Settings');
                button.innerHTML = '<i class="fas fa-cog"></i>';
                
                // Style the button
                button.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    width: 50px;
                    height: 50px;
                    background: #8b5cf6;
                    border: 2px solid #7c3aed;
                    border-radius: 50%;
                    color: white;
                    font-size: 20px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 10000;
                    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
                    transition: all 0.3s ease;
                `;
                
                document.body.appendChild(button);
                this.button = button;
                
                SettingsLogger.success('Fallback settings button created', button);
            } catch (error) {
                SettingsLogger.error('Failed to create fallback button', error);
            }
        },

        /**
         * Check if Settings Sidebar module is available
         */
        checkModuleAvailability() {
            SettingsLogger.group('Checking Module Availability');
            
            try {
                // Check class
                if (typeof SettingsSidebarModule !== 'undefined') {
                    SettingsLogger.success('SettingsSidebarModule class found');
                } else {
                    SettingsLogger.error('SettingsSidebarModule class NOT found');
                }

                // Check ModuleRegistry
                if (window.ModuleRegistry) {
                    SettingsLogger.success('ModuleRegistry exists');
                    
                    if (window.ModuleRegistry['settings-sidebar']) {
                        SettingsLogger.success('Module registered in ModuleRegistry');
                    } else {
                        SettingsLogger.warn('Module NOT registered in ModuleRegistry');
                    }
                } else {
                    SettingsLogger.warn('ModuleRegistry not found');
                }

                // Check global instance
                if (window.settingsModule) {
                    SettingsLogger.success('window.settingsModule instance exists');
                    this.module = window.settingsModule;
                } else {
                    SettingsLogger.warn('window.settingsModule instance NOT found');
                    SettingsLogger.info('Attempting to create instance...');
                    
                    if (typeof SettingsSidebarModule !== 'undefined') {
                        this.module = new SettingsSidebarModule('settings-sidebar');
                        window.settingsModule = this.module;
                        SettingsLogger.success('Created window.settingsModule instance');
                    }
                }

                // Check module initialization
                if (this.module) {
                    if (this.module.initialized) {
                        SettingsLogger.success('Module is initialized');
                    } else {
                        SettingsLogger.info('Module not initialized. Initializing now...');
                        this.module.initialize().then(() => {
                            SettingsLogger.success('Module initialized successfully');
                        }).catch(error => {
                            SettingsLogger.error('Module initialization failed', error);
                        });
                    }
                }

                // Check module container
                const container = document.getElementById('tab-settings-sidebar');
                if (container) {
                    SettingsLogger.success('Module container found', container);
                } else {
                    SettingsLogger.warn('Module container NOT found (expected #tab-settings-sidebar)');
                }

            } catch (error) {
                SettingsLogger.error('Error checking module availability', error);
            } finally {
                SettingsLogger.groupEnd();
            }
        },

        /**
         * Setup event listeners
         */
        setupEventListeners() {
            if (!this.button) {
                SettingsLogger.error('Cannot setup event listeners: button not found');
                return;
            }

            SettingsLogger.info('Setting up event listeners...');

            // Click handler
            this.button.addEventListener('click', (event) => {
                event.preventDefault();
                event.stopPropagation();
                this.handleButtonClick();
            });

            // Hover effects
            this.button.addEventListener('mouseenter', () => {
                SettingsLogger.log('Button hover: enter');
                this.button.style.transform = 'scale(1.1)';
            });

            this.button.addEventListener('mouseleave', () => {
                SettingsLogger.log('Button hover: leave');
                this.button.style.transform = 'scale(1)';
            });

            SettingsLogger.success('Event listeners attached to settings button');
        },

        /**
         * Handle button click
         */
        handleButtonClick() {
            SettingsLogger.group('Settings Button Clicked');
            
            try {
                SettingsLogger.info('Button click event triggered');

                // Check if module is available
                if (!this.module) {
                    SettingsLogger.error('Module instance not available');
                    this.showErrorMessage('Settings module not loaded. Please refresh the page.');
                    return;
                }

                // Try ModuleManager first
                if (window.ModuleManager && typeof window.ModuleManager.switchToModule === 'function') {
                    SettingsLogger.info('Using ModuleManager.switchToModule()');
                    window.ModuleManager.switchToModule('settings-sidebar');
                    SettingsLogger.success('Module switched via ModuleManager');
                } 
                // Try module's switchSubTab method
                else if (typeof this.module.switchSubTab === 'function') {
                    SettingsLogger.info('Using module.switchSubTab()');
                    this.module.switchSubTab('recovery');
                    SettingsLogger.success('Switched to recovery tab');
                    
                    // Show module container if hidden
                    this.showModuleContainer();
                }
                // Fallback: toggle container visibility
                else {
                    SettingsLogger.warn('Using fallback: toggling container');
                    this.showModuleContainer();
                }

            } catch (error) {
                SettingsLogger.error('Error handling button click', error);
                this.showErrorMessage(`Failed to open settings: ${error.message}`);
            } finally {
                SettingsLogger.groupEnd();
            }
        },

        /**
         * Show module container
         */
        showModuleContainer() {
            const container = document.getElementById('tab-settings-sidebar');
            
            if (!container) {
                SettingsLogger.error('Module container not found');
                return;
            }

            // Toggle visibility
            if (container.style.display === 'none' || !container.style.display) {
                container.style.display = 'block';
                SettingsLogger.success('Module container shown');
            } else {
                container.style.display = 'none';
                SettingsLogger.info('Module container hidden');
            }
        },

        /**
         * Show error message to user
         */
        showErrorMessage(message) {
            alert(message);
            SettingsLogger.error(message);
        },

        /**
         * Output CSS to console for easy copying
         */
        outputCSSToConsole() {
            SettingsLogger.info('Preparing to output CSS...');
            
            setTimeout(() => {
                fetch('UI/external/modules/settings-sidebar/settings-sidebar.css')
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                        }
                        return response.text();
                    })
                    .then(css => {
                        console.log('\n\n');
                        console.log('%c═══════════════════════════════════════════════════', 'color: #8b5cf6; font-size: 14px; font-weight: bold;');
                        console.log('%c    Settings Sidebar Module - CSS Code    ', 'color: #8b5cf6; font-size: 16px; font-weight: bold;');
                        console.log('%c═══════════════════════════════════════════════════', 'color: #8b5cf6; font-size: 14px; font-weight: bold;');
                        console.log('%c\nℹ️  Copy the CSS below and paste into your stylesheet:', 'color: #58a6ff; font-size: 13px;');
                        console.log('%c\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #30363d;');
                        console.log(css);
                        console.log('%c\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #30363d;');
                        console.log('%c\n✅ CSS loaded successfully - Total: ' + css.length + ' characters', 'color: #0f0; font-weight: bold;');
                        console.log('%c\n═══════════════════════════════════════════════════\n\n', 'color: #8b5cf6; font-size: 14px; font-weight: bold;');
                        
                        SettingsLogger.success('CSS output to console successfully');
                    })
                    .catch(error => {
                        SettingsLogger.error('Failed to load CSS', error);
                        console.error('\n\n%c❌ Failed to load CSS:', 'color: #f00; font-size: 14px; font-weight: bold;', error.message);
                    });
            }, 2000);
        },

        /**
         * Get current module state for debugging
         */
        getModuleState() {
            return {
                buttonFound: !!this.button,
                buttonElement: this.button,
                moduleInstance: !!this.module,
                moduleInitialized: this.module ? this.module.initialized : false,
                containerExists: !!document.getElementById('tab-settings-sidebar'),
                registryExists: !!window.ModuleRegistry,
                moduleRegistered: window.ModuleRegistry ? !!window.ModuleRegistry['settings-sidebar'] : false,
                globalInstanceExists: !!window.settingsModule,
                managerExists: !!window.ModuleManager
            };
        },

        /**
         * Output debug info to console
         */
        debugInfo() {
            console.log('\n\n');
            console.log('%c═══════════════════════════════════════════════════', 'color: #8b5cf6; font-size: 14px; font-weight: bold;');
            console.log('%c    Settings Sidebar - Debug Information    ', 'color: #8b5cf6; font-size: 16px; font-weight: bold;');
            console.log('%c═══════════════════════════════════════════════════', 'color: #8b5cf6; font-size: 14px; font-weight: bold;');
            
            const state = this.getModuleState();
            
            console.table(state);
            
            console.log('\n%cModule Instance:', 'color: #58a6ff; font-weight: bold;');
            console.log(this.module);
            
            console.log('\n%cButton Element:', 'color: #58a6ff; font-weight: bold;');
            console.log(this.button);
            
            console.log('\n%cModule Container:', 'color: #58a6ff; font-weight: bold;');
            console.log(document.getElementById('tab-settings-sidebar'));
            
            console.log('\n%c═══════════════════════════════════════════════════\n\n', 'color: #8b5cf6; font-size: 14px; font-weight: bold;');
        }
    };

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            SettingsLogger.info('DOM loaded, initializing...');
            SettingsButtonManager.init();
        });
    } else {
        SettingsLogger.info('DOM already loaded, initializing immediately...');
        SettingsButtonManager.init();
    }

    // Expose for debugging
    window.SettingsButtonManager = SettingsButtonManager;
    window.SettingsLogger = SettingsLogger;

    // Auto-output debug info after 3 seconds
    setTimeout(() => {
        SettingsButtonManager.debugInfo();
    }, 3000);

    SettingsLogger.success('Settings button integration script loaded');

})();
