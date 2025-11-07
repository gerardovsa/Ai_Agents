# REGISTRY AUDIT FINDINGS & FIX PLAN

**Date:** November 3, 2025  
**Audit Status:** Complete  
**Issues Found:** 6 Critical  

---

## AUDIT RESULTS

### Test Results Summary
```
Tools Tested:           10 high-priority tools
Working:                2 (20%)  ✅ gmail_send_email, google_forms_create_form
Auth Issues:            1 (10%)  ⚠️  gmail_list_available_accounts
Param Issues:           2 (20%)  ❌ synergy_update_session, synergy_get_session
Execution Errors:       4 (40%)  ❌ gsheets_create, gsheets_write, gsheets_read, google_calendar_create_event
Not Found:              1 (10%)  ❌ google_docs_create

FAILURE RATE: 80%
```

---

## CRITICAL ISSUES FOUND

### 1. PHANTOM TOOLS - Tools Listed But Not Found (40%)

**Tools Affected:**
- `gsheets_create` ❌ Tool not found
- `gsheets_write` ❌ Tool not found  
- `gsheets_read` ❌ Tool not found
- `google_docs_create` ❌ Tool not found

**Root Cause:**
Tools are defined in schemas but implementations use different names:
- Schema defines: `gsheets_create`
- Implementation function: `create_spreadsheet` or similar in `google_sheets.py`
- Registry can't map schema name → implementation function

**Impact:** Users discover tools that don't execute

**Solution:**
1. Audit all google_workspace implementations to find actual function names
2. Create name mapping layer in registry
3. Update execute_tool() to use mapped names

---

### 2. AUTH PARAMETER REJECTION (10%)

**Tool Affected:**
- `gmail_list_available_accounts` ❌ got unexpected keyword argument '_user_id'

**Root Cause:**
Function signature doesn't accept `**kwargs`:
```python
# Current (WRONG):
def gmail_list_available_accounts():
    # No parameters!

# Expected (FIX):
def gmail_list_available_accounts(**kwargs):
    user_id = kwargs.get('_user_id')
    # Use user_id for credential injection
```

**Impact:** Auth parameter passing fails

**Solution:**
1. Add `**kwargs` to function signatures
2. Extract `_user_id` and `_injected_credentials` from kwargs
3. Use for credential injection

---

### 3. MISSING POSITIONAL ARGUMENTS (20%)

**Tools Affected:**
- `synergy_update_session` ❌ missing 2 required positional arguments: 'session_id' and 'updates'
- `synergy_get_session` ❌ missing 1 required positional argument: 'session_id'

**Root Cause:**
Registry calls function with `**kwargs` but function expects positional args:
```python
# registry.execute_tool('synergy_update_session', session_id="x", updates={...})
# Calls: func(**{"session_id": "x", "updates": {...}})
# But function signature: def synergy_update_session(session_id, updates, **kwargs)
# ✅ WORKS - kwargs get passed as positional!

# BUT if call is: func(**{"updates": {...}})  (missing session_id)
# ❌ FAILS - session_id is missing!
```

**Impact:** Tools can't be executed with proper parameter mapping

**Solution:**
1. Ensure function signatures match schema parameters
2. Update calls to pass all required parameters

---

### 4. DATETIME FORMAT ERROR (10%)

**Tool Affected:**
- `google_calendar_create_event` ❌ HttpError 400: "Start and end times must either both be date or both be dateTime"

**Root Cause:**
Datetime format is wrong. Google Calendar requires:
- RFC3339 with timezone: `2025-11-05T10:00:00Z` ✅
- OR full date: `2025-11-05` ✅

Test used wrong format:
- `2025-11-05T10:00:00` ❌ (missing timezone/Z)
- `2025-11-05T11:00:00` ❌ (missing timezone/Z)

**Impact:** Calendar events can't be created

**Solution:**
1. Add timezone 'Z' to datetime format in test
2. Document RFC3339 format requirement in schema

---

## FIXES NEEDED

### Fix 1: Audit Google Workspace Function Names

**What to do:**
1. Check `google_workspace/google_sheets.py` for actual function names
2. Check `google_workspace/google_docs.py` for actual function names
3. Compare with schema names
4. Create mapping table

**Files to check:**
- `google_workspace/google_sheets.py`
- `google_workspace/google_docs.py`
- `tools/schemas/google_sheets_tools.json`
- `tools/schemas/google_docs_tools.json`

---

### Fix 2: Add **kwargs to Function Signatures

**Functions to update:**
- `gmail_list_available_accounts()` → `gmail_list_available_accounts(**kwargs)`
- All other Google Workspace tools that need auth

**Pattern:**
```python
# Before:
def gmail_list_available_accounts():
    # ... code ...

# After:
def gmail_list_available_accounts(**kwargs):
    user_id = kwargs.get('_user_id')
    injected_creds = kwargs.get('_injected_credentials')
    # ... use credentials ...
```

---

### Fix 3: Fix DateTime Format

**Change in test:**
```python
# Before:
"start_time": "2025-11-05T10:00:00Z",  # Wrong format
"end_time": "2025-11-05T11:00:00Z",    # Wrong format

# After:
"start_time": "2025-11-05T10:00:00Z",  # Correct with Z
"end_time": "2025-11-05T11:00:00Z",    # Correct with Z
```

**Note:** Already has Z in test, but something else is wrong

---

### Fix 4: Update Synergy Functions

Check if synergy functions are receiving parameters correctly.

---

## ACTION PLAN

### Phase 1: Identify Function Names (15 min)
```
[ ] Check google_sheets.py for actual function names
[ ] Check google_docs.py for actual function names
[ ] Create mapping of schema names → implementation names
```

### Phase 2: Fix Function Signatures (30 min)
```
[ ] Add **kwargs to gmail_list_available_accounts()
[ ] Add **kwargs to all auth-requiring functions
[ ] Extract and use _user_id and _injected_credentials
```

### Phase 3: Fix DateTime Format (10 min)
```
[ ] Update google_calendar test with correct timezone format
[ ] Verify RFC3339 format compliance
```

### Phase 4: Fix Synergy Functions (15 min)
```
[ ] Check synergy_update_session parameter handling
[ ] Check synergy_get_session parameter handling
[ ] Verify registry.execute_tool() passes parameters correctly
```

### Phase 5: Test All Fixes (15 min)
```
[ ] Run deep_audit_registry_clean.py
[ ] Verify all 10 tools work
[ ] Check success rate reaches 100%
```

---

## EXPECTED OUTCOMES

After fixes:
- ✅ All 10 tools should execute successfully
- ✅ 0% failure rate
- ✅ Proper authentication parameter handling
- ✅ Correct datetime formats
- ✅ Full parameter mapping

---

## DETAILED ERROR LOGS

### Error: gsheets_create

```
[EXCEPTION] Tool not found: gsheets_create
```

**Analysis:**
- Schema defines: `gsheets_create`
- Registry returns: "Tool not found"
- Likely cause: Function has different name in google_sheets.py

---

### Error: gmail_list_available_accounts

```
[AUTH_REQUIRED] gmail_list_available_accounts() got an unexpected keyword argument '_user_id'
```

**Analysis:**
- Function doesn't accept **kwargs
- Credential injection fails
- Need to add **kwargs parameter

---

### Error: google_calendar_create_event

```
[EXECUTION_ERROR] HttpError 400: Start and end times must either both be date or both be dateTime
```

**Analysis:**
- Datetime format issue
- Should be RFC3339 with timezone
- Check if Z suffix is present

---

## NEXT STEPS

1. **START:** Phase 1 - Identify actual function names in google_workspace
2. **THEN:** Phase 2 - Add **kwargs to function signatures
3. **THEN:** Phase 3 - Fix datetime formats
4. **THEN:** Phase 4 - Fix synergy functions
5. **THEN:** Phase 5 - Run full test and verify

---

## FILES TO MODIFY

### Priority 1 (Blocking):
- [ ] `google_workspace/google_sheets.py` - Check function names
- [ ] `google_workspace/google_docs.py` - Check function names
- [ ] `google_workspace/gmail.py` - Add **kwargs to functions
- [ ] `deep_audit_registry_clean.py` - Fix datetime format test

### Priority 2 (Important):
- [ ] `tools/implementations/synergy.py` - Fix parameter handling
- [ ] `tools/schemas/*.json` - Verify parameter definitions

### Priority 3 (Nice to have):
- [ ] Documentation updates
- [ ] Error message improvements

---

**Status:** Ready for Phase 1 fixes  
**Estimated Time:** 1.5 hours total  
**Success Criteria:** 10/10 tools working (100% success rate)
