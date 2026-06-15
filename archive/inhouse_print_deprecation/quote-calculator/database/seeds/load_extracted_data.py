"""
Load Extracted Calculator Data into PostgreSQL
Version: 1.0.0
Created: December 17, 2025

Purpose: Populate calculator_pricing_catalog tables from CALCULATOR_PRICING_CATALOG_EXTRACTED.json

Usage:
    python load_extracted_data.py
    python load_extracted_data.py --dry-run  # Test without committing
"""

import json
import psycopg2
from psycopg2.extras import Json
from decimal import Decimal
from datetime import datetime
import sys
import os

# Database connection - Supabase PostgreSQL
DB_URL = 'postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres'

def load_json_data():
    """Load extracted calculator data from JSON file"""
    # Fixed path to AI_agents root
    json_path = r'C:\Users\gpoli\GIT\AI_agents\CALCULATOR_PRICING_CATALOG_EXTRACTED.json'
    
    print(f"📄 Loading data from: {json_path}")
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    print(f"✅ Loaded data for {len(data)} calculators")
    return data

def extract_all_parameters(calculators_data):
    """Extract all unique parameters from all calculators"""
    parameters_map = {}  # parameter_name -> {category, base_value, used_by[]}
    
    for calc in calculators_data:
        calc_name = calc['name']
        calc_file = calc['file']
        
        # Process pricing constants
        for param_name, param_value in calc.get('pricing_constants', {}).items():
            if param_name not in parameters_map:
                parameters_map[param_name] = {
                    'parameter_name': param_name,
                    'category': categorize_parameter(param_name),
                    'base_value': None,
                    'value_unit': determine_unit(param_name),
                    'used_by': []
                }
            
            # Add calculator usage
            parameters_map[param_name]['used_by'].append({
                'calculator': calc_name,
                'value': float(param_value) if param_value else None,
                'override': False,
                'file': calc_file,
                'added_date': datetime.now().isoformat()
            })
            
            # Update base_value (use most common value)
            if parameters_map[param_name]['base_value'] is None:
                parameters_map[param_name]['base_value'] = float(param_value) if param_value else None
        
        # Process pricing dictionaries (e.g., material_map)
        for dict_name, dict_values in calc.get('pricing_dicts', {}).items():
            for key, value in dict_values.items():
                param_name = f"{dict_name}_{key}"
                
                if param_name not in parameters_map:
                    parameters_map[param_name] = {
                        'parameter_name': param_name,
                        'category': 'Material',
                        'base_value': float(value) if value else None,
                        'value_unit': 'currency',
                        'used_by': []
                    }
                
                parameters_map[param_name]['used_by'].append({
                    'calculator': calc_name,
                    'value': float(value) if value else None,
                    'override': False,
                    'file': calc_file,
                    'added_date': datetime.now().isoformat()
                })
    
    print(f"📊 Extracted {len(parameters_map)} unique parameters")
    return list(parameters_map.values())

def categorize_parameter(param_name):
    """Categorize parameter based on name"""
    param_lower = param_name.lower()
    
    if any(x in param_lower for x in ['setup', 'impos', 'guilo', 'artwork']):
        return 'Setup'
    elif any(x in param_lower for x in ['material', 'stock', 'paper', 'vinyl', 'metal']):
        return 'Material'
    elif any(x in param_lower for x in ['print', 'ink', 'toner']):
        return 'Print'
    elif any(x in param_lower for x in ['profit', 'margin']):
        return 'Profit'
    elif any(x in param_lower for x in ['gst', 'tax']):
        return 'Tax'
    elif any(x in param_lower for x in ['bind', 'wire', 'spiral', 'perfect']):
        return 'Binding'
    elif any(x in param_lower for x in ['finish', 'lamin', 'cello', 'gloss', 'matt']):
        return 'Finishing'
    elif any(x in param_lower for x in ['ship', 'freight', 'delivery']):
        return 'Shipping'
    else:
        return 'Other'

def determine_unit(param_name):
    """Determine value unit based on parameter name"""
    param_lower = param_name.lower()
    
    if 'rate' in param_lower or 'gst' in param_lower or 'margin' in param_lower:
        return 'multiplier'
    elif 'sqm' in param_lower or 'm2' in param_lower:
        return 'per_sqm'
    elif 'sheet' in param_lower:
        return 'per_sheet'
    elif '1000' in param_lower:
        return 'per_1000'
    elif 'percent' in param_lower:
        return 'percentage'
    else:
        return 'currency'

def calculate_most_common_value(used_by):
    """Calculate most common value from usage array"""
    if not used_by:
        return None
    
    values = [u['value'] for u in used_by if u['value'] is not None]
    if not values:
        return None
    
    # Return most frequent value
    from collections import Counter
    return Counter(values).most_common(1)[0][0]

def insert_parameters(conn, parameters):
    """Insert parameters into calculator_pricing_parameters table"""
    cursor = conn.cursor()
    
    inserted_count = 0
    skipped_count = 0
    
    for param in parameters:
        try:
            # Calculate statistics
            most_common = calculate_most_common_value(param['used_by'])
            values = [u['value'] for u in param['used_by'] if u['value'] is not None]
            value_range = {
                'min': min(values) if values else None,
                'max': max(values) if values else None
            } if values else None
            
            # Insert parameter
            cursor.execute("""
                INSERT INTO calculator_pricing_parameters (
                    parameter_name,
                    category,
                    base_value,
                    value_unit,
                    used_by_calculators,
                    most_common_value,
                    value_range,
                    last_modified_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (parameter_name) DO UPDATE SET
                    used_by_calculators = EXCLUDED.used_by_calculators,
                    most_common_value = EXCLUDED.most_common_value,
                    value_range = EXCLUDED.value_range,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (
                param['parameter_name'],
                param['category'],
                param['base_value'],
                param['value_unit'],
                Json(param['used_by']),
                most_common,
                Json(value_range) if value_range else None,
                'data_loader'
            ))
            
            param_id = cursor.fetchone()[0]
            inserted_count += 1
            
            if inserted_count % 50 == 0:
                print(f"  Inserted {inserted_count} parameters...")
            
        except Exception as e:
            print(f"⚠️  Error inserting {param['parameter_name']}: {e}")
            skipped_count += 1
            continue
    
    print(f"✅ Inserted {inserted_count} parameters")
    if skipped_count > 0:
        print(f"⚠️  Skipped {skipped_count} parameters due to errors")
    
    cursor.close()
    return inserted_count

def insert_calculators(conn, calculators_data):
    """Insert calculators into calculators_registry table"""
    cursor = conn.cursor()
    
    inserted_count = 0
    
    for calc in calculators_data:
        try:
            # Build parameters_used JSONB
            parameters_used = {}
            
            # Add pricing constants
            for param_name, param_value in calc.get('pricing_constants', {}).items():
                parameters_used[param_name] = {
                    'value': float(param_value) if param_value else None,
                    'unit': determine_unit(param_name),
                    'override': False
                }
            
            # Add pricing dicts
            for dict_name, dict_values in calc.get('pricing_dicts', {}).items():
                for key, value in dict_values.items():
                    param_name = f"{dict_name}_{key}"
                    parameters_used[param_name] = {
                        'value': float(value) if value else None,
                        'unit': 'currency',
                        'override': False
                    }
            
            # Determine calculator type
            calc_type = 'shopify'  # Most are shopify
            if 'god' in calc['file'].lower():
                calc_type = 'god'
            elif 'custom' in calc['file'].lower():
                calc_type = 'custom'
            
            # Extract special features from metadata
            features = calc.get('metadata', {}).get('features', [])
            
            # Insert calculator
            cursor.execute("""
                INSERT INTO calculators_registry (
                    calculator_name,
                    calculator_type,
                    display_name,
                    file_path,
                    parameters_used,
                    special_features,
                    is_active,
                    last_modified_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (calculator_name) DO UPDATE SET
                    parameters_used = EXCLUDED.parameters_used,
                    special_features = EXCLUDED.special_features,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (
                calc['name'],
                calc_type,
                calc['name'].replace('_', ' ').title(),
                calc['file'],
                Json(parameters_used),
                features,
                True,
                'data_loader'
            ))
            
            inserted_count += 1
            
        except Exception as e:
            print(f"⚠️  Error inserting calculator {calc['name']}: {e}")
            continue
    
    print(f"✅ Inserted {inserted_count} calculators")
    cursor.close()
    return inserted_count

def create_initial_history(conn):
    """Create initial history entries for all parameters"""
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO calculator_parameter_history (
            parameter_id,
            change_type,
            new_value,
            changed_by,
            change_reason
        )
        SELECT 
            id,
            'parameter_created',
            jsonb_build_object(
                'parameter_name', parameter_name,
                'base_value', base_value,
                'usage_count', total_usage_count
            ),
            'data_loader',
            'Initial data load from CALCULATOR_PRICING_CATALOG_EXTRACTED.json'
        FROM calculator_pricing_parameters
        WHERE id NOT IN (SELECT parameter_id FROM calculator_parameter_history)
    """)
    
    count = cursor.rowcount
    print(f"✅ Created {count} history entries")
    cursor.close()
    return count

def main(dry_run=False):
    """Main execution"""
    print("=" * 80)
    print("Calculator Pricing Catalog - Data Loader")
    print("=" * 80)
    print()
    
    if dry_run:
        print("🔍 DRY RUN MODE - No data will be committed")
        print()
    
    # Load JSON data
    calculators_data = load_json_data()
    
    # Extract parameters
    print("\n📊 Extracting parameters...")
    parameters = extract_all_parameters(calculators_data)
    
    # Connect to database
    print(f"\n🔌 Connecting to Supabase PostgreSQL database")
    try:
        conn = psycopg2.connect(DB_URL)
        print("✅ Connected successfully")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n💡 Check Supabase connection URL")
        return 1
    
    try:
        # Insert parameters
        print("\n📥 Inserting parameters...")
        param_count = insert_parameters(conn, parameters)
        
        # Insert calculators
        print("\n📥 Inserting calculators...")
        calc_count = insert_calculators(conn, calculators_data)
        
        # Create history
        print("\n📜 Creating history entries...")
        history_count = create_initial_history(conn)
        
        # Commit or rollback
        if dry_run:
            conn.rollback()
            print("\n🔙 ROLLED BACK (dry run)")
        else:
            conn.commit()
            print("\n✅ COMMITTED to database")
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Parameters inserted: {param_count}")
        print(f"Calculators inserted: {calc_count}")
        print(f"History entries created: {history_count}")
        print()
        
        # Verification query
        if not dry_run:
            print("📊 Verification:")
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM calculator_pricing_parameters")
            print(f"  Total parameters in DB: {cursor.fetchone()[0]}")
            
            cursor.execute("SELECT COUNT(*) FROM calculators_registry")
            print(f"  Total calculators in DB: {cursor.fetchone()[0]}")
            
            cursor.execute("SELECT COUNT(*) FROM calculator_parameter_history")
            print(f"  Total history entries: {cursor.fetchone()[0]}")
            
            cursor.close()
        
        return 0
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error during data load: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        conn.close()
        print("\n🔌 Database connection closed")

if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv
    sys.exit(main(dry_run))
