"""
Upload the current sessions.db to Google Drive folder
This will replace the old file that's missing the threads table
"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from tools.registry_v3 import RegistryV3

DRIVE_FOLDER_ID = "1UwmYADDh6vuNKlMOlcjFog4SSwnThE-O"
LOCAL_DB_PATH = "data/sessions.db"

print("=" * 80)
print("UPLOADING FRESH sessions.db TO GOOGLE DRIVE")
print("=" * 80)
print()
print(f"Local file: {LOCAL_DB_PATH}")
print(f"Target folder: {DRIVE_FOLDER_ID}")
print()

registry = RegistryV3()

try:
    # Check local file exists
    import os
    if not os.path.exists(LOCAL_DB_PATH):
        print(f"[ERROR] File not found: {LOCAL_DB_PATH}")
        sys.exit(1)
    
    file_size = os.path.getsize(LOCAL_DB_PATH) / 1024  # KB
    print(f"File size: {file_size:.1f} KB")
    print()
    
    # Upload to Google Drive
    print("Uploading to Google Drive...")
    result = registry.execute_tool(
        tool_name='google_drive_upload_file',
        file_path=LOCAL_DB_PATH,
        name='sessions.db',
        parent_folder_id=DRIVE_FOLDER_ID
    )
    
    print()
    print("[OK] Upload complete!")
    print()
    print(f"File ID: {result.get('id')}")
    print(f"Name: {result.get('name')}")
    print(f"Size: {result.get('size')} bytes")
    print(f"Download URL: https://drive.google.com/uc?export=download&id={result.get('id')}")
    print()
    print("=" * 80)
    print("NEXT: UPDATE RENDER SHELL COMMAND")
    print("=" * 80)
    print()
    print(f"curl -L 'https://drive.google.com/uc?export=download&id={result.get('id')}' -o sessions.db")
    print()
    
except Exception as e:
    print(f"[ERROR] Upload failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
