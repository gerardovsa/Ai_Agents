"""
OAuth Database Requirements Analysis
Extracts ALL table and column requirements from Google and Microsoft OAuth code
Compares with actual database schema to find missing columns
"""

import sqlite3
import re
import os
from pathlib import Path
from collections import defaultdict

# Color output helpers
def print_header(text):
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def print_section(text):
    print(f"\n--- {text} ---")

def print_error(text):
    print(f"ERROR: {text}")

def print_success(text):
    print(f"SUCCESS: {text}")

def print_warning(text):
    print(f"WARNING: {text}")


class OAuthDatabaseAnalyzer:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent.parent
        self.db_path = self.root_dir / 'data' / 'ai_infrastructure.db'
        
        # Files to analyze
        self.oauth_files = [
            'AI_infrastructure/routes/google_auth_routes_V2_FIXED.py',
            'AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py',
            'AI_infrastructure/routes/auth_routes.py',
            'AI_infrastructure/utils/email_alias_helpers.py',
            'AI_infrastructure/routes/thread_assignment_routes.py',
        ]
        
        # Track requirements
        self.required_columns = defaultdict(set)
        self.actual_columns = defaultdict(set)
        self.missing_columns = defaultdict(set)
        
    def extract_column_requirements(self):
        """Extract all column references from OAuth code"""
        print_header("EXTRACTING DATABASE REQUIREMENTS FROM OAUTH CODE")
        
        patterns = [
            # INSERT INTO table (col1, col2, ...) VALUES
            r'INSERT\s+INTO\s+(\w+)\s*\((.*?)\)\s*VALUES',
            # UPDATE table SET col1=?, col2=?
            r'UPDATE\s+(\w+)\s+SET\s+(.*?)\s+WHERE',
            # SELECT col1, col2 FROM table
            r'SELECT\s+(.*?)\s+FROM\s+(\w+)',
            # column = ? or column=?
            r'(\w+)\s*=\s*\?',
            # WHERE column IN
            r'WHERE\s+(\w+)\s+IN',
            # cursor['column']
            r"cursor\['(\w+)'\]",
            r'cursor\["(\w+)"\]',
            # row['column']
            r"row\['(\w+)'\]",
            r'row\["(\w+)"\]',
            # user['column']
            r"user\['(\w+)'\]",
            r'user\["(\w+)"\]',
        ]
        
        for file_path in self.oauth_files:
            full_path = self.root_dir / file_path
            if not full_path.exists():
                print_warning(f"File not found: {file_path}")
                continue
                
            print(f"Analyzing: {file_path}")
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find all SQL statements
            sql_statements = re.findall(r'(INSERT|UPDATE|SELECT|DELETE).*?(?=\n|$)', content, re.IGNORECASE | re.DOTALL)
            
            for statement in sql_statements:
                # Extract table name
                table_match = re.search(r'(?:FROM|INTO|UPDATE)\s+(\w+)', statement, re.IGNORECASE)
                if table_match:
                    table_name = table_match.group(1)
                    
                    # Extract column names
                    if 'INSERT INTO' in statement.upper():
                        cols_match = re.search(r'\((.*?)\)', statement)
                        if cols_match:
                            cols = [c.strip() for c in cols_match.group(1).split(',')]
                            for col in cols:
                                self.required_columns[table_name].add(col)
                                print(f"  {table_name}.{col} (INSERT)")
                    
                    elif 'UPDATE' in statement.upper():
                        set_match = re.search(r'SET\s+(.*?)\s+WHERE', statement, re.IGNORECASE)
                        if set_match:
                            updates = set_match.group(1).split(',')
                            for update in updates:
                                col = update.split('=')[0].strip()
                                self.required_columns[table_name].add(col)
                                print(f"  {table_name}.{col} (UPDATE)")
                    
                    elif 'SELECT' in statement.upper():
                        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', statement, re.IGNORECASE)
                        if select_match:
                            cols = select_match.group(1)
                            if cols.strip() != '*':
                                for col in cols.split(','):
                                    col = col.strip()
                                    if ' AS ' in col.upper():
                                        col = col.split()[0]
                                    self.required_columns[table_name].add(col)
                                    print(f"  {table_name}.{col} (SELECT)")
            
            # Find dictionary access patterns
            for pattern in [r"row\['(\w+)'\]", r'row\["(\w+)"\]', r"user\['(\w+)'\]", r'user\["(\w+)"\]']:
                matches = re.findall(pattern, content)
                for col in matches:
                    # These are likely from users or oauth_tokens tables
                    self.required_columns['users'].add(col)
                    self.required_columns['oauth_tokens'].add(col)
        
        print(f"\nFound requirements for {len(self.required_columns)} tables")
        for table, cols in self.required_columns.items():
            print(f"  {table}: {len(cols)} columns")
    
    def get_actual_schema(self):
        """Get actual database schema"""
        print_header("READING ACTUAL DATABASE SCHEMA")
        
        if not self.db_path.exists():
            print_error(f"Database not found: {self.db_path}")
            return
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"Found {len(tables)} tables in database")
        
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            print(f"\n{table} ({len(columns)} columns):")
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                self.actual_columns[table].add(col_name)
                print(f"  - {col_name} ({col_type})")
        
        conn.close()
    
    def compare_schemas(self):
        """Compare required vs actual columns"""
        print_header("COMPARING REQUIRED VS ACTUAL COLUMNS")
        
        all_tables = set(self.required_columns.keys()) | set(self.actual_columns.keys())
        
        for table in sorted(all_tables):
            required = self.required_columns.get(table, set())
            actual = self.actual_columns.get(table, set())
            missing = required - actual
            
            if missing:
                self.missing_columns[table] = missing
                print_section(f"{table} - MISSING COLUMNS")
                for col in sorted(missing):
                    print_error(f"  MISSING: {col}")
            
            extra = actual - required
            if extra:
                print_section(f"{table} - EXTRA COLUMNS (not used in code)")
                for col in sorted(extra):
                    print_warning(f"  EXTRA: {col}")
            
            if not missing and not extra:
                print_section(f"{table} - OK")
                print_success("  All required columns exist")
    
    def generate_migration_script(self):
        """Generate migration script for missing columns"""
        if not self.missing_columns:
            print_header("NO MIGRATION NEEDED")
            print_success("All required columns exist in database")
            return
        
        print_header("GENERATING MIGRATION SCRIPT")
        
        migration_path = self.root_dir / 'AI_infrastructure' / 'migrations' / 'add_all_missing_oauth_columns.py'
        
        migration_code = '''"""
CRITICAL MIGRATION: Add ALL missing OAuth columns
Generated from OAuth code analysis
"""

import sqlite3
from pathlib import Path

def run_migration():
    """Add all missing columns identified from OAuth code analysis"""
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / 'ai_infrastructure.db'
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print(f"Running OAuth columns migration on {db_path}")
    
    # Get current schema
    cursor.execute("PRAGMA table_info(users)")
    users_cols = {col[1] for col in cursor.fetchall()}
    
    cursor.execute("PRAGMA table_info(oauth_tokens)")
    oauth_cols = {col[1] for col in cursor.fetchall()}
    
'''
        
        # Add missing columns for each table
        for table, columns in sorted(self.missing_columns.items()):
            migration_code += f'\n    # {table} table\n'
            for col in sorted(columns):
                # Guess column type based on name
                col_type = 'TEXT'
                if any(x in col.lower() for x in ['id', 'count', 'attempts']):
                    col_type = 'INTEGER'
                elif any(x in col.lower() for x in ['timestamp', 'time', 'at', 'date']):
                    col_type = 'TEXT'  # Store as ISO format
                elif any(x in col.lower() for x in ['is_', 'has_', 'enabled', 'verified']):
                    col_type = 'INTEGER'  # Boolean as 0/1
                
                migration_code += f'''    if '{col}' not in {table}_cols:
        cursor.execute("ALTER TABLE {table} ADD COLUMN {col} {col_type}")
        print(f"  Added {table}.{col} ({col_type})")
    
'''
        
        migration_code += '''    conn.commit()
    conn.close()
    print(" Migration complete!")

if __name__ == '__main__':
    run_migration()
'''
        
        with open(migration_path, 'w', encoding='utf-8') as f:
            f.write(migration_code)
        
        print(f"Migration script created: {migration_path}")
        print("\nTo apply migration:")
        print(f"  python {migration_path}")
    
    def generate_summary_report(self):
        """Generate summary report"""
        print_header("SUMMARY REPORT")
        
        print(f"Total tables analyzed: {len(self.required_columns)}")
        print(f"Total tables in database: {len(self.actual_columns)}")
        
        total_missing = sum(len(cols) for cols in self.missing_columns.values())
        print(f"\nTotal missing columns: {total_missing}")
        
        if total_missing > 0:
            print("\nMISSING COLUMNS BY TABLE:")
            for table, cols in sorted(self.missing_columns.items()):
                print(f"  {table}: {len(cols)} missing")
                for col in sorted(cols):
                    print(f"    - {col}")
        else:
            print_success("\nAll required columns exist - database is up to date!")
        
        print(f"\nDatabase location: {self.db_path}")
        print(f"Database size: {self.db_path.stat().st_size / 1024:.1f} KB")
    
    def run_full_analysis(self):
        """Run complete analysis"""
        try:
            self.extract_column_requirements()
            self.get_actual_schema()
            self.compare_schemas()
            self.generate_migration_script()
            self.generate_summary_report()
            
            return len(self.missing_columns) == 0
            
        except Exception as e:
            print_error(f"Analysis failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    analyzer = OAuthDatabaseAnalyzer()
    success = analyzer.run_full_analysis()
    
    exit(0 if success else 1)
