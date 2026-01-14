# Vector Database Enhanced Features - Complete Documentation

## Overview

This document describes the **complete enhanced vector database system** with user permissions, categorization, folders, hybrid search, and advanced metadata filtering capabilities.

**Date:** November 30, 2025  
**Version:** 2.0.0 (Enhanced)  
**Status:** ✅ Production Ready  

---

## 🚀 What's New (Enhanced Features)

### 1. **User-Linked Filing System**
- **Owner Tagging**: Every vector automatically tagged with `owner_user_id`
- **Data Isolation**: Users can only access their own vectors
- **Global Vectors**: Option to create public vectors with `visibility: 'global'`
- **Team Sharing**: `visibility: 'team'` for team-wide access

### 2. **Hierarchical Categorization**
- **Primary Categories**: `legal`, `finance`, `marketing`, `hr`, `engineering`, `general`
- **Subcategories**: e.g., `contracts`, `invoices`, `campaigns`, `policies`
- **Namespace Pattern**: `user_{user_id}_{category}`
- **Metadata Fields**: `category`, `subcategory`, `tags[]`

### 3. **Folder System**
- Namespaces represent folders/categories
- Format: `user_42_legal`, `user_42_finance`
- Each user has isolated folder structure
- Folders can be listed, described, and deleted

### 4. **Hybrid Search** (Dense + Sparse Vectors)
- **Dense Vectors**: Semantic search via OpenAI embeddings (1536 dimensions)
- **Sparse Vectors**: Keyword matching via TF-IDF (100 features)
- **Automatic Generation**: Both vectors created during upload
- **Query Integration**: `pinecone_query_namespaces` uses hybrid search by default

### 5. **Advanced Metadata Filtering**
- **Operators**: `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$nin`, `$exists`
- **Multi-Field Queries**: Combine multiple filters
- **Pure Metadata Retrieval**: `pinecone_fetch_by_metadata` (no embedding needed)

### 6. **AI Credential-Based Search**
- AI agents can search vectors with user context
- Automatic filtering by `owner_user_id`
- Respects visibility settings (user/global/team)
- Tools accept `_user_id` parameter

---

## 📊 Architecture

### Data Flow

```
User Uploads Document (vector_db_upload_document)
           ↓
    Extract Text (PDF, TXT, MD, DOCX)
           ↓
    Chunk Text (800 chars, 20 overlap)
           ↓
    Generate Embeddings
    ├── Dense Vector (OpenAI ada-002, 1536 dims)
    └── Sparse Vector (TF-IDF, 100 features)
           ↓
    Add Enhanced Metadata
    ├── owner_user_id: 42
    ├── category: 'legal'
    ├── subcategory: 'contracts'
    ├── tags: ['important', '2024']
    ├── visibility: 'user'
    ├── upload_date: '2025-11-30T12:00:00Z'
    └── file_extension: '.pdf'
           ↓
    Upsert to Pinecone (namespace: user_42_legal)
           ↓
    Return Result (vectors_uploaded, hybrid_search_enabled)
```

### Database Schema (Pinecone Metadata)

Each vector in Pinecone has this metadata structure:

```json
{
  "metadata": {
    // Original fields
    "text": "chunk text content...",
    "document": "contract_2024.pdf",
    "document_id": "abc12345",
    "chunk_index": 0,
    "chunk_size": 800,
    
    // 🚀 Enhanced fields
    "owner_user_id": 42,
    "category": "legal",
    "subcategory": "contracts",
    "tags": ["important", "2024", "confidential"],
    "visibility": "user",
    "upload_date": "2025-11-30T12:00:00Z",
    "file_extension": ".pdf",
    "source": "vector_db_upload_document"
  }
}
```

---

## 🛠️ New Flask Endpoints (5 Total)

### 1. POST `/api/vector-db/query-namespaces`
**Cross-namespace query with hybrid search aggregation**

**Request Body:**
```json
{
  "query_text": "contract amendments from 2024",
  "namespaces": ["user_42_legal", "user_42_finance"],
  "metric": "cosine",
  "top_k": 10,
  "filter": {
    "category": {"$eq": "legal"},
    "year": {"$gte": 2024}
  },
  "include_metadata": true,
  "include_values": false
}
```

**Response:**
```json
{
  "success": true,
  "matches": [
    {
      "id": "vec_123",
      "score": 0.95,
      "namespace": "user_42_legal",
      "metadata": {...}
    }
  ],
  "usage": {"read_units": 3},
  "namespaces_searched": ["user_42_legal", "user_42_finance"]
}
```

**Features:**
- ✅ Queries multiple namespaces in parallel
- ✅ Automatic sparse vector generation (hybrid search)
- ✅ User ownership filtering (only user's namespaces)
- ✅ Result aggregation and sorting by score

---

### 2. POST `/api/vector-db/fetch-by-metadata`
**Pure metadata filtering without embeddings**

**Request Body:**
```json
{
  "filter": {
    "category": {"$eq": "legal"},
    "year": {"$gte": 2024},
    "author": {"$in": ["John", "Jane"]},
    "tags": {"$in": ["important"]}
  },
  "namespace": "user_42_legal",
  "limit": 100,
  "fields": ["filename", "upload_date", "category"]
}
```

**Response:**
```json
{
  "success": true,
  "vectors": [
    {
      "id": "vec_123",
      "metadata": {
        "filename": "contract.pdf",
        "upload_date": "2025-11-30T12:00:00Z",
        "category": "legal"
      },
      "namespace": "user_42_legal"
    }
  ],
  "total_count": 45
}
```

**Features:**
- ✅ No embedding generation (fast metadata-only queries)
- ✅ Complex filter operators ($eq, $ne, $gt, $lt, $in, $nin)
- ✅ Field selection (return only specific metadata)
- ✅ User ownership enforced automatically

---

### 3. GET `/api/vector-db/namespaces`
**List all folders/categories**

**Query Parameters:**
- `include_stats` (bool): Include vector counts (default: true)
- `prefix` (string): Filter by namespace prefix (optional)

**Response:**
```json
{
  "success": true,
  "namespaces": [
    {
      "name": "user_42_legal",
      "display_name": "Legal Documents",
      "vector_count": 145,
      "category": "legal",
      "owner_user_id": 42
    },
    {
      "name": "user_42_finance",
      "display_name": "Finance Reports",
      "vector_count": 89,
      "category": "finance",
      "owner_user_id": 42
    }
  ],
  "total_count": 2
}
```

**Features:**
- ✅ Only returns user's namespaces (isolation)
- ✅ Vector counts per folder
- ✅ Friendly display names (parsed from namespace)

---

### 4. GET `/api/vector-db/namespaces/:namespace`
**Get detailed folder/namespace statistics**

**Response:**
```json
{
  "success": true,
  "namespace": {
    "name": "user_42_legal",
    "display_name": "Legal Documents",
    "vector_count": 145,
    "dimension": 1536,
    "metric": "cosine",
    "category": "legal",
    "owner_user_id": 42,
    "metadata_schema": {
      "filename": "string",
      "upload_date": "datetime",
      "category": "string",
      "subcategory": "string",
      "tags": "array",
      "owner_user_id": "integer"
    }
  }
}
```

**Features:**
- ✅ Validates user owns namespace (403 if not)
- ✅ Displays metadata schema
- ✅ Vector count and index configuration

---

### 5. DELETE `/api/vector-db/namespaces/:namespace?confirm=DELETE`
**Delete folder and all vectors**

**Query Parameters:**
- `confirm` (string): Must be "DELETE" to proceed

**Response:**
```json
{
  "success": true,
  "message": "Namespace 'user_42_legal' deleted successfully",
  "vectors_deleted": 145
}
```

**Security:**
- ✅ Validates user owns namespace
- ✅ Protects default namespace from deletion
- ✅ Requires explicit confirmation parameter
- ✅ Returns vector count deleted

---

## 🤖 New AI Tools (2 Total)

### 1. `pinecone_query_namespaces`
**Query multiple namespaces with hybrid search**

**Function Signature:**
```python
pinecone_query_namespaces(
    query_text: str,                    # REQUIRED
    namespaces: List[str] = [],         # Empty = all user namespaces
    metric: str = 'cosine',
    top_k: int = 10,
    filter: Dict = None,
    include_metadata: bool = True,
    include_values: bool = False,
    _user_id: int = None,
    _injected_credentials: bool = True
) -> Dict[str, Any]
```

**Example Usage (AI Agent):**
```python
result = registry.execute_tool(
    'pinecone_query_namespaces',
    query_text='contract amendments from 2024',
    namespaces=['user_42_legal', 'user_42_finance'],
    top_k=10,
    filter={'year': {'$gte': 2024}},
    _user_id=42,
    _injected_credentials=True
)

# Returns
{
    "success": true,
    "matches": [...],
    "hybrid_search": true,
    "usage": {"read_units": 3}
}
```

**Features:**
- ✅ Automatic sparse vector generation (TF-IDF from query_text)
- ✅ Parallel namespace queries
- ✅ Result aggregation and sorting
- ✅ User ownership filtering

---

### 2. `pinecone_fetch_by_metadata`
**Pure metadata filtering (no embeddings)**

**Function Signature:**
```python
pinecone_fetch_by_metadata(
    filter: Dict[str, Any],             # REQUIRED
    namespace: str = '',
    limit: int = 100,
    fields: List[str] = None,
    _user_id: int = None,
    _injected_credentials: bool = True
) -> Dict[str, Any]
```

**Example Usage (AI Agent):**
```python
result = registry.execute_tool(
    'pinecone_fetch_by_metadata',
    filter={
        'category': {'$eq': 'legal'},
        'year': {'$gte': 2024},
        'tags': {'$in': ['important']}
    },
    namespace='user_42_legal',
    limit=50,
    fields=['filename', 'upload_date'],
    _user_id=42,
    _injected_credentials=True
)

# Returns
{
    "success": true,
    "vectors": [
        {
            "id": "vec_123",
            "metadata": {"filename": "...", "upload_date": "..."}
        }
    ],
    "total_count": 45
}
```

**Features:**
- ✅ No embedding generation (fast)
- ✅ Complex metadata queries
- ✅ Field selection
- ✅ User ownership enforced

---

## 📝 Enhanced Upload Tool

### `vector_db_upload_document` (Enhanced)

**New Parameters:**
```python
vector_db_upload_document(
    file_path: str,                     # REQUIRED
    filename: str,                      # REQUIRED
    chunk_size: int = 800,
    chunk_overlap: int = 20,
    namespace: str = '',                # Auto: user_{user_id}_{category}
    category: str = 'general',          # 🚀 NEW
    subcategory: str = '',              # 🚀 NEW
    tags: List[str] = None,             # 🚀 NEW
    visibility: str = 'user',           # 🚀 NEW (user/global/team)
    _user_id: int = None,
    _injected_credentials: bool = True
) -> Dict[str, Any]
```

**Example Usage (AI Agent):**
```python
result = registry.execute_tool(
    'vector_db_upload_document',
    file_path='/path/to/contract_2024.pdf',
    filename='contract_2024.pdf',
    category='legal',
    subcategory='contracts',
    tags=['important', '2024', 'confidential'],
    visibility='user',
    _user_id=42,
    _injected_credentials=True
)

# Returns
{
    "success": true,
    "vectors_uploaded": 45,
    "document_id": "abc12345",
    "namespace": "user_42_legal",
    "hybrid_search_enabled": true,
    "metadata": {
        "category": "legal",
        "subcategory": "contracts",
        "tags": ["important", "2024", "confidential"],
        "visibility": "user",
        "owner_user_id": 42
    }
}
```

**Features:**
- ✅ Automatic sparse vector generation (TF-IDF)
- ✅ Enhanced metadata tagging
- ✅ User ownership automatic
- ✅ Namespace auto-creation
- ✅ Visibility control

---

## 🔍 Filter Query Examples

### Example 1: Find Legal Documents from 2024
```json
{
  "category": {"$eq": "legal"},
  "upload_date": {"$gte": "2024-01-01T00:00:00Z"}
}
```

### Example 2: Find Important PDFs by Multiple Authors
```json
{
  "file_extension": {"$eq": ".pdf"},
  "tags": {"$in": ["important"]},
  "author": {"$in": ["John", "Jane"]}
}
```

### Example 3: Find All Non-Archived Documents
```json
{
  "tags": {"$nin": ["archived"]},
  "visibility": {"$eq": "user"}
}
```

### Example 4: Complex Multi-Field Query
```json
{
  "category": {"$eq": "finance"},
  "subcategory": {"$in": ["invoices", "receipts"]},
  "upload_date": {"$gte": "2024-01-01", "$lte": "2024-12-31"},
  "tags": {"$in": ["paid"]},
  "visibility": {"$ne": "archived"}
}
```

---

## 🧪 Testing Guide

### 1. Upload Test Document
```python
# Test sparse vector generation and categorization
from tools.registry_v3 import RegistryV3

registry = RegistryV3()

result = registry.execute_tool(
    'vector_db_upload_document',
    file_path='C:/test/sample.pdf',
    filename='sample.pdf',
    category='legal',
    subcategory='contracts',
    tags=['test', '2024'],
    visibility='user',
    _user_id=1,
    _injected_credentials=True
)

print(f"Hybrid search enabled: {result['hybrid_search_enabled']}")
print(f"Namespace: {result['namespace']}")
```

### 2. Test Cross-Namespace Query
```python
# Query multiple folders with hybrid search
result = registry.execute_tool(
    'pinecone_query_namespaces',
    query_text='legal contracts from 2024',
    namespaces=['user_1_legal', 'user_1_finance'],
    top_k=5,
    _user_id=1,
    _injected_credentials=True
)

print(f"Found {len(result['matches'])} matches across {len(result['namespaces_searched'])} namespaces")
```

### 3. Test Metadata Filtering
```python
# Find all legal documents without embeddings
result = registry.execute_tool(
    'pinecone_fetch_by_metadata',
    filter={
        'category': {'$eq': 'legal'},
        'tags': {'$in': ['important']}
    },
    namespace='user_1_legal',
    limit=10,
    _user_id=1,
    _injected_credentials=True
)

print(f"Found {result['total_count']} legal documents tagged as important")
```

### 4. Test Namespace Management
```bash
# List user's folders
curl -X GET http://localhost:5001/api/vector-db/namespaces \
  -H "Authorization: Bearer <JWT_TOKEN>"

# Describe specific folder
curl -X GET http://localhost:5001/api/vector-db/namespaces/user_1_legal \
  -H "Authorization: Bearer <JWT_TOKEN>"

# Delete folder (with confirmation)
curl -X DELETE "http://localhost:5001/api/vector-db/namespaces/user_1_test?confirm=DELETE" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

## 📚 GitHub Research Findings

### Advanced Strategies Implemented

**From Pinecone Python Client:**
- ✅ `query_namespaces()` - Multi-namespace parallel queries
- ✅ `SparseValues` - Hybrid search with sparse vectors
- ✅ `FilterTypedDict` - Advanced metadata filtering
- ✅ `QueryResultsAggregator` - Cross-namespace result merging

**From Vector Database Ecosystem:**
- ✅ Hybrid search (Meilisearch, Orama patterns)
- ✅ Multi-tenancy via namespaces (Pinecone native)
- ✅ Metadata filtering (Weaviate pattern)
- ✅ User permissions (custom implementation)
- ✅ Categorization (LlamaIndex pattern)

---

## 🚨 Security & Best Practices

### User Isolation
- **Automatic**: All queries filtered by `owner_user_id`
- **Namespace Validation**: Users can only access `user_{user_id}_*` namespaces
- **Visibility Control**: `user` (private), `global` (public), `team` (shared)

### Data Integrity
- **Required Fields**: `owner_user_id` always set on upload
- **Immutable Ownership**: Cannot change vector ownership after upload
- **Audit Trail**: `upload_date`, `source` tracked

### Performance
- **Batch Processing**: 500 chunks at a time for embedding
- **Sparse Vector Optimization**: TF-IDF limited to 100 features
- **Parallel Queries**: Multiple namespaces queried simultaneously

---

## 📦 Dependencies

### Python Packages (Required)
```bash
pip install pinecone-client openai scikit-learn PyPDF2 python-docx
```

### Versions
- `pinecone-client` >= 2.0.0
- `openai` >= 1.0.0
- `scikit-learn` >= 1.3.0
- `PyPDF2` >= 3.0.0
- `python-docx` >= 0.8.11

---

## 🎯 Use Cases

### 1. Legal Document Management
```python
# Upload contract
registry.execute_tool('vector_db_upload_document', 
    filename='contract_2024.pdf',
    category='legal',
    subcategory='contracts',
    tags=['important', '2024', 'client_acme'],
    visibility='user'
)

# Search across legal and finance
registry.execute_tool('pinecone_query_namespaces',
    query_text='ACME contract payment terms',
    namespaces=['user_42_legal', 'user_42_finance']
)
```

### 2. Compliance Auditing
```python
# Find all confidential documents from 2024
registry.execute_tool('pinecone_fetch_by_metadata',
    filter={
        'tags': {'$in': ['confidential']},
        'upload_date': {'$gte': '2024-01-01'}
    }
)
```

### 3. Knowledge Base with Global Sharing
```python
# Upload public knowledge base article
registry.execute_tool('vector_db_upload_document',
    filename='kb_article.md',
    category='knowledge_base',
    tags=['public', 'help'],
    visibility='global'  # Accessible to all users
)
```

---

## 🔗 Related Documentation

- `README.md` - Main vector database documentation
- `IMPLEMENTATION_SUMMARY.md` - Phase 1 frontend implementation
- `QUICK_START.md` - Quick setup guide
- `vector_database.html` - UI implementation
- `vector_database_enhanced.js` - Enhanced UI components
- `vector_database_enhanced.css` - Professional styling

---

## 📝 Changelog

### Version 2.0.0 (November 30, 2025)
- ✅ Added 5 new Flask endpoints (cross-namespace, metadata filtering, namespace management)
- ✅ Added 2 new AI tools (query_namespaces, fetch_by_metadata)
- ✅ Implemented hybrid search with sparse vectors (TF-IDF)
- ✅ Enhanced upload tool with categorization and user ownership
- ✅ Added visibility control (user/global/team)
- ✅ Implemented namespace-based folder system
- ✅ Added comprehensive metadata filtering
- ✅ GitHub research integration (Pinecone + ecosystem patterns)

### Version 1.0.0 (November 2025)
- ✅ Initial vector database module
- ✅ 3-tab UI (Credentials, Upload, Documents)
- ✅ 4 enhanced feature tabs (frontend only)
- ✅ Basic Pinecone operations (query, upsert, delete, fetch)

---

**Status:** ✅ Production Ready  
**Next Steps:** UI integration, testing with real users, performance optimization
