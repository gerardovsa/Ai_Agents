"""
Query stock_data.db for vinyl stock items in unified_stocks table
"""
import sqlite3
import json

def query_vinyl_stocks():
    conn = sqlite3.connect('data/stock_data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # First, list all tables
    print("=" * 80)
    print("TABLES IN stock_data.db:")
    print("=" * 80)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    for table in tables:
        print(f"  - {table['name']}")
    
    # Check if unified_stocks table exists
    if 'unified_stocks' in [t['name'] for t in tables]:
        print("\n" + "=" * 80)
        print("UNIFIED_STOCKS TABLE SCHEMA:")
        print("=" * 80)
        cursor.execute("PRAGMA table_info(unified_stocks)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col['name']:30s} {col['type']:15s} {'NOT NULL' if col['notnull'] else ''}")
        
        # Query for vinyl stock items
        print("\n" + "=" * 80)
        print("VINYL STOCK ITEMS IN unified_stocks:")
        print("=" * 80)
        
        cursor.execute("""
            SELECT * FROM unified_stocks 
            WHERE LOWER(stock_id) LIKE '%vinyl%' 
               OR LOWER(stock_description) LIKE '%vinyl%'
               OR LOWER(stock_type_name) LIKE '%vinyl%'
               OR LOWER(stock_description) LIKE '%monomeric%'
               OR LOWER(stock_description) LIKE '%polymeric%'
               OR LOWER(stock_description) LIKE '%laminate%'
               OR LOWER(stock_description) LIKE '%adestor%'
               OR LOWER(stock_type_name) LIKE '%monomeric%'
               OR LOWER(stock_type_name) LIKE '%polymeric%'
               OR LOWER(stock_type_name) LIKE '%laminate%'
               OR LOWER(colour) LIKE '%vinyl%'
               OR LOWER(material_type) LIKE '%vinyl%'
            ORDER BY stock_description
        """)
        
        vinyl_stocks = cursor.fetchall()
        
        if vinyl_stocks:
            print(f"\nFound {len(vinyl_stocks)} vinyl-related stock items:\n")
            
            for idx, stock in enumerate(vinyl_stocks, 1):
                print(f"\n{idx}. STOCK ID: {stock['stock_id']}")
                print(f"   Stock Type Name: {stock['stock_type_name']}")
                print(f"   Description: {stock['stock_description']}")
                print(f"   Category: {stock['stock_category']}")
                print(f"   Material Type: {stock['material_type']}")
                if stock['roll_width_mm']:
                    print(f"   Roll Width: {stock['roll_width_mm']}mm")
                if stock['roll_length_mm']:
                    print(f"   Roll Length: {stock['roll_length_mm']}mm")
                if stock['length_mm'] and stock['width_mm']:
                    print(f"   Sheet Dimensions: {stock['length_mm']}mm x {stock['width_mm']}mm")
                if stock['gsm']:
                    print(f"   GSM: {stock['gsm']}")
                if stock['thickness_mm']:
                    print(f"   Thickness: {stock['thickness_mm']}mm")
                print(f"   Colour: {stock['colour']}")
                print(f"   Finish: {stock['finish']}")
                if stock['cost_per_thousand']:
                    print(f"   Cost/1000: ${stock['cost_per_thousand']:.2f}")
                if stock['cost_per_roll']:
                    print(f"   Cost/Roll: ${stock['cost_per_roll']:.2f}")
                if stock['cost_per_sqm']:
                    print(f"   Cost/SQM: ${stock['cost_per_sqm']:.2f}")
                if stock['cost_per_lm']:
                    print(f"   Cost/Linear Metre: ${stock['cost_per_lm']:.2f}")
                if stock['markup']:
                    print(f"   Markup: {stock['markup']:.1f}%")
                print(f"   Supplier: {stock['supplier_name']}")
                print(f"   Brand: {stock['brand_name']}")
                print(f"   Active: {'Yes' if stock['is_active'] else 'No'}")
        else:
            print("\nNo vinyl stock items found in unified_stocks table.")
            
            # Try broader search
            print("\n" + "=" * 80)
            print("ALL STOCK ITEMS (first 20):")
            print("=" * 80)
            cursor.execute("SELECT * FROM unified_stocks LIMIT 20")
            all_stocks = cursor.fetchall()
            for stock in all_stocks:
                print(f"\n  Stock ID: {stock['stock_id']}")
                print(f"  Description: {stock['stock_description']}")
    else:
        print("\n  unified_stocks table NOT FOUND!")
        print("\n  Searching for similar table names...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%stock%'")
        stock_tables = cursor.fetchall()
        for table in stock_tables:
            print(f"    - {table['name']}")
    
    conn.close()

if __name__ == "__main__":
    query_vinyl_stocks()
