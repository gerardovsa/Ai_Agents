# Communication Hub Authentication Fix - Complete Solution

**Date:** November 10, 2025  
**Status:** 🔧 IN PROGRESS  
**Issue:** Communication Hub not connecting to Gmail/Outlook accounts  

---

## 🔍 ROOT CAUSE ANALYSIS

### Issues Identified:

1. **❌ Wrong Authentication System**
   - **Current:** Uses `UserAuthManager` (wrong)
   - **Should Use:** `CredentialInjector` (correct - same as agents)
   - **Impact:** Not finding OAuth tokens in database

2. **❌ Hardcoded user_id=1 in Frontend**
   - **Current:** JavaScript sends `user_id=1` to all API calls
   - **Should Use:** Actual logged-in user ID from `window.AppState.user.id`
   - **Impact:** All users see user 1's emails

3. **❌ Wrong Credential Lookup**
   - **Current:** Checks `user_gmail_accounts` table (doesn't exist)
   - **Should Use:** `oauth_tokens` table (correct location)
   - **Database:** `data/ai_infrastructure.db`

4. **❌ No Credential Injection**
   - **Current:** Calls Gmail tools without `_user_id` and `_injected_credentials`
   - **Should Use:** Same pattern as agent routes (lines 1324-1328 in agent_routes_v4.py)

---

## ✅ THE FIX

### Part 1: Backend Routes (`communication_routes.py`)

**Changes needed:**
1. Replace `UserAuthManager` with `CredentialInjector`
2. Use `injector.get_google_credentials(user_id)` for Gmail
3. Use `injector.get_microsoft_credentials(user_id)` for Outlook  
4. Pass `_user_id` and `_injected_credentials=True` to all tool calls
5. Get actual user email from OAuth token metadata

### Part 2: Frontend JavaScript (`communication-hub.js`)

**Changes needed:**
1. Add `getUserId()` method to get logged-in user from `window.AppState`
2. Replace all `user_id=1` with `user_id=${this.getUserId()}`
3. Add error handling for when user is not logged in
4. Add "Connect Account" button if no OAuth tokens found

---

## 📊 DATABASE VERIFICATION

**From database_analysis_report.txt:**

```
DATABASE: ai_infrastructure.db
Location: C:\Users\gpoli\GIT\AI_agents\data\ai_infrastructure.db

TABLE: oauth_tokens - 5 rows
Columns:
  - id (INTEGER PK)
  - user_id (INTEGER NOT NULL)
  - platform (TEXT NOT NULL) → 'google' or 'microsoft'
  - access_token (TEXT NOT NULL)
  - refresh_token (TEXT)
  - token_expiry (TEXT)
  - scopes (TEXT)
  - created_at (TEXT)
  - updated_at (TEXT)
```

**✅ Confirmed:** You have 5 OAuth tokens in the database  
**✅ Confirmed:** Tokens are in `data/ai_infrastructure.db`  
**✅ Confirmed:** CredentialInjector reads from this table

---

## 🔧 IMPLEMENTATION PLAN

### Step 1: Fix Backend Routes ✅ (In progress)
- [ ] Replace `UserAuthManager` with `CredentialInjector`
- [ ] Update `get_accounts()` to use `oauth_tokens` table
- [ ] Update `list_emails()` to inject credentials properly
- [ ] Add proper error messages when OAuth not connected

### Step 2: Fix Frontend JavaScript ✅ (In progress)
- [ ] Add `getUserId()` method
- [ ] Update all API calls to use actual user_id
- [ ] Add authentication state checking
- [ ] Show "Connect Gmail/Outlook" if no tokens

### Step 3: Testing Checklist
- [ ] User with Gmail OAuth can see Gmail messages
- [ ] User with Outlook OAuth can see Outlook messages  
- [ ] Multiple users see their own emails (not user 1's)
- [ ] Error messages show if not connected
- [ ] "Connect Account" button works

---

## 📝 CODE EXAMPLES

### ✅ CORRECT Pattern (From agent_routes_v4.py)

```python
# Line 1324-1328 in agent_routes_v4.py
gmail_result = registry.execute_tool(
    'gmail_list_messages',
    max_results=50,
    _user_id=user_id,           # ← Inject user ID
    _injected_credentials=True  # ← Enable credential injection
)
```

### ❌ WRONG Pattern (Current communication_routes.py)

```python
# Current - Missing credential injection
gmail_result = gmail_list_messages(
    max_results=limit
    # ❌ No _user_id
    # ❌ No _injected_credentials
)
```

---

## 🎯 EXPECTED OUTCOME

**After Fix:**

1. **Backend Logs:**
   ```
   [Communication Hub] Getting accounts for user_id=1
   🔑 Injecting Google credentials for user 1 into tool: gmail_list_messages
   ✅ Created gmail v1 service for user 1
   [Communication Hub] ✅ Got 25 Gmail messages
   [Communication Hub] Returning 25 total email(s)
   ```

2. **Frontend Console:**
   ```
   [Communication Hub] Loaded 1 account(s)
   [Communication Hub] Loaded 25 email(s)
   [Communication Hub] Refreshing inbox...
   ```

3. **UI Shows:**
   - ✅ Connected Gmail account in dropdown
   - ✅ Email list with 25 messages
   - ✅ Stat cards: Total: 25, Gmail: 25, Outlook: 0, Unread: 5

---

## 🔐 AUTHENTICATION FLOW

### Current (Broken):
```
User clicks "Refresh" 
  → Frontend sends user_id=1
  → Backend uses UserAuthManager 
  → Checks user_gmail_accounts table (doesn't exist)
  → Returns empty accounts: []
  → No emails load
```

### After Fix (Working):
```
User clicks "Refresh"
  → Frontend sends user_id=<actual_user_id>
  → Backend uses CredentialInjector
  → Checks oauth_tokens table (exists, has 5 tokens)
  → Returns accounts: [{provider: 'gmail', email: 'user@gmail.com'}]
  → Calls gmail_list_messages with _user_id and _injected_credentials
  → CredentialInjector fetches Google OAuth token
  → Gmail API returns messages
  → Frontend displays emails
```

---

## 🚀 NEXT STEPS

1. **Apply backend fix** → Replace communication_routes.py
2. **Apply frontend fix** → Update communication-hub.js
3. **Restart Flask server** → `BISTOP && BISTART`
4. **Clear browser cache** → Hard refresh (Ctrl+Shift+R)
5. **Test with your account** → Should see your emails
6. **Check server logs** → Should see credential injection logs

---

**Status:** Ready to implement fixes
**Files to modify:** 2 files
**Time estimate:** 5 minutes
**Risk level:** Low (only affects Communication Hub module)

