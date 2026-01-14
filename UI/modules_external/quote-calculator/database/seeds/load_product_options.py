"""
Load Product Options Data into Database

Purpose:
    Load extracted product options from PRODUCT_OPTIONS_EXTRACTED.json into:
    - product_options table (155 options expected)
    - product_option_choices table (436 choices expected)
    - product_option_history table (log all creations)

Author: AI Agent
Date: December 17, 2025
"""

import json
import psycopg2
from psycopg2.extras import Json, RealDictCursor
from pathlib import Path

DB_URL = 'postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres'
JSON_FILE = Path(__file__).parent / 'PRODUCT_OPTIONS_EXTRACTED.json'

def load_product_options_data():
    """Main data loading function"""
    print("\n" + "="*80)
    print("LOAD PRODUCT OPTIONS DATA")
    print("="*80 + "\n")
    
    # Load JSON file
    print(f"Loading: {JSON_FILE.name}")
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Loaded {len(data)} calculators\n")
    
    # Connect to database
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = False  # Use transactions
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        stats = {
            'options_created': 0,
            'choices_created': 0,
            'history_logged': 0,
            'errors': []
        }
        
        # Process each calculator
        for calculator_name, calc_data in data.items():
            print(f"Processing: {calculator_name}")
            print(f"  Product: {calc_data['product_title']}")
            print(f"  Options: {calc_data['total_options']}, Choices: {calc_data['total_choices']}")
            
            # Process each option
            for option_data in calc_data['options']:
                option_name = option_data['option_name']
                
                try:
                    # Insert option
                    cur.execute("""
                        INSERT INTO product_options (
                            calculator_name,
                            option_name,
                            field_id,
                            option_type,
                            is_required,
                            default_choice,
                            display_order,
                            metadata
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        calculator_name,
                        option_name,
                        option_data.get('field_id'),
                        option_data.get('option_type', 'select'),
                        option_data.get('is_required', False),
                        option_data.get('default_choice'),
                        None,  # display_order will be set later if needed
                        Json({
                            'calculator_key': calc_data['calculator_key'],
                            'product_title': calc_data['product_title']
                        })
                    ))
                    
                    option_id = cur.fetchone()['id']
                    stats['options_created'] += 1
                    
                    # Log option creation to history
                    cur.execute("""
                        INSERT INTO product_option_history (
                            change_type,
                            option_id,
                            new_value,
                            changed_by
                        ) VALUES (%s, %s, %s, %s)
                    """, (
                        'option_created',
                        option_id,
                        Json({
                            'calculator_name': calculator_name,
                            'option_name': option_name,
                            'field_id': option_data.get('field_id')
                        }),
                        'data_loader'
                    ))
                    stats['history_logged'] += 1
                    
                except psycopg2.errors.UniqueViolation:
                    # Duplicate option, skip but get existing ID
                    conn.rollback()
                    cur = conn.cursor(cursor_factory=RealDictCursor)  # Re-create cursor after rollback
                    cur.execute("""
                        SELECT id FROM product_options
                        WHERE calculator_name = %s AND option_name = %s
                    """, (calculator_name, option_name))
                    result = cur.fetchone()
                    if result:
                        option_id = result['id']
                        print(f"    ⚠️  {option_name}: duplicate (using existing ID {option_id})")
                        stats['errors'].append(f"Duplicate option: {calculator_name}.{option_name}")
                    else:
                        print(f"    ❌ {option_name}: duplicate but couldn't find existing record!")
                        continue
                
                # Insert choices for this option
                choices_for_option = 0
                for choice_data in option_data['choices']:
                    cur.execute("""
                        INSERT INTO product_option_choices (
                            option_id,
                            choice_title,
                            price,
                            price_type,
                            sku,
                            display_order,
                            description,
                            metadata
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        option_id,
                        choice_data['choice_title'],
                        choice_data['price'],
                        choice_data.get('price_type', 'fixed'),
                        choice_data.get('sku'),
                        choice_data.get('display_order'),
                        choice_data.get('description'),
                        Json({})  # Empty metadata for now
                    ))
                    
                    choice_id = cur.fetchone()['id']
                    stats['choices_created'] += 1
                    choices_for_option += 1
                    
                    # Log choice creation to history
                    cur.execute("""
                        INSERT INTO product_option_history (
                            change_type,
                            choice_id,
                            new_value,
                            changed_by
                        ) VALUES (%s, %s, %s, %s)
                    """, (
                        'choice_created',
                        choice_id,
                        Json({
                            'choice_title': choice_data['choice_title'],
                            'price': float(choice_data['price']),
                            'price_type': choice_data.get('price_type', 'fixed')
                        }),
                        'data_loader'
                    ))
                    stats['history_logged'] += 1
                
                print(f"    ✅ {option_name}: {choices_for_option} choices")
            
            print()
        
        # Commit transaction
        conn.commit()
        
        # Print summary
        print("="*80)
        print("DATA LOADING SUMMARY")
        print("="*80)
        print(f"\n✅ Options created: {stats['options_created']}")
        print(f"✅ Choices created: {stats['choices_created']}")
        print(f"✅ History entries logged: {stats['history_logged']}")
        
        # Verify data
        print("\n" + "-"*80)
        print("VERIFICATION")
        print("-"*80 + "\n")
        
        # Count by table
        cur.execute("SELECT COUNT(*) as count FROM product_options")
        print(f"product_options: {cur.fetchone()['count']} rows")
        
        cur.execute("SELECT COUNT(*) as count FROM product_option_choices")
        print(f"product_option_choices: {cur.fetchone()['count']} rows")
        
        cur.execute("SELECT COUNT(*) as count FROM product_option_history")
        print(f"product_option_history: {cur.fetchone()['count']} rows")
        
        # Test views
        print("\n" + "-"*80)
        print("VIEW TESTS")
        print("-"*80 + "\n")
        
        # Calculator config summary
        cur.execute("""
            SELECT * FROM v_calculator_options_config
            ORDER BY total_options DESC
            LIMIT 5
        """)
        print("Top 5 calculators by option count:")
        for row in cur.fetchall():
            print(f"  {row['calculator_name']}: {row['total_options']} options ({row['required_options']} required)")
        
        # Price variance analysis
        cur.execute("""
            SELECT * FROM v_option_price_variance
            ORDER BY variance_percentage DESC
            LIMIT 5
        """)
        print("\nTop 5 options by price variance:")
        for row in cur.fetchall():
            print(f"  {row['calculator_name']}.{row['option_name']}: {row['variance_percentage']}% variance")
            print(f"    Range: ${row['min_price']} - ${row['max_price']}")
        
        # Sample data
        print("\n" + "-"*80)
        print("SAMPLE DATA (First 3 Options)")
        print("-"*80 + "\n")
        
        cur.execute("""
            SELECT 
                po.calculator_name,
                po.option_name,
                po.field_id,
                COUNT(poc.id) as choice_count,
                MIN(poc.price) as min_price,
                MAX(poc.price) as max_price
            FROM product_options po
            LEFT JOIN product_option_choices poc ON po.id = poc.option_id
            GROUP BY po.id, po.calculator_name, po.option_name, po.field_id
            ORDER BY po.calculator_name, po.option_name
            LIMIT 3
        """)
        
        for row in cur.fetchall():
            print(f"{row['calculator_name']}.{row['option_name']} ({row['field_id']})")
            print(f"  Choices: {row['choice_count']}, Price range: ${row['min_price']} - ${row['max_price']}")
            print()
        
        print("="*80)
        print("✅ PRODUCT OPTIONS DATA LOADING COMPLETE")
        print("="*80 + "\n")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    load_product_options_data()
