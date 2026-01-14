"""Check users table schema in Supabase"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'AI_infrastructure'))

from shared.db_connection_wrapper import get_connection

conn = get_connection('ai_infrastructure')
cursor = conn.cursor()

# Get column information
cursor.execute("""
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns 
    WHERE table_name = 'users'
    ORDER BY ordinal_position
""")

columns = cursor.fetchall()

print("\n" + "="*70)
print("USERS TABLE SCHEMA (Supabase)")
print("="*70)

for col in columns:
    col_name = col[0] if isinstance(col, tuple) else col['column_name']
    data_type = col[1] if isinstance(col, tuple) else col['data_type']
    is_nullable = col[2] if isinstance(col, tuple) else col['is_nullable']
    default = col[3] if isinstance(col, tuple) else col['column_default']
    
    nullable_str = "NULL" if is_nullable == 'YES' else "NOT NULL"
    default_str = f" DEFAULT {default}" if default else ""
    
    print(f"  {col_name:30} {data_type:20} {nullable_str:10} {default_str}")

print("="*70)

# Check if permissions column exists
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'users' AND column_name = 'permissions'
""")
has_permissions = cursor.fetchone() is not None

print(f"\n✅ permissions column exists: {has_permissions}")

if not has_permissions:
    print("\n⚠️  WARNING: 'permissions' column is MISSING from users table!")
    print("   This will cause Excel and OneDrive tools to fail.")
    print("\n   To fix, run:")
    print("   ALTER TABLE users ADD COLUMN permissions JSONB DEFAULT '{}'::jsonb;")

conn.close()
