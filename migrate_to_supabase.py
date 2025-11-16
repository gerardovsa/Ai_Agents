"""
Data Migration Script: SQLite → Supabase PostgreSQL

Migrates data from local SQLite databases to Supabase PostgreSQL.
Handles schema mapping: SQLite DB name → PostgreSQL schema name

Databases to migrate:
- ai_infrastructure.db → ai_infrastructure schema
- sessions.db → sessions schema  
- synergy_sessions.db → synergy_sessions schema
- stock_data.db → stock_data schema

Usage:
    python migrate_to_supabase.py

Prerequisites:
- SUPABASE_DB_URL must be set in environment
- Local SQLite databases must exist in data/ folder
"""

import os
import sys
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path
from datetime import datetime

# Database configurations
SQLITE_DBS = {
    'ai_infrastructure': 'data/ai_infrastructure.db',
    'sessions': 'data/sessions.db',
    'synergy_sessions': 'data/synergy_sessions.db',
    'stock_data': 'data/stock_data.db'
}

# Get Supabase connection URL from environment
SUPABASE_URL = os.getenv('SUPABASE_DB_URL')
if not SUPABASE_URL:
    print("ERROR: SUPABASE_DB_URL environment variable not set")
    print("Set it to: postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres")
    sys.exit(1)


def get_sqlite_tables(db_path):
    """Get list of tables from SQLite database"""
    if not os.path.exists(db_path):
        print(f"  ⚠️  Database not found: {db_path}")
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables


def get_table_schema(db_path, table_name):
    """Get CREATE TABLE statement from SQLite"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def convert_sqlite_to_postgres_type(sqlite_type):
    """Convert SQLite type to PostgreSQL type"""
    sqlite_type = sqlite_type.upper()
    
    # Exact matches
    if sqlite_type == 'INTEGER': return 'INTEGER'
    if sqlite_type == 'TEXT': return 'TEXT'
    if sqlite_type == 'REAL': return 'DOUBLE PRECISION'
    if sqlite_type == 'BLOB': return 'BYTEA'
    if sqlite_type == 'BOOLEAN': return 'BOOLEAN'
    if sqlite_type == 'DATETIME': return 'TIMESTAMP'
    if sqlite_type == 'TIMESTAMP': return 'TIMESTAMP'
    if sqlite_type == 'DATE': return 'DATE'
    if sqlite_type == 'TIME': return 'TIME'
    
    # VARCHAR variants
    if 'VARCHAR' in sqlite_type or 'CHAR' in sqlite_type:
        return sqlite_type  # Keep as-is
    
    # Default to TEXT for unknown types
    return 'TEXT'


def create_postgres_table(pg_cursor, schema_name, table_name, sqlite_create_sql):
    """Create table in PostgreSQL based on SQLite schema"""
    # Skip if table already exists
    pg_cursor.execute(f"""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = %s
        )
    """, (schema_name, table_name))
    
    result = pg_cursor.fetchone()
    exists = result['exists'] if isinstance(result, dict) else result[0]
    if exists:
        print(f"    ℹ️  Table {schema_name}.{table_name} already exists")
        return True
    
    # Parse SQLite CREATE TABLE and convert to PostgreSQL
    # This is a simplified version - for complex schemas, may need manual review
    postgres_sql = sqlite_create_sql.replace('AUTOINCREMENT', 'GENERATED ALWAYS AS IDENTITY')
    
    # Add schema prefix
    postgres_sql = postgres_sql.replace(f'CREATE TABLE {table_name}', 
                                       f'CREATE TABLE {schema_name}.{table_name}')
    
    try:
        pg_cursor.execute(postgres_sql)
        print(f"    ✅ Created table: {schema_name}.{table_name}")
        return True
    except Exception as e:
        print(f"    ❌ Failed to create table {schema_name}.{table_name}: {e}")
        print(f"       SQL: {postgres_sql[:200]}...")
        return False


def get_table_row_count(db_path, table_name):
    """Get row count from SQLite table"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def migrate_table_data(sqlite_path, schema_name, table_name, pg_conn, skip_existing=True):
    """Migrate data from SQLite table to PostgreSQL"""
    # Get SQLite data
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    try:
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"      ℹ️  Table {table_name} is empty")
            return 0
        
        # Get column names
        columns = [description[0] for description in sqlite_cursor.description]
        
        # Check if table is empty in PostgreSQL
        pg_cursor = pg_conn.cursor()
        pg_cursor.execute(f'SELECT COUNT(*) as count FROM {schema_name}.{table_name}')
        result = pg_cursor.fetchone()
        existing_count = result['count'] if isinstance(result, dict) else result[0]
        
        if existing_count > 0 and skip_existing:
            print(f"      ⏭️  Skipping - table already has {existing_count} rows")
            return 0
        
        # Prepare INSERT statement with ON CONFLICT handling
        placeholders = ','.join(['%s'] * len(columns))
        columns_str = ','.join([f'"{col}"' for col in columns])
        
        # Try to get primary key column (usually 'id')
        pg_cursor.execute(f"""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = '{schema_name}.{table_name}'::regclass
            AND i.indisprimary
        """)
        pk_result = pg_cursor.fetchone()
        pk_column = pk_result['attname'] if pk_result and isinstance(pk_result, dict) else (pk_result[0] if pk_result else None)
        
        if pk_column:
            insert_sql = f'INSERT INTO {schema_name}.{table_name} ({columns_str}) VALUES ({placeholders}) ON CONFLICT ({pk_column}) DO NOTHING'
        else:
            insert_sql = f'INSERT INTO {schema_name}.{table_name} ({columns_str}) VALUES ({placeholders})'
        
        # Insert data in batches
        pg_cursor = pg_conn.cursor()
        batch_size = 100
        inserted = 0
        
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i+batch_size]
            values = [tuple(row) for row in batch]
            
            try:
                pg_cursor.executemany(insert_sql, values)
                pg_conn.commit()
                inserted += len(batch)
                print(f"      📊 Inserted {inserted}/{len(rows)} rows", end='\r')
            except Exception as e:
                print(f"\n      ⚠️  Error inserting batch {i//batch_size + 1}: {e}")
                pg_conn.rollback()
                # Try one by one
                for row in batch:
                    try:
                        pg_cursor.execute(insert_sql, tuple(row))
                        pg_conn.commit()
                        inserted += 1
                    except Exception as e2:
                        print(f"\n      ❌ Failed to insert row: {e2}")
                        pg_conn.rollback()
        
        print(f"\n      ✅ Migrated {inserted} rows to {schema_name}.{table_name}")
        return inserted
        
    except Exception as e:
        print(f"      ❌ Error migrating {table_name}: {e}")
        return 0
    finally:
        sqlite_conn.close()


def migrate_database(db_name, sqlite_path, pg_conn):
    """Migrate entire SQLite database to PostgreSQL schema"""
    print(f"\n{'='*60}")
    print(f"Migrating: {db_name}")
    print(f"Source: {sqlite_path}")
    print(f"Target Schema: {db_name}")
    print(f"{'='*60}")
    
    if not os.path.exists(sqlite_path):
        print(f"⚠️  Database not found: {sqlite_path}")
        return
    
    # Create schema if not exists
    pg_cursor = pg_conn.cursor()
    try:
        pg_cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {db_name}")
        pg_conn.commit()
        print(f"✅ Schema '{db_name}' ready")
    except Exception as e:
        print(f"❌ Failed to create schema: {e}")
        return
    
    # Get tables
    tables = get_sqlite_tables(sqlite_path)
    print(f"📊 Found {len(tables)} tables: {', '.join(tables)}")
    
    total_rows = 0
    
    for table in tables:
        print(f"\n  📋 Processing table: {table}")
        
        # Get row count
        row_count = get_table_row_count(sqlite_path, table)
        print(f"    📊 Rows in SQLite: {row_count}")
        
        if row_count == 0:
            print(f"    ⏭️  Skipping empty table")
            continue
        
        # Get schema
        create_sql = get_table_schema(sqlite_path, table)
        if not create_sql:
            print(f"    ⚠️  Could not get schema for {table}")
            continue
        
        # Create table in PostgreSQL
        if create_postgres_table(pg_cursor, db_name, table, create_sql):
            pg_conn.commit()
            
            # Migrate data
            migrated = migrate_table_data(sqlite_path, db_name, table, pg_conn)
            total_rows += migrated
    
    print(f"\n✅ Completed migration for {db_name}: {total_rows} total rows migrated")


def verify_migration(pg_conn):
    """Verify data was migrated successfully"""
    print(f"\n{'='*60}")
    print("VERIFICATION REPORT")
    print(f"{'='*60}")
    
    pg_cursor = pg_conn.cursor()
    
    for schema_name, sqlite_path in SQLITE_DBS.items():
        if not os.path.exists(sqlite_path):
            continue
            
        print(f"\n📊 Schema: {schema_name}")
        
        # Get tables in this schema
        pg_cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s
            ORDER BY table_name
        """, (schema_name,))
        
        results = pg_cursor.fetchall()
        pg_tables = [row['table_name'] if isinstance(row, dict) else row[0] for row in results]
        
        if not pg_tables:
            print(f"  ⚠️  No tables found in schema")
            continue
        
        # Check row counts
        for table in pg_tables:
            pg_cursor.execute(f'SELECT COUNT(*) FROM {schema_name}.{table}')
            result = pg_cursor.fetchone()
            pg_count = result['count'] if isinstance(result, dict) else result[0]
            
            # Get SQLite count
            sqlite_conn = sqlite3.connect(sqlite_path)
            sqlite_cursor = sqlite_conn.cursor()
            try:
                sqlite_cursor.execute(f'SELECT COUNT(*) FROM {table}')
                sqlite_count = sqlite_cursor.fetchone()[0]
            except:
                sqlite_count = 0
            sqlite_conn.close()
            
            status = "✅" if pg_count == sqlite_count else "⚠️"
            print(f"  {status} {table}: SQLite={sqlite_count}, PostgreSQL={pg_count}")


def main():
    """Main migration process"""
    print(f"\n{'#'*60}")
    print("# SQLite → Supabase PostgreSQL Migration")
    print(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*60}")
    
    # Connect to Supabase
    print(f"\n🔗 Connecting to Supabase...")
    try:
        pg_conn = psycopg2.connect(
            SUPABASE_URL,
            cursor_factory=RealDictCursor,
            connect_timeout=30,
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5
        )
        print(f"✅ Connected to Supabase PostgreSQL")
        
        # Get PostgreSQL version
        cursor = pg_conn.cursor()
        cursor.execute("SELECT version()")
        result = cursor.fetchone()
        if result:
            version = result[0] if isinstance(result, tuple) else result['version']
            print(f"📊 {version.split(',')[0]}")
        
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        sys.exit(1)
    
    # Migrate each database
    for db_name, sqlite_path in SQLITE_DBS.items():
        migrate_database(db_name, sqlite_path, pg_conn)
    
    # Verify migration
    verify_migration(pg_conn)
    
    # Close connection
    pg_conn.close()
    
    print(f"\n{'#'*60}")
    print(f"# Migration Complete!")
    print(f"# Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*60}\n")


if __name__ == '__main__':
    main()
