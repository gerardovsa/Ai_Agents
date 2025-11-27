"""Test script to check connections table and query it"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import get_database_connection

def check_tables():
    """Check what credential/oauth tables exist"""
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    # Check for tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'ai_infrastructure' 
        AND (table_name LIKE '%credential%' OR table_name LIKE '%oauth%' OR table_name LIKE '%connection%')
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    print(f"\nFound {len(tables)} relevant tables:")
    for table in tables:
        table_name = table['table_name'] if isinstance(table, dict) else table[0]
        print(f"  - {table_name}")
    
    cursor.close()
    conn.close()
    
    return [t['table_name'] if isinstance(t, dict) else t[0] for t in tables]

def test_connections_query(user_id=14):
    """Test the connections query"""
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    print(f"\n\nTesting connections query for user_id={user_id}...")
    
    try:
        cursor.execute("""
            SELECT 
                id,
                platform,
                credential_type,
                is_active,
                created_at,
                updated_at,
                metadata
            FROM ai_infrastructure.user_platform_credentials
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
        
        rows = cursor.fetchall()
        print(f"✅ Query successful! Found {len(rows)} connections")
        
        for row in rows:
            print(f"\n  Platform: {row[1]}")
            print(f"  Type: {row[2]}")
            print(f"  Active: {row[3]}")
            print(f"  Created: {row[4]}")
        
    except Exception as e:
        print(f"❌ Query failed: {e}")
        
        # Check if table exists
        print("\nChecking if user_platform_credentials table exists...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'ai_infrastructure' 
            AND table_name = 'user_platform_credentials'
        """)
        
        table_check = cursor.fetchone()
        if table_check:
            print("✅ Table exists")
            
            # Check columns
            print("\nChecking table columns...")
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'ai_infrastructure' 
                AND table_name = 'user_platform_credentials'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            print(f"Found {len(columns)} columns:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")
        else:
            print("❌ Table does NOT exist!")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    tables = check_tables()
    test_connections_query()
