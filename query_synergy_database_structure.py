"""
Query Synergy Sessions Database Structure
Analyzes synergy_sessions schema and documents all tables and their structure
"""

import sys
sys.path.insert(0, 'c:\\Users\\gpoli\\GIT\\AI_agents\\AI_infrastructure')

from shared.database_utils import get_synergy_sessions_connection

def get_all_tables(conn):
    """Get all tables in synergy_sessions schema"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'synergy_sessions' 
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    cursor.close()
    return [t['table_name'] for t in tables]

def get_table_columns(conn, table_name):
    """Get all columns for a specific table"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'synergy_sessions' 
        AND table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    columns = cursor.fetchall()
    cursor.close()
    # Return as tuples for unpacking
    return [(c['column_name'], c['data_type'], c['character_maximum_length'], 
             c['is_nullable'], c['column_default']) for c in columns]

def get_table_indexes(conn, table_name):
    """Get all indexes for a specific table"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            indexname,
            indexdef
        FROM pg_indexes
        WHERE schemaname = 'synergy_sessions' 
        AND tablename = %s
    """, (table_name,))
    indexes = cursor.fetchall()
    cursor.close()
    return [(i['indexname'], i['indexdef']) for i in indexes]

def main():
    print("\n" + "="*80)
    print("  SYNERGY_SESSIONS DATABASE STRUCTURE ANALYSIS")
    print("="*80)
    
    conn = get_synergy_sessions_connection()
    
    try:
        # Get all tables
        tables = get_all_tables(conn)
        print(f"\n📊 Found {len(tables)} tables in synergy_sessions schema:\n")
        
        for table in tables:
            print(f"\n{'='*80}")
            print(f"TABLE: synergy_sessions.{table}")
            print('='*80)
            
            # Get columns
            columns = get_table_columns(conn, table)
            print(f"\nColumns ({len(columns)}):")
            print("-" * 80)
            
            for col in columns:
                col_name, data_type, max_length, nullable, default = col
                type_str = data_type
                if max_length:
                    type_str += f"({max_length})"
                nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                default_str = f" DEFAULT {default}" if default else ""
                
                print(f"  • {col_name:<30} {type_str:<20} {nullable_str:<10} {default_str}")
            
            # Get indexes
            indexes = get_table_indexes(conn, table)
            if indexes:
                print(f"\nIndexes ({len(indexes)}):")
                print("-" * 80)
                for idx_name, idx_def in indexes:
                    print(f"  • {idx_name}")
                    print(f"    {idx_def}")
            
            # If this is synergy_internal_docs, get sample data
            if table == 'synergy_internal_docs':
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) as count FROM synergy_sessions.synergy_internal_docs
                """)
                result = cursor.fetchone()
                count = result['count'] if result else 0
                print(f"\n📈 Total documents: {count}")
                
                if count > 0:
                    cursor.execute("""
                        SELECT doc_type, COUNT(*) as count
                        FROM synergy_sessions.synergy_internal_docs 
                        GROUP BY doc_type
                    """)
                    doc_types = cursor.fetchall()
                    print("\nDocument types:")
                    for row in doc_types:
                        print(f"  • {row['doc_type']}: {row['count']}")
                    
                    cursor.execute("""
                        SELECT 
                            CASE 
                                WHEN session_id IS NOT NULL AND session_id != '' THEN 'Linked to session'
                                ELSE 'Orphaned'
                            END as link_status,
                            COUNT(*) as count
                        FROM synergy_sessions.synergy_internal_docs
                        GROUP BY link_status
                    """)
                    link_stats = cursor.fetchall()
                    print("\nLink status:")
                    for row in link_stats:
                        print(f"  • {row['link_status']}: {row['count']}")
                
                cursor.close()
        
        print("\n" + "="*80)
        print("  DATABASE CAPABILITIES SUMMARY")
        print("="*80)
        print("\n✅ What's Possible:")
        print("  • Full-text search (PostgreSQL ts_vector)")
        print("  • JSON/JSONB storage for metadata, tags, content")
        print("  • Proper indexing for performance")
        print("  • Foreign key relationships")
        print("  • Transaction support")
        print("  • Complex queries with JOINs")
        print("  • Date/time filtering")
        print("  • Aggregations (COUNT, GROUP BY)")
        print("  • Supabase real-time subscriptions (if enabled)")
        
        print("\n📋 Documents Library Sidebar - Data Available:")
        print("  • Document metadata (title, type, version, slug)")
        print("  • Session linking (session_id foreign key)")
        print("  • User tracking (created_by, last_edited_by)")
        print("  • Timestamps (created_at, updated_at)")
        print("  • Tags (JSON array)")
        print("  • Visibility control (private/team/public)")
        print("  • Share URLs")
        print("  • Content (JSON structure)")
        print("  • Metadata (JSONB for extensibility)")
        
    finally:
        conn.close()
    
    print("\n" + "="*80)
    print("  ANALYSIS COMPLETE")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
