/**
 * Tabulator Theme Adapter
 * Dynamically applies module colors to Tabulator tables
 * Version: 1.0.0
 * Last Updated: November 7, 2025
 * 
 * Purpose:
 * - Read module colors from manifest
 * - Generate custom CSS variables for Tabulator
 * - Apply theme dynamically to tables
 */

class TabulatorThemeAdapter {
    constructor(moduleId, manifest) {
        this.moduleId = moduleId;
        this.manifest = manifest;
        this.colors = manifest?.colors || this.getDefaultColors();
        this.styleElement = null;
    }

    /**
     * Get default colors if manifest doesn't define them
     */
    getDefaultColors() {
        return {
            primary: '#0078d4',
            secondary: '#00b294',
            hover: '#006cbe'
        };
    }

    /**
     * Generate CSS variables for module-specific Tabulator theme
     */
    generateThemeCSS() {
        const { primary, secondary, hover } = this.colors;

        // Helper: Lighten color for backgrounds
        const lighten = (color, opacity) => {
            const hex = color.replace('#', '');
            const r = parseInt(hex.substr(0, 2), 16);
            const g = parseInt(hex.substr(2, 2), 16);
            const b = parseInt(hex.substr(4, 2), 16);
            return `rgba(${r}, ${g}, ${b}, ${opacity})`;
        };

        return `
/* ============================================================================
   TABULATOR THEME - ${this.moduleId.toUpperCase()} MODULE
   Auto-generated from manifest.json colors
   ============================================================================ */

/* Scope all styles to this module's container */
#tab-${this.moduleId} .tabulator,
#${this.moduleId}-table-container .tabulator {
    /* Module Color Variables */
    --tabulator-primary: ${primary};
    --tabulator-secondary: ${secondary};
    --tabulator-hover: ${hover};
    --tabulator-primary-light: ${lighten(primary, 0.1)};
    --tabulator-primary-lighter: ${lighten(primary, 0.05)};
    
    /* Dark Theme Base Colors */
    --tabulator-bg-dark: #0B0E13;
    --tabulator-bg-darker: #161b22;
    --tabulator-border: #2A3142;
    --tabulator-text: #E5E7EB;
    --tabulator-text-secondary: #9CA3AF;
    
    /* Table Structure */
    background-color: var(--tabulator-bg-dark);
    border: 1px solid var(--tabulator-border);
    color: var(--tabulator-text);
    font-size: 14px;
}

/* ===== HEADER STYLING ===== */
#tab-${this.moduleId} .tabulator .tabulator-header,
#${this.moduleId}-table-container .tabulator .tabulator-header {
    background-color: var(--tabulator-bg-darker);
    border-bottom: 2px solid var(--tabulator-primary);
    color: var(--tabulator-text);
    font-weight: 600;
}

#tab-${this.moduleId} .tabulator .tabulator-col,
#${this.moduleId}-table-container .tabulator .tabulator-col {
    background-color: var(--tabulator-bg-darker);
    border-right: 1px solid var(--tabulator-border);
}

#tab-${this.moduleId} .tabulator .tabulator-col:hover,
#${this.moduleId}-table-container .tabulator .tabulator-col:hover {
    background-color: var(--tabulator-primary-lighter);
}

#tab-${this.moduleId} .tabulator .tabulator-col-content,
#${this.moduleId}-table-container .tabulator .tabulator-col-content {
    color: var(--tabulator-text);
    padding: 12px 10px;
}

/* ===== SORT ARROWS ===== */
#tab-${this.moduleId} .tabulator .tabulator-col.tabulator-sortable .tabulator-col-title,
#${this.moduleId}-table-container .tabulator .tabulator-col.tabulator-sortable .tabulator-col-title {
    padding-right: 20px;
}

#tab-${this.moduleId} .tabulator .tabulator-arrow,
#${this.moduleId}-table-container .tabulator .tabulator-arrow {
    border-bottom-color: var(--tabulator-primary);
}

/* ===== HEADER FILTERS ===== */
#tab-${this.moduleId} .tabulator .tabulator-header-filter input,
#${this.moduleId}-table-container .tabulator .tabulator-header-filter input,
#tab-${this.moduleId} .tabulator .tabulator-header-filter select,
#${this.moduleId}-table-container .tabulator .tabulator-header-filter select {
    background: var(--tabulator-bg-dark);
    border: 1px solid var(--tabulator-border);
    color: var(--tabulator-text);
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}

#tab-${this.moduleId} .tabulator .tabulator-header-filter input:focus,
#${this.moduleId}-table-container .tabulator .tabulator-header-filter input:focus,
#tab-${this.moduleId} .tabulator .tabulator-header-filter select:focus,
#${this.moduleId}-table-container .tabulator .tabulator-header-filter select:focus {
    border-color: var(--tabulator-primary);
    outline: none;
    box-shadow: 0 0 0 2px var(--tabulator-primary-light);
}

/* ===== ROWS ===== */
#tab-${this.moduleId} .tabulator .tabulator-row,
#${this.moduleId}-table-container .tabulator .tabulator-row {
    background-color: var(--tabulator-bg-dark);
    border-bottom: 1px solid var(--tabulator-border);
    color: var(--tabulator-text);
}

#tab-${this.moduleId} .tabulator .tabulator-row:hover,
#${this.moduleId}-table-container .tabulator .tabulator-row:hover {
    background-color: var(--tabulator-primary-lighter) !important;
}

#tab-${this.moduleId} .tabulator .tabulator-row.tabulator-row-even,
#${this.moduleId}-table-container .tabulator .tabulator-row.tabulator-row-even {
    background-color: var(--tabulator-bg-darker);
}

/* ===== SELECTED ROWS ===== */
#tab-${this.moduleId} .tabulator .tabulator-row.tabulator-selected,
#${this.moduleId}-table-container .tabulator .tabulator-row.tabulator-selected {
    background-color: var(--tabulator-primary-light) !important;
}

#tab-${this.moduleId} .tabulator .tabulator-row.tabulator-selected:hover,
#${this.moduleId}-table-container .tabulator .tabulator-row.tabulator-selected:hover {
    background-color: var(--tabulator-hover) !important;
    opacity: 0.9;
}

/* ===== CELLS ===== */
#tab-${this.moduleId} .tabulator .tabulator-cell,
#${this.moduleId}-table-container .tabulator .tabulator-cell {
    border-right: 1px solid var(--tabulator-border);
    padding: 10px 10px;
}

/* ===== PAGINATION ===== */
#tab-${this.moduleId} .tabulator .tabulator-footer,
#${this.moduleId}-table-container .tabulator .tabulator-footer {
    background-color: var(--tabulator-bg-darker);
    border-top: 2px solid var(--tabulator-primary);
    color: var(--tabulator-text);
    padding: 10px;
}

#tab-${this.moduleId} .tabulator .tabulator-page,
#${this.moduleId}-table-container .tabulator .tabulator-page {
    background: var(--tabulator-bg-dark);
    border: 1px solid var(--tabulator-border);
    color: var(--tabulator-text);
    margin: 0 4px;
    padding: 6px 12px;
    border-radius: 4px;
}

#tab-${this.moduleId} .tabulator .tabulator-page:hover,
#${this.moduleId}-table-container .tabulator .tabulator-page:hover {
    background: var(--tabulator-primary-lighter);
    border-color: var(--tabulator-primary);
}

#tab-${this.moduleId} .tabulator .tabulator-page.active,
#${this.moduleId}-table-container .tabulator .tabulator-page.active {
    background: var(--tabulator-primary);
    border-color: var(--tabulator-primary);
    color: white;
    font-weight: 600;
}

#tab-${this.moduleId} .tabulator .tabulator-page.disabled,
#${this.moduleId}-table-container .tabulator .tabulator-page.disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

/* ===== ROW SELECTION CHECKBOX ===== */
#tab-${this.moduleId} .tabulator .tabulator-row-handle,
#${this.moduleId}-table-container .tabulator .tabulator-row-handle {
    background: var(--tabulator-bg-darker);
}

#tab-${this.moduleId} .tabulator .tabulator-row-handle input[type="checkbox"],
#${this.moduleId}-table-container .tabulator .tabulator-row-handle input[type="checkbox"] {
    accent-color: var(--tabulator-primary);
}

/* ===== LOADING OVERLAY ===== */
#tab-${this.moduleId} .tabulator .tabulator-loader,
#${this.moduleId}-table-container .tabulator .tabulator-loader {
    background: rgba(11, 14, 19, 0.9);
    border: 2px solid var(--tabulator-primary);
}

#tab-${this.moduleId} .tabulator .tabulator-loader-msg,
#${this.moduleId}-table-container .tabulator .tabulator-loader-msg {
    color: var(--tabulator-primary);
    font-weight: 600;
}

/* ===== EDIT MODE ===== */
#tab-${this.moduleId} .tabulator .tabulator-cell.tabulator-editing,
#${this.moduleId}-table-container .tabulator .tabulator-cell.tabulator-editing {
    border: 2px solid var(--tabulator-primary);
    background: var(--tabulator-bg-darker);
}

#tab-${this.moduleId} .tabulator .tabulator-cell.tabulator-editing input,
#${this.moduleId}-table-container .tabulator .tabulator-cell.tabulator-editing input,
#tab-${this.moduleId} .tabulator .tabulator-cell.tabulator-editing select,
#${this.moduleId}-table-container .tabulator .tabulator-cell.tabulator-editing select {
    background: var(--tabulator-bg-dark);
    border: 1px solid var(--tabulator-primary);
    color: var(--tabulator-text);
}

/* ===== SCROLLBARS ===== */
#tab-${this.moduleId} .tabulator .tabulator-tableholder::-webkit-scrollbar,
#${this.moduleId}-table-container .tabulator .tabulator-tableholder::-webkit-scrollbar {
    width: 12px;
    height: 12px;
}

#tab-${this.moduleId} .tabulator .tabulator-tableholder::-webkit-scrollbar-track,
#${this.moduleId}-table-container .tabulator .tabulator-tableholder::-webkit-scrollbar-track {
    background: var(--tabulator-bg-darker);
}

#tab-${this.moduleId} .tabulator .tabulator-tableholder::-webkit-scrollbar-thumb,
#${this.moduleId}-table-container .tabulator .tabulator-tableholder::-webkit-scrollbar-thumb {
    background: var(--tabulator-primary);
    border-radius: 6px;
}

#tab-${this.moduleId} .tabulator .tabulator-tableholder::-webkit-scrollbar-thumb:hover,
#${this.moduleId}-table-container .tabulator .tabulator-tableholder::-webkit-scrollbar-thumb:hover {
    background: var(--tabulator-hover);
}

/* ===== ROW TAGGING STYLES (from tabulator-functions.js) ===== */
#tab-${this.moduleId} .tabulator .tagged-row-green,
#${this.moduleId}-table-container .tabulator .tagged-row-green {
    background: rgba(40, 167, 69, 0.15) !important;
    border-left: 4px solid #28a745 !important;
}

#tab-${this.moduleId} .tabulator .tagged-row-orange,
#${this.moduleId}-table-container .tabulator .tagged-row-orange {
    background: rgba(253, 126, 20, 0.15) !important;
    border-left: 4px solid #fd7e14 !important;
}

#tab-${this.moduleId} .tabulator .tagged-row-red,
#${this.moduleId}-table-container .tabulator .tagged-row-red {
    background: rgba(220, 53, 69, 0.15) !important;
    border-left: 4px solid #dc3545 !important;
}

#tab-${this.moduleId} .tabulator .action-btn-tag.tag-green,
#${this.moduleId}-table-container .tabulator .action-btn-tag.tag-green {
    background: #28a745 !important;
    color: white !important;
}

#tab-${this.moduleId} .tabulator .action-btn-tag.tag-orange,
#${this.moduleId}-table-container .tabulator .action-btn-tag.tag-orange {
    background: #fd7e14 !important;
    color: white !important;
}

#tab-${this.moduleId} .tabulator .action-btn-tag.tag-red,
#${this.moduleId}-table-container .tabulator .action-btn-tag.tag-red {
    background: #dc3545 !important;
    color: white !important;
}

/* ===== ACTION BUTTONS ===== */
#tab-${this.moduleId} .tabulator .action-btn,
#${this.moduleId}-table-container .tabulator .action-btn {
    background: var(--tabulator-primary);
    color: white;
    border: none;
    padding: 4px 10px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 11px;
    transition: all 0.2s ease;
}

#tab-${this.moduleId} .tabulator .action-btn:hover,
#${this.moduleId}-table-container .tabulator .action-btn:hover {
    background: var(--tabulator-hover);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px var(--tabulator-primary-light);
}

/* ===== RESPONSIVE FONT SIZING ===== */
#tab-${this.moduleId} .tabulator[data-font-size="small"],
#${this.moduleId}-table-container .tabulator[data-font-size="small"] {
    font-size: 12px;
}

#tab-${this.moduleId} .tabulator[data-font-size="large"],
#${this.moduleId}-table-container .tabulator[data-font-size="large"] {
    font-size: 16px;
}

#tab-${this.moduleId} .tabulator[data-font-size="xlarge"],
#${this.moduleId}-table-container .tabulator[data-font-size="xlarge"] {
    font-size: 18px;
}
`;
    }

    /**
     * Inject theme CSS into document head
     */
    injectTheme() {
        // Remove existing theme if already injected
        if (this.styleElement) {
            this.styleElement.remove();
        }

        // Create style element
        this.styleElement = document.createElement('style');
        this.styleElement.id = `tabulator-theme-${this.moduleId}`;
        this.styleElement.textContent = this.generateThemeCSS();

        // Append to head
        document.head.appendChild(this.styleElement);

        console.log(`✅ Tabulator theme injected for ${this.moduleId} module`);
        console.log(`   Primary: ${this.colors.primary}`);
        console.log(`   Secondary: ${this.colors.secondary}`);
        console.log(`   Hover: ${this.colors.hover}`);
    }

    /**
     * Remove theme CSS from document
     */
    removeTheme() {
        if (this.styleElement) {
            this.styleElement.remove();
            this.styleElement = null;
            console.log(`🗑️  Tabulator theme removed for ${this.moduleId} module`);
        }
    }

    /**
     * Update colors dynamically
     */
    updateColors(newColors) {
        this.colors = { ...this.colors, ...newColors };
        this.injectTheme(); // Re-inject with new colors
    }
}

// Export to window for global access
window.TabulatorThemeAdapter = TabulatorThemeAdapter;

console.log('✅ TabulatorThemeAdapter loaded');
