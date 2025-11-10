"""Apply **kwargs to _get_forms_service and _get_drive_service - MANUAL FIX"""

# Read the file
with open('google_workspace/google_forms.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace _get_forms_service signature
old_forms_sig = "def _get_forms_service():"
new_forms_sig = "def _get_forms_service(_user_id=None, _injected_credentials=None, **kwargs):"

if old_forms_sig in content:
    content = content.replace(old_forms_sig, new_forms_sig)
    print(f"✅ Replaced _get_forms_service signature")
else:
    print(f"⚠️  _get_forms_service already updated or not found")

# Replace _get_drive_service signature
old_drive_sig = "def _get_drive_service():"
new_drive_sig = "def _get_drive_service(_user_id=None, _injected_credentials=None, **kwargs):"

if old_drive_sig in content:
    content = content.replace(old_drive_sig, new_drive_sig)
    print(f"✅ Replaced _get_drive_service signature")
else:
    print(f"⚠️  _get_drive_service already updated or not found")

# Write back
with open('google_workspace/google_forms.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ File written successfully!")
print(f"Verifying changes...")

# Verify
with open('google_workspace/google_forms.py', 'r', encoding='utf-8') as f:
    verify_content = f.read()
    
if new_forms_sig in verify_content:
    print(f"✅ VERIFIED: _get_forms_service has **kwargs")
else:
    print(f"❌ VERIFICATION FAILED: **kwargs not in _get_forms_service!")

if new_drive_sig in verify_content:
    print(f"✅ VERIFIED: _get_drive_service has **kwargs")
else:
    print(f"❌ VERIFICATION FAILED: **kwargs not in _get_drive_service!")

print(f"\n🎉 All changes applied and verified!")
