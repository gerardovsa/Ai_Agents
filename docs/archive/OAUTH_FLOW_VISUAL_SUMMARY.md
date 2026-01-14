# OAuth Authentication Flow - Visual Summary

## Complete End-to-End Flow (After Fixes #9a + #9b)

```
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (UI)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. User clicks "Sign in with Google"                          │
│     → OAuth consent flow                                        │
│     → JWT token stored in localStorage                          │
│                                                                 │
│  2. User sends message: "Create a Google Doc"                  │
│     → Headers: { Authorization: "Bearer <JWT_TOKEN>" }         │
│     → POST /api/agent/start                                    │
│                                                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│             MIDDLEWARE (agent_routes_v4.py)                     │
│             @agent_bp.before_request                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  3. Extract JWT from Authorization header                      │
│     token = request.headers.get('Authorization')              │
│     → "Bearer eyJ0eXAiOiJKV1QiLCJh..."                         │
│                                                                 │
│  4. Verify JWT signature                                       │
│     user_manager = UserAuthManager()                           │
│     verified = user_manager.verify_token(token)                │
│     → Returns: { user_id: 1, email: "user@example.com" }      │
│                                                                 │
│  5. Set g.user_id for all routes                              │
│     g.user_id = verified['user_id']                           │
│     → g.user_id = 1                                           │
│                                                                 │
│  ✅ Console: "🔑 [AUTH] Request authenticated: user_id=1"       │
│                                                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              ROUTE HANDLER (/api/agent/start)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  6. Get user_id from middleware                                │
│     user_id = g.get('user_id', 1)                             │
│     → user_id = 1                                             │
│                                                                 │
│  7. Start background worker thread                             │
│     thread = threading.Thread(                                 │
│         target=run_simple_agent_worker,                        │
│         args=(session_id, prompt, user_id, ...)               │
│     )                                                          │
│     thread.start()                                             │
│                                                                 │
│  ✅ Console: "[Stream 1] 👤 User ID: 1"                        │
│                                                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           WORKER (streaming_agent_worker.py)                    │
│           StreamingAgentWorker.execute_round()                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  8. Claude API returns tool use request                        │
│     tool_name = "google_docs_smart_create_from_markdown"      │
│     tool_input = { title: "Test Doc", content: "..." }        │
│                                                                 │
│  9. Execute tool with _user_id parameter                       │
│     result = self.registry.execute_tool(                       │
│         tool_name,                                             │
│         **tool_input,                                          │
│         _user_id=user_id    ← FIX #9b (was: user_id=user_id) │
│     )                                                          │
│                                                                 │
│  ✅ Console: "[Tool] google_docs_smart_create_from_markdown"    │
│                                                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              REGISTRY (registry_v3.py)                          │
│              execute_tool()                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  10. Get tool function                                          │
│      func = self.tools[tool_name]['function']                  │
│      → google_docs_smart_create_from_markdown                  │
│                                                                 │
│  11. Call function with kwargs                                  │
│      return func(**kwargs)                                      │
│      → func(title="Test Doc", content="...", _user_id=1)       │
│                                                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│          GOOGLE TOOL (google_docs.py)                           │
│          google_docs_smart_create_from_markdown()               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  12. Function signature with _user_id parameter                 │
│      def google_docs_smart_create_from_markdown(                │
│          title,                                                 │
│          markdown_content,                                      │
│          _user_id=None,    ← Receives user_id from worker      │
│          _injected_credentials=None,                            │
│          ...                                                    │
│      ):                                                         │
│                                                                 │
│  13. Fetch OAuth credentials from database                      │
│      cred_dict = _get_user_credentials_if_available(           │
│          _user_id,                                             │
│          _injected_credentials                                 │
│      )                                                          │
│      → Queries: oauth_tokens table WHERE user_id=1             │
│      → Returns: { access_token: "...", refresh_token: "..." }  │
│                                                                 │
│  14. Build Google Docs API service                              │
│      docs_service = _get_docs_service(                          │
│          user_id=_user_id,                                     │
│          injected_credentials=cred_dict                         │
│      )                                                          │
│      → Uses user's OAuth credentials (not service account)     │
│                                                                 │
│  15. Create document with user's permissions                    │
│      document = docs_service.documents().create(...).execute() │
│      → Document created in user's Google Drive                 │
│      → Uses user's quota, permissions, access                  │
│                                                                 │
│  ✅ Console: "🔑 Using database OAuth credentials for user 1"   │
│  ✅ Console: "✅ Document created: https://docs.google.com/..." │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Parameter Name Convention

### CRITICAL: Underscore Prefix Required

All Google Workspace tools use `_user_id` parameter (with underscore prefix):

```python
# ✅ CORRECT - Google tool signatures
def gmail_send_email(to, subject, body, _user_id=None, ...):
def google_docs_create_document(title, _user_id=None, ...):
def google_drive_create_folder(name, _user_id=None, ...):
def google_calendar_create_event(summary, _user_id=None, ...):

# ❌ WRONG - Will not work (underscore missing)
def gmail_send_email(to, subject, body, user_id=None, ...):
```

### Why the Underscore?

1. **Prevents parameter conflicts** - User might pass `user_id` as tool parameter
2. **Indicates internal parameter** - Not part of tool's public API
3. **Consistent convention** - All 584+ Google tools follow this pattern
4. **Credential injection marker** - Signals parameter used for authentication

---

## Before vs After Fix #9b

### BEFORE (Not Working)
```python
# streaming_agent_worker.py line 305
result = self.registry.execute_tool(
    tool_name,
    **tool_input,
    user_id=user_id    # ❌ WRONG - no underscore
)

# Google tool receives:
# - title = "Test Doc"
# - content = "..."
# - user_id = 1         # ❌ Tool doesn't recognize this parameter
# - _user_id = None     # ❌ Tool sees no user_id!

# Result:
# ❌ "No user OAuth credentials - using service account"
# ❌ 403 PERMISSION_DENIED error
```

### AFTER (Working)
```python
# streaming_agent_worker.py line 305
result = self.registry.execute_tool(
    tool_name,
    **tool_input,
    _user_id=user_id    # ✅ CORRECT - with underscore
)

# Google tool receives:
# - title = "Test Doc"
# - content = "..."
# - _user_id = 1        # ✅ Tool recognizes this parameter!

# Result:
# ✅ "Using database OAuth credentials for user 1"
# ✅ Document created successfully
```

---

## Database Schema

### oauth_tokens Table
```sql
CREATE TABLE oauth_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,  -- 'google' or 'microsoft'
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_expiry DATETIME,
    scope TEXT,
    email TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE (user_id, platform)
);
```

### Query Pattern
```python
# Tool fetches credentials
cursor.execute("""
    SELECT access_token, refresh_token, token_expiry
    FROM oauth_tokens
    WHERE user_id = ? AND platform = 'google'
    ORDER BY updated_at DESC
    LIMIT 1
""", (user_id,))

row = cursor.fetchone()
if row:
    credentials = {
        'access_token': row[0],
        'refresh_token': row[1],
        'token_expiry': row[2]
    }
else:
    # Fall back to service account
    credentials = service_account_credentials
```

---

## Testing Checklist

### ✅ Fix #9a: Middleware Extracts user_id
```powershell
# Check console logs after sending message:
🔑 [AUTH] Request authenticated: user_id=1, email=user@example.com
```

### ✅ Fix #9b: Worker Passes _user_id
```powershell
# Check console logs during tool execution:
[Stream 1] 👤 User ID for credential injection: 1
[Tool Execution] google_docs_smart_create_from_markdown
🔑 Using database OAuth credentials for user 1
```

### ❌ Should NOT See (Old Behavior)
```powershell
# These errors indicate OAuth not working:
❌ No user OAuth credentials - using service account
❌ Using service account from environment variables
❌ WARNING: Encountered 403 Forbidden with reason "PERMISSION_DENIED"
```

---

## Summary

**Fix #9a:** Middleware extracts `user_id` from JWT → Sets `g.user_id`  
**Fix #9b:** Worker passes `_user_id` (with underscore) → Tools recognize parameter  

**Result:** Complete OAuth credential injection pipeline working end-to-end!

**Documentation:** See `OAUTH_AUTHENTICATION_FIX_OCT31.md` for comprehensive guide
