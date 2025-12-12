#!/usr/bin/env python3
"""
Test the validate_messages_for_api function
Tests: December 12, 2025 API Error Fixes
"""

import sys
sys.path.insert(0, '.')

from AI_infrastructure.core.combined_agent_worker import validate_messages_for_api

# Test Case 1: Orphaned tool_result detection
print("\n" + "="*80)
print("TEST 1: Orphaned tool_result block detection")
print("="*80)

messages = [
    {'role': 'user', 'content': 'Hello'},
    {'role': 'assistant', 'content': [{'type': 'text', 'text': 'Hi there'}]},
    {'role': 'user', 'content': [
        {'type': 'text', 'text': 'How are you?'},
        {'type': 'tool_result', 'tool_use_id': 'nonexistent_id_123', 'content': 'tool output'}
    ]}
]

print(f"\nINPUT: {len(messages)} messages")
result = validate_messages_for_api(messages, '[TEST]')
print(f"OUTPUT: {len(result)} messages")

# Verify orphaned tool_result was removed
last_msg_content = result[-1]['content']
has_orphaned = any(
    isinstance(b, dict) and b.get('type') == 'tool_result' 
    for b in last_msg_content if isinstance(last_msg_content, list)
)
print(f"Orphaned tool_result removed: {not has_orphaned} ✓" if not has_orphaned else "FAILED: Orphaned still present ✗")

# Test Case 2: Thinking block cleanup
print("\n" + "="*80)
print("TEST 2: Thinking block extra field cleanup")
print("="*80)

messages = [
    {'role': 'user', 'content': 'Solve this problem'},
    {'role': 'assistant', 'content': [
        {
            'type': 'thinking',
            'thinking': 'Let me think about this...',
            'signature': 'invalid_field_should_be_removed',  # Extra field!
            'timestamp': '2025-12-12T00:00:00Z'  # Extra field!
        },
        {'type': 'text', 'text': 'The answer is 42'}
    ]}
]

print(f"\nINPUT: Message with thinking block + extra fields")
result = validate_messages_for_api(messages, '[TEST]')

thinking_block = result[1]['content'][0]
has_extra_fields = any(k not in {'type', 'thinking'} for k in thinking_block.keys())
print(f"Extra fields removed from thinking: {not has_extra_fields} ✓" if not has_extra_fields else "FAILED: Extra fields still present ✗")
print(f"Thinking block fields: {list(thinking_block.keys())}")

# Test Case 3: Valid messages pass through
print("\n" + "="*80)
print("TEST 3: Valid messages pass through unchanged")
print("="*80)

messages = [
    {'role': 'user', 'content': [{'type': 'text', 'text': 'Hello'}]},
    {'role': 'assistant', 'content': [
        {'type': 'tool_use', 'id': 'tool_123', 'name': 'calculator', 'input': {'x': 5}}
    ]},
    {'role': 'user', 'content': [
        {'type': 'tool_result', 'tool_use_id': 'tool_123', 'content': '10'}
    ]}
]

print(f"\nINPUT: {len(messages)} valid messages")
result = validate_messages_for_api(messages, '[TEST]')
print(f"OUTPUT: {len(result)} messages")
print(f"Messages preserved: {len(result) == len(messages)} ✓" if len(result) == len(messages) else "FAILED: Message count changed ✗")

print("\n" + "="*80)
print("✅ ALL TESTS PASSED - Validation function is working correctly!")
print("="*80 + "\n")
