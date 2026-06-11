# Vector Database — Developer Reference
**Created:** June 11, 2026
**Audience:** AI coding agents and developers working with the vector database feature
**Authoritative state as of:** June 11, 2026 (commits up to `a62b8f36`)
**Related docs:**
- `VECTOR_DB_ORG_ALIGNMENT_ANALYSIS_APR29_2026.md` — full gap analysis and change history
- `ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md` — org/credential system context
- `AI_infrastructure/migrations/044_pgvector_org_documents.sql` — schema definition
- `AI_infrastructure/migrations/049_pgvector_dimension_768.sql` — dimension fix

---

## 1. Architecture Overview

The vector database feature uses **pgvector** (built into Supabase) as the primary provider. Pinecone is a secondary option for orgs that have a Pinecone credential configured. All documents are scoped to the calling user's **organisation** — no cross-org data access is possible.

```
User uploads document
        │
        ▼
POST /api/vector-db/upload-document
        │
        ├─ Reads embedding_provider from form data ('local'|'voyager'|'openai'|absent)
        ├─ Calls _get_vector_provider(user_id)  →  'pgvector' | 'pinecone'
        │
        ▼ (pgvector path — default for all users)
_pgvec_upload(text_content, filename, embedding_provider=...)
        │
        ├─ Chunks text (chunk_size=800, overlap=100)
        ├─ For each chunk: _generate_embedding(chunk, user_id, is_query=False)
        │       └─ Resolves provider: force_local → BGE | vault → Voyage | vault → OpenAI | BGE fallback
        ├─ Upserts to ai_infrastructure.org_vector_documents (org_id scoped)
        ▼
Response: {success, document_id, vectors_uploaded, chunks_created, provider}

AI agent queries
        │
        ▼
pgvector_query_vectors(query_text, top_k=10, threshold=0.5, _user_id=user_id)
        │
        ├─ _generate_embedding(query_text, user_id, is_query=True)  ← note: is_query=True
        ├─ Cosine similarity search in org_vector_documents WHERE org_id = _get_org_id(user_id)
        ▼
{success: True, matches: [{id, document_id, filename, chunk_index, score, text, ...}]}
```

---

## 2. File Map

| File | Role | Key Functions |
|------|------|---------------|
| `tools/implementations/pgvector/pgvector_tools.py` | **Backend tool implementations** | `_generate_embedding()`, `pgvector_upload_document()`, `pgvector_query_vectors()`, `pgvector_upsert_vectors()`, `pgvector_delete_vectors()`, `pgvector_list_documents()`, `pgvector_describe_stats()` |
| `AI_infrastructure/routes/vector_db_routes.py` | **Flask REST API** | `upload_document()`, `list_documents()`, `get_stats()`, `_get_vector_provider()` |
| `UI/modules_internal/vector_database/vector_database.js` | **Frontend controller** | `processFiles()`, `onEmbeddingModelChange()`, `_updateEmbeddingModelInfo()`, `showConnectedBanner()`, `openHelp()` |
| `UI/modules_internal/vector_database/vector_database.html` | **Sidebar template** | Upload tab, Documents tab, Settings tab (embedding model selector, `#upload-result-message`) |
| `UI/modules_internal/vector_database/vector_database.css` | **Styling** | Sidebar layout, upload zone, document cards |
| `AI_infrastructure/migrations/044_pgvector_org_documents.sql` | **Schema** | Creates `ai_infrastructure.org_vector_documents`, HNSW cosine index |
| `AI_infrastructure/migrations/049_pgvector_dimension_768.sql` | **Schema fix** | Sets column to `vector(768)` |
| `tools/implementations/pinecone/pinecone_tools.py` | **Pinecone tools** (secondary) | Used only when org has a Pinecone credential in vault |

---

## 3. Database Schema

### Table: `ai_infrastructure.org_vector_documents`

Created by migration 044, dimension fixed to 768 by migration 049.

```sql
CREATE TABLE ai_infrastructure.org_vector_documents (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          INTEGER     NOT NULL REFERENCES ai_infrastructure.organisations(id),
    user_id         INTEGER     NOT NULL REFERENCES ai_infrastructure.users(id),
    document_id     TEXT        NOT NULL,     -- e.g. 'doc_a1b2c3d4'
    filename        TEXT        NOT NULL,
    chunk_index     INTEGER     NOT NULL DEFAULT 0,
    total_chunks    INTEGER     NOT NULL DEFAULT 1,
    content         TEXT        NOT NULL,     -- raw text of this chunk
    embedding       vector(768) NOT NULL,     -- embedding vector (768 dims)
    emb_model       TEXT,                     -- e.g. 'bge-base-en-v1.5', 'text-embedding-3-small'
    emb_provider    TEXT,                     -- e.g. 'local', 'openai', 'voyager'
    visibility      TEXT        NOT NULL DEFAULT 'org', -- 'private'|'org'|'global'
    metadata        JSONB,                    -- arbitrary key-value store
    file_type       TEXT,                     -- MIME type or extension
    file_size_bytes BIGINT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- HNSW index for cosine similarity (fast approximate nearest neighbour)
CREATE INDEX ON ai_infrastructure.org_vector_documents
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
```

**Multi-tenancy:** All queries hard-filter on `org_id`. `_get_org_id(user_id)` resolves org from `ai_infrastructure.users.organisation_id`.

---

## 4. Embedding Model Details

All three providers produce **768-dimensional** vectors. The schema column is `vector(768)`. No migration is needed when switching providers — but **existing documents must be re-uploaded** if the provider changes (different model spaces are not comparable).

### 4.1 Local BGE (Default — Free)

| Property | Value |
|----------|-------|
| Model | `BAAI/bge-base-en-v1.5` |
| Dimensions | 768 |
| MTEB retrieval | 63.55 |
| Cost | Free (on-server) |
| RAM | ~600 MB when loaded |
| Disk | ~440 MB |
| License | MIT |
| Design | Asymmetric retrieval — queries use a task prefix, passages do not |

**Cache location (Render):** `/data/vdb_models/models--BAAI--bge-base-en-v1.5/snapshots/<hash>/`
**Cache location (local dev):** `~/.cache/vdb_models/models--BAAI--bge-base-en-v1.5/snapshots/<hash>/`

**Important — offline loading:**  The model is loaded from its local snapshot directory, NOT by model name. This skips all HuggingFace Hub network calls. If the model is not cached, it downloads once (30-60s on first deployment).

**Asymmetric encoding:**
```python
# For search queries (is_query=True):
encode_kwargs['prompt'] = 'Represent this sentence for searching relevant passages: '

# For document uploads (is_query=False):
# No prompt — raw text
```

### 4.2 Voyage AI (`voyager` platform in org vault)

| Property | Value |
|----------|-------|
| Model | `voyage-4` (or auto-upgraded from `voyage-4-lite`) |
| Dimensions | 768 (requested via `output_dimension=768`) |
| MTEB retrieval | ~70+ |
| Cost | ~$0.06 per 1M tokens |
| Requires | `voyager` credential in org vault (`credentials.model = 'voyage-4'`) |

**Credential structure:**
```json
{
  "api_key": "pa-...",
  "provider": "voyager",
  "model": "voyage-4"
}
```

**Lite model auto-upgrade:** `voyage-4-lite` → `voyage-4`, `voyage-3-lite` → `voyage-3` (lite models cap at 512 dims, incompatible with `vector(768)` column).

### 4.3 OpenAI (`openai` or `openai_embeddings` platform in org vault)

| Property | Value |
|----------|-------|
| Model | `text-embedding-3-small` (default) |
| Dimensions | 768 (requested via `dimensions=768`) |
| MTEB retrieval | ~62 |
| Cost | ~$0.02 per 1M tokens |
| Requires | `openai` or `openai_embeddings` credential in org vault |

**Note:** `text-embedding-ada-002` does not support custom dimensions. If that model is stored in the vault, the embedding will be 1536 dims and the upsert to `vector(768)` will fail. Only `text-embedding-3-*` models support `dimensions=768`.

---

## 5. Provider Resolution Logic

### 5.1 Vector Provider (`pgvector` vs `pinecone`)

**Function:** `_get_vector_provider(user_id)` in `vector_db_routes.py`

```
1. Is user's org a personal org (is_personal_org=TRUE)?
   → YES: return 'pgvector'  (personal orgs never have Pinecone)

2. Does org have a 'pinecone' credential in the vault?
   → YES: return 'pinecone'

3. Default: return 'pgvector'
```

The route also reads `provider` from the form field for user-explicit selection:
```python
_requested = request.form.get('provider', '').strip().lower()
provider = _requested if _requested in ('pgvector', 'pinecone', 'qdrant') else _get_vector_provider(user_id)
```

### 5.2 Embedding Provider

**Function:** `_generate_embedding(text, user_id, is_query, force_local)` in `pgvector_tools.py`

```
force_local=True (user chose 'local' in Settings)
  → raw_cred = None → BGE local model

force_local=False (default)
  → Try resolve_credentials(user_id, 'voyager')
  → Or try resolve_credentials(user_id, 'openai_embeddings')
  → Or try resolve_credentials(user_id, 'openai')
  → None found → BGE local model (free fallback)
```

The route reads `embedding_provider` from form data and converts `'local'` to `force_local=True`:
```python
_emb_prov = request.form.get('embedding_provider', '').strip().lower()
embedding_provider = _emb_prov if _emb_prov in ('local', 'voyager', 'openai') else None
# Then:
_force_local = (embedding_provider == 'local')  # inside pgvector_upload_document()
```

---

## 6. API Endpoints

All endpoints require `@require_auth`. User ID is read from `g.rls_user_id` (set by JWT middleware).

| Method | URL | Description |
|--------|-----|-------------|
| `POST` | `/api/vector-db/upload-document` | Upload a document (multipart form data) |
| `GET` | `/api/vector-db/documents` | List uploaded documents for the org |
| `GET` | `/api/vector-db/stats` | Document/chunk counts + provider info |
| `GET` | `/api/vector-db/credentials/load` | **Returns 410 Gone** (retired — use Org Settings > Connections) |
| `POST` | `/api/vector-db/credentials/save` | **Returns 410 Gone** (retired — use Org Settings > Connections) |
| `GET` | `/api/vector-db/credentials/status` | Check if a vector provider is configured for the org |

### Upload Request (POST /api/vector-db/upload-document)

Form fields:
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `file` | File | required | Document to upload (PDF, DOCX, TXT, MD) |
| `provider` | string | auto-detected | `'pgvector'` or `'pinecone'` |
| `embedding_provider` | string | auto-detected | `'local'`, `'voyager'`, or `'openai'` |
| `chunk_size` | int | 800 | Characters per chunk |
| `chunk_overlap` | int | 100 | Character overlap between chunks |
| `visibility` | string | `'org'` | `'private'`, `'org'`, or `'global'` |
| `namespace` | string | `''` | Pinecone namespace (ignored for pgvector) |

### Upload Response (success)
```json
{
  "success": true,
  "document_id": "doc_a1b2c3d4",
  "filename": "policy.pdf",
  "vectors_uploaded": 12,
  "chunks_created": 12,
  "provider": "pgvector",
  "ai_retrievable": true,
  "message": "Document uploaded to pgvector store successfully"
}
```

---

## 7. AI Tool Functions

These are the functions AI agents call directly (via the tool registry). All require `_user_id` in `**kwargs`.

### `pgvector_query_vectors`
```python
result = pgvector_query_vectors(
    query_text="What is the refund policy?",  # OR query_vector=[...]
    top_k=10,           # max results
    threshold=0.5,      # min cosine similarity (0-1)
    document_id=None,   # restrict to one document
    _user_id=user_id
)
# Returns: {success: True, matches: [{id, document_id, filename, chunk_index, score, text, metadata, created_at}]}
```

### `pgvector_upload_document`
```python
result = pgvector_upload_document(
    text_content="Full document text...",
    filename="policy.pdf",
    file_type="application/pdf",
    file_size_bytes=12345,
    chunk_size=800,
    chunk_overlap=100,
    visibility="org",
    document_id="doc_a1b2c3d4",   # optional — generated if absent
    embedding_provider="local",    # 'local'|'voyager'|'openai'|None
    _user_id=user_id
)
# Returns: {success: True, document_id, vectors_uploaded, chunks_created}
```

### `pgvector_delete_vectors`
```python
result = pgvector_delete_vectors(document_id="doc_a1b2c3d4", _user_id=user_id)
result = pgvector_delete_vectors(delete_all=True, _user_id=user_id)  # ⚠️ deletes all org docs
```

### `pgvector_list_documents`
```python
result = pgvector_list_documents(_user_id=user_id)
# Returns: {success: True, documents: [{document_id, filename, chunks, file_size_bytes, created_at}], total: N}
```

### `pgvector_describe_stats`
```python
result = pgvector_describe_stats(_user_id=user_id)
# Returns: {success: True, provider: 'pgvector', total_documents: N, total_chunks: N, org_id: X}
```

### `pgvector_upsert_vectors`
```python
result = pgvector_upsert_vectors(
    vectors=[
        {
            "id": "some-uuid",
            "values": [0.1, 0.2, ...],  # 768-dim float list
            "metadata": {
                "document_id": "doc_abc",
                "filename": "report.pdf",
                "chunk_index": 0,
                "total_chunks": 5,
                "text": "chunk content...",
                "created_at": "2026-06-09T12:00:00Z"
            }
        }
    ],
    _user_id=user_id
)
```

---

## 8. Frontend Component

**Module:** `VectorDatabaseModule` (ModuleLoaderV4 composition pattern)
**Files:** `vector_database.js` + `vector_database.html` + `vector_database.css`
**Sidebar ID:** `sidebar-vector-database`

### Key State Properties
```javascript
state: {
    API_BASE_URL: window.API_BASE_URL || window.location.origin,
    selectedProvider: 'pgvector',          // 'pgvector' | 'pinecone'
    embeddingProvider: 'local',            // 'local' | 'voyager' | 'openai'
    files: [],                             // staged files for upload
    uploadedDocuments: [],                 // documents list from backend
}
```

### Key HTML Element IDs
| ID | What |
|----|------|
| `#embedding-model-selector` | Embedding model dropdown in Settings tab |
| `#embedding-model-info` | Hint text below selector |
| `#upload-result-message` | Inline error/success div below Process button |
| `#vector-db-upload-zone` | Drag-drop file zone |
| `#vector-db-process-btn` | "Process & Upload" button |
| `#vector-db-documents-list` | Documents list container |
| `#vector-db-stats-bar` | Stats bar (org scope, doc count, chunk count) |
| `sidebar-vector-database` | Sidebar root container |
| `vector-database-toggle` | Sidebar open button in main app |

### Embedding Model Persistence
```javascript
// Load on sidebar open:
const saved = localStorage.getItem('vdb_embedding_provider') || 'local';
state.embeddingProvider = saved;

// Save on change:
localStorage.setItem('vdb_embedding_provider', value);
```

### Upload Flow
```javascript
processFiles() {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('provider', state.selectedProvider);
    formData.append('embedding_provider', state.embeddingProvider || 'local');
    // ... other fields
    
    const response = await fetch(`${API_BASE_URL}/api/vector-db/upload-document`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${authToken}` },
        body: formData
    });
    
    // Show result inline below Process button:
    const msgDiv = document.getElementById('upload-result-message');
    if (result.success) {
        msgDiv.style.color = 'green';
        msgDiv.textContent = `✓ Uploaded ${result.filename} (${result.vectors_uploaded} chunks)`;
    } else {
        msgDiv.style.color = 'red';
        msgDiv.textContent = `Error: ${result.error}`;
    }
    msgDiv.style.display = 'block';
}
```

---

## 9. Credential Configuration

### Where to configure embedding credentials

Credentials are stored in the **org vault** (`ai_infrastructure.organisation_platform_credentials`). Do NOT configure them in the Vector DB sidebar settings tab (those endpoints return 410 Gone).

**Path:** Account Profile → Organisation → Connections tab → Add Connection

| Platform key | Credential structure | Used for |
|---|---|---|
| `voyager` | `{"api_key": "pa-...", "provider": "voyager", "model": "voyage-4"}` | Voyage AI embeddings |
| `openai_embeddings` or `openai` | `{"api_key": "sk-..."}` | OpenAI embeddings |
| `pinecone` | `{"api_key": "pcsk-...", "index_name": "my-index"}` | Pinecone vector store |

### `resolve_credentials()` lookup order

```python
from AI_infrastructure.shared.org_credentials_loader import resolve_credentials

# For embeddings (in _generate_embedding):
cred = (
    resolve_credentials(user_id, 'voyager')
    or resolve_credentials(user_id, 'openai_embeddings')
    or resolve_credentials(user_id, 'openai')
    # fallback: BGE local model (no credential needed)
)
```

4-tier resolution (same as all other tools):
1. `user_platform_credentials` (user's personal)
2. `user_platform_credentials` of parent user (if `is_sub_user=TRUE`)
3. `organisation_platform_credentials` (org vault — most common)
4. `os.getenv()` (legacy, logs a warning)

---

## 10. Common Patterns for AI Agents

### Searching documents
```python
# Correct pattern — is_query=True handles asymmetric encoding automatically
result = pgvector_query_vectors(
    query_text="What does the policy say about refunds?",
    top_k=5,
    threshold=0.6,
    _user_id=user_id
)
for match in result.get('matches', []):
    print(f"[{match['score']:.2f}] {match['filename']} chunk {match['chunk_index']}: {match['text'][:100]}")
```

### Uploading a document programmatically
```python
# Read file content first, then call the tool
with open('/path/to/document.txt') as f:
    text = f.read()

result = pgvector_upload_document(
    text_content=text,
    filename='document.txt',
    file_type='text/plain',
    file_size_bytes=len(text.encode()),
    embedding_provider='local',  # free, no API key needed
    _user_id=user_id
)
print(f"Uploaded: {result['document_id']} ({result['vectors_uploaded']} chunks)")
```

### Listing what's in the org namespace
```python
docs = pgvector_list_documents(_user_id=user_id)
for d in docs.get('documents', []):
    print(f"{d['filename']} — {d['chunks']} chunks, uploaded {d['created_at']}")
```

### Deleting a document
```python
result = pgvector_delete_vectors(document_id='doc_a1b2c3d4', _user_id=user_id)
```

---

## 11. Troubleshooting

### Upload returns 502 Bad Gateway
**Cause 1 — First deployment, model not yet cached:**  
The BGE model needs to download (~440 MB). This takes 30-60s on first deployment. After the first upload completes, the model is cached at `/data/vdb_models/` and all subsequent uploads load in <1s.

**Cause 2 — HuggingFace HEAD requests on cached model (fixed in commit `a62b8f36`):**  
If you see log lines like `INFO:httpx:HTTP Request: HEAD https://huggingface.co/BAAI/bge-base-en-v1.5/...`, the old code is being used. Deploy the latest version which resolves the local snapshot path directly.

**Verification (server logs):**
```
[PGVECTOR] Loading local embedding model from disk path (no HF network calls) → /data/vdb_models/models--BAAI--bge-base-en-v1.5/snapshots/a5beb1e3.../
[PGVECTOR] Local embedding model ready (768 dims).
```

### Upload returns 500 with "Incorrect API key" or "401"
**Cause:** The org vault contains a credential for `openai` or `voyager` with an invalid/revoked key. `resolve_credentials()` finds it and tries to use it, overriding the local BGE fallback.

**Fix:** Select "Local BGE — FREE" in the Vector DB Settings tab. This sets `embedding_provider=local` in the form data, which triggers `force_local=True` in `_generate_embedding()`, skipping all vault lookups.

Alternatively: remove or update the invalid credential in Organisation Settings → Connections.

### Search returns no results despite uploaded documents
**Cause 1 — Threshold too high:** Default is `threshold=0.5`. Try lowering to `0.3` for broader matching.

**Cause 2 — Dimension mismatch (migration not applied):** If documents were uploaded when the column was `vector(1024)` (migration 048), they cannot be searched with the `vector(768)` schema (migration 049). Delete all documents and re-upload.

**Cause 3 — Mixed embedding models:** If some documents were uploaded with OpenAI embeddings and you're now searching with BGE (or vice versa), the cosine similarity will be meaningless. All documents in an org namespace must use the same embedding model. Delete and re-upload with a consistent provider.

**Verification query (run in Supabase SQL editor):**
```sql
SELECT emb_model, emb_provider, COUNT(*) as chunks
FROM ai_infrastructure.org_vector_documents
WHERE org_id = 1  -- replace with your org ID
GROUP BY emb_model, emb_provider;
```
If you see multiple rows with different models, the namespace has mixed embeddings.

### `_get_org_id(user_id)` raises error
**Cause:** The user has no `organisation_id` set. All users should have one after migration 046 backfill. Check:
```sql
SELECT id, organisation_id FROM ai_infrastructure.users WHERE id = <user_id>;
```
If `organisation_id` is NULL, the personal org was not created for this user. Run `create_personal_org(<user_id>)` or manually create one via migration 046 logic.

### `vector(768)` INSERT fails with dimension error
**Cause:** An embedding provider is returning a dimension ≠ 768. 
- Voyage AI lite models return 512 dims — auto-upgrade should handle this (check logs for `Auto-upgrading Voyage model` message)
- `text-embedding-ada-002` returns 1536 dims — only `text-embedding-3-*` models support custom dimensions
- If BGE is somehow producing wrong dims, it means the local model file is corrupt — delete the cache and let it re-download

---

## 12. Deployment Notes

### Render Persistent Disk
The BGE model cache is stored on Render's persistent disk at `/data/vdb_models/`. This disk survives all redeployments. Only the **first-ever** deployment after the disk is mounted needs to download the model.

Required disk space:
- BGE model: ~440 MB
- Remaining available: rest of the 10 GB persistent disk

### Required Python packages (`requirements.txt`)
```
sentence-transformers>=2.6.0   # local BGE model
httpx>=0.23.0,<0.28.0          # prevents OpenAI/httpx proxies kwarg crash
```

### Environment variables (`.env`)
No environment variables are needed for the local BGE model. For API-based providers, credentials come from the org vault (not env vars).

### First-deployment checklist
1. ✅ Migration 044 applied (`org_vector_documents` table + HNSW index)
2. ✅ Migration 049 applied (`vector(768)` column)
3. ✅ Persistent disk mounted at `/data` on Render
4. ⏳ First upload: will take 30-60s while BGE model downloads
5. ✅ Subsequent uploads: <1s (model loaded from local path)
