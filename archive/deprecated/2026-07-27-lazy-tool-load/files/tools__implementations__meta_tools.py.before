"""
Meta-Tools Implementation - Tool discovery and guidance
These meta-tools help Claude discover and use the 604+ available tools
Uses registry directly (no external dependencies)

FIXED: All calls to registry.execute_tool() now use keyword-only arguments
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
    
    result = {
        "success": True,
        "platforms": platforms,
        "platform_count": len(platforms),
        "tool_counts": {p: platform_counts[p] for p in platforms},
        "total_tools": sum(platform_counts[p] for p in platforms)
    }
    
    # Inject session status (if available in kwargs)
    if '_session_status' in kwargs:
        result['_session_status'] = kwargs['_session_status']
    
    return result


def list_platform_tools(platform: str, **kwargs) -> Dict[str, Any]:
    """
    List all tools for a platform - NAMES AND DESCRIPTIONS ONLY (no parameter schemas)
    
    Returns a simple list of tool names and what they do.
    If you need to know how to use a tool, call get_tool_schema(tool_name).
    
    Supports platform name matching:
    - "microsoft" matches all microsoft_* tools
    - "microsoft_word" matches microsoft_word_* tools
    - "outlook" expands to microsoft_outlook
    - "google" matches all google_* tools
    - "gmail" matches gmail_* tools
    
    Args:
        platform: Platform name (e.g., 'google_forms', 'microsoft_outlook', 'gmail')
                 or platform alias ('microsoft', 'google', 'm365', 'office')
    
    Returns:
        Dict with list of tool names and short descriptions
    """
    from tools.registry_v3 import get_registry
    
    registry = get_registry()
    platform_lower = platform.lower()
    
    # Define platform aliases for exact expansion
    platform_aliases = {
        'microsoft': ['microsoft_'],  # Match all microsoft_ tools
        'microsoft 365': ['microsoft_'],
        'm365': ['microsoft_'],
        'office': ['microsoft_outlook', 'microsoft_word', 'microsoft_excel', 'microsoft_teams'],
        'office 365': ['microsoft_'],
        'outlook': ['microsoft_outlook_'],
        'teams': ['microsoft_teams_'],
        'onedrive': ['microsoft_onedrive_'],
        'todo': ['microsoft_todo_'],
        'word': ['microsoft_word_'],
        'excel': ['microsoft_excel_'],
        'onenote': ['microsoft_onenote_'],
        'forms': ['microsoft_forms_'],
        'sharepoint': ['microsoft_sharepoint_'],
        'calendar': ['microsoft_calendar_', 'google_calendar_'],
        'google': ['google_', 'gmail_'],  # All Google tools
        'google workspace': ['google_', 'gmail_'],
        'gsuite': ['google_', 'gmail_'],
        'gmail': ['gmail_'],
        'sheets': ['google_sheets_'],
        'docs': ['google_docs_'],
        'drive': ['google_drive_'],
        'forms': ['google_forms_'],
        'synergy': ['synergy_'],  # Synergy Dashboard tools
        'dashboard': ['synergy_'],  # Alias for synergy
        'kanban': ['synergy_'],  # Alias for synergy
        'agent': ['assign_and_activate', 'request_update', 'respond_to'],  # Agent coordination
        'agents': ['assign_and_activate', 'request_update', 'respond_to'],  # Agent coordination
        'multi-agent': ['assign_and_activate', 'request_update', 'respond_to'],  # Agent coordination
        'multi_agent': ['assign_and_activate', 'request_update', 'respond_to'],  # Agent coordination
        'agent_coordination': ['assign_and_activate', 'request_update', 'respond_to'],  # Agent coordination
        'coordination': ['assign_and_activate', 'request_update', 'respond_to'],  # Agent coordination
        'cross-thread': ['request_update', 'respond_to'],  # Cross-thread communication
        'cross_thread': ['request_update', 'respond_to'],  # Cross-thread communication
    }
    
    tool_list = []
    matched_platform = None
    
    # FIRST: Try matching by platform field in tool schema
    # This handles platforms like "advanced_agent_coordination" where tools don't share a common prefix
    for tool_name, tool in registry.tools.items():
        tool_platform = tool.get("platform", "").lower()
        if tool_platform == platform_lower:
            tool_list.append({
                "name": tool_name,
                "short_description": tool.get("short_description", tool.get("description", ""))
            })
    if tool_list:
        matched_platform = platform_lower
    
    # SECOND: Check if input is a direct prefix (like "microsoft_word")
    # Try direct prefix matching for compound names
    if not tool_list and '_' in platform_lower:
        # e.g., "microsoft_word" or "google_sheets"
        prefix = platform_lower + '_' if not platform_lower.endswith('_') else platform_lower
        for tool_name, tool in registry.tools.items():
            if tool_name.lower().startswith(prefix):
                tool_list.append({
                    "name": tool_name,
                    "short_description": tool.get("short_description", tool.get("description", ""))
                })
        if tool_list:
            matched_platform = platform_lower
    
    # If not found, try exact alias expansion
    if not tool_list:
        if platform_lower in platform_aliases:
            search_prefixes = platform_aliases[platform_lower]
            matched_platform = platform_lower
            
            for tool_name, tool in registry.tools.items():
                # Check if tool name starts with any of the search prefixes
                for prefix in search_prefixes:
                    if tool_name.lower().startswith(prefix):
                        tool_list.append({
                            "name": tool_name,
                            "short_description": tool.get("short_description", tool.get("description", ""))
                        })
                        break  # Don't add tool twice
    
    if not tool_list:
        # Get list of available platforms/prefixes for helpful error message
        available_prefixes = set()
        for tool_name in registry.tools.keys():
            # Extract first part of tool name
            parts = tool_name.lower().split('_')
            if len(parts) >= 2:
                available_prefixes.add('_'.join(parts[:2]))  # e.g., "microsoft_word", "google_sheets"
        
        result = {
            "success": False,
            "error": f"No tools found for platform: {platform}",
            "available_platforms": sorted(list(available_prefixes)),
            "platform_aliases_available": sorted(list(platform_aliases.keys())),
            "suggestion": "Try using a platform alias like 'microsoft', 'google', 'outlook', 'gmail', etc. or use exact prefix like 'microsoft_word', 'google_sheets'"
        }
        
        # Inject session status (if available in kwargs)
        if '_session_status' in kwargs:
            result['_session_status'] = kwargs['_session_status']
        
        return result
    
    # Build result with session status injection
    result = {
        "success": True,
        "platform": platform,
        "matched_platform": matched_platform,
        "tool_count": len(tool_list),
        "tools": tool_list
    }
    
    # Inject session status (if available in kwargs from combined_agent_worker)
    if '_session_status' in kwargs:
        result['_session_status'] = kwargs['_session_status']
    
    # Build smart guidance for broad platform searches
    guidance = None
    subplatforms_info = None
    
    if matched_platform in ['microsoft', 'microsoft 365', 'm365']:
        subplatforms = ['outlook', 'teams', 'excel', 'word', 'onedrive', 'calendar', 'todo', 'forms', 'sharepoint', 'onenote']
        guidance = "To narrow down further, try:\n" + \
                   "  - list_platform_tools('microsoft_outlook') for email/calendar\n" + \
                   "  - list_platform_tools('microsoft_teams') for messaging\n" + \
                   "  - list_platform_tools('microsoft_excel') for spreadsheets\n" + \
                   "  - list_platform_tools('microsoft_word') for documents\n" + \
                   "  - list_platform_tools('microsoft_onedrive') for files"
        subplatforms_info = {
            "available_subplatforms": subplatforms,
            "pattern": "microsoft_[subplatform]_[action]",
            "examples": ["microsoft_outlook_send_email", "microsoft_teams_send_message", "microsoft_excel_create_workbook"]
        }
    elif matched_platform in ['google', 'google workspace', 'gsuite']:
        subplatforms = ['gmail', 'sheets', 'docs', 'forms', 'calendar', 'drive', 'tasks']
        guidance = "To narrow down further, try:\n" + \
                   "  - list_platform_tools('gmail') for email\n" + \
                   "  - list_platform_tools('google_sheets') for spreadsheets\n" + \
                   "  - list_platform_tools('google_docs') for documents\n" + \
                   "  - list_platform_tools('google_forms') for forms\n" + \
                   "  - list_platform_tools('google_calendar') for scheduling"
        subplatforms_info = {
            "available_subplatforms": subplatforms,
            "pattern": "google_[subplatform]_[action]",
            "examples": ["gmail_send_email", "google_sheets_create_spreadsheet", "google_docs_create_document"]
        }
    elif matched_platform in ['synergy', 'dashboard', 'kanban']:
        guidance = "Synergy Dashboard - Visual Kanban board for multi-platform project tracking:\n\n" + \
                   "CORE TOOLS:\n" + \
                   "  - synergy_smart_project_tracker - ONE-CALL project setup with full tracking\n" + \
                   "  - synergy_create_session - Create new project card\n" + \
                   "  - synergy_get_session - Fetch current project state\n" + \
                   "  - synergy_list_sessions - View all projects on dashboard\n" + \
                   "  - synergy_move_session - Change project status/column\n\n" + \
                   "APPEND TOOLS (Efficient single-item additions - RECOMMENDED!):\n" + \
                   "  - synergy_add_document - Add ONE document (no fetch needed)\n" + \
                   "  - synergy_add_link - Add ONE external link (no fetch needed)\n" + \
                   "  - synergy_add_next_step - Add ONE action item (no fetch needed)\n" + \
                   "  - synergy_add_tag - Add ONE tag (no fetch needed)\n" + \
                   "  - synergy_link_thread - Link ONE conversation thread (no fetch needed)\n" + \
                   "  - synergy_assign_agent - Assign ONE AI agent (no fetch needed)\n\n" + \
                   "EDIT TOOLS (Description, Notes, and Checklist Management):\n" + \
                   "  - synergy_edit_description - Replace description text\n" + \
                   "  - synergy_edit_notes - Replace notes text\n" + \
                   "  - synergy_checklist_add_item - Add checklist item\n" + \
                   "  - synergy_checklist_edit_item - Edit checklist item text\n" + \
                   "  - synergy_checklist_toggle_item - Check/uncheck item (mark done/undone)\n" + \
                   "  - synergy_checklist_delete_item - Delete checklist item\n" + \
                   "  - synergy_checklist_add_sub_item - Add nested sub-item to checklist\n\n" + \
                   "BULK UPDATE (Only when replacing entire arrays):\n" + \
                   "  - synergy_update_session - REPLACES entire arrays (requires fetch first)\n\n" + \
                   "WORKFLOW: Use append/edit tools for incremental updates. They're efficient and preserve existing data."
        subplatforms_info = {
            "key_tools": ["synergy_smart_project_tracker", "synergy_add_document", "synergy_checklist_add_item"],
            "append_tools": ["synergy_add_document", "synergy_add_link", "synergy_add_next_step", "synergy_add_tag", "synergy_link_thread", "synergy_assign_agent"],
            "edit_tools": ["synergy_edit_description", "synergy_edit_notes", "synergy_checklist_add_item", "synergy_checklist_edit_item", "synergy_checklist_toggle_item", "synergy_checklist_delete_item", "synergy_checklist_add_sub_item"],
            "pattern": "synergy_[action]_[object]",
            "examples": ["synergy_create_session", "synergy_add_document", "synergy_checklist_toggle_item"]
        }
    elif matched_platform in ['advanced_agent_coordination', 'agent_coordination', 'multi_agent', 'agent', 'agents']:
        guidance = "Multi-Agent Coordination - Distribute work across 26 AI agents with cross-thread communication:\n\n" + \
                   "CORE TOOLS (3 total):\n\n" + \
                   "1. assign_and_activate_agent_with_slugs - ALL-IN-ONE COMBO TOOL\n" + \
                   "   The primary tool for distributing work to agents.\n" + \
                   "   - Accepts NATO names ('Alpha', 'Bravo', 'Charlie'...'Zulu') or numbers (1-26)\n" + \
                   "   - Creates or updates thread in agent column\n" + \
                   "   - Assigns multiple resource slugs (workflow, internal_doc, synergy_session)\n" + \
                   "   - Sends instruction message to agent\n" + \
                   "   - Returns UI commands for automatic tab/column opening\n" + \
                   "   - Optional auto_trigger to immediately start agent processing\n\n" + \
                   "   Example: Distribute e-commerce project across 3 agents:\n" + \
                   "     assign_and_activate_agent_with_slugs(\n" + \
                   "       target_agent='Alpha',\n" + \
                   "       thread_title='E-Commerce Frontend',\n" + \
                   "       instructions='Build React frontend...',\n" + \
                   "       slugs={'workflow_slug': 'react-workflow'},\n" + \
                   "       auto_trigger=True, open_ui=True\n" + \
                   "     )\n\n" + \
                   "2. request_update_from_thread - Cross-thread communication initiator\n" + \
                   "   Request information/status from another agent's thread.\n" + \
                   "   - Creates cross_thread_requests database record\n" + \
                   "   - Inserts formatted request into target thread with priority icon\n" + \
                   "   - Priority levels: low (🔵), medium (🟡), high (🟠), urgent (🔴)\n" + \
                   "   - Request types: status_update, deliverable, question, coordination, resource_request\n" + \
                   "   - Optional wait_for_response with timeout polling\n\n" + \
                   "   Example: Request status from Agent Bravo:\n" + \
                   "     request_update_from_thread(\n" + \
                   "       target_thread_id='Bravo',\n" + \
                   "       request_message='Status of API endpoints?',\n" + \
                   "       request_type='status_update',\n" + \
                   "       priority='high'\n" + \
                   "     )\n\n" + \
                   "3. respond_to_cross_thread_request - Cross-thread response handler\n" + \
                   "   Respond to incoming requests from other agents.\n" + \
                   "   - Updates request status to 'completed'\n" + \
                   "   - Sends response back to source thread\n" + \
                   "   - Notifies source thread of response arrival\n\n" + \
                   "   Example: Respond to request:\n" + \
                   "     respond_to_cross_thread_request(\n" + \
                   "       request_id='req_abc123',\n" + \
                   "       response_message='API 90% complete, ready by EOD'\n" + \
                   "     )\n\n" + \
                   "KEY FEATURES:\n" + \
                   "  - 26 NATO agents: Alpha, Bravo, Charlie, Delta, Echo, Foxtrot, Golf, Hotel, India, Juliet,\n" + \
                   "    Kilo, Lima, Mike, November, Oscar, Papa, Quebec, Romeo, Sierra, Tango, Uniform,\n" + \
                   "    Victor, Whiskey, X-ray, Yankee, Zulu\n" + \
                   "  - Flexible identifiers: 'Alpha' or 'agent-1' or '1' (all work the same)\n" + \
                   "  - UI automation: Automatic tab switching, column opening, thread info display\n" + \
                   "  - Resource linking: Attach workflows, internal docs, synergy sessions to agent threads\n" + \
                   "  - Cross-thread messaging: Agents can request updates and receive responses\n" + \
                   "  - Database tracking: All requests/responses tracked in cross_thread_requests table\n\n" + \
                   "TYPICAL WORKFLOWS:\n\n" + \
                   "A) Distribute Multi-Agent Project:\n" + \
                   "   1. Call assign_and_activate_agent_with_slugs for each agent (Alpha, Bravo, Charlie)\n" + \
                   "   2. Each call assigns work, attaches resources, and opens UI\n" + \
                   "   3. Set auto_trigger=True to immediately start agents\n" + \
                   "   4. Result: 3 agents working in parallel with full coordination\n\n" + \
                   "B) Request Status Update:\n" + \
                   "   1. Prime AI calls request_update_from_thread(target='Bravo')\n" + \
                   "   2. Request appears in Agent Bravo's thread with priority icon\n" + \
                   "   3. Agent Bravo's AI calls respond_to_cross_thread_request()\n" + \
                   "   4. Response appears in Prime AI's thread\n\n" + \
                   "C) Synergy Session Coordination:\n" + \
                   "   1. Assign same synergy_session_id to multiple agents\n" + \
                   "   2. All agents' threads link to synergy card automatically\n" + \
                   "   3. Synergy card shows all linked threads with info badges\n\n" + \
                   "BEST PRACTICES:\n" + \
                   "  - Use NATO names for clarity ('Alpha' is clearer than '1')\n" + \
                   "  - Set auto_trigger=True when ready for agent to start immediately\n" + \
                   "  - Use high priority for time-sensitive cross-thread requests\n" + \
                   "  - Link synergy sessions when agents collaborate on same project\n" + \
                   "  - Include clear, detailed instructions in thread messages"
        subplatforms_info = {
            "agent_count": 26,
            "nato_names": ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "India", "Juliet", "Kilo", "Lima", "Mike", "November", "Oscar", "Papa", "Quebec", "Romeo", "Sierra", "Tango", "Uniform", "Victor", "Whiskey", "X-ray", "Yankee", "Zulu"],
            "key_tool": "assign_and_activate_agent_with_slugs",
            "communication_tools": ["request_update_from_thread", "respond_to_cross_thread_request"],
            "pattern": "[agent_action]_[object]",
            "examples": ["assign_and_activate_agent_with_slugs", "request_update_from_thread", "respond_to_cross_thread_request"]
        }
    
    # Sort alphabetically
    tool_list.sort(key=lambda x: x["name"])
    
    # Update result with additional fields
    result["matched_as"] = matched_platform
    result["next_steps"] = (
        "To use a tool: 1) Call get_tool_schema(tool_name) to see parameters, "
        "2) Call execute_tool(tool_name, parameters={...}) — pass tool "
        "arguments under the `parameters` dict, not as top-level kwargs."
    )
    
    if guidance:
        result["guidance"] = guidance
    
    if subplatforms_info:
        result["naming_pattern"] = subplatforms_info
    
    return result


def get_tool_schema(tool_name: str = None, **kwargs) -> Dict[str, Any]:
    """
    Get FULL Anthropic-formatted parameter schema for ONE specific tool
    
    Use this AFTER list_platform_tools() to learn how to use a specific tool.
    Returns complete parameter information formatted for Anthropic API with input_schema.
    
    MULTI-PROVIDER COMPATIBLE: Handles both Anthropic (Claude) and OpenAI (GPT) formats.
    
    Args:
        tool_name: Name of the tool (e.g., 'gmail_send_email', 'google_docs_create_document')
    
    Returns:
        Dict with full Anthropic-formatted tool schema including input_schema
    """
    import json
    from tools.registry_v3 import get_registry
    
    # MULTI-PROVIDER PARAMETER EXTRACTION (same as execute_tool)
    extracted_tool_name = tool_name
    
    # Extract from kwargs (Anthropic format)
    if not extracted_tool_name and 'tool_name' in kwargs:
        extracted_tool_name = kwargs.get('tool_name')
    
    # Extract from JSON arguments (OpenAI format)
    if not extracted_tool_name and 'arguments' in kwargs:
        arguments = kwargs.get('arguments')
        if isinstance(arguments, str):
            try:
                args_dict = json.loads(arguments)
                extracted_tool_name = args_dict.get('tool_name')
            except json.JSONDecodeError:
                pass
    
    # Extract from nested input (API wrapper format)
    if not extracted_tool_name and 'input' in kwargs:
        input_obj = kwargs.get('input')
        if isinstance(input_obj, dict):
            extracted_tool_name = input_obj.get('tool_name')
    
    # Validate tool_name extracted
    if not extracted_tool_name:
        error_result = {
            "success": False,
            "error": "❌ MISSING PARAMETER: tool_name is required",
            "correct_usage": "get_tool_schema(tool_name='exact_tool_name')",
            "example": "get_tool_schema(tool_name='microsoft_excel_create_workbook')",
            "workflow": {
                "step_1": "Call list_available_platforms() to see all platform names",
                "step_2": "Call list_platform_tools(platform='platform_name') to see available tools",
                "step_3": "Call get_tool_schema(tool_name='exact_tool_name') to see parameters",
                "step_4": (
                    "Call execute_tool(tool_name='exact_tool_name', "
                    "parameters={...}) — pass tool arguments under the "
                    "`parameters` dict, not as top-level kwargs."
                ),
            },
            "note": "You MUST pass tool_name parameter. Do NOT call get_tool_schema() without parameters.",
            "received_params": list(kwargs.keys())
        }
        # Inject session status even in errors
        if '_session_status' in kwargs:
            error_result['_session_status'] = kwargs['_session_status']
        print(f"\n[META-TOOL ERROR] get_tool_schema() - Missing tool_name:")
        print(f"  - Received params: {list(kwargs.keys())}")
        print(f"  ⚠️ MUST use: get_tool_schema(tool_name='exact_tool_name')")
        return error_result
    
    print(f"\n[META-TOOL] get_tool_schema() called:")
    print(f"  - Tool name: {extracted_tool_name}")
    
    registry = get_registry()
    
    # Check if tool exists
    if extracted_tool_name not in registry.tools:
        # Find similar tools to suggest
        all_tool_names = list(registry.tools.keys())
        similar_tools = []
        search_term = extracted_tool_name.lower()
        
        # Find tools with similar names (substring matching)
        for tool in all_tool_names:
            if search_term in tool.lower() or tool.lower() in search_term:
                similar_tools.append(tool)
        
        # Limit to top 5 suggestions
        similar_tools = similar_tools[:5]
        
        error_result = {
            "success": False,
            "error": f"❌ TOOL NOT FOUND: '{extracted_tool_name}' does not exist in registry",
            "similar_tools": similar_tools if similar_tools else None,
            "hint": "You may have guessed the wrong tool name. Use discovery tools instead of guessing.",
            "correct_workflow": {
                "step_1": "Call search_tools(query='excel') to find Excel-related tools",
                "step_2": "Or call list_platform_tools(platform='microsoft_excel') to list all Excel tools",
                "step_3": "Use the EXACT tool name from the results",
                "step_4": "Call get_tool_schema(tool_name='exact_name_from_results')"
            },
            "available_discovery_tools": [
                "search_tools(query='keyword') - Search by keyword across all tools",
                "list_available_platforms() - See all platform names",
                "list_platform_tools(platform='name') - List tools for specific platform"
            ],
            "common_mistakes": {
                "wrong": "google_sheets_create_spreadsheet (does not exist)",
                "correct": "Use search_tools(query='sheets create') to find actual tool name"
            }
        }
        # Inject session status even in errors
        if '_session_status' in kwargs:
            error_result['_session_status'] = kwargs['_session_status']
        print(f"[META-TOOL ERROR] get_tool_schema() - Tool not found: {extracted_tool_name}")
        if similar_tools:
            print(f"  💡 Similar tools found: {', '.join(similar_tools[:3])}")
        return error_result
    
    tool = registry.tools[extracted_tool_name]
    
    # Get the Anthropic-formatted version which includes input_schema
    anthropic_tools = registry.get_anthropic_tools()
    anthropic_tool = None
    for at in anthropic_tools:
        if at.get('name') == tool_name:
            anthropic_tool = at
            break
    
    if not anthropic_tool:
        # Fallback to manual schema if not in Anthropic format
        return {
            "success": True,
            "tool_name": tool_name,
            "description": tool.get("description", ""),
            "platform": tool.get("platform", "unknown"),
            "input_schema": {
                "type": "object",
                "properties": tool.get("parameters", {}).get("properties", tool.get("parameters", {})),
                "required": tool.get("parameters", {}).get("required", [])
            },
            "examples": tool.get("examples", []),
            "note": "Add this tool to your tools list to use it"
        }
    
    print(f"[META-TOOL] get_tool_schema() returning schema for: {extracted_tool_name}")
    
    result = {
        "success": True,
        "tool_name": tool_name,
        "description": anthropic_tool.get("description", ""),
        "platform": tool.get("platform", "unknown"),
        "input_schema": anthropic_tool.get("input_schema", {}),
        "examples": tool.get("examples", []),
        "note": "Add this tool to your tools list to use it. The input_schema shows all required and optional parameters."
    }
    
    # Inject session status (if available in kwargs)
    if '_session_status' in kwargs:
        result['_session_status'] = kwargs['_session_status']
    
    return result


def search_tools(query: str, **kwargs) -> Dict[str, Any]:
    """
    Search for tools by keyword with strategic alias expansion (NO fuzzy matching)
    
    Examples:
    - search_tools("send email") → finds gmail_send_email, outlook_send_email
    - search_tools("gmail") → finds all Gmail tools
    - search_tools("microsoft") → finds microsoft_outlook, microsoft_calendar, etc.
    - search_tools("m365") → expands to Microsoft 365 tools
    - search_tools("office") → expands to Microsoft Office tools
    
    Args:
        query: Search query (e.g., 'email', 'gmail', 'microsoft', 'm365', 'office', 'outlook')
    
    Returns:
        Dict with matching tools (names and descriptions only)
    """
    from tools.registry_v3 import get_registry
    
    registry = get_registry()
    query_lower = query.lower().strip()
    
    # CRITICAL: Detect searches for web search/fetch tools
    # Claude has these as SERVER TOOLS (no client-side execution needed)
    web_search_queries = ['websearch', 'web_search', 'web search', 'search web', 'search internet', 
                          'internet search', 'tavily', 'brave', 'brave search', 'search engine',
                          'online search', 'web query']
    web_fetch_queries = ['webfetch', 'web_fetch', 'web fetch', 'fetch url', 'fetch web', 
                        'read url', 'get url', 'scrape', 'scrape web', 'download url',
                        'read webpage', 'fetch page', 'get webpage']
    
    # Check if searching for web search tools
    if any(q in query_lower for q in web_search_queries):
        return {
            "success": True,
            "match_count": 1,
            "query": query,
            "guidance": """SERVER TOOL AVAILABLE: web_search

You have a web_search SERVER TOOL that's ALWAYS available.
This tool runs on Anthropic's servers and provides real-time internet access.

HOW TO USE (NO execute_tool NEEDED):
You don't call search_tools() or execute_tool() for this. Just USE IT DIRECTLY in your content blocks.

EXAMPLE:
User: "What's the latest AI news?"

Your response should include:
{
  "type": "tool_use",
  "name": "web_search",
  "input": {
    "query": "latest AI news November 2025"
  }
}

Claude API executes search automatically on server
You receive results with URLs, titles, content, page age
You analyze and respond to user

KEY POINTS:
- Server tool (no client execution)
- Max 5 searches per conversation
- Returns URLs, titles, snippets, page age
- Localized to Brisbane, Queensland, Australia
- Use for: current events, news, trends, recent data, anything after your knowledge cutoff

WHEN TO USE:
- Current events, news, trends
- Latest pricing or market data
- Recent technical standards
- Real-time information
- Any info beyond your knowledge cutoff (April 2024)

NEVER say "I need to find a web search tool" - YOU ALREADY HAVE IT!
Just use it directly.""",
            "available_platforms": ["anthropic_server_tools"],
            "tools": [{
                "name": "web_search",
                "description": "Server-side real-time web search (always available)",
                "platform": "anthropic_server_tools",
                "type": "server_tool",
                "usage": "Use directly in content blocks with tool_use type, no execute_tool() needed"
            }],
            "critical_note": "This is a SERVER TOOL - it's not in your tools list but you can use it directly. Don't search for alternatives."
        }
    
    # Check if searching for web fetch tools
    if any(q in query_lower for q in web_fetch_queries):
        return {
            "success": True,
            "match_count": 1,
            "query": query,
            "guidance": """SERVER TOOL AVAILABLE: web_fetch

You have a web_fetch SERVER TOOL that's ALWAYS available.
This tool runs on Anthropic's servers and fetches full content from URLs.

HOW TO USE (NO execute_tool NEEDED):
You don't call search_tools() or execute_tool() for this. Just USE IT DIRECTLY in your content blocks.

EXAMPLE:
User: "Analyze this article: https://example.com/article"

Your response should include:
{
  "type": "tool_use",
  "name": "web_fetch",
  "input": {
    "url": "https://example.com/article"
  }
}

Claude API fetches content automatically on server
You receive full document content with citations
You analyze and respond to user

KEY POINTS:
- Server tool (no client execution)
- Max 10 fetches per conversation
- Fetches PDFs, web pages, documents
- Returns full content with citations
- Max 100,000 tokens per fetch
- Use for: analyzing URLs, reading documents, summarizing web content

WHEN TO USE:
- Analyze specific URL
- Read webpage content
- Extract info from PDF link
- Summarize document at URL
- Compare multiple URLs
- Follow up on web_search results

NEVER say "I need to find a web fetch tool" - YOU ALREADY HAVE IT!
Just use it directly.""",
            "available_platforms": ["anthropic_server_tools"],
            "tools": [{
                "name": "web_fetch",
                "description": "Server-side URL content fetching (always available)",
                "platform": "anthropic_server_tools",
                "type": "server_tool",
                "usage": "Use directly in content blocks with tool_use type, no execute_tool() needed"
            }],
            "critical_note": "This is a SERVER TOOL - it's not in your tools list but you can use it directly. Don't search for alternatives."
        }
    
    # Continue with normal search for client-side tools
    
    # Strategic alias expansion (NOT fuzzy logic - exact matches only)
    alias_map = {
        'microsoft': ['microsoft_', 'outlook_', 'teams_', 'onedrive_', 'word_', 'excel_', 'powerpoint_'],
        'microsoft 365': ['microsoft_', 'outlook_', 'teams_', 'onedrive_', 'word_', 'excel_', 'powerpoint_'],
        'm365': ['microsoft_', 'outlook_', 'teams_', 'onedrive_', 'word_', 'excel_', 'powerpoint_'],
        'office': ['outlook_', 'word_', 'excel_', 'powerpoint_', 'microsoft_'],
        'office 365': ['outlook_', 'word_', 'excel_', 'powerpoint_', 'microsoft_'],
        'google': ['google_', 'gmail_', 'gsheets_'],
        'google workspace': ['google_', 'gmail_', 'gsheets_', 'google_docs', 'google_calendar', 'google_drive'],
        'gsuite': ['google_', 'gmail_', 'gsheets_', 'google_docs', 'google_calendar', 'google_drive'],
        'email': ['gmail_', 'outlook_', 'email', 'send'],
        'mail': ['gmail_', 'outlook_', 'email', 'send'],
        'spreadsheet': ['sheets', 'excel', 'spreadsheet'],
        'sheets': ['sheets', 'excel', 'spreadsheet'],
        'document': ['docs', 'word', 'document'],
        'calendar': ['calendar', 'scheduling'],
        'chat': ['teams', 'slack', 'message'],
        'storage': ['drive', 'onedrive', 'dropbox'],
        'agent': ['assign_and_activate', 'request_update', 'respond_to'],
        'agents': ['assign_and_activate', 'request_update', 'respond_to'],
        'multi-agent': ['assign_and_activate', 'request_update', 'respond_to'],
        'coordination': ['assign_and_activate', 'request_update', 'respond_to', 'coordination'],
        'distribute': ['assign_and_activate', 'agent'],
        'delegate': ['assign_and_activate', 'agent'],
        # Calculator aliases for better discovery
        'quote': ['calculate'],
        'price': ['calculate'],
        'pricing': ['calculate'],
        'cost': ['calculate'],
        'shopify': ['calculate'],
        'signs': ['calculate_bollard', 'calculate_construction', 'calculate_election', 'calculate_corflute'],
        'sign': ['calculate_bollard', 'calculate_construction', 'calculate_election', 'calculate_corflute'],
        'booklet': ['calculate_saddle', 'calculate_spiral', 'calculate_wire'],
        'booklets': ['calculate_saddle', 'calculate_spiral', 'calculate_wire'],
        'book': ['calculate_saddle', 'calculate_spiral', 'calculate_wire', 'calculate_perfect'],
        'books': ['calculate_saddle', 'calculate_spiral', 'calculate_wire', 'calculate_perfect'],
        'notepad': ['calculate_notepads'],
        'notepads': ['calculate_notepads'],
        'business card': ['calculate_business_cards', 'calculate_economical', 'calculate_premium'],
        'business cards': ['calculate_business_cards', 'calculate_economical', 'calculate_premium'],
        'cards': ['calculate_business_cards', 'calculate_economical', 'calculate_premium', 'calculate_strut'],
        'flyer': ['calculate_flyers', 'calculate_folded'],
        'flyers': ['calculate_flyers', 'calculate_folded'],
        'letterhead': ['calculate_letterheads', 'calculate_printed'],
        'letterheads': ['calculate_letterheads', 'calculate_printed'],
        'sticker': ['calculate_custom_vinyl'],
        'stickers': ['calculate_custom_vinyl'],
        'vinyl': ['calculate_custom_vinyl'],
        'poster': ['calculate_custom_poster'],
        'posters': ['calculate_custom_poster'],
        'banner': ['calculate_luxury', 'calculate_pull_up'],
        'banners': ['calculate_luxury', 'calculate_pull_up'],
        'frame': ['calculate_metal_face', 'calculate_corflute_insert', 'calculate_selfie'],
        'frames': ['calculate_metal_face', 'calculate_corflute_insert', 'calculate_selfie'],
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
        },
        'agent': {
            'platforms': ['coordination', 'multi-agent', 'cross-thread'],
            'guidance': "Multi-Agent Coordination - 3 tools to distribute work across 26 AI agents:\n\n1. assign_and_activate_agent_with_slugs - PRIMARY TOOL for work distribution\n   - Assign work to any of 26 NATO agents (Alpha-Zulu)\n   - Attach workflows, docs, synergy sessions\n   - Automatic UI updates and agent triggering\n\n2. request_update_from_thread - Request info from another agent\n   - Cross-thread communication with priority levels\n   - Track requests in database\n\n3. respond_to_cross_thread_request - Respond to incoming requests\n   - Complete request/response cycle\n\nUse list_platform_tools('agent') or list_platform_tools('advanced_agent_coordination') for detailed info."
        }
    }
    
    # Determine search keywords (expand aliases or use query directly)
    search_keywords = []
    
    # Check for exact alias match first
    if query_lower in alias_map:
        search_keywords = alias_map[query_lower]
    else:
        # No alias - check if any alias appears as substring in query
        alias_found = False
        for alias, expansions in alias_map.items():
            if alias in query_lower:
                search_keywords.extend(expansions)
                alias_found = True
        
        # If no alias found, use query directly for substring matching
        if not alias_found:
            search_keywords = [query_lower]
    
    # Search tool names and descriptions (exact substring matching only)
    matching_tools = []
    matched_tool_names = set()
    
    for tool_name, tool in registry.tools.items():
        # Skip meta-tools in search results
        if tool_name.startswith(('list_', 'get_platform', 'recommend_', 'execute_', 'search_')):
            continue
        
        if tool_name in matched_tool_names:
            continue
        
        description = tool.get("description", "").lower()
        
        # Check if any search keyword appears in tool name or description
        matched = False
        for keyword in search_keywords:
            if keyword in tool_name.lower() or keyword in description:
                matched = True
                break
        
        if matched:
            matching_tools.append({
                "name": tool_name,
                "short_description": tool.get("short_description", tool.get("description", "")),
                "platform": tool.get("platform", "unknown")
            })
            matched_tool_names.add(tool_name)
    
    # Sort alphabetically by name
    matching_tools.sort(key=lambda x: x["name"])
    
    # Build response
    result = {
        "success": True,
        "query": query,
        "match_count": len(matching_tools),
        "tools": matching_tools[:50],  # Limit to 50 results
        "search_method": "exact_substring_matching",
        "aliases_available": list(alias_map.keys()),
        "next_steps": (
            "To use a tool: 1) Call get_tool_schema(tool_name) to see parameters, "
            "2) Call execute_tool(tool_name, parameters={...}) — pass tool "
            "arguments under the `parameters` dict, not as top-level kwargs."
        )
    }
    
    # Add smart guidance for broad platform searches
    for broad_query, components in platform_components.items():
        if query_lower in broad_query or broad_query in query_lower:
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
    guide += (
        "3. Call execute_tool(tool_name, parameters={...}) to use the tool — "
        "pass tool arguments under the `parameters` dict, not as top-level "
        "kwargs.\n"
    )
    
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
    # Delegate to search_tools which has full alias expansion and matching logic
    return search_tools(task_description, **kwargs)


def execute_tool(
    tool_name: str = None,
    parameters: Optional[Dict[str, Any]] = None,
    **tool_params,
) -> Dict[str, Any]:
    """
    Execute ANY tool by name (proxy function for dynamic tool execution)

    This allows Claude to call tools after discovering them via list_platform_tools(),
    without needing all 603 tool schemas sent upfront.

    MULTI-PROVIDER COMPATIBLE: Handles both Anthropic (Claude) and OpenAI (GPT) formats.

    Anthropic sends: execute_tool(input={"tool_name": "X", "param": "Y"})
    OpenAI sends: execute_tool(arguments='{"tool_name": "X", "param": "Y"}')

    PASSING TOOL PARAMETERS
    -----------------------
    The MCP server builds this function's JSON schema from the typed
    signature. ``**tool_params`` is invisible to the schema, so any tool
    argument passed as a top-level kwarg is dropped at MCP validation time
    (the bug that caused ``gmail_get_message(message_id=...)`` to lose
    ``message_id`` and crash with ``missing 1 required positional argument``).

    To forward arguments, the AI must pass them under the typed
    ``parameters`` argument (a JSON object). The convention is:

        execute_tool(
            tool_name="gmail_get_message",
            parameters={"message_id": "19f993e672f4c126", "format": "full"},
        )

    ``parameters`` accepts either a dict or a JSON string (auto-parsed).
    The merged kwargs are then forwarded to ``registry.execute_tool()``.

    Args:
        tool_name: Name of tool to execute (e.g., 'gmail_send_email',
            'google_docs_create') [REQUIRED]
        parameters: Dict (or JSON string) of arguments to forward to the
            tool. Optional tool parameters belong here, NOT as top-level
            kwargs. ``_user_id`` and ``_injected_credentials`` are added
            by the MCP auth layer and survive the merge.
        **tool_params: Reserved for future use. Currently the MCP schema
            does not expose top-level kwargs, so anything passed here is
            silently dropped. Use ``parameters`` instead.

    Returns:
        Result from the executed tool
    """
    import json
    from tools.registry_v3 import get_registry

    # MULTI-PROVIDER PARAMETER EXTRACTION
    # Handle 4 different ways providers send parameters:

    # 1. Direct parameter (least common, but check first)
    extracted_tool_name = tool_name
    params = dict(tool_params)

    # 2. Anthropic format: tool_name in kwargs
    if not extracted_tool_name and 'tool_name' in params:
        extracted_tool_name = params.pop('tool_name')

    # 3. OpenAI format: JSON string in 'arguments'
    if not extracted_tool_name and 'arguments' in params:
        arguments = params.pop('arguments')
        if isinstance(arguments, str):
            try:
                args_dict = json.loads(arguments)
                extracted_tool_name = args_dict.pop('tool_name', None)
                params.update(args_dict)  # Merge remaining args
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Failed to parse arguments JSON: {str(e)}",
                    "received_arguments": arguments[:100]
                }

    # 4. Nested input object (some API wrappers)
    if not extracted_tool_name and 'input' in params:
        input_obj = params.pop('input')
        if isinstance(input_obj, dict):
            extracted_tool_name = input_obj.pop('tool_name', None)
            params.update(input_obj)

    # 5. Typed `parameters` argument (the new MCP-safe path).
    # Because the function signature declares `parameters: Optional[Dict]`,
    # the MCP server's generated JSON schema exposes it as a typed object
    # property — so values passed here actually reach this function.
    #
    # This step runs LAST so that ``parameters`` overrides values from
    # every earlier extraction shape (direct kwargs, Anthropic ``input``,
    # OpenAI ``arguments``). Two rules govern the merge:
    #
    #   (a) Non-``_`` keys from ``parameters`` win over kwargs — the AI's
    #       explicit, typed request is the source of truth for tool args.
    #   (b) ``_``-prefixed keys from ``parameters`` are ignored — auth-layer
    #       injections (``_user_id``, ``_injected_credentials``) must not
    #       be overridable by an AI-supplied dict, even by accident.
    if parameters is not None:
        if isinstance(parameters, str):
            try:
                parameters = json.loads(parameters)
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Failed to parse 'parameters' JSON: {str(e)}",
                    "received_parameters": parameters[:100],
                }
        if isinstance(parameters, dict):
            for k, v in parameters.items():
                if not k.startswith('_'):
                    params[k] = v
        else:
            return {
                "success": False,
                "error": (
                    "'parameters' must be a dict or JSON string, got "
                    f"{type(parameters).__name__}"
                ),
                "received_type": str(type(parameters)),
            }

    # NOTE: nested 'parameters' unwrapping used to live at this position
    # in the function. It has moved to step 5 (typed ``parameters`` arg)
    # so the MCP schema actually exposes the field and the AI's tool
    # arguments survive validation. Keeping a 'parameters' key in
    # **tool_params** for backward compatibility is fine: the early
    # extraction shapes (Anthropic ``input``, OpenAI ``arguments``)
    # already merged anything they found there into ``params``.

    # Validate tool_name extracted
    if not extracted_tool_name:
        return {
            "success": False,
            "error": "❌ MISSING PARAMETER: tool_name is required",
            "correct_usage": (
                "execute_tool(tool_name='exact_tool_name', "
                "parameters={'param1': 'value1', 'param2': 'value2'})"
            ),
            "workflow": {
                "step_1": "First discover tools: search_tools(query='keyword') or list_platform_tools(platform='name')",
                "step_2": "Get parameters: get_tool_schema(tool_name='exact_tool_name')",
                "step_3": (
                    "Then execute: execute_tool(tool_name='exact_tool_name', "
                    "parameters={...})"
                ),
                "warning": (
                    "MCP drops top-level kwargs because the JSON schema "
                    "only declares `tool_name`. Always pass tool "
                    "arguments under the `parameters` dict."
                ),
            },
            "received_params": list(tool_params.keys()),
            "example": {
                "discovery": "search_tools(query='excel create')",
                "get_params": "get_tool_schema(tool_name='microsoft_excel_create_workbook')",
                "execution": (
                    "execute_tool("
                    "tool_name='microsoft_excel_create_workbook', "
                    "parameters={'name': 'My Spreadsheet'})"
                ),
            },
            "note": "You MUST pass tool_name parameter. Do NOT call execute_tool() without tool_name.",
        }
    
    registry = get_registry()
    
    # Check if tool exists
    if extracted_tool_name not in registry.tools:
        # Try to suggest similar tools
        all_tools = list(registry.tools.keys())
        suggestions = [t for t in all_tools if extracted_tool_name.lower() in t.lower()][:5]
        
        return {
            "success": False,
            "error": f"❌ TOOL NOT FOUND: '{extracted_tool_name}' does not exist in registry",
            "similar_tools": suggestions if suggestions else None,
            "hint": "You likely guessed the wrong tool name. Use discovery tools instead of guessing.",
            "correct_workflow": {
                "instead_of_guessing": "DO NOT guess tool names like 'google_sheets_create_spreadsheet'",
                "step_1": "Use search_tools(query='sheets create') to find actual tool names",
                "step_2": "Or use list_platform_tools(platform='google_sheets') to list all tools",
                "step_3": "Use the EXACT tool name from the discovery results",
                "step_4": (
                    "Call execute_tool(tool_name='exact_name_from_discovery', "
                    "parameters={...}) — pass tool arguments under the "
                    "`parameters` dict, not as top-level kwargs."
                ),
            },
            "available_discovery_tools": [
                "search_tools(query='keyword') - Search across all 1071 tools",
                "list_available_platforms() - See all platform names",
                "list_platform_tools(platform='name') - List tools for platform",
                "get_tool_schema(tool_name='name') - Get parameters before executing"
            ],
            "common_mistakes": {
                "wrong_1": "microsoft_word_create_document (guessed name - does not exist)",
                "correct_1": "search_tools(query='word create') → use exact name from results",
                "wrong_2": "google_sheets_create_spreadsheet (guessed name - does not exist)",
                "correct_2": "search_tools(query='sheets create') → use exact name from results"
            },
            "available_tool_count": len(all_tools),
            "registry_stats": f"Total tools available: {len(all_tools)} across all platforms"
        }
    
    # Execute the tool with credential injection
    try:
        # Log execution attempt
        print(f"\n[META-TOOL] execute_tool() called:")
        print(f"  - Target tool: {extracted_tool_name}")
        print(f"  - Parameters: {list(params.keys())}")
        print(f"  - Has _user_id: {'_user_id' in params}")
        print(f"  - Has _injected_credentials: {'_injected_credentials' in params}")
        if '_user_id' in params:
            print(f"  - User ID: {params['_user_id']}")
        
        # Log parameter values (for debugging - exclude sensitive fields)
        safe_params = {k: v for k, v in params.items() 
                      if k not in ['_injected_credentials', 'password', 'api_key', 'token']}
        print(f"  - Safe parameter values: {safe_params}")
        
        # CRITICAL: registry.execute_tool() only accepts **kwargs, not positional args
        # Must pass tool_name inside kwargs dictionary
        result = registry.execute_tool(tool_name=extracted_tool_name, **params)
        
        # ✅ FIX (Jan 19, 2026): Handle different return types (dict, list, primitives)
        if isinstance(result, dict):
            success_status = result.get('success', 'unknown')
            print(f"[META-TOOL] execute_tool() result: success={success_status}")
            if not success_status:
                print(f"[META-TOOL] Error from target tool: {result.get('error', 'No error message')}")
        elif isinstance(result, list):
            print(f"[META-TOOL] execute_tool() result: list with {len(result)} items")
        else:
            print(f"[META-TOOL] execute_tool() result: {type(result).__name__}")
        
        return {
            "success": True,
            "tool": extracted_tool_name,
            "result": result,
            "parameters_used": list(params.keys())
        }
    except Exception as e:
        import traceback
        error_details = {
            "success": False,
            "error": f"Tool execution failed: {str(e)}",
            "tool": extracted_tool_name,
            "parameters_received": list(params.keys()),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        
        # Log the error
        print(f"\n[META-TOOL ERROR] execute_tool() failed:")
        print(f"  - Tool: {extracted_tool_name}")
        print(f"  - Error: {str(e)}")
        print(f"  - Error Type: {type(e).__name__}")
        print(f"  - Traceback:\n{traceback.format_exc()}")
        
        return error_details


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