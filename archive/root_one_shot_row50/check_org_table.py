#!/usr/bin/env python3
"""Check organisations table schema and data in production"""

from AI_infrastructure.shared.database_utils import execute_query

print("=" * 100)
print("ORGANISATIONS TABLE SCHEMA")
print("=" * 100)

# Get table schema
columns = execute_query(
    """
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns 
    WHERE table_schema='ai_infrastructure' AND table_name='organisations'
    ORDER BY ordinal_position
    """,
    (),
    fetch_mode='all'
)

print(f"\nTotal columns: {len(columns)}\n")
for col in columns:
    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
    default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
    print(f"  {col['column_name']:25} {col['data_type']:20} {nullable:10}{default}")

print("\n" + "=" * 100)
print("ORGANISATIONS TABLE DATA")
print("=" * 100)

# Get all rows
rows = execute_query(
    "SELECT * FROM ai_infrastructure.organisations ORDER BY id",
    (),
    fetch_mode='all'
)

print(f"\nTotal rows: {len(rows)}\n")
if rows:
    for row in rows:
        print(f"Row ID={row['id']}:")
        for key, value in row.items():
            if isinstance(value, str) and len(str(value)) > 60:
                print(f"  {key}: {str(value)[:60]}...")
            else:
                print(f"  {key}: {value}")
        print()
else:
    print("❌ NO ROWS FOUND IN organisations TABLE")

print("\n" + "=" * 100)
print("VERIFY THE EXACT QUERY FROM get_org_info()")
print("=" * 100)

# Run the exact query from get_org_info
result = execute_query(
    """
    SELECT id, name, slug, plan_tier, display_name, logo_url,
           timezone, country_code, is_active, created_at,
           description, visibility, allowed_domains,
           ai_provider, ai_model, ai_max_tokens
    FROM ai_infrastructure.organisations 
    WHERE id = 1
    """,
    (),
    fetch_mode='one'
)

print(f"\nQuery result for id=1: {result}")
if result:
    print(f"✅ Row exists and query works")
else:
    print(f"❌ Query returned None")
