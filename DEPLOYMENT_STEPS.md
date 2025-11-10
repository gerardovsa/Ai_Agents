# AI Agents - Render.com Deployment Steps
**Date**: November 8, 2025  
**Branch**: v3 (pushed to GitHub)  
**Status**: Ready to Deploy

---

## ✅ COMPLETED STEPS

1. ✅ Updated `render.yaml` to deploy from `v3` branch
2. ✅ Committed changes (commit: 8186ed7)
3. ✅ Pushed v3 branch to GitHub
4. ✅ GitHub repository confirmed: https://github.com/gerardovsa/Ai_Agents.git

---

## 🚀 DEPLOYMENT INSTRUCTIONS

### Step 1: Access Render Dashboard
1. Go to: **https://dashboard.render.com**
2. Log in to your Render account
3. Click the **"New +"** button in the top right

---

### Step 2: Create New Blueprint Instance
1. Select **"Blueprint"** from the dropdown menu
2. Connect your GitHub account (if not already connected)
3. Select repository: **gerardovsa/Ai_Agents**
4. Render will automatically detect `render.yaml` in the repository

---

### Step 3: Configure Blueprint
1. **Branch**: Confirm it shows `v3` (from render.yaml)
2. **Service Name**: `ai-agents-backend`
3. **Region**: Singapore (from render.yaml)
4. **Plan**: Starter ($7/month) - You can downgrade to Free after testing
5. Click **"Apply"**

---

### Step 4: Add Environment Variables (CRITICAL)

**In the Render Dashboard, go to your service → Environment tab and add these secrets:**

#### Required Secrets:
```bash
# AI Provider Keys
ANTHROPIC_API_KEY=<your-anthropic-key>
OPENAI_API_KEY=<your-openai-key>
DEEPSEEK_API_KEY_1=<your-deepseek-key>

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=<your-google-client-id>
GOOGLE_OAUTH_CLIENT_SECRET=<your-google-client-secret>

# Microsoft OAuth
MICROSOFT_CLIENT_ID=<your-microsoft-client-id>
MICROSOFT_CLIENT_SECRET=<your-microsoft-client-secret>
MICROSOFT_TENANT_ID=common

# Flask Secret (Generate new one)
SECRET_KEY=<generate-with-command-below>

# Database (Optional - will auto-create)
DATABASE_URL=sqlite:////app/data/ai_infrastructure.db

# Optional Keys (if you use these services)
WOOCOMMERCE_API_KEY=<your-woo-key>
WOOCOMMERCE_API_SECRET=<your-woo-secret>
CLOUDFLARE_API_KEY=<your-cloudflare-key>
NGROK_AUTH_TOKEN=<your-ngrok-token>
```

#### Generate SECRET_KEY:
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

**Get your keys from `.env.master` file** (if you have it locally)

---

### Step 5: Monitor Deployment

**Once you click "Apply", Render will:**
1. Clone the v3 branch from GitHub
2. Build the Docker container using `Dockerfile`
3. Install dependencies from `requirements.txt`
4. Start the Flask app on port 10000
5. Run health checks on `/health` endpoint

**Deployment takes 3-5 minutes**

#### Watch Progress:
- Go to **Dashboard → Your Service → Logs**
- Look for: 
  - ✅ "Build succeeded"
  - ✅ "Deploy live"
  - ✅ Health check passing

---

### Step 6: Get Your Service URL

After deployment succeeds:
1. Your service URL will be: `https://ai-agents-backend-XXXX.onrender.com`
2. Copy this URL - you'll need it for OAuth setup

---

### Step 7: Update OAuth Redirect URIs

#### Google Cloud Console:
1. Go to: https://console.cloud.google.com/apis/credentials
2. Select your OAuth 2.0 Client ID
3. Add to **Authorized redirect URIs**:
   ```
   https://your-render-url.onrender.com/api/auth/google/callback
   ```
4. Save

#### Microsoft Azure Portal:
1. Go to: https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade
2. Select your app registration
3. Go to **Authentication** → **Platform configurations** → **Web**
4. Add redirect URI:
   ```
   https://your-render-url.onrender.com/api/auth/microsoft/callback
   ```
5. Save

---

### Step 8: Test Your Deployment

#### Test Health Endpoint:
```powershell
# Replace with your actual URL
curl https://your-render-url.onrender.com/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "service": "AI Agents Platform",
  "version": "3.0",
  "timestamp": "2025-11-08T..."
}
```

#### Test AI Chat:
```powershell
curl -X POST https://your-render-url.onrender.com/api/agent/chat `
  -H "Content-Type: application/json" `
  -d '{"message": "Hello, test message", "user_id": 1}'
```

---

### Step 9: Monitor Performance

#### Check Logs:
```powershell
# In Render Dashboard → Logs tab
# Look for:
# - "Flask app started on port 10000"
# - "Loaded XXX tools"
# - No errors in startup
```

#### Monitor Metrics:
- CPU usage
- Memory usage (should be under 512MB on Starter plan)
- Response times (should be ~100-200ms from Australia)

---

## 🔧 TROUBLESHOOTING

### Issue: Build Fails
**Check**: 
- Dockerfile syntax
- requirements.txt packages installable
- GitHub branch is `v3`

### Issue: Health Check Fails
**Check**:
- Port is set to `$PORT` (Render provides this)
- `/health` endpoint exists in flask_app.py
- No startup errors in logs

### Issue: Environment Variables Not Working
**Check**:
- All required secrets added in Render dashboard
- SECRET_KEY generated correctly
- API keys are valid and active

### Issue: OAuth Not Working
**Check**:
- Redirect URIs updated in Google/Microsoft consoles
- URLs match exactly (https://your-url.onrender.com)
- OAuth credentials added to Render environment

---

## 💰 COST OPTIMIZATION

### Current Plan: Starter ($7/month)
- Always on
- 512MB RAM
- 0.5 CPU

### Downgrade to Free (After Testing):
1. Go to **Dashboard → Your Service → Settings**
2. Click **Change Plan**
3. Select **Free**
4. Confirm

**Free Plan**:
- Spins down after 15 minutes of inactivity
- 750 hours/month free
- 1-2 minute cold start on first request
- Good for testing/development

---

## 📊 EXPECTED RESULTS

### Successful Deployment Shows:
- ✅ Service status: **Live**
- ✅ Health check: **Passing**
- ✅ Build time: **3-5 minutes**
- ✅ Memory usage: **~250-400MB**
- ✅ Response time: **100-200ms** (from Australia)

### Your Service Will Have:
- Public URL: `https://ai-agents-backend-XXXX.onrender.com`
- All 576 tools available
- Google/Microsoft OAuth login
- SQLite databases in `/app/data/`
- Auto-deploy on git push to v3 branch

---

## 📚 HELPFUL RESOURCES

### Render Documentation:
- Blueprint Guide: https://render.com/docs/blueprint-spec
- Environment Variables: https://render.com/docs/environment-variables
- Health Checks: https://render.com/docs/health-checks

### Project Documentation:
- `Render_backend/README.md` - Complete toolkit guide
- `Render_backend/DEPLOYMENT_GUIDE_FOR_AI.md` - Detailed deployment steps
- `RENDER_DEPLOYMENT_ANALYSIS_COMPLETE.md` - Full analysis document

---

## 🎯 QUICK CHECKLIST

Before you start:
- [ ] Logged into Render dashboard
- [ ] Have all API keys from `.env.master` ready
- [ ] Generated new SECRET_KEY
- [ ] Know your Google/Microsoft OAuth app credentials

During deployment:
- [ ] Selected correct repository (gerardovsa/Ai_Agents)
- [ ] Confirmed branch is v3
- [ ] Added all environment variables
- [ ] Deployment succeeded (no errors)

After deployment:
- [ ] Tested `/health` endpoint
- [ ] Updated OAuth redirect URIs
- [ ] Tested AI chat functionality
- [ ] Monitored logs for errors

---

## 🚀 READY TO DEPLOY!

Everything is prepared and pushed to GitHub. You can now:

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +" → "Blueprint"**
3. **Follow Steps 1-9 above**

**Estimated Total Time**: 10-15 minutes

Good luck with your deployment!
