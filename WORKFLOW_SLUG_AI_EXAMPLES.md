# Workflow Slug - AI Usage Examples

## How AI Accesses Workflows Using Slugs

This document provides real examples of how the AI can use workflow slugs to interact with automations.

## Available AI Tools

### Tool 1: `automation_get_workflow`
**Purpose:** Retrieve full workflow data by slug

**Usage:**
```python
automation_get_workflow(
    automation_id='email-to-sheets-automation'
)
```

**Returns:**
```json
{
  "automation": {
    "id": "email-to-sheets-automation",
    "slug": "email-to-sheets-automation",
    "title": "Email to Sheets Automation",
    "description": "Process incoming emails and log to Google Sheets",
    "status": "draft",
    "category": "operations",
    "ui_json": {
      "shapes": [
        {
          "id": "shape_1",
          "type": "trigger",
          "label": "New Email Received",
          "x": 200,
          "y": 100,
          "width": 220,
          "height": 90,
          "color": "#10B981",
          "text": "New Email Received\nTrigger: Gmail inbox monitoring"
        },
        {
          "id": "shape_2",
          "type": "tool",
          "label": "Parse Email Content",
          "x": 200,
          "y": 300,
          "text": "Parse Email Content\nExtract sender, subject, body"
        }
      ],
      "connections": [
        {
          "id": 1,
          "from": 1,
          "to": 2,
          "label": "email data"
        }
      ]
    }
  }
}
```

### Tool 2: `automation_list_workflows`
**Purpose:** List all workflows (optionally filter by category/status)

**Usage:**
```python
# Get all workflows
automation_list_workflows()

# Filter by category
automation_list_workflows(category='operations')

# Filter by status
automation_list_workflows(status='active')
```

**Returns:**
```json
{
  "workflows": [
    {
      "slug": "email-to-sheets-automation",
      "title": "Email to Sheets Automation",
      "status": "draft",
      "category": "operations"
    },
    {
      "slug": "daily-sales-report",
      "title": "Daily Sales Report Generator",
      "status": "active",
      "category": "sales"
    }
  ]
}
```

### Tool 3: `automation_save_workflow`
**Purpose:** Save/update workflow data

**Usage:**
```python
automation_save_workflow(
    automation_id='email-to-sheets-automation',
    title='Email to Sheets Automation (Updated)',
    description='Enhanced with error handling',
    ui_json={
        'shapes': [...],
        'connections': [...]
    },
    status='draft'
)
```

## Real Conversation Examples

### Example 1: User Drags Slug to Chat

**User Action:** Drags `email-to-sheets-automation` slug pill to AI chat

**User Message:**
```
[email-to-sheets-automation]
Can you explain what this workflow does step by step?
```

**AI Response Process:**
1. Detect slug in brackets: `email-to-sheets-automation`
2. Call tool: `automation_get_workflow('email-to-sheets-automation')`
3. Parse workflow data (6 shapes, 6 connections)
4. Analyze sequence and respond

**AI Response:**
```
I've analyzed the "Email to Sheets Automation" workflow. Here's what it does:

📧 Step-by-Step Flow:

1. **Trigger: New Email Received** (shape_1)
   - Monitors Gmail inbox for incoming emails
   - Activates when new message arrives

2. **Parse Email Content** (shape_2)
   - Extracts sender email, subject line, and body text
   - Prepares data for categorization

3. **Categorize Email** (shape_3)
   - Uses AI to classify as urgent/normal/spam
   - Determines routing for next steps

4. **Log to Sheets** (shape_4)
   - Appends row to Google Sheets
   - Records: timestamp, sender, subject, category

5. **Send Notification** (shape_5) - Conditional
   - IF email is urgent → sends Slack notification
   - Alerts team for immediate attention

6. **Complete** (shape_6)
   - Workflow finishes successfully
   - Email fully processed and logged

Would you like me to:
- Add error handling for failed API calls?
- Include email attachment processing?
- Add more categorization rules?
```

### Example 2: User Copies and Pastes Slug

**User Action:** Clicks slug pill (copies), then pastes in chat

**User Message:**
```
email-to-sheets-automation

Add a shape that checks if the email has attachments and saves them to Google Drive
```

**AI Response Process:**
1. Recognize slug format (lowercase, hyphens)
2. Call: `automation_get_workflow('email-to-sheets-automation')`
3. Get current workflow structure
4. Analyze where to insert new shape
5. Create new shape definition
6. Update connections
7. Call: `automation_save_workflow()` with updated data

**AI Response:**
```
✅ I've added an "Attachment Handler" shape to your workflow!

**Changes Made:**

New Shape Added:
- **ID:** shape_7
- **Type:** tool
- **Label:** "Check & Save Attachments"
- **Position:** (200, 250) - between Parse and Categorize
- **Description:** "If email has attachments, save to Google Drive"

Connections Updated:
- shape_2 → shape_7: "parsed data"
- shape_7 → shape_3: "with attachments saved"
- shape_7 → shape_3: "no attachments" (alternate path)

The workflow now:
1. Receives email
2. Parses content
3. **Checks for attachments** (NEW)
4. **Saves to Google Drive if present** (NEW)
5. Categorizes email
6. Logs to Sheets
7. Sends notification (if urgent)
8. Completes

Would you like me to:
- Add file type validation (only PDFs/images)?
- Include virus scanning for attachments?
- Send notification when large files are saved?
```

### Example 3: User Uses "Send to AI" Button

**User Action:** Clicks "Send to AI" button on canvas

**AI Receives:**
```
[AUTOMATION: Email to Sheets Automation (email-to-sheets-automation)]
```

**User Message:**
```
[AUTOMATION: Email to Sheets Automation (email-to-sheets-automation)]
Review this workflow and suggest improvements for reliability and error handling
```

**AI Response Process:**
1. Extract slug from parentheses: `email-to-sheets-automation`
2. Call: `automation_get_workflow('email-to-sheets-automation')`
3. Analyze all shapes and connections
4. Identify potential failure points
5. Generate improvement recommendations

**AI Response:**
```
I've reviewed your "Email to Sheets Automation" workflow. Here are my recommendations for improving reliability:

🔴 **Critical Issues:**

1. **No Error Handling on Gmail Trigger**
   - Problem: If Gmail API fails, workflow stops silently
   - Fix: Add retry logic with exponential backoff
   - Impact: Prevents missed emails during API outages

2. **Missing Sheet Write Validation**
   - Problem: No confirmation that data was written to Sheets
   - Fix: Add verification step to check row was appended
   - Impact: Ensures data integrity

🟡 **Warnings:**

3. **Single Point of Failure: Categorize Step**
   - Problem: If AI categorization fails, workflow stops
   - Fix: Add fallback to rule-based categorization
   - Impact: Workflow continues even if AI is unavailable

4. **No Slack Notification Timeout**
   - Problem: Could hang indefinitely if Slack API is down
   - Fix: Add 5-second timeout with retry
   - Impact: Prevents workflow from getting stuck

🟢 **Enhancements:**

5. **Add Duplicate Detection**
   - Benefit: Prevents logging same email multiple times
   - Implementation: Check Sheet for existing message ID before append

6. **Add Execution Logging**
   - Benefit: Track success/failure rates
   - Implementation: Log each step's result to database

Would you like me to implement any of these improvements?
I can add the fixes directly to your workflow.
```

### Example 4: Comparing Two Workflows

**User Message:**
```
Compare these two workflows:
email-to-sheets-automation
daily-sales-report

Which one is better structured?
```

**AI Response Process:**
1. Recognize two slugs
2. Call: `automation_get_workflow('email-to-sheets-automation')`
3. Call: `automation_get_workflow('daily-sales-report')`
4. Compare structure, connections, complexity
5. Provide analysis

**AI Response:**
```
I've analyzed both workflows. Here's a comparison:

📊 **Workflow Comparison:**

| Metric | Email to Sheets | Daily Sales Report |
|--------|----------------|-------------------|
| Shapes | 6 | 8 |
| Connections | 6 | 8 |
| Conditional Branches | 1 (urgent check) | 2 (amount, approval) |
| External APIs | 3 (Gmail, Sheets, Slack) | 4 (DB, Charts, Email, Drive) |
| Complexity | Medium | High |

🏆 **Better Structured:** Daily Sales Report

**Reasons:**

1. **Clearer Separation of Concerns**
   - Sales Report separates data fetch, processing, and output
   - Email workflow mixes parsing and categorization

2. **More Robust Error Handling Points**
   - Sales Report has validation after each major step
   - Email workflow missing validation checks

3. **Better Parallel Processing**
   - Sales Report generates charts while formatting report
   - Email workflow is strictly sequential

4. **Archival & Audit Trail**
   - Sales Report saves to Google Drive for records
   - Email workflow only logs to Sheets (no backup)

⚠️ **However:**

Email to Sheets is simpler and **more appropriate for its use case**:
- Event-driven (email arrives) vs scheduled (daily)
- Simple logging vs complex report generation
- Lower risk tolerance needed

**Recommendation:**
Both are well-designed for their purposes. Consider:
- Adding archival step to Email workflow (like Sales Report)
- Simplifying Sales Report if charts aren't always needed
```

### Example 5: Bulk Operations

**User Message:**
```
Get all my draft workflows and activate them
```

**AI Response Process:**
1. Call: `automation_list_workflows(status='draft')`
2. Get list of draft workflow slugs
3. For each slug, call: `automation_activate_workflow(slug)`
4. Report results

**AI Response:**
```
I found 4 draft workflows. Here's what I did:

✅ **Activated Successfully:**

1. **email-to-sheets-automation**
   - Status: draft → active
   - Trigger: Email monitoring started
   - Next execution: When new email arrives

2. **daily-sales-report**
   - Status: draft → active
   - Trigger: Daily at 9:00 AM UTC
   - Next execution: Tomorrow at 09:00

3. **customer-onboarding-flow**
   - Status: draft → active
   - Trigger: New customer signup
   - Next execution: When signup event occurs

❌ **Failed to Activate:**

4. **invoice-approval-workflow**
   - Error: Missing required configuration
   - Issue: No approval email address set
   - Action Required: Add finance manager email in shape_5

**Summary:**
- 3 of 4 workflows now active
- 1 requires configuration before activation
- All active workflows are monitoring their triggers

Would you like me to help configure the invoice approval workflow?
```

## Pattern: Slug Recognition

**AI should recognize these formats:**

```
Bracketed:
[email-to-sheets-automation]
[daily-sales-report]

Automation Tag:
[AUTOMATION: Email to Sheets Automation (email-to-sheets-automation)]

Plain:
email-to-sheets-automation
daily-sales-report

In sentence:
"I want to modify email-to-sheets-automation to add..."
```

## Pattern: Slug Validation

**AI should validate slugs before API calls:**

```python
def is_valid_slug(slug: str) -> bool:
    """Check if string is a valid workflow slug"""
    import re
    
    # Must be lowercase letters, numbers, hyphens, underscores only
    pattern = r'^[a-z0-9_-]+$'
    
    # Must be 1-50 characters
    if not slug or len(slug) > 50:
        return False
    
    return bool(re.match(pattern, slug))

# Examples
is_valid_slug('email-to-sheets-automation')  # ✅ True
is_valid_slug('daily_sales_report')          # ✅ True
is_valid_slug('UPPERCASE')                   # ❌ False (uppercase)
is_valid_slug('has space')                   # ❌ False (space)
is_valid_slug('has@special')                 # ❌ False (special char)
is_valid_slug('')                            # ❌ False (empty)
```

## Common Use Cases

### 1. Get Workflow Details
```
User: email-to-sheets-automation show me the details
AI: [Calls automation_get_workflow, displays shapes/connections]
```

### 2. Modify Workflow
```
User: email-to-sheets-automation add error handling
AI: [Gets workflow, adds try/catch shapes, saves back]
```

### 3. Execute Workflow
```
User: email-to-sheets-automation run it now
AI: [Calls automation_execute_workflow, monitors execution]
```

### 4. Check Status
```
User: email-to-sheets-automation what's the status?
AI: [Gets workflow, checks status field, reports last execution]
```

### 5. Export Workflow
```
User: email-to-sheets-automation export as JSON
AI: [Calls automation_export, provides download link]
```

## Error Handling

### Workflow Not Found
```
User: nonexistent-workflow-slug
AI: 
"I couldn't find a workflow with the slug 'nonexistent-workflow-slug'.

Available workflows:
- email-to-sheets-automation
- daily-sales-report
- customer-onboarding-flow
- invoice-approval-workflow

Did you mean one of these?"
```

### Invalid Slug Format
```
User: INVALID SLUG WITH SPACES
AI:
"That doesn't look like a valid workflow slug. Slugs should be:
- Lowercase letters only
- Numbers and hyphens/underscores allowed
- No spaces or special characters

Example: email-to-sheets-automation

Would you like me to list your workflows?"
```

### API Error
```
User: email-to-sheets-automation
AI: [API call fails with 500 error]
Response:
"I encountered an error while fetching the workflow:
- Error: Internal server error (500)
- Workflow: email-to-sheets-automation
- Time: 2025-11-19 12:30:45 UTC

The workflow server might be experiencing issues. 
Would you like me to try again?"
```

## Summary

**The slug system provides:**
- ✅ Unique identifier for each workflow
- ✅ Easy copy/paste between UI and AI
- ✅ Drag-and-drop from workflow list to chat
- ✅ Direct API access using slug
- ✅ All CRUD operations supported
- ✅ Validation and error handling
- ✅ Clear, human-readable format

**AI can use slugs to:**
- ✅ Retrieve workflow data
- ✅ Modify workflow structure
- ✅ Execute workflows
- ✅ Check execution history
- ✅ Compare multiple workflows
- ✅ Activate/deactivate workflows
- ✅ Export workflow definitions

**Everything is production-ready and working!**

---

**Last Updated:** November 19, 2025  
**Status:** Production Ready ✅
