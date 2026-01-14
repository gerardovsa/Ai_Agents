"""
Complete Database and API System Structure Visualizer with Script Validation

Analyzes databases, scripts, API routes, and detects inconsistencies
"""

import sqlite3
from pathlib import Path
import sys
import re
from collections import defaultdict


class DatabaseAnalyzer:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.databases = {}
        self.load_databases()
    
    def load_databases(self):
        """Load all non-backup databases"""
        for db_file in self.data_dir.glob("*.db"):
            if "backup" not in db_file.name.lower():
                self.databases[db_file.name] = self.analyze_database(db_file)
    
    def analyze_database(self, db_path):
        """Analyze single database structure"""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row['name'] for row in cursor.fetchall()]
        
        db_info = {
            'path': str(db_path),
            'size': db_path.stat().st_size,
            'tables': {}
        }
        
        for table_name in tables:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()['count']
            
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            foreign_keys = [dict(row) for row in cursor.fetchall()]
            
            # Fetch sample data for each column (up to 3 distinct examples)
            column_examples = {}
            for col in columns:
                col_name = col['name']
                try:
                    # Get distinct non-null examples
                    cursor.execute(f"""
                        SELECT DISTINCT {col_name} 
                        FROM {table_name} 
                        WHERE {col_name} IS NOT NULL 
                        LIMIT 3
                    """)
                    examples = [row[0] for row in cursor.fetchall()]
                    column_examples[col_name] = examples
                except:
                    column_examples[col_name] = []
            
            db_info['tables'][table_name] = {
                'columns': columns,
                'row_count': count,
                'foreign_keys': foreign_keys,
                'column_examples': column_examples
            }
        
        conn.close()
        return db_info


class ScriptAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.scripts = []
        self.scan_scripts()
    
    def scan_scripts(self):
        """Scan Python and JavaScript files only"""
        exclude_dirs = {'__pycache__', '.git', 'venv', '.venv', 'node_modules', 'archive', 'archived', 'Archive', 'Archived'}
        exclude_patterns = ['test_', 'fix_', 'TEST_', 'FIX_']
        
        # Scan both .py and .js files
        for pattern in ["*.py", "*.js"]:
            for script_file in self.project_root.rglob(pattern):
                # Skip excluded directories
                if any(excluded in script_file.parts for excluded in exclude_dirs):
                    continue
                
                # Skip root folder files (only files in subfolders)
                if script_file.parent == self.project_root:
                    continue
                
                # Skip test and fix files
                if any(script_file.name.startswith(pattern) for pattern in exclude_patterns):
                    continue
                
                script_info = self.analyze_script(script_file)
                if script_info['db_connections'] or script_info['table_accesses']:
                    self.scripts.append(script_info)
    
    def analyze_script(self, script_path):
        """Analyze script for database patterns"""
        try:
            content = script_path.read_text(encoding='utf-8', errors='ignore')
        except:
            return {'path': str(script_path), 'db_connections': [], 'table_accesses': [], 'error': True}
        
        db_connections = []
        table_accesses = []
        
        # Find database connections
        patterns = [
            r'sqlite3\.connect\([\'"]([^\'"]+)[\'"]',
            r'DATABASE_PATH\s*=\s*[\'"]([^\'"]+)[\'"]',
            r'db_path\s*=\s*[\'"]([^\'"]+)[\'"]'
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                db_path = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                db_connections.append({'path': db_path, 'line': line_num})
        
        # Find table accesses
        for match in re.finditer(r'FROM\s+(\w+)', content, re.IGNORECASE):
            table_accesses.append(match.group(1))
        for match in re.finditer(r'INTO\s+(\w+)', content, re.IGNORECASE):
            table_accesses.append(match.group(1))
        
        return {
            'path': str(script_path.relative_to(self.project_root)),
            'full_path': str(script_path),
            'db_connections': db_connections,
            'table_accesses': list(set(table_accesses)),
            'lines': len(content.split('\n'))
        }


class APIAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.routes = []
        self.scan_routes()
    
    def scan_routes(self):
        """Scan Flask route files"""
        routes_dir = self.project_root / 'AI_infrastructure' / 'routes'
        
        if not routes_dir.exists():
            return
        
        for route_file in routes_dir.glob("*_routes.py"):
            route_info = self.analyze_route_file(route_file)
            self.routes.extend(route_info)
    
    def analyze_route_file(self, route_path):
        """Analyze Flask route file"""
        try:
            content = route_path.read_text(encoding='utf-8', errors='ignore')
        except:
            return []
        
        routes = []
        route_pattern = r'@\w+\.route\([\'"]([^\'"]+)[\'"]'
        
        for match in re.finditer(route_pattern, content):
            endpoint = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            
            # Find database paths near route
            route_start = match.start()
            route_end = content.find('\n@', route_start + 1)
            if route_end == -1:
                route_end = len(content)
            
            route_section = content[route_start:route_end]
            
            db_paths = []
            for db_match in re.finditer(r'[\'"]([^\'"]*\.db)[\'"]', route_section):
                db_path = db_match.group(1)
                if 'backup' not in db_path.lower():
                    db_paths.append(db_path)
            
            tables = []
            for table_match in re.finditer(r'FROM\s+(\w+)', route_section, re.IGNORECASE):
                tables.append(table_match.group(1))
            
            routes.append({
                'endpoint': endpoint,
                'file': route_path.name,
                'line': line_num,
                'databases': list(set(db_paths)),
                'tables': list(set(tables))
            })
        
        return routes


class InconsistencyDetector:
    def __init__(self, db_analyzer, script_analyzer):
        self.db_analyzer = db_analyzer
        self.script_analyzer = script_analyzer
        self.issues = []
    
    def detect_all_issues(self):
        """Run all checks"""
        self.check_missing_databases()
        self.check_missing_tables()
        self.check_incorrect_paths()
        return self.issues
    
    def check_missing_databases(self):
        """Check for non-existent databases"""
        existing_dbs = set(self.db_analyzer.databases.keys())
        
        for script in self.script_analyzer.scripts:
            for conn in script['db_connections']:
                db_name = Path(conn['path']).name
                if db_name not in existing_dbs and 'backup' not in db_name.lower():
                    self.issues.append({
                        'type': 'MISSING_DATABASE',
                        'severity': 'HIGH',
                        'file': script['path'],
                        'line': conn['line'],
                        'database': db_name,
                        'message': f"References non-existent database: {db_name}"
                    })
    
    def check_missing_tables(self):
        """Check for non-existent tables"""
        table_map = {}
        for db_name, db_info in self.db_analyzer.databases.items():
            for table_name in db_info['tables'].keys():
                if table_name not in table_map:
                    table_map[table_name] = []
                table_map[table_name].append(db_name)
        
        for script in self.script_analyzer.scripts:
            for table in script['table_accesses']:
                if table not in table_map and table not in ['sqlite_master', 'sqlite_sequence']:
                    self.issues.append({
                        'type': 'MISSING_TABLE',
                        'severity': 'HIGH',
                        'file': script['path'],
                        'table': table,
                        'message': f"References non-existent table: {table}"
                    })
    
    def check_incorrect_paths(self):
        """Check for incorrect paths"""
        correct_patterns = [
            r'data/.*\.db',
            r'data\\.*\.db',
            r'Path.*data.*\.db'
        ]
        
        for script in self.script_analyzer.scripts:
            for conn in script['db_connections']:
                db_path = conn['path']
                is_correct = any(re.search(pattern, db_path) for pattern in correct_patterns)
                
                if not is_correct and 'AI_infrastructure' in db_path:
                    self.issues.append({
                        'type': 'INCORRECT_PATH',
                        'severity': 'MEDIUM',
                        'file': script['path'],
                        'line': conn['line'],
                        'path': db_path,
                        'message': f"Should use data/ folder: {db_path}"
                    })


def print_section(title, char="="):
    """Print section header"""
    print(f"\n{char * 100}")
    print(f"{title}")
    print(f"{char * 100}\n")


def _format_examples(examples):
    """Format example values for display"""
    formatted = []
    for ex in examples[:3]:
        if ex is None:
            formatted.append("NULL")
        elif isinstance(ex, str):
            # Truncate long strings
            if len(ex) > 50:
                formatted.append(f'"{ex[:47]}..."')
            else:
                formatted.append(f'"{ex}"')
        elif isinstance(ex, (int, float)):
            formatted.append(str(ex))
        else:
            formatted.append(str(ex)[:50])
    return ", ".join(formatted)


def print_database_structure(db_analyzer):
    """Print database structure with example data"""
    print_section("DATABASE STRUCTURE WITH EXAMPLE DATA")
    
    for db_name, db_info in sorted(db_analyzer.databases.items()):
        print(f"\n{'#' * 100}")
        print(f"DATABASE: {db_name}")
        print(f"Location: {db_info['path']}")
        print(f"Size: {db_info['size']:,} bytes")
        print(f"Tables: {len(db_info['tables'])}")
        print(f"{'#' * 100}\n")
        
        for table_name, table_info in sorted(db_info['tables'].items()):
            print(f"  TABLE: {table_name} - {table_info['row_count']:,} rows")
            print(f"  {'-' * 96}")
            
            column_examples = table_info.get('column_examples', {})
            
            for col in table_info['columns']:
                pk = " [PK]" if col['pk'] else ""
                nn = " [NOT NULL]" if col['notnull'] else ""
                col_name = col['name']
                col_type = col['type']
                
                # Format column header
                print(f"    {col_name:<30} {col_type:<15}{pk}{nn}")
                
                # Show example data if available
                examples = column_examples.get(col_name, [])
                if examples:
                    example_str = _format_examples(examples)
                    print(f"      Examples: {example_str}")
                elif table_info['row_count'] > 0:
                    print(f"      Examples: (all NULL)")
                else:
                    print(f"      Examples: (table empty)")
            
            if table_info['foreign_keys']:
                print(f"\n  Foreign Keys:")
                for fk in table_info['foreign_keys']:
                    print(f"    {fk['from']} -> {fk['table']}.{fk['to']}")
            print()


def print_script_analysis(script_analyzer):
    """Print script analysis"""
    print_section("SCRIPT DATABASE ACCESS ANALYSIS")
    
    print(f"Total scripts with database access: {len(script_analyzer.scripts)}\n")
    
    by_directory = defaultdict(list)
    for script in script_analyzer.scripts:
        directory = str(Path(script['path']).parent)
        by_directory[directory].append(script)
    
    for directory, scripts in sorted(by_directory.items())[:15]:
        print(f"\n{'#' * 100}")
        print(f"DIRECTORY: {directory}")
        print(f"{'#' * 100}")
        
        for script in sorted(scripts, key=lambda x: x['path'])[:10]:
            print(f"\n  FILE: {Path(script['path']).name} ({script['lines']} lines)")
            
            if script['db_connections']:
                print(f"  Database Connections:")
                for conn in script['db_connections'][:3]:
                    print(f"    Line {conn['line']}: {conn['path']}")
            
            if script['table_accesses']:
                print(f"  Tables: {', '.join(sorted(script['table_accesses'])[:10])}")


def print_api_analysis(api_analyzer):
    """Print API analysis"""
    print_section("API ROUTES TO DATABASE CONNECTIONS")
    
    print(f"Total API routes: {len(api_analyzer.routes)}\n")
    
    by_database = defaultdict(list)
    no_database = []
    
    for route in api_analyzer.routes:
        if route['databases']:
            for db in route['databases']:
                by_database[db].append(route)
        else:
            no_database.append(route)
    
    for db_name, routes in sorted(by_database.items()):
        print(f"\n{'#' * 100}")
        print(f"DATABASE: {db_name}")
        print(f"{'#' * 100}")
        
        for route in sorted(routes, key=lambda x: x['endpoint'])[:20]:
            tables = ', '.join(route['tables'][:3]) if route['tables'] else '(none)'
            print(f"  {route['endpoint']:<50} Tables: {tables}")
    
    if no_database:
        print(f"\n{'#' * 100}")
        print(f"ROUTES WITHOUT EXPLICIT DATABASE ({len(no_database)} routes)")
        print(f"{'#' * 100}")
        for route in no_database[:15]:
            print(f"  {route['endpoint']} in {route['file']}")


def print_inconsistencies(issues):
    """Print issues"""
    print_section("INCONSISTENCY DETECTION REPORT")
    
    if not issues:
        print("SUCCESS - No inconsistencies detected\n")
        return
    
    by_severity = defaultdict(list)
    for issue in issues:
        by_severity[issue['severity']].append(issue)
    
    print(f"WARNING - Total Issues: {len(issues)}")
    print(f"  HIGH: {len(by_severity['HIGH'])}")
    print(f"  MEDIUM: {len(by_severity['MEDIUM'])}\n")
    
    for severity in ['HIGH', 'MEDIUM']:
        if severity not in by_severity:
            continue
        
        print(f"\n{'#' * 100}")
        print(f"{severity} SEVERITY ({len(by_severity[severity])})")
        print(f"{'#' * 100}")
        
        by_type = defaultdict(list)
        for issue in by_severity[severity]:
            by_type[issue['type']].append(issue)
        
        for issue_type, type_issues in sorted(by_type.items()):
            print(f"\n  {issue_type} ({len(type_issues)} issues):")
            for issue in type_issues[:10]:
                print(f"    ERROR: {issue['message']}")
                print(f"    File: {issue['file']}")
                if 'line' in issue:
                    print(f"    Line: {issue['line']}")
                if 'database' in issue:
                    print(f"    Database: {issue['database']}")
                if 'table' in issue:
                    print(f"    Table: {issue['table']}")
                print()


def print_ui_mapping():
    """Print UI to data source mapping"""
    print_section("UI ELEMENT TO DATA SOURCE MAPPING")
    
    print("""
1. THREAD LIST (Left Sidebar)
   Data Source: sessions.db.threads
   API: GET /api/threads
   Key Fields: thread_slug, last_agent_location, last_message_timestamp

2. MESSAGE HISTORY (Chat Area)
   Data Source: sessions.db.messages
   API: GET /api/threads/<thread_slug>/messages
   Key Fields: role, content, timestamp, tool_calls

3. AGENT SELECTOR (Top Bar)
   Data Source: thread_assignments.location
   API: GET /api/thread-assignments/<thread_slug>
   Values: 'prime', 'agent-1', 'agent-2', 'agent-3', 'agent-4'

4. USER PROFILE (Account Menu)
   Data Source: ai_infrastructure.db.users
   API: GET /api/auth/me
   Key Fields: username, email, role, primary_gmail

5. SUB-USER MANAGEMENT (Settings)
   Data Source: ai_infrastructure.db.users (WHERE is_sub_user = 1)
   API: GET /api/users/sub-users
   Fields: allowed_tools, allowed_agents, data_access_scope
""")


def print_debugging_guide():
    """Print debugging guide"""
    print_section("DEBUGGING GUIDE")
    
    print("""
COMMON ISSUES:

1. "Table not found" error
   - Check database connection path (should be data/xxx.db)
   - Verify table exists with this script
   - Check spelling and case sensitivity

2. "Database is locked" error
   - Check for unclosed connections
   - Use: with sqlite3.connect() as conn:
   - Enable WAL mode: PRAGMA journal_mode=WAL

3. API returns empty data
   - Check row counts in this script
   - Verify WHERE clauses not too restrictive
   - Test query in sqlite3 CLI

4. Foreign key constraint failed
   - Check parent record exists
   - Enable foreign keys: PRAGMA foreign_keys = ON
   - Use correct ID type (INTEGER vs TEXT)

5. Permission denied
   - Pass _user_id to execute_tool()
   - Check user permissions in users table
   - Verify allowed_tools, allowed_agents fields
""")


def main():
    """Main execution"""
    project_root = Path(__file__).parent.parent
    data_dir = Path(__file__).parent
    
    print("\n" + "=" * 100)
    print("AI AGENTS PLATFORM - COMPLETE SYSTEM ANALYSIS")
    print("=" * 100)
    print(f"Project: {project_root}")
    print(f"Data: {data_dir}")
    
    print("\nInitializing analyzers...")
    db_analyzer = DatabaseAnalyzer(data_dir)
    print(f"  Databases: {len(db_analyzer.databases)}")
    
    script_analyzer = ScriptAnalyzer(project_root)
    print(f"  Scripts: {len(script_analyzer.scripts)}")
    
    api_analyzer = APIAnalyzer(project_root)
    print(f"  API Routes: {len(api_analyzer.routes)}")
    
    inconsistency_detector = InconsistencyDetector(db_analyzer, script_analyzer)
    issues = inconsistency_detector.detect_all_issues()
    print(f"  Issues: {len(issues)}")
    
    # Print all sections
    print_database_structure(db_analyzer)
    print_script_analysis(script_analyzer)
    print_api_analysis(api_analyzer)
    print_inconsistencies(issues)
    print_ui_mapping()
    print_debugging_guide()
    
    print("\n" + "=" * 100)
    print("ANALYSIS COMPLETE")
    print("=" * 100)
    
    # Save to file in data folder
    output_file = data_dir / 'database_analysis_report.txt'
    print(f"\nSaving report to: {output_file}")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Redirect stdout to file
            import sys
            original_stdout = sys.stdout
            sys.stdout = f
            
            # Re-run all print functions to file
            print_database_structure(db_analyzer)
            print_script_analysis(script_analyzer)
            print_api_analysis(api_analyzer)
            print_inconsistencies(issues)
            print_ui_mapping()
            print_debugging_guide()
            
            print("\n" + "=" * 100)
            print("ANALYSIS COMPLETE")
            print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 100)
            
            # Restore stdout
            sys.stdout = original_stdout
        
        print(f"SUCCESS: Report saved successfully!")
        print(f"File: {output_file.name}")
        print(f"Location: {output_file.parent}")
        
    except Exception as e:
        print(f"ERROR: Failed to save report: {e}")


if __name__ == '__main__':
    from datetime import datetime
    main()
