# MESSAGE FORMAT COMPLETE ANALYSIS
**Date:** November 22, 2025  
**Status:** COMPREHENSIVE AUDIT - All Message Handling Paths  
**Purpose:** Document EXACTLY how messages should be formatted at every stage

---

## 📋 EXECUTIVE SUMMARY

**CORRECT FORMAT:** All AI message events (thinking, tool_use, tool_result, text) should be saved as **JSON strings** in the database.

**CURRENT STATUS:**
- ✅ Backend saves messages as JSON (agent_routes_v4.py lines 637 & 1532)
- ⏳ Need to verify frontend sends messages in correct format
- ⏳ Need to verify database actually receives JSON strings

---

## 🔄 COMPLETE MESSAGE FLOW

### 1️⃣ **USER SENDS MESSAGE** (Frontend → Backend)

**Location:** `UI/modules/agents/agent-js.js` or `prime_ai_chat.js`

**Format Sent to Backend:**
```javascript
// POST /api/agent/start
{
    "agent_id": "1",
    "message": "User's text message",
    "conversation_history": [
        {
            "role": "user",
            "content": [
                { "type": "text", "text": "Previous user message" }
            ]
        },
        {
            "role": "assistant",
            "content": [
                { 
                    "type": "thinking", 
                    "thinking": "AI reasoning...",
                    "signature": "EsQGCkYICRg..." 
                },
                { "type": "text", "text": "AI response" }
            ]
        }
    ]
}
```

**✅ CORRECT:** Conversation history is sent as **structured JSON objects** with content blocks.

---

### 2️⃣ **BACKEND RECEIVES MESSAGE** (agent_routes_v4.py)

**Location:** `/api/agent/start` endpoint (lines 545-575)

**What Backend Receives:**
```python
# Line 558: Extract conversation_history
conversation_history = data.get('conversation_history', [])

# Example of what's in conversation_history:
[
    {
        'role': 'user',
        'content': [{'type': 'text', 'text': 'Hello'}]
    },
    {
        'role': 'assistant',
        'content': [
            {'type': 'thinking', 'thinking': '...', 'signature': '...'},
            {'type': 'text', 'text': 'Hi there'}
        ]
    }
]
```

**✅ CORRECT:** Backend receives messages as structured dictionaries/lists.

---

### 3️⃣ **BACKEND PROCESSES & SAVES** (agent_routes_v4.py)

#### **Save Point 1: User Message (Line 625-645)**

**Location:** `/start` endpoint after receiving user message

```python
for message in messages_to_save:
    # Save content as JSON string to preserve full structure
    # (thinking blocks, tool_use, tool_result, signatures, etc.)
    content = message.get('content', '')
    if isinstance(content, (list, dict)):
        # Serialize to JSON string
        import json
        content = json.dumps(content)  # ✅ CORRECT!
    
    # Insert message with JSON content
    cursor.execute("""
        INSERT INTO sessions.messages 
        (thread_id, role, content, created_at)
        VALUES (%s, %s, %s, NOW())
    """, (db_thread_id, message['role'], content))
```

**Example Database Insert:**
```sql
INSERT INTO sessions.messages (thread_id, role, content, created_at)
VALUES (
    1744,
    'assistant',
    '[{"type": "thinking", "thinking": "...", "signature": "EsQG..."}, {"type": "text", "text": "Hello"}]',
    NOW()
);
```

**✅ CORRECT:** Content saved as JSON string.

#### **Save Point 2: AI Response (Line 1520-1545)**

**Location:** `/stream` endpoint after AI completes response

```python
for message in messages_to_save:
    # Save content as JSON string to preserve full structure
    # (thinking blocks, tool_use, tool_result, signatures, etc.)
    content = message.get('content', '')
    if isinstance(content, (list, dict)):
        # Serialize to JSON string
        import json
        content = json.dumps(content)  # ✅ CORRECT!
    
    # Insert message
    cursor.execute("""
        INSERT INTO sessions.messages 
        (thread_id, role, content, created_at)
        VALUES (%s, %s, %s, NOW())
    """, (db_thread_id, message['role'], content))
```

**✅ CORRECT:** Content saved as JSON string.

---

### 4️⃣ **DATABASE STORAGE** (Supabase PostgreSQL)

**Table:** `sessions.messages`

**Schema:**
```sql
CREATE TABLE sessions.messages (
    id SERIAL PRIMARY KEY,
    thread_id INTEGER REFERENCES sessions.threads(id),
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,  -- ⚠️ TEXT column stores JSON string
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

**Example Row:**
```
id: 198
thread_id: 1744
role: "user"
content: '[{"type": "text", "text": "hi can you tell me the time"}]'
created_at: 2025-11-22 04:49:52.518273
```

**✅ CORRECT FORMAT:** Content is a JSON string, not plain text.

**❌ WRONG FORMAT (OLD):**
```
content: "hi can you tell me the time"  -- Plain text, loses structure
```

---

### 5️⃣ **BACKEND LOADS MESSAGES** (From Database)

**When loading from database:**

```python
# Query messages
cursor.execute("""
    SELECT id, role, content, created_at 
    FROM sessions.messages 
    WHERE thread_id = %s 
    ORDER BY created_at ASC
""", (thread_id,))

messages = cursor.fetchall()

# Parse content back to objects
for msg in messages:
    content = msg['content']
    if isinstance(content, str):
        try:
            # Parse JSON string back to list/dict
            parsed_content = json.loads(content)
            msg['content'] = parsed_content
        except json.JSONDecodeError:
            # Old plain text format
            msg['content'] = [{'type': 'text', 'text': content}]
```

**✅ CORRECT:** Parse JSON string back to structured objects before sending to frontend.

---

### 6️⃣ **FRONTEND RECEIVES MESSAGES** (From Backend)

**Via SSE events during streaming:**

```javascript
// Event: conversation_sync
{
    "type": "conversation_sync",
    "conversation": [
        {
            "role": "user",
            "content": [{"type": "text", "text": "Hello"}]
        },
        {
            "role": "assistant",
            "content": [
                {"type": "thinking", "thinking": "...", "signature": "..."},
                {"type": "text", "text": "Hi"}
            ]
        }
    ]
}
```

**✅ CORRECT:** Frontend receives structured objects, not JSON strings.

---

### 7️⃣ **FRONTEND STORES IN MESSAGESTORE** (UI/modules/components/message_store.js)

```javascript
class MessageStore {
    async addMessage(threadId, message, options = {}) {
        // Message structure:
        // {
        //     role: "assistant",
        //     content: [
        //         { type: "thinking", thinking: "...", signature: "..." },
        //         { type: "text", text: "..." }
        //     ]
        // }
        
        this._messages.get(threadId).push(message);
        return message;
    }
}
```

**✅ CORRECT:** MessageStore keeps messages as structured objects in memory.

---

## 🔍 VERIFICATION POINTS

### ✅ **What's Working (As of Nov 22, 2025):**

1. **Backend Saves JSON** (agent_routes_v4.py)
   - Lines 637 & 1532: `json.dumps(content)` 
   - Preserves thinking blocks, tool_use, tool_result, signatures

2. **Frontend Sends Structured Data**
   - conversation_history sent as JSON objects
   - Content blocks properly formatted

3. **SSE Events Send Structured Data**
   - conversation_sync includes full block structure
   - No text extraction during streaming

### ⚠️ **Potential Issues to Check:**

1. **Old Messages in Database**
   - Messages 210-213 saved as plain text/HTML
   - Need to verify NEW messages save as JSON after server restart

2. **Frontend Message Sending**
   - Verify conversation_history maintains structure
   - Check no text extraction happens before POST

3. **Database Column Type**
   - Using TEXT column (correct for JSON strings)
   - Could optionally use JSONB for native JSON support

---

## 📊 MESSAGE CONTENT BLOCK TYPES

**All these types MUST be preserved in JSON:**

### 1. **Text Blocks**
```json
{
    "type": "text",
    "text": "The actual text content"
}
```

### 2. **Thinking Blocks** (Extended Thinking)
```json
{
    "type": "thinking",
    "thinking": "AI's reasoning process...",
    "signature": "EsQGCkYICRgCKkCXWXy+..."  // MUST preserve!
}
```

### 3. **Tool Use Blocks**
```json
{
    "type": "tool_use",
    "id": "toolu_01ABC123...",
    "name": "gmail_send_email",
    "input": {
        "to": "user@example.com",
        "subject": "Test"
    }
}
```

### 4. **Tool Result Blocks**
```json
{
    "type": "tool_result",
    "tool_use_id": "toolu_01ABC123...",
    "content": "Email sent successfully",
    "is_error": false
}
```

---

## 🔧 CODE LOCATIONS

### Backend (Python):

1. **Message Saving:**
   - `AI_infrastructure/routes/agent_routes_v4.py`
     - Line 637: User message save (JSON)
     - Line 1532: AI response save (JSON)

2. **Message Loading:**
   - Need to add JSON parsing when loading from database
   - Currently missing in thread load routes

### Frontend (JavaScript):

1. **Message Sending:**
   - `UI/modules/agents/agent-js.js` (agent columns)
   - `UI/modules/agents/prime_ai_chat.js` (Prime AI)
   - Both send conversation_history as structured objects

2. **Message Storage:**
   - `UI/modules/components/message_store.js`
   - Stores messages as objects in memory

3. **Message Rendering:**
   - `UI/modules/shared/message_renderer.js`
   - Renders from structured objects

---

## 🎯 TESTING CHECKLIST

### Test 1: Verify Backend Saves JSON
```sql
-- Check most recent messages
SELECT 
    id, 
    role, 
    LEFT(content, 100) as content_preview,
    CASE 
        WHEN content LIKE '[%' OR content LIKE '{%' THEN 'JSON'
        ELSE 'PLAIN TEXT'
    END as format,
    created_at
FROM sessions.messages
WHERE thread_id = 1744
ORDER BY created_at DESC
LIMIT 5;
```

**Expected:** All new messages show format = 'JSON'

### Test 2: Verify JSON Structure
```python
import json

# Load message from database
content_str = '[{"type":"thinking","thinking":"...","signature":"..."},{"type":"text","text":"..."}]'

# Parse back to objects
parsed = json.loads(content_str)

# Verify structure
assert isinstance(parsed, list)
assert parsed[0]['type'] == 'thinking'
assert 'signature' in parsed[0]  # CRITICAL!
```

### Test 3: End-to-End Flow
1. Send message in Prime AI
2. Wait for AI response with thinking
3. Check Flask logs: "[Backend AI Response Save] ✅ Saved X messages"
4. Query database: Verify content is JSON string
5. Reload page: Verify messages render correctly
6. Send another message: Verify thinking blocks work (no API error)

---

## 🚨 CRITICAL RULES

### ✅ DO:
- Always save `content` as JSON string: `json.dumps(content)`
- Preserve ALL fields in content blocks (especially `signature`)
- Parse JSON back to objects when loading from database
- Send structured objects in conversation_history
- Keep MessageStore with structured objects

### ❌ DON'T:
- Extract only text from content blocks
- Convert content to plain strings
- Lose thinking block signatures
- Save HTML-rendered content
- Flatten content arrays to strings

---

## 📝 SUMMARY

**CORRECT MESSAGE FORMAT CHAIN:**

```
Frontend (Objects) 
    → JSON.stringify for POST 
        → Backend (Dicts/Lists) 
            → json.dumps() for database 
                → Database (JSON String in TEXT column)
                    → json.loads() when reading
                        → Backend (Dicts/Lists)
                            → Frontend (Objects)
```

**Key Points:**
- **In Memory:** Structured objects (JavaScript objects, Python dicts/lists)
- **In Transit:** JSON strings (HTTP POST, SSE events)
- **In Database:** JSON strings (TEXT column with JSON content)
- **For Rendering:** Structured objects (parsed from JSON)

---

**Last Updated:** November 22, 2025  
**Next Steps:** 
1. Verify NEW messages save as JSON (after server restart)
2. Test end-to-end with Prime AI
3. Check thinking block signatures preserved
4. Monitor database for correct format
