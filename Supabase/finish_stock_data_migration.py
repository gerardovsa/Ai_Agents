#!/usr/bin/env python3
"""
Finish Stock Data Migration
Migrates remaining stock_data tables (PostgreSQL lowercased the table names)
"""

import sys
import sqlite3
from pathlib import Path
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values

# Load credentials from .env.master
env_master_path = Path(__file__).parent.parent / '.env.master'
credentials = {}
with open(env_master_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            credentials[key.strip()] = value.strip()

supabase_db_url = credentials.get('SUPABASE_DB_URL')

# Connect to PostgreSQL
print("Connecting to Supabase...")
pg_conn = psycopg2.connect(supabase_db_url)
pg_conn.autocommit = False

# Connect to SQLite
sqlite_path = Path(__file__).parent.parent / 'data' / 'stock_data.db'
sqlite_conn = sqlite3.connect(str(sqlite_path))
sqlite_conn.row_factory = sqlite3.Row

print("Migrating stock_data tables...")

# Get all tables from SQLite
cursor = sqlite_conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
tables = [row[0] for row in cursor.fetchall()]

pg_cursor = pg_conn.cursor()

for table_name in tables:
    # Get table info
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    column_names = [col[1] for col in columns_info]
    column_types = {col[1]: col[2] for col in columns_info}
    
    # Get data
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    if not rows:
        print(f"  Skipping {table_name} (no data)")
        continue
    
    print(f"  Migrating {table_name} ({len(rows)} rows)...", end='', flush=True)
    
    # PostgreSQL lowercases table names
    pg_table_name = table_name.lower()
    
    # Convert rows (handle booleans and type mismatches)
    data = []
    for row in rows:
        converted_row = []
        for i, value in enumerate(row):
            col_name = column_names[i]
            col_type = column_types[col_name].upper()
            
            # Convert boolean values (SQLite stores as 0/1)
            if 'BOOL' in col_type and value is not None:
                converted_row.append(bool(value))
            # Convert integers (handle text that should be int)
            elif 'INT' in col_type and value is not None and isinstance(value, str):
                try:
                    converted_row.append(int(value))
                except ValueError:
                    # If can't convert, set to NULL
                    converted_row.append(None)
            else:
                converted_row.append(value)
        
        data.append(tuple(converted_row))
    
    # Insert with lowercase table name
    try:
        # Truncate table first to avoid duplicates
        pg_cursor.execute(sql.SQL('TRUNCATE TABLE {} CASCADE').format(
            sql.Identifier('stock_data', pg_table_name)
        ))
        
        insert_sql = sql.SQL('INSERT INTO {} ({}) VALUES %s').format(
            sql.Identifier('stock_data', pg_table_name),
            sql.SQL(', ').join([sql.Identifier(col) for col in column_names])
        )
        
        execute_values(pg_cursor, insert_sql, data, page_size=1000)
        print(f" OK ({len(data)} rows)")
    
    except Exception as e:
        print(f" ERROR: {str(e)[:100]}")
        pg_conn.rollback()
        continue

# Commit all
pg_conn.commit()

# Verify
print("\nVerifying migration...")
pg_cursor.execute("SELECT COUNT(*) FROM stock_data.extracted_jobs")
count = pg_cursor.fetchone()[0]
print(f"  extracted_jobs: {count} rows")

pg_cursor.execute("SELECT COUNT(*) FROM stock_data.stocklevels")
count = pg_cursor.fetchone()[0]
print(f"  stocklevels: {count} rows")

print("\nMigration complete!")

pg_conn.close()
sqlite_conn.close()
