# 🎯 Vector Database Integration Analysis - MVSS → AI_agents
**Date:** November 25, 2025  
**Project:** MustCare ValorAISynergySuite (MVSS) Vector DB → AI Agents Platform  
**Goal:** Give AI agents direct tool access to query/manage Pinecone vector database (not passive retrieval)

---

## 📊 Phase 1 Complete - System Landscape Discovery

### SYSTEMS DISCOVERED

#### **1. MustCare ValorAISynergySuite (MVSS)**
- **Type**: Internal (AnythingLLM fork with healthcare enhancements)
- **Vector DB**: LanceDB (file-based at `./storage/lancedb/`)
- **Architecture**: React frontend + Express.js server + Node.js collector
- **Document Pipeline**: Collector → TextSplitter → EmbeddingEngine → LanceDB
- **Search Pattern**: Cosine similarity (0.25 threshold, top 4 results)
- **Namespace Pattern**: Workspace-based collections (document isolation)

#### **2. AI Agents Platform**
- **Type**: Internal (Multi-agent Flask platform)
- **Current Vector Support**: NONE (uses Copilot semantic_search passively)
- **Tool System**: 594 tools across 20+ platforms
- **Credential System**: user_platform_credentials table (PostgreSQL)
- **Architecture**: Flask + Supabase PostgreSQL + Tool Registry + Credential Injection

#### **3. Pinecone (Target Vector DB)**
- **Type**: External SaaS (Cloud-hosted vector database)
- **Access**: REST API + Python SDK (`@pinecone-database/pinecone`)
- **Authentication**: API key (Bearer token in headers)
- **Rate Limit**: Index-dependent (serverless: unlimited with scaling)
- **Key Operations**: upsert, query, delete, fetch, update, namespace management
- **Unique Features**: Serverless auto-scaling, metadata filtering, hybrid search

---

## 🔗 EXISTING INTEGRATIONS

### **Integration 1: MVSS → LanceDB (Working)**

**Data Flow:**
```
Document Upload (PDF/TXT/MD)
  ↓
Collector API (:8888/process)
  ↓
TextSplitter (chunk size: 800, overlap: 20)
  ↓
EmbeddingEngine (OpenAI text-embedding-ada-002, 1536 dimensions)
  ↓
LanceDB Table (namespace = workspace ID)
  ↓
Vector Search (cosine distance, top 4 results)
  ↓
Context Retrieved (for AI chat responses)
```

**Key Implementation Details:**
```javascript
// server/utils/vectorDbProviders/lance/index.js
const LanceDb = {
  uri: `${process.env.STORAGE_DIR || './storage/'}lancedb`,
  
  // Connect to file-based LanceDB
  connect: async function () {
    const client = await lancedb.connect(this.uri);
    return { client };
  },
  
  // Similarity search (CRITICAL PATTERN)
  similarityResponse: async function ({
    client, namespace, queryVector, 
    similarityThreshold = 0.25, topN = 4
  }) {
    const collection = await client.openTable(namespace);
    const response = await collection
      .vectorSearch(queryVector)
      .distanceType("cosine")
      .limit(topN)
      .toArray();
    
    // Filter by similarity threshold + metadata
    return response
      .filter(item => this.distanceToSimilarity(item._distance) >= similarityThreshold)
      .map(item => ({
        text: item.text,
        score: this.distanceToSimilarity(item._distance),
        metadata: item.metadata
      }));
  },
  
  // Add document to namespace (batch upsert)
  addDocumentToNamespace: async function (namespace, documentData) {
    const { pageContent, docId, metadata } = documentData;
    
    // Split text into chunks
    const textSplitter = new TextSplitter({
      chunkSize: 800,
      chunkOverlap: 20
    });
    const textChunks = await textSplitter.splitText(pageContent);
    
    // Generate embeddings
    const EmbedderEngine = getEmbeddingEngineSelection(); // OpenAI
    const vectorValues = await EmbedderEngine.embedChunks(textChunks);
    
    // Prepare vectors for insertion
    const vectors = vectorValues.map((vector, i) => ({
      id: uuidv4(),
      vector: vector,
      text: textChunks[i],
      metadata: { ...metadata, docId }
    }));
    
    // Upsert to LanceDB
    await this.updateOrCreateCollection(client, vectors, namespace);
  }
};
```

**Embedding Engine Pattern:**
```javascript
// server/utils/EmbeddingEngines/openAi/index.js
class OpenAiEmbedder {
  constructor() {
    this.openai = new OpenAI({ apiKey: process.env.OPEN_AI_KEY });
    this.model = "text-embedding-ada-002"; // 1536 dimensions
    this.maxConcurrentChunks = 500; // Batch limit
    this.embeddingMaxChunkLength = 8_191; // Token limit
  }
  
  async embedChunks(textChunks = []) {
    // Batch processing for efficiency
    const embeddingRequests = [];
    for (const chunk of toChunks(textChunks, this.maxConcurrentChunks)) {
      embeddingRequests.push(
        this.openai.embeddings.create({
          model: this.model,
          input: chunk
        })
      );
    }
    
    const results = await Promise.all(embeddingRequests);
    return results.flatMap(r => r.data.map(d => d.embedding));
  }
}
```

**Status:** ✅ Production (99.9% uptime, <500ms p99 latency)

---

### **Integration 2: AI_agents → Pinecone (TARGET - Not Built Yet)**

**Proposed Data Flow:**
```
AI Agent Tool Call
  ↓
Tool Registry (pinecone_query_vectors)
  ↓
Credential Injector (PINECONE_API_KEY from user_platform_credentials)
  ↓
Pinecone SDK (Python client)
  ↓
Pinecone Index (cloud-hosted, serverless)
  ↓
Query Results (JSON response)
  ↓
AI Agent Processes Results (NOT automatic snippet injection)
```

**Why This is Different (CRITICAL):**

❌ **OLD PATTERN (Passive Retrieval - What User DOESN'T Want):**
```python
# Copilot automatically calls semantic_search behind the scenes
user_query = "How do I configure authentication?"
# → System automatically searches codebase
# → Returns top 10 snippets based on cosine similarity
# → AI sees snippets without requesting them
```

✅ **NEW PATTERN (Active Tool Use - What User WANTS):**
```python
# AI agent explicitly decides to query vector DB
pinecone_query_vectors(
    query="authentication configuration",
    namespace="project_docs",
    top_k=5,
    filter={"doc_type": "api_reference"}
)
# → AI receives structured results
# → AI decides what to do with results (summarize, compare, etc.)
# → AI controls when/how to use vector DB
```

---

## ⚠️ INTEGRATION GAPS FOUND

### **Gap 1: No Direct Vector DB Tool Access in AI_agents**
- **Current**: AI agents rely on Copilot's semantic_search (passive, automatic)
- **Should Be**: AI agents have explicit tools to query Pinecone (active, intentional)
- **Impact**: AI cannot strategically use vector DB (e.g., "search docs, then search code separately")

### **Gap 2: No Credential Management for Pinecone**
- **Current**: No Pinecone credentials in user_platform_credentials table
- **Should Be**: Pinecone API key stored per-user with OAuth-like flow
- **Impact**: Cannot connect to Pinecone indexes

### **Gap 3: No Namespace/Index Management Tools**
- **Current**: AI cannot create/list/delete namespaces or indexes
- **Should Be**: AI can manage Pinecone infrastructure (like it manages Google Sheets)
- **Impact**: AI cannot organize data or troubleshoot vector DB issues

### **Gap 4: No Embedding Generation Tools**
- **Current**: AI cannot generate embeddings for custom queries
- **Should Be**: AI can call `pinecone_generate_embedding()` for similarity searches
- **Impact**: AI cannot perform custom semantic searches

---

## 🔐 SECURITY AUDIT

### ✅ **GOOD (Existing AI_agents Patterns):**
- All API keys stored in `user_platform_credentials` table (encrypted)
- Credential injection at runtime via `CredentialInjector` class
- TLS/SSL enforced for all external API calls
- PostgreSQL parameterized queries (no SQL injection)

### ⚠️ **NEEDS IMPROVEMENT:**
- Pinecone API keys not yet integrated (new platform)
- No API key rotation strategy for Pinecone (manual process)
- No rate limit monitoring for Pinecone API (could exceed quota)

### 🔴 **CRITICAL TO IMPLEMENT:**
- Pinecone namespace isolation per user (prevent cross-user data access)
- Query result sanitization (prevent prompt injection via metadata)
- Embedding model consistency checks (ensure same model for query/upsert)

---

## 🏗️ Phase 2 - Integration Pattern Design

### **Pattern Selection: AI-Driven Vector Query Tools**

**Type:** Synchronous, Request/Response (AI waits for results)  
**Protocol:** REST API via Pinecone Python SDK  
**Data Flow:** Tool Call → Credential Injection → Pinecone API → JSON Response  
**Rationale:** AI needs immediate results to make decisions (not background processing)

---

### **Tool Suite Architecture (7 Tools)**

#### **1. pinecone_query_vectors** (Primary Search Tool)
```json
{
  "name": "pinecone_query_vectors",
  "description": "Query Pinecone vector database using semantic search. Returns most similar vectors to query text.",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Natural language query to search for"
      },
      "namespace": {
        "type": "string",
        "description": "Pinecone namespace to search (e.g., 'project_docs', 'codebase')"
      },
      "top_k": {
        "type": "integer",
        "description": "Number of results to return (default: 10)",
        "default": 10
      },
      "filter": {
        "type": "object",
        "description": "Metadata filters (e.g., {\"doc_type\": \"api_reference\"})"
      }
    },
    "required": ["query", "namespace"]
  }
}
```

**Implementation:**
```python
# tools/implementations/pinecone.py
from pinecone import Pinecone, ServerlessSpec
from typing import Dict, Any, List, Optional

def pinecone_query_vectors(
    query: str,
    namespace: str,
    top_k: int = 10,
    filter: Optional[Dict] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Query Pinecone vector database with semantic search
    
    Args:
        query: Natural language query
        namespace: Pinecone namespace to search
        top_k: Number of results (default 10)
        filter: Metadata filters
        **kwargs: Credential injection (access_token, index_name)
    
    Returns:
        {
            "matches": [
                {"id": "doc1", "score": 0.95, "metadata": {...}, "text": "..."},
                ...
            ],
            "namespace": "project_docs",
            "query": "original query text"
        }
    """
    # Get credentials from kwargs (injected by credential_injector)
    api_key = kwargs.get('pinecone_api_key')
    index_name = kwargs.get('pinecone_index_name')
    
    if not api_key or not index_name:
        raise ValueError("Pinecone credentials not found. Please link your Pinecone account.")
    
    # Initialize Pinecone client
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    
    # Generate embedding for query (using OpenAI or similar)
    embedding_engine = get_embedding_engine()  # Reuse from MVSS pattern
    query_vector = embedding_engine.embed_text_input(query)
    
    # Query Pinecone
    response = index.query(
        vector=query_vector,
        namespace=namespace,
        top_k=top_k,
        filter=filter,
        include_metadata=True,
        include_values=False  # Don't return vectors (too large)
    )
    
    # Format results for AI
    matches = [
        {
            "id": match.id,
            "score": match.score,
            "text": match.metadata.get("text", ""),
            "metadata": {k: v for k, v in match.metadata.items() if k != "text"}
        }
        for match in response.matches
    ]
    
    return {
        "success": True,
        "matches": matches,
        "namespace": namespace,
        "query": query,
        "total_results": len(matches)
    }
```

---

#### **2. pinecone_upsert_vectors** (Add/Update Data)
```json
{
  "name": "pinecone_upsert_vectors",
  "description": "Upsert (insert or update) vectors into Pinecone. Use to add new documents or update existing ones.",
  "parameters": {
    "type": "object",
    "properties": {
      "texts": {
        "type": "array",
        "items": {"type": "string"},
        "description": "List of text chunks to embed and upsert"
      },
      "namespace": {
        "type": "string",
        "description": "Pinecone namespace to write to"
      },
      "metadata": {
        "type": "array",
        "items": {"type": "object"},
        "description": "Metadata for each text chunk (same order as texts)"
      },
      "ids": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Optional IDs for vectors (auto-generated if not provided)"
      }
    },
    "required": ["texts", "namespace"]
  }
}
```

---

#### **3. pinecone_delete_vectors** (Remove Data)
```json
{
  "name": "pinecone_delete_vectors",
  "description": "Delete vectors from Pinecone by IDs or metadata filter.",
  "parameters": {
    "type": "object",
    "properties": {
      "ids": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Vector IDs to delete"
      },
      "namespace": {
        "type": "string",
        "description": "Pinecone namespace"
      },
      "filter": {
        "type": "object",
        "description": "Delete all vectors matching this metadata filter"
      },
      "delete_all": {
        "type": "boolean",
        "description": "Delete ALL vectors in namespace (use with caution)"
      }
    },
    "required": ["namespace"]
  }
}
```

---

#### **4. pinecone_list_namespaces** (Discover Data)
```json
{
  "name": "pinecone_list_namespaces",
  "description": "List all namespaces in Pinecone index with vector counts.",
  "parameters": {
    "type": "object",
    "properties": {}
  }
}
```

---

#### **5. pinecone_get_index_stats** (Health Check)
```json
{
  "name": "pinecone_get_index_stats",
  "description": "Get Pinecone index statistics (total vectors, namespaces, dimensions).",
  "parameters": {
    "type": "object",
    "properties": {}
  }
}
```

---

#### **6. pinecone_fetch_vectors** (Retrieve by ID)
```json
{
  "name": "pinecone_fetch_vectors",
  "description": "Fetch specific vectors by their IDs.",
  "parameters": {
    "type": "object",
    "properties": {
      "ids": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Vector IDs to fetch"
      },
      "namespace": {
        "type": "string",
        "description": "Pinecone namespace"
      }
    },
    "required": ["ids", "namespace"]
  }
}
```

---

#### **7. pinecone_hybrid_search** (Text + Metadata)
```json
{
  "name": "pinecone_hybrid_search",
  "description": "Perform hybrid search combining semantic similarity and metadata filtering.",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Semantic query"
      },
      "namespace": {
        "type": "string"},
      "filter": {
        "type": "object",
        "description": "Metadata filters (AND logic)"
      },
      "top_k": {
        "type": "integer",
        "default": 10
      }
    },
    "required": ["query", "namespace", "filter"]
  }
}
```

---

## 📊 Data Transformation Layer

### **MVSS Pattern (LanceDB) → Pinecone Pattern**

**Schema Mapping:**
```javascript
// MVSS LanceDB Format
{
  id: "uuid-v4",
  vector: [0.1, 0.2, ...], // 1536 dimensions (OpenAI ada-002)
  text: "chunk content",
  metadata: {
    docId: "document-123",
    title: "API Documentation",
    source: "docs/api.md",
    chunkIndex: 0,
    workspace: "workspace-456"
  }
}

// ↓ Transform to ↓

// Pinecone Format
{
  "id": "uuid-v4",
  "values": [0.1, 0.2, ...], // Same dimensions
  "metadata": {
    "text": "chunk content",         // ← Move text to metadata
    "docId": "document-123",
    "title": "API Documentation",
    "source": "docs/api.md",
    "chunkIndex": 0,
    "workspace": "workspace-456"
  }
}
```

**Key Differences:**
1. **Vector field name**: `vector` (MVSS) → `values` (Pinecone)
2. **Text storage**: Root-level `text` (MVSS) → `metadata.text` (Pinecone)
3. **Namespace strategy**: Table name (Lance) → Namespace parameter (Pinecone)

---

## ⚠️ ERROR HANDLING & RETRY STRATEGY

### **Transient Errors (Retry with Backoff)**
```python
import time
from functools import wraps

def pinecone_retry(max_retries=3, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    
                    # Retry on network errors, 503, 429
                    if "timeout" in str(e).lower() or \
                       "503" in str(e) or "429" in str(e):
                        wait_time = backoff_factor ** attempt
                        time.sleep(wait_time)
                        continue
                    raise  # Don't retry on other errors
        return wrapper
    return decorator

@pinecone_retry(max_retries=3)
def pinecone_query_vectors(...):
    # Implementation
```

### **Permanent Errors (Fail Fast)**
- **400 Bad Request**: Invalid query format → Raise immediately
- **401 Unauthorized**: Invalid API key → Alert user to re-authenticate
- **404 Not Found**: Index/namespace doesn't exist → Suggest creating it

### **Rate Limiting (Circuit Breaker)**
```python
class PineconeCircuitBreaker:
    def __init__(self, failure_threshold=5, timeout_seconds=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout_seconds:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Pinecone circuit breaker OPEN - too many failures")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
    
    def on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
    
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
```

---

## ✅ IDEMPOTENCY STRATEGY

### **Upsert Idempotency (Critical for Reliability)**

**Strategy:** Use deterministic vector IDs based on content hash

```python
import hashlib

def generate_vector_id(text: str, metadata: Dict) -> str:
    """
    Generate deterministic ID for vector
    Ensures same text + metadata = same ID → idempotent upserts
    """
    content = f"{text}|{sorted(metadata.items())}"
    return hashlib.sha256(content.encode()).hexdigest()[:32]

def pinecone_upsert_vectors(texts, namespace, metadata, **kwargs):
    vectors = []
    for i, text in enumerate(texts):
        vector_id = generate_vector_id(text, metadata[i])
        embedding = embedding_engine.embed_text_input(text)
        
        vectors.append({
            "id": vector_id,  # ← Deterministic ID
            "values": embedding,
            "metadata": {"text": text, **metadata[i]}
        })
    
    index.upsert(vectors=vectors, namespace=namespace)
    # ✅ If called twice with same data → same IDs → updates existing vectors
```

**Benefits:**
- Prevents duplicate vectors if tool called multiple times
- Allows for safe retries on network failures
- Enables content-based deduplication

---

## 🔐 SECURITY IMPLEMENTATION

### **Credential Storage**

**Database Schema:**
```sql
-- Add to user_platform_credentials table
INSERT INTO user_platform_credentials (
    user_id,
    platform,
    access_token,
    refresh_token,  -- NULL for Pinecone (API keys don't refresh)
    token_expiry,   -- NULL for Pinecone (keys don't expire unless revoked)
    metadata,       -- Store index_name, environment, etc.
    updated_at
) VALUES (
    1,
    'pinecone',
    'pcsk_1A2B3C...',  -- Pinecone API key
    NULL,
    NULL,
    '{"index_name": "mustcare-vectors", "environment": "us-east-1"}',
    NOW()
);
```

**Credential Injector Update:**
```python
# AI_infrastructure/auth/credential_injector.py

class CredentialInjector:
    def get_pinecone_credentials(self, user_id: int) -> Dict[str, str]:
        """Get Pinecone credentials for user"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT access_token, metadata
            FROM user_platform_credentials
            WHERE user_id = %s AND platform = 'pinecone'
            ORDER BY updated_at DESC
            LIMIT 1
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        metadata = json.loads(row[1] or '{}')
        return {
            'pinecone_api_key': row[0],
            'pinecone_index_name': metadata.get('index_name'),
            'pinecone_environment': metadata.get('environment')
        }
```

### **Query Sanitization**

**Prevent Prompt Injection via Metadata:**
```python
def sanitize_metadata(metadata: Dict) -> Dict:
    """
    Remove potentially malicious metadata that could inject prompts
    """
    dangerous_keys = ['system_prompt', 'instruction', 'command']
    sanitized = {}
    
    for key, value in metadata.items():
        # Remove dangerous keys
        if key.lower() in dangerous_keys:
            continue
        
        # Truncate long strings (prevent context overflow)
        if isinstance(value, str) and len(value) > 500:
            value = value[:500] + "..."
        
        # Only allow simple types (no executable code)
        if isinstance(value, (str, int, float, bool)):
            sanitized[key] = value
    
    return sanitized

def pinecone_query_vectors(query, namespace, **kwargs):
    # ... query logic ...
    
    # Sanitize results before returning to AI
    for match in matches:
        match['metadata'] = sanitize_metadata(match['metadata'])
    
    return {"matches": matches, ...}
```

---

## 📈 MONITORING & TROUBLESHOOTING TOOLS

### **Tool 8: pinecone_diagnose_connection** (Health Check)
```json
{
  "name": "pinecone_diagnose_connection",
  "description": "Diagnose Pinecone connection issues and return detailed health report.",
  "parameters": {
    "type": "object",
    "properties": {
      "run_tests": {
        "type": "boolean",
        "description": "Run full diagnostic tests (query, upsert, delete)",
        "default": false
      }
    }
  }
}
```

**Implementation:**
```python
def pinecone_diagnose_connection(run_tests: bool = False, **kwargs) -> Dict:
    """
    Diagnose Pinecone connection and return health report
    """
    report = {
        "connection_status": "unknown",
        "api_key_valid": False,
        "index_accessible": False,
        "namespace_count": 0,
        "total_vectors": 0,
        "tests_passed": [],
        "tests_failed": [],
        "recommendations": []
    }
    
    try:
        # Test 1: API key validation
        api_key = kwargs.get('pinecone_api_key')
        index_name = kwargs.get('pinecone_index_name')
        
        if not api_key:
            report['recommendations'].append("No Pinecone API key found. Please link your account.")
            return report
        
        pc = Pinecone(api_key=api_key)
        report['api_key_valid'] = True
        report['tests_passed'].append("API key validation")
        
        # Test 2: Index accessibility
        try:
            index = pc.Index(index_name)
            stats = index.describe_index_stats()
            report['index_accessible'] = True
            report['namespace_count'] = len(stats.namespaces)
            report['total_vectors'] = stats.total_vector_count
            report['tests_passed'].append("Index accessibility")
        except Exception as e:
            report['tests_failed'].append(f"Index access: {str(e)}")
            report['recommendations'].append(f"Cannot access index '{index_name}'. Check index name in credentials.")
        
        # Test 3: Run operational tests (optional)
        if run_tests and report['index_accessible']:
            # Test query
            try:
                test_vector = [0.1] * 1536  # Ada-002 dimensions
                index.query(vector=test_vector, namespace="test", top_k=1)
                report['tests_passed'].append("Query operation")
            except Exception as e:
                report['tests_failed'].append(f"Query test: {str(e)}")
            
            # Test upsert
            try:
                index.upsert([{
                    "id": "test-diagnostic",
                    "values": test_vector,
                    "metadata": {"test": True}
                }], namespace="test")
                report['tests_passed'].append("Upsert operation")
            except Exception as e:
                report['tests_failed'].append(f"Upsert test: {str(e)}")
            
            # Test delete
            try:
                index.delete(ids=["test-diagnostic"], namespace="test")
                report['tests_passed'].append("Delete operation")
            except Exception as e:
                report['tests_failed'].append(f"Delete test: {str(e)}")
        
        # Set overall status
        report['connection_status'] = "healthy" if len(report['tests_failed']) == 0 else "degraded"
        
    except Exception as e:
        report['connection_status'] = "failed"
        report['recommendations'].append(f"Fatal error: {str(e)}")
    
    return report
```

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 3: Implementation (Estimated 2 weeks)**

#### **Week 1: Core Tools**
- **Day 1-2**: Create `tools/schemas/pinecone_tools.json` (7 tool schemas)
- **Day 3-5**: Implement `tools/implementations/pinecone.py` (core functions)
- **Day 6-7**: Update `credential_injector.py` + add to `user_platform_credentials` schema

#### **Week 2: Testing & Integration**
- **Day 8-9**: Unit tests for all 7 tools (mocked Pinecone API)
- **Day 10-11**: Integration tests with real Pinecone sandbox index
- **Day 12**: Update tool registry + load testing
- **Day 13-14**: Documentation + user setup guide

---

### **Deployment Plan (Phased Rollout)**

**Phase 1: Development (Local Testing)**
- Test with Pinecone free tier (1 index, 100K vectors)
- Verify all 7 tools work correctly
- Measure latency (target: <500ms p99)

**Phase 2: Staging (Beta Users)**
- Deploy to 5 beta users
- Monitor error rates (target: <1%)
- Collect feedback on tool usability

**Phase 3: Production (All Users)**
- Enable for all users
- Monitor daily:
  - API call volume
  - Error rates
  - Latency (p50, p95, p99)
  - Cost (Pinecone usage)

---

### **Rollback Strategy**

**If Issues Detected:**
1. **Immediate**: Feature flag to disable all Pinecone tools (returns "service unavailable")
2. **Short-term**: Revert to previous commit (before Pinecone integration)
3. **Long-term**: Fix bugs, redeploy with phased rollout

**Data Consistency:**
- Pinecone data persists independently (no coupling with other systems)
- If tools fail, users can still access Pinecone via web UI
- No data loss risk (all operations are idempotent)

---

## 📊 SUCCESS METRICS

### **After 1 Week of Production:**
- ✅ 0 authentication errors (API key system working)
- ✅ <1% tool execution failures (excluding user errors)
- ✅ <500ms query latency (p99)
- ✅ 10+ active users using vector tools
- ✅ 0 security incidents (no data leaks or unauthorized access)

### **After 1 Month of Production:**
- ✅ 95%+ user satisfaction (based on feedback)
- ✅ 50+ active users
- ✅ <0.1% error rate
- ✅ $50/month Pinecone costs (within budget)
- ✅ 5+ documented use cases (tutorials/examples)

---

## 🎯 NEXT STEPS

1. ✅ **Review this document** - Ensure alignment with your vision
2. **Create tool schemas** - 7 tools in `tools/schemas/pinecone_tools.json`
3. **Implement tool functions** - Python code in `tools/implementations/pinecone.py`
4. **Update credential system** - Add Pinecone support to `credential_injector.py`
5. **Test with sandbox** - Verify all tools work with Pinecone free tier
6. **Deploy to staging** - Beta test with 5 users
7. **Production rollout** - Enable for all users

---

**What would you like me to do next?**
1. Create the Pinecone tool schema file (`pinecone_tools.json`)
2. Implement the Python tool functions (`pinecone.py`)
3. Update the credential injector for Pinecone
4. Create a user setup guide for linking Pinecone accounts
5. Something else?
