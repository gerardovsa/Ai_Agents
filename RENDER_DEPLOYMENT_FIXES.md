# Render Deployment Fixes - November 24, 2025

**Critical Issues Found in Deployment Console Logs**

---

## 🔴 Issue #1: Duplicate API_BASE_URL Declaration

### Error
```javascript
account_profile.js:1 Uncaught SyntaxError: Identifier 'API_BASE_URL' has already been declared
(index):16213 Uncaught SyntaxError: Identifier 'API_BASE_URL' has already been declared
```

### Root Cause
`API_BASE_URL` is being declared twice:
1. In `account_profile.js` (line 1)
2. In main HTML file `(index)` (line 16213)

### Fix
Find and remove duplicate declaration:

```bash
# Search for all declarations
grep -rn "const API_BASE_URL" UI/
grep -rn "var API_BASE_URL" UI/
grep -rn "let API_BASE_URL" UI/
```

**Option 1: Use existing global**
```javascript
// In account_profile.js - DON'T redeclare
// const API_BASE_URL = ... ❌

// Use existing global
const API_BASE_URL = window.API_BASE_URL || '/api'; // ✅
```

**Option 2: Declare only once**
```javascript
// In main HTML <script> section (ONCE ONLY)
const API_BASE_URL = window.location.origin + '/api';

// In all other files - just use it
// NO const API_BASE_URL = ...
```

---

## 🔴 Issue #2: Supabase Connection Manager Failure

### Error
```javascript
supabase-connection-manager.js:88 Uncaught (in promise) TypeError: 
window.loadSupabaseConfig is not a function

❌ [Supabase] Cannot subscribe - client unavailable
❌ [Supabase] Reconnection failed (5 attempts)
```

### Root Cause
Connection manager tries to call `window.loadSupabaseConfig()` but function doesn't exist

### Fix

**Step 1: Check if loadSupabaseConfig exists**
```bash
grep -rn "loadSupabaseConfig" UI/
```

**Step 2: Ensure function is defined BEFORE connection manager loads**

In your main HTML file, add this BEFORE `supabase-connection-manager.js`:

```html
<script>
// Define loadSupabaseConfig function
window.loadSupabaseConfig = async function() {
    console.log('[Config] Loading Supabase config...');
    
    try {
        const response = await fetch('/api/auth/google/config');
        const data = await response.json();
        
        if (data.supabase_url && data.supabase_anon_key) {
            window.SUPABASE_URL = data.supabase_url;
            window.SUPABASE_ANON_KEY = data.supabase_anon_key;
            console.log('[Config] Supabase config loaded successfully');
            return true;
        } else {
            console.error('[Config] Invalid config response:', data);
            return false;
        }
    } catch (error) {
        console.error('[Config] Failed to load Supabase config:', error);
        return false;
    }
};

console.log('[Config] loadSupabaseConfig function registered');
</script>

<!-- NOW load connection manager -->
<script src="/UI/js/supabase-connection-manager.js"></script>
```

**Step 3: Verify script load order**

Correct order:
```html
<!-- 1. Load Supabase SDK first -->
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>

<!-- 2. Define config function -->
<script>
window.loadSupabaseConfig = async function() { /* ... */ };
</script>

<!-- 3. Load connection manager -->
<script src="/UI/js/supabase-connection-manager.js"></script>

<!-- 4. Load other modules that need Supabase -->
<script src="/UI/modules/..."></script>
```

---

## 🔴 Issue #3: 401 Unauthorized API Call

### Error
```javascript
localhost:5001/api/automation/list:1 Failed to load resource: 
the server responded with a status of 401 (UNAUTHORIZED)
```

### Root Cause
API call made before authentication complete, or auth token not sent

### Fix

**Option 1: Wait for authentication**
```javascript
// In automation-workflows.js (or wherever API is called)

// DON'T do this immediately on load:
// fetch('/api/automation/list') ❌

// DO this after auth ready:
async function loadWorkflows() {
    // Wait for auth
    if (!window.UserAuth || !window.UserAuth.isAuthenticated()) {
        console.log('[Automation] Waiting for authentication...');
        // Listen for auth event
        document.addEventListener('auth:ready', () => {
            fetchWorkflows();
        });
        return;
    }
    
    fetchWorkflows();
}

function fetchWorkflows() {
    fetch('/api/automation/list', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`, // Include token
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => console.log('Workflows:', data))
    .catch(err => console.error('Workflows error:', err));
}
```

**Option 2: Add auth token to all requests**
```javascript
// Create a helper function
window.authenticatedFetch = async function(url, options = {}) {
    const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
    
    if (!token) {
        throw new Error('Not authenticated');
    }
    
    options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
    
    return fetch(url, options);
};

// Use it everywhere:
window.authenticatedFetch('/api/automation/list')
    .then(res => res.json())
    .then(data => console.log(data))
    .catch(err => console.error(err));
```

---

## 🔧 Quick Fix Script

Run this to apply all fixes automatically:

```bash
cd c:\Users\gpoli\GIT\AI_agents
python scripts/testing/validate_render_deployment.py https://your-app.onrender.com
```

This will:
1. ✅ Detect duplicate API_BASE_URL declarations
2. ✅ Verify loadSupabaseConfig exists
3. ✅ Check Supabase connection status
4. ✅ Monitor for 401 auth errors
5. ✅ Validate WebSocket connections
6. ✅ Generate fix recommendations

---

## 📊 Validation Checklist

After applying fixes, verify:

- [ ] No "Identifier 'API_BASE_URL' has already been declared" errors
- [ ] `window.loadSupabaseConfig` is a function (check console)
- [ ] Supabase connection manager creates client successfully
- [ ] No "❌ [Supabase] Reconnection failed" messages
- [ ] API calls return 200 (not 401)
- [ ] Only 1 WebSocket connection established

---

## 🚀 Testing

### Local Testing
```powershell
# Start local server
BISTART

# Open browser to http://localhost:5001
# Open DevTools console
# Check for errors
```

### Render Testing
```powershell
# Install playwright
pip install playwright
playwright install chromium

# Run validation
python scripts/testing/validate_render_deployment.py https://your-app.onrender.com

# Check report
notepad data\render_validation_report.json
```

---

## 🔍 Root Cause Analysis

### Why These Errors Happen in Render (But Not Locally)

1. **Different script loading order**
   - Local: Synchronous file loading
   - Render: CDN delays, network latency

2. **Build/minification issues**
   - Duplicate declarations not caught in dev
   - Minifier doesn't deduplicate globals

3. **Environment variables**
   - Local: Direct .env access
   - Render: Needs async config fetch

4. **Auth token handling**
   - Local: Session persists
   - Render: Token must be explicitly included

---

## 📝 Prevention (For Future Deployments)

1. **Add pre-deployment validation**
   ```yaml
   # .github/workflows/pre-deploy.yml
   - name: Validate deployment
     run: python scripts/testing/validate_render_deployment.py http://localhost:5001
   ```

2. **Add ESLint rule**
   ```json
   {
     "rules": {
       "no-redeclare": ["error", { "builtinGlobals": true }]
     }
   }
   ```

3. **Add startup health check**
   ```javascript
   // In main HTML
   window.addEventListener('load', () => {
       const healthCheck = {
           api_base_url: typeof API_BASE_URL !== 'undefined',
           supabase_config: typeof window.loadSupabaseConfig === 'function',
           connection_manager: typeof window.connectionManager !== 'undefined',
           user_auth: typeof window.UserAuth !== 'undefined'
       };
       
       console.log('[Health Check]', healthCheck);
       
       const failures = Object.entries(healthCheck)
           .filter(([key, value]) => !value)
           .map(([key]) => key);
       
       if (failures.length > 0) {
           console.error('[Health Check] FAILED:', failures);
           alert(`Application health check failed: ${failures.join(', ')}`);
       }
   });
   ```

---

## 🎯 Expected Results After Fixes

**Console should show:**
```javascript
✅ [Config] loadSupabaseConfig function registered
✅ [Config] Supabase config loaded successfully
✅ [Supabase] Connection manager initialized
✅ [Supabase] Client created successfully
✅ [Supabase] Network listeners configured
✅ [Auth] User authenticated
✅ [API] /api/automation/list - 200 OK
✅ [Realtime] WebSocket connected
```

**Should NOT show:**
```javascript
❌ Identifier 'API_BASE_URL' has already been declared
❌ window.loadSupabaseConfig is not a function
❌ [Supabase] Cannot subscribe - client unavailable
❌ [Supabase] Reconnection failed
❌ 401 (UNAUTHORIZED)
```

---

**Last Updated:** November 24, 2025  
**Status:** Ready to apply fixes  
**Priority:** CRITICAL - Deploy ASAP
