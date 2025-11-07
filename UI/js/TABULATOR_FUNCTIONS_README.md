# Tabulator Functions - Utility Library

**Version:** 1.0.0  
**Last Updated:** October 30, 2025  
**File:** `tabulator-functions.js`  
**CSS:** `../css/tabulator-enhancements.css`

## Overview

Centralized utility library for Tabulator tables providing row tagging, cell popups, bulk operations, column management, and enhanced selection features.

---

## Installation

### 1. Include in HTML

```html
<!-- Include Tabulator library first -->
<link href="https://unpkg.com/tabulator-tables@5.5.0/dist/css/tabulator.min.css" rel="stylesheet">
<script src="https://unpkg.com/tabulator-tables@5.5.0/dist/js/tabulator.min.js"></script>

<!-- Include Tabulator Functions -->
<link href="css/tabulator-enhancements.css" rel="stylesheet">
<script src="js/tabulator-functions.js"></script>
```

### 2. Include in Module

```javascript
// In your module's manifest.json
{
    "dependencies": [
        "https://unpkg.com/tabulator-tables@5.5.0/dist/css/tabulator.min.css",
        "https://unpkg.com/tabulator-tables@5.5.0/dist/js/tabulator.min.js",
        "css/tabulator-enhancements.css",
        "js/tabulator-functions.js"
    ]
}
```

---

## Features

### 1. Row Tagging System

Color-code rows with green/orange/red tags for visual organization.

**Basic Usage:**

```javascript
// Initialize table with row tagging
const table = new Tabulator('#my-table', {
    // ... other options
    rowFormatter: function(row) {
        window.TabulatorFunctions.applyRowTagFormatter(row, 'id', 'my_module_tags');
    },
    columns: [
        {
            title: "Tag",
            field: "actions",
            width: 60,
            frozen: true,
            headerSort: false,
            hozAlign: "center",
            formatter: window.TabulatorFunctions.createTagButtonFormatter('id', table, 'my_module_tags')
        },
        // ... other columns
    ]
});
```

**API:**

```javascript
// Get row tag
const tag = window.TabulatorFunctions.getRowTag(rowId, storageKey);

// Set row tag
window.TabulatorFunctions.setRowTag(rowId, 'green', storageKey);

// Remove row tag
window.TabulatorFunctions.removeRowTag(rowId, storageKey);

// Toggle tag (cycle: untagged → green → orange → red → untagged)
window.TabulatorFunctions.toggleRowTag(event, rowId, table, storageKey);

// Bulk tag selected rows
const count = window.TabulatorFunctions.bulkTagRows(table, 'green', 'id', storageKey);
```

**Parameters:**
- `rowId` - Unique identifier for the row
- `storageKey` - localStorage key (default: 'row_tags')
- `table` - Tabulator instance
- `tagColor` - 'green', 'orange', 'red', or null to clear

---

### 2. Cell Popup Viewer

Double-click any cell to view full content in draggable popup.

**Basic Usage:**

```javascript
// Enable cell popup on double-click
table.on("cellDblClick", function(e, cell) {
    window.TabulatorFunctions.showCellPopup(e, cell);
});
```

**Features:**
- Shows up to 50,000 characters
- Displays character count and token estimate
- Draggable popup window
- Copy to clipboard functionality

**API:**

```javascript
// Show popup
window.TabulatorFunctions.showCellPopup(event, cell);

// Close popup
window.TabulatorFunctions.closeCellPopup();

// Copy content
window.TabulatorFunctions.copyCellContent(fieldName);
```

---

### 3. View Full Row

Display entire row data as formatted JSON popup.

**Basic Usage:**

```javascript
// Add view row button to actions column
{
    title: "Actions",
    field: "actions",
    formatter: function(cell) {
        const row = cell.getRow().getData();
        return `
            <button onclick="window.TabulatorFunctions.viewFullRow(window.myTable, '${row.id}', 'id')">
                View Full Row
            </button>
        `;
    }
}
```

**API:**

```javascript
// View full row
window.TabulatorFunctions.viewFullRow(table, rowId, idField);

// Copy full row data
window.TabulatorFunctions.copyFullRowData();
```

---

### 4. Bulk Operations

Select and perform operations on multiple rows.

**Basic Usage:**

```javascript
// Enable row selection
const table = new Tabulator('#my-table', {
    selectable: true,
    selectableRangeMode: "click",  // Shift+click range selection
    columns: [
        {
            title: "Select",
            formatter: "rowSelection",
            titleFormatter: "rowSelection",
            hozAlign: "center",
            headerSort: false,
            width: 60,
            frozen: true
        },
        // ... other columns
    ]
});

// Setup selection counter
window.TabulatorFunctions.setupSelectionCounter(table, 'selection-count');

// Enhanced checkbox click (click anywhere in cell to toggle)
window.TabulatorFunctions.setupEnhancedCheckboxClick(table);
```

**Bulk Delete:**

```javascript
async function bulkDelete() {
    const result = await window.TabulatorFunctions.bulkDeleteRows(
        table,
        async (rowData) => {
            // Your delete logic here
            const response = await fetch('/api/delete', {
                method: 'POST',
                body: JSON.stringify({ ids: rowData.map(r => r.id) })
            });
            const result = await response.json();
            return { success: result.success, count: rowData.length };
        },
        'Are you sure you want to delete these rows?'
    );
    
    if (result.success) {
        console.log(`Deleted ${result.count} rows`);
    }
}
```

---

### 5. Column Management

Hide/show columns and create custom header menus.

**Basic Usage:**

```javascript
// Add header menu to all columns
const table = new Tabulator('#my-table', {
    headerMenu: window.TabulatorFunctions.createColumnHeaderMenu(),
    columns: [
        // ... columns
    ]
});

// Show all hidden columns
function showAllColumns() {
    window.TabulatorFunctions.showAllColumns(table);
}

// Hide specific column
function hideColumn(fieldName) {
    window.TabulatorFunctions.hideColumn(table, fieldName);
}
```

**Column Title with Hide Button:**

```javascript
{
    title: "Column Name",
    field: "field_name",
    titleFormatter: window.TabulatorFunctions.columnTitleWithHideButton
}
```

**Header Menu Features:**
- Hide Column
- Show All Columns
- Collapse Column (vertical text)
- Expand Column

---

## Complete Example

```javascript
// Initialize table with all features
const myTable = new Tabulator('#my-table', {
    // Selection
    selectable: true,
    selectableRangeMode: "click",
    
    // Persistence
    persistenceMode: "local",
    persistence: {
        sort: true,
        filter: true,
        columns: ["width", "visible"]
    },
    
    // Row formatter for tags
    rowFormatter: function(row) {
        window.TabulatorFunctions.applyRowTagFormatter(row, 'id', 'my_tags');
    },
    
    // Header menu
    headerMenu: window.TabulatorFunctions.createColumnHeaderMenu(),
    
    columns: [
        {
            title: "Select",
            formatter: "rowSelection",
            titleFormatter: "rowSelection",
            hozAlign: "center",
            width: 60,
            frozen: true,
            headerSort: false
        },
        {
            title: "#",
            field: "row_number",
            width: 50,
            frozen: true,
            headerSort: false,
            hozAlign: "center",
            formatter: function(cell) {
                return cell.getRow().getPosition();
            },
            cssClass: "row-number-column"
        },
        {
            title: "Tag",
            field: "actions",
            width: 60,
            frozen: true,
            headerSort: false,
            hozAlign: "center",
            cssClass: "tag-column-boundary",
            formatter: window.TabulatorFunctions.createTagButtonFormatter('id', myTable, 'my_tags')
        },
        {
            title: "Name",
            field: "name",
            headerFilter: "input",
            titleFormatter: window.TabulatorFunctions.columnTitleWithHideButton
        },
        // ... more columns
    ]
});

// Enable cell popup on double-click
myTable.on("cellDblClick", function(e, cell) {
    window.TabulatorFunctions.showCellPopup(e, cell);
});

// Setup selection counter
window.TabulatorFunctions.setupSelectionCounter(myTable, 'selection-count');

// Enhanced checkbox click
window.TabulatorFunctions.setupEnhancedCheckboxClick(myTable);

// Store table reference globally
window.myTable = myTable;
```

**HTML:**

```html
<div>
    <div style="margin-bottom: 16px;">
        <span id="selection-count" class="selection-count">0 selected</span>
        
        <button onclick="bulkTagRows('green')">
            <i class="fas fa-tag"></i> Tag Green
        </button>
        <button onclick="bulkTagRows('orange')">
            <i class="fas fa-tag"></i> Tag Orange
        </button>
        <button onclick="bulkTagRows('red')">
            <i class="fas fa-tag"></i> Tag Red
        </button>
        <button onclick="bulkTagRows(null)">
            <i class="fas fa-tag"></i> Clear Tags
        </button>
        
        <button onclick="showAllColumns()">
            <i class="fas fa-eye"></i> Show All Columns
        </button>
        
        <button onclick="bulkDelete()">
            <i class="fas fa-trash"></i> Delete Selected
        </button>
    </div>
    
    <div id="my-table"></div>
</div>
```

**JavaScript Functions:**

```javascript
function bulkTagRows(tagColor) {
    const count = window.TabulatorFunctions.bulkTagRows(
        window.myTable, 
        tagColor, 
        'id', 
        'my_tags'
    );
    console.log(`Tagged ${count} rows`);
}

function showAllColumns() {
    window.TabulatorFunctions.showAllColumns(window.myTable);
}

async function bulkDelete() {
    const result = await window.TabulatorFunctions.bulkDeleteRows(
        window.myTable,
        async (rowData) => {
            // Your delete API call
            return { success: true, count: rowData.length };
        }
    );
}
```

---

## Storage Keys

Each module should use a unique localStorage key for tags to avoid conflicts:

```javascript
// Good - module-specific
'database_visualizer_tags'
'salesforce_tags'
'stock_manager_tags'

// Bad - generic (conflicts possible)
'row_tags'
'tags'
```

---

## CSS Customization

Override default styles in your module CSS:

```css
/* Custom tag colors */
.action-btn-tag.tag-green {
    background: #00ff00;
}

/* Custom popup styling */
.cell-popup {
    max-width: 1200px;
    border-radius: 12px;
}

/* Custom tagged row backgrounds */
.tabulator-row.tagged-row-green {
    background: rgba(0, 255, 0, 0.1) !important;
}
```

---

## API Reference

### Row Tagging

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `getRowTag(rowId, storageKey)` | rowId: string, storageKey: string | string\|null | Get tag color for row |
| `setRowTag(rowId, color, storageKey)` | rowId: string, color: string\|null, storageKey: string | void | Set tag color |
| `removeRowTag(rowId, storageKey)` | rowId: string, storageKey: string | void | Remove tag |
| `toggleRowTag(event, rowId, table, storageKey)` | event: Event, rowId: string, table: Tabulator, storageKey: string | string | Toggle through tag colors |
| `bulkTagRows(table, tagColor, idField, storageKey)` | table: Tabulator, tagColor: string\|null, idField: string, storageKey: string | number | Bulk tag selected rows |
| `applyRowTagFormatter(row, idField, storageKey)` | row: TabulatorRow, idField: string, storageKey: string | void | Row formatter function |
| `createTagButtonFormatter(idField, table, storageKey)` | idField: string, table: Tabulator, storageKey: string | Function | Create tag button formatter |

### Cell Popup

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `showCellPopup(event, cell)` | event: Event, cell: TabulatorCell | void | Show cell content popup |
| `closeCellPopup()` | none | void | Close popup |
| `copyCellContent(fieldName)` | fieldName: string | void | Copy content to clipboard |

### Full Row Viewer

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `viewFullRow(table, rowId, idField)` | table: Tabulator, rowId: string, idField: string | void | View full row as JSON |
| `copyFullRowData()` | none | void | Copy full row JSON |

### Bulk Operations

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `bulkDeleteRows(table, deleteCallback, confirmMessage)` | table: Tabulator, deleteCallback: Function, confirmMessage: string | Promise<Object> | Delete selected rows |
| `updateSelectionCount(table, elementId)` | table: Tabulator, elementId: string | void | Update selection count display |

### Column Management

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `columnTitleWithHideButton(cell)` | cell: TabulatorCell | string | Column title with hide button |
| `hideColumn(table, fieldName)` | table: Tabulator, fieldName: string | void | Hide column |
| `showAllColumns(table)` | table: Tabulator | void | Show all columns |
| `createColumnHeaderMenu()` | none | Array | Create header menu config |

### Selection Enhancements

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `setupEnhancedCheckboxClick(table)` | table: Tabulator | void | Enable click anywhere in checkbox cell |
| `setupSelectionCounter(table, elementId)` | table: Tabulator, elementId: string | void | Auto-update selection count |

---

## Browser Compatibility

- Chrome/Edge: 90+
- Firefox: 88+
- Safari: 14+

Requires:
- localStorage support
- Clipboard API (for copy functions)
- ES6+ (arrow functions, const/let, template literals)

---

## Troubleshooting

### Tags not persisting
**Issue:** Tags disappear after page reload  
**Solution:** Verify localStorage is enabled and storageKey is consistent

### Popup not appearing
**Issue:** Double-click doesn't show popup  
**Solution:** Ensure `cellDblClick` event is attached after table initialization

### Selection not working
**Issue:** Checkboxes don't toggle  
**Solution:** Call `setupEnhancedCheckboxClick(table)` after table creation

### Styles not applying
**Issue:** Tags/popups look wrong  
**Solution:** Include `tabulator-enhancements.css` after Tabulator CSS

---

## Version History

**1.0.0** (October 30, 2025)
- Initial release
- Row tagging system
- Cell popup viewer
- Bulk operations
- Column management
- Enhanced selection

---

**Last Updated:** October 30, 2025  
**Status:** Production Ready
