# Tool Library Architecture - Comprehensive Analysis

**Date:** November 23, 2025  
**Author:** System Architecture Analysis  
**Status:** Production - 594+ Tools Active

---

## Executive Summary

The AI Agents platform features a **sophisticated, modular tool library architecture** that enables:

- ✅ **594+ tools** across 20+ platforms (Google, Microsoft, Stripe, Xero, Shopify, etc.)
- ✅ **Plug-and-play integration** - Drop files → tools auto-discover → ready to use
- ✅ **Zero manual registration** - No code changes needed for new platforms
- ✅ **Credential injection** - Automatic OAuth token injection at runtime
- ✅ **Multi-format support** - JSON schemas, Python implementations, flexible patterns
- ✅ **Backward compatible** - Legacy and modern patterns coexist

This document provides a **complete architectural breakdown** for understanding and extending the system.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Tool Loading Process](#tool-loading-process)
4. [Platform Integration Patterns](#platform-integration-patterns)
5. [Adding New Platforms (Step-by-Step)](#adding-new-platforms-step-by-step)
6. [Module Plugin System](#module-plugin-system)
7. [Credential Injection System](#credential-injection-system)
8. [Real-World Examples](#real-world-examples)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI AGENTS TOOL LIBRARY                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────┐      ┌────────────────┐                    │
│  │ Tool Schemas  │      │ Implementations│                    │
│  │  (JSON)       │      │    (Python)    │                    │
│  ├───────────────┤      ├────────────────┤                    │
│  │ 60+ files     │──┬──→│ 45+ modules    │                    │
│  │ tools/schemas/│  │   │ tools/impl/    │                    │
│  └───────────────┘  │   │ google_ws/     │                    │
│                     │   │ UI/modules/    │                    │
│                     │   └────────────────┘                    │
│                     │            ↓                             │
│                     │   ┌────────────────┐                    │
│                     └──→│  RegistryV3    │                    │
│                         │  (Orchestrator)│                    │
│                         └────────┬───────┘                    │
│                                  ↓                             │
│                         ┌────────────────┐                    │
│                         │ 594+ Tools     │                    │
│                         │ Loaded & Ready │                    │
│                         └────────┬───────┘                    │
│                                  ↓                             │
│                         ┌────────────────┐                    │
│                         │ AI Agent       │                    │
│                         │ Can Execute    │                    │
│                         └────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

### Key Principles

1. **Separation of Concerns**
   - **Schemas** define tool interface (what AI sees)
   - **Implementations** contain business logic (what tool does)
   - **Registry** connects schemas to implementations (orchestration)

2. **Automatic Discovery**
   - Drop JSON schema → tool appears to AI
   - Drop Python module → implementation available
   - No manual registration needed

3. **Flexible Patterns**
   - Supports multiple implementation styles
   - Works with classes, functions, modules
   - Backward compatible with legacy code

4. **Runtime Credential Injection**
   - No credentials in code
   - OAuth tokens injected at execution time
   - Per-user credential isolation

---

## Core Components

### 1. Registry V3 (The Orchestrator)

**File:** `tools/registry_v3.py` (787 lines)

**Purpose:** Central orchestration system that loads, organizes, and executes all tools.

**Key Responsibilities:**

```python
class RegistryV3:
    def __init__(self):
        self.tools = {}              # 594+ tool schemas
        self.implementations = {}    # Python modules/functions
        
        self._load_schemas()         # Load JSON definitions
        self._load_implementations() # Load Python code
        self._load_module_plugins()  # Load UI modules (optional)
    
    def execute_tool(self, tool_name, **kwargs):
        """Execute any tool with credential injection"""
        # 1. Get tool function
        # 2. Inject OAuth credentials
        # 3. Execute and return result
```

**Loading Priority (Critical!):**

```
1. google_workspace/          ← PRIMARY for Google tools (12 modules)
2. tools/implementations/     ← FALLBACK for other platforms (45+ modules)
3. UI/external/modules/       ← PLUGINS (optional, auto-discovered)
```

**Why this order?**
- Google tools have special integration needs
- Direct loading from `google_workspace/` ensures proper credential handling
- Other platforms use standard pattern in `tools/implementations/`
- Plugin modules are optional and discovered last

### 2. Tool Schemas (JSON Definitions)

**Location:** `tools/schemas/` (60+ JSON files)

**Purpose:** Define tool interface for AI agents in Anthropic Claude format.

**Structure:**

```json
{
  "platform": "platform_name",
  "description": "What this platform does",
  "tools": [
    {
      "name": "tool_function_name",
      "description": "Clear description for AI (include examples, use cases)",
      "platform": "platform_name",
      "parameters": {
        "type": "object",
        "properties": {
          "param_name": {
            "type": "string|integer|boolean|array|object",
            "description": "Parameter description",
            "required": true|false,
            "default": "optional_default"
          }
        },
        "required": ["param1", "param2"]
      },
      "returns": {
        "type": "object",
        "description": "What the tool returns"
      },
      "examples": [
        {
          "description": "Example use case",
          "parameters": { "param1": "value" }
        }
      ]
    }
  ]
}
```

**Example Platforms:**

```
tools/schemas/
├── google_sheets_tools.json       ← 15 Google Sheets tools
├── microsoft_outlook_tools.json   ← 12 Outlook tools
├── stripe_tools.json              ← 9 Stripe payment tools
├── xero_tools.json                ← 15 Xero accounting tools
├── calculator_tools.json          ← 7 InHouse Print calculators
├── automation_tools.json          ← 8 workflow automation tools
├── synergy_tools.json             ← 12 project management tools
└── ... (60+ total)
```

**Critical Fields:**

- `name` - **Exact function name** to call (must match implementation)
- `description` - **Rich, detailed** explanation for AI (include examples!)
- `parameters.type` - Must be "object" (Anthropic requirement)
- `parameters.properties` - Individual parameter definitions
- `parameters.required` - Array of required parameter names

### 3. Tool Implementations (Python Code)

**Locations:**
- `google_workspace/` - 12 Google platform modules
- `tools/implementations/` - 45+ other platform modules
- `UI/external/modules/*/implementations/` - Plugin modules

**Purpose:** Business logic that executes when AI calls a tool.

**Implementation Patterns:**

#### Pattern A: Direct Functions (Simple)

```python
# tools/implementations/stripe.py

def stripe_create_customer(email: str, name: str = None, **kwargs) -> dict:
    """
    Create Stripe customer
    
    Args:
        email: Customer email
        name: Optional customer name
        **kwargs: Credential injection
    
    Returns:
        Customer object with ID
    """
    # Get credentials
    stripe_api_key = kwargs.get('stripe_api_key')
    
    # Execute business logic
    import stripe
    stripe.api_key = stripe_api_key
    
    customer = stripe.Customer.create(
        email=email,
        name=name
    )
    
    return {
        'success': True,
        'customer_id': customer.id,
        'email': customer.email
    }
```

#### Pattern B: Class-Based (Microsoft Pattern)

```python
# tools/implementations/microsoft_outlook_tools.py

class MicrosoftOutlookTools:
    """Microsoft Outlook tool implementations"""
    
    def __init__(self):
        self.credentials = None
    
    def outlook_send_email(
        self, 
        to: str, 
        subject: str, 
        body: str,
        **kwargs
    ) -> dict:
        """Send email via Outlook"""
        # Extract credentials
        access_token = kwargs.get('access_token')
        
        # Call Microsoft Graph API
        import requests
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            'https://graph.microsoft.com/v1.0/me/sendMail',
            headers=headers,
            json={'message': {...}, 'saveToSentItems': True}
        )
        
        return {'success': True, 'message_id': ...}

# Create global instance (required for registry!)
microsoft_outlook_tools = MicrosoftOutlookTools()

# Export module-level functions (registry looks for these)
def microsoft_outlook_send_email(**kwargs):
    return microsoft_outlook_tools.outlook_send_email(**kwargs)
```

**Why this pattern?**
- Class encapsulates related functionality
- Global instance allows stateful operation
- Module-level functions provide clean interface
- Registry finds `microsoft_outlook_send_email()` function

#### Pattern C: Module with Multiple Functions (Google Pattern)

```python
# google_workspace/gmail.py

def gmail_send_email(to: str, subject: str, body: str, **kwargs) -> dict:
    """Send email via Gmail"""
    # Implementation
    pass

def gmail_list_messages(max_results: int = 10, **kwargs) -> list:
    """List Gmail messages"""
    # Implementation
    pass

def gmail_get_message(message_id: str, **kwargs) -> dict:
    """Get single message"""
    # Implementation
    pass

# No class needed - just functions
# Registry imports module and calls functions directly
```

### 4. Credential Injection System

**File:** `AI_infrastructure/auth/credential_injector.py`

**Purpose:** Inject OAuth tokens and API keys at runtime (not stored in code).

**How It Works:**

```python
# In agent_worker.py (execution flow)

# 1. User requests tool execution
user_id = 1
tool_name = "gmail_send_email"
params = {"to": "test@example.com", "subject": "Hi"}

# 2. Credential injector fetches user's OAuth tokens
injector = CredentialInjector()
credentials = injector.get_google_credentials(user_id)
# Returns: {'access_token': 'ya29.a0...', 'refresh_token': '...'}

# 3. Registry executes tool WITH credentials
result = registry.execute_tool(
    tool_name="gmail_send_email",
    to="test@example.com",
    subject="Hi",
    _user_id=user_id,                    # User ID for permission checks
    _injected_credentials=credentials    # OAuth tokens (not in params!)
)

# 4. Tool implementation extracts credentials
def gmail_send_email(to, subject, **kwargs):
    access_token = kwargs.get('access_token')  # ← Injected credential
    # Use token for Gmail API call
```

**Database Storage:**

```sql
-- user_platform_credentials table
CREATE TABLE user_platform_credentials (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,         -- 'google', 'microsoft', etc.
    access_token TEXT NOT NULL,     -- OAuth access token
    refresh_token TEXT,             -- OAuth refresh token
    token_expiry TIMESTAMP,         -- Token expiration
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Platform Patterns:**

| Platform | Credential Type | Injected As | Example |
|----------|----------------|-------------|---------|
| Google | OAuth 2.0 | `access_token`, `refresh_token` | Gmail, Sheets, Drive |
| Microsoft | OAuth 2.0 | `access_token` | Outlook, Word, Excel |
| Stripe | API Key | `stripe_api_key` | Payments, customers |
| Xero | OAuth 2.0 | `access_token`, `tenant_id` | Invoices, contacts |

---

## Tool Loading Process

### Complete Loading Sequence

```
Step 1: Initialize Registry
    ├─ Create empty tools {} dict
    ├─ Create empty implementations {} dict
    └─ Set up directory paths

Step 2: Load Schemas (_load_schemas)
    ├─ Scan tools/schemas/ for *.json files (60+ files)
    ├─ For each schema file:
    │   ├─ Parse JSON with UTF-8 encoding
    │   ├─ Extract platform name
    │   ├─ For each tool in "tools" array:
    │   │   ├─ Set tool["platform"] = schema platform
    │   │   └─ Add to self.tools[tool_name] = tool
    │   └─ Log loaded tools
    └─ Result: 594+ tools in self.tools

Step 3: Load Google Workspace Implementations (_load_from_google_workspace)
    ├─ Import from google_workspace/ directory
    ├─ Load 12 Google modules:
    │   ├─ google_workspace.gmail
    │   ├─ google_workspace.google_docs
    │   ├─ google_workspace.google_sheets
    │   ├─ google_workspace.google_drive
    │   ├─ google_workspace.google_calendar
    │   ├─ google_workspace.google_tasks
    │   ├─ google_workspace.google_slides
    │   ├─ google_workspace.google_meet
    │   ├─ google_workspace.google_analytics
    │   ├─ google_workspace.google_cloud_run
    │   ├─ google_workspace.google_forms
    │   └─ google_workspace.google_auth_helper
    └─ Result: Google tools loaded (PRIMARY source)

Step 4: Load Other Implementations (_load_from_implementations)
    ├─ Scan tools/implementations/ for *.py files (45+ files)
    ├─ Special handling for:
    │   ├─ sql_database.py (register individual functions)
    │   └─ meta_tools.py (register individual functions)
    ├─ For each module:
    │   ├─ Import module
    │   ├─ Extract class instance (if Microsoft pattern)
    │   ├─ Add to self.implementations[module_name]
    │   └─ Log available functions
    └─ Result: All non-Google tools loaded

Step 5: Load Module Plugins (_load_module_plugins)
    ├─ Call module_plugin_loader.py
    ├─ Discover UI/external/modules/* with schema/ + implementations/
    ├─ Load plugin schemas (JSON)
    ├─ Load plugin implementations (Python)
    ├─ Add to self.tools and self.implementations
    └─ Result: Plugin tools available (calculator, stock, etc.)

Step 6: Ready for Execution
    ├─ Total: 594+ tools loaded
    ├─ 35+ implementation modules
    ├─ 20+ platforms integrated
    └─ AI agents can discover and execute tools
```

### Loading Priority Examples

**Example 1: Gmail Tool**

```
Tool Schema:
  tools/schemas/gmail_tools.json
  → defines "gmail_send_email"

Implementation Search:
  1. Check google_workspace/gmail.py ✅ FOUND (PRIMARY)
  2. (Skip tools/implementations/ - already found)

Result:
  gmail_send_email → google_workspace.gmail.gmail_send_email()
```

**Example 2: Stripe Tool**

```
Tool Schema:
  tools/schemas/stripe_tools.json
  → defines "stripe_create_customer"

Implementation Search:
  1. Check google_workspace/ ❌ NOT FOUND (not a Google tool)
  2. Check tools/implementations/stripe.py ✅ FOUND

Result:
  stripe_create_customer → tools.implementations.stripe.stripe_create_customer()
```

**Example 3: Calculator Tool (Plugin)**

```
Tool Schema:
  UI/external/modules/calculator-module/schema/calculator_tools.json
  → defines "calculate_flyers"

Implementation Search:
  1. Check google_workspace/ ❌ NOT FOUND
  2. Check tools/implementations/ ❌ NOT FOUND
  3. Check plugin loader ✅ FOUND

Result:
  calculate_flyers → calculator_module.calculator_wrapper.calculate_flyers()
```

---

## Platform Integration Patterns

### Pattern 1: Simple Function-Based (Easiest)

**Best for:** Simple APIs, single-purpose tools, stateless operations

**Example:** Stripe, Twilio, Resend

**Implementation:**

```python
# tools/implementations/stripe.py

def stripe_create_customer(email: str, name: str = None, **kwargs) -> dict:
    """Create Stripe customer"""
    stripe_api_key = kwargs.get('stripe_api_key')
    
    import stripe
    stripe.api_key = stripe_api_key
    
    customer = stripe.Customer.create(email=email, name=name)
    return {'success': True, 'customer_id': customer.id}

def stripe_create_payment_intent(amount: int, currency: str = 'usd', **kwargs) -> dict:
    """Create payment intent"""
    stripe_api_key = kwargs.get('stripe_api_key')
    
    import stripe
    stripe.api_key = stripe_api_key
    
    intent = stripe.PaymentIntent.create(amount=amount, currency=currency)
    return {'success': True, 'intent_id': intent.id}

# ... more functions
```

**Schema:**

```json
{
  "platform": "stripe",
  "tools": [
    {
      "name": "stripe_create_customer",
      "description": "Create a new Stripe customer",
      "parameters": {
        "type": "object",
        "properties": {
          "email": {"type": "string", "description": "Customer email"},
          "name": {"type": "string", "description": "Customer name"}
        },
        "required": ["email"]
      }
    }
  ]
}
```

**Pros:**
- ✅ Simple and straightforward
- ✅ Easy to understand
- ✅ No boilerplate code

**Cons:**
- ❌ No shared state between functions
- ❌ Credential handling repeated in each function

### Pattern 2: Class-Based with Global Instance (Microsoft)

**Best for:** Stateful operations, shared configuration, complex APIs

**Example:** Microsoft Outlook, Word, Excel

**Implementation:**

```python
# tools/implementations/microsoft_outlook_tools.py

class MicrosoftOutlookTools:
    """Microsoft Outlook API wrapper"""
    
    def __init__(self):
        self.base_url = 'https://graph.microsoft.com/v1.0'
        self.credentials = None
    
    def _get_headers(self, access_token: str) -> dict:
        """Shared header builder"""
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def outlook_send_email(self, to: str, subject: str, body: str, **kwargs) -> dict:
        """Send email"""
        access_token = kwargs.get('access_token')
        headers = self._get_headers(access_token)
        
        import requests
        response = requests.post(
            f'{self.base_url}/me/sendMail',
            headers=headers,
            json={'message': {...}}
        )
        
        return {'success': True}
    
    def outlook_list_messages(self, max_results: int = 50, **kwargs) -> list:
        """List messages"""
        access_token = kwargs.get('access_token')
        headers = self._get_headers(access_token)
        
        import requests
        response = requests.get(
            f'{self.base_url}/me/messages',
            headers=headers,
            params={'$top': max_results}
        )
        
        return response.json()['value']

# CRITICAL: Create global instance
microsoft_outlook_tools = MicrosoftOutlookTools()

# CRITICAL: Export module-level wrapper functions
def microsoft_outlook_send_email(**kwargs):
    """Wrapper for registry"""
    return microsoft_outlook_tools.outlook_send_email(**kwargs)

def microsoft_outlook_list_messages(**kwargs):
    """Wrapper for registry"""
    return microsoft_outlook_tools.outlook_list_messages(**kwargs)
```

**Schema:**

```json
{
  "platform": "microsoft_outlook",
  "tools": [
    {
      "name": "microsoft_outlook_send_email",
      "description": "Send email via Outlook",
      "parameters": {...}
    },
    {
      "name": "microsoft_outlook_list_messages",
      "description": "List Outlook messages",
      "parameters": {...}
    }
  ]
}
```

**Pros:**
- ✅ Shared configuration (base_url, etc.)
- ✅ Reusable helper methods (_get_headers)
- ✅ Stateful operations possible
- ✅ Clean separation of concerns

**Cons:**
- ❌ More boilerplate (wrappers needed)
- ❌ Two-layer structure (class + wrappers)

### Pattern 3: Module with Functions (Google)

**Best for:** Platform with many related tools, direct function access

**Example:** Gmail, Google Sheets, Google Drive

**Implementation:**

```python
# google_workspace/gmail.py

def gmail_send_email(to: str, subject: str, body: str, **kwargs) -> dict:
    """Send email via Gmail"""
    access_token = kwargs.get('access_token')
    
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    
    creds = Credentials(token=access_token)
    service = build('gmail', 'v1', credentials=creds)
    
    message = {...}  # Build message
    result = service.users().messages().send(userId='me', body=message).execute()
    
    return {'success': True, 'message_id': result['id']}

def gmail_list_messages(max_results: int = 10, **kwargs) -> list:
    """List Gmail messages"""
    access_token = kwargs.get('access_token')
    
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    
    creds = Credentials(token=access_token)
    service = build('gmail', 'v1', credentials=creds)
    
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    return results.get('messages', [])

def gmail_get_message(message_id: str, **kwargs) -> dict:
    """Get single message"""
    # Implementation
    pass

# ... 12 more Gmail functions
```

**Schema:**

```json
{
  "platform": "gmail",
  "tools": [
    {"name": "gmail_send_email", ...},
    {"name": "gmail_list_messages", ...},
    {"name": "gmail_get_message", ...}
  ]
}
```

**Pros:**
- ✅ Direct function access (no wrappers)
- ✅ Clean, simple code
- ✅ Easy to add new functions

**Cons:**
- ❌ Credential handling repeated
- ❌ No shared state between functions

### Pattern 4: Plugin Module (Modular)

**Best for:** External integrations, optional features, third-party systems

**Example:** InHouse Print Calculator, Stock Management

**Structure:**

```
UI/external/modules/calculator-module/
├── schema/
│   └── calculator_tools.json           ← Tool definitions
├── implementations/
│   └── calculator_wrapper.py           ← Tool implementations
└── backend/
    └── calculator_wrapper.py           ← Business logic (called by wrapper)
```

**Implementation:**

```python
# UI/external/modules/calculator-module/implementations/calculator_wrapper.py

import sys
from pathlib import Path

# Add backend module to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from calculator_wrapper import QuoteCalculatorWrapper

# Initialize calculator
calculator = QuoteCalculatorWrapper()

def calculate_flyers(quantity: int, width: int, height: int, **kwargs) -> dict:
    """Calculate flyer quote"""
    try:
        result = calculator.calculate_flyers(
            quantity=quantity,
            width=width,
            height=height,
            ...
        )
        return result
    except Exception as e:
        return {'success': False, 'error': str(e)}

def calculate_business_cards(quantity: int, finish_size: str, **kwargs) -> dict:
    """Calculate business card quote"""
    # Implementation
    pass

# ... 5 more calculator functions
```

**Schema:**

```json
{
  "platform": "calculator",
  "tools": [
    {"name": "calculate_flyers", ...},
    {"name": "calculate_business_cards", ...}
  ]
}
```

**Auto-Discovery:**

```python
# tools/plugins/module_plugin_loader.py

class ModulePluginLoader:
    def discover_modules_with_tools(self):
        """Find modules with schema/ and implementations/"""
        for module_dir in self.modules_dir.iterdir():
            schema_dir = module_dir / "schema"
            impl_dir = module_dir / "implementations"
            
            if schema_dir.exists() and impl_dir.exists():
                # Module has tools! Load them.
                self.load_module_schemas(module_dir.name)
                self.load_module_implementations(module_dir.name)
```

**Pros:**
- ✅ Complete isolation (separate folder)
- ✅ Optional (remove folder = tools disappear)
- ✅ No main codebase changes needed
- ✅ Can include own dependencies

**Cons:**
- ❌ More complex folder structure
- ❌ Requires plugin loader system

---

## Adding New Platforms (Step-by-Step)

### Method 1: Standard Integration (Recommended)

**Use when:** Adding mainstream platforms (APIs, SaaS tools)

**Steps:**

#### Step 1: Create Tool Schema

**File:** `tools/schemas/my_platform_tools.json`

```json
{
  "platform": "my_platform",
  "description": "My Platform API - Description of what it does",
  "tools": [
    {
      "name": "my_platform_create_item",
      "description": "Create a new item in My Platform. Include detailed examples and use cases for AI.",
      "platform": "my_platform",
      "parameters": {
        "type": "object",
        "properties": {
          "title": {
            "type": "string",
            "description": "Item title (required)"
          },
          "description": {
            "type": "string",
            "description": "Item description (optional)"
          },
          "tags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of tags"
          }
        },
        "required": ["title"]
      },
      "returns": {
        "type": "object",
        "description": "Created item with ID and URL"
      },
      "examples": [
        {
          "description": "Create simple item",
          "parameters": {
            "title": "My Item",
            "description": "Item description"
          }
        }
      ]
    },
    {
      "name": "my_platform_list_items",
      "description": "List all items from My Platform",
      "platform": "my_platform",
      "parameters": {
        "type": "object",
        "properties": {
          "limit": {
            "type": "integer",
            "description": "Max items to return (default: 10)"
          }
        },
        "required": []
      },
      "returns": {
        "type": "array",
        "description": "List of items"
      }
    }
  ]
}
```

#### Step 2: Create Implementation

**File:** `tools/implementations/my_platform.py`

```python
"""
My Platform Tools - Integration with My Platform API

Functions:
- my_platform_create_item: Create items
- my_platform_list_items: List items
- my_platform_get_item: Get single item
- my_platform_update_item: Update item
- my_platform_delete_item: Delete item

FILE: tools/implementations/my_platform.py
PURPOSE: My Platform API wrapper for AI agents
DEPENDENCIES:
- requests (HTTP client)
- my_platform_sdk (optional, if SDK exists)
LAST MODIFIED: 2025-11-23 - Initial creation
"""

import requests
from typing import Dict, Any, List, Optional

class MyPlatformError(Exception):
    """Custom exception for My Platform errors"""
    pass


def my_platform_create_item(
    title: str,
    description: str = None,
    tags: List[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a new item in My Platform
    
    Args:
        title: Item title (required)
        description: Item description (optional)
        tags: List of tags (optional)
        **kwargs: Credential injection (api_key, access_token, etc.)
    
    Returns:
        Dict with item_id, title, url
    
    Raises:
        MyPlatformError: If creation fails
    """
    # CRITICAL: Extract credentials from kwargs (injected by credential_injector)
    api_key = kwargs.get('my_platform_api_key')
    if not api_key:
        raise MyPlatformError("my_platform_api_key required but not provided")
    
    # Build API request
    url = "https://api.myplatform.com/v1/items"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "title": title,
        "description": description or "",
        "tags": tags or []
    }
    
    # Make API call
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        return {
            "success": True,
            "item_id": data.get("id"),
            "title": data.get("title"),
            "url": data.get("url"),
            "created_at": data.get("created_at")
        }
    except requests.exceptions.RequestException as e:
        raise MyPlatformError(f"Failed to create item: {str(e)}")


def my_platform_list_items(
    limit: int = 10,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    List items from My Platform
    
    Args:
        limit: Max items to return (default: 10)
        **kwargs: Credential injection
    
    Returns:
        List of items with id, title, url
    
    Raises:
        MyPlatformError: If listing fails
    """
    # Extract credentials
    api_key = kwargs.get('my_platform_api_key')
    if not api_key:
        raise MyPlatformError("my_platform_api_key required")
    
    # Build request
    url = f"https://api.myplatform.com/v1/items?limit={limit}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Make API call
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        return [{
            "item_id": item.get("id"),
            "title": item.get("title"),
            "url": item.get("url"),
            "created_at": item.get("created_at")
        } for item in data.get("items", [])]
    except requests.exceptions.RequestException as e:
        raise MyPlatformError(f"Failed to list items: {str(e)}")


def my_platform_get_item(item_id: str, **kwargs) -> Dict[str, Any]:
    """Get single item by ID"""
    # Implementation
    pass


def my_platform_update_item(item_id: str, **kwargs) -> Dict[str, Any]:
    """Update item"""
    # Implementation
    pass


def my_platform_delete_item(item_id: str, **kwargs) -> Dict[str, Any]:
    """Delete item"""
    # Implementation
    pass
```

#### Step 3: Add Credential Support (If OAuth)

**File:** `AI_infrastructure/auth/credential_injector.py`

Add method to fetch credentials:

```python
def get_my_platform_credentials(self, user_id: int) -> Dict[str, str]:
    """Get My Platform credentials for user"""
    conn = self.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT access_token, api_key, token_expiry
        FROM user_platform_credentials
        WHERE user_id = ? AND platform = 'my_platform'
        ORDER BY updated_at DESC
        LIMIT 1
    """, (user_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        'my_platform_api_key': row[1],  # or access_token: row[0]
        'token_expiry': row[2]
    }
```

#### Step 4: Test Integration

Create test script:

```python
# test_my_platform.py

import sys
sys.path.insert(0, 'AI_infrastructure')

from tools.registry_v3 import RegistryV3

# Load registry
registry = RegistryV3()

# Check if tools loaded
my_tools = [name for name in registry.tools.keys() if 'my_platform' in name]
print(f"Found {len(my_tools)} My Platform tools:")
for tool in my_tools:
    print(f"  - {tool}")

# Test tool execution (with mock credentials)
print("\nTesting tool execution:")
try:
    result = registry.execute_tool(
        tool_name='my_platform_list_items',
        limit=5,
        my_platform_api_key='mock_key_for_testing'
    )
    print(f"✅ Tool execution successful: {result}")
except Exception as e:
    print(f"⚠️  Tool execution failed: {e}")
```

Run test:

```powershell
cd C:\Users\gpoli\GIT\AI_agents
python test_my_platform.py
```

#### Step 5: Restart Flask Server

```powershell
cd C:\Users\gpoli\GIT\AI_agents
BISTART
```

Expected output:

```
[REGISTRY_V3] Loading schemas...
[SCHEMAS] Loaded 599 tool definitions  ← (+5 new tools)
[REGISTRY_V3] Loading from tools/implementations/
   tools.implementations.my_platform: 5 functions  ← NEW!
[OK] Registry V3 initialized: 599 tools loaded
```

**Done!** Tools are now available to AI agents.

### Method 2: Plugin Module (Advanced)

**Use when:** External system, optional feature, complex dependencies

**Steps:**

#### Step 1: Create Module Structure

```powershell
mkdir UI\external\modules\my-module
mkdir UI\external\modules\my-module\schema
mkdir UI\external\modules\my-module\implementations
mkdir UI\external\modules\my-module\backend
```

#### Step 2: Create Schema

**File:** `UI/external/modules/my-module/schema/my_tools.json`

```json
{
  "platform": "my_module",
  "description": "My Module - Description",
  "tools": [
    {
      "name": "my_tool_function",
      "description": "Tool description",
      "parameters": {...}
    }
  ]
}
```

#### Step 3: Create Implementation Wrapper

**File:** `UI/external/modules/my-module/implementations/my_wrapper.py`

```python
"""
My Module Tool Wrapper

FILE: UI/external/modules/my-module/implementations/my_wrapper.py
PURPOSE: Tool implementations
"""

import sys
from pathlib import Path

# Add backend module to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Import business logic
from my_business_logic import MyBusinessLogic

# Initialize
business_logic = MyBusinessLogic()

def my_tool_function(param1: str, **kwargs) -> dict:
    """Tool implementation"""
    try:
        result = business_logic.do_something(param1)
        return {'success': True, 'result': result}
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

#### Step 4: Create Business Logic

**File:** `UI/external/modules/my-module/backend/my_business_logic.py`

```python
"""
My Module Business Logic

FILE: UI/external/modules/my-module/backend/my_business_logic.py
PURPOSE: Core business logic (separate from AI wrapper)
"""

class MyBusinessLogic:
    def __init__(self):
        # Initialize
        pass
    
    def do_something(self, param1: str):
        # Business logic
        return f"Processed: {param1}"
```

#### Step 5: Restart Server

```powershell
BISTART
```

Expected output:

```
[REGISTRY_V3] Loading module plugins...
OK [Module Plugin] Discovered module: my-module
     [my-module] Loaded schema: my_tools.json (1 tools)
[PLUGINS] Loaded 1 tools from 1 modules
```

**Done!** Plugin module loaded automatically.

---

## Module Plugin System

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  MODULE PLUGIN SYSTEM                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │ UI/external/modules/                         │          │
│  ├──────────────────────────────────────────────┤          │
│  │                                              │          │
│  │  ┌────────────────┐  ┌────────────────┐    │          │
│  │  │ calculator-    │  │ stock-         │    │          │
│  │  │ module/        │  │ management/    │    │          │
│  │  ├────────────────┤  ├────────────────┤    │          │
│  │  │ schema/        │  │ schema/        │    │          │
│  │  │ impl/          │  │ impl/          │    │          │
│  │  │ backend/       │  │ backend/       │    │          │
│  │  └────────────────┘  └────────────────┘    │          │
│  │                                              │          │
│  └──────────────────────────────────────────────┘          │
│                     ↓                                       │
│  ┌──────────────────────────────────────────────┐          │
│  │ tools/plugins/module_plugin_loader.py        │          │
│  ├──────────────────────────────────────────────┤          │
│  │ 1. Discovers modules with schema/ + impl/    │          │
│  │ 2. Loads JSON schemas                        │          │
│  │ 3. Loads Python implementations              │          │
│  │ 4. Returns to Registry V3                    │          │
│  └──────────────────────────────────────────────┘          │
│                     ↓                                       │
│  ┌──────────────────────────────────────────────┐          │
│  │ Registry V3                                   │          │
│  ├──────────────────────────────────────────────┤          │
│  │ • Adds plugin tools to self.tools             │          │
│  │ • Adds plugin impl to self.implementations   │          │
│  │ • Tools available to AI agents                │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Benefits

1. **Zero Code Changes**
   - Add folder → tools appear
   - Remove folder → tools disappear
   - No registry edits needed

2. **Complete Isolation**
   - Module has own dependencies
   - Own business logic
   - Own configuration

3. **Optional Features**
   - Calculator module (optional)
   - Stock management (optional)
   - Easy to enable/disable

4. **Development Flexibility**
   - Develop module separately
   - Test independently
   - Deploy when ready

### Plugin Module Structure

```
UI/external/modules/my-module/
├── manifest.json                    ← UI metadata (optional)
├── my-module.js                     ← Frontend code (optional)
├── my-module.css                    ← Styling (optional)
│
├── schema/                          ← AI TOOLS (required)
│   └── my_tools.json               ← Tool definitions
│
├── implementations/                 ← AI TOOLS (required)
│   ├── __init__.py                 ← Python package marker
│   └── my_wrapper.py               ← Tool implementations
│
├── backend/                         ← BUSINESS LOGIC (optional)
│   ├── __init__.py
│   ├── my_business_logic.py        ← Core functionality
│   └── config.json                 ← Configuration
│
├── routes/                          ← FLASK ROUTES (optional)
│   ├── __init__.py
│   └── my_routes.py                ← HTTP endpoints
│
└── docs/
    └── README.md
```

**Minimum Required:**
- `schema/my_tools.json` - Tool definitions
- `implementations/my_wrapper.py` - Tool implementations

Everything else is optional!

### Discovery Process

```python
# tools/plugins/module_plugin_loader.py

class ModulePluginLoader:
    def discover_modules_with_tools(self):
        """Find modules with tools"""
        modules_with_tools = []
        
        for module_dir in self.modules_dir.iterdir():
            # Check if has schema/ and implementations/
            schema_dir = module_dir / "schema"
            impl_dir = module_dir / "implementations"
            
            if schema_dir.exists() and impl_dir.exists():
                # Module has tools!
                modules_with_tools.append(module_dir.name)
                print(f"Discovered module: {module_dir.name}")
        
        return modules_with_tools
    
    def load_module_schemas(self, module_id):
        """Load JSON schemas from module"""
        schema_dir = self.modules_dir / module_id / "schema"
        all_tools = []
        
        for schema_file in schema_dir.glob("*.json"):
            with open(schema_file, 'r') as f:
                schema_data = json.load(f)
                if "tools" in schema_data:
                    all_tools.extend(schema_data["tools"])
        
        return all_tools
    
    def load_module_implementations(self, module_id, tool_names):
        """Load Python implementations from module"""
        impl_dir = self.modules_dir / module_id / "implementations"
        implementations = {}
        
        # Find wrapper file(s)
        wrapper_files = list(impl_dir.glob("*_wrapper.py"))
        
        for wrapper_file in wrapper_files:
            # Import wrapper module
            spec = importlib.util.spec_from_file_location(
                wrapper_file.stem, 
                wrapper_file
            )
            wrapper_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(wrapper_module)
            
            # Map tool names to functions
            for tool_name in tool_names:
                if hasattr(wrapper_module, tool_name):
                    implementations[tool_name] = getattr(wrapper_module, tool_name)
        
        return implementations
```

---

## Credential Injection System

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 CREDENTIAL INJECTION FLOW                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. AI Agent calls tool                                     │
│     ↓                                                        │
│  2. Agent Worker extracts user_id                           │
│     ↓                                                        │
│  3. Credential Injector queries database                    │
│     ↓                                                        │
│  ┌────────────────────────────────────────┐                 │
│  │ user_platform_credentials table        │                 │
│  ├────────────────────────────────────────┤                 │
│  │ user_id | platform | access_token      │                 │
│  │ 1       | google   | ya29.a0...        │                 │
│  │ 1       | microsoft| eyJ0...           │                 │
│  │ 2       | google   | ya29.b1...        │                 │
│  └────────────────────────────────────────┘                 │
│     ↓                                                        │
│  4. Returns OAuth tokens for user + platform                │
│     ↓                                                        │
│  5. Registry adds tokens to **kwargs                        │
│     ↓                                                        │
│  6. Tool extracts: access_token = kwargs.get('access_token')│
│     ↓                                                        │
│  7. Tool uses tokens for API call                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

```sql
CREATE TABLE user_platform_credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    token_expiry TIMESTAMP,
    tenant_id TEXT,              -- For platforms needing tenant/org ID
    additional_data TEXT,         -- JSON for platform-specific data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, platform)
);

-- Example data:
INSERT INTO user_platform_credentials 
(user_id, platform, access_token, refresh_token, token_expiry)
VALUES 
(1, 'google', 'ya29.a0AfH6SMBxx...', '1//0gAx...', '2025-11-23 14:30:00'),
(1, 'microsoft', 'eyJ0eXAiOiJKV1...', NULL, '2025-11-23 15:00:00'),
(1, 'stripe', 'sk_test_51Xxx...', NULL, NULL),
(1, 'xero', 'ya29.c0Hxxx...', '1//0fXxx...', '2025-11-23 16:00:00');
```

### Credential Injector

```python
# AI_infrastructure/auth/credential_injector.py

class CredentialInjector:
    """Injects OAuth credentials at tool execution time"""
    
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / 'data' / 'ai_infrastructure.db'
    
    def get_google_credentials(self, user_id: int) -> Dict[str, str]:
        """Get Google OAuth credentials"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT access_token, refresh_token, token_expiry
            FROM user_platform_credentials
            WHERE user_id = ? AND platform = 'google'
            ORDER BY updated_at DESC
            LIMIT 1
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'access_token': row[0],
            'refresh_token': row[1],
            'token_expiry': row[2]
        }
    
    def get_microsoft_credentials(self, user_id: int) -> Dict[str, str]:
        """Get Microsoft OAuth credentials"""
        # Similar to get_google_credentials
        pass
    
    def get_platform_credentials(self, user_id: int, platform: str) -> Dict[str, str]:
        """Generic credential fetcher"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT access_token, refresh_token, token_expiry, tenant_id, additional_data
            FROM user_platform_credentials
            WHERE user_id = ? AND platform = ?
            ORDER BY updated_at DESC
            LIMIT 1
        """, (user_id, platform))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'access_token': row[0],
            'refresh_token': row[1],
            'token_expiry': row[2],
            'tenant_id': row[3],
            'additional_data': json.loads(row[4]) if row[4] else {}
        }
```

### Injection in Agent Worker

```python
# AI_infrastructure/core/agent_worker.py

class AgentWorker:
    def execute_tool_with_credentials(self, tool_name, params, user_id):
        """Execute tool with automatic credential injection"""
        
        # Get tool platform
        tool = self.registry.get_tool(tool_name)
        platform = tool.get('platform')
        
        # Fetch credentials
        injector = CredentialInjector()
        credentials = injector.get_platform_credentials(user_id, platform)
        
        if not credentials:
            return {'error': f'No credentials found for platform: {platform}'}
        
        # Execute tool with credentials
        result = self.registry.execute_tool(
            tool_name=tool_name,
            **params,
            _user_id=user_id,
            _injected_credentials=credentials
        )
        
        return result
```

### Tool Credential Extraction

```python
# In tool implementation

def my_tool_function(param1: str, **kwargs) -> dict:
    """Tool function"""
    
    # Extract credentials from kwargs
    credentials = kwargs.get('_injected_credentials', {})
    access_token = credentials.get('access_token')
    refresh_token = credentials.get('refresh_token')
    
    # Or direct extraction (if credential injector adds to root kwargs)
    access_token = kwargs.get('access_token')
    
    # Validate
    if not access_token:
        raise ValueError("access_token required but not provided")
    
    # Use token for API call
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    
    return response.json()
```

---

## Real-World Examples

### Example 1: Gmail Send Email (Google Pattern)

**Schema:** `tools/schemas/gmail_tools.json`

```json
{
  "platform": "gmail",
  "tools": [
    {
      "name": "gmail_send_email",
      "description": "Send email via Gmail. Example: Send 'Hello World' to john@example.com with subject 'Test'",
      "parameters": {
        "type": "object",
        "properties": {
          "to": {"type": "string", "description": "Recipient email"},
          "subject": {"type": "string", "description": "Email subject"},
          "body": {"type": "string", "description": "Email body (plain text or HTML)"}
        },
        "required": ["to", "subject", "body"]
      }
    }
  ]
}
```

**Implementation:** `google_workspace/gmail.py`

```python
def gmail_send_email(to: str, subject: str, body: str, **kwargs) -> dict:
    """Send email via Gmail"""
    access_token = kwargs.get('access_token')
    
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from email.mime.text import MIMEText
    import base64
    
    # Create credentials
    creds = Credentials(token=access_token)
    service = build('gmail', 'v1', credentials=creds)
    
    # Build message
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    # Send
    result = service.users().messages().send(
        userId='me',
        body={'raw': raw}
    ).execute()
    
    return {
        'success': True,
        'message_id': result['id'],
        'thread_id': result['threadId']
    }
```

**Usage by AI:**

```
User: "Send an email to john@example.com saying hello"

AI: [calls tool]
execute_tool(
    tool_name="gmail_send_email",
    to="john@example.com",
    subject="Hello",
    body="Hello from AI Agent!",
    _user_id=1
)

Backend: [injects credentials]
access_token = "ya29.a0..."

Tool: [executes]
Gmail API: Email sent successfully

Result: {"success": true, "message_id": "18c5..."}

AI: "✅ Email sent to john@example.com"
```

### Example 2: Stripe Create Customer (Function Pattern)

**Schema:** `tools/schemas/stripe_tools.json`

```json
{
  "platform": "stripe",
  "tools": [
    {
      "name": "stripe_create_customer",
      "description": "Create a new Stripe customer for payment processing",
      "parameters": {
        "type": "object",
        "properties": {
          "email": {"type": "string", "description": "Customer email"},
          "name": {"type": "string", "description": "Customer name"},
          "description": {"type": "string", "description": "Customer description"}
        },
        "required": ["email"]
      }
    }
  ]
}
```

**Implementation:** `tools/implementations/stripe.py`

```python
import stripe

def stripe_create_customer(
    email: str, 
    name: str = None, 
    description: str = None,
    **kwargs
) -> dict:
    """Create Stripe customer"""
    stripe_api_key = kwargs.get('stripe_api_key')
    stripe.api_key = stripe_api_key
    
    customer = stripe.Customer.create(
        email=email,
        name=name,
        description=description
    )
    
    return {
        'success': True,
        'customer_id': customer.id,
        'email': customer.email,
        'created': customer.created
    }
```

**Usage:**

```
User: "Create a Stripe customer for john.doe@example.com named John Doe"

AI: [calls tool]
execute_tool(
    tool_name="stripe_create_customer",
    email="john.doe@example.com",
    name="John Doe",
    _user_id=1
)

Backend: [injects Stripe API key]
stripe_api_key = "sk_test_51..."

Tool: [creates customer]
Stripe API: Customer created

Result: {
  "success": true,
  "customer_id": "cus_xxxxx",
  "email": "john.doe@example.com"
}

AI: "✅ Created Stripe customer: cus_xxxxx"
```

### Example 3: Calculator (Plugin Pattern)

**Schema:** `UI/external/modules/calculator-module/schema/calculator_tools.json`

```json
{
  "platform": "calculator",
  "tools": [
    {
      "name": "calculate_flyers",
      "description": "Calculate quote for printing flyers",
      "parameters": {
        "type": "object",
        "properties": {
          "quantity": {"type": "integer"},
          "width": {"type": "integer"},
          "height": {"type": "integer"},
          "stock_gsm": {"type": "integer"},
          "print_mode": {"type": "string"}
        },
        "required": ["quantity", "width", "height", "stock_gsm", "print_mode"]
      }
    }
  ]
}
```

**Implementation:** `UI/external/modules/calculator-module/implementations/calculator_wrapper.py`

```python
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from calculator_wrapper import QuoteCalculatorWrapper

# Initialize calculator
calculator = QuoteCalculatorWrapper()

def calculate_flyers(
    quantity: int,
    width: int,
    height: int,
    stock_gsm: int,
    print_mode: str,
    **kwargs
) -> dict:
    """Calculate flyer quote"""
    try:
        result = calculator.calculate_flyers(
            quantity=quantity,
            width=width,
            height=height,
            stock_gsm=stock_gsm,
            print_mode=print_mode
        )
        return result
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

**Usage:**

```
User: "Calculate quote for 1,000 A4 flyers on 170 GSM, double-sided"

AI: [calls tool]
execute_tool(
    tool_name="calculate_flyers",
    quantity=1000,
    width=210,
    height=297,
    stock_gsm=170,
    print_mode="double_sided",
    _user_id=1
)

Plugin: [calculates quote]
Calculator: Processes pricing

Result: {
  "success": true,
  "quote": {
    "total": "$245.00",
    "per_unit": "$0.245",
    "turnaround": "3 business days"
  }
}

AI: "Quote for 1,000 A4 flyers: $245.00 ($0.245 each)"
```

---

## Best Practices

### Schema Design

✅ **DO:**

1. **Write descriptive tool descriptions**
   ```json
   "description": "Create Google Sheet with optional data and markdown formatting. 
   Example: Create sales report with color-coded performance metrics."
   ```

2. **Include examples**
   ```json
   "examples": [
     {
       "description": "Create simple contact list",
       "parameters": {
         "title": "Contacts",
         "headers": ["Name", "Email", "Phone"]
       }
     }
   ]
   ```

3. **Document return values**
   ```json
   "returns": {
     "type": "object",
     "description": "Created sheet with spreadsheet_id, url, and row count"
   }
   ```

4. **Use clear parameter names**
   ```json
   "properties": {
     "max_results": {...},     // GOOD: Clear intent
     "limit": {...}            // OKAY: Common pattern
   }
   ```

❌ **DON'T:**

1. **Use vague descriptions**
   ```json
   "description": "Creates stuff"  // BAD!
   ```

2. **Forget required fields**
   ```json
   "parameters": {
     "type": "object",
     "properties": {...},
     // Missing "required" array!
   }
   ```

3. **Use ambiguous names**
   ```json
   "properties": {
     "val": {...},  // BAD: What value?
     "data": {...}  // BAD: What kind of data?
   }
   ```

### Implementation Best Practices

✅ **DO:**

1. **Extract credentials from kwargs**
   ```python
   def my_tool(**kwargs):
       access_token = kwargs.get('access_token')
       if not access_token:
           raise ValueError("access_token required")
   ```

2. **Use type hints**
   ```python
   def my_tool(param1: str, param2: int = 10, **kwargs) -> dict:
       # Clear parameter types
   ```

3. **Return consistent structure**
   ```python
   return {
       'success': True,
       'result': {...},
       'message': 'Operation completed'
   }
   ```

4. **Handle errors gracefully**
   ```python
   try:
       result = api_call()
       return {'success': True, 'data': result}
   except APIError as e:
       return {'success': False, 'error': str(e)}
   ```

5. **Add docstrings**
   ```python
   def my_tool(param1: str, **kwargs) -> dict:
       """
       Brief description
       
       Args:
           param1: Description
           **kwargs: Credential injection
       
       Returns:
           Dict with success and result
       """
   ```

❌ **DON'T:**

1. **Hardcode credentials**
   ```python
   def my_tool():
       api_key = "sk_test_xxx..."  // BAD!
   ```

2. **Ignore errors**
   ```python
   def my_tool():
       try:
           api_call()
       except:
           pass  // BAD! Silent failure
   ```

3. **Return inconsistent structures**
   ```python
   # Sometimes returns string, sometimes dict
   if success:
       return "Success"
   else:
       return {'error': 'Failed'}  // BAD!
   ```

### Testing

✅ **DO:**

1. **Test schema loading**
   ```python
   registry = RegistryV3()
   assert 'my_tool' in registry.tools
   ```

2. **Test implementation loading**
   ```python
   func = registry.get_tool_function('my_tool')
   assert func is not None
   ```

3. **Test with mock credentials**
   ```python
   result = registry.execute_tool(
       tool_name='my_tool',
       param1='test',
       access_token='mock_token'
   )
   ```

4. **Test error handling**
   ```python
   result = registry.execute_tool(
       tool_name='my_tool',
       param1='test'
       # Missing credentials
   )
   assert 'error' in result
   ```

---

## Troubleshooting

### Issue: Tool Not Loading

**Symptom:**
```
Tool 'my_tool' not found in registry
```

**Diagnosis:**

```powershell
cd C:\Users\gpoli\GIT\AI_agents
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); print([t for t in r.tools if 'my_tool' in t])"
```

**Causes:**

1. ❌ Schema file not in `tools/schemas/`
2. ❌ JSON syntax error in schema
3. ❌ Tool name mismatch (schema vs implementation)
4. ❌ Missing "tools" array in schema

**Solution:**

1. Check schema file location
2. Validate JSON: `python -m json.tool tools/schemas/my_tools.json`
3. Verify tool name matches exactly
4. Restart Flask server

### Issue: Tool Execution Fails

**Symptom:**
```
Tool 'my_tool' executed but returned error
```

**Diagnosis:**

Check Flask logs:
```powershell
Get-Content "AI_infrastructure\flask_app.log" -Tail 50
```

**Causes:**

1. ❌ Missing credentials
2. ❌ Implementation not found
3. ❌ API call failed
4. ❌ Parameter type mismatch

**Solution:**

1. Check credential injection:
   ```python
   access_token = kwargs.get('access_token')
   print(f"Token: {access_token}")
   ```

2. Verify implementation loads:
   ```python
   func = registry.get_tool_function('my_tool')
   print(f"Found: {func}")
   ```

3. Test API separately
4. Add type conversion in wrapper

### Issue: Credentials Not Injecting

**Symptom:**
```
Tool receives empty access_token
```

**Diagnosis:**

Check database:
```sql
SELECT * FROM user_platform_credentials 
WHERE user_id = 1 AND platform = 'my_platform';
```

**Causes:**

1. ❌ No credentials in database
2. ❌ Wrong platform name
3. ❌ Credential injector not called
4. ❌ User ID mismatch

**Solution:**

1. Add credentials via OAuth flow
2. Verify platform name matches schema
3. Check agent_worker.py calls injector
4. Use correct user ID in API call

### Issue: Module Plugin Not Loading

**Symptom:**
```
[PLUGINS] No module plugins found
```

**Diagnosis:**

Check folder structure:
```powershell
ls UI\external\modules\my-module\
```

**Causes:**

1. ❌ Missing `schema/` folder
2. ❌ Missing `implementations/` folder
3. ❌ No `*_wrapper.py` file
4. ❌ Import errors in wrapper

**Solution:**

1. Create required folders
2. Add wrapper file
3. Fix import errors
4. Restart server

---

## Summary

The AI Agents Tool Library provides a **powerful, flexible architecture** for integrating platforms:

### Key Strengths

1. ✅ **Modular** - Add platforms without touching core code
2. ✅ **Automatic** - Tools auto-discover and register
3. ✅ **Flexible** - Multiple implementation patterns supported
4. ✅ **Secure** - Runtime credential injection (no hardcoded keys)
5. ✅ **Scalable** - 594+ tools, growing easily

### Integration Patterns

- **Standard Integration** - `tools/schemas/` + `tools/implementations/`
- **Google Integration** - `tools/schemas/` + `google_workspace/`
- **Plugin Module** - `UI/external/modules/*/schema/` + `implementations/`

### Adding New Platforms

1. Create JSON schema
2. Create Python implementation
3. (Optional) Add credential support
4. Restart server
5. **Done!**

### Best Practices

- Write detailed descriptions
- Use credential injection
- Return consistent structures
- Test thoroughly
- Document well

---

**For questions or issues, consult:**
- Registry V3: `tools/registry_v3.py`
- Plugin Loader: `tools/plugins/module_plugin_loader.py`
- Credential Injector: `AI_infrastructure/auth/credential_injector.py`
- GitHub Copilot Instructions: `.github/copilot-instructions.md`

**Status:** ✅ PRODUCTION READY - 594+ Tools Active
