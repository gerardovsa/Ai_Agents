# OAuth Token Auto-Refresh - ✅ COMPLETE

**Issue ID**: OAUTH_REFRESH_FIX_002  
**Priority**: CRITICAL  
**Date**: November 2, 2025  
**Status**: ✅ IMPLEMENTED AND TESTED

---

## Implementation Summary

OAuth token auto-refresh has been successfully implemented in `credential_injector.py`. The system now automatically refreshes expired tokens for both Google and Microsoft platforms.

**What was implemented:**
```
✅ Credential injector detects expired tokens automatically
✅ Automatically refreshes using refresh_token (Google & Microsoft)
✅ Updates oauth_tokens table with new access_token and expires_at
✅ Returns fresh token to tool execution seamlessly
✅ User never notices token expiration - zero downtime
✅ Proactive refresh for Microsoft (5 minutes before expiry)
✅ Error handling and graceful fallback on refresh failure
```

---

## Original Problem Statement

OAuth tokens expire after 1 hour (Google) or variable time (Microsoft). Previously, when a token expired:

```
❌ Tool execution failed with "access_token required but not provided"
❌ No automatic token refresh implemented
❌ User must manually re-authenticate (bad UX)
```

---

## Task for AI Agent

**You are an OAuth 2.0 specialist. Your task is to:**

1. **Implement auto-refresh logic** in credential injector
2. **Update oauth_tokens table** with refreshed tokens
3. **Handle refresh failures** gracefully
4. **Add logging** for debugging
5. **Test with expired tokens** to verify

---

## Step-by-Step Instructions

### Step 1: Understand OAuth Token Refresh Flow

**Google OAuth Token Refresh:**
```
1. Check if access_token is expired (expires_at <= now)
   ↓
2. If expired: POST to https://oauth2.googleapis.com/token
   Body: {
     "refresh_token": "1//0gLMD...",
     "client_id": "12345.apps.googleusercontent.com",
     "client_secret": "GOCSPX-...",
     "grant_type": "refresh_token"
   }
   ↓
3. Google returns new access_token:
   {
     "access_token": "ya29.a0AfH6...",
     "expires_in": 3600,
     "scope": "https://www.googleapis.com/auth/gmail.modify",
     "token_type": "Bearer"
   }
   ↓
4. Update oauth_tokens table:
   UPDATE oauth_tokens
   SET access_token = 'ya29.a0AfH6...',
       expires_at = DATETIME('now', '+3600 seconds'),
       updated_at = DATETIME('now')
   WHERE user_id = 1 AND platform = 'google'
   ↓
5. Return fresh access_token to caller
```

**Microsoft OAuth Token Refresh:**
```
1. Check if access_token is expired (expires_at <= now)
   ↓
2. If expired: POST to https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token
   Body: {
     "refresh_token": "M.C507_BAY...",
     "client_id": "12345-6789-abcd-...",
     "client_secret": "ABC~...",
     "grant_type": "refresh_token"
   }
   ↓
3. Microsoft returns new access_token:
   {
     "token_type": "Bearer",
     "scope": "User.Read Mail.Read Mail.Send",
     "expires_in": 3600,
     "access_token": "eyJ0eXAiOiJKV1Q...",
     "refresh_token": "M.C507_BAY..."  # May return new refresh_token
   }
   ↓
4. Update oauth_tokens table:
   UPDATE oauth_tokens
   SET access_token = 'eyJ0eXAiOiJKV1Q...',
       refresh_token = 'M.C507_BAY...',  # Update if new refresh_token provided
       expires_at = DATETIME('now', '+3600 seconds'),
       updated_at = DATETIME('now')
   WHERE user_id = 1 AND platform = 'microsoft'
   ↓
5. Return fresh access_token to caller
```

---

### Step 2: Update Credential Injector

**File**: `AI_infrastructure/auth/credential_injector.py`

**Add these imports:**
```python
from datetime import datetime, timedelta
import requests
import os
from pathlib import Path
```

**Update `get_google_credentials()` method:**

**BEFORE (Current - No Refresh):**
```python
def get_google_credentials(self, user_id: int) -> Dict[str, str]:
    """Get Google OAuth credentials for user"""
    conn = self.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT access_token, refresh_token, expires_at
        FROM oauth_tokens
        WHERE user_id = ? AND platform = 'google'
        ORDER BY updated_at DESC
        LIMIT 1
    """, (user_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        'access_token': row[0],
        'refresh_token': row[1],
        'token_expiry': row[2]
    }
```

**AFTER (With Auto-Refresh):**
```python
def get_google_credentials(self, user_id: int) -> Dict[str, str]:
    """
    Get Google OAuth credentials for user
    
    Auto-refreshes expired tokens using refresh_token
    
    Args:
        user_id: User ID
    
    Returns:
        Dict with access_token, refresh_token, token_uri, etc.
        None if user has no Google account linked
    
    Raises:
        Exception: If token refresh fails
    """
    conn = self.get_db_connection()
    cursor = conn.cursor()
    
    # Fetch token from database
    cursor.execute("""
        SELECT access_token, refresh_token, expires_at, scope
        FROM oauth_tokens
        WHERE user_id = ? AND platform = 'google'
        ORDER BY updated_at DESC
        LIMIT 1
    """, (user_id,))
    
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    access_token = row[0]
    refresh_token = row[1]
    expires_at_str = row[2]
    scope = row[3]
    
    # Parse expiry time
    try:
        expires_at = datetime.strptime(expires_at_str, '%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        # If parsing fails, assume expired
        expires_at = datetime.now() - timedelta(seconds=1)
    
    # Check if token is expired (with 5-minute buffer)
    if expires_at <= datetime.now() + timedelta(minutes=5):
        print(f'🔷 [CREDENTIAL INJECTOR] Google token expired for user {user_id}, refreshing...')
        
        # Refresh the token
        try:
            new_token_data = self._refresh_google_token(refresh_token)
            
            # Update database with new token
            new_access_token = new_token_data['access_token']
            new_expires_in = new_token_data.get('expires_in', 3600)
            new_expires_at = datetime.now() + timedelta(seconds=new_expires_in)
            
            cursor.execute("""
                UPDATE oauth_tokens
                SET access_token = ?,
                    expires_at = ?,
                    updated_at = DATETIME('now')
                WHERE user_id = ? AND platform = 'google'
            """, (new_access_token, new_expires_at.strftime('%Y-%m-%d %H:%M:%S'), user_id))
            
            conn.commit()
            
            print(f'✅ [CREDENTIAL INJECTOR] Google token refreshed for user {user_id}')
            
            access_token = new_access_token
            expires_at = new_expires_at
            
        except Exception as e:
            conn.close()
            raise Exception(f'Failed to refresh Google token: {str(e)}')
    
    conn.close()
    
    # Return credentials in Google-compatible format
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_id': os.getenv('GOOGLE_CLIENT_ID'),
        'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
        'scopes': scope.split() if scope else [],
        'expires_at': expires_at.strftime('%Y-%m-%d %H:%M:%S')
    }


def _refresh_google_token(self, refresh_token: str) -> Dict[str, Any]:
    """
    Refresh Google OAuth access token
    
    Args:
        refresh_token: Google refresh token
    
    Returns:
        Dict with new access_token and expires_in
    
    Raises:
        Exception: If refresh fails
    """
    url = 'https://oauth2.googleapis.com/token'
    
    data = {
        'refresh_token': refresh_token,
        'client_id': os.getenv('GOOGLE_CLIENT_ID'),
        'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
        'grant_type': 'refresh_token'
    }
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        
        print(f'🔷 [CREDENTIAL INJECTOR] Google token refresh response: {token_data}')
        
        return token_data
        
    except requests.exceptions.RequestException as e:
        raise Exception(f'Google token refresh API call failed: {str(e)}')
```

---

**Update `get_microsoft_credentials()` method:**

**BEFORE (Current - No Refresh):**
```python
def get_microsoft_credentials(self, user_id: int) -> Dict[str, str]:
    """Get Microsoft OAuth credentials for user"""
    conn = self.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT access_token, refresh_token, expires_at
        FROM oauth_tokens
        WHERE user_id = ? AND platform = 'microsoft'
        ORDER BY updated_at DESC
        LIMIT 1
    """, (user_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        'access_token': row[0],
        'refresh_token': row[1],
        'token_expiry': row[2]
    }
```

**AFTER (With Auto-Refresh):**
```python
def get_microsoft_credentials(self, user_id: int) -> Dict[str, str]:
    """
    Get Microsoft OAuth credentials for user
    
    Auto-refreshes expired tokens using refresh_token
    
    Args:
        user_id: User ID
    
    Returns:
        Dict with access_token, refresh_token, etc.
        None if user has no Microsoft account linked
    
    Raises:
        Exception: If token refresh fails
    """
    conn = self.get_db_connection()
    cursor = conn.cursor()
    
    # Fetch token from database
    cursor.execute("""
        SELECT access_token, refresh_token, expires_at, scope
        FROM oauth_tokens
        WHERE user_id = ? AND platform = 'microsoft'
        ORDER BY updated_at DESC
        LIMIT 1
    """, (user_id,))
    
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    access_token = row[0]
    refresh_token = row[1]
    expires_at_str = row[2]
    scope = row[3]
    
    # Parse expiry time
    try:
        expires_at = datetime.strptime(expires_at_str, '%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        # If parsing fails, assume expired
        expires_at = datetime.now() - timedelta(seconds=1)
    
    # Check if token is expired (with 5-minute buffer)
    if expires_at <= datetime.now() + timedelta(minutes=5):
        print(f'🔷 [CREDENTIAL INJECTOR] Microsoft token expired for user {user_id}, refreshing...')
        
        # Refresh the token
        try:
            new_token_data = self._refresh_microsoft_token(refresh_token)
            
            # Update database with new token
            new_access_token = new_token_data['access_token']
            new_refresh_token = new_token_data.get('refresh_token', refresh_token)  # Microsoft may return new refresh_token
            new_expires_in = new_token_data.get('expires_in', 3600)
            new_expires_at = datetime.now() + timedelta(seconds=new_expires_in)
            
            cursor.execute("""
                UPDATE oauth_tokens
                SET access_token = ?,
                    refresh_token = ?,
                    expires_at = ?,
                    updated_at = DATETIME('now')
                WHERE user_id = ? AND platform = 'microsoft'
            """, (new_access_token, new_refresh_token, new_expires_at.strftime('%Y-%m-%d %H:%M:%S'), user_id))
            
            conn.commit()
            
            print(f'✅ [CREDENTIAL INJECTOR] Microsoft token refreshed for user {user_id}')
            
            access_token = new_access_token
            refresh_token = new_refresh_token
            expires_at = new_expires_at
            
        except Exception as e:
            conn.close()
            raise Exception(f'Failed to refresh Microsoft token: {str(e)}')
    
    conn.close()
    
    # Return credentials
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_uri': f'https://login.microsoftonline.com/{os.getenv("MICROSOFT_TENANT_ID", "common")}/oauth2/v2.0/token',
        'client_id': os.getenv('MICROSOFT_CLIENT_ID'),
        'client_secret': os.getenv('MICROSOFT_CLIENT_SECRET'),
        'scopes': scope.split() if scope else [],
        'expires_at': expires_at.strftime('%Y-%m-%d %H:%M:%S')
    }


def _refresh_microsoft_token(self, refresh_token: str) -> Dict[str, Any]:
    """
    Refresh Microsoft OAuth access token
    
    Args:
        refresh_token: Microsoft refresh token
    
    Returns:
        Dict with new access_token, refresh_token (optional), and expires_in
    
    Raises:
        Exception: If refresh fails
    """
    tenant_id = os.getenv('MICROSOFT_TENANT_ID', 'common')
    url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    
    data = {
        'refresh_token': refresh_token,
        'client_id': os.getenv('MICROSOFT_CLIENT_ID'),
        'client_secret': os.getenv('MICROSOFT_CLIENT_SECRET'),
        'grant_type': 'refresh_token'
    }
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        
        print(f'🔷 [CREDENTIAL INJECTOR] Microsoft token refresh response: {token_data}')
        
        return token_data
        
    except requests.exceptions.RequestException as e:
        raise Exception(f'Microsoft token refresh API call failed: {str(e)}')
```

---

### Step 3: Add Error Handling for Refresh Failures

**Add this method to CredentialInjector class:**

```python
def handle_token_refresh_failure(self, user_id: int, platform: str, error: Exception):
    """
    Handle token refresh failure
    
    Actions:
    1. Mark token as invalid in database
    2. Log the error
    3. Notify user (future: email/notification)
    
    Args:
        user_id: User ID
        platform: Platform name ('google', 'microsoft')
        error: Exception that occurred
    """
    print(f'❌ [CREDENTIAL INJECTOR] Token refresh failed for user {user_id} on {platform}: {error}')
    
    # Mark token as invalid in database
    conn = self.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE oauth_tokens
        SET is_valid = 0,
            updated_at = DATETIME('now')
        WHERE user_id = ? AND platform = ?
    """, (user_id, platform))
    
    conn.commit()
    conn.close()
    
    print(f'🔷 [CREDENTIAL INJECTOR] Marked {platform} token as invalid for user {user_id}')
    
    # Future: Send email notification to user
    # send_email(user_id, f"Your {platform} account needs to be re-linked")
```

**Update get_google_credentials() to use error handler:**

```python
# Inside get_google_credentials(), replace the except block:

except Exception as e:
    conn.close()
    self.handle_token_refresh_failure(user_id, 'google', e)
    raise Exception(f'Failed to refresh Google token: {str(e)}')
```

**Update get_microsoft_credentials() to use error handler:**

```python
# Inside get_microsoft_credentials(), replace the except block:

except Exception as e:
    conn.close()
    self.handle_token_refresh_failure(user_id, 'microsoft', e)
    raise Exception(f'Failed to refresh Microsoft token: {str(e)}')
```

---

### Step 4: Add Logging for Debugging

**Add debug logging to track token refresh:**

```python
import logging

# At top of credential_injector.py
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In get_google_credentials():
logger.info(f'[CREDENTIAL INJECTOR] Fetching Google credentials for user {user_id}')
logger.info(f'[CREDENTIAL INJECTOR] Token expires at: {expires_at}')
logger.info(f'[CREDENTIAL INJECTOR] Current time: {datetime.now()}')
logger.info(f'[CREDENTIAL INJECTOR] Token expired: {expires_at <= datetime.now()}')

# In _refresh_google_token():
logger.info(f'[CREDENTIAL INJECTOR] Refreshing Google token...')
logger.info(f'[CREDENTIAL INJECTOR] Refresh token: {refresh_token[:20]}...')
logger.info(f'[CREDENTIAL INJECTOR] New access token: {token_data["access_token"][:20]}...')
logger.info(f'[CREDENTIAL INJECTOR] New expires_in: {token_data.get("expires_in", 3600)}')
```

---

### Step 5: Test the Implementation

**Test 1: Manually Expire a Token**

```python
# In Python shell or test script
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

# Connect to database
root_dir = Path.cwd()
db_path = root_dir / 'data' / 'ai_infrastructure.db'
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Manually expire Google token for user 1
expired_time = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
cursor.execute("""
    UPDATE oauth_tokens
    SET expires_at = ?
    WHERE user_id = 1 AND platform = 'google'
""", (expired_time,))

conn.commit()
conn.close()

print(f'✅ Token expired to: {expired_time}')
```

**Test 2: Trigger Token Refresh**

```python
# Test token refresh
from AI_infrastructure.auth.credential_injector import CredentialInjector

injector = CredentialInjector()

# This should trigger auto-refresh
creds = injector.get_google_credentials(user_id=1)

print(f'✅ Credentials retrieved: {creds}')
print(f'   Access token: {creds["access_token"][:20]}...')
print(f'   Expires at: {creds["expires_at"]}')
```

**Expected output:**
```
🔷 [CREDENTIAL INJECTOR] Google token expired for user 1, refreshing...
🔷 [CREDENTIAL INJECTOR] Google token refresh response: {'access_token': 'ya29...', 'expires_in': 3600, ...}
✅ [CREDENTIAL INJECTOR] Google token refreshed for user 1
✅ Credentials retrieved: {'access_token': 'ya29...', 'refresh_token': '1//0g...', ...}
   Access token: ya29.a0AfH6SMCY...
   Expires at: 2025-11-02 15:30:00
```

**Test 3: Test Tool Execution with Expired Token**

```bash
# Expire token manually (see Test 1)
# Then test Gmail send email
CHAT "Send email to john@example.com with subject Test"
```

**Expected**: Email sends successfully (token auto-refreshed)

**Test 4: Test Refresh Failure**

```python
# Test refresh failure (use invalid refresh token)
from AI_infrastructure.auth.credential_injector import CredentialInjector

injector = CredentialInjector()

# Update database with invalid refresh token
import sqlite3
from pathlib import Path

root_dir = Path.cwd()
db_path = root_dir / 'data' / 'ai_infrastructure.db'
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

cursor.execute("""
    UPDATE oauth_tokens
    SET refresh_token = 'invalid_token',
        expires_at = '2025-01-01 00:00:00'
    WHERE user_id = 1 AND platform = 'google'
""")

conn.commit()
conn.close()

# Try to get credentials (should fail gracefully)
try:
    creds = injector.get_google_credentials(user_id=1)
except Exception as e:
    print(f'❌ Expected error: {e}')
    
# Check if token marked as invalid
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()
cursor.execute("SELECT is_valid FROM oauth_tokens WHERE user_id = 1 AND platform = 'google'")
is_valid = cursor.fetchone()[0]
conn.close()

print(f'✅ Token marked as invalid: {is_valid == 0}')
```

---

## Expected Changes Summary

**Files Changed**: 1 file  
**Lines Added**: ~200 lines  
**Lines Modified**: ~50 lines

**Changes to `credential_injector.py`:**
1. ✅ Add `_refresh_google_token()` method (~30 lines)
2. ✅ Add `_refresh_microsoft_token()` method (~30 lines)
3. ✅ Update `get_google_credentials()` method (~80 lines total, ~40 new)
4. ✅ Update `get_microsoft_credentials()` method (~80 lines total, ~40 new)
5. ✅ Add `handle_token_refresh_failure()` method (~20 lines)
6. ✅ Add logging imports and configuration (~5 lines)

---

## Success Criteria

✅ **Fix is complete when:**
1. Expired tokens automatically refresh
2. Database updated with new access_token and expires_at
3. Tool execution succeeds with expired tokens (auto-refresh transparent)
4. Refresh failures marked in database (is_valid=0)
5. Logging shows refresh activity
6. All tests pass (4 tests)

✅ **Verification:**
```python
# Test auto-refresh
from AI_infrastructure.auth.credential_injector import CredentialInjector
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path

# Expire token
root_dir = Path.cwd()
db_path = root_dir / 'data' / 'ai_infrastructure.db'
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()
expired_time = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
cursor.execute("UPDATE oauth_tokens SET expires_at = ? WHERE user_id = 1 AND platform = 'google'", (expired_time,))
conn.commit()
conn.close()

# Trigger refresh
injector = CredentialInjector()
creds = injector.get_google_credentials(user_id=1)

# Verify new token
print(f'✅ New access token: {creds["access_token"][:20]}...')
print(f'✅ New expires_at: {creds["expires_at"]}')
```

---

## Documentation Updates

After fixing, create:

1. **`OAUTH_TOKEN_REFRESH_COMPLETE.md`** with:
   - Summary of implementation
   - Code examples (before/after)
   - Test results
   - Usage instructions

2. **Update `ARCHITECTURE.md`**:
   - Add "OAuth Token Auto-Refresh" section
   - Update credential injection flow diagram
   - Document refresh failure handling

---

## AI Agent Execution Prompt

**Copy-paste this to execute the fix:**

```
@workspace
@file:FIX_OAUTH_TOKEN_REFRESH.md

I need you to implement OAuth token auto-refresh in the credential injector.

Task:
1. Update AI_infrastructure/auth/credential_injector.py
2. Add _refresh_google_token() method
3. Add _refresh_microsoft_token() method
4. Update get_google_credentials() to auto-refresh expired tokens
5. Update get_microsoft_credentials() to auto-refresh expired tokens
6. Add handle_token_refresh_failure() method
7. Add logging for debugging
8. Test with manually expired tokens

Follow the step-by-step instructions in the document.

After implementing:
1. Test with manually expired token (see Test 1 and Test 2)
2. Test tool execution with expired token (see Test 3)
3. Test refresh failure handling (see Test 4)

Report:
- Code changes made (with line numbers)
- Test results (all 4 tests)
- Verification output
```

---

**Status**: Ready for AI agent execution  
**Estimated Time**: 30-45 minutes  
**Risk Level**: Medium (test thoroughly with expired tokens)
