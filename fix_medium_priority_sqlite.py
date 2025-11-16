"""
Automated Fix Script for MEDIUM Priority SQLite → Supabase Migration

This script updates the 7 MEDIUM priority files identified in the audit:
1. utils/email_alias_helpers.py
2. utils/user_context_builder.py
3. utils/database_helpers.py
4. workspace/invitation_manager.py
5. threads/thread_manager.py
6. threads/message_manager.py
7. threads/thread_sharing_manager.py

Usage:
    python fix_medium_priority_sqlite.py [--dry-run]

Options:
    --dry-run    Show what would be changed without making changes
"""

import sys
import argparse
from pathlib import Path
from typing import List, Tuple

def backup_file(file_path: Path) -> Path:
    """Create backup of file before modifying"""
    backup_path = file_path.with_suffix(file_path.suffix + '.backup')
    backup_path.write_text(file_path.read_text(encoding='utf-8'), encoding='utf-8')
    return backup_path

def fix_email_alias_helpers(file_path: Path, dry_run: bool = False) -> bool:
    """Fix utils/email_alias_helpers.py"""
    if not file_path.exists():
        print(f"  ⚠ File not found: {file_path}")
        return False
    
    content = file_path.read_text(encoding='utf-8')
    
    # Replace imports
    old_import = "import sqlite3"
    new_import = """import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.database_utils import get_database_connection"""
    
    # Replace connection calls
    old_connect = "sqlite3.connect("
    new_connect = "get_database_connection('ai_infrastructure')"
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        content = content.replace(old_connect, new_connect)
        
        if not dry_run:
            backup_file(file_path)
            file_path.write_text(content, encoding='utf-8')
            print(f"  ✓ Fixed: {file_path.name}")
        else:
            print(f"  [DRY RUN] Would fix: {file_path.name}")
        return True
    else:
        print(f"  ℹ Already fixed or no changes needed: {file_path.name}")
        return False

def fix_user_context_builder(file_path: Path, dry_run: bool = False) -> bool:
    """Fix utils/user_context_builder.py"""
    if not file_path.exists():
        print(f"  ⚠ File not found: {file_path}")
        return False
    
    content = file_path.read_text(encoding='utf-8')
    
    # This file has conditional imports - need careful handling
    if "import sqlite3" in content and "sqlite3.connect(" in content:
        # Add import at top
        new_import = """import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.database_utils import get_database_connection
"""
        
        # Find the first import statement
        lines = content.split('\n')
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_pos = i
                break
        
        # Insert new import after first import block
        lines.insert(insert_pos + 1, new_import)
        content = '\n'.join(lines)
        
        # Replace sqlite3.connect() calls
        content = content.replace(
            "conn = sqlite3.connect(",
            "conn = get_database_connection('ai_infrastructure')  # "
        )
        
        if not dry_run:
            backup_file(file_path)
            file_path.write_text(content, encoding='utf-8')
            print(f"  ✓ Fixed: {file_path.name}")
        else:
            print(f"  [DRY RUN] Would fix: {file_path.name}")
        return True
    else:
        print(f"  ℹ Already fixed or no changes needed: {file_path.name}")
        return False

def fix_thread_manager(file_path: Path, schema: str, dry_run: bool = False) -> bool:
    """Fix thread manager files (thread_manager, message_manager, thread_sharing_manager)"""
    if not file_path.exists():
        print(f"  ⚠ File not found: {file_path}")
        return False
    
    content = file_path.read_text(encoding='utf-8')
    
    if "sqlite3.connect(self.db_path)" in content:
        # Add import
        new_import = """import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.database_utils import get_database_connection
"""
        
        # Insert import after existing imports
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('import sqlite3'):
                lines[i] = new_import + line  # Keep sqlite3 for type hints
                break
        
        content = '\n'.join(lines)
        
        # Replace _get_connection method
        content = content.replace(
            "conn = sqlite3.connect(self.db_path)",
            f"conn = get_database_connection('{schema}')"
        )
        
        if not dry_run:
            backup_file(file_path)
            file_path.write_text(content, encoding='utf-8')
            print(f"  ✓ Fixed: {file_path.name}")
        else:
            print(f"  [DRY RUN] Would fix: {file_path.name}")
        return True
    else:
        print(f"  ℹ Already fixed or no changes needed: {file_path.name}")
        return False

def fix_invitation_manager(file_path: Path, dry_run: bool = False) -> bool:
    """Fix workspace/invitation_manager.py"""
    return fix_thread_manager(file_path, 'ai_infrastructure', dry_run)

def main():
    parser = argparse.ArgumentParser(description='Fix MEDIUM priority SQLite → Supabase files')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying them')
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("MEDIUM PRIORITY SQLITE → SUPABASE MIGRATION FIX")
    print("="*80 + "\n")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified\n")
    else:
        print("⚠️  LIVE MODE - Files will be modified (backups created)\n")
    
    project_root = Path(__file__).parent
    ai_infra = project_root / 'AI_infrastructure'
    
    files_fixed = 0
    files_total = 7
    
    # Fix each file
    print("[1/7] Fixing email_alias_helpers.py...")
    if fix_email_alias_helpers(ai_infra / 'utils' / 'email_alias_helpers.py', args.dry_run):
        files_fixed += 1
    
    print("\n[2/7] Fixing user_context_builder.py...")
    if fix_user_context_builder(ai_infra / 'utils' / 'user_context_builder.py', args.dry_run):
        files_fixed += 1
    
    print("\n[3/7] Fixing invitation_manager.py...")
    if fix_invitation_manager(ai_infra / 'workspace' / 'invitation_manager.py', args.dry_run):
        files_fixed += 1
    
    print("\n[4/7] Fixing thread_manager.py...")
    if fix_thread_manager(ai_infra / 'threads' / 'thread_manager.py', 'sessions', args.dry_run):
        files_fixed += 1
    
    print("\n[5/7] Fixing message_manager.py...")
    if fix_thread_manager(ai_infra / 'threads' / 'message_manager.py', 'sessions', args.dry_run):
        files_fixed += 1
    
    print("\n[6/7] Fixing thread_sharing_manager.py...")
    if fix_thread_manager(ai_infra / 'threads' / 'thread_sharing_manager.py', 'sessions', args.dry_run):
        files_fixed += 1
    
    print("\n[7/7] Skipping database_helpers.py (complex - needs manual review)")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80 + "\n")
    
    print(f"Files processed: {files_total}")
    print(f"Files fixed: {files_fixed}")
    print(f"Files skipped: {files_total - files_fixed}")
    
    if args.dry_run:
        print("\n✓ DRY RUN COMPLETE - No files were modified")
        print("  Run without --dry-run to apply changes")
    else:
        print(f"\n✓ MIGRATION COMPLETE - {files_fixed} files updated")
        print("  Backup files created with .backup extension")
        print("\nNext steps:")
        print("  1. Run: python verify_supabase_migration.py")
        print("  2. Test with: BISTART")
        print("  3. Check for errors in Flask logs")
    
    print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    main()
