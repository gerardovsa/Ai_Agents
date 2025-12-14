# Microsoft Word Markdown Tool Enhancement Plan

**Date**: December 14, 2025  
**Status**: Proposal for Review  
**Goal**: Enhance `microsoft_word_smart_create_from_markdown` to replace `microsoft_word_smart_generate_report`

---

## 🎯 Current Issues Identified by Testing AI

### 1. ❌ **No Table of Contents**
- Tool doesn't auto-generate TOC
- Manual numbering creates no benefit

### 2. ⚠️ **Limited List Customization**
- Only standard bullets (`-`) and numbers (`1.`)
- No checkboxes or custom list symbols

### 3. ⚠️ **Horizontal Line Alignment**
- `---` creates left-aligned lines by default
- Cannot center them via markdown

### 4. ❌ **No Font/Size Control**
- Only heading levels (H1-H6) for size variation
- No line spacing control
- No font family selection

---

## ✅ What Currently Works Well

### **Text Formatting (8 types)**
- **Bold**, *italic*, ~~strikethrough~~
- `Code/monospace`, ==highlight==
- __Underline__, H~2~O (subscript), x^2^ (superscript)

### **Structure**
- 6 heading levels (H1-H6)
- Tables (any size, complexity)
- Bullet & numbered lists
- Nested lists (unlimited depth)
- Code blocks with syntax
- Blockquotes

### **Special Elements**
- Page breaks: `<<PAGE-BREAK>>`
- Horizontal lines: `---`
- Hyperlinks: `[text](url)`
- Images: `![alt](url)`

### **Alignment**
- Left (default): `<-text`
- Center: `->text<-`
- Right: `text->`

---

## 🚀 Proposed Enhancements (Priority Order)

### **Priority 1: Must Have**

#### 1. **Title Page with Metadata**
```json
{
  "include_title_page": true,
  "title_page_subtitle": "Q4 2025 Financial Analysis",
  "metadata": {
    "author": "Jane Smith, CFO",
    "company": "Acme Corporation",
    "department": "Finance",
    "date": "December 14, 2025",
    "version": "1.0 - Final",
    "reference_number": "FIN-2025-Q4-001",
    "confidentiality": "Confidential - Internal Use Only"
  }
}
```

**Impact**: Makes documents professional and enterprise-ready

---

#### 2. **Auto-Generated Table of Contents**
```json
{
  "include_toc": true,
  "toc_depth": 3,  // Include H1, H2, H3
  "toc_title": "Table of Contents"
}
```

**Impact**: Solves the #1 issue identified by testing AI

---

#### 3. **Page Numbers (Customizable)**
```json
{
  "page_numbers": {
    "enabled": true,
    "position": "bottom_center",  // or bottom_right, top_center, etc.
    "format": "page_of_total",    // Shows "Page 1 of 10"
    "start_page": 2,               // Skip title page
    "show_on_first_page": false
  }
}
```

**Impact**: Essential for professional documents

---

#### 4. **Centered Horizontal Lines (Default)**
```json
{
  "horizontal_rules": {
    "alignment": "center",      // ✅ DEFAULT behavior change
    "width_percent": 80,        // 80% of page width
    "style": "single"           // or double, thick, dashed, dotted
  }
}
```

**Impact**: Fixes issue #3 from testing AI

---

#### 5. **Document Type Styling**
```json
{
  "document_type": "report"  // or proposal, technical, legal, medical, etc.
}
```

**Types**:
- `report` - Business reports with formal styling
- `proposal` - Business proposals
- `technical` - Technical docs (code-friendly fonts)
- `legal` - Legal documents
- `medical` - Medical reports
- `letter` - Business letters
- `meeting_minutes` - Meeting minutes
- `invoice` - Invoice/billing
- `academic` - Academic papers
- `manual` - User manuals
- `creative` - Creative documents

**Impact**: Replaces the need for `microsoft_word_smart_generate_report`

---

### **Priority 2: Should Have**

#### 6. **Headers and Footers**
```json
{
  "header": {
    "enabled": true,
    "left_text": "Acme Corporation",
    "center_text": "Q4 Financial Report",
    "right_text": "December 2025",
    "show_on_first_page": false
  },
  "footer": {
    "enabled": true,
    "left_text": "Confidential",
    "center_text": "{page_number}",  // Auto page number
    "right_text": "FIN-2025-Q4"
  }
}
```

**Impact**: Professional document branding

---

#### 7. **Line Spacing Control**
```json
{
  "options": {
    "line_spacing": 1.5,  // 1.0 = single, 1.5 = 1.5x, 2.0 = double
    "paragraph_spacing": {
      "before": 0,
      "after": 8
    }
  }
}
```

**Impact**: Fixes issue #4 from testing AI

---

#### 8. **Font Control**
```json
{
  "options": {
    "font_family": "Calibri",  // or Arial, Times New Roman, etc.
    "font_size": 11            // Body text size (points)
  }
}
```

**Impact**: Fixes issue #4 from testing AI

---

#### 9. **Export to PDF**
```json
{
  "export_pdf": true
}
```

**Impact**: Matches `microsoft_word_smart_generate_report` functionality

---

### **Priority 3: Nice to Have**

#### 10. **Margin Control**
```json
{
  "options": {
    "margins": {
      "top": 1.0,
      "bottom": 1.0,
      "left": 1.25,
      "right": 1.25
    }
  }
}
```

---

#### 11. **Multiple Horizontal Rule Styles**
Already proposed in Priority 1 #4

---

## 📊 Feature Comparison

| Feature | Current Markdown Tool | Report Tool | **ENHANCED Tool** |
|---------|----------------------|-------------|-------------------|
| Markdown formatting | ✅ Full (30+ features) | ❌ None | ✅ **Full** |
| Title page | ❌ No | ✅ Yes | ✅ **Yes + Customizable** |
| Table of Contents | ❌ No | ✅ Yes | ✅ **Yes + Auto-numbered** |
| Page numbers | ❌ No | ⚠️ Maybe | ✅ **Yes + Customizable** |
| Headers/Footers | ❌ No | ❌ No | ✅ **Yes (NEW)** |
| Metadata display | ❌ No | ✅ Yes | ✅ **Yes + More fields** |
| Document types | ❌ No | ✅ 8 types | ✅ **11 types** |
| Centered HR lines | ❌ No | ❌ No | ✅ **Yes (DEFAULT)** |
| Line spacing | ❌ No | ❌ No | ✅ **Yes (NEW)** |
| Font control | ❌ No | ⚠️ Per type | ✅ **Yes (customizable)** |
| Export PDF | ❌ No | ✅ Yes | ✅ **Yes** |
| Tables | ✅ Yes | ✅ Yes | ✅ **Yes** |
| Nested lists | ✅ Yes | ✅ Yes | ✅ **Yes** |
| Code blocks | ✅ Yes | ❌ No | ✅ **Yes** |
| Subscript/Superscript | ✅ Yes | ❌ No | ✅ **Yes** |
| Images from URL | ✅ Yes | ⚠️ Limited | ✅ **Yes** |
| Alignment control | ✅ Yes | ❌ No | ✅ **Yes** |

---

## 💡 Example Usage (Enhanced Tool)

```json
{
  "title": "Q4 2025 Financial Report",
  "title_page_subtitle": "Annual Performance Analysis",
  "include_title_page": true,
  "include_toc": true,
  "toc_depth": 3,
  
  "metadata": {
    "author": "Jane Smith, CFO",
    "company": "Acme Corporation",
    "department": "Finance Department",
    "date": "December 14, 2025",
    "version": "1.0 - Final",
    "confidentiality": "Confidential"
  },
  
  "page_numbers": {
    "enabled": true,
    "position": "bottom_center",
    "format": "page_of_total",
    "start_page": 2,
    "show_on_first_page": false
  },
  
  "horizontal_rules": {
    "alignment": "center",
    "width_percent": 80
  },
  
  "document_type": "report",
  
  "options": {
    "line_spacing": 1.5,
    "font_family": "Calibri",
    "font_size": 11
  },
  
  "export_pdf": true,
  
  "markdown_content": "# Executive Summary\n\nStrong growth in Q4...\n\n---\n\n## Financial Performance\n\n| Metric | Q3 | Q4 |\n|--------|----|----|..."
}
```

**This creates**:
- ✅ Beautiful title page with all metadata
- ✅ Auto-numbered table of contents on page 2
- ✅ Page numbers starting on page 3 (after TOC)
- ✅ Centered horizontal lines at 80% width
- ✅ 1.5x line spacing throughout
- ✅ Professional report styling
- ✅ PDF export alongside .docx

---

## 🎯 Implementation Strategy

### **Phase 1: Core Enhancements** (Weeks 1-2)
1. Title page generation with metadata
2. Auto-generated TOC **with AUTOMATIC numbering** (strips any manual numbers from headings)
3. Page numbering system
4. Centered horizontal rules (default behavior)
5. Document type styling

**Outcome**: Tool can replace `microsoft_word_smart_generate_report` for 90% of use cases

---

## 🚨 **CRITICAL: TOC Auto-Numbering Specification**

### **Problem Identified (from testing)**
- Screenshot shows double numbering: `1. 1. Introduction`
- Caused by: AI adding manual numbers (`# 1. Introduction`) + TOC adding auto-numbers

### **Solution Requirements**

#### **1. Strip Manual Numbers from Headings**
When processing markdown for TOC, detect and remove:
- `# 1. Introduction` → Store as `Introduction` (H1)
- `## 2.1 Background` → Store as `Background` (H2)
- `### 3.1.1 Details` → Store as `Details` (H3)

**Regex pattern to detect**:
```python
import re

# Matches: "# 1. Title", "## 2.1 Title", "### 2.1.1 Title"
heading_pattern = r'^(#{1,6})\s+(\d+\.)+\s+(.+)$'

# Example:
text = "# 1. Introduction"
match = re.match(heading_pattern, text)
if match:
    level = len(match.group(1))  # Number of # symbols
    clean_title = match.group(3)  # "Introduction" (without numbers)
```

#### **2. Auto-Number in TOC Only**
TOC generation should:
```python
def generate_toc(headings, depth=3):
    """
    headings = [
        {'level': 1, 'title': 'Introduction'},
        {'level': 2, 'title': 'Background'},
        {'level': 2, 'title': 'Objectives'},
        {'level': 1, 'title': 'Analysis'},
    ]
    """
    counters = [0] * 6  # H1-H6 counters
    toc_lines = []
    
    for heading in headings:
        level = heading['level']
        if level > depth:
            continue
            
        # Increment current level counter
        counters[level - 1] += 1
        
        # Reset all deeper level counters
        for i in range(level, 6):
            counters[i] = 0
        
        # Build number string (e.g., "2.3.1")
        number_parts = [str(counters[i]) for i in range(level) if counters[i] > 0]
        number = '.'.join(number_parts)
        
        # Format TOC line with indentation
        indent = '   ' * (level - 1)
        toc_line = f"{indent}{number}. {heading['title']}"
        toc_lines.append(toc_line)
    
    return '\n'.join(toc_lines)
```

**Output**:
```
1. Introduction
   1.1 Background
   1.2 Objectives
2. Analysis
```

#### **3. Keep Numbers in Actual Headings (Optional)**
You have TWO options:

**Option A: Strip numbers everywhere** (Recommended)
```python
# Input markdown:
"# 1. Introduction"

# Rendered in document:
"Introduction"  # Clean, no numbers

# TOC shows:
"1. Introduction"  # Auto-numbered
```

**Option B: Keep original numbers in headings**
```python
# Input markdown:
"# 1. Introduction"

# Rendered in document:
"1. Introduction"  # Keep as-is

# TOC shows:
"1. Introduction"  # Match exactly (don't add more numbers)
```

**Recommendation**: Use **Option A** - strip all manual numbers, let TOC auto-number

#### **4. TOC Field Code (Word)**
Use Word's native TOC field for auto-updating:
```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def insert_toc(doc, depth=3):
    """Insert Word TOC field that auto-updates"""
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    
    # Begin TOC field
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'begin')
    run._element.append(fldChar)
    
    # TOC instruction
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = f'TOC \\o "1-{depth}" \\h \\z \\u'
    run._element.append(instrText)
    
    # End TOC field
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'end')
    run._element.append(fldChar)
    
    # Note: User must right-click and "Update Field" in Word to populate
    # Or use doc.fields.update_all() if using win32com
```

**TOC Instruction Explained**:
- `TOC` = Table of Contents
- `\o "1-3"` = Use heading levels 1-3
- `\h` = Hyperlink entries to headings
- `\z` = Hide page numbers in web view
- `\u` = Use outline levels instead of paragraph styles

#### **5. Alternative: Pre-Rendered TOC**
If TOC field doesn't work, generate manually:
```python
def add_manual_toc(doc, headings, depth=3):
    """Add pre-rendered TOC (not auto-updating)"""
    doc.add_heading('Table of Contents', level=1)
    
    counters = [0] * 6
    for heading in headings:
        level = heading['level']
        if level > depth:
            continue
        
        # Update counters
        counters[level - 1] += 1
        for i in range(level, 6):
            counters[i] = 0
        
        # Build number
        number = '.'.join(str(counters[i]) for i in range(level) if counters[i] > 0)
        
        # Add TOC line
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.5 * (level - 1))
        p.add_run(f"{number}. {heading['title']}")
        
        # Optional: Add page number (if available)
        # p.add_run().add_tab()
        # p.add_run(str(heading.get('page_number', '??')))
```

---

## 📋 **Updated Schema Addition**

```json
{
  "include_toc": {
    "type": "boolean",
    "description": "Auto-generate table of contents with automatic numbering",
    "default": false
  },
  "toc_options": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "TOC heading title",
        "default": "Table of Contents"
      },
      "depth": {
        "type": "integer",
        "description": "Maximum heading level to include (1-6). E.g., 3 includes H1, H2, H3",
        "default": 3,
        "minimum": 1,
        "maximum": 6
      },
      "numbering_style": {
        "type": "string",
        "description": "TOC numbering format",
        "enum": ["decimal", "roman_upper", "roman_lower", "alpha_upper", "alpha_lower"],
        "default": "decimal"
      },
      "strip_manual_numbers": {
        "type": "boolean",
        "description": "Remove manual numbering from headings (e.g., '# 1. Title' becomes '# Title'). RECOMMENDED: true to avoid double numbering",
        "default": true
      },
      "show_page_numbers": {
        "type": "boolean",
        "description": "Show page numbers in TOC",
        "default": true
      },
      "page_break_after": {
        "type": "boolean",
        "description": "Insert page break after TOC",
        "default": true
      },
      "hyperlink_entries": {
        "type": "boolean",
        "description": "Make TOC entries clickable links to sections",
        "default": true
      }
    }
  }
}
```

---

## ✅ **Example Correct Usage**

### **AI Should Generate (NO manual numbers):**
```markdown
# Introduction
Welcome to the report...

# Key Features Being Tested
We tested the following...

## Formatting Capabilities
The tool supports...

## Performance Metrics
Speed was measured...

# Test Results
Results show...

## Speed Analysis
Average speed: 2.5s

## Quality Analysis  
Output quality: 9/10

# Recommendations
We recommend...

# Conclusion
In summary...
```

### **Tool Output (Auto-numbered TOC):**
```
Table of Contents
1. Introduction..........................1
2. Key Features Being Tested.............2
   2.1 Formatting Capabilities...........3
   2.2 Performance Metrics...............4
3. Test Results..........................5
   3.1 Speed Analysis....................6
   3.2 Quality Analysis..................7
4. Recommendations.......................8
5. Conclusion............................9
```

### **If AI Makes Mistake (manual numbers):**
```markdown
# 1. Introduction
# 2. Key Features Being Tested
## 2.1 Formatting Capabilities
```

**Tool should auto-fix** (if `strip_manual_numbers: true`):
```
Detected manual numbers, removing...
# Introduction
# Key Features Being Tested
## Formatting Capabilities
```

**Then TOC shows correctly**:
```
1. Introduction
2. Key Features Being Tested
   2.1 Formatting Capabilities
```

---

### **Phase 2: Professional Features** (Weeks 3-4)
6. Headers and footers
7. Line spacing control
8. Font family/size control
9. PDF export integration

**Outcome**: Feature parity with report tool + markdown advantages

---

### **Phase 3: Advanced Options** (Week 5)
10. Margin control
11. Advanced horizontal rule styles
12. Paragraph spacing fine-tuning

**Outcome**: Professional-grade document generator

---

## ✅ Benefits of Consolidation

### **For AI**:
- ✅ One tool instead of two (simpler mental model)
- ✅ Markdown = token efficiency (73% reduction vs JSON)
- ✅ More flexible (mix structure + formatting)
- ✅ Better for code examples (markdown code blocks)

### **For Users**:
- ✅ Professional documents with less effort
- ✅ Auto-generated TOC (no manual work)
- ✅ Centered horizontal lines (visual polish)
- ✅ Customizable fonts and spacing (brand compliance)

### **For System**:
- ✅ Reduce tool count (594 → 593)
- ✅ Consolidate maintenance (one codebase vs two)
- ✅ Better test coverage (focus on one tool)

---

## ⚠️ Migration Path

### **Option 1: Keep Both Tools (Recommended Initially)**
- Enhance markdown tool with all features
- Mark report tool as "DEPRECATED - Use microsoft_word_smart_create_from_markdown"
- Monitor usage for 1 month
- Remove report tool if markdown adoption is high

### **Option 2: Immediate Replacement**
- Deploy enhanced markdown tool
- Remove report tool immediately
- Update AI instructions to use markdown tool for all documents

---

## 📋 Open Questions for Review

1. **Should we keep `microsoft_word_smart_generate_report`?**
   - Pro: Backwards compatibility, simpler for non-markdown users
   - Con: Duplicate functionality, more tools to maintain

2. **Default horizontal rule alignment?**
   - Testing AI suggests "center" as default
   - Current behavior is "left"
   - Recommendation: **Center (80% width)** as default

3. **TOC auto-numbering style?**
   - Options: 1.0, 1.1, 1.1.1 vs. I, A, 1, a
   - Recommendation: **1.0 format** (industry standard for business)

4. **Document type presets - how many?**
   - Current report tool: 8 types
   - Proposed: 11 types
   - Question: Are 11 enough or too many?

---

## 🚀 COMPLETE SCHEMA SPECIFICATION

Based on detailed analysis, here's the complete enhanced schema:

### **NEW PARAMETERS TO ADD:**

```json
{
  "title": "string (required)",
  "markdown_content": "string (required)",
  
  // ===== NEW FEATURES =====
  
  // TITLE PAGE
  "include_title_page": "boolean (default: false)",
  "title_page_options": {
    "subtitle": "string (optional)",
    "author": "string (optional)", 
    "company": "string (optional)",
    "department": "string (optional)",
    "version": "string (optional)",
    "date": "string (optional, auto if true)",
    "logo_url": "string (optional)"
  },
  
  // TABLE OF CONTENTS
  "include_toc": "boolean (default: false)",
  "toc_options": {
    "title": "string (default: 'Table of Contents')",
    "depth": "integer 1-6 (default: 3)",
    "page_break_after": "boolean (default: true)",
    "strip_manual_numbers": "boolean (default: true)"
  },
  
  // PAGE NUMBERS
  "include_page_numbers": "boolean (default: false)",
  "page_number_options": {
    "position": "string: 'footer-center', 'footer-right', 'footer-left', 'header-center', 'header-right', 'header-left' (default: 'footer-center')",
    "format": "string: 'Page X', 'Page X of Y', 'X', 'X/Y' (default: 'Page X')",
    "start_number": "integer (default: 1)",
    "exclude_title_page": "boolean (default: true)"
  },
  
  // HEADERS & FOOTERS
  "header_text": "string (optional)",
  "footer_text": "string (optional)",
  "header_alignment": "string: 'left', 'center', 'right' (default: 'left')",
  "footer_alignment": "string: 'left', 'center', 'right' (default: 'center')",
  
  // FORMATTING DEFAULTS
  "formatting_options": {
    "center_horizontal_rules": "boolean (default: true)",
    "default_font": "string: 'Arial', 'Calibri', 'Times New Roman', 'Cambria', 'Tahoma' (default: 'Calibri')",
    "body_font_size": "integer 8-24 (default: 11)",
    "line_spacing": "float 1.0-3.0 (default: 1.15)",
    "margin_inches": {
      "top": "float (default: 1.0)",
      "bottom": "float (default: 1.0)", 
      "left": "float (default: 1.0)",
      "right": "float (default: 1.0)"
    }
  },
  
  // DOCUMENT METADATA
  "metadata": {
    "author": "string (optional)",
    "subject": "string (optional)",
    "keywords": "array of strings (optional)",
    "comments": "string (optional)"
  },
  
  // EXISTING
  "folder_id": "string (optional)"
}
```

---

## 📊 FEATURE COMPARISON TABLE

| Feature | Current Markdown Tool | Proposed Enhancement | Report Tool (Broken) |
|---------|----------------------|---------------------|---------------------|
| **Markdown Support** | ✅ 30+ features | ✅ Same | ❌ No markdown |
| **Title Page** | ❌ No | ✅ **ADD** | ✅ Has |
| **Auto TOC** | ❌ No | ✅ **ADD** | ✅ Has (broken) |
| **Page Numbers** | ❌ No | ✅ **ADD** | ✅ Has |
| **Headers/Footers** | ❌ No | ✅ **ADD** | ❌ No |
| **Centered HR Lines** | ❌ No | ✅ **ADD** | ? Unknown |
| **Custom Fonts** | ❌ No | ✅ **ADD** | ? Unknown |
| **Line Spacing** | ❌ No | ✅ **ADD** | ? Unknown |
| **Document Metadata** | ❌ No | ✅ **ADD** | ✅ Has |
| **Fast & Reliable** | ✅ Yes | ✅ Yes | ❌ Errors |

---

## 📝 EXAMPLE USAGE COMPARISON

### **Simple Document (Current Style)**
```python
microsoft_word_smart_create_from_markdown(
    title="My Report",
    markdown_content="# Heading\nContent here"
)
```

### **Professional Document (Enhanced)**
```python
microsoft_word_smart_create_from_markdown(
    title="Q4 Financial Report",
    markdown_content="# Executive Summary\nOur revenue...",
    
    # Title Page
    include_title_page=True,
    title_page_options={
        "subtitle": "Annual Performance Review",
        "author": "John Smith",
        "company": "InHouse Print",
        "department": "Finance",
        "version": "1.0",
        "date": "auto"  # Uses today's date
    },
    
    # Table of Contents
    include_toc=True,
    toc_options={
        "depth": 3,  # Show H1, H2, H3 only
        "page_break_after": True,
        "strip_manual_numbers": True
    },
    
    # Page Numbers
    include_page_numbers=True,
    page_number_options={
        "position": "footer-center",
        "format": "Page X of Y",
        "exclude_title_page": True
    },
    
    # Headers & Footers
    header_text="CONFIDENTIAL - InHouse Print",
    footer_text="© 2025 InHouse Print",
    
    # Formatting
    formatting_options={
        "center_horizontal_rules": True,  # FIX YOUR ISSUE
        "default_font": "Arial",
        "body_font_size": 11,
        "line_spacing": 1.5
    },
    
    # Metadata
    metadata={
        "author": "John Smith",
        "subject": "Q4 Financial Report",
        "keywords": ["finance", "Q4", "2025"]
    }
)
```

---

## 🎨 TITLE PAGE DESIGN SPECIFICATION

```
┌─────────────────────────────────────┐
│                                     │
│                                     │
│                                     │
│         [COMPANY LOGO]              │
│                                     │
│                                     │
│      Q4 FINANCIAL REPORT            │
│   Annual Performance Review         │
│                                     │
│                                     │
│      Author: John Smith             │
│      Department: Finance            │
│      Version: 1.0                   │
│      Date: December 14, 2025        │
│                                     │
│                                     │
│      © 2025 InHouse Print           │
│                                     │
└─────────────────────────────────────┘
```

**Title Page Layout Rules:**
1. Centered alignment for all elements
2. Logo at top (if provided) - 2-3 inches from top
3. Main title - Large bold font (18-24pt)
4. Subtitle - Medium font (14-16pt), italic
5. Metadata section - Standard font (11-12pt), 6-8 lines from bottom
6. Footer text - Small font (9-10pt), bottom margin

---

## 🔧 TECHNICAL IMPLEMENTATION NOTES

### **For Centered Horizontal Rules:**
```python
# Current (left-aligned):
paragraph.add_run().add_picture(horizontal_line_image)

# Enhanced (centered):
paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
paragraph.add_run().add_picture(horizontal_line_image)
```

### **For Auto TOC:**
```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def add_toc(doc, depth=3, title="Table of Contents"):
    # Add TOC heading
    toc_heading = doc.add_paragraph(title)
    toc_heading.style = 'Heading 1'
    
    # Add TOC field
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    
    # TOC field code: TOC \o "1-3" \h \z \u
    # \o "1-3" = levels 1-3
    # \h = hyperlinks
    # \z = hide page numbers in web layout
    # \u = use outline levels
    
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'begin')
    run._r.append(fldChar)
    
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = f'TOC \\o "1-{depth}" \\h \\z \\u'
    run._r.append(instrText)
    
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar)
    
    # Add page break after TOC
    doc.add_page_break()
```

### **For Page Numbers:**
```python
def add_page_numbers(section, position='footer-center', format_str='Page X'):
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    
    footer = section.footer
    paragraph = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    
    # Set alignment based on position
    if 'center' in position:
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    elif 'right' in position:
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
    else:
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
    
    # Add "Page " text
    run = paragraph.add_run(format_str.replace('X', ''))
    
    # Add PAGE field for current page number
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'begin')
    run._r.append(fldChar)
    
    instrText = OxmlElement('w:instrText')
    instrText.text = 'PAGE'
    run._r.append(instrText)
    
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar)
    
    # Add " of Y" if needed
    if 'Y' in format_str:
        run = paragraph.add_run(' of ')
        
        fldChar = OxmlElement('w:fldChar')
        fldChar.set(qn('w:fldCharType'), 'begin')
        run._r.append(fldChar)
        
        instrText = OxmlElement('w:instrText')
        instrText.text = 'NUMPAGES'
        run._r.append(instrText)
        
        fldChar = OxmlElement('w:fldChar')
        fldChar.set(qn('w:fldCharType'), 'end')
        run._r.append(fldChar)
```

### **For Title Page:**
```python
def create_title_page(doc, options):
    from datetime import datetime
    
    # Add centered paragraphs with spacing
    if options.get('logo_url'):
        logo_para = doc.add_paragraph()
        logo_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        run = logo_para.add_run()
        run.add_picture(options['logo_url'], width=Inches(2.5))
        logo_para.paragraph_format.space_before = Pt(72)  # 1 inch
    
    # Main title
    title_para = doc.add_paragraph(options.get('title', ''))
    title_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    title_para.runs[0].font.size = Pt(24)
    title_para.runs[0].font.bold = True
    title_para.paragraph_format.space_before = Pt(144)  # 2 inches
    
    # Subtitle
    if options.get('subtitle'):
        subtitle_para = doc.add_paragraph(options['subtitle'])
        subtitle_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        subtitle_para.runs[0].font.size = Pt(16)
        subtitle_para.runs[0].font.italic = True
        subtitle_para.paragraph_format.space_before = Pt(12)
    
    # Metadata section
    metadata_start = Pt(360)  # 5 inches from top
    
    for key in ['author', 'company', 'department', 'version']:
        if options.get(key):
            para = doc.add_paragraph(f"{key.title()}: {options[key]}")
            para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            para.runs[0].font.size = Pt(12)
    
    # Date
    if options.get('date'):
        date_str = datetime.now().strftime('%B %d, %Y') if options['date'] == 'auto' else options['date']
        date_para = doc.add_paragraph(f"Date: {date_str}")
        date_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        date_para.runs[0].font.size = Pt(12)
    
    # Page break after title page
    doc.add_page_break()
```

---

## 📋 WHAT TO TAKE FROM REPORT TOOL

### **Features to Migrate:**
1. ✅ **Title page generation** - Professional look
2. ✅ **Auto TOC with numbering** - Navigation
3. ✅ **Page numbers** - Essential for printing
4. ✅ **Document metadata** - File properties
5. ✅ **Structured sections** - Clean hierarchy

### **Features to Keep from Markdown Tool:**
1. ✅ **30+ markdown features** - Flexibility
2. ✅ **Fast performance** - Reliability
3. ✅ **Simple syntax** - Easy to use
4. ✅ **Tables, lists, code blocks** - Rich content

### **Features to Fix:**
1. ✅ **Center horizontal rules** - Default centered
2. ✅ **Add TOC support** - Auto-generated
3. ✅ **Add title page** - Optional but professional
4. ✅ **Add page numbers** - With customization
5. ✅ **Add headers/footers** - Consistent branding

---

## 🎯 Recommendation

**IMPLEMENT Priority 1 features FIRST** (1-5):
1. Title page with metadata
2. Auto-generated TOC
3. Page numbers
4. Centered horizontal rules (default)
5. Document type styling

This solves ALL issues identified by testing AI and enables tool consolidation.

**Implementation Timeline:**
- **Phase 1** (2-3 weeks): Priority 1 features (title page, TOC, page numbers, centered HR, metadata)
- **Phase 2** (1-2 weeks): Priority 2 features (headers/footers, line spacing, margins)
- **Phase 3** (1 week): Priority 3 features (font control, TOC depth, logo support) + testing

**Total Estimated Effort:** 4-6 weeks for complete implementation

**Next Steps**:
1. ✅ Create test document showing enhanced output
2. ✅ Research python-docx TOC/page number implementation
3. ✅ Draft implementation pseudocode
4. ✅ Create before/after comparison document
5. Review this proposal and approve Priority 1 features
6. Create implementation tickets
7. Begin development

---

**Question for Decision**: Should we proceed with Phase 1 implementation?
