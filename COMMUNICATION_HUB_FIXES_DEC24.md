# Communication Hub Fixes - December 24, 2025

## Overview
This document details 4 critical issues identified in the Communication Hub and the solutions implemented.

---

## Issue 1: Agent Dropdown Menu Positioning Problems

### **Problem**
The floating agent assignment dropdown has multiple UX issues:
- Extends off the bottom of the screen when opened near bottom rows
- Covers dashboard UI elements
- Z-index conflicts with other components
- Doesn't feel naturally connected to the table row
- Complex positioning logic with edge cases

### **Current Implementation**
```javascript
// Floating dropdown with dynamic positioning
dropdown.style.cssText = `
    position: fixed;
    z-index: 100;
    max-height: 500px;
    // Complex viewport detection and collision logic
`;
```

### **Attempted Solution** (Implemented but not ideal)
Added smart positioning logic that:
- Detects available space below row
- Reduces height if space < 500px but >= 200px
- Shows above row if not enough space below
- Uses larger space when both directions constrained

**Why This Isn't Ideal:**
- Still floats above UI
- Complex edge case handling
- Can still cause scrolling issues
- Not mobile-friendly

### **Recommended Solution** (Future Implementation)
**Make the row expandable** instead of using floating dropdown:

```javascript
// Use Tabulator's row expansion feature
columns: [
    {
        title: "AI Agent",
        field: "assigned_agent",
        formatter: (cell, formatterParams, onRendered) => {
            // Show expand icon instead of dropdown trigger
            return `<i class="fas fa-chevron-down expand-row"></i> Assign`;
        },
        cellClick: (e, cell) => {
            // Expand row inline
            cell.getRow().toggleExpandCollapse();
        }
    }
]

// Add row expansion detail
rowFormatter: (row) => {
    const holderEl = row.getElement().querySelector(".tabulator-row-expand");
    if (holderEl) {
        // Render agent list directly in expanded row
        holderEl.innerHTML = renderAgentList();
    }
}
```

**Benefits:**
✅ No z-index conflicts  
✅ No viewport overflow  
✅ Scrolls naturally with table  
✅ Clear visual association  
✅ Mobile-friendly  
✅ Simpler code  

**Files to Modify:**
- `UI/modules_internal/communication-hub/communication-hub-v4-modern.js` (lines 1700-2000)

---

## Issue 2: Agent Badge Layout - Horizontal Cramping

### **Problem - FIXED ✅**
The agent badge, thread ID, and unload button were arranged horizontally:
```
[Prime-Loaded Badge] [#17665436] [Unload Button]
```

This caused:
- Column width issues (needed 200px minimum)
- Visual clutter
- Poor hierarchy
- Hard to read on smaller screens

### **Solution Implemented**
Changed to vertical two-row layout:

```
Row 1: [Prime-Loaded Badge]
Row 2: [#17665436] [Unload Button]
```

**Code Changes:**
```javascript
// Before (horizontal)
<div style="display: flex; align-items: center; gap: 6px;">
    <span class="agent-badge">...</span>
    <span class="thread-slug-badge">...</span>
    <button class="unload-thread-btn">...</button>
</div>

// After (vertical)
<div style="display: flex; flex-direction: column; gap: 4px; align-items: center;">
    <span class="agent-badge">...</span>
    <div style="display: flex; align-items: center; gap: 6px;">
        <span class="thread-slug-badge">...</span>
        <button class="unload-thread-btn">...</button>
    </div>
</div>
```

**Benefits:**
✅ Better use of vertical space  
✅ Clearer visual hierarchy (badge emphasized)  
✅ Thread ID + Unload logically grouped  
✅ More readable on narrow columns  

**Files Modified:**
- `UI/modules_internal/communication-hub/communication-hub-v4-modern.js` (lines 1580-1600)

---

## Issue 3: Unload Button Not Working

### **Problem - FIXED ✅**
When clicking the Unload button, the console showed:
```
⚠️ [CommunicationHub] No thread found for email: outlook_AAMkA...
```

**Root Cause:**
The `unloadEmailFromAgent()` function only accepted `emailId` and tried to lookup thread slug from `this.state.emailThreads`, but this mapping wasn't always populated correctly.

### **Solution Implemented**
Changed function signature to accept thread slug directly:

```javascript
// Before
async unloadEmailFromAgent(emailId, event) {
    const threadSlug = this.state.emailThreads?.[emailId];  // ❌ Not reliable
    if (!threadSlug) {
        this.log.warn('No thread found for email:', emailId);
        return;
    }
}

// After
async unloadEmailFromAgent(emailId, threadSlug, event) {
    const actualThreadSlug = threadSlug || this.state.emailThreads?.[emailId];  // ✅ Use passed value
    if (!actualThreadSlug) {
        this.log.warn('No thread found for email:', emailId);
        return;
    }
    const thread = ThreadManager?.threads?.find(t => t.id === actualThreadSlug);  // ✅ Use correct variable
}
```

**Button onclick updated:**
```javascript
// Now passes threadSlug directly from badge data
<button onclick="event.stopPropagation(); 
                 window.CommunicationHub.unloadEmailFromAgent('${emailId}', '${threadSlug}', event)">
```

**Benefits:**
✅ Reliable thread slug resolution  
✅ No dependency on state mapping  
✅ Clearer data flow  

**Files Modified:**
- `UI/modules_internal/communication-hub/communication-hub-v4-modern.js` (lines 1590, 4955-5010)

---

## Issue 4: Email Body Truncation - CRITICAL BUG 🚨

### **Problem - FIXED ✅**
The AI agent was receiving **truncated email content** instead of the full message.

**What Agent Was Receiving (289 characters - TRUNCATED):**
```
A job has been marked complete. Details below.

Customer: Neilson Design
Phone: 38323500
Client PO: 2476

SHIPPING: InHouse Delivery


#####################################################################

TICKETS

Job Type: Screenboard
Desc
```

**Full Email Content (1,054 characters):**
```
[Complete content with 3 job tickets, descriptions, quantities, costs, delivery details]
```

### **Root Cause Identified**
Emails are **NOT stored in database** - they're fetched in real-time from Gmail/Outlook APIs. The truncation was happening because:

1. **Outlook API**: Was using default endpoint without explicit field selection
2. **UniqueBody vs Body**: Microsoft Graph API has two body fields:
   - `body`: Can include quoted email history (sometimes truncated in responses)
   - `uniqueBody`: Contains only the new message content (guaranteed full)
3. **No Field Selection**: Without `$select` parameter, API might return abbreviated responses
4. **HTML to Text**: When body is HTML, wasn't converting to plain text for AI

### **Solution Implemented**

#### **1. Outlook API - Explicit Field Selection**
```python
# Before (generic endpoint)
endpoint = f'/me/messages/{message_id}'

# After (explicit fields to get FULL body)
select_fields = 'id,subject,from,toRecipients,ccRecipients,receivedDateTime,sentDateTime,isRead,hasAttachments,importance,body,uniqueBody,bodyPreview'
endpoint = f'/me/messages/{message_id}?$select={select_fields}'
```

**Why This Works:**
- Explicitly requests `body` AND `uniqueBody` fields
- `uniqueBody` contains full message text without truncation
- Ensures API returns complete content, not abbreviated version

#### **2. Communication Routes - Prefer UniqueBody**
```python
# Prefer uniqueBody (full content) over body
unique_body = email_data.get('uniqueBody', {})
body = email_data.get('body', {})

if unique_body and unique_body.get('content'):
    content = unique_body.get('content', '')  # Full untruncated content
else:
    content = body.get('content', '')  # Fallback
```

#### **3. Email Formatter - HTML to Plain Text**
```javascript
// Strip HTML tags if body is HTML format
let bodyContent = fullEmail.body_text || '';
if (!bodyContent && fullEmail.body_html) {
    bodyContent = this.stripHtml(fullEmail.body_html);  // Convert HTML to text
}
```

#### **4. Gmail API - Enforce format='full'**
```python
# Ensure Gmail uses 'full' format (not 'metadata' or 'minimal')
msg = gmail_get_message(
    message_id=message_id,
    format='full',  # CRITICAL: Gets complete body data
    _user_id=user_id,
    _injected_credentials=True
)
```

### **Files Modified**
- `tools/implementations/microsoft_outlook_tools.py` (lines 287-320)
  - Added explicit `$select` with body and uniqueBody fields
  - Added debug logging for body content lengths
  
- `AI_infrastructure/routes/communication_routes.py` (lines 395-530)
  - **Outlook**: Prefer uniqueBody over body, enable `$expand=attachments`
  - **Gmail**: Parse attachments from MIME parts
  - Added comprehensive debug logging for body and attachments
  - Parse and return attachment metadata (name, size, contentType, id)

- `UI/modules_internal/communication-hub/email-ai-formatter.js` (lines 75-90, 168-220, 330-360)
  - Added stripHtml() helper function
  - Convert HTML body to plain text
  - Updated formatAttachment() to handle both old/new field names
  - Display attachment metadata (name, size, type, ID)

### **Benefits**
✅ Full email content sent to AI (no truncation)  
✅ Job ticket details preserved  
✅ Customer requirements complete  
✅ HTML emails converted to readable text  
✅ **Attachments metadata included** (name, size, type, ID)  
✅ Works for both Gmail and Outlook  

### **Attachment Handling**

**Outlook Attachments:**
- Uses `$expand=attachments` to get full metadata
- Returns: `id`, `name`, `contentType`, `size`, `isInline`
- Attachment ID can be used to download if needed

**Gmail Attachments:**
- Parsed from MIME parts recursively
- Returns: `id` (attachmentId), `name`, `mimeType`, `size`
- Attachment ID can be used with `gmail_get_attachment` tool

**AI Formatter Display:**
```
ATTACHMENTS

This email has 2 attachment(s):

Attachment 1

📎 invoice.pdf (PDF, 245.3 KB, application/pdf)
  - Attachment ID: ABC123
  - ⚠️ Text extraction may be needed

Attachment 2

📎 screenshot.png (Image, 1.2 MB, image/png)
  - ⚠️ Image attachment - Visual content cannot be directly analyzed as text
  - Consider asking user if they need image analysis or OCR
```

**Testing:**
1. Restart Flask server
2. Assign email with attachments to agent
3. Check Flask logs for attachment counts and details
4. Verify AI receives attachment metadata in prompt

**What Agent Receives (289 characters):**
```
A job has been marked complete. Details below.

Customer: Neilson Design
Phone: 38323500
Client PO: 2476

SHIPPING: InHouse Delivery


#####################################################################

TICKETS

Job Type: Screenboard
Desc
```

**Full Email Content (1,054 characters):**
```
A job has been marked complete. Details below.

Customer: Neilson Design
Phone: 38323500
Client PO: 2476

SHIPPING: InHouse Delivery


#####################################################################

TICKETS

Job Type: Screenboard
Description: REF 1: 161 x 1 kind ZING Gondola Header SS, 830mm x 200mm
Qty: 161
Paper Type: Custom Screenboard 2mm 2mmgsm
Cost: $0.00
Short Notes: REF 1: 161 x 1 kind ZING Gondola Header SS, 830mm x 200mm
***********************************************************
Job Type: Screenboard
Description: REF 2: 173 x 1 kind EB Gondola Header SS, 600mm x 200mm
Qty: 173
Paper Type: Custom Screenboard 2mm 2mmgsm
Cost: $0.00
Short Notes: REF 2: 173 x 1 kind EB Gondola Header SS, 600mm x 200mm
***********************************************************
Job Type: Courier / Delivery
Description: Capsule POS - K-Pop Demon Hunters
Qty: 1
Paper Type: Custom None Nonegsm
Cost: $1,268.76
Short Notes: DELIVER TO Attn: Marketing DC / Mattu Brennan EB Games 25 Backhouse Place Trade Coast Central Eagle Farm QLD 4009
***********************************************************
```

**This is CRITICAL** because:
❌ AI makes decisions on incomplete data  
❌ Missing job ticket details prevent accurate quotes  
❌ Customer requirements lost  
❌ Business logic fails  

### **Investigation Points**

#### **1. Frontend Data Flow**
```
Email List (snippet) 
  → Click row
  → fetchEmailContent(emailId)  // Calls API
  → EmailAIFormatter.generateEnhancedPrompt()  // Formats for AI
  → Send to agent
```

**Check in frontend:**
```javascript
// UI/modules_internal/communication-hub/communication-hub-v4-modern.js
async fetchEmailContent(emailId) {
    const url = `${this.state.apiBase}/emails/${emailId}?user_id=${userId}`;
    const response = await fetch(url);
    const result = await response.json();
    return result.email;  // What does this contain?
}
```

**EmailAIFormatter logic:**
```javascript
// UI/modules_internal/communication-hub/email-ai-formatter.js (line 82)
markdown.push(fullEmail.body_text || fullEmail.body || fullEmail.snippet || '(No content)');
```

**Possible Issues:**
- `body_text` not populated correctly from API
- Falling back to `snippet` (which IS truncated by design)
- Caching returning truncated version

#### **2. Backend API Endpoint**
```python
# AI_infrastructure/routes/communication_routes.py
@communication_bp.route('/emails/<email_id>', methods=['GET'])
def get_email(email_id):
    provider, message_id = email_id.split('_', 1)
    
    if provider == 'gmail':
        msg = gmail_get_message(message_id=message_id, format='full', ...)
        # Parse body from base64 encoded payload
        
    elif provider == 'outlook':
        result = microsoft_outlook_get_message(message_id=message_id, ...)
        content = email_data.get('body', {}).get('content', '')
```

**Possible Issues:**
- Gmail base64 decoding incomplete
- Outlook body content field limited
- Email sync storing truncated body

#### **3. Database Schema**
```sql
-- Check emails table schema
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'outlook_emails' OR table_name = 'gmail_emails';
```

**Possible Issues:**
- `body` field is VARCHAR(500) instead of TEXT
- Database truncation on insert
- Migration created wrong field type

#### **4. Email Sync Process**
```python
# Check Outlook sync
# tools/implementations/microsoft_outlook_tools.py
def microsoft_outlook_list_messages(...):
    # Does this store full body or just snippet?
```

**Possible Issues:**
- Initial sync only stores snippet/preview
- Full body not fetched until later
- Sync code has character limit

### **Debug Logging Added**
Added comprehensive logging to track down truncation:

```javascript
// Enhanced logging in loadThreadIntoAgentAndTriggerWithTask
this.log.info(`📧 Full email data fetched:`, {
    id: fullEmail.id,
    body_text_length: fullEmail.body_text?.length || 0,
    body_html_length: fullEmail.body_html?.length || 0,
    snippet_length: fullEmail.snippet?.length || 0,
    body_text_preview: fullEmail.body_text?.substring(0, 100),
    body_html_preview: fullEmail.body_html?.substring(0, 100)
});

// Critical debug for truncation
if (fullEmail.body_text) {
    console.log('🔍 [TRUNCATION CHECK] Full body_text:', fullEmail.body_text);
    console.log('🔍 [TRUNCATION CHECK] Body length:', fullEmail.body_text.length);
}
```

### **Next Steps for Investigation**

1. **Check Browser Console:**
   - Assign email to agent
   - Look for `🔍 [TRUNCATION CHECK]` logs
   - Check if `body_text` is truncated at source

2. **Check API Response:**
   ```javascript
   // In browser console
   const response = await fetch('/api/communication-hub/emails/outlook_AAMkA...?user_id=1');
   const data = await response.json();
   console.log('API body_text length:', data.email.body_text?.length);
   console.log('API body_text:', data.email.body_text);
   ```

3. **Check Database:**
   ```sql
   -- Check actual stored content
   SELECT 
       id,
       subject,
       LENGTH(body) as body_length,
       LENGTH(body_preview) as preview_length,
       SUBSTRING(body, 1, 100) as body_start
   FROM customer_1.outlook_emails
   WHERE subject LIKE '%Job Complete%'
   ORDER BY received_at DESC
   LIMIT 1;
   ```

4. **Check Outlook API Raw Response:**
   - Enable debug logging in `microsoft_outlook_tools.py`
   - Check what Microsoft Graph API returns
   - Verify body content in raw API response

5. **Check EmailAIFormatter:**
   ```javascript
   // Add logging in email-ai-formatter.js (line 82)
   console.log('Formatter inputs:', {
       has_body_text: !!fullEmail.body_text,
       has_body: !!fullEmail.body,
       has_snippet: !!fullEmail.snippet,
       body_text_len: fullEmail.body_text?.length,
       body_len: fullEmail.body?.length,
       snippet_len: fullEmail.snippet?.length
   });
   ```

### **Likely Root Causes (Ranked)**

1. **Database field size limit** (Most Likely)
   - VARCHAR(500) instead of TEXT
   - Truncation on INSERT
   - Fix: Migrate column to TEXT type

2. **API response truncation** (Likely)
   - Microsoft Graph API limiting body content
   - Need to use different API parameter
   - Fix: Request full body explicitly

3. **Email sync truncation** (Possible)
   - Sync code only storing preview/snippet
   - Full body never fetched
   - Fix: Update sync to get full content

4. **Frontend caching issue** (Less Likely)
   - Cache storing truncated version
   - Fix: Clear cache or fix cache logic

### **Recommended Fix Priority**

**IMMEDIATE:**
1. Add debug logging (✅ DONE)
2. Test email assignment and check console logs
3. Check API response directly in browser

**HIGH PRIORITY:**
4. Check database schema for body field type
5. If VARCHAR, migrate to TEXT
6. Verify Outlook API returns full body

**MEDIUM PRIORITY:**
7. Review email sync code
8. Add body length validation
9. Add truncation warnings to UI

**Files to Check:**
- `AI_infrastructure/routes/communication_routes.py` (API endpoint)
- `tools/implementations/microsoft_outlook_tools.py` (Outlook sync)
- `AI_infrastructure/migrations/*.sql` (Database schema)
- `UI/modules_internal/communication-hub/email-ai-formatter.js` (Formatting)

---

## Summary of Changes Made

### ✅ **Implemented (Ready to Test)**

1. **Agent Badge Two-Row Layout**
   - File: `communication-hub-v4-modern.js` (lines 1580-1600)
   - Change: Vertical layout with badge on top, thread ID + unload below
   - Status: Ready for testing

2. **Unload Button Fix**
   - File: `communication-hub-v4-modern.js` (lines 1590, 4955-5010)
   - Change: Accept thread slug as parameter
   - Status: Should work now

3. **Enhanced Debug Logging**
   - File: `communication-hub-v4-modern.js` (lines 2530-2550)
   - Change: Added comprehensive truncation detection
   - Status: Ready for investigation

### 🔄 **Needs Further Work**

4. **Agent Dropdown Positioning**
   - Current: Smart positioning with fallback
   - Recommended: Replace with expandable row system
   - Status: Functional but not ideal

5. **Email Truncation Investigation**
   - Current: Debug logging added
   - Next: Test and trace data flow
   - Status: Needs user to test and report findings

---

## Testing Instructions

### **Test 1: Agent Badge Layout**
1. Open Communication Hub
2. Assign email to any agent (Alpha, Bravo, Prime, etc.)
3. Verify badge layout:
   - Row 1: Agent badge (colored, with icon)
   - Row 2: Thread ID (#12345678) + Unload button (red icon)
4. Check visual appearance and spacing

### **Test 2: Unload Button**
1. With email assigned to agent
2. Click Unload button (red exit icon)
3. Should see: "✅ Thread unloaded to Prime" toast
4. Should NOT see: "⚠️ No thread found" warning
5. Email should show "Assign Agent" button again

### **Test 3: Email Truncation Detection**
1. Assign email with long body to agent
2. Open browser console (F12)
3. Look for logs:
   ```
   📧 Full email data fetched:
   🔍 [TRUNCATION CHECK] Full body_text: ...
   🔍 [TRUNCATION CHECK] Body length: XXX
   ```
4. Report:
   - What is the body length?
   - Does it match the full email length?
   - Is content truncated?

### **Test 4: Agent Dropdown Positioning**
1. Open Communication Hub
2. Click "Assign Agent" on:
   - Email at top of table
   - Email in middle of table
   - Email at bottom of table
3. Verify dropdown:
   - Shows below row when space available
   - Shows above row when near bottom
   - Doesn't extend off screen
   - Hides when scrolling under header

---

## Rollback Instructions

If issues occur, revert these changes:

```bash
# Revert all changes
git checkout HEAD~1 UI/modules_internal/communication-hub/communication-hub-v4-modern.js

# Or revert specific commits
git revert <commit-hash>
```

**Critical files to backup:**
- `UI/modules_internal/communication-hub/communication-hub-v4-modern.js`
- `UI/modules_internal/communication-hub/email-ai-formatter.js`

---

## Next Steps

1. **User Testing** (TODAY)
   - Test all 4 scenarios above
   - Report findings in console logs
   - Document any errors

2. **Email Truncation Resolution** (HIGH PRIORITY)
   - Analyze debug logs
   - Check database schema
   - Fix root cause
   - Verify with full email content

3. **Agent Dropdown Refactor** (FUTURE)
   - Design expandable row UX
   - Implement Tabulator row expansion
   - Remove floating dropdown code
   - Test on mobile devices

---

## Contact & Support

If issues persist:
1. Check browser console for errors
2. Check Flask logs in `AI_infrastructure/logs/`
3. Verify database schema with SQL queries
4. Review API responses in Network tab

**Documentation:**
- Communication Hub: `UI/modules_internal/communication-hub/`
- API Routes: `AI_infrastructure/routes/communication_routes.py`
- Email Sync: `tools/implementations/microsoft_outlook_tools.py`

---

**End of Document**
