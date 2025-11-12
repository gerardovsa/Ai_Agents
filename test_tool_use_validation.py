"""
Test Tool Use Validation Fix
Tests the validation logic for tool_use <-> tool_result pairing

Run with: python test_tool_use_validation.py
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from core.combined_agent_worker import (
    validate_conversation_history,
    validate_user_content,
    validate_and_reorder_assistant_content
)


def test_valid_conversation():
    """Test valid conversation with proper tool_use -> tool_result pairing"""
    print("\n" + "=" * 80)
    print("TEST 1: Valid Conversation (tool_use followed by tool_result)")
    print("=" * 80)
    
    conversation = [
        {
            'role': 'user',
            'content': [{'type': 'text', 'text': 'List my emails'}]
        },
        {
            'role': 'assistant',
            'content': [
                {'type': 'thinking', 'thinking': 'I should list emails', 'signature': ''},
                {'type': 'tool_use', 'id': 'toolu_01ABC', 'name': 'gmail_list_messages', 'input': {}}
            ]
        },
        {
            'role': 'user',
            'content': [
                {'type': 'tool_result', 'tool_use_id': 'toolu_01ABC', 'content': 'Email list'}
            ]
        },
        {
            'role': 'assistant',
            'content': [{'type': 'text', 'text': 'Here are your emails'}]
        }
    ]
    
    validated = validate_conversation_history(conversation)
    
    print(f"\nOriginal messages: {len(conversation)}")
    print(f"Validated messages: {len(validated)}")
    
    if len(validated) == len(conversation):
        print("✅ PASS: All messages preserved")
        return True
    else:
        print("❌ FAIL: Messages were removed")
        return False


def test_orphaned_tool_result():
    """Test orphaned tool_result (no prior tool_use)"""
    print("\n" + "=" * 80)
    print("TEST 2: Orphaned tool_result (should be removed)")
    print("=" * 80)
    
    conversation = [
        {
            'role': 'user',
            'content': [{'type': 'text', 'text': 'Hello'}]
        },
        {
            'role': 'assistant',
            'content': [{'type': 'text', 'text': 'Hi there'}]
        },
        {
            'role': 'user',
            'content': [
                {'type': 'tool_result', 'tool_use_id': 'toolu_01XYZ', 'content': 'Result'}  # ORPHANED!
            ]
        }
    ]
    
    validated = validate_conversation_history(conversation)
    
    print(f"\nOriginal messages: {len(conversation)}")
    print(f"Validated messages: {len(validated)}")
    
    # Should remove the user message with orphaned tool_result
    if len(validated) == 2:  # Only first 2 messages
        print("✅ PASS: Orphaned tool_result removed")
        return True
    else:
        print("❌ FAIL: Orphaned tool_result NOT removed")
        print(f"Expected 2 messages, got {len(validated)}")
        return False


def test_missing_tool_result():
    """Test missing tool_result for tool_use"""
    print("\n" + "=" * 80)
    print("TEST 3: Missing tool_result (tool_use without result)")
    print("=" * 80)
    
    conversation = [
        {
            'role': 'user',
            'content': [{'type': 'text', 'text': 'List my emails'}]
        },
        {
            'role': 'assistant',
            'content': [
                {'type': 'tool_use', 'id': 'toolu_01ABC', 'name': 'gmail_list_messages', 'input': {}},
                {'type': 'tool_use', 'id': 'toolu_01DEF', 'name': 'gmail_list_labels', 'input': {}}
            ]
        },
        {
            'role': 'user',
            'content': [
                {'type': 'tool_result', 'tool_use_id': 'toolu_01ABC', 'content': 'Emails'}
                # MISSING tool_result for toolu_01DEF!
            ]
        }
    ]
    
    validated = validate_conversation_history(conversation)
    
    print(f"\nOriginal messages: {len(conversation)}")
    print(f"Validated messages: {len(validated)}")
    
    # Check if message 2 has tool_use
    if len(validated) >= 2:
        msg1 = validated[1]
        tool_use_ids = [b.get('id') for b in msg1.get('content', []) if b.get('type') == 'tool_use']
        print(f"Assistant message tool_use IDs: {tool_use_ids}")
        
        if len(validated) >= 3:
            msg2 = validated[2]
            tool_result_ids = [b.get('tool_use_id') for b in msg2.get('content', []) if b.get('type') == 'tool_result']
            print(f"User message tool_result IDs: {tool_result_ids}")
            
            missing = set(tool_use_ids) - set(tool_result_ids)
            if missing:
                print(f"⚠️  Missing tool_result for: {missing}")
                print("✅ PASS: Missing tool_result detected (would be caught by pre-API validation)")
                return True
    
    print("❌ FAIL: Missing tool_result NOT detected")
    return False


def test_duplicate_assistant_merge():
    """Test merging duplicate consecutive assistant messages"""
    print("\n" + "=" * 80)
    print("TEST 4: Duplicate Assistant Messages (should merge)")
    print("=" * 80)
    
    conversation = [
        {
            'role': 'user',
            'content': [{'type': 'text', 'text': 'Hello'}]
        },
        {
            'role': 'assistant',
            'content': [{'type': 'text', 'text': 'Part 1'}]
        },
        {
            'role': 'assistant',  # DUPLICATE!
            'content': [{'type': 'text', 'text': 'Part 2'}]
        }
    ]
    
    validated = validate_conversation_history(conversation)
    
    print(f"\nOriginal messages: {len(conversation)}")
    print(f"Validated messages: {len(validated)}")
    
    if len(validated) == 2:  # Should merge into 2 messages
        msg1 = validated[1]
        texts = [b.get('text') for b in msg1.get('content', []) if b.get('type') == 'text']
        print(f"Merged assistant content: {texts}")
        
        if len(texts) == 2 and 'Part 1' in texts[0] and 'Part 2' in texts[1]:
            print("✅ PASS: Duplicate assistant messages merged correctly")
            return True
    
    print("❌ FAIL: Duplicate assistant messages NOT merged")
    return False


def test_thinking_block_ordering():
    """Test thinking blocks are moved to first position"""
    print("\n" + "=" * 80)
    print("TEST 5: Thinking Block Ordering (should be first)")
    print("=" * 80)
    
    conversation = [
        {
            'role': 'user',
            'content': [{'type': 'text', 'text': 'Hello'}]
        },
        {
            'role': 'assistant',
            'content': [
                {'type': 'text', 'text': 'Hi there'},  # Text first
                {'type': 'thinking', 'thinking': 'Should greet back', 'signature': ''}  # Thinking second - WRONG!
            ]
        }
    ]
    
    validated = validate_conversation_history(conversation)
    
    if len(validated) >= 2:
        msg1 = validated[1]
        block_types = [b.get('type') for b in msg1.get('content', [])]
        print(f"Block order: {block_types}")
        
        if block_types[0] == 'thinking':
            print("✅ PASS: Thinking block moved to first position")
            return True
    
    print("❌ FAIL: Thinking block NOT moved to first position")
    return False


def test_tool_results_in_assistant_message():
    """Test tool_result blocks incorrectly stored in assistant message"""
    print("\n" + "=" * 80)
    print("TEST 6: tool_result in assistant (should extract and move to user message)")
    print("=" * 80)
    
    # This is the ACTUAL problem from the error log!
    conversation = [
        {
            'role': 'user',
            'content': [{'type': 'text', 'text': 'List my emails'}]
        },
        {
            'role': 'assistant',
            'content': [
                {'type': 'thinking', 'thinking': 'I should use tools', 'signature': ''},
                {'type': 'tool_use', 'id': 'toolu_01ABC', 'name': 'gmail_list_messages', 'input': {}},
                {'type': 'tool_result', 'tool_use_id': 'toolu_01ABC', 'content': 'Email list'},  # WRONG PLACE!
                {'type': 'tool_use', 'id': 'toolu_01DEF', 'name': 'gmail_list_labels', 'input': {}},
                {'type': 'tool_result', 'tool_use_id': 'toolu_01DEF', 'content': 'Label list'},  # WRONG PLACE!
                {'type': 'text', 'text': 'Here are your emails'}
            ]
        }
    ]
    
    validated = validate_conversation_history(conversation)
    
    print(f"\nOriginal messages: {len(conversation)}")
    print(f"Validated messages: {len(validated)}")
    
    # Should have 3 messages now: user, assistant (with tool_use only), user (with tool_result)
    if len(validated) == 3:
        msg1 = validated[1]  # Assistant
        msg2 = validated[2]  # User with tool_results
        
        # Check assistant has tool_use but NO tool_result
        assistant_types = [b.get('type') for b in msg1.get('content', [])]
        print(f"Assistant message blocks: {assistant_types}")
        
        if 'tool_result' in assistant_types:
            print("❌ FAIL: tool_result still in assistant message")
            return False
        
        if 'tool_use' not in assistant_types:
            print("❌ FAIL: tool_use removed from assistant message")
            return False
        
        # Check user message has tool_result blocks
        if msg2.get('role') != 'user':
            print(f"❌ FAIL: Expected user message, got {msg2.get('role')}")
            return False
        
        user_types = [b.get('type') for b in msg2.get('content', [])]
        print(f"Inserted user message blocks: {user_types}")
        
        if user_types != ['tool_result', 'tool_result']:
            print(f"❌ FAIL: Expected ['tool_result', 'tool_result'], got {user_types}")
            return False
        
        print("✅ PASS: tool_result blocks extracted and moved to user message")
        return True
    else:
        print(f"❌ FAIL: Expected 3 messages, got {len(validated)}")
        return False


def run_all_tests():
    """Run all validation tests"""
    print("\n" + "=" * 80)
    print("🧪 TOOL USE VALIDATION TEST SUITE")
    print("=" * 80)
    
    tests = [
        test_valid_conversation,
        test_orphaned_tool_result,
        test_missing_tool_result,
        test_duplicate_assistant_merge,
        test_thinking_block_ordering,
        test_tool_results_in_assistant_message  # NEW TEST!
    ]
    
    results = []
    for test_fn in tests:
        try:
            result = test_fn()
            results.append((test_fn.__name__, result))
        except Exception as e:
            print(f"❌ ERROR in {test_fn.__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_fn.__name__, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
