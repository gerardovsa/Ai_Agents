"""
Calculator Pricing Database Connector
=====================================

Supabase PostgreSQL connector for the 8-table Calculator Pricing Database.
Separate from InHousePrintDB (SQL Server for orders/production).

Database: ai-agents-production-inhouse (Supabase PostgreSQL)
Host: aws-1-ap-southeast-2.pooler.supabase.com:6543

Tables:
    Pricing Constants System (4 tables):
    - calculator_pricing_parameters (64 rows) - Parameter definitions
    - calculator_parameter_overrides (104 rows) - Calculator-specific values
    - calculator_parameter_history - Audit trail
    - calculators_registry (30 rows) - Calculator metadata
    
    Product Options System (4 tables):
    - product_options (154 rows) - Option definitions
    - product_option_choices (432 rows) - Choices with prices
    - product_option_overrides - Price overrides (customer/time-based)
    - product_option_history - Audit trail

Usage:
    from calculator_pricing_db import CalculatorPricingDB
    
    db = CalculatorPricingDB()
    result = db.execute_query("SELECT * FROM calculator_pricing_parameters LIMIT 10")
    df = result['data']

FILE: UI/modules_external/quote-calculator/backend/calculator_pricing_db.py
PURPOSE: Supabase PostgreSQL connector for calculator pricing database
CREATED: December 17, 2025
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime


class CalculatorPricingDB:
    """
    Database connection utility for Calculator Pricing Database (Supabase PostgreSQL)
    
    Provides safe query execution with automatic connection management.
    Separate from InHousePrintDB (SQL Server for orders).
    """
    
    def __init__(self):
        """
        Initialize database connection to Supabase Calculator Pricing DB
        
        Connection Priority:
        1. Environment variable: SUPABASE_DB_URL_POOLER (Render deployment)
        2. Environment variable: SUPABASE_DB_URL (local development)
        3. Raises error if neither found
        """
        self.connection_url = os.environ.get('SUPABASE_DB_URL_POOLER') or os.environ.get('SUPABASE_DB_URL')
        
        if not self.connection_url:
            raise ValueError(
                "❌ SUPABASE_DB_URL_POOLER or SUPABASE_DB_URL environment variable required!\n"
                "   This connector requires Supabase PostgreSQL connection string.\n"
                "   Example: postgresql://postgres.xxx:password@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"
            )
        
        self.connection = None
        self._connect()
    
    def _connect(self) -> bool:
        """
        Establish connection to Supabase PostgreSQL
        
        Returns:
            True if successful, raises exception on failure
        """
        try:
            self.connection = psycopg2.connect(
                self.connection_url,
                cursor_factory=RealDictCursor,
                connect_timeout=10
            )
            
            # Test connection with simple query
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            
            print("✅ [Calculator Pricing DB] Connected to Supabase PostgreSQL")
            return True
            
        except psycopg2.OperationalError as e:
            raise ConnectionError(
                f"❌ Failed to connect to Calculator Pricing Database:\n"
                f"   {str(e)}\n"
                f"   Check SUPABASE_DB_URL_POOLER environment variable"
            )
        except Exception as e:
            raise RuntimeError(f"❌ Unexpected error connecting to database: {str(e)}")
    
    def _ensure_connection(self):
        """Ensure database connection is alive, reconnect if needed"""
        try:
            if self.connection is None or self.connection.closed:
                print("⚠️  Connection lost, reconnecting...")
                self._connect()
            else:
                # Test connection
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
        except Exception:
            print("⚠️  Connection test failed, reconnecting...")
            self._connect()
    
    def execute_query(self, sql: str, params: Optional[tuple] = None, return_dataframe: bool = True) -> Dict[str, Any]:
        """
        Execute SELECT query (read-only)
        
        Args:
            sql: SQL query string (must be SELECT)
            params: Query parameters for safe parameterization (optional)
            return_dataframe: If True, return pandas DataFrame; if False, return list of dicts
        
        Returns:
            {
                "success": True,
                "data": pd.DataFrame or List[Dict],
                "row_count": int,
                "query": str,
                "execution_time_ms": float
            }
        
        Raises:
            ValueError: If query is not SELECT
            psycopg2.Error: On database errors
        """
        # Safety check: Only allow SELECT queries
        sql_upper = sql.strip().upper()
        if not sql_upper.startswith('SELECT') and not sql_upper.startswith('WITH'):
            raise ValueError(
                "❌ Only SELECT queries allowed in execute_query()!\n"
                "   Use execute_modify() for INSERT/UPDATE/DELETE operations."
            )
        
        self._ensure_connection()
        
        start_time = datetime.now()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            cursor.close()
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Convert to DataFrame or list of dicts
            if return_dataframe:
                data = pd.DataFrame([dict(row) for row in rows]) if rows else pd.DataFrame()
            else:
                data = [dict(row) for row in rows]
            
            return {
                "success": True,
                "data": data,
                "row_count": len(rows),
                "query": sql,
                "execution_time_ms": round(execution_time, 2)
            }
            
        except psycopg2.Error as e:
            self.connection.rollback()
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "query": sql,
                "params": params
            }
        except Exception as e:
            self.connection.rollback()
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_type": type(e).__name__,
                "query": sql
            }
    
    def execute_modify(self, sql: str, params: Optional[tuple] = None, auto_commit: bool = True) -> Dict[str, Any]:
        """
        Execute INSERT/UPDATE/DELETE query (write operations)
        
        Args:
            sql: SQL query string (INSERT/UPDATE/DELETE)
            params: Query parameters for safe parameterization (optional)
            auto_commit: If True, auto-commit; if False, caller must commit
        
        Returns:
            {
                "success": True,
                "rows_affected": int,
                "query": str,
                "execution_time_ms": float
            }
        
        Raises:
            ValueError: If query is SELECT (use execute_query instead)
            psycopg2.Error: On database errors
        """
        # Safety check: Block SELECT queries
        sql_upper = sql.strip().upper()
        if sql_upper.startswith('SELECT'):
            raise ValueError(
                "❌ SELECT queries not allowed in execute_modify()!\n"
                "   Use execute_query() for read operations."
            )
        
        # Warning for dangerous operations
        if any(keyword in sql_upper for keyword in ['DROP TABLE', 'TRUNCATE', 'DROP DATABASE']):
            return {
                "success": False,
                "error": "❌ DANGEROUS OPERATION BLOCKED: DROP/TRUNCATE not allowed via this method",
                "query": sql
            }
        
        self._ensure_connection()
        
        start_time = datetime.now()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, params)
            rows_affected = cursor.rowcount
            cursor.close()
            
            if auto_commit:
                self.connection.commit()
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "success": True,
                "rows_affected": rows_affected,
                "query": sql,
                "execution_time_ms": round(execution_time, 2),
                "committed": auto_commit
            }
            
        except psycopg2.Error as e:
            self.connection.rollback()
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "query": sql,
                "params": params
            }
        except Exception as e:
            self.connection.rollback()
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_type": type(e).__name__,
                "query": sql
            }
    
    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get complete schema information for all 8 calculator pricing tables
        
        Returns:
            {
                "success": True,
                "tables": {
                    "calculator_pricing_parameters": {
                        "row_count": 64,
                        "columns": [{"name": "id", "type": "integer", ...}, ...]
                    },
                    ...
                },
                "relationships": [...],
                "indexes": [...]
            }
        """
        tables = [
            'calculator_pricing_parameters',
            'calculator_parameter_overrides',
            'calculator_parameter_history',
            'calculators_registry',
            'product_options',
            'product_option_choices',
            'product_option_overrides',
            'product_option_history'
        ]
        
        schema_info = {"success": True, "tables": {}}
        
        try:
            for table in tables:
                # Get row count
                count_result = self.execute_query(f"SELECT COUNT(*) as count FROM {table}", return_dataframe=False)
                row_count = count_result['data'][0]['count'] if count_result['success'] else 0
                
                # Get column information
                columns_result = self.execute_query(f"""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position
                """, return_dataframe=False)
                
                schema_info['tables'][table] = {
                    "row_count": row_count,
                    "columns": columns_result['data'] if columns_result['success'] else []
                }
            
            return schema_info
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to retrieve schema info: {str(e)}"
            }
    
    def close(self):
        """Close database connection"""
        if self.connection and not self.connection.closed:
            self.connection.close()
            print("✅ [Calculator Pricing DB] Connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# ==================== USAGE EXAMPLES ====================

if __name__ == "__main__":
    print("="*70)
    print("CALCULATOR PRICING DATABASE CONNECTOR TEST")
    print("="*70)
    
    try:
        # Initialize connection
        db = CalculatorPricingDB()
        
        # Test 1: Query pricing parameters
        print("\n📋 Test 1: Query Pricing Parameters")
        result = db.execute_query("""
            SELECT 
                parameter_name,
                data_type,
                base_value,
                (value_statistics->>'variance_pct')::numeric as variance_pct
            FROM calculator_pricing_parameters
            WHERE (value_statistics->>'variance_pct')::numeric > 100
            ORDER BY variance_pct DESC
            LIMIT 5
        """)
        
        if result['success']:
            print(f"✅ Found {result['row_count']} high variance parameters")
            print(result['data'])
        else:
            print(f"❌ Query failed: {result['error']}")
        
        # Test 2: Get schema info
        print("\n📊 Test 2: Get Schema Information")
        schema = db.get_schema_info()
        
        if schema['success']:
            print("✅ Schema retrieved for all tables:")
            for table_name, info in schema['tables'].items():
                print(f"   {table_name}: {info['row_count']} rows, {len(info['columns'])} columns")
        else:
            print(f"❌ Schema retrieval failed: {schema['error']}")
        
        # Test 3: Query product options
        print("\n🛍️  Test 3: Query Product Options")
        result = db.execute_query("""
            SELECT 
                calculator_name,
                COUNT(*) as option_count
            FROM product_options
            GROUP BY calculator_name
            ORDER BY option_count DESC
            LIMIT 5
        """)
        
        if result['success']:
            print(f"✅ Found {result['row_count']} calculators with product options")
            print(result['data'])
        
        # Close connection
        db.close()
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
