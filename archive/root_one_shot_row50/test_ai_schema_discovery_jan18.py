"""
Test AI Agent Schema Discovery - Can it work around incorrect documentation?
January 18, 2026

Purpose: Simulate what an AI agent would do when encountering schema errors.
Tests if the agent can discover correct column names via INFORMATION_SCHEMA.
"""

import sys
sys.path.insert(0, 'UI/modules_external/inhouse-print')
sys.path.insert(0, 'AI_infrastructure/shared')

from db_connector import InHousePrintDB
import json

def test_ai_workaround_strategies():
    """Test if AI can discover correct schema when documentation is wrong"""
    
    db = InHousePrintDB()
    
    print("="*80)
    print("SCENARIO: AI Agent Tries to Query Orders")
    print("="*80)
    print("\n📚 Step 1: AI reads schema guide (says OrderNumber exists)")
    print("🤖 Step 2: AI writes query using OrderNumber")
    print("❌ Step 3: Query fails - Invalid column name 'OrderNumber'")
    print("🔍 Step 4: Can AI discover correct column name?\n")
    
    # Strategy 1: Query INFORMATION_SCHEMA to get actual columns
    print("-"*80)
    print("STRATEGY 1: Query INFORMATION_SCHEMA.COLUMNS")
    print("-"*80)
    
    try:
        query = """
            SELECT 
                COLUMN_NAME, 
                DATA_TYPE, 
                IS_NULLABLE,
                COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'Orders'
            ORDER BY ORDINAL_POSITION
        """
        print(f"Query:\n{query}\n")
        
        result = db.execute_query(query)
        
        if result is not None and len(result) > 0:
            print(f"✅ SUCCESS - Found {len(result)} columns in Orders table")
            print("\nActual Orders columns:")
            for idx, row in result.iterrows():
                nullable = "NULL" if row['IS_NULLABLE'] == 'YES' else "NOT NULL"
                default = f" DEFAULT {row['COLUMN_DEFAULT']}" if row['COLUMN_DEFAULT'] else ""
                print(f"  • {row['COLUMN_NAME']} ({row['DATA_TYPE']}) {nullable}{default}")
            
            # Check for commonly assumed columns
            columns = result['COLUMN_NAME'].tolist()
            
            print("\n📊 Schema Validation:")
            missing = []
            if 'OrderNumber' not in columns:
                print("  ❌ OrderNumber - NOT FOUND (guide says it exists)")
                missing.append('OrderNumber')
            if 'ColourStatus' not in columns:
                print("  ❌ ColourStatus - NOT FOUND (guide says it exists)")
                missing.append('ColourStatus')
            if 'Status' not in columns:
                print("  ✅ Status - NOT FOUND (guide correctly says it doesn't exist)")
            
            print(f"\n🎯 AI Discovery Success: Found {len(columns)} actual columns")
            print(f"⚠️  Documentation errors: {len(missing)} columns documented but don't exist")
            
            return {"success": True, "columns": columns, "missing_documented": missing}
        else:
            print("❌ FAIL - No columns returned")
            return {"success": False, "error": "No columns found"}
            
    except Exception as e:
        print(f"❌ FAIL - Error: {e}")
        return {"success": False, "error": str(e)}
    
    print("\n" + "="*80)

def test_jobtickets_schema():
    """Test JobTickets table schema discovery"""
    
    db = InHousePrintDB()
    
    print("\n" + "="*80)
    print("TESTING: JobTickets Table Schema Discovery")
    print("="*80)
    
    try:
        query = """
            SELECT 
                COLUMN_NAME, 
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'JobTickets'
            ORDER BY ORDINAL_POSITION
        """
        
        result = db.execute_query(query)
        
        if result is not None and len(result) > 0:
            print(f"✅ Found {len(result)} columns in JobTickets table\n")
            
            # Check for commonly assumed columns
            columns = result['COLUMN_NAME'].tolist()
            
            print("🔍 Critical Column Validation:")
            checks = [
                ('JobID', 'Primary key field'),
                ('DateCreated', 'Creation timestamp'),
                ('PrintType', 'Print type field'),
                ('GSMID', 'Paper weight foreign key'),
                ('BindTypeID', 'Binding type foreign key'),
                ('PaperSizeID', 'Paper size foreign key')
            ]
            
            found = []
            missing = []
            
            for col, description in checks:
                if col in columns:
                    print(f"  ✅ {col} - FOUND ({description})")
                    found.append(col)
                else:
                    print(f"  ❌ {col} - NOT FOUND ({description})")
                    missing.append(col)
            
            print(f"\n📊 Results:")
            print(f"  Found: {len(found)}/{len(checks)} expected columns")
            print(f"  Missing: {len(missing)} columns documented but don't exist")
            
            if missing:
                print(f"\n🔍 AI would need to find alternatives for: {', '.join(missing)}")
            
            # Show first 20 actual columns
            print(f"\n📋 First 20 Actual Columns:")
            for col in columns[:20]:
                print(f"  • {col}")
            
            if len(columns) > 20:
                print(f"  ... and {len(columns) - 20} more columns")
            
            return {"success": True, "total_columns": len(columns), "found": found, "missing": missing}
        else:
            print("❌ No columns found")
            return {"success": False}
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}

def test_get_all_tables():
    """Get list of all tables in database"""
    
    db = InHousePrintDB()
    
    print("\n" + "="*80)
    print("TESTING: Database Table Discovery")
    print("="*80)
    
    try:
        query = """
            SELECT 
                TABLE_NAME,
                TABLE_TYPE
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """
        
        result = db.execute_query(query)
        
        if result is not None and len(result) > 0:
            tables = result['TABLE_NAME'].tolist()
            print(f"✅ Found {len(tables)} tables in database\n")
            
            # Check for commonly referenced tables
            print("🔍 Critical Table Validation:")
            expected_tables = [
                'Orders', 'JobTickets', 'Clients', 
                'BusinessTable',  # We know this doesn't exist
                'PaperSize', 'JobType', 'GSM', 'BindType'
            ]
            
            for table in expected_tables:
                if table in tables:
                    print(f"  ✅ {table} - EXISTS")
                else:
                    print(f"  ❌ {table} - NOT FOUND")
            
            print(f"\n📋 All Tables ({len(tables)}):")
            for table in tables:
                print(f"  • {table}")
            
            return {"success": True, "tables": tables}
        else:
            print("❌ No tables found")
            return {"success": False}
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}

def test_ai_adaptive_query():
    """Test if AI can write a working query after discovering schema"""
    
    db = InHousePrintDB()
    
    print("\n" + "="*80)
    print("SCENARIO: AI Adapts After Schema Discovery")
    print("="*80)
    
    # First, discover what columns actually exist
    print("\n🔍 Step 1: Discovering actual Orders columns...")
    try:
        schema_query = """
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'Orders'
        """
        schema_result = db.execute_query(schema_query)
        
        if schema_result is None or len(schema_result) == 0:
            print("❌ Failed to get schema")
            return {"success": False}
        
        columns = schema_result['COLUMN_NAME'].tolist()
        print(f"✅ Found {len(columns)} columns")
        
        # Build a safe query using only columns we KNOW exist
        safe_columns = [c for c in ['OrderID', 'OrderDate', 'CustomerMYOB_ID', 'Invoiced'] if c in columns]
        
        if len(safe_columns) == 0:
            print("❌ None of the basic columns exist!")
            return {"success": False}
        
        print(f"\n🤖 Step 2: Building query with confirmed columns: {', '.join(safe_columns)}")
        
        # Try a safe query
        safe_query = f"""
            SELECT TOP 5 {', '.join(safe_columns)}
            FROM Orders
            ORDER BY OrderDate DESC
        """
        
        print(f"\nQuery:\n{safe_query}\n")
        
        result = db.execute_query(safe_query)
        
        if result is not None and len(result) > 0:
            print(f"✅ SUCCESS - AI adapted and query returned {len(result)} rows")
            print(f"\nSample data:")
            print(result.head(3).to_string())
            
            return {"success": True, "strategy": "adaptive", "rows": len(result)}
        else:
            print("❌ Query returned no data")
            return {"success": False}
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("\n" + "="*80)
    print("AI AGENT SCHEMA DISCOVERY TEST")
    print("Testing if AI can work around incorrect documentation")
    print("="*80)
    
    # Test 1: Can AI discover actual Orders schema?
    orders_result = test_ai_workaround_strategies()
    
    # Test 2: Can AI discover JobTickets schema?
    jobtickets_result = test_jobtickets_schema()
    
    # Test 3: Can AI discover all tables?
    tables_result = test_get_all_tables()
    
    # Test 4: Can AI write working queries after discovery?
    adaptive_result = test_ai_adaptive_query()
    
    # Summary
    print("\n" + "="*80)
    print("FINAL ASSESSMENT: Can AI Work Around Bad Documentation?")
    print("="*80)
    
    if all([
        orders_result.get('success'),
        jobtickets_result.get('success'),
        tables_result.get('success'),
        adaptive_result.get('success')
    ]):
        print("\n✅ YES - AI CAN WORK AROUND IT!")
        print("\n🎯 AI Strategy:")
        print("  1. Read schema guide (even if wrong)")
        print("  2. Try query based on guide")
        print("  3. When it fails, query INFORMATION_SCHEMA")
        print("  4. Discover actual columns")
        print("  5. Rebuild query with correct columns")
        print("  6. Success!")
        
        print("\n⚠️  BUT:")
        print("  • Requires 2-3x more queries (discovery + actual)")
        print("  • Slower response time")
        print("  • Uses more tokens")
        print("  • Still needs schema guide for context")
        
        print("\n💡 RECOMMENDATION:")
        print("  Fix the schema documentation for best performance!")
    else:
        print("\n❌ NO - AI CANNOT RELIABLY WORK AROUND IT")
        print("\nFailed components:")
        if not orders_result.get('success'):
            print("  ❌ Orders schema discovery failed")
        if not jobtickets_result.get('success'):
            print("  ❌ JobTickets schema discovery failed")
        if not tables_result.get('success'):
            print("  ❌ Table discovery failed")
        if not adaptive_result.get('success'):
            print("  ❌ Adaptive query generation failed")
        
        print("\n🚨 CRITICAL: Schema documentation MUST be fixed!")
    
    print("\n" + "="*80)
