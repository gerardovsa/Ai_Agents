# Pruning Function Analysis - HTTP 500 Fix

**Date:** November 14, 2025  
**Issue:** HTTP 500 error caused by missing `prune_conversation_for_context_limit()` function  
**Status:** TEMPORARILY DISABLED (Function commented out)

---

## 🔍 What Happened

### The Error
```python
ImportError: cannot import name 'prune_conversation_for_context_limit' 
from 'core.combined_agent_worker'
```

**Location:** `AI_infrastructure/routes/agent_routes_v4.py` line 502  
**Impact:** Complete system crash - HTTP 500 on every message send attempt

---

## 📊 Functional Flow Analysis

### 1. **Message Send Flow (Before Fix)**

```
User clicks Send in UI
    ↓
Frontend: business-ai-platform-v2.html
    ↓
POST /api/agent/agent/1/start
    ↓
agent_routes_v4.py: start_agent() function
    ↓
Line 498-510: Try to prune conversation history
    ↓
❌ CRASH: Function doesn't exist
    ↓
HTTP 500 returned to frontend
    ↓
User sees "Sorry, I encountered an error"
```

### 2. **What the Pruning Was SUPPOSED To Do**

```python
# INTENDED PURPOSE (from comments in code):
# "CRITICAL: Prune conversation IMMEDIATELY if it's too large"
# "This prevents re-sending 231K+ tokens that already exceeded the limit"

if len(conversation_history) > 0:
    conversation_history = prune_conversation_for_context_limit(
        conversation_history,
        max_estimated_tokens=180000,  # ← 180K token limit
        preserve_first_user=True      # ← Keep first user message
    )
```

**Goal:** Reduce conversation history to fit within Claude's 200K token context window

**Strategy:**
- Target: 180,000 tokens (90% of 200K limit - safety buffer)
- Method: Remove old messages while keeping first user message
- Trigger: Any conversation with history (proactive pruning)

### 3. **Why It Would Prune**

**Anthropic Claude Token Limits:**
- **Hard limit:** 200,000 input tokens
- **Safe limit:** 180,000 tokens (90% - leaves room for system prompt, tools, thinking blocks)

**When pruning would trigger:**
```
Conversation grows → Reaches 180K+ tokens → Prune old messages → Keep recent context
```

**What gets removed:**
1. Oldest messages first (FIFO - First In, First Out)
2. Middle of conversation (preserve first user message for context)
3. Tool results from early rounds (can be verbose)
4. Historical thinking blocks (not needed for current task)

**What gets preserved:**
1. ✅ First user message (initial intent/context)
2. ✅ Most recent N messages (current conversation flow)
3. ✅ Current tool use (active operations)
4. ✅ System-critical messages (errors, warnings)

---

## 🚨 Likely Areas of Issues

### Issue #1: **Function Doesn't Exist**
- **Status:** ✅ FIXED (commented out import)
- **Root cause:** Code references function that was never implemented
- **Impact:** System crash on every message

### Issue #2: **No Token Counting Before API Call**
- **Status:** ⚠️ ACTIVE ISSUE
- **Current behavior:** Conversations can exceed 200K tokens
- **Impact:** Anthropic API rejects request with error
- **Evidence:** Comment mentions "231K+ tokens that already exceeded the limit"

### Issue #3: **Frontend Sends Full History Every Time**
- **Status:** ⚠️ DESIGN ISSUE
- **Current behavior:** 
  ```javascript
  // business-ai-platform-v2.html line ~1464
  📜 Sending X messages in conversation history (filtered empty messages)
  ```
- **Impact:** 
  - Every API call includes ENTIRE conversation
  - No incremental message sending
  - Token usage grows linearly with conversation length
  - Can easily exceed 200K tokens in long conversations

### Issue #4: **No Fallback Handling**
- **Status:** ⚠️ MISSING
- **What's missing:**
  - No error handling if conversation exceeds 200K
  - No user notification ("Conversation too long, pruning history...")
  - No graceful degradation (e.g., summarize old messages)

### Issue #5: **Token Estimation vs Actual Count**
- **Status:** ⚠️ POTENTIAL ISSUE
- **Current approach:** Heuristic (`len(text) // 4`)
- **Anthropic's approach:** Exact tokenization via API
- **Risk:** May underestimate tokens, still hit 200K limit
- **Solution exists:** `utils/token_counter.py` has `count_conversation_tokens()` API method

---

## 🔧 Current Fix (Temporary)

**What I did:**
```python
# TEMPORARILY DISABLED - Function not implemented yet
# if len(conversation_history) > 0:
#     from core.combined_agent_worker import prune_conversation_for_context_limit
#     ... (entire block commented out)
```

**Result:**
- ✅ System no longer crashes
- ✅ Users can send messages
- ⚠️ No protection against 200K token limit
- ⚠️ Long conversations will eventually fail with Anthropic API error

---

## 🎯 Proper Solution (Needs Implementation)

### Option 1: **Implement the Pruning Function**

**Create:** `AI_infrastructure/core/combined_agent_worker.py`

```python
def prune_conversation_for_context_limit(
    conversation_history: List[Dict],
    max_estimated_tokens: int = 180000,
    preserve_first_user: bool = True
) -> List[Dict]:
    """
    Intelligently prune conversation history to fit within token limit
    
    Strategy:
    1. Use exact token counting (utils/token_counter.py)
    2. If under limit, return unchanged
    3. If over limit:
       - Preserve first user message (context)
       - Preserve last N messages (recent conversation)
       - Remove middle messages (old history)
    4. Re-count and verify under limit
    
    Args:
        conversation_history: List of message dicts
        max_estimated_tokens: Target token count (default: 180K)
        preserve_first_user: Keep first user message (default: True)
    
    Returns:
        Pruned conversation history
    """
    from utils.token_counter import count_conversation_tokens
    
    # Count current tokens
    current_tokens = count_conversation_tokens(conversation_history)
    
    if current_tokens <= max_estimated_tokens:
        return conversation_history  # Under limit, no pruning needed
    
    print(f"[PRUNE] Conversation exceeds limit: {current_tokens} > {max_estimated_tokens}")
    
    # Strategy: Keep first message + last N messages
    if preserve_first_user and len(conversation_history) > 0:
        first_msg = [conversation_history[0]]
    else:
        first_msg = []
    
    # Binary search to find how many recent messages fit
    recent_msgs = conversation_history[-1:]  # Start with last message
    
    for i in range(len(conversation_history) - 2, 0, -1):
        test_history = first_msg + [conversation_history[i]] + recent_msgs
        test_tokens = count_conversation_tokens(test_history)
        
        if test_tokens > max_estimated_tokens:
            break  # Can't add more
        
        recent_msgs = [conversation_history[i]] + recent_msgs
    
    pruned_history = first_msg + recent_msgs
    final_tokens = count_conversation_tokens(pruned_history)
    
    print(f"[PRUNE] Result: {len(conversation_history)} → {len(pruned_history)} messages")
    print(f"[PRUNE] Tokens: {current_tokens} → {final_tokens}")
    
    return pruned_history
```

### Option 2: **Smart Summarization (Advanced)**

Instead of removing messages, summarize old parts:

```python
def prune_with_summarization(conversation_history, max_tokens):
    """
    1. Keep recent messages (last 50K tokens)
    2. Summarize middle messages (50-180K → 10K summary)
    3. Keep first message
    
    Result: [First] + [Summary] + [Recent]
    """
    # Use Claude to summarize old messages
    # Insert summary as system message
    # Return compact conversation
```

### Option 3: **Progressive Context (Best)**

```python
def progressive_context_management(conversation_history, max_tokens):
    """
    Hybrid approach:
    1. First 5 rounds: Full history
    2. Round 6-20: Keep first + summarize middle + last 5 rounds
    3. Round 20+: Rolling window (last 10 rounds + summary)
    """
```

---

## 📈 Token Usage Example

### Scenario: Long Conversation

```
Round 1:  User: "Hello" (5 tokens)
          AI: "Hi! How can I help?" (10 tokens)
          Total: 15 tokens

Round 10: Total: 15,000 tokens ✅ (Safe)

Round 50: Total: 75,000 tokens ✅ (Safe)

Round 100: Total: 150,000 tokens ⚠️ (Approaching limit)

Round 150: Total: 231,000 tokens ❌ (EXCEEDS LIMIT - API ERROR)
          ↓
     WITHOUT PRUNING: HTTP 400 from Anthropic
     WITH PRUNING: Prune to 180K, continue conversation ✅
```

---

## 🎯 Recommended Next Steps

### Immediate (Critical):
1. ✅ **DONE:** Comment out broken import (system works)
2. ⚠️ **TODO:** Monitor for "Token limit exceeded" errors in logs

### Short-term (This Week):
1. Implement `prune_conversation_for_context_limit()` in `combined_agent_worker.py`
2. Use exact token counting (`utils/token_counter.py`)
3. Test with long conversations (100+ rounds)
4. Add user notification: "Conversation history pruned for performance"

### Long-term (Nice to Have):
1. Smart summarization (condense old messages)
2. Progressive context management (hybrid approach)
3. Token usage dashboard (show user their usage)
4. Conversation checkpoints (save/restore state)

---

## 📝 Testing Checklist

**When implementing pruning function:**

- [ ] Test with empty conversation (edge case)
- [ ] Test with 1 message (preserve it)
- [ ] Test with conversation under limit (no pruning)
- [ ] Test with conversation at 190K tokens (prune to 180K)
- [ ] Test with conversation at 250K tokens (prune to 180K)
- [ ] Verify first user message preserved
- [ ] Verify recent messages preserved
- [ ] Verify token count accurate (use API, not heuristic)
- [ ] Test tool results preserved in recent messages
- [ ] Test thinking blocks handled correctly
- [ ] Performance test (pruning should take <1 second)

---

## 🔗 Related Files

**Core Files:**
- `AI_infrastructure/routes/agent_routes_v4.py` (line 498-510) - Where pruning would happen
- `AI_infrastructure/core/combined_agent_worker.py` - Where function should be implemented
- `AI_infrastructure/utils/token_counter.py` - Token counting utility (already exists!)

**Frontend:**
- `UI/business-ai-platform-v2.html` (line ~1464) - Sends full conversation history

**Documentation:**
- `PRUNING_FUNCTION_ANALYSIS.md` (this file)

---

## 💡 Key Insights

1. **Problem is VISIBLE in code comments:**
   - "prevents re-sending 231K+ tokens"
   - This means it HAS happened before!

2. **Solution already 50% built:**
   - `utils/token_counter.py` has exact token counting
   - Just need pruning logic

3. **Frontend design contributes:**
   - Sending full history every time is inefficient
   - Consider incremental messages in future

4. **User experience matters:**
   - Silent pruning = confusing ("where did my messages go?")
   - Need notification: "Older messages hidden for performance"

---

**Status:** Analysis complete, temporary fix in place, proper implementation needed.
