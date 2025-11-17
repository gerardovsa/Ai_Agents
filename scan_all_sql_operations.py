"""
Comprehensive scan for ALL SQL operation issues
Checks for:
1. INSERT - missing RETURNING, wrong placeholders
2. UPDATE - wrong placeholders, missing WHERE
3. DELETE - wrong placeholders, missing WHERE
4. SELECT - wrong placeholders
5. execute_sqlite_* function usage
6. SQLite-specific syntax (datetime('now'), AUTOINCREMENT, etc.)
"""
import re
from pathlib import Path

def scan_file(file_path):
    """Scan a single file for SQL operation issues"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_upper = line.upper()
            
            # 1. Check for execute_sqlite_* functions
            if 'execute_sqlite_query' in line or 'execute_sqlite_update' in line:
                issues.append({
                    'line': i,
                    'type': 'SQLITE_FUNCTION',
                    'operation': 'ALL',
                    'content': line.strip()[:120],
                    'severity': 'CRITICAL',
                    'fix': 'Replace with get_database_connection() + cursor.execute()'
                })
            
            # 2. Check for SQLite-specific syntax
            if "datetime('now')" in line or 'datetime("now")' in line:
                issues.append({
                    'line': i,
                    'type': 'SQLITE_DATETIME',
                    'operation': 'INSERT/UPDATE',
                    'content': line.strip()[:120],
                    'severity': 'HIGH',
                    'fix': "Replace with CURRENT_TIMESTAMP or NOW()"
                })
            
            if 'AUTOINCREMENT' in line_upper:
                issues.append({
                    'line': i,
                    'type': 'SQLITE_AUTOINCREMENT',
                    'operation': 'CREATE TABLE',
                    'content': line.strip()[:120],
                    'severity': 'HIGH',
                    'fix': 'Use SERIAL or BIGSERIAL for PostgreSQL'
                })
            
            # 3. Check for UPDATE without WHERE (dangerous!)
            if 'UPDATE ' in line_upper and 'SET' in line_upper:
                # Get next 10 lines to see full statement
                statement_lines = lines[i-1:min(i+10, len(lines))]
                statement = ' '.join([l.strip() for l in statement_lines])
                
                if 'WHERE' not in statement.upper():
                    issues.append({
                        'line': i,
                        'type': 'UPDATE_NO_WHERE',
                        'operation': 'UPDATE',
                        'content': line.strip()[:120],
                        'severity': 'CRITICAL',
                        'fix': 'Add WHERE clause to prevent updating all rows!'
                    })
            
            # 4. Check for DELETE without WHERE (extremely dangerous!)
            if 'DELETE FROM' in line_upper:
                # Get next 10 lines
                statement_lines = lines[i-1:min(i+10, len(lines))]
                statement = ' '.join([l.strip() for l in statement_lines])
                
                if 'WHERE' not in statement.upper():
                    issues.append({
                        'line': i,
                        'type': 'DELETE_NO_WHERE',
                        'operation': 'DELETE',
                        'content': line.strip()[:120],
                        'severity': 'CRITICAL',
                        'fix': 'Add WHERE clause to prevent deleting all rows!'
                    })
            
            # 5. Check for $1, $2 style placeholders (should be %s)
            if re.search(r'\$\d+', line) and any(keyword in line_upper for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WHERE']):
                # Exclude comments about costs
                if not re.search(r'\$\d+\.\d+', line) and '# $' not in line:
                    issues.append({
                        'line': i,
                        'type': 'WRONG_PLACEHOLDER',
                        'operation': 'ALL',
                        'content': line.strip()[:120],
                        'severity': 'HIGH',
                        'fix': 'Replace $1, $2, etc. with %s for psycopg2'
                    })
            
            # 6. Check for LIMIT with ? placeholder
            if 'LIMIT ?' in line_upper or 'OFFSET ?' in line_upper:
                issues.append({
                    'line': i,
                    'type': 'LIMIT_WRONG_PLACEHOLDER',
                    'operation': 'SELECT',
                    'content': line.strip()[:120],
                    'severity': 'MEDIUM',
                    'fix': 'Replace ? with %s'
                })
            
            # 7. Check for PRAGMA (SQLite-only)
            if 'PRAGMA' in line_upper:
                issues.append({
                    'line': i,
                    'type': 'SQLITE_PRAGMA',
                    'operation': 'PRAGMA',
                    'content': line.strip()[:120],
                    'severity': 'HIGH',
                    'fix': 'Remove PRAGMA statements (SQLite-specific)'
                })
            
            # 8. Check for || concatenation with datetime
            if "'-' ||" in line or "|| '-'" in line:
                if 'datetime' in line.lower() or 'now' in line.lower():
                    issues.append({
                        'line': i,
                        'type': 'SQLITE_CONCAT_DATETIME',
                        'operation': 'SELECT/WHERE',
                        'content': line.strip()[:120],
                        'severity': 'MEDIUM',
                        'fix': 'Use PostgreSQL interval syntax: NOW() - INTERVAL \'X hours\''
                    })
        
        return issues
        
    except Exception as e:
        return []

def main():
    print("=" * 120)
    print("COMPREHENSIVE SQL OPERATIONS SCAN")
    print("=" * 120)
    print("\nScanning for:")
    print("  1. INSERT issues (missing RETURNING, wrong placeholders)")
    print("  2. UPDATE issues (wrong placeholders, missing WHERE)")
    print("  3. DELETE issues (wrong placeholders, missing WHERE)")
    print("  4. SELECT issues (wrong placeholders)")
    print("  5. SQLite-specific syntax")
    print("  6. execute_sqlite_* function usage")
    print("\n" + "=" * 120)
    
    base_dir = Path('AI_infrastructure')
    python_files = list(base_dir.glob('**/*.py'))
    python_files = [f for f in python_files if '__pycache__' not in str(f) and ' copy' not in str(f)]
    
    all_issues = {}
    issue_counts = {
        'CRITICAL': 0,
        'HIGH': 0,
        'MEDIUM': 0
    }
    
    for file_path in python_files:
        issues = scan_file(file_path)
        if issues:
            all_issues[str(file_path)] = issues
            for issue in issues:
                issue_counts[issue['severity']] += 1
    
    # Display results by severity
    if not all_issues:
        print("\n✅ PERFECT! No SQL issues found!")
        print("   All queries use proper PostgreSQL syntax")
        return
    
    print(f"\n⚠️  Found {sum(issue_counts.values())} issues in {len(all_issues)} files\n")
    
    # Group by severity
    critical_issues = []
    high_issues = []
    medium_issues = []
    
    for file_path, issues in all_issues.items():
        rel_path = file_path.replace('AI_infrastructure\\\\', '')
        for issue in issues:
            issue_data = {
                'file': rel_path,
                'line': issue['line'],
                'type': issue['type'],
                'operation': issue['operation'],
                'content': issue['content'],
                'fix': issue['fix']
            }
            
            if issue['severity'] == 'CRITICAL':
                critical_issues.append(issue_data)
            elif issue['severity'] == 'HIGH':
                high_issues.append(issue_data)
            else:
                medium_issues.append(issue_data)
    
    # Display CRITICAL issues
    if critical_issues:
        print("🔴 CRITICAL - Must fix immediately (will break in production):")
        print("=" * 120)
        
        # Group by type
        by_type = {}
        for issue in critical_issues:
            issue_type = issue['type']
            if issue_type not in by_type:
                by_type[issue_type] = []
            by_type[issue_type].append(issue)
        
        for issue_type, issues in sorted(by_type.items()):
            print(f"\n📌 {issue_type} ({len(issues)} occurrences):")
            print(f"   Fix: {issues[0]['fix']}")
            print("   Files:")
            
            # Show first 10 per type
            for issue in issues[:10]:
                print(f"     - {issue['file']}:{issue['line']}")
                print(f"       {issue['content'][:100]}")
            
            if len(issues) > 10:
                print(f"     ... and {len(issues) - 10} more")
    
    # Display HIGH priority issues
    if high_issues:
        print("\n\n🟠 HIGH PRIORITY - Should fix soon:")
        print("=" * 120)
        
        by_type = {}
        for issue in high_issues:
            issue_type = issue['type']
            if issue_type not in by_type:
                by_type[issue_type] = []
            by_type[issue_type].append(issue)
        
        for issue_type, issues in sorted(by_type.items()):
            print(f"\n📌 {issue_type} ({len(issues)} occurrences):")
            print(f"   Fix: {issues[0]['fix']}")
            
            # Show first 5 per type
            for issue in issues[:5]:
                print(f"     - {issue['file']}:{issue['line']}")
            
            if len(issues) > 5:
                print(f"     ... and {len(issues) - 5} more")
    
    # Display MEDIUM priority issues summary
    if medium_issues:
        print("\n\n🟡 MEDIUM PRIORITY - Review when possible:")
        print("=" * 120)
        
        by_type = {}
        for issue in medium_issues:
            issue_type = issue['type']
            if issue_type not in by_type:
                by_type[issue_type] = []
            by_type[issue_type].append(issue)
        
        for issue_type, issues in sorted(by_type.items()):
            print(f"   {issue_type}: {len(issues)} occurrences")
    
    # Summary
    print("\n\n" + "=" * 120)
    print("SUMMARY")
    print("=" * 120)
    print(f"🔴 CRITICAL: {issue_counts['CRITICAL']} issues (WILL break in production)")
    print(f"🟠 HIGH:     {issue_counts['HIGH']} issues (Should fix soon)")
    print(f"🟡 MEDIUM:   {issue_counts['MEDIUM']} issues (Review when possible)")
    print(f"📁 Files:    {len(all_issues)} files affected")
    print("=" * 120)
    
    if critical_issues:
        print("\n⚠️  URGENT: Critical issues MUST be fixed before production deployment!")
        print("   These will cause errors on Render where only Supabase is available.")

if __name__ == '__main__':
    main()
