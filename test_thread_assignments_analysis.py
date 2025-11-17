"""
Test Thread Assignments Analysis
Connects to Supabase and runs comprehensive thread location checks
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.master')

def connect_to_supabase():
    """Connect to Supabase PostgreSQL"""
    db_url = os.getenv('SUPABASE_DB_URL')
    if not db_url:
        raise ValueError("SUPABASE_DB_URL not set in .env.master")
    
    print(f"Connecting to Supabase...")
    conn = psycopg2.connect(db_url)
    print(f"✅ Connected to Supabase")
    return conn


def run_query(conn, query, description):
    """Run a query and display results"""
    print(f"\n{'=' * 80}")
    print(f"{description}")
    print(f"{'=' * 80}")
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query)
        results = cursor.fetchall()
        
        if not results:
            print("No results found.")
            return
        
        # Print column headers
        if results:
            headers = results[0].keys()
            header_str = " | ".join(str(h) for h in headers)
            print(header_str)
            print("-" * len(header_str))
            
            # Print rows
            for row in results:
                row_str = " | ".join(str(v) if v is not None else "NULL" for v in row.values())
                print(row_str)
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all thread assignment checks"""
    
    print("=" * 80)
    print("THREAD ASSIGNMENTS ANALYSIS")
    print("=" * 80)
    
    conn = connect_to_supabase()
    
    # Query 1: Threads with location set
    query1 = """
        SELECT 
            id,
            thread_slug,
            name as thread_name,
            location,
            user_id,
            created_at::date as created,
            CASE 
                WHEN location IS NULL THEN 'No location (Prime)'
                WHEN location = 'prime' THEN 'Prime (explicit)'
                WHEN location LIKE 'agent-%' THEN 'Agent location'
                ELSE 'Other: ' || location
            END as location_type
        FROM sessions.threads
        WHERE user_id IN (1, 12, 13, 14)
        ORDER BY user_id, created_at DESC
        LIMIT 20;
    """
    run_query(conn, query1, "1. THREADS WITH LOCATION SET (Recent 20)")
    
    # Query 2: User metadata check
    query2 = """
        SELECT 
            id as user_id,
            username,
            email,
            CASE 
                WHEN metadata IS NULL THEN 'No metadata'
                WHEN metadata = '{}' THEN 'Empty metadata'
                WHEN metadata LIKE '%thread_assignments%' THEN 'Has thread_assignments'
                ELSE 'Has other metadata'
            END as metadata_status,
            LENGTH(metadata) as metadata_length
        FROM ai_infrastructure.users
        WHERE id IN (1, 12, 13, 14)
        ORDER BY id;
    """
    run_query(conn, query2, "2. USER METADATA (JSON STORAGE)")
    
    # Query 3: Unused thread_assignments tables
    query3 = """
        SELECT 
            'ai_infrastructure.thread_assignments' as table_name,
            COUNT(*) as row_count
        FROM ai_infrastructure.thread_assignments
        UNION ALL
        SELECT 
            'sessions.thread_assignments' as table_name,
            COUNT(*) as row_count
        FROM sessions.thread_assignments;
    """
    run_query(conn, query3, "3. UNUSED THREAD_ASSIGNMENTS TABLES (Should be 0)")
    
    # Query 4: Thread distribution by location
    query4 = """
        SELECT 
            COALESCE(location, 'NULL (Prime)') as location,
            COUNT(*) as thread_count,
            COUNT(DISTINCT user_id) as unique_users,
            MIN(created_at::date) as oldest_thread,
            MAX(created_at::date) as newest_thread
        FROM sessions.threads
        WHERE user_id IN (1, 12, 13, 14)
        GROUP BY location
        ORDER BY thread_count DESC;
    """
    run_query(conn, query4, "4. THREAD DISTRIBUTION BY LOCATION")
    
    # Query 5: Recent threads with activity
    query5 = """
        SELECT 
            t.id,
            t.thread_slug,
            t.name as thread_name,
            t.location,
            t.user_id,
            u.username,
            t.updated_at::date as last_updated,
            EXTRACT(days FROM (CURRENT_TIMESTAMP - t.updated_at))::integer as days_ago
        FROM sessions.threads t
        LEFT JOIN ai_infrastructure.users u ON t.user_id = u.id
        WHERE t.user_id IN (1, 12, 13, 14)
            AND t.updated_at > CURRENT_TIMESTAMP - INTERVAL '30 days'
        ORDER BY t.updated_at DESC
        LIMIT 20;
    """
    run_query(conn, query5, "5. RECENT THREADS (Last 30 days)")
    
    # Query 6: Summary
    query6 = """
        SELECT 
            'Total threads for your users' as metric,
            COUNT(*)::text as value
        FROM sessions.threads
        WHERE user_id IN (1, 12, 13, 14)
        UNION ALL
        SELECT 
            'Threads with location set',
            COUNT(*)::text
        FROM sessions.threads
        WHERE user_id IN (1, 12, 13, 14)
            AND location IS NOT NULL
        UNION ALL
        SELECT 
            'Threads in Prime (NULL location)',
            COUNT(*)::text
        FROM sessions.threads
        WHERE user_id IN (1, 12, 13, 14)
            AND location IS NULL;
    """
    run_query(conn, query6, "6. SUMMARY STATISTICS")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nKEY FINDINGS:")
    print("- Thread locations stored in: sessions.threads.location column")
    print("- Values: NULL (Prime), 'prime', 'agent-1', 'agent-2', etc.")
    print("- users.metadata approach: NOT currently used for locations")
    print("\nRECOMMENDATIONS:")
    print("1. If thread_assignments tables show 0 rows, drop them (unused)")
    print("2. Continue using threads.location column for assignments")
    print("3. Update THREAD_ASSIGNMENTS_EXPLAINED.md with correct info")


if __name__ == '__main__':
    main()
