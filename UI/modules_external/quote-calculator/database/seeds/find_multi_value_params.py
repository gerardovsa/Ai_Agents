#!/usr/bin/env python3
"""
Find parameters used by multiple calculators with multiple distinct values.
This shows which parameters have calculator-specific customization.
"""

import psycopg2
from psycopg2.extras import Json
import json
import os
from dotenv import load_dotenv

# Supabase connection URL (same as load_extracted_data.py)
DB_URL = 'postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres'

def main():
    """Find and display parameters with multiple products and multiple values."""
    
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    print('=' * 120)
    print('PARAMETERS WITH MULTIPLE CALCULATORS AND MULTIPLE VALUES')
    print('=' * 120)
    print()
    
    # Query parameters with high variance
    cur.execute("""
        SELECT 
            parameter_name,
            category,
            base_value,
            total_usage_count,
            (value_statistics->>'distinct_count')::INTEGER as distinct_values_count,
            value_statistics->'distinct_values' as distinct_values_json,
            value_statistics->'range' as range_json,
            (value_statistics->>'mean')::DECIMAL as mean_value,
            value_statistics->'value_counts' as value_counts_json
        FROM calculator_pricing_parameters
        WHERE 
            total_usage_count >= 5  -- Used by at least 5 calculators
            AND (value_statistics->>'distinct_count')::INTEGER >= 3  -- At least 3 different values
        ORDER BY 
            (value_statistics->>'distinct_count')::INTEGER DESC,
            total_usage_count DESC
        LIMIT 15;
    """)
    
    results = cur.fetchall()
    
    print(f"Found {len(results)} parameters with multiple values across multiple calculators\n")
    
    for idx, row in enumerate(results, 1):
        param_name, category, base_value, usage_count, distinct_count, distinct_vals, range_json, mean_val, value_counts = row
        
        # JSONB is already parsed by psycopg2
        distinct_values = distinct_vals if distinct_vals else []
        value_range = range_json if range_json else {}
        counts = value_counts if value_counts else {}
        
        print(f"{idx}. Parameter: {param_name}")
        print(f"   Category: {category}")
        print(f"   Base Value: ${base_value}")
        print(f"   Used By: {usage_count} calculators")
        print(f"   Distinct Values: {distinct_count} different values")
        
        if value_range:
            print(f"   Range: ${value_range.get('min', 0)} - ${value_range.get('max', 0)}")
        
        if mean_val:
            print(f"   Mean: ${mean_val}")
        
        print(f"   All Values: {distinct_values}")
        
        # Show value distribution
        if counts:
            print(f"   Distribution:")
            sorted_counts = sorted(counts.items(), key=lambda x: float(x[0]), reverse=True)
            for value, count in sorted_counts[:5]:  # Top 5
                print(f"      ${value} used by {count} calculator(s)")
        
        print()
        print('-' * 120)
        print()
    
    # Pick the best example - most diverse parameter
    if results:
        best_param = results[0][0]  # First result has highest distinct_count
        
        print()
        print('=' * 120)
        print(f'DETAILED PER-CALCULATOR BREAKDOWN: {best_param}')
        print('=' * 120)
        print()
        
        cur.execute("""
            SELECT 
                parameter_name,
                used_by_calculators
            FROM calculator_pricing_parameters
            WHERE parameter_name = %s;
        """, (best_param,))
        
        result = cur.fetchone()
        if result:
            param_name, calculators = result
            
            # Sort by value (descending)
            calc_list = sorted(calculators, key=lambda x: float(x.get('value', 0)), reverse=True)
            
            print(f"{'Calculator Name':<45} {'Value':<15} {'Override?':<12}")
            print('-' * 120)
            
            for calc in calc_list:
                calc_name = calc.get('calculator', 'Unknown')[:43]
                value = calc.get('value', 0)
                override = 'YES' if calc.get('override', False) else 'NO'
                print(f"{calc_name:<45} ${value:<14.2f} {override:<12}")
    
    cur.close()
    conn.close()
    
    print()
    print('=' * 120)
    print('✅ QUERY COMPLETE')
    print('=' * 120)

if __name__ == '__main__':
    main()
