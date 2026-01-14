# Microsoft Word Tools - Quick Start Guide

**Updated:** November 4, 2025 (After "File is not a zip file" fix)  
**Status:** ✅ All tools working correctly

---

## Quick Example: Complete Word Document

```python
from tools.registry_v3 import RegistryV3

registry = RegistryV3()

# 1. Create document with initial content
doc = registry.execute_tool(
    tool_name='microsoft_word_create_document',
    name='Veterinary_Financial_Report_Q3_2025',
    content='Executive Summary\n\nThis report covers Q3 2025 financial performance.',
    _user_id=1,
    _injected_credentials=True
)

doc_id = doc['document_id']
print(f"📄 Document created: {doc['web_url']}")

# 2. Add heading
registry.execute_tool(
    tool_name='microsoft_word_insert_heading',
    document_id=doc_id,
    text='Financial Performance Analysis',
    level=1,
    _user_id=1,
    _injected_credentials=True
)

# 3. Add content paragraphs
registry.execute_tool(
    tool_name='microsoft_word_append_text',
    document_id=doc_id,
    text='Q3 2025 showed strong revenue growth of 23% year-over-year.',
    paragraph=True,
    _user_id=1,
    _injected_credentials=True
)

# 4. Add financial table
registry.execute_tool(
    tool_name='microsoft_word_insert_table',
    document_id=doc_id,
    rows=4,
    columns=3,
    data=[
        ['Metric', 'Q2 2025', 'Q3 2025'],
        ['Revenue', '$145,000', '$168,000'],
        ['Expenses', '$98,000', '$105,000'],
        ['Net Profit', '$47,000', '$63,000']
    ],
    _user_id=1,
    _injected_credentials=True
)

print("✅ Document completed successfully!")
```

---

## Available Word Tools

### Document Management (4 tools)

| Tool | Purpose | Example |
|------|---------|---------|
| `microsoft_word_create_document` | Create new document | `name='Report', content='Text'` |
| `microsoft_word_get_document` | Get document metadata | `document_id='abc123'` |
| `microsoft_word_list_documents` | List all documents | `limit=10` |
| `microsoft_word_delete_document` | Delete document | `document_id='abc123'` |

### Content Operations (4 tools)

| Tool | Purpose | Example |
|------|---------|---------|
| `microsoft_word_append_text` | Add text to end | `text='Content', paragraph=True` |
| `microsoft_word_get_content` | Read document text | `document_id='abc123'` |
| `microsoft_word_search_text` | Find text in document | `search_term='revenue'` |
| `microsoft_word_replace_text` | Find and replace | `find='old', replace='new'` |

### Formatting & Styles (8 tools)

| Tool | Purpose | Example |
|------|---------|---------|
| `microsoft_word_insert_heading` | Add heading | `text='Title', level=1` |
| `microsoft_word_insert_table` | Add table | `rows=3, columns=3, data=[...]` |
| `microsoft_word_insert_image` | Add image | `image_url='https://...', width=5` |
| `microsoft_word_format_text` | Apply formatting | `format_type='bold'` |
| `microsoft_word_apply_style` | Apply style | `style_name='Heading 1'` |
| `microsoft_word_insert_page_break` | Add page break | `document_id='abc123'` |
| `microsoft_word_set_margins` | Set page margins | `top=1, bottom=1, left=1, right=1` |
| `microsoft_word_set_page_size` | Set page size | `width=8.5, height=11` |

### Comments & Collaboration (3 tools)

| Tool | Purpose | Example |
|------|---------|---------|
| `microsoft_word_add_comment` | Add comment | `text='Review this', location='para1'` |
| `microsoft_word_list_comments` | Get all comments | `document_id='abc123'` |
| `microsoft_word_resolve_comment` | Resolve comment | `comment_id='xyz789'` |

### Advanced Features (13 tools)

| Tool | Purpose | Example |
|------|---------|---------|
| `microsoft_word_smart_generate_report` | Auto-generate formatted report | `title='Report', sections=[...]` |
| `microsoft_word_export_pdf` | Convert to PDF | `document_id='abc123'` |
| `microsoft_word_use_template` | Create from template | `template_id='tmpl123'` |
| `microsoft_word_insert_toc` | Add table of contents | `document_id='abc123'` |
| And 9 more... | | |

---

## Common Patterns

### Pattern 1: Financial Report

```python
# Create document
doc = create_document(name='Financial_Report', content='')

# Add title
insert_heading(doc_id, 'Q3 2025 Financial Report', level=1)

# Add executive summary
append_text(doc_id, 'Executive Summary\n\nRevenue increased 23%...')

# Add financial table
insert_table(doc_id, rows=5, columns=4, data=financial_data)

# Add analysis section
insert_heading(doc_id, 'Detailed Analysis', level=2)
append_text(doc_id, 'Revenue growth was driven by...')
```

### Pattern 2: Meeting Minutes

```python
# Create with template
doc = create_document(name='Meeting_Minutes_2025_11_04')

# Add meeting info
insert_heading(doc_id, 'Meeting: Budget Review', level=1)
append_text(doc_id, 'Date: November 4, 2025\nAttendees: John, Sarah, Mike')

# Add agenda table
insert_table(doc_id, rows=4, columns=2, data=[
    ['Topic', 'Owner'],
    ['Budget Review', 'John'],
    ['Q4 Planning', 'Sarah'],
    ['Action Items', 'Mike']
])

# Add notes
insert_heading(doc_id, 'Discussion Notes', level=2)
append_text(doc_id, 'Budget approved with minor adjustments...')
```

### Pattern 3: Veterinary Report

```python
# Create patient report
doc = create_document(name='Patient_Report_Fluffy')

# Add patient info
insert_heading(doc_id, 'Patient: Fluffy (ID: 12345)', level=1)
append_text(doc_id, 'Owner: John Smith\nBreed: Golden Retriever\nAge: 5 years')

# Add examination table
insert_table(doc_id, rows=4, columns=2, data=[
    ['Parameter', 'Value'],
    ['Weight', '65 lbs'],
    ['Temperature', '101.5°F'],
    ['Heart Rate', '90 bpm']
])

# Add diagnosis
insert_heading(doc_id, 'Diagnosis', level=2)
append_text(doc_id, 'Mild arthritis in left hind leg...')

# Add treatment plan
insert_heading(doc_id, 'Treatment Plan', level=2)
append_text(doc_id, '1. Pain medication (5mg daily)\n2. Physical therapy\n3. Follow-up in 2 weeks')
```

---

## Important Notes

### ✅ Documents Are Immediately Editable

After the "File is not a zip file" fix, documents can be edited right after creation:

```python
# Create document
doc = create_document(name='Test')

# Edit immediately (NO DELAY NEEDED!)
insert_heading(doc['document_id'], 'Title')  # ✅ Works!
append_text(doc['document_id'], 'Content')   # ✅ Works!
insert_table(doc['document_id'], 3, 3, data) # ✅ Works!
```

### 📝 Initial Content Recommended

Always provide initial content when creating documents:

```python
# GOOD - Creates valid DOCX with content
create_document(name='Report', content='Initial text here')

# ALSO GOOD - Creates valid empty DOCX
create_document(name='Report', content='')

# BOTH WORK NOW - Thanks to the fix!
```

### 🔒 Authentication Required

All Word tools require Microsoft OAuth:

```python
# User must sign in first
# Visit: http://localhost:5001/api/auth/microsoft/login

# Then use with user_id
execute_tool(
    tool_name='microsoft_word_create_document',
    name='Report',
    _user_id=1,  # ← Required
    _injected_credentials=True  # ← Required
)
```

### 📊 Table Data Format

Tables expect a 2D array:

```python
data = [
    ['Header 1', 'Header 2', 'Header 3'],  # Row 1
    ['Cell 1', 'Cell 2', 'Cell 3'],        # Row 2
    ['Cell 4', 'Cell 5', 'Cell 6']         # Row 3
]

insert_table(doc_id, rows=3, columns=3, data=data)
```

### 🎨 Formatting Options

Text formatting options:

```python
# Bold
format_text(doc_id, text='Important', format_type='bold')

# Italic
format_text(doc_id, text='Emphasis', format_type='italic')

# Underline
format_text(doc_id, text='Highlighted', format_type='underline')

# Color (requires hex code)
format_text(doc_id, text='Red text', color='#FF0000')
```

---

## Troubleshooting

### Issue: "User does not have Microsoft OAuth credentials"

**Solution:**
```
1. Visit: http://localhost:5001/api/auth/microsoft/login
2. Sign in with Microsoft account
3. Grant permissions
4. Try tool again
```

### Issue: Document not found

**Solution:**
```python
# List all documents to find the right one
docs = list_documents(limit=50, _user_id=1)
for doc in docs['documents']:
    print(f"{doc['name']}: {doc['document_id']}")
```

### Issue: Table data doesn't fit

**Solution:**
```python
# Make sure rows and columns match data
data = [
    ['A', 'B'],  # 2 columns
    ['C', 'D']   # 2 columns
]

# rows=2, columns=2 (matches data shape)
insert_table(doc_id, rows=2, columns=2, data=data)
```

---

## Best Practices

### 1. Use Descriptive Names
```python
# GOOD
create_document(name='Veterinary_Financial_Report_Q3_2025')

# BAD
create_document(name='doc1')
```

### 2. Structure Content with Headings
```python
insert_heading(doc_id, 'Chapter 1: Introduction', level=1)
insert_heading(doc_id, 'Section 1.1: Background', level=2)
insert_heading(doc_id, 'Subsection 1.1.1: History', level=3)
```

### 3. Use Tables for Structured Data
```python
# Better than plain text
insert_table(doc_id, data=[[...]])

# Instead of
append_text(doc_id, 'Name: John\nAge: 30\nCity: NYC')
```

### 4. Add Comments for Collaboration
```python
add_comment(doc_id, 
    text='Please review this section', 
    location='paragraph_5'
)
```

---

## Complete Example: Professional Report

See `test_word_fix.py` for a complete working example that creates a professional veterinary financial report with:
- Heading
- Executive summary
- Financial table
- Analysis section
- Formatted text

---

**For More Information:**
- Full documentation: `WORD_FILE_ZIP_ERROR_FIX.md`
- Tool schemas: `tools/schemas/microsoft_word_tools.json`
- Implementation: `tools/implementations/microsoft_word_tools.py`
- Tests: `test_word_docx_creation.py`

---

**Version:** 1.0.0  
**Last Updated:** November 4, 2025  
**Status:** ✅ Production Ready
