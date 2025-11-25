# Schema Prefix Fix for Users Table

## Problem
Multiple `users` tables exist in Supabase across different schemas:
- `ai_infrastructure.users` (app users) - HAS permissions column ✅
- `auth.users` (Supabase auth) - NO permissions column ❌  
- `sessions.users` (session data) - NO permissions column ❌

When queries don't specify schema (`FROM users`), PostgreSQL uses `search_path` to resolve which table to query. On **Render deployment**, the search_path might include `auth` schema, causing queries to hit `auth.users` instead of `ai_infrastructure.users`.

**Error seen:**
```
column "permissions" does not exist
LINE 3: role, permissions, allowed_tools, allowed...
```

## Solution
Explicitly qualify all `users` table references with `ai_infrastructure.` schema prefix.

## Files to Fix

### High Priority (Causes Excel/OneDrive errors)
1. ✅ **FIXED** - `AI_infrastructure/auth/permission_checker.py` line 110
   - `FROM users WHERE` → `FROM ai_infrastructure.users WHERE`

### Medium Priority (User authentication/management)
2. `AI_infrastructure/auth/user_auth.py` - Multiple lines
   - Lines 361, 524, 1782, 1837
   - `INSERT INTO users` → `INSERT INTO ai_infrastructure.users`
   - `UPDATE users SET` → `UPDATE ai_infrastructure.users SET`
   - `FROM users WHERE` → `FROM ai_infrastructure.users WHERE`

3. `AI_infrastructure/database_toolkit/user_manager.py` - Multiple lines
   - Lines 50, 82, 84, 86, 124, 126, 245
   - All user table operations

### Low Priority (Examples/tests/utilities)
4. `AI_infrastructure/workspace/workspace_manager.py` - Lines 153, 517
5. `AI_infrastructure/utils/email_alias_helpers.py` - Lines 48, 107, 113, 179
6. `AI_infrastructure/utils/database_helpers.py` - Lines 170, 222

### Not Critical (Examples in comments/docs)
- `shared/database_utils.py` - Examples in docstrings (lines 593-618)
- `shared/db_connection_wrapper.py` - Examples (lines 10, 36)

## Testing After Fix
```bash
python scripts/testing/test_microsoft_auto_refresh.py
# Should work without "column permissions does not exist" error
```

## Deployment
After fixing:
1. Commit changes
2. Push to GitHub (branch v9)
3. Deploy to Render (will pull latest code)
4. Test Microsoft Excel/OneDrive tools - should work!

## Alternative Fix (Not Recommended)
Could modify `search_path` on Render:
```sql
ALTER ROLE your_role SET search_path = ai_infrastructure, public, auth;
```
But explicit schema prefixes are more reliable and portable.
