"""
Meta-Tools Implementation - Tool discovery and guidance

These meta-tools help Claude discover and use the 604+ available tools
Uses registry directly (no external dependencies)
"""

from typing import Dict, Any, List, Optional


def list_available_platforms(**kwargs) -> Dict[str, Any]:
    """
    List all platforms that have tools available
    
    Returns:
        Dict with platforms list and tool counts per platform
    """
    from tools.registry_v3 import get_registry
    
    registry = get_registry()
    
    # Group tools by platform
    platform_counts = {}
    for tool_name, tool in registry.tools.items():
        platform = tool.get("platform", "unknown")
        platform_counts[platform] = platform_counts.get(platform, 0) + 1
    
    # Remove meta_tools from main list
    platforms = [p for p in sorted(platform_counts.keys()) if p != "meta_tools"]
    
    return {
        "success": True,
        "platforms": platforms,
        "platform_count": len(platforms),
        "tool_counts": {p: platform_counts[p] for p in platforms},
        "total_tools": sum(platform_counts[p] for p in platforms)
    }


def list_platform_tools(platform: str, **kwargs) -> Dict[str, Any]:
    """
    List all tools for a platform - NAMES AND DESCRIPTIONS ONLY (no parameter schemas)
    
    Returns a simple list of tool names and what they do.
    If you need to know how to use a tool, call get_tool_schema(tool_name).
    
    Supports fuzzy platform name matching:
    - "microsoft" matches: microsoft_outlook, microsoft_calendar, etc.
    - "m365" fuzzy matches to Microsoft 365 tools
    - "office" fuzzy matches to Microsoft Office tools
    - "google" matches: google_forms, google_sheets, gmail, etc.
    
    Args:
        platform: Platform name (e.g., 'google_forms', 'microsoft_outlook', 'gmail')
                 or platform group ('microsoft', 'google', 'm365', 'office')
    
    Returns:
        Dict with list of tool names and short descriptions
    """
    from tools.registry_v3 import get_registry
    from difflib import SequenceMatcher
    
    registry = get_registry()
    platform_lower = platform.lower()
    
    # Define platform aliases for fuzzy matching
    # Maps common names to actual platform names in registry
    platform_aliases = {
        'microsoft': ['microsoft_calendar', 'microsoft_outlook', 'microsoft_teams', 'microsoft_onedrive', 'microsoft_todo'],
        'microsoft 365': ['microsoft_calendar', 'microsoft_outlook', 'microsoft_teams', 'microsoft_onedrive', 'microsoft_todo'],
        'm365': ['microsoft_calendar', 'microsoft_outlook', 'microsoft_teams', 'microsoft_onedrive', 'microsoft_todo'],
        'office': ['microsoft_outlook', 'microsoft_word_tools', 'microsoft_excel_tools', 'microsoft_onedrive', 'microsoft_teams'],
        'office 365': ['microsoft_calendar', 'microsoft_outlook', 'microsoft_teams', 'microsoft_onedrive', 'microsoft_todo'],
        'outlook': 'microsoft_outlook',
        'teams': 'microsoft_teams',
        'onedrive': 'microsoft_onedrive',
        'todo': 'microsoft_todo',
        'word': 'microsoft_word_tools',
        'excel': 'microsoft_excel_tools',
        'onenote': 'microsoft_onenote_tools',
        'forms': 'microsoft_forms_tools',
        'sharepoint': 'microsoft_sharepoint_tools',
        'google': ['gmail', 'google_sheets', 'google_docs', 'google_forms', 'google_calendar', 'google_drive', 'google_tasks'],
        'google workspace': ['gmail', 'google_sheets', 'google_docs', 'google_forms', 'google_calendar', 'google_drive'],
        'gmail': 'gmail',
        'sheets': 'google_sheets',
        'docs': 'google_docs',
        'drive': 'google_drive',
        'calendar': ['google_calendar', 'microsoft_calendar'],
    }
    
    # Try direct platform match first
    tool_list = []
    matched_platform = None
    
    # 1. Exact match
    for tool_name, tool in registry.tools.items():
        if tool.get("platform") == platform_lower:
            tool_list.append({
                "name": tool_name,
                "description": tool.get("description", "")
            })
            matched_platform = platform_lower
    
    # 2. If no exact match, try fuzzy platform aliases
    if not tool_list:
        for alias, platforms in platform_aliases.items():
            if alias.lower() == platform_lower:
                # Exact alias match
                if isinstance(platforms, list):
                    # Multiple platforms (e.g., 'microsoft' maps to multiple platform names)
                    for tool_name, tool in registry.tools.items():
                        if tool.get("platform") in platforms:
                            tool_list.append({
                                "name": tool_name,
                                "description": tool.get("description", "")
                            })
                else:
                    # Single platform
                    for tool_name, tool in registry.tools.items():
                        if tool.get("platform") == platforms:
                            tool_list.append({
                                "name": tool_name,
                                "description": tool.get("description", "")
                            })
                matched_platform = alias
                break
    
    # 3. Fuzzy similarity match on aliases
    if not tool_list:
        best_match = None
        best_score = 0
        for alias in platform_aliases.keys():
            score = SequenceMatcher(None, platform_lower, alias.lower()).ratio()
            if score > best_score and score > 0.7:  # 70% similarity threshold
                best_score = score
                best_match = alias
        
        if best_match:
            platforms = platform_aliases[best_match]
            if isinstance(platforms, list):
                for tool_name, tool in registry.tools.items():
                    if tool.get("platform") in platforms:
                        tool_list.append({
                            "name": tool_name,
                            "description": tool.get("description", "")
                        })
            else:
                for tool_name, tool in registry.tools.items():
                    if tool.get("platform") == platforms:
                        tool_list.append({
                            "name": tool_name,
                            "description": tool.get("description", "")
                        })
            matched_platform = best_match
    
    if not tool_list:
        # Get list of available platforms for helpful error message
        available_platforms = set()
        for tool_name, tool in registry.tools.items():
            available_platforms.add(tool.get("platform", "unknown"))
        
        return {
            "success": False,
            "error": f"No tools found for platform: {platform}",
            "available_platforms": sorted(list(available_platforms)),
            "platform_aliases_available": sorted(list(platform_aliases.keys())),
            "suggestion": "Try using a platform alias like 'microsoft', 'google', 'outlook', 'gmail', etc. or call list_available_platforms() to see exact platform names"
        }
    
    # Build smart guidance for broad platform searches
    guidance = None
    subplatforms_info = None
    
    if matched_platform in ['microsoft', 'microsoft 365', 'm365', 'office', 'office 365']:
        subplatforms = ['excel', 'word', 'outlook', 'teams', 'onedrive', 'powerpoint', 'onenote', 'forms', 'sharepoint']
        guidance = "To narrow down further, use specific platform names:\n" + \
                   "  - search_tools('outlook') for email and calendar tools\n" + \
                   "  - search_tools('teams') for messaging and meeting tools\n" + \
                   "  - search_tools('excel_tools') for spreadsheet tools\n" + \
                   "  - search_tools('word_tools') for document tools\n" + \
                   "  - search_tools('onedrive') for file storage tools\n\n" + \
                   "Or use the naming pattern: microsoft_[PLATFORM] in tool names (e.g., microsoft_outlook_send_email)"
        subplatforms_info = {
            "available_subplatforms": subplatforms,
            "pattern": "microsoft_[subplatform]_[action]",
            "examples": ["microsoft_outlook_send_email", "microsoft_teams_send_message", "microsoft_excel_tools_create_workbook"]
        }
    elif matched_platform in ['google', 'google workspace']:
        subplatforms = ['gmail', 'sheets', 'docs', 'forms', 'calendar', 'drive', 'tasks']
        guidance = "To narrow down further, use specific platform names:\n" + \
                   "  - search_tools('gmail') for email tools\n" + \
                   "  - search_tools('sheets') for spreadsheet tools\n" + \
                   "  - search_tools('docs') for document tools\n" + \
                   "  - search_tools('forms') for form creation tools\n" + \
                   "  - search_tools('calendar') for scheduling tools\n" + \
                   "  - search_tools('drive') for file storage tools\n\n" + \
                   "Or use the naming pattern: google_[PLATFORM]_[ACTION] in tool names (e.g., google_sheets_create_spreadsheet)"
        subplatforms_info = {
            "available_subplatforms": subplatforms,
            "pattern": "google_[subplatform]_[action]",
            "examples": ["google_sheets_create_spreadsheet", "google_docs_create_document", "gmail_send_email"]
        }
    
    result = {
        "success": True,
        "platform": platform,
        "matched_as": matched_platform if matched_platform != platform_lower else None,
        "tool_count": len(tool_list),
        "tools": tool_list,
        "fuzzy_matching": matched_platform != platform_lower,
        "next_steps": "To use a tool: 1) Call get_tool_schema(tool_name) to see parameters, 2) Call execute_tool(tool_name, **params)"
    }
    
    # Add guidance and subplatform info if available
    if guidance:
        result["guidance"] = guidance
    if subplatforms_info:
        result["naming_pattern"] = subplatforms_info
    
    return result


def get_tool_schema(tool_name: str = None, **kwargs) -> Dict[str, Any]:
    """
    Get FULL parameter schema for ONE specific tool
    
    Use this AFTER list_platform_tools() to learn how to use a specific tool.
    Returns complete parameter information including types, requirements, examples.
    
    Args:
        tool_name: Name of the tool (e.g., 'gmail_send_email', 'google_docs_create_document')
    
    Returns:
        Dict with full tool schema including parameters
    """
    from tools.registry_v3 import get_registry
    
    # Handle case where tool_name is passed in kwargs instead of positional arg
    if tool_name is None and 'tool_name' in kwargs:
        tool_name = kwargs.pop('tool_name')
    
    if not tool_name:
        return {
            "success": False,
            "error": "tool_name parameter is required",
            "usage": "get_tool_schema('gmail_send_email')"
        }
    
    registry = get_registry()
    
    # Check if tool exists
    if tool_name not in registry.tools:
        return {
            "success": False,
            "error": f"Tool not found: {tool_name}",
            "suggestion": "Call list_available_platforms() then list_platform_tools(platform) to see available tools"
        }
    
    tool = registry.tools[tool_name]
    
    return {
        "success": True,
        "tool_name": tool_name,
        "description": tool.get("description", ""),
        "platform": tool.get("platform", "unknown"),
        "parameters": tool.get("parameters", {}),
        "returns": tool.get("returns", {}),
        "examples": tool.get("examples", []),
        "usage": f"Call execute_tool('{tool_name}', param1=value1, param2=value2, ...)"
    }


def search_tools(query: str, **kwargs) -> Dict[str, Any]:
    """
    Search for tools by keyword or task description with fuzzy matching
    
    Examples:
    - search_tools("send email") → finds gmail_send_email, outlook_send_email
    - search_tools("create spreadsheet") → finds google_sheets_create, excel_create_workbook
    - search_tools("gmail") → finds all Gmail tools
    - search_tools("microsoft") → finds microsoft_outlook, microsoft_calendar, etc.
    - search_tools("m365") → fuzzy matches to Microsoft 365 tools
    - search_tools("office") → fuzzy matches to Microsoft Office tools
    
    Args:
        query: Search query (e.g., 'email', 'gmail', 'microsoft', 'm365', 'office', 'outlook')
    
    Returns:
        Dict with matching tools (names and descriptions only)
    """
    from tools.registry_v3 import get_registry
    from difflib import SequenceMatcher
    
    registry = get_registry()
    query_lower = query.lower()
    
    # Define fuzzy matching aliases for common platform names
    fuzzy_aliases = {
        'microsoft': ['microsoft_', 'outlook_', 'teams_', 'onedrive_', 'word_', 'excel_', 'powerpoint_'],
        'microsoft 365': ['microsoft_', 'outlook_', 'teams_', 'onedrive_', 'word_', 'excel_', 'powerpoint_'],
        'm365': ['microsoft_', 'outlook_', 'teams_', 'onedrive_', 'word_', 'excel_', 'powerpoint_'],
        'office': ['outlook_', 'word_', 'excel_', 'powerpoint_', 'microsoft_'],
        'office 365': ['outlook_', 'word_', 'excel_', 'powerpoint_', 'microsoft_'],
        'google': ['google_', 'gmail_', 'gsheets_'],
        'google workspace': ['google_', 'gmail_', 'gsheets_', 'google_docs', 'google_calendar', 'google_drive'],
        'email': ['gmail_', 'outlook_', 'email', 'send'],
        'spreadsheet': ['sheets', 'excel', 'spreadsheet'],
        'document': ['docs', 'word', 'document'],
        'calendar': ['calendar', 'scheduling'],
        'chat': ['teams', 'slack', 'message'],
        'storage': ['drive', 'onedrive', 'dropbox'],
    }
    
    # Platform subcomponents for guidance
    platform_components = {
        'microsoft': {
            'platforms': ['excel', 'word', 'outlook', 'teams', 'onedrive', 'powerpoint', 'onenote', 'forms', 'sharepoint'],
            'guidance': "Use microsoft_[PLATFORM] format to narrow down:\n- microsoft_outlook (email, calendar, contacts)\n- microsoft_teams (messaging, meetings)\n- microsoft_excel_tools (spreadsheet operations)\n- microsoft_word_tools (document editing)\n- microsoft_onedrive (file storage)\n- microsoft_calendar (scheduling)\nOr use list_platform_tools('PLATFORM_NAME') for specific tool lists."
        },
        'google': {
            'platforms': ['gmail', 'sheets', 'docs', 'forms', 'calendar', 'drive', 'tasks'],
            'guidance': "Use google_[PLATFORM] format to narrow down:\n- gmail (email operations)\n- google_sheets (spreadsheet operations)\n- google_docs (document editing)\n- google_forms (form creation and responses)\n- google_calendar (scheduling)\n- google_drive (file storage)\n- google_tasks (task management)\nOr use list_platform_tools('PLATFORM_NAME') for specific tool lists."
        }
    }
    
    # Search tool names and descriptions
    matching_tools = []
    matched_tool_names = set()  # Track to avoid duplicates
    
    for tool_name, tool in registry.tools.items():
        # Skip meta-tools in search results
        if tool_name.startswith(('list_', 'get_platform', 'recommend_', 'execute_', 'search_')):
            continue
        
        if tool_name in matched_tool_names:
            continue
        
        description = tool.get("description", "").lower()
        
        # 1. Exact substring match (highest priority)
        if query_lower in tool_name.lower() or query_lower in description:
            matching_tools.append({
                "name": tool_name,
                "description": tool.get("description", ""),
                "platform": tool.get("platform", "unknown"),
                "match_type": "exact"
            })
            matched_tool_names.add(tool_name)
            continue
        
        # 2. Check fuzzy aliases (medium priority)
        for alias, prefixes in fuzzy_aliases.items():
            if query_lower.startswith(alias) or alias.startswith(query_lower) or SequenceMatcher(None, query_lower, alias).ratio() > 0.8:
                # Check if tool name starts with any of the prefixes for this alias
                if any(tool_name.startswith(prefix) for prefix in prefixes):
                    matching_tools.append({
                        "name": tool_name,
                        "description": tool.get("description", ""),
                        "platform": tool.get("platform", "unknown"),
                        "match_type": "fuzzy_alias"
                    })
                    matched_tool_names.add(tool_name)
                    break
        
        if tool_name in matched_tool_names:
            continue
        
        # 3. Fuzzy match on tool name and description (lowest priority)
        name_similarity = SequenceMatcher(None, query_lower, tool_name.lower()).ratio()
        desc_similarity = SequenceMatcher(None, query_lower, description).ratio()
        max_similarity = max(name_similarity, desc_similarity)
        
        if max_similarity > 0.7:  # 70% match threshold for fuzzy matching
            matching_tools.append({
                "name": tool_name,
                "description": tool.get("description", ""),
                "platform": tool.get("platform", "unknown"),
                "match_type": "fuzzy",
                "similarity": round(max_similarity * 100)
            })
            matched_tool_names.add(tool_name)
    
    # Sort results: exact > fuzzy_alias > fuzzy
    match_type_order = {"exact": 0, "fuzzy_alias": 1, "fuzzy": 2}
    matching_tools.sort(key=lambda x: (match_type_order.get(x.get("match_type", "fuzzy"), 3), -x.get("similarity", 70)))
    
    # Build response with smart guidance for broad searches
    result = {
        "success": True,
        "query": query,
        "match_count": len(matching_tools),
        "tools": matching_tools[:50],  # Limit to 50 results
        "fuzzy_matching_enabled": True,
        "aliases_checked": list(fuzzy_aliases.keys()),
        "next_steps": "To use a tool: 1) Call get_tool_schema(tool_name) to see parameters, 2) Call execute_tool(tool_name, **params)"
    }
    
    # Add smart guidance for broad platform searches
    for broad_query, components in platform_components.items():
        if query_lower in broad_query or broad_query in query_lower or SequenceMatcher(None, query_lower, broad_query).ratio() > 0.8:
            result["guidance"] = f"\n{components['guidance']}"
            result["available_subplatforms"] = components['platforms']
            result["info"] = f"Found {len(matching_tools)} {broad_query.capitalize()} tools. To narrow down the results, try searching for specific subplatforms: {', '.join(components['platforms'])}"
            break
    
    return result


def get_platform_guide(platform: str, **kwargs) -> Dict[str, Any]:
    """
    Get detailed usage guide for a platform's tools
    
    Args:
        platform: Platform name (e.g., 'google_workspace', 'microsoft_365', 'calculator')
    
    Returns:
        Dict with detailed guide text
    """
    # Simple implementation - just return basic info about the platform
    from tools.registry_v3 import get_registry
    
    registry = get_registry()
    
    # Count tools for this platform
    tool_names = [name for name, tool in registry.tools.items() if tool.get("platform") == platform]
    
    if not tool_names:
        return {
            "success": False,
            "error": f"Platform not found: {platform}",
            "suggestion": "Call list_available_platforms() to see available platforms"
        }
    
    guide = f"Platform: {platform}\n"
    guide += f"Tools available: {len(tool_names)}\n\n"
    guide += "To use this platform:\n"
    guide += f"1. Call list_platform_tools('{platform}') to see all tools\n"
    guide += "2. Call get_tool_schema(tool_name) to learn about a specific tool\n"
    guide += "3. Call execute_tool(tool_name, **params) to use the tool\n"
    
    return {
        "success": True,
        "platform": platform,
        "tool_count": len(tool_names),
        "guide": guide
    }


def recommend_tools_for_task(task_description: str, 
                             user_platforms: Optional[List[str]] = None,
                             **kwargs) -> Dict[str, Any]:
    """
    Get smart recommendations for which tools to use for a task
    
    Args:
        task_description: What you want to do
        user_platforms: List of platforms user has connected (optional)
    
    Returns:
        Dict with recommendations
    """
    # Simple recommendation: use search_tools instead
    return {
        "success": True,
        "task": task_description,
        "recommendation": f"Use search_tools('{task_description}') to find relevant tools",
        "example": f"search_tools('{task_description.split()[0]}') will find matching tools"
    }


def execute_tool(tool_name: str = None, **tool_params) -> Dict[str, Any]:
    """
    Execute ANY tool by name (proxy function for dynamic tool execution)
    
    This allows Claude to call tools after discovering them via list_platform_tools(),
    without needing all 603 tool schemas sent upfront.
    
    Args:
        tool_name: Name of tool to execute (e.g., 'gmail_send_email', 'google_docs_create')
        **tool_params: All parameters required by the tool
    
    Returns:
        Result from the executed tool
    """
    from tools.registry_v3 import get_registry
    
    # Handle case where tool_name is passed in kwargs instead of positional arg
    # (can happen with Anthropic's additionalProperties handling)
    if tool_name is None and 'tool_name' in tool_params:
        tool_name = tool_params.pop('tool_name')
    
    if not tool_name:
        return {
            "success": False,
            "error": "tool_name parameter is required",
            "usage": "execute_tool(tool_name='gmail_send_email', to='...', subject='...', body='...')"
        }
    
    registry = get_registry()
    
    # Check if tool exists
    if tool_name not in registry.tools:
        return {
            "success": False,
            "error": f"Tool not found: {tool_name}",
            "available_platforms": list(set([t.split('_')[0] for t in registry.tools.keys()])),
            "suggestion": f"Call list_available_platforms() to see platforms, then list_platform_tools(platform) to see tools"
        }
    
    try:
        # Remove tool_name from params if it was passed as a kwarg (to avoid duplicate argument)
        if 'tool_name' in tool_params:
            del tool_params['tool_name']
        
        # Execute the tool via registry (pass tool_name as keyword argument to avoid conflicts)
        result = registry.execute_tool(tool_name=tool_name, **tool_params)
        
        return {
            "success": True,
            "tool_executed": tool_name,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Tool execution failed: {str(e)}",
            "tool_name": tool_name,
            "parameters_provided": list(tool_params.keys())
        }


def get_workflow_steps(workflow_name: str, **kwargs) -> Dict[str, Any]:
    """
    Get step-by-step workflow for common tasks
    
    Args:
        workflow_name: Name of workflow (e.g., 'send_email', 'create_document', 'generate_quote')
    
    Returns:
        Dict with step-by-step instructions
    """
    # Generic workflow guidance
    workflows = {
        "send_email": [
            "1. Call search_tools('email') or list_platform_tools('google_workspace')",
            "2. Find gmail_send_email or outlook_send_email",
            "3. Call get_tool_schema('gmail_send_email')",
            "4. Call execute_tool('gmail_send_email', to='...', subject='...', body='...')"
        ],
        "create_document": [
            "1. Call search_tools('document') or list_platform_tools('google_workspace')",
            "2. Find google_docs_create_document",
            "3. Call get_tool_schema('google_docs_create_document')",
            "4. Call execute_tool('google_docs_create_document', title='...')"
        ],
        "generate_quote": [
            "1. Call list_platform_tools('calculator')",
            "2. Find appropriate calculator tool (e.g., calculate_business_cards)",
            "3. Call get_tool_schema('calculate_business_cards')",
            "4. Call execute_tool('calculate_business_cards', quantity=..., stock_type='...')"
        ]
    }
    
    steps = workflows.get(workflow_name)
    
    if not steps:
        return {
            "success": False,
            "error": f"Workflow not found: {workflow_name}",
            "available_workflows": list(workflows.keys()),
            "suggestion": "Use search_tools() to find relevant tools for your task"
        }
    
    return {
        "success": True,
        "workflow_name": workflow_name,
        "steps": "\n".join(steps)
    }


# Module info for registry
__all__ = [
    "list_available_platforms",
    "list_platform_tools",
    "get_tool_schema",
    "search_tools",
    "get_platform_guide",
    "recommend_tools_for_task",
    "get_workflow_steps",
    "execute_tool"
]
