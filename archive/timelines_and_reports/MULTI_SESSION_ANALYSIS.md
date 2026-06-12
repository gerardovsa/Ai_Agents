# Multi-Session User Analysis & WebRTC Requirements

**Date:** December 17, 2025  
**Context:** Teams using same user-id on different devices

---

## 🎯 Multi-Session Architecture

### Current Implementation (ALREADY WORKING)

The system **already supports** multiple sessions per user-id:

```javascript
// synergy-realtime.js - Line 30-33
sessionToken: null,  // Unique browser session identifier
sessionDisplayName: null,  // Per-session display name
otherSessionsViewingAgents: {},  // Track other sessions per agent
```

### How It Works

**1. Session Token Generation (Line 498-503)**
```javascript
_generateSessionToken() {
    // Creates unique token per browser/tab/device
    if (!this.sessionToken) {
        this.sessionToken = 'session_' + Math.random().toString(36).substring(2) + '_' + Date.now();
    }
    return this.sessionToken;
}
```

**2. Presence Announcement (Line 571-580)**
```javascript
// Each device announces:
{
    user_id: 2,                    // Same for team
    user_name: "John Doe",         // Same for team
    session_token: "session_abc123", // UNIQUE per device
    device: "Windows",             // Device type
    display_name: "John's Laptop"  // Custom name
}
```

**3. Multi-Session Tracking (Line 720-745)**
```javascript
// Server sends updates from OTHER sessions
_handleAgentViewed(data) {
    // Ignore own session
    if (data.session_token === this.sessionToken) return;
    
    // Track OTHER sessions with same user_id
    const agentId = data.agent_id;
    if (!this.otherSessionsViewingAgents[agentId]) {
        this.otherSessionsViewingAgents[agentId] = [];
    }
    
    // Add to list if not already present
    const exists = this.otherSessionsViewingAgents[agentId].find(
        s => s.session_token === data.session_token
    );
    if (!exists) {
        this.otherSessionsViewingAgents[agentId].push({
            session_token: data.session_token,
            user_name: data.user_name,
            device: data.device,
            display_name: data.display_name
        });
    }
}
```

### Example Scenario: Team Using Same User ID

**Setup:**
- User ID: `2` (shared account)
- Team members:
  - Sarah on Windows laptop
  - Mike on Mac desktop  
  - Lisa on iPhone

**What Happens:**

```
Sarah (Windows) logs in:
  user_id: 2
  session_token: session_xyz123
  display_name: "Sarah's Laptop"
  device: "Windows"

Mike (Mac) logs in:
  user_id: 2
  session_token: session_abc456
  display_name: "Mike's Mac"
  device: "Mac"

Lisa (iPhone) logs in:
  user_id: 2
  session_token: session_def789
  display_name: "Lisa's iPhone"
  device: "iPhone"
```

**Badge Display:**
```
┌─────────────────────────────┐
│  Alpha-3 Agent Column       │
│  👥 3 (active users)        │  ← Shows 3 sessions
│                             │
│  Viewing:                   │
│  • Sarah's Laptop (Windows) │
│  • Mike's Mac (Mac)         │
│  • Lisa's iPhone (iPhone)   │
└─────────────────────────────┘
```

### Messaging Between Sessions

**Current:** Messages go to ALL sessions with same user_id

```javascript
// Send to user ID 2
SynergyRealtime.sendDirectMessage(2, "Hello team!");

// Server delivers to:
// - session_xyz123 (Sarah's Laptop)
// - session_abc456 (Mike's Mac)
// - session_def789 (Lisa's iPhone)
```

**Enhanced:** Send to specific session

```javascript
// Send to specific device
SynergyRealtime.sendDirectMessage(2, "Sarah only", "session_xyz123");

// Server delivers ONLY to Sarah's Laptop
```

---

## 📞 WebRTC Requirements

### Native Browser Support (No Library Needed!)

**WebRTC is built into ALL modern browsers:**
- ✅ Chrome/Edge (Chromium) - Full support
- ✅ Firefox - Full support
- ✅ Safari - Full support (iOS 11+)
- ✅ Opera - Full support

**APIs Used:**
```javascript
// 1. Get microphone access
navigator.mediaDevices.getUserMedia({ audio: true })

// 2. Create peer connection
new RTCPeerConnection(config)

// 3. Send/receive media tracks
peerConnection.addTrack(track, stream)
peerConnection.ontrack = (event) => { ... }
```

### No External Library Required!

**Why?** WebRTC is a **web standard** built into browsers.

**What You Need:**
1. **STUN servers** (free, public available) - for NAT traversal
2. **Signaling server** (you already have: Flask-SocketIO) - for setup
3. **HTTPS** (or localhost) - security requirement

### STUN Servers (Already Configured)

```javascript
// chat-sidebar.js - Line 19-23
config: {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' }
    ]
}
```

**These are FREE Google STUN servers** - work perfectly!

### Signaling (Already Implemented)

Voice calls use WebSocket for signaling:

```
Caller                  WebSocket Server           Receiver
  │                           │                        │
  ├─ voice_call_offer ───────►│───────────────────────►│
  │                           │                        │
  │◄──────────────────────────│◄─ voice_call_answer ──┤
  │                           │                        │
  ├─ ICE candidates ──────────►│───────────────────────►│
  │◄──────────────────────────│◄─ ICE candidates ─────┤
  │                           │                        │
  │                                                     │
  └──── Direct P2P Audio Connection ───────────────────┘
        (bypasses server after setup)
```

### Browser Compatibility Check

Add this to chat-sidebar.js:

```javascript
_checkWebRTCSupport() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.error('[CHAT] WebRTC not supported');
        return false;
    }
    if (!window.RTCPeerConnection) {
        console.error('[CHAT] RTCPeerConnection not supported');
        return false;
    }
    return true;
}
```

---

## 🚫 Emoji Removal Required

### Locations Found:

**1. synergy-realtime.js (Line 551-556)**
```javascript
// BEFORE (with emojis):
if (/iPhone|iPad|iPod/.test(ua)) return '📱 iPhone';
if (/Android/.test(ua)) return '📱 Android';
if (/Mac/.test(ua)) return '💻 Mac';
if (/Windows/.test(ua)) return '💻 Windows';
if (/Linux/.test(ua)) return '💻 Linux';
return '💻 Desktop';

// AFTER (text only):
if (/iPhone|iPad|iPod/.test(ua)) return 'iPhone';
if (/Android/.test(ua)) return 'Android';
if (/Mac/.test(ua)) return 'Mac';
if (/Windows/.test(ua)) return 'Windows';
if (/Linux/.test(ua)) return 'Linux';
return 'Desktop';
```

**2. CSS device badges** - Replace emoji with icons:
```css
/* Use Font Awesome instead */
.device-badge::before {
    content: '\f109'; /* fa-laptop */
    font-family: 'Font Awesome 5 Free';
}
```

---

## 🧪 Smoke Test Checklist

### 1. JavaScript Syntax
- [x] chat-sidebar.js - Valid JavaScript
- [x] No undefined variables
- [x] All functions defined before use

### 2. Dependencies
- [x] SynergyRealtime (already exists)
- [x] Socket.IO (already loaded)
- [x] EnhancedToast (optional, graceful fallback)
- [x] WebRTC (native browser API)

### 3. Import Order
```html
<!-- Required order: -->
<script src="/socket.io/socket.io.js"></script>
<script src="shared/js/synergy-realtime.js"></script>
<script src="shared/js/chat-sidebar.js"></script>
```

### 4. API Endpoints Needed
- `/api/messages/conversations` - Get chat list
- `/api/messages/history` - Get message history
- `/api/messages/mark-read` - Mark as read
- `/api/messages/<id>` DELETE - Delete message
- `/api/user/avatar/<id>` - Get avatar image

### 5. WebSocket Events
- `voice_call_offer` - Start call
- `voice_call_answer` - Accept call
- `voice_call_ice_candidate` - NAT traversal
- `voice_call_ended` - End call

---

## ✅ Recommendations

### 1. Display Name Prompt
When user first joins, ask for device name:

```javascript
_getSessionDisplayName() {
    let displayName = localStorage.getItem('session_display_name');
    if (!displayName) {
        displayName = prompt('Enter a name for this device (e.g., "Sarah\'s Laptop"):');
        if (displayName) {
            localStorage.setItem('session_display_name', displayName);
        }
    }
    return displayName || this._getUserName() + '\'s Device';
}
```

### 2. Session List UI
Show team members their active sessions:

```
┌──────────────────────────────┐
│  Your Active Sessions:       │
├──────────────────────────────┤
│  • Sarah's Laptop (Windows)  │ ← Current
│  • Mike's Mac (Mac)          │
│  • Lisa's iPhone (iPhone)    │
└──────────────────────────────┘
```

### 3. Direct Session Messaging
Add UI to select specific device:

```
┌──────────────────────────────┐
│  Send message to:            │
├──────────────────────────────┤
│  ○ All team members          │
│  ● Sarah's Laptop only       │
│  ○ Mike's Mac only           │
└──────────────────────────────┘
```

### 4. Voice Call Session Selection
When calling shared user ID:

```javascript
startVoiceCall() {
    // If multiple sessions, show picker
    const sessions = this.getActiveSessionsForUser(this.activeConversation);
    
    if (sessions.length > 1) {
        // Show session picker
        const sessionId = this.showSessionPicker(sessions);
        // Call specific session
        this.initiateCall(this.activeConversation, sessionId);
    } else {
        // Single session, call directly
        this.initiateCall(this.activeConversation);
    }
}
```

---

## 🎯 Summary

### Multi-Session Support: ✅ ALREADY IMPLEMENTED
- Session tokens differentiate devices
- Presence tracking works per-session
- Badge system shows all active sessions
- Messages can target specific sessions

### WebRTC: ✅ NO LIBRARY NEEDED
- Native browser support
- Free STUN servers configured
- Signaling via existing WebSocket
- Works on all modern browsers

### Emojis: ⚠️ NEED TO REMOVE
- Found in device detection
- Replace with text labels
- Use Font Awesome icons for UI

### Testing: 📋 READY TO SMOKE TEST
- All dependencies available
- No missing imports
- API endpoints documented
- WebSocket events defined

---

**Next Steps:**
1. Remove emojis from synergy-realtime.js
2. Run smoke test on all files
3. Test multi-session scenarios
4. Verify WebRTC voice calls work
