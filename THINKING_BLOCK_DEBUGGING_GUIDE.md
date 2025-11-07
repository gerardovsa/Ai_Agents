# Thinking Block Error Debugging Guide 🔍

**Quick reference for diagnosing and fixing Anthropic API thinking block errors**

---

## Error Signature

```
Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 
'message': 'messages.1.content.0: If an assistant message contains any thinking blocks, 
the first block must be `thinking` or `redacted_thinking`. Found `text`.'}}
```

**Translation:** An assistant message has thinking blocks, but the first block is `text` instead of `thinking`.

---

## Quick Diagnosis

### 1. Check Log Output

**Look for these patterns:**

✅ **GOOD - Fix is working:**
```
[Combined Worker] 🔧 Message 2 (assistant) reordered:
    Before: ['text', 'thinking', 'tool_use']
    After:  ['thinking', 'text', 'tool_use']
[Combined Simple main] 🔍 Re-validating entire history before round 2...
[Combined Worker] ✅ Validated: 10 valid messages
```

❌ **BAD - Fix not applied:**
```
[Stream Round 4] Sending 8 messages to Claude...
ERROR: 400 - thinking blocks must be first
```

### 2. Check Function Flow

**In `run_simple_agent_worker()` tool loop, verify this exists:**

```python
# After tool execution, BEFORE next API call:
messages = validate_conversation_history(messages)  # ← MUST BE HERE
```

**Location:** Line ~685 in `combined_agent_worker.py`

### 3. Check Validation Function

**In `validate_and_reorder_assistant_content()`, verify:**

```python
# STEP 4: Reorder: thinking blocks first, then others
thinking_blocks = [b for b in validated_blocks if b.get('type') in ('thinking', 'redacted_thinking')]
other_blocks = [b for b in validated_blocks if b.get('type') not in ('thinking', 'redacted_thinking')]

return thinking_blocks + other_blocks  # ← Thinking MUST be first
```

---

## Common Causes

### Cause 1: Missing Re-Validation
**Symptom:** Error on 2nd+ tool execution round  
**Fix:** Add `messages = validate_conversation_history(messages)` before API call

### Cause 2: Content Not a List
**Symptom:** `validate_and_reorder_assistant_content()` returns unchanged content  
**Fix:** Use `normalize_content_to_blocks()` first

### Cause 3: tool_result in Assistant Message
**Symptom:** API rejects entire message structure  
**Fix:** Ensure validation removes tool_result blocks from assistant messages

### Cause 4: Orphaned tool_result
**Symptom:** User message has tool_result but no prior tool_use  
**Fix:** Validation should remove orphaned tool_results

---

## Validation Checklist

Before every API call to Anthropic, ensure:

- [ ] All assistant messages have been validated
- [ ] Thinking blocks are first in assistant messages
- [ ] No tool_result blocks in assistant messages
- [ ] No orphaned tool_result blocks in user messages
- [ ] All content is in block format (not strings)
- [ ] No duplicate consecutive roles (user-user or assistant-assistant)
- [ ] All required block fields are present (text.text, tool_use.id, etc.)

---

## Testing Commands

### Test 1: Import Validation
```powershell
cd c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\core
python -c "from combined_agent_worker import validate_conversation_history; print('✅ OK')"
```

### Test 2: Block Reordering
```python
from AI_infrastructure.core.combined_agent_worker import validate_and_reorder_assistant_content

# Test case: Wrong order
content = [
    {'type': 'text', 'text': 'Let me search...'},
    {'type': 'thinking', 'thinking': 'Need to use tool', 'signature': ''},
]

# Should reorder
result = validate_and_reorder_assistant_content(content)
print(f"First block type: {result[0]['type']}")  # Should be 'thinking'
```

### Test 3: Full Conversation
```python
from AI_infrastructure.core.combined_agent_worker import validate_conversation_history

history = [
    {
        'role': 'user',
        'content': [{'type': 'text', 'text': 'Search OneDrive'}]
    },
    {
        'role': 'assistant',
        'content': [
            {'type': 'text', 'text': 'Searching...'},
            {'type': 'thinking', 'thinking': 'Using OneDrive tool', 'signature': ''},
        ]
    }
]

validated = validate_conversation_history(history)
print(f"Assistant blocks: {[b['type'] for b in validated[1]['content']]}")
# Should be: ['thinking', 'text']
```

### Test 4: End-to-End
```powershell
# Restart server
BISTART

# Test problematic query
CHAT "search my one drive for any recent word docs"

# Check logs for validation output
# Should see: "Re-validating entire history before round X"
```

---

## Log Patterns to Watch

### Pattern 1: Reordering Happening
```
[Combined Worker] 🔧 Message 2 (assistant) reordered:
    Before: ['text', 'thinking', 'tool_use']
    After:  ['thinking', 'text', 'tool_use']
```
**Meaning:** Validation is working, blocks were out of order and got fixed

### Pattern 2: Re-Validation
```
[Combined Simple main] 🔍 Re-validating entire history before round 2...
[Combined Worker] ✅ Validated: 10 valid messages
```
**Meaning:** History re-validated before API call (THIS IS CRITICAL)

### Pattern 3: Block Removal
```
[Combined Worker] ⚠️ Removing tool_result from assistant message (API violation)
```
**Meaning:** Invalid block removed (good - prevents 400 error)

### Pattern 4: Orphan Detection
```
[Combined Worker] ⚠️ Removing orphaned tool_result from user message
```
**Meaning:** tool_result without matching tool_use removed (good)

---

## Emergency Fixes

### If Error Still Occurs:

#### Fix 1: Strip ALL Thinking Blocks (Nuclear Option)
```python
# In run_simple_agent_worker(), before adding to messages:
content = [b for b in current_response['content'] if b.get('type') not in ('thinking', 'redacted_thinking')]
messages.append({'role': 'assistant', 'content': content})
```

**Trade-off:** Loses thinking context, but prevents errors

#### Fix 2: Convert to String Format
```python
# Extract only text from response
text_only = ''.join([b.get('text', '') for b in current_response['content'] if b.get('type') == 'text'])
messages.append({'role': 'assistant', 'content': text_only})
```

**Trade-off:** Loses all block structure, but always works

#### Fix 3: Fresh History
```python
# Start new conversation (lose history)
messages = [{'role': 'user', 'content': prompt}]
```

**Trade-off:** Loses conversation context

---

## Anthropic API Rules

### RULE 1: Thinking Block Position
**If thinking blocks exist in assistant message:**
- First block MUST be `thinking` or `redacted_thinking`
- Other blocks can follow in any order

### RULE 2: tool_result Placement
**tool_result blocks:**
- Can ONLY appear in user messages
- Must have matching `tool_use_id` from prior assistant message
- Forbidden in assistant messages

### RULE 3: Content Block Structure
**All blocks must have:**
- `type` field (string)
- Type-specific fields:
  - `thinking`: `thinking` (string), `signature` (string)
  - `text`: `text` (string)
  - `tool_use`: `id`, `name`, `input`
  - `tool_result`: `tool_use_id`, `content`

### RULE 4: Message Alternation
**Conversation must alternate:**
- user → assistant → user → assistant
- No consecutive same-role messages
- First message must be user

---

## Code Locations

### Primary Validation:
- **File:** `AI_infrastructure/core/combined_agent_worker.py`
- **Function:** `validate_conversation_history()` (Line ~230)
- **Function:** `validate_and_reorder_assistant_content()` (Line ~40)

### Critical Fix Location:
- **File:** `AI_infrastructure/core/combined_agent_worker.py`
- **Function:** `run_simple_agent_worker()` (Line ~685)
- **Critical Line:**
  ```python
  messages = validate_conversation_history(messages)
  ```

### Alternative Workers:
- **File:** `AI_infrastructure/core/streaming_agent_worker.py`
- **Note:** May need same fix if using streaming worker directly

---

## Success Metrics

**After fix is deployed:**
- ✅ Zero 400 errors about thinking blocks
- ✅ Log shows "Re-validating entire history" before each API call
- ✅ Multi-turn tool conversations complete successfully
- ✅ OneDrive/Google/Microsoft tools work correctly

---

## Contact & Support

**If error persists after fix:**
1. Check logs for validation output
2. Test with simple query first
3. Check if using `combined_agent_worker.py` (not old versions)
4. Verify server restarted after code changes
5. Check Anthropic API status: https://status.anthropic.com/

---

**Version:** 1.0.0  
**Last Updated:** November 7, 2025  
**Related:** `ANTHROPIC_THINKING_BLOCK_FIX_COMPLETE.md`
