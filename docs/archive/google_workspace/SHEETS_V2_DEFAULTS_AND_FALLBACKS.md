# Google Sheets Markdown v2.0 - Default Behaviors & Fallbacks

**Date:** November 2, 2025  
**Version:** v2.0 Phase 1

---

## 🎯 Summary of All Default Behaviors

When markdown codes are **not specified**, the system uses these defaults:

| Feature | Default Behavior | When Applied |
|---------|-----------------|--------------|
| **Alignment** | `LEFT` | No `(L)`, `(R)`, or `(C)` specified |
| **Text Color** | Black | No `[R]`, `[G]`, etc. specified |
| **Background Color** | White (no background) | No `{LG}`, `{LR}`, etc. specified |
| **Text Bold** | Normal weight | No `**text**` specified |
| **Text Italic** | Normal style | No `*text*` specified |
| **Font Size** | 10pt (default) | No `#` header specified |
| **Header Background** | Light gray (0.9, 0.9, 0.9) | For `#` headers ONLY |
| **Border Style** | All borders | When `auto_borders=True` (default) |
| **Header Row Bg** | Gray (0.85, 0.85, 0.85) | When `header_row_background=True` (default) |

---

## 📏 Alignment Defaults

### Default: LEFT alignment

**When no alignment code is specified:**
```python
# These are all LEFT-aligned by default
'Product Name'           # → LEFT (default)
'$125,000'              # → LEFT (default)  
'Active'                # → LEFT (default)
```

**Explicit alignment overrides default:**
```python
'(L)Product Name'       # → LEFT (explicit)
'(R)$125,000'          # → RIGHT (explicit) ✅ Better for numbers
'(C)Header'            # → CENTER (explicit) ✅ Better for headers
```

**Google Sheets Natural Behavior:**
- Text values: Default LEFT (strings, text)
- Number values: Default RIGHT (numbers, currency)
- Our markdown: **Always defaults to LEFT** unless you specify otherwise

### Special Case: Header Row

**Default header alignment:**
```python
# When header_row_background=True (default), headers are CENTER-aligned
headers = ['Product', 'Revenue', 'Status']
# Result: All headers CENTER-aligned + gray background

# Override with explicit alignment:
headers = ['(L)Product', '(R)Revenue', '(C)Status']
# Result: Left, Right, Center respectively
```

---

## 🎨 Color Defaults

### Text Color Default: Black

**When no color code is specified:**
```python
'Normal text'           # → Black (0, 0, 0)
'Product Name'          # → Black (default)
'$125,000'             # → Black (default)
```

**Explicit color overrides default:**
```python
'[G]Active'            # → Green (0.2, 0.8, 0.2)
'[R]Blocked'           # → Red (0.9, 0.2, 0.2)
'[B]Info'              # → Blue (0.2, 0.5, 0.9)
```

### Background Color Default: White (transparent)

**When no background code is specified:**
```python
'Normal cell'          # → No background (white/transparent)
'Product Name'         # → No background
'$125,000'            # → No background
```

**Explicit background overrides default:**
```python
'{LG}Approved'         # → Light green background (0.85, 0.95, 0.85)
'{LR}Alert'            # → Light red background (0.95, 0.8, 0.8)
'{LB}Note'             # → Light blue background (0.85, 0.9, 0.95)
```

### Special Case: Headers with # symbol

**Headers get auto-gray background UNLESS you specify otherwise:**
```python
# Header with auto-gray background:
'# Product Name'       # → Bold, 18pt, GRAY background (0.9, 0.9, 0.9)

# Header with custom background (explicit):
'{LB}# Product Name'   # → Bold, 18pt, LIGHT BLUE background (overrides gray)

# Header with no background (use header_row_background=False):
headers = ['# Product', '# Revenue']
parse_markdown=True,
header_row_background=False
# Result: Bold, 18pt, NO gray background
```

---

## 📝 Text Formatting Defaults

### Bold Default: Normal weight

**When no `**` is specified:**
```python
'Normal text'          # → Normal weight (not bold)
'Product Name'         # → Normal weight
```

**Explicit bold:**
```python
'**Bold text**'        # → Bold weight
'**Premium Widget**'   # → Bold
```

### Italic Default: Normal style

**When no `*` is specified:**
```python
'Normal text'          # → Normal style (not italic)
'Product Name'         # → Normal style
```

**Explicit italic:**
```python
'*Italic text*'        # → Italic style
'*Note*'               # → Italic
```

### Font Size Default: 10pt

**When no `#` header is specified:**
```python
'Normal text'          # → 10pt (Google Sheets default)
'Product Name'         # → 10pt
'$125,000'            # → 10pt
```

**Explicit font sizes with headers:**
```python
'# Large Header'       # → 18pt (level 1)
'## Medium Header'     # → 16pt (level 2)
'### Small Header'     # → 14pt (level 3)
```

---

## 🎛️ Parameter Defaults

### parse_markdown (default: False)

**When `parse_markdown=False` (default):**
```python
google_sheets_create(
    title='My Sheet',
    headers=['**Name**', '[G]Status'],
    data=[['(R)John', '{LG}Active']],
    # parse_markdown not specified → defaults to False
)
# Result: Literal text "**Name**", "[G]Status", "(R)John", "{LG}Active"
# No formatting applied!
```

**When `parse_markdown=True` (explicit):**
```python
google_sheets_create(
    title='My Sheet',
    headers=['**Name**', '[G]Status'],
    data=[['(R)John', '{LG}Active']],
    parse_markdown=True  # ✅ Must be explicit!
)
# Result: Bold "Name", Green "Status", Right-aligned "John", Light green "Active"
```

### header_row_background (default: True)

**When `header_row_background=True` (default):**
```python
google_sheets_create(
    title='My Sheet',
    headers=['Product', 'Revenue'],
    parse_markdown=True
    # header_row_background not specified → defaults to True
)
# Result: Headers with GRAY background (0.85, 0.85, 0.85) + CENTER alignment
```

**When `header_row_background=False` (explicit):**
```python
google_sheets_create(
    title='My Sheet',
    headers=['[B]Product', '{LB}Revenue'],
    parse_markdown=True,
    header_row_background=False  # ✅ Disable auto-gray
)
# Result: Blue text "Product", Light blue background "Revenue"
# NO auto-gray background, full markdown control
```

### auto_borders (default: True)

**When `auto_borders=True` (default):**
```python
google_sheets_create(
    title='My Sheet',
    headers=['Name', 'Age'],
    data=[['John', 30]],
    parse_markdown=True
    # auto_borders not specified → defaults to True
)
# Result: All cells have borders (1px solid gray)
```

**When `auto_borders=False` (explicit):**
```python
google_sheets_create(
    title='My Sheet',
    headers=['Name', 'Age'],
    data=[['John', 30]],
    parse_markdown=True,
    auto_borders=False  # ✅ Clean borderless sheet
)
# Result: No borders, clean minimalist look
```

---

## 🔗 Stacking Order & Precedence

### Parsing Order (Sequential)

When multiple markdown codes are present, they are parsed in this order:

```
1. (ALIGN)    → Alignment parsed first (must be at start)
2. [COLOR]    → Text color parsed second
3. {BG}       → Background color parsed third
4. **bold**   → Bold formatting
5. *italic*   → Italic formatting
6. # header   → Header level + font size
```

**Example:**
```python
'(R)[G]{LG}**Premium Widget**'
```

**Parsing steps:**
1. `(R)` → Remove, set alignment RIGHT
2. `[G]` → Remove, set text color GREEN
3. `{LG}` → Remove, set background LIGHT GREEN
4. `**Premium Widget**` → Remove `**`, set BOLD, text = "Premium Widget"

**Result:** Right-aligned, green text, light green background, bold "Premium Widget"

### Precedence Rules

**Explicit markdown ALWAYS overrides defaults:**
```python
# Default behavior (LEFT, black, no background):
'Product Name'

# Explicit overrides:
'(R)Product Name'      # RIGHT alignment (overrides LEFT default)
'[G]Product Name'      # Green text (overrides black default)
'{LG}Product Name'     # Light green bg (overrides white default)
```

**Explicit background overrides auto-gray for headers:**
```python
# Header with auto-gray:
'# Product'            # → Gray background (0.9, 0.9, 0.9) [default]

# Header with explicit background:
'{LB}# Product'        # → Light blue background [explicit overrides auto-gray]
```

**Parameter overrides affect all cells:**
```python
# header_row_background=False disables auto-gray for ALL headers:
headers = ['# Product', '## Category', '### Item']
header_row_background = False
# Result: All 3 headers have NO gray background (unless explicit {BG})

# auto_borders=False disables borders for ALL cells:
auto_borders = False
# Result: Entire sheet is borderless
```

---

## 📋 Quick Reference: What Happens When...

### No markdown at all:
```python
headers = ['Name', 'Age', 'City']
data = [['John', 30, 'NYC']]
parse_markdown = True
```
**Result:**
- All cells: LEFT-aligned, black text, white background, 10pt, normal weight
- Headers: CENTER-aligned, gray background (if header_row_background=True)
- Borders: All cells (if auto_borders=True)

### Only alignment:
```python
data = [['(R)$125,000', '(L)Product', '(C)Status']]
```
**Result:**
- First cell: RIGHT-aligned, black text, white bg
- Second cell: LEFT-aligned, black text, white bg
- Third cell: CENTER-aligned, black text, white bg

### Only color:
```python
data = [['[G]Active', '[R]Blocked', '[B]Info']]
```
**Result:**
- First cell: LEFT-aligned, green text, white bg
- Second cell: LEFT-aligned, red text, white bg
- Third cell: LEFT-aligned, blue text, white bg

### Only background:
```python
data = [['{LG}Approved', '{LR}Alert', '{LB}Note']]
```
**Result:**
- First cell: LEFT-aligned, black text, light green bg
- Second cell: LEFT-aligned, black text, light red bg
- Third cell: LEFT-aligned, black text, light blue bg

### Everything combined:
```python
data = [['(R)[G]{LG}**+16%**']]
```
**Result:**
- RIGHT-aligned, green text, light green bg, bold, "+" sign preserved

---

## ⚠️ Common Gotchas

### 1. Alignment must be first

**Wrong:**
```python
'[G](R)Text'           # ❌ Alignment AFTER color (won't work!)
```

**Correct:**
```python
'(R)[G]Text'           # ✅ Alignment BEFORE color
```

### 2. parse_markdown must be True

**Wrong:**
```python
data = [['(R)[G]Active']]
# parse_markdown not specified → defaults to False
# Result: Literal text "(R)[G]Active" (no formatting!)
```

**Correct:**
```python
data = [['(R)[G]Active']]
parse_markdown = True  # ✅ Explicit!
# Result: Right-aligned, green "Active"
```

### 3. Shortened codes must be valid

**Wrong:**
```python
'[RED]Text'            # ❌ Not shortened! This is v1.2 verbose syntax (needs closing [/RED])
'[GRN]Text'            # ❌ Invalid code (should be [G])
'{GREEN}Text'          # ❌ Wrong syntax (should be {LG})
```

**Correct:**
```python
'[R]Text'              # ✅ v2.0 shortened (no closing)
'[G]Text'              # ✅ Valid shortened code
'{LG}Text'             # ✅ Valid shortened background
```

### 4. Headers auto-gray unless disabled

**Surprising behavior:**
```python
headers = ['# Product', '# Revenue']
parse_markdown = True
# Expectation: Just large bold text
# Reality: Large bold text + GRAY background (auto-applied!)
```

**Fix:**
```python
headers = ['# Product', '# Revenue']
parse_markdown = True
header_row_background = False  # ✅ Disable auto-gray
# Result: Large bold text, NO gray background
```

---

## 🎓 Best Practices

### 1. Always specify alignment for numbers

**Bad (default LEFT):**
```python
data = [['$125,000', '$85,000']]  # LEFT-aligned numbers (hard to read!)
```

**Good (explicit RIGHT):**
```python
data = [['(R)$125,000', '(R)$85,000']]  # RIGHT-aligned numbers (easy to read!)
```

### 2. Use explicit alignment for headers

**Default (CENTER from header_row_background):**
```python
headers = ['Product', 'Revenue']  # CENTER-aligned (from auto-gray)
```

**Explicit (full control):**
```python
headers = ['(L)Product', '(R)Revenue']  # Left and Right (better for mixed content)
```

### 3. Disable auto-styles when using full markdown control

**Interference from defaults:**
```python
headers = ['{LB}Product', '{LG}Revenue']
header_row_background = True  # ❌ Conflicts! Gray overwrites blue/green
```

**Clean approach:**
```python
headers = ['{LB}Product', '{LG}Revenue']
header_row_background = False  # ✅ Your colors, no interference
```

---

## 📊 Default Values Summary Table

| Setting | Default Value | To Change |
|---------|--------------|-----------|
| **Cell alignment** | `LEFT` | Add `(R)` or `(C)` |
| **Header alignment** | `CENTER` | Add `(L)` or `(R)` to headers |
| **Text color** | Black (0, 0, 0) | Add `[G]`, `[R]`, etc. |
| **Background color** | White (transparent) | Add `{LG}`, `{LR}`, etc. |
| **Font weight** | Normal | Add `**text**` |
| **Font style** | Normal | Add `*text*` |
| **Font size** | 10pt | Add `#`, `##`, or `###` |
| **Header bg (# headers)** | Gray (0.9, 0.9, 0.9) | Add `{LG}` or set `header_row_background=False` |
| **Header row bg** | Gray (0.85, 0.85, 0.85) | Set `header_row_background=False` |
| **Borders** | All cells, 1px solid | Set `auto_borders=False` |
| **parse_markdown** | `False` | Set `parse_markdown=True` |

---

## 🎯 Key Takeaway

**Everything defaults to Google Sheets standard formatting UNLESS you explicitly use markdown codes:**

- **No markdown = Default appearance** (LEFT, black, white, 10pt, normal)
- **Explicit markdown = Custom appearance** (your alignment, colors, backgrounds, etc.)
- **Parameters control auto-behaviors** (header gray, borders, markdown parsing)

**Golden Rule:** If you want something different from the defaults, use the markdown codes explicitly!

---

**Document Version:** 1.0  
**Date:** November 2, 2025  
**Status:** Complete reference for v2.0 Phase 1
