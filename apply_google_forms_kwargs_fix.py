"""
Automated Google Forms **kwargs fixer
Applies all necessary fixes in one go
"""

import re

# Read the file
with open('google_workspace/google_forms.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Track changes
changes_made = 0

# Pattern 1: Add **kwargs to function signatures (except those already having it)
def_pattern = r'^def (google_forms_\w+)\((.*?)\):'

def fix_signature(match):
    global changes_made
    func_name = match.group(1)
    params = match.group(2).strip()
    
    # Skip if already has **kwargs
    if '**kwargs' in params:
        return match.group(0)
    
    # Skip helper functions
    if func_name.startswith('_'):
        return match.group(0)
    
    # Add **kwargs
    if params:
        new_signature = f"def {func_name}({params}, **kwargs):"
    else:
        new_signature = f"def {func_name}(**kwargs):"
    
    changes_made += 1
    return new_signature

# Apply signature fixes
content = re.sub(def_pattern, fix_signature, content, flags=re.MULTILINE)

print(f"✅ Fixed {changes_made} function signatures")

# Pattern 2: Update service calls to pass **kwargs
service_patterns = [
    (r'(\s+)service = _get_forms_service\(\)', r'\1service = _get_forms_service(**kwargs)'),
    (r'(\s+)service = _get_drive_service\(\)', r'\1service = _get_drive_service(**kwargs)'),
]

service_changes = 0
for old_pattern, new_pattern in service_patterns:
    new_content, count = re.subn(old_pattern, new_pattern, content)
    if count > 0:
        content = new_content
        service_changes += count
        print(f"✅ Updated {count} {old_pattern.split('_')[2]} calls")

# Write back
with open('google_workspace/google_forms.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n🎉 COMPLETE!")
print(f"   Total signature fixes: {changes_made}")
print(f"   Total service call updates: {service_changes}")
print(f"   File updated: google_workspace/google_forms.py")
