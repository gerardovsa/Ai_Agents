# Deployment Blueprint System - Multi-Version Strategy

## 🎯 Goal
Create a blueprint system where each new version (v11, v12, v13...) can be deployed to Render with automatic URL detection, requiring zero manual configuration.

---

## 📋 Blueprint Strategy

### Option 1: Branch-Based Deployment (Recommended)
Each version gets its own branch and Render service that automatically detects its URL.

```
Branch: v11 → Render Service: ai-agents-v11 → URL: https://ai-agents-v11.onrender.com
Branch: v12 → Render Service: ai-agents-v12 → URL: https://ai-agents-v12.onrender.com
Branch: v13 → Render Service: ai-agents-v13 → URL: https://ai-agents-v13.onrender.com
```

### Option 2: Environment-Based Deployment
Single codebase with different environment configurations.

```
Production: https://ai-agents.onrender.com
Staging: https://ai-agents-staging.onrender.com
Testing: https://ai-agents-test.onrender.com
```

---

## 🚀 Implementation Plan

### Step 1: Create Version Detection Script

**File: `scripts/detect_version.py`**
```python
#!/usr/bin/env python3
"""
Auto-detect deployment version from branch name or environment
Used during Docker build to embed version info
"""
import os
import subprocess
import json

def get_version_info():
    """Detect version from git branch or environment"""
    version_info = {
        'branch': 'unknown',
        'version': 'unknown',
        'commit': 'unknown',
        'expected_url': None
    }
    
    try:
        # Get current branch name
        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        version_info['branch'] = branch
        
        # Extract version number from branch (v10, v11, v12, etc.)
        if branch.startswith('v') and branch[1:].isdigit():
            version_num = branch[1:]
            version_info['version'] = version_num
            version_info['expected_url'] = f'https://ai-agents-v{version_num}.onrender.com'
        
        # Get commit hash
        commit = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        version_info['commit'] = commit
        
    except Exception as e:
        print(f"Warning: Could not detect version: {e}")
    
    # Check for environment override
    if os.getenv('VERSION_NUMBER'):
        version_info['version'] = os.getenv('VERSION_NUMBER')
        version_info['expected_url'] = f"https://ai-agents-v{os.getenv('VERSION_NUMBER')}.onrender.com"
    
    return version_info

if __name__ == '__main__':
    info = get_version_info()
    print(json.dumps(info, indent=2))
```

### Step 2: Enhanced URL Detection with Version Awareness

**File: `AI_infrastructure/utils/version_detector.py`**
```python
"""
Version-aware URL detection for multi-version deployments
Automatically detects which version is running and uses correct URL
"""
import os
import json
from pathlib import Path

class VersionDetector:
    def __init__(self):
        self.version_file = Path(__file__).parent.parent.parent / 'version_info.json'
        self.version_info = self._load_version_info()
    
    def _load_version_info(self):
        """Load version info embedded during Docker build"""
        if self.version_file.exists():
            with open(self.version_file, 'r') as f:
                return json.load(f)
        return {
            'branch': 'unknown',
            'version': 'unknown',
            'expected_url': None
        }
    
    def get_expected_frontend_url(self):
        """
        Get the expected frontend URL for this version
        Returns None if not set (will use smart detection)
        """
        # Priority 1: Environment variable (manual override)
        if os.getenv('FRONTEND_URL'):
            return os.getenv('FRONTEND_URL')
        
        # Priority 2: Version-based URL (from build time)
        if self.version_info.get('expected_url'):
            return self.version_info['expected_url']
        
        # Priority 3: Construct from version number
        version = self.version_info.get('version')
        if version and version != 'unknown':
            return f'https://ai-agents-v{version}.onrender.com'
        
        return None
    
    def get_version_number(self):
        """Get version number (10, 11, 12, etc.)"""
        return self.version_info.get('version', 'unknown')
    
    def get_branch_name(self):
        """Get git branch name"""
        return self.version_info.get('branch', 'unknown')
    
    def get_commit_hash(self):
        """Get git commit hash"""
        return self.version_info.get('commit', 'unknown')

# Global instance
version_detector = VersionDetector()
```

### Step 3: Update OAuth URL Helper with Version Awareness

**File: `AI_infrastructure/utils/oauth_url_helper.py` (Enhanced)**
```python
"""
OAuth URL Helper - Smart Frontend URL Detection with Version Awareness
"""
import os
from urllib.parse import urlparse
from flask import request, session
from .version_detector import version_detector

def get_frontend_url(request_obj, session_obj=None):
    """
    Get the correct frontend URL for OAuth redirects with version awareness
    
    Priority:
    1. Session storage (captured at OAuth start)
    2. Referer header
    3. Origin header
    4. Version-based expected URL (from build)
    5. FRONTEND_URL env var (manual override)
    6. request.url_root (fallback)
    """
    frontend_url = None
    detection_method = None
    
    # Priority 1: OAuth origin from session
    if session_obj and 'oauth_origin_url' in session_obj:
        frontend_url = session_obj['oauth_origin_url']
        detection_method = "session (oauth_origin_url)"
    
    # Priority 2: Referer header
    if not frontend_url and request_obj.referrer:
        parsed = urlparse(request_obj.referrer)
        frontend_url = f"{parsed.scheme}://{parsed.netloc}"
        detection_method = "Referer header"
    
    # Priority 3: Origin header
    if not frontend_url and request_obj.headers.get('Origin'):
        frontend_url = request_obj.headers.get('Origin')
        detection_method = "Origin header"
    
    # Priority 4: Version-based expected URL (NEW!)
    if not frontend_url:
        expected_url = version_detector.get_expected_frontend_url()
        if expected_url:
            frontend_url = expected_url
            detection_method = f"version detector (v{version_detector.get_version_number()})"
    
    # Priority 5: FRONTEND_URL environment variable
    if not frontend_url and os.getenv('FRONTEND_URL'):
        frontend_url = os.getenv('FRONTEND_URL')
        detection_method = "FRONTEND_URL env var"
    
    # Priority 6: request.url_root (fallback)
    if not frontend_url:
        frontend_url = request_obj.url_root.rstrip('/')
        detection_method = "request.url_root (fallback)"
    
    # Ensure HTTPS for Render
    if 'onrender.com' in frontend_url or os.getenv('RENDER') == 'true':
        frontend_url = frontend_url.replace('http://', 'https://')
    
    # Force HTTP for localhost
    if 'localhost' in frontend_url or '127.0.0.1' in frontend_url:
        frontend_url = frontend_url.replace('https://', 'http://')
    
    version_num = version_detector.get_version_number()
    print(f"🔀 [Frontend URL] Version {version_num} - Detected via {detection_method}: {frontend_url}")
    
    return frontend_url
```

### Step 4: Update Dockerfile to Embed Version Info

**File: `Dockerfile` (Add version detection)**
```dockerfile
# ... existing Dockerfile content ...

# NEW: Detect and embed version information
COPY scripts/detect_version.py /tmp/detect_version.py
RUN python3 /tmp/detect_version.py > /app/version_info.json && \
    cat /app/version_info.json && \
    rm /tmp/detect_version.py

# ... rest of Dockerfile ...
```

### Step 5: Create Deployment Blueprint Template

**File: `deployment_blueprints/render-vX-template.yaml`**
```yaml
# ========================================
# AI Agents Platform - Version X Deployment Blueprint
# ========================================
# Instructions:
# 1. Copy this file to render.yaml
# 2. Replace 'vX' with your version (v11, v12, etc.)
# 3. Push to corresponding branch
# 4. Render auto-deploys with correct URL detection

services:
  - type: web
    name: ai-agents-vX  # ← CHANGE THIS (e.g., ai-agents-v11)
    env: docker
    region: singapore
    plan: starter
    
    # Docker image from GitHub Container Registry
    image:
      url: ghcr.io/gerardovsa/ai_agents:vX  # ← CHANGE THIS
    
    # Repository configuration
    repo: https://github.com/gerardovsa/AI_agents
    branch: vX  # ← CHANGE THIS (e.g., v11)
    
    autoDeploy: true
    healthCheckPath: /health
    
    # Persistent disk
    disk:
      name: ai-agents-data-vX  # ← CHANGE THIS
      mountPath: /data
      sizeGB: 10
    
    # Environment variables
    envVars:
      - key: PYTHONUNBUFFERED
        value: "1"
      
      - key: PYTHONIOENCODING
        value: "utf-8"
      
      - key: RENDER
        value: "true"
      
      - key: ENVIRONMENT
        value: "production"
      
      - key: PORT
        value: "10000"
      
      # Version number (for URL detection)
      - key: VERSION_NUMBER
        value: "X"  # ← CHANGE THIS (e.g., 11, 12, 13)
      
      # Optional: Manual URL override (usually not needed)
      # - key: FRONTEND_URL
      #   value: "https://ai-agents-vX.onrender.com"
      
      # ... rest of environment variables ...
```

---

## 🔄 Deployment Workflow

### Creating a New Version (e.g., v11)

**Step 1: Create Branch**
```powershell
# From v10 branch
git checkout v10
git pull origin v10

# Create v11 branch
git checkout -b v11

# Update version marker
echo '{"version": "11"}' > VERSION
git add VERSION
git commit -m "chore: Initialize v11 branch"
git push origin v11
```

**Step 2: Create Render Service**
```powershell
# Copy blueprint
cp deployment_blueprints/render-vX-template.yaml render.yaml

# Edit render.yaml:
# - name: ai-agents-v11
# - image.url: ghcr.io/gerardovsa/ai_agents:v11
# - branch: v11
# - VERSION_NUMBER: "11"
# - disk.name: ai-agents-data-v11

git add render.yaml
git commit -m "feat: Configure v11 deployment"
git push origin v11
```

**Step 3: Configure GitHub Actions**

**File: `.github/workflows/docker-build-v11.yml`**
```yaml
name: Build and Push Docker Image (v11)

on:
  push:
    branches: [ v11 ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: gerardovsa/ai_agents

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract version from branch
        id: version
        run: |
          BRANCH_NAME=${GITHUB_REF#refs/heads/}
          echo "branch=$BRANCH_NAME" >> $GITHUB_OUTPUT
          echo "version=11" >> $GITHUB_OUTPUT
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:v11
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:v11-${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            VERSION_NUMBER=11
            BRANCH_NAME=v11
```

**Step 4: Create Render Service**
1. Go to Render Dashboard: https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your repository
4. Configure:
   - **Name**: `ai-agents-v11`
   - **Branch**: `v11`
   - **Environment**: `Docker`
   - **Region**: `Singapore`
   - Use the `render.yaml` configuration
5. Click "Create Web Service"

**Step 5: Verify Deployment**
```powershell
# Check GitHub Actions
# Visit: https://github.com/gerardovsa/AI_agents/actions

# Wait for build to complete

# Test the deployment
curl https://ai-agents-v11.onrender.com/health

# Test OAuth flow
# Visit: https://ai-agents-v11.onrender.com
# Login with Google
# Verify URL stays on v11
```

---

## 🛠️ Automation Scripts

### Script 1: Create New Version
**File: `scripts/create_new_version.ps1`**
```powershell
<#
.SYNOPSIS
    Create a new deployment version
.EXAMPLE
    .\scripts\create_new_version.ps1 -Version 11
#>
param(
    [Parameter(Mandatory=$true)]
    [int]$Version
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Creating deployment version v$Version..." -ForegroundColor Cyan

# Check if branch already exists
$branchExists = git branch --list "v$Version"
if ($branchExists) {
    Write-Host "❌ Branch v$Version already exists!" -ForegroundColor Red
    exit 1
}

# Get latest from current branch
Write-Host "📥 Pulling latest changes..." -ForegroundColor Yellow
git pull

# Create new branch
Write-Host "🌿 Creating branch v$Version..." -ForegroundColor Yellow
git checkout -b "v$Version"

# Create version file
Write-Host "📝 Creating version marker..." -ForegroundColor Yellow
@{version=$Version} | ConvertTo-Json | Out-File -FilePath "VERSION" -Encoding UTF8
git add VERSION

# Copy and update render.yaml
Write-Host "⚙️  Configuring deployment..." -ForegroundColor Yellow
if (Test-Path "deployment_blueprints/render-vX-template.yaml") {
    $renderConfig = Get-Content "deployment_blueprints/render-vX-template.yaml" -Raw
    $renderConfig = $renderConfig -replace 'vX', "v$Version"
    $renderConfig = $renderConfig -replace 'value: "X"', "value: `"$Version`""
    $renderConfig | Out-File -FilePath "render.yaml" -Encoding UTF8
    git add render.yaml
}

# Create GitHub Actions workflow
Write-Host "🔧 Creating GitHub Actions workflow..." -ForegroundColor Yellow
$workflowTemplate = Get-Content ".github/workflows/docker-build-v10.yml" -Raw
$workflowContent = $workflowTemplate -replace 'v10', "v$Version"
$workflowContent = $workflowContent -replace 'version=10', "version=$Version"
$workflowContent | Out-File -FilePath ".github/workflows/docker-build-v$Version.yml" -Encoding UTF8
git add ".github/workflows/docker-build-v$Version.yml"

# Commit changes
Write-Host "💾 Committing changes..." -ForegroundColor Yellow
git commit -m "feat: Initialize v$Version deployment branch"

# Push to origin
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Yellow
git push origin "v$Version"

Write-Host "`n✅ Version v$Version created successfully!" -ForegroundColor Green
Write-Host "`n📋 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Go to Render Dashboard: https://dashboard.render.com" -ForegroundColor White
Write-Host "  2. Create new Web Service:" -ForegroundColor White
Write-Host "     - Name: ai-agents-v$Version" -ForegroundColor Yellow
Write-Host "     - Branch: v$Version" -ForegroundColor Yellow
Write-Host "     - Region: Singapore" -ForegroundColor Yellow
Write-Host "  3. Wait for GitHub Actions to build Docker image" -ForegroundColor White
Write-Host "  4. Render will auto-deploy" -ForegroundColor White
Write-Host "  5. Test: https://ai-agents-v$Version.onrender.com`n" -ForegroundColor Green
```

### Script 2: Quick Deploy Script
**File: `scripts/quick_deploy.ps1`**
```powershell
<#
.SYNOPSIS
    Quick deploy current version
.EXAMPLE
    .\scripts\quick_deploy.ps1
#>

$ErrorActionPreference = "Stop"

# Detect current version
$branch = git rev-parse --abbrev-ref HEAD
Write-Host "🔍 Current branch: $branch" -ForegroundColor Cyan

if ($branch -match '^v(\d+)$') {
    $version = $Matches[1]
    Write-Host "✅ Detected version: $version" -ForegroundColor Green
} else {
    Write-Host "❌ Not on a version branch (expected v10, v11, etc.)" -ForegroundColor Red
    exit 1
}

# Commit and push
Write-Host "📤 Deploying v$version..." -ForegroundColor Yellow
git add .
git commit -m "deploy: Update v$version deployment"
git push origin "v$version"

Write-Host "✅ Deployed! GitHub Actions will build and Render will deploy." -ForegroundColor Green
Write-Host "🔗 Monitor: https://github.com/gerardovsa/AI_agents/actions" -ForegroundColor Cyan
Write-Host "🌐 URL: https://ai-agents-v$version.onrender.com" -ForegroundColor Cyan
```

---

## 📊 Version Management Dashboard

**File: `scripts/list_versions.ps1`**
```powershell
<#
.SYNOPSIS
    List all deployed versions
#>

Write-Host "`n📊 Deployed Versions:" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

# List local branches
$branches = git branch -a | Select-String 'v\d+' | ForEach-Object {
    $_ -replace '.*/(v\d+).*', '$1'
} | Select-Object -Unique | Sort-Object

foreach ($branch in $branches) {
    if ($branch -match 'v(\d+)') {
        $version = $Matches[1]
        $url = "https://ai-agents-v$version.onrender.com"
        
        Write-Host "`nVersion: " -NoNewline -ForegroundColor Yellow
        Write-Host "v$version" -ForegroundColor White
        Write-Host "URL:     " -NoNewline -ForegroundColor Yellow
        Write-Host $url -ForegroundColor Cyan
        Write-Host "Status:  " -NoNewline -ForegroundColor Yellow
        
        try {
            $response = Invoke-WebRequest -Uri "$url/health" -TimeoutSec 5 -ErrorAction Stop
            Write-Host "🟢 Online" -ForegroundColor Green
        } catch {
            Write-Host "🔴 Offline" -ForegroundColor Red
        }
    }
}

Write-Host "`n" + ("=" * 60) -ForegroundColor Gray
```

---

## ✅ Benefits of This System

1. **Zero Manual Configuration**: Each version auto-detects its URL
2. **Clean Separation**: Each version has its own branch, service, and database
3. **Easy Rollback**: Keep old versions running during transition
4. **A/B Testing**: Run multiple versions simultaneously
5. **Parallel Development**: Teams can work on different versions
6. **Simple Creation**: One command creates new version
7. **Consistent URLs**: Predictable naming pattern (v11, v12, v13...)

---

## 🚀 Quick Start Guide

```powershell
# Create v11
.\scripts\create_new_version.ps1 -Version 11

# Deploy updates to v11
git checkout v11
# Make changes...
.\scripts\quick_deploy.ps1

# List all versions
.\scripts\list_versions.ps1
```

---

**Last Updated**: November 29, 2025  
**Status**: ✅ Blueprint Ready  
**Next Action**: Create scripts and test with v11 deployment
