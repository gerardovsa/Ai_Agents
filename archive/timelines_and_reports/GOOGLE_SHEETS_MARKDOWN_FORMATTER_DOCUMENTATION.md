# Google Sheets Markdown Formatter - Custom Tool 📊

**Location**: `google_workspace/sheets_markdown_formatter.py`  
**Integration**: Used by `google_sheets_create()` with `parse_markdown=True`  
**Purpose**: Convert markdown syntax to native Google Sheets formatting

---

## 🎯 Overview

This is a **custom-built markdown parser** specifically for Google Sheets that converts markdown syntax into Google Sheets API formatting requests. It allows AI agents to create beautifully formatted spreadsheets using simple markdown syntax.

### How It Works

```python
# In google_sheets.py
google_sheets_create(
    title="Sales Report",
    headers=["# Product", "**Q3**", "**Q4**", "[RED]Alert[/RED]"],
    data=[
        ["**Widget**", "100", "150", "[GREEN]Up[/GREEN]"],
        ["*Gadget*", "200", "180", "[RED]Down[/RED]"]
    ],
    parse_markdown=True  # ← Activates markdown formatter
)
```

**Result**: Professional spreadsheet with:
- Bold headers with gray background
- Colored text (green/red indicators)
- Formatted cells with borders
- Clean, readable layout

---

## 📝 Supported Markdown Syntax

### Text Formatting

| Syntax | Result | Example |
|--------|--------|---------|
| `**text**` | **Bold** | `**John Doe**` → Bold text |
| `*text*` | *Italic* | `*30 years old*` → Italic text |
| `# text` | Header Level 1 | `# Patient Records` → Bold, 18pt, gray bg |
| `## text` | Header Level 2 | `## Quarterly Report` → Bold, 16pt, gray bg |
| `### text` | Header Level 3 | `### Summary` → Bold, 14pt, gray bg |

### Text Colors (v1.0 - Verbose)

| Syntax | Result |
|--------|--------|
| `[RED]text[/RED]` | <span style="color:red">Red text</span> |
| `[GREEN]text[/GREEN]` | <span style="color:green">Green text</span> |
| `[BLUE]text[/BLUE]` | <span style="color:blue">Blue text</span> |
| `[YELLOW]text[/YELLOW]` | <span style="color:#CC9900">Yellow text</span> |
| `[ORANGE]text[/ORANGE]` | <span style="color:orange">Orange text</span> |
| `[PURPLE]text[/PURPLE]` | <span style="color:purple">Purple text</span> |
| `[GRAY]text[/GRAY]` | <span style="color:gray">Gray text</span> |
| `[BLACK]text[/BLACK]` | <span style="color:black">Black text</span> |

### Text Colors (v2.0 - Shortened - NO CLOSING TAG)

| Syntax | Result | Notes |
|--------|--------|-------|
| `[R]text` | <span style="color:red">Red text</span> | No `[/R]` needed |
| `[G]text` | <span style="color:green">Green text</span> | No `[/G]` needed |
| `[B]text` | <span style="color:blue">Blue text</span> | No `[/B]` needed |
| `[P]text` | <span style="color:purple">Purple text</span> | No `[/P]` needed |
| `[GR]text` | <span style="color:gray">Gray text</span> | No `[/GR]` needed |
| `[BK]text` | <span style="color:black">Black text</span> | No `[/BK]` needed |

**Example**: `[R]CRITICAL` → Red text without closing tag

### Background Colors (v1.0 - Verbose)

| Syntax | Result |
|--------|--------|
| `[BG:LIGHTGRAY]text[/BG]` | Light gray background |
| `[BG:LIGHTRED]text[/BG]` | Light red background |
| `[BG:LIGHTGREEN]text[/BG]` | Light green background |
| `[BG:LIGHTBLUE]text[/BG]` | Light blue background |
| `[BG:LIGHTYELLOW]text[/BG]` | Light yellow background |
| `[BG:LIGHTORANGE]text[/BG]` | Light orange background |
| `[BG:LIGHTPURPLE]text[/BG]` | Light purple background |
| `[BG:WHITE]text[/BG]` | White background |

### Background Colors (v2.0 - Shortened - NO CLOSING TAG)

| Syntax | Result | Notes |
|--------|--------|-------|
| `{LR}text` | Light red background | No closing needed |
| `{LG}text` | Light green background | No closing needed |
| `{LB}text` | Light blue background | No closing needed |
| `{LP}text` | Light purple background | No closing needed |
| `{LGR}text` | Light gray background | No closing needed |

**Example**: `{LG}Approved` → Light green background without closing tag

### Alignment (v2.0 - Must be at start of cell)

| Syntax | Result | Example |
|--------|--------|---------|
| `(L)text` | Left aligned | `(L)Total Sales` |
| `(C)text` | Center aligned | `(C)$1,000` |
| `(R)text` | Right aligned | `(R)15%` |

**Note**: Alignment code must be **at the beginning** of the cell text.

### Tables & Borders

The formatter automatically:
- ✅ Adds borders to all cells when `auto_borders=True` (default)
- ✅ Parses markdown table syntax (pipe-delimited tables)
- ✅ Skips separator lines (`|---|---|`)

**Markdown Table Example**:
```markdown
| **Name** | *Age* | City |
|----------|-------|------|
| John     | 30    | NYC  |
| Jane     | 25    | LA   |
```

---

## 🚀 Usage Examples

### Example 1: Sales Report with Indicators

```python
google_sheets_create(
    title="Q4 Sales Report",
    headers=["# Product", "**Q3**", "**Q4**", "**Trend**"],
    data=[
        ["**Widget A**", "100", "150", "[G]↑ 50%"],
        ["**Widget B**", "200", "180", "[R]↓ 10%"],
        ["**Gadget C**", "50", "75", "[G]↑ 50%"]
    ],
    parse_markdown=True
)
```

**Result**:
- Header row: Bold with gray background
- Product names: Bold
- Trend indicators: Green (up) or Red (down) arrows
- All cells: Bordered table

### Example 2: Patient Records with Status

```python
google_sheets_create(
    title="Patient Status Board",
    headers=["# Patient Name", "**Age**", "**Status**", "**Alert Level**"],
    data=[
        ["John Doe", "45", "[GREEN]Stable[/GREEN]", "{LG}Normal"],
        ["Jane Smith", "67", "[YELLOW]Monitored[/YELLOW]", "{LR}High Risk"],
        ["Bob Jones", "52", "[RED]Critical[/RED]", "{LR}URGENT"]
    ],
    parse_markdown=True
)
```

**Result**:
- Status column: Colored text (green/yellow/red)
- Alert Level: Colored backgrounds (light green/light red)
- Clean, professional medical status board

### Example 3: Financial Dashboard with Alignment

```python
google_sheets_create(
    title="Financial Summary",
    headers=["# Account", "(C)**Q4 2025**", "(R)**Amount**"],
    data=[
        ["Revenue", "(C)Total", "(R)$150,000"],
        ["Expenses", "(C)Total", "(R)$95,000"],
        ["**Net Profit**", "", "(R)**$55,000**"]
    ],
    parse_markdown=True
)
```

**Result**:
- Headers: Left/Center/Right aligned
- Dollar amounts: Right-aligned
- Net Profit row: Bold for emphasis

### Example 4: V2.0 Shortened Syntax (Fastest)

```python
google_sheets_create(
    title="Status Board",
    headers=["# Task", "**Owner**", "**Status**"],
    data=[
        ["Deploy API", "John", "[G]Complete"],      # Green text
        ["Test Suite", "Jane", "{LG}In Progress"],  # Light green bg
        ["Bug Fix", "Bob", "[R]Blocked"]            # Red text
    ],
    parse_markdown=True
)
```

**Result**: Same formatting as verbose syntax, but cleaner code.

---

## 🔧 Technical Implementation

### Architecture

```
google_sheets_create(parse_markdown=True)
    ↓
sheets_markdown_formatter.format_data_with_markdown()
    ↓
MarkdownToSheetsFormatter.parse_data_with_markdown()
    ↓
For each cell:
    - parse_cell_markdown() → (clean_text, format_dict)
    - _create_cell_format_request() → API request
    ↓
Returns:
    - clean_data (markdown removed)
    - clean_headers (markdown removed)
    - format_requests (Google Sheets API formatting)
```

### Google Sheets API Requests Generated

The formatter generates these API request types:

1. **repeatCell** - Format individual cells
   ```python
   {
       'repeatCell': {
           'range': {...},
           'cell': {
               'userEnteredFormat': {
                   'textFormat': {'bold': True, 'foregroundColor': {...}},
                   'backgroundColor': {...},
                   'horizontalAlignment': 'CENTER'
               }
           },
           'fields': 'userEnteredFormat(...)'
       }
   }
   ```

2. **updateBorders** - Add borders to tables
   ```python
   {
       'updateBorders': {
           'range': {...},
           'top': border_style,
           'bottom': border_style,
           'left': border_style,
           'right': border_style,
           'innerHorizontal': border_style,
           'innerVertical': border_style
       }
   }
   ```

### Color RGB Values

**Text Colors**:
- RED: `{red: 0.9, green: 0.2, blue: 0.2}`
- GREEN: `{red: 0.2, green: 0.8, blue: 0.2}`
- BLUE: `{red: 0.2, green: 0.5, blue: 0.9}`
- YELLOW: `{red: 0.8, green: 0.6, blue: 0.0}` (darker for visibility)
- ORANGE: `{red: 0.9, green: 0.5, blue: 0.1}` (darker for visibility)
- PURPLE: `{red: 0.7, green: 0.3, blue: 0.9}`
- GRAY: `{red: 0.5, green: 0.5, blue: 0.5}`

**Background Colors**:
- LIGHTRED: `{red: 0.95, green: 0.8, blue: 0.8}`
- LIGHTGREEN: `{red: 0.85, green: 0.95, blue: 0.85}`
- LIGHTBLUE: `{red: 0.85, green: 0.9, blue: 0.95}`
- LIGHTGRAY: `{red: 0.9, green: 0.9, blue: 0.9}`

---

## 📊 Performance & Behavior

### What Gets Removed
The formatter **removes markdown syntax** from cell values before writing to Google Sheets:
- `**Bold**` → `Bold`
- `[RED]text[/RED]` → `text`
- `# Header` → `Header`
- `{LG}text` → `text`

The formatting is applied via **separate API calls** using `batchUpdate()`.

### API Call Efficiency

**Without markdown formatting**:
```python
google_sheets_create(title="Report", data=[[...]])
# API calls: 2 (create + write data)
```

**With markdown formatting**:
```python
google_sheets_create(title="Report", data=[[...]], parse_markdown=True)
# API calls: 3 (create + write data + batchUpdate formatting)
```

**Cost**: +1 API call for all formatting (very efficient!)

### Auto-Borders

When `auto_borders=True` (default):
- Adds borders to entire table automatically
- Single `updateBorders` request covers all cells
- Thickness: 1px
- Color: Light gray `{red: 0.8, green: 0.8, blue: 0.8}`

To disable: `google_sheets_create(..., parse_markdown=True, auto_borders=False)`

---

## 🎨 Common Use Cases

### 1. Status Dashboards
```python
headers=["# Task", "**Owner**", "**Status**"]
data=[
    ["Deploy", "John", "[G]Complete"],
    ["Test", "Jane", "[R]Blocked"]
]
```

### 2. Financial Reports
```python
headers=["# Account", "(R)**Amount**"]
data=[
    ["Revenue", "(R)$150,000"],
    ["Expenses", "(R)$95,000"],
    ["**Net Profit**", "(R)**$55,000**"]
]
```

### 3. Medical Records
```python
headers=["# Patient", "**Status**", "**Alert**"]
data=[
    ["John Doe", "[GREEN]Stable[/GREEN]", "{LG}Normal"],
    ["Jane Smith", "[RED]Critical[/RED]", "{LR}Urgent"]
]
```

### 4. Project Tracking
```python
headers=["# Feature", "**Priority**", "**Progress**"]
data=[
    ["API v2", "[R]HIGH", "75%"],
    ["UI Redesign", "[YELLOW]MED", "30%"],
    ["Docs", "[G]LOW", "90%"]
]
```

---

## 🔍 Integration with New Smart Builder

The markdown formatter integrates seamlessly with the new `google_sheets_smart_builder`:

```python
google_sheets_smart_builder(
    spreadsheet_name="Status Report",
    sheets=[
        {
            "name": "Tasks",
            "headers": ["# Task", "**Owner**", "**Status**"],
            "data": [
                ["Deploy", "John", "[G]Complete"],
                ["Test", "Jane", "{LG}In Progress"]
            ]
        }
    ]
    # Note: Smart builder currently doesn't expose parse_markdown
    # This is a potential enhancement (add parse_markdown parameter)
)
```

**TODO**: Add `parse_markdown=True` parameter to `google_sheets_smart_builder` to enable markdown in multi-sheet creation.

---

## ⚠️ Limitations & Considerations

### Current Limitations

1. **Sheet ID**: Always targets `sheetId: 0` (first sheet)
   - Works fine for single-sheet creation
   - For multi-sheet, would need sheet-specific formatting

2. **No Nested Formatting**: Can't combine all features in one cell
   - ✅ `**Bold**` + `[RED]` works
   - ❌ Complex nesting may conflict

3. **Alignment Must Be First**: `(L)`, `(R)`, `(C)` must be at cell start
   - ✅ `(R)$1,000`
   - ❌ `Total (R)$1,000` won't align

4. **No Column Width**: Doesn't auto-adjust column widths
   - Sheets defaults to standard width
   - Manual adjustment needed for very long content

### Best Practices

1. **Use Shortened Syntax (v2.0)** for cleaner code:
   - `[R]text` instead of `[RED]text[/RED]`
   - `{LG}text` instead of `[BG:LIGHTGREEN]text[/BG]`

2. **Headers as First Row**: Put headers in `headers=[]` parameter
   - Ensures correct row offset for data formatting

3. **Consistent Alignment**: Use alignment codes consistently across columns
   - `(R)` for all dollar amounts
   - `(C)` for all percentages

4. **Test Complex Formatting**: Test multi-format cells before production

---

## 🚀 Future Enhancements

### Planned Improvements

1. **Smart Builder Integration**
   - Add `parse_markdown` to `google_sheets_smart_builder`
   - Enable per-sheet markdown settings
   - Support multi-sheet formatting

2. **Auto Column Width**
   - Detect content width
   - Auto-adjust column widths based on content

3. **More Alignment Options**
   - Vertical alignment (top/middle/bottom)
   - Text wrapping control

4. **Number Formatting**
   - Currency: `[$]1000` → `$1,000.00`
   - Percentage: `[%]75` → `75%`
   - Date: `[DATE]2025-12-16` → `Dec 16, 2025`

5. **Cell Merging**
   - Syntax: `[MERGE:3]text` → Merge 3 cells

6. **Conditional Formatting**
   - Syntax: `[IF>100:RED]125` → Red if >100

---

## 📚 Code Reference

**Main Function**:
```python
format_data_with_markdown(
    data: List[List[Any]],
    headers: List[str] = None,
    auto_borders: bool = True
) -> Tuple[List[List[Any]], List[str], List[Dict]]
```

**Returns**:
- `clean_data`: Data with markdown removed
- `clean_headers`: Headers with markdown removed
- `format_requests`: Google Sheets API formatting requests

**Class**:
```python
MarkdownToSheetsFormatter()
    - parse_cell_markdown(text) → (clean_text, format_dict)
    - parse_data_with_markdown(data) → (clean_data, format_requests)
    - add_border_formatting(rows, cols) → [border_requests]
```

---

## ✅ Summary

The **Google Sheets Markdown Formatter** is a powerful custom tool that:

- ✅ Converts markdown → native Google Sheets formatting
- ✅ Supports text formatting (bold, italic, headers)
- ✅ Supports colors (text + backgrounds)
- ✅ Supports alignment (left/center/right)
- ✅ Auto-adds borders for professional tables
- ✅ Works seamlessly with `google_sheets_create()`
- ✅ Generates efficient API requests (single batchUpdate)
- ✅ V2.0 shortened syntax for cleaner code

**Impact**: Enables AI agents to create **professional, formatted spreadsheets** using simple markdown syntax instead of complex API calls.

**Status**: ✅ Production Ready (in use since Nov 2025)
