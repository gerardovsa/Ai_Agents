"""
Fix ALL indentation issues in validation blocks
"""

from pathlib import Path
import re

wrapper_file = Path("UI/modules_external/quote-calculator/implementations/calculator_wrapper.py")
content = wrapper_file.read_text(encoding='utf-8')

# Pattern to find validation blocks with wrong indentation (spaces not 4)
# Look for validation that starts with spaces not divisible by 4
pattern = r'(^(\s+))# Check for typos in parameter names.*?\n\2typo_error = _validate_no_typos.*?\n\2if typo_error:\n\2    return typo_error\n'

# Fix indentation - ensure it's always 4 spaces (one indent level inside function)
def fix_indent(match):
    old_indent = match.group(2)
    # Calculate correct indent (should be 4 spaces for top-level function body)
    correct_indent = '    '
    
    # Replace old indent with correct indent throughout the block
    fixed_block = match.group(0).replace(old_indent, correct_indent)
    return fixed_block

content = re.sub(pattern, fix_indent, content, flags=re.MULTILINE)

# Also fix any trailing spaces on blank lines after validation
content = re.sub(r'return typo_error\n\s+\n', 'return typo_error\n    \n', content)

# Save
wrapper_file.write_text(content, encoding='utf-8')

print("✅ Fixed indentation in all validation blocks")
print(f"   File: {wrapper_file}")
