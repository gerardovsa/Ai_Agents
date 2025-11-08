"""
Combined Agent Worker - Unified and Fixed
Combines agent_worker.py + streaming_agent_worker.py with all critical fixes

CRITICAL FIXES APPLIED (Nov 7, 2025):
1. ✅ Thinking block ordering (must be first if present)
2. ✅ tool_result blocks removed from assistant messages
3. ✅ Orphaned tool_result detection (backwards search through ALL messages)
4. ✅ String content converted to blocks (both user and assistant)
5. ✅ Signature field validation for thinking blocks
6. ✅ Duplicate consecutive role detection and merging
7. ✅ Block field validation (text.text, tool_use.id, etc.)

UNIFIED EXPORTS:
- run_agent_worker() - Background worker with file support
- run_simple_agent_worker() - Synchronous text-only worker
- agent_worker() - CLI chat worker
- execute_streaming_request() - Multi-round streaming

USAGE:
    from core.combined_agent_worker import run_agent_worker, agent_worker
"""

import json
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Generator
from queue import Queue
import threading


# ============================================================
# SHARED VALIDATION FUNCTIONS (Used by all workers)
# ============================================================

def validate_and_reorder_assistant_content(content: List[Dict]) -> List[Dict]:
    """
    Comprehensive validation and reordering for assistant message content
    
    CRITICAL ANTHROPIC API RULES:
    1. If thinking blocks exist, first block MUST be 'thinking' or 'redacted_thinking'
    2. tool_result blocks are FORBIDDEN in assistant messages (only in user messages)
    3. Thinking blocks must have 'thinking' field (string) and 'signature' field
    4. Text blocks must have 'text' field (string)
    5. tool_use blocks must have 'id', 'name', 'input' fields
    
    Args:
        content: List of content blocks from assistant message
    
    Returns:
        Validated and reordered content (thinking first, invalid blocks removed)
    """
    if not isinstance(content, list) or not content:
        return content
    
    # STEP 1: Validate and filter blocks
    validated_blocks = []
    for block in content:
        if not isinstance(block, dict):
            print(f"[Combined Worker] ⚠️ Skipping non-dict block")
            continue
        
        block_type = block.get('type')
        
        # RULE 1: tool_result blocks are FORBIDDEN in assistant messages
        if block_type == 'tool_result':
            print(f"[Combined Worker] ⚠️ Removing tool_result from assistant message (API violation)")
            continue
        
        # RULE 2: Validate thinking blocks
        if block_type in ('thinking', 'redacted_thinking'):
            if 'thinking' not in block or not isinstance(block.get('thinking'), str):
                print(f"[Combined Worker] ⚠️ Removing invalid thinking block (missing 'thinking' field)")
                continue
            # RULE 2a: Ensure signature field exists (extended thinking requirement)
            if 'signature' not in block:
                print(f"[Combined Worker] ⚠️ Adding missing 'signature' field to thinking block")
                block['signature'] = ''
        
        # RULE 3: Validate text blocks
        elif block_type == 'text':
            if 'text' not in block or not isinstance(block.get('text'), str):
                print(f"[Combined Worker] ⚠️ Removing invalid text block (missing 'text' field)")
                continue
        
        # RULE 4: Validate tool_use blocks
        elif block_type == 'tool_use':
            if not all(k in block for k in ['id', 'name', 'input']):
                print(f"[Combined Worker] ⚠️ Removing invalid tool_use block (missing required fields)")
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
    
    print(f"[Combined Worker] 🔧 Reordered: {len(thinking_blocks)} thinking + {len(other_blocks)} other blocks")
    return thinking_blocks + other_blocks


def validate_user_content(content: List[Dict], messages: List[Dict]) -> List[Dict]:
    """
    Validate user message content (check for orphaned tool_results)
    
    Args:
        content: List of content blocks from user message
        messages: Previous validated messages (to check for tool_use)
    
    Returns:
        Validated content with orphaned tool_results removed
    """
    if not isinstance(content, list) or not content:
        return content
    
    # Look backwards through ALL previous messages to find last assistant with tool_use
    has_tool_use_before = False
    for prev_msg in reversed(messages):
        if prev_msg.get('role') == 'assistant':
            prev_content = prev_msg.get('content', [])
            has_tool_use_before = any(
                b.get('type') == 'tool_use' for b in prev_content if isinstance(b, dict)
            )
            break  # Stop at first assistant message found
        elif prev_msg.get('role') == 'user':
            # Another user message before assistant - definitely orphaned
            break
    
    # Validate and clean blocks
    validated_blocks = []
    for block in content:
        if not isinstance(block, dict):
            print(f"[Combined Worker] ⚠️ Skipping non-dict block in user message")
            continue
        
        # Remove orphaned tool_result blocks
        if block.get('type') == 'tool_result' and not has_tool_use_before:
            print(f"[Combined Worker] ⚠️ Removing orphaned tool_result from user message")
            continue
        
        validated_blocks.append(block)
    
    return validated_blocks


def normalize_content_to_blocks(content: Any, role: str) -> List[Dict]:
    """
    Normalize content to list of blocks format
    
    Handles:
    - Plain strings → [{"type": "text", "text": content}]
    - JSON strings → Parse and validate
    - Already blocks → Return as-is
    
    Args:
        content: Content in any format
        role: Message role (for logging)
    
    Returns:
        List of content blocks
    """
    # Already a list of blocks
    if isinstance(content, list):
        return content
    
    # Plain string
    if isinstance(content, str):
        # Try parsing as JSON first
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list):
                print(f"[Combined Worker] 🔧 Parsed JSON string to {len(parsed)} blocks ({role})")
                return parsed
            else:
                # JSON but not a list - wrap in text block
                print(f"[Combined Worker] 🔧 Converting JSON value to text block ({role})")
                return [{'type': 'text', 'text': str(parsed)}]
        except (json.JSONDecodeError, TypeError):
            # Not JSON - wrap in text block
            print(f"[Combined Worker] 🔧 Converting plain string to text block ({role})")
            return [{'type': 'text', 'text': content}]
    
    # Unknown format - convert to text block
    print(f"[Combined Worker] ⚠️ Unknown content type ({type(content)}) - converting to text ({role})")
    return [{'type': 'text', 'text': str(content)}]


def validate_conversation_history(conversation_history: List[Dict]) -> List[Dict]:
    """
    Comprehensive validation of conversation history
    
    Fixes ALL 7 critical issues:
    1. Thinking block ordering
    2. tool_result in assistant messages
    3. Orphaned tool_results
    4. String to block conversion
    5. Signature field validation
    6. Duplicate consecutive roles
    7. Block field validation
    
    Args:
        conversation_history: Raw conversation history
    
    Returns:
        Validated and fixed conversation history
    """
    messages = []
    
    print(f"[Combined Worker] 🔍 Validating {len(conversation_history)} messages...")
    
    for idx, msg in enumerate(conversation_history):
        message = {
            'role': msg.get('role'),
            'content': msg.get('content')
        }
        
        # STEP 1: Normalize content to blocks
        message['content'] = normalize_content_to_blocks(message['content'], message['role'])
        
        # STEP 2: Validate based on role
        if message['role'] == 'assistant':
            # Log block types BEFORE validation
            before_types = [b.get('type') for b in message['content'] if isinstance(b, dict)]
            
            message['content'] = validate_and_reorder_assistant_content(message['content'])
            
            # Log block types AFTER validation
            after_types = [b.get('type') for b in message['content'] if isinstance(b, dict)]
            
            if before_types != after_types:
                print(f"[Combined Worker] 🔧 Message {idx} (assistant) reordered:")
                print(f"    Before: {before_types}")
                print(f"    After:  {after_types}")
            
            # Skip if all blocks were invalid
            if not message['content']:
                print(f"[Combined Worker] ⚠️ Skipping message {idx} - all blocks invalid")
                continue
        
        elif message['role'] == 'user':
            message['content'] = validate_user_content(message['content'], messages)
            
            # Skip if all blocks were removed
            if not message['content']:
                print(f"[Combined Worker] ⚠️ Skipping message {idx} - all blocks orphaned")
                continue
        
        # STEP 3: Check for duplicate consecutive roles
        if messages and messages[-1].get('role') == message['role']:
            print(f"[Combined Worker] ⚠️ Duplicate {message['role']} message at index {idx}")
            
            # Merge content blocks
            if isinstance(messages[-1].get('content'), list) and isinstance(message.get('content'), list):
                print(f"[Combined Worker] 🔧 Merging {len(message['content'])} blocks into previous message")
                messages[-1]['content'].extend(message['content'])
                
                # CRITICAL: If merging assistant messages, reorder thinking blocks to first
                if message['role'] == 'assistant':
                    print(f"[Combined Worker] 🔧 Re-validating merged assistant content")
                    messages[-1]['content'] = validate_and_reorder_assistant_content(messages[-1]['content'])
                
                continue
            else:
                print(f"[Combined Worker] ⚠️ Cannot merge - skipping message {idx}")
                continue
        
        # STEP 4: Add validated message
        messages.append(message)
    
    print(f"[Combined Worker] ✅ Validated: {len(messages)} valid messages")
    return messages


# ============================================================
# LEGACY HELPER FUNCTIONS (For backward compatibility)
# ============================================================

def strip_thinking_blocks(content: List[Dict]) -> List[Dict]:
    """
    Remove thinking blocks from content array (legacy function)
    
    NOTE: This is legacy - modern code should use validate_and_reorder_assistant_content()
    Kept for backward compatibility with existing code
    """
    if not isinstance(content, list):
        return content
    
    return [
        block for block in content
        if block.get('type') not in ('thinking', 'redacted_thinking')
    ]


def prepare_content_for_storage(content: List[Dict]) -> List[Dict]:
    """
    Prepare assistant message content for database storage (legacy function)
    
    Keeps: text blocks, tool_use blocks
    Removes: thinking blocks, tool_result blocks
    """
    if not isinstance(content, list):
        return content
    
    return [
        block for block in content
        if block.get('type') in ('text', 'tool_use')
    ]


# Alias for backward compatibility
reorder_assistant_content_blocks = validate_and_reorder_assistant_content


# ============================================================
# WORKER IMPLEMENTATIONS
# ============================================================

# Add calculator module path to import ToolUseAgent
calculator_module_path = os.path.join(os.path.dirname(__file__), '..', '..', 'UI', 'external', 'modules', 'calculator-module', 'ORIGINAL')
sys.path.insert(0, calculator_module_path)

# Import REAL ToolUseAgent from calculator module (optional)
try:
    from tool_use_agent import ToolUseAgent
    TOOL_USE_AGENT_AVAILABLE = True
    print("✅ [Combined Worker] ToolUseAgent imported - Quote Calculator tools available")
except ImportError:
    TOOL_USE_AGENT_AVAILABLE = False
    print("ℹ️  [Combined Worker] Quote Calculator module not found (optional)")
    
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
    user_id: Optional[int] = None,
    thread_id: Optional[str] = None
):
    """
    Background worker that executes ToolUseAgent (with file support)
    
    Args:
        agent_id: Agent identifier
        prompt: User prompt text
        file_data: List of file dicts with {filename, content_type, data (bytes)}
        lock: threading.Lock for thread safety
        session_id: Session ID
        queue: Queue for SSE events
        conversation_history: Previous conversation (will be validated)
        context: UI context
        user_id: User ID for OAuth credential injection
    """
    if user_id is None:
        user_id = 1
    
    log_prefix = f"[Combined Worker {agent_id}]"
    
    try:
        print("\n\n" + "=" * 100)
        print(f"🚀 NEW REQUEST STARTED - run_agent_worker")
        print("=" * 100)
        print(f"Session: {session_id[:8]}")
        print(f"Agent: {agent_id}")
        print(f"User ID: {user_id}")
        print(f"Files: {len(file_data)}")
        print(f"Prompt: {prompt[:100]}..." if len(prompt) > 100 else f"Prompt: {prompt}")
        print("=" * 100 + "\n")
        
        # Validate conversation history (fixes all 7 issues)
        if conversation_history:
            conversation_history = validate_conversation_history(conversation_history)
        
        # Build content blocks from files
        content_blocks = []
        
        for file_info in file_data:
            filename = file_info.get('filename', 'unknown')
            content_type = file_info.get('content_type', 'application/octet-stream')
            file_bytes = file_info.get('data', b'')
            
            import base64
            encoded_data = base64.b64encode(file_bytes).decode('utf-8')
            
            if content_type == 'application/pdf':
                block_type = 'document'
            elif content_type.startswith('image/'):
                block_type = 'image'
            else:
                block_type = 'document'
            
            content_blocks.append({
                'type': block_type,
                'source': {
                    'type': 'base64',
                    'media_type': content_type,
                    'data': encoded_data
                }
            })
            
            print(f"{log_prefix} Added {block_type}: {filename}")
        
        # Add text prompt
        if prompt:
            content_blocks.append({'type': 'text', 'text': prompt})
        elif not content_blocks:
            queue.put({'type': 'error', 'error': 'No prompt or files provided'})
            return
        
        print(f"{log_prefix} Initializing ToolUseAgent...")
        
        def log_callback(log_entry: dict):
            """Stream ToolUseAgent logs to SSE queue"""
            event_type = log_entry.get('type', 'log')
            
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
            config_path = 'config/database-config.json'
            agent = ToolUseAgent(config_path, log_callback=log_callback)
            
            queue.put({'type': 'thinking', 'content': 'Processing with Tool Use API...'})
            
            result = agent.process_request(
                customer_message=prompt,
                max_turns=20,
                conversation_history=conversation_history,
                content_blocks=content_blocks if file_data else None
            )
            
            if result.get('success'):
                final_response = result.get('final_response', '')
                
                queue.put({'type': 'response', 'content': final_response})
                complete_payload = {
                    'type': 'complete',
                    'result': final_response,
                    'session_id': session_id,
                    'tool_calls': result.get('tool_calls', 0),
                    'thinking_tokens': result.get('thinking_tokens', 0)
                }
                if thread_id is not None:
                    complete_payload['thread_id'] = thread_id
                queue.put(complete_payload)
                
                print(f"{log_prefix} Complete")
            else:
                error_msg = result.get('error', 'Unknown error')
                queue.put({'type': 'error', 'error': error_msg})
            
            agent.close()
            
        except Exception as e:
            print(f"{log_prefix} ToolUseAgent error: {e}")
            import traceback
            traceback.print_exc()
            queue.put({'type': 'error', 'error': str(e)})
        
    except Exception as e:
        print(f"{log_prefix} Worker error: {e}")
        import traceback
        traceback.print_exc()
        queue.put({'type': 'error', 'error': str(e)})
    
    finally:
        try:
            lock.release()
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
    user_id: int = 1,
    thread_id: Optional[str] = None
):
    """
    Simplified worker for text-only prompts (no files)
    
    USES: Validated conversation history (all 7 fixes applied)
    
    Args:
        agent_id: Agent identifier
        prompt: User prompt text
        lock: threading.Lock
        session_id: Session ID
        queue: Queue for SSE events
        conversation_history: Previous conversation (will be validated)
        ai_client: UnifiedAIClient instance
        user_id: User ID for OAuth credential injection
    """
    log_prefix = f"[Combined Simple {agent_id}]"
    
    try:
        print("\n\n" + "=" * 100)
        print(f"🚀 NEW REQUEST STARTED - run_simple_agent_worker")
        print("=" * 100)
        print(f"Session: {session_id[:8]}")
        print(f"Agent: {agent_id}")
        print(f"User ID: {user_id}")
        print(f"Prompt: {prompt[:100]}..." if len(prompt) > 100 else f"Prompt: {prompt}")
        print("=" * 100 + "\n")
        
        if ai_client is None:
            raise ValueError("ai_client is required but not provided")
        
        # Load tools from registry
        from tools import registry_v3
        registry = registry_v3.get_registry()
        
        # Just-in-time schema loading
        conversation_length = len(conversation_history or [])
        
        meta_tool_names = [
            'list_available_platforms',
            'list_platform_tools',
            'get_tool_schema',
            'get_platform_guide',
            'recommend_tools_for_task'
        ]
        
        all_tools_dict = {t['name']: t for t in registry.get_anthropic_tools()}
        tools = [all_tools_dict[name] for name in meta_tool_names if name in all_tools_dict]
        
        print(f"{log_prefix} 🔷 Sending {len(tools)} meta-tools")
        
        # Get system prompt
        prompt_name = 'data_agent_chat'
        system_prompt = ai_client.get_system_prompt(prompt_name)
        
        # Build messages with VALIDATED history
        messages = []
        if conversation_history:
            print(f"{log_prefix} 🔍 Validating {len(conversation_history)} messages from history...")
            
            # CRITICAL: Use comprehensive validation (fixes all 7 issues)
            messages = validate_conversation_history(conversation_history)
            
            print(f"{log_prefix} ✅ Validated: {len(messages)} valid messages")
        
        messages.append({'role': 'user', 'content': prompt})
        
        # Call AI with tools
        response = ai_client.create_message(
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
        
        # Extract response
        response_text = ''
        tool_uses = []
        
        if isinstance(response, dict) and 'content' in response:
            for block in response['content']:
                if block.get('type') == 'thinking':
                    queue.put({'type': 'thinking_block', 'content': block.get('thinking', '')})
                elif block.get('type') == 'text':
                    response_text += block.get('text', '')
                elif block.get('type') == 'tool_use':
                    tool_uses.append(block)
        
        # Tool execution loop (with validation)
        max_tool_iterations = 20
        tool_iteration = 0
        current_response = response
        
        while (tool_uses and current_response.get('stop_reason') == 'tool_use' and 
               tool_iteration < max_tool_iterations):
            
            tool_iteration += 1
            print(f"{log_prefix} 🔧 Tool iteration {tool_iteration}: {len(tool_uses)} tool(s)")
            
            if tool_iteration == 1 and response_text:
                queue.put({'type': 'content_delta', 'text': response_text})
            
            # Execute tools
            tool_results = []
            for tool_use in tool_uses:
                tool_name = tool_use.get('name')
                tool_input = tool_use.get('input', {})
                tool_id = tool_use.get('id')
                
                queue.put({'type': 'tool_use', 'tool_name': tool_name, 'tool_input': tool_input})
                
                try:
                    # Execute tool
                    if tool_name in ['get_tool_schema', 'execute_tool']:
                        from tools.implementations.meta_tools import execute_tool as execute_tool_fn, get_tool_schema as get_tool_schema_fn
                        
                        if tool_name == 'execute_tool':
                            result = execute_tool_fn(**tool_input, _user_id=user_id, _injected_credentials=True)
                        else:
                            result = get_tool_schema_fn(**tool_input)
                    else:
                        tool_input_copy = {k: v for k, v in tool_input.items() if k != 'tool_name'}
                        
                        if tool_name.startswith(('google_', 'microsoft_')):
                            result = registry.execute_tool(
                                tool_name=tool_name,
                                _user_id=user_id,
                                _injected_credentials=True,
                                **tool_input_copy
                            )
                        else:
                            result = registry.execute_tool(tool_name=tool_name, **tool_input_copy)
                    
                    queue.put({'type': 'tool_result', 'tool_name': tool_name, 'result': result, 'success': True})
                    
                    tool_results.append({
                        'type': 'tool_result',
                        'tool_use_id': tool_id,
                        'content': str(result)
                    })
                    
                except Exception as tool_error:
                    print(f"{log_prefix} ❌ Tool failed: {tool_name} - {tool_error}")
                    queue.put({'type': 'tool_result', 'tool_name': tool_name, 'result': str(tool_error), 'success': False})
                    
                    tool_results.append({
                        'type': 'tool_result',
                        'tool_use_id': tool_id,
                        'content': f"Error: {str(tool_error)}",
                        'is_error': True
                    })
            
            # CRITICAL: Validate assistant content before adding to messages
            content = current_response.get('content', [])
            validated_content = validate_and_reorder_assistant_content(content)
            
            # Add validated content to messages
            messages.append({'role': 'assistant', 'content': validated_content})
            messages.append({'role': 'user', 'content': tool_results})
            
            # CRITICAL FIX: Re-validate entire message history before next API call
            # This prevents "text block before thinking block" errors from propagating
            print(f"{log_prefix} 🔍 Re-validating entire history before round {tool_iteration + 1}...")
            messages = validate_conversation_history(messages)
            print(f"{log_prefix} ✅ History validated: {len(messages)} messages")
            
            # Get next response
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
            
            # Extract new tool_uses
            tool_uses = []
            if isinstance(current_response, dict) and 'content' in current_response:
                for block in current_response['content']:
                    if block.get('type') == 'tool_use':
                        tool_uses.append(block)
        
        # Send final response
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
            if response_text:
                queue.put({'type': 'content_delta', 'text': response_text})
        
        complete_payload = {'type': 'complete', 'result': response_text, 'session_id': session_id}
        if thread_id is not None:
            complete_payload['thread_id'] = thread_id
        queue.put(complete_payload)
        
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
    
    USES: Validated conversation history (all 7 fixes applied)
    
    Args:
        message: User message
        session_id: Session ID
        user_id: User ID for OAuth credential lookup
        conversation_history: Previous messages (will be validated)
        ai_client: UnifiedAIClient instance
        attachments: List of file attachments
    
    Returns:
        Dict with response and tool_calls
    """
    from tools.registry_v3 import get_registry
    
    try:
        print("\n\n" + "=" * 100)
        print(f"🚀 NEW REQUEST STARTED - agent_worker (CLI)")
        print("=" * 100)
        print(f"Session: {session_id[:8]}")
        print(f"User ID: {user_id}")
        print(f"Message: {message[:100]}..." if len(message) > 100 else f"Message: {message}")
        print(f"History: {len(conversation_history) if conversation_history else 0} messages")
        print(f"Attachments: {len(attachments) if attachments else 0}")
        print("=" * 100 + "\n")
        
        registry = get_registry()
        tools = registry.get_anthropic_tools()
        
        # Validate conversation history (fixes all 7 issues)
        if conversation_history is None:
            conversation_history = []
        
        if conversation_history:
            conversation_history = validate_conversation_history(conversation_history)
        
        # Build user message with attachments
        user_message = {'role': 'user'}
        
        if attachments and len(attachments) > 0:
            content_blocks = [{'type': 'text', 'text': message}]
            
            for attachment in attachments:
                content_blocks.append({
                    'type': attachment.get('type', 'document'),
                    'source': {
                        'type': 'base64',
                        'media_type': attachment.get('media_type'),
                        'data': attachment.get('source', {}).get('data')
                    }
                })
            
            user_message['content'] = content_blocks
        else:
            user_message['content'] = message
        
        messages = conversation_history + [user_message]
        
        # Build system prompt
        system_prompt = """You are a helpful AI assistant with access to tools.

You can use tools to help the user complete tasks."""
        
        # Call AI
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
                
                try:
                    if 'tool_name' in tool_input:
                        del tool_input['tool_name']
                    
                    if tool_name.startswith(('google_', 'microsoft_')):
                        result = registry.execute_tool(
                            tool_name=tool_name,
                            _user_id=user_id,
                            _injected_credentials=True,
                            **tool_input
                        )
                    else:
                        result = registry.execute_tool(tool_name=tool_name, **tool_input)
                    
                    tool_calls.append({'name': tool_name, 'success': True, 'result': result})
                except Exception as e:
                    tool_calls.append({'name': tool_name, 'success': False, 'error': str(e)})
        
        return {
            'response': response_text,
            'tool_calls': tool_calls,
            'session_id': session_id
        }
        
    except Exception as e:
        print(f"❌ [Combined CLI Worker] Error: {e}")
        import traceback
        traceback.print_exc()
        raise


def execute_streaming_request(
    session_id: str,
    user_prompt: str,
    conversation_history: List[Dict],
    system_prompt: str,
    tools: List[Dict],
    user_id: Optional[int] = None,
    max_rounds: int = 20,
    current_round: int = 1
) -> Generator[Dict[str, Any], None, None]:
    """
    Execute streaming request with multi-round tool use
    
    FULL STREAMING IMPLEMENTATION with all validation fixes applied
    
    Args:
        session_id: Session identifier
        user_prompt: User's message
        conversation_history: Full conversation history (will be validated)
        system_prompt: System prompt for AI
        tools: List of tool definitions
        user_id: User ID for credential injection
        max_rounds: Maximum recursive rounds (safety limit)
        current_round: Current round number
    
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
        
        print("\n\n" + "=" * 100)
        print(f"🚀 NEW REQUEST STARTED - execute_streaming_request (Round {current_round})")
        print("=" * 100)
        print(f"Session: {session_id[:8]}")
        print(f"User ID: {user_id}")
        print(f"Prompt: {user_prompt[:100] if user_prompt else '(continuation)'}")
        print(f"History: {len(conversation_history)} messages")
        print(f"Tools: {len(tools)} available")
        print("=" * 100 + "\n")
        
        # CRITICAL: ALWAYS validate conversation history before API call (all rounds)
        # This ensures thinking blocks are first, even on recursive calls
        if conversation_history:
            print(f"{log_prefix} Validating {len(conversation_history)} messages before Round {current_round}...")
            conversation_history = validate_conversation_history(conversation_history)
            print(f"{log_prefix} Validation complete: {len(conversation_history)} messages ready")
        
        # Build messages
        messages = conversation_history.copy()
        if user_prompt and current_round == 1:
            messages.append({'role': 'user', 'content': user_prompt})
        
        # Initialize Anthropic client
        import os
        from anthropic import Anthropic
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            yield {'type': 'error', 'error': 'ANTHROPIC_API_KEY not found'}
            return
        
        client = Anthropic(api_key=api_key, timeout=120.0, max_retries=3)
        model = "claude-sonnet-4-5-20250929"
        
        # Track content blocks and stop reason
        all_content_blocks = []
        stop_reason = None
        tool_uses = []
        
        # Stream response from Claude
        with client.messages.stream(
            model=model,
            max_tokens=16000,
            system=system_prompt,
            messages=messages,
            tools=tools,
            thinking={'type': 'enabled', 'budget_tokens': 5000},
            extra_headers={'anthropic-beta': 'web-fetch-2025-09-10'}
        ) as stream:
            # Process streaming events
            for event in stream:
                if not hasattr(event, 'type'):
                    continue
                
                event_type = event.type
                
                # CONTENT BLOCK START
                if event_type == 'content_block_start':
                    if hasattr(event, 'content_block'):
                        block = event.content_block
                        block_type = block.type
                        index = event.index
                        
                        all_content_blocks.append(block)
                        
                        if block_type == 'thinking':
                            yield {'type': 'thinking', 'content': '', 'block_index': index, 'delta_type': 'start'}
                        elif block_type == 'text':
                            yield {'type': 'content_delta', 'text': '', 'block_index': index, 'delta_type': 'start'}
                        elif block_type == 'tool_use':
                            tool_uses.append({'id': block.id, 'name': block.name, 'input': {}})
                            yield {'type': 'tool_use', 'tool_name': block.name, 'tool_id': block.id, 'tool_input': {}, 'block_index': index}
                
                # CONTENT BLOCK DELTA
                elif event_type == 'content_block_delta':
                    if hasattr(event, 'delta'):
                        delta = event.delta
                        delta_type = delta.type
                        index = event.index
                        
                        if delta_type == 'thinking_delta':
                            yield {'type': 'thinking', 'content': delta.thinking, 'block_index': index, 'delta_type': 'delta'}
                        elif delta_type == 'text_delta':
                            yield {'type': 'content_delta', 'text': delta.text, 'block_index': index, 'delta_type': 'delta'}
            
            # Get final message
            final_message = stream.get_final_message()
            
            if final_message:
                stop_reason = final_message.stop_reason
                all_content_blocks = final_message.content
                
                # Parse tool inputs
                tool_uses = []
                for block in all_content_blocks:
                    if hasattr(block, 'type') and block.type == 'tool_use':
                        tool_uses.append({'id': block.id, 'name': block.name, 'input': block.input})
                        yield {'type': 'tool_input_complete', 'tool_name': block.name, 'tool_id': block.id, 'tool_input': block.input}
        
        # Serialize content blocks
        serialized_content = []
        for block in all_content_blocks:
            if hasattr(block, 'type'):
                if block.type == 'thinking':
                    serialized_content.append({'type': 'thinking', 'thinking': block.thinking, 'signature': getattr(block, 'signature', '')})
                elif block.type == 'text':
                    serialized_content.append({'type': 'text', 'text': block.text})
                elif block.type == 'tool_use':
                    serialized_content.append({'type': 'tool_use', 'id': block.id, 'name': block.name, 'input': block.input})
        
        # CRITICAL: Reorder blocks - thinking MUST be first if present (Anthropic API requirement)
        thinking_blocks = [b for b in serialized_content if b.get('type') == 'thinking']
        other_blocks = [b for b in serialized_content if b.get('type') != 'thinking']
        serialized_content = thinking_blocks + other_blocks
        
        print(f"{log_prefix} Serialized {len(serialized_content)} blocks (thinking blocks first: {len(thinking_blocks)})")
        
        # Add assistant response to history (with ALL blocks including thinking)
        conversation_history.append({'role': 'assistant', 'content': serialized_content})
        
        # Execute tools if present
        if tool_uses and stop_reason == 'tool_use':
            from tools.registry_v3 import get_registry
            registry = get_registry()
            
            tool_results = []
            for tool_use in tool_uses:
                tool_name = tool_use['name']
                tool_input = tool_use['input'].copy()
                tool_id = tool_use['id']
                
                try:
                    # Handle meta-tools specially
                    if tool_name in ['get_tool_schema', 'execute_tool']:
                        from tools.implementations.meta_tools import execute_tool as execute_tool_fn, get_tool_schema as get_tool_schema_fn
                        
                        if tool_name == 'execute_tool':
                            result = execute_tool_fn(**tool_input, _user_id=user_id, _injected_credentials=True)
                        else:
                            result = get_tool_schema_fn(**tool_input)
                    else:
                        # Regular tools with credential injection
                        if tool_name.startswith(('google_', 'microsoft_')):
                            result = registry.execute_tool(tool_name=tool_name, _user_id=user_id, _injected_credentials=True, **tool_input)
                        else:
                            result = registry.execute_tool(tool_name=tool_name, **tool_input)
                    
                    result_str = json.dumps(result, indent=2) if not isinstance(result, str) else result
                    tool_results.append({'type': 'tool_result', 'tool_use_id': tool_id, 'content': result_str})
                    yield {'type': 'tool_result', 'tool_name': tool_name, 'tool_id': tool_id, 'result': result_str, 'success': True}
                
                except Exception as e:
                    error_msg = f"Tool execution failed: {str(e)}"
                    tool_results.append({'type': 'tool_result', 'tool_use_id': tool_id, 'content': error_msg, 'is_error': True})
                    yield {'type': 'tool_result', 'tool_name': tool_name, 'tool_id': tool_id, 'result': error_msg, 'success': False, 'error': error_msg}
            
            # Add tool results to history
            conversation_history.append({'role': 'user', 'content': tool_results})
            
            # Recursive call for next round
            yield from execute_streaming_request(
                session_id=session_id,
                user_prompt='',
                conversation_history=conversation_history,
                system_prompt=system_prompt,
                tools=tools,
                user_id=user_id,
                max_rounds=max_rounds,
                current_round=current_round + 1
            )
        else:
            # Conversation complete
            final_text = ''
            for block in all_content_blocks:
                if hasattr(block, 'type') and block.type == 'text':
                    final_text += block.text
            
            yield {'type': 'complete', 'session_id': session_id, 'full_response': final_text, 'stop_reason': stop_reason, 'total_rounds': current_round}
    
    except Exception as e:
        print(f"{log_prefix} ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        yield {'type': 'error', 'error': str(e), 'session_id': session_id, 'round': current_round}
