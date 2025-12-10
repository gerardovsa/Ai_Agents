# 🧪 Calculator Test Dashboard

## Overview

A comprehensive web-based UI for testing all Shopify (25) and GOD (3) calculators with real-time visual feedback.

## Features

### ✅ What It Does

1. **Visual Testing Dashboard**
   - Real-time test execution with progress bars
   - Color-coded status indicators (green=pass, red=fail, yellow=testing)
   - Individual test phases for each calculator
   - Detailed test results with expandable sections

2. **Test Phases (4 per calculator)**
   - ✅ **Discovery** - Can AI find the calculator via search?
   - ✅ **Schema** - Does it have complete parameter definitions?
   - ✅ **Requirements** - Are there enums for AI guidance?
   - ✅ **Execution** - Does the calculator run correctly?

3. **Search Keywords Display**
   - Each calculator shows its search keywords
   - Keywords are in the test config (NOT in calculator JSON schemas)
   - Helps understand how AI agents discover calculators

4. **Separate Sections**
   - Shopify Calculators (25 total)
   - GOD Calculators (3 total)
   - Independent stats for each section

5. **Real-Time Stats**
   - Total calculators
   - Passed/Failed counts
   - Discovery rate percentage
   - Live progress tracking

## Quick Start

### 1. Start the Backend Server

```powershell
cd c:\Users\gpoli\GIT\AI_agents
python calculator_test_server.py
```

You should see:
```
================================================================================
🧪 Calculator Test Dashboard Backend
================================================================================
Total Calculators: 28
  - Shopify: 25
  - GOD: 3

Server starting on http://localhost:5000
```

### 2. Open the Dashboard

Open `calculator_test_dashboard.html` in your browser:

```powershell
Start-Process "calculator_test_dashboard.html"
```

Or simply double-click the HTML file.

### 3. Run Tests

- **Run All Tests** - Tests all 28 calculators
- **Run Shopify Only** - Tests 25 Shopify calculators
- **Run GOD Only** - Tests 3 GOD calculators

Tests run automatically and update in real-time!

## Files Created

### Frontend
- **calculator_test_dashboard.html** (880 lines)
  - Beautiful responsive UI
  - Real-time test visualization
  - Progress tracking
  - Live log window
  - Stats dashboard

### Backend
- **calculator_test_server.py** (411 lines)
  - Flask REST API
  - Test execution engine
  - Calculator discovery testing
  - Schema validation
  - Requirements checking
  - Execution testing

## Search Keywords Configuration

### Shopify Calculator Keywords

All keywords are configured in `calculator_test_server.py`:

```python
CALCULATOR_KEYWORDS = {
    "calculate_bollard_signs": ["bollard", "signs", "quote", "calculator"],
    "calculate_construction_signs": ["construction", "signs", "quote", "calculator"],
    "calculate_saddle_stitch_books": ["booklet", "saddle stitch", "stapled", "book"],
    # ... all 25 Shopify calculators
}
```

### GOD Calculator Keywords

```python
"calculate_god_flyers": ["flyer", "god", "database", "digital", "quote"],
"calculate_god_letterheads": ["letterhead", "god", "database", "stationery", "quote"],
"calculate_god_perfect_bound_books": ["perfect bound", "book", "god", "database", "quote"]
```

### Important Notes

- ✅ **Keywords are in test config only**
- ✅ **NOT added to calculator JSON schemas**
- ✅ **Search uses existing alias system in meta_tools.py**
- ✅ **Keywords help test discoverability**

## API Endpoints

### GET /health
Health check endpoint

### POST /test/discovery
Test calculator discovery via keywords
```json
{
  "calculator": "calculate_saddle_stitch_books",
  "keywords": ["booklet", "saddle stitch", "stapled", "book"]
}
```

### POST /test/schema
Test calculator schema validation
```json
{
  "calculator": "calculate_saddle_stitch_books"
}
```

### POST /test/requirements
Test calculator requirements (enums)
```json
{
  "calculator": "calculate_saddle_stitch_books"
}
```

### POST /test/execution
Test calculator execution
```json
{
  "calculator": "calculate_saddle_stitch_books"
}
```

### GET /calculators/list
Get all calculators with keywords

### POST /test/run-all
Run all tests in batch mode
```json
{
  "type": "all"  // or "shopify" or "god"
}
```

## Test Results

### Visual Indicators

- 🟢 **Green Card** - All tests passed
- 🔴 **Red Card** - One or more tests failed
- 🟡 **Yellow Card** - Currently testing
- ⚪ **Gray Card** - Not tested yet

### Phase Icons

- ✓ - Phase passed
- ✗ - Phase failed
- ⟳ - Currently testing
- 1,2,3,4 - Pending

## Usage Workflow

### Daily Testing Workflow

1. **Make Changes to Calculator**
   - Edit calculator code
   - Modify parameters
   - Update logic

2. **Run Dashboard Tests**
   - Start server
   - Open dashboard
   - Click "Run All Tests"

3. **Review Results**
   - Check which calculators failed
   - Expand details to see errors
   - Fix issues

4. **Re-test**
   - Run tests again
   - Verify all green (100% pass)
   - Deploy with confidence

### Before Deployment

Always run the dashboard to ensure:
- ✅ All calculators discoverable via search
- ✅ All schemas complete
- ✅ All parameters have enum guidance
- ✅ All calculators execute correctly

## Technical Details

### Frontend Stack
- Pure HTML/CSS/JavaScript
- No frameworks required
- Responsive design
- Real-time updates via fetch API

### Backend Stack
- Flask (Python web framework)
- Flask-CORS (cross-origin support)
- Existing test infrastructure

### Test Execution Flow

```
User clicks "Run Tests"
    ↓
Frontend sends POST request per calculator
    ↓
Backend runs 4 test phases
    ↓
Results stream back to frontend
    ↓
UI updates in real-time
    ↓
Summary stats calculated
```

### Performance

- Tests run sequentially (one at a time)
- Each calculator: ~2-5 seconds
- Total time for 28 calculators: ~2-3 minutes
- Can stop tests mid-run

## Troubleshooting

### Server Won't Start

```powershell
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill process if needed
taskkill /PID <PID> /F

# Restart server
python calculator_test_server.py
```

### Dashboard Can't Connect

1. Check server is running
2. Open browser console (F12)
3. Check for CORS errors
4. Verify URL is http://localhost:5000

### Tests Failing

1. Check server logs for errors
2. Expand test details in UI
3. Verify calculator exists
4. Check if tools loaded correctly

## Future Enhancements

Potential additions:
- [ ] Export test results to JSON/CSV
- [ ] Historical test tracking
- [ ] Performance benchmarking
- [ ] Automated regression testing
- [ ] Email notifications on failures
- [ ] Integration with CI/CD pipeline

## Summary

This dashboard gives you a **professional, visual, real-time testing system** for all calculators. 

**No more guessing if calculators work** - just run the dashboard and see instant results!

Perfect for:
- ✅ Pre-deployment validation
- ✅ Regression testing
- ✅ Discovery rate monitoring
- ✅ Schema completeness checking
- ✅ AI agent readiness verification

---

**Status:** ✅ PRODUCTION READY  
**Date:** December 10, 2025  
**Version:** 1.0.0
