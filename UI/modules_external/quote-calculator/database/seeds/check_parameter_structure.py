#!/usr/bin/env python3
"""
Check what parameters actually exist and understand their structure
"""

import psycopg2
import json

DB_URL = 'postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres'

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

print('=' * 120)
print('CHECKING ACTUAL PARAMETER STRUCTURE')
print('=' * 120)
print()

# Look at a few different parameters to understand the structure
test_params = ['quantity', 'print_sides', 'finish_size', 'paper_stock', 'celloglaze', 'impos_setup']

for param_name in test_params:
    cur.execute('''
        SELECT 
            parameter_name,
            category,
            base_value,
            value_unit,
            used_by_calculators
        FROM calculator_pricing_parameters
        WHERE parameter_name = %s;
    ''', (param_name,))
    
    result = cur.fetchone()
    if result:
        name, category, base_value, unit, calculators = result
        print(f'Parameter: {name}')
        print(f'Category: {category}')
        print(f'Base Value: {base_value}')
        print(f'Unit: {unit}')
        print(f'Number of calculators using it: {len(calculators) if calculators else 0}')
        
        if calculators and len(calculators) > 0:
            print(f'First calculator example:')
            first_calc = calculators[0]
            print(f'  Calculator: {first_calc.get("calculator")}')
            print(f'  Value: {first_calc.get("value")}')
            print(f'  Type of value: {type(first_calc.get("value"))}')
            
            # Check if it's a list/array of options
            value = first_calc.get("value")
            if isinstance(value, (list, dict)):
                print(f'  VALUE IS COMPLEX: {json.dumps(value, indent=4)}')
        
        print()
        print('-' * 120)
        print()
    else:
        print(f'Parameter "{param_name}" NOT FOUND in database')
        print('-' * 120)
        print()

# Check what type of data we actually have
print()
print('=' * 120)
print('ALL PARAMETERS IN DATABASE')
print('=' * 120)
cur.execute('''
    SELECT parameter_name, category, value_unit 
    FROM calculator_pricing_parameters 
    ORDER BY parameter_name;
''')

print(f'{"Parameter Name":<40} {"Category":<15} {"Unit":<20}')
print('-' * 120)
for row in cur.fetchall():
    print(f'{row[0]:<40} {row[1]:<15} {row[2] or "None":<20}')

print()
print('=' * 120)
print('CONCLUSION: What kind of data do we have?')
print('=' * 120)

cur.close()
conn.close()
