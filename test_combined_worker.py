"""
Combined Agent Worker - Comprehensive Test Suite
Tests all functions and validates the 7 critical fixes

Test Categories:
1. Import Tests - Verify all exports available
2. Validation Tests - Test the 7 critical fixes
3. Smoke Tests - End-to-end worker execution
"""

import sys
import os
from pathlib import Path

# Setup paths
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir / "AI_infrastructure"))
sys.path.insert(0, str(root_dir / "tools"))

print("=" * 80)
print("COMBINED AGENT WORKER - TEST SUITE")
print("=" * 80)
print()

# ============================================================
# TEST 1: IMPORT TESTS
# ============================================================
print("[TEST 1] IMPORT TESTS")
print("-" * 80)

try:
    from core.combined_agent_worker import (
        run_agent_worker,
        run_simple_agent_worker, 
        agent_worker,
        execute_streaming_request,
        validate_conversation_history,
        validate_and_reorder_assistant_content,
        validate_user_content
    )
    print("✅ All imports successful")
    print(f"   - run_agent_worker: {type(run_agent_worker)}")
    print(f"   - run_simple_agent_worker: {type(run_simple_agent_worker)}")
    print(f"   - agent_worker: {type(agent_worker)}")
    print(f"   - execute_streaming_request: {type(execute_streaming_request)}")
    print(f"   - validate_conversation_history: {type(validate_conversation_history)}")
    print(f"   - validate_and_reorder_assistant_content: {type(validate_and_reorder_assistant_content)}")
    print(f"   - validate_user_content: {type(validate_user_content)}")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

print()

# ============================================================
# TEST 2: VALIDATION FUNCTION TESTS
# ============================================================
print("[TEST 2] VALIDATION FUNCTION TESTS")
print("-" * 80)

# Test 2.1: Thinking Block Ordering
print("\n[2.1] Thinking Block Ordering Fix")
assistant_content_bad = [
    {"type": "text", "text": "I'll help you with that"},
    {"type": "thinking", "thinking": "Analyzing request", "signature": ""}
]
assistant_content_fixed = validate_and_reorder_assistant_content(assistant_content_bad)
if assistant_content_fixed[0]["type"] in ("thinking", "redacted_thinking"):
    print("✅ Thinking blocks moved to first position")
else:
    print("❌ Thinking blocks NOT properly reordered")

# Test 2.2: tool_result Removal from Assistant
print("\n[2.2] tool_result Removal from Assistant Messages")
assistant_with_tool_result = [
    {"type": "text", "text": "Result"},
    {"type": "tool_result", "tool_use_id": "123", "content": "data"}
]
cleaned = validate_and_reorder_assistant_content(assistant_with_tool_result)
has_tool_result = any(b.get("type") == "tool_result" for b in cleaned)
if not has_tool_result:
    print("✅ tool_result blocks removed from assistant message")
else:
    print("❌ tool_result blocks NOT removed")

# Test 2.3: Orphaned tool_result Detection
print("\n[2.3] Orphaned tool_result Detection (Backwards Search)")
conversation_with_orphan = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": [{"type": "text", "text": "Hi"}]},
    {"role": "user", "content": "Do task"},
    {"role": "assistant", "content": [{"type": "tool_use", "id": "call_123", "name": "test_tool", "input": {}}]},
    {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "call_999", "content": "orphaned"}]}
]
validated_conv = validate_conversation_history(conversation_with_orphan)
last_user_msg = validated_conv[-1]
has_orphan = any(
    b.get("type") == "tool_result" and b.get("tool_use_id") == "call_999" 
    for b in (last_user_msg["content"] if isinstance(last_user_msg["content"], list) else [])
)
if not has_orphan:
    print("✅ Orphaned tool_result detected and removed")
else:
    print("❌ Orphaned tool_result NOT detected")

# Test 2.4: String to Blocks Conversion
print("\n[2.4] String Content Conversion")
conversation_with_strings = [
    {"role": "user", "content": "Hello world"},
    {"role": "assistant", "content": "Hi there"}
]
validated = validate_conversation_history(conversation_with_strings)
all_lists = all(isinstance(msg["content"], list) for msg in validated)
if all_lists:
    print("✅ String content converted to blocks format")
else:
    print("❌ String content NOT converted")

# Test 2.5: Missing Signature Field
print("\n[2.5] Signature Field Validation")
thinking_no_sig = [{"type": "thinking", "thinking": "Analyzing..."}]
fixed = validate_and_reorder_assistant_content(thinking_no_sig)
has_signature = "signature" in fixed[0]
if has_signature:
    print("✅ Missing signature field added to thinking block")
else:
    print("❌ Signature field NOT added")

# Test 2.6: Duplicate Role Detection
print("\n[2.6] Duplicate Consecutive Role Detection")
conversation_duplicate_roles = [
    {"role": "user", "content": "First message"},
    {"role": "user", "content": "Second message"},
    {"role": "assistant", "content": "Response"}
]
validated = validate_conversation_history(conversation_duplicate_roles)
if len(validated) == 2 and validated[0]["role"] == "user" and validated[1]["role"] == "assistant":
    print("✅ Duplicate user roles merged into single message")
else:
    print(f"❌ Duplicate roles NOT properly handled (got {len(validated)} messages)")

# Test 2.7: Block Field Validation
print("\n[2.7] Block Field Validation")
invalid_blocks = [
    {"type": "text"},  # Missing 'text' field
    {"type": "tool_use", "name": "test"},  # Missing 'id' and 'input'
    {"type": "thinking"},  # Missing 'thinking' field
    {"type": "text", "text": "Valid"}
]
cleaned = validate_and_reorder_assistant_content(invalid_blocks)
if len(cleaned) == 1 and cleaned[0]["type"] == "text":
    print("✅ Invalid blocks removed, valid blocks preserved")
else:
    print(f"❌ Block field validation failed (got {len(cleaned)} blocks, expected 1)")

print()

# ============================================================
# TEST 3: SMOKE TESTS (Registry Required)
# ============================================================
print("[TEST 3] SMOKE TESTS")
print("-" * 80)

try:
    from tools.registry_v3 import get_registry
    registry = get_registry()
    print(f"✅ Registry loaded: {len(registry.tools)} tools available")
except Exception as e:
    print(f"⚠️  Registry not available: {e}")
    print("   Skipping smoke tests (registry required)")
    registry = None

if registry:
    # Test 3.1: Simple Worker Function Signature
    print("\n[3.1] Worker Function Signatures")
    import inspect
    
    # Check run_agent_worker signature
    sig = inspect.signature(run_agent_worker)
    params = list(sig.parameters.keys())
    expected = ['user_id', 'message', 'session_id', 'message_queue', 'conversation_history', 'uploaded_files']
    if all(p in params for p in expected):
        print(f"✅ run_agent_worker signature valid: {params[:6]}")
    else:
        print(f"❌ run_agent_worker signature invalid")
    
    # Check run_simple_agent_worker signature
    sig = inspect.signature(run_simple_agent_worker)
    params = list(sig.parameters.keys())
    expected = ['user_id', 'message', 'session_id', 'conversation_history']
    if all(p in params for p in expected):
        print(f"✅ run_simple_agent_worker signature valid: {params[:4]}")
    else:
        print(f"❌ run_simple_agent_worker signature invalid")
    
    # Check agent_worker signature
    sig = inspect.signature(agent_worker)
    params = list(sig.parameters.keys())
    expected = ['user_id', 'message', 'conversation_history']
    if all(p in params for p in expected):
        print(f"✅ agent_worker signature valid: {params[:3]}")
    else:
        print(f"❌ agent_worker signature invalid")
    
    # Check execute_streaming_request signature
    sig = inspect.signature(execute_streaming_request)
    params = list(sig.parameters.keys())
    expected = ['user_id', 'message', 'conversation_history']
    if all(p in params for p in expected):
        print(f"✅ execute_streaming_request signature valid: {params[:3]}")
    else:
        print(f"❌ execute_streaming_request signature invalid")

print()

# ============================================================
# SUMMARY
# ============================================================
print("=" * 80)
print("TEST SUITE COMPLETE")
print("=" * 80)
print()
print("NEXT STEPS:")
print("1. Update agent_routes_v4.py imports to use combined_agent_worker")
print("2. Restart Flask server (BISTART)")
print("3. Test with live requests:")
print("   - CHAT 'Hello' (simple test)")
print("   - CHAT 'List my Gmail messages' (tool execution)")
print("   - Multi-round conversation (validation test)")
print()
print("ROLLBACK PLAN:")
print("If issues occur, revert imports in agent_routes_v4.py:")
print("   from core.agent_worker import ...")
print("   from core.streaming_agent_worker import ...")
print()
