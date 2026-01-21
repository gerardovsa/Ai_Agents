# Process Files/Attachments User ID Fix - January 22, 2026

## Problem Statement
`process_outlook_attachment_for_ai` and other file processing tools were failing with error:
```
"No user_id provided. User must be authenticated to use Microsoft tools."
```

Despite user being authenticated and other Microsoft tools working correctly.

## Root Cause
In `combined_agent_worker.py` (line 3289-3293), the code only passed `_user_id` parameter to tools starting with `google_` or `microsoft_` prefixes:

```python
# ❌ OLD CODE - BROKEN
if tool_name.startswith(('google_', 'microsoft_')):
    result = registry.execute_tool(tool_name=tool_name, _user_id=user_id, _injected_credentials=True, **tool_input)
else:
    result = registry.execute_tool(tool_name=tool_name, **tool_input)
```

**Why This Failed:**
- `process_outlook_attachment_for_ai` is defined in `tools/implementations/universal_file_tools.py`
- It doesn't start with `microsoft_` prefix (it's a universal tool that works with multiple platforms)
- Therefore it wasn't receiving the `_user_id` parameter
- The tool requires `user_id` to authenticate with Microsoft Graph API to download attachments

## The Fix

**File 1:** `AI_infrastructure/core/combined_agent_worker.py` (Line ~3289)

```python
# ✅ NEW CODE - FIXED
# ALWAYS pass _user_id for ALL tools
# Previously only passed for google_/microsoft_ tools, but universal_file_tools 
# (process_outlook_attachment_for_ai, etc.) also need user authentication
result = registry.execute_tool(tool_name=tool_name, _user_id=user_id, _injected_credentials=True, **tool_input)
```

**File 2:** `tools/registry_v3.py` (Line ~713)

```python
# ✅ FIX (Jan 22, 2026): Smart parameter handling
# Try calling with all kwargs first (for tools with **kwargs like universal_file_tools)
try:
    result = func(**kwargs)
except TypeError as e:
    # If tool doesn't accept internal params, filter them out and retry
    if "unexpected keyword argument" in str(e) and any(k.startswith('_') for k in kwargs):
        logger.debug(f"[EXECUTE_TOOL] Tool '{tool_name}' doesn't accept internal params, filtering...")
        tool_kwargs = {k: v for k, v in kwargs.items() if not k.startswith('_')}
        result = func(**tool_kwargs)
    else:
        raise  # Re-raise if it's a different TypeError
```

**Rationale:**
1. **Universal Approach:** All tools receive `_user_id` from combined_agent_worker
2. **Smart Filtering:** Registry tries passing all params first, then filters if needed
3. **Backward Compatible:** Tools with `**kwargs` get everything; tools without get filtered params
4. **No Breaking Changes:** Existing tools continue to work regardless of signature

## Technical Details

### How User ID Flows Through System

1. **User Authentication:** User logs in, `user_id` stored in session
2. **AI Request:** Frontend sends request with session token
3. **Flask Route:** Extracts `user_id` from session → `g.user_id`
4. **Agent Worker:** Passes `user_id` to `execute_streaming_request()`
5. **Tool Execution:** NOW passes `_user_id` to **ALL** tools via `registry.execute_tool()`
6. **Registry:** Resolves user_id (priority: kwargs → thread-local → Flask g)
7. **Tool Implementation:** Extracts `user_id` from kwargs:
   ```python
   user_id = kwargs.pop('_user_id', None) or kwargs.pop('user_id', None)
   ```

### Universal File Handler Authentication

The `process_outlook_attachment_for_ai` tool uses this flow:

```python
# tools/implementations/universal_file_tools.py
@tool_executor()
def process_outlook_attachment_for_ai(message_id: str, attachment_id: str, mode: str = 'auto', **kwargs):
    # Extract user_id from kwargs (injected by credential system)
    user_id = kwargs.pop('_user_id', None) or kwargs.pop('user_id', None)
    
    if not user_id:
        return {'success': False, 'error': 'No user_id provided...'}
    
    handler = UniversalFileHandler(user_id=user_id, **kwargs)
    return handler.process_file(source='outlook', source_id={...}, mode=mode)
```

The `UniversalFileHandler` then:
1. Fetches Microsoft Graph credentials from database using `user_id`
2. Authenticates with Microsoft Graph API
3. Downloads the attachment
4. Processes it (PDF → text extraction, image → base64, etc.)
5. Returns content block ready for AI consumption

## Related Files

- **Fixed:** `AI_infrastructure/core/combined_agent_worker.py` (line 3289)
- **Tool Implementation:** `tools/implementations/universal_file_tools.py`
- **Core Handler:** `AI_infrastructure/core/universal_file_handler.py`
- **Registry:** `tools/registry_v3.py` (execute_tool method handles user_id resolution)

## Testing

### Before Fix
```bash
# AI tries to process Outlook attachment
process_outlook_attachment_for_ai(message_id="...", attachment_id="...")

# Result: ❌ ERROR
{
  "success": false,
  "error": "No user_id provided. User must be authenticated to use Microsoft tools."
}
```

### After Fix
```bash
# AI tries to process Outlook attachment
process_outlook_attachment_for_ai(message_id="...", attachment_id="...")

# Result: ✅ SUCCESS
{
  "success": true,
  "method": "files_api",
  "content_block": {
    "type": "document",
    "source": {
      "type": "url",
      "url": "https://api.anthropic.com/v1/messages/batches/..."
    }
  },
  "metadata": {
    "name": "report.pdf",
    "size": 377900,
    "token_estimate": 800
  }
}
```

## Impact

### Fixed Tools
All universal file processing tools now work:
- ✅ `process_outlook_attachment_for_ai`
- ✅ `process_gmail_attachment_for_ai`
- ✅ `process_onedrive_file_for_ai`
- ✅ `process_google_drive_file_for_ai`
- ✅ `process_sharepoint_file_for_ai`

### No Breaking Changes
- Existing tools continue to work (they already ignore unused kwargs)
- No schema changes required
- No frontend changes required
- Backward compatible with all existing tool implementations

## Why This Wasn't Caught Earlier

1. **Recent Feature:** Universal file tools were added November 2025
2. **Testing Scope:** Initial testing likely used direct API calls with explicit `user_id`
3. **Tool Naming:** The `microsoft_` prefix filter made sense for `microsoft_outlook_*` tools but didn't account for universal tools
4. **Edge Case:** Only affects tools that:
   - Require authentication
   - Are NOT prefixed with `google_` or `microsoft_`
   - Are called through AI agent (not direct API)

## Prevention

### Best Practice: Always Pass Authentication
```python
# ✅ GOOD - Pass user_id to ALL tools
result = registry.execute_tool(
    tool_name=tool_name, 
    _user_id=user_id, 
    _injected_credentials=True, 
    **tool_input
)

# ❌ BAD - Conditional passing based on tool name prefix
if tool_name.startswith(('google_', 'microsoft_')):
    result = registry.execute_tool(tool_name=tool_name, _user_id=user_id, ...)
else:
    result = registry.execute_tool(tool_name=tool_name, ...)  # May fail!
```

### Registry Already Handles This
The `registry_v3.py` `execute_tool()` method has multi-source fallback for user_id:
1. `_user_id` in kwargs (explicit injection) ← **THIS FIX ENSURES THIS WORKS**
2. Thread-local storage (worker threads)
3. Flask g context (main request thread)

**Conclusion:** With this fix, ANY tool that needs authentication will receive it automatically, regardless of naming convention or module location.

## Commit Message
```
fix(agent): pass _user_id to ALL tools, not just google_/microsoft_ prefixed

Previously, only tools starting with google_ or microsoft_ received _user_id
parameter for authentication. This broke universal_file_tools like
process_outlook_attachment_for_ai which need auth but don't follow naming prefix.

Now ALL tools receive _user_id (tools that don't need it ignore via **kwargs).

Fixes: process_outlook_attachment_for_ai authentication errors
Impact: All universal file processing tools now work correctly
```

## Related Issues
- Universal File Tools implementation: November 2025
- Credential injection system: Phase 1 (October 2025)
- Thread-local storage fix: January 13, 2026
- **This fix:** January 22, 2026

## Key Takeaway
**Never filter authentication parameters based on tool name prefixes.** Always pass authentication context to all tools and let individual tools decide if they need it. This is more robust and prevents edge cases like this.
