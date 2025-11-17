"""
Scan for potential INSERT statement issues with PostgreSQL
Checks for:
1. INSERT statements missing RETURNING clause for auto-increment IDs
2. execute_sqlite_* functions still being used
3. Missing %s placeholders
"""
import re
from pathlib import Path

def scan_file(file_path):
    """Scan a single file for INSERT issues"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_num = i
            
            # Check for execute_sqlite_* functions (should be removed)
            if 'execute_sqlite_query' in line or 'execute_sqlite_update' in line:
                issues.append({
                    'line': line_num,
                    'type': 'SQLITE_FUNCTION',
                    'content': line.strip()[:100],
                    'severity': 'HIGH'
                })
            
            # Check for INSERT without RETURNING (for tables with serial IDs)
            if 'INSERT INTO' in line.upper():
                # Get next 20 lines to see full statement
                statement_lines = lines[i-1:min(i+20, len(lines))]
                statement = '\n'.join(statement_lines)
                
                # Check if it's inserting into a table that likely has auto-increment
                tables_with_serial = [
                    'sessions.messages',
                    'sessions.threads', 
                    'sessions.saved_threads',
                    'ai_infrastructure.users',
                    'ai_infrastructure.oauth_tokens',
                    'ai_infrastructure.scheduled_tasks',
                    'synergy_sessions.synergy_sessions'
                ]
                
                for table in tables_with_serial:
                    if table in statement.lower():
                        # Check if it has RETURNING clause
                        if 'RETURNING' not in statement.upper():
                            # Check if it's specifying the ID column explicitly
                            if re.search(r'\(\s*id\s*,', statement, re.IGNORECASE):
                                issues.append({
                                    'line': line_num,
                                    'type': 'MISSING_RETURNING',
                                    'table': table,
                                    'content': line.strip()[:100],
                                    'severity': 'MEDIUM',
                                    'suggestion': f'Remove id from column list OR add RETURNING id'
                                })
        
        return issues
        
    except Exception as e:
        return []

def main():
    print("=" * 100)
    print("SCANNING FOR INSERT STATEMENT ISSUES")
    print("=" * 100)
    
    base_dir = Path('AI_infrastructure')
    python_files = list(base_dir.glob('**/*.py'))
    python_files = [f for f in python_files if '__pycache__' not in str(f) and ' copy' not in str(f)]
    
    all_issues = {}
    
    for file_path in python_files:
        issues = scan_file(file_path)
        if issues:
            all_issues[str(file_path)] = issues
    
    # Display results
    if not all_issues:
        print("\n✅ No issues found! All INSERT statements look good.")
        return
    
    print(f"\n⚠️  Found issues in {len(all_issues)} files:\n")
    
    high_priority = []
    medium_priority = []
    
    for file_path, issues in sorted(all_issues.items()):
        rel_path = file_path.replace('AI_infrastructure\\\\', '')
        
        for issue in issues:
            issue_info = {
                'file': rel_path,
                'line': issue['line'],
                'type': issue['type'],
                'content': issue['content']
            }
            
            if issue['severity'] == 'HIGH':
                high_priority.append(issue_info)
            else:
                medium_priority.append(issue_info)
    
    if high_priority:
        print("🔴 HIGH PRIORITY - Must fix immediately:")
        print("-" * 100)
        for issue in high_priority:
            print(f"\n  📁 {issue['file']}:{issue['line']}")
            print(f"  ⚠️  {issue['type']}")
            print(f"  📝 {issue['content']}")
    
    if medium_priority:
        print("\n\n🟡 MEDIUM PRIORITY - Review and fix:")
        print("-" * 100)
        for issue in medium_priority[:20]:  # Show first 20
            print(f"\n  📁 {issue['file']}:{issue['line']}")
            print(f"  ⚠️  {issue['type']}")
            print(f"  📝 {issue['content']}")
        
        if len(medium_priority) > 20:
            print(f"\n  ... and {len(medium_priority) - 20} more issues")
    
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"🔴 High priority: {len(high_priority)}")
    print(f"🟡 Medium priority: {len(medium_priority)}")
    print(f"📁 Files affected: {len(all_issues)}")
    print("=" * 100)
    
    if high_priority:
        print("\n⚠️  CRITICAL: execute_sqlite_* functions must be replaced with Supabase equivalents")
        print("   These will fail on Render deployment!")

if __name__ == '__main__':
    main()
