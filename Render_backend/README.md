# Render Deployment Toolkit

Complete automation toolkit for deploying the AI Agents platform to Render.com. This toolkit provides step-by-step scripts and documentation for AI assistants helping users deploy their platform.

## 📁 Toolkit Structure

```
Render_backend/
├── 📖 DEPLOYMENT_GUIDE_FOR_AI.md    # Complete deployment guide for AI assistants
├── 📖 README.md                      # This file
├── 🚀 render_deploy.py               # Master CLI (run this for full automation)
│
├── 🔧 Utility Scripts:
│   ├── check_prerequisites.py        # Verify requirements before deployment
│   ├── clean_git_secrets.py          # Remove secrets from git history
│   ├── extract_env_vars.py           # Export .env.master to Render format
│   ├── validate_api_keys.py          # Test API keys before deployment
│   ├── monitor_deployment.py         # Real-time deployment monitoring
│   ├── test_deployment.py            # Comprehensive endpoint testing
│   ├── fetch_logs.py                 # Retrieve deployment logs
│   ├── update_oauth_redirects.py     # OAuth configuration instructions
│   └── downgrade_to_free.py          # Switch to free plan
│
└── 📦 Legacy Scripts:
    ├── deploy_to_render_api.py       # Original API deployment script
    ├── check_render_service.py       # Service status checker
    ├── fix_render_deployment.py      # Update and redeploy
    └── get_render_logs.py            # Fetch deployment details
```

## 🚀 Quick Start

### Option 1: Full Automation (Recommended)

Run the master CLI for complete deployment:

```powershell
cd C:\Users\gpoli\GIT\AI_agents
python Render_backend\render_deploy.py
```

This will:
1. ✅ Check prerequisites
2. 🧹 Clean git secrets
3. 📦 Extract environment variables
4. 🔐 Validate API keys
5. 🚀 Deploy to Render
6. 📊 Monitor deployment progress
7. 🧪 Test deployment
8. 🔗 Provide OAuth update instructions

### Option 2: Step-by-Step

Run individual scripts for granular control:

```powershell
# 1. Check if ready to deploy
python Render_backend\check_prerequisites.py

# 2. Clean git history of secrets
python Render_backend\clean_git_secrets.py --create-clean-branch

# 3. Extract environment variables
python Render_backend\extract_env_vars.py

# 4. Validate API keys work
python Render_backend\validate_api_keys.py

# 5. Deploy to Render
python deploy_to_render_api.py

# 6. Monitor deployment progress
python Render_backend\monitor_deployment.py srv-YOUR_SERVICE_ID

# 7. Test deployment
python Render_backend\test_deployment.py https://your-service.onrender.com

# 8. Update OAuth redirects (instructions only)
python Render_backend\update_oauth_redirects.py https://your-service.onrender.com

# 9. (Optional) Downgrade to free plan
python Render_backend\downgrade_to_free.py srv-YOUR_SERVICE_ID
```

### Option 3: Check Only

Just verify you're ready to deploy without actually deploying:

```powershell
python Render_backend\render_deploy.py --check-only
```

## 📋 Prerequisites

Before running any deployment scripts, ensure you have:

### 1. Required Files
- ✅ `runtime.txt` - Python version specification
- ✅ `requirements.txt` - Python dependencies
- ✅ `.gitignore` - Excludes sensitive files
- ✅ `AI_infrastructure/flask_app.py` - Flask application entry point

### 2. Environment Variables
- ✅ `.env.master` file with API keys:
  ```bash
  ANTHROPIC_API_KEY=sk-ant-...
  OPENAI_API_KEY=sk-...
  DEEPSEEK_API_KEY_1=sk-...
  MICROSOFT_CLIENT_ID=...
  MICROSOFT_CLIENT_SECRET=...
  RENDER_API_KEY=rnd_...
  ```

### 3. Git Repository
- ✅ Git initialized (`git init`)
- ✅ Git remote configured (`git remote add origin ...`)
- ✅ Clean branch without secrets (V2_clean recommended)

### 4. Render Account
- ✅ Account created at https://render.com
- ✅ API key generated from https://dashboard.render.com/u/YOUR_USERNAME/settings#api-keys
- ✅ GitHub repository connected (optional, but recommended)

### 5. Python Packages
```powershell
pip install requests python-dotenv anthropic openai msal
```

## 📖 Script Documentation

### `render_deploy.py` - Master CLI

**Purpose**: Orchestrates entire deployment workflow from prerequisites to live production.

**Usage**:
```powershell
python Render_backend\render_deploy.py                 # Interactive mode
python Render_backend\render_deploy.py --auto          # Automatic mode
python Render_backend\render_deploy.py --check-only    # Prerequisites only
python Render_backend\render_deploy.py --monitor-only  # Monitor existing deployment
```

**Features**:
- Color-coded output for better visibility
- Interactive prompts with confirmations
- Automatic error recovery
- Progress tracking across all steps

---

### `check_prerequisites.py` - Prerequisites Checker

**Purpose**: Verify all requirements are met before deployment.

**Usage**:
```powershell
python Render_backend\check_prerequisites.py
```

**Checks**:
- Required files exist (runtime.txt, requirements.txt, etc.)
- .env.master has required API keys
- Git repository initialized
- Git remote configured
- Python version
- Render API key format

**Exit Codes**:
- `0` - All prerequisites met
- `1` - Missing prerequisites

---

### `clean_git_secrets.py` - Git Secret Cleaner

**Purpose**: Remove sensitive files from git history to allow GitHub push.

**Usage**:
```powershell
python Render_backend\clean_git_secrets.py                    # Remove from cache only
python Render_backend\clean_git_secrets.py --create-clean-branch  # Create V2_clean branch
```

**Actions**:
1. Updates .gitignore with sensitive patterns
2. Removes sensitive files from git cache
3. (Optional) Creates orphan branch with clean history
4. Commits changes

**Files Removed**:
- `config.py`
- `.env.master`, `.env`, `.env.*`
- `vsa-anythingllm-project-*.json`
- `**/service-account*.json`
- Documentation with embedded secrets

---

### `extract_env_vars.py` - Environment Variable Extractor

**Purpose**: Convert .env.master to Render API-compatible JSON format.

**Usage**:
```powershell
python Render_backend\extract_env_vars.py
```

**Output**: `render_env_vars.json` with structure:
```json
[
  {"key": "ANTHROPIC_API_KEY", "value": "sk-ant-..."},
  {"key": "OPENAI_API_KEY", "value": "sk-..."},
  ...
]
```

**Features**:
- UTF-8 encoding support
- Automatic PORT=10000 addition
- Masked preview of sensitive values
- Validation of required keys

---

### `validate_api_keys.py` - API Key Validator

**Purpose**: Test API keys by making real API calls before deployment.

**Usage**:
```powershell
python Render_backend\validate_api_keys.py
```

**Tests**:
- ✅ Anthropic Claude API key
- ✅ OpenAI API key
- ✅ DeepSeek API key
- ✅ Microsoft OAuth credentials (MSAL token acquisition)

**Exit Codes**:
- `0` - All keys valid
- `1` - Some keys invalid

---

### `monitor_deployment.py` - Deployment Monitor

**Purpose**: Real-time monitoring of Render deployment progress.

**Usage**:
```powershell
python Render_backend\monitor_deployment.py srv-YOUR_SERVICE_ID
python Render_backend\monitor_deployment.py srv-YOUR_SERVICE_ID 5  # Check every 5 seconds
```

**Features**:
- Real-time status updates
- Emoji status indicators (🔨 building, ✅ live, ❌ failed)
- Elapsed time tracking
- Automatic completion detection
- Helpful next steps on completion

**Status Emojis**:
- 🆕 Created
- 🔨 Build in progress
- 🔄 Update in progress
- ✅ Live
- ❌ Failed
- 🚫 Canceled

---

### `test_deployment.py` - Deployment Tester

**Purpose**: Comprehensive testing of deployed service endpoints.

**Usage**:
```powershell
python Render_backend\test_deployment.py https://your-service.onrender.com
```

**Tests**:
1. ✅ Health endpoint (`/health`)
2. ✅ API status (`/api/status`)
3. ✅ Tools list (`/api/tools`)
4. ✅ CORS configuration
5. ✅ Response time
6. ✅ Database connection

**Exit Codes**:
- `0` - All tests passed
- `1` - Some tests failed

---

### `fetch_logs.py` - Log Fetcher

**Purpose**: Retrieve deployment logs for debugging.

**Usage**:
```powershell
python Render_backend\fetch_logs.py srv-YOUR_SERVICE_ID
```

**Features**:
- Recent deployment summary
- Service events timeline
- Instructions for accessing full logs
- Direct dashboard links

**Note**: Render API v1 doesn't expose build logs endpoint. This script provides instructions for accessing logs via dashboard or CLI.

---

### `update_oauth_redirects.py` - OAuth Configuration Helper

**Purpose**: Provide instructions for updating OAuth redirect URLs.

**Usage**:
```powershell
python Render_backend\update_oauth_redirects.py https://your-service.onrender.com
```

**Provides**:
- Step-by-step Microsoft Azure AD instructions
- Step-by-step Google Cloud Console instructions
- Environment variable verification checklist
- Testing instructions for OAuth flows

**Redirect URLs**:
- Microsoft: `https://your-service.onrender.com/api/auth/microsoft/callback`
- Google: `https://your-service.onrender.com/api/auth/google/callback`

---

### `downgrade_to_free.py` - Plan Downgrader

**Purpose**: Switch Render service from Starter ($7/month) to Free plan.

**Usage**:
```powershell
python Render_backend\downgrade_to_free.py srv-YOUR_SERVICE_ID
```

**Features**:
- Current plan detection
- Free plan limitations explanation
- Confirmation prompt
- Keep-alive solutions (UptimeRobot, cron jobs)

**Free Plan Limitations**:
- 🔴 Sleeps after 15 minutes inactivity
- 🔴 512 MB RAM (vs 2GB)
- 🔴 Shared CPU
- 🟢 Still free: HTTPS, custom domains, auto-deploys

**Keep-Alive Solution**: Use UptimeRobot to ping `/health` every 14 minutes.

---

## 🔧 Troubleshooting

### Deployment Failed - Build Error

**Symptoms**: Build fails, status shows `build_failed`

**Solutions**:
1. Check logs: `python Render_backend\fetch_logs.py`
2. Verify runtime.txt has correct Python version
3. Check requirements.txt is valid (no syntax errors)
4. Ensure all dependencies are installable

**Common Causes**:
- Wrong Python version in runtime.txt
- Missing system dependencies in requirements.txt
- Incompatible package versions

---

### Deployment Failed - Runtime Error

**Symptoms**: Build succeeds but service crashes on startup

**Solutions**:
1. Check environment variables are set correctly
2. Verify start command in Render dashboard
3. Check application logs in dashboard
4. Test database connection

**Common Causes**:
- Missing environment variables
- Database path issues
- Port configuration problems

---

### OAuth Flows Not Working

**Symptoms**: OAuth redirects fail, users can't authenticate

**Solutions**:
1. Update redirect URLs: `python Render_backend\update_oauth_redirects.py`
2. Verify Microsoft Azure AD redirect URI
3. Verify Google Cloud Console redirect URI
4. Check environment variables: MICROSOFT_CLIENT_ID, GOOGLE_CLIENT_ID

**Redirect URLs Must Match Exactly**:
- Microsoft: `https://your-service.onrender.com/api/auth/microsoft/callback`
- Google: `https://your-service.onrender.com/api/auth/google/callback`

---

### Service Sleeping on Free Plan

**Symptoms**: Service takes 30 seconds to respond after inactivity

**Solutions**:
1. Set up UptimeRobot: https://uptimerobot.com
2. Monitor: `https://your-service.onrender.com/health`
3. Interval: 14 minutes
4. Alternative: Upgrade to Starter plan ($7/month)

---

## 📚 Additional Resources

### Render Documentation
- **Dashboard**: https://dashboard.render.com
- **API Docs**: https://api-docs.render.com/reference/introduction
- **CLI**: https://render.com/docs/cli
- **Status Page**: https://status.render.com

### Getting Render API Key
1. Go to https://dashboard.render.com
2. Click your profile (top right)
3. Select "Account Settings"
4. Click "API Keys" tab
5. Click "Create API Key"
6. Copy key (starts with `rnd_`)
7. Add to .env.master: `RENDER_API_KEY=rnd_...`

### Getting Microsoft OAuth Credentials
1. Go to https://portal.azure.com
2. Navigate to "Azure Active Directory" → "App registrations"
3. Click "New registration"
4. Name: "AI Agents Backend"
5. Supported account types: "Accounts in any organizational directory"
6. Redirect URI: `https://your-service.onrender.com/api/auth/microsoft/callback`
7. Copy Application (client) ID → `MICROSOFT_CLIENT_ID`
8. Create client secret → `MICROSOFT_CLIENT_SECRET`

### Getting Google OAuth Credentials
1. Go to https://console.cloud.google.com
2. Select or create project
3. Navigate to "APIs & Services" → "Credentials"
4. Click "Create Credentials" → "OAuth 2.0 Client ID"
5. Application type: "Web application"
6. Authorized redirect URIs: `https://your-service.onrender.com/api/auth/google/callback`
7. Copy Client ID → `GOOGLE_CLIENT_ID`
8. Copy Client Secret → `GOOGLE_CLIENT_SECRET`

---

## 🤖 For AI Assistants

This toolkit is designed for AI assistants helping users deploy the platform. Follow this workflow:

1. **Always start with prerequisites**: `python Render_backend\check_prerequisites.py`
2. **Guide user through missing items**: Explain what's needed and how to get it
3. **Use master CLI for automation**: `python Render_backend\render_deploy.py`
4. **Monitor progress**: Real-time updates keep user informed
5. **Test deployment**: Verify everything works before declaring success
6. **Provide OAuth instructions**: User must update redirect URLs manually

**Key Points**:
- Don't skip prerequisites - they prevent deployment failures
- Explain WHY each step is needed, not just WHAT to do
- Use the comprehensive guide: `DEPLOYMENT_GUIDE_FOR_AI.md`
- Be patient - builds take 5-10 minutes
- Always test after deployment

---

## 📝 License

Part of the AI Agents platform - see main repository LICENSE file.

---

**Last Updated**: January 2025  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
