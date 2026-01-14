# Render.com Authentication Issue - Diagnosis & Fix

## Problem Statement

**Environment**: Render.com (production deployment)  
**Symptom**: Users appear "not connected or authenticated"  
**Status**: JWT_SECRET is correctly configured ✅  
**Impact**: Authentication works locally but fails on Render.com

---

## Environment Variables Status ✅

All required variables are set on Render.com:

```bash
JWT_SECRET=7466add577aefb38e7ab6c849d7742d89ccf10f53eddb04ae470c1451142158d
SECRET_KEY=7466add577aefb38e7ab6c849d7742d89ccf10f53eddb04ae470c1451142158d
SUPABASE_URL=https://ryoicrdifiqhqpsnjmdo.supabase.co
SUPABASE_DB_URL=postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@...
MICROSOFT_CLIENT_ID=324f7fef-50ac-4948-9f34-5f95b03ad818
MICROSOFT_REDIRECT_URI=https://ai-agents-backend-singapore.onrender.com/api/auth/microsoft/callback
```

So the problem is **NOT** missing environment variables.

---

## Actual Root Causes (Most Likely)

### 1. **Frontend Served from Different Origin** ⚠️

**Issue**: Your backend is on Render.com, but where is your frontend served from?

| Scenario | Frontend URL | Backend URL | Problem |
|----------|--------------|-------------|---------|
| ❌ **Separate Domains** | `file:///C:/Users/...` or `http://localhost:5001` | `https://ai-agents-backend-singapore.onrender.com` | CORS blocks cookie/localStorage |
| ❌ **GitHub Pages** | `https://yourusername.github.io` | `https://ai-agents-backend-singapore.onrender.com` | Cross-origin token storage fails |
| ✅ **Same Domain** | `https://ai-agents-backend-singapore.onrender.com` | `https://ai-agents-backend-singapore.onrender.com` | Works correctly |

**Check**: How are you accessing the UI on Render.com?
- Opening local HTML file? ❌
- Accessing via Render URL? ✅

---

### 2. **OAuth Redirect URI Mismatch** ⚠️

**Current Render Config**:
```bash
MICROSOFT_REDIRECT_URI=https://ai-agents-backend-singapore.onrender.com/api/auth/microsoft/callback
```

**Check**: Is this EXACT URL registered in your Microsoft Azure AD app?

Go to [Azure Portal](https://portal.azure.com/) → App Registrations → Your App → Authentication:
- ✅ Redirect URI should be: `https://ai-agents-backend-singapore.onrender.com/api/auth/microsoft/callback`
- ✅ Type: Web
- ✅ ID tokens: Enabled

---

### 3. **Token Storage After OAuth Redirect** ⚠️

**The OAuth Flow**:
```
1. User clicks "Login with Microsoft"
2. Redirect to Microsoft → User authorizes
3. Microsoft redirects to: /api/auth/microsoft/callback?code=...
4. Backend creates JWT token
5. Backend redirects to frontend with token in URL: /?token=...
6. Frontend extracts token from URL
7. Frontend stores in localStorage
8. Frontend makes API calls with token
```

**Potential Failure Point**: Step 5-7 might fail if:
- Redirect URL is wrong
- Frontend can't parse token from URL
- localStorage is blocked (cross-origin)

---

### 4. **Static File Serving on Render** ⚠️

**Issue**: Render might not be serving your `UI/business-ai-platform-v2.html` file correctly.

**Check your Render configuration**:

#### Option A: Serve Static Files from Flask
```python
# flask_app.py (your current setup)
@app.route('/')
def index():
    return send_from_directory('../UI', 'business-ai-platform-v2.html')
```

#### Option B: Separate Static Site
Deploy frontend separately:
- Render Static Site service
- Netlify
- Vercel
- GitHub Pages

---

## Diagnostic Steps

### Step 1: Check Render Logs

Go to Render Dashboard → Your Service → Logs

Look for:
```
✅ Token created and stored in sessions table
✅ Token verified successfully  
✅ User authenticated
❌ Token not found in database
❌ Token expired
❌ 401 UNAUTHORIZED
```

### Step 2: Test Backend API Directly

```bash
# Get login URL
curl https://ai-agents-backend-singapore.onrender.com/api/auth/microsoft/login

# Should return redirect URL to Microsoft
```

### Step 3: Check Token Flow

Open browser DevTools (F12) → Console:

```javascript
// After login, check if token is stored
console.log('Token:', localStorage.getItem('authToken'));

// Check if token is being sent in requests
console.log('UserAuth.token:', window.UserAuth?.token);
```

### Step 4: Verify Database

Check Supabase directly:

```sql
-- Check if user sessions exist
SELECT * FROM ai_infrastructure.user_sessions 
WHERE user_id = 14 
ORDER BY created_at DESC 
LIMIT 5;

-- Check if tokens are being created
SELECT COUNT(*) FROM ai_infrastructure.user_sessions;
```

---

## Most Likely Solutions

### Solution 1: Serve Frontend from Same Domain (RECOMMENDED)

**Current Setup** (if using file:// protocol):
```
Frontend: file:///C:/Users/gpoli/GIT/AI_agents/UI/business-ai-platform-v2.html
Backend:  https://ai-agents-backend-singapore.onrender.com
❌ Result: Cross-origin issues, localStorage blocked
```

**Fixed Setup**:
```
Frontend: https://ai-agents-backend-singapore.onrender.com/
Backend:  https://ai-agents-backend-singapore.onrender.com/api/...
✅ Result: Same origin, everything works
```

**How to Fix**:

Ensure your Flask app serves the HTML:

```python
# flask_app.py
@app.route('/')
def index():
    """Serve main application page"""
    return send_from_directory('../UI', 'business-ai-platform-v2.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS, images)"""
    return send_from_directory('../UI', path)
```

---

### Solution 2: Fix CORS for Cross-Origin Setup

If you MUST serve frontend from different domain:

```python
# flask_app.py
from flask_cors import CORS

CORS(app, 
    origins=[
        'http://localhost:5001',
        'https://ai-agents-backend-singapore.onrender.com',
        'https://your-frontend-domain.com'  # Add your frontend domain
    ],
    supports_credentials=True,
    allow_headers=['Content-Type', 'Authorization'],
    expose_headers=['Content-Type', 'Authorization']
)
```

**Frontend**: Update API base URL

```javascript
// UI/business-ai-platform-v2.html
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5001' 
    : 'https://ai-agents-backend-singapore.onrender.com';
```

---

### Solution 3: Fix OAuth Redirect

**Update your Microsoft auth callback**:

```python
# AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py
@microsoft_auth_bp.route('/callback', methods=['GET'])
def microsoft_callback():
    # ... existing code ...
    
    # Generate JWT token
    token = generate_jwt_token(...)
    
    # CRITICAL: Redirect to frontend with token
    frontend_url = os.getenv('FRONTEND_URL', 'https://ai-agents-backend-singapore.onrender.com')
    redirect_url = f"{frontend_url}/?token={token}"
    
    return redirect(redirect_url)
```

**Add to Render environment variables**:
```
FRONTEND_URL=https://ai-agents-backend-singapore.onrender.com
```

---

## Quick Test

1. **Test backend health**:
   ```
   https://ai-agents-backend-singapore.onrender.com/health
   ```
   Should return `{"status": "healthy"}`

2. **Test OAuth initiation**:
   ```
   https://ai-agents-backend-singapore.onrender.com/api/auth/microsoft/login
   ```
   Should redirect to Microsoft

3. **Access frontend**:
   ```
   https://ai-agents-backend-singapore.onrender.com/
   ```
   Should load your HTML

4. **After login, check localStorage**:
   ```javascript
   // Browser Console (F12)
   localStorage.getItem('authToken')
   ```
   Should show JWT token

---

## Next Steps

**Tell me**:
1. How are you accessing the frontend on Render.com?
   - Via Render URL? (Good ✅)
   - Via local file? (Bad ❌)
   - Via different domain? (Needs CORS fix)

2. What do you see in Render logs when you try to login?

3. Does `https://ai-agents-backend-singapore.onrender.com/health` work?

4. Does `https://ai-agents-backend-singapore.onrender.com/` serve your HTML?

Once I know these answers, I can give you the exact fix.

---

## Summary

✅ JWT_SECRET is configured  
✅ Environment variables are correct  
⚠️ **Likely Issue**: Frontend not served from same origin as backend  
🔧 **Quick Fix**: Access via `https://ai-agents-backend-singapore.onrender.com/` instead of local file

