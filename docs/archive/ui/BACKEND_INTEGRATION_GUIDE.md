# 🔗 Backend Integration Guide - Business AI Platform

## 📋 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Backend Services](#backend-services)
3. [API Endpoints](#api-endpoints)
4. [Authentication Flow](#authentication-flow)
5. [Tool Integration](#tool-integration)
6. [Implementation Steps](#implementation-steps)

---

## 🏗️ Architecture Overview

### Backend Services

```
┌─────────────────────────────────────────────────────────────┐
│                  Business AI Platform UI                     │
│                 (business-ai-platform-v2.html)              │
│                     Port: Browser (file://)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP/REST APIs
                         │
          ┌──────────────┴──────────────┐
          │                             │
┌─────────▼──────────┐      ┌──────────▼─────────────┐
│  Flask Main App    │      │ VSA Automation Agent   │
│  Port: 4000        │      │ Port: 5300             │
│  (AI Core)         │      │ (Transcript Agent)     │
└─────────┬──────────┘      └──────────┬─────────────┘
          │                             │
          │                             │
    ┌─────▼──────┐              ┌──────▼─────┐
    │ 281 Tools  │              │ 25 Tools   │
    │ 19 Platforms│              │ Workflow   │
    └────────────┘              └────────────┘
```

### Port Allocation

| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| **Business AI Platform** | 4000 | Main Flask API server | ✅ Active |
| **VSA Automation Agent** | 5300 | Transcript processing agent | ✅ Active |
| **Render Backend** | - | Production deployment | 🌐 Cloud |

---

## 🚀 Backend Services

### 1. **Flask Main App** (Port 4000)
- **Location**: `C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\flask_app.py`
- **Purpose**: Primary API server for Business AI Platform
- **Features**:
  - Multi-provider AI (Anthropic, OpenAI, DeepSeek)
  - Unified session management
  - 281 tools across 19 platforms
  - Thread/conversation storage
  - Export functionality

**Key Routes**:
```python
# Agent Routes (/api/agent/*)
POST   /api/agent/chat          # Chat with AI (streaming)
POST   /api/agent/stream        # SSE streaming
GET    /api/agent/tools         # List available tools
POST   /api/agent/upload        # Upload files
GET    /api/agent/session/:id   # Get session details

# Thread Routes (/api/threads/*)
GET    /api/threads             # List all threads
POST   /api/threads             # Create new thread
GET    /api/threads/:id         # Get specific thread
DELETE /api/threads/:id         # Delete thread

# Export Routes (/api/export/*)
POST   /api/export/txt          # Export as text
POST   /api/export/pdf          # Export as PDF
POST   /api/export/markdown     # Export as markdown

# Health Check
GET    /health                  # Service health status
```

### 2. **VSA Automation Agent** (Port 5300)
- **Location**: `C:\Users\gpoli\GIT\AI_agents\vsa_automation_agent.py`
- **Purpose**: Specialized transcript processing automation
- **Features**:
  - Claude 4 Extended Thinking
  - Multi-client database management
  - Google Workspace integration
  - Automated workflows
  - Real-time monitoring

**Key Routes**:
```python
# Agent Routes
POST   /api/agent/chat          # Chat with agent (extended thinking)
GET    /api/agent/session/:id   # Session details
GET    /api/agent/sessions      # All sessions

# Client Management
GET    /api/clients             # All configured clients
GET    /api/clients/:id         # Client details
POST   /api/clients             # Add new client
POST   /api/clients/:id/test    # Test client connection

# Processing
POST   /api/processing/trigger  # Trigger automated processing
GET    /api/processing/status   # Processing status
GET    /api/processing/monitor  # Real-time monitoring

# Google Integration
GET    /api/google/drive/folders          # List Drive folders
GET    /api/google/drive/files/:id        # List files
POST   /api/google/drive/import/:id       # Import file
POST   /api/google/sheets/import          # Import from Sheets
POST   /api/google/gmail/monitor          # Monitor Gmail

# Notifications
POST   /api/notifications/send   # Send notification
POST   /api/notifications/setup  # Setup notification channels

# System
GET    /api/health              # Health check
GET    /api/tools               # Available tools
```

---

## 🔧 API Endpoints

### Health Check
```javascript
// Check backend health
const response = await fetch('http://localhost:4000/health');
const data = await response.json();

// Expected response:
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2025-10-26T12:00:00Z",
  "services": {
    "ai_client": "connected",
    "session_manager": "active",
    "database": "connected"
  }
}
```

### Chat with AI Agent
```javascript
// Standard chat (Port 4000)
const response = await fetch('http://localhost:4000/api/agent/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "Show me today's sales",
    session_id: "session_123",
    context: {
      tab: "sales",
      platform: "business_ai_platform"
    }
  })
});
const data = await response.json();

// Streaming chat (SSE)
const eventSource = new EventSource(
  `http://localhost:4000/api/agent/stream?session_id=session_123&message=${encodeURIComponent(message)}`
);

eventSource.addEventListener('content_block_delta', (e) => {
  const data = JSON.parse(e.data);
  console.log(data.text); // Stream text chunks
});
```

### Get Available Tools
```javascript
// List all tools
const response = await fetch('http://localhost:4000/api/agent/tools');
const data = await response.json();

// Expected response:
{
  "success": true,
  "tools": [
    {
      "name": "slack_send_message",
      "platform": "Slack",
      "description": "Send message to Slack channel",
      "category": "communication"
    },
    {
      "name": "woocommerce_get_orders",
      "platform": "WooCommerce",
      "description": "Fetch WooCommerce orders",
      "category": "e-commerce"
    },
    // ... 279 more tools
  ],
  "total": 281,
  "platforms": 19
}
```

---

## 🔐 Authentication Flow

### 1. **Google OAuth Integration**
```javascript
// Location: google-auth.js (already in project root)
import { GoogleAuth } from './google-auth.js';

const googleAuth = new GoogleAuth();

// Authorize
const authResult = await googleAuth.authorize();

// Get access token
const token = await googleAuth.getAccessToken();

// Use token in API calls
const response = await fetch('http://localhost:4000/api/google/drive/folders', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### 2. **Session Management**
```javascript
// Generate session ID
function generateSessionId() {
  return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Store in AppState
AppState.sessionId = generateSessionId();

// Use in all API calls
const response = await fetch('http://localhost:4000/api/agent/chat', {
  method: 'POST',
  body: JSON.stringify({
    message: "...",
    session_id: AppState.sessionId
  })
});
```

---

## 🛠️ Tool Integration

### Tool Registry Structure
```javascript
// Tools are organized by platform:
const PLATFORMS = {
  'Slack': 24,           // Communication
  'Gmail': 29,           // Email
  'Twilio': 18,          // SMS/Voice
  'WooCommerce': 29,     // E-commerce
  'Stripe': 25,          // Payments
  'Google Docs': 22,     // Documents
  'Google Sheets': 20,   // Spreadsheets
  'Google Drive': 18,    // Storage
  'Supabase': 15,        // Database
  'GitHub': 16,          // Version control
  // ... 9 more platforms
};

// Total: 281 tools across 19 platforms
```

### Using Tools via AI Agent
```javascript
// Ask AI to use tools
const response = await fetch('http://localhost:4000/api/agent/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "Send a Slack message to #general saying 'Hello team!'",
    session_id: AppState.sessionId,
    context: {
      tab: "communication",
      platform: "business_ai_platform"
    }
  })
});

// AI will automatically:
// 1. Parse the request
// 2. Select the appropriate tool (slack_send_message)
// 3. Execute the tool
// 4. Return the result
```

---

## 📝 Implementation Steps

### Step 1: Update API Base URL Configuration

**Current** (in `business-ai-platform-v2.html` line 1651):
```javascript
const API_BASE_URL = 'http://localhost:4000';
```

**✅ Already correct!** Your HTML is pointing to the right port.

### Step 2: Add VSA Automation Agent Endpoints

Add this after the existing `API_ENDPOINTS` (line 1652):

```javascript
const API_ENDPOINTS = {
  // Existing endpoints...
  health: '/health',
  agent: {
    chat: '/api/agent/chat',
    stream: '/api/agent/stream',
    tools: '/api/agent/tools',
    upload: '/api/agent/upload'
  },
  // ... existing code ...
};

// ✅ NEW: Add VSA Automation Agent endpoints
const VSA_API_BASE_URL = 'http://localhost:5300';
const VSA_API_ENDPOINTS = {
  agent: {
    chat: '/api/agent/chat',
    session: '/api/agent/session',
    sessions: '/api/agent/sessions'
  },
  clients: {
    list: '/api/clients',
    get: '/api/clients/:id',
    create: '/api/clients',
    test: '/api/clients/:id/test'
  },
  processing: {
    trigger: '/api/processing/trigger',
    status: '/api/processing/status',
    monitor: '/api/processing/monitor'
  },
  google: {
    driveFolders: '/api/google/drive/folders',
    driveFiles: '/api/google/drive/files/:id',
    driveImport: '/api/google/drive/import/:id',
    sheetsImport: '/api/google/sheets/import',
    gmailMonitor: '/api/google/gmail/monitor'
  },
  notifications: {
    send: '/api/notifications/send',
    setup: '/api/notifications/setup'
  },
  health: '/api/health',
  tools: '/api/tools'
};
```

### Step 3: Add Authentication Manager

Add this after `AppState` (line 1670):

```javascript
// ==================== AUTHENTICATION MANAGER ====================
const AuthManager = {
  googleAuth: null,
  tokens: {},
  
  async initializeGoogleAuth() {
    if (typeof GoogleAuth !== 'undefined') {
      this.googleAuth = new GoogleAuth();
      console.log('✅ Google Auth initialized');
    } else {
      console.warn('⚠️ google-auth.js not loaded');
    }
  },
  
  async getGoogleToken() {
    if (!this.googleAuth) {
      await this.initializeGoogleAuth();
    }
    
    if (this.googleAuth) {
      return await this.googleAuth.getAccessToken();
    }
    return null;
  },
  
  async authorizeGoogle() {
    if (!this.googleAuth) {
      await this.initializeGoogleAuth();
    }
    
    if (this.googleAuth) {
      return await this.googleAuth.authorize();
    }
    return null;
  }
};
```

### Step 4: Update `loadPlatformStatus()` Function

**Replace the existing function** (line 1877) with enhanced version:

```javascript
async function loadPlatformStatus() {
  const grid = document.getElementById('platform-status-grid');
  
  // Show loading state
  grid.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);"><i class="fas fa-spinner fa-spin"></i> Loading platforms...</div>';
  
  if (!AppState.isConnected) {
    grid.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">Backend disconnected</div>';
    return;
  }
  
  try {
    // ✅ Fetch tool list from Flask (281 tools)
    const response = await fetch(`${API_BASE_URL}/api/agent/tools`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Extract unique platforms from tools
    const platformMap = new Map();
    
    if (data.tools && Array.isArray(data.tools)) {
      data.tools.forEach(tool => {
        const platform = tool.platform || 'Unknown';
        if (!platformMap.has(platform)) {
          platformMap.set(platform, {
            name: platform,
            status: 'connected',
            tools: [],
            icon: getPlatformIcon(platform),
            color: getPlatformColor(platform),
            category: tool.category || 'other'
          });
        }
        platformMap.get(platform).tools.push({
          name: tool.name,
          description: tool.description
        });
      });
    }
    
    const platforms = Array.from(platformMap.values());
    
    // Render platforms
    if (platforms.length === 0) {
      grid.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">No platforms configured</div>';
      return;
    }
    
    // Sort by category
    const categories = {
      'communication': [],
      'e-commerce': [],
      'documents': [],
      'database': [],
      'infrastructure': [],
      'ai': [],
      'other': []
    };
    
    platforms.forEach(p => {
      const cat = p.category || 'other';
      if (!categories[cat]) categories[cat] = [];
      categories[cat].push(p);
    });
    
    // Render by category
    let html = '';
    for (const [category, platformList] of Object.entries(categories)) {
      if (platformList.length === 0) continue;
      
      html += `
        <div style="margin-bottom: 24px;">
          <h3 style="font-size: 14px; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 12px;">
            ${category.replace('-', ' ')}
          </h3>
      `;
      
      platformList.forEach(p => {
        html += `
          <div class="platform-card" style="display: flex; align-items: center; gap: 12px; padding: 12px; background: var(--bg-tertiary); border-radius: 6px; margin-bottom: 8px; cursor: pointer; transition: all 0.2s ease;" onclick="showPlatformDetails('${p.name}')">
            <div style="width: 40px; height: 40px; background: ${p.color}; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: white;">
              <i class="fab ${p.icon}"></i>
            </div>
            <div style="flex: 1;">
              <div style="font-weight: 600;">${p.name}</div>
              <div style="font-size: 12px; color: var(--text-secondary);">${p.tools.length} tools available</div>
            </div>
            <div style="width: 8px; height: 8px; background: var(--accent-success); border-radius: 50%;" title="Connected"></div>
          </div>
        `;
      });
      
      html += '</div>';
    }
    
    grid.innerHTML = html;
    
    // Store platforms in AppState
    AppState.platforms = platforms;
    
    console.log(`✅ Loaded ${platforms.length} platforms with ${data.tools.length} tools`);
    
  } catch (error) {
    console.error('❌ Failed to load platforms:', error);
    grid.innerHTML = `
      <div style="padding: 20px; text-align: center;">
        <div style="color: var(--accent-error); margin-bottom: 8px;">
          <i class="fas fa-exclamation-triangle"></i> Failed to load platforms
        </div>
        <div style="font-size: 12px; color: var(--text-secondary);">${error.message}</div>
        <button onclick="loadPlatformStatus()" style="margin-top: 12px; padding: 8px 16px; background: var(--accent-primary); color: white; border: none; border-radius: 4px; cursor: pointer;">
          <i class="fas fa-redo"></i> Retry
        </button>
      </div>
    `;
  }
}

// ✅ NEW: Show platform details modal
function showPlatformDetails(platformName) {
  const platform = AppState.platforms.find(p => p.name === platformName);
  if (!platform) return;
  
  const modal = document.createElement('div');
  modal.className = 'platform-details-modal';
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
  `;
  
  modal.innerHTML = `
    <div style="background: var(--bg-secondary); border-radius: 12px; padding: 24px; max-width: 600px; max-height: 80vh; overflow-y: auto; width: 90%;">
      <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
        <div style="width: 60px; height: 60px; background: ${platform.color}; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-size: 28px;">
          <i class="fab ${platform.icon}"></i>
        </div>
        <div style="flex: 1;">
          <h2 style="margin: 0; font-size: 24px;">${platform.name}</h2>
          <div style="color: var(--text-secondary); font-size: 14px;">${platform.tools.length} tools available</div>
        </div>
        <button onclick="this.closest('.platform-details-modal').remove()" style="background: transparent; border: none; color: var(--text-secondary); font-size: 24px; cursor: pointer;">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div style="margin-bottom: 16px;">
        <h3 style="font-size: 16px; margin-bottom: 12px;">Available Tools</h3>
        ${platform.tools.map(tool => `
          <div style="padding: 12px; background: var(--bg-tertiary); border-radius: 6px; margin-bottom: 8px;">
            <div style="font-weight: 600; margin-bottom: 4px;">${tool.name}</div>
            <div style="font-size: 12px; color: var(--text-secondary);">${tool.description || 'No description available'}</div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
  
  document.body.appendChild(modal);
  
  // Close on overlay click
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.remove();
    }
  });
}
```

### Step 5: Initialize Authentication on Load

Update the `DOMContentLoaded` event (line 1677):

```javascript
document.addEventListener('DOMContentLoaded', async () => {
  console.log('🚀 Business AI Platform initializing...');
  console.log('🔧 VERSION: Connected to Flask Backend (Port 4000)');
  console.log('🎯 API Base URL:', API_BASE_URL);
  console.log('🎯 VSA Agent URL:', VSA_API_BASE_URL);
  
  // ✅ Initialize authentication
  await AuthManager.initializeGoogleAuth();
  
  // Initialize visualization engine for chat messages
  initVisualizationEngine();
  
  // Check Flask backend connection
  await checkBackendConnection();
  
  initTabNavigation();
  initChatPanel();
  initThemeToggle();
  initMultiAgent();
  await loadPlatformStatus();
  
  console.log('✅ Platform ready!');
  console.log('📊 Available:', AppState.platforms?.length || 0, 'platforms');
});
```

---

## ✅ Testing Checklist

### 1. **Backend Health Check**
```bash
# Test Flask Main App (Port 4000)
curl http://localhost:4000/health

# Test VSA Agent (Port 5300)
curl http://localhost:5300/api/health
```

### 2. **Start Services**
```powershell
# Start all services
cd C:\Users\gpoli\GIT\AI_agents
.\BISTART.ps1

# Services should start:
# ✅ Port 4000: Flask Main App
# ✅ Port 5300: VSA Automation Agent
```

### 3. **Test API Endpoints**
```javascript
// In browser console
// Test tool list
fetch('http://localhost:4000/api/agent/tools')
  .then(r => r.json())
  .then(d => console.log('Tools:', d.tools.length));

// Test chat
fetch('http://localhost:4000/api/agent/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Hello!',
    session_id: 'test_123'
  })
}).then(r => r.json()).then(console.log);
```

---

## 🎯 Next Steps

1. ✅ **Update HTML file** with authentication and enhanced platform loading
2. ✅ **Test backend connectivity** (BISTART already handles this)
3. ✅ **Implement Google OAuth** flow for Drive/Sheets access
4. ✅ **Add platform-specific features** to each tab
5. ✅ **Test multi-agent communication** with backend tools

---

## 📚 Additional Resources

- **Tool Registry**: `C:\Users\gpoli\GIT\AI_agents\tools\registry.py`
- **Config File**: `C:\Users\gpoli\GIT\AI_agents\config.py`
- **Google Auth**: `C:\Users\gpoli\GIT\AI_agents\google-auth.js`
- **Flask Routes**: `C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\routes\`
- **VSA Agent**: `C:\Users\gpoli\GIT\AI_agents\vsa_automation_agent.py`

---

**Last Updated**: October 26, 2025  
**Version**: 1.0.0  
**Status**: ✅ Ready for Integration
