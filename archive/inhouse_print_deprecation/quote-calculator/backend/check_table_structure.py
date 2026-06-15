"""Check calculator_parameter_overrides table structure"""
import sys
from pathlib import Path

# Add AI_infrastructure to path
ai_infra = Path(__file__).parent.parent.parent.parent.parent / 'AI_infrastructure'
sys.path.insert(0, str(ai_infra))

from shared.database_utils import get_database_connection

conn = get_database_connection('ai_infrastructure')
cursor = conn.cursor()

# Check calculator_parameter_overrides
cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'calculator_parameter_overrides'
    ORDER BY ordinal_position
""")

print('calculator_parameter_overrides columns:')
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f'  {row["column_name"]:35} {row["data_type"]:20} nullable={row["is_nullable"]}')
else:
    print('  Table does not exist or has no columns')

# Check calculator_pricing_parameters
cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'calculator_pricing_parameters'
    ORDER BY ordinal_position
""")

print('\ncalculator_pricing_parameters columns:')
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f'  {row["column_name"]:35} {row["data_type"]:20} nullable={row["is_nullable"]}')
else:
    print('  Table does not exist or has no columns')

# Check allowed categories
cursor.execute("""
    SELECT DISTINCT category 
    FROM calculator_pricing_parameters 
    ORDER BY category
""")

print('\nAllowed categories:')
rows = cursor.fetchall()
for row in rows:
    print(f'  - {row["category"]}')

# Check allowed value_units
cursor.execute("""
    SELECT DISTINCT value_unit 
    FROM calculator_pricing_parameters 
    WHERE value_unit IS NOT NULL
    ORDER BY value_unit
""")

print('\nAllowed value_units:')
rows = cursor.fetchall()
for row in rows:
    print(f'  - {row["value_unit"]}')

cursor.close()
conn.close()
