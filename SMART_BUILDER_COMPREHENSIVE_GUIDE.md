# 🎯 microsoft_excel_smart_sheet_builder - THE COMPLETE EXCEL TOOL

## ONE TOOL TO DO IT ALL

`microsoft_excel_smart_sheet_builder` is now the **comprehensive** tool for ALL Excel operations:

✅ Create new workbooks from scratch  
✅ Update existing workbooks granularly  
✅ Multiple worksheets in one call  
✅ Natural language formulas  
✅ Direct Excel formulas  
✅ Cross-sheet references  
✅ Multiple charts  
✅ Backward compatible  

---

## 🚀 Three Modes

### Mode 1: CREATE FROM SCRATCH (Comprehensive)
```python
microsoft_excel_smart_sheet_builder(
    workbook_name="Q1 Sales Report",
    worksheets=[
        {
            "name": "Sales Data",
            "columns": ["Rep", "Month", "Amount", "Region"],
            "data": [
                ["Alice", "Jan", 1000, "West"],
                ["Bob", "Jan", 1200, "East"],
                ["Carol", "Feb", 1100, "West"]
            ],
            "formulas": [
                {"cell": "C10", "formula": "sum column C"},
                {"cell": "C11", "formula": "average column C"}
            ],
            "chart": {
                "type": "column",
                "range": "A1:C10",
                "title": "Sales by Rep"
            }
        },
        {
            "name": "Summary",
            "columns": ["Metric", "Value"],
            "data": [
                ["Total Sales", ""],
                ["Average", ""],
                ["Count", ""]
            ],
            "formulas": [
                {"cell": "B1", "formula": "=SUM('Sales Data'!C:C)"},
                {"cell": "B2", "formula": "=AVERAGE('Sales Data'!C:C)"},
                {"cell": "B3", "formula": "=COUNT('Sales Data'!A:A)"}
            ]
        },
        {
            "name": "Regional Analysis",
            "chart": {
                "type": "pie",
                "range": "'Sales Data'!D1:D10",
                "title": "Sales by Region"
            }
        }
    ]
)
```

**Creates:**
- New workbook "Q1 Sales Report"
- 3 worksheets (Sales Data, Summary, Regional Analysis)
- Data in Sales Data sheet
- 5 formulas (2 in Sales Data, 3 cross-sheet in Summary)
- 2 charts (column chart and pie chart)

---

### Mode 2: UPDATE EXISTING (Granular)
```python
microsoft_excel_smart_sheet_builder(
    workbook_id="abc123def456",  # Existing workbook
    formulas=[
        {"sheet": "Data", "cell": "E1", "formula": "multiply column B by column C"},
        {"sheet": "Data", "cell": "F1", "formula": "=B1*1.1"},
        {"sheet": "Summary", "cell": "C1", "formula": "=SUM(Data!E:E)"}
    ],
    charts=[
        {"sheet": "Data", "type": "line", "range": "A1:C20", "title": "Trend Analysis"}
    ]
)
```

**Updates existing workbook with:**
- 3 new formulas
- 1 new chart
- NO new worksheets (updates existing)

---

### Mode 3: SIMPLE (Legacy/Backward Compatible)
```python
microsoft_excel_smart_sheet_builder(
    workbook_name="Sales Tracker",
    sheet_description="sales tracker with rep names and monthly totals"
)
```

**Auto-creates:**
- Columns: Sales Rep, Month, Amount, Region
- 5 rows of sample data
- SUM and AVERAGE formulas
- Column chart

---

## 📋 Parameter Reference

### Workbook Selection
| Parameter | Type | Description |
|-----------|------|-------------|
| `workbook_name` | string | Name for NEW workbook (create mode) |
| `workbook_id` | string | ID of EXISTING workbook (update mode) |

**Rule:** Provide EITHER workbook_name (create) OR workbook_id (update)

### Worksheets (Array)
```python
worksheets=[
    {
        "name": "Sheet Name",               # Required
        "description": "sales tracker",     # Optional (for auto-detection)
        "columns": ["Col1", "Col2"],        # Optional (explicit or auto-detected)
        "data": [[row1], [row2]],          # Optional (or auto-generated samples)
        "formulas": [                       # Optional
            {"cell": "C1", "formula": "sum column B"},
            {"range": "D1:D10", "formula": "multiply A1 by B1"}
        ],
        "chart": {                          # Optional
            "type": "column",               # column, bar, line, pie, scatter, area
            "range": "A1:C10",
            "title": "Chart Title"
        }
    }
]
```

### Global Formulas (Array)
```python
formulas=[
    {
        "sheet": "Data",                    # Required
        "cell": "E1",                       # Use cell OR range
        "formula": "sum column C"           # Natural language or Excel syntax
    },
    {
        "sheet": "Summary",
        "cell": "B1",
        "formula": "=SUM('Data'!C:C)"      # Cross-sheet reference
    }
]
```

### Global Charts (Array)
```python
charts=[
    {
        "sheet": "Data",                    # Required
        "type": "line",                     # column, bar, line, pie, scatter, area
        "range": "A1:C10",                  # Required
        "title": "Sales Trend"              # Required
    }
]
```

### Legacy (Backward Compatibility)
| Parameter | Type | Description |
|-----------|------|-------------|
| `sheet_description` | string | Single-sheet natural language description |
| `data_structure` | dict | Single-sheet columns/data specification |
| `include_formulas` | bool | Auto-add formulas (default: true) |
| `include_charts` | bool | Auto-generate charts (default: true) |

---

## 🎯 Formula Types

### 1. Natural Language
```python
"formula": "sum column C"
"formula": "average column D"
"formula": "multiply column B by column C"
"formula": "count column A"
```

**Converted to:**
- `=SUM(C:C)`
- `=AVERAGE(D:D)`
- `=B2*C2`
- `=COUNT(A:A)`

### 2. Direct Excel Syntax
```python
"formula": "=SUM(C:C)"
"formula": "=AVERAGE(D:D)"
"formula": "=B2*C2"
"formula": "=VLOOKUP(A2, Sheet2!A:B, 2, FALSE)"
```

**Used as-is** (no conversion)

### 3. Cross-Sheet References
```python
"formula": "=SUM('Sales Data'!C:C)"
"formula": "=AVERAGE('Q1 Results'!B:B)"
"formula": "='Sheet1'!A1 * 'Sheet2'!B1"
```

**Note:** Use single quotes for sheet names with spaces

---

## 📊 Chart Types

| Type | Excel Name | Use For |
|------|------------|---------|
| `column` | ColumnClustered | Comparisons, categories |
| `bar` | BarClustered | Horizontal comparisons |
| `line` | Line | Trends, timelines |
| `pie` | Pie | Distributions, percentages |
| `scatter` | XYScatter | Correlations |
| `area` | Area | Cumulative trends |

---

## 🔥 Real-World Examples

### Example 1: Complete Sales Report
```python
result = microsoft_excel_smart_sheet_builder(
    workbook_name="Q1 2025 Sales Report",
    worksheets=[
        # Raw sales data
        {
            "name": "Sales Transactions",
            "columns": ["Date", "Rep", "Product", "Quantity", "Price", "Total"],
            "formulas": [
                {"cell": "F2", "formula": "multiply column D by column E"},
                {"cell": "F100", "formula": "sum column F"}
            ]
        },
        # Summary by rep
        {
            "name": "Rep Summary",
            "columns": ["Rep", "Total Sales", "Avg Deal Size", "Deal Count"],
            "chart": {
                "type": "bar",
                "range": "A1:B20",
                "title": "Sales by Rep"
            }
        },
        # Charts dashboard
        {
            "name": "Dashboard",
            "chart": {
                "type": "line",
                "range": "'Sales Transactions'!A1:F100",
                "title": "Sales Trend"
            }
        }
    ]
)
```

### Example 2: Financial Model with Cross-Sheet Calculations
```python
result = microsoft_excel_smart_sheet_builder(
    workbook_name="Financial Model",
    worksheets=[
        {
            "name": "Revenue",
            "columns": ["Month", "Product A", "Product B", "Product C"],
            "formulas": [
                {"cell": "E2", "formula": "sum column B, column C, column D"}
            ]
        },
        {
            "name": "Expenses",
            "columns": ["Month", "Salaries", "Rent", "Marketing"],
            "formulas": [
                {"cell": "E2", "formula": "=B2+C2+D2"}
            ]
        },
        {
            "name": "Profit",
            "columns": ["Month", "Total Revenue", "Total Expenses", "Net Profit"],
            "formulas": [
                {"cell": "B2", "formula": "=Revenue!E2"},
                {"cell": "C2", "formula": "=Expenses!E2"},
                {"cell": "D2", "formula": "=B2-C2"}
            ],
            "chart": {
                "type": "column",
                "range": "A1:D12",
                "title": "Monthly Profit"
            }
        }
    ]
)
```

### Example 3: Update Existing Workbook
```python
# Add new calculations to existing workbook
result = microsoft_excel_smart_sheet_builder(
    workbook_id="existing_workbook_id",
    formulas=[
        # Add profit margin calculation
        {"sheet": "Sales", "cell": "G1", "formula": "Profit Margin"},
        {"sheet": "Sales", "cell": "G2", "formula": "=(F2-E2)/F2"},
        
        # Add year-to-date total
        {"sheet": "Summary", "cell": "B10", "formula": "=SUM(Sales!F:F)"}
    ],
    charts=[
        # Add trend chart
        {"sheet": "Sales", "type": "line", "range": "A1:G50", "title": "Sales Trend"}
    ]
)
```

---

## ⚡ Performance

| Operation | Speed | Replaces |
|-----------|-------|----------|
| Create 3-sheet workbook | ~5 sec | 10+ tool calls |
| Add 5 formulas | ~2 sec | 5 tool calls |
| Add 2 charts | ~1 sec | 2 tool calls |
| Complete report | ~8 sec | 20+ tool calls |

**Efficiency gain:** 70-90% reduction in API calls

---

## ✅ Return Structure

```python
{
    "success": True,
    "mode": "create",  # or "update"
    "workbook_id": "abc123...",
    "web_url": "https://onedrive.live.com/...",
    "worksheets_created": ["Sales Data", "Summary", "Charts"],
    "worksheets_updated": [],
    "formulas_added": 5,
    "formulas": [
        {"sheet": "Sales Data", "cell": "C10", "formula": "=SUM(C:C)"},
        {"sheet": "Summary", "cell": "B1", "formula": "=SUM('Sales Data'!C:C)"}
    ],
    "charts_created": 2,
    "charts": [
        {"sheet": "Sales Data", "type": "ColumnClustered", "title": "Sales by Rep"},
        {"sheet": "Charts", "type": "Pie", "title": "Regional Distribution"}
    ],
    "ready_for_data": True
}
```

---

## 🎓 AI Agent Best Practices

### When to Use This Tool

✅ **Use when:**
- Creating multi-sheet workbooks
- Need formulas AND charts together
- Updating existing workbooks
- Cross-sheet calculations needed
- User wants "comprehensive report"

❌ **Don't use when:**
- Simple single-cell update → Use `microsoft_excel_update_range`
- Just reading data → Use `microsoft_excel_get_range`
- Only need to delete → Use delete tools

### AI Response Templates

**Creating:**
> "I'll create a comprehensive Q1 Sales Report workbook with 3 sheets: Sales Data (with transactions and totals), Summary (with cross-sheet calculations), and Charts (with trend and distribution visualizations)."

**Updating:**
> "I'll add those profit margin formulas to your existing Sales workbook and create a trend chart."

**Legacy/Simple:**
> "I'll create a sales tracker with columns for rep names, months, and amounts, plus automatic totals."

---

## 🔧 Troubleshooting

### Issue: "Must provide either workbook_name or workbook_id"
**Fix:** Specify one mode - create (workbook_name) or update (workbook_id)

### Issue: Formula not calculating
**Fix:** Use `microsoft_excel_calculate(workbook_id)` to force recalculation

### Issue: Cross-sheet formula error
**Fix:** Use single quotes: `=SUM('Sheet Name'!C:C)` not `=SUM(Sheet Name!C:C)`

### Issue: Chart not showing all data
**Fix:** Verify range includes headers: `A1:C10` not `A2:C10`

---

## 📚 Summary

**microsoft_excel_smart_sheet_builder** is now your **ONE-STOP TOOL** for:

1. **Create** complete workbooks from scratch
2. **Update** existing workbooks granularly
3. **Formulas** (natural language OR Excel syntax)
4. **Charts** (multiple types, multiple sheets)
5. **Cross-sheet** calculations and references

**Replaces 20+ individual tool calls with ONE comprehensive operation.**
