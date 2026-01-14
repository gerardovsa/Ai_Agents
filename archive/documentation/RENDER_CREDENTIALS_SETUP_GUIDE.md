# 🔐 Render Authentication & Credentials Setup Guide

**Created:** November 10, 2025  
**For:** Tim - Complete Render CLI & API Setup  
**Time Required:** 10-15 minutes

---

## 📋 Overview

This guide will help you set up **complete access** to Render.com services for:
1. **Render CLI** - Command-line management
2. **Render API** - Programmatic access
3. **AI Agent Integration** - AI-powered deployment management

---

## 🚀 Step 1: Get Your Render API Key (5 minutes)

### What You Need:
- Access to Render.com dashboard
- Account owner permissions

### Instructions:

**1.1 Log into Render Dashboard**
```
https://dashboard.render.com/
```

**1.2 Navigate to Account Settings**
- Click your profile icon (top right)
- Select **"Account Settings"**

**1.3 Generate API Key**
- Scroll to **"API Keys"** section
- Click **"Create API Key"**
- Give it a name: `AI_Agents_Integration`
- Copy the key immediately (shown only once!)

**1.4 Save Your API Key**

Your API key will look like:
```
rnd_aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890
```

**⚠️ IMPORTANT:** Save this key immediately - you won't see it again!

---

## 🔧 Step 2: Install Render CLI (3 minutes)

### Windows Installation (PowerShell)

**2.1 Download CLI**
```powershell
# Create tools directory
New-Item -Path "C:\Tools\render" -ItemType Directory -Force

# Download latest CLI
Invoke-WebRequest -Uri "https://github.com/render-oss/cli/releases/latest/download/cli_windows_amd64.zip" -OutFile "C:\Tools\render-cli.zip"

# Extract
Expand-Archive -Path "C:\Tools\render-cli.zip" -DestinationPath "C:\Tools\render" -Force

# Verify installation
C:\Tools\render\render.exe --version
```

**Expected output:**
```
render version 1.x.x
```

**2.2 Add to PATH (Permanent)**
```powershell
# Add Render CLI to system PATH
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$newPath = "$currentPath;C:\Tools\render"
[Environment]::SetEnvironmentVariable("PATH", $newPath, "User")

# Restart PowerShell for PATH to take effect
```

**2.3 Verify Installation**

Close and reopen PowerShell, then:
```powershell
render --version
```

Should show version without errors.

---

## 🔑 Step 3: Authenticate Render CLI (2 minutes)

### Option A: Interactive Login (Recommended)

**3.1 Start Login Process**
```powershell
render login
```

**3.2 Follow Browser Prompts**
- Browser opens automatically
- Click **"Authorize"**
- Return to PowerShell

**3.3 Verify Authentication**
```powershell
render services
```

**Expected output:**
```
ID                        Name                          Type         Status
srv-d48abiripnbc73dce5m0  MustCare ValorAISynergySuite  web service  active
dpg-d47gs124d50c7385p51g  PostgreSQL                    database     active
```

### Option B: API Key Login (Alternative)

**3.1 Set Environment Variable**
```powershell
# Temporary (current session only)
$env:RENDER_API_KEY = "rnd_YOUR_API_KEY_HERE"

# Permanent (all sessions)
[Environment]::SetEnvironmentVariable("RENDER_API_KEY", "rnd_YOUR_API_KEY_HERE", "User")
```

**3.2 Verify Authentication**
```powershell
render services
```

---

## 🤖 Step 4: Configure AI Agent Tools (3 minutes)

### 4.1 Add API Key to Environment File

**Edit:** `C:\Users\gpoli\GIT\AI_agents\.env.master`

**Add this line:**
```bash
# Render Cloud Management
RENDER_API_KEY=rnd_YOUR_API_KEY_HERE
```

### 4.2 Verify Tools Are Loaded

**Restart Flask:**
```powershell
cd C:\Users\gpoli\GIT\AI_agents
BISTART
```

**Check Flask logs for:**
```
INFO:tools.registry_v3:   tools.implementations.render: 13 functions
✅ Render routes loaded successfully
```

### 4.3 Test AI Agent Integration

**Open chat and try:**
```
CHAT "List my Render services"
```

**Expected response:**
```
I found 2 Render services:

1. MustCare ValorAISynergySuite (srv-d48abiripnbc73dce5m0)
   - Type: Web Service
   - Status: Active
   - Region: Oregon (US West)
   - URL: https://mustcare-valoraisynergysuite.onrender.com

2. PostgreSQL Database (dpg-d47gs124d50c7385p51g-a)
   - Type: Database
   - Status: Active
```

---

## 📝 Step 5: Test All Render Integrations

### 5.1 Test CLI Commands

**List Services:**
```powershell
render services --output json
```

**View Logs:**
```powershell
render logs srv-d48abiripnbc73dce5m0 --tail 50
```

**List Deployments:**
```powershell
render deploys srv-d48abiripnbc73dce5m0
```

**Deploy Service:**
```powershell
render deploy srv-d48abiripnbc73dce5m0 --wait
```

### 5.2 Test API Endpoints

**Open PowerShell:**
```powershell
# Test services endpoint
Invoke-RestMethod -Uri "http://localhost:5001/api/render/services" -Method GET

# Test logs endpoint
Invoke-RestMethod -Uri "http://localhost:5001/api/render/logs?service_id=srv-d48abiripnbc73dce5m0&tail=10" -Method GET

# Test deploys endpoint
Invoke-RestMethod -Uri "http://localhost:5001/api/render/deploys?service_id=srv-d48abiripnbc73dce5m0&limit=5" -Method GET
```

### 5.3 Test UI Module

**Open Browser:**
```
http://localhost:5001/UI/business-ai-platform-v2.html
```

**Look for:**
- Purple cloud icon ☁️ in sidebar
- Click it
- Services tab shows MustCare service
- Logs tab shows real-time logs
- Deploy button works

---

## 🔐 Security Best Practices

### Protect Your API Key

**✅ DO:**
- Store API key in `.env.master` file
- Add `.env.master` to `.gitignore`
- Use environment variables in code
- Rotate keys every 90 days
- Use separate keys for dev/prod

**❌ DON'T:**
- Commit API keys to Git
- Share keys in chat/email
- Use same key across teams
- Store keys in plain text files
- Hardcode keys in source code

### Key Storage Locations

**Environment File:**
```
C:\Users\gpoli\GIT\AI_agents\.env.master
```

**System Environment (Permanent):**
```powershell
[Environment]::GetEnvironmentVariable("RENDER_API_KEY", "User")
```

**Session Environment (Temporary):**
```powershell
$env:RENDER_API_KEY
```

---

## 🎯 Quick Reference Commands

### Essential CLI Commands

```powershell
# Login
render login

# List all services
render services

# Get service details
render services srv-d48abiripnbc73dce5m0

# View logs (last 100 lines)
render logs srv-d48abiripnbc73dce5m0 --tail 100

# Stream logs in real-time
render logs srv-d48abiripnbc73dce5m0 --follow

# List deployments
render deploys srv-d48abiripnbc73dce5m0

# Deploy service
render deploy srv-d48abiripnbc73dce5m0

# Restart service
render restart srv-d48abiripnbc73dce5m0

# Get service info as JSON
render services srv-d48abiripnbc73dce5m0 --output json

# View environment variables
render env list srv-d48abiripnbc73dce5m0

# Update environment variable
render env set KEY=VALUE srv-d48abiripnbc73dce5m0
```

### Essential AI Chat Commands

```powershell
# List services
CHAT "List my Render services"

# View logs
CHAT "Show me logs for MustCare service"

# Deploy service
CHAT "Deploy srv-d48abiripnbc73dce5m0"

# Check service status
CHAT "What's the status of MustCare ValorAISynergySuite?"

# Restart service
CHAT "Restart the MustCare service"

# View deployment history
CHAT "Show me recent deployments for MustCare"
```

---

## 🆘 Troubleshooting

### Issue: "render: command not found"

**Solution:**
```powershell
# Check if Render CLI is installed
Test-Path "C:\Tools\render\render.exe"

# If false, reinstall CLI (Step 2)
# If true, add to PATH (Step 2.2)

# Verify PATH
$env:PATH -split ";" | Select-String "render"
```

### Issue: "Authentication failed"

**Solution:**
```powershell
# Re-login
render login

# Or set API key
$env:RENDER_API_KEY = "rnd_YOUR_API_KEY_HERE"

# Verify authentication
render services
```

### Issue: "API returns 401 Unauthorized"

**Solution:**
```powershell
# Check API key is set
echo $env:RENDER_API_KEY

# If empty, set it
$env:RENDER_API_KEY = "rnd_YOUR_API_KEY_HERE"

# Restart Flask
cd C:\Users\gpoli\GIT\AI_agents
BISTART
```

### Issue: "Module not appearing in UI"

**Solution:**
```powershell
# Check manifest entry exists
Get-Content "C:\Users\gpoli\GIT\AI_agents\UI\external\modules\manifest.json" | Select-String "render-management"

# Check Flask logs
# Should see: "✅ Render routes loaded successfully"

# Hard refresh browser
# Press: Ctrl + Shift + R
```

### Issue: "Services list is empty"

**Solution:**
```powershell
# Verify CLI authentication
render services

# If shows services, check API
Invoke-RestMethod -Uri "http://localhost:5001/api/render/services" -Method GET

# If API fails, check Flask is running
Invoke-RestMethod -Uri "http://localhost:5001/health" -Method GET
```

---

## 📊 Your Render Services

### MustCare ValorAISynergySuite

**Service ID:** `srv-d48abiripnbc73dce5m0`  
**Type:** Web Service  
**Region:** Oregon (US West)  
**URL:** https://mustcare-valoraisynergysuite.onrender.com  

**Environment Variables:**
```bash
NODE_ENV=production
PORT=3000
# Add others as needed
```

**Useful Commands:**
```powershell
# View logs
render logs srv-d48abiripnbc73dce5m0 --tail 100

# Deploy
render deploy srv-d48abiripnbc73dce5m0 --wait

# Restart
render restart srv-d48abiripnbc73dce5m0

# View env vars
render env list srv-d48abiripnbc73dce5m0
```

### PostgreSQL Database

**Database ID:** `dpg-d47gs124d50c7385p51g-a`  
**Type:** PostgreSQL  
**Version:** 16 (Latest)

**Connection String:**
```
Internal: postgresql://user:pass@dpg-d47gs124d50c7385p51g-a/dbname
External: postgresql://user:pass@dpg-d47gs124d50c7385p51g-a.oregon-postgres.render.com/dbname
```

**Useful Commands:**
```powershell
# Create backup
render postgres backup dpg-d47gs124d50c7385p51g-a

# List backups
render postgres backups dpg-d47gs124d50c7385p51g-a

# Restore from backup
render postgres restore dpg-d47gs124d50c7385p51g-a --backup-id <id>
```

---

## 🎓 Additional Resources

### Official Documentation

**Render CLI:**
- GitHub: https://github.com/render-oss/cli
- Docs: https://render.com/docs/cli

**Render API:**
- API Reference: https://api-docs.render.com/reference
- Authentication: https://render.com/docs/api#authentication

**Render Dashboard:**
- Dashboard: https://dashboard.render.com/
- Service Settings: https://dashboard.render.com/web/srv-d48abiripnbc73dce5m0

### Internal Documentation

**AI_agents Repository:**
- Setup Guide: `RENDER_READY_TO_USE.md`
- Integration Status: `RENDER_INTEGRATION_COMPLETE.md`
- Module Activation: `RENDER_MODULE_ACTIVATED.md`

**Module Files:**
- Location: `UI/external/modules/render-management/`
- Backend Routes: `AI_infrastructure/routes/render_routes.py`
- Tools: `tools/schemas/render_tools.json`
- Implementation: `tools/implementations/render.py`

---

## ✅ Setup Checklist

Print this checklist and check off each step:

### Installation
- [ ] Render CLI downloaded and installed
- [ ] Render CLI added to PATH
- [ ] CLI version verified (`render --version`)

### Authentication
- [ ] Render API key generated from dashboard
- [ ] API key saved securely
- [ ] CLI authenticated (`render login`)
- [ ] CLI authentication verified (`render services`)
- [ ] API key added to `.env.master`

### AI Agent Integration
- [ ] Flask restarted with new environment
- [ ] Render tools loaded (check Flask logs)
- [ ] Render routes registered (check Flask logs)
- [ ] UI module appears (cloud icon visible)
- [ ] Test chat command works

### Testing
- [ ] CLI commands work (`render services`)
- [ ] API endpoints respond (`/api/render/services`)
- [ ] UI module loads services
- [ ] Deploy button works
- [ ] Logs tab shows logs

### Documentation
- [ ] API key documented in password manager
- [ ] Service IDs recorded
- [ ] Common commands bookmarked
- [ ] Team members notified

---

## 🎉 You're All Set!

Once you've completed all steps above, you'll have:

✅ **Full CLI access** - Command-line control of all Render services  
✅ **API integration** - Programmatic access via Flask routes  
✅ **UI module** - Visual management with cloud icon  
✅ **AI agent integration** - Chat commands for deployments  
✅ **Real-time monitoring** - Logs, metrics, and deployment tracking

---

**Need Help?**

- Check Flask logs: Look for Render-related errors
- Test API: `Invoke-RestMethod -Uri "http://localhost:5001/api/render/services"`
- Verify CLI: `render services --output json`
- Check module: Open browser DevTools (F12) and look for JavaScript errors

**Questions?**

Contact the development team or refer to:
- `RENDER_READY_TO_USE.md` - Complete setup guide
- `RENDER_INTEGRATION_COMPLETE.md` - Technical details
- Render Docs: https://render.com/docs

---

**Created:** November 10, 2025  
**Last Updated:** November 10, 2025  
**Version:** 1.0.0  
**Status:** ✅ Complete and ready for use
