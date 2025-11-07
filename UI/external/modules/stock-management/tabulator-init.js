/**
 * Stock Management Tabulator Initialization Helper
 * Version: 1.0.0
 * Last Updated: November 7, 2025
 * 
 * Purpose:
 * - Clean, modular Tabulator initialization separate from broken stock-management.js
 * - Applies adaptive theming from manifest.json colors
 * - Integrates with tabulator-functions.js utility library
 * - Manages all Tabulator table instances for Stock Management module
 * 
 * Dependencies:
 * - Tabulator 5.5.2 (CDN)
 * - tabulator-functions.js (utility library)
 * - tabulator-theme-adapter.js (adaptive theming)
 * 
 * Usage:
 * const helper = new StockManagementTabulatorHelper(moduleInstance);
 * helper.initialize();
 * helper.createReorderDashboard('container-id', data);
 */

class StockManagementTabulatorHelper {
    constructor(moduleInstance) {
        this.module = moduleInstance;
        this.themeAdapter = null;
        this.tables = {}; // Store table instances by key
        this.selectedRows = {}; // Track selected rows per table

        console.log('[Tabulator Helper] Initializing for Stock Management module');
    }

    /**
     * Initialize theme adapter and apply module colors
     */
    initialize() {
        try {
            // Check dependencies loaded
            if (typeof Tabulator === 'undefined') {
                console.error('[Tabulator Helper] ERROR: Tabulator library not loaded');
                return false;
            }

            if (typeof TabulatorThemeAdapter === 'undefined') {
                console.error('[Tabulator Helper] ERROR: TabulatorThemeAdapter not loaded');
                return false;
            }

            if (typeof TabulatorFunctions === 'undefined') {
                console.warn('[Tabulator Helper] WARNING: TabulatorFunctions not loaded (utility features disabled)');
            }

            // Apply adaptive theme
            this.themeAdapter = new TabulatorThemeAdapter(
                this.module.moduleId,
                this.module.manifest
            );
            this.themeAdapter.injectTheme();

            console.log('[Tabulator Helper] Initialized successfully');
            console.log(`  Primary Color: ${this.module.manifest.colors.primary}`);
            console.log(`  Secondary Color: ${this.module.manifest.colors.secondary}`);
            console.log(`  Hover Color: ${this.module.manifest.colors.hover}`);

            return true;
        } catch (error) {
            console.error('[Tabulator Helper] Initialization failed:', error);
            return false;
        }
    }

    /**
     * Create Reorder Dashboard Tabulator table
     * 
     * @param {string} containerId - DOM element ID for table container
     * @param {Array} data - Array of reorder items
     * @returns {Tabulator} Table instance
     */
    createReorderDashboard(containerId, data) {
        try {
            console.log(`[Tabulator Helper] Creating Reorder Dashboard in #${containerId}`);
            console.log(`  Data rows: ${data.length}`);

            // Check if Tabulator utilities available
            const hasUtilities = typeof window.TabulatorFunctions !== 'undefined';

            const tableConfig = {
                data: data,
                layout: "fitDataStretch",
                pagination: true,
                paginationSize: 20,
                paginationSizeSelector: [10, 20, 50, 100],
                movableColumns: true,
                resizableColumns: true,
                resizableRows: false,
                selectable: true,
                selectableRangeMode: "click",
                height: "600px",
                placeholder: "No reorder items found",

                // Columns definition
                columns: [
                    // Selection checkbox
                    {
                        formatter: "rowSelection",
                        titleFormatter: "rowSelection",
                        hozAlign: "center",
                        headerSort: false,
                        width: 50,
                        frozen: true
                    },

                    // Tag button (if utilities loaded)
                    ...(hasUtilities ? [{
                        title: "Tag",
                        field: "_tag",
                        width: 60,
                        hozAlign: "center",
                        headerSort: false,
                        frozen: true,
                        formatter: window.TabulatorFunctions.createTagButtonFormatter('sku', null, 'stock_reorder_tags')
                    }] : []),

                    // SKU
                    {
                        title: "SKU",
                        field: "sku",
                        width: 120,
                        headerFilter: "input",
                        headerFilterPlaceholder: "Search SKU...",
                        frozen: true
                    },

                    // Product Name
                    {
                        title: "Product Name",
                        field: "product_name",
                        width: 250,
                        headerFilter: "input",
                        headerFilterPlaceholder: "Search name...",
                        tooltip: true
                    },

                    // Current Stock
                    {
                        title: "Current Stock",
                        field: "current_stock",
                        width: 120,
                        hozAlign: "right",
                        headerFilter: "number",
                        headerFilterPlaceholder: "Min...",
                        headerFilterFunc: ">=",
                        formatter: (cell) => {
                            const value = cell.getValue();
                            const reorderLevel = cell.getRow().getData().reorder_level;

                            // Color code: red if below reorder level
                            if (value < reorderLevel) {
                                return `<span style="color: #dc3545; font-weight: 600;">${value}</span>`;
                            }
                            return value;
                        }
                    },

                    // Reorder Level
                    {
                        title: "Reorder Level",
                        field: "reorder_level",
                        width: 120,
                        hozAlign: "right",
                        headerFilter: "number"
                    },

                    // Reorder Quantity
                    {
                        title: "Reorder Qty",
                        field: "reorder_quantity",
                        width: 120,
                        hozAlign: "right",
                        headerFilter: "number",
                        editor: "number",
                        editorParams: { min: 0, step: 1 }
                    },

                    // Status
                    {
                        title: "Status",
                        field: "status",
                        width: 120,
                        headerFilter: "select",
                        headerFilterParams: {
                            values: {
                                "": "All",
                                "critical": "Critical",
                                "low": "Low",
                                "normal": "Normal",
                                "ordered": "Ordered"
                            }
                        },
                        formatter: (cell) => {
                            const status = cell.getValue() || 'normal';
                            const colors = {
                                'critical': '#dc3545',
                                'low': '#ffc107',
                                'normal': '#28a745',
                                'ordered': '#17a2b8'
                            };

                            return `<span style="
                                background: ${colors[status] || '#6c757d'};
                                color: white;
                                padding: 4px 12px;
                                border-radius: 12px;
                                font-size: 11px;
                                font-weight: 600;
                                text-transform: uppercase;
                            ">${status}</span>`;
                        }
                    },

                    // Supplier
                    {
                        title: "Supplier",
                        field: "supplier",
                        width: 150,
                        headerFilter: "input",
                        headerFilterPlaceholder: "Search supplier..."
                    },

                    // Last Order Date
                    {
                        title: "Last Order",
                        field: "last_order_date",
                        width: 120,
                        formatter: (cell) => {
                            const date = cell.getValue();
                            if (!date) return '-';
                            return new Date(date).toLocaleDateString();
                        }
                    },

                    // Actions
                    {
                        title: "Actions",
                        field: "_actions",
                        width: 120,
                        hozAlign: "center",
                        headerSort: false,
                        formatter: (cell) => {
                            return `
                                <button class="action-btn action-btn-order" 
                                        style="margin: 0 4px; padding: 4px 10px; font-size: 11px;">
                                    Order
                                </button>
                                <button class="action-btn action-btn-view" 
                                        style="margin: 0 4px; padding: 4px 10px; font-size: 11px;">
                                    View
                                </button>
                            `;
                        },
                        cellClick: (e, cell) => {
                            if (e.target.classList.contains('action-btn-order')) {
                                this.handleReorderAction(cell.getRow().getData());
                            } else if (e.target.classList.contains('action-btn-view')) {
                                this.handleViewAction(cell.getRow().getData());
                            }
                        }
                    }
                ],

                // Event handlers
                rowSelectionChanged: (data, rows) => {
                    this.selectedRows['reorder'] = data;

                    // Update selection count if utilities loaded
                    if (hasUtilities) {
                        const table = this.tables['reorder'];
                        window.TabulatorFunctions.updateSelectionCount(table, 'reorder-selection-count');
                    }

                    console.log(`[Reorder] ${data.length} rows selected`);
                },

                cellDblClick: (e, cell) => {
                    // Open cell popup if utilities loaded
                    if (hasUtilities) {
                        window.TabulatorFunctions.showCellPopup(e, cell);
                    }
                },

                dataLoaded: (data) => {
                    console.log(`[Reorder] Data loaded: ${data.length} rows`);

                    // Apply row tags if utilities loaded
                    if (hasUtilities) {
                        const table = this.tables['reorder'];
                        table.getRows().forEach(row => {
                            window.TabulatorFunctions.applyRowTagFormatter(row, 'sku', 'stock_reorder_tags');
                        });
                    }
                }
            };

            // Create table
            const table = new Tabulator(`#${containerId}`, tableConfig);
            this.tables['reorder'] = table;

            // Setup enhanced checkbox click if utilities loaded
            if (hasUtilities) {
                table.on("tableBuilt", () => {
                    window.TabulatorFunctions.setupEnhancedCheckboxClick(table);
                });
            }

            console.log('[Tabulator Helper] Reorder Dashboard created successfully');
            return table;

        } catch (error) {
            console.error('[Tabulator Helper] Failed to create Reorder Dashboard:', error);
            return null;
        }
    }

    /**
     * Create Profit Analysis Tabulator table
     * 
     * @param {string} containerId - DOM element ID for table container
     * @param {Array} data - Array of profit analysis items
     * @returns {Tabulator} Table instance
     */
    createProfitAnalysis(containerId, data) {
        try {
            console.log(`[Tabulator Helper] Creating Profit Analysis in #${containerId}`);
            console.log(`  Data rows: ${data.length}`);

            const hasUtilities = typeof window.TabulatorFunctions !== 'undefined';

            const tableConfig = {
                data: data,
                layout: "fitDataStretch",
                pagination: true,
                paginationSize: 20,
                paginationSizeSelector: [10, 20, 50, 100],
                movableColumns: true,
                resizableColumns: true,
                selectable: true,
                height: "600px",
                placeholder: "No profit data found",

                columns: [
                    // Selection checkbox
                    {
                        formatter: "rowSelection",
                        titleFormatter: "rowSelection",
                        hozAlign: "center",
                        headerSort: false,
                        width: 50,
                        frozen: true
                    },

                    // Period
                    {
                        title: "Period",
                        field: "period",
                        width: 120,
                        headerFilter: "input",
                        headerFilterPlaceholder: "Search period...",
                        frozen: true
                    },

                    // Product Name
                    {
                        title: "Product",
                        field: "product_name",
                        width: 200,
                        headerFilter: "input",
                        headerFilterPlaceholder: "Search product...",
                        tooltip: true
                    },

                    // Revenue
                    {
                        title: "Revenue",
                        field: "revenue",
                        width: 130,
                        hozAlign: "right",
                        headerFilter: "number",
                        formatter: "money",
                        formatterParams: {
                            symbol: "$",
                            precision: 2,
                            thousand: ","
                        }
                    },

                    // Cost
                    {
                        title: "Cost",
                        field: "cost",
                        width: 130,
                        hozAlign: "right",
                        headerFilter: "number",
                        formatter: "money",
                        formatterParams: {
                            symbol: "$",
                            precision: 2,
                            thousand: ","
                        }
                    },

                    // Profit
                    {
                        title: "Profit",
                        field: "profit",
                        width: 130,
                        hozAlign: "right",
                        headerFilter: "number",
                        formatter: (cell) => {
                            const value = cell.getValue();
                            const color = value >= 0 ? '#28a745' : '#dc3545';
                            const formatted = new Intl.NumberFormat('en-US', {
                                style: 'currency',
                                currency: 'USD'
                            }).format(value);

                            return `<span style="color: ${color}; font-weight: 600;">${formatted}</span>`;
                        }
                    },

                    // Margin %
                    {
                        title: "Margin %",
                        field: "margin_percent",
                        width: 110,
                        hozAlign: "right",
                        headerFilter: "number",
                        formatter: (cell) => {
                            const value = cell.getValue();
                            const color = value >= 20 ? '#28a745' : value >= 10 ? '#ffc107' : '#dc3545';

                            return `<span style="color: ${color}; font-weight: 600;">${value.toFixed(2)}%</span>`;
                        }
                    },

                    // Units Sold
                    {
                        title: "Units Sold",
                        field: "units_sold",
                        width: 110,
                        hozAlign: "right",
                        headerFilter: "number"
                    }
                ],

                // Event handlers
                rowSelectionChanged: (data, rows) => {
                    this.selectedRows['profit'] = data;

                    if (hasUtilities) {
                        const table = this.tables['profit'];
                        window.TabulatorFunctions.updateSelectionCount(table, 'profit-selection-count');
                    }

                    console.log(`[Profit] ${data.length} rows selected`);
                },

                cellDblClick: (e, cell) => {
                    if (hasUtilities) {
                        window.TabulatorFunctions.showCellPopup(e, cell);
                    }
                },

                dataLoaded: (data) => {
                    console.log(`[Profit] Data loaded: ${data.length} rows`);
                }
            };

            // Create table
            const table = new Tabulator(`#${containerId}`, tableConfig);
            this.tables['profit'] = table;

            // Setup enhanced checkbox click
            if (hasUtilities) {
                table.on("tableBuilt", () => {
                    window.TabulatorFunctions.setupEnhancedCheckboxClick(table);
                });
            }

            console.log('[Tabulator Helper] Profit Analysis created successfully');
            return table;

        } catch (error) {
            console.error('[Tabulator Helper] Failed to create Profit Analysis:', error);
            return null;
        }
    }

    /**
     * Export table to Excel
     * @param {string} tableKey - Key of table to export ('reorder' or 'profit')
     * @param {string} filename - Output filename (without extension)
     */
    exportToExcel(tableKey, filename) {
        const table = this.tables[tableKey];
        if (!table) {
            console.error(`[Tabulator Helper] Table '${tableKey}' not found`);
            return;
        }

        try {
            table.download("xlsx", `${filename}.xlsx`, {
                sheetName: "Stock Data"
            });
            console.log(`[Tabulator Helper] Exported ${tableKey} to ${filename}.xlsx`);
        } catch (error) {
            console.error('[Tabulator Helper] Export failed:', error);
        }
    }

    /**
     * Set font size for table
     * @param {string} tableKey - Table key ('reorder' or 'profit')
     * @param {string} size - Size: 'small', 'medium', 'large', 'xlarge'
     */
    setFontSize(tableKey, size) {
        const table = this.tables[tableKey];
        if (!table) {
            console.error(`[Tabulator Helper] Table '${tableKey}' not found`);
            return;
        }

        table.element.setAttribute('data-font-size', size);
        console.log(`[Tabulator Helper] Font size set to ${size} for ${tableKey}`);
    }

    /**
     * Bulk delete selected rows
     * @param {string} tableKey - Table key
     * @param {Function} deleteCallback - Async function(rowsData) => Promise<{success, count}>
     */
    async bulkDelete(tableKey, deleteCallback) {
        const table = this.tables[tableKey];
        if (!table) {
            console.error(`[Tabulator Helper] Table '${tableKey}' not found`);
            return;
        }

        if (typeof window.TabulatorFunctions === 'undefined') {
            console.error('[Tabulator Helper] TabulatorFunctions not loaded');
            return;
        }

        try {
            await window.TabulatorFunctions.bulkDeleteRows(
                table,
                deleteCallback,
                "Are you sure you want to delete selected items?"
            );
        } catch (error) {
            console.error('[Tabulator Helper] Bulk delete failed:', error);
        }
    }

    /**
     * Handle reorder action (create purchase order)
     * @param {Object} rowData - Row data object
     */
    handleReorderAction(rowData) {
        console.log('[Tabulator Helper] Order action:', rowData);

        // Call module's reorder handler if exists
        if (typeof this.module.handleReorderRequest === 'function') {
            this.module.handleReorderRequest(rowData);
        } else {
            console.warn('[Tabulator Helper] Module.handleReorderRequest not found');
        }
    }

    /**
     * Handle view action (show item details)
     * @param {Object} rowData - Row data object
     */
    handleViewAction(rowData) {
        console.log('[Tabulator Helper] View action:', rowData);

        // Use full row viewer if available
        if (typeof window.TabulatorFunctions !== 'undefined') {
            const table = this.tables['reorder'];
            window.TabulatorFunctions.viewFullRow(table, rowData.sku, 'sku');
        }
    }

    /**
     * Get table instance by key
     * @param {string} tableKey - Table key
     * @returns {Tabulator|null} Table instance or null
     */
    getTable(tableKey) {
        return this.tables[tableKey] || null;
    }

    /**
     * Get selected rows for table
     * @param {string} tableKey - Table key
     * @returns {Array} Selected row data
     */
    getSelectedRows(tableKey) {
        return this.selectedRows[tableKey] || [];
    }

    /**
     * Cleanup - remove theme and destroy tables
     */
    destroy() {
        // Remove theme
        if (this.themeAdapter) {
            this.themeAdapter.removeTheme();
        }

        // Destroy all tables
        Object.keys(this.tables).forEach(key => {
            if (this.tables[key]) {
                this.tables[key].destroy();
            }
        });

        this.tables = {};
        this.selectedRows = {};

        console.log('[Tabulator Helper] Destroyed');
    }
}

// Export to window for global access
window.StockManagementTabulatorHelper = StockManagementTabulatorHelper;

console.log('[Tabulator Init] StockManagementTabulatorHelper loaded');
