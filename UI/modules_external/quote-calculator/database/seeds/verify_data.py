#!/usr/bin/env python3
"""
Quick verification script for calculator pricing catalog data
"""

import psycopg2

DB_URL = 'postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres'

print("\n" + "="*80)
print("CALCULATOR PRICING CATALOG - DATA VERIFICATION")
print("="*80)

try:
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    # Top 10 most used parameters
    print("\n📊 Top 10 Most Used Parameters:\n")
    cur.execute("""
        SELECT parameter_name, category, base_value, total_usage_count,
               jsonb_array_length(used_by_calculators) as actual_count
        FROM calculator_pricing_parameters
        ORDER BY jsonb_array_length(used_by_calculators) DESC
        LIMIT 10;
    """)
    
    for i, row in enumerate(cur.fetchall(), 1):
        param, cat, val, stored_count, actual_count = row
        print(f"{i}. {param} ({cat}) = ${val:.2f} - Used by {actual_count} calculators")
    
    # Sample calculators
    print("\n\n📋 Sample Calculators:\n")
    cur.execute("""
        SELECT calculator_name, calculator_type, 
               jsonb_object_keys(parameters_used) as param_count,
               special_features
        FROM calculators_registry
        LIMIT 5;
    """)
    
    for row in cur.fetchall():
        name, type_, params, features = row
        print(f"• {name} ({type_}) - Features: {features}")
    
    # Statistics
    print("\n\n📈 Database Statistics:\n")
    cur.execute("SELECT COUNT(*) FROM calculator_pricing_parameters;")
    param_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM calculators_registry;")
    calc_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM calculator_parameter_history;")
    history_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM calculator_parameter_overrides;")
    override_count = cur.fetchone()[0]
    
    print(f"Parameters: {param_count}")
    print(f"Calculators: {calc_count}")
    print(f"History Entries: {history_count}")
    print(f"Overrides: {override_count}")
    
    conn.close()
    
    print("\n" + "="*80)
    print("✅ VERIFICATION COMPLETE")
    print("="*80 + "\n")

except Exception as e:
    print(f"\n❌ Error: {e}\n")
