"""
Stock Database Tools - Read/Write operations for AI agents
===========================================================
from shared.database_utils import convert_sql_placeholders

Provides tool functions for AI agents to interact with stock databases:
- Read operations: Query stock levels, schemas, transactions
- Write operations: Update stock levels, add transactions, create alerts
- Temp SQLite database: Full inventory management (20 columns)
- Production SQL Server: Pricing data only (7 columns)
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys
import os

# Import db_connector from same directory (inhouse_modules)
try:
    from db_connector import InHousePrintDB
except ImportError:
    from .db_connector import InHousePrintDB


class StockDatabaseTools:
    """Tools for AI agents to interact with stock databases."""
    
    def __init__(self, temp_db_path: Optional[str] = None, prod_config_path: Optional[str] = None):
        """
        Initialize stock database tools.
        
        Args:
            temp_db_path: Path to temp SQLite database (default: AI_agents/data/stock_data.db)
            prod_config_path: Path to production config (default: AI_agents/config/database-config.json)
        """
        current_dir = Path(__file__).resolve().parent
        root_dir = current_dir.parent  # AI_agents root
        
        # Setup temp database path
        if temp_db_path:
            self.temp_db_path = Path(temp_db_path)
        else:
            self.temp_db_path = root_dir / "data" / "stock_data.db"
        
        # Setup production config path
        if prod_config_path:
            self.prod_config_path = Path(prod_config_path)
        else:
            self.prod_config_path = root_dir / "config" / "database-config.json"
        
        self.prod_db = None
    
    def _connect_temp(self) -> sqlite3.Connection:
        """Connect to temp SQLite database."""
        return sqlite3.connect(self.temp_db_path)
    
    def _connect_production(self) -> InHousePrintDB:
        """Connect to production SQL Server database."""
        if not self.prod_db:
            self.prod_db = InHousePrintDB(str(self.prod_config_path))
        return self.prod_db
    
    # ========================================================================
    # READ OPERATIONS (Safe for AI agents)
    # ========================================================================
    
    def query_stock_levels(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query stock levels from temp database with optional filters.
        
        Args:
            filters: Optional dict with keys:
                - stock_type: Filter by stock type (e.g., "Satin", "Gloss")
                - gsm: Filter by GSM (e.g., 300, 350)
                - min_level: Minimum stock level
                - max_level: Maximum stock level
                - status: Filter by status ("critical", "low", "ok")
        
        Returns:
            Dict with keys:
                - success: bool
                - stocks: List of stock records
                - total_count: int
                - message: str
        """
        try:
            conn = self._connect_temp()
            cursor = conn.cursor()
            
            # Build query
            query = "SELECT * FROM StockLevels WHERE 1=1"
            params = []
            
            if filters:
                if 'stock_type' in filters:
                    query += " AND StockTypeDesc LIKE ?"
                    params.append(f"%{filters['stock_type']}%")
                
                if 'gsm' in filters:
                    query += " AND GSM = ?"
                    params.append(filters['gsm'])
                
                if 'min_level' in filters:
                    query += " AND CurrentStockLevel >= ?"
                    params.append(filters['min_level'])
                
                if 'max_level' in filters:
                    query += " AND CurrentStockLevel <= ?"
                    params.append(filters['max_level'])
                
                if 'status' in filters:
                    status = filters['status'].lower()
                    if status == 'critical':
                        query += " AND CurrentStockLevel <= CriticalLevel"
                    elif status == 'low':
                        query += " AND CurrentStockLevel > CriticalLevel AND CurrentStockLevel <= ReorderPoint"
                    elif status == 'ok':
                        query += " AND CurrentStockLevel > ReorderPoint"
            
            query += " ORDER BY StockTypeDesc, GSM"
            
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            stocks = []
            for row in rows:
                stock = dict(zip(columns, row))
                
                # Calculate status
                current = stock['CurrentStockLevel'] or 0
                critical = stock['CriticalLevel'] or 500
                reorder = stock['ReorderPoint'] or 1000
                
                if current <= critical:
                    stock['Status'] = 'critical'
                elif current <= reorder:
                    stock['Status'] = 'low'
                else:
                    stock['Status'] = 'ok'
                
                stocks.append(stock)
            
            conn.close()
            
            return {
                'success': True,
                'stocks': stocks,
                'total_count': len(stocks),
                'message': f"Found {len(stocks)} stock records"
            }
            
        except Exception as e:
            return {
                'success': False,
                'stocks': [],
                'total_count': 0,
                'message': f"Error querying stock levels: {str(e)}"
            }
    
    def get_stock_transactions(self, stock_id: Optional[int] = None, limit: int = 50) -> Dict[str, Any]:
        """
        Get stock transaction history from temp database.
        
        Args:
            stock_id: Optional stock ID to filter transactions
            limit: Maximum number of records to return (default: 50)
        
        Returns:
            Dict with keys:
                - success: bool
                - transactions: List of transaction records
                - total_count: int
                - message: str
        """
        try:
            conn = self._connect_temp()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    st.*,
                    sl.StockTypeDesc,
                    sl.GSM
                FROM StockTransactions st
                LEFT JOIN StockLevels sl ON st.StockID = sl.StockID
                WHERE 1=1
            """
            params = []
            
            if stock_id:
                query += " AND st.StockID = ?"
                params.append(stock_id)
            
            query += " ORDER BY st.TransactionDate DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            transactions = [dict(zip(columns, row)) for row in rows]
            
            conn.close()
            
            return {
                'success': True,
                'transactions': transactions,
                'total_count': len(transactions),
                'message': f"Found {len(transactions)} transactions"
            }
            
        except Exception as e:
            return {
                'success': False,
                'transactions': [],
                'total_count': 0,
                'message': f"Error querying transactions: {str(e)}"
            }
    
    def get_reorder_alerts(self) -> Dict[str, Any]:
        """
        Get all active reorder alerts from temp database.
        
        Returns:
            Dict with keys:
                - success: bool
                - alerts: List of alert records
                - critical_count: int (alerts at critical level)
                - warning_count: int (alerts at reorder point)
                - message: str
        """
        try:
            conn = self._connect_temp()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    ra.*,
                    sl.StockTypeDesc,
                    sl.GSM,
                    sl.CurrentStockLevel,
                    sl.CriticalLevel,
                    sl.ReorderPoint
                FROM ReorderAlerts ra
                LEFT JOIN StockLevels sl ON ra.StockID = sl.StockID
                WHERE ra.IsAcknowledged = 0 AND ra.IsSuppressed = 0
                ORDER BY ra.GeneratedDate DESC
            """
            
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            alerts = [dict(zip(columns, row)) for row in rows]
            
            # Count critical vs warning
            critical_count = len([a for a in alerts if a.get('AlertType') == 'CRITICAL'])
            warning_count = len([a for a in alerts if a.get('AlertType') == 'WARNING'])
            
            conn.close()
            
            return {
                'success': True,
                'alerts': alerts,
                'critical_count': critical_count,
                'warning_count': warning_count,
                'total_count': len(alerts),
                'message': f"Found {len(alerts)} active alerts ({critical_count} critical, {warning_count} warnings)"
            }
            
        except Exception as e:
            return {
                'success': False,
                'alerts': [],
                'critical_count': 0,
                'warning_count': 0,
                'total_count': 0,
                'message': f"Error querying alerts: {str(e)}"
            }
    
    def get_production_pricing(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query production pricing data from SQL Server.
        
        Args:
            filters: Optional dict with keys:
                - gsm: Filter by GSM
                - stock_type_id: Filter by stock type ID
        
        Returns:
            Dict with keys:
                - success: bool
                - pricing: List of pricing records
                - total_count: int
                - message: str
        """
        try:
            db = self._connect_production()
            
            query = """
                SELECT 
                    ds.StockID,
                    ds.StockTypeID,
                    dst.StockTypeDesc,
                    ds.Length,
                    ds.Width,
                    ds.GSM,
                    ds.CostPerThousand,
                    ds.Markup,
                    CAST((ds.CostPerThousand * (1 + ds.Markup/100.0)) AS DECIMAL(10,2)) AS SellPricePerThousand
                FROM Quote_DigitalStocks ds
                INNER JOIN Quote_DigitalStockType dst ON ds.StockTypeID = dst.StockTypeID
                WHERE 1=1
            """
            
            if filters:
                if 'gsm' in filters:
                    query += f" AND ds.GSM = {filters['gsm']}"
                if 'stock_type_id' in filters:
                    query += f" AND ds.StockTypeID = {filters['stock_type_id']}"
            
            query += " ORDER BY dst.StockTypeDesc, ds.GSM, ds.Length, ds.Width"
            
            result = db.execute_query(query)
            
            # Convert DataFrame to list of dicts if needed
            if hasattr(result, 'to_dict'):
                pricing = result.to_dict('records')
            else:
                pricing = []
            
            return {
                'success': True,
                'pricing': pricing,
                'total_count': len(pricing),
                'message': f"Found {len(pricing)} pricing records"
            }
            
        except Exception as e:
            return {
                'success': False,
                'pricing': [],
                'total_count': 0,
                'message': f"Error querying production pricing: {str(e)}"
            }
    
    # ========================================================================
    # WRITE OPERATIONS (Restricted to temp database only)
    # ========================================================================
    
    def update_stock_level(self, stock_id: int, new_level: int, reason: str, reference: Optional[str] = None) -> Dict[str, Any]:
        """
        Update stock level in temp database and create transaction record.
        
        Args:
            stock_id: Stock ID to update
            new_level: New stock level
            reason: Reason for update (e.g., "Manual adjustment", "Production consumption")
            reference: Optional reference (e.g., job ticket number, order ID)
        
        Returns:
            Dict with keys:
                - success: bool
                - old_level: int
                - new_level: int
                - transaction_id: int (ID of created transaction)
                - message: str
        """
        try:
            conn = self._connect_temp()
            cursor = conn.cursor()
            
            # Get current level
            sql, params = convert_sql_placeholders("SELECT CurrentStockLevel FROM StockLevels WHERE StockID = ?", (stock_id,))

            cursor.execute(sql, params)
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                return {
                    'success': False,
                    'message': f"Stock ID {stock_id} not found"
                }
            
            old_level = row[0] or 0
            quantity_change = new_level - old_level
            
            # Update stock level
            sql, params = convert_sql_placeholders("""
                UPDATE StockLevels 
                SET CurrentStockLevel = ?,
                    LastUpdated = CURRENT_TIMESTAMP
                WHERE StockID = ?
            """, (new_level, stock_id))

            cursor.execute(sql, params)
            
            # Create transaction record
            transaction_type = "ADJUSTMENT" if quantity_change >= 0 else "CONSUMPTION"
            
            sql, params = convert_sql_placeholders("""
                INSERT INTO StockTransactions 
                (StockID, TransactionType, QuantityChange, TransactionDate, Reason, Reference)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
            """, (stock_id, transaction_type, quantity_change, reason, reference))

            
            cursor.execute(sql, params)
            
            transaction_id = cursor.lastrowid
            
            # Check if reorder alert needed
            sql, params = convert_sql_placeholders("""
                SELECT CriticalLevel, ReorderPoint 
                FROM StockLevels 
                WHERE StockID = ?
            """, (stock_id,))

            cursor.execute(sql, params)
            critical, reorder = cursor.fetchone()
            
            if new_level <= (critical or 500):
                sql, params = convert_sql_placeholders("""
                    INSERT INTO ReorderAlerts (StockID, AlertLevel, CurrentLevel, ReorderPoint, IsAcknowledged)
                    VALUES (?, 'CRITICAL', ?, ?, 0)
                """, (stock_id, new_level, critical))

                cursor.execute(sql, params)
            elif new_level <= (reorder or 1000):
                sql, params = convert_sql_placeholders("""
                    INSERT INTO ReorderAlerts (StockID, AlertLevel, CurrentLevel, ReorderPoint, IsAcknowledged)
                    VALUES (?, 'WARNING', ?, ?, 0)
                """, (stock_id, new_level, reorder))

                cursor.execute(sql, params)
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'old_level': old_level,
                'new_level': new_level,
                'quantity_change': quantity_change,
                'transaction_id': transaction_id,
                'message': f"Stock level updated from {old_level} to {new_level} (change: {quantity_change:+d})"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Error updating stock level: {str(e)}"
            }
    
    def add_stock_transaction(self, stock_id: int, transaction_type: str, quantity_change: int, 
                            reason: str, reference: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a stock transaction without updating stock level (for audit trail).
        
        Args:
            stock_id: Stock ID
            transaction_type: Type ("PURCHASE", "CONSUMPTION", "ADJUSTMENT", "RETURN")
            quantity_change: Quantity change (positive or negative)
            reason: Reason for transaction
            reference: Optional reference (order ID, PO number, etc.)
        
        Returns:
            Dict with keys:
                - success: bool
                - transaction_id: int
                - message: str
        """
        try:
            conn = self._connect_temp()
            cursor = conn.cursor()
            
            sql, params = convert_sql_placeholders("""
                INSERT INTO StockTransactions 
                (StockID, TransactionType, QuantityChange, TransactionDate, Reason, Reference)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
            """, (stock_id, transaction_type, quantity_change, reason, reference))

            
            cursor.execute(sql, params)
            
            transaction_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'message': f"Transaction recorded (ID: {transaction_id})"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Error adding transaction: {str(e)}"
            }
    
    def resolve_reorder_alert(self, alert_id: int, resolution_notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Mark a reorder alert as resolved.
        
        Args:
            alert_id: Alert ID to resolve
            resolution_notes: Optional notes about resolution
        
        Returns:
            Dict with keys:
                - success: bool
                - message: str
        """
        try:
            conn = self._connect_temp()
            cursor = conn.cursor()
            
            sql, params = convert_sql_placeholders("""
                UPDATE ReorderAlerts 
                SET IsAcknowledged = 1,
                    AcknowledgedDate = CURRENT_TIMESTAMP,
                    AcknowledgedBy = ?
                WHERE AlertID = ?
            """, (resolution_notes or 'System', alert_id))

            
            cursor.execute(sql, params)
            
            if cursor.rowcount == 0:
                conn.close()
                return {
                    'success': False,
                    'message': f"Alert ID {alert_id} not found"
                }
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': f"Alert {alert_id} resolved"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Error resolving alert: {str(e)}"
            }


# Singleton instance for use in Flask app
_stock_tools_instance = None

def get_stock_tools() -> StockDatabaseTools:
    """Get singleton instance of StockDatabaseTools."""
    global _stock_tools_instance
    if _stock_tools_instance is None:
        _stock_tools_instance = StockDatabaseTools()
    return _stock_tools_instance
