r"""
Integration tests for complete AI Infrastructure

Run:
    cd C:\Users\gpoli\GIT\In_House_SQL\G_Folder
    python -m pytest AI_infrastructure/tests/test_integration.py -v
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import os
import sys
import tempfile
import json

# Add core directory to path
core_path = os.path.join(os.path.dirname(__file__), '..', 'core')
sys.path.insert(0, core_path)

from unified_session_manager import UnifiedSessionManager
from unified_anthropic_client import UnifiedAnthropicClient


class TestIntegration:
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, 'test_sessions.db')
        yield db_path
        if os.path.exists(db_path):
            os.remove(db_path)
        os.rmdir(temp_dir)
    
    
    @pytest.fixture
    def session_manager(self, temp_db):
        """Create session manager"""
        return UnifiedSessionManager(db_path=temp_db)
    
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration"""
        return {
            'AI': {
                'AnthropicAPIKey': 'test-key',
                'Model': 'claude-sonnet-4-5-20250929'
            }
        }
    
    
    @pytest.fixture
    def anthropic_client(self, mock_config):
        """Create Anthropic client with mock config"""
        temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(mock_config, temp_config)
        temp_config.close()
        
        from unified_anthropic_client import init_anthropic_client
        client = init_anthropic_client(temp_config.name)
        
        yield client
        
        os.unlink(temp_config.name)
    
    
    @pytest.mark.asyncio
    async def test_complete_chat_flow(self, session_manager, anthropic_client):
        """Test complete flow: create session → send message → stream → update conversation"""
        
        # 1. Create session
        session_id = session_manager.create_session('stock_chat')
        assert session_id is not None
        
        # 2. Get session data
        session_data = session_manager.get_session(session_id)
        assert session_data['conversation'] == []
        
        # 3. Get queue for SSE streaming
        queue = session_manager.get_queue(session_id)
        
        # 4. Mock Anthropic response
        mock_stream = AsyncMock()
        mock_stream.__aiter__.return_value = [
            Mock(
                type='content_block_start',
                index=0,
                content_block=Mock(type='text', text='')
            ),
            Mock(
                type='content_block_delta',
                index=0,
                delta=Mock(type='text_delta', text='Test response')
            ),
            Mock(type='content_block_stop', index=0),
            Mock(type='message_stop')
        ]
        
        # 5. Process with Anthropic client
        events_received = []
        
        def callback(event):
            events_received.append(event)
            queue.put(event)
        
        with patch.object(anthropic_client.client.messages, 'stream', return_value=mock_stream):
            updated_conversation = await anthropic_client.process_streaming(
                session_id=session_id,
                session_data=session_data,
                prompt='Hello',
                sse_callback=callback
            )
        
        # 6. Verify conversation updated
        assert len(updated_conversation) == 2  # user + assistant
        assert updated_conversation[0]['role'] == 'user'
        assert updated_conversation[1]['role'] == 'assistant'
        
        # 7. Update session with new conversation
        success = session_manager.update_conversation(session_id, updated_conversation)
        assert success is True
        
        # 8. Verify persistence
        session_data = session_manager.get_session(session_id)
        assert len(session_data['conversation']) == 2
        
        # 9. Verify events sent to queue
        assert len(events_received) > 0
        assert any(e.get('type') == 'content_block_delta' for e in events_received)
    
    
    @pytest.mark.asyncio
    async def test_multi_turn_conversation(self, session_manager, anthropic_client):
        """Test multi-turn conversation persistence"""
        
        session_id = session_manager.create_session('data_agent_chat')
        
        # Turn 1
        session_data = session_manager.get_session(session_id)
        
        mock_stream_1 = AsyncMock()
        mock_stream_1.__aiter__.return_value = [
            Mock(type='content_block_start', index=0, content_block=Mock(type='text', text='')),
            Mock(type='content_block_delta', index=0, delta=Mock(type='text_delta', text='Response 1')),
            Mock(type='message_stop')
        ]
        
        with patch.object(anthropic_client.client.messages, 'stream', return_value=mock_stream_1):
            conversation = await anthropic_client.process_streaming(
                session_id=session_id,
                session_data=session_data,
                prompt='Question 1',
                sse_callback=lambda e: None
            )
        
        session_manager.update_conversation(session_id, conversation)
        assert len(conversation) == 2
        
        # Turn 2 (should include Turn 1 history)
        session_data = session_manager.get_session(session_id)
        assert len(session_data['conversation']) == 2  # Has Turn 1 history
        
        mock_stream_2 = AsyncMock()
        mock_stream_2.__aiter__.return_value = [
            Mock(type='content_block_start', index=0, content_block=Mock(type='text', text='')),
            Mock(type='content_block_delta', index=0, delta=Mock(type='text_delta', text='Response 2')),
            Mock(type='message_stop')
        ]
        
        with patch.object(anthropic_client.client.messages, 'stream', return_value=mock_stream_2):
            conversation = await anthropic_client.process_streaming(
                session_id=session_id,
                session_data=session_data,
                prompt='Question 2',
                sse_callback=lambda e: None
            )
        
        session_manager.update_conversation(session_id, conversation)
        assert len(conversation) == 4  # Turn 1 + Turn 2
    
    
    def test_concurrent_sessions(self, session_manager):
        """Test multiple concurrent sessions"""
        sessions = []
        
        # Create 10 concurrent sessions
        for i in range(10):
            session_id = session_manager.create_session(
                ui_context='stock_chat' if i % 2 == 0 else 'data_agent_chat'
            )
            sessions.append(session_id)
        
        # Verify all sessions exist
        for session_id in sessions:
            session = session_manager.get_session(session_id)
            assert session is not None
            
            # Verify independent queues
            queue = session_manager.get_queue(session_id)
            assert queue is not None
    
    
    def test_sse_event_format_compatibility(self, anthropic_client):
        """Test SSE events match existing frontend format"""
        
        # Test content_block_start
        event = Mock()
        event.type = 'content_block_start'
        event.index = 0
        event.content_block = Mock(type='text', text='')
        
        sse_event = anthropic_client._convert_event_to_sse(event)
        
        # Required fields for existing frontend
        assert 'type' in sse_event
        assert 'index' in sse_event
        assert 'content_type' in sse_event
        assert sse_event['type'] == 'content_block_start'
        
        # Test content_block_delta
        event = Mock()
        event.type = 'content_block_delta'
        event.index = 0
        event.delta = Mock(type='text_delta', text='Test')
        
        sse_event = anthropic_client._convert_event_to_sse(event)
        
        # Required fields
        assert 'type' in sse_event
        assert 'index' in sse_event
        assert 'delta' in sse_event
        assert 'text' in sse_event['delta']
        assert sse_event['delta']['text'] == 'Test'
    
    
    def test_system_prompt_routing(self, anthropic_client):
        """Test correct system prompt selected for each UI context"""
        
        contexts = [
            'stock_chat',
            'data_agent_chat',
            'single_viewer',
            'triple_agent'
        ]
        
        for context in contexts:
            if context == 'triple_agent':
                # Test all 3 agents
                for agent_id in ['1', '2', '3']:
                    prompt = anthropic_client._get_triple_agent_prompt(agent_id)
                    assert isinstance(prompt, str)
                    assert len(prompt) > 100
            else:
                # Get appropriate prompt
                if context == 'stock_chat':
                    prompt = anthropic_client._get_stock_chat_prompt()
                elif context == 'data_agent_chat':
                    prompt = anthropic_client._get_data_agent_prompt()
                elif context == 'single_viewer':
                    prompt = anthropic_client._get_single_viewer_prompt()
                
                assert isinstance(prompt, str)
                assert len(prompt) > 100


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
