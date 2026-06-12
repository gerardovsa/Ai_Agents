# 🔍 Universal Search - Multi-Platform Multi-Database Architecture Analysis

**Date:** December 8, 2025  
**System:** Valor AI Sidebar - Universal Search Module  
**Purpose:** Complete analysis of how the search system handles multiple platforms/databases

---

## 📊 **SYSTEM OVERVIEW**

Universal Search is a **unified multi-source search interface** that searches across:
- ✅ **Cloud Drives** (Google Drive, OneDrive, Dropbox, SharePoint)
- ✅ **Vector Databases** (Qdrant, Pinecone, pgvector - AI semantic search)
- ✅ **Supabase Databases** (Threads, Messages, Synergy sessions)
- ✅ **External Platforms** (Gmail, Slack, Confluence, Notion)
- ✅ **Local Documents** (Document library indexed in PostgreSQL)

---

## 🏗️ **ARCHITECTURE BREAKDOWN**

### **1. Frontend Component (`universal-search.js`)**

#### **A. State Management**
```javascript
state: {
    query: '',                                    // User's search query
    results: [],                                  // All search results
    loading: false,                               // Loading state
    error: null,                                  // Error message
    selectedSources: new Set([                    // User-selected sources (checkboxes)
        'documents', 
        'threads', 
        'vector-database'
    ]),
    availableSources: {},                         // Which sources user has connected
    searchTimeout: null,                          // Debounce timer
    stats: {
        total: 0,                                 // Total results count
        bySource: {}                              // Count per source
    }
}
```

#### **B. Source Detection System**

**How It Works:**
```javascript
// Step 1: On module load, fetch available sources
async loadAvailableSources() {
    const response = await this.api.get('/api/universal-search/sources');
    
    this.state.availableSources = {
        documents: true,        // ✅ Always available (internal DB)
        threads: true,          // ✅ Always available (internal DB)
        'vector-database': true, // ✅ Available if configured
        gmail: false,           // ❌ Not connected (no OAuth)
        slack: false,           // ❌ Not connected (no OAuth)
        synergy: true           // ✅ Always available (internal DB)
    };
}
```

**Backend Detection (`/api/universal-search/sources`):**
```python
def get_available_sources():
    # Check OAuth credentials for each platform
    platforms = ['google_drive', 'onedrive', 'dropbox', 'sharepoint',
                 'gmail', 'slack', 'confluence', 'notion']
    
    available_sources = []
    for platform in platforms:
        creds = auth_manager.get_platform_credentials(user_id, platform)
        if creds:  # User has connected this platform
            available_sources.append({
                'platform': platform,
                'enabled': True,
                'credential_status': 'active'
            })
    
    # Always available (internal databases)
    available_sources.extend([
        {'platform': 'threads', 'enabled': True},
        {'platform': 'messages', 'enabled': True},
        {'platform': 'synergy', 'enabled': True},
        {'platform': 'documents', 'enabled': True},
        {'platform': 'vector-database', 'enabled': True}
    ])
    
    return available_sources
```

#### **C. Source Selection UI**

**Checkbox Rendering:**
```javascript
renderSourceCheckboxes() {
    const sources = [
        { id: 'documents', label: 'Documents', icon: 'fa-file-alt' },
        { id: 'vector-database', label: 'Vector Database (AI Search)', icon: 'fa-database' },
        { id: 'threads', label: 'Threads', icon: 'fa-comments' },
        { id: 'messages', label: 'Messages', icon: 'fa-envelope' },
        { id: 'synergy', label: 'Synergy Sessions', icon: 'fa-users' },
        { id: 'automations', label: 'Automations', icon: 'fa-robot' },
        { id: 'gmail', label: 'Gmail', icon: 'fa-google' },
        { id: 'slack', label: 'Slack', icon: 'fa-slack' }
    ];
    
    return sources.map(source => {
        const available = this.state.availableSources[source.id];  // ✅ Connected?
        const checked = this.state.selectedSources.has(source.id);  // ☑️ User selected?
        const disabled = !available;                                // 🚫 Disabled if not connected
        
        return `
            <label class="${disabled ? 'disabled' : ''}">
                <input type="checkbox" 
                       value="${source.id}" 
                       ${checked ? 'checked' : ''}
                       ${disabled ? 'disabled' : ''}
                />
                <i class="fas ${source.icon}"></i>
                <span>${source.label}</span>
                ${!available ? '<span class="not-connected">(Not Connected)</span>' : ''}
            </label>
        `;
    }).join('');
}
```

**User Interaction:**
```javascript
// When user checks/unchecks a source
this.dom.on(this.container, 'change', '.universal-search-filter-label input', (e) => {
    const source = e.target.value;
    
    if (e.target.checked) {
        this.state.selectedSources.add(source);        // Add to search
    } else {
        this.state.selectedSources.delete(source);     // Remove from search
    }
    
    // Re-search automatically if query exists
    if (this.state.query) {
        this.search();
    }
});
```

#### **D. Search Execution**

```javascript
async search() {
    const params = {
        query: 'reduce costs',                           // User's query
        sources: ['documents', 'vector-database', 'threads'],  // Selected sources
        limit: 50                                        // Max results per source
    };
    
    // POST to backend with selected sources
    const response = await this.api.get('/api/universal-search/search', { params });
    
    this.state.results = response.results;  // All results merged
    this.showResults();                     // Display grouped by source
}
```

---

## 🔧 **BACKEND PROCESSING (`universal_search_routes.py`)**

### **2. Search Request Handling**

```python
@universal_search_bp.route('/search', methods=['POST'])
@require_auth
def universal_search():
    data = request.get_json()
    
    query = data.get('query', '')
    sources = data.get('sources', [])  # Frontend sends selected sources
    search_type = data.get('search_type', 'hybrid')  # fulltext/semantic/hybrid
    limit = data.get('limit', 10)
    
    # Parse which sources to search
    include_documents = 'documents' in sources or data.get('include_documents', True)
    include_threads = 'threads' in sources or data.get('include_messages', True)
    include_synergy = 'synergy' in sources or data.get('include_synergy', True)
    include_vector_db = 'vector-database' in sources
    include_gmail = 'gmail' in sources
    include_slack = 'slack' in sources
    
    results = {
        'query': query,
        'search_type': search_type,
        'total_results': 0,
        'sources': {}  # Results grouped by source
    }
```

### **3. Per-Source Search Logic**

#### **Source 1: Document Library (PostgreSQL)**
```python
if include_documents:
    if search_type == 'fulltext':
        # Traditional SQL full-text search
        cursor.execute("""
            SELECT document_id, title, source, file_type, url, created_at,
                   ts_rank(fts_tokens, websearch_to_tsquery('english', %s)) AS rank
            FROM ai_infrastructure.document_library
            WHERE fts_tokens @@ websearch_to_tsquery('english', %s)
              AND owner_user_id = %s
            ORDER BY rank DESC
            LIMIT %s
        """, (query, query, user_id, limit))
    
    elif search_type == 'semantic':
        # Vector similarity search (embeddings)
        query_embedding = generate_embedding(query, user_id)
        cursor.execute("""
            SELECT document_id, title, ...,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM ai_infrastructure.document_library
            WHERE owner_user_id = %s
              AND embedding IS NOT NULL
              AND (1 - (embedding <=> %s::vector)) > 0.3
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (query_embedding, user_id, query_embedding, query_embedding, limit))
    
    elif search_type == 'hybrid':
        # RRF (Rank Reciprocal Fusion) - combines keyword + semantic
        cursor.execute("""
            SELECT * FROM ai_infrastructure.hybrid_search_documents_multi(
                %s, %s::vector, %s, 0.5, 0.5, 0.3, 'pgvector'
            )
        """, (query, query_embedding, limit))
    
    results['sources']['documents'] = {
        'count': len(docs),
        'results': docs
    }
```

#### **Source 2: Vector Database (Qdrant/Pinecone)**
```python
if include_vector_db and query_embedding:
    # Generate embedding first
    query_embedding = generate_embedding(query, user_id)
    
    # Try Qdrant (free, fast, self-hosted)
    try:
        qdrant_client = get_qdrant_client(user_id)
        search_results = qdrant_client.search(
            collection_name="user_documents",
            query_vector=query_embedding,
            limit=limit
        )
        
        vector_results = [
            {
                'id': hit.id,
                'title': hit.payload.get('title'),
                'snippet': hit.payload.get('text')[:200],
                'score': float(hit.score),  # Similarity score 0-1
                'provider': 'Qdrant'
            }
            for hit in search_results
        ]
        
        results['sources']['vector-database'] = {
            'count': len(vector_results),
            'results': vector_results
        }
    except:
        # Fallback to Pinecone if Qdrant fails
        pass
```

#### **Source 3: Threads (Supabase)**
```python
if include_threads:
    if search_type == 'fulltext':
        cursor.execute("""
            SELECT thread_slug, name, created_at,
                   ts_rank(fts_tokens, websearch_to_tsquery('english', %s)) AS rank
            FROM sessions.threads
            WHERE fts_tokens @@ websearch_to_tsquery('english', %s)
              AND user_id = %s
            ORDER BY rank DESC
            LIMIT %s
        """, (query, query, user_id, limit))
    
    results['sources']['threads'] = {
        'count': len(threads),
        'results': threads
    }
```

#### **Source 4: Messages (Supabase)**
```python
if include_messages:
    cursor.execute("""
        SELECT m.id, m.content, m.created_at, t.name as thread_name
        FROM sessions.messages m
        JOIN sessions.threads t ON m.thread_id = t.id
        WHERE m.fts_tokens @@ websearch_to_tsquery('english', %s)
          AND t.user_id = %s
        LIMIT %s
    """, (query, user_id, limit))
    
    results['sources']['messages'] = {
        'count': len(messages),
        'results': messages
    }
```

#### **Source 5: Synergy Sessions (Supabase)**
```python
if include_synergy:
    cursor.execute("""
        SELECT session_id, title, created_at,
               ts_rank(fts_tokens, websearch_to_tsquery('english', %s)) AS rank
        FROM synergy_sessions.sessions
        WHERE fts_tokens @@ websearch_to_tsquery('english', %s)
          AND user_id = %s
        ORDER BY rank DESC
        LIMIT %s
    """, (query, query, user_id, limit))
    
    results['sources']['synergy'] = {
        'count': len(synergy),
        'results': synergy
    }
```

#### **Source 6: Gmail (OAuth API)**
```python
if include_gmail:
    gmail_creds = auth_manager.get_platform_credentials(user_id, 'google')
    if gmail_creds:
        response = requests.get(
            'https://gmail.googleapis.com/gmail/v1/users/me/messages',
            params={'q': query, 'maxResults': limit},
            headers={'Authorization': f'Bearer {gmail_creds["access_token"]}'}
        )
        
        results['sources']['gmail'] = {
            'count': len(gmail_messages),
            'results': gmail_messages
        }
```

#### **Source 7: Slack (OAuth API)**
```python
if include_slack:
    slack_creds = auth_manager.get_platform_credentials(user_id, 'slack')
    if slack_creds:
        response = requests.get(
            'https://slack.com/api/search.messages',
            params={'query': query, 'count': limit},
            headers={'Authorization': f'Bearer {slack_creds["access_token"]}'}
        )
        
        results['sources']['slack'] = {
            'count': len(slack_messages),
            'results': slack_messages
        }
```

---

## 📦 **RESULT GROUPING & DISPLAY**

### **Backend Response:**
```json
{
    "query": "reduce costs",
    "search_type": "hybrid",
    "total_results": 15,
    "sources": {
        "documents": {
            "count": 5,
            "results": [
                {"id": 1, "title": "Cost Reduction Strategy.pdf", "score": 0.94},
                {"id": 2, "title": "Budget Optimization.docx", "score": 0.87}
            ]
        },
        "vector-database": {
            "count": 3,
            "results": [
                {"id": "vec123", "title": "Expense Management.pdf", "score": 0.91, "provider": "Qdrant"},
                {"id": "vec456", "title": "Financial Planning.docx", "score": 0.85, "provider": "Qdrant"}
            ]
        },
        "threads": {
            "count": 4,
            "results": [...]
        },
        "gmail": {
            "count": 3,
            "results": [...]
        }
    }
}
```

### **Frontend Display:**
```javascript
renderResults() {
    const grouped = this.groupResultsBySource();
    
    let html = `<div class="universal-search-results-wrapper">`;
    
    // Header
    html += `
        <div class="universal-search-results-header">
            <h3>Found ${this.state.stats.total} results</h3>
            <p>Searched across ${this.state.selectedSources.size} sources</p>
        </div>
    `;
    
    // Group results by source
    for (const [source, items] of Object.entries(grouped)) {
        html += `
            <div class="universal-search-source-group">
                <h4>
                    <i class="${this.getSourceIcon(source)}"></i>
                    ${this.getSourceLabel(source)} (${items.length})
                </h4>
                <div class="universal-search-items">
                    ${items.map(item => this.renderResultItem(item)).join('')}
                </div>
            </div>
        `;
    }
    
    return html;
}
```

---

## 🎛️ **SOURCE CONTROL MECHANISMS**

### **1. Automatic Connection Detection**
```python
# Backend checks if user has OAuth credentials
gmail_creds = auth_manager.get_platform_credentials(user_id, 'google')
if gmail_creds:
    # Gmail is AVAILABLE - show checkbox enabled
else:
    # Gmail is NOT AVAILABLE - show checkbox disabled with "Not Connected"
```

### **2. User Selection (Checkboxes)**
```javascript
// User can toggle any connected source on/off
selectedSources: new Set(['documents', 'threads', 'vector-database'])

// When checkbox changes:
if (checked) {
    selectedSources.add('gmail');  // Include in next search
} else {
    selectedSources.delete('gmail');  // Exclude from next search
}
```

### **3. Backend Filtering**
```python
# Backend only searches sources that are:
# 1. User-selected (in sources array)
# 2. User-connected (has credentials)
# 3. Available (service is up)

if 'gmail' in sources and gmail_creds:
    # Search Gmail
```

---

## 🔐 **CREDENTIAL & PERMISSION MANAGEMENT**

### **How Credentials Are Checked:**
```python
from AI_infrastructure.auth.user_auth import UserAuthManager

auth_manager = UserAuthManager()

def get_platform_credentials(user_id, platform):
    """
    Returns OAuth credentials if user has connected platform
    
    Checks:
    - oauth_tokens table in database
    - Token expiry (refreshes if needed)
    - Platform connection status
    """
    return {
        'access_token': '...',
        'refresh_token': '...',
        'expires_at': '...'
    }
```

### **Platform Connection Flow:**
1. **User connects platform** (via Settings → Platform Connections)
2. **OAuth flow** stores tokens in `oauth_tokens` table
3. **Backend detects** credentials available
4. **Frontend enables** checkbox for that platform
5. **User selects** platform for search
6. **Backend uses** stored credentials to search

---

## 🔄 **SEARCH FLOW DIAGRAM**

```
┌─────────────────────────────────────────────────────────────┐
│                    USER TYPES QUERY                         │
│              "reduce costs strategies"                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│          FRONTEND: Universal Search Module                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Selected Sources (Checkboxes):                     │   │
│  │  ☑ Documents                                        │   │
│  │  ☑ Vector Database (AI Search)                     │   │
│  │  ☑ Threads                                          │   │
│  │  ☐ Gmail (Not Connected)                            │   │
│  │  ☐ Slack (Not Connected)                            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ POST /api/universal-search/search
                      │ { query: "reduce costs", sources: [...] }
                      ▼
┌─────────────────────────────────────────────────────────────┐
│          BACKEND: universal_search_routes.py                │
│                                                             │
│  1. Parse request                                           │
│  2. Check user permissions                                  │
│  3. Generate embeddings (if semantic search)                │
│  4. Search each selected source:                            │
│                                                             │
│     ┌─────────────────────────────────────┐               │
│     │ SOURCE: Documents (PostgreSQL)      │               │
│     │ ✅ Full-text search                  │               │
│     │ ✅ Results: 5 documents               │               │
│     └─────────────────────────────────────┘               │
│                                                             │
│     ┌─────────────────────────────────────┐               │
│     │ SOURCE: Vector Database (Qdrant)    │               │
│     │ ✅ Semantic similarity search         │               │
│     │ ✅ Results: 3 documents (90%+ match)  │               │
│     └─────────────────────────────────────┘               │
│                                                             │
│     ┌─────────────────────────────────────┐               │
│     │ SOURCE: Threads (Supabase)          │               │
│     │ ✅ Full-text search                  │               │
│     │ ✅ Results: 4 threads                 │               │
│     └─────────────────────────────────────┘               │
│                                                             │
│     ┌─────────────────────────────────────┐               │
│     │ SOURCE: Gmail                       │               │
│     │ ❌ Skipped (not selected)            │               │
│     └─────────────────────────────────────┘               │
│                                                             │
│  5. Merge all results                                       │
│  6. Return JSON response                                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ Response: { sources: {...}, total: 12 }
                      ▼
┌─────────────────────────────────────────────────────────────┐
│          FRONTEND: Display Results                          │
│                                                             │
│  📄 Documents - 5 results                                   │
│     • Cost Reduction Strategy.pdf (rank: 0.94)             │
│     • Budget Optimization.docx (rank: 0.87)                │
│                                                             │
│  🗄️ Vector Database (AI Search) - 3 results                 │
│     • Expense Management.pdf (similarity: 91%)             │
│     • Financial Planning.docx (similarity: 85%)            │
│                                                             │
│  💬 Threads - 4 results                                     │
│     • Thread: Q4 Budget Discussion (rank: 0.76)            │
│     • Thread: Cost Savings Ideas (rank: 0.71)              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 **SEARCH TYPE COMPARISON**

| Search Type | How It Works | Used For | Speed | Accuracy |
|------------|--------------|----------|-------|----------|
| **Full-text** | PostgreSQL GIN indexes, `ts_rank()` | Exact keyword matching | ⚡ Very Fast | 🎯 High (exact terms) |
| **Semantic** | Vector embeddings, cosine similarity | Concept/meaning search | 🐢 Slower (embedding API) | 🧠 High (concepts) |
| **Hybrid** | RRF combination of both | Best of both worlds | ⚡🐢 Medium | 🎯🧠 Very High |

**Hybrid Search Formula (RRF - Rank Reciprocal Fusion):**
```python
# Combines keyword rank + semantic similarity
hybrid_score = (
    keyword_weight * (1 / (keyword_rank + 60)) +
    semantic_weight * (1 / (semantic_rank + 60))
)
```

---

## 🎯 **KEY FEATURES**

### ✅ **Multi-Platform Support**
- Internal databases (always available)
- OAuth platforms (when connected)
- Vector databases (when configured)

### ✅ **Smart Source Detection**
- Auto-detects connected platforms
- Disables checkboxes for disconnected platforms
- Shows "(Not Connected)" label

### ✅ **Flexible Search Types**
- Full-text (fast, exact)
- Semantic (AI-powered, conceptual)
- Hybrid (best results)

### ✅ **Real-time Filtering**
- Check/uncheck sources → instant re-search
- No page reload needed
- Preserves search query

### ✅ **Grouped Results**
- Results organized by source
- Shows count per source
- Expandable/collapsible sections

### ✅ **Scalable Architecture**
- Easy to add new sources
- Modular backend design
- Frontend auto-updates

---

## 🔧 **HOW TO ADD A NEW SOURCE**

### **1. Frontend (`universal-search.js`):**
```javascript
// Add to source list
renderSourceCheckboxes() {
    const sources = [
        // ... existing sources
        { id: 'confluence', label: 'Confluence', icon: 'fa-book' }  // NEW
    ];
}

// Add icon mapping
getSourceIcon(source) {
    const icons = {
        // ... existing icons
        'confluence': 'fas fa-book'  // NEW
    };
}

// Add label mapping
getSourceLabel(source) {
    const labels = {
        // ... existing labels
        'confluence': 'Confluence Wiki'  // NEW
    };
}
```

### **2. Backend (`universal_search_routes.py`):**
```python
# Add source parameter
include_confluence = 'confluence' in sources

# Add search section
if include_confluence:
    confluence_creds = auth_manager.get_platform_credentials(user_id, 'confluence')
    if confluence_creds:
        # Search Confluence API
        response = requests.get(
            'https://your-site.atlassian.net/wiki/rest/api/content/search',
            params={'cql': f'text ~ "{query}"'},
            headers={'Authorization': f'Bearer {confluence_creds["access_token"]}'}
        )
        
        results['sources']['confluence'] = {
            'count': len(confluence_results),
            'results': confluence_results
        }
```

### **3. Platform Connection:**
- Add OAuth flow in Platform Connections
- Store tokens in `oauth_tokens` table
- Backend auto-detects availability

**That's it!** The source is now fully integrated.

---

## 🎓 **SUMMARY**

**Universal Search is a sophisticated multi-source search aggregator that:**

1. **Detects** which platforms/databases user has connected
2. **Enables/Disables** checkboxes based on availability
3. **Allows** user to select which sources to search
4. **Executes** parallel searches across selected sources
5. **Merges** results and groups by source
6. **Displays** results with counts and relevance scores

**The system is:**
- ✅ **Connection-aware** - Only shows/enables connected platforms
- ✅ **User-controlled** - Checkboxes for include/exclude
- ✅ **Real-time** - Changes trigger instant re-search
- ✅ **Extensible** - Easy to add new sources
- ✅ **Intelligent** - Supports keyword, semantic, and hybrid search

**Key Innovation:**
Instead of separate search interfaces for each platform, users get **ONE search box** that searches EVERYTHING they have access to, with granular control over which sources to include.
