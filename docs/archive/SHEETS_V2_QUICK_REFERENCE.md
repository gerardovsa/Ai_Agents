# Google Sheets Markdown v2.0 - Quick Reference

**⚠️ IMPORTANT: This syntax ONLY works in `google_sheets_create` and `google_sheets_create_multiple` tools!**

---

## 📏 Alignment (Parentheses)

```
(L)text    → Left-align
(R)text    → Right-align
(C)text    → Center-align
```

**Examples:**
```python
'(R)$125,000'        # Right-aligned number
'(C)Header'          # Centered header
'(L)Product Name'    # Left-aligned text
```

---

## 🎨 Text Colors (Square Brackets - NO closing tag)

```
[R]text     → Red 🔴 (errors, critical, negative)
[G]text     → Green 🟢 (success, active, positive)
[B]text     → Blue 🔵 (info, neutral)
[P]text     → Purple 🟣 (special, VIP)
[GR]text    → Gray ⚫ (inactive, archived)
[BK]text    → Black (default)
```

**Examples:**
```python
'[G]Active'      # Green "Active"
'[R]Blocked'     # Red "Blocked"
'[B]Info'        # Blue "Info"
```

---

## 🎨 Background Colors (Curly Braces - NO closing tag)

```
{LR}text    → Light red background
{LG}text    → Light green background
{LB}text    → Light blue background
{LP}text    → Light purple background
{LGR}text   → Light gray background
```

**Examples:**
```python
'{LG}Approved'   # Light green background
'{LR}Alert'      # Light red background
'{LB}Note'       # Light blue background
```

---

## 🔗 Stacking (Combine Multiple Formats)

**Order:** `(ALIGN)[COLOR]{BACKGROUND}text`

**Examples:**
```python
'(R)[G]{LG}+16%'         # Right, green text, light green bg
'(C)[R]{LR}BLOCKED'      # Center, red text, light red bg
'(L)[B]Info'             # Left, blue text, no background
'(R)$125K'               # Right-aligned only
'[G]Active'              # Green text only
```

---

## 💻 Code Examples

### Sales Report
```python
from tools.registry_v3 import RegistryV3

registry = RegistryV3()
result = registry.execute_tool(
    'google_sheets_create',
    title='Q4 Sales Report',
    headers=[
        '(C)# Product',
        '(R)**Q3**',
        '(R)**Q4**',
        '(R)**Change**'
    ],
    data=[
        ['(L)[G]Premium', '(R)$145K', '(R)$168K', '(R)[G]{LG}+16%'],
        ['(L)Standard', '(R)$85K', '(R)$78K', '(R)[R]{LR}-8%']
    ],
    parse_markdown=True,
    _user_id=1
)
```

### Status Dashboard
```python
result = registry.execute_tool(
    'google_sheets_create',
    title='Project Status',
    headers=['(L)# Task', '(C)**Status**', '(R)**Owner**'],
    data=[
        ['(L)API Integration', '(C)[G]{LG}Complete', '(R)Alice'],
        ['(L)UI Redesign', '(C)[R]{LR}Blocked', '(R)Bob']
    ],
    parse_markdown=True,
    _user_id=1
)
```

### Multi-Sheet Creation
```python
result = registry.execute_tool(
    'google_sheets_create_multiple',
    spreadsheets_config=[
        {
            'title': 'Sales Report',
            'headers': ['(C)Product', '(R)Revenue'],
            'data': [['(L)[G]Premium', '(R)$168K']],
            'parse_markdown': True
        },
        {
            'title': 'Inventory',
            'headers': ['(L)SKU', '(R)Stock'],
            'data': [['(L)WDG-001', '(R)[G]{LG}250']],
            'parse_markdown': True
        }
    ],
    _user_id=1
)
```

---

## 📊 Character Savings

| v1.2 Verbose | v2.0 Compact | Savings |
|--------------|--------------|---------|
| `[RED]text[/RED]` (16) | `[R]text` (7) | **56%** |
| `[BG:LIGHTGREEN]text[/BG]` (29) | `{LG}text` (9) | **69%** |
| Combined (38) | `[R]{LG}text` (12) | **68%** |

---

## ⚠️ Important Notes

### Only for These Tools:
- ✅ `google_sheets_create` (single sheet)
- ✅ `google_sheets_create_multiple` (multiple sheets)

### Do NOT Use In:
- ❌ `google_docs_create`
- ❌ `gmail_send_email`
- ❌ Other tools

### Enable Markdown:
```python
parse_markdown=True  # Must be set!
```

### Backward Compatible:
```python
# v1.2 still works
'[RED]Error[/RED]'

# v2.0 new syntax
'[R]Error'

# Can mix both
headers=['[RED]Old[/RED]', '[G]New']
```

---

## 🎯 Common Patterns

**Financial Reports:**
```python
'(R)[G]{LG}+16%'    # Positive change
'(R)[R]{LR}-8%'     # Negative change
'(R)$125,000'       # Right-aligned number
```

**Status Indicators:**
```python
'[G]{LG}Active'     # Success state
'[R]{LR}Blocked'    # Error state
'[B]{LB}Pending'    # Neutral state
```

**Product Lists:**
```python
'(L)[G]Premium'     # Left-aligned, green
'(L)Standard'       # Left-aligned, default
'(L)[GR]Archived'   # Left-aligned, gray
```

---

**Full Documentation:** `SHEETS_V2_IMPLEMENTATION_COMPLETE.md`  
**Test Suite:** `testing_tools/test_sheets_v2_phase1.py`  
**Status:** ✅ Production Ready (4/4 tests passing)
