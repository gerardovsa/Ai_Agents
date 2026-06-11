# Maximum Rounds Parameter Audit
**Date:** November 3, 2025  
**Status:** ✅ AUDIT COMPLETE

## Summary
Found **3 PRIMARY LOCATIONS** for max_rounds/max_turns parameters:
- **1 NEEDS UPDATE**: `streaming_agent_worker.py` line 68 (max_rounds = 10 → 20)
- **2 ALREADY CORRECT**: `agent_worker.py` line 152 (max_turns = 20 ✅), `constants.py` line 12 (MAX_TURNS = 20 ✅)

## Detailed Findings

### 1. ✅ CONSTANTS CONFIGURATION (PRIMARY SOURCE)
**File:** `AI_infrastructure/config/constants.py`  
**Line:** 12  
**Current Value:** `MAX_TURNS = 20`  
**Status:** ✅ CORRECT - No changes needed

```python
# Maximum turns in multi-turn conversations
# Prevents infinite loops while allowing complex workflows
MAX_TURNS = 20
```

**Impact:** This is the centralized source for conversation turn limits. All modules should import from here.

---

### 2. ✅ AGENT WORKER (PRIMARY EXECUTION)
**File:** `AI_infrastructure/core/agent_worker.py`  
**Line:** 152  
**Current Value:** `max_turns=20`  
**Status:** ✅ CORRECT - Already aligned with constants

```python
result = agent.process_request(
    customer_message=prompt,
    max_turns=20,  # ✅ CORRECT
    conversation_history=conversation_history,
    content_blocks=content_blocks if file_data else None
)
```

**Impact:** Main agent execution path - used for non-streaming AI agent requests.

---

### 3. ❌ STREAMING AGENT WORKER (NEEDS UPDATE)
**File:** `AI_infrastructure/core/streaming_agent_worker.py`  
**Line:** 68  
**Current Value:** `max_rounds: int = 10`  
**Status:** ❌ NEEDS UPDATE to 20

```python
def execute_with_streaming(
    self,
    session_id: str,
    user_prompt: str,
    conversation_history: List[Dict],
    tools: List[Dict],
    system_prompt: str,
    user_id: Optional[int] = None,
    max_rounds: int = 10,  # ❌ NEEDS UPDATE
    current_round: int = 1
) -> Generator[Dict[str, Any], None, None]:
```

**Impact:** Streaming agent execution path - used for real-time streaming requests. This is the PRIMARY parameter that needs updating.

---

## Update Strategy

### Option 1: RECOMMENDED - Use Constants File
Update streaming_agent_worker.py to import from constants:

```python
from AI_infrastructure.config.constants import MAX_TURNS

def execute_with_streaming(
    self,
    session_id: str,
    user_prompt: str,
    conversation_history: List[Dict],
    tools: List[Dict],
    system_prompt: str,
    user_id: Optional[int] = None,
    max_rounds: int = MAX_TURNS,  # ✅ Import from constants
    current_round: int = 1
) -> Generator[Dict[str, Any], None, None]:
```

**Benefits:**
- Single source of truth for configuration
- Easy to change globally (one place: constants.py)
- Consistent with agent_worker.py pattern
- Centralized management for Account Settings UI

### Option 2: Direct Update
Simply change line 68 from `10` to `20`:

```python
max_rounds: int = 20,  # Updated from 10
```

**Pros:** Simple, immediate fix  
**Cons:** Creates duplicate values, harder to manage

---

## Secondary Locations (ARCHIVE - Not Active)

These are old/archived files that do NOT affect current operations:

### Archive Locations (Informational Only)
1. **agent_routes_v2.py** (archive)
   - Line 1089: `max_turns = 20` ✅

2. **agent_routes_OLD_MONOLITHIC.py** (archive)
   - Line 1085: `max_turns = 20` ✅

3. **agent_routes_LEGACY_DO_NOT_USE.py** (archive)
   - Line 1484: `max_turns = 20` ✅

4. **agent_routes copy.py** (archive)
   - Line 1589: `max_turns = 20` ✅

**Status:** These are archived/legacy files. No action needed.

---

## Verification Checklist

- [ ] Update streaming_agent_worker.py line 68
- [ ] Optionally import MAX_TURNS from constants.py
- [ ] Test streaming agent with multiple rounds
- [ ] Verify Account Settings UI can override this value
- [ ] Confirm non-streaming agent continues to work

---

## Next Steps

1. **Immediate:** Update streaming_agent_worker.py line 68 (change 10 → 20)
2. **Follow-up:** Add Account Settings UI to allow users to configure max_rounds
3. **Backend Integration:** Store user preferences and apply them at runtime
4. **Testing:** Verify both streaming and non-streaming agents respect the setting

---

## Related Features

**Account Settings UI Needed For:**
- ✨ Model selection (dropdown)
- 🎛️ Round parameters (max_turns, timeout)
- 📊 Token parameters (max_tokens, thinking budget)
- 💾 Persistence via localStorage
- 🔄 Backend synchronization

**User Control Flow:**
1. User opens Account Settings
2. Selects max_rounds (default 20)
3. Clicks Save
4. Value stored in localStorage
5. Sent to backend with next AI request
6. Agent uses user's setting instead of default

---

## Configuration Summary

| Parameter | File | Current Value | Target | Status |
|-----------|------|---------------|--------|--------|
| MAX_TURNS | constants.py | 20 | 20 | ✅ |
| max_turns | agent_worker.py | 20 | 20 | ✅ |
| max_rounds | streaming_agent_worker.py | **10** | **20** | ❌ NEEDS UPDATE |

**Critical:** Only 1 parameter needs updating (streaming_agent_worker.py line 68)
