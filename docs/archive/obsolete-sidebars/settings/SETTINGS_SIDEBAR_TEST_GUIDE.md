# Settings Sidebar Module - Testing & Debugging Guide

**Date:** November 23, 2025  
**Purpose:** Quick testing and CSS extraction guide

---

## 🚀 Quick Start - Testing the Module

### **Option 1: Standalone Test Page (Recommended)**

**File:** `test_settings_sidebar_module.html`

**Steps:**
1. Open file in browser:
   ```
   file:///c:/Users/gpoli/GIT/AI_agents/test_settings_sidebar_module.html
   ```

2. Click **"Test Module Load"** button

3. Click the **purple settings icon** (top-right corner)

4. Test all 4 tabs:
   - Recovery (default)
   - Error Tracking (NEW)
   - Display
   - Advanced

5. **CSS Output:**
   - Automatically output to browser console after 2 seconds
   - Or click **"Output CSS to Console"** button
   - Open DevTools (F12) to copy CSS

---

### **Option 2: Main Application Integration**

**Steps:**
1. Add to your main HTML (e.g., `business-ai-platform-v2.html`):
   ```html
   <!-- Settings Button Integration (Enhanced Debugging) -->
   <script src="UI/external/modules/settings-sidebar/settings-button-integration.js"></script>
   ```

2. Open DevTools (F12)

3. Look for purple console messages:
   ```
   [Settings Button] ✅ Module integration script loaded
   [Settings Button] ✅ Settings button found
   [Settings Button] ✅ Module initialized
   ```

4. CSS automatically output to console after 3 seconds

---

## 📋 Console Output Features

### **Automatic on Load:**

1. **Module Status Check** (immediately)
   ```
   [Settings Button] Checking Module Availability
   ✅ SettingsSidebarModule class found
   ✅ ModuleRegistry exists
   ✅ Module registered
   ✅ Module initialized
   ```

2. **CSS Code Output** (after 2-3 seconds)
   ```
   ═══════════════════════════════════════════════════
       Settings Sidebar Module - CSS Code
   ═══════════════════════════════════════════════════
   
   [Full CSS code here - ready to copy/paste]
   
   ✅ CSS loaded successfully - Total: 18,542 characters
   ```

3. **Debug Information** (after 3 seconds)
   ```
   ═══════════════════════════════════════════════════
       Settings Sidebar - Debug Information
   ═══════════════════════════════════════════════════
   
   [Table with module state]
   [Module instance object]
   [Button element]
   [Container element]
   ```

---

## 🎨 Extracting CSS

### **Method 1: Automatic Console Output**

1. Open any page with Settings Sidebar loaded
2. Open DevTools (F12)
3. Wait 2-3 seconds
4. Look for purple header:
   ```
   Settings Sidebar Module - CSS Code
   ```
5. Select all CSS text
6. Right-click → Copy
7. Paste into your CSS file

### **Method 2: Manual Trigger**

1. Open DevTools (F12)
2. Run in console:
   ```javascript
   SettingsButtonManager.outputCSSToConsole()
   ```
3. CSS appears in console
4. Copy/paste

### **Method 3: Test Page Button**

1. Open `test_settings_sidebar_module.html`
2. Click **"Output CSS to Console"** button
3. Open DevTools (F12)
4. Copy CSS from console

### **Method 4: Direct File Access**

**File Location:**
```
UI/external/modules/settings-sidebar/settings-sidebar.css
```

Open file and copy directly (but console output has nice formatting!)

---

## 🐛 Debugging

### **Check Module Load Status**

**In Console:**
```javascript
// Check if module exists
window.settingsModule

// Get module state
SettingsButtonManager.getModuleState()

// Full debug info
SettingsButtonManager.debugInfo()
```

**Expected Output:**
```javascript
{
  buttonFound: true,
  buttonElement: button#settings-button,
  moduleInstance: true,
  moduleInitialized: true,
  containerExists: true,
  registryExists: true,
  moduleRegistered: true,
  globalInstanceExists: true,
  managerExists: true
}
```

### **Common Issues**

#### **Issue: Module Not Loading**

**Symptoms:**
```
❌ SettingsSidebarModule class NOT found
```

**Solution:**
1. Check script is included:
   ```html
   <script src="UI/external/modules/settings-sidebar/settings-sidebar.js"></script>
   ```
2. Check path is correct
3. Check browser console for 404 errors

#### **Issue: Button Not Found**

**Symptoms:**
```
⚠️ Settings button not found. Creating fallback button...
```

**Solution:**
- Fallback button auto-created (purple circle, top-right)
- Add proper button to your HTML:
   ```html
   <button id="settings-button" data-module-action="settings">
       <i class="fas fa-cog"></i>
   </button>
   ```

#### **Issue: CSS Not Appearing**

**Symptoms:**
- Module loads but no styling

**Solution:**
1. Check CSS file is included:
   ```html
   <link rel="stylesheet" href="UI/external/modules/settings-sidebar/settings-sidebar.css">
   ```
2. Or copy CSS from console and add inline
3. Check browser DevTools for CSS load errors

#### **Issue: Module Container Not Found**

**Symptoms:**
```
⚠️ Module container NOT found (expected #tab-settings-sidebar)
```

**Solution:**
- Module container auto-created by BaseModule
- Or add manually:
   ```html
   <div id="tab-settings-sidebar"></div>
   ```

---

## 🧪 Testing Features

### **Test Error Recovery**

1. Open Settings Sidebar
2. Go to **Recovery** tab
3. Check statistics dashboard
4. Toggle recovery types
5. Change max retries
6. Click **"Save Settings"**

### **Test Error Tracking** (NEW)

1. Go to **Tracking** tab
2. Click **"Simulate Error Recovery"** (in test page)
3. See error type statistics
4. View recovery timeline
5. Check error logs table
6. View effectiveness metrics

**Or manually in console:**
```javascript
// Simulate errors
window.settingsModule.logError(
    'tool_use_mismatch',
    'Test error message',
    true,  // recovered
    2,     // attempt number
    'test_thread_123'
);

// Record recovery
window.settingsModule.recordRecovery('tool_use_mismatch', true);

// Refresh tracking tab
window.settingsModule.switchSubTab('tracking');
```

### **Test Display Settings**

1. Go to **Display** tab
2. Toggle settings
3. Click **"Save Settings"**
4. Settings persist in localStorage

### **Test Advanced Settings**

1. Go to **Advanced** tab
2. Test export settings:
   ```javascript
   window.settingsModule.exportSettings()
   ```
3. Test import (upload JSON file)
4. Test reset (with confirmation)

---

## 📊 Monitoring Module Health

### **Check Settings Storage**

**In Console:**
```javascript
// View current settings
const settings = localStorage.getItem('aiAgentSettings');
console.log(JSON.parse(settings));

// View error logs
const logs = localStorage.getItem('aiAgentErrorLogs');
console.log(JSON.parse(logs));
```

### **Check Module Initialization**

**In Console:**
```javascript
// Check initialization status
console.log('Initialized:', window.settingsModule.initialized);

// Check active tab
console.log('Active tab:', window.settingsModule.activeSubTab);

// Check sub-tabs
console.log('Sub-tabs:', window.settingsModule.subTabs);
```

### **Monitor Button Clicks**

All button clicks are logged to console with purple `[Settings Button]` prefix:

```
[Settings Button] Button click event triggered
[Settings Button] Using ModuleManager.switchToModule()
[Settings Button] ✅ Module switched via ModuleManager
```

---

## 🎯 Production Integration Checklist

### **1. Add Module Script**
```html
<script src="UI/js/module-base.js"></script>
<script src="UI/external/modules/settings-sidebar/settings-sidebar.js"></script>
```

### **2. Add Module Styles**
```html
<link rel="stylesheet" href="UI/external/modules/settings-sidebar/settings-sidebar.css">
```

### **3. Add Integration Script (Optional - for debugging)**
```html
<script src="UI/external/modules/settings-sidebar/settings-button-integration.js"></script>
```

### **4. Add Settings Button**
```html
<button id="settings-button" data-module-action="settings" title="Settings">
    <i class="fas fa-cog"></i>
</button>
```

### **5. Verify Module Registration**

In console after page load:
```javascript
console.log('Module registered:', !!window.ModuleRegistry['settings-sidebar']);
console.log('Module instance:', !!window.settingsModule);
```

### **6. Test All Features**
- [ ] Settings button opens sidebar
- [ ] All 4 tabs render
- [ ] Settings persist
- [ ] Error tracking works
- [ ] Statistics update
- [ ] Export/import works

---

## 🔧 Advanced Debugging

### **Enable Verbose Logging**

**In Console:**
```javascript
// Enable detailed logging
window.settingsModule.settingsManager.update('advanced.debugMode', true);

// Test a recovery
window.settingsModule.isErrorRecoveryEnabled('tool_use_mismatch');
// Will log detailed debug info
```

### **Trace Button Click Flow**

**Set breakpoint in DevTools:**
1. Open Sources tab
2. Find: `settings-button-integration.js`
3. Set breakpoint in `handleButtonClick()`
4. Click settings button
5. Step through code

### **Monitor localStorage Changes**

**In Console:**
```javascript
// Watch localStorage changes
const originalSetItem = localStorage.setItem;
localStorage.setItem = function(key, value) {
    console.log('localStorage.setItem:', key, value);
    originalSetItem.apply(this, arguments);
};
```

---

## 📝 CSS Customization

### **Module Colors**

**In CSS:**
```css
:root {
    --module-settings-primary: #8b5cf6;   /* Purple */
    --module-settings-secondary: #7c3aed; /* Dark Purple */
    --module-settings-hover: #6d28d9;     /* Darker Purple */
}
```

**Change to your brand colors:**
```css
:root {
    --module-settings-primary: #your-color;
    --module-settings-secondary: #your-darker-color;
    --module-settings-hover: #your-darkest-color;
}
```

### **Button Styling**

**Change settings button appearance:**
```css
#settings-button {
    background: #your-color;
    border-color: #your-border-color;
    /* ... other styles */
}
```

---

## 🎉 Success Criteria

### **Module Loads Successfully:**
✅ Console shows:
```
[Settings Sidebar] Module loading...
✅ Settings Sidebar module registered
✅ Settings Sidebar module ready
```

### **CSS Loads Successfully:**
✅ Console shows:
```
Settings Sidebar Module - CSS Code
✅ CSS loaded successfully - Total: 18,542 characters
```

### **Button Works:**
✅ Clicking button opens sidebar
✅ All tabs render with content
✅ Settings persist after save

### **Error Tracking Works:**
✅ Error logs appear in tracking tab
✅ Statistics update correctly
✅ Timeline shows recent errors
✅ Effectiveness metrics calculate

---

## 🆘 Support

### **If Module Won't Load:**

1. Check browser console for errors
2. Run: `SettingsButtonManager.debugInfo()`
3. Verify file paths are correct
4. Check network tab in DevTools for 404s

### **If CSS Missing:**

1. Run: `SettingsButtonManager.outputCSSToConsole()`
2. Copy CSS from console
3. Add to main stylesheet
4. Or include via `<link>` tag

### **If Button Not Working:**

1. Check: `SettingsButtonManager.getModuleState()`
2. Look for false values
3. Check console for click event logs
4. Verify module is initialized

---

## 📚 Related Files

- **Module JS:** `UI/external/modules/settings-sidebar/settings-sidebar.js`
- **Module CSS:** `UI/external/modules/settings-sidebar/settings-sidebar.css`
- **Manifest:** `UI/external/modules/settings-sidebar/manifest.json`
- **Integration Script:** `UI/external/modules/settings-sidebar/settings-button-integration.js`
- **Test Page:** `test_settings_sidebar_module.html`
- **Documentation:** `UI/external/modules/settings-sidebar/README.md`

---

## ✅ Quick Test Checklist

**5-Minute Smoke Test:**

1. [ ] Open test page or main app
2. [ ] Check console for purple success messages
3. [ ] Wait for CSS output (2-3 seconds)
4. [ ] Copy CSS from console
5. [ ] Click settings button (purple circle or icon)
6. [ ] Verify sidebar opens
7. [ ] Click all 4 tabs
8. [ ] Simulate error recovery (test page)
9. [ ] Check tracking tab shows data
10. [ ] Export settings (test)

**If all pass:** ✅ Module is production ready!

---

**End of Testing Guide**

**For full documentation, see:** `UI/external/modules/settings-sidebar/README.md`
