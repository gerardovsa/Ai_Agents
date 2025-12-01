# ModuleLoader V4 Path Resolution Fix - November 30, 2025

## Problem

Communication Hub and other modules were failing to load with 404 errors:

```
GET http://localhost:5001/external/modules/communication-hub/communication-hub.js net::ERR_ABORTED 404 (NOT FOUND)
```

**Root Cause:**
- ModuleLoader was looking for `manifest.paths.script` but manifest uses `manifest.paths.js`
- ModuleLoader wasn't checking `manifest.js_file` property (V3 manifest format)
- Manifest paths included `UI/modules_external/` prefix, but Flask serves at `/external/modules/`

## Solution

Updated `UI/shared/js/module-loader-v4.js` to support multiple manifest formats and normalize paths:

### Fix #1: Enhanced JS Path Resolution (Lines 160-172)

**Before:**
```javascript
const modulePath = manifest.paths?.script || manifest.scriptPath || `external/modules/${moduleId}/${manifest.files?.js || moduleId + '.js'}`;
```

**After:**
```javascript
// Check multiple manifest formats for compatibility:
// - manifest.paths.script (V4 format)
// - manifest.paths.js (alternative V4 format)
// - manifest.scriptPath (legacy)
// - manifest.js_file (V3 format)
// - fallback: external/modules/{moduleId}/{moduleId}.js
const modulePath = manifest.paths?.script 
    || manifest.paths?.js 
    || manifest.scriptPath 
    || (manifest.js_file ? `external/modules/${moduleId}/${manifest.js_file}` : null)
    || `external/modules/${moduleId}/${manifest.files?.js || moduleId + '.js'}`;
```

### Fix #2: Path Normalization for Flask Routing (Lines 203-215)

**Added:**
```javascript
// Normalize path for Flask routing
let importPath = modulePath;

// Strip UI/modules_external/ or UI/modules_internal/ prefix if present
// Flask serves modules at /external/modules/ and /internal/modules/
if (importPath.includes('UI/modules_external/')) {
    importPath = importPath.replace('UI/modules_external/', 'external/modules/');
} else if (importPath.includes('UI/modules_internal/')) {
    importPath = importPath.replace('UI/modules_internal/', 'internal/modules/');
}
```

### Fix #3: Enhanced CSS Path Resolution (Lines 372-395)

**Before:**
```javascript
const cssPath = manifest.paths?.style || manifest.stylePath || `external/modules/${moduleId}/${manifest.css_file || manifest.files?.css || moduleId + '.css'}`;
```

**After:**
```javascript
// Check multiple manifest formats for compatibility
let cssPath = manifest.paths?.style 
    || manifest.paths?.css 
    || manifest.stylePath 
    || (manifest.css_file ? `external/modules/${moduleId}/${manifest.css_file}` : null)
    || `external/modules/${moduleId}/${manifest.files?.css || moduleId + '.css'}`;

// Normalize path for Flask routing
if (cssPath.includes('UI/modules_external/')) {
    cssPath = cssPath.replace('UI/modules_external/', 'external/modules/');
} else if (cssPath.includes('UI/modules_internal/')) {
    cssPath = cssPath.replace('UI/modules_internal/', 'internal/modules/');
}

// Ensure absolute path
if (!cssPath.startsWith('/') && !cssPath.startsWith('http')) {
    cssPath = '/' + cssPath;
}
```

## Supported Manifest Formats

The ModuleLoader now supports all these manifest property combinations:

### V4 Modern Format
```json
{
    "paths": {
        "script": "external/modules/mymodule/mymodule.js",
        "style": "external/modules/mymodule/mymodule.css"
    }
}
```

### V4 Alternative Format (communication-hub uses this)
```json
{
    "paths": {
        "js": "UI/modules_external/communication-hub/communication-hub-v4-modern.js",
        "css": "UI/modules_external/communication-hub/communication-hub.css"
    }
}
```

### V3 Legacy Format
```json
{
    "js_file": "communication-hub-v4-modern.js",
    "css_file": "communication-hub.css"
}
```

### Legacy scriptPath/stylePath
```json
{
    "scriptPath": "external/modules/mymodule/mymodule.js",
    "stylePath": "external/modules/mymodule/mymodule.css"
}
```

## Flask Route Compatibility

Flask serves module files at:
- `/external/modules/<module_id>/<filename>` (defined in flask_app.py line 849)
- `/UI/modules_external/<module_id>/<filename>` (alternative route, line 875)

The path normalization ensures all manifest formats map to these Flask routes correctly.

## Testing

1. **Hard refresh browser** (CTRL+SHIFT+R)
2. **Click Communication Hub button** - Should load without 404 errors
3. **Check console logs** - Should see:
   ```
   [ModuleLoaderV4] 🔷 Importing ES6 module: /external/modules/communication-hub/communication-hub-v4-modern.js
   [ModuleLoaderV4] ✅ Loaded CSS for communication-hub
   ```

## Files Modified

- `UI/shared/js/module-loader-v4.js` (3 sections updated)

## Compatibility

✅ **Backward Compatible** - All existing manifest formats still work  
✅ **Forward Compatible** - Supports new V4 manifest formats  
✅ **Path Normalization** - Handles full paths and relative paths  
✅ **Flask Integration** - Maps to correct Flask routes

---

**Status:** ✅ Complete  
**Date:** November 30, 2025  
**Tested:** Pending user verification
