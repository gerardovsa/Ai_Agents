# Tool Construction Process - Complete Guide

## Overview

This guide explains how to create tools for the AI Agent platform using the **progressive discovery architecture**. Understanding this pattern is CRITICAL for building tools that AI agents can discover and use effectively.

---

## Core Philosophy: Progressive Discovery

### The Problem We Solve

**OLD WAY (Bad):**
- Put ALL tool instructions in system prompt
- 646 tools × 50 lines each = 32,300 lines
- Exceeds token limits
- Slow, expensive, cluttered

**OUR WAY (Good):**
- System prompt: Brief mentions only (3-4 lines per tool category)
- Tool schemas: Full instructions, examples, workflows
- AI discovers tools on-demand using meta-tools
- Scales infinitely, stays under token limits

---

## The Progressive Discovery Flow

```
User Request: "Send an email"
        ↓
AI reads system prompt: "For email, use meta-tools to discover"
        ↓
AI calls: list_available_platforms()
        ↓
Returns: ["gmail", "microsoft_outlook", "slack", ...]
        ↓
AI calls: list_platform_tools("gmail")
        ↓
Returns: ["gmail_send_email", "gmail_create_draft", ...]
        ↓
AI calls: get_tool_schema("gmail_send_email")
        ↓
Returns: FULL INSTRUCTIONS from schema
        ↓
AI reads schema: parameters, examples, best practices
        ↓
AI calls: gmail_send_email(to="...", subject="...", body="...")
        ↓
Success!
```

**Key Insight:** The AI doesn't need to know EVERYTHING upfront. It learns what it needs, when it needs it.

---

## Architecture: Three Layers

### Layer 1: System Prompt (Brief Overview)
**File:** `AI_infrastructure/prompts/tool_usage_system_prompt.md`

**Purpose:** High-level guidance, NOT detailed instructions

**What to include:**
- Tool category exists
- Brief 1-line purpose
- Pointer to use meta-tools for discovery

**What NOT to include:**
- Long examples
- Parameter lists
- Step-by-step workflows
- Edge cases

**Example:**
```markdown
## MULTI-AGENT COORDINATION

You have 26 AI agent threads (Alpha-Zulu, or agent-1 through agent-26) for distributing complex work.

**Tools:** Use `list_platform_tools("advanced_agent_coordination")` to discover coordination tools.
**Key Tool:** `assign_and_activate_agent_with_slugs` - Assigns work to agents with UI automation.

Call `get_tool_schema(tool_name)` for detailed instructions.
```

**That's it!** 4 lines, not 150 lines.

---

### Layer 2: Tool Schema (Full Instructions)
**File:** `tools/schemas/your_platform_tools.json`

**Purpose:** Complete documentation that AI reads on-demand

**What to include:**
- ✅ Detailed description
- ✅ All parameters with types, descriptions, defaults
- ✅ Multiple examples (simple → complex)
- ✅ Common patterns and workflows
- ✅ Error handling guidance
- ✅ Best practices
- ✅ Related tools
- ✅ When to use vs when NOT to use

**Critical Understanding:**
The tool schema is NOT just parameter definitions - it's the AI's INSTRUCTION MANUAL for that tool.

---

### Layer 3: Tool Implementation (Python Code)
**File:** `tools/implementations/your_platform.py`

**Purpose:** Executes the actual logic

**What to include:**
- ✅ Function matching schema name exactly
- ✅ Parameter validation
- ✅ Error handling with descriptive messages
- ✅ Return structured data (dicts/lists)
- ✅ Docstrings explaining behavior

---

## Creating a New Tool: Step-by-Step

### Step 1: Add Brief Mention to System Prompt

**Location:** `AI_infrastructure/prompts/tool_usage_system_prompt.md`

Find an appropriate section (or create new one) and add:

```markdown
## YOUR PLATFORM NAME

Brief description of what this platform does (1-2 sentences).

**Tools:** Use `list_platform_tools("your_platform")` to discover available tools.
**Key Tools:**
- `your_platform_main_action` - Brief description
- `your_platform_secondary_action` - Brief description

Call `get_tool_schema(tool_name)` for detailed parameters and examples.
```

**Guidelines:**
- Keep to 3-5 lines total
- Don't include examples
- Don't list all parameters
- Don't explain workflows
- DO mention when to use this vs other platforms

---

### Step 2: Create Tool Schema (THE MOST IMPORTANT PART)

**Location:** `tools/schemas/your_platform_tools.json`

**Template:**

```json
{
  "platform": "your_platform",
  "description": "Comprehensive description of what this platform integration does. Explain the use cases, capabilities, and limitations.",
  "tools": [
    {
      "name": "your_platform_action_name",
      "description": "DETAILED description of what this specific tool does. Explain the expected outcome, any side effects, and what gets returned. This is the AI's PRIMARY instruction source - be thorough!",
      "platform": "your_platform",
      "parameters": {
        "type": "object",
        "properties": {
          "required_param": {
            "type": "string",
            "description": "DETAILED explanation of this parameter. Include: what it's for, format requirements, validation rules, examples of valid values, and what happens if invalid."
          },
          "optional_param": {
            "type": "integer",
            "description": "Detailed explanation. Always state if optional and provide default value.",
            "default": 100
          },
          "enum_param": {
            "type": "string",
            "description": "Parameter with limited choices. Explain WHEN to use each option.",
            "enum": ["option1", "option2", "option3"]
          }
        },
        "required": ["required_param"]
      },
      "returns": {
        "type": "object",
        "description": "DETAILED explanation of return value structure. Include all fields, their types, and what they mean.",
        "properties": {
          "success": {
            "type": "boolean",
            "description": "Whether operation succeeded"
          },
          "result_id": {
            "type": "string",
            "description": "ID of created/modified resource"
          },
          "data": {
            "type": "object",
            "description": "Additional data returned"
          }
        }
      },
      "examples": [
        {
          "description": "Simple common use case - this is the FIRST thing AI will try",
          "parameters": {
            "required_param": "simple_value",
            "optional_param": 50
          }
        },
        {
          "description": "Complex use case with all options - shows full capabilities",
          "parameters": {
            "required_param": "complex_value",
            "optional_param": 200,
            "enum_param": "option2"
          }
        },
        {
          "description": "Edge case or specific scenario - helps AI understand limits",
          "parameters": {
            "required_param": "edge_case_value"
          }
        }
      ],
      "usage_guide": {
        "when_to_use": [
          "Use this tool when user explicitly requests X",
          "Use when you need to Y",
          "Use as part of workflow involving Z"
        ],
        "when_not_to_use": [
          "Don't use for simple A - use simpler_tool instead",
          "Don't use if B condition - not supported",
          "Don't use for C - use platform_other_tool instead"
        ],
        "common_patterns": [
          {
            "pattern": "Create → Update → Verify workflow",
            "steps": [
              "1. Call your_platform_create(...)",
              "2. Get result_id from response",
              "3. Call your_platform_update(result_id, ...)",
              "4. Call your_platform_get(result_id) to verify"
            ]
          }
        ],
        "best_practices": [
          "Always validate X before calling",
          "Check Y field in return value for status",
          "Use Z parameter for better performance"
        ],
        "error_handling": [
          {
            "error": "ResourceNotFound",
            "meaning": "The specified resource doesn't exist",
            "solution": "Verify resource ID is correct, or create resource first"
          },
          {
            "error": "InvalidParameter",
            "meaning": "A parameter value is invalid",
            "solution": "Check parameter format in schema, ensure enum values match exactly"
          }
        ]
      },
      "related_tools": [
        "your_platform_other_tool - Use this for follow-up actions",
        "different_platform_similar_tool - Alternative approach for same outcome"
      ]
    }
  ]
}
```

### CRITICAL SCHEMA PRINCIPLES

#### 1. The Schema IS the Prompt

When AI calls `get_tool_schema("your_tool")`, it receives this JSON and reads it as INSTRUCTIONS.

Think of schema fields as:
- `description` = Main instruction text
- `parameters.properties.param.description` = Parameter-specific instructions
- `examples` = Visual demonstrations
- `usage_guide` = Advanced instructions
- `returns.description` = What to expect back

#### 2. Be Extremely Detailed in Descriptions

**BAD:**
```json
"description": "Creates a resource"
```

**GOOD:**
```json
"description": "Creates a new resource in the platform with the specified parameters. The resource is immediately active and can be used in subsequent operations. Returns the resource ID which you MUST save for future updates or deletions. The operation is idempotent - calling with the same parameters twice will return the existing resource rather than creating a duplicate."
```

#### 3. Parameter Descriptions Are Instructions

**BAD:**
```json
"email": {
  "type": "string",
  "description": "Email address"
}
```

**GOOD:**
```json
"email": {
  "type": "string",
  "description": "Recipient email address. Must be valid email format (user@domain.com). If sending to multiple recipients, use comma-separated list: 'user1@example.com,user2@example.com'. Maximum 50 recipients per call. For more recipients, make multiple calls or use batch_send tool instead."
}
```

#### 4. Examples Are Critical

AI learns by example. Provide:
- **Simple example** (80% of use cases)
- **Complex example** (full features)
- **Edge case example** (limits/special scenarios)

**Template:**
```json
"examples": [
  {
    "description": "Basic use case - most common scenario",
    "parameters": {
      "required_field": "typical_value"
    }
  },
  {
    "description": "Advanced use case - showing all options",
    "parameters": {
      "required_field": "value",
      "optional_field_1": "advanced_value",
      "optional_field_2": true,
      "nested_object": {
        "sub_field": "detailed_example"
      }
    }
  },
  {
    "description": "Edge case - handling special situation",
    "parameters": {
      "required_field": "edge_case_value",
      "special_flag": true
    }
  }
]
```

#### 5. Usage Guide = Advanced Prompting

The `usage_guide` section is where you teach AI:

**When to use:**
```json
"when_to_use": [
  "User explicitly asks to 'create X'",
  "You need to store data persistently",
  "As part of multi-step workflow where X is required",
  "When simpler_tool fails due to limitations"
]
```

**When NOT to use:**
```json
"when_not_to_use": [
  "For read-only operations - use get_tool instead",
  "If resource already exists - use update_tool instead",
  "For temporary data - store in memory, don't create resource",
  "If user hasn't confirmed - ask first before creating"
]
```

**Common patterns:**
```json
"common_patterns": [
  {
    "pattern": "Create-Update-Notify workflow",
    "description": "Standard flow for user-requested resource creation",
    "steps": [
      "1. Validate user input parameters",
      "2. Call create_tool(...) to create resource",
      "3. Extract resource_id from response",
      "4. Call update_tool(resource_id, ...) to add details",
      "5. Call notify_tool(...) to inform user",
      "6. Return resource_id to user for future reference"
    ],
    "example": "When user says 'Create a doc and share with team'"
  }
]
```

**Best practices:**
```json
"best_practices": [
  "Always store returned resource_id - you'll need it for updates",
  "Check 'status' field in response before proceeding",
  "Use batch operations for >10 items (call batch_tool instead)",
  "Set timeout_seconds parameter for long operations",
  "Include descriptive titles/names - helps user identify resources later"
]
```

**Error handling:**
```json
"error_handling": [
  {
    "error": "DuplicateResource",
    "meaning": "A resource with this name/ID already exists",
    "solution": "Check if resource exists first using list_tool or get_tool. If exists, use update_tool instead of create_tool. Or append timestamp to name to make unique.",
    "example": "If creating 'Report' fails, try 'Report 2024-11-22' or update existing"
  },
  {
    "error": "QuotaExceeded",
    "meaning": "User has reached platform limit for this resource type",
    "solution": "1. Check current quota with get_quota_tool. 2. Delete old unused resources. 3. Ask user to upgrade plan. 4. Use alternative approach if available.",
    "prevention": "Call get_quota_tool BEFORE creating many resources"
  }
]
```

---

### Step 3: Create Implementation

**Location:** `tools/implementations/your_platform.py`

**Template:**

```python
"""
Your Platform Tools - Integration with Platform API

Functions:
- your_platform_action_name: Creates/updates/deletes resources
- your_platform_secondary_action: Alternative operation

Each function accepts **kwargs for credential injection.
"""

import requests
from typing import Dict, Any, List, Optional


class YourPlatformError(Exception):
    """Custom exception for platform-specific errors"""
    pass


def your_platform_action_name(
    required_param: str,
    optional_param: int = 100,
    enum_param: str = "option1",
    **kwargs
) -> Dict[str, Any]:
    """
    Detailed docstring explaining what this function does.
    
    This docstring is for DEVELOPERS, not AI. Keep it concise.
    The AI reads the schema description, not this.
    
    Args:
        required_param: Brief explanation
        optional_param: Brief explanation (default: 100)
        enum_param: Brief explanation (default: "option1")
        **kwargs: Injected credentials (access_token, etc.)
    
    Returns:
        Dict with:
            - success: bool
            - resource_id: str
            - data: Dict with resource details
    
    Raises:
        YourPlatformError: If operation fails
    """
    
    # 1. Get credentials from kwargs (injected by credential_injector)
    access_token = kwargs.get('access_token')
    if not access_token:
        raise YourPlatformError("access_token required but not provided")
    
    # 2. Validate parameters
    if not required_param:
        raise YourPlatformError("required_param cannot be empty")
    
    valid_enums = ["option1", "option2", "option3"]
    if enum_param not in valid_enums:
        raise YourPlatformError(f"enum_param must be one of {valid_enums}")
    
    # 3. Build API request
    api_url = "https://api.yourplatform.com/v1/resource"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "required_field": required_param,
        "optional_field": optional_param,
        "enum_field": enum_param
    }
    
    # 4. Make API call with error handling
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # 5. Return structured response
        return {
            "success": True,
            "resource_id": data.get("id"),
            "resource_url": data.get("url"),
            "data": {
                "name": data.get("name"),
                "status": data.get("status"),
                "created_at": data.get("created_at")
            }
        }
        
    except requests.exceptions.HTTPError as e:
        # Parse error from API response
        error_msg = "Unknown error"
        try:
            error_data = e.response.json()
            error_msg = error_data.get("message", str(e))
        except:
            error_msg = str(e)
        
        raise YourPlatformError(f"API request failed: {error_msg}")
    
    except requests.exceptions.RequestException as e:
        raise YourPlatformError(f"Network error: {str(e)}")


# Helper functions (not exposed as tools)
def _validate_email(email: str) -> bool:
    """Internal validation function"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

**Key Implementation Principles:**

1. **Always accept `**kwargs`** - Credentials are injected at runtime
2. **Extract credentials from kwargs** - Don't use global variables
3. **Validate inputs** - Provide clear error messages
4. **Handle errors gracefully** - Catch and re-raise with context
5. **Return structured data** - Consistent dict format
6. **Use type hints** - Helps with validation
7. **Keep it simple** - Complex logic belongs in helper functions

---

## Meta-Tools: The Discovery System

### Understanding Meta-Tools

Meta-tools are tools that help AI discover other tools. They're the foundation of progressive learning.

### Core Meta-Tools

#### 1. `list_available_platforms()`

**What it does:** Returns list of all platform names

**When AI uses it:** 
- First time in conversation when user asks about capabilities
- When user asks "what can you do?"
- When unsure which platform to use

**Returns:**
```json
{
  "platforms": [
    "gmail",
    "google_docs",
    "microsoft_outlook",
    "slack",
    "stripe",
    "advanced_agent_coordination",
    ...
  ],
  "count": 42
}
```

#### 2. `list_platform_tools(platform_name)`

**What it does:** Returns all tools for a specific platform

**When AI uses it:**
- After seeing platform name from list_available_platforms
- When user mentions a platform ("use Gmail")
- When starting work with a new platform

**Returns:**
```json
{
  "platform": "gmail",
  "tools": [
    {
      "name": "gmail_send_email",
      "description": "Send email to recipients"
    },
    {
      "name": "gmail_create_draft",
      "description": "Create email draft"
    },
    ...
  ],
  "count": 15
}
```

#### 3. `get_tool_schema(tool_name)`

**What it does:** Returns COMPLETE schema for specific tool

**When AI uses it:**
- Before calling any tool for the first time
- When user asks about specific tool capabilities
- When previous tool call failed (re-read to check parameters)

**Returns:**
```json
{
  "name": "gmail_send_email",
  "description": "FULL DETAILED DESCRIPTION...",
  "parameters": { /* complete parameter definitions */ },
  "returns": { /* return value structure */ },
  "examples": [ /* all examples */ ],
  "usage_guide": { /* when to use, patterns, best practices */ }
}
```

**THIS IS THE KEY MOMENT:** When AI reads this, it learns everything about the tool.

#### 4. `recommend_tools_for_task(task_description)`

**What it does:** AI-powered tool recommendation

**When AI uses it:**
- When multiple tools could work
- When unsure which approach is best
- When user's request is ambiguous

**Returns:**
```json
{
  "recommendations": [
    {
      "tool": "gmail_smart_compose_and_send",
      "confidence": 0.95,
      "reason": "Best for rich HTML emails with attachments",
      "alternative": "gmail_send_email for simple text emails"
    }
  ]
}
```

---

## Progressive Learning in Action: Complete Example

### User Request:
> "Assign the frontend work to Agent Alpha"

### AI's Progressive Discovery Process:

**Step 1: Check System Prompt**

AI reads:
```markdown
## MULTI-AGENT COORDINATION

You have 26 AI agent threads for distributing complex work.

Tools: Use list_platform_tools("advanced_agent_coordination") to discover.
Key Tool: assign_and_activate_agent_with_slugs
```

AI thinks: "I need coordination tools. Let me discover them."

---

**Step 2: Call Meta-Tool**

```python
AI calls: list_platform_tools("advanced_agent_coordination")
```

Returns:
```json
{
  "platform": "advanced_agent_coordination",
  "tools": [
    {
      "name": "assign_and_activate_agent_with_slugs",
      "description": "Assigns work to agent threads with UI automation"
    },
    {
      "name": "request_update_from_thread",
      "description": "Cross-thread communication"
    },
    {
      "name": "respond_to_cross_thread_request",
      "description": "Respond to requests from other agents"
    }
  ]
}
```

AI thinks: "assign_and_activate_agent_with_slugs looks right. Let me learn more."

---

**Step 3: Get Full Schema**

```python
AI calls: get_tool_schema("assign_and_activate_agent_with_slugs")
```

Returns: **FULL SCHEMA** with:
- Detailed description (explains UI commands)
- All parameters (target_agent, thread_title, instructions, slugs, auto_trigger, open_ui)
- Parameter descriptions (NATO names, agent locations, what each does)
- Examples (simple → complex scenarios)
- Usage guide (when to use, patterns, best practices)
- Error handling (what can go wrong, how to fix)
- Related tools (other coordination tools)

AI reads all of this and thinks: "Now I understand! I need to:
1. Use target_agent='Alpha'
2. Set thread_title descriptive
3. Provide detailed instructions
4. Set open_ui=True to get UI commands
5. Returns ui_commands array that frontend processes"

---

**Step 4: Execute Tool**

```python
AI calls: assign_and_activate_agent_with_slugs(
    target_agent="Alpha",
    thread_title="Frontend Development",
    instructions="Build React frontend for e-commerce platform",
    open_ui=True
)
```

Returns:
```json
{
  "success": true,
  "thread_id": "abc-123",
  "ui_commands": [
    {"command": "switch_tab", "tab_name": "multi-agent"},
    {"command": "open_agent_column", "agent_number": 1}
  ]
}
```

---

**Step 5: Report to User**

AI response:
```
✅ Work assigned to Agent Alpha

Thread: Frontend Development
Location: agent-1 (Alpha)
Status: Ready (awaiting manual trigger)

The Multi-Agent tab will automatically open with Alpha's column visible.
```

---

**Total Token Usage:**

- System prompt mention: ~50 tokens (brief overview)
- list_platform_tools: ~200 tokens (tool names list)
- get_tool_schema: ~1,500 tokens (full instructions)
- **Total: ~1,750 tokens**

**vs. putting everything in system prompt: ~2,500 tokens × always loaded**

**Savings:** Only pays for what it uses, when it uses it.

---

## Common Mistakes When Creating Tools

### Mistake 1: Putting Too Much in System Prompt

**DON'T:**
```markdown
## MY NEW TOOL

This tool does X by calling API Y with parameters A, B, C.

Parameters:
- param_a: string - description (required)
- param_b: integer - description (optional, default: 100)
- param_c: boolean - description (optional, default: false)

Examples:
1. Simple case: my_tool(param_a="value")
2. Complex case: my_tool(param_a="value", param_b=200, param_c=true)

Best practices:
- Always validate param_a
- Use param_b=50 for better performance
- Set param_c=true only when needed

Returns: {success, result_id, data}

Errors:
- InvalidParam: check parameter format
- QuotaExceeded: user needs upgrade
```

**DO:**
```markdown
## MY NEW TOOL

Tool for X. Use list_platform_tools("my_platform") to discover.
Call get_tool_schema("my_tool") for parameters.
```

### Mistake 2: Vague Schema Descriptions

**DON'T:**
```json
{
  "name": "my_tool",
  "description": "Does something useful",
  "parameters": {
    "type": "object",
    "properties": {
      "input": {
        "type": "string",
        "description": "Input value"
      }
    }
  }
}
```

**DO:**
```json
{
  "name": "my_tool",
  "description": "Creates a new resource in the platform with the specified parameters. The resource becomes immediately active and returns an ID that MUST be saved for future updates. Operation is idempotent - duplicate calls return existing resource. Typical use case: When user requests 'create X', this is the primary tool. For modifications, use update_tool instead.",
  "parameters": {
    "type": "object",
    "properties": {
      "input": {
        "type": "string",
        "description": "Resource name/title. Must be unique within user's account. Length: 3-100 characters. Valid characters: letters, numbers, spaces, hyphens. Examples: 'My Project', 'Q4-Report-2024'. If name exists, tool returns existing resource ID rather than creating duplicate."
      }
    }
  }
}
```

### Mistake 3: Missing Examples

**DON'T:**
```json
{
  "examples": [
    {
      "description": "Example",
      "parameters": {"field": "value"}
    }
  ]
}
```

**DO:**
```json
{
  "examples": [
    {
      "description": "Simple case - most common scenario (80% of use)",
      "parameters": {
        "required_field": "typical_value"
      },
      "expected_result": {
        "success": true,
        "resource_id": "abc123"
      },
      "notes": "This is the baseline. If user just says 'create X', use these defaults."
    },
    {
      "description": "Complex case - showing all optional parameters",
      "parameters": {
        "required_field": "value",
        "optional_field_1": "advanced_setting",
        "optional_field_2": true,
        "nested_config": {
          "sub_option": "detailed_value"
        }
      },
      "expected_result": {
        "success": true,
        "resource_id": "xyz789",
        "additional_data": {...}
      },
      "notes": "Use when user explicitly requests advanced features or custom configuration."
    },
    {
      "description": "Edge case - handling special situation",
      "parameters": {
        "required_field": "special_format_value",
        "edge_case_flag": true
      },
      "expected_result": {
        "success": true,
        "warning": "Special handling applied"
      },
      "notes": "Use when X condition. Common in scenario Y. Fallback if normal approach fails."
    }
  ]
}
```

### Mistake 4: No Usage Guide

**DON'T:**
Just parameters and examples.

**DO:**
```json
{
  "usage_guide": {
    "when_to_use": [
      "User explicitly requests 'create X'",
      "Need persistent storage (not temporary)",
      "As first step in Create → Configure → Activate workflow",
      "When list_tool shows resource doesn't exist yet"
    ],
    "when_not_to_use": [
      "Resource already exists - use update_tool instead (check first with get_tool)",
      "For temporary data - just store in memory",
      "User hasn't confirmed - ask before creating",
      "For read-only needs - use get_tool instead"
    ],
    "common_patterns": [...],
    "best_practices": [...],
    "error_handling": [...]
  }
}
```

### Mistake 5: Weak Error Messages

**Implementation DON'T:**
```python
def my_tool(param):
    if not param:
        raise Exception("Error")
```

**Implementation DO:**
```python
def my_tool(param):
    if not param:
        raise MyToolError(
            "Parameter 'param' is required but was not provided. "
            "This parameter specifies the resource name and must be "
            "a non-empty string between 3-100 characters. "
            "Example: 'My Resource Name'"
        )
```

**Schema DON'T:**
```json
{
  "error_handling": [
    {"error": "ParamError", "solution": "Fix parameter"}
  ]
}
```

**Schema DO:**
```json
{
  "error_handling": [
    {
      "error": "ParamError: Parameter 'param' is required",
      "meaning": "The 'param' parameter was not provided or was empty/null",
      "solution": "1. Check that you're passing 'param' in the function call. 2. Verify the value is not empty, null, or undefined. 3. Ensure format matches schema (string, 3-100 chars). 4. Example correct call: my_tool(param='Valid Name')",
      "prevention": "Always call get_tool_schema() first to see required parameters. Mark required params clearly in your internal checklist before calling tool.",
      "common_cause": "Forgot to extract param from user's message, or tried to use undefined variable"
    }
  ]
}
```

---

## Testing Your Tool

### Test Checklist:

1. **Schema Validation**
   - [ ] File is valid JSON
   - [ ] Tool name matches implementation function name exactly
   - [ ] All parameters have descriptions
   - [ ] Required parameters listed in "required" array
   - [ ] At least 2-3 examples provided
   - [ ] Usage guide section included

2. **Implementation Testing**
   - [ ] Function accepts **kwargs
   - [ ] Credentials extracted from kwargs
   - [ ] Parameters validated with clear error messages
   - [ ] Returns structured dict (not string)
   - [ ] Errors raised with descriptive messages
   - [ ] Type hints present

3. **Progressive Discovery Testing**
   - [ ] Tool appears in list_platform_tools() output
   - [ ] get_tool_schema() returns full schema
   - [ ] Schema description is detailed enough to use tool without guessing
   - [ ] Examples cover common use cases
   - [ ] Error handling guide helps AI recover from failures

4. **Integration Testing**
   - [ ] Add tool to registry (registry_v3.py will auto-load from schema)
   - [ ] Test with AI: "Use [platform] to [action]"
   - [ ] Verify AI calls list_platform_tools → get_tool_schema → your_tool
   - [ ] Check AI reads schema and uses tool correctly
   - [ ] Verify errors are handled gracefully

---

## Best Practices Summary

### System Prompt

✅ **DO:**
- Brief mention (3-4 lines)
- State tool exists
- Point to meta-tools for discovery
- Explain one-line purpose

❌ **DON'T:**
- Long examples
- Parameter lists
- Workflows
- Edge cases

### Tool Schema

✅ **DO:**
- EXTREMELY detailed descriptions
- Multiple examples (simple → complex → edge)
- Complete usage_guide section
- Comprehensive error_handling guide
- Clear when_to_use / when_not_to_use
- Common patterns section
- Related tools list

❌ **DON'T:**
- Assume AI knows anything
- Use vague descriptions
- Skip examples
- Forget usage_guide
- Leave out error handling

### Tool Implementation

✅ **DO:**
- Accept **kwargs for credentials
- Validate all inputs
- Descriptive error messages
- Return structured data
- Type hints everywhere
- Handle network errors

❌ **DON'T:**
- Use global credentials
- Silent failures
- Return strings instead of dicts
- Assume valid input
- Forget error context

---

## The Schema Is a Prompt

**Remember:** When AI calls `get_tool_schema()`, it's not just reading parameter definitions - it's receiving INSTRUCTIONS on how to use the tool.

Think of every field as prompting the AI:

| Field | What AI Learns |
|-------|----------------|
| `description` | What this tool does and when to use it |
| `parameters.properties.X.description` | How to use parameter X correctly |
| `examples` | Patterns to follow |
| `usage_guide.when_to_use` | Trigger conditions |
| `usage_guide.when_not_to_use` | Avoidance conditions |
| `usage_guide.common_patterns` | Workflows to follow |
| `usage_guide.best_practices` | Optimization tips |
| `usage_guide.error_handling` | Recovery strategies |
| `returns.description` | What to expect and how to use result |

**Every word matters.** The AI reads this ONCE and uses it to make decisions.

---

## Example: Well-Constructed Tool

See `tools/schemas/advanced_agent_coordination_tools.json` for a complete example following all these principles:

- ✅ Brief system prompt mention (4 lines)
- ✅ Detailed schema descriptions
- ✅ Multiple examples (simple → complex)
- ✅ Complete usage_guide
- ✅ Error handling guide
- ✅ Common patterns
- ✅ Best practices
- ✅ Related tools

Result: AI can discover and use this tool effectively with ZERO training.

---

## Summary: The Progressive Discovery Loop

```
System Prompt (brief overview)
        ↓
    User Request
        ↓
AI: "Need tools for X"
        ↓
list_available_platforms()
        ↓
AI: "Platform Y has relevant tools"
        ↓
list_platform_tools("Y")
        ↓
AI: "Tool Z looks right"
        ↓
get_tool_schema("Z")
        ↓
AI: *reads complete instructions*
        ↓
AI: "Now I understand everything"
        ↓
    Execute Tool Z
        ↓
    Success!
```

**Key Insight:** Each step is cheap (small token cost), but together they enable the AI to learn on-demand without bloating the system prompt.

---

## Conclusion

Building tools for this platform is about **empowering progressive discovery**, not front-loading knowledge.

**The Pattern:**
1. System prompt: "Tool exists, use meta-tools to learn"
2. Tool schema: Complete instructions, examples, patterns
3. Implementation: Robust execution with good errors

**The Result:**
AI agents that can discover, learn, and use 646+ tools effectively while staying within token limits.

**Remember:**
- The schema IS the prompt
- Every description is an instruction
- Examples teach patterns
- Usage guides prevent mistakes
- Error handling enables recovery

**Build tools that teach themselves.**

---

**Document Version:** 1.0  
**Date:** November 22, 2025  
**Status:** Complete Guide  
**Audience:** AI tool developers, system architects  
**Purpose:** Standardize tool construction for progressive discovery
