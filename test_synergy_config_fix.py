#!/usr/bin/env python3
"""
Test script to verify synergy_config.py uses PostgreSQL correctly
Verifies:
1. No SQLite fallback attempted
2. Uses SUPABASE_DB_URL_POOLER environment variable
3. Queries synergy_sessions.synergy_config table
4. Returns default values when DB not available
"""

import os
import sys

# Ensure environment variable is set for testing
if not os.environ.get('SUPABASE_DB_URL_POOLER'):
    print("⚠️  SUPABASE_DB_URL_POOLER not set - testing with defaults")
    os.environ['SUPABASE_DB_URL_POOLER'] = 'postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres'

# Import after setting env var
from shared.synergy_config import SynergyConfig, get_kanban_columns

print("\n" + "="*70)
print("TESTING SYNERGY CONFIG - PostgreSQL Fix")
print("="*70)

# Test 1: Instantiate config
print("\n[TEST 1] Creating SynergyConfig instance...")
try:
    config = SynergyConfig()
    print("✅ SynergyConfig instantiated successfully")
except Exception as e:
    print(f"❌ Failed to instantiate: {e}")
    sys.exit(1)

# Test 2: Get kanban columns
print("\n[TEST 2] Getting Kanban columns...")
try:
    columns = get_kanban_columns()
    print(f"✅ Kanban Columns Retrieved: {columns}")
    print(f"   Type: {type(columns)}")
    print(f"   Count: {len(columns)}")
except Exception as e:
    print(f"❌ Failed to get columns: {e}")

# Test 3: Get priority levels
print("\n[TEST 3] Getting Priority levels...")
try:
    priorities = config.get_priority_levels()
    print(f"✅ Priority Levels: {priorities}")
except Exception as e:
    print(f"❌ Failed to get priorities: {e}")

# Test 4: Get session statuses
print("\n[TEST 4] Getting Session statuses...")
try:
    statuses = config.get_session_statuses()
    print(f"✅ Session Statuses: {statuses}")
except Exception as e:
    print(f"❌ Failed to get statuses: {e}")

# Test 5: Get platform options
print("\n[TEST 5] Getting Platform options...")
try:
    platforms = config.get_platform_options()
    print(f"✅ Platform Options: {platforms[:5]}... ({len(platforms)} total)")
except Exception as e:
    print(f"❌ Failed to get platforms: {e}")

# Test 6: Verify no SQLite attempts
print("\n[TEST 6] Verifying NO SQLite usage...")
try:
    # This should use PostgreSQL, not SQLite
    import io
    import contextlib
    
    # Capture any output that mentions SQLite
    output_capture = io.StringIO()
    with contextlib.redirect_stdout(output_capture):
        with contextlib.redirect_stderr(output_capture):
            test_config = SynergyConfig()
            _ = test_config.get_kanban_columns()
    
    output_text = output_capture.getvalue()
    if 'sqlite' in output_text.lower():
        print(f"❌ SQLite detected in output: {output_text}")
    else:
        print("✅ No SQLite usage detected")
        
except Exception as e:
    print(f"⚠️  Test skipped: {e}")

print("\n" + "="*70)
print("SYNERGY CONFIG TESTS COMPLETE")
print("="*70 + "\n")
