# Qdrant Integration Testing Guide

**Created:** December 7, 2025  
**Purpose:** Validate Qdrant vector database integration with cutting-edge features

---

## 🎯 Testing Overview

This guide provides comprehensive testing procedures for the Qdrant vector database integration, including:
- Backend API validation (8 endpoints)
- Frontend UI functionality (provider selector, Docker wizard, connection testing)
- Advanced features (multi-modal embeddings, quantization, hybrid search)
- Multi-tenancy isolation
- Authentication & authorization

---

## 📋 Pre-Testing Checklist

### 1. Environment Setup
```bash
# Check Qdrant is installed in requirements.txt
grep "qdrant-client" requirements.txt
# Expected: qdrant-client>=1.7.0

# Install dependencies
pip install -r requirements.txt

# Verify flask_app.py blueprint registration
grep "qdrant_bp" AI_infrastructure/flask_app.py
# Expected: from routes.qdrant_routes import qdrant_bp
# Expected: app.register_blueprint(qdrant_bp, url_prefix='/api/qdrant')
```

### 2. Qdrant Server Setup (Choose ONE)

#### Option A: Local Docker (Recommended for Testing)
```bash
# Pull Qdrant image
docker pull qdrant/qdrant:latest

# Start Qdrant (no authentication)
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v ~/qdrant_data:/qdrant/storage \
  qdrant/qdrant:latest

# Verify Qdrant is running
curl http://localhost:6333/
# Expected: {"title":"qdrant - vector search engine","version":"..."}
```

#### Option B: Qdrant Cloud
1. Sign up at https://cloud.qdrant.io
2. Create a cluster
3. Get API key and host URL

### 3. Flask Server Setup
```bash
# Start Flask server
cd AI_agents
python AI_infrastructure/flask_app.py

# Server should start on port 5000
# Verify: http://localhost:5000
```

---

## 🧪 Backend API Tests (8 Endpoints)

### Test 1: Connect to Qdrant
**Endpoint:** `POST /api/qdrant/connect`

```bash
# Test 1A: Local Qdrant (no auth)
curl -X POST http://localhost:5000/api/qdrant/connect \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "host": "localhost",
    "port": 6333
  }'

# Expected Response:
{
  "success": true,
  "message": "Connected to Qdrant successfully",
  "version": "1.7.0",
  "collections": []
}

# Test 1B: Qdrant Cloud (with API key)
curl -X POST http://localhost:5000/api/qdrant/connect \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "host": "xyz-abc.aws.cloud.qdrant.io",
    "port": 6333,
    "api_key": "your-api-key-here"
  }'

# Test 1C: Invalid credentials (should fail)
curl -X POST http://localhost:5000/api/qdrant/connect \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "host": "invalid-host",
    "port": 9999
  }'

# Expected Response:
{
  "success": false,
  "error": "Connection failed: [Errno 111] Connection refused"
}
```

---

### Test 2: Create Collection
**Endpoint:** `POST /api/qdrant/create-collection`

```bash
# Test 2A: Create collection with default settings
curl -X POST http://localhost:5000/api/qdrant/create-collection \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "test_docs",
    "vector_size": 1536,
    "distance": "Cosine"
  }'

# Expected Response:
{
  "success": true,
  "message": "Collection test_docs_user_123 created successfully",
  "collection_name": "test_docs_user_123"
}

# Test 2B: Create collection with quantization (4x compression)
curl -X POST http://localhost:5000/api/qdrant/create-collection \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "quantized_docs",
    "vector_size": 1536,
    "distance": "Cosine",
    "quantization": "scalar",
    "quantization_params": {
      "type": "scalar",
      "quantile": 0.99
    }
  }'

# Test 2C: Create collection with multi-vector support (ColBERT MaxSim)
curl -X POST http://localhost:5000/api/qdrant/create-collection \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "multivector_docs",
    "vector_size": 768,
    "distance": "Cosine",
    "multi_vector": true
  }'

# Test 2D: Duplicate collection (should fail gracefully)
curl -X POST http://localhost:5000/api/qdrant/create-collection \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "test_docs",
    "vector_size": 1536
  }'

# Expected Response:
{
  "success": false,
  "error": "Collection already exists"
}
```

---

### Test 3: Upsert Vectors (with Auto-Embedding)
**Endpoint:** `POST /api/qdrant/upsert`

```bash
# Test 3A: Single document upsert (auto-embedding)
curl -X POST http://localhost:5000/api/qdrant/upsert \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "test_docs",
    "documents": [
      {
        "id": "doc1",
        "text": "This is a test document about AI and machine learning.",
        "metadata": {
          "title": "AI Guide",
          "author": "Test User",
          "timestamp": "2025-12-07T10:00:00Z"
        }
      }
    ]
  }'

# Expected Response:
{
  "success": true,
  "message": "Upserted 1 vectors to test_docs_user_123",
  "points_upserted": 1,
  "embeddings_generated": 1
}

# Test 3B: Batch upsert (10 documents)
curl -X POST http://localhost:5000/api/qdrant/upsert \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "test_docs",
    "documents": [
      {"id": "doc2", "text": "Document about Python programming", "metadata": {"category": "programming"}},
      {"id": "doc3", "text": "Document about web development", "metadata": {"category": "web"}},
      {"id": "doc4", "text": "Document about data science", "metadata": {"category": "data"}},
      {"id": "doc5", "text": "Document about DevOps", "metadata": {"category": "operations"}},
      {"id": "doc6", "text": "Document about cloud computing", "metadata": {"category": "cloud"}},
      {"id": "doc7", "text": "Document about cybersecurity", "metadata": {"category": "security"}},
      {"id": "doc8", "text": "Document about machine learning", "metadata": {"category": "ai"}},
      {"id": "doc9", "text": "Document about blockchain", "metadata": {"category": "crypto"}},
      {"id": "doc10", "text": "Document about IoT", "metadata": {"category": "hardware"}},
      {"id": "doc11", "text": "Document about quantum computing", "metadata": {"category": "research"}}
    ]
  }'

# Test 3C: Upsert with custom vectors (no auto-embedding)
curl -X POST http://localhost:5000/api/qdrant/upsert \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "test_docs",
    "points": [
      {
        "id": "custom1",
        "vector": [0.1, 0.2, 0.3, ...],  # 1536 dimensions
        "payload": {"custom": "metadata"}
      }
    ]
  }'
```

---

### Test 4: Semantic Search
**Endpoint:** `POST /api/qdrant/search`

```bash
# Test 4A: Basic semantic search
curl -X POST http://localhost:5000/api/qdrant/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "test_docs",
    "query": "Tell me about artificial intelligence",
    "limit": 5
  }'

# Expected Response:
{
  "success": true,
  "results": [
    {
      "id": "doc1",
      "score": 0.92,
      "payload": {
        "text": "This is a test document about AI and machine learning.",
        "title": "AI Guide",
        "author": "Test User"
      }
    },
    {
      "id": "doc8",
      "score": 0.87,
      "payload": {"text": "Document about machine learning", "category": "ai"}
    }
  ],
  "total": 2
}

# Test 4B: Search with metadata filter
curl -X POST http://localhost:5000/api/qdrant/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "test_docs",
    "query": "programming",
    "limit": 10,
    "filter": {
      "must": [
        {"key": "category", "match": {"value": "programming"}}
      ]
    }
  }'

# Test 4C: Search with score threshold
curl -X POST http://localhost:5000/api/qdrant/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "test_docs",
    "query": "cloud technologies",
    "limit": 5,
    "score_threshold": 0.8
  }'
```

---

### Test 5: Hybrid Search (Dense + Sparse BM25)
**Endpoint:** `POST /api/qdrant/hybrid-search`

```bash
# Test 5A: Hybrid search (balanced)
curl -X POST http://localhost:5000/api/qdrant/hybrid-search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "test_docs",
    "query": "machine learning algorithms",
    "limit": 5,
    "alpha": 0.5
  }'

# Expected Response:
{
  "success": true,
  "results": [
    {
      "id": "doc8",
      "score": 0.94,
      "payload": {"text": "Document about machine learning", "category": "ai"}
    }
  ],
  "search_type": "hybrid",
  "alpha": 0.5
}

# Test 5B: Semantic-focused hybrid search (alpha=0.8)
curl -X POST http://localhost:5000/api/qdrant/hybrid-search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "test_docs",
    "query": "AI technology",
    "limit": 5,
    "alpha": 0.8
  }'

# Test 5C: Keyword-focused hybrid search (alpha=0.2)
curl -X POST http://localhost:5000/api/qdrant/hybrid-search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "test_docs",
    "query": "python programming language",
    "limit": 5,
    "alpha": 0.2
  }'
```

---

### Test 6: Get Stats
**Endpoint:** `GET /api/qdrant/stats`

```bash
# Test 6A: Get all stats
curl -X GET http://localhost:5000/api/qdrant/stats \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Expected Response:
{
  "success": true,
  "stats": {
    "collections_count": 3,
    "total_vectors": 11,
    "collections": [
      {
        "name": "test_docs_user_123",
        "vectors_count": 11,
        "indexed_vectors_count": 11,
        "points_count": 11,
        "segments_count": 1,
        "status": "green",
        "optimizer_status": "ok",
        "vector_data_config": {
          "size": 1536,
          "distance": "Cosine"
        }
      },
      {
        "name": "quantized_docs_user_123",
        "vectors_count": 0,
        "status": "green"
      }
    ]
  }
}

# Test 6B: Get stats for specific collection
curl -X GET "http://localhost:5000/api/qdrant/stats?collection_name=test_docs" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### Test 7: Delete Vectors
**Endpoint:** `POST /api/qdrant/delete`

```bash
# Test 7A: Delete by IDs
curl -X POST http://localhost:5000/api/qdrant/delete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "test_docs",
    "point_ids": ["doc1", "doc2"]
  }'

# Expected Response:
{
  "success": true,
  "message": "Deleted 2 points from test_docs_user_123"
}

# Test 7B: Delete by metadata filter
curl -X POST http://localhost:5000/api/qdrant/delete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "test_docs",
    "filter": {
      "must": [
        {"key": "category", "match": {"value": "programming"}}
      ]
    }
  }'

# Test 7C: Delete entire collection
curl -X POST http://localhost:5000/api/qdrant/delete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "test_docs",
    "delete_collection": true
  }'
```

---

### Test 8: Create Snapshot
**Endpoint:** `POST /api/qdrant/snapshot`

```bash
# Test 8A: Create snapshot
curl -X POST http://localhost:5000/api/qdrant/snapshot \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "test_docs"
  }'

# Expected Response:
{
  "success": true,
  "snapshot": {
    "name": "test_docs_user_123-2025-12-07T10-30-00.snapshot",
    "size": 1048576,
    "created_at": "2025-12-07T10:30:00Z"
  }
}
```

---

## 🎨 Frontend UI Tests

### Test 9: Provider Selector
1. **Open Vector Database Sidebar:**
   - Click "Vector Database" icon in main navigation (left side of screen)
   - Sidebar should slide in from left (450px width)

2. **Test Provider Dropdown:**
   - Locate "Provider" dropdown in header area
   - Should show 4 options:
     - 🌲 Pinecone (default)
     - ⚡ Qdrant (FREE)
     - 🚀 Voyager
     - 🐘 pgvector
   - Select "⚡ Qdrant (FREE)"
   - Provider info text should update to: "⚡ Qdrant - FREE self-hosted, 1-5ms latency, unlimited storage"
   - "Qdrant" tab should appear in tab navigation

3. **Verify State Persistence:**
   - Refresh page
   - Selected provider should remain "Qdrant"
   - Check browser localStorage: `selectedProvider` should be "qdrant"

---

### Test 10: Qdrant Configuration Tab

1. **Switch to Qdrant Tab:**
   - Click "Qdrant" tab (should be visible after selecting Qdrant provider)
   - Tab content should display Qdrant configuration UI

2. **Test Deployment Type Selector:**
   - Dropdown should show 3 options:
     - 🖥️ Customer Server (Docker - FREE, 1-5ms)
     - ☁️ Valor Cloud (Render - FREE, 100-150ms)
     - 🌐 Qdrant Cloud (Managed - $25-99/mo, 50-100ms)
   - Select "Customer Server"
   - Docker wizard section should be visible

3. **Test Docker Wizard:**
   - Click "Generate Docker Commands" button
   - Should detect OS (Windows/Linux)
   - Commands should appear in text area below button
   - Windows: PowerShell commands with `New-Item`, `docker run`, `Invoke-WebRequest`
   - Linux: Bash commands with `mkdir -p`, `docker run`, `curl`
   - Copy commands to clipboard (optional)

4. **Test Connection Settings:**
   - Enter Host: `localhost`
   - Enter Port: `6333`
   - Leave API Key blank (for local Docker)
   - Click "Test Connection" button
   - Button should show spinner icon
   - Connection status box should display:
     - Loading: 🔄 "Testing connection..." (blue)
     - Success: ✅ "Connected successfully! Version: 1.7.0" (green)
     - Error: ❌ "Connection failed: [error message]" (red)

5. **Test Advanced Features Toggles:**
   - **Multi-Modal Embeddings:** Click toggle, should turn green
   - **Vector Quantization:** Click toggle, should turn green
   - **Hybrid Search:** Click toggle, should turn green
   - Check browser console for log messages: `[VECTOR DB] Multi-modal embeddings: true`
   - Verify localStorage updates: `multiModalEnabled`, `quantizationEnabled`, `hybridSearchEnabled`

---

## 🔒 Security & Multi-Tenancy Tests

### Test 11: Multi-Tenancy Isolation

**Goal:** Verify that users can only access their own collections

```bash
# User 1 (ID: 123) creates collection
curl -X POST http://localhost:5000/api/qdrant/create-collection \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer USER1_JWT_TOKEN" \
  -d '{
    "collection_name": "my_docs",
    "vector_size": 1536
  }'
# Expected: Collection "my_docs_user_123" created

# User 1 upserts data
curl -X POST http://localhost:5000/api/qdrant/upsert \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer USER1_JWT_TOKEN" \
  -d '{
    "collection_name": "my_docs",
    "documents": [{"id": "secret1", "text": "User 1 secret data"}]
  }'

# User 2 (ID: 456) tries to access User 1's collection
curl -X POST http://localhost:5000/api/qdrant/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer USER2_JWT_TOKEN" \
  -d '{
    "collection_name": "my_docs",
    "query": "secret"
  }'
# Expected: {"success": false, "error": "Collection not found"}
# (User 2 gets "my_docs_user_456" which doesn't exist)

# User 2 creates own collection
curl -X POST http://localhost:5000/api/qdrant/create-collection \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer USER2_JWT_TOKEN" \
  -d '{
    "collection_name": "my_docs",
    "vector_size": 1536
  }'
# Expected: Collection "my_docs_user_456" created (separate from User 1)

# Verify isolation in Qdrant
curl http://localhost:6333/collections
# Expected: Should see both "my_docs_user_123" and "my_docs_user_456"
```

---

### Test 12: Authentication & Authorization

```bash
# Test 12A: No JWT token (should fail)
curl -X POST http://localhost:5000/api/qdrant/connect \
  -H "Content-Type: application/json" \
  -d '{
    "host": "localhost",
    "port": 6333
  }'
# Expected: {"error": "Unauthorized", "message": "Missing token"}

# Test 12B: Invalid JWT token (should fail)
curl -X POST http://localhost:5000/api/qdrant/connect \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer INVALID_TOKEN" \
  -d '{
    "host": "localhost",
    "port": 6333
  }'
# Expected: {"error": "Unauthorized", "message": "Invalid token"}

# Test 12C: Expired JWT token (should fail)
curl -X POST http://localhost:5000/api/qdrant/connect \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer EXPIRED_TOKEN" \
  -d '{
    "host": "localhost",
    "port": 6333
  }'
# Expected: {"error": "Unauthorized", "message": "Token expired"}
```

---

## 🚀 Advanced Feature Tests

### Test 13: Multi-Modal Embeddings (CLIP-Style)

**Note:** Multi-modal embeddings require backend support for image/audio/video processing. Currently implemented for text only, but architecture supports future expansion.

```bash
# Test 13A: Text + Image (Future Feature)
curl -X POST http://localhost:5000/api/qdrant/upsert \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "multimodal_docs",
    "documents": [
      {
        "id": "mm1",
        "text": "A photo of a cat sitting on a laptop",
        "image_url": "https://example.com/cat.jpg",
        "metadata": {"type": "image_with_caption"}
      }
    ],
    "multi_modal": true
  }'

# Expected: Backend generates CLIP embeddings for both text and image
```

---

### Test 14: Vector Quantization (4-32x Compression)

```bash
# Test 14A: Create collection with Scalar Quantization (4x compression)
curl -X POST http://localhost:5000/api/qdrant/create-collection \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "quantized_test",
    "vector_size": 1536,
    "distance": "Cosine",
    "quantization": "scalar",
    "quantization_params": {
      "type": "scalar",
      "quantile": 0.99,
      "always_ram": true
    }
  }'

# Test 14B: Upsert 10,000 vectors and measure performance
# Before quantization: ~60MB RAM, 100ms search
# After quantization: ~15MB RAM, 120ms search (4x compression, 20% slower)

# Test 14C: Binary Quantization (32x compression)
curl -X POST http://localhost:5000/api/qdrant/create-collection \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "binary_test",
    "vector_size": 1536,
    "distance": "Cosine",
    "quantization": "binary",
    "quantization_params": {
      "type": "binary",
      "always_ram": true
    }
  }'
# Before: 60MB RAM
# After: 1.9MB RAM (32x compression)
```

---

### Test 15: ColBERT MaxSim (Multi-Vector Search)

**Note:** ColBERT MaxSim is a cutting-edge feature for sentence-level granularity in semantic search.

```bash
# Test 15A: Create multi-vector collection
curl -X POST http://localhost:5000/api/qdrant/create-collection \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "colbert_test",
    "vector_size": 768,
    "distance": "Cosine",
    "multi_vector": true,
    "vectors_config": {
      "": {
        "size": 768,
        "distance": "Cosine",
        "on_disk": false
      }
    }
  }'

# Test 15B: Upsert document with multiple sentence embeddings
curl -X POST http://localhost:5000/api/qdrant/upsert \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "colbert_test",
    "points": [
      {
        "id": "doc1",
        "vector": [
          [0.1, 0.2, ...],  # Sentence 1 embedding (768 dims)
          [0.3, 0.4, ...],  # Sentence 2 embedding (768 dims)
          [0.5, 0.6, ...]   # Sentence 3 embedding (768 dims)
        ],
        "payload": {"text": "Multi-sentence document"}
      }
    ]
  }'

# Test 15C: Search with ColBERT MaxSim
# Uses maximum similarity across all sentence embeddings
curl -X POST http://localhost:5000/api/qdrant/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "colbert_test",
    "query": "specific sentence from document",
    "limit": 5
  }'
# Expected: Higher precision for finding specific sentences within documents
```

---

## 📊 Performance Benchmarks

### Test 16: Load Testing

```bash
# Test 16A: Upsert Performance (1,000 documents)
time curl -X POST http://localhost:5000/api/qdrant/upsert \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "collection_name": "perf_test",
    "documents": [...]  # 1,000 documents
  }'
# Expected: <5 seconds (auto-embedding + upsert)

# Test 16B: Search Performance (10,000 vectors)
# Measure average search latency over 100 queries
for i in {1..100}; do
  curl -X POST http://localhost:5000/api/qdrant/search \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer YOUR_JWT_TOKEN" \
    -d '{"collection_name": "perf_test", "query": "test query '$i'", "limit": 10}'
done
# Expected: <50ms average (local Docker), <150ms (Valor Cloud)

# Test 16C: Concurrent Users (50 simultaneous searches)
seq 1 50 | xargs -P 50 -I {} curl -X POST http://localhost:5000/api/qdrant/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"collection_name": "perf_test", "query": "concurrent test", "limit": 10}'
# Expected: No errors, <200ms max latency
```

---

## ✅ Expected Results Summary

| Test | Component | Expected Outcome |
|------|-----------|------------------|
| 1-8  | Backend API | All 8 endpoints respond with correct data |
| 9    | Provider Selector | Dropdown works, state persists |
| 10   | Qdrant Config Tab | All UI elements functional |
| 11   | Multi-Tenancy | Users isolated, cannot access other users' data |
| 12   | Authentication | JWT required, invalid tokens rejected |
| 13   | Multi-Modal | Text embeddings work (image/audio future) |
| 14   | Quantization | 4-32x compression, 10-20% slower search |
| 15   | ColBERT MaxSim | Sentence-level precision (if implemented) |
| 16   | Performance | <50ms search, <5s upsert (1k docs) |

---

## 🐛 Troubleshooting

### Issue 1: Connection Failed
**Error:** `{"success": false, "error": "Connection failed: [Errno 111] Connection refused"}`

**Solutions:**
- Verify Qdrant is running: `docker ps | grep qdrant`
- Check port is accessible: `curl http://localhost:6333/`
- Verify firewall allows port 6333
- Check Qdrant logs: `docker logs qdrant`

---

### Issue 2: Collection Not Found
**Error:** `{"success": false, "error": "Collection not found"}`

**Solutions:**
- Verify collection exists: `curl http://localhost:6333/collections`
- Check user_id suffix: Should be `collection_name_user_123`
- Create collection first using Test 2

---

### Issue 3: Embedding Generation Failed
**Error:** `{"success": false, "error": "Failed to generate embeddings"}`

**Solutions:**
- Check Voyager AI API key: `echo $VOYAGER_API_KEY`
- Check OpenAI API key: `echo $OPENAI_API_KEY`
- Verify UnifiedAIClient is initialized
- Check Flask server logs for detailed error

---

### Issue 4: Frontend Toggle Not Working
**Symptoms:** Toggle switches don't change state

**Solutions:**
- Check browser console for JavaScript errors
- Verify event handlers are registered: Search for `dom.on` in `vector_database.js`
- Clear browser cache and localStorage
- Verify CSS styles loaded: `.toggle-switch` should exist

---

## 🎓 Next Steps

After completing all tests:

1. **Create User Documentation:**
   - Customer-facing guide for Qdrant setup
   - Docker deployment instructions
   - Best practices for vector search

2. **Production Deployment:**
   - Deploy to Render with Qdrant Cloud integration
   - Configure environment variables
   - Set up monitoring and alerting

3. **Advanced Features:**
   - Implement multi-modal embeddings (CLIP)
   - Add GPU support for quantization
   - Build visual analytics dashboard

4. **Optimization:**
   - Enable binary quantization for large collections (>1M vectors)
   - Implement caching for frequently accessed vectors
   - Add batch processing for bulk uploads

---

## 📚 References

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Qdrant Python Client](https://github.com/qdrant/qdrant-client)
- [ColBERT MaxSim Paper](https://arxiv.org/abs/2004.12832)
- [Vector Quantization Guide](https://qdrant.tech/documentation/guides/quantization/)
- [CLIP Multi-Modal Embeddings](https://openai.com/research/clip)

---

**Testing Completed:** ____/____/____  
**Tester:** ________________  
**All Tests Passed:** ☐ YES  ☐ NO  
**Notes:** ________________________________________________
