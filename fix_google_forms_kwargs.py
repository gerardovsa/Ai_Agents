"""
Script to add **kwargs to all Google Forms functions
Generates multi_replace operations for efficient batch fixing
"""

import re
import json

# Read the file
with open('google_workspace/google_forms.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all functions that need fixing
functions_to_fix = []
for match in re.finditer(r'^def (google_forms_\w+)\((.*?)\):', content, re.MULTILINE):
    func_name = match.group(1)
    params = match.group(2).strip()
    
    # Skip if already has **kwargs or is a helper function
    if '**kwargs' not in params and not func_name.startswith('_'):
        # Get the full line for context
        start_pos = match.start()
        # Find 3 lines before
        lines_before = content[:start_pos].split('\n')[-4:-1]
        # Find the def line
        def_line = match.group(0)
        # Find 3 lines after
        end_pos = match.end()
        lines_after_start = content[end_pos:end_pos+500]
        lines_after = lines_after_start.split('\n')[:4]
        
        # Construct old and new strings
        old_def = f"def {func_name}({params}):"
        if params:
            new_def = f"def {func_name}({params}, **kwargs):"
        else:
            new_def = f"def {func_name}(**kwargs):"
        
        functions_to_fix.append({
            'func_name': func_name,
            'old_def': old_def,
            'new_def': new_def,
            'params': params
        })

print(f"Found {len(functions_to_fix)} functions to fix\n")

# Check for service calls that need **kwargs passed
service_call_fixes = []
for func in functions_to_fix:
    func_name = func['func_name']
    # Find the function body
    pattern = rf"def {re.escape(func_name)}\(.*?\):.*?(?=\ndef |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        func_body = match.group(0)
        # Check if it calls _get_forms_service() or _get_drive_service()
        if '_get_forms_service()' in func_body:
            service_call_fixes.append({
                'func_name': func_name,
                'old_call': 'service = _get_forms_service()',
                'new_call': 'service = _get_forms_service(**kwargs)'
            })
        if '_get_drive_service()' in func_body:
            service_call_fixes.append({
                'func_name': func_name,
                'old_call': 'service = _get_drive_service()',
                'new_call': 'service = _get_drive_service(**kwargs)'
            })

print(f"Found {len(service_call_fixes)} service calls to update\n")

# Save results
output = {
    'signature_fixes': functions_to_fix[:20],  # First 20 for review
    'service_call_fixes': service_call_fixes[:20],
    'total_signature_fixes': len(functions_to_fix),
    'total_service_fixes': len(service_call_fixes)
}

with open('google_forms_fixes.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"✅ Analysis complete!")
print(f"   - {len(functions_to_fix)} function signatures need **kwargs")
print(f"   - {len(service_call_fixes)} service calls need to pass **kwargs")
print(f"\nSample fixes:")
for i, fix in enumerate(functions_to_fix[:5]):
    print(f"\n{i+1}. {fix['func_name']}")
    print(f"   OLD: {fix['old_def']}")
    print(f"   NEW: {fix['new_def']}")
