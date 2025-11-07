## Tool Naming Conventions and Discovery Guidance

### Quick Reference

**When searching for tools, use these patterns:**

```
search_tools("microsoft")        → 350+ Microsoft tools
search_tools("google")           → 200+ Google tools
search_tools("outlook")          → Specific Outlook email tools
search_tools("gmail")            → Specific Gmail tools
search_tools("teams")            → Microsoft Teams tools
search_tools("sheets")           → Google Sheets tools
search_tools("email")            → All email-related tools
search_tools("spreadsheet")      → All spreadsheet tools
```

---

## Microsoft 365 (m365/Office) Tools

### Available Platforms
```
excel, word, outlook, teams, onedrive, powerpoint, onenote, forms, sharepoint
```

### Naming Pattern
```
microsoft_[PLATFORM]_[ACTION]

Examples:
- microsoft_outlook_send_email
- microsoft_teams_send_message
- microsoft_excel_tools_create_workbook
- microsoft_word_tools_create_document
- microsoft_calendar_create_event
- microsoft_onedrive_upload_file
```

### How to Use

**Step 1: Search for the platform**
```
search_tools("microsoft")  → Shows 350 tools
```

**Step 2: Narrow down to specific platform**
```
search_tools("outlook")    → Shows 25 Outlook tools
search_tools("teams")      → Shows 20 Teams tools
search_tools("excel")      → Shows Excel tools
```

**Step 3: Get tool details**
```
get_tool_schema("microsoft_outlook_send_email")
```

**Step 4: Execute the tool**
```
execute_tool("microsoft_outlook_send_email", to="user@domain.com", subject="...", body="...")
```

### Common Subplatforms

| Platform | Tools Available | Examples |
|----------|-----------------|----------|
| **Outlook** | 25+ | send_email, create_event, get_messages, add_contact |
| **Teams** | 20+ | send_message, send_chat, create_channel, schedule_meeting |
| **Excel** | 15+ | create_workbook, add_data, format_cells, create_chart |
| **Word** | 12+ | create_document, add_text, format_text, add_table |
| **OneDrive** | 10+ | upload_file, create_folder, list_files, share_file |
| **Calendar** | 8+ | create_event, update_event, list_events, delete_event |
| **Forms** | 6+ | create_form, get_responses, add_question, close_form |
| **SharePoint** | 8+ | create_site, upload_document, manage_list, share_item |

---

## Google Workspace Tools

### Available Platforms
```
gmail, sheets, docs, forms, calendar, drive, tasks
```

### Naming Pattern
```
google_[PLATFORM]_[ACTION]

Examples:
- google_sheets_create_spreadsheet
- google_docs_create_document
- gmail_send_email
- google_forms_create_form
- google_calendar_create_event
- google_drive_upload_file
- google_tasks_add_task
```

### How to Use

**Step 1: Search for the platform**
```
search_tools("google")     → Shows 200+ tools
```

**Step 2: Narrow down to specific platform**
```
search_tools("gmail")      → Shows Gmail tools
search_tools("sheets")     → Shows Google Sheets tools
search_tools("docs")       → Shows Google Docs tools
search_tools("forms")      → Shows Google Forms tools
```

**Step 3: Get tool details**
```
get_tool_schema("google_sheets_create_spreadsheet")
```

**Step 4: Execute the tool**
```
execute_tool("google_sheets_create_spreadsheet", title="My Sheet", headers=["Name", "Email"])
```

### Common Subplatforms

| Platform | Tools Available | Examples |
|----------|-----------------|----------|
| **Gmail** | 30+ | send_email, get_messages, create_draft, add_label, archive |
| **Sheets** | 25+ | create_spreadsheet, add_data, format_cells, create_chart |
| **Docs** | 20+ | create_document, add_text, format_text, add_table |
| **Forms** | 15+ | create_form, get_responses, add_question, close_form |
| **Calendar** | 12+ | create_event, update_event, list_events, delete_event |
| **Drive** | 15+ | upload_file, create_folder, list_files, share_file |
| **Tasks** | 8+ | add_task, list_tasks, update_task, delete_task |

---

## Discovery Strategy

### Overwhelming Results? Use This Approach

**Problem:** `search_tools("microsoft")` returns 350 tools - too many!

**Solution:** Use specific subplatform names

```
# Instead of searching broadly:
search_tools("microsoft")        # Returns 350 tools ❌ Too many!

# Search for specific subplatform:
search_tools("outlook")          # Returns 25 tools ✅ Better!
search_tools("teams")            # Returns 20 tools ✅ Better!
search_tools("excel_tools")      # Returns 15 tools ✅ Better!

# Or use the naming pattern directly:
get_tool_schema("microsoft_outlook_send_email")  # Get exact tool ✅ Best!
```

### Quick Decision Tree

```
User wants to send an email:
  └─ Ask: Google or Microsoft?
     ├─ Google → search_tools("gmail") → find gmail_send_email
     └─ Microsoft → search_tools("outlook") → find microsoft_outlook_send_email

User wants to create a spreadsheet:
  └─ Ask: Google or Microsoft?
     ├─ Google → search_tools("sheets") → find google_sheets_create_spreadsheet
     └─ Microsoft → search_tools("excel") → find microsoft_excel_tools_create_workbook

User wants to schedule a meeting:
  └─ Ask: Google or Microsoft?
     ├─ Google → search_tools("calendar") → find google_calendar_create_event
     └─ Microsoft → search_tools("teams") → find microsoft_teams_schedule_meeting
                  or search_tools("outlook") → find microsoft_calendar_create_event
```

---

## Advanced Patterns

### Functional Categories (Works Across Platforms)

```
search_tools("email")          → Gmail + Outlook email tools
search_tools("spreadsheet")    → Google Sheets + Excel tools
search_tools("document")       → Google Docs + Word tools
search_tools("calendar")       → Google Calendar + Outlook Calendar
search_tools("storage")        → Google Drive + OneDrive tools
search_tools("chat")           → Teams + Slack messaging tools
```

### Using list_platform_tools()

```
# Get all Microsoft platforms
list_platform_tools("microsoft")    → Lists all Microsoft tools grouped by platform

# Get specific platform
list_platform_tools("outlook")      → Lists Outlook email tools
list_platform_tools("teams")        → Lists Teams messaging tools
list_platform_tools("gmail")        → Lists Gmail email tools
```

---

## System Prompt Guidance

### For AI Agents (Claude, etc.)

When a user requests tool usage:

1. **Identify the platform need** (Google or Microsoft?)
2. **Identify the subplatform** (Gmail, Outlook, Teams, Sheets, etc.)
3. **Search narrowly** using subplatform name
4. **Get tool schema** to understand parameters
5. **Execute with parameters**

**Example workflow:**
```
User: "Send an email with an Excel attachment"

AI Response:
  1. This requires email + Excel tools
  2. Identify platform: Microsoft or Google? (Ask user or assume based on context)
  3. Search: search_tools("outlook") for email
             search_tools("excel") for attachment
  4. Find: microsoft_outlook_send_email + microsoft_excel_tools_...
  5. Get schemas: get_tool_schema("microsoft_outlook_send_email")
  6. Execute with file attachment parameter
```

---

## Naming Convention Rules (For Tool Developers)

When creating new tools, follow this pattern:

```
[PLATFORM]_[SUBPLATFORM]_[ACTION]

Where:
- PLATFORM: google, microsoft, slack, stripe, etc.
- SUBPLATFORM: sheets, outlook, teams, calendar, etc.
- ACTION: create, send, update, delete, list, get, etc.

Examples:
✓ google_sheets_create_spreadsheet
✓ microsoft_outlook_send_email
✓ microsoft_teams_send_message
✓ google_forms_create_form
✓ microsoft_excel_tools_add_data

✗ sheet_create (missing platform)
✗ create_spreadsheet (too vague)
✗ gs_create (unclear abbreviations)
```

---

## Troubleshooting

### "I'm getting too many tools"
**Solution:** Use specific subplatform name
```
search_tools("microsoft")       # ❌ 350 tools
search_tools("microsoft_outlook")  # ✅ 25 tools
search_tools("outlook")         # ✅ 25 tools
```

### "I can't find the tool I need"
**Solution:** Try functional search
```
search_tools("email")           # Finds all email tools
search_tools("spreadsheet")     # Finds all spreadsheet tools
get_tool_schema("tool_name")    # Get details on specific tool
```

### "The tool naming is confusing"
**Solution:** Use list_platform_tools()
```
list_platform_tools("microsoft")   # See all Microsoft tools organized
list_platform_tools("google")      # See all Google tools organized
```

---

## Tool Count Reference

Current tool inventory:

```
Microsoft 365 Suite:
  - Outlook: 25+ tools
  - Teams: 20+ tools
  - Excel: 15+ tools
  - Word: 12+ tools
  - OneDrive: 10+ tools
  - Calendar: 8+ tools
  - Forms: 6+ tools
  - SharePoint: 8+ tools
  Total: ~350 Microsoft tools

Google Workspace Suite:
  - Gmail: 30+ tools
  - Sheets: 25+ tools
  - Docs: 20+ tools
  - Forms: 15+ tools
  - Calendar: 12+ tools
  - Drive: 15+ tools
  - Tasks: 8+ tools
  Total: ~200 Google tools

Other Platforms:
  - Stripe: 40+ tools
  - Slack: 30+ tools
  - Salesforce: 25+ tools
  - Jira: 20+ tools
  - Other: 100+ tools

Total System: 600+ tools
```

---

## Version History

- **Nov 3, 2025**: Initial creation with Microsoft and Google guidance
- Pattern-based discovery documented
- Troubleshooting guide added
