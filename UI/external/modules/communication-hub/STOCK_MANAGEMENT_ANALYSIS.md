# Stock Management Usage Analytics - Structure Analysis

**Analysis Date:** November 10, 2025  
**Reference Module:** Stock Management v4.1.0  
**Purpose:** Document structure for Communication Hub implementation

---

## 📊 USAGE ANALYTICS DASHBOARD STRUCTURE

### 1. HTML LAYOUT PATTERN

The Usage Analytics tab follows this structure (from `stock-management.js` lines 838-951):

```html
<div class="module-dashboard">
    <!-- 1. CARD HEADER (Title + Subtitle) -->
    <div class="dashboard-card">
        <div class="card-header">
            <div class="header-left" style="width: 100%; display: flex; flex-direction: column; gap: 8px; text-align: center;">
                <h3 class="card-title" style="font-size: 24px; margin: 0;">
                    <i class="fas fa-chart-line"></i> Usage Analytics
                </h3>
                <div class="card-subtitle" style="margin: 0;">
                    Stock consumption trends and patterns
                </div>
            </div>
        </div>
    </div>
    
    <!-- 2. SUMMARY METRICS (4 stat cards) -->
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-icon primary">
                <i class="fas fa-boxes"></i>
            </div>
            <div class="stat-content">
                <div class="stat-label">Total Stocks Used</div>
                <div class="stat-value" id="total-stocks-used">-</div>
            </div>
        </div>
        <!-- ... 3 more stat-cards ... -->
    </div>
    
    <!-- 3. TOOLBAR (Period Selector + Refresh Button) -->
    <div class="bulk-operations-toolbar" style="display: flex; align-items: center; gap: 12px; padding: 16px 20px; background: #1a1f2e; border-bottom: 1px solid #2a3142; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <select id="usage-period-selector" class="form-control" style="...">
                <option value="30">Last 30 Days</option>
                <option value="90" selected>Last 90 Days</option>
                <option value="180">Last 180 Days</option>
                <option value="365">Last Year</option>
            </select>
            <button class="btn btn-primary" id="usage-refresh-btn" onclick="...">
                <i class="fas fa-sync-alt"></i> Refresh
            </button>
        </div>
    </div>
    
    <!-- 4. DATA CARD (with 3 states: ready/loading/table) -->
    <div class="dashboard-card">
        <div class="card-header">
            <h3 class="card-title">
                <i class="fas fa-chart-bar"></i> Usage Analytics Data
            </h3>
        </div>
        <div class="card-content">
            <!-- State 1: Ready (instructions) -->
            <div id="analytics-ready" class="ready-state" style="...">
                <i class="fas fa-info-circle"></i>
                <p>Click the <strong>Refresh</strong> button to load usage analytics data</p>
            </div>
            
            <!-- State 2: Loading -->
            <div id="analytics-loading" class="loading-state" style="display: none;">
                <i class="fas fa-spinner fa-spin"></i> Loading analytics...
            </div>
            
            <!-- State 3: Tabulator Table -->
            <div id="analytics-table-container" style="display: none; min-height: 400px;"></div>
        </div>
    </div>
</div>
```

---

## 🎨 CSS STYLING SYSTEM

### A. UI Standards (`ui-standards.css`)

Stock Management uses standardized CSS classes from `ui-standards.css`:

**1. Layout Containers:**
```css
.module-dashboard { /* Main container */ }
.dashboard-card { /* Card wrapper */ }
.card-header { /* Card header */ }
.card-content { /* Card body */ }
```

**2. Stat Cards Grid:**
```css
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--space-4);
    margin-bottom: var(--space-5);
}

.stat-card {
    background: var(--card-background);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    padding: var(--space-4);
    display: flex;
    align-items: center;
    gap: var(--space-3);
}

.stat-icon {
    width: 48px;
    height: 48px;
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
}

.stat-icon.primary { background: rgba(0, 120, 212, 0.2); color: #0078d4; }
.stat-icon.success { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.stat-icon.warning { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
.stat-icon.danger { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
.stat-icon.info { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }

.stat-content {
    flex: 1;
}

.stat-label {
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
    margin-bottom: var(--space-1);
}

.stat-value {
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-bold);
    color: var(--text-primary);
}
```

**3. CSS Variables (used throughout):**
```css
:root {
    /* Spacing (8px base) */
    --space-1: 4px;
    --space-2: 8px;
    --space-3: 12px;
    --space-4: 16px;
    --space-5: 20px;
    --space-6: 24px;

    /* Typography */
    --font-size-xs: 11px;
    --font-size-sm: 13px;
    --font-size-base: 14px;
    --font-size-md: 16px;
    --font-size-lg: 18px;
    --font-size-xl: 24px;
    --font-size-2xl: 28px;

    /* Border Radius */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
    --radius-xl: 16px;

    /* Colors (from theme) */
    --card-background: #161b22;
    --bg-secondary: #0d1117;
    --border-default: #30363d;
    --text-primary: #e6edf3;
    --text-secondary: #7d8590;
}
```

### B. Tabulator Enhancements (`tabulator-enhancements.css`)

**1. Row Tagging:**
```css
.action-btn-tag {
    background: #6c757d;
    border: 2px solid #6c757d;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    cursor: pointer;
}

.action-btn-tag.tag-green { background: #2e7d32; }
.action-btn-tag.tag-orange { background: #e65100; }
.action-btn-tag.tag-red { background: #c62828; }

.tabulator-row.tagged-row-green {
    background: rgba(46, 125, 50, 0.1) !important;
    border-left: 4px solid #2e7d32 !important;
}
```

**2. Cell Popup:**
```css
.cell-popup {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 80%;
    max-width: 1000px;
    max-height: 80vh;
    background: var(--bg-card, #1e1e1e);
    border: 1px solid var(--border-color, #444);
    border-radius: 8px;
}
```

### C. Toast Notifications (`tabulator-toast.css`)

**Position: Bottom-left**

```css
.toast-container {
    position: fixed;
    bottom: var(--space-4, 20px);
    left: var(--space-4, 20px);
    z-index: 100000;
    display: flex;
    flex-direction: column-reverse; /* Stack from bottom up */
    gap: var(--space-2, 10px);
    max-width: 400px;
}

.toast {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
    padding: var(--space-3, 12px) var(--space-4, 16px);
    background: var(--card-background, #2d2d2d);
    border: 1px solid var(--border-default, #444);
    border-radius: var(--border-radius-md, 6px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    opacity: 0;
    transform: translateX(-400px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.toast-show { opacity: 1; transform: translateX(0); }
.toast-hide { opacity: 0; transform: translateX(-400px); }

.toast-success { border-left: 4px solid var(--success-color, #28a745); }
.toast-error { border-left: 4px solid var(--error-color, #dc3545); }
.toast-warning { border-left: 4px solid var(--warning-color, #ffc107); }
.toast-info { border-left: 4px solid var(--info-color, #17a2b8); }
```

---

## 🔧 TABULATOR INITIALIZATION PATTERN

### Method 1: Direct Initialization (Stock Management Main)

From `stock-management.js` lines 1022-1109:

```javascript
renderUsageTable(data) {
    const container = document.getElementById('analytics-table-container');
    if (!container) {
        console.warn('[WARN] Cannot find container: analytics-table-container');
        return;
    }

    // Destroy existing table
    if (this.usageTable) {
        this.usageTable.destroy();
    }

    // Create Tabulator
    this.usageTable = new Tabulator(container, {
        data: data,
        layout: "fitDataStretch",
        pagination: "local",
        paginationSize: 25,
        paginationSizeSelector: [10, 25, 50, 100],
        movableColumns: true,
        resizableColumns: true,
        height: "500px",
        placeholder: "No usage data available",
        
        columns: [
            {
                title: "Stock ID",
                field: "StockID",
                width: 120,
                headerSort: true,
                headerFilter: "input",
                formatter: function (cell) {
                    return `<span style="font-weight: 600; color: #0078d4;">${cell.getValue()}</span>`;
                }
            },
            {
                title: "Stock Type",
                field: "StockType",
                width: 200,
                headerSort: true,
                headerFilter: "input"
            },
            {
                title: "GSM",
                field: "GSM",
                width: 100,
                headerSort: true,
                hozAlign: "center"
            },
            {
                title: "Dimensions",
                field: "Dimensions",
                width: 150,
                headerSort: true,
                hozAlign: "center"
            },
            {
                title: "Usage Count",
                field: "usage_count",
                width: 130,
                headerSort: true,
                hozAlign: "right",
                formatter: function (cell) {
                    const value = cell.getValue() || 0;
                    return `<span style="font-weight: 700; color: #10b981;">${value.toLocaleString()}</span>`;
                }
            },
            {
                title: "Total Sheets",
                field: "total_quantity",
                width: 140,
                headerSort: true,
                hozAlign: "right",
                formatter: function (cell) {
                    const value = cell.getValue() || 0;
                    return `<span style="font-weight: 700;">${value.toLocaleString()}</span>`;
                }
            }
        ]
    });

    console.log('[TABULATOR] Usage analytics table rendered with', data.length, 'rows');
}
```

**Key Features:**
- ✅ Destroy old instance before creating new
- ✅ Store table reference (`this.usageTable`)
- ✅ Local pagination (25 per page)
- ✅ Movable/resizable columns
- ✅ Header filters on text columns
- ✅ Custom formatters for styling
- ✅ Placeholder message

---

### Method 2: Helper Class Pattern (Tabulator Init)

From `tabulator-init.js` lines 1-638:

```javascript
class StockManagementTabulatorHelper {
    constructor(moduleInstance) {
        this.module = moduleInstance;
        this.themeAdapter = null;
        this.tables = {}; // Store table instances by key
        this.selectedRows = {}; // Track selected rows per table
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
                console.warn('[Tabulator Helper] WARNING: TabulatorFunctions not loaded');
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

            return true;
        } catch (error) {
            console.error('[Tabulator Helper] Initialization failed:', error);
            return false;
        }
    }

    /**
     * Create Reorder Dashboard Tabulator table
     */
    createReorderDashboard(containerId, data) {
        try {
            console.log(`[Tabulator Helper] Creating Reorder Dashboard in #${containerId}`);

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

                    // Data columns...
                    {
                        title: "SKU",
                        field: "sku",
                        width: 120,
                        headerFilter: "input",
                        headerFilterPlaceholder: "Search SKU...",
                        frozen: true
                    },
                    // ... more columns ...
                ],

                // Event handlers
                rowSelectionChanged: (data, rows) => {
                    this.selectedRows['reorder'] = data;

                    if (hasUtilities) {
                        const table = this.tables['reorder'];
                        window.TabulatorFunctions.updateSelectionCount(table, 'reorder-selection-count');
                    }

                    console.log(`[Reorder] ${data.length} rows selected`);
                },

                cellDblClick: (e, cell) => {
                    if (hasUtilities) {
                        window.TabulatorFunctions.showCellPopup(e, cell);
                    }
                },

                dataLoaded: (data) => {
                    console.log(`[Reorder] Data loaded: ${data.length} rows`);

                    if (hasUtilities) {
                        const table = this.tables['reorder'];
                        table.getRows().forEach(row => {
                            window.TabulatorFunctions.applyRowTagFormatter(row, 'sku', 'stock_reorder_tags');
                        });
                    }
                }
            };

            // Create and store table instance
            const table = new Tabulator(`#${containerId}`, tableConfig);
            this.tables['reorder'] = table;

            console.log('[Tabulator Helper] Reorder Dashboard created successfully');
            return table;

        } catch (error) {
            console.error('[Tabulator Helper] Failed to create Reorder Dashboard:', error);
            return null;
        }
    }
}
```

**Helper Pattern Features:**
- ✅ Centralized table management
- ✅ Theme adapter integration
- ✅ Dependency checking
- ✅ Optional utility features (tag buttons, cell popups)
- ✅ Event handler abstraction
- ✅ Multiple table instance storage

---

## 📦 DEPENDENCIES (from manifest.json)

Stock Management declares dependencies in specific order:

```json
{
    "dependencies": [
        "https://cdn.plot.ly/plotly-2.27.0.min.js",
        "https://unpkg.com/tabulator-tables@5.5.2/dist/css/tabulator.min.css",
        "https://unpkg.com/tabulator-tables@5.5.2/dist/js/tabulator.min.js",
        "/js/tabulator-functions.js",
        "/js/tabulator-theme-adapter.js",
        "/js/tabulator-enhancements.js",
        "/css/tabulator-enhancements.css",
        "/external/modules/stock-management/tabulator-init.js"
    ]
}
```

**Order Matters:**
1. **Plotly** - Chart library (optional)
2. **Tabulator CSS** - Base styles
3. **Tabulator JS** - Core library
4. **Tabulator Functions** - Utility library (tag buttons, popups)
5. **Theme Adapter** - Adaptive theming
6. **Enhancements JS** - Additional features
7. **Enhancements CSS** - Enhancement styles
8. **Module-specific Init** - Helper classes

---

## 🔄 DATA FLOW PATTERN

### 1. User Clicks "Refresh" Button

```javascript
// Button onclick handler (line 932)
onclick="stockModule.refreshUsageAnalyticsTab()"
```

### 2. Refresh Method Triggers Load

```javascript
refreshUsageAnalyticsTab() {
    console.log('[REFRESH] Refreshing usage analytics tab...');
    this.loadUsageAnalytics();
}
```

### 3. Load Method Fetches Data

```javascript
async loadUsageAnalytics() {
    console.log(`[LOAD] Loading usage analytics for ${this.currentPeriod} days...`);

    // Show loading state
    const loadingDiv = document.getElementById('analytics-loading');
    const readyDiv = document.getElementById('analytics-ready');
    const tableContainer = document.getElementById('analytics-table-container');

    if (loadingDiv) loadingDiv.style.display = 'block';
    if (readyDiv) readyDiv.style.display = 'none';
    if (tableContainer) tableContainer.style.display = 'none';

    try {
        // Fetch from backend API
        const response = await fetch(
            `${this.backendUrl}/api/stock-management/usage-analytics?days=${this.currentPeriod}&group_by=month`
        );

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        if (result.status !== 'ok') {
            throw new Error(result.message || 'Failed to load usage analytics');
        }

        console.log('[OK] Usage analytics loaded:', result.data.length, 'records');

        // Calculate summary stats
        const data = result.data || [];
        const totalStocks = data.length;
        const totalUsage = data.reduce((sum, item) => sum + (item.usage_count || 0), 0);
        const totalSheets = data.reduce((sum, item) => sum + (item.total_quantity || 0), 0);

        // Fast movers = usage > average
        const avgUsage = totalUsage / (totalStocks || 1);
        const fastMovers = data.filter(item => item.usage_count > avgUsage).length;
        const slowMovers = data.filter(item => item.usage_count < avgUsage).length;

        // Update stat cards
        document.getElementById('total-stocks-used').textContent = totalStocks;
        document.getElementById('total-sheets-used').textContent = totalSheets.toLocaleString();
        document.getElementById('fast-movers-count').textContent = fastMovers;
        document.getElementById('slow-movers-count').textContent = slowMovers;

        // Render Tabulator table
        this.renderUsageTable(data);

        // Update UI state
        if (loadingDiv) loadingDiv.style.display = 'none';
        if (tableContainer) tableContainer.style.display = 'block';

    } catch (error) {
        console.error('[ERROR] Failed to load usage analytics:', error);
        
        // Show error state
        if (loadingDiv) {
            loadingDiv.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Failed to load usage analytics</p>
                    <p class="error-detail">${error.message}</p>
                    <button class="btn btn-primary" onclick="stockModule.refreshUsageAnalyticsTab()">
                        <i class="fas fa-redo"></i> Retry
                    </button>
                </div>
            `;
            loadingDiv.style.display = 'block';
        }
    }
}
```

### 4. Render Method Creates Tabulator

```javascript
renderUsageTable(data) {
    // Destroy old instance
    if (this.usageTable) {
        this.usageTable.destroy();
    }

    // Create new Tabulator instance
    this.usageTable = new Tabulator(container, {
        data: data,
        // ... configuration ...
    });
}
```

---

## 🎯 KEY PATTERNS FOR COMMUNICATION HUB

### ✅ MUST USE:

1. **Three-state loading pattern:**
   - `ready-state` (instructions)
   - `loading-state` (spinner)
   - `table-container` (Tabulator)

2. **Stat cards grid:**
   ```html
   <div class="stats-grid">
       <div class="stat-card">
           <div class="stat-icon primary"><i class="fas fa-inbox"></i></div>
           <div class="stat-content">
               <div class="stat-label">Total Emails</div>
               <div class="stat-value" id="total-emails">-</div>
           </div>
       </div>
   </div>
   ```

3. **Toolbar pattern:**
   ```html
   <div class="bulk-operations-toolbar" style="display: flex; align-items: center; gap: 12px; padding: 16px 20px; background: #1a1f2e; border-bottom: 1px solid #2a3142;">
       <select>...</select>
       <button class="btn btn-primary" onclick="...">
           <i class="fas fa-sync-alt"></i> Refresh
       </button>
   </div>
   ```

4. **Destroy-before-create pattern:**
   ```javascript
   if (this.emailTable) {
       this.emailTable.destroy();
   }
   this.emailTable = new Tabulator(container, {...});
   ```

5. **CSS Variables:**
   - Use `var(--card-background)` not hardcoded colors
   - Use `var(--space-4)` for spacing
   - Use `var(--text-primary)` for text colors

6. **Console logging with prefixes:**
   ```javascript
   console.log('[LOAD] Loading emails...');
   console.log('[TABULATOR] Email table rendered with', data.length, 'rows');
   console.error('[ERROR] Failed to fetch emails:', error);
   ```

### ⚠️ AVOID:

1. Auto-loading data on tab init (causes performance issues)
2. Inline styles without CSS variables
3. Missing destroy() calls before recreating tables
4. Hardcoded colors (use CSS variables from manifest)
5. Missing error states

---

## 📊 RECOMMENDED IMPLEMENTATION FOR COMMUNICATION HUB

### Unified Inbox Tab Structure:

```javascript
initializeUnifiedInboxTab() {
    const tab = this.getSubTabContainer('unified-inbox');
    if (!tab) {
        console.error('[INIT] Could not find unified-inbox container');
        return;
    }

    console.log('[INIT] Initializing Unified Inbox tab...');

    tab.innerHTML = `
        <div class="module-dashboard">
            <!-- Header -->
            <div class="dashboard-card">
                <div class="card-header">
                    <div class="header-left" style="width: 100%; display: flex; flex-direction: column; gap: 8px; text-align: center;">
                        <h3 class="card-title" style="font-size: 24px; margin: 0;">
                            <i class="fas fa-inbox"></i> Unified Inbox
                        </h3>
                        <div class="card-subtitle" style="margin: 0;">
                            All messages from Gmail and Outlook
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Stat Cards -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon primary">
                        <i class="fas fa-envelope"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-label">Total Emails</div>
                        <div class="stat-value" id="total-emails-count">-</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon success">
                        <i class="fab fa-google"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-label">Gmail</div>
                        <div class="stat-value" id="gmail-count">-</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon info">
                        <i class="fab fa-microsoft"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-label">Outlook</div>
                        <div class="stat-value" id="outlook-count">-</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon warning">
                        <i class="fas fa-envelope-open"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-label">Unread</div>
                        <div class="stat-value" id="unread-count">-</div>
                    </div>
                </div>
            </div>
            
            <!-- Toolbar -->
            <div class="bulk-operations-toolbar" style="display: flex; align-items: center; gap: 12px; padding: 16px 20px; background: #1a1f2e; border-bottom: 1px solid #2a3142; margin-bottom: 20px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <select id="account-filter" class="form-control" style="margin: 0; width: auto; padding: 6px 10px;">
                        <option value="all">All Accounts</option>
                        <option value="gmail">Gmail Only</option>
                        <option value="outlook">Outlook Only</option>
                    </select>
                    <select id="email-limit" class="form-control" style="margin: 0; width: auto; padding: 6px 10px;">
                        <option value="50">Show 50</option>
                        <option value="100" selected>Show 100</option>
                        <option value="200">Show 200</option>
                    </select>
                    <button class="btn btn-primary" id="email-refresh-btn" onclick="communicationHub.refreshInbox()" style="padding: 6px 12px; font-size: 12px;">
                        <i class="fas fa-sync-alt"></i> Refresh
                    </button>
                </div>
                
                <div style="margin-left: auto; display: flex; gap: 8px;">
                    <button class="btn btn-secondary" onclick="communicationHub.sendSelectedToAI()" style="padding: 6px 12px; font-size: 12px;">
                        <i class="fas fa-robot"></i> Send Selected to AI
                    </button>
                </div>
            </div>
            
            <!-- Email Table -->
            <div class="dashboard-card">
                <div class="card-header">
                    <h3 class="card-title">
                        <i class="fas fa-list"></i> Email Messages
                    </h3>
                </div>
                <div class="card-content">
                    <!-- Ready State -->
                    <div id="inbox-ready" class="ready-state" style="text-align: center; padding: 40px; color: #9ca3af;">
                        <i class="fas fa-info-circle" style="font-size: 32px; color: #4ec9b0; margin-bottom: 10px; display: block;"></i>
                        <p style="margin: 0; font-size: 16px;">Click the <strong>Refresh</strong> button to load your emails</p>
                        <p style="margin: 5px 0 0 0; font-size: 12px; color: #6b7280;">Select account filter and click Refresh</p>
                    </div>
                    
                    <!-- Loading State -->
                    <div id="inbox-loading" class="loading-state" style="display: none; text-align: center; padding: 40px;">
                        <i class="fas fa-spinner fa-spin" style="font-size: 32px; color: #0078d4; margin-bottom: 10px; display: block;"></i>
                        <p style="margin: 0; font-size: 16px; color: #e5e7eb;">Loading emails...</p>
                    </div>
                    
                    <!-- Table Container -->
                    <div id="email-table-container" style="display: none; min-height: 500px;"></div>
                </div>
            </div>
        </div>
    `;

    // Setup event listeners
    document.getElementById('account-filter')?.addEventListener('change', (e) => {
        this.currentAccountFilter = e.target.value;
    });

    document.getElementById('email-limit')?.addEventListener('change', (e) => {
        this.currentEmailLimit = parseInt(e.target.value);
    });
}
```

---

## 🎉 SUMMARY

**Stock Management provides a complete blueprint for:**

1. ✅ Three-state loading UI (ready/loading/table)
2. ✅ Stat cards grid with icons
3. ✅ Toolbar with filters and refresh button
4. ✅ Tabulator initialization with destroy pattern
5. ✅ CSS variable usage for theming
6. ✅ Console logging standards
7. ✅ Error handling patterns
8. ✅ Event handler registration

**Communication Hub should replicate this EXACT structure for:**
- Unified Inbox tab
- Threads tab
- Search tab

**Already implemented differently:**
- Compose tab (form-based, not table-based)

---

**Next Steps:**
1. Update Communication Hub Unified Inbox to match Stock Management structure
2. Add stat cards grid
3. Add three-state loading pattern
4. Add toolbar with account filter and refresh button
5. Update Tabulator initialization to use destroy-before-create pattern
6. Replace hardcoded styles with CSS variables

---

**Document Version:** 1.0.0  
**Last Updated:** November 10, 2025  
**Status:** Complete Analysis
