# 🎤 Transcription Sidebar - Complete Integration Guide

**Complete settings sidebar for STT + TTS transcription modules**

---

## 📋 Files Created

| File | Purpose | Size | Status |
|------|---------|------|--------|
| `transcription-sidebar.html` | Sidebar HTML structure | 350 lines | ✅ Complete |
| `transcription-sidebar.css` | Sidebar styling | 700 lines | ✅ Complete |
| `transcription-sidebar.js` | Controller logic | 650 lines | ✅ Complete |

---

## 🎯 Features

### 🎤 STT Settings Tab
- Whisper backend URL configuration
- API key management (optional)
- Insert mode selection (append/replace/none)
- Chunk size adjustment (1-10 seconds)
- Sample rate selection (16kHz/44kHz/48kHz)
- Live recording controls
- Recording status display (state, chunks, duration)

### 🗣️ TTS Settings Tab
- Voice selection (100+ voices)
- Speed control (0.5x - 2x)
- Pitch control (0.5x - 2x)
- Volume control (0% - 100%)
- Playback controls (pause/stop/clear)
- TTS status display (state, utterances, position)

### 📝 Transcripts Tab
- STT transcript collection with timestamps
- TTS transcript collection with timestamps
- Copy/delete individual transcripts
- Export as TXT or JSON
- Clear all transcripts

### 📊 Status Tab
- Whisper backend connection status
- Browser support detection (MediaRecorder, SpeechSynthesis, Microphone)
- Session statistics (chunks, utterances, recording time, words)
- Reset statistics function

---

## 🚀 Integration Steps

### Step 1: Add Files to Project

Place the following files in `AI_agents/UI/modules/transcription/`:

```
UI/modules/transcription/
├── stt-module.js (already exists)
├── stt-module.css (already exists)
├── tts-module.js (already exists)
├── tts-module.css (already exists)
├── transcription-sidebar.html ✨ NEW
├── transcription-sidebar.css ✨ NEW
└── transcription-sidebar.js ✨ NEW
```

### Step 2: Add to HTML `<head>` Section

Add CSS files:

```html
<!-- Transcription Modules -->
<link rel="stylesheet" href="UI/modules/transcription/stt-module.css">
<link rel="stylesheet" href="UI/modules/transcription/tts-module.css">
<link rel="stylesheet" href="UI/modules/transcription/transcription-sidebar.css">
```

### Step 3: Load Sidebar HTML

Add before closing `</body>` tag:

```html
<!-- Transcription Modules -->
<script src="UI/modules/transcription/stt-module.js"></script>
<script src="UI/modules/transcription/tts-module.js"></script>
<script src="UI/modules/transcription/transcription-sidebar.js"></script>

<script>
    // Load transcription sidebar HTML dynamically
    fetch('UI/modules/transcription/transcription-sidebar.html')
        .then(response => response.text())
        .then(html => {
            document.body.insertAdjacentHTML('beforeend', html);
            console.log('[Transcription] Sidebar HTML loaded');
            
            // Initialize sidebar
            if (window.TranscriptionSidebar) {
                window.TranscriptionSidebar.init();
            }
        })
        .catch(error => console.error('[Transcription] Failed to load sidebar HTML:', error));
</script>
```

### Step 4: Add Microphone Button to Chat Input

Find your chat input area and add the microphone button:

```html
<!-- Example: Chat input container -->
<div class="chat-input-container">
    <!-- Microphone button (toggles sidebar) -->
    <button id="transcription-sidebar-toggle" 
            class="chat-input-btn" 
            onclick="TranscriptionSidebar.toggleSidebar()"
            title="Open transcription settings">
        <i class="fas fa-microphone"></i>
    </button>
    
    <!-- Chat input -->
    <textarea id="ai-chat-input" placeholder="Type or speak your message..."></textarea>
    
    <!-- Send button -->
    <button id="send-btn" class="chat-input-btn">
        <i class="fas fa-paper-plane"></i>
    </button>
</div>
```

**CSS for microphone button** (add to your main CSS):

```css
.chat-input-btn {
    width: 40px;
    height: 40px;
    border: none;
    background: var(--accent-primary, #58a6ff);
    color: white;
    border-radius: 8px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
}

.chat-input-btn:hover {
    background: var(--accent-hover, #4a93e0);
    transform: scale(1.05);
}

.chat-input-btn i {
    font-size: 18px;
}
```

---

## 🎨 Visual Design

### Sidebar Layout

```
┌─────────────────────────────────────────────┐
│ 🎤 Transcription              [↻] [×]      │  Header
├─────────────────────────────────────────────┤
│ [STT] [TTS] [Transcripts] [Status]          │  Tabs
├─────────────────────────────────────────────┤
│                                             │
│  🎤 Speech-to-Text Settings                 │
│  ┌───────────────────────────────────────┐ │
│  │ Whisper Backend URL:                  │ │
│  │ [http://localhost:3001/...]           │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  [💾 Save STT Settings]                     │
│  [🧪 Test STT Connection]                   │
│                                             │
│  🎚️ Recording Controls                      │
│  [🎤 Start Recording]                       │
│                                             │
│  State: Idle                                │
│  Chunks Sent: 0                             │
│  Duration: 0:00                             │
│                                             │
└─────────────────────────────────────────────┘
```

### Color Scheme

- **Background**: Dark theme (`--bg-primary`, `--bg-secondary`, `--bg-tertiary`)
- **Text**: Light theme (`--text-primary`, `--text-muted`)
- **Accent**: Blue (`--accent-primary: #58a6ff`)
- **Recording**: Red (`#ef4444` with pulsing animation)
- **Success**: Green (`#10b981`)
- **Error**: Red (`#ef4444`)

---

## 🔧 API Reference

### Global Object: `window.TranscriptionSidebar`

**Sidebar Control:**
```javascript
TranscriptionSidebar.toggleSidebar()   // Open/close sidebar
TranscriptionSidebar.switchTab('stt')  // Switch tabs: 'stt', 'tts', 'transcripts', 'status'
TranscriptionSidebar.refreshStatus()   // Refresh backend/browser status
```

**Recording Control:**
```javascript
TranscriptionSidebar.toggleRecording()  // Start/stop STT recording
```

**TTS Control:**
```javascript
TranscriptionSidebar.pauseTTS()              // Pause/resume TTS playback
TranscriptionSidebar.stopTTS()               // Stop TTS playback
TranscriptionSidebar.clearTTSTranscript()    // Clear TTS transcript display
```

**Transcript Management:**
```javascript
TranscriptionSidebar.addSTTTranscript(text)     // Add STT transcript to collection
TranscriptionSidebar.addTTSTranscript(text)     // Add TTS transcript to collection
TranscriptionSidebar.copyTranscript(timestamp)  // Copy transcript to clipboard
TranscriptionSidebar.deleteTranscript(timestamp)// Delete single transcript
TranscriptionSidebar.clearAllTranscripts()      // Clear all transcripts
TranscriptionSidebar.exportTranscripts('txt')   // Export as TXT or JSON
```

**Settings:**
```javascript
TranscriptionSidebar.saveSTTSettings()   // Save STT settings to localStorage
TranscriptionSidebar.saveTTSSettings()   // Save TTS settings to localStorage
TranscriptionSidebar.loadSettings()      // Load settings from localStorage
```

**Testing:**
```javascript
TranscriptionSidebar.testSTT()   // Test STT connection
TranscriptionSidebar.testTTS()   // Test TTS voice
```

**Statistics:**
```javascript
TranscriptionSidebar.resetStatistics()  // Reset all statistics
```

---

## 🎯 Usage Examples

### Example 1: Open Sidebar Programmatically

```javascript
// Open sidebar when user clicks microphone button
document.getElementById('mic-btn').addEventListener('click', () => {
    window.TranscriptionSidebar.toggleSidebar();
});
```

### Example 2: Automatically Add AI Response to TTS

```javascript
// When AI responds, speak it and add to transcript
function handleAIResponse(responseText) {
    // Speak response
    if (window.TranscriptionSidebar.ttsModule) {
        window.TranscriptionSidebar.ttsModule.speak(responseText);
    }
    
    // Add to transcript collection
    window.TranscriptionSidebar.addTTSTranscript(responseText);
}
```

### Example 3: Custom Recording Button

```javascript
// Add recording button anywhere in UI
<button onclick="window.TranscriptionSidebar.toggleRecording()">
    <i class="fas fa-microphone"></i> Record
</button>
```

### Example 4: Export Transcripts Automatically

```javascript
// Export transcripts when user leaves page
window.addEventListener('beforeunload', () => {
    if (confirm('Export transcripts before leaving?')) {
        window.TranscriptionSidebar.exportTranscripts('json');
    }
});
```

---

## 🔐 Backend Requirements

### Whisper Backend (Required for STT)

The sidebar expects a Whisper backend running at `http://localhost:3001/api/v1/transcribe`.

**Start backend:**
```powershell
cd "c:\Users\gpoli\GIT\MustCare ValorAISynergySuite"
docker-compose up -d
```

**Verify backend:**
```bash
curl http://localhost:3001/api/v1/system/check
```

**Expected response:**
```json
{
  "status": "ok",
  "whisper": "available",
  "version": "1.0.0"
}
```

**API Authentication** (optional):
- If backend requires authentication, set API key in sidebar settings
- API key sent as `X-API-Key` header with each request

### TTS (No Backend Required)

TTS uses native browser Web Speech API - no backend needed!

---

## 📊 Status Indicators

### Backend Status Dot

| Color | Meaning | Detail |
|-------|---------|--------|
| 🟢 Green | Online | Backend is reachable and healthy |
| 🔴 Red | Offline | Cannot connect to backend |
| ⚫ Gray | Checking | Testing connection... |

### Browser Support

| Feature | Required | Detection |
|---------|----------|-----------|
| MediaRecorder API | ✅ Yes | For STT audio recording |
| Web Speech API | ✅ Yes | For TTS playback |
| Microphone Access | ✅ Yes | For STT recording |

**All features must be supported** for full functionality.

---

## 🎛️ Settings Persistence

Settings are saved to `localStorage`:

| Setting | Key | Default |
|---------|-----|---------|
| STT Settings | `transcription-stt-settings` | See defaults below |
| TTS Settings | `transcription-tts-settings` | See defaults below |

**STT Default Settings:**
```json
{
  "whisperEndpoint": "http://localhost:3001/api/v1/transcribe",
  "apiKey": null,
  "insertMode": "append",
  "chunkSize": 5000,
  "sampleRate": 16000
}
```

**TTS Default Settings:**
```json
{
  "voice": null,
  "rate": 1.0,
  "pitch": 1.0,
  "volume": 100
}
```

---

## 🐛 Troubleshooting

### Issue: Sidebar not appearing

**Solutions:**
1. Check HTML file loaded: `fetch('UI/modules/transcription/transcription-sidebar.html')`
2. Check CSS loaded: `<link rel="stylesheet" href="UI/modules/transcription/transcription-sidebar.css">`
3. Check sidebar not collapsed: Remove `collapsed` class from `#transcription-sidebar`

**Debug commands:**
```javascript
console.log(document.getElementById('transcription-sidebar'));
console.log(window.TranscriptionSidebar);
```

### Issue: Backend connection failed

**Solutions:**
1. Check Whisper backend is running: `curl http://localhost:3001/api/v1/system/check`
2. Check endpoint URL in settings tab
3. Check network tab in browser DevTools for CORS errors
4. Try with/without API key

### Issue: Microphone not working

**Solutions:**
1. Check microphone permission granted in browser settings
2. Check microphone not used by another application
3. Check browser supports MediaRecorder API (Chrome, Edge, Firefox)

**Debug command:**
```javascript
navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
        console.log('Microphone access granted');
        stream.getTracks().forEach(track => track.stop());
    })
    .catch(err => console.error('Microphone access denied:', err));
```

### Issue: TTS not speaking

**Solutions:**
1. Check browser supports Web Speech API (check Status tab)
2. Check volume not muted in sidebar settings
3. Check voice selected in dropdown
4. Try different voice (some voices may not work on all systems)

**Debug command:**
```javascript
if ('speechSynthesis' in window) {
    console.log('Web Speech API supported');
    console.log('Available voices:', speechSynthesis.getVoices().length);
} else {
    console.error('Web Speech API not supported');
}
```

---

## 🎨 Customization

### Change Sidebar Width

Edit `transcription-sidebar.css` line 18:

```css
.transcription-sidebar {
    width: 450px;  /* Change to desired width (e.g., 500px, 600px) */
}
```

### Change Sidebar Side (Left/Right)

Edit `transcription-sidebar.css` lines 21-22:

```css
/* For right side (default): */
.transcription-sidebar {
    right: 0;
}

/* For left side: */
.transcription-sidebar {
    left: 0;
    right: auto;
    border-left: none;
    border-right: 1px solid var(--border-default, #30363d);
}
```

### Add Custom Tab

1. Add tab button in HTML:
```html
<button class="transcription-tab" onclick="TranscriptionSidebar.switchTab('custom')" data-tab="custom">
    <i class="fas fa-star"></i>
    <span>Custom</span>
</button>
```

2. Add tab content:
```html
<div class="transcription-tab-content" id="custom-tab">
    <div class="transcription-section">
        <h3><i class="fas fa-star"></i> Custom Settings</h3>
        <!-- Your custom content here -->
    </div>
</div>
```

---

## ✅ Final Checklist

Before deployment, verify:

- [ ] All 3 files added to `UI/modules/transcription/`
- [ ] CSS files linked in `<head>` section
- [ ] JavaScript files loaded before `</body>`
- [ ] Sidebar HTML loaded dynamically
- [ ] Microphone button added to chat input
- [ ] Whisper backend running (for STT)
- [ ] Browser supports required APIs (check Status tab)
- [ ] Settings persist after page reload
- [ ] Transcripts can be exported
- [ ] Sidebar opens/closes smoothly

---

## 📚 Related Documentation

- **STT Module**: `STT_MODULE_COMPLETE.md` (coming soon)
- **TTS Module**: `TTS_MODULE_COMPLETE.md` (already exists)
- **Complete Demo**: `complete-demo.html` (already exists)
- **Integration Guide**: This document

---

**Last Updated:** November 25, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready

---

## 🎉 Next Steps

1. **Integrate into `business-ai-platform-v2.html`**:
   - Add microphone button to chat input
   - Load sidebar HTML/CSS/JS
   - Initialize `TranscriptionSidebar.init()`

2. **Connect to Chat System**:
   - Auto-insert STT transcripts into chat input
   - Auto-speak AI responses with TTS
   - Save transcripts to database

3. **Enhance UI**:
   - Add keyboard shortcuts (Ctrl+M for microphone)
   - Add toast notifications for success/error
   - Add tutorial/onboarding for first-time users

4. **Add Analytics**:
   - Track usage statistics (recordings, transcripts)
   - Monitor backend health metrics
   - Export analytics dashboard

Would you like me to proceed with integrating the sidebar into `business-ai-platform-v2.html`?
