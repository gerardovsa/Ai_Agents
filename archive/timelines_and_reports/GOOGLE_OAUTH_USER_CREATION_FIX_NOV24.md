# Google OAuth User Creation Fix - November 24, 2025

## Issues Fixed

### 1. Database Error: NULL ID on User Creation
**Error:**
```
null value in column "id" of relation "users" violates not-null constraint
DETAIL: Failing row contains (null, elex, elex@vetsuccessacademy.com, ...)
```

**Root Cause:**
- The `ai_infrastructure.users` table's `id` column had no default value or sequence
- PostgreSQL requires explicit ID or a sequence for auto-increment
- The code was using `cursor.lastrowid` which doesn't work with psycopg2

**Fix Applied:**
1. Created sequence: `ai_infrastructure.users_id_seq`
2. Set sequence as default for `id` column
3. Changed INSERT to use `RETURNING id` clause
4. Changed `cursor.lastrowid` to `cursor.fetchone()['id']`

**Migration Script:** `fix_users_id_autoincrement.py`

### 2. HTTP Header Error on OAuth Failure
**Error:**
```
ValueError: Header values must not contain newline characters.
```

**Root Cause:**
- PostgreSQL error messages contain newlines
- Flask redirect was putting the error message directly in URL
- HTTP headers cannot contain newlines

**Fix Applied:**
- Import `urllib.parse.quote`
- Remove newlines from error message: `str(e).replace('\n', ' ')`
- URL-encode the error message: `quote(error_msg)`

## Files Modified

### AI_infrastructure/routes/google_auth_routes_V2_FIXED.py
**Line 265-272** - Fixed user creation INSERT:
```python
# OLD:
cursor.execute('''
    INSERT INTO ai_infrastructure.users (username, email, password_hash, role) 
    VALUES (%s, %s, %s, %s)
''', (username, email, 'oauth_google', 'user'))
user_id = cursor.lastrowid

# NEW:
cursor.execute('''
    INSERT INTO ai_infrastructure.users (username, email, password_hash, role) 
    VALUES (%s, %s, %s, %s)
    RETURNING id
''', (username, email, 'oauth_google', 'user'))
user_id = cursor.fetchone()['id']
```

**Line 620-627** - Fixed error message handling:
```python
# OLD:
return redirect(f'{frontend_url}/?error=user_creation_failed&message={str(e)}')

# NEW:
from urllib.parse import quote
error_msg = quote(str(e).replace('\n', ' '))
return redirect(f'{frontend_url}/?error=user_creation_failed&message={error_msg}')
```

## Database Changes

### Sequence Created:
```sql
CREATE SEQUENCE ai_infrastructure.users_id_seq
START WITH 15
INCREMENT BY 1;

ALTER TABLE ai_infrastructure.users 
ALTER COLUMN id SET DEFAULT nextval('ai_infrastructure.users_id_seq'::regclass);

ALTER SEQUENCE ai_infrastructure.users_id_seq 
OWNED BY ai_infrastructure.users.id;
```

## Testing

### Local Tests Passed:
1. ✅ Sequence creation and association
2. ✅ Auto-increment ID generation
3. ✅ INSERT with RETURNING id
4. ✅ OAuth user creation flow

### Test Scripts Created:
- `check_users_table.py` - Check column definitions
- `check_users_full_schema.py` - Check full schema and sequences
- `fix_users_id_autoincrement.py` - Migration script
- `test_oauth_user_creation.py` - Test OAuth user creation

## Deployment Status

### Local:
- ✅ Database migration applied
- ✅ Code changes tested
- ✅ Flask server restarted

### Render (Production):
- ⏳ Code changes committed (ready to push)
- ⏳ Database migration needs to run on Render Supabase
- ⏳ Need to deploy v9 branch

## Next Steps

1. **Commit and Push:**
   ```bash
   git commit -m "Fix Google OAuth user creation - Add RETURNING id for PostgreSQL and URL-encode error messages"
   git push origin v9
   ```

2. **Run Migration on Render Supabase:**
   - Connect to Render's Supabase instance
   - Run `fix_users_id_autoincrement.py` against production database
   - OR manually execute the SQL commands

3. **Verify on Render:**
   - Wait for deployment
   - Test Google OAuth login
   - Verify new users can be created

## Impact

- **Users Affected:** All new Google OAuth users
- **Existing Users:** No impact (existing users already have IDs)
- **Downtime:** None (backward compatible)
- **Breaking Changes:** None

## Related Issues

- Similar check needed for Microsoft OAuth (no issues found)
- All other tables use proper sequences (checked)

## Notes

- PostgreSQL best practice: Use SERIAL or BIGSERIAL for auto-increment columns
- Always use `RETURNING id` with INSERT statements in PostgreSQL
- URL-encode all user-facing error messages in redirects
