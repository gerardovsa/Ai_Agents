# Markdown Tools Quick Start Guide

**Ready to use immediately after Flask restart!**

---

## 🚀 Quick Examples

### Example 1: Financial Report with Bookmarks

```python
markdown = '''
# Q4 2024 Financial Report

<<BOOKMARK:executive_summary>>
## Executive Summary
Revenue grew 40% year-over-year to reach $6.2M in Q4 2024.

<<BOOKMARK:key_metrics>>
## Key Financial Metrics

| Metric | Q3 2024 | Q4 2024 | Change |
|--------|---------|---------|--------|
| Revenue | **$4.5M** | **$6.2M** | *+38%* |
| Customers | 1,200 | 1,720 | +43% |
| ARPU | $3,750 | $3,605 | -4% |

### Revenue Breakdown
- **Premium Tier**: $3.8M (61% of total)
- **Standard Tier**: $1.9M (31%)
- **Basic Tier**: $0.5M (8%)

<<BOOKMARK:risk_assessment>>
## Risk Assessment
*Customer concentration risk identified in top 3 accounts...*
'''

# Create with Smart Update Method
result = google_docs_smart_create_from_markdown(
    title='Q4 2024 Financial Report',
    markdown_content=markdown,
    _user_id=12,
    _injected_credentials=True
)

# Or with DOCX V2 Method (faster)
result = google_docs_smart_create_from_markdown_v2(
    title='Q4 2024 Financial Report V2',
    markdown_content=markdown,
    _user_id=12,
    _injected_credentials=True
)

print(f"Document created: {result['document_url']}")
print(f"Bookmark: {result['document_url']}#bookmark=executive_summary")
```

**Result:**
- ✅ Headings: H1 at 16pt (was 20pt), H2 at 14pt (was 18pt)
- ✅ Bookmarks: `executive_summary`, `key_metrics`, `risk_assessment`
- ✅ Table: Formatted with bold headers and italic changes
- ✅ Lists: Properly indented with bold/italic support

---

### Example 2: Sales Dashboard with Excel Export

```python
# Create formatted Google Sheet
result = google_sheets_create(
    title='Weekly Sales Dashboard',
    headers=[
        '# Product Line',
        '**Week 1**',
        '**Week 2**',
        '**Week 3**',
        '**Status**'
    ],
    data=[
        ['**Premium Software**', '$145K', '$168K', '$182K', '[G]+26%'],
        ['Standard Services', '$85K', '$78K', '$92K', '[G]+8%'],
        ['Basic Support', '$34K', '$29K', '$25K', '[R]-26%'],
        ['**TOTAL**', '**$264K**', '**$275K**', '**$299K**', '[G]+13%']
    ],
    parse_markdown=True,
    _user_id=12,
    _injected_credentials=True
)

print(f"View online: {result['url']}")
print(f"Download Excel: {result['excel_export_url']}")
print(f"Download CSV: {result['capabilities']['download_csv']}")
print(f"Download PDF: {result['capabilities']['download_pdf']}")

# Send Excel link via email
send_email(
    to='sales-team@company.com',
    subject='Weekly Sales Dashboard',
    body=f'''
    Hi Team,
    
    This week's sales dashboard is ready:
    - View online: {result['url']}
    - Download Excel: {result['excel_export_url']}
    
    Key highlights:
    - Overall growth: +13%
    - Premium software leading at +26%
    - Basic support needs attention (-26%)
    
    Best regards
    '''
)
```

**Result:**
- ✅ Bold headers (`# Product Line`, `**Week 1**`)
- ✅ Colored text (`[G]` = green for growth, `[R]` = red for decline)
- ✅ Excel download preserves ALL formatting
- ✅ Multiple download options available

---

### Example 3: Technical Manual with TOC

```python
markdown = '''
# Technical Installation Guide

<<TOC>>

<<BOOKMARK:prerequisites>>
## Prerequisites

Before installing, ensure you have:
- Python 3.9 or higher
- PostgreSQL 14+
- Node.js 18+

<<BOOKMARK:installation>>
## Installation Steps

### 1. Clone Repository
```
git clone https://github.com/company/project.git
cd project
```

### 2. Install Dependencies
```
pip install -r requirements.txt
npm install
```

<<BOOKMARK:configuration>>
## Configuration

Edit the `.env` file with your settings:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_HOST` | **Yes** | localhost | Database host |
| `DB_PORT` | No | 5432 | Database port |
| `API_KEY` | **Yes** | - | Your API key |

<<BOOKMARK:troubleshooting>>
## Troubleshooting

### Common Issues

#### Database Connection Failed
- Check PostgreSQL is running
- Verify `.env` settings
- Test connection: `psql -h localhost -U postgres`

#### Port Already in Use
- Change port in `.env`
- Or kill existing process: `lsof -ti:5001 | xargs kill`
'''

# DOCX V2 supports TOC (Smart Update doesn't)
result = google_docs_smart_create_from_markdown_v2(
    title='Installation Guide with TOC',
    markdown_content=markdown,
    _user_id=12,
    _injected_credentials=True
)

print(f"Document created: {result['document_url']}")
print("Open in Word and right-click TOC to update page numbers")
```

**Result:**
- ✅ Auto-generated table of contents
- ✅ Four bookmarks for navigation
- ✅ Code blocks formatted
- ✅ Tables with bold headers
- ✅ Nested headings (H2, H3, H4)

---

## 🎯 Choose Your Method

### Smart Update (API-based)

**Best for:**
- ✅ Images/media
- ✅ Online-only documents
- ✅ Maximum formatting control
- ✅ Page breaks

**Use when:**
- Document needs images
- You want `<<NEW-PAGE>>` support
- Speed is less critical (2-8 seconds)

**Example:**
```python
result = google_docs_smart_create_from_markdown(
    title='My Document',
    markdown_content=markdown,
    _user_id=12,
    _injected_credentials=True
)
```

### DOCX V2 (Upload-based)

**Best for:**
- ✅ Speed (0.5-2 seconds)
- ✅ Table of contents
- ✅ Large documents
- ✅ Offline editing

**Use when:**
- Need TOC with page numbers
- Document is very large
- Speed is important
- Users will download as DOCX

**Example:**
```python
result = google_docs_smart_create_from_markdown_v2(
    title='My Document V2',
    markdown_content=markdown,
    _user_id=12,
    _injected_credentials=True
)
```

---

## 📋 Markdown Cheat Sheet

### Basic Formatting
```markdown
**bold text**           → Bold
*italic text*           → Italic
`inline code`           → Code
~~strikethrough~~       → Strikethrough
==highlighted text==    → Yellow highlight
```

### Headings (Google Docs)
```markdown
# Main Title (20pt)
## Section (18pt)
### Sub-section (16pt)
#### List Header (14pt)
```

### Lists
```markdown
- Bullet point
  - Nested bullet
    - Deep nested

1. Numbered item
   1. Nested number
```

### Tables
```markdown
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| **Bold** | *Italic* | `Code`   |
| Cell A   | Cell B   | Cell C   |
```

### Special Commands
```markdown
<<BOOKMARK:name>>       → Create bookmark
<<TOC>>                 → Table of contents (DOCX V2 only)
<<NEW-PAGE>>            → Page break (Smart Update only)
---                     → Horizontal line
```

### Sheets: Headers and Formatting
```python
# Headers (larger, bold text)
headers = ['# Product', '**Q1**', '*Notes*']

# Alignment
'(L)Left aligned'
'(R)Right aligned'
'(C)Centered'

# Text colors (compact)
'[R]Red text'
'[G]Green text'
'[B]Blue text'
'[P]Purple text'

# Backgrounds (compact)
'{LR}Light red background'
'{LG}Light green background'
'{LB}Light blue background'

# Inline formatting
'**Bold**'
'*Italic*'
'`Code`'
```

---

## ⚡ Real-World Scenarios

### Scenario 1: Weekly Report to Stakeholders

```python
# 1. Create formatted sheet
result = google_sheets_create(
    title=f'Weekly Report - Week {week_number}',
    headers=['# Metric', '**This Week**', '**Last Week**', '**Change**'],
    data=weekly_data,  # Your data with [G]/[R] color codes
    parse_markdown=True,
    _user_id=12,
    _injected_credentials=True
)

# 2. Email stakeholders with Excel link
send_email(
    to='stakeholders@company.com',
    subject=f'Weekly Report - Week {week_number}',
    body=f'''
    Hi Team,
    
    This week's performance report is ready.
    
    View online: {result['url']}
    Download Excel: {result['excel_export_url']}
    
    Quick summary: {summary_text}
    '''
)

# Result: Stakeholders can view online OR download formatted Excel
```

### Scenario 2: Policy Document with Navigation

```python
markdown = '''
# Company Policy Handbook 2024

<<BOOKMARK:code_of_conduct>>
## Code of Conduct
All employees must...

<<BOOKMARK:leave_policy>>
## Leave Policy
Annual leave entitlement...

<<BOOKMARK:expense_policy>>
## Expense Reimbursement
Submit expenses within 30 days...

<<BOOKMARK:remote_work>>
## Remote Work Guidelines
Remote work is permitted...
'''

# Create with bookmarks
result = google_docs_smart_create_from_markdown(
    title='Policy Handbook 2024',
    markdown_content=markdown,
    _user_id=12,
    _injected_credentials=True
)

# Share specific sections
print(f"Code of Conduct: {result['document_url']}#bookmark=code_of_conduct")
print(f"Leave Policy: {result['document_url']}#bookmark=leave_policy")

# Result: Easy navigation to specific policy sections
```

### Scenario 3: Technical Documentation

```python
markdown = '''
# API Documentation

<<TOC>>

<<BOOKMARK:authentication>>
## Authentication

All API requests require authentication...

<<BOOKMARK:endpoints>>
## API Endpoints

### GET /users
Retrieve user list...

### POST /users
Create new user...

<<BOOKMARK:error_codes>>
## Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Missing API key |
| 404 | Not Found | Resource doesn't exist |
'''

# DOCX V2 for TOC support
result = google_docs_smart_create_from_markdown_v2(
    title='API Documentation v2.0',
    markdown_content=markdown,
    _user_id=12,
    _injected_credentials=True
)

# Result: Professional API docs with TOC and bookmarks
```

---

## 🔧 Troubleshooting

### Bookmarks Not Working?

**Check:**
1. ✅ Used correct syntax: `<<BOOKMARK:name>>`
2. ✅ Bookmark name is valid (letters, numbers, underscores only)
3. ✅ No spaces in bookmark name

**Fix:**
```markdown
# Bad
<<BOOKMARK:my section>>  ❌ Has space

# Good
<<BOOKMARK:my_section>>  ✅ Underscore instead
```

### Headings Still Too Large?

**Check:**
1. ✅ Restarted Flask server: `BISTART`
2. ✅ Using latest code
3. ✅ Cleared browser cache

**Verify:**
```python
# Should show: H1:16pt, H2:14pt, H3:12pt, H4:11pt
# (Not old sizes: H1:20pt, H2:18pt, H3:16pt)
```

### Excel Export Not Showing?

**Check:**
1. ✅ Using `google_sheets_create` (not other sheets functions)
2. ✅ Checking `result['excel_export_url']` or `result['capabilities']`

**Example:**
```python
result = google_sheets_create(...)

# Old way (still works)
print(result['url'])

# NEW ways
print(result['excel_export_url'])  # Direct Excel link
print(result['capabilities']['download_excel'])  # Same thing
```

### TOC Not Generating?

**Check:**
1. ✅ Using DOCX V2 method (not Smart Update)
2. ✅ Used `<<TOC>>` command
3. ✅ Opened in Microsoft Word (not just Google Docs)

**How to update TOC in Word:**
1. Open document in Word
2. Right-click on TOC area
3. Select "Update Field"
4. Choose "Update entire table"

---

## 📝 Before You Start

### 1. Restart Flask Server
```powershell
BISTART
```

### 2. Test with Simple Example
```python
markdown = '''
# Test Document

<<BOOKMARK:test_section>>
## Test Section
This is a test with **bold** and *italic* text.
'''

result = google_docs_smart_create_from_markdown(
    title='Simple Test',
    markdown_content=markdown,
    _user_id=12,
    _injected_credentials=True
)

print(f"Success! Document: {result['document_url']}")
```

### 3. Try Your Financial Report
```python
# Now test with your actual financial report markdown
# All formatting should work perfectly!
```

---

## 🎉 What's New Summary

| Feature | Before | After |
|---------|--------|-------|
| **Headings** | H1:20pt, H2:18pt (too large) | H1:16pt, H2:14pt (readable) |
| **Navigation** | Manual scrolling | Bookmarks with direct links |
| **Excel Export** | Copy/paste to Excel | One-click download with formatting |
| **TOC** | Manual creation | Auto-generated (DOCX V2) |
| **Document Size** | Presentation-style | Professional business style |

---

**Ready to use! Just run `BISTART` and start creating documents.**

**Last Updated:** November 9, 2025
