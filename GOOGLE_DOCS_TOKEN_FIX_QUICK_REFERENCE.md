# Google Docs Token Overflow - Quick Reference

## Problem
```
Error: prompt is too long: 209727 tokens > 200000 maximum
```

## Solution Summary

| Tool | Tokens | When to Use |
|------|--------|-------------|
| `google_docs_get_document()` | **500** | Check title & preview (DEFAULT) |
| `google_docs_search_document(query='X')` | **2,000** | Find specific info (RECOMMENDED) |
| `google_docs_get_document(format='text')` | **50K** | Read full text (small docs only) |
| `google_docs_get_document(format='markdown')` | **55K** | Read formatted (small docs only) |
| `google_docs_get_document(format='full')` | **200K+** | ❌ NEVER (causes errors) |

---

## Code Examples

### ✅ Recommended: Get Summary (Always Works)
```python
result = execute_tool(
    'google_docs_get_document',
    document_id='1M11p3SwvTHFSF5pcJd-oq2w9E_ShaBL17IMckkpkvj0'
)
# Returns: 500 tokens (title + 2K preview)
```

### ✅ Best: Search for Specific Content
```python
result = execute_tool(
    'google_docs_search_document',
    document_id='1M11p3SwvTHFSF5pcJd-oq2w9E_ShaBL17IMckkpkvj0',
    query='clinical competence',
    context_chars=800
)
# Returns: ~2K tokens (matching sections only)
```

### ⚠️ Use Carefully: Full Text (Small Docs Only)
```python
result = execute_tool(
    'google_docs_get_document',
    document_id='small_doc_id',
    format='text'  # or 'markdown'
)
# Returns: 10K-50K tokens (depends on size)
```

### ❌ Never: Full JSON
```python
# DON'T DO THIS - causes 400 errors on large docs
result = execute_tool(
    'google_docs_get_document',
    document_id='doc_id',
    format='full'  # ❌ 200K+ tokens
)
```

---

## AI Agent Workflow

```
User: "What does this document say about X?"

Step 1: Check document exists
  → google_docs_get_document(doc_id)
  → Returns: title + preview (500 tokens)

Step 2: Search for specific content  
  → google_docs_search_document(doc_id, query='X')
  → Returns: relevant sections (2K tokens)

Step 3: Answer user question
  → Use search results to formulate answer
```

---

## Token Savings

| Document Size | OLD (format='full') | NEW (search) | Savings |
|---------------|---------------------|--------------|---------|
| 100 pages | 237K tokens ❌ | 2K tokens ✅ | **99%** |
| 50 pages | 120K tokens ❌ | 2K tokens ✅ | **98%** |
| 20 pages | 45K tokens ⚠️ | 2K tokens ✅ | **95%** |
| 5 pages | 12K tokens ⚠️ | 2K tokens ✅ | **83%** |

---

## Format Parameter

```python
format='summary'   # ✅ DEFAULT - 500 tokens (preview)
format='text'      # ⚠️ 10K-50K tokens (plain text)
format='markdown'  # ⚠️ 10K-55K tokens (formatted)
format='full'      # ❌ 200K+ tokens (causes errors)
```

---

## Quick Decision Tree

```
Need document info?
├─ Just checking title/preview? → format='summary' (DEFAULT)
├─ Looking for specific content? → google_docs_search_document()
├─ Need full text of small doc? → format='text' or 'markdown'
└─ Need complete JSON? → ❌ DON'T (use search instead)
```

---

## Common Use Cases

**"Summarize this document"**
```python
# Get preview + search key sections
summary = google_docs_get_document(doc_id)
key_sections = google_docs_search_document(doc_id, query='key terms')
```

**"What does it say about X?"**
```python
# Search for X
results = google_docs_search_document(doc_id, query='X')
```

**"Read this short document"**
```python
# Only if you know it's <50 pages
text = google_docs_get_document(doc_id, format='text')
```

---

## Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| `prompt too long: 209727 tokens` | Used `format='full'` on large doc | Use default (summary) or search |
| `400 - maximum 200000` | Returned too much data | Use `google_docs_search_document()` |
| `No matches found` | Search query didn't match | Try different keywords |

---

**Files Modified**:
- `google_workspace/google_docs.py` (added format parameter + search function)
- `tools/schemas/google_docs_tools.json` (updated schema + added search tool)

**Date**: November 27, 2025  
**Status**: ✅ Production Ready
