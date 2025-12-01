# InHouse Kanban Sidebar Toggle Test Guide

## 🎯 What Should Happen

When you click the **InHouse Kanban floating toggle button**, the sidebar should:

1. ✅ Slide in from the **left side** (from `left: 60px`)
2. ✅ Use animation: `translateX(-100%)` → `translateX(0)`
3. ✅ Display the sidebar content from `inhouse-kanban-SIDEBAR.html`
4. ✅ Show "Production Workflow" header
5. ✅ Display workboard selector, column selector, and job cards

## 🔍 Debug Steps

### Step 1: Check if Sidebar HTML is in DOM

Open browser console (F12) and run:

```javascript
// Check if sidebar element exists
const sidebar = document.getElementById('inhouse-kanban-sidebar');
console.log('Sidebar element:', sidebar);
console.log('Sidebar classes:', sidebar?.className);
console.log('Sidebar style:', sidebar?.style.cssText);
```

**Expected Output:**
```
Sidebar element: <div id="inhouse-kanban-sidebar" class="module-sidebar kanban-sidebar">
Sidebar classes: module-sidebar kanban-sidebar
Sidebar style: width: 480px; left: 60px; transform: translateX(-100%);
```

### Step 2: Check if Sidebar Controller Exists

```javascript
// Check if sidebar controller is loaded
console.log('Sidebar controller:', window.inhouseKanbanSidebar);
console.log('Has openSidebar:', typeof window.inhouseKanbanSidebar?.openSidebar);
```

**Expected Output:**
```
Sidebar controller: InhouseKanbanSidebar {module: InhouseKanbanModule, ...}
Has openSidebar: function
```

### Step 3: Manually Test Opening Sidebar

```javascript
// Try opening the sidebar manually
if (window.inhouseKanbanSidebar) {
    window.inhouseKanbanSidebar.openSidebar();
} else {
    console.error('❌ Sidebar controller not found!');
}
```

**Expected Result:** Sidebar should slide in from left side.

### Step 4: Check Toggle Button Click Handler

```javascript
// Check if toggle button exists and has click handler
const toggle = document.getElementById('inhouse-kanban-floating-toggle');
console.log('Toggle button:', toggle);
console.log('Toggle dataset:', toggle?.dataset);
```

**Expected Output:**
```
Toggle button: <button id="inhouse-kanban-floating-toggle" ...>
Toggle dataset: {moduleId: 'inhouse-kanban', side: 'left'}
```

### Step 5: Monitor Toggle Click

```javascript
// Add debug logging to see what happens on click
const toggle = document.getElementById('inhouse-kanban-floating-toggle');
if (toggle) {
    toggle.addEventListener('click', () => {
        console.log('🔵 Toggle clicked!');
        console.log('📍 Current side:', toggle.dataset.side);
        console.log('📦 Module loaded:', window.ModuleLoader?.loadedModules.has('inhouse-kanban'));
        console.log('🎯 Sidebar controller:', !!window.inhouseKanbanSidebar);
    }, true); // Use capture phase to see event first
}
```

## 🐛 Common Issues & Fixes

### Issue 1: Sidebar Element Not Found
**Symptom:** `document.getElementById('inhouse-kanban-sidebar')` returns `null`

**Cause:** HTML file not loaded into DOM

**Fix:**
```javascript
// Force load the module
if (window.moduleLoader) {
    await window.moduleLoader.loadModule('inhouse-kanban');
    console.log('✅ Module loaded, checking sidebar again...');
    console.log('Sidebar now:', document.getElementById('inhouse-kanban-sidebar'));
}
```

### Issue 2: Sidebar Controller Not Available
**Symptom:** `window.inhouseKanbanSidebar` is `undefined`

**Cause:** Module JavaScript not initialized

**Fix:**
```javascript
// Check module registry
console.log('Module registry:', window.ModuleRegistry?.['inhouse-kanban']);

// Initialize if needed
if (window.ModuleRegistry?.['inhouse-kanban']?.init) {
    await window.ModuleRegistry['inhouse-kanban'].init();
    console.log('✅ Module initialized');
}
```

### Issue 3: Toggle Doesn't Call openSidebar
**Symptom:** Click does nothing or switches tab instead

**Cause:** Manifest flag `floating_toggle_opens_sidebar` not set

**Fix:** Check manifest.json:
```json
{
    "floating_toggle_opens_sidebar": true,
    "sidebar": {
        "enabled": true
    }
}
```

### Issue 4: Sidebar Opens on Wrong Side
**Symptom:** Sidebar appears on right instead of left

**Cause:** Toggle side not set correctly

**Fix:**
```javascript
// Check and fix toggle side
const toggle = document.getElementById('inhouse-kanban-floating-toggle');
console.log('Current side:', localStorage.getItem('inhouse-kanban-toggle-side'));

// Force left side
localStorage.setItem('inhouse-kanban-toggle-side', 'left');
toggle.dataset.side = 'left';
toggle.style.left = '0';
toggle.style.right = 'auto';

// Update sidebar position
const sidebar = document.getElementById('inhouse-kanban-sidebar');
sidebar.style.left = '60px';
sidebar.style.right = 'auto';
sidebar.style.transform = 'translateX(-100%)';
```

## ✅ Complete Test Sequence

Run this in console to test everything:

```javascript
(async function testKanbanSidebar() {
    console.log('🧪 Testing InHouse Kanban Sidebar Toggle');
    console.log('═'.repeat(50));
    
    // 1. Check sidebar element
    const sidebar = document.getElementById('inhouse-kanban-sidebar');
    console.log('1️⃣ Sidebar element exists:', !!sidebar);
    if (!sidebar) {
        console.error('❌ Sidebar HTML not in DOM! Loading module...');
        await window.moduleLoader.loadModule('inhouse-kanban');
        await new Promise(r => setTimeout(r, 1000));
    }
    
    // 2. Check sidebar controller
    console.log('2️⃣ Sidebar controller exists:', !!window.inhouseKanbanSidebar);
    if (!window.inhouseKanbanSidebar) {
        console.error('❌ Controller not initialized! Initializing...');
        if (window.ModuleRegistry?.['inhouse-kanban']?.init) {
            await window.ModuleRegistry['inhouse-kanban'].init();
        }
    }
    
    // 3. Check toggle button
    const toggle = document.getElementById('inhouse-kanban-floating-toggle');
    console.log('3️⃣ Toggle button exists:', !!toggle);
    console.log('   Toggle side:', toggle?.dataset.side);
    console.log('   Toggle position:', {
        left: toggle?.style.left,
        right: toggle?.style.right,
        top: toggle?.style.top
    });
    
    // 4. Check CSS
    const sidebarElement = document.getElementById('inhouse-kanban-sidebar');
    if (sidebarElement) {
        const computedStyle = window.getComputedStyle(sidebarElement);
        console.log('4️⃣ Sidebar CSS:', {
            left: computedStyle.left,
            right: computedStyle.right,
            transform: computedStyle.transform,
            width: computedStyle.width
        });
    }
    
    // 5. Test opening
    console.log('5️⃣ Testing sidebar open...');
    if (window.inhouseKanbanSidebar) {
        window.inhouseKanbanSidebar.openSidebar();
        await new Promise(r => setTimeout(r, 500));
        const isActive = sidebarElement?.classList.contains('active');
        console.log('   Sidebar opened:', isActive);
        
        if (isActive) {
            console.log('✅ SUCCESS! Sidebar is visible');
        } else {
            console.log('❌ FAILED! Sidebar did not open');
        }
    } else {
        console.log('❌ Cannot test - controller not available');
    }
    
    console.log('═'.repeat(50));
})();
```

## 📊 Expected Console Output (Success)

```
🧪 Testing InHouse Kanban Sidebar Toggle
══════════════════════════════════════════════════
1️⃣ Sidebar element exists: true
2️⃣ Sidebar controller exists: true
3️⃣ Toggle button exists: true
   Toggle side: left
   Toggle position: {left: '0px', right: 'auto', top: '821.75px'}
4️⃣ Sidebar CSS: {left: '60px', right: 'auto', transform: 'matrix(1, 0, 0, 1, -480, 0)', width: '480px'}
5️⃣ Testing sidebar open...
✅ Kanban sidebar opened
   Sidebar opened: true
✅ SUCCESS! Sidebar is visible
══════════════════════════════════════════════════
```

## 🔧 Quick Fix Commands

### Force Toggle to Open Sidebar
```javascript
const toggle = document.getElementById('inhouse-kanban-floating-toggle');
toggle.addEventListener('click', function(e) {
    e.stopPropagation();
    e.preventDefault();
    console.log('🔵 Force opening sidebar...');
    window.inhouseKanbanSidebar?.openSidebar();
}, true);
```

### Manually Position Sidebar
```javascript
const sidebar = document.getElementById('inhouse-kanban-sidebar');
sidebar.style.position = 'fixed';
sidebar.style.top = '60px';
sidebar.style.left = '60px';
sidebar.style.right = 'auto';
sidebar.style.width = '480px';
sidebar.style.height = 'calc(100vh - 60px)';
sidebar.style.transform = 'translateX(-100%)';
sidebar.style.transition = 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
sidebar.style.zIndex = '9999';

// To open
sidebar.classList.add('active');
sidebar.style.transform = 'translateX(0)';
```

---

**Created:** November 29, 2025  
**Status:** Ready for testing
