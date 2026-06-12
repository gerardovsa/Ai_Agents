"""
Complete Schema Audit - Find Next 15+ Issues
January 18, 2026

Systematically check every table and column against documentation
"""

import sys
sys.path.insert(0, 'UI/modules_external/inhouse-print')
from db_connector import InHousePrintDB
import json

db = InHousePrintDB()

print("="*80)
print("COMPLETE SCHEMA AUDIT - Finding All Documentation Errors")
print("="*80)

# Get all table schemas
tables_to_audit = [
    'Orders',
    'JobTickets', 
    'PaperSize',
    'BindType',
    'Clients',
    'JobType',
    'GSM',
    'PaperType',
    'JobStage'
]

all_schemas = {}

for table in tables_to_audit:
    print(f"\n{'='*80}")
    print(f"AUDITING: {table}")
    print(f"{'='*80}")
    
    try:
        query = f"""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE,
                COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = '{table}'
            ORDER BY ORDINAL_POSITION
        """
        
        result = db.execute_query(query)
        
        if result is not None and len(result) > 0:
            all_schemas[table] = result['COLUMN_NAME'].tolist()
            print(f"✅ Found {len(result)} columns")
            
            # Show all columns
            for idx, row in result.iterrows():
                nullable = "NULL" if row['IS_NULLABLE'] == 'YES' else "NOT NULL"
                max_len = f"({row['CHARACTER_MAXIMUM_LENGTH']})" if row['CHARACTER_MAXIMUM_LENGTH'] else ""
                print(f"  {idx+1:2d}. {row['COLUMN_NAME']:30s} {row['DATA_TYPE']}{max_len:15s} {nullable}")
        else:
            print(f"❌ Table not found or empty")
            all_schemas[table] = []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        all_schemas[table] = []

# Now compare against documented assumptions
print("\n" + "="*80)
print("COMPARING ACTUAL SCHEMA vs DOCUMENTED ASSUMPTIONS")
print("="*80)

issues = []

# Known documented columns that might be wrong
documented_columns = {
    'Orders': [
        ('OrderID', True),
        ('OrderNumber', False),  # We fixed this -> ClientOrderNum
        ('CustomerMYOB_ID', True),
        ('ClientName', True),
        ('ClientOrderNum', True),  # Fixed
        ('OrderDate', True),
        ('Status', False),  # Already documented as not existing
        ('TotalCost', False),  # Already documented as not existing
        ('ColourStatus', False),  # We fixed this - it's in JobTickets
        ('ReadToInvoice', True),
        ('Invoiced', True),
        ('CustomerPickup', True),
        ('Urgent', True),
        ('DateRequired', True),
        ('OrderNotes', True)
    ],
    'JobTickets': [
        ('TicketID', True),  # Fixed (was JobID)
        ('JobID', False),  # We fixed this
        ('OrderID', True),
        ('DateCreated', False),  # Already documented
        ('TicketNotes', True),
        ('QTY', True),
        ('Cost', True),
        ('ColourStatus', True),
        ('PaperSizeID', True),
        ('PaperTypeID', True),
        ('JobTypeID', True),
        ('BindTypeID', True),
        ('GSM_ID', True),  # Fixed (was GSMID)
        ('GSMID', False),  # We fixed this
        ('PrintType', False),  # Documented as not existing
        ('StageID', True),
        ('CelloYes', True),  # Celloglaze fields
        ('FoldYes', True),
        ('StitchYes', True)
    ],
    'PaperSize': [
        ('SizeID', True),
        ('[Desc]', True),  # Reserved word - needs brackets
        ('Desc', True),  # Check if brackets required
        ('Width', False),  # Documented as not existing
        ('Height', False),  # Documented as not existing
    ],
    'BindType': [
        ('BindID', True),
        ('BindTypeDesc', True),
        ('[Desc]', False),  # Documented as not existing
    ],
    'GSM': [
        ('GSM_ID', True),  # Fixed
        ('GSMID', False),  # We fixed this
        ('[Desc]', True),
        ('DESC', True),  # Check actual column name
    ],
    'Clients': [
        ('ContactID', True),
        ('Name', True),
        ('defaultEmail', True),
        ('Phone', True),
        ('AddressLine1', True)
    ]
}

print("\nChecking documented columns against actual schema:\n")

for table, columns in documented_columns.items():
    if table not in all_schemas:
        print(f"\n⚠️  {table}: Table not found in database")
        continue
    
    actual = all_schemas[table]
    print(f"\n{table} ({len(actual)} actual columns):")
    
    for col_name, should_exist in columns:
        # Clean column name for comparison
        clean_name = col_name.replace('[', '').replace(']', '')
        
        if should_exist:
            if clean_name in actual:
                print(f"  ✅ {col_name:30s} - EXISTS (correctly documented)")
            else:
                print(f"  ❌ {col_name:30s} - NOT FOUND (documented as existing)")
                issues.append({
                    'table': table,
                    'column': col_name,
                    'issue': 'documented_but_missing',
                    'severity': 'HIGH'
                })
        else:
            if clean_name in actual:
                print(f"  ⚠️  {col_name:30s} - EXISTS (documented as NOT existing)")
                issues.append({
                    'table': table,
                    'column': col_name,
                    'issue': 'exists_but_documented_as_missing',
                    'severity': 'MEDIUM'
                })
            else:
                print(f"  ✅ {col_name:30s} - NOT FOUND (correctly documented)")

# Look for undocumented columns
print("\n" + "="*80)
print("UNDOCUMENTED COLUMNS (exist but not mentioned in guide)")
print("="*80)

for table, actual_cols in all_schemas.items():
    if table in documented_columns:
        documented = [c[0].replace('[', '').replace(']', '') for c in documented_columns[table]]
        undocumented = [c for c in actual_cols if c not in documented]
        
        if undocumented:
            print(f"\n{table}: {len(undocumented)} undocumented columns")
            for col in undocumented:
                print(f"  • {col}")
                issues.append({
                    'table': table,
                    'column': col,
                    'issue': 'undocumented',
                    'severity': 'LOW'
                })

# Summary
print("\n" + "="*80)
print(f"AUDIT SUMMARY - Found {len(issues)} Issues")
print("="*80)

high = [i for i in issues if i['severity'] == 'HIGH']
medium = [i for i in issues if i['severity'] == 'MEDIUM']
low = [i for i in issues if i['severity'] == 'LOW']

print(f"\n🚨 HIGH Priority (documented but missing): {len(high)}")
for i in high:
    print(f"   {i['table']}.{i['column']}")

print(f"\n⚠️  MEDIUM Priority (exists but documented as missing): {len(medium)}")
for i in medium:
    print(f"   {i['table']}.{i['column']}")

print(f"\n📝 LOW Priority (undocumented): {len(low)}")
print(f"   {low[:5]}..." if len(low) > 5 else f"   {low}")

# Export to JSON for processing
with open('schema_audit_results_jan18.json', 'w') as f:
    json.dump({
        'actual_schemas': {k: v for k, v in all_schemas.items()},
        'issues': issues,
        'summary': {
            'high': len(high),
            'medium': len(medium),
            'low': len(low),
            'total': len(issues)
        }
    }, f, indent=2)

print(f"\n💾 Full audit saved to: schema_audit_results_jan18.json")
print("="*80)
