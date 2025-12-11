# Calculator Test Dashboard Guide

## 🎯 Purpose
Visual dashboard to test all 35 quote calculators through **Registry V3** - the exact same way AI agents use them.

## 📋 Prerequisites

### 1. Flask Server Must Be Running
```powershell
# Start the Flask server (BISTART)
cd C:\Users\gpoli\GIT\AI_agents
python AI_infrastructure/flask_app.py
```

Server runs on: `http://localhost:5001`

### 2. Test File Location
Test suite is located at:
```
UI/modules_external/quote-calculator/tests/test_all_calculators.py
```

## 🚀 How to Use Dashboard

### Step 1: Start Flask Server
```powershell
# Navigate to project root
cd C:\Users\gpoli\GIT\AI_agents

# Start Flask server (BISTART)
python AI_infrastructure/flask_app.py

# Wait for: "Running on http://localhost:5001"
```

### Step 2: Open Dashboard
```
Open in browser:
file:///C:/Users/gpoli/GIT/AI_agents/calculator_test_dashboard.html
```

### Step 3: Check Server Status
- Dashboard will automatically check server status
- Look for: ✓ Server Connected (green indicator)
- If disconnected, ensure Flask server is running

### Step 4: Run Tests
1. **Test Shopify Calculators**: Click "Run Shopify Tests" button
2. **Test GOD Calculators**: Click "Run GOD Tests" button
3. **Test All Calculators**: Click "Run All Tests" button

## 🔍 What Gets Tested

Dashboard runs 4 test phases for each calculator:

### 1. **Discovery** (Registry V3 Registration)
- ✅ Checks if calculator exists in Registry V3
- ✅ Verifies platform (shopify/god)
- ✅ Shows description

### 2. **Schema** (Parameter Structure)
- ✅ Loads parameter schema from Registry V3
- ✅ Shows total parameters
- ✅ Shows required parameters
- ✅ Lists parameter names

### 3. **Requirements** (Enum Guidance)
- ✅ Checks parameter validation rules
- ✅ Shows enum constraints
- ✅ Validates parameter types

### 4. **Execution** (Actual Quote Calculation)
- ✅ Executes calculator via Flask API
- ✅ Uses Registry V3 (exact AI pattern)
- ✅ Shows quote price
- ✅ Shows execution time
- ✅ Shows sample parameters used

## 📊 Dashboard Features

### Real-Time Logging
- All test results appear in console log
- Color-coded messages:
  - 🟢 Green = Success
  - 🔴 Red = Error
  - 🟡 Yellow = Info

### Progress Tracking
- Visual progress bar
- Tests passed/failed counters
- Current test indicator

### Test Details
- Click calculator name to see detailed results
- Shows quote breakdown
- Shows parameter values used
- Shows error tracebacks if failed

## 🔧 API Endpoints Used

Dashboard connects to these Flask endpoints:

### 1. Health Check
```javascript
GET http://localhost:5001/health
```
Verifies Flask server is running

### 2. List Calculators
```javascript
GET http://localhost:5001/api/calculator/list
```
Returns all 35+ calculators from Registry V3

### 3. Test Calculator
```javascript
POST http://localhost:5001/api/calculator/test
Body: {
    "tool_name": "calculate_business_cards",
    "params": {"quantity": 1000, "stock_type": "premium", "sides": 2}
}
```
Executes calculator through Registry V3

## ✅ Expected Results

**All 35 calculators should PASS:**
- ✅ 25 Shopify calculators
- ✅ 3 GOD calculators
- ✅ 7 additional calculators

**Success Rate: 100%** (35/35 working)

## 🐛 Troubleshooting

### Server Disconnected
```
❌ Problem: Red "Server Disconnected" indicator

✅ Solution:
1. Check Flask server is running
2. Check port 5001 is not blocked
3. Verify server output shows "Running on http://localhost:5001"
```

### 404 Errors
```
❌ Problem: "HTTP 404: Not Found"

✅ Solution:
1. Ensure Flask app has calculator endpoints
2. Check AI_infrastructure/flask_app.py has:
   - POST /api/calculator/test
   - GET /api/calculator/list
3. Restart Flask server
```

### Calculator Execution Fails
```
❌ Problem: "Execution ERROR"

✅ Solution:
1. Check Registry V3 is loaded (server logs)
2. Verify calculator wrapper exists
3. Check database connection (for GOD calculators)
4. Review traceback in dashboard log
```

### Import Errors
```
❌ Problem: "ModuleNotFoundError: No module named 'Decimal'"

✅ Solution:
1. Ensure Python environment has all dependencies
2. Check imports in calculator_wrapper.py:
   - from decimal import Decimal
   - import traceback
3. Restart Flask server
```

## 📝 Sample Test Flow

```
1. User clicks "Run All Tests"
2. Dashboard checks server status ✅
3. Dashboard loads calculator list from Registry V3 ✅
4. For each calculator:
   a. Discovery Test - Check Registry V3 ✅
   b. Schema Test - Load parameters ✅
   c. Requirements Test - Check enums ✅
   d. Execution Test - Run calculation via Flask API ✅
5. Dashboard shows results:
   - ✅ 35/35 PASSED
   - Total execution time
   - Individual calculator details
```

## 🎯 Why This Matters

**Dashboard Replicates EXACT AI Usage:**
- ✅ Uses Registry V3 (not mock data)
- ✅ Calls Flask API (same as AI agents)
- ✅ Same parameter passing
- ✅ Same response format
- ✅ Real quote calculations

**This is NOT a simulation** - the dashboard executes actual calculators through the production Registry V3 system.

## 📚 Related Files

- **Dashboard**: `calculator_test_dashboard.html` (this file)
- **Test Suite**: `UI/modules_external/quote-calculator/tests/test_all_calculators.py`
- **Flask API**: `AI_infrastructure/flask_app.py` (endpoints at lines 462-590)
- **Registry V3**: `tools/registry_v3.py`
- **Calculator Wrapper**: `UI/modules_external/quote-calculator/implementations/calculator_wrapper.py`
- **Test Documentation**: `UI/modules_external/quote-calculator/tests/README.md`

## 🚀 Quick Start Commands

```powershell
# Terminal 1: Start Flask Server
cd C:\Users\gpoli\GIT\AI_agents
python AI_infrastructure/flask_app.py

# Terminal 2: Run Python Tests (Alternative)
cd C:\Users\gpoli\GIT\AI_agents
python UI/modules_external/quote-calculator/tests/test_all_calculators.py

# Browser: Open Dashboard
# file:///C:/Users/gpoli/GIT/AI_agents/calculator_test_dashboard.html
```

---

**Status**: ✅ All 35 calculators working (100% success rate)
**Last Updated**: December 2025
**AI Integration**: Full Registry V3 compatibility
