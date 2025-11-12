# 📧 Communication Hub Module

**Unified inbox for Gmail and Outlook with AI agent integration**

## Overview

The Communication Hub provides a centralized interface for managing emails from multiple providers (Gmail and Outlook) with powerful AI integration features including drag-and-drop to AI agents, right-click context menus, and bulk email analysis.

## Features

### ✅ Core Features
- **Unified Inbox**: View emails from Gmail and Outlook in one place
- **Multi-Account Support**: Switch between accounts or view all emails together
- **Email Composition**: Send emails via any connected account
- **Thread View**: Group related emails into conversations (coming soon)
- **Full-Text Search**: Search across all accounts simultaneously

### 🤖 AI Integration Features
1. **Drag-and-Drop to AI Sidebar**
   - Drag any email to the AI chat panel
   - Automatically packages email metadata (from, to, subject, date, body)
   - Sends formatted message to AI agent for analysis

2. **Right-Click Context Menu**
   - Send to AI Prime
   - Send to specific agent (choose from list)
   - Reply, Forward, Delete
   - Mark as Read/Unread

3. **Bulk Selection Mode**
   - Select multiple emails with checkboxes
   - Send batch to AI for analysis
   - Get common themes, priority order, suggested actions

4. **Quick AI Actions**
   - Robot icon button in each row for instant AI analysis
   - One-click email summarization
   - Smart reply suggestions

## Installation

### 1. Module Files (Already Created)
```
UI/external/modules/communication-hub/
├── manifest.json              # Module configuration
├── communication-hub.js       # Main module logic
├── communication-hub.css      # Styles
└── README.md                  # This file
```

### 2. Backend Routes (Already Registered)
File: `AI_infrastructure/routes/communication_routes.py`
- Registered in `flask_app.py` as `communication_bp`
- Available at `/api/communication-hub/*`

### 3. Dependencies
- **Frontend**: Tabulator.js (already in platform)
- **Backend**: 
  - Gmail API wrapper (`google_workspace/gmail.py`)
  - Outlook API wrapper (`tools/implementations/microsoft_outlook_tools.py`)
  - CredentialInjector (`AI_infrastructure/auth/credential_injector.py`)

## Usage

### Connect Accounts

Before using the Communication Hub, connect your email accounts:

1. **Gmail**: Use Google OAuth flow
   - Navigate to Settings → Account Linking → Google
   - Click "Connect Gmail"
   - Authorize access

2. **Outlook**: Use Microsoft OAuth flow
   - Navigate to Settings → Account Linking → Microsoft
   - Click "Connect Outlook"
   - Authorize access

### Basic Email Operations

**View Inbox:**
- Module automatically loads emails from connected accounts
- Use account selector to filter by provider
- Click email to open preview panel

**Send Email:**
1. Click "Compose" tab
2. Select "From" account (Gmail or Outlook)
3. Enter recipient, subject, and message
4. Click "Send Email"

**Search Emails:**
1. Click "Search" tab
2. Enter search query
3. Results appear from all accounts

### AI Integration

**Method 1: Drag-and-Drop**
1. Click and hold on any email row
2. Drag email to AI sidebar (left panel)
3. Drop into chat area
4. AI automatically receives formatted email for analysis

**Method 2: Right-Click Menu**
1. Right-click on any email
2. Choose "Send to AI Prime" for instant analysis
3. Or choose "Send to Agent..." to select specific agent

**Method 3: Bulk Selection**
1. Click "Select" button in toolbar
2. Check multiple emails
3. Click "Send to AI" button
4. AI analyzes all selected emails together

**Method 4: Quick Action Button**
1. Click robot icon in email row
2. Email instantly sent to AI Prime

### AI Analysis Prompts

When emails are sent to AI, they are formatted as:

```
📧 **Email Analysis Request**

**From:** sender@example.com
**To:** recipient@example.com
**Subject:** Important Project Update
**Date:** Nov 10, 2025 2:30 PM
**Provider:** gmail

**Email Body:**
[Full email content here]

---

Please analyze this email and provide:
1. Summary of key points
2. Suggested actions
3. Important dates or deadlines
4. Any concerns or flags
```

For bulk emails, AI receives:
```
📧 **Batch Email Analysis Request**

**Selected Emails:** 5

**Email 1:**
- From: person1@example.com
- Subject: Budget Approval
- Date: Nov 10, 2025
- Preview: Please review the Q4 budget...

[... more emails ...]

Please analyze these emails and provide:
1. Common themes or topics
2. Priority order for responses
3. Suggested actions for each
4. Any important deadlines
```

## API Endpoints

### GET /api/communication-hub/accounts
Get list of connected email accounts

**Response:**
```json
{
  "success": true,
  "accounts": [
    {
      "id": "gmail",
      "provider": "gmail",
      "email": "user@gmail.com",
      "name": "Gmail",
      "connected": true
    }
  ],
  "count": 1
}
```

### GET /api/communication-hub/emails
List emails from selected account(s)

**Query Params:**
- `account` - Account ID ('all', 'gmail', 'outlook')
- `limit` - Max emails (default: 50)
- `user_id` - User ID (default: 1)

**Response:**
```json
{
  "success": true,
  "emails": [
    {
      "id": "gmail_12345",
      "provider": "gmail",
      "from": "sender@example.com",
      "to": "recipient@example.com",
      "subject": "Important Update",
      "date": "2025-11-10T14:30:00Z",
      "is_read": false,
      "snippet": "Email preview text...",
      "has_attachments": false
    }
  ],
  "count": 25
}
```

### GET /api/communication-hub/emails/{email_id}
Get full email content

**Response:**
```json
{
  "success": true,
  "email": {
    "id": "gmail_12345",
    "provider": "gmail",
    "from": "sender@example.com",
    "to": "recipient@example.com",
    "subject": "Important Update",
    "date": "2025-11-10T14:30:00Z",
    "body_text": "Plain text body...",
    "body_html": "<p>HTML body...</p>",
    "snippet": "Email preview...",
    "attachments": []
  }
}
```

### POST /api/communication-hub/send
Send email via selected account

**Request Body:**
```json
{
  "from": "gmail",
  "to": "recipient@example.com",
  "cc": "cc@example.com",
  "subject": "Email Subject",
  "body": "Email body content",
  "user_id": 1
}
```

### POST /api/communication-hub/emails/{email_id}/read
Mark email as read

### GET /api/communication-hub/search
Search emails across accounts

**Query Params:**
- `q` - Search query
- `limit` - Max results
- `user_id` - User ID

### DELETE /api/communication-hub/emails/{email_id}
Delete email

## Architecture

### Frontend (communication-hub.js)

**Class Structure:**
```javascript
class CommunicationHubModule extends BaseModule {
    // State
    emails = []
    selectedAccount = 'all'
    accounts = []
    selectedEmails = new Set()
    draggedEmail = null
    
    // Methods
    initialize()
    loadAccounts()
    loadEmails()
    createEmailTable()
    handleDragStart()
    showContextMenu()
    sendEmailToAI()
    // ... more methods
}
```

**Key Components:**
1. **Tabulator Table**: Displays emails with drag support
2. **Context Menu**: Right-click actions
3. **Preview Panel**: Slide-out email viewer
4. **Compose Form**: Email composition interface
5. **Search Interface**: Full-text search across accounts

### Backend (communication_routes.py)

**Blueprint:** `communication_bp`

**Key Functions:**
- `get_accounts()` - List connected accounts
- `list_emails()` - Unified inbox from multiple providers
- `get_email()` - Fetch full email content
- `send_email()` - Send via selected provider
- `search_emails()` - Search across accounts
- `mark_email_as_read()` - Update read status
- `delete_email()` - Delete email

**Integration:**
- Uses `CredentialInjector` for OAuth tokens
- Calls Gmail API wrapper functions
- Calls Outlook API wrapper functions
- Returns unified format for frontend

## Drag-and-Drop Implementation

### Email Row → AI Sidebar

**1. Row Setup (in createEmailTable):**
```javascript
this.tabulatorTable.on("rowMouseEnter", function(e, row){
    const rowElement = row.getElement();
    rowElement.draggable = true;
    
    rowElement.addEventListener('dragstart', (event) => {
        self.handleDragStart(event, row.getData());
    });
});
```

**2. Drag Start Handler:**
```javascript
handleDragStart(event, email) {
    // Package email metadata
    const emailMetadata = {
        type: 'email',
        provider: email.provider,
        id: email.id,
        from: email.from,
        subject: email.subject,
        date: email.date,
        snippet: email.snippet
    };
    
    // Set drag data
    event.dataTransfer.setData('application/json', JSON.stringify(emailMetadata));
    event.dataTransfer.setData('text/plain', `Email: ${email.subject}...`);
}
```

**3. AI Sidebar Drop Zone:**
The AI chat panel must listen for drop events and extract email data:
```javascript
chatPanel.addEventListener('drop', (event) => {
    const emailData = JSON.parse(event.dataTransfer.getData('application/json'));
    if (emailData.type === 'email') {
        // Fetch full email content
        // Format message for AI
        // Send to AI chat
    }
});
```

## Context Menu Implementation

### Right-Click Menu

**HTML Structure:**
```html
<div id="email-context-menu" class="context-menu">
    <div class="context-menu-item" data-action="send-to-prime">
        <i class="fas fa-robot"></i> Send to AI Prime
    </div>
    <div class="context-menu-item" data-action="send-to-agent">
        <i class="fas fa-users"></i> Send to Agent...
    </div>
    <!-- More menu items -->
</div>
```

**Show on Right-Click:**
```javascript
rowContext: (e, row) => {
    e.preventDefault();
    this.showContextMenu(e, row.getData());
}
```

**Action Handler:**
```javascript
handleContextMenuAction(action) {
    const email = this.contextMenuEmail;
    
    switch (action) {
        case 'send-to-prime':
            this.sendEmailToAI(email, 'AI Prime');
            break;
        case 'send-to-agent':
            this.showAgentSelector(email);
            break;
        // More actions...
    }
}
```

## Styling

### CSS Variables (Customizable)
```css
--module-primary: #6366f1;
--module-secondary: #818cf8;
--module-hover: #4f46e5;
--surface-color: #ffffff;
--border-color: #e5e7eb;
--text-primary: #1f2937;
```

### Key Classes
- `.communication-hub-inbox` - Main container
- `.inbox-header` - Toolbar with actions
- `.email-preview-panel` - Slide-out panel
- `.context-menu` - Right-click menu
- `.drag-preview` - Drag visual feedback
- `.agent-selector-modal` - Agent selection dialog

## Troubleshooting

### Module Not Loading

**Check:**
1. Files exist in `UI/external/modules/communication-hub/`
2. `manifest.json` is valid JSON
3. Module registered in `ModuleRegistry`
4. Browser console for errors

**Fix:**
```javascript
// In browser console:
console.log(window.ModuleRegistry);
// Should show: { 'communication-hub': CommunicationHubModule }
```

### No Emails Displayed

**Check:**
1. Accounts connected via OAuth
2. Backend routes registered in Flask
3. API endpoint responding: `GET /api/communication-hub/accounts`
4. Credentials exist in database

**Debug:**
```javascript
// Check accounts:
fetch('/api/communication-hub/accounts')
    .then(r => r.json())
    .then(console.log);

// Check emails:
fetch('/api/communication-hub/emails?account=all')
    .then(r => r.json())
    .then(console.log);
```

### Drag-and-Drop Not Working

**Check:**
1. Rows are `draggable="true"`
2. AI sidebar has drop event listener
3. `dataTransfer` has email data
4. Browser console for drag events

**Fix:**
```javascript
// Test drag data:
rowElement.addEventListener('dragstart', (e) => {
    console.log('Dragging:', e.dataTransfer.types);
});
```

### Context Menu Not Appearing

**Check:**
1. Context menu element exists in DOM
2. `rowContext` handler attached to Tabulator
3. Event preventDefault() called
4. CSS `display: none` → `display: block` on show

## Future Enhancements

- [ ] Thread grouping (conversation view)
- [ ] Email templates (saved replies)
- [ ] Scheduled sending
- [ ] Rich text editor (TinyMCE/Quill)
- [ ] Attachment upload/download
- [ ] Email filters (starred, labels, categories)
- [ ] Real-time updates (WebSockets)
- [ ] Read receipts
- [ ] Email signatures
- [ ] Slack integration (add Slack messages to unified inbox)

## Contributing

When adding features:

1. **Update manifest.json** - Add new tabs or features
2. **Add methods to class** - Keep code organized
3. **Document in README** - Update usage instructions
4. **Test with real accounts** - Verify Gmail and Outlook work
5. **Update CSS** - Match existing design patterns

## Support

For issues or questions:
- Check browser console for JavaScript errors
- Check Flask logs for backend errors
- Verify OAuth credentials are valid
- Test API endpoints with curl/Postman

## Version History

- **1.0.0** (2025-11-10) - Initial release
  - Unified inbox for Gmail and Outlook
  - Drag-and-drop to AI sidebar
  - Right-click context menu
  - Bulk selection mode
  - Email composition
  - Search functionality

---

**Last Updated:** November 10, 2025  
**Maintainer:** InHouse Print Development Team  
**License:** Proprietary
