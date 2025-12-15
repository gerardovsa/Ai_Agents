# PARAMETRIC CAD MODULE - QUICK TEST GUIDE

**Status:** ✅ READY FOR TESTING  
**Date:** December 15, 2025

---

## 🚀 Quick Start

### 1. Refresh Browser
Press **Ctrl + Shift + R** (hard refresh) to clear cache

### 2. Open Test Page
```
http://localhost:5001/external/modules/parametric-cad/SMOKE_TEST.html
```

### 3. Run Tests
Click **"▶️ Run All Tests"** button

---

## ✅ Expected Results

### Automated Tests (7/7 should pass)
- ✅ **Manifest Accessible** - Module metadata loads
- ✅ **Manifest Structure** - All required fields present
- ✅ **HTML File Accessible** - UI template loads
- ✅ **CSS File Accessible** - Styling loads
- ✅ **JS File Accessible** - JavaScript engine loads
- ✅ **CDN Dependencies** - Three.js, OrbitControls, OpenCascade.js
- ⏳ **Module Loader** - Pending (normal for standalone test)

### Browser Console (Expected Logs)
```
✅ OrbitControls loaded: function
✅ OpenCascade.js loaded, initializing WASM...
✅ OpenCascade.js WASM initialized
🔧 [ParametricCAD] Initializing...
⏳ [ParametricCAD] Loading OpenCascade.js WASM module...
✅ [ParametricCAD] OpenCascade.js loaded successfully
✅ [ParametricCAD] Three.js scene initialized
✅ [ParametricCAD] Initialization complete
✅ Parametric CAD ready
```

---

## 🧪 Manual Tests

### Test 1: Load Module in Frame
1. Click **"📦 Load Module in Frame"**
2. Wait 5-10 seconds for WASM to load
3. Should see:
   - Loading overlay disappears
   - 3D viewport with grid
   - Parts library on left
   - Properties panel on right

### Test 2: Create Extrusion
1. Click any part button (e.g., **"▭ 40x40 (500mm)"**)
2. Check console for:
   ```
   🔧 Creating profile8 40x40 extrusion (500mm)
   ```
3. Part should appear in viewport (may be simple box for now)

### Test 3: Orbit Controls
1. Click and drag in viewport - should rotate view
2. Mouse wheel - should zoom in/out
3. Right-click drag - should pan

### Test 4: Export
1. Click **"📄 Export STEP"**
2. Should download `design.step` file
3. Open in CAD software to verify

---

## ⚠️ Known Issues (Expected)

### Simplified Geometry
**Issue:** Parts appear as simple boxes instead of T-slot profiles  
**Status:** Expected - documented limitation  
**Fix:** Requires full T-slot cross-section implementation

### Placeholder Tessellation
**Issue:** May see cube geometry instead of actual extrusion shape  
**Status:** Expected - documented limitation  
**Fix:** Requires OpenCascade mesh extraction implementation

### Coming Soon Alerts
**Issue:** DXF export, AI assistant show "coming soon" alerts  
**Status:** Expected - features not yet implemented

---

## 🐛 Unexpected Errors

### If you see: "opencascade is not defined"
**Fix:** Hard refresh browser (Ctrl + Shift + R)

### If you see: "OrbitControls is not defined"
**Fix:** Check browser console for import errors, hard refresh

### If you see: "Failed to load OpenCascade.js"
**Fix:** Check internet connection, CDN may be blocked

### If module doesn't load at all
**Fix:** 
```powershell
# Restart Flask
cd c:\Users\gpoli\GIT\AI_agents\AI_infrastructure
Get-Job | Remove-Job -Force
Get-Process python | Where-Object {$_.CommandLine -match "flask"} | Stop-Process
python flask_app.py
```

---

## 📊 Test Checklist

- [ ] All 6 automated tests pass
- [ ] Module loads in iframe preview
- [ ] 3D viewport renders with grid
- [ ] OrbitControls work (rotate, zoom, pan)
- [ ] Parts library buttons visible
- [ ] Can create extrusion (shows console log)
- [ ] Export STEP downloads file
- [ ] No critical errors in console

---

## 🎯 Success Criteria

**PASS** if:
- ✅ 6/7 automated tests pass (registry test can be pending)
- ✅ OpenCascade.js WASM initializes
- ✅ Three.js scene renders
- ✅ No "is not defined" errors
- ✅ Module fully interactive

**NEEDS WORK** if:
- ❌ CDN loading errors
- ❌ "opencascade is not defined"
- ❌ Module doesn't initialize
- ❌ Critical JavaScript errors

---

## 🔧 Fixed Issues (This Session)

### Issue 1: OrbitControls 404
**Before:** Using deprecated `/examples/js/` path  
**After:** Using modern `/examples/jsm/` ES module path  
**Status:** ✅ FIXED

### Issue 2: OpenCascade.js 404
**Before:** Using non-existent beta.2 version  
**After:** Using stable v1.1.1  
**Status:** ✅ FIXED

### Issue 3: "opencascade is not defined"
**Before:** Trying to call `opencascade()` before script loaded  
**After:** Using `window.opencascadeReady` Promise  
**Status:** ✅ FIXED

### Issue 4: "initOpenCascade not found"
**Before:** Looking for wrong function name  
**After:** Using correct `opencascade()` function  
**Status:** ✅ FIXED

---

## 📝 Next Steps After Testing

### If Tests Pass:
1. Test creating multiple extrusions
2. Test template functions (workbench, enclosure, frame)
3. Verify export functionality works
4. Plan full T-slot geometry implementation

### If Tests Fail:
1. Copy console errors
2. Check browser DevTools Network tab for failed requests
3. Report specific error messages
4. Check Flask server logs

---

## 🎓 Developer Notes

### Module Architecture
- **Frontend:** Pure browser-based (no backend CAD processing)
- **CAD Engine:** OpenCascade.js (OCCT compiled to WebAssembly)
- **3D Rendering:** Three.js with OrbitControls
- **Collaboration:** Supabase Realtime (optional)
- **Export:** Native STEP/STL via OpenCascade

### Performance
- **WASM Load:** 5-10 seconds first time (then cached)
- **File Size:** ~330KB OpenCascade.js + ~600KB Three.js
- **Memory:** ~50MB for small assemblies

### Browser Compatibility
- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ⚠️ Safari (limited WebAssembly support)
- ❌ IE11 (not supported)

---

**End of Quick Test Guide**  
**Ready to test!** 🚀
