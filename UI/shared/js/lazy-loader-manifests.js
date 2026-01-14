/**
 * Lazy Loader Manifests - Feature Module Definitions
 * 
 * Purpose: Define which modules to load for each feature
 * Usage: LazyLoader.loadManifest(MANIFESTS.synergy)
 * 
 * Each manifest includes:
 * - name: Feature name
 * - modules: Array of {url, options} to load
 * - dependencies: Array of prerequisite URLs
 * - estimatedSize: Approximate download size (KB)
 * - estimatedTime: Approximate load time (ms)
 * 
 * @version 1.0.0
 * @date December 6, 2025
 */

window.MANIFESTS = {
    /**
     * Post-Authentication Essentials
     * ✅ OPTIMIZED: Removed duplicate modules (already in HTML with data-post-auth defer)
     * ⚡ Only CDN libraries loaded here, internal modules handled by HTML
     * Target: 0.3s load time
     */
    postAuth: {
        name: 'Post-Auth Essentials',
        estimatedSize: 250, // KB (reduced from 740KB)
        estimatedTime: 300, // ms (reduced from 1000ms)
        dependencies: [],
        modules: [
            // ✅ Markdown & syntax highlighting (CDN only)
            {
                url: 'https://cdn.jsdelivr.net/npm/marked@9.1.0/marked.min.js',
                options: { async: true }
            },
            {
                url: 'https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js',
                options: { async: true }
            },
            {
                url: 'https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-tomorrow.min.css'
            }

            // ❌ REMOVED: Thread management system (loaded via HTML <script data-post-auth defer>)
            // ❌ REMOVED: Chat system (loaded via HTML <script data-post-auth defer>)
            // ❌ REMOVED: Real-time connection (loaded via HTML <script data-post-auth defer>)
            // See business-ai-platform-v2.html lines 588-639 for these modules
        ]
    },

    /**
     * Synergy Dashboard
     * Loads when user clicks Synergy tab
     * Target: 0.5s load time
     */
    synergy: {
        name: 'Synergy Dashboard',
        estimatedSize: 600, // KB
        estimatedTime: 500, // ms
        dependencies: [
            'https://cdn.jsdelivr.net/npm/tabulator-tables@6.2.5/dist/js/tabulator.min.js'
        ],
        modules: [
            // Synergy core
            {
                url: 'modules_internal/synergy/synergy.js',
                options: { async: false }
            },
            {
                url: 'modules_internal/synergy/synergy-manager.js',
                options: { async: false }
            },
            {
                url: 'modules_internal/synergy/synergy-js.js',
                options: { async: true }
            },
            {
                url: 'modules_internal/synergy/synergy-board-init.js',
                options: { async: true }
            },

            // Tabulator enhancements
            {
                url: 'shared/js/tabulator-functions.js',
                options: { async: true }
            },
            {
                url: 'shared/js/tabulator-enhancements.js',
                options: { async: true }
            },
            {
                url: 'shared/js/tabulator-validation.js',
                options: { async: true }
            },

            // Real-time updates
            {
                url: 'shared/js/synergy-realtime.js',
                options: { async: true }
            }
        ]
    },

    /**
     * Automation Canvas
     * Loads when user clicks Automation tab
     * Target: 0.3s load time
     */
    automation: {
        name: 'Automation Canvas',
        estimatedSize: 400, // KB
        estimatedTime: 400, // ms
        dependencies: [],
        modules: [
            {
                url: 'modules_internal/automation-workflows/automation-workflows.js',
                options: { async: false }
            },
            {
                url: 'modules_internal/automation-workflows/automation-canvas-extensions.js',
                options: { async: true }
            },
            {
                url: 'modules_internal/automation-workflows/automation-canvas-diagnostics.js',
                options: { async: true }
            },
            {
                url: 'modules_internal/automation-workflows/automation-thread-integration.js',
                options: { async: true }
            }
        ]
    },

    /**
     * Advanced Visualizations
     * Loads when user creates chart/graph
     * Target: 1.0s load time
     */
    visualizations: {
        name: 'Advanced Visualizations',
        estimatedSize: 3000, // KB (large: Chart.js + Plotly)
        estimatedTime: 1000, // ms
        dependencies: [],
        modules: [
            // Chart libraries
            {
                url: 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js',
                options: { async: true }
            },
            {
                url: 'https://cdn.plot.ly/plotly-2.27.0.min.js',
                options: { async: true }
            },
            {
                url: 'https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js',
                options: { async: true }
            },

            // Visualization engine
            {
                url: 'UI/visualisation_engine/visualisation_engine.js',
                options: { async: false }
            },
            {
                url: 'UI/visualisation_engine/visualisation_adapters.js',
                options: { async: true }
            },
            {
                url: 'UI/visualisation_engine/visualisation_interactive.js',
                options: { async: true }
            }
        ]
    },

    /**
     * Spreadsheet Editor
     * Loads when user opens data grid
     * Target: 1.5s load time
     */
    spreadsheet: {
        name: 'Spreadsheet Editor',
        estimatedSize: 1800, // KB (Handsontable is heavy)
        estimatedTime: 1500, // ms
        dependencies: [],
        modules: [
            {
                url: 'https://cdn.jsdelivr.net/npm/handsontable@14.5.0/dist/handsontable.full.min.js',
                options: { async: true }
            },
            {
                url: 'https://cdn.jsdelivr.net/npm/handsontable@14.5.0/dist/handsontable.full.min.css'
            },
            {
                url: 'modules_internal/spreadsheet/spreadsheet-editor.js',
                options: { async: false }
            },
            {
                url: 'modules_internal/spreadsheet/spreadsheet-formulas.js',
                options: { async: true }
            }
        ]
    },

    /**
     * PDF Export
     * Loads when user exports to PDF
     * Target: 0.8s load time
     */
    pdfExport: {
        name: 'PDF Export',
        estimatedSize: 600, // KB
        estimatedTime: 800, // ms
        dependencies: [],
        modules: [
            {
                url: 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js',
                options: { async: true }
            },
            {
                url: 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js',
                options: { async: true }
            },
            {
                url: 'modules_internal/export/pdf-generator.js',
                options: { async: false }
            }
        ]
    },

    /**
     * Transcription System
     * Loads when user clicks Transcription tab
     * Target: 0.4s load time
     */
    transcription: {
        name: 'Transcription System',
        estimatedSize: 400, // KB
        estimatedTime: 400, // ms
        dependencies: [],
        modules: [
            {
                url: 'modules_internal/transcription/transcription.js',
                options: { async: false }
            },
            {
                url: 'modules_internal/transcription/transcription-sidebar.js',
                options: { async: true }
            },
            {
                url: 'modules_internal/transcription/transcription-streaming-container.js',
                options: { async: true }
            }
        ]
    },

    /**
     * Background Pre-fetch
     * Loads after dashboard visible (non-blocking)
     * Target: Load in background, no time constraint
     */
    background: {
        name: 'Background Pre-fetch',
        estimatedSize: 2000, // KB
        estimatedTime: 0, // Non-blocking
        dependencies: [],
        modules: [
            // Common libraries (pre-fetch for future use)
            {
                url: 'https://cdn.jsdelivr.net/npm/tabulator-tables@6.2.5/dist/js/tabulator.min.js',
                options: { async: true }
            },
            {
                url: 'https://cdn.jsdelivr.net/npm/tabulator-tables@6.2.5/dist/css/tabulator_bootstrap5.min.css'
            },

            // Less common features
            {
                url: 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js',
                options: { async: true }
            }
        ]
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MANIFESTS;
}

console.log('✅ Lazy Loader Manifests loaded');
console.log(`📦 Available manifests: ${Object.keys(MANIFESTS).join(', ')}`);
