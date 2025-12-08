# Workspace Search & Message Retrieval - Complete Testing Instructions

Use these instructions to systematically test all workspace search and message retrieval functionality.

---

## 🧪 TEST SUITE 1: Simple Keyword Search

### Test 1.1: Basic Keyword Search in Messages
```
Test workspace_simple_search with the following:
- search_query: "database performance"
- workspace_ids: [1, 2, 3]
- limit: 20

Expected results:
- Returns messages containing "database performance"
- Case-insensitive matching
- Results sorted by created_at DESC (newest first)
- Both messages and transcriptions searched

Verify the response includes:
- success: True
- results.messages: Array of matching messages
- results.transcriptions: Array of matching transcriptions
- total_count: Sum of messages + transcriptions found
- search_type: "simple"
```

### Test 1.2: Search Only Transcriptions
```
Test workspace_simple_search:
- search_query: "quarterly report"
- search_messages: false
- search_transcriptions: true
- limit: 30

Expected results:
- Only transcriptions returned (no messages)
- Messages array should be empty
- Searches both 'text' and 'whisper_text' fields
```

### Test 1.3: Wildcard Search
```
Test workspace_simple_search:
- search_query: "%deploy%production%"
- limit: 25

Expected results:
- Finds messages containing both "deploy" and "production" in any order
- Wildcard % works like SQL LIKE operator
```

### Test 1.4: Filter by User
```
Test workspace_simple_search:
- search_query: "pricing"
- user_id: 5
- workspace_ids: [1]
- limit: 50

Expected results:
- Only messages/transcriptions from user_id 5
- In workspace 1 only
- Containing "pricing"
```

---

## 🧪 TEST SUITE 2: Semantic Search (AI-Powered)

**⚠️ PREREQUISITES**: 
- Run migration script first: `python tools/migrations/enable_pgvector_and_populate_embeddings.py`
- Verify OPENAI_API_KEY is set: `echo $OPENAI_API_KEY`

### Test 2.1: Basic Semantic Search
```
Test workspace_semantic_search with the following:
- search_query: "Tell me about pricing strategy discussions"
- workspace_ids: [1, 2]
- similarity_threshold: 0.7
- limit: 10

Expected results:
- Finds messages about "cost structure", "revenue model", "pricing tiers"
- Even without exact keyword "pricing strategy"
- Results ranked by similarity_score (0.0-1.0)
- Higher scores = more relevant

Verify the response includes:
- success: True
- results: Array of messages with similarity_score field
- Results sorted by similarity_score DESC (most relevant first)
- search_type: "semantic"
```

### Test 2.2: Database Performance Query
```
Test workspace_semantic_search:
- search_query: "database performance issues"
- limit: 20

Expected results:
- Finds "SQL optimization", "query speed", "data store performance"
- Finds "slow queries", "database bottlenecks"
- WITHOUT requiring exact keyword "database performance"
```

### Test 2.3: High Precision Search
```
Test workspace_semantic_search:
- search_query: "Kubernetes deployment configuration"
- similarity_threshold: 0.85
- limit: 5

Expected results:
- Very strict matching (0.85 threshold)
- Only highly relevant results
- Fewer results but more precise
```

### Test 2.4: Fallback on Failure
```
Test workspace_semantic_search when pgvector not enabled:
- search_query: "test query"

Expected results if pgvector not enabled:
- success: False
- error: "pgvector extension not enabled..."
- fallback: "Use workspace_simple_search..."
- Suggests alternative endpoint
```

---

## 🧪 TEST SUITE 3: Message Retrieval

### Test 3.1: Get Recent Messages from Workspace
```
Test workspace_get_messages:
- workspace_ids: [1]
- limit: 50

Expected results:
- 50 most recent messages from workspace 1
- All roles (user, assistant, system)
- Full message details with workspace_name and user_name
```

### Test 3.2: Get Entire Thread Conversation
```
Test workspace_get_messages:
- thread_id: 42

Expected results:
- All messages from thread 42
- Complete conversation history
- Ordered chronologically (newest first)
- Useful for context retrieval
```

### Test 3.3: Get Messages by Date Range
```
Test workspace_get_messages:
- user_id: 5
- date_from: "2025-12-01"
- date_to: "2025-12-07"
- limit: 100

Expected results:
- All messages from user 5 in date range
- Inclusive dates (includes both start and end dates)
- Useful for "show me what we discussed last week"
```

### Test 3.4: Get Only AI Responses
```
Test workspace_get_messages:
- workspace_ids: [1]
- role: "assistant"
- limit: 200

Expected results:
- Only AI assistant responses
- No user messages or system messages
- Useful for reviewing AI's answers
```

### Test 3.5: Pagination Test
```
Test workspace_get_messages (Page 1):
- workspace_ids: [1, 2]
- limit: 100
- offset: 0

Then test Page 2:
- workspace_ids: [1, 2]
- limit: 100
- offset: 100

Expected results:
- total_count stays the same
- returned_count shows messages in this page
- has_more: true/false indicates more results
- No duplicate messages between pages
```

---

## 🧪 TEST SUITE 4: Transcription Retrieval

### Test 4.1: Get Recent Transcriptions
```
Test workspace_get_transcriptions:
- workspace_ids: [1]
- limit: 20

Expected results:
- 20 most recent transcriptions from workspace 1
- Both 'text' and 'whisper_text' fields populated
- Excludes deleted transcriptions (deleted_at IS NULL)
```

### Test 4.2: Get Transcriptions from Session
```
Test workspace_get_transcriptions:
- session_id: 789

Expected results:
- All transcriptions from session 789
- Chronological order (newest first)
- Useful for session review
```

### Test 4.3: Find Long Transcriptions
```
Test workspace_get_transcriptions:
- min_duration: 120
- limit: 30

Expected results:
- Only transcriptions longer than 2 minutes (120 seconds)
- Useful for finding substantial recordings
- Duration field in seconds
```

### Test 4.4: Get Whisper AI Transcriptions
```
Test workspace_get_transcriptions:
- transcription_mode: "whisper"
- date_from: "2025-12-01"
- date_to: "2025-12-07"
- limit: 50

Expected results:
- Only Whisper AI transcriptions (highest quality)
- Within date range
- whisper_text field should be populated
```

### Test 4.5: Find Short Recordings
```
Test workspace_get_transcriptions:
- max_duration: 30
- limit: 10

Expected results:
- Only transcriptions 30 seconds or shorter
- Useful for finding brief voice notes
```

---

## 🧪 TEST SUITE 5: API Endpoint Testing

### Test 5.1: Simple Search Endpoint
```
POST http://localhost:5000/api/v1/workspace/search

Body:
{
  "search_query": "database performance",
  "workspace_ids": [1, 2, 3],
  "limit": 20
}

Expected HTTP 200:
{
  "success": true,
  "results": {
    "messages": [...],
    "transcriptions": [...]
  },
  "total_count": 15,
  "search_type": "simple"
}
```

### Test 5.2: Semantic Search Endpoint
```
POST http://localhost:5000/api/v1/workspace/semantic-search

Body:
{
  "search_query": "Tell me about pricing discussions",
  "workspace_ids": [1, 2],
  "similarity_threshold": 0.7,
  "limit": 10
}

Expected HTTP 200:
{
  "success": true,
  "results": [
    {
      "id": 12345,
      "content": "...",
      "similarity_score": 0.89,
      "workspace_name": "Engineering",
      "user_name": "sarah"
    }
  ],
  "total_count": 8,
  "search_type": "semantic"
}
```

### Test 5.3: Messages Endpoint
```
POST http://localhost:5000/api/v1/workspace/messages

Body:
{
  "workspace_ids": [1],
  "thread_id": 42,
  "limit": 100
}

Expected HTTP 200:
{
  "success": true,
  "messages": [...],
  "total_count": 87,
  "returned_count": 87,
  "has_more": false
}
```

### Test 5.4: Transcriptions Endpoint
```
POST http://localhost:5000/api/v1/workspace/transcriptions

Body:
{
  "workspace_ids": [1],
  "transcription_mode": "whisper",
  "min_duration": 120,
  "limit": 50
}

Expected HTTP 200:
{
  "success": true,
  "transcriptions": [...],
  "total_count": 23,
  "returned_count": 23,
  "has_more": false
}
```

---

## 🧪 TEST SUITE 6: Error Handling

### Test 6.1: Missing Required Parameter
```
POST http://localhost:5000/api/v1/workspace/search

Body:
{
  "workspace_ids": [1],
  "limit": 20
}

Expected HTTP 400:
{
  "success": false,
  "error": "search_query is required"
}
```

### Test 6.2: Semantic Search Without pgvector
```
POST http://localhost:5000/api/v1/workspace/semantic-search

Body:
{
  "search_query": "test"
}

Expected HTTP 503 (if pgvector not enabled):
{
  "success": false,
  "error": "pgvector extension not enabled...",
  "fallback": "Use workspace_simple_search..."
}
```

### Test 6.3: Invalid Workspace IDs
```
Test workspace_get_messages:
- workspace_ids: [9999999]
- limit: 50

Expected results:
- success: True
- messages: [] (empty array)
- total_count: 0
- No error (just empty results)
```

---

## 📊 COMPREHENSIVE TEST RESULTS TEMPLATE

```
═══════════════════════════════════════════════════════════════
WORKSPACE SEARCH TOOLS TEST RESULTS SUMMARY
═══════════════════════════════════════════════════════════════

Test Date: [Date]
Database: Supabase PostgreSQL
Total Tests: 24

───────────────────────────────────────────────────────────────
SUITE 1: Simple Keyword Search (4 tests)
───────────────────────────────────────────────────────────────
✅ Test 1.1: Basic Keyword Search - PASS
   - Found: [X] messages, [Y] transcriptions
   - Total: [X+Y] results

✅ Test 1.2: Search Only Transcriptions - PASS
   - Messages: 0 (expected)
   - Transcriptions: [X]

✅ Test 1.3: Wildcard Search - PASS
   - Results contained both keywords

✅ Test 1.4: Filter by User - PASS
   - All results from user_id 5

───────────────────────────────────────────────────────────────
SUITE 2: Semantic Search (4 tests)
───────────────────────────────────────────────────────────────
[✅/⚠️] Test 2.1: Basic Semantic Search - [PASS/SKIP]
   - Status: [Requires pgvector setup]
   - Results: [X] messages with similarity scores

[✅/⚠️] Test 2.2: Database Performance Query - [PASS/SKIP]
   - Found related terms without exact keywords

[✅/⚠️] Test 2.3: High Precision Search - [PASS/SKIP]
   - Threshold 0.85 returned [X] highly relevant results

[✅/⚠️] Test 2.4: Fallback on Failure - PASS
   - Proper error message and fallback suggestion

───────────────────────────────────────────────────────────────
SUITE 3: Message Retrieval (5 tests)
───────────────────────────────────────────────────────────────
✅ Test 3.1: Get Recent Messages - PASS
   - Retrieved [X] messages

✅ Test 3.2: Get Thread Conversation - PASS
   - Thread [ID] has [X] messages

✅ Test 3.3: Get Messages by Date Range - PASS
   - Date range working correctly

✅ Test 3.4: Get Only AI Responses - PASS
   - All messages have role='assistant'

✅ Test 3.5: Pagination Test - PASS
   - No duplicates between pages
   - has_more flag correct

───────────────────────────────────────────────────────────────
SUITE 4: Transcription Retrieval (5 tests)
───────────────────────────────────────────────────────────────
✅ Test 4.1: Get Recent Transcriptions - PASS
✅ Test 4.2: Get from Session - PASS
✅ Test 4.3: Find Long Transcriptions - PASS
✅ Test 4.4: Get Whisper AI Transcriptions - PASS
✅ Test 4.5: Find Short Recordings - PASS

───────────────────────────────────────────────────────────────
SUITE 5: API Endpoint Testing (4 tests)
───────────────────────────────────────────────────────────────
✅ Test 5.1: Simple Search Endpoint - PASS (HTTP 200)
[✅/⚠️] Test 5.2: Semantic Search Endpoint - [PASS/SKIP]
✅ Test 5.3: Messages Endpoint - PASS (HTTP 200)
✅ Test 5.4: Transcriptions Endpoint - PASS (HTTP 200)

───────────────────────────────────────────────────────────────
SUITE 6: Error Handling (3 tests)
───────────────────────────────────────────────────────────────
✅ Test 6.1: Missing Parameter - Proper validation (HTTP 400)
✅ Test 6.2: Semantic Search Without pgvector - Proper fallback
✅ Test 6.3: Invalid Workspace IDs - Graceful handling

───────────────────────────────────────────────────────────────
OVERALL RESULTS
───────────────────────────────────────────────────────────────
Tests Passed: [X]/24
Tests Skipped: [Y]/24 (Semantic search requires setup)
Pass Rate: [XX]%

Core Functionality Status: ✅ FULLY FUNCTIONAL
Simple Search: ✅ WORKING
Semantic Search: [✅ WORKING / ⚠️ REQUIRES SETUP]
Message Retrieval: ✅ WORKING
Transcription Retrieval: ✅ WORKING
API Endpoints: ✅ WORKING

═══════════════════════════════════════════════════════════════
```

---

## 🎯 QUICK REFERENCE: Copy-Paste Test Commands

### Python Testing
```python
from tools.implementations.workspace_search import *

# Test 1: Simple search
result = workspace_simple_search(
    search_query="database performance",
    workspace_ids=[1, 2, 3],
    limit=20
)

# Test 2: Semantic search
result = workspace_semantic_search(
    search_query="Tell me about pricing discussions",
    workspace_ids=[1, 2],
    similarity_threshold=0.7,
    limit=10
)

# Test 3: Get messages
result = workspace_get_messages(
    workspace_ids=[1],
    thread_id=42,
    limit=100
)

# Test 4: Get transcriptions
result = workspace_get_transcriptions(
    workspace_ids=[1],
    transcription_mode="whisper",
    min_duration=120,
    limit=50
)
```

### cURL Testing
```bash
# Simple search
curl -X POST http://localhost:5000/api/v1/workspace/search \
  -H "Content-Type: application/json" \
  -d '{"search_query":"database performance","workspace_ids":[1,2,3],"limit":20}'

# Semantic search
curl -X POST http://localhost:5000/api/v1/workspace/semantic-search \
  -H "Content-Type: application/json" \
  -d '{"search_query":"pricing discussions","similarity_threshold":0.7,"limit":10}'

# Get messages
curl -X POST http://localhost:5000/api/v1/workspace/messages \
  -H "Content-Type: application/json" \
  -d '{"workspace_ids":[1],"thread_id":42,"limit":100}'

# Get transcriptions
curl -X POST http://localhost:5000/api/v1/workspace/transcriptions \
  -H "Content-Type: application/json" \
  -d '{"workspace_ids":[1],"transcription_mode":"whisper","limit":50}'
```

---

## ⚠️ IMPORTANT NOTES FOR TESTERS

1. **Semantic Search Setup**: Requires one-time migration
   - Run: `python tools/migrations/enable_pgvector_and_populate_embeddings.py`
   - Cost: ~$2-3 for ~10,000 messages
   - Time: ~15-30 minutes

2. **Database Access**: Ensure environment variables are set
   - SUPABASE_HOST
   - SUPABASE_USER
   - SUPABASE_PASSWORD
   - SUPABASE_DATABASE (default: postgres)
   - SUPABASE_PORT (default: 5432)
   - OPENAI_API_KEY (for semantic search)

3. **Test Data**: Tests assume existing data
   - Workspace IDs 1, 2, 3 should exist
   - Messages with various content
   - Transcriptions in database
   - If no data, create test messages first

4. **Rate Limiting**: Semantic search uses OpenAI API
   - Max 3000 requests/minute
   - Each search = 1 API call
   - Cost: ~$0.02 per 1M tokens

5. **Performance**: 
   - Simple search: < 100ms
   - Semantic search: 200-500ms (includes OpenAI API call)
   - Message retrieval: < 50ms
   - Transcription retrieval: < 50ms

---

## 📚 ADDITIONAL RESOURCES

- **Tool Schemas**: `tools/schemas/workspace_search_tools.json`
- **Implementation**: `tools/implementations/workspace_search.py`
- **API Routes**: `AI_infrastructure/routes/workspace_search_routes.py`
- **Migration Script**: `tools/migrations/enable_pgvector_and_populate_embeddings.py`
- **Documentation**: `WORKSPACE_SEARCH_COMPLETE_GUIDE.md`

---

**Testing Complete!** Use these instructions to thoroughly test all workspace search and message retrieval functionality.
