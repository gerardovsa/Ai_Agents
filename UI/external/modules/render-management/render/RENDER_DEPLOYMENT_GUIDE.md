# MustCare ValorAISynergySuite V3 - Render.com Deployment Guide

## 🎯 Overview

This guide provides complete instructions for deploying **MustCare ValorAISynergySuite V3** (AnythingLLM fork with Claude 4 integration) to Render.com using Docker.

**Deployment Architecture:**
- **Main Service**: Web application (React frontend + Express backend + Collector)
- **Database**: PostgreSQL 14+ managed database
- **Storage**: Persistent disk for LanceDB vector database
- **Region**: Singapore (closest to Australia)

**Estimated Deployment Time:** 15-20 minutes
**Monthly Cost:** ~$34.50 (can scale down to ~$14/month for testing)

---

## 📋 Prerequisites

### 1. Required Accounts & API Keys

- **Render.com Account**: https://dashboard.render.com/register
- **GitHub Account**: Repository must be pushed to GitHub
- **Anthropic API Key**: https://console.anthropic.com/settings/keys

### 2. Required Software (for local testing)

- Node.js 20.x
- Docker Desktop (optional, for local testing)
- Git

### 3. Repository Requirements

- Branch: `V8-Render`
- Files required:
  - `render.yaml` (blueprint configuration)
  - `render/Dockerfile.render` (main application)
  - `render/start.sh` (startup script)
  - `render/.env.render.template` (environment template)

---

## 🚀 Deployment Steps

### Step 1: Prepare Your Repository

**1.1 Ensure you're on the V8-Render branch:**

```powershell
cd "c:\Users\gpoli\GIT\MustCare ValorAISynergySuite"
git checkout V8-Render
git status
```

**1.2 Verify render files exist:**

```powershell
ls render/
# Should show: Dockerfile.render, start.sh, .env.render.template

ls render.yaml
# Should exist in project root
```

**1.3 Commit and push to GitHub:**

```powershell
git add .
git commit -m "feat: Add Render.com V8 deployment configuration"
git push origin V8-Render
```

---

### Step 2: Get Your Anthropic API Key

**2.1 Navigate to Anthropic Console:**
- Go to: https://console.anthropic.com/settings/keys
- Sign in or create account

**2.2 Create new API key:**
- Click "Create Key"
- Name: `MustCare-ValorAI-Production`
- Copy the key (starts with `sk-ant-`)
- **Save this key securely** - you'll need it in Step 4

---

### Step 3: Deploy to Render via Blueprint

**3.1 Sign in to Render:**
- Go to: https://dashboard.render.com
- Sign in or create account
- Connect your GitHub account if not already connected

**3.2 Deploy from Blueprint:**

1. Click **"New +"** button (top right)
2. Select **"Blueprint"**
3. **Connect Repository:**
   - Select your GitHub account
   - Find: `MustCare_ValorAISynergySuite`
   - Branch: `V8-Render`
4. **Configure Blueprint:**
   - Blueprint Name: `MustCare ValorAI V3`
   - Blueprint File: `render.yaml` (auto-detected)
5. Click **"Apply"**

**3.3 Wait for initial setup:**
- Render will create:
  - ✅ Web service: `mustcare-valorai-v3`
  - ✅ PostgreSQL database: `mustcare-postgres`
  - ✅ Persistent disk: `vector-storage` (10GB)
- This takes ~2-3 minutes

---

### Step 4: Configure Environment Variables

**4.1 Navigate to your web service:**
- Dashboard → Services → `mustcare-valorai-v3`

**4.2 Go to Environment tab:**
- Click **"Environment"** in left sidebar

**4.3 Add required secret (ANTHROPIC_API_KEY):**

The blueprint auto-generates most environment variables, but you MUST add:

1. Find `ANTHROPIC_API_KEY` in the list
2. Click the value field
3. Paste your Anthropic API key from Step 2
4. Click **"Save Changes"**

**4.4 Verify other environment variables:**

These should be auto-configured by render.yaml:
- ✅ `JWT_SECRET` - Auto-generated
- ✅ `DATABASE_URL` - Auto-configured from database
- ✅ `MULTI_USER_MODE` - Set to `true`
- ✅ `LLM_PROVIDER` - Set to `anthropic`
- ✅ `ANTHROPIC_MODEL_PREF` - Set to `claude-sonnet-4-20250514`
- ✅ `ANTHROPIC_WEB_SEARCH_ENABLED` - Set to `true`
- ✅ `ANTHROPIC_CODE_EXECUTION_ENABLED` - Set to `true`
- ✅ `VECTOR_DB` - Set to `lancedb`
- ✅ `STORAGE_DIR` - Set to `/app/storage`

---

### Step 5: Trigger Deployment

**5.1 Manual deploy:**
- Go to: Services → `mustcare-valorai-v3`
- Click **"Manual Deploy"** → **"Deploy latest commit"**

**5.2 Monitor build logs:**
- Click **"Logs"** tab
- Watch the build progress
- **Expected build time: 8-12 minutes**

**Build stages you'll see:**
1. ✅ Cloning repository
2. ✅ Building Docker image (multi-stage)
   - Stage 1: Frontend build (~3 min)
   - Stage 2: Server build (~2 min)
   - Stage 3: Collector build (~1 min)
   - Stage 4: Final image assembly (~1 min)
3. ✅ Pushing image to registry (~2 min)
4. ✅ Starting container (~30 sec)
5. ✅ Health check passing

**5.3 Wait for "Live" status:**
- Service status will change from "Building" → "Deploying" → "Live"
- You'll see: **🟢 Live** indicator

---

### Step 6: Verify Deployment

**6.1 Get your service URL:**
- In service dashboard, find: `https://mustcare-valorai-v3.onrender.com`

**6.2 Test health endpoint:**

```powershell
curl https://mustcare-valorai-v3.onrender.com/api/v1/system/check
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "node": "v20.x.x",
  "uptime": 123
}
```

**6.3 Open in browser:**
- Navigate to: `https://mustcare-valorai-v3.onrender.com`
- You should see the MustCare login/setup page

---

### Step 7: Initial Setup

**7.1 Create admin account:**
1. Open your deployment URL
2. You'll see "Welcome to MustCare ValorAI"
3. Click "Create Account" or "Setup"
4. Fill in:
   - Username: `admin`
   - Password: (secure password, min 8 chars)
   - Email: your-email@example.com
5. Click "Create Admin Account"

**7.2 Verify Claude 4 features:**
- Create a new workspace
- Test chat with Claude Sonnet 4
- Test advanced features:
  - ✅ Web search
  - ✅ Code execution
  - ✅ Document upload
  - ✅ Interleaved thinking

**7.3 Test multi-user features:**
- Go to Settings → Users
- Create additional users (manager/default roles)
- Test role-based permissions

---

## 💰 Cost Breakdown

### Default Configuration (Production)

| Service | Plan | Specs | Cost/Month |
|---------|------|-------|------------|
| **Web Service** | Standard | 2GB RAM, 2 CPU | $25.00 |
| **PostgreSQL** | Starter | 256MB RAM, 1GB storage | $7.00 |
| **Persistent Disk** | 10GB | Vector storage | $2.50 |
| **Total** | | | **$34.50/month** |

### Cost Optimization (Testing/Development)

| Service | Plan | Specs | Cost/Month |
|---------|------|-------|------------|
| **Web Service** | Starter | 512MB RAM, 0.5 CPU | $7.00 |
| **PostgreSQL** | Starter | 256MB RAM, 1GB storage | $7.00 |
| **Persistent Disk** | 5GB | Vector storage | $1.25 |
| **Total** | | | **$15.25/month** |

### Free Tier (Limited Testing)

| Service | Plan | Specs | Cost/Month |
|---------|------|-------|------------|
| **Web Service** | Free | 512MB RAM | $0.00* |
| **PostgreSQL** | External | Use external DB | $0.00 |
| **Total** | | | **Free** |

*Free tier: 750 hours/month, spins down after 15 min inactivity

---

## 🔧 Advanced Configuration

### Upgrade to Basic PostgreSQL (Recommended for Production)

**Why upgrade?**
- Starter plan (256MB) may be insufficient for heavy usage
- Basic plan (1GB RAM, 10GB storage) = $21/month

**How to upgrade:**
1. Dashboard → Databases → `mustcare-postgres`
2. Settings → Plan
3. Select "Basic" ($21/month)
4. Confirm upgrade
5. No downtime, automatic migration

### Scale Web Service

**Upgrade to Professional ($85/month):**
- 4GB RAM, 4 CPU cores
- Better for high concurrency
- Faster document processing

**How to scale:**
1. Dashboard → Services → `mustcare-valorai-v3`
2. Settings → Plan
3. Select desired plan
4. Confirm

### Increase Persistent Disk

**Current: 10GB ($2.50/month)**

If you need more space for documents/vectors:
1. Dashboard → Services → `mustcare-valorai-v3`
2. Disks → `vector-storage`
3. Click "Resize"
4. Select new size (e.g., 20GB = $5/month)
5. Confirm (applies immediately, no downtime)

### Custom Domain

**Setup custom domain:**
1. Dashboard → Services → `mustcare-valorai-v3`
2. Settings → Custom Domains
3. Add your domain: `valorai.yourdomain.com`
4. Add CNAME record to your DNS:
   - Type: CNAME
   - Name: `valorai`
   - Value: `mustcare-valorai-v3.onrender.com`
5. Render auto-provisions SSL certificate

---

## 🐛 Troubleshooting

### Build Failures

**Issue: "Node version mismatch"**
```
ERROR: This project requires Node.js 20.x
```

**Solution:**
- Verify `render/Dockerfile.render` uses `FROM node:20-slim`
- Don't change to Node 18 - cheerio@1.1.2 requires Node 20+

---

**Issue: "Frontend build failed - Missing asset"**
```
ERROR: Could not resolve './user.png'
```

**Solution:**
- Use Phosphor React Icons instead of PNG assets
- Check `frontend/src/components/` for PNG imports
- Replace with: `import { User } from "@phosphor-icons/react";`

---

**Issue: "Out of memory during build"**
```
ERROR: Docker build killed (OOM)
```

**Solution:**
- Upgrade to Standard plan ($25/month) - 2GB RAM
- Or optimize Dockerfile with `--max-old-space-size=512` for npm build

---

### Runtime Errors

**Issue: "Database connection failed"**
```
ERROR: connect ECONNREFUSED
```

**Solution:**
1. Verify DATABASE_URL is set correctly
2. Check database is "Available" status
3. Check IP allowlist (should be empty for Render-internal access)

---

**Issue: "Anthropic API key invalid"**
```
ERROR: 401 Unauthorized - Invalid API key
```

**Solution:**
1. Verify ANTHROPIC_API_KEY in Environment tab
2. Check key starts with `sk-ant-`
3. Regenerate key in Anthropic Console if needed

---

**Issue: "Health check failing"**
```
WARN: Health check failed - timeout
```

**Solution:**
1. Check logs for startup errors
2. Verify port 3001 is exposed
3. Check startup script executed successfully
4. Increase start-period in Dockerfile HEALTHCHECK if needed

---

### Performance Issues

**Issue: "Slow response times"**

**Solution:**
1. Upgrade to Standard plan (2GB RAM)
2. Check database performance (upgrade to Basic)
3. Enable vector caching: `CACHE_VECTORS=true`
4. Monitor logs for bottlenecks

---

**Issue: "Collector timeout"**

**Solution:**
1. Check collector service is running: `curl http://localhost:8888/process`
2. Increase startup wait time in `start.sh`
3. Check collector logs in `/app/logs/collector.log`

---

## 📊 Monitoring & Maintenance

### View Logs

**Web service logs:**
```
Dashboard → Services → mustcare-valorai-v3 → Logs
```

**Database logs:**
```
Dashboard → Databases → mustcare-postgres → Logs
```

**Download logs:**
```powershell
# Using Render CLI
render logs mustcare-valorai-v3 --follow
```

### Metrics

**View metrics:**
1. Dashboard → Services → `mustcare-valorai-v3`
2. Metrics tab
3. Monitor:
   - CPU usage
   - Memory usage
   - Request rate
   - Response time

### Backups

**PostgreSQL automatic backups:**
- Daily backups (retained 7 days)
- Point-in-time recovery available
- Manual backup:
  1. Databases → `mustcare-postgres`
  2. Backups → "Create Backup"

**Vector storage backup:**
- Persistent disk is backed up daily
- Download via:
  ```powershell
  # SSH into service
  render ssh mustcare-valorai-v3
  # Tar vector storage
  tar -czf /tmp/vectors.tar.gz /app/storage/lancedb
  ```

---

## 🔄 Updates & Redeployment

### Automatic Deployment (Recommended)

**Setup auto-deploy:**
1. Dashboard → Services → `mustcare-valorai-v3`
2. Settings → Build & Deploy
3. Enable "Auto-Deploy" toggle
4. Select branch: `V8-Render`

Now every push to V8-Render will auto-deploy.

### Manual Deployment

**Deploy latest commit:**
```powershell
# Push changes to GitHub
git add .
git commit -m "feat: Update feature X"
git push origin V8-Render

# Then in Render Dashboard:
# Services → mustcare-valorai-v3 → Manual Deploy → Deploy latest commit
```

### Rollback

**Rollback to previous version:**
1. Dashboard → Services → `mustcare-valorai-v3`
2. Deploys tab
3. Find previous successful deploy
4. Click "Rollback to this version"
5. Confirm

---

## 🔐 Security Best Practices

### Environment Variables

- ✅ **DO**: Use Render's environment variable management
- ✅ **DO**: Enable "Sync: false" for secrets
- ❌ **DON'T**: Commit `.env` files to git
- ❌ **DON'T**: Share API keys publicly

### JWT Secret

- Generate strong secret: `openssl rand -hex 32`
- Rotate every 90 days
- Update in Environment variables → Redeploy

### API Keys

- Use different keys for production vs development
- Monitor usage in Anthropic Console
- Set spending limits
- Rotate keys if compromised

### HTTPS

- Render provides automatic SSL certificates
- Force HTTPS (enabled by default)
- Use custom domain for production

### Database Security

- Use strong passwords (auto-generated by Render)
- Keep IP allowlist empty (internal access only)
- Enable automatic backups
- Monitor connection logs

---

## 📞 Support & Resources

### Render Documentation
- **Dashboard**: https://dashboard.render.com
- **Docs**: https://render.com/docs
- **Community**: https://community.render.com
- **Status**: https://status.render.com
- **Support**: support@render.com

### MustCare Project
- **GitHub**: https://github.com/gerardovsa/MustCare_ValorAISynergySuite
- **Issues**: [Repository Issues Page]
- **Discussions**: [Repository Discussions]

### Anthropic
- **Console**: https://console.anthropic.com
- **Docs**: https://docs.anthropic.com
- **Support**: support@anthropic.com

---

## ✅ Post-Deployment Checklist

- [ ] Service is "Live" (green indicator)
- [ ] Health check passing: `/api/v1/system/check`
- [ ] Admin account created
- [ ] Claude 4 features tested (web search, code execution)
- [ ] Multi-user authentication tested
- [ ] Document upload and vector search tested
- [ ] Custom domain configured (optional)
- [ ] Auto-deploy enabled
- [ ] Backups verified
- [ ] Monitoring configured
- [ ] Cost tracking reviewed
- [ ] Team access granted (if applicable)

---

## 🎉 Success!

Your MustCare ValorAISynergySuite V3 is now live on Render.com!

**Access your deployment:**
- URL: `https://mustcare-valorai-v3.onrender.com`
- Or: `https://your-custom-domain.com`

**Key features available:**
- ✅ Claude 4 Sonnet (with extended thinking)
- ✅ Web search integration
- ✅ Code execution sandbox
- ✅ Document processing with LanceDB
- ✅ Multi-user authentication
- ✅ Role-based access control
- ✅ Workspace isolation
- ✅ Vector similarity search

**Need help?** Check troubleshooting section or contact support.

---

**Last Updated:** November 8, 2025  
**Version:** V8-Render  
**Deployment Target:** Render.com (Singapore Region)
