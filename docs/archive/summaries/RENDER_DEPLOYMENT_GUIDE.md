# AI-Powered Multi-Platform Intelligence Suite - Render.com Deployment

**Platform**: Render.com  
**Cost**: Starts FREE, scales to $7-25/month  
**Deployment Time**: 15 minutes

---

## 🎯 Why Render.com?

### Advantages
✅ **Free Tier**: Includes PostgreSQL database, Redis, web services  
✅ **Auto-Deploy**: Push to GitHub = automatic deployment  
✅ **Docker Support**: Full Docker/Docker Compose support  
✅ **Managed Database**: PostgreSQL, Redis included  
✅ **SSL/HTTPS**: Automatic SSL certificates  
✅ **Zero DevOps**: No server management needed  
✅ **Easy Scaling**: Upgrade plans with one click  

### Render vs Traditional VPS
| Feature | Render.com | DigitalOcean VPS | AWS EC2 |
|---------|------------|------------------|---------|
| **Setup Time** | 15 min | 2-4 hours | 4-8 hours |
| **Free Tier** | Yes (limited) | No | Yes (1 year) |
| **Managed DB** | Yes | No | Optional |
| **Auto SSL** | Yes | Manual | Manual |
| **Auto Scaling** | Yes | Manual | Manual |
| **DevOps Skills** | None | Moderate | Advanced |

---

## 🏗️ Architecture on Render.com

```
┌─────────────────────────────────────────────────────────────────┐
│                    Render.com Infrastructure                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Web Service (Docker)                                    │   │
│  │  - FastAPI Backend                                       │   │
│  │  - Tool Registry (281 tools)                            │   │
│  │  - AI Orchestration                                      │   │
│  │  - URL: https://ai-suite.onrender.com                   │   │
│  │  - Auto-deploy from GitHub                              │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     │                                            │
│  ┌──────────────────▼───────────────────────────────────────┐   │
│  │  PostgreSQL (Managed)                                    │   │
│  │  - Free: 256 MB RAM, 1 GB Storage                       │   │
│  │  - Paid: 1-4 GB RAM, 10-100 GB Storage                 │   │
│  │  - Auto-backups                                          │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     │                                            │
│  ┌──────────────────▼───────────────────────────────────────┐   │
│  │  Redis (Managed)                                         │   │
│  │  - Free: 25 MB                                           │   │
│  │  - Paid: 100 MB - 2 GB                                  │   │
│  │  - Used for caching & job queue                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Background Worker (Optional)                            │  │
│  │  - Process long-running jobs                             │  │
│  │  - Document generation queue                             │  │
│  │  - Email sending queue                                   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

External Services (Not on Render):
├─ ONLYOFFICE Document Server (separate Docker host or cloud)
├─ OpenAI API (external)
├─ Anthropic API (external)
├─ Google Workspace APIs (external)
└─ Supabase (external database option)
```

---

## 📋 Deployment Steps

### Step 1: Prepare Repository (5 minutes)

Create `render.yaml` in project root:

```yaml
# render.yaml - Render Blueprint for AI Suite
services:
  # ============================================================================
  # Main Web Service - FastAPI Backend
  # ============================================================================
  - type: web
    name: ai-suite-backend
    runtime: docker
    region: oregon  # Choose: oregon, frankfurt, singapore
    plan: starter  # Free tier: use 'free', Paid: 'starter' ($7/mo)
    dockerfilePath: ./Dockerfile
    dockerContext: .
    envVars:
      # ONLYOFFICE (external)
      - key: ONLYOFFICE_SERVER_URL
        sync: false
      - key: ONLYOFFICE_JWT_SECRET
        generateValue: true  # Auto-generate secure secret
      
      # AI Model APIs
      - key: OPENAI_API_KEY
        sync: false
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: DEEPSEEK_API_KEY
        sync: false
      
      # Google Workspace OAuth2
      - key: GOOGLE_CLIENT_ID
        sync: false
      - key: GOOGLE_CLIENT_SECRET
        sync: false
      
      # Database (use Render PostgreSQL or Supabase)
      - key: DATABASE_URL
        fromDatabase:
          name: ai-suite-postgres
          property: connectionString
      - key: REDIS_URL
        fromDatabase:
          name: ai-suite-redis
          property: connectionString
      
      # Supabase (alternative to Render PostgreSQL)
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
      
      # E-Commerce & Payments
      - key: STRIPE_SECRET_KEY
        sync: false
      - key: WOOCOMMERCE_URL
        sync: false
      - key: WOOCOMMERCE_KEY
        sync: false
      - key: WOOCOMMERCE_SECRET
        sync: false
      - key: PAYPAL_CLIENT_ID
        sync: false
      - key: PAYPAL_SECRET
        sync: false
      
      # Communications
      - key: TWILIO_ACCOUNT_SID
        sync: false
      - key: TWILIO_AUTH_TOKEN
        sync: false
      - key: SLACK_BOT_TOKEN
        sync: false
      
      # Social Media
      - key: INSTAGRAM_ACCESS_TOKEN
        sync: false
      
      # Application Settings
      - key: ENVIRONMENT
        value: production
      - key: LOG_LEVEL
        value: INFO
      - key: ALLOWED_ORIGINS
        value: https://ai-suite.onrender.com,https://yourdomain.com
    
    healthCheckPath: /health
    autoDeploy: true  # Auto-deploy on git push
    
  # ============================================================================
  # Background Worker (Optional - for heavy processing)
  # ============================================================================
  - type: worker
    name: ai-suite-worker
    runtime: docker
    dockerfilePath: ./Dockerfile.worker
    dockerContext: .
    plan: starter
    envVars:
      - fromGroup: ai-suite-backend  # Inherit env vars from web service

# ============================================================================
# Databases (Managed by Render)
# ============================================================================
databases:
  # PostgreSQL
  - name: ai-suite-postgres
    databaseName: ai_suite_db
    user: ai_suite_user
    plan: free  # Free: 256 MB RAM, Paid: starter ($7/mo)
    region: oregon
    
  # Redis
  - name: ai-suite-redis
    plan: free  # Free: 25 MB, Paid: starter ($10/mo)
    region: oregon
    maxmemoryPolicy: allkeys-lru  # Cache eviction policy
```

---

### Step 2: Create Render-Optimized Dockerfile

Create `Dockerfile` in project root:

```dockerfile
# Dockerfile for Render.com - Optimized for fast builds
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p logs temp uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port (Render uses PORT env var)
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Start application (Render provides $PORT automatically)
CMD uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2
```

---

### Step 3: Update `requirements.txt`

```txt
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
psycopg2-binary==2.9.9  # For PostgreSQL
redis==5.0.1
sqlalchemy==2.0.23

# Google APIs
google-api-python-client==2.108.0
google-auth==2.25.0
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0

# AI Model SDKs
openai==1.6.1
anthropic==0.8.1
# deepseek (add if available on PyPI)

# Platform Integration SDKs
stripe==7.8.0
twilio==8.11.0
slack-sdk==3.26.1
facebook-sdk==3.1.0  # For Instagram
paypalrestsdk==1.13.3

# Cloud & Infrastructure
assemblyai==0.24.0
cloudconvert==2.1.0
PyGithub==2.1.1
pyngrok==7.0.5

# WooCommerce & E-commerce
woocommerce==3.0.0

# Supabase
supabase==2.3.0

# Utilities
python-dotenv==1.0.0
python-multipart==0.0.6
aiofiles==23.2.1
httpx==0.25.2
requests==2.31.0

# Job Queue (for background worker)
celery==5.3.4
celery[redis]==5.3.4

# Monitoring & Logging
sentry-sdk==1.39.1
python-json-logger==2.0.7
```

---

### Step 4: Create `main.py` (FastAPI Entry Point)

```python
#!/usr/bin/env python3
"""
AI-Powered Multi-Platform Intelligence Suite
FastAPI Backend for Render.com Deployment
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sentry_sdk

# Import tool registry
from tools.registry import ToolRegistry

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Sentry (optional)
if os.getenv('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        environment=os.getenv('ENVIRONMENT', 'production'),
        traces_sample_rate=0.1
    )

# Global tool registry
tool_registry = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    global tool_registry
    
    # Startup
    logger.info("🚀 Starting AI Suite Backend...")
    tool_registry = ToolRegistry()
    tools = tool_registry.list_tools()
    logger.info(f"✅ Loaded {len(tools)} tools across {len(set(t['platform'] for t in tools))} platforms")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down AI Suite Backend...")

# Create FastAPI app
app = FastAPI(
    title="AI-Powered Multi-Platform Intelligence Suite",
    description="Unified API for 281 tools across 19 platforms",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Health check endpoint (required by Render)
@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {
        "status": "healthy",
        "environment": os.getenv('ENVIRONMENT', 'unknown'),
        "tools_loaded": len(tool_registry.list_tools()) if tool_registry else 0
    }

# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "AI-Powered Multi-Platform Intelligence Suite",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "tools": "/api/tools"
    }

# List all available tools
@app.get("/api/tools")
async def list_tools():
    """List all available tools"""
    if not tool_registry:
        raise HTTPException(status_code=503, detail="Tool registry not initialized")
    
    tools = tool_registry.list_tools()
    
    # Group by platform
    platforms = {}
    for tool in tools:
        platform = tool['platform']
        if platform not in platforms:
            platforms[platform] = []
        platforms[platform].append(tool['name'])
    
    return {
        "total_tools": len(tools),
        "total_platforms": len(platforms),
        "platforms": platforms
    }

# Execute tool endpoint
@app.post("/api/tools/{tool_name}")
async def execute_tool(tool_name: str, parameters: dict):
    """Execute a specific tool"""
    if not tool_registry:
        raise HTTPException(status_code=503, detail="Tool registry not initialized")
    
    try:
        tool = tool_registry.get_tool(tool_name)
        result = await tool.execute(**parameters)
        return {
            "success": True,
            "tool": tool_name,
            "result": result
        }
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "type": type(exc).__name__
        }
    )

# Import API routers (add as you build features)
# from api.routes import gmail, docs, forms, ai, workflows
# app.include_router(gmail.router, prefix="/api/gmail", tags=["Gmail"])
# app.include_router(docs.router, prefix="/api/docs", tags=["Google Docs"])
# app.include_router(forms.router, prefix="/api/forms", tags=["Google Forms"])
# app.include_router(ai.router, prefix="/api/ai", tags=["AI Models"])
# app.include_router(workflows.router, prefix="/api/workflows", tags=["Workflows"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv('ENVIRONMENT') == 'development'
    )
```

---

### Step 5: Deploy to Render (5 minutes)

#### Option A: Deploy via Dashboard (Easy)

1. **Sign up**: https://render.com (free account)

2. **Connect GitHub**:
   - Go to Dashboard → New → Blueprint
   - Connect your GitHub repository
   - Select branch: `google-extension` or `main`

3. **Select `render.yaml`**:
   - Render auto-detects the blueprint
   - Click "Apply"

4. **Add Environment Variables**:
   - Dashboard → Environment
   - Add all API keys (see list below)
   - Click "Save"

5. **Deploy**:
   - Render automatically builds and deploys
   - Wait 5-10 minutes for first build
   - Your app will be live at: `https://ai-suite.onrender.com`

#### Option B: Deploy via CLI (Advanced)

```bash
# Install Render CLI
npm install -g render-cli

# Login
render login

# Create blueprint
render blueprint create

# Deploy
render blueprint deploy --file render.yaml
```

---

### Step 6: ONLYOFFICE Deployment Options on Render

**Challenge**: Render doesn't support Docker Compose, so ONLYOFFICE needs separate hosting.

#### Option 1: Deploy ONLYOFFICE on Render (Separate Service)
```yaml
# Add to render.yaml
  - type: web
    name: onlyoffice-documentserver
    runtime: docker
    dockerfilePath: ./Dockerfile.onlyoffice
    plan: standard  # Requires $25/mo plan (2 GB RAM minimum)
    envVars:
      - key: JWT_SECRET
        generateValue: true
    disk:
      name: onlyoffice-data
      mountPath: /var/www/onlyoffice/Data
      sizeGB: 10
```

**Cost**: $25/month  
**Pros**: Same platform, easy management  
**Cons**: More expensive than alternatives

#### Option 2: Use ONLYOFFICE Cloud (Recommended for MVP)
```bash
# Sign up for free tier
# https://www.onlyoffice.com/docspace-registration

# Get API credentials
ONLYOFFICE_SERVER_URL=https://your-docspace.onlyoffice.com
ONLYOFFICE_JWT_SECRET=your_jwt_secret
```

**Cost**: FREE (5 users), then $5-10/user/month  
**Pros**: Managed, no infrastructure, free tier  
**Cons**: Not self-hosted, requires internet

#### Option 3: Deploy ONLYOFFICE on DigitalOcean (Best Value)
```bash
# Use DigitalOcean App Platform or Droplet
# Deploy ONLYOFFICE Docker container
# Connect to Render backend via HTTPS

# DigitalOcean 1-Click App
https://marketplace.digitalocean.com/apps/onlyoffice-docs
```

**Cost**: $6/month (1 GB Droplet)  
**Pros**: Cheap, self-hosted, full control  
**Cons**: Separate platform to manage

#### Option 4: Use Google Docs API Instead (No ONLYOFFICE)
```python
# For MVP, use Google Docs tools instead
# Already have 19 Google Docs tools implemented
# No additional infrastructure needed
```

**Cost**: FREE (with Google Workspace account)  
**Pros**: No infrastructure, use existing tools  
**Cons**: Not self-hosted, requires Google account

**Recommendation**: Start with **Option 4 (Google Docs)** for MVP, then add **Option 3 (DigitalOcean)** for ONLYOFFICE later.

---

## 💰 Cost Breakdown

### Free Tier (Perfect for MVP/Testing)
| Service | Cost | Limits |
|---------|------|--------|
| Web Service | **FREE** | 750 hrs/mo, sleeps after 15 min inactivity |
| PostgreSQL | **FREE** | 256 MB RAM, 1 GB storage |
| Redis | **FREE** | 25 MB |
| SSL Certificate | **FREE** | Auto-renewed |
| Custom Domain | **FREE** | CNAME setup |
| **TOTAL** | **$0/month** | Great for testing |

### Production Tier (Recommended)
| Service | Cost | Specs |
|---------|------|-------|
| Web Service (Starter) | **$7/mo** | Always on, 512 MB RAM |
| PostgreSQL (Starter) | **$7/mo** | 1 GB RAM, 10 GB storage |
| Redis (Starter) | **$10/mo** | 100 MB |
| Background Worker | **$7/mo** | Optional, for heavy jobs |
| **TOTAL** | **$24-31/mo** | Production-ready |

### Scale Tier (High Traffic)
| Service | Cost | Specs |
|---------|------|-------|
| Web Service (Standard) | **$25/mo** | 2 GB RAM, auto-scale |
| PostgreSQL (Standard) | **$25/mo** | 4 GB RAM, 100 GB storage |
| Redis (Standard) | **$50/mo** | 1 GB |
| Background Workers (2x) | **$50/mo** | Parallel processing |
| **TOTAL** | **$150/mo** | Enterprise scale |

**Comparison**: 
- Render Production: **$24/mo**
- Traditional VPS + DevOps: **$40/mo + 20 hours setup**
- AWS Managed Services: **$100+/mo**

---

## 🚀 Post-Deployment Checklist

### 1. Verify Deployment
```bash
# Test health endpoint
curl https://ai-suite.onrender.com/health

# Expected response:
# {"status": "healthy", "tools_loaded": 281}

# List all tools
curl https://ai-suite.onrender.com/api/tools

# Execute a tool
curl -X POST https://ai-suite.onrender.com/api/tools/gmail_send_email \
  -H "Content-Type: application/json" \
  -d '{"to": ["test@example.com"], "subject": "Test", "body": "Hello"}'
```

### 2. Set Up Custom Domain (Optional)
```bash
# Render Dashboard → Settings → Custom Domain
# Add CNAME record:
# api.yourdomain.com → ai-suite.onrender.com
```

### 3. Configure Auto-Deploy
```bash
# Render Dashboard → Settings → Build & Deploy
# ✅ Auto-Deploy: Yes
# Branch: google-extension (or main)

# Now: git push = automatic deployment
git add .
git commit -m "Deploy to Render"
git push origin google-extension
```

### 4. Set Up Monitoring
```bash
# Option 1: Render Built-in Metrics
# Dashboard → Metrics → View logs, CPU, memory

# Option 2: Sentry (Error Tracking)
# Add to .env:
SENTRY_DSN=https://xxx@sentry.io/xxx

# Option 3: Datadog (Advanced)
# Add to render.yaml:
  - key: DD_API_KEY
    sync: false
```

### 5. Configure Backups
```bash
# PostgreSQL auto-backups enabled by default
# Manual backup:
# Dashboard → Database → Backups → Create Backup

# Download backup:
# Dashboard → Database → Backups → Download
```

---

## 🔧 Development Workflow

### Local Development
```bash
# 1. Clone repo
git clone https://github.com/gerardovsa/Valor_AI_Sidebar.git
cd AI_agents

# 2. Create .env file
cp .env.example .env
# Add your API keys

# 3. Run locally
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py

# 4. Test at http://localhost:8000
```

### Deploy to Render
```bash
# 1. Make changes
git add .
git commit -m "Add new feature"

# 2. Push to GitHub
git push origin google-extension

# 3. Render auto-deploys
# Check logs: render logs -f ai-suite-backend
```

### Rollback if Needed
```bash
# Render Dashboard → Deploys → Select previous deploy → Redeploy
# Or via CLI:
render deploys rollback ai-suite-backend --deploy-id dep_xxx
```

---

## 🎯 Next Steps

### Immediate (This Week)
1. ✅ Deploy to Render free tier
2. ⏳ Test all API endpoints
3. ⏳ Add AI model tools (OpenAI, Anthropic, DeepSeek)
4. ⏳ Implement Gmail tools
5. ⏳ Create first workflow (customer quote automation)

### Short-term (Next 2 Weeks)
1. Upgrade to Render Starter plan ($24/mo)
2. Implement Google Docs tools
3. Implement Google Forms tools
4. Add custom domain
5. Set up Sentry monitoring

### Medium-term (Next Month)
1. Deploy ONLYOFFICE on DigitalOcean
2. Add background worker for heavy processing
3. Implement remaining platforms (Instagram, PayPal, etc.)
4. Build admin dashboard UI
5. Scale to Standard plan if needed

---

## 🐛 Troubleshooting

### Issue: Deployment Failed
```bash
# Check build logs
render logs ai-suite-backend --build

# Common fix: Missing dependency
# Add to requirements.txt and redeploy
```

### Issue: Service Sleeping (Free Tier)
```bash
# Symptom: First request takes 30+ seconds
# Cause: Free tier sleeps after 15 min inactivity

# Solution 1: Upgrade to Starter ($7/mo) - Always on
# Solution 2: Use UptimeRobot to ping every 10 minutes
# https://uptimerobot.com (free)
```

### Issue: Database Connection Error
```bash
# Check DATABASE_URL is set correctly
render env get DATABASE_URL --service ai-suite-backend

# Test connection
python -c "import psycopg2; conn = psycopg2.connect('$DATABASE_URL'); print('✅ Connected')"
```

### Issue: High Memory Usage
```bash
# Monitor memory
render metrics ai-suite-backend

# Solution: Reduce workers in Dockerfile
# Change: --workers 2
# To: --workers 1
```

---

## 🎉 Deployment Complete!

You now have a **production-ready AI-powered platform** on Render.com with:

✅ **Auto-scaling infrastructure**  
✅ **Managed database (PostgreSQL + Redis)**  
✅ **Automatic SSL/HTTPS**  
✅ **Auto-deploy from GitHub**  
✅ **281 tools across 19 platforms**  
✅ **Health monitoring**  
✅ **Cost: $0-31/month** (vs $684/month for SaaS alternatives)

**Your API is live at**: `https://ai-suite.onrender.com`

### What's Different from Local Setup?
- ✅ **No Docker needed** (Render handles it)
- ✅ **No server management** (Render manages it)
- ✅ **Auto-scaling** (Render scales automatically)
- ✅ **Global CDN** (Fast worldwide)
- ✅ **DDoS protection** (Built-in security)

**Ready to deploy?** Push your code and watch it go live! 🚀
