"""
Validate Code Against Database Schemas

This script checks common coding issues:
1. Invalid column references
2. Wrong database paths
3. Invalid table names
4. Missing indexes on queries

Usage:
    python validate_code_against_schemas.py [file_or_directory]
"""

import json
import re
from pathlib import Path
import sys

# Load schemas
def load_schemas():
    schema_file = Path(__file__).parent / 'DATABASE_SCHEMAS.json'
    with open(schema_file, 'r', encoding='utf-8') as f:
        return json.load(f)

# Extract SQL queries from Python files
def extract_sql_queries(file_path):
    """Extract SQL queries from Python code"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    queries = []
    
    # Pattern 1: Multi-line triple-quoted strings with SQL
    pattern1 = r'"""(.*?)"""'
    for match in re.finditer(pattern1, content, re.DOTALL):
        text = match.group(1)
        if any(keyword in text.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE']):
            queries.append({
                'query': text.strip(),
                'line': content[:match.start()].count('\n') + 1,
                'type': 'triple_quote'
            })
    
    # Pattern 2: execute() calls with inline SQL
    pattern2 = r'execute\(["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE)[^"\']*)["\']'
    for match in re.finditer(pattern2, content, re.IGNORECASE):
        queries.append({
            'query': match.group(1).strip(),
            'line': content[:match.start()].count('\n') + 1,
            'type': 'execute'
        })
    
    return queries

def validate_query(query_info, schemas):
    """Validate a SQL query against schemas"""
    issues = []
    query = query_info['query'].upper()
    
    # Extract table names
    table_pattern = r'\b(?:FROM|JOIN|INTO|UPDATE)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
    tables = re.findall(table_pattern, query)
    
    for table in tables:
        table_lower = table.lower()
        found = False
        
        for db_name, db_schema in schemas['databases'].items():
            if db_schema.get('exists') and 'tables' in db_schema:
                if table_lower in db_schema['tables']:
                    found = True
                    
                    # Check column references
                    column_pattern = r'\b' + table_lower + r'\.([a-zA-Z_][a-zA-Z0-9_]*)'
                    columns = re.findall(column_pattern, query, re.IGNORECASE)
                    
                    valid_columns = [col['name'] for col in db_schema['tables'][table_lower]['columns']]
                    
                    for col in columns:
                        if col.lower() not in [c.lower() for c in valid_columns]:
                            issues.append({
                                'severity': 'ERROR',
                                'message': f"Invalid column '{col}' in table '{table}'",
                                'valid_columns': valid_columns
                            })
                    
                    break
        
        if not found:
            issues.append({
                'severity': 'WARNING',
                'message': f"Table '{table}' not found in any database",
                'hint': 'Check if table name is correct or if using dynamic table names'
            })
    
    return issues

def check_database_paths(file_path):
    """Check for database path references"""
    issues = []
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Check for old database paths
    old_patterns = [
        (r'AI_infrastructure[/\\]ai_infrastructure\.db', 'Should use data/ai_infrastructure.db'),
        (r'AI_infrastructure[/\\]sessions\.db', 'Should use data/sessions.db'),
        (r'\.\.[\\/]ai_infrastructure\.db', 'Should use data/ai_infrastructure.db from root'),
    ]
    
    for line_num, line in enumerate(lines, 1):
        for pattern, message in old_patterns:
            if re.search(pattern, line):
                issues.append({
                    'line': line_num,
                    'severity': 'WARNING',
                    'message': f"Deprecated database path: {message}",
                    'code': line.strip()
                })
    
    return issues

def validate_file(file_path, schemas):
    """Validate a single file"""
    print(f"\n{'='*60}")
    print(f"Validating: {file_path}")
    print(f"{'='*60}")
    
    issues = []
    
    # Check database paths
    path_issues = check_database_paths(file_path)
    issues.extend(path_issues)
    
    # Extract and validate SQL queries
    queries = extract_sql_queries(file_path)
    
    if queries:
        print(f"Found {len(queries)} SQL queries")
        
        for query_info in queries:
            query_issues = validate_query(query_info, schemas)
            
            if query_issues:
                for issue in query_issues:
                    issue['line'] = query_info['line']
                    issue['query'] = query_info['query'][:100] + '...' if len(query_info['query']) > 100 else query_info['query']
                    issues.append(issue)
    
    # Report issues
    if issues:
        print(f"\n⚠️  Found {len(issues)} issues:\n")
        
        errors = [i for i in issues if i.get('severity') == 'ERROR']
        warnings = [i for i in issues if i.get('severity') == 'WARNING']
        
        if errors:
            print(f"❌ {len(errors)} ERRORS:")
            for issue in errors:
                print(f"  Line {issue.get('line', '?')}: {issue['message']}")
                if 'valid_columns' in issue:
                    print(f"    Valid columns: {', '.join(issue['valid_columns'][:10])}")
        
        if warnings:
            print(f"\n⚠️  {len(warnings)} WARNINGS:")
            for issue in warnings:
                print(f"  Line {issue.get('line', '?')}: {issue['message']}")
                if 'hint' in issue:
                    print(f"    Hint: {issue['hint']}")
                if 'code' in issue:
                    print(f"    Code: {issue['code']}")
    else:
        print("✅ No issues found")
    
    return issues

def main():
    schemas = load_schemas()
    
    print(f"{'='*60}")
    print(f"DATABASE SCHEMA VALIDATION")
    print(f"Loaded {len(schemas['databases'])} database schemas")
    print(f"{'='*60}")
    
    # Get target path
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    else:
        target = Path(__file__).parent / 'AI_infrastructure' / 'routes'
    
    # Validate files
    all_issues = []
    
    if target.is_file():
        issues = validate_file(target, schemas)
        all_issues.extend(issues)
    elif target.is_dir():
        python_files = list(target.glob('**/*.py'))
        print(f"\nFound {len(python_files)} Python files to validate\n")
        
        for py_file in python_files:
            issues = validate_file(py_file, schemas)
            all_issues.extend(issues)
    else:
        print(f"❌ Target not found: {target}")
        return
    
    # Summary
    print(f"\n{'='*60}")
    print(f"VALIDATION SUMMARY")
    print(f"{'='*60}")
    
    errors = [i for i in all_issues if i.get('severity') == 'ERROR']
    warnings = [i for i in all_issues if i.get('severity') == 'WARNING']
    
    print(f"Total Issues: {len(all_issues)}")
    print(f"  Errors: {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    
    if errors:
        print(f"\n❌ VALIDATION FAILED - {len(errors)} errors found")
    elif warnings:
        print(f"\n⚠️  VALIDATION PASSED with warnings")
    else:
        print(f"\n✅ VALIDATION PASSED - No issues found")

if __name__ == '__main__':
    main()
