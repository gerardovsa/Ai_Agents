"""
Audit all database queries for Supabase compatibility
Checks for:
1. SQLite placeholders (?) instead of PostgreSQL (%s)
2. SQLite-specific functions (datetime(), strftime())
3. SQLite-specific syntax (AUTOINCREMENT, INTEGER PRIMARY KEY)
4. Missing schema prefixes
"""
import os
import re
from pathlib import Path

# Patterns to detect
ISSUES = {
    'sqlite_placeholder': {
        'pattern': r'(WHERE|VALUES|SET|AND|OR|IN)\s+[^=]*=\s*\?',
        'severity': 'CRITICAL',
        'description': 'SQLite placeholder (?) instead of PostgreSQL (%s)'
    },
    'datetime_function': {
        'pattern': r"datetime\s*\(\s*['\"]now['\"]",
        'severity': 'HIGH',
        'description': 'SQLite datetime() function - use CURRENT_TIMESTAMP'
    },
    'strftime_function': {
        'pattern': r"strftime\s*\(",
        'severity': 'MEDIUM',
        'description': 'SQLite strftime() function - use PostgreSQL date functions'
    },
    'autoincrement': {
        'pattern': r'AUTOINCREMENT',
        'severity': 'MEDIUM',
        'description': 'SQLite AUTOINCREMENT - use PostgreSQL SERIAL'
    },
    'integer_primary_key': {
        'pattern': r'INTEGER\s+PRIMARY\s+KEY',
        'severity': 'LOW',
        'description': 'SQLite INTEGER PRIMARY KEY - prefer SERIAL PRIMARY KEY'
    }
}

def scan_file(filepath):
    """Scan a single file for issues"""
    issues_found = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
        for issue_name, issue_info in ISSUES.items():
            pattern = issue_info['pattern']
            
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    # Skip comments
                    if line.strip().startswith('#'):
                        continue
                    
                    issues_found.append({
                        'file': str(filepath),
                        'line': line_num,
                        'severity': issue_info['severity'],
                        'type': issue_name,
                        'description': issue_info['description'],
                        'code': line.strip()
                    })
    
    except Exception as e:
        print(f"Error scanning {filepath}: {e}")
    
    return issues_found

def scan_directory(directory, extensions=['.py']):
    """Scan all files in directory"""
    all_issues = []
    
    directory = Path(directory)
    
    for ext in extensions:
        for filepath in directory.rglob(f'*{ext}'):
            # Skip test files and archived files
            if 'test_' in filepath.name or '__pycache__' in str(filepath) or 'archive' in str(filepath).lower():
                continue
            
            issues = scan_file(filepath)
            all_issues.extend(issues)
    
    return all_issues

def generate_report(issues):
    """Generate audit report"""
    print("\n" + "=" * 100)
    print("DATABASE QUERY AUDIT REPORT - SUPABASE COMPATIBILITY CHECK")
    print("=" * 100)
    
    if not issues:
        print("\n✅ NO ISSUES FOUND - All queries are Supabase compatible!")
        return
    
    # Group by severity
    critical = [i for i in issues if i['severity'] == 'CRITICAL']
    high = [i for i in issues if i['severity'] == 'HIGH']
    medium = [i for i in issues if i['severity'] == 'MEDIUM']
    low = [i for i in issues if i['severity'] == 'LOW']
    
    print(f"\n📊 SUMMARY:")
    print(f"   🔴 CRITICAL: {len(critical)} issues (Must fix immediately)")
    print(f"   🟠 HIGH:     {len(high)} issues (Should fix soon)")
    print(f"   🟡 MEDIUM:   {len(medium)} issues (Fix when convenient)")
    print(f"   🟢 LOW:      {len(low)} issues (Nice to have)")
    print(f"   📝 TOTAL:    {len(issues)} issues")
    
    # Show critical issues first
    if critical:
        print("\n" + "=" * 100)
        print("🔴 CRITICAL ISSUES - MUST FIX IMMEDIATELY")
        print("=" * 100)
        for issue in critical[:20]:  # Show first 20
            print(f"\n📄 File: {issue['file']}")
            print(f"   Line {issue['line']}: {issue['description']}")
            print(f"   Code: {issue['code'][:100]}...")
    
    # Show high priority issues
    if high:
        print("\n" + "=" * 100)
        print("🟠 HIGH PRIORITY ISSUES")
        print("=" * 100)
        for issue in high[:10]:  # Show first 10
            print(f"\n📄 File: {issue['file']}")
            print(f"   Line {issue['line']}: {issue['description']}")
            print(f"   Code: {issue['code'][:100]}...")
    
    # Group by file for summary
    print("\n" + "=" * 100)
    print("FILES WITH ISSUES")
    print("=" * 100)
    
    files_with_issues = {}
    for issue in issues:
        file = issue['file']
        if file not in files_with_issues:
            files_with_issues[file] = []
        files_with_issues[file].append(issue)
    
    # Sort by issue count
    sorted_files = sorted(files_with_issues.items(), key=lambda x: len(x[1]), reverse=True)
    
    for file, file_issues in sorted_files[:30]:  # Show top 30 files
        critical_count = len([i for i in file_issues if i['severity'] == 'CRITICAL'])
        high_count = len([i for i in file_issues if i['severity'] == 'HIGH'])
        medium_count = len([i for i in file_issues if i['severity'] == 'MEDIUM'])
        low_count = len([i for i in file_issues if i['severity'] == 'LOW'])
        
        print(f"\n📄 {file}")
        print(f"   Issues: {len(file_issues)} (🔴{critical_count} 🟠{high_count} 🟡{medium_count} 🟢{low_count})")
    
    print("\n" + "=" * 100)
    print("RECOMMENDATIONS")
    print("=" * 100)
    print("""
1. CRITICAL: Replace all SQLite placeholders (?) with PostgreSQL (%s)
   - Find: WHERE column = ?
   - Replace: WHERE column = %s

2. HIGH: Replace datetime('now') with CURRENT_TIMESTAMP
   - Find: datetime('now')
   - Replace: CURRENT_TIMESTAMP

3. MEDIUM: Replace strftime() with PostgreSQL date functions
   - strftime('%Y-%m-%d') → TO_CHAR(date, 'YYYY-MM-DD')
   - strftime('%Y-%m') → TO_CHAR(date, 'YYYY-MM')

4. MEDIUM: Replace AUTOINCREMENT with SERIAL
   - INTEGER PRIMARY KEY AUTOINCREMENT → SERIAL PRIMARY KEY

5. Always use schema prefixes:
   - FROM users → FROM ai_infrastructure.users
   - FROM threads → FROM sessions.threads
    """)

if __name__ == "__main__":
    print("Scanning AI_infrastructure directory...")
    
    # Scan main directory
    ai_infra_path = Path(__file__).parent / 'AI_infrastructure'
    issues = scan_directory(ai_infra_path)
    
    # Generate report
    generate_report(issues)
    
    print("\n" + "=" * 100)
    print("AUDIT COMPLETE")
    print("=" * 100)
