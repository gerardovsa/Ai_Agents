"""
Create Shopify Tables in Supabase PostgreSQL
=============================================
Migrates Shopify schema from SQLite to PostgreSQL
"""

from AI_infrastructure.shared.database_utils import get_database_connection
from pathlib import Path

def create_shopify_tables():
    """Create all Shopify tables in Supabase"""
    conn = None
    cursor = None
    
    try:
        # Read SQL file
        sql_file = Path(__file__).parent / 'create_shopify_tables_supabase.sql'
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        print("\n📦 Creating Shopify Tables in Supabase PostgreSQL...")
        print("=" * 80)
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Execute the entire script
        cursor.execute(sql_script)
        conn.commit()
        
        print("\n✅ Tables Created Successfully!")
        print("-" * 80)
        
        # List created tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'ai_infrastructure' 
              AND table_name LIKE 'shopify_%'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\n📋 Shopify Tables ({len(tables)} total):")
        print("-" * 80)
        for table in tables:
            print(f"   ✓ {table['table_name']}")
        
        # Show table details
        print("\n" + "=" * 80)
        print("📊 Table Structure Summary:")
        print("=" * 80)
        
        for table in tables:
            table_name = table['table_name']
            cursor.execute(f"""
                SELECT COUNT(*) as row_count
                FROM ai_infrastructure.{table_name}
            """)
            count = cursor.fetchone()['row_count']
            
            cursor.execute(f"""
                SELECT COUNT(*) as col_count
                FROM information_schema.columns
                WHERE table_schema = 'ai_infrastructure'
                  AND table_name = '{table_name}'
            """)
            cols = cursor.fetchone()['col_count']
            
            print(f"   {table_name:35s} | {cols:2d} columns | {count:5d} rows")
        
        print("=" * 80)
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        print("\n✅ Migration Complete!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            try:
                conn.rollback()
            except:
                pass
        return False
        
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("🚀 SHOPIFY/WOOCOMMERCE SCHEMA MIGRATION")
    print("=" * 80)
    print("\nThis will create the following tables in ai_infrastructure schema:")
    print("  - shopify_webhook_events")
    print("  - shopify_orders")
    print("  - shopify_line_items")
    print("  - shopify_line_properties")
    print("  - shopify_customers")
    print("  - shopify_products")
    print("  - shopify_product_mapping")
    print("  - shopify_stock_usage")
    print("  - shopify_price_parity")
    print()
    
    response = input("Continue? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        success = create_shopify_tables()
        if success:
            print("🎉 Ready to sync WooCommerce data!")
        else:
            print("❌ Migration failed. Check errors above.")
    else:
        print("\n❌ Migration cancelled.")
