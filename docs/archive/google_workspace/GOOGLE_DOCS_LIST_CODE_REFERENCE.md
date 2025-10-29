# 🎯 Google Docs List Formatting - Code Reference

**Date:** October 27, 2025  
**File:** `google_workspace/google_docs.py`  
**Feature:** Bulleted, Numbered, and Nested List Handling

---

## 📋 Overview

The Google Docs smart tool handles three types of lists:
1. **Bulleted Lists** (`- item` or `* item`)
2. **Numbered Lists** (`1. item`, `2. item`, etc.)
3. **Nested/Tiered Lists** (using 2 spaces per nesting level)

---

## 🔹 Bulleted Lists Code

### **Detection Pattern**

```python
# Regex pattern to detect bullet items with optional indentation
bullet_match = re.match(r'^(\s*)[-*]\s+(.+)$', line)
```

**Pattern Breakdown:**
- `^(\s*)` - Capture leading whitespace (for nesting level)
- `[-*]` - Match either `-` or `*` as bullet marker
- `\s+` - Match one or more spaces after bullet
- `(.+)$` - Capture the actual list item text

### **Nesting Level Calculation**

```python
indent = len(bullet_check.group(1))  # Count leading spaces
nesting_level = indent // 2           # 2 spaces = 1 nesting level
```

**Examples:**
- `- Item` → 0 spaces → level 0
- `  - Item` → 2 spaces → level 1
- `    - Item` → 4 spaces → level 2

### **Collection Phase**

```python
# Collect all consecutive bullet items
bullet_items = []
nesting_levels = []
bullet_formatting = []

while i < len(lines):
    bullet_check = re.match(r'^(\s*)[-*]\s+(.+)$', lines[i])
    if bullet_check:
        indent = len(bullet_check.group(1))
        nesting_level = indent // 2
        raw_text = bullet_check.group(2)
        
        # Extract inline formatting (bold, italic, etc.)
        clean_text, formatting_ops = _extract_inline_formatting(raw_text)
        
        bullet_items.append(clean_text + '\n')
        nesting_levels.append(nesting_level)
        bullet_formatting.append(formatting_ops)
        i += 1
    else:
        break  # Stop when non-bullet line encountered
```

### **Insertion Phase**

```python
# Insert all bullet text first
bullet_start = current_index
for item in bullet_items:
    requests.append({
        'insertText': {
            'text': item,
            'location': {'index': current_index}
        }
    })
    current_index += len(item)
```

### **Formatting Phase**

```python
# Apply bullet formatting with nesting
for idx, (item, level, fmt_ops) in enumerate(zip(bullet_items, nesting_levels, bullet_formatting)):
    item_start = bullet_start + sum(len(bullet_items[j]) for j in range(idx))
    item_end = item_start + len(item)
    
    # 1. Create bullet point
    requests.append({
        'createParagraphBullets': {
            'range': {
                'startIndex': item_start,
                'endIndex': item_end
            },
            'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
        }
    })
    
    # 2. Apply nesting indentation (if nested)
    if level > 0:
        requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': item_start,
                    'endIndex': item_end
                },
                'paragraphStyle': {
                    'indentStart': {'magnitude': 36 * level, 'unit': 'PT'},
                    'indentFirstLine': {'magnitude': 18 * level, 'unit': 'PT'}
                },
                'fields': 'indentStart,indentFirstLine'
            }
        })
    
    # 3. Apply inline formatting (bold, italic, etc.)
    for fmt in fmt_ops:
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': item_start + fmt['start'],
                    'endIndex': item_start + fmt['end']
                },
                'textStyle': fmt['style'],
                'fields': fmt['fields']
            }
        })
```

### **Bullet Preset**

```python
'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
```

**Rendering:**
- Level 0: ● (filled disc)
- Level 1: ○ (circle)
- Level 2: ■ (square)

---

## 🔢 Numbered Lists Code

### **Detection Pattern**

```python
# Regex pattern to detect numbered items with optional indentation
numbered_match = re.match(r'^(\s*)\d+\.\s+(.+)$', line)
```

**Pattern Breakdown:**
- `^(\s*)` - Capture leading whitespace
- `\d+` - Match one or more digits
- `\.` - Match literal period
- `\s+` - Match spaces after period
- `(.+)$` - Capture item text

### **Nesting Level Calculation**

```python
indent = len(numbered_check.group(1))  # Count leading spaces
nesting_level = indent // 2             # 2 spaces = 1 nesting level
```

**Examples:**
- `1. Item` → 0 spaces → level 0
- `  1. Item` → 2 spaces → level 1
- `    1. Item` → 4 spaces → level 2

### **Numbered Preset (⭐ IMPROVED - STANDARD FORMAT)**

```python
'bulletPreset': 'NUMBERED_DECIMAL_ALPHA_ROMAN_NESTED'
```

**Rendering (Standard Lowercase Format):**
- Level 0: 1, 2, 3... (arabic numerals)
- Level 1: a, b, c... (lowercase letters) ← STANDARD
- Level 2: i, ii, iii... (lowercase roman numerals) ← STANDARD
- Level 3: iv, v, vi... (continued roman numerals)

**This is the most widely used format in:**
- ✅ Academic papers
- ✅ Business reports
- ✅ Legal documents
- ✅ Professional proposals

**Old Format (❌ Deprecated):**
```python
'bulletPreset': 'NUMBERED_DECIMAL_NESTED'  # Was: 1, 1.1, 1.1.1
'bulletPreset': 'NUMBERED_UPPERALPHA_ROMAN_NESTED'  # Was: 1, A, i (uppercase)
```

### **Formatting Phase (⭐ IMPROVED)**

```python
# Apply numbered formatting with conventional nesting (1, A, i)
for idx, (item, level, fmt_ops) in enumerate(zip(numbered_items, nesting_levels, numbered_formatting)):
    item_start = numbered_start + sum(len(numbered_items[j]) for j in range(idx))
    item_end = item_start + len(item)
    
    # 1. Create numbered list with CONVENTIONAL format
    requests.append({
        'createParagraphBullets': {
            'range': {
                'startIndex': item_start,
                'endIndex': item_end
            },
                            'bulletPreset': 'NUMBERED_DECIMAL_ALPHA_ROMAN_NESTED'  # 1, a, i format (standard lowercase)
                        }
                    })
                    
                    # 2. Apply CONSISTENT indentation matching bullet lists
                    # Same 36 PT per level with hanging indent
                    base_indent = 36 * (level + 1)  # Start at 36 PT for level 0
                    hanging_offset = 18  # Number hangs 18 PT left of content    requests.append({
        'updateParagraphStyle': {
            'range': {
                'startIndex': item_start,
                'endIndex': item_end
            },
            'paragraphStyle': {
                'indentStart': {'magnitude': base_indent, 'unit': 'PT'},
                'indentFirstLine': {'magnitude': base_indent - hanging_offset, 'unit': 'PT'}
            },
            'fields': 'indentStart,indentFirstLine'
        }
    })
    
    # 3. Apply inline formatting
    for fmt in fmt_ops:
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': item_start + fmt['start'],
                    'endIndex': item_start + fmt['end']
                },
                'textStyle': fmt['style'],
                'fields': fmt['fields']
            }
        })
```

---

## 🎯 Key Differences: Bullets vs Numbered (⭐ UPDATED)

| Feature | Bulleted Lists | Numbered Lists |
|---------|---------------|----------------|
| **Preset** | `BULLET_DISC_CIRCLE_SQUARE` | `NUMBERED_DECIMAL_ALPHA_ROMAN_NESTED` ✅ |
| **Level 0 Indent** | 36 PT ✅ | 36 PT ✅ |
| **Level 1 Indent** | 72 PT | 72 PT |
| **Indent Formula** | `36 * (level + 1)` ✅ | `36 * (level + 1)` ✅ |
| **First Line Indent** | `base - 18` ✅ | `base - 18` ✅ |
| **Hanging Offset** | 18 PT ✅ | 18 PT ✅ |
| **Visual (L0, L1, L2)** | ●, ○, ■ | 1, a, i ✅ |

**⭐ Major Changes:**
- ✅ **Both use same indentation formula** (was different before)
- ✅ **Both use hanging indent** for multi-line alignment
- ✅ **Standard lowercase numbering** (1, a, i) - most widely used format
- ✅ **No special cases** - all levels treated consistently

---

## 📐 Indentation Mathematics (⭐ UPDATED)

### **Unified Formula (Same for Bullets AND Numbers)**

```python
# BOTH bullet lists AND numbered lists use this formula now:
base_indent = 36 * (level + 1)  # PT (points)
hanging_offset = 18             # PT

indentStart = base_indent                    # Where content starts
indentFirstLine = base_indent - hanging_offset  # Where bullet/number appears
```

### **Visual Example**

```
Level 0 Bullets:
  ●   Item with text           (indentStart: 36 PT, firstLine: 18 PT)
      that continues here       Multi-line aligned ✅

Level 1 Bullets:
    ○   Nested item            (indentStart: 72 PT, firstLine: 54 PT)
        continues aligned       Multi-line aligned ✅

Level 2 Bullets:
      ■   Deep nested          (indentStart: 108 PT, firstLine: 90 PT)
          stays aligned         Multi-line aligned ✅

Level 0 Numbered:
  1.  Item with text           (indentStart: 36 PT, firstLine: 18 PT)
      that continues here       Multi-line aligned ✅

Level 1 Numbered:
    a.  Nested item            (indentStart: 72 PT, firstLine: 54 PT)
        continues aligned       Multi-line aligned ✅

Level 2 Numbered:
      i.   Deep nested         (indentStart: 108 PT, firstLine: 90 PT)
           stays aligned        Multi-line aligned ✅
```

### **Hanging Indent Visualization**

```
Position Ruler (PT):
0     18    36    54    72    90
|     |     |     |     |     |

Level 0:
|     ●     |Content starts here and wraps
|     |     |to align perfectly with start

Level 1:
|     |     ○     |Content at 72 PT wraps
|     |     |     |to this same position

Level 2:
|     |     |     ■     |Content at 108 PT
|     |     |     |     |aligns here too
```

---

## 🔧 Inline Formatting Support

Both list types support inline formatting within list items:

```python
# Extract inline formatting helper function
clean_text, formatting_ops = _extract_inline_formatting(raw_text)
```

**Supported Inline Formats:**
- `**bold text**` → Bold
- `*italic text*` → Italic
- `~~strikethrough~~` → Strikethrough
- `==highlighted==` → Yellow highlight
- `` `code` `` → Monospace font
- `[link text](url)` → Hyperlink

### **Application**

```python
# Apply inline formatting to each list item
for fmt in fmt_ops:
    requests.append({
        'updateTextStyle': {
            'range': {
                'startIndex': item_start + fmt['start'],
                'endIndex': item_start + fmt['end']
            },
            'textStyle': fmt['style'],
            'fields': fmt['fields']
        }
    })
```

---

## 📊 Complete Example

### **Markdown Input**

```markdown
Here are the main points:

- **Bold point** at level 0
  - *Italic subpoint* at level 1
    - Regular text at level 2

And numbered steps:

1. First step with ==highlighting==
   1. Sub-step A with `code`
   2. Sub-step B
2. Second step
```

### **Processing Flow**

1. **Detection:** Regex matches list items
2. **Collection:** Group consecutive items, calculate nesting levels
3. **Insertion:** Insert all text at once
4. **Bullet/Number Application:** Apply list formatting with preset
5. **Indentation:** Apply nesting-based indentation
6. **Inline Formatting:** Apply bold, italic, etc. to text ranges

### **API Requests Generated**

```python
# For "- **Bold point** at level 0"
[
    {'insertText': {'text': 'Bold point\n', 'location': {'index': 100}}},
    {'createParagraphBullets': {'range': {'startIndex': 100, 'endIndex': 111}, 'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'}},
    {'updateTextStyle': {'range': {'startIndex': 100, 'endIndex': 110}, 'textStyle': {'bold': True}, 'fields': 'bold'}}
]

# For "  - *Italic subpoint* at level 1"
[
    {'insertText': {'text': 'Italic subpoint\n', 'location': {'index': 111}}},
    {'createParagraphBullets': {'range': {'startIndex': 111, 'endIndex': 127}, 'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'}},
    {'updateParagraphStyle': {'range': {'startIndex': 111, 'endIndex': 127}, 'paragraphStyle': {'indentStart': {'magnitude': 36, 'unit': 'PT'}, 'indentFirstLine': {'magnitude': 18, 'unit': 'PT'}}, 'fields': 'indentStart,indentFirstLine'}},
    {'updateTextStyle': {'range': {'startIndex': 111, 'endIndex': 126}, 'textStyle': {'italic': True}, 'fields': 'italic'}}
]
```

---

## 🎯 Key Design Principles

### **1. Batch Processing**
- Collect ALL list items before inserting ANY
- Calculate ALL indices upfront
- Execute ALL operations in single `batchUpdate`

### **2. Mathematical Precision**
```python
# Calculate exact position of each item
item_start = numbered_start + sum(len(numbered_items[j]) for j in range(idx))
item_end = item_start + len(item)
```

### **3. Three-Phase Approach**
1. **Insert** text
2. **Apply** list formatting
3. **Style** with inline formatting

### **4. Consistent Spacing**
- 36 PT per nesting level for body indent
- 18 PT per nesting level for first line indent
- Numbered lists offset by +1 level for visual alignment

---

## 🧪 Testing Examples

### **Simple Bullet List**

```markdown
- Item 1
- Item 2
- Item 3
```

**Output:** 3 bullet points at level 0

### **Nested Bullet List**

```markdown
- Level 0
  - Level 1
    - Level 2
      - Level 3
```

**Output:** 4 items with increasing indentation

### **Mixed Formatting**

```markdown
- **Bold** and *italic* and ==highlighted==
  - With `code` in nested item
    - [Link to Google](https://google.com)
```

**Output:** All inline formatting preserved across nesting levels

### **Numbered with Nesting**

```markdown
1. First
   1. Sub A
   2. Sub B
2. Second
```

**Output:** 
- 1, 2 (level 0)
- a, b (level 1)

---

## 💡 Common Patterns

### **Converting Flat List to Nested**

```python
# User provides:
"- A\n- B\n- C"

# To create nesting, add 2 spaces per level:
"- A\n  - B\n    - C"
```

### **Inline Formatting Extraction**

```python
raw_text = "This is **bold** and *italic*"
clean_text, formatting_ops = _extract_inline_formatting(raw_text)

# clean_text = "This is bold and italic"
# formatting_ops = [
#     {'start': 8, 'end': 12, 'style': {'bold': True}, 'fields': 'bold'},
#     {'start': 17, 'end': 23, 'style': {'italic': True}, 'fields': 'italic'}
# ]
```

---

**File Location:** `google_workspace/google_docs.py` (lines 1109-1273)  
**Related Functions:** `_extract_inline_formatting()`, `google_docs_create_from_markdown()`, `google_docs_smart_update()`
