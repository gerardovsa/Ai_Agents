# Pinecone Enhanced Features - Modern Framework Integration

**Date:** December 2024  
**Based on:** pinecone-python-client v3.0+ (GitHub analysis)  
**Status:** Enhancement recommendations for vector_database module

---

## 📊 Overview

Analysis of the official Pinecone Python SDK reveals **15+ advanced features** not yet implemented in our vector_database module. This document provides implementation guidance for Modern Framework integration.

---

## 🆕 Advanced Features Available

### 1. **Sparse Vectors & Hybrid Search** ⭐ High Priority

**What it is:**  
Combine dense (semantic) and sparse (keyword) vectors for more accurate retrieval.

**Pinecone API:**
```python
# Upsert with sparse vectors
index.upsert(vectors=[
    Vector(
        id="doc1",
        values=[0.1, 0.2, ...],  # Dense vector (1536d)
        sparse_values=SparseValues(
            indices=[1, 5, 10],    # Token IDs
            values=[0.5, 0.3, 0.2] # TF-IDF weights
        ),
        metadata={"title": "Document 1"}
    )
])

# Query with hybrid search
results = index.query(
    vector=[0.1, 0.2, ...],           # Dense query
    sparse_vector=SparseValues(
        indices=[1, 5],
        values=[0.6, 0.4]
    ),
    top_k=10,
    include_metadata=True
)
```

**Implementation in vector_database_modern.js:**
```javascript
// Add to uploadDocument method
async uploadDocument(file, utilities) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('enable_hybrid_search', true); // NEW: Enable sparse vectors
    
    const response = await utilities.api.post(
        '/api/vector-db/upload-document',
        formData,
        { 'Content-Type': 'multipart/form-data' }
    );
}

// Add hybrid search UI controls
this.dom.html('#queryControls', `
    <div>
        <label>
            <input type="checkbox" id="enableHybridSearch" />
            Enable Hybrid Search (keyword + semantic)
        </label>
    </div>
`);
```

**Backend Tool Enhancement (pinecone_tools.py):**
```python
# Add to vector_db_upload_document()
def vector_db_upload_document(
    file_path: str,
    namespace: str = "default",
    enable_hybrid_search: bool = False,  # NEW parameter
    **kwargs
):
    """Upload document with optional sparse vector generation"""
    
    # ... existing code ...
    
    if enable_hybrid_search:
        # Generate sparse vectors using TF-IDF or BM25
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(max_features=100)
        sparse_matrix = vectorizer.fit_transform([chunk])
        
        sparse_values = SparseValues(
            indices=sparse_matrix.indices.tolist(),
            values=sparse_matrix.data.tolist()
        )
        
        vector_obj['sparse_values'] = sparse_values
```

**Benefits:**
- ✅ Better accuracy for domain-specific queries
- ✅ Keyword matching + semantic understanding
- ✅ Handles acronyms, technical terms better

---

### 2. **Query Namespaces (Cross-Namespace Search)** ⭐ Medium Priority

**What it is:**  
Query multiple namespaces simultaneously and aggregate results.

**Pinecone API:**
```python
# Query across 3 namespaces in parallel
combined_results = index.query_namespaces(
    vector=[0.1, 0.2, ...],
    namespaces=['legal', 'medical', 'general'],
    metric='cosine',
    top_k=10,
    include_metadata=True
)

# Results automatically ranked and merged
for match in combined_results.matches:
    print(f"{match.id} (ns: {match.namespace}): {match.score}")

print(f"Total read units: {combined_results.usage.read_units}")
```

**Implementation in vector_database_modern.js:**
```javascript
// Add multi-namespace search UI
this.dom.html('#advancedSearch', `
    <div class="namespace-selector">
        <label>Search Namespaces:</label>
        <div>
            <label><input type="checkbox" value="default" checked /> Default</label>
            <label><input type="checkbox" value="legal" /> Legal</label>
            <label><input type="checkbox" value="medical" /> Medical</label>
        </div>
    </div>
`);

// Add search method
async searchAcrossNamespaces(query, utilities) {
    const selectedNamespaces = Array.from(
        this.dom.findAll('input[type="checkbox"]:checked')
    ).map(el => el.value);
    
    const response = await utilities.api.post('/api/vector-db/query-namespaces', {
        query_text: query,
        namespaces: selectedNamespaces,
        top_k: 10
    });
    
    this.renderCrossNamespaceResults(response.data);
}

renderCrossNamespaceResults(results) {
    const html = results.matches.map(match => `
        <div class="result-card">
            <span class="namespace-badge">${match.namespace}</span>
            <h4>${match.metadata.title}</h4>
            <p>Score: ${match.score.toFixed(4)}</p>
        </div>
    `).join('');
    
    this.dom.html('#searchResults', html);
}
```

**Backend Tool (NEW):**
```python
# Add to pinecone_tools.py
def pinecone_query_namespaces(
    query_text: str,
    namespaces: List[str],
    metric: str = 'cosine',
    top_k: int = 10,
    **kwargs
) -> Dict[str, Any]:
    """
    Query multiple namespaces and return aggregated results
    
    Tool #9: pinecone_query_namespaces
    """
    user_id = kwargs.get('_user_id')
    client = _get_pinecone_client(user_id)
    
    # Get embedding
    embedding = _generate_embedding(query_text, user_id)
    
    # Query across namespaces
    results = client.query_namespaces(
        vector=embedding,
        namespaces=namespaces,
        metric=metric,
        top_k=top_k,
        include_metadata=True
    )
    
    return {
        "matches": [
            {
                "id": m.id,
                "namespace": m.namespace,
                "score": m.score,
                "metadata": m.metadata
            } for m in results.matches
        ],
        "usage": {
            "read_units": results.usage.read_units
        }
    }
```

**Benefits:**
- ✅ Multi-tenant search (e.g., search user1 + user2 data)
- ✅ Cross-domain queries (e.g., legal + medical docs)
- ✅ Automatic result ranking across namespaces

---

### 3. **Namespace Management** ⭐ Medium Priority

**What it is:**  
Create, describe, list, and delete namespaces via API.

**Pinecone API:**
```python
# Create namespace with schema
index.namespace.create(
    name='legal_docs',
    schema={'title': 'text', 'date': 'date'}
)

# List all namespaces
namespaces = index.namespace.list()
for ns in namespaces.namespaces:
    print(f"{ns.name}: {ns.vector_count} vectors")

# Describe namespace
info = index.namespace.describe('legal_docs')
print(f"Vectors: {info.vector_count}, Dimension: {info.dimension}")

# Delete namespace
index.namespace.delete('old_namespace')
```

**Implementation in vector_database_modern.js:**
```javascript
// Add namespace management tab
addNamespaceTab(container, utilities) {
    this.dom.html(container, `
        <div class="namespace-manager">
            <h3>Namespace Management</h3>
            
            <div class="create-namespace">
                <input type="text" id="newNamespaceName" placeholder="New namespace name" />
                <button id="createNamespaceBtn">Create</button>
            </div>
            
            <div id="namespaceList">
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Vector Count</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="namespaceTableBody"></tbody>
                </table>
            </div>
        </div>
    `);
    
    this.dom.on('#createNamespaceBtn', 'click', () => this.createNamespace(utilities));
    this.loadNamespaceList(utilities);
}

async loadNamespaceList(utilities) {
    const response = await utilities.api.get('/api/vector-db/namespaces');
    const tbody = this.dom.find('#namespaceTableBody');
    
    tbody.innerHTML = response.data.namespaces.map(ns => `
        <tr>
            <td>${ns.name}</td>
            <td>${ns.vector_count}</td>
            <td>
                <button data-action="describe" data-ns="${ns.name}">Info</button>
                <button data-action="delete" data-ns="${ns.name}">Delete</button>
            </td>
        </tr>
    `).join('');
}
```

**Backend Endpoints (NEW):**
```python
# Add to vector_db_routes.py
@vector_db_bp.route('/namespaces', methods=['GET'])
@require_auth
def list_namespaces():
    """List all namespaces in index"""
    user_id = request.user_id
    client = get_pinecone_client(user_id)
    
    namespaces = client.namespace.list()
    return jsonify({
        "namespaces": [
            {
                "name": ns.name,
                "vector_count": ns.vector_count
            } for ns in namespaces.namespaces
        ]
    })

@vector_db_bp.route('/namespaces/<namespace>', methods=['GET'])
@require_auth
def describe_namespace(namespace):
    """Get detailed namespace information"""
    user_id = request.user_id
    client = get_pinecone_client(user_id)
    
    info = client.namespace.describe(namespace)
    return jsonify({
        "name": info.name,
        "vector_count": info.vector_count,
        "dimension": info.dimension
    })
```

**Benefits:**
- ✅ Better organization for multi-tenant applications
- ✅ Namespace-level statistics and monitoring
- ✅ Cleaner data isolation

---

### 4. **Fetch by Metadata (Advanced Filtering)** ⭐ High Priority

**What it is:**  
Retrieve vectors using metadata filters without embedding query.

**Pinecone API:**
```python
# Fetch all legal documents from 2024
results = index.fetch_by_metadata(
    filter={
        "category": {"$eq": "legal"},
        "year": {"$gte": 2024}
    },
    limit=100,
    namespace='default'
)

# Paginated fetching
pagination_token = results.pagination.next
while pagination_token:
    next_page = index.fetch_by_metadata(
        filter=filter,
        pagination_token=pagination_token
    )
    pagination_token = next_page.pagination.next
```

**Implementation in vector_database_modern.js:**
```javascript
// Add metadata filter UI
addMetadataFilters(container, utilities) {
    this.dom.html(container, `
        <div class="metadata-filter">
            <h4>Filter by Metadata</h4>
            <div id="filterRules"></div>
            <button id="addFilterRule">+ Add Rule</button>
            <button id="applyFilter">Apply Filter</button>
        </div>
    `);
    
    this.dom.on('#addFilterRule', 'click', () => this.addFilterRule());
    this.dom.on('#applyFilter', 'click', () => this.applyMetadataFilter(utilities));
}

addFilterRule() {
    const ruleHtml = `
        <div class="filter-rule">
            <select class="filter-field">
                <option value="category">Category</option>
                <option value="year">Year</option>
                <option value="author">Author</option>
            </select>
            <select class="filter-operator">
                <option value="$eq">Equals</option>
                <option value="$ne">Not Equals</option>
                <option value="$gt">Greater Than</option>
                <option value="$gte">Greater or Equal</option>
                <option value="$lt">Less Than</option>
                <option value="$lte">Less or Equal</option>
            </select>
            <input type="text" class="filter-value" placeholder="Value" />
            <button class="remove-rule">×</button>
        </div>
    `;
    this.dom.append('#filterRules', ruleHtml);
}

async applyMetadataFilter(utilities) {
    const rules = Array.from(this.dom.findAll('.filter-rule')).map(rule => ({
        field: rule.querySelector('.filter-field').value,
        operator: rule.querySelector('.filter-operator').value,
        value: rule.querySelector('.filter-value').value
    }));
    
    const filter = {};
    rules.forEach(rule => {
        filter[rule.field] = { [rule.operator]: rule.value };
    });
    
    const response = await utilities.api.post('/api/vector-db/fetch-by-metadata', {
        filter: filter,
        limit: 100
    });
    
    this.renderMetadataResults(response.data);
}
```

**Backend Tool (NEW):**
```python
# Add to pinecone_tools.py
def pinecone_fetch_by_metadata(
    filter: Dict[str, Any],
    limit: int = 100,
    namespace: str = "default",
    pagination_token: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Fetch vectors by metadata filter (no embedding query needed)
    
    Tool #10: pinecone_fetch_by_metadata
    """
    user_id = kwargs.get('_user_id')
    client = _get_pinecone_client(user_id)
    
    results = client.fetch_by_metadata(
        filter=filter,
        limit=limit,
        namespace=namespace,
        pagination_token=pagination_token
    )
    
    return {
        "vectors": [
            {
                "id": v.id,
                "values": v.values,
                "metadata": v.metadata
            } for v in results.vectors
        ],
        "pagination": {
            "next": results.pagination.next if results.pagination else None
        }
    }
```

**Benefits:**
- ✅ Efficient metadata-only queries (no embedding needed)
- ✅ Export/backup filtered subsets
- ✅ Data auditing and compliance

---

### 5. **Bulk Import API** ⭐ Low Priority (Future)

**What it is:**  
Async import of large datasets from S3/GCS/Azure.

**Pinecone API:**
```python
# Start bulk import job
job = index.bulk_import.start(
    source_uri='s3://my-bucket/vectors.parquet',
    namespace='default',
    import_mode='upsert'
)

# Monitor job progress
status = index.bulk_import.describe(job.id)
print(f"Progress: {status.progress}% - {status.status}")

# List all import jobs
jobs = index.bulk_import.list()
```

**Implementation Notes:**
- Requires cloud storage integration (S3, GCS, Azure)
- Async processing - UI needs progress polling
- Best for 100K+ vectors
- Defer to Phase 2 after core features stable

---

### 6. **Collections (Index Backups)** ⭐ Low Priority

**What it is:**  
Create static snapshots of indexes for backups/experiments.

**Pinecone API:**
```python
# Create collection from index
collection = pc.create_collection(
    name='production_backup_2024',
    source='production-index'
)

# List collections
collections = pc.list_collections()

# Restore collection to new index
pc.create_index(
    name='restored-index',
    dimension=1536,
    metric='cosine',
    spec=ServerlessSpec(cloud='aws', region='us-east-1'),
    source_collection='production_backup_2024'
)
```

**Implementation Priority:** Phase 3 (operations/admin tools)

---

## 📋 Implementation Priority

### Phase 1 (Immediate - Q1 2025)
1. ✅ **Sparse Vectors & Hybrid Search** - High user impact
2. ✅ **Fetch by Metadata** - Essential for filtering
3. ✅ **Query Namespaces** - Multi-tenant support

### Phase 2 (Q2 2025)
4. **Namespace Management** - Better organization
5. **Advanced Metadata Filters** - UI builder for complex queries
6. **Reranking** - Improve search accuracy

### Phase 3 (Q3 2025 - Future)
7. **Bulk Import API** - Large-scale data ingestion
8. **Collections API** - Backup/restore workflows
9. **Performance Monitoring** - Usage analytics

---

## 🛠️ Tool Schema Updates Required

Add to `tools/schemas/pinecone_tools.json`:

```json
{
  "tools": [
    {
      "name": "pinecone_query_namespaces",
      "description": "Query multiple namespaces simultaneously and aggregate results. Returns combined ranked results from all specified namespaces.",
      "platform": "pinecone",
      "parameters": {
        "type": "object",
        "properties": {
          "query_text": {
            "type": "string",
            "description": "Text to convert to embedding for query"
          },
          "namespaces": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of namespace names to query"
          },
          "metric": {
            "type": "string",
            "enum": ["cosine", "euclidean", "dotproduct"],
            "description": "Distance metric for ranking"
          },
          "top_k": {
            "type": "integer",
            "description": "Number of results per namespace",
            "default": 10
          }
        },
        "required": ["query_text", "namespaces"]
      }
    },
    {
      "name": "pinecone_fetch_by_metadata",
      "description": "Fetch vectors using metadata filters without embedding query. Supports complex filters with $eq, $ne, $gt, $gte, $lt, $lte operators.",
      "platform": "pinecone",
      "parameters": {
        "type": "object",
        "properties": {
          "filter": {
            "type": "object",
            "description": "Metadata filter object with field: {operator: value} structure"
          },
          "limit": {
            "type": "integer",
            "description": "Maximum vectors to return",
            "default": 100
          },
          "namespace": {
            "type": "string",
            "description": "Namespace to query",
            "default": "default"
          },
          "pagination_token": {
            "type": "string",
            "description": "Token from previous response for pagination"
          }
        },
        "required": ["filter"]
      }
    }
  ]
}
```

---

## 📖 Documentation References

**Official Pinecone Docs:**
- Python SDK: https://github.com/pinecone-io/pinecone-python-client
- Sparse Vectors: https://docs.pinecone.io/guides/data/understanding-hybrid-search
- Query Namespaces: https://docs.pinecone.io/reference/query_namespaces
- Metadata Filtering: https://docs.pinecone.io/guides/data/filtering-with-metadata

**Modern Framework Integration:**
- Module Composition Pattern: UI/MODERN_FRAMEWORK_GUIDE.md
- Utility Injection: UI/UTILITIES_REFERENCE.md
- Lifecycle Hooks: UI/LIFECYCLE_HOOKS_SPEC.md

---

**Next Steps:**
1. Review priority features with team
2. Create Flask endpoint stubs for new tools
3. Update manifest.json with new API endpoints
4. Implement UI components in vector_database_modern.js
5. Test with Modern Framework loader
6. Update tool registry with new tool schemas

---

**Last Updated:** December 2024  
**Version:** 1.0  
**Status:** 📋 Enhancement Roadmap
