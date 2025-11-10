# 🇦🇺 AI Agents Platform - Australia Docker Deployment Guide

## 📍 Region-Optimized Deployment for Australia

**Target Region:** Singapore (closest to Australia with ~100ms latency)  
**Deployment Method:** Docker (for sandbox code execution support)  
**Provider:** Render.com  
**GitHub Integration:** Automatic deployment from your GitHub account

---

## 🌏 Why Singapore Region?

Render.com regions ranked by Australia proximity:

| Region | Location | Latency from Australia | Recommended |
|--------|----------|------------------------|-------------|
| **Singapore** | Southeast Asia | **~100-150ms** | ✅ **BEST** |
| Oregon | US West | ~200-250ms | ⚠️ High latency |
| Ohio | US East | ~250-300ms | ❌ Very high latency |
| Frankfurt | Europe | ~300-350ms | ❌ Very high latency |

**Singapore offers:**
- 50-60% lower latency vs Oregon
- Better timezone alignment (GMT+8 vs GMT+10 Brisbane)
- Optimal for Australian users
- Docker support for code execution sandboxes

---

## 🐳 Docker Deployment Architecture

### Why Docker for AI Agents?

**Standard Python deployment limitations:**
- Cannot execute arbitrary user code safely
- No sandboxed environment for data analysis
- Limited package installation during runtime
- Security risks with code execution

**Docker deployment advantages:**
- ✅ **Sandboxed code execution** - Run user code in isolated containers
- ✅ **Dynamic package installation** - Install Python packages on-demand
- ✅ **Data analysis capabilities** - Execute pandas, numpy, matplotlib code
- ✅ **Security** - Isolated from main application
- ✅ **Resource limits** - Control CPU/memory per execution

### Current Docker Experience (In_House_SQL Project)

You already have production Docker deployment experience with:
- **In_House_SQL Flask service** - Docker deployment on Render
- **Streamlit UI service** - Docker deployment on Render
- **render.yaml configuration** - Multi-service Docker setup
- **Working Dockerfile** - Python 3.13, ODBC drivers, multi-stage build

**Proven setup:**
```yaml
services:
  - type: web
    name: inhouseprint-flask
    env: docker  # Docker deployment
    plan: free
    dockerfilePath: ./Quote_Calculator/AI_Quote_Agent/web_interface/Dockerfile
    envVars:
      - key: ANTHROPIC_API_KEY
      - key: DATABASE_SERVER
```

---

## 📦 Deployment Options

### Option 1: Docker Deployment (Recommended for Code Execution)

**Use Case:** Need sandbox code execution, data analysis, dynamic packages

**Files needed:**
1. `Dockerfile` - Container configuration
2. `render.yaml` - Service definition
3. `.dockerignore` - Exclude unnecessary files

**Advantages:**
- Sandboxed execution environment
- Full control over system dependencies
- Can install additional packages at runtime
- Better security isolation

**Disadvantages:**
- Longer build times (5-8 minutes vs 3-5 minutes)
- Slightly more complex configuration
- Requires Dockerfile maintenance

### Option 2: Native Python Deployment (Simpler)

**Use Case:** Basic API server, no code execution needed

**Files needed:**
1. `requirements.txt` - Python dependencies
2. `runtime.txt` - Python version

**Advantages:**
- Faster builds (3-5 minutes)
- Simpler configuration
- Easier to maintain

**Disadvantages:**
- No sandboxed code execution
- Cannot install packages at runtime
- Limited security isolation

---

## 🚀 Quick Start: Docker Deployment to Singapore

### Prerequisites (You Already Have)

✅ GitHub account (gerardovsa)  
✅ Render.com account (linked to GitHub)  
✅ AI_agents repository on GitHub  
✅ Docker deployment experience (In_House_SQL)  
✅ Render API key (in your Render dashboard)

### Step 1: Create Dockerfile

```dockerfile
# AI Agents Platform - Docker Configuration
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed for specific tools)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire application
COPY . .

# Add application to Python path
ENV PYTHONPATH="/app:/app/tools:/app/AI_infrastructure:${PYTHONPATH}"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV RENDER=true
ENV ENVIRONMENT=production

# Expose Flask port
EXPOSE 5001

# Run Flask app
CMD ["python", "AI_infrastructure/flask_app.py"]
```

**Save as:** `C:\Users\gpoli\GIT\AI_agents\Dockerfile`

### Step 2: Create .dockerignore

```
# Git
.git
.gitignore
.github

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist
build
.pytest_cache
.coverage

# Environment
.env
.env.master
.env.*
venv/
env/
*.env

# Secrets (CRITICAL - DO NOT INCLUDE IN DOCKER IMAGE)
config.py
**/service-account*.json
**/azure_ad_app_config.json
**/credentials*.json
**/*_credentials*.json

# IDE
.vscode
.idea
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database (local only)
*.db
*.sqlite
*.sqlite3

# Documentation
docs/archive/
*.md
!README.md

# Testing
testing_tools/
test_*.py
*_test.py
```

**Save as:** `C:\Users\gpoli\GIT\AI_agents\.dockerignore`

### Step 3: Create render.yaml (Singapore Region)

```yaml
services:
  # AI Agents Platform - Flask Backend
  - type: web
    name: ai-agents-backend
    env: docker
    region: singapore  # 🇸🇬 CLOSEST TO AUSTRALIA
    plan: starter  # $7/month (can downgrade to free later)
    rootDir: .
    dockerfilePath: ./Dockerfile
    dockerContext: ./
    
    # Build configuration
    autoDeploy: true  # Auto-deploy on git push
    branch: V2_clean
    
    # Health check endpoint
    healthCheckPath: /health
    
    # Environment variables
    envVars:
      # Flask configuration
      - key: PYTHONUNBUFFERED
        value: "1"
      - key: RENDER
        value: "true"
      - key: ENVIRONMENT
        value: "production"
      - key: PORT
        value: "10000"  # Render default
      
      # AI Provider Keys (sync from .env file)
      - key: ANTHROPIC_API_KEY
        sync: false  # Will add manually in dashboard
      - key: OPENAI_API_KEY
        sync: false
      - key: DEEPSEEK_API_KEY_1
        sync: false
      
      # Microsoft OAuth (sync from .env file)
      - key: MICROSOFT_CLIENT_ID
        sync: false
      - key: MICROSOFT_CLIENT_SECRET
        sync: false
      - key: MICROSOFT_TENANT_ID
        value: common
      
      # Google OAuth (sync from .env file)
      - key: GOOGLE_OAUTH_CLIENT_ID
        sync: false
      - key: GOOGLE_OAUTH_CLIENT_SECRET
        sync: false
      - key: GOOGLE_OAUTH_MODE
        value: web  # Use web mode for production
      
      # Database paths (automatically created in container)
      - key: DATABASE_PATH
        value: /app/data/ai_infrastructure.db
      - key: SESSION_DB_PATH
        value: /app/data/sessions.db
```

**Save as:** `C:\Users\gpoli\GIT\AI_agents\render.yaml`

### Step 4: Extract Environment Variables

```powershell
cd C:\Users\gpoli\GIT\AI_agents
python Render_backend\extract_env_vars.py
```

**Output:** `render_env_vars.json` with all API keys formatted for Render

### Step 5: Deploy to Render (Singapore Region)

**Automated deployment:**

```powershell
cd C:\Users\gpoli\GIT\AI_agents
python Render_backend\render_deploy.py
```

**The script will:**
1. ✅ Check prerequisites
2. ✅ Validate Dockerfile exists
3. ✅ Validate render.yaml exists
4. ✅ Push to GitHub (branch: V2_clean)
5. ✅ Create Render service in **Singapore region**
6. ✅ Upload environment variables
7. ✅ Trigger Docker build
8. ✅ Monitor deployment progress

**Expected build time:** 5-8 minutes

**Manual deployment (alternative):**

1. Push to GitHub:
   ```powershell
   git add Dockerfile .dockerignore render.yaml
   git commit -m "feat: Add Docker deployment configuration for Singapore"
   git push origin V2_clean
   ```

2. Go to Render dashboard: https://dashboard.render.com

3. Click "New +" → "Web Service"

4. Connect repository: `gerardovsa/AI_agents`

5. Configure:
   - **Branch:** `V2_clean`
   - **Region:** `singapore` ⭐ **IMPORTANT**
   - **Environment:** `Docker`
   - **Dockerfile Path:** `./Dockerfile`
   - **Plan:** Starter ($7/month)

6. Add environment variables from `render_env_vars.json`

7. Click "Create Web Service"

---

## 📊 Monitoring Deployment

### Real-time Build Monitoring

```powershell
python Render_backend\monitor_deployment.py srv-xxxxx
```

**Build stages:**
1. ⏳ Cloning repository from GitHub
2. ⏳ Building Docker image (5-8 minutes)
   - Installing system dependencies
   - Installing Python packages
   - Copying application files
3. ⏳ Pushing image to registry
4. ⏳ Starting container
5. ⏳ Running Flask server
6. ⏳ Loading 564 tools
7. ✅ Service live

### Check Service Status

```powershell
python Render_backend\test_render_connection.py
```

**Expected output:**
```
Service: ai-agents-backend
Status:  Live
Plan:    Starter
Region:  Singapore  # 🇸🇬
Runtime: Docker
URL:     https://ai-agents-backend-xxxx.onrender.com
```

---

## 🧪 Post-Deployment Testing

### Test Endpoints

```powershell
python Render_backend\test_deployment.py https://ai-agents-backend-xxxx.onrender.com
```

**Tests:**
1. ✅ /health endpoint
2. ✅ /api/status
3. ✅ /api/tools (564 tools loaded)
4. ✅ CORS headers
5. ✅ Response times (should be ~100-150ms from Australia)
6. ✅ Database connection

### Latency Test from Australia

```powershell
# Test latency from your location
curl -w "\nTime: %{time_total}s\n" https://ai-agents-backend-xxxx.onrender.com/health
```

**Expected:**
- **Singapore:** 100-150ms ✅
- **Oregon:** 200-250ms ⚠️

---

## 🔧 OAuth Configuration (Post-Deployment)

### Update Redirect URLs

After deployment, update OAuth redirect URLs in:

**1. Google Cloud Console**
- Go to: https://console.cloud.google.com/apis/credentials
- Edit OAuth 2.0 Client: `AI Agents Platform`
- Add redirect URL: `https://ai-agents-backend-xxxx.onrender.com/api/auth/google/callback`

**2. Microsoft Azure Portal**
- Go to: https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps
- Edit app: `AI Agents Platform`
- Add redirect URL: `https://ai-agents-backend-xxxx.onrender.com/api/auth/microsoft/callback`

**Automated update script:**

```powershell
python Render_backend\update_oauth_redirects.py https://ai-agents-backend-xxxx.onrender.com
```

---

## 💰 Cost Optimization

### Starter Plan (Recommended Initially)

**Cost:** $7/month per service  
**Benefits:**
- Always-on (no spin down)
- Better performance
- Dedicated resources
- <100ms response time from Australia

### Free Plan (After Testing)

**Cost:** $0/month  
**Limitations:**
- Services spin down after 15 min inactivity
- 750 hours/month free compute
- 1-2 min cold start
- Shared resources

**Downgrade after testing:**

```powershell
python Render_backend\downgrade_to_free.py srv-xxxxx
```

---

## 🏗️ Advanced: Sandbox Code Execution

### Enable Code Execution Tools

Once deployed, you can add sandboxed code execution tools:

**1. Python Code Executor Tool**

```json
{
  "name": "execute_python_code",
  "description": "Execute Python code in isolated sandbox",
  "parameters": {
    "code": "string",
    "packages": "array",
    "timeout": "integer"
  }
}
```

**2. Data Analysis Tool**

```json
{
  "name": "analyze_data",
  "description": "Analyze CSV/Excel data with pandas",
  "parameters": {
    "data_url": "string",
    "analysis_code": "string"
  }
}
```

**3. Visualization Tool**

```json
{
  "name": "create_chart",
  "description": "Create charts from data using matplotlib",
  "parameters": {
    "data": "object",
    "chart_type": "string"
  }
}
```

### Security Considerations

**Docker provides isolation:**
- Code runs in separate container
- Limited CPU/memory per execution
- No access to main application files
- Timeout limits prevent runaway processes
- No network access (optional)

---

## 📝 Deployment Checklist

### Before Deployment

- [ ] Create `Dockerfile`
- [ ] Create `.dockerignore`
- [ ] Create `render.yaml` with **Singapore region**
- [ ] Extract environment variables (`render_env_vars.json`)
- [ ] Clean git secrets (`clean_git_secrets.py`)
- [ ] Push to GitHub branch `V2_clean`

### During Deployment

- [ ] Run `python Render_backend\render_deploy.py`
- [ ] Verify region is **Singapore**
- [ ] Monitor build progress
- [ ] Check for build errors

### After Deployment

- [ ] Test all endpoints
- [ ] Check latency from Australia (~100-150ms)
- [ ] Update OAuth redirect URLs
- [ ] Test OAuth flows (Google + Microsoft)
- [ ] Test tool execution (564 tools)
- [ ] Set up monitoring alerts

---

## 🆘 Troubleshooting

### Build Fails - Missing Dependencies

**Symptom:** Docker build fails during `pip install`

**Fix:** Check `requirements.txt` includes all packages

```powershell
# Test locally first
docker build -t ai-agents-test .
```

### Slow Response Times

**Symptom:** Response times >300ms from Australia

**Cause:** Service deployed to Oregon instead of Singapore

**Fix:** Check `render.yaml` has `region: singapore`

```yaml
services:
  - type: web
    region: singapore  # NOT oregon
```

### OAuth Not Working

**Symptom:** OAuth redirects fail with 400 error

**Cause:** Redirect URLs not updated in Google/Microsoft consoles

**Fix:** Run update script

```powershell
python Render_backend\update_oauth_redirects.py https://your-service.onrender.com
```

### Service Suspended

**Symptom:** Free tier service spins down after 15 min

**Cause:** Free plan limitation

**Fix:** Upgrade to Starter plan or accept cold starts

```powershell
# Upgrade to Starter (always-on)
# Via Render dashboard: Service Settings → Plan → Starter
```

---

## 📚 Additional Resources

### Documentation
- **Main deployment guide:** `Render_backend/DEPLOYMENT_GUIDE_FOR_AI.md`
- **Render API docs:** `Render_backend/README.md`
- **Docker reference:** Your `In_House_SQL/G_Folder/Dockerfile`

### Render Documentation
- Render Docker Guide: https://render.com/docs/docker
- Render Regions: https://render.com/docs/regions
- Render Environment Variables: https://render.com/docs/environment-variables

### Your Existing Docker Deployments
- **In_House_SQL Flask:** Working Docker deployment on Render
- **In_House_SQL Streamlit:** Working Docker deployment on Render
- **render.yaml reference:** `C:\Users\gpoli\GIT\In_House_SQL\G_Folder\render.yaml`

---

## 🎯 Summary

**Recommended Configuration for Australia:**

```yaml
Region: Singapore (not Oregon)
Deployment: Docker (for code execution)
Plan: Starter initially, downgrade to Free after testing
Branch: V2_clean (clean git history)
Build time: 5-8 minutes
Expected latency: 100-150ms from Australia
```

**Next Steps:**

1. Create `Dockerfile` (see Step 1 above)
2. Create `.dockerignore` (see Step 2 above)
3. Create `render.yaml` with Singapore region (see Step 3 above)
4. Run automated deployment:
   ```powershell
   python Render_backend\render_deploy.py
   ```
5. Monitor build and test deployment
6. Update OAuth redirect URLs
7. Test from Australia (verify <150ms latency)

**Deployment command:**

```powershell
cd C:\Users\gpoli\GIT\AI_agents
python Render_backend\render_deploy.py
```

---

**Last Updated:** November 8, 2025  
**Region:** Singapore (closest to Australia)  
**Deployment Type:** Docker (sandbox code execution support)  
**Status:** Ready for deployment
