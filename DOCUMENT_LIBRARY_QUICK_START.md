# Document Library - Quick Start Guide

## 🎯 What Is This?

A **universal document library** with advanced search capabilities that AI agents can use to find documents across:
- Google Drive
- OneDrive
- Dropbox
- SharePoint
- Internal documents

## 🔍 Search Types

### 1. **Full-Text Search** (Fast, Exact Matches)
```python
registry.execute_tool(
    'document_library_search_fulltext',
    query='contract agreement',
    limit=10,
    _user_id=12
)
```
**Use when:** Looking for specific keywords or phrases

### 2. **Semantic Search** (Conceptual Similarity)
```python
registry.execute_tool(
    'document_library_search_semantic',
    query='machine learning best practices',
    threshold=0.3,
    _user_id=12
)
```
**Use when:** Finding related concepts, "documents like this"

### 3. **Hybrid Search** (Best of Both)
```python
registry.execute_tool(
    'document_library_search_hybrid',
    query='sales performance report',
    _user_id=12
)
```
**Use when:** Want comprehensive results (keywords + concepts)

## 🎛️ Advanced Filtering

```python
registry.execute_tool(
    'document_library_filter_advanced',
    must=[
        {'field': 'source', 'operator': 'equals', 'value': 'google_drive'},
        {'field': 'file_type', 'operator': 'equals', 'value': 'document'}
    ],
    range_filters={
        'created_at': {'gte': '2024-01-01', 'lte': '2024-12-31'}
    },
    _user_id=12
)
```

**Operators Available:**
- `equals`, `not_equals`
- `contains`, `starts_with`, `ends_with`
- `in` (array), `is_null`, `is_not_null`
- Range: `gte` (≥), `lte` (≤), `gt` (>), `lt` (<)

## 📊 Get Statistics

```python
# Get facets for filter UI
facets = registry.execute_tool(
    'document_library_get_facets',
    _user_id=12
)

# Get library stats
stats = registry.execute_tool(
    'document_library_get_stats',
    _user_id=12
)
```

## 🚀 Quick Commands

**List recent documents:**
```python
registry.execute_tool('document_library_list', limit=20, _user_id=12)
```

**Get document details:**
```python
registry.execute_tool('document_library_get', document_id='doc_123', _user_id=12)
```

**Add document:**
```python
registry.execute_tool(
    'document_library_add',
    document_id='gdrive_abc',
    source='google_drive',
    title='Q4 Report',
    _user_id=12
)
```

## 🎨 Filter Examples

**Documents from last quarter:**
```python
range_filters={'created_at': {'gte': '2024-10-01', 'lte': '2024-12-31'}}
```

**Large files only:**
```python
range_filters={'file_size_bytes': {'gte': 10485760}}  # > 10MB
```

**Tagged documents:**
```python
must=[{'field': 'tags', 'operator': 'contains', 'value': 'important'}]
```

**Exclude archived:**
```python
must_not=[{'field': 'is_archived', 'operator': 'equals', 'value': True}]
```

## 📁 Files Created

- `create_document_library_with_search.sql` - Database schema
- `document_library_routes.py` - API endpoints
- `document_library_tools.json` - AI tool definitions
- `document_library.py` - AI tool implementations

## 📝 Next Steps

1. Deploy database schema to Supabase
2. Create frontend UI module
3. Integrate with Google Drive/OneDrive APIs
4. Set up automatic syncing

## 🔗 Full Documentation

See `DOCUMENT_LIBRARY_SEARCH_IMPLEMENTATION_COMPLETE.md` for complete details.
