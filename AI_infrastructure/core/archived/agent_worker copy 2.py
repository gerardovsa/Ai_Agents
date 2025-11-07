"""
Agent Worker
Background thread that executes ToolUseAgent with SSE streaming
Replaces OLD Flask's run_agent_worker() with cleaner implementation

FIXED: All registry.execute_tool() calls now use keyword argument for tool_name
FIXED: Strip thinking blocks before storing in conversation history (Nov 5, 2025)
"""
import json
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from queue import Queue
import threading


def strip_thinking_blocks(content: List[Dict]) -> List[Dict]:
    """
    Remove thinking blocks from content array
    
    Thinking blocks are shown to user in real-time via SSE,
    but should NOT be stored in conversation history.
    
    This prevents Claude API format errors on subsequent requests:
    "If an assistant message contains any thinking blocks,
     the first block must be 'thinking' or 'redacted_thinking'"
    
    Args:
        content: List of content blocks from Claude response
    
    Returns:
        Content without thinking/redacted_thinking blocks
    """
    if not isinstance(content, list):
        return content
    
    return [
        block for block in content
        if block.get('type') not in ('thinking', 'redacted_thinking')
    ]


def prepare_content_for_storage(content: List[Dict]) -> List[Dict]:
    """
    Prepare assistant message content for database storage
    
    BEST PRACTICE (ChatGPT/Claude.ai pattern):
    - Keep: text blocks (main response)
    - Keep: tool_use blocks (shows what AI requested)
    - Remove: thinking blocks (already shown in real-time)
    - Remove: tool_result blocks (too verbose, not needed for context)
    
    This creates clean, focused conversation history that:
    1. Provides context for future turns
    2. Shows transparency (what tools were used)
    3. Avoids format errors with Claude API
    4. Reduces database bloat
    
    Args:
        content: List of content blocks from Claude response
    
    Returns:
        Filtered content ready for storage
    """
    if not isinstance(content, list):
        return content
    
    return [
        block for block in content
        if block.get('type') in ('text', 'tool_use')
        # Excludes: thinking, redacted_thinking, tool_result
    ]


def reorder_assistant_content_blocks(content: List[Dict]) -> List[Dict]:
    """
    Validate and reorder assistant message content blocks to satisfy Anthropic API requirements
    
    CRITICAL ANTHROPIC API RULES:
    1. If an assistant message contains any thinking blocks, the first block 
       MUST be 'thinking' or 'redacted_thinking'.
    2. tool_result blocks can ONLY be in user messages, never assistant
    3. Thinking blocks must have a 'thinking' string field
    
    This function:
    - Removes invalid blocks (tool_result, invalid thinking)
    - Reorders valid blocks (thinking first, then others)
    
    Args:
        content: List of content blocks from assistant message
    
    Returns:
        Validated and reordered content with thinking blocks first
    """
    if not isinstance(content, list) or not content:
        return content
    
    # STEP 1: Validate and filter blocks
    validated_blocks = []
    for block in content:
        if not isinstance(block, dict):
            continue
        
        # RULE 1: tool_result blocks are FORBIDDEN in assistant messages
        if block.get('type') == 'tool_result':
            print(f"[Agent Worker] ⚠️ Removing tool_result from assistant message (invalid)")
            continue
        
        # RULE 2: Thinking blocks must have 'thinking' field
        if block.get('type') == 'thinking':
            if 'thinking' not in block or not isinstance(block.get('thinking'), str):
                print(f"[Agent Worker] ⚠️ Removing invalid thinking block (missing 'thinking' field)")
                continue
        
        validated_blocks.append(block)
    
    if not validated_blocks:
        return []
    
    # STEP 2: Check if there are any thinking blocks
    has_thinking = any(
        block.get('type') in ('thinking', 'redacted_thinking')
        for block in validated_blocks
    )
    
    if not has_thinking:
        return validated_blocks  # No thinking blocks, no need to reorder
    
    # STEP 3: Check if first block is already thinking
    first_block_type = validated_blocks[0].get('type')
    if first_block_type in ('thinking', 'redacted_thinking'):
        return validated_blocks  # Already correct order
    
    # STEP 4: Reorder: thinking blocks first, then others
    thinking_blocks = [
        b for b in validated_blocks 
        if b.get('type') in ('thinking', 'redacted_thinking')
    ]
    other_blocks = [
        b for b in validated_blocks 
        if b.get('type') not in ('thinking', 'redacted_thinking')
    ]
    
    print(f"[Agent Worker] 🔧 Reordered: {len(thinking_blocks)} thinking + {len(other_blocks)} other blocks")
    return thinking_blocks + other_blocks

# Add calculator module path to import ToolUseAgent
calculator_module_path = os.path.join(os.path.dirname(__file__), '..', '..', 'UI', 'external', 'modules', 'calculator-module', 'ORIGINAL')
sys.path.insert(0, calculator_module_path)

# Import REAL ToolUseAgent from calculator module (optional - provides additional quote tools)
try:
    from tool_use_agent import ToolUseAgent
    TOOL_USE_AGENT_AVAILABLE = True
    print("✅ [Agent Worker] ToolUseAgent imported - Quote Calculator tools available")
except ImportError as e:
    # This is OPTIONAL - system works fine without it
    TOOL_USE_AGENT_AVAILABLE = False
    print("ℹ️  [Agent Worker] Quote Calculator module not found (optional)")
    print("   → Using 584 registry_v3 tools (all features available)")
    
    # Fallback placeholder
    class ToolUseAgent:
        """Placeholder - using registry_v3 tools only"""
        def __init__(self, config_path=None):
            self.tools = []
        def _get_tool_definitions(self):
            return []
        def execute_tool(self, tool_name, tool_input):
            return {"status": "Tool execution via unified_ai_client", "tool": tool_name}


def run_agent_worker(
    agent_id: str,
    prompt: str,
    file_data: List[Dict[str, Any]],
    lock: threading.Lock,
    session_id: str,
    queue: Queue,
    conversation_history: Optional[List[Dict]] = None,
    context: str = 'triple_agent',
    user_id: Optional[int] = None
):
    """
    Background worker that executes ToolUseAgent
    
    Args:
        agent_id: Agent identifier (1, 2, 3, stock_ai, single_viewer)
        prompt: User prompt text
        file_data: List of file dicts with {filename, content_type, data (bytes)}
        lock: threading.Lock for thread safety
        session_id: Session ID
        queue: Queue for SSE events
        conversation_history: Previous conversation for context
        context: UI context (triple_agent, single_viewer, stock_management)
        user_id: User ID for OAuth credential injection (optional, defaults to 1 if None)
    """
    
    # Default user_id to 1 if not provided
    if user_id is None:
        user_id = 1
        print(f"[Agent Worker {agent_id}] No user_id provided, defaulting to {user_id}")
    
    log_prefix = f"[Agent Worker {agent_id}]"
    
    try:
        print(f"{log_prefix} Starting for session {session_id[:8]}...")
        
        # Build content blocks from files
        content_blocks = []
        
        # Add files as content blocks
        for file_info in file_data:
            filename = file_info.get('filename', 'unknown')
            content_type = file_info.get('content_type', 'application/octet-stream')
            file_bytes = file_info.get('data', b'')
            
            # Encode to base64
            import base64
            encoded_data = base64.b64encode(file_bytes).decode('utf-8')
            
            # Determine content block type
            if content_type == 'application/pdf':
                block_type = 'document'
            elif content_type.startswith('image/'):
                block_type = 'image'
            else:
                block_type = 'document'  # Default to document
            
            content_blocks.append({
                'type': block_type,
                'source': {
                    'type': 'base64',
                    'media_type': content_type,
                    'data': encoded_data
                }
            })
            
            print(f"{log_prefix} Added {block_type}: {filename} ({len(file_bytes)} bytes)")
        
        # Add text prompt
        if prompt:
            content_blocks.append({
                'type': 'text',
                'text': prompt
            })
        elif not content_blocks:
            # No files, no prompt - error
            queue.put({'type': 'error', 'error': 'No prompt or files provided'})
            return
        
        #  INTEGRATE TOOLUSEAGENT - Real implementation
        print(f"{log_prefix} Initializing ToolUseAgent...")
        
        # Initialize ToolUseAgent with log callback for SSE streaming
        def log_callback(log_entry: dict):
            """Stream ToolUseAgent logs to SSE queue"""
            event_type = log_entry.get('type', 'log')
            
            # Map ToolUseAgent events to SSE events
            if event_type == 'thinking':
                queue.put({'type': 'thinking', 'content': log_entry.get('content', '')})
            elif event_type == 'tool_use':
                queue.put({'type': 'tool_use', 'tool_name': log_entry.get('tool_name', ''), 'input': log_entry.get('input', {})})
            elif event_type == 'tool_result':
                queue.put({'type': 'tool_result', 'tool_name': log_entry.get('tool_name', ''), 'output': log_entry.get('output', '')})
            elif event_type == 'response':
                queue.put({'type': 'response', 'content': log_entry.get('content', '')})
            elif event_type == 'error':
                queue.put({'type': 'error', 'error': log_entry.get('error', '')})
        
        try:
            # Initialize agent (config path relative to AI_infrastructure)
            config_path = 'config/database-config.json'
            agent = ToolUseAgent(config_path, log_callback=log_callback)
            
            # Send initial thinking event
            queue.put({'type': 'thinking', 'content': 'Processing with Tool Use API...'})
            
            # Process request with ToolUseAgent
            result = agent.process_request(
                customer_message=prompt,
                max_turns=20,
                conversation_history=conversation_history,
                content_blocks=content_blocks if file_data else None
            )
            
            # Check success
            if result.get('success'):
                final_response = result.get('final_response', '')
                
                # Send final response
                queue.put({
                    'type': 'response',
                    'content': final_response
                })
                
                # Signal completion
                queue.put({
                    'type': 'complete',
                    'result': final_response,
                    'session_id': session_id,
                    'tool_calls': result.get('tool_calls', 0),
                    'thinking_tokens': result.get('thinking_tokens', 0)
                })
                
                print(f"{log_prefix} Complete ({len(final_response)} chars, {result.get('tool_calls', 0)} tools)")
            else:
                # Error in processing
                error_msg = result.get('error', 'Unknown error')
                queue.put({'type': 'error', 'error': error_msg})
                print(f"{log_prefix} Error: {error_msg}")
            
            # Close agent cleanly
            agent.close()
            
        except Exception as e:
            error_msg = str(e)
            print(f"{log_prefix} ToolUseAgent error: {error_msg}")
            import traceback
            traceback.print_exc()
            queue.put({'type': 'error', 'error': error_msg})
        
    except Exception as e:
        error_msg = str(e)
        print(f"{log_prefix} Worker error: {error_msg}")
        import traceback
        traceback.print_exc()
        queue.put({'type': 'error', 'error': error_msg})
    
    finally:
        # Release lock
        try:
            lock.release()
            print(f"{log_prefix} Lock released")
        except Exception as e:
            print(f"{log_prefix} Lock release error: {e}")


def run_simple_agent_worker(
    agent_id: str,
    prompt: str,
    lock: threading.Lock,
    session_id: str,
    queue: Queue,
    conversation_history: Optional[List[Dict]] = None,
    ai_client = None,
    user_id: int = 1
):
    """
    Simplified worker for text-only prompts (no files)
    
    Used by Triple Agent for quick queries
    
    Args:
        user_id: User ID for OAuth credential injection (defaults to 1)
    """
    
    log_prefix = f"[Simple Agent {agent_id}]"
    
    print(f"\n{'='*60}")
    print(f"{log_prefix} WORKER THREAD STARTED!")
    print(f"{log_prefix} Session: {session_id[:8] if session_id else 'None'}...")
    print(f"{log_prefix} Prompt: {prompt[:50] if prompt else 'None'}...")
    print(f"{log_prefix} AI Client: {ai_client is not None}")
    print(f"{log_prefix} Queue: {queue}")
    print(f"{'='*60}\n")
    
    try:
        print(f"{log_prefix} Starting for session {session_id[:8]}...")
        
        # Validate ai_client
        if ai_client is None:
            print(f"{log_prefix} ERROR: ai_client is None!")
            raise ValueError("ai_client is required but was not provided")
        
        # ✅ FIX: Load tools from registry with JUST-IN-TIME SCHEMA LOADING
        from tools import registry_v3
        registry = registry_v3.get_registry()
        
        # ✅ JUST-IN-TIME SCHEMA LOADING:
        # Turn 1: Send only meta-tools (5 tools, 431 tokens)
        # Turn 2+: Send meta-tools + ONLY requested schemas (~600-800 tokens per turn)
        # NEVER send all 607 schemas!
        
        conversation_length = len(conversation_history or [])
        
        # Meta-tools always included for discovery
        meta_tool_names = [
            'list_available_platforms',
            'list_platform_tools',
            'get_tool_schema',  # ← KEY: AI requests specific tool schemas here
            'get_platform_guide',
            'recommend_tools_for_task'
        ]
        
        # Get meta-tools from registry
        all_tools_dict = {t['name']: t for t in registry.get_anthropic_tools()}
        meta_tools = [all_tools_dict[name] for name in meta_tool_names if name in all_tools_dict]
        
        # Track which tool schemas have been explicitly requested
        requested_tool_schemas = set()
        
        if conversation_history:
            # Parse conversation to find get_tool_schema calls
            # When AI calls get_tool_schema('tool_name'), we extract the tool_name
            for msg in conversation_history:
                if msg.get('role') == 'user' and isinstance(msg.get('content'), list):
                    for block in msg['content']:
                        if isinstance(block, dict) and block.get('type') == 'tool_result':
                            # Check if this is result from get_tool_schema
                            content = block.get('content', '')
                            if isinstance(content, str) and 'tool_name' in content and 'input_schema' in content:
                                # Extract tool name from schema result
                                try:
                                    import json
                                    schema_result = json.loads(content) if isinstance(content, str) else content
                                    if 'tool_name' in schema_result:
                                        tool_name = schema_result['tool_name']
                                        requested_tool_schemas.add(tool_name)
                                        print(f"{log_prefix} 🔷 Tracked requested schema: {tool_name}")
                                except:
                                    pass
        
        # Build final tools list: meta-tools + requested schemas
        tools = meta_tools.copy()
        
        for tool_name in requested_tool_schemas:
            if tool_name in all_tools_dict:
                tools.append(all_tools_dict[tool_name])
        
        print(f"{log_prefix} 🔷 [Just-In-Time Schema Loading] Turn {conversation_length + 1}:")
        print(f"{log_prefix} 🔷   Meta-tools: {len(meta_tools)}")
        print(f"{log_prefix} 🔷   Requested schemas: {len(requested_tool_schemas)}")
        print(f"{log_prefix} 🔷   Total: {len(tools)} tools sent")
        if requested_tool_schemas:
            print(f"{log_prefix} 🔷   Requested tools: {sorted(list(requested_tool_schemas))}")
        
        # Use default general agent context (no context parameter in this function)
        prompt_name = 'data_agent_chat'
        print(f"{log_prefix} Using general agent context")
        
        system_prompt = ai_client.get_system_prompt(prompt_name)
        print(f"{log_prefix} System prompt loaded: {prompt_name} ({len(system_prompt)} chars)")
        
        # Inject location and temperature context into system prompt
        from core.ip_location import get_location_for_prompt, get_location_dict
        try:
            # Get location with all data including temperature
            location_dict = get_location_dict()
            location_string = get_location_for_prompt()
            
            # Extract data for context string
            current_time_str = location_dict.get('current_time', 'Unknown time')
            day_of_week = location_dict.get('day_of_week', 'Unknown')
            season = location_dict.get('season', 'Unknown season')
            temp_c = location_dict.get('temperature_c')
            temp_f = location_dict.get('temperature_f')
            weather_condition = location_dict.get('weather_condition', 'Unknown')
            
            # Extract month name from date
            from datetime import datetime
            date_str = location_dict.get('date', '')
            try:
                month_name = datetime.strptime(date_str, '%Y-%m-%d').strftime('%B')
            except:
                month_name = 'November'
            
            # Build comprehensive time context with temperature
            if temp_c is not None:
                temp_str = f"{temp_c}°C ({temp_f}°F), {weather_condition}"
                time_context = f"{location_string} | {day_of_week}, {current_time_str} | {month_name} ({season}) | {temp_str}"
            else:
                time_context = f"{location_string} | {day_of_week}, {current_time_str} | {month_name} ({season})"
            
            # Replace placeholder in system prompt
            system_prompt = system_prompt.replace('{{USER_LOCATION}}', time_context)
            
            print(f"{log_prefix} 📍 Location context: {location_string}")
            print(f"{log_prefix} 🕐 Time context: {day_of_week}, {current_time_str}")
            if temp_c is not None:
                print(f"{log_prefix} 🌡️  Temperature: {temp_c}°C ({temp_f}°F), {weather_condition}")
        except Exception as e:
            print(f"{log_prefix} ⚠️  Failed to inject location context: {e}")
            # Use fallback placeholder replacement
            system_prompt = system_prompt.replace('{{USER_LOCATION}}', 'Location unavailable')
        
        # Build messages with history
        messages = []
        if conversation_history:
            # Validate and reorder all messages in conversation history
            print(f"{log_prefix} 🔍 Validating {len(conversation_history)} messages from history...")
            
            for idx, msg in enumerate(conversation_history):
                msg_copy = msg.copy()  # Don't mutate original
                
                # Validate assistant messages
                if msg_copy.get('role') == 'assistant' and isinstance(msg_copy.get('content'), list):
                    # Use reorder_assistant_content_blocks which now includes validation
                    msg_copy['content'] = reorder_assistant_content_blocks(msg_copy['content'])
                    
                    # If validation removed all blocks, skip this message
                    if not msg_copy['content']:
                        print(f"{log_prefix} ⚠️ Skipping message {idx} - all blocks were invalid")
                        continue
                
                # Validate user messages (check for orphaned tool_results)
                elif msg_copy.get('role') == 'user' and isinstance(msg_copy.get('content'), list):
                    # Check if previous message was assistant with tool_use
                    has_tool_use_before = False
                    if messages and messages[-1].get('role') == 'assistant':
                        prev_content = messages[-1].get('content', [])
                        has_tool_use_before = any(
                            b.get('type') == 'tool_use' for b in prev_content if isinstance(b, dict)
                        )
                    
                    # If no tool_use before, remove tool_result blocks (orphaned)
                    if not has_tool_use_before:
                        validated_user_content = []
                        for block in msg_copy['content']:
                            if isinstance(block, dict) and block.get('type') == 'tool_result':
                                print(f"{log_prefix} ⚠️ Removing orphaned tool_result from message {idx}")
                                continue
                            validated_user_content.append(block)
                        msg_copy['content'] = validated_user_content
                        
                        # If all blocks removed, skip message
                        if not msg_copy['content']:
                            print(f"{log_prefix} ⚠️ Skipping message {idx} - all blocks were orphaned")
                            continue
                
                messages.append(msg_copy)
            
            print(f"{log_prefix} ✅ Validated history: {len(messages)} valid messages")
        
        messages.append({'role': 'user', 'content': prompt})
        
        # ✅ Call AI with Extended Thinking + Server Tools + Tool Usage Instructions
        response = ai_client.create_message(
            messages=messages,
            provider='anthropic',
            model='claude-sonnet-4-5-20250929',
            max_tokens=16000,
            system=system_prompt,  # ✅ Include tool usage instructions
            tools=tools,  # Client tools (584+ from registry)
            enable_thinking=True,  # ✅ Extended Thinking
            thinking_budget=5000,  # Token budget for thinking
            enable_web_search=True,  # ✅ Web Search server tool
            enable_web_fetch=True  # Web Fetch (optional, BETA)
        )
        
        # Extract text, thinking blocks, and tool uses
        response_text = ''
        thinking_content = ''
        tool_uses = []
        
        if isinstance(response, dict) and 'content' in response:
            for block in response['content']:
                # Handle thinking blocks
                if block.get('type') == 'thinking':
                    thinking_content += block.get('thinking', '')
                    # Send thinking to client
                    queue.put({
                        'type': 'thinking_block',
                        'content': block.get('thinking', '')
                    })
                # Handle text blocks
                elif block.get('type') == 'text':
                    response_text += block.get('text', '')
                # Handle tool use blocks
                elif block.get('type') == 'tool_use':
                    tool_uses.append(block)
        
        # ✅ TOOL EXECUTION LOOP: Continue while AI wants to use tools
        max_tool_iterations = 20  # Prevent infinite loops
        tool_iteration = 0
        current_response = response
        
        while (tool_uses and current_response.get('stop_reason') == 'tool_use' and 
               tool_iteration < max_tool_iterations):
            
            tool_iteration += 1
            print(f"{log_prefix} 🔧 Tool iteration {tool_iteration}: AI requested {len(tool_uses)} tool(s)")
            
            # Send initial text response if any (only on first iteration)
            if tool_iteration == 1 and response_text:
                queue.put({'type': 'content_delta', 'text': response_text})
            
            # Execute each tool and collect results
            tool_results = []
            for tool_use in tool_uses:
                tool_name = tool_use.get('name')
                tool_input = tool_use.get('input', {})
                tool_id = tool_use.get('id')
                
                print(f"{log_prefix} 🔧 Executing tool: {tool_name}")
                
                # CRITICAL: Server tools (web_search, web_fetch) are executed by Anthropic API
                # They should NOT be executed locally - skip them and let API handle them
                server_tools = ['web_search', 'web_fetch']
                if tool_name in server_tools:
                    print(f"{log_prefix} ⚠️  SERVER TOOL: {tool_name} - Executed by Anthropic API (skipping local execution)")
                    # Server tools are handled by Anthropic - results come back automatically
                    # DO NOT add to tool_results - API provides these directly
                    continue
                
                # Send tool_use event to UI
                queue.put({
                    'type': 'tool_use',
                    'tool_name': tool_name,
                    'tool_input': tool_input
                })
                
                try:
                    # CRITICAL: Meta-tools (get_tool_schema, execute_tool) have a special case:
                    # They ARE tools themselves AND they take a 'tool_name' parameter
                    # This causes a conflict when calling registry.execute_tool(tool_name='execute_tool', tool_name='target_tool')
                    # Solution: Call the meta-tool function directly, not through registry
                    meta_tools_that_need_special_handling = ['get_tool_schema', 'execute_tool']
                    
                    if tool_name in meta_tools_that_need_special_handling:
                        # Get the meta-tool function directly
                        from tools.implementations.meta_tools import execute_tool as execute_tool_fn, get_tool_schema as get_tool_schema_fn
                        
                        # DEBUG: Log what we're receiving
                        print(f"{log_prefix} ===== META-TOOL CALL =====")
                        print(f"{log_prefix} Meta-tool name: {tool_name}")
                        print(f"{log_prefix} Tool input keys: {list(tool_input.keys())}")
                        print(f"{log_prefix} User ID: {user_id}")
                        
                        if tool_name == 'execute_tool':
                            print(f"{log_prefix} Calling execute_tool_fn with:")
                            print(f"{log_prefix}   - Target tool: {tool_input.get('tool_name', 'MISSING')}")
                            print(f"{log_prefix}   - User ID: {user_id}")
                            print(f"{log_prefix}   - Credentials: True")
                            
                            # CRITICAL: Pass user_id and injected_credentials to meta-tool
                            # so it can forward them to the target tool for credential injection
                            result = execute_tool_fn(
                                **tool_input,
                                _user_id=user_id,
                                _injected_credentials=True
                            )
                            
                            print(f"{log_prefix} execute_tool_fn returned:")
                            print(f"{log_prefix}   - Success: {result.get('success', 'unknown')}")
                            if not result.get('success'):
                                print(f"{log_prefix}   - Error: {result.get('error', 'No error')}")
                            elif 'result' in result:
                                print(f"{log_prefix}   - Target tool success: {result.get('result', {}).get('success', 'unknown')}")
                                if not result.get('result', {}).get('success'):
                                    print(f"{log_prefix}   - Target tool error: {result.get('result', {}).get('error', 'No error')}")
                                    
                        elif tool_name == 'get_tool_schema':
                            print(f"{log_prefix} Calling get_tool_schema_fn for: {tool_input.get('tool_name', 'MISSING')}")
                            # get_tool_schema doesn't need credentials (just returns schema)
                            result = get_tool_schema_fn(**tool_input)
                            print(f"{log_prefix} get_tool_schema_fn returned: success={result.get('success', 'unknown')}")
                    else:
                        # For regular tools: remove tool_name from input (it's just the tool to execute)
                        tool_input_copy = {k: v for k, v in tool_input.items() if k != 'tool_name'}
                        
                        # CRITICAL FIX: Pass credentials to ALL platform tools
                        # Pass _user_id/_injected_credentials for Google Workspace and Microsoft 365 tools
                        if tool_name.startswith(('google_', 'microsoft_')):
                            result = registry.execute_tool(
                                tool_name=tool_name,
                                _user_id=user_id,
                                _injected_credentials=True,
                                **tool_input_copy
                            )
                        else:
                            result = registry.execute_tool(
                                tool_name=tool_name,
                                **tool_input_copy
                            )
                    
                    # Send tool_result event to UI
                    queue.put({
                        'type': 'tool_result',
                        'tool_name': tool_name,
                        'result': result,
                        'success': True
                    })
                    
                    # Add to tool_results for Claude
                    tool_results.append({
                        'type': 'tool_result',
                        'tool_use_id': tool_id,
                        'content': str(result)
                    })
                    
                    print(f"{log_prefix} ✅ Tool executed successfully: {tool_name}")
                    
                except Exception as tool_error:
                    print(f"{log_prefix} ❌ Tool execution failed: {tool_name} - {tool_error}")
                    
                    # Send error to UI
                    queue.put({
                        'type': 'tool_result',
                        'tool_name': tool_name,
                        'result': str(tool_error),
                        'success': False
                    })
                    
                    # Add error to tool_results
                    tool_results.append({
                        'type': 'tool_result',
                        'tool_use_id': tool_id,
                        'content': f"Error: {str(tool_error)}",
                        'is_error': True
                    })
            
            # ✅ Continue conversation with tool results
            print(f"{log_prefix} 🔄 Sending tool results back to AI...")
            
            # CRITICAL FIX (Nov 7 2025): Validate and reorder assistant message content
            # ANTHROPIC API RULES:
            # 1. tool_result blocks can ONLY be in user messages, never assistant
            # 2. If assistant message contains thinking blocks, thinking MUST be first
            # 3. Thinking blocks must have 'thinking' field
            
            # STEP 1: Check if content has thinking blocks
            content = current_response['content']
            has_thinking = any(
                isinstance(b, dict) and b.get('type') in ('thinking', 'redacted_thinking')
                for b in content
            )
            
            # STEP 2: Reorder if needed (thinking must be first)
            if has_thinking:
                first_block = content[0] if content else {}
                if isinstance(first_block, dict) and first_block.get('type') not in ('thinking', 'redacted_thinking'):
                    print(f"{log_prefix} 🔧 Reordering content - moving thinking to first position")
                    
                    # Extract thinking blocks and other blocks
                    thinking_blocks = [b for b in content if isinstance(b, dict) and b.get('type') in ('thinking', 'redacted_thinking')]
                    other_blocks = [b for b in content if isinstance(b, dict) and b.get('type') not in ('thinking', 'redacted_thinking')]
                    
                    # Reorder: thinking first, then others
                    content = thinking_blocks + other_blocks
                    print(f"{log_prefix} ✅ Reordered: {len(thinking_blocks)} thinking + {len(other_blocks)} other blocks")
            
            # STEP 3: Validate and filter blocks
            validated_content = []
            for block in content:
                # RULE 1: tool_result blocks are FORBIDDEN in assistant messages
                if isinstance(block, dict) and block.get('type') == 'tool_result':
                    print(f"{log_prefix} ⚠️ ERROR: Found tool_result in assistant content - REMOVING (violates Anthropic API rules)")
                    continue
                
                # RULE 2: Thinking blocks must have 'thinking' field
                if isinstance(block, dict) and block.get('type') == 'thinking':
                    if 'thinking' not in block or not isinstance(block.get('thinking'), str):
                        print(f"{log_prefix} ⚠️ WARNING: Removing invalid thinking block (missing or invalid 'thinking' field)")
                        continue
                
                validated_content.append(block)
            
            # For THIS turn's conversation with Claude, use validated content
            messages.append({'role': 'assistant', 'content': validated_content})
            messages.append({'role': 'user', 'content': tool_results})
            
            # Get response from AI after processing tool results
            current_response = ai_client.create_message(
                messages=messages,
                provider='anthropic',
                model='claude-sonnet-4-5-20250929',
                max_tokens=16000,
                system=system_prompt,
                tools=tools,
                enable_thinking=True,
                thinking_budget=5000,
                enable_web_search=True,
                enable_web_fetch=True
            )
            
            print(f"{log_prefix} 🔍 Stop reason after tool execution: {current_response.get('stop_reason')}")
            
            # Extract new tool_uses for next iteration (if any)
            tool_uses = []
            if isinstance(current_response, dict) and 'content' in current_response:
                for block in current_response['content']:
                    if block.get('type') == 'tool_use':
                        tool_uses.append(block)
        
        # End of tool execution loop
        if tool_iteration >= max_tool_iterations:
            print(f"{log_prefix} ⚠️ Reached max tool iterations ({max_tool_iterations})")
        
        # Extract and send final text from last response
        if tool_iteration > 0:
            final_text = ''
            if isinstance(current_response, dict) and 'content' in current_response:
                for block in current_response['content']:
                    if block.get('type') == 'text':
                        final_text += block.get('text', '')
            
            if final_text:
                queue.put({'type': 'content_delta', 'text': final_text})
                response_text += final_text
        
        else:
            # No tools used - send response directly
            if response_text:
                queue.put({'type': 'content_delta', 'text': response_text})
        
        # Send completion event
        queue.put({'type': 'complete', 'result': response_text, 'session_id': session_id})
        
        print(f"{log_prefix} Complete")
        
    except Exception as e:
        print(f"{log_prefix} Error: {e}")
        import traceback
        traceback.print_exc()
        queue.put({'type': 'error', 'error': str(e)})
    
    finally:
        try:
            lock.release()
        except:
            pass


def agent_worker(
    message: str,
    session_id: str,
    user_id: int,
    conversation_history: Optional[List[Dict]] = None,
    ai_client=None,
    attachments: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Synchronous agent worker for CLI chat endpoint
    
    Args:
        message: User message
        session_id: Session ID
        user_id: User ID for OAuth credential lookup
        conversation_history: Previous messages
        ai_client: UnifiedAIClient instance
        attachments: List of file attachments (documents/images)
    
    Returns:
        Dict with response and tool_calls
    """
    from tools.registry_v3 import get_registry
    
    try:
        print(f"\n🤖 [agent_worker] Processing message for user_id={user_id}")
        print(f"   Message: {message[:50]}...")
        if attachments:
            print(f"   Attachments: {len(attachments)} files")
            for att in attachments:
                print(f"      - {att.get('name', 'unknown')} ({att.get('media_type', 'unknown')})")
        
        # Get registry and tools
        registry = get_registry()
        tools = registry.get_anthropic_tools()
        print(f"   Tools available: {len(tools)}")
        
        # Build conversation
        if conversation_history is None:
            conversation_history = []
        
        # Progressive loading check
        conversation_length = len(conversation_history)
        if conversation_length == 0:
            # First turn: send only meta-tools
            meta_tool_names = [
                'list_available_platforms',
                'list_platform_tools',
                'get_platform_guide',
                'recommend_tools_for_task',
                'get_workflow_steps'
            ]
            all_tools_dict = {t['name']: t for t in tools}
            tools = [all_tools_dict[name] for name in meta_tool_names if name in all_tools_dict]
            print(f"🔷 [Progressive Loading] First turn: Sending {len(tools)} meta-tools only")
        else:
            print(f"🔷 [Progressive Loading] Turn {conversation_length + 1}: Sending {len(tools)} full tools")
        
        # Add user message with optional attachments
        user_message = {'role': 'user'}
        
        if attachments and len(attachments) > 0:
            # Build content array with text and attachment blocks
            content_blocks = [{'type': 'text', 'text': message}]
            
            for attachment in attachments:
                content_blocks.append({
                    'type': attachment.get('type', 'document'),  # 'document' or 'image'
                    'source': {
                        'type': 'base64',
                        'media_type': attachment.get('media_type'),
                        'data': attachment.get('source', {}).get('data')
                    }
                })
            
            user_message['content'] = content_blocks
            print(f"   📎 Added {len(attachments)} attachments to message")
        else:
            # Simple text message
            user_message['content'] = message
        
        messages = conversation_history + [user_message]
        
        # Get user preferences (nickname, auth platform, communication style)
        from routes.user_preferences_routes import get_user_preferences
        user_prefs = get_user_preferences(user_id) if user_id else None
        nickname = user_prefs.get('nickname', '') if user_prefs else ''
        auth_platform = user_prefs.get('auth_platform', 'auto') if user_prefs else 'auto'
        communication_style = user_prefs.get('communication_style', 'professional') if user_prefs else 'professional'
        detail_level = user_prefs.get('detail_level', 'standard') if user_prefs else 'standard'
        
        if nickname:
            print(f"   👤 User nickname: {nickname}")
        print(f"   🔐 Auth platform: {auth_platform}")
        print(f"   💬 Communication style: {communication_style}")
        print(f"   📊 Detail level: {detail_level}")
        
        # Get user location and temperature context for system prompt
        from core.ip_location import get_location_dict
        try:
            location_dict = get_location_dict()
            
            # Build location context with temperature
            location_str = location_dict.get('location_string', 'Brisbane, Queensland, Australia')
            current_time = location_dict.get('current_time', 'Unknown time')
            day_of_week = location_dict.get('day_of_week', 'Unknown')
            season = location_dict.get('season', 'Unknown')
            temp_c = location_dict.get('temperature_c')
            temp_f = location_dict.get('temperature_f')
            weather = location_dict.get('weather_condition', 'Unknown')
            
            # Build context string
            if temp_c is not None:
                location_context = f"{location_str} | {day_of_week}, {current_time} | {season} | {temp_c}°C ({temp_f}°F), {weather}"
            else:
                location_context = f"{location_str} | {day_of_week}, {current_time} | {season}"
            
            print(f"   📍 Location: {location_str}")
            print(f"   🕐 Time: {day_of_week}, {current_time}")
            if temp_c is not None:
                print(f"   🌡️  Temperature: {temp_c}°C ({temp_f}°F), {weather}")
        except Exception as e:
            print(f"   ⚠️  Location detection failed: {e}, using default")
            location_context = "Brisbane, Queensland, Australia"
        
        # Build system prompt with user preferences + location/temperature context
        user_context_parts = []
        if nickname:
            user_context_parts.append(f"User's Nickname: {nickname}")
        user_context_parts.append(f"Preferred Auth: {auth_platform}")
        user_context_parts.append(f"Communication Style: {communication_style} (adjust your tone accordingly)")
        user_context_parts.append(f"Detail Level: {detail_level} (adjust response length)")
        user_context_parts.append(f"Location & Time: {location_context}")
        
        context_string = "\n- ".join(user_context_parts)
        
        system_prompt = f"""You are a helpful AI assistant with access to tools.

Current Context:
- {context_string}

You can use tools to help the user complete tasks. Always consider the user's preferences, location, time, and weather conditions when providing suggestions or recommendations.

Communication Guidelines:
- If nickname is provided, you may use it in a friendly manner
- Adapt your communication style to match the user's preference ({communication_style})
- Adjust response detail level to match user's preference ({detail_level})
- Consider current weather and temperature when making suggestions"""
        
        # Call AI with tools
        response = ai_client.create_message(
            messages=messages,
            tools=tools,
            max_tokens=4096,
            model='claude-sonnet-4-5-20250929',
            system=system_prompt
        )
        
        response_text = ''
        tool_calls = []
        
        # Process response
        for block in response.get('content', []):
            if block.get('type') == 'text':
                response_text += block.get('text', '')
            elif block.get('type') == 'tool_use':
                tool_name = block.get('name')
                tool_input = block.get('input', {})
                
                print(f"   🔧 Tool call: {tool_name}")
                
                # Execute tool with user_id for credential injection
                try:
                    # Remove 'tool_name' from tool_input if present (passed via additionalProperties)
                    # This prevents "got multiple values for argument 'tool_name'" error
                    if 'tool_name' in tool_input:
                        del tool_input['tool_name']
                    
                    # CRITICAL FIX: Pass credentials to ALL platform tools
                    # Pass _user_id/_injected_credentials for Google Workspace and Microsoft 365 tools
                    # Microsoft tools now use consistent 'microsoft_' prefix
                    if tool_name.startswith(('google_', 'microsoft_')):
                        result = registry.execute_tool(
                            tool_name=tool_name,  # ← FIXED: keyword argument
                            _user_id=user_id,
                            _injected_credentials=True,
                            **tool_input
                        )
                    else:
                        result = registry.execute_tool(
                            tool_name=tool_name,  # ← FIXED: keyword argument
                            **tool_input
                        )
                    
                    tool_calls.append({
                        'name': tool_name,
                        'success': True,
                        'result': result
                    })
                    print(f"   ✅ Tool executed successfully")
                except Exception as e:
                    print(f"   ❌ Tool execution failed: {e}")
                    tool_calls.append({
                        'name': tool_name,
                        'success': False,
                        'error': str(e)
                    })
        
        return {
            'response': response_text,
            'tool_calls': tool_calls,
            'session_id': session_id
        }
        
    except Exception as e:
        print(f"❌ [agent_worker] Error: {e}")
        import traceback
        traceback.print_exc()
        raise