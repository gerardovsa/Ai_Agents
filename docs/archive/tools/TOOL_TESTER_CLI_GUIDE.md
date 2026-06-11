# Tool Tester CLI - Quick Reference

## Overview

`test_tool.py` is a CLI tool for rapidly testing AI agent tools with user credentials. It executes tools through the **real tool registry** with **credential injection**, exactly as the AI agent does.

## Quick Start

```powershell
# Interactive mode (recommended for first-time use)
python test_tool.py

# List all users
python test_tool.py --list-users

# Search for tools
python test_tool.py --search slides
python test_tool.py --search gmail
python test_tool.py --search microsoft

# Get tool information
python test_tool.py --info google_slides_create_presentation

# Execute a tool directly
python test_tool.py --user 12 --tool google_slides_create_presentation --title "My Presentation"
```

## Features

### 1. List Users
Shows all users with their OAuth credential status:

```powershell
python test_tool.py --list-users
```

Output:
```
ID    Username             Email                               Google   Microsoft
3     inhouse              inhouse@vetsuccessacademy.com       Yes      No
12    gerardo              gerardo@vetsuccessacademy.com       Yes      No
13    Gerardo              Gerardo@minivetguide.onmicrosoft.com No       Yes
```

### 2. Search Tools
Find tools by keyword:

```powershell
python test_tool.py --search slides
python test_tool.py --search email
python test_tool.py --search calendar
```

### 3. Tool Information
Get detailed info about a tool (parameters, types, descriptions):

```powershell
python test_tool.py --info google_slides_create_presentation
```

Output shows:
- Tool description
- All parameters with types
- Required vs optional parameters
- Parameter descriptions

### 4. Execute Tools
Run tools with user credentials:

```powershell
# Google Slides - Create presentation
python test_tool.py --user 12 --tool google_slides_create_presentation --title "Q4 Report"

# Gmail - Send email
python test_tool.py --user 12 --tool gmail_send_email --to "test@example.com" --subject "Test" --body "Hello"

# Google Docs - Create document
python test_tool.py --user 12 --tool google_docs_create_document --title "Meeting Notes"

# Microsoft Word - Create document (user 13 has Microsoft credentials)
python test_tool.py --user 13 --tool microsoft_word_create_document --title "Project Plan"
```

### 5. Interactive Mode
Guided workflow for exploring and testing tools:

```powershell
python test_tool.py
```

Interactive commands:
- `search [term]` - Search for tools
- `info <tool>` - Show tool information
- `exec <tool>` - Execute a tool (prompts for parameters)
- `users` - Show user list
- `quit` - Exit

Example session:
```
> search slides
# Shows all slides-related tools

> info google_slides_create_presentation
# Shows tool parameters

> exec google_slides_create_presentation
# Prompts for parameters:
  title (string) [REQUIRED]: My Presentation
  
# Executes and shows result
```

## Common Use Cases

### Test Google Workspace Tools
```powershell
# User 12 has Google OAuth
python test_tool.py --user 12 --tool google_slides_create_presentation --title "Test"
python test_tool.py --user 12 --tool google_docs_create_document --title "Notes"
python test_tool.py --user 12 --tool gmail_send_email --to "me@example.com" --subject "Hi"
```

### Test Microsoft 365 Tools
```powershell
# User 13 has Microsoft OAuth
python test_tool.py --user 13 --tool microsoft_word_create_document --title "Report"
python test_tool.py --user 13 --tool microsoft_outlook_send_email --to "user@example.com"
python test_tool.py --user 13 --tool microsoft_excel_create_workbook --name "Budget"
```

### Test Calculator Tools
```powershell
python test_tool.py --user 12 --tool calculate_business_cards --quantity 1000 --stock "350GSM Satin"
python test_tool.py --user 12 --tool calculate_flyers --quantity 500 --stock "150GSM Gloss"
```

## How It Works

1. **Loads Tool Registry** - Initializes the same `RegistryV3` that the AI agent uses
2. **Fetches Credentials** - Retrieves OAuth tokens from the database for the specified user
3. **Injects Credentials** - Passes `_user_id` and `_injected_credentials` to the tool
4. **Executes Tool** - Calls `registry.execute_tool()` with user credentials
5. **Returns Result** - Shows formatted JSON output

This is **exactly** how the AI agent executes tools, so you're testing the real production flow.

## Credential Injection

When you execute a tool, it automatically:
- Looks up the user's OAuth tokens in `data/ai_infrastructure.db`
- Injects credentials via `_user_id` parameter
- Tool implementation retrieves tokens from database
- Uses tokens for API calls (Google, Microsoft, etc.)

Example:
```python
# What happens internally:
registry.execute_tool(
    tool_name='google_slides_create_presentation',
    _user_id=12,  # Injected automatically
    _injected_credentials=True,  # Injected automatically
    title='My Presentation'  # Your parameter
)
```

## Troubleshooting

### User has no OAuth credentials
**Error**: OAuth credentials not found

**Solution**: User needs to link their account first:
1. Open web UI (http://localhost:5001)
2. Go to Settings → Account Linking
3. Link Google or Microsoft account
4. Try again

### Tool not found
**Error**: Tool 'xyz' not found

**Solution**: Search for the correct tool name:
```powershell
python test_tool.py --search <keyword>
```

### API Error
**Error**: 401 Unauthorized or 403 Forbidden

**Reasons**:
- OAuth token expired (need to re-authenticate)
- Missing scopes (need to re-link account with more permissions)
- API disabled (check Google/Microsoft admin console)

## Examples Gallery

### Create and Populate a Presentation
```powershell
# Create presentation
python test_tool.py --user 12 --tool google_slides_create_presentation --title "Sales Report"

# Add slide
python test_tool.py --user 12 --tool google_slides_add_slide --presentation_id "PRESENTATION_ID"

# Insert text
python test_tool.py --user 12 --tool google_slides_insert_text --presentation_id "PRESENTATION_ID" --slide_index 0 --text "Q4 Results"
```

### Email Workflow
```powershell
# Send email
python test_tool.py --user 12 --tool gmail_send_email --to "team@example.com" --subject "Report Ready" --body "The quarterly report is complete."

# List inbox
python test_tool.py --user 12 --tool gmail_list_messages --max_results 10
```

### Document Creation
```powershell
# Google Docs
python test_tool.py --user 12 --tool google_docs_create_document --title "Project Brief"

# Microsoft Word
python test_tool.py --user 13 --tool microsoft_word_create_document --title "Proposal"
```

## Comparison with Original test_google_slides_credentials.py

**Old script** (`test_google_slides_credentials.py`):
- ❌ Hard-coded tests for specific tools
- ❌ Manual credential retrieval
- ❌ Limited to Google Slides
- ❌ Not reusable

**New tool** (`test_tool.py`):
- ✅ Works with ALL 645 tools
- ✅ Automatic credential injection
- ✅ Works with Google, Microsoft, and all platforms
- ✅ Fully interactive and reusable
- ✅ Command-line arguments for automation
- ✅ Uses the REAL AI agent flow

## Integration with Development Workflow

### Test new tool implementations
```powershell
# After creating a new tool:
python test_tool.py --info my_new_tool
python test_tool.py --user 12 --tool my_new_tool --param1 "value"
```

### Validate credential injection
```powershell
# Test with different users to verify credential handling:
python test_tool.py --user 12 --tool google_slides_create_presentation --title "User 12 Test"
python test_tool.py --user 13 --tool microsoft_word_create_document --title "User 13 Test"
```

### Debug tool issues
```powershell
# Run tool and inspect full output:
python test_tool.py --user 12 --tool problematic_tool --debug
# Shows full stack trace and credential flow
```

## Status

✅ **PRODUCTION READY**
- Tested with Google Workspace tools (Slides, Docs, Gmail)
- Tested with Microsoft 365 tools (Word, Excel, Outlook)
- Tested with Calculator tools
- Credential injection working perfectly
- All 645 tools accessible

## Files

- `test_tool.py` - Main CLI tool (370 lines)
- Location: `C:\Users\gpoli\GIT\AI_agents\test_tool.py`

## See Also

- `tool_tester.py` - Original API-based version (deprecated)
- `test_google_slides_credentials.py` - Original hard-coded test (deprecated)
- `TOOL_TESTING_COMPLETE.md` - Full documentation
