"""
FINAL FIX - Add **kwargs and validation to ALL remaining calculator functions
Handles complex multi-line signatures properly
"""

from pathlib import Path
import re

wrapper_file = Path("UI/modules_external/quote-calculator/implementations/calculator_wrapper.py")
content = wrapper_file.read_text(encoding='utf-8')

fixed_count = 0

# Step 1: Find ALL function definitions that DON'T have **kwargs yet
pattern = r'(def calculate_\w+\([^)]+?)(\) -> Dict\[str, Any\]:)'

matches = list(re.finditer(pattern, content, flags=re.DOTALL))
print(f"Found {len(matches)} function signatures")

# Process from end to start (to preserve positions)
for match in reversed(matches):
    func_signature = match.group(1)
    closing = match.group(2)
    
    # Skip if already has **kwargs
    if '**kwargs' in func_signature:
        continue
    
    # Add **kwargs before the closing paren
    # Find the last parameter line
    lines = func_signature.split('\n')
    if len(lines) > 1:
        # Multi-line signature - add with proper indentation
        indent = '    '  # Standard 4-space indent
        new_signature = func_signature + f',\n{indent}**kwargs  # Absorb internal registry params\n'
    else:
        # Single line - add inline
        new_signature = func_signature + ',\n    **kwargs  # Absorb internal registry params\n'
    
    # Replace in content
    content = content[:match.start()] + new_signature + closing + content[match.end():]
    fixed_count += 1
    
    # Extract function name for logging
    func_name_match = re.search(r'def (calculate_\w+)\(', func_signature)
    if func_name_match:
        print(f"✅ Added **kwargs to: {func_name_match.group(1)}")

# Save intermediate result
wrapper_file.write_text(content, encoding='utf-8')
print(f"\n📝 Step 1: Added **kwargs to {fixed_count} functions")

# Step 2: Add validation to ALL functions that have **kwargs but no validation
validation_count = 0

# Pattern: function with **kwargs, docstring, then code (not validation)
pattern2 = r'(def (calculate_\w+)\([^)]*\*\*kwargs[^)]*\)\s*->\s*Dict\[str, Any\]:\s*"""(?:[^"]|"(?!""))*?""")\s*\n(\s+)(?!#\s*Check for typos)'

def add_validation(match):
    global validation_count
    header = match.group(1)
    func_name = match.group(2)
    indent = match.group(3)
    
    validation = f'''\n{indent}# Check for typos in parameter names (unexpected kwargs)
{indent}typo_error = _validate_no_typos(kwargs, "{func_name}")
{indent}if typo_error:
{indent}    return typo_error
{indent}
{indent}'''
    
    validation_count += 1
    print(f"✅ Added validation to: {func_name}")
    return header + validation

content = re.sub(pattern2, add_validation, content, flags=re.DOTALL)

# Save final result
wrapper_file.write_text(content, encoding='utf-8')

print(f"\n📝 Step 2: Added validation to {validation_count} functions")
print(f"\n🎉 COMPLETE: Fixed {fixed_count + validation_count} calculator functions total")
print(f"   File: {wrapper_file}")
