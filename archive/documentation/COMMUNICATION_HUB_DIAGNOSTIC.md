# Communication Hub Connection Diagnostic Report

**Date:** November 10, 2025  
**Issue:** Communication Hub not connecting to Gmail/Outlook - no emails showing  
**Status:** 🔴 CRITICAL - Multiple authentication issues found

---

## 🔍 ROOT CAUSE ANALYSIS

### Issue #1: WRONG AUTHENTICATION SYSTEM ❌

**File:** `AI_infrastructure/routes/communication_routes.py`  
**Line 44:** Uses `UserAuthManager` instead of credential injection pattern

```python
# CURRENT (WRONG):
from auth.user_auth import UserAuthManager
auth_manager = UserAuthManager()

# Line 90:
google_creds = auth_manager.get_user_google_oauth_credentials(user_id)
```

**Problem:** This checks `oauth_tokens` table but uses WRONG method that expects different structure.

**What it should be:**
```python
# CORRECT:
# Use the credential injection pattern like all other routes
# Pass _user_id and _injected_credentials=True to tool functions
```

---

### Issue #2: DATA LOCATION ✅ CONFIRMED

From `database_analysis_report.txt`:

**Database:** `C:\Users\gpoli\GIT\AI_agents\data\ai_infrastructure.db`

**Table: oauth_tokens** (5 rows exist!)
```
Columns:
- id (INTEGER PK)
- user_id (INTEGER NOT NULL)  
- platform (TEXT NOT NULL) → 'google' or 'microsoft'
- access_token (TEXT NOT NULL)
- refresh_token (TEXT)
- token_type (TEXT)
- expires_at (TIMESTAMP)
- scope (TEXT)
- email (TEXT)
- ...25 more columns
```

**YOU HAVE 5 OAUTH TOKENS IN DATABASE!** ✅

---

### Issue #3: GMAIL TOOL EXPECTS CREDENTIAL INJECTION

From `google_workspace/gmail.py` lines 32-100:

```python
def _get_gmail_service(_user_id=None, _injected_credentials=None, **kwargs):
    """Get authenticated Gmail API service"""
    
    # ✅ NEW: If user_id provided, use database credentials
    if _user_id and _injected_credentials:
        print(f"🔑 Using database credentials for user {_user_id}")
        
        # Get credentials from database via UserAuthManager
        auth_manager = UserAuthManager()
        cred_dict = auth_manager.get_user_google_oauth_credentials(_user_id)
        
        # Build Gmail service with OAuth tokens
        credentials = Credentials(
            token=cred_dict['access_token'],
            refresh_token=cred_dict.get('refresh_token'),
            ...
        )
        return build('gmail', 'v1', credentials=credentials)
```

**The Gmail wrapper ALREADY supports credential injection!**

---

## 🛠️ THE FIX - COMPLETE SOLUTION

### Step 1: Check What OAuth Tokens You Have

Run this diagnostic:

```powershell
cd C:\Users\gpoli\GIT\AI_agents
python -c "import sqlite3; conn = sqlite3.connect('data/ai_infrastructure.db'); cursor = conn.cursor(); cursor.execute('SELECT user_id, platform, email, account_identifier, is_active FROM oauth_tokens'); rows = cursor.fetchall(); print('OAuth Tokens in Database:'); [print(f'  User {r[0]}: {r[1]} - {r[2] or r[3]} (active={r[4]})') for r in rows]; conn.close()"
```

**Expected output:**
```
OAuth Tokens in Database:
  User 1: google - your.email@gmail.com (active=1)
  User 1: microsoft - your.email@outlook.com (active=1)
```

---

### Step 2: Fix Communication Routes (COMPLETE REWRITE)

Replace `AI_infrastructure/routes/communication_routes.py` with this corrected version:

```python
"""
FILE: AI_infrastructure/routes/communication_routes.py
PURPOSE: Communication Hub backend routes - Unified API for Gmail and Outlook

FIXED: Now uses proper credential injection pattern (matches agent_routes_v4.py)
LAST MODIFIED: 2025-11-10 - Fixed authentication to use credential injection
"""

from flask import Blueprint, request, jsonify
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import Gmail and Outlook tools (they handle credential injection internally)
from google_workspace.gmail import (
    gmail_list_messages, 
    gmail_get_message, 
    gmail_send_email,
    gmail_mark_as_read,
    gmail_delete_message,
    gmail_search_messages
)

# Microsoft Outlook imports
try:
    from tools.implementations.microsoft_outlook_tools import (
        microsoft_outlook_list_messages,
        microsoft_outlook_get_message,
        microsoft_outlook_send_email
    )
    OUTLOOK_AVAILABLE = True
except ImportError:
    print("[Communication Hub] ⚠️ Microsoft Outlook tools not available")
    OUTLOOK_AVAILABLE = False

# Create Blueprint
communication_bp = Blueprint('communication', __name__, url_prefix='/api/communication-hub')


@communication_bp.route('/accounts', methods=['GET'])
def get_accounts():
    """
    Get all connected email accounts for user
    Checks oauth_tokens table for active credentials
    """
    user_id = request.args.get('user_id', 1, type=int)
    
    print(f"[Communication Hub] 🔍 Checking accounts for user_id={user_id}")
    
    accounts = []
    
    # Check oauth_tokens table directly
    import sqlite3
    db_path = Path(__file__).parent.parent.parent / 'data' / 'ai_infrastructure.db'
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all active OAuth tokens for this user
        cursor.execute("""
            SELECT platform, email, account_identifier, access_token
            FROM oauth_tokens
            WHERE user_id = ? AND (is_active = 1 OR is_active IS NULL)
        """, (user_id,))
        
        tokens = cursor.fetchall()
        conn.close()
        
        print(f"[Communication Hub] Found {len(tokens)} OAuth token(s) in database")
        
        for token in tokens:
            platform = token['platform']
            email = token['email'] or token['account_identifier'] or f'{platform} Account'
            has_token = len(token['access_token'] or '') > 0
            
            print(f"[Communication Hub]   - {platform}: {email} (has_token={has_token})")
            
            if platform == 'google' and has_token:
                accounts.append({
                    'id': 'gmail',
                    'provider': 'gmail',
                    'email': email,
                    'display_name': f'Gmail ({email})',
                    'has_oauth': True
                })
            elif platform == 'microsoft' and has_token and OUTLOOK_AVAILABLE:
                accounts.append({
                    'id': 'outlook',
                    'provider': 'outlook',
                    'email': email,
                    'display_name': f'Outlook ({email})',
                    'has_oauth': True
                })
        
        print(f"[Communication Hub] ✅ Returning {len(accounts)} account(s)")
        
    except Exception as e:
        print(f"[Communication Hub] ❌ Database error: {e}")
        import traceback
        traceback.print_exc()
    
    return jsonify({
        'success': True,
        'accounts': accounts
    })


@communication_bp.route('/emails', methods=['GET'])
def list_emails():
    """
    List emails from selected account(s)
    Uses credential injection pattern (_user_id + _injected_credentials)
    """
    user_id = request.args.get('user_id', 1, type=int)
    account = request.args.get('account', 'all')
    limit = int(request.args.get('limit', 50))
    
    print(f"[Communication Hub] 📧 Listing emails: user_id={user_id}, account={account}, limit={limit}")
    
    emails = []
    
    # ✅ Gmail with credential injection
    if account in ['all', 'gmail']:
        try:
            print(f"[Communication Hub] Calling gmail_list_messages...")
            gmail_result = gmail_list_messages(
                max_results=limit,
                _user_id=user_id,
                _injected_credentials=True
            )
            
            print(f"[Communication Hub] Gmail result: {gmail_result.get('success')}")
            
            if gmail_result.get('success'):
                messages = gmail_result.get('messages', [])
                print(f"[Communication Hub] ✅ Got {len(messages)} Gmail messages")
                for msg in messages:
                    emails.append({
                        'id': f"gmail_{msg['id']}",
                        'provider': 'gmail',
                        'from': msg.get('from', 'Unknown'),
                        'to': msg.get('to', ''),
                        'subject': msg.get('subject', 'No Subject'),
                        'date': msg.get('date', ''),
                        'is_read': 'UNREAD' not in msg.get('labelIds', []),
                        'snippet': msg.get('snippet', ''),
                        'body_text': msg.get('body', ''),
                        'body_html': msg.get('body_html', '')
                    })
            else:
                error = gmail_result.get('error', 'Unknown error')
                print(f"[Communication Hub] ❌ Gmail failed: {error}")
        except Exception as e:
            print(f"[Communication Hub] ❌ Gmail exception: {e}")
            import traceback
            traceback.print_exc()
    
    # ✅ Outlook with credential injection
    if account in ['all', 'outlook'] and OUTLOOK_AVAILABLE:
        try:
            print(f"[Communication Hub] Calling microsoft_outlook_list_messages...")
            outlook_result = microsoft_outlook_list_messages(
                max_results=limit,
                _user_id=user_id,
                _injected_credentials=True
            )
            
            if outlook_result.get('success'):
                messages = outlook_result.get('messages', [])
                print(f"[Communication Hub] ✅ Got {len(messages)} Outlook messages")
                for msg in messages:
                    from_address = msg.get('from', {}).get('emailAddress', {})
                    emails.append({
                        'id': f"outlook_{msg['id']}",
                        'provider': 'outlook',
                        'from': from_address.get('address', 'Unknown'),
                        'to': ', '.join([addr.get('emailAddress', {}).get('address', '') 
                                       for addr in msg.get('toRecipients', [])]),
                        'subject': msg.get('subject', 'No Subject'),
                        'date': msg.get('receivedDateTime', ''),
                        'is_read': msg.get('isRead', False),
                        'snippet': msg.get('bodyPreview', ''),
                        'body_text': msg.get('body', {}).get('content', ''),
                        'body_html': msg.get('body', {}).get('content', '')
                    })
            else:
                error = outlook_result.get('error', 'Unknown error')
                print(f"[Communication Hub] ❌ Outlook failed: {error}")
        except Exception as e:
            print(f"[Communication Hub] ❌ Outlook exception: {e}")
            import traceback
            traceback.print_exc()
    
    # Sort by date (newest first)
    emails.sort(key=lambda x: x['date'], reverse=True)
    
    print(f"[Communication Hub] ✅ Returning {len(emails)} total email(s)")
    
    return jsonify({
        'success': True,
        'emails': emails,
        'count': len(emails)
    })


# ... REST OF FILE UNCHANGED ...
# (Keep get_email, send_email, mark_as_read, etc. routes as-is)
```

---

### Step 3: Restart Flask and Test

```powershell
# Stop server
BISTOP

# Start server with logging
cd C:\Users\gpoli\GIT\AI_agents\AI_infrastructure
python flask_app.py
```

**Watch for these logs:**
```
[Communication Hub] 🔍 Checking accounts for user_id=1
[Communication Hub] Found 2 OAuth token(s) in database
[Communication Hub]   - google: your.email@gmail.com (has_token=True)
[Communication Hub]   - microsoft: your.email@outlook.com (has_token=True)
[Communication Hub] ✅ Returning 2 account(s)
```

---

### Step 4: Test in Browser

1. Open Communication Hub module
2. Open browser DevTools (F12) → Console tab
3. Click "Unified Inbox" tab
4. Click "Refresh" button

**Expected browser console logs:**
```
[Communication Hub] Loaded 2 account(s)
[Communication Hub] Fetching emails...
[Communication Hub] Loaded 25 email(s)
```

**Expected Flask logs:**
```
[Communication Hub] 📧 Listing emails: user_id=1, account=all, limit=50
[Communication Hub] Calling gmail_list_messages...
🔑 Using database credentials for user 1
✅ Gmail service created with user 1's credentials
[Communication Hub] Gmail result: True
[Communication Hub] ✅ Got 25 Gmail messages
[Communication Hub] ✅ Returning 25 total email(s)
```

---

## 🔬 IF STILL NO EMAILS - DIAGNOSTIC CHECKLIST

### Check 1: Do you have OAuth tokens?

```powershell
python -c "import sqlite3; conn = sqlite3.connect('data/ai_infrastructure.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM oauth_tokens WHERE user_id=1'); print(f'Tokens for user 1: {cursor.fetchone()[0]}'); conn.close()"
```

**If 0:** You need to authenticate first:
1. Visit `http://localhost:5001/auth/google/login`
2. Complete OAuth flow
3. Check tokens again

### Check 2: Are tokens expired?

```powershell
python -c "import sqlite3; from datetime import datetime; conn = sqlite3.connect('data/ai_infrastructure.db'); cursor = conn.cursor(); cursor.execute('SELECT platform, expires_at FROM oauth_tokens WHERE user_id=1'); rows = cursor.fetchall(); [print(f'{r[0]}: expires {r[1]}') for r in rows]; conn.close()"
```

**If expired:** Tokens should auto-refresh, but you can manually re-authenticate.

### Check 3: Test Gmail tool directly

```powershell
cd C:\Users\gpoli\GIT\AI_agents
python -c "from google_workspace.gmail import gmail_list_messages; result = gmail_list_messages(max_results=5, _user_id=1, _injected_credentials=True); print(f'Success: {result.get(\"success\")}'); print(f'Messages: {len(result.get(\"messages\", []))}')"
```

**Expected:**
```
🔑 Using database credentials for user 1
✅ Gmail service created with user 1's credentials
Success: True
Messages: 5
```

### Check 4: Check UserAuthManager method

```powershell
python -c "from AI_infrastructure.auth.user_auth import UserAuthManager; auth = UserAuthManager(); creds = auth.get_user_google_oauth_credentials(1); print(f'Has creds: {creds is not None}'); print(f'Keys: {list(creds.keys()) if creds else \"None\"}')"
```

**Expected:**
```
Has creds: True
Keys: ['access_token', 'refresh_token', 'token_uri', 'client_id', 'client_secret', 'scopes']
```

---

## 📊 SUMMARY

| Issue | Status | Fix |
|-------|--------|-----|
| **Database location** | ✅ CORRECT | `data/ai_infrastructure.db` |
| **OAuth tokens exist** | ✅ YES | 5 tokens in oauth_tokens table |
| **Gmail tool supports injection** | ✅ YES | Already implemented |
| **Communication routes** | ❌ WRONG | Using UserAuthManager incorrectly |
| **Credential injection** | ❌ MISSING | Not passing _user_id + _injected_credentials |
| **Blueprint registration** | ✅ CORRECT | Registered in flask_app.py:133 |
| **API endpoint** | ✅ CORRECT | /api/communication-hub/* |

---

## 🎯 ACTION ITEMS

1. ✅ **Verify OAuth tokens exist** - Run Check 1 diagnostic
2. ❌ **Replace communication_routes.py** - Use fixed version above
3. ⏳ **Restart Flask server** - `BISTOP` then `BISTART`
4. ⏳ **Test in browser** - Open Communication Hub, click Refresh
5. ⏳ **Check logs** - Verify "Using database credentials" appears

---

**Status:** Ready to fix - complete solution provided above!  
**ETA:** 5 minutes to implement, test, and verify working.
