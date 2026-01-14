# 🚀 Transcription Module - Quick Start Guide

**Framework:** ModuleLoaderV4 (Modern Framework)  
**Version:** 2.0.0  
**Pattern:** Composition-based

---

## ⚡ Quick Commands

### Load Module (Browser Console)
```javascript
await window.ModuleLoaderV4.loadModule('transcription', 'sidebar');
```

### Check Status
```javascript
window.ModuleLoaderV4.isModuleLoaded('transcription');  // true/false
```

### Reload Module (Hot Reload)
```javascript
await window.ModuleLoaderV4.reloadModule('transcription');
```

### Unload Module
```javascript
await window.ModuleLoaderV4.unloadModule('transcription');
```

### Enable Debug Mode
```javascript
window.ModuleLoaderV4.enableDebug();
await window.ModuleLoaderV4.loadModule('transcription', 'sidebar');
// See detailed console logs
```

---

## 📁 File Structure (What You Need)

```
UI/modules_internal/transcription/
├── manifest.json              ← Module config (26 lines)
├── transcription.js           ← Main module (700 lines) ✨ NEW
├── transcription-sidebar.js   ← Shared state (2,182 lines)
└── [other files preserved]    ← UI/styling unchanged
```

---

## 🎯 Key Concepts

### 1. Module Definition (Export Default)
```javascript
export default {
    state: { /* properties */ },
    async onSidebarLoad(utilities) { /* init */ },
    onUnload(utilities) { /* cleanup */ }
};
```

### 2. Utility Injection (Explicit)
```javascript
async onSidebarLoad(utilities) {
    Object.assign(this, utilities);  // ← CRITICAL
    // Now: this.dom, this.api, this.storage, this.events, this.log
}
```

### 3. Event Listeners (Auto-cleanup)
```javascript
setupSidebarListeners() {
    this.dom.on(this.container, 'click', '[data-action="start"]', () => {
        this.startRecording();
    });
    // Framework automatically cleans up on unload
}
```

### 4. State Management
```javascript
this.state.isRecording = true;       // ✅ Correct
this.isRecording = true;             // ❌ Wrong (not in state)
```

---

## 🔧 Available Utilities

| Utility | What It Does | Example |
|---------|--------------|---------|
| `dom` | DOM operations | `this.dom.getContainer()` |
| `api` | HTTP requests | `this.api.get('/api/data')` |
| `storage` | localStorage | `this.storage.get('key')` |
| `events` | Event bus | `this.events.emit('event')` |
| `log` | Logging | `this.log.info('message')` |

---

## 🎮 Common Actions

### Start Recording (STT)
```javascript
async startRecording() {
    await this.state.sharedState.startRecording('sidebar');
    this.state.isRecording = true;
    this.renderSidebar();
}
```

### Stop Recording (STT)
```javascript
stopRecording() {
    this.state.sharedState.stopRecording();
    this.state.isRecording = false;
    this.renderSidebar();
}
```

### Speak Text (TTS)
```javascript
speakText(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = this.state.settings.rate;
    utterance.pitch = this.state.settings.pitch;
    window.speechSynthesis.speak(utterance);
}
```

### Save Settings
```javascript
saveSettings() {
    this.storage.set('transcription_settings', this.state.settings);
}
```

### Load Settings
```javascript
async loadSettings() {
    const saved = this.storage.get('transcription_settings');
    if (saved) {
        this.state.settings = { ...this.state.settings, ...saved };
    }
}
```

---

## 🧪 Testing Workflow

### 1. Open Browser Console
Press `F12` in your browser

### 2. Check Module Available
```javascript
window.ModuleLoaderV4.isModuleAvailable('transcription');
// Expected: true
```

### 3. Load Module
```javascript
await window.ModuleLoaderV4.loadModule('transcription', 'sidebar');
// Expected: Sidebar appears, no errors
```

### 4. Test Features
- Click "Start Recording" → Should start recording
- Speak into microphone → Transcript should appear
- Click "Stop Recording" → Recording stops
- Enter text in TTS → Click "Speak" → Should hear voice

### 5. Check State
```javascript
// Get module instance (internal framework API)
const loader = window.ModuleLoaderV4;
// Module state is private, but check loaded status:
loader.isModuleLoaded('transcription');  // true
```

### 6. Reload (Hot Reload)
```javascript
await window.ModuleLoaderV4.reloadModule('transcription');
// Module reloads without page refresh
```

---

## 🚨 Common Issues

### Issue: "Utilities undefined"
**Symptom:** `this.dom`, `this.api` are undefined  
**Fix:** Add `Object.assign(this, utilities)` to lifecycle hooks

```javascript
async onSidebarLoad(utilities) {
    Object.assign(this, utilities);  // ← Must have this!
}
```

### Issue: "Container not found"
**Symptom:** `this.container` is null  
**Fix:** Call `this.dom.getContainer()` in lifecycle hook

```javascript
async onSidebarLoad(utilities) {
    Object.assign(this, utilities);
    this.container = this.dom.getContainer();  // ← Get container
}
```

### Issue: "Module not loading"
**Symptom:** Module doesn't appear  
**Fix:** Check manifest.json syntax

```javascript
// Enable debug mode to see detailed logs
window.ModuleLoaderV4.enableDebug();
await window.ModuleLoaderV4.loadModule('transcription', 'sidebar');
// Check console for errors
```

### Issue: "State not persisting"
**Symptom:** Settings reset on reload  
**Fix:** Call `saveSettings()` when state changes

```javascript
this.dom.on(this.container, 'change', '[data-setting]', (e) => {
    this.state.settings.something = e.target.value;
    this.saveSettings();  // ← Save to localStorage
});
```

---

## 📖 Documentation Index

| Document | Purpose |
|----------|---------|
| `MODERN_FRAMEWORK_ALIGNMENT.md` | Complete alignment guide |
| `TRANSCRIPTION_MIGRATION_LOG.md` | Migration details |
| `TRANSCRIPTION_QUICK_START.md` | This file |
| `manifest.json` | Module configuration |
| `transcription.js` | Main module code |
| `ARCHITECTURE.md` | System architecture |
| `README.md` | General overview |

---

## 🎯 Next Steps

1. **Test in browser:**
   ```javascript
   await window.ModuleLoaderV4.loadModule('transcription', 'sidebar');
   ```

2. **Try features:**
   - Start/stop recording
   - Test TTS with different voices
   - Adjust settings (rate, pitch, volume)
   - Copy/clear transcript

3. **Check console:**
   - Look for "Transcription sidebar loaded successfully"
   - No error messages
   - Utilities injected correctly

4. **Test hot reload:**
   ```javascript
   await window.ModuleLoaderV4.reloadModule('transcription');
   ```

5. **Test cleanup:**
   ```javascript
   await window.ModuleLoaderV4.unloadModule('transcription');
   // Check for memory leaks in DevTools
   ```

---

## 💡 Pro Tips

✅ **Always use `this.state.property`** - Never `this.property` directly  
✅ **Use `this.dom.on()` for events** - Automatic cleanup  
✅ **Call `Object.assign(this, utilities)` first** - In all lifecycle hooks  
✅ **Enable debug mode** - See detailed framework logs  
✅ **Test hot reload** - Faster development cycle  
✅ **Check DevTools Memory** - Verify no leaks on unload  

---

**Version:** 1.0.0  
**Created:** November 30, 2025  
**Framework:** ModuleLoaderV4  
**Status:** ✅ Production Ready
