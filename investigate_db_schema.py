"""
Investigate SQL Schema Issues
Examines both SQLite (stock_data.db) and SQL Server (InHousePrintDB) schemas
"""

import sqlite3
import json
from pathlib import Path

print("=" * 80)
print("DATABASE SCHEMA INVESTIGATION")
print("=" * 80)

# ============================================================================
# Part 1: SQLite stock_data.db Schema
# ============================================================================

print("\n[PART 1] SQLite Database: data/stock_data.db")
print("-" * 80)

sqlite_path = Path(__file__).parent / "data" / "stock_data.db"

if not sqlite_path.exists():
    print(f"[ERROR] SQLite database not found: {sqlite_path}")
else:
    print(f"[OK] Database found: {sqlite_path}")
    
    try:
        conn = sqlite3.connect(str(sqlite_path))
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n[TABLES] Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Get schema for each table
        print("\n[SCHEMAS] Detailed table structures:")
        for table in tables:
            table_name = table[0]
            print(f"\n  Table: {table_name}")
            print("  " + "-" * 70)
            
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                pk_marker = " [PRIMARY KEY]" if pk else ""
                null_marker = " NOT NULL" if not_null else ""
                default_marker = f" DEFAULT {default_val}" if default_val else ""
                print(f"    {col_name:<30} {col_type:<15}{null_marker}{default_marker}{pk_marker}")
        
        # Check for specific issues from test failures
        print("\n[ISSUE CHECK] Test 7 Error - 'no such column: ra.IsResolved'")
        print("  Checking ReorderAlerts table for IsResolved column...")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%alert%' OR name LIKE '%reorder%'")
        alert_tables = cursor.fetchall()
        
        if alert_tables:
            for table in alert_tables:
                table_name = table[0]
                print(f"\n  Found table: {table_name}")
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                col_names = [col[1] for col in columns]
                print(f"  Columns: {', '.join(col_names)}")
                
                if 'IsResolved' in col_names:
                    print("  [OK] IsResolved column exists")
                else:
                    print("  [MISSING] IsResolved column NOT found")
        else:
            print("  [WARNING] No alert/reorder tables found")
        
        conn.close()
        print("\n[OK] SQLite examination complete")
        
    except Exception as e:
        print(f"[ERROR] SQLite examination failed: {e}")

# ============================================================================
# Part 2: SQL Server Database Configuration
# ============================================================================

print("\n\n[PART 2] SQL Server Database: InHousePrintDB (Remote)")
print("-" * 80)

config_path = Path(__file__).parent / "config" / "database-config.json"

if not config_path.exists():
    print(f"[ERROR] Config not found: {config_path}")
else:
    print(f"[OK] Config found: {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("\n[CONNECTION INFO]")
        print(f"  Server: {config.get('server', 'NOT SET')}")
        print(f"  Database: {config.get('database', 'NOT SET')}")
        print(f"  Driver: {config.get('driver', 'NOT SET')}")
        print(f"  UID: {config.get('uid', 'NOT SET')}")
        print(f"  PWD: {'*' * len(config.get('pwd', '')) if config.get('pwd') else 'NOT SET'}")
        
        # Try to import pyodbc and test connection
        print("\n[CONNECTION TEST]")
        try:
            import pyodbc
            print("  [OK] pyodbc module available")
            
            conn_str = f"DRIVER={{{config['driver']}}};SERVER={config['server']};DATABASE={config['database']};UID={config['uid']};PWD={config['pwd']}"
            
            print("  Attempting connection...")
            conn = pyodbc.connect(conn_str, timeout=5)
            cursor = conn.cursor()
            
            print("  [OK] Connection successful!")
            
            # Get database name
            cursor.execute("SELECT DB_NAME()")
            db_name = cursor.fetchone()[0]
            print(f"  Connected to database: {db_name}")
            
            # Get table list
            cursor.execute("""
                SELECT TABLE_SCHEMA, TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_SCHEMA, TABLE_NAME
            """)
            tables = cursor.fetchall()
            
            print(f"\n[TABLES] Found {len(tables)} tables:")
            for schema, table_name in tables[:20]:  # Show first 20
                print(f"  - {schema}.{table_name}")
            
            if len(tables) > 20:
                print(f"  ... and {len(tables) - 20} more tables")
            
            # Check for specific tables mentioned in test errors
            print("\n[ISSUE CHECK] Test 3 Error - 'Invalid object name Ticket'")
            cursor.execute("""
                SELECT TABLE_SCHEMA, TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'Ticket'
            """)
            ticket_tables = cursor.fetchall()
            
            if ticket_tables:
                for schema, table_name in ticket_tables:
                    print(f"  [FOUND] {schema}.{table_name}")
                    print(f"  [FIX] Use qualified name: {schema}.{table_name} instead of just 'Ticket'")
                    
                    # Get columns
                    cursor.execute(f"""
                        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table_name}'
                        ORDER BY ORDINAL_POSITION
                    """)
                    columns = cursor.fetchall()
                    print(f"  Columns ({len(columns)}):")
                    for col_name, data_type, nullable in columns[:10]:
                        print(f"    - {col_name} ({data_type}) {'NULL' if nullable == 'YES' else 'NOT NULL'}")
                    if len(columns) > 10:
                        print(f"    ... and {len(columns) - 10} more columns")
            else:
                print("  [ERROR] Ticket table NOT found in any schema")
                print("  [SEARCH] Looking for similar table names...")
                cursor.execute("""
                    SELECT TABLE_SCHEMA, TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME LIKE '%Ticket%'
                """)
                similar = cursor.fetchall()
                if similar:
                    for schema, table_name in similar:
                        print(f"    Found: {schema}.{table_name}")
            
            # Check other important tables mentioned in Viki prompt
            print("\n[SCHEMA VERIFICATION] Checking tables from Viki prompt:")
            important_tables = ['PaperSize', 'BindType', 'TicketNotes']
            
            for table in important_tables:
                cursor.execute(f"""
                    SELECT TABLE_SCHEMA, TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = '{table}'
                """)
                results = cursor.fetchall()
                
                if results:
                    for schema, table_name in results:
                        print(f"\n  Table: {schema}.{table_name}")
                        cursor.execute(f"""
                            SELECT COLUMN_NAME, DATA_TYPE
                            FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table_name}'
                            ORDER BY ORDINAL_POSITION
                        """)
                        columns = cursor.fetchall()
                        col_names = [f"{col[0]} ({col[1]})" for col in columns]
                        print(f"    Columns: {', '.join(col_names)}")
                        
                        # Specific checks from Viki prompt
                        col_name_list = [col[0] for col in columns]
                        if table == 'PaperSize':
                            has_width = 'Width' in col_name_list
                            has_height = 'Height' in col_name_list
                            print(f"    Viki Warning: 'PaperSize has NO Width/Height columns'")
                            print(f"    Actual: Width={'FOUND' if has_width else 'MISSING'}, Height={'FOUND' if has_height else 'MISSING'}")
                        elif table == 'BindType':
                            has_bindname = 'BindName' in col_name_list
                            has_binddesc = 'BindTypeDesc' in col_name_list
                            print(f"    Viki Warning: 'BindType uses BindTypeDesc NOT BindName'")
                            print(f"    Actual: BindName={'FOUND' if has_bindname else 'MISSING'}, BindTypeDesc={'FOUND' if has_binddesc else 'MISSING'}")
                else:
                    print(f"\n  Table: {table} - NOT FOUND")
            
            conn.close()
            print("\n[OK] SQL Server examination complete")
            
        except ImportError:
            print("  [ERROR] pyodbc not installed - cannot test SQL Server connection")
        except pyodbc.Error as e:
            print(f"  [ERROR] Connection failed: {e}")
        except Exception as e:
            print(f"  [ERROR] Unexpected error: {e}")
        
    except Exception as e:
        print(f"[ERROR] Config reading failed: {e}")

# ============================================================================
# Part 3: Test Failure Analysis
# ============================================================================

print("\n\n[PART 3] Test Failure Analysis")
print("-" * 80)

print("\n[TEST 3 FAILURE] SQL Execution - 'Invalid object name Ticket'")
print("  Issue: SQL Server requires schema-qualified table names")
print("  Current: SELECT TOP 5 JobNumber, CustomerName FROM Ticket")
print("  Fix: SELECT TOP 5 JobNumber, CustomerName FROM dbo.Ticket")
print("  Location: Backend SQL generation in tool_use_agent.py")

print("\n[TEST 4 FAILURE] Calculator Requirements - Returns 0 parameters")
print("  Issue: Backend may not implement _get_calculator_requirements")
print("  Location: tool_use_agent.py needs calculator requirements method")
print("  Impact: AI cannot learn parameter options dynamically")

print("\n[TEST 5 FAILURE] Quote Calculation - Structure mismatch")
print("  Issue: Backend returns 'summary' field, test expects 'pricing.total'")
print("  Current structure: {'summary': 'Quote calculated: $89.54 for ...'}")
print("  Expected structure: {'pricing': {'total': 89.54}}")
print("  Location: Backend calculator return format")

print("\n[TEST 7 FAILURE] Reorder Alerts - 'no such column: ra.IsResolved'")
print("  Issue: SQLite query uses column that doesn't exist in schema")
print("  Location: Backend stock_database_tools.py reorder alerts query")
print("  Fix: Either add IsResolved column or remove from query")

print("\n" + "=" * 80)
print("INVESTIGATION COMPLETE")
print("=" * 80)
