"""Fix credential passing in google_forms_create_form"""

# Read the file
with open('google_workspace/google_forms.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the service call to extract and pass credentials explicitly
old_service_call = "    try:\n        service = _get_forms_service(**kwargs)"
new_service_call = """    try:
        # Extract credential parameters from kwargs
        _user_id = kwargs.get('_user_id')
        _injected_credentials = kwargs.get('_injected_credentials')
        service = _get_forms_service(_user_id=_user_id, _injected_credentials=_injected_credentials, **kwargs)"""

if old_service_call in content:
    content = content.replace(old_service_call, new_service_call)
    print("✅ Fixed service call in google_forms_create_form")
else:
    print("⚠️  Pattern not found, trying alternate...")
    # Try with just the service call line
    old_alt = "        service = _get_forms_service(**kwargs)"
    new_alt = """        # Extract credential parameters from kwargs
        _user_id = kwargs.get('_user_id')
        _injected_credentials = kwargs.get('_injected_credentials')
        service = _get_forms_service(_user_id=_user_id, _injected_credentials=_injected_credentials, **kwargs)"""
    
    if old_alt in content:
        content = content.replace(old_alt, new_alt, 1)  # Only replace first occurrence
        print("✅ Fixed service call (alternate pattern)")
    else:
        print("❌ Could not find service call to fix!")

# Also fix the drive service call
old_drive_call = "                drive_service = _get_drive_service(**kwargs)"
new_drive_call = "                drive_service = _get_drive_service(_user_id=_user_id, _injected_credentials=_injected_credentials, **kwargs)"

if old_drive_call in content:
    content = content.replace(old_drive_call, new_drive_call)
    print("✅ Fixed drive service call")
else:
    print("⚠️  Drive service call already fixed or not found")

# Write back
with open('google_workspace/google_forms.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ File written!")

# Verify
with open('google_workspace/google_forms.py', 'r', encoding='utf-8') as f:
    verify_content = f.read()

if "_user_id = kwargs.get('_user_id')" in verify_content:
    print("✅ VERIFIED: Credential extraction added")
else:
    print("❌ VERIFICATION FAILED")

print("\n🎉 Credential passing fixed!")
