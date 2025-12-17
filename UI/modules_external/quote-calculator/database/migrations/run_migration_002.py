#!/usr/bin/env python3
"""
Run Migration 002: Fix Duplicates and Add Value Statistics
"""

import psycopg2
from psycopg2.extras import Json
import json
from decimal import Decimal
from statistics import mean, median, stdev

DB_URL = 'postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres'

print("\n" + "="*80)
print("MIGRATION 002: Fix Duplicates & Add Value Statistics")
print("="*80)

try:
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = False
    cur = conn.cursor()
    
    # Step 1: Find and merge duplicates
    print("\n📋 Step 1: Finding duplicate parameters...")
    cur.execute("""
        SELECT LOWER(parameter_name) as lower_name, 
               array_agg(id ORDER BY created_at) as ids,
               array_agg(parameter_name ORDER BY created_at) as names
        FROM calculator_pricing_parameters
        GROUP BY LOWER(parameter_name)
        HAVING COUNT(*) > 1;
    """)
    
    duplicates = cur.fetchall()
    print(f"Found {len(duplicates)} duplicate parameter sets")
    
    for lower_name, ids, names in duplicates:
        print(f"\n  Merging: {names} → {lower_name}")
        merge_into_id = ids[0]
        merge_from_ids = ids[1:]
        
        # Get all calculators from all duplicates
        cur.execute("""
            SELECT jsonb_agg(DISTINCT elem)
            FROM (
                SELECT jsonb_array_elements(used_by_calculators) as elem
                FROM calculator_pricing_parameters
                WHERE id = ANY(%s)
            ) sub;
        """, (ids,))
        
        combined_calculators = cur.fetchone()[0]
        
        # Delete duplicates
        cur.execute("""
            DELETE FROM calculator_pricing_parameters
            WHERE id = ANY(%s);
        """, (merge_from_ids,))
        
        # Update kept parameter
        cur.execute("""
            UPDATE calculator_pricing_parameters
            SET used_by_calculators = %s,
                parameter_name = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s;
        """, (Json(combined_calculators) if isinstance(combined_calculators, (dict, list)) else combined_calculators, 
              lower_name, merge_into_id))
        
        print(f"  ✅ Merged {len(merge_from_ids)} duplicates into ID {merge_into_id}")
    
    # Step 2: Add value_statistics column if it doesn't exist
    print("\n📋 Step 2: Adding value_statistics column...")
    cur.execute("""
        ALTER TABLE calculator_pricing_parameters 
        ADD COLUMN IF NOT EXISTS value_statistics JSONB DEFAULT '{}'::JSONB;
    """)
    
    # Step 3: Calculate statistics for each parameter
    print("\n📋 Step 3: Calculating value statistics...")
    cur.execute("SELECT id, parameter_name, used_by_calculators FROM calculator_pricing_parameters;")
    
    parameters = cur.fetchall()
    updated = 0
    
    for param_id, param_name, used_by_calculators in parameters:
        # Parse JSONB
        if isinstance(used_by_calculators, str):
            calculators = json.loads(used_by_calculators)
        else:
            calculators = used_by_calculators
        
        # Extract values (skip None values)
        values = [float(calc['value']) for calc in calculators if calc.get('value') is not None]
        
        if not values:
            continue
        
        # Calculate statistics
        min_val = min(values)
        max_val = max(values)
        mean_val = mean(values)
        median_val = median(values)
        std_dev_val = stdev(values) if len(values) > 1 else 0
        distinct_values = sorted(list(set(values)))
        
        # Count occurrences of each value
        value_counts = {}
        for val in values:
            val_str = str(val)
            value_counts[val_str] = value_counts.get(val_str, 0) + 1
        
        # Build statistics object
        stats = {
            'range': {'min': min_val, 'max': max_val},
            'mean': round(mean_val, 4),
            'median': round(median_val, 4),
            'std_dev': round(std_dev_val, 4),
            'distinct_count': len(distinct_values),
            'distinct_values': distinct_values,
            'value_counts': value_counts
        }
        
        # Update parameter
        cur.execute("""
            UPDATE calculator_pricing_parameters
            SET value_statistics = %s,
                total_usage_count = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s;
        """, (Json(stats), len(calculators), param_id))
        
        updated += 1
        if updated % 10 == 0:
            print(f"  Updated {updated} parameters...")
    
    print(f"✅ Updated {updated} parameters with statistics")
    
    # Step 4: Update calculators_registry
    print("\n📋 Step 4: Updating calculator parameter counts...")
    cur.execute("""
        UPDATE calculators_registry
        SET total_parameters_count = (
            SELECT COUNT(*)
            FROM jsonb_object_keys(parameters_used)
        ),
        updated_at = CURRENT_TIMESTAMP;
    """)
    
    # Step 5: Create analysis view
    print("\n📋 Step 5: Creating analysis view...")
    cur.execute("""
        DROP VIEW IF EXISTS v_parameter_value_analysis;
        
        CREATE VIEW v_parameter_value_analysis AS
        SELECT 
            p.id,
            p.parameter_name,
            p.category,
            p.base_value,
            p.total_usage_count,
            (p.value_statistics->>'mean')::DECIMAL as mean_value,
            (p.value_statistics->'range'->>'min')::DECIMAL as min_value,
            (p.value_statistics->'range'->>'max')::DECIMAL as max_value,
            (p.value_statistics->>'distinct_count')::INTEGER as distinct_values,
            -- Calculate variance (how different are the values)
            CASE 
                WHEN (p.value_statistics->'range'->>'max')::DECIMAL = (p.value_statistics->'range'->>'min')::DECIMAL 
                THEN 0
                ELSE ((p.value_statistics->'range'->>'max')::DECIMAL - (p.value_statistics->'range'->>'min')::DECIMAL) / 
                     NULLIF((p.value_statistics->>'mean')::DECIMAL, 0) * 100
            END as variance_percentage,
            -- Calculator breakdown
            p.used_by_calculators,
            p.value_statistics
        FROM calculator_pricing_parameters p
        ORDER BY variance_percentage DESC NULLS LAST;
    """)
    
    # Commit all changes
    conn.commit()
    
    # Show results
    print("\n" + "="*80)
    print("📊 TOP 10 PARAMETERS WITH HIGHEST VALUE VARIANCE")
    print("="*80)
    
    cur.execute("""
        SELECT parameter_name, min_value, max_value, mean_value, 
               variance_percentage, total_usage_count
        FROM v_parameter_value_analysis
        WHERE variance_percentage > 0
        ORDER BY variance_percentage DESC
        LIMIT 10;
    """)
    
    print(f"\n{'Parameter':<30} {'Min':<10} {'Max':<10} {'Mean':<10} {'Variance':<10} {'Used By'}")
    print("-" * 80)
    
    for row in cur.fetchall():
        param, min_v, max_v, mean_v, var_pct, usage = row
        print(f"{param:<30} ${min_v:<9.2f} ${max_v:<9.2f} ${mean_v:<9.2f} {var_pct:<9.1f}% {usage}")
    
    # Show sample calculator values for a high-variance parameter
    print("\n" + "="*80)
    print("📋 SAMPLE: impos_setup VALUES BY CALCULATOR")
    print("="*80)
    
    cur.execute("""
        SELECT 
            elem->>'calculator' as calculator,
            (elem->>'value')::DECIMAL as value,
            (elem->>'override')::BOOLEAN as is_override
        FROM calculator_pricing_parameters p,
             LATERAL jsonb_array_elements(p.used_by_calculators) as elem
        WHERE p.parameter_name = 'impos_setup'
        ORDER BY (elem->>'value')::DECIMAL DESC
        LIMIT 10;
    """)
    
    print(f"\n{'Calculator':<40} {'Value':<15} {'Override?'}")
    print("-" * 70)
    
    for calc, val, override in cur.fetchall():
        override_str = "YES" if override else "NO"
        print(f"{calc:<40} ${val:<14.2f} {override_str}")
    
    conn.close()
    
    print("\n" + "="*80)
    print("✅ MIGRATION 002 COMPLETE")
    print("="*80)
    print("\nNew features:")
    print("  • Duplicates merged (cutting_block + CUTTING_BLOCK)")
    print("  • value_statistics column added with range/mean/median/std_dev")
    print("  • v_parameter_value_analysis view created")
    print("  • total_usage_count now calculated correctly")
    print("\n")

except Exception as e:
    conn.rollback()
    print(f"\n❌ Error: {e}\n")
    import traceback
    traceback.print_exc()
