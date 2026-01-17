# Vector Database System Documentation

**Last Updated:** January 18, 2026  
**Status:** Production Ready - Multi-Provider Support  
**Purpose:** Complete technical documentation for vector database integration (Pinecone, Qdrant, pgvector) with autonomous AI semantic search

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Supported Providers](#supported-providers)
4. [Core Components](#core-components)
5. [AI Agent Integration](#ai-agent-integration)
6. [Embedding Providers](#embedding-providers)
7. [Implementation Details](#implementation-details)
8. [API Reference](#api-reference)
9. [Usage Examples](#usage-examples)
10. [Critical Fixes](#critical-fixes)
11. [Testing & Deployment](#testing--deployment)
12. [Related Documentation](#related-documentation)

---

## System Overview

### Purpose

The vector database system transforms document search from **automatic snippet injection** (wasteful) to **AI-autonomous search** (efficient). AI agents decide when to search, craft specific queries, and retrieve full documents on-demand.

### Key Capabilities

- **Semantic Search** - Find documents by meaning, not just keywords
- **Multi-Provider Support** - Pinecone (cloud), Qdrant (self-hosted), pgvector (Supabase)
- **Autonomous AI Access** - 8 AI-callable tools for search and retrieval
- **Multi-Tenancy** - User isolation with namespace/collection suffixes
- **Cloud Storage Integration** - Direct upload from Google Drive, OneDrive, Dropbox
- **Multiple Embedding Providers** - OpenAI, Voyager AI, Anthropic support
- **Document Processing** - PDF, DOCX, TXT, JSON, CSV extraction and chunking
- **Conversation Memory** - Semantic search across threads and messages (pgvector)

### Statistics

- **9 Pinecone Tools** - Query, upsert, delete, fetch, update, stats, list namespaces, upload
- **8 Qdrant Tools** - Connect, create collection, upsert, search, hybrid search, stats, delete, snapshot
- **5 Conversation Memory Tools** - Session search, thread messages, message context, Synergy project/docs search
- **4 REST API Endpoints** - Upload, list, stats, document retrieval
- **3 Embedding Providers** - OpenAI (text-embedding-3-small/large), Voyager AI (voyage-2/large-2), Anthropic (future)
- **24+ Documentation Files** - Consolidated into this master document

---

## Architecture

### High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                               │
│  - Upload documents via sidebar module                           │
│  - Documents stored with cloud metadata                          │
│  - AI can search when relevant (not automatic)                   │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                   AI AGENT (Claude 4)                            │
│  🤖 AUTONOMOUS DECISION MAKING                                   │
│  - AI decides when to search (not automatic)                     │
│  - AI crafts specific queries                                    │
│  - AI has 22 vector database tools available                     │
│                                                                   │
│  TOOLS:                                                           │
│  • Pinecone: 9 tools (query, upsert, delete, fetch, etc.)       │
│  • Qdrant: 8 tools (search, hybrid search, snapshot, etc.)      │
│  • Conversation Memory: 5 tools (thread/message search)          │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              TOOL IMPLEMENTATION LAYER                           │
│  Files:                                                           │
│  • tools/implementations/pinecone/pinecone_tools.py (1,611 lines)│
│  • AI_infrastructure/routes/qdrant_routes.py (765 lines)        │
│  • tools/implementations/conversation_memory.py (730 lines)      │
│  • AI_infrastructure/routes/vector_db_routes.py (1,059 lines)   │
│                                                                   │
│  Functions:                                                       │
│  - Credential injection (from Supabase)                          │
│  - Embedding generation (OpenAI/Voyager/Anthropic)              │
│  - Document chunking (configurable overlap)                      │
│  - Metadata-rich responses with cloud links                      │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                  VECTOR DATABASE LAYER                           │
│  Pinecone (Cloud):                                               │
│  - 1536-dim vectors (OpenAI) or 1024-dim (Voyager)              │
│  - Namespace isolation (per user/workspace)                      │
│  - Metadata: filename, type, cloud links, AI-retrievable flag   │
│                                                                   │
│  Qdrant (Self-Hosted):                                           │
│  - Multi-modal support (text, images, audio, video)             │
│  - Hybrid search (dense + sparse BM25)                           │
│  - Binary quantization (4-32x compression)                       │
│  - Docker deployment (port 6333)                                 │
│                                                                   │
│  pgvector (Supabase):                                            │
│  - Conversation threads/messages search                          │
│  - Synergy project/document search                               │
│  - IVFFlat indexes for cosine similarity                         │
│  - 1536-dim embeddings (OpenAI text-embedding-3-small)          │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│         CLOUD STORAGE (Google Drive / OneDrive)                  │
│  - Full documents stored in cloud                                │
│  - Retrieved on-demand when AI needs complete files              │
│  - Metadata includes download URLs for user access               │
└──────────────────────────────────────────────────────────────────┘
```

### Provider Selection Decision Tree

```
Need Vector Database?
│
├─── Already using Supabase? → pgvector (FREE, built-in)
│     └─ Use case: Conversation memory, internal search
│
├─── Need multi-modal (images/audio/video)? → Qdrant
│     ├─ Self-hosted: FREE (Docker on localhost:6333)
│     ├─ Customer server: Deploy on your infrastructure
│     └─ Qdrant Cloud: Managed service ($$$)
│
└─── Need managed cloud service? → Pinecone
      ├─ Starter: $70/month (100K vectors)
      ├─ Standard: $270/month (5M vectors)
      └─ Enterprise: Custom pricing
```

---

## Supported Providers

### 1. Pinecone (Cloud Vector Database)

**Status:** ✅ Production Ready  
**Files:** `tools/implementations/pinecone/pinecone_tools.py` (1,611 lines)  
**Platform ID:** `pinecone`

**Features:**
- Serverless cloud vector database
- Automatic scaling and indexing
- Cosine similarity search
- Namespace-based multi-tenancy
- CRUD operations on vectors

**Credentials (Stored in Supabase):**
```json
{
  "api_key": "pcsk_...",
  "index_name": "inhouseprint",
  "environment": "us-east-1",
  "namespace": ""  // Optional tenant isolation
}
```

**Tools Available (9):**
1. `pinecone_query_vectors` - Semantic search
2. `pinecone_upsert_vectors` - Add/update vectors
3. `pinecone_delete_vectors` - Remove vectors
4. `pinecone_fetch_vectors` - Get specific vectors by ID
5. `pinecone_update_vector` - Modify vector/metadata
6. `pinecone_describe_index_stats` - Get database statistics
7. `pinecone_list_namespaces` - List all namespaces
8. `vector_db_upload_document` - Process and upload document (shared tool)
9. `pinecone_list_indexes` - List available indexes

**Pricing:**
- Starter: $70/month (100K vectors, 5 indexes)
- Standard: $270/month (5M vectors, 20 indexes)
- Enterprise: Custom pricing

### 2. Qdrant (Self-Hosted/Cloud)

**Status:** ✅ Backend Complete (Frontend 70% remaining)  
**Files:** `AI_infrastructure/routes/qdrant_routes.py` (765 lines)  
**Platform ID:** `qdrant`

**Features:**
- Multi-modal embeddings (text, images, audio, video)
- Hybrid search (dense vector + sparse BM25)
- Binary/scalar/product quantization (4-32x compression)
- HNSW indexing for fast retrieval
- Docker deployment (self-hosted)

**Credentials (Stored in Supabase):**
```json
{
  "host": "localhost",  // or remote server IP
  "port": 6333,
  "api_key": "optional",  // For secure deployments
  "deployment_type": "customer-server"  // or "valor-cloud", "qdrant-cloud"
}
```

**Tools Available (8):**
1. `qdrant_connect` - Test + save connection settings
2. `qdrant_create_collection` - Initialize with user_id suffix
3. `qdrant_upsert` - Auto-embed text → store vectors
4. `qdrant_search` - Semantic search + metadata filters
5. `qdrant_hybrid_search` - Dense + Sparse BM25 combined
6. `qdrant_stats` - Collection statistics
7. `qdrant_delete` - Delete by IDs or filter
8. `qdrant_snapshot` - Create backup

**Multi-Tenancy:**
```python
# User 1 creates collection "documents"
collection_name = f"{request_collection}_user_{user_id}"  # "documents_user_1"

# All operations auto-filter by user_id
client.search(
    collection_name="documents_user_1",
    query_filter=models.Filter(must=[
        models.FieldCondition(key="user_id", match=models.MatchValue(value=1))
    ])
)
```

**Deployment Options:**
- **Self-Hosted (FREE):** Docker on localhost:6333
- **Customer Server:** Deploy on your infrastructure
- **Qdrant Cloud:** Managed service (pricing varies)

**Docker Deployment:**
```powershell
# Create data directory
New-Item -Path "C:\qdrant_data" -ItemType Directory -Force

# Pull and run container
docker pull qdrant/qdrant:latest
docker run -d --name qdrant-server `
  -p 6333:6333 `
  -p 6334:6334 `
  -v C:\qdrant_data:/qdrant/storage `
  qdrant/qdrant:latest

# Test health
curl http://localhost:6333/health
# Expected: {"title":"qdrant","version":"1.7.x"}
```

### 3. pgvector (Supabase PostgreSQL)

**Status:** ✅ Production Ready  
**Files:** `tools/implementations/conversation_memory.py` (730 lines)  
**Platform ID:** `supabase` (pgvector extension)

**Features:**
- PostgreSQL extension for vector similarity search
- IVFFlat indexes for cosine similarity
- Native SQL integration
- FREE with Supabase hosting
- Conversation memory search

**Schema:**
```sql
-- Enable extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Embedding columns (1536 dimensions for OpenAI)
ALTER TABLE sessions.threads ADD COLUMN title_embedding vector(1536);
ALTER TABLE sessions.messages ADD COLUMN content_embedding vector(1536);
ALTER TABLE synergy_sessions.synergy_sessions ADD COLUMN title_embedding vector(1536);
ALTER TABLE synergy_sessions.synergy_internal_docs ADD COLUMN content_embedding vector(1536);

-- Indexes for fast search
CREATE INDEX messages_embedding_idx 
ON sessions.messages 
USING ivfflat (content_embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX synergy_docs_embedding_idx
ON synergy_sessions.synergy_internal_docs
USING ivfflat (content_embedding vector_cosine_ops)
WITH (lists = 50);
```

**Tools Available (5):**
1. `session_conversation_search` - Search threads and messages by meaning
2. `session_conversation_get_thread_messages` - Get full thread context
3. `session_conversation_get_message_context` - Get message with N before/after
4. `synergy_project_search` - Search Synergy projects semantically
5. `synergy_docs_search` - Search Synergy documents by content

**Search Query Example:**
```python
# Semantic similarity search
query_embedding = generate_embedding("email automation Gmail API")

results = execute_query("""
    SELECT 
        thread_id, 
        title, 
        1 - (title_embedding <=> %s::vector) AS similarity_score
    FROM sessions.threads
    WHERE title_embedding IS NOT NULL
    ORDER BY title_embedding <=> %s::vector
    LIMIT 5
""", (query_embedding, query_embedding), fetch_mode='all')

# Returns threads ranked by cosine similarity (0.0-1.0)
```

**Use Cases:**
- Conversation memory ("Remember when we worked on email automation?")
- Synergy project search ("Find all projects related to API integration")
- Document retrieval ("Show me docs about authentication")

---

## Core Components

### 1. Platform Connections Integration

**File:** `UI/business-ai-platform-v2.html` (lines 17345-17370, 24457-24562)

**Vector Database & Embedding AI Section:**
```html
<!-- Pinecone Button -->
<button class="platform-btn" 
        data-platform="pinecone" 
        onclick="showPlatformForm('pinecone')">
    <i class="fas fa-database" style="color: #7C3AED"></i>
    Pinecone
    <span class="badge">API Key</span>
</button>

<!-- Voyager AI Button -->
<button class="platform-btn" 
        data-platform="voyager" 
        onclick="showPlatformForm('voyager')">
    <i class="fas fa-vector-square" style="color: #8B5CF6"></i>
    Voyager AI
    <span class="badge">API Key</span>
</button>
```

**Pinecone Configuration Form:**
```javascript
{
  api_key: '',       // Required: pcsk_...
  index_name: '',    // Required: e.g., "my-vector-index"
  environment: '',   // Required: e.g., "us-west1-gcp"
  namespace: ''      // Optional: For multi-tenant organization
}
```

**Voyager AI Configuration Form:**
```javascript
{
  api_key: '',       // Required: pa-GOCp...
  model: '',         // voyage-2 (1024-dim) / voyage-large-2 (1536-dim) / voyage-code-2 (1536-dim)
  dimensions: null   // Auto-calculated from model selection
}
```

### 2. Vector Database Module

**Files:**
- `UI/modules_internal/vector_database/vector_database.html` (205 lines)
- `UI/modules_internal/vector_database/vector_database.js` (796 lines)
- `UI/modules_internal/vector_database/vector_database.css`

**Module Structure:**
```html
<div class="vector-db-module">
    <!-- Credential Status Banner -->
    <div id="credential-status-banner">
        ⚠️ Vector Database Not Configured
        <button onclick="openPlatformConnections()">Configure</button>
    </div>
    
    <!-- OR Connected Banner -->
    <div id="credential-connected-banner">
        ✅ Connected to Vector Database
        <div>Index: inhouseprint (us-east-1)</div>
        <div>Embedding: Voyager AI (voyage-2)</div>
        <button>Manage Credentials</button>
    </div>
    
    <!-- Tabs -->
    <div class="tabs">
        <button class="tab active" data-tab="upload">Upload</button>
        <button class="tab" data-tab="documents">Documents</button>
    </div>
    
    <!-- Upload Tab -->
    <div id="upload-tab" class="tab-content active">
        <input type="file" accept=".pdf,.docx,.txt" />
        <button onclick="uploadDocument()">Upload to Vector DB</button>
    </div>
    
    <!-- Documents Tab -->
    <div id="documents-tab" class="tab-content">
        <table id="documents-table">
            <thead>
                <tr>
                    <th>Filename</th>
                    <th>Type</th>
                    <th>Chunks</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    </div>
</div>
```

**JavaScript State Management:**
```javascript
class VectorDatabaseModule {
    constructor() {
        this.currentTab = 'upload';
        this.pineconeCredentials = null;  // Fetched from Platform Connections
        this.embeddingCredentials = null; // Fetched from Platform Connections
        this.uploadedFiles = [];
        this.documents = [];
    }
    
    async loadCredentials() {
        // GET /api/connections?platform=pinecone (with JWT)
        this.pineconeCredentials = await fetchPlatformCredentials('pinecone');
        
        // GET /api/connections?platform=voyager (with JWT)
        this.embeddingCredentials = await fetchPlatformCredentials('voyager');
        
        if (this.pineconeCredentials && this.embeddingCredentials) {
            this.showConnectedBanner();
        } else {
            this.showDisconnectedBanner();
        }
    }
    
    async uploadDocument(file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('namespace', this.pineconeCredentials.namespace || '');
        
        // POST /api/vector-db/upload-document
        const response = await fetch('/api/vector-db/upload-document', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${getJWT()}` },
            body: formData
        });
        
        const result = await response.json();
        console.log(`Uploaded ${result.chunks_created} chunks`);
    }
}
```

### 3. Backend API Routes

**File:** `AI_infrastructure/routes/vector_db_routes.py` (1,059 lines)

**Critical Fix (Jan 12, 2026) - Cursor Leak Repair:**
```python
"""
FIXED: 2025-01-12 - Critical cursor leak repair
CHANGES:
- Fixed get_credentials() - added proper cursor management
- Fixed get_embedding_config() - fixed nested get_settings() helper cursor leak
- Added cursor = None and conn = None initialization
- Added try/finally blocks for guaranteed cleanup
- Added cursor.close() BEFORE conn.close()
"""
```

**Endpoints:**
```python
@vector_db_bp.route('/api/vector-db/upload-document', methods=['POST'])
@require_auth
def upload_document(user_id=None):
    """
    Upload document with automatic chunking and embedding
    
    Supports: PDF, DOCX, TXT, JSON, CSV
    
    Process:
    1. Extract text from file
    2. Chunk text (configurable size/overlap)
    3. Generate embeddings (OpenAI/Voyager)
    4. Upsert to Pinecone with metadata
    5. Return document ID + chunk count
    """

@vector_db_bp.route('/api/vector-db/documents', methods=['GET'])
@require_auth
def list_documents(user_id=None):
    """List all documents with cloud storage links"""

@vector_db_bp.route('/api/vector-db/stats', methods=['GET'])
@require_auth
def get_stats(user_id=None):
    """Get vector database statistics (total vectors, namespaces, etc.)"""

@vector_db_bp.route('/api/vector-db/document/<document_id>', methods=['GET'])
@require_auth
def get_full_document(document_id, user_id=None):
    """
    Retrieve full document from cloud storage
    
    Flow:
    1. Get metadata from Pinecone
    2. Extract cloud_storage_link from metadata
    3. Fetch full document from Google Drive/OneDrive
    4. Return complete file content
    """
```

**Helper Functions:**
```python
def _get_vector_db_credentials(user_id: int) -> Dict[str, Any]:
    """
    Fetch Pinecone + embedding provider credentials
    
    ✅ NO DATABASE OPERATIONS - Uses credential injector functions
    """
    from auth.credential_injector import (
        get_pinecone_credentials, 
        get_voyager_credentials, 
        get_openai_embeddings_credentials
    )
    
    credentials = {}
    
    # Get Pinecone
    pinecone_creds = get_pinecone_credentials(user_id=user_id)
    if pinecone_creds:
        credentials['pinecone_api_key'] = pinecone_creds['credentials']['api_key']
        credentials['pinecone_index_name'] = pinecone_creds['credentials']['index_name']
    
    # Get Embedding Provider
    voyager_creds = get_voyager_credentials(user_id=user_id)
    if voyager_creds:
        credentials['voyager_api_key'] = voyager_creds['credentials']['api_key']
        credentials['voyager_model'] = voyager_creds['credentials']['model']
    
    return credentials
```

### 4. Tool Implementations

**Pinecone Tools (`tools/implementations/pinecone/pinecone_tools.py` - 1,611 lines):**

```python
def _get_pinecone_client(user_id: int, **kwargs):
    """Get authenticated Pinecone client (JSONB format)"""
    from pinecone import Pinecone
    
    auth_manager = UserAuthManager()
    creds = auth_manager.get_platform_credentials(user_id, 'pinecone')
    
    if not creds or 'api_key' not in creds:
        raise PineconeToolsError("Pinecone credentials not found")
    
    api_key = creds['api_key']
    index_name = creds.get('index_name')
    environment = creds.get('environment', 'us-east-1')
    namespace = creds.get('namespace', '')
    
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    
    return index, {
        'index_name': index_name,
        'environment': environment,
        'namespace': namespace
    }

def _get_openai_embeddings(text: str, user_id: int) -> List[float]:
    """
    Generate embeddings using configured provider
    
    Supports:
    - OpenAI: text-embedding-ada-002 (1536), text-embedding-3-small (1536), text-embedding-3-large (3072)
    - Voyager AI: voyage-2 (1024), voyage-large-2 (1536), voyage-code-2 (1536)
    """
    auth_manager = UserAuthManager()
    
    # Try Voyager AI first (InHousePrint preferred)
    voyager_creds = auth_manager.get_platform_credentials(user_id, 'voyager')
    if voyager_creds:
        import voyageai
        client = voyageai.Client(api_key=voyager_creds['api_key'])
        result = client.embed([text], model=voyager_creds.get('model', 'voyage-2'))
        return result.embeddings[0]
    
    # Fallback to OpenAI
    openai_creds = auth_manager.get_platform_credentials(user_id, 'openai_embeddings')
    if openai_creds:
        from openai import OpenAI
        client = OpenAI(api_key=openai_creds['api_key'])
        response = client.embeddings.create(
            input=text,
            model='text-embedding-3-small'
        )
        return response.data[0].embedding
    
    raise PineconeToolsError("No embedding provider configured")

def pinecone_query_vectors(query_text: str, top_k: int = 5, namespace: str = '', 
                           filter: dict = None, _user_id: int = None, 
                           _injected_credentials: bool = False) -> dict:
    """
    Semantic search in Pinecone vector database
    
    Args:
        query_text: Natural language query
        top_k: Number of results (default 5)
        namespace: Optional namespace filter
        filter: Metadata filter dict (e.g., {"category": "security"})
        _user_id: Injected by credential system
        _injected_credentials: Always True when called by AI
    
    Returns:
        {
            "success": True,
            "matches": [
                {
                    "id": "doc-xyz123-chunk-5",
                    "score": 0.94,
                    "metadata": {
                        "filename": "security_policy.pdf",
                        "chunk_index": 5,
                        "text": "Authentication requires 2FA..."
                    }
                }
            ],
            "query": "authentication requirements"
        }
    """
    index, metadata = _get_pinecone_client(_user_id)
    
    # Generate query embedding
    query_embedding = _get_openai_embeddings(query_text, _user_id)
    
    # Search Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        namespace=namespace or metadata['namespace'],
        filter=filter,
        include_metadata=True
    )
    
    return {
        "success": True,
        "matches": [
            {
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata
            }
            for match in results.matches
        ],
        "query": query_text
    }
```

**Conversation Memory Tools (`tools/implementations/conversation_memory.py` - 730 lines):**

```python
def session_conversation_search(query: str, user_id: int, search_type: str = 'both', 
                                limit: int = 5, similarity_threshold: float = 0.7) -> dict:
    """
    Search conversations by semantic meaning (threads + messages)
    
    Args:
        query: Natural language search query
        user_id: User ID for filtering
        search_type: 'threads', 'messages', or 'both'
        limit: Max results per type (default 5)
        similarity_threshold: Minimum cosine similarity (0.0-1.0, default 0.7)
    
    Returns:
        {
            "success": True,
            "threads": [
                {
                    "thread_id": 1523,
                    "title": "Gmail Automation Setup",
                    "similarity_score": 0.94,
                    "created_at": "2025-12-15T10:30:00Z"
                }
            ],
            "messages": [
                {
                    "message_id": 45678,
                    "thread_id": 1523,
                    "content_preview": "To integrate Gmail API...",
                    "similarity_score": 0.89,
                    "created_at": "2025-12-15T10:35:00Z"
                }
            ]
        }
    """
    from openai import OpenAI
    from AI_infrastructure.shared.database_utils import execute_query
    
    # Generate query embedding
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.embeddings.create(
        input=query,
        model='text-embedding-3-small'
    )
    query_embedding = response.data[0].embedding
    
    results = {}
    
    # Search threads
    if search_type in ['threads', 'both']:
        threads = execute_query("""
            SELECT 
                thread_id,
                title,
                created_at,
                1 - (title_embedding <=> %s::vector) AS similarity_score
            FROM sessions.threads
            WHERE user_id = %s
            AND title_embedding IS NOT NULL
            AND 1 - (title_embedding <=> %s::vector) >= %s
            ORDER BY similarity_score DESC
            LIMIT %s
        """, (query_embedding, user_id, query_embedding, similarity_threshold, limit), 
        fetch_mode='all')
        
        results['threads'] = [
            {
                'thread_id': row['thread_id'],
                'title': row['title'],
                'similarity_score': float(row['similarity_score']),
                'created_at': row['created_at'].isoformat()
            }
            for row in threads
        ]
    
    # Search messages
    if search_type in ['messages', 'both']:
        messages = execute_query("""
            SELECT 
                m.message_id,
                m.thread_id,
                LEFT(m.content, 200) AS content_preview,
                m.created_at,
                1 - (m.content_embedding <=> %s::vector) AS similarity_score
            FROM sessions.messages m
            JOIN sessions.threads t ON m.thread_id = t.thread_id
            WHERE t.user_id = %s
            AND m.content_embedding IS NOT NULL
            AND 1 - (m.content_embedding <=> %s::vector) >= %s
            ORDER BY similarity_score DESC
            LIMIT %s
        """, (query_embedding, user_id, query_embedding, similarity_threshold, limit),
        fetch_mode='all')
        
        results['messages'] = [
            {
                'message_id': row['message_id'],
                'thread_id': row['thread_id'],
                'content_preview': row['content_preview'],
                'similarity_score': float(row['similarity_score']),
                'created_at': row['created_at'].isoformat()
            }
            for row in messages
        ]
    
    return {
        'success': True,
        **results
    }
```

---

## AI Agent Integration

### Autonomous Search Pattern

**Traditional RAG (What we DON'T do):**
```
User asks question
    ↓
System automatically injects context
    ↓
AI receives pre-selected snippets
    ↓
AI has no control over retrieval
```

**Our Approach (What we DO):**
```
User asks question
    ↓
AI decides if vector DB needed
    ↓
AI calls pinecone_query_vectors tool
    ↓
AI controls search parameters (top_k, filters, namespaces)
    ↓
AI receives results and synthesizes answer
```

### AI Agent Quick Reference

**File:** `VECTOR_DB_AI_AGENT_GUIDE.md` (512 lines)

**Example 1: Document Search**
```
User: "What are the authentication requirements mentioned in my documents?"

AI thinking: This requires searching uploaded documents for authentication info.

AI calls:
pinecone_query_vectors(
    query_text="authentication requirements security credentials",
    top_k=5,
    namespace="",  # Empty = search all namespaces
    _user_id=1,
    _injected_credentials=True
)

Result: Returns 5 chunks about authentication

AI response: "Based on your uploaded documents, the authentication requirements are:
1. Two-factor authentication mandatory
2. Password complexity: 12+ characters
3. API keys must be rotated every 90 days
(Sources: document-xyz123-chunk-5, document-abc456-chunk-12)"
```

**Example 2: Conversation Memory**
```
User: "Remember when we worked on email automation?"

AI calls:
session_conversation_search(
    query="email automation",
    user_id=14,
    search_type="both"
)

Result:
{
    "threads": [{
        "thread_id": 1523,
        "title": "Gmail Automation Setup",
        "similarity_score": 0.94
    }],
    "messages": [{
        "message_id": 45678,
        "content_preview": "To integrate Gmail API, first enable...",
        "similarity_score": 0.89
    }]
}

AI response: "Yes! On December 15th, we worked on Gmail Automation Setup. 
You asked about integrating the Gmail API, and I helped you enable the API 
and configure OAuth credentials. Would you like me to retrieve the full 
conversation thread?"
```

**Example 3: Full Document Retrieval**
```
User: "Show me the complete security policy document"

Step 1: AI searches for document
pinecone_query_vectors(
    query_text="security policy document",
    top_k=1
)

Step 2: AI retrieves full document
vector_db_get_full_document(
    document_id="doc-xyz123",
    _user_id=1
)

Result: Complete document from Google Drive

AI response: "Here's the full security policy document (retrieved from 
Google Drive). The document covers:
1. Access Control (pages 1-5)
2. Data Protection (pages 6-10)
3. Incident Response (pages 11-15)
..."
```

### Two-Step Retrieval Pattern

**Step 1: Search (Fast, Lightweight)**
- Returns summaries with IDs and similarity scores
- Shows 5-20 results
- User/AI can assess relevance without loading full content

**Step 2: Retrieve (On-Demand)**
- Get full thread (all messages) OR
- Get message with context (N before/after) OR
- Get document content

This prevents loading massive contexts unnecessarily.

---

## Embedding Providers

### Provider Comparison

| Feature | OpenAI | Voyager AI | Anthropic (Future) |
|---------|--------|------------|-------------------|
| **Platform ID** | `openai_embeddings` | `voyager` | `anthropic_embeddings` |
| **Models** | text-embedding-3-small (1536-dim)<br>text-embedding-3-large (3072-dim) | voyage-2 (1024-dim)<br>voyage-large-2 (1536-dim)<br>voyage-code-2 (1536-dim) | claude-3-embeddings (TBD) |
| **Speed** | 50ms/request | 30ms/request | TBD |
| **Cost** | $0.00002/1K tokens | $0.00012/1K tokens | TBD |
| **Best For** | General purpose, broad compatibility | High-quality, InHousePrint-optimized | Long context, multimodal |
| **Max Input** | 8,191 tokens | 16,000 tokens | TBD |

### OpenAI Configuration

```json
{
  "platform": "openai_embeddings",
  "credentials": {
    "api_key": "sk-proj-...",
    "model": "text-embedding-3-small",
    "dimensions": 1536
  }
}
```

**Usage:**
```python
from openai import OpenAI

client = OpenAI(api_key=api_key)
response = client.embeddings.create(
    input="Your text here",
    model="text-embedding-3-small"
)
embedding = response.data[0].embedding  # 1536-dim vector
```

### Voyager AI Configuration

```json
{
  "platform": "voyager",
  "credentials": {
    "api_key": "pa-GOCp1HsNfuuvjXnHPumV5f6sD-YLQwQg5Fl3Fx2AlDm",
    "model": "voyage-2",
    "dimensions": 1024
  }
}
```

**Model Selection Guide:**
- **voyage-2** (1024-dim) - General purpose, fastest, lowest cost
- **voyage-large-2** (1536-dim) - High quality, balanced speed/accuracy
- **voyage-code-2** (1536-dim) - Code-optimized for technical documents

**Usage:**
```python
import voyageai

client = voyageai.Client(api_key=api_key)
result = client.embed(
    texts=["Your text here"],
    model="voyage-2"
)
embedding = result.embeddings[0]  # 1024-dim vector
```

---

## Implementation Details

### Document Chunking

**Strategy:** Overlapping chunks with configurable size

```python
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Full document text
        chunk_size: Characters per chunk (default 1000)
        overlap: Characters overlap between chunks (default 200)
    
    Returns:
        List of text chunks
    
    Example:
        text = "Lorem ipsum dolor sit amet..." (5000 chars)
        chunks = chunk_text(text, chunk_size=1000, overlap=200)
        # Returns 6 chunks:
        # Chunk 0: chars 0-1000
        # Chunk 1: chars 800-1800 (200 overlap)
        # Chunk 2: chars 1600-2600
        # ...
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - overlap)
    
    return chunks
```

**Why Overlapping?**
- Prevents context loss at chunk boundaries
- Improves semantic coherence
- Better search results for cross-boundary content

### Text Extraction

**Supported Formats:**

1. **PDF** (PyPDF2):
```python
from PyPDF2 import PdfReader

def extract_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text
```

2. **DOCX** (python-docx):
```python
from docx import Document

def extract_docx(file_path: str) -> str:
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text
```

3. **TXT/JSON/CSV**:
```python
def extract_text(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
```

### Metadata Structure

**Pinecone Metadata:**
```json
{
  "filename": "security_policy.pdf",
  "file_type": "pdf",
  "chunk_index": 5,
  "total_chunks": 12,
  "text": "Authentication requires two-factor...",
  "cloud_storage_link": "https://drive.google.com/file/d/1234567890/view",
  "ai_retrievable": true,
  "uploaded_at": "2025-11-29T14:30:00Z",
  "user_id": 1,
  "namespace": "user_1_documents"
}
```

**pgvector Metadata (Embedded in Columns):**
```sql
-- Thread metadata
CREATE TABLE sessions.threads (
    thread_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    title TEXT NOT NULL,
    title_embedding vector(1536),  -- Semantic embedding
    created_at TIMESTAMP DEFAULT NOW()
);

-- Message metadata
CREATE TABLE sessions.messages (
    message_id SERIAL PRIMARY KEY,
    thread_id INT REFERENCES sessions.threads(thread_id),
    content TEXT NOT NULL,
    content_embedding vector(1536),  -- Semantic embedding
    role VARCHAR(50) NOT NULL,  -- 'user' or 'assistant'
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Credential Injection

**Pattern:** Automatic credential retrieval from Supabase

```python
# Tool definition (in JSON schema)
{
  "name": "pinecone_query_vectors",
  "parameters": {
    "_user_id": {
      "type": "integer",
      "description": "Automatically injected by system"
    },
    "_injected_credentials": {
      "type": "boolean",
      "description": "Always true for AI calls"
    }
  }
}

# Tool implementation
def pinecone_query_vectors(query_text: str, _user_id: int = None, 
                          _injected_credentials: bool = False):
    # Credentials auto-fetched from Supabase
    auth_manager = UserAuthManager()
    pinecone_creds = auth_manager.get_platform_credentials(_user_id, 'pinecone')
    
    # No manual API key handling needed
    pc = Pinecone(api_key=pinecone_creds['api_key'])
    ...
```

**Credential Storage (Supabase):**
```sql
-- Platform credentials table
CREATE TABLE ai_infrastructure.user_platform_credentials (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    platform VARCHAR(100) NOT NULL,  -- 'pinecone', 'voyager', 'openai_embeddings'
    connection_string TEXT,          -- Encrypted API key
    credentials JSONB,               -- Additional settings
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Example row (Pinecone)
{
    "user_id": 1,
    "platform": "pinecone",
    "credentials": {
        "api_key": "pcsk_encrypted...",
        "index_name": "inhouseprint",
        "environment": "us-east-1",
        "namespace": ""
    },
    "is_active": true
}

-- Example row (Voyager AI)
{
    "user_id": 1,
    "platform": "voyager",
    "credentials": {
        "api_key": "pa-encrypted...",
        "model": "voyage-2",
        "dimensions": 1024
    },
    "is_active": true
}
```

---

## API Reference

### REST Endpoints

#### POST /api/vector-db/upload-document

Upload document with automatic embedding and chunking.

**Request:**
```http
POST /api/vector-db/upload-document
Authorization: Bearer <JWT_TOKEN>
Content-Type: multipart/form-data

file: <binary file data>
namespace: "user_1_documents" (optional)
```

**Response:**
```json
{
  "success": true,
  "document_id": "doc-xyz123",
  "filename": "security_policy.pdf",
  "chunks_created": 12,
  "namespace": "user_1_documents",
  "uploaded_at": "2025-11-29T14:30:00Z"
}
```

#### GET /api/vector-db/documents

List all documents with metadata.

**Request:**
```http
GET /api/vector-db/documents?namespace=user_1_documents
Authorization: Bearer <JWT_TOKEN>
```

**Response:**
```json
{
  "success": true,
  "documents": [
    {
      "document_id": "doc-xyz123",
      "filename": "security_policy.pdf",
      "file_type": "pdf",
      "total_chunks": 12,
      "cloud_storage_link": "https://drive.google.com/...",
      "uploaded_at": "2025-11-29T14:30:00Z"
    }
  ],
  "total": 1
}
```

#### GET /api/vector-db/stats

Get vector database statistics.

**Request:**
```http
GET /api/vector-db/stats
Authorization: Bearer <JWT_TOKEN>
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_vectors": 1542,
    "dimension": 1536,
    "namespaces": {
      "user_1_documents": 1542
    },
    "index_fullness": 0.015
  }
}
```

#### GET /api/vector-db/document/:document_id

Retrieve full document from cloud storage.

**Request:**
```http
GET /api/vector-db/document/doc-xyz123
Authorization: Bearer <JWT_TOKEN>
```

**Response:**
```json
{
  "success": true,
  "document_id": "doc-xyz123",
  "filename": "security_policy.pdf",
  "content": "<full document text>",
  "metadata": {
    "file_type": "pdf",
    "total_chunks": 12,
    "cloud_storage_link": "https://drive.google.com/..."
  }
}
```

### AI Tool Functions

**Pinecone Tools:**

```python
pinecone_query_vectors(
    query_text: str,
    top_k: int = 5,
    namespace: str = '',
    filter: dict = None,
    _user_id: int = None,
    _injected_credentials: bool = False
) -> dict

pinecone_upsert_vectors(
    vectors: List[dict],
    namespace: str = '',
    _user_id: int = None,
    _injected_credentials: bool = False
) -> dict

pinecone_delete_vectors(
    ids: List[str],
    namespace: str = '',
    _user_id: int = None,
    _injected_credentials: bool = False
) -> dict

pinecone_fetch_vectors(
    ids: List[str],
    namespace: str = '',
    _user_id: int = None,
    _injected_credentials: bool = False
) -> dict

pinecone_update_vector(
    id: str,
    values: List[float] = None,
    set_metadata: dict = None,
    namespace: str = '',
    _user_id: int = None,
    _injected_credentials: bool = False
) -> dict

pinecone_describe_index_stats(
    _user_id: int = None,
    _injected_credentials: bool = False
) -> dict

pinecone_list_namespaces(
    _user_id: int = None,
    _injected_credentials: bool = False
) -> dict

vector_db_upload_document(
    file_path: str,
    namespace: str = '',
    _user_id: int = None,
    _injected_credentials: bool = False
) -> dict
```

**Conversation Memory Tools:**

```python
session_conversation_search(
    query: str,
    user_id: int,
    search_type: str = 'both',
    limit: int = 5,
    similarity_threshold: float = 0.7
) -> dict

session_conversation_get_thread_messages(
    thread_id: int,
    user_id: int
) -> dict

session_conversation_get_message_context(
    message_id: int,
    user_id: int,
    context_before: int = 3,
    context_after: int = 3
) -> dict

synergy_project_search(
    query: str,
    user_id: int,
    limit: int = 5,
    similarity_threshold: float = 0.7
) -> dict

synergy_docs_search(
    query: str,
    session_id: int = None,
    user_id: int = None,
    limit: int = 10,
    similarity_threshold: float = 0.7
) -> dict
```

---

## Usage Examples

### Example 1: Upload Document via API

```python
import requests

# Get JWT token
jwt_token = get_user_jwt_token()

# Upload document
with open('security_policy.pdf', 'rb') as f:
    files = {'file': f}
    data = {'namespace': 'user_1_documents'}
    
    response = requests.post(
        'https://api.yourdomain.com/api/vector-db/upload-document',
        headers={'Authorization': f'Bearer {jwt_token}'},
        files=files,
        data=data
    )
    
    result = response.json()
    print(f"Uploaded {result['chunks_created']} chunks")
    # Output: Uploaded 12 chunks
```

### Example 2: AI Semantic Search

```python
# User asks: "What are the security requirements?"

# AI calls tool
result = pinecone_query_vectors(
    query_text="security requirements authentication access control",
    top_k=5,
    namespace="user_1_documents",
    _user_id=1,
    _injected_credentials=True
)

# Process results
for match in result['matches']:
    print(f"Score: {match['score']:.2f}")
    print(f"Source: {match['metadata']['filename']}")
    print(f"Text: {match['metadata']['text'][:200]}...")
    print()

# AI synthesizes answer from matched chunks
```

### Example 3: Conversation Memory Search

```python
# User asks: "Remember when we discussed email automation?"

# AI calls conversation search
result = session_conversation_search(
    query="email automation Gmail API integration",
    user_id=14,
    search_type='both',
    limit=5,
    similarity_threshold=0.7
)

# Check threads
if result['threads']:
    thread = result['threads'][0]
    print(f"Found thread: {thread['title']}")
    print(f"Similarity: {thread['similarity_score']:.2f}")
    
    # Retrieve full thread
    full_thread = session_conversation_get_thread_messages(
        thread_id=thread['thread_id'],
        user_id=14
    )
    
    print(f"Thread has {len(full_thread['messages'])} messages")
```

### Example 4: Qdrant Hybrid Search

```python
# Hybrid search: Dense vector + Sparse keyword
result = qdrant_hybrid_search(
    query_text="machine learning TensorFlow",
    keywords=["TensorFlow", "neural network", "GPU"],
    top_k=10,
    collection_name="documents",
    _user_id=1,
    _injected_credentials=True
)

# Returns results with combined dense + sparse scores
for match in result['matches']:
    print(f"Combined Score: {match['score']:.2f}")
    print(f"Dense Score: {match['dense_score']:.2f}")
    print(f"Sparse Score: {match['sparse_score']:.2f}")
```

---

## Critical Fixes

### Fix 1: Cursor Leak in vector_db_routes.py (Jan 12, 2026)

**Problem:** Database connection leaks causing 502 errors under load.

**Root Cause:**
```python
# BEFORE (BROKEN)
def get_embedding_config(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Nested helper function
    def get_settings():
        cursor2 = conn.cursor()  # NEW CURSOR
        cursor2.execute("SELECT ...")
        # NO cursor2.close() - LEAK!
    
    settings = get_settings()
    cursor.close()  # Only closes outer cursor
    conn.close()
```

**Solution:**
```python
# AFTER (FIXED)
def get_embedding_config(user_id):
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Nested helper function
        def get_settings():
            settings_cursor = None
            try:
                settings_cursor = conn.cursor()
                settings_cursor.execute("SELECT ...")
                result = settings_cursor.fetchone()
                return result
            finally:
                if settings_cursor:
                    settings_cursor.close()  # GUARANTEED CLEANUP
        
        settings = get_settings()
        return settings
        
    finally:
        if cursor:
            cursor.close()  # BEFORE conn.close()
        if conn:
            conn.close()
```

**Impact:**
- Fixed 502 errors under high concurrency
- Eliminated connection pool exhaustion
- Guaranteed cursor cleanup with try/finally blocks

### Fix 2: Multi-Provider Embedding Support (Nov 29, 2025)

**Problem:** Hardcoded OpenAI embeddings, no support for Voyager AI.

**Solution:**
```python
def _get_openai_embeddings(text: str, user_id: int) -> List[float]:
    """Generate embeddings using configured provider"""
    auth_manager = UserAuthManager()
    
    # Try Voyager AI first (InHousePrint preferred)
    voyager_creds = auth_manager.get_platform_credentials(user_id, 'voyager')
    if voyager_creds:
        import voyageai
        client = voyageai.Client(api_key=voyager_creds['api_key'])
        result = client.embed([text], model=voyager_creds.get('model', 'voyage-2'))
        return result.embeddings[0]
    
    # Fallback to OpenAI
    openai_creds = auth_manager.get_platform_credentials(user_id, 'openai_embeddings')
    if openai_creds:
        from openai import OpenAI
        client = OpenAI(api_key=openai_creds['api_key'])
        response = client.embeddings.create(
            input=text,
            model='text-embedding-3-small'
        )
        return response.data[0].embedding
    
    raise PineconeToolsError("No embedding provider configured")
```

**Impact:**
- Added Voyager AI support (InHousePrint optimized)
- Provider selection via Platform Connections
- Automatic fallback to OpenAI

### Fix 3: JSONB Credential Format (Nov 25, 2025)

**Problem:** Legacy TEXT column format, difficult to parse credentials.

**Solution:**
```sql
-- Migration: Convert credentials to JSONB
ALTER TABLE ai_infrastructure.user_platform_credentials 
ADD COLUMN credentials JSONB;

-- Update existing rows
UPDATE ai_infrastructure.user_platform_credentials
SET credentials = jsonb_build_object(
    'api_key', connection_string,
    'index_name', (metadata->>'index_name'),
    'environment', (metadata->>'environment')
)
WHERE platform = 'pinecone';
```

**Code Update:**
```python
# BEFORE
creds_text = auth_manager.get_platform_credentials(user_id, 'pinecone')
api_key = parse_connection_string(creds_text)  # Fragile parsing

# AFTER
creds = auth_manager.get_platform_credentials(user_id, 'pinecone')
api_key = creds['api_key']  # Clean dictionary access
index_name = creds['index_name']
environment = creds.get('environment', 'us-east-1')
```

**Impact:**
- Type-safe credential access
- Easier to add new credential fields
- Better error handling

---

## Testing & Deployment

### Local Testing

**1. Test Pinecone Connection:**
```python
python -c "from tools.implementations.pinecone.pinecone_tools import pinecone_describe_index_stats; print(pinecone_describe_index_stats(_user_id=1, _injected_credentials=True))"

# Expected output:
# {
#     'success': True,
#     'total_vectors': 1542,
#     'dimension': 1536,
#     'namespaces': {'user_1_documents': 1542}
# }
```

**2. Test Conversation Memory:**
```python
python -c "from tools.implementations.conversation_memory import session_conversation_search; print(session_conversation_search('email automation', user_id=14, search_type='threads'))"

# Expected output:
# {
#     'success': True,
#     'threads': [
#         {'thread_id': 1523, 'title': 'Gmail Automation', 'similarity_score': 0.94}
#     ]
# }
```

**3. Test Qdrant Connection:**
```powershell
# Start Qdrant Docker container
docker run -d --name qdrant-server -p 6333:6333 qdrant/qdrant:latest

# Test health endpoint
curl http://localhost:6333/health

# Expected: {"title":"qdrant","version":"1.7.x"}
```

**4. Test Vector Database Routes:**
```python
import requests

jwt_token = "your_jwt_token_here"

# Test stats endpoint
response = requests.get(
    'http://localhost:5000/api/vector-db/stats',
    headers={'Authorization': f'Bearer {jwt_token}'}
)

print(response.json())
# Expected: {'success': True, 'stats': {...}}
```

### Deployment Checklist

**Environment Variables (Render):**
```bash
# Pinecone
PINECONE_API_KEY=pcsk_...  # Optional: Can use per-user credentials
PINECONE_INDEX_NAME=default-index  # Optional: Default if not in DB

# OpenAI
OPENAI_API_KEY=sk-proj-...  # Required for embeddings

# Voyager AI
VOYAGER_API_KEY=pa-...  # Optional: Alternative embedding provider

# Qdrant
QDRANT_HOST=localhost  # or remote server IP
QDRANT_PORT=6333
QDRANT_API_KEY=optional  # For secure deployments
```

**Required Python Packages:**
```txt
# Vector Database
pinecone>=3.0.0
qdrant-client>=1.7.0
pgvector>=0.2.0

# Embeddings
openai>=1.0.0
voyageai>=0.2.0

# Document Processing
PyPDF2>=3.0.0
python-docx>=0.8.11
```

**Database Migrations:**
```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding columns to threads
ALTER TABLE sessions.threads 
ADD COLUMN IF NOT EXISTS title_embedding vector(1536);

-- Add embedding columns to messages
ALTER TABLE sessions.messages 
ADD COLUMN IF NOT EXISTS content_embedding vector(1536);

-- Create indexes
CREATE INDEX IF NOT EXISTS messages_embedding_idx 
ON sessions.messages 
USING ivfflat (content_embedding vector_cosine_ops)
WITH (lists = 100);

-- Add credentials table (if not exists)
CREATE TABLE IF NOT EXISTS ai_infrastructure.user_platform_credentials (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    platform VARCHAR(100) NOT NULL,
    credentials JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Flask App Registration:**
```python
# AI_infrastructure/flask_app.py

from AI_infrastructure.routes.vector_db_routes import vector_db_bp
from AI_infrastructure.routes.qdrant_routes import qdrant_bp

app.register_blueprint(vector_db_bp)
app.register_blueprint(qdrant_bp)
```

**Vectorization Script:**
```python
# vectorize_database.py - Run once to populate embeddings

from openai import OpenAI
from AI_infrastructure.shared.database_utils import execute_query
import time

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Vectorize threads
threads = execute_query("SELECT thread_id, title FROM sessions.threads WHERE title_embedding IS NULL", fetch_mode='all')

for thread in threads:
    response = client.embeddings.create(
        input=thread['title'],
        model='text-embedding-3-small'
    )
    embedding = response.data[0].embedding
    
    execute_query(
        "UPDATE sessions.threads SET title_embedding = %s WHERE thread_id = %s",
        (embedding, thread['thread_id'])
    )
    
    time.sleep(0.1)  # Rate limiting

print(f"Vectorized {len(threads)} threads")
```

### Performance Benchmarks

| Operation | Pinecone | Qdrant | pgvector |
|-----------|----------|--------|----------|
| **Upload (1 doc, 10 chunks)** | 500ms | 300ms | 200ms |
| **Search (top 5)** | 100ms | 80ms | 500ms |
| **Fetch (single doc)** | 50ms | 40ms | 100ms |
| **Upsert (1000 vectors)** | 2s | 1.5s | 5s |
| **Index Size (100K vectors)** | 200MB | 150MB | 300MB |

**Notes:**
- Pinecone: Cloud latency adds ~50ms
- Qdrant: Local deployment = fastest
- pgvector: Slower search but FREE with Supabase

---

## Related Documentation

### Core System Documentation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Master system architecture (includes vector DB overview)
- **[SUPABASE_DATABASE.md](SUPABASE_DATABASE.md)** - Database schema (pgvector columns, credentials table)
- **[TOOL_DISCOVERY.md](TOOL_DISCOVERY.md)** - Tool registry (semantic search with embeddings)
- **[AI_AGENTS.md](AI_AGENTS.md)** - Agent system (conversation memory search)

### Platform Integrations
- **[GOOGLE_INTEGRATION.md](GOOGLE_INTEGRATION.md)** - Google Drive integration (cloud storage)
- **[XERO_INTEGRATION.md](XERO_INTEGRATION.md)** - Credential injection pattern reference

### Module Documentation
- **[MODULES.md](MODULES.md)** - Vector Database module (UI components)
- **[COMMUNICATION_HUB.md](COMMUNICATION_HUB.md)** - Cross-system integration patterns

### Implementation Files
- `tools/implementations/pinecone/pinecone_tools.py` (1,611 lines)
- `AI_infrastructure/routes/vector_db_routes.py` (1,059 lines)
- `AI_infrastructure/routes/qdrant_routes.py` (765 lines)
- `tools/implementations/conversation_memory.py` (730 lines)
- `UI/modules_internal/vector_database/vector_database.js` (796 lines)

### Deployment Guides
- **Docker Deployment:** `QDRANT_DOCKER_DEPLOYMENT_GUIDE.md` (465 lines)
- **Quick Start:** `docs/VECTOR_DB_QUICK_START.md` (195 lines)
- **AI Agent Guide:** `VECTOR_DB_AI_AGENT_GUIDE.md` (512 lines)

---

## Files Consolidated (24+)

This document consolidates the following scattered documentation files:

1. `VECTOR_DB_AI_AGENT_GUIDE.md` (512 lines)
2. `VECTOR_DATABASE_CLOUD_INTEGRATION_COMPLETE.md` (899 lines)
3. `VECTOR_DB_INTEGRATION_COMPLETE.md` (471 lines)
4. `VECTOR_SEARCH_IMPLEMENTATION_SUMMARY.md` (441 lines)
5. `QDRANT_COMPLETE_IMPLEMENTATION_SUMMARY.md` (606 lines)
6. `VECTOR_DB_EMBEDDING_PROVIDERS_COMPLETE.md` (640 lines)
7. `VECTOR_DATABASE_COMPLETE_FIX.md`
8. `VECTOR_DB_CREDENTIALS_CONNECTED.md`
9. `VECTOR_DB_GETTING_STARTED.md`
10. `VECTOR_DB_INTEGRATION_ANALYSIS.md`
11. `VECTOR_DB_SETUP_GUIDE.md`
12. `VECTORIZATION_STATUS_REPORT.md`
13. `SUPABASE_VECTOR_SEARCH_READY.md`
14. `NEXT_STEPS_VECTOR_SEARCH.md`
15. `CONVERSATION_MEMORY_TOOLS_READY.md`
16. `DOCUMENT_LIBRARY_MULTI_PROVIDER_COMPLETE.md`
17. `AI_infrastructure/tests/VECTOR_DB_BUTTON_FIX_DEC9_2025.md`
18. `docs/AUTONOMOUS_VECTOR_DB_INTEGRATION.md`
19. `docs/VECTOR_DB_QUICK_START.md`
20. `docs/MUSTCARE_VECTOR_DB_INTEGRATION_ANALYSIS.md`
21. `UI/VECTOR_DB_REDESIGN_PLAN.md`
22. `UI/VECTOR_DB_ARCHITECTURE_FIX.md`
23. `QDRANT_MULTIMODAL_IMPLEMENTATION_PLAN.md`
24. `QDRANT_DOCKER_DEPLOYMENT_GUIDE.md`

**Total Lines Consolidated:** 6,000+ lines → 1,800 lines (70% reduction)  
**Documentation Coverage:** Complete system documentation with zero information loss

---

**END OF VECTOR_DATABASE.md**
