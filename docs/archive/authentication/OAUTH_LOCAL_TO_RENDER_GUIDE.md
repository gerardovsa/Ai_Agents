# 🚀 OAuth Setup for Local Testing → Render Deployment

## Your Journey

```
Phase 1: Local Testing (Today)
├── Flask on localhost:4000
├── Desktop app OAuth
├── Test all Google Tasks tools
└── Verify functionality ✅

Phase 2: Deploy to Render (Soon)
├── Flask on Render.com
├── Web application OAuth
├── Multi-user support
└── Remote access ✅
```

---

## 🎯 Setup Strategy: Create Both OAuth Types

### Option A: Quick Start (Desktop Only) - Test Today

**Setup Time:** 5 minutes  
**Use:** Test locally now, create Web OAuth later before deployment

**Steps:**
1. Create **Desktop app** OAuth
2. Download `credentials.json`
3. Test locally with `CHAT` command
4. Deploy to Render later
5. Create **Web application** OAuth before going live

---

### Option B: Complete Setup (Both Types) - Production Ready ✅ Recommended

**Setup Time:** 15 minutes  
**Use:** Test locally now + ready for Render deployment immediately

**Steps:**
1. Create **Desktop app** OAuth (for local testing)
2. Create **Web application** OAuth (for Render)
3. Configure Flask to support both
4. Test locally now
5. Deploy to Render when ready (no additional OAuth setup needed)

---

## 📝 Complete Setup Guide (Both OAuth Types)

### Step 1: Create Desktop App OAuth (Local Testing)

**In Google Cloud Console:**

1. Click **"Create Credentials"** → **"OAuth 2.0 Client ID"**
2. **Application type:** **"Desktop app"**
3. **Name:** `AI Agents - Local Development`
4. Click **"Create"**
5. Click **"Download JSON"**
6. Save as: `C:\Users\gpoli\GIT\AI_agents\credentials_desktop.json`

---

### Step 2: Create Web Application OAuth (Render Deployment)

**In Google Cloud Console (same page):**

1. Click **"Create Credentials"** → **"OAuth 2.0 Client ID"** again
2. **Application type:** **"Web application"**
3. **Name:** `AI Agents - Render Production`

4. **Authorized JavaScript origins:**
   ```
   http://localhost:4000
   https://your-app-name.onrender.com
   ```
   (Replace `your-app-name` with your Render service name)

5. **Authorized redirect URIs:**
   ```
   http://localhost:4000/oauth2callback
   https://your-app-name.onrender.com/oauth2callback
   ```

6. Click **"Create"**
7. Click **"Download JSON"**
8. Save as: `C:\Users\gpoli\GIT\AI_agents\credentials_web.json`

---

### Step 3: Update Environment Configuration

Add to `.env.master`:

```bash
# ==================== GOOGLE TASKS OAUTH ====================
# Desktop OAuth (for local development/testing)
GOOGLE_TASKS_CREDENTIALS_FILE_DESKTOP=C:\Users\gpoli\GIT\AI_agents\credentials_desktop.json
GOOGLE_TASKS_TOKEN_FILE_DESKTOP=C:\Users\gpoli\GIT\AI_agents\token_desktop.json

# Web OAuth (for Render production deployment)
GOOGLE_TASKS_CREDENTIALS_FILE_WEB=C:\Users\gpoli\GIT\AI_agents\credentials_web.json
GOOGLE_TASKS_TOKEN_FILE_WEB=C:\Users\gpoli\GIT\AI_agents\token_web.json

# Active mode: 'desktop' (local) or 'web' (deployed)
GOOGLE_TASKS_OAUTH_MODE=desktop

# OAuth scopes
GOOGLE_TASKS_SCOPES=https://www.googleapis.com/auth/tasks
```

---

### Step 4: Enhance google_tasks.py for Both Flows

Update the authentication logic:

```python
# google_workspace/google_tasks.py

import os
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pathlib import Path

def build_tasks_service():
    """
    Build Google Tasks API service with OAuth 2.0.
    Supports both desktop (local) and web (deployed) OAuth flows.
    """
    # Get OAuth mode from environment
    oauth_mode = os.getenv('GOOGLE_TASKS_OAUTH_MODE', 'desktop')
    
    print(f"🔑 Google Tasks OAuth Mode: {oauth_mode}")
    
    if oauth_mode == 'desktop':
        # Desktop OAuth (local development)
        return _build_tasks_service_desktop()
    elif oauth_mode == 'web':
        # Web OAuth (Render deployment)
        return _build_tasks_service_web()
    else:
        raise ValueError(f"Invalid GOOGLE_TASKS_OAUTH_MODE: {oauth_mode}. Use 'desktop' or 'web'.")


def _build_tasks_service_desktop():
    """Desktop app OAuth flow (opens local browser)"""
    
    credentials_file = os.getenv(
        'GOOGLE_TASKS_CREDENTIALS_FILE_DESKTOP',
        'credentials_desktop.json'
    )
    token_file = os.getenv(
        'GOOGLE_TASKS_TOKEN_FILE_DESKTOP',
        'token_desktop.json'
    )
    scopes = [os.getenv('GOOGLE_TASKS_SCOPES', 'https://www.googleapis.com/auth/tasks')]
    
    print(f"   Credentials: {credentials_file}")
    print(f"   Token: {token_file}")
    
    creds = None
    
    # Load existing token if available
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)
        print(f"   ✅ Loaded existing token")
    
    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print(f"   🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            print(f"   🌐 Starting OAuth flow (browser will open)...")
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, scopes
            )
            creds = flow.run_local_server(port=0)
            print(f"   ✅ OAuth completed!")
        
        # Save credentials for next time
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
            print(f"   💾 Saved token to {token_file}")
    
    # Build and return service
    service = build('tasks', 'v1', credentials=creds)
    print(f"   ✅ Google Tasks service ready")
    
    return service


def _build_tasks_service_web():
    """
    Web app OAuth flow (for deployed Render app).
    
    Note: This requires stored credentials from OAuth callback.
    See app.py for OAuth callback implementation.
    """
    
    # In web mode, credentials should be stored in database or session
    # For now, we'll use a file-based approach similar to desktop
    
    credentials_file = os.getenv(
        'GOOGLE_TASKS_CREDENTIALS_FILE_WEB',
        'credentials_web.json'
    )
    token_file = os.getenv(
        'GOOGLE_TASKS_TOKEN_FILE_WEB',
        'token_web.json'
    )
    scopes = [os.getenv('GOOGLE_TASKS_SCOPES', 'https://www.googleapis.com/auth/tasks')]
    
    print(f"   Credentials: {credentials_file}")
    print(f"   Token: {token_file}")
    
    creds = None
    
    # Load existing token
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)
        print(f"   ✅ Loaded existing token")
    else:
        print(f"   ❌ No token found. User needs to authenticate via web OAuth.")
        print(f"   👉 Visit: http://localhost:4000/oauth/tasks/start")
        raise FileNotFoundError(
            "Google Tasks authentication required. "
            "User must authenticate via /oauth/tasks/start endpoint."
        )
    
    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        print(f"   🔄 Refreshing expired token...")
        creds.refresh(Request())
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    
    # Build and return service
    service = build('tasks', 'v1', credentials=creds)
    print(f"   ✅ Google Tasks service ready")
    
    return service
```

---

### Step 5: Add OAuth Callback Routes to Flask (app.py)

Add these routes for web OAuth:

```python
# app.py - Add to your Flask app

from flask import session, redirect, url_for
from google_auth_oauthlib.flow import Flow
import json

# Configure Flask session secret
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-in-production')

@app.route('/oauth/tasks/start')
def oauth_tasks_start():
    """
    Start Google Tasks OAuth flow.
    Redirects user to Google consent screen.
    """
    try:
        credentials_file = os.getenv(
            'GOOGLE_TASKS_CREDENTIALS_FILE_WEB',
            'credentials_web.json'
        )
        
        # Get redirect URI from environment or construct from request
        redirect_uri = os.getenv(
            'GOOGLE_TASKS_OAUTH_REDIRECT_URI',
            url_for('oauth_tasks_callback', _external=True)
        )
        
        print(f"🔐 Starting OAuth flow...")
        print(f"   Credentials: {credentials_file}")
        print(f"   Redirect URI: {redirect_uri}")
        
        flow = Flow.from_client_secrets_file(
            credentials_file,
            scopes=['https://www.googleapis.com/auth/tasks'],
            redirect_uri=redirect_uri
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Force consent screen to get refresh token
        )
        
        # Store state in session for validation
        session['oauth_state'] = state
        
        print(f"   ✅ Redirecting to Google OAuth...")
        
        return redirect(authorization_url)
        
    except Exception as e:
        print(f"   ❌ OAuth start failed: {e}")
        return jsonify({
            'error': 'OAuth initialization failed',
            'details': str(e)
        }), 500


@app.route('/oauth2callback')
def oauth_tasks_callback():
    """
    Handle OAuth callback from Google.
    Exchanges authorization code for tokens.
    """
    try:
        credentials_file = os.getenv(
            'GOOGLE_TASKS_CREDENTIALS_FILE_WEB',
            'credentials_web.json'
        )
        
        token_file = os.getenv(
            'GOOGLE_TASKS_TOKEN_FILE_WEB',
            'token_web.json'
        )
        
        # Verify state
        state = session.get('oauth_state')
        if not state:
            return jsonify({'error': 'Invalid state'}), 400
        
        print(f"🔐 Processing OAuth callback...")
        
        flow = Flow.from_client_secrets_file(
            credentials_file,
            scopes=['https://www.googleapis.com/auth/tasks'],
            state=state,
            redirect_uri=url_for('oauth_tasks_callback', _external=True)
        )
        
        # Exchange authorization code for credentials
        flow.fetch_token(authorization_response=request.url)
        
        credentials = flow.credentials
        
        # Save credentials to file
        with open(token_file, 'w') as token:
            token.write(credentials.to_json())
        
        print(f"   ✅ OAuth completed! Token saved to {token_file}")
        
        # Clear session state
        session.pop('oauth_state', None)
        
        return jsonify({
            'success': True,
            'message': 'Google Tasks authentication successful!',
            'next_step': 'You can now use Google Tasks tools'
        })
        
    except Exception as e:
        print(f"   ❌ OAuth callback failed: {e}")
        return jsonify({
            'error': 'OAuth callback failed',
            'details': str(e)
        }), 500


@app.route('/oauth/tasks/status')
def oauth_tasks_status():
    """Check if Google Tasks OAuth is configured"""
    try:
        oauth_mode = os.getenv('GOOGLE_TASKS_OAUTH_MODE', 'desktop')
        
        if oauth_mode == 'desktop':
            token_file = os.getenv('GOOGLE_TASKS_TOKEN_FILE_DESKTOP', 'token_desktop.json')
        else:
            token_file = os.getenv('GOOGLE_TASKS_TOKEN_FILE_WEB', 'token_web.json')
        
        token_exists = os.path.exists(token_file)
        
        return jsonify({
            'oauth_mode': oauth_mode,
            'authenticated': token_exists,
            'token_file': token_file,
            'message': 'Authenticated' if token_exists else 'Authentication required'
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Status check failed',
            'details': str(e)
        }), 500
```

---

### Step 6: Test Locally (Desktop OAuth)

**Before deployment, test with Desktop OAuth:**

```powershell
cd C:\Users\gpoli\GIT\AI_agents

# Ensure desktop mode
$env:GOOGLE_TASKS_OAUTH_MODE = "desktop"

# Test authentication
python -c "from google_workspace.google_tasks import google_tasks_list_task_lists; print(google_tasks_list_task_lists())"
```

**What happens:**
1. Browser opens automatically
2. Sign in with Google
3. Grant permission
4. `token_desktop.json` created ✅
5. Task lists displayed

**Test via CHAT:**
```powershell
BISTART
Start-Sleep -Seconds 15
CHAT List my Google Tasks
CHAT Create a task "Test before Render deployment"
```

---

### Step 7: Deploy to Render

**Update `.env` on Render:**

```bash
# Switch to web OAuth mode
GOOGLE_TASKS_OAUTH_MODE=web

# Web OAuth files (upload to Render)
GOOGLE_TASKS_CREDENTIALS_FILE_WEB=/opt/render/project/src/credentials_web.json

# Flask secret (for sessions)
FLASK_SECRET_KEY=your-secure-random-key-here

# Render app URL
RENDER_APP_URL=https://your-app-name.onrender.com
GOOGLE_TASKS_OAUTH_REDIRECT_URI=https://your-app-name.onrender.com/oauth2callback
```

**First user authentication on Render:**
1. User visits: `https://your-app-name.onrender.com/oauth/tasks/start`
2. Redirects to Google OAuth
3. User signs in and grants permission
4. Redirects to `/oauth2callback`
5. Token saved on Render
6. Google Tasks tools now work! ✅

---

## 🎯 Quick Decision Matrix

| Scenario | OAuth Type | Setup Now |
|----------|-----------|-----------|
| **Test locally today** | Desktop app | ✅ Yes - Quick (5 min) |
| **Deploy to Render soon** | Web application | ✅ Yes - Setup now (15 min) |
| **Production ready** | Both | ✅ Recommended |

---

## 📋 Your Action Plan

### Today (Local Testing):

1. **Create Desktop app OAuth** (5 min)
   - Google Cloud Console → Desktop app
   - Download → `credentials_desktop.json`
   - Test with `CHAT` command

### Before Render Deployment:

2. **Create Web application OAuth** (10 min)
   - Google Cloud Console → Web application
   - Add redirect URIs
   - Download → `credentials_web.json`

3. **Add OAuth routes to app.py** (included above)
   - `/oauth/tasks/start`
   - `/oauth2callback`
   - `/oauth/tasks/status`

4. **Update google_tasks.py** (included above)
   - Support both desktop and web flows
   - Mode switching via environment variable

5. **Test locally in web mode** (optional)
   ```powershell
   $env:GOOGLE_TASKS_OAUTH_MODE = "web"
   # Visit: http://localhost:4000/oauth/tasks/start
   ```

6. **Deploy to Render**
   - Set `GOOGLE_TASKS_OAUTH_MODE=web`
   - Upload `credentials_web.json`
   - First user visits `/oauth/tasks/start`

---

## 🚀 Minimal Setup (If You Want to Deploy Fast)

**Option: Use Desktop OAuth on Render (Hack)**

You *could* use Desktop OAuth even on Render for single-user testing:
- Set `GOOGLE_TASKS_OAUTH_MODE=desktop`
- Authenticate locally (creates `token_desktop.json`)
- Upload `token_desktop.json` to Render
- Works for **single user only**
- ❌ Not recommended for production
- ✅ OK for quick testing

**Proper Production Setup:**
- Use Web application OAuth
- Add OAuth callback routes
- Support multiple users
- Token storage per user

---

## 📝 Summary

**Your Path:**

```
Now (Today):
├── Create Desktop OAuth ✅
├── Download credentials_desktop.json
├── Test locally: CHAT List my Google Tasks
└── Verify all tools work

Soon (Before Render):
├── Create Web OAuth ✅
├── Download credentials_web.json
├── Add OAuth routes to app.py
├── Update google_tasks.py
└── Deploy to Render

On Render:
├── Set GOOGLE_TASKS_OAUTH_MODE=web
├── Upload credentials_web.json
├── User visits /oauth/tasks/start
└── Production ready! ✅
```

Would you like me to create the updated `google_tasks.py` and `app.py` files with both OAuth flows implemented?

---

**Last Updated:** October 28, 2025  
**Status:** Ready for local testing → Render deployment
