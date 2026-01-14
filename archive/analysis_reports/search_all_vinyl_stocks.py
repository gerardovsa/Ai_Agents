"""
Search ALL databases for vinyl stock items
Including:
1. AI_agents/data/stock_data.db (SQLite)
2. In_House_SQL/G_Folder/Quote_Calculator/stocks/stock_data.db (SQLite)
3. In_House_SQL/G_Folder/Inventory/stock_data.db (SQLite)
4. In_House_SQL/G_Folder/Inv-Stock/stocks/stock_data.db (SQLite)
5. InHousePrint SQL Server database
"""
import sqlite3
import sys
import os

# Add In_House_SQL to path for db_connector
sys.path.insert(0, r'c:\Users\gpoli\GIT\In_House_SQL')

def search_sqlite_db(db_path, db_name):
    """Search a SQLite database for vinyl stock"""
    print("\n" + "=" * 100)
    print(f"DATABASE: {db_name}")
    print(f"Path: {db_path}")
    print("=" * 100)
    
    if not os.path.exists(db_path):
        print(f"  ❌ Database file not found!")
        return []
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"\nTables found: {len(tables)}")
        
        vinyl_stocks = []
        
        # Search relevant tables
        for table in tables:
            if 'stock' in table.lower() or 'material' in table.lower() or 'inventory' in table.lower():
                print(f"\n  Searching table: {table}")
                
                # Get columns
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                # Build search query based on available columns
                search_conditions = []
                for col in columns:
                    col_lower = col.lower()
                    if any(term in col_lower for term in ['desc', 'name', 'type', 'material', 'colour', 'color']):
                        search_conditions.append(f"LOWER({col}) LIKE '%vinyl%'")
                        search_conditions.append(f"LOWER({col}) LIKE '%monomeric%'")
                        search_conditions.append(f"LOWER({col}) LIKE '%polymeric%'")
                        search_conditions.append(f"LOWER({col}) LIKE '%laminate%'")
                        search_conditions.append(f"LOWER({col}) LIKE '%adestor%'")
                
                if search_conditions:
                    query = f"SELECT * FROM {table} WHERE {' OR '.join(search_conditions)}"
                    try:
                        cursor.execute(query)
                        results = cursor.fetchall()
                        
                        if results:
                            print(f"    ✅ Found {len(results)} vinyl items in {table}")
                            for row in results:
                                vinyl_stocks.append({
                                    'database': db_name,
                                    'table': table,
                                    'data': dict(row)
                                })
                        else:
                            print(f"    ⚫ No vinyl items in {table}")
                    except Exception as e:
                        print(f"    ⚠️  Error searching {table}: {e}")
        
        conn.close()
        
        # Print detailed results for this database
        if vinyl_stocks:
            print(f"\n{'=' * 100}")
            print(f"VINYL STOCKS FOUND IN {db_name}: {len(vinyl_stocks)} items")
            print('=' * 100)
            
            for idx, item in enumerate(vinyl_stocks, 1):
                print(f"\n{idx}. TABLE: {item['table']}")
                data = item['data']
                
                # Print key fields
                key_fields = ['stock_id', 'stockid', 'id', 'materialid', 
                             'stock_type_name', 'stocktypedesc', 'description',
                             'stock_description', 'thickness', 'gsm',
                             'roll_width_mm', 'roll_length_mm', 'sheetwidth', 'sheetheight',
                             'cost_per_thousand', 'cost_per_roll', 'cost_per_sqm', 'costpersheet',
                             'markup', 'supplier_name', 'suppliername',
                             'colour', 'color', 'finish', 'material_type']
                
                for field in key_fields:
                    for key, value in data.items():
                        if key.lower() == field.lower() and value is not None:
                            print(f"   {key}: {value}")
        
        return vinyl_stocks
        
    except Exception as e:
        print(f"  ❌ Error accessing database: {e}")
        return []

def search_sql_server():
    """Search SQL Server database for vinyl stock"""
    print("\n" + "=" * 100)
    print("DATABASE: InHousePrint SQL Server")
    print("=" * 100)
    
    try:
        from db_connector import InHousePrintDB
        
        db = InHousePrintDB()
        
        # Search stock-related tables
        stock_queries = [
            # Stock table
            ("Stock", """
                SELECT TOP 100 *
                FROM Stock
                WHERE LOWER(StockTypeDesc) LIKE '%vinyl%'
                   OR LOWER(StockTypeDesc) LIKE '%monomeric%'
                   OR LOWER(StockTypeDesc) LIKE '%polymeric%'
                   OR LOWER(StockTypeDesc) LIKE '%laminate%'
                   OR LOWER(StockTypeDesc) LIKE '%adestor%'
                   OR LOWER(Colour) LIKE '%vinyl%'
                ORDER BY StockTypeDesc
            """),
            # CorfluteMaterials (might have vinyl info)
            ("CorfluteMaterials", """
                SELECT *
                FROM CorfluteMaterials
                WHERE LOWER(Colour) LIKE '%vinyl%'
            """),
            # Check for any tables with 'vinyl' in data
            ("General Search", """
                SELECT 
                    'Stock' as TableName,
                    StockID,
                    StockTypeDesc,
                    GSM,
                    Length,
                    Width,
                    Colour,
                    CostPerThousand,
                    Markup,
                    CurrentStockLevel,
                    SupplierName
                FROM Stock
                WHERE StockTypeDesc IS NOT NULL
                  AND (
                      LOWER(StockTypeDesc) LIKE '%vinyl%'
                      OR LOWER(StockTypeDesc) LIKE '%mono%'
                      OR LOWER(StockTypeDesc) LIKE '%poly%'
                      OR LOWER(StockTypeDesc) LIKE '%lamin%'
                  )
            """)
        ]
        
        all_results = []
        
        for query_name, query in stock_queries:
            print(f"\n  Executing: {query_name}")
            try:
                df = db.query(query)
                if not df.empty:
                    print(f"    ✅ Found {len(df)} rows")
                    all_results.append({
                        'query_name': query_name,
                        'results': df
                    })
                    
                    # Display results
                    print(f"\n    Results from {query_name}:")
                    for idx, row in df.iterrows():
                        print(f"\n    Row {idx + 1}:")
                        for col in df.columns:
                            if pd.notna(row[col]):
                                print(f"      {col}: {row[col]}")
                else:
                    print(f"    ⚫ No results")
            except Exception as e:
                print(f"    ⚠️  Error: {e}")
        
        db.close()
        return all_results
        
    except ImportError:
        print("  ⚠️  Could not import db_connector - SQL Server search skipped")
        print("  Install required packages: pip install pyodbc pandas")
        return []
    except Exception as e:
        print(f"  ❌ Error connecting to SQL Server: {e}")
        return []

def main():
    """Main search function"""
    print("=" * 100)
    print("VINYL STOCK SEARCH - ALL DATABASES")
    print("=" * 100)
    
    all_vinyl_stocks = []
    
    # 1. AI_agents stock.db
    db1 = search_sqlite_db(
        r'c:\Users\gpoli\GIT\AI_agents\data\stock_data.db',
        'AI_agents/data/stock_data.db'
    )
    all_vinyl_stocks.extend(db1)
    
    # 2. Quote_Calculator stock.db
    db2 = search_sqlite_db(
        r'c:\Users\gpoli\GIT\In_House_SQL\G_Folder\Quote_Calculator\stocks\stock_data.db',
        'Quote_Calculator/stocks/stock_data.db'
    )
    all_vinyl_stocks.extend(db2)
    
    # 3. Inventory stock.db
    db3 = search_sqlite_db(
        r'c:\Users\gpoli\GIT\In_House_SQL\G_Folder\Inventory\stock_data.db',
        'Inventory/stock_data.db'
    )
    all_vinyl_stocks.extend(db3)
    
    # 4. Inv-Stock stock.db
    db4 = search_sqlite_db(
        r'c:\Users\gpoli\GIT\In_House_SQL\G_Folder\Inv-Stock\stocks\stock_data.db',
        'Inv-Stock/stocks/stock_data.db'
    )
    all_vinyl_stocks.extend(db4)
    
    # 5. SQL Server
    sql_results = search_sql_server()
    
    # Final summary
    print("\n" + "=" * 100)
    print("FINAL SUMMARY - ALL DATABASES")
    print("=" * 100)
    print(f"\nTotal SQLite vinyl stocks found: {len(all_vinyl_stocks)}")
    print(f"Total SQL Server queries executed: {len(sql_results)}")
    
    # Group by material type
    print("\n" + "-" * 100)
    print("VINYL MATERIALS BY TYPE:")
    print("-" * 100)
    
    monomeric = []
    polymeric = []
    laminates = []
    other_vinyl = []
    
    for item in all_vinyl_stocks:
        data_str = str(item['data']).lower()
        if 'monomeric' in data_str or 'mono' in data_str:
            monomeric.append(item)
        elif 'polymeric' in data_str or 'poly' in data_str:
            polymeric.append(item)
        elif 'laminate' in data_str or 'lamin' in data_str:
            laminates.append(item)
        else:
            other_vinyl.append(item)
    
    print(f"\nMonomeric Vinyl: {len(monomeric)} items")
    print(f"Polymeric Vinyl: {len(polymeric)} items")
    print(f"Laminates: {len(laminates)} items")
    print(f"Other Vinyl: {len(other_vinyl)} items")
    
    # Show costs for found items
    print("\n" + "-" * 100)
    print("COST SUMMARY:")
    print("-" * 100)
    
    for item in all_vinyl_stocks[:20]:  # Show first 20
        data = item['data']
        desc = data.get('stock_description') or data.get('stock_type_name') or data.get('StockTypeDesc') or 'Unknown'
        
        # Try to find cost fields
        cost = None
        for key, value in data.items():
            if 'cost' in key.lower() and value:
                cost = f"{key}: ${value}"
                break
        
        if cost:
            print(f"  {desc[:60]:60s} | {cost}")

if __name__ == "__main__":
    main()
