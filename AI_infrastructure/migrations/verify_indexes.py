"""Verify performance indexes were created successfully"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.database_utils import get_database_connection


def verify_indexes():
    """Check that all indexes were created"""
    
    print("=" * 70)
    print("VERIFYING PERFORMANCE INDEXES")
    print("=" * 70)
    
    # Check sessions schema
    print("\n[1] Checking sessions schema indexes...")
    conn = get_database_connection('sessions')
    cur = conn.cursor()
    
    cur.execute("""
        SELECT indexname, tablename, indexdef 
        FROM pg_indexes 
        WHERE schemaname = 'sessions' 
        AND indexname LIKE 'idx_%'
        ORDER BY tablename, indexname
    """)
    
    results = cur.fetchall()
    if results:
        for idx_name, table, definition in results:
            print(f"  ✅ {idx_name} on {table}")
    else:
        print("  ⚠️  No indexes found in sessions schema")
    
    # Check ai_infrastructure schema
    print("\n[2] Checking ai_infrastructure schema indexes...")
    conn_ai = get_database_connection('ai_infrastructure')
    cur_ai = conn_ai.cursor()
    
    cur_ai.execute("""
        SELECT indexname, tablename, indexdef 
        FROM pg_indexes 
        WHERE schemaname = 'ai_infrastructure' 
        AND indexname LIKE 'idx_%'
        ORDER BY tablename, indexname
    """)
    
    results_ai = cur_ai.fetchall()
    if results_ai:
        for idx_name, table, definition in results_ai:
            print(f"  ✅ {idx_name} on {table}")
    else:
        print("  ⚠️  No indexes found in ai_infrastructure schema")
    
    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)
    
    conn.close()
    conn_ai.close()


if __name__ == "__main__":
    verify_indexes()
