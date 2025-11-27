# 🧠 Memory Context - Visual Architecture Guide

**Purpose:** Visual diagrams showing how memory context works (and should work)

---

## 🔴 Current Reality: Memory Context NOT WORKING

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER EXECUTES TOOL                          │
│  User: "Send email to john@example.com about project update"   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    AI AGENT CALLS TOOL                          │
│  Tool: gmail_send_email                                         │
│  Parameters: {to: 'john@example.com', subject: 'Project Update'}│
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    REGISTRY EXECUTES TOOL                       │
│  registry.execute_tool('gmail_send_email', ...)                 │
│                                                                 │
│  Result: {                                                      │
│    success: true,                                               │
│    message_id: 'abc123',                                        │
│    to: 'john@example.com',                                      │
│    subject: 'Project Update'                                    │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│         ✅ TOOL INTELLIGENCE LOGGER (WORKING)                   │
│  Logs to: ai_infrastructure.ai_tool_intelligence_log           │
│  Data: execution_time, parameters, AI observation              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              ❌ MEMORY VECTORIZATION (NOT WORKING)              │
│  Should vectorize result and store in Pinecone                 │
│  BUT: No code reads memory_context from schema                 │
│  BUT: No code calls pinecone_upsert_vectors                    │
│  BUT: Result is NOT stored for future retrieval                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   RESULT RETURNED TO USER                       │
│  ✅ Tool worked                                                 │
│  ❌ But NOT searchable later                                    │
│  ❌ AI can't recall this action in future conversations        │
└─────────────────────────────────────────────────────────────────┘


=== LATER IN NEW CONVERSATION ===

┌─────────────────────────────────────────────────────────────────┐
│  User: "What was the subject of that email I sent to John?"    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    AI HAS NO MEMORY                             │
│  AI Response: "I don't have access to your past emails.        │
│   Could you check your Gmail Sent folder?"                      │
│                                                                 │
│  ❌ Can't search Pinecone (no vectors stored)                   │
│  ❌ Can't recall previous conversation                          │
│  ❌ User must manually find email                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🟢 Desired Flow: Memory Context WORKING

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER EXECUTES TOOL                          │
│  User: "Send email to john@example.com about project update"   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    AI AGENT CALLS TOOL                          │
│  Tool: gmail_send_email                                         │
│  Parameters: {to: 'john@example.com', subject: 'Project Update'}│
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    REGISTRY EXECUTES TOOL                       │
│  registry.execute_tool('gmail_send_email', ...)                 │
│                                                                 │
│  Result: {                                                      │
│    success: true,                                               │
│    message_id: 'abc123',                                        │
│    to: 'john@example.com',                                      │
│    subject: 'Project Update'                                    │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│         ✅ TOOL INTELLIGENCE LOGGER (WORKING)                   │
│  Logs to: ai_infrastructure.ai_tool_intelligence_log           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              ✅ MEMORY VECTORIZATION (NEW!)                     │
│                                                                 │
│  Step 1: Read memory_context from schema                       │
│    vectorization_fields: ['to', 'subject', 'message_id']       │
│                                                                 │
│  Step 2: Extract fields from result                            │
│    to: 'john@example.com'                                       │
│    subject: 'Project Update'                                    │
│    message_id: 'abc123'                                         │
│                                                                 │
│  Step 3: Build searchable text                                 │
│    "Email to john@example.com about Project Update"            │
│                                                                 │
│  Step 4: Generate embedding via OpenAI                          │
│    [0.123, 0.456, 0.789, ..., 0.321] (1536 dimensions)         │
│                                                                 │
│  Step 5: Store in Pinecone                                      │
│    Vector ID: gmail_send_email_7a3f8b2c                        │
│    Namespace: user_14                                           │
│    Metadata: {                                                  │
│      tool_name: 'gmail_send_email',                             │
│      user_id: 14,                                               │
│      timestamp: '2025-11-27T10:30:15',                          │
│      to: 'john@example.com',                                    │
│      subject: 'Project Update',                                 │
│      message_id: 'abc123'                                       │
│    }                                                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   RESULT RETURNED TO USER                       │
│  ✅ Tool worked                                                 │
│  ✅ Result vectorized and stored                                │
│  ✅ AI can recall this action in future conversations          │
└─────────────────────────────────────────────────────────────────┘


=== LATER IN NEW CONVERSATION ===

┌─────────────────────────────────────────────────────────────────┐
│  User: "What was the subject of that email I sent to John?"    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 AI SEARCHES MEMORY (PINECONE)                   │
│                                                                 │
│  Step 1: Generate embedding of question                        │
│    "email sent to John subject"                                 │
│    → [0.145, 0.423, 0.812, ..., 0.298]                         │
│                                                                 │
│  Step 2: Query Pinecone with semantic search                   │
│    Tool: pinecone_query_vectors                                 │
│    Parameters: {                                                │
│      query_text: 'email sent to John subject',                 │
│      top_k: 5,                                                  │
│      namespace: 'user_14'                                       │
│    }                                                            │
│                                                                 │
│  Step 3: Pinecone returns similar vectors                      │
│    Match 1: gmail_send_email_7a3f8b2c (score: 0.94)           │
│      Metadata: {                                                │
│        to: 'john@example.com',                                  │
│        subject: 'Project Update',                               │
│        timestamp: '2025-11-27T10:30:15'                         │
│      }                                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    AI RESPONDS WITH MEMORY                      │
│  AI: "I found the email you sent to John:                      │
│                                                                 │
│  Subject: Project Update                                        │
│  Sent to: john@example.com                                      │
│  Date: November 27, 2025 at 10:30 AM                           │
│  Message ID: abc123"                                            │
│                                                                 │
│  ✅ AI recalled past action                                     │
│  ✅ User didn't have to manually search                         │
│  ✅ Semantic search found correct email                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Schema → Vector Storage Flow

```
┌─────────────────────────────────────────────────────────────────┐
│         TOOL SCHEMA (gmail_tools.json)                          │
├─────────────────────────────────────────────────────────────────┤
│  "gmail_send_email": {                                          │
│    "parameters": {...},                                         │
│    "memory_context": {                     ← THIS SECTION!      │
│      "vectorization_fields": [            ← WHAT TO VECTORIZE  │
│        "to",                                                    │
│        "subject",                                               │
│        "message_id",                                            │
│        "thread_id"                                              │
│      ],                                                         │
│      "search_keywords": [                 ← HOW USER FINDS IT  │
│        "email", "send message", "correspondence"                │
│      ],                                                         │
│      "typical_use_cases": [               ← WHEN TO USE IT     │
│        "Customer communication",                                │
│        "Team collaboration"                                     │
│      ],                                                         │
│      "conversation_memory_hints": {       ← WHAT AI REMEMBERS  │
│        "what_to_remember": "Recipient emails, subjects",        │
│        "search_context": "emails I sent"                        │
│      }                                                          │
│    }                                                            │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│         MEMORY CONTEXT MANAGER (NEW!)                           │
│  File: AI_infrastructure/core/memory_context_manager.py        │
├─────────────────────────────────────────────────────────────────┤
│  def vectorize_tool_result():                                   │
│    # 1. Extract vectorization_fields from schema               │
│    fields = schema['memory_context']['vectorization_fields']   │
│                                                                 │
│    # 2. Build searchable text from result                      │
│    text = f"Email to {result['to']} about {result['subject']}" │
│                                                                 │
│    # 3. Generate embedding (1536 dimensions)                   │
│    embedding = openai.embeddings.create(                        │
│      input=text,                                                │
│      model="text-embedding-3-small"                             │
│    )                                                            │
│                                                                 │
│    # 4. Store in Pinecone                                      │
│    pinecone.upsert([{                                           │
│      'id': 'gmail_send_email_7a3f8b2c',                         │
│      'values': embedding,                                       │
│      'metadata': {                                              │
│        'tool_name': 'gmail_send_email',                         │
│        'to': result['to'],                                      │
│        'subject': result['subject']                             │
│      }                                                          │
│    }])                                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              PINECONE VECTOR DATABASE                           │
│  Index: inhouseprint                                            │
│  Namespace: user_14                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Vector: gmail_send_email_7a3f8b2c                             │
│  ├─ Values: [0.123, 0.456, ..., 0.789] (1536 dims)             │
│  └─ Metadata: {                                                 │
│       tool_name: 'gmail_send_email',                            │
│       user_id: 14,                                              │
│       timestamp: '2025-11-27T10:30:15',                         │
│       to: 'john@example.com',                                   │
│       subject: 'Project Update',                                │
│       message_id: 'abc123'                                      │
│     }                                                           │
│                                                                 │
│  Vector: gmail_send_email_9f2e1d4a                             │
│  ├─ Values: [0.234, 0.567, ..., 0.891]                         │
│  └─ Metadata: {                                                 │
│       to: 'sarah@company.com',                                  │
│       subject: 'Q4 Budget Review',                              │
│       timestamp: '2025-11-15T14:20:00'                          │
│     }                                                           │
│                                                                 │
│  Vector: google_docs_create_document_3c5a7b8f                  │
│  ├─ Values: [0.345, 0.678, ..., 0.012]                         │
│  └─ Metadata: {                                                 │
│       tool_name: 'google_docs_create_document',                 │
│       title: 'Project Proposal',                                │
│       document_id: 'doc_xyz789'                                 │
│     }                                                           │
│                                                                 │
│  ... (100,000+ vectors)                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Semantic Search Example

```
USER QUERY: "Show me the email about budget I sent to Sarah"
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Generate Query Embedding                               │
│                                                                 │
│  Text: "email about budget sent to Sarah"                      │
│  Embedding: [0.156, 0.489, 0.723, ..., 0.334] (1536 dims)      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: Pinecone Cosine Similarity Search                     │
│                                                                 │
│  Query Vector: [0.156, 0.489, ...]                             │
│  Against: All vectors in namespace user_14                     │
│                                                                 │
│  Similarity Scores:                                             │
│  • gmail_send_email_9f2e1d4a: 0.94 ← BEST MATCH!              │
│    (Subject: "Q4 Budget Review", to: "sarah@company.com")      │
│                                                                 │
│  • gmail_send_email_7a3f8b2c: 0.72                             │
│    (Subject: "Project Update", to: "john@example.com")         │
│                                                                 │
│  • google_docs_create_document_3c5a7b8f: 0.68                  │
│    (Title: "Budget Proposal Draft")                            │
│                                                                 │
│  • gmail_send_email_1a8b4c2d: 0.45                             │
│    (Subject: "Meeting Notes", to: "team@company.com")          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Return Top Matches                                    │
│                                                                 │
│  Top 3 Results:                                                 │
│                                                                 │
│  1. gmail_send_email_9f2e1d4a (score: 0.94)                    │
│     Subject: Q4 Budget Review                                   │
│     To: sarah@company.com                                       │
│     Date: Nov 15, 2025                                          │
│     Message ID: xyz789                                          │
│                                                                 │
│  2. gmail_send_email_7a3f8b2c (score: 0.72)                    │
│     Subject: Project Update                                     │
│     To: john@example.com                                        │
│     Date: Nov 27, 2025                                          │
│                                                                 │
│  3. google_docs_create_document_3c5a7b8f (score: 0.68)         │
│     Title: Budget Proposal Draft                                │
│     Document ID: doc_xyz789                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  AI RESPONSE:                                                   │
│                                                                 │
│  "I found the email about budget you sent to Sarah:            │
│                                                                 │
│  Subject: Q4 Budget Review                                      │
│  Sent to: sarah@company.com                                     │
│  Date: November 15, 2025                                        │
│  Message ID: xyz789                                             │
│                                                                 │
│  Would you like me to retrieve the full email content?"        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🗂️ Data Storage Comparison

### WITHOUT Memory Context (Current)
```
┌─────────────────────────────────────────────────────────────────┐
│  ai_tool_intelligence_log (PostgreSQL)                         │
├─────────────────────────────────────────────────────────────────┤
│  id: 1                                                          │
│  user_id: 14                                                    │
│  tool_name: 'gmail_send_email'                                  │
│  tool_parameters: {"to": "john@example.com", "subject": "..."}  │
│  execution_duration_ms: 1250                                    │
│  ai_observation: "User sent email to customer..."              │
│                                                                 │
│  ✅ STORES: Execution metadata                                  │
│  ❌ NOT SEARCHABLE: Can't find by semantic meaning             │
│  ❌ NOT REUSABLE: Can't recall in future conversations         │
└─────────────────────────────────────────────────────────────────┘
```

### WITH Memory Context (Desired)
```
┌─────────────────────────────────────────────────────────────────┐
│  ai_tool_intelligence_log (PostgreSQL)                         │
│  ✅ Same as before - execution metadata                        │
└─────────────────────────────────────────────────────────────────┘
                    PLUS
┌─────────────────────────────────────────────────────────────────┐
│  Pinecone Vector Database                                       │
├─────────────────────────────────────────────────────────────────┤
│  Vector ID: gmail_send_email_7a3f8b2c                          │
│  Values: [0.123, 0.456, ..., 0.789] (1536 dimensions)          │
│  Metadata: {                                                    │
│    tool_name: 'gmail_send_email',                               │
│    user_id: 14,                                                 │
│    to: 'john@example.com',                                      │
│    subject: 'Project Update',                                   │
│    message_id: 'abc123',                                        │
│    timestamp: '2025-11-27T10:30:15'                             │
│  }                                                              │
│                                                                 │
│  ✅ SEARCHABLE: Semantic meaning captured                       │
│  ✅ REUSABLE: Can recall in future conversations               │
│  ✅ FAST: Cosine similarity search in milliseconds             │
└─────────────────────────────────────────────────────────────────┘
```

---

**Last Updated:** November 27, 2025  
**Status:** Visual guide complete  
**Next:** Implement MemoryContextManager class
