"""Get FILE_IDs from Google Drive folder"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from tools.registry_v3 import RegistryV3
import json

# Your Google Drive folder ID
FOLDER_ID = "1UwmYADDh6vuNKlMOlcjFog4SSwnThE-O"

print("Fetching files from Google Drive folder...")
print(f"Folder ID: {FOLDER_ID}")
print()

registry = RegistryV3()

# Query for files in this folder
query = f"'{FOLDER_ID}' in parents"

try:
    result = registry.execute_tool(
        tool_name='google_drive_list_files',
        query=query,
        max_results=50
    )
    
    files = result.get('files', [])
    
    if not files:
        print("No files found in folder!")
        sys.exit(1)
    
    print(f"Found {len(files)} files:")
    print("=" * 80)
    
    # Filter for .db files
    db_files = [f for f in files if f['name'].endswith('.db')]
    
    if not db_files:
        print("No .db files found!")
        print("\nAll files in folder:")
        for f in files:
            print(f"  - {f['name']} ({f['mimeType']})")
        sys.exit(1)
    
    print(f"\nDatabase files ({len(db_files)}):")
    print("-" * 80)
    
    for f in db_files:
        size_mb = int(f.get('size', 0)) / (1024 * 1024)
        print(f"\nFile: {f['name']}")
        print(f"  FILE_ID: {f['id']}")
        print(f"  Size: {size_mb:.2f} MB")
        print(f"  Download URL: https://drive.google.com/uc?export=download&id={f['id']}")
    
    print()
    print("=" * 80)
    print("RENDER SHELL COMMANDS:")
    print("=" * 80)
    print()
    print("cd /data")
    print("mkdir -p backup_$(date +%Y%m%d_%H%M%S)")
    print("cp *.db backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null")
    print()
    
    for f in db_files:
        print(f"# {f['name']}")
        print(f"wget --no-check-certificate 'https://drive.google.com/uc?export=download&id={f['id']}' -O {f['name']}")
        print()
    
    print("ls -lh *.db")
    print("sqlite3 ai_infrastructure.db \"SELECT name FROM pragma_table_info('users') WHERE name LIKE '%oauth%';\"")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
