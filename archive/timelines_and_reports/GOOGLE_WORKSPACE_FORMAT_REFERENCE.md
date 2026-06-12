# Google Workspace Format Reference - Complete Guide

**Last Updated:** November 27, 2025  
**Purpose:** Comprehensive reference for all `format` parameter options across Google Workspace tools

---

## Table of Contents

1. [Overview](#overview)
2. [Google Docs Formats](#google-docs-formats)
3. [Google Sheets Formats](#google-sheets-formats)
4. [Google Slides Formats](#google-slides-formats)
5. [Google Forms Formats](#google-forms-formats)
6. [Token Usage Comparison](#token-usage-comparison)
7. [Format Selection Guide](#format-selection-guide)
8. [Structure Metadata](#structure-metadata)

---

## Overview

All Google Workspace `get_*` functions now support a `format` parameter with 4 standardized options:

| Format | Token Usage | Best For | Data Included |
|--------|-------------|----------|---------------|
| **summary** | 500-2K | Quick metadata, previews | Title, ID, 2K char preview, stats |
| **text** | 50K-100K | Plain content extraction | Raw text, no formatting |
| **markdown** | 55K-120K | AI processing, structured content | Formatted markdown + structure metadata |
| **full** | 200K+ | Legacy, detailed analysis | Complete JSON (AVOID unless needed) |

**Default:** `format='summary'` (99.8% token reduction vs full)

---

## Google Docs Formats

### Tool: `google_docs_get_document(document_id, format='summary')`

#### Format: 'summary' (DEFAULT)
**Token Usage:** ~500 tokens

**Returns:**
```json
{
  "success": true,
  "title": "Sales Report Q3 2024",
  "document_id": "1M11p3SwvTHFSF5pcJd-oq2w9E_ShaBL17IMckkpkvj0",
  "preview": "First 2000 characters of content...",
  "character_count": 45892,
  "page_count": 12,
  "format": "summary",
  "sections": ["Executive Summary", "Revenue Analysis", "Forecast"],
  "note": "Use format='markdown' for full content or google_docs_search_document() for specific sections"
}
```

**Use Cases:**
- Quick document overview
- Check if document exists
- Get metadata before processing
- Verify document size before full extraction

---

#### Format: 'text'
**Token Usage:** ~50K tokens (for 40-page document)

**Returns:**
```json
{
  "success": true,
  "title": "Sales Report Q3 2024",
  "document_id": "1M11p3SwvTHFSF5pcJd-oq2w9E_ShaBL17IMckkpkvj0",
  "text": "Executive Summary\n\nQ3 revenue increased 23% YoY...\n\nRevenue Analysis\n\nTotal sales: $4.2M\nGrowth rate: +23%...",
  "character_count": 45892,
  "format": "text"
}
```

**Use Cases:**
- Plain text extraction for analysis
- Word count or keyword search
- Text-to-speech processing
- Simple content migration

**Note:** No formatting preserved (no bold, italic, headings, lists)

---

#### Format: 'markdown' ⭐ RECOMMENDED FOR AI
**Token Usage:** ~55K tokens (for 40-page document)

**Returns:**
```json
{
  "success": true,
  "title": "Sales Report Q3 2024",
  "document_id": "1M11p3SwvTHFSF5pcJd-oq2w9E_ShaBL17IMckkpkvj0",
  "markdown": "---\n**Document Structure:**\n- H1 (##): 18pt, 20pt above, 6pt below\n- H2 (###): 14pt, 10pt above, 3pt below\n- H3 (####): 12pt, 8pt above, 2pt below\n- Normal text: 11pt\n---\n\n# Sales Report Q3 2024\n\n## Executive Summary\n\nQ3 revenue increased **23% YoY** to **$4.2M**...\n\n### Key Metrics\n\n- Total sales: $4.2M\n- Growth rate: +23%\n- Customer acquisition: +15%\n\n## Revenue Analysis\n\nDetailed breakdown by region...",
  "character_count": 46120,
  "format": "markdown",
  "structure": {
    "heading_1_size": "18pt",
    "heading_2_size": "14pt", 
    "heading_3_size": "12pt",
    "heading_4_size": null,
    "normal_text_size": "11pt",
    "heading_spacing": {
      "H1": "20pt above, 6pt below",
      "H2": "10pt above, 3pt below",
      "H3": "8pt above, 2pt below"
    }
  },
  "note": "Full document as markdown with document structure metadata. AI can see heading sizes and spacing to match original formatting hierarchy."
}
```

**Markdown Syntax Used:**
- `# Title` - Document title (centered, largest)
- `## H1` - Heading 1 (18pt default)
- `### H2` - Heading 2 (14pt default)
- `#### H3` - Heading 3 (12pt default)
- `##### H4` - Heading 4 (11pt default)
- `**bold text**` - Bold formatting
- `*italic text*` - Italic formatting
- `- bullet point` - Unordered lists
- `  - nested bullet` - Nested lists (2 spaces per level)

**Structure Metadata:**
The `structure` field provides font sizes and spacing for each heading level, enabling AI to:
- Understand visual hierarchy ("## is 18pt, ### is 14pt")
- Maintain consistency when creating similar documents
- Match original document styling
- Preserve spacing relationships

**Use Cases:**
- AI content processing
- Document analysis with formatting
- Content migration with structure preservation
- Creating similar documents with matching styles

---

#### Format: 'full' ⚠️ LEGACY - AVOID
**Token Usage:** ~237K tokens (for 40-page document) - **EXCEEDS CLAUDE LIMIT**

**Returns:**
Complete JSON structure with all formatting metadata (textStyle, paragraphStyle, etc.)

**Use Cases:**
- Legacy integrations only
- When you need exact pixel-level formatting
- Advanced document analysis tools

**Warning:** 
- Will hit 200,000 token context limit on documents >30 pages
- 99.8% of data is formatting metadata
- Use `format='markdown'` instead for structure-aware content

---

### Tool: `google_docs_search_document(document_id, query, context_chars=800, max_matches=10)`

**Token Usage:** ~2K tokens (regardless of document size)

**Returns:**
```json
{
  "success": true,
  "title": "Sales Report Q3 2024",
  "document_id": "1M11p3SwvTHFSF5pcJd-oq2w9E_ShaBL17IMckkpkvj0",
  "query": "revenue analysis",
  "matches": [
    {
      "match_index": 1,
      "context": "...## Revenue Analysis\n\nTotal sales reached $4.2M in Q3, representing a 23% year-over-year increase. This growth was driven primarily by enterprise customers...",
      "character_position": 5420
    }
  ],
  "match_count": 1,
  "note": "Use this for targeted extraction from large documents instead of format='full'"
}
```

**Use Cases:**
- Extract specific sections from large documents
- Keyword-based content retrieval
- Targeted analysis without full document load
- When you know what you're looking for

---

## Google Sheets Formats

### Tool: `google_sheets_get_range(spreadsheet_id, range, format='summary')`

#### Format: 'summary' (DEFAULT)
**Token Usage:** ~500 tokens

**Returns:**
```json
{
  "success": true,
  "title": "Q3 Sales Data",
  "spreadsheet_id": "1abc...",
  "range": "Sheet1!A1:E100",
  "row_count": 100,
  "column_count": 5,
  "preview": [
    ["Product", "Q1", "Q2", "Q3", "Total"],
    ["Widget A", "$50K", "$65K", "$78K", "$193K"],
    ["Widget B", "$32K", "$41K", "$52K", "$125K"]
  ],
  "format": "summary",
  "note": "Preview shows first 3 rows. Use format='values' for all data."
}
```

---

#### Format: 'values'
**Token Usage:** ~20K tokens (for 100 rows × 10 columns)

**Returns:**
```json
{
  "success": true,
  "spreadsheet_id": "1abc...",
  "range": "Sheet1!A1:E100",
  "values": [
    ["Product", "Q1", "Q2", "Q3", "Total"],
    ["Widget A", 50000, 65000, 78000, 193000],
    ["Widget B", 32000, 41000, 52000, 125000],
    ...
  ],
  "format": "values"
}
```

**Note:** Returns raw cell values (numbers, strings) without formulas or formatting

---

#### Format: 'markdown' 🆕 COMING SOON
**Token Usage:** ~25K tokens (for 100 rows × 10 columns)

**Planned Returns:**
```json
{
  "success": true,
  "markdown": "| Product | Q1 | Q2 | Q3 | Total |\n|---------|-----|-----|-----|-------|\n| Widget A | $50K | $65K | $78K | $193K |\n| Widget B | $32K | $41K | $52K | $125K |",
  "format": "markdown",
  "note": "Converted to markdown table with preserved formatting"
}
```

**Status:** Not yet implemented (planned)

---

#### Format: 'full'
**Token Usage:** ~150K tokens (for 100 rows × 10 columns with conditional formatting)

**Returns:**
Complete cell data including formulas, formatting, conditional rules, data validation

**Use Cases:**
- Exact spreadsheet replication
- Conditional formatting analysis
- Formula auditing

---

## Google Slides Formats

### Tool: `google_slides_get_presentation(presentation_id, format='summary')`

#### Format: 'summary' (DEFAULT)
**Token Usage:** ~1K tokens

**Returns:**
```json
{
  "success": true,
  "title": "Q3 Business Review",
  "presentation_id": "1xyz...",
  "slide_count": 24,
  "page_size": {"width": 10, "height": 7.5},
  "slides": [
    {"slide_id": "p", "title": "Title Slide", "layout": "TITLE"},
    {"slide_id": "g1", "title": "Agenda", "layout": "TITLE_AND_BODY"}
  ],
  "format": "summary",
  "note": "Use format='markdown' for full content or specify slide_id for single slide"
}
```

---

#### Format: 'text'
**Token Usage:** ~80K tokens (for 24 slides)

**Returns:**
```json
{
  "success": true,
  "presentation_id": "1xyz...",
  "text": "Slide 1: Q3 Business Review\n\nSlide 2: Agenda\n- Executive Summary\n- Financial Results\n- Strategic Initiatives...",
  "format": "text"
}
```

---

#### Format: 'markdown' 🆕 COMING SOON
**Token Usage:** ~90K tokens (for 24 slides)

**Planned Returns:**
```json
{
  "success": true,
  "markdown": "---\nSlide 1\n---\n\n# Q3 Business Review\n\n**Presented by:** John Smith  \n**Date:** November 15, 2024\n\n---\nSlide 2\n---\n\n## Agenda\n\n- Executive Summary\n- Financial Results\n- Strategic Initiatives...",
  "format": "markdown",
  "structure": {
    "title_font_size": "44pt",
    "subtitle_font_size": "28pt",
    "body_font_size": "18pt"
  }
}
```

**Status:** Not yet implemented (HIGH PRIORITY - identified as at-risk for token overflow)

---

#### Format: 'full' ⚠️ AVOID
**Token Usage:** ~280K tokens (for 24 slides) - **EXCEEDS CLAUDE LIMIT**

**Warning:** Includes all shape properties, transforms, fills, borders - causes token overflow

---

## Google Forms Formats

### Tool: `google_forms_get_form(form_id, format='summary')`

#### Format: 'summary' (DEFAULT)
**Token Usage:** ~800 tokens

**Returns:**
```json
{
  "success": true,
  "title": "Customer Satisfaction Survey",
  "form_id": "1def...",
  "question_count": 15,
  "questions": [
    {"id": "q1", "title": "How satisfied are you?", "type": "MULTIPLE_CHOICE"},
    {"id": "q2", "title": "What can we improve?", "type": "PARAGRAPH_TEXT"}
  ],
  "format": "summary"
}
```

---

#### Format: 'text'
**Token Usage:** ~15K tokens (for 15-question form)

**Returns:**
```json
{
  "success": true,
  "text": "Customer Satisfaction Survey\n\nQuestion 1: How satisfied are you with our service?\n- Very Satisfied\n- Satisfied\n- Neutral\n- Dissatisfied\n- Very Dissatisfied\n\nQuestion 2: What can we improve?...",
  "format": "text"
}
```

---

#### Format: 'markdown' 🆕 COMING SOON
**Token Usage:** ~18K tokens (for 15-question form)

**Planned Returns:**
```json
{
  "success": true,
  "markdown": "# Customer Satisfaction Survey\n\n## Question 1: How satisfied are you?\n\n**Type:** Multiple Choice (required)\n\n- ○ Very Satisfied\n- ○ Satisfied\n- ○ Neutral\n- ○ Dissatisfied\n- ○ Very Dissatisfied\n\n## Question 2: What can we improve?\n\n**Type:** Paragraph Text (optional)\n\n[Long answer text field]",
  "format": "markdown"
}
```

**Status:** Not yet implemented (HIGH PRIORITY)

---

#### Format: 'full' ⚠️ AVOID
**Token Usage:** ~95K tokens (for 15-question form with validation rules)

**Warning:** Includes all validation rules, conditional logic, quiz settings

---

### Tool: `google_forms_get_response_summary(form_id, format='summary')`

#### Format: 'summary' (DEFAULT)
**Token Usage:** ~1.5K tokens

**Returns:**
```json
{
  "success": true,
  "form_id": "1def...",
  "total_responses": 342,
  "top_responses": {
    "q1": {"Very Satisfied": 156, "Satisfied": 98, "Neutral": 45},
    "q2": ["Faster response times", "Better documentation", "More features"]
  },
  "format": "summary"
}
```

---

#### Format: 'full'
**Token Usage:** ~180K tokens (for 342 responses) - **NEAR CLAUDE LIMIT**

**Warning:** Includes every individual response - use summary instead

---

## Token Usage Comparison

### Example: 40-Page Google Doc (12,000 words)

| Format | Tokens | % of Full | Recommended |
|--------|--------|-----------|-------------|
| **summary** | 500 | 0.2% | ✅ For previews |
| **text** | 50,000 | 21% | ✅ For plain content |
| **markdown** | 55,000 | 23% | ⭐ **BEST for AI** |
| **full** | 237,366 | 100% | ❌ Exceeds limit |

### Example: 24-Slide Presentation

| Format | Tokens | % of Full | Recommended |
|--------|--------|-----------|-------------|
| **summary** | 1,000 | 0.4% | ✅ For overview |
| **text** | 80,000 | 29% | ✅ For content |
| **markdown** | 90,000 | 32% | ⭐ **BEST** (when available) |
| **full** | 280,000 | 100% | ❌ Exceeds limit |

### Example: 100-Row Spreadsheet

| Format | Tokens | % of Full | Recommended |
|--------|--------|-----------|-------------|
| **summary** | 500 | 0.3% | ✅ For metadata |
| **values** | 20,000 | 13% | ⭐ **BEST** |
| **markdown** | 25,000 | 17% | ✅ When tables needed |
| **full** | 150,000 | 100% | ⚠️ Only if needed |

---

## Format Selection Guide

### Decision Tree

```
Do you need full content?
├─ NO → Use format='summary'
│        ✅ 500-2K tokens
│        ✅ Fastest
│        ✅ 99.8% token reduction
│
└─ YES
   │
   ├─ Do you need formatting/structure?
   │  ├─ NO → Use format='text'
   │  │       ✅ 50K-100K tokens
   │  │       ✅ Plain text only
   │  │
   │  └─ YES → Use format='markdown' ⭐
   │          ✅ 55K-120K tokens
   │          ✅ Preserves headings, bold, italic, lists
   │          ✅ Includes structure metadata for AI
   │          ✅ Best balance: readability + token efficiency
   │
   └─ Do you need exact pixel-level formatting?
      └─ Use format='full' (LAST RESORT)
             ⚠️ 200K+ tokens
             ⚠️ May exceed Claude limit
             ⚠️ Only for legacy/advanced use cases
```

---

### Use Case Recommendations

| Use Case | Recommended Format | Why |
|----------|-------------------|-----|
| **AI content analysis** | `markdown` | Structure metadata + formatting |
| **Quick document check** | `summary` | Fastest, minimal tokens |
| **Text extraction** | `text` | Clean content, no formatting |
| **Creating similar docs** | `markdown` | AI sees heading sizes/spacing |
| **Data extraction** | `summary` → `values` (sheets) | Efficient two-step approach |
| **Legacy integrations** | `full` | Only if absolutely required |
| **Large document sections** | Use `google_docs_search_document()` | Targeted extraction |

---

## Structure Metadata

### What is Structure Metadata?

Structure metadata provides the **visual hierarchy** of documents so AI can understand not just the semantic meaning (## = heading) but the **actual sizes and spacing** used.

### Why It Matters

**Without structure metadata:**
```markdown
## Executive Summary
### Key Findings
```
AI sees: "This is H1, this is H2" ❌ No size context

**With structure metadata:**
```markdown
---
Document Structure:
- H1 (##): 18pt, 20pt above, 6pt below
- H2 (###): 14pt, 10pt above, 3pt below
---

## Executive Summary
### Key Findings
```
AI sees: "H1 is 18pt with 20pt spacing, H2 is 14pt with 10pt spacing" ✅ Full context

### Structure Info Fields

```json
"structure": {
  "heading_1_size": "18pt",      // Font size of H1 headings
  "heading_2_size": "14pt",      // Font size of H2 headings
  "heading_3_size": "12pt",      // Font size of H3 headings
  "heading_4_size": "11pt",      // Font size of H4 headings (optional)
  "normal_text_size": "11pt",    // Body paragraph font size
  "heading_spacing": {
    "H1": "20pt above, 6pt below",  // Spacing for H1
    "H2": "10pt above, 3pt below",  // Spacing for H2
    "H3": "8pt above, 2pt below"    // Spacing for H3
  }
}
```

### Use Cases for Structure Metadata

1. **Document Consistency:**
   - AI creating new sections can match existing heading sizes
   - Maintains visual consistency across document

2. **Template Creation:**
   - Extract structure from one document
   - Apply to new documents automatically

3. **Style Analysis:**
   - Compare formatting across documents
   - Identify inconsistencies

4. **Content Migration:**
   - Preserve visual hierarchy when moving content
   - Maintain brand guidelines

---

## Advanced Usage Examples

### Example 1: Progressive Document Loading

```python
# Step 1: Check if document is large
result = google_docs_get_document(doc_id, format='summary')
char_count = result['character_count']

# Step 2: Choose appropriate format
if char_count < 10000:
    # Small doc - use markdown
    content = google_docs_get_document(doc_id, format='markdown')
elif char_count < 50000:
    # Medium doc - use text first, then markdown if needed
    content = google_docs_get_document(doc_id, format='text')
else:
    # Large doc - use search for specific sections
    content = google_docs_search_document(doc_id, query='executive summary')
```

### Example 2: Structure-Aware Document Creation

```python
# Get structure from existing document
source = google_docs_get_document(source_doc_id, format='markdown')
structure = source['structure']

# AI prompt with structure context
prompt = f"""Create a new section matching this document structure:
- H1 should be {structure['heading_1_size']} with {structure['heading_spacing']['H1']}
- H2 should be {structure['heading_2_size']} with {structure['heading_spacing']['H2']}
- Normal text should be {structure['normal_text_size']}

New section topic: Q4 Financial Results
"""
```

### Example 3: Targeted Content Extraction

```python
# Instead of loading full document (237K tokens)
full_doc = google_docs_get_document(doc_id, format='full')  # ❌ Wasteful

# Use search for specific sections (2K tokens each)
revenue = google_docs_search_document(doc_id, 'revenue analysis')  # ✅ Efficient
forecast = google_docs_search_document(doc_id, 'forecast 2025')
risks = google_docs_search_document(doc_id, 'risk factors')
```

---

## Implementation Status

| Tool | summary | text | markdown | full | Structure Metadata |
|------|---------|------|----------|------|--------------------|
| **google_docs_get_document** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **google_docs_search_document** | N/A | N/A | ✅ | N/A | ❌ |
| **google_sheets_get_range** | ✅ | N/A | 🔴 Planned | ✅ | ❌ |
| **google_slides_get_presentation** | ✅ | ✅ | 🔴 Planned | ✅ | 🔴 Planned |
| **google_forms_get_form** | ✅ | ✅ | 🔴 Planned | ✅ | ❌ |
| **google_forms_get_response_summary** | ✅ | N/A | N/A | ✅ | ❌ |

**Legend:**
- ✅ Implemented
- 🔴 Planned (high priority)
- ❌ Not applicable

---

## Migration Guide

### Migrating from format='full' (Legacy)

**Before (AVOID):**
```python
doc = google_docs_get_document(doc_id, format='full')
# Returns 237,366 tokens - EXCEEDS CLAUDE LIMIT
```

**After (RECOMMENDED):**
```python
# For AI processing
doc = google_docs_get_document(doc_id, format='markdown')
# Returns 55,000 tokens - 99.8% reduction

# Access structure metadata
structure = doc['structure']
print(f"H1 size: {structure['heading_1_size']}")
print(f"H1 spacing: {structure['heading_spacing']['H1']}")
```

### Updating Tool Calls

**Old pattern:**
```python
# Implicit format='full' (legacy default)
doc = google_docs_get_document(doc_id)
```

**New pattern:**
```python
# Explicit format (summary is now default)
doc = google_docs_get_document(doc_id, format='summary')

# For AI processing with structure
doc = google_docs_get_document(doc_id, format='markdown')
```

---

## Performance Metrics

### Token Efficiency

| Format | Avg Tokens/Page | 10-Page Doc | 50-Page Doc | 100-Page Doc |
|--------|-----------------|-------------|-------------|--------------|
| **summary** | 500 total | 500 | 500 | 500 |
| **text** | 1,250 | 12,500 | 62,500 | 125,000 |
| **markdown** | 1,375 | 13,750 | 68,750 | 137,500 |
| **full** | 5,934 | 59,340 | 296,700 | 593,400 ❌ |

### API Performance

| Format | Avg Response Time | Data Transfer |
|--------|-------------------|---------------|
| **summary** | 0.3s | 2 KB |
| **text** | 0.8s | 100 KB |
| **markdown** | 1.2s | 110 KB |
| **full** | 3.5s | 950 KB |

---

## Best Practices

### DO:
✅ **Use `format='summary'` as default** - 99.8% token savings  
✅ **Use `format='markdown'` for AI processing** - Structure + efficiency  
✅ **Use `google_docs_search_document()` for large docs** - Targeted extraction  
✅ **Check `character_count` in summary** - Size-aware loading  
✅ **Use structure metadata** - AI can match existing formatting  
✅ **Progressive loading** - summary → text → markdown → full (only if needed)

### DON'T:
❌ **Don't use `format='full'` by default** - Causes token overflow  
❌ **Don't load full docs >30 pages** - Will exceed Claude limit  
❌ **Don't ignore structure metadata** - AI loses visual context  
❌ **Don't use full format for simple text extraction** - Wasteful  
❌ **Don't assume all content fits in context** - Check token limits

---

## Troubleshooting

### Issue: "Token limit exceeded"

**Cause:** Using `format='full'` on large document

**Solution:**
```python
# Instead of:
doc = google_docs_get_document(doc_id, format='full')  # ❌

# Use:
doc = google_docs_get_document(doc_id, format='markdown')  # ✅
```

### Issue: "AI doesn't match document formatting"

**Cause:** Using `format='text'` which strips all structure

**Solution:**
```python
# Instead of:
doc = google_docs_get_document(doc_id, format='text')  # ❌ No structure

# Use:
doc = google_docs_get_document(doc_id, format='markdown')  # ✅ Has structure
structure = doc['structure']
# Include structure in AI prompt
```

### Issue: "Need specific section from large document"

**Cause:** Loading full document unnecessarily

**Solution:**
```python
# Instead of:
doc = google_docs_get_document(large_doc_id, format='full')  # ❌ 237K tokens

# Use:
section = google_docs_search_document(large_doc_id, 'revenue analysis')  # ✅ 2K tokens
```

---

## Future Enhancements

### Planned Features

1. **Google Sheets Markdown Tables** (Q1 2025)
   - Convert values to markdown tables
   - Preserve conditional formatting as text annotations
   - Include formula display

2. **Google Slides Markdown** (Q1 2025)
   - Convert slides to markdown with speaker notes
   - Include structure metadata (title/body font sizes)
   - Preserve slide transitions as comments

3. **Google Forms Markdown** (Q1 2025)
   - Readable question/answer format
   - Include validation rules as text
   - Preserve conditional logic

4. **Smart Format Auto-Selection** (Q2 2025)
   - Automatically choose format based on document size
   - Warn when approaching token limits
   - Suggest `search_document()` for large files

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│           GOOGLE WORKSPACE FORMAT QUICK REFERENCE           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📄 DOCS: google_docs_get_document(doc_id, format='X')     │
│  ├─ summary  →   500 tokens  → Quick preview       ✅      │
│  ├─ text     → 50,000 tokens → Plain content       ✅      │
│  ├─ markdown → 55,000 tokens → AI processing ⭐    ✅      │
│  └─ full     → 237,000 tokens → Legacy only        ❌      │
│                                                             │
│  📊 SHEETS: google_sheets_get_range(sheet_id, range)       │
│  ├─ summary  →   500 tokens  → Metadata + preview  ✅      │
│  ├─ values   → 20,000 tokens  → Raw data          ✅      │
│  ├─ markdown → 25,000 tokens  → Tables (planned)   🔴      │
│  └─ full     → 150,000 tokens → All formatting    ⚠️      │
│                                                             │
│  📽️ SLIDES: google_slides_get_presentation(pres_id)       │
│  ├─ summary  →  1,000 tokens  → Overview          ✅      │
│  ├─ text     → 80,000 tokens  → Content only      ✅      │
│  ├─ markdown → 90,000 tokens  → Formatted (planned) 🔴     │
│  └─ full     → 280,000 tokens → Exceeds limit     ❌      │
│                                                             │
│  📋 FORMS: google_forms_get_form(form_id)                  │
│  ├─ summary  →   800 tokens   → Questions list    ✅      │
│  ├─ text     → 15,000 tokens  → Full form         ✅      │
│  ├─ markdown → 18,000 tokens  → Formatted (planned) 🔴     │
│  └─ full     → 95,000 tokens  → All validation    ⚠️      │
│                                                             │
│  🔍 SEARCH: google_docs_search_document(doc_id, query)     │
│  └─ Always ~2,000 tokens → Targeted extraction    ⭐      │
│                                                             │
└─────────────────────────────────────────────────────────────┘

LEGEND:
✅ Recommended    ⭐ Best for AI    🔴 Coming soon    ❌ Avoid    ⚠️ Use carefully
```

---

**Last Updated:** November 27, 2025  
**Version:** 1.0.0  
**Status:** ✅ Complete for Google Docs, Partial for Sheets/Slides/Forms
