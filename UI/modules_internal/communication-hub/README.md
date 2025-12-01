# 📧 Communication Hub - Complete Documentation

**Module ID:** communication-hub  
**Version:** 3.0.0  
**Last Updated:** November 29, 2025  
**Status:** ✅ Production Ready (V3.0 Compliant)  
**Compliance Score:** 68/100 (GOOD)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture & Compliance](#architecture--compliance)
3. [Installation](#installation)
4. [Usage Guide](#usage-guide)
5. [API Reference](#api-reference)
6. [Gmail & Outlook Integration](#gmail--outlook-integration)
7. [AI Agent Features](#ai-agent-features)
8. [Troubleshooting](#troubleshooting)
9. [Development Guide](#development-guide)
10. [Testing](#testing)

---

## Overview

The Communication Hub is a **V3.0 external module** that provides a unified inbox experience for Gmail and Outlook email integration with powerful AI agent capabilities.

### Key Features

✅ **Unified Inbox** - View emails from Gmail and Outlook in one interface  
✅ **Multi-Account Support** - Switch between accounts or view all together  
✅ **Email Composition** - Send emails via any connected account  
✅ **AI Integration** - Drag-and-drop emails to AI agents for analysis  
✅ **Context Menu** - Right-click emails for quick AI actions  
✅ **Bulk Operations** - Select multiple emails for batch AI analysis  
✅ **Full-Text Search** - Search across all accounts simultaneously  
✅ **Thread View** - Group related emails into conversations  
✅ **Export** - Export emails to Excel, CSV, or PDF

### Architecture Pattern

**Architecture 2 (Inline HTML-in-JS)**
- No separate HTML file
- All UI generated programmatically in JavaScript
- Uses template literals for HTML structure
- BaseModule polyfill included for independence
- Event delegation for dynamic content

---

## Architecture & Compliance

### V3.0 Manifest Compliance ✅ PASS

**Required Fields (All Present):**
```json
{
  "id": "communication-hub",
  "name": "Communication Hub",
  "version": "3.0.0",
  "type": "external",
  "category": "communication",
  "icon": "fas fa-comments",
  "color": "#6366f1",
  "description": "Unified inbox for Gmail and Outlook with AI integration"
}
```

**Capabilities Configuration:**
```json
{
  "capabilities": {
    "dashboard": {
      "enabled": true,
      "container_id": "communication-main-container"
    },
    "thread_integration": {
      "enabled": false
    }
  }
}
```

**Loading Strategy:**
```json
{
  "loading": {
    "strategy": "on_startup",
    "priority": 50
  }
}
```

### File Structure

```
UI/modules_external/communication-hub/
├── manifest.json                    # V3.0 module configuration
├── communication-hub.js             # Main module logic (1,982 lines)
├── communication-hub.css            # Styling (889 lines)
├── COMMUNICATION_HUB_COMPLETE.md    # This file
└── test_communication_hub_connection.ps1  # Test script
```

### Compliance Score Breakdown

**Total: 68/100 (GOOD Rating)**

| Check | Score | Status |
|-------|-------|--------|
| File Structure | 10/10 | ✅ PASS |
| V3.0 Manifest | 20/20 | ✅ PASS |
| Architecture Pattern | 15/15 | ✅ PASS (90% confidence) |
| Sidebar Integration | 0/10 | N/A (uses dashboard) |
| API Endpoints | 0/10 | ⚠️ External Flask routes |
| UI Rendering | 8/15 | ⚠️ PARTIAL (no explicit render) |
| Connections | 10/10 | ✅ PASS |
| Documentation | 5/10 | ✅ PASS (now consolidated) |

---

## Installation

### Prerequisites

1. **Backend Server Running**
   ```powershell
   cd C:\Users\gpoli\GIT\AI_agents
   BISTART  # Starts Flask server on port 5001
   ```

2. **OAuth Accounts Connected**
   - Gmail: Settings → Account Linking → Google
   - Outlook: Settings → Account Linking → Microsoft

### Module Files (Already Deployed)

The module is already installed at:
```
UI/modules_external/communication-hub/
```

### Backend Routes (Already Registered)

Routes are automatically registered via `flask_app.py`:
```python
from AI_infrastructure.routes.communication_routes import communication_bp
app.register_blueprint(communication_bp)  # /api/communication-hub/*
```

### Dependencies

**Frontend:**
- Tabulator.js 6.3.0 (email table)
- Font Awesome (icons)
- Platform UI framework

**Backend:**
- Gmail API wrapper (`google_workspace/gmail.py`)
- Outlook API wrapper (`tools/implementations/microsoft_outlook_tools.py`)
- CredentialInjector (`AI_infrastructure/auth/credential_injector.py`)
- Supabase PostgreSQL (`ai_infrastructure.oauth_tokens` table)

---

## Usage Guide

### Basic Operations

#### 1. View Inbox

Module automatically loads emails when activated:
1. Click "Communication Hub" in module selector
2. Emails appear in unified inbox table
3. Use account selector to filter by provider (Gmail/Outlook/All)
4. Click any email to open preview panel

#### 2. Send Email

**Method 1: Compose Tab**
1. Click "Compose" tab
2. Select "From" account (Gmail or Outlook dropdown)
3. Enter recipient email (To field)
4. Enter subject line
5. Type message body
6. Click "Send Email"

**Method 2: Reply to Email**
1. Right-click email in table
2. Select "Reply"
3. Compose window pre-fills recipient and subject
4. Type reply message
5. Click "Send"

#### 3. Search Emails

1. Click "Search" tab
2. Enter search query (searches subject, body, from, to)
3. Results appear from all connected accounts
4. Filter by account if needed

#### 4. Mark as Read/Unread

**Option A: Button Click**
- Click envelope icon in email row

**Option B: Context Menu**
- Right-click email → "Mark as Read/Unread"

#### 5. Delete Email

**Option A: Button Click**
- Click trash icon in email row

**Option B: Context Menu**
- Right-click email → "Delete"

---

## API Reference

### Backend Endpoints

**Base URL:** `http://localhost:5001/api/communication-hub`

#### GET /accounts
Get list of connected email accounts

**Response:**
```json
{
  "success": true,
  "accounts": [
    {
      "provider": "gmail",
      "email": "user@gmail.com",
      "enabled": true,
      "last_synced": "2025-11-29T10:30:00Z"
    },
    {
      "provider": "outlook",
      "email": "user@outlook.com",
      "enabled": true,
      "last_synced": "2025-11-29T10:28:00Z"
    }
  ]
}
```

#### GET /emails
Get unified inbox messages

**Query Parameters:**
- `provider` (optional): "gmail" | "outlook" | "all"
- `limit` (optional): Number of emails (default: 50)
- `offset` (optional): Pagination offset

**Response:**
```json
{
  "success": true,
  "emails": [
    {
      "id": "msg_gmail_12345",
      "provider": "gmail",
      "from": "sender@example.com",
      "to": "user@gmail.com",
      "subject": "Meeting Tomorrow",
      "snippet": "Hi, just confirming our meeting...",
      "date": "2025-11-29T09:45:00Z",
      "is_read": false,
      "has_attachments": true,
      "labels": ["INBOX", "IMPORTANT"]
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

#### GET /emails/:id
Get full email content

**Response:**
```json
{
  "success": true,
  "email": {
    "id": "msg_gmail_12345",
    "provider": "gmail",
    "from": "sender@example.com",
    "to": "user@gmail.com",
    "subject": "Meeting Tomorrow",
    "body": "Full email body content...",
    "date": "2025-11-29T09:45:00Z",
    "is_read": false,
    "attachments": [
      {
        "filename": "agenda.pdf",
        "size": 45678,
        "mime_type": "application/pdf"
      }
    ]
  }
}
```

#### POST /send
Send new email

**Request Body:**
```json
{
  "provider": "gmail",
  "to": "recipient@example.com",
  "subject": "Hello",
  "body": "Email message content",
  "cc": "cc@example.com",
  "bcc": "bcc@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message_id": "msg_gmail_67890",
  "provider": "gmail",
  "sent_at": "2025-11-29T10:35:00Z"
}
```

#### POST /emails/:id/read
Mark email as read/unread

**Request Body:**
```json
{
  "is_read": true
}
```

#### DELETE /emails/:id
Delete email

**Response:**
```json
{
  "success": true,
  "message": "Email deleted successfully"
}
```

#### GET /search
Search emails across all accounts

**Query Parameters:**
- `query`: Search query string
- `provider` (optional): Filter by provider

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "id": "msg_outlook_54321",
      "provider": "outlook",
      "from": "boss@company.com",
      "subject": "Urgent: Project Update",
      "snippet": "The client needs...",
      "date": "2025-11-29T08:00:00Z",
      "relevance_score": 0.95
    }
  ],
  "total_results": 12,
  "query": "project update"
}
```

### Frontend Methods

#### CommunicationHubModule Class

**Constructor:**
```javascript
const hub = new CommunicationHubModule();
```

**Methods:**

**async initialize()**
Initialize the module and load emails
```javascript
await hub.initialize();
```

**async loadEmails(provider = 'all')**
Load emails from specified provider
```javascript
await hub.loadEmails('gmail');  // Gmail only
await hub.loadEmails('outlook'); // Outlook only
await hub.loadEmails('all');     // All accounts
```

**async sendEmail(emailData)**
Send email via specified provider
```javascript
await hub.sendEmail({
  provider: 'gmail',
  to: 'recipient@example.com',
  subject: 'Test',
  body: 'Hello World'
});
```

**async markAsRead(emailId, isRead)**
Mark email as read/unread
```javascript
await hub.markAsRead('msg_gmail_12345', true);
```

**async deleteEmail(emailId)**
Delete email
```javascript
await hub.deleteEmail('msg_gmail_12345');
```

**async searchEmails(query)**
Search emails
```javascript
const results = await hub.searchEmails('project update');
```

**sendToAI(emailData)**
Send email to AI agent
```javascript
hub.sendToAI({
  from: 'sender@example.com',
  subject: 'Meeting Tomorrow',
  body: 'Full email content...'
});
```

**getSubTabContainer(subTabId)**
Get reference to sub-tab container (Architecture 2 helper)
```javascript
const container = hub.getSubTabContainer('unified-inbox');
```

---

## Gmail & Outlook Integration

### Gmail Integration

**Backend Implementation:**
- File: `google_workspace/gmail.py` (1,639 lines)
- API: Google Gmail API v1
- Authentication: OAuth 2.0 via service account
- Credentials: `ai_infrastructure.oauth_tokens` table

**Available Operations:**
- List messages (inbox, sent, drafts)
- Get full message content
- Send email (text and HTML)
- Mark as read/unread
- Delete message
- Search messages
- Manage labels
- Create drafts
- Manage filters
- Thread operations

**Credential Flow:**
1. User connects Gmail via Settings → Account Linking
2. OAuth tokens stored in `oauth_tokens` table
3. Backend uses `CredentialInjector` to fetch tokens
4. Gmail API calls use user's access token

### Outlook Integration

**Backend Implementation:**
- File: `tools/implementations/microsoft_outlook_tools.py` (900+ lines)
- API: Microsoft Graph API v1.0
- Authentication: OAuth 2.0 via Azure AD
- Credentials: `ai_infrastructure.oauth_tokens` table

**Available Operations:**
- List messages (inbox, sent, drafts)
- Get full message content
- Send email (text and HTML)
- Mark as read/unread
- Delete message
- Search messages
- Manage folders
- Create drafts
- Manage categories
- Create rules

**Credential Flow:**
1. User connects Outlook via Settings → Account Linking
2. OAuth tokens stored in `oauth_tokens` table
3. Backend uses `CredentialInjector` to fetch tokens
4. Graph API calls use user's access token

### Account Management

**Database Schema:**
```sql
-- ai_infrastructure.oauth_tokens table
CREATE TABLE oauth_tokens (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  platform TEXT NOT NULL,  -- 'google' or 'microsoft'
  access_token TEXT NOT NULL,
  refresh_token TEXT,
  expires_at TIMESTAMP,
  scope TEXT,
  email TEXT,
  is_active BOOLEAN DEFAULT TRUE
);
```

**Backend Methods:**
```python
# AI_infrastructure/auth/user_auth.py
def get_user_google_oauth_credentials(user_id):
    """Get Google OAuth tokens for user"""
    
def get_user_microsoft_oauth_credentials(user_id):
    """Get Microsoft OAuth tokens for user"""
```

---

## AI Agent Features

### Feature 1: Drag-and-Drop to AI Sidebar

**How it Works:**
1. User clicks and holds on any email row
2. Drag cursor to AI chat panel (right sidebar)
3. Module packages email data:
   ```javascript
   {
     from: "sender@example.com",
     to: "user@gmail.com",
     subject: "Meeting Tomorrow",
     date: "2025-11-29 09:45",
     body: "Full email content...",
     provider: "gmail"
   }
   ```
4. Sends formatted message to AI:
   ```
   Analyze this email:
   From: sender@example.com
   To: user@gmail.com
   Subject: Meeting Tomorrow
   Date: 2025-11-29 09:45
   
   Full email content...
   ```

**Implementation:**
```javascript
// communication-hub.js (lines 1200-1250)
setupDragAndDrop() {
  this.emailTable.on('rowMouseDown', (e, row) => {
    // Enable drag on mouse down
    row.getElement().setAttribute('draggable', 'true');
  });
  
  this.emailTable.on('rowDragStart', (e, row) => {
    const emailData = row.getData();
    e.dataTransfer.setData('application/json', JSON.stringify(emailData));
  });
}
```

### Feature 2: Right-Click Context Menu

**Available Actions:**
- Send to AI Prime (default agent)
- Send to Specific Agent (choose from list)
- Reply to Email
- Forward Email
- Delete Email
- Mark as Read/Unread
- Tag Email (green/orange/red)

**Implementation:**
```javascript
// communication-hub.js (lines 1300-1450)
showContextMenu(e, emailData) {
  const menu = document.createElement('div');
  menu.className = 'email-context-menu';
  menu.innerHTML = `
    <div class="context-menu-item" data-action="send-to-ai">
      <i class="fas fa-robot"></i> Send to AI Prime
    </div>
    <div class="context-menu-item" data-action="send-to-agent">
      <i class="fas fa-users"></i> Send to Specific Agent
    </div>
    <hr>
    <div class="context-menu-item" data-action="reply">
      <i class="fas fa-reply"></i> Reply
    </div>
    <div class="context-menu-item" data-action="forward">
      <i class="fas fa-share"></i> Forward
    </div>
    <hr>
    <div class="context-menu-item" data-action="delete">
      <i class="fas fa-trash"></i> Delete
    </div>
  `;
  // Position and show menu
}
```

### Feature 3: Bulk Selection Mode

**How to Use:**
1. Click "Select Mode" button in toolbar
2. Checkboxes appear in email table
3. Select multiple emails (10+ recommended)
4. Click "Send Selected to AI" button
5. AI receives batch for analysis:
   ```
   Analyze these 15 emails and provide:
   1. Common themes
   2. Priority order (urgent first)
   3. Suggested actions for each
   
   Email 1: From sender1@example.com, Subject: ...
   Email 2: From sender2@example.com, Subject: ...
   ...
   ```

**Implementation:**
```javascript
// communication-hub.js (lines 1500-1600)
enableBulkMode() {
  this.emailTable.addColumn({
    title: '<input type="checkbox" id="select-all">',
    field: '_selected',
    formatter: 'tickCross',
    width: 40,
    headerSort: false
  }, true);  // Insert at beginning
}
```

### Feature 4: Quick AI Actions (Robot Icon)

**One-Click Actions:**
- Summarize email (get 2-3 sentence summary)
- Generate reply (AI drafts appropriate response)
- Extract action items (identify tasks mentioned)
- Sentiment analysis (positive/negative/neutral)
- Priority assessment (high/medium/low urgency)

**Implementation:**
```javascript
// communication-hub.js (lines 1650-1750)
quickAIAction(emailData, action) {
  let prompt = '';
  
  switch(action) {
    case 'summarize':
      prompt = `Summarize this email in 2-3 sentences:\n${emailData.body}`;
      break;
    case 'reply':
      prompt = `Draft a professional reply to:\n${emailData.body}`;
      break;
    case 'actions':
      prompt = `Extract action items from:\n${emailData.body}`;
      break;
  }
  
  window.aiChat.sendMessage(prompt);
}
```

---

## Troubleshooting

### Issue: Emails Not Loading

**Symptoms:**
- Inbox appears empty
- "Loading..." message persists
- Console shows 401 or 403 errors

**Solutions:**

**1. Check OAuth Tokens:**
```javascript
// Open browser console
const tokens = localStorage.getItem('authToken');
console.log('Auth token:', tokens ? 'Present' : 'Missing');
```

**2. Verify Backend Connection:**
```powershell
# Test backend API
curl http://localhost:5001/api/communication-hub/accounts
```

**3. Reconnect Accounts:**
- Settings → Account Linking → Google → Disconnect → Reconnect
- Settings → Account Linking → Microsoft → Disconnect → Reconnect

**4. Check Backend Logs:**
```powershell
# View Flask logs
cd C:\Users\gpoli\GIT\AI_agents
# Check AI_infrastructure/logs/ folder
```

### Issue: Send Email Fails

**Symptoms:**
- "Send Email" button doesn't work
- Error: "Failed to send email"
- Console shows 400 Bad Request

**Solutions:**

**1. Verify Required Fields:**
```javascript
// All fields must be filled:
{
  provider: 'gmail',  // REQUIRED
  to: 'recipient@example.com',  // REQUIRED
  subject: 'Subject line',  // REQUIRED
  body: 'Email content'  // REQUIRED
}
```

**2. Check Email Format:**
- To/CC/BCC must be valid email addresses
- Body cannot be empty
- Subject cannot be empty

**3. Test with Simple Email:**
```javascript
// Open browser console
window.communicationHub.sendEmail({
  provider: 'gmail',
  to: 'test@example.com',
  subject: 'Test',
  body: 'Hello'
});
```

### Issue: Drag-and-Drop Not Working

**Symptoms:**
- Cannot drag emails to AI sidebar
- Drag cursor doesn't change
- AI doesn't receive email data

**Solutions:**

**1. Check Global Instance:**
```javascript
// Open browser console
console.log('Hub instance:', window.communicationHub);
// Should show object, not undefined
```

**2. Verify AI Sidebar Exists:**
```javascript
// Check if AI sidebar is loaded
const sidebar = document.getElementById('aiChat');
console.log('AI Sidebar:', sidebar ? 'Found' : 'Missing');
```

**3. Re-initialize Module:**
```javascript
// Reload the module
window.ModuleRegistry['communication-hub'].initialize();
```

### Issue: Context Menu Not Appearing

**Symptoms:**
- Right-click does nothing
- Menu appears in wrong location
- Menu closes immediately

**Solutions:**

**1. Disable Browser Default:**
```javascript
// Check if preventDefault is working
// Should NOT see browser's default menu
```

**2. Check Z-Index:**
```css
/* communication-hub.css */
.email-context-menu {
  z-index: 10000;  /* Must be high value */
}
```

**3. Clear Previous Menus:**
```javascript
// Remove any existing menus
document.querySelectorAll('.email-context-menu').forEach(m => m.remove());
```

### Issue: Backend URL Mismatch

**Symptoms:**
- Console error: "Failed to fetch"
- Network tab shows 404 for `/api/communication-hub/*`
- Backend is running but frontend can't connect

**Solutions:**

**1. Check Backend URL:**
```javascript
// communication-hub.js line 36
this.backendUrl = '/api/communication-hub';

// Should match Flask route:
// communication_routes.py line 73
communication_bp = Blueprint('communication', __name__, 
                            url_prefix='/api/communication-hub')
```

**2. Verify Flask Server:**
```powershell
# Check server is running
curl http://localhost:5001/api/communication-hub/accounts

# Should return JSON, not 404
```

**3. Check CORS Settings:**
```python
# AI_infrastructure/config.py
CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5001']
```

---

## Development Guide

### Architecture 2 Pattern Checklist

When modifying the module, follow Architecture 2 best practices:

✅ **No Separate HTML File**
- All UI generated in JavaScript
- Use template literals for structure

✅ **BaseModule Polyfill**
- Includes lightweight BaseModule replacement
- Provides sub-tab navigation framework

✅ **Global Instance Exposure**
```javascript
// REQUIRED for inline onclick handlers
window.communicationHub = moduleInstance;
window.communicationHubInstance = moduleInstance;  // Alias
```

✅ **Container Helper Method**
```javascript
getSubTabContainer(subTabId) {
  const mainContainer = document.getElementById('tab-communication');
  if (!mainContainer) return null;
  
  return mainContainer.querySelector(`#${subTabId}`);
}
```

✅ **Event Delegation**
```javascript
// PREFER event delegation over inline handlers
container.addEventListener('click', (e) => {
  if (e.target.closest('.email-row')) {
    this.handleEmailClick(e);
  }
});

// AVOID inline handlers (but sometimes necessary)
// If using inline, ensure global instance exists
```

### Adding New Features

**Step 1: Add to Manifest Capabilities**
```json
{
  "capabilities": {
    "dashboard": { "enabled": true },
    "new_feature": {
      "enabled": true,
      "config_key": "value"
    }
  }
}
```

**Step 2: Create Backend Endpoint**
```python
# AI_infrastructure/routes/communication_routes.py
@communication_bp.route('/new-feature', methods=['POST'])
def new_feature():
    """New feature endpoint"""
    # Implementation
    return jsonify({"success": True})
```

**Step 3: Add Frontend Method**
```javascript
// communication-hub.js
async callNewFeature(data) {
  const response = await fetch(`${this.backendUrl}/new-feature`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('authToken')}`
    },
    body: JSON.stringify(data)
  });
  
  return await response.json();
}
```

**Step 4: Add UI Element**
```javascript
// In initializeUnifiedInbox() or appropriate method
const button = `
  <button onclick="window.communicationHub.callNewFeature({})">
    New Feature
  </button>
`;
container.innerHTML += button;
```

### Code Style Guidelines

**1. Use Arrow Functions:**
```javascript
// GOOD
const loadEmails = async () => { ... };

// AVOID
function loadEmails() { ... }
```

**2. Use Template Literals:**
```javascript
// GOOD
const html = `
  <div class="email-row">
    <span>${email.from}</span>
    <span>${email.subject}</span>
  </div>
`;

// AVOID
const html = '<div class="email-row">' +
  '<span>' + email.from + '</span>' +
  '<span>' + email.subject + '</span>' +
  '</div>';
```

**3. Error Handling:**
```javascript
// ALWAYS use try-catch for async operations
try {
  const result = await this.loadEmails();
  this.displayEmails(result.emails);
} catch (error) {
  console.error('❌ Failed to load emails:', error);
  this.showErrorNotification('Failed to load emails. Please try again.');
}
```

**4. Console Logging:**
```javascript
// Use emoji prefixes for visibility
console.log('🔧 Processing email...');
console.log('✅ Email sent successfully');
console.error('❌ Failed to send email:', error);
console.log('🔍 Debug info:', data);
```

---

## Testing

### Manual Testing Checklist

**Basic Functionality:**
- [ ] Module loads without errors
- [ ] Unified inbox displays emails
- [ ] Account selector works (Gmail/Outlook/All)
- [ ] Email preview panel opens on click
- [ ] Compose email form validates input
- [ ] Send email succeeds
- [ ] Mark as read/unread works
- [ ] Delete email works
- [ ] Search returns results

**AI Integration:**
- [ ] Drag-and-drop to AI sidebar works
- [ ] Right-click context menu appears
- [ ] "Send to AI" sends formatted email
- [ ] "Send to Specific Agent" shows agent list
- [ ] Bulk selection mode activates
- [ ] Selected emails batch to AI
- [ ] Quick AI actions (robot icon) work

**Edge Cases:**
- [ ] Empty inbox displays message
- [ ] No accounts connected shows prompt
- [ ] Invalid email address rejected
- [ ] Large email loads without timeout
- [ ] Multiple rapid clicks handled gracefully

### Automated Testing Script

```powershell
# test_communication_hub_connection.ps1
cd C:\Users\gpoli\GIT\AI_agents

Write-Host "Testing Communication Hub Module..." -ForegroundColor Cyan

# Test 1: Backend server running
Write-Host "`n1. Testing backend server..." -ForegroundColor Yellow
$response = Invoke-WebRequest -Uri "http://localhost:5001/api/communication-hub/accounts" `
  -Method GET -Headers @{"Authorization"="Bearer YOUR_TOKEN"} -ErrorAction SilentlyContinue

if ($response.StatusCode -eq 200) {
  Write-Host "   ✅ Backend server responding" -ForegroundColor Green
} else {
  Write-Host "   ❌ Backend server not responding" -ForegroundColor Red
}

# Test 2: Gmail integration
Write-Host "`n2. Testing Gmail integration..." -ForegroundColor Yellow
# Test Gmail API connection
# (Add test code)

# Test 3: Outlook integration
Write-Host "`n3. Testing Outlook integration..." -ForegroundColor Yellow
# Test Outlook API connection
# (Add test code)

Write-Host "`nTesting complete!" -ForegroundColor Cyan
```

### Performance Testing

**Load Time:**
- Module initialization: < 500ms
- Email table render (50 emails): < 1s
- Search results: < 2s
- Email preview panel: < 300ms

**Stress Test:**
```javascript
// Test with 1000+ emails
const testData = Array(1000).fill(null).map((_, i) => ({
  id: `msg_${i}`,
  from: `sender${i}@example.com`,
  subject: `Test Email ${i}`,
  body: 'Lorem ipsum...',
  date: new Date().toISOString()
}));

window.communicationHub.emailTable.setData(testData);
// Should render without freezing browser
```

---

## Best Practices

### Security

✅ **Always use HTTPS in production**  
✅ **Store OAuth tokens securely in database**  
✅ **Validate email addresses server-side**  
✅ **Sanitize email content to prevent XSS**  
✅ **Use JWT authentication for API calls**  
✅ **Never expose API keys in frontend code**

### Performance

✅ **Lazy load email bodies (fetch on preview)**  
✅ **Paginate inbox (50 emails per page)**  
✅ **Cache email list in localStorage (5 min TTL)**  
✅ **Debounce search input (300ms delay)**  
✅ **Use virtual scrolling for large lists**  
✅ **Compress API responses with gzip**

### User Experience

✅ **Show loading indicators for async operations**  
✅ **Display error messages with retry option**  
✅ **Confirm destructive actions (delete email)**  
✅ **Auto-save compose draft every 30 seconds**  
✅ **Highlight unread emails with bold text**  
✅ **Show notification count in module icon**

---

## Version History

### v3.0.0 (November 29, 2025)
- ✅ Upgraded to V3.0 manifest schema
- ✅ Added `type` and `category` fields
- ✅ Added `capabilities` section
- ✅ Added `loading` strategy configuration
- ✅ Exposed global `window.communicationHub` instance
- ✅ Consolidated documentation into single file
- ✅ Achieved 68/100 compliance score (GOOD rating)

### v2.0.0 (November 28, 2025)
- Added drag-and-drop to AI sidebar
- Added right-click context menu
- Added bulk selection mode
- Added quick AI actions (robot icon)
- Improved email table with Tabulator.js
- Added email preview panel

### v1.0.0 (November 27, 2025)
- Initial release
- Gmail integration
- Outlook integration
- Basic inbox, compose, search functionality

---

**Last Updated:** November 29, 2025  
**Version:** 3.0.0  
**Status:** ✅ Production Ready (V3.0 Compliant)  
**Compliance Score:** 68/100 (GOOD)
