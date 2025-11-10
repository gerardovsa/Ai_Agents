# Render.com Deployment Toolkit for AI Agents Platform

## 📋 Complete Deployment Guide for AI Assistants

This guide provides **step-by-step instructions** for deploying the AI Agents platform to Render.com, designed to be followed by AI assistants helping users deploy this project.

---

## 🎯 Overview

**What This Deploys:**
- Flask backend (AI Agents Platform)
- 564 tools across 35+ platforms
- OAuth authentication (Microsoft 365 + Google)
- PostgreSQL database (optional)
- Redis cache (optional)

**Deployment Method:** GitHub → Render.com automatic deployment

**Time Required:** ~15-20 minutes (including build time)

---

## 📚 Table of Contents

1. [Prerequisites Check](#1-prerequisites-check)
2. [GitHub Repository Setup](#2-github-repository-setup)
3. [Render Account Setup](#3-render-account-setup)
4. [Environment Variables Preparation](#4-environment-variables-preparation)
5. [Deployment Execution](#5-deployment-execution)
6. [Post-Deployment Configuration](#6-post-deployment-configuration)
7. [Verification & Testing](#7-verification--testing)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Prerequisites Check

###  Checklist

Run this command to check prerequisites:

```powershell
python Render_backend/check_prerequisites.py
```

**Required Items:**

- [x] GitHub account (user must provide username)
- [x] Render.com account (user must create at https://dashboard.render.com/register)
- [x] Git repository initialized locally
- [x] All sensitive files excluded via `.gitignore`
- [x] `.env.master` file with API keys (local only, never commit)
- [x] `runtime.txt` specifying Python version
- [x] `requirements.txt` at repository root

**Files That MUST Exist:**
```
AI_agents/
├── runtime.txt                  # Python version
├── requirements.txt             # Dependencies
├── .gitignore                   # Excludes secrets
├── AI_infrastructure/
│   └── flask_app.py            # Flask entry point
└── .env.master                 # Local only (never push)
```

---

## 2. GitHub Repository Setup

### Step 2.1: Remove Secrets from Git History

**Why:** GitHub secret scanning will block pushes containing API keys.

**Command:**
```powershell
python Render_backend/clean_git_secrets.py
```

**What it does:**
- Removes files with embedded secrets from git tracking
- Creates clean branch without secret history
- Updates `.gitignore` to prevent future leaks

**Files to exclude:**
- `config.py` (contains API keys)
- `.env.master` (contains credentials)
- `**/service-account*.json` (Google credentials)
- `**/azure_ad_app_config.json` (Microsoft credentials)
- Documentation files with example keys

### Step 2.2: Create Clean Branch

```powershell
# Create orphan branch (no history)
git checkout --orphan V2_clean

# Add all files (respecting .gitignore)
git add -A

# Commit
git commit -m "feat: Complete AI Infrastructure with OAuth, 564 Tools, and Unified UI (clean history)"
```

### Step 2.3: Push to GitHub

**Get GitHub repository URL from user:**
```
User must provide: https://github.com/USERNAME/REPO_NAME.git
```

**Push commands:**
```powershell
# Add remote (if not already added)
git remote add origin https://github.com/USERNAME/REPO_NAME.git

# Push clean branch
git push -u origin V2_clean
```

**If push fails with secret scanning errors:**
```powershell
# Run secret cleaner again
python Render_backend/clean_git_secrets.py --force

# Retry push
git push -u origin V2_clean --force
```

---

## 3. Render Account Setup

### Step 3.1: Create Render Account

**Instructions for user:**
1. Go to: https://dashboard.render.com/register
2. Sign up with GitHub account (recommended) or email
3. Verify email address
4. Complete onboarding

### Step 3.2: Get Render API Key

**Instructions for user:**
1. Go to: https://dashboard.render.com/u/settings
2. Click "API Keys" section
3. Click "+ Create API Key"
4. Name it: `AI_Agents_Deploy`
5. Copy the key (starts with `rnd_`)
6. **Save to `.env.master`:**
   ```
   RENDER_API_KEY=rnd_xxxxxxxxxxxxxxxxxxxxx
   ```

**Verification:**
```powershell
python Render_backend/verify_render_credentials.py
```

### Step 3.3: Connect GitHub to Render

**Instructions for user:**
1. Go to: https://dashboard.render.com/select-repo
2. Click "Connect GitHub"
3. Authorize Render app
4. Select repository: `USERNAME/REPO_NAME`
5. Confirm access

---

## 4. Environment Variables Preparation

### Step 4.1: Extract Environment Variables

**Command:**
```powershell
python Render_backend/extract_env_vars.py
```

**What it does:**
- Reads `.env.master` (local file)
- Extracts required variables for Render
- Generates `render_env_vars.json` (excluded from git)
- Lists all 40+ environment variables needed

**Output:** `render_env_vars.json`
```json
{
  "ANTHROPIC_API_KEY": "sk-ant-...",
  "OPENAI_API_KEY": "sk-proj-...",
  "MICROSOFT_CLIENT_ID": "...",
  "MICROSOFT_CLIENT_SECRET": "...",
  "PORT": "10000",
  "FLASK_ENV": "production"
}
```

### Step 4.2: Validate API Keys

**Command:**
```powershell
python Render_backend/validate_api_keys.py
```

**What it validates:**
- Anthropic API key (test API call)
- OpenAI API key (test API call)
- Microsoft OAuth credentials (check format)
- Google OAuth credentials (check service account)

---

## 5. Deployment Execution

### Step 5.1: Deploy via API (Recommended)

**Command:**
```powershell
python Render_backend/deploy_to_render.py
```

**What it does:**
1. Checks if service already exists
2. Creates new web service via Render API
3. Configures:
   - GitHub repo: `USERNAME/REPO_NAME`
   - Branch: `V2_clean`
   - Region: `oregon` (US West)
   - Plan: `starter` (downgrade to free later)
   - Build command: `pip install -r requirements.txt`
   - Start command: `python AI_infrastructure/flask_app.py`
4. Uploads all environment variables
5. Triggers initial deployment

**Expected output:**
```
 Service created successfully!
   Service ID: srv-xxxxxxxxxxxxx
   Service URL: https://ai-agents-backend-xxxx.onrender.com
   Dashboard: https://dashboard.render.com/web/srv-xxxxxxxxxxxxx
   
⏳ Build in progress (5-10 minutes)...
```

### Step 5.2: Deploy via CLI (Alternative)

**If API deployment fails, use Render CLI:**

**Install Render CLI:**
```powershell
# Using npm
npm install -g render-cli

# Or download from: https://render.com/docs/cli
```

**Deploy command:**
```powershell
python Render_backend/deploy_via_cli.py
```

### Step 5.3: Deploy via Dashboard (Manual)

**If both API and CLI fail, use manual deployment:**

```powershell
# Generate dashboard instructions
python Render_backend/generate_dashboard_guide.py
```

**Manual steps:**
1. Go to: https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect repository: `USERNAME/REPO_NAME`
4. Select branch: `V2_clean`
5. Configure service:
   - Name: `ai-agents-backend`
   - Region: Oregon (US West)
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python AI_infrastructure/flask_app.py`
6. Add environment variables (copy from `render_env_vars.json`)
7. Click "Create Web Service"

---

## 6. Post-Deployment Configuration

### Step 6.1: Monitor Deployment

**Command:**
```powershell
python Render_backend/monitor_deployment.py --service-id srv-xxxxxxxxxxxxx
```

**What it monitors:**
- Build progress (real-time)
- Deployment status
- Logs output
- Error detection

**Build stages:**
1. ⏳ Cloning repository
2. ⏳ Installing Python 3.11
3. ⏳ Installing dependencies (pip)
4. ⏳ Starting Flask server
5. ⏳ Loading 564 tools
6.  Service live

### Step 6.2: Update OAuth Redirect URLs

**After deployment succeeds, update OAuth providers:**

**Get service URL:**
```powershell
python Render_backend/get_service_url.py --service-id srv-xxxxxxxxxxxxx
```

**Output:** `https://ai-agents-backend-xxxx.onrender.com`

**Microsoft Azure Portal:**
1. Go to: https://portal.azure.com
2. Navigate to: Azure Active Directory → App Registrations
3. Select your app
4. Go to: Authentication → Redirect URIs
5. Add: `https://ai-agents-backend-xxxx.onrender.com/api/auth/microsoft/callback`
6. Save

**Google Cloud Console:**
1. Go to: https://console.cloud.google.com
2. Navigate to: APIs & Services → Credentials
3. Select your OAuth 2.0 Client ID
4. Add Authorized redirect URI: `https://ai-agents-backend-xxxx.onrender.com/api/auth/google/callback`
5. Save

**Automate OAuth updates:**
```powershell
python Render_backend/update_oauth_redirects.py --service-url https://ai-agents-backend-xxxx.onrender.com
```

### Step 6.3: Downgrade to Free Plan (Optional)

**Command:**
```powershell
python Render_backend/downgrade_to_free.py --service-id srv-xxxxxxxxxxxxx
```

**What it does:**
- Changes plan from `starter` to `free`
- Saves $7/month
- Note: Free plan sleeps after 15 min inactivity

**Manual downgrade:**
1. Go to service dashboard
2. Click "Settings"
3. Under "Plan", select "Free"
4. Confirm change

---

## 7. Verification & Testing

### Step 7.1: Health Check

**Command:**
```powershell
python Render_backend/test_deployment.py --service-url https://ai-agents-backend-xxxx.onrender.com
```

**Tests performed:**
1.  Health endpoint: `/health`
2.  Agent endpoint: `/api/agent/query`
3.  OAuth endpoints: `/api/auth/microsoft/login`, `/api/auth/google/login`
4.  Tool registry: Check 564 tools loaded
5.  Database connection
6.  Response time (<2s)

### Step 7.2: Manual Testing

**Health check:**
```powershell
curl https://ai-agents-backend-xxxx.onrender.com/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "tools_loaded": 564,
  "uptime": "5 minutes"
}
```

**Test AI agent:**
```powershell
curl -X POST https://ai-agents-backend-xxxx.onrender.com/api/agent/query `
  -H "Content-Type: application/json" `
  -d '{\"query\":\"What tools are available?\",\"user_id\":1}'
```

### Step 7.3: Performance Testing

**Command:**
```powershell
python Render_backend/performance_test.py --service-url https://ai-agents-backend-xxxx.onrender.com
```

**Metrics:**
- Response time (target: <2s)
- Throughput (requests/second)
- Error rate (target: 0%)
- Memory usage

---

## 8. Troubleshooting

### Common Issues

#### Issue 1: Build Fails - "Module not found"

**Cause:** Missing dependency in `requirements.txt`

**Fix:**
```powershell
python Render_backend/fix_missing_dependencies.py
```

**What it does:**
- Scans all Python files for imports
- Compares with `requirements.txt`
- Adds missing packages
- Commits and pushes update

#### Issue 2: Service Returns 502 Bad Gateway

**Cause:** Flask app not starting correctly

**Debug:**
```powershell
python Render_backend/fetch_logs.py --service-id srv-xxxxxxxxxxxxx
```

**Common fixes:**
- Check `PORT` environment variable (must be `10000`)
- Verify start command: `python AI_infrastructure/flask_app.py`
- Check for syntax errors in Flask app

#### Issue 3: Secret Scanning Block

**Cause:** API keys in commit history

**Fix:**
```powershell
python Render_backend/clean_git_secrets.py --aggressive
git push origin V2_clean --force
```

#### Issue 4: OAuth Not Working

**Cause:** Redirect URLs not updated

**Fix:**
```powershell
python Render_backend/verify_oauth_config.py --service-url https://ai-agents-backend-xxxx.onrender.com
```

**Output shows:**
- Current redirect URLs
- Required redirect URLs
- Instructions to update

---

## 🛠️ Utility Scripts Reference

All scripts are located in `Render_backend/`:

| Script | Purpose | Usage |
|--------|---------|-------|
| `check_prerequisites.py` | Verify deployment requirements | `python Render_backend/check_prerequisites.py` |
| `clean_git_secrets.py` | Remove secrets from git | `python Render_backend/clean_git_secrets.py` |
| `extract_env_vars.py` | Export environment variables | `python Render_backend/extract_env_vars.py` |
| `validate_api_keys.py` | Test API keys | `python Render_backend/validate_api_keys.py` |
| `deploy_to_render.py` | Deploy via API | `python Render_backend/deploy_to_render.py` |
| `monitor_deployment.py` | Watch build progress | `python Render_backend/monitor_deployment.py` |
| `test_deployment.py` | Verify deployment | `python Render_backend/test_deployment.py` |
| `fetch_logs.py` | Get Render logs | `python Render_backend/fetch_logs.py` |
| `update_oauth_redirects.py` | Update OAuth URLs | `python Render_backend/update_oauth_redirects.py` |
| `downgrade_to_free.py` | Switch to free plan | `python Render_backend/downgrade_to_free.py` |

---

## 📞 Getting Help

### Render API Documentation
https://api-docs.render.com/

### Render Dashboard
https://dashboard.render.com

### Project Documentation
See `docs/` folder for detailed documentation

---

## 🎯 Quick Start (TL;DR for AI)

```powershell
# 1. Clean secrets
python Render_backend/clean_git_secrets.py

# 2. Push to GitHub
git checkout --orphan V2_clean
git add -A
git commit -m "deploy: Clean deployment"
git push -u origin V2_clean

# 3. Get Render API key (user must provide)
# Save to .env.master: RENDER_API_KEY=rnd_xxx

# 4. Deploy
python Render_backend/deploy_to_render.py

# 5. Monitor
python Render_backend/monitor_deployment.py

# 6. Test
python Render_backend/test_deployment.py
```

---

**Last Updated:** October 29, 2025  
**Version:** 1.0.0  
**Status:**  Complete Guide for AI Deployment
