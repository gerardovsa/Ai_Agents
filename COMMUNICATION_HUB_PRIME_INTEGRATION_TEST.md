# Communication Hub Prime Integration - End-to-End Test Plan
**Date:** December 26, 2025
**Component:** communication-hub-v4-modern.js (6,314 lines)
**Status:** ✅ COMPILED - 0 Syntax Errors

---

## 🎯 Test Objective
Verify that assigning an email to "Prime-Loaded" automatically:
1. Creates thread with location="prime-loaded"
2. Opens Prime AI sidebar
3. Loads email content as first message
4. Sends task-specific prompt automatically
5. Streams AI response

---

## 📋 Pre-Test Checklist

### ✅ Component Status
- [x] communication-hub-v4-modern.js - **0 syntax errors**
- [x] prime_ai_chat.js - Available
- [x] thread-manager-interactions.js - Available
- [x] ThreadManager.loadThreadInPrime() - Function exists
- [x] sendChatMessage() - Global function exists

### 🔧 Dependencies Required
- **ThreadManager** - Thread management system
- **EmailAIFormatter** - Email-to-AI prompt converter
- **AttachmentProcessor** - File processing
- **UnifiedMessageRenderer** - Message display
- **window.UserAuth** - User authentication
- **sendChatMessage()** - Prime message sender

---

## 🧪 Test Scenarios

### **Scenario 1: Assign Email to Prime-Loaded (Summarize Task)**

**Setup:**
1. Open Communication Hub (email inbox)
2. Select any email from the table
3. Right-click on email row → "Assign to Agent" → Select "Prime-Loaded"
4. Choose task type: "Summarize"

**Expected Flow:**
```javascript
assignEmailToAgentWithTask(emailId, 'Prime-Loaded', 27, 'summarize', cell)
  ↓
1. Fetches full email content (body_text, attachments)
2. Creates thread with location="prime-loaded"
3. Links email to thread in relation_threads table
  ↓
loadThreadIntoAgentAndTriggerWithTask(threadSlug, 'prime-loaded', emailData, attachments, 'summarize')
  ↓
4. ThreadManager.loadThreadInPrime(threadSlug)
   - Opens Prime sidebar
   - Clears messages container
   - Loads thread messages
   - Updates Prime header with thread title
  ↓
5. Updates thread location to 'prime-loaded' via API
6. Refreshes ThreadManager
7. Waits 300ms for UI to render
  ↓
8. Populates ai-chat-input with prompt:
   "Please provide a clear, concise summary of this email, highlighting the key points and any action items."
  ↓
9. Calls sendChatMessage()
   - Adds user message bubble
   - Sends to Claude API
   - Streams assistant response
```

**Expected UI Result:**
```
┌────────────────────────────────────────┐
│ AI Prime Sidebar (Thread: 176675...)   │
├────────────────────────────────────────┤
│ 👤 USER:                               │
│ Please provide a clear, concise        │
│ summary of this email, highlighting    │
│ the key points and any action items.   │
├────────────────────────────────────────┤
│ 🤖 ASSISTANT (streaming...):           │
│ Here's a summary of the email:         │
│ • Main point: ...                      │
│ • Action items: ...                    │
│ [AI continues...]                      │
└────────────────────────────────────────┘
```

**Success Criteria:**
- ✅ Prime sidebar opens automatically
- ✅ Email content NOT visible in chat (only task prompt)
- ✅ AI response streams in real-time
- ✅ No console errors
- ✅ Thread location = "prime-loaded" in database

---

### **Scenario 2: Assign Email to Prime-Loaded (Generate Quote Task)**

**Setup:**
1. Select email requesting quote for products
2. Assign to Prime-Loaded → Task: "Generate Quote"

**Expected Prompt:**
```
Please analyze this email and generate a comprehensive quote for the customer.

STEP 1: EXTRACT AVAILABLE INFORMATION
- Product/service requested
- Quantities mentioned
- Sizes/dimensions specified
- Materials/finishes stated
- Deadline/turnaround requirements
- Customer name and contact details

STEP 2: QUERY FRED DATABASE FOR CUSTOMER HISTORY
[includes 3 rounds of SQL queries with inhouse_execute_query tool]

STEP 3: FILL MISSING SPECIFICATIONS
Use historical data to complete calculator requirements...

STEP 4: GENERATE QUOTE USING APPROPRIATE CALCULATOR
You have access to 80+ printing quote calculators...

STEP 5: DRAFT PROFESSIONAL QUOTE
Include line items, prices, turnaround, payment terms...

STEP 6: ADD VALUE SUGGESTIONS
Recommend upgrades based on history...
```

**Success Criteria:**
- ✅ Detailed multi-step prompt sent
- ✅ AI begins executing database queries
- ✅ AI uses quote calculators
- ✅ Professional quote generated
- ✅ No manual intervention required

---

### **Scenario 3: Assign Email with Attachments to Prime-Loaded**

**Setup:**
1. Select email with PDF attachments (e.g., logo.pdf)
2. Assign to Prime-Loaded → Task: "Analyze"

**Expected Behavior:**
```javascript
processedAttachments = [
  {
    filename: 'logo.pdf',
    detected_type: 'pdf',
    base64_data: '...',
    mime_type: 'application/pdf'
  }
]

messageContent = [
  { type: 'text', text: 'Please analyze this email...' },
  { type: 'image', source: { type: 'base64', media_type: 'image/png', data: '...' } }
]
```

**Success Criteria:**
- ✅ Attachments processed before sending
- ✅ Multimodal message sent to Claude
- ✅ AI acknowledges attachments in response
- ✅ No "attachment failed to process" errors

---

### **Scenario 4: Null Safety - Assign from Preview Panel**

**Setup:**
1. Click on email in table (opens preview panel on right)
2. In preview panel, click "Assign to Agent" → Prime-Loaded
3. Note: `cell = null` because not assigned from table

**Expected Behavior:**
```javascript
assignEmailToAgentWithTask(emailId, 'Prime-Loaded', 27, 'summarize', null)
  ↓
// Null checks pass
if (cell && cell.getElement) {
  // Skipped - cell is null
}

// Fetch from state instead
emailData = this.state.emails.find(e => e.id === emailId);

// Cell update skipped
if (cell && cell.getRow) {
  // Skipped - cell is null
} else {
  this.state.tabulatorTable.redraw(); // Redraw entire table
}
```

**Success Criteria:**
- ✅ No "Cannot read properties of null" errors
- ✅ Assignment succeeds without cell reference
- ✅ Prime opens and processes email
- ✅ Table redraws to show assignment

---

### **Scenario 5: Database Location Format**

**Setup:**
1. Assign email to Prime-Loaded

**Expected Database State:**
```sql
-- threads table
INSERT INTO threads (thread_slug, location, ...)
VALUES ('1766755242652', 'prime-loaded', ...);

-- relation_threads table
INSERT INTO relation_threads (email_id, thread_slug, location, ...)
VALUES (12345, '1766755242652', 'prime-loaded', ...);
```

**Success Criteria:**
- ✅ location = "prime-loaded" (TEXT format)
- ✅ NOT agentId = 27 (NUMERIC format)
- ✅ No CheckViolation: chk_location_valid error
- ✅ Thread queryable by location filter

---

## 🔍 Manual Testing Steps

### **Step 1: Start Flask Server**
```powershell
cd c:\Users\gpoli\GIT\AI_agents\AI_infrastructure
python flask_app.py
```
**Expected:** Server starts on port 5001, tool registry loads

### **Step 2: Open Business AI Platform**
```
http://localhost:5001/UI/business-ai-platform-v2.html
```
**Expected:** Platform loads, user authenticated

### **Step 3: Open Communication Hub**
- Click "Communication Hub" in left sidebar
- **Expected:** Email inbox loads with table

### **Step 4: Assign Email to Prime-Loaded**
1. Right-click on any email row
2. Select "Assign to Agent" → "Prime-Loaded"
3. Select task: "Summarize"
4. Click "Assign"

**Expected Console Logs:**
```
✅ [CommunicationHub] Assigning email 12345 to agent: Prime-Loaded with task: summarize
✅ [CommunicationHub] Full email data fetched
✅ [CommunicationHub] Thread created: 1766755242652
✅ [CommunicationHub] Email linked to thread
✅ [Interactions] Loading thread in Prime: Email: Subject...
✅ [Interactions] Thread assigned to prime-loaded: 1766755242652
✅ [Interactions] Rendering 0 messages...
✅ [CommunicationHub] Loaded thread 1766755242652 into Prime
✅ [CommunicationHub] Updated thread location to prime-loaded
✅ [CommunicationHub] Sent summarize task to Prime
✅ [Prime] User message added via UnifiedMessageRenderer
✅ [Prime] Streaming response...
```

**Expected UI:**
- Prime sidebar opens on right
- User message visible with task prompt
- AI assistant message streams below
- No error toasts

### **Step 5: Verify Database**
```sql
-- Check thread location
SELECT thread_slug, location, title 
FROM sessions.threads 
WHERE thread_slug = '1766755242652';

-- Expected: location = 'prime-loaded'

-- Check email-thread relationship
SELECT email_id, thread_slug, location
FROM sessions.relation_threads
WHERE thread_slug = '1766755242652';

-- Expected: location = 'prime-loaded'
```

### **Step 6: Test Other Task Types**
Repeat Step 4 with:
- [ ] Generate Quote
- [ ] Draft Reply
- [ ] Extract Tasks
- [ ] Analyze
- [ ] Discuss

---

## ❌ Common Failure Points

### **Issue 1: Prime sidebar doesn't open**
**Symptom:** Assignment succeeds but sidebar stays closed
**Likely Cause:** ThreadManager.loadThreadInPrime() failed
**Debug:**
```javascript
console.log('ThreadManager exists?', typeof ThreadManager !== 'undefined');
console.log('loadThreadInPrime exists?', typeof ThreadManager?.loadThreadInPrime === 'function');
```

### **Issue 2: Message not sent automatically**
**Symptom:** Prime opens but no user message appears
**Likely Cause:** sendChatMessage() not found or input not populated
**Debug:**
```javascript
console.log('Prime input:', document.getElementById('ai-chat-input'));
console.log('Input value:', document.getElementById('ai-chat-input')?.value);
console.log('sendChatMessage exists?', typeof sendChatMessage === 'function');
```

### **Issue 3: Database constraint error**
**Symptom:** CheckViolation: chk_location_valid
**Likely Cause:** agentId sent as number instead of text
**Debug:**
```javascript
console.log('Location value:', location);
console.log('Location type:', typeof location);
// Expected: "prime-loaded" (string)
```

### **Issue 4: "Cannot read properties of null"**
**Symptom:** Error when assigning from preview panel
**Likely Cause:** Missing null checks for cell parameter
**Debug:**
```javascript
console.log('Cell provided?', cell !== null);
console.log('Cell has getElement?', cell?.getElement !== undefined);
```

---

## 📊 Test Results Template

```
Date: _____________
Tester: _____________

| Scenario | Status | Notes |
|----------|--------|-------|
| 1. Summarize Task | ⬜ Pass ⬜ Fail | |
| 2. Generate Quote | ⬜ Pass ⬜ Fail | |
| 3. With Attachments | ⬜ Pass ⬜ Fail | |
| 4. From Preview Panel | ⬜ Pass ⬜ Fail | |
| 5. Database Location | ⬜ Pass ⬜ Fail | |

Console Errors: _______________
Browser: _______________
Flask Version: _______________
```

---

## ✅ Sign-Off Criteria

All scenarios must pass with:
- ✅ 0 console errors
- ✅ 0 database constraint violations
- ✅ 0 null reference errors
- ✅ Prime opens automatically
- ✅ AI responds within 5 seconds
- ✅ Thread location correctly set

**Approved By:** _____________
**Date:** _____________
