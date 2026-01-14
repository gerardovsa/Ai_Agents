# Supabase Credentials Integration - Complete Guide

**Date:** November 30, 2025  
**Project:** AI_agents - VSA Veterinary Alerts Module  
**Purpose:** Secure storage and retrieval of Supabase API credentials

---

## 📋 Overview

This integration adds Supabase credentials to the `user_platform_credentials` table, enabling the VSA Veterinary Alerts module to securely access the SQL_Data_AI_UI_v5 Supabase database.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI_agents System                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Frontend Module (vsa-veterinary-alerts.js)                 │
│           │                                                   │
│           │ 1. Fetch credentials                             │
│           ↓                                                   │
│  Flask Endpoint (/api/credentials/supabase)                 │
│           │                                                   │
│           │ 2. Query database                                │
│           ↓                                                   │
│  user_platform_credentials table                            │
│  (ai_infrastructure schema)                                 │
│           │                                                   │
│           │ 3. Return anon_key + URL                         │
│           ↓                                                   │
│  Supabase JS Client (frontend)                              │
│           │                                                   │
│           │ 4. Connect to external DB                        │
│           ↓                                                   │
│  SQL_Data_AI_UI_v5 Supabase Database                        │
│  (wuwmvtslltqhaycyukxk.supabase.co)                         │
│           │                                                   │
│           │ 5. Query veterinary_calls table                  │
│           ↓                                                   │
│  Display Alerts & Follow-ups                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation Steps

### Step 1: Insert Credentials into Database

1. **Open the SQL script:**
   ```
   c:\Users\gpoli\GIT\AI_agents\SUPABASE_CREDENTIALS_INSERT.sql
   ```

2. **Open Supabase SQL Editor:**
   - URL: https://supabase.com/dashboard/project/ryoicrdifiqhqpsnjmdo/editor
   - Or navigate to: Your Project → SQL Editor

3. **Execute the SQL script:**
   - Copy the entire contents of `SUPABASE_CREDENTIALS_INSERT.sql`
   - Paste into SQL Editor
   - Click "Run"

4. **Verify insertion:**
   - The script includes a verification query at the end
   - You should see output showing the inserted credentials
   - Expected columns: id, user_id, platform, credential_type, credentials, etc.

### Step 2: Register Flask Blueprint

Add the credentials endpoint to your Flask app:

**File:** `AI_infrastructure/flask_app.py`

```python
# Add import at the top
from routes.supabase_credentials_routes import supabase_credentials_bp

# Register blueprint (add with other blueprints)
app.register_blueprint(supabase_credentials_bp, url_prefix='/api/credentials')
```

**Verification:**
```powershell
# Restart Flask server
BISTART

# Wait for server to start, then test endpoint
curl http://localhost:5001/api/credentials/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "supabase_credentials_routes",
  "endpoints": [
    "GET /api/credentials/supabase",
    "GET /api/credentials/supabase/backend",
    "GET /api/credentials/supabase/test",
    "GET /api/credentials/platforms",
    "GET /api/credentials/health"
  ]
}
```

### Step 3: Update Frontend Module (Optional)

The VSA module (`vsa-veterinary-alerts.js`) currently uses hardcoded credentials. To use database credentials instead:

**File:** `UI/modules_external/vsa-veterinary-alerts/vsa-veterinary-alerts.js`

**Replace lines 14-15 with:**
```javascript
// Supabase connection (fetched from backend)
supabaseUrl: null,
supabaseKey: null,
```

**Add new method after `onDashboardLoad`:**
```javascript
async fetchCredentials() {
    try {
        const response = await fetch('/api/credentials/supabase');
        const data = await response.json();
        
        if (data.success) {
            this.state.supabaseUrl = data.credentials.url;
            this.state.supabaseKey = data.credentials.anon_key;
            this.log.info('Credentials fetched from backend');
        } else {
            throw new Error(data.error || 'Failed to fetch credentials');
        }
    } catch (error) {
        this.log.error('Failed to fetch credentials:', error);
        // Fallback to hardcoded (temporary)
        this.state.supabaseUrl = 'https://wuwmvtslltqhaycyukxk.supabase.co';
        this.state.supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';
    }
},
```

**Update `onDashboardLoad` method:**
```javascript
async onDashboardLoad(utilities) {
    Object.assign(this, utilities);
    this.log.info('VSA Alerts Dashboard loading...');
    
    try {
        this.container = this.dom.getContainer();
        if (!this.container) {
            throw new Error('Dashboard container not found');
        }
        
        // Fetch credentials from backend
        await this.fetchCredentials();
        
        // Initialize Supabase client
        await this.initializeSupabase();
        
        // ... rest of method
    }
}
```

---

## 🔧 Available Tools

### 1. Python Script: `get_supabase_credentials.py`

**Purpose:** Retrieve credentials from database (for testing/development)

**Usage:**
```powershell
# Show formatted summary
python get_supabase_credentials.py

# Get credentials for specific user
python get_supabase_credentials.py 2

# Output as JSON
python get_supabase_credentials.py --json

# Get credentials for user 2 as JSON
python get_supabase_credentials.py 2 --json
```

**Example Output:**
```
============================================================
SUPABASE CREDENTIALS SUMMARY
============================================================

✅ Credentials found for user_id=1

Project Details:
  URL:        https://wuwmvtslltqhaycyukxk.supabase.co
  Project ID: wuwmvtslltqhaycyukxk
  Region:     ap-southeast-2

Database Connection:
  Host:     db.wuwmvtslltqhaycyukxk.supabase.co
  Port:     5432
  Database: postgres
  User:     postgres

API Keys:
  Anon Key:    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (length: 204)
  Service Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (length: 214)

============================================================
```

### 2. Flask API Endpoints

#### GET `/api/credentials/supabase`
**Purpose:** Get frontend-safe credentials (anon_key only)

**Example:**
```javascript
fetch('/api/credentials/supabase')
  .then(res => res.json())
  .then(data => {
    console.log(data.credentials.url);
    console.log(data.credentials.anon_key);
  });
```

**Response:**
```json
{
  "success": true,
  "credentials": {
    "url": "https://wuwmvtslltqhaycyukxk.supabase.co",
    "anon_key": "eyJhbGciOiJ...",
    "project_id": "wuwmvtslltqhaycyukxk",
    "region": "ap-southeast-2"
  }
}
```

#### GET `/api/credentials/supabase/backend`
**Purpose:** Get full credentials including service_key (server-side only)

**⚠️ Security Warning:** Only use from backend code, not frontend!

#### GET `/api/credentials/supabase/test`
**Purpose:** Test Supabase connection using stored credentials

**Example:**
```powershell
curl http://localhost:5001/api/credentials/supabase/test
```

**Response:**
```json
{
  "success": true,
  "message": "Supabase connection successful",
  "url": "https://wuwmvtslltqhaycyukxk.supabase.co",
  "project_id": "wuwmvtslltqhaycyukxk",
  "test_query": "SELECT id FROM veterinary_calls LIMIT 1",
  "records_found": 1
}
```

#### GET `/api/credentials/platforms`
**Purpose:** List all available platform credentials for user

**Example:**
```powershell
curl http://localhost:5001/api/credentials/platforms?user_id=1
```

**Response:**
```json
{
  "success": true,
  "platforms": [
    {
      "platform": "supabase",
      "credential_type": "api_keys",
      "is_active": true,
      "metadata": {
        "purpose": "VSA Veterinary Alerts Module",
        "database": "veterinary_calls"
      },
      "updated_at": "2025-11-30T10:30:00"
    }
  ],
  "count": 1
}
```

---

## 🔐 Security Considerations

### Credential Types

1. **Anon Key (Public):**
   - Safe to use in frontend JavaScript
   - Has row-level security (RLS) restrictions
   - Used for: `vsa-veterinary-alerts.js` module

2. **Service Key (Private):**
   - **NEVER** expose to frontend
   - Bypasses RLS restrictions
   - Used for: Backend operations only

### Best Practices

1. ✅ **DO:** Fetch credentials from `/api/credentials/supabase` in frontend
2. ✅ **DO:** Use anon_key for client-side Supabase connections
3. ✅ **DO:** Store service_key only in `user_platform_credentials` table
4. ❌ **DON'T:** Hardcode credentials in JavaScript files
5. ❌ **DON'T:** Commit credentials to version control
6. ❌ **DON'T:** Expose service_key to frontend

### Database Table Structure

```sql
ai_infrastructure.user_platform_credentials
├── id (serial) PRIMARY KEY
├── user_id (integer) - Links to users table
├── platform (text) - e.g., 'supabase', 'google', 'microsoft'
├── credential_type (text) - e.g., 'api_keys', 'oauth_token'
├── credential_key (text) - Key identifier
├── credential_value (text) - Primary credential (service_key)
├── credentials (jsonb) - Full credential object
├── metadata (jsonb) - Additional info
├── is_active (boolean) - Enable/disable credentials
├── created_at (timestamp)
└── updated_at (timestamp)
```

---

## 🧪 Testing

### Test 1: Verify Database Insert

```powershell
python get_supabase_credentials.py
```

Expected: Shows credential summary with all fields populated

### Test 2: Test Flask Endpoint

```powershell
# Start server
BISTART

# Wait 10 seconds, then test
curl http://localhost:5001/api/credentials/health
```

Expected: Returns health check with list of endpoints

### Test 3: Test Credential Retrieval

```powershell
curl http://localhost:5001/api/credentials/supabase
```

Expected: Returns JSON with url, anon_key, project_id, region

### Test 4: Test Supabase Connection

```powershell
curl http://localhost:5001/api/credentials/supabase/test
```

Expected: Returns success message with record count

### Test 5: Test Frontend Integration

1. Open browser: http://localhost:5001
2. Open DevTools Console
3. Navigate to VSA Alerts module
4. Check Console for "Credentials fetched from backend"
5. Verify data loads successfully

---

## 🐛 Troubleshooting

### Issue: "Credentials not found"

**Solution:**
1. Verify SQL script was executed: `python get_supabase_credentials.py`
2. Check user_id matches: Default is 1
3. Verify platform name: Should be 'supabase' (lowercase)
4. Check is_active flag: Should be true

### Issue: "Failed to connect to Supabase"

**Solution:**
1. Test connection manually: `curl http://localhost:5001/api/credentials/supabase/test`
2. Check internet connection
3. Verify Supabase project is active
4. Check URL is correct: https://wuwmvtslltqhaycyukxk.supabase.co

### Issue: "Endpoint not found"

**Solution:**
1. Verify blueprint is registered in flask_app.py
2. Restart Flask server: BISTART
3. Check endpoint URL includes `/api/credentials` prefix
4. Verify Flask logs for any errors

### Issue: Module still using hardcoded credentials

**Solution:**
1. Update `vsa-veterinary-alerts.js` as shown in Step 3
2. Clear browser cache: Ctrl+Shift+R (hard refresh)
3. Check DevTools Console for credential fetch logs
4. Verify Flask endpoint is responding

---

## 📁 Files Created

1. **SUPABASE_CREDENTIALS_INSERT.sql**
   - SQL script to insert credentials into database
   - Location: `c:\Users\gpoli\GIT\AI_agents\`

2. **get_supabase_credentials.py**
   - Python utility to retrieve and test credentials
   - Location: `c:\Users\gpoli\GIT\AI_agents\`

3. **supabase_credentials_routes.py**
   - Flask API endpoints for credential retrieval
   - Location: `c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\routes\`

4. **SUPABASE_CREDENTIALS_COMPLETE.md** (this file)
   - Complete documentation
   - Location: `c:\Users\gpoli\GIT\AI_agents\`

---

## ✅ Success Checklist

- [ ] SQL script executed successfully
- [ ] Credentials visible in `python get_supabase_credentials.py`
- [ ] Flask blueprint registered in flask_app.py
- [ ] Flask server restarted (BISTART)
- [ ] Health endpoint responds: `/api/credentials/health`
- [ ] Supabase endpoint responds: `/api/credentials/supabase`
- [ ] Test endpoint succeeds: `/api/credentials/supabase/test`
- [ ] Frontend module updated (optional)
- [ ] VSA Alerts module loads successfully
- [ ] Data displays in dashboard

---

## 🔄 Next Steps

1. **Enable Authentication:**
   - Add JWT token verification to endpoints
   - Require authentication for credential access

2. **Add More Platforms:**
   - Use same pattern for Google, Microsoft, Shopify, etc.
   - Each platform gets own entry in `user_platform_credentials`

3. **Implement Credential Rotation:**
   - Add endpoint to update credentials
   - Track credential version history

4. **Add Audit Logging:**
   - Log all credential access
   - Track which modules use which credentials

---

**Status:** ✅ Complete  
**Last Updated:** November 30, 2025
