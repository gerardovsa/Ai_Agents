# Google Docs & Charts - Smart Tools Guide

**AI Agent Instructions for Creating Professional Reports with Charts**

---

## 🎯 Quick Overview

The AI has THREE main tools for creating professional documents with charts:

1. **`google_docs_create_professional_report_with_charts`** - ⭐ RECOMMENDED for full reports
2. **`google_charts_create`** - For standalone spreadsheet charts
3. **`google_docs_insert_chart`** - For adding charts to existing docs (limited - see notes)

---

## ⭐ Tool 1: Professional Report with Charts (RECOMMENDED)

**Function**: `google_docs_create_professional_report_with_charts`

**When to Use**:
- User wants a complete report with multiple charts
- Financial reports, business analytics, presentations
- Clean stakeholder-ready documents
- "Create a report with charts showing..."

### What It Creates:

1. **Clean Google Doc** with:
   - Professional formatting (no instructions in document)
   - Chart placeholders (italicized text: ***Copy and paste chart over this placeholder***)
   - Figure references (Figure 1, Figure 2, etc.) as hyperlinks
   - Space for analysis below each chart
   - Executive summary section

2. **Google Spreadsheet** with:
   - Multiple charts (each in own sheet tab OR all in one sheet)
   - Black, bold, centered chart titles
   - Axis labels with units (e.g., "Amount ($)")
   - Legends with proper labels
   - Data positioned next to charts
   - Editable by anyone with link

### How to Call:

```python
result = google_docs_create_professional_report_with_charts(
    report_title="Q1 2025 Financial Performance Report",
    charts_config=[
        {
            'title': 'Monthly Revenue Q1 2025',
            'headers': ['Month', 'Revenue ($)', 'Expenses ($)', 'Profit ($)'],
            'data': [
                ['January', 125000, 85000, 40000],
                ['February', 138000, 92000, 46000],
                ['March', 145000, 95000, 50000]
            ],
            'chart_type': 'COLUMN',
            'x_axis': 'Month',
            'y_axis': 'Amount ($)'
        },
        {
            'title': 'Quarterly Revenue Comparison',
            'headers': ['Quarter', 'Q1 2024', 'Q1 2025'],
            'data': [
                ['Revenue', 350000, 408000],
                ['Expenses', 250000, 272000],
                ['Profit', 100000, 136000]
            ],
            'chart_type': 'BAR',
            'x_axis': 'Metric',
            'y_axis': 'Amount ($)'
        },
        {
            'title': 'Expense Breakdown Q1 2025',
            'headers': ['Category', 'Amount ($)'],
            'data': [
                ['Salaries', 150000],
                ['Marketing', 60000],
                ['Operations', 40000],
                ['R&D', 22000]
            ],
            'chart_type': 'PIE',
            'x_axis': 'Category',
            'y_axis': 'Amount ($)'
        }
    ],
    separate_sheets=True  # True = each chart in own sheet (recommended)
)

# Return to user:
print(result['document_url'])       # Google Doc URL
print(result['spreadsheet_url'])    # Google Spreadsheet URL
print(result['instructions'])       # Step-by-step user instructions
```

### Chart Types Supported:

- `COLUMN` - Vertical bars (good for time series, comparisons)
- `BAR` - Horizontal bars (good for rankings, categories)
- `LINE` - Line graph (good for trends over time)
- `AREA` - Filled area chart (good for cumulative data)
- `PIE` - Pie chart (good for proportions, percentages)
- `SCATTER` - Scatter plot (good for correlations)
- `COMBO` - Combination chart (multiple chart types)
- `HISTOGRAM` - Histogram (good for distributions)
- `CANDLESTICK` - Financial candlestick chart
- `BUBBLE` - Bubble chart (3 dimensions)

### Return Value:

```python
{
    'document_id': '1KHf-FVzcHLA8IDgQPzfXTlCw3ZAGSeefamqw3iWCuQM',
    'document_url': 'https://docs.google.com/document/d/1KHf.../edit',
    'spreadsheet_id': '1KaEylbHv8WzBmpQscfe4lEEq9xTTPKvDzX33XFWuZY4',
    'spreadsheet_url': 'https://docs.google.com/spreadsheets/d/1KaE.../edit',
    'charts': [
        {
            'title': 'Monthly Revenue Q1 2025',
            'chart_id': 1946860284,
            'data_range': "'Chart 1 Data'!A1:D4",
            'sheet_name': 'Chart 1 Data',
            'link': 'https://docs.google.com/.../edit#gid=0&range=Chart 1 Data!A1:D4'
        },
        ...
    ],
    'instructions': 'STEP 1: Open the Google Doc...\nSTEP 2: For each chart:\n...'
}
```

### Document Structure Created:

```markdown
# Q1 2025 Financial Performance Report

## Executive Summary

This report presents the financial performance analysis for Q1 2025 with interactive visualizations.

---

## Monthly Revenue Q1 2025

***Copy and paste chart over this placeholder***

**Figure 1**: [Monthly Revenue Q1 2025](link-to-spreadsheet)

Analysis and key insights for this visualization. Refer to Figure 1 for detailed breakdown.

---

## Quarterly Revenue Comparison

***Copy and paste chart over this placeholder***

**Figure 2**: [Quarterly Revenue Comparison](link-to-spreadsheet)

Analysis and key insights for this visualization. Refer to Figure 2 for detailed breakdown.

---

[etc.]
```

### User Workflow (Tell User):

1. **Open the Google Doc** (provide URL)
2. **For each chart**:
   - Click the Figure link (e.g., "Figure 1: Monthly Revenue Q1 2025")
   - Spreadsheet opens showing chart next to data
   - Right-click chart → Copy
   - Return to document
   - Click placeholder text → Paste (Ctrl+V)
   - Chart replaces placeholder in perfect position
3. **Add analysis** - Replace generic text with insights

---

## 📊 Tool 2: Standalone Spreadsheet Chart

**Function**: `google_charts_create`

**When to Use**:
- User wants just a chart in a spreadsheet (no document)
- Quick data visualization
- Testing chart types
- "Create a chart showing..."

### How to Call:

```python
result = google_charts_create(
    title="Q1 Sales Dashboard",
    chart_type="column",
    headers=["Month", "Revenue ($)", "Expenses ($)", "Profit ($)"],
    data=[
        ["January", 125000, 85000, 40000],
        ["February", 138000, 92000, 46000],
        ["March", 145000, 95000, 50000]
    ],
    chart_options={
        'title': 'Q1 Financial Performance',
        'x_axis_title': 'Month',
        'y_axis_title': 'Amount ($)',
        'colors': ['#34a853', '#ea4335', '#4285f4'],  # Green, Red, Blue
        'width': 600,
        'height': 400,
        'legend_position': 'bottom',
        'stacked': False
    }
)

print(result['url'])  # Spreadsheet URL
print(result['spreadsheet_id'])
print(result['chart_id'])
```

### Chart Options:

- `title` - Chart title (displayed on chart)
- `subtitle` - Chart subtitle
- `x_axis_title` - X-axis label (e.g., "Month", "Category")
- `y_axis_title` - Y-axis label (e.g., "Amount ($)", "Revenue (€)")
- `width` - Chart width in pixels (default: 600)
- `height` - Chart height in pixels (default: 400)
- `position` - Chart position `{'row': 0, 'col': 5}`
- `legend_position` - 'bottom', 'top', 'left', 'right', 'none'
- `colors` - Array of hex colors `['#1a73e8', '#34a853', '#ea4335']`
- `stacked` - True/False (for column/bar/area charts)

---

## ⚠️ Tool 3: Insert Chart in Existing Doc (LIMITED)

**Function**: `google_docs_insert_chart`

**⚠️ IMPORTANT LIMITATION**: This tool has a critical API limitation:
- Google Docs API **cannot** fetch Google Sheets export URLs
- Even with public permissions, image insertion fails
- **ONLY works** if you have a Google Workspace Shared Drive

**When to Use** (rarely):
- You have a Shared Drive available
- Need to insert a chart into an existing document
- Document already has content

**Recommended Alternative**: Use `google_docs_create_professional_report_with_charts` instead, which:
- Creates clean document with chart placeholders
- User manually copies charts (works 100% of the time)
- Professional workflow that doesn't depend on API limitations

---

## 🎯 AI Decision Tree: Which Tool to Use?

```
User Request: "Create a report with charts"
├─ Multiple charts + professional document?
│  └─  Use: google_docs_create_professional_report_with_charts
│
├─ Just need a chart in spreadsheet?
│  └─  Use: google_charts_create
│
└─ Need to add chart to existing doc?
   └─ ⚠️ Use: Manual workflow (create chart, user copies it)
```

---

## 📝 Example AI Responses

### User: "Create a financial report for Q1 2025 with revenue charts"

**AI Response:**
```
I'll create a professional financial report with interactive charts for Q1 2025.

[Calls: google_docs_create_professional_report_with_charts with appropriate data]

 Report created successfully!

📄 **Google Doc**: [URL]
📊 **Spreadsheet with Charts**: [URL]

**What's included:**
- Executive summary
- 3 professional charts:
  1. Figure 1: Monthly Revenue Q1 2025 (column chart)
  2. Figure 2: Quarterly Comparison (bar chart)
  3. Figure 3: Expense Breakdown (pie chart)

**How to insert the charts:**
1. Open the document above
2. Click any "Figure X" link to open the spreadsheet
3. Right-click the chart and select "Copy"
4. Return to the document and paste over the placeholder
5. The chart will appear in the perfect position

All charts have:
- Black, centered titles
- Axis labels with units ($)
- Proper legends
- Editable data (anyone with link can edit)

Would you like me to add more charts or modify the data?
```

### User: "Show me a bar chart of sales by region"

**AI Response:**
```
I'll create a bar chart showing sales by region.

[Calls: google_charts_create with regional data]

 Chart created!

📊 **View Chart**: [Spreadsheet URL]

The chart displays:
- Horizontal bars for easy comparison
- Sales amounts in dollars
- Color-coded regions
- Interactive legend

You can edit the data directly in the spreadsheet, and the chart will update automatically.

Would you like me to create a full report document with this chart?
```

---

## 🚨 Critical Rules

### NO EMOJIS EVER
**NEVER use emojis in Google Docs or Sheets!**
-  Emojis corrupt document structure
-  Causes rendering failures
-  Breaks formatting
-  Use text descriptions instead

### Chart Title Formatting
- Titles are automatically: **Black, Bold, Centered**
- Font size: 14pt
- Don't need to manually format

### Axis Labels
- Always include units: "Amount ($)", "Revenue (€)", "Count (#)"
- Be specific: "Monthly Revenue" not just "Revenue"
- Format: "Category/Metric (Unit)"

### Data Structure
- First column = labels (x-axis, categories)
- Remaining columns = data series
- Headers are optional but recommended
- Example:
  ```python
  headers = ['Month', 'Revenue ($)', 'Expenses ($)']
  data = [
      ['Jan', 10000, 5000],
      ['Feb', 12000, 5500],
      ['Mar', 11000, 5200]
  ]
  ```

### Permissions
- All documents: "Anyone with link can EDIT"
- All spreadsheets: "Anyone with link can EDIT"
- Automatically set by the tools

---

## 🔍 Troubleshooting

### "Chart not showing in spreadsheet"
- Check the sheet tab name (Chart 1 Data, Chart 2 Data, etc.)
- Verify chart_id in return value
- Charts are positioned to the right of data (column H+)

### "Link doesn't work in document"
- Links use format: `[Text](URL)`
- Markdown is automatically converted to hyperlinks
- Check that URL is complete (starts with https://)

### "Chart has wrong data"
- Verify data array structure (2D array)
- First column = labels, remaining = data series
- Headers are separate from data
- Check data types (numbers not strings)

### "User can't copy chart"
- User must right-click the chart itself (not the cell)
- Select "Copy" (not "Copy chart link")
- Paste in document placeholder location

---

## 📚 Additional Resources

**Test File**: `C:\Users\gpoli\GIT\AI_agents\create_professional_charts.py`
- Contains working example
- Run to see complete workflow
- Generates sample report with 3 charts

**Tool Implementation**: `C:\Users\gpoli\GIT\AI_agents\tools\implementations\google_docs.py`
- Line 2713: `google_charts_create`
- Line 3187: `google_docs_create_professional_report_with_charts`
- Line 3072: `google_docs_insert_chart`

**Tool Schemas**:
- `tools/schemas/google_docs_tools.json` - Document tools
- `tools/schemas/google_charts_tools.json` - Chart tools

---

##  Success Checklist

Before telling user "Done":
- [ ] Document URL provided
- [ ] Spreadsheet URL provided
- [ ] Instructions explained (how to copy/paste charts)
- [ ] Chart types match user request
- [ ] Data is correct
- [ ] Axis labels have units
- [ ] Figure numbers are sequential
- [ ] No emojis used
- [ ] Permissions are public (anyone with link)

---

**Last Updated**: October 27, 2025  
**Version**: 1.0.0  
**Status**:  Production Ready
