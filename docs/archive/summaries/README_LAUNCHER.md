# 🚀 Business AI Platform Launcher

Quick launch scripts to start the Business AI Platform from anywhere!

## 📋 Files Created

1. **BISTART.bat** - Windows Batch launcher (works from any directory)
2. **BISTART.ps1** - PowerShell launcher (more colorful output)
3. **BISTOP.ps1** - PowerShell script to stop all servers

## 🎯 Quick Start

### Method 1: Batch File (Simplest)
```cmd
cd C:\Users\gpoli\GIT\AI_agents
BISTART.bat
```

### Method 2: PowerShell (Recommended)
```powershell
cd C:\Users\gpoli\GIT\AI_agents
.\BISTART.ps1
```

### From Any Directory (After Setup)
```powershell
BISTART
```

## ⚙️ What It Does

When you run `BISTART`, it:

1. ✅ **Starts Flask Backend** (Port 5001)
   - Opens new terminal window
   - Runs: `python flask_app.py`
   - Location: `AI_agents\AI_infrastructure\`

2. ✅ **Starts UI Server** (Port 8080)
   - Opens new terminal window
   - Runs: `python -m http.server 8080`
   - Location: `AI_agents\UI\`

3. ✅ **Opens Browser**
   - Automatically opens: `http://localhost:8080/business-ai-platform-v2.html`

## 🛑 Stopping Servers

### Option 1: Manual
Press `Ctrl+C` in each terminal window

### Option 2: Automated (PowerShell)
```powershell
.\BISTOP.ps1
```

This kills all Flask and UI server processes automatically.

## 📍 URLs

After launching:

- **Flask Backend**: http://localhost:5001
- **UI Platform**: http://localhost:8080/business-ai-platform-v2.html
- **Health Check**: http://localhost:5001/health

## 🔧 Advanced Setup (Run from Anywhere)

To run `BISTART` from any directory:

### Windows PowerShell Profile
1. Edit your PowerShell profile:
   ```powershell
   notepad $PROFILE
   ```

2. Add this line:
   ```powershell
   Set-Alias BISTART "C:\Users\gpoli\GIT\AI_agents\BISTART.ps1"
   Set-Alias BISTOP "C:\Users\gpoli\GIT\AI_agents\BISTOP.ps1"
   ```

3. Reload profile:
   ```powershell
   . $PROFILE
   ```

4. Now you can run from anywhere:
   ```powershell
   cd C:\Any\Directory
   BISTART
   ```

### Add to System PATH (Batch File)
1. Right-click "This PC" → Properties → Advanced System Settings
2. Environment Variables → System Variables → Path → Edit
3. Add: `C:\Users\gpoli\GIT\AI_agents`
4. Click OK
5. Restart terminal
6. Now run from anywhere:
   ```cmd
   BISTART
   ```

## 🐛 Troubleshooting

### Flask won't start
- Check if Python is installed: `python --version`
- Check if Flask dependencies are installed: `pip list | Select-String flask`
- Manually test: `cd AI_infrastructure; python flask_app.py`

### UI server won't start
- Check if port 8080 is free: `netstat -ano | findstr :8080`
- Kill existing process: `taskkill /PID <PID> /F`

### Browser doesn't open
- Manually open: http://localhost:8080/business-ai-platform-v2.html
- Check UI server is running in terminal window

### "File not found" errors
- Verify paths in BISTART scripts match your directory structure
- Edit `FLASK_DIR` and `UI_DIR` variables if needed

## 📊 Platform Features

Once launched, you get access to:

- ✅ **281 AI Tools** across 19 platforms
- ✅ **Multi-Agent NATO Columns** (Alpha, Bravo, Charlie... Zulu)
- ✅ **Real-time AI Chat** with tool execution
- ✅ **Dashboard** with platform status
- ✅ **Independent Agent Sessions**
- ✅ **SSE Streaming** for real-time responses

## 🎨 Multi-Agent System

The platform includes NATO phonetic alphabet agents:
- **Alpha, Bravo, Charlie** (default 3 agents)
- Click "ADD AGENT" to add Delta, Echo, Foxtrot, etc.
- Maximum 26 agents (Zulu)
- Each agent has independent chat history
- Hamburger menus (⋮) for New Chat, Save Thread, Close

## 📝 Notes

- Flask backend runs on **Port 5001**
- UI server runs on **Port 8080**
- Both servers run in separate terminal windows
- Browser auto-opens to platform
- Press `Ctrl+C` in each terminal to stop servers
- Use `BISTOP.ps1` to kill all processes at once

## 🚀 Quick Commands Summary

```powershell
# Start platform
.\BISTART.ps1

# Stop platform
.\BISTOP.ps1

# Check Flask health
curl http://localhost:5001/health

# Check available tools
curl http://localhost:5001/api/agent/tools
```

---

**Created**: October 24, 2025  
**Version**: 1.0  
**Tested On**: Windows 11, PowerShell 5.1, Python 3.x
