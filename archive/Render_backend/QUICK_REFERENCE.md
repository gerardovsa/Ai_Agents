# RENDER CLI - QUICK REFERENCE CARD

**Fast command reference for Render.com project management**

---

## Setup

```powershell
# Set API key (one time)
$env:RENDER_API_KEY="rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu"

# Navigate to Render_backend
cd c:\Users\gpoli\GIT\AI_agents\Render_backend
```

---

## Most Common Commands (90% of Usage)

```powershell
# List all services
python render_complete_cli.py services list

# Check status of all services
python render_complete_cli.py status overview

# Get specific service details
python render_complete_cli.py services get srv-d40tai15pdvs73ddh4m0

# Restart a service
python render_complete_cli.py services restart srv-d40tai15pdvs73ddh4m0

# Check service health
python render_complete_cli.py health check srv-d40tai15pdvs73ddh4m0

# AI Agents quick status
python render_complete_cli.py quick status
```

---

## Environment Variables (Critical for Deployment)

```powershell
# List env vars
python render_complete_cli.py env list srv-xxxxx

# Set single var
python render_complete_cli.py env set srv-xxxxx PORT 10000

# Export all vars to file
python render_complete_cli.py env export srv-xxxxx backup.env

# Import vars from file
python render_complete_cli.py env import srv-xxxxx config.env
```

---

## Deployment Commands

```powershell
# Validate render.yaml
python render_complete_cli.py blueprint validate ..\render.yaml

# Get Singapore deployment guide
python render_complete_cli.py quick singapore

# Trigger manual deploy
python render_complete_cli.py deploys trigger srv-xxxxx

# Trigger with cache clear (full rebuild)
python render_complete_cli.py deploys trigger srv-xxxxx --clear-cache

# View deploy history
python render_complete_cli.py deploys list srv-xxxxx
```

---

## Service Management

```powershell
# Delete service (with confirmation)
python render_complete_cli.py services delete srv-xxxxx

# Create service from config
python render_complete_cli.py services create service-config.json

# Scale service (shows dashboard link)
python render_complete_cli.py services scale srv-xxxxx 3
```

---

## Current AI Agents Service

**Oregon Service (needs migration):**
```
ID:     srv-d40tai15pdvs73ddh4m0
URL:    https://ai-agents-backend-2oi8.onrender.com
Region: Oregon (⚠️ should be Singapore)
Env:    Python (⚠️ should be Docker)
```

**Quick Commands:**
```powershell
# Check status
python render_complete_cli.py services get srv-d40tai15pdvs73ddh4m0

# Export env vars
python render_complete_cli.py env export srv-d40tai15pdvs73ddh4m0 oregon.env

# Restart
python render_complete_cli.py services restart srv-d40tai15pdvs73ddh4m0
```

---

## Smart Deploy Tool

```powershell
# Analyze all capabilities
python smart_deploy.py --analyze

# Get deployment guide
python smart_deploy.py --deploy

# Check service status
python smart_deploy.py --status

# Delete old service
python smart_deploy.py --delete
```

---

## Help Commands

```powershell
# Main help
python render_complete_cli.py --help

# Services help
python render_complete_cli.py services --help

# Deploys help
python render_complete_cli.py deploys --help

# Environment vars help
python render_complete_cli.py env --help
```

---

## Migration Workflow (Oregon → Singapore)

```powershell
# 1. Export current env vars
python render_complete_cli.py env export srv-d40tai15pdvs73ddh4m0 oregon.env

# 2. Validate blueprint
python render_complete_cli.py blueprint validate ..\render.yaml

# 3. Get deployment guide
python render_complete_cli.py quick singapore

# 4. After new service created, import env vars
python render_complete_cli.py env import srv-new-singapore oregon.env

# 5. Verify new service
python render_complete_cli.py health check srv-new-singapore

# 6. Delete old service
python render_complete_cli.py services delete srv-d40tai15pdvs73ddh4m0
```

---

## Troubleshooting

**API Key Issues:**
```powershell
echo $env:RENDER_API_KEY
# Should show: rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu
```

**Get Service ID:**
```powershell
python render_complete_cli.py services list
# Look for "ID: srv-xxxxx"
```

**Logs Not Working:**
```
Use Dashboard: https://dashboard.render.com/web/srv-xxxxx
Or Render CLI: render logs tail srv-xxxxx
```

---

## Quick Status Check

```powershell
# One command to see everything
python render_complete_cli.py status overview

# Output shows:
# - Total services (16)
# - Active (12) vs Suspended (4)
# - Services by region (Oregon: 3, Singapore: 13)
```

---

## Resources

- **Full Documentation:** `README_RENDER_CLI.md`
- **Build Summary:** `RENDER_CLI_COMPLETE.md`
- **Render Dashboard:** https://dashboard.render.com/
- **API Docs:** https://api-docs.render.com/

---

**Quick Access:**
```powershell
# Add to PowerShell profile for fast access
function render-status { python c:\Users\gpoli\GIT\AI_agents\Render_backend\render_complete_cli.py status overview }
function render-list { python c:\Users\gpoli\GIT\AI_agents\Render_backend\render_complete_cli.py services list }
function render-quick { python c:\Users\gpoli\GIT\AI_agents\Render_backend\render_complete_cli.py quick status }
```

---

**Version:** 1.0.0  
**Last Updated:** November 8, 2025  
**Status:** Production Ready ✅
