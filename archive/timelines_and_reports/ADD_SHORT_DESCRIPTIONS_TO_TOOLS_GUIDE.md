# AI Agent Instructions: Add Short Descriptions to Tool Schemas

**Date:** December 10, 2025  
**Purpose:** Add `short_description` field to all 749 tool schemas for hybrid tool search  
**Estimated Time:** 3-4 hours (automated processing of 80+ JSON files)  
**Priority:** HIGH - Required for `hybrid_tool_search` implementation

---

## 📋 OBJECTIVE

Add a **short_description** field (1-2 sentences, max 100 characters) to every tool in all tool schema JSON files. This enables the `hybrid_tool_search` tool to return concise, readable tool lists without token bloat.

---

## 🎯 UNIFIED JSON STRUCTURE ANALYSIS

After analyzing 30+ tool schema files, here's the **CURRENT structure** (as of Dec 2025):

### ✅ **CONSISTENT FIELDS** (Present in ALL tools):

```json
{
  "platform": "gmail",              // ✅ Always present at file level
  "description": "...",              // ✅ Always present at file level (platform description)
  "tools": [                         // ✅ Always present
    {
      "name": "tool_name",           // ✅ REQUIRED - Always present
      "description": "...",          // ✅ REQUIRED - Always present (full description)
      "platform": "gmail",           // ✅ OPTIONAL - Sometimes duplicated at tool level
      "parameters": {...}            // ✅ REQUIRED - Always present
    }
  ]
}
```

### ❌ **MISSING FIELD** (What we need to add):

```json
{
  "name": "gmail_send_email",
  "short_description": "Send email via Gmail",  // ❌ DOES NOT EXIST - WE NEED TO ADD THIS
  "description": "🚨 CRITICAL EXECUTION RULES:\n(1) ALWAYS execute THIS tool NOW...\n\n[50+ more lines]",
  "platform": "gmail"
}
```

---

## 📊 CURRENT DESCRIPTION PATTERNS (Problems to Solve)

### ❌ **Problem 1: MASSIVE descriptions with execution rules**

**Current:**
```json
{
  "name": "gmail_send_email",
  "description": "🚨 CRITICAL EXECUTION RULES:\n(1) ALWAYS execute THIS tool NOW - NEVER reference 'I created earlier' or use conversation history\n(2) MUST return format: **[Name]** | ID: `[id]` | URL: [full_url] | Link: [title](url)\n(3) Use EXACT values from tool response - NEVER make up fake URLs/IDs\n(4) If tool fails, say 'Failed to create' - NEVER pretend it succeeded\n\nExample response:\nCreated: **New Document**\n- ID: `abc123`\n- URL: https://example.com/doc/abc123\n- Link: [New Document](https://example.com/doc/abc123)\n\nSend an email via Gmail. Supports HTML content, attachments, CC, BCC, importance flags, and read receipts."
}
```

**What we need to extract:**
```json
{
  "short_description": "Send email via Gmail with attachments, CC, BCC"
}
```

---

### ❌ **Problem 2: Smart tools with combo capabilities**

**Current:**
```json
{
  "name": "gmail_ai_smart_compose_and_send",
  "description": "🚨 CRITICAL...[rules]\n\n📧 SMART TOOL: AI-powered email composition and sending in ONE call. Takes natural language prompt, generates professional email, and sends or creates draft."
}
```

**What we need:**
```json
{
  "short_description": "SMART: AI-compose + send email in one call"
}
```

---

### ❌ **Problem 3: Calculator tools with product-specific info**

**Current:**
```json
{
  "name": "calculate_flyers",
  "description": "🚨 CRITICAL...[rules]\n\nCalculate quote for digital flyers/leaflets. ALSO used for BUSINESS CARDS (90mm x 55mm). Supports various stock types, print modes (single/double sided), quantities, and cellophane finishes. Returns detailed quote with cost breakdown."
}
```

**What we need:**
```json
{
  "short_description": "Quote flyers/business cards with print options"
}
```

---

## 🔧 IMPLEMENTATION STRATEGY

### **Step 1: Extraction Algorithm**

Create Python script that processes each tool and extracts short description:

```python
import json
import re
from pathlib import Path

def extract_short_description(full_description: str, tool_name: str) -> str:
    """
    Extract short description from full description.
    
    Rules:
    1. Remove CRITICAL EXECUTION RULES section
    2. Remove Example response sections
    3. Find actual tool description (usually after rules)
    4. Extract first 1-2 sentences (max 100 chars)
    5. Add SMART prefix if tool is smart/bundled
    6. Include key capabilities if space allows
    """
    
    # Remove critical rules section (everything before "Example response:")
    # Pattern: 🚨 CRITICAL...(multiple lines)...Example response:...(multiple lines)
    text = re.sub(
        r'🚨 CRITICAL.*?(?=\n\n[A-Z]|\n\n📧|\n\n⚠️|\n\nCalculate|\n\nSend|\n\nCreate)',
        '',
        full_description,
        flags=re.DOTALL
    )
    
    # Remove example response blocks
    text = re.sub(r'Example response:.*?(?=\n\n)', '', text, flags=re.DOTALL)
    
    # Remove ⚠️ warning blocks at start
    text = re.sub(r'^⚠️.*?(?=\n\n)', '', text, flags=re.DOTALL | re.MULTILINE)
    
    # Clean up whitespace
    text = text.strip()
    
    # Extract first sentence or up to 100 chars
    first_sentence = re.split(r'(?<=[.!?])\s+', text)[0]
    
    # If first sentence is too long, truncate at 100 chars
    if len(first_sentence) > 100:
        first_sentence = first_sentence[:97] + '...'
    
    # Add SMART prefix if applicable
    if 'SMART TOOL' in full_description or 'smart_bundled' in full_description:
        first_sentence = 'SMART: ' + first_sentence
    
    return first_sentence


def process_tool_schema(file_path: Path):
    """Process a single tool schema JSON file."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    modified = False
    
    # Process each tool in the schema
    for tool in data.get('tools', []):
        tool_name = tool.get('name', '')
        full_desc = tool.get('description', '')
        
        # Skip if short_description already exists
        if 'short_description' in tool:
            print(f"  ⏭️  {tool_name} - Already has short_description")
            continue
        
        # Extract short description
        short_desc = extract_short_description(full_desc, tool_name)
        
        # Add to tool (insert after 'name' field for readability)
        tool['short_description'] = short_desc
        modified = True
        
        print(f"  ✅ {tool_name}")
        print(f"     Short: {short_desc}")
    
    # Save file if modified
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved: {file_path.name}\n")
    else:
        print(f"⏭️  No changes: {file_path.name}\n")


def main():
    """Process all tool schema files."""
    
    schemas_dir = Path('tools/schemas')
    json_files = list(schemas_dir.glob('*.json'))
    
    print(f"📂 Found {len(json_files)} JSON files\n")
    print("="*80)
    
    for i, file_path in enumerate(json_files, 1):
        print(f"\n[{i}/{len(json_files)}] Processing: {file_path.name}")
        print("-"*80)
        
        try:
            process_tool_schema(file_path)
        except Exception as e:
            print(f"❌ ERROR: {e}\n")
            continue
    
    print("\n" + "="*80)
    print("✅ COMPLETE - All tool schemas processed")
    print("="*80)


if __name__ == '__main__':
    main()
```

---

## 📝 SHORT DESCRIPTION GUIDELINES

### **Format Rules:**

1. **Length:** 1-2 sentences, max 100 characters
2. **Prefix:** Add "SMART: " for smart/bundled tools
3. **Action-oriented:** Start with verb (Send, Create, Get, Calculate, List, etc.)
4. **Key capabilities:** Include 1-2 key features if space allows
5. **No emojis:** Keep clean and professional
6. **No execution rules:** Just the tool's purpose

---

### **Examples by Tool Type:**

#### **Email Tools:**
```json
{
  "name": "gmail_send_email",
  "short_description": "Send email via Gmail with attachments, CC, BCC"
}

{
  "name": "gmail_ai_smart_compose_and_send",
  "short_description": "SMART: AI-compose and send email in one call"
}

{
  "name": "microsoft_outlook_send_email",
  "short_description": "Send email via Outlook with attachments, flags"
}
```

#### **Document Tools:**
```json
{
  "name": "google_docs_create_document",
  "short_description": "Create new Google Doc with optional content"
}

{
  "name": "google_sheets_create",
  "short_description": "Create spreadsheet with markdown formatting support"
}

{
  "name": "microsoft_word_create_document",
  "short_description": "Create Word doc with styles and formatting"
}
```

#### **Calculator Tools:**
```json
{
  "name": "calculate_flyers",
  "short_description": "Quote flyers/business cards with print options"
}

{
  "name": "calculate_booklets",
  "short_description": "Quote saddle-stitch booklets with page counts"
}

{
  "name": "calculate_perfect_bound_books",
  "short_description": "Quote perfect-bound books with cover/internal specs"
}
```

#### **Data Tools:**
```json
{
  "name": "google_sheets_read_range",
  "short_description": "Read data from spreadsheet range"
}

{
  "name": "xero_get_invoices",
  "short_description": "Get Xero invoices with status/date filters"
}

{
  "name": "stripe_create_payment_intent",
  "short_description": "Create payment intent for card payments"
}
```

#### **Communication Tools:**
```json
{
  "name": "slack_post_message",
  "short_description": "Post message to Slack channel or thread"
}

{
  "name": "twilio_send_sms",
  "short_description": "Send SMS via Twilio with media support"
}

{
  "name": "microsoft_teams_send_message",
  "short_description": "Send message to Teams channel"
}
```

#### **Meta Tools:**
```json
{
  "name": "search_tools",
  "short_description": "Search available tools by keyword"
}

{
  "name": "list_platform_tools",
  "short_description": "List all tools for a specific platform"
}

{
  "name": "get_tool_schema",
  "short_description": "Get full parameter schema for a tool"
}
```

#### **Smart/Bundled Tools:**
```json
{
  "name": "synergy_smart_project_tracker",
  "short_description": "SMART: Create multi-platform project with milestones"
}

{
  "name": "indesign_create_catalog_from_data",
  "short_description": "SMART: Generate complete catalog from CSV in one call"
}

{
  "name": "gmail_smart_bulk_send_personalized",
  "short_description": "SMART: Send personalized bulk emails with merge"
}
```

---

## 🎯 STEP-BY-STEP EXECUTION PLAN

### **Phase 1: Setup (5 minutes)**

1. Create Python script file: `add_short_descriptions.py`
2. Copy the extraction algorithm code above
3. Test on 1 file first: `calculator_tools.json`
4. Verify output looks correct

### **Phase 2: Process All Files (2-3 hours)**

1. Run script: `python add_short_descriptions.py`
2. Script will:
   - Process all 80+ JSON files
   - Extract short descriptions automatically
   - Add `short_description` field to each tool
   - Save files with proper formatting
3. Monitor console output for errors
4. Handle edge cases manually if needed

### **Phase 3: Manual Review (30 minutes)**

Review 10-20 random tools to ensure quality:

```bash
# Check a few random files
cat tools/schemas/gmail_tools.json | grep -A 2 "short_description"
cat tools/schemas/calculator_tools.json | grep -A 2 "short_description"
cat tools/schemas/google_sheets_tools.json | grep -A 2 "short_description"
```

### **Phase 4: Validation (15 minutes)**

Test that hybrid_tool_search can access short descriptions:

```python
# Test script
from tools.registry_v3 import RegistryV3

registry = RegistryV3()
tool = registry.get_tool('gmail_send_email')

print(f"Tool: {tool['name']}")
print(f"Short: {tool.get('short_description', 'MISSING')}")
print(f"Platform: {tool.get('platform')}")
```

Expected output:
```
Tool: gmail_send_email
Short: Send email via Gmail with attachments, CC, BCC
Platform: gmail
```

---

## 📊 EXPECTED RESULTS

After completion, **ALL 749 tools** should have:

```json
{
  "name": "tool_name",
  "short_description": "Action-oriented 1-2 sentence description (max 100 chars)",
  "description": "[Full description with rules and examples]",
  "platform": "platform_name",
  "parameters": {...}
}
```

---

## 🔍 EDGE CASES TO HANDLE

### **Case 1: Platform Guide Tools**
```json
{
  "name": "xero_platform_guide",
  "short_description": "Get platform guidance and tool recommendations"
}
```

### **Case 2: Disabled/Testing Tools**
```json
{
  "name": "gmail_smart_bulk_send_personalized_DISABLED_TESTING",
  "short_description": "DISABLED: Bulk send with personalization (testing)"
}
```

### **Case 3: Multi-purpose Tools**
```json
{
  "name": "calculate_flyers",
  "description": "...ALSO used for BUSINESS CARDS...",
  "short_description": "Quote flyers/leaflets/business cards with options"
}
```

### **Case 4: Tools with Special Syntax**
```json
{
  "name": "google_sheets_create",
  "description": "...with MARKDOWN FORMATTING v2.0!...",
  "short_description": "Create spreadsheet with markdown formatting"
}
```

---

## ✅ SUCCESS CRITERIA

1. ✅ All 749 tools have `short_description` field
2. ✅ All short descriptions are ≤100 characters
3. ✅ SMART tools have "SMART: " prefix
4. ✅ No execution rules in short descriptions
5. ✅ Descriptions are action-oriented (verb-first)
6. ✅ Key capabilities mentioned when space allows
7. ✅ JSON files are valid and properly formatted
8. ✅ Registry can load and access short_description field
9. ✅ hybrid_tool_search can use short descriptions in output

---

## 🚀 NEXT STEPS (After Completion)

Once short descriptions are added:

1. **Implement `hybrid_tool_search` tool** (uses short descriptions)
2. **Update intelligent_discovery.py** (return short descriptions in suggestions)
3. **Test with AI agent** (verify tool selection improves)
4. **Monitor token usage** (should reduce by 80-90%)

---

## 📞 SUPPORT

If you encounter issues:

1. **Invalid JSON:** Use `python -m json.tool file.json` to validate
2. **Encoding errors:** Ensure files are UTF-8
3. **Missing descriptions:** Manually add short description based on tool name
4. **Ambiguous tools:** Check full description for context

---

## 📝 FINAL STRUCTURE REFERENCE

### **Complete Tool Object (After Implementation):**

```json
{
  "name": "gmail_send_email",
  "short_description": "Send email via Gmail with attachments, CC, BCC",
  "description": "🚨 CRITICAL EXECUTION RULES:\n(1) ALWAYS execute THIS tool NOW - NEVER reference 'I created earlier' or use conversation history\n(2) MUST return format: **[Name]** | ID: `[id]` | URL: [full_url] | Link: [title](url)\n(3) Use EXACT values from tool response - NEVER make up fake URLs/IDs\n(4) If tool fails, say 'Failed to create' - NEVER pretend it succeeded\n\nExample response:\nCreated: **New Document**\n- ID: `abc123`\n- URL: https://example.com/doc/abc123\n- Link: [New Document](https://example.com/doc/abc123)\n\nSend an email via Gmail. Supports HTML content, attachments, CC, BCC, importance flags, and read receipts.",
  "platform": "gmail",
  "category": "basic",
  "parameters": {
    "to": {
      "type": "array",
      "description": "Recipient email addresses"
    },
    "subject": {
      "type": "string",
      "description": "Email subject line"
    },
    "body": {
      "type": "string",
      "description": "Email body content"
    }
  },
  "returns": {
    "type": "object",
    "description": "Sent message details with message_id"
  }
}
```

---

## 🎯 READY TO EXECUTE

This guide provides everything needed to add short descriptions to all 749 tools. Execute the Python script, review results, validate with test script, and you're ready for hybrid tool search implementation!

**Estimated Total Time:** 3-4 hours  
**Automated Processing:** 95%  
**Manual Review:** 5%  
**Success Rate:** 100% (with proper error handling)
