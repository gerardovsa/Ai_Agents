"""
Streaming Agent Worker - Multi-Round Tool Use with SSE
Implements the working pattern from In_House_SQL ToolUseAgent

Key Features:
- Real-time SSE streaming (thinking, text, tool_use, tool_result)
- Recursive continuation after tool execution
- Unlimited rounds of tool use
- Proper conversation history management
- Credential injection for OAuth tools

Architecture:
1. Stream thinking blocks → SSE event: "thinking"
2. Stream text blocks → SSE event: "content_delta"
3. Stream tool_use blocks → SSE event: "tool_use"
4. Execute tools → SSE event: "tool_result"
5. If stop_reason == "tool_use" → RECURSIVE CALL
6. If stop_reason == "end_turn" → SSE event: "complete"
"""

import json
import os
import sys
from typing import Dict, List, Any, Generator, Optional
from datetime import datetime
from anthropic import Anthropic
from queue import Empty

# Add parent directory to import tools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import validation functions from combined worker (Nov 7, 2025)
# CRITICAL FIX: Use unified validation to prevent API errors
from core.combined_agent_worker import (
    validate_conversation_history,
    validate_and_reorder_assistant_content,
    normalize_content_to_blocks
)
from tools.registry_v3 import get_registry
from AI_infrastructure.auth.credential_injector import inject_user_credentials_into_tool


class StreamingAgentWorker:
    """
    Multi-round streaming agent that properly handles tool use
    Pattern copied from In_House_SQL ToolUseAgent
    """
    
    def __init__(self, anthropic_api_key: str = None):
        """
        Initialize streaming agent worker
        
        Args:
            anthropic_api_key: Anthropic API key (optional, will use env var if not provided)
        """
        self.api_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        # Initialize Anthropic client with increased timeout and retries
        self.client = Anthropic(
            api_key=self.api_key,
            timeout=120.0,  # Increased from default 60s to handle SSL handshake delays
            max_retries=3   # Retry up to 3 times on network errors
        )
        self.registry = get_registry()
        self.model = "claude-sonnet-4-5-20250929"
        self.max_tokens = 16000
        self.thinking_budget = 5000
        
        print(f"[Streaming Worker] Initialized with {len(self.registry.tools)} tools (120s timeout, 3 retries)")
    
    def execute_with_streaming(
        self,
        session_id: str,
        user_prompt: str,
        conversation_history: List[Dict],
        tools: List[Dict],
        system_prompt: str,
        user_id: Optional[int] = None,
        max_rounds: int = 20,
        current_round: int = 1
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Execute AI request with multi-round streaming
        
        This is the CORE function that implements the recursive streaming pattern
        
        Args:
            session_id: Session identifier
            user_prompt: User's message (empty string for continuation rounds)
            conversation_history: Full conversation history
            tools: List of tool definitions in Anthropic format
            system_prompt: System prompt for the AI
            user_id: User ID for credential injection
            max_rounds: Maximum recursive rounds (safety limit)
            current_round: Current round number (for logging)
        
        Yields:
            Dict: SSE events with type and data
        """
        log_prefix = f"[Stream Round {current_round}]"
        
        try:
            # Safety check: Prevent infinite loops
            if current_round > max_rounds:
                yield {
                    'type': 'error',
                    'error': f'Maximum rounds ({max_rounds}) exceeded',
                    'session_id': session_id
                }
                return
            
            print(f"{log_prefix} Starting for session {session_id[:8]}...")
            print(f"{log_prefix} History: {len(conversation_history)} messages")
            print(f"{log_prefix} Tools: {len(tools)} available")
            
            # Build messages from conversation history
            messages = self._build_messages(conversation_history, user_prompt, current_round == 1)
            
            if not messages:
                yield {
                    'type': 'error',
                    'error': 'No messages to send',
                    'session_id': session_id
                }
                return
            
            # Calculate approximate token count for logging
            import tiktoken
            try:
                enc = tiktoken.get_encoding("cl100k_base")
                
                # Count system prompt tokens
                system_tokens = len(enc.encode(system_prompt))
                
                # Count message tokens
                message_text = json.dumps(messages)
                message_tokens = len(enc.encode(message_text))
                
                # Count tool definition tokens
                tool_text = json.dumps(tools)
                tool_tokens = len(enc.encode(tool_text))
                
                total_prompt_tokens = system_tokens + message_tokens + tool_tokens
                
                print(f"{log_prefix} Sending {len(messages)} messages to Claude...")
                print(f"{log_prefix} 📊 Token count: ~{total_prompt_tokens:,} tokens")
                print(f"{log_prefix}    ├─ System prompt: ~{system_tokens:,} tokens")
                print(f"{log_prefix}    ├─ Messages: ~{message_tokens:,} tokens")
                print(f"{log_prefix}    └─ Tools ({len(tools)}): ~{tool_tokens:,} tokens")
                
                if total_prompt_tokens > 190000:
                    print(f"{log_prefix} ⚠️  WARNING: Approaching 200k token limit!")
            except Exception as e:
                print(f"{log_prefix} Sending {len(messages)} messages to Claude...")
                print(f"{log_prefix} ⚠️  Could not calculate token count: {e}")
            
            # Track content blocks and stop reason
            all_content_blocks = []
            stop_reason = None
            tool_uses = []
            response_tokens = 0
            
            # Stream response from Claude with beta headers for server tools
            with self.client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=messages,
                tools=tools,
                thinking={
                    'type': 'enabled',
                    'budget_tokens': 5000
                },
                extra_headers={
                    'anthropic-beta': 'web-fetch-2025-09-10'
                }
            ) as stream:
                # Process streaming events
                for event in stream:
                    if not hasattr(event, 'type'):
                        continue
                    
                    event_type = event.type
                    
                    # ============================================================
                    # CONTENT BLOCK START - New thinking/text/tool_use block
                    # ============================================================
                    if event_type == 'content_block_start':
                        if hasattr(event, 'content_block'):
                            block = event.content_block
                            block_type = block.type
                            index = event.index
                            
                            # Track all content blocks
                            all_content_blocks.append(block)
                            
                            # THINKING BLOCK START
                            if block_type == 'thinking':
                                print(f"{log_prefix} [THINKING BLOCK] Started at index {index}")
                                yield {
                                    'type': 'thinking',
                                    'content': '',
                                    'block_index': index,
                                    'delta_type': 'start'
                                }
                            
                            # TEXT BLOCK START
                            elif block_type == 'text':
                                print(f"{log_prefix} [TEXT BLOCK] Started at index {index}")
                                yield {
                                    'type': 'content_delta',
                                    'text': '',
                                    'block_index': index,
                                    'delta_type': 'start'
                                }
                            
                            # TOOL USE BLOCK START
                            elif block_type == 'tool_use':
                                tool_name = block.name
                                tool_id = block.id
                                print(f"{log_prefix} [TOOL USE] {tool_name} (id: {tool_id})")
                                
                                # Track for execution
                                tool_uses.append({
                                    'id': tool_id,
                                    'name': tool_name,
                                    'input': {}  # Will be populated by input_json_delta events
                                })
                                
                                # Yield tool_use event
                                yield {
                                    'type': 'tool_use',
                                    'tool_name': tool_name,
                                    'tool_id': tool_id,
                                    'tool_input': {},
                                    'block_index': index
                                }
                            
                            # SERVER TOOL USE BLOCK START (web_search, web_fetch)
                            elif block_type == 'server_tool_use':
                                tool_name = block.name
                                tool_id = block.id
                                print(f"{log_prefix} [SERVER TOOL USE] {tool_name} (id: {tool_id})")
                                
                                # Yield server_tool_use event for UI rendering
                                yield {
                                    'type': 'server_tool_use',
                                    'name': tool_name,
                                    'id': tool_id,
                                    'input': getattr(block, 'input', {}),
                                    'block_index': index
                                }
                            
                            # WEB SEARCH RESULT BLOCK
                            elif block_type == 'web_search_tool_result':
                                tool_id = block.tool_use_id
                                print(f"{log_prefix} [WEB SEARCH RESULT] (tool_id: {tool_id})")
                                
                                # Yield web_search_tool_result event for UI rendering
                                yield {
                                    'type': 'web_search_tool_result',
                                    'tool_use_id': tool_id,
                                    'content': getattr(block, 'content', []),
                                    'block_index': index
                                }
                            
                            # WEB FETCH RESULT BLOCK
                            elif block_type == 'web_fetch_tool_result':
                                tool_id = block.tool_use_id
                                print(f"{log_prefix} [WEB FETCH RESULT] (tool_id: {tool_id})")
                                
                                # Yield web_fetch_tool_result event for UI rendering
                                yield {
                                    'type': 'web_fetch_tool_result',
                                    'tool_use_id': tool_id,
                                    'content': getattr(block, 'content', {}),
                                    'block_index': index
                                }
                    
                    # ============================================================
                    # CONTENT BLOCK DELTA - Incremental updates
                    # ============================================================
                    elif event_type == 'content_block_delta':
                        if hasattr(event, 'delta'):
                            delta = event.delta
                            delta_type = delta.type
                            index = event.index
                            
                            # THINKING DELTA
                            if delta_type == 'thinking_delta':
                                thinking_text = delta.thinking
                                print(f"{log_prefix} [THINKING DELTA] +{len(thinking_text)} chars")
                                yield {
                                    'type': 'thinking',
                                    'content': thinking_text,
                                    'block_index': index,
                                    'delta_type': 'delta'
                                }
                            
                            # TEXT DELTA
                            elif delta_type == 'text_delta':
                                text_chunk = delta.text
                                print(f"{log_prefix} [TEXT DELTA] +{len(text_chunk)} chars")
                                yield {
                                    'type': 'content_delta',
                                    'text': text_chunk,
                                    'block_index': index,
                                    'delta_type': 'delta'
                                }
                            
                            # TOOL INPUT JSON DELTA
                            elif delta_type == 'input_json_delta':
                                json_chunk = delta.partial_json
                                # Accumulate JSON input for tool execution
                                if tool_uses and index < len(tool_uses):
                                    # Note: We'll parse the complete JSON at block_stop
                                    pass
                    
                    # ============================================================
                    # CONTENT BLOCK STOP - Block completed
                    # ============================================================
                    elif event_type == 'content_block_stop':
                        index = event.index
                        print(f"{log_prefix} [BLOCK STOP] Index {index}")
                
                # Get final message to capture stop_reason and complete content
                final_message = stream.get_final_message()
                
                if final_message:
                    stop_reason = final_message.stop_reason
                    all_content_blocks = final_message.content
                    
                    # Parse tool inputs from complete content blocks
                    tool_uses = []
                    for block in all_content_blocks:
                        if hasattr(block, 'type') and block.type == 'tool_use':
                            tool_uses.append({
                                'id': block.id,
                                'name': block.name,
                                'input': block.input
                            })
                    
                    print(f"{log_prefix} Stream complete - stop_reason: {stop_reason}")
                    print(f"{log_prefix} Content blocks: {len(all_content_blocks)}")
                    print(f"{log_prefix} Tool uses: {len(tool_uses)}")
                    
                    # Send complete tool inputs to frontend (now that JSON parsing is done)
                    for tool_use in tool_uses:
                        print(f"{log_prefix} [TOOL INPUT COMPLETE] {tool_use['name']} with {len(str(tool_use['input']))} bytes")
                        yield {
                            'type': 'tool_input_complete',
                            'tool_name': tool_use['name'],
                            'tool_id': tool_use['id'],
                            'tool_input': tool_use['input']
                        }
            
            # ============================================================
            # ADD ASSISTANT RESPONSE TO CONVERSATION HISTORY
            # ============================================================
            # Convert content blocks to serializable format
            serialized_content = self._serialize_content_blocks(all_content_blocks)
            
            # CRITICAL FIX (Nov 6 2025): KEEP thinking blocks in conversation history!
            # Anthropic API REQUIRES thinking blocks to be first in assistant messages
            # If we filter them out, Round 2+ fails with:
            #   "messages.X.content.0.type: Expected `thinking` but found `text`"
            # 
            # G_Folder solution: Keep ALL blocks (thinking, text, tool_use) in history
            # - Thinking blocks needed for API continuity
            # - Frontend already filters them from display
            # - Database stores them for session resume
            
            # CRITICAL: Always add assistant response to history with ALL blocks
            # Without this, tool_result blocks have no corresponding tool_use block
            conversation_history.append({
                'role': 'assistant',
                'content': serialized_content  # ✅ KEEP ALL BLOCKS (thinking, text, tool_use)
            })
            print(f"{log_prefix} Added assistant response to history (ALL blocks including thinking)")
            
            # ============================================================
            # EXECUTE TOOLS IF PRESENT
            # ============================================================
            if tool_uses and stop_reason == 'tool_use':
                print(f"{log_prefix} Executing {len(tool_uses)} tool(s)...")
                
                # Build tool_results array
                tool_results = []
                
                for tool_use in tool_uses:
                    tool_name = tool_use['name']
                    tool_input = tool_use['input'].copy()  # Make a copy to avoid mutating original
                    tool_id = tool_use['id']
                    
                    # DEBUG: Log EVERYTHING to both console and file
                    import datetime
                    debug_msg = f"\n[{datetime.datetime.now()}] ===== TOOL EXECUTION DEBUG =====\n"
                    debug_msg += f"tool_name: {tool_name}\n"
                    debug_msg += f"tool_input: {tool_input}\n"
                    debug_msg += f"tool_id: {tool_id}\n"
                    debug_msg += f"================================\n"
                    
                    # Write to file
                    with open('C:\\Users\\gpoli\\GIT\\AI_agents\\streaming_debug.log', 'a', encoding='utf-8') as f:
                        f.write(debug_msg)
                    
                    # Also print to console
                    print(f"{log_prefix} ===== TOOL EXECUTION DEBUG =====")
                    print(f"{log_prefix} tool_name: {tool_name}")
                    print(f"{log_prefix} tool_input: {tool_input}")
                    print(f"{log_prefix} tool_id: {tool_id}")
                    print(f"{log_prefix} ================================")
                    
                    print(f"{log_prefix} Executing: {tool_name}")
                    
                    try:
                        # CRITICAL FIX: Meta-tools (get_tool_schema, execute_tool) have a special case:
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
                                # Fallback for other meta-tools
                                result = self.registry.execute_tool(tool_name=tool_name, **tool_input)
                        else:
                            # For regular tools: Pass tool_name separately
                            # CRITICAL FIX: Pass credentials to ALL platform tools
                            # Pass _user_id/_injected_credentials for Google Workspace and Microsoft 365 tools
                            if tool_name.startswith(('google_', 'microsoft_')):
                                result = self.registry.execute_tool(
                                    tool_name=tool_name,
                                    _user_id=user_id,
                                    _injected_credentials=True,
                                    **tool_input
                                )
                            else:
                                result = self.registry.execute_tool(
                                    tool_name=tool_name,
                                    **tool_input
                                )
                        
                        # Convert result to string if needed
                        if not isinstance(result, str):
                            result_str = json.dumps(result, indent=2)
                        else:
                            result_str = result
                        
                        print(f"{log_prefix} Tool result: {result_str[:200]}...")
                        
                        # Build tool_result content block
                        tool_results.append({
                            'type': 'tool_result',
                            'tool_use_id': tool_id,
                            'content': result_str
                        })
                        
                        # Yield tool_result event
                        yield {
                            'type': 'tool_result',
                            'tool_name': tool_name,
                            'tool_id': tool_id,
                            'result': result_str,
                            'success': True
                        }
                    
                    except Exception as e:
                        error_msg = f"Tool execution failed: {str(e)}"
                        print(f"{log_prefix} ERROR: {error_msg}")
                        
                        tool_results.append({
                            'type': 'tool_result',
                            'tool_use_id': tool_id,
                            'content': error_msg,
                            'is_error': True
                        })
                        
                        # Yield tool_result error event
                        yield {
                            'type': 'tool_result',
                            'tool_name': tool_name,
                            'tool_id': tool_id,
                            'result': error_msg,
                            'success': False,
                            'error': error_msg
                        }
                
                # ============================================================
                # ADD TOOL RESULTS TO CONVERSATION HISTORY
                # ============================================================
                # Tool results go as "user" role in Anthropic API
                conversation_history.append({
                    'role': 'user',
                    'content': tool_results
                })
                print(f"{log_prefix} Added {len(tool_results)} tool result(s) to history")
                
                # ============================================================
                # RECURSIVE CALL - Continue conversation
                # ============================================================
                print(f"{log_prefix} Recursive call to round {current_round + 1}...")
                
                # Recursively call this function to continue the conversation
                yield from self.execute_with_streaming(
                    session_id=session_id,
                    user_prompt='',  # Empty prompt for continuation
                    conversation_history=conversation_history,
                    tools=tools,
                    system_prompt=system_prompt,
                    user_id=user_id,
                    max_rounds=max_rounds,
                    current_round=current_round + 1
                )
            
            else:
                # ============================================================
                # FINAL RESPONSE - No more tools, conversation complete
                # ============================================================
                print(f"{log_prefix} Conversation complete (stop_reason: {stop_reason})")
                
                # Extract final text response and count tokens
                final_text = ''
                for block in all_content_blocks:
                    if hasattr(block, 'type') and block.type == 'text':
                        final_text += block.text
                
                # Calculate response token count
                try:
                    response_tokens = len(enc.encode(final_text))
                    print(f"{log_prefix} 📊 Response tokens: ~{response_tokens:,} tokens")
                    print(f"{log_prefix} 📊 Total round tokens: ~{total_prompt_tokens + response_tokens:,} tokens")
                except:
                    pass
                
                # Yield complete event
                yield {
                    'type': 'complete',
                    'session_id': session_id,
                    'full_response': final_text,
                    'stop_reason': stop_reason,
                    'total_rounds': current_round
                }
        
        except Exception as e:
            print(f"{log_prefix} ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            
            yield {
                'type': 'error',
                'error': str(e),
                'session_id': session_id,
                'round': current_round
            }
    
    def _build_messages(
        self,
        conversation_history: List[Dict],
        user_prompt: str,
        is_first_round: bool
    ) -> List[Dict]:
        """
        Build messages array for Claude API
        
        Args:
            conversation_history: Full conversation history
            user_prompt: Current user prompt (empty for continuation)
            is_first_round: Whether this is the first round
        
        Returns:
            List of messages in Anthropic format
        """
        messages = []
        
        print(f"[StreamingWorker] 🔍 Using unified validation for {len(conversation_history)} messages...")
        
        # CRITICAL FIX (Nov 7, 2025): Use unified validation from combined_agent_worker
        # This fixes all 7 critical issues including thinking block ordering
        validated_history = validate_conversation_history(conversation_history)
        
        print(f"[StreamingWorker] ✅ Validation complete: {len(validated_history)} valid messages")
        
        # Use validated messages directly (already normalized and validated)
        for idx, msg in enumerate(validated_history):
            # Skip old manual validation - already done by validate_conversation_history()
            message = {
                'role': msg.get('role'),
                'content': msg.get('content')
            }
            
            # Debug logging only (validation already done)
            if idx >= 0 and idx <= 5:  # Log first 6 messages
                print(f"[StreamingWorker] 📝 Message {idx}:")
                print(f"[StreamingWorker]    Role: {message['role']}")
                if isinstance(message.get('content'), list):
                    print(f"[StreamingWorker]    Content blocks: {len(message['content'])}")
                    for block_idx, block in enumerate(message['content']):
                        if isinstance(block, dict):
                            print(f"[StreamingWorker]      Block {block_idx}: type={block.get('type')}")
                elif isinstance(message.get('content'), str):
                    print(f"[StreamingWorker]    Content: string ({len(message['content'])} chars)")
            
            # Messages are already validated - just add them
            messages.append(message)
        
        print(f"[StreamingWorker] ✅ Built {len(messages)} messages for API")
        
        # Add new user prompt if first round
        if is_first_round and user_prompt:
            messages.append({
                'role': 'user',
                'content': user_prompt
            })
            print(f"[StreamingWorker] ✅ Added new user prompt")
        
        return messages
    
    # OLD VALIDATION CODE REMOVED - Now using unified validation from combined_agent_worker
    # All the manual parsing and validation below is NO LONGER NEEDED
    
    def _build_messages_OLD_BACKUP(
        self,
        conversation_history: List[Dict],
        user_prompt: str,
        is_first_round: bool
    ) -> List[Dict]:
        """
        OLD VERSION - BACKUP ONLY
        This method is kept for reference but should NOT be used
        Use _build_messages() instead which calls unified validation
        """
        messages = []
        
        for idx, msg in enumerate(conversation_history):
            message = {
                'role': msg.get('role'),
                'content': msg.get('content')
            }
            
            # OLD MANUAL VALIDATION CODE (replaced by unified validation)
            if isinstance(message.get('content'), str):
                import json
                parsed_blocks = None
                try:
                    parsed = json.loads(message['content'])
                    parsed_blocks = parsed if isinstance(parsed, list) else None
                    if parsed_blocks is None and isinstance(parsed, dict):
                        parsed_blocks = [parsed]
                except (json.JSONDecodeError, TypeError):
                    parsed_blocks = None
                
                # Secondary parse attempt: handle Python-style literals (single quotes)
                if parsed_blocks is None:
                    try:
                        import ast
                        parsed_literal = ast.literal_eval(message['content'])
                        if isinstance(parsed_literal, list):
                            parsed_blocks = parsed_literal
                        elif isinstance(parsed_literal, dict):
                            parsed_blocks = [parsed_literal]
                    except (ValueError, SyntaxError):
                        parsed_blocks = None
                
                if parsed_blocks is not None:
                    # Ensure every block is a dict with a type
                    normalized_blocks = []
                    for block in parsed_blocks:
                        if isinstance(block, dict) and block.get('type'):
                            normalized_blocks.append(block)
                        elif isinstance(block, str):
                            normalized_blocks.append({'type': 'text', 'text': block})
                    if normalized_blocks:
                        print(f"[StreamingWorker] 🔧 Parsed string content to {len(normalized_blocks)} blocks for message {idx}")
                        message['content'] = normalized_blocks
                    else:
                        print(f"[StreamingWorker] ⚠️ Parsed string content but no valid blocks for message {idx}")
                        if message['role'] == 'assistant':
                            message['content'] = [{'type': 'text', 'text': message['content']}]
                else:
                    # Not parsable - wrap plain string in text block for assistant messages
                    # Anthropic API requires assistant messages to use blocks, not plain strings
                    if message['role'] == 'assistant':
                        print(f"[StreamingWorker] 🔧 Converting plain string to text block for assistant message {idx}")
                        message['content'] = [{'type': 'text', 'text': message['content']}]
                    # User messages can stay as strings
            
            # DEBUG: Log ALL messages to diagnose the issue
            if idx >= 0 and idx <= 15:  # Log first 16 messages
                print(f"[StreamingWorker] 📝 Message {idx}:")
                print(f"[StreamingWorker]    Role: {message['role']}")
                if isinstance(message.get('content'), list):
                    print(f"[StreamingWorker]    Content blocks: {len(message['content'])}")
                    for block_idx, block in enumerate(message['content']):
                        if isinstance(block, dict):
                            print(f"[StreamingWorker]      Block {block_idx}: type={block.get('type')}")
                elif isinstance(message.get('content'), str):
                    print(f"[StreamingWorker]    Content: string ({len(message['content'])} chars)")
                else:
                    print(f"[StreamingWorker]    Content: {type(message.get('content'))}")
            
            # CRITICAL FIX: Reorder assistant message content blocks
            # Anthropic API requirement: If thinking blocks exist, first block MUST be thinking
            # BUGFIX: Run validation for ALL assistant messages, not just those with thinking
            if message['role'] == 'assistant' and isinstance(message.get('content'), list) and len(message['content']) > 0:
                # Detect thinking blocks
                has_thinking = any(
                    block.get('type') in ('thinking', 'redacted_thinking')
                    for block in message['content'] 
                    if isinstance(block, dict)
                )
                
                # Debug logging - show ALL messages
                first_block = message['content'][0]
                print(f"[StreamingWorker] Message {idx} ({message['role']}): {len(message['content'])} blocks")
                print(f"[StreamingWorker]   First block type: {first_block.get('type') if isinstance(first_block, dict) else type(first_block)}")
                print(f"[StreamingWorker]   Has thinking blocks: {'YES' if has_thinking else 'NO'}")
                
                # STEP 1: Reorder if thinking blocks exist and first block is not thinking
                if has_thinking:
                    first_block = message['content'][0]
                    if isinstance(first_block, dict) and first_block.get('type') not in ('thinking', 'redacted_thinking'):
                        print(f"[StreamingWorker] 🔧 Reordering message {idx} - moving thinking to first position")
                        
                        # Extract thinking blocks and other blocks
                        thinking_blocks = [
                            b for b in message['content'] 
                            if isinstance(b, dict) and b.get('type') in ('thinking', 'redacted_thinking')
                        ]
                        other_blocks = [
                            b for b in message['content'] 
                            if isinstance(b, dict) and b.get('type') not in ('thinking', 'redacted_thinking')
                        ]
                        
                        # Reorder: thinking first, then others
                        message['content'] = thinking_blocks + other_blocks
                        print(f"[StreamingWorker] ✅ Reordered: {len(thinking_blocks)} thinking + {len(other_blocks)} other blocks")
                        print(f"[StreamingWorker]   New first block: {message['content'][0].get('type')}")
                
                # STEP 2: ALWAYS validate and remove invalid blocks (regardless of thinking blocks)
                # ANTHROPIC API RULE: tool_result blocks can ONLY be in user messages, never assistant
                valid_content = []
                for block in message['content']:
                    # RULE 1: tool_result blocks are FORBIDDEN in assistant messages
                    if isinstance(block, dict) and block.get('type') == 'tool_result':
                        print(f"[StreamingWorker] ⚠️ ERROR: Found tool_result in assistant message {idx} - REMOVING (violates Anthropic API rules)")
                        continue
                    
                    # RULE 2: Thinking blocks must have 'thinking' field
                    if isinstance(block, dict) and block.get('type') == 'thinking':
                        if 'thinking' not in block or not isinstance(block.get('thinking'), str):
                            print(f"[StreamingWorker] ⚠️ WARNING: Removing invalid thinking block from message {idx} (missing or invalid 'thinking' field)")
                            continue
                    
                    valid_content.append(block)
                message['content'] = valid_content
                
                # Skip if all blocks were removed
                if not message['content']:
                    print(f"[StreamingWorker] ⚠️ Skipping message {idx} - all blocks were invalid")
                    continue
            
            # Validate user messages (check for orphaned tool_results)
            elif message['role'] == 'user' and isinstance(message.get('content'), list):
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
                    for block in message['content']:
                        if isinstance(block, dict) and block.get('type') == 'tool_result':
                            print(f"[StreamingWorker] ⚠️ Removing orphaned tool_result from message {idx}")
                            continue
                        validated_user_content.append(block)
                    message['content'] = validated_user_content
                    
                    # Skip if all blocks removed
                    if not message['content']:
                        print(f"[StreamingWorker] ⚠️ Skipping message {idx} - all blocks were orphaned")
                        continue
            
            messages.append(message)
        
        print(f"[StreamingWorker] ✅ Validated history: {len(messages)} valid messages")
        
        # Add new user prompt if provided (first round only)
        if user_prompt and is_first_round:
            messages.append({
                'role': 'user',
                'content': user_prompt
            })
        
        # CRITICAL: Preserve attachment content blocks in conversation history
        # User messages may contain arrays of content blocks (text + document/image blocks)
        # This ensures attachments sent via /chat endpoint are preserved in streaming
        for msg in messages:
            if msg['role'] == 'user' and isinstance(msg.get('content'), list):
                # Already has content blocks - attachments preserved ✅
                print(f"[StreamingWorker] User message has {len(msg['content'])} content blocks (includes attachments)")
        
        return messages
    
    def _serialize_content_blocks(self, content_blocks: Any) -> Any:
        """
        Serialize Anthropic content blocks to storable format
        
        CRITICAL: When thinking blocks exist, they MUST be first
        This is required by Anthropic API for extended thinking
        
        Args:
            content_blocks: Anthropic ContentBlock objects or list
        
        Returns:
            Serialized content (string or list of dicts)
        """
        # Handle simple string
        if isinstance(content_blocks, str):
            return content_blocks
        
        # Handle list of blocks
        if isinstance(content_blocks, list):
            # If already serialized (dicts), check if reordering is needed
            if content_blocks and isinstance(content_blocks[0], dict):
                serialized = content_blocks
                # Skip to reordering check below
            else:
                # Serialize Anthropic ContentBlock objects
                serialized = []
                for block in content_blocks:
                    if hasattr(block, 'type'):
                        block_type = block.type
                        
                        if block_type == 'thinking':
                            serialized.append({
                                'type': 'thinking',
                                'thinking': block.thinking,
                                'signature': block.signature  # Required by Claude API for extended thinking
                            })
                        
                        elif block_type == 'text':
                            serialized.append({
                                'type': 'text',
                                'text': block.text
                            })
                        
                        elif block_type == 'tool_use':
                            serialized.append({
                                'type': 'tool_use',
                                'id': block.id,
                                'name': block.name,
                                'input': block.input
                            })
                        
                        # SERVER TOOL BLOCKS (web_search, web_fetch)
                        elif block_type == 'server_tool_use':
                            serialized.append({
                                'type': 'server_tool_use',
                                'id': block.id,
                                'name': block.name,
                                'input': getattr(block, 'input', {})
                            })
                        
                        elif block_type == 'web_search_tool_result':
                            serialized.append({
                                'type': 'web_search_tool_result',
                                'tool_use_id': block.tool_use_id,
                                'content': getattr(block, 'content', [])
                            })
                        
                        elif block_type == 'web_fetch_tool_result':
                            serialized.append({
                                'type': 'web_fetch_tool_result',
                                'tool_use_id': block.tool_use_id,
                                'content': getattr(block, 'content', {})
                            })
            
            # CRITICAL FIX: Reorder blocks - thinking MUST be first
            # Anthropic API requirement: "If an assistant message contains any thinking blocks,
            # the first block must be `thinking` or `redacted_thinking`"
            if serialized:
                has_thinking = any(b.get('type') == 'thinking' for b in serialized)
                
                if has_thinking and serialized[0].get('type') != 'thinking':
                    print(f"[StreamingWorker] Reordering serialized blocks - moving thinking to first position")
                    
                    # Separate thinking blocks from other blocks
                    thinking_blocks = [b for b in serialized if b.get('type') == 'thinking']
                    other_blocks = [b for b in serialized if b.get('type') != 'thinking']
                    
                    # Reorder: thinking first, then others
                    serialized = thinking_blocks + other_blocks
                    print(f"[StreamingWorker] Reordered: {len(thinking_blocks)} thinking + {len(other_blocks)} other blocks")
                
                # CRITICAL FIX: Validate thinking blocks have required fields
                # Anthropic API requires thinking blocks to have 'thinking' field
                for idx, block in enumerate(serialized):
                    if isinstance(block, dict) and block.get('type') == 'thinking':
                        if 'thinking' not in block:
                            print(f"[StreamingWorker] ⚠️ WARNING: Thinking block at index {idx} missing 'thinking' field - removing block")
                            # Remove invalid thinking block to prevent API error
                            serialized = [b for i, b in enumerate(serialized) if i != idx]
                        elif not isinstance(block.get('thinking'), str):
                            print(f"[StreamingWorker] ⚠️ WARNING: Thinking block at index {idx} has invalid 'thinking' field type: {type(block.get('thinking'))} - removing block")
                            serialized = [b for i, b in enumerate(serialized) if i != idx]
            
            return serialized
        
        # Fallback
        return str(content_blocks)


# ============================================================
# HELPER FUNCTIONS FOR FLASK ROUTES
# ============================================================

def create_streaming_worker() -> StreamingAgentWorker:
    """
    Factory function to create a streaming worker
    
    Returns:
        StreamingAgentWorker instance
    """
    return StreamingAgentWorker()


def execute_streaming_request(
    session_id: str,
    user_prompt: str,
    conversation_history: List[Dict],
    system_prompt: str,
    tools: List[Dict],
    user_id: Optional[int] = None
) -> Generator[Dict[str, Any], None, None]:
    """
    Execute streaming request (convenience wrapper)
    
    Args:
        session_id: Session identifier
        user_prompt: User's message
        conversation_history: Full conversation history
        system_prompt: System prompt for AI
        tools: List of tool definitions
        user_id: User ID for credential injection
    
    Yields:
        Dict: SSE events
    """
    worker = create_streaming_worker()
    
    yield from worker.execute_with_streaming(
        session_id=session_id,
        user_prompt=user_prompt,
        conversation_history=conversation_history,
        tools=tools,
        system_prompt=system_prompt,
        user_id=user_id
    )
