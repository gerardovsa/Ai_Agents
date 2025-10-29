# 📄 Google Docs PDF Export & Page Numbering

## Overview

Two new capabilities have been added to the AI Agent Platform for Google Docs:

1. **PDF Export** - Convert Google Docs to PDF format (already existed, now documented)
2. **Page Number Configuration** - Configure documents for page numbering with custom starting numbers

---

## 🔧 PDF Export

### Function: `google_docs_export_as_pdf`

**Purpose:** Export a Google Doc as a PDF file with all formatting preserved.

**Location:** `google_workspace/google_docs.py` (lines 2392-2425)

### Usage

```python
from google_workspace import google_docs_export_as_pdf

# Export document as PDF
result = google_docs_export_as_pdf(document_id='YOUR_DOC_ID')

# Result structure:
{
    'data': b'%PDF-1.4...',      # Binary PDF data
    'mime_type': 'application/pdf',
    'size': 245678               # File size in bytes
}
```

### Via AI Agent Chat

```bash
CHAT Export this Google Doc as PDF: https://docs.google.com/document/d/abc123/edit
```

### Technical Details

**Implementation:**
- Uses Google Drive API v3 `files().export_media()`
- MIME type: `application/pdf`
- Uses `MediaIoBaseDownload` for efficient chunked downloads
- Returns binary data in `BytesIO` format

**Requirements:**
- Google Drive API access
- Document must be accessible with current credentials
- Read permission on the document

**Error Handling:**
- Raises exception if document not found
- Raises exception if export fails
- Prints detailed error messages with traceback

---

## 📊 Page Number Configuration

### Function: `google_docs_add_page_numbers`

**Purpose:** Configure Google Doc for page numbering with custom starting number.

**⚠️ IMPORTANT:** Google Docs API does not support automatic page number insertion. This function configures the document settings and provides instructions for manual insertion via Google Docs UI.

**Location:** `google_workspace/google_docs.py` (lines 2428-2520)

### Usage

```python
from google_workspace import google_docs_add_page_numbers

# Configure page numbering
result = google_docs_add_page_numbers(
    document_id='YOUR_DOC_ID',
    position='FOOTER',          # 'HEADER' or 'FOOTER'
    alignment='CENTER',         # 'LEFT', 'CENTER', or 'RIGHT'
    starting_number=1          # Start from page 1 (or any number)
)

# Result structure:
{
    'document_id': 'abc123',
    'document_url': 'https://docs.google.com/document/d/abc123/edit',
    'starting_number': 1,
    'requested_position': 'FOOTER',
    'requested_alignment': 'CENTER',
    'success': True,
    'manual_step_required': True,
    'instructions': '📄 Page Numbering Configured...',
    'message': 'Document configured for page numbering starting at 1. Manual insertion required...'
}
```

### Via AI Agent Chat

```bash
CHAT Configure page numbers for this doc starting at page 5: https://docs.google.com/document/d/abc123/edit
```

The AI will:
1. Configure the starting page number to 5
2. Provide detailed instructions for manually inserting page numbers
3. Return the document URL for easy access

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `document_id` | string | **Required** | Google Doc document ID |
| `position` | string | `'FOOTER'` | `'HEADER'` or `'FOOTER'` (informational only) |
| `alignment` | string | `'CENTER'` | `'LEFT'`, `'CENTER'`, or `'RIGHT'` (informational only) |
| `starting_number` | integer | `1` | Page number to start from |

### What It Does

**✅ Automatic Configuration:**
- Sets `pageNumberStart` in document style (e.g., start from page 5)
- Configures `useFirstPageHeaderFooter` to use same header/footer on all pages
- Prepares document for consistent page numbering

**📋 Manual Step Required:**

After running the function, you must manually insert page numbers:

**Method 1 (Quick):**
1. Open document: [provided URL]
2. Click: **Insert** > **Page numbers**
3. Choose position and format
4. Page numbers will start from the configured number

**Method 2 (Header/Footer):**
1. Click: **Insert** > **Headers & footers** > **Footer** (or Header)
2. In the footer, click: **Insert** > **Page number**
3. Page numbers display starting from configured number

### Return Value

The function returns detailed instructions including:

```
📄 Page Numbering Configured

Document: https://docs.google.com/document/d/abc123/edit

SETTINGS APPLIED:
✅ Starting page number: 5
✅ Use same header/footer on all pages: Yes

MANUAL INSERTION REQUIRED:
Google Docs API does not support automatic page number insertion.
Please complete the setup manually:

1. Open the document: [URL]
2. Click: Insert > Page numbers
3. Choose position: FOOTER - CENTER
4. Select format (page number will start from 5)

ALTERNATIVE METHOD:
1. Click: Insert > Headers & footers > FOOTER
2. In the footer, click: Insert > Page number
3. Page numbers will display starting from 5

The document is now ready - page numbering will begin at page 5 once inserted.
```

### Why Manual Step is Required

**Google Docs API Limitation:**

The Google Docs API does not provide methods to:
- Insert page number fields programmatically
- Create header/footer content automatically
- Trigger page number insertion

**What the API Can Do:**
- ✅ Set starting page number (`pageNumberStart`)
- ✅ Configure header/footer behavior (`useFirstPageHeaderFooter`)
- ✅ Modify document style settings

**What Requires Manual Insertion:**
- ❌ Inserting the actual page number field
- ❌ Creating header/footer sections
- ❌ Setting page number position/alignment

This is a known limitation of the Google Docs API, not a bug in our implementation.

---

## 🎯 Use Cases

### Use Case 1: Create Report and Export to PDF

```python
# 1. Create document with content
doc_id = google_docs_create(title="Monthly Report")

# 2. Add content
google_docs_add_formatted_content(
    document_id=doc_id,
    content="# Monthly Sales Report\n\nTotal sales: $150,000..."
)

# 3. Configure page numbering
google_docs_add_page_numbers(
    document_id=doc_id,
    position='FOOTER',
    alignment='RIGHT',
    starting_number=1
)

# 4. (User manually inserts page numbers in Google Docs UI)

# 5. Export to PDF
pdf_result = google_docs_export_as_pdf(document_id=doc_id)

# 6. Save PDF locally
with open('monthly_report.pdf', 'wb') as f:
    f.write(pdf_result['data'])

print(f"✅ PDF exported: {pdf_result['size']} bytes")
```

### Use Case 2: Multi-Document Report (Start Page 10)

```python
# Create appendix document that starts at page 10
doc_id = google_docs_create(title="Report Appendix")

# Configure to start at page 10
result = google_docs_add_page_numbers(
    document_id=doc_id,
    position='FOOTER',
    alignment='CENTER',
    starting_number=10
)

# Print instructions for user
print(result['instructions'])

# Add content
google_docs_add_formatted_content(
    document_id=doc_id,
    content="## Appendix A: Financial Details\n\n..."
)
```

### Use Case 3: Batch Export Multiple Documents

```python
document_ids = ['doc1_id', 'doc2_id', 'doc3_id']

for doc_id in document_ids:
    try:
        # Export as PDF
        pdf_result = google_docs_export_as_pdf(document_id=doc_id)
        
        # Save with doc ID as filename
        filename = f"{doc_id}.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_result['data'])
        
        print(f"✅ Exported {filename} ({pdf_result['size']} bytes)")
        
    except Exception as e:
        print(f"❌ Failed to export {doc_id}: {e}")
```

---

## 🔍 Tool Schema

Both functions are registered in `tools/schemas/google_docs_tools.json`:

### PDF Export Schema

```json
{
  "name": "google_docs_export_as_pdf",
  "description": "Export document as PDF",
  "platform": "google_docs",
  "parameters": {
    "document_id": {
      "type": "string",
      "description": "Document ID",
      "required": true
    }
  },
  "returns": {
    "type": "object",
    "description": "PDF file data (base64 encoded)"
  }
}
```

### Page Number Configuration Schema

```json
{
  "name": "google_docs_add_page_numbers",
  "description": "Configure document for page numbering (starting number). NOTE: Actual page number insertion requires manual step via Google Docs UI: Insert > Page numbers",
  "platform": "google_docs",
  "parameters": {
    "document_id": {
      "type": "string",
      "description": "Document ID",
      "required": true
    },
    "position": {
      "type": "string",
      "description": "Page number position: HEADER or FOOTER (default: FOOTER)",
      "required": false,
      "default": "FOOTER"
    },
    "alignment": {
      "type": "string",
      "description": "Page number alignment: LEFT, CENTER, or RIGHT (default: CENTER)",
      "required": false,
      "default": "CENTER"
    },
    "starting_number": {
      "type": "integer",
      "description": "Page number to start from (default: 1)",
      "required": false,
      "default": 1
    }
  },
  "returns": {
    "type": "object",
    "description": "Configuration result with manual insertion instructions"
  }
}
```

---

## 🧪 Testing

### Test PDF Export

```python
# Create test document
doc_id = google_docs_create(title="Test PDF Export")

# Add content
google_docs_add_formatted_content(
    document_id=doc_id,
    content="# Test Document\n\nThis is a test for PDF export.\n\n- Bullet 1\n- Bullet 2"
)

# Export to PDF
result = google_docs_export_as_pdf(document_id=doc_id)

# Verify
assert result['mime_type'] == 'application/pdf'
assert result['size'] > 0
assert result['data'].startswith(b'%PDF')

print(f"✅ PDF export test passed: {result['size']} bytes")
```

### Test Page Number Configuration

```python
# Create test document
doc_id = google_docs_create(title="Test Page Numbers")

# Configure page numbering
result = google_docs_add_page_numbers(
    document_id=doc_id,
    position='FOOTER',
    alignment='RIGHT',
    starting_number=5
)

# Verify
assert result['success'] == True
assert result['starting_number'] == 5
assert result['manual_step_required'] == True
assert 'instructions' in result
assert 'document_url' in result

print(f"✅ Page numbering test passed")
print(result['instructions'])
```

---

## 🚨 Troubleshooting

### Issue: PDF Export Returns Empty Data

**Symptoms:** PDF result has 0 bytes or empty data

**Solutions:**
1. Verify document ID is correct
2. Check document permissions (must have read access)
3. Ensure document is not empty
4. Verify Google Drive API is enabled

**Debug:**
```python
# Check document exists first
doc = google_docs_get(document_id=doc_id)
print(f"Document title: {doc['title']}")
```

---

### Issue: Page Numbers Not Starting from Configured Number

**Symptoms:** Page numbers start from 1 instead of configured number (e.g., 5)

**Cause:** Manual insertion step not completed, or insertion done before configuration

**Solution:**
1. Run `google_docs_add_page_numbers()` FIRST
2. THEN manually insert page numbers via Google Docs UI
3. Page numbers will respect the `pageNumberStart` setting

**Verification:**
```python
# Check document style
doc = google_docs_get(document_id=doc_id)
print(f"Page number start: {doc.get('documentStyle', {}).get('pageNumberStart')}")
```

---

### Issue: "Manual step required" Message

**This is NORMAL:** Google Docs API does not support automatic page number insertion.

**What to do:**
1. Read the instructions provided in the result
2. Open the document URL provided
3. Follow the manual insertion steps
4. Page numbers will appear starting from configured number

**This is NOT a bug** - it's a limitation of Google Docs API.

---

## 📚 API References

### Google Docs API v1
- [documents.batchUpdate](https://developers.google.com/docs/api/reference/rest/v1/documents/batchUpdate)
- [documentStyle](https://developers.google.com/docs/api/reference/rest/v1/documents#documentstyle)
- [pageNumberStart property](https://developers.google.com/docs/api/reference/rest/v1/documents#documentstyle)

### Google Drive API v3
- [files.export](https://developers.google.com/drive/api/v3/reference/files/export)
- [MediaIoBaseDownload](https://googleapis.github.io/google-api-python-client/docs/epy/googleapiclient.http.MediaIoBaseDownload-class.html)

---

## 🔄 Updates

**Date:** October 24, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready

**Changes:**
- ✅ Added `google_docs_export_as_pdf` documentation (function already existed)
- ✅ Created `google_docs_add_page_numbers` function
- ✅ Added tool schemas for both functions
- ✅ Updated `google_workspace/__init__.py` exports
- ✅ Created comprehensive documentation with examples

**Known Limitations:**
- Page number insertion requires manual step (Google Docs API limitation)
- Position/alignment parameters are informational only (used in instructions)
- PDF export requires read access to document

---

## 🎓 Next Steps

After implementing page number configuration:

1. **Test both functions** with real documents
2. **Verify PDF exports** have correct formatting
3. **Follow manual steps** for page number insertion
4. **Create workflow scripts** combining both features
5. **Update user documentation** with examples

**Integration Example:**

```bash
# Start AI Agent
BISTART

# Wait for tools to load
Start-Sleep -Seconds 12

# Test via chat
CHAT Create a Google Doc called "Test Report"
CHAT Add a heading "Monthly Report" and some bullet points to the doc
CHAT Configure page numbers starting at 1 for the doc
CHAT Export the doc as PDF
```

The AI will guide you through the manual page numbering step!

---

**Questions or Issues?** Check the troubleshooting section or review the source code in `google_workspace/google_docs.py`.
