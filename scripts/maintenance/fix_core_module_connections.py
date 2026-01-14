"""
Fix Core Module Database Connections
====================================

Automatically updates core modules to use connection pooling instead of direct SQLite connections.

CRITICAL FIXES:
- unified_session_manager.py (9 locations)
- thread_manager.py (2 locations)
- prompt_injection_manager.py (6 locations)
- database_toolkit modules (5 files)
- thread_sharing_manager.py (1 location)

USAGE:
    python scripts/maintenance/fix_core_module_connections.py
    
WARNING: This will modify source files! Commit your changes first!
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

class ConnectionFixer:
    def __init__(self):
        self.files_fixed = []
        self.total_replacements = 0
        self.dry_run = False  # Set to True to preview changes
        
    def fix_file(self, file_path: Path, schema_name: str = 'ai_infrastructure') -> int:
        """
        Fix database connections in a single file
        
        Args:
            file_path: Path to file to fix
            schema_name: Schema name to use (ai_infrastructure, sessions, etc.)
        
        Returns:
            Number of replacements made
        """
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            return 0
        
        print(f"\n📄 Processing: {file_path.relative_to(PROJECT_ROOT)}")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        replacements = 0
        
        # Pattern 1: Direct sqlite3.connect calls
        # BEFORE: conn = sqlite3.connect(self.db_path)
        # AFTER:  conn = get_database_connection('schema_name')
        
        patterns = [
            # Pattern 1: conn = sqlite3.connect(...)
            (
                r'(\s+)(conn\s*=\s*)sqlite3\.connect\([^)]+\)',
                rf'\1\2get_database_connection(\'{schema_name}\')'
            ),
            # Pattern 2: with sqlite3.connect(...) as conn:
            (
                r'(\s+)(with\s+)sqlite3\.connect\([^)]+\)(\s+as\s+conn:)',
                rf'\1\2get_database_connection(\'{schema_name}\')\3'
            ),
            # Pattern 3: return sqlite3.connect(...)
            (
                r'(return\s+)sqlite3\.connect\([^)]+\)',
                rf'\1get_database_connection(\'{schema_name}\')'
            ),
        ]
        
        for pattern, replacement in patterns:
            matches = list(re.finditer(pattern, content))
            if matches:
                content = re.sub(pattern, replacement, content)
                replacements += len(matches)
                print(f"  ✅ Replaced {len(matches)} direct connection(s)")
        
        # Check if import needs to be added
        if replacements > 0:
            if 'from shared.database_utils import get_database_connection' not in content:
                # Find import section (after docstring, before class definitions)
                lines = content.split('\n')
                insert_line = 0
                in_docstring = False
                
                for i, line in enumerate(lines):
                    # Skip docstrings
                    if '"""' in line or "'''" in line:
                        in_docstring = not in_docstring
                        continue
                    
                    if not in_docstring:
                        # Find first import statement
                        if line.strip().startswith('import ') or line.strip().startswith('from '):
                            insert_line = i
                            break
                
                # Insert import after other imports
                if insert_line > 0:
                    # Find last import in block
                    for i in range(insert_line, len(lines)):
                        if not (lines[i].strip().startswith('import ') or 
                               lines[i].strip().startswith('from ') or
                               lines[i].strip() == ''):
                            insert_line = i
                            break
                    
                    lines.insert(insert_line, 'from shared.database_utils import get_database_connection')
                    content = '\n'.join(lines)
                    print(f"  ✅ Added import statement")
        
        # Write back if changes were made
        if content != original_content:
            if not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  💾 Saved changes ({replacements} replacements)")
            else:
                print(f"  🔍 DRY RUN: Would make {replacements} replacements")
            
            self.files_fixed.append(file_path)
            self.total_replacements += replacements
        else:
            print(f"  ℹ️  No changes needed")
        
        return replacements
    
    def fix_all_core_modules(self):
        """Fix all core modules that bypass connection pool"""
        
        print("=" * 80)
        print("FIXING CORE MODULE DATABASE CONNECTIONS")
        print("=" * 80)
        
        # Priority 1: unified_session_manager.py
        print("\n🔴 PRIORITY 1: Session Manager")
        self.fix_file(
            PROJECT_ROOT / 'AI_infrastructure' / 'core' / 'unified_session_manager.py',
            schema_name='sessions'
        )
        
        # Priority 2: thread_manager.py
        print("\n🔴 PRIORITY 2: Thread Manager")
        self.fix_file(
            PROJECT_ROOT / 'AI_infrastructure' / 'thread_manager.py',
            schema_name='sessions'
        )
        
        # Priority 3: prompt_injection_manager.py
        print("\n🔴 PRIORITY 3: Prompt Injection Manager")
        self.fix_file(
            PROJECT_ROOT / 'AI_infrastructure' / 'core' / 'prompt_injection_manager.py',
            schema_name='ai_infrastructure'
        )
        
        # Priority 4: Database toolkit
        print("\n🟡 PRIORITY 4: Database Toolkit")
        toolkit_dir = PROJECT_ROOT / 'AI_infrastructure' / 'database_toolkit'
        if toolkit_dir.exists():
            for file_name in ['schema_manager.py', 'user_manager.py', 'query_tool.py', 
                             'session_manager.py', 'diagnostics.py']:
                file_path = toolkit_dir / file_name
                if file_path.exists():
                    self.fix_file(file_path, schema_name='ai_infrastructure')
        
        # Priority 5: thread_sharing_manager.py
        print("\n🟡 PRIORITY 5: Thread Sharing Manager")
        self.fix_file(
            PROJECT_ROOT / 'AI_infrastructure' / 'threads' / 'thread_sharing_manager.py',
            schema_name='sessions'
        )
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Files processed: {len(self.files_fixed)}")
        print(f"Total replacements: {self.total_replacements}")
        
        if self.files_fixed:
            print(f"\n✅ Files modified:")
            for file_path in self.files_fixed:
                print(f"  - {file_path.relative_to(PROJECT_ROOT)}")
        else:
            print(f"\nℹ️  No files needed changes")
        
        if not self.dry_run and self.total_replacements > 0:
            print(f"\n⚠️  IMPORTANT:")
            print(f"   1. Review changes with: git diff")
            print(f"   2. Test locally: BISTART")
            print(f"   3. Commit: git add . && git commit -m 'Fix: Update core modules to use connection pool'")
            print(f"   4. Deploy: git push origin v6")


def main():
    """Main entry point"""
    
    print("\n⚠️  WARNING: This will modify source files!")
    print("   Make sure you have committed your current changes first.\n")
    
    response = input("Continue? (y/N): ")
    if response.lower() != 'y':
        print("Aborted.")
        return
    
    fixer = ConnectionFixer()
    
    # Optional: Enable dry-run mode
    dry_run = input("\nDry run first? (recommended) (Y/n): ")
    if dry_run.lower() != 'n':
        print("\n🔍 DRY RUN MODE - No files will be modified")
        fixer.dry_run = True
        fixer.fix_all_core_modules()
        
        print("\n" + "=" * 80)
        proceed = input("\nProceed with actual changes? (y/N): ")
        if proceed.lower() != 'y':
            print("Aborted.")
            return
        
        # Reset and run for real
        fixer = ConnectionFixer()
        fixer.dry_run = False
    
    # Run fixes
    fixer.fix_all_core_modules()
    
    print("\n" + "=" * 80)
    print("✅ DONE")
    print("=" * 80)


if __name__ == '__main__':
    main()
