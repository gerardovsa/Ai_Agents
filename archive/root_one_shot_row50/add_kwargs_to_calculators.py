"""
Add **kwargs and typo validation to all calculator wrapper functions
Fixes the _user_id parameter injection error
"""

import re
from pathlib import Path

# File to modify
wrapper_file = Path("UI/modules_external/quote-calculator/implementations/calculator_wrapper.py")

# Read the file
content = wrapper_file.read_text(encoding='utf-8')

# Pattern to find calculator function definitions (those WITHOUT **kwargs already)
pattern = r'(^def calculate_\w+\([^)]+)(\) -> Dict\[str, Any\]:)'

def add_kwargs_if_missing(match):
    """Add **kwargs to function signature if not already present"""
    func_signature = match.group(1)
    closing = match.group(2)
    
    # Check if **kwargs already present
    if '**kwargs' in func_signature:
        return match.group(0)  # Already has it, no change
    
    # Add **kwargs before the closing parenthesis
    new_signature = func_signature + ',\n    **kwargs  # Absorb internal registry params (_user_id, etc.)'
    return new_signature + closing

# Apply the transformation
modified_content = re.sub(pattern, add_kwargs_if_missing, content, flags=re.MULTILINE)

# Now add validation call after docstring for functions that don't have it
# Pattern: function with **kwargs, followed by docstring, NOT followed by typo validation
pattern2 = r'(def calculate_\w+\([^)]*\*\*kwargs[^)]*\) -> Dict\[str, Any\]:\s+"""[^"]+""")\s+(if not )'

def add_validation_if_missing(match):
    """Add typo validation before the first 'if' statement"""
    header = match.group(1)
    if_statement = match.group(2)
    
    # Extract function name
    func_name_match = re.search(r'def (calculate_\w+)\(', header)
    if not func_name_match:
        return match.group(0)
    
    func_name = func_name_match.group(1)
    
    # Check if validation already present
    if '_validate_no_typos' in header:
        return match.group(0)
    
    # Add validation
    validation = f'''
    # Check for typos in parameter names (unexpected kwargs)
    typo_error = _validate_no_typos(kwargs, "{func_name}")
    if typo_error:
        return typo_error
    
    '''
    
    return header + validation + if_statement

# Apply validation injection
modified_content = re.sub(pattern2, add_validation_if_missing, modified_content, flags=re.DOTALL)

# Save the modified file
wrapper_file.write_text(modified_content, encoding='utf-8')

print("✅ Added **kwargs and typo validation to all calculator functions")
print(f"   Modified: {wrapper_file}")
