# Quick Fix: ModuleLoader V4 Instance vs Class Reference

## 🚨 TL;DR - The Problem

**Error in console:**
```javascript
Uncaught TypeError: ModuleLoaderV4 is not a constructor
    at (index):343:32
```

**Root cause:** Code was trying to instantiate an **already-instantiated object**.

The `module-loader-v4.js` file exports an **instance**, not a class:
```javascript
export default moduleLoader;  // ← Already an instance!
```

But the HTML was doing:
```javascript
import ModuleLoaderV4 from './shared/js/module-loader-v4.js';
const loaderInstance = new ModuleLoaderV4();  // ❌ TypeError!
```

## ✅ The Fix (3 Changes)

### Change 0: Line 343 in `business-ai-platform-v2.html` **← CRITICAL**

```javascript
// ❌ WRONG (trying to instantiate an instance)
import ModuleLoaderV4 from './shared/js/module-loader-v4.js';
const loaderInstance = new ModuleLoaderV4();  // TypeError!
window.ModuleLoaderV4 = ModuleLoaderV4;
window.moduleLoader = loaderInstance;

// ✅ CORRECT (use the exported instance directly)
import moduleLoader from './shared/js/module-loader-v4.js';
window.moduleLoader = moduleLoader;
window.ModuleLoaderV4 = moduleLoader;  // Alias
```

### Change 1: Line 304 in `business-ai-platform-v2.html`

```javascript
// ❌ WRONG (calling on class)
if (moduleLoaderReady && window.ModuleLoaderV4) {
    if (window.ModuleLoaderV4.initialized && !forceReload) {
        return;
    }
    await window.ModuleLoaderV4.initialize(userId);
}

// ✅ CORRECT (calling on instance)
if (moduleLoaderReady && window.moduleLoader) {
    if (window.moduleLoader.initialized && !forceReload) {
        return;
    }
    await window.moduleLoader.initialize(userId);
}
```

### Change 2: Line 367 in `business-ai-platform-v2.html`

```javascript
// ❌ WRONG
if (ModuleLoaderV4 && !ModuleLoaderV4.initialized) {
    await ModuleLoaderV4.initialize(userId);
}

// ✅ CORRECT
if (loaderInstance && !loaderInstance.initialized) {
    await loaderInstance.initialize(userId);
}
```

## 🎯 Rule of Thumb

**ALWAYS use:**
- `window.moduleLoader` → The instance (object with methods)

**NEVER use for method calls:**
- `window.ModuleLoaderV4` → The class (constructor function)

## 🧪 Quick Test

```javascript
// In browser console:
console.log('Instance check:', typeof window.moduleLoader);  // "object" ✅
console.log('Has initialize:', typeof window.moduleLoader.initialize);  // "function" ✅

// This will fail:
console.log('Class check:', typeof window.ModuleLoaderV4.initialize);  // "undefined" ❌
```

## 📝 Developer Checklist

When working with ModuleLoader:
- [ ] Always reference `window.moduleLoader` (not `window.ModuleLoaderV4`)
- [ ] Check `window.moduleLoader.initialized` for state
- [ ] Call `window.moduleLoader.loadModule(id)` to load modules
- [ ] Use `window.moduleLoader.modules` to access loaded modules

---

**Status:** ✅ Fixed November 30, 2025  
**Files changed:** `UI/business-ai-platform-v2.html`  
**Impact:** Fixes module loading for all users
