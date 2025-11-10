# 🔧 Dual Flask Launch Fix - October 23, 2025

**Problem**: RESTARTNEW was launching **TWO Flask apps** simultaneously  
**Status**: ✅ FIXED  

---

## 🐛 Root Cause

**Streamlit auto-launch feature** in `web_ui.py` was automatically starting the OLD Flask app (`flask_triple_agent_app.py` on port 5000) whenever Streamlit started, even though RESTARTNEW was already launching the NEW Flask app (`flask_app.py` on port 5001).

### What Was Happening:
```
User types: RESTARTNEW
↓
1. restart_servers_new.ps1 launches NEW Flask (port 5001) ✅
2. restart_servers_new.ps1 launches Streamlit (port 8501) ✅
3. Streamlit starts → auto_launch_flask() runs ❌
4. auto_launch_flask() launches OLD Flask (port 5000) ❌

Result: TWO Flask apps running!
```

---

## ✅ Fixes Applied

### Fix 1: Disabled Streamlit Auto-Launch
**File**: `tools/web_ui.py`

**Changed**:
```python
# Before (Line 126):
def auto_launch_flask():

# After (Line 126):
def auto_launch_flask_DISABLED():  # ✅ Renamed to disable

# Before (Line 193):
    auto_launch_flask()

# After (Line 193):
    # auto_launch_flask()  # DISABLED - manually launch Flask with RESTARTNEW
    print("INFO: Flask auto-launch disabled - use RESTARTNEW command to launch NEW Flask on port 5001")
```

**Result**: Streamlit no longer auto-starts OLD Flask.

### Fix 2: Updated RESTARTNEW Banner
**File**: PowerShell Profile (`$PROFILE`)

**Changed banner to show correct port**:
```powershell
# Before:
Flask:     http://127.0.0.1:5000

# After:
Flask:     http://localhost:5001 (NEW Flask - Testing)
```

---

## 🧪 How to Test

### Test 1: Clean Start
```powershell
# 1. Close all Flask/Streamlit windows
Get-Process python | Where-Object { $_.CommandLine -like "*flask*" } | Stop-Process -Force
Get-Process python | Where-Object { $_.CommandLine -like "*streamlit*" } | Stop-Process -Force

# 2. Run RESTARTNEW
RESTARTNEW

# 3. Check what's running
netstat -ano | findstr ":5000"  # Should be EMPTY ✅
netstat -ano | findstr ":5001"  # Should show NEW Flask ✅
netstat -ano | findstr ":8501"  # Should show Streamlit ✅
```

**Expected Result**:
- ✅ Only ONE Flask window opens (NEW Flask on port 5001)
- ✅ Streamlit opens in current terminal
- ✅ No second Flask window for OLD Flask
- ✅ Console shows: "INFO: Flask auto-launch disabled..."

### Test 2: Check Ports
```powershell
# After RESTARTNEW, verify ports:
Invoke-WebRequest -Uri http://localhost:5001/health  # NEW Flask ✅
Invoke-WebRequest -Uri http://localhost:5000/health  # Should FAIL (not running) ✅
Invoke-WebRequest -Uri http://localhost:8501  # Streamlit ✅
```

---

## 🎯 Current Architecture

### Port Assignments:
```
Port 5000: OLD Flask (flask_triple_agent_app.py)
           - Production app
           - Launch manually: cd G_Folder ; .\restart_servers.ps1
           - Status: Available but not auto-started

Port 5001: NEW Flask (AI_infrastructure/flask_app.py)
           - Testing/development app
           - Launch with: RESTARTNEW (global command)
           - Status: Auto-started via RESTARTNEW ✅

Port 8501: Streamlit (web_ui.py)
           - Shared UI for both Flask apps
           - Launch with: RESTARTNEW (global command)
           - Auto-launch OLD Flask: DISABLED ✅
```

### Commands:
```powershell
# Launch NEW Flask (port 5001) + Streamlit
RESTARTNEW  # Recommended for testing NEW architecture

# Launch OLD Flask (port 5000) + Streamlit (manual)
cd c:\Users\gpoli\GIT\In_House_SQL\G_Folder
.\restart_servers.ps1

# Run both side-by-side (for comparison)
# Terminal 1:
cd c:\Users\gpoli\GIT\In_House_SQL\G_Folder
.\restart_servers.ps1  # OLD Flask on 5000

# Terminal 2:
RESTARTNEW  # NEW Flask on 5001 + Streamlit on 8501
```

---

## 📝 What Changed

### Files Modified:
1. **`tools/web_ui.py`** (Lines 126, 193)
   - Renamed `auto_launch_flask()` to `auto_launch_flask_DISABLED()`
   - Commented out function call
   - Added info message about manual launch

2. **PowerShell Profile** (`$PROFILE`)
   - Updated RESTARTNEW banner to show port 5001

### Files NOT Changed:
- `restart_servers_new.ps1` - Still correct (launches NEW Flask on 5001)
- `restart_servers.ps1` - Unchanged (launches OLD Flask on 5000)
- `flask_app.py` - Unchanged (runs on port 5001)
- `flask_triple_agent_app.py` - Unchanged (runs on port 5000)

---

## 💡 Why This Design

### Problem with Auto-Launch:
The Streamlit auto-launch feature was designed for the OLD single-Flask architecture. With the NEW dual-Flask architecture (OLD for production, NEW for testing), auto-launch creates conflicts.

### Solution:
**Manual control** - User explicitly chooses which Flask to run:
- `RESTARTNEW` → NEW Flask (testing)
- `.\restart_servers.ps1` → OLD Flask (production)
- Both can run together for comparison

### Benefits:
- ✅ No port conflicts
- ✅ Clear which Flask is running
- ✅ Safe testing (NEW Flask isolated on port 5001)
- ✅ Production unaffected (OLD Flask available on 5000 when needed)

---

## 🔄 To Re-Enable Auto-Launch Later

If you want to restore auto-launch (e.g., after NEW Flask becomes production):

**Option 1: Re-enable OLD Flask auto-launch**
```python
# web_ui.py line 126:
def auto_launch_flask_DISABLED():  # Remove _DISABLED

# web_ui.py line 193:
auto_launch_flask()  # Uncomment
```

**Option 2: Change to auto-launch NEW Flask**
```python
# web_ui.py line 151:
flask_script = os.path.join(flask_dir, 'flask_app.py')  # NEW Flask

# web_ui.py line 149:
flask_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'AI_infrastructure'))
```

---

## 🎉 Summary

**Before**:
```
RESTARTNEW
├── Launches NEW Flask (port 5001) ✅
├── Launches Streamlit (port 8501) ✅
└── Streamlit auto-launches OLD Flask (port 5000) ❌
    Result: TWO Flask apps running! ❌
```

**After**:
```
RESTARTNEW
├── Launches NEW Flask (port 5001) ✅
├── Launches Streamlit (port 8501) ✅
└── Streamlit auto-launch disabled ✅
    Result: ONLY NEW Flask running! ✅
```

**Status**: ✅ FIXED - RESTARTNEW now launches only ONE Flask app (NEW on port 5001)

---

**Next Steps**: Test UI connection with `RESTARTNEW` → Open http://localhost:5001/stock-management
