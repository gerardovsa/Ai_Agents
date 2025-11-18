"""
Test Tool Use / Tool Result Validation Fix

Tests the ID matching validation added to prevent API errors
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from core.combined_agent_worker import validate_and_reorder_assistant_content, validate_conversation_history

# Test Case 1: VALID - Matching tool_use and tool_result IDs
print("\n" + "="*80)
print("TEST 1: VALID - Matching tool_use and tool_result IDs")
print("="*80)

valid_content = [
    {'type': 'tool_use', 'id': 'toolu_123', 'name': 'test_tool', 'input': {}},
    {'type': 'tool_result', 'tool_use_id': 'toolu_123', 'content': 'result1'},
    {'type': 'tool_use', 'id': 'toolu_456', 'name': 'test_tool2', 'input': {}},
    {'type': 'tool_result', 'tool_use_id': 'toolu_456', 'content': 'result2'},
    {'type': 'text', 'text': 'Done!'}
]

validated, extracted = validate_and_reorder_assistant_content(valid_content)

print(f"\nResults:")
print(f"  Validated blocks: {len(validated)}")
print(f"  Extracted tool_results: {len(extracted)}")
print(f"  Expected: 3 validated (2 tool_use + 1 text), 2 extracted tool_results")

if len(validated) == 3 and len(extracted) == 2:
    print("✅ TEST 1 PASSED: Valid content processed correctly")
else:
    print("❌ TEST 1 FAILED")

# Test Case 2: INVALID - Mismatched tool_use and tool_result IDs
print("\n" + "="*80)
print("TEST 2: INVALID - Mismatched tool_use and tool_result IDs")
print("="*80)

invalid_content = [
    {'type': 'tool_use', 'id': 'toolu_NEW_123', 'name': 'test_tool', 'input': {}},
    {'type': 'tool_result', 'tool_use_id': 'toolu_OLD_456', 'content': 'result1'},  # WRONG ID!
    {'type': 'tool_use', 'id': 'toolu_NEW_789', 'name': 'test_tool2', 'input': {}},
    {'type': 'tool_result', 'tool_use_id': 'toolu_OLD_999', 'content': 'result2'},  # WRONG ID!
    {'type': 'text', 'text': 'Done!'}
]

validated, extracted = validate_and_reorder_assistant_content(invalid_content)

print(f"\nResults:")
print(f"  Validated blocks: {len(validated)}")
print(f"  Extracted tool_results: {len(extracted)}")
print(f"  Expected: 0 validated, 0 extracted (conversation truncated to prevent API error)")

if len(validated) == 0 and len(extracted) == 0:
    print("✅ TEST 2 PASSED: Invalid content detected and conversation truncated")
else:
    print("❌ TEST 2 FAILED: Should have returned empty lists!")

# Test Case 3: PARTIAL MISMATCH - Some tool_use IDs missing tool_results
print("\n" + "="*80)
print("TEST 3: PARTIAL MISMATCH - Some tool_use IDs missing tool_results")
print("="*80)

partial_content = [
    {'type': 'tool_use', 'id': 'toolu_AAA', 'name': 'test_tool', 'input': {}},
    {'type': 'tool_result', 'tool_use_id': 'toolu_AAA', 'content': 'result1'},  # MATCHES
    {'type': 'tool_use', 'id': 'toolu_BBB', 'name': 'test_tool2', 'input': {}},
    # NO tool_result for toolu_BBB - will cause API error!
    {'type': 'text', 'text': 'Done!'}
]

validated, extracted = validate_and_reorder_assistant_content(partial_content)

print(f"\nResults:")
print(f"  Validated blocks: {len(validated)}")
print(f"  Extracted tool_results: {len(extracted)}")
print(f"  Expected: 0 validated, 0 extracted (missing tool_result detected)")

if len(validated) == 0 and len(extracted) == 0:
    print("✅ TEST 3 PASSED: Missing tool_result detected and conversation truncated")
else:
    print("❌ TEST 3 FAILED: Should have detected missing tool_result!")

# Test Case 4: FULL CONVERSATION VALIDATION
print("\n" + "="*80)
print("TEST 4: FULL CONVERSATION VALIDATION")
print("="*80)

conversation = [
    {
        'role': 'user',
        'content': [{'type': 'text', 'text': 'Hello'}]
    },
    {
        'role': 'assistant',
        'content': [
            {'type': 'tool_use', 'id': 'toolu_VALID_1', 'name': 'tool1', 'input': {}},
            {'type': 'tool_result', 'tool_use_id': 'toolu_VALID_1', 'content': 'ok'},
            {'type': 'text', 'text': 'Processing...'}
        ]
    },
    {
        'role': 'user',
        'content': [{'type': 'text', 'text': 'Continue'}]
    },
    {
        'role': 'assistant',
        'content': [
            {'type': 'tool_use', 'id': 'toolu_MISMATCH_1', 'name': 'tool2', 'input': {}},
            {'type': 'tool_result', 'tool_use_id': 'toolu_WRONG_ID', 'content': 'ok'},  # WRONG!
            {'type': 'text', 'text': 'Done'}
        ]
    }
]

validated_conv = validate_conversation_history(conversation)

print(f"\nResults:")
print(f"  Original conversation: {len(conversation)} messages")
print(f"  Validated conversation: {len(validated_conv)} messages")
print(f"  Expected: 3 messages (last message with mismatch should be removed)")

if len(validated_conv) <= 3:
    print("✅ TEST 4 PASSED: Malformed assistant message removed from conversation")
else:
    print("❌ TEST 4 FAILED: Malformed message not removed!")

# Summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print("These tests verify that the ID matching validation prevents API errors")
print("by truncating conversations when tool_use/tool_result IDs don't match.")
print("\nThe fix should:")
print("  1. Allow valid conversations with matching IDs")
print("  2. Truncate conversations with mismatched IDs")
print("  3. Detect partial mismatches (missing tool_results)")
print("  4. Remove malformed messages from conversation history")
