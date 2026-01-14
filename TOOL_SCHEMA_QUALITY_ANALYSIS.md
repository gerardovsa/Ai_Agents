# Tool Schema Quality Analysis

**Date**: November 20, 2025  
**Issue**: Most tool schemas lack comprehensive instructions found in Google Docs smart markdown tools

---

## Problem Identified

**User Request**: "your schemas my be comprehensive and have clear instructions on how to use them ... look at the google doc smart markdown tool"

**Analysis**: 
- ✅ Google Docs smart markdown tools (google_docs_smart_create_from_markdown, google_docs_smart_update, google_docs_smart_create_from_markdown_v2) have **EXCELLENT** comprehensive instructions
- ❌ Most other platform tools have **GENERIC PLACEHOLDER** descriptions
- ❌ Many tools have copy-pasted example responses that don't match the tool

---

## Gold Standard: Google Docs Smart Markdown Tools

### What Makes Them Excellent

**1. Critical Warnings at Top**
```json
"description": "⚠️ MUST USE: execute_tool(tool_name='google_docs_smart_create_from_markdown', ...) - DO NOT call directly!

CRITICAL: DO NOT include emojis in the markdown_content parameter. Use plain text only. Emojis cause formatting errors and encoding issues.

SMART TOOL: Create fully formatted Google Docs from markdown..."
```

**2. Feature Listings with Syntax**
```
Supports: # headings (H1-H6, always black), **bold**, *italic*, ~~strikethrough~~, ==highlight==, `code`, ```blocks```, [links](url), ![images](url), nested bullets/numbers (indent 2 spaces), > blockquotes, --- lines, <<NEW-PAGE>>, <<BOOKMARK:name>>
```

**3. Clear Hierarchy Explanations**
```
HEADING HIERARCHY: H1-H3 for document structure, H4 (11pt bold) ONLY for list titles
```

**4. Special Syntax Documentation**
```
BOOKMARK SYNTAX: <<BOOKMARK:section_name>> creates a named range that can be linked directly: document_url#bookmark=section_name. Use for table of contents, section navigation, or external references.
```

**5. Complete Feature Matrix**
```
COMPLETE MARKDOWN SUPPORT:

TEXT FORMATTING:
- **bold** or __bold__ -> Bold text
- *italic* or _italic_ -> Italic text
- __underline__ -> Underlined text (double underscore)
- ~~strikethrough~~ -> Strikethrough text
- ==highlight== -> Yellow highlighted text
- `inline code` -> Monospace code
- H~2~O -> Subscript (H2O)
- x^2^ -> Superscript (x2)
```

**6. Usage Examples**
```json
"examples": [
  {
    "description": "Create formatted business report with advanced features",
    "parameters": {
      "title": "Q4 Business Report",
      "markdown_content": "->**Q4 2024 Sales Report**<-\n\n..."
    }
  }
]
```

**7. Technical Details**
```
DEFAULT FONT: Arial 11pt (matches Google Docs, NOT Times New Roman)
HEADING SIZES: H1=20pt, H2=18pt, H3=16pt, H4-H6=11pt
```

**8. Comparison with Alternatives**
```
ADVANTAGES OVER V1:
- Faster (0.5-2s vs 2-8s)
- Much less code
- High success rate
- Automatic shareability
```

---

## Bad Examples: Generic Placeholders

### Stripe Tools (stripe_tools.json)

**Problem:**
```json
{
  "name": "stripe_create_payment_intent",
  "description": "Example response:\nCreated: **New Document**\n- ID: `abc123`\n- URL: https://example.com/doc/abc123`\n\nCreate a payment intent for card payments"
}
```

**Issues:**
- "Created: **New Document**" is wrong (it's a payment, not a document)
- No usage instructions
- No parameter explanations
- No common patterns
- No error handling guidance

**Should Be:**
```json
{
  "name": "stripe_create_payment_intent",
  "description": "Create a payment intent for online card payments. Payment intents track the customer's payment lifecycle from creation through checkout to completion.

USAGE INSTRUCTIONS:
Use this when customer needs to pay for products/services. Payment intent is created server-side, client_secret is passed to frontend for Stripe.js to complete payment.

COMMON PARAMETERS:
- amount: In CENTS (e.g., $10.00 = 1000)
- currency: Lowercase ISO code ('usd', 'eur', 'gbp')
- customer_id: Optional but recommended for repeat customers
- metadata: Custom fields (order_id, user_id, etc.)

WORKFLOW:
1. Create payment intent (this tool)
2. Pass client_secret to frontend
3. Customer enters payment details
4. Stripe processes payment
5. Confirm with stripe_confirm_payment() or webhook

EXAMPLE:
amount=5000 (= $50.00), currency='usd', customer_id='cus_abc123', metadata={'order_id': '12345'}

RETURNS:
- id: Payment intent ID (pi_xxx)
- client_secret: Pass to Stripe.js (pi_xxx_secret_xxx)
- status: 'requires_payment_method' (awaiting customer action)
- amount, currency: Confirmed values

ERROR HANDLING:
- Invalid amount: Must be positive integer
- Invalid currency: Use 3-letter ISO code
- Customer not found: Verify customer_id exists"
}
```

### Slack Tools (slack_tools.json)

**Problem:**
```json
{
  "name": "slack_post_message",
  "description": "Example response:\nCreated: **New Document**\n...\n\nPost a message to a channel or user"
}
```

**Issues:**
- Wrong example response (not a document)
- No markdown syntax examples
- No Block Kit explanation
- No threading guidance
- No emoji syntax

**Should Be:**
```json
{
  "name": "slack_post_message",
  "description": "Post a message to Slack channel or direct message. Supports markdown formatting, Block Kit rich layouts, threading, and custom bot appearance.

USAGE INSTRUCTIONS:
Use this to send notifications, alerts, reports, or conversational messages to Slack. Messages can be plain text, markdown-formatted, or use Block Kit for interactive elements.

CHANNEL FORMATS:
- Public channel: '#general' or 'C1234567890' (ID)
- Private channel: Must use ID (user needs to be member)
- Direct message: '@username' or 'U1234567890' (user ID)
- Multi-person DM: Use group ID (G1234567890)

TEXT FORMATTING (Markdown):
- *bold* → Bold text
- _italic_ → Italic text
- ~strike~ → Strikethrough
- `code` → Inline code
- ```code block``` → Code block
- <url|text> → Hyperlink
- <@U123|name> → @mention user
- <#C123|channel> → #channel link
- :emoji: → Emoji

THREADING:
- New message: Omit thread_ts
- Reply in thread: Set thread_ts to parent message timestamp
- Thread parent: Save message ts for future replies

BLOCKS (Rich Formatting):
- Use 'blocks' parameter for interactive messages
- Supports buttons, dropdowns, images, sections
- See Slack Block Kit Builder for JSON structure

BOT APPEARANCE:
- username: Custom bot name (overrides app name)
- icon_emoji: ':robot_face:' (overrides app icon)
- icon_url: Custom image URL

EXAMPLE:
channel='#alerts', text='*Error*: Database connection failed\n```\nConnection timeout after 30s\n```', thread_ts='1234567890.123456'

RETURNS:
- ts: Message timestamp (save for threading)
- channel: Channel ID where posted
- message: Full message object with formatting

ERROR HANDLING:
- channel_not_found: Verify channel exists and bot is member
- not_in_channel: Bot needs to be added to private channel
- rate_limit: Wait 1 second between messages"
}
```

---

## Platforms Needing Updates

### High Priority (User-Facing Tools)
1. **Stripe** (9 tools) - Payment processing
2. **Slack** (11 tools) - Team communication
3. **Twilio** (8 tools) - SMS/Voice
4. **Xero** (21 tools) - Accounting
5. **WooCommerce** (30 tools) - E-commerce
6. **Shopify** (if exists) - E-commerce

### Medium Priority (Developer Tools)
7. **GitHub** (5 tools) - Code management
8. **Render** (13 tools) - Deployment
9. **Cloudflare** (4 tools) - CDN/DNS
10. **Supabase** (39 tools) - Database

### Lower Priority (Already Good or Less Used)
11. **Google Workspace** - Most already have good docs
12. **Microsoft 365** - Microsoft tools
13. **Automation** - Just updated (✅ DONE)

---

## Standard Template for Tool Descriptions

```json
{
  "name": "platform_tool_action",
  "description": "[One-line summary of what tool does]

USAGE INSTRUCTIONS:
[When to use this tool, what problem it solves]

[Platform-specific concepts explained]

PARAMETERS EXPLAINED:
- param1: [What it does, format, examples]
- param2: [Optional vs required, defaults]
- param3: [Common values, validation rules]

WORKFLOW/PROCESS:
1. [Step 1]
2. [Step 2]
3. [Step 3]

SYNTAX/FORMATTING (if applicable):
- [Special syntax with examples]
- [Format rules]

EXAMPLE:
param1='value1', param2='value2', param3={'key': 'value'}

RETURNS:
- field1: [What it contains, when to use it]
- field2: [Format, meaning]
- field3: [Next steps with this value]

ERROR HANDLING:
- error_type: [What causes it, how to fix]
- another_error: [Prevention tips]

RELATED TOOLS:
- tool_name: [When to use instead/after]",
  "platform": "platform",
  "parameters": {...},
  "returns": {...}
}
```

---

## Implementation Plan

### Phase 1: High-Value Platforms (Week 1)
**Target**: Stripe, Slack, Twilio (28 tools total)

**Stripe** (9 tools):
1. stripe_create_payment_intent
2. stripe_confirm_payment
3. stripe_create_customer
4. stripe_create_subscription
5. stripe_cancel_subscription
6. stripe_create_refund
7. stripe_list_payments
8. stripe_get_payment
9. stripe_create_invoice

**Focus**:
- Payment workflow explanations
- Amount in cents clarification
- Currency code examples
- Customer lifecycle
- Metadata usage patterns

### Phase 2: E-commerce Platforms (Week 2)
**Target**: Xero, WooCommerce (51 tools total)

**Xero** (21 tools) - Accounting workflows
**WooCommerce** (30 tools) - Product/order management

**Focus**:
- Business process explanations
- Tax calculations
- Product variations
- Order status workflows

### Phase 3: Developer Tools (Week 3)
**Target**: GitHub, Render, Cloudflare, Supabase (61 tools total)

**Focus**:
- Git workflows
- Deployment pipelines
- DNS record types
- Database query patterns

### Phase 4: Remaining Platforms (Week 4)
**Target**: Any remaining tools

---

## Quality Checklist

For each tool, ensure:

- [ ] **One-line summary** at top (not generic placeholder)
- [ ] **Usage instructions** (when to use, what problem it solves)
- [ ] **Parameter explanations** (format, examples, validation)
- [ ] **Workflow/process** (step-by-step if multi-step)
- [ ] **Syntax examples** (if tool has special formatting)
- [ ] **Real example** (with actual parameter values)
- [ ] **Return value explanations** (what each field means, how to use)
- [ ] **Error handling** (common errors and fixes)
- [ ] **Related tools** (what to use before/after)

**Remove:**
- ❌ Generic "Example response: Created: **New Document**" placeholders
- ❌ Copy-pasted example responses from other tools
- ❌ Vague descriptions without usage context

---

## Benefits of Comprehensive Tool Schemas

### For AI Agents
✅ **Knows when to use tool** (clear use cases)  
✅ **Uses correct parameter formats** (examples shown)  
✅ **Handles errors properly** (error patterns documented)  
✅ **Chains tools correctly** (related tools listed)  
✅ **Explains results to users** (return values explained)

### For Developers
✅ **Less debugging** (parameters are clear)  
✅ **Faster integration** (workflows documented)  
✅ **Better error messages** (AI knows what went wrong)  
✅ **Self-documenting** (schema is the documentation)

### For Users
✅ **Better responses** (AI understands tool fully)  
✅ **Fewer errors** (correct usage patterns)  
✅ **Clear explanations** (AI can describe what it's doing)  
✅ **Predictable behavior** (consistent tool usage)

---

## Next Steps

1. **Start with Stripe** (9 tools, high business value)
2. **Create updated schemas** following Google Docs pattern
3. **Test with AI agent** (verify improved understanding)
4. **Document patterns** (reusable templates for other platforms)
5. **Roll out incrementally** (validate before full deployment)

---

## Status

- ✅ **Automation tools** - Comprehensive platform guide + per-tool instructions (COMPLETE)
- ✅ **Google Docs** - Smart markdown tools already excellent (REFERENCE)
- ⏳ **Stripe** - Needs comprehensive instructions (NEXT)
- ⏳ **Slack** - Needs comprehensive instructions
- ⏳ **Twilio** - Needs comprehensive instructions
- ⏳ **55+ other platforms** - Varying quality, need review

**Goal**: Match Google Docs smart markdown tool quality across ALL 767 tools.
