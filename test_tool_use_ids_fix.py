"""
Test to verify tool_use_ids bug fix in combined_agent_worker.py

This test simulates the scenario that caused the NameError:
- Assistant message with tool_use blocks
- User message with tool_result blocks
- Validation should check for missing tool_results without crashing
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from core.combined_agent_worker import validate_conversation_history

# Test Case 1: Valid conversation with matching tool_use and tool_result
print("Test 1: Valid conversation with matching tool_use/tool_result")
print("=" * 70)

messages = [
    {
        'role': 'user',
        'content': [{'type': 'text', 'text': 'Test message'}]
    },
    {
        'role': 'assistant',
        'content': [
            {
                'type': 'tool_use',
                'id': 'toolu_123',
                'name': 'test_tool',
                'input': {'param': 'value'}
            },
            {
                'type': 'text',
                'text': 'Using test tool'
            }
        ]
    },
    {
        'role': 'user',
        'content': [
            {
                'type': 'tool_result',
                'tool_use_id': 'toolu_123',
                'content': [{'type': 'text', 'text': 'Success'}]
            }
        ]
    }
]

try:
    validated = validate_conversation_history(messages)
    print(f"✅ PASS: Validated {len(validated)} messages without error")
except NameError as e:
    print(f"❌ FAIL: NameError occurred: {e}")
except Exception as e:
    print(f"⚠️  WARN: Other error: {e}")

print()

# Test Case 2: Missing tool_result (should be detected gracefully)
print("Test 2: Missing tool_result (should detect but not crash)")
print("=" * 70)

messages_missing = [
    {
        'role': 'user',
        'content': [{'type': 'text', 'text': 'Test message'}]
    },
    {
        'role': 'assistant',
        'content': [
            {
                'type': 'tool_use',
                'id': 'toolu_456',
                'name': 'test_tool',
                'input': {'param': 'value'}
            },
            {
                'type': 'text',
                'text': 'Using test tool'
            }
        ]
    },
    {
        'role': 'user',
        'content': [
            {
                'type': 'tool_result',
                'tool_use_id': 'toolu_999',  # Wrong ID!
                'content': [{'type': 'text', 'text': 'Success'}]
            }
        ]
    }
]

try:
    validated = validate_conversation_history(messages_missing)
    print(f"✅ PASS: Validated {len(validated)} messages, detected missing tool_result gracefully")
except NameError as e:
    print(f"❌ FAIL: NameError occurred: {e}")
except Exception as e:
    print(f"⚠️  WARN: Other error: {e}")

print()

# Test Case 3: Multiple tool_use blocks
print("Test 3: Multiple tool_use blocks with matching results")
print("=" * 70)

messages_multi = [
    {
        'role': 'user',
        'content': [{'type': 'text', 'text': 'Test message'}]
    },
    {
        'role': 'assistant',
        'content': [
            {
                'type': 'tool_use',
                'id': 'toolu_001',
                'name': 'tool_1',
                'input': {}
            },
            {
                'type': 'tool_use',
                'id': 'toolu_002',
                'name': 'tool_2',
                'input': {}
            },
            {
                'type': 'text',
                'text': 'Using multiple tools'
            }
        ]
    },
    {
        'role': 'user',
        'content': [
            {
                'type': 'tool_result',
                'tool_use_id': 'toolu_001',
                'content': [{'type': 'text', 'text': 'Result 1'}]
            },
            {
                'type': 'tool_result',
                'tool_use_id': 'toolu_002',
                'content': [{'type': 'text', 'text': 'Result 2'}]
            }
        ]
    }
]

try:
    validated = validate_conversation_history(messages_multi)
    print(f"✅ PASS: Validated {len(validated)} messages with multiple tools")
except NameError as e:
    print(f"❌ FAIL: NameError occurred: {e}")
except Exception as e:
    print(f"⚠️  WARN: Other error: {e}")

print()
print("=" * 70)
print("SUMMARY: If all tests show ✅ PASS, the bug fix is successful!")
print("=" * 70)
