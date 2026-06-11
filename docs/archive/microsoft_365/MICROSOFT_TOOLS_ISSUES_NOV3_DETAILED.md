# Microsoft 365 Tools - Critical Issues Analysis (Nov 3, 2025)

## Summary
Three critical issues preventing Microsoft 365 tools from working properly with AI agent.

---

## ISSUE #1: Tool Name Mismatch (CRITICAL)

### Problem
Claude is calling tools with incorrect names that don't exist in registry:
```
Tool not found: microsoft_word_create_document
Tool not found: microsoft_excel_create_workbook
```

### What Claude Is Calling
- `microsoft_word_create_document`
- `microsoft_excel_create_workbook`

### What Registry Actually Has
- `word_create_document` ✅
- `excel_create_workbook` ✅

### Root Cause
Claude is hallucinating tool names by adding `microsoft_` prefix. This happens because:
1. Schema files are named `microsoft_word_tools.json` 
2. Implementation modules are named `microsoft_word_tools.py`
3. But the tool NAMES inside schemas are just `word_create_document` (no prefix)

### Evidence
```python
# What registry exports (CORRECT):
Tools in registry: ['word_create_document', 'excel_create_workbook']

# What Anthropic tools list shows (CORRECT):
Anthropic tool names: ['word_create_document', 'excel_create_workbook']

# What Claude tries to call (WRONG):
Claude's attempted tool calls: ['microsoft_word_create_document', 'microsoft_excel_create_workbook']
```

### Solution Needed
Option A: Prefix all Microsoft tool names in schemas with `microsoft_` prefix
```json
{
  "name": "microsoft_word_create_document",  // Add prefix
  "description": "Create a new Word document..."
}
```

Option B: Update agent prompt to explicitly list available tool names

**RECOMMENDED**: Option A (consistent with other platforms)

---

## ISSUE #2: Missing Positional Arguments for OneDrive Tools

### Problem
```
ERROR: MicrosoftOneDriveTools.onedrive_upload_file() missing 2 required positional arguments: 'user_id' and 'local_file_path'
```

### Root Cause
The Microsoft tool implementation expects positional arguments but the registry is passing them as keyword arguments.

### Implementation Issue
Microsoft tool methods like:
```python
class MicrosoftOneDriveTools:
    def onedrive_upload_file(self, user_id: str, local_file_path: str, **kwargs):
        # user_id and local_file_path are required positional args
        pass
```

But registry calls them with:
```python
# Registry tries to call with all kwargs:
tool_instance.onedrive_upload_file(
    **kwargs  # user_id and local_file_path should be here but might not be
)
```

### Schema Check
Looking at `microsoft_onedrive_tools.json` for `onedrive_upload_file`:
- Required parameters should include: `user_id`, `local_file_path`
- These need to be in the `required` array

### Solution Needed
1. ✅ Verify schema has correct `required` array
2. ✅ Ensure tool receives all required parameters
3. Modify tool invocation to properly extract and pass parameters

---

## ISSUE #3: Credential Injection Not Working

### Problem
Tools are being called but credentials not being passed:
- `user_id` parameter missing
- `_injected_credentials` not present
- OAuth tokens not available to Microsoft tools

### Current Code (agent_worker.py - lines 358-365)
```python
if tool_name.startswith('google_') or tool_name.startswith(('outlook_', 'word_', 'excel_', ...)):
    # Add user_id and injected_credentials
    input_data['_user_id'] = user_id
    input_data['_injected_credentials'] = True
```

### Issue
This condition doesn't catch:
- `microsoft_word_create_document` (because it checks for `word_` not `microsoft_word_`)
- Any other renamed tools

### Solution Needed
Update credential injection to catch all Microsoft prefixes:
```python
# Check both 'word_' AND 'microsoft_word_' patterns
if tool_name.startswith(('google_', 'microsoft_', 'outlook_', 'word_', 'excel_', 'teams_', ...)):
    input_data['_user_id'] = user_id
    input_data['_injected_credentials'] = True
```

Or simpler:
```python
if tool_name.startswith(('google_', 'microsoft_')) or any(tool_name.startswith(p) for p in MICROSOFT_PREFIXES):
    input_data['_user_id'] = user_id
    input_data['_injected_credentials'] = True
```

---

## Summary of All Three Issues

| Issue | Type | Status | Action |
|-------|------|--------|--------|
| Tool name mismatch | Schema naming | CRITICAL | Add `microsoft_` prefix to all tool names in schemas |
| Missing positional args | Parameter passing | CRITICAL | Verify `required` array in schemas is complete |
| Credential injection | Auth passing | CRITICAL | Update agent framework credential condition to match new tool names |

---

## Files That Need Changes

### 1. All 10 Microsoft Schema Files
Add `microsoft_` prefix to every tool name:
- `tools/schemas/microsoft_word_tools.json` - Add `microsoft_` to all tool names
- `tools/schemas/microsoft_excel_tools.json` - Add `microsoft_` to all tool names
- `tools/schemas/microsoft_outlook_tools.json` - Already have proper names
- `tools/schemas/microsoft_teams_tools.json`
- `tools/schemas/microsoft_onedrive_tools.json`
- `tools/schemas/microsoft_calendar_tools.json`
- `tools/schemas/microsoft_forms_tools.json`
- `tools/schemas/microsoft_todo_tools.json`
- `tools/schemas/microsoft_sharepoint_tools.json`
- `tools/schemas/microsoft_onenote_tools.json`

### 2. Agent Framework Files
Update credential injection logic:
- `AI_infrastructure/core/agent_worker.py` - Lines with credential injection check
- `AI_infrastructure/core/streaming_agent_worker.py` - Same update needed

---

## Next Steps (Priority Order)

1. **URGENT**: Add `microsoft_` prefix to all tool names in Word, Excel, OneDrive, Teams schemas
2. Verify `required` arrays are complete in all Microsoft schemas
3. Update agent framework credential injection to match new tool names
4. Test tool execution end-to-end with proper credentials
5. Verify Word and Excel document creation works

---

## Quick Fix Checklist

- [ ] Add `microsoft_` prefix to Word tool names (e.g., `microsoft_word_create_document`)
- [ ] Add `microsoft_` prefix to Excel tool names (e.g., `microsoft_excel_create_workbook`)
- [ ] Add `microsoft_` prefix to other Microsoft tools (Teams, OneDrive, etc.)
- [ ] Verify `required` arrays have all required parameters
- [ ] Update agent_worker.py credential injection condition
- [ ] Update streaming_agent_worker.py credential injection condition
- [ ] Test Word document creation
- [ ] Test Excel workbook creation
- [ ] Test OneDrive file upload
- [ ] Test Teams message sending

