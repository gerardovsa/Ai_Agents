# 🔧 RESTARTNEW Script Fix - Port 5001 + Virtual Environment

**Date**: October 23, 2025  
**Issue**: RESTARTNEW was launching NEW Flask on wrong port (5000 instead of 5001) and Streamlit couldn't find virtual environment  
**Status**: ✅ FIXED  

---

## 🐛 Problems Identified

### Problem 1: Port Conflict
```
STEP 4: Starting NEW Flask on port 5000 (AI_infrastructure)...
Flask (NEW):  http://localhost:5000  ← WRONG! Should be 5001
```

**Impact**: NEW Flask tried to use same port as OLD Flask (5000), causing conflicts.

### Problem 2: Streamlit Not Found
```
& : The term 'streamlit' is not recognized...
```

**Root Cause**: Virtual environment wasn't activated before running Streamlit in STEP 5.

---

## ✅ Fixes Applied

### Fix 1: Changed NEW Flask Port to 5001
**File**: `restart_servers_new.ps1`

**Changed**:
```powershell
# Before:
STEP 4: Starting NEW Flask on port 5000...
Port: 5000
Flask (NEW):  http://localhost:5000

# After:
STEP 4: Starting NEW Flask on port 5001...
Port: 5001 (NEW - Testing)
Flask (NEW):  http://localhost:5001
```

**Lines modified**: 128, 138, 164

### Fix 2: Activate Virtual Environment Before Streamlit
**File**: `restart_servers_new.ps1`

**Added**:
```powershell
# STEP 5: Start Streamlit
Write-Host "STEP 5: Starting Streamlit..." -ForegroundColor Yellow

# ✅ NEW: Activate virtual environment first
& c:/Users/gpoli/GIT/In_House_SQL/.venv/Scripts/Activate.ps1

# Clear Streamlit cache
& streamlit cache clear 2>$null

# Start Streamlit
& streamlit run web_ui.py
```

**Line added**: 158 (virtual environment activation)

### Fix 3: Updated Flask Process Detection
**File**: `restart_servers_new.ps1`

**Changed**:
```powershell
# Before:
$flaskProcesses = ... -like "*5000*"

# After:
$flaskProcesses = ... -like "*5001*"
```

**Line modified**: 22

---

## 🧪 How to Test

### Test 1: Run RESTARTNEW
```powershell
RESTARTNEW
```

**Expected Output**:
```
STEP 4: Starting NEW Flask on port 5001 (AI_infrastructure)...
   [OK] NEW Flask starting in new window...

STEP 5: Starting Streamlit...
   Clearing Streamlit cache...

====================================================================
  SERVERS STARTING
====================================================================
  Flask (NEW):  http://localhost:5001  ✅ Port 5001!
  Streamlit:    http://localhost:8501  ✅ Streamlit runs!
====================================================================

  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

### Test 2: Verify NEW Flask Window Opens
- New PowerShell window should open
- Shows: "Port: 5001 (NEW - Testing)"
- Flask should start without errors

### Test 3: Verify Streamlit Starts
- Current terminal stays open (doesn't close)
- Streamlit UI accessible at http://localhost:8501
- No "streamlit is not recognized" error

### Test 4: Check Ports
```powershell
netstat -ano | findstr ":5001"  # Should show NEW Flask
netstat -ano | findstr ":8501"  # Should show Streamlit
```

---

## 🎯 Summary

### What Changed:
- ✅ NEW Flask now uses port **5001** (not 5000)
- ✅ Virtual environment activated before Streamlit
- ✅ Port detection updated (5001 instead of 5000)

### What This Means:
- ✅ **No port conflicts** - OLD Flask (5000) and NEW Flask (5001) can run side-by-side
- ✅ **Streamlit works** - Finds command after venv activation
- ✅ **RESTARTNEW command works** - Launches both servers correctly

### Port Architecture:
```
OLD Flask (Production):  http://localhost:5000  (restart_servers.ps1)
NEW Flask (Testing):     http://localhost:5001  (restart_servers_new.ps1 / RESTARTNEW)
Streamlit (Both):        http://localhost:8501  (shared UI)
```

---

## 🚀 Ready to Use

**Command**:
```powershell
RESTARTNEW
```

**What Happens**:
1. Stops any running Flask on port 5001
2. Stops any running Streamlit
3. Clears Python cache
4. Starts NEW Flask on port 5001 (in new window)
5. Starts Streamlit on port 8501 (current window)

**Access**:
- NEW Flask: http://localhost:5001
- Streamlit: http://localhost:8501

**UIs**:
- Stock Management: http://localhost:5001/stock-management
- Single Agent: http://localhost:5001/single-agent-viewer
- Triple Agent: http://localhost:5001/triple-agent

---

**Status**: ✅ FIXED - Ready to test UI connections!
