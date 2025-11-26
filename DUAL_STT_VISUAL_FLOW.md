# 🎯 Dual-Mode STT Visual Flow Diagram

## User Experience Timeline

```
TIME →
0s     0.3s          1.0s              2.5s              5.0s
│      │             │                 │                 │
USER   INTERIM       FINAL             WHISPER           COMPLETE
SPEAKS TEXT          (Browser STT)     CORRECTION        
│      │             │                 │                 │
│      ↓             ↓                 ↓                 ↓
│    "Hello..."▋   "Hello world"    "Hello world"     (stable)
│    (gray,        (green,           (purple dot,
│     italic,       solid,            high quality)
│     pulsing)      85% conf)
```

---

## Architecture Layers

```
┌──────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Transcription Streaming Container                      │  │
│  │  - Shows interim text (gray, italic, pulsing)          │  │
│  │  - Shows final text (colored by confidence)            │  │
│  │  - Shows source indicators (dots)                      │  │
│  │  - Auto-scrolls, copy/insert/send buttons             │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                            ↑
                            │ streamText(text, isFinal, confidence, source)
                            │
┌──────────────────────────────────────────────────────────────┐
│                  DUAL-MODE STT CONTROLLER                     │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  STTModuleDual Class                                   │  │
│  │                                                         │  │
│  │  ┌──────────────────────┐  ┌──────────────────────┐  │  │
│  │  │ Browser STT Path     │  │ Whisper Backend Path │  │  │
│  │  │ • webkitSpeech...    │  │ • MediaRecorder      │  │  │
│  │  │ • recognition.onr... │  │ • Chunk capture      │  │  │
│  │  │ • Instant interim    │  │ • Backend upload     │  │  │
│  │  │ • 0.1-0.5s delay    │  │ • 1-5s delay        │  │  │
│  │  └──────────────────────┘  └──────────────────────┘  │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                            ↑
                            │ getUserMedia({audio: true})
                            │
┌──────────────────────────────────────────────────────────────┐
│                    BROWSER AUDIO APIs                         │
│  ┌─────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │ Navigator       │  │ MediaRecorder│  │ SpeechRecog...  │ │
│  │ .mediaDevices   │  │ .start()     │  │ .start()        │ │
│  │ .getUserMedia() │  │ .ondataavail │  │ .onresult       │ │
│  └─────────────────┘  └──────────────┘  └─────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                            ↑
                            │ Hardware audio stream
                            │
┌──────────────────────────────────────────────────────────────┐
│                      MICROPHONE HARDWARE                      │
└──────────────────────────────────────────────────────────────┘
```

---

## Data Flow Sequence

### Step 1: Recording Start

```
┌─────────────┐
│ User clicks │
│ microphone  │
│ button      │
└──────┬──────┘
       │
       ↓
┌────────────────────────────────────────┐
│ STTModuleDual.startRecording()        │
│ • Request microphone permission       │
│ • Get audio stream                    │
└──────┬─────────────────────────────────┘
       │
       ├───────────────────────┬─────────────────────────┐
       │                       │                         │
       ↓                       ↓                         ↓
┌──────────────────┐  ┌───────────────────┐  ┌──────────────────┐
│ Browser STT      │  │ MediaRecorder     │  │ UI Update        │
│ recognition.     │  │ mediaRecorder.    │  │ • Button red     │
│ start()          │  │ start(1000)       │  │ • Status         │
│                  │  │                   │  │   "Recording..." │
└──────────────────┘  └───────────────────┘  └──────────────────┘
```

---

### Step 2: User Speaking (Instant Streaming)

```
┌──────────────┐
│ User speaks: │
│ "Hello..."   │
└──────┬───────┘
       │
       ↓ (0.3 seconds)
┌─────────────────────────────────────┐
│ Browser STT recognition.onresult    │
│ • event.results[0].isFinal = false  │
│ • transcript = "Hello..."           │
└──────┬──────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│ onInterimTranscript({               │
│   transcript: "Hello...",           │
│   isFinal: false,                   │
│   confidence: 0.85,                 │
│   source: 'browser-speech-api'      │
│ })                                  │
└──────┬──────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│ TranscriptionStreaming.streamText(  │
│   "Hello...",                       │
│   false,  // interim                │
│   0.85,                             │
│   'browser-stt'                     │
│ )                                   │
└──────┬──────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│ DOM Update:                         │
│ <span class="ai-transcript-interim" │
│       data-source="browser-stt">    │
│   Hello...▋                         │
│ </span>                             │
└─────────────────────────────────────┘

USER SEES: 💭 "Hello..."▋ (gray, italic, pulsing, typing cursor)
```

---

### Step 3: Final Browser STT Result

```
┌──────────────┐
│ User pauses  │
│ after word   │
└──────┬───────┘
       │
       ↓ (1.0 seconds from start)
┌─────────────────────────────────────┐
│ Browser STT recognition.onresult    │
│ • event.results[0].isFinal = true   │
│ • transcript = "Hello world"        │
│ • confidence = 0.92                 │
└──────┬──────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│ onTranscript({                      │
│   transcript: "Hello world",        │
│   isFinal: true,                    │
│   confidence: 0.92,                 │
│   source: 'browser-speech-api'      │
│ })                                  │
└──────┬──────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│ TranscriptionStreaming.streamText(  │
│   "Hello world",                    │
│   true,  // final                   │
│   'high', // 0.92 → high            │
│   'browser-stt'                     │
│ )                                   │
└──────┬──────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│ DOM Update:                         │
│ • Remove interim span               │
│ • Add final span:                   │
│ <span class="ai-transcript-final"   │
│       data-source="browser-stt"     │
│       data-confidence="high">       │
│   Hello world                       │
│ </span>                             │
└─────────────────────────────────────┘

USER SEES: ✅ ● "Hello world" (green text, blue dot)
```

---

### Step 4: Whisper Backend Processing (Parallel)

```
MEANWHILE (started at 0s, completes at 2.5s):

┌──────────────────────────────────────┐
│ MediaRecorder.ondataavailable        │
│ • event.data.size = 48000 bytes      │
│ • blob = WebM audio chunk            │
└──────┬───────────────────────────────┘
       │
       ↓ (1.0 seconds)
┌──────────────────────────────────────┐
│ sendChunkToWhisper(blob)             │
│ • Create FormData with audio file    │
│ • POST to /api/transcribe            │
└──────┬───────────────────────────────┘
       │
       ↓ HTTP POST (1.5 seconds processing)
┌──────────────────────────────────────┐
│ Flask Backend                        │
│ • whisper_model.transcribe()         │
│ • result = { transcript: "Hello..." }│
└──────┬───────────────────────────────┘
       │
       ↓ JSON response
┌──────────────────────────────────────┐
│ onTranscript({                       │
│   transcript: "Hello world",         │
│   isFinal: true,                     │
│   confidence: 1.0,                   │
│   source: 'whisper-backend'          │
│ })                                   │
└──────┬───────────────────────────────┘
       │
       ↓
┌──────────────────────────────────────┐
│ TranscriptionStreaming.streamText(   │
│   "Hello world",                     │
│   true,                              │
│   'high',                            │
│   'whisper'                          │
│ )                                    │
└──────┬───────────────────────────────┘
       │
       ↓
┌──────────────────────────────────────┐
│ DOM Update:                          │
│ <span class="ai-transcript-final"    │
│       data-source="whisper"          │
│       data-confidence="high">        │
│   Hello world                        │
│ </span>                              │
└──────────────────────────────────────┘

USER SEES: ✅ ● "Hello world" (green text, purple dot)
```

---

## Confidence Color Decision Tree

```
                    ┌─────────────────┐
                    │ Transcript Text │
                    │ Received        │
                    └────────┬────────┘
                             │
                             ↓
                    ┌─────────────────┐
                    │ Check Source    │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │                             │
              ↓                             ↓
     ┌─────────────────┐          ┌─────────────────┐
     │ Browser STT     │          │ Whisper Backend │
     │ (has confidence)│          │ (no confidence) │
     └────────┬────────┘          └────────┬────────┘
              │                             │
              ↓                             ↓
     ┌─────────────────┐          ┌─────────────────┐
     │ Check confidence│          │ Default: HIGH   │
     │ value (0-1)     │          │ (Whisper is     │
     └────────┬────────┘          │  always good)   │
              │                   └────────┬────────┘
              │                             │
      ┌───────┼───────┬──────────┐         │
      │       │       │          │         │
      ↓       ↓       ↓          ↓         ↓
   >=0.8   0.5-0.79  <0.5    unknown   always
      │       │       │          │         │
      ↓       ↓       ↓          ↓         ↓
   ┌────┐ ┌────┐ ┌────┐  ┌─────────┐ ┌────┐
   │HIGH│ │MED │ │LOW │  │ UNKNOWN │ │HIGH│
   │    │ │    │ │    │  │         │ │    │
   │🟢  │ │🟠  │ │🔴  │  │  ⚪     │ │🟢  │
   └────┘ └────┘ └────┘  └─────────┘ └────┘
     │       │       │          │         │
     ↓       ↓       ↓          ↓         ↓
 #3fb950 #f0883e #f85149   #e6edf3   #3fb950
  GREEN   ORANGE   RED      WHITE     GREEN
```

---

## CSS Styling Decision Tree

```
                ┌──────────────────┐
                │ Text Element     │
                │ Created in DOM   │
                └────────┬─────────┘
                         │
                         ↓
                ┌──────────────────┐
                │ Check isFinal    │
                └────────┬─────────┘
                         │
              ┌──────────┼──────────┐
              │                     │
              ↓                     ↓
     ┌────────────────┐    ┌────────────────┐
     │ isFinal=false  │    │ isFinal=true   │
     │ (INTERIM)      │    │ (FINAL)        │
     └────────┬───────┘    └────────┬───────┘
              │                     │
              ↓                     ↓
     ┌────────────────┐    ┌────────────────┐
     │ .ai-transcript-│    │ .ai-transcript-│
     │ interim        │    │ final          │
     │                │    │                │
     │ • Gray #8b949e │    │ data-source=   │
     │ • Italic       │    │ data-confidence│
     │ • Pulse anim   │    └────────┬───────┘
     │ • Cursor ▋     │             │
     └────────────────┘      ┌──────┴───────┐
                             │              │
                             ↓              ↓
                    ┌──────────────┐ ┌───────────┐
                    │ Confidence   │ │ Source    │
                    │ Color        │ │ Indicator │
                    └──────┬───────┘ └─────┬─────┘
                           │               │
                    ┌──────┴───────┐       │
                    │ high → green │       │
                    │ med → orange │       │
                    │ low → red    │       │
                    └──────────────┘       │
                                          │
                                   ┌──────┴─────┐
                                   │ browser-stt│
                                   │ → blue dot │
                                   │ whisper    │
                                   │ → purple   │
                                   └────────────┘
```

---

## State Machine Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    STTModuleDual States                      │
└─────────────────────────────────────────────────────────────┘

                    ┌──────────┐
                    │  IDLE    │
                    │ ready to │
                    │  record  │
                    └────┬─────┘
                         │
                         │ User clicks microphone
                         ↓
                    ┌──────────┐
                    │ STARTING │
                    │ request  │
                    │  mic     │
                    └────┬─────┘
                         │
                         │ getUserMedia() success
                         ↓
                    ┌──────────┐
                    │RECORDING │
                    │ • Browser│
                    │   STT    │
                    │ • Media  │
                    │   Rec    │
                    └────┬─────┘
                         │
              ┌──────────┼──────────┐
              │                     │
              ↓                     ↓
     ┌────────────────┐    ┌────────────────┐
     │ INTERIM_UPDATE │    │ CHUNK_SENDING  │
     │ (Browser STT   │    │ (Whisper API)  │
     │  onresult)     │    │                │
     └────────┬───────┘    └────────┬───────┘
              │                     │
              │                     ↓
              │            ┌────────────────┐
              │            │ CHUNK_         │
              │            │ PROCESSING     │
              │            │ (Backend)      │
              │            └────────┬───────┘
              │                     │
              │                     ↓
              │            ┌────────────────┐
              │            │ CHUNK_         │
              │            │ COMPLETE       │
              │            └────────┬───────┘
              │                     │
              └─────────┬───────────┘
                        │
                        │ User clicks stop
                        ↓
                    ┌──────────┐
                    │ STOPPING │
                    │ cleanup  │
                    └────┬─────┘
                         │
                         ↓
                    ┌──────────┐
                    │  IDLE    │
                    └──────────┘
```

---

## Error Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Error Handling Flow                       │
└─────────────────────────────────────────────────────────────┘

                    ┌──────────┐
                    │ Operation│
                    │ Attempted│
                    └────┬─────┘
                         │
                         ↓
                    ┌──────────┐
                    │  Error?  │
                    └────┬─────┘
                         │
              ┌──────────┼──────────┐
              │                     │
              ↓ NO                  ↓ YES
         ┌─────────┐          ┌──────────┐
         │ Success │          │ Check    │
         │ Continue│          │ Error    │
         └─────────┘          │ Type     │
                              └────┬─────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ↓                    ↓                    ↓
     ┌────────────────┐   ┌────────────────┐  ┌────────────────┐
     │ Browser STT    │   │ MediaRecorder  │  │ Whisper API    │
     │ Error          │   │ Error          │  │ Error          │
     └────────┬───────┘   └────────┬───────┘  └────────┬───────┘
              │                    │                    │
              ↓                    ↓                    ↓
     ┌────────────────┐   ┌────────────────┐  ┌────────────────┐
     │ audio-capture? │   │ NotAllowed?    │  │ HTTP 500+?     │
     │ no-speech?     │   │ NotFound?      │  │ Network fail?  │
     └────────┬───────┘   └────────┬───────┘  └────────┬───────┘
              │                    │                    │
              ↓                    ↓                    ↓
     ┌────────────────┐   ┌────────────────┐  ┌────────────────┐
     │ NON-FATAL      │   │ FATAL          │  │ RETRYABLE      │
     │ Continue with  │   │ Show error     │  │ Retry with     │
     │ Whisper only   │   │ Stop recording │  │ backoff        │
     └────────────────┘   └────────────────┘  └────────┬───────┘
                                                        │
                                                        ↓
                                               ┌────────────────┐
                                               │ Max retries?   │
                                               └────────┬───────┘
                                                        │
                                                 ┌──────┴──────┐
                                                 │             │
                                                 ↓ NO          ↓ YES
                                            ┌─────────┐  ┌─────────┐
                                            │ Retry   │  │ Give up │
                                            └─────────┘  └─────────┘
```

---

## Component Interaction Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                       USER INTERFACE LAYER                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ business-ai-platform-v2.html                              │  │
│  │ • Microphone button                                       │  │
│  │ • Chat input field                                        │  │
│  │ • Transcription streaming container                       │  │
│  └────────────────────────────┬─────────────────────────────┘  │
└────────────────────────────────┼────────────────────────────────┘
                                 │
                                 │ initializeSTTModule()
                                 ↓
┌────────────────────────────────────────────────────────────────┐
│                    CONTROLLER LAYER                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STTModuleDual (stt-module-dual.js)                       │  │
│  │ • Manages both STT paths                                 │  │
│  │ • Coordinates recording lifecycle                        │  │
│  │ • Emits callbacks (onInterimTranscript, onTranscript)    │  │
│  └───────┬──────────────────────┬───────────────────────────┘  │
└──────────┼──────────────────────┼────────────────────────────────┘
           │                      │
           │                      └──────────────────┐
           ↓                                         ↓
┌──────────────────────────┐            ┌──────────────────────────┐
│ BROWSER STT PATH         │            │ WHISPER BACKEND PATH     │
│ ┌──────────────────────┐ │            │ ┌──────────────────────┐│
│ │ webkitSpeechRecog... ││            │ │ MediaRecorder        ││
│ │ • recognition.start()││            │ │ • start(1000)        ││
│ │ • onresult handler   ││            │ │ • ondataavailable    ││
│ └──────────────────────┘ │            │ └──────────────────────┘│
└──────────┬───────────────┘            └──────────┬───────────────┘
           │                                       │
           │ onInterimTranscript({...})           │ sendChunkToWhisper(blob)
           │ onTranscript({...})                  │
           │                                      │
           └──────────────────┬───────────────────┘
                              │
                              ↓
┌────────────────────────────────────────────────────────────────┐
│                     DISPLAY LAYER                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ TranscriptionStreamingController                          │  │
│  │ (transcription-streaming-container.js)                    │  │
│  │ • streamText(text, isFinal, confidence, source)           │  │
│  │ • Updates DOM with styled spans                           │  │
│  │ • Manages interim/final text display                      │  │
│  └──────────────────────────┬───────────────────────────────┘  │
└────────────────────────────────┼────────────────────────────────┘
                                 │
                                 ↓
┌────────────────────────────────────────────────────────────────┐
│                      DOM/CSS LAYER                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ #ai-transcription-text container                          │  │
│  │ • .ai-transcript-interim (gray, italic, pulsing)          │  │
│  │ • .ai-transcript-final (confidence colored, source dot)   │  │
│  │ • CSS animations and hover effects                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## File Dependency Graph

```
business-ai-platform-v2.html
    │
    ├─→ modules/transcription/stt-module-dual.js
    │   │
    │   ├─→ Browser Web Speech API (webkitSpeechRecognition)
    │   ├─→ MediaRecorder API
    │   └─→ Fetch API (/api/transcribe endpoint)
    │
    ├─→ modules/transcription/transcription-streaming-container.js
    │   │
    │   └─→ DOM manipulation (createElement, appendChild, etc.)
    │
    ├─→ modules/transcription/transcription-streaming-container.css
    │   │
    │   ├─→ .ai-transcript-interim styles
    │   ├─→ .ai-transcript-final styles
    │   ├─→ Confidence color variables
    │   └─→ Animation keyframes
    │
    └─→ modules/transcription/config.js
        │
        └─→ API endpoint configuration
```

---

**Last Updated:** 2025-11-27  
**Purpose:** Visual reference for dual-mode STT architecture  
**For:** Developers and technical documentation
