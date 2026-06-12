# 🎯 SMART Sheet Builder - Build Excel from Scratch

## Overview

**`excel_smart_sheet_builder`** creates complete, professional Excel workbooks from natural language descriptions. No manual setup required—just describe what you need.

---

## 🚀 What It Does

### Automatic Features:
1. **Column Detection** - Recognizes structure from description
2. **Sample Data** - Generates realistic placeholder data
3. **Smart Formulas** - Adds SUM/AVERAGE for numeric columns
4. **Auto Charts** - Creates appropriate visualizations
5. **Summary Sheet** - Documents workbook structure
6. **Professional Ready** - Formatted and ready for real data

---

## 📊 Pattern Recognition

### Sales/Revenue Tracking
**Description:** `"sales tracker with rep performance"`

**Auto-Creates:**
```
Columns: Sales Rep | Month | Amount | Region
Formulas: SUM(Amount), AVERAGE(Amount)
Chart: Column chart showing sales by rep
Sample Data: 5 rows with realistic sales figures
```

### Expense Reports
**Description:** `"expense report with budget tracking"`

**Auto-Creates:**
```
Columns: Category | Date | Amount | Vendor
Formulas: Total expenses, Average per category
Chart: Pie chart showing expense breakdown
Sample Data: Common expense categories
```

### Project Management
**Description:** `"project timeline with milestones"`

**Auto-Creates:**
```
Columns: Task | Owner | Start Date | End Date | Status
Formulas: Count of tasks by status
Chart: Bar chart showing task distribution
Sample Data: 5 sample tasks with dates
```

### Inventory Management
**Description:** `"inventory tracker with stock levels"`

**Auto-Creates:**
```
Columns: Product | SKU | Quantity | Price | Supplier
Formulas: Total value, Item count
Chart: Column chart showing stock by product
Sample Data: 5 sample products
```

### Customer Database
**Description:** `"customer database with contact info"`

**Auto-Creates:**
```
Columns: Name | Email | Phone | Company | Status
Formulas: Customer count by status
Chart: Pie chart showing status distribution
Sample Data: 5 sample contacts
```

---

## 🎯 Usage Examples

### Example 1: Quick Sales Tracker
```python
result = excel_smart_sheet_builder(
    workbook_name="Q1 Sales Tracker",
    sheet_description="sales tracker with monthly totals and regional breakdown"
)

# Creates workbook with:
# - Data sheet with headers + 5 sample rows
# - SUM formulas for totals
# - AVERAGE formulas for metrics
# - Column chart showing sales trends
# - Summary sheet documenting structure
```

### Example 2: Custom Structure
```python
result = excel_smart_sheet_builder(
    workbook_name="Team Expenses",
    sheet_description="expense tracking",
    data_structure={
        "columns": ["Date", "Team Member", "Category", "Amount", "Receipt #"],
        "sample_data": [
            ["2025-01-15", "Alice", "Travel", 250, "RCP-001"],
            ["2025-01-16", "Bob", "Meals", 45, "RCP-002"]
        ],
        "chart_type": "bar"
    },
    include_formulas=True
)
```

### Example 3: Simple Template (No Formulas/Charts)
```python
result = excel_smart_sheet_builder(
    workbook_name="Simple Contact List",
    sheet_description="customer contacts",
    include_formulas=False,
    include_charts=False
)

# Creates basic structure only
# Ready for manual data entry
```

---

## 🧠 Intelligence Features

### 1. Column Type Detection
```python
# Automatically recognizes column types:
"Amount" → Numeric (adds SUM/AVERAGE)
"Date" → Date format (generates sequential dates)
"Status" → Text (uses predefined values)
"Email" → Email format (generates valid emails)
```

### 2. Smart Chart Selection
```python
# Chooses chart type based on description:
"timeline" → Line chart
"comparison" → Bar chart
"distribution" → Pie chart
"tracking" → Column chart (default)
```

### 3. Sample Data Generation
```python
# Generates realistic sample data:
Dates: Sequential dates from today backward
Amounts: Graduated values (1000, 1200, 1400...)
Names: Common business names
Statuses: Active/Pending/Complete/On Hold
Categories: Category A/B/C/D/E
```

---

## 📋 What Gets Created

### Data Sheet
```
Row 1: Column Headers (Bold, formatted)
Row 2-6: Sample data matching column types
Row 7: [Blank]
Row 8: TOTALS + SUM formulas
Row 9: AVERAGE + AVERAGE formulas
```

### Summary Sheet
```
Workbook Summary
Created: [timestamp]
Columns: [count]
Sample Rows: [count]
Formulas Added: [count]
Chart Created: Yes/No

Column Structure:
  1. [Column Name] - [Type]
  2. [Column Name] - [Type]
  ...
```

---

## 🔧 Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workbook_name` | string | ✅ Yes | Name for workbook (e.g., "Q1 Sales") |
| `sheet_description` | string | ✅ Yes | Natural language description |
| `data_structure` | dict | ❌ No | Custom columns/data override |
| `include_formulas` | bool | ❌ No | Add SUM/AVERAGE (default: true) |
| `include_charts` | bool | ❌ No | Create chart (default: true) |
| `include_formatting` | bool | ❌ No | Professional format (default: true) |

---

## 📤 Return Structure

```python
{
    "success": True,
    "workbook_id": "abc123...",
    "web_url": "https://onedrive.live.com/...",
    "structure": {
        "columns": ["Sales Rep", "Month", "Amount", "Region"],
        "sample_rows": 5,
        "formulas_added": [
            {"column": "Amount", "formula": "=SUM(C:C)"}
        ],
        "chart_created": True,
        "chart_type": "ColumnClustered"
    },
    "sheets": ["Data", "Summary"],
    "ready_for_data": True
}
```

---

## 🎓 AI Agent Integration

### When AI Should Suggest This Tool:

✅ **Use SMART Sheet Builder when:**
- User says "create a spreadsheet for..."
- User needs a template or starting point
- User has no existing data
- User describes a tracking/reporting need

❌ **Don't use when:**
- User has CSV/JSON data (use `excel_smart_import_csv`)
- User wants to modify existing workbook
- User needs only formulas (use `excel_smart_formula_builder`)

### Example AI Responses:

**User:** "I need to track sales for my team"

**AI:** "I'll create a sales tracker workbook with columns for rep names, monthly sales, and regional performance. It will include auto-calculated totals and a visualization chart."

```python
excel_smart_sheet_builder(
    workbook_name="Team Sales Tracker",
    sheet_description="sales tracker with rep performance and monthly totals"
)
```

---

## 🔗 Integration with Other Tools

### Typical Workflow:
```python
# 1. Build structure from scratch
result = excel_smart_sheet_builder(
    workbook_name="Sales Q1",
    sheet_description="sales tracker"
)

# 2. Add real data to replace samples
excel_update_range(
    workbook_id=result['workbook_id'],
    worksheet_name="Data",
    range_address="A2:D50",
    values=actual_sales_data
)

# 3. Refresh formulas
excel_calculate(
    workbook_id=result['workbook_id']
)

# 4. Share with team
excel_share_workbook(
    workbook_id=result['workbook_id'],
    permissions="edit"
)
```

---

## 🎯 Pattern Recognition Keywords

### Detected Patterns:

| Keywords | Auto-Generated Columns |
|----------|----------------------|
| `sales`, `revenue`, `income` | Sales Rep, Month, Amount, Region |
| `expense`, `cost`, `spending` | Category, Date, Amount, Vendor |
| `project`, `task`, `timeline` | Task, Owner, Start Date, End Date, Status |
| `inventory`, `stock`, `products` | Product, SKU, Quantity, Price, Supplier |
| `customer`, `contact`, `client` | Name, Email, Phone, Company, Status |
| *(default)* | Name, Date, Value, Category, Notes |

---

## 🚀 Advanced Customization

### Override Auto-Detection:
```python
excel_smart_sheet_builder(
    workbook_name="Custom Report",
    sheet_description="generic tracker",
    data_structure={
        "columns": ["Custom Col 1", "Custom Col 2", "Custom Col 3"],
        "sample_data": [
            ["Value A1", "Value B1", "Value C1"],
            ["Value A2", "Value B2", "Value C2"]
        ],
        "formulas": ["sum column C"],  # Natural language
        "chart_type": "line"
    }
)
```

---

## ⚡ Performance

- **Average duration:** ~3 seconds
- **Creates:** 2 sheets (Data + Summary)
- **Adds:** 5+ sample rows
- **Formulas:** 2-6 auto-calculated fields
- **Chart:** 1 visualization
- **Rate limit:** 20 workbooks/minute

---

## ✅ Success Indicators

**Look for in response:**
- `"success": True`
- `"ready_for_data": True`
- `"formulas_added": [...]` - List of formulas created
- `"chart_created": True`
- `"web_url"` - Link to open workbook

---

## 🎨 Use Cases

### 1. Quick Prototyping
"I need a sales tracker but don't have data yet" → Creates template with sample data

### 2. Team Templates
"Create a standard expense report for my team" → Shareable template with formulas

### 3. Client Deliverables
"Build a project status tracker for client review" → Professional workbook ready to populate

### 4. Data Collection
"Set up a form for collecting customer info" → Structured columns ready for input

### 5. Ad-hoc Analysis
"I need to analyze regional sales" → Quick structure to paste data into

---

## 🔍 Comparison with Other Tools

| Tool | Use When | Output |
|------|----------|--------|
| **smart_sheet_builder** | No data, need structure from scratch | Template with sample data |
| **smart_import_csv** | Have CSV data to import | Workbook with your data |
| **smart_financial_report** | Have financial data dict | Multi-sheet financial report |
| **create_workbook** | Need blank workbook | Empty workbook, manual setup |

---

## 💡 Pro Tips

### 1. Be Descriptive
```python
# ❌ Vague
"create a tracker"

# ✅ Specific
"sales tracker with rep names, monthly revenue, and quarterly totals"
```

### 2. Mention Key Metrics
```python
# Mentions "totals" → Auto-adds SUM formulas
"expense report with category totals"

# Mentions "average" → Auto-adds AVERAGE formulas
"sales with average per rep"
```

### 3. Specify Chart Needs
```python
# "timeline" → Line chart
"project timeline with milestones"

# "comparison" → Bar chart
"compare sales across regions"

# "breakdown" → Pie chart
"expense breakdown by category"
```

---

## 🎯 Summary

**SMART Sheet Builder** = The fastest way to create professional Excel workbooks from scratch.

**One sentence, 30 seconds:**
```python
excel_smart_sheet_builder(
    workbook_name="Q1 Sales",
    sheet_description="sales tracker with totals and charts"
)
```

**vs. Manual (5-10 minutes):**
1. Create workbook
2. Add worksheet
3. Type headers
4. Format headers
5. Add sample data
6. Create formulas
7. Create chart
8. Add summary

**Result:** Fully functional, professional workbook ready for real data.
