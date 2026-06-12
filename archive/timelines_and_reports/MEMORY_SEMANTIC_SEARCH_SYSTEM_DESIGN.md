# Memory & Semantic Search System - Complete Architecture

**Date:** November 27, 2025  
**Purpose:** Add semantic search, summarization, and compression to conversation/Synergy data

---

## 🧠 Overview - Tool Intelligence vs Memory System

**CRITICAL CLARIFICATION:**

1. **Tool Intelligence Log (Silent Platform Learning)** - NOT FOR AI ACCESS
   - Purpose: Platform improvement by analyzing tool usage patterns
   - Data: Tool execution logs (errors, workflows, patterns, refinements)
   - Access: **NEVER exposed to AI** - only for human dashboard analysis
   - Goal: Improve platform UX, onboarding, automation suggestions
   - Status: ✅ Complete (from previous design)

2. **Memory & Semantic Search (This Design)** - FOR AI ACCESS
   - Purpose: AI can search and recall previous conversations/work
   - Data: Conversation threads, messages, Synergy sessions, documents
   - Access: **AI tools** for real-time context retrieval
   - Goal: AI remembers past work, avoids redoing tasks, finds relevant context
   - Status: 🚀 NEW DESIGN

---

## 📊 Current Data Architecture Analysis

### **Existing Data Sources:**

**1. Conversation Data (PostgreSQL - `sessions` schema)**
```sql
-- Threads (conversations)
sessions.threads
├── id (primary key)
├── title
├── user_id
├── created_at
├── updated_at
├── thread_type ('chat', 'agent', 'automation')
└── metadata (JSONB)

-- Messages (conversation history)
sessions.messages
├── id (primary key)
├── thread_id (foreign key)
├── role ('user', 'assistant', 'system')
├── content (TEXT - markdown, tool results, thinking blocks)
├── created_at
└── metadata (JSONB - thinking_blocks, tool_use, citations)
```

**2. Synergy Project Data (PostgreSQL - `synergy_sessions` schema)**
```sql
-- Synergy sessions (projects)
synergy_sessions.sessions
├── id (primary key)
├── user_id
├── title
├── description (TEXT - project context)
├── platforms_involved (TEXT[] - ['gmail', 'sheets', 'docs'])
├── next_steps (JSONB[] - checklist items)
├── documents (JSONB[] - [{title, url, type}])
├── links (JSONB[])
├── tags (TEXT[])
├── priority ('low', 'medium', 'high', 'critical')
├── status ('active', 'completed', 'archived')
├── created_at
└── updated_at

-- Milestones (project phases)
synergy_sessions.milestones
├── id (primary key)
├── session_id (foreign key)
├── title
├── description
├── tasks (JSONB[])
├── documents (JSONB[])
└── metadata
```

**3. Pinecone Integration (Already Available)**
```python
# From: AI_infrastructure/routes/vector_db/vector_db_routes.py
# 9 endpoints already implemented:
- POST /api/vector-db/credentials/save
- GET /api/vector-db/credentials/get
- POST /api/vector-db/test-connection
- POST /api/vector-db/embedding-config/save
- POST /api/vector-db/upload-document
- GET /api/vector-db/stats
- GET /api/vector-db/documents
- DELETE /api/vector-db/document/<doc_id>
```

---

## 🎯 Design Goals

### **What We Need:**

1. **Semantic Search Across Conversations**
   - User: "What did we discuss about the customer database last month?"
   - AI: Searches vectorized conversation history, returns relevant threads

2. **Synergy Project Memory**
   - User: "What projects have I worked on with Google Sheets?"
   - AI: Semantic search across Synergy sessions by platform tags

3. **Auto-Summarization (Token Compression)**
   - Problem: Threads with 50+ messages exceed context window
   - Solution: Auto-summarize old messages (100 messages → 1 paragraph)

4. **Conversation Continuation**
   - User returns after 3 days: "Continue that email automation project"
   - AI: Semantic search finds thread, loads summary, resumes work

5. **Cross-Thread Context**
   - User: "Remember that validation formula I used in the sales project?"
   - AI: Searches across ALL threads for code snippets, formulas, solutions

---

## 🧩 System Architecture

### **Component 1: Conversation Vectorization**

**What to Vectorize:**
```python
# For each conversation thread:
vectorized_content = {
    'thread_id': thread.id,
    'user_id': thread.user_id,
    'title': thread.title,
    'summary': summarize_thread(thread),  # AI-generated
    'key_topics': extract_topics(thread),  # ['email', 'automation', 'gmail']
    'tools_used': extract_tools(thread),  # ['gmail_send_email', 'synergy_create_session']
    'created_at': thread.created_at,
    'message_count': len(thread.messages)
}

# Vector metadata (stored in Pinecone):
metadata = {
    'type': 'conversation_thread',
    'thread_id': thread.id,
    'user_id': thread.user_id,
    'title': thread.title,
    'summary': summary[:500],  # Truncated
    'tools': json.dumps(tools_used),
    'created_at': created_at.isoformat()
}
```

**Embedding Strategy:**
- **Combine:** title + summary + key topics → single text block
- **Embed:** OpenAI `text-embedding-ada-002` (1536 dimensions)
- **Store:** Pinecone with metadata for filtering
- **Namespace:** `user_{user_id}_conversations`

---

### **Component 2: Synergy Session Vectorization**

**What to Vectorize:**
```python
# For each Synergy session:
vectorized_session = {
    'session_id': session.id,
    'user_id': session.user_id,
    'title': session.title,
    'description': session.description,
    'platforms_involved': session.platforms_involved,  # ['gmail', 'sheets']
    'next_steps': [step['text'] for step in session.next_steps],
    'documents': [doc['title'] for doc in session.documents],
    'tags': session.tags,
    'status': session.status,
    'priority': session.priority
}

# Vector metadata:
metadata = {
    'type': 'synergy_session',
    'session_id': session.id,
    'user_id': session.user_id,
    'title': session.title,
    'description': session.description[:500],
    'platforms': json.dumps(session.platforms_involved),
    'status': session.status,
    'priority': session.priority
}
```

**Embedding Strategy:**
- **Combine:** title + description + platforms + tags + next_steps → text block
- **Embed:** OpenAI `text-embedding-ada-002`
- **Store:** Pinecone
- **Namespace:** `user_{user_id}_synergy_sessions`

---

### **Component 3: Auto-Summarization (Token Compression)**

**Problem:**
- Thread with 50 messages = 30,000+ tokens
- Claude 200K limit = can only load ~6 threads
- Need: Compress old conversations for context efficiency

**Solution: Progressive Summarization**

```python
def progressive_summarize_thread(thread_id: int) -> Dict[str, str]:
    """
    Summarize thread in layers:
    1. Recent messages (last 10) → FULL TEXT (detailed context)
    2. Middle messages (11-30) → SUMMARY (key points only)
    3. Old messages (31+) → COMPRESSED SUMMARY (1 paragraph)
    
    Returns:
        {
            'full_messages': [last 10 messages],  # ~5,000 tokens
            'middle_summary': 'User worked on...',  # ~1,000 tokens
            'old_summary': 'Early discussion...',  # ~200 tokens
            'total_tokens_saved': 24800  # 30,000 → 6,200
        }
    """
    messages = get_thread_messages(thread_id)
    
    # Layer 1: Recent (keep full)
    recent = messages[-10:]
    
    # Layer 2: Middle (summarize per 5-message chunks)
    middle = messages[-30:-10]
    middle_summary = summarize_chunks(middle, chunk_size=5)
    
    # Layer 3: Old (compress to 1 paragraph)
    old = messages[:-30]
    old_summary = summarize_compressed(old)
    
    return {
        'full_messages': recent,
        'middle_summary': middle_summary,
        'old_summary': old_summary,
        'metadata': {
            'total_messages': len(messages),
            'recent_count': len(recent),
            'middle_count': len(middle),
            'old_count': len(old)
        }
    }
```

**Storage Strategy:**
- Store summaries in PostgreSQL: `sessions.thread_summaries`
- Regenerate when thread updated (async background task)
- Cache in Redis for fast access

---

### **Component 4: Semantic Search Tools**

**Tool 1: `search_past_conversations()`**

```python
def search_past_conversations(
    query: str,
    user_id: int,
    limit: int = 5,
    time_filter: Optional[str] = None,  # 'last_week', 'last_month', 'last_year'
    thread_type: Optional[str] = None  # 'chat', 'agent', 'automation'
) -> Dict[str, Any]:
    """
    Semantic search across user's conversation history
    
    Examples:
        query="customer database project" 
        → Returns threads about databases, customers, CRM work
        
        query="email automation with Gmail"
        → Returns threads using gmail tools
        
        query="spreadsheet validation formulas"
        → Returns code/formulas from past work
    
    Returns:
        {
            'results': [
                {
                    'thread_id': 42,
                    'title': 'Customer Database Setup',
                    'summary': 'User created Google Sheet database...',
                    'similarity_score': 0.92,
                    'created_at': '2025-11-20',
                    'message_count': 28,
                    'tools_used': ['google_sheets_create', 'synergy_create_session']
                }
            ],
            'total_results': 5
        }
    """
    # 1. Generate query embedding
    query_embedding = openai.Embedding.create(
        input=query,
        model="text-embedding-ada-002"
    )
    
    # 2. Search Pinecone
    results = pinecone_index.query(
        vector=query_embedding,
        top_k=limit,
        namespace=f"user_{user_id}_conversations",
        filter={
            'user_id': user_id,
            **(time_filter and {'created_at': {'$gte': time_filter_date}}),
            **(thread_type and {'thread_type': thread_type})
        },
        include_metadata=True
    )
    
    # 3. Load thread summaries from PostgreSQL
    thread_ids = [r['metadata']['thread_id'] for r in results.matches]
    summaries = get_thread_summaries(thread_ids)
    
    # 4. Return enriched results
    return format_search_results(results, summaries)
```

---

**Tool 2: `search_synergy_projects()`**

```python
def search_synergy_projects(
    query: str,
    user_id: int,
    limit: int = 5,
    platforms: Optional[List[str]] = None,  # ['gmail', 'sheets']
    status: Optional[str] = None,  # 'active', 'completed'
    priority: Optional[str] = None  # 'high', 'critical'
) -> Dict[str, Any]:
    """
    Semantic search across Synergy project sessions
    
    Examples:
        query="email marketing campaigns"
        → Returns sessions with email/marketing work
        
        query="Google Sheets databases"
        → Returns sessions using sheets platform
        
        query="high priority automation projects"
        → Filters by priority and automation keywords
    
    Returns:
        {
            'results': [
                {
                    'session_id': 'sess_abc123',
                    'title': 'Email Campaign Automation',
                    'description': 'Automated newsletter system...',
                    'platforms_involved': ['gmail', 'sheets', 'forms'],
                    'status': 'active',
                    'priority': 'high',
                    'similarity_score': 0.89,
                    'documents_count': 5
                }
            ],
            'total_results': 3
        }
    """
    # Similar to search_past_conversations but:
    # - Searches namespace: user_{user_id}_synergy_sessions
    # - Filters by platforms_involved, status, priority
    # - Returns session metadata with documents/links
```

---

**Tool 3: `recall_thread_context()`**

```python
def recall_thread_context(
    thread_id: int,
    user_id: int,
    include_full_history: bool = False
) -> Dict[str, Any]:
    """
    Load thread context with progressive summarization
    
    Use when:
    - User says "continue that project"
    - Resuming work after days/weeks
    - Need full context without token overflow
    
    Returns:
        {
            'thread_id': 42,
            'title': 'Customer Database Setup',
            'created_at': '2025-11-15',
            'last_updated': '2025-11-20',
            
            # Summarized context (token-efficient)
            'summary': {
                'old_messages': 'User initially discussed...',  # 200 tokens
                'middle_messages': 'Then worked on schema...',  # 1000 tokens
                'recent_messages': [...last 10 full messages...]  # 5000 tokens
            },
            
            # Synergy session linked (if any)
            'synergy_session_id': 'sess_abc123',
            'synergy_project': {
                'title': 'Customer Database',
                'status': 'in_progress',
                'documents': [...]
            },
            
            # Tools used
            'tools_history': ['google_sheets_create', 'synergy_create_session'],
            
            # Token efficiency
            'tokens_saved': 24800,  # vs loading full history
            'full_message_count': 47
        }
    """
    # 1. Get thread from PostgreSQL
    thread = get_thread(thread_id, user_id)
    
    # 2. Get progressive summary
    summary = progressive_summarize_thread(thread_id)
    
    # 3. Get linked Synergy session (if exists)
    synergy_session = get_linked_synergy_session(thread_id)
    
    # 4. Extract tools used
    tools_history = extract_tools_from_thread(thread_id)
    
    return format_thread_context(thread, summary, synergy_session, tools_history)
```

---

**Tool 4: `remember_code_snippet()`**

```python
def remember_code_snippet(
    query: str,
    user_id: int,
    language: Optional[str] = None,  # 'python', 'javascript', 'sql'
    limit: int = 3
) -> Dict[str, Any]:
    """
    Search for code snippets from past conversations
    
    Examples:
        query="validation formula for email addresses"
        → Returns RegEx or validation code from past work
        
        query="Python script for CSV processing"
        → Returns pandas code snippets
        
        query="SQL query for grouping by date"
        → Returns GROUP BY examples
    
    Returns:
        {
            'snippets': [
                {
                    'thread_id': 42,
                    'thread_title': 'Email Validator Project',
                    'code': 'import re\ndef validate_email(email): ...',
                    'language': 'python',
                    'context': 'User asked for email validation...',
                    'similarity_score': 0.91
                }
            ]
        }
    """
    # 1. Search conversations with code_block metadata
    # 2. Extract code from messages.metadata.thinking_blocks
    # 3. Rank by similarity to query
    # 4. Return code with context
```

---

### **Component 5: Auto-Summarization Triggers**

**When to Summarize:**

1. **Threshold-Based (Automatic)**
   ```python
   # Background task runs every hour
   def auto_summarize_threads():
       threads = get_threads_needing_summary()
       for thread in threads:
           if thread.message_count > 30 and not has_recent_summary(thread):
               generate_summary_async(thread.id)
   
   # Criteria:
   # - Thread has 30+ messages
   # - Last summary >7 days old
   # - Thread still active (updated within 30 days)
   ```

2. **On-Demand (User Request)**
   ```python
   # User: "Summarize this conversation"
   # AI calls: summarize_current_thread(thread_id)
   ```

3. **Before Context Loading**
   ```python
   # When AI loads thread context, check if summary exists
   # If not, generate on-the-fly (with caching)
   ```

---

## 🗄️ Database Schema Extensions

### **New Table 1: `sessions.thread_summaries`**

```sql
CREATE TABLE sessions.thread_summaries (
    id SERIAL PRIMARY KEY,
    thread_id INTEGER NOT NULL REFERENCES sessions.threads(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL,
    
    -- Summarization layers
    old_summary TEXT,  -- Messages 31+ compressed
    middle_summary TEXT,  -- Messages 11-30 summarized
    
    -- Metadata
    total_messages INTEGER,  -- Total messages when summarized
    recent_messages_count INTEGER DEFAULT 10,  -- How many kept full
    
    -- Extraction
    key_topics TEXT[],  -- ['email', 'automation', 'gmail']
    tools_used TEXT[],  -- ['gmail_send_email', 'synergy_create_session']
    platforms_involved TEXT[],  -- ['gmail', 'google_sheets']
    
    -- Token efficiency
    original_tokens INTEGER,  -- Before summarization
    compressed_tokens INTEGER,  -- After summarization
    tokens_saved INTEGER,  -- Difference
    
    -- Timestamps
    generated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,  -- Auto-regenerate after 30 days
    
    -- Indexing
    INDEX idx_thread_summaries_thread (thread_id),
    INDEX idx_thread_summaries_user (user_id),
    INDEX idx_thread_summaries_expiry (expires_at)
);
```

---

### **New Table 2: `sessions.vectorization_queue`**

```sql
CREATE TABLE sessions.vectorization_queue (
    id SERIAL PRIMARY KEY,
    
    -- What to vectorize
    entity_type VARCHAR(50) NOT NULL,  -- 'thread', 'synergy_session', 'message'
    entity_id VARCHAR(100) NOT NULL,
    user_id INTEGER NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'processing', 'completed', 'failed'
    priority INTEGER DEFAULT 5,  -- 1-10 (10 = urgent)
    
    -- Processing
    attempts INTEGER DEFAULT 0,
    last_attempt_at TIMESTAMP,
    error_message TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    
    INDEX idx_vectorization_queue_status (status, priority),
    INDEX idx_vectorization_queue_entity (entity_type, entity_id)
);
```

**Usage:**
- Background worker processes queue
- When thread updated → add to queue
- When Synergy session created → add to queue
- Retry failed vectorizations (max 3 attempts)

---

## 🔧 Implementation Plan

### **Phase 1: Vectorization Infrastructure (Week 1)**

**Step 1: Pinecone Setup**
```python
# tools/implementations/vector_memory.py

import openai
import pinecone
from typing import Dict, Any, List, Optional

class VectorMemoryManager:
    """Manages vectorization and semantic search"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.pinecone_client = self._init_pinecone()
        self.index = self.pinecone_client.Index('synergy-memory')
    
    def vectorize_thread(self, thread_id: int):
        """Vectorize conversation thread"""
        # 1. Get thread data
        thread = get_thread(thread_id)
        summary = generate_thread_summary(thread)
        
        # 2. Create text for embedding
        text = f"{thread.title}\n\n{summary}\n\nTopics: {', '.join(thread.topics)}"
        
        # 3. Generate embedding
        embedding = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"
        )['data'][0]['embedding']
        
        # 4. Store in Pinecone
        self.index.upsert(
            vectors=[{
                'id': f"thread_{thread_id}",
                'values': embedding,
                'metadata': {
                    'type': 'conversation_thread',
                    'thread_id': thread_id,
                    'user_id': self.user_id,
                    'title': thread.title,
                    'summary': summary[:500],
                    'created_at': thread.created_at.isoformat()
                }
            }],
            namespace=f"user_{self.user_id}_conversations"
        )
```

**Step 2: Background Worker**
```python
# AI_infrastructure/workers/vectorization_worker.py

import time
from vector_memory import VectorMemoryManager

def process_vectorization_queue():
    """Background worker - runs every 5 minutes"""
    while True:
        pending = get_pending_vectorizations(limit=10)
        
        for item in pending:
            try:
                update_status(item.id, 'processing')
                
                manager = VectorMemoryManager(item.user_id)
                
                if item.entity_type == 'thread':
                    manager.vectorize_thread(item.entity_id)
                elif item.entity_type == 'synergy_session':
                    manager.vectorize_synergy_session(item.entity_id)
                
                update_status(item.id, 'completed')
                
            except Exception as e:
                update_status(item.id, 'failed', error=str(e))
                increment_attempts(item.id)
        
        time.sleep(300)  # 5 minutes
```

---

### **Phase 2: Summarization Engine (Week 2)**

**Step 1: Summarization Service**
```python
# AI_infrastructure/services/summarization_service.py

import anthropic
from typing import List, Dict

class SummarizationService:
    """Generate progressive summaries of threads"""
    
    def __init__(self):
        self.client = anthropic.Anthropic()
    
    def summarize_thread(self, thread_id: int) -> Dict[str, str]:
        """Progressive summarization"""
        messages = get_thread_messages(thread_id)
        
        # Recent (keep full)
        recent = messages[-10:]
        
        # Middle (5-message chunks)
        middle = messages[-30:-10]
        middle_summary = self._summarize_chunk(middle, detail_level='moderate')
        
        # Old (compress to paragraph)
        old = messages[:-30]
        old_summary = self._summarize_chunk(old, detail_level='brief')
        
        return {
            'old_summary': old_summary,
            'middle_summary': middle_summary,
            'recent_messages': recent,
            'metadata': {
                'total_messages': len(messages),
                'tokens_saved': self._calculate_tokens_saved(messages)
            }
        }
    
    def _summarize_chunk(self, messages: List[Dict], detail_level: str) -> str:
        """Summarize message chunk using Claude"""
        prompt = f"""Summarize this conversation segment ({detail_level} detail):

{self._format_messages(messages)}

Summary:"""
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500 if detail_level == 'moderate' else 200,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
```

---

### **Phase 3: AI Tools Integration (Week 3)**

**Tool Schema: `tools/schemas/memory_tools.json`**

```json
{
  "platform": "memory",
  "description": "Semantic memory and search tools for recalling past conversations and work",
  "tools": [
    {
      "name": "search_past_conversations",
      "description": "Search your conversation history semantically. Use when user references past work or asks 'what did we discuss about X?'",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "What to search for (natural language)"
          },
          "limit": {
            "type": "integer",
            "default": 5,
            "description": "Max results to return"
          },
          "time_filter": {
            "type": "string",
            "enum": ["last_week", "last_month", "last_year", "all_time"],
            "description": "Time range to search"
          }
        },
        "required": ["query"]
      }
    },
    {
      "name": "search_synergy_projects",
      "description": "Search Synergy project sessions semantically. Use when user asks about past projects or work involving specific platforms.",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "What to search for"
          },
          "platforms": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Filter by platforms: ['gmail', 'sheets', etc.]"
          },
          "status": {
            "type": "string",
            "enum": ["active", "completed", "archived"],
            "description": "Filter by project status"
          }
        },
        "required": ["query"]
      }
    },
    {
      "name": "recall_thread_context",
      "description": "Load full context of a previous conversation with progressive summarization. Use when resuming work or when user says 'continue that project'.",
      "parameters": {
        "type": "object",
        "properties": {
          "thread_id": {
            "type": "integer",
            "description": "Thread ID from search results"
          }
        },
        "required": ["thread_id"]
      }
    },
    {
      "name": "summarize_current_thread",
      "description": "Generate summary of the current conversation. Use when user asks for summary or when thread has 30+ messages.",
      "parameters": {
        "type": "object",
        "properties": {
          "include_code": {
            "type": "boolean",
            "default": true,
            "description": "Include code snippets in summary"
          },
          "include_decisions": {
            "type": "boolean",
            "default": true,
            "description": "Highlight key decisions made"
          }
        },
        "required": []
      }
    },
    {
      "name": "remember_code_snippet",
      "description": "Search for code snippets from past conversations. Use when user asks 'how did I do X before?' or needs reusable code.",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "What code/formula to search for"
          },
          "language": {
            "type": "string",
            "enum": ["python", "javascript", "sql", "any"],
            "description": "Programming language filter"
          }
        },
        "required": ["query"]
      }
    }
  ]
}
```

---

## 🎯 Use Case Examples

### **Example 1: Resume Previous Work**

**User:** "Continue that email automation project from last week"

**AI Workflow:**
```python
# 1. Semantic search
results = search_past_conversations(
    query="email automation project",
    time_filter="last_month"
)

# 2. Find best match
thread = results[0]  # "Email Campaign Automation"

# 3. Load context
context = recall_thread_context(thread['thread_id'])

# 4. Resume work
AI: "Found your email automation project: **Email Campaign Automation**

**Summary:** You were building an automated newsletter system using Gmail and Google Forms. The setup included:
- Gmail API for sending campaigns
- Google Forms for subscriber sign-ups  
- Google Sheets for contact management
- Synergy session tracking progress

**Last step:** You created the Gmail draft template. 
**Next:** We need to set up the automation scheduler.

Would you like to continue from here?"
```

---

### **Example 2: Find Reusable Code**

**User:** "How did I validate email addresses in that form project?"

**AI Workflow:**
```python
# 1. Search code snippets
snippets = remember_code_snippet(
    query="email validation formula",
    language="any"
)

# 2. Return with context
AI: "Found your email validation code from the **Customer Signup Form** project (Nov 15):

```javascript
function validateEmail(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}
```

You used this in the Google Forms validation script. It checks for:
- At least one character before @
- Domain with period
- No spaces

Would you like me to reuse this formula in your current project?"
```

---

### **Example 3: Find Past Project**

**User:** "What projects have I done with Google Sheets and high priority?"

**AI Workflow:**
```python
# 1. Search Synergy projects
projects = search_synergy_projects(
    query="Google Sheets",
    platforms=["google_sheets"],
    priority="high"
)

# 2. Return matches
AI: "Found 3 high-priority projects using Google Sheets:

1. **Customer Database System** (Nov 15 - Active)
   - Platforms: Google Sheets, Forms, Gmail
   - Status: In Progress
   - Documents: 5 (including validation schema)

2. **Sales Pipeline Tracker** (Nov 1 - Completed)
   - Platforms: Google Sheets, Calendar
   - Status: Completed
   - Documents: 3 spreadsheets

3. **Inventory Management** (Oct 20 - Archived)
   - Platforms: Google Sheets, Drive
   - Status: Archived
   - Documents: 7

Which would you like to open?"
```

---

## 📊 Success Metrics

**Track These KPIs:**

1. **Memory Retrieval Accuracy**
   - % of semantic searches returning relevant results
   - Target: >85% user satisfaction

2. **Token Efficiency**
   - Average tokens saved per thread via summarization
   - Target: >70% reduction for threads with 30+ messages

3. **Context Continuation Rate**
   - % of resumed threads where AI correctly recalls context
   - Target: >90%

4. **Tool Usage**
   - `search_past_conversations()` calls per day
   - `recall_thread_context()` calls per day
   - Target: 20+ searches/day after 1 month

5. **Vectorization Coverage**
   - % of threads vectorized within 1 hour of creation
   - Target: >95%

---

## ✅ Implementation Checklist

### **Phase 1: Infrastructure (Week 1)**
- [ ] Set up Pinecone indexes (conversations, synergy_sessions)
- [ ] Create `VectorMemoryManager` class
- [ ] Implement OpenAI embedding generation
- [ ] Build vectorization queue system
- [ ] Deploy background worker

### **Phase 2: Summarization (Week 2)**
- [ ] Create `sessions.thread_summaries` table
- [ ] Implement `SummarizationService` with progressive layers
- [ ] Build auto-summarization triggers (30+ messages)
- [ ] Add caching layer (Redis) for summaries
- [ ] Test token savings (target: 70%+)

### **Phase 3: AI Tools (Week 3)**
- [ ] Create `memory_tools.json` schema
- [ ] Implement `search_past_conversations()` tool
- [ ] Implement `search_synergy_projects()` tool
- [ ] Implement `recall_thread_context()` tool
- [ ] Implement `remember_code_snippet()` tool
- [ ] Test with real user scenarios

### **Phase 4: Integration (Week 4)**
- [ ] Update system prompt with memory tool instructions
- [ ] Add auto-vectorization on thread creation
- [ ] Add auto-vectorization on Synergy session creation
- [ ] Build admin dashboard for vectorization stats
- [ ] Performance testing (semantic search <500ms)

---

## 🚀 Advanced Features (Future)

1. **Entity Extraction**
   - Extract: people names, companies, project names, dates
   - Store: `sessions.thread_entities` table
   - Use: "Find all threads mentioning John Smith"

2. **Knowledge Graph**
   - Link: Threads → Synergy Sessions → Documents → Tools
   - Visualize: Relationship graph in UI
   - Use: "Show me everything related to this customer"

3. **Automatic Workflow Detection**
   - Analyze: Common tool sequences across threads
   - Suggest: "You do this often - create automation?"
   - Link to: Tool Intelligence Log (from previous design)

4. **Cross-User Knowledge Base**
   - Store: Public/shared solutions (opt-in)
   - Search: "How do other users validate emails?"
   - Privacy: Anonymized, user-controlled

---

**Last Updated:** November 27, 2025  
**Status:** Design Complete - Ready for Implementation  
**Next Step:** Phase 1 - Set up Pinecone indexes and vectorization infrastructure  
**Estimated Time:** 4 weeks for full implementation
