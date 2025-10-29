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

# Add Quote_Calculator path to import ToolUseAgent
quote_calculator_path = os.path.join(os.path.dirname(__file__), '..', '..', 'Quote_Calculator')
sys.path.insert(0, quote_calculator_path)

# TODO: Uncomment when tool_use_agent is available
# from AI_Quote_Agent.core.tool_use_agent import ToolUseAgent

# Placeholder for ToolUseAgent - using unified AI client instead
from core.unified_ai_client import ai_client

# Placeholder class for ToolUseAgent
class ToolUseAgent:
    """Placeholder - using unified_ai_client instead"""
    def __init__(self):
        self.tools = []
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
    context: str = 'triple_agent'
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
    """
    
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
        
        # ✅ INTEGRATE TOOLUSEAGENT - Real implementation
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
    conversation_history: Optional[List[Dict]] = None
):
    """
    Simplified worker for text-only prompts (no files)
    
    Used by Triple Agent for quick queries
    """
    
    log_prefix = f"[Simple Agent {agent_id}]"
    
    try:
        print(f"{log_prefix} Starting for session {session_id[:8]}...")
        
        # Send thinking event
        queue.put({'type': 'thinking', 'content': 'Processing...'})
        
        # Build messages with history
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({'role': 'user', 'content': prompt})
        
        # Call AI
        response = ai_client.create_message(
            messages=messages,
            provider='anthropic',
            model='claude-sonnet-4-20250514',
            max_tokens=4000
        )
        
        # Extract text
        response_text = ''
        if isinstance(response, dict) and 'content' in response:
            for block in response['content']:
                if block.get('type') == 'text':
                    response_text += block.get('text', '')
        
        # Send response
        queue.put({'type': 'response', 'content': response_text})
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
