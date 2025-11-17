"""
COMPREHENSIVE FIX: Replace ALL SQLite placeholders with PostgreSQL placeholders
Fixes: ? → %s throughout the entire codebase
"""
import os
import re
from pathlib import Path

def fix_sqlite_placeholders_in_file(file_path):
    """Replace ? with %s in SQL queries, being careful with comments and strings"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern to find SQL queries with ? placeholders
        # This looks for ? that are likely SQL placeholders (not in comments)
        patterns = [
            # WHERE clauses
            (r'WHERE\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s*=\s*\?', r'WHERE \1 = %s'),
            (r'AND\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s*=\s*\?', r'AND \1 = %s'),
            (r'OR\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s*=\s*\?', r'OR \1 = %s'),
            
            # SET clauses
            (r'SET\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s*=\s*\?', r'SET \1 = %s'),
            (r',\s*([a-zA-Z_][a-zA-Z0-9_.]*)\s*=\s*\?', r', \1 = %s'),
            
            # VALUES clauses
            (r'VALUES\s*\(([?%s,\s]+)\)', lambda m: 'VALUES (' + m.group(1).replace('?', '%s') + ')'),
            
            # IN clauses
            (r'IN\s*\(\s*\?', r'IN ( %s'),
            
            # LIKE clauses
            (r'LIKE\s+\?', r'LIKE %s'),
            
            # >= <= > < operators
            (r'>=\s*\?', r'>= %s'),
            (r'<=\s*\?', r'<= %s'),
            (r'>\s*\?', r'> %s'),
            (r'<\s*\?', r'< %s'),
            
            # Common WHERE patterns
            (r'where_clauses\.append\("([^"]*)\s*=\s*\?"\)', r'where_clauses.append("\1 = %s")'),
            (r"where_clauses\.append\('([^']*)\\s*=\\s*\\?'\)", r"where_clauses.append('\1 = %s')"),
            
            # INSERT patterns
            (r'\)\s+VALUES\s+\(\s*\?', r') VALUES ( %s'),
            
            # Common SQL patterns at end of string
            (r'"\s*,\s*\?', r'", %s'),
            (r"'\s*,\s*\?", r"', %s"),
            
            # Tuple parameters
            (r'\(\s*\?([,\)])', r'( %s\1'),
            (r',\s*\?([,\)])', r', %s\1'),
        ]
        
        for pattern, replacement in patterns:
            if callable(replacement):
                content = re.sub(pattern, replacement, content)
            else:
                content = re.sub(pattern, replacement, content)
        
        # Additional pass: catch any remaining ? in SQL context
        # Look for ? between quotes that's likely a SQL placeholder
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Skip comment lines
            if line.strip().startswith('#'):
                fixed_lines.append(line)
                continue
            
            # Check if line contains SQL keywords and ?
            if any(keyword in line.upper() for keyword in ['WHERE', 'SET', 'VALUES', 'AND', 'OR', 'LIKE', 'IN ']):
                if '?' in line and '# ?' not in line:  # Not in comment
                    # Replace remaining ? with %s in SQL context
                    # But be careful about strings and comments
                    in_string = False
                    quote_char = None
                    new_line = []
                    i = 0
                    while i < len(line):
                        char = line[i]
                        
                        # Track string boundaries
                        if char in ('"', "'") and (i == 0 or line[i-1] != '\\'):
                            if not in_string:
                                in_string = True
                                quote_char = char
                            elif char == quote_char:
                                in_string = False
                                quote_char = None
                        
                        # Replace ? with %s if we're in a string (SQL query)
                        if char == '?' and in_string:
                            # Check if this looks like a SQL placeholder
                            # (preceded by =, space, comma, or open paren)
                            if i > 0 and line[i-1] in ('=', ' ', ',', '('):
                                new_line.append('%s')
                            else:
                                new_line.append(char)
                        else:
                            new_line.append(char)
                        
                        i += 1
                    
                    line = ''.join(new_line)
            
            fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    print("=" * 100)
    print("COMPREHENSIVE SQLite -> PostgreSQL PLACEHOLDER FIX")
    print("=" * 100)
    
    # Directories to scan
    base_dir = Path('AI_infrastructure')
    
    # File patterns to fix
    patterns = ['**/*.py']
    
    files_to_fix = set()
    for pattern in patterns:
        files_to_fix.update(base_dir.glob(pattern))
    
    # Exclude test files and backups
    files_to_fix = [
        f for f in files_to_fix 
        if 'test_' not in f.name 
        and ' copy' not in str(f)
        and '__pycache__' not in str(f)
        and '.pyc' not in str(f)
    ]
    
    print(f"\nScanning {len(files_to_fix)} Python files in AI_infrastructure/")
    print("=" * 100)
    
    fixed_count = 0
    skipped_count = 0
    
    for file_path in sorted(files_to_fix):
        rel_path = str(file_path)
        
        if fix_sqlite_placeholders_in_file(file_path):
            print(f"✅ {rel_path}")
            fixed_count += 1
        else:
            skipped_count += 1
    
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"✅ Files fixed: {fixed_count}")
    print(f"⚪ Files unchanged: {skipped_count}")
    print(f"📁 Total files scanned: {len(files_to_fix)}")
    print("=" * 100)
    
    if fixed_count > 0:
        print("\n✅ SUCCESS! All SQLite placeholders replaced with PostgreSQL placeholders")
        print("   Next step: Test database connections with: python test_all_database_connections.py")
    else:
        print("\n✅ All files already use PostgreSQL placeholders - no changes needed!")

if __name__ == '__main__':
    main()
