"""
Fix all SQLite placeholders (?) to PostgreSQL placeholders (%s)
This script scans and fixes all Python files in AI_infrastructure
"""
import os
import re
from pathlib import Path

def fix_sql_placeholders(file_path):
    """Fix SQLite placeholders in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # Pattern 1: WHERE column = ?
        pattern1 = r'(WHERE\s+\w+\s*=\s*)\?'
        matches1 = re.findall(pattern1, content, re.IGNORECASE)
        if matches1:
            content = re.sub(pattern1, r'\1%s', content, flags=re.IGNORECASE)
            changes_made.append(f"WHERE clauses: {len(matches1)}")
        
        # Pattern 2: AND column = ?
        pattern2 = r'(AND\s+\w+[\.\w]*\s*=\s*)\?'
        matches2 = re.findall(pattern2, content, re.IGNORECASE)
        if matches2:
            content = re.sub(pattern2, r'\1%s', content, flags=re.IGNORECASE)
            changes_made.append(f"AND clauses: {len(matches2)}")
        
        # Pattern 3: SET column = ?
        pattern3 = r'(SET\s+\w+\s*=\s*)\?'
        matches3 = re.findall(pattern3, content, re.IGNORECASE)
        if matches3:
            content = re.sub(pattern3, r'\1%s', content, flags=re.IGNORECASE)
            changes_made.append(f"SET clauses: {len(matches3)}")
        
        # Pattern 4: VALUES (?, ?, ...)
        pattern4 = r'\?(?=\s*[,\)])'
        matches4 = re.findall(r'VALUES\s*\([^\)]*\?[^\)]*\)', content, re.IGNORECASE)
        if matches4:
            # Only replace ? in VALUES clauses
            def replace_in_values(match):
                return match.group(0).replace('?', '%s')
            content = re.sub(r'VALUES\s*\([^\)]+\)', replace_in_values, content, flags=re.IGNORECASE)
            changes_made.append(f"VALUES clauses: {len(matches4)}")
        
        # Pattern 5: IN (?, ?, ...)
        pattern5 = r'IN\s*\([^\)]*\?[^\)]*\)'
        matches5 = re.findall(pattern5, content, re.IGNORECASE)
        if matches5:
            def replace_in_clause(match):
                return match.group(0).replace('?', '%s')
            content = re.sub(pattern5, replace_in_clause, content, flags=re.IGNORECASE)
            changes_made.append(f"IN clauses: {len(matches5)}")
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes_made
        
        return False, []
        
    except Exception as e:
        print(f"ERROR processing {file_path}: {str(e)}")
        return False, []

def scan_and_fix(directory):
    """Scan directory for Python files and fix placeholders"""
    fixed_files = []
    skipped_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip __pycache__ and .git directories
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules', 'venv']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                
                # Skip test files and backup files
                if 'test_' in file or file.endswith('.bak') or ' copy' in str(file_path):
                    skipped_files.append(str(file_path))
                    continue
                
                changed, changes = fix_sql_placeholders(file_path)
                if changed:
                    fixed_files.append((str(file_path), changes))
    
    return fixed_files, skipped_files

if __name__ == '__main__':
    print("=" * 80)
    print("SQL PLACEHOLDER FIX - SQLite (?) to PostgreSQL (%s)")
    print("=" * 80)
    
    ai_infra_dir = Path(__file__).parent / 'AI_infrastructure'
    
    print(f"\nScanning: {ai_infra_dir}")
    print("-" * 80)
    
    fixed, skipped = scan_and_fix(ai_infra_dir)
    
    if fixed:
        print(f"\n✅ FIXED {len(fixed)} files:\n")
        for file_path, changes in fixed:
            rel_path = Path(file_path).relative_to(Path(__file__).parent)
            print(f"  📝 {rel_path}")
            for change in changes:
                print(f"      - {change}")
    else:
        print("\n✅ No files needed fixing!")
    
    if skipped:
        print(f"\n⏭️  Skipped {len(skipped)} files (tests/backups)")
    
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
