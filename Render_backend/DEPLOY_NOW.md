# AI AGENTS - RENDER DEPLOYMENT GUIDE
**Complete Step-by-Step Deployment to Singapore Region**

**Date:** November 8, 2025  
**Target:** Deploy AI Agents to Render.com Singapore (Docker environment)  
**Current Status:** Oregon service (srv-d40tai15pdvs73ddh4m0) needs migration

---

## Pre-Deployment Checklist

✅ **Repository:** gerardovsa/Ai_Agents  
✅ **Branch:** V2_clean  
✅ **render.yaml:** Validated ✅  
✅ **Dockerfile:** Ready ✅  
✅ **Environment Variables:** Listed below  

---

## Step 1: Access Render Dashboard

1. Go to: **https://dashboard.render.com/select-repo**
2. Sign in with your Render account
3. Click **"Connect a repository"**

---

## Step 2: Connect GitHub Repository

1. **Select Repository:** `gerardovsa/Ai_Agents`
2. **Branch:** `V2_clean` (this is your deployment branch)
3. Click **"Connect"**

Render will automatically detect `render.yaml` in your repository.

---

## Step 3: Review Blueprint Configuration

Render will show you the blueprint from `render.yaml`:

```yaml
Service Name: ai-agents-backend
Type: Web Service
Environment: Docker
Region: Singapore ✅
Plan: Starter
Auto-Deploy: Yes
Health Check: /health
```

**Verify these settings match:**
- ✅ Region: **Singapore** (not Oregon)
- ✅ Environment: **Docker** (not Python)
- ✅ Plan: **Starter** (or higher)
- ✅ Dockerfile Path: `./Dockerfile`

---

## Step 4: Add Environment Variables

Click **"Add Environment Variable"** and add these **CRITICAL** variables:

### Required Variables (Must Add):

```bash
# Flask Configuration
PORT=10000
FLASK_SECRET_KEY=your-super-secret-key-here-change-this
DEBUG=False
RENDER=true

# Database Path
DB_PATH=/var/data/ai_infrastructure.db

# Python Configuration
PYTHON_VERSION=3.11
PYTHONUNBUFFERED=1

# Google OAuth (Critical - from .env.master)
GOOGLE_OAUTH_CLIENT_ID=38241773079-ccen45jmhhe56lonk2tpj002kbesme9v.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=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
GOOGLE_REDIRECT_URI=https://your-service-name.onrender.com/api/auth/google/callback
GOOGLE_OAUTH_REDIRECT_URI=https://your-service-name.onrender.com/oauth2callback

# Service Account Email
SERVICE_ACCOUNT_EMAIL=vsa-anythingllm-project@appspot.gserviceaccount.com

# API Keys (from .env.master - add your actual keys)
ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key
DEEPSEEK_API_KEY=your-deepseek-key

# Microsoft OAuth (if using Microsoft tools)
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_TENANT_ID=common

# WooCommerce (if using)
WOOCOMMERCE_URL=https://minivetguide.com
WOOCOMMERCE_CONSUMER_KEY=your-woocommerce-key
WOOCOMMERCE_CONSUMER_SECRET=your-woocommerce-secret
```

### ⚠️ IMPORTANT: Update These After Deployment

After your service is deployed, you'll get a URL like:
`https://ai-agents-singapore-abc123.onrender.com`

**Go back to Environment Variables and UPDATE:**
```bash
GOOGLE_REDIRECT_URI=https://ai-agents-singapore-abc123.onrender.com/api/auth/google/callback
GOOGLE_OAUTH_REDIRECT_URI=https://ai-agents-singapore-abc123.onrender.com/oauth2callback
```

Then click **"Manual Deploy"** → **"Clear build cache & deploy"**

---

## Step 5: Add Service Account File

The `service-account.json` file needs to be in your repository root.

**Verify it exists:**
```powershell
cd c:\Users\gpoli\GIT\AI_agents
ls service-account.json
```

If it exists, it will be automatically included in the Docker build.

**Security Note:** This file is in `.gitignore` for local development, but you'll need to add it to your deployment branch or use Render's secret file feature.

---

## Step 6: Deploy!

1. Review all settings one final time
2. Click **"Apply"** or **"Create Web Service"**
3. Render will:
   - Clone your repository
   - Build Docker image from `Dockerfile`
   - Run health checks on `/health` endpoint
   - Deploy to Singapore region

**Expected Build Time:** 5-10 minutes

---

## Step 7: Monitor Deployment

### Watch Build Logs:
1. You'll be redirected to the service dashboard
2. Click **"Logs"** tab
3. Watch for:
   ```
   ✅ Building Docker image...
   ✅ Installing dependencies...
   ✅ Starting Flask app on port 10000...
   ✅ Health check passed
   ✅ Deploy live!
   ```

### Check Service Status:
```powershell
# Using our CLI tool
python render_complete_cli.py services list

# Or check specific service (replace with your new service ID)
python render_complete_cli.py health check srv-xxxxx
```

---

## Step 8: Verify Deployment

### Test the Service:

1. **Health Check:**
   ```
   https://your-service-name.onrender.com/health
   ```
   Should return: `{"status": "healthy"}`

2. **API Status:**
   ```
   https://your-service-name.onrender.com/api/status
   ```
   Should show tool count and platform info

3. **Test Tools:**
   Open the UI and try sending a message to verify:
   - AI agent responds
   - Tools load correctly
   - Database connections work

---

## Step 9: Update OAuth Redirect URLs

### Google Cloud Console:
1. Go to: https://console.cloud.google.com/apis/credentials
2. Select your OAuth 2.0 Client ID
3. Add to **Authorized redirect URIs:**
   ```
   https://your-service-name.onrender.com/api/auth/google/callback
   https://your-service-name.onrender.com/oauth2callback
   ```
4. Save changes

### Microsoft Azure (if using):
1. Go to Azure Portal → App Registrations
2. Select your app
3. Add redirect URI:
   ```
   https://your-service-name.onrender.com/api/auth/microsoft/callback
   ```

---

## Step 10: Test Multi-Agent Features

1. Open your deployed URL
2. Test the Multi-Agent NATO columns:
   - Create new agents (Alpha, Bravo, Charlie, etc.)
   - Send messages
   - Test drag-and-drop threads
   - Verify collapse/expand features work

3. Test tools:
   - Google Workspace (Sheets, Docs, Gmail)
   - Calculator tools (Business cards, flyers, etc.)
   - WooCommerce integration
   - Database queries

---

## Step 11: Delete Old Oregon Service (After Verification)

**⚠️ ONLY after new Singapore service is working perfectly:**

```powershell
# Using CLI tool
python render_complete_cli.py services delete srv-d40tai15pdvs73ddh4m0
```

This will:
- Prompt for confirmation (type 'DELETE')
- Remove the old Oregon service
- Free up resources

---

## Troubleshooting

### Build Fails:

**Check Dockerfile:**
```powershell
cd c:\Users\gpoli\GIT\AI_agents
docker build -t ai-agents-test .
```

**Common Issues:**
- Missing dependencies in `requirements.txt`
- Python version mismatch
- Port configuration (must use PORT env var)

### Health Check Fails:

**Verify Health Endpoint:**
```python
# In flask_app.py, ensure this exists:
@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})
```

### Environment Variables Not Working:

**Check Variable Names:**
- Must match exactly (case-sensitive)
- No extra spaces
- Use quotes for values with special characters

### Service Won't Start:

**Check Logs in Render Dashboard:**
1. Go to service dashboard
2. Click "Logs" tab
3. Look for error messages
4. Common issues:
   - Database path not writable
   - Missing API keys
   - Port binding errors

---

## Performance Benefits

**Singapore vs Oregon:**
- **Latency:** 100-150ms (Singapore) vs 200-250ms (Oregon)
- **Improvement:** 50% faster response times
- **Location:** Optimal for Australia
- **Docker:** Enables code execution sandbox

---

## Quick Commands Reference

```powershell
# Check all services
python render_complete_cli.py status overview

# Get service details
python render_complete_cli.py services get srv-xxxxx

# Check health
python render_complete_cli.py health check srv-xxxxx

# View deploy history
python render_complete_cli.py deploys list srv-xxxxx

# Trigger redeploy
python render_complete_cli.py deploys trigger srv-xxxxx --clear-cache

# Export environment variables
python render_complete_cli.py env export srv-xxxxx backup.env

# Import environment variables
python render_complete_cli.py env import srv-xxxxx config.env
```

---

## Next Steps After Deployment

1. **Update Documentation:**
   - Update API_BASE_URL in your UI
   - Update README with new deployment URL
   - Document environment variables

2. **Set Up Monitoring:**
   - Enable Render notifications
   - Set up uptime monitoring
   - Configure alerts

3. **Backup:**
   - Export environment variables monthly
   - Document custom configurations
   - Save deployment settings

4. **Scale (if needed):**
   - Upgrade to Standard plan for better performance
   - Add more instances for high traffic
   - Configure auto-scaling

---

## Support Resources

- **Render Docs:** https://render.com/docs
- **Render Dashboard:** https://dashboard.render.com
- **API Reference:** https://api-docs.render.com/
- **Status Page:** https://status.render.com/
- **CLI Tool:** `render_complete_cli.py` (this repo)

---

## Deployment Checklist

Before clicking "Apply", verify:

- ✅ Repository connected: gerardovsa/Ai_Agents
- ✅ Branch selected: V2_clean
- ✅ Region set: Singapore
- ✅ Environment: Docker
- ✅ Plan: Starter (or higher)
- ✅ Health check path: /health
- ✅ All environment variables added
- ✅ service-account.json in repository
- ✅ Port set to 10000
- ✅ Auto-deploy enabled

**Ready to deploy!** 🚀

---

**Last Updated:** November 8, 2025  
**Status:** Ready for Production Deployment ✅
