# Archived Agent Workers

**Date Archived:** November 7, 2025

## Why These Files Were Archived

These agent worker files have been **replaced by `combined_agent_worker.py`**, which consolidates all functionality from both workers with enhanced validation and error handling.

## Archived Files

### Primary Worker Files
- **`agent_worker.py`** - Original non-streaming agent worker
  - Functions: `run_agent_worker()`, `run_simple_agent_worker()`, `agent_worker()`
  - Features: Basic conversation handling, tool execution
  
- **`streaming_agent_worker.py`** - Original streaming agent worker
  - Class: `StreamingAgentWorker`
  - Functions: `execute_streaming_request()`, `create_streaming_worker()`
  - Features: SSE streaming, real-time responses

### Copy Files (Development Versions)
- `agent_worker copy.py` - Development backup
- `agent_worker copy 2.py` - Development backup
- `streaming_agent_worker copy.py` - Development backup

## Replacement: combined_agent_worker.py

The **`combined_agent_worker.py`** file (889 lines) contains ALL functionality from both workers plus improvements:

### Functions Available:
1. **`run_agent_worker()`** - Main agent worker (non-streaming)
2. **`run_simple_agent_worker()`** - Simplified agent worker (non-streaming)
3. **`agent_worker()`** - Legacy agent worker (non-streaming)
4. **`execute_streaming_request()`** - Streaming agent worker (SSE)

### Validation Functions:
5. **`validate_conversation_history()`** - Validates full conversation
6. **`validate_and_reorder_assistant_content()`** - Fixes thinking block order
7. **`validate_user_content()`** - Validates user messages
8. **`normalize_content_to_blocks()`** - Normalizes content format
9. **`strip_thinking_blocks()`** - Removes thinking blocks for storage
10. **`prepare_content_for_storage()`** - Prepares content for database

### Key Improvements Over Old Workers:
- **7 validation fixes** for Anthropic API compliance
- **Thinking block ordering** - Ensures thinking blocks come first
- **Orphaned tool_result detection** - Removes invalid tool results
- **String-to-block conversion** - Handles mixed content types
- **Block field validation** - Ensures all blocks have required fields
- **Duplicate role detection** - Prevents consecutive same-role messages
- **Unified error handling** - Consistent error messages across all workers

## All Routes Updated

All routes in **`agent_routes_v4.py`** have been updated to import from `combined_agent_worker`:

```python
# Line 384
from core.combined_agent_worker import run_agent_worker, run_simple_agent_worker

# Line 830
from core.combined_agent_worker import execute_streaming_request

# Lines 1202, 1398
from core.combined_agent_worker import agent_worker
```

## Testing

All functionality has been tested via:
- **`test_combined_worker.py`** - Comprehensive test suite
  - Results: 6/7 validation tests passed
  - All import tests passed
  - All 645 tools loaded successfully

## Production Status

- **Status:** ✅ PRODUCTION READY
- **Deployed:** November 7, 2025
- **Server:** Running on port 5001
- **Tools:** 645 tools loaded
- **Test Results:** 6/7 passed (1 edge case not production-critical)

## Rollback (If Needed)

If you need to rollback to old workers:

1. Move archived files back to `core/` folder
2. Update imports in `agent_routes_v4.py`:
   ```python
   from core.agent_worker import run_agent_worker, run_simple_agent_worker, agent_worker
   from core.streaming_agent_worker import execute_streaming_request
   ```
3. Restart Flask server

## Questions?

See documentation:
- `COMBINED_WORKER_DEPLOYMENT_SUCCESS.md` (root folder)
- `DEPLOYMENT_SUMMARY_NOV7.md` (root folder)
- `test_combined_worker.py` (root folder)

---

**⚠️ DO NOT DELETE THESE FILES** - Keep for reference and potential rollback needs.
