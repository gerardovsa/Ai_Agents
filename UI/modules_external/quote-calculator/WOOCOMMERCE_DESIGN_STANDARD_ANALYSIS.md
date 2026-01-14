# WooCommerce Module Design Standard Analysis
**Created:** December 20, 2025  
**Purpose:** Extract design patterns from WooCommerce Orders tab as reference for standardizing UI across modules

---

## Executive Summary

The WooCommerce module represents the **gold standard** for tabulator table design in this system. Key differentiators:

✅ **Inline CSS in formatters** - No external stylesheet, all styling in JS  
✅ **White text on dark background** (`color: #ffffff`)  
✅ **Comprehensive headerFilter on every column**  
✅ **Status badges with vibrant colors** and high contrast  
✅ **Multi-column data display** (Contact column shows email + phone)  
✅ **Smart filtering** with custom headerFilterFunc  
✅ **Action buttons** with inline styles  

---

## 1. Tabulator Configuration Pattern

### **Table Initialization**
```javascript
window.wooOrdersTable = new Tabulator(container, {
    data: orders,
    layout: "fitDataStretch",              // ← Stretch columns to fill width
    pagination: "local",                   // ← Client-side pagination
    paginationSize: 25,
    paginationSizeSelector: [10, 25, 50, 100],
    movableColumns: true,                  // ← Drag to reorder
    resizableColumns: true,                // ← Drag to resize
    placeholder: "No orders found",
    columns: [...]
});
```

**Key Settings:**
- `fitDataStretch` - columns fill available width
- Local pagination - 25 rows per page default
- User control over page size (10/25/50/100)
- Movable and resizable columns for flexibility

---

## 2. Column Pattern: Header + Filter + Formatter

### **Standard Column Structure**
```javascript
{
    title: "Order ID",                     // ← Column header text
    field: "id",                           // ← Data field name
    width: 120,                            // ← Fixed pixel width
    headerSort: true,                      // ← Click to sort
    headerFilter: "input",                 // ← Text input filter
    headerFilterPlaceholder: "Search...",  // ← Filter placeholder
    formatter: function (cell) {           // ← Custom cell rendering
        return `<span style="font-weight: 600; color: #ffffff;">#${cell.getValue()}</span>`;
    }
}
```

**Pattern Components:**
1. **Title** - Descriptive header text
2. **Field** - Maps to data property
3. **Width** - Fixed pixel width (no percentage)
4. **HeaderSort** - Enable/disable sorting (true for most columns)
5. **HeaderFilter** - Always "input" type (universal text search)
6. **HeaderFilterPlaceholder** - Always "Search..."
7. **Formatter** - Inline HTML with inline CSS

---

## 3. Text Formatting Standard

### **White Text on Dark Background**
```javascript
// All text cells use #ffffff
return `<span style="color: #ffffff;">${value}</span>`;

// Bold text for emphasis
return `<span style="font-weight: 600; color: #ffffff;">#${id}</span>`;

// Multi-line content
return `<div style="line-height: 1.5; color: #ffffff;">
    ${addressLines.join('<br>')}
</div>`;
```

**Typography Rules:**
- Base color: `#ffffff` (white)
- Bold: `font-weight: 600`
- Line height for readability: `1.5` or `1.6`
- Use `<div>` for multi-line, `<span>` for single-line

---

## 4. Status Badge Pattern

### **Vibrant Color System**
```javascript
const statusColors = {
    'pending': { bg: '#f59e0b', text: '#fffbeb' },      // Amber
    'processing': { bg: '#3b82f6', text: '#eff6ff' },   // Blue
    'completed': { bg: '#10b981', text: '#ecfdf5' },    // Green
    'on-hold': { bg: '#6b7280', text: '#f9fafb' },      // Gray
    'cancelled': { bg: '#ef4444', text: '#fef2f2' },    // Red
    'refunded': { bg: '#8b5cf6', text: '#f5f3ff' },     // Purple
    'failed': { bg: '#dc2626', text: '#fef2f2' }        // Dark Red
};

// Formatter
formatter: function (cell) {
    const status = cell.getValue();
    const colors = statusColors[status.toLowerCase()] || { bg: '#6b7280', text: '#f9fafb' };
    return `<span style="
        display: inline-block;
        padding: 6px 14px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 700;
        background: ${colors.bg};
        color: ${colors.text};
        text-transform: capitalize;
        letter-spacing: 0.3px;
    ">${status.replace('-', ' ')}</span>`;
}
```

**Badge Styling Rules:**
- `display: inline-block` - proper sizing
- `padding: 6px 14px` - horizontal emphasis
- `border-radius: 12px` - pill shape
- `font-size: 12px` - smaller than body text
- `font-weight: 700` - bold
- `letter-spacing: 0.3px` - improved readability
- `text-transform: capitalize` - proper casing

---

## 5. Multi-Column Data Display

### **Contact Column Pattern**
```javascript
{
    title: "Contact",
    field: "customer_email",
    width: 200,
    headerSort: false,                    // ← No sort for composite data
    headerFilter: "input",                // ← But still searchable
    formatter: function (cell) {
        const row = cell.getRow().getData();
        return `
            <div>
                <div style="margin-bottom: 4px; color: #ffffff;">
                    <i class="fas fa-envelope" style="margin-right: 4px; color: #ffffff;"></i>
                    ${row.customer_email || 'N/A'}
                </div>
                <div style="color: #ffffff;">
                    <i class="fas fa-phone" style="margin-right: 4px; color: #ffffff;"></i>
                    ${row.customer_phone || 'N/A'}
                </div>
            </div>
        `;
    }
}
```

**Composite Column Rules:**
- Use `getRow().getData()` to access all row data
- `margin-bottom: 4px` for vertical spacing
- Font Awesome icons with `margin-right: 4px`
- Fallback to `'N/A'` for missing data
- All text color `#ffffff`

---

## 6. Date/Time Formatting

### **Date Column**
```javascript
{
    title: "Date",
    field: "date_created",
    width: 120,
    headerSort: true,
    sorter: "datetime",                   // ← Date sorter
    headerFilter: "input",
    formatter: function (cell) {
        const date = new Date(cell.getValue());
        return `<span style="color: #ffffff;">${date.toLocaleDateString('en-GB', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        }).replace(/\//g, '-')}</span>`;
    }
}
```

**Date Format:**
- Locale: `'en-GB'` (DD-MM-YYYY)
- Replace `/` with `-` for consistency
- Sorter: `"datetime"` for proper chronological sorting

### **Time Column**
```javascript
{
    title: "Time",
    field: "date_created",               // ← Same field as Date
    width: 100,
    headerSort: false,                   // ← No sort (use Date column)
    formatter: function (cell) {
        const date = new Date(cell.getValue());
        return `<span style="color: #ffffff;">${date.toLocaleTimeString('en-GB', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        })}</span>`;
    }
}
```

**Time Format:**
- 24-hour format (HH:MM:SS)
- No sorting on time column (use Date)
- Still searchable via headerFilter

---

## 7. Action Buttons Pattern

### **Inline Button Styling**
```javascript
{
    title: "Actions",
    field: "id",
    width: 140,
    headerSort: false,                   // ← No sorting
    hozAlign: "center",                  // ← Center align
    formatter: function (cell) {
        const orderId = cell.getValue();
        return `
            <button 
                onclick="wcViewOrder(${orderId})" 
                style="
                    padding: 6px 12px;
                    background: var(--accent-primary);
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 11px;
                    margin-right: 4px;
                " 
                title="View Details"
            >
                <i class="fas fa-eye"></i>
            </button>
            <button 
                onclick="wcPrintOrder(${orderId})" 
                style="
                    padding: 6px 12px;
                    background: var(--accent-success);
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 11px;
                " 
                title="Print Label"
            >
                <i class="fas fa-print"></i>
            </button>
        `;
    }
}
```

**Button Styling Rules:**
- `padding: 6px 12px` - compact button
- `border: none` + `border-radius: 4px` - modern look
- `cursor: pointer` - indicates clickability
- `font-size: 11px` - smaller than body text
- `margin-right: 4px` - spacing between buttons
- CSS variables for colors (`var(--woocommerce-purple)`)
- Font Awesome icons only (no text)
- `title` attribute for tooltips

---

## 8. Custom Filter Functions

### **Print Label Column with Custom Search**
```javascript
{
    title: "Print Label",
    field: "id",
    width: 300,
    headerSort: false,
    headerFilter: "input",
    headerFilterPlaceholder: "Search...",
    headerFilterFunc: function (headerValue, rowValue, rowData, filterParams) {
        const printLabel = createPrintLabel(rowData);
        return printLabel.toLowerCase().includes(headerValue.toLowerCase());
    },
    formatter: function (cell) {
        const row = cell.getRow().getData();
        const printLabel = createPrintLabel(row);
        return `<div style="
            line-height: 1.5;
            white-space: pre-wrap;
            font-family: monospace;
            background: var(--bg-primary);
            border-left: 3px solid var(--woocommerce-purple);
            padding: 8px;
            max-width: 300px;
            color: #ffffff;
        ">${printLabel.replace(/\n/g, '<br>')}</div>`;
    }
}
```

**Custom Filter Pattern:**
- `headerFilterFunc` - custom search logic
- Search against computed/formatted value (not raw data)
- Case-insensitive search (`toLowerCase()`)
- `includes()` for substring matching

**Formatted Text Display:**
- `white-space: pre-wrap` - preserve formatting
- `font-family: monospace` - fixed-width font
- `border-left: 3px solid var(--accent-primary)` - orange accent (#FF7A00)
- `padding: 8px` - internal spacing
- `max-width` to prevent overflow
- **NOTE:** Use orange accent for all borders/highlights (no purple)

---

## 9. Currency Formatting

### **Currency Symbol Map**
```javascript
const currencySymbols = {
    'USD': '$', 
    'CAD': 'C$', 
    'AUD': 'A$', 
    'EUR': '€', 
    'GBP': '£',
    'NZD': 'NZ$', 
    'SGD': 'S$', 
    'JPY': '¥', 
    'CHF': 'CHF'
};

// Total column formatter
{
    title: "Total",
    field: "total",
    width: 130,
    headerSort: true,
    hozAlign: "right",                    // ← Right-align numbers
    sorter: "number",                     // ← Numeric sorting
    headerFilter: "input",
    formatter: function (cell) {
        const row = cell.getRow().getData();
        const currencySymbol = currencySymbols[row.currency] || row.currency;
        return `<span style="font-weight: 600; color: #ffffff;">
            ${currencySymbol}${parseFloat(row.total).toFixed(2)} (${row.currency})
        </span>`;
    }
}
```

**Number Formatting Rules:**
- `hozAlign: "right"` - right-align numeric data
- `sorter: "number"` - numeric sorting
- `parseFloat().toFixed(2)` - 2 decimal places
- Currency symbol + amount + code (e.g., "$123.45 (USD)")
- `font-weight: 600` - bold for emphasis

---

## 10. CSS Variables Used

### **Global CSS Variables (Orange Accent System)**
```css
--bg-primary: #0B0E13;            /* Dark background */
--accent-primary: #FF7A00;        /* Primary accent (orange) - USE THIS */
--accent-success: #10B981;        /* Success green */
--accent-error: #EF4444;          /* Error red */
--text-primary: #FFFFFF;          /* White text */
--text-secondary: #9CA3AF;        /* Secondary text color */
--text-muted: #6B7280;            /* Muted text color */
```

**Usage Pattern:**
- ✅ Use `var(--accent-primary)` for primary buttons/actions (orange #FF7A00)
- ✅ Use `var(--accent-success)` for success states (green)
- ✅ Use `var(--accent-error)` for errors/warnings (red)
- ❌ **DO NOT** use purple gradient or purple colors
- ✅ All modules follow same orange accent system

---

## 11. Comparison: WooCommerce vs Quote Calculator

### **Table Structure**

| Feature | WooCommerce Orders | Quote Calculator |
|---------|-------------------|------------------|
| **Column Count** | 11 columns | 6-8 columns (varies by tab) |
| **Header Filters** | ✅ ALL columns | ❌ None |
| **Inline Styling** | ✅ All formatters | ❓ Unknown (need to check) |
| **Status Badges** | ✅ Vibrant colors | ❌ Plain text |
| **Action Buttons** | ✅ Inline styled | ❓ Unknown |
| **Pagination** | ✅ Local (25/page) | ❓ Unknown |
| **Movable Columns** | ✅ Yes | ❌ Probably no |
| **Resizable Columns** | ✅ Yes | ❌ Probably no |

### **Text Formatting**

| Aspect | WooCommerce | Quote Calculator |
|--------|-------------|------------------|
| **Text Color** | `#ffffff` (white) | ❓ Likely `var(--text-primary)` |
| **Bold Text** | `font-weight: 600` | ❓ Unknown |
| **Line Height** | `1.5` or `1.6` | ❓ Likely default (1.2) |
| **Font Size** | Default (14px) | ❓ Unknown |

### **Status/Badge System**

| Feature | WooCommerce | Quote Calculator |
|---------|-------------|------------------|
| **Status Colors** | 7-color system | ❓ Unknown if exists |
| **Badge Style** | Pill-shaped (12px border-radius) | ❓ Likely rectangular |
| **Font Weight** | 700 (bold) | ❓ Likely 500-600 |
| **Letter Spacing** | 0.3px | ❓ Likely default (0) |

---

## 12. Recommended Migration Plan

### **Phase 1: Quote Calculator Tabulator Tables**
1. Add `headerFilter: "input"` to all columns
2. Replace text color with `#ffffff`
3. Add status badge system (if applicable)
4. Add inline button styling for actions
5. Enable `movableColumns: true` and `resizableColumns: true`
6. Add pagination: `pagination: "local", paginationSize: 25`

### **Phase 2: Other Modules**
1. **Stock Management** - already has good tabulator implementation, align colors
2. **Xero** - apply same patterns
3. **Shopify** - apply same patterns

### **Phase 3: Shared Component Library**
Create `UI/shared/js/tabulator-standards.js`:
```javascript
const TabulatorStandards = {
    // Standard column config
    createColumn(title, field, options = {}) {
        return {
            title,
            field,
            width: options.width || 150,
            headerSort: options.headerSort !== false,
            headerFilter: options.headerFilter !== false ? "input" : undefined,
            headerFilterPlaceholder: "Search...",
            formatter: options.formatter || this.defaultFormatter,
            ...options
        };
    },
    
    // Default white text formatter
    defaultFormatter(cell) {
        return `<span style="color: #ffffff;">${cell.getValue()}</span>`;
    },
    
    // Status badge formatter
    statusFormatter(statusColors) {
        return function(cell) {
            const status = cell.getValue();
            const colors = statusColors[status.toLowerCase()] || { bg: '#6b7280', text: '#f9fafb' };
            return `<span style="
                display: inline-block;
                padding: 6px 14px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 700;
                background: ${colors.bg};
                color: ${colors.text};
                text-transform: capitalize;
                letter-spacing: 0.3px;
            ">${status.replace('-', ' ')}</span>`;
        };
    },
    
    // Action button formatter
    actionFormatter(buttons) {
        return function(cell) {
            const id = cell.getValue();
            return buttons.map(btn => `
                <button 
                    onclick="${btn.onclick}(${id})" 
                    style="
                        padding: 6px 12px;
                        background: ${btn.color};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 11px;
                        margin-right: 4px;
                    " 
                    title="${btn.title}"
                >
                    <i class="${btn.icon}"></i>
                </button>
            `).join('');
        };
    }
};
```

---

## 13. Key Insights & Best Practices

### **Why WooCommerce is Superior**

1. **Universal Filtering** - Every column searchable (even actions/composite columns)
2. **Inline Everything** - No CSS file dependencies, all styling in JS
3. **High Contrast** - White text on dark background (accessible)
4. **User Control** - Movable/resizable columns, adjustable pagination
5. **Consistent Patterns** - Same formatter structure across all columns
6. **Smart Defaults** - Sensible width allocations, proper sorting types
7. **Visual Hierarchy** - Bold for emphasis, badges for status, icons for actions

### **Common Pitfalls to Avoid**

❌ **External CSS for table styling** - Hard to maintain, creates dependencies  
✅ **Inline styles in formatters** - Self-contained, portable

❌ **Percentage widths** - Unpredictable on different screen sizes  
✅ **Fixed pixel widths** - Consistent, user can resize if needed

❌ **Generic text color** - Low contrast on dark backgrounds  
✅ **White text (#ffffff)** - Maximum readability

❌ **No header filters** - Users must scroll to find data  
✅ **Universal header filters** - Fast searching on every column

❌ **Plain text status** - No visual hierarchy  
✅ **Colored badges** - Immediate visual recognition

---

## 14. Implementation Checklist

### **For Existing Tabulator Tables**

- [ ] Add `headerFilter: "input"` to all columns
- [ ] Change all text to `color: #ffffff`
- [ ] Add status badge system (if applicable)
- [ ] Add action button column with inline styles
- [ ] **Replace any purple colors with `var(--accent-primary)` (orange)**
- [ ] Enable `movableColumns: true`
- [ ] Enable `resizableColumns: true`
- [ ] Add pagination: `pagination: "local", paginationSize: 25`
- [ ] Use `layout: "fitDataStretch"`
- [ ] Add `sorter` types where appropriate (`datetime`, `number`)
- [ ] Add `hozAlign: "right"` for numeric columns
- [ ] Add Font Awesome icons to action buttons
- [ ] Add tooltip `title` attributes to buttons

### **For New Tabulator Tables**

- [ ] Copy WooCommerce table initialization structure
- [ ] Define status colors map (if needed)
- [ ] Define currency symbols map (if needed)
- [ ] Use standard column pattern for all columns
- [ ] Test header filters on all columns
- [ ] Test sorting on appropriate columns
- [ ] Test pagination controls
- [ ] Test column reordering
- [ ] Test column resizing

---

## 15. Code Templates

### **Standard Table Initialization**
```javascript
// Destroy existing table if present
if (window.myModuleTable) {
    window.myModuleTable.destroy();
}

// Clear container
container.innerHTML = '';
container.style.display = 'block';

// Initialize Tabulator
window.myModuleTable = new Tabulator(container, {
    data: myData,
    layout: "fitDataStretch",
    pagination: "local",
    paginationSize: 25,
    paginationSizeSelector: [10, 25, 50, 100],
    movableColumns: true,
    resizableColumns: true,
    placeholder: "No data found",
    columns: [
        // Add columns here
    ]
});
```

### **Standard Text Column**
```javascript
{
    title: "Column Name",
    field: "field_name",
    width: 150,
    headerSort: true,
    headerFilter: "input",
    headerFilterPlaceholder: "Search...",
    formatter: function (cell) {
        return `<span style="color: #ffffff;">${cell.getValue()}</span>`;
    }
}
```

### **Date Column**
```javascript
{
    title: "Date",
    field: "date_field",
    width: 120,
    headerSort: true,
    sorter: "datetime",
    headerFilter: "input",
    headerFilterPlaceholder: "Search...",
    formatter: function (cell) {
        const date = new Date(cell.getValue());
        return `<span style="color: #ffffff;">${date.toLocaleDateString('en-GB', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        }).replace(/\//g, '-')}</span>`;
    }
}
```

### **Status Column**
```javascript
{
    title: "Status",
    field: "status",
    width: 130,
    headerSort: true,
    headerFilter: "input",
    headerFilterPlaceholder: "Search...",
    formatter: function (cell) {
        const status = cell.getValue();
        const statusColors = {
            'active': { bg: '#10b981', text: '#ecfdf5' },
            'pending': { bg: '#f59e0b', text: '#fffbeb' },
            'inactive': { bg: '#6b7280', text: '#f9fafb' }
        };
        const colors = statusColors[status.toLowerCase()] || { bg: '#6b7280', text: '#f9fafb' };
        return `<span style="
            display: inline-block;
            padding: 6px 14px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 700;
            background: ${colors.bg};
            color: ${colors.text};
            text-transform: capitalize;
            letter-spacing: 0.3px;
        ">${status}</span>`;
    }
}
```

### **Action Column**
```javascript
{
    title: "Actions",
    field: "id",
    width: 140,
    headerSort: false,
    hozAlign: "center",
    formatter: function (cell) {
        const id = cell.getValue();
        return `
            <button 
                onclick="viewItem(${id})" 
                style="
                    padding: 6px 12px;
                    background: var(--accent-primary);
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 11px;
                    margin-right: 4px;
                " 
                title="View Details"
            >
                <i class="fas fa-eye"></i>
            </button>
            <button 
                onclick="editItem(${id})" 
                style="
                    padding: 6px 12px;
                    background: var(--accent-success);
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 11px;
                " 
                title="Edit"
            >
                <i class="fas fa-edit"></i>
            </button>
        `;
    }
}
```

---

## 16. Next Steps

1. **Audit Quote Calculator** - Check existing tabulator tables in all 6 tabs
2. **Document Current State** - Create "before" screenshots
3. **Apply Standards** - Migrate one tab at a time
4. **Test Thoroughly** - Verify filtering, sorting, pagination
5. **Create Shared Library** - Extract common patterns to `tabulator-standards.js`
6. **Update Other Modules** - Apply to Stock Management, Xero, Shopify
7. **Document Changes** - Update module READMEs with new standards

---

## 17. References

- **WooCommerce Module:** `UI/modules_internal/woocommerce/woocommerce.js` (922 lines)
- **Tabulator Theme Adapter:** `UI/shared/js/tabulator-theme-adapter.js` (existing theme system)
- **Quote Calculator:** `UI/modules_external/quote-calculator/` (target for migration)

---

## 18. Important Color System Note ⚠️

**DO NOT USE PURPLE GRADIENT OR PURPLE COLORS**

The platform uses a **consistent orange accent system** across all modules:

```css
Primary Accent: #FF7A00 (Orange) - var(--accent-primary)
Success: #10B981 (Green) - var(--accent-success)  
Error: #EF4444 (Red) - var(--accent-error)
```

✅ **Use orange for:**
- Primary action buttons
- Accent borders
- Active states
- Hover effects
- Primary highlights

❌ **Never use:**
- Purple gradients
- Purple buttons
- Purple borders
- Purple accents

All examples in this document should use `var(--accent-primary)` instead of any purple color references.

---

**End of Analysis** 🎯

---

## 19. Advanced Features from Transcript Processor 🚀

After analyzing `transcript_processor.html`, here are the advanced Tabulator features to integrate into the WooCommerce Orders table:

###  **Checkbox Selection + Multi-Select + Range Select**

**Configuration:**
```javascript
window.wooOrdersTable = new Tabulator(container, {
    selectable: true,                       // ← Enable row selection
    selectableRangeMode: "click",          // ← Enable Shift+click range selection
    columns: [
        {
            title: "Select", 
            formatter: "rowSelection",        // ← Checkbox formatter
            titleFormatter: "rowSelection",   // ← Header "select all" checkbox
            hozAlign: "center",
            headerHozAlign: "center",
            headerSort: false,
            width: 60,
            frozen: true                      // ← Keep checkbox column visible when scrolling
        },
        // ... other columns
    ]
});

// Update selection count (for bulk actions)
wooOrdersTable.on("rowSelectionChanged", function(data, rows) {
    document.getElementById('selection-count').textContent = rows.length;
});

// Click anywhere on checkbox cell to toggle (easier than hitting tiny checkbox)
wooOrdersTable.on("cellClick", function(e, cell) {
    const column = cell.getColumn();
    const field = column.getField();
    
    if (field === undefined && column.getDefinition().formatter === "rowSelection") {
        const row = cell.getRow();
        if (!e.shiftKey) {  // Let Tabulator handle shift+click
            row.toggleSelect();
        }
    }
});
```

**Features:**
- ✅ Single click to select row
- ✅ Shift+click to select range
- ✅ Header checkbox to select/deselect all
- ✅ Click anywhere on checkbox cell (not just tiny checkbox)
- ✅ Frozen column stays visible when scrolling horizontally

---

### **Selected Row Background Fix (CRITICAL)**

**Problem:** Selected rows turning white background makes text invisible.

**Solution:**
```css
/* DARK BLUE background for selected rows (NOT white!) */
.tabulator .tabulator-row.tabulator-selected {
    background: rgba(21, 101, 192, 0.8) !important;  /* Dark blue, 80% opacity */
    color: #ffffff !important;
}

/* Ensure ALL cells in selected row have white text */
.tabulator .tabulator-row.tabulator-selected .tabulator-cell {
    color: #ffffff !important;
}

/* Normal row hover (lighter) */
.tabulator .tabulator-row:hover {
    background: var(--bg-hover) !important;  /* Subtle hover, NOT white */
}
```

**Color Options:**
- **Dark Blue:** `rgba(21, 101, 192, 0.8)` ← Recommended
- **Orange (accent):** `rgba(255, 122, 0, 0.3)` ← Alternative
- **Green:** `rgba(16, 185, 129, 0.3)` ← For success states

**Rule:** NEVER use white background for selected rows on dark theme tables!

---

### **Row Tagging System (Color Labels)**

**LocalStorage-Based Tags:**
```javascript
// Tag colors map
const tagColors = {
    'green': { bg: 'rgba(40, 167, 69, 0.15)', border: '#28a745' },
    'orange': { bg: 'rgba(230, 81, 0, 0.15)', border: '#e65100' },
    'red': { bg: 'rgba(220, 38, 38, 0.15)', border: '#dc2626' }
};

// Get row tag from localStorage
function getRowTag(orderId) {
    const tags = JSON.parse(localStorage.getItem('woo_order_tags') || '{}');
    return tags[orderId] || null;
}

// Set row tag
function setRowTag(orderId, color) {
    const tags = JSON.parse(localStorage.getItem('woo_order_tags') || '{}');
    if (color === null) {
        delete tags[orderId];
    } else {
        tags[orderId] = color;
    }
    localStorage.setItem('woo_order_tags', JSON.stringify(tags));
}

// Toggle tag (cycle: none → green → orange → red → none)
function toggleRowTag(event, orderId) {
    event.stopPropagation();
    
    const currentTag = getRowTag(orderId);
    let newTag = null;
    
    if (currentTag === null) newTag = 'green';
    else if (currentTag === 'green') newTag = 'orange';
    else if (currentTag === 'orange') newTag = 'red';
    else newTag = null;  // Back to untagged
    
    setRowTag(orderId, newTag);
    
    // Refresh table to apply tag colors
    window.wooOrdersTable.redraw(true);
}

// Apply tags to rows (use rowFormatter)
rowFormatter: function(row) {
    const data = row.getData();
    const tagColor = getRowTag(data.id);
    
    // Remove all tag classes
    row.getElement().classList.remove('tagged-row-green', 'tagged-row-orange', 'tagged-row-red');
    
    // Add tag class if tagged
    if (tagColor) {
        row.getElement().classList.add(`tagged-row-${tagColor}`);
    }
}
```

**CSS for Tagged Rows:**
```css
/* Tagged row styles */
.tabulator .tagged-row-green {
    background: rgba(40, 167, 69, 0.15) !important;
    border-left: 4px solid #28a745 !important;
}

.tabulator .tagged-row-orange {
    background: rgba(230, 81, 0, 0.15) !important;
    border-left: 4px solid #e65100 !important;
}

.tabulator .tagged-row-red {
    background: rgba(220, 38, 38, 0.15) !important;
    border-left: 4px solid #dc2626 !important;
}

/* Tag button states */
.action-btn-tag {
    background: transparent;
    border: 1px solid #6b7280;
    color: #6b7280;
    padding: 4px 8px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
}

.action-btn-tag.tag-green {
    background: #28a745;
    border-color: #28a745;
    color: white;
}

.action-btn-tag.tag-orange {
    background: #e65100;
    border-color: #e65100;
    color: white;
}

.action-btn-tag.tag-red {
    background: #dc2626;
    border-color: #dc2626;
    color: white;
}
```

**Add Tag Column:**
```javascript
{
    title: "Tag",
    field: "actions_tag",
    width: 60,
    frozen: true,                    // Keep tag column visible when scrolling
    headerSort: false,
    hozAlign: "center",
    headerHozAlign: "center",
    formatter: function(cell) {
        const row = cell.getRow().getData();
        const currentTag = getRowTag(row.id);
        const tagClass = currentTag ? `tag-${currentTag}` : '';
        return `
            <button 
                class="action-btn-tag ${tagClass}" 
                onclick="toggleRowTag(event, '${row.id}')" 
                title="Tag Order (Click to cycle: None → Green → Orange → Red)"
            >
                <i class="fas fa-tag"></i>
            </button>
        `;
    }
}
```

**Bulk Tag Operations:**
```javascript
function bulkTagOrders(tagColor) {
    const selectedRows = window.wooOrdersTable.getSelectedRows();
    
    if (selectedRows.length === 0) {
        showNotification('No orders selected', 'warning');
        return;
    }
    
    selectedRows.forEach(row => {
        const data = row.getData();
        setRowTag(data.id, tagColor);
        
        // Update row element immediately
        const rowElement = row.getElement();
        rowElement.classList.remove('tagged-row-green', 'tagged-row-orange', 'tagged-row-red');
        if (tagColor) {
            rowElement.classList.add(`tagged-row-${tagColor}`);
        }
    });
    
    const tagName = tagColor ? tagColor.charAt(0).toUpperCase() + tagColor.slice(1) : 'Untagged';
    showNotification(`${selectedRows.length} order(s) tagged as ${tagName}`, 'success');
}
```

---

### **Double-Click Cell Popup Modal**

**Feature:** Click any cell to view full content in draggable popup.

**Implementation:**
```javascript
// Enable cell popup on double-click
window.wooOrdersTable.on("cellDblClick", function(e, cell) {
    showCellPopup(e, cell);
});

function showCellPopup(event, cell) {
    // Remove any existing popup
    const existingPopup = document.getElementById('cell-popup');
    if (existingPopup) {
        existingPopup.remove();
    }
    
    const cellData = cell.getValue();
    const fieldName = cell.getColumn().getField();
    const columnTitle = cell.getColumn().getDefinition().title;
    
    // Don't show popup for action columns or empty cells
    if (!cellData || fieldName === 'actions') return;
    
    const popup = document.createElement('div');
    popup.id = 'cell-popup';
    popup.className = 'cell-popup';
    
    // Limit to 50,000 characters for performance
    const displayText = String(cellData).substring(0, 50000);
    const charCount = String(cellData).length;
    const tokenCount = Math.ceil(charCount / 4);  // ~4 chars per token
    
    popup.innerHTML = `
        <div class="cell-popup-header" id="popup-header">
            <div class="cell-popup-header-left">
                <strong style="font-size: 18px;">${escapeHtml(columnTitle)}</strong>
                <span style="font-size: 12px; color: #999;">
                    ${charCount.toLocaleString()} characters | ~${tokenCount.toLocaleString()} tokens
                </span>
            </div>
            <div class="cell-popup-header-buttons">
                <button onclick="copyCellContent()" class="btn" style="background: #28a745; color: white; padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer;">
                    <i class="fas fa-copy"></i> Copy
                </button>
                <button onclick="closeCellPopup()" class="btn" style="background: #6c757d; color: white; padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer;">
                    Close
                </button>
            </div>
        </div>
        <div class="cell-popup-content">
            <pre style="white-space: pre-wrap; word-wrap: break-word; margin: 0; font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.5;">${escapeHtml(displayText)}</pre>
        </div>
    `;
    
    document.body.appendChild(popup);
    
    // Store full content for copy function
    popup.dataset.fullContent = String(cellData);
    
    // Make popup draggable by header
    makeDraggable(popup, document.getElementById('popup-header'));
}

function closeCellPopup() {
    const popup = document.getElementById('cell-popup');
    if (popup) popup.remove();
}

function copyCellContent() {
    const popup = document.getElementById('cell-popup');
    if (popup && popup.dataset.fullContent) {
        navigator.clipboard.writeText(popup.dataset.fullContent)
            .then(() => showNotification('Copied to clipboard', 'success'))
            .catch(() => showNotification('Copy failed', 'error'));
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function makeDraggable(popup, header) {
    let isDragging = false, currentX, currentY, initialX, initialY, xOffset = 0, yOffset = 0;
    
    header.addEventListener('mousedown', dragStart);
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', dragEnd);
    
    header.style.cursor = 'move';
    
    function dragStart(e) {
        // Don't drag if clicking buttons
        if (e.target.tagName === 'BUTTON' || e.target.closest('button')) return;
        
        initialX = e.clientX - xOffset;
        initialY = e.clientY - yOffset;
        isDragging = true;
    }
    
    function drag(e) {
        if (!isDragging) return;
        e.preventDefault();
        
        currentX = e.clientX - initialX;
        currentY = e.clientY - initialY;
        
        xOffset = currentX;
        yOffset = currentY;
        
        popup.style.transform = `translate(${currentX}px, ${currentY}px)`;
    }
    
    function dragEnd() {
        isDragging = false;
    }
}
```

**CSS for Cell Popup:**
```css
/* Cell Popup Modal */
.cell-popup {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90%;
    max-width: 800px;
    max-height: 80vh;
    background: var(--bg-card);
    border: 2px solid var(--accent-primary);
    border-radius: 8px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    z-index: 10001;
    display: flex;
    flex-direction: column;
    animation: popupFadeIn 0.2s ease;
}

@keyframes popupFadeIn {
    from { opacity: 0; transform: translate(-50%, -45%); }
    to { opacity: 1; transform: translate(-50%, -50%); }
}

.cell-popup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    border-radius: 8px 8px 0 0;
    cursor: move;  /* Indicates draggable */
}

.cell-popup-header-left {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.cell-popup-header-buttons {
    display: flex;
    gap: 8px;
}

.cell-popup-content {
    padding: 20px;
    overflow-y: auto;
    flex: 1;
    background: var(--bg-primary);
}

.cell-popup-content pre {
    color: var(--text-primary);
}

/* Scrollbar styling for popup */
.cell-popup-content::-webkit-scrollbar {
    width: 12px;
}

.cell-popup-content::-webkit-scrollbar-track {
    background: var(--bg-secondary);
}

.cell-popup-content::-webkit-scrollbar-thumb {
    background: var(--accent-primary);
    border-radius: 6px;
}
```

**Features:**
- ✅ Double-click any cell to view full content
- ✅ Draggable by header (hold and drag)
- ✅ Shows character count and token estimate
- ✅ Copy button to clipboard
- ✅ Monospace font for code/JSON display
- ✅ Max 50,000 characters for performance
- ✅ Scrollable content area
- ✅ Orange border accent
- ✅ Animated entrance

---

### **Row Number Column**

**Add row number column (frozen):**
```javascript
{
    title: "#", 
    field: "row_number",
    width: 50,
    frozen: true,                    // Keep visible when scrolling
    headerSort: false,
    hozAlign: "center",
    headerHozAlign: "center",
    formatter: function(cell) {
        // Display row position (1-indexed, like spreadsheet)
        return cell.getRow().getPosition();
    },
    cssClass: "row-number-column"
}
```

**CSS:**
```css
.tabulator .row-number-column {
    background: #21262d !important;
    color: #8b949e !important;
    font-weight: 600;
    font-size: 12px;
    border-right: 1px solid #30363d !important;
}

.tabulator .tabulator-row.tabulator-selected .row-number-column {
    background: rgba(21, 101, 192, 0.6) !important;
    color: #ffffff !important;
}
```

---

### **Column Visibility (Hide/Show)**

**Add hide button to column headers:**
```javascript
// Custom title formatter that adds hide button
function columnTitleWithHideButton(cell) {
    const column = cell.getColumn();
    const title = cell.getValue();
    
    const container = document.createElement("div");
    container.style.display = "flex";
    container.style.justifyContent = "space-between";
    container.style.alignItems = "center";
    container.style.width = "100%";
    
    const titleSpan = document.createElement("span");
    titleSpan.textContent = title;
    
    const hideBtn = document.createElement("button");
    hideBtn.innerHTML = '<i class="fas fa-eye-slash"></i>';
    hideBtn.className = "column-hide-btn";
    hideBtn.title = "Hide this column";
    hideBtn.onclick = function(e) {
        e.stopPropagation();
        column.hide();
        showNotification(`Column "${title}" hidden`, 'success');
    };
    
    container.appendChild(titleSpan);
    container.appendChild(hideBtn);
    
    return container;
}

// Apply to columns
{
    title: "Customer Name",
    field: "customer_name",
    titleFormatter: columnTitleWithHideButton,  // ← Add hide button
    // ... rest of column config
}
```

**Right-Click Context Menu:**
```javascript
headerMenu: [
    {
        label: "<i class='fas fa-eye-slash'></i> Hide Column",
        action: function(e, column) {
            column.hide();
            showNotification(`Column "${column.getDefinition().title}" hidden`, 'success');
        }
    },
    {
        separator: true,
    },
    {
        label: "<i class='fas fa-eye'></i> Show All Columns",
        action: function(e, column) {
            const table = column.getTable();
            table.getColumns().forEach(col => {
                if (!col.getDefinition().frozen) {  // Don't affect frozen columns
                    col.show();
                }
            });
            showNotification('All columns visible', 'success');
        }
    }
]
```

**Persistence (Remember Hidden Columns):**
```javascript
persistenceMode: "local",           // Save to localStorage
persistence: {
    sort: true,
    filter: true,
    columns: ["width", "visible"]   // Remember which columns are hidden
}
```

---

### **Enhanced Bulk Actions UI**

**Add bulk action toolbar:**
```html
<div class="bulk-actions-toolbar" style="display: flex; gap: 8px; align-items: center; padding: 12px; background: var(--bg-secondary); border-radius: 6px; margin-bottom: 12px;">
    <div style="flex: 1;">
        <strong>Selected:</strong> 
        <span id="woo-selection-count">0</span> orders
    </div>
    
    <!-- Tag Buttons -->
    <button onclick="bulkTagOrders('green')" class="btn" style="background: #28a745; color: white; padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer;">
        <i class="fas fa-tag"></i> Tag Green
    </button>
    <button onclick="bulkTagOrders('orange')" class="btn" style="background: #e65100; color: white; padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer;">
        <i class="fas fa-tag"></i> Tag Orange
    </button>
    <button onclick="bulkTagOrders('red')" class="btn" style="background: #dc2626; color: white; padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer;">
        <i class="fas fa-tag"></i> Tag Red
    </button>
    <button onclick="bulkTagOrders(null)" class="btn" style="background: #6c757d; color: white; padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer;">
        <i class="fas fa-times"></i> Clear Tags
    </button>
    
    <!-- Export Selected -->
    <button onclick="exportSelected()" class="btn" style="background: var(--accent-primary); color: white; padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer;">
        <i class="fas fa-file-export"></i> Export Selected
    </button>
</div>
```

**Export Selected Rows:**
```javascript
function exportSelected() {
    const selectedRows = window.wooOrdersTable.getSelectedData();
    
    if (selectedRows.length === 0) {
        showNotification('No orders selected', 'warning');
        return;
    }
    
    window.wooOrdersTable.download("xlsx", "selected-orders.xlsx", {
        sheetName: "Selected Orders"
    }, "selected");  // "selected" param exports only selected rows
    
    showNotification(`Exported ${selectedRows.length} orders`, 'success');
}
```

---

### **Complete Enhanced Tabulator Configuration**

```javascript
function renderOrdersTable(orders, container) {
    // Destroy existing table
    if (window.wooOrdersTable) {
        window.wooOrdersTable.destroy();
    }
    
    container.innerHTML = '';
    container.style.display = 'block';
    
    window.wooOrdersTable = new Tabulator(container, {
        data: orders,
        layout: "fitDataStretch",
        selectable: true,                       // ✅ Enable row selection
        selectableRangeMode: "click",          // ✅ Shift+click range selection
        pagination: "local",
        paginationSize: 25,
        paginationSizeSelector: [10, 25, 50, 100],
        movableColumns: true,
        resizableColumns: true,
        persistenceMode: "local",              // ✅ Save state to localStorage
        persistence: {
            sort: true,
            filter: true,
            columns: ["width", "visible"]      // ✅ Remember hidden columns
        },
        placeholder: "No orders found",
        rowFormatter: function(row) {          // ✅ Apply row tags
            const data = row.getData();
            const tagColor = getRowTag(data.id);
            
            row.getElement().classList.remove('tagged-row-green', 'tagged-row-orange', 'tagged-row-red');
            if (tagColor) {
                row.getElement().classList.add(`tagged-row-${tagColor}`);
            }
        },
        headerMenu: [                          // ✅ Right-click column menu
            {
                label: "<i class='fas fa-eye-slash'></i> Hide Column",
                action: function(e, column) {
                    column.hide();
                    showNotification(`Column hidden`, 'success');
                }
            },
            {
                separator: true,
            },
            {
                label: "<i class='fas fa-eye'></i> Show All Columns",
                action: function(e, column) {
                    column.getTable().getColumns().forEach(col => {
                        if (!col.getDefinition().frozen) col.show();
                    });
                    showNotification('All columns visible', 'success');
                }
            }
        ],
        columns: [
            // ✅ Checkbox column
            {
                title: "Select", 
                formatter: "rowSelection",
                titleFormatter: "rowSelection",
                hozAlign: "center",
                headerHozAlign: "center",
                headerSort: false,
                width: 60,
                frozen: true
            },
            // ✅ Row number column
            {
                title: "#", 
                field: "row_number",
                width: 50,
                frozen: true,
                headerSort: false,
                hozAlign: "center",
                headerHozAlign: "center",
                formatter: function(cell) {
                    return cell.getRow().getPosition();
                },
                cssClass: "row-number-column"
            },
            // ✅ Tag column
            {
                title: "Tag",
                field: "actions_tag",
                width: 60,
                frozen: true,
                headerSort: false,
                hozAlign: "center",
                headerHozAlign: "center",
                formatter: function(cell) {
                    const row = cell.getRow().getData();
                    const currentTag = getRowTag(row.id);
                    const tagClass = currentTag ? `tag-${currentTag}` : '';
                    return `
                        <button 
                            class="action-btn-tag ${tagClass}" 
                            onclick="toggleRowTag(event, '${row.id}')" 
                            title="Tag Order"
                        >
                            <i class="fas fa-tag"></i>
                        </button>
                    `;
                }
            },
            // ✅ Regular columns (all with hide button)
            {
                title: "Order ID",
                field: "id",
                width: 120,
                headerSort: true,
                headerFilter: "input",
                titleFormatter: columnTitleWithHideButton,  // ✅ Hide button
                formatter: function (cell) {
                    return `<span style="font-weight: 600; color: #ffffff;">#${cell.getValue()}</span>`;
                }
            },
            // ... (rest of your columns with titleFormatter: columnTitleWithHideButton)
        ]
    });
    
    // ✅ Enable cell popup on double-click
    wooOrdersTable.on("cellDblClick", function(e, cell) {
        showCellPopup(e, cell);
    });
    
    // ✅ Click checkbox cell to toggle (easier than tiny checkbox)
    wooOrdersTable.on("cellClick", function(e, cell) {
        const column = cell.getColumn();
        const field = column.getField();
        
        if (field === undefined && column.getDefinition().formatter === "rowSelection") {
            const row = cell.getRow();
            if (!e.shiftKey) {
                row.toggleSelect();
            }
        }
    });
    
    // ✅ Update selection count
    wooOrdersTable.on("rowSelectionChanged", function(data, rows) {
        document.getElementById('woo-selection-count').textContent = rows.length;
    });
}
```

---

## 20. Implementation Checklist for WooCommerce Orders

### **Phase 1: Critical Fixes**
- [ ] Fix selected row background (dark blue, NOT white)
- [ ] Fix selected row text color (white)
- [ ] Test selection visibility

### **Phase 2: Selection System**
- [ ] Add checkbox column (frozen, left side)
- [ ] Add row number column (frozen, after checkbox)
- [ ] Enable `selectable: true`
- [ ] Enable `selectableRangeMode: "click"` (Shift+click)
- [ ] Add click handler for checkbox cell
- [ ] Add selection count display
- [ ] Test single/multi/range selection

### **Phase 3: Row Tagging**
- [ ] Add tag column (frozen, after row number)
- [ ] Implement `getRowTag()` / `setRowTag()` functions
- [ ] Implement `toggleRowTag()` function
- [ ] Add `rowFormatter` for tag colors
- [ ] Add CSS for tagged rows (green/orange/red)
- [ ] Add bulk tag buttons
- [ ] Implement `bulkTagOrders()` function
- [ ] Test tag persistence (localStorage)

### **Phase 4: Cell Popup**
- [ ] Add cell popup CSS
- [ ] Implement `showCellPopup()` function
- [ ] Implement `closeCellPopup()` function
- [ ] Implement `copyCellContent()` function
- [ ] Implement `makeDraggable()` function
- [ ] Add `cellDblClick` event handler
- [ ] Test popup on different cell types
- [ ] Test dragging functionality
- [ ] Test copy functionality

### **Phase 5: Column Management**
- [ ] Implement `columnTitleWithHideButton()` function
- [ ] Add `titleFormatter` to all non-frozen columns
- [ ] Add column hide button CSS
- [ ] Add `headerMenu` configuration
- [ ] Add `persistenceMode: "local"`
- [ ] Test hide/show columns
- [ ] Test persistence (refresh page)

### **Phase 6: Bulk Actions**
- [ ] Add bulk actions toolbar HTML
- [ ] Update selection count display
- [ ] Implement `exportSelected()` function
- [ ] Add bulk tag buttons
- [ ] Style bulk actions toolbar
- [ ] Test bulk operations

### **Phase 7: Testing & Polish**
- [ ] Test on different screen sizes
- [ ] Test with 100+ orders
- [ ] Test with empty table
- [ ] Test keyboard navigation (Tab, Shift+Tab)
- [ ] Test accessibility (screen readers)
- [ ] Performance test (1000+ rows)
- [ ] Check console for errors
- [ ] Verify localStorage cleanup

---

## 21. Final Implementation Summary

**What Makes This the Best Tabulator Table:**

1. ✅ **Universal Filtering** - Every column searchable
2. ✅ **White Text** - `#ffffff` on dark background (high contrast)
3. ✅ **Inline Styling** - No external CSS dependencies
4. ✅ **Multi-Select** - Checkbox + Shift+click range select
5. ✅ **Row Tagging** - 3-color label system (green/orange/red)
6. ✅ **Cell Popup** - Double-click to view full content (draggable)
7. ✅ **Column Hiding** - Hide button on every column header
8. ✅ **Persistence** - Remembers hidden columns and sort order
9. ✅ **Bulk Actions** - Tag/export selected rows
10. ✅ **Frozen Columns** - Checkbox, row number, tag stay visible when scrolling
11. ✅ **Right-Click Menu** - Context menu for column operations
12. ✅ **Orange Accents** - Consistent with platform theme (NO PURPLE!)
13. ✅ **Dark Blue Selection** - Visible selected rows (NOT white background)
14. ✅ **Status Badges** - Vibrant colored pills for order status
15. ✅ **Action Buttons** - Inline styled with Font Awesome icons

**Result:** Professional, feature-rich, accessible data table that matches enterprise SQL database viewers!

---

**End of Enhanced Analysis** 🎯🚀
