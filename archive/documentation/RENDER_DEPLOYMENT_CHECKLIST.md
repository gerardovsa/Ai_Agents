# Render Deployment Checklist - Final Steps

## ✅ COMPLETED

### 1. Git Repository
- ✅ Branch: v5 (clean, no secrets)
- ✅ Latest commits pushed to origin/v5
- ✅ GitHub Actions: Docker build pipeline ready
- ✅ GHCR Image: ghcr.io/gerardovsa/ai_agents:latest

### 2. Environment Variables Updated
- ✅ Changed to use: vsa-anythingllm-project@appspot.gserviceaccount.com
- ✅ Google Workspace APIs enabled on this service account

## 🔄 PENDING - Verify Service Account Upload

### Singapore Service (srv-d4b2723uibrs73ff02t0)

Go to: https://dashboard.render.com/web/srv-d4b2723uibrs73ff02t0/env

**Check these environment variables exist:**

#### AI Provider Keys (Required)
```
✓ ANTHROPIC_API_KEY = sk-ant-api03-LMc3dxc3Q...
✓ OPENAI_API_KEY = sk-proj-ETANHl9WQ...
✓ DEEPSEEK_API_KEY_1 = sk-d276e3e75dfd4c20...
```

#### Google OAuth (Required)
```
✓ GOOGLE_OAUTH_CLIENT_ID = 38241773079-ccen45jmhhe56lonk2tpj002kbesme9v.apps.googleusercontent.com
✓ GOOGLE_OAUTH_CLIENT_SECRET = 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
✓ GOOGLE_REDIRECT_URI = https://ai-agents-backend-singapore.onrender.com/api/auth/google/callback
```

#### Google Service Account (CRITICAL - Check This!)
```
✓ SERVICE_ACCOUNT_EMAIL = vsa-anythingllm-project@appspot.gserviceaccount.com
✓ GOOGLE_APPLICATION_CREDENTIALS = /data/vsa-anythingllm-project-ab7c8caf8c47.json
✓ GOOGLE_CLOUD_PROJECT = vsa-anythingllm-project
```

#### Microsoft OAuth (Optional)
```
□ MICROSOFT_CLIENT_ID = [Get from Azure Portal]
□ MICROSOFT_CLIENT_SECRET = [Get from Azure Portal]
□ MICROSOFT_TENANT_ID = common
```

### 3. Upload Service Account JSON File

**CRITICAL**: The service account JSON file must be uploaded to the `/data` folder on Render.

#### Option A: Upload via Render Shell (Recommended)
1. Go to: https://dashboard.render.com/web/srv-d4b2723uibrs73ff02t0/shell
2. Click "Connect"
3. Run these commands:
   ```bash
   cd /data
   cat > vsa-anythingllm-project-[YOUR-KEY-ID].json << 'EOF'
   {
     "type": "service_account",
     "project_id": "vsa-anythingllm-project",
     "private_key_id": "[YOUR-PRIVATE-KEY-ID]",
     "private_key": "[YOUR-PRIVATE-KEY]",
     "client_email": "vsa-anythingllm-project@appspot.gserviceaccount.com",
     "client_id": "[YOUR-CLIENT-ID]",
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token",
     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/vsa-anythingllm-project%40appspot.gserviceaccount.com"
   }
   EOF
   
   # Verify file was created
   ls -lah vsa-anythingllm-project-ab7c8caf8c47.json
   cat vsa-anythingllm-project-ab7c8caf8c47.json | head -5
   ```

#### Option B: Upload via Dockerfile (Alternative)
Add to Dockerfile before COPY command:
```dockerfile
# Copy service account JSON to /data
RUN mkdir -p /data
COPY vsa-anythingllm-project-ab7c8caf8c47.json /data/
```

### 4. Verify Service Account Permissions

Check Google Cloud Console:
https://console.cloud.google.com/iam-admin/serviceaccounts?project=vsa-anythingllm-project

**Required APIs enabled:**
- ✓ Gmail API
- ✓ Google Drive API
- ✓ Google Docs API
- ✓ Google Sheets API
- ✓ Google Calendar API
- ✓ Google Forms API

**Required IAM roles:**
- ✓ Cloud Run Admin
- ✓ Service Account User

## 🚀 DEPLOYMENT

### After Environment Variables Are Set:

1. **Trigger Deployment**
   - Any push to `v5` branch triggers GitHub Actions
   - GitHub Actions builds Docker image
   - Pushes to GHCR
   - Render auto-deploys (~3-5 minutes)

2. **Or Manual Deploy**
   - Go to: https://dashboard.render.com/web/srv-d4b2723uibrs73ff02t0
   - Click "Manual Deploy" → "Deploy latest commit"

3. **Monitor Deployment**
   - Go to: https://dashboard.render.com/web/srv-d4b2723uibrs73ff02t0/logs
   - Watch for:
     ```
     🔷 [REGISTRY] Loaded 594 tools across 35 platforms
     🔷 [ANTHROPIC] API key: SET ✓
     🔷 [OPENAI] API key: SET ✓
     🔷 [DEEPSEEK] API key: SET ✓
     🔷 [GOOGLE] Service account: vsa-anythingllm-project@appspot.gserviceaccount.com ✓
     * Running on all addresses (0.0.0.0)
     * Running on http://127.0.0.1:10000
     ```

## ✅ FINAL VERIFICATION

### 1. Health Check
```bash
curl https://ai-agents-backend-singapore.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "app": "new_flask_app",
  "providers": ["anthropic", "deepseek", "openai"],
  "tools_loaded": 594,
  "service_account": "vsa-anythingllm-project@appspot.gserviceaccount.com"
}
```

### 2. Test UI
1. Visit: https://ai-agents-backend-singapore.onrender.com
2. Open browser console (F12)
3. Check for: `API Base URL: https://ai-agents-backend-singapore.onrender.com`
4. Should NOT see: `http://localhost:5001`

### 3. Test Google Login
1. Click "Login with Google"
2. Should redirect to Google OAuth
3. After login, check you can access Gmail/Drive tools

### 4. Test AI Chat
1. Type a message: "List my tools"
2. Should get response with 594 tools listed
3. Try: "Send an email to gerardo@vetsuccessacademy.com"

## 📊 MONITORING

### Key Metrics to Watch

**Render Dashboard:**
- CPU Usage: Should be <50% avg
- Memory: Should be <400MB avg
- Response Time: <500ms avg
- Disk Usage: <1GB used (out of 10GB)

**Error Patterns:**
- ❌ "Service account not found" → Upload JSON to /data
- ❌ "Database is locked" → Fixed with retry logic
- ❌ "Connection timeout" → Check Gunicorn workers
- ❌ "401 Unauthorized" → Check API keys

## 🔄 IN-HOUSE SERVICE (Optional)

If you want to update the second service:

Go to: https://dashboard.render.com/web/srv-d48j2qndiees739vq7b0/settings

1. Change branch: `v3-clean-deploy` → `v5`
2. Add same environment variables as Singapore service
3. Update `GOOGLE_REDIRECT_URI` to:
   ```
   https://ai-agents-in-house.onrender.com/api/auth/google/callback
   ```
4. Upload same service account JSON to /data
5. Click "Save Changes"

## 📝 NOTES

- **10GB Disk**: Automatically mounts to `/data` on first deploy
- **Cost**: $7/month (Starter) + $2.50/month (10GB disk) = $9.50/month
- **Service Account**: Has broader access than OAuth (server-side operations)
- **Auto-deploy**: Enabled on pushes to v5 branch
- **Backup**: Render disk has automatic daily snapshots

---

**Status**: Ready for deployment once service account JSON is uploaded to `/data`

**Next Step**: Upload JSON file using Render Shell (Option A above)
