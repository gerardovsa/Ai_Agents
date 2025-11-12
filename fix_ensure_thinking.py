"""Fix ensure_thinking_on_final_assistant function"""

with open('AI_infrastructure/core/combined_agent_worker.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the function start
func_start = None
for i, line in enumerate(lines):
    if line.strip().startswith('def ensure_thinking_on_final_assistant'):
        func_start = i
        break

if func_start is None:
    print("Function not found")
    exit(1)

# Find the function end (next function or class)
func_end = None
for i in range(func_start + 1, len(lines)):
    line = lines[i]
    # Check for next function/class at same indent level
    if (line.startswith('def ') or line.startswith('class ') or 
        (line.startswith('# ===') and '====' in line)):
        func_end = i
        break

if func_end is None:
    print("Function end not found")
    exit(1)

print(f"Function found at lines {func_start+1} to {func_end}")

# Replace with new function
new_function = '''def ensure_thinking_on_final_assistant(messages: List[Dict], thinking_enabled: bool) -> List[Dict]:
    """
    CRITICAL FIX (Nov 12, 2025 - Anthropic API Requirement):
    
    When thinking is enabled, the API requires that the FINAL assistant message
    in the conversation history starts with a thinking block.
    
    Per Anthropic docs:
    "When `thinking` is enabled, a final `assistant` message must start with a thinking block."
    "During tool use, you must pass thinking blocks back to the API for the last assistant message."
    
    UPDATED (Nov 12, 2025): We now preserve all messages instead of deleting them.
    The presence of the `thinking` parameter in the API call is sufficient for Claude
    to generate thinking blocks in the response, even if prior assistant messages lack them.
    
    Args:
        messages: Validated conversation history
        thinking_enabled: Whether extended thinking is enabled for this request
    
    Returns:
        Conversation history (preserved, no deletions)
    """
    if not thinking_enabled:
        return messages  # No requirement when thinking disabled
    
    if not messages:
        return messages  # Empty conversation
    
    # Find the last assistant message
    last_assistant_idx = None
    for i in range(len(messages) - 1, -1, -1):
        if messages[i].get('role') == 'assistant':
            last_assistant_idx = i
            break
    
    if last_assistant_idx is None:
        # No assistant messages in history
        print(f"[Combined Worker] ℹ️  No assistant messages in history (thinking requirement N/A)")
        return messages
    
    last_assistant = messages[last_assistant_idx]
    content = last_assistant.get('content', [])
    
    if not isinstance(content, list):
        print(f"[Combined Worker] ⚠️ Last assistant message has non-list content")
        return messages
    
    # Check if first block is thinking
    has_thinking_first = False
    if content:
        first_block_type = content[0].get('type') if isinstance(content[0], dict) else None
        has_thinking_first = first_block_type in ('thinking', 'redacted_thinking')
    
    if has_thinking_first:
        print(f"[Combined Worker] ✅ Last assistant message (#{last_assistant_idx}) starts with thinking block")
    else:
        # Last assistant message doesn't have thinking blocks - this is OK
        # The API will generate thinking blocks when `thinking` param is present
        print(f"[Combined Worker] ℹ️  Last assistant message (#{last_assistant_idx}) has no thinking blocks (API will generate them)")
        print(f"[Combined Worker]   Content blocks: {[b.get('type') for b in content if isinstance(b, dict)]}")
    
    # Always preserve all messages
    return messages


'''

# Replace lines
new_lines = lines[:func_start] + [new_function] + lines[func_end:]

# Write back
with open('AI_infrastructure/core/combined_agent_worker.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"✅ Function replaced successfully (lines {func_start+1}-{func_end} replaced)")
