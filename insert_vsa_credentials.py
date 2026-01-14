"""
Insert VSA Supabase Credentials
================================

Inserts VSA veterinary alerts Supabase credentials into
ai_infrastructure.user_platform_credentials table.

Run this once to set up the VSA database connection.
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AI_infrastructure.shared.database_utils import get_database_connection


def insert_vsa_credentials():
    """Insert VSA Supabase credentials into database."""
    
    # VSA Supabase credentials
    credentials = {
        "url": "https://wuwmvtslltqhaycyukxk.supabase.co",
        "region": "ap-southeast-2",
        "db_host": "db.wuwmvtslltqhaycyukxk.supabase.co",
        "db_name": "postgres",
        "db_port": "5432",
        "db_user": "postgres",
        "anon_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1d212dHNsbHRxaGF5Y3l1a3hrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzE2MzM3NjMsImV4cCI6MjA0NzIwOTc2M30.pBhNdUFQ8zSbZo8wAd8LJWb7qN6wLRJgW-kEgRf3saY",
        "project_id": "wuwmvtslltqhaycyukxk",
        "db_password": "phonetranscriptions11!",
        "service_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1d212dHNsbHRxaGF5Y3l1a3hrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTIyNDMzNCwiZXhwIjoyMDY2ODAwMzM0fQ.tUJ473GHC139vvH0X6fIgaFtgmLTl-VaUCf9kY6xQj4"
    }
    
    metadata = {
        "tables": ["veterinary_calls", "manager_alerts_tags", "follow_up_actions", "call_full_transcript_and_full_analysis"],
        "purpose": "VSA Veterinary Alerts Module",
        "database": "veterinary_calls",
        "created_by": "insert_vsa_credentials.py"
    }
    
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Check if credentials already exist
        cursor.execute("""
            SELECT id FROM ai_infrastructure.user_platform_credentials
            WHERE platform = %s AND credentials::text LIKE %s
        """, ('supabase', '%wuwmvtslltqhaycyukxk%'))
        
        result = cursor.fetchall()
        
        if result and len(result) > 0:
            # RealDictCursor returns dictionaries
            print(f"✅ VSA credentials already exist (ID: {result[0]['id']})")
            cursor.close()
            conn.close()
            return
        
        # Insert new credentials
        cursor.execute("""
            INSERT INTO ai_infrastructure.user_platform_credentials
            (user_id, platform, credential_type, credential_key, credential_value, is_active, metadata, credentials)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            1,  # user_id
            'supabase',  # platform
            'api_keys',  # credential_type
            'supabase_api',  # credential_key
            credentials['service_key'],  # credential_value (service key)
            True,  # is_active
            json.dumps(metadata),  # metadata
            json.dumps(credentials)  # credentials
        ))
        
        new_result = cursor.fetchall()
        if new_result and len(new_result) > 0:
            new_id = new_result[0]['id']
        else:
            new_id = 'unknown'
        conn.commit()
        
        print(f"✅ VSA Supabase credentials inserted successfully (ID: {new_id})")
        print(f"   URL: {credentials['url']}")
        print(f"   Tables: {', '.join(metadata['tables'])}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error inserting credentials: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    insert_vsa_credentials()
