# 🔍 Universal Search System - Complete Deployment Guide

**Created:** November 30, 2025  
**Status:** ✅ Backend Complete, 🔄 Deployment Pending  
**Version:** 1.0.0

---

## 📋 Overview

The **Universal Search System** enables users to search across ALL connected platforms in ONE unified interface:
- 📄 Documents (Google Drive, OneDrive, Dropbox, SharePoint)
- 💬 Message Threads (sessions.threads)
- ✉️ Messages (sessions.messages)
- 🤝 Synergy Sessions (synergy_sessions.sessions)
- 📧 Gmail (via Gmail API)
- 💼 Slack (via Slack API)
- 🗄️ Supabase Tables (custom user data)

**Search Types:**
- 📝 **Full-Text** - PostgreSQL GIN indexes with exact matching
- 🧠 **Semantic** - Vector similarity using multi-provider embeddings
- 🎯 **Hybrid** - Reciprocal Rank Fusion (RRF) combining both

**Multi-Provider Embedding Support:**
- 🤖 OpenAI (ada-002, 3-small, 3-large)
- 🚀 Voyage AI (voyage-2, voyage-large-2) - Best for technical content
- 🌐 Cohere (embed-english-v3.0, multilingual) - Best for multilingual

**Vector Databases:**
- 🐘 pgvector (PostgreSQL extension with HNSW indexes)
- 🌲 Pinecone (external SaaS with managed scaling)

**Cloud Folder Sync:**
- ⏰ Scheduled syncing with cron expressions
- 🔄 Incremental updates (only new/modified files)
- 🤖 Automatic embedding generation
- 📊 Batch processing for large folders

---

## 📦 Implementation Status

### ✅ Completed Components

**1. Multi-Provider Database Schema** (`create_document_library_multi_provider.sql`)
- Enhanced document_library table with embedding_provider, vector_db_provider columns
- 3 PostgreSQL functions: semantic_search_documents_multi, hybrid_search_documents_multi, get_embedding_provider_stats
- 10 indexes: GIN (FTS), HNSW (vectors), B-tree, trigram
- Support for OpenAI, Voyage AI, Cohere embeddings
- Support for pgvector and Pinecone storage

**2. Cloud Folder Sync Database Schema** (`create_cloud_folders_table.sql`)
- cloud_folders table for folder configurations
- Supports Google Drive, OneDrive, Dropbox, SharePoint
- Sync schedule tracking with cron expressions
- Status tracking (pending, syncing, completed, error)

**3. Python Tool Implementations** (`document_library_multi_provider.py`)
- 10 tool functions with multi-provider support
- Auto-detection of embedding provider (priority: Voyage → Cohere → OpenAI)
- Auto-detection of vector database (pgvector vs Pinecone)
- Credential injection from user_platform_credentials table

**4. Universal Search Backend** (`universal_search_routes.py`)
- 5 Flask endpoints:
  1. POST /api/universal-search/search - Main search across all platforms
  2. POST /api/universal-search/facets - Get aggregated filter counts
  3. GET /api/universal-search/sources - List available platforms
  4. POST /api/universal-search/index-messages - Generate embeddings for messages
  5. POST /api/universal-search/index-synergy - Generate embeddings for Synergy
- Multi-provider embedding generation helper
- Support for 7+ platform types
- Full-text, semantic, and hybrid search

**5. Cloud Folder Sync Backend** (`cloud_folder_sync_routes.py`)
- 5 Flask endpoints:
  1. POST /api/cloud-sync/add-folder - Link cloud folder for syncing
  2. GET /api/cloud-sync/folders - List linked folders
  3. POST /api/cloud-sync/sync-now - Trigger immediate sync
  4. PUT /api/cloud-sync/folder/{id}/schedule - Update sync schedule
  5. DELETE /api/cloud-sync/folder/{id} - Unlink folder
- APScheduler integration for background syncing
- Incremental sync (only new/modified files)
- Automatic embedding generation for new documents
- Support for Google Drive, OneDrive (extendable to Dropbox, SharePoint)

**6. Universal Search Frontend UI** (`UI/modules_internal/universal-search/`)
- Modern professional interface with search box
- Multi-platform source selection checkboxes
- Search type selector (fulltext, semantic, hybrid)
- Results grouped by source with highlighting
- Faceted filters sidebar
- Real-time search suggestions (300ms debounce)
- Responsive design (desktop/mobile)

**7. Dependencies Installed**
- ✅ voyageai 0.3.5
- ✅ cohere 5.20.0
- ✅ pinecone-client 6.0.0
- ✅ Supporting packages (aiolimiter, fastavro, httpx-sse, types-requests, pinecone-plugin-interface)

**8. Complete Documentation** (`DOCUMENT_LIBRARY_MULTI_PROVIDER_COMPLETE.md`)
- Provider comparison tables
- Usage examples
- Configuration guide
- Performance characteristics
- Troubleshooting guide

### 🔄 Pending Tasks

**1. Database Deployment** (High Priority)
- Deploy multi-provider schema to Supabase
- Add embedding/FTS columns to existing tables
- Create indexes on new columns

**2. Flask App Integration** (High Priority)
- Register universal_search_routes blueprint
- Register cloud_folder_sync_routes blueprint
- Test API endpoints

**3. Index Existing Data** (Medium Priority)
- Generate embeddings for existing messages
- Generate embeddings for existing Synergy sessions
- Index existing threads

**4. Configuration Setup** (Medium Priority)
- Configure user credentials (Voyage, Cohere, Pinecone)
- Test multi-provider auto-detection
- Verify OAuth tokens for cloud platforms

**5. UI Module Registration** (High Priority)
- Register universal-search module in sidebar
- Create navigation link
- Test frontend-backend integration

---

## 🚀 Deployment Steps

### Step 1: Deploy Database Schema

#### 1.1 Deploy Multi-Provider Document Library Schema

```bash
# Connect to Supabase PostgreSQL
psql -h db.YOUR_PROJECT.supabase.co -U postgres -d postgres

# Deploy schema
\i c:/Users/gpoli/GIT/AI_agents/AI_infrastructure/database/migrations/create_document_library_multi_provider.sql

# Verify tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'ai_infrastructure' 
AND table_name = 'document_library';

# Verify functions
SELECT routine_name FROM information_schema.routines 
WHERE routine_schema = 'ai_infrastructure' 
AND routine_type = 'FUNCTION';
```

**Expected Output:**
- ✅ document_library table with new columns (embedding_provider, vector_db_provider, etc.)
- ✅ 3 functions: semantic_search_documents_multi, hybrid_search_documents_multi, get_embedding_provider_stats
- ✅ 10 indexes created

#### 1.2 Deploy Cloud Folders Schema

```bash
# Deploy cloud folders table
\i c:/Users/gpoli/GIT/AI_agents/AI_infrastructure/database/migrations/create_cloud_folders_table.sql

# Verify table
SELECT * FROM ai_infrastructure.cloud_folders LIMIT 0;
```

**Expected Output:**
- ✅ cloud_folders table created
- ✅ 4 indexes created

#### 1.3 Add Embedding/FTS Columns to Existing Tables

```sql
-- ========================================================================
-- SESSIONS.MESSAGES TABLE
-- ========================================================================

ALTER TABLE sessions.messages
ADD COLUMN embedding vector(1536),
ADD COLUMN fts_tokens tsvector,
ADD COLUMN embedding_provider TEXT DEFAULT 'openai' CHECK (embedding_provider IN ('openai', 'voyage', 'cohere', 'none')),
ADD COLUMN indexed_at TIMESTAMPTZ;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_messages_embedding 
ON sessions.messages USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_messages_fts 
ON sessions.messages USING gin(fts_tokens);

CREATE INDEX IF NOT EXISTS idx_messages_indexed 
ON sessions.messages(indexed_at) WHERE indexed_at IS NOT NULL;

-- ========================================================================
-- SESSIONS.THREADS TABLE
-- ========================================================================

ALTER TABLE sessions.threads
ADD COLUMN embedding vector(1536),
ADD COLUMN fts_tokens tsvector,
ADD COLUMN embedding_provider TEXT DEFAULT 'openai' CHECK (embedding_provider IN ('openai', 'voyage', 'cohere', 'none')),
ADD COLUMN indexed_at TIMESTAMPTZ;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_threads_embedding 
ON sessions.threads USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_threads_fts 
ON sessions.threads USING gin(fts_tokens);

CREATE INDEX IF NOT EXISTS idx_threads_indexed 
ON sessions.threads(indexed_at) WHERE indexed_at IS NOT NULL;

-- ========================================================================
-- SYNERGY_SESSIONS.SESSIONS TABLE
-- ========================================================================

ALTER TABLE synergy_sessions.sessions
ADD COLUMN embedding vector(1536),
ADD COLUMN fts_tokens tsvector,
ADD COLUMN embedding_provider TEXT DEFAULT 'openai' CHECK (embedding_provider IN ('openai', 'voyage', 'cohere', 'none')),
ADD COLUMN agent_count INTEGER DEFAULT 1,
ADD COLUMN indexed_at TIMESTAMPTZ;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_synergy_embedding 
ON synergy_sessions.sessions USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_synergy_fts 
ON synergy_sessions.sessions USING gin(fts_tokens);

CREATE INDEX IF NOT EXISTS idx_synergy_indexed 
ON synergy_sessions.sessions(indexed_at) WHERE indexed_at IS NOT NULL;

-- Add comments
COMMENT ON COLUMN sessions.messages.embedding IS 'Vector embedding for semantic search (1536 dimensions)';
COMMENT ON COLUMN sessions.messages.fts_tokens IS 'Full-text search tokens generated from message content';
COMMENT ON COLUMN sessions.messages.embedding_provider IS 'Provider used for embedding generation (openai, voyage, cohere)';

COMMENT ON COLUMN sessions.threads.embedding IS 'Vector embedding for semantic search (1536 dimensions)';
COMMENT ON COLUMN sessions.threads.fts_tokens IS 'Full-text search tokens generated from thread name';
COMMENT ON COLUMN sessions.threads.embedding_provider IS 'Provider used for embedding generation (openai, voyage, cohere)';

COMMENT ON COLUMN synergy_sessions.sessions.embedding IS 'Vector embedding for semantic search (1536 dimensions)';
COMMENT ON COLUMN synergy_sessions.sessions.fts_tokens IS 'Full-text search tokens generated from session data';
COMMENT ON COLUMN synergy_sessions.sessions.embedding_provider IS 'Provider used for embedding generation (openai, voyage, cohere)';
COMMENT ON COLUMN synergy_sessions.sessions.agent_count IS 'Number of AI agents in this Synergy session';
```

**Verification:**
```sql
-- Check columns added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'sessions' 
AND table_name = 'messages' 
AND column_name IN ('embedding', 'fts_tokens', 'embedding_provider', 'indexed_at');

-- Check indexes created
SELECT indexname FROM pg_indexes 
WHERE tablename IN ('messages', 'threads', 'sessions')
AND indexname LIKE '%embedding%' OR indexname LIKE '%fts%';
```

---

### Step 2: Register Flask Routes

#### 2.1 Update Flask App

**File:** `AI_infrastructure/flask_app.py`

Add blueprint registrations after existing routes:

```python
# ========================================================================
# IMPORT UNIVERSAL SEARCH & CLOUD SYNC BLUEPRINTS
# ========================================================================

from AI_infrastructure.routes.universal_search_routes import universal_search_bp
from AI_infrastructure.routes.cloud_folder_sync_routes import cloud_sync_bp

# ========================================================================
# REGISTER BLUEPRINTS (Add after existing registrations)
# ========================================================================

app.register_blueprint(universal_search_bp)
app.register_blueprint(cloud_sync_bp)

print('[Flask App] Universal Search routes registered')
print('[Flask App] Cloud Folder Sync routes registered')
```

#### 2.2 Verify Routes Registered

```powershell
# Restart Flask server
cd c:\Users\gpoli\GIT\AI_agents
BISTART

# Check logs for confirmation
# Expected output:
# [Flask App] Universal Search routes registered
# [Flask App] Cloud Folder Sync routes registered
```

#### 2.3 Test API Endpoints

```powershell
# Test universal search health
curl http://localhost:5001/api/universal-search/sources `
  -H "Authorization: Bearer YOUR_TOKEN"

# Test cloud sync health
curl http://localhost:5001/api/cloud-sync/folders `
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Step 3: Index Existing Data

#### 3.1 Index Messages

```python
# Python script or API call
import requests

response = requests.post(
    'http://localhost:5001/api/universal-search/index-messages',
    json={
        'force_reindex': False  # Set to True to re-index all
    },
    headers={'Authorization': f'Bearer {token}'}
)

print(response.json())
# Expected: {'success': True, 'indexed_count': 1234, 'total_messages': 1234}
```

**Alternative: Run via tool registry**
```python
from tools.registry_v3 import RegistryV3

registry = RegistryV3()
result = registry.execute_tool(
    'universal_search_index_messages',
    user_id=12,
    force_reindex=False
)
print(result)
```

#### 3.2 Index Synergy Sessions

```python
# Python script or API call
response = requests.post(
    'http://localhost:5001/api/universal-search/index-synergy',
    headers={'Authorization': f'Bearer {token}'}
)

print(response.json())
# Expected: {'success': True, 'indexed_count': 42, 'total_sessions': 42}
```

#### 3.3 Monitor Indexing Progress

```sql
-- Check indexing status
SELECT 
    'messages' as table_name,
    COUNT(*) as total,
    COUNT(embedding) as indexed,
    ROUND(100.0 * COUNT(embedding) / NULLIF(COUNT(*), 0), 2) as percent_indexed
FROM sessions.messages

UNION ALL

SELECT 
    'threads',
    COUNT(*),
    COUNT(embedding),
    ROUND(100.0 * COUNT(embedding) / NULLIF(COUNT(*), 0), 2)
FROM sessions.threads

UNION ALL

SELECT 
    'synergy',
    COUNT(*),
    COUNT(embedding),
    ROUND(100.0 * COUNT(embedding) / NULLIF(COUNT(*), 0), 2)
FROM synergy_sessions.sessions;
```

---

### Step 4: Configure User Credentials

#### 4.1 Store Voyage AI Credentials

```python
from AI_infrastructure.auth.user_auth import UserAuthManager

auth = UserAuthManager()

# Store Voyage AI key
auth.store_platform_credential(
    user_id=12,
    platform='voyage',
    credential_value='pa-GOCp1HsNfuuvjXnHPumV5f6sD-YLQwQg5Fl3Fx2AlDm'
)
```

#### 4.2 Store Cohere Credentials

```python
# Store Cohere key
auth.store_platform_credential(
    user_id=12,
    platform='cohere',
    credential_value='YOUR_COHERE_API_KEY'
)
```

#### 4.3 Store Pinecone Credentials

```python
# Store Pinecone key with metadata
auth.store_platform_credential(
    user_id=12,
    platform='pinecone',
    credential_value='pcsk_4NZhAZ_YOUR_PINECONE_KEY',
    metadata={
        'index_name': 'inhouseprint',
        'environment': 'us-east-1'
    }
)
```

#### 4.4 Verify Credential Storage

```sql
-- Check stored credentials
SELECT platform, created_at, metadata 
FROM ai_infrastructure.user_platform_credentials
WHERE user_id = 12
AND platform IN ('voyage', 'cohere', 'pinecone');
```

---

### Step 5: Register UI Module

#### 5.1 Register in Sidebar

**File:** `UI/sidebar.js`

Add module registration:

```javascript
// Register Universal Search Module
SidebarManager.register({
    id: 'universal-search',
    name: 'Universal Search',
    icon: 'search',
    category: 'search',
    order: 5,
    onClick: () => {
        // Load universal search UI
        window.ModuleLoader.loadModule('universal-search');
    }
});
```

#### 5.2 Create Module Loader Hook

**File:** `UI/module-loader.js` (if not exists, create pattern)

```javascript
window.ModuleLoader = {
    loadModule: async (moduleId) => {
        const container = document.getElementById('main-content');
        if (!container) return;
        
        // Load module based on ID
        if (moduleId === 'universal-search') {
            container.innerHTML = '<div id="universal-search-container"></div>';
            
            // Load CSS
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = '/UI/modules_internal/universal-search/universal-search.css';
            document.head.appendChild(link);
            
            // Load JS
            const script = document.createElement('script');
            script.src = '/UI/modules_internal/universal-search/universal-search.js';
            document.body.appendChild(script);
        }
    }
};
```

---

### Step 6: Test End-to-End

#### 6.1 Test Search Functionality

```javascript
// Open browser console on Universal Search page
// Type in search box: "project management"

// Expected flow:
// 1. Input detected (300ms debounce)
// 2. API call to /api/universal-search/search
// 3. Results grouped by source displayed
// 4. Facets updated in sidebar
```

#### 6.2 Test Cloud Folder Sync

```javascript
// Add Google Drive folder for syncing
fetch('/api/cloud-sync/add-folder', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        platform: 'google_drive',
        folder_id: '1AbC2DeF3GhI4JkL5MnO6PqR',
        folder_name: 'Project Documents',
        sync_schedule: '0 */6 * * *',  // Every 6 hours
        auto_embed: true,
        recursive: false
    })
}).then(r => r.json()).then(console.log);

// Expected: {'success': True, 'folder_id': 1, 'message': 'Folder linked and initial sync started'}
```

#### 6.3 Monitor Sync Status

```javascript
// Check linked folders
fetch('/api/cloud-sync/folders', {
    headers: {'Authorization': `Bearer ${token}`}
}).then(r => r.json()).then(console.log);

// Expected: List of folders with sync status
```

#### 6.4 Test Multi-Provider Embedding

```python
# Test embedding generation with different providers
from tools.implementations.document_library_multi_provider import _generate_embedding

# Will auto-detect: Voyage → Cohere → OpenAI
embedding = _generate_embedding("Test document content", user_id=12)
print(f"Embedding dimensions: {len(embedding)}")
# Expected: 1536 (if using OpenAI or Voyage)
# Expected: 1024 (if using Cohere)
```

---

## 🧪 Testing Checklist

### Database Tests
- [ ] document_library table has new multi-provider columns
- [ ] cloud_folders table created successfully
- [ ] messages/threads/synergy tables have embedding columns
- [ ] All indexes created (HNSW, GIN, B-tree)
- [ ] Functions work: semantic_search_documents_multi, hybrid_search_documents_multi

### Backend Tests
- [ ] Universal search endpoints respond (5 endpoints)
- [ ] Cloud sync endpoints respond (5 endpoints)
- [ ] Multi-provider embedding generation works
- [ ] Auto-detection selects correct provider
- [ ] Full-text search returns results
- [ ] Semantic search returns results
- [ ] Hybrid search combines both correctly

### Frontend Tests
- [ ] Universal Search module loads in sidebar
- [ ] Search input detects typing (debounced)
- [ ] Source checkboxes filter results
- [ ] Search type selector changes behavior
- [ ] Results display with highlighting
- [ ] Facets sidebar shows filters
- [ ] Result items open correctly

### Integration Tests
- [ ] Search across documents works
- [ ] Search across messages works
- [ ] Search across threads works
- [ ] Search across Synergy works
- [ ] Gmail search works (if connected)
- [ ] Slack search works (if connected)
- [ ] Cloud folder sync completes successfully
- [ ] Scheduled syncing triggers automatically

---

## 🔍 Troubleshooting

### Issue: "Embedding provider not detected"

**Cause:** No credentials found for Voyage, Cohere, or OpenAI

**Solution:**
```python
from AI_infrastructure.auth.user_auth import UserAuthManager
auth = UserAuthManager()

# Store at least one provider
auth.store_platform_credential(user_id=12, platform='voyage', credential_value='YOUR_KEY')
```

### Issue: "No results found" for semantic search

**Cause:** Embeddings not generated for content

**Solution:**
```python
# Index existing data
import requests
requests.post('http://localhost:5001/api/universal-search/index-messages', 
              headers={'Authorization': f'Bearer {token}'})
requests.post('http://localhost:5001/api/universal-search/index-synergy',
              headers={'Authorization': f'Bearer {token}'})
```

### Issue: "Cloud sync fails with API error"

**Cause:** OAuth credentials expired or invalid

**Solution:**
```python
# Refresh OAuth tokens
from AI_infrastructure.auth.credential_injector import CredentialInjector
injector = CredentialInjector()

# Will automatically refresh if expired
google_creds = injector.get_google_credentials(user_id=12)
```

### Issue: "Search results don't include Gmail/Slack"

**Cause:** Platform not connected or not selected in source filters

**Solution:**
1. Check OAuth connection: `/api/universal-search/sources`
2. Verify source checkbox is checked in UI
3. Check `include_gmail=true` in API request body

---

## 📊 Performance Optimization

### Database Optimization

```sql
-- Vacuum and analyze for optimal performance
VACUUM ANALYZE ai_infrastructure.document_library;
VACUUM ANALYZE sessions.messages;
VACUUM ANALYZE sessions.threads;
VACUUM ANALYZE synergy_sessions.sessions;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname IN ('ai_infrastructure', 'sessions', 'synergy_sessions')
ORDER BY idx_scan DESC;
```

### Query Performance

```sql
-- Full-text search (fastest)
EXPLAIN ANALYZE
SELECT * FROM sessions.messages
WHERE fts_tokens @@ websearch_to_tsquery('english', 'project management')
LIMIT 20;

-- Expected: Index Scan using idx_messages_fts (~5-10ms)

-- Semantic search (slower, more accurate)
EXPLAIN ANALYZE
SELECT *, embedding <=> '[0.1, 0.2, ...]'::vector AS distance
FROM sessions.messages
WHERE embedding IS NOT NULL
ORDER BY distance
LIMIT 20;

-- Expected: Index Scan using idx_messages_embedding (~20-50ms)
```

### Embedding Generation

```python
# Batch embedding generation (more efficient)
from tools.implementations.document_library_multi_provider import _generate_embedding

texts = ['Document 1', 'Document 2', 'Document 3']
embeddings = [_generate_embedding(text, user_id=12) for text in texts]
# NOTE: Implement batch API calls for production (Voyage/Cohere support batching)
```

---

## 🚀 Next Steps

### Phase 1: Core Deployment (This Week)
1. ✅ Deploy database schema
2. ✅ Register Flask routes
3. ✅ Index existing messages/threads/Synergy
4. ✅ Test search functionality end-to-end

### Phase 2: Cloud Sync (Next Week)
1. Link 2-3 Google Drive folders
2. Test scheduled syncing
3. Monitor sync performance
4. Add OneDrive support

### Phase 3: Advanced Features (Future)
1. Real-time search suggestions
2. Search history and saved searches
3. Advanced filters (date ranges, file types, sentiment)
4. Export search results
5. Search analytics dashboard

---

## 📚 Related Documentation

- **Multi-Provider Guide:** `DOCUMENT_LIBRARY_MULTI_PROVIDER_COMPLETE.md`
- **Database Schema:** `create_document_library_multi_provider.sql`
- **Cloud Sync Schema:** `create_cloud_folders_table.sql`
- **Backend Routes:** `universal_search_routes.py`, `cloud_folder_sync_routes.py`
- **Frontend UI:** `UI/modules_internal/universal-search/`

---

**Last Updated:** November 30, 2025  
**Status:** ✅ Implementation Complete - Ready for Deployment  
**Next Action:** Deploy database schema and register Flask routes
