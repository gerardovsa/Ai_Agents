/**
 * Vector Database - Integration Bootstrap
 * 
 * PURPOSE: Connect enhanced features to main module
 * USAGE: Import this file in vector_database_modern.js
 * 
 * LAST MODIFIED: 2025-11-30
 */

import { EnhancedVectorFeatures } from './vector_database_enhanced.js';

/**
 * Integrate enhanced features into main module
 * Call this in onSidebarLoad() after base setup
 */
export function integrateEnhancedFeatures(moduleContext, utilities) {
    // Extend module context with enhanced features
    Object.assign(moduleContext, {

        /**
         * Add enhanced tabs to sidebar
         */
        setupEnhancedTabs(container) {
            // Get existing tabs container
            const tabsContainer = container.querySelector('.vector-db-tabs');
            if (!tabsContainer) {
                utilities.log.warn('[ENHANCED] Tabs container not found');
                return;
            }

            // Add enhanced tab buttons
            const enhancedTabs = `
                <button class="vector-db-tab" data-tab="hybrid-search">
                    🔍 Hybrid Search
                </button>
                <button class="vector-db-tab" data-tab="cross-namespace">
                    🌐 Cross-Namespace
                </button>
                <button class="vector-db-tab" data-tab="metadata-filter">
                    🔧 Metadata Filter
                </button>
                <button class="vector-db-tab" data-tab="namespace-mgmt">
                    📁 Namespaces
                </button>
            `;

            tabsContainer.insertAdjacentHTML('beforeend', enhancedTabs);
            utilities.log.info('[ENHANCED] Added 4 enhanced tabs');
        },

        /**
         * Handle enhanced tab switching
         */
        switchToEnhancedTab(tabName, container) {
            utilities.log.info('[ENHANCED] Switching to:', tabName);

            const contentContainer = container.querySelector('#vector-db-content');
            if (!contentContainer) {
                utilities.log.error('[ENHANCED] Content container not found');
                return;
            }

            // Clear existing content
            contentContainer.innerHTML = '';

            // Render appropriate enhanced feature
            switch (tabName) {
                case 'hybrid-search':
                    EnhancedVectorFeatures.renderHybridSearchTab(contentContainer, utilities);
                    break;

                case 'cross-namespace':
                    EnhancedVectorFeatures.renderCrossNamespaceTab(contentContainer, utilities);
                    break;

                case 'metadata-filter':
                    EnhancedVectorFeatures.renderMetadataFilterTab(contentContainer, utilities);
                    break;

                case 'namespace-mgmt':
                    EnhancedVectorFeatures.renderNamespaceManagementTab(contentContainer, utilities);
                    break;

                default:
                    utilities.log.warn('[ENHANCED] Unknown tab:', tabName);
            }
        },

        /**
         * Load enhanced CSS
         */
        loadEnhancedStyles() {
            // Check if already loaded
            if (document.getElementById('vector-db-enhanced-styles')) {
                return;
            }

            const link = document.createElement('link');
            link.id = 'vector-db-enhanced-styles';
            link.rel = 'stylesheet';
            link.href = '/UI/modules_internal/vector_database/vector_database_enhanced.css';
            document.head.appendChild(link);

            utilities.log.info('[ENHANCED] Styles loaded');
        },

        /**
         * Initialize enhanced features
         */
        async initializeEnhanced(container) {
            try {
                // Load enhanced CSS
                this.loadEnhancedStyles();

                // Add enhanced tabs to UI
                this.setupEnhancedTabs(container);

                // Store reference to EnhancedVectorFeatures
                this.enhanced = EnhancedVectorFeatures;

                utilities.log.info('[ENHANCED] Initialization complete');
                return true;

            } catch (error) {
                utilities.log.error('[ENHANCED] Initialization failed:', error);
                return false;
            }
        }
    });

    return moduleContext;
}

/**
 * Enhanced tab detection helper
 */
export function isEnhancedTab(tabName) {
    const enhancedTabs = ['hybrid-search', 'cross-namespace', 'metadata-filter', 'namespace-mgmt'];
    return enhancedTabs.includes(tabName);
}

/**
 * Feature availability checker
 */
export function checkEnhancedFeaturesAvailable() {
    const checks = {
        hybrid_search: false,
        cross_namespace: false,
        metadata_filter: false,
        namespace_mgmt: false
    };

    // Check if enhanced module loaded
    if (typeof EnhancedVectorFeatures === 'undefined') {
        return { available: false, checks };
    }

    // Check each feature
    checks.hybrid_search = typeof EnhancedVectorFeatures.renderHybridSearchTab === 'function';
    checks.cross_namespace = typeof EnhancedVectorFeatures.renderCrossNamespaceTab === 'function';
    checks.metadata_filter = typeof EnhancedVectorFeatures.renderMetadataFilterTab === 'function';
    checks.namespace_mgmt = typeof EnhancedVectorFeatures.renderNamespaceManagementTab === 'function';

    const allAvailable = Object.values(checks).every(check => check === true);

    return { available: allAvailable, checks };
}

/**
 * Usage Example:
 * 
 * // In vector_database_modern.js:
 * 
 * import { integrateEnhancedFeatures, isEnhancedTab } from './vector_database_integration.js';
 * 
 * export default {
 *     // ... existing code ...
 *     
 *     async onSidebarLoad(utilities) {
 *         Object.assign(this, utilities);
 *         
 *         // Get container
 *         this.container = this.dom.getContainer();
 *         
 *         // Setup base features
 *         this.setupEventListeners();
 *         await this.loadCredentials();
 *         
 *         // ✨ Integrate enhanced features
 *         integrateEnhancedFeatures(this, utilities);
 *         await this.initializeEnhanced(this.container);
 *         
 *         // Switch to saved tab
 *         this.switchTab(this.state.currentTab);
 *     },
 *     
 *     switchTab(tabName) {
 *         // Check if enhanced tab
 *         if (isEnhancedTab(tabName)) {
 *             this.switchToEnhancedTab(tabName, this.container);
 *         } else {
 *             // Handle base tabs (credentials, upload, documents)
 *             // ... existing code ...
 *         }
 *         
 *         this.state.currentTab = tabName;
 *     }
 * };
 */
