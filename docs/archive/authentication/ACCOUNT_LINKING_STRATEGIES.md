# 🔗 Account Linking Strategies - Analysis & Recommendations

**Date:** October 28, 2025  
**Status:** Design Decision Needed  
**Purpose:** Evaluate different approaches to multi-email account linking

---

## 🎯 The Goal

**User wants:**
- One person with multiple emails (e.g., `john@gmail.com`, `john@company.com`, `john@yahoo.com`)
- Login with ANY email → access same data
- One "primary" account where data lives
- Ability to use credentials from any linked account
- Seamless experience across all emails

---

## 📊 Strategy Comparison

### **Strategy 1: Primary + Linked Accounts (Recommended)**

**Concept:** One master account, others link to it

```
Primary Account:
  ├─ User ID: 123
  ├─ Email: john@gmail.com (PRIMARY)
  ├─ All data stored here
  └─ Linked Accounts:
       ├─ john@company.com (M365 OAuth)
       └─ john@yahoo.com (Google OAuth)
```

**Database Structure:**
```sql
-- Main users table (unchanged)
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE,
    username TEXT,
    password_hash TEXT,
    role TEXT,
    is_primary BOOLEAN DEFAULT 1,  -- New: Marks primary account
    primary_account_id INTEGER,     -- New: NULL if primary, otherwise points to primary
    created_at TIMESTAMP,
    FOREIGN KEY (primary_account_id) REFERENCES users(id)
);

-- Track which platforms are linked
CREATE TABLE user_linked_emails (
    id INTEGER PRIMARY KEY,
    primary_user_id INTEGER NOT NULL,
    linked_email TEXT NOT NULL,
    oauth_provider TEXT,  -- 'google', 'microsoft365'
    linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (primary_user_id) REFERENCES users(id),
    UNIQUE(primary_user_id, linked_email)
);
```

**How It Works:**
```
1. User logs in with john@gmail.com
   → Creates User ID: 123 (primary_account_id = NULL, is_primary = 1)

2. User clicks "Link Microsoft Account"
   → OAuth flow with john@company.com
   → Creates User ID: 456 (primary_account_id = 123, is_primary = 0)
   → Stores M365 OAuth tokens under user_id: 123 (primary)
   → Inserts: user_linked_emails(primary=123, linked='john@company.com')

3. User logs out, logs in with john@company.com
   → Backend finds user_id: 456
   → Checks: primary_account_id = 123
   → Redirects all queries to use user_id: 123
   → Generates JWT with user_id: 123 (not 456)
```

**Pros:**
- ✅ Clear hierarchy (one primary account)
- ✅ All data in one place
- ✅ Easy to query (always use primary_account_id)
- ✅ User can change primary later
- ✅ Credentials stored per email (flexible)

**Cons:**
- ⚠️ Requires modifying users table
- ⚠️ Migration needed for existing users
- ⚠️ Slightly complex logic (redirect to primary)

---

### **Strategy 2: Account Aliases (Simpler)**

**Concept:** One account, multiple email aliases

```
Main Account:
  User ID: 123
  Primary Email: john@gmail.com
  
Email Aliases:
  - john@company.com → User ID: 123
  - john@yahoo.com → User ID: 123
```

**Database Structure:**
```sql
-- Users table (unchanged)
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE,  -- Primary email
    username TEXT,
    password_hash TEXT,
    role TEXT
);

-- Simple aliases table
CREATE TABLE user_email_aliases (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    alias_email TEXT UNIQUE NOT NULL,
    oauth_provider TEXT,
    is_verified BOOLEAN DEFAULT 0,
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**How It Works:**
```
1. User logs in with john@gmail.com
   → Creates User ID: 123
   → email = 'john@gmail.com' (in users table)

2. User clicks "Add Email"
   → OAuth flow with john@company.com
   → Inserts: user_email_aliases(user_id=123, alias='john@company.com')
   → Stores M365 tokens under user_id: 123

3. User logs in with john@company.com
   → Backend checks users WHERE email = 'john@company.com' → NOT FOUND
   → Backend checks aliases WHERE alias_email = 'john@company.com' → FOUND user_id: 123
   → Uses user_id: 123 for everything
```

**Pros:**
- ✅ Very simple concept (aliases = pointers)
- ✅ Minimal database changes
- ✅ Easy to understand and maintain
- ✅ All queries use same user_id

**Cons:**
- ⚠️ Primary email in users.email is special (not in aliases)
- ⚠️ Need to check TWO places for email lookup
- ⚠️ Changing primary email is complex

---

### **Strategy 3: Email → User Mapping Table**

**Concept:** Separate email storage from user identity

```
User Identity:
  User ID: 123
  Username: john_smith
  (no email in users table!)

Email Mappings:
  john@gmail.com     → User 123 (primary)
  john@company.com   → User 123
  john@yahoo.com     → User 123
```

**Database Structure:**
```sql
-- Users table (NO EMAIL!)
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    role TEXT,
    display_name TEXT,
    created_at TIMESTAMP
);

-- All emails go here
CREATE TABLE user_emails (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    email TEXT UNIQUE NOT NULL,
    is_primary BOOLEAN DEFAULT 0,
    oauth_provider TEXT,  -- NULL for password login
    verified BOOLEAN DEFAULT 0,
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, is_primary) WHERE is_primary = 1  -- Only one primary per user
);
```

**How It Works:**
```
1. User logs in with john@gmail.com
   → Creates User ID: 123, username: 'john_smith'
   → Inserts: user_emails(user_id=123, email='john@gmail.com', is_primary=1)

2. User adds john@company.com
   → Inserts: user_emails(user_id=123, email='john@company.com', is_primary=0)

3. Any login with any email
   → SELECT user_id FROM user_emails WHERE email = ?
   → Always gets user_id: 123
```

**Pros:**
- ✅ Clean separation (identity vs contact info)
- ✅ All emails treated equally (except primary flag)
- ✅ Easy to add/remove emails
- ✅ Changing primary email is trivial (flip boolean)
- ✅ Most flexible long-term

**Cons:**
- ⚠️ Major schema change (remove email from users)
- ⚠️ Complex migration for existing data
- ⚠️ Over-engineered for current needs?

---

### **Strategy 4: Unified Identity Table**

**Concept:** Identity provider abstraction

```
User Identity: john_smith_123
  
Identity Providers:
  - google:john@gmail.com → john_smith_123
  - microsoft365:john@company.com → john_smith_123
  - yahoo:john@yahoo.com → john_smith_123
```

**Database Structure:**
```sql
-- Abstract user (no email, no provider)
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    display_name TEXT,
    role TEXT
);

-- All auth methods here
CREATE TABLE user_identities (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    provider TEXT NOT NULL,  -- 'google', 'microsoft365', 'password'
    provider_user_id TEXT,   -- External ID from provider
    email TEXT NOT NULL,
    is_primary BOOLEAN DEFAULT 0,
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(provider, email)
);
```

**How It Works:**
```
1. Login with Google (john@gmail.com)
   → Creates user_id: 123
   → Inserts: user_identities(user_id=123, provider='google', email='john@gmail.com')

2. Link M365 (john@company.com)
   → Inserts: user_identities(user_id=123, provider='microsoft365', email='john@company.com')

3. Login with any provider + any email
   → SELECT user_id FROM user_identities WHERE provider=? AND email=?
   → Returns user_id: 123
```

**Pros:**
- ✅ Enterprise-grade architecture
- ✅ Supports ANY identity provider (SAML, LDAP, etc.)
- ✅ Clear provider isolation
- ✅ Easy to add new providers

**Cons:**
- ⚠️ Most complex option
- ⚠️ Overkill for 2 OAuth providers
- ⚠️ Significant development effort

---

## 🎯 Recommended Strategy: **#2 - Account Aliases**

**Why this one?**
- ✨ **Simplest to implement** (minimal changes)
- ✨ **Easy to understand** (aliases → main account)
- ✨ **Solves the problem** (multiple emails → one user)
- ✨ **Low risk** (doesn't touch existing users table much)
- ✨ **Fast to deploy** (can ship this week)

---

## 🛠️ Implementation Plan (Strategy #2)

### **Phase 1: Database Setup**

```sql
-- New table for email aliases
CREATE TABLE IF NOT EXISTS user_email_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    alias_email TEXT UNIQUE NOT NULL,
    oauth_provider TEXT,  -- 'google', 'microsoft365', etc.
    is_verified BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    metadata TEXT,  -- JSON for additional data
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index for fast lookups
CREATE INDEX idx_aliases_email ON user_email_aliases(alias_email);
CREATE INDEX idx_aliases_user ON user_email_aliases(user_id);
```

### **Phase 2: Helper Functions**

```python
def get_user_id_by_email(email: str) -> Optional[int]:
    """
    Get user ID from email (checks both users table and aliases)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check main users table first
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    if user:
        return user['id']
    
    # Check aliases table
    cursor.execute('SELECT user_id FROM user_email_aliases WHERE alias_email = ?', (email,))
    alias = cursor.fetchone()
    if alias:
        return alias['user_id']
    
    conn.close()
    return None

def add_email_alias(user_id: int, email: str, provider: str) -> bool:
    """
    Link a new email to existing user account
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_email_aliases 
            (user_id, alias_email, oauth_provider, is_verified)
            VALUES (?, ?, ?, 1)
        ''', (user_id, email, provider))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # Email already exists as alias
        return False

def get_all_emails_for_user(user_id: int) -> List[dict]:
    """
    Get primary email + all aliases for a user
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get primary email
    cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    emails = [{
        'email': user['email'],
        'is_primary': True,
        'provider': 'primary'
    }]
    
    # Get aliases
    cursor.execute('''
        SELECT alias_email, oauth_provider, created_at, last_used
        FROM user_email_aliases 
        WHERE user_id = ?
    ''', (user_id,))
    
    for alias in cursor.fetchall():
        emails.append({
            'email': alias['alias_email'],
            'is_primary': False,
            'provider': alias['oauth_provider'],
            'created_at': alias['created_at'],
            'last_used': alias['last_used']
        })
    
    conn.close()
    return emails
```

### **Phase 3: Update OAuth Routes**

```python
# In google_auth_routes.py and microsoft_auth_routes.py

@google_auth_bp.route('/callback')
def google_callback():
    # ... existing OAuth flow ...
    
    email = profile.get('email')
    
    # NEW: Check both users and aliases
    user_id = get_user_id_by_email(email)
    
    if user_id:
        # Existing user (via primary or alias)
        print(f'✅ Found user via email lookup: {user_id}')
    else:
        # Check if this is a linking request
        linking_user_id = session.get('linking_user_id')
        
        if linking_user_id:
            # User is linking a new account
            add_email_alias(linking_user_id, email, 'google')
            user_id = linking_user_id
            print(f'🔗 Linked {email} to user {user_id}')
        else:
            # New user - create account
            username = email.split('@')[0]
            cursor.execute(
                'INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
                (username, email, 'oauth_google', 'user')
            )
            user_id = cursor.lastrowid
            print(f'🆕 Created new user: {user_id}')
    
    # Store OAuth tokens under found/created user_id
    # ... rest of flow ...
```

### **Phase 4: New API Endpoints**

```python
# New file: AI_infrastructure/routes/account_linking_routes.py

from flask import Blueprint, jsonify, request, session
import jwt as pyjwt

account_linking_bp = Blueprint('account_linking', __name__, url_prefix='/api/account')

@account_linking_bp.route('/link/google', methods=['POST'])
def link_google_account():
    """
    Initiate linking Google account to current user
    
    POST /api/account/link/google
    Headers: Authorization: Bearer <jwt_token>
    
    Returns: Redirect URL for Google OAuth
    """
    # Get current user from JWT
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_data = pyjwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
    user_id = user_data['user_id']
    
    # Store user_id in session for callback
    session['linking_user_id'] = user_id
    session['linking_provider'] = 'google'
    
    # Generate OAuth URL
    state = secrets.token_urlsafe(32)
    session['google_oauth_state'] = state
    
    auth_url = f"{GOOGLE_AUTH_URL}?client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&response_type=code&scope={SCOPES}&state={state}"
    
    return jsonify({
        'success': True,
        'auth_url': auth_url,
        'message': 'Redirect user to this URL to link Google account'
    })

@account_linking_bp.route('/link/microsoft', methods=['POST'])
def link_microsoft_account():
    """Similar to link_google_account"""
    # ... same pattern for M365 ...

@account_linking_bp.route('/emails', methods=['GET'])
def get_linked_emails():
    """
    Get all emails for current user
    
    GET /api/account/emails
    Headers: Authorization: Bearer <jwt_token>
    
    Returns: List of primary + alias emails
    """
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_data = pyjwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
    user_id = user_data['user_id']
    
    emails = get_all_emails_for_user(user_id)
    
    return jsonify({
        'success': True,
        'emails': emails
    })

@account_linking_bp.route('/emails/<int:alias_id>', methods=['DELETE'])
def unlink_email(alias_id):
    """
    Remove email alias
    
    DELETE /api/account/emails/<alias_id>
    Headers: Authorization: Bearer <jwt_token>
    """
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_data = pyjwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
    user_id = user_data['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify this alias belongs to the user
    cursor.execute('''
        DELETE FROM user_email_aliases 
        WHERE id = ? AND user_id = ?
    ''', (alias_id, user_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Email unlinked'})
```

### **Phase 5: Frontend UI**

```javascript
// Add to business-ai-platform-v2.html

const AccountManager = {
    async getLinkedEmails() {
        const response = await fetch('/api/account/emails', {
            headers: UserAuth.getAuthHeaders()
        });
        return await response.json();
    },
    
    async linkGoogleAccount() {
        const response = await fetch('/api/account/link/google', {
            method: 'POST',
            headers: UserAuth.getAuthHeaders()
        });
        const data = await response.json();
        
        if (data.success) {
            // Redirect to Google OAuth
            window.location.href = data.auth_url;
        }
    },
    
    async linkMicrosoftAccount() {
        const response = await fetch('/api/account/link/microsoft', {
            method: 'POST',
            headers: UserAuth.getAuthHeaders()
        });
        const data = await response.json();
        
        if (data.success) {
            window.location.href = data.auth_url;
        }
    },
    
    async unlinkEmail(aliasId) {
        if (!confirm('Are you sure you want to unlink this email?')) return;
        
        await fetch(`/api/account/emails/${aliasId}`, {
            method: 'DELETE',
            headers: UserAuth.getAuthHeaders()
        });
        
        // Refresh list
        this.loadLinkedEmails();
    },
    
    async loadLinkedEmails() {
        const data = await this.getLinkedEmails();
        const container = document.getElementById('linkedEmailsList');
        
        container.innerHTML = data.emails.map(email => `
            <div class="email-item ${email.is_primary ? 'primary' : ''}">
                <span class="email">${email.email}</span>
                <span class="provider">${email.provider}</span>
                ${email.is_primary ? 
                    '<span class="badge">Primary</span>' : 
                    `<button onclick="AccountManager.unlinkEmail(${email.id})">Unlink</button>`
                }
            </div>
        `).join('');
    }
};
```

---

## 📋 User Experience Flow

### **Scenario: User Links Second Email**

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: User Already Logged In                                 │
└─────────────────────────────────────────────────────────────────┘

User: john@gmail.com (logged in)
User ID: 123
Has threads, data, settings

┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: User Goes to Settings → Link Account                   │
└─────────────────────────────────────────────────────────────────┘

UI shows:
  Primary Email: john@gmail.com ✓
  
  [Link Google Account]
  [Link Microsoft 365]

User clicks: [Link Microsoft 365]

┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Backend Prepares Linking                               │
└─────────────────────────────────────────────────────────────────┘

POST /api/account/link/microsoft
  Headers: Authorization: Bearer <user_123_token>
  
Backend:
  - Extracts user_id: 123 from JWT
  - Stores: session['linking_user_id'] = 123
  - Returns M365 OAuth URL

┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: OAuth Flow                                             │
└─────────────────────────────────────────────────────────────────┘

User redirected to Microsoft login
User signs in: john@company.com
Microsoft redirects back

┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Callback Handles Linking                               │
└─────────────────────────────────────────────────────────────────┘

/api/auth/microsoft/callback

Backend checks:
  - session['linking_user_id'] exists? YES: 123
  - This is a LINKING request (not new login)
  
Actions:
  1. Get email from M365: john@company.com
  2. Check if email already exists: NO
  3. Insert alias:
     user_email_aliases:
       user_id: 123
       alias_email: john@company.com
       oauth_provider: microsoft365
  4. Store M365 OAuth tokens under user_id: 123
  5. Redirect back to settings page

┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: User Sees Updated Settings                             │
└─────────────────────────────────────────────────────────────────┘

UI now shows:
  Primary Email: john@gmail.com ✓
  Linked Emails:
    - john@company.com (Microsoft 365) [Unlink]
  
  [Link Another Account]

┌─────────────────────────────────────────────────────────────────┐
│ STEP 7: User Logs Out & Back In with Linked Email              │
└─────────────────────────────────────────────────────────────────┘

User logs out
User clicks: Sign in with Microsoft 365
User signs in: john@company.com

Backend:
  1. Check users table: WHERE email = 'john@company.com'
     → NOT FOUND
  2. Check aliases: WHERE alias_email = 'john@company.com'
     → FOUND! user_id: 123
  3. Generate JWT with user_id: 123
  4. Redirect to dashboard

Result:
  ✅ User sees ALL their old data
  ✅ Same user_id (123)
  ✅ Chat threads preserved
  ✅ Settings intact
  ✅ Can use EITHER email to login
```

---

## ✨ Why This Strategy Wins

### **1. Backwards Compatible**
```
Existing users: Work unchanged (email in users table)
New users: Work unchanged (email in users table)
Linked users: Additional aliases in new table
```

### **2. Clear Data Ownership**
```
users.email = PRIMARY email (always)
user_email_aliases = SECONDARY emails (links to primary)
```

### **3. Easy to Query**
```sql
-- Get user ID from ANY email (one function)
SELECT id FROM users WHERE email = ?
UNION
SELECT user_id FROM user_email_aliases WHERE alias_email = ?
```

### **4. Flexible**
```
User can:
  - Add multiple aliases
  - Remove aliases (except primary)
  - Change primary email (update users.email)
  - See all linked accounts
```

### **5. Minimal Risk**
```
- No changes to existing users table structure
- New table is isolated
- Rollback is easy (drop table)
- No data migration needed
```

---

## 🚀 Implementation Timeline

**Week 1:**
- Create user_email_aliases table
- Add helper functions
- Update OAuth callback logic

**Week 2:**
- Create account linking API endpoints
- Add backend logout endpoint
- Test linking flow

**Week 3:**
- Build frontend UI (settings page)
- Add "Link Account" buttons
- Display linked emails

**Week 4:**
- User testing
- Bug fixes
- Documentation

**Total:** 4 weeks to fully implement Strategy #2

---

## 🎯 Alternative: Quick Win (Interim Solution)

If we need something **immediately**, we could do a **temporary fix**:

```python
# Just update OAuth callbacks to be smarter
# No new tables, no UI changes

def google_callback():
    email = get_email_from_google()
    
    # NEW: Check if email matches pattern
    base_email = extract_base_email(email)  # john@gmail.com → john
    
    # Look for existing user with similar email
    cursor.execute('''
        SELECT id FROM users 
        WHERE email LIKE ?
    ''', (f'{base_email}%',))
    
    # Use first match (risky but simple)
    user = cursor.fetchone()
    if user:
        user_id = user['id']
    else:
        # Create new user
        user_id = create_new_user(email)
```

**Pros:** 5 minutes to implement  
**Cons:** Unreliable, security risk, not recommended

---

## 📝 Final Recommendation

**Implement Strategy #2: Account Aliases**

**Timeline:** 4 weeks  
**Risk:** Low  
**Complexity:** Medium  
**Value:** High

This gives you:
- ✅ Multiple emails per user
- ✅ Clear primary account
- ✅ Easy to understand and maintain
- ✅ Room to grow (can migrate to Strategy #3 later)

**Start now, ship in 4 weeks! 🚀**

