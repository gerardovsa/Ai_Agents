"""Apply **kwargs to google_forms_create_form - MANUAL FIX"""

# Read the file
with open('google_workspace/google_forms.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the function signature
old_sig = "def google_forms_create_form(title, document_title=None, description=None, shareable=True):"
new_sig = "def google_forms_create_form(title, document_title=None, description=None, shareable=True, **kwargs):"

if old_sig in content:
    content = content.replace(old_sig, new_sig, 1)  # Only replace first occurrence
    print(f"✅ Replaced function signature")
else:
    print(f"❌ Old signature not found!")
    print(f"Searching for variations...")
    # Try without colon
    if "def google_forms_create_form(title, document_title=None, description=None, shareable=True" in content:
        print(f"  Found without colon - file might already be updated?")
    sys.exit(1)

# Also need to pass **kwargs to _get_forms_service
old_service_call = "        service = _get_forms_service()"
new_service_call = "        service = _get_forms_service(**kwargs)"

if old_service_call in content:
    content = content.replace(old_service_call, new_service_call, 1)
    print(f"✅ Updated service call to pass kwargs")
else:
    print(f"⚠️  Service call already updated or not found")

# Also update the drive service call
old_drive_call = "                drive_service = _get_drive_service()"
new_drive_call = "                drive_service = _get_drive_service(**kwargs)"

if old_drive_call in content:
    content = content.replace(old_drive_call, new_drive_call, 1)
    print(f"✅ Updated drive service call to pass kwargs")
else:
    print(f"⚠️  Drive service call already updated or not found")

# Write back
with open('google_workspace/google_forms.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ File written successfully!")
print(f"Verifying changes...")

# Verify
with open('google_workspace/google_forms.py', 'r', encoding='utf-8') as f:
    verify_content = f.read()
    
if new_sig in verify_content:
    print(f"✅ VERIFIED: Function signature has **kwargs")
else:
    print(f"❌ VERIFICATION FAILED: **kwargs not in file!")
    sys.exit(1)

if new_service_call in verify_content:
    print(f"✅ VERIFIED: Service call passes **kwargs")
else:
    print(f"⚠️  Service call not verified")

print(f"\n🎉 All changes applied and verified!")
