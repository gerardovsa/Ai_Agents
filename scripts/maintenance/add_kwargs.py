#!/usr/bin/env python3
"""
Add **kwargs to all word_ functions that are missing it
"""
import re

# Read file
with open('microsoft_word_tools.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if this is a word_ function definition
    if re.match(r'\s*def word_\w+\(', line):
        # Collect the full function signature (could span multiple lines)
        func_lines = [line]
        j = i + 1
        while j < len(lines) and not lines[j].strip().startswith('"""'):
            func_lines.append(lines[j])
            if ')' in lines[j]:
                break
            j += 1
        
        # Join the signature
        full_sig = ''.join(func_lines)
        
        # Check if **kwargs is already in signature
        if '**kwargs' not in full_sig:
            # Find where to insert **kwargs (before the closing ):)
            # Need to handle both single line and multi-line
            last_func_line_idx = len(func_lines) - 1
            last_line = func_lines[last_func_line_idx]
            
            # Find the ) -> or ): pattern
            if ') ->' in last_line:
                func_lines[last_func_line_idx] = last_line.replace(') ->', ', **kwargs) ->')
            elif '):' in last_line:
                func_lines[last_func_line_idx] = last_line.replace('):', ', **kwargs):')
            
            # Add modified lines
            output_lines.extend(func_lines)
            i = j
        else:
            # Already has **kwargs, keep as is
            output_lines.extend(func_lines)
            i = j
    else:
        output_lines.append(line)
        i += 1

# Write back
with open('microsoft_word_tools.py', 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print(' Added **kwargs to all word_ functions')
