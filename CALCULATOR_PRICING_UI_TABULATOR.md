# Calculator Pricing Catalog UI - Tabulator Implementation

## Overview

A **Tabulator-based web interface** for managing 363 pricing parameters across 30 calculators, leveraging your existing Tabulator infrastructure.

---

## Why Tabulator? (Already in Your Stack!)

**You Already Have:**
- ✅ Tabulator 5.5.0 loaded in `business-ai-platform-v2.html`
- ✅ `tabulator-enhancements.js` (1239 lines) - 10 advanced features
- ✅ `tabulator-functions.js` (690 lines) - Utility library
- ✅ `tabulator-theme-adapter.js` (397 lines) - Module color theming
- ✅ `TabulatorPresets` - Saved views system
- ✅ `AdvancedFilterSystem` - Multi-column filtering
- ✅ `RowTaggingSystem` - Green/orange/red tagging
- ✅ `BulkActionsMenu` - Bulk operations UI
- ✅ Dark theme CSS with module color integration

**Proven in Production:**
- Stock Management module (5 Tabulator tables)
- Xero module (4 Tabulator tables)
- Shopify module (1 Tabulator table)

---

## Architecture

### File Structure

```
UI/modules_external/quote-calculator/
├── catalog/                                 # NEW Calculator Catalog Module
│   ├── catalog.html                         # Module HTML (loaded by module manager)
│   ├── catalog.js                           # Main module class
│   ├── catalog-tabulator.js                 # Tabulator table configurations
│   ├── catalog-api.js                       # Flask API client
│   └── manifest.json                        # Module config (colors, icon, routes)
│
├── backend/
│   ├── api/
│   │   └── catalog_routes.py                # NEW Flask routes
│   ├── models/
│   │   └── catalog_models.py                # SQLAlchemy models
│   └── services/
│       └── catalog_service.py               # Business logic
│
└── database/
    ├── migrations/
    │   └── 001_create_catalog_tables.sql    # DDL from design
    └── seeds/
        └── load_extracted_data.py            # Populate from JSON
```

### Module Integration

**Uses Existing Infrastructure:**
- Module Manager (lazy loading)
- Tabulator Theme Adapter (module colors)
- Tabulator Functions (tagging, filters, bulk actions)
- Tabulator Enhancements (presets, history, exports)
- API Utils (Flask communication)
- Toast System (notifications)

---

## Main Interface: Parameter Matrix

### HTML Structure

```html
<!-- catalog.html -->
<div id="calculator-catalog-module" class="module-container">
    <!-- Header Bar -->
    <div class="catalog-header">
        <div class="catalog-header-left">
            <h2>Calculator Pricing Catalog</h2>
            <span class="catalog-subtitle">363 parameters across 30 calculators</span>
        </div>
        <div class="catalog-header-right">
            <button id="catalog-refresh-btn" class="btn-icon" title="Refresh Data">
                <i class="fas fa-sync"></i>
            </button>
            <button id="catalog-presets-btn" class="btn-icon" title="Saved Views">
                <i class="fas fa-bookmark"></i>
            </button>
            <button id="catalog-export-btn" class="btn-icon" title="Export">
                <i class="fas fa-download"></i>
            </button>
        </div>
    </div>

    <!-- Filter Bar -->
    <div class="catalog-filters">
        <div class="filter-group">
            <label>Category</label>
            <select id="catalog-filter-category">
                <option value="">All Categories</option>
                <option value="Setup">Setup Costs</option>
                <option value="Material">Material Costs</option>
                <option value="Print">Print Costs</option>
                <option value="Profit">Profit Margins</option>
                <option value="Tax">Tax Rates</option>
            </select>
        </div>
        
        <div class="filter-group">
            <label>Calculator</label>
            <select id="catalog-filter-calculator">
                <option value="">All Calculators</option>
                <!-- Populated dynamically -->
            </select>
        </div>
        
        <div class="filter-group">
            <label>Search</label>
            <input type="text" id="catalog-search" placeholder="Search parameters...">
        </div>
        
        <button id="catalog-clear-filters" class="btn-secondary">Clear Filters</button>
    </div>

    <!-- Bulk Actions Menu (appears when rows selected) -->
    <div id="catalog-bulk-menu" class="bulk-actions-menu" style="display: none;">
        <span class="bulk-selection-count">0 rows selected</span>
        <button class="bulk-action-btn" data-action="update-base">Update Base Value</button>
        <button class="bulk-action-btn" data-action="create-override">Create Override</button>
        <button class="bulk-action-btn" data-action="reset-override">Reset to Base</button>
        <button class="bulk-action-btn" data-action="tag-green">Tag Green</button>
        <button class="bulk-action-btn" data-action="tag-orange">Tag Orange</button>
        <button class="bulk-action-btn" data-action="tag-red">Tag Red</button>
        <button class="bulk-action-btn" data-action="clear-tag">Clear Tags</button>
    </div>

    <!-- Main Tabulator Table -->
    <div id="catalog-parameter-matrix" class="tabulator-container"></div>

    <!-- Detail Panel (slide-out when row clicked) -->
    <div id="catalog-detail-panel" class="detail-panel" style="display: none;">
        <div class="detail-panel-header">
            <h3 id="detail-param-name"></h3>
            <button id="detail-close-btn" class="btn-icon">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="detail-panel-content">
            <!-- Parameter details, usage stats, history -->
        </div>
    </div>
</div>
```

---

## Tabulator Table Configuration

### catalog-tabulator.js

```javascript
/**
 * Calculator Catalog Tabulator Configurations
 * Version: 1.0.0
 */

class CatalogTabulatorHelper {
    constructor(moduleInstance) {
        this.module = moduleInstance;
        this.tables = {};
        this.themeAdapter = null;
    }

    /**
     * Initialize theme adapter
     */
    initialize() {
        // Apply module colors from manifest
        this.themeAdapter = new TabulatorThemeAdapter(
            this.module.moduleId,
            this.module.manifest
        );
        this.themeAdapter.injectTheme();

        console.log('[Catalog Tabulator] Initialized with module theme');
        return true;
    }

    /**
     * Create Parameter Matrix Table
     * Main table showing all parameters × calculators
     */
    createParameterMatrix(containerId, data) {
        const calculatorColumns = this.getCalculatorColumns();

        const tableConfig = {
            data: data,
            layout: "fitData",
            pagination: true,
            paginationSize: 50,
            paginationSizeSelector: [25, 50, 100, 200],
            movableColumns: true,
            resizableColumns: true,
            resizableRows: false,
            selectable: "highlight", // Multi-row selection
            selectableRangeMode: "click",
            height: "calc(100vh - 300px)",
            placeholder: "No parameters found",
            
            // Enable advanced features
            persistentLayout: true,
            persistentSort: true,
            persistentFilter: true,

            // Columns Definition
            columns: [
                // Selection checkbox
                {
                    formatter: "rowSelection",
                    titleFormatter: "rowSelection",
                    hozAlign: "center",
                    headerSort: false,
                    width: 50,
                    frozen: true,
                    download: false
                },

                // Tag button (using your existing row tagging system)
                {
                    title: "Tag",
                    field: "_tag",
                    width: 60,
                    hozAlign: "center",
                    headerSort: false,
                    frozen: true,
                    download: false,
                    formatter: window.TabulatorFunctions.createTagButtonFormatter(
                        'parameter_id',
                        null,
                        'catalog_parameter_tags'
                    )
                },

                // Parameter Name (frozen left)
                {
                    title: "Parameter Name",
                    field: "parameter_name",
                    width: 200,
                    headerFilter: "input",
                    headerFilterPlaceholder: "Search...",
                    frozen: true,
                    tooltip: true,
                    formatter: "html",
                    formatterParams: {
                        target: "_blank"
                    },
                    cellClick: (e, cell) => {
                        this.module.showParameterDetail(cell.getData());
                    }
                },

                // Category
                {
                    title: "Category",
                    field: "category",
                    width: 120,
                    headerFilter: "select",
                    headerFilterParams: {
                        values: ["", "Setup", "Material", "Print", "Profit", "Tax"],
                        clearable: true
                    },
                    frozen: true
                },

                // Base Value
                {
                    title: "Base Value",
                    field: "base_value",
                    width: 100,
                    hozAlign: "right",
                    editor: "number",
                    editorParams: {
                        min: 0,
                        step: 0.01
                    },
                    formatter: "money",
                    formatterParams: {
                        decimal: ".",
                        thousand: ",",
                        symbol: "$",
                        precision: 2
                    },
                    headerFilter: "number",
                    headerFilterPlaceholder: "Min...",
                    frozen: true,
                    cellEdited: (cell) => {
                        this.module.updateBaseValue(cell);
                    }
                },

                // Total Usage Count (generated column)
                {
                    title: "Used By",
                    field: "total_usage_count",
                    width: 90,
                    hozAlign: "center",
                    headerFilter: "number",
                    headerFilterPlaceholder: "Min...",
                    tooltip: "Number of calculators using this parameter"
                },

                // Dynamic Calculator Columns (30 columns)
                ...calculatorColumns,

                // Actions column
                {
                    title: "Actions",
                    field: "_actions",
                    width: 120,
                    hozAlign: "center",
                    headerSort: false,
                    download: false,
                    formatter: this.createActionsFormatter()
                }
            ],

            // Row Context Menu (right-click)
            rowContextMenu: [
                {
                    label: "View Details",
                    action: (e, row) => {
                        this.module.showParameterDetail(row.getData());
                    }
                },
                {
                    label: "Edit Base Value",
                    action: (e, row) => {
                        this.module.editBaseValue(row);
                    }
                },
                {
                    separator: true
                },
                {
                    label: "Create Override",
                    action: (e, row) => {
                        this.module.createOverride(row);
                    }
                },
                {
                    label: "Reset All Overrides",
                    action: (e, row) => {
                        this.module.resetAllOverrides(row);
                    }
                },
                {
                    separator: true
                },
                {
                    label: "View History",
                    action: (e, row) => {
                        this.module.viewHistory(row);
                    }
                },
                {
                    label: "Export Parameter",
                    action: (e, row) => {
                        this.module.exportParameter(row);
                    }
                }
            ],

            // Callbacks
            rowSelectionChanged: (data, rows) => {
                this.module.onRowSelectionChanged(data, rows);
            },

            dataLoaded: (data) => {
                console.log(`[Catalog] Loaded ${data.length} parameters`);
                this.applyStoredTags();
            }
        };

        // Create table instance
        const table = new Tabulator(`#${containerId}`, tableConfig);

        // Store reference
        this.tables['parameterMatrix'] = table;

        // Enable advanced enhancements
        this.enableAdvancedFeatures(table);

        return table;
    }

    /**
     * Generate dynamic calculator columns
     * Creates 30 columns (one per calculator)
     */
    getCalculatorColumns() {
        const calculators = [
            'BollardSigns',
            'PremiumBusinessCards',
            'NotepadsA4',
            'NotepadsA5',
            'NotepadsA6',
            'WireBound',
            'SpiralBound',
            'CustomVinylStickers',
            'CorfluteSigns',
            // ... 21 more calculators
        ];

        return calculators.map(calc => ({
            title: calc.replace(/([A-Z])/g, ' $1').trim(), // "BollardSigns" → "Bollard Signs"
            field: `calc_${calc}`,
            width: 120,
            hozAlign: "right",
            headerFilter: "number",
            editor: "number",
            editorParams: {
                min: 0,
                step: 0.01
            },
            formatter: this.createCalculatorCellFormatter(calc),
            cellEdited: (cell) => {
                this.module.updateCalculatorValue(cell, calc);
            },
            tooltip: (e, cell) => {
                return this.getCalculatorCellTooltip(cell, calc);
            }
        }));
    }

    /**
     * Custom formatter for calculator cells
     * Shows value with color coding:
     * - Green background = uses base value
     * - Orange background = has override
     * - Gray = parameter not used by calculator
     */
    createCalculatorCellFormatter(calculatorName) {
        return function(cell, formatterParams, onRendered) {
            const value = cell.getValue();
            const rowData = cell.getData();
            const baseValue = rowData.base_value;
            const usedByCalculators = rowData.used_by_calculators || [];

            // Find calculator usage info
            const calcUsage = usedByCalculators.find(
                c => c.calculator === calculatorName
            );

            if (!calcUsage) {
                // Parameter not used by this calculator
                cell.getElement().style.background = 'rgba(100, 100, 100, 0.1)';
                cell.getElement().style.color = '#666';
                return '—';
            }

            const isOverride = calcUsage.override;
            const calcValue = calcUsage.value;

            // Color coding
            if (isOverride) {
                // Orange = custom override
                cell.getElement().style.background = 'rgba(230, 81, 0, 0.15)';
                cell.getElement().style.borderLeft = '3px solid #e65100';
                cell.getElement().innerHTML = `<span title="Override">⚠️ $${calcValue.toFixed(2)}</span>`;
            } else {
                // Green = uses base value
                cell.getElement().style.background = 'rgba(46, 125, 50, 0.15)';
                cell.getElement().style.borderLeft = '3px solid #2e7d32';
                cell.getElement().innerHTML = `<span title="Base value">✅ $${calcValue.toFixed(2)}</span>`;
            }

            return cell.getElement();
        };
    }

    /**
     * Get tooltip text for calculator cell
     */
    getCalculatorCellTooltip(cell, calculatorName) {
        const rowData = cell.getData();
        const usedByCalculators = rowData.used_by_calculators || [];
        const calcUsage = usedByCalculators.find(c => c.calculator === calculatorName);

        if (!calcUsage) {
            return `${calculatorName} does not use this parameter`;
        }

        if (calcUsage.override) {
            return `${calculatorName}: $${calcUsage.value.toFixed(2)} (Override)\nBase: $${rowData.base_value.toFixed(2)}\nAdded: ${calcUsage.added_date}`;
        } else {
            return `${calculatorName}: $${calcUsage.value.toFixed(2)} (Base)\nAdded: ${calcUsage.added_date}`;
        }
    }

    /**
     * Create actions column formatter
     */
    createActionsFormatter() {
        return function(cell, formatterParams, onRendered) {
            const container = document.createElement('div');
            container.style.display = 'flex';
            container.style.gap = '4px';
            container.style.justifyContent = 'center';

            // Edit button
            const editBtn = document.createElement('button');
            editBtn.className = 'action-btn-small';
            editBtn.innerHTML = '<i class="fas fa-edit"></i>';
            editBtn.title = 'Edit';
            editBtn.onclick = (e) => {
                e.stopPropagation();
                // Open edit modal
            };

            // History button
            const historyBtn = document.createElement('button');
            historyBtn.className = 'action-btn-small';
            historyBtn.innerHTML = '<i class="fas fa-history"></i>';
            historyBtn.title = 'View History';
            historyBtn.onclick = (e) => {
                e.stopPropagation();
                // Open history modal
            };

            container.appendChild(editBtn);
            container.appendChild(historyBtn);

            return container;
        };
    }

    /**
     * Enable advanced Tabulator enhancements
     */
    enableAdvancedFeatures(table) {
        // 1. Advanced Filtering (from tabulator-enhancements.js)
        if (window.AdvancedFilterSystem) {
            this.filterSystem = new AdvancedFilterSystem(this);
        }

        // 2. Saved Presets (from tabulator-enhancements.js)
        if (window.TabulatorPresets) {
            this.presets = new TabulatorPresets(this);
        }

        // 3. Bulk Actions Menu (from tabulator-enhancements.js)
        if (window.BulkActionsMenu) {
            this.bulkActions = new BulkActionsMenu(this, 'catalog-bulk-menu');
        }

        // 4. History Tracking (from tabulator-enhancements.js)
        if (window.TabulatorHistory) {
            this.history = new TabulatorHistory(this);
        }

        // 5. Export Options (from tabulator-enhancements.js)
        if (window.TabulatorExport) {
            this.export = new TabulatorExport(this);
        }

        console.log('[Catalog] Advanced features enabled');
    }

    /**
     * Apply stored row tags on data load
     */
    applyStoredTags() {
        const table = this.tables['parameterMatrix'];
        if (!table) return;

        const tags = JSON.parse(localStorage.getItem('catalog_parameter_tags') || '{}');
        
        table.getRows().forEach(row => {
            const paramId = row.getData().parameter_id;
            const tagColor = tags[paramId];
            
            if (tagColor) {
                row.getElement().classList.add(`tagged-row-${tagColor}`);
            }
        });
    }

    /**
     * Get table instance by key
     */
    getTable(key) {
        return this.tables[key];
    }
}
```

---

## Data Flow

### 1. Load Data from PostgreSQL

```javascript
// catalog-api.js
class CatalogAPI {
    constructor(baseURL) {
        this.baseURL = baseURL || '/api/calculator/catalog';
    }

    /**
     * Get all parameters with calculator usage
     */
    async getParameters(filters = {}) {
        const params = new URLSearchParams(filters);
        const response = await fetch(`${this.baseURL}/parameters?${params}`);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch parameters: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Update base value
     */
    async updateBaseValue(parameterId, newValue, reason) {
        const response = await fetch(`${this.baseURL}/parameters/${parameterId}/base`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ value: newValue, reason: reason })
        });

        return await response.json();
    }

    /**
     * Create calculator override
     */
    async createOverride(parameterId, calculatorName, value, reason) {
        const response = await fetch(`${this.baseURL}/overrides`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                parameter_id: parameterId,
                calculator_name: calculatorName,
                override_value: value,
                override_reason: reason
            })
        });

        return await response.json();
    }

    /**
     * Bulk update parameters
     */
    async bulkUpdate(parameterIds, operation, value, mode) {
        const response = await fetch(`${this.baseURL}/bulk-update`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                parameter_ids: parameterIds,
                operation: operation, // 'set', 'increase', 'decrease', 'multiply'
                value: value,
                mode: mode // 'base', 'selective', 'force'
            })
        });

        return await response.json();
    }

    /**
     * Get parameter history
     */
    async getHistory(parameterId) {
        const response = await fetch(`${this.baseURL}/parameters/${parameterId}/history`);
        return await response.json();
    }
}
```

### 2. Transform Data for Tabulator

```javascript
// catalog.js
class CalculatorCatalogModule {
    async loadParameters() {
        try {
            // Fetch from API
            const data = await this.api.getParameters(this.currentFilters);

            // Transform for Tabulator
            const transformedData = data.map(param => {
                const row = {
                    parameter_id: param.id,
                    parameter_name: param.parameter_name,
                    category: param.category,
                    subcategory: param.subcategory,
                    base_value: param.base_value,
                    value_unit: param.value_unit,
                    total_usage_count: param.total_usage_count,
                    used_by_calculators: param.used_by_calculators,
                    description: param.description
                };

                // Add calculator columns dynamically
                const usedBy = param.used_by_calculators || [];
                usedBy.forEach(calc => {
                    row[`calc_${calc.calculator}`] = calc.value;
                });

                return row;
            });

            // Load into table
            this.tabulatorHelper.getTable('parameterMatrix').setData(transformedData);

        } catch (error) {
            console.error('[Catalog] Failed to load parameters:', error);
            this.showToast('Failed to load parameters', 'error');
        }
    }
}
```

---

## Key Features (Using Existing Tabulator Enhancements)

### 1. Row Tagging System ✅
**Already Built:** `tabulator-functions.js`
- Green/Orange/Red tagging
- Tag button formatter
- Bulk tag operations
- Persistent storage in localStorage

**Usage:**
```javascript
// Tag column already configured
{
    title: "Tag",
    formatter: window.TabulatorFunctions.createTagButtonFormatter(
        'parameter_id',
        null,
        'catalog_parameter_tags'
    )
}
```

### 2. Bulk Actions Menu ✅
**Already Built:** `tabulator-enhancements.js` - `BulkActionsMenu`
- Shows when rows selected
- Custom action buttons
- Selection counter

**Usage:**
```javascript
this.bulkActions = new BulkActionsMenu(this, 'catalog-bulk-menu');
```

### 3. Saved Presets (Views) ✅
**Already Built:** `tabulator-enhancements.js` - `TabulatorPresets`
- Save current view (filters, sort, columns)
- Load preset by name
- Delete presets
- Stored in localStorage

**Usage:**
```javascript
// Save current view
this.presets.savePreset('My Custom View', 'parameterMatrix');

// Load preset
this.presets.loadPreset('My Custom View', 'parameterMatrix');
```

### 4. Advanced Filtering ✅
**Already Built:** `tabulator-enhancements.js` - `AdvancedFilterSystem`
- Multi-column filters
- Date range filters
- Custom filter functions

**Usage:**
```javascript
// Apply multi-filter
this.filterSystem.applyMultiFilter('parameterMatrix', [
    { field: 'category', type: '=', value: 'Setup' },
    { field: 'base_value', type: '>', value: 10 }
]);
```

### 5. Export Options ✅
**Already Built:** `tabulator-enhancements.js` - `TabulatorExport`
- CSV, JSON, XLSX export
- Custom export presets
- Filtered data export

**Usage:**
```javascript
// Export to CSV
this.export.exportData('parameterMatrix', 'csv', 'calculator-catalog.csv');

// Export to Excel
this.export.exportData('parameterMatrix', 'xlsx', 'calculator-catalog.xlsx');
```

### 6. History Tracking ✅
**Already Built:** `tabulator-enhancements.js` - `TabulatorHistory`
- Track all edits
- Undo/redo functionality
- History modal viewer

**Usage:**
```javascript
this.history = new TabulatorHistory(this);
```

### 7. Inline Editing ✅
**Built-in Tabulator Feature**
- Cell editor on click
- Number/text/select editors
- Validation on change
- `cellEdited` callback

### 8. Theme Adaptation ✅
**Already Built:** `tabulator-theme-adapter.js`
- Module colors from manifest.json
- Dark theme with primary/secondary colors
- Automatic CSS injection

### 9. Mobile Responsive ✅
**Already Built:** `tabulator-enhancements.js` - `MobileResponsiveLayout`
- Switches to card layout on mobile
- Touch-friendly interactions
- Swipe actions

### 10. Toast Notifications ✅
**Already Built:** `tabulator-toast-system.js`
- Success/error/warning/info toasts
- Auto-dismiss
- Queue system

---

## Implementation Timeline

### Week 1: Core Table
**Days 1-2: Database Setup**
- Run SQL migration script
- Load extracted JSON data
- Verify data structure

**Days 3-5: Tabulator Integration**
- Create `catalog-tabulator.js`
- Configure parameter matrix table
- Test with real data

**Days 6-7: Basic API**
- Flask routes for GET /parameters
- Flask routes for PUT /parameters/:id/base
- Test data loading

### Week 2: Editing & Updates
**Days 1-3: Inline Editing**
- Enable cell editors
- Wire up cellEdited callbacks
- Validate inputs

**Days 4-5: Bulk Operations**
- Bulk update modal
- Update propagation (3 modes)
- Bulk validation

**Days 6-7: Override System**
- Create override modal
- Reset overrides
- Override indicators in cells

### Week 3: Advanced Features
**Days 1-2: Detail Panel**
- Slide-out parameter details
- Usage statistics
- Value distribution chart

**Days 3-4: Comparison View**
- Side-by-side calculator comparison
- Difference highlighting
- Align values action

**Days 5-7: Analytics Dashboard**
- Parameter usage charts
- Override frequency
- Change timeline

### Week 4: Polish & Testing
**Days 1-2: UI/UX Polish**
- Responsive design
- Loading states
- Error handling

**Days 3-4: Testing**
- Test bulk updates
- Test override propagation
- Test export/import

**Days 5-7: Documentation**
- User guide
- Developer docs
- API documentation

---

## Manifest Configuration

```json
{
    "moduleId": "calculator-catalog",
    "name": "Calculator Catalog",
    "version": "1.0.0",
    "icon": "fa-calculator",
    "colors": {
        "primary": "#FF6B35",
        "secondary": "#F7931E",
        "hover": "#E55D2A"
    },
    "routes": [
        {
            "path": "/catalog",
            "label": "Parameter Matrix",
            "icon": "fa-table"
        },
        {
            "path": "/catalog/analytics",
            "label": "Analytics",
            "icon": "fa-chart-line"
        },
        {
            "path": "/catalog/comparison",
            "label": "Compare",
            "icon": "fa-columns"
        }
    ],
    "dependencies": [
        "tabulator-tables@5.5.0",
        "tabulator-functions.js",
        "tabulator-enhancements.js",
        "tabulator-theme-adapter.js"
    ],
    "apiEndpoints": [
        "/api/calculator/catalog/parameters",
        "/api/calculator/catalog/overrides",
        "/api/calculator/catalog/history",
        "/api/calculator/catalog/bulk-update"
    ]
}
```

---

## CSS Styling (Reuses Existing)

**Already Have:**
- `tabulator-enhancements.css` (1052 lines)
- Dark theme with module colors
- Row tagging styles
- Bulk actions menu styles
- Modal styles
- Toast styles

**Need to Add (Minimal):**
```css
/* Calculator cell color coding */
.tabulator-cell.calc-cell-base {
    background: rgba(46, 125, 50, 0.15) !important;
    border-left: 3px solid #2e7d32 !important;
}

.tabulator-cell.calc-cell-override {
    background: rgba(230, 81, 0, 0.15) !important;
    border-left: 3px solid #e65100 !important;
}

.tabulator-cell.calc-cell-unused {
    background: rgba(100, 100, 100, 0.1) !important;
    color: #666 !important;
}

/* Detail panel slide-out */
.detail-panel {
    position: fixed;
    right: -500px;
    top: 0;
    width: 500px;
    height: 100vh;
    background: var(--bg-card);
    border-left: 1px solid var(--border-color);
    transition: right 0.3s ease;
    z-index: 1000;
}

.detail-panel.open {
    right: 0;
}
```

---

## API Routes (Flask)

```python
# backend/api/catalog_routes.py
from flask import Blueprint, jsonify, request
from models.catalog_models import (
    CalculatorPricingParameter,
    CalculatorParameterOverride,
    CalculatorParameterHistory
)
from services.catalog_service import CatalogService

catalog_bp = Blueprint('catalog', __name__, url_prefix='/api/calculator/catalog')
catalog_service = CatalogService()

@catalog_bp.route('/parameters', methods=['GET'])
def get_parameters():
    """Get all parameters with calculator usage"""
    filters = {
        'category': request.args.get('category'),
        'calculator': request.args.get('calculator'),
        'search': request.args.get('search')
    }
    
    parameters = catalog_service.get_parameters(filters)
    return jsonify(parameters)

@catalog_bp.route('/parameters/<int:param_id>/base', methods=['PUT'])
def update_base_value(param_id):
    """Update base value"""
    data = request.json
    new_value = data.get('value')
    reason = data.get('reason')
    
    result = catalog_service.update_base_value(param_id, new_value, reason)
    return jsonify(result)

@catalog_bp.route('/overrides', methods=['POST'])
def create_override():
    """Create calculator-specific override"""
    data = request.json
    result = catalog_service.create_override(
        data['parameter_id'],
        data['calculator_name'],
        data['override_value'],
        data.get('override_reason')
    )
    return jsonify(result)

@catalog_bp.route('/bulk-update', methods=['POST'])
def bulk_update():
    """Bulk update parameters"""
    data = request.json
    result = catalog_service.bulk_update(
        data['parameter_ids'],
        data['operation'],
        data['value'],
        data.get('mode', 'base')
    )
    return jsonify(result)

@catalog_bp.route('/parameters/<int:param_id>/history', methods=['GET'])
def get_history(param_id):
    """Get parameter change history"""
    history = catalog_service.get_history(param_id)
    return jsonify(history)
```

---

## Summary

**What You Get:**
- ✅ Reuses 100% of existing Tabulator infrastructure
- ✅ 10 advanced features already built (enhancements.js)
- ✅ Module color theming (theme-adapter.js)
- ✅ Row tagging system (functions.js)
- ✅ Dark theme styling (enhancements.css)
- ✅ Proven in 3 production modules
- ✅ 4-week timeline (vs 8-12 weeks for new framework)

**Timeline:**
- Week 1: Core table + API
- Week 2: Editing + bulk operations
- Week 3: Advanced features
- Week 4: Polish + testing

**Next Steps:**
1. Create SQL migration script
2. Build `catalog-tabulator.js` configuration
3. Create Flask API routes
4. Test with extracted JSON data

Ready to start building?
