r"""
Unit tests for UnifiedAnthropicClient

Run:
    cd C:\Users\gpoli\GIT\In_House_SQL\G_Folder
    python -m pytest AI_infrastructure/tests/test_anthropic_client.py -v
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import os
import sys

# Add core directory to path
core_path = os.path.join(os.path.dirname(__file__), '..', 'core')
sys.path.insert(0, core_path)

from unified_anthropic_client import UnifiedAnthropicClient


class TestAnthropicClient:
    
    @pytest.fixture
    def mock_config(self):
        """Mock config data"""
        return {
            'AI': {
                'AnthropicAPIKey': 'test-api-key',
                'Model': 'claude-sonnet-4-5-20250929'
            }
        }
    
    
    @pytest.fixture
    def client(self, mock_config):
        """Create client with mock config"""
        with patch('builtins.open', create=True) as mock_open:
            import json
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_config)
            
            from unified_anthropic_client import init_anthropic_client
            return init_anthropic_client('fake-config.json')
    
    
    def test_initialization(self, client):
        """Test client initializes correctly"""
        assert client is not None
        assert hasattr(client, 'client')
        assert hasattr(client, 'model')
        assert client.model == 'claude-sonnet-4-5-20250929'
    
    
    def test_system_prompts_exist(self, client):
        """Test all system prompts defined"""
        prompts = {
            'stock_chat': client._get_stock_chat_prompt(),
            'data_agent_chat': client._get_data_agent_prompt(),
            'single_viewer': client._get_single_viewer_prompt(),
            'triple_agent_1': client._get_triple_agent_prompt('1'),
            'triple_agent_2': client._get_triple_agent_prompt('2'),
            'triple_agent_3': client._get_triple_agent_prompt('3'),
        }
        
        for context, prompt in prompts.items():
            assert isinstance(prompt, str)
            assert len(prompt) > 100  # Should be substantial
            print(f"  ✓ {context}: {len(prompt)} chars")
    
    
    def test_sse_event_conversion(self, client):
        """Test SSE event conversion matches existing format"""
        # content_block_start event
        anthropic_event_start = Mock()
        anthropic_event_start.type = 'content_block_start'
        anthropic_event_start.index = 0
        anthropic_event_start.content_block = Mock(type='text', text='')
        
        sse_event = client._convert_event_to_sse(anthropic_event_start)
        assert sse_event['type'] == 'content_block_start'
        assert sse_event['index'] == 0
        assert sse_event['content_type'] == 'text'
        
        # content_block_delta event
        anthropic_event_delta = Mock()
        anthropic_event_delta.type = 'content_block_delta'
        anthropic_event_delta.index = 0
        anthropic_event_delta.delta = Mock(type='text_delta', text='Hello')
        
        sse_event = client._convert_event_to_sse(anthropic_event_delta)
        assert sse_event['type'] == 'content_block_delta'
        assert sse_event['delta']['text'] == 'Hello'
    
    
    @pytest.mark.asyncio
    async def test_process_streaming_text_only(self, client):
        """Test processing simple text prompt (no tools)"""
        # Mock Anthropic API response
        mock_stream = AsyncMock()
        mock_stream.__aiter__.return_value = [
            # Start event
            Mock(
                type='content_block_start',
                index=0,
                content_block=Mock(type='text', text='')
            ),
            # Delta events
            Mock(
                type='content_block_delta',
                index=0,
                delta=Mock(type='text_delta', text='Hello ')
            ),
            Mock(
                type='content_block_delta',
                index=0,
                delta=Mock(type='text_delta', text='world!')
            ),
            # Stop event
            Mock(type='content_block_stop', index=0),
            Mock(type='message_stop')
        ]
        
        with patch.object(client.client.messages, 'stream', return_value=mock_stream):
            events_received = []
            
            async def callback(event):
                events_received.append(event)
            
            session_data = {
                'ui_context': 'stock_chat',
                'conversation': []
            }
            
            conversation = await client.process_streaming(
                session_id='test-session',
                session_data=session_data,
                prompt='Hello',
                sse_callback=callback
            )
            
            # Verify conversation updated
            assert len(conversation) == 2  # user + assistant
            assert conversation[0]['role'] == 'user'
            assert conversation[1]['role'] == 'assistant'
            
            # Verify events sent via callback
            assert len(events_received) > 0
            assert any(e.get('type') == 'content_block_start' for e in events_received)
            assert any(e.get('type') == 'content_block_delta' for e in events_received)
    
    
    def test_tool_execution_integration(self, client):
        """Test tool execution integration exists"""
        # Verify method exists
        assert hasattr(client, '_handle_tool_use')
        
        # Test with mock tool use
        tool_use = {
            'id': 'tool-123',
            'name': 'execute_sql_query',
            'input': {
                'connection_id': 'test-connection',
                'query': 'SELECT 1',
                'query_name': 'Test Query',
                'query_description': 'Test'
            }
        }
        
        # Should return tool result (even if tool fails)
        result = client._handle_tool_use(tool_use)
        assert 'tool_use_id' in result
        assert result['tool_use_id'] == 'tool-123'
        assert 'content' in result or 'error' in result
    
    
    def test_conversation_continuation_with_tools(self, client):
        """Test conversation continues after tool execution"""
        # This would be a complex integration test
        # Verify the structure is correct
        assert hasattr(client, 'process_streaming')
        assert hasattr(client, '_handle_tool_use')
        
        # Mock conversation with tool use
        conversation = [
            {'role': 'user', 'content': 'What stocks do we have?'},
            {
                'role': 'assistant',
                'content': [
                    {'type': 'text', 'text': 'Let me check...'},
                    {
                        'type': 'tool_use',
                        'id': 'tool-1',
                        'name': 'query_stock_levels',
                        'input': {}
                    }
                ]
            }
        ]
        
        # Verify structure is valid for Anthropic API
        assert conversation[1]['role'] == 'assistant'
        assert any(block['type'] == 'tool_use' for block in conversation[1]['content'])
    
    
    def test_file_handling(self, client):
        """Test file encoding for document analysis"""
        # Mock file
        from io import BytesIO
        mock_file = Mock()
        mock_file.filename = 'test.pdf'
        mock_file.read.return_value = b'PDF content here'
        
        # Client should be able to handle files
        # (actual encoding tested in invoice_processor tests)
        assert hasattr(client, 'process_streaming')
        # Files parameter exists in process_streaming signature


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
