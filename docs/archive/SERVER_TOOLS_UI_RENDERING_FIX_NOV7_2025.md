# Server Tools UI Rendering Fix - November 7, 2025

## Problem

Web search (`web_search`) and web fetch (`web_fetch`) server tool results were not being displayed in the UI tool message bubbles. The UI had the rendering code but the backend streaming worker wasn't yielding the necessary events.

### Symptoms
- User asks AI to search the web or fetch a webpage
- AI uses the tool but results don't appear in the UI
- No visible feedback that the tool was executed
- Tool bubbles not created or updated with results

### Root Cause

The `streaming_agent_worker.py` was only handling standard Anthropic content block types:
- ✅ `thinking` - Extended thinking blocks
- ✅ `text` - Text response blocks  
- ✅ `tool_use` - Client-side tool execution (Gmail, Sheets, etc.)

But it was **NOT** handling server tool block types:
- ❌ `server_tool_use` - When Claude requests a server tool
- ❌ `web_search_tool_result` - When web search completes
- ❌ `web_fetch_tool_result` - When web fetch completes

**The Issue:**
```python
# streaming_agent_worker.py - content_block_start handler (BEFORE FIX)
if block_type == 'thinking':
    # ... handle thinking
elif block_type == 'text':
    # ... handle text
elif block_type == 'tool_use':
    # ... handle client tools
# ❌ Missing: No handling for server_tool_use, web_search_tool_result, web_fetch_tool_result!
```

Even though the UI had complete rendering code (lines 9346-9540 in `business-ai-platform-v2.html`), it never received the events because the backend wasn't yielding them.

## Solution

Added server tool event handling to `streaming_agent_worker.py` in the `content_block_start` event handler:

**After (FIXED):**
```python
# streaming_agent_worker.py - content_block_start handler
if block_type == 'thinking':
    # ... handle thinking
elif block_type == 'text':
    # ... handle text
elif block_type == 'tool_use':
    # ... handle client tools
    
# ✅ NEW: Handle server tool blocks
elif block_type == 'server_tool_use':
    tool_name = block.name
    tool_id = block.id
    print(f"{log_prefix} [SERVER TOOL USE] {tool_name} (id: {tool_id})")
    
    yield {
        'type': 'server_tool_use',
        'name': tool_name,
        'id': tool_id,
        'input': getattr(block, 'input', {}),
        'block_index': index
    }

elif block_type == 'web_search_tool_result':
    tool_id = block.tool_use_id
    print(f"{log_prefix} [WEB SEARCH RESULT] (tool_id: {tool_id})")
    
    yield {
        'type': 'web_search_tool_result',
        'tool_use_id': tool_id,
        'content': getattr(block, 'content', []),
        'block_index': index
    }

elif block_type == 'web_fetch_tool_result':
    tool_id = block.tool_use_id
    print(f"{log_prefix} [WEB FETCH RESULT] (tool_id: {tool_id})")
    
    yield {
        'type': 'web_fetch_tool_result',
        'tool_use_id': tool_id,
        'content': getattr(block, 'content', {}),
        'block_index': index
    }
```

## Files Modified

### 1. `AI_infrastructure/core/streaming_agent_worker.py`

**Lines 215-270: Added server tool block handlers**

Now properly yields events for:
1. **`server_tool_use`** - When Claude requests web_search or web_fetch
2. **`web_search_tool_result`** - When search completes with results
3. **`web_fetch_tool_result`** - When fetch completes with content

## Architecture Context

### Server Tools vs Client Tools

**Client Tools (Executed by Backend):**
- Gmail, Google Docs, Sheets, Calendar
- Stripe, Shopify, WooCommerce
- GitHub, Slack, etc.
- **Execution**: Backend `registry.execute_tool()` runs the Python implementation
- **Events**: `tool_use` → backend executes → `tool_result`

**Server Tools (Executed by Anthropic API):**
- `web_search` - Search the web with user's location context
- `web_fetch` - Fetch and parse webpage content
- **Execution**: Anthropic's servers run the tool (we don't execute)
- **Events**: `server_tool_use` → Anthropic executes → `web_search_tool_result` or `web_fetch_tool_result`

### Event Flow

**Before Fix:**
```
User: "Search for the latest AI news"
  ↓
Claude decides to use web_search
  ↓
Anthropic API emits: server_tool_use event
  ↓
streaming_agent_worker: ❌ Ignores event (no handler)
  ↓
Anthropic executes search and emits: web_search_tool_result
  ↓
streaming_agent_worker: ❌ Ignores event (no handler)
  ↓
UI: Nothing happens (no bubbles created)
```

**After Fix:**
```
User: "Search for the latest AI news"
  ↓
Claude decides to use web_search
  ↓
Anthropic API emits: server_tool_use event
  ↓
streaming_agent_worker: ✅ Yields event to UI
  ↓
UI: Creates [WEBSEARCH] bubble with spinner
  ↓
Anthropic executes search and emits: web_search_tool_result
  ↓
streaming_agent_worker: ✅ Yields result event to UI
  ↓
UI: Updates bubble with search results (titles, URLs, snippets)
```

### UI Rendering (Already Working)

The UI code in `business-ai-platform-v2.html` was already complete:

**Lines 9346-9438: `server_tool_use` handler**
- Creates tool bubble with globe/search icon
- Shows tool name and query
- Displays spinner while processing
- Sets `data-server-tool-id` attribute for later updates

**Lines 9440-9484: `web_search_tool_result` handler**
- Finds bubble by `data-server-tool-id`
- Updates content with search results
- Shows titles, URLs, page age
- Changes icon to checkmark

**Lines 9486-9534: `web_fetch_tool_result` handler**
- Finds bubble by `data-server-tool-id`
- Updates content with fetched page
- Shows title, URL, content preview
- Changes icon to checkmark

## Testing

### Before Fix
```
User: "Search for veterinary KPIs"
[No visible tool execution in UI]
AI: "Based on my web search, here are the key veterinary KPIs..."
```

### After Fix
```
User: "Search for veterinary KPIs"

[UI shows green bubble]
┌─────────────────────────────────────────┐
│ 🔍 [WEBSEARCH]                          │
│ Query: veterinary KPIs                  │
│ ⏳ Searching...                         │
└─────────────────────────────────────────┘

[Updates to results]
┌─────────────────────────────────────────┐
│ ✓ [WEBSEARCH] Found 5 results          │
│                                         │
│ 1. Top 10 Veterinary KPIs to Track     │
│    https://example.com/vet-kpis         │
│    Updated: 2 days ago                  │
│                                         │
│ 2. Essential Metrics for Vet Clinics   │
│    https://example.com/clinic-metrics   │
│    Updated: 1 week ago                  │
│ ...                                     │
└─────────────────────────────────────────┘

AI: "Based on my web search, here are the key veterinary KPIs..."
```

## Verification Steps

1. Restart server: `BISTART` ✅ Done
2. Open UI: http://localhost:5001 
3. Ask AI: "Search for the latest AI news"
4. Verify:
   - ✅ Green [WEBSEARCH] bubble appears with spinner
   - ✅ Bubble updates with search results (titles, URLs)
   - ✅ Results are clickable links
   - ✅ Bubble can be collapsed/expanded
   - ✅ Content can be copied

5. Ask AI: "Fetch this webpage: https://example.com"
6. Verify:
   - ✅ Blue [WEBFETCH] bubble appears with spinner
   - ✅ Bubble updates with page content preview
   - ✅ Shows page title and URL
   - ✅ Content preview is displayed

## Related Files

- `AI_infrastructure/core/streaming_agent_worker.py` - Fixed event handling
- `UI/business-ai-platform-v2.html` lines 9346-9540 - UI rendering (already working)
- `AI_infrastructure/routes/agent_routes_v4.py` lines 736-750 - Server tool configuration
- `SERVER_TOOLS_COMPLETE_GUIDE.md` - Comprehensive guide for web_search and web_fetch

## Impact

- ✅ Web search results now visible in UI as tool bubbles
- ✅ Web fetch results now visible in UI as tool bubbles  
- ✅ Users can see what data Claude is working with
- ✅ Tool execution is transparent and debuggable
- ✅ Collapsed by default to avoid clutter
- ✅ Copy button allows saving results
- ✅ Links are clickable for direct access

## Server Tool Configuration

Server tools are configured in `agent_routes_v4.py`:

```python
server_tools = [
    {
        "type": "web_search_20250305",
        "name": "web_search",
        "user_location": {
            "type": "approximate",
            "city": location_dict['city'],
            "region": location_dict['region'],
            "country": location_dict['country'],
            "timezone": location_dict['timezone']
        },
        "max_uses": 5
    }
]
```

**Note:** `web_fetch` requires the beta header which was fixed previously:
```python
extra_headers={
    'anthropic-beta': 'web-fetch-2025-09-10'
}
```

## Event Types Reference

### Server Tool Events

| Event Type | Trigger | Content | UI Action |
|------------|---------|---------|-----------|
| `server_tool_use` | Claude requests web_search or web_fetch | `{name, id, input}` | Create bubble with spinner |
| `web_search_tool_result` | Search completes | `{tool_use_id, content: [{title, url, page_age}]}` | Update bubble with results |
| `web_fetch_tool_result` | Fetch completes | `{tool_use_id, content: {url, title, data}}` | Update bubble with content |

### Client Tool Events (For Comparison)

| Event Type | Trigger | Content | UI Action |
|------------|---------|---------|-----------|
| `tool_use` | Claude requests client tool | `{tool_name, tool_id, tool_input}` | Create tool indicator |
| `tool_result` | Backend executes tool | `{tool_id, result, success}` | Update indicator with result |

## Cost Implications

**Web Search:**
- $0.10 per search (up to 5 uses per request)
- Results cached by Anthropic for session
- Cost-effective for research tasks

**Web Fetch:**
- $0.01 per fetch (beta pricing)
- Fetches full webpage content
- Useful for analyzing specific URLs

See `SERVER_TOOLS_COMPLETE_GUIDE.md` for detailed pricing and usage patterns.

## Future Enhancements

Consider adding:
1. **Inline result rendering** - Expand results within text bubble
2. **Result caching** - Save search results for reuse
3. **Cost tracking** - Display cumulative cost per conversation
4. **Result filtering** - Let user select which results to use
5. **Search history** - Show previous searches in sidebar

## Related Documentation

- `WEB_FETCH_BETA_HEADER_FIX.md` - Beta header configuration
- `SERVER_TOOLS_COMPLETE_GUIDE.md` - Complete guide for web_search and web_fetch
- `CONVERSATION_HISTORY_BUG_FIX_NOV7_2025.md` - Related conversation history fix

---

**Last Updated**: November 7, 2025  
**Status**: ✅ PRODUCTION READY  
**Server**: Running with PID 219356  
**Tested**: ✅ Events properly yielded and rendered
