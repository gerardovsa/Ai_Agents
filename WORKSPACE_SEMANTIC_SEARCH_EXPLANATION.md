# 🔍 Workspace & Transcription Semantic Search - Complete Explanation

> **What You're Asking**: Enable AI to search through workspace chat history and transcriptions using semantic/vector search instead of just keyword matching.

---

## 🎯 Your Request Explained

### What You Want

**1. Search Workspace Threads**
- "Find all conversations where we discussed the pricing strategy"
- "What did we say about the database migration last week?"
- AI understands **context and meaning**, not just exact keywords

**2. Search Across All Workspaces**
- "Show me every time anyone mentioned the new product feature"
- "Find discussions about customer complaints across all teams"
- Search multiple workspaces at once for a specific user

**3. Search Transcriptions**
- "Find the meeting where John talked about Q4 goals"
- "What was said in the transcription about the bug fix?"
- Search voice transcriptions with semantic understanding

**4. Semantic/Vector Search**
- Instead of: `SELECT * FROM messages WHERE content LIKE '%database%'` (keyword matching)
- You want: Find messages about "data storage" even if they use terms like "database", "SQL", "persistence", "storage system"
- **Meaning-based search** using embeddings/vectors

---

## 📊 Current Database Structure

### What You Have

From your Supabase/PostgreSQL database:

```sql
-- MESSAGES TABLE (workspace_chats.messages)
CREATE TABLE workspace_chats (
    id INTEGER,
    workspace_id INTEGER,      -- Which workspace
    thread_id INTEGER,          -- Which conversation thread
    session_id TEXT,            -- Session identifier
    role TEXT,                  -- 'user', 'assistant', 'system'
    content TEXT,               -- The actual message text
    user_id INTEGER,            -- Who sent it
    embedding_vector TEXT,      -- 🎯 THIS EXISTS BUT MAY BE EMPTY
    created_at TIMESTAMP,
    metadata TEXT
);

-- TRANSCRIPTIONS TABLE (valorai_chrome_extension.transcriptions)
CREATE TABLE transcriptions (
    transcription_id UUID,
    text TEXT,                  -- Web Speech transcription
    whisper_text TEXT,          -- Whisper AI transcription
    transcription_mode TEXT,    -- 'web_speech', 'whisper', 'hybrid'
    duration NUMERIC,
    user_id INTEGER,
    workspace_id INTEGER,
    session_id UUID,
    created_at TIMESTAMP,
    deleted_at TIMESTAMP
);
```

### What's Missing

✅ **You HAVE**:
- Messages table with `content` field
- `embedding_vector` column (TEXT field for storing JSON embeddings)
- Transcriptions table with text fields
- Workspace and user relationships

❌ **You DON'T HAVE** (yet):
- **Populated embeddings** - The `embedding_vector` column is likely empty/NULL
- **pgvector extension** - PostgreSQL extension for efficient vector similarity search
- **Search functions** - AI agent tools to perform semantic search
- **Embedding generation** - Process to convert text → vectors

---

## 🧠 How Semantic Search Works

### The Concept

**Traditional Search** (keyword matching):
```sql
SELECT * FROM messages 
WHERE content LIKE '%database%';
```
- Only finds exact word "database"
- Misses: "SQL", "data store", "persistence layer", "PostgreSQL"

**Semantic Search** (vector/embedding search):
```sql
SELECT * FROM messages 
ORDER BY embedding_vector <-> query_embedding
LIMIT 10;
```
- Finds messages with **similar meaning**
- Understands synonyms and context
- Ranks by relevance

### The Process

1. **Generate Embeddings** (one-time setup):
   ```
   Message Text → OpenAI Embeddings API → 1536-dimensional vector
   "We need to migrate the database" → [0.234, -0.123, 0.456, ...]
   ```

2. **Store Embeddings**:
   ```sql
   UPDATE messages 
   SET embedding_vector = '[0.234, -0.123, ...]'::vector
   WHERE id = 123;
   ```

3. **Search by Similarity**:
   ```
   User Query: "data storage issues"
   → Generate embedding for query
   → Find messages with closest vector distance
   → Return top N matches ranked by relevance
   ```

---

## 🚀 Implementation Plan

### Option 1: PostgreSQL pgvector (Recommended)

**Pros**: Fast, efficient, native PostgreSQL, works with Supabase
**Cons**: Requires database migration, one-time embedding generation

#### Steps:

**1. Enable pgvector Extension**
```sql
-- Run in Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;

-- Convert embedding_vector from TEXT to vector type
ALTER TABLE workspace_chats.messages 
ALTER COLUMN embedding_vector TYPE vector(1536) 
USING embedding_vector::vector;

-- Add index for fast similarity search
CREATE INDEX idx_messages_embedding 
ON workspace_chats.messages 
USING ivfflat (embedding_vector vector_cosine_ops)
WITH (lists = 100);
```

**2. Generate Embeddings for Existing Messages**
```python
# tools/implementations/generate_embeddings.py
import openai
import psycopg2
from AI_infrastructure.shared.database_utils import get_database_connection

def generate_embeddings_batch(batch_size=100):
    """Generate embeddings for all messages missing them"""
    conn = get_database_connection('workspace_chats')
    cursor = conn.cursor()
    
    # Get messages without embeddings
    cursor.execute("""
        SELECT id, content 
        FROM messages 
        WHERE embedding_vector IS NULL 
        AND content IS NOT NULL
        LIMIT %s
    """, (batch_size,))
    
    messages = cursor.fetchall()
    
    for msg_id, content in messages:
        # Generate embedding using OpenAI
        response = openai.Embedding.create(
            model="text-embedding-3-small",
            input=content[:8000]  # Truncate long messages
        )
        embedding = response['data'][0]['embedding']
        
        # Store embedding
        cursor.execute("""
            UPDATE messages 
            SET embedding_vector = %s
            WHERE id = %s
        """, (embedding, msg_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"Generated embeddings for {len(messages)} messages")
```

**3. Create Search Tool**
```python
# tools/implementations/workspace_semantic_search.py
def workspace_semantic_search(
    search_query: str,
    workspace_ids: list = None,
    user_id: int = None,
    limit: int = 10,
    similarity_threshold: float = 0.7
) -> dict:
    """
    Semantic search across workspace messages using embeddings
    
    Args:
        search_query: Natural language search query
        workspace_ids: List of workspace IDs to search (None = all accessible)
        user_id: Filter by specific user (None = all users)
        limit: Max results to return
        similarity_threshold: Minimum similarity score (0-1)
    
    Returns:
        {
            'success': True,
            'results': [
                {
                    'message_id': 123,
                    'workspace_id': 5,
                    'workspace_name': 'Engineering Team',
                    'thread_id': 45,
                    'content': 'Message text...',
                    'user': 'john.doe',
                    'created_at': '2025-12-08T10:30:00',
                    'similarity_score': 0.92,
                    'role': 'user'
                },
                ...
            ],
            'query': search_query,
            'total_results': 10
        }
    
    Example:
        # Find discussions about database issues
        workspace_semantic_search(
            search_query="database performance problems",
            workspace_ids=[1, 2, 3],
            limit=20
        )
        
        # Find what John said about pricing
        workspace_semantic_search(
            search_query="pricing strategy discussions",
            user_id=5,
            limit=15
        )
    """
    import openai
    from AI_infrastructure.shared.database_utils import get_database_connection
    
    try:
        # Generate embedding for search query
        response = openai.Embedding.create(
            model="text-embedding-3-small",
            input=search_query
        )
        query_embedding = response['data'][0]['embedding']
        
        conn = get_database_connection('workspace_chats')
        cursor = conn.cursor()
        
        # Build SQL query with filters
        filters = []
        params = [query_embedding, similarity_threshold, limit]
        
        if workspace_ids:
            filters.append("m.workspace_id = ANY(%s)")
            params.insert(0, workspace_ids)
        
        if user_id:
            filters.append("m.user_id = %s")
            params.insert(1 if workspace_ids else 0, user_id)
        
        where_clause = f"AND {' AND '.join(filters)}" if filters else ""
        
        # Semantic search query
        query = f"""
            SELECT 
                m.id as message_id,
                m.workspace_id,
                w.name as workspace_name,
                m.thread_id,
                m.content,
                u.username,
                m.created_at,
                m.role,
                1 - (m.embedding_vector <=> %s::vector) as similarity
            FROM messages m
            LEFT JOIN workspaces w ON m.workspace_id = w.id
            LEFT JOIN users u ON m.user_id = u.id
            WHERE m.embedding_vector IS NOT NULL
            {where_clause}
            AND (1 - (m.embedding_vector <=> %s::vector)) > %s
            ORDER BY similarity DESC
            LIMIT %s
        """
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        formatted_results = []
        for row in results:
            formatted_results.append({
                'message_id': row[0],
                'workspace_id': row[1],
                'workspace_name': row[2],
                'thread_id': row[3],
                'content': row[4],
                'user': row[5],
                'created_at': row[6].isoformat(),
                'role': row[7],
                'similarity_score': round(float(row[8]), 4)
            })
        
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'results': formatted_results,
            'query': search_query,
            'total_results': len(formatted_results)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'query': search_query
        }
```

**4. Create Transcription Search Tool**
```python
# tools/implementations/transcription_semantic_search.py
def transcription_semantic_search(
    search_query: str,
    user_id: int = None,
    workspace_id: int = None,
    mode: str = None,  # 'web_speech', 'whisper', 'hybrid'
    limit: int = 10
) -> dict:
    """
    Semantic search across transcriptions
    
    Args:
        search_query: What to search for
        user_id: Filter by specific user
        workspace_id: Filter by workspace
        mode: Filter by transcription mode
        limit: Max results
    
    Returns:
        {
            'success': True,
            'results': [
                {
                    'transcription_id': 'uuid',
                    'text': 'Web speech text...',
                    'whisper_text': 'Whisper text...',
                    'mode': 'hybrid',
                    'duration': 125.5,
                    'user': 'john.doe',
                    'workspace': 'Engineering',
                    'created_at': '2025-12-08T10:30:00',
                    'similarity_score': 0.89
                }
            ]
        }
    """
    import openai
    from AI_infrastructure.shared.database_utils import get_database_connection
    
    try:
        # Generate query embedding
        response = openai.Embedding.create(
            model="text-embedding-3-small",
            input=search_query
        )
        query_embedding = response['data'][0]['embedding']
        
        conn = get_database_connection('valorai_chrome_extension')
        cursor = conn.cursor()
        
        # Build filters
        filters = ["t.deleted_at IS NULL"]
        params = [query_embedding]
        
        if user_id:
            filters.append("t.user_id = %s")
            params.append(user_id)
        
        if workspace_id:
            filters.append("t.workspace_id = %s")
            params.append(workspace_id)
        
        if mode:
            filters.append("t.transcription_mode = %s")
            params.append(mode)
        
        where_clause = " AND ".join(filters)
        
        # Search query
        query = f"""
            SELECT 
                t.transcription_id,
                t.text,
                t.whisper_text,
                t.transcription_mode,
                t.duration,
                u.username,
                w.name as workspace_name,
                t.created_at,
                1 - (t.embedding_vector <=> %s::vector) as similarity
            FROM transcriptions t
            LEFT JOIN users u ON t.user_id = u.id
            LEFT JOIN workspaces w ON t.workspace_id = w.id
            WHERE {where_clause}
            AND t.embedding_vector IS NOT NULL
            ORDER BY similarity DESC
            LIMIT %s
        """
        
        params.append(limit)
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        formatted_results = []
        for row in results:
            formatted_results.append({
                'transcription_id': row[0],
                'text': row[1],
                'whisper_text': row[2],
                'mode': row[3],
                'duration': float(row[4]),
                'user': row[5],
                'workspace': row[6],
                'created_at': row[7].isoformat(),
                'similarity_score': round(float(row[8]), 4)
            })
        
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'results': formatted_results,
            'query': search_query,
            'total_results': len(formatted_results)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'query': search_query
        }
```

**5. Add Tool Schemas**
```json
// tools/schemas/semantic_search_tools.json
{
  "workspace_semantic_search": {
    "type": "function",
    "function": {
      "name": "workspace_semantic_search",
      "description": "Search workspace chat messages using semantic/vector search. Finds messages by meaning, not just keywords. Understands context and synonyms.",
      "parameters": {
        "type": "object",
        "properties": {
          "search_query": {
            "type": "string",
            "description": "Natural language search query. Examples: 'database performance issues', 'pricing discussions', 'bug reports about login'"
          },
          "workspace_ids": {
            "type": "array",
            "items": {"type": "integer"},
            "description": "Optional: List of workspace IDs to search. Omit to search all accessible workspaces"
          },
          "user_id": {
            "type": "integer",
            "description": "Optional: Filter results by specific user ID"
          },
          "limit": {
            "type": "integer",
            "description": "Maximum number of results to return (default: 10, max: 50)",
            "default": 10
          },
          "similarity_threshold": {
            "type": "number",
            "description": "Minimum similarity score (0-1, default: 0.7). Higher = more relevant",
            "default": 0.7
          }
        },
        "required": ["search_query"]
      }
    }
  },
  "transcription_semantic_search": {
    "type": "function",
    "function": {
      "name": "transcription_semantic_search",
      "description": "Search voice transcriptions using semantic search. Finds transcriptions by meaning and context.",
      "parameters": {
        "type": "object",
        "properties": {
          "search_query": {
            "type": "string",
            "description": "What to search for in transcriptions"
          },
          "user_id": {
            "type": "integer",
            "description": "Optional: Filter by user who created transcription"
          },
          "workspace_id": {
            "type": "integer",
            "description": "Optional: Filter by workspace"
          },
          "mode": {
            "type": "string",
            "enum": ["web_speech", "whisper", "hybrid"],
            "description": "Optional: Filter by transcription mode"
          },
          "limit": {
            "type": "integer",
            "description": "Max results (default: 10)",
            "default": 10
          }
        },
        "required": ["search_query"]
      }
    }
  }
}
```

---

### Option 2: PostgreSQL Full-Text Search (Simpler Alternative)

**Pros**: Built-in, no extra extensions, easier to implement
**Cons**: Keyword-based (not true semantic), less accurate for meaning

```sql
-- Add tsvector column for full-text search
ALTER TABLE messages 
ADD COLUMN content_tsv tsvector;

-- Generate tsvector from content
UPDATE messages 
SET content_tsv = to_tsvector('english', content);

-- Add GIN index for fast search
CREATE INDEX idx_messages_content_tsv 
ON messages USING GIN(content_tsv);

-- Search query
SELECT * FROM messages
WHERE content_tsv @@ to_tsquery('english', 'database & performance')
ORDER BY ts_rank(content_tsv, to_tsquery('english', 'database & performance')) DESC
LIMIT 10;
```

This is **NOT semantic** but better than LIKE queries.

---

## 💰 Cost Considerations

### OpenAI Embeddings API Pricing

**Model**: `text-embedding-3-small`
- **Cost**: $0.02 per 1M tokens (~$0.00002 per 1K tokens)
- **Example**: 10,000 messages × 100 words/message = ~$2-3 one-time cost

**Embedding Generation**:
- One-time cost for existing messages
- Ongoing cost for new messages (minimal)
- Batch processing to reduce API calls

**Monthly Estimate** (assuming 10K messages/month):
- Embedding cost: ~$0.20/month
- Storage cost: Negligible (vectors are just JSON arrays)
- Search cost: Free (local vector distance calculation)

---

## 🎯 Recommendation

**Phase 1** (Quick Win - 2-3 hours):
1. ✅ Use PostgreSQL Full-Text Search (tsvector)
2. ✅ Add search tool for messages
3. ✅ Add search tool for transcriptions
4. ✅ Test with keyword-based queries

**Phase 2** (True Semantic - 1 day):
1. Enable pgvector extension on Supabase
2. Generate embeddings for existing messages (batch process)
3. Auto-generate embeddings for new messages (trigger/hook)
4. Update search tools to use vector similarity

**Phase 3** (Advanced - ongoing):
1. Hybrid search (combine keyword + semantic)
2. Relevance tuning and feedback loops
3. Search analytics and optimization
4. Multi-modal search (text + metadata)

---

## 📚 Usage Examples

### Example 1: Find Database Discussions
```python
# User asks: "What did we discuss about database performance?"
workspace_semantic_search(
    search_query="database performance optimization",
    workspace_ids=[1, 2, 3],  # Engineering workspaces
    limit=15
)

# Results:
# - "The PostgreSQL query is really slow on large tables..."
# - "We need to add indexes to improve DB speed..."
# - "Consider switching to a faster data store for this use case..."
```

### Example 2: Find User's Comments
```python
# User asks: "What did Sarah say about the pricing model?"
workspace_semantic_search(
    search_query="pricing model revenue strategy",
    user_id=42,  # Sarah's user ID
    limit=10
)
```

### Example 3: Search Transcriptions
```python
# User asks: "Find the meeting where we talked about Q4 goals"
transcription_semantic_search(
    search_query="Q4 quarterly goals objectives planning",
    workspace_id=5,
    limit=10
)
```

### Example 4: Cross-Workspace Search
```python
# User asks: "Show all mentions of the new feature across all teams"
workspace_semantic_search(
    search_query="new dashboard feature analytics charts",
    # workspace_ids=None means search ALL workspaces user has access to
    limit=50
)
```

---

## ✅ Next Steps

**To Implement This**:

1. **Choose approach** (pgvector semantic OR tsvector full-text)
2. **Run database migration** (add columns/indexes)
3. **Generate embeddings** (for pgvector option)
4. **Create search tools** (Python functions)
5. **Add tool schemas** (JSON definitions)
6. **Test searches** (verify relevance)
7. **Document usage** (examples for AI agent)

**Estimated Time**:
- Full-Text Search: 2-3 hours
- Semantic Search: 1 day (including embedding generation)

**Estimated Cost**:
- One-time: $2-5 (embeddings for existing data)
- Ongoing: <$1/month (new messages only)

---

## 🤔 Decision Matrix

| Feature | Full-Text Search | Semantic Search |
|---------|------------------|-----------------|
| **Accuracy** | Good (keyword) | Excellent (meaning) |
| **Setup Time** | 2-3 hours | 1 day |
| **Cost** | Free | ~$3 one-time + $1/mo |
| **Dependencies** | Built-in PostgreSQL | pgvector + OpenAI API |
| **Maintenance** | Minimal | Minimal |
| **Flexibility** | Limited | High |
| **Relevance** | Keywords only | Context-aware |

**My Recommendation**: Start with **Full-Text Search** (fast, free, good enough), then upgrade to **Semantic Search** once you confirm it's valuable.

---

**Ready to implement?** Let me know which approach you want, and I'll create the database migration scripts and Python tools!
