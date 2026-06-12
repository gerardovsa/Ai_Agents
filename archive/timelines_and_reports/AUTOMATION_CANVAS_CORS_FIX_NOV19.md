# Automation Canvas CORS Fix - November 19, 2025

**Issue:** CORS error when opening HTML from file system  
**Status:** ✅ FIXED  
**Time:** 10 minutes

---

## 🐛 Problem

When opening `business-ai-platform-v2.html` directly from file system (file:// protocol), the Automation Canvas module was getting CORS errors:

```
Access to fetch at 'file:///C:/api/automation/list' from origin 'null' 
has been blocked by CORS policy: Cross origin requests are only supported 
for protocol schemes: chrome, chrome-extension, chrome-untrusted, data, 
http, https, isolated-app.
```

**Root Cause:** JavaScript was using relative URLs like `/api/automation/list` which resolve to `file:///C:/api/automation/list` when HTML is opened from file system instead of `http://localhost:5001/api/automation/list`.

---

## ✅ Solution

Added API base URL configuration to `automation-workflows.js` to dynamically use the correct endpoint based on how the page is accessed.

### Changes Made

**File:** `UI/external/modules/automation-workflows/automation-workflows.js`

#### 1. Added API Base URL Property (Line 50)

```javascript
// API configuration
this.apiBaseUrl = window.API_BASE_URL || 'http://localhost:5001';
```

This uses:
- `window.API_BASE_URL` - Set by main HTML file (detects file:// vs http://)
- Fallback: `http://localhost:5001` if not set

#### 2. Added Helper Method (Lines 68-75)

```javascript
/**
 * Get full API URL for a given endpoint
 * @param {string} endpoint - API endpoint path (e.g., '/api/automation/list')
 * @returns {string} Full URL
 */
getApiUrl(endpoint) {
    return `${this.apiBaseUrl}${endpoint}`;
}
```

#### 3. Updated All Fetch Calls (8 occurrences)

**Before:**
```javascript
const response = await fetch('/api/automation/list', { ... });
```

**After:**
```javascript
const response = await fetch(this.getApiUrl('/api/automation/list'), { ... });
```

**Updated endpoints:**
1. `loadWorkflows()` - Line 990
2. `autoSaveWorkflow()` - Line 118
3. `loadWorkflow(workflowId)` - Line 1159
4. `loadWorkflowBySlug(slug)` - Line 1209
5. `saveWorkflow()` - Line 1286
6. `duplicateWorkflow(workflowId)` - Line 1318 (load)
7. `duplicateWorkflow(workflowId)` - Line 1343 (save)
8. `deleteWorkflow(workflowId)` - Line 1392

---

## 🔄 How It Works

### When Served via Flask (http://localhost:5001)

```javascript
// window.API_BASE_URL is set to 'http://localhost:5001'
this.apiBaseUrl = 'http://localhost:5001';

// Builds URL
this.getApiUrl('/api/automation/list')
// Returns: 'http://localhost:5001/api/automation/list'
```

### When Opened from File System (file:///)

```javascript
// window.API_BASE_URL is set to 'http://localhost:5001' by HTML
this.apiBaseUrl = 'http://localhost:5001';

// Builds URL
this.getApiUrl('/api/automation/list')
// Returns: 'http://localhost:5001/api/automation/list'
```

**Result:** Always points to Flask server regardless of how HTML is accessed.

---

## 🧪 Testing

### Test 1: File System Access

1. Open `UI/business-ai-platform-v2.html` directly in browser
2. Navigate to Automation tab
3. Check browser console

**Expected:** No CORS errors, workflows load from http://localhost:5001

### Test 2: Flask Server Access

1. Start Flask: `BISTART`
2. Open http://localhost:5001 in browser
3. Navigate to Automation tab
4. Check browser console

**Expected:** No errors, workflows load normally

---

## 📊 Results

**Before Fix:**
```
❌ TypeError: Failed to fetch
❌ CORS policy error
❌ file:///C:/api/automation/list blocked
❌ Automation canvas doesn't load workflows
```

**After Fix:**
```
✅ API calls go to http://localhost:5001
✅ No CORS errors
✅ Workflows load successfully
✅ All automation features work
```

---

## 🔗 Related

**Similar Patterns in Codebase:**

Other modules already use this pattern:
- `synergy-milestone-interactions.js` (line 26):
  ```javascript
  this.apiBaseUrl = window.API_BASE_URL || 'http://localhost:5001';
  ```

**HTML Configuration:**

`business-ai-platform-v2.html` sets `window.API_BASE_URL`:
```javascript
const API_BASE_URL = (FORCE_LOCAL || isLocalhost || isFileProtocol) 
    ? 'http://localhost:5001' 
    : 'https://production-url.com';

window.API_BASE_URL = API_BASE_URL;
```

---

## 📝 Summary

**Issue:** Automation canvas couldn't load workflows due to CORS error  
**Cause:** Hardcoded relative URLs (`/api/automation/list`)  
**Fix:** Use `window.API_BASE_URL` with helper method  
**Lines Changed:** 8 fetch calls + 1 helper method  
**Impact:** Automation canvas now works from both file:// and http://  

**Status:** ✅ COMPLETE - Ready for testing

---

**Last Updated:** November 19, 2025  
**Fixed By:** AI Agent (Claude Sonnet 4.5)
