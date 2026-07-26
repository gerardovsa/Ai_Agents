"""
Tool Call Processor - Processes tool_use blocks from Claude API responses
Part of V4 Modular Architecture

Responsibilities:
- Parse tool_use blocks from Claude response content
- Build tool_result blocks for conversation
- Handle multiple tool calls in sequence
- Format tool results for Claude API
"""

from typing import Dict, Any, List, Optional
import json
import sys
from pathlib import Path

# Add paths
ai_infra_dir = Path(__file__).parent.parent
if str(ai_infra_dir) not in sys.path:
    sys.path.insert(0, str(ai_infra_dir))

from utils.logger import get_logger
from core.tool_executor import ToolExecutor

logger = get_logger(__name__)


class ToolCallProcessor:
    """
    Processes tool calls from Claude API responses.
    
    Workflow:
    1. Parse response content blocks
    2. Extract tool_use blocks
    3. Execute tools via ToolExecutor
    4. Format results as tool_result blocks
    5. Add to conversation for next turn
    
    Usage:
        processor = ToolCallProcessor()
        response = claude_client.messages.create(...)
        tool_results = processor.process_response(response, user_id=1)
    """

    def __init__(self, executor: Optional[ToolExecutor] = None):
        """
        Initialize processor with tool executor.
        
        Args:
            executor: Optional ToolExecutor instance (creates new if not provided)
        """
        self.executor = executor or ToolExecutor()
        logger.info("🔄 ToolCallProcessor initialized")

    def extract_tool_calls(self, content_blocks: List[Any]) -> List[Dict[str, Any]]:
        """
        Extract tool_use blocks from Claude response content.
        
        Args:
            content_blocks: List of content blocks from Claude response
            
        Returns:
            List of tool call dicts with structure:
            {
                "id": "toolu_123",
                "name": "gmail_send_email",
                "input": {"to": "...", "subject": "..."}
            }
            
        Example:
            blocks = response.content
            tool_calls = processor.extract_tool_calls(blocks)
            print(f"Found {len(tool_calls)} tool calls")
        """
        logger.debug(f"🔍 Extracting tool calls from {len(content_blocks)} blocks")
        
        tool_calls = []
        
        for block in content_blocks:
            if hasattr(block, 'type') and block.type == 'tool_use':
                tool_call = {
                    'id': block.id,
                    'name': block.name,
                    'input': block.input
                }
                tool_calls.append(tool_call)
                logger.debug(f"📦 Found tool call: {block.name}")
        
        logger.info(f"Extracted {len(tool_calls)} tool calls")
        return tool_calls

    def execute_tool_calls(self, tool_calls: List[Dict[str, Any]], 
                          user_id: Optional[int] = None,
                          credentials: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute multiple tool calls and return results.
        
        Args:
            tool_calls: List of tool call dicts from extract_tool_calls()
            user_id: Optional user ID for credential injection
            credentials: Optional credentials dict
            
        Returns:
            List of result dicts with structure:
            {
                "tool_use_id": "toolu_123",
                "tool_name": "gmail_send_email",
                "success": True,
                "result": {...},
                "error": None  # or error message if failed
            }
            
        Example:
            results = processor.execute_tool_calls(tool_calls, user_id=1)
            for result in results:
                if result['success']:
                    print(f"{result['tool_name']}: {result['result']}")
                else:
                    print(f" {result['tool_name']}: {result['error']}")
        """
        logger.info(f"⚙️ Executing {len(tool_calls)} tool calls")
        
        results = []
        
        for i, tool_call in enumerate(tool_calls, 1):
            tool_name = tool_call['name']
            tool_input = tool_call['input']
            tool_id = tool_call['id']
            
            logger.info(f"🔧 [{i}/{len(tool_calls)}] Executing: {tool_name}")
            
            try:
                result = self.executor.execute_tool(
                    tool_name=tool_name,
                    parameters=tool_input,
                    user_id=user_id,
                    credentials=credentials
                )
                
                results.append({
                    'tool_use_id': tool_id,
                    'tool_name': tool_name,
                    'success': True,
                    'result': result,
                    'error': None
                })
                
                logger.info(f"[{i}/{len(tool_calls)}] Success: {tool_name}")
                
            except Exception as e:
                logger.error(f" [{i}/{len(tool_calls)}] Failed: {tool_name} - {e}")
                
                results.append({
                    'tool_use_id': tool_id,
                    'tool_name': tool_name,
                    'success': False,
                    'result': None,
                    'error': str(e)
                })
        
        success_count = sum(1 for r in results if r['success'])
        logger.info(f"📊 Execution complete: {success_count}/{len(results)} successful")
        
        return results

    def build_tool_result_blocks(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Build tool_result content blocks for Claude API.
        
        ✨ NEW (Jan 2026): Detects content_block in tool results and includes them
        as structured content blocks (images/documents) instead of JSON strings.
        This allows Claude to natively process files without token overflow.
        
        Args:
            results: List of result dicts from execute_tool_calls()
            
        Returns:
            List of tool_result blocks in Claude API format:
            [
                {
                    "type": "tool_result",
                    "tool_use_id": "toolu_123",
                    "content": [
                        {"type": "text", "text": "Processed file: report.pdf"},
                        {"type": "document", "source": {"type": "base64", ...}}
                    ]
                }
            ]
            
        Example:
            result_blocks = processor.build_tool_result_blocks(results)
            conversation.append({
                "role": "user",
                "content": result_blocks
            })
        """
        logger.debug(f"🏗️ Building tool_result blocks for {len(results)} results")
        
        blocks = []
        
        for result in results:
            if result['success']:
                tool_result = result['result']
                
                # Check if result contains a content_block (from file processing tools)
                if isinstance(tool_result, dict) and 'content_block' in tool_result:
                    # Multi-part content: text + content block
                    content_block = tool_result['content_block']
                    metadata = tool_result.get('metadata', {})
                    
                    # Build text description
                    text_part = {
                        "type": "text",
                        "text": f"✅ Processed {metadata.get('source', 'file')}: {metadata.get('name', 'unknown')}\n"
                                f"Size: {metadata.get('size', 0):,} bytes\n"
                                f"Type: {metadata.get('type', 'unknown')}\n"
                                f"Method: {tool_result.get('method', 'direct')}\n"
                                f"Token estimate: ~{metadata.get('token_estimate', 0):,} tokens"
                    }
                    
                    # Content is array with text + content_block
                    content = [text_part, content_block]
                    logger.info(f"📎 Including content_block for {result['tool_name']}: "
                               f"{content_block['type']} ({metadata.get('size', 0):,} bytes)")
                else:
                    # Regular result - convert to JSON string
                    content = json.dumps(tool_result, indent=2)
            else:
                # Format error message
                content = f"Error: {result['error']}"
            
            block = {
                'type': 'tool_result',
                'tool_use_id': result['tool_use_id'],
                'content': content
            }

            # ✅ FIX F4 (Jul 26, 2026): Promote the tool_result block to the
            # SDK's BetaToolResultBlockParam class. This makes the wire
            # contract explicit, gives us `is_error` and `cache_control` for
            # free, and ensures any future SDK change (e.g. a new required
            # field) raises here instead of producing a 400 upstream.
            #
            # The constructed instance is converted back to a plain dict so
            # the rest of the pipeline (which speaks in dicts) keeps working
            # unchanged. We pass `is_error` based on the result['success']
            # flag the executor already returns — Anthropic treats `is_error`
            # blocks specially (model is told the call failed and asked to
            # retry or try a different tool).
            try:
                from anthropic.types.beta.tools import BetaToolResultBlockParam
                sdk_block = BetaToolResultBlockParam(
                    tool_use_id=result['tool_use_id'],
                    content=content,
                    is_error=not result.get('success', True),
                )
                block = dict(sdk_block)
            except Exception as _sdk_err:
                # Defensive: if the SDK shape ever drifts and the constructor
                # raises, keep the legacy dict rather than blowing up the
                # whole response pipeline. Logged for visibility.
                import logging as _log
                _log.getLogger(__name__).warning(
                    f"[ToolProcessor] BetaToolResultBlockParam ctor failed, "
                    f"falling back to raw dict: {_sdk_err}"
                )

            blocks.append(block)
            logger.debug(f"📦 Built result block for {result['tool_name']}")
        
        logger.info(f"✅ Built {len(blocks)} tool_result blocks")
        return blocks

    def process_response(self, response, user_id: Optional[int] = None,
                        credentials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process Claude API response end-to-end.
        
        Workflow:
        1. Extract tool_use blocks
        2. Execute tools
        3. Build tool_result blocks
        4. Return structured data
        
        Args:
            response: Claude API response object
            user_id: Optional user ID for credential injection
            credentials: Optional credentials dict
            
        Returns:
            Dict with structure:
            {
                "has_tool_calls": bool,
                "tool_calls": [...],
                "tool_results": [...],
                "result_blocks": [...],  # Ready for conversation
                "text_content": str,      # Any text blocks
                "thinking_content": str   # Any thinking blocks
            }
            
        Example:
            response = claude_client.messages.create(...)
            data = processor.process_response(response, user_id=1)
            
            if data['has_tool_calls']:
                # Add results to conversation
                conversation.append({
                    "role": "user",
                    "content": data['result_blocks']
                })
        """
        logger.info("🔄 Processing Claude response")
        
        # Extract text and thinking content
        text_content = ""
        thinking_content = ""
        
        for block in response.content:
            if hasattr(block, 'type'):
                if block.type == 'text':
                    text_content += block.text
                elif block.type == 'thinking':
                    thinking_content += block.thinking
        
        # Extract tool calls
        tool_calls = self.extract_tool_calls(response.content)
        
        if not tool_calls:
            logger.info("ℹ️ No tool calls found")
            return {
                'has_tool_calls': False,
                'tool_calls': [],
                'tool_results': [],
                'result_blocks': [],
                'text_content': text_content,
                'thinking_content': thinking_content
            }
        
        # Execute tools
        tool_results = self.execute_tool_calls(tool_calls, user_id, credentials)
        
        # Build result blocks
        result_blocks = self.build_tool_result_blocks(tool_results)
        
        logger.info(f"Response processed: {len(tool_calls)} tools executed")
        
        return {
            'has_tool_calls': True,
            'tool_calls': tool_calls,
            'tool_results': tool_results,
            'result_blocks': result_blocks,
            'text_content': text_content,
            'thinking_content': thinking_content
        }


# Export
__all__ = ['ToolCallProcessor']
