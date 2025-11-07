"""
Response Serializer - Convert Claude API responses to JSON format
Part of V4 Modular Architecture

Responsibilities:
- Parse Claude content blocks
- Extract text, thinking, tool_use, tool_result blocks
- Format for JSON serialization
- Handle streaming and non-streaming formats
"""

from typing import Dict, Any, List, Optional
import json
import sys
from pathlib import Path

# Add paths
ai_infra_dir = Path(__file__).parent.parent
if str(ai_infra_dir) not in sys.path:
    sys.path.insert(0, str(ai_infra_dir))

tools_dir = ai_infra_dir.parent
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from AI_infrastructure.utils.logger import get_logger

logger = get_logger(__name__)


class ResponseSerializer:
    """
    Serializes Claude API responses to JSON-compatible format.
    
    Features:
    - Parse content blocks (text, thinking, tool_use, tool_result)
    - Extract metadata (model, tokens, stop_reason)
    - Format for streaming (SSE events)
    - Format for HTTP responses (JSON)
    
    Usage:
        serializer = ResponseSerializer()
        
        # Serialize complete response
        data = serializer.serialize_response(claude_response)
        
        # Extract specific content types
        text = serializer.extract_text(claude_response)
        thinking = serializer.extract_thinking(claude_response)
        tools = serializer.extract_tool_calls(claude_response)
    """

    def __init__(self):
        """Initialize response serializer."""
        logger.debug("🔧 ResponseSerializer initialized")

    def serialize_response(self, response: Dict[str, Any], 
                          include_metadata: bool = True) -> Dict[str, Any]:
        """
        Serialize Claude API response to JSON format.
        
        Args:
            response: Claude API response dict
            include_metadata: Include model/token metadata
            
        Returns:
            Serialized dict with structure:
            {
                "content": [...],  # Content blocks
                "text": str,       # Extracted text
                "thinking": str,   # Extracted thinking
                "tool_calls": [],  # Extracted tool calls
                "metadata": {...}  # Optional metadata
            }
            
        Example:
            data = serializer.serialize_response(response)
            print(f"Text: {data['text']}")
            print(f"Tools: {len(data['tool_calls'])}")
        """
        logger.debug("📦 Serializing Claude response")
        
        content_blocks = response.get('content', [])
        
        # Extract different content types
        text = self.extract_text(response)
        thinking = self.extract_thinking(response)
        tool_calls = self.extract_tool_calls(response)
        
        result = {
            'content': content_blocks,
            'text': text,
            'thinking': thinking,
            'tool_calls': tool_calls
        }
        
        # Add metadata if requested
        if include_metadata:
            result['metadata'] = {
                'model': response.get('model', 'unknown'),
                'stop_reason': response.get('stop_reason'),
                'usage': response.get('usage', {}),
                'id': response.get('id'),
                'role': response.get('role', 'assistant')
            }
            logger.debug(f"📊 Metadata: model={result['metadata']['model']}, "
                        f"stop_reason={result['metadata']['stop_reason']}")
        
        logger.info(f"Response serialized: {len(text)} chars text, "
                   f"{len(thinking)} chars thinking, {len(tool_calls)} tools")
        
        return result

    def extract_text(self, response: Dict[str, Any]) -> str:
        """
        Extract text content from response.
        
        Args:
            response: Claude API response
            
        Returns:
            Concatenated text from all text blocks
            
        Example:
            text = serializer.extract_text(response)
            print(f"Assistant said: {text}")
        """
        content_blocks = response.get('content', [])
        
        text_blocks = [
            block['text']
            for block in content_blocks
            if block.get('type') == 'text'
        ]
        
        text = '\n\n'.join(text_blocks)
        logger.debug(f"📝 Extracted {len(text_blocks)} text blocks ({len(text)} chars)")
        
        return text

    def extract_thinking(self, response: Dict[str, Any]) -> str:
        """
        Extract thinking content from response.
        
        Args:
            response: Claude API response
            
        Returns:
            Concatenated thinking from all thinking blocks
            
        Example:
            thinking = serializer.extract_thinking(response)
            if thinking:
                print(f"Claude's reasoning: {thinking}")
        """
        content_blocks = response.get('content', [])
        
        thinking_blocks = [
            block['thinking']
            for block in content_blocks
            if block.get('type') == 'thinking'
        ]
        
        thinking = '\n\n'.join(thinking_blocks)
        
        if thinking:
            logger.debug(f"💭 Extracted {len(thinking_blocks)} thinking blocks ({len(thinking)} chars)")
        
        return thinking

    def extract_tool_calls(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract tool_use blocks from response.
        
        Args:
            response: Claude API response
            
        Returns:
            List of tool call dicts: [{"id": str, "name": str, "input": dict}, ...]
            
        Example:
            tools = serializer.extract_tool_calls(response)
            for tool in tools:
                print(f"Tool: {tool['name']} - ID: {tool['id']}")
        """
        content_blocks = response.get('content', [])
        
        tool_calls = [
            {
                'id': block['id'],
                'name': block['name'],
                'input': block['input']
            }
            for block in content_blocks
            if block.get('type') == 'tool_use'
        ]
        
        if tool_calls:
            logger.debug(f"🔧 Extracted {len(tool_calls)} tool calls")
            for tool in tool_calls:
                logger.debug(f"  - {tool['name']} (id: {tool['id'][:8]}...)")
        
        return tool_calls

    def serialize_for_sse(self, response: Dict[str, Any]) -> List[str]:
        """
        Serialize response as SSE (Server-Sent Events) for streaming.
        
        Args:
            response: Claude API response
            
        Returns:
            List of SSE event strings
            
        Example:
            events = serializer.serialize_for_sse(response)
            for event in events:
                yield event
        """
        logger.debug("🌊 Serializing for SSE streaming")
        
        events = []
        content_blocks = response.get('content', [])
        
        # Start event
        events.append(f"event: message_start\ndata: {json.dumps({'type': 'start'})}\n\n")
        
        # Content events
        for i, block in enumerate(content_blocks):
            block_type = block.get('type')
            
            if block_type == 'text':
                events.append(f"event: content_block\ndata: {json.dumps({
                    'type': 'text',
                    'text': block['text'],
                    'index': i
                })}\n\n")
            
            elif block_type == 'thinking':
                events.append(f"event: thinking\ndata: {json.dumps({
                    'type': 'thinking',
                    'thinking': block['thinking'],
                    'index': i
                })}\n\n")
            
            elif block_type == 'tool_use':
                events.append(f"event: tool_call\ndata: {json.dumps({
                    'type': 'tool_use',
                    'id': block['id'],
                    'name': block['name'],
                    'input': block['input'],
                    'index': i
                })}\n\n")
        
        # Done event
        events.append(f"event: message_stop\ndata: {json.dumps({
            'type': 'stop',
            'stop_reason': response.get('stop_reason'),
            'usage': response.get('usage', {})
        })}\n\n")
        
        logger.info(f"Created {len(events)} SSE events")
        return events

    def serialize_error(self, error: Exception, 
                       request_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Serialize error to JSON format.
        
        Args:
            error: Exception object
            request_id: Optional request ID
            
        Returns:
            Error dict with structure:
            {
                "error": str,
                "error_type": str,
                "request_id": str
            }
            
        Example:
            try:
                # ... API call
            except Exception as e:
                error_data = serializer.serialize_error(e, request_id)
                return jsonify(error_data), 500
        """
        error_type = type(error).__name__
        error_msg = str(error)
        
        logger.error(f" Serializing error: {error_type}: {error_msg}")
        
        result = {
            'error': error_msg,
            'error_type': error_type,
            'request_id': request_id
        }
        
        return result

    def format_conversation(self, conversation: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format conversation history for JSON serialization.
        
        Ensures all content is JSON-serializable.
        
        Args:
            conversation: List of message dicts
            
        Returns:
            Formatted conversation list
            
        Example:
            formatted = serializer.format_conversation(conversation)
            json.dumps(formatted)  # No serialization errors
        """
        logger.debug(f"📋 Formatting {len(conversation)} messages")
        
        formatted = []
        for msg in conversation:
            formatted_msg = {
                'role': msg['role'],
                'content': msg['content']
            }
            
            # Ensure content is proper format
            if isinstance(formatted_msg['content'], str):
                # Simple text content
                pass
            elif isinstance(formatted_msg['content'], list):
                # Content blocks - already in correct format
                pass
            else:
                # Unexpected format - convert to string
                logger.warning(f"⚠️ Unexpected content format: {type(formatted_msg['content'])}")
                formatted_msg['content'] = str(formatted_msg['content'])
            
            formatted.append(formatted_msg)
        
        logger.debug(f"Conversation formatted: {len(formatted)} messages")
        return formatted


# Export
__all__ = ['ResponseSerializer']
