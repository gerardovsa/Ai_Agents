#!/usr/bin/env python3
"""
Run ML Analytics Schema Migration (008)
Creates tables for ML predictions, models, customer intelligence, and anomalies.

This should be run ONCE on production to create the required tables.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from AI_infrastructure.shared.database_utils import execute_query, get_database_connection

def run_migration():
    """Execute the ML analytics schema migration."""
    
    print("=" * 70)
    print("ML ANALYTICS SCHEMA MIGRATION (008)")
    print("=" * 70)
    print("\nThis will create:")
    print("  - ml_models (store trained ML models)")
    print("  - ml_predictions (cache predictions)")
    print("  - customer_intelligence (customer insights cache)")
    print("  - anomaly_detections (anomaly results)")
    print("  - xero_invoice_ml_cache (Xero invoice ML cache)")
    print("\n" + "=" * 70)
    
    # Read the SQL file
    sql_file = os.path.join(os.path.dirname(__file__), '008_ml_analytics_schema.sql')
    
    if not os.path.exists(sql_file):
        print(f"❌ ERROR: Migration file not found: {sql_file}")
        return False
    
    print(f"\nReading SQL from: {sql_file}")
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print(f"Executing migration as single transaction...\n")
    
    success_count = 0
    error_count = 0
    
    # Use direct connection for SQL with procedural code
    conn = get_database_connection('ai_infrastructure')
    
    try:
        cursor = conn.cursor()
        cursor.execute(sql_content)
        conn.commit()
        cursor.close()
        
        print(f"✅ Migration executed successfully")
        success_count = 1
        
    except Exception as e:
        conn.rollback()
        error_msg = str(e)
        
        # Check if error is "already exists" (which is OK for idempotent migrations)
        if 'already exists' in error_msg.lower():
            print(f"⚠️  Some objects already exist (migration is idempotent)")
            success_count = 1
        else:
            print(f"❌ ERROR: {error_msg}")
            error_count = 1
    finally:
        conn.close()
    
    print("\n" + "=" * 70)
    print("MIGRATION SUMMARY")
    print("=" * 70)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Errors: {error_count}")
    
    if error_count == 0:
        print("\n🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        return True
    else:
        print(f"\n⚠️  MIGRATION COMPLETED WITH {error_count} ERROR(S)")
        return False

def verify_migration():
    """Verify the migration created the expected tables."""
    
    print("\n" + "=" * 70)
    print("VERIFYING MIGRATION")
    print("=" * 70)
    
    tables = [
        'ml_models',
        'ml_predictions',
        'customer_intelligence',
        'anomaly_detections',
        'xero_invoice_ml_cache'
    ]
    
    all_exist = True
    
    for table in tables:
        try:
            exists = execute_query(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)",
                (table,),
                fetch_mode='value'
            )
            
            if exists:
                print(f"✅ {table} - EXISTS")
            else:
                print(f"❌ {table} - NOT FOUND")
                all_exist = False
                
        except Exception as e:
            print(f"❌ {table} - ERROR: {e}")
            all_exist = False
    
    return all_exist

if __name__ == '__main__':
    print("\n🚀 Starting ML Analytics Schema Migration...\n")
    
    success = run_migration()
    
    if success:
        verified = verify_migration()
        
        if verified:
            print("\n✅ ALL TABLES VERIFIED - Migration complete!\n")
            sys.exit(0)
        else:
            print("\n⚠️  Some tables missing - Check errors above\n")
            sys.exit(1)
    else:
        print("\n❌ Migration failed - Check errors above\n")
        sys.exit(1)
