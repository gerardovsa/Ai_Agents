"""
Check and fix user_platform_credentials table schema in Supabase

This script:
1. Checks if the table exists
2. Verifies the table schema
3. Creates/fixes the table if needed
4. Adds Pinecone and Voyager credentials
"""

import sys
from pathlib import Path

# Add AI_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

from shared.database_utils import get_database_connection
import json

def check_and_fix_table():
    """Check table schema and fix if needed"""
    
    print("=" * 60)
    print("Checking user_platform_credentials Table Schema")
    print("=" * 60)
    
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    # Check if table exists in Supabase
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'ai_infrastructure' 
        AND table_name = 'user_platform_credentials'
    """)
    
    table_exists = cursor.fetchone()
    
    if not table_exists:
        print("\n❌ Table 'user_platform_credentials' does not exist in ai_infrastructure schema")
        print("   Creating table...")
        
        # Create table with proper PostgreSQL syntax
        cursor.execute("""
            CREATE TABLE ai_infrastructure.user_platform_credentials (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                credential_type TEXT NOT NULL,
                credential_key TEXT NOT NULL,
                credential_value TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSONB,
                UNIQUE(user_id, platform, credential_key)
            )
        """)
        conn.commit()
        print("   ✅ Table created successfully")
    else:
        print("\n✅ Table exists")
        
        # Check column structure
        cursor.execute("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_schema = 'ai_infrastructure'
            AND table_name = 'user_platform_credentials'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print(f"\n   Columns ({len(columns)}):")
        for col in columns:
            col_name = col[0] if isinstance(col, (list, tuple)) else col
            col_type = col[1] if isinstance(col, (list, tuple)) and len(col) > 1 else 'unknown'
            col_default = col[2] if isinstance(col, (list, tuple)) and len(col) > 2 else None
            print(f"   - {col_name}: {col_type} (default: {col_default})")
    
    conn.close()

def add_credentials_direct():
    """Add credentials directly using simple SQL"""
    
    print("\n" + "=" * 60)
    print("Adding Credentials Directly to Database")
    print("=" * 60)
    
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    user_id = 1  # Master account
    
    credentials = [
        {
            'platform': 'pinecone',
            'type': 'api_key',
            'key': 'PINECONE_API_KEY',
            'value': 'pcsk_4NZhAZ_8JpgceKPsfMsgRQGouKyfMWNZJ5SybzB72PCVVjVuK1HCkyc7uUd8RFAtDykyhr',
            'metadata': {
                'index_name': 'inhouseprint',
                'environment': 'us-east-1',
                'namespace': '',
                'description': 'InHousePrint vector database'
            }
        },
        {
            'platform': 'voyager',
            'type': 'api_key',
            'key': 'VOYAGER_API_KEY',
            'value': 'pa-GOCp1HsNfuuvjXnHPumV5f6sD-YLQwQg5Fl3Fx2AlDm',
            'metadata': {
                'provider': 'InHousePrint',
                'model': 'voyager',
                'dimensions': 1536,
                'description': 'Voyager embedding model'
            }
        },
        {
            'platform': 'openai_embeddings',
            'type': 'api_key',
            'key': 'OPENAI_API_KEY',
            'value': os.getenv('OPENAI_API_KEY', ''),  # Get from environment variable
            'metadata': {
                'model': 'text-embedding-ada-002',
                'dimensions': 1536,
                'description': 'OpenAI embeddings (backup)'
            }
        },
    ]
    
    for cred in credentials:
        print(f"\n📝 Adding {cred['platform']} credentials...")
        
        # Check if exists
        cursor.execute("""
            SELECT id FROM ai_infrastructure.user_platform_credentials
            WHERE user_id = %s AND platform = %s AND credential_key = %s
        """, (user_id, cred['platform'], cred['key']))
        
        existing = cursor.fetchone()
        
        metadata_json = json.dumps(cred['metadata'])
        
        if existing:
            # Update
            cursor.execute("""
                UPDATE ai_infrastructure.user_platform_credentials
                SET credential_value = %s,
                    credential_type = %s,
                    metadata = %s::jsonb,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (cred['value'], cred['type'], metadata_json, existing[0]))
            print(f"   ✅ Updated (ID: {existing[0]})")
        else:
            # Insert - get max ID and increment
            cursor.execute("""
                SELECT COALESCE(MAX(id), 0) + 1 as next_id 
                FROM ai_infrastructure.user_platform_credentials
            """)
            result = cursor.fetchone()
            next_id = result['next_id'] if isinstance(result, dict) else result[0] if isinstance(result, (list, tuple)) else 1
            
            cursor.execute("""
                INSERT INTO ai_infrastructure.user_platform_credentials
                (id, user_id, platform, credential_type, credential_key, credential_value, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
                RETURNING id
            """, (next_id, user_id, cred['platform'], cred['type'], cred['key'], cred['value'], metadata_json))
            
            result = cursor.fetchone()
            new_id = result['id'] if isinstance(result, dict) else result[0] if isinstance(result, (list, tuple)) else next_id
            print(f"   ✅ Inserted (ID: {new_id})")
    
    conn.commit()
    conn.close()
    
    print("\n✅ All credentials added successfully")

def verify_credentials():
    """Verify credentials were saved"""
    
    print("\n" + "=" * 60)
    print("Verifying Saved Credentials")
    print("=" * 60)
    
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, platform, credential_key, 
               LEFT(credential_value, 10) || '...' || RIGHT(credential_value, 8) as masked_value,
               metadata->>'index_name' as index_name,
               metadata->>'model' as model,
               created_at
        FROM ai_infrastructure.user_platform_credentials
        WHERE user_id = 1
        ORDER BY platform
    """)
    
    credentials = cursor.fetchall()
    
    print(f"\n✅ Found {len(credentials)} credentials:\n")
    
    for cred in credentials:
        print(f"Platform: {cred[1]}")
        print(f"  Key: {cred[2]}")
        print(f"  Value: {cred[3]}")
        if cred[4]:
            print(f"  Index: {cred[4]}")
        if cred[5]:
            print(f"  Model: {cred[5]}")
        print(f"  Created: {cred[6]}")
        print()
    
    conn.close()

if __name__ == '__main__':
    try:
        # Step 1: Check/fix table
        check_and_fix_table()
        
        # Step 2: Add credentials
        add_credentials_direct()
        
        # Step 3: Verify
        verify_credentials()
        
        print("=" * 60)
        print("✅ DONE - Credentials successfully added to database")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
