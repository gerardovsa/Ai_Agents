# 🚀 Synergy Dashboard - Quick Reference Card

## ⚡ Quick Start (30 seconds)

```bash
cd C:\Users\gpoli\GIT\AI_agents
SYNERGY_START.bat
```

**Server URL:** http://localhost:4000  
**WebSocket:** ws://localhost:4000/ws/synergy  
**Dashboard:** Open `UI/business-ai-platform-v2.html` in browser

---

## 📡 API Endpoints (Copy & Paste)

### List All Sessions
```bash
curl http://localhost:4000/api/sessions/list
```

### Create Session
```bash
curl -X POST http://localhost:4000/api/sessions/create -H "Content-Type: application/json" -d "{\"title\":\"New Task\",\"priority\":\"high\"}"
```

### Update Session (with Google sync)
```bash
curl -X PATCH http://localhost:4000/api/sessions/SESSION_ID -H "Content-Type: application/json" -d "{\"updates\":{\"title\":\"Updated\"},\"sync\":{\"google_tasks\":true,\"google_calendar\":true}}"
```

### Move Column (drag & drop)
```bash
curl -X PATCH http://localhost:4000/api/sessions/SESSION_ID/column -H "Content-Type: application/json" -d "{\"column\":\"done\"}"
```

### Delete Session
```bash
curl -X DELETE http://localhost:4000/api/sessions/SESSION_ID
```

---

## 🔌 WebSocket (Browser Console)

```javascript
// Connect
const socket = io('http://localhost:4000/ws/synergy');

// Subscribe to updates
socket.on('connect', () => {
    socket.emit('subscribe', { channel: 'synergy_board' });
});

// Listen for card edits
socket.on('card_edited', (data) => {
    console.log('Card edited:', data);
});

// Listen for card moves
socket.on('card_moved', (data) => {
    console.log('Card moved:', data);
});
```

---

## 🔧 Troubleshooting

### Server won't start
```bash
# Kill existing process
taskkill /F /IM python.exe

# Start fresh
SYNERGY_START.bat
```

### Google sync not working
```bash
# Check environment variable
echo %GOOGLE_APPLICATION_CREDENTIALS%

# Should show: C:\Users\gpoli\GIT\AI_agents\vsa-anythingllm-project-ab7c8caf8c47.json
```

### Database reset
```bash
# Stop server (Ctrl+C)
# Delete database
del data\synergy_sessions.db

# Restart server (will create fresh database with sample data)
SYNERGY_START.bat
```

---

## 📊 Health Checks

```bash
# Server health
curl http://localhost:4000/health

# API info
curl http://localhost:4000/api/info

# Session count
curl http://localhost:4000/api/sessions/list | python -c "import sys, json; print(len(json.load(sys.stdin)))"
```

---

## 🎯 Common Tasks

### Test Google Tasks Sync
```bash
# Create session with sync
curl -X POST http://localhost:4000/api/sessions/create -H "Content-Type: application/json" -d "{\"title\":\"Test Task\",\"description\":\"Testing Google sync\",\"due_date\":\"2025-11-15\"}"

# Copy session_id from response, then sync
curl -X PATCH http://localhost:4000/api/sessions/SESSION_ID -H "Content-Type: application/json" -d "{\"sync\":{\"google_tasks\":true}}"

# Check https://tasks.google.com/
```

### Test Real-time Collaboration
```bash
# Terminal 1: Watch server logs
python synergy_backend.py

# Terminal 2: Edit a session
curl -X PATCH http://localhost:4000/api/sessions/SESSION_ID -H "Content-Type: application/json" -d "{\"updates\":{\"title\":\"Live Update\"}}"

# Terminal 1: See broadcast log
# 📡 Broadcasting card_edited: {...}
```

---

## 📂 File Locations

```
Backend:         C:\Users\gpoli\GIT\AI_agents\synergy_backend.py
Frontend:        C:\Users\gpoli\GIT\AI_agents\UI\business-ai-platform-v2.html
Database:        C:\Users\gpoli\GIT\AI_agents\data\synergy_sessions.db
Service Account: C:\Users\gpoli\GIT\AI_agents\vsa-anythingllm-project-ab7c8caf8c47.json
Launcher:        C:\Users\gpoli\GIT\AI_agents\SYNERGY_START.bat
```

---

## 🔑 Important URLs

- **Dashboard:** Open `UI/business-ai-platform-v2.html` in browser
- **API Server:** http://localhost:4000
- **Health Check:** http://localhost:4000/health
- **API Info:** http://localhost:4000/api/info
- **Google Tasks:** https://tasks.google.com/
- **Google Calendar:** https://calendar.google.com/

---

## 💡 Pro Tips

1. **Always use `SYNERGY_START.bat`** - Sets up environment correctly
2. **Check server logs** - Shows all operations and errors
3. **Keep database file** - Easy backup, just copy `data/synergy_sessions.db`
4. **Test with curl first** - Before testing in browser
5. **Use two browser windows** - To see real-time updates

---

## 🆘 Emergency Commands

```bash
# Stop everything
taskkill /F /IM python.exe

# Clean slate
del data\synergy_sessions.db
SYNERGY_START.bat

# Check what's using port 4000
netstat -ano | findstr :4000
```

---

**Status:** ✅ Ready to Use  
**Version:** 1.0.0  
**Last Updated:** October 28, 2025
