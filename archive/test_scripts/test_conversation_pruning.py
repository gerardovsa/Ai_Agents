"""
Test conversation pruning implementation

Tests:
1. No pruning needed for short conversations
2. Pruning triggers for long conversations
3. First user message is preserved
4. Recent messages are kept
5. Estimated token calculation
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from core.combined_agent_worker import prune_conversation_for_context_limit

def test_no_pruning_needed():
    """Test that short conversations are not pruned"""
    messages = [
        {'role': 'user', 'content': 'Hello'},
        {'role': 'assistant', 'content': 'Hi there!'},
        {'role': 'user', 'content': 'How are you?'},
        {'role': 'assistant', 'content': 'I am doing well!'}
    ]
    
    result = prune_conversation_for_context_limit(messages, max_estimated_tokens=180000)
    
    assert len(result) == len(messages), f"Expected {len(messages)} messages, got {len(result)}"
    print("Test 1 PASSED - No pruning for short conversations")


def test_pruning_triggers():
    """Test that long conversations are pruned"""
    # Create 300 messages (should exceed limit)
    messages = []
    for i in range(300):
        messages.append({'role': 'user', 'content': f'Message {i}'})
        messages.append({'role': 'assistant', 'content': f'Response {i}'})
    
    result = prune_conversation_for_context_limit(messages, max_estimated_tokens=180000)
    
    assert len(result) < len(messages), f"Expected pruning, got same length"
    print(f"Test 2 PASSED - Pruning triggered: {len(messages)} -> {len(result)} messages")


def test_first_user_preserved():
    """Test that first user message is preserved"""
    messages = []
    for i in range(300):
        messages.append({'role': 'user', 'content': f'Message {i}'})
        messages.append({'role': 'assistant', 'content': f'Response {i}'})
    
    result = prune_conversation_for_context_limit(messages, max_estimated_tokens=180000, preserve_first_user=True)
    
    assert result[0]['role'] == 'user', "First message should be user"
    assert result[0]['content'] == 'Message 0', "First user message should be preserved"
    print("Test 3 PASSED - First user message preserved")


def test_recent_messages_kept():
    """Test that recent messages are kept"""
    messages = []
    for i in range(300):
        messages.append({'role': 'user', 'content': f'Message {i}'})
        messages.append({'role': 'assistant', 'content': f'Response {i}'})
    
    result = prune_conversation_for_context_limit(messages, max_estimated_tokens=180000)
    
    # Last message should still be from the end of the original conversation
    last_original = messages[-1]['content']
    last_pruned = result[-1]['content']
    
    assert last_pruned == last_original, "Last message should be preserved"
    print("Test 4 PASSED - Recent messages kept")


def test_token_estimation():
    """Test estimated token calculation logic"""
    # With 800 tokens per message estimate and 180K limit:
    # 180000 / 800 = 225 messages maximum
    
    messages = []
    for i in range(300):  # Create more than 225
        messages.append({'role': 'user', 'content': f'Message {i}'})
    
    result = prune_conversation_for_context_limit(messages, max_estimated_tokens=180000)
    
    # Should be approximately 225 messages (or 226 with first preserved)
    expected_max = 225
    assert len(result) <= expected_max + 10, f"Too many messages: {len(result)} > {expected_max + 10}"
    print(f"Test 5 PASSED - Token estimation working: {len(messages)} -> {len(result)} messages")


if __name__ == '__main__':
    print("\nTesting Conversation Pruning Implementation")
    print("=" * 60)
    
    try:
        test_no_pruning_needed()
        test_pruning_triggers()
        test_first_user_preserved()
        test_recent_messages_kept()
        test_token_estimation()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
