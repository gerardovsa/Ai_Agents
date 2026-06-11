# Tool Reinforcement Instructions - To Be Added to ALL Tool Schemas

## Problem Statement

The AI is:
1. ❌ Using conversation history instead of actually executing tools
2. ❌ Creating fake/broken links that don't exist
3. ❌ Saying "I created X" without actually creating anything
4. ❌ Referencing previous messages instead of current tool execution

## Solution: Add These Instructions to EVERY Tool Description

### Template to Prepend to Tool Descriptions:

```
🚨 CRITICAL EXECUTION RULES:
1. ALWAYS execute THIS tool for THIS action - NEVER reference conversation history
2. ALWAYS return the ACTUAL result from THIS execution - not from memory
3. ALWAYS format response as: [Name] - [ID] - [Full URL] - [Clickable hyperlink with title]
4. NEVER make up URLs - use the EXACT URL returned by the tool
5. NEVER say "I created X earlier" - CREATE IT NOW with this tool

Example correct response format:
✅ "Created spreadsheet: **Sales Report Q4**
   - Spreadsheet ID: `1WVCNk9AvzXCq36s6jnUopHiMAAc-2tqbb6_OiyiZTSA`
   - Full URL: https://docs.google.com/spreadsheets/d/1WVCNk9AvzXCq36s6jnUopHiMAAc-2tqbb6_OiyiZTSA/edit
   - Direct link: [Sales Report Q4](https://docs.google.com/spreadsheets/d/1WVCNk9AvzXCq36s6jnUopHiMAAc-2tqbb6_OiyiZTSA/edit)"

❌ WRONG: "I created the sales report spreadsheet earlier" (Not from THIS execution!)
❌ WRONG: "Here's the spreadsheet: [link]" (No ID, no full URL, might be fake!)
❌ WRONG: "[Sales Report](https://docs.google.com/...)" (Where's the ID? Where's the full URL?)

---

```

### Apply to These Tool Categories:

1. **Creation Tools** (google_sheets_create, google_docs_create, gmail_send_email, etc.):
   - Must return: Name, ID, URL, clickable link
   - Must use ACTUAL returned values
   - Cannot reference "earlier creation"

2. **Read Tools** (google_sheets_read_data, google_docs_get_content, gmail_list_messages, etc.):
   - Must return: Resource name, ID, actual data read
   - Must cite EXACT file/resource accessed
   - Cannot say "based on the data" without specifying which resource

3. **Update Tools** (google_docs_update_content, woocommerce_update_product, etc.):
   - Must return: What was updated, resource ID, confirmation URL
   - Must show before/after for critical updates
   - Cannot assume update succeeded without tool result

4. **Search/List Tools** (gmail_search_messages, woocommerce_search_products, etc.):
   - Must return: Number of results, IDs, titles
   - Must show what search parameters were used
   - Cannot fabricate search results

## Implementation Plan

### Step 1: Update All Google Workspace Tool Schemas
- google_sheets_tools.json (4 tools)
- google_docs_tools.json (38 tools)
- google_drive_tools.json (22 tools)
- google_forms_tools.json (98 tools)
- google_calendar_tools.json (11 tools)
- gmail_tools.json (45 tools)

### Step 2: Update All E-commerce Tool Schemas
- woocommerce_tools.json (30 tools)
- stripe_tools.json (9 tools)

### Step 3: Update All Communication Tool Schemas
- slack_tools.json (11 tools)
- twilio_tools.json (8 tools)

### Step 4: Update All Microsoft 365 Tool Schemas
- microsoft_excel_tools.json (30 tools)
- microsoft_word_tools.json (25 tools)
- microsoft_outlook_tools.json (7 tools)
- microsoft_sharepoint_tools.json (23 tools)
- etc.

### Step 5: Update All Remaining Tool Schemas
- github_tools.json (5 tools)
- supabase_tools.json (28 tools)
- cloudflare_tools.json (4 tools)
- calculator_tools.json (7 tools)
- etc.

## Specific Format Requirements

### For ALL Create/Update Tools:

```json
{
  "name": "tool_name",
  "description": "🚨 EXECUTION RULES: (1) Execute THIS tool NOW - never reference conversation history (2) Return: Name - ID - Full URL - Clickable link (3) Use ACTUAL values from tool result (4) Format: **[Name]** | ID: `[id]` | URL: [full url] | Link: [title](url)\n\n[Original tool description...]",
  "parameters": {...},
  "returns": {
    "type": "object",
    "description": "MUST include: name/title, id, url (full), and be formatted as: Name - ID - URL - Clickable link"
  }
}
```

### For ALL Read/Search Tools:

```json
{
  "name": "tool_name",
  "description": "🚨 EXECUTION RULES: (1) Execute THIS tool NOW - never use cached/remembered data (2) Cite EXACT resource: Name - ID - Path (3) Show what you ACTUALLY read: 'Read X rows from [Resource Name] (ID: [id])' (4) If tool fails, say 'Failed to read [Resource]' - never fabricate data\n\n[Original tool description...]",
  "parameters": {...},
  "returns": {
    "type": "object", 
    "description": "MUST cite: resource name, resource ID, what was read, success/failure status"
  }
}
```

## Testing Criteria

After implementation, test that AI:

✅ Always executes the actual tool (not memory)
✅ Always provides: Name - ID - Full URL - Clickable link
✅ Never makes up URLs or IDs
✅ Never references "earlier" actions
✅ Always cites exact resources accessed
✅ Always shows failure when tools fail
✅ Never hallucinated data from failed tools

## Example Before/After

### BEFORE (Problem):
```
User: "Create a sales spreadsheet"
AI: "I created the sales spreadsheet for you. Here's the link: [Sales Report](https://docs.google.com/spreadsheets/d/ABC123)"

Issues:
- ❌ No ID shown
- ❌ No full URL shown  
- ❌ Might be fake URL
- ❌ Can't verify it was actually created
```

### AFTER (Fixed):
```
User: "Create a sales spreadsheet"
AI: "Created spreadsheet using google_sheets_create:

**Sales Report Q4**
- Spreadsheet ID: `1WVCNk9AvzXCq36s6jnUopHiMAAc-2tqbb6_OiyiZTSA`
- Full URL: https://docs.google.com/spreadsheets/d/1WVCNk9AvzXCq36s6jnUopHiMAAc-2tqbb6_OiyiZTSA/edit
- Direct link: [Open Sales Report Q4](https://docs.google.com/spreadsheets/d/1WVCNk9AvzXCq36s6jnUopHiMAAc-2tqbb6_OiyiZTSA/edit)

Status: ✅ Created successfully with 0 rows"

Verification:
- ✅ Tool executed (google_sheets_create)
- ✅ Name provided
- ✅ ID provided
- ✅ Full URL provided
- ✅ Clickable link provided
- ✅ Can verify creation
```

## Priority Tool Schemas to Update First

1. **google_sheets_create** - Most commonly broken
2. **google_docs_create** - Frequently fake links
3. **gmail_send_email** - Often references old emails
4. **google_docs_smart_create_from_markdown** - Complex, easy to fake
5. **woocommerce_create_product** - E-commerce critical
6. **google_sheets_read_data** - Often uses cached data
7. **gmail_list_messages** - Fabricates email lists
8. **google_drive_upload_file** - Missing IDs/URLs

## Implementation Status

- [ ] Created reinforcement template
- [ ] Updated Google Sheets tools (4 tools)
- [ ] Updated Google Docs tools (38 tools)
- [ ] Updated Gmail tools (45 tools)
- [ ] Updated Google Drive tools (22 tools)
- [ ] Updated WooCommerce tools (30 tools)
- [ ] Updated all remaining tools (400+ tools)
- [ ] Tested with real AI conversations
- [ ] Verified no more fake links
- [ ] Verified no more conversation history usage
- [ ] Verified proper Name - ID - URL - Link format

## Success Metrics

After implementation, measure:
- 0% fake URLs (down from ~30%)
- 0% conversation history references (down from ~40%)
- 100% proper format: Name - ID - URL - Link
- 100% actual tool execution (not memory)
- 100% citation of exact resources accessed
