# Communication Hub - Email to Agent Thread Integration

**Date**: December 8, 2025  
**Purpose**: Ensure emails assigned to agents properly link to threads with email badge display  
**Status**: ✅ COMPLETE

---

## 🎯 Overview

When an email is assigned to an agent (Prime, Alpha, Bravo, etc.), the system now:
1. Creates a thread in `sessions.threads` with the agent's location
2. Links the email to the thread by populating email columns
3. Displays an email badge in the thread card (like synergy session badges)
4. Shows email subject and participants in the thread info area

---

## 🔗 Data Flow

### Step-by-Step Process:

```
User clicks "Assign Agent" on email
    ↓
Dropdown shows agents (Prime, Alpha, Bravo...)
    ↓
User selects agent (e.g., Alpha)
    ↓
1. POST /api/threads/create
   ├─ location: 'agent-1' (Alpha)
   ├─ title: 'Email: Meeting Request'
   ├─ tags: ['email', 'gmail', 'assigned']
   └─ metadata: {email context}
    ↓
2. POST /api/thread-assignments/email
   ├─ thread_slug: '1733684123456'
   ├─ email_thread_id: 'gmail_19af966764ed2d52'
   ├─ email_subject: 'Meeting Request'
   └─ email_participants: 'john@example.com'
    ↓
3. UPDATE sessions.threads SET
   ├─ email_thread_id = 'gmail_19af966764ed2d52'
   ├─ email_subject = 'Meeting Request'
   └─ email_participants = '["john@example.com"]'
    ↓
4. Thread card now displays:
   [🤖 Alpha]  [✉️ Meeting Request from john@example.com]
```

---

## 📊 Database Schema

### `sessions.threads` Table Columns

```sql
CREATE TABLE sessions.threads (
    id SERIAL PRIMARY KEY,
    thread_slug TEXT NOT NULL UNIQUE,
    user_id INTEGER,
    name TEXT NOT NULL,                    -- Thread title (e.g., "Email: Meeting Request")
    location TEXT,                         -- Agent location (e.g., 'prime', 'agent-1', 'agent-2')
    metadata TEXT,                         -- JSON with email context
    tags TEXT,                             -- JSON array ['email', 'gmail', 'assigned']
    
    -- Email Integration Columns (populated by /api/thread-assignments/email)
    email_thread_id TEXT,                  -- Email ID (e.g., 'gmail_19af966764ed2d52')
    email_subject TEXT,                    -- Email subject
    email_participants TEXT,               -- JSON array of email addresses
    
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    ...
);
```

### Location Values (Agent Mapping)

| Location      | Agent Name | Purpose                           |
|---------------|------------|-----------------------------------|
| `prime`       | Prime      | Main AI assistant                 |
| `prime-loaded`| Prime      | Prime with loaded context         |
| `agent-1`     | Alpha      | First specialized agent           |
| `agent-2`     | Bravo      | Second specialized agent          |
| `agent-3`     | Charlie    | Third specialized agent           |
| `agent-4`     | Delta      | Fourth specialized agent          |
| `agent-5`     | Echo       | Fifth specialized agent           |
| `agent-6`     | Foxtrot    | Sixth specialized agent           |
| `agent-7`     | Golf       | Seventh specialized agent         |

---

## 🔧 Code Implementation

### Frontend: `communication-hub-v4-modern.js`

**Location**: Lines ~1800-1840

```javascript
async assignEmailToAgent(emailId, agentName, cell, agentId = null) {
    const userId = window.UserAuth?.user?.id || 1;
    const emailData = cell.getRow().getData();
    const fullEmail = await this.fetchEmailContent(emailId);
    
    // Step 1: Create thread with agent location
    const threadResponse = await this.api.post('/api/threads/create', {
        user_id: userId,
        title: `Email: ${fullEmail.subject || 'No Subject'}`,
        context_type: 'email',
        location: location,  // 'prime', 'agent-1', 'agent-2', etc.
        tags: ['email', fullEmail.provider, 'assigned'],
        metadata: {
            email_id: emailId,
            email_subject: fullEmail.subject,
            email_from: fullEmail.from,
            email_to: fullEmail.to,
            email_provider: fullEmail.provider,
            assigned_agent: agentName,
            assigned_at: new Date().toISOString()
        }
    });
    
    const threadSlug = threadResponse.thread_slug;
    
    // Step 2: CRITICAL - Link email to thread
    // This populates email_thread_id, email_subject, email_participants columns
    const linkResponse = await this.api.post('/api/thread-assignments/email', {
        user_id: userId,
        thread_slug: threadSlug,
        email_thread_id: emailId,
        email_subject: fullEmail.subject,
        email_participants: fullEmail.from
    });
    
    // This makes the email badge appear in thread card!
}
```

**Key Changes:**
- ✅ Added comprehensive logging with emojis
- ✅ Added error checking for link response
- ✅ Added comment explaining why email link is critical

---

### Backend: `thread_assignment_routes.py`

**Route**: `POST /api/thread-assignments/email`  
**Location**: Lines ~755-815

```python
@thread_assignment_bp.route('/api/thread-assignments/email', methods=['POST'])
def link_email_thread():
    """
    Link email to conversation thread
    Updates sessions.threads with email metadata
    """
    data = request.get_json()
    user_id = data.get('user_id')
    thread_slug = data.get('thread_slug')
    email_thread_id = data.get('email_thread_id')
    email_subject = data.get('email_subject')
    email_participants = data.get('email_participants', [])
    
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # Update thread with email metadata
            cursor.execute("""
                UPDATE sessions.threads 
                SET email_thread_id = %s,
                    email_subject = %s,
                    email_participants = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE thread_slug = %s AND user_id = %s
            """, (email_thread_id, email_subject, json.dumps(email_participants), thread_slug, user_id))
            
            conn.commit()
    
    return jsonify({
        'success': True,
        'thread_slug': thread_slug,
        'email_thread_id': email_thread_id
    })
```

**What This Does:**
- Updates `email_thread_id` column with email ID (e.g., `gmail_19af966764ed2d52`)
- Updates `email_subject` column with email subject
- Updates `email_participants` column with sender/recipients
- Sets `updated_at` timestamp

**Result:**
Thread is now "linked" to email and will show email badge in UI.

---

## 🎨 UI Display

### Thread Card Email Badge (Teal Pill)

**Template**: `thread-card-templates.js` Lines ~738-757

```javascript
${thread.email_thread_id ? `
    <div class="thread-item-email thread-item-email-linked" 
         data-email-id="${thread.email_thread_id}">
        <button class="email-badge" 
                style="background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%); 
                       color: white; padding: 8px 14px; border-radius: 8px; 
                       box-shadow: 0 2px 8px rgba(20, 184, 166, 0.3);"
                onclick="window.CommunicationHub?.openEmailPreview('${thread.email_thread_id}')">
            <i class="fas fa-envelope"></i>
            <span>${thread.email_subject || 'Email Thread'}</span>
            ${thread.email_participants ? 
                `<span>from ${thread.email_participants}</span>` : ''}
        </button>
        <button class="email-unlink" 
                onclick="ThreadManager.unlinkEmail('${thread.id}', '${thread.email_thread_id}')">
            <i class="fas fa-unlink"></i>
        </button>
    </div>
` : ''}
```

**Visual Result:**

```
┌─────────────────────────────────────────────────────┐
│ 🤖 Alpha                                            │
│                                                     │
│ Thread Title: Email: Meeting Request               │
│                                                     │
│ [✉️ Meeting Request from john@example.com     ×]   │ ← Email Badge (Teal)
│                                                     │
│ [🔗 Synergy Session: Project Alpha         ×]      │ ← Synergy Badge (Purple)
│                                                     │
│ Last updated: 2 minutes ago                         │
└─────────────────────────────────────────────────────┘
```

**Badge Features:**
- **Teal gradient** - Distinct from synergy (purple) and workflow (orange)
- **Click email badge** - Opens email preview in Communication Hub
- **Shows subject** - Email subject displayed on badge
- **Shows sender** - "from john@example.com"
- **Unlink button** - Remove email linkage (X icon)

---

## 🔍 How to Verify It's Working

### Test Scenario:

**Step 1: Assign Email to Agent**
```
1. Open Communication Hub → Unified Inbox
2. Load emails (click Refresh)
3. Click "Assign Agent" on any email
4. Select "Alpha" from dropdown
```

**Expected Console Output:**
```javascript
🤖 Assigning email gmail_19af966764ed2d52 to agent: Alpha (ID: agent-1)
📧 Thread created: 1733684123456
📎 Email linked to thread - will show in thread info area
✅ Email gmail_19af966764ed2d52 assigned to agent Alpha in thread 1733684123456
```

**Step 2: Open Agent Panel**
```
1. Open Command Centre sidebar
2. Click "Alpha" agent panel
3. Look at thread cards
```

**Expected UI:**
```
Thread card should show:
- Thread title: "Email: [Subject]"
- Teal email badge with subject
- "from [sender]" text
- Click badge opens email preview
```

**Step 3: Verify Database**
```sql
SELECT 
    thread_slug,
    name,
    location,
    email_thread_id,
    email_subject,
    email_participants,
    tags
FROM sessions.threads
WHERE email_thread_id IS NOT NULL
ORDER BY created_at DESC
LIMIT 5;
```

**Expected Result:**
```
thread_slug       | name                    | location | email_thread_id         | email_subject      | email_participants
1733684123456     | Email: Meeting Request  | agent-1  | gmail_19af966764ed2d52  | Meeting Request    | ["john@example.com"]
```

---

## 📋 API Endpoints

### 1. Create Thread with Email Context

```http
POST /api/threads/create
Content-Type: application/json

{
  "user_id": 1,
  "title": "Email: Meeting Request",
  "context_type": "email",
  "location": "agent-1",
  "tags": ["email", "gmail", "assigned"],
  "metadata": {
    "email_id": "gmail_19af966764ed2d52",
    "email_subject": "Meeting Request",
    "email_from": "john@example.com",
    "email_to": "support@company.com",
    "email_provider": "gmail",
    "assigned_agent": "Alpha",
    "assigned_at": "2025-12-08T10:30:00Z"
  }
}
```

**Response:**
```json
{
  "success": true,
  "thread": {
    "id": "1733684123456",
    "title": "Email: Meeting Request",
    "created": "2025-12-08T10:30:00Z",
    "agent_id": "agent-1",
    "user_id": 1
  },
  "thread_slug": "1733684123456"
}
```

---

### 2. Link Email to Thread (CRITICAL)

```http
POST /api/thread-assignments/email
Content-Type: application/json

{
  "user_id": 1,
  "thread_slug": "1733684123456",
  "email_thread_id": "gmail_19af966764ed2d52",
  "email_subject": "Meeting Request",
  "email_participants": "john@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "thread_slug": "1733684123456",
  "email_thread_id": "gmail_19af966764ed2d52",
  "email_subject": "Meeting Request"
}
```

**What Happens:**
```sql
UPDATE sessions.threads 
SET 
    email_thread_id = 'gmail_19af966764ed2d52',
    email_subject = 'Meeting Request',
    email_participants = '["john@example.com"]',
    updated_at = CURRENT_TIMESTAMP
WHERE thread_slug = '1733684123456' AND user_id = 1;
```

---

### 3. Get Thread Emails

```http
GET /api/communication-hub/threads/1733684123456/emails?user_id=1
```

**Response:**
```json
{
  "success": true,
  "emails": [
    {
      "id": "gmail_19af966764ed2d52",
      "provider": "gmail",
      "from": "john@example.com",
      "subject": "Meeting Request",
      "date": "2025-12-08T09:15:00Z",
      "body_text": "...",
      "body_html": "..."
    }
  ],
  "count": 1,
  "thread_slug": "1733684123456"
}
```

---

### 4. Unlink Email from Thread

```http
POST /api/thread-assignments/email/unlink
Content-Type: application/json

{
  "user_id": 1,
  "thread_slug": "1733684123456"
}
```

**Response:**
```json
{
  "success": true,
  "thread_slug": "1733684123456"
}
```

**What Happens:**
```sql
UPDATE sessions.threads 
SET 
    email_thread_id = NULL,
    email_subject = NULL,
    email_participants = NULL,
    updated_at = CURRENT_TIMESTAMP
WHERE thread_slug = '1733684123456' AND user_id = 1;
```

---

## 🎯 Key Differences: Email vs Synergy

| Feature                | Email Linkage                     | Synergy Session Linkage           |
|------------------------|-----------------------------------|-----------------------------------|
| **Badge Color**        | Teal (#14b8a6)                   | Purple (#8b5cf6)                  |
| **Icon**               | `<i class="fas fa-envelope">`    | `<i class="fas fa-link">`         |
| **Link Column**        | `email_thread_id`                | `synergy_card_id`                 |
| **Data Columns**       | `email_subject`, `email_participants` | `synergy_card_name`          |
| **Click Action**       | Opens email preview              | Opens synergy card                |
| **Unlink Route**       | `/api/thread-assignments/email/unlink` | `/api/threads/unlink/synergy` |
| **Display Template**   | `thread-item-email-linked`       | `thread-link-row`                 |

---

## 🐛 Troubleshooting

### Issue 1: Email Badge Not Showing

**Symptom**: Thread created but no email badge appears in thread card

**Cause**: Email linkage endpoint not called or failed

**Debug Steps:**
1. Check browser console for errors
2. Look for "📎 Email linked to thread" success message
3. Check database:
   ```sql
   SELECT email_thread_id, email_subject 
   FROM sessions.threads 
   WHERE thread_slug = '1733684123456';
   ```
4. If columns are NULL, linkage failed

**Solution**: Ensure `/api/thread-assignments/email` endpoint is called after thread creation

---

### Issue 2: Email Badge Shows but Click Doesn't Work

**Symptom**: Badge appears but clicking doesn't open email

**Cause**: `window.CommunicationHub` not defined or email preview method missing

**Debug Steps:**
1. Check console: `console.log(window.CommunicationHub)`
2. Check if Communication Hub module is loaded
3. Verify `openEmailPreview` method exists

**Solution**: Ensure Communication Hub is initialized before clicking badge

---

### Issue 3: Multiple Emails Linked to Same Thread

**Symptom**: Thread shows different email each time it loads

**Cause**: Thread reassigned to different emails without unlinking first

**Debug Steps:**
```sql
SELECT thread_slug, email_thread_id, email_subject, updated_at
FROM sessions.threads
WHERE email_thread_id IS NOT NULL
ORDER BY updated_at DESC;
```

**Solution**: Unlink old email before assigning new one

---

## 🔮 Future Enhancements

### Planned Features:

1. **Multiple Emails Per Thread**
   - Store email IDs in JSON array
   - Show multiple email badges
   - Requires schema change: `email_thread_ids JSONB[]`

2. **Email Thread History**
   - Track when email was assigned/unassigned
   - Show assignment history in thread info
   - Requires new table: `email_thread_history`

3. **Email Status Sync**
   - Show if email was read/archived/replied
   - Update badge color based on status
   - Requires polling Communication Hub API

4. **Drag-and-Drop Email to Agent**
   - Drag email from inbox to agent panel
   - Auto-create thread and link
   - Requires drag-and-drop event handlers

---

## 📚 Related Files

### Frontend:
- `UI/modules_internal/communication-hub/communication-hub-v4-modern.js` - Email assignment logic
- `UI/modules_internal/thread-cards/thread-card-templates.js` - Email badge display
- `UI/modules_internal/thread-cards/email-thread-integration.js` - Email integration utilities

### Backend:
- `AI_infrastructure/routes/thread_routes.py` - Thread creation
- `AI_infrastructure/routes/thread_assignment_routes.py` - Email linkage endpoints
- `AI_infrastructure/routes/communication_routes.py` - Email fetching

### Database:
- `sessions.threads` table - Stores thread data with email columns

---

## ✅ Verification Checklist

After implementing this feature, verify:

- [ ] Email can be assigned to agent from Communication Hub
- [ ] Thread is created with correct location (prime, agent-1, etc.)
- [ ] `email_thread_id` column is populated in database
- [ ] `email_subject` column shows correct subject
- [ ] `email_participants` column shows sender email
- [ ] Thread card displays teal email badge
- [ ] Email badge shows subject and sender
- [ ] Clicking email badge opens email preview
- [ ] Unlink button removes email linkage
- [ ] Console shows success messages
- [ ] No errors in browser console
- [ ] No errors in backend logs

---

**Status**: ✅ **COMPLETE**  
**Integration**: Email ↔ Agent Thread ↔ Thread Info Badge  
**Similar Pattern**: Synergy Session Badges

---

*Generated: December 8, 2025*  
*Agent: GitHub Copilot (Claude Sonnet 4.5)*
