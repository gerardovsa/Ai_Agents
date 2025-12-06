# Progressive Tool Discovery Architecture - Complete Explanation

**Created**: December 5, 2025  
**Purpose**: Explain how AI agents discover and learn about 594+ tools dynamically through Just-In-Time (JIT) instruction loading

---

## 📋 Table of Contents

1. [The Problem: Token Overload](#the-problem-token-overload)
2. [The Solution: Progressive Discovery](#the-solution-progressive-discovery)
3. [Architecture Overview](#architecture-overview)
4. [The 4-Tier System](#the-4-tier-system)
5. [How AI Uses It (Step-by-Step)](#how-ai-uses-it-step-by-step)
6. [Schema Structure](#schema-structure)
7. [Real-World Example](#real-world-example)
8. [Benefits & Trade-offs](#benefits--trade-offs)

---

## The Problem: Token Overload

### What Happens Without Progressive Discovery?

**Scenario**: You have 594 tools across 20+ platforms (Google, Microsoft, Slack, Stripe, Xero, etc.)

**Naive Approach**: Send ALL tool schemas to Claude on EVERY request

```json
{
  "tools": [
    {"name": "gmail_send_email", "description": "...", "parameters": {...}},
    {"name": "gmail_get_message", "description": "...", "parameters": {...}},
    {"name": "google_sheets_create_spreadsheet", "description": "...", "parameters": {...}},
    // ... 591 more tools ...
  ]
}
```

**Result**: 🔥 **DISASTER**

- **Token Explosion**: 594 tools × ~500 tokens each = **297,000 tokens**
- **Context Limit**: Claude 200K limit exceeded before user even speaks!
- **Cost**: Massive API costs (tokens charged on EVERY request)
- **Performance**: Slow response times from parsing huge tool catalog
- **Confusion**: AI overwhelmed with irrelevant tools

**Example Problem**:
```
User: "Send an email to john@example.com"

AI receives:
- Gmail tools (relevant ✅)
- Stripe payment tools (irrelevant ❌)
- Xero accounting tools (irrelevant ❌)
- Slack messaging tools (irrelevant ❌)
- 590 other tools (irrelevant ❌)

Result: AI confused, picks wrong tool, or timeout
```

---

## The Solution: Progressive Discovery

### The Core Concept: Just-In-Time (JIT) Tool Loading

**Philosophy**: AI should only learn about tools **when it needs them**, not all at once.

**How It Works**:
```
Round 1: AI gets 5 meta-tools (discovery tools)
Round 2: AI uses meta-tools to discover relevant platform tools
Round 3: AI uses tools to complete user's task
```

**Key Insight**: Meta-tools ARE the instruction manual. AI learns by using tools, not by reading upfront.

---

## Architecture Overview

### Three Core Components

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  1. REGISTRY (tools/registry_v3.py)                     │
│     - Auto-loads 594 tools from schemas/ and            │
│       implementations/                                   │
│     - Converts to Anthropic format                      │
│     - Provides meta-tools for discovery                 │
│                                                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  2. META-TOOLS (tools/implementations/meta_tools.py)    │
│     - list_available_platforms()                        │
│     - list_platform_tools(platform)                     │
│     - get_tool_schema(tool_name)                        │
│     - execute_tool(tool_name, **params)                 │
│     - search_tools(query)                               │
│     - recommend_tools_for_task(task)                    │
│                                                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  3. TOOL SCHEMAS (tools/schemas/*.json)                 │
│     - Platform-specific tool definitions                │
│     - EXTREMELY detailed descriptions (200+ words)      │
│     - Examples, usage guides, error handling            │
│     - Tool intelligence & memory context                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
User: "Send an email to john@example.com"
           │
           ▼
┌─────────────────────────────────────┐
│  AI Agent (Claude)                  │
│  Current Knowledge: 5 meta-tools    │
└──────────────┬──────────────────────┘
               │
               │ Step 1: Discovery
               ▼
┌─────────────────────────────────────┐
│  list_available_platforms()         │
│  → Returns: ["gmail", "google_     │
│     sheets", "microsoft_outlook"]   │
└──────────────┬──────────────────────┘
               │
               │ Step 2: Platform Selection
               ▼
┌─────────────────────────────────────┐
│  list_platform_tools("gmail")       │
│  → Returns: [                       │
│      "gmail_send_email",            │
│      "gmail_get_message",           │
│      "gmail_list_messages"          │
│    ]                                │
└──────────────┬──────────────────────┘
               │
               │ Step 3: Schema Learning
               ▼
┌─────────────────────────────────────┐
│  get_tool_schema("gmail_send_email")│
│  → Returns: Full parameter schema   │
│    with examples, usage guide       │
└──────────────┬──────────────────────┘
               │
               │ Step 4: Execution
               ▼
┌─────────────────────────────────────┐
│  gmail_send_email(                  │
│    to="john@example.com",           │
│    subject="Hi John",               │
│    body="..."                       │
│  )                                  │
└─────────────────────────────────────┘
```

---

## The 4-Tier System

### Tier 1: Initial State (5 Meta-Tools)

**What AI Receives on FIRST Request**:

```python
tools = [
    {
        "name": "list_available_platforms",
        "description": "List all platforms that have tools available...",
        "parameters": {...}
    },
    {
        "name": "list_platform_tools",
        "description": "List all tools for a platform...",
        "parameters": {"platform": {"type": "string"}}
    },
    {
        "name": "get_tool_schema",
        "description": "Get FULL parameter schema for ONE specific tool...",
        "parameters": {"tool_name": {"type": "string"}}
    },
    {
        "name": "execute_tool",
        "description": "Execute a tool with parameters...",
        "parameters": {"tool_name": {"type": "string"}, ...}
    },
    {
        "name": "search_tools",
        "description": "Semantic search across all tool descriptions...",
        "parameters": {"query": {"type": "string"}}
    }
]
```

**Token Cost**: ~2,500 tokens (0.125% of 200K limit)

**What AI Knows**: Nothing about Gmail, Google Sheets, or any platform tools. Only knows HOW to discover them.

---

### Tier 2: Platform Discovery

**AI Action**: `list_available_platforms()`

**Response**:
```json
{
  "success": true,
  "platforms": [
    "gmail",
    "google_sheets",
    "google_docs",
    "microsoft_outlook",
    "microsoft_excel",
    "slack",
    "stripe",
    "xero",
    "shopify",
    "synergy"
  ],
  "platform_count": 10,
  "tool_counts": {
    "gmail": 15,
    "google_sheets": 12,
    "slack": 8
  },
  "total_tools": 594
}
```

**Token Cost**: ~500 tokens

**What AI Learned**: 
- 10 platforms available
- Gmail has 15 tools
- Google Sheets has 12 tools
- Can narrow down to relevant platform

**AI's Internal Reasoning**:
```
User wants email → Gmail platform (15 tools)
User wants spreadsheet → Google Sheets platform (12 tools)
User wants payment → Stripe platform
```

---

### Tier 3: Tool Catalog (Lightweight)

**AI Action**: `list_platform_tools(platform="gmail")`

**Response**:
```json
{
  "success": true,
  "platform": "gmail",
  "tool_count": 15,
  "tools": [
    {
      "name": "gmail_send_email",
      "description": "Send an email via Gmail (OAuth2 authenticated). Use this when user wants to send emails. Supports attachments, CC, BCC."
    },
    {
      "name": "gmail_get_message",
      "description": "Get a single email message by ID. Returns full email content, headers, attachments."
    },
    {
      "name": "gmail_list_messages",
      "description": "List messages with optional filters (from, to, subject, date range). Returns message IDs and metadata."
    },
    {
      "name": "gmail_search_messages",
      "description": "Search emails using Gmail query syntax (same as search bar). Returns matching message IDs."
    },
    {
      "name": "gmail_create_draft",
      "description": "Create a draft email without sending. User can review/edit in Gmail UI before sending."
    }
    // ... 10 more tools ...
  ],
  "next_steps": "To use a tool: Call get_tool_schema(tool_name) to see parameters"
}
```

**Token Cost**: ~1,500 tokens (15 tools × ~100 tokens each)

**What AI Learned**:
- Gmail has 5 main tools for sending, getting, listing, searching, drafting
- Each tool has a SHORT description (what it does, when to use)
- NO parameter details yet (that comes in Tier 4)

**AI's Selection Logic**:
```
User: "Send email to john@example.com"
→ Relevant: gmail_send_email ✅
→ NOT relevant: gmail_list_messages ❌
→ NOT relevant: gmail_search_messages ❌

Decision: Call get_tool_schema("gmail_send_email")
```

---

### Tier 4: Full Schema (On-Demand)

**AI Action**: `get_tool_schema(tool_name="gmail_send_email")`

**Response** (EXTREMELY DETAILED):
```json
{
  "name": "gmail_send_email",
  "description": "Send an email via Gmail with OAuth2 authentication.\n\nThis tool sends emails on behalf of the authenticated user. It supports rich HTML content, attachments, CC/BCC recipients, and custom headers. The email is sent immediately upon execution.\n\nUse this tool when:\n- User explicitly asks to 'send email'\n- User provides recipient email address\n- User provides subject and message content\n- User wants to email a file/document\n\nDO NOT use this tool when:\n- User wants to CREATE A DRAFT (use gmail_create_draft instead)\n- User wants to REPLY to existing email (use gmail_reply_to_message)\n- User hasn't confirmed recipient address (ask first)\n\nCommon scenarios:\n1. 'Send email to john@example.com with subject...' → Use this tool\n2. 'Draft an email to...' → Use gmail_create_draft instead\n3. 'Reply to the last email' → Use gmail_reply_to_message\n\nImportant notes:\n- Requires 'gmail.send' OAuth scope\n- Maximum attachment size: 25MB\n- Rate limit: 500 emails per day\n- HTML and plain text supported\n- Can send to multiple recipients (to, cc, bcc)\n\nConstraints:\n- Recipient email must be valid format\n- Subject line maximum 998 characters\n- Body can be HTML or plain text\n- Attachments must be base64 encoded",
  
  "parameters": {
    "type": "object",
    "properties": {
      "to": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Recipient email addresses (required). Each must be valid email format.\n\nExamples:\n- ['john@example.com']\n- ['alice@company.com', 'bob@company.com']\n\nNote: Multiple recipients will ALL receive the same email."
      },
      "subject": {
        "type": "string",
        "description": "Email subject line (required). Maximum 998 characters.\n\nExamples:\n- 'Meeting Notes - Q4 Planning'\n- 'Invoice #12345 for October'\n- 'RE: Your question about...'",
        "maxLength": 998
      },
      "body": {
        "type": "string",
        "description": "Email body content (required). Can be plain text or HTML.\n\nPlain text example:\n'Hi John,\\n\\nThanks for meeting yesterday...'\n\nHTML example:\n'<p>Hi John,</p><p>Thanks for meeting...</p>'\n\nNote: HTML is automatically detected by content."
      },
      "cc": {
        "type": "array",
        "items": {"type": "string"},
        "description": "CC (Carbon Copy) recipients (optional). These recipients will see each other's addresses.\n\nExample: ['manager@company.com', 'team@company.com']",
        "default": []
      },
      "bcc": {
        "type": "array",
        "items": {"type": "string"},
        "description": "BCC (Blind Carbon Copy) recipients (optional). These recipients are HIDDEN from other recipients.\n\nExample: ['archive@company.com']\n\nUse case: Send to multiple people without revealing their emails to each other.",
        "default": []
      },
      "attachments": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "filename": {"type": "string"},
            "data": {"type": "string", "description": "Base64 encoded file content"},
            "mime_type": {"type": "string"}
          }
        },
        "description": "File attachments (optional). Each attachment must include filename, base64 data, and MIME type.\n\nExample:\n[{\n  'filename': 'report.pdf',\n  'data': 'JVBERi0xLjQK...',\n  'mime_type': 'application/pdf'\n}]\n\nSupported formats: PDF, DOCX, XLSX, JPG, PNG, etc.\nMaximum size: 25MB per attachment",
        "default": []
      }
    },
    "required": ["to", "subject", "body"]
  },
  
  "examples": [
    {
      "description": "Simple email - Basic usage with required params only",
      "parameters": {
        "to": ["john@example.com"],
        "subject": "Meeting Follow-up",
        "body": "Hi John,\n\nThanks for the meeting today. Looking forward to working together!\n\nBest,\nAI Assistant"
      },
      "expected_result": {
        "success": true,
        "message_id": "18f2a3b4c5d6e7f8",
        "thread_id": "18f2a3b4c5d6e7f8"
      }
    },
    {
      "description": "Email with CC/BCC and HTML - Complex example",
      "parameters": {
        "to": ["client@example.com"],
        "cc": ["manager@mycompany.com"],
        "bcc": ["archive@mycompany.com"],
        "subject": "Project Proposal - Q1 2025",
        "body": "<h1>Project Proposal</h1><p>Please review the attached proposal...</p>"
      },
      "expected_result": {
        "success": true,
        "message_id": "19g3b4c5d6e7f8g9"
      }
    },
    {
      "description": "Error case - Invalid email format",
      "parameters": {
        "to": ["invalid-email"],
        "subject": "Test",
        "body": "Test message"
      },
      "expected_result": {
        "success": false,
        "error": "Invalid email format: 'invalid-email'. Must be valid email address (e.g., user@domain.com)"
      }
    }
  ],
  
  "usage_guide": {
    "when_to_use": [
      "User explicitly says 'send email' or 'email to...'",
      "User provides recipient email address",
      "User has confirmed the email should be sent NOW (not drafted)",
      "User wants to send a file/document via email",
      "User wants to notify someone via email"
    ],
    "when_not_to_use": [
      "User wants to CREATE A DRAFT → Use gmail_create_draft instead",
      "User wants to REPLY to existing email → Use gmail_reply_to_message",
      "User wants to FORWARD email → Use gmail_forward_message",
      "User hasn't confirmed recipient → Ask user first",
      "User wants to VIEW emails → Use gmail_list_messages or gmail_get_message"
    ],
    "workflow": [
      "Step 1: Confirm user wants to SEND (not draft) the email",
      "Step 2: Verify you have recipient email address (ask if not provided)",
      "Step 3: Verify you have subject and body content",
      "Step 4: Call gmail_send_email() with parameters",
      "Step 5: Confirm success to user with message ID",
      "Step 6: Provide Gmail link: https://mail.google.com/mail/u/0/#sent/{message_id}"
    ],
    "best_practices": [
      "ALWAYS confirm recipient address before sending (prevent accidental sends)",
      "Use descriptive subject lines (users appreciate context)",
      "For HTML emails, ensure proper formatting with <p> tags",
      "When attaching files, check file size < 25MB",
      "Use BCC when sending to multiple recipients who shouldn't see each other",
      "Store returned message_id for tracking/reference",
      "Provide Gmail link to user so they can verify send"
    ],
    "error_handling": [
      "Error 401: 'Unauthorized' → User needs to re-authenticate with Gmail OAuth (call gmail_authenticate)",
      "Error 403: 'Insufficient Permission' → User needs 'gmail.send' scope (have them re-authenticate)",
      "Error 400: 'Invalid email format' → Check recipient addresses are valid (user@domain.com format)",
      "Error 400: 'Attachment too large' → Attachments exceed 25MB limit (ask user to use Drive instead)",
      "Error 429: 'Rate limited' → User sent 500+ emails today (daily limit reached, wait until tomorrow)",
      "Error 'Invalid attachment' → Base64 encoding failed (check file encoding)",
      "Error 'Recipient not found' → Email address doesn't exist (verify with user)"
    ],
    "related_tools": [
      "gmail_create_draft - Use if user wants to REVIEW before sending",
      "gmail_list_messages - Call BEFORE to find message ID for replies",
      "gmail_get_message - Call to retrieve original message for context",
      "gmail_reply_to_message - Use if replying to existing email (preserves thread)",
      "gmail_forward_message - Use if forwarding existing email",
      "google_drive_share_file - Use if file too large for attachment (25MB limit)"
    ]
  },
  
  "tool_intelligence": {
    "category": "communication",
    "typical_workflow_patterns": [
      "gmail_list_messages → gmail_send_email",
      "gmail_get_message → gmail_reply_to_message",
      "google_drive_upload_file → gmail_send_email (with Drive link)"
    ],
    "success_indicators": {
      "keywords": ["sent successfully", "message sent", "email delivered"],
      "behavioral": ["User thanks AI", "User asks to send another", "User continues conversation"]
    },
    "failure_indicators": {
      "keywords": ["failed", "error", "couldn't send", "unauthorized"],
      "behavioral": ["User asks to retry", "User re-authenticates", "User provides different email"]
    }
  },
  
  "memory_context": {
    "vectorization_fields": ["subject", "body", "to"],
    "search_keywords": ["email", "gmail", "send", "message"],
    "related_synergy_platforms": ["gmail"],
    "typical_use_cases": [
      "Send meeting notes to team members",
      "Send invoice to client",
      "Send project update to stakeholders",
      "Send password reset link to user",
      "Send weekly report to manager"
    ]
  }
}
```

**Token Cost**: ~2,000 tokens (ONE tool's full schema)

**What AI Learned**:
- **Exact parameters**: `to`, `subject`, `body`, `cc`, `bcc`, `attachments`
- **Parameter types**: `to` is array of strings, `subject` is string
- **Required vs optional**: `to`, `subject`, `body` are required
- **Validation rules**: Subject max 998 chars, attachments max 25MB
- **3 complete examples**: Simple, complex, error case
- **When to use**: Explicit "send email" request
- **When NOT to use**: Draft, reply, forward (use different tools)
- **Workflow steps**: 6-step process from confirmation to success
- **Error handling**: 7 common errors with solutions
- **Related tools**: 6 alternative tools for similar tasks

**AI Can Now Execute**:
```python
gmail_send_email(
    to=["john@example.com"],
    subject="Meeting Follow-up",
    body="Hi John,\n\nThanks for the meeting today..."
)
```

---

## How AI Uses It (Step-by-Step)

### Real Conversation Flow

**User Request**:
```
"Send an email to john@example.com with subject 'Q4 Planning' 
and tell him the meeting is at 2pm tomorrow"
```

### Round 1: Discovery

**AI's Thinking**:
```
I need to send an email. Let me find email tools.
Step 1: What platforms are available?
```

**AI Action**:
```json
{
  "tool_use": {
    "name": "list_available_platforms",
    "input": {}
  }
}
```

**Tool Result**:
```json
{
  "platforms": ["gmail", "microsoft_outlook", "slack", ...],
  "tool_counts": {"gmail": 15, "microsoft_outlook": 12}
}
```

**AI's Thinking**:
```
Great! Gmail and Microsoft Outlook both have email tools.
User didn't specify, so I'll check Gmail first (most common).
Step 2: What tools does Gmail have?
```

### Round 2: Platform Exploration

**AI Action**:
```json
{
  "tool_use": {
    "name": "list_platform_tools",
    "input": {"platform": "gmail"}
  }
}
```

**Tool Result**:
```json
{
  "tools": [
    {"name": "gmail_send_email", "description": "Send an email via Gmail..."},
    {"name": "gmail_create_draft", "description": "Create a draft email..."},
    {"name": "gmail_list_messages", "description": "List messages..."}
  ]
}
```

**AI's Thinking**:
```
Perfect! gmail_send_email is what I need.
But I don't know the parameters yet.
Step 3: What parameters does gmail_send_email need?
```

### Round 3: Schema Learning

**AI Action**:
```json
{
  "tool_use": {
    "name": "get_tool_schema",
    "input": {"tool_name": "gmail_send_email"}
  }
}
```

**Tool Result**: (Full schema from Tier 4 above)

**AI's Thinking**:
```
Now I know everything!
Required: to, subject, body
Optional: cc, bcc, attachments

User provided:
- to: john@example.com ✅
- subject: Q4 Planning ✅
- body: Need to compose from "meeting is at 2pm tomorrow" ✅

Step 4: Execute the tool!
```

### Round 4: Execution

**AI Action**:
```json
{
  "tool_use": {
    "name": "gmail_send_email",
    "input": {
      "to": ["john@example.com"],
      "subject": "Q4 Planning",
      "body": "Hi John,\n\nThis is a reminder that our Q4 planning meeting is scheduled for 2pm tomorrow.\n\nLooking forward to seeing you there!\n\nBest regards"
    }
  }
}
```

**Tool Result**:
```json
{
  "success": true,
  "message_id": "18f2a3b4c5d6e7f8",
  "thread_id": "18f2a3b4c5d6e7f8"
}
```

**AI Response to User**:
```
✅ Email sent successfully to john@example.com!

Subject: Q4 Planning
Message ID: 18f2a3b4c5d6e7f8

I've sent John a reminder about the Q4 planning meeting at 2pm tomorrow.

[View in Gmail](https://mail.google.com/mail/u/0/#sent/18f2a3b4c5d6e7f8)
```

---

## Schema Structure

### Complete Tool Schema Format

```json
{
  "platform": "gmail",
  "description": "Gmail integration - 15 tools for email management",
  "tools": [
    {
      // ═══════════════════════════════════════════════════════════
      // BASIC IDENTIFICATION
      // ═══════════════════════════════════════════════════════════
      "name": "gmail_send_email",
      "platform": "gmail",
      
      // ═══════════════════════════════════════════════════════════
      // EXTREMELY DETAILED DESCRIPTION (200-300 words)
      // ═══════════════════════════════════════════════════════════
      "description": "Send an email via Gmail...\n\n[200-300 words with:]
        - What the tool does
        - When to use it (4-5 scenarios)
        - When NOT to use it (alternatives)
        - Important constraints
        - Rate limits
        - OAuth scopes required",
      
      // ═══════════════════════════════════════════════════════════
      // ANTHROPIC-COMPATIBLE PARAMETERS
      // ═══════════════════════════════════════════════════════════
      "parameters": {
        "type": "object",
        "properties": {
          "to": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Recipient email addresses...\n\nExamples:\n- ['john@example.com']\n- ['alice@co.com', 'bob@co.com']"
          },
          "subject": {
            "type": "string",
            "description": "Email subject line...\n\nExamples:\n- 'Meeting Notes'\n- 'Invoice #12345'",
            "maxLength": 998
          }
        },
        "required": ["to", "subject", "body"]
      },
      
      // ═══════════════════════════════════════════════════════════
      // RETURN VALUE STRUCTURE
      // ═══════════════════════════════════════════════════════════
      "returns": {
        "type": "object",
        "properties": {
          "success": {"type": "boolean"},
          "message_id": {"type": "string"},
          "error": {"type": "string"}
        }
      },
      
      // ═══════════════════════════════════════════════════════════
      // 3 COMPREHENSIVE EXAMPLES
      // ═══════════════════════════════════════════════════════════
      "examples": [
        {
          "description": "Simple email - Basic usage",
          "parameters": {...},
          "expected_result": {...}
        },
        {
          "description": "Complex email - All parameters",
          "parameters": {...},
          "expected_result": {...}
        },
        {
          "description": "Error case - Invalid input",
          "parameters": {...},
          "expected_result": {"success": false, "error": "..."}
        }
      ],
      
      // ═══════════════════════════════════════════════════════════
      // USAGE GUIDE (5 SECTIONS - CRITICAL!)
      // ═══════════════════════════════════════════════════════════
      "usage_guide": {
        "when_to_use": [
          "Scenario 1: User explicitly asks to send email",
          "Scenario 2: User provides recipient address",
          "Scenario 3: ..."
        ],
        "when_not_to_use": [
          "Alternative 1: Use gmail_create_draft if drafting",
          "Alternative 2: Use gmail_reply_to_message if replying",
          "Alternative 3: ..."
        ],
        "workflow": [
          "Step 1: Confirm user wants to SEND (not draft)",
          "Step 2: Verify recipient address",
          "Step 3: Call tool with parameters",
          "Step 4: Confirm success to user",
          "Step 5: Provide Gmail link"
        ],
        "best_practices": [
          "Practice 1: Always confirm recipient before sending",
          "Practice 2: Use descriptive subject lines",
          "Practice 3: Store message_id for tracking"
        ],
        "error_handling": [
          "Error 401: User needs to re-authenticate → Call gmail_authenticate",
          "Error 403: Insufficient permissions → Re-authenticate with gmail.send scope",
          "Error 400: Invalid email format → Verify recipient format",
          "Error 429: Rate limited → Daily limit reached (500 emails)"
        ],
        "related_tools": [
          "gmail_create_draft - Use if user wants to review first",
          "gmail_reply_to_message - Use if replying to existing",
          "google_drive_share_file - Use if attachment too large"
        ]
      },
      
      // ═══════════════════════════════════════════════════════════
      // TOOL INTELLIGENCE (Silent Learning System)
      // ═══════════════════════════════════════════════════════════
      "tool_intelligence": {
        "category": "communication",
        "typical_workflow_patterns": [
          "gmail_list_messages → gmail_send_email",
          "gmail_get_message → gmail_reply_to_message"
        ],
        "success_indicators": {
          "keywords": ["sent successfully", "delivered"],
          "behavioral": ["User thanks AI", "User sends another"]
        },
        "failure_indicators": {
          "keywords": ["failed", "error", "unauthorized"],
          "behavioral": ["User asks to retry", "User re-authenticates"]
        }
      },
      
      // ═══════════════════════════════════════════════════════════
      // MEMORY CONTEXT (Semantic Search Integration)
      // ═══════════════════════════════════════════════════════════
      "memory_context": {
        "vectorization_fields": ["subject", "body", "to"],
        "search_keywords": ["email", "gmail", "send", "message"],
        "related_synergy_platforms": ["gmail"],
        "typical_use_cases": [
          "Send meeting notes to team",
          "Send invoice to client",
          "Send project update"
        ]
      }
    }
  ]
}
```

### Key Schema Features

**1. Anthropic-Compatible**:
- Uses exact format Claude expects
- `parameters.type = "object"`
- `properties` with nested descriptions
- `required` array for mandatory fields

**2. Self-Documenting**:
- AI doesn't need external docs
- Everything is in the schema
- Examples show exact usage patterns

**3. Intelligence Layers**:
- **Layer 1**: Tool execution (functional)
- **Layer 2**: Tool intelligence (analytics, learning)
- **Layer 3**: Memory context (semantic search)

**4. Progressive Detail**:
- Tier 3 shows SHORT description (100 words)
- Tier 4 shows FULL description (200-300 words)
- AI only loads what it needs

---

## Real-World Example

### Scenario: User Wants to Create Spreadsheet

```
User: "Create a spreadsheet with columns Name, Email, Phone 
       and add 3 sample rows of data"
```

### AI's Journey Through Discovery

**Round 1: Platform Discovery**

```python
AI → list_available_platforms()

Result:
{
  "platforms": ["gmail", "google_sheets", "google_docs", ...],
  "tool_counts": {"google_sheets": 12, "microsoft_excel": 10}
}

AI Thinking: "google_sheets has 12 tools. Let me check those."
```

**Round 2: Tool Discovery**

```python
AI → list_platform_tools(platform="google_sheets")

Result:
{
  "tools": [
    {"name": "google_sheets_create_spreadsheet", "description": "Create new spreadsheet..."},
    {"name": "google_sheets_add_rows", "description": "Add rows to existing sheet..."},
    {"name": "google_sheets_get_values", "description": "Read cell values..."}
  ]
}

AI Thinking: "google_sheets_create_spreadsheet is what I need. 
              Then google_sheets_add_rows for the data."
```

**Round 3: Schema Learning (First Tool)**

```python
AI → get_tool_schema(tool_name="google_sheets_create_spreadsheet")

Result: (Full 2000-token schema)
{
  "name": "google_sheets_create_spreadsheet",
  "parameters": {
    "properties": {
      "title": {"type": "string", "description": "Spreadsheet title..."},
      "sheet_names": {"type": "array", "description": "Sheet tab names..."}
    },
    "required": ["title"]
  },
  "examples": [...]
}

AI Thinking: "Required: title. Optional: sheet_names. Got it!"
```

**Round 4: First Execution**

```python
AI → google_sheets_create_spreadsheet(
  title="Contact List",
  sheet_names=["Contacts"]
)

Result:
{
  "success": true,
  "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUaCOmMEzv",
  "spreadsheet_url": "https://docs.google.com/spreadsheets/d/1BxiMVs..."
}

AI Thinking: "Spreadsheet created! Now I need to add the columns and data.
              Let me get the schema for google_sheets_add_rows."
```

**Round 5: Schema Learning (Second Tool)**

```python
AI → get_tool_schema(tool_name="google_sheets_add_rows")

Result: (Full schema)
{
  "parameters": {
    "properties": {
      "spreadsheet_id": {"type": "string"},
      "sheet_name": {"type": "string", "default": "Sheet1"},
      "values": {"type": "array", "description": "2D array of cell values..."}
    }
  },
  "examples": [
    {
      "parameters": {
        "values": [
          ["Name", "Email", "Phone"],
          ["John Doe", "john@example.com", "555-1234"]
        ]
      }
    }
  ]
}

AI Thinking: "Ah! values is a 2D array. First row is headers, 
              then data rows. Perfect!"
```

**Round 6: Second Execution**

```python
AI → google_sheets_add_rows(
  spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUaCOmMEzv",
  sheet_name="Contacts",
  values=[
    ["Name", "Email", "Phone"],
    ["John Doe", "john@example.com", "555-1234"],
    ["Jane Smith", "jane@example.com", "555-5678"],
    ["Bob Johnson", "bob@example.com", "555-9012"]
  ]
)

Result:
{
  "success": true,
  "updated_cells": 12,
  "updated_range": "Contacts!A1:C4"
}

AI Thinking: "Perfect! Spreadsheet created with headers and 3 data rows."
```

**Final Response to User**:

```
✅ Spreadsheet created successfully!

**Contact List**
https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUaCOmMEzv

I've added:
- Column headers: Name, Email, Phone
- 3 sample contacts:
  1. John Doe (john@example.com, 555-1234)
  2. Jane Smith (jane@example.com, 555-5678)
  3. Bob Johnson (bob@example.com, 555-9012)

The spreadsheet is ready to use!
```

---

## Benefits & Trade-offs

### ✅ Benefits

**1. Token Efficiency**
- **Initial**: 2,500 tokens (meta-tools only)
- **Traditional**: 297,000 tokens (all 594 tools)
- **Savings**: 99.2% reduction in initial context

**2. Scalability**
- Can add 1000 more tools without affecting initial load
- AI discovers tools on-demand
- No "too many tools" problem

**3. Cost Optimization**
- Only pay for tools AI actually uses
- Meta-tools are cheap (~500 tokens each)
- Full schemas only loaded when needed

**4. Performance**
- Faster API responses (less parsing)
- Smaller message payloads
- Better AI reasoning (less noise)

**5. Maintainability**
- Add new tools → Auto-discovered
- Update tool → Only affects that tool
- No global changes needed

**6. User Experience**
- AI finds right tool faster
- Less confusion from irrelevant tools
- More accurate tool selection

### ⚠️ Trade-offs

**1. Extra Rounds Required**
- Traditional: 1 round (AI has all tools)
- Progressive: 3-4 rounds (discover → learn → execute)
- **Impact**: +2-3 API calls per task

**2. Learning Overhead**
- AI must call meta-tools first
- Adds ~2 seconds per new platform
- **Mitigation**: Cache frequently used schemas

**3. Schema Consistency Required**
- All tools must follow same format
- Broken schema = AI can't learn
- **Solution**: Automated validation

**4. Initial Discovery Cost**
- First time using platform: Extra tokens
- Subsequent uses: Cached in conversation
- **Pattern**: Pay once, benefit repeatedly

### 📊 Token Cost Comparison

**Traditional Approach** (All 594 tools upfront):
```
Initial message: 297,000 tokens
User prompt:      100 tokens
AI response:      500 tokens
Tool execution:   200 tokens
─────────────────────────────────
TOTAL:           297,800 tokens
COST:            ~$0.89 (Claude Sonnet)
```

**Progressive Discovery** (Gmail example):
```
Meta-tools:       2,500 tokens
list_platforms:     500 tokens
list_tools:       1,500 tokens
get_schema:       2,000 tokens
User prompt:        100 tokens
AI response:        500 tokens
Tool execution:     200 tokens
─────────────────────────────────
TOTAL:            7,300 tokens
COST:             ~$0.02 (Claude Sonnet)
SAVINGS:          97.5%
```

---

## Advanced Features

### 1. Platform Aliases

**User-Friendly Names**:
```python
# User says: "outlook"
AI → list_platform_tools(platform="outlook")

# System expands to:
platform = "microsoft_outlook"

# Aliases:
{
  "outlook": "microsoft_outlook",
  "sheets": "google_sheets",
  "docs": "google_docs",
  "gmail": "gmail",
  "calendar": ["microsoft_calendar", "google_calendar"]
}
```

### 2. Smart Tool Suggestions

**Semantic Search**:
```python
AI → search_tools(query="send email with attachment")

Result:
[
  {"name": "gmail_send_email", "score": 0.95},
  {"name": "microsoft_outlook_send_email", "score": 0.92},
  {"name": "slack_send_message", "score": 0.45}
]
```

### 3. Workflow Recommendations

**Multi-Tool Tasks**:
```python
AI → recommend_tools_for_task(task="Export data to spreadsheet")

Result:
{
  "workflow": [
    "Step 1: xero_get_invoices (fetch data)",
    "Step 2: google_sheets_create_spreadsheet (create sheet)",
    "Step 3: google_sheets_add_rows (insert data)"
  ]
}
```

### 4. Infinite Loop Prevention

**Problem**: AI might repeatedly call discovery tools

**Solution**: Detection & Guidance
```python
# After 3 identical meta-tool calls:
System: "⚠️ INFINITE LOOP DETECTED: You've called list_platform_tools 
         3 times in a row. After discovering tools, proceed to 
         get_tool_schema() or execute_tool()."
```

### 5. Session Status Injection

**Token Awareness**:
```python
# After each tool execution:
Tool Result + Session Status:
"""
{result data}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 SESSION STATUS (Round 4/30)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tokens Used: 45,000 / 200,000 (22.5%)
Rounds Completed: 4/30
Status: 🟢 NORMAL

💡 You have plenty of context space.
   → Work freely, explore options
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
```

---

## Summary: How It All Works Together

### The Complete Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ USER REQUEST: "Send email to john@example.com"                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ ROUND 1: AI receives 5 meta-tools (2,500 tokens)                │
│   → list_available_platforms                                    │
│   → list_platform_tools                                         │
│   → get_tool_schema                                             │
│   → execute_tool                                                │
│   → search_tools                                                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ ROUND 2: AI discovers platforms (500 tokens)                    │
│   AI → list_available_platforms()                               │
│   Result: ["gmail", "google_sheets", "microsoft_outlook", ...]  │
│   AI Thinking: "gmail is relevant for email"                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ ROUND 3: AI discovers Gmail tools (1,500 tokens)                │
│   AI → list_platform_tools(platform="gmail")                    │
│   Result: ["gmail_send_email", "gmail_create_draft", ...]       │
│   AI Thinking: "gmail_send_email is what I need"                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ ROUND 4: AI learns tool parameters (2,000 tokens)               │
│   AI → get_tool_schema(tool_name="gmail_send_email")            │
│   Result: Full schema with examples, usage guide, errors        │
│   AI Thinking: "Required: to, subject, body. Got it!"           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ ROUND 5: AI executes tool (200 tokens)                          │
│   AI → gmail_send_email(                                        │
│     to=["john@example.com"],                                    │
│     subject="...",                                              │
│     body="..."                                                  │
│   )                                                             │
│   Result: {"success": true, "message_id": "..."}                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ FINAL RESPONSE: "✅ Email sent successfully!"                   │
│   Total tokens: 7,300 (vs 297,000 traditional)                  │
│   Total rounds: 5 (vs 1 traditional)                            │
│   Cost savings: 97.5%                                           │
│   Time overhead: +2-3 seconds (acceptable for 97% savings)      │
└─────────────────────────────────────────────────────────────────┘
```

### Key Takeaways

1. **Progressive Discovery = Just-In-Time Learning**
   - AI doesn't need to know ALL tools upfront
   - AI learns tools WHEN needed, not BEFORE needed

2. **Meta-Tools ARE the Instruction Manual**
   - No separate documentation needed
   - AI discovers capabilities through tool use
   - Self-documenting architecture

3. **Token Efficiency Through Laziness**
   - Only load what you need
   - Cache what you've loaded
   - Share across conversation

4. **Scalable to Thousands of Tools**
   - Adding tool doesn't increase initial cost
   - Discovery cost amortized across uses
   - No "tool overload" problem

5. **Trade-off: Latency vs Efficiency**
   - Extra 2-3 seconds for discovery
   - 97% token cost savings
   - Better tool selection accuracy

---

## Implementation Files

**Key Files to Understand**:

1. **`tools/registry_v3.py`** (864 lines)
   - Auto-loads tools from schemas/
   - Converts to Anthropic format
   - Provides meta-tool access

2. **`tools/implementations/meta_tools.py`** (984 lines)
   - list_available_platforms()
   - list_platform_tools()
   - get_tool_schema()
   - execute_tool()
   - search_tools()

3. **`tools/schemas/*.json`** (Multiple files)
   - gmail_tools.json
   - google_sheets_tools.json
   - microsoft_outlook_tools.json
   - etc.

4. **`AI_infrastructure/core/combined_agent_worker.py`** (2676 lines)
   - Streaming implementation
   - Tool execution loop
   - Session status injection
   - Infinite loop detection

---

## Conclusion

Progressive Tool Discovery solves the fundamental problem of **tool overload** in AI agent systems. By implementing a 4-tier Just-In-Time learning architecture, AI agents can:

- **Start fast** (5 meta-tools = 2,500 tokens)
- **Learn on-demand** (discover → explore → execute)
- **Scale infinitely** (594 tools → 1000+ tools, same cost)
- **Save 97%** token costs compared to traditional approaches

The system is **self-documenting** (AI learns by using tools), **efficient** (only loads what's needed), and **maintainable** (add tools without breaking existing ones).

**Result**: A production-ready system handling 594 tools across 20+ platforms with minimal token overhead and maximum flexibility.

---

**Next Steps**:
1. Read the Platform Tool Suite Construction Agent prompt (how to build new tool suites)
2. Explore existing schemas in `tools/schemas/`
3. Test progressive discovery with a sample request
4. Add your own platform tools following the same pattern

**Questions?** The architecture is designed to be self-explanatory through tool use. Start with `list_available_platforms()` and explore!
