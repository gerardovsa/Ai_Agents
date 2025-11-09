# Render Deployment Toolkit - Quick Guide

**Fast, encoding-safe monitoring and management for Render deployments**

---

## Features

✅ **Encoding-safe** - Works perfectly in Windows PowerShell/CMD  
✅ **Quick commands** - Fast access to common operations  
✅ **Live monitoring** - Watch deployments in real-time  
✅ **Health checks** - Test service endpoints  
✅ **Status overview** - See everything at a glance  

---

## Setup (One-Time)

```powershell
# Navigate to toolkit directory
cd C:\Users\gpoli\GIT\AI_agents\Render_backend

# Set API key (if not already in environment)
$env:RENDER_API_KEY="rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu"
```

---

## Common Commands

### Quick Status (Most Used)
```powershell
# See everything at once: service status, latest deploy, health
python render_toolkit.py quick
```

### Monitor Active Deployment
```powershell
# Watch current deployment until completion (checks every 30s)
python render_toolkit.py monitor

# Custom interval and max checks
python render_toolkit.py monitor --interval 20 --max-checks 30
```

### Service Information
```powershell
# Get detailed service info
python render_toolkit.py service
```

### Deployment History
```powershell
# Show last 3 deployments
python render_toolkit.py deploys

# Show last 10 deployments
python render_toolkit.py deploys --all
```

### Health Check
```powershell
# Test /health endpoint
python render_toolkit.py health
```

### Environment Variables
```powershell
# Count env vars (doesn't show values for security)
python render_toolkit.py env
```

### Full Status Report
```powershell
# Service info + recent deployments
python render_toolkit.py status

# Include more deployments
python render_toolkit.py status --all
```

---

## Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `quick` | Quick status overview | `python render_toolkit.py quick` |
| `monitor` | Watch deployment until done | `python render_toolkit.py monitor` |
| `watch` | Alias for monitor | `python render_toolkit.py watch` |
| `service` | Service details | `python render_toolkit.py service` |
| `deploys` | Deployment history | `python render_toolkit.py deploys --all` |
| `health` | Health check | `python render_toolkit.py health` |
| `env` | Environment variables | `python render_toolkit.py env` |
| `status` | Full status report | `python render_toolkit.py status` |

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--all` | Show all items (for deploys) | Show 3 |
| `--interval N` | Check every N seconds (monitor) | 30 |
| `--max-checks N` | Max checks (monitor) | 20 |
| `--service-id ID` | Use different service | Current service |

---

## Example Workflows

### After Pushing Code
```powershell
# 1. Check if deployment started
python render_toolkit.py quick

# 2. Monitor until completion
python render_toolkit.py monitor

# 3. Test health endpoint
python render_toolkit.py health
```

### Check Deployment Status
```powershell
# Quick check
python render_toolkit.py quick

# Detailed history
python render_toolkit.py deploys --all
```

### Continuous Monitoring
```powershell
# Monitor with faster checks (every 15 seconds)
python render_toolkit.py monitor --interval 15

# Monitor for longer (up to 40 checks = 20 minutes at 30s intervals)
python render_toolkit.py monitor --max-checks 40
```

---

## Output Examples

### Quick Status
```
==================================================================================================
  QUICK STATUS OVERVIEW
==================================================================================================

Service Status: [ACTIVE] not_suspended
Service URL:    https://ai-agents-backend-singapore.onrender.com

Latest Deploy:  [BUILD] build_in_progress
Deploy ID:      dep-d481tvemcj7s73809810
Created:        2025-11-09T05:15:32Z

Health Status:  [HEALTHY]

==================================================================================================
```

### Monitoring Output
```
==================================================================================================
  DEPLOYMENT MONITOR
==================================================================================================

Monitoring deployment: dep-d481tvemcj7s73809810
Initial status: build_in_progress
Checking every 30 seconds (max 20 checks)

[14:25:30] Check 1/20: [BUILD] build_in_progress - waiting 30s...
[14:26:00] Check 2/20: [BUILD] build_in_progress - waiting 30s...
[14:26:30] Check 3/20: [DEPLOY] deploying - waiting 30s...
[14:27:00] Check 4/20: [OK] live

Deployment completed with status: live

[SUCCESS] Deployment successful!
```

---

## Troubleshooting

**Command not found:**
```powershell
# Make sure you're in the right directory
cd C:\Users\gpoli\GIT\AI_agents\Render_backend
```

**API errors:**
```powershell
# Check API key is set
echo $env:RENDER_API_KEY

# Should show: rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu
```

**Encoding errors:**
```powershell
# Toolkit handles encoding automatically
# If you still see issues, set:
$env:PYTHONIOENCODING="utf-8"
python render_toolkit.py quick
```

**Service ID issues:**
```powershell
# Use different service
python render_toolkit.py quick --service-id srv-xxxxx
```

---

## PowerShell Aliases (Optional)

Add to your PowerShell profile for faster access:

```powershell
# Edit profile
notepad $PROFILE

# Add these functions:
function rdeploy { python C:\Users\gpoli\GIT\AI_agents\Render_backend\render_toolkit.py quick }
function rwatch { python C:\Users\gpoli\GIT\AI_agents\Render_backend\render_toolkit.py monitor }
function rhealth { python C:\Users\gpoli\GIT\AI_agents\Render_backend\render_toolkit.py health }
function rstatus { python C:\Users\gpoli\GIT\AI_agents\Render_backend\render_toolkit.py status }

# Then use:
rdeploy     # Quick status
rwatch      # Monitor deployment
rhealth     # Health check
rstatus     # Full status
```

---

## Service Information

**Current Service:**
- **Name:** ai-agents-backend-singapore
- **ID:** srv-d47nfr2li9vc738s0uc0
- **Region:** Singapore
- **URL:** https://ai-agents-backend-singapore.onrender.com
- **Dashboard:** https://dashboard.render.com/web/srv-d47nfr2li9vc738s0uc0

---

## Tips

1. **Use `quick` for fast checks** - Most commonly used command
2. **Use `monitor` after git push** - Watch deployment complete
3. **Check `health` if issues** - Verifies service is responding
4. **Use `deploys --all`** - See full deployment history
5. **Interrupt with Ctrl+C** - Safe to cancel monitoring anytime

---

**Version:** 1.0.0  
**Last Updated:** November 9, 2025  
**Status:** Production Ready ✅
