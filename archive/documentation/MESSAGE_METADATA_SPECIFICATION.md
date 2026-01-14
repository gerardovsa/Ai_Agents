# Message Metadata Specification

**System:** AI Agents Platform  
**Database:** `data/sessions.db` → `messages` table  
**Date:** November 8, 2025  
**Status:** ✅ Production Schema (19 columns)

---

## 📊 **COMPLETE METADATA CAPTURED PER MESSAGE**

### **1. Core Identity** (4 fields)
```sql
id                  INTEGER PRIMARY KEY  -- Unique message ID
thread_id           INTEGER              -- Links to threads.id
session_id          TEXT                 -- Legacy session identifier
workspace_id        INTEGER              -- Workspace context
```

**Purpose:** Message identification and thread linking  
**Usage:** Primary keys, foreign keys, message lookup

---

### **2. Content & Communication** (3 fields)
```sql
role                TEXT NOT NULL        -- 'user', 'assistant', 'system', 'tool'
content             TEXT NOT NULL        -- Message text or tool response
prompt              TEXT                 -- Original user prompt (for assistant messages)
```

**Purpose:** Conversation content storage  
**Examples:**
- `role: 'user'` → User's input
- `role: 'assistant'` → AI's response
- `role: 'tool'` → Tool execution result
- `content` → Full message text
- `prompt` → Original prompt that generated response

---

### **3. AI Performance Metrics** (3 fields)
```sql
tokens_used         INTEGER              -- Total tokens consumed
response_time_ms    INTEGER              -- Response generation time (milliseconds)
response_data       TEXT                 -- Raw API response (JSON)
```

**Purpose:** Performance tracking, cost calculation, debugging  
**Examples:**
```json
{
  "tokens_used": 1250,
  "response_time_ms": 3420,
  "response_data": "{\"model\":\"claude-3-sonnet\",\"stop_reason\":\"end_turn\"}"
}
```

**Use Cases:**
- Cost analysis (tokens × price per token)
- Performance monitoring (slow responses)
- Debugging (full API response inspection)

---

### **4. Tool Execution** (1 field)
```sql
tool_calls          TEXT                 -- JSON array of tool invocations
```

**Purpose:** Track which tools were called and their parameters  
**Format:** JSON array
```json
[
  {
    "name": "google_docs_create_document",
    "parameters": {
      "title": "Project Plan",
      "content": "..."
    },
    "result": {
      "document_id": "abc123",
      "url": "https://docs.google.com/..."
    }
  }
]
```

**Use Cases:**
- Audit trail (what actions were taken)
- Tool usage analytics
- Debugging tool failures
- Replay tool sequences

---

### **5. User Context** (2 fields)
```sql
user_id            INTEGER              -- User who created message
api_session_id     TEXT                 -- API session identifier
```

**Purpose:** User attribution and session tracking  
**Use Cases:**
- Multi-user support
- User-specific history
- Session management

---

### **6. Timestamps** (2 fields)
```sql
created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**Purpose:** Message timeline tracking  
**Use Cases:**
- Conversation chronology
- Activity analytics
- Message age calculation
- Last update tracking

---

### **7. User Feedback** (2 fields)
```sql
feedback_score     INTEGER              -- User rating (-1, 0, +1)
include            BOOLEAN DEFAULT 1     -- Include in context (false = exclude)
```

**Purpose:** User feedback and context management  
**Examples:**
```json
{
  "feedback_score": 1,    // 👍 Good response
  "include": true         // Include in conversation history
}
```

**Use Cases:**
- Quality tracking
- User satisfaction metrics
- Context window management (exclude low-quality messages)
- Training data curation

---

### **8. Advanced Features** (1 field)
```sql
embedding_vector   TEXT                 -- Vector representation (for semantic search)
```

**Purpose:** Semantic search and similarity matching  
**Format:** JSON array of floats
```json
[0.123, -0.456, 0.789, ...] // 1536-dimensional vector
```

**Use Cases:**
- Semantic message search
- Find similar conversations
- Topic clustering
- Content recommendations

---

### **9. Custom Metadata** (1 field)
```sql
metadata           TEXT                 -- JSON object for custom fields
```

**Purpose:** Extensible metadata storage  
**Format:** JSON object (unlimited nested structure)
```json
{
  "agent_name": "Research Assistant",
  "task_type": "data_analysis",
  "priority": "high",
  "tags": ["urgent", "finance"],
  "custom_field": "any value",
  "nested": {
    "deeply": {
      "nested": "data"
    }
  }
}
```

**Current Use:** Reserved for future extensions  
**Potential Uses:**
- Agent assignments
- Message classification
- Custom workflows
- Third-party integrations

---

## 📈 **METADATA USAGE BY OPERATION**

### **Fork Thread:**
```json
{
  "metadata": {
    "forked_from_message_id": 123,
    "fork_point": "2025-11-08T14:30:00Z",
    "branch_reason": "Alternative approach"
  }
}
```

### **Clone Thread:**
```json
{
  "metadata": {
    "cloned_from_thread": "1762582042027",
    "clone_date": "2025-11-08T14:30:00Z",
    "original_message_id": 456
  }
}
```

### **Copy Message:**
```json
{
  "metadata": {
    "copied_from_message_id": 789,
    "copied_from_thread": "1762582042027",
    "copy_date": "2025-11-08T14:30:00Z"
  }
}
```

### **Synergy Integration:**
```json
{
  "metadata": {
    "synergy_session_id": "sess_20251108_1430_project_alpha",
    "synergy_task_id": "task_42",
    "synergy_status": "in_progress"
  }
}
```

---

## 🔍 **CURRENT STATE (Nov 8, 2025)**

**Database Analysis:**
- **Total messages:** 460
- **Messages with metadata:** 0 (field exists but not yet populated)
- **Messages with tool_calls:** 0 (not yet captured)
- **Messages with tokens_used:** 0 (not yet tracked)

**Message Distribution:**
- **User messages:** 230
- **Assistant messages:** 230

**Why metadata is empty:**
- Existing messages are from old sessions (before metadata tracking)
- Schema is ready, but population happens with new messages
- All 19 columns exist and are ready to use

---

## 🚀 **GOING FORWARD**

### **When Backend Creates Messages:**

```python
# In agent_routes.py or message creation code:
insert_message = """
    INSERT INTO messages (
        thread_id, session_id, role, content, prompt,
        user_id, tool_calls, tokens_used, response_time_ms,
        metadata, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

metadata = {
    "agent_name": "Research Assistant",
    "model": "claude-3-sonnet",
    "temperature": 0.7,
    "task_type": "analysis"
}

execute_sqlite_update(db_path, insert_message, (
    thread_id,
    session_id,
    'assistant',
    response_content,
    user_prompt,
    user_id,
    json.dumps(tool_calls),      # Tool execution log
    total_tokens,                # Cost tracking
    response_time_ms,            # Performance monitoring
    json.dumps(metadata),        # Custom metadata
    datetime.now().isoformat(),
    datetime.now().isoformat()
))
```

### **When Frontend Displays Messages:**

```javascript
// Message component
const MessageCard = ({ message }) => {
  return (
    <div className="message">
      <div className="message-header">
        <span className="role">{message.role}</span>
        <span className="timestamp">{formatDate(message.created_at)}</span>
        {message.tokens_used && (
          <span className="tokens">{message.tokens_used} tokens</span>
        )}
      </div>
      
      <div className="message-content">
        {message.content}
      </div>
      
      {message.tool_calls && (
        <div className="tools-used">
          {message.tool_calls.map(tool => (
            <ToolBadge key={tool.name} tool={tool} />
          ))}
        </div>
      )}
      
      {message.metadata && (
        <MessageMetadata data={message.metadata} />
      )}
    </div>
  );
};
```

---

## 📋 **METADATA CHECKLIST**

### **Required Fields (Always Populated):**
- [x] `role` - Message type
- [x] `content` - Message text
- [x] `created_at` - Creation timestamp

### **Standard Fields (Should Be Populated):**
- [ ] `thread_id` - Link to thread
- [ ] `user_id` - User attribution
- [ ] `session_id` - Session tracking
- [ ] `workspace_id` - Workspace context

### **Performance Fields (When Available):**
- [ ] `tokens_used` - Token consumption
- [ ] `response_time_ms` - Response latency
- [ ] `prompt` - Original user input
- [ ] `response_data` - Raw API response

### **Advanced Fields (Optional):**
- [ ] `tool_calls` - Tool execution log
- [ ] `feedback_score` - User rating
- [ ] `embedding_vector` - Semantic vector
- [ ] `metadata` - Custom JSON data

---

## 🎯 **KEY TAKEAWAYS**

1. **Schema is Ready:** All 19 metadata columns exist in database ✅
2. **Population Needed:** Backend code needs to populate these fields when creating messages
3. **Extensible:** `metadata` JSON field allows unlimited custom data
4. **Performance Ready:** Token and timing tracking built-in
5. **Tool Tracking:** `tool_calls` captures complete audit trail
6. **User Feedback:** Rating and inclusion flags for quality control
7. **Semantic Search:** Embedding vector support for advanced features

---

**Next Steps:**
1. Update message creation code to populate all fields
2. Add token/timing tracking to API responses
3. Implement tool_calls logging
4. Add metadata to fork/clone/copy operations
5. Build frontend UI to display message metadata

**Total Metadata Fields:** 19 columns  
**Status:** Schema complete, awaiting population  
**Flexibility:** JSON metadata field allows unlimited extensions
