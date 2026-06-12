# Message Content Format Fix - Complete Solution
**Date:** November 22, 2025  
**Status:** Ready to Deploy  
**Issue:** Some messages stored as HTML/plain text instead of JSON content blocks

---

## Problem Summary

Looking at database messages for thread 1744:

**CORRECT FORMAT (JSON content blocks):**
```json
[
  {"type": "thinking", "thinking": "The user is asking..."},
  {"type": "text", "text": "Hello! Good afternoon!"}
]
```

**WRONG FORMAT (Plain HTML/text):**
```
<div class="ai-thinking-dots"><span></span><span></span><span></span></div> Hi! Based on your location...
```

**Impact:**
- Claude API throws 400 errors when thinking blocks are modified
- Messages can't be properly reconstructed in conversation history
- Frontend displays mix of formatted and raw content

---

## Root Cause Analysis

### What Went Wrong (Historical)

**Before November 22, 2025:**
- Some code path was rendering content blocks to HTML before saving
- Messages got saved as plain strings instead of JSON arrays
- This created inconsistent database state

**Current State (November 22, 2025):**
- ✅ Backend `conversation_sync` sends proper content blocks
- ✅ Frontend `UnifiedMessageRenderer` saves raw content
- ✅ Thread loader preserves content blocks
- ❌ Old messages in database have HTML/text format

### What's Working Now

1. **Streaming endpoint** (`/api/agent/stream`):
   - Returns content blocks via `conversation_sync` event
   - Frontend stores them correctly in `AppState.chatMessages`

2. **Message saving** (`/api/threads/messages/save`):
   - Frontend sends raw `content` from messages
   - Backend serializes to JSON with `json.dumps()`

3. **Message loading** (`/api/threads/{thread_id}/messages`):
   - Backend returns messages as-is from database
   - Tries to parse JSON, falls back to string

---

## Solution: Multi-Layer Fix

### Layer 1: Backend - Handle Both Formats

Update message loading to normalize both formats:

**File:** `AI_infrastructure/routes/agent_routes_v4.py`

```python
def normalize_message_content(content_str):
    """
    Normalize message content to always return content blocks array
    
    Handles:
    - JSON array strings (correct format)
    - Plain text/HTML strings (legacy format)
    - Already-parsed lists/dicts
    """
    # Already a list/dict
    if isinstance(content_str, (list, dict)):
        if isinstance(content_str, list):
            return content_str
        return [content_str]  # Wrap dict in array
    
    # Try to parse as JSON
    try:
        parsed = json.loads(content_str)
        if isinstance(parsed, list):
            return parsed
        return [{'type': 'text', 'text': str(parsed)}]
    except (json.JSONDecodeError, TypeError):
        pass
    
    # Plain text - convert to content block
    if isinstance(content_str, str):
        # Strip HTML tags if present
        text = re.sub(r'<[^>]+>', '', content_str).strip()
        if text:
            return [{'type': 'text', 'text': text}]
    
    return []
```

**Usage in message loading:**
```python
# Line ~640 (user message load)
content = normalize_message_content(row[2])  # row[2] is content column

# Line ~1535 (assistant message load)
content = normalize_message_content(row[2])
```

### Layer 2: Database Migration Script

Create script to convert existing HTML/text messages to JSON:

**File:** `AI_infrastructure/migrations/migrate_message_content_format.py`

```python
"""
Migrate message content from HTML/text to JSON content blocks
"""
import psycopg2
import json
import re
from pathlib import Path

# Load database config
config_path = Path(__file__).parent.parent / 'database-config.json'
with open(config_path) as f:
    db_config = json.load(f)

conn = psycopg2.connect(
    host=db_config['host'],
    database=db_config['database'],
    user=db_config['user'],
    password=db_config['password'],
    port=db_config.get('port', 5432)
)

def is_json_content(content_str):
    """Check if content is already JSON format"""
    try:
        parsed = json.loads(content_str)
        return isinstance(parsed, (list, dict))
    except:
        return False

def convert_to_content_blocks(content_str):
    """Convert plain text/HTML to content blocks array"""
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '', content_str).strip()
    
    if not text:
        return []
    
    return [{'type': 'text', 'text': text}]

def migrate_messages():
    """Migrate all non-JSON message content to JSON format"""
    cursor = conn.cursor()
    
    # Find all messages with non-JSON content
    cursor.execute("""
        SELECT id, content, role 
        FROM sessions.messages 
        WHERE role IN ('user', 'assistant')
        ORDER BY id
    """)
    
    rows = cursor.fetchall()
    total = len(rows)
    migrated = 0
    skipped = 0
    
    print(f"Found {total} messages to check")
    
    for msg_id, content, role in rows:
        # Check if already JSON
        if is_json_content(content):
            skipped += 1
            continue
        
        # Convert to content blocks
        content_blocks = convert_to_content_blocks(content)
        content_json = json.dumps(content_blocks)
        
        # Update database
        cursor.execute("""
            UPDATE sessions.messages
            SET content = %s
            WHERE id = %s
        """, (content_json, msg_id))
        
        migrated += 1
        
        if migrated % 100 == 0:
            print(f"Migrated {migrated}/{total} messages...")
            conn.commit()
    
    conn.commit()
    print(f"\n✅ Migration complete:")
    print(f"   - Migrated: {migrated}")
    print(f"   - Already JSON: {skipped}")
    print(f"   - Total: {total}")

if __name__ == '__main__':
    try:
        migrate_messages()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()
```

### Layer 3: Frontend - Validate Before Saving

Add validation to ensure content blocks format:

**File:** `UI/modules/components/thread_loader.js`

```javascript
// Add validation function
function validateContentFormat(content) {
    /**
     * Ensure content is in proper content blocks format
     * @param {any} content - Message content
     * @returns {Array} - Content blocks array
     */
    // Already an array - validate blocks
    if (Array.isArray(content)) {
        return content.filter(block => 
            block && 
            typeof block === 'object' && 
            block.type
        );
    }
    
    // String - convert to text block
    if (typeof content === 'string') {
        // Skip empty strings
        if (!content.trim()) return [];
        
        return [{
            type: 'text',
            text: content
        }];
    }
    
    // Object - wrap in array
    if (typeof content === 'object' && content !== null) {
        if (content.type && (content.text || content.thinking)) {
            return [content];
        }
    }
    
    console.warn('[ThreadLoader] Invalid content format:', typeof content);
    return [];
}

// Update saveMessagesToThread (line ~192)
messages: messages.map(msg => ({
    role: msg.role,
    content: validateContentFormat(msg.content),  // ✅ Validate format
    timestamp: msg.timestamp || Date.now(),
    tool_calls: msg.tool_calls,
    tokens_used: msg.tokens_used,
    response_time_ms: msg.response_time_ms,
    metadata: msg.metadata || {}
}))
```

---

## Deployment Steps

### Step 1: Backup Database
```powershell
cd C:\Users\gpoli\GIT\AI_agents
python -c "
import psycopg2, json
from pathlib import Path
config = json.load(open('AI_infrastructure/database-config.json'))
conn = psycopg2.connect(
    host=config['host'],
    database=config['database'],
    user=config['user'],
    password=config['password']
)
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM sessions.messages')
print(f'Total messages: {cursor.fetchone()[0]}')
conn.close()
"
```

### Step 2: Run Migration Script
```powershell
cd C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\migrations
python migrate_message_content_format.py
```

### Step 3: Update Backend Code
```powershell
# Apply normalize_message_content function
# Update agent_routes_v4.py as shown in Layer 1
```

### Step 4: Update Frontend Code
```powershell
# Apply validateContentFormat function
# Update thread_loader.js as shown in Layer 3
```

### Step 5: Test
```powershell
# Test message loading
CHAT "hello"

# Test thread loading with old messages
# Open thread 1744 and verify messages display correctly
```

---

## Testing Checklist

- [ ] Old messages (HTML format) load and display correctly
- [ ] New messages save as JSON content blocks
- [ ] Thread loading works with both formats
- [ ] Conversation sync preserves thinking blocks
- [ ] Claude API accepts reconstructed conversation history
- [ ] No 400 errors about modified thinking blocks

---

## Files to Modify

1. **Backend:**
   - `AI_infrastructure/routes/agent_routes_v4.py` - Add normalize function
   - `AI_infrastructure/migrations/migrate_message_content_format.py` - New file

2. **Frontend:**
   - `UI/modules/components/thread_loader.js` - Add validation

---

## Success Criteria

✅ All messages in database are in JSON format  
✅ Frontend can load/display both old and new formats  
✅ Backend normalizes content before sending to Claude  
✅ No more 400 errors about thinking blocks  
✅ Conversation history fully reconstructed  

---

## Rollback Plan

If issues occur:
1. Restore database from backup
2. Revert code changes via git
3. Restart Flask server

---

**STATUS: Ready to implement**
**NEXT STEP: Run migration script and update code**
