"""
Migration 003: Populate calculator_parameter_overrides from JSONB arrays

Purpose:
    Transform the used_by_calculators JSONB arrays in calculator_pricing_parameters
    into individual rows in calculator_parameter_overrides table. This enables:
    - Per-calculator price customization
    - Individual override management (activate/deactivate)
    - Cleaner queries (no JSONB array traversal)
    - Better foreign key relationships

Strategy:
    1. Read each parameter's used_by_calculators JSONB array
    2. For each calculator using the parameter:
       - If value != base_value: Create override row
       - If value == base_value: Skip (will use base value)
    3. Log all creations to calculator_parameter_history

Expected Result:
    - ~284 override rows created (only where value differs from base)
    - History entries logged for each override creation
    - calculator_parameter_overrides table populated and ready for use

Author: AI Agent
Date: December 17, 2025
"""

import psycopg2
from psycopg2.extras import Json, RealDictCursor
import json
from datetime import datetime
from decimal import Decimal

# Supabase PostgreSQL connection
DB_URL = 'postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres'

def connect_db():
    """Establish database connection"""
    return psycopg2.connect(DB_URL)

def get_all_parameters(conn):
    """Fetch all parameters with their JSONB arrays"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT 
                id,
                parameter_name,
                base_value,
                used_by_calculators
            FROM calculator_pricing_parameters
            ORDER BY parameter_name
        """)
        return cur.fetchall()

def create_override(conn, parameter_id, calculator_name, override_value):
    """Create a single override row"""
    with conn.cursor() as cur:
        # Check if override already exists
        cur.execute("""
            SELECT id FROM calculator_parameter_overrides
            WHERE parameter_id = %s 
            AND calculator_name = %s 
            AND is_active = TRUE
        """, (parameter_id, calculator_name))
        
        if cur.fetchone():
            return None  # Override already exists, skip
        
        # Insert override
        cur.execute("""
            INSERT INTO calculator_parameter_overrides 
                (parameter_id, calculator_name, override_value, override_reason, is_active, created_by)
            VALUES (%s, %s, %s, %s, TRUE, %s)
            RETURNING id
        """, (
            parameter_id,
            calculator_name,
            override_value,
            f'Migrated from JSONB array for {calculator_name}',
            'migration_003'
        ))
        
        override_id = cur.fetchone()[0]
        return override_id

def log_to_history(conn, parameter_id, override_value, calculator_name):
    """Log override creation to history table"""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO calculator_parameter_history
                (change_type, parameter_id, old_value, new_value, changed_by)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            'override_created',
            parameter_id,
            Json({'source': 'migration', 'calculator': calculator_name}),
            Json({'override_value': float(override_value), 'calculator_name': calculator_name}),
            'migration_003'
        ))

def populate_overrides():
    """Main migration function"""
    conn = connect_db()
    
    try:
        print("\n" + "="*80)
        print("MIGRATION 003: POPULATE PRICING CONSTANT OVERRIDES")
        print("="*80 + "\n")
        
        # Get all parameters
        parameters = get_all_parameters(conn)
        print(f"✅ Found {len(parameters)} parameters to process\n")
        
        total_overrides_created = 0
        total_skipped_base_match = 0
        errors = []
        
        # Process each parameter
        for param in parameters:
            param_id = param['id']
            param_name = param['parameter_name']
            
            # Handle None base_value
            if param['base_value'] is None:
                print(f"⏭️  Skipping {param_name}: base_value is NULL")
                continue
                
            base_value = Decimal(str(param['base_value']))
            used_by = param['used_by_calculators'] or []
            
            print(f"Processing: {param_name} (base_value: {base_value})")
            print(f"  Used by {len(used_by)} calculators")
            
            overrides_for_param = 0
            skipped_for_param = 0
            
            # Process each calculator using this parameter
            for calc_data in used_by:
                calculator_name = calc_data.get('calculator')
                calc_value = calc_data.get('value')
                
                if not calculator_name or calc_value is None:
                    continue
                
                # Convert value to Decimal for comparison
                calc_value_decimal = Decimal(str(calc_value))
                
                # Only create override if value differs from base
                if calc_value_decimal != base_value:
                    override_id = create_override(
                        conn, 
                        param_id, 
                        calculator_name, 
                        calc_value_decimal
                    )
                    
                    if override_id:
                        log_to_history(
                            conn,
                            param_id,
                            calc_value_decimal,
                            calculator_name
                        )
                        overrides_for_param += 1
                        total_overrides_created += 1
                        print(f"    ✅ Created override: {calculator_name} = {calc_value_decimal}")
                    else:
                        print(f"    ⏭️  Override already exists: {calculator_name}")
                else:
                    skipped_for_param += 1
                    total_skipped_base_match += 1
            
            if overrides_for_param > 0:
                print(f"  📊 Created {overrides_for_param} overrides, skipped {skipped_for_param} (match base)\n")
            else:
                print(f"  ⏭️  No overrides needed (all match base value)\n")
        
        # Commit transaction
        conn.commit()
        
        # Print summary
        print("\n" + "="*80)
        print("MIGRATION 003 COMPLETE")
        print("="*80)
        print("\n✅ Total overrides created: {total_overrides_created}")
        print(f"⏭️  Skipped (match base value): {total_skipped_base_match}")
        
        if errors:
            print(f"\n⚠️  ERRORS ENCOUNTERED ({len(errors)}):")
            for error in errors[:10]:  # Show first 10 errors
                print(f"   - {error}")
            if len(errors) > 10:
                print(f"   ... and {len(errors) - 10} more")
        
        # Verify results
        print("\n" + "-"*80)
        print("VERIFICATION")
        print("-"*80)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Count overrides
            cur.execute("SELECT COUNT(*) as count FROM calculator_parameter_overrides WHERE is_active = TRUE")
            override_count = cur.fetchone()['count']
            print(f"✅ Active overrides in database: {override_count}")
            
            # Count history entries
            cur.execute("SELECT COUNT(*) as count FROM calculator_parameter_history WHERE change_type = 'override_created'")
            history_count = cur.fetchone()['count']
            print(f"✅ History entries created: {history_count}")
            
            # Show sample overrides
            cur.execute("""
                SELECT 
                    cpp.parameter_name,
                    cpo.calculator_name,
                    cpp.base_value,
                    cpo.override_value,
                    cpo.override_reason
                FROM calculator_parameter_overrides cpo
                JOIN calculator_pricing_parameters cpp ON cpo.parameter_id = cpp.id
                WHERE cpo.is_active = TRUE
                ORDER BY cpp.parameter_name, cpo.calculator_name
                LIMIT 10
            """)
            samples = cur.fetchall()
            
            if samples:
                print("\n📋 SAMPLE OVERRIDES (first 10):")
                print(f"{'Parameter':<30} {'Calculator':<25} {'Base':<10} {'Override':<10}")
                print("-" * 75)
                for row in samples:
                    print(f"{row['parameter_name']:<30} {row['calculator_name']:<25} {row['base_value']:<10.2f} {row['override_value']:<10.2f}")
        
        print("\n✅ Migration 003 completed successfully!\n")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    finally:
        conn.close()

if __name__ == '__main__':
    populate_overrides()
