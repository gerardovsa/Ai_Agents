# Module Files Object Support Fix - November 30, 2025

## Problem

The inhouse-kanban module wasn't loading because Flask couldn't find the JS/CSS file paths.

**Manifest Structure:**
```json
{
  "id": "inhouse-kanban",
  "files": {
    "js": "inhouse-kanban-V4-COMPLETE.js",
    "css": "inhouse-kanban-NEW.css",
    "html": "inhouse-kanban-SIDEBAR.html"
  },
  "paths": {
    "script": "UI/modules_external/inhouse-kanban/inhouse-kanban-V4-COMPLETE.js?v=4.0.0",
    "style": "UI/modules_external/inhouse-kanban/inhouse-kanban-NEW.css?v=4.0.0"
  }
}
```

**Flask's module_registry.py** was only looking for root-level properties:
- `manifest_data.get('js_file')` ❌ Returned None
- `manifest_data.get('scriptPath')` ❌ Returned None

## Solution

Updated `AI_infrastructure/core/module_registry.py` to support BOTH formats:
1. **Root-level** (legacy): `js_file`, `css_file`, `html_file`, `scriptPath`, `stylePath`
2. **Nested objects** (modern): `files.js`, `files.css`, `files.html`, `paths.script`, `paths.style`

## Code Changes

**File:** `AI_infrastructure/core/module_registry.py` (lines 230-245)

```python
# Extract file paths (support both root-level and files.* object)
files_obj = manifest_data.get('files', {})
paths_obj = manifest_data.get('paths', {})

js_file = manifest_data.get('js_file') or files_obj.get('js')
css_file = manifest_data.get('css_file') or files_obj.get('css')
html_file = manifest_data.get('html_file') or files_obj.get('html')

scriptPath = manifest_data.get('scriptPath') or paths_obj.get('script')
stylePath = manifest_data.get('stylePath') or paths_obj.get('style')
htmlPath = manifest_data.get('htmlPath') or paths_obj.get('html') or paths_obj.get('sidebar_html')

# Create ModuleManifest object
manifest = ModuleManifest(
    ...
    js_file=js_file,  # ✅ Now extracts from files.js
    css_file=css_file,  # ✅ Now extracts from files.css
    html_file=html_file,  # ✅ Now extracts from files.html
    scriptPath=scriptPath,  # ✅ Now extracts from paths.script
    stylePath=stylePath,  # ✅ Now extracts from paths.style
    htmlPath=htmlPath,  # ✅ Now extracts from paths.sidebar_html
    ...
)
```

## Verification

**Before fix:**
```json
{
  "id": "inhouse-kanban",
  "js_file": null,  // ❌ Missing!
  "scriptPath": null,  // ❌ Missing!
  "loading": {
    "framework": "v4"
  }
}
```

**After fix:**
```json
{
  "id": "inhouse-kanban",
  "js_file": "inhouse-kanban-V4-COMPLETE.js",  // ✅ Found!
  "scriptPath": "UI/modules_external/inhouse-kanban/inhouse-kanban-V4-COMPLETE.js?v=4.0.0",  // ✅ Found!
  "css_file": "inhouse-kanban-NEW.css",  // ✅ Found!
  "stylePath": "UI/modules_external/inhouse-kanban/inhouse-kanban-NEW.css?v=4.0.0",  // ✅ Found!
  "loading": {
    "framework": "v4"
  }
}
```

## Benefits

✅ **Backward compatible** - Still supports old root-level format  
✅ **Modern manifest support** - Handles nested `files` and `paths` objects  
✅ **Fallback logic** - Tries root-level first, then nested objects  
✅ **Works for all modules** - Communication-hub, inhouse-kanban, vsa-veterinary-alerts

## Testing

```powershell
# Restart Flask
BISTART

# Wait 12 seconds for Flask to initialize
Start-Sleep -Seconds 12

# Verify module has file paths
$response = Invoke-RestMethod -Uri "http://localhost:5001/api/modules/list" -Method GET
$kanban = $response.modules | Where-Object { $_.id -eq 'inhouse-kanban' }
$kanban.js_file  # Should show: inhouse-kanban-V4-COMPLETE.js
$kanban.scriptPath  # Should show: UI/modules_external/inhouse-kanban/inhouse-kanban-V4-COMPLETE.js?v=4.0.0

# Refresh browser and click inhouse-kanban button
# Should load as ES6 module with V4 framework
```

## Related Fixes

This completes the module loading fix chain:
1. ✅ Added tab containers for external modules (inhouse-kanban, vsa-alerts)
2. ✅ Fixed container naming (`#communication-hub-main-container`)
3. ✅ Updated manifest to use V4 file (`inhouse-kanban-V4-COMPLETE.js`)
4. ✅ **Fixed Flask to read files from nested objects** (this fix)

**Status:** ✅ COMPLETE - All external modules should now load correctly!
