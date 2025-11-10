# Deploy AI Agents to Singapore via Render Dashboard

Since the Render API for creating services requires complex configuration, **the easiest method is to use the Render Dashboard with your existing `render.yaml` file.**

## ✅ Quick Deployment Steps (5 minutes)

### 1. Open Render Dashboard
Go to: https://dashboard.render.com

### 2. Create New Web Service
- Click **"New +"** button (top right)
- Select **"Web Service"**

### 3. Connect Repository
- Select **"Build and deploy from a Git repository"**
- Click **"Connect"** next to `gerardovsa/Ai_Agents`
- If not connected, click **"Configure account"** and authorize GitHub

### 4. Configure Service
Use these **EXACT settings**:

| Setting | Value |
|---------|-------|
| **Name** | `ai-agents-backend-singapore` |
| **Region** | **Singapore** 🇸🇬 (CRITICAL!) |
| **Branch** | `V2_clean` |
| **Root Directory** | `.` (leave blank or use dot) |
| **Environment** | **Docker** |
| **Dockerfile Path** | `./Dockerfile` |
| **Docker Context** | `./` |
| **Plan** | **Starter** ($7/month) |
| **Auto-Deploy** | **Yes** (enabled) |

### 5. Advanced Settings

Click **"Advanced"** and configure:

**Build Settings:**
- Docker Command: (leave default)
- Docker Build Context: `./`

**Health Check:**
- Health Check Path: `/health`

**Environment Variables:**
Add these immediately (before first deploy):

```
PYTHONUNBUFFERED=1
RENDER=true
ENVIRONMENT=production
PORT=10000

# AI Provider Keys (REQUIRED!)
ANTHROPIC_API_KEY=sk-ant-...  ← Add your key
OPENAI_API_KEY=sk-...         ← Add your key
DEEPSEEK_API_KEY_1=sk-...     ← Add your key

# Microsoft OAuth (REQUIRED!)
MICROSOFT_CLIENT_ID=...       ← Add your ID
MICROSOFT_CLIENT_SECRET=...   ← Add your secret
MICROSOFT_TENANT_ID=common

# Google OAuth (Optional)
GOOGLE_CLIENT_ID=...          ← Add if using OAuth
GOOGLE_CLIENT_SECRET=...      ← Add if using OAuth
```

### 6. Create Service
- Click **"Create Web Service"**
- Wait 5-10 minutes for Docker build

---

## 📊 Monitor Deployment

### Check Build Progress
```powershell
cd c:\Users\gpoli\GIT\AI_agents\Render_backend
python render_cli.py list  # Find new service ID
python render_cli.py logs srv-XXXXXX  # Replace with actual ID
```

### Check Deploy Status
```powershell
python render_cli.py status srv-XXXXXX
python render_cli.py deploys srv-XXXXXX
```

---

## ✅ Post-Deployment Tasks

### 1. Test Health Endpoint
```powershell
# Replace URL with your actual service URL
curl https://ai-agents-backend-singapore.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "tools_loaded": 594,
  "timestamp": "2025-11-08T..."
}
```

### 2. Update OAuth Redirect URLs

**Google Cloud Console:**
https://console.cloud.google.com/apis/credentials

Add authorized redirect URI:
```
https://ai-agents-backend-singapore.onrender.com/api/auth/google/callback
```

**Microsoft Azure Portal:**
https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps

Add redirect URI:
```
https://ai-agents-backend-singapore.onrender.com/api/auth/microsoft/callback
```

### 3. Test Full Functionality
- Open UI and connect to new backend
- Test AI chat functionality
- Test tool execution
- Verify latency improvement

### 4. Delete Old Oregon Service
Once verified working:
```powershell
cd c:\Users\gpoli\GIT\AI_agents\Render_backend
python delete_oregon_service.py
```

---

## 🎯 Performance Comparison

| Metric | Oregon (Old) | Singapore (New) | Improvement |
|--------|-------------|-----------------|-------------|
| Latency (Australia) | 200-250ms | 100-150ms | **50% faster** |
| Environment | Python | Docker | **Code execution sandbox** |
| Region Distance | 12,000 km | 6,000 km | **2x closer** |

---

## 🔧 Troubleshooting

### Build Failed
Check logs:
```powershell
python render_cli.py logs srv-XXXXXX
```

Common issues:
- Missing Dockerfile → Check `Dockerfile` exists in root
- Wrong branch → Ensure `V2_clean` branch exists
- Dependencies fail → Check `requirements.txt`

### Health Check Failed
1. Check PORT is set to 10000
2. Verify `/health` endpoint exists in `flask_app.py`
3. Check logs for startup errors

### Tools Not Loading
1. Verify all environment variables are set
2. Check API keys are valid
3. Review logs for import errors

---

## 📝 Service URLs

After deployment, you'll get:
- **Service URL**: `https://ai-agents-backend-singapore.onrender.com`
- **Service ID**: `srv-XXXXXX` (from dashboard)
- **Logs**: Available in dashboard and via CLI

Save these details for future reference!

---

## 🚀 Alternative: Use render.yaml (Blueprint)

If you prefer automated deployment:

1. Go to: https://dashboard.render.com/select-repo
2. Select `gerardovsa/Ai_Agents`
3. Render will detect `render.yaml`
4. Click **"Apply"**
5. Service will be created automatically with all settings from `render.yaml`

⚠️ **Note**: You still need to add API keys manually in the dashboard after creation!

---

**Status**: Ready to deploy ✅  
**Time Required**: 5-10 minutes  
**Cost**: $7/month (Starter plan)
