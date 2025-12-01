# VSA Veterinary Alerts - Quick Start Guide

**5-Minute Setup & Testing Guide**

---

## Step 1: Verify Files Exist (30 seconds)

Check that all files were created:

```powershell
cd c:\Users\gpoli\GIT\AI_agents\UI\modules_external\vsa-veterinary-alerts
ls
```

**Expected output:**
```
INTEGRATION_COMPLETE.md
manifest.json
README.md
VERIFY_MODULE.js
vsa-alerts-sidebar.html
vsa-veterinary-alerts.css
vsa-veterinary-alerts.js
```

✅ All 7 files present → Continue  
❌ Files missing → Re-run creation commands

---

## Step 2: Start AI_agents Server (1 minute)

```powershell
cd c:\Users\gpoli\GIT\AI_agents
BISTART
```

Wait for:
- Flask server starts on port 5001
- Tools load (594 tools)
- No errors in console

---

## Step 3: Open Browser (30 seconds)

Navigate to: **http://localhost:5001**

Wait for AI_agents interface to load.

---

## Step 4: Verify Module Detected (1 minute)

Open browser console (F12), paste and run:

```javascript
// Quick check
const loader = window.ModuleLoaderV4;
console.log('Module available:', loader.isModuleAvailable('vsa-veterinary-alerts'));
```

**Expected:** `Module available: true`

If `false`, check browser console for errors.

---

## Step 5: Load Module (30 seconds)

In browser console:

```javascript
// Load module
await window.ModuleLoaderV4.loadModule('vsa-veterinary-alerts', 'dashboard');
console.log('Module loaded:', window.ModuleLoaderV4.isModuleLoaded('vsa-veterinary-alerts'));
```

**Expected:** `Module loaded: true`

---

## Step 6: Run Full Verification (1 minute)

Copy the entire contents of `VERIFY_MODULE.js` into browser console and press Enter.

**Expected output:**
```
=== VSA Veterinary Alerts Module Verification ===

[Test 1] Checking ModuleLoaderV4...
✅ ModuleLoaderV4 found

[Test 2] Checking module availability...
✅ vsa-veterinary-alerts module is available

[Test 3] Checking manifest.json...
✅ Manifest loaded

[Test 4] Loading module (dashboard)...
✅ Module loaded successfully

[Test 5] Checking module instance...
✅ Module is loaded
✅ All utilities injected
✅ Module state exists
✅ Supabase client initialized
✅ Data loaded from Supabase

=== Verification Summary ===
✅ Passed: 12
🎉 ALL TESTS PASSED! Module is working correctly.
```

---

## Step 7: View Dashboard (30 seconds)

In AI_agents interface:
1. Look for **"VSA Alerts"** tab in navigation
2. Click on it
3. Dashboard should display with alerts/follow-ups

**Expected:**
- Header: "VSA Veterinary Alerts"
- Stats cards (5 metrics)
- Filter controls
- Alert/follow-up cards (if data exists)

---

## Step 8: Test Sidebar (30 seconds)

1. Look for draggable **"Quick Alerts"** button on left side
2. Click to open sidebar
3. Sidebar shows high-priority alerts

**Expected:**
- Sidebar slides in from left
- Shows quick alerts
- "View All" button works

---

## Troubleshooting

### Module Not Found

**Symptom:** `isModuleAvailable() returns false`

**Solutions:**
1. Check files exist in correct directory
2. Verify `manifest.json` is valid JSON
3. Restart Flask server (BISTART)
4. Hard refresh browser (Ctrl+Shift+R)

### Supabase Connection Failed

**Symptom:** "Supabase initialization failed" error

**Solutions:**
1. Check internet connection
2. Verify Supabase URL is reachable
3. Check browser console Network tab for failed requests
4. Try loading Supabase library manually:
   ```javascript
   // In console
   const script = document.createElement('script');
   script.src = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2';
   document.head.appendChild(script);
   ```

### No Data Loading

**Symptom:** Empty state displayed, no alerts/follow-ups

**Solutions:**
1. Check database has data:
   - Open: https://supabase.com/dashboard/project/wuwmvtslltqhaycyukxk
   - Query: `SELECT COUNT(*) FROM veterinary_calls WHERE manager_alerts_tags IS NOT NULL`
2. Verify credentials correct in `vsa-veterinary-alerts.js`
3. Check browser console for API errors
4. Test direct Supabase connection:
   ```javascript
   const instance = window.ModuleLoaderV4.moduleInstances.get('vsa-veterinary-alerts');
   console.log('Error:', instance.state.error);
   ```

### Module Loads but UI Blank

**Symptom:** Module loaded, but dashboard empty

**Solutions:**
1. Check CSS loaded:
   ```javascript
   const css = document.querySelector('link[href*="vsa-veterinary-alerts.css"]');
   console.log('CSS loaded:', !!css);
   ```
2. Check container exists:
   ```javascript
   const instance = window.ModuleLoaderV4.moduleInstances.get('vsa-veterinary-alerts');
   console.log('Container:', instance.container);
   ```
3. Force re-render:
   ```javascript
   instance.renderDashboard();
   ```

---

## Quick Debug Commands

```javascript
// Enable debug logging
window.ModuleLoaderV4.enableDebug();

// Get module instance
const module = window.ModuleLoaderV4.moduleInstances.get('vsa-veterinary-alerts');

// Check state
console.log('State:', module.state);

// Check data
console.log('Alerts:', module.state.alerts);
console.log('Follow-ups:', module.state.followUps);

// Check loading
console.log('Loading:', module.state.loading);
console.log('Error:', module.state.error);

// Force refresh
await module.refreshData();

// Re-render
module.renderDashboard();

// Reload module
await window.ModuleLoaderV4.reloadModule('vsa-veterinary-alerts');
```

---

## Expected Data Counts

If connected to VSA database correctly:

**veterinary_calls table:**
- ~500 records (limit)
- ~50-100 alerts (from `manager_alerts_tags`)
- ~30-50 follow-ups (from `follow_up_actions`)

**Stats should show:**
- Total Alerts: 50-100
- High Priority: 15-30
- Pending: 40-90
- Resolved: 0-10
- Follow-ups: 30-50

---

## Success Checklist

✅ All 7 files created  
✅ Flask server running  
✅ Module detected by loader  
✅ Manifest loaded correctly  
✅ Module loaded successfully  
✅ Utilities injected  
✅ Supabase client initialized  
✅ Data loaded from database  
✅ Dashboard displays correctly  
✅ Filters work  
✅ Sidebar opens  
✅ Auto-refresh working  

---

## Next Steps

After successful setup:

1. **Test Filtering:**
   - Try severity filters (High/Medium/Low)
   - Test date ranges (Today/Week/Month/All)
   - Use search box

2. **Test View Modes:**
   - Switch between Alerts/Follow-ups/Both
   - Verify data updates correctly

3. **Test Sidebar:**
   - Open/close sidebar
   - Click alerts to view details
   - Test "View All" button

4. **Monitor Performance:**
   - Check auto-refresh (every 60s)
   - Verify no console errors
   - Check memory usage in DevTools

---

## Documentation

**Full Documentation:** `README.md`  
**Integration Details:** `INTEGRATION_COMPLETE.md`  
**Verification Script:** `VERIFY_MODULE.js`  
**Framework Guide:** `.github/prompts/Module Architect V4.0 - Modern Framework.prompt.md`

---

**Setup Time:** ~5 minutes  
**Status:** ✅ Production Ready  
**Framework:** ModuleLoaderV4 (Modern Composition Pattern)

**Need Help?**
1. Check browser console for errors
2. Enable debug mode: `window.ModuleLoaderV4.enableDebug()`
3. Review troubleshooting section above
4. Check README.md for detailed documentation
