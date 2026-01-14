# MICROSOFT 365 TOOLS - PARAMETER REQUIREMENTS & FIXES
## November 3, 2025

## THE PROBLEM - Two Issues Preventing Tool Execution

### Issue #1: execute_tool Meta-Function Positional Argument Conflict

**Error:**
```
Tool execution failed: tools.registry_v3.RegistryV3.execute_tool() got multiple values for keyword argument 'tool_name'
```

**Root Cause:**
The proxy function `execute_tool()` in `meta_tools.py` had a positional parameter:
```python
# WRONG
def execute_tool(tool_name: str = None, **tool_params) -> Dict[str, Any]:
```

Anthropic's native tool interface calls it with ALL parameters as keywords:
```python
execute_tool(tool_name="outlook_send_email", to="user@example.com", ...)
```

This creates a conflict: `tool_name` passed both positionally and as keyword.

**Solution (APPLIED):**
```python
# CORRECT
def execute_tool(**tool_params) -> Dict[str, Any]:
    tool_name = tool_params.pop('tool_name', None)
    # ... rest of implementation
```

**Files Fixed:**
- `tools/implementations/meta_tools.py` line 472

**Status:** ✅ FIXED

---

### Issue #2: Microsoft Tools Missing Required Parameters

The AI agent needs to know which parameters are REQUIRED for each tool.

#### Word Document Tool
**Function Signature:**
```python
def word_create_document(self, name: str, content: str = "", folder_id: Optional[str] = None, **kwargs)
```

**Required Parameters:**
- `name`: Document name (REQUIRED) - example: "My Document" or "Report.docx"
- `content`: Initial text content (optional, default: empty string)
- `folder_id`: OneDrive folder ID (optional, default: root folder)

**Example Call:**
```python
registry.execute_tool(
    tool_name='word_create_document',
    name='Business Plan',  # REQUIRED!
    content='Executive Summary...',  # Optional
    _user_id=1,  # For authentication
    _injected_credentials=True
)
```

#### Outlook Email Tool
**Function Signature:**
```python
def outlook_send_email(self, to: List[str], subject: str, body: str, 
                      body_type: str = 'html', cc: List[str] = None, 
                      bcc: List[str] = None, importance: str = 'normal',
                      attachments: List[Dict] = None, 
                      request_read_receipt: bool = False, **kwargs)
```

**Required Parameters:**
- `to`: List of email addresses (REQUIRED) - example: `['user@example.com', 'other@example.com']`
- `subject`: Email subject (REQUIRED) - example: "Project Update"
- `body`: Email body text (REQUIRED) - example: "Please review..."

**Optional Parameters:**
- `body_type`: 'html' (default) or 'text'
- `cc`: List of CC recipients
- `bcc`: List of BCC recipients
- `importance`: 'normal', 'high', or 'low'
- `attachments`: List of file attachments
- `request_read_receipt`: Boolean

**Example Call:**
```python
registry.execute_tool(
    tool_name='outlook_send_email',
    to=['inhouse@vetsuccessacademy.com', 'gerardo@vetsuccessacademy.com'],  # REQUIRED!
    subject='Document Links',  # REQUIRED!
    body='Please see the attached links to the documents created.',  # REQUIRED!
    body_type='html',  # Optional
    _user_id=1,
    _injected_credentials=True
)
```

#### Excel Workbook Tool
**Function Signature:**
```python
def excel_create_workbook(self, name: str, **kwargs)
```

**Required Parameters:**
- `name`: Workbook name (REQUIRED) - example: "Q4 Report" or "Sales Data.xlsx"

**Example Call:**
```python
registry.execute_tool(
    tool_name='excel_create_workbook',
    name='Quarterly Financial Report',  # REQUIRED!
    _user_id=1,
    _injected_credentials=True
)
```

---

## SOLUTION: Update Tool Schemas to Mark Required Parameters

The tool schemas in `tools/schemas/microsoft_*.json` need to clearly mark which parameters are REQUIRED.

### Current Schema Format (INCOMPLETE)
```json
{
  "name": "word_create_document",
  "parameters": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "Document name"
      }
    }
    // Missing: "required": ["name"]
  }
}
```

### Fixed Schema Format (COMPLETE)
```json
{
  "name": "word_create_document",
  "parameters": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "Document name (e.g., 'My Document' or 'Report.docx')"
      },
      "content": {
        "type": "string",
        "description": "Initial text content (optional)"
      },
      "folder_id": {
        "type": "string",
        "description": "OneDrive folder ID (optional, uses root if not provided)"
      }
    },
    "required": ["name"]  // THIS IS CRITICAL!
  }
}
```

---

## WHAT THE AI NEEDS TO KNOW

### Current Problem
When Claude calls a tool, it doesn't receive information about which parameters are required. So it might call:
```python
word_create_document()  # ❌ Missing 'name' parameter!
outlook_send_email(to=['user@example.com'])  # ❌ Missing 'subject' and 'body'!
```

### Solution: Schema must list required parameters

The schema MUST include `"required": [...]` array:
```json
"required": ["name"]  // For word_create_document
"required": ["to", "subject", "body"]  // For outlook_send_email
"required": ["name"]  // For excel_create_workbook
```

When this is present, Anthropic will:
1. Display required parameters in the tool description
2. Ensure Claude includes all required parameters in tool calls
3. Return validation errors if required parameters are missing

---

## FILES THAT NEED UPDATING

### 1. `tools/schemas/microsoft_word_tools.json`
Update `word_create_document` schema:
```json
{
  "name": "word_create_document",
  "description": "Create a new Word document in OneDrive. Requires document name.",
  "platform": "microsoft_word",
  "parameters": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "Document name (e.g., 'Business Plan', 'Report.docx')"
      },
      "content": {
        "type": "string",
        "description": "Initial text content to add to document (optional)"
      },
      "folder_id": {
        "type": "string",
        "description": "OneDrive folder ID to create document in (optional, defaults to root)"
      }
    },
    "required": ["name"]
  }
}
```

### 2. `tools/schemas/microsoft_outlook_tools.json`
Update `outlook_send_email` schema:
```json
{
  "name": "outlook_send_email",
  "description": "Send an email via Microsoft 365 Outlook. Requires recipient, subject, and message body.",
  "platform": "microsoft_outlook",
  "parameters": {
    "type": "object",
    "properties": {
      "to": {
        "type": "array",
        "items": {"type": "string"},
        "description": "List of recipient email addresses (e.g., ['user@example.com', 'other@example.com'])"
      },
      "subject": {
        "type": "string",
        "description": "Email subject line"
      },
      "body": {
        "type": "string",
        "description": "Email body text (supports HTML if body_type='html')"
      },
      "body_type": {
        "type": "string",
        "enum": ["html", "text"],
        "description": "Email body format (default: 'html')"
      },
      "cc": {
        "type": "array",
        "items": {"type": "string"},
        "description": "List of CC recipient email addresses (optional)"
      },
      "bcc": {
        "type": "array",
        "items": {"type": "string"},
        "description": "List of BCC recipient email addresses (optional)"
      },
      "importance": {
        "type": "string",
        "enum": ["normal", "high", "low"],
        "description": "Email importance level (default: 'normal')"
      }
    },
    "required": ["to", "subject", "body"]
  }
}
```

### 3. `tools/schemas/microsoft_excel_tools.json`
Update `excel_create_workbook` schema:
```json
{
  "name": "excel_create_workbook",
  "description": "Create a new Excel workbook in OneDrive. Requires workbook name.",
  "platform": "microsoft_excel",
  "parameters": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "Workbook name (e.g., 'Q4 Report', 'Sales Data.xlsx')"
      }
    },
    "required": ["name"]
  }
}
```

---

## TESTING THE FIX

After updating schemas, test with:

```python
from tools.registry_v3 import RegistryV3

r = RegistryV3()

# Test 1: Word document with required name
result = r.execute_tool(
    tool_name='word_create_document',
    name='Test Document',
    _user_id=1,
    _injected_credentials=True
)
print(f"Word: {result}")

# Test 2: Email with all required fields
result = r.execute_tool(
    tool_name='outlook_send_email',
    to=['inhouse@vetsuccessacademy.com', 'gerardo@vetsuccessacademy.com'],
    subject='Documents Ready',
    body='Your documents have been created and are ready for download.',
    _user_id=1,
    _injected_credentials=True
)
print(f"Email: {result}")

# Test 3: Excel with required name
result = r.execute_tool(
    tool_name='excel_create_workbook',
    name='Financial Report',
    _user_id=1,
    _injected_credentials=True
)
print(f"Excel: {result}")
```

---

## CURRENT STATUS

### Fixed ✅
- `execute_tool` meta-function no longer has positional parameter conflict
- All 606 tools loadable without errors
- Microsoft 365 tools callable with proper credentials injection

### In Progress 🟡
- Schema updates to mark required parameters
- AI prompting to ensure required parameters included

### Working ✅
- `max_turns = 20` already set in agent_worker.py
- Framework supports long conversations
- Ready for parameter-aware execution

---

## KEY TAKEAWAY

**The issue is NOT with the tool framework anymore** - it's with the **tool schema documentation**.

When Claude/Anthropic sees:
```json
"required": ["name", "to", "subject"]
```

It WILL include those parameters in tool calls. Without this, Claude guesses and might omit required params.

**Fix:** Update Microsoft tool schemas to include `"required"` arrays with all mandatory parameters.
