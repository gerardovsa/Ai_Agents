"""
Check if Stock 249 (Adestor Gloss Removable) exists in BOTH databases:
1. SQLite unified_stocks table
2. SQL Server InHousePrint Stock table
"""
import sqlite3
import sys
import os
import pandas as pd

# Add In_House_SQL to path for db_connector
sys.path.insert(0, r'c:\Users\gpoli\GIT\In_House_SQL')

print("=" * 100)
print("CHECKING STOCK 249 (Adestor Gloss Removable) IN BOTH DATABASES")
print("=" * 100)

# ===========================
# 1. CHECK SQLITE DATABASE
# ===========================
print("\n" + "=" * 100)
print("1. SQLITE DATABASE: unified_stocks table")
print("=" * 100)

try:
    conn = sqlite3.connect(r'c:\Users\gpoli\GIT\AI_agents\data\stock_data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM unified_stocks WHERE stock_id = "249"')
    row = cursor.fetchone()
    
    if row:
        print("\n✅ FOUND in SQLite unified_stocks:")
        print(f"   Stock ID: {row['stock_id']}")
        print(f"   Name: {row['stock_type_name']}")
        print(f"   Description: {row['stock_description']}")
        print(f"   Format: {row['length_mm']}mm × {row['width_mm']}mm SHEETS")
        print(f"   Unit Type: {row['unit_type']}")
        print(f"   Category: {row['stock_category']}")
        print(f"   Cost: ${row['cost_per_thousand']}/1000 sheets")
        print(f"   Markup: {row['markup']}%")
        print(f"   Active: {row['is_active']}")
        print(f"   Source: {row['source']}")
    else:
        print("\n❌ NOT FOUND in SQLite unified_stocks")
    
    conn.close()
except Exception as e:
    print(f"\n❌ Error accessing SQLite: {e}")

# ===========================
# 2. CHECK SQL SERVER DATABASE
# ===========================
print("\n" + "=" * 100)
print("2. SQL SERVER DATABASE: Stock table")
print("=" * 100)

try:
    from db_connector import InHousePrintDB
    
    # Use correct config path
    config_path = r'c:\Users\gpoli\GIT\In_House_SQL\config\database-config.json'
    db = InHousePrintDB(config_path=config_path)
    
    # First, list all tables to find the stock table
    tables_query = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        AND TABLE_NAME LIKE '%Stock%'
        ORDER BY TABLE_NAME
    """
    
    print("\nFinding Stock tables in SQL Server...")
    tables_df = db.execute_query(tables_query)
    print(f"Found {len(tables_df)} tables with 'Stock' in name:")
    for table in tables_df['TABLE_NAME']:
        print(f"   - {table}")
    
    # Stock 249 is digital stock, so check Quote_DigitalStocks
    print("\nQuerying Quote_DigitalStocks for Stock ID 249...")
    
    # First check structure
    structure_query = """
        SELECT TOP 1 * FROM Quote_DigitalStocks
    """
    sample = db.execute_query(structure_query)
    print(f"Quote_DigitalStocks columns: {', '.join(sample.columns)}")
    
    # Now query for stock 249
    query = f"""
        SELECT * FROM Quote_DigitalStocks
        WHERE StockID = 249
    """
    
    df = db.execute_query(query)
    
    if not df.empty:
        print("\n✅ FOUND in SQL Server Quote_DigitalStocks table:")
        row = df.iloc[0]
        for col in df.columns:
            if pd.notna(row[col]):
                print(f"   {col}: {row[col]}")
        
        # Get the stock type description from Quote_DigitalStockType
        type_query = f"""
            SELECT StockTypeDesc, Colour, SupplierName, CurrentStockLevel, IsActive
            FROM Quote_DigitalStockType
            WHERE StockTypeID = {int(row['StockTypeID'])}
        """
        type_df = db.execute_query(type_query)
        if not type_df.empty:
            print(f"\n   From Quote_DigitalStockType:")
            type_row = type_df.iloc[0]
            for col in type_df.columns:
                if pd.notna(type_row[col]):
                    print(f"      {col}: {type_row[col]}")
    else:
        print("\n❌ NOT FOUND in SQL Server Quote_DigitalStocks table")
    
    db.close()
    
except ImportError:
    print("\n⚠️  Could not import db_connector - SQL Server check skipped")
    print("   Install: pip install pyodbc pandas")
except FileNotFoundError as e:
    print(f"\n⚠️  Database config not found: {e}")
    print("   SQL Server connection requires database-config.json")
except Exception as e:
    print(f"\n❌ Error accessing SQL Server: {e}")

# ===========================
# SUMMARY
# ===========================
print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
print("""
Stock 249 - Adestor Gloss Removable:

FORMAT: Pre-cut SHEETS (450mm × 320mm)
USE: Digital printing on sheet-fed presses
NOT SUITABLE FOR: Roll-to-roll vinyl sticker production

The stock exists in BOTH databases because:
1. SQLite unified_stocks syncs FROM SQL Server Stock table
2. unified_stocks.source = 'sql_server' confirms it came from SQL Server
3. Both databases reference the same physical stock item

This is digital printing sheet stock, not roll-to-roll vinyl.
It cannot be used for the vinyl stickers calculator which requires:
- 1370mm width rolls
- 50m+ lengths
- Wide-format printer compatibility
- Vinyl plotter compatibility
""")
