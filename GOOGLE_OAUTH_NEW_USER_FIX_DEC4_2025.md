# Google OAuth New User Login Fix - December 4, 2025

## Problem
New Google users could successfully authenticate with Google OAuth but would get redirected to `/?error=oauth_failed` instead of logging in.

### Error in Logs
```
[GOOGLE OAUTH] Unexpected error: cannot access local variable 'bool_true' where it is not associated with a value
UnboundLocalError: cannot access local variable 'bool_true' where it is not associated with a value
```

### Root Cause
The variable `bool_true` was only defined inside the `if existing:` block (for updating existing tokens) but was also needed in the `else:` block (for inserting new tokens). When a new user logged in, the INSERT code path tried to use an undefined variable.

**File**: `AI_infrastructure/routes/google_auth_routes_V2_FIXED.py`  
**Line**: 722

```python
# BEFORE (BROKEN):
if existing:
    # UPDATE existing token
    print(f'   Updating existing token for user {user_id}')
    
    # PostgreSQL needs TRUE/FALSE for boolean columns
    from shared.database_utils import is_using_supabase
    bool_true = True if is_using_supabase() else 1  # ← Only defined here
    
    # ... UPDATE query ...
else:
    # INSERT new token
    cursor.execute('''INSERT INTO ... VALUES (%s, ..., %s)''', (
        user_id,
        # ... more params ...
        bool_true,  # ❌ UnboundLocalError: not defined in this scope!
```

## Solution
Moved the `bool_true` variable definition **before** the conditional block so it's available in both UPDATE and INSERT code paths.

```python
# AFTER (FIXED):
# PostgreSQL needs TRUE/FALSE for boolean columns (define BEFORE conditional)
from shared.database_utils import is_using_supabase
bool_true = True if is_using_supabase() else 1  # ✅ Defined once, used everywhere

# Check if token exists for this user+platform
cursor.execute('SELECT id FROM ai_infrastructure.oauth_tokens WHERE user_id = %s AND platform = %s', (user_id, 'google'))
existing = cursor.fetchone()

if existing:
    # UPDATE existing token - bool_true available ✅
    # ...
else:
    # INSERT new token - bool_true available ✅
    # ...
```

## Impact
- **Existing Users**: No change (update path was already working)
- **New Users**: Can now successfully complete OAuth flow and create accounts
- **Database Compatibility**: Maintains PostgreSQL (TRUE) and SQLite (1) compatibility

## Testing Scenario
1. User clicks "Sign in with Google"
2. Google authentication succeeds
3. User does NOT exist in `ai_infrastructure.users` table
4. System creates new user with `create_user()`
5. System attempts to insert OAuth tokens
6. **Before Fix**: UnboundLocalError, redirect to `/?error=oauth_failed`
7. **After Fix**: Tokens inserted successfully, user logged in ✅

## Related Code
- **OAuth Callback**: `google_callback()` function
- **Token Storage**: Lines 640-750 in `google_auth_routes_V2_FIXED.py`
- **User Creation**: `create_user()` function (lines 780-830)

## Files Modified
- `AI_infrastructure/routes/google_auth_routes_V2_FIXED.py` (1 line moved)

## Commit Message
```
FIX: Google OAuth new user login (UnboundLocalError)

Problem:
- New Google users could authenticate but got redirected with error
- UnboundLocalError: bool_true not defined in INSERT token path
- Variable only defined inside UPDATE conditional block

Solution:
- Moved bool_true definition before if/else conditional
- Now available in both UPDATE and INSERT code paths
- Maintains PostgreSQL (TRUE) and SQLite (1) compatibility

Impact:
- Existing users: No change (update path unaffected)
- New users: Can now complete OAuth flow successfully
- Single line moved, zero logic changes

Tested: New user login flow working (user 20 created successfully)
```

## Log Evidence (Fixed)
```
[GOOGLE OAUTH] User profile fetched:
   Email: itsupport@vetsuccessacademy.com
   Name: Gerardo Poli
   Google ID: 112678243768296252667
Created new user: itsupport (ID: 20) with active=TRUE, permissions=user
[GOOGLE OAUTH] New user created: itsupport (ID: 20)
[GOOGLE OAUTH] Storing tokens in oauth_tokens table...
   Creating new token for user 20
✅ [GOOGLE OAUTH] Tokens stored successfully (NEW USER PATH WORKS!)
```

## Prevention
This type of error can be prevented by:
1. Defining shared variables **before** conditional blocks
2. Using linters that detect undefined variable usage
3. Testing both code paths (UPDATE and INSERT) during development
4. Adding integration tests for new user registration flow

---

**Status**: ✅ Fixed  
**Date**: December 4, 2025  
**Severity**: High (blocked all new user signups)  
**Fix Complexity**: Trivial (1 line moved)
