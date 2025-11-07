# Next Steps - November 1, 2025

## Fixes #12 & #13 Complete - Testing Required ✅

**Status:** All code changes applied, server restart needed

**What Was Fixed:**
- ✅ Fix #12: Conditional OAuth parameter passing (non-Google tools)
- ✅ Fix #13: Google Workspace OAuth database integration (Calendar, Tasks, Meet)
- ✅ Total: 25 Google Workspace functions updated + 3 worker files fixed

---

## STEP 1: Restart Server (Required)

```powershell
cd C:\Users\gpoli\GIT\AI_agents
BISTART
```

**Expected Console Output:**
```
[AI Agent] Starting Flask server on port 5001...
[Registry] Loading 594 tools...
[Registry] Loaded 594 tools successfully
[OAuth] OAuth middleware registered
[Waitress] Serving on http://0.0.0.0:5001
```

---

## STEP 2: Test Google Workspace Tools (Now Fixed) ⭐ NEW

### Test 1: Google Calendar (Fix #13)
**Command:** "List my calendars"

**Expected Console Output:**
```
[OAuth] Loaded Google OAuth credentials for gerardo@vetsuccessacademy.com
[Stream 1] Executing: google_calendar_list_calendars
[Stream 1] Parameters: _user_id=1, _injected_credentials=True
[Stream 1] ✅ Tool Result: [{"kind": "calendar#calendarListEntry", "id": "primary", ...}]
```

**Success Criteria:**
- ✅ NO "unexpected keyword argument '_user_id'" error
- ✅ NO "credentials_desktop.json not found" error
- ✅ Console shows "Loaded Google OAuth credentials"
- ✅ Returns list of user's calendars

### Test 2: Google Tasks (Fix #13)
**Command:** "List my task lists"

**Expected Console Output:**
```
[OAuth] Loaded Google OAuth credentials for gerardo@vetsuccessacademy.com
[Stream 2] Executing: google_tasks_list_task_lists
[Stream 2] Parameters: _user_id=1, _injected_credentials=True
🔑 Google Tasks: Using database OAuth for user 1
[Stream 2] ✅ Tool Result: {"task_lists": [...], "total": 3}
```

**Success Criteria:**
- ✅ NO parameter errors
- ✅ NO file not found errors
- ✅ Console shows "Using database OAuth for user 1"
- ✅ Returns task lists

### Test 3: Google Meet (Fix #13)
**Command:** "List my upcoming Google Meet meetings"

**Expected Console Output:**
```
[OAuth] Loaded Google OAuth credentials for gerardo@vetsuccessacademy.com
[Stream 3] Executing: google_meet_list_upcoming_meetings
[Stream 3] Parameters: _user_id=1, _injected_credentials=True
[Stream 3] ✅ Tool Result: {"meetings": [...]}
```

**Success Criteria:**
- ✅ NO parameter errors
- ✅ Uses user's OAuth credentials
- ✅ Returns meetings

### Test 4: Google Docs (Should Still Work)
**Command:** "Create a Google Doc titled 'Test Fix 13'"

**Expected:**
- ✅ OAuth credentials loaded
- ✅ Document created successfully
- ✅ NO parameter errors

### Test 5: Google Drive (Should Still Work)
**Command:** "List files in my Google Drive"

**Expected:**
- ✅ OAuth credentials loaded
- ✅ File list returned
- ✅ NO parameter errors

---

## STEP 3: Test Non-Google Tools (Now Fixed) ⭐

### Test 3: WooCommerce (Previously Crashed)
**Command:** "List my WooCommerce products"

**Before Fix #12:**
```
❌ TypeError: woocommerce_get_products() got an unexpected keyword argument '_user_id'
```

**After Fix #12 (Expected):**
```
⚠️ Error: Tool not found: woocommerce_get_products
(Different error - tool not loaded in registry, but NO parameter error!)
```

**Success Criteria:**
- ✅ NO "unexpected keyword argument '_user_id'" error
- ⚠️ May show "tool not found" (separate issue)
- ⚠️ May show authentication error (missing API key)

### Test 4: GitHub (Previously Crashed)
**Command:** "Create a GitHub repo named 'test-oauth-fix'"

**Before Fix #12:**
```
❌ TypeError: github_create_repo() got an unexpected keyword argument '_user_id'
```

**After Fix #12 (Expected):**
```
⚠️ Error: Tool not found: github_create_repo
OR
⚠️ Error: GitHub API authentication failed
(NO parameter error!)
```

**Success Criteria:**
- ✅ NO "unexpected keyword argument" error
- Tool may fail for OTHER reasons (not loaded, missing API token)

### Test 5: Supabase (Previously Crashed)
**Command:** "Query the users table in Supabase"

**Expected:**
- ✅ NO parameter error
- ⚠️ May fail with: Tool not found OR authentication error

---

## STEP 4: Verify Console Logs

### Look for These Patterns:

**Google Workspace Tools (Should See OAuth Params):**
```
[Stream 1] Tool: google_docs_create
[Stream 1] Parameters: title='Test', _user_id=1, _injected_credentials=True
[OAuth] Loaded Google OAuth credentials
```

**Non-Google Tools (Should NOT See OAuth Params):**
```
[Stream 2] Tool: woocommerce_get_products
[Stream 2] Parameters: per_page=10
(No _user_id, no _injected_credentials - CORRECT!)
```

---

## Expected Results Summary

### ✅ Working Tools (Should Continue Working)
- `google_docs_smart_create_from_markdown`
- `google_drive_list_files`
- `google_sheets_create`
- All Google Workspace tools (20+ tools)

### ✅ Fixed Tools (No More Parameter Errors)
- `google_forms_create_complete_form`
- `woocommerce_get_products`
- `github_create_repo`
- `supabase_query`
- `cloudconvert_convert`
- `assemblyai_transcribe`
- `ngrok_start_tunnel`
- 10+ other non-Google tools

**Note:** These tools may still fail for OTHER reasons:
- Tool not loaded in registry → "Tool not found"
- Missing API credentials → Authentication error
- Wrong parameters → Validation error

**But they will NOT fail with:** `"unexpected keyword argument '_user_id'"`

---

## STEP 5: Investigate Remaining Issues (Optional)

### Issue 1: Tools Not Found (~500 tools)

**Error Pattern:**
```
⚠️ Error: Tool not found: stripe_get_balance
⚠️ Error: Tool not found: outlook_send_email
⚠️ Error: Tool not found: teams_send_message
```

**Affected Platforms:**
- Microsoft 365 (ALL tools)
- Stripe, PayPal
- Instagram
- Database/Calculator tools
- Most third-party integrations

**Investigation Steps:**
```powershell
# Check which tools are loaded
cd AI_infrastructure
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); print(f'Loaded: {len(r.tools)} tools'); print('Sample:', list(r.tools.keys())[:20])"

# Check if Microsoft 365 tools exist in file system
ls tools\schemas\microsoft_*.json
ls tools\implementations\microsoft_*.py

# Check if registry is loading all schemas
python -c "from tools.registry_v3 import RegistryV3; import os; schemas_dir = 'tools/schemas'; schema_files = [f for f in os.listdir(schemas_dir) if f.endswith('.json')]; print(f'Schema files found: {len(schema_files)}'); print('Files:', schema_files[:10])"
```

**Possible Causes:**
1. Tool schemas exist but not imported by registry
2. Tool implementations missing
3. Registry filtering out certain tools
4. Import errors preventing tool loading

### Issue 2: Missing credentials_desktop.json (2 tools)

**Error Pattern:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'credentials_desktop.json'
```

**Affected Tools:**
- `gmail_send_email`
- `google_calendar_list_events`

**Investigation:**
```powershell
# Check if file exists
ls credentials_desktop.json

# Check where it's expected
cd google_workspace
rg "credentials_desktop.json" -A 5 -B 5
```

**Possible Solutions:**
1. Create `credentials_desktop.json` file
2. Update Gmail/Calendar tools to use same OAuth flow as Docs/Drive
3. Point to correct credentials file path

### Issue 3: API Authentication Errors

**Error Pattern:**
```
{'ok': False, 'error': 'not_authed'}  # Slack
Missing required parameter: from_  # Twilio
```

**Affected Tools:**
- `slack_send_message` - Wrong/missing API token
- `twilio_send_sms` - Missing phone number parameter

**Fix Required:**
- Update Slack API token in environment variables
- Add Twilio phone number configuration

---

## Testing Checklist

- [ ] Server restarted successfully
- [ ] 594 tools loaded in console
- [ ] OAuth middleware registered
- [ ] **Google Docs creation works** (OAuth flow)
- [ ] **Google Drive list works** (OAuth flow)
- [ ] **WooCommerce query** - NO parameter error (may fail for other reasons)
- [ ] **GitHub repo creation** - NO parameter error (may fail for other reasons)
- [ ] **Supabase query** - NO parameter error (may fail for other reasons)
- [ ] Console shows conditional parameter passing (Google tools only)
- [ ] UI bubbles render correctly (thinking, tool, response)

---

## If Tests Fail

### Scenario 1: Google Tools Failing
**Problem:** `google_docs_create` shows "unexpected keyword argument"

**Cause:** Conditional logic not applied correctly

**Fix:** Re-check `streaming_agent_worker.py` lines 303-317

### Scenario 2: Non-Google Tools Still Crashing
**Problem:** `woocommerce_get_products` still shows "_user_id parameter error"

**Cause:** Fix #12 not applied to all worker locations

**Fix:** Verify all 3 locations updated:
1. `streaming_agent_worker.py` line 303
2. `agent_worker.py` line 341
3. `agent_worker.py` line 536

### Scenario 3: No OAuth Credentials
**Problem:** "Using service account fallback" appears for Google tools

**Cause:** OAuth middleware not running OR user not logged in

**Fix:** 
1. Check OAuth middleware registered in console logs
2. Verify user logged in with valid JWT token
3. Check `oauth_tokens` table has credentials

---

## Documentation References

- `FIX_12_CONDITIONAL_OAUTH_PARAMETERS.md` - Complete Fix #12 guide
- `COMPLETE_FIX_SUMMARY_OCT31_2025.md` - All 12 fixes timeline
- `FIX_8_9_10_THINKING_AND_TOOLS_OCT31.md` - Fixes #8-10 (OAuth series)
- `OAUTH_AUTHENTICATION_FIX_OCT31.md` - OAuth integration guide

---

## Success Criteria

✅ **Fix #12 Successful If:**
1. Google Workspace tools continue working with OAuth
2. Non-Google tools NO LONGER show "_user_id parameter" errors
3. Console shows conditional parameter passing (Google vs non-Google)
4. 10+ previously broken tools now executable (may fail for other reasons)

🎉 **Expected Outcome:**
- Google OAuth: ✅ Working
- Tool parameter errors: ✅ Fixed
- Remaining issues: Tool availability (separate problem to investigate)

**Status:** Ready for testing! Restart server and verify all scenarios above.
