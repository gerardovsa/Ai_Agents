# 🎯 UI Connection - Quick Reference Card

**Date**: October 23, 2025  
**Status**: ✅ CONNECTED & READY TO TEST  

---

## ⚡ Quick Start (30 seconds)

```powershell
# 1. Start NEW Flask
RESTARTNEW

# 2. Open browser
http://localhost:5001/stock-management

# 3. Done! ✅
```

---

## 🌐 All UI URLs

```
Stock Management:   http://localhost:5001/stock-management
Single Agent:       http://localhost:5001/single-agent-viewer
Data Agent Chat:    http://localhost:5001/data-agent-chat
Triple Agent:       http://localhost:5001/triple-agent
Home (default):     http://localhost:5001/
```

---

## 🧪 Test Connection

```powershell
cd c:\Users\gpoli\GIT\In_House_SQL\G_Folder\AI_infrastructure
.\test_ui_connection.ps1
```

**Expected**: ✅ 7-9 tests pass (HTML UIs load, Stock API accessible)

---

## ✅ What Works

- HTML UIs load from NEW Flask ✅
- Stock AI Chat (basic) ✅
- File uploads (PDFs, images) ✅
- SSE streaming ✅
- Session management ✅

---

## ⚠️ What's Missing (Expected)

- Stock Master tab (needs `/master-unified`)
- Invoice processing (needs `/process-invoice`)
- Thread management (needs `/list-threads`)
- AI analytics (needs `/ai-extracted-analytics`)

**Note**: This is Phase 1. Phase 2 adds missing endpoints.

---

## 📚 Documentation

| File | Description |
|------|-------------|
| `UI_CONNECTION_WHAT_CHANGED.md` | What was done, before/after |
| `UI_CONNECTION_COMPLETE_SUMMARY.md` | Complete technical summary |
| `UI_CONNECTION_PLAN.md` | Phase 2 implementation plan |
| `test_ui_connection.ps1` | Automated test script |
| `QUICK_START_UI_TEST.ps1` | Quick start instructions |

---

## 🔧 Commands

### Start Servers:
```powershell
RESTARTNEW               # NEW Flask (port 5001)
.\restart_servers.ps1    # OLD Flask (port 5000)
```

### Test:
```powershell
.\test_ui_connection.ps1          # Full test
Invoke-WebRequest -Uri http://localhost:5001/health  # Quick check
```

### Open UIs:
```powershell
Start-Process http://localhost:5001/stock-management
Start-Process http://localhost:5001/single-agent-viewer
Start-Process http://localhost:5001/triple-agent
```

---

## 🎯 Next Steps

**Phase 1**: ✅ COMPLETE (UIs connected)  
**Phase 2**: ⏳ Add missing endpoints (30-60 min)  
**Phase 3**: ⏳ Test full functionality (15 min)  
**Phase 4**: ⏳ Compare OLD vs NEW (10 min)  

See `UI_CONNECTION_PLAN.md` for Phase 2 details.

---

## ⚡ One-Liner Test

```powershell
RESTARTNEW ; Start-Sleep 15 ; Start-Process http://localhost:5001/stock-management
```

(Starts NEW Flask, waits 15s, opens Stock Management)

---

## 🚨 Troubleshooting

**Problem**: UIs don't load  
**Fix**: Check NEW Flask is running: `RESTARTNEW`

**Problem**: 404 errors in UI  
**Fix**: Expected! Some endpoints not implemented yet (Phase 2)

**Problem**: Port 5001 already in use  
**Fix**: Kill process: `Get-Process -Id (Get-NetTCPConnection -LocalPort 5001).OwningProcess | Stop-Process`

---

**Status**: ✅ UIs connected, basic chat works, ready for Phase 2 endpoint implementation
