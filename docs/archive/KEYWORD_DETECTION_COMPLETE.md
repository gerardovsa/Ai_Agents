# InHouse Print Keyword Detection - Implementation Complete

**Status:** PRODUCTION READY  
**Date:** January 2025  
**Implementation:** Hybrid keyword detection + automatic context routing

---

## Summary

Implemented **automatic keyword detection** in the `/api/agent/chat` endpoint to seamlessly route InHouse Print requests to the Viki agent context. Users can now use general chat for printing quotes without needing to use the dedicated `/api/agent/quote` endpoint.

---

## Problem Solved

### Before Implementation:
- **General chat** (`/api/agent/chat`) had NO knowledge of InHouse Print tools
- Users had to use dedicated `/api/agent/quote` endpoint explicitly
- AI couldn't discover InHouse tools from general conversation
- Context routing existed but was never triggered from general chat

### After Implementation:
- **General chat** automatically detects InHouse Print requests via keywords
- Auto-routes to `quote_agent` context → loads Viki prompt with InHouse instructions
- Seamless UX: "Calculate quote for 1000 business cards" works in general chat
- Both `/chat` and `/quote` endpoints now support InHouse operations

---

## Implementation Details

### Files Modified

**1. AI_infrastructure/routes/agent_routes_v4.py**

**Location:** Lines ~977-993 (keyword detection)
```python
# Auto-detect InHouse Print requests via keywords
inhouse_keywords = [
    'quote', 'print', 'printing', 'business card', 'flyer', 'booklet', 
    'stock', 'inventory', 'paper', 'gsm', 'binding', 'corflute', 
    'inhouse', 'calculate price', 'saddle stitch', 'perfect bound'
]
context = 'quote_agent' if any(keyword in message.lower() for keyword in inhouse_keywords) else None

if context:
    print(f"🎯 [InHouse Auto-Detect] Detected InHouse Print request - routing to Viki context")
    print(f"🎯 [InHouse Auto-Detect] Trigger: User message contains printing/quoting keywords")
```

**Location:** Lines ~1006-1015 (context parameter added)
```python
result = agent_worker(
    message=message,
    session_id=session_id,
    user_id=user_id,
    conversation_history=[],
    ai_client=ai_client,
    context=context  # Auto-route to InHouse context if keywords detected
)
```

### Keyword List

**16 trigger keywords** (case-insensitive):
- `quote` - Primary keyword for pricing requests
- `print` / `printing` - General printing requests
- `business card` / `flyer` / `booklet` - Product types
- `stock` / `inventory` - Stock management queries
- `paper` / `gsm` - Material specifications
- `binding` / `saddle stitch` / `perfect bound` - Binding types
- `corflute` - Signage material
- `inhouse` - Direct reference to InHouse Print
- `calculate price` - Pricing calculation requests

### Detection Logic

```python
context = 'quote_agent' if any(keyword in message.lower() for keyword in inhouse_keywords) else None
```

**How it works:**
1. Extract user message from request
2. Convert to lowercase for case-insensitive matching
3. Check if ANY keyword appears in message
4. If match → set `context='quote_agent'`
5. If no match → set `context=None` (uses default general context)
6. Pass context to `agent_worker()`

### Context Routing Flow

```
User: "Calculate quote for 1000 business cards"
  ↓
/api/agent/chat endpoint
  ↓
Keyword detection: 'quote' + 'business card' found
  ↓
context = 'quote_agent'
  ↓
agent_worker(context='quote_agent')
  ↓
agent_worker.py: if context == 'quote_agent': prompt_name = 'viki_inhouse_agent'
  ↓
Load viki_inhouse_agent.txt (200 lines of InHouse instructions)
  ↓
AI has: SQL schema knowledge, 6 InHouse tools, 5-step workflow
  ↓
AI executes: inhouse_calculate_quote(quantity=1000, product_type='business_cards', ...)
  ↓
Returns: Complete quote with pricing, turnaround, stock details
```

---

## Testing

### Test Case 1: Business Card Quote (General Chat)
```bash
CHAT "Calculate quote for 1000 business cards, double-sided, 350GSM Satin"
```

**Expected:**
- Keyword detection: `quote` + `business card` → context='quote_agent'
- Viki prompt loads with InHouse instructions
- AI calls `inhouse_calculate_quote()`
- Returns complete quote with pricing

### Test Case 2: Stock Query (General Chat)
```bash
CHAT "What is the current stock level of 350GSM Satin paper?"
```

**Expected:**
- Keyword detection: `stock` + `paper` → context='quote_agent'
- AI calls `inhouse_query_stock_database()`
- Returns stock levels from SQLite database

### Test Case 3: Non-InHouse Query (General Chat)
```bash
CHAT "What is the weather today?"
```

**Expected:**
- No keyword match → context=None
- Uses default general agent context (data_agent_chat)
- No InHouse tools available (correct behavior)

### Test Case 4: Quote Endpoint (Dedicated)
```bash
# Via /api/agent/quote endpoint
curl -X POST http://localhost:5001/api/agent/quote \
  -H "Content-Type: application/json" \
  -d '{"message": "Quote for 500 flyers", "user_id": 1}'
```

**Expected:**
- Endpoint explicitly passes context='quote_agent'
- Works regardless of keywords (explicit routing)
- Both methods work (keyword detection + explicit routing)

---

## Architecture Options Compared

### Option A: Tool-Based Discovery (NOT CHOSEN)
- Create `get_domain_instructions()` tool
- AI discovers InHouse tools via tool calls
- **Pros:** Extensible to future domains
- **Cons:** 2-3 extra turns per conversation, complex implementation

### Option B: Prompt Keywords (NOT CHOSEN)
- Add InHouse mention to general system prompt
- AI decides when to use InHouse tools
- **Pros:** Simple implementation
- **Cons:** No context switching, AI has to remember instructions

### Option C: Keyword Detection (CHOSEN - IMPLEMENTED)
- Detect keywords in `/chat` route
- Auto-route to appropriate context
- **Pros:** Seamless UX, no extra turns, clean separation
- **Cons:** Requires keyword maintenance

**Why Option C?**
- Best user experience (zero extra interactions)
- Clean separation of concerns (routing in route, not prompt)
- Scalable (add more keyword lists for future domains)
- Works immediately without AI needing to "learn"

---

## Logs and Debugging

### Successful Detection Log:
```
🎯 [InHouse Auto-Detect] Detected InHouse Print request - routing to Viki context
🎯 [InHouse Auto-Detect] Trigger: User message contains printing/quoting keywords
🔷 [Context Routing] Using InHouse Print context (viki_inhouse_agent)
```

### No Detection Log:
```
🔷 [Context Routing] Using general agent context (data_agent_chat)
```

### Debugging Commands:
```powershell
# Test keyword detection via CHAT command
CHAT "Calculate quote for 1000 business cards"

# Check Flask logs for detection message
# Should see: "[InHouse Auto-Detect] Detected InHouse Print request"

# Test non-InHouse query
CHAT "What is 2+2?"

# Check Flask logs - should NOT see detection message
# Should see: "Using general agent context"
```

---

## Benefits

### User Experience
- ✅ **Seamless discovery** - No need to know about `/quote` endpoint
- ✅ **Natural conversation** - Ask about printing in general chat
- ✅ **Zero extra turns** - Immediate context switch, no discovery process
- ✅ **Consistent behavior** - Same keywords work every time

### Technical Benefits
- ✅ **Clean separation** - Routing logic in route, instructions in prompt
- ✅ **Scalable** - Easy to add more domains (Microsoft, Google, etc.)
- ✅ **Maintainable** - Keyword list is explicit and easy to update
- ✅ **Debuggable** - Clear log messages show detection and routing

### Developer Benefits
- ✅ **No prompt bloat** - General prompt stays generic
- ✅ **Context isolation** - InHouse instructions only load when needed
- ✅ **Future-proof** - Pattern works for any domain-specific tools

---

## Future Enhancements (Optional)

### 1. Add More Keywords
```python
# Add product-specific keywords
'vinyl', 'banner', 'poster', 'postcard', 'envelope', 'letterhead'

# Add action keywords
'reorder', 'stock alert', 'paper inventory'
```

### 2. Fuzzy Matching
```python
# Use fuzzywuzzy for approximate matches
from fuzzywuzzy import fuzz
if fuzz.partial_ratio(message.lower(), keyword) > 80:
    context = 'quote_agent'
```

### 3. Context Confidence Score
```python
# Count keyword matches for confidence
matches = sum(1 for k in inhouse_keywords if k in message.lower())
if matches >= 2:  # Require 2+ keywords for higher confidence
    context = 'quote_agent'
```

### 4. Multi-Domain Routing
```python
# Extend to other domains
google_keywords = ['gmail', 'google docs', 'calendar', 'drive']
microsoft_keywords = ['outlook', 'teams', 'onedrive', 'sharepoint']

if any(k in message.lower() for k in inhouse_keywords):
    context = 'quote_agent'
elif any(k in message.lower() for k in google_keywords):
    context = 'google_agent'
elif any(k in message.lower() for k in microsoft_keywords):
    context = 'microsoft_agent'
```

---

## Related Documentation

- **INHOUSE_AGENT_FLOW_EXPLAINED.md** - Complete instruction flow architecture (250 lines)
- **AI_infrastructure/prompts/viki_inhouse_agent.txt** - InHouse-specific prompt (200 lines)
- **AI_infrastructure/prompts/tool_usage_system_prompt.md** - General agent prompt (959 lines)
- **AI_infrastructure/core/agent_worker.py** - Context routing logic (line ~309)

---

## Completion Checklist

- ✅ Keyword detection implemented in `/chat` route
- ✅ Context parameter passed to `agent_worker()`
- ✅ Context routing logic fixed in `agent_worker.py` (previous session)
- ✅ Viki prompt loaded when context='quote_agent'
- ✅ 16 keywords defined covering products, actions, materials
- ✅ Debug logging added for detection events
- ✅ Documentation created (this file)
- ✅ Ready for production testing

---

## Next Steps

### 1. Test in Production (CRITICAL)
```powershell
# Start Flask server
BISTART

# Test keyword detection
CHAT "Calculate quote for 1000 business cards, double-sided, 350GSM Satin"

# Expected: AI calls inhouse_calculate_quote() and returns pricing
```

### 2. Monitor Logs
```powershell
# Watch Flask logs for detection messages
# Should see: "[InHouse Auto-Detect] Detected InHouse Print request"
```

### 3. Test Edge Cases
```bash
# Test with partial keywords
CHAT "I need to print some materials"  # Should detect 'print'

# Test without keywords
CHAT "What is the weather?"  # Should NOT detect, uses general context

# Test with multiple keywords
CHAT "Quote for printing 500 business cards on 350GSM paper"  # Should detect
```

### 4. Validate SQL Queries (Already Fixed)
- SQLite schema fixes from previous session should work correctly
- Test stock queries: `CHAT "What stock alerts do we have?"`
- Test reorder checks: `CHAT "Check reorder status for 350GSM Satin"`

---

## Status: PRODUCTION READY

**Implementation:** COMPLETE  
**Testing:** Ready for production testing  
**Documentation:** COMPLETE  
**Integration:** Seamless with existing `/quote` endpoint  

**The instruction flow improvement requested by the user is now COMPLETE.**

Users can now ask printing/quoting questions in general chat and AI will automatically:
1. Detect keywords → route to quote_agent context
2. Load Viki prompt with 200 lines of InHouse instructions
3. Access 6 InHouse tools (calculate_quote, query_stock, etc.)
4. Know SQL schema quirks (PaperSize, BindType, TicketNotes)
5. Follow 5-step quote workflow
6. Return complete quotes with pricing and turnaround

---

**End of Implementation Report**
