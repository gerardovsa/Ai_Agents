#!/usr/bin/env python3
"""
Export database schema from local development to SQL file
This SQL file will be committed to git and run on Render first deployment
"""

import sqlite3
import os
from pathlib import Path

def export_schema(db_path, output_file):
    """Export CREATE TABLE statements from database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all CREATE TABLE statements
    cursor.execute("""
        SELECT sql FROM sqlite_master 
        WHERE type='table' AND sql IS NOT NULL
        ORDER BY name
    """)
    
    tables = cursor.fetchall()
    conn.close()
    
    with open(output_file, 'w') as f:
        f.write("-- AI Agents Database Schema\n")
        f.write(f"-- Exported from: {db_path}\n")
        f.write("-- Date: {}\n\n".format(__import__('datetime').datetime.now()))
        
        for table_sql in tables:
            f.write(table_sql[0] + ";\n\n")
    
    print(f"✅ Exported schema to: {output_file}")
    print(f"   Tables exported: {len(tables)}")

if __name__ == '__main__':
    root_dir = Path(__file__).parent.parent.parent
    data_dir = root_dir / 'data'
    deployment_dir = root_dir / 'scripts' / 'deployment'
    
    # Export ai_infrastructure.db schema
    export_schema(
        data_dir / 'ai_infrastructure.db',
        deployment_dir / 'ai_infrastructure_schema.sql'
    )
    
    # Export sessions.db schema
    export_schema(
        data_dir / 'sessions.db',
        deployment_dir / 'sessions_schema.sql'
    )
    
    # Export synergy_sessions.db schema
    export_schema(
        data_dir / 'synergy_sessions.db',
        deployment_dir / 'synergy_sessions_schema.sql'
    )
    
    print("\n✅ All schemas exported!")
    print("📝 Next steps:")
    print("   1. Commit these .sql files to git")
    print("   2. They'll be used on first Render deployment")
