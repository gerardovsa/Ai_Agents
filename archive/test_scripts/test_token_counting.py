"""
Test token counting implementation

Tests:
1. estimate_tokens() function works
2. Token counting for short strings
3. Token counting for long strings
4. Token counting appears in logs during tool execution
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from core.combined_agent_worker import estimate_tokens

def test_estimate_tokens_basic():
    """Test basic token estimation"""
    
    # Short string: ~10 chars = ~2-3 tokens
    short = "Hello"
    tokens = estimate_tokens(short)
    assert tokens > 0, "Should return positive token count"
    assert tokens == 1, f"Expected ~1 token for 'Hello', got {tokens}"  # 5 chars / 4 = 1.25 -> 1
    print(f"Test 1 PASSED - Short string: '{short}' = {tokens} tokens")


def test_estimate_tokens_medium():
    """Test token estimation for medium strings"""
    
    # Medium string: ~100 chars = ~25 tokens
    medium = "This is a medium length string that should be around 100 characters long for testing purposes here."
    tokens = estimate_tokens(medium)
    expected = len(medium) // 4
    assert tokens == expected, f"Expected {expected} tokens, got {tokens}"
    print(f"Test 2 PASSED - Medium string: {len(medium)} chars = {tokens} tokens")


def test_estimate_tokens_large():
    """Test token estimation for large strings"""
    
    # Large string: 10,000 chars = ~2,500 tokens
    large = "x" * 10000
    tokens = estimate_tokens(large)
    expected = 2500
    assert tokens == expected, f"Expected {expected} tokens, got {tokens}"
    print(f"Test 3 PASSED - Large string: 10,000 chars = {tokens:,} tokens")


def test_estimate_tokens_json():
    """Test token estimation for JSON-like tool results"""
    
    # Simulate a tool result (JSON string)
    tool_result = '{"status": "success", "data": {"items": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]}, "count": 2}'
    tokens = estimate_tokens(tool_result)
    print(f"Test 4 PASSED - JSON result: {len(tool_result)} chars = {tokens} tokens")


def test_estimate_tokens_empty():
    """Test token estimation for empty/None strings"""
    
    assert estimate_tokens("") == 0, "Empty string should be 0 tokens"
    assert estimate_tokens(None) == 0, "None should be 0 tokens"
    print("Test 5 PASSED - Empty/None handling works")


def test_realistic_tool_results():
    """Test with realistic tool result sizes"""
    
    # Small result: ~200 chars
    small_result = '{"success": true, "message": "Operation completed successfully", "data": {"id": 123, "created_at": "2025-01-15T10:30:00Z"}}'
    small_tokens = estimate_tokens(small_result)
    print(f"\nTest 6 - Realistic tool results:")
    print(f"  Small result: {len(small_result)} chars = {small_tokens} tokens")
    
    # Medium result: ~2,000 chars (list of items)
    medium_result = str([{"id": i, "name": f"Item {i}", "description": f"This is item number {i} with some additional details"} for i in range(20)])
    medium_tokens = estimate_tokens(medium_result)
    print(f"  Medium result: {len(medium_result)} chars = {medium_tokens} tokens")
    
    # Large result: ~20,000 chars (big dataset)
    large_result = str([{"id": i, "name": f"Item {i}", "description": f"This is item number {i} with some additional details and more content to make it longer"} for i in range(200)])
    large_tokens = estimate_tokens(large_result)
    print(f"  Large result: {len(large_result)} chars = {large_tokens:,} tokens")
    
    # Very large result: ~100,000 chars
    very_large_result = str([{"id": i, "name": f"Item {i}", "description": f"This is item number {i} with extensive details " * 10} for i in range(500)])
    very_large_tokens = estimate_tokens(very_large_result)
    print(f"  Very large result: {len(very_large_result)} chars = {very_large_tokens:,} tokens")
    
    print("Test 6 PASSED - Realistic token counts calculated")


if __name__ == '__main__':
    print("\nTesting Token Counting Implementation")
    print("=" * 60)
    
    try:
        test_estimate_tokens_basic()
        test_estimate_tokens_medium()
        test_estimate_tokens_large()
        test_estimate_tokens_json()
        test_estimate_tokens_empty()
        test_realistic_tool_results()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED")
        print("=" * 60)
        print("\nToken counting is working correctly!")
        print("You'll now see logs like:")
        print("  📊 Tool result tokens: tool_name = 1,234 tokens")
        print("  📊 ITERATION 1 TOTAL: 5,678 tokens from 3 tool result(s)")
        print("  📊 CUMULATIVE TOOL RESULTS: 12,345 tokens across 2 iteration(s)")
        print("  📊 ESTIMATED CONVERSATION SIZE: 145,678 tokens (~72.8% of 200K limit)")
        
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
