"""
Check which database tables are actively used vs potentially unused
"""

import sqlite3
import os
from pathlib import Path

def analyze_table_usage():
    """Analyze which tables are used in the codebase"""
    
    root = Path(__file__).parent
    data_dir = root / 'data'
    
    # Database files
    databases = {
        'sessions.db': data_dir / 'sessions.db',
        'ai_infrastructure.db': data_dir / 'ai_infrastructure.db', 
        'synergy_sessions.db': data_dir / 'synergy_sessions.db'
    }
    
    print("=" * 80)
    print("DATABASE TABLE USAGE ANALYSIS")
    print("=" * 80)
    
    all_tables = {}
    
    # Get all tables from each database
    for db_name, db_path in databases.items():
        if not db_path.exists():
            print(f"\n⚠️  {db_name} not found at {db_path}")
            continue
            
        print(f"\n{'=' * 80}")
        print(f"DATABASE: {db_name}")
        print(f"{'=' * 80}")
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        
        tables = cursor.fetchall()
        
        for table_tuple in tables:
            table_name = table_tuple[0]
            
            # Get row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
            except:
                row_count = 0
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            col_names = [col[1] for col in columns]
            
            all_tables[f"{db_name}:{table_name}"] = {
                'db': db_name,
                'table': table_name,
                'rows': row_count,
                'columns': col_names
            }
            
            print(f"\n📊 {table_name}")
            print(f"   Rows: {row_count}")
            print(f"   Columns: {', '.join(col_names[:5])}{'...' if len(col_names) > 5 else ''}")
        
        conn.close()
    
    # Now check which tables are referenced in code
    print(f"\n{'=' * 80}")
    print("CODE USAGE ANALYSIS")
    print(f"{'=' * 80}")
    
    # Search for table references in Python files
    ai_infra_dir = root / 'AI_infrastructure'
    
    table_references = {}
    
    for db_table, info in all_tables.items():
        table_name = info['table']
        table_references[table_name] = {
            'files': [],
            'count': 0
        }
    
    # Search Python files
    for py_file in ai_infra_dir.rglob('*.py'):
        try:
            content = py_file.read_text(encoding='utf-8')
            
            for table_name in table_references.keys():
                # Look for table references (various patterns)
                patterns = [
                    f'FROM {table_name}',
                    f'INTO {table_name}',
                    f'UPDATE {table_name}',
                    f'TABLE {table_name}',
                    f'"{table_name}"',
                    f"'{table_name}'"
                ]
                
                found = False
                for pattern in patterns:
                    if pattern in content:
                        found = True
                        break
                
                if found:
                    rel_path = py_file.relative_to(root)
                    if str(rel_path) not in table_references[table_name]['files']:
                        table_references[table_name]['files'].append(str(rel_path))
                        table_references[table_name]['count'] += 1
        except:
            pass
    
    # Categorize tables
    print("\n✅ ACTIVELY USED TABLES (found in code):")
    print("-" * 80)
    
    used_tables = []
    for db_table, info in all_tables.items():
        table_name = info['table']
        refs = table_references.get(table_name, {'files': [], 'count': 0})
        
        if refs['count'] > 0:
            used_tables.append(table_name)
            print(f"\n📌 {info['db']}:{table_name}")
            print(f"   Rows: {info['rows']}")
            print(f"   Referenced in {refs['count']} files:")
            for file in refs['files'][:3]:
                print(f"   - {file}")
            if len(refs['files']) > 3:
                print(f"   ... and {len(refs['files']) - 3} more")
    
    print(f"\n\n⚠️  POTENTIALLY UNUSED TABLES (not found in code):")
    print("-" * 80)
    
    unused_tables = []
    for db_table, info in all_tables.items():
        table_name = info['table']
        refs = table_references.get(table_name, {'files': [], 'count': 0})
        
        if refs['count'] == 0:
            unused_tables.append(table_name)
            print(f"\n❌ {info['db']}:{table_name}")
            print(f"   Rows: {info['rows']}")
            print(f"   Columns: {', '.join(info['columns'][:5])}{'...' if len(info['columns']) > 5 else ''}")
            
            # Provide recommendation
            if info['rows'] == 0:
                print(f"   💡 Recommendation: SAFE TO DELETE (0 rows, no code references)")
            else:
                print(f"   ⚠️  Recommendation: CHECK CAREFULLY (has {info['rows']} rows but no code references)")
    
    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total tables: {len(all_tables)}")
    print(f"Used tables: {len(used_tables)}")
    print(f"Potentially unused: {len(unused_tables)}")
    print(f"\nUnused tables list: {', '.join(unused_tables)}")
    
    # Check for legacy/migration tables
    print(f"\n{'=' * 80}")
    print("LEGACY/MIGRATION ANALYSIS")
    print(f"{'=' * 80}")
    
    legacy_keywords = ['old', 'legacy', 'temp', 'backup', 'migration', 'archive']
    
    for db_table, info in all_tables.items():
        table_name = info['table'].lower()
        is_legacy = any(keyword in table_name for keyword in legacy_keywords)
        
        if is_legacy:
            print(f"\n🗄️  {info['db']}:{info['table']}")
            print(f"   Rows: {info['rows']}")
            print(f"   Appears to be legacy/migration table")

if __name__ == '__main__':
    analyze_table_usage()
