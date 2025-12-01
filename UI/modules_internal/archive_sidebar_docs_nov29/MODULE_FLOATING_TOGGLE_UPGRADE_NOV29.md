# Module Floating Toggle - Sidebar Framework Integration (November 29, 2025)

## 🎯 Objective

Upgrade `module-floating-toggle` buttons (like InHouse Kanban) to match the new Universal Sidebar Framework behavior, providing consistent UX across all module toggles.

---

## ✅ Changes Implemented

### 1. **Styling Update - Match Synergy Toggle**

**Before (Old Style):**
- Rectangle shape (36px × 64px)
- Solid background color
- Edge-mounted (0px from left/right)
- Custom padding/shadow

**After (New Style):**
- **Circular shape** (48px × 48px) - matches Synergy toggle
- **Background:** `var(--bg-secondary)` with border
- **Hover:** Blue border + color (`var(--accent-primary)`)
- **Active:** Blue background with glow effect
- **Positioned:** 80px from edges (60px sidebar + 20px spacing)

**CSS Changes:**
```css
.module-floating-toggle {
    position: fixed;
    width: 48px;              /* ← Circular */
    height: 48px;             /* ← Circular */
    border-radius: 50%;       /* ← Circular */
    background: var(--bg-secondary);
    border: 2px solid var(--border-default);
    color: var(--text-secondary);
    cursor: move;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}

.module-floating-toggle:hover {
    background: var(--bg-tertiary);
    border-color: var(--accent-primary);  /* ← Blue border */
    color: var(--accent-primary);         /* ← Blue icon */
    transform: scale(1.05);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.module-floating-toggle.active {
    background: var(--accent-primary);    /* ← Blue background */
    border-color: var(--accent-primary);
    color: white;
    box-shadow: 0 0 20px rgba(79, 108, 255, 0.4);  /* ← Blue glow */
}
```

---

### 2. **Dynamic Side Detection**

**New Feature:** Toggle automatically detects LEFT vs RIGHT based on screen position when dragged.

**How It Works:**
```javascript
// When user drags and releases toggle
const windowWidth = window.innerWidth;
const toggleRect = toggle.getBoundingClientRect();
const toggleCenterX = toggleRect.left + (toggleRect.width / 2);

// Detect side: left half = left, right half = right
const detectedSide = toggleCenterX < (windowWidth / 2) ? 'left' : 'right';

if (detectedSide !== currentSide) {
    currentSide = detectedSide;
    localStorage.setItem(`${moduleId}-toggle-side`, currentSide);
    positionToggle();  // Update toggle and sidebar
}
```

**User Experience:**
1. User drags toggle from left to right side of screen
2. System detects: "Toggle crossed center line!"
3. Automatically switches to right side
4. Sidebar reconfigures to open from right
5. Preference saved - persists across reloads

---

### 3. **60px Offset Positioning**

**Problem:** Old toggles were flush against edges (0px) - overlapped main sidebar menu

**Solution:** Toggles now positioned **80px from edges**

**Left Side:**
```javascript
toggle.style.left = '80px';   // 60px main sidebar + 20px spacing
toggle.style.right = 'auto';
```

**Right Side:**
```javascript
toggle.style.right = '80px';  // 60px spacing + 20px margin
toggle.style.left = 'auto';
```

**Sidebar Positioning:**
```javascript
// Left sidebar
sidebar.style.left = '60px';  // Clear of main sidebar menu
sidebar.style.transform = 'translateX(calc(-100% - 60px))';  // Hidden

// Right sidebar  
sidebar.style.right = '60px';  // 60px from right edge
sidebar.style.transform = 'translateX(calc(100% + 60px))';  // Hidden
```

---

### 4. **SidebarManager Integration**

**New:** Module floating toggles now integrate with Universal Sidebar Framework

**When toggle is dragged:**
```javascript
// Update SidebarManager if module is registered
if (window.SidebarManager && window.SidebarManager.sidebars.has(`${moduleId}-sidebar`)) {
    const sidebarConfig = window.SidebarManager.sidebars.get(`${moduleId}-sidebar`);
    sidebarConfig.side = currentSide;
    const sidebarElement = sidebarConfig.element;
    if (sidebarElement) {
        window.SidebarManager.applySidebarStyles(sidebarElement, sidebarConfig);
    }
}
```

**Benefits:**
- Consistent behavior across all sidebars
- Centralized state management
- Automatic styling updates
- Single source of truth for sidebar positioning

---

## 📐 Visual Comparison

### Before (Old Design):

```
┌──────┬────────────────────────────────────────────────────┐
│ 60px │                                                    │
│ Main │█  ← Rectangle toggle (36x64px)                     │
│ Side │█     Flush against edge (0px)                      │
│ bar  │█     Custom styling                                │
│      │█                                                    │
└──────┴────────────────────────────────────────────────────┘
       ↑ Toggle overlaps main sidebar
```

### After (New Design):

```
┌──────┬────────────────────────────────────────────────────┐
│ 60px │                                                    │
│ Main │    ╔═══╗  ← Circular toggle (48x48px)             │
│ Side │    ║ ● ║     80px from edge                        │
│ bar  │    ╚═══╝     Matches Synergy toggle                │
│      │    ↑                                                │
│      │   80px spacing (60px + 20px)                       │
└──────┴────────────────────────────────────────────────────┘
       ↑ Clear of main sidebar menu
```

---

## 🎨 Animation Behavior

### Left Side Sidebar

**Closed State:**
```
Toggle at 80px from left
Sidebar hidden: transform: translateX(calc(-100% - 60px))
```

**Opening:**
```
Sidebar slides IN from left wall → towards right
Animation: cubic-bezier(0.4, 0, 0.2, 1)
Duration: 300ms
```

**Open State:**
```
Sidebar visible at 60px from left edge
Transform: translateX(0)
Toggle shows blue glow (active state)
```

### Right Side Sidebar

**Closed State:**
```
Toggle at 80px from right
Sidebar hidden: transform: translateX(calc(100% + 60px))
```

**Opening:**
```
Sidebar slides IN from right wall → towards left
Animation: cubic-bezier(0.4, 0, 0.2, 1)
Duration: 300ms
```

**Open State:**
```
Sidebar visible at 60px from right edge
Transform: translateX(0)
Toggle shows blue glow (active state)
```

---

## 🔄 Interaction Patterns

### Single Click
- **Action:** Opens/closes sidebar
- **Behavior:** Sidebar slides in from appropriate wall
- **Visual:** Toggle glows blue when sidebar open

### Double Click (within 400ms)
- **Action:** Switches toggle to opposite side
- **Behavior:** Toggle moves, sidebar reconfigures
- **Persistence:** Side preference saved to localStorage

### Drag Across Screen
- **Action:** User drags toggle anywhere
- **Detection:** System detects left vs right half
- **Auto-Update:** Sidebar automatically reconfigures
- **Feedback:** Console logs side change

---

## 📋 Affected Modules

All modules using `floating_toggle: true` in manifest:

1. **inhouse-kanban** ✅
   - Production Workflow toggle
   - Color: `#6B7280` (gray)
   - Opens sidebar on left/right

2. **Future modules** ✅
   - Any module with `floating_toggle: true`
   - Automatically inherits new behavior
   - Consistent UX across platform

---

## 🧪 Testing Checklist

- [x] Toggle has circular shape (48px × 48px)
- [x] Toggle positioned 80px from edges (not 0px)
- [x] Hover shows blue border and icon
- [x] Active shows blue background with glow
- [x] Drag to left half → sidebar opens from left
- [x] Drag to right half → sidebar opens from right
- [x] Double-click switches sides
- [x] Sidebar positioned 60px from edges
- [x] Sidebar slides in from wall smoothly
- [x] Position persists across page reloads
- [x] SidebarManager integration works
- [x] No overlap with main sidebar menu

---

## 🔧 Files Modified

### 1. `UI/business-ai-platform-v2.html`
**Lines 2969-3018:** Updated `.module-floating-toggle` CSS

**Changes:**
- Circular shape (50% border-radius)
- Synergy-matching colors
- 48px × 48px dimensions
- Hover/active states with blue glow

### 2. `UI/modules/module_loader.js`
**Lines 450-600:** Updated `initializeFloatingToggle()` method

**Changes:**
- Added dynamic side detection on drag
- Updated toggle positioning (80px from edges)
- Updated sidebar positioning (60px offsets)
- SidebarManager integration
- Improved transform values for animations

---

## 💡 Developer Notes

### Manifest Configuration

To use the new floating toggle system:

```json
{
  "id": "my-module",
  "name": "My Module",
  "floating_toggle": true,
  "floating_toggle_position": "left",
  "floating_toggle_default_top": 280,
  "sidebar": {
    "enabled": true,
    "position": "left",
    "width": 450
  }
}
```

### JavaScript Controller

Toggle state management:

```javascript
// Check which side toggle is on
const currentSide = localStorage.getItem('my-module-toggle-side') || 'left';

// Listen for side changes
window.addEventListener('storage', (e) => {
    if (e.key === 'my-module-toggle-side') {
        console.log('Toggle moved to:', e.newValue);
        // Update your module's UI accordingly
    }
});
```

---

## 🚀 Benefits

### For Users:
- ✅ Consistent toggle appearance across all modules
- ✅ Intuitive drag-to-reposition behavior
- ✅ Automatic side detection (no manual switching)
- ✅ Sidebars never overlap main UI elements
- ✅ Smooth, professional animations

### For Developers:
- ✅ No custom styling needed per module
- ✅ Automatic integration with SidebarManager
- ✅ Simple manifest configuration
- ✅ Consistent behavior without extra code
- ✅ State management handled by framework

---

## 📚 Related Documentation

- **SIDEBAR_FRAMEWORK_GUIDE.md** - Main framework documentation
- **SIDEBAR_TOGGLE_IMPROVEMENTS_NOV29.md** - Sidebar framework upgrade details
- **SIDEBAR_VISUAL_GUIDE.md** - Visual diagrams and examples
- **MODULE_SYSTEM_ARCHITECTURE_COMPLETE.md** - Module system overview

---

## 🎯 Migration Guide

### From Old Floating Toggle to New

**Old Code (Remove):**
```css
.module-floating-toggle {
    width: 36px;
    height: 64px;
    border-radius: 12px 0 0 12px;  /* Asymmetric */
}
```

**New Code (Already Applied):**
```css
.module-floating-toggle {
    width: 48px;
    height: 48px;
    border-radius: 50%;  /* Circular */
}
```

**No changes needed in module code** - framework handles everything!

---

## ⚡ Performance Notes

- **CSS transitions:** 200ms (faster than before)
- **Drag detection:** Debounced for smooth performance
- **localStorage:** Only writes on position/side change
- **SidebarManager:** Lazy integration (only if available)
- **Memory:** No memory leaks (event listeners properly managed)

---

**Last Updated:** November 29, 2025  
**Version:** 2.0  
**Status:** ✅ Production Ready  
**Breaking Changes:** None (backward compatible with visual improvements)
