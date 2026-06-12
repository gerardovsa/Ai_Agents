#!/usr/bin/env python3
"""Check what's missing or out of sync between local and production."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from AI_infrastructure.shared.database_utils import execute_query

def check_ml_tables():
    """Check if ML analytics tables exist."""
    print("=" * 70)
    print("CHECKING ML ANALYTICS SCHEMA DEPLOYMENT")
    print("=" * 70)
    
    ml_tables = [
        'ml_models',
        'ml_predictions', 
        'customer_intelligence',
        'anomaly_detections',
        'xero_invoice_ml_cache'
    ]
    
    found_tables = []
    missing_tables = []
    
    for table in ml_tables:
        try:
            result = execute_query(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)",
                (table,),
                fetch_mode='value'
            )
            if result:
                found_tables.append(table)
                print(f"✅ {table}")
            else:
                missing_tables.append(table)
                print(f"❌ {table} - NOT FOUND")
        except Exception as e:
            missing_tables.append(table)
            print(f"❌ {table} - ERROR: {e}")
    
    return found_tables, missing_tables

def check_user_platform_credentials():
    """Check if user platform credentials table has InHouse data."""
    print("\n" + "=" * 70)
    print("CHECKING USER PLATFORM CREDENTIALS")
    print("=" * 70)
    
    try:
        creds = execute_query(
            "SELECT platform, is_active FROM ai_infrastructure.user_platform_credentials WHERE user_id=1",
            fetch_mode='all'
        )
        if creds:
            print(f"✅ Found {len(creds)} credential(s) for user_id=1:")
            for c in creds:
                status = "ACTIVE" if c['is_active'] else "INACTIVE"
                print(f"   - {c['platform']} ({status})")
        else:
            print("❌ No credentials found for user_id=1")
        return creds
    except Exception as e:
        print(f"❌ Error checking credentials: {e}")
        return None

def check_recent_migrations():
    """Check if recent migration marker exists."""
    print("\n" + "=" * 70)
    print("CHECKING MIGRATION TRACKING")
    print("=" * 70)
    
    try:
        # Check if migration tracking table exists
        has_tracking = execute_query(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'schema_migrations')",
            fetch_mode='value'
        )
        
        if has_tracking:
            print("✅ Migration tracking table exists")
            migrations = execute_query(
                "SELECT version, applied_at FROM schema_migrations ORDER BY applied_at DESC LIMIT 5",
                fetch_mode='all'
            )
            if migrations:
                print(f"   Last 5 migrations applied:")
                for m in migrations:
                    print(f"   - {m['version']} at {m['applied_at']}")
            else:
                print("   (No migrations recorded)")
        else:
            print("⚠️  No migration tracking table found")
    except Exception as e:
        print(f"⚠️  Migration tracking not configured: {e}")

def check_connection_pool_stats():
    """Check if connection monitoring endpoint exists."""
    print("\n" + "=" * 70)
    print("CHECKING CONNECTION POOL MONITORING")
    print("=" * 70)
    
    # This will be checked when Flask server is running
    print("⚠️  Connection stats endpoint must be tested with Flask running")
    print("   Test URL: http://localhost:5001/api/admin/connection-stats")

def main():
    print("\n🔍 PRODUCTION SYNC CHECK\n")
    
    # Check ML tables
    found_ml, missing_ml = check_ml_tables()
    
    # Check credentials
    creds = check_user_platform_credentials()
    
    # Check migrations
    check_recent_migrations()
    
    # Check connection monitoring
    check_connection_pool_stats()
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    issues = []
    
    if missing_ml:
        issues.append(f"❌ Missing ML tables: {', '.join(missing_ml)}")
        print(f"❌ Missing ML tables: {', '.join(missing_ml)}")
        print(f"   Fix: Run migration 008_ml_analytics_schema.sql")
    else:
        print(f"✅ All ML tables exist ({len(found_ml)} tables)")
    
    if not creds or not any(c['platform'] == 'inhouse_print' for c in creds):
        issues.append("❌ InHouse Print credentials missing")
        print("❌ InHouse Print credentials missing for user_id=1")
        print("   Fix: Run ADD_MISSING_CREDENTIALS_TO_SUPABASE.sql")
    else:
        print("✅ InHouse Print credentials exist")
    
    print("\n" + "=" * 70)
    if issues:
        print("🚨 PRODUCTION OUT OF SYNC - ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
        return 1
    else:
        print("✅ LOCAL AND PRODUCTION IN SYNC")
        return 0

if __name__ == '__main__':
    sys.exit(main())
