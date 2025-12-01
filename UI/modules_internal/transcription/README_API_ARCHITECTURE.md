# Transcription Module - API Design Architecture

## Overview
Centralized, environment-aware transcription system with **zero hardcoded URLs**. Automatically detects local vs production environments and provides dynamic API endpoint resolution.

---

## Architecture Principles (API Design Architect Standards)

### ✅ **No Hardcoded URLs**
- All endpoints managed through `TranscriptionConfig` singleton
- Environment auto-detection (localhost vs Render)
- User-configurable overrides via localStorage

### ✅ **Environment Agnostic**
```javascript
// Uses global window.API_BASE_URL (set in business-ai-platform-v2.html)
localhost:* → http://localhost:5001
render.com → https://ai-agents-backend-singapore.onrender.com
custom → User-defined via localStorage
```

### ✅ **Consistent with Other Modules**
- Uses same `window.API_BASE_URL` as InHouse Kanban, Thread Manager, Vector Database
- No duplicate environment detection logic
- Single source of truth for all API endpoints

### ✅ **Centralized Configuration**
- **Single source of truth**: `config.js`
- **Dynamic endpoint resolution**: `getEndpoint('transcribe')`
- **Runtime reconfiguration**: No code changes needed for deployment

---

## File Structure

```
UI/modules/transcription/
├── config.js                     ← 🔧 CENTRALIZED CONFIG (load first!)
├── stt-module.js                 ← Speech-to-Text module
├── tts-module.js                 ← Text-to-Speech module
├── transcription-sidebar.js      ← Sidebar controller
├── transcription-sidebar.html    ← Settings UI
├── transcription-streaming-container.js
├── diagnostic.js
└── README_API_ARCHITECTURE.md    ← This file
```

---

## Configuration System (`config.js`)

### Core Features

**1. Uses Global API_BASE_URL**
```javascript
// Inherits environment detection from business-ai-platform-v2.html
this.globalApiBaseUrl = window.API_BASE_URL || 'http://localhost:5001';

// Production: https://ai-agents-backend-singapore.onrender.com (auto-detected)
// Local: http://localhost:5001 (auto-detected)
// Same detection logic as InHouse Kanban, Thread Manager, Vector Database
```

**2. Endpoint Management**
```javascript
this.endpoints = {
    transcribe: '/api/transcribe',
    systemCheck: '/api/system/check',
    transcribeV1: '/api/v1/transcribe',  // Legacy
    systemCheckV1: '/api/v1/system/check' // Legacy
};
```

**3. Custom Overrides**
```javascript
// Set custom backend URL (persists in localStorage)
TranscriptionConfig.setCustomBackendUrl('https://my-backend.onrender.com');

// Reset to auto-detection
TranscriptionConfig.setCustomBackendUrl(null);
```

---

## Usage Patterns

### **1. In Modules (stt-module.js, transcription-sidebar.js)**

**Before (❌ Hardcoded):**
```javascript
whisperEndpoint: 'http://localhost:3001/api/v1/transcribe'  // BAD!
```

**After (✅ Dynamic):**
```javascript
whisperEndpoint: window.TranscriptionConfig ? 
    window.TranscriptionConfig.getEndpoint('transcribe') : 
    'http://localhost:5001/api/transcribe'  // Fallback only
```

### **2. In HTML (business-ai-platform-v2.html)**

**Load order is CRITICAL:**
```html
<!-- Load config.js FIRST -->
<script src="modules/transcription/config.js"></script>
<script src="modules/transcription/stt-module.js"></script>
<script src="modules/transcription/tts-module.js"></script>
<script src="modules/transcription/transcription-sidebar.js"></script>
```

### **3. In UI Settings**

**Auto-detect button:**
```html
<button onclick="TranscriptionSidebar.detectBackendUrl()">
    🔄 Auto-detect
</button>
```

**Test connection button:**
```html
<button onclick="TranscriptionSidebar.testBackendConnection()">
    🧪 Test
</button>
```

---

## Deployment Guide

### **Local Development (localhost:5001)**

1. Start Flask backend:
   ```powershell
   cd C:\Users\gpoli\GIT\AI_agents\AI_infrastructure
   python flask_app.py
   ```

2. Open UI (via web server):
   ```powershell
   cd C:\Users\gpoli\GIT\AI_agents\UI
   python -m http.server 8000
   ```

3. Navigate to: `http://localhost:8000/business-ai-platform-v2.html`

4. System auto-detects: `http://localhost:5001/api/transcribe`

---

### **Production (Render.com)**

1. **No configuration needed in config.js!** 
   - Uses `window.API_BASE_URL` which is already configured in `business-ai-platform-v2.html`
   - Production URL: `https://ai-agents-backend-singapore.onrender.com`

2. Deploy to Render:
   - Backend Flask app → Render web service
   - Frontend HTML → Static site or served via Flask

3. System auto-detects: `https://ai-agents-backend-singapore.onrender.com/api/transcribe`

**Note:** To change production URL, edit `business-ai-platform-v2.html` line 300 (not config.js)

---

### **Custom Backend (Any URL)**

**Via Console (temporary):**
```javascript
setTranscriptionBackend('https://custom-backend.com');
```

**Via UI (persistent):**
1. Open Transcription Settings sidebar
2. Enter custom URL in "Whisper Backend URL" field
3. Click "Save Settings"
4. Stored in localStorage, persists across sessions

---

## Global Console Commands

**Check current configuration:**
```javascript
getTranscriptionConfig()
// Returns:
// {
//   environment: 'local',
//   baseUrl: 'http://localhost:5001',
//   endpoints: {...},
//   customUrl: null,
//   productionUrl: 'https://your-app.onrender.com',
//   localUrl: 'http://localhost:5001'
// }
```

**Set custom backend:**
```javascript
setTranscriptionBackend('https://my-backend.onrender.com')
```

**Test connection:**
```javascript
await testTranscriptionBackend()
// Logs: ✅ Backend is reachable
// Or: ❌ Backend unreachable
```

**Reset to defaults:**
```javascript
TranscriptionConfig.reset()
```

---

## API Endpoint Structure

### **Flask Backend (port 5001)**

**Required endpoints:**

**1. Transcribe Audio**
```
POST /api/transcribe
Content-Type: multipart/form-data

Body:
- audio: audio/webm blob
- chunk_id: string (UUID)
- timestamp: integer
- session_id: string (optional)

Response:
{
  "success": true,
  "transcript": "Hello world",
  "chunk_id": "abc123",
  "confidence": 0.95
}
```

**2. System Health Check**
```
GET /api/system/check

Response:
{
  "status": "ok",
  "service": "transcription",
  "version": "1.0.0"
}
```

**3. Legacy V1 Endpoints (optional)**
```
POST /api/v1/transcribe
GET /api/v1/system/check
```

---

## Migration Checklist

### From Hardcoded URLs → Config System

- [ ] Add `config.js` to project
- [ ] Load `config.js` BEFORE other transcription modules
- [ ] Update `stt-module.js` to use `TranscriptionConfig`
- [ ] Update `transcription-sidebar.js` to use `TranscriptionConfig`
- [ ] Update `diagnostic.js` messages
- [ ] Update HTML input field to show auto-detected URL
- [ ] Add auto-detect button to UI
- [ ] Add test connection button to UI
- [ ] Set production URL in `config.js` before deployment
- [ ] Test local environment (localhost:5001)
- [ ] Test production environment (Render)
- [ ] Verify localStorage persistence

---

## Troubleshooting

### **Problem: "Backend unreachable" error**

**Solution 1: Check backend is running**
```powershell
# Local: Flask should be on port 5001
curl http://localhost:5001/api/system/check
```

**Solution 2: Check detected URL**
```javascript
// In browser console:
getTranscriptionConfig()
// Verify baseUrl matches your backend
```

**Solution 3: Override with custom URL**
```javascript
setTranscriptionBackend('http://localhost:5001')
// Or use UI: Settings → Whisper Backend URL → Enter URL → Save
```

---

### **Problem: "TranscriptionConfig not loaded"**

**Solution: Check script load order**
```html
<!-- config.js MUST load first -->
<script src="modules/transcription/config.js"></script>
<script src="modules/transcription/stt-module.js"></script>
```

**Verify in console:**
```javascript
window.TranscriptionConfig  // Should be defined
```

---

### **Problem: CORS errors**

**Solution 1: Open via web server (not file://)**
```powershell
# Use Python HTTP server
python -m http.server 8000

# Or VS Code Live Server extension
# Right-click HTML → "Open with Live Server"
```

**Solution 2: Configure Flask CORS**
```python
# In flask_app.py
from flask_cors import CORS
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

---

## Benefits of This Architecture

✅ **Zero hardcoded URLs** - All endpoints centralized  
✅ **Environment agnostic** - Works on local + Render + custom  
✅ **User configurable** - Override via UI or console  
✅ **Persistent config** - localStorage caching  
✅ **Debug friendly** - Console commands for inspection  
✅ **Production ready** - Single config change for deployment  
✅ **Backwards compatible** - Fallback URLs if config fails  

---

## Version History

**v2.0 (2025-11-26)** - Centralized config system  
- Created `config.js` with environment detection
- Removed all hardcoded URLs from modules
- Added UI controls for backend configuration
- Added global console commands
- Production deployment ready

**v1.0 (2025-01-XX)** - Initial implementation  
- Hardcoded localhost:3001 URLs
- No environment detection
- Manual URL changes required for deployment

---

## Contact & Support

**API Design Questions:**  
Reference: `.github/prompts/API Design Architect.prompt.md`

**Configuration Issues:**  
Check: `getTranscriptionConfig()` in browser console

**Backend Setup:**  
See: `AI_infrastructure/flask_app.py` (Flask backend)

---

**Last Updated:** November 26, 2025  
**Status:** ✅ Production Ready  
**API Version:** v2.0
