# AI Agents Tool System Architecture - Complete Analysis

**Date:** November 15, 2025  
**Source:** AI_Agents Project (https://github.com/gerardovsa/Ai_Agents/tree/v5)  
**Total Tools:** 600+ across 20+ platforms  
**Analysis Scope:** Tool design, schemas, progressive discovery, AI reasoning workflow

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Tool Registry Architecture](#tool-registry-architecture)
3. [Schema System Design](#schema-system-design)
4. [Meta-Tools: Progressive Discovery](#meta-tools-progressive-discovery)
5. [Google Workspace: Complete Platform Analysis](#google-workspace-complete-platform-analysis)
6. [AI Tool Selection Workflow](#ai-tool-selection-workflow)
7. [Credential Injection System](#credential-injection-system)
8. [Implementation Patterns](#implementation-patterns)

---

## Executive Summary

The AI_Agents project implements a **sophisticated 3-tier tool discovery system** that scales to 600+ tools across 20+ platforms without overwhelming Claude with tool schemas.

### Key Innovation: Progressive Tool Discovery

**Traditional Approach (Fails at scale):**
```
Send ALL 600 tool schemas to Claude upfront
→ Token overflow (200,000+ tokens)
→ Claude confused by too many options
→ Poor tool selection
```

**AI_Agents Approach (Scales infinitely):**
```
Tier 1: Meta-Tools (8 tools) → Claude learns HOW to discover tools
Tier 2: Platform Browsing → Claude narrows to specific platform
Tier 3: Tool Execution → Claude gets schema only when needed
```

### Architecture Highlights

| Component | Purpose | Scale |
|-----------|---------|-------|
| **Registry V3** | Central tool catalog | 584 tools |
| **Meta-Tools** | Tool discovery system | 8 meta-tools |
| **Schemas** | JSON tool definitions | 50+ schema files |
| **Implementations** | Actual tool code | 30+ modules |
| **Google Workspace** | Primary integration | 190+ tools across 10 platforms |
| **Credential Injection** | Per-user OAuth | 750+ lines |

---

## Tool Registry Architecture

### RegistryV3: Central Nervous System

**File:** `tools/registry_v3.py` (450+ lines)

```python
class RegistryV3:
    """
    Enhanced tool registry with:
    1. Schema loading (JSON → tool definitions)
    2. Implementation loading (Python → executable functions)
    3. Credential injection support
    4. Anthropic API format conversion
    """
    
    def __init__(self):
        self.tools = {}              # tool_name → schema
        self.implementations = {}    # module_name → Python module
        
        # Load components
        self._load_schemas()         # From tools/schemas/*.json
        self._load_implementations() # From google_workspace/*.py + tools/implementations/*.py
        
    def execute_tool(self, **kwargs) -> Any:
        """Execute tool with automatic credential injection"""
        tool_name = kwargs.get('tool_name')
        user_id = kwargs.get('_user_id')
        
        # Get implementation
        impl_function = self.get_tool_function(tool_name)
        
        # Inject credentials if needed
        if user_id and '_injected_credentials' in inspect.signature(impl_function).parameters:
            kwargs['_injected_credentials'] = True
            
        # Execute
        return impl_function(**kwargs)
```

### Two-Phase Loading System

**Phase 1: Schema Loading (tools/schemas/)**
```
tools/schemas/
├── gmail_tools.json              (30 tools)
├── google_docs_tools.json        (31 tools)
├── google_sheets_tools.json      (7 tools)
├── google_calendar_tools.json    (12 tools)
├── google_forms_tools.json       (32 tools)
├── google_drive_tools.json       (15 tools)
├── google_tasks_tools.json       (12 tools)
├── google_slides_tools.json      (16 tools)
├── google_meet_tools.json        (14 tools)
├── google_analytics_tools.json   (12 tools)
├── microsoft_outlook_tools.json  (23 tools)
├── microsoft_excel_tools.json    (23 tools)
├── microsoft_word_tools.json     (19 tools)
├── microsoft_teams_tools.json    (15 tools)
├── microsoft_todo_tools.json     (18 tools)
├── microsoft_calendar_tools.json (17 tools)
└── ... (35+ more schema files)

TOTAL: 584 tool definitions
```

**Phase 2: Implementation Loading**

**Priority 1:** `google_workspace/` directory (Google tools)
```python
google_workspace/
├── gmail.py                    (45 functions)
├── google_docs.py              (38 functions)
├── google_forms.py             (98 functions)
├── google_drive.py             (22 functions)
├── google_calendar.py          (11 functions)
├── google_tasks.py             (25 functions)
├── google_slides.py            (19 functions)
├── google_meet.py              (23 functions)
├── google_analytics.py         (19 functions)
├── google_cloud_run.py         (18 functions)
└── google_auth_helper.py       (12 functions - credential builders)

TOTAL: 330+ Google functions
```

**Priority 2:** `tools/implementations/` directory (Other platforms)
```python
tools/implementations/
├── microsoft_calendar_tools.py (600+ lines, 17 functions)
├── microsoft_todo_tools.py     (800+ lines, task management)
├── microsoft_outlook_tools.py  (Outlook email)
├── microsoft_word_tools.py     (Word documents)
├── microsoft_excel_tools.py    (Excel spreadsheets)
├── woocommerce_tools.py        (E-commerce)
├── stripe_tools.py             (Payments)
└── meta_tools.py               (Tool discovery - 8 functions)

TOTAL: 254+ non-Google functions
```

### Registry Singleton Pattern

```python
# Global registry instance
_registry_instance = None

def get_registry() -> RegistryV3:
    """Get or create singleton registry"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = RegistryV3()
    return _registry_instance
```

**Why Singleton?**
- Load schemas once (expensive operation)
- Consistent tool state across application
- Share implementation cache

---

## Schema System Design

### JSON Schema Format

Every tool follows this structure:

```json
{
  "name": "google_calendar_create_event",
  "description": "Create a new calendar event with title, date, time, and optional attendees. Supports recurring events and reminders.",
  "platform": "google_calendar",
  "category": "scheduling",
  "parameters": {
    "summary": {
      "type": "string",
      "description": "Event title/summary",
      "required": true,
      "example": "Team Meeting"
    },
    "start_time": {
      "type": "string",
      "description": "Start time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)",
      "required": true,
      "example": "2025-11-15T14:00:00"
    },
    "end_time": {
      "type": "string",
      "description": "End time in ISO 8601 format",
      "required": true,
      "example": "2025-11-15T15:00:00"
    },
    "attendees": {
      "type": "array",
      "description": "List of attendee email addresses",
      "required": false,
      "items": {"type": "string"},
      "example": ["john@example.com", "jane@example.com"]
    },
    "recurrence": {
      "type": "string",
      "description": "Recurrence rule (RRULE format) for recurring events",
      "required": false,
      "example": "FREQ=WEEKLY;BYDAY=MO,WE,FR"
    }
  },
  "returns": {
    "type": "object",
    "description": "Created event details",
    "properties": {
      "event_id": {"type": "string"},
      "html_link": {"type": "string"},
      "hangout_link": {"type": "string"}
    }
  },
  "examples": [
    {
      "description": "Create a one-time meeting",
      "code": "google_calendar_create_event(summary='Weekly Standup', start_time='2025-11-18T10:00:00', end_time='2025-11-18T10:30:00', attendees=['team@company.com'])"
    },
    {
      "description": "Create recurring event (every Monday at 2 PM)",
      "code": "google_calendar_create_event(summary='Team Review', start_time='2025-11-18T14:00:00', end_time='2025-11-18T15:00:00', recurrence='FREQ=WEEKLY;BYDAY=MO')"
    }
  ]
}
```

### Schema Components Explained

| Field | Purpose | AI Benefit |
|-------|---------|------------|
| **name** | Unique tool identifier | Disambiguates similar tools |
| **description** | Rich explanation with use cases | Helps AI understand WHEN to use tool |
| **platform** | Platform grouping | Enables platform-specific discovery |
| **category** | Functional grouping | Cross-platform task matching |
| **parameters** | Typed parameter definitions | Validates input, shows examples |
| **returns** | Expected output structure | Helps AI understand result format |
| **examples** | Real-world usage scenarios | Teaches AI correct usage patterns |

### Anthropic API Conversion

Registry converts internal schema to Anthropic's function calling format:

```python
def get_anthropic_tools(self) -> List[Dict[str, Any]]:
    """Convert all tool schemas to Anthropic format"""
    anthropic_tools = []
    
    for tool_name, tool_schema in self.tools.items():
        # Convert to Anthropic format
        anthropic_tool = {
            "name": tool_name,
            "description": tool_schema["description"],
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
        
        # Add parameters
        for param_name, param_def in tool_schema.get("parameters", {}).items():
            anthropic_tool["input_schema"]["properties"][param_name] = {
                "type": param_def["type"],
                "description": param_def["description"]
            }
            
            if param_def.get("required"):
                anthropic_tool["input_schema"]["required"].append(param_name)
        
        anthropic_tools.append(anthropic_tool)
    
    return anthropic_tools
```

**Claude receives:**
```json
{
  "name": "google_calendar_create_event",
  "description": "Create a new calendar event...",
  "input_schema": {
    "type": "object",
    "properties": {
      "summary": {"type": "string", "description": "Event title/summary"},
      "start_time": {"type": "string", "description": "Start time in ISO 8601..."},
      ...
    },
    "required": ["summary", "start_time", "end_time"]
  }
}
```

---

## Meta-Tools: Progressive Discovery

### The Problem: Tool Overwhelm

**Scenario:** User asks "send me a calendar invite"

**Bad Approach:**
```
Send ALL 584 tool schemas to Claude
→ 200,000+ tokens consumed
→ Claude sees:
   - google_calendar_create_event
   - google_calendar_update_event
   - google_calendar_delete_event
   - microsoft_calendar_create_event
   - microsoft_calendar_update_event
   - gmail_send_email (wrong tool!)
   - google_tasks_create_task (wrong tool!)
   - ... 577 more tools
→ Claude confused, picks wrong tool
```

**Meta-Tools Approach:**
```
Step 1: Claude gets ONLY 8 meta-tools upfront
Step 2: Claude calls list_platform_tools("google_calendar")
        → Returns 12 calendar tool names (no schemas yet)
Step 3: Claude calls get_tool_schema("google_calendar_create_event")
        → Returns FULL schema for just this ONE tool
Step 4: Claude executes tool with correct parameters
```

### Meta-Tools Catalog

**File:** `tools/implementations/meta_tools.py` (610+ lines)

```python
"""
Meta-Tools Implementation - Tool discovery and guidance
These meta-tools help Claude discover and use the 604+ available tools
"""

# 1. PLATFORM DISCOVERY
def list_available_platforms(**kwargs) -> Dict[str, Any]:
    """
    List all 20+ platforms with tool counts
    
    Returns:
    {
        "platforms": [
            {"name": "google_calendar", "tool_count": 12, "description": "..."},
            {"name": "microsoft_outlook", "tool_count": 23, "description": "..."},
            ...
        ]
    }
    """
    
# 2. PLATFORM TOOL LISTING
def list_platform_tools(platform: str, **kwargs) -> Dict[str, Any]:
    """
    List all tools for a specific platform (NO schemas yet)
    
    Args:
        platform: "google_calendar", "microsoft_outlook", etc.
    
    Returns:
    {
        "platform": "google_calendar",
        "tool_count": 12,
        "tools": [
            {"name": "google_calendar_create_event", "description": "Create event..."},
            {"name": "google_calendar_list_events", "description": "List events..."},
            ...
        ]
    }
    """
    
# 3. TOOL SCHEMA RETRIEVAL (KEY STEP!)
def get_tool_schema(tool_name: str, **kwargs) -> Dict[str, Any]:
    """
    Get FULL Anthropic-formatted schema for ONE specific tool
    
    This is CRITICAL - AI only gets full parameter details when calling this!
    
    Args:
        tool_name: Exact tool name (e.g., "google_calendar_create_event")
    
    Returns:
    {
        "name": "google_calendar_create_event",
        "description": "...",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {...},
                "start_time": {...},
                ...
            },
            "required": ["summary", "start_time", "end_time"]
        }
    }
    """
    
# 4. CROSS-PLATFORM SEARCH
def search_tools(query: str, **kwargs) -> Dict[str, Any]:
    """
    Search tools across ALL platforms by keyword
    
    Includes smart guidance for broad searches:
    - "microsoft" → Shows 182 tools + guidance to narrow to subplatform
    - "google" → Shows 190 tools + guidance to use specific platform
    - "calendar" → Shows calendar tools from Google + Microsoft
    
    Args:
        query: Search term (platform name, action verb, etc.)
    
    Returns:
    {
        "query": "calendar",
        "match_count": 29,
        "tools": [
            {"name": "google_calendar_create_event", "platform": "google_calendar"},
            {"name": "microsoft_calendar_create_event", "platform": "microsoft_calendar"},
            ...
        ],
        "guidance": "Found tools across multiple platforms. Use list_platform_tools() to focus on one."
    }
    """
    
# 5. PLATFORM-SPECIFIC GUIDANCE
def get_platform_guide(platform: str, **kwargs) -> Dict[str, Any]:
    """
    Get comprehensive guide for a platform
    
    Returns:
    - Authentication requirements
    - Available tool categories
    - Common workflows
    - Best practices
    """
    
# 6. TASK-BASED RECOMMENDATIONS
def recommend_tools_for_task(task_description: str, 
                              user_platforms: Optional[List[str]] = None,
                              **kwargs) -> Dict[str, Any]:
    """
    Recommend tools based on natural language task description
    
    Args:
        task_description: "Send an email with attachment"
        user_platforms: ["google_workspace"] (user's connected platforms)
    
    Returns recommended tools with reasoning
    """
    
# 7. WORKFLOW INSTRUCTIONS
def get_workflow_steps(workflow_name: str, **kwargs) -> Dict[str, Any]:
    """
    Get step-by-step tool sequence for complex workflows
    
    Available workflows:
    - "email_campaign" → gmail tools sequence
    - "document_creation" → docs + drive tools
    - "calendar_scheduling" → calendar tools with conflict checking
    """
    
# 8. DYNAMIC TOOL EXECUTION
def execute_tool(tool_name: str, **tool_params) -> Dict[str, Any]:
    """
    Execute ANY tool by name (proxy function)
    
    This allows Claude to call tools after discovering them,
    without needing all 603 tool schemas sent upfront.
    
    Multi-provider compatible (Anthropic + OpenAI formats)
    """
```

### Meta-Tool Usage Flow

**Example: User asks "Create a calendar event for next Monday at 2 PM"**

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: AI Receives User Request                           │
│ "Create a calendar event for next Monday at 2 PM"          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: AI Reasoning (Internal)                            │
│ - Task: Create calendar event                              │
│ - Platform needed: Calendar (Google or Microsoft?)         │
│ - Don't know specific tool yet → Use meta-tool             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: AI Calls search_tools("calendar")                  │
│                                                             │
│ Returns:                                                    │
│ - google_calendar_create_event (Google Calendar)           │
│ - google_calendar_create_recurring_event (Google)          │
│ - microsoft_calendar_create_event (Microsoft Outlook)      │
│ - microsoft_calendar_create_recurring_event (Microsoft)    │
│ - google_tasks_create_task (wrong - tasks not events)      │
│                                                             │
│ Guidance: "Found 29 calendar tools across 2 platforms"     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: AI Narrows to Platform                             │
│ - User likely uses Google Workspace                         │
│ - Calls list_platform_tools("google_calendar")             │
│                                                             │
│ Returns 12 tools:                                           │
│ 1. google_calendar_create_event ✓                          │
│ 2. google_calendar_list_events                             │
│ 3. google_calendar_update_event                            │
│ 4. google_calendar_delete_event                            │
│ ... (8 more)                                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 5: AI Gets Full Schema                                │
│ Calls get_tool_schema("google_calendar_create_event")      │
│                                                             │
│ Returns FULL parameter schema:                             │
│ {                                                           │
│   "parameters": {                                           │
│     "summary": {"type": "string", "required": true},        │
│     "start_time": {"type": "string", "required": true},     │
│     "end_time": {"type": "string", "required": true},       │
│     "attendees": {"type": "array", "required": false},      │
│     "recurrence": {"type": "string", "required": false}     │
│   }                                                         │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 6: AI Executes Tool                                   │
│ google_calendar_create_event(                              │
│   summary="Meeting",                                        │
│   start_time="2025-11-18T14:00:00",                        │
│   end_time="2025-11-18T15:00:00"                           │
│ )                                                           │
│                                                             │
│ Success! Event created with ID: abc123                      │
└─────────────────────────────────────────────────────────────┘
```

**Token Usage Comparison:**

| Approach | Tokens Sent to Claude | Result |
|----------|----------------------|--------|
| **Send All Tools Upfront** | 200,000+ tokens | Overwhelm, wrong tool selection |
| **Meta-Tools (Progressive)** | 5,000 tokens | Correct tool selection |
| **Savings** | 195,000 tokens (97.5% reduction) | ✅ Better accuracy |

---

## Google Workspace: Complete Platform Analysis

### 10 Integrated Platforms

AI_Agents has **complete implementations** for all Google Workspace services:

| # | Platform | Tools | Schema File | Implementation File | Lines of Code |
|---|----------|-------|-------------|---------------------|---------------|
| 1 | **Gmail** | 45 | `gmail_tools.json` (1,847 lines) | `google_workspace/gmail.py` (746 lines) | 2,593 |
| 2 | **Google Docs** | 38 | `google_docs_tools.json` (1,284 lines) | `google_workspace/google_docs.py` (3,583 lines) | 4,867 |
| 3 | **Google Sheets** | 7 | `google_sheets_tools.json` | `google_workspace/google_docs.py` (shared) | Shared |
| 4 | **Google Forms** | 98 | `google_forms_tools.json` (1,156 lines) | `google_workspace/google_forms.py` (3,000+ lines) | 4,156+ |
| 5 | **Google Drive** | 22 | `google_drive_tools.json` | `google_workspace/google_drive.py` (800+ lines) | 800+ |
| 6 | **Google Calendar** | 11 | `google_calendar_tools.json` | `google_workspace/google_calendar.py` (400+ lines) | 400+ |
| 7 | **Google Tasks** | 25 | `google_tasks_tools.json` | `google_workspace/google_tasks.py` (612 lines) | 612 |
| 8 | **Google Slides** | 19 | `google_slides_tools.json` | `google_workspace/google_slides.py` (800+ lines) | 800+ |
| 9 | **Google Meet** | 23 | `google_meet_tools.json` | `google_workspace/google_meet.py` (900+ lines) | 900+ |
| 10 | **Google Analytics** | 19 | `google_analytics_tools.json` | `google_workspace/google_analytics.py` (600+ lines) | 600+ |

**TOTAL:** 307+ Google Workspace tools across 15,728+ lines of code

### Tool Categories Across Platforms

**Email & Communication (68 tools)**
- Gmail: Send, receive, search, labels, filters, attachments
- Meet: Video meetings, recurring meetings, waiting rooms

**Document Creation (65 tools)**
- Docs: Create, format, tables, charts, export (PDF/HTML/Markdown)
- Slides: Presentations, themes, animations, speaker notes
- Forms: Surveys, quizzes, conditional logic, response analysis

**Data & Analytics (26 tools)**
- Sheets: Create, read, write, formulas, charts
- Analytics: GA4 reports, user behavior, conversion tracking

**Organization & Productivity (43 tools)**
- Calendar: Events, recurring events, reminders, availability checking
- Tasks: Task lists, projects, due dates, priorities
- Drive: File management, folders, sharing, permissions

**Platform Services (5 tools)**
- Auth: Service account credentials, OAuth token management
- Cloud Run: Serverless deployment (bonus feature)

### Naming Convention: `google_[platform]_[action]`

**Pattern Examples:**

```python
# Gmail (special case - uses "gmail_" not "google_gmail_")
gmail_send_email(to, subject, body, attachments)
gmail_list_messages(query="is:unread", max_results=10)
gmail_search_messages(query="from:boss@company.com")
gmail_create_label(name="Important Clients")

# Google Docs
google_docs_create_document(title="Q4 Report")
google_docs_smart_create_from_markdown(title, markdown_content)
google_docs_insert_table(document_id, rows=5, columns=3)
google_docs_export_as_pdf(document_id, output_path)

# Google Sheets
google_sheets_create(title="Sales Data", headers=["Product", "Revenue"])
google_sheets_read_data(spreadsheet_id, range_name="Sheet1!A1:D10")
google_sheets_format_cells(spreadsheet_id, range_name, bold=True, color="#FF0000")

# Google Forms
google_forms_create_form(title="Customer Survey")
google_forms_add_question(form_id, "What's your email?", type="short_answer")
google_forms_get_responses(form_id)

# Google Calendar
google_calendar_create_event(summary="Team Meeting", start_time="2025-11-18T14:00:00")
google_calendar_create_recurring_event(summary="Weekly Standup", recurrence="FREQ=WEEKLY;BYDAY=MO")
google_calendar_check_availability(calendar_id, start_time, end_time)

# Google Drive
google_drive_upload_file(file_path, folder_id=None)
google_drive_create_folder(name="Project Files")
google_drive_share_file(file_id, email="colleague@company.com", role="writer")

# Google Tasks
google_tasks_create_task(title="Review proposal", due_date="2025-11-20")
google_tasks_smart_create_project(project_name="Q4 Launch", tasks_list=[...])
google_tasks_smart_organize_by_priority(task_list_id)

# Google Slides
google_slides_create_presentation(title="Pitch Deck")
google_slides_add_slide(presentation_id, layout="TITLE_AND_BODY")
google_slides_insert_image(presentation_id, slide_index, image_url)

# Google Meet
google_meet_create_meeting(summary="Quarterly Review", start_time="...")
google_meet_create_recurring_meeting(summary="Daily Standup", recurrence="DAILY")

# Google Analytics
google_analytics_get_realtime_report(property_id)
google_analytics_get_page_views(property_id, start_date, end_date)
google_analytics_get_conversions(property_id, metric_names=["conversions", "revenue"])
```

### Google-Specific Features

**1. Service Account Authentication**

**File:** `google_workspace/google_auth_helper.py` (12 functions)

```python
def build_gmail_service(_user_id=None, _injected_credentials=None):
    """Build Gmail API service with automatic credential injection"""
    if _injected_credentials:
        # Use user's OAuth tokens from database
        return build('gmail', 'v1', credentials=_injected_credentials)
    else:
        # Use service account (for system-level operations)
        credentials = get_service_account_credentials([
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.readonly',
        ])
        return build('gmail', 'v1', credentials=credentials)

# Similar builders for:
build_docs_service()        # Google Docs API v1
build_drive_service()       # Google Drive API v3
build_calendar_service()    # Google Calendar API v3
build_forms_service()       # Google Forms API v1
build_sheets_service()      # Google Sheets API v4
build_tasks_service()       # Google Tasks API v1
build_slides_service()      # Google Slides API v1
build_meet_service()        # Google Meet API v2
build_analytics_service()   # Google Analytics API v4
```

**2. SMART Bundled Tools**

Complex operations that normally require 5-10 API calls → 1 tool call

```python
# Example: Create complete form with questions and settings
google_forms_create_complete_form(
    title="Customer Feedback Survey",
    description="Help us improve!",
    questions=[
        {"text": "What's your email?", "type": "short_answer", "required": True},
        {"text": "Rate our service (1-5)", "type": "scale", "required": True},
        {"text": "Any suggestions?", "type": "paragraph", "required": False}
    ],
    settings={
        "allow_response_edits": True,
        "require_login": False,
        "confirmation_message": "Thanks for your feedback!"
    }
)
# Result: Form created, questions added, settings configured, shareable link returned
# Normally: 6 separate API calls → Now: 1 tool call
```

**More SMART Tools:**

- `gmail_smart_compose_and_send()` - AI drafts email + sends
- `google_docs_smart_create_from_markdown()` - Markdown → formatted Doc
- `google_tasks_smart_create_project()` - Creates task list + all subtasks
- `google_sheets_ai_generate_table()` - AI generates spreadsheet structure
- `google_calendar_smart_find_meeting_time()` - Checks availability across attendees

**3. Credential Injection Pattern**

Every Google tool accepts these hidden parameters:

```python
def google_calendar_create_event(
    summary,
    start_time,
    end_time,
    attendees=None,
    _user_id=None,              # Hidden - injected by system
    _injected_credentials=None,  # Hidden - OAuth tokens from DB
    **kwargs
):
    """
    Create calendar event
    
    _user_id: Database user ID (automatically injected)
    _injected_credentials: OAuth Credentials object (automatically injected)
    
    If both are provided, tool uses USER'S Google Calendar (not service account)
    """
    service = build_calendar_service(_user_id, _injected_credentials)
    # ... rest of implementation
```

**How It Works:**

```
User Request: "Create a calendar event"
     ↓
Agent calls: google_calendar_create_event(summary="Meeting", ...)
     ↓
ToolExecutor intercepts call
     ↓
ToolExecutor injects: _user_id=42, _injected_credentials=<Credentials object>
     ↓
Tool executes with USER's credentials
     ↓
Event created in USER's personal Google Calendar (not system calendar)
```

### Google OAuth Scopes

**Scopes Required for 307 Tools:**

```python
GOOGLE_WORKSPACE_SCOPES = [
    # Gmail (45 tools)
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels',
    
    # Google Drive (22 tools)
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    
    # Google Docs (38 tools)
    'https://www.googleapis.com/auth/documents',
    
    # Google Sheets (7 tools)
    'https://www.googleapis.com/auth/spreadsheets',
    
    # Google Forms (98 tools)
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/forms.responses.readonly',
    
    # Google Calendar (11 tools)
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    
    # Google Tasks (25 tools)
    'https://www.googleapis.com/auth/tasks',
    
    # Google Slides (19 tools)
    'https://www.googleapis.com/auth/presentations',
    
    # Google Meet (23 tools)
    'https://www.googleapis.com/auth/meetings.space.created',
    
    # Google Analytics (19 tools)
    'https://www.googleapis.com/auth/analytics.readonly',
]
```

**OAuth Flow:**

```
User clicks "Connect Google Calendar"
     ↓
Redirected to Google OAuth consent screen
     ↓
User grants permission to access Calendar
     ↓
Google returns access_token + refresh_token
     ↓
Tokens stored in database (oauth_tokens table)
     ↓
Future tool calls auto-inject these tokens
     ↓
Tokens auto-refresh when expired
```

---

## AI Tool Selection Workflow

### System Prompt Design

**File:** `AI_infrastructure/prompts/tool_usage_system_prompt_v3_COMPACT.md` (1,200+ lines)

```markdown
# AI Agent System Instructions v3.0

You have **607 tools** across 20+ platforms. Discover them systematically:

## **THREE-METHOD TOOL DISCOVERY SYSTEM**

### **METHOD 1: list_platform_tools(platform)**
Returns list of tool NAMES + descriptions (no parameter schemas)

list_platform_tools("google_calendar")    # 12 Calendar tools
list_platform_tools("microsoft_outlook")  # 23 Outlook tools

**When to use:** You know the platform, need to see available tools

### **METHOD 2: search_tools(query)**
Returns matching tool NAMES + descriptions (exact matching, no fuzzy)

search_tools("send_email")               # Email tools
search_tools("create_calendar_event")    # Calendar tools

**When to use:** Don't know exact platform, but know the action

### **METHOD 3: get_tool_schema(tool_name)**
**CRITICAL STEP!** Returns FULL Anthropic schema with all parameters

get_tool_schema("gmail_send_email")
→ Returns parameters: to, subject, body, cc, bcc, attachments (with types & requirements)

**When to use:** Found a tool via Method 1 or 2, now need to execute it

---

## **QUICK DECISION TREE**

**User asks to do something...**

1. **Do you know a tool that does this?**
   - YES → Use it with `function_calls`
   - NO → Go to step 2

2. **Can you discover the tool?**
   - YES → Use `list_platform_tools()` or `search_tools()`
   - NO → Tell user exactly why you can't (no platform, no tool exists)

3. **Do you have the tool's schema?**
   - YES → Execute tool with correct parameters
   - NO → Use `get_tool_schema(tool_name)` first

4. **Before executing - Does this need confirmation?**
   - Expensive (>10k tokens, >$0.03) → Call `request_user_confirmation()` FIRST
   - Destructive (delete, modify) → Call `request_user_confirmation()` FIRST
   - Multiple approaches possible → Call `request_user_choice()` to let user decide
   - Otherwise → Execute immediately
```

### AI Reasoning Examples

**Example 1: Simple Calendar Event**

```
User: "Create a calendar event for tomorrow at 2 PM"

Claude's Internal Reasoning:
1. Task: Create calendar event
2. Platform: Likely Google Calendar (common platform)
3. Don't know exact tool → Use meta-tool
4. Call search_tools("calendar event") → Returns 29 tools
5. Too many! Narrow to platform → Call list_platform_tools("google_calendar")
6. Returns 12 tools, I see "google_calendar_create_event" ✓
7. Get schema → Call get_tool_schema("google_calendar_create_event")
8. Now I know required parameters: summary, start_time, end_time
9. Execute tool:
   google_calendar_create_event(
     summary="Meeting",
     start_time="2025-11-16T14:00:00",
     end_time="2025-11-16T15:00:00"
   )
10. Success! Return result to user
```

**Example 2: Complex Workflow (Document + Share)**

```
User: "Create a project proposal document and share it with my team"

Claude's Internal Reasoning:
1. Task: Two steps (create doc + share)
2. Platform: Google Docs (for document) + Google Drive (for sharing)
3. Step 1 - Create Doc:
   - Call list_platform_tools("google_docs")
   - Find "google_docs_create_document"
   - Call get_tool_schema("google_docs_create_document")
   - Execute: google_docs_create_document(title="Project Proposal")
   - Result: document_id = "abc123"
4. Step 2 - Share Doc:
   - Call list_platform_tools("google_drive")
   - Find "google_drive_share_file"
   - Call get_tool_schema("google_drive_share_file")
   - Execute: google_drive_share_file(file_id="abc123", email="team@company.com", role="writer")
5. Success! Both operations complete
```

**Example 3: Platform Ambiguity**

```
User: "Send me a meeting invite"

Claude's Internal Reasoning:
1. Task: Send meeting invite
2. Platform: Ambiguous! Could be:
   - Google Calendar (create event + send invite)
   - Microsoft Outlook (send calendar invite)
   - Gmail (send email with invite)
3. Use cross-platform search → Call search_tools("meeting invite")
4. Returns:
   - google_calendar_create_event (with attendees parameter)
   - microsoft_calendar_send_meeting_invitation
   - gmail_send_email (generic email)
5. Ask user: "Would you prefer to use Google Calendar or Microsoft Outlook for the meeting invite?"
6. User: "Google Calendar"
7. Proceed with google_calendar_create_event
```

### Tool Selection Priorities

**AI follows this priority order:**

```
Priority 1: SMART Tools (complex operations)
    ↓ (if no SMART tool exists)
Priority 2: Basic Tools (single operations)
    ↓ (if unsure which tool)
Priority 3: Meta-Tools (discover tools)
    ↓ (if tool doesn't exist)
Priority 4: Ask User (clarify or explain limitation)
```

**Example:**

```
User: "Create a comprehensive customer survey"

AI Reasoning:
1. Check for SMART tool:
   - google_forms_create_complete_form ✓ (creates form + questions + settings)
   - USE THIS! (saves 6+ API calls)

Alternative (if no SMART tool):
2. Use basic tools sequentially:
   - google_forms_create_form(title="Survey")
   - google_forms_add_question(...)
   - google_forms_add_question(...)
   - google_forms_add_question(...)
   - google_forms_update_settings(...)
   - google_forms_get_shareable_link(...)
```

---

## Credential Injection System

### Purpose: Per-User Tool Execution

**Problem:** How do tools know WHICH user's account to use?

**Bad Solution:** Service accounts (all users share one account)
- ❌ Privacy violation (all data in one account)
- ❌ Permission issues (can't access user's private calendars)
- ❌ No personalization (can't use user's Gmail labels, task lists, etc.)

**AI_Agents Solution:** Credential Injection

```
User 1 calls tool → Uses User 1's OAuth tokens → Accesses User 1's calendar
User 2 calls tool → Uses User 2's OAuth tokens → Accesses User 2's calendar
```

### Architecture

**File:** `AI_infrastructure/auth/credential_injector.py` (750+ lines)

```python
class CredentialInjector:
    """
    Injects user-specific OAuth credentials into tool calls
    
    This allows same tool code to work for ANY user by dynamically
    swapping credentials at runtime.
    """
    
    def inject_credentials_into_tool(self, tool_name: str, parameters: Dict, user_id: int):
        """
        Modify tool parameters to include user's OAuth credentials
        
        Args:
            tool_name: "google_calendar_create_event"
            parameters: {"summary": "Meeting", "start_time": "..."}
            user_id: 42 (database user ID)
        
        Returns:
            Modified parameters with injected credentials:
            {
                "summary": "Meeting",
                "start_time": "...",
                "_user_id": 42,
                "_injected_credentials": <Credentials object>
            }
        """
        # Get user's OAuth tokens from database
        token_record = self.db.query(OAuthToken).filter_by(
            user_id=user_id,
            platform='google'  # or 'microsoft' based on tool
        ).first()
        
        if not token_record:
            raise AuthenticationError("User has not connected Google account")
        
        # Check if token expired
        if token_record.token_expiry < datetime.now():
            # Auto-refresh token
            new_tokens = self._refresh_oauth_token(token_record.refresh_token)
            token_record.access_token = new_tokens['access_token']
            token_record.token_expiry = new_tokens['expires_at']
            self.db.commit()
        
        # Create Credentials object
        credentials = Credentials(
            token=token_record.access_token,
            refresh_token=token_record.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET')
        )
        
        # Inject into parameters
        parameters['_user_id'] = user_id
        parameters['_injected_credentials'] = credentials
        
        return parameters
```

### Database Schema

**Table:** `oauth_tokens`

```sql
CREATE TABLE oauth_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('google', 'microsoft')),
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_expiry TIMESTAMP WITH TIME ZONE,
    scope TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, platform)
);

CREATE INDEX idx_oauth_tokens_user ON oauth_tokens(user_id);
CREATE INDEX idx_oauth_tokens_platform ON oauth_tokens(user_id, platform);
```

**Example Records:**

```
id | user_id | platform  | access_token           | refresh_token          | token_expiry
---+---------+-----------+------------------------+------------------------+-------------------------
1  | 42      | google    | ya29.a0AfH6SMB...      | 1//0gZq3Zx...          | 2025-11-15 15:30:00
2  | 42      | microsoft | EwBgA8l6BAAUO9...      | M.R3_BAY.-CYj...       | 2025-11-15 16:00:00
3  | 99      | google    | ya29.a0AfH6SMC...      | 1//0gZq3Zy...          | 2025-11-15 14:45:00
```

### OAuth Routes

**Google OAuth:**

```python
# File: AI_infrastructure/routes/google_auth_routes_V2_FIXED.py

@auth_bp.route('/api/auth/google/calendar/login')
def google_oauth_login():
    """Initiate Google OAuth flow"""
    authorization_url = (
        'https://accounts.google.com/o/oauth2/v2/auth?'
        f'client_id={GOOGLE_CLIENT_ID}&'
        f'redirect_uri={GOOGLE_REDIRECT_URI}&'
        'response_type=code&'
        'scope=https://www.googleapis.com/auth/calendar%20'
              'https://www.googleapis.com/auth/gmail.send%20'
              'https://www.googleapis.com/auth/drive&'
        'access_type=offline&'
        'prompt=consent'
    )
    return redirect(authorization_url)

@auth_bp.route('/api/auth/google/callback')
def google_oauth_callback():
    """Handle Google OAuth callback"""
    code = request.args.get('code')
    
    # Exchange code for tokens
    response = requests.post('https://oauth2.googleapis.com/token', data={
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code'
    })
    
    tokens = response.json()
    
    # Save to database
    oauth_token = OAuthToken(
        user_id=current_user.id,
        platform='google',
        access_token=tokens['access_token'],
        refresh_token=tokens.get('refresh_token'),
        token_expiry=datetime.now() + timedelta(seconds=tokens['expires_in']),
        scope=tokens.get('scope')
    )
    db.session.add(oauth_token)
    db.session.commit()
    
    return redirect('/dashboard?oauth=success')
```

**Microsoft OAuth:** (Similar pattern in `microsoft_auth_routes_V2_FIXED.py`)

### Auto-Refresh Logic

```python
def _refresh_oauth_token(self, refresh_token: str, platform: str) -> Dict:
    """
    Automatically refresh expired OAuth token
    
    Called transparently when access token expires.
    User doesn't need to re-authenticate.
    """
    if platform == 'google':
        response = requests.post('https://oauth2.googleapis.com/token', data={
            'refresh_token': refresh_token,
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'grant_type': 'refresh_token'
        })
    elif platform == 'microsoft':
        response = requests.post('https://login.microsoftonline.com/common/oauth2/v2.0/token', data={
            'refresh_token': refresh_token,
            'client_id': os.getenv('MICROSOFT_CLIENT_ID'),
            'client_secret': os.getenv('MICROSOFT_CLIENT_SECRET'),
            'grant_type': 'refresh_token'
        })
    
    tokens = response.json()
    
    return {
        'access_token': tokens['access_token'],
        'expires_at': datetime.now() + timedelta(seconds=tokens['expires_in'])
    }
```

---

## Implementation Patterns

### Pattern 1: Schema-First Development

**Process:**

```
1. Design JSON schema (defines interface)
   ↓
2. Write implementation (fulfills interface)
   ↓
3. Registry auto-loads both
   ↓
4. AI can discover and use tool
```

**Example:**

**Step 1: Create Schema** (`tools/schemas/google_calendar_tools.json`)

```json
{
  "platform": "google_calendar",
  "tools": [
    {
      "name": "google_calendar_create_event",
      "description": "Create a new calendar event with title, date, time, and optional attendees",
      "parameters": {
        "summary": {
          "type": "string",
          "description": "Event title",
          "required": true
        },
        "start_time": {
          "type": "string",
          "description": "Start time (ISO 8601 format)",
          "required": true
        },
        "end_time": {
          "type": "string",
          "description": "End time (ISO 8601 format)",
          "required": true
        }
      }
    }
  ]
}
```

**Step 2: Write Implementation** (`google_workspace/google_calendar.py`)

```python
def google_calendar_create_event(
    summary,
    start_time,
    end_time,
    attendees=None,
    _user_id=None,
    _injected_credentials=None,
    **kwargs
):
    """Create calendar event (implementation matches schema)"""
    service = build_calendar_service(_user_id, _injected_credentials)
    
    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'UTC'},
        'end': {'dateTime': end_time, 'timeZone': 'UTC'},
    }
    
    if attendees:
        event['attendees'] = [{'email': email} for email in attendees]
    
    result = service.events().insert(calendarId='primary', body=event).execute()
    
    return {
        'event_id': result['id'],
        'html_link': result.get('htmlLink'),
        'status': result.get('status')
    }
```

**Step 3: Registry Auto-Loads**

```python
# Registry initialization
registry = RegistryV3()
# ✅ Loaded schema: google_calendar_create_event
# ✅ Loaded implementation: google_calendar.py → google_calendar_create_event()

# AI can now discover it
tools = registry.list_tools_by_platform('google_calendar')
# Returns: [{'name': 'google_calendar_create_event', ...}]
```

### Pattern 2: Module-Based Organization

```
google_workspace/
├── gmail.py                   # Email functions (45 tools)
│   ├── gmail_send_email()
│   ├── gmail_list_messages()
│   ├── gmail_search_messages()
│   └── ...
│
├── google_calendar.py         # Calendar functions (11 tools)
│   ├── google_calendar_create_event()
│   ├── google_calendar_list_events()
│   └── ...
│
├── google_docs.py             # Document functions (38 tools)
│   ├── google_docs_create_document()
│   ├── google_docs_insert_text()
│   └── ...
│
└── google_auth_helper.py      # Shared authentication
    ├── build_gmail_service()
    ├── build_calendar_service()
    └── ...
```

**Benefits:**
- Clear separation of concerns
- Easy to find implementation
- Shared auth logic (no duplication)
- Each module is self-contained

### Pattern 3: Error Handling & Validation

**Every tool follows this pattern:**

```python
def google_calendar_create_event(summary, start_time, end_time, **kwargs):
    """Create calendar event with comprehensive error handling"""
    
    # 1. PARAMETER VALIDATION
    if not summary:
        return {"success": False, "error": "summary is required"}
    
    try:
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
    except ValueError as e:
        return {"success": False, "error": f"Invalid datetime format: {str(e)}"}
    
    if end_dt <= start_dt:
        return {"success": False, "error": "end_time must be after start_time"}
    
    # 2. AUTHENTICATION
    try:
        service = build_calendar_service(
            kwargs.get('_user_id'),
            kwargs.get('_injected_credentials')
        )
    except Exception as e:
        return {"success": False, "error": f"Authentication failed: {str(e)}"}
    
    # 3. API CALL
    try:
        event = {
            'summary': summary,
            'start': {'dateTime': start_time, 'timeZone': 'UTC'},
            'end': {'dateTime': end_time, 'timeZone': 'UTC'},
        }
        
        result = service.events().insert(
            calendarId='primary',
            body=event
        ).execute()
        
        # 4. SUCCESS RESPONSE
        return {
            "success": True,
            "event_id": result['id'],
            "html_link": result.get('htmlLink'),
            "status": result.get('status')
        }
        
    except HttpError as e:
        # 5. API ERROR HANDLING
        error_details = e.error_details[0] if e.error_details else {}
        return {
            "success": False,
            "error": f"Google Calendar API error: {error_details.get('message', str(e))}",
            "error_code": e.resp.status
        }
    except Exception as e:
        # 6. UNEXPECTED ERROR
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }
```

### Pattern 4: Return Value Standardization

**All tools return this structure:**

```python
# SUCCESS
{
    "success": True,
    "result_field_1": "...",
    "result_field_2": "...",
    ...
}

# ERROR
{
    "success": False,
    "error": "Human-readable error message",
    "error_code": "OPTIONAL_ERROR_CODE"
}
```

**Benefits:**
- AI can reliably check `success` field
- Consistent error handling across all tools
- Easy to debug (clear error messages)

---

## Integration with Health_app

### Medication Reminder Implementation (Using AI_Agents Patterns)

**Step 1: Copy Calendar Files**

```powershell
# Copy Google Calendar implementation
Copy-Item "C:\Users\gpoli\GIT\AI_agents\google_workspace\google_calendar.py" `
          "C:\Users\gpoli\GIT\Health_app\app\integrations\google_calendar.py"

# Copy Microsoft Calendar implementation
Copy-Item "C:\Users\gpoli\GIT\AI_agents\tools\implementations\microsoft_calendar_tools.py" `
          "C:\Users\gpoli\GIT\Health_app\app\integrations\microsoft_calendar.py"

# Copy credential injector
Copy-Item "C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\auth\credential_injector.py" `
          "C:\Users\gpoli\GIT\Health_app\app\auth\credential_injector.py"
```

**Step 2: Create Tool Registry (Simplified for Health_app)**

```python
# File: app/services/tool_registry.py

class HealthToolRegistry:
    """
    Simplified tool registry for Health_app
    Only loads health-related tools (no 584-tool overwhelm!)
    """
    
    def __init__(self):
        self.tools = {}
        self._load_health_tools()
    
    def _load_health_tools(self):
        """Load only medication reminder tools"""
        from app.integrations.google_calendar import (
            google_calendar_create_event,
            google_calendar_create_recurring_event,
            google_calendar_delete_event
        )
        from app.integrations.microsoft_calendar import (
            microsoft_calendar_create_event,
            microsoft_calendar_create_recurring_event,
            microsoft_calendar_delete_event
        )
        
        self.tools = {
            'google_calendar_create_event': google_calendar_create_event,
            'google_calendar_create_recurring_event': google_calendar_create_recurring_event,
            'microsoft_calendar_create_event': microsoft_calendar_create_event,
            'microsoft_calendar_create_recurring_event': microsoft_calendar_create_recurring_event,
        }
    
    def execute_tool(self, tool_name, user_id, **params):
        """Execute tool with automatic credential injection"""
        from app.auth.credential_injector import inject_credentials
        
        # Inject user's OAuth credentials
        params = inject_credentials(user_id, tool_name, params)
        
        # Execute tool
        tool_func = self.tools[tool_name]
        return tool_func(**params)
```

**Step 3: Create Calendar Service Wrapper**

```python
# File: app/services/calendar_service.py

class CalendarService:
    """
    High-level calendar service for medication reminders
    Uses AI_Agents pattern: tool registry + credential injection
    """
    
    def __init__(self):
        self.registry = HealthToolRegistry()
    
    def create_medication_reminder(
        self,
        user_id: int,
        medication_name: str,
        dosage: str,
        time: str,
        frequency: str = 'daily'
    ):
        """
        Create recurring calendar reminder for medication
        
        Args:
            user_id: Database user ID
            medication_name: "Gabapentin"
            dosage: "300mg"
            time: "08:00"  # 8 AM
            frequency: "daily", "twice_daily", "weekly"
        
        Uses AI_Agents patterns:
        1. Tool registry for calendar API abstraction
        2. Credential injection for per-user OAuth
        3. Recurrence patterns from AI_Agents
        """
        # Determine user's calendar platform
        user = User.query.get(user_id)
        calendar_platform = user.calendar_platform  # 'google' or 'microsoft'
        
        # Build event details
        summary = f"💊 {medication_name} - {dosage}"
        description = (
            f"Medication Reminder\n"
            f"Medication: {medication_name}\n"
            f"Dosage: {dosage}\n"
            f"Time: {time}\n"
            f"\n"
            f"Log your medication after taking it in the FND/PTSD Companion app."
        )
        
        # Calculate start/end times
        now = datetime.now()
        reminder_time = datetime.strptime(time, "%H:%M").time()
        start_datetime = datetime.combine(now.date(), reminder_time)
        end_datetime = start_datetime + timedelta(minutes=15)  # 15-min reminder window
        
        # Build recurrence rule (AI_Agents pattern)
        recurrence_rules = {
            'daily': 'FREQ=DAILY',
            'twice_daily': 'FREQ=DAILY;INTERVAL=12',  # Every 12 hours
            'weekly': 'FREQ=WEEKLY',
            'as_needed': None  # No recurrence
        }
        recurrence = recurrence_rules.get(frequency)
        
        # Select tool based on platform
        if calendar_platform == 'google':
            tool_name = 'google_calendar_create_recurring_event'
        elif calendar_platform == 'microsoft':
            tool_name = 'microsoft_calendar_create_recurring_event'
        else:
            raise ValueError(f"Unknown calendar platform: {calendar_platform}")
        
        # Execute tool via registry (with auto credential injection)
        result = self.registry.execute_tool(
            tool_name=tool_name,
            user_id=user_id,
            summary=summary,
            start_time=start_datetime.isoformat(),
            end_time=end_datetime.isoformat(),
            description=description,
            recurrence=recurrence,
            reminders=[
                {'method': 'popup', 'minutes': 15},  # 15 min before
                {'method': 'notification', 'minutes': 15}  # Phone notification
            ]
        )
        
        if result['success']:
            # Save event ID to database for future deletion
            self._save_medication_reminder_mapping(
                user_id=user_id,
                medication_name=medication_name,
                calendar_event_id=result['event_id'],
                platform=calendar_platform
            )
        
        return result
```

**Step 4: Integrate with Medication Logging UI**

```python
# File: app/ui/screens/medication_log.py

def medication_log_screen(user_id):
    """Medication logging screen with calendar integration"""
    
    with gr.Column():
        gr.Markdown("## 💊 Log Medication")
        
        medication_name = gr.Textbox(label="Medication Name", placeholder="e.g., Gabapentin")
        dosage = gr.Textbox(label="Dosage", placeholder="e.g., 300mg")
        time_taken = gr.Textbox(label="Time Taken", value=datetime.now().strftime("%H:%M"))
        
        # Calendar reminder toggle
        enable_reminders = gr.Checkbox(
            label="Enable calendar reminders for this medication",
            value=False
        )
        
        reminder_frequency = gr.Dropdown(
            label="Reminder Frequency",
            choices=["daily", "twice_daily", "weekly", "as_needed"],
            value="daily",
            visible=False
        )
        
        submit_btn = gr.Button("Log Medication", variant="primary")
        status_msg = gr.Textbox(label="Status", interactive=False)
        
        # Show/hide frequency selector based on checkbox
        enable_reminders.change(
            fn=lambda checked: gr.update(visible=checked),
            inputs=[enable_reminders],
            outputs=[reminder_frequency]
        )
        
        def log_medication_with_reminder(med_name, dose, time, enable_calendar, frequency):
            """Log medication and optionally create calendar reminder"""
            
            # Save to database
            medication_log = MedicationLog(
                user_id=user_id,
                medication_name=med_name,
                dosage=dose,
                time_taken=time,
                logged_at=datetime.now()
            )
            db.session.add(medication_log)
            db.session.commit()
            
            status = f"✅ Logged {med_name} {dose} at {time}"
            
            # Create calendar reminder if enabled
            if enable_calendar:
                try:
                    calendar_service = CalendarService()
                    result = calendar_service.create_medication_reminder(
                        user_id=user_id,
                        medication_name=med_name,
                        dosage=dose,
                        time=time,
                        frequency=frequency
                    )
                    
                    if result['success']:
                        status += f"\n✅ Calendar reminders created in your calendar"
                    else:
                        status += f"\n⚠️ Calendar reminder failed: {result['error']}"
                        
                except Exception as e:
                    status += f"\n⚠️ Calendar reminder error: {str(e)}"
            
            return status
        
        submit_btn.click(
            fn=log_medication_with_reminder,
            inputs=[medication_name, dosage, time_taken, enable_reminders, reminder_frequency],
            outputs=[status_msg]
        )
```

---

## Summary

The AI_Agents tool architecture demonstrates **enterprise-scale AI tool management** through:

1. **Progressive Discovery:** Meta-tools enable AI to navigate 600+ tools without token overflow
2. **Schema-First Design:** JSON schemas define contracts, implementations fulfill them
3. **Credential Injection:** Per-user OAuth enables personal data access (not shared service accounts)
4. **Modular Organization:** Platform-based file structure (google_workspace/, microsoft_365/, etc.)
5. **Google Workspace Mastery:** 307+ tools across 10 platforms with SMART bundled operations
6. **AI-Friendly Patterns:** Consistent naming, error handling, return values

**For Health_app Integration:**
- Copy 5-10 calendar files (not all 584 tools)
- Adapt credential injection for Health_app's authentication
- Use calendar service wrapper to abstract platform differences
- Enable native phone notifications via calendar API (better than in-app notifications)

**Key Takeaway:** AI_Agents solved the "600-tool problem" through **intelligent tiering** - AI discovers tools progressively rather than receiving everything upfront.

---

**Document Version:** 1.0  
**Last Updated:** November 15, 2025  
**Next Steps:** See `CALENDAR_INTEGRATION_PLAN.md` for Health_app implementation roadmap
