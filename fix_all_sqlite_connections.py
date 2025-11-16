"""
MASS FIX: Replace ALL sqlite3.connect() with universal wrapper
This script automatically updates critical files to use Supabase-aware connections
"""

import re
from pathlib import Path

# Files to fix (CRITICAL PRIORITY)
CRITICAL_FILES = [
    'AI_infrastructure/auth/user_auth.py',
    'AI_infrastructure/auth/credential_injector.py',
    'AI_infrastructure/auth/permission_checker.py',
    'AI_infrastructure/builders/user_profile_builder.py',
    'AI_infrastructure/builders/credential_fetcher.py',
    'AI_infrastructure/scheduler.py',
    'AI_infrastructure/routes/automation_routes.py',
    'AI_infrastructure/routes/account_linking_routes.py',
]

def fix_file(file_path: Path):
    """
    Fix a single file:
    1. Add import for wrapper
    2. Replace sqlite3.connect() calls
    """
    print(f"\n{'='*80}")
    print(f"Fixing: {file_path}")
    print(f"{'='*80}")
    
    if not file_path.exists():
        print(f"   ⚠️  File not found, skipping")
        return
    
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    changes_made = []
    
    # Check if file uses sqlite3
    if 'sqlite3.connect' not in content:
        print(f"   ℹ️  No sqlite3.connect() calls found")
        return
    
    # Step 1: Add wrapper import (if not already present)
    if 'from shared.db_connection_wrapper import get_connection' not in content:
        # Find where to add import
        if 'import sqlite3' in content:
            # Add after sqlite3 import
            content = content.replace(
                'import sqlite3',
                'import sqlite3  # Keep for type hints\nfrom shared.db_connection_wrapper import get_connection'
            )
            changes_made.append("Added wrapper import after sqlite3")
        elif 'from pathlib import Path' in content:
            # Add after pathlib import
            content = content.replace(
                'from pathlib import Path',
                'from pathlib import Path\nfrom shared.db_connection_wrapper import get_connection'
            )
            changes_made.append("Added wrapper import after pathlib")
        else:
            # Add at top of imports
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    lines.insert(i, 'from shared.db_connection_wrapper import get_connection')
                    content = '\n'.join(lines)
                    changes_made.append("Added wrapper import at top")
                    break
    
    # Step 2: Replace sqlite3.connect() calls
    replacements = 0
    
    # Pattern 1: with sqlite3.connect(str(db_path)) as conn:
    pattern1 = r'with sqlite3\.connect\(str\(.*?db_path.*?\)\) as conn:'
    if re.search(pattern1, content):
        content = re.sub(
            pattern1,
            "with get_connection('ai_infrastructure') as conn:",
            content
        )
        replacements += content.count("with get_connection('ai_infrastructure') as conn:")
        changes_made.append(f"Replaced 'with sqlite3.connect()' patterns")
    
    # Pattern 2: conn = sqlite3.connect(str(db_path))
    pattern2 = r'conn = sqlite3\.connect\(str\(.*?db_path.*?\)\)'
    if re.search(pattern2, content):
        content = re.sub(
            pattern2,
            "conn = get_connection('ai_infrastructure')",
            content
        )
        replacements += 1
        changes_made.append(f"Replaced 'conn = sqlite3.connect()' patterns")
    
    # Pattern 3: conn = sqlite3.connect(self.db_path)
    pattern3 = r'conn = sqlite3\.connect\(self\.db_path\)'
    if re.search(pattern3, content):
        content = re.sub(
            pattern3,
            "conn = get_connection('ai_infrastructure')",
            content
        )
        replacements += 1
        changes_made.append(f"Replaced 'conn = sqlite3.connect(self.db_path)' patterns")
    
    # Pattern 4: return sqlite3.connect(...)
    pattern4 = r'return sqlite3\.connect\([^)]+\)'
    if re.search(pattern4, content):
        content = re.sub(
            pattern4,
            "return get_connection('ai_infrastructure')",
            content
        )
        replacements += 1
        changes_made.append(f"Replaced 'return sqlite3.connect()' patterns")
    
    # Write changes
    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        print(f"   ✅ FIXED!")
        for change in changes_made:
            print(f"      - {change}")
        print(f"   Total replacements: {replacements}")
    else:
        print(f"   ℹ️  No changes needed")

def main():
    root = Path(__file__).parent
    
    print("="*80)
    print(" MASS SQLite → Supabase Migration")
    print("="*80)
    print(f"\nFixing {len(CRITICAL_FILES)} critical files...\n")
    
    for file_rel_path in CRITICAL_FILES:
        file_path = root / file_rel_path
        try:
            fix_file(file_path)
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print(" COMPLETE!")
    print("="*80)
    print("\nNext steps:")
    print("1. Test locally (should still use SQLite)")
    print("2. Commit and push to GitHub")
    print("3. Render will auto-deploy with Supabase connections")
    print("\nVerify with:")
    print("   python test_db_connection.py")

if __name__ == '__main__':
    main()
