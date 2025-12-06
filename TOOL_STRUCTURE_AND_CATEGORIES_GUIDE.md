# Tool Structure, Locations, and Categories - Complete Guide

**Created**: December 5, 2025  
**Purpose**: Comprehensive documentation of tool organization, file structure, formats, and categorization in the AI Agent platform

---

## 📁 Directory Structure

```
AI_agents/
├── tools/
│   ├── schemas/                  ← JSON schema definitions (82 files)
│   │   ├── gmail_tools.json
│   │   ├── google_sheets_tools.json
│   │   ├── microsoft_outlook_tools.json
│   │   ├── xero_tools.json
│   │   ├── synergy_tools.json
│   │   └── ... (77 more)
│   │
│   ├── implementations/          ← Python implementations (58 files)
│   │   ├── gmail_smart.py
│   │   ├── meta_tools.py
│   │   ├── automation.py
│   │   ├── calculator.py
│   │   └── ... (54 more)
│   │
│   ├── plugins/                  ← Module-specific plugins
│   │   └── (auto-loaded by registry)
│   │
│   ├── testing/                  ← Test suites
│   │
│   ├── registry_v3.py           ← Central tool registry (auto-discovery)
│   ├── intelligent_discovery.py ← Semantic search engine
│   └── requirements.txt         ← Tool dependencies
│
├── google_workspace/            ← Google tools (PRIMARY for Gmail, Drive, Docs, etc.)
│   ├── gmail.py
│   ├── google_docs.py
│   ├── google_sheets.py
│   └── ... (12 more)
│
├── Microsoft_365_Connection/    ← Microsoft tools (Outlook, Excel, Word, etc.)
│   └── microsoft_graph.py
│
├── UI/external/modules/         ← External platform modules
│   ├── xero/
│   ├── shopify/
│   ├── woocommerce/
│   └── ... (platform-specific)
│
└── inhouse_modules/             ← Internal business modules
    ├── calculator/
    ├── synergy_kanban/
    └── stock_management/
```

---

## 🗂️ Tool Categories (8 Types)

### 1. **Platform Integration Tools** (Largest Category)

**Purpose**: Connect to external platforms via OAuth APIs

**Platforms** (20+ major platforms):
```
Communication:
├── gmail (15 tools)
├── microsoft_outlook (12 tools)
├── slack (8 tools)
└── twilio (6 tools)

Productivity:
├── google_sheets (18 tools)
├── google_docs (14 tools)
├── google_drive (10 tools)
├── microsoft_excel (10 tools)
├── microsoft_word (8 tools)
└── notion (planned)

Business:
├── xero (25+ tools - accounting)
├── stripe (12 tools - payments)
├── shopify (10 tools - ecommerce)
├── woocommerce (8 tools - ecommerce)
├── paypal (6 tools - payments)
└── kajabi (20+ tools - courses)

Design/Media:
├── adobe_indesign (35+ tools)
├── cloudflare (8 tools - CDN)
└── cloudconvert (6 tools - file conversion)

Development:
├── github (12 tools)
├── render (10 tools - hosting)
└── google_cloud_run (8 tools)

Data/Analytics:
├── google_analytics (8 tools)
├── pinecone (vector database)
├── supabase (database)
└── sql_database (generic SQL)
```

**Schema Location**: `tools/schemas/{platform}_tools.json`  
**Implementation Location**: 
- Google: `google_workspace/{platform}.py` (PRIMARY)
- Microsoft: `Microsoft_365_Connection/microsoft_graph.py`
- Other: `tools/implementations/{platform}.py`

**File Format**: See [Platform Integration Format](#platform-integration-format)

---

### 2. **Smart/Bundled Tools** (AI-Enhanced)

**Purpose**: Intelligent wrappers that combine multiple operations with AI decision-making

**Examples**:
```python
# Gmail Smart Tools (tools/schemas/gmail_smart_tools.json)
- gmail_ai_smart_compose_and_send        # AI writes + sends email
- gmail_smart_bulk_send_personalized     # Mail merge with {{variables}}
- gmail_smart_inbox_organizer            # Auto-categorize/archive
- gmail_analyze_email_smart              # Token estimation + confirmation

# Kajabi Smart Tools (tools/schemas/kajabi_smart_tools.json)
- kajabi_smart_course_builder            # AI-generated course structure
- kajabi_smart_email_sequence            # Automated drip campaigns

# Google Docs Smart Tools (tools/schemas/google_docs_tools.json)
- google_docs_ai_format_document         # AI-powered formatting
- google_docs_smart_table_of_contents    # Auto-generate TOC
```

**Key Features**:
- ⚡ **Bundled Operations**: Multiple API calls in one tool
- 🤖 **AI Decision-Making**: Uses Claude/GPT for content generation
- 💰 **Cost-Aware**: Token estimation before execution
- ✅ **Confirmation System**: Asks user before large operations
- 🔄 **Error Recovery**: Automatic retries with fallbacks

**Category Field**: `"category": "smart_bundled"`

---

### 3. **Meta-Tools** (Discovery System)

**Purpose**: Tools that help AI discover and learn about other tools

**Schema**: `tools/schemas/meta_tools.json`  
**Implementation**: `tools/implementations/meta_tools.py`

**The 7 Meta-Tools**:
```python
1. list_available_platforms()
   → Returns: ["gmail", "google_sheets", "xero", ...]
   → Use: Initial discovery

2. list_platform_tools(platform)
   → Returns: Tool names + short descriptions (NO schemas)
   → Use: Narrow down to relevant platform

3. get_tool_schema(tool_name)
   → Returns: FULL Anthropic-formatted schema
   → Use: Learn how to use a specific tool

4. execute_tool(tool_name, **params)
   → Returns: Tool execution result
   → Use: Run the tool with credentials injected

5. search_tools(query)
   → Returns: Semantic search results across all tools
   → Use: Find tools by natural language query

6. get_platform_guide(platform)
   → Returns: Platform-specific usage patterns
   → Use: Learn platform best practices

7. recommend_tools_for_task(task)
   → Returns: Multi-step workflow recommendations
   → Use: Complex tasks requiring multiple tools
```

**Special Properties**:
- ✅ **Never Truncated**: Exempted from 2K token limit
- 🚫 **Infinite Loop Detection**: Prevents repeated calls
- 📚 **Self-Documenting**: AI learns by using tools

See [PROGRESSIVE_TOOL_DISCOVERY_ARCHITECTURE.md](./PROGRESSIVE_TOOL_DISCOVERY_ARCHITECTURE.md) for complete details.

---

### 4. **Automation Tools** (Workflow Engine)

**Purpose**: Visual workflow builder with triggers, actions, and conditions

**Schema**: `tools/schemas/automation_tools.json`  
**Implementation**: `tools/implementations/automation.py`

**Tool Types**:
```python
# Automation Management
- automation_create_workflow
- automation_update_workflow
- automation_delete_workflow
- automation_list_workflows
- automation_get_workflow

# Workflow Execution
- automation_trigger_workflow_manually
- automation_get_execution_logs
- automation_get_workflow_analytics

# Visual Canvas
- automation_visual_create_node
- automation_visual_connect_nodes
- automation_visual_set_trigger
```

**Workflow Structure**:
```json
{
  "id": "wf_12345",
  "name": "Invoice Automation",
  "trigger": {
    "type": "webhook",
    "platform": "xero",
    "event": "invoice.created"
  },
  "nodes": [
    {
      "id": "node_1",
      "type": "condition",
      "check": "invoice.amount > 1000"
    },
    {
      "id": "node_2",
      "type": "action",
      "tool": "gmail_send_email",
      "params": {"to": "manager@company.com"}
    }
  ]
}
```

**Database Tables**:
- `automation_workflows` - Workflow definitions
- `automation_execution_logs` - Execution history
- `automation_workflow_analytics` - Performance metrics

---

### 5. **Synergy Tools** (Internal Kanban)

**Purpose**: In-house project management with AI agent coordination

**Schemas** (4 files):
```
tools/schemas/synergy_tools.json                    # Core CRUD
tools/schemas/synergy_instruction_tools.json        # AI instructions
tools/schemas/synergy_recommender_tools.json        # Smart suggestions
tools/schemas/synergy_smart_internal_doc_tool.json  # Documentation
```

**Implementation**: `inhouse_modules/synergy_kanban/`

**Core Tools**:
```python
# Card Management
- synergy_create_card
- synergy_update_card
- synergy_delete_card
- synergy_get_card_details

# Board Operations
- synergy_list_cards_by_column
- synergy_move_card
- synergy_assign_card
- synergy_archive_card

# AI Coordination
- synergy_create_instruction_card        # Instructions for agents
- synergy_recommend_next_actions         # AI suggestions
- synergy_update_milestone               # Progress tracking
```

**Database Tables**:
- `synergy_cards` - Card definitions
- `synergy_columns` - Board columns (To Do, In Progress, Done)
- `synergy_milestones` - Milestone tracking
- `synergy_tags` - Tag system
- `synergy_comments` - Comments/activity log

**Real-Time Sync**: PostgreSQL + WebSockets

---

### 6. **Calculator Tools** (Business Calculations)

**Purpose**: Complex pricing calculations for printing business

**Schema**: `tools/schemas/calculator_tools.json`  
**Implementation**: `UI/external/modules/calculator/`

**Product Calculators** (15+ tools):
```python
# Print Products
- calculate_flyers
- calculate_business_cards
- calculate_booklets
- calculate_perfect_bound_books
- calculate_saddle_stitch_books
- calculate_spiral_bound_books

# Signage
- calculate_corflute_signs
- calculate_bollard_signs
- calculate_election_signs
- calculate_construction_signs

# Specialty Items
- calculate_stackable_cubes
- calculate_selfie_frames
- calculate_vinyl_stickers       # Uses VSA stock database

# Stock Management
- get_stock_list
- query_vinyl_stock
- update_stock_levels
```

**Database Tables**:
- `vinyl_stock_analysis` (VSA) - Stock inventory
- `product_pricing` - Base pricing rules
- `material_costs` - Raw material prices

---

### 7. **Memory/Context Tools** (Semantic Search)

**Purpose**: Long-term memory and semantic search across conversations

**Schema**: `tools/schemas/memory_tools.json`  
**Implementation**: `tools/implementations/memory_tools.py`

**Tools**:
```python
# Memory Storage
- memory_store_context
- memory_retrieve_context
- memory_search_semantic

# Vector Database
- vector_store_document
- vector_search_similar
- vector_delete_document

# Citation System
- memory_get_citations
- memory_link_to_source
```

**Vector Database Integration**:
- **Provider**: Pinecone or Supabase pgvector
- **Embedding Model**: text-embedding-ada-002 (OpenAI)
- **Dimensions**: 1536
- **Search**: Cosine similarity

**Use Cases**:
- Thread context across sessions
- Document chunking and retrieval
- Semantic search in email history
- Citation tracking for AI responses

---

### 8. **Scheduler Tools** (Cron/Automation)

**Purpose**: Time-based automation and recurring tasks

**Schema**: `tools/schemas/scheduler_tools.json`  
**Implementation**: `tools/implementations/scheduler.py`

**Tools**:
```python
# Schedule Management
- scheduler_create_job
- scheduler_update_job
- scheduler_delete_job
- scheduler_list_jobs
- scheduler_pause_job
- scheduler_resume_job

# Execution
- scheduler_run_now           # Immediate execution
- scheduler_get_job_history   # Execution logs
```

**Cron Syntax Support**:
```python
# Examples
"0 9 * * 1"       # Every Monday at 9am
"*/15 * * * *"    # Every 15 minutes
"0 0 1 * *"       # First day of month at midnight
```

**Database Tables**:
- `scheduled_jobs` - Job definitions
- `job_execution_history` - Execution logs
- `job_errors` - Error tracking

---

## 📄 Schema Format (JSON)

### Platform Integration Format

**File**: `tools/schemas/{platform}_tools.json`

```json
{
  "platform": "gmail",
  "version": "2.0",
  "description": "Gmail API - Complete email management...",
  
  "tools": [
    {
      "name": "gmail_send_email",
      "platform": "gmail",
      "category": "basic",
      
      "description": "Send an email via Gmail with OAuth2 authentication.\n\n[200-300 words]\n\nUse this tool when:\n- User explicitly asks to 'send email'\n- ...\n\nDO NOT use this tool when:\n- User wants to CREATE A DRAFT → Use gmail_create_draft\n- ...",
      
      "parameters": {
        "type": "object",
        "properties": {
          "to": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Recipient email addresses...\n\nExamples:\n- ['john@example.com']\n- ..."
          },
          "subject": {
            "type": "string",
            "description": "Email subject line...",
            "maxLength": 998
          },
          "body": {
            "type": "string",
            "description": "Email body content..."
          },
          "cc": {
            "type": "array",
            "items": {"type": "string"},
            "description": "CC recipients (optional)",
            "default": []
          }
        },
        "required": ["to", "subject", "body"]
      },
      
      "returns": {
        "type": "object",
        "properties": {
          "success": {"type": "boolean"},
          "message_id": {"type": "string"},
          "error": {"type": "string"}
        }
      },
      
      "examples": [
        {
          "description": "Simple email - Basic usage",
          "parameters": {
            "to": ["john@example.com"],
            "subject": "Meeting Follow-up",
            "body": "Hi John,\n\nThanks for the meeting..."
          },
          "expected_result": {
            "success": true,
            "message_id": "18f2a3b4c5d6e7f8"
          }
        },
        {
          "description": "Error case - Invalid email",
          "parameters": {
            "to": ["invalid-email"],
            "subject": "Test",
            "body": "Test"
          },
          "expected_result": {
            "success": false,
            "error": "Invalid email format"
          }
        }
      ],
      
      "usage_guide": {
        "when_to_use": [
          "User explicitly says 'send email' or 'email to...'",
          "User provides recipient email address",
          "User has confirmed the email should be sent NOW"
        ],
        "when_not_to_use": [
          "User wants to CREATE A DRAFT → Use gmail_create_draft",
          "User wants to REPLY → Use gmail_reply_to_message"
        ],
        "workflow": [
          "Step 1: Confirm user wants to SEND (not draft)",
          "Step 2: Verify recipient email address",
          "Step 3: Call tool with parameters",
          "Step 4: Confirm success to user"
        ],
        "best_practices": [
          "ALWAYS confirm recipient before sending",
          "Use descriptive subject lines",
          "Store returned message_id for tracking"
        ],
        "error_handling": [
          "Error 401: User needs to re-authenticate",
          "Error 400: Invalid email format → Check addresses"
        ],
        "related_tools": [
          "gmail_create_draft - Use if user wants to review first",
          "gmail_reply_to_message - Use if replying to existing"
        ]
      },
      
      "tool_intelligence": {
        "category": "communication",
        "typical_workflow_patterns": [
          "gmail_list_messages → gmail_send_email",
          "gmail_get_message → gmail_reply_to_message"
        ],
        "success_indicators": {
          "keywords": ["sent successfully", "delivered"],
          "behavioral": ["User thanks AI", "User sends another"]
        }
      },
      
      "memory_context": {
        "vectorization_fields": ["subject", "body", "to"],
        "search_keywords": ["email", "gmail", "send", "message"],
        "related_synergy_platforms": ["gmail"],
        "typical_use_cases": [
          "Send meeting notes to team",
          "Send invoice to client"
        ]
      }
    }
  ]
}
```

### Schema Field Breakdown

**Top-Level Fields**:
```json
{
  "platform": "gmail",           // Platform identifier (REQUIRED)
  "version": "2.0",              // Schema version
  "description": "...",          // Platform overview (50-100 words)
  "tools": [...]                 // Array of tool definitions
}
```

**Tool Object Fields**:
```json
{
  "name": "gmail_send_email",             // Unique tool identifier (REQUIRED)
  "platform": "gmail",                    // Platform (inherits from top-level)
  "category": "basic",                    // Tool category (optional)
  "description": "...",                   // 200-300 words (REQUIRED)
  "parameters": {...},                    // Anthropic-compatible schema (REQUIRED)
  "returns": {...},                       // Return value structure
  "examples": [...],                      // 3+ examples (REQUIRED)
  "usage_guide": {...},                   // 6 subsections (REQUIRED)
  "tool_intelligence": {...},             // Analytics metadata (optional)
  "memory_context": {...}                 // Semantic search metadata (optional)
}
```

**Parameter Schema** (Anthropic-Compatible):
```json
{
  "type": "object",
  "properties": {
    "param_name": {
      "type": "string",                   // string, array, object, boolean, integer
      "description": "...",               // DETAILED description with examples
      "required": false,                  // Required vs optional
      "default": "value",                 // Default value (optional params only)
      "maxLength": 998,                   // Validation rules (optional)
      "enum": ["option1", "option2"]      // Allowed values (optional)
    }
  },
  "required": ["param1", "param2"]        // List of required params
}
```

**Usage Guide Structure** (CRITICAL):
```json
{
  "when_to_use": [                        // 4-5 scenarios
    "User explicitly asks to send email",
    "User provides recipient address"
  ],
  "when_not_to_use": [                    // 3-4 alternatives
    "User wants draft → Use gmail_create_draft",
    "User wants reply → Use gmail_reply_to_message"
  ],
  "workflow": [                           // 4-6 step process
    "Step 1: Confirm user wants to send",
    "Step 2: Verify recipient",
    "Step 3: Call tool",
    "Step 4: Confirm success"
  ],
  "best_practices": [                     // 4-5 tips
    "Always confirm recipient before sending",
    "Use descriptive subject lines"
  ],
  "error_handling": [                     // 5-7 common errors
    "Error 401: Re-authenticate",
    "Error 400: Invalid format → Check addresses"
  ],
  "related_tools": [                      // 3-6 alternative tools
    "gmail_create_draft - Review first",
    "gmail_reply_to_message - Reply to existing"
  ]
}
```

---

## 🐍 Implementation Format (Python)

**File**: `tools/implementations/{platform}.py`

```python
"""
PLATFORM TOOLS - Implementation
================================

This module implements all tools for [platform] platform.
Tools use OAuth2 authentication via credential injection.

Credential Injection:
- **kwargs contains _user_id (required)
- **kwargs contains _injected_credentials (OAuth tokens)

All tools must:
1. Extract credentials from **kwargs
2. Use credentials for API authentication
3. Return standardized response format
4. Handle errors gracefully
"""

from typing import Dict, Any, Optional, List
import sys
from pathlib import Path

# Import shared utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from AI_infrastructure.core.credential_injector import get_user_credentials

# Import platform SDK
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def gmail_send_email(
    to: List[str],
    subject: str,
    body: str,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    attachments: Optional[List[Dict]] = None,
    **kwargs  # Contains _user_id, _injected_credentials
) -> Dict[str, Any]:
    """
    Send an email via Gmail
    
    This tool uses OAuth2 credentials injected by the credential injector.
    DO NOT ask user for credentials - they are automatically provided.
    
    Args:
        to: Recipient email addresses
        subject: Email subject line
        body: Email body content
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        attachments: File attachments (optional)
        **kwargs: Contains _user_id, _injected_credentials
    
    Returns:
        {
            "success": true,
            "message_id": "18f2a3b4c5d6e7f8",
            "thread_id": "18f2a3b4c5d6e7f8"
        }
    
    Raises:
        ValueError: Invalid email format
        AuthError: OAuth credentials expired
        APIError: Gmail API error
    """
    # STEP 1: Extract credentials from kwargs
    user_id = kwargs.get('_user_id')
    injected_creds = kwargs.get('_injected_credentials', {})
    
    if not user_id:
        return {
            "success": False,
            "error": "Missing _user_id in kwargs (credential injection failure)"
        }
    
    # STEP 2: Get OAuth credentials for this user
    gmail_creds = injected_creds.get('gmail')
    if not gmail_creds:
        return {
            "success": False,
            "error": "User not authenticated with Gmail. Please authenticate first.",
            "auth_url": "/oauth/gmail/authorize"
        }
    
    try:
        # STEP 3: Build Gmail API service
        credentials = Credentials(
            token=gmail_creds['access_token'],
            refresh_token=gmail_creds.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=gmail_creds['client_id'],
            client_secret=gmail_creds['client_secret']
        )
        
        service = build('gmail', 'v1', credentials=credentials)
        
        # STEP 4: Build email message
        message = _build_email_message(to, subject, body, cc, bcc, attachments)
        
        # STEP 5: Send email
        result = service.users().messages().send(
            userId='me',
            body={'raw': message}
        ).execute()
        
        # STEP 6: Return standardized response
        return {
            "success": True,
            "message_id": result['id'],
            "thread_id": result['threadId'],
            "labels": result.get('labelIds', [])
        }
        
    except Exception as e:
        # STEP 7: Error handling
        error_type = type(e).__name__
        error_msg = str(e)
        
        # Specific error handling
        if 'invalid_grant' in error_msg.lower():
            return {
                "success": False,
                "error": "OAuth credentials expired. User needs to re-authenticate.",
                "auth_url": "/oauth/gmail/authorize",
                "error_type": "AuthError"
            }
        elif 'invalid email' in error_msg.lower():
            return {
                "success": False,
                "error": f"Invalid email format: {', '.join(to)}",
                "error_type": "ValidationError"
            }
        else:
            return {
                "success": False,
                "error": f"Gmail API error: {error_msg}",
                "error_type": error_type
            }


def _build_email_message(
    to: List[str],
    subject: str,
    body: str,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    attachments: Optional[List[Dict]] = None
) -> str:
    """
    Build RFC 2822 email message
    
    Returns base64-encoded message string
    """
    import base64
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    message = MIMEMultipart()
    message['to'] = ', '.join(to)
    message['subject'] = subject
    
    if cc:
        message['cc'] = ', '.join(cc)
    if bcc:
        message['bcc'] = ', '.join(bcc)
    
    # Attach body
    message.attach(MIMEText(body, 'plain'))
    
    # TODO: Attach files if attachments provided
    
    # Encode to base64
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return raw


# Export all tools
__all__ = [
    'gmail_send_email',
    'gmail_create_draft',
    'gmail_list_messages',
    # ... more tools
]
```

### Implementation Key Patterns

**1. Credential Injection** (CRITICAL):
```python
def tool_function(**kwargs):
    user_id = kwargs.get('_user_id')              # User identifier
    creds = kwargs.get('_injected_credentials')   # OAuth tokens
    
    if not user_id:
        return {"success": False, "error": "Missing _user_id"}
```

**2. Standardized Response Format**:
```python
# Success
return {
    "success": True,
    "data": {...},           # Tool-specific data
    "message": "Optional success message"
}

# Error
return {
    "success": False,
    "error": "Human-readable error",
    "error_type": "AuthError",
    "suggestion": "Please re-authenticate"
}
```

**3. Error Handling**:
```python
try:
    result = api_call()
    return {"success": True, "data": result}
except AuthenticationError:
    return {
        "success": False,
        "error": "OAuth expired",
        "auth_url": "/oauth/{platform}/authorize"
    }
except ValidationError as e:
    return {
        "success": False,
        "error": f"Invalid input: {e}"
    }
except Exception as e:
    return {
        "success": False,
        "error": f"Unexpected error: {e}",
        "error_type": type(e).__name__
    }
```

---

## 🔍 Tool Discovery Flow

**How AI Finds and Uses Tools**:

```
┌─────────────────────────────────────────────────────────────┐
│ USER: "Send email to john@example.com about the meeting"   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ AI AGENT (Claude) - Initial State                          │
│ Known Tools: 5 meta-tools only                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Platform Discovery                                 │
│ AI → list_available_platforms()                            │
│ Result: ["gmail", "microsoft_outlook", "slack", ...]       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Tool Discovery                                     │
│ AI → list_platform_tools(platform="gmail")                 │
│ Result: ["gmail_send_email", "gmail_create_draft", ...]    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Schema Learning                                    │
│ AI → get_tool_schema(tool_name="gmail_send_email")         │
│ Result: Full 2000-token schema with examples, usage guide  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Tool Execution                                     │
│ AI → execute_tool(                                         │
│   tool_name="gmail_send_email",                            │
│   to=["john@example.com"],                                 │
│   subject="Meeting Follow-up",                             │
│   body="Hi John, thanks for the meeting..."                │
│ )                                                          │
│                                                            │
│ Registry injects credentials automatically                 │
│ Returns: {"success": true, "message_id": "..."}            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ AI RESPONSE TO USER:                                       │
│ "✅ Email sent successfully to john@example.com!"          │
│ Message ID: 18f2a3b4c5d6e7f8                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Tool Statistics

**Total Tools**: 594+ across 20+ platforms

**Breakdown by Category**:
```
Platform Integration:    450 tools (76%)
├── Google Workspace:    90 tools
├── Microsoft 365:       65 tools
├── Business (Xero, etc): 120 tools
├── Communication:       45 tools
└── Other Platforms:     130 tools

Smart/Bundled:          35 tools (6%)
Meta-Tools:             7 tools (1%)
Automation:             25 tools (4%)
Synergy (Kanban):       40 tools (7%)
Calculator:             20 tools (3%)
Memory/Context:         10 tools (2%)
Scheduler:              7 tools (1%)
```

**Most Used Platforms** (by tool call frequency):
1. Gmail (email management)
2. Google Sheets (data manipulation)
3. Xero (accounting)
4. Synergy (internal kanban)
5. Google Docs (document creation)

---

## 🔐 Security & Credentials

### OAuth Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER INITIATES AUTH                                     │
│    Frontend: /oauth/{platform}/authorize                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. REDIRECT TO PLATFORM                                    │
│    Google: accounts.google.com/o/oauth2/auth              │
│    Microsoft: login.microsoftonline.com/common/oauth2/... │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. USER GRANTS PERMISSIONS                                 │
│    Platform shows scopes: "Read emails, Send emails"       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. CALLBACK WITH AUTH CODE                                 │
│    Backend: /oauth/{platform}/callback?code=xyz            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. EXCHANGE CODE FOR TOKENS                                │
│    Backend → Platform: Exchange auth code                  │
│    Platform → Backend: Access token + Refresh token        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. STORE IN DATABASE (ENCRYPTED)                           │
│    Table: platform_credentials                             │
│    Columns: user_id, platform, access_token (encrypted),   │
│             refresh_token (encrypted), expires_at          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. TOOL EXECUTION WITH INJECTED CREDENTIALS                │
│    AI calls: execute_tool(tool_name="gmail_send_email")    │
│    Registry: Fetches credentials from DB                   │
│    Registry: Injects into **kwargs                         │
│    Tool: Uses credentials for API call                     │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema (platform_credentials)

```sql
CREATE TABLE platform_credentials (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    platform VARCHAR(50) NOT NULL,          -- 'gmail', 'xero', etc.
    email VARCHAR(255),                     -- User's email on platform
    access_token TEXT,                      -- Encrypted OAuth token
    refresh_token TEXT,                     -- Encrypted refresh token
    expires_at TIMESTAMP,                   -- Token expiration
    scopes TEXT[],                          -- Granted permissions
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, platform)               -- One credential per user per platform
);
```

---

## 🛠️ Creating New Tools

### Quick Start Checklist

**1. Create JSON Schema** (`tools/schemas/{platform}_tools.json`):
```json
{
  "platform": "your_platform",
  "version": "1.0",
  "description": "Platform description...",
  "tools": [
    {
      "name": "your_platform_action",
      "description": "200-300 words with use cases...",
      "parameters": {
        "type": "object",
        "properties": {...},
        "required": [...]
      },
      "examples": [...],
      "usage_guide": {...}
    }
  ]
}
```

**2. Create Python Implementation** (`tools/implementations/{platform}.py`):
```python
def your_platform_action(param1, param2, **kwargs):
    user_id = kwargs.get('_user_id')
    creds = kwargs.get('_injected_credentials', {})
    
    # Use credentials for API call
    # Return standardized response
    return {"success": True, "data": result}
```

**3. Registry Auto-Discovers**:
- Schema loaded from `tools/schemas/`
- Implementation loaded from `tools/implementations/`
- Tool available immediately via `execute_tool()`

**4. Test Tool**:
```python
# Test in Python
from tools.registry_v3 import RegistryV3
registry = RegistryV3()

result = registry.execute_tool(
    tool_name='your_platform_action',
    param1='value1',
    _user_id=1,
    _injected_credentials={'your_platform': {...}}
)
```

---

## 📚 Related Documentation

- [PROGRESSIVE_TOOL_DISCOVERY_ARCHITECTURE.md](./PROGRESSIVE_TOOL_DISCOVERY_ARCHITECTURE.md) - How AI learns tools
- [TOOL_CONSTRUCTION_PROCESS.md](./TOOL_CONSTRUCTION_PROCESS.md) - Building new tools
- [COMPLETE_TOOL_SCHEMA_PATTERN.md](./COMPLETE_TOOL_SCHEMA_PATTERN.md) - Schema templates
- [PLATFORM_CREDENTIALS_QUICK_START.md](./PLATFORM_CREDENTIALS_QUICK_START.md) - OAuth setup

---

## 🎯 Summary

**Tool Organization**:
- **Schemas**: `tools/schemas/*.json` (82 files)
- **Implementations**: `tools/implementations/*.py` (58 files)
- **Registry**: Auto-discovers and loads all tools

**8 Categories**:
1. Platform Integration (450 tools)
2. Smart/Bundled (35 tools)
3. Meta-Tools (7 tools)
4. Automation (25 tools)
5. Synergy Kanban (40 tools)
6. Calculator (20 tools)
7. Memory/Context (10 tools)
8. Scheduler (7 tools)

**Key Features**:
- ✅ Auto-discovery via registry_v3.py
- 🔐 OAuth credential injection
- 📚 Self-documenting schemas
- 🤖 AI-powered meta-tools
- 🔄 Standardized response format
- ⚡ 594+ tools across 20+ platforms

**Progressive Discovery**:
AI starts with 5 meta-tools → Discovers 20+ platforms → Learns specific tool schemas → Executes with injected credentials
