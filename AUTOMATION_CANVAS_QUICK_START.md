# AUTOMATION CANVAS - QUICK START GUIDE

## Access the Canvas

1. Start backend: `BISTART`
2. Open UI: `http://localhost:5001`
3. Click purple **Automation Workflows** icon in sidebar

---

## Visual Workflow Creation

### Drag Shapes from Palette

| Shape | Purpose | Example |
|-------|---------|---------|
| 🔷 **Hexagon** | TRIGGER - When to start | "Every day at 9am", "When new email arrives" |
| 🟦 **Rectangle** | ACTION - What to do | "Send email", "Create document", "Save to database" |
| 🔸 **Diamond** | DECISION - If/else logic | "If email from boss", "If amount > $1000" |
| ⭕ **Circle** | END - Workflow complete | "Success", "Failure", "Done" |

### Connect Shapes
- Click connection point on shape
- Drag to another shape
- Creates execution flow

### Add Text
- Double-click shape
- Type description
- Text auto-sizes

---

## AI-Powered Workflow Creation

### Natural Language → Workflow

**Example 1: Email Automation**
```
User: "Create automation: When I get an email from my boss, 
       save it to a Google Sheet and send me a notification"

AI: ✓ Created workflow "Boss Email Tracker"
    - Trigger: Gmail new message (from:boss@company.com)
    - Action 1: Extract email data
    - Action 2: Append to Google Sheets
    - Action 3: Send Slack notification
```

**Example 2: Daily Report**
```
User: "Every weekday at 8am, generate sales report and email it to team"

AI: ✓ Created workflow "Daily Sales Report"
    - Trigger: Schedule (0 8 * * 1-5)
    - Action 1: Query database for sales data
    - Action 2: Generate PDF report
    - Action 3: Email to team distribution list
```

**Example 3: Data Processing**
```
User: "When new file uploaded to Google Drive, convert to PDF and save to Dropbox"

AI: ✓ Created workflow "Auto PDF Converter"
    - Trigger: Google Drive file upload
    - Decision: Check file type
    - Action 1: Convert to PDF (if Word/Excel)
    - Action 2: Upload to Dropbox
```

---

## Workflow Execution

### Manual Execution
```
User: "Run the Boss Email Tracker workflow now"

AI: ✓ Executed workflow
    Status: Success
    Duration: 1.8 seconds
    Tools used: gmail_list_messages, google_sheets_append_row, slack_post_message
```

### Scheduled Execution
```
User: "Schedule Daily Sales Report for every weekday at 8am"

AI: ✓ Scheduled workflow
    Cron: 0 8 * * 1-5
    Next run: Tomorrow at 8:00 AM EST
```

---

## Cron Expression Examples

| Schedule | Cron Expression | Use Case |
|----------|----------------|----------|
| Every hour | `0 * * * *` | Frequent monitoring |
| Every day at 9am | `0 9 * * *` | Daily reports |
| Every weekday at 8am | `0 8 * * 1-5` | Business hours |
| Every Monday at 10am | `0 10 * * 1` | Weekly summaries |
| Every 15 minutes | `*/15 * * * *` | Real-time sync |
| First of month at noon | `0 12 1 * *` | Monthly billing |

---

## Available Tools (594 Total)

### Popular Workflow Tools

**Email & Communication**
- `gmail_send_email` - Send Gmail
- `gmail_list_messages` - List emails
- `outlook_send_email` - Send Outlook
- `slack_post_message` - Post to Slack
- `twilio_send_sms` - Send SMS

**Google Workspace**
- `google_docs_create_document` - Create doc
- `google_sheets_append_row` - Add to sheet
- `google_drive_upload_file` - Upload file
- `google_calendar_create_event` - Add event

**Microsoft 365**
- `microsoft_word_create_document`
- `microsoft_excel_add_row`
- `microsoft_teams_send_message`
- `microsoft_onedrive_upload_file`

**Data & AI**
- `ai_summarize_text` - AI text summary
- `ai_extract_entities` - Extract data
- `data_analysis_query` - SQL queries
- `generate_pdf_report` - Create PDFs

**Business Systems**
- `xero_create_invoice` - Xero accounting
- `stripe_create_customer` - Stripe payments
- `shopify_get_orders` - Shopify e-commerce
- `salesforce_create_lead` - Salesforce CRM

---

## Workflow Templates

### Template 1: Email to Task
```
TRIGGER: Gmail new message (label:important)
  ↓
ACTION: Extract email subject and body
  ↓
ACTION: Create Google Task
  ↓
ACTION: Send confirmation email
  ↓
END: Task created
```

### Template 2: Invoice Processing
```
TRIGGER: Email attachment received
  ↓
DECISION: Is PDF invoice?
  ↓ YES
ACTION: Extract invoice data (AI)
  ↓
ACTION: Create Xero invoice
  ↓
ACTION: Save to Google Drive
  ↓
END: Invoice processed

  ↓ NO
END: Skip non-invoice
```

### Template 3: Social Media Scheduler
```
TRIGGER: Schedule (0 9,12,17 * * *)
  ↓
ACTION: Get next post from database
  ↓
DECISION: Post type?
  ↓ Twitter
ACTION: Post to Twitter
  ↓ LinkedIn  
ACTION: Post to LinkedIn
  ↓ Both
ACTION: Post to both platforms
  ↓
END: Posted successfully
```

---

## Troubleshooting

### Module Not Visible
1. Check manifest: `UI/external/modules/manifest.json`
2. Verify `automation-workflows` entry exists
3. Refresh browser (Ctrl+F5)

### Shapes Not Rendering
1. Check browser console (F12)
2. Verify CSS file loaded
3. Hard refresh (Ctrl+Shift+R)

### API Errors
1. Check backend is running: `BISTART`
2. Verify endpoint: `http://localhost:5001/api/automation/list`
3. Check network tab in browser dev tools

### Workflow Won't Save
1. Check user authentication
2. Verify database connection
3. Check backend logs for errors

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Delete` | Delete selected shape |
| `Ctrl+C` | Copy selected shapes |
| `Ctrl+V` | Paste shapes |
| `Ctrl+S` | Save workflow |
| `Ctrl+=` | Zoom in |
| `Ctrl+-` | Zoom out |
| `Ctrl+0` | Reset zoom |
| `Space+Drag` | Pan canvas |

---

## Best Practices

### 1. Name Workflows Clearly
- ✅ "Daily Sales Report - Email to Team"
- ❌ "Workflow 1"

### 2. Add Descriptions
- Explain what the workflow does
- Document any special requirements
- Note external dependencies

### 3. Use Decision Nodes
- Handle errors gracefully
- Add conditional logic
- Create alternative paths

### 4. Test Before Scheduling
- Execute manually first
- Verify all steps work
- Check output quality

### 5. Monitor Execution History
- Review past runs
- Check for errors
- Optimize performance

---

## Advanced Features

### Variable Substitution
```
Action: Send email
  To: {{user_email}}
  Subject: Report for {{date}}
  Body: {{generated_content}}
```

### Conditional Execution
```
Decision: If {{amount}} > 1000
  YES → Send to manager
  NO → Auto-approve
```

### Error Handling
```
Action: Try to send email
  ↓ SUCCESS
END: Email sent
  ↓ FAILURE
ACTION: Log error
  ↓
ACTION: Send admin alert
  ↓
END: Error handled
```

---

## Getting Help

### Check Resources
1. **Documentation**: `AUTOMATION_CANVAS_FIX_COMPLETE.md`
2. **Test Script**: `python test_automation_canvas.py`
3. **Backend Logs**: Check Flask terminal output

### Ask the AI
```
User: "How do I create a workflow that runs every hour?"
User: "Show me all my active automations"
User: "Debug workflow auto_123456789"
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────┐
│  AUTOMATION CANVAS CHEAT SHEET              │
├─────────────────────────────────────────────┤
│                                             │
│  🔷 Hexagon   = TRIGGER (when to start)    │
│  🟦 Rectangle = ACTION (what to do)        │
│  🔸 Diamond   = DECISION (if/else)         │
│  ⭕ Circle    = END (completion)           │
│                                             │
│  Drag → Connect → Save → Execute           │
│                                             │
│  Ask AI: "Create automation for..."        │
│                                             │
│  Schedule: Cron expressions                │
│    0 9 * * *     = Daily 9am               │
│    0 8 * * 1-5   = Weekdays 8am            │
│    */15 * * * *  = Every 15 min            │
│                                             │
│  Tools: 741 available                       │
│    - Gmail, Outlook, Slack                 │
│    - Google Workspace, Microsoft 365       │
│    - Xero, Stripe, Shopify                 │
│    - AI, PDF, Data Analysis                │
│                                             │
└─────────────────────────────────────────────┘
```

---

**Status**: PRODUCTION READY  
**Last Updated**: November 16, 2025  
**Version**: 2.0.0
