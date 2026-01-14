# 🔧 Tool Catalog System - Complete Documentation

## Overview

Your AI agent has access to **296+ tools across 20+ platforms** with a sophisticated two-tier discovery system.

---

## How Tools Are Provided to the AI

### ✅ 1. System Prompt Instructions

The AI receives comprehensive instructions in the system prompt including:

```
**TOOL DISCOVERY SYSTEM:**
When you need tools from a specific platform, use the `list_platform_tools` meta-tool FIRST to load them.

Available platforms include:
🛒 **E-commerce:** woocommerce (29 tools), stripe (25 tools)
📧 **Communication:** gmail (29 tools), slack (24 tools), twilio (16 tools)
📊 **Google Workspace:** google_docs (19 tools), google_drive (15 tools), google_sheets (4 tools), 
                         google_forms (15 tools), google_calendar (12 tools), google_analytics (12 tools)
☁️ **Cloud:** google_cloud_run (15 tools), cloudflare (4 tools)
💾 **Database:** supabase (25 tools)
💰 **Payments:** paypal (16 tools)
📱 **Social:** instagram (20 tools)
🔧 **Dev Tools:** github (4 tools), ngrok (4 tools)
🔄 **Media:** cloudconvert (4 tools), assemblyai (4 tools)
```

### ✅ 2. Pre-Loaded Priority Tools (50 tools)

Most commonly used platforms are automatically loaded:
- slack, gmail, woocommerce, google_sheets, stripe
- google_cloud_run, google_docs, google_drive, google_forms

### ✅ 3. Discovery Meta-Tool

The AI can discover and load additional tools on-demand:

```json
{
  "name": "list_platform_tools",
  "description": "Discover available platforms and their tools. Use this FIRST to see what platforms are available.",
  "input_schema": {
    "type": "object",
    "properties": {
      "platforms": {
        "type": "array",
        "description": "Platform names to get tools for. Available: slack, gmail, woocommerce, ...",
        "items": {"type": "string"}
      }
    }
  }
}
```

### ✅ 4. Tool Schemas with Rich Descriptions

Each tool includes:
- **Name** - Unique identifier
- **Description** - Detailed explanation with examples
- **Platform** - Which service it connects to
- **Parameters** - Each parameter has type, description, required flag, examples
- **Returns** - What the tool returns

**Example from `google_docs_tools.json`:**

```json
{
  "name": "google_docs_smart_create_from_markdown",
  "description": "🤖 SMART TOOL: Create a fully formatted Google Doc from markdown in ONE CALL. Supports ALL formatting: headings (# to ######), colored headings (## Title {#1a73e8}), **bold**, *italic*, ~~strikethrough~~, ==highlight==, `inline code`, ```code blocks```, [links](url), ![images](url), - nested bullets (2 spaces = 1 level), 1. nested numbers, > blockquotes, --- horizontal lines, <<NEW-PAGE>>, and | tables | with | content |",
  "platform": "google_docs",
  "parameters": {
    "title": {
      "type": "string",
      "description": "Document title",
      "required": true
    },
    "markdown_content": {
      "type": "string",
      "description": "Full markdown content with ALL features: # headings (H1-H6), colored headings (## Title {#hexcode}), **bold**, *italic*, ~~strikethrough~~, ==highlight==, `code`, ```blocks```, [text](url) links, ![alt](url) images, nested lists (indent with 2 spaces), > blockquotes, --- lines, <<NEW-PAGE>>, | tables |",
      "required": true
    }
  }
}
```

---

## Current System Strengths

### ✅ EXCELLENT Coverage

1. **Inline Examples** - Parameter descriptions include examples:
   ```
   "data": "2D array of data rows. Example: [['Alice', 100], ['Bob', 200]]"
   ```

2. **SMART Tool Annotations** - Special tools are clearly marked:
   ```
   "🤖 SMART TOOL: Create a fully formatted Google Doc from markdown in ONE CALL"
   ```

3. **Usage Patterns** - Descriptions explain when to use:
   ```
   "Use this instead of multiple separate tools (insert_text, format_text, etc.)"
   ```

4. **Supported Features** - Lists ALL capabilities:
   ```
   "Supports: # headings, **bold**, *italic*, [links](url), | tables |, ..."
   ```

---

## Areas for Improvement

### ❌ 1. No Separate Documentation Catalog

**Issue:** AI relies on inline descriptions only. There's no comprehensive catalog document showing:
- ✅ Best practices for each platform
- ✅ Complete workflow examples
- ✅ Common pitfalls and solutions
- ✅ Multi-tool orchestration patterns

**Recommendation:** Create platform-specific guide documents (see below)

### ❌ 2. Multi-Platform Tools Need Context

**Issue:** Tools like `google_docs_smart_create_from_markdown` work across multiple Google services but lack cross-platform workflow examples.

**Recommendation:** Add workflow diagrams showing tool combinations

### ❌ 3. No Error Recovery Examples

**Issue:** Descriptions don't show what to do when a tool fails.

**Example Missing:**
```
If google_docs_smart_create_from_markdown fails with permissions error:
1. Try google_docs_create_document (basic creation)
2. Use google_docs_share to set permissions
3. Then retry formatting with google_docs_smart_update
```

---

## Recommended Enhancements

### 📚 1. Create Platform Guide Documents

For each major platform, create a guide in `tools/guides/`:

**Example: `tools/guides/google_docs_guide.md`**

```markdown
# Google Docs Platform Guide

## Tool Hierarchy (Use in This Order)

### TIER 1: Smart Tools (Always Try First)
1. **google_docs_smart_create_from_markdown** - Creates fully formatted doc in 1 call
2. **google_docs_smart_update** - Adds content to existing docs efficiently
3. **google_docs_smart_generate** - AI-powered document generation

### TIER 2: Basic Tools (Fallback)
- google_docs_create_document - Basic document creation
- google_docs_insert_text - Add plain text
- google_docs_format_text - Apply formatting

### TIER 3: Advanced Tools (Special Cases)
- google_docs_insert_table - Complex table operations
- google_docs_insert_image - Image embedding
- google_docs_create_doc_with_charts - Reports with embedded charts

## Common Workflows

### Workflow 1: Create Formatted Report
```
Step 1: Use google_docs_smart_create_from_markdown
Input:
  title: "Q4 Financial Report"
  markdown_content: "# Executive Summary\n\n**Revenue:** $2.5M\n\n## Details..."
  
Step 2: Share document
Input:
  document_id: <from step 1>
  share_with: "team@company.com"
```

### Workflow 2: Update Existing Document
```
Step 1: Get current content
  google_docs_get_document(document_id)
  
Step 2: Append new section
  google_docs_smart_update(
    document_id: <id>,
    markdown_content: "## New Section...",
    insertion_position: "end"
  )
```

## Error Recovery Patterns

### Permission Denied
If you get "Permission denied" error:
1. Check if document exists: google_docs_get_document
2. Verify sharing settings
3. Try creating in user's Drive root instead of shared folder

### Formatting Failed
If formatting doesn't apply:
1. Verify markdown syntax is correct
2. Check for special characters that need escaping
3. Break into smaller chunks (< 10,000 chars per update)
```

### 📚 2. Add System Prompt Enhancement

Add to the system prompt:

```markdown
**PLATFORM-SPECIFIC GUIDES:**
When working with a platform for the first time, remember these patterns:

**Google Docs:**
- Always use SMART tools first (google_docs_smart_create_from_markdown, google_docs_smart_update)
- Don't use multiple basic tools when a smart tool exists
- Example: DON'T: create_document + insert_text + format_text (3 calls)
          DO: smart_create_from_markdown (1 call)

**Gmail:**
- Use gmail_smart_bulk_send_personalized for multiple recipients
- Always validate email addresses before sending
- Check gmail_list_labels before organizing messages

**WooCommerce:**
- List products first to avoid duplicates: woocommerce_list_products
- Use batch tools for bulk operations (10+ items)
- Always set product status: 'draft' for review, 'publish' when ready
```

### 📚 3. Add Tool Usage Examples to System Prompt

```markdown
**REAL-WORLD TOOL EXAMPLES:**

**Creating a Professional Document:**
✅ CORRECT:
```
google_docs_smart_create_from_markdown(
  title="Product Requirements Document",
  markdown_content="""
# Product Overview
**Product Name:** Mobile Fitness App

## Core Features
- User authentication
- Workout tracking
- Progress charts

## Technical Requirements
| Component | Technology | Status |
|-----------|------------|--------|
| Backend   | Node.js    | ✅     |
| Frontend  | React      | 🔄     |
| Database  | PostgreSQL | ✅     |
  """
)
```

❌ WRONG:
```
1. google_docs_create_document(title="PRD")
2. google_docs_insert_text(text="Product Overview")
3. google_docs_format_text(bold=true)
4. google_docs_insert_text(text="Product Name: Mobile Fitness App")
... (15 more calls)
```
```

### 📚 4. Create Cross-Platform Workflow Examples

**Example: `tools/workflows/create_project_suite.md`**

```markdown
# Create Complete Project Suite

## Goal
Create a full project workspace: Document + Spreadsheet + Calendar Events + Task List

## Tools Required (5 calls total)
1. google_docs_smart_create_from_markdown
2. google_sheets_create_spreadsheet
3. google_calendar_create_event
4. google_tasks_create_task (multiple)
5. google_drive_create_folder (to organize)

## Step-by-Step

### 1. Create Project Folder
```python
folder = google_drive_create_folder(
    name="Q1 2025 Marketing Campaign",
    parent_folder_id=None  # Root directory
)
# Returns: folder_id, folder_url
```

### 2. Create Project Document
```python
doc = google_docs_smart_create_from_markdown(
    title="Q1 Marketing Campaign - Project Plan",
    markdown_content="""
    # Campaign Overview
    **Duration:** Jan 1 - Mar 31, 2025
    
    ## Milestones
    - [ ] Strategy finalization
    - [ ] Content creation
    - [ ] Launch campaign
    """,
    folder_id=folder.folder_id
)
```

### 3. Create Budget Spreadsheet
```python
sheet = google_sheets_create_spreadsheet(
    title="Q1 Marketing Budget",
    data=[
        ["Category", "Budget", "Actual", "Remaining"],
        ["Ads", 10000, 0, 10000],
        ["Content", 5000, 0, 5000]
    ],
    folder_id=folder.folder_id
)
```

### 4. Create Calendar Events
```python
kickoff = google_calendar_create_event(
    summary="Q1 Campaign Kickoff",
    start_time="2025-01-05T10:00:00-08:00",
    end_time="2025-01-05T11:00:00-08:00",
    attendees=["team@company.com"],
    description=f"Project doc: {doc.document_url}\nBudget: {sheet.spreadsheet_url}"
)
```

### 5. Create Task List
```python
tasks = [
    google_tasks_create_task(
        title="Finalize campaign strategy",
        due_date="2025-01-10",
        notes=f"See doc: {doc.document_url}"
    ),
    google_tasks_create_task(
        title="Review budget allocations",
        due_date="2025-01-12",
        notes=f"Update: {sheet.spreadsheet_url}"
    )
]
```

## Result
- ✅ Organized folder structure
- ✅ Professional project document
- ✅ Budget tracking spreadsheet
- ✅ Calendar events with links
- ✅ Task list with due dates
- ✅ All interconnected with URLs
```

---

## Implementation Plan

### Phase 1: Immediate (Today)
1. ✅ Create `tools/guides/` directory
2. ✅ Write top 5 platform guides (Google Docs, Gmail, Sheets, Drive, WooCommerce)
3. ✅ Add platform guide references to system prompt

### Phase 2: This Week
4. ✅ Create `tools/workflows/` directory with common multi-tool workflows
5. ✅ Add error recovery patterns to each guide
6. ✅ Create `TOOL_QUICK_REFERENCE.md` - one-page cheat sheet

### Phase 3: Ongoing
7. ✅ Add usage examples to system prompt for most-used tools
8. ✅ Create video/GIF demos for complex workflows
9. ✅ Build interactive tool explorer UI

---

## File Structure

```
AI_agents/
├── tools/
│   ├── schemas/              # ✅ DONE - Tool definitions with examples
│   │   ├── google_docs_tools.json
│   │   ├── gmail_tools.json
│   │   └── ...
│   │
│   ├── guides/               # 📝 TODO - Platform-specific guides
│   │   ├── google_docs_guide.md
│   │   ├── gmail_guide.md
│   │   ├── woocommerce_guide.md
│   │   └── ...
│   │
│   ├── workflows/            # 📝 TODO - Multi-tool examples
│   │   ├── create_project_suite.md
│   │   ├── bulk_email_campaign.md
│   │   ├── automated_reporting.md
│   │   └── ...
│   │
│   └── TOOL_QUICK_REFERENCE.md  # 📝 TODO - One-page cheat sheet
│
└── AI_infrastructure/
    └── routes/
        └── agent_routes.py   # ✅ DONE - System prompt with instructions
```

---

## Answer to Your Questions

### ❓ "Does the agent get the platforms as part of the prompt?"

**YES** ✅ The agent receives:
1. **Platform catalog** - List of all 20+ platforms with tool counts
2. **Priority tools** - 50 most common tools pre-loaded
3. **Discovery tool** - `list_platform_tools` to load more on-demand

### ❓ "Can it request tools for each platform?"

**YES** ✅ The agent can:
1. Call `list_platform_tools(platforms=['gmail', 'slack'])` 
2. Receive detailed tool definitions for those platforms
3. Use those tools immediately in the same conversation

### ❓ "Remember there should be a catalogue of tools with instructions?"

**PARTIALLY** ⚠️ Current state:
- ✅ **Tool descriptions** - Inline in JSON schemas (good)
- ✅ **Parameter examples** - Inline in JSON schemas (good)
- ❌ **Platform guides** - Missing (needs creation)
- ❌ **Workflow examples** - Missing (needs creation)
- ❌ **Error recovery** - Missing (needs documentation)

### ❓ "Smart tools need instructions not just JSON example?"

**CORRECT** ✅ Smart tools need:
1. ✅ When to use them (vs basic tools)
2. ✅ Complete markdown syntax supported
3. ✅ Limitations and edge cases
4. ✅ Multi-call workflows (chaining results)
5. ✅ Error handling strategies

**Recommendation:** Create dedicated guide documents as outlined above.

---

## Next Steps

1. **Review this document** - Confirm the approach
2. **Create platform guides** - Start with top 5 platforms
3. **Add workflow examples** - Document common multi-tool patterns
4. **Update system prompt** - Reference the new guides
5. **Test with AI** - Verify improved tool usage

Would you like me to create the first platform guide (Google Docs) as a template?
