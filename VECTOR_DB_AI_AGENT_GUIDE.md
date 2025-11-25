# Vector Database Tools - AI Agent Quick Reference

## 🤖 For AI Agents Using These Tools

This guide explains how Claude/AI agents should use the Pinecone vector database tools in the AI_agents platform.

---

## 🎯 Core Concept: Active Retrieval vs Passive RAG

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

**Key Difference:** You (the AI) actively request information when needed, with full control over search parameters.

---

## 🛠️ Available Tools (8 Total)

### 1. pinecone_query_vectors - Semantic Search
**When to use:** User asks question that might be answered by uploaded documents

**Example conversation:**
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

**Tips:**
- Use `query_text` for natural language queries (auto-embedded)
- Set `top_k` based on complexity (5-10 for most queries)
- Use `filter` to narrow results: `{"category": "security"}`
- Include sources in your response (chunk IDs from metadata)

### 2. pinecone_describe_index_stats - Check What's Available
**When to use:** User asks what documents are available, or before searching

**Example conversation:**
```
User: "What documents do I have uploaded?"

AI calls:
pinecone_describe_index_stats(
    _user_id=1,
    _injected_credentials=True
)

Result: {
    "total_vectors": 1542,
    "dimension": 1536,
    "namespaces": {
        "doc-xyz123": 142,
        "doc-abc456": 380,
        "doc-def789": 1020
    }
}

AI response: "You have 3 documents indexed in the vector database:
- doc-xyz123 (142 chunks)
- doc-abc456 (380 chunks)
- doc-def789 (1020 chunks)

Total: 1,542 text chunks ready for search."
```

### 3. pinecone_list_namespaces - List Documents
**When to use:** Similar to describe_index_stats but with more structure

**Example:**
```
AI calls:
pinecone_list_namespaces(
    _user_id=1,
    _injected_credentials=True
)

Result: {
    "namespaces": [
        {"name": "doc-xyz123", "vector_count": 142},
        {"name": "doc-abc456", "vector_count": 380}
    ]
}
```

### 4. pinecone_fetch_vectors - Get Specific Chunks
**When to use:** User wants to see exact text from a specific chunk

**Example:**
```
User: "Show me the full text of chunk 5 from document xyz123"

AI calls:
pinecone_fetch_vectors(
    ids=["doc-xyz123-chunk-5"],
    namespace="doc-xyz123",
    _user_id=1,
    _injected_credentials=True
)

Result: Returns full text of that chunk
```

### 5. vector_db_upload_document - Upload Document
**When to use:** User wants to add a document to the vector database

**Example:**
```
User: "Can you upload this document to the vector database?"
[User provides file path or attaches file]

AI calls:
vector_db_upload_document(
    file_path="/tmp/uploaded_file.pdf",
    filename="company_handbook.pdf",
    chunk_size=800,
    chunk_overlap=20,
    namespace="",  # Auto-generates unique namespace
    _user_id=1,
    _injected_credentials=True
)

Result: {
    "document_id": "doc-new123",
    "vectors_created": 245,
    "namespace": "doc-new123"
}

AI response: "Successfully uploaded company_handbook.pdf to the vector database!
- Created 245 text chunks
- Namespace: doc-new123
- Ready for search queries"
```

**Note:** This is a FULL pipeline - it handles text extraction, chunking, embedding, and upsert automatically.

### 6. pinecone_delete_vectors - Remove Documents
**When to use:** User wants to delete a document or clean up

**Example:**
```
User: "Delete document xyz123"

AI calls:
pinecone_delete_vectors(
    delete_all=True,
    namespace="doc-xyz123",
    _user_id=1,
    _injected_credentials=True
)

AI response: "Document xyz123 has been deleted from the vector database."
```

### 7. pinecone_upsert_vectors - Add Custom Vectors
**When to use:** Advanced use case - adding pre-embedded vectors

**Example:**
```
User: "Add this custom embedding to the database"

AI calls:
pinecone_upsert_vectors(
    vectors=[{
        "id": "custom-1",
        "values": [0.1, 0.2, ..., 0.5],  # 1536 dimensions
        "metadata": {"text": "...", "category": "custom"}
    }],
    namespace="custom",
    _user_id=1,
    _injected_credentials=True
)
```

**Note:** Most users will use `vector_db_upload_document` instead.

### 8. pinecone_update_vector - Modify Metadata
**When to use:** Update metadata without re-embedding

**Example:**
```
AI calls:
pinecone_update_vector(
    id="doc-xyz123-chunk-5",
    metadata={"category": "updated", "reviewed": True},
    namespace="doc-xyz123",
    _user_id=1,
    _injected_credentials=True
)
```

---

## 💡 Common Usage Patterns

### Pattern 1: Simple Document Search
```
User: "What does my documentation say about API rate limits?"

Step 1: Query vector DB
AI calls: pinecone_query_vectors(
    query_text="API rate limits throttling requests per second",
    top_k=5
)

Step 2: Synthesize answer from results
AI response: "According to your documentation (doc-xyz123-chunk-8):
- Rate limit: 100 requests per minute
- Burst limit: 20 requests per second
- Headers: X-RateLimit-Remaining shows remaining quota"
```

### Pattern 2: Multi-Step Research
```
User: "Compare what my documents say about authentication vs authorization"

Step 1: Search for authentication
AI calls: pinecone_query_vectors(query_text="authentication login credentials")

Step 2: Search for authorization
AI calls: pinecone_query_vectors(query_text="authorization permissions access control")

Step 3: Compare and synthesize
AI response: "Here's how your documents distinguish them:

Authentication (from doc-abc456):
- Verifying user identity
- Username/password or OAuth
- Happens at login

Authorization (from doc-xyz123):
- Determining access rights
- Role-based permissions
- Happens on every request"
```

### Pattern 3: Check Before Search
```
User: "Search my documents for deployment procedures"

Step 1: Check if documents exist
AI calls: pinecone_describe_index_stats()

Result: total_vectors: 0 (no documents)

AI response: "You don't have any documents uploaded to the vector database yet. 
Would you like to upload documentation first? I can help you do that."
```

### Pattern 4: Filtered Search
```
User: "Find security-related information from engineering docs"

AI calls: pinecone_query_vectors(
    query_text="security authentication encryption",
    top_k=10,
    filter={"category": "engineering", "department": "security"}
)
```

---

## 🎯 Best Practices for AI Agents

### DO:
1. **Check stats first** - Call `pinecone_describe_index_stats()` to see if documents exist
2. **Use descriptive queries** - Expand user questions into richer query_text
3. **Cite sources** - Include chunk IDs in responses (e.g., "from doc-xyz123-chunk-5")
4. **Set appropriate top_k** - Use 5-10 for most queries
5. **Handle empty results** - Gracefully respond if no matching documents found
6. **Use namespaces** - If user says "search document ABC", use namespace="doc-ABC"

### DON'T:
1. **Don't assume documents exist** - Always check first
2. **Don't use query_vector directly** - Use query_text (auto-embedded)
3. **Don't ignore metadata** - Use filters when user specifies categories/types
4. **Don't return raw JSON** - Synthesize into natural language
5. **Don't over-retrieve** - top_k=50 is rarely needed
6. **Don't forget credentials** - Always include `_user_id` and `_injected_credentials=True`

---

## 🔍 Query Text Tips

### Good Query Text Construction

**User asks:** "How do I reset my password?"

**❌ Bad query_text:**
```python
query_text="password"
```

**✅ Good query_text:**
```python
query_text="password reset forgot change credentials account recovery"
```

**Why:** More keywords = better semantic matching

### Expanding User Questions

| User Question | Good query_text |
|--------------|-----------------|
| "What's the API key?" | "API key authentication credentials access token" |
| "How do I deploy?" | "deployment deploy production release workflow CI/CD" |
| "Error codes?" | "error codes status codes HTTP responses exceptions" |
| "Performance tips?" | "performance optimization speed latency caching" |

---

## 🚨 Error Handling

### Handle Missing Credentials
```python
Result: {"success": False, "error": "Pinecone credentials not found"}

AI response: "I don't have Pinecone credentials configured. Please:
1. Open the Vector Database sidebar
2. Go to Credentials tab
3. Enter your Pinecone API key and index details
4. Click Save and Test Connection"
```

### Handle No Results
```python
Result: {"success": True, "matches": [], "count": 0}

AI response: "I couldn't find any information about X in your uploaded documents. 
The documents might not contain that information, or it might be phrased differently.
Try asking in another way, or check if the right documents are uploaded."
```

### Handle Dimension Mismatch
```python
Result: {"success": False, "error": "dimension mismatch"}

AI response: "There's a configuration issue with the vector database. 
The embedding model doesn't match the index dimensions. Please check:
- Index dimensions: Should be 1536 for ada-002
- Embedding model: Should be text-embedding-ada-002"
```

---

## 📊 Response Format Examples

### Good Response (With Citations)
```
Based on your documentation (doc-api-guide-chunk-12), the authentication flow is:

1. User submits credentials to /auth/login
2. Server validates and issues JWT token
3. Client includes token in Authorization header: "Bearer {token}"
4. Token expires after 24 hours

Additional details in doc-security-policies-chunk-5 mention that tokens can be refreshed using the /auth/refresh endpoint.
```

### Bad Response (No Citations)
```
The authentication flow involves submitting credentials, getting a token, and using it in requests. Tokens expire.
```

**Why bad:** No sources, vague, doesn't show where information came from.

---

## 🔄 Multi-Turn Conversations

You can reference vector DB results across conversation turns:

```
Turn 1:
User: "What does my documentation say about rate limits?"
AI: [Searches, finds info] "Rate limit is 100 req/min (doc-api-v2-chunk-8)"

Turn 2:
User: "Can I increase that?"
AI: [Searches with context] "Yes, according to doc-enterprise-features-chunk-3, 
enterprise plans can request custom rate limits up to 1000 req/min"

Turn 3:
User: "How do I upgrade?"
AI: [Searches] "To upgrade to enterprise (doc-pricing-chunk-2)..."
```

**Note:** Each search is independent - you don't maintain "context" in the vector DB, but you can chain searches based on conversation flow.

---

## 🎓 Advanced Patterns

### Aggregation Across Documents
```
User: "Summarize all mentions of 'API' across all my documents"

Step 1: Large search
AI calls: pinecone_query_vectors(query_text="API", top_k=50)

Step 2: Analyze results
AI response: "I found 50 references to APIs across 5 documents:
- doc-api-guide: 22 mentions (REST API design)
- doc-backend-arch: 15 mentions (microservices communication)
- doc-mobile-app: 8 mentions (API client implementation)
- doc-security: 3 mentions (API key management)
- doc-deployment: 2 mentions (API gateway configuration)"
```

### Comparative Analysis
```
User: "Compare version 1 vs version 2 features"

Step 1: Search version 1 docs
AI calls: pinecone_query_vectors(
    query_text="features capabilities functionality",
    filter={"version": "1.0"}
)

Step 2: Search version 2 docs
AI calls: pinecone_query_vectors(
    query_text="features capabilities functionality",
    filter={"version": "2.0"}
)

Step 3: Compare and present differences
```

---

## 🎯 Tool Selection Decision Tree

```
User asks a question
    ↓
Is it about documents?
    ├─ No → Answer directly without tools
    └─ Yes ↓
        
Are documents uploaded?
    ├─ Unknown → Call pinecone_describe_index_stats()
    │   ├─ 0 vectors → "No documents uploaded"
    │   └─ Has vectors → Continue to search
    └─ Known to exist → Continue to search

What type of query?
    ├─ "What documents?" → Call pinecone_list_namespaces()
    ├─ "Search for X" → Call pinecone_query_vectors(query_text="X")
    ├─ "Show chunk Y" → Call pinecone_fetch_vectors(ids=["Y"])
    ├─ "Upload file" → Call vector_db_upload_document()
    └─ "Delete doc" → Call pinecone_delete_vectors(delete_all=True)
```

---

## 🚀 Quick Start Checklist for AI Agents

When user mentions documents/knowledge base/vector DB:

1. [ ] Check if documents exist (`pinecone_describe_index_stats`)
2. [ ] If no documents, offer to help upload
3. [ ] If documents exist, formulate good query_text
4. [ ] Execute search with appropriate top_k (5-10)
5. [ ] Synthesize results into natural language
6. [ ] Cite sources (include chunk IDs)
7. [ ] Offer follow-up questions or clarifications

---

**Last Updated:** January 20, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready for AI Agent Use  
**Tool Count:** 8 tools available
