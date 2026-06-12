"""
Test token counting for tool_result blocks
"""
import json
import tiktoken

# Simulate the content from message [16]
tool_result_content = [
    {
        "type": "text",
        "text": "x" * 380000  # Simulate 380K characters
    }
]

tool_result_block = {
    "type": "tool_result",
    "tool_use_id": "toolu_123",
    "content": tool_result_content
}

# Test current counting logic
encoder = tiktoken.get_encoding("cl100k_base")

# Method 1: Current buggy approach (str(block['content']))
method1_tokens = len(encoder.encode(str(tool_result_block['content'])))

# Method 2: Correct approach (recursively count nested blocks)
def count_tool_result_tokens(content):
    """Recursively count tokens in tool_result content"""
    if isinstance(content, str):
        return len(encoder.encode(content))
    elif isinstance(content, list):
        total = 0
        for item in content:
            if isinstance(item, dict):
                if 'text' in item:
                    total += len(encoder.encode(item['text']))
                elif 'content' in item:
                    total += count_tool_result_tokens(item['content'])
            elif isinstance(item, str):
                total += len(encoder.encode(item))
        return total
    elif isinstance(content, dict):
        return len(encoder.encode(json.dumps(content)))
    else:
        return len(encoder.encode(str(content)))

method2_tokens = count_tool_result_tokens(tool_result_block['content'])

print("\n" + "="*80)
print("TOKEN COUNTING COMPARISON")
print("="*80)
print(f"Tool result content: 380,000 characters")
print(f"Method 1 (str(content)): {method1_tokens:,} tokens (BUGGY)")
print(f"Method 2 (recursive count): {method2_tokens:,} tokens (CORRECT)")
print(f"Difference: {abs(method2_tokens - method1_tokens):,} tokens")
print("="*80 + "\n")

# Expected: method2_tokens should be ~271K (matching actual message [16])
# Expected: method1_tokens should be much smaller (bug causing undercounting)
