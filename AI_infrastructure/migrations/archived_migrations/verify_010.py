"""Verify migration 010 - No prime-loaded threads remain"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.database_utils import execute_query

print("🔍 Verifying migration 010...\n")

# Check for prime-loaded threads
count = execute_query(
    "SELECT COUNT(*) FROM sessions.threads WHERE location = 'prime-loaded'",
    fetch_mode='value'
)

print(f"Threads with location='prime-loaded': {count}")

if count == 0:
    print("✅ SUCCESS: No prime-loaded threads found\n")
else:
    print(f"❌ FAILURE: Found {count} prime-loaded threads\n")
    sys.exit(1)

# Show distribution
print("📊 Current thread location distribution:")
rows = execute_query(
    "SELECT location, COUNT(*) as count FROM sessions.threads GROUP BY location ORDER BY count DESC",
    fetch_mode='all'
)

for row in rows:
    print(f"  {row['location']}: {row['count']}")

print("\n✅ Database verification complete")
