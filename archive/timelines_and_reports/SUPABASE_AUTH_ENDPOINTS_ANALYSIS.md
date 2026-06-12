# Supabase Auth Endpoints Analysis

## `/api/auth/profile` Endpoint

**File:** `AI_infrastructure/routes/auth_routes.py` (lines 218-330)

### What It Does:
Returns complete user profile including:
- User basic info (from JWT token)
- Gmail accounts linked
- Workspace ID
- Authentication platform (google/microsoft/local)
- OAuth connection status for Google and Microsoft

### Supabase Tables Queried:

1. **`ai_infrastructure.users`** (line 241)
   ```sql
   SELECT password_hash 
   FROM ai_infrastructure.users 
   WHERE id = ?
   ```
   - Gets password_hash to determine auth platform
   - `oauth_google` → Google OAuth user
   - `oauth_microsoft` or `OAUTH_USER_NO_PASSWORD` → Microsoft OAuth user

2. **`ai_infrastructure.oauth_tokens`** (line 256)
   ```sql
   SELECT platform 
   FROM ai_infrastructure.oauth_tokens 
   WHERE user_id = ? AND is_active = ?
   ORDER BY created_at DESC LIMIT 1
   ```
   - Fallback to determine platform if password_hash is ambiguous

3. **`ai_infrastructure.oauth_tokens`** (line 283)
   ```sql
   SELECT COUNT(*) as count 
   FROM ai_infrastructure.oauth_tokens 
   WHERE user_id = ? 
   AND platform = 'google' 
   AND access_token IS NOT NULL
   AND (is_active = ? OR is_active IS NULL)
   AND (expires_at IS NULL OR expires_at > NOW())
   ```
   - Checks if user has **active Google OAuth tokens**
   - Returns `google_oauth_connected: true/false`

4. **`ai_infrastructure.oauth_tokens`** (line 301)
   ```sql
   SELECT COUNT(*) as count 
   FROM ai_infrastructure.oauth_tokens 
   WHERE user_id = ? 
   AND (platform = 'microsoft' OR platform = 'microsoft365')
   AND access_token IS NOT NULL
   AND (is_active = ? OR is_active IS NULL)
   AND (expires_at IS NULL OR expires_at > NOW())
   ```
   - Checks if user has **active Microsoft OAuth tokens**
   - Returns `microsoft_oauth_connected: true/false`

5. **Helper Calls:**
   - `user_auth_manager.get_user_gmail_accounts(user_id)` → Queries `ai_infrastructure.user_gmail_accounts`
   - `user_auth_manager.get_user_workspace(user_id)` → Queries `ai_infrastructure.workspaces`

### Response Example:
```json
{
  "success": true,
  "profile": {
    "user_id": 14,
    "email": "printing@inhouseprint.com.au",
    "username": "gerardo",
    "role": "admin",
    "id": 14,
    "gmail_accounts": [],
    "workspace_id": 1,
    "auth_platform": "google",
    "google_oauth_connected": true,
    "microsoft_oauth_connected": false
  }
}
```

---

## `/api/auth/verify` Endpoint

**File:** `AI_infrastructure/routes/auth_routes.py` (lines 135-149)

### What It Does:
Verifies JWT token validity and returns basic user info

### Supabase Tables Queried:
**NONE** - Only validates JWT token signature and expiration

The `@require_auth` decorator (from `user_auth.py`) does query Supabase:
- **`ai_infrastructure.users`** - Validates user_id from token exists in database

### Response Example:
```json
{
  "success": true,
  "user": {
    "user_id": 14,
    "email": "printing@inhouseprint.com.au",
    "username": "gerardo",
    "role": "admin"
  }
}
```

---

## Summary

| Endpoint | Tables Accessed | Purpose |
|----------|----------------|---------|
| `/api/auth/verify` | `ai_infrastructure.users` (via decorator) | Validate token and return basic user info |
| `/api/auth/profile` | `ai_infrastructure.users`<br>`ai_infrastructure.oauth_tokens` (3 queries)<br>`ai_infrastructure.user_gmail_accounts`<br>`ai_infrastructure.workspaces` | Complete profile with OAuth status |

### Current Errors (From Browser Console):

**401 Unauthorized on `/api/auth/profile`:**
```
GET https://ai-agents-backend-singapore.onrender.com/api/auth/profile 401
```

**Possible Causes:**
1. ✅ **FIXED** - Schema prefixes added (`ai_infrastructure.users`, etc.)
2. ⏳ **PENDING** - Render deployment completing
3. ⚠️ **TOKEN MISMATCH** - User's JWT token signed with old SECRET_KEY
   - Solution: Clear `localStorage.clear()` and re-login

**500 Internal Server Error on `/api/prompts/library/db`:**
```
GET https://ai-agents-backend-singapore.onrender.com/api/prompts/library/db?user_id=1 500
```
- Caused by missing schema prefix on `prompt_library` table
- ✅ **FIXED** - Schema prefix added in commit `805e446`

**500 Internal Server Error on `/api/threads/list`:**
```
GET https://ai-agents-backend-singapore.onrender.com/api/threads/list?user_id=12 500
Error: 'relation "threads" does not exist'
Error: 'column t.workflow_slug does not exist'
```
- Caused by missing schema prefix `sessions.threads`
- ✅ **FIXED** - Schema prefix added in commit `805e446`

---

## Next Steps:

1. **Wait for Render deployment** (commit `f84535b`) - should be live in 2-3 minutes
2. **Clear browser localStorage**:
   ```javascript
   localStorage.clear();
   location.reload();
   ```
3. **Re-login via Google OAuth** to get new JWT token signed with correct SECRET_KEY
4. All errors should be resolved ✅
