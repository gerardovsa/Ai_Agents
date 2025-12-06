# Infinite Loop Detection Fix - Progressive Search Support
**Date:** December 5, 2025

## Critical Issues Discovered

### Issue 1: Legitimate Progressive Search Blocked ❌
**What Happened:**
```
User: "Find database tools"
Round 1: search_tools("database sql") → 0 results
Round 2: search_tools("data") → 479 results (too broad)
Round 3: search_tools("db") → 🛑 BLOCKED (infinite loop error)
```

**Problem:** Agent was **legitimately narrowing search strategy** with different queries, but got blocked because the system only checks **tool name**, not **parameters**.

### Issue 2: Hanging Thread (Critical UX Bug) 🚨
**What Happened:**
- Loop detection triggered during tool execution
- Error yielded via stream: `yield {'type': 'error', ...}`
- Stream terminates with `return`
- **NO tool_result sent back to agent**
- Frontend stuck in "tool-running" state forever
- Thread cannot be closed or recovered
- User has no way to continue conversation

**Root Cause:**
```python
# combined_agent_worker.py line ~2500
if not error_recovery_mode:
    error_msg = "INFINITE LOOP DETECTED..."
    yield {'type': 'error', 'error': error_msg}
    return  # ← EXITS WITHOUT SENDING TOOL RESULT
```

The agent expects a `tool_result` message to close the tool execution cycle, but gets cut off mid-stream.

## The Fixes

### Fix 1: Track Query Parameters for search_tools
Only block if **same tool with same query** called 3x:

```python
# Track tool calls WITH parameters for search_tools
recent_tool_calls = []  # List of (tool_name, query_param)

for msg in conversation_history[-6:]:
    if msg.get('role') == 'assistant':
        for block in content:
            if block.get('type') == 'tool_use':
                tool_name = block.get('name')
                tool_input = block.get('input', {})
                
                # For search_tools, track the query parameter
                if tool_name == 'search_tools':
                    query = tool_input.get('query', '')
                    recent_tool_calls.append(('search_tools', query))
                else:
                    # For other meta-tools, just track name
                    recent_tool_calls.append((tool_name, None))

# Check for true loops (identical tool+query combos)
if len(recent_tool_calls) >= 3:
    last_three = recent_tool_calls[-3:]
    
    # Block only if ALL THREE are identical (tool name AND query)
    if len(set(last_three)) == 1:  # All three tuples are the same
        # This is a true loop - block it
```

**Result:**
- ✅ `search_tools("sql")` → `search_tools("data")` → `search_tools("db")` = ALLOWED (different queries)
- ❌ `search_tools("email")` → `search_tools("email")` → `search_tools("email")` = BLOCKED (same query)

### Fix 2: Return Synthetic Tool Result (Prevent Hanging)
When blocking, send a proper tool_result so the agent can continue:

```python
if not error_recovery_mode:
    error_msg = f"""⚠️  INFINITE LOOP DETECTED: You called '{repeated_tool}' {repeat_count} times with the same query.

🛑 STOP calling discovery tools repeatedly!

✅ NEXT STEPS:
1. Use different search terms if previous queries didn't work
2. Call get_tool_schema("tool_name") to learn parameters
3. Call execute_tool("tool_name", ...) to take action

Previous searches:
{chr(10).join(f'  - {call[1]}' for call in recent_tool_calls[-3:] if call[0] == repeated_tool)}

Try a different approach now."""
    
    print(f"{log_prefix} 🛑 {error_msg}")
    
    # CRITICAL FIX: Send synthetic tool_result to prevent hanging
    # This allows the agent to receive the error and respond naturally
    synthetic_tool_results = []
    for tool_use in tool_uses:
        synthetic_tool_results.append({
            'type': 'tool_result',
            'tool_use_id': tool_use['id'],
            'content': error_msg,
            'is_error': True
        })
    
    # Yield tool results as normal (don't use 'error' type)
    for result in synthetic_tool_results:
        yield {
            'type': 'tool_result',
            'tool_name': tool_use['name'],
            'tool_result': result,
            'session_id': session_id,
            'round': current_round
        }
    
    # Add to conversation history so agent can respond
    conversation_history.append({
        'role': 'user',
        'content': synthetic_tool_results
    })
    
    # Continue the loop to let agent respond (don't return)
    continue  # ← Go to next round, not return
```

**Key Changes:**
1. Send `tool_result` (not `error`) - keeps stream format consistent
2. Add to conversation history - agent sees the error as a tool result
3. Use `continue` (not `return`) - allows agent to respond to the error
4. Thread remains functional - user can close or continue

### Fix 3: Update System Prompt Guidance
Make it clear that **progressive refinement is OK**:

```markdown
ANTI-LOOP RULES (UPDATED):
1. 🛑 Don't call search_tools() with the SAME query 3+ times
2. ✅ Progressive refinement IS allowed:
   - search_tools("database") → 0 results
   - search_tools("data") → too many results  
   - search_tools("postgres") → perfect!
3. ✅ After finding tools → move to get_tool_schema() or execute_tool()
4. ❌ Repeating identical searches wastes time and will be blocked
```

## Implementation

### File: `combined_agent_worker.py`
**Location:** Lines 2430-2510 (infinite loop detection block)

**Changes:**
1. Replace `recent_tools = []` with `recent_tool_calls = []` (tuples)
2. Track `(tool_name, query)` for search_tools
3. Compare tuples instead of just tool names
4. Send synthetic tool_result on block (not error)
5. Use `continue` instead of `return`

### File: `agent_routes_v4.py`
**Location:** System prompt section (ANTI-LOOP RULES)

**Changes:**
1. Update rule 1: "with the SAME query"
2. Add rule 2: "Progressive refinement IS allowed"
3. Add examples of good vs bad search patterns

## Testing Scenarios

### Test 1: Progressive Search ✅ (Should ALLOW)
```
User: "Find database tools"
Round 1: search_tools("database sql") → 0 results
Round 2: search_tools("data") → 479 results
Round 3: search_tools("postgres") → Success!
```
**Expected:** All allowed, agent finds tools

### Test 2: True Infinite Loop ❌ (Should BLOCK)
```
User: "Find email tools"
Round 1: search_tools("email") → 24 tools found
Round 2: search_tools("email") → Same 24 tools
Round 3: search_tools("email") → 🛑 BLOCKED with guidance
```
**Expected:** Blocked after 3rd identical search

### Test 3: Thread Recovery (Should WORK)
```
User: "Find email tools"
Round 1-3: Triggers loop detection
System: Sends synthetic tool_result with error message
Agent: Receives error, responds naturally
User: Can continue conversation or close thread
```
**Expected:** Thread remains functional, no hanging state

## Benefits

### Before Fixes:
- ❌ Progressive refinement blocked (false positive)
- ❌ Thread hangs when loop detected
- ❌ User has no recovery path
- ❌ Frontend stuck in "tool-running" forever

### After Fixes:
- ✅ Progressive refinement allowed (smarter detection)
- ✅ Thread stays functional when loop detected
- ✅ Agent receives error as tool_result and can respond
- ✅ User can close thread or continue normally
- ✅ Frontend receives proper completion signal

## Deployment Steps

1. **Backup current file:**
   ```powershell
   Copy-Item "AI_infrastructure\core\combined_agent_worker.py" `
             "AI_infrastructure\core\combined_agent_worker.py.backup_dec5"
   ```

2. **Apply fixes to combined_agent_worker.py**
   - Update loop detection to track (tool_name, query) tuples
   - Send synthetic tool_result instead of error on block
   - Use `continue` instead of `return`

3. **Update system prompt in agent_routes_v4.py**
   - Clarify progressive refinement is allowed
   - Add examples of good search patterns

4. **Restart Flask:**
   ```powershell
   cd "C:\Users\gpoli\GIT\AI_agents"
   .\BISTART.bat
   ```

5. **Test all scenarios:**
   - Progressive search (should work)
   - Identical search loop (should block gracefully)
   - Thread recovery (should not hang)

## Status
⏳ **READY TO IMPLEMENT**

## Files to Modify
1. `AI_infrastructure\core\combined_agent_worker.py` (lines 2430-2510)
2. `AI_infrastructure\routes\agent_routes_v4.py` (system prompt section)

## Related Documentation
- `INFINITE_LOOP_DETECTION_FIX_NOV25.md` (original fix)
- `ERROR_RECOVERY_FIX_NOV25.md` (error recovery enhancement)
- This document supersedes previous loop detection logic
