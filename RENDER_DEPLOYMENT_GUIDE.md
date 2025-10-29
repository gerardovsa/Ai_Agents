# 🚀 Deploy AI Agents to Render.com - Complete Guide

**Project:** AI Agents V2 (564 Tools, Flask Backend)  
**Target:** Render.com Hosting  
**Status:** Ready to Deploy ✅

---

## 📋 Prerequisites Checklist

- ✅ RENDER_API_KEY configured in .env.master
- ✅ 15 existing services on Render (account connected)
- ✅ V2 branch created locally with all changes
- ✅ 548 files committed (262,090 lines)
- ❌ GitHub repository needs to be created
- ❌ V2 branch needs to be pushed

---

## 🎯 Quick Deploy Steps (20 minutes)

### **Step 1: Create GitHub Repository** (2 minutes)

1. Go to: https://github.com/new
2. **Repository name:** `AI_agents`
3. **Description:** "AI Agent Platform with 564 Tools - V2"
4. **Visibility:** Private (recommended - contains sensitive config)
5. **DON'T** initialize with README (we have local code)
6. Click **Create repository**

### **Step 2: Push Code to GitHub** (3 minutes)

```powershell
cd C:\Users\gpoli\GIT\AI_agents

# Push V2 branch (your active work)
git push -u origin V2

# Push main branch (original version)
git push -u origin main

# Set V2 as default branch (optional)
# Go to: Settings → Branches → Default branch → Change to V2
```

**Authentication:** 
- If prompted, use Personal Access Token (not password)
- Generate at: https://github.com/settings/tokens
- Permissions needed: `repo` (full control)

### **Step 3: Connect Repository to Render** (5 minutes)

1. Go to: https://dashboard.render.com
2. Click **New +** → **Web Service**
3. Click **Configure account** (if not connected yet)
4. Select **gerardovsa/AI_agents** from your repositories
5. Click **Connect**

### **Step 4: Configure Service** (5 minutes)

On the "Create Web Service" page, use these **EXACT** settings:

| Setting | Value | Notes |
|---------|-------|-------|
| **Name** | `ai-agents-v2` | Will become URL |
| **Region** | Oregon (US West) | Lowest latency |
| **Branch** | `V2` | Your active development branch |
| **Root Directory** | `AI_infrastructure` | Where flask_app.py lives |
| **Runtime** | Python 3 | Auto-detected |
| **Build Command** | `pip install -r requirements.txt` | Install dependencies |
| **Start Command** | `python flask_app.py` | Start Flask server |
| **Plan** | Free | $0/month, good for testing |

**Advanced Settings:**
- **Health Check Path:** `/health`
- **Auto-Deploy:** ✅ Yes (deploy on push)

### **Step 5: Add Environment Variables** (5 minutes)

Click **Advanced** → **Add Environment Variable** and add these:

#### **REQUIRED - Flask Core** ✅
```bash
FLASK_ENV=production
PORT=10000
SECRET_KEY=<generate-32-random-chars>
PYTHONPATH=/opt/render/project/src
```

**Generate SECRET_KEY:**
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

#### **REQUIRED - AI Providers** ✅
Get these from your `.env.master` file:
```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=sk-...
```

#### **REQUIRED - Microsoft OAuth** ✅
```bash
MICROSOFT_CLIENT_ID=<from Azure Portal>
MICROSOFT_CLIENT_SECRET=<from Azure Portal>
MICROSOFT_TENANT_ID=common
```

#### **REQUIRED - Google OAuth** ✅
```bash
GOOGLE_CLIENT_ID=<from Google Console>
GOOGLE_CLIENT_SECRET=<from Google Console>
```

#### **OPTIONAL - Additional Tools** (Add as needed)
```bash
STRIPE_SECRET_KEY=sk_...
WOOCOMMERCE_URL=https://yourstore.com
WOOCOMMERCE_KEY=ck_...
WOOCOMMERCE_SECRET=cs_...
SLACK_BOT_TOKEN=xoxb-...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
```

**💡 TIP:** Copy values from `C:\Users\gpoli\GIT\AI_agents\.env.master`

### **Step 6: Deploy!** (1 minute)

1. Click **Create Web Service**
2. Render will:
   - Clone your repository
   - Install dependencies (~3 minutes)
   - Start Flask server (~1 minute)
   - Assign URL: `https://ai-agents-v2.onrender.com`

**Monitor progress** at: https://dashboard.render.com

---

## 🔍 Post-Deployment Verification (10 minutes)

### **Check 1: Build Succeeded**
Look for in logs:
```
Successfully installed flask anthropic openai...
Starting Flask application...
✅ 564 tools loaded successfully
🚀 Flask server running on port 10000
```

### **Check 2: Health Endpoint**
Visit: `https://ai-agents-v2.onrender.com/health`

**Expected response:**
```json
{
  "status": "healthy",
  "tools_loaded": 564,
  "version": "2.0.0"
}
```

### **Check 3: Update OAuth Redirect URLs**

#### **Microsoft Azure Portal**
1. Go to: https://portal.azure.com
2. Navigate to: Azure Active Directory → App registrations → Your app
3. Click **Authentication** → **Add a platform** → **Web**
4. Add redirect URI: `https://ai-agents-v2.onrender.com/api/auth/microsoft/callback`
5. Click **Save**

#### **Google Cloud Console**
1. Go to: https://console.cloud.google.com
2. Navigate to: APIs & Services → Credentials → OAuth 2.0 Client IDs
3. Click your client → **Authorized redirect URIs**
4. Add: `https://ai-agents-v2.onrender.com/api/auth/google/callback`
5. Click **Save**

### **Check 4: Test OAuth Login**
1. Visit: `https://ai-agents-v2.onrender.com`
2. Click **Sign in with Microsoft 365**
3. Verify redirect works
4. Click **Sign in with Google**
5. Verify redirect works

---

## 🐛 Troubleshooting

### **Error: Build Failed**

**Check logs for:**
- Missing `requirements.txt` → Should be at `AI_infrastructure/requirements.txt`
- Python version mismatch → Render uses Python 3.12 by default
- Module not found → Add to requirements.txt

**Fix:**
```bash
# Create requirements.txt if missing
cd AI_infrastructure
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Add requirements.txt"
git push
```

### **Error: Application Failed to Start**

**Common causes:**
- Port binding issue → Flask must use `os.getenv('PORT', 10000)`
- Database path error → Use absolute paths with `os.path.join()`
- Missing environment variables → Check Render dashboard

**Check flask_app.py:**
```python
# Correct port binding
port = int(os.getenv('PORT', 10000))
app.run(host='0.0.0.0', port=port)
```

### **Error: OAuth Redirects Fail**

**Symptoms:** "redirect_uri_mismatch" error

**Solution:**
1. Check redirect URIs in Azure Portal and Google Console
2. Must EXACTLY match: `https://ai-agents-v2.onrender.com/api/auth/{provider}/callback`
3. No trailing slashes
4. HTTPS required (not HTTP)

### **Error: 564 Tools Not Loading**

**Check:**
1. `tools/` directory exists in repository
2. `tools/registry.py` is present
3. Tool schemas in `tools/schemas/` are valid JSON
4. Logs show "Loading tools from registry..."

**Fix:**
```python
# Verify in Python console
from tools.registry import ToolRegistry
registry = ToolRegistry()
print(f"Loaded {len(registry.tools)} tools")
```

---

## 📊 Expected Results

### **Successful Deployment Shows:**

```
Build Logs:
✅ Installing dependencies from requirements.txt
✅ 156 packages installed
✅ Build completed in 3m 42s

Runtime Logs:
✅ Starting Flask application
✅ Loading tool registry...
✅ Loaded 564 tools from 35 implementations
✅ 19 API endpoints registered
✅ OAuth managers initialized (Microsoft, Google)
✅ Flask server running on 0.0.0.0:10000
```

### **Service URL:**
`https://ai-agents-v2.onrender.com`

### **API Endpoints Available:**
- `/health` - Health check
- `/api/auth/microsoft/login` - Microsoft OAuth start
- `/api/auth/microsoft/callback` - Microsoft OAuth callback
- `/api/auth/google/login` - Google OAuth start
- `/api/auth/google/callback` - Google OAuth callback
- `/api/auth/profile` - Get user profile
- `/api/agent/chat` - AI agent conversation
- `/api/tools/list` - List all 564 tools

---

## 🔧 Advanced Configuration

### **Use PostgreSQL Instead of SQLite**

Render's free tier has ephemeral storage (resets on redeploy). For persistent data:

1. Create PostgreSQL database:
   - Dashboard → New + → PostgreSQL
   - Name: `ai-agents-db`
   - Plan: Free (1GB)

2. Add environment variable:
   ```bash
   DATABASE_URL=<connection-string-from-render>
   ```

3. Update `auth_routes.py`:
   ```python
   # Use PostgreSQL if DATABASE_URL exists
   import os
   db_url = os.getenv('DATABASE_URL')
   if db_url:
       # Use SQLAlchemy with PostgreSQL
       engine = create_engine(db_url)
   else:
       # Fallback to SQLite
       db_path = 'ai_infrastructure.db'
   ```

### **Enable CORS for Frontend**

If using separate frontend domain:

```python
# In flask_app.py
from flask_cors import CORS

CORS(app, origins=[
    'https://yourdomain.com',
    'https://ai-agents-v2.onrender.com'
])
```

### **Custom Domain**

1. Render Dashboard → Your service → Settings → Custom Domain
2. Add: `api.yourdomain.com`
3. Update DNS: Add CNAME pointing to Render
4. Update OAuth redirect URIs to use custom domain

---

## 📱 Monitoring & Logs

### **View Logs:**
1. Dashboard → Your service → Logs
2. Filter by level: Info, Warning, Error
3. Download logs for debugging

### **Metrics:**
- CPU usage (free tier: limited)
- Memory usage (512MB on free tier)
- Request latency
- Uptime (free tier: spins down after 15 min idle)

### **Alerts:**
- Dashboard → Your service → Settings → Notifications
- Email alerts for deploy failures, crashes

---

## 🎉 Success Checklist

- [ ] GitHub repository created at github.com/gerardovsa/AI_agents
- [ ] V2 and main branches pushed
- [ ] Render service connected to repository
- [ ] All environment variables added (15+ required)
- [ ] Build succeeded (logs show 564 tools loaded)
- [ ] Health endpoint returns 200 OK
- [ ] OAuth redirect URIs updated in Azure and Google
- [ ] Microsoft 365 login works
- [ ] Google login works
- [ ] AI agent responds to queries
- [ ] Tool execution works with credentials

---

## 📞 Support Resources

- **Render Status:** https://status.render.com
- **Render Docs:** https://render.com/docs
- **GitHub Issues:** https://github.com/gerardovsa/AI_agents/issues
- **Your Email:** gerardo@vetsuccessacademy.com

---

**Last Updated:** October 29, 2025  
**Version:** 2.0.0  
**Status:** Ready for Deployment ✅
