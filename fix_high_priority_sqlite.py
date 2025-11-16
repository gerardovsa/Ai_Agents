"""
Fix High Priority SQLite Remnants for Supabase Migration
========================================================

This script removes SQLite-specific code from 5 HIGH priority files:
1. AI_infrastructure/auth/user_auth.py (5 row_factory lines)
2. AI_infrastructure/scheduler.py (7 row_factory lines)
3. AI_infrastructure/routes/automation_routes.py (2 row_factory lines)
4. AI_infrastructure/auth/permission_checker.py (1 row_factory line)
5. AI_infrastructure/auth/credential_injector.py (already clean)

Changes:
- Remove: conn.row_factory = sqlite3.Row (PostgreSQL doesn't use this)
- Remove: import sqlite3 (if only used for row_factory)
- Keep: Type hints that mention sqlite3.Connection (for documentation)

Note: These files already use get_database_connection() which returns
PostgreSQL connections on Render. The row_factory lines are harmless but
indicate SQLite legacy code.
"""

import re
from pathlib import Path
from datetime import datetime

# Files to fix
FILES_TO_FIX = {
    'AI_infrastructure/auth/user_auth.py': {
        'row_factory_lines': 4,
        'keep_sqlite3_import': True,  # Used in type hints
        'description': 'User authentication manager'
    },
    'AI_infrastructure/scheduler.py': {
        'row_factory_lines': 7,
        'keep_sqlite3_import': False,
        'description': 'Automation workflow scheduler'
    },
    'AI_infrastructure/routes/automation_routes.py': {
        'row_factory_lines': 2,
        'keep_sqlite3_import': False,
        'description': 'Automation API routes'
    },
    'AI_infrastructure/auth/permission_checker.py': {
        'row_factory_lines': 1,
        'keep_sqlite3_import': False,
        'description': 'Permission authorization checker'
    }
}


def remove_row_factory_lines(content: str) -> tuple[str, int]:
    """
    Remove all lines with conn.row_factory = sqlite3.Row
    
    Returns:
        (modified_content, num_removals)
    """
    lines = content.split('\n')
    new_lines = []
    removals = 0
    
    for line in lines:
        # Skip lines that set row_factory
        if re.search(r'\.row_factory\s*=\s*sqlite3\.Row', line):
            removals += 1
            print(f"  🗑️  Removed: {line.strip()}")
            continue
        new_lines.append(line)
    
    return '\n'.join(new_lines), removals


def remove_sqlite3_import(content: str, keep_for_hints: bool) -> tuple[str, bool]:
    """
    Remove 'import sqlite3' line if not needed for type hints
    
    Returns:
        (modified_content, was_removed)
    """
    if keep_for_hints:
        print(f"  ℹ️  Keeping 'import sqlite3' for type hints")
        return content, False
    
    lines = content.split('\n')
    new_lines = []
    removed = False
    
    for line in lines:
        # Remove standalone 'import sqlite3' line
        if re.match(r'^\s*import\s+sqlite3\s*$', line):
            removed = True
            print(f"  🗑️  Removed: {line.strip()}")
            continue
        new_lines.append(line)
    
    return '\n'.join(new_lines), removed


def update_file_header(content: str, file_path: str) -> str:
    """Update LAST MODIFIED in file header"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Update LAST MODIFIED line
    pattern = r'(LAST MODIFIED:)\s*\d{4}-\d{2}-\d{2}.*'
    replacement = f'\\1 {today} - Removed SQLite remnants for Supabase migration'
    content = re.sub(pattern, replacement, content, count=1)
    
    return content


def fix_file(file_path: str, config: dict) -> dict:
    """
    Fix a single file
    
    Returns:
        dict with results
    """
    full_path = Path(file_path)
    
    if not full_path.exists():
        return {
            'success': False,
            'error': f'File not found: {file_path}'
        }
    
    print(f"\n📝 Processing: {file_path}")
    print(f"   Description: {config['description']}")
    
    # Read file
    with open(full_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Apply fixes
    content = original_content
    
    # 1. Remove row_factory lines
    content, row_factory_removals = remove_row_factory_lines(content)
    
    # 2. Remove sqlite3 import if not needed
    content, import_removed = remove_sqlite3_import(content, config['keep_sqlite3_import'])
    
    # 3. Update file header
    content = update_file_header(content, file_path)
    
    # Check if anything changed
    if content == original_content:
        print(f"  ℹ️  No changes needed")
        return {
            'success': True,
            'changed': False,
            'file': file_path
        }
    
    # Create backup
    backup_path = full_path.with_suffix(full_path.suffix + '.backup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(original_content)
    print(f"  💾 Backup created: {backup_path.name}")
    
    # Write modified file
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✅ Fixed successfully!")
    print(f"     - Removed {row_factory_removals} row_factory lines")
    print(f"     - Removed import sqlite3: {'Yes' if import_removed else 'No'}")
    
    return {
        'success': True,
        'changed': True,
        'file': file_path,
        'row_factory_removals': row_factory_removals,
        'import_removed': import_removed,
        'backup': str(backup_path)
    }


def main():
    """Fix all high priority files"""
    print("="*70)
    print("🔧 HIGH PRIORITY SQLITE REMNANT REMOVAL")
    print("="*70)
    print(f"Files to process: {len(FILES_TO_FIX)}")
    print(f"Target: Remove conn.row_factory = sqlite3.Row (PostgreSQL doesn't use this)")
    print()
    
    results = []
    
    for file_path, config in FILES_TO_FIX.items():
        result = fix_file(file_path, config)
        results.append(result)
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    success_count = sum(1 for r in results if r['success'])
    changed_count = sum(1 for r in results if r.get('changed', False))
    total_removals = sum(r.get('row_factory_removals', 0) for r in results)
    
    print(f"Files processed: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Modified: {changed_count}")
    print(f"Total row_factory lines removed: {total_removals}")
    
    if changed_count > 0:
        print("\n✅ FILES FIXED:")
        for r in results:
            if r.get('changed'):
                print(f"  - {r['file']}")
                if r.get('backup'):
                    print(f"    Backup: {r['backup']}")
    
    if any(not r['success'] for r in results):
        print("\n❌ ERRORS:")
        for r in results:
            if not r['success']:
                print(f"  - {r['file']}: {r.get('error', 'Unknown error')}")
    
    print("\n" + "="*70)
    print("🎯 NEXT STEPS")
    print("="*70)
    print("1. Review changes in modified files")
    print("2. Run: python test_high_priority_fixes.py")
    print("3. Test locally: BISTART")
    print("4. If tests pass, commit and deploy:")
    print("   git add AI_infrastructure/auth/ AI_infrastructure/routes/")
    print("   git add AI_infrastructure/scheduler.py")
    print("   git commit -m 'Remove SQLite remnants from high priority files'")
    print("   git push origin v6")
    print("="*70)
    
    return all(r['success'] for r in results)


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
