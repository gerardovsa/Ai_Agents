"""
Agent Worker
Background thread that executes ToolUseAgent with SSE streaming

Replaces OLD Flask's run_agent_worker() with cleaner implementation
"""

import json
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from queue import Queue
import threading

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
                max_turns=10,
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
        
        # ✅ FIX: Load tools from registry with PROGRESSIVE LOADING
        from tools import registry_v3
        registry = registry_v3.get_registry()
        
        # ✅ PROGRESSIVE LOADING: Send only meta-tools on first turn
        conversation_length = len(conversation_history or [])
        
        if conversation_length == 0:
            # First turn: Send ONLY meta-tools for discovery
            meta_tool_names = [
                'list_available_platforms',
                'list_platform_tools',
                'get_platform_guide',
                'recommend_tools_for_task',
                'get_workflow_steps'
            ]
            
            # Get only meta-tools from full registry
            all_tools_dict = {t['name']: t for t in registry.get_anthropic_tools()}
            tools = [all_tools_dict[name] for name in meta_tool_names if name in all_tools_dict]
            
            print(f"{log_prefix} 🔷 [Progressive Loading] First turn: Sending {len(tools)} meta-tools only")
            print(f"{log_prefix} 🔷 Meta-tools: {[t['name'] for t in tools]}")
        else:
            # Subsequent turns: Send full tool list
            tools = registry.get_anthropic_tools()
            print(f"{log_prefix} 🔷 [Progressive Loading] Turn {conversation_length + 1}: Sending {len(tools)} full tools")
        
        # ✅ Get system prompt with tool usage instructions
        system_prompt = ai_client.get_system_prompt('data_agent_chat')
        print(f"{log_prefix} System prompt loaded ({len(system_prompt)} chars)")
        
        # Build messages with history
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
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
                
                # Send tool_use event to UI
                queue.put({
                    'type': 'tool_use',
                    'tool_name': tool_name,
                    'tool_input': tool_input
                })
                
                try:
                    # Remove 'tool_name' from tool_input if present (to prevent duplicate argument)
                    tool_input_copy = {k: v for k, v in tool_input.items() if k != 'tool_name'}
                    
                    # Execute tool using registry
                    # Only pass _user_id/_injected_credentials to Google Workspace tools
                    if tool_name.startswith('google_'):
                        result = registry.execute_tool(
                            tool_name,
                            _user_id=user_id,
                            _injected_credentials=True,
                            **tool_input_copy
                        )
                    else:
                        result = registry.execute_tool(
                            tool_name,
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
            
            # ⚠️ CRITICAL: When Extended Thinking is enabled, assistant messages MUST start with thinking block
            # Keep ALL blocks including thinking (Anthropic requires them for Extended Thinking)
            messages.append({'role': 'assistant', 'content': current_response['content']})
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
    ai_client=None
) -> Dict[str, Any]:
    """
    Synchronous agent worker for CLI chat endpoint
    
    Args:
        message: User message
        session_id: Session ID
        user_id: User ID for OAuth credential lookup
        conversation_history: Previous messages
        ai_client: UnifiedAIClient instance
    
    Returns:
        Dict with response and tool_calls
    """
    from tools.registry_v3 import get_registry
    
    try:
        print(f"\n🤖 [agent_worker] Processing message for user_id={user_id}")
        print(f"   Message: {message[:50]}...")
        
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
        
        # Add user message
        messages = conversation_history + [{
            'role': 'user',
            'content': message
        }]
        
        # Call AI with tools
        response = ai_client.create_message(
            messages=messages,
            tools=tools,
            max_tokens=4096,
            model='claude-sonnet-4-5-20250929'
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
                
                # Execute tool with user_id for credential injection (Google tools only)
                try:
                    # Remove 'tool_name' from tool_input if present (passed via additionalProperties)
                    # This prevents "got multiple values for argument 'tool_name'" error
                    if 'tool_name' in tool_input:
                        del tool_input['tool_name']
                    
                    # Inject OAuth parameters for Google Workspace and Microsoft 365 tools
                    if (tool_name.startswith('google_') or 
                        tool_name.startswith(('outlook_', 'word_', 'excel_', 'teams_', 'onedrive_', 'calendar_', 'todo_', 'forms_', 'sharepoint_'))):
                        tool_input['_user_id'] = user_id
                        tool_input['_injected_credentials'] = True
                    
                    # FIXED: Use keyword argument to avoid parameter conflict
                    result = registry.execute_tool(tool_name=tool_name, **tool_input)
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
