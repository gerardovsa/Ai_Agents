"""
CRITICAL FIX: Add sessions. schema prefix to ALL SQL queries

This script scans all Python files in AI_infrastructure and adds the sessions. prefix
to table names that are missing it.

Tables in sessions schema:
- threads
- messages
- api_sessions
- saved_threads
- sessions
- thread_shares
- thread_users
- workspaces
- users
"""

import os
import re
from pathlib import Path

# Tables that need sessions. prefix
SESSIONS_TABLES = [
    'threads',
    'messages',
    'api_sessions',
    'saved_threads',
    'sessions',
    'thread_shares',
    'thread_users',
    'workspaces',
    # Note: 'users' is in BOTH ai_infrastructure AND sessions schema
]

# Directories to scan
SCAN_DIRS = [
    'AI_infrastructure/routes',
    'AI_infrastructure/threads',
    'AI_infrastructure/core',
]

def find_unqualified_tables(file_path):
    """Find SQL queries with unqualified table names"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Skip comments
        if line.strip().startswith('#'):
            continue
        
        # Look for FROM/JOIN/INTO/UPDATE table_name patterns
        for table in SESSIONS_TABLES:
            # Pattern: FROM threads (without sessions. prefix)
            pattern = rf'\b(FROM|JOIN|INTO|UPDATE)\s+{table}\b(?!\s*\()'
            
            if re.search(pattern, line, re.IGNORECASE):
                # Check if it already has sessions. prefix
                if f'sessions.{table}' not in line.lower():
                    issues.append({
                        'line_num': line_num,
                        'line': line.strip(),
                        'table': table,
                        'file': file_path
                    })
    
    return issues

def scan_directory(base_dir):
    """Scan directory for Python files with SQL queries"""
    all_issues = []
    
    for scan_dir in SCAN_DIRS:
        dir_path = Path(base_dir) / scan_dir
        if not dir_path.exists():
            continue
        
        for py_file in dir_path.rglob('*.py'):
            issues = find_unqualified_tables(py_file)
            if issues:
                all_issues.extend(issues)
    
    return all_issues

def main():
    base_dir = Path(__file__).parent
    print("🔍 Scanning for missing sessions. schema prefixes...")
    print("=" * 80)
    
    all_issues = scan_directory(base_dir)
    
    if not all_issues:
        print("✅ No issues found! All queries have proper schema prefixes.")
        return
    
    # Group by file
    files_with_issues = {}
    for issue in all_issues:
        file_path = issue['file']
        if file_path not in files_with_issues:
            files_with_issues[file_path] = []
        files_with_issues[file_path].append(issue)
    
    print(f"❌ Found {len(all_issues)} issues in {len(files_with_issues)} files:\n")
    
    for file_path, issues in files_with_issues.items():
        rel_path = os.path.relpath(file_path, base_dir)
        print(f"\n📄 {rel_path} ({len(issues)} issues)")
        print("-" * 80)
        
        for issue in issues:
            print(f"  Line {issue['line_num']}: {issue['table']}")
            print(f"    {issue['line'][:100]}")
    
    print("\n" + "=" * 80)
    print(f"TOTAL: {len(all_issues)} missing schema prefixes")
    print("=" * 80)
    
    # Generate fix recommendations
    print("\n\n📋 FIX RECOMMENDATIONS:\n")
    
    for table in SESSIONS_TABLES:
        table_issues = [i for i in all_issues if i['table'] == table]
        if table_issues:
            print(f"\n{table}: {len(table_issues)} occurrences")
            print(f"  Find: FROM {table}")
            print(f"  Replace: FROM sessions.{table}")
            print(f"  (Also for JOIN, INTO, UPDATE)")

if __name__ == '__main__':
    main()
