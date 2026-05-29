# Transcription Feature Analysis — May 28, 2026

**Date:** May 28, 2026  
**Author:** GitHub Copilot (Analysis of AI Agents V11 codebase)  
**Platform:** Business AI Platform v2 (Flask + Vanilla JS SPA)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Interface Layout](#2-interface-layout)
   - 2.1 [Prime Chat Mic Button](#21-prime-chat-mic-button)
   - 2.2 [Agent Input Mic Buttons](#22-agent-input-mic-buttons)
   - 2.3 [Transcription Sidebar Toggle Button](#23-transcription-sidebar-toggle-button)
   - 2.4 [Transcription Sidebar (5-Tab Layout)](#24-transcription-sidebar-5-tab-layout)
   - 2.5 [Streaming Container (Floating Status UI)](#25-streaming-container-floating-status-ui)
3. [File Map & Code Locations](#3-file-map--code-locations)
4. [Architecture Overview](#4-architecture-overview)
5. [How It Works — User Flow](#5-how-it-works--user-flow)
   - 5.1 [Prime Chat: Voice-to-Chat Flow](#51-prime-chat-voice-to-chat-flow)
   - 5.2 [Agent Input: Per-Agent Voice Flow](#52-agent-input-per-agent-voice-flow)
   - 5.3 [Sidebar: Full-Featured Recording Flow](#53-sidebar-full-featured-recording-flow)
   - 5.4 [Upload Tab: Whisper File Transcription Flow](#54-upload-tab-whisper-file-transcription-flow)
   - 5.5 [TTS Flow](#55-tts-flow)
6. [Technical Deep-Dive](#6-technical-deep-dive)
   - 6.1 [SharedTranscriptionState Singleton](#61-sharedtranscriptionstate-singleton)
   - 6.2 [Browser Speech Recognition (webkitSpeechRecognition)](#62-browser-speech-recognition-webkitspeechrecognition)
   - 6.3 [Audio Level Monitoring (Web Audio API)](#63-audio-level-monitoring-web-audio-api)
   - 6.4 [TranscriptionSidebarController](#64-transcriptionsidebarcontroller)
   - 6.5 [Streaming Container (window.TranscriptionStreaming)](#65-streaming-container-windowtranscriptionstreaming)
   - 6.6 [Backend: Flask Blueprint (transcription_routes.py)](#66-backend-flask-blueprint-transcription_routespy)
   - 6.7 [Database Schema](#67-database-schema)
   - 6.8 [Agent Input Manager Integration](#68-agent-input-manager-integration)
7. [Key Functions & Line Numbers](#7-key-functions--line-numbers)
8. [Current Limitations & Known Issues](#8-current-limitations--known-issues)
9. [Platform Comparison: Anthropic Claude vs OpenAI ChatGPT vs This Implementation](#9-platform-comparison-anthropic-claude-vs-openai-chatgpt-vs-this-implementation)
   - 9.1 [Anthropic Claude — Audio & Transcription Capabilities](#91-anthropic-claude--audio--transcription-capabilities)
   - 9.2 [OpenAI / ChatGPT — Transcription Ecosystem (2025–2026)](#92-openai--chatgpt--transcription-ecosystem-20252026)
   - 9.3 [This Platform vs Industry Leaders](#93-this-platform-vs-industry-leaders)
10. [Enhancement Recommendations](#10-enhancement-recommendations)

---

## 1. Executive Summary

The AI Agents Business Platform v2 includes a mature, multi-mode voice transcription system built into the frontend as a pluggable module (`UI/modules_internal/transcription/`). It provides:

- **Live recording** from microphone or system audio using the browser `webkitSpeechRecognition` API
- **File upload transcription** via OpenAI Whisper (local model, presently disabled for Docker builds)
- **Text-to-Speech (TTS)** via browser `speechSynthesis`
- **Real-time audio level visualisation** using Web Audio API FFT analysis
- **Per-agent** and **Prime Chat** mic buttons that route spoken text directly into their respective input fields
- **A full 5-tab sidebar** for advanced recording, file management, TTS, transcript export, and configuration

The primary STT engine is Chrome's built-in `webkitSpeechRecognition`, which delivers instant, zero-latency transcription without any network round trips. The secondary Whisper-based engine (higher accuracy, offline) is architected and present but currently disabled in production.

In contrast with the industry leaders: **Anthropic Claude has no audio/STT API** as of May 2026, while **OpenAI** has built a rich audio platform (`whisper-1`, `gpt-4o-transcribe`, `gpt-4o-transcribe-diarize`, `gpt-realtime-whisper`) that represents the direction this system should evolve toward.

---

## 2. Interface Layout

### 2.1 Prime Chat Mic Button

**Location:** Bottom toolbar of the Prime Chat input area  
**File:** `UI/business-ai-platform-v2.html` — approximately line 20948  
**HTML:**
```html
<button class="ai-chat-mic-btn" id="ai-chat-mic-btn"
    title="Start voice transcription"
    onclick="toggleTranscriptionRecording()">
    <i class="fas fa-microphone"></i>
</button>
```

**CSS (lines ~11143–11210):**
```css
.ai-chat-mic-btn {
    width: 32px;
    height: 32px;
    background: transparent;
    color: rgba(139,148,158,0.5);
    border: none;
    border-radius: 6px;
}
/* Visible only when input panel is expanded */
.ai-chat-input-container.expanded .ai-chat-mic-btn {
    border: 1px solid var(--border-default);
    color: var(--text-primary);
}
.ai-chat-mic-btn:hover {
    color: var(--accent-primary) !important;
    border-color: var(--accent-primary) !important;
}
/* Recording state — red pulsing */
.ai-chat-mic-btn.recording {
    background: rgba(218,54,51,0.15);
    color: #da3633;
    border-color: #da3633;
    animation: pulse 1.5s infinite;
}
```

**Behaviour:**
- Hidden (low opacity) when Prime Chat panel is collapsed
- Visible with `border-default` when panel is expanded
- Turns red with a pulsing animation when recording is active
- `onclick` calls global `window.toggleTranscriptionRecording()`

---

### 2.2 Agent Input Mic Buttons

**Location:** Per-agent input toolbar (one mic button per active AI agent)  
**File:** `UI/modules_internal/agents/agent-input-manager.js` — line 269  
**HTML ID pattern:** `id="agent-mic-{agentId}"`  
**Icon:** `fas fa-microphone` → switches to `fas fa-stop` when recording

**Behaviour:**
- Each agent has its own independent mic button
- Clicking starts/stops recording via `SharedTranscriptionState.startRecording(null, customCallback)`
- `customCallback` routes final transcripts **directly into that agent's** `#agent-input-{agentId}` textarea
- Auto-expands the agent input area on recording start

---

### 2.3 Transcription Sidebar Toggle Button

**Location:** Left navigation panel  
**File:** `UI/business-ai-platform-v2.html` — line ~18713  
**HTML:**
```html
<button id="transcription-sidebar-toggle"
    data-action="transcription-sidebar"
    title="Transcript Processing"
    class="sidebar-nav-btn">
    <i class="fas fa-microphone-alt"></i>
</button>
```

**Behaviour:** Toggles the left sidebar (450px wide) between `collapsed` and open states.

---

### 2.4 Transcription Sidebar (5-Tab Layout)

**File:** `UI/modules_internal/transcription/transcription-sidebar.html` (loaded dynamically via `fetch()`)  
**Container:** `<div class="universal-sidebar sidebar-left collapsed" id="transcription-sidebar" data-side="left">` — line ~21160  
**Width:** 450px (Universal Sidebar Framework)

The sidebar has five tabs:

| Tab | ID | Content |
|-----|-----|---------|
| **Recording** (default) | `recording-tab` | Status stats grid, audio detection with 8 EQ bars, source selector, live transcript display |
| **Upload** | `upload-tab` | Drag-and-drop zone, language selection (14 languages + auto), progress bar, history list |
| **TTS** | `tts-tab` | Voice selector, speed/pitch/volume sliders, playback controls |
| **Transcripts** | `transcripts-tab` | STT + TTS transcript collections with TXT/JSON export |
| **Settings** | `settings-tab` | Word timestamps, speaker diarisation, quality metrics, language detection, VAD, export format (text/json/srt/vtt/ass), STT backend URL override |

**Recording Tab Detail:**
- Left column: Status stats (`#stt-state`, `#stt-duration`, `#stt-chunks`)
- Right column: Record button, Pause button, Delete button
- Audio Detection panel (collapsible): 8 `.eq-bar` elements (real-time FFT equaliser), `#audio-level-badge` (shows dB), source selector (System Audio vs Microphone)
- Live transcript: `#transcription-live-display` — interim text shown in grey, final text in white

**Upload Tab Detail:**
- `#upload-zone` — draggable, `onclick` triggers `#transcription-file-input`
- Language select `#whisper-language-select` — 14 options (English, Spanish, French, German, Italian, Portuguese, Dutch, Russian, Chinese, Japanese, Korean, Arabic, Hindi, auto)
- `#transcription-history-list` — prior uploads with search

---

### 2.5 Streaming Container (Floating Status UI)

**Files:**
- `UI/modules_internal/transcription/transcription-streaming-container.html`
- `UI/modules_internal/transcription/transcription-streaming-container.js`

**Purpose:** A small floating overlay displayed below the Prime Chat input during live recording. Shows recording status, accumulated transcript text, and quick actions (Insert to Input, Send).

**Key elements:**
- `#ai-transcription-container` — the floating box
- `#ai-transcription-text` — scrolling transcript display
- Status dot with states: `ready` (grey) → `recording` (red pulsing) → `processing` (yellow)
- "Insert" button → copies text to `#ai-chat-input`
- "Send" button → insert + fires send event

---

## 3. File Map & Code Locations

### Frontend Files

| File | Purpose | Key Contents |
|------|---------|-------------|
| `UI/business-ai-platform-v2.html` | Main SPA | Mic button (L20948), sidebar toggle (L18713), sidebar container (L21160), init block (L28737–28843), recording CSS (L28951–28958), CSS links (L774–778) |
| `UI/modules_internal/transcription/transcription-sidebar.js` | Core STT/singleton | `SharedTranscriptionState` class, `TranscriptionSidebarController` class |
| `UI/modules_internal/transcription/transcription-sidebar.html` | 5-tab sidebar UI | All tab HTML, `.eq-bar` elements, controls |
| `UI/modules_internal/transcription/transcription-sidebar.css` | Sidebar styles | tab styles, EQ bar animations, recording state colours |
| `UI/modules_internal/transcription/transcription-streaming-container.js` | Floating overlay | `window.TranscriptionStreaming` singleton |
| `UI/modules_internal/transcription/transcription-streaming-container.html` | Floating overlay UI | `#ai-transcription-container`, status dot, text area, action buttons |
| `UI/modules_internal/transcription/transcription-streaming-container.css` | Overlay styles | |
| `UI/modules_internal/transcription/config.js` | Config & base URLs | `TranscriptionConfig` class, endpoint map, localStorage URL override |
| `UI/modules_internal/transcription/stt-module.js` | Original STT module | **Currently commented out** (L28742 in main HTML); MediaRecorder + Whisper approach |
| `UI/modules_internal/transcription/tts-module.js` | TTS module | `speechSynthesis` wrapper |
| `UI/modules_internal/transcription/ARCHITECTURE.md` | Architecture docs | Component diagram, callback names, design rationale |
| `UI/modules_internal/agents/agent-input-manager.js` | Per-agent inputs | `toggleTranscription(agentId)` at line 269 |

### Backend Files

| File | Purpose | Key Contents |
|------|---------|-------------|
| `AI_infrastructure/routes/transcription_routes.py` | Flask Blueprint | `transcription_bp`, all 4 endpoints |
| `AI_infrastructure/database_toolkit/schema_manager.py` | DB schema | `user_transcriptions` table, `transcription_uploads` table |

### Config Files

| File | Purpose |
|------|---------|
| `UI/modules_internal/transcription/config.js` | `TranscriptionConfig` — endpoint URLs, base URL auto-detection |

---

## 4. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              TRANSCRIPTION SYSTEM                                   │
│                                                                                     │
│  ┌─────────────────┐   ┌──────────────────────┐   ┌──────────────────────────────┐ │
│  │  Prime Chat     │   │  Agent Input Manager │   │  Transcription Sidebar       │ │
│  │  #ai-chat-mic-  │   │  #agent-mic-{n}      │   │  #transcription-sidebar      │ │
│  │  btn            │   │  toggleTranscription │   │  5-tab UI (450px left panel) │ │
│  │  onclick=toggle │   │  (agentId)           │   │  via fetch() inject          │ │
│  │  Transcription  │   │                      │   │                              │ │
│  │  Recording()    │   │  Routes output →     │   │  TranscriptionSidebarCtrl   │ │
│  └────────┬────────┘   │  agent textarea      │   │  .toggleRecording()          │ │
│           │            └──────────┬───────────┘   └──────────────┬───────────────┘ │
│           │                       │                               │                 │
│           └───────────────────────┴───────────────────────────────┘                 │
│                                           │                                         │
│                                           ▼                                         │
│                         ┌────────────────────────────────┐                         │
│                         │  window.SharedTranscriptionState │                        │
│                         │  (Singleton — transcription-    │                        │
│                         │   sidebar.js)                   │                        │
│                         │                                 │                        │
│                         │  startRecording(source, cb)     │                        │
│                         │  stopRecording()                │                        │
│                         │  startAudioPreview()            │                        │
│                         │  on(event, callback)            │                        │
│                         │  trigger(event, ...args)        │                        │
│                         └───────────────┬─────────────────┘                        │
│                                         │                                           │
│              ┌──────────────────────────┤──────────────────────────┐               │
│              ▼                          ▼                          ▼               │
│  ┌───────────────────────┐  ┌──────────────────────┐  ┌────────────────────────┐  │
│  │  webkitSpeechRecog.   │  │  getDisplayMedia()   │  │  getUserMedia()        │  │
│  │  (Chrome Web Speech   │  │  (System Audio)      │  │  (Microphone)          │  │
│  │  API)                 │  │  [experimental]      │  │  [primary fallback]    │  │
│  │  continuous: true     │  └──────────────────────┘  └────────────────────────┘  │
│  │  interimResults: true │             │                          │               │
│  │  lang: 'en-US'        │             └──────────────────────────┘               │
│  │  auto-restart on end  │                          │                             │
│  └────────────┬──────────┘                          ▼                             │
│               │                       ┌─────────────────────────┐                 │
│               │                       │  Web Audio API          │                 │
│               │                       │  AudioContext           │                 │
│               │                       │  AnalyserNode (fft=256) │                 │
│               │                       │  8 × .eq-bar elements   │                 │
│               │                       │  #audio-level-badge     │                 │
│               │                       └─────────────────────────┘                 │
│               │                                                                   │
│    ┌──────────▼──────────────────────────────────────────────────────────────┐    │
│    │               Observer Callbacks (trigger / on)                         │    │
│    │  onStart   → update mic button CSS + TranscriptionStreaming.updateStatus │    │
│    │  onStop    → remove recording class from all mic buttons                 │    │
│    │  onTranscript → route text to correct textarea (via source param / cb)  │    │
│    │  onError   → display error, log to console                               │    │
│    └─────────────────────────────────────────────────────────────────────────┘    │
│                                         │                                          │
│                    ┌────────────────────┴────────────────────┐                    │
│                    ▼                                         ▼                    │
│     ┌──────────────────────────┐            ┌───────────────────────────────┐    │
│     │  Streaming Container     │            │  Sidebar Live Display        │    │
│     │  window.TranscriptionS.  │            │  #transcription-live-display  │    │
│     │  #ai-transcription-text  │            │  grey = interim, white=final  │    │
│     │  → #ai-chat-input        │            └───────────────────────────────┘    │
│     └──────────────────────────┘                                                  │
│                                                                                   │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │                     BACKEND (Flask — transcription_routes.py)              │  │
│  │                                                                            │  │
│  │  POST /api/transcribe          ← file upload → Whisper → transcript text  │  │
│  │  GET  /api/system/check        ← health + Whisper availability check      │  │
│  │  POST /api/transcriptions/save ← @require_auth → PostgreSQL INSERT        │  │
│  │  GET  /api/transcriptions/history ← paginated history                     │  │
│  │                                                                            │  │
│  │  Whisper: lazy-loaded (get_whisper_model()) — DISABLED in Docker Dec 2025 │  │
│  └────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. How It Works — User Flow

### 5.1 Prime Chat: Voice-to-Chat Flow

1. User clicks the **mic button** (`#ai-chat-mic-btn`) in the Prime Chat toolbar.
2. `onclick="toggleTranscriptionRecording()"` fires — this global function is defined in the main HTML init block at line ~28803.
3. If **not currently recording**:
   - Calls `window.SharedTranscriptionState.startRecording('chat')`.
   - Browser prompts for microphone permission (first time).
   - `startRecording()` attempts `getDisplayMedia` (system audio) first; falls back to `getUserMedia` (microphone).
   - `webkitSpeechRecognition` starts with `continuous=true`, `interimResults=true`.
   - The mic button changes to red pulsing animation (`.recording` class added).
   - The streaming container (`TranscriptionStreaming`) shows a red status dot.
   - The `onStart` callback fires — updates button appearance.
4. As the user speaks:
   - `browserRecognition.onresult` fires continuously.
   - Interim results (grey) stream to `#ai-transcription-text` in the floating container.
   - Final results stream as white text appended to the transcript.
5. User clicks the button again to **stop**:
   - `SharedTranscriptionState.stopRecording()` called.
   - `browserRecognition.stop()` called, audio stream tracks stopped.
   - `onStop` callbacks fire — mic button returns to default state.
6. The accumulated text in the streaming container can be:
   - Clicked **Insert** → copies to `#ai-chat-input`
   - Clicked **Send** → insert + triggers send button

---

### 5.2 Agent Input: Per-Agent Voice Flow

1. User clicks the mic button in a specific Agent's input toolbar (`#agent-mic-{agentId}`).
2. `toggleTranscription(agentId)` fires in `agent-input-manager.js` (line 269).
3. Agent input area is **auto-expanded** (`expand(agentId)`).
4. `SharedTranscriptionState.startRecording(null, customCallback)` is called.
   - The `customCallback` is unique per agent: on final transcript, it appends text to `#agent-input-{agentId}` and dispatches an `input` event to trigger auto-resize.
5. Mic button changes to `fas fa-stop` + `.recording` class.
6. Spoken words are routed **only to that agent's textarea**, not to Prime Chat.
7. Clicking stop restores the microphone icon and stops recording.

Key difference from Prime Chat: the agent mic flow uses a **custom callback** rather than the global `onTranscript` events, so text is precisely routed to the correct agent input without cross-contamination.

---

### 5.3 Sidebar: Full-Featured Recording Flow

1. User opens sidebar via **Transcript Processing** button in left nav (`#transcription-sidebar-toggle`).
2. The sidebar HTML is lazy-loaded via `fetch()` into `#transcription-sidebar` (if not already loaded).
3. `TranscriptionSidebar.init()` runs — loads settings from `localStorage`, starts audio preview (1 second delay), checks browser support.
4. **Audio Preview** (`startAudioPreview()`): Silently acquires the microphone stream and starts FFT analysis, so the equaliser bars are **already moving** when the user opens the sidebar, providing visual feedback of microphone health before recording starts.
5. User can select audio source: **System Audio** (screen share audio) or **Microphone** — via `selectAudioSource(source)`.
6. User clicks **Record** → `toggleRecording()` → `SharedTranscriptionState.startRecording('sidebar')`.
7. Live transcript text appears in `#transcription-live-display`:
   - **Interim** results in grey (still being processed by browser STT)
   - **Final** results in white (confirmed words)
8. User can click **Pause** → `togglePause()` → calls `browserRecognition.stop()` / `.start()` to suspend/resume.
9. User clicks **Delete** to clear the current transcript buffer.
10. Switch to **Transcripts** tab → export as TXT or JSON via `exportTranscripts()`.

---

### 5.4 Upload Tab: Whisper File Transcription Flow

1. User Opens sidebar → clicks **Upload** tab.
2. Drags an audio file (wav/mp3/webm/ogg/m4a/flac) onto `#upload-zone`, or clicks to browse files via `#transcription-file-input`.
3. `handleFileDrop(event)` or `handleFileSelect(event)` fires.
4. File is validated (extension check) and sent as `multipart/form-data` `POST /api/transcribe` to the backend.
5. Backend (`transcription_routes.py`):
   - Validates extension against allowed list.
   - Saves file to a temp path.
   - Calls `get_whisper_model()` (lazy-loaded `openai-whisper` + `torch`).
   - **⚠️ CURRENTLY DISABLED:** Whisper model is not loaded in Docker build (Dec 2025 optimisation). Returns placeholder message: `"[Whisper not available - install openai-whisper or enable model]"`.
   - If enabled: returns `{transcript, language, confidence, duration, word_count}`.
6. Transcript is displayed in the Upload tab and optionally saved to `user_transcriptions` PostgreSQL table.

---

### 5.5 TTS Flow

1. User opens sidebar → clicks **TTS** tab.
2. Types text in TTS input area.
3. Adjusts voice (browser-native voices), speed (0.5–2.0), pitch (0–2), volume (0–1) via sliders.
4. Clicks **Play** → `tts-module.js` calls `speechSynthesis.speak(utterance)`.
5. Spoken text is saved to TTS transcript collection and visible in the **Transcripts** tab.
6. User can export TTS transcripts as TXT or JSON.

---

## 6. Technical Deep-Dive

### 6.1 SharedTranscriptionState Singleton

**File:** `UI/modules_internal/transcription/transcription-sidebar.js`  
**Instantiated as:** `window.SharedTranscriptionState = new SharedTranscriptionState()`

This is the core class that owns all recording state. It is a singleton — only one instance ever exists — and is the single source of truth for whether recording is active.

**Key properties:**
```javascript
this.isRecording = false;
this.browserRecognition = null;   // webkitSpeechRecognition instance
this.audioContext = null;         // Web Audio API context
this.audioAnalyzer = null;        // AnalyserNode for FFT
this.previewStream = null;        // MediaStream for audio preview
this.previewSource = null;        // AudioBufferSourceNode
this.recordingSource = null;      // Current recording source
this.callbacks = {
    onStart: [],
    onStop: [],
    onTranscript: [],
    onError: []
};
```

**Observer pattern:**
```javascript
on(event, callback)       // Register callback for an event
trigger(event, ...args)   // Execute all callbacks for an event
```

**`startRecording(source, transcriptCallback)`:**
```
source = 'chat' | 'sidebar' | 'agent-{id}' | null
transcriptCallback = custom function for routing (used by agent input manager)
```
1. Tries `navigator.mediaDevices.getDisplayMedia({ audio: true, video: false })` for system audio.
2. Falls back to `navigator.mediaDevices.getUserMedia({ audio: true })` for microphone.
3. Creates `new webkitSpeechRecognition()` with `continuous=true`, `interimResults=true`, `lang='en-US'`.
4. Wires `onresult`, `onerror`, `onend` (auto-restart) handlers.
5. Sets `isRecording = true`, triggers `onStart` callbacks.
6. Returns a Promise.

**Audio source priority logic:**
```
1. System Audio (getDisplayMedia) — preferred for meeting recording, system-wide capture
        ↓ if fails (user denies or unsupported)
2. Microphone (getUserMedia) — standard microphone input
```

---

### 6.2 Browser Speech Recognition (webkitSpeechRecognition)

**API:** Chrome's proprietary `webkitSpeechRecognition` (also available as `SpeechRecognition` in newer Chrome versions)

**Configuration:**
```javascript
recognition.continuous = true;        // Don't stop after one phrase
recognition.interimResults = true;    // Fire events for partial results
recognition.lang = 'en-US';           // Language (configurable via settings)
```

**`onresult` handler:**
```javascript
recognition.onresult = (event) => {
    let interim = '';
    let final = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
            final += event.results[i][0].transcript;
        } else {
            interim += event.results[i][0].transcript;
        }
    }
    // Route to appropriate target via callbacks
    trigger('onTranscript', final, interim);
    if (transcriptCallback) transcriptCallback(final, interim);
};
```

**Auto-restart logic:**
Chrome's STT automatically pauses after ~60 seconds of silence (or speech). The `onend` handler:
```javascript
recognition.onend = () => {
    if (this.isRecording) {
        // Still supposed to be recording — restart
        recognition.start();
    }
};
```
This ensures continuous recording without user intervention.

**Browser Compatibility:**
- ✅ Chrome / Chromium: Full support
- ✅ Edge (Chromium): Full support
- ❌ Firefox: `webkitSpeechRecognition` not supported
- ❌ Safari: Partial support (requires `SpeechRecognition` polyfill)

---

### 6.3 Audio Level Monitoring (Web Audio API)

**`startAudioLevelMonitoring(audioStream, isPreview)`:**
```javascript
this.audioContext = new AudioContext();
this.audioAnalyzer = this.audioContext.createAnalyser();
this.audioAnalyzer.fftSize = 256;    // 128 frequency bins
const source = this.audioContext.createMediaStreamSource(audioStream);
source.connect(this.audioAnalyzer);
```

**`updateAudioLevels()` — requestAnimationFrame loop:**
```javascript
const dataArray = new Uint8Array(analyzerNode.frequencyBinCount);  // 128 values
analyzerNode.getByteFrequencyData(dataArray);

// Map 128 frequency bins → 8 EQ bars
// Calculate RMS dB level
// Colour: green (optimal -30dB to -10dB) → orange (good, louder) → red (loud, >-5dB)
// Update 8 × .eq-bar heights + #audio-level-badge text
requestAnimationFrame(updateAudioLevels);
```

This runs at ~60fps and provides a real-time visual equaliser in the sidebar Recording tab, giving users immediate feedback on audio input quality before and during recording.

---

### 6.4 TranscriptionSidebarController

**File:** `UI/modules_internal/transcription/transcription-sidebar.js`  
**Exposed as:** `window.TranscriptionSidebar`

**`init()`:**
- Loads settings from `localStorage`
- Calls `startAudioPreview()` after 1 second
- Checks browser support (`webkitSpeechRecognition` availability)
- Inits TTS module and STT module (if enabled)

**`toggleRecording()`:**
- If not recording: calls `SharedTranscriptionState.startRecording('sidebar')`
- If recording: calls `SharedTranscriptionState.stopRecording()`
- Registers `onTranscript` callback → `handleBrowserTranscript(event, 'sidebar')`

**`handleBrowserTranscript(event, source)`:**
- Appends interim transcript as `<span style="color:grey">` to `#transcription-live-display`
- Appends final transcript as `<span style="color:white">` to `#transcription-live-display`
- Auto-scrolls display to bottom

**`switchTab(tabName)`:**
- Activates CSS class `.active` on `#tabs-{tabName}` button
- Shows `#{tabName}-tab` content div, hides others

**`handleFileSelect(event)` / `handleFileDrop(event)`:**
- Validates file type against allowed extensions
- POSTs to `TranscriptionConfig.getEndpoint('transcribe')` as multipart form data
- Shows progress bar during upload

**`exportTranscripts(format)`:**
- `format = 'txt'` | `'json'`
- Collects all STT transcripts from `#stt-transcript-collection` and TTS transcripts from `#tts-transcript-collection`
- Creates a Blob and triggers browser download

**`saveTTSSettings()` / `selectAudioSource(source)` / `refreshStatus()`:**
- Settings saved to `localStorage`
- Audio source change triggers `SharedTranscriptionState.startAudioPreview()` with new source
- `refreshStatus()` calls `GET /api/system/check` and updates status indicators

---

### 6.5 Streaming Container (window.TranscriptionStreaming)

**Files:**
- `UI/modules_internal/transcription/transcription-streaming-container.js`
- `UI/modules_internal/transcription/transcription-streaming-container.html`

**API:**
```javascript
window.TranscriptionStreaming.streamText(text, isFinal, confidence)
    // Appends text to #ai-transcription-text
    // isFinal=false → grey span (interim)
    // isFinal=true → white span (final)

window.TranscriptionStreaming.insertTranscript()
    // Copies all text from #ai-transcription-text to #ai-chat-input

window.TranscriptionStreaming.sendTranscript()
    // insertTranscript() + triggers send button click

window.TranscriptionStreaming.updateStatus('ready'|'recording'|'processing')
    // Updates status dot colour + animation class
    // ready → grey static
    // recording → red pulsing
    // processing → yellow pulsing
```

The streaming container is always present in the DOM (loaded in the main HTML init block at line ~28737) but only becomes visible when recording is active.

---

### 6.6 Backend: Flask Blueprint (transcription_routes.py)

**File:** `AI_infrastructure/routes/transcription_routes.py`  
**Blueprint name:** `transcription_bp`

#### `POST /api/transcribe`

```python
@transcription_bp.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    """
    Accept audio file upload, run through Whisper, return transcript.
    Accepts: file or audio field in multipart form data.
    Validates: extension (wav, mp3, webm, ogg, m4a, flac)
    Returns: {success, transcript, text, language, confidence, duration, 
               session_id, file_info}
    """
```

**Whisper lazy-loading:**
```python
_whisper_model = None
_whisper_lib_available = False

def get_whisper_model():
    global _whisper_model, _whisper_lib_available
    if _whisper_model is None:
        try:
            import whisper
            import torch
            _whisper_model = whisper.load_model("base")
            _whisper_lib_available = True
        except ImportError:
            return None
    return _whisper_model
```

**⚠️ Current Status:** `openai-whisper` and `torch` are NOT installed in the production Docker image (disabled Dec 2025 to speed up builds). The endpoint returns:
```json
{
  "success": false,
  "transcript": "[Whisper not available - install openai-whisper or enable model]",
  "error": "whisper library not available"
}
```

#### `GET /api/system/check`

```python
@transcription_bp.route('/api/system/check', methods=['GET'])
def system_check():
    return jsonify({
        "status": "ok",
        "service": "transcription",
        "available": _whisper_lib_available,
        "provider": "whisper" if _whisper_lib_available else "none",
        "model": "base",
        "supported_formats": ["wav", "mp3", "webm", "ogg", "m4a", "flac"]
    })
```

#### `POST /api/transcriptions/save` (@require_auth)

```python
# Saves to PostgreSQL: ai_infrastructure.user_transcriptions
# Fields: user_id, source_type ('browser_stt'|'whisper'|'tts'), 
#         transcript_text, confidence, language, duration_seconds,
#         word_count, model_used, metadata (JSONB)
```

#### `GET /api/transcriptions/history`

```python
# Returns paginated list of prior transcriptions for current user
# Default page size: 20
```

---

### 6.7 Database Schema

**Tables:** Defined in `AI_infrastructure/database_toolkit/schema_manager.py`

**`ai_infrastructure.user_transcriptions`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | SERIAL PK | |
| `user_id` | INT | FK to users |
| `source_type` | VARCHAR(50) | `browser_stt` / `whisper` / `tts` |
| `transcript_text` | TEXT | Full transcript |
| `confidence` | FLOAT | 0.0–1.0 (browser STT has no confidence; Whisper provides it) |
| `language` | VARCHAR(10) | Detected language code |
| `duration_seconds` | FLOAT | Recording/audio duration |
| `word_count` | INT | Computed from transcript text |
| `model_used` | VARCHAR(50) | `webkitSpeechRecognition` / `whisper-base` / `speechSynthesis` |
| `metadata` | JSONB | Additional model-specific data |
| `created_at` | TIMESTAMPTZ | |

**`ai_infrastructure.transcription_uploads`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | SERIAL PK | |
| `user_id` | INT | FK to users |
| `original_filename` | VARCHAR(255) | |
| `file_size_bytes` | BIGINT | |
| `transcript_id` | INT | FK to user_transcriptions |
| `status` | VARCHAR(50) | `pending` / `processing` / `complete` / `failed` |
| `created_at` | TIMESTAMPTZ | |

---

### 6.8 Agent Input Manager Integration

**File:** `UI/modules_internal/agents/agent-input-manager.js`  
**Function:** `toggleTranscription(agentId)` — line 269

```javascript
function toggleTranscription(agentId) {
    const state = getState(agentId);
    const micBtn = document.getElementById(`agent-mic-${agentId}`);

    if (state.isRecording) {
        // STOP
        window.SharedTranscriptionState.stopRecording();
        micBtn.classList.remove('recording');
        micBtn.querySelector('i').className = 'fas fa-microphone';
        state.isRecording = false;
    } else {
        // START — auto-expand input first
        expand(agentId);
        
        const targetInput = document.getElementById(`agent-input-${agentId}`);
        
        // START with custom routing callback
        window.SharedTranscriptionState.startRecording(null, (finalTranscript, interimTranscript) => {
            if (finalTranscript) {
                targetInput.value += finalTranscript + ' ';
                targetInput.dispatchEvent(new Event('input', { bubbles: true })); // auto-resize
            }
        })
        .then(() => {
            micBtn.classList.add('recording');
            micBtn.querySelector('i').className = 'fas fa-stop';
            state.isRecording = true;
        })
        .catch(error => {
            alert(`Could not start recording for Agent ${agentId}: ` + error.message);
        });
    }
}
```

**Key design point:** `SharedTranscriptionState.startRecording()` returns a **Promise**. The agent input manager uses `.then()` to set the recording state only after the microphone permission has been granted and `webkitSpeechRecognition` has actually started, avoiding race conditions.

---

## 7. Key Functions & Line Numbers

| Function | File | ~Line | Description |
|----------|------|-------|-------------|
| `toggleTranscriptionRecording()` | `business-ai-platform-v2.html` | 28803 | Global — Prime Chat mic button handler |
| `SharedTranscriptionState.startRecording(source, cb)` | `transcription-sidebar.js` | ~200 | Core recording start — media acquisition + STT init |
| `SharedTranscriptionState.stopRecording()` | `transcription-sidebar.js` | ~290 | Stops all streams + STT |
| `SharedTranscriptionState.startAudioPreview()` | `transcription-sidebar.js` | ~320 | Silent preview for EQ visualisation |
| `SharedTranscriptionState.startAudioLevelMonitoring(stream)` | `transcription-sidebar.js` | ~360 | Web Audio API FFT setup |
| `SharedTranscriptionState.updateAudioLevels()` | `transcription-sidebar.js` | ~395 | rAF loop — 60fps EQ bar update |
| `SharedTranscriptionState.on(event, cb)` | `transcription-sidebar.js` | ~150 | Observer registration |
| `SharedTranscriptionState.trigger(event, …args)` | `transcription-sidebar.js` | ~160 | Observer fire |
| `TranscriptionSidebarController.init()` | `transcription-sidebar.js` | ~450 | Sidebar controller init |
| `TranscriptionSidebarController.toggleRecording()` | `transcription-sidebar.js` | ~500 | Sidebar record button handler |
| `TranscriptionSidebarController.handleBrowserTranscript(ev, src)` | `transcription-sidebar.js` | ~540 | Routes interim/final to sidebar display |
| `TranscriptionSidebarController.switchTab(name)` | `transcription-sidebar.js` | ~610 | Tab switching |
| `TranscriptionSidebarController.handleFileSelect(ev)` | `transcription-sidebar.js` | ~650 | File upload → Whisper |
| `TranscriptionSidebarController.exportTranscripts(fmt)` | `transcription-sidebar.js` | ~720 | Download TXT or JSON |
| `window.TranscriptionStreaming.streamText(text,isFinal,conf)` | `transcription-streaming-container.js` | ~80 | Append text to floating overlay |
| `window.TranscriptionStreaming.insertTranscript()` | `transcription-streaming-container.js` | ~120 | Copy overlay text → #ai-chat-input |
| `window.TranscriptionStreaming.updateStatus(state)` | `transcription-streaming-container.js` | ~140 | Status dot colour |
| `toggleTranscription(agentId)` | `agent-input-manager.js` | 269 | Per-agent mic button handler |
| `transcribe_audio()` | `transcription_routes.py` | ~80 | Backend — Whisper file endpoint |
| `system_check()` | `transcription_routes.py` | ~170 | Backend — health check |

---

## 8. Current Limitations & Known Issues

### 8.1 Chrome-Only STT

`webkitSpeechRecognition` is a Chrome/Chromium-only API. Users on Firefox or Safari get no live transcription. The `stt-module.js` (original MediaRecorder + Whisper approach) was designed to solve this but is currently commented out.

### 8.2 Whisper Disabled in Production

The backend Whisper model is not installed in the Docker build (Dec 2025). File upload transcription returns an error placeholder. Re-enabling requires:
```dockerfile
RUN pip install openai-whisper torch
```
Or switching to the OpenAI Whisper API (`openai.audio.transcriptions.create`) to avoid the heavy local dependency.

### 8.3 stt-module.js Commented Out

```html
<!-- In business-ai-platform-v2.html line 28742 -->
<!-- <script src="modules_internal/transcription/stt-module.js"></script> -->
```
This module (original MediaRecorder approach) is disabled because it conflicts with `SharedTranscriptionState` — both try to acquire the microphone simultaneously. The fix would be to integrate the MediaRecorder approach into `SharedTranscriptionState` as a fallback path for non-Chrome browsers.

### 8.4 System Audio Source Experimental

`navigator.mediaDevices.getDisplayMedia()` for audio-only capture is non-standard and behaves differently across platforms:
- On macOS, screen sharing audio capture requires OS-level permission.
- On Windows, it captures the entire system audio mix.
- On Linux, support varies by browser/compositor.

The code handles this gracefully by falling back to `getUserMedia`, but the "System Audio" option in the sidebar may silently use microphone instead.

### 8.5 No Cross-Browser Confidence Scores

`webkitSpeechRecognition` does expose `event.results[i][0].confidence` but this value is often `0` or `undefined` in practice. Only Whisper provides meaningful confidence scores (0.0–1.0 per segment).

### 8.6 Language Locked to en-US for Live STT

The `browserRecognition.lang` is set to `'en-US'` by default. The Settings tab has a language override, but the wiring between the settings saved to `localStorage` and the recognition init needs to be confirmed.

### 8.7 No Server-Side Streaming

The current implementation is entirely client-side for live recording (browser STT) or a full round-trip for file uploads (Whisper). There is no WebSocket-based streaming transcription from the backend — this is what OpenAI's Realtime API now offers.

---

## 9. Platform Comparison: Anthropic Claude vs OpenAI ChatGPT vs This Implementation

### 9.1 Anthropic Claude — Audio & Transcription Capabilities

**As of May 2026, Anthropic Claude has NO native audio transcription API.**

Key facts confirmed from docs research:
- The Claude API (`/v1/messages`) accepts **text, images, PDFs, and plain text files** as input types.
- Audio files (wav, mp3, webm, etc.) are **not supported** as input to the Claude API.
- There is no `POST /v1/audio/transcriptions` equivalent on the Anthropic API.
- The Anthropic Files API (beta, April 2025) supports `PDF`, `image/*`, and `text/plain` MIME types — **no audio MIME types**.
- `docs.anthropic.com/en/docs/build-with-claude/speech-to-text` — **page does not exist** (confirmed 404).
- `docs.anthropic.com/en/docs/build-with-claude/audio` — **page does not exist** (confirmed 404).

**What Claude.ai (consumer product) has:**
- Claude.ai mobile apps (iOS/Android) have a **voice mode** introduced in 2024–2025.
- This uses the **device's native STT** (iOS Speech Recognition / Android SpeechRecognition) to convert speech to text, then sends the text to Claude — it is NOT processing audio natively.
- There is no RTT (real-time speech-to-Claude) API exposed to developers.

**Summary:** For any AI platform building a voice/transcription feature on top of the Anthropic Claude API, they must handle audio processing themselves (exactly as this platform does — using browser STT or Whisper) and send only the resulting text to Claude.

---

### 9.2 OpenAI / ChatGPT — Transcription Ecosystem (2025–2026)

OpenAI has built the most comprehensive transcription platform available as of May 2026:

#### File-Based Transcription Models

| Model | Best For | Response Formats | Notes |
|-------|----------|-----------------|-------|
| `whisper-1` | Legacy integrations, translations | `json`, `text`, `srt`, `vtt`, `verbose_json` | Word-level timestamps, 25MB limit |
| `gpt-4o-transcribe` | High-accuracy transcription | `json`, `text` | Supports `prompt` parameter, streaming |
| `gpt-4o-mini-transcribe` | Cost-effective transcription | `json`, `text` | Lower cost, streaming |
| `gpt-4o-transcribe-diarize` | Speaker identification | `json`, `text`, `diarized_json` | Up to 4 known speakers via reference clips |

**`gpt-4o-transcribe-diarize`** (new in 2025) enables:
- Speaker-labelled segments with `start`/`end` timestamps
- Up to 4 reference speaker clips for named identification
- Requires `chunking_strategy` for audio >30 seconds (`"auto"` recommended)

**Translations:** `whisper-1` only — transcribes any supported language and translates to English.

**Supported input formats:** `mp3`, `mp4`, `mpeg`, `mpga`, `m4a`, `wav`, `webm` — 25MB limit.

**Supported languages:** 57 languages with <50% word error rate (98 total, lower quality for the rest).

**Streaming Transcription (file-based):**
```python
stream = client.audio.transcriptions.create(
    model="gpt-4o-mini-transcribe",
    file=audio_file,
    stream=True
)
# Emits transcript.text.delta events + transcript.text.done
```

#### Realtime Transcription API

OpenAI's **Realtime Transcription API** (GA in 2025) enables browser-direct, low-latency live transcription:

| Model | Use Case |
|-------|----------|
| `gpt-realtime-whisper` | Live audio streaming, WebSocket/WebRTC |
| Others in Realtime API | Speech-to-speech voice agents |

**Session flow:**
```json
{ "type": "session.update",
  "session": {
    "type": "transcription",
    "audio": { "input": {
      "format": { "type": "audio/pcm", "rate": 24000 },
      "transcription": { "model": "gpt-realtime-whisper", "language": "en" }
    }}
  }
}
```

**Latency tuning** via `audio.input.transcription.delay`:
- `minimal` — most latency-sensitive (live captions)
- `low` — low-latency captions
- `medium` — balanced (default)
- `high` — accuracy priority
- `xhigh` — maximum context, highest accuracy

**Events received:**
```javascript
conversation.item.input_audio_transcription.delta   // Incremental text
conversation.item.input_audio_transcription.completed // Full final transcript
transcript.text.segment  // Speaker segment (diarize mode)
```

**ChatGPT Advanced Voice Mode:**
- Available in ChatGPT web and mobile since late 2023, expanded 2024–2025
- Speech-to-speech: user speaks → GPT-4o processes audio natively → responds in voice
- Does NOT flow through Whisper — GPT-4o audio preview handles end-to-end
- Developer API: `gpt-4o-audio-preview` with `input_audio` content type in Messages API (separate from Realtime)

---

### 9.3 This Platform vs Industry Leaders

| Feature | This Platform | Anthropic Claude API | OpenAI API |
|---------|--------------|---------------------|------------|
| **Live STT** | ✅ Browser `webkitSpeechRecognition` (Chrome only) | ❌ No audio API | ✅ `gpt-realtime-whisper` (WebSocket/WebRTC) |
| **File Upload Transcription** | ⚠️ Local Whisper (disabled in prod) | ❌ No audio API | ✅ `whisper-1`, `gpt-4o-transcribe`, `gpt-4o-mini-transcribe` |
| **Speaker Diarisation** | ⚠️ Settings toggle exists, not wired | ❌ | ✅ `gpt-4o-transcribe-diarize` |
| **Streaming Transcription** | ⚠️ Interim Results (in-browser only) | ❌ | ✅ `stream=True` on file transcription + Realtime API |
| **Language Support** | 14 selectable options (browser permitting) | ❌ | 57 languages (<50% WER), 98 total |
| **Cross-browser Support** | ❌ Chrome only for live STT | — | ✅ API-based (any browser) |
| **Confidence Scores** | ⚠️ From browser STT (often 0) | — | ✅ `logprobs`, confidence from Whisper |
| **Word Timestamps** | ⚠️ Settings toggle, not wired to browser STT | — | ✅ `whisper-1` with `timestamp_granularities[]` |
| **TTS** | ✅ Browser `speechSynthesis` | ❌ No TTS API | ✅ `/v1/audio/speech` with multiple voices |
| **Prompt Steering for STT** | ❌ | — | ✅ `prompt` parameter on `gpt-4o-transcribe` |
| **Offline Transcription** | ✅ Browser STT is local; Whisper can be local | — | ❌ API-dependent |
| **Privacy (no data to server)** | ✅ Browser STT never leaves device | — | ❌ Audio sent to OpenAI servers |
| **Cost for live STT** | ✅ Zero (browser API) | — | 💰 Realtime API is usage-billed |
| **SRT/VTT export** | ✅ Settings option present | — | ✅ `whisper-1` response formats |
| **Per-agent routing** | ✅ Custom callback per agent textarea | — | ❌ Not a platform concept |
| **Audio visualisation (EQ)** | ✅ Real-time 8-bar FFT equaliser | — | ❌ |

**Strategic observations:**

1. **OpenAI is the clear leader** in transcription APIs. The new `gpt-4o-transcribe` models significantly outperform `whisper-1` in accuracy, and `gpt-realtime-whisper` eliminates the need for browser-native STT entirely.

2. **Anthropic Claude has no audio strategy** at the API level. Any platform using Claude as its AI backbone (as this platform does) must implement its own audio pipeline. This platform has already done that correctly.

3. **This platform's biggest strengths:**
   - Zero-cost, zero-latency live transcription via browser STT
   - Privacy-preserving (audio never leaves the device for live recording)
   - Seamless routing to per-agent and Prime Chat inputs
   - Rich sidebar with audio visualisation and export tools

4. **This platform's biggest gaps vs OpenAI:**
   - No server-side Whisper API integration (disabled)
   - Chrome-only for live STT
   - No speaker diarisation connected to the backend
   - No word-level timestamps surfaced in the UI

---

## 10. Enhancement Recommendations

Ordered by impact-to-effort ratio:

### Priority 1 — Re-enable Whisper via OpenAI API (High Impact, Low Effort)

Replace the local Whisper Docker dependency with a call to `openai.audio.transcriptions.create`:

```python
# In transcription_routes.py
from openai import OpenAI

def transcribe_with_openai_api(file_path, language=None):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    with open(file_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=audio_file,
            language=language,
            response_format="json"
        )
    return transcript.text
```

This removes the Docker weight of `torch` + `whisper` while providing **better accuracy** via the `gpt-4o-transcribe` model. Org-level OpenAI API credential from the Credentials Vault would be used.

---

### Priority 2 — Cross-Browser STT via Realtime API (High Impact, Medium Effort)

The `stt-module.js` (commented out) was on the right path. Replace the current fallback path with OpenAI's Realtime Transcription API:

```javascript
// For non-Chrome browsers (when webkitSpeechRecognition is unavailable):
// 1. Open WebSocket to OpenAI Realtime API via backend proxy
// 2. Stream MediaRecorder chunks as base64 PCM
// 3. Receive transcript.text.delta events
// 4. Route to same onTranscript callbacks
```

This would make live transcription work in Firefox and Safari.

---

### Priority 3 — Speaker Diarisation Wiring (Medium Impact, Low Effort)

The Settings tab has toggle switches for `word-timestamps` and `speaker-diarisation`. Connect these to the `/api/transcribe` endpoint:

```javascript
// In handleFileSelect, read settings from localStorage:
const diarise = localStorage.getItem('transcription-speaker-diarisation') === 'true';

// In POST body:
formData.append('diarise', diarise);
```

In the backend, use `gpt-4o-transcribe-diarize` when requested.

---

### Priority 4 — Language Detection for Live STT (Medium Impact, Low Effort)

The `browserRecognition.lang` should read from the sidebar language setting:

```javascript
const lang = localStorage.getItem('transcription-language') || 'en-US';
recognition.lang = lang;
```

---

### Priority 5 — Module-Gating the Transcription Sidebar (Low Impact, Low Effort)

Per the pending architecture work (see `MODULE_VISIBILITY_ARCHITECTURE.md`), the transcription sidebar toggle button (`#transcription-sidebar-toggle`) should carry:

```html
data-module="transcription"
```

So it is only visible when the org has the `transcription` module enabled in `org_module_access`. This is already in the module catalog with `required_platforms: ['assemblyai']` — however the current implementation uses browser STT, not AssemblyAI. The catalog entry should be updated to remove the `assemblyai` requirement since basic transcription works without it.

---

### Priority 6 — SRT/VTT Export from Whisper (Low Impact, Medium Effort)

The Settings tab has `export-format` select with `srt` and `vtt` options. These formats require word-level timestamps. When using `gpt-4o-transcribe` or `whisper-1` with `timestamp_granularities: ['word']`, the backend can build SRT/VTT from `transcript.words` data and return the correct format to the frontend.

---

*End of document — Transcription Feature Analysis May 28, 2026*
