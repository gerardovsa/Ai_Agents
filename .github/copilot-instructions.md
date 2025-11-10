# GitHub Copilot Instructions - AI Agents Platform

## Architecture Overview

This is a multi-agent AI platform with 576 tools across 20+ platforms. The Flask backend runs on port 5001 and provides a unified API for tool execution, session management, and multi-provider AI interactions.

## Calculator Tools Integration (January 2025)

**NEW**: InHouse Print quote calculators now accessible to AI agents!

### Available Calculator Tools (7 total):
1. `calculate_business_cards` - Business cards with Shopify pricing
2. `calculate_flyers` - Flyers/leaflets (also handles business cards as 90x55mm)
3. `calculate_perfect_bound_books` - Perfect bound books with glued spine
4. `calculate_corflute_signs` - Rigid signage with tier pricing
5. `calculate_booklets` - Saddle-stitched booklets
6. `get_stock_list` - Available paper stocks
7. `get_calculator_requirements` - Parameter requirements for any calculator

### How It Works:
- Wrapper in `tools/implementations/calculator.py` imports calculator from In_House_SQL project
- Direct import strategy (no HTTP wrapper needed)
- Connects to In_House_SQL database: `C:\Users\gpoli\GIT\In_House_SQL\G_Folder`
- Uses `ComprehensiveQuoteCalculator` class from `complete_calculator_implementation.py`

### Usage Example:
```
User: "Calculate quote for 1,000 business cards, double-sided, 350GSM Satin"
AI: Calls calculate_business_cards(quantity=1000, stock_type="standard", ...)
Returns: Quote with total price, per-card cost, stock details, turnaround time
```

### Files Created:
- `tools/schemas/calculator_tools.json` - 7 tool definitions
- `tools/implementations/calculator.py` - CalculatorWrapper class
- `CALCULATOR_INTEGRATION_COMPLETE.md` - Complete documentation
- `CALCULATOR_QUICK_START.md` - Quick reference guide

## Progressive Tool Loading System (January 2025) 🎉 NEW

**CRITICAL FEATURE**: Claude now discovers tools hierarchically instead of receiving all 594 tools upfront!

### System Overview:
- **First turn**: Send only 5 meta-tools (99.2% token reduction: 70,844 → 431 tokens)
- **Subsequent turns**: Send all 594 tools after discovery
- **Cost savings**: $211/day with 1,000 requests
- **Implementation**: `AI_infrastructure/core/agent_worker.py` lines 236-258

### How It Works:
```python
# agent_worker.py - Progressive loading logic
conversation_length = len(conversation_history or [])

if conversation_length == 0:
    # First turn: 5 meta-tools only
    meta_tool_names = ['list_available_platforms', 'list_platform_tools', 
                       'get_platform_guide', 'recommend_tools_for_task',
                       'get_workflow_steps']
    all_tools_dict = {t['name']: t for t in registry.get_anthropic_tools()}
    tools = [all_tools_dict[name] for name in meta_tool_names if name in all_tools_dict]
    print(f"🔷 [Progressive Loading] First turn: Sending {len(tools)} meta-tools only")
else:
    # Subsequent turns: 594 full tools
    tools = registry.get_anthropic_tools()
    print(f"🔷 [Progressive Loading] Turn {conversation_length + 1}: Sending {len(tools)} full tools")
```

### Workflow Example:
```
User: "Send an email to john@example.com"

Turn 1 (5 meta-tools sent):
  Claude calls: list_available_platforms()
  Result: ["google_workspace", "microsoft_365", ...]

Turn 2 (594 full tools sent):
  Claude calls: gmail_send_email(to="john@example.com", ...)
  Result: Email sent successfully
```

### Testing:
```powershell
# Test progressive loading
cd c:\Users\gpoli\GIT\AI_agents
python test_progressive_with_google.py

# Expected output:
# ✅ Turn 1: list_available_platforms used
# ✅ Turn 2: gmail_send_email used
# 🎉 SUCCESS! Progressive tool discovery working!
```

### Documentation:
- `PROGRESSIVE_LOADING_SUCCESS.md` - Complete implementation guide
- `AGENT_FLOW_ANALYSIS.md` - Architecture analysis (1,500+ lines)
- `QUICK_FIX_PROGRESSIVE_TOOLS.md` - Implementation guide (800+ lines)
- `test_progressive_with_google.py` - End-to-end test (400+ lines)

### Status: ✅ PRODUCTION READY - All tests passing

---

## Google Sheets Markdown Formatting v2.0 (November 2025) ⚡ ENHANCED

**FEATURE**: Convert markdown syntax to professional Google Sheets formatting with v2.0 compact syntax!

### Overview:
- Create beautifully formatted spreadsheets using simple markdown syntax
- **96% time savings** (15 min → 30 sec per sheet)
- **100% backward compatible** (opt-in feature)
- **Production ready** - All tests passing (4/4)

### Usage:
```python
registry.execute_tool(
    'google_sheets_create',
    title='Sales Report',
    headers=['# Product', '**Q3**', '**Q4**', '**Status**'],
    data=[
        ['**Premium**', '$145K', '$168K', '[GREEN]+16%[/GREEN]'],
        ['Standard', '$85K', '$78K', '[RED]-8%[/RED]']
    ],
    parse_markdown=True,  # ✨ ADD THIS!
    _user_id=1,
    _injected_credentials=True
)
```

### v2.0 Syntax (COMPACT - RECOMMENDED):

**Alignment (parentheses at start):**
- `(L)text` → Left align
- `(R)text` → Right align
- `(C)text` → Center align

**Text Colors (shortened, no closing):**
- `[R]text` → Red (🔴 errors, critical, blocked)
- `[G]text` → Green (🟢 success, active, complete)
- `[B]text` → Blue (🔵 info, neutral)
- `[P]text` → Purple (🟣 special, VIP)
- `[GR]text` → Gray (⚫ inactive, archived)
- `[BK]text` → Black (standard)

**Background Colors (curly braces, no closing):**
- `{LR}text` → Light red background
- `{LG}text` → Light green background
- `{LB}text` → Light blue background
- `{LP}text` → Light purple background
- `{LGR}text` → Light gray background

**Stacking Order:** `(ALIGN)[COLOR]{BG}text`  
**Example:** `(R)[G]{LG}$125K` → Right-aligned, green text, light green background

**Character Savings:** 32-75% shorter than v1.2 syntax!

### v1.2 Syntax (VERBOSE - STILL SUPPORTED):
- `**bold text**` → Bold formatting
- `*italic text*` → Italic formatting
- `# Header` → Large bold header (18pt)
- `[RED]text[/RED]` → Red text (verbose with closing)
- `[BG:LIGHTGREEN]text[/BG]` → Light green background (verbose)
- **Automatic borders** on all cells (controlled by `auto_borders` parameter)

### Before vs After:

**Without markdown (default):**
```
| **Name** | [RED]Status[/RED] |  ← Literal markdown visible
```

**With markdown (parse_markdown=True):**
```
| Name (bold, 18pt) | Status (bold) |  ← Professional formatting
| John (bold)       | Critical (red)|  ← No markdown syntax
```

### Business Use Cases:

**1. Sales Dashboards:**
```python
headers=['# Product', '**Revenue**', '**Growth**']
data=[['**Premium**', '$145K', '[GREEN]+16%[/GREEN]']]
```

**2. Patient Records:**
```python
headers=['# Patient', '**Status**', '**Priority**']
data=[['**Dr. Smith**', '[GREEN]Stable[/GREEN]', 'Low']]
```

**3. Inventory Alerts:**
```python
headers=['# SKU', '**Stock**', '**Alert**']
data=[['WDG-001', '250', '[GREEN]OK[/GREEN]']]
```

**4. Project Status:**
```python
headers=['# Task', '**Owner**', '**Status**']
data=[['**API**', 'John', '[YELLOW]In Progress[/YELLOW]']]
```

### Files:
- Implementation: `google_workspace/sheets_markdown_formatter.py` (400+ lines)
- Integration: `google_workspace/google_docs.py` (enhanced google_sheets_create)
- Schema: `tools/schemas/google_sheets_tools.json` (updated)
- Tests: `testing_tools/test_sheets_markdown.py` (4/4 passing)
- Docs: `SHEETS_MARKDOWN_FEATURE_COMPLETE.md`, `SHEETS_MARKDOWN_VISUAL_GUIDE.md`

### Test Results:
```
✅ Test 1: Markdown formatter module - PASS
✅ Test 2: Create without markdown (baseline) - PASS
✅ Test 3: Create with markdown (feature) - PASS
✅ Test 4: Complex business report - PASS

Results: 4/4 tests passed (100%)
Status: PRODUCTION READY
```

### Key Benefits:
- ✅ Professional formatting without manual work
- ✅ Consistency with Google Docs markdown rendering
- ✅ Color-coded dashboards for better visibility
- ✅ 96% time savings vs manual formatting
- ✅ Simple syntax, easy to use
- ✅ 100% backward compatible

### Pro Tips:
- Use `[COLOR]` tags for status indicators (green=good, red=bad)
- Use `**bold**` for emphasis on key items
- Use `# Headers` for visual hierarchy
- Combine styles: `**[RED]Critical[/RED]**` = bold red text
- Default is `parse_markdown=False` (preserves existing behavior)

---

## Key Component Pattern

### Core Files & Responsibilities
- `app.py` - **MAIN APPLICATION** - Flask app entry point (legacy)
- `AI_infrastructure/flask_app.py` - **NEW FLASK APP** - Modern Flask backend (port 5001)
- `tools/registry_v3.py` - **TOOL REGISTRY** - Loads 594 tools from schemas and implementations (was registry.py)
- `config.py` - **GLOBAL CONFIG** - API keys for all tools
- `AI_infrastructure/config.py` - **FLASK CONFIG** - Flask settings and database paths
- `scripts/` - **ORGANIZED SCRIPTS** - Startup, setup, testing, maintenance utilities
- `AI_infrastructure/core/agent_worker.py` - **AGENT WORKER** - Progressive tool loading implementation (lines 236-258)

### Tool System Pattern (Critical)
```python
# Tool implementations inherit from base class
class MyToolImplementation:
    def __init__(self, **kwargs):
        self.credentials = None  # Credentials injected at runtime
        
    def my_tool_method(self, param1, param2, **kwargs):
        """Tool method with credential injection"""
        # Get credentials from kwargs (injected by credential_injector)
        access_token = kwargs.get('access_token')
        # Use credentials for API calls
        return self.execute_api_call(access_token, param1, param2)
```

## Configuration Architecture (CRITICAL)

### Two Config Files - Correct Architecture

**1. Root `config.py` - Global API keys storage**
   - **Purpose**: Provides API keys for all tools
   - **Contains**: 
     - `DEEPSEEK_API_KEYS` - List of DeepSeek API keys
     - `ANTHROPIC_API_KEYS` - List of Anthropic Claude API keys
     - `OPENAI_API_KEYS` - List of OpenAI API keys
     - `get_api_key_enhanced()` - Helper function for round-robin key rotation
   - **Used by**: Tool implementations in `tools/implementations/`
   - **Import pattern**: `from config import get_api_key_enhanced, DEEPSEEK_API_KEYS`
   - **Location**: `C:\Users\gpoli\GIT\AI_agents\config.py`

**2. AI_infrastructure/config.py - Flask application config**
   - **Purpose**: Flask app settings and database paths
   - **Contains**:
     - `Config` class with Flask configuration
     - `DB_CONFIG_PATH` - Path to database-config.json
     - `SESSION_DB_PATH` - Path to sessions.db
     - `SECRET_KEY` - Flask secret key
     - `DEBUG` - Debug mode setting
     - `CORS_ORIGINS` - CORS allowed origins
   - **Used by**: Flask app (`flask_app.py`) and infrastructure modules
   - **Import pattern**: `from config import Config` (within AI_infrastructure/)
   - **Location**: `C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\config.py`

## 🗄️ Database Architecture (CRITICAL - MUST FOLLOW)

### ✅ CORRECT Database Locations

**ALL database files MUST be in the `data/` folder:**

```python
# CORRECT PATTERN (ALWAYS USE THIS):
from pathlib import Path
root_dir = Path(__file__).parent.parent.parent  # Go up to AI_agents root
db_path = root_dir / 'data' / 'ai_infrastructure.db'
conn = sqlite3.connect(str(db_path))
```

**Official Database Locations:**

| Database | Location | Purpose |
|----------|----------|---------|
| `ai_infrastructure.db` | `data/ai_infrastructure.db` | User data, OAuth tokens, credentials |
| `sessions.db` | `data/sessions.db` | Flask sessions, JWT tokens |
| `synergy_sessions.db` | `data/synergy_sessions.db` | Synergy feature data |

**Full Paths:**
- ✅ `C:\Users\gpoli\GIT\AI_agents\data\ai_infrastructure.db` - CORRECT
- ❌ `C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\ai_infrastructure.db` - WRONG (old location)

### ❌ NEVER Use These Paths:

```python
# WRONG - Don't use AI_infrastructure/ folder for databases
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai_infrastructure.db')

# WRONG - Don't use relative paths
db_path = '../ai_infrastructure.db'

# WRONG - Don't hardcode absolute paths
db_path = 'C:\\Users\\gpoli\\GIT\\AI_agents\\AI_infrastructure\\ai_infrastructure.db'
```

### Database Connection Template

**When creating any new route or module that needs database access:**

```python
def get_db_connection():
    """
    Get database connection to ai_infrastructure.db in data/ folder
    
    CRITICAL: Always use data/ai_infrastructure.db (CORRECT LOCATION)
    Do NOT use AI_infrastructure/ai_infrastructure.db (WRONG - old location)
    """
    import sqlite3
    from pathlib import Path
    
    root_dir = Path(__file__).parent.parent.parent  # Up to AI_agents root
    db_path = root_dir / 'data' / 'ai_infrastructure.db'
    
    # Optional: Debug log to verify correct path
    print(f'🔷 [DB CONNECTION] Using: {db_path}')
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn
```

### Quick Verification

**To verify you're using the correct path:**

```python
# This should print: C:\Users\gpoli\GIT\AI_agents\data\ai_infrastructure.db
from pathlib import Path
root_dir = Path(__file__).parent.parent.parent
print(root_dir / 'data' / 'ai_infrastructure.db')
```

**See `DATABASE_PATH_FIX_COMPLETE.md` for full documentation.**

### Import Rules (MUST FOLLOW)

 **DO** - Tool implementations import from root config:
```python
# In tools/implementations/my_tool.py
from config import get_api_key_enhanced, DEEPSEEK_API_KEYS
```

 **DO** - Flask infrastructure imports from local config:
```python
# In AI_infrastructure/flask_app.py or AI_infrastructure/routes/*.py
import sys
sys.path.insert(0, os.path.dirname(__file__))
from config import Config
```

 **DON'T** - Mix up the configs:
```python
# WRONG - Tool trying to import Flask Config class
from config import Config  # This doesn't exist in root config.py

# WRONG - Flask app trying to import API keys from local config
from config import DEEPSEEK_API_KEYS  # This doesn't exist in AI_infrastructure/config.py
```

## Critical Development Commands

### Start the AI Agent Server
```powershell
# From any directory (PATH command)
BISTART

# Or manually
cd C:\Users\gpoli\GIT\AI_agents
BISTART

# Or directly
cd C:\Users\gpoli\GIT\AI_agents\AI_infrastructure
python flask_app.py
```

### Talk to AI Agent
```powershell
# From any directory (PATH command)
CHAT What tools are available?
CHAT List my Gmail messages
CHAT "Create a Google Doc titled 'Test Document'"

# Multi-word queries need quotes
CHAT "Send an email to john@example.com with subject 'Hello'"
```

### Test Tool Loading
```powershell
cd C:\Users\gpoli\GIT\AI_agents
python -c "from tools.registry import ToolRegistry; registry = ToolRegistry(); print(f'Loaded {len(registry.tools)} tools')"
```

## 🛠️ Tool System Architecture (COMPLETE GUIDE)

### Tool Structure - Two Required Files

Every tool needs **TWO files**:
1. **Schema file** (JSON) in `tools/schemas/` - Defines the tool interface
2. **Implementation file** (Python) in `tools/implementations/` or `google_workspace/` - Contains the actual code

### Tool Loading Process
1. **Schema Loading** - Loads JSON schemas from `tools/schemas/`
2. **Implementation Loading** - Loads Python implementations from `tools/implementations/`
3. **Registry Creation** - Creates unified registry with 564 tools
4. **Credential Injection** - Injects credentials at runtime via `credential_injector.py`

### Credential Injection Pattern
```python
# AI_infrastructure/auth/credential_injector.py
class CredentialInjector:
    def get_google_credentials(self, user_id):
        """Get Google OAuth credentials for user"""
        # Fetch from user_platform_credentials table
        return {
            'access_token': token,
            'refresh_token': refresh,
            'token_uri': uri
        }
    
    def get_microsoft_credentials(self, user_id):
        """Get Microsoft Graph credentials for user"""
        # Fetch from user_platform_credentials table
        return {
            'access_token': token
        }
```

### Tool Execution Flow
```
User Request → Flask Route → Agent Routes → Tool Registry
    ↓
Credential Injector (adds user credentials)
    ↓
Tool Implementation (executes with credentials)
    ↓
API Call (Google/Microsoft/etc.)
    ↓
Return Result
```

## 📝 HOW TO ADD NEW TOOLS (Step-by-Step Guide)

### Tool Schema Formats (CRITICAL - Choose One)

The registry supports **TWO schema formats**. Choose based on your preference:

**Format 1 - Simple Format (Legacy - Most Tools Use This):**
```json
{
  "platform": "my_platform",
  "description": "Platform description",
  "tools": [
    {
      "name": "my_tool_function",
      "description": "What this tool does",
      "platform": "my_platform",
      "parameters": {
        "param1": {
          "type": "string",
          "description": "Parameter description",
          "required": true
        },
        "param2": {
          "type": "integer",
          "description": "Optional parameter",
          "required": false,
          "default": 100
        }
      },
      "returns": {
        "type": "object",
        "description": "What the tool returns"
      }
    }
  ]
}
```

**Format 2 - Anthropic Native Format (Recommended for New Tools):**
```json
{
  "platform": "my_platform",
  "description": "Platform description",
  "tools": [
    {
      "name": "my_tool_function",
      "description": "What this tool does",
      "platform": "my_platform",
      "parameters": {
        "type": "object",
        "properties": {
          "param1": {
            "type": "string",
            "description": "Parameter description"
          },
          "param2": {
            "type": "integer",
            "description": "Optional parameter",
            "default": 100
          }
        },
        "required": ["param1"]
      },
      "returns": {
        "type": "object",
        "description": "What the tool returns"
      }
    }
  ]
}
```

**Both formats are automatically converted to Anthropic's required format by `registry_v3.py`.**

### Step 1: Create Schema File

Create `tools/schemas/my_platform_tools.json`:

```json
{
  "platform": "my_platform",
  "description": "Brief description of what this platform does",
  "tools": [
    {
      "name": "my_platform_create_item",
      "description": "Create a new item in My Platform. Returns item ID and details.",
      "platform": "my_platform",
      "parameters": {
        "type": "object",
        "properties": {
          "title": {
            "type": "string",
            "description": "Item title (required)"
          },
          "content": {
            "type": "string",
            "description": "Item content (optional)"
          },
          "tags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of tags (optional)"
          }
        },
        "required": ["title"]
      },
      "returns": {
        "type": "object",
        "description": "Created item with ID, title, and URL"
      },
      "examples": [
        {
          "description": "Create simple item",
          "parameters": {
            "title": "My Item",
            "content": "Item description"
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
            "description": "Max items to return (default: 10)",
            "default": 10
          }
        },
        "required": []
      },
      "returns": {
        "type": "array",
        "description": "List of items with ID, title, and metadata"
      }
    }
  ]
}
```

**Schema Best Practices:**
- Use clear, descriptive tool names: `platform_action_object`
- Include examples for complex tools
- Document all parameters with types and descriptions
- Specify which parameters are required
- Use `type: "object"` with `properties` and `required` array (Format 2)

### Step 2: Create Implementation File

Create `tools/implementations/my_platform.py`:

```python
"""
My Platform Tools - Integration with My Platform API

Functions:
- my_platform_create_item: Create items
- my_platform_list_items: List items
"""

import requests
from typing import Dict, Any, List, Optional

class MyPlatformError(Exception):
    """Custom exception for My Platform errors"""
    pass


def my_platform_create_item(
    title: str,
    content: Optional[str] = None,
    tags: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a new item in My Platform
    
    Args:
        title: Item title (required)
        content: Item content (optional)
        tags: List of tags (optional)
        **kwargs: Credential injection (access_token, etc.)
    
    Returns:
        Dict with item_id, title, url
    
    Raises:
        MyPlatformError: If creation fails
    """
    # Get credentials from kwargs (injected by credential_injector)
    access_token = kwargs.get('access_token')
    if not access_token:
        raise MyPlatformError("access_token required but not provided")
    
    # Build request
    url = "https://api.myplatform.com/v1/items"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "title": title,
        "content": content or "",
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
        **kwargs: Credential injection (access_token, etc.)
    
    Returns:
        List of items with id, title, url
    
    Raises:
        MyPlatformError: If listing fails
    """
    # Get credentials
    access_token = kwargs.get('access_token')
    if not access_token:
        raise MyPlatformError("access_token required")
    
    # Build request
    url = f"https://api.myplatform.com/v1/items?limit={limit}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
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


# Optional: Helper functions (not exposed as tools)
def _validate_item_title(title: str) -> bool:
    """Internal validation function"""
    return len(title) > 0 and len(title) <= 200
```

**Implementation Best Practices:**
- Always accept `**kwargs` for credential injection
- Extract credentials from `kwargs` (access_token, refresh_token, etc.)
- Raise descriptive exceptions on errors
- Return consistent, well-structured data
- Include type hints for all parameters
- Add docstrings for all public functions
- Use custom exception classes for platform-specific errors

### Step 3: Test Your Tool

Create a test script `test_my_platform.py`:

```python
"""Test My Platform tools"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from tools.registry_v3 import RegistryV3

# Load registry
registry = RegistryV3()

# Check if your tools loaded
my_tools = [name for name in registry.tools.keys() if 'my_platform' in name]
print(f"Found {len(my_tools)} My Platform tools:")
for tool in my_tools:
    print(f"  - {tool}")

# Check schema format
for tool_name in my_tools:
    tool = registry.get_tool(tool_name)
    print(f"\n{tool_name} schema:")
    print(f"  Has parameters: {'parameters' in tool}")
    print(f"  Description: {tool.get('description', 'N/A')[:60]}...")

# Get Anthropic-formatted tools
anthropic_tools = registry.get_anthropic_tools()
my_anthropic_tools = [t for t in anthropic_tools if 'my_platform' in t['name']]

print(f"\nAnthropic format validation:")
for tool in my_anthropic_tools:
    has_input_schema = 'input_schema' in tool
    has_type = tool.get('input_schema', {}).get('type') == 'object'
    has_props = 'properties' in tool.get('input_schema', {})
    
    status = "✅" if (has_input_schema and has_type and has_props) else "❌"
    print(f"  {status} {tool['name']}")

# Test tool execution (with mock credentials)
print("\n\nTesting tool execution:")
try:
    # This will fail without real credentials, but tests the function signature
    result = registry.execute_tool(
        'my_platform_list_items',
        limit=5,
        access_token='mock_token_for_testing'
    )
    print(f"✅ Tool execution successful: {result}")
except Exception as e:
    print(f"⚠️  Tool execution failed (expected without real credentials): {e}")
```

Run the test:
```powershell
cd C:\Users\gpoli\GIT\AI_agents
python test_my_platform.py
```

### Step 4: Add Credential Support (If Needed)

If your platform requires OAuth, update `AI_infrastructure/auth/credential_injector.py`:

```python
def get_my_platform_credentials(self, user_id: int) -> Dict[str, str]:
    """Get My Platform credentials for user"""
    conn = self.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT access_token, refresh_token, token_expiry
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
        'access_token': row[0],
        'refresh_token': row[1],
        'token_expiry': row[2]
    }
```

### Step 5: Verify Registry Loading

```powershell
cd C:\Users\gpoli\GIT\AI_agents
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); print(f'Total tools: {len(r.tools)}'); my_tools = [t for t in r.tools if 'my_platform' in t]; print(f'My Platform tools: {len(my_tools)}'); print(my_tools)"
```

Expected output:
```
Total tools: 586  # (584 + your 2 new tools)
My Platform tools: 2
['my_platform_create_item', 'my_platform_list_items']
```

### Step 6: Test in Flask App

Start the server:
```powershell
BISTART
```

Test via API:
```powershell
# Using CHAT command
CHAT "List items from My Platform"

# Or via curl
curl -X POST http://localhost:5001/api/agent/chat `
  -H "Content-Type: application/json" `
  -d '{"message": "List items from My Platform", "user_id": 1}'
```

### Common Issues and Solutions

**Issue: Tool not loading**
- Check schema file is in `tools/schemas/`
- Verify JSON is valid (use JSONLint)
- Check implementation file is in `tools/implementations/`
- Ensure function names match tool names in schema

**Issue: Schema validation errors**
- Use Format 2 (Anthropic native) for new tools
- Ensure `parameters` has `type: "object"`
- Put `required` inside `parameters` as an array
- Include `properties` object

**Issue: Credential injection not working**
- Add `**kwargs` to function signature
- Extract credentials from kwargs: `access_token = kwargs.get('access_token')`
- Update `credential_injector.py` with getter method

**Issue: Tool execution fails**
- Check error messages in Flask logs
- Verify API endpoint is correct
- Test credentials are valid
- Check network connectivity

### Tool Naming Conventions

✅ **Good naming:**
- `gmail_send_email`
- `google_docs_create_document`
- `slack_post_message`
- `stripe_create_customer`

❌ **Bad naming:**
- `sendEmail` (no platform prefix)
- `google_create` (ambiguous action)
- `my-tool-name` (use underscores, not hyphens)

### Complete Example: Stripe Tools

See `tools/schemas/stripe_tools.json` and `tools/implementations/stripe.py` for a complete working example with:
- Multiple tools (9 total)
- Proper error handling
- Credential injection
- Type hints
- Documentation
- Examples

### IMPORTANT: Schema Format Conversion (October 2025 Fix)

The `registry_v3.py` file's `get_anthropic_tools()` method automatically converts **both schema formats** to Anthropic's required format:

**What it does:**
1. **Detects Format 2**: Checks if `parameters` already has `type: "object"`
2. **Direct conversion**: If Format 2, directly copies to `input_schema`
3. **Legacy conversion**: If Format 1, converts flat parameter dict to nested structure

**Result:**
```json
{
  "name": "tool_name",
  "description": "...",
  "input_schema": {
    "type": "object",
    "properties": {...},
    "required": [...]
  }
}
```

**Before this fix (Oct 2025):**
- ~30 warnings: "Unknown parameter format for X.required: <class 'list'>"
- Google Meet/Slides tools had malformed schemas
- Some tools failed Anthropic API validation

**After this fix:**
- ✅ ALL 584 tools have valid schemas
- NO warnings during registry loading
- Both schema formats work correctly
- Full Anthropic API compatibility

**When adding new tools, you can use either format** - the registry will handle the conversion automatically.

## Integration Points

### Flask Routes
```python
# AI_infrastructure/routes/
- agent_routes.py       # Main AI agent conversation endpoints
- thread_routes.py      # Thread management
- export_routes.py      # Export conversations
- task_sync_routes.py   # Universal task sync
- account_linking_routes.py  # OAuth account linking
```

### Authentication Systems
```python
# Google OAuth
from google_workspace.google_auth_manager import GoogleAuthManager

# Microsoft OAuth
from Microsoft_365_Connection.microsoft365_oauth_manager import Microsoft365OAuthManager
```

## Script Organization

### scripts/ Folder Structure
```
scripts/
├── startup/           # BISTART, BISTOP, chat, SYNERGY_START
├── setup/            # setup_master_account, setup_microsoft_login
├── testing/          # test_* files (8 test scripts)
├── maintenance/      # cleanup scripts, fix scripts (8 maintenance scripts)
├── deployment/       # ai_agent_render_deploy
└── utilities/        # task_sync_universal, utility helpers
```

### Script Usage Rules

 **DO** - Keep essential scripts in root:
- `BISTART.bat` / `BISTART.ps1` - Server startup (PATH command)
- `CHAT.bat` / `chat.ps1` - AI agent CLI (PATH command)
- `app.py` - Legacy Flask entry point
- `config.py` - Global API keys

 **DO** - Organize utilities in scripts/:
- Test scripts → `scripts/testing/`
- Setup scripts → `scripts/setup/`
- Maintenance tools → `scripts/maintenance/`

 **DON'T** - Put tool implementations in scripts/:
- Tools belong in `tools/implementations/`
- Keep scripts and tools separate

## Common Anti-Patterns (Avoid)

###  Don't: Static credential checks at init
```python
# Bad - Checking for credentials at class init
class MyTool:
    def __init__(self):
        if not os.getenv('MICROSOFT_GRAPH_ACCESS_TOKEN'):
            print('  Warning: Token not set')  # This will always warn!
```

###  Do: Dynamic credential injection
```python
# Good - Credentials injected at runtime
class MyTool:
    def my_method(self, param1, **kwargs):
        access_token = kwargs.get('access_token')
        if not access_token:
            raise ValueError("access_token required")
        # Use token for API call
```

###  Don't: Import wrong config
```python
# Bad - Tool trying to import Flask Config
from config import Config  # Doesn't exist in root config.py!

# Bad - Flask app trying to import API keys from local config
from config import DEEPSEEK_API_KEYS  # Doesn't exist in AI_infrastructure/config.py!
```

###  Do: Import correct config
```python
# Good - Tool importing API keys from root
from config import get_api_key_enhanced

# Good - Flask app importing from local config
sys.path.insert(0, os.path.dirname(__file__))
from config import Config
```

##  Testing & Debugging

### Tool Registry Testing
```powershell
# Load registry and check tool count
python -c "from tools.registry import ToolRegistry; r = ToolRegistry(); print(f'{len(r.tools)} tools loaded')"

# Check for warnings
python -c "from tools.registry import ToolRegistry; ToolRegistry()"
# Should show NO warnings about MICROSOFT_GRAPH_ACCESS_TOKEN
```

### Flask Startup Testing
```powershell
cd C:\Users\gpoli\GIT\AI_agents\AI_infrastructure
$env:PYTHONIOENCODING="utf-8"
python flask_app.py

# Should start on port 5001 with:
# - 564 tools loaded
# - 35 implementations
# - 19 API endpoints
# - No errors or warnings
```

### Credential Injection Testing
```python
# Test Google credentials
from AI_infrastructure.auth.credential_injector import CredentialInjector
injector = CredentialInjector()
creds = injector.get_google_credentials(user_id=1)
print(creds)  # Should show access_token, refresh_token, etc.

# Test Microsoft credentials
creds = injector.get_microsoft_credentials(user_id=1)
print(creds)  # Should show access_token
```

##  Critical Performance Notes

- **Tool Loading**: 564 tools load in ~2-3 seconds via registry
- **Credential Injection**: Credentials fetched from SQLite on-demand (not at init)
- **API Key Rotation**: Uses round-robin across multiple keys via `get_api_key_enhanced()`
- **Database**: SQLite for user data (`ai_infrastructure.db`) and sessions (`sessions.db`)

## 📚 Documentation Structure

```
docs/
├── archive/          # Archived old documentation (238 files)
├── active/          # Current documentation (21 files)
├── CLEANUP_COMPLETE.md
├── SCRIPT_ORGANIZATION_COMPLETE.md
├── TOOLS_REORGANIZATION_COMPLETE.md
└── IMPORT_FIX_SUMMARY.md
```

## � Documentation Standards (MUST FOLLOW)

### Template System
All documentation follows standardized templates located in `/templates/`:
- `FILE_HEADER_TEMPLATE.md` - Required header for all code files
- `README_TEMPLATE.md` - Required for all folders
- `NOTES_TEMPLATE.md` - Required for active development folders
- `CHANGELOG_TEMPLATE.md` - Required for production code folders
- `INDEX_TEMPLATE.md` - Required for folders with 10+ files
- `AGENT_CONTEXT_TEMPLATE.md` - Required for AI agent specialization

### File Documentation Headers (MANDATORY)

Every code file MUST have a header comment at the top:

**JavaScript/TypeScript:**
```javascript
/**
 * FILE: [full path from project root]
 * PURPOSE: [one-line description]
 * 
 * DEPENDENCIES:
 * - [internal/file.js] ([what it provides])
 * - [package-name] ^[version] ([what it's used for])
 * 
 * EXPORTS:
 * - [functionName(params)] - [description]
 * 
 * USED BY:
 * - [path/to/consumer.js] ([how it's used])
 * 
 * RELATED FILES:
 * - [path/to/related.js] ([relationship])
 * 
 * NOTES:
 * - [Important implementation details]
 * - [Security considerations]
 * - [Known limitations]
 * 
 * LAST MODIFIED: YYYY-MM-DD - [change description]
 */
```

**Python:**
```python
"""
FILE: path/to/file.py
PURPOSE: [one-line description]

DEPENDENCIES:
- internal.module ([what it provides])
- package==version ([what it's used for])

EXPORTS:
- function_name(params: type) -> return_type - [description]

USED BY:
- path.to.consumer ([how it's used])

RELATED FILES:
- path.to.related ([relationship])

NOTES:
- [Important implementation details]
- [Security considerations]
- [Known limitations]

LAST MODIFIED: YYYY-MM-DD - [change description]
"""
```

### Folder Documentation Requirements

**README.md (Required for ALL folders):**
- Overview of folder purpose
- Structure and file listing
- Conventions and patterns used
- Dependencies and related folders
- Agent ownership
- Last updated date

**NOTES.md (Required for ACTIVE DEVELOPMENT folders):**
- Current work in progress
- Agent context (which AI agent is working)
- Decisions made during development
- Questions and blockers
- TODO items
- Session log with dates

**CHANGELOG.md (Required for PRODUCTION CODE folders):**
- Chronological change tracking
- Format: Date → Added/Changed/Fixed/Deprecated/Removed/Security
- Document breaking changes
- Version milestones

**INDEX.md (Required for folders with 10+ files):**
- Complete file inventory
- Brief purpose for each file
- Dependencies and relationships
- Quick reference guide

### Code Update Rules (CRITICAL)

When modifying existing code:
1. ✅ **UPDATE existing files** - Never create duplicates
2. ✅ **UPDATE file header** - Always update LAST MODIFIED field
3. ✅ **UPDATE documentation** - Update README.md, NOTES.md, CHANGELOG.md
4. ✅ **PRESERVE signatures** - Keep existing function signatures unless explicitly changing
5. ✅ **MAINTAIN patterns** - Follow existing error handling and dependency patterns

### Documentation Update Rules

When you create or modify files:
1. Add/update header comment block in the file
2. Update NOTES.md with what you did
3. If changes are significant, update README.md
4. Before deployment, move NOTES.md entries to CHANGELOG.md
5. If adding new files, update INDEX.md (if it exists)

### When Starting Work

1. Check for README.md in the folder - read it first
2. Check for NOTES.md - see current state and decisions
3. Check agent context file in `/agents/` folder
4. Reference these files in your work:
   - `@file:folder/README.md`
   - `@file:folder/NOTES.md`
   - `@file:templates/FILE_HEADER_TEMPLATE.md`

### When Generating Code

1. Follow existing patterns in the codebase
2. Include file header on new files (use template)
3. Add JSDoc/docstring comments for functions
4. Use shared utilities (never duplicate)
5. Follow error handling patterns
6. Use proper logging (never console.log in production)

### Response Format for Documentation

When I ask you to document or create code:
1. Show me the file header first
2. Then show the implementation
3. Then tell me what documentation files need updating
4. List specific changes needed for README.md, NOTES.md, etc.

Example:
```javascript
// [Show file with header]

// Documentation updates needed:
// - Update AI_infrastructure/routes/NOTES.md: Add "Implemented X feature"
// - Update AI_infrastructure/routes/CHANGELOG.md: Add to "Added" section
// - Update AI_infrastructure/routes/README.md: Add X to feature list
```

### Shared Code Rules

Use utilities in `AI_infrastructure/shared/`:
- Never create custom versions in feature code
- Always import from shared modules
- Follow established patterns

### Template Usage with AI

Reference templates when creating files:
```
@file:templates/FILE_HEADER_TEMPLATE.md
Create AI_infrastructure/services/newService.py with proper header
```

```
@file:templates/README_TEMPLATE.md
Create README.md for the new /services folder
```

```
@file:templates/AGENT_CONTEXT_TEMPLATE.md
Create agent context for the Authentication Agent
```

## �🔒 Environment Variables

### Required in .env.master
```bash
# AI Provider Keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY_1=sk-...

# Microsoft OAuth
MICROSOFT_CLIENT_ID=...
MICROSOFT_CLIENT_SECRET=...
MICROSOFT_TENANT_ID=common

# Google OAuth (uses service-account.json)
# No env vars needed for Google - uses service account file

# Database
# Automatically created in AI_infrastructure/data/
```

---

##  Communication Preferences

**User prefers updates in CHAT only, not terminal commands.**

When completing tasks:
-  **DO**: Provide status updates and summaries directly in chat responses
-  **DON'T**: Use `run_in_terminal` with `Write-Host` commands for summaries
-  **DO**: Use terminal only for functional commands (running scripts, checking status, etc.)
-  **DON'T**: Generate colorful PowerShell reports - just explain changes conversationally

---

##  Quick Reference Checklist

### Before Making Changes:
- [ ] Understand which config file to import (root for tools, AI_infrastructure for Flask)
- [ ] Check if script belongs in `scripts/` or `tools/implementations/`
- [ ] Verify tool implementations use credential injection (not static checks)
- [ ] Test tool loading: `python -c "from tools.registry import ToolRegistry; ToolRegistry()"`
- [ ] Test Flask startup: `cd AI_infrastructure; python flask_app.py`

### After Making Changes:
- [ ] No warnings about MICROSOFT_GRAPH_ACCESS_TOKEN
- [ ] Flask starts successfully on port 5001
- [ ] All 564 tools load without errors
- [ ] Correct config imports (root vs AI_infrastructure)
- [ ] Scripts organized in proper folders

---

# CRITICAL RULE:  NO EMOJIS IN YOUR CODE or TEST SCRIPTS - NO FUKING EMOJIS - the cause UnicodeEncodeError!!!


**Last Updated:** November 1, 2025  
**Version:** 1.2.0  
**Status:** Production Ready (with Calculator Integration + Google Sheets Markdown Formatting)
