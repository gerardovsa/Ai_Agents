/**
 * ========================================
 * Dev Tools Auto-Plugin Loader
 * ========================================
 * Registers dev-tools module with ModuleRegistry for automatic dashboard integration
 * This enables the dev-tools to be auto-loaded when the dashboard initializes
 */

(function () {
    'use strict';

    console.log('[DevToolsPlugin] 🔌 Loading dev-tools auto-plugin...');

    /**
     * Wait for ModuleRegistry to be available
     * @returns {Promise<void>}
     */
    const waitForRegistry = () => {
        return new Promise((resolve) => {
            if (window.ModuleRegistry) {
                resolve();
                return;
            }

            const checkInterval = setInterval(() => {
                if (window.ModuleRegistry) {
                    clearInterval(checkInterval);
                    resolve();
                }
            }, 100);

            // Timeout after 10 seconds
            setTimeout(() => {
                clearInterval(checkInterval);
                console.error('[DevToolsPlugin] ❌ ModuleRegistry not found after 10s');
                resolve(); // Resolve anyway to prevent hanging
            }, 10000);
        });
    };

    /**
     * Initialize dev-tools module
     * @param {HTMLElement|string} container - Container element or selector
     * @returns {Promise<Object>} Dev Tools instance
     */
    const initDevTools = async (container) => {
        console.log('[DevToolsPlugin] 🚀 Initializing dev-tools module...');

        try {
            // Get DevToolsModule singleton
            if (typeof DevToolsModule === 'undefined') {
                throw new Error('DevToolsModule not loaded. Include dev-tools-module.js before this plugin.');
            }

            const devTools = DevToolsModule.getInstance({
                apiBase: window.location.origin,
                monacoPath: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs',
                enableWebSocket: true,
                enableAutoSave: true,
                autoSaveInterval: 30000,
                enableCredentialTesting: true,
                theme: 'vs-dark',
                enableLivePreview: true,
                previewUpdateDelay: 1000
            });

            // Initialize workspace in container
            await devTools.initialize(container);

            console.log('[DevToolsPlugin] ✅ Dev-tools module initialized successfully');
            return devTools;

        } catch (error) {
            console.error('[DevToolsPlugin] ❌ Failed to initialize dev-tools:', error);
            throw error;
        }
    };

    /**
     * Destroy dev-tools module instance
     * @returns {Promise<void>}
     */
    const destroyDevTools = async () => {
        console.log('[DevToolsPlugin] 🔄 Destroying dev-tools module...');

        try {
            if (typeof DevToolsModule !== 'undefined') {
                const devTools = DevToolsModule.getInstance();
                if (devTools && typeof devTools.destroy === 'function') {
                    devTools.destroy();
                }
            }
            console.log('[DevToolsPlugin] ✅ Dev-tools module destroyed');
        } catch (error) {
            console.error('[DevToolsPlugin] ❌ Failed to destroy dev-tools:', error);
        }
    };

    /**
     * Register module with ModuleRegistry
     */
    const registerModule = async () => {
        await waitForRegistry();

        if (!window.ModuleRegistry) {
            console.error('[DevToolsPlugin] ❌ ModuleRegistry not available');
            return;
        }

        try {
            window.ModuleRegistry.register({
                // Module identification
                id: 'dev-tools',
                name: 'Module Creator',
                version: '3.0.0',
                description: 'Visual module creator with Monaco Editor integration',

                // Module metadata
                icon: 'fa-tools',
                type: 'utility', // utility = background service, not shown in UI by default
                category: 'development',

                // Module capabilities
                capabilities: {
                    dashboard: true,        // Can be shown in dashboard
                    sidebar: false,         // Not a sidebar module
                    modal: true,            // Can be opened in modal
                    standalone: true        // Can run in standalone page
                },

                // Auto-load configuration
                autoLoad: false,  // Don't auto-load (only load when explicitly requested)
                priority: 10,     // Load priority (1-100, higher = loads first)

                // Initialization function
                init: async (container) => {
                    return await initDevTools(container);
                },

                // Destruction function
                destroy: async () => {
                    return await destroyDevTools();
                },

                // Module actions (toolbar buttons, context menu items)
                actions: [
                    {
                        id: 'new-module',
                        name: 'New Module',
                        icon: 'fa-plus',
                        handler: async () => {
                            const devTools = DevToolsModule.getInstance();
                            if (devTools) {
                                await devTools.createNewModule();
                            }
                        }
                    },
                    {
                        id: 'save-module',
                        name: 'Save Module',
                        icon: 'fa-save',
                        handler: async () => {
                            const devTools = DevToolsModule.getInstance();
                            if (devTools) {
                                await devTools.saveModule();
                            }
                        }
                    },
                    {
                        id: 'validate-module',
                        name: 'Validate Module',
                        icon: 'fa-check-circle',
                        handler: async () => {
                            const devTools = DevToolsModule.getInstance();
                            if (devTools) {
                                await devTools.validateModule();
                            }
                        }
                    }
                ],

                // Module settings
                settings: {
                    enableAutoSave: {
                        type: 'boolean',
                        default: true,
                        label: 'Enable Auto-Save',
                        description: 'Automatically save module every 30 seconds'
                    },
                    enableLivePreview: {
                        type: 'boolean',
                        default: true,
                        label: 'Enable Live Preview',
                        description: 'Show live preview of module in iframe'
                    },
                    theme: {
                        type: 'select',
                        default: 'vs-dark',
                        options: [
                            { value: 'vs', label: 'Light' },
                            { value: 'vs-dark', label: 'Dark' },
                            { value: 'hc-black', label: 'High Contrast' }
                        ],
                        label: 'Editor Theme',
                        description: 'Monaco Editor color theme'
                    }
                },

                // Module dependencies
                dependencies: {
                    scripts: [
                        'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs/loader.js'
                    ],
                    styles: [
                        'dev-tools-styles.css'
                    ]
                },

                // Module status
                status: {
                    enabled: true,
                    active: false,
                    error: null
                }
            });

            console.log('[DevToolsPlugin] ✅ Module registered with ModuleRegistry');

        } catch (error) {
            console.error('[DevToolsPlugin] ❌ Failed to register module:', error);
        }
    };

    // Auto-register when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', registerModule);
    } else {
        registerModule();
    }

})();
