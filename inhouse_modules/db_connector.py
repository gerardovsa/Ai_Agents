#!/usr/bin/env python3
"""
InHousePrint Database Connection Tool
====================================

A Python utility for connecting to and querying the InHousePrint SQL Server database.
Provides both programmatic access and interactive query capabilities.

Requirements:
    pip install pyodbc pandas streamlit plotly

Usage:
    python db_connector.py --interactive
    python db_connector.py --query "SELECT * FROM Orders LIMIT 10"
"""

import pyodbc
import pandas as pd
import json
import argparse
import sys
import warnings
from datetime import datetime
from typing import Optional, Dict, List, Any

# Suppress pandas SQLAlchemy warnings
warnings.filterwarnings('ignore', message='pandas only supports SQLAlchemy connectable')

class InHousePrintDB:
    """Database connection and query utility for InHousePrint system."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize database connection with configuration.
        
        Priority order:
        1. Try Supabase credentials (for Render deployment)
        2. Fall back to config_path (for local development)
        """
        import os
        
        # Try Supabase credentials first (Render deployment)
        self.config = None
        try:
            # Check if we should use Supabase
            if os.environ.get('SUPABASE_DB_URL_POOLER'):
                print("🔧 Render deployment mode - using Supabase credentials")
                from AI_infrastructure.auth.supabase_credentials import get_database_config
                self.config = get_database_config()
                print("✅ Credentials loaded from Supabase")
        except Exception as e:
            print(f"⚠️  Supabase credentials not available: {e}")
        
        # Fall back to config file if Supabase not available
        if self.config is None:
            if config_path is None:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                config_path = os.path.join(current_dir, "..", "..", "config", "database-config.json")
            self.config = self._load_config(config_path)
        
        self.connection = None
        self.connect()
    
    def _load_config(self, config_path: str) -> dict:
        """Load database configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Configuration file not found: {config_path}")
            raise FileNotFoundError(f"Database config not found: {config_path}")
        except json.JSONDecodeError:
            print(f"⚠️  Invalid JSON in configuration file: {config_path}")
            raise ValueError(f"Invalid database config: {config_path}")
    
    def connect(self) -> bool:
        """Establish connection to SQL Server database."""
        try:
            conn_str = self.config['DatabaseConnections']['Primary']['ConnectionString']
            
            # Convert connection string format for pyodbc
            # Format: data source=server,port;user id=user;password=pass;database=db
            parts = conn_str.split(';')
            server = None
            uid = None
            pwd = None
            database = None
            
            for part in parts:
                if 'data source=' in part.lower():
                    server = part.split('=')[1]
                elif 'user id=' in part.lower():
                    uid = part.split('=')[1]
                elif 'password=' in part.lower():
                    pwd = part.split('=')[1]
                elif 'database=' in part.lower():
                    database = part.split('=')[1]
            
            # Try multiple ODBC drivers in order of preference
            drivers = [
                "ODBC Driver 18 for SQL Server",
                "ODBC Driver 17 for SQL Server", 
                "ODBC Driver 13 for SQL Server",
                "SQL Server Native Client 11.0",
                "SQL Server"
            ]
            
            connection_successful = False
            for driver in drivers:
                try:
                    # Build pyodbc connection string with timeouts
                    pyodbc_conn_str = (
                        f"DRIVER={{{driver}}};"
                        f"SERVER={server};"
                        f"DATABASE={database};"
                        f"UID={uid};"
                        f"PWD={pwd};"
                        f"TrustServerCertificate=yes;"
                        f"Encrypt=no;"
                        f"Connection Timeout=3;"  # 3 second connection timeout
                        f"Login Timeout=3;"       # 3 second login timeout
                    )
                    
                    self.connection = pyodbc.connect(pyodbc_conn_str, timeout=3)
                    print(f" Connected to database: {database} using {driver}")
                    connection_successful = True
                    break
                    
                except pyodbc.Error as driver_error:
                    continue  # Try next driver
            
            if not connection_successful:
                raise Exception("No compatible ODBC driver found. Please install Microsoft ODBC Driver for SQL Server.")
                
            return True
            
        except Exception as e:
            print(f"⚠️  Failed to connect to database: {str(e)}")
            print("💡 Troubleshooting:")
            print("   1. Install Microsoft ODBC Driver 17 or 18 for SQL Server")
            print("   2. Check if SQL Server is running and accessible")
            print("   3. Verify connection details in config file")
            # Don't exit - raise exception so caller can handle it
            raise ConnectionError(f"Database connection failed: {str(e)}")
    
    def execute_query(self, query: str, params: tuple = None) -> pd.DataFrame:
        """
        Execute SQL query and return results as pandas DataFrame.
        
        Args:
            query: SQL query string (can contain ? placeholders)
            params: Optional tuple of parameters for parameterized queries
            
        Returns:
            pandas DataFrame with query results
        """
        if not self.connection:
            raise Exception("No database connection available")
        
        try:
            if params:
                # Use parameterized query
                return pd.read_sql(query, self.connection, params=params)
            else:
                # Regular query
                return pd.read_sql(query, self.connection)
        except Exception as e:
            print(f" Query execution failed: {str(e)}")
            raise
    
    def get_table_info(self, table_name: Optional[str] = None) -> pd.DataFrame:
        """Get information about tables in the database."""
        if table_name:
            query = """
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
            """
            return pd.read_sql(query, self.connection, params=[table_name])
        else:
            query = """
            SELECT 
                TABLE_NAME,
                TABLE_TYPE
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'dbo'
            ORDER BY TABLE_NAME
            """
            return self.execute_query(query)
    
    def get_business_summary(self) -> Dict[str, Any]:
        """Get high-level business metrics."""
        queries = {
            'total_orders': "SELECT COUNT(*) as count FROM Orders",  # Corrected table name
            'active_orders': "SELECT COUNT(*) as count FROM Orders WHERE Invoiced = 0",
            'total_clients': "SELECT COUNT(*) as count FROM Clients",  # Corrected table name
            'job_tickets_today': """
                SELECT COUNT(*) as count 
                FROM JobTickets jt
                INNER JOIN Orders o ON jt.OrderID = o.OrderID
                WHERE CAST(o.OrderDate as DATE) = CAST(GETDATE() as DATE)
            """,
            'publishing_projects': "SELECT COUNT(*) as count FROM PublishingProject WHERE Invoiced = 0"
        }
        
        results = {}
        for key, query in queries.items():
            try:
                df = self.execute_query(query)
                results[key] = df.iloc[0]['count'] if not df.empty else 0
            except Exception as e:
                results[key] = f"Error: {str(e)}"
        
        return results
    
    def get_recent_orders(self, limit: int = 10) -> pd.DataFrame:
        """Get most recent orders."""
        query = f"""
        SELECT TOP {limit}
            o.OrderID,
            o.ClientName,
            o.OrderDate,
            o.DateRequired,
            
            b.BusinessName
        FROM Orders o
        LEFT JOIN Business b ON o.InvoicingBusinessID = b.BusinessID
        ORDER BY o.OrderDate DESC
        """
        return self.execute_query(query)
    
    def get_workboard_status(self) -> pd.DataFrame:
        """Get current workboard status across all stages."""
        query = """
        SELECT 
            js.[Desc] as Stage,
            COUNT(jt.TicketID) as JobCount,
            SUM(jt.Cost) as TotalValue
        FROM JobTickets jt
        INNER JOIN JobStage js ON jt.StageID = js.StageID
        LEFT JOIN JobTickets jt ON o.OrderID = jt.OrderID
        WHERE jt.InternalInvoiceComplete = 0
        GROUP BY js.[Desc], js.StageID
        ORDER BY js.StageID
        """
        return self.execute_query(query)
    
    def search_clients(self, search_term: str) -> pd.DataFrame:
        """Search for clients by name."""
        query = """
        SELECT 
            ContactID,
            Name,
            AddressCity,
            Phone,
            b.BusinessName
        FROM Clients c
        LEFT JOIN Business b ON c.BusinessID = b.BusinessID
        WHERE Name LIKE ?
        ORDER BY Name
        """
        return pd.read_sql(query, self.connection, params=[f'%{search_term}%'])
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

def interactive_mode(db: InHousePrintDB):
    """Interactive command-line interface for database queries."""
    print("\n🔧 InHousePrint Database Interactive Mode")
    print("=" * 50)
    print("Commands:")
    print("  tables          - List all tables")
    print("  describe <table> - Describe table structure")
    print("  summary         - Business summary")
    print("  recent          - Recent orders")
    print("  workboard       - Workboard status")
    print("  search <name>   - Search clients")
    print("  query <SQL>     - Execute custom SQL")
    print("  quit            - Exit")
    print("=" * 50)
    
    while True:
        try:
            command = input("\n📊 db> ").strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                break
            elif command.lower() == 'tables':
                print(db.get_table_info())
            elif command.lower().startswith('describe '):
                table_name = command.split(' ', 1)[1]
                print(db.get_table_info(table_name))
            elif command.lower() == 'summary':
                summary = db.get_business_summary()
                for key, value in summary.items():
                    print(f"{key.replace('_', ' ').title()}: {value}")
            elif command.lower() == 'recent':
                print(db.get_recent_orders())
            elif command.lower() == 'workboard':
                print(db.get_workboard_status())
            elif command.lower().startswith('search '):
                search_term = command.split(' ', 1)[1]
                print(db.search_clients(search_term))
            elif command.lower().startswith('query '):
                sql = command.split(' ', 1)[1]
                print(db.execute_query(sql))
            else:
                print("Unknown command. Type 'quit' to exit.")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f" Error: {str(e)}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="InHousePrint Database Tool")
    parser.add_argument('--interactive', action='store_true', help='Start interactive mode')
    parser.add_argument('--query', type=str, help='Execute a single query')
    parser.add_argument('--summary', action='store_true', help='Show business summary')
    parser.add_argument('--config', type=str, default='config/database-config.json', help='Configuration file path')
    
    args = parser.parse_args()
    
    # Initialize database connection
    db = InHousePrintDB(args.config)
    
    try:
        if args.interactive:
            interactive_mode(db)
        elif args.query:
            result = db.execute_query(args.query)
            print(result)
        elif args.summary:
            summary = db.get_business_summary()
            print("\n📊 Business Summary:")
            print("=" * 30)
            for key, value in summary.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
        else:
            print("No action specified. Use --help for options.")
    
    finally:
        db.close()

if __name__ == "__main__":
    main()
