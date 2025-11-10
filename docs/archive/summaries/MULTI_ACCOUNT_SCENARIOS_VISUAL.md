# 🎭 Multi-Account Scenarios - Visual Guide

**Date:** October 28, 2025  
**Purpose:** Visual representation of what happens with multiple OAuth logins

---

## 🔴 Scenario 1: Login Gmail #1, Then Gmail #2 (PROBLEM!)

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: First Login                                             │
└─────────────────────────────────────────────────────────────────┘

User: john@gmail.com
  ↓
Google OAuth
  ↓
Backend checks: SELECT * FROM users WHERE email = 'john@gmail.com'
  ↓
Result: NOT FOUND
  ↓
CREATE NEW USER:
  ┌──────────────────────────────────┐
  │ users table                      │
  ├──────────────────────────────────┤
  │ id: 123                          │
  │ email: john@gmail.com            │
  │ username: john                   │
  └──────────────────────────────────┘
  ↓
Store Google OAuth tokens:
  ┌──────────────────────────────────┐
  │ user_platform_credentials        │
  ├──────────────────────────────────┤
  │ user_id: 123                     │
  │ platform: google                 │
  │ access_token: ya29...            │
  │ refresh_token: 1//0g...          │
  └──────────────────────────────────┘
  ↓
Generate JWT:
  ┌──────────────────────────────────┐
  │ user_sessions                    │
  ├──────────────────────────────────┤
  │ user_id: 123                     │
  │ token: eyJhbGci...               │
  │ expires_at: +24h                 │
  └──────────────────────────────────┘
  ↓
Frontend: localStorage.authToken = "eyJhbGci..."
  ↓
✅ USER LOGGED IN AS "john" (ID: 123)

┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: User Works                                              │
└─────────────────────────────────────────────────────────────────┘

User creates:
  - Chat Thread #1 (user_id: 123)
  - Chat Thread #2 (user_id: 123)
  - Saves preferences (user_id: 123)

All data tied to User ID: 123

┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: User Logs Out                                           │
└─────────────────────────────────────────────────────────────────┘

Frontend:
  localStorage.removeItem('authToken') ✅
  localStorage.removeItem('userProfile') ✅

Backend:
  JWT token in user_sessions: STILL THERE ⚠️
  OAuth tokens: STILL THERE ⚠️
  User account: STILL EXISTS ✅

┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Login with DIFFERENT Gmail (john2@gmail.com)           │
└─────────────────────────────────────────────────────────────────┘

User: john2@gmail.com  ← DIFFERENT EMAIL!
  ↓
Google OAuth
  ↓
Backend checks: SELECT * FROM users WHERE email = 'john2@gmail.com'
  ↓
Result: NOT FOUND
  ↓
❌ CREATE NEW USER (AGAIN!):
  ┌──────────────────────────────────┐
  │ users table                      │
  ├──────────────────────────────────┤
  │ id: 456  ← NEW USER ID!          │
  │ email: john2@gmail.com           │
  │ username: john2                  │
  └──────────────────────────────────┘
  ↓
Store NEW Google OAuth tokens:
  ┌──────────────────────────────────┐
  │ user_platform_credentials        │
  ├──────────────────────────────────┤
  │ user_id: 456  ← DIFFERENT USER!  │
  │ platform: google                 │
  │ access_token: ya29...            │
  │ refresh_token: 1//0g...          │
  └──────────────────────────────────┘
  ↓
Generate NEW JWT:
  ┌──────────────────────────────────┐
  │ user_sessions                    │
  ├──────────────────────────────────┤
  │ user_id: 456  ← NEW SESSION!     │
  │ token: eyJhbGci... (different)   │
  │ expires_at: +24h                 │
  └──────────────────────────────────┘
  ↓
Frontend: localStorage.authToken = "eyJhbGci..." (NEW TOKEN)
  ↓
✅ USER LOGGED IN AS "john2" (ID: 456)

┌─────────────────────────────────────────────────────────────────┐
│ RESULT: TWO SEPARATE ACCOUNTS!                                  │
└─────────────────────────────────────────────────────────────────┘

Database State:

users table:
  ┌─────┬──────────┬────────────────────┐
  │ ID  │ Username │ Email              │
  ├─────┼──────────┼────────────────────┤
  │ 123 │ john     │ john@gmail.com     │  ← Old account
  │ 456 │ john2    │ john2@gmail.com    │  ← New account
  └─────┴──────────┴────────────────────┘

Chat Threads:
  User ID 123:
    - Chat Thread #1 ← NOT VISIBLE TO john2!
    - Chat Thread #2 ← NOT VISIBLE TO john2!
  
  User ID 456:
    - (empty) ← Starting fresh

❌ USER CONFUSED: "Where did my chats go?!"
```

---

## 🟢 Scenario 2: Login Gmail, Then M365 (SAME EMAIL - GOOD!)

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: First Login with Google                                │
└─────────────────────────────────────────────────────────────────┘

User: jane@company.com (via Google OAuth)
  ↓
Backend: CREATE USER
  ┌──────────────────────────────────┐
  │ users table                      │
  ├──────────────────────────────────┤
  │ id: 789                          │
  │ email: jane@company.com          │
  │ username: jane                   │
  └──────────────────────────────────┘
  ↓
Store Google credentials:
  ┌──────────────────────────────────┐
  │ user_platform_credentials        │
  ├──────────────────────────────────┤
  │ user_id: 789                     │
  │ platform: google                 │
  │ credential_key: access_token     │
  │ credential_value: ya29...        │
  └──────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: User Works & Logs Out                                  │
└─────────────────────────────────────────────────────────────────┘

User creates chat threads (tied to user_id: 789)
User logs out (localStorage cleared)

┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Login with M365 (SAME EMAIL)                           │
└─────────────────────────────────────────────────────────────────┘

User: jane@company.com (via Microsoft 365 OAuth)
  ↓
Backend checks: SELECT * FROM users WHERE email = 'jane@company.com'
  ↓
Result: FOUND! (User ID: 789)
  ↓
✅ USE EXISTING ACCOUNT (no new user created)
  ┌──────────────────────────────────┐
  │ users table                      │
  ├──────────────────────────────────┤
  │ id: 789  ← SAME USER ID!         │
  │ email: jane@company.com          │
  │ username: jane                   │
  └──────────────────────────────────┘
  ↓
Store M365 credentials (NEW ROWS):
  ┌──────────────────────────────────┐
  │ user_platform_credentials        │
  ├──────────────────────────────────┤
  │ user_id: 789                     │
  │ platform: google                 │ ← Old row (still there)
  │ credential_key: access_token     │
  ├──────────────────────────────────┤
  │ user_id: 789                     │
  │ platform: microsoft365           │ ← NEW ROW
  │ credential_key: access_token     │
  │ credential_value: EwBwA8...      │
  └──────────────────────────────────┘
  ↓
Generate JWT (same user_id: 789)
  ↓
✅ USER LOGGED IN AS "jane" (ID: 789)

┌─────────────────────────────────────────────────────────────────┐
│ RESULT: SAME ACCOUNT, BOTH OAUTH PROVIDERS LINKED!             │
└─────────────────────────────────────────────────────────────────┘

Database State:

users table:
  ┌─────┬──────────┬────────────────────┐
  │ ID  │ Username │ Email              │
  ├─────┼──────────┼────────────────────┤
  │ 789 │ jane     │ jane@company.com   │  ← ONE account
  └─────┴──────────┴────────────────────┘

user_platform_credentials:
  ┌─────────┬────────────────┬─────────────────┐
  │ User ID │ Platform       │ Token           │
  ├─────────┼────────────────┼─────────────────┤
  │ 789     │ google         │ ya29...         │  ← Google
  │ 789     │ microsoft365   │ EwBwA8...       │  ← M365
  └─────────┴────────────────┴─────────────────┘

Chat Threads:
  User ID 789:
    - Chat Thread #1 ← STILL VISIBLE!
    - Chat Thread #2 ← STILL VISIBLE!

✅ USER HAPPY: "My chats are still here!"
✅ USER CAN USE EITHER PROVIDER to login going forward
```

---

## 🔴 Scenario 3: Login Gmail, Then M365 (DIFFERENT EMAILS - PROBLEM!)

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: First Login with Gmail                                 │
└─────────────────────────────────────────────────────────────────┘

User: alice@gmail.com (via Google OAuth)
  ↓
Backend: CREATE USER
  ┌──────────────────────────────────┐
  │ users table                      │
  ├──────────────────────────────────┤
  │ id: 111                          │
  │ email: alice@gmail.com           │
  │ username: alice                  │
  └──────────────────────────────────┘

User creates chat threads (user_id: 111)

┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Logout, Then Login with M365 (DIFFERENT EMAIL)         │
└─────────────────────────────────────────────────────────────────┘

User: alice@company.com (via Microsoft 365 OAuth)
  ↓
Backend checks: SELECT * FROM users WHERE email = 'alice@company.com'
  ↓
Result: NOT FOUND (different email!)
  ↓
❌ CREATE NEW USER (AGAIN!):
  ┌──────────────────────────────────┐
  │ users table                      │
  ├──────────────────────────────────┤
  │ id: 222  ← NEW USER ID!          │
  │ email: alice@company.com         │
  │ username: alice                  │
  └──────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ RESULT: TWO SEPARATE ACCOUNTS!                                  │
└─────────────────────────────────────────────────────────────────┘

Database State:

users table:
  ┌─────┬──────────┬─────────────────────┐
  │ ID  │ Username │ Email               │
  ├─────┼──────────┼─────────────────────┤
  │ 111 │ alice    │ alice@gmail.com     │  ← Personal
  │ 222 │ alice    │ alice@company.com   │  ← Work
  └─────┴──────────┴─────────────────────┘

Chat Threads:
  User ID 111: Chat Thread #1, #2
  User ID 222: (empty)

❌ SAME PERSON, TWO ACCOUNTS, DATA SPLIT!
```

---

## 📊 Summary Table

| Scenario | Email 1 | Email 2 | Result | Data Shared? |
|----------|---------|---------|--------|--------------|
| **1** | john@gmail.com | john2@gmail.com | ❌ 2 accounts | No |
| **2** | jane@company.com (Google) | jane@company.com (M365) | ✅ 1 account | Yes |
| **3** | alice@gmail.com | alice@company.com | ❌ 2 accounts | No |

---

## 🔍 Key Insight

**Current System Logic:**
```python
# Backend checks ONLY email address
user = db.query("SELECT * FROM users WHERE email = ?", (email,))

if user:
    # Use existing account
    use_account(user.id)
else:
    # Create NEW account
    create_account(email)
```

**Problem:**
- ✅ Works if user always uses SAME email
- ❌ Breaks if user has multiple emails
- ❌ No way to link accounts

---

## 🛠️ What Needs to Be Built

### **Account Linking Feature**

**User Flow:**
```
1. User logged in as john@gmail.com (User ID: 123)
2. User goes to Settings → "Link Another Account"
3. User clicks "Link Microsoft 365"
4. OAuth flow → john@company.com
5. Backend:
   - Creates user_id: 456 for john@company.com
   - Links 456 → 123 (primary)
   - Stores M365 credentials under user_id: 123
6. Result: One primary account, multiple linked emails
```

**Database Changes Needed:**
```sql
-- New table for linking accounts
CREATE TABLE user_account_links (
    id INTEGER PRIMARY KEY,
    primary_user_id INTEGER,
    linked_user_id INTEGER,
    linked_email TEXT,
    link_type TEXT,
    created_at TIMESTAMP
);

-- Example:
primary_user_id: 123 (john@gmail.com)
linked_user_id: 456 (john@company.com)
link_type: 'microsoft365'

-- Query threads:
SELECT * FROM threads 
WHERE user_id = 123 OR user_id IN (
    SELECT linked_user_id FROM user_account_links 
    WHERE primary_user_id = 123
)
```

---

## 🎯 Recommendation

**Priority: HIGH**

**Current State:**
- ⚠️ Multiple emails = Multiple accounts
- ⚠️ Data fragmentation
- ⚠️ User confusion

**Fix:**
1. Add account linking feature
2. Add "Primary Email" concept
3. Update queries to include linked accounts
4. Add UI to manage linked accounts

**Until then:**
- ⚠️ Users should use SAME email across all OAuth providers
- ⚠️ Document this limitation clearly

---

**Status:** 🔴 **NEEDS FIXING**  
**Impact:** HIGH - Affects every user with multiple emails  
**Complexity:** Medium - Requires database changes + UI

