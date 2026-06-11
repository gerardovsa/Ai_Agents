# OAuth Scripts Guide - Complete Architecture Map

## Overview

Your AI Agent system has **12 OAuth-related scripts** across multiple directories. This creates **confusion and redundancy**. Here's what each script does and which ones are **ACTIVE vs LEGACY**.

---

## 🎯 ACTIVE SCRIPTS (Currently Used)

### 1. **AI_infrastructure/auth/user_auth.py** ✅ ACTIVE
**Location:** `C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\auth\user_auth.py`

**Purpose:** Core user authentication and profile management
- **Class:** `UserAuthManager`
- **Functions:**
  - User registration/login (username/password)
  - JWT token generation and validation
  - User profile management
  - Multi-tenant workspace isolation
  - Gmail account management (loads from .env.master)

**Database Tables Used:**
- `users` - User accounts
- `user_sessions` - JWT tokens
- `user_profile` - User metadata

**When Used:** Every authenticated request (OAuth middleware checks JWT tokens from here)

**Dependencies:** Loads from `.env.master` file

---

### 2. **AI_infrastructure/auth/credential_injector.py** ✅ ACTIVE
**Location:** `C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\auth\credential_injector.py`

**Purpose:** Injects user OAuth credentials into Google Workspace tool calls
- **Key Function:** `create_google_service_with_user_credentials(user_id, service_name, version)`
- **Process:**
  1. Queries `oauth_tokens` table for user's Google OAuth tokens
  2. Creates `Credentials` object from stored tokens
  3. Builds Google API service (Gmail, Calendar, Tasks, etc.)
  4. Returns authenticated service

**Database Tables Used:**
- `oauth_tokens` - OAuth access/refresh tokens

**When Used:** 
- Every Google Workspace tool call (Docs, Drive, Calendar, Tasks, Meet)
- **Fix #13** just updated 25 functions to use this!

**Critical:** This is the **CENTRAL HUB** for database OAuth. All Google tools should use this.

---

### 3. **AI_infrastructure/routes/google_auth_routes_V2_FIXED.py** ✅ ACTIVE
**Location:** `C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\routes\google_auth_routes_V2_FIXED.py`

**Purpose:** Google OAuth 2.0 flow for user authentication (Login with Google)
- **Blueprint:** `google_auth_bp` (registered in Flask app)
- **Routes:**
  - `/api/auth/google/login` - Initiates Google OAuth flow
  - `/api/auth/google/callback` - Handles OAuth callback from Google
  - `/api/auth/google/status` - Checks current OAuth status
  - `/api/auth/google/revoke` - Revokes OAuth tokens

**OAuth Flow:**
1. User clicks "Login with Google"
2. Redirects to Google consent screen
3. Google redirects back to `/callback` with authorization code
4. Exchanges code for access_token + refresh_token
5. **Writes to `oauth_tokens` table** (24-column schema)
6. Returns JWT token for user session

**Database Tables Used:**
- `oauth_tokens` - Stores Google OAuth tokens
- `users` - Creates/updates user record
- `user_sessions` - Stores JWT token

**Scopes Requested:**
- Gmail (read, send, compose)
- Drive (full access)
- Calendar (full access)
- Docs (full access)
- Sheets (full access)
- Forms (full access)
- Tasks (full access)

**Dependencies:** Loads from `.env.master`:
- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI`

---

### 4. **AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py** ✅ ACTIVE
**Location:** `C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\routes\microsoft_auth_routes_V2_FIXED.py`

**Purpose:** Microsoft 365 OAuth 2.0 flow (Login with Microsoft)
- **Blueprint:** `microsoft_auth_bp` (registered in Flask app)
- **Routes:**
  - `/api/auth/microsoft/login` - Initiates Microsoft OAuth flow
  - `/api/auth/microsoft/callback` - Handles OAuth callback
  - `/api/auth/microsoft/status` - Checks OAuth status
  - `/api/auth/microsoft/revoke` - Revokes tokens

**Similar to Google auth but for Microsoft Graph API**

**Database Tables Used:**
- `oauth_tokens` - Stores Microsoft OAuth tokens (platform='microsoft')
- `users` - Creates/updates user
- `user_sessions` - JWT token

**Dependencies:** Loads from `.env.master`:
- `MICROSOFT_CLIENT_ID`
- `MICROSOFT_CLIENT_SECRET`
- `MICROSOFT_TENANT_ID`

---

### 5. **Microsoft_365_Connection/microsoft365_oauth_manager.py** ✅ ACTIVE
**Location:** `C:\Users\gpoli\GIT\AI_agents\Microsoft_365_Connection\microsoft365_oauth_manager.py`

**Purpose:** Microsoft 365 OAuth utilities and token management
- **Class:** `Microsoft365OAuthManager`
- **Functions:**
  - Build authorization URLs
  - Exchange authorization codes for tokens
  - Refresh expired tokens
  - Validate tokens
  - Get user info from Microsoft Graph API

**Used By:** `microsoft_auth_routes_V2_FIXED.py`

**Not a Flask route** - Helper library for OAuth operations

---

### 6. **AI_infrastructure/config/oauth_config.py** ✅ ACTIVE
**Location:** `C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\config\oauth_config.py`

**Purpose:** Centralized OAuth provider configuration
- **Dictionary:** `OAUTH_PROVIDERS`
- **Contains:**
  - Google OAuth config (client_id, client_secret, scopes, redirect_uri)
  - Microsoft OAuth config
  - Microsoft365 OAuth config

**Loads from `.env.master`**

**Used By:** OAuth routes for configuration data

**Note:** This provides a **centralized config** but individual route files also load `.env.master` directly. Consider consolidating to use ONLY this config.

---

## 📦 UTILITY SCRIPTS

### 7. **get_auth_token.py** ✅ UTILITY (CLI Only)
**Location:** `C:\Users\gpoli\GIT\AI_agents\get_auth_token.py`

**Purpose:** CLI utility to generate JWT tokens for testing
- **Usage:** `python get_auth_token.py user@example.com`
- **Function:**
  1. Looks up user by email in `users` table
  2. If not found, creates dev user
  3. Generates JWT token (30-day expiry)
  4. Stores in `user_sessions` table
  5. Prints token to stdout

**Used By:** `CHAT.ps1` CLI tool (for local testing)

**Not a web service** - Developer convenience script

---

### 8. **google-auth.js** ⚠️ FRONTEND (Chrome Extension)
**Location:** `C:\Users\gpoli\GIT\AI_agents\google-auth.js`

**Purpose:** Client-side Google OAuth for Chrome extension
- **Class:** `GoogleAuthManager`
- **Functions:**
  - Initialize Google OAuth in browser
  - Launch Chrome identity web auth flow
  - Handle OAuth callbacks
  - Store/retrieve tokens in Chrome storage
  - Support public document access (no auth)

**Scopes:**
- Spreadsheets (readonly)
- Documents (readonly)
- Drive (readonly)

**Environment:** Chrome extension only, NOT Flask backend

**Note:** This is **COMPLETELY SEPARATE** from backend OAuth. Frontend handles its own OAuth for extension features.

---

## 🗑️ LEGACY SCRIPTS (Deprecated/Unused)

### 9. **google_workspace/oauth_manager.py** ⚠️ LEGACY (File-based OAuth)
**Location:** `C:\Users\gpoli\GIT\AI_agents\google_workspace\oauth_manager.py`

**Original Purpose:** File-based OAuth for Google Workspace tools
- Desktop mode: Load `credentials_desktop.json`
- Web mode: Load `credentials_web.json`
- Token caching in JSON files

**Status:** ⚠️ **BEING REPLACED**
- **Fix #13** updated Google tools to use **database OAuth** instead
- Google Calendar, Tasks, Meet now call `credential_injector.py`
- File-based OAuth is **fallback only**

**Problem:** 
- Requires `credentials_desktop.json` file (doesn't exist in production)
- Single-user authentication (no multi-tenant support)
- No token storage in database

**Future:** Should be **deprecated entirely** once all tools migrate to database OAuth

---

### 10. **google_workspace/oauth_credential_loader.py** ✅ TRANSITIONAL
**Location:** `C:\Users\gpoli\GIT\AI_agents\google_workspace\oauth_credential_loader.py`

**Purpose:** Load OAuth credentials from database for Google Workspace tools
- **Function:** `get_oauth_credentials_from_db(user_id)`
- **Process:**
  1. Connects to `data/ai_infrastructure.db`
  2. Queries `oauth_tokens` table
  3. Returns credential dict

**Status:** ✅ **GOOD APPROACH** but redundant with `credential_injector.py`

**Difference:**
- `oauth_credential_loader.py` - Returns credential dict (lower level)
- `credential_injector.py` - Returns Google API service object (higher level)

**Recommendation:** Consolidate - use `credential_injector.py` only

---

### 11. **AI_infrastructure/routes/oauth_routes.py** ⚠️ LEGACY (Google OAuth - Old Version)
**Location:** `C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\routes\oauth_routes.py`

**Original Purpose:** Google Workspace OAuth routes (old architecture)
- **Blueprint:** `oauth_bp` (url_prefix='/api/oauth')
- **Routes:**
  - `/api/oauth/workspace/start` - Start OAuth flow
  - Requires `credentials_web.json` file

**Status:** ⚠️ **LEGACY** - Replaced by `google_auth_routes_V2_FIXED.py`

**Differences from V2_FIXED:**
- Uses **file-based credentials** (`credentials_web.json`)
- Old URL structure (`/api/oauth/*` vs `/api/auth/google/*`)
- Different OAuth scopes configuration
- No database OAuth token storage

**Action:** ⚠️ **DELETE OR RENAME TO .OLD** - Not registered in Flask app (verified in flask_app.py line 101)
- New Google auth uses `google_auth_routes_V2_FIXED.py`
- This file is **NOT ACTIVE** and causes confusion

---

### 12. **routes/microsoft_auth_routes.py** ⚠️ LEGACY (Not Used)
**Location:** `C:\Users\gpoli\GIT\AI_agents\routes\microsoft_auth_routes.py`

**Original Purpose:** Microsoft 365 OAuth routes (old version)
- **Blueprint:** `microsoft_auth_bp` (NO url_prefix)
- **Routes:**
  - `/api/auth/microsoft/*`
- **Scopes:** User.Read, Mail, Teams, OneDrive, Calendar, Tasks
- **Writes to:** `user_platform_credentials` table (old schema)

**Status:** ⚠️ **NOT REGISTERED** - Flask app uses V2_FIXED instead

**Verified:** `flask_app.py` line 84:
```python
from routes.microsoft_auth_routes_V2_FIXED import microsoft_auth_bp
```

**This means:**
- ✅ Flask app imports from **V2_FIXED** (correct schema)
- ⚠️ Old `routes/microsoft_auth_routes.py` is **NOT USED**
- ✅ No conflict - V2_FIXED is the active version

**Action:** Safe to **DELETE** `routes/microsoft_auth_routes.py` (old version, not registered)

---

## 🏗️ Architecture Summary

### Current OAuth Flow (Fix #13)

```
User Login (Frontend)
    ↓
/api/auth/google/login (google_auth_routes_V2_FIXED.py)
    ↓
Google OAuth Consent Screen
    ↓
/api/auth/google/callback (exchanges code for tokens)
    ↓
INSERT INTO oauth_tokens (access_token, refresh_token, ...)
    ↓
Returns JWT token to user (stored in browser localStorage)
    ↓
User sends chat message with JWT token
    ↓
OAuth middleware (agent_routes_v4.py) validates JWT → sets g.user_id
    ↓
Agent worker passes _user_id=1, _injected_credentials=True to tool
    ↓
Tool function (e.g., google_calendar_list_calendars)
    ↓
credential_injector.create_google_service_with_user_credentials(user_id=1)
    ↓
SELECT access_token FROM oauth_tokens WHERE user_id=1 AND platform='google'
    ↓
Google API service created with user's OAuth token
    ↓
Returns user's personal data (calendars, emails, tasks, etc.)
```

---

## 📊 Database Schema

### oauth_tokens Table (24 columns)
```sql
CREATE TABLE oauth_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,  -- 'google' or 'microsoft'
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_type TEXT,
    expires_at TEXT,
    scope TEXT,
    email TEXT,
    name TEXT,
    picture TEXT,
    -- ... 13 more columns
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Key Queries

**Store Google OAuth tokens:**
```sql
INSERT INTO oauth_tokens (
    user_id, platform, access_token, refresh_token, 
    expires_at, email, scope
) VALUES (?, 'google', ?, ?, ?, ?, ?)
```

**Load Google OAuth tokens:**
```sql
SELECT access_token, refresh_token, token_uri, client_id, client_secret, scopes
FROM oauth_tokens
WHERE user_id = ? AND platform = 'google'
ORDER BY updated_at DESC
LIMIT 1
```

---

## 🔧 Recommendations

### 1. Consolidate OAuth Credential Loading
**Current:** 2 scripts do similar things
- `credential_injector.py` - Returns Google API service
- `oauth_credential_loader.py` - Returns credential dict

**Recommendation:** Use `credential_injector.py` only (it's higher level and more convenient)

### 2. Deprecate File-Based OAuth
**Current:** `google_workspace/oauth_manager.py` still tries to load `credentials_desktop.json`

**Recommendation:** 
- Remove all references to `credentials_desktop.json`
- Make database OAuth the ONLY option
- Delete `oauth_manager.py` once all tools migrated

### 3. Remove Duplicate OAuth Routes
**Current:** May have duplicate Microsoft auth routes in 2 locations

**Action:**
- Check if `routes/microsoft_auth_routes.py` is registered
- If not, delete it
- Keep only `AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py`

### 4. Centralize OAuth Config
**Current:** Multiple files load `.env.master` directly

**Recommendation:** 
- All routes should import from `oauth_config.py`
- Only `oauth_config.py` should load `.env.master`
- Reduces duplication and errors

### 5. Document Frontend vs Backend OAuth
**Current:** `google-auth.js` handles Chrome extension OAuth separately

**Clarification Needed:**
- Does frontend need its own OAuth? (Yes - for extension features)
- Should frontend use backend OAuth tokens? (Maybe - for SSO)
- Clear separation of concerns

---

## 📝 Quick Reference

### Which Script Should I Use For...?

**User login with Google:**
→ `AI_infrastructure/routes/google_auth_routes_V2_FIXED.py`

**User login with Microsoft:**
→ `AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py`

**Load Google OAuth tokens for tools:**
→ `AI_infrastructure/auth/credential_injector.py`

**Create Google API service with user credentials:**
→ `credential_injector.create_google_service_with_user_credentials(user_id, service_name)`

**Generate JWT token for CLI testing:**
→ `python get_auth_token.py user@example.com`

**Get OAuth config for any provider:**
→ `AI_infrastructure/config/oauth_config.py` → `OAUTH_PROVIDERS['google']`

**Handle user registration/login:**
→ `AI_infrastructure/auth/user_auth.py` → `UserAuthManager`

---

## 🚨 Critical Path (What Actually Runs)

**Active OAuth Routes (Registered in Flask app):**
1. `google_auth_routes_V2_FIXED.py` - Google OAuth flow
2. `microsoft_auth_routes_V2_FIXED.py` - Microsoft OAuth flow

**Active OAuth Libraries:**
1. `user_auth.py` - User authentication and JWT tokens
2. `credential_injector.py` - Google OAuth credential injection
3. `microsoft365_oauth_manager.py` - Microsoft OAuth utilities

**Active Utilities:**
1. `get_auth_token.py` - CLI JWT token generator
2. `oauth_config.py` - Centralized OAuth config

**Legacy/Transitional:**
1. `oauth_manager.py` - File-based OAuth (being phased out)
2. `oauth_credential_loader.py` - Database OAuth (redundant with credential_injector)

**Frontend Only:**
1. `google-auth.js` - Chrome extension OAuth (separate from backend)

**Legacy (Not Registered):**
1. `oauth_routes.py` - Old Google OAuth routes (NOT registered, safe to delete)
2. `routes/microsoft_auth_routes.py` - Old Microsoft OAuth routes (NOT registered, V2_FIXED is used instead)

---

## 🎯 Action Items

### High Priority (Clean Up Legacy Files)

- [ ] **Delete Legacy OAuth Routes**
  - [x] ✅ Verified `microsoft_auth_routes_V2_FIXED.py` is registered (not old version)
  - [ ] Delete `routes/microsoft_auth_routes.py` (old Microsoft OAuth, not used)
  - [ ] Delete `AI_infrastructure/routes/oauth_routes.py` (old Google OAuth, not used)

### Medium Priority (Consolidation)

- [ ] **Consolidate** OAuth credential loading (keep only `credential_injector.py`)
  - [ ] Remove redundant `oauth_credential_loader.py`
  - [ ] Update any tools still using `oauth_credential_loader` to use `credential_injector`

- [ ] **Phase out** file-based OAuth (`oauth_manager.py`)
  - [ ] Migrate any remaining tools from file-based to database OAuth
  - [ ] Remove `credentials_desktop.json` and `credentials_web.json` references

- [ ] **Centralize** `.env.master` loading (all routes use `oauth_config.py`)
  - [ ] Update `google_auth_routes_V2_FIXED.py` to import from `oauth_config.py`
  - [ ] Update `microsoft_auth_routes_V2_FIXED.py` to import from `oauth_config.py`

### Low Priority (Testing & Documentation)

- [ ] **Test** all Google Workspace tools with database OAuth (Fix #13)
  - [ ] Calendar: List calendars
  - [ ] Tasks: List task lists
  - [ ] Meet: List meetings
  - [ ] Gmail: Send email
  - [ ] Drive: List files

- [ ] **Document** frontend vs backend OAuth separation
  - [ ] Clarify when to use `google-auth.js` (Chrome extension only)
  - [ ] Clarify when to use backend OAuth routes (web app)

---

**Summary:** You have 12 OAuth scripts, but only **6-7 are actively used**. The rest are legacy or redundant. Main active components: `google_auth_routes_V2_FIXED.py`, `microsoft_auth_routes_V2_FIXED.py`, `user_auth.py`, and `credential_injector.py`.
