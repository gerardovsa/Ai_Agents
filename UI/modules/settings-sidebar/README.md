# Settings Sidebar Module

**Location:** `UI/modules/settings-sidebar/`  
**Status:** ✅ Complete - Ready for Integration  
**Dependencies:** Font Awesome, prompt-sidebar CSS base styles

---

## 📁 Module Structure

```
UI/modules/settings-sidebar/
├── settings-sidebar.html    # HTML template (loaded dynamically)
├── settings-sidebar.css     # Module-specific styles
├── settings-sidebar.js      # Module logic and API
└── README.md               # This file
```

---

## 🚀 Integration Instructions

### Step 1: Load Module Files

Add to your main HTML file `<head>`:

```html
<!-- Settings Sidebar Module -->
<link rel="stylesheet" href="UI/modules/settings-sidebar/settings-sidebar.css">
```

Add before closing `</body>`:

```html
<!-- Settings Sidebar Module -->
<script src="UI/modules/settings-sidebar/settings-sidebar.js"></script>
<script>
    // Load settings sidebar HTML dynamically
    fetch('UI/modules/settings-sidebar/settings-sidebar.html')
        .then(response => response.text())
        .then(html => {
            document.body.insertAdjacentHTML('beforeend', html);
            console.log('[Settings] Sidebar HTML loaded');
        })
        .catch(error => console.error('[Settings] Failed to load sidebar HTML:', error));
</script>
```

### Step 2: Wire Up Settings Button

The settings button already exists in your HTML. The module automatically wires it up on load, but you can also manually trigger it:

```javascript
// Open settings sidebar
window.openSettingsSidebar();

// Close settings sidebar
window.closeSettingsSidebar();
```

---

## 🎯 Features

### Error Recovery Settings Tab
- ✅ Master enable/disable toggle
- ✅ Individual recovery type controls:
  - Tool Use Mismatch
  - Invalid Message Structure
  - Context Length Exceeded
  - Rate Limit Exceeded
  - Network Errors
- ✅ Max retry attempts (1-5)
- ✅ Show recovery notifications toggle
- ✅ Detailed logging toggle
- 📊 Recovery statistics panel

### Display Settings Tab
- Show thinking process toggle
- Show tool use details toggle
- Auto-scroll to bottom toggle

### Advanced Settings Tab
- Debug mode toggle
- Cache API responses toggle

---

## 💾 Data Storage

All settings are stored in `localStorage` under key: `aiAgentSettings`

**Default Settings:**
```javascript
{
    autoRecovery: {
        enabled: true,
        toolMismatch: true,
        invalidStructure: true,
        contextLength: true,
        rateLimit: true,
        network: true,
        maxRetries: 3,
        showNotifications: true,
        detailedLogging: true
    },
    display: {
        showThinking: true,
        showToolDetails: true,
        autoScroll: true
    },
    advanced: {
        debugMode: false,
        cacheResponses: true
    },
    statistics: {
        totalRecoveries: 0,
        successfulRecoveries: 0,
        failedRecoveries: 0,
        lastRecovery: null
    }
}
```

---

## 🔌 JavaScript API

### Global Functions

```javascript
// Settings Management
window.SettingsManager.load()           // Load all settings
window.SettingsManager.save(settings)   // Save all settings
window.SettingsManager.get('path')      // Get specific setting
window.SettingsManager.set('path', val) // Set specific setting

// UI Controls
window.openSettingsSidebar()            // Open sidebar
window.closeSettingsSidebar()           // Close sidebar
window.switchSettingsTab('recovery')    // Switch tabs

// Error Recovery Integration
window.isErrorRecoveryEnabled(type)     // Check if recovery enabled
window.getMaxRetryAttempts()            // Get max retry count
window.shouldShowRecoveryNotifications() // Check notification preference
window.isDetailedLoggingEnabled()       // Check logging preference

// Statistics
window.SettingsManager.recordRecovery(success) // Record recovery attempt
window.resetRecoveryStats()             // Reset statistics
window.resetAllSettings()               // Reset to defaults
```

### Usage Examples

**Check if error recovery is enabled:**
```javascript
const enabled = window.isErrorRecoveryEnabled('tool_use_mismatch');
if (!enabled) {
    console.log('Recovery disabled - skipping');
    return;
}
```

**Get user preferences:**
```javascript
const maxRetries = window.getMaxRetryAttempts();
const showNotifications = window.shouldShowRecoveryNotifications();
```

**Update settings programmatically:**
```javascript
// Disable all recovery
SettingsManager.set('autoRecovery.enabled', false);

// Disable specific type
SettingsManager.set('autoRecovery.toolMismatch', false);

// Change max retries
SettingsManager.set('autoRecovery.maxRetries', 5);
```

**Record recovery statistics:**
```javascript
// On successful recovery
SettingsManager.recordRecovery(true);

// On failed recovery
SettingsManager.recordRecovery(false);
```

---

## 🎨 Styling Notes

### CSS Variables Used
- `--bg-primary`: #0d1117
- `--bg-secondary`: #161b22
- `--bg-tertiary`: #21262d
- `--border-default`: #30363d
- `--text-primary`: #c9d1d9
- `--text-secondary`: #8b949e
- `--accent-primary`: #1f6feb

### Responsive Design
- Mobile-optimized (< 768px)
- Touch-friendly toggle switches
- Stacked layout on small screens

---

## 🧪 Testing

### Manual Testing Checklist

1. **Load Module**
   - [ ] CSS loads without errors
   - [ ] JS loads without errors
   - [ ] HTML loads dynamically
   - [ ] No console errors

2. **Open Sidebar**
   - [ ] Click settings button (⚙️)
   - [ ] Sidebar slides in from right
   - [ ] Settings load from localStorage
   - [ ] Default values displayed correctly

3. **Test Toggles**
   - [ ] Master recovery toggle works
   - [ ] Sub-options disable when master OFF
   - [ ] Individual toggles save correctly
   - [ ] Settings persist after reload

4. **Test Statistics**
   - [ ] Statistics display correctly
   - [ ] Reset button clears stats
   - [ ] Timestamps format correctly

5. **Test Integration**
   - [ ] Error recovery checks settings
   - [ ] Disabled recovery skips gracefully
   - [ ] Notifications respect preferences
   - [ ] Logging respects preferences

### Console Testing

```javascript
// Open sidebar
window.openSettingsSidebar();

// Check current settings
console.log(SettingsManager.load());

// Toggle recovery off
SettingsManager.set('autoRecovery.enabled', false);

// Verify
console.log(window.isErrorRecoveryEnabled('tool_use_mismatch')); // false

// Record test recovery
SettingsManager.recordRecovery(true);

// Check stats
console.log(SettingsManager.get('statistics'));
```

---

## 🐛 Troubleshooting

### Issue: Settings sidebar not appearing
**Solution:** Check that HTML loaded successfully, verify CSS link

### Issue: Settings not saving
**Solution:** Check browser localStorage quota, clear localStorage

### Issue: Toggles not working
**Solution:** Hard refresh (Ctrl+Shift+R), verify JS loaded

### Issue: Statistics not updating
**Solution:** Check console for errors, verify DOM elements exist

---

## 📊 Browser Compatibility

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Opera 76+

---

## 🔒 Security Notes

- All data stored in browser localStorage (client-side)
- No sensitive data transmitted
- XSS-safe (no innerHTML with user input)
- CSRF-safe (no server-side mutations)

---

## 📈 Future Enhancements

- [ ] Export/Import settings (JSON file)
- [ ] Cloud sync (save to server)
- [ ] Per-agent settings (different settings per agent)
- [ ] Recovery history log (view past attempts)
- [ ] Auto-disable after X failures (circuit breaker)
- [ ] Recovery templates (predefined strategies)
- [ ] Keyboard shortcuts (Ctrl+, to open)

---

## 📝 Changelog

### v1.0.0 (November 23, 2025)
- ✅ Initial release
- ✅ Error recovery settings
- ✅ Display preferences
- ✅ Advanced configuration
- ✅ Statistics tracking
- ✅ localStorage persistence
- ✅ Integration with error recovery system

---

**Module Owner:** AI Infrastructure Team  
**Last Updated:** November 23, 2025  
**Status:** Production Ready 🚀
