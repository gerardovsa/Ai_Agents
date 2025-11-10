# Render Backend Cleanup Script
# Removes redundant files and archives historical documentation

import os
import shutil
from pathlib import Path

# Get base directory
base_dir = Path(__file__).parent

# Files to DELETE completely (redundant/outdated)
files_to_delete = [
    # Old CLI versions (replaced by render_universal_cli.py)
    'render_cli.py',
    'render_complete_cli.py',
    
    # Project-specific deployment scripts
    'delete_oregon_service.py',
    'deploy_singapore_docker.py',
    'smart_deploy.py',
    'render_deploy.py',
    'deploy_to_render.ps1',
    
    # Test scripts (outdated)
    'test_cors_fix.py',
    'test_flask_connectivity.py',
    'test_shopify_endpoint.py',
    'test_deployment.py',
    'test_render_connection.py',
    
    # Monitoring scripts (project-specific)
    'monitor_flask_deploy.py',
    'monitor_streamlit_deploy.py',
    'monitor_deployment.py',
    
    # Redundant documentation (consolidated into README_NEW.md)
    'DEPLOY_NOW.md',
    'DEPLOY_VIA_DASHBOARD.md',
    'README_RENDER_CLI.md',
    'RENDER_CLI_COMPLETE.md',
    'QUICK_START.md',
    'QUICK_REFERENCE.md',
    
    # Old README (replaced by README_NEW.md)
    'README.md',
    
    # Utility scripts that are obsolete
    'downgrade_to_free.py',
    'update_oauth_redirects.py',
]

# Files to ARCHIVE (historical documentation)
files_to_archive = [
    'DEPLOYMENT_GUIDE_FOR_AI.md',
    'DEPLOYMENT_ANALYSIS.md',
    'AUSTRALIA_DOCKER_DEPLOYMENT.md',
    'CURRENT_STATE_ANALYSIS.md',
    'FIXES_APPLIED.md',
]

# Create archive directory
archive_dir = base_dir / 'archive'
archive_dir.mkdir(exist_ok=True)

print("=" * 80)
print("  RENDER BACKEND CLEANUP")
print("=" * 80)
print()

# Delete redundant files
print("Deleting redundant files...")
deleted_count = 0
for filename in files_to_delete:
    file_path = base_dir / filename
    if file_path.exists():
        try:
            os.remove(file_path)
            print(f"  ✅ Deleted: {filename}")
            deleted_count += 1
        except Exception as e:
            print(f"  ❌ Failed to delete {filename}: {e}")
    else:
        print(f"  ⚠️  Not found: {filename}")

print()
print(f"Deleted {deleted_count} files")
print()

# Archive historical documentation
print("Archiving historical documentation...")
archived_count = 0
for filename in files_to_archive:
    file_path = base_dir / filename
    if file_path.exists():
        try:
            shutil.move(str(file_path), str(archive_dir / filename))
            print(f"  ✅ Archived: {filename}")
            archived_count += 1
        except Exception as e:
            print(f"  ❌ Failed to archive {filename}: {e}")
    else:
        print(f"  ⚠️  Not found: {filename}")

print()
print(f"Archived {archived_count} files")
print()

# Rename README_NEW.md to README.md
print("Renaming README_NEW.md to README.md...")
readme_new = base_dir / 'README_NEW.md'
readme_final = base_dir / 'README.md'
if readme_new.exists():
    try:
        shutil.move(str(readme_new), str(readme_final))
        print("  ✅ Renamed README_NEW.md → README.md")
    except Exception as e:
        print(f"  ❌ Failed to rename: {e}")
else:
    print("  ⚠️  README_NEW.md not found")

print()
print("=" * 80)
print("  CLEANUP COMPLETE")
print("=" * 80)
print()

# Show final file structure
print("Final toolkit structure:")
print()
remaining_files = [
    f.name for f in base_dir.iterdir() 
    if f.is_file() and not f.name.startswith('.')
]
remaining_files.sort()

for filename in remaining_files:
    if filename.endswith('.py'):
        print(f"  📜 {filename}")
    elif filename.endswith('.md'):
        print(f"  📄 {filename}")
    elif filename.endswith('.json'):
        print(f"  📋 {filename}")

print()
print("Folders:")
folders = [f.name for f in base_dir.iterdir() if f.is_dir() and not f.name.startswith('.')]
for folder in sorted(folders):
    print(f"  📁 {folder}/")

print()
print(f"Total files: {len(remaining_files)}")
print(f"Total folders: {len(folders)}")
