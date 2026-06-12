"""
Clean up duplicate validation calls and fix indentation
"""

from pathlib import Path
import re

wrapper_file = Path("UI/modules_external/quote-calculator/implementations/calculator_wrapper.py")
content = wrapper_file.read_text(encoding='utf-8')

# Pattern to find duplicate validation blocks
# Look for 2+ consecutive occurrences of the same validation
pattern = r'(\s+)# Check for typos in parameter names.*?\n\1typo_error = _validate_no_typos\(kwargs, "([^"]+)"\)\n\1if typo_error:\n\1    return typo_error\n\1\n'

# Find all duplicates
matches = list(re.finditer(pattern, content))
print(f"Found {len(matches)} validation blocks")

# Group by function name
from collections import defaultdict
by_function = defaultdict(list)
for match in matches:
    func_name = match.group(2)
    by_function[func_name].append(match)

# Remove duplicates (keep only first occurrence)
fixed_count = 0
for func_name, func_matches in by_function.items():
    if len(func_matches) > 1:
        print(f"Removing {len(func_matches)-1} duplicates from: {func_name}")
        # Sort by position (reverse) and remove all but the first
        sorted_matches = sorted(func_matches, key=lambda m: m.start(), reverse=True)
        for match in sorted_matches[:-1]:  # Skip the first (earliest) one
            content = content[:match.start()] + content[match.end():]
            fixed_count += 1

# Save
wrapper_file.write_text(content, encoding='utf-8')

print(f"\n✅ Removed {fixed_count} duplicate validation blocks")
print(f"   File: {wrapper_file}")
