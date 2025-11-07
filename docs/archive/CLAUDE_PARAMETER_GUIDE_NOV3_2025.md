# HOW TO USE MICROSOFT 365 TOOLS - PARAMETER GUIDE FOR CLAUDE
## November 3, 2025

## THE ANSWER TO "DOES IT NEED TO KNOW IT NEEDS TWO PARAMETERS??"

**YES!** But it's more nuanced:

### Anthropic WILL enforce required parameters

When you send Claude tools with this schema:
```json
{
  "name": "word_create_document",
  "input_schema": {
    "type": "object",
    "properties": {
      "name": {"type": "string", "description": "..."},
      "content": {"type": "string", "description": "..."}
    },
    "required": ["name"]
  }
}
```

Anthropic's API will:
1. ✅ Show Claude that `name` is REQUIRED
2. ✅ Reject tool calls that don't include `name`
3. ✅ Force Claude to provide a value for `name`

### BUT THERE'S A CATCH

Claude will provide **A** value, but it might be generic:
- Instead of: `name='Q4 Business Report'`
- Claude might use: `name='document'` or `name='Document 1'`

### THE REAL PROBLEM

When you ask:
```
"Create a Word document"
```

Claude interprets this as permission to call the tool, but since YOU didn't specify what name/content to use, Claude just picks something generic.

### THE SOLUTION - TWO APPROACHES

#### Approach 1: Tell Claude EXACTLY what to do
```
"Create a Word document:
- Name: 'Q4 Financial Report'
- Content: 'Revenue: $100k, Expenses: $60k, Profit: $40k'"
```

Result: Claude calls `word_create_document(name='Q4 Financial Report', content='Revenue: $100k...')`

#### Approach 2: Let Claude Ask
Add system instruction:
```
"If you need to create a document but don't know what to name it or what content to put in it, 
ASK THE USER FIRST before calling the tool. Example: 
'I can create a Word document, but I need to know:
- What should the document be named?
- What content should it contain?'"
```

Result: Claude asks you for the details first

---

## SPECIFIC PARAMETER REQUIREMENTS

### word_create_document
```
REQUIRED:
  - name (str): "Q4 Report", "Sales Summary", "Project Plan", etc.

OPTIONAL:
  - content (str): The text to include in the document
  - folder_id (str): OneDrive folder ID
```

**Example Call:**
```python
word_create_document(
    name="Quarterly Business Report 2025",
    content="This is our quarterly business report\n\nQ1: $50,000\nQ2: $60,000\nQ3: $75,000"
)
```

### outlook_send_email
```
REQUIRED:
  - to (list): ["email1@example.com", "email2@example.com"]
  - subject (str): "Report Ready", "Documents Shared", etc.
  - body (str): The email message

OPTIONAL:
  - body_type (str): "html" (default) or "text"
  - cc (list): CC recipients
  - bcc (list): BCC recipients
  - importance (str): "normal", "high", "low"
```

**Example Call:**
```python
outlook_send_email(
    to=["inhouse@vetsuccessacademy.com", "gerardo@vetsuccessacademy.com"],
    subject="Q4 Reports Ready",
    body="<p>Please review the attached Q4 business report.</p><p>All data has been compiled and verified.</p>"
)
```

### excel_create_workbook
```
REQUIRED:
  - name (str): "Q4 Data", "Financial Summary", "Sales Tracking", etc.

OPTIONAL:
  - None currently documented, but can add data after creation
```

**Example Call:**
```python
excel_create_workbook(
    name="Q4 Financial Summary"
)
```

---

## WHAT THE SCHEMAS CURRENTLY LOOK LIKE

### For word_create_document
```json
{
  "name": "word_create_document",
  "description": "Create a new Word document in OneDrive",
  "input_schema": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "Document name (will add .docx if not present)"
      },
      "content": {
        "type": "string", 
        "description": "Initial text content (plain text)"
      },
      "folder_id": {
        "type": "string",
        "description": "OneDrive folder ID (default: root)"
      }
    },
    "required": ["name"]  ← ANTHROPIC ENFORCES THIS
  }
}
```

### For outlook_send_email
```json
{
  "name": "outlook_send_email",
  "description": "Send an email via Microsoft 365 Outlook",
  "input_schema": {
    "type": "object",
    "properties": {
      "to": {
        "type": "array",
        "items": {"type": "string"},
        "description": "List of recipient email addresses"
      },
      "subject": {
        "type": "string",
        "description": "Email subject line"
      },
      "body": {
        "type": "string",
        "description": "Email body text"
      },
      "body_type": {
        "type": "string",
        "enum": ["html", "text"],
        "description": "Email body format"
      },
      "cc": {
        "type": "array",
        "items": {"type": "string"},
        "description": "CC recipients (optional)"
      }
    },
    "required": ["to", "subject", "body"]  ← ANTHROPIC ENFORCES THIS
  }
}
```

**What this means:**
- If Claude tries to call it without `to`, `subject`, or `body` → Anthropic rejects it
- Claude MUST include all three
- But Claude still needs to know WHAT values to use

---

## HOW TO PROMPT CLAUDE EFFECTIVELY

### ❌ VAGUE INSTRUCTIONS (Won't work well)
```
"Send an email with document links"
```
Result: Claude might use generic subject/body

### ✅ SPECIFIC INSTRUCTIONS (Works great)
```
"Send an email to inhouse@vetsuccessacademy.com and gerardo@vetsuccessacademy.com
Subject: 'Q4 Documents Ready for Review'
Body: 'Hi team,

The following documents have been created:
- Word Report: Q4 Business Report (created at 2025-11-03)
- Excel Workbook: Q4 Financial Data (created at 2025-11-03)

Please review and provide feedback by end of week.

Thanks,
Admin'"
```
Result: Claude uses EXACT values you specified

### ✅ BETTER - LET CLAUDE DECIDE
```
"Create:
1. A Word document named 'Q4 Report' containing:
   - Title: 'Q4 Business Report'
   - Q1 Revenue: $50,000
   - Q2 Revenue: $60,000  
   - Q3 Revenue: $75,000
   - Total: $185,000

2. An Excel workbook named 'Q4 Financial Data'

3. Send an email to inhouse@vetsuccessacademy.com and gerardo@vetsuccessacademy.com
   explaining that both documents are ready and providing links to them"
```
Result: Claude creates all three with sensible defaults

---

## CURRENT STATUS

### What's Fixed ✅
- `required` arrays properly set in schemas
- Anthropic API will enforce required parameters
- Framework properly routes parameters to tools
- Credentials injected for authorized users

### What Needs Improvement 🟡
- Better system prompt telling Claude HOW to use these tools
- Clearer descriptions of what each parameter should contain
- Examples in the schema showing typical usage

### What You Can Do NOW
1. Give Claude SPECIFIC values for all required parameters
2. Ask Claude to create documents with specific names and content
3. Ask Claude to send emails with specific subject/body text
4. Use 20 conversation turns if Claude needs clarification

---

## EXAMPLE COMPLETE WORKFLOW

### User Request:
```
"I need you to create a Word document about Q4 sales,
create an Excel workbook with the sales data,
and send both to inhouse@vetsuccessacademy.com and gerardo@vetsuccessacademy.com"
```

### Claude's Internal Process:
1. Sees `word_create_document` requires `name` → checks user message for name hint
   - Finds: "Q4 sales" → uses `name='Q4 Sales Report'`
2. Sees it can include optional `content` → creates descriptive content
   - Includes: Q1/Q2/Q3 sales figures
3. Sees `excel_create_workbook` requires `name` → uses `name='Q4 Sales Data'`
4. Sees `outlook_send_email` requires `to`, `subject`, `body`
   - `to`: `['inhouse@vetsuccessacademy.com', 'gerardo@vetsuccessacademy.com']`
   - `subject`: Generates something like "Q4 Sales Reports"
   - `body`: Generates message explaining the documents

### Result: ✅ All three tools called with appropriate values

---

## FINAL ANSWER

**Q: Does it need to know it needs TWO parameters??**

**A:** Anthropic's schema validation will FORCE required parameters to be included. But:

1. **Schema shows requirements** ✅
   - `required: ["name"]` for word_create_document
   - `required: ["to", "subject", "body"]` for outlook_send_email

2. **Anthropic enforces them** ✅
   - Rejects calls missing required parameters
   - Requires Claude to include them

3. **You guide the values** 🟡
   - Tell Claude specifically what to use
   - Or ask Claude to ask you for clarification
   - Or trust Claude to pick sensible defaults

The framework is set up correctly. Just make sure your prompts to Claude include specific values for required parameters!
