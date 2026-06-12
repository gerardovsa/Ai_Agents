# 🔥 FORCE REFRESH - Clear Service Worker Cache

## The Problem

Your browser has a **Service Worker** caching the OLD JavaScript files. Even after hard refresh (Ctrl+Shift+R), the service worker serves cached versions of:
- `transcription-sidebar.js` (with old timer bugs)
- `business-ai-platform-v2.html` (with old STTModule initialization)

This is why you're STILL seeing:
- Whisper ffmpeg errors
- Timer continuing after stop
- Audio chunks being sent to backend

---

## Solution: Clear Service Worker Cache

### Step 1: Open Browser Console

1. Press `F12` to open DevTools
2. Go to **Console** tab

### Step 2: Run These Commands

```javascript
// 1. Clear service worker cache
await window.clearServiceWorkerCache();

// 2. Unregister service worker
navigator.serviceWorker.getRegistrations().then(registrations => {
    registrations.forEach(registration => {
        registration.unregister();
        console.log('Service worker unregistered');
    });
});

// 3. Clear all caches
caches.keys().then(names => {
    names.forEach(name => {
        caches.delete(name);
        console.log('Deleted cache:', name);
    });
});
```

### Step 3: Hard Refresh

After running the above commands:
1. Close DevTools
2. Press `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
3. **OR** Right-click refresh button → "Empty Cache and Hard Reload"

---

## Verification

After refresh, check console for these NEW log messages:

### ✅ GOOD (New Code Loaded):
```
[TRANSCRIPTION] ❌ STTModule DISABLED - Using SharedTranscriptionState only
[TRANSCRIPTION] Do NOT initialize STTModule - causes audio-capture errors
[SHARED STATE] Browser recognition started
```

### ❌ BAD (Old Code Still Cached):
```
🎤 Starting recording...  ← STTModule still initializing
[SHARED STATE] Recognition error: audio-capture
📦 Audio chunk received: 0 bytes
📤 Sending chunk to Whisper...
```

---

## If Still Not Working

### Nuclear Option: Chrome Incognito Mode

1. Close ALL browser windows
2. Open Chrome in Incognito/Private mode (`Ctrl+Shift+N`)
3. Navigate to `http://localhost:5001`
4. Test transcription

**Why this works:** Incognito mode ignores all caches and service workers.

---

## Alternative: Clear All Site Data

1. Open Chrome DevTools (`F12`)
2. Go to **Application** tab
3. In left sidebar, click **Storage**
4. Click **Clear site data** button
5. Confirm
6. Hard refresh (`Ctrl+Shift+R`)

---

## Root Cause

Service workers are designed to cache files for offline access. This is great for production, but during development it causes:
- Old JavaScript files being served
- Bug fixes not appearing
- Confusion about what code is actually running

Your transcription fixes ARE in the files, but the browser is serving **cached old versions**.

---

## After Clearing Cache

Once cache is cleared, you should see:
1. **NO Whisper errors** - No ffmpeg output in console
2. **NO audio-capture errors** - STTModule disabled
3. **Timer stops correctly** - clearInterval working
4. **Text appears in real-time** - Browser STT streaming

---

## Pro Tip: Disable Cache During Development

To prevent this in future:

1. Open DevTools (`F12`)
2. Go to **Network** tab
3. Check **Disable cache** checkbox
4. Keep DevTools open while developing

This forces browser to always fetch fresh files.

---

**Last Updated:** November 27, 2024  
**Issue:** Service Worker caching old JavaScript  
**Solution:** Clear cache + unregister service worker  
**Status:** Ready to test
