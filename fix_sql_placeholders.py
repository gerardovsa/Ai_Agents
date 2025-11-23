"""
Auto-fix SQL placeholder syntax across all Python files
Converts SQLite (?) to PostgreSQL (%s) compatible code
"""

import os
import re
from pathlib import Path

def fix_sql_execute(content):
    """
    Convert cursor.execute() calls to use convert_sql_placeholders()
    
    Pattern: sql, params = convert_sql_placeholders('SQL with ?', (params,))
 cursor.execute(sql, params)
    Result: sql, params = convert_sql_placeholders('SQL with ?', (params,))
            cursor.execute(sql, params)
    """
    # Pattern 1: Single-line execute with parameters
    pattern1 = r"(\s+)(cursor\.execute\()(['\"])(.+?\?[^'\"]*?)(\3)\s*,\s*(\([^)]+\))\s*\)"
    
    def replace1(match):
        indent = match.group(1)
        execute_start = match.group(2)
        quote = match.group(3)
        sql = match.group(4)
        params = match.group(6)
        
        return (
            f"{indent}sql, params = convert_sql_placeholders({quote}{sql}{quote}, {params})\n"
            f"{indent}cursor.execute(sql, params)"
        )
    
    content = re.sub(pattern1, replace1, content)
    
    # Pattern 2: Multi-line execute with ''' or """
    pattern2 = r"(\s+)(cursor\.execute\()('''|\"\"\")(.*?)(\3)\s*,\s*(\([^)]+\))\s*\)"
    
    def replace2(match):
        indent = match.group(1)
        execute_start = match.group(2)
        quote = match.group(3)
        sql = match.group(4)
        params = match.group(6)
        
        return (
            f"{indent}sql, params = convert_sql_placeholders({quote}{sql}{quote}, {params})\n"
            f"{indent}cursor.execute(sql, params)"
        )
    
    content = re.sub(pattern2, replace2, content, flags=re.DOTALL)
    
    return content

def add_import(content, filepath):
    """Add convert_sql_placeholders to imports if needed"""
    if 'convert_sql_placeholders' in content:
        return content  # Already imported
    
    if '?' not in content:
        return content  # No SQL placeholders to fix
    
    # Find existing database_utils import
    import_pattern = r'from shared\.database_utils import ([^\n]+)'
    match = re.search(import_pattern, content)
    
    if match:
        # Add to existing import
        existing_imports = match.group(1)
        if 'convert_sql_placeholders' not in existing_imports:
            new_imports = existing_imports.rstrip() + ', convert_sql_placeholders'
            content = content.replace(
                f'from shared.database_utils import {existing_imports}',
                f'from shared.database_utils import {new_imports}'
            )
    else:
        # Check if file uses database connections
        if 'get_db_connection' in content or 'cursor.execute' in content:
            # Add import after other imports
            import_section = content[:content.find('\n\n')]
            new_import = '\nfrom shared.database_utils import convert_sql_placeholders'
            content = import_section + new_import + content[len(import_section):]
    
    return content

def process_file(filepath):
    """Process a single Python file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()
        
        if '?' not in original or 'cursor.execute' not in original:
            return False, "No SQL placeholders found"
        
        # Add import
        content = add_import(original, filepath)
        
        # Fix SQL executes
        content = fix_sql_execute(content)
        
        if content == original:
            return False, "No changes needed"
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, "Fixed"
    
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Process all Python files in AI_infrastructure"""
    # Scan the whole repository (project root) instead of only AI_infrastructure
    root = Path(__file__).parent
    
    print("=" * 80)
    print("SQL PLACEHOLDER AUTO-FIX")
    print("=" * 80)
    print(f"\nScanning: {root}\n")
    
    files_fixed = 0
    files_skipped = 0
    errors = 0
    
    for pyfile in root.rglob('*.py'):
        rel_path = pyfile.relative_to(root.parent)
        success, message = process_file(pyfile)
        
        if success:
            print(f"✅ {rel_path}")
            files_fixed += 1
        elif 'Error' in message:
            print(f"❌ {rel_path}: {message}")
            errors += 1
        else:
            files_skipped += 1
    
    print("\n" + "=" * 80)
    print(f"Fixed: {files_fixed} files")
    print(f"Skipped: {files_skipped} files")
    print(f"Errors: {errors} files")
    print("=" * 80)

if __name__ == '__main__':
    main()
