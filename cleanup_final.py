#!/usr/bin/env python3
"""Clean up all orphaned code after initMultiAgent function."""

from pathlib import Path

file_path = Path("UI/modules_internal/agents/agent-js.js")

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the pattern: function closing } followed by next comment block
# The initMultiAgent function should end with }
# Followed by the next function definition which starts with /**

# Split by the comment block that should mark the start of the next function
parts = content.split('\n/**\n * Load all deferred thread messages')

if len(parts) >= 2:
    before_comment = parts[0]
    after_comment_block = parts[1]
    
    # Find the last } in the "before" part - that's where initMultiAgent should end
    last_brace_idx = before_comment.rfind('\n}')
    
    if last_brace_idx > 0:
        # Keep everything up to and including the last }
        fixed_content = before_comment[:last_brace_idx + 2]  # +2 for \n}
        
        # Add back the comment block and everything after
        fixed_content += '\n\n/**\n * Load all deferred thread messages' + after_comment_block
        
        # Count the lines we're deleting
        original_lines = len(content.split('\n'))
        new_lines = len(fixed_content.split('\n'))
        deleted = original_lines - new_lines
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"Cleaned up successfully!")
        print(f"Deleted {deleted} lines of orphaned code")
        print(f"Original: {original_lines} lines")
        print(f"New: {new_lines} lines")
    else:
        print("Could not find function closing brace")
else:
    print("Could not find comment block marker")
