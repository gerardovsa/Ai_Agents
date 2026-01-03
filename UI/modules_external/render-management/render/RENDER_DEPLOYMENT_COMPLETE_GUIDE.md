# MustCare ValorAISynergySuite - Complete Render.com Deployment Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Database Setup](#database-setup)
3. [Service Deployment](#service-deployment)
4. [Environment Configuration](#environment-configuration)
5. [CLI Tools Reference](#cli-tools-reference)
6. [Troubleshooting](#troubleshooting)
7. [Post-Deployment](#post-deployment)
8. [Multi-Client Deployment](#multi-client-deployment)

---

## 🎯 Prerequisites

### Required Accounts
- **Render.com Account** (Free tier sufficient for testing)
- **GitHub Account** with repository access
- **Anthropic API Key** for Claude integration

### Required Tools
- Git (for version control)
- Python 3.x (for deployment scripts)
- Web browser (for Render dashboard)

### Render API Key
1. Go to https://dashboard.render.com/account/settings
2. Scroll to "API Keys"
3. Click "Create New API Key"
4. Save the key securely (format: `rnd_...`)

---

## 🗄️ Database Setup

### Step 1: Create PostgreSQL Database

**Via Render Dashboard:**

1. Go to https://dashboard.render.com
2. Click "New +" → "PostgreSQL"
3. Configure database:
   - **Name**: `mustcare-postgres-v8` (or your choice)
   - **Database**: `mustcare_db`
   - **User**: `postgres` (auto-generated)
   - **Region**: `Singapore` (Southeast Asia)
   - **Plan**: `Free` (256MB RAM, 1GB storage)
   - **PostgreSQL Version**: `16`

4. Click "Create Database"
5. **Save the Database ID** (format: `dpg-...`)
6. **Save the Internal Database URL** from connection info

**Via API:**

```python
import requests

RENDER_API_KEY = 'rnd_YOUR_API_KEY'
OWNER_ID = 'tea_YOUR_OWNER_ID'  # From account settings

headers = {
    'Authorization': f'Bearer {RENDER_API_KEY}',
    'Content-Type': 'application/json'
}

database_payload = {
    "name": "mustcare-postgres-v8",
    "databaseName": "mustcare_db",
    "databaseUser": "postgres",
    "region": "singapore",
    "plan": "free",
    "ownerId": OWNER_ID
}

response = requests.post(
    'https://api.render.com/v1/postgres',
    headers=headers,
    json=database_payload
)

if response.status_code == 201:
    data = response.json()
    database_id = data.get('id')
    print(f"✅ Database created: {database_id}")
else:
    print(f"❌ Failed: {response.text}")
```

### Step 2: Get Database Connection String

```python
response = requests.get(
    f'https://api.render.com/v1/postgres/{database_id}',
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    connection_info = data.get('connectionInfo', {})
    
    # Internal URL (for services in same region)
    internal_url = connection_info.get('internalConnectionString')
    
    # External URL (for external connections)
    external_url = connection_info.get('externalConnectionString')
    
    print(f"Internal URL: {internal_url}")
    print(f"External URL: {external_url}")
```

---

## 🚀 Service Deployment

### Step 1: Prepare Repository

Ensure your repository has these files in the `render/` folder:

```
render/
├── Dockerfile.render          # Multi-stage Docker build
├── start.sh                    # Container startup script
├── deploy_final.py             # Automated deployment script
└── RENDER_DEPLOYMENT_COMPLETE_GUIDE.md (this file)
```

**Key Dockerfile Requirements:**
- Uses `npm install` (not `npm ci`) - no package-lock.json required
- Multi-stage build: frontend → server → collector → final
- PORT 10000 (Render requirement)
- Health check on `/api/v1/system/check`

### Step 2: Configure Deployment Script

Edit `render/deploy_final.py` and update:

```python
# Configuration
RENDER_API_KEY = 'rnd_YOUR_API_KEY'
ANTHROPIC_API_KEY = 'sk-ant-YOUR_KEY'
OWNER_ID = 'tea_YOUR_OWNER_ID'
DATABASE_ID = 'dpg_YOUR_DATABASE_ID'  # From Step 1
```

### Step 3: Run Deployment

```powershell
cd "C:\Users\YOUR_PATH\MustCare ValorAISynergySuite"
python render\deploy_final.py
```

**What the script does:**
1. ✅ Verifies database exists
2. ✅ Generates JWT secret
3. ✅ Prepares 15 environment variables
4. ✅ Creates web service via Render API
5. ✅ Sets Docker configuration
6. ✅ Triggers initial deployment

**Expected Output:**
```
======================================================================
 MUSTCARE VALORAI - FINAL DEPLOYMENT
======================================================================

STEP 1: Verifying Prerequisites
----------------------------------------------------------------------
✅ Database: mustcare-postgres-v8
   Connection: postgresql://postgres@dpg-...

STEP 2: Generating Secure Secrets
----------------------------------------------------------------------
✅ JWT Secret: H1BttCromO7ziRX...

STEP 3: Preparing Environment Variables
----------------------------------------------------------------------
  • ANTHROPIC_API_KEY: sk-ant-api03-...
  • JWT_SECRET: H1BttCromO7ziRX...
  • DATABASE_URL: postgresql://postgres@...
  • NODE_ENV: production
  • PORT: 10000
  • SERVER_PORT: 10000
  • COLLECTOR_PORT: 8888
  • STORAGE_DIR: /app/storage
  • VECTOR_DB_TYPE: lancedb
  • LLM_PROVIDER: anthropic
  • ANTHROPIC_MODEL: claude-sonnet-4-20250514
  • EMBEDDING_ENGINE: native
  • EMBEDDING_MODEL_PREF: nomic-embed-text-v1.5
  • DISABLE_TELEMETRY: true
  • AUTH_TOKEN: OLFksrqXh00aDhvPfN...

✅ 15 environment variables prepared

STEP 4: Creating Render Web Service
----------------------------------------------------------------------
Configuration:
  • Name: mustcare-valorai-final
  • Repository: gerardovsa/MustCare_ValorAISynergySuite
  • Branch: V8-Render
  • Region: Singapore (Southeast Asia)
  • Plan: Starter ($7/month)
  • Dockerfile: render/Dockerfile.render
  • Docker Context: . (repository root)
  • Health Check: /api/v1/system/check
  • Environment Variables: 15

Creating service...
Response Status: 201

======================================================================
 ✅ SERVICE CREATED SUCCESSFULLY!
======================================================================

Service ID: srv-...
Service Name: mustcare-valorai-final
Service URL: https://mustcare-valorai-final.onrender.com

Dashboard: https://dashboard.render.com/web/srv-...
```

### Step 4: Monitor Build Progress

**Option 1: CLI Monitor Tool (Recommended)**

```powershell
cd render
python deploy-monitor.py --watch
```

**Option 2: Dashboard**

Go to the dashboard URL provided and click the **"Logs"** tab to see real-time build output.

**Expected Build Stages (5-8 minutes with optimized Dockerfile):**

```
Stage 1: Frontend Build (~3 minutes)
  - Install dependencies (npm install)
  - Build React/Vite production bundle
  - Verify dist/ output

Stage 2: Final Image (~3 minutes)
  - Install server dependencies
  - Install collector dependencies
  - Copy built assets
  - Create storage directories
  - Deploy to Render

Stage 3: Health Check (~1 minute)
  - Verify server responds on PORT 10000
  - Check /api/v1/system/check endpoint
```

---

## ⚙️ Environment Configuration

### Required Environment Variables

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `ANTHROPIC_API_KEY` | Claude API key | `sk-ant-api03-...` |
| `JWT_SECRET` | Session encryption | Auto-generated 64-char string |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://postgres@dpg-...` |
| `NODE_ENV` | Environment | `production` |
| `PORT` | Main server port | `10000` (Render requirement) |
| `SERVER_PORT` | Server listen port | `10000` |
| `COLLECTOR_PORT` | Document processor | `8888` |
| `STORAGE_DIR` | Storage path | `/app/storage` |
| `VECTOR_DB_TYPE` | Vector database | `lancedb` |
| `LLM_PROVIDER` | AI provider | `anthropic` |
| `ANTHROPIC_MODEL` | Claude model | `claude-sonnet-4-20250514` |
| `EMBEDDING_ENGINE` | Embedding provider | `native` |
| `EMBEDDING_MODEL_PREF` | Embedding model | `nomic-embed-text-v1.5` |
| `DISABLE_TELEMETRY` | Disable tracking | `true` |
| `AUTH_TOKEN` | API authentication | Auto-generated 32-char string |

### Setting Environment Variables Manually

**Via Render Dashboard:**
1. Go to service dashboard
2. Click "Environment" in left sidebar
3. Click "Add Environment Variable"
4. Enter key and value
5. Click "Save Changes"
6. Redeploy service

**Via API:**

```python
import secrets

# Generate secure secrets
jwt_secret = secrets.token_urlsafe(64)
auth_token = secrets.token_urlsafe(32)

env_vars = {
    'ANTHROPIC_API_KEY': 'sk-ant-...',
    'JWT_SECRET': jwt_secret,
    'DATABASE_URL': 'postgresql://...',
    # ... (all 15 variables)
}

for key, value in env_vars.items():
    response = requests.put(
        f'https://api.render.com/v1/services/{service_id}/env-vars/{key}',
        headers=headers,
        json={'key': key, 'value': value}
    )
    print(f"{'✅' if response.status_code in [200,201] else '❌'} {key}")
```

---

## �️ CLI Tools Reference

### Available Tools

The `render/` folder contains professional CLI tools for deployment management:

```
render/
├── deploy-monitor.py           # 🎯 Real-time deployment monitoring
├── trigger_deploy.py           # 🚀 Manual deployment trigger
├── update_to_optimized.py      # ⚡ Switch to optimized Dockerfile
├── add_env_vars.py             # 🔧 Set environment variables
├── diagnose_service.py         # 🔍 Service diagnostics
├── check_current_status.py     # 📊 Quick status check
└── deploy_final.py             # 🏗️ Full automated deployment
```

### 1. Deployment Monitor - `deploy-monitor.py`

**Real-time deployment status with colored output.**

**Usage:**
```powershell
# Check once
python deploy-monitor.py

# Continuous monitoring
python deploy-monitor.py --watch

# Custom interval (15s)
python deploy-monitor.py -w -i 15
```

**Features:**
- Color-coded status ([BUILDING], [LIVE], [FAILED])
- Build stage tracking
- Duration calculation
- Auto-refresh mode

### 2. Other CLI Tools

- **`trigger_deploy.py`** - Trigger new deployment with cache clear
- **`update_to_optimized.py`** - Switch to optimized Dockerfile
- **`add_env_vars.py`** - Set all 15 environment variables
- **`diagnose_service.py`** - Validate service configuration
- **`check_current_status.py`** - View deployment history

**Recommendation:** Use `deploy-monitor.py --watch` during deployments for real-time feedback!

---

## �🔧 Troubleshooting

### Common Build Errors

#### 1. "npm ci: Cannot find package-lock.json"
**Error:**
```
npm error `npm ci` can only install packages when your package.json and package-lock.json are in sync
```

**Solution:**
Change `npm ci` to `npm install` in Dockerfile.render:
```dockerfile
# Before (❌)
RUN npm ci --legacy-peer-deps

# After (✅)
RUN npm install --legacy-peer-deps
```

#### 2. "Could not resolve './icons/google.png'"
**Error:**
```
RollupError: Could not resolve "./icons/google.png" from "src/pages/Admin/Agents/WebSearchSelection/index.jsx"
```

**Solution:**
Replace PNG import with placeholder icon:
```javascript
// Before (❌)
import GoogleSearchIcon from "./icons/google.png";

// After (✅)
const GoogleSearchIcon = AnythingLLMIcon;
```

#### 3. "Dockerfile not found"
**Error:**
```
error: failed to solve: failed to read dockerfile: open Dockerfile: no such file or directory
```

**Solution:**
Update Dockerfile path in service settings:
```python
# Via API
update_payload = {
    "serviceDetails": {
        "envSpecificDetails": {
            "dockerfilePath": "render/Dockerfile.render",  # ✅ Correct path
            "dockerContext": "."
        }
    }
}
```

#### 4. "Out of memory during build"
**Error:**
```
ERROR: failed to solve: process terminated with signal SIGKILL
```

**Solution:**
Upgrade to Starter plan (512MB → 2GB RAM) or use single-stage Dockerfile:
```dockerfile
# Use render/Dockerfile.simple instead
FROM node:20-slim
# ... (single-stage build with sequential installs)
```

#### 5. "Health check failing"
**Error:**
```
Health check failed: http://localhost:10000/api/v1/system/check returned 502
```

**Solution:**
Check start.sh exports PORT correctly:
```bash
export PORT=${PORT:-10000}
export SERVER_PORT=${PORT}
```

### Deployment Status Checks

```python
# Check deployment status
response = requests.get(
    f'https://api.render.com/v1/services/{service_id}/deploys?limit=1',
    headers=headers
)

deploys = response.json()
if deploys:
    deploy = deploys[0]['deploy']
    print(f"Status: {deploy.get('status')}")
    print(f"Started: {deploy.get('startedAt')}")
    print(f"Finished: {deploy.get('finishedAt')}")
```

**Deploy Statuses:**
- `build_in_progress` - Currently building
- `live` - Successfully deployed
- `build_failed` - Build encountered error
- `update_failed` - Deployment update failed

### Debug Commands

```powershell
# Verify files exist in repository
git ls-tree -r V8-Render --name-only | Select-String "render/Dockerfile"

# Check Docker syntax locally
docker build -f render/Dockerfile.render -t test .

# Test deployment script
python render/deploy_final.py

# Monitor deployment
python render/monitor_deployment.py
```

---

## ✅ Post-Deployment

### Step 1: Verify Service is Live

```bash
# Check health endpoint
curl https://mustcare-valorai-final.onrender.com/api/v1/system/check

# Expected response:
{
  "online": true,
  "LLMProvider": "anthropic",
  "vectorDB": "lancedb",
  "model": "claude-sonnet-4-20250514"
}
```

### Step 2: Access Application

**Frontend URL:**
```
https://mustcare-valorai-final.onrender.com
```

**Default Login:**
- Username: `admin`
- Password: Set during first-time setup

### Step 3: Configure First Workspace

1. Navigate to dashboard
2. Click "New Workspace"
3. Configure:
   - Name: MustCare Workspace
   - LLM: Anthropic Claude 4 Sonnet
   - Vector DB: LanceDB (default)
   - Embedding: Native (nomic-embed-text-v1.5)

4. Upload documents:
   - Navigate to workspace
   - Click "Upload Documents"
   - Select PDF/TXT/MD files
   - Wait for processing (collector service)

### Step 4: Test AI Chat

1. Open workspace
2. Click "Chat"
3. Send test message:
   ```
   Hello! Please summarize the uploaded documents.
   ```

4. Verify Claude 4 responds with document context

---

## 🏢 Multi-Client Deployment

### Architecture for Multiple Clients

```
Client A:
├── Service: mustcare-client-a
├── Database: mustcare-db-client-a
└── URL: https://clienta.yourdomain.com

Client B:
├── Service: mustcare-client-b
├── Database: mustcare-db-client-b
└── URL: https://clientb.yourdomain.com

Shared:
└── Blueprint: render.yaml (template for new clients)
```

### Step 1: Create Blueprint Template

Create `render.yaml` in repository root:

```yaml
services:
  - type: web
    name: mustcare-valorai-CLIENT_NAME
    env: docker
    region: singapore
    plan: starter
    branch: V8-Render
    dockerfilePath: render/Dockerfile.render
    dockerContext: .
    healthCheckPath: /api/v1/system/check
    envVars:
      - key: NODE_ENV
        value: production
      - key: PORT
        value: 10000
      - key: SERVER_PORT
        value: 10000
      - key: ANTHROPIC_API_KEY
        sync: false  # Set manually per client
      - key: JWT_SECRET
        generateValue: true
      - key: AUTH_TOKEN
        generateValue: true

databases:
  - name: mustcare-db-CLIENT_NAME
    databaseName: mustcare_db
    user: postgres
    region: singapore
    plan: free
```

### Step 2: Automated Client Deployment Script

Create `render/deploy_new_client.py`:

```python
"""
Deploy MustCare for a new client
Usage: python deploy_new_client.py --client="client-name" --api-key="sk-ant-..."
"""

import requests
import secrets
import argparse

def deploy_client(client_name, anthropic_api_key, render_api_key, owner_id):
    headers = {
        'Authorization': f'Bearer {render_api_key}',
        'Content-Type': 'application/json'
    }
    
    print(f"Deploying MustCare for client: {client_name}")
    print("="*70)
    
    # 1. Create database
    db_payload = {
        "name": f"mustcare-db-{client_name}",
        "databaseName": "mustcare_db",
        "databaseUser": "postgres",
        "region": "singapore",
        "plan": "free",
        "ownerId": owner_id
    }
    
    db_response = requests.post(
        'https://api.render.com/v1/postgres',
        headers=headers,
        json=db_payload
    )
    
    if db_response.status_code != 201:
        print(f"❌ Database creation failed: {db_response.text}")
        return
    
    database_id = db_response.json().get('id')
    print(f"✅ Database created: {database_id}")
    
    # 2. Get database URL
    db_info = requests.get(
        f'https://api.render.com/v1/postgres/{database_id}',
        headers=headers
    ).json()
    
    database_url = db_info.get('connectionInfo', {}).get('internalConnectionString')
    print(f"✅ Database URL retrieved")
    
    # 3. Create service
    service_payload = {
        "type": "web_service",
        "name": f"mustcare-{client_name}",
        "ownerId": owner_id,
        "repo": "https://github.com/gerardovsa/MustCare_ValorAISynergySuite",
        "branch": "V8-Render",
        "autoDeploy": "yes",
        "serviceDetails": {
            "env": "docker",
            "region": "singapore",
            "plan": "starter",
            "healthCheckPath": "/api/v1/system/check",
            "envSpecificDetails": {
                "dockerfilePath": "render/Dockerfile.render",
                "dockerContext": ".",
                "envVars": [
                    {"key": "ANTHROPIC_API_KEY", "value": anthropic_api_key},
                    {"key": "JWT_SECRET", "value": secrets.token_urlsafe(64)},
                    {"key": "DATABASE_URL", "value": database_url},
                    {"key": "NODE_ENV", "value": "production"},
                    {"key": "PORT", "value": "10000"},
                    {"key": "SERVER_PORT", "value": "10000"},
                    {"key": "COLLECTOR_PORT", "value": "8888"},
                    {"key": "STORAGE_DIR", "value": "/app/storage"},
                    {"key": "VECTOR_DB_TYPE", "value": "lancedb"},
                    {"key": "LLM_PROVIDER", "value": "anthropic"},
                    {"key": "ANTHROPIC_MODEL", "value": "claude-sonnet-4-20250514"},
                    {"key": "EMBEDDING_ENGINE", "value": "native"},
                    {"key": "EMBEDDING_MODEL_PREF", "value": "nomic-embed-text-v1.5"},
                    {"key": "DISABLE_TELEMETRY", "value": "true"},
                    {"key": "AUTH_TOKEN", "value": secrets.token_urlsafe(32)}
                ]
            }
        }
    }
    
    service_response = requests.post(
        'https://api.render.com/v1/services',
        headers=headers,
        json=service_payload
    )
    
    if service_response.status_code not in [200, 201]:
        print(f"❌ Service creation failed: {service_response.text}")
        return
    
    service_id = service_response.json().get('id')
    service_name = service_response.json().get('name')
    
    print(f"✅ Service created: {service_id}")
    print()
    print("="*70)
    print(" DEPLOYMENT COMPLETE")
    print("="*70)
    print(f"Client: {client_name}")
    print(f"Service URL: https://{service_name}.onrender.com")
    print(f"Database: {database_id}")
    print(f"Dashboard: https://dashboard.render.com/web/{service_id}")
    print()
    print("Build will take 8-12 minutes to complete.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--client', required=True, help='Client name (lowercase, hyphens)')
    parser.add_argument('--api-key', required=True, help='Anthropic API key for this client')
    parser.add_argument('--render-key', required=True, help='Render API key')
    parser.add_argument('--owner-id', required=True, help='Render owner ID')
    
    args = parser.parse_args()
    
    deploy_client(args.client, args.api_key, args.render_key, args.owner_id)
```

### Step 3: Deploy New Client

```powershell
python render/deploy_new_client.py `
  --client="acme-corp" `
  --api-key="sk-ant-api03-CLIENT_KEY" `
  --render-key="rnd_YOUR_RENDER_KEY" `
  --owner-id="tea_YOUR_OWNER_ID"
```

---

## 📊 Cost Estimation

### Per Client Costs (Render.com)

| Resource | Plan | Cost | Specs |
|----------|------|------|-------|
| Web Service | Starter | $7/month | 512MB RAM, 0.5 CPU |
| PostgreSQL | Free | $0 | 256MB RAM, 1GB storage |
| **Total** | | **$7/month** | per client |

### Scaling Options

**Upgrade Service:**
- Standard: $25/month (2GB RAM, 1 CPU)
- Pro: $85/month (8GB RAM, 4 CPU)

**Upgrade Database:**
- Basic: $7/month (1GB RAM, 10GB storage)
- Standard: $25/month (4GB RAM, 50GB storage)

---

## 🔐 Security Best Practices

### 1. API Keys
- ✅ Store Anthropic keys per client
- ✅ Rotate JWT secrets regularly
- ✅ Use different AUTH_TOKEN per service
- ❌ Never commit API keys to repository

### 2. Database
- ✅ Use internal connection strings (same region)
- ✅ Enable SSL connections
- ✅ Regular backups (Render auto-backups on paid plans)
- ❌ Don't expose database publicly

### 3. Service Access
- ✅ Use environment-based configs
- ✅ Enable health check monitoring
- ✅ Set up error notifications
- ❌ Don't use default passwords

---

## 📞 Support & Resources

### Official Documentation
- Render Docs: https://render.com/docs
- Render API: https://api-docs.render.com
- AnythingLLM: https://useanything.com

### Monitoring
- Service Dashboard: https://dashboard.render.com
- Logs: Service → Logs tab
- Metrics: Service → Metrics tab

### Common Commands Reference

```powershell
# Deploy new service
python render/deploy_final.py

# Deploy for new client
python render/deploy_new_client.py --client="name" --api-key="key"

# Monitor deployment
python render/monitor_deployment.py

# Check service status
curl https://SERVICE_NAME.onrender.com/api/v1/system/check

# View logs (requires Render CLI)
render logs -s SERVICE_ID

# Trigger redeploy
python -c "import requests; requests.post('https://api.render.com/v1/services/SERVICE_ID/deploys', headers={'Authorization':'Bearer API_KEY'}, json={'clearCache':'clear'})"
```

---

## ✨ Summary Checklist

- [ ] Render account created
- [ ] API key obtained
- [ ] PostgreSQL database created
- [ ] Database connection string saved
- [ ] Repository prepared (Dockerfile, start.sh)
- [ ] Deployment script configured
- [ ] Service deployed successfully
- [ ] Environment variables set
- [ ] Health check passing
- [ ] Application accessible
- [ ] First workspace created
- [ ] Documents uploaded and processed
- [ ] AI chat tested and working

**Congratulations! Your MustCare ValorAISynergySuite is now live on Render.com! 🎉**

---

**Last Updated:** November 9, 2025  
**Version:** 1.0  
**Branch:** V8-Render  
**Commit:** 4ee582e
