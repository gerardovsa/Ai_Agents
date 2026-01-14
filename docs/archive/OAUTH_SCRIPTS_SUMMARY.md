# OAuth Scripts Summary - Quick Answer

## The Question
**"what are all these scripts?"** - 12 OAuth-related files identified

---

## The Answer

You have **12 OAuth scripts**, but only **6-8 are actually used**:

### ✅ ACTIVE (6 Core Files)

1. **google_auth_routes_V2_FIXED.py** - Google OAuth login flow (registered in Flask)
2. **microsoft_auth_routes_V2_FIXED.py** - Microsoft OAuth login flow (registered in Flask)
3. **user_auth.py** - User authentication and JWT tokens
4. **credential_injector.py** - Injects OAuth into tool calls ⭐ **CRITICAL**
5. **oauth_config.py** - OAuth provider configuration
6. **microsoft365_oauth_manager.py** - Microsoft OAuth utilities

### 🛠️ UTILITIES (2 Files)

7. **get_auth_token.py** - CLI utility for testing (generates JWT tokens)
8. **google-auth.js** - Chrome extension OAuth (separate from backend)

### ⚠️ LEGACY (2 Phase Out)

9. **oauth_manager.py** - File-based OAuth (being replaced by database OAuth)
10. **oauth_credential_loader.py** - Database OAuth loader (redundant with credential_injector)

### ❌ DELETE (2 Not Used)

11. **oauth_routes.py** - Old Google OAuth routes (NOT registered in Flask)
12. **routes/microsoft_auth_routes.py** - Old Microsoft OAuth routes (NOT registered in Flask)

---

## Why So Many Files?

### Evolution Over Time

**Phase 1 (Legacy):** File-based OAuth
- `oauth_manager.py` loaded tokens from `credentials_desktop.json` files
- Single-user, no database storage
- Problem: Not multi-tenant, files missing in production

**Phase 2 (Transition):** Database OAuth introduced
- `oauth_credential_loader.py` created to query database
- Tokens stored in `oauth_tokens` table
- Problem: Two systems coexisting (files + database)

**Phase 3 (Current):** Database OAuth standardized
- **Fix #13** unified Google tools to use database OAuth
- `credential_injector.py` became the standard approach
- `google_auth_routes_V2_FIXED.py` handles OAuth login flow
- Problem: Legacy files still exist

**Phase 4 (Future):** Cleanup needed
- Delete legacy OAuth routes
- Phase out file-based OAuth manager
- Consolidate credential loaders

### Multiple Providers

**Google Workspace:**
- `google_auth_routes_V2_FIXED.py` - OAuth routes
- `credential_injector.py` - Credential injection
- `oauth_manager.py` - Legacy file-based

**Microsoft 365:**
- `microsoft_auth_routes_V2_FIXED.py` - OAuth routes
- `microsoft365_oauth_manager.py` - OAuth utilities
- `routes/microsoft_auth_routes.py` - Old routes (not used)

### Multiple Interfaces

**Backend (Flask):**
- OAuth routes for web login
- Credential injection for tools

**Frontend (Chrome Extension):**
- `google-auth.js` - Separate OAuth flow for extension features

**CLI (Developer Tools):**
- `get_auth_token.py` - Generate JWT tokens for testing

---

## The Core OAuth Flow (Fix #13)

```
1. User clicks "Login with Google"
   → google_auth_routes_V2_FIXED.py

2. Google OAuth consent screen
   → User grants permissions

3. OAuth callback receives tokens
   → Stored in oauth_tokens table

4. User sends chat message with JWT token
   → OAuth middleware validates JWT

5. Agent worker calls Google tool
   → Passes _user_id=1, _injected_credentials=True

6. Tool calls credential_injector.py
   → Queries oauth_tokens table
   → Creates Google API service
   → Returns user's personal data
```

**Critical File:** `credential_injector.py` - This is the **CENTRAL HUB** for database OAuth

---

## What Each File Actually Does

| File | Purpose | Status | When Used |
|------|---------|--------|-----------|
| google_auth_routes_V2_FIXED.py | Google OAuth login flow | ✅ ACTIVE | User clicks "Login with Google" |
| microsoft_auth_routes_V2_FIXED.py | Microsoft OAuth login flow | ✅ ACTIVE | User clicks "Login with Microsoft" |
| user_auth.py | User auth and JWT tokens | ✅ ACTIVE | Every authenticated request |
| credential_injector.py | OAuth injection for tools | ✅ ACTIVE | Every Google tool call |
| oauth_config.py | OAuth provider config | ✅ ACTIVE | OAuth routes load config |
| microsoft365_oauth_manager.py | Microsoft OAuth utils | ✅ ACTIVE | Microsoft OAuth operations |
| get_auth_token.py | CLI token generator | 🛠️ UTILITY | Local testing only |
| google-auth.js | Chrome extension OAuth | ⚠️ FRONTEND | Extension features only |
| oauth_manager.py | File-based OAuth | ⚠️ LEGACY | Fallback (phasing out) |
| oauth_credential_loader.py | Database OAuth loader | ⚠️ LEGACY | Redundant with credential_injector |
| oauth_routes.py | Old Google OAuth routes | ❌ DELETE | Not registered in Flask |
| routes/microsoft_auth_routes.py | Old Microsoft OAuth routes | ❌ DELETE | Not registered in Flask |

---

## Quick Decision Guide

### "Which file should I modify to..."

**Add a new OAuth provider (e.g., Slack)?**
→ Create new file: `AI_infrastructure/routes/slack_auth_routes.py`
→ Model after: `google_auth_routes_V2_FIXED.py`
→ Register in: `flask_app.py`

**Change OAuth scopes for Google?**
→ Modify: `google_auth_routes_V2_FIXED.py` (line with scopes list)

**Inject OAuth into a new Google tool?**
→ Use: `credential_injector.create_google_service_with_user_credentials(user_id, service_name)`
→ Example: Fix #13 updated 25 Google functions this way

**Change OAuth credentials (client_id/secret)?**
→ Update: `.env.master` file
→ Loaded by: `oauth_config.py`

**Generate JWT token for CLI testing?**
→ Run: `python get_auth_token.py user@example.com`

**Check if user is logged in?**
→ Query: `oauth_tokens` table WHERE `user_id = ?`
→ Or use: `@oauth_required` middleware decorator

---

## Database Schema

### oauth_tokens Table (24 columns)

**Key Columns:**
- `user_id` - Which user owns these tokens
- `platform` - 'google' or 'microsoft'
- `access_token` - Current access token (expires in 1 hour)
- `refresh_token` - Refresh token (never expires unless revoked)
- `expires_at` - When access token expires
- `email` - User's email address
- `scope` - Granted permissions

**Example Query:**
```sql
SELECT access_token, refresh_token
FROM oauth_tokens
WHERE user_id = 1 AND platform = 'google'
ORDER BY updated_at DESC
LIMIT 1
```

---

## Next Steps (Cleanup)

### Priority 1: Delete Legacy Files
- [ ] Delete `AI_infrastructure/routes/oauth_routes.py` (not registered)
- [ ] Delete `routes/microsoft_auth_routes.py` (not registered)

### Priority 2: Consolidate OAuth Loading
- [ ] Remove `oauth_credential_loader.py` (use `credential_injector.py` instead)
- [ ] Update any tools using `oauth_credential_loader` to use `credential_injector`

### Priority 3: Phase Out File-Based OAuth
- [ ] Migrate any remaining tools from `oauth_manager.py` to database OAuth
- [ ] Remove `credentials_desktop.json` references
- [ ] Delete `oauth_manager.py` once all tools migrated

### Priority 4: Centralize Config Loading
- [ ] Update OAuth routes to import from `oauth_config.py`
- [ ] Remove direct `.env.master` loading from routes
- [ ] Single source of truth for OAuth credentials

---

## Key Takeaways

1. **You have 12 OAuth files, but only 6-8 are active**
   - 6 core files (OAuth routes, auth, credential injection)
   - 2 utilities (CLI, Chrome extension)
   - 2 legacy (file-based OAuth, old loader)
   - 2 to delete (old OAuth routes)

2. **Fix #13 unified Google tools to use database OAuth**
   - 25 functions updated across 3 files
   - All now use `credential_injector.py`
   - No more `credentials_desktop.json` dependency

3. **credential_injector.py is the critical file**
   - Injects user OAuth tokens into tool calls
   - Queries `oauth_tokens` table
   - Returns Google API service objects
   - Used by all Google Workspace tools

4. **Legacy files cause confusion**
   - Old OAuth routes not registered in Flask
   - File-based OAuth being phased out
   - Cleanup needed to reduce complexity

5. **Clear separation of concerns**
   - Backend OAuth: Flask routes + database storage
   - Frontend OAuth: Chrome extension (separate flow)
   - CLI OAuth: JWT token generator for testing

---

**See Also:**
- `OAUTH_SCRIPTS_GUIDE.md` - Complete documentation (50+ pages)
- `OAUTH_ARCHITECTURE_DIAGRAM.md` - Visual diagrams of OAuth flow
- `FIX_13_GOOGLE_WORKSPACE_OAUTH_DATABASE.md` - Fix #13 implementation

**Status:** OAuth architecture fully documented. Ready for cleanup and testing.
