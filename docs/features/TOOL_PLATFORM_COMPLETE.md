# 🔧 Tool Platform - Complete Documentation

## Overview

The Tool Platform provides 281+ integrated tools across 19+ platforms, enabling AI agents to perform real-world actions like sending emails, managing e-commerce, accessing Google Workspace, and more.

**Key Features:**
- 281+ tools across 19+ platforms
- Centralized tool registry & discovery
- Automatic tool execution during agent conversations
- Platform-specific authentication handling
- Error handling & retry logic
- Tool usage tracking & logging

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Supported Platforms](#supported-platforms)
3. [Tool Registry](#tool-registry)
4. [Tool Execution](#tool-execution)
5. [Adding New Tools](#adding-new-tools)
6. [Platform Integration](#platform-integration)
7. [Authentication](#authentication)
8. [Usage Examples](#usage-examples)
9. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### Component Structure

```
tools/
├── registry.py                    #  Tool discovery & execution engine
├── implementations/               # Platform-specific tool implementations
│   ├── gmail_tools.py            # 29 Gmail tools
│   ├── slack_tools.py            # 24 Slack tools
│   ├── woocommerce_tools.py      # 29 WooCommerce tools
│   ├── google_docs_tools.py      # Google Docs integration
│   ├── google_sheets_tools.py    # Google Sheets integration
│   └── [other platforms...]
├── microsoft_*.py                 # Microsoft 365 tools (10 modules)
└── schemas/                       # Tool parameter schemas
```

### Tool Registry Pattern

```python
# Central registry for all tools
class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self.load_all_tools()
    
    def register_tool(self, name, platform, function, description, parameters):
        """Register a tool for AI use"""
        self.tools[name] = {
            'name': name,
            'platform': platform,
            'function': function,
            'description': description,
            'parameters': parameters
        }
    
    def execute_tool(self, name, input_data):
        """Execute a tool by name"""
        tool = self.tools.get(name)
        if not tool:
            raise ValueError(f"Tool {name} not found")
        
        return tool['function'](**input_data)
```

---

## Supported Platforms

### Platform Breakdown

| Platform | Tools | Category | Authentication |
|----------|-------|----------|----------------|
| **Gmail** | 29 | Communication | OAuth 2.0 |
| **Slack** | 24 | Communication | OAuth 2.0 |
| **WooCommerce** | 29 | E-commerce | API Key |
| **Google Docs** | 18 | Productivity | OAuth 2.0 |
| **Google Sheets** | 22 | Productivity | OAuth 2.0 |
| **Google Forms** | 15 | Productivity | OAuth 2.0 |
| **Google Drive** | 20 | Storage | OAuth 2.0 |
| **Google Calendar** | 16 | Productivity | OAuth 2.0 |
| **Google Tasks** | 12 | Productivity | OAuth 2.0 |
| **Google Slides** | 14 | Productivity | OAuth 2.0 |
| **Google Meet** | 8 | Communication | OAuth 2.0 |
| **Microsoft Word** | 15 | Productivity | OAuth 2.0 |
| **Microsoft Excel** | 18 | Productivity | OAuth 2.0 |
| **Microsoft Outlook** | 20 | Communication | OAuth 2.0 |
| **Microsoft Teams** | 16 | Communication | OAuth 2.0 |
| **Microsoft OneDrive** | 14 | Storage | OAuth 2.0 |
| **Stripe** | 25 | E-commerce | API Key |
| **Supabase** | 12 | Database | API Key |
| **GitHub** | 18 | Development | OAuth 2.0 |

**Total:** 281+ tools across 19+ platforms

---

## Tool Registry

### Initialization

```python
from tools.registry import ToolRegistry

# Initialize registry (auto-loads all tools)
registry = ToolRegistry()

print(f" Loaded {len(registry.tools)} tools")
# Output:  Loaded 281 tools
```

### Listing Tools

```python
# List all tools
all_tools = registry.list_tools()

# Get tools by platform
gmail_tools = registry.get_tools_by_platform('gmail')
print(f"Gmail tools: {len(gmail_tools)}")
# Output: Gmail tools: 29

# Search tools by keyword
email_tools = registry.search_tools('email')
```

### Tool Structure

Each tool has the following structure:

```python
{
    "name": "gmail_send",
    "platform": "gmail",
    "description": "Send an email via Gmail",
    "parameters": {
        "to": {
            "type": "string",
            "description": "Recipient email address"
        },
        "subject": {
            "type": "string",
            "description": "Email subject"
        },
        "body": {
            "type": "string",
            "description": "Email body (HTML supported)"
        },
        "cc": {
            "type": "string",
            "description": "CC recipients (optional)",
            "required": false
        }
    },
    "function": <callable>
}
```

---

## Tool Execution

### Automatic Execution (via AI Agent)

Tools are automatically executed when the AI decides to use them:

```javascript
// User asks agent to send email
const response = await fetch('http://localhost:4000/api/agent/data-agent/start', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({
        message: "Send an email to john@example.com with subject 'Meeting' and body 'See you tomorrow'"
    })
});

// Agent will:
// 1. Understand the request
// 2. Choose gmail_send tool
// 3. Extract parameters
// 4. Execute tool
// 5. Return result
```

### Manual Execution

```python
from tools.registry import ToolRegistry

registry = ToolRegistry()

# Execute tool directly
result = registry.execute_tool('gmail_send', {
    'to': 'john@example.com',
    'subject': 'Test Email',
    'body': 'This is a test'
})

print(result)
# Output: {'success': True, 'message_id': 'msg-123'}
```

### Execution Flow

```
1. AI decides to use tool
   ↓
2. Agent worker extracts tool name & parameters
   ↓
3. ToolRegistry.execute_tool() called
   ↓
4. Authentication checked (OAuth/API key)
   ↓
5. Tool function executed
   ↓
6. Result returned to AI
   ↓
7. AI continues with result
   ↓
8. Response streamed to client
```

### Error Handling

```python
try:
    result = registry.execute_tool('gmail_send', {
        'to': 'invalid-email',
        'subject': 'Test'
    })
except ToolExecutionError as e:
    print(f"Tool failed: {e}")
    # Log error, retry, or fallback
```

---

## Adding New Tools

### Step 1: Create Tool Implementation

Create file: `tools/implementations/my_platform_tools.py`

```python
"""
My Platform Tools
Description of what this platform does
"""

def my_tool_action(param1, param2):
    """
    Do something on my platform
    
    Args:
        param1 (str): Description
        param2 (int): Description
    
    Returns:
        dict: Result with success status
    """
    # Your implementation
    result = perform_action(param1, param2)
    
    return {
        "success": True,
        "data": result
    }
```

### Step 2: Register Tool

In the same file:

```python
from tools.registry import ToolRegistry

def register_tools(registry: ToolRegistry):
    """Register all tools for this platform"""
    
    registry.register_tool(
        name="my_platform_action",
        platform="my_platform",
        function=my_tool_action,
        description="Do something on my platform",
        parameters={
            "param1": {
                "type": "string",
                "description": "First parameter",
                "required": True
            },
            "param2": {
                "type": "integer",
                "description": "Second parameter",
                "required": True
            }
        }
    )

# Auto-register on import
_registry = ToolRegistry()
register_tools(_registry)
```

### Step 3: Import in Registry

Edit `tools/registry.py`:

```python
class ToolRegistry:
    def load_all_tools(self):
        """Load tools from all platforms"""
        from tools.implementations import gmail_tools
        from tools.implementations import slack_tools
        from tools.implementations import my_platform_tools  #  Add this
        
        # Tools auto-register on import
        print(f" Loaded {len(self.tools)} tools")
```

### Step 4: Test Tool

```python
from tools.registry import ToolRegistry

registry = ToolRegistry()

# Verify tool loaded
tool = registry.get_tool('my_platform_action')
print(f"Tool: {tool['description']}")

# Test execution
result = registry.execute_tool('my_platform_action', {
    'param1': 'test',
    'param2': 42
})

print(f"Result: {result}")
```

---

## Platform Integration

### Gmail Integration

**Available Tools:**
- `gmail_send` - Send email
- `gmail_list` - List emails
- `gmail_read` - Read email
- `gmail_search` - Search emails
- `gmail_delete` - Delete email
- `gmail_create_draft` - Create draft
- `gmail_send_draft` - Send draft
- ... (29 total)

**Example:**

```python
# Send email via AI
message = "Send an email to team@company.com with subject 'Weekly Update' and attach the sales report"

# AI will use gmail_send tool automatically
```

---

### WooCommerce Integration

**Available Tools:**
- `woocommerce_list_products` - List products
- `woocommerce_create_product` - Create product
- `woocommerce_update_product` - Update product
- `woocommerce_delete_product` - Delete product
- `woocommerce_list_orders` - List orders
- `woocommerce_get_order` - Get order details
- `woocommerce_update_order_status` - Update order status
- ... (29 total)

**Example:**

```python
# Manage store via AI
message = "List all orders from the last 7 days and update any pending orders to processing"

# AI will use woocommerce_list_orders and woocommerce_update_order_status
```

---

### Google Workspace Integration

**Google Docs (18 tools):**
- Create, read, update, delete documents
- Format text (bold, italic, headings)
- Insert tables, images, links
- Manage permissions

**Google Sheets (22 tools):**
- Create, read, update spreadsheets
- Read/write ranges
- Format cells
- Create charts
- Run formulas

**Google Forms (15 tools):**
- Create forms
- Add questions (multiple choice, text, etc.)
- Manage responses
- Send forms

**Example:**

```python
# Complex workflow via AI
message = """
Create a Google Doc titled 'Q4 Report' with:
1. A heading 'Sales Summary'
2. A table with product names and sales
3. Then create a Google Sheet with the same data
4. Add a chart showing trends
"""

# AI will orchestrate multiple tools across platforms
```

---

### Microsoft 365 Integration

**Microsoft Word (15 tools):**
- Create, read, update documents
- Format text & paragraphs
- Insert tables, images

**Microsoft Excel (18 tools):**
- Manage workbooks & worksheets
- Read/write ranges
- Create charts & formulas

**Microsoft Outlook (20 tools):**
- Send/read emails
- Manage calendar events
- Create tasks

**Microsoft Teams (16 tools):**
- Send messages to channels
- Create teams & channels
- Manage members

**Example:**

```python
# Cross-platform workflow
message = """
1. Get the latest sales data from Excel
2. Create a Word document with the analysis
3. Send it via Outlook to the management team
4. Post a summary in the Teams sales channel
"""

# AI orchestrates across all Microsoft tools
```

---

## Authentication

### OAuth 2.0 Platforms

**Google Workspace:**
```python
# OAuth handled automatically via google_auth_routes.py
# User logs in once, token stored securely
```

**Microsoft 365:**
```python
# OAuth handled automatically via microsoft_auth_routes.py
# User logs in once, token stored securely
```

**Slack:**
```python
# OAuth handled via Slack app configuration
# Workspace token used for all tools
```

### API Key Platforms

**WooCommerce:**
```python
# API credentials in .env
WOOCOMMERCE_URL=https://yourstore.com
WOOCOMMERCE_KEY=ck_xxx
WOOCOMMERCE_SECRET=cs_xxx
```

**Stripe:**
```python
# API key in .env
STRIPE_API_KEY=sk_test_xxx
```

**Supabase:**
```python
# API credentials in .env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
```

---

## Usage Examples

### Example 1: Send Email

```javascript
// Via AI agent
const response = await fetch('http://localhost:4000/api/agent/data-agent/start', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({
        message: "Send an email to john@example.com saying 'Meeting at 3pm tomorrow'"
    })
});

// AI uses gmail_send tool
// Result streamed back via SSE
```

### Example 2: Manage E-commerce

```javascript
const response = await fetch('http://localhost:4000/api/agent/data-agent/start', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({
        message: "Show me all pending orders and update them to processing"
    })
});

// AI uses:
// 1. woocommerce_list_orders (filter: status=pending)
// 2. woocommerce_update_order_status (for each order)
```

### Example 3: Document Creation

```javascript
const response = await fetch('http://localhost:4000/api/agent/data-agent/start', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({
        message: "Create a Google Doc titled 'Meeting Notes' with today's date as heading"
    })
});

// AI uses:
// 1. google_docs_create
// 2. google_docs_insert_text
// 3. google_docs_format_text
```

### Example 4: Multi-Platform Workflow

```javascript
const response = await fetch('http://localhost:4000/api/agent/data-agent/start', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({
        message: `
            1. Get WooCommerce sales data from last month
            2. Create a Google Sheet with the data
            3. Generate a chart showing trends
            4. Create a Google Doc summarizing findings
            5. Email the doc to management@company.com
        `
    })
});

// AI orchestrates:
// woocommerce_list_orders → google_sheets_create → 
// google_sheets_create_chart → google_docs_create → gmail_send
```

---

## Troubleshooting

### Issue: Tool Not Found

**Symptoms:** Error "Tool xyz not found"

**Solutions:**
1. List available tools:
```bash
curl http://localhost:4000/api/agent/tools
```

2. Check tool registry:
```python
from tools.registry import ToolRegistry
registry = ToolRegistry()
print([t['name'] for t in registry.list_tools()])
```

3. Verify tool is imported in `registry.py`

---

### Issue: Authentication Error

**Symptoms:** "OAuth token expired" or "Invalid API key"

**Solutions:**

**For OAuth (Google/Microsoft/Slack):**
1. Re-authenticate:
```javascript
// Redirect to OAuth flow
window.location.href = 'http://localhost:4000/api/auth/google/authorize';
```

2. Check token expiration:
```python
# In Flask
from routes.google_auth_routes import check_token_expiry
is_valid = check_token_expiry(user_id)
```

**For API Keys (WooCommerce/Stripe):**
1. Verify .env file:
```bash
cat .env | grep WOOCOMMERCE
```

2. Test API key directly:
```python
import os
from tools.implementations.woocommerce_tools import test_connection

result = test_connection()
print(result)
```

---

### Issue: Tool Execution Timeout

**Symptoms:** Tool takes too long, SSE disconnects

**Solutions:**
1. Increase timeout in tool implementation:
```python
def my_slow_tool(param):
    import requests
    response = requests.get(url, timeout=30)  # Increase from default 10
    return response.json()
```

2. Implement async execution:
```python
import asyncio

async def my_async_tool(param):
    # Async implementation
    result = await fetch_data(param)
    return result
```

---

### Issue: Tool Returns Error

**Symptoms:** tool_result shows error

**Solutions:**
1. Check tool logs:
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. Test tool directly:
```python
result = registry.execute_tool('tool_name', {'param': 'value'})
if not result.get('success'):
    print(f"Error: {result.get('error')}")
```

3. Validate input parameters:
```python
tool = registry.get_tool('tool_name')
print(f"Required params: {tool['parameters']}")
```

---

## Performance

### Metrics

**Typical Performance:**
- Tool execution: 100-2000ms (varies by platform)
- Gmail tools: 200-800ms
- Google Docs/Sheets: 300-1000ms
- WooCommerce: 500-2000ms
- Local tools: < 100ms

### Optimization Tips

1. **Batch operations** when possible
2. **Cache frequently accessed data**
3. **Use async tools** for I/O-bound operations
4. **Limit result sizes** (pagination)
5. **Monitor rate limits** per platform

---

## Platform-Specific Notes

### Google Workspace

- **Rate Limits:** 100 requests/100 seconds per user
- **Quota:** 1,500 requests/day (default)
- **Best Practices:** Batch requests, use conditional updates

### Microsoft 365

- **Rate Limits:** Varies by service (typically 2000/hour)
- **Quota:** Service-specific
- **Best Practices:** Use delta queries, batch requests

### WooCommerce

- **Rate Limits:** Depends on hosting
- **Quota:** Usually unlimited
- **Best Practices:** Use filtering, limit page sizes

---

**Last Updated:** October 29, 2025  
**Version:** 2.0.0  
**Status:**  Production Ready
