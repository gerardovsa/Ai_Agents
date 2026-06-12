# 🚀 Quick Start: Deploy to Render (Australia)

## ⚡ 3-Step Deployment

### Step 1: Run Deployment Wizard (2 minutes)

```powershell
cd C:\Users\gpoli\GIT\AI_agents
python deploy_australia.py
```

**This will:**
- ✅ Check all prerequisites  
- ✅ Verify Singapore region configured
- ✅ Extract environment variables to `render_env_vars.json`
- ✅ Guide next steps

---

### Step 2: Deploy via Render Dashboard (5 minutes)

1. **Go to:** https://dashboard.render.com
2. **Click:** "New +" → "Web Service"
3. **Connect:** `gerardovsa/AI_agents` repository
4. **Configure:**
   - **Branch:** `V2_clean`
   - **Region:** `Singapore` ⭐ **CRITICAL**
   - **Environment:** `Docker`
   - **Plan:** `Starter` ($7/month)
5. **Add environment variables** from `render_env_vars.json`:
   ```
   ANTHROPIC_API_KEY=sk-ant-xxxxx
   OPENAI_API_KEY=sk-xxxxx
   DEEPSEEK_API_KEY_1=sk-xxxxx
   MICROSOFT_CLIENT_ID=xxxxx
   MICROSOFT_CLIENT_SECRET=xxxxx
   GOOGLE_OAUTH_CLIENT_ID=xxxxx
   GOOGLE_OAUTH_CLIENT_SECRET=xxxxx
   SECRET_KEY=(generate new: python -c "import secrets; print(secrets.token_hex(32))")
   ```
6. **Click:** "Create Web Service"
7. **Wait:** 8-10 minutes for build

---

### Step 3: Update OAuth & Test (3 minutes)

```powershell
# Get your service URL (e.g., https://ai-agents-backend-xxxx.onrender.com)
$SERVICE_URL = "YOUR_RENDER_URL_HERE"

# Update OAuth redirect URLs
python Render_backend/update_oauth_redirects.py $SERVICE_URL

# Test deployment
python Render_backend/test_deployment.py $SERVICE_URL
```

**Manually update OAuth consoles:**

1. **Google Cloud Console:** https://console.cloud.google.com/apis/credentials
   - Add redirect: `https://ai-agents-backend-xxxx.onrender.com/api/auth/google/callback`

2. **Microsoft Azure Portal:** https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps
   - Add redirect: `https://ai-agents-backend-xxxx.onrender.com/api/auth/microsoft/callback`

---

## ✅ Done!

**Your service is now live:**
- 🌏 Region: Singapore (100-150ms from Australia)
- 🐳 Runtime: Docker + Python 3.11
- 🛠️ Tools: 564 loaded
- 💰 Cost: $7/month (Starter) or $0/month (Free after testing)

---

## 📊 Expected Results

### Build Time
- **Total:** 8-10 minutes
- **Docker build:** 5-7 minutes
- **Startup:** 30 seconds
- **Tool loading:** 10 seconds

### Performance
- **Latency (AU):** 100-150ms ✅
- **Health check:** <100ms
- **API calls:** 150-300ms

### Service URL
```
https://ai-agents-backend-xxxx.onrender.com
```

---

## 🔧 Troubleshooting

### Build Fails
```powershell
# Check logs
python Render_backend/fetch_logs.py srv-xxxxx
```

### Service Won't Start
- ✅ Verify PORT environment variable is set to 10000
- ✅ Check all required environment variables are set
- ✅ Review build logs for errors

### OAuth Not Working
- ✅ Update redirect URLs in Google/Microsoft consoles
- ✅ Match exact URL from Render (include https://)

---

## 💡 Pro Tips

### Cost Optimization
```powershell
# Downgrade to Free tier after testing
python Render_backend/downgrade_to_free.py srv-xxxxx
```

**Note:** Free tier spins down after 15 min inactivity (1-2 min cold start)

### Monitor Service
```powershell
# Real-time deployment monitoring
python Render_backend/monitor_deployment.py srv-xxxxx
```

### Test Latency
```powershell
# From Australia
curl -w "\nTime: %{time_total}s\n" https://your-service.onrender.com/health
```

**Expected:** 0.1-0.15 seconds (100-150ms)

---

## 📚 Full Documentation

- **Deployment Guide:** `Render_backend/AUSTRALIA_DOCKER_DEPLOYMENT.md`
- **Issue Analysis:** `Render_backend/DEPLOYMENT_ANALYSIS.md`
- **Fixes Applied:** `Render_backend/FIXES_APPLIED.md`

---

**Total Time:** ~15 minutes  
**Difficulty:** ⭐⭐☆☆☆ (Easy)  
**Status:** 🟢 Ready to deploy
