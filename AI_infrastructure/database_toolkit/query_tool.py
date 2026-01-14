"""
Query Tool
==========

Interactive SQL query interface for the database.
"""

import csv
from typing import List, Optional, Tuple
from datetime import datetime


class QueryTool:
    """Interactive SQL query tool"""
    
    def __init__(self, db_path: str = "ai_infrastructure.db"):
        """Initialize query tool"""
        self.db_path = db_path
    
    def get_connection(self) -> psycopg2.connection:
        """Get database connection"""
        conn = psycopg2.connect(self.db_path)
        conn.row_factory = psycopg2.extras.RealDictRow
        return conn
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[dict]:
        """
        Execute SQL query and return results
        
        Args:
            query: SQL query string
            params: Optional query parameters
        
        Returns:
            List of result dicts
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Fetch results
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            
            conn.close()
            return results
        
        except Exception as e:
            conn.close()
            raise Exception(f"Query error: {e}")
    
    def export_to_csv(self, query: str, output_file: str) -> int:
        """
        Execute query and export results to CSV
        
        Args:
            query: SQL query
            output_file: Output CSV file path
        
        Returns:
            Number of rows exported
        """
        results = self.execute_query(query)
        
        if not results:
            return 0
        
        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        
        return len(results)
    
    def format_results(self, results: List[dict], max_rows: int = 50) -> str:
        """Format query results as table"""
        if not results:
            return "No results"
        
        # Limit rows
        display_results = results[:max_rows]
        truncated = len(results) > max_rows
        
        # Get column names
        columns = list(display_results[0].keys())
        
        # Calculate column widths
        widths = {col: len(col) for col in columns}
        for row in display_results:
            for col in columns:
                val_len = len(str(row[col]))
                if val_len > widths[col]:
                    widths[col] = min(val_len, 50)  # Max 50 chars per column
        
        # Build table
        output = []
        
        # Header
        header = " | ".join(col.ljust(widths[col]) for col in columns)
        separator = "-+-".join("-" * widths[col] for col in columns)
        
        output.append(header)
        output.append(separator)
        
        # Rows
        for row in display_results:
            row_str = " | ".join(
                str(row[col])[:widths[col]].ljust(widths[col]) 
                for col in columns
            )
            output.append(row_str)
        
        if truncated:
            output.append(f"\n... {len(results) - max_rows} more rows")
        
        return "\n".join(output)


if __name__ == "__main__":
    # Test query tool
    tool = QueryTool()
    results = tool.execute_query("SELECT * FROM users LIMIT 5")
    print(tool.format_results(results))

