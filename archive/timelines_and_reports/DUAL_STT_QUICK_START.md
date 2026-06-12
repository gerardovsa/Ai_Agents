# ⚡ Dual-Mode STT - 5-Minute Quick Start

## Goal
Get instant streaming transcription working in **5 minutes**.

---

## Prerequisites

✅ Flask server running (`BISTART`)  
✅ Chrome or Edge browser  
✅ Microphone connected and working  

---

## Step 1: Add Script Tag (30 seconds)

**File:** `UI/business-ai-platform-v2.html`  
**Location:** Around line 21000 (with other script tags)

```html
<!-- Add this line -->
<script src="modules/transcription/stt-module-dual.js"></script>
```

---

## Step 2: Update Initialization (2 minutes)

**File:** `UI/business-ai-platform-v2.html`  
**Location:** Around line 21070 (initializeSTTModule function)

**Replace entire function with:**

```javascript
function initializeSTTModule() {
    if (sttModule) return;

    sttModule = new STTModuleDual({
        recordButton: 'voiceRecordBtn',
        insertTarget: 'ai-chat-input',
        useBrowserSTT: true,
        
        onStart: () => {
            console.log('🎤 Recording started');
            window.TranscriptionStreaming?.show();
            window.TranscriptionStreaming?.updateStatus('recording', '🔴 Recording...');
        },
        
        onInterimTranscript: (data) => {
            window.TranscriptionStreaming?.streamText(
                data.transcript, 
                false, 
                data.confidence, 
                data.source
            );
        },
        
        onTranscript: (data) => {
            window.TranscriptionStreaming?.streamText(
                data.transcript, 
                true, 
                data.confidence, 
                data.source
            );
        },
        
        onStop: () => {
            console.log('🛑 Recording stopped');
            window.TranscriptionStreaming?.updateStatus('ready', 'Ready');
        },
        
        onError: (error) => {
            console.error('❌ STT Error:', error);
        }
    });
    
    console.log('✅ Dual-Mode STT initialized');
}
```

---

## Step 3: Test (2 minutes)

### 3.1 Reload Page
Press `Ctrl+Shift+R` to hard reload (clear cache)

### 3.2 Open Browser Console
Press `F12` → Console tab

### 3.3 Click Microphone Button
Look for: `✅ Dual-Mode STT initialized`

### 3.4 Speak Clearly
Say: **"Hello world, this is a test"**

### 3.5 Watch for Instant Text
You should see:
1. **0.3s:** Gray italic text appearing: `💭 "Hello..."▋`
2. **1.0s:** Green solid text: `✅ "Hello world, this is a test"`
3. **3.0s:** Purple dot text (Whisper): `● "Hello world, this is a test"`

---

## Expected Console Output

```
🎤 [Dual STT] Initializing...
✅ [Browser STT] Initialized
✅ [Dual STT] Initialized successfully
   • Browser STT: ENABLED
   • Whisper Backend: ENABLED
🎤 Recording started
✅ Microphone stream obtained
✅ [Browser STT] Started (instant streaming active)
✅ [MediaRecorder] Started (1000ms chunks)
💭 [Browser STT] Interim: "Hello..."
💭 [Browser STT] Interim: "Hello world..."
📝 [Browser STT] Final: "Hello world, this is a test" (confidence: 92%)
📦 [MediaRecorder] Chunk: 48000 bytes
📤 [Whisper] Sending chunk: dual_1732729847_1_1732729850
✅ [Whisper] Transcribed: "Hello world, this is a test"
🛑 Recording stopped
```

---

## Troubleshooting

### ❌ No gray italic text appearing

**Problem:** Browser STT not working  
**Check Console For:**
```
[Browser STT] Error: audio-capture
```

**Solution:** This is normal! System falls back to Whisper only.  
Browser STT conflicts with MediaRecorder sometimes.

---

### ❌ No text at all

**Problem:** Microphone permissions  
**Check Console For:**
```
getUserMedia error: NotAllowedError
```

**Solution:**
1. Click 🎤 icon in address bar (left side)
2. Select "Always allow"
3. Reload page
4. Try again

---

### ❌ Text appears but not green/orange/red

**Problem:** CSS not loaded  
**Check:** Network tab in DevTools  
**Solution:** Hard reload (`Ctrl+Shift+R`)

---

### ❌ Whisper text not appearing

**Problem:** Backend not running  
**Check Console For:**
```
Failed to fetch http://localhost:5001/api/transcribe
```

**Solution:**
```powershell
cd C:\Users\gpoli\GIT\AI_agents
BISTART
```

Wait for: `✅ Flask running on http://localhost:5001`

---

## Verify Success

### ✅ Checklist

- [ ] Gray italic text appears **instantly** as you speak
- [ ] Text turns green/orange when you pause
- [ ] Purple dot text appears 2-3 seconds later
- [ ] Hover over text shows "browser-stt" or "whisper"
- [ ] Text inserted into chat input field
- [ ] No console errors (except maybe audio-capture)

### ✅ Visual Test

**Speak this phrase:**  
"The quick brown fox jumps over the lazy dog"

**You should see:**
```
Timeline:
0.0s: Click microphone
0.3s: 💭 "The quick..."▋
0.5s: 💭 "The quick brown..."▋
0.8s: 💭 "The quick brown fox..."▋
1.2s: ✅ "The quick brown fox jumps over the lazy dog" (green)
3.5s: ● "The quick brown fox jumps over the lazy dog" (purple dot)
```

---

## Quick Reference

### Browser Console Commands

**Check if Speech Recognition available:**
```javascript
console.log('STT Available:', !!(window.SpeechRecognition || window.webkitSpeechRecognition));
```

**Check module loaded:**
```javascript
console.log('Module loaded:', !!window.STTModuleDual);
```

**Check module state:**
```javascript
console.log('State:', sttModule?.getState());
```

**Force Whisper-only mode:**
```javascript
sttModule = new STTModuleDual({
    useBrowserSTT: false, // Disable instant streaming
    // ... other options
});
```

---

## Next Steps

If everything works:
1. ✅ Read `DUAL_STT_MIGRATION_GUIDE.md` for advanced config
2. ✅ Read `CONFIDENCE_STYLING_REFERENCE.md` for styling options
3. ✅ Customize colors/animations in CSS file
4. ✅ Test with different languages (change `browserLanguage`)
5. ✅ Monitor performance in production

If issues persist:
1. ❌ Check browser (must be Chrome/Edge)
2. ❌ Check Flask logs for Whisper errors
3. ❌ Check microphone settings in OS
4. ❌ Try incognito mode (eliminate extension conflicts)
5. ❌ Check `DUAL_STT_MIGRATION_GUIDE.md` troubleshooting section

---

## Configuration Quick Tweaks

### Disable Browser STT (Whisper Only)
```javascript
useBrowserSTT: false
```

### Change Language
```javascript
browserLanguage: 'es-ES'  // Spanish
```

### Faster Chunks (More Real-Time)
```javascript
timeSlice: 500  // 500ms chunks instead of 1000ms
```

### Slower Chunks (Less API Calls)
```javascript
timeSlice: 3000  // 3s chunks
```

---

## Common Mistakes

### ❌ Mistake 1: Using Old Module
```javascript
// WRONG
sttModule = new STTModule({ ... });
```
```javascript
// CORRECT
sttModule = new STTModuleDual({ ... });
```

---

### ❌ Mistake 2: Missing onInterimTranscript
```javascript
// WRONG - No interim callback
sttModule = new STTModuleDual({
    onTranscript: (data) => { ... }
    // Missing: onInterimTranscript
});
```
```javascript
// CORRECT - Both callbacks
sttModule = new STTModuleDual({
    onInterimTranscript: (data) => { ... },  // For streaming
    onTranscript: (data) => { ... }           // For final
});
```

---

### ❌ Mistake 3: Not Passing Source
```javascript
// WRONG
streamText(data.transcript, true, data.confidence);
```
```javascript
// CORRECT
streamText(data.transcript, true, data.confidence, data.source);
```

---

## Success Indicators

### 🟢 What Success Looks Like

**Console:**
```
✅ [Dual STT] Initialized successfully
   • Browser STT: ENABLED
   • Whisper Backend: ENABLED
💭 [Browser STT] Interim: "..."
📝 [Browser STT] Final: "..." (confidence: 92%)
✅ [Whisper] Transcribed: "..."
```

**Visual:**
- Gray text appears instantly (< 0.5s)
- Green text when you pause (< 1.5s)
- Purple dot text 2-3s later
- Smooth animations, no flickering
- Hover shows tooltips

**User Experience:**
- Feels like Google Docs voice typing
- Text appears as you speak
- No waiting for backend
- Quality improves after speech ends

---

## One-Line Health Check

**Run this in browser console:**
```javascript
fetch('http://localhost:5001/api/system/check').then(r=>r.json()).then(d=>console.log('✅ Whisper available:',d.whisper_available)); console.log('✅ Browser STT available:', !!(window.SpeechRecognition||window.webkitSpeechRecognition)); console.log('✅ Module loaded:', !!window.STTModuleDual);
```

**Expected output:**
```
✅ Browser STT available: true
✅ Module loaded: true
✅ Whisper available: true
```

---

## Rollback (If Needed)

**Change one line:**
```javascript
// Change from:
sttModule = new STTModuleDual({ ... });

// Back to:
sttModule = new STTModule({ ... });
```

Remove the `onInterimTranscript` callback (not needed for old module).

---

**Total Time:** 5 minutes  
**Difficulty:** Easy (2 code changes)  
**Reward:** Instant streaming transcription like Google Docs  

**Ready?** Start with Step 1! 🚀
