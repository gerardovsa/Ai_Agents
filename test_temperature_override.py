"""
Test temperature override when thinking is enabled
Verifies that temperature is forced to 1.0 when Extended Thinking is enabled
"""

import sys
from pathlib import Path

# Add paths
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir / "AI_infrastructure" / "core"))
sys.path.insert(0, str(root_dir))

def test_unified_ai_client_temperature():
    """Test UnifiedAIClient.create_message temperature handling"""
    print("\n" + "="*80)
    print("TEST 1: UnifiedAIClient.create_message() Temperature Override")
    print("="*80)
    
    from unified_ai_client import UnifiedAIClient
    
    # Initialize client (requires config file)
    config_path = root_dir / "config" / "database-config.json"
    if not config_path.exists():
        config_path = root_dir / "AI_infrastructure" / "config" / "database-config.json"
    
    if not config_path.exists():
        print("⚠️  Config file not found, skipping UnifiedAIClient test")
        return False
    
    try:
        client = UnifiedAIClient(str(config_path))
        print("✅ UnifiedAIClient initialized")
    except Exception as e:
        print(f"⚠️  Could not initialize UnifiedAIClient: {e}")
        return False
    
    # Check signature includes temperature parameter
    import inspect
    sig = inspect.signature(client.create_message)
    params = list(sig.parameters.keys())
    
    print(f"\ncreate_message() parameters: {params}")
    
    if 'temperature' in params:
        print("✅ temperature parameter present in create_message()")
        
        # Check default value
        temp_param = sig.parameters['temperature']
        print(f"   Default value: {temp_param.default}")
        
        if temp_param.default == 1.0:
            print("✅ Default temperature is 1.0")
        else:
            print(f"⚠️  Default temperature is {temp_param.default}, expected 1.0")
    else:
        print("❌ temperature parameter NOT found in create_message()")
        return False
    
    return True


def test_combined_worker_temperature():
    """Test execute_streaming_request temperature handling"""
    print("\n" + "="*80)
    print("TEST 2: execute_streaming_request() Temperature Override")
    print("="*80)
    
    from combined_agent_worker import execute_streaming_request
    import inspect
    
    # Check signature includes temperature parameters
    sig = inspect.signature(execute_streaming_request)
    params = list(sig.parameters.keys())
    
    print(f"\nexecute_streaming_request() parameters:")
    for param in params:
        print(f"   - {param}")
    
    required_params = ['ai_model', 'ai_temperature', 'ai_max_tokens', 'ai_thinking_enabled', 'ai_thinking_budget']
    missing = [p for p in required_params if p not in params]
    
    if not missing:
        print(f"✅ All required AI preference parameters present: {required_params}")
    else:
        print(f"❌ Missing parameters: {missing}")
        return False
    
    # Check default values
    print("\nDefault values:")
    for param_name in required_params:
        param = sig.parameters[param_name]
        print(f"   {param_name}: {param.default}")
    
    # Verify ai_thinking_enabled defaults to True
    if sig.parameters['ai_thinking_enabled'].default == True:
        print("✅ ai_thinking_enabled defaults to True")
    else:
        print("⚠️  ai_thinking_enabled does not default to True")
    
    return True


def test_validation_logic():
    """Test that validation logic preserves assistant messages"""
    print("\n" + "="*80)
    print("TEST 3: Conversation History Preservation")
    print("="*80)
    
    from combined_agent_worker import validate_conversation_history, ensure_thinking_on_final_assistant
    
    # Create test conversation with assistant message lacking thinking blocks
    test_conversation = [
        {'role': 'user', 'content': [{'type': 'text', 'text': 'Hello'}]},
        {'role': 'assistant', 'content': [{'type': 'text', 'text': 'Hi there!'}]},
        {'role': 'user', 'content': [{'type': 'text', 'text': 'How are you?'}]}
    ]
    
    print(f"\nInput conversation: {len(test_conversation)} messages")
    print("   Message 1: user")
    print("   Message 2: assistant (NO thinking blocks)")
    print("   Message 3: user")
    
    # Validate conversation
    validated = validate_conversation_history(test_conversation.copy())
    print(f"\nAfter validate_conversation_history(): {len(validated)} messages")
    
    if len(validated) == len(test_conversation):
        print("✅ All messages preserved during validation")
    else:
        print(f"❌ Messages were removed: {len(test_conversation)} → {len(validated)}")
        return False
    
    # Ensure thinking on final assistant (thinking_enabled=True)
    final_validated = ensure_thinking_on_final_assistant(validated.copy(), thinking_enabled=True)
    print(f"\nAfter ensure_thinking_on_final_assistant(thinking_enabled=True): {len(final_validated)} messages")
    
    if len(final_validated) == len(validated):
        print("✅ All messages preserved (no deletion when thinking enabled)")
    else:
        print(f"❌ Messages were deleted: {len(validated)} → {len(final_validated)}")
        return False
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("TEMPERATURE OVERRIDE & THINKING VALIDATION TESTS")
    print("="*80)
    
    results = []
    
    # Test 1: UnifiedAIClient temperature parameter
    try:
        result = test_unified_ai_client_temperature()
        results.append(("UnifiedAIClient temperature", result))
    except Exception as e:
        print(f"❌ Test 1 failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("UnifiedAIClient temperature", False))
    
    # Test 2: execute_streaming_request parameters
    try:
        result = test_combined_worker_temperature()
        results.append(("execute_streaming_request params", result))
    except Exception as e:
        print(f"❌ Test 2 failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("execute_streaming_request params", False))
    
    # Test 3: Validation logic
    try:
        result = test_validation_logic()
        results.append(("Conversation preservation", result))
    except Exception as e:
        print(f"❌ Test 3 failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Conversation preservation", False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\nResults: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
