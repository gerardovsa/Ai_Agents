# 🚀 Render Quick Start - Tim's Cheat Sheet

**5-Minute Setup Guide**

---

## Step 1: Get API Key (2 min)

1. Go to: https://dashboard.render.com/
2. Click profile icon → **Account Settings**
3. Scroll to **API Keys** → Click **Create API Key**
4. Name it: `AI_Agents_Integration`
5. **Copy the key immediately!** (You won't see it again)

```
Your key looks like: rnd_aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890
```

---

## Step 2: Install CLI (2 min)

**Copy/paste this into PowerShell:**

```powershell
# Download and install
New-Item -Path "C:\Tools\render" -ItemType Directory -Force
Invoke-WebRequest -Uri "https://github.com/render-oss/cli/releases/latest/download/cli_windows_amd64.zip" -OutFile "C:\Tools\render-cli.zip"
Expand-Archive -Path "C:\Tools\render-cli.zip" -DestinationPath "C:\Tools\render" -Force

# Add to PATH
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$newPath = "$currentPath;C:\Tools\render"
[Environment]::SetEnvironmentVariable("PATH", $newPath, "User")

# Restart PowerShell after this!
```

---

## Step 3: Login (1 min)

**After restarting PowerShell:**

```powershell
render login
```

Browser opens → Click **Authorize** → Done!

**Test it:**
```powershell
render services
```

You should see:
```
srv-d48abiripnbc73dce5m0  MustCare ValorAISynergySuite  active
dpg-d47gs124d50c7385p51g  PostgreSQL                    active
```

---

## Step 4: Add to AI Agents (1 min)

**Edit file:** `C:\Users\gpoli\GIT\AI_agents\.env.master`

**Add this line:**
```bash
RENDER_API_KEY=rnd_YOUR_API_KEY_HERE
```

**Restart Flask:**
```powershell
cd C:\Users\gpoli\GIT\AI_agents
BISTART
```

---

## Step 5: Test Everything (1 min)

### Test UI Module
```
1. Open: http://localhost:5001/UI/business-ai-platform-v2.html
2. Look for purple cloud icon ☁️ in sidebar
3. Click it → See services grid
```

### Test Chat Commands
```powershell
CHAT "List my Render services"
CHAT "Show me MustCare logs"
CHAT "Deploy srv-d48abiripnbc73dce5m0"
```

---

## 📝 Essential Commands

### CLI Commands
```powershell
render services                           # List all services
render logs srv-d48abiripnbc73dce5m0     # View logs
render deploy srv-d48abiripnbc73dce5m0   # Deploy service
render restart srv-d48abiripnbc73dce5m0  # Restart service
```

### Chat Commands
```
"List my Render services"
"Show me logs for MustCare"
"Deploy MustCare service"
"What's the status of srv-d48abiripnbc73dce5m0?"
```

### API Test
```powershell
Invoke-RestMethod -Uri "http://localhost:5001/api/render/services"
```

---

## 🆘 Quick Fixes

### "Command not found"
```powershell
# Restart PowerShell
# Then test:
render --version
```

### "Authentication failed"
```powershell
render login
# Or:
$env:RENDER_API_KEY = "rnd_YOUR_KEY"
```

### "Module not showing"
```
1. Check Flask logs for: "✅ Render routes loaded"
2. Hard refresh browser: Ctrl + Shift + R
3. Check console (F12) for JavaScript errors
```

---

## 🎯 Your Services

**MustCare Service:**
- ID: `srv-d48abiripnbc73dce5m0`
- URL: https://mustcare-valoraisynergysuite.onrender.com

**PostgreSQL Database:**
- ID: `dpg-d47gs124d50c7385p51g-a`

---

## ✅ Done!

You now have:
- ✅ Render CLI working
- ✅ API key configured
- ✅ UI module with cloud icon ☁️
- ✅ AI chat commands ready

**Full docs:** See `RENDER_CREDENTIALS_SETUP_GUIDE.md`
