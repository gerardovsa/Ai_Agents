# Quick Fix: Module Path Resolution (Nov 30, 2025)

## TL;DR

**Problem:** Communication Hub (and potentially other modules) failing to load with 404 errors  
**Cause:** ModuleLoader not checking `manifest.js_file` and not normalizing `UI/modules_external/` paths  
**Fix:** Enhanced path resolution + Flask route normalization  
**Files Changed:** `UI/shared/js/module-loader-v4.js`

---

## The Error

```
GET http://localhost:5001/external/modules/communication-hub/communication-hub.js 
net::ERR_ABORTED 404 (NOT FOUND)
```

**Why?** ModuleLoader was looking for `communication-hub.js` but actual file is `communication-hub-v4-modern.js`

---

## 3 Changes Made

### Change #1: Check `manifest.js_file`
```javascript
// NOW checks manifest.js_file (V3 format)
const modulePath = manifest.paths?.script 
    || manifest.paths?.js 
    || manifest.scriptPath 
    || (manifest.js_file ? `external/modules/${moduleId}/${manifest.js_file}` : null)  // ← NEW
    || `external/modules/${moduleId}/${moduleId + '.js'}`;
```

### Change #2: Normalize Paths
```javascript
// Strip UI/modules_external/ prefix (Flask doesn't serve that way)
if (importPath.includes('UI/modules_external/')) {
    importPath = importPath.replace('UI/modules_external/', 'external/modules/');
}
```

### Change #3: CSS Path Resolution
Same fixes applied to CSS loading:
- Check `manifest.css_file`
- Check `manifest.paths.css`
- Normalize `UI/modules_external/` → `external/modules/`

---

## Testing Checklist

1. **Hard refresh:** CTRL+SHIFT+R
2. **Click Communication Hub button**
3. **Expected in console:**
   ```
   [ModuleLoaderV4] 🔷 Importing ES6 module: /external/modules/communication-hub/communication-hub-v4-modern.js
   [ModuleLoaderV4] ✅ Loaded CSS for communication-hub
   ```
4. **Module should load** without 404 errors

---

## Manifest Formats Supported

| Format | Property | Example |
|--------|----------|---------|
| V4 Modern | `paths.script` | `external/modules/mymodule/mymodule.js` |
| V4 Alt | `paths.js` | `UI/modules_external/mymodule/mymodule.js` |
| V3 Legacy | `js_file` | `mymodule-v4-modern.js` |
| Legacy | `scriptPath` | `external/modules/mymodule/mymodule.js` |

**All formats now work!**

---

## Git Commit

If successful:
```powershell
cd c:\Users\gpoli\GIT\AI_agents
git add UI/shared/js/module-loader-v4.js
git commit -m "fix: ModuleLoader path resolution - support manifest.js_file and normalize UI paths"
git push origin v10
```

---

**Status:** Ready for testing  
**Expected Result:** Communication Hub loads without errors
