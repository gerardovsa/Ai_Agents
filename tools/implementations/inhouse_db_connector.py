#!/usr/bin/env python3
"""
InHousePrint Database Connection for AI_agents
================================================
Lightweight database connector for AI_agents tool system

Provides SQL Server connection with credential injection support
"""

import pyodbc
import pandas as pd
import json
import sys
import os
import warnings
from typing import Optional, Dict, Any

# Suppress pandas SQLAlchemy warnings
warnings.filterwarnings('ignore', message='pandas only supports SQLAlchemy connectable')


class InHousePrintDB:
    """Database connection for InHousePrint SQL Server"""
    
    def __init__(self, **kwargs):
        """
        Initialize with credential injection support
        
        Credentials injected at runtime by credential_injector.py
        """
        self.credentials = None  # Injected at runtime
        self.connection = None
        self.config = None
        
        # Get config path from kwargs or use default
        config_path = kwargs.get('config_path', self._get_default_config_path())
        
        if config_path and os.path.exists(config_path):
            self.config = self._load_config(config_path)
            self.connect(**kwargs)
    
    def _get_default_config_path(self) -> str:
        """Get default config path relative to AI_infrastructure"""
        # Try to find config in AI_infrastructure/data
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        config_path = os.path.join(base_dir, 'AI_infrastructure', 'data', 'database-config.json')
        
        if os.path.exists(config_path):
            return config_path
        
        # Fallback to local directory
        return os.path.join(os.path.dirname(__file__), 'database-config.json')
    
    def _load_config(self, config_path: str) -> dict:
        """Load database configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"WARNING: Config file not found: {config_path}")
            return None
        except json.JSONDecodeError:
            print(f"ERROR: Invalid JSON in config file: {config_path}")
            return None
    
    def connect(self, **kwargs) -> Dict[str, Any]:
        """
        Establish SQL Server connection
        
        Supports both config file and credential injection
        """
        try:
            # Get credentials from kwargs (injected by credential_injector)
            server = kwargs.get('server')
            database = kwargs.get('database')
            username = kwargs.get('username')
            password = kwargs.get('password')
            driver = kwargs.get('driver', '{ODBC Driver 17 for SQL Server}')
            
            # Fallback to config file if no credentials injected
            if not server and self.config:
                conn_str = self.config['DatabaseConnections']['Primary']['ConnectionString']
                
                # Parse connection string
                parts = conn_str.split(';')
                for part in parts:
                    if 'data source=' in part.lower():
                        server = part.split('=')[1]
                    elif 'user id=' in part.lower():
                        username = part.split('=')[1]
                    elif 'password=' in part.lower():
                        password = part.split('=')[1]
                    elif 'database=' in part.lower():
                        database = part.split('=')[1]
            
            if not server:
                return {
                    'success': False,
                    'error': 'No server specified and no config file found'
                }
            
            # Try multiple ODBC drivers
            drivers = [
                "{ODBC Driver 18 for SQL Server}",
                "{ODBC Driver 17 for SQL Server}",
                "{SQL Server Native Client 11.0}",
                "{SQL Server}"
            ]
            
            # If specific driver provided, try it first
            if driver and driver not in drivers:
                drivers.insert(0, driver)
            
            connection_successful = False
            last_error = None
            
            for drv in drivers:
                try:
                    # Build connection string
                    if username and password:
                        # SQL authentication
                        conn_str = (
                            f"DRIVER={drv};"
                            f"SERVER={server};"
                            f"DATABASE={database};"
                            f"UID={username};"
                            f"PWD={password};"
                            f"TrustServerCertificate=yes;"
                            f"Encrypt=no;"
                        )
                    else:
                        # Windows authentication
                        conn_str = (
                            f"DRIVER={drv};"
                            f"SERVER={server};"
                            f"DATABASE={database};"
                            f"Trusted_Connection=yes;"
                            f"TrustServerCertificate=yes;"
                        )
                    
                    self.connection = pyodbc.connect(conn_str, timeout=30)
                    connection_successful = True
                    
                    return {
                        'success': True,
                        'message': f'Connected to {database} on {server}',
                        'driver': drv
                    }
                    
                except pyodbc.Error as e:
                    last_error = str(e)
                    continue  # Try next driver
            
            return {
                'success': False,
                'error': f'Failed to connect with any driver. Last error: {last_error}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_query(self, query: str, params: tuple = None, **kwargs) -> Dict[str, Any]:
        """
        Execute SQL query and return results
        
        Returns dict with success flag, data, and metadata
        """
        if not self.connection:
            return {
                'success': False,
                'error': 'No database connection available'
            }
        
        try:
            cursor = self.connection.cursor()
            
            # Execute with or without parameters
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Get column names
            columns = [column[0] for column in cursor.description] if cursor.description else []
            
            # Fetch results
            rows = cursor.fetchall()
            cursor.close()
            
            # Convert to DataFrame
            df = pd.DataFrame.from_records(rows, columns=columns)
            
            return {
                'success': True,
                'rows': len(df),
                'columns': list(df.columns),
                'data': df.to_dict('records'),
                'dataframe': df  # Include DataFrame for advanced usage
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_business_summary(self, **kwargs) -> Dict[str, Any]:
        """Get high-level business metrics"""
        queries = {
            'total_orders': "SELECT COUNT(*) as count FROM Orders",
            'active_orders': "SELECT COUNT(*) as count FROM Orders WHERE Invoiced = 0",
            'total_clients': "SELECT COUNT(*) as count FROM Clients",
            'recent_revenue': """
                SELECT SUM(TotalCost) as revenue
                FROM Orders 
                WHERE OrderDate >= DATEADD(MONTH, -1, GETDATE())
                AND Invoiced = 1
            """
        }
        
        results = {}
        for key, query in queries.items():
            result = self.execute_query(query)
            if result['success'] and len(result['data']) > 0:
                results[key] = result['data'][0].get('count') or result['data'][0].get('revenue', 0)
            else:
                results[key] = 0
        
        return {
            'success': True,
            'metrics': results
        }
    
    def close(self, **kwargs) -> Dict[str, Any]:
        """Close database connection"""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                return {
                    'success': True,
                    'message': 'Connection closed'
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }
        
        return {
            'success': True,
            'message': 'No connection to close'
        }
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            if self.connection:
                self.connection.close()
        except:
            pass
