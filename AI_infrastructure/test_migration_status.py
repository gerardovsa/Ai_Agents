"""Quick database validation for prime -> unassigned migration"""
from shared.database_utils import execute_query

print("\n📊 Database Migration Validation\n")

# Check thread location distribution
rows = execute_query(
    "SELECT location, COUNT(*) as count FROM sessions.threads GROUP BY location ORDER BY count DESC",
    fetch_mode='all'
)

print("Current thread locations:")
for r in rows:
    print(f"  {r['location']}: {r['count']}")

# Check for any remaining 'prime' locations
prime_count = execute_query(
    "SELECT COUNT(*) FROM sessions.threads WHERE location = 'prime'",
    fetch_mode='value'
)

print(f"\n❌ Threads with 'prime' location: {prime_count}")

# Check unassigned count
unassigned_count = execute_query(
    "SELECT COUNT(*) FROM sessions.threads WHERE location = 'unassigned'",
    fetch_mode='value'
)

print(f"✅ Threads with 'unassigned' location: {unassigned_count}")

# Verify constraint exists
constraint_check = execute_query(
    """
    SELECT conname, pg_get_constraintdef(oid) 
    FROM pg_constraint 
    WHERE conname = 'chk_location_valid'
    """,
    fetch_mode='one'
)

if constraint_check:
    print(f"\n✅ Constraint found: {constraint_check['conname']}")
    print(f"   Definition: {constraint_check['pg_get_constraintdef'][:100]}...")
else:
    print("\n❌ Constraint NOT found!")

print("\n✅ Database validation complete!\n")
