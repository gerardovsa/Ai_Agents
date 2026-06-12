# 🔧 Browser Console Commands - Module System Diagnostics

## ⚠️ CRITICAL: Use `window.moduleLoader` NOT `window.ModuleLoaderV4`

**The Issue:**
- `window.ModuleLoaderV4` = The **CLASS** (constructor)
- `window.moduleLoader` = The **INSTANCE** (singleton object)

You must use the **instance** to access modules!

---

## ✅ Correct Commands (Copy-Paste These)

### 1. Check Module Loader Status
```javascript
// Check if instance exists
console.log('ModuleLoader instance:', window.moduleLoader);
console.log('Initialized:', window.moduleLoader?.initialized);
console.log('User ID:', window.moduleLoader?.userId);
```

### 2. List All Modules
```javascript
// Get all loaded modules
const modules = Array.from(window.moduleLoader.modules.entries());
console.log(`Total modules: ${modules.length}`);

// Show first 5 modules
modules.slice(0, 5).forEach(([id, mod]) => {
  console.log(`${id}: available=${mod.available}`);
});
```

### 3. Check Communication Hub & Universal Search
```javascript
// Find specific modules
const modules = Array.from(window.moduleLoader.modules.entries());
const comm = modules.find(([id]) => id === 'communication-hub');
const univ = modules.find(([id]) => id === 'universal-search');

console.log('Communication Hub:', {
  found: !!comm,
  available: comm?.[1]?.available,
  icon: comm?.[1]?.icon,
  name: comm?.[1]?.name
});

console.log('Universal Search:', {
  found: !!univ,
  available: univ?.[1]?.available,
  icon: univ?.[1]?.icon,
  name: univ?.[1]?.name
});
```

### 4. Force Set Available & Regenerate Buttons
```javascript
// Set modules as available
window.moduleLoader.modules.get('communication-hub').available = true;
window.moduleLoader.modules.get('universal-search').available = true;

// Regenerate sidebar buttons
await window.moduleLoader.generateSidebarButtons();

console.log('✅ Buttons regenerated!');
```

### 5. Check Sidebar Container
```javascript
// Find sidebar and buttons
const sidebar = document.getElementById('sidebarModulesSection');
const container = document.getElementById('module-buttons-container');

console.log('Sidebar exists:', !!sidebar);
console.log('Container exists:', !!container);
console.log('Total buttons:', container?.children.length);

// List all button module IDs
if (container) {
  const buttonIds = Array.from(container.children).map(btn => btn.dataset.moduleId);
  console.log('Button IDs:', buttonIds);
  console.log('Has comm-hub:', buttonIds.includes('communication-hub'));
  console.log('Has univ-search:', buttonIds.includes('universal-search'));
}
```

### 6. Manual Button Creation (Last Resort)
```javascript
// If buttons still missing, create them manually
const container = document.getElementById('module-buttons-container');

// Communication Hub Button
const commBtn = document.createElement('button');
commBtn.className = 'sidebar-icon-btn';
commBtn.title = 'Communication Hub';
commBtn.dataset.moduleId = 'communication-hub';
const commIcon = document.createElement('i');
commIcon.className = 'fas fa-comments';
commIcon.style.color = '#6366f1';
commBtn.appendChild(commIcon);
commBtn.addEventListener('click', async () => {
  await window.moduleLoader.loadModule('communication-hub', 'dashboard');
});
container.appendChild(commBtn);

// Universal Search Button
const univBtn = document.createElement('button');
univBtn.className = 'sidebar-icon-btn';
univBtn.title = 'Universal Search';
univBtn.dataset.moduleId = 'universal-search';
const univIcon = document.createElement('i');
univIcon.className = 'fas fa-search';
univIcon.style.color = '#6B7280';
univBtn.appendChild(univIcon);
univBtn.addEventListener('click', async () => {
  await window.moduleLoader.loadModule('universal-search', 'sidebar');
});
container.appendChild(univBtn);

console.log('✅ Manual buttons created!');
```

### 7. Force Module System Reload
```javascript
// Reinitialize entire module system
const userId = parseInt(localStorage.getItem('user_id')) || 1;
await window.initializeModuleSystem(true);  // force reload
console.log('✅ Module system reloaded');
```

---

## 🔍 Diagnostic Checklist

Run these in order and report results:

```javascript
// ===== STEP 1: Check if module loader loaded =====
console.log('1. ModuleLoader class exists:', typeof window.ModuleLoaderV4 !== 'undefined');
console.log('2. ModuleLoader instance exists:', typeof window.moduleLoader !== 'undefined');
console.log('3. Instance initialized:', window.moduleLoader?.initialized);

// ===== STEP 2: Check module counts =====
console.log('4. Total modules loaded:', window.moduleLoader?.modules?.size);
console.log('5. Module list fetch:', await fetch('/api/modules/list').then(r => r.json()).then(d => d.count));

// ===== STEP 3: Check specific modules =====
const comm = window.moduleLoader?.modules.get('communication-hub');
const univ = window.moduleLoader?.modules.get('universal-search');
console.log('6. Comm-hub exists:', !!comm);
console.log('7. Comm-hub available:', comm?.available);
console.log('8. Univ-search exists:', !!univ);
console.log('9. Univ-search available:', univ?.available);

// ===== STEP 4: Check sidebar =====
const container = document.getElementById('module-buttons-container');
console.log('10. Sidebar container exists:', !!container);
console.log('11. Total buttons:', container?.children.length);
console.log('12. Button IDs:', Array.from(container?.children || []).map(b => b.dataset.moduleId));
```

---

## 📊 Expected vs Actual Results

### ✅ Expected (All Good)
```
1. ModuleLoader class exists: true
2. ModuleLoader instance exists: true
3. Instance initialized: true
4. Total modules loaded: 22
5. Module list fetch: 22
6. Comm-hub exists: true
7. Comm-hub available: true
8. Univ-search exists: true
9. Univ-search available: true
10. Sidebar container exists: true
11. Total buttons: 10+
12. Button IDs: [...includes 'communication-hub' and 'universal-search'...]
```

### ❌ If You See This
```
1. ModuleLoader class exists: true
2. ModuleLoader instance exists: true
3. Instance initialized: true
4. Total modules loaded: 22
5. Module list fetch: 22
6. Comm-hub exists: true
7. Comm-hub available: FALSE  ← PROBLEM!
8. Univ-search exists: true
9. Univ-search available: FALSE  ← PROBLEM!
```

**Fix:** Run command #4 above (Force Set Available)

### ❌ If Module Loader Not Loaded
```
1. ModuleLoader class exists: false
2. ModuleLoader instance exists: false
```

**Fix:** 
1. Check for JavaScript errors in console
2. Hard refresh browser (CTRL+SHIFT+R)
3. Check Network tab - verify `module-loader-v4.js` loaded successfully

---

## 🚨 Common Errors & Fixes

### Error: `Cannot read properties of undefined (reading 'modules')`
**Cause:** Using `window.ModuleLoaderV4` instead of `window.moduleLoader`  
**Fix:** Use `window.moduleLoader.modules` (lowercase)

### Error: Module loader not initialized
**Cause:** Authentication not complete or initialization failed  
**Fix:** 
```javascript
// Check auth status
console.log('Auth token:', localStorage.getItem('token'));
console.log('User ID:', localStorage.getItem('user_id'));

// Force reinitialize
await window.initializeModuleSystem(true);
```

### Buttons exist but clicking does nothing
**Cause:** Event handlers not attached or module not available  
**Fix:**
```javascript
// Check if buttons have click handlers
const btn = document.querySelector('[data-module-id="communication-hub"]');
console.log('Has listeners:', btn?._hasListeners);

// Check module availability
console.log('Available:', window.moduleLoader.modules.get('communication-hub')?.available);
```

---

**Last Updated:** November 30, 2025  
**Use:** `window.moduleLoader` not `window.ModuleLoaderV4`
