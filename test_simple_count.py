import tiktoken

encoder = tiktoken.get_encoding("cl100k_base")

# Test: Does str() on a large list undercount tokens?
large_text = "x" * 100000  # 100K chars
nested_list = [{"type": "text", "text": large_text}]

# Method 1: str(nested_list)
str_version = str(nested_list)
tokens_from_str = len(encoder.encode(str_version))

# Method 2: Direct text
tokens_from_text = len(encoder.encode(large_text))

print(f"Method 1 (str(list)): {tokens_from_str:,} tokens")
print(f"Method 2 (direct text): {tokens_from_text:,} tokens")
print(f"Ratio: {tokens_from_text / tokens_from_str:.2f}x undercounting")
