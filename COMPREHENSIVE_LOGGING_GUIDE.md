# Comprehensive Logging Guide for Thread Routes
**Date:** November 25, 2025  
**Purpose:** Track functional flows and identify failures clearly

## Logging Pattern Standards

### Success Flow Format
```python
print(f"\n{'='*80}")
print(f"[FUNCTION_NAME] 🔷 Starting operation...")
print(f"{'='*80}")
print(f"[FUNCTION_NAME] Input param 1: {value1}")
print(f"[FUNCTION_NAME] Input param 2: {value2}")

# ... operation code ...

print(f"[FUNCTION_NAME] ✅ SUCCESS: Operation completed")
print(f"[FUNCTION_NAME] Result: {result_summary}")
print(f"{'='*80}\n")
```

### Failure Flow Format
```python
# Validation failure
if not required_field:
    print(f"[FUNCTION_NAME] ❌ FAILED: Missing {field_name}")
    print(f"{'='*80}\n")
    return error_response("error message", 400)

# Exception failure
except Exception as e:
    print(f"[FUNCTION_NAME] ❌ EXCEPTION: {str(e)}")
    import traceback
    traceback.print_exc()
    print(f"{'='*80}\n")
    return error_response(str(e), 500)
```

### Skip/No-Op Flow Format
```python
if condition_not_met:
    print(f"[FUNCTION_NAME] ⏭️  SKIPPED: Reason for skipping")
    print(f"{'='*80}\n")
    return success_response({"skipped": True})
```

## Icon Legend

| Icon | Meaning | Use Case |
|------|---------|----------|
| 🔷 | Starting | Function entry point |
| ✅ | Success | Operation completed successfully |
| ❌ | Failed | Validation error or exception |
| ⏭️  | Skipped | Intentionally not executed |
| 📝 | Create | Creating new resource |
| 💾 | Save | Saving/updating data |
| 📂 | Load | Loading/retrieving data |
| 🔄 | Autosave | Background/automatic save |
| 🗑️  | Delete | Removing resource |
| 📊 | List | Retrieving multiple items |
| 🔍 | Search | Finding specific items |

## Key Functions to Log

### High Priority (User-Facing Operations)
1. **create_thread** - Thread creation (Status: LOGGED ✅)
2. **save_thread** - Manual thread save  
3. **autosave_thread** - Automatic save (Status: LOGGED ✅)
4. **load_thread** - Thread retrieval
5. **delete_thread** - Thread deletion
6. **list_threads** - Thread listing

### Medium Priority (Background Operations)
7. **update_thread_title** - Title updates
8. **mark_thread_read** - Read status
9. **get_thread_stats** - Statistics
10. **branch_thread** - Thread branching

### Connection Pool Monitoring
Every database operation should log:
- **Before:** "Opening connection..."
- **After:** "Connection closed"
- **Error:** "Connection leak detected!"

## Expected Log Output Examples

### Successful Thread Creation
```
================================================================================
[THREAD CREATE] 📝 Creating new thread...
================================================================================
[THREAD CREATE] User ID: 14
[THREAD CREATE] Agent: prime
[THREAD CREATE] Title: New Chat
[THREAD CREATE] ✅ SUCCESS: Thread created
[THREAD CREATE] Thread slug: thread_1732571234567
[THREAD CREATE] Title: New Chat
================================================================================
```

### Failed Thread Creation (Missing User)
```
================================================================================
[THREAD CREATE] 📝 Creating new thread...
================================================================================
[THREAD CREATE] User ID: None
[THREAD CREATE] ❌ FAILED: Missing user_id
================================================================================
```

### Autosave Flow (Skipped - Not Milestone)
```
================================================================================
[AUTOSAVE] 🔄 Checking autosave trigger...
================================================================================
[AUTOSAVE] Agent: prime, Session: abc123
[AUTOSAVE] Message count: 3
[AUTOSAVE] ⏭️  SKIPPED: Waiting for milestone (current: 3, next: 5)
================================================================================
```

### Autosave Flow (Success - Milestone Reached)
```
================================================================================
[AUTOSAVE] 🔄 Checking autosave trigger...
================================================================================
[AUTOSAVE] Agent: prime, Session: abc123
[AUTOSAVE] Message count: 5
[AUTOSAVE] 💾 Milestone reached (5 messages) - saving...
[AUTOSAVE] ✅ SUCCESS: Thread auto-saved
[AUTOSAVE] Thread ID: prime_abc123
[AUTOSAVE] Messages: 5
================================================================================
```

### Connection Pool Exhaustion (Error)
```
================================================================================
[THREAD LOAD] 📂 Loading thread...
[THREAD LOAD] Thread slug: thread_123
================================================================================
[THREAD LOAD] User ID: 14
[POOL] Got connection from pool for 'sessions' (wait: 1.2ms)
[POOL] ❌ CONNECTION POOL EXHAUSTED - LEAKED CONNECTIONS DETECTED
Schema: sessions
Pool stats:
  Acquired: 9
  Returned: 7
  LEAKED: 2

SOLUTION:
  1. Check code for missing conn.close() calls
  2. Use context managers: with get_database_connection() as conn:
  3. Restart application to reset pool
[THREAD LOAD] ❌ EXCEPTION: Connection pool exhausted
Traceback (most recent call last):
  ...
================================================================================
```

## How to Read Logs

### 1. Look for Success Markers
- `✅ SUCCESS:` = Operation completed
- Count these to track successful operations per minute/hour

### 2. Look for Failure Markers
- `❌ FAILED:` = Validation error (bad input)
- `❌ EXCEPTION:` = Runtime error (system issue)
- Review stack traces for debugging

### 3. Look for Skip Markers
- `⏭️  SKIPPED:` = Intentional no-op (not an error)
- Common for conditional operations

### 4. Track Connection Pool Stats
- `[POOL]` messages show pool health
- Watch for "LEAKED" connections
- `Acquired` should equal `Returned`

## Implementation Status

✅ **Completed:**
- `autosave_thread` - Full logging with success/failure/skip paths
- `create_thread` - Entry logging added

⏳ **In Progress:**
- Adding logging to remaining 15+ functions

🔜 **Planned:**
- Connection pool health monitoring endpoint
- Real-time log streaming to UI
- Automated leak detection alerts

## Quick Reference Commands

```powershell
# View real-time logs (Flask terminal)
# Look for patterns: ✅ SUCCESS, ❌ FAILED, ⏭️  SKIPPED

# Count successful operations
Select-String -Path "flask_output.log" -Pattern "✅ SUCCESS" | Measure-Object

# Find failed operations
Select-String -Path "flask_output.log" -Pattern "❌ FAILED|❌ EXCEPTION"

# Check connection pool stats
Select-String -Path "flask_output.log" -Pattern "\[POOL\]"
```

## Next Steps

1. **Review current logs** - Check if patterns are clear
2. **Add missing logging** - Complete remaining functions
3. **Test failure scenarios** - Trigger errors intentionally to verify logging
4. **Monitor production** - Watch for patterns indicating issues

---

**Status:** Logging framework established, incrementally rolling out to all endpoints
**Last Updated:** November 25, 2025
